"""
The traces of a dataset figure over time: one trace of an experiment in the value picked, the traces of several experiments lined up on their additions and read at shared times, and their mean, SD and SEM.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.delta_psi import DELTA_PSI_COLUMN
from utils_shared.helpers import name_simplifier
from utils_shared.schema import HAEM_KEYS, TIME_COLUMN, VO2_KEYS


# ---- CONSTANTS -----------------------------------------------------------------------
# The traces a plot over time can show, as kept in the roles of a plot; a haem is
# HAEM_TRACE_START then its name in lower-case letters and digits ('haem_cytbh')
OXYGEN_TRACE = 'oxygen'
VO2_TRACE = 'vo2'
PSI_TRACE = 'delta_psi'
HAEM_TRACE_START = 'haem_'
# The values of the OCR and of Δψ, (the role kept, the words shown); the first is the
# one a new plot starts at. The haems have the views of config.HAEM_SOURCE_BY_MODE.
VO2_VALUES = (('baseline', '% of baseline'),
              ('raw', 'As measured'),
              ('change', 'Change from baseline'),
              ('od', 'Per OD'),
              )
PSI_VALUES = (('raw', 'mV'), ('change', 'Change from baseline'))
CHANGE_VALUE = 'change'
# The title of the y axis for each value
OXYGEN_LABEL = 'O$_2$ (µM)'
VO2_LABELS = {'baseline': 'OCR (% of baseline)',
              'raw': 'OCR (µM min$^{-1}$)',
              'change': 'Change in OCR (µM min$^{-1}$)',
              'od': 'OCR (µM min$^{-1}$ OD$^{-1}$)',
              }
PSI_LABELS = {'raw': 'Δψ (mV)', 'change': 'Change in Δψ (mV)'}
HAEM_LABELS = {'percent': '{} oxidised (%)',
               'abs': '{} absorbance (mOD)',
               'abs_od': '{} absorbance (mOD OD$^{{-1}}$)',
               'delta_abs': '{} ΔD (mOD)',
               'delta_abs_od': '{} ΔD (mOD OD$^{{-1}}$)',
               }
# The shared times the lined-up traces are read at: one every second
STEPS_PER_MINUTE = 60
# how far a time may miss the end of a trace and still be read there (rounding)
TIME_TOLERANCE_MIN = 1e-9


# ---- READING HELPERS -----------------------------------------------------------------


# ---- _baseline_mean_finder -----------------------------------------------------------
def _baseline_mean_finder(experiment: dict, trace: str, column: str) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to find the average of the OCR or of Δψ in the baseline of an
    experiment, for its change from baseline.

    ---- Inputs ----
    experiment : dict
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md).
    trace : str
        VO2_TRACE or PSI_TRACE.
    column : str
        The column of the OCR in its table; not used for Δψ.

    ---- Globals read ----
    VO2_KEYS (imported), VO2_TRACE.

    ---- Outputs ----
    Optional[float]
        The average in the baseline (µM min⁻¹, or mV); None for a file without a
        baseline, or without a Δψ in it.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if trace == VO2_TRACE:
        table = experiment.get(VO2_KEYS['baseline'])
        used = None if table is None else table.attrs.get('baseline_percent')
        mean = ((used or {}).get('baseline_mean') or {}).get(column)
    else:
        windows = (experiment.get('averages') or {}).get('windows') or {}
        mean = ((windows.get('average0') or {}).get('delta_psi') or {}).get('mean')
    if mean is None or not np.isfinite(mean):
        return None
    return float(mean)


# ---- _haem_table_finder --------------------------------------------------------------
def _haem_table_finder(experiment: dict,
                       view: str,
                       is_per_od: bool,
                       ) -> Tuple[Optional[str], Optional[object]]:
    """
    ---- Summary ----
    Helper function to find the table of the haems in one view: per OD when the run
    is and the file has it, otherwise as it is.

    ---- Inputs ----
    experiment : dict
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md).
    view : str
        'delta', 'abs' or 'percent' (a key of config.HAEM_SOURCE_BY_MODE).
    is_per_od : bool
        True when the run shows its haems per OD.

    ---- Globals read ----
    settings.FALLBACK_WITHOUT_OD, settings.HAEM_SOURCE_BY_MODE; HAEM_KEYS (imported).

    ---- Outputs ----
    Tuple[Optional[str], Optional[object]]
        (the haem source, such as 'delta_abs'; its table), or (None, None) when the
        file has no haems in that view.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    pair = settings.HAEM_SOURCE_BY_MODE.get(view)
    if pair is None:
        return None, None
    source = pair[1] if is_per_od else pair[0]
    if HAEM_KEYS[source] not in experiment:
        source = settings.FALLBACK_WITHOUT_OD.get(source, source)
    table = experiment.get(HAEM_KEYS[source])
    return (None, None) if table is None else (source, table)


# ---- ALIGNING HELPERS ----------------------------------------------------------------


# ---- _pieces_lister ------------------------------------------------------------------
def _pieces_lister(spans: Sequence[Tuple[float, float]],
                   additions: Sequence[Sequence[float]],
                   zero: Optional[int],
                   ) -> Tuple[List[Tuple[float, float, List[float]]],
                              List[float],
                              List[float],
                              ]:
    """
    ---- Summary ----
    Helper function to cut the shared time axis of several experiments into pieces,
    each piece being a stretch where every experiment's own time is the shared time
    plus one fixed number of its own.

    ---- Inputs ----
    spans : Sequence[Tuple[float, float]]
        (first time, last time) of the trace of each experiment, on its own clock
        (min).
    additions : Sequence[Sequence[float]]
        The times of the additions of each experiment, in order, the same number in
        each (min).
    zero : Optional[int]
        Which addition is time 0 of the shared axis, from 0; None to line up on the
        clocks as they are, without the additions.

    ---- Globals read ----
    STEPS_PER_MINUTE.

    ---- Outputs ----
    Tuple[List[Tuple[float, float, List[float]]], List[float], List[float]]
        (the pieces in time order, each (start, end, the number added for each
        experiment) on the shared axis; the shared times of the additions; the shared
        times where the spare middle of a longer gap is left out).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See traces_aligner.

    ---- Helpers ----
    None.
    """

    # ---- 1 The clocks as they are ----------------------------------------------------
    count = len(additions[0]) if additions else 0
    if zero is None or count == 0:
        start = max(first for first, _ in spans)
        end = min(last for _, last in spans)
        return [(start, end, [0.0] * len(spans))], [], []

    # ---- 2 Where each addition sits on the shared axis -------------------------------
    zero = min(zero, count - 1)
    gaps = [[own[place + 1] - own[place] for own in additions]
            for place in range(count - 1)
            ]
    shortest = [min(gap) for gap in gaps]
    places = [float(sum(shortest[:place])) for place in range(count)]
    places = [place - places[zero] for place in places]

    # ---- 3 Before the first addition, as far as the shortest experiment goes ---------
    before = max(min(own[0] - first for own, (first, _) in zip(additions, spans)), 0.0)
    pieces = [
        (places[0] - before, places[0], [own[0] - places[0] for own in additions]),
        ]

    # ---- 4 Each gap: counted from the addition before, then back from the next -------
    breaks = []
    for place, gap in enumerate(shortest):
        middle = places[place] + gap / 2.0
        pieces.append((places[place],
                       middle,
                       [own[place] - places[place] for own in additions],
                       ),
                      )
        pieces.append((middle,
                       places[place + 1],
                       [own[place + 1] - places[place + 1] for own in additions],
                       ),
                      )
        if max(gaps[place]) - gap > 1.0 / STEPS_PER_MINUTE:
            breaks.append(middle)

    # ---- 5 After the last addition, as far as the shortest experiment goes -----------
    after = max(min(last - own[-1] for own, (_, last) in zip(additions, spans)), 0.0)
    pieces.append((places[-1],
                   places[-1] + after,
                   [own[-1] - places[-1] for own in additions],
                   ),
                  )
    return pieces, places, breaks


# ---- _trace_interpolator -------------------------------------------------------------
def _trace_interpolator(times: np.ndarray,
                        values: np.ndarray,
                        wanted: np.ndarray,
                        ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to read a trace at other times, on the straight line between its
    two nearest points; empty (NaN) outside the trace and beside an empty point.

    ---- Inputs ----
    times : np.ndarray
        The times of the trace, increasing, shape (n_points,) (min).
    values : np.ndarray
        Its values, shape (n_points,).
    wanted : np.ndarray
        The times to read it at, shape (n_times,) (min).

    ---- Globals read ----
    TIME_TOLERANCE_MIN.

    ---- Outputs ----
    np.ndarray
        The values at the wanted times, shape (n_times,).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    y = y1 + (y2 - y1) x (t - t1) / (t2 - t1), with (t1, y1) and (t2, y2) the points
    either side of t.

    ---- Helpers ----
    None.
    """

    wanted = np.asarray(wanted, dtype=float).copy()
    for edge in (times[0], times[-1]):  # a time a rounding away from an end is the end
        wanted[np.abs(wanted - edge) < TIME_TOLERANCE_MIN] = edge
    return np.interp(wanted, times, values, left=np.nan, right=np.nan)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- additions_lister ----------------------------------------------------------------
def additions_lister(experiment: dict) -> List[float]:
    """
    ---- Summary ----
    Main function to list the times of the additions of an experiment, in order.

    ---- Inputs ----
    experiment : dict
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[float]
        The times (min); empty for a file without additions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    events = (experiment.get('metadata') or {}).get('events') or []
    return sorted(float(event['time']) for event in events)


# ---- line_breaker --------------------------------------------------------------------
def line_breaker(times: np.ndarray,
                 values: np.ndarray,
                 breaks: Sequence[float],
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Main function to break a lined-up trace where the spare middle of a longer gap
    was left out: an empty point is put in at each break, so the line is not drawn
    across it.

    ---- Inputs ----
    times : np.ndarray
        The shared times, shape (n_times,) (min).
    values : np.ndarray
        The values at those times, shape (n_times,).
    breaks : Sequence[float]
        The shared times of the breaks (traces_aligner) (min).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray]
        (the times, the values), each one point longer for every break.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=float)
    for moment in sorted(breaks):
        place = int(np.searchsorted(times, moment - TIME_TOLERANCE_MIN, side='left'))
        times = np.insert(times, place, moment)
        values = np.insert(values, place, np.nan)
    return times, values


# ---- trace_reader --------------------------------------------------------------------
def trace_reader(experiment: dict,
                 trace: str,
                 value: str,
                 is_per_od: bool = False,
                 ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to read one trace of an experiment in the value picked: the
    measured oxygen; the OCR as measured, per OD, as % of baseline or as its change
    from baseline; a haem as ΔD, absorbance or % oxidised; Δψ in mV or as its change
    from baseline.

    ---- Inputs ----
    experiment : dict
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md).
    trace : str
        OXYGEN_TRACE, VO2_TRACE, PSI_TRACE, or HAEM_TRACE_START then the name of a
        haem in lower-case letters and digits.
    value : str
        For the OCR a key of VO2_VALUES, for Δψ one of PSI_VALUES, for a haem a view
        ('delta', 'abs', 'percent'); not used for the oxygen.
    is_per_od : bool
        True when the run shows its haems per OD.

    ---- Globals read ----
    CHANGE_VALUE, HAEM_LABELS, HAEM_TRACE_START, OXYGEN_LABEL, OXYGEN_TRACE,
    PSI_LABELS, PSI_TRACE, VO2_LABELS, VO2_TRACE; DELTA_PSI_COLUMN, TIME_COLUMN,
    VO2_KEYS (imported).

    ---- Outputs ----
    Optional[dict]
        {'times_min': np.ndarray (n_points,), 'values': np.ndarray (n_points,),
        'label': the title of the y axis with its unit}; None when the file does not
        have that trace in that value (no such table or haem, no baseline for a
        change from baseline or a % of baseline).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Change from baseline: y = x - b, with x the trace at one time and b its average
    in the baseline of the file (MATHS.md section 10.1). The other values are read
    as the run worked them out.

    ---- Helpers ----
    _baseline_mean_finder
    _haem_table_finder
    name_simplifier
    """

    # ---- 1 The table, its column and what is taken off -------------------------------
    shift = 0.0
    if trace == OXYGEN_TRACE:
        table, column, label = experiment.get('CcO2'), None, OXYGEN_LABEL
    elif trace == VO2_TRACE:
        if value not in VO2_LABELS:
            return None
        key = VO2_KEYS['raw' if value == CHANGE_VALUE else value]
        table, column, label = experiment.get(key), None, VO2_LABELS[value]
    elif trace == PSI_TRACE:
        if value not in PSI_LABELS:
            return None
        table, column, label = (experiment.get('delta_psi'),
                                DELTA_PSI_COLUMN,
                                PSI_LABELS[value],
                                )
    elif trace.startswith(HAEM_TRACE_START):
        source, table = _haem_table_finder(experiment, value, is_per_od)
        if table is None:
            return None
        wanted = trace[len(HAEM_TRACE_START):]
        column = next((name
                       for name in table.columns
                       if name_simplifier(str(name)) == wanted
                       ),
                      None,
                      )
        if column is None:
            return None
        label = HAEM_LABELS[source].format(column)
    else:
        return None
    if table is None:
        return None
    if column is None:  # the oxygen and the OCR: the one column beside the time
        others = [name for name in table.columns if name != TIME_COLUMN]
        if not others:
            return None
        column = others[0]
    if column not in table.columns:
        return None
    if value == CHANGE_VALUE and trace in (VO2_TRACE, PSI_TRACE):
        mean = _baseline_mean_finder(experiment, trace, column)
        if mean is None:
            return None
        shift = mean

    # ---- 2 The trace, without the rows that have no time -----------------------------
    times = np.asarray(table[TIME_COLUMN], dtype=float)
    values = np.asarray(table[column], dtype=float) - shift
    has_time = np.isfinite(times)
    if not has_time.any():
        return None
    return {'times_min': times[has_time], 'values': values[has_time], 'label': label}


# ---- traces_aligner ------------------------------------------------------------------
def traces_aligner(traces: Sequence[dict], zero: Optional[int]) -> dict:
    """
    ---- Summary ----
    Main function to line the traces of several experiments up on their additions
    and read them all at the same shared times, one every second. The additions are
    the measuring stick: up to halfway through a gap between two additions a point
    is placed by its time after the addition before it, past halfway by its time
    before the next one, so a window 30 s before an addition is 30 s before it in
    every experiment. The gap on the shared axis is the shortest of the experiments;
    the spare middle of a longer gap is left out, and nothing is stretched. An
    experiment with another number of additions than most is left out.

    ---- Inputs ----
    traces : Sequence[dict]
        One per experiment: 'times_min' and 'values' (np.ndarray, (n_points,), the
        times increasing) and 'additions_min' (the times of its additions, in
        order).
    zero : Optional[int]
        Which addition is time 0 of the shared axis, from 0 (the last, when there
        are fewer); None to line the traces up on their clocks as they are.

    ---- Globals read ----
    STEPS_PER_MINUTE.

    ---- Outputs ----
    dict
        'times_min': the shared times, np.ndarray (n_times,); 'values': np.ndarray
        (n_kept, n_times), a row per experiment kept, NaN where it has no value;
        'kept' and 'left_out': the places in traces of the experiments kept and left
        out; 'additions_min': the shared times of the additions; 'breaks_min': the
        shared times where a spare middle was left out.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With a_i the time of addition i on an experiment's own clock, g_i the shortest
    gap a_(i+1) - a_i of the experiments and A_i the shared time of addition i (A of
    the addition picked = 0, A_(i+1) = A_i + g_i), a point at the own time x is at
    the shared time t:
        before the first addition:   t = A_0 + (x - a_0)
        first half of gap i:         t = A_i + (x - a_i),          t < A_i + g_i / 2
        second half of gap i:        t = A_(i+1) - (a_(i+1) - x),  t >= A_i + g_i / 2
        after the last addition:     t = A_last + (x - a_last)
    Before the first and after the last addition the axis goes as far as the
    shortest experiment does. The number of additions most experiments have is the
    one kept; with a tie, the one met first (MATHS.md section 10.2).

    ---- Helpers ----
    _pieces_lister
    _trace_interpolator
    """

    # ---- 1 The experiments with the number of additions most have --------------------
    places = list(range(len(traces)))
    if zero is None:
        kept = places
    else:
        counts = [len(trace['additions_min']) for trace in traces]
        most = Counter(counts).most_common(1)[0][0] if counts else 0
        kept = [place for place in places if counts[place] == most]
    left_out = [place for place in places if place not in kept]
    empty = {'times_min': np.array([]),
             'values': np.empty((len(kept), 0)),
             'kept': kept,
             'left_out': left_out,
             'additions_min': [],
             'breaks_min': [],
             }
    if not kept:
        return empty

    # ---- 2 The pieces of the shared axis ---------------------------------------------
    members = [traces[place] for place in kept]
    spans = [(float(trace['times_min'][0]), float(trace['times_min'][-1]))
             for trace in members
             ]
    pieces, additions, breaks = _pieces_lister(spans,
                                               [trace['additions_min']
                                                for trace in members
                                                ],
                                               zero,
                                               )

    # ---- 3 The shared times, each in the last piece that holds it --------------------
    piece_by_step: Dict[int, int] = {}
    for index, (start, end, _) in enumerate(pieces):
        first = int(np.ceil(start * STEPS_PER_MINUTE - 1e-6))
        last = int(np.floor(end * STEPS_PER_MINUTE + 1e-6))
        for step in range(first, last + 1):
            piece_by_step[step] = index
    if not piece_by_step:
        return empty
    steps = np.array(sorted(piece_by_step))
    times = steps / STEPS_PER_MINUTE
    owners = np.array([piece_by_step[step] for step in steps])

    # ---- 4 Each trace read at its own time of each shared time -----------------------
    values = np.full((len(members), len(times)), np.nan)
    for row, trace in enumerate(members):
        added = np.array([piece[2][row] for piece in pieces])[owners]
        values[row] = _trace_interpolator(np.asarray(trace['times_min'], dtype=float),
                                          np.asarray(trace['values'], dtype=float),
                                          times + added,
                                          )
    return {'times_min': times,
            'values': values,
            'kept': kept,
            'left_out': left_out,
            'additions_min': additions,
            'breaks_min': breaks,
            }


# ---- traces_averager -----------------------------------------------------------------
def traces_averager(values: np.ndarray) -> dict:
    """
    ---- Summary ----
    Main function to average lined-up traces at each shared time: the mean, the
    spread (SD) and the standard error of the mean (SEM) of the experiments that
    have a value there.

    ---- Inputs ----
    values : np.ndarray
        The traces, shape (n_experiments, n_times), NaN where one has no value.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        'mean', 'sd' and 'sem': np.ndarray (n_times,), NaN where no experiment has a
        value (the SD and the SEM also where only one has); 'n': np.ndarray
        (n_times,) of int, how many experiments have a value.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mean = (y_1 + ... + y_n) / n; SD = sqrt(((y_1 - mean)² + ... + (y_n - mean)²) /
    (n - 1)); SEM = SD / sqrt(n) (MATHS.md section 10.3).

    ---- Helpers ----
    None.
    """

    values = np.asarray(values, dtype=float)
    has_value = np.isfinite(values)
    count = has_value.sum(axis=0)
    filled = np.where(has_value, values, 0.0)
    mean = np.full(values.shape[1], np.nan)
    np.divide(filled.sum(axis=0), count, out=mean, where=count > 0)
    squares = np.where(has_value, (values - mean) ** 2, 0.0).sum(axis=0)
    spread = np.full(values.shape[1], np.nan)
    np.divide(squares, count - 1, out=spread, where=count > 1)
    spread = np.sqrt(spread)
    error = np.full(values.shape[1], np.nan)
    np.divide(spread, np.sqrt(count), out=error, where=count > 1)
    return {'mean': mean, 'sd': spread, 'sem': error, 'n': count}
