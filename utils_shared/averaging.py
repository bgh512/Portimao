"""
Event-window averaging of OCR and haem data for one experiment.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.delta_psi import DELTA_PSI_COLUMN
from utils_shared.schema import (DELTA_HAEM_SOURCES,
                                 HAEM_KEYS,
                                 measurement_column_finder,
                                 source_resolver,
                                 time_getter,
                                 value_getter,
                                 VO2_KEYS,
                                 )


# ---- CONSTANTS -----------------------------------------------------------------------
# What the window step keeps for a file. The settled windows: the length of every
# window and how long before the next addition each ends, in seconds, and whether there
# are any (1 or 0). The quick windows: the length of every window and how long after
# its addition each starts, in seconds, and whether there are any (1 or 0).
WINDOW_KEYS = ('window_s', 'gap_s', 'is_on', 'quick_s', 'delay_s', 'quick_is_on')
# The kinds of window: the baseline before the first addition, a settled window ending
# before the next addition, a quick window starting after its own addition.
WINDOW_KINDS = ('baseline', 'settled', 'quick')
# a window may end this much after the next addition and still fit (rounding of times)
FIT_TOLERANCE_MIN = 1e-9
# What a window set on its own may hold (each_window, DATA_FORMAT.md): its length and
# its gap before the next addition (the baseline and a settled window) or its start
# after its own addition (a quick window), in minutes, and whether it is used. The
# baseline is always used: every change is measured from it.
EACH_WINDOW_FIELDS = {'baseline': ('length_min', 'gap_min'),
                      'settled': ('length_min', 'gap_min', 'is_used'),
                      'quick': ('length_min', 'delay_min', 'is_used'),
                      }
# the problem of a window the user left out with its tick
LEFT_OUT_PROBLEM = 'Left out by you.'
# The shared values of the windows in the answers, which a file fixed by hand
# (file_windows, DATA_FORMAT.md) may hold its own of.
SHARED_WINDOW_ANSWERS = ('window_minutes',
                         'gap_minutes',
                         'final_gap_minutes',
                         'quick_minutes',
                         'delay_minutes',
                         )
# What the window step keeps for a file besides WINDOW_KEYS: how long before the end of
# the recording the last settled window ends (s); whether a drag or a typed number moves
# only the window touched (1) or every window of its kind (0); and the window of each
# kind last dragged with that on (its number, the baseline 0; -1 for none).
PICKED_KEYS = ('settled_picked', 'quick_picked')
STEP_EXTRA_KEYS = ('final_gap_s', 'each_is_on') + PICKED_KEYS
# In the window step a window's own value is kept as '<window>:<field>' ('average2:
# window_s', 'quick1:is_used'), and an edge of one window is dragged as
# '<field>@<window>' ('gap_s@average1').
OWN_SEPARATOR = ':'
EDGE_SEPARATOR = '@'
# The fields of the window step a window may hold its own of, by kind, and the field of
# each_window (minutes) each stands for.
STEP_OWN_FIELDS = {'settled': {'window_s': 'length_min', 'gap_s': 'gap_min'},
                   'quick': {'quick_s': 'length_min', 'delay_s': 'delay_min'},
                   }
NO_PICK = -1.0


# ---- AVERAGING HELPERS ---------------------------------------------------------------


# ---- _baseline_change_adder ----------------------------------------------------------
def _baseline_change_adder(window_stats: Dict[str, Dict[str, float]],
                           baseline_stats: Dict[str, Dict[str, float]],
                           percent_of_baseline: bool = True,
                           ) -> None:
    """
    ---- Summary ----
    Helper function to add the change from the baseline window to the statistics of a
    window.

    ---- Inputs ----
    window_stats : Dict[str, Dict[str, float]]
        Statistics of one window, from window_statistics_calculator; modified in place.
    baseline_stats : Dict[str, Dict[str, float]]
        Statistics of the baseline window (average0).
    percent_of_baseline : bool
        False for sources that already are a change from a reference (baseline near 0),
        where a percentage is meaningless.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    window_stats: adds "delta" and "change" to every column.

    ---- Equations ----
    delta = mean - baseline_mean; change = mean / baseline_mean x 100 (NaN if
    percent_of_baseline is False, the baseline is 0 or a value is not finite).

    ---- Helpers ----
    None.
    """

    # ---- 1 Add the change from the baseline ------------------------------------------
    for column, stats in window_stats.items():
        baseline = baseline_stats.get(column, {}).get('mean', np.nan)
        stats['delta'] = (stats['mean'] - baseline if np.isfinite(baseline) and
                          np.isfinite(stats['mean']) else np.nan
                          )
        usable = (np.isfinite(baseline)
                  and not np.isclose(baseline, 0.0)
                  and np.isfinite(stats['mean'])
                  )
        if not percent_of_baseline:
            stats['change'] = np.nan
        elif usable:
            stats['change'] = stats['mean'] / baseline * 100.0
        else:
            stats['change'] = np.nan


# ---- _delta_psi_statistics_calculator ------------------------------------------------
def _delta_psi_statistics_calculator(table: pd.DataFrame,
                                     start_time: float,
                                     end_time: float,
                                     ) -> Dict[str, float]:
    """
    ---- Summary ----
    Helper function to average delta psi inside a time window over the spectra that
    have a value, and to count them, as delta psi is empty wherever bH or bL is
    outside its limits.

    ---- Inputs ----
    table : pd.DataFrame
        experiment['delta_psi'] (DATA_FORMAT.md): a time column and DELTA_PSI_COLUMN
        in mV, NaN where it could not be worked out.
    start_time : float
        Window start, in minutes.
    end_time : float
        Window end, in minutes.

    ---- Globals read ----
    DELTA_PSI_COLUMN (imported).

    ---- Outputs ----
    Dict[str, float]
        {'mean', 'sd'} in mV as window_statistics_calculator gives them, with
        'spectra_used' (spectra of the window with a value) and 'spectra_in_window'
        (all its spectra).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mean and SD over the spectra with start_time <= t <= end_time and a finite value.

    ---- Helpers ----
    time_getter
    value_getter
    window_statistics_calculator
    """

    times = time_getter(table)
    in_window = np.isfinite(times) & (times >= start_time) & (times <= end_time)
    values = value_getter(table, DELTA_PSI_COLUMN)
    stats = window_statistics_calculator(table, start_time, end_time)[DELTA_PSI_COLUMN]
    stats['spectra_used'] = int(np.count_nonzero(in_window & np.isfinite(values)))
    stats['spectra_in_window'] = int(np.count_nonzero(in_window))
    return stats


# ---- _left_out_finder ----------------------------------------------------------------
def _left_out_finder(each_window: Dict[str, dict], name: str) -> bool:
    """
    ---- Summary ----
    Helper function to say whether the user left a window out with its tick.

    ---- Inputs ----
    each_window : Dict[str, dict]
        The windows set on their own (DATA_FORMAT.md, each_window).
    name : str
        The window's name ('average2', 'quick1'); the baseline 'average0' is never
        left out.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when its 'is_used' is false.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if name == 'average0':
        return False
    return not bool((each_window.get(name) or {}).get('is_used', True))


# ---- _own_minutes_reader -------------------------------------------------------------
def _own_minutes_reader(each_window: Dict[str, dict],
                        name: str,
                        field: str,
                        shared: float,
                        ) -> float:
    """
    ---- Summary ----
    Helper function to give a value of one window: its own when it was set on its own,
    otherwise the value shared by the windows of its kind.

    ---- Inputs ----
    each_window : Dict[str, dict]
        The windows set on their own (DATA_FORMAT.md, each_window).
    name : str
        The window's name ('average0', 'average2', 'quick1').
    field : str
        'length_min', 'gap_min' or 'delay_min'.
    shared : float
        The shared value, in minutes.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The value in minutes. Raises ValueError for a length of 0 or less, or a gap
        or start below 0.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    value = (each_window.get(name) or {}).get(field)
    if value is None:
        return float(shared)
    value = float(value)
    if field == 'length_min' and value <= 0:
        raise ValueError(f'The averaging region {name} must be longer than 0 min. '
                         'Correct it in the averaging step.',
                         )
    if value < 0:
        raise ValueError(f'The averaging region {name} cannot start or end on the '
                         'wrong side of its addition. Correct it in the averaging '
                         'step.',
                         )
    return value


# ---- WINDOW STEP HELPERS -------------------------------------------------------------


# ---- _edge_key_splitter --------------------------------------------------------------
def _edge_key_splitter(key: str) -> Tuple[str, Optional[str]]:
    """
    ---- Summary ----
    Helper function to split the key of an edge of the window step into its field and
    the window it belongs to.

    ---- Inputs ----
    key : str
        'gap_s@average1' for an edge of one window, or a field alone ('window_s',
        'final_gap_s', 'average2:is_used').

    ---- Globals read ----
    EDGE_SEPARATOR (module constant).

    ---- Outputs ----
    Tuple[str, Optional[str]]
        (field, window name), the window None for a field alone.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    field, _, window = key.partition(EDGE_SEPARATOR)
    return field, window or None


# ---- _picked_window_namer ------------------------------------------------------------
def _picked_window_namer(values: Dict[str, float], kind: str) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to name the window of one kind last dragged with "Adjust each
    window" on.

    ---- Inputs ----
    values : Dict[str, float]
        The values of one file in the window step.
    kind : str
        'settled' or 'quick'.

    ---- Globals read ----
    NO_PICK (module constant).

    ---- Outputs ----
    Optional[str]
        'average0' (the baseline), 'average2', 'quick1' ..., or None when none was
        dragged.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    number = int(round(values.get(f'{kind}_picked', NO_PICK)))
    if number < 0 or (kind == 'quick' and number == 0):
        return None
    return f"{'quick' if kind == 'quick' else 'average'}{number}"


# ---- _step_own_reader ----------------------------------------------------------------
def _step_own_reader(values: Dict[str, float]) -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to give the windows of one file set on their own in the window
    step, in the form of each_window (DATA_FORMAT.md).

    ---- Inputs ----
    values : Dict[str, float]
        The values of one file in the window step, the own values of a window under
        '<window>:<field>' in seconds, its tick under '<window>:is_used'.

    ---- Globals read ----
    OWN_SEPARATOR, STEP_OWN_FIELDS (module constants).

    ---- Outputs ----
    Dict[str, dict]
        {window name: {'length_min', 'gap_min' or 'delay_min', 'is_used'}}, sorted by
        name; a window ticked keeps no 'is_used', and the baseline never has one.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    minutes = seconds / 60.

    ---- Helpers ----
    None.
    """

    own: Dict[str, dict] = {}
    for key, value in values.items():
        name, separator, field = key.partition(OWN_SEPARATOR)
        if not separator:
            continue
        if field == 'is_used':
            if name != 'average0' and not value:
                own.setdefault(name, {})['is_used'] = False
            continue
        kind = 'quick' if name.startswith('quick') else 'settled'
        own_field = STEP_OWN_FIELDS[kind].get(field)
        if own_field is not None:
            own.setdefault(name, {})[own_field] = float(value) / 60.0
    return {name: own[name] for name in sorted(own)}


# ---- _window_edge_reader -------------------------------------------------------------
def _window_edge_reader(values: Dict[str, float],
                        field: str,
                        window: str,
                        time_min: float,
                        event_times_min: List[float],
                        recording_span_min: Tuple[float, float],
                        final_window_gap_minutes: float,
                        step_seconds: float,
                        ) -> float:
    """
    ---- Summary ----
    Helper function to turn where the mouse holds an edge of one named window into
    the value of its field, as window_pointer_reader does for the nearest window, with
    that window's own values.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step.
    field : str
        'window_s' or 'gap_s' (the baseline or a settled window), 'delay_s' or
        'quick_s' (a quick window).
    window : str
        The window's name ('average0', 'average2', 'quick1').
    time_min : float
        Time under the mouse on the time axis of the plot (min).
    event_times_min : List[float]
        Times of the file's additions on that axis (min), in order; at least one.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data on that axis (min).
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, when the
        values do not hold it, in minutes.
    step_seconds : float
        The step the result is rounded to, in seconds (> 0).

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The new value in seconds: a length of at least one step, a gap or a start of at
        least 0; the value as it is for a window the file does not have.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    window_s = end of the window - time; gap_s = the addition after it - time; delay_s
    = time - its addition; quick_s = time - its start; each x 60, rounded to whole
    steps.

    ---- Helpers ----
    _step_own_reader
    _window_number_finder
    quick_span_lister
    window_span_lister
    """

    own = _step_own_reader(values)
    number = _window_number_finder(window)
    if window.startswith('quick'):
        quick = {name: start
                 for name, start, _, _ in quick_span_lister(event_times_min,
                                                            recording_span_min,
                                                            values['quick_s'] / 60.0,
                                                            values['delay_s'] / 60.0,
                                                            own,
                                                            )
                 }
        if window not in quick:
            return float(values[field])
        if field == 'delay_s':
            seconds, lowest = (time_min - event_times_min[number - 1]) * 60.0, 0.0
        else:
            seconds, lowest = (time_min - quick[window]) * 60.0, step_seconds
        return max(round(seconds / step_seconds) * step_seconds, lowest)
    final = values.get('final_gap_s', final_window_gap_minutes * 60.0) / 60.0
    ends = {name: end
            for name, _, end, _ in window_span_lister(event_times_min,
                                                      recording_span_min,
                                                      values['window_s'] / 60.0,
                                                      values['gap_s'] / 60.0,
                                                      final,
                                                      each_window=own,
                                                      )
            }
    if window not in ends or (field == 'gap_s' and number >= len(event_times_min)):
        return float(values[field])
    if field == 'window_s':
        seconds, lowest = (ends[window] - time_min) * 60.0, step_seconds
    else:
        seconds, lowest = (event_times_min[number] - time_min) * 60.0, 0.0
    return max(round(seconds / step_seconds) * step_seconds, lowest)


# ---- _window_number_finder -----------------------------------------------------------
def _window_number_finder(name: str) -> int:
    """
    ---- Summary ----
    Helper function to give the number of a window from its name.

    ---- Inputs ----
    name : str
        'average0' (the baseline), 'average2', 'quick1' ...

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        The number at the end of the name: 0, 2, 1 ...

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    prefix = 'quick' if name.startswith('quick') else 'average'
    return int(name[len(prefix):])


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- baseline_percent_adder ----------------------------------------------------------
def baseline_percent_adder(experiment: dict) -> bool:
    """
    ---- Summary ----
    Main function to put the OCR of an experiment on its % of baseline and store it:
    every value divided by the average of the OCR in the baseline window (the window
    before the first addition, average0 of the averages). An experiment without a
    baseline gets no such table.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md, with its averages worked
        out (experiment_averages_calculator) and its OCR in experiment['VoO2'].

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the table was added. False when the experiment has no baseline
        window, no OCR, or an average in the baseline that is 0 or not a number; a
        table left by an earlier run is then taken away.

    ---- Globals mutated ----
    experiment: adds experiment['VoO2_baseline'], a copy of experiment['VoO2'] in % of
    baseline; its attrs['baseline_percent'] holds {'start_time', 'end_time': the
    baseline window (min), 'baseline_mean': {column: the average in it, µM min⁻¹}}.

    ---- Equations ----
    OCR (% of baseline) = OCR / mean(OCR in average0) x 100. The OCR per OD gives the
    same numbers, as the OD divides both.

    ---- Helpers ----
    measurement_column_finder
    value_getter
    window_statistics_calculator
    """

    # ---- 1 Find the baseline window and the OCR --------------------------------------
    experiment.pop('VoO2_baseline', None)
    windows = (experiment.get('averages') or {}).get('windows', {})
    baseline = windows.get('average0')
    source = experiment.get('VoO2')
    if baseline is None or not isinstance(source, pd.DataFrame) or source.empty:
        return False

    # ---- 2 Divide by the average in the baseline -------------------------------------
    start, end = baseline['start_time'], baseline['end_time']
    stats = window_statistics_calculator(source, start, end)
    table = source.copy()
    means = {}
    for column in measurement_column_finder(source):
        mean = stats[str(column)]['mean']
        if not np.isfinite(mean) or np.isclose(mean, 0.0):
            return False
        table[column] = value_getter(source, column) / mean * 100.0
        means[str(column)] = mean
    if not means:
        return False
    table.attrs['baseline_percent'] = {'start_time': start,
                                       'end_time': end,
                                       'baseline_mean': means,
                                       }
    experiment['VoO2_baseline'] = table
    return True


# ---- experiment_averages_calculator --------------------------------------------------
def experiment_averages_calculator(experiment: dict,
                                   window_minutes: float,
                                   gap_minutes: float,
                                   final_window_gap_minutes: float,
                                   baseline_minimum_seconds: float,
                                   vo2_source: Optional[str] = 'od',
                                   haem_source: Optional[str] = 'abs',
                                   quick_minutes: Optional[float] = None,
                                   delay_minutes: float = 0.0,
                                   is_settled: bool = True,
                                   haem_views: Optional[Dict[str, str]] = None,
                                   each_window: Optional[Dict[str, dict]] = None,
                                   ) -> dict:
    """
    ---- Summary ----
    Main function to calculate event-window statistics for VoO2 and haem data and store
    them in the experiment: the baseline, the settled windows (ending before the next
    addition) and, when asked for, the quick windows (starting after each addition),
    each with its own length, gap or start where it has them. Every view of the haems
    asked for, and delta psi when the experiment has it, are averaged in the same
    windows. A window the user left out is kept among the skipped ones, marked so.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    window_minutes : float
        Length of each averaging window, in minutes (> 0).
    gap_minutes : float
        How long before the next addition each window ends, in minutes (>= 0).
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, in minutes (>=
        0).
    baseline_minimum_seconds : float
        Least time the data inside the baseline window (average0) must span, in
        seconds (>= 0).
    vo2_source : Optional[str]
        VoO2 source key (e.g. 'od', 'raw', 'percent'); None leaves VoO2 out.
    haem_source : Optional[str]
        Haem source key (e.g. 'abs', 'delta_abs_od'); None leaves the haems out.
    quick_minutes : Optional[float]
        Length of each quick window, in minutes (> 0); None for no quick windows.
    delay_minutes : float
        How long after its addition each quick window starts, in minutes (>= 0).
    is_settled : bool
        False leaves the settled windows out (the baseline stays).
    haem_views : Optional[Dict[str, str]]
        {view: haem source} of every way the haems can be shown
        (Config.haem_view_lister); a view whose table the experiment does not have is
        left out. None averages no views.
    each_window : Optional[Dict[str, dict]]
        The windows of this file set on their own (DATA_FORMAT.md, each_window), as
        window_plan_finder gives them; None for none.

    ---- Globals read ----
    schema.VO2_KEYS, HAEM_KEYS and DELTA_HAEM_SOURCES; DELTA_PSI_COLUMN;
    LEFT_OUT_PROBLEM (module constant).

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError for invalid settings, no
        source, no events or invalid times. A window that does not fit between two
        additions (or after the last one) is skipped, not an error; so is the baseline
        window when it holds too little data, and the run then has no baseline: the
        delta and change of every window are NaN.

    ---- Globals mutated ----
    experiment: adds experiment["averages"] = {"settings", "windows", "skipped"}
    (layout in DATA_FORMAT.md).

    ---- Equations ----
    Each window's own length, gap and start stand in for the shared ones below where
    it has them. average0 ends gap_minutes before the first event and starts
    window_minutes before its end, or at the start of the recording when that is
    later; it is skipped when the points inside it span less than
    baseline_minimum_seconds. averageN ends gap_minutes before event N+1
    (final_window_gap_minutes before the end of the recording for the last event);
    each window starts window_minutes before its end and is skipped when that is
    before its own event. quickN starts delay_minutes after event N and ends
    quick_minutes later; it is skipped when that is after event N+1 (the end of the
    recording for the last event). change = mean /
    mean(average0) x 100 (NaN for delta abs sources); delta = mean - mean(average0),
    for the settled and the quick windows alike. The haem views and delta psi have a
    delta only (their change is NaN).

    ---- Helpers ----
    _baseline_change_adder
    _delta_psi_statistics_calculator
    quick_span_lister
    source_resolver
    time_getter
    window_span_lister
    window_statistics_calculator
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    name = experiment['experiment_name']
    if window_minutes <= 0:
        raise ValueError('The averaging region must be longer than 0 min. Correct it '
                         'where the program asks for it.',
                         )
    if gap_minutes < 0 or final_window_gap_minutes < 0:
        raise ValueError('The gap before an averaging region cannot be negative. '
                         'Correct it where the program asks for it.',
                         )
    if baseline_minimum_seconds < 0:
        raise ValueError('The least length of the baseline cannot be negative. '
                         'Correct it in config.py.',
                         )
    if quick_minutes is not None and quick_minutes <= 0:
        raise ValueError('The quick averaging region must be longer than 0 min. '
                         'Correct it where the program asks for it.',
                         )
    if delay_minutes < 0:
        raise ValueError('A quick averaging region cannot start before its addition. '
                         'Correct it where the program asks for it.',
                         )
    if vo2_source is None and haem_source is None:
        raise ValueError(f'{name}: there is nothing to average, neither oxygen '
                         'consumption nor haems.',
                         )

    # ---- 2 Resolve the data sources --------------------------------------------------
    vo2_key, vo2_df = (source_resolver(experiment, vo2_source, VO2_KEYS, 'VO2')
                       if vo2_source
                       else (None, None)
                       )
    haem_key, haem_df = (source_resolver(experiment, haem_source, HAEM_KEYS, 'haem')
                         if haem_source
                         else (None, None)
                         )
    # the table each view was averaged from says its unit (per OD or not)
    view_tables, view_keys = {}, {}
    for view, source in (haem_views or {}).items():
        table = experiment.get(HAEM_KEYS.get(source, ''))
        if isinstance(table, pd.DataFrame) and not table.empty:
            view_tables[view] = table
            view_keys[view] = HAEM_KEYS[source]
    psi_table = experiment.get('delta_psi')
    if not isinstance(psi_table, pd.DataFrame) or psi_table.empty:
        psi_table = None

    # ---- 3 Define the windows --------------------------------------------------------
    events = sorted(experiment['metadata'].get('events', []),
                    key=lambda event: event['time'],
                    )
    if not events:
        raise ValueError(f'{name}: none of the additions has a time, so there is '
                         'nothing to average around.',
                         )
    reference_df = vo2_df if vo2_df is not None else haem_df
    reference_times = time_getter(reference_df)
    if not np.any(np.isfinite(reference_times)):
        raise ValueError(f'{name}: the times of the values could not be read, so '
                         'they cannot be averaged.',
                         )
    recording_start = float(np.nanmin(reference_times))
    recording_end = float(np.nanmax(reference_times))
    # The baseline window never reaches back before the recording, and counts only
    # when its data span long enough to be a level and not a few points.
    own = {name: dict(values) for name, values in (each_window or {}).items()}
    spans = window_span_lister([float(event['time']) for event in events],
                               (recording_start, recording_end),
                               window_minutes,
                               gap_minutes,
                               final_window_gap_minutes,
                               each_window=own,
                               )
    _, baseline_start, baseline_end, _ = spans[0]
    inside = reference_times[np.isfinite(reference_times)
                             & (reference_times >= baseline_start)
                             & (reference_times <= baseline_end)
                             ]
    span_seconds = float(inside.max() - inside.min()) * 60.0 if inside.size else 0.0
    boundaries = []
    skipped: Dict[str, dict] = {}
    if span_seconds < baseline_minimum_seconds - 1e-9:
        skipped['average0'] = {'start_time': baseline_start,
                               'end_time': baseline_end,
                               'reason': f'Less than {baseline_minimum_seconds:g} s of '
                                         'data before the first addition.',
                               }
    else:
        boundaries.append(('average0', baseline_start, baseline_end, 'baseline'))
    kind_spans = [('settled', span) for span in spans[1:]] if is_settled else []
    if quick_minutes is not None:
        kind_spans += [('quick', span)
                       for span in quick_span_lister([float(event['time'])
                                                      for event in events
                                                      ],
                                                     (recording_start, recording_end),
                                                     quick_minutes,
                                                     delay_minutes,
                                                     own,
                                                     )
                       ]
    for kind, (window_name, start, end, problem) in kind_spans:
        if problem is not None:
            skipped[window_name] = {'start_time': start,
                                    'end_time': end,
                                    'reason': problem,
                                    'kind': kind,
                                    'left_out': problem == LEFT_OUT_PROBLEM,
                                    }
        else:
            boundaries.append((window_name, start, end, kind))
    if 'average0' in skipped:
        skipped['average0']['kind'] = 'baseline'

    # ---- 4 Calculate the window statistics -------------------------------------------
    windows = {}
    for window_name, start, end, kind in boundaries:
        windows[window_name] = {'start_time': start,
                                'end_time': end,
                                'kind': kind,
                                'vo2': window_statistics_calculator(vo2_df, start, end)
                                if vo2_df is not None
                                else {},
                                'haem': window_statistics_calculator(haem_df,
                                                                     start,
                                                                     end,
                                                                     )
                                if haem_df is not None
                                else {},
                                'haem_views': {view: window_statistics_calculator(table,
                                                                                  start,
                                                                                  end,
                                                                                  )
                                               for view, table in view_tables.items()
                                               },
                                }
        if psi_table is not None:
            windows[window_name]['delta_psi'] = _delta_psi_statistics_calculator(
                psi_table,
                start,
                end,
                )

    # ---- 5 Store the results ---------------------------------------------------------
    baseline = windows.get('average0', {'vo2': {}, 'haem': {}})  # none: all NaN
    haem_is_absolute = haem_source not in DELTA_HAEM_SOURCES
    for window in windows.values():
        _baseline_change_adder(window['vo2'], baseline['vo2'])
        _baseline_change_adder(window['haem'],
                               baseline['haem'],
                               percent_of_baseline=haem_is_absolute,
                               )
        # A haem view or delta psi has no level a percentage could be taken of: only
        # its difference from the baseline is kept.
        for view, stats in window['haem_views'].items():
            _baseline_change_adder(stats,
                                   baseline.get('haem_views', {}).get(view, {}),
                                   percent_of_baseline=False,
                                   )
        if 'delta_psi' in window:
            _baseline_change_adder({'delta_psi': window['delta_psi']},
                                   {'delta_psi': baseline.get('delta_psi', {})},
                                   percent_of_baseline=False,
                                   )
    final_gap = final_window_gap_minutes
    experiment['averages'] = {'settings': {'window_minutes': window_minutes,
                                           'gap_minutes': gap_minutes,
                                           'final_window_gap_minutes': final_gap,
                                           'vo2_source': vo2_source,
                                           'vo2_key': vo2_key,
                                           'haem_source': haem_source,
                                           'haem_key': haem_key,
                                           'haem_view_keys': view_keys,
                                           'baseline_minimum_seconds':
                                               baseline_minimum_seconds,
                                           'quick_minutes': quick_minutes,
                                           'delay_minutes': delay_minutes,
                                           'is_settled': is_settled,
                                           'each_window': own,
                                           },
                              'windows': windows,
                              'skipped': skipped,
                              }
    return experiment


# ---- kind_span_lister ----------------------------------------------------------------
def kind_span_lister(kind: str,
                     event_times_min: List[float],
                     recording_span_min: Tuple[float, float],
                     window_minutes: float,
                     gap_minutes: float,
                     final_window_gap_minutes: float,
                     quick_minutes: float,
                     delay_minutes: float,
                     each_window: Optional[Dict[str, dict]] = None,
                     ) -> List[Tuple[str, float, float, Optional[str]]]:
    """
    ---- Summary ----
    Main function to give the windows a figure that uses one kind of window averages
    over: the baseline, then the window of that kind of each addition, all under the
    names of the settled windows, so the figure reads either kind in the same way.
    Each window keeps its own length, gap or start and its tick where it has them.

    ---- Inputs ----
    kind : str
        'settled' or 'quick'.
    event_times_min : List[float]
        Times of the additions (min), in order; at least one.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data (min).
    window_minutes : float
        Length of the baseline and of each settled window, in minutes.
    gap_minutes : float
        How long before the next addition the baseline and each settled window end, in
        minutes.
    final_window_gap_minutes : float
        How long before the end of the recording the last settled window ends, in
        minutes.
    quick_minutes : float
        Length of each quick window, in minutes.
    delay_minutes : float
        How long after its addition each quick window starts, in minutes.
    each_window : Optional[Dict[str, dict]]
        The windows set on their own (DATA_FORMAT.md, each_window), under their own
        names ('quick1'); None for none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, float, float, Optional[str]]]
        [(name, start, end, problem)] in minutes: 'average0' (the baseline), then
        'average1' for the first addition and so on, as window_span_lister gives them.
        Raises ValueError for a kind that is neither.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    quick_span_lister
    window_span_lister
    """

    if kind not in ('settled', 'quick'):
        raise ValueError(f'The kind of averaging region {kind!r} is not known.')
    spans =window_span_lister(event_times_min,
                              recording_span_min,
                              window_minutes,
                              gap_minutes,
                              final_window_gap_minutes,
                              each_window=each_window,
                              )
    if kind == 'settled':
        return spans
    quick = quick_span_lister(event_times_min,
                              recording_span_min,
                              quick_minutes,
                              delay_minutes,
                              each_window,
                              )
    return spans[:1] + [(f'average{index}', start, end, problem)
                        for index, (_, start, end, problem) in enumerate(quick, start=1)
                        ]


# ---- quick_span_lister ---------------------------------------------------------------
def quick_span_lister(event_times_min: List[float],
                      recording_span_min: Tuple[float, float],
                      quick_minutes: float,
                      delay_minutes: float,
                      each_window: Optional[Dict[str, dict]] = None,
                      ) -> List[Tuple[str, float, float, Optional[str]]]:
    """
    ---- Summary ----
    Main function to give where the quick windows of one file fall, and which do not
    fit or were left out: one window starting a set time after each addition, each
    with its own length and start where it has them. The averaging and the plot of the
    window step both use it.

    ---- Inputs ----
    event_times_min : List[float]
        Times of the additions (min), in order.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data (min).
    quick_minutes : float
        Length of each quick window, in minutes.
    delay_minutes : float
        How long after its addition each quick window starts, in minutes.
    each_window : Optional[Dict[str, dict]]
        {window name: {'length_min', 'delay_min', 'is_used'}} of the windows set on
        their own (DATA_FORMAT.md, each_window); a value not given is the shared one.
        None for none.

    ---- Globals read ----
    FIT_TOLERANCE_MIN and LEFT_OUT_PROBLEM (module constants).

    ---- Outputs ----
    List[Tuple[str, float, float, Optional[str]]]
        [(name, start, end, problem)] in minutes, 'quick1' after the first addition and
        so on. The problem is None for a window that fits, LEFT_OUT_PROBLEM for one
        left out, or one sentence saying why it does not fit.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    quickN: start = addition N + its delay; end = start + its length; it does not fit
    when end > addition N + 1 (the end of the recording for the last addition).

    ---- Helpers ----
    _left_out_finder
    _own_minutes_reader
    """

    own = each_window or {}
    _, recording_end = recording_span_min
    spans = []
    for i, event_time in enumerate(event_times_min):
        name = f'quick{i + 1}'
        if i + 1 < len(event_times_min):
            limit = event_times_min[i + 1]
            problem = f'Insufficient time between additions {i + 1} and {i + 2}.'
        else:
            limit = recording_end
            problem = 'Insufficient recording time after the final addition.'
        start = event_time + _own_minutes_reader(own, name, 'delay_min', delay_minutes)
        end = start + _own_minutes_reader(own, name, 'length_min', quick_minutes)
        if _left_out_finder(own, name):
            problem = LEFT_OUT_PROBLEM
        elif end <= limit + FIT_TOLERANCE_MIN:
            problem = None
        spans.append((name, start, end, problem))
    return spans


# ---- window_kind_picker --------------------------------------------------------------
def window_kind_picker(averages: dict, kind: str) -> dict:
    """
    ---- Summary ----
    Main function to give a figure that uses one kind of window the averages of an
    experiment with the baseline and the windows of that kind only, the quick windows
    under the names of the settled ones, so the figure reads either kind in the same
    way.

    ---- Inputs ----
    averages : dict
        experiment['averages'] (DATA_FORMAT.md); not changed.
    kind : str
        'settled' or 'quick'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        A copy of the averages whose 'windows' and 'skipped' hold the baseline
        ('average0') and the windows of the kind, named 'average1' ... by the number
        of their addition. Raises ValueError for a kind that is neither.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if kind not in ('settled', 'quick'):
        raise ValueError(f'The kind of averaging region {kind!r} is not known.')
    picked =dict(averages)
    for key in ('windows', 'skipped'):
        picked[key] = {}
        for name, window in averages.get(key, {}).items():
            # a record without a kind is the baseline or a settled window
            own = window.get('kind', 'baseline' if name == 'average0' else 'settled')
            if own in ('baseline', kind):
                picked[key][name.replace('quick', 'average')] = window
    return picked


# ---- window_layout_finder ------------------------------------------------------------
def window_layout_finder(values: Dict[str, float],
                         event_times_min: List[float],
                         recording_span_min: Tuple[float, float],
                         final_window_gap_minutes: float,
                         baseline_minimum_seconds: float,
                         ) -> Tuple[List[Tuple[str, float, str, str]],
                                    List[Tuple[float, float, str]],
                                    ]:
    """
    ---- Summary ----
    Main function to give what the window step draws on the plot of one file: the two
    edges of every averaging window, each with its own values, and the windows as parts
    to shade, those that do not fit and those left out apart. The first window of each
    kind carries the words. The baseline is there when either kind of window is
    switched on.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step: WINDOW_KEYS, and where set
        final_gap_s and the windows' own values ('average2:window_s',
        'quick1:is_used').
    event_times_min : List[float]
        Times of the file's additions on the time axis of the plot (min), in order,
        not those marked ignore.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data on that axis (min).
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, in minutes,
        when the values hold no final_gap_s.
    baseline_minimum_seconds : float
        Least length of the baseline window, in seconds.

    ---- Globals read ----
    EDGE_SEPARATOR, LEFT_OUT_PROBLEM, OWN_SEPARATOR (module constants).

    ---- Outputs ----
    Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
        ([(key, time in min, words, kind)], [(start, end, kind)]). The key of an edge
        names its window ('window_s@average1'). The baseline and the settled windows
        first: the start of each is an edge of 'window_s' (kind 'baseline' for the
        baseline, with the words "baseline" and its length, 'average' for a settled
        window), the end of each but the last settled window an edge of 'gap_s' (kind
        'baseline_end' or 'average_end'), and the end of the last settled window the
        edge 'final_gap_s' (kind 'average_end'). Then the quick windows: the start of
        each is an edge of 'delay_s' (kind 'quick'), its end an edge of 'quick_s'
        (kind 'quick_end'). A part has the kind 'baseline', 'average', 'quick',
        'average_unfit' for a window that does not fit, 'left_out' for one left
        out, or 'not_picked' for a window other than the one picked while "Adjust
        region manually" is on; the last two have no edges. Both lists are empty when
        both kinds are switched off or the file has no additions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _step_own_reader
    quick_span_lister
    window_span_lister
    """

    # ---- 1 The windows of the file ---------------------------------------------------
    is_settled, is_quick = bool(values['is_on']), bool(values['quick_is_on'])
    if not (is_settled or is_quick) or not event_times_min:
        return [], []
    own = _step_own_reader(values)
    final_s = values.get('final_gap_s', final_window_gap_minutes * 60.0)
    spans = window_span_lister(event_times_min,
                               recording_span_min,
                               values['window_s'] / 60.0,
                               values['gap_s'] / 60.0,
                               final_s / 60.0,
                               baseline_minimum_seconds,
                               each_window=own,
                               )
    if not is_settled:
        spans = spans[:1]  # the baseline only

    # ---- 2 The baseline and the settled windows --------------------------------------
    # The baseline says what it is; the words of the settled windows are on the first
    # of them used, or on the baseline when it stands alone. With "Adjust region
    # manually" on, only the window picked has edges and words; the others are grey.
    edges, parts = [], []
    picked = (_picked_window_namer(values, 'settled')
              if values.get('each_is_on') and is_settled
              else None
              )
    if picked is not None and picked not in [span[0] for span in spans]:
        picked = None
    worded = picked or (None if is_settled else 'average0')
    for index, (name, start, end, problem) in enumerate(spans):
        if problem == LEFT_OUT_PROBLEM:
            parts.append((start, end, 'left_out'))
            continue
        if picked is not None and name != picked:
            if end > start:
                parts.append((start, end, 'not_picked'))
            continue
        kind = 'baseline' if index == 0 else 'average'
        length_s = values.get(f'{name}{OWN_SEPARATOR}window_s', values['window_s'])
        gap_s = values.get(f'{name}{OWN_SEPARATOR}gap_s', values['gap_s'])
        if index == 0:
            words = f'baseline {round(length_s, 2):g} s'
        elif worded is None or name == worded:
            worded = name
            words = f'region {round(length_s, 2):g} s'
        else:
            words = ''
        edges.append((f'window_s{EDGE_SEPARATOR}{name}', start, words, kind))
        if is_settled and index == len(spans) - 1:
            words = f'ends {round(final_s, 2):g} s before the end of the file'
            edges.append(('final_gap_s', end, words, 'average_end'))
        else:
            words = (f'ends {round(gap_s, 2):g} s before the addition'
                     if name == worded
                     else ''
                     )
            edges.append((f'gap_s{EDGE_SEPARATOR}{name}', end, words, f'{kind}_end'))
        if end > start:
            parts.append((start, end, kind if problem is None else 'average_unfit'))
    if not is_quick:
        return edges, parts

    # ---- 3 The quick windows ---------------------------------------------------------
    quick = quick_span_lister(event_times_min,
                              recording_span_min,
                              values['quick_s'] / 60.0,
                              values['delay_s'] / 60.0,
                              own,
                              )
    worded = None
    for name, start, end, problem in quick:
        if problem == LEFT_OUT_PROBLEM:
            parts.append((start, end, 'left_out'))
            continue
        is_first, worded = worded is None, worded or name
        delay_s = values.get(f'{name}{OWN_SEPARATOR}delay_s', values['delay_s'])
        length_s = values.get(f'{name}{OWN_SEPARATOR}quick_s', values['quick_s'])
        words = f'starts {round(delay_s, 2):g} s after the addition' if is_first else ''
        edges.append((f'delay_s{EDGE_SEPARATOR}{name}', start, words, 'quick'))
        words = f'quick region {round(length_s, 2):g} s' if is_first else ''
        edges.append((f'quick_s{EDGE_SEPARATOR}{name}', end, words, 'quick_end'))
        parts.append((start, end, 'quick' if problem is None else 'average_unfit'))
    return edges, parts


# ---- window_plan_finder --------------------------------------------------------------
def window_plan_finder(answers: dict, file_name: str) -> dict:
    """
    ---- Summary ----
    Main function to give the averaging windows of one file: those of a file fixed by
    hand when it was, otherwise those shared by the dataset, with every window set on
    its own.

    ---- Inputs ----
    answers : dict
        The answers of the run: the shared values (SHARED_WINDOW_ANSWERS),
        'each_window' and 'file_windows' (DATA_FORMAT.md); the last two may be missing
        (a dataset saved before windows could be set on their own).
    file_name : str
        The file's name without its ending, as experiment_name.

    ---- Globals read ----
    SHARED_WINDOW_ANSWERS (module constant).

    ---- Outputs ----
    dict
        {'window_minutes', 'gap_minutes', 'final_gap_minutes', 'quick_minutes',
        'delay_minutes': floats in minutes, 'each_window': {window name: {...}}}, a
        copy. A file fixed by hand takes from the dataset any value it does not hold.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    own = (answers.get('file_windows') or {}).get(file_name)
    if not isinstance(own, dict):
        own = {}
    plan = {key: float(own.get(key, answers[key])) for key in SHARED_WINDOW_ANSWERS}
    windows = own['each_window'] if 'each_window' in own else answers.get('each_window')
    plan['each_window'] = {name: dict(values)
                           for name, values in (windows or {}).items()
                           }
    return plan


# ---- window_plan_reader --------------------------------------------------------------
def window_plan_reader(values: Dict[str, float]) -> dict:
    """
    ---- Summary ----
    Main function to give the averaging windows of one file as the window step holds
    them, in the form window_plan_finder gives: the inverse of window_values_maker.

    ---- Inputs ----
    values : Dict[str, float]
        The values of one file in the window step (WINDOW_KEYS, STEP_EXTRA_KEYS and
        the windows' own values).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {'window_minutes', 'gap_minutes', 'final_gap_minutes', 'quick_minutes',
        'delay_minutes': floats in minutes, 'each_window': {window name: {...}}}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    minutes = seconds / 60.

    ---- Helpers ----
    _step_own_reader
    """

    return {'window_minutes': values['window_s'] / 60.0,
            'gap_minutes': values['gap_s'] / 60.0,
            'final_gap_minutes': values['final_gap_s'] / 60.0,
            'quick_minutes': values['quick_s'] / 60.0,
            'delay_minutes': values['delay_s'] / 60.0,
            'each_window': _step_own_reader(values),
            }


# ---- window_pointer_reader -----------------------------------------------------------
def window_pointer_reader(values: Dict[str, float],
                          key: str,
                          time_min: float,
                          event_times_min: List[float],
                          recording_span_min: Tuple[float, float],
                          final_window_gap_minutes: float,
                          step_seconds: float,
                          ) -> float:
    """
    ---- Summary ----
    Main function to turn where the mouse holds an edge of an averaging window into
    the value of its field, in seconds rounded to whole steps: for a settled window
    its length (a start edge) or how long before the next addition it ends (an end
    edge); for a quick window how long after its addition it starts (a start edge) or
    its length (an end edge); for the end of the last settled window how long before
    the end of the recording it ends. An edge whose key names its window is that
    window's, with its own values; otherwise the edge held is the one of its kind
    nearest the mouse, which stays the same edge while it follows the mouse.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step (WINDOW_KEYS, and where set
        final_gap_s and the windows' own values).
    key : str
        'window_s' for the start and 'gap_s' for the end of a settled window or the
        baseline, 'delay_s' for the start and 'quick_s' for the end of a quick window,
        each with '@' and its window where it names one ('gap_s@average1'), or
        'final_gap_s'.
    time_min : float
        Time under the mouse on the time axis of the plot (min).
    event_times_min : List[float]
        Times of the file's additions on that axis (min), in order.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data on that axis (min).
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, in minutes.
    step_seconds : float
        The step the result is rounded to, in seconds (> 0).

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The new value of the field, in seconds: a length of at least one step, or a
        gap or a start after the addition of at least 0. The value as it is when the
        file has no edge of that kind.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    length_s = round((end of the window held - time) x 60 / step) x step;
    gap_s = round((addition after the window held - time) x 60 / step) x step, with
    the addition after a window = its end + the gap now;
    delay_s = round((time - addition of the quick window held) x 60 / step) x step,
    with the addition of a quick window = its start - the delay now;
    quick_s = round((time - start of the quick window held) x 60 / step) x step;
    final_gap_s = round((end of the recording - time) x 60 / step) x step.

    ---- Helpers ----
    _edge_key_splitter
    _window_edge_reader
    quick_span_lister
    window_span_lister
    """

    field, window = _edge_key_splitter(key)
    if not event_times_min:
        return values[field]
    if field == 'final_gap_s':
        seconds = (recording_span_min[1] - time_min) * 60.0
        return max(round(seconds / step_seconds) * step_seconds, 0.0)
    if window is not None:
        return _window_edge_reader(values,
                                   field,
                                   window,
                                   time_min,
                                   event_times_min,
                                   recording_span_min,
                                   final_window_gap_minutes,
                                   step_seconds,
                                   )
    if key in ('delay_s', 'quick_s'):
        delay_minutes = values['delay_s'] / 60.0
        quick = quick_span_lister(event_times_min,
                                  recording_span_min,
                                  values['quick_s'] / 60.0,
                                  delay_minutes,
                                  )
        if key == 'delay_s':
            _, start, _, _ = min(quick, key=lambda span: abs(span[1] - time_min))
            seconds = (time_min - (start - delay_minutes)) * 60.0
            return max(round(seconds / step_seconds) * step_seconds, 0.0)
        _, start, _, _ = min(quick, key=lambda span: abs(span[2] - time_min))
        seconds = (time_min - start) * 60.0
        return max(round(seconds / step_seconds) * step_seconds, step_seconds)
    gap_minutes = values['gap_s'] / 60.0
    spans = window_span_lister(event_times_min,
                               recording_span_min,
                               values['window_s'] / 60.0,
                               gap_minutes,
                               final_window_gap_minutes,
                               )
    if not values['is_on']:
        spans = spans[:1]  # only the baseline has edges
    if key == 'window_s':
        _, _, end, _ = min(spans, key=lambda span: abs(span[1] - time_min))
        seconds = (end - time_min) * 60.0
        return max(round(seconds / step_seconds) * step_seconds, step_seconds)
    # the end of the last settled window cannot be pulled
    ends = spans[:-1] if values['is_on'] else spans
    _, _, end, _ = min(ends, key=lambda span: abs(span[2] - time_min))
    seconds = (end + gap_minutes - time_min) * 60.0
    return max(round(seconds / step_seconds) * step_seconds, 0.0)


# ---- window_row_teller ---------------------------------------------------------------
def window_row_teller(values: Dict[str, float],
                      addition_count: int,
                      ) -> List[Tuple[str, List[Tuple[str, str, bool]]]]:
    """
    ---- Summary ----
    Main function to give what each row of the window step shows for the file shown: a
    numbered tick for each window of its kind ("Use: 1 2 3"), to leave it out. The
    quick windows are hidden for now, so their row is always empty.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step.
    addition_count : int
        How many additions the file has (one window of each kind for each).

    ---- Globals read ----
    OWN_SEPARATOR (module constant).

    ---- Outputs ----
    List[Tuple[str, List[Tuple[str, str, bool]]]]
        [(note, [(field, words, is_ticked)])] for the settled row, then the quick row:
        the note is always empty, and the ticks ('average1:is_used', '1', True) ...
        A row whose kind is switched off has none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    rows = []
    for kind, switch, prefix in (('settled', 'is_on', 'average'),
                                 ('quick', 'quick_is_on', 'quick'),
                                 ):
        if not values.get(switch) or kind == 'quick':
            rows.append(('', []))
            continue
        note = ''
        ticks = []
        for number in range(1, addition_count + 1):
            field = f'{prefix}{number}{OWN_SEPARATOR}is_used'
            ticks.append((field, str(number), bool(values.get(field, 1.0))))
        rows.append((note, ticks))
    return rows


# ---- window_pick_lister --------------------------------------------------------------
def window_pick_lister(values: Dict[str, float],
                       addition_count: int,
                       ) -> Tuple[List[Tuple[str, float, str, bool]], str]:
    """
    ---- Summary ----
    Main function to give the buttons beside "Adjust region manually" for the file
    shown, one per window of the baseline and the settled windows, and the note beside
    them: while it is on, the window picked is the only one that changes.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step.
    addition_count : int
        How many additions the file has (one settled window for each).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[List[Tuple[str, float, str, bool]], str]
        ([(field, value, words, is_picked)], note): the field set by a click
        ('settled_picked') and its value (0 the baseline, 1 the first window ...),
        the words ('Baseline', '1' ...) and whether it is the window picked; the note
        says when the last window is picked that its time is before the end of the
        file. Both empty while "Adjust region manually" is off, the windows are
        switched off or the file has no additions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _picked_window_namer
    _window_number_finder
    """

    if not (values.get('each_is_on') and values.get('is_on')) or addition_count < 1:
        return [], ''
    name = _picked_window_namer(values, 'settled')
    number = _window_number_finder(name) if name is not None else -1
    picks = [('settled_picked',
              float(index),
              'Baseline' if index == 0 else str(index),
              index == number,
              )
             for index in range(addition_count + 1)
             ]
    note = ('the last region: its time is before the end of the file'
            if number == addition_count
            else ''
            )
    return picks, note


# ---- window_shown_maker --------------------------------------------------------------
def window_shown_maker(values: Dict[str, float],
                       addition_count: Optional[int] = None,
                       ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to give the values the boxes of the window step show in place of
    the shared ones: with "Adjust region manually" on, those of the window of each
    kind picked. For the last settled window the second box shows how long before the
    end of the file it ends.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step.
    addition_count : Optional[int]
        How many additions the file has, to know its last window; None for not known.

    ---- Globals read ----
    OWN_SEPARATOR, STEP_OWN_FIELDS (module constants).

    ---- Outputs ----
    Dict[str, float]
        {field: value in seconds} of the fields shown otherwise; empty with "Adjust
        region manually" off or no window picked.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _picked_window_namer
    _window_number_finder
    """

    shown: Dict[str, float] = {}
    if not values.get('each_is_on'):
        return shown
    for kind, fields in STEP_OWN_FIELDS.items():
        name = _picked_window_namer(values, kind)
        if name is None:
            continue
        for field in fields:
            shown[field] = values.get(f'{name}{OWN_SEPARATOR}{field}', values[field])
        if (kind == 'settled' and
                addition_count is not None and
                _window_number_finder(name) == addition_count and
                'final_gap_s' in values
                ):
            shown['gap_s'] = values['final_gap_s']
    return shown


# ---- window_span_lister --------------------------------------------------------------
def window_span_lister(event_times_min: List[float],
                       recording_span_min: Tuple[float, float],
                       window_minutes: float,
                       gap_minutes: float,
                       final_window_gap_minutes: float,
                       baseline_minimum_seconds: float = 0.0,
                       each_window: Optional[Dict[str, dict]] = None,
                       ) -> List[Tuple[str, float, float, Optional[str]]]:
    """
    ---- Summary ----
    Main function to give where the averaging windows of one file fall, and which do
    not fit or were left out: the baseline window before the first addition, then one
    window after each addition, each with its own length and gap where it has them.
    The averaging and the plot of the window step both use it.

    ---- Inputs ----
    event_times_min : List[float]
        Times of the additions (min), in order; at least one.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data (min).
    window_minutes : float
        Length of each window, in minutes.
    gap_minutes : float
        How long before the next addition each window ends, in minutes.
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, in minutes.
    baseline_minimum_seconds : float
        Least length of the baseline window, in seconds; 0 (the standard) never finds
        it too short, for a caller that checks the data inside it itself.
    each_window : Optional[Dict[str, dict]]
        {window name: {'length_min', 'gap_min', 'is_used'}} of the windows set on
        their own (DATA_FORMAT.md, each_window); a value not given is the shared one.
        The gap of the last window is always final_window_gap_minutes. None for none.

    ---- Globals read ----
    LEFT_OUT_PROBLEM (module constant).

    ---- Outputs ----
    List[Tuple[str, float, float, Optional[str]]]
        [(name, start, end, problem)] in minutes, 'average0' (the baseline) first, then
        'average1' after the first addition and so on. The problem is None for a
        window that fits, LEFT_OUT_PROBLEM for one left out, or one sentence saying
        why it does not fit.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    average0: end = first addition - its gap; start = end - its length, or the start
    of the recording when that is later; too short when end - start < the least
    length. averageN: end = addition N + 1 - its gap (the end of the recording - final
    gap for the last addition); start = end - its length; it does not fit when start <
    addition N.

    ---- Helpers ----
    _left_out_finder
    _own_minutes_reader
    """

    own = each_window or {}
    recording_start, recording_end = recording_span_min
    baseline_end = event_times_min[0] - _own_minutes_reader(own,
                                                            'average0',
                                                            'gap_min',
                                                            gap_minutes,
                                                            )
    baseline_start = max(baseline_end - _own_minutes_reader(own,
                                                            'average0',
                                                            'length_min',
                                                            window_minutes,
                                                            ),
                         recording_start,
                         )
    is_short = ((baseline_end - baseline_start) * 60.0
                < baseline_minimum_seconds - 1e-9
                )
    spans = [('average0',
              baseline_start,
              baseline_end,
              f'Less than {baseline_minimum_seconds:g} s of data before the first '
              'addition.'
              if is_short
              else None,
              ),
             ]
    for i, event_time in enumerate(event_times_min):
        name = f'average{i + 1}'
        if i + 1 < len(event_times_min):
            end = event_times_min[i + 1] - _own_minutes_reader(own,
                                                               name,
                                                               'gap_min',
                                                               gap_minutes,
                                                               )
            problem = f'Insufficient time between additions {i + 1} and {i + 2}.'
        else:
            # the last window ends a set time before the end of the file, whichever
            # window that is in this file
            end = recording_end - final_window_gap_minutes
            problem = 'Insufficient recording time after the final addition.'
        start = end - _own_minutes_reader(own, name, 'length_min', window_minutes)
        if _left_out_finder(own, name):
            problem = LEFT_OUT_PROBLEM
        elif start >= event_time:
            problem = None
        spans.append((name, start, end, problem))
    return spans


# ---- window_statistics_calculator ----------------------------------------------------
def window_statistics_calculator(df: pd.DataFrame,
                                 start_time: float,
                                 end_time: float,
                                 ) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Main function to calculate the mean and sample SD of every measurement column inside
    a time window.

    ---- Inputs ----
    df : pd.DataFrame
        Data frame with a time column and measurement columns (DATA_FORMAT.md).
    start_time : float
        Window start, in minutes.
    end_time : float
        Window end, in minutes.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        {column: {"mean", "sd"}}. Values are NaN when no finite point falls in the
        window (SD: fewer than two).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mean = sum(x) / n; SD = sqrt(sum((x - mean)^2) / (n - 1)) over the finite points
    with start_time <= t <= end_time.

    ---- Helpers ----
    measurement_column_finder
    time_getter
    value_getter
    """

    # ---- 1 Select the window ---------------------------------------------------------
    times = time_getter(df)
    in_window = np.isfinite(times) & (times >= start_time) & (times <= end_time)

    # ---- 2 Calculate the statistics --------------------------------------------------
    stats = {}
    for column in measurement_column_finder(df):
        values = value_getter(df, column)
        selected = values[in_window & np.isfinite(values)]
        stats[str(column)] = {'mean': float(np.mean(selected))
                              if selected.size
                              else np.nan,
                              'sd': float(np.std(selected, ddof=1))
                              if selected.size >= 2
                              else np.nan,
                              }
    return stats


# ---- window_value_setter -------------------------------------------------------------
def window_value_setter(values: Dict[str, float],
                        key: str,
                        value: float,
                        addition_count: Optional[int] = None,
                        ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to set one value of the settled or the quick windows (a length, how
    long before the next addition or after its own a window ends or starts, how long
    before the end of the file the last settled window ends, whether there are windows
    of a kind, whether a window is used, whether "Adjust region manually" is on, or
    the window picked), as dragged, typed, ticked or clicked in the window step.
    Switching "Adjust region manually" on picks window 1. While it is on, a dragged
    edge sets the value of its window only and makes it the window picked, and a typed
    value goes to the window picked (the time before the next addition of the last
    window is its time before the end of the file); with it off, or no window picked,
    the value is set for every window of its kind, which lose their own values of that
    field. A value that cannot be used leaves everything as it is.

    ---- Inputs ----
    values : Dict[str, float]
        The values of the file in the window step now; not changed.
    key : str
        The field set: one of WINDOW_KEYS or STEP_EXTRA_KEYS, a field with '@' and the
        window of the edge dragged ('gap_s@average1'), or the tick of a window
        ('average2:is_used').
    value : float
        Its new value: seconds, or for a switch or a tick anything but 0 for on, or
        the number of the window picked (0 the baseline).
    addition_count : Optional[int]
        How many additions the file has, to know its last window; None for not known.

    ---- Globals read ----
    OWN_SEPARATOR, STEP_OWN_FIELDS (module constants).

    ---- Outputs ----
    Dict[str, float]
        The new values. A length of 0 or less, a gap or a start after the addition
        below 0, or a tick of the baseline (always used), changes nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _edge_key_splitter
    _picked_window_namer
    _window_number_finder
    """

    # ---- 1 A tick or a switch --------------------------------------------------------
    field, window = _edge_key_splitter(key)
    name, separator, own_field = field.partition(OWN_SEPARATOR)
    if separator:
        if own_field != 'is_used' or name == 'average0':
            return dict(values)
        return dict(values, **{field: 1.0 if value else 0.0})
    if field == 'each_is_on':
        if not value:
            return dict(values, each_is_on=0.0)
        return dict(values, each_is_on=1.0, settled_picked=1.0)
    if field in ('is_on', 'quick_is_on'):
        return dict(values, **{field: 1.0 if value else 0.0})
    if field in PICKED_KEYS:
        return dict(values, **{field: float(round(value))})

    # ---- 2 A length, a gap or a start ------------------------------------------------
    if field in ('window_s', 'quick_s') and value <= 0:
        return dict(values)
    if field in ('gap_s', 'delay_s', 'final_gap_s') and value < 0:
        return dict(values)
    kind = next((own_kind
                 for own_kind, fields in STEP_OWN_FIELDS.items()
                 if field in fields
                 ),
                None,
                )
    if kind is None:
        return dict(values, **{field: float(value)})
    if values.get('each_is_on'):
        target = window or _picked_window_namer(values, kind)
        if (target is not None and
                window is None and
                field == 'gap_s' and
                addition_count is not None and
                _window_number_finder(target) == addition_count
                ):
            # the last window ends a time before the end of the file
            return dict(values, final_gap_s=float(value))
        if target is not None:
            return dict(values,
                        **{f'{target}{OWN_SEPARATOR}{field}': float(value),
                           f'{kind}_picked': float(_window_number_finder(target)),
                           },
                        )
    changed = {own_key: own_value
               for own_key, own_value in values.items()
               if not own_key.endswith(f'{OWN_SEPARATOR}{field}')
               }
    changed[field] = float(value)
    return changed


# ---- window_values_maker -------------------------------------------------------------
def window_values_maker(plan: dict,
                        is_settled: bool,
                        is_quick: bool,
                        ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to give the values the window step starts one file with, from its
    averaging windows: the inverse of window_plan_reader. "Adjust region manually"
    starts on, with window 1 picked, when a window has a length, a gap or a start of
    its own.

    ---- Inputs ----
    plan : dict
        The windows of the file, as window_plan_finder gives them.
    is_settled : bool
        Whether there are settled windows.
    is_quick : bool
        Whether there are quick windows.

    ---- Globals read ----
    NO_PICK, OWN_SEPARATOR, STEP_OWN_FIELDS (module constants).

    ---- Outputs ----
    Dict[str, float]
        WINDOW_KEYS and STEP_EXTRA_KEYS, in seconds rounded to 0.01 s, with the own
        values of each window ('average2:window_s') and its tick ('quick1:is_used').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    seconds = minutes x 60.

    ---- Helpers ----
    None.
    """

    values = {'window_s': round(plan['window_minutes'] * 60.0, 2),
              'gap_s': round(plan['gap_minutes'] * 60.0, 2),
              'is_on': 1.0 if is_settled else 0.0,
              'quick_s': round(plan['quick_minutes'] * 60.0, 2),
              'delay_s': round(plan['delay_minutes'] * 60.0, 2),
              'quick_is_on': 1.0 if is_quick else 0.0,
              'final_gap_s': round(plan['final_gap_minutes'] * 60.0, 2),
              'each_is_on': 0.0,
              'settled_picked': NO_PICK,
              'quick_picked': NO_PICK,
              }
    for name, own in (plan.get('each_window') or {}).items():
        kind = 'quick' if name.startswith('quick') else 'settled'
        step_fields = {own_field: field
                       for field, own_field in STEP_OWN_FIELDS[kind].items()
                       }
        for own_field, value in own.items():
            if own_field == 'is_used':
                values[f'{name}{OWN_SEPARATOR}is_used'] = 1.0 if value else 0.0
            elif own_field in step_fields:
                key = f'{name}{OWN_SEPARATOR}{step_fields[own_field]}'
                values[key] = round(float(value) * 60.0, 2)
                values['each_is_on'] = 1.0
                values['settled_picked'] = 1.0
    return values
