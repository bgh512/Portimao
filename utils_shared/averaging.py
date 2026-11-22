"""
Event-window averaging of OCR and haem data for one experiment.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
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


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


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
                                   ) -> dict:
    """
    ---- Summary ----
    Main function to calculate event-window statistics for VoO2 and haem data and store
    them in the experiment: the baseline, the settled windows (ending before the next
    addition) and, when asked for, the quick windows (starting after each addition).

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

    ---- Globals read ----
    schema.VO2_KEYS, HAEM_KEYS and DELTA_HAEM_SOURCES.

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
    average0 ends gap_minutes before the first event and starts window_minutes before
    its end, or at the start of the recording when that is later; it is skipped when
    the points inside it span less than baseline_minimum_seconds. averageN ends
    gap_minutes before event N+1 (final_window_gap_minutes before the end of the
    recording for the last event); each window starts window_minutes before its end
    and is skipped when that is before its own event. quickN starts delay_minutes
    after event N and ends quick_minutes later; it is skipped when that is after event
    N+1 (the end of the recording for the last event). change = mean /
    mean(average0) x 100 (NaN for delta abs sources); delta = mean - mean(average0),
    for the settled and the quick windows alike.

    ---- Helpers ----
    _baseline_change_adder
    quick_span_lister
    source_resolver
    time_getter
    window_span_lister
    window_statistics_calculator
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    name = experiment['experiment_name']
    if window_minutes <= 0:
        raise ValueError('The averaging window must be longer than 0 min. Correct it '
                         'where the program asks for it.',
                         )
    if gap_minutes < 0 or final_window_gap_minutes < 0:
        raise ValueError('The gap before an averaging window cannot be negative. '
                         'Correct it where the program asks for it.',
                         )
    if baseline_minimum_seconds < 0:
        raise ValueError('The least length of the baseline cannot be negative. '
                         'Correct it in config.py.',
                         )
    if quick_minutes is not None and quick_minutes <= 0:
        raise ValueError('The quick averaging window must be longer than 0 min. '
                         'Correct it where the program asks for it.',
                         )
    if delay_minutes < 0:
        raise ValueError('A quick averaging window cannot start before its addition. '
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
    spans = window_span_lister([float(event['time']) for event in events],
                               (recording_start, recording_end),
                               window_minutes,
                               gap_minutes,
                               final_window_gap_minutes,
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
                                                     )
                       ]
    for kind, (window_name, start, end, problem) in kind_spans:
        if problem is not None:
            skipped[window_name] = {'start_time': start,
                                    'end_time': end,
                                    'reason': problem,
                                    'kind': kind,
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
                                }

    # ---- 5 Store the results ---------------------------------------------------------
    baseline = windows.get('average0', {'vo2': {}, 'haem': {}})  # none: all NaN
    haem_is_absolute = haem_source not in DELTA_HAEM_SOURCES
    for window in windows.values():
        _baseline_change_adder(window['vo2'], baseline['vo2'])
        _baseline_change_adder(window['haem'],
                               baseline['haem'],
                               percent_of_baseline=haem_is_absolute,
                               )
    final_gap = final_window_gap_minutes
    experiment['averages'] = {'settings': {'window_minutes': window_minutes,
                                           'gap_minutes': gap_minutes,
                                           'final_window_gap_minutes': final_gap,
                                           'vo2_source': vo2_source,
                                           'vo2_key': vo2_key,
                                           'haem_source': haem_source,
                                           'haem_key': haem_key,
                                           'baseline_minimum_seconds':
                                               baseline_minimum_seconds,
                                           'quick_minutes': quick_minutes,
                                           'delay_minutes': delay_minutes,
                                           'is_settled': is_settled,
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
                     ) -> List[Tuple[str, float, float, Optional[str]]]:
    """
    ---- Summary ----
    Main function to give the windows a figure that uses one kind of window averages
    over: the baseline, then the window of that kind of each addition, all under the
    names of the settled windows, so the figure reads either kind in the same way.

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
        raise ValueError(f'The kind of averaging window {kind!r} is not known.')
    spans = window_span_lister(event_times_min,
                               recording_span_min,
                               window_minutes,
                               gap_minutes,
                               final_window_gap_minutes,
                               )
    if kind == 'settled':
        return spans
    quick = quick_span_lister(event_times_min,
                              recording_span_min,
                              quick_minutes,
                              delay_minutes,
                              )
    return spans[:1] + [(f'average{index}', start, end, problem)
                        for index, (_, start, end, problem) in enumerate(quick, start=1)
                        ]


# ---- quick_span_lister ---------------------------------------------------------------
def quick_span_lister(event_times_min: List[float],
                      recording_span_min: Tuple[float, float],
                      quick_minutes: float,
                      delay_minutes: float,
                      ) -> List[Tuple[str, float, float, Optional[str]]]:
    """
    ---- Summary ----
    Main function to give where the quick windows of one file fall, and which do not
    fit: one window starting a set time after each addition. The averaging and the plot
    of the window step both use it.

    ---- Inputs ----
    event_times_min : List[float]
        Times of the additions (min), in order.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data (min).
    quick_minutes : float
        Length of each quick window, in minutes.
    delay_minutes : float
        How long after its addition each quick window starts, in minutes.

    ---- Globals read ----
    FIT_TOLERANCE_MIN (module constant).

    ---- Outputs ----
    List[Tuple[str, float, float, Optional[str]]]
        [(name, start, end, problem)] in minutes, 'quick1' after the first addition and
        so on. The problem is None for a window that fits, or one sentence saying why
        it does not.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    quickN: start = addition N + delay; end = start + length; it does not fit when end
    > addition N + 1 (the end of the recording for the last addition).

    ---- Helpers ----
    None.
    """

    _, recording_end = recording_span_min
    spans = []
    for i, event_time in enumerate(event_times_min):
        if i + 1 < len(event_times_min):
            limit = event_times_min[i + 1]
            problem = f'Insufficient time between additions {i + 1} and {i + 2}.'
        else:
            limit = recording_end
            problem = 'Insufficient recording time after the final addition.'
        start = event_time + delay_minutes
        end = start + quick_minutes
        spans.append((f'quick{i + 1}',
                      start,
                      end,
                      problem if end > limit + FIT_TOLERANCE_MIN else None,
                      ),
                     )
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
        raise ValueError(f'The kind of averaging window {kind!r} is not known.')
    picked = dict(averages)
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
    edges of every averaging window, and the windows as parts to shade, those that do
    not fit apart. The first edge of each kind carries its words. The baseline is
    there when either kind of window is switched on.

    ---- Inputs ----
    values : Dict[str, float]
        The settled and the quick windows of the file (WINDOW_KEYS).
    event_times_min : List[float]
        Times of the file's additions on the time axis of the plot (min), in order,
        not those marked ignore.
    recording_span_min : Tuple[float, float]
        (first, last) time of the data on that axis (min).
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, in minutes.
    baseline_minimum_seconds : float
        Least length of the baseline window, in seconds.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
        ([(field, time in min, words, kind)], [(start, end, kind)]). The baseline and
        the settled windows first: the start of each is an edge of the field
        'window_s' (kind 'average'), the end of each but the last settled window an
        edge of 'gap_s' (kind 'average_end'; the last window ends a fixed time before
        the end of the recording). Then the quick windows: the start of each is an
        edge of 'delay_s' (kind 'quick'), its end an edge of 'quick_s' (kind
        'quick_end'). A part has the kind 'average', 'quick', or 'average_unfit' for a
        window that does not fit. Both lists are empty when both kinds are switched off
        or the file has no additions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    quick_span_lister
    window_span_lister
    """

    is_settled, is_quick = bool(values['is_on']), bool(values['quick_is_on'])
    if not (is_settled or is_quick) or not event_times_min:
        return [], []
    spans = window_span_lister(event_times_min,
                               recording_span_min,
                               values['window_s'] / 60.0,
                               values['gap_s'] / 60.0,
                               final_window_gap_minutes,
                               baseline_minimum_seconds,
                               )
    if not is_settled:
        spans = spans[:1]  # the baseline only
    edges, parts = [], []
    for index, (_, start, end, problem) in enumerate(spans):
        words = f"window {round(values['window_s'], 2):g} s" if index == 0 else ''
        edges.append(('window_s', start, words, 'average'))
        if index < len(spans) - 1 or not is_settled:
            words = (f"ends {round(values['gap_s'], 2):g} s before the addition"
                     if index == 0
                     else ''
                     )
            edges.append(('gap_s', end, words, 'average_end'))
        if end > start:
            parts.append((start,
                          end,
                          'average' if problem is None else 'average_unfit',
                          ),
                         )
    if not is_quick:
        return edges, parts
    quick = quick_span_lister(event_times_min,
                              recording_span_min,
                              values['quick_s'] / 60.0,
                              values['delay_s'] / 60.0,
                              )
    for index, (_, start, end, problem) in enumerate(quick):
        words = (f"starts {round(values['delay_s'], 2):g} s after the addition"
                 if index == 0
                 else ''
                 )
        edges.append(('delay_s', start, words, 'quick'))
        words = f"quick window {round(values['quick_s'], 2):g} s" if index == 0 else ''
        edges.append(('quick_s', end, words, 'quick_end'))
        parts.append((start, end, 'quick' if problem is None else 'average_unfit'))
    return edges, parts


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
    its length (an end edge). The edge held is the one of its kind nearest the mouse,
    which stays the same edge while it follows the mouse.

    ---- Inputs ----
    values : Dict[str, float]
        The settled and the quick windows of the file now (WINDOW_KEYS).
    key : str
        'window_s' for the start and 'gap_s' for the end of a settled window or the
        baseline, 'delay_s' for the start and 'quick_s' for the end of a quick window.
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
    quick_s = round((time - start of the quick window held) x 60 / step) x step.

    ---- Helpers ----
    quick_span_lister
    window_span_lister
    """

    if not event_times_min:
        return values[key]
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


# ---- window_span_lister --------------------------------------------------------------
def window_span_lister(event_times_min: List[float],
                       recording_span_min: Tuple[float, float],
                       window_minutes: float,
                       gap_minutes: float,
                       final_window_gap_minutes: float,
                       baseline_minimum_seconds: float = 0.0,
                       ) -> List[Tuple[str, float, float, Optional[str]]]:
    """
    ---- Summary ----
    Main function to give where the averaging windows of one file fall, and which do
    not fit: the baseline window before the first addition, then one window after each
    addition. The averaging and the plot of the window step both use it.

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

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, float, float, Optional[str]]]
        [(name, start, end, problem)] in minutes, 'average0' (the baseline) first, then
        'average1' after the first addition and so on. The problem is None for a
        window that fits, or one sentence saying why it does not.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    average0: end = first addition - gap; start = end - window, or the start of the
    recording when that is later; too short when end - start < the least length.
    averageN: end = addition N + 1 - gap (the end of the recording - final gap for the
    last addition); start = end - window; it does not fit when start < addition N.

    ---- Helpers ----
    None.
    """

    recording_start, recording_end = recording_span_min
    baseline_end = event_times_min[0] - gap_minutes
    baseline_start = max(baseline_end - window_minutes, recording_start)
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
        if i + 1 < len(event_times_min):
            end = event_times_min[i + 1] - gap_minutes
            problem = f'Insufficient time between additions {i + 1} and {i + 2}.'
        else:
            end = recording_end - final_window_gap_minutes
            problem = 'Insufficient recording time after the final addition.'
        start = end - window_minutes
        spans.append((f'average{i + 1}',
                      start,
                      end,
                      problem if start < event_time else None,
                      ),
                     )
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
                        ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to set one value of the settled or the quick windows (a length, how
    long before the next addition or after its own a window ends or starts, or
    whether there are windows of that kind), as dragged, typed or ticked in the window
    step. A value that cannot be used leaves everything as it is.

    ---- Inputs ----
    values : Dict[str, float]
        The settled and the quick windows now (WINDOW_KEYS); not changed.
    key : str
        The field set: one of WINDOW_KEYS.
    value : float
        Its new value: seconds, or for 'is_on' and 'quick_is_on' anything but 0 for
        windows.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, float]
        The new values. A length of 0 or less, or a gap or a start after the addition
        below 0, changes nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if key in ('is_on', 'quick_is_on'):
        return dict(values, **{key: 1.0 if value else 0.0})
    if key in ('window_s', 'quick_s') and value <= 0:
        return dict(values)
    if key in ('gap_s', 'delay_s') and value < 0:
        return dict(values)
    return dict(values, **{key: float(value)})
