"""
Tests of the traces of a dataset figure over time, worked out by hand on made-up experiments: a trace in each value, traces lined up on their additions, an experiment with another number of additions, a line broken where a gap was shortened, and the mean, the SD and the SEM.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.delta_psi import DELTA_PSI_COLUMN
from utils_shared.schema import TIME_COLUMN
from utils_shared.trace_alignment import (additions_lister,
                                          line_breaker,
                                          trace_reader,
                                          traces_aligner,
                                          traces_averager,
                                          )


# ---- CONSTANTS -----------------------------------------------------------------------
B_HAEM = 'Cyt $b_H$'


# ---- MAKERS --------------------------------------------------------------------------


# ---- _clock_trace_maker --------------------------------------------------------------
def _clock_trace_maker(end_min: float, additions: List[float]) -> dict:
    """
    ---- Summary ----
    Helper function to make a trace whose value at each time is that time, from 0
    min, every half minute: read at a shared time, it gives back the experiment's
    own time there.

    ---- Inputs ----
    end_min : float
        The last time of the trace (min).
    additions : List[float]
        The times of the additions of the experiment (min).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The trace, as traces_aligner takes it.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(0.0, end_min + 0.25, 0.5)
    return {'times_min': times, 'values': times.copy(), 'additions_min': additions}


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make the slim copy of a made-up experiment at 0, 1, 2 and 3
    min: measured oxygen 50, 48, 46, 44 µM; an OCR of 10, 10, 6, 2 µM min⁻¹ with a
    baseline average of 10, so 100, 100, 60, 20 % of baseline, and 5, 5, 3, 1 per
    OD; bH as ΔD 0, 1, 2, 3 mOD, as absorbance 10, 11, 12, 13 mOD (per OD 5, 5.5, 6,
    6.5) and 0, 25, 50, 75 % oxidised; Δψ 130, 126, 122, 118 mV with a baseline
    average of 130; additions at 2 and 1 min, stored in that order.

    ---- Inputs ----
    None.

    ---- Globals read ----
    B_HAEM; DELTA_PSI_COLUMN, TIME_COLUMN (imported).

    ---- Outputs ----
    dict
        The slim copy (page_experiment, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(4.0)
    ocr = np.array([10.0, 10.0, 6.0, 2.0])
    percent = pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr * 10.0})
    percent.attrs['baseline_percent'] = {'start_time': 0.0,
                                         'end_time': 1.0,
                                         'baseline_mean': {'VoO2': 10.0},
                                         }
    return {'experiment_name': 'e1',
            'metadata': {'events': [{'time': 2.0, 'label': 'second'},
                                    {'time': 1.0, 'label': 'first'},
                                    ],
                         },
            'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 50.0 - 2 * times}),
            'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr}),
            'VoO2_OD': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr / 2.0}),
            'VoO2_baseline': percent,
            'haem_delta_abs': pd.DataFrame({TIME_COLUMN: times,
                                            'spectrum_index': times,
                                            B_HAEM: times,
                                            },
                                           ),
            'haem_abs': pd.DataFrame({TIME_COLUMN: times, B_HAEM: 10.0 + times}),
            'haem_abs_OD': pd.DataFrame({TIME_COLUMN: times,
                                         B_HAEM: (10.0 + times) / 2.0,
                                         },
                                        ),
            'haem_percent': pd.DataFrame({TIME_COLUMN: times, B_HAEM: 25.0 * times}),
            'delta_psi': pd.DataFrame({TIME_COLUMN: times,
                                       DELTA_PSI_COLUMN: 130.0 - 4.0 * times,
                                       },
                                      ),
            'averages': {'windows': {'average0': {'delta_psi': {'mean': 130.0}}}},
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_trace_in_each_value ------------------------------------------------------
def test_a_trace_in_each_value() -> None:
    """
    ---- Summary ----
    Main function to check one trace of an experiment in each value it can be shown
    in, with the title of its y axis: the oxygen; the OCR as measured, as % of
    baseline, as its change from baseline and per OD; a haem as ΔD, absorbance and
    % oxidised, per OD where the run is and the file has it; Δψ in mV and as its
    change from baseline; nothing for what the file does not have; and its
    additions in time order.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Change from baseline, y = x - b: the OCR with b = 10 is 10 - 10 = 0, 0, 6 - 10 =
    -4 and 2 - 10 = -8 µM min⁻¹ (the example of MATHS.md section 10.1); Δψ with b =
    130 is 0, -4, -8 and -12 mV.

    ---- Helpers ----
    _experiment_maker
    """

    # ---- 1 The oxygen and the OCR ----------------------------------------------------
    experiment = _experiment_maker()
    read = trace_reader(experiment, 'oxygen', '')
    assert list(read['values']) == [50.0, 48.0, 46.0, 44.0]
    assert list(read['times_min']) == [0.0, 1.0, 2.0, 3.0]
    assert read['label'] == 'O$_2$ (µM)'
    wanted = {'raw': ([10.0, 10.0, 6.0, 2.0], 'OCR (µM min$^{-1}$)'),
              'baseline': ([100.0, 100.0, 60.0, 20.0], 'OCR (% of baseline)'),
              'change': ([0.0, 0.0, -4.0, -8.0], 'Change in OCR (µM min$^{-1}$)'),
              'od': ([5.0, 5.0, 3.0, 1.0], 'OCR (µM min$^{-1}$ OD$^{-1}$)'),
              }
    for value, (values, label) in wanted.items():
        read = trace_reader(experiment, 'vo2', value)
        assert (list(read['values']), read['label']) == (values, label)

    # ---- 2 A haem --------------------------------------------------------------------
    read = trace_reader(experiment, 'haem_cytbh', 'delta')
    assert list(read['values']) == [0.0, 1.0, 2.0, 3.0]
    assert read['label'] == 'Cyt $b_H$ ΔD (mOD)'
    read = trace_reader(experiment, 'haem_cytbh', 'abs', is_per_od=True)
    assert list(read['values']) == [5.0, 5.5, 6.0, 6.5]
    assert read['label'] == 'Cyt $b_H$ absorbance (mOD OD$^{-1}$)'
    # ΔD per OD is not in this file: it is shown as it is
    read = trace_reader(experiment, 'haem_cytbh', 'delta', is_per_od=True)
    assert list(read['values']) == [0.0, 1.0, 2.0, 3.0]
    read = trace_reader(experiment, 'haem_cytbh', 'percent', is_per_od=True)
    assert list(read['values']) == [0.0, 25.0, 50.0, 75.0]
    assert read['label'] == 'Cyt $b_H$ oxidised (%)'

    # ---- 3 Δψ ------------------------------------------------------------------------
    read = trace_reader(experiment, 'delta_psi', 'raw')
    assert (list(read['values']), read['label']) == ([130.0, 126.0, 122.0, 118.0],
                                                     'Δψ (mV)',
                                                     )
    read = trace_reader(experiment, 'delta_psi', 'change')
    assert (list(read['values']), read['label']) == ([0.0, -4.0, -8.0, -12.0],
                                                     'Change in Δψ (mV)',
                                                     )

    # ---- 4 What the file does not have -----------------------------------------------
    assert trace_reader(experiment, 'haem_cytcc', 'delta') is None
    assert trace_reader(experiment, 'vo2', 'no such value') is None
    assert trace_reader(experiment, 'no such trace', '') is None
    del experiment['VoO2_baseline'], experiment['averages'], experiment['haem_percent']
    assert trace_reader(experiment, 'vo2', 'baseline') is None
    assert trace_reader(experiment, 'vo2', 'change') is None
    assert trace_reader(experiment, 'delta_psi', 'change') is None
    assert trace_reader(experiment, 'haem_cytbh', 'percent') is None
    assert trace_reader(experiment, 'vo2', 'raw') is not None

    # ---- 5 Its additions -------------------------------------------------------------
    assert additions_lister(experiment) == [1.0, 2.0]
    assert additions_lister({}) == []


# ---- test_traces_are_lined_up_on_their_additions -------------------------------------
def test_traces_are_lined_up_on_their_additions() -> None:
    """
    ---- Summary ----
    Main function to check two experiments lined up on their additions, worked out
    by hand (the example of MATHS.md section 10.2): where the additions and the
    break sit on the shared axis, how far it goes, the own time of each experiment
    at shared times in both halves of the gap, and the same with time 0 at the
    second addition.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A (0 to 20 min) has additions at 10 and 16 min, B (0 to 25 min) at 12 and 17
    min. The shortest gap is 5, so the additions are at 0 and 5. A has 10 min
    before its first addition and B 12: the axis starts at -10. A has 4 min after
    its last and B 8: it ends at 5 + 4 = 9, so it has 19 x 60 + 1 = 1141 times. 1
    min after addition 1: A 10 + 1 = 11, B 12 + 1 = 13. 30 s before addition 2, at
    5 - 0.5 = 4.5: A 16 - 0.5 = 15.5, B 16.5. The halves meet at 2.5: there A is 16
    - 2.5 = 13.5 and B 14.5; one second earlier A is still counted from its first
    addition, 10 + 2.5 - 1/60. At -10: A 0, B 2. At 9: A 20, B 21.

    ---- Helpers ----
    _clock_trace_maker
    """

    # ---- 1 Time 0 at the first addition ----------------------------------------------
    traces = [_clock_trace_maker(20.0, [10.0, 16.0]),
              _clock_trace_maker(25.0, [12.0, 17.0]),
              ]
    found = traces_aligner(traces, 0)
    times, values = found['times_min'], found['values']
    assert found['additions_min'] == [0.0, 5.0]
    assert found['breaks_min'] == [2.5]
    assert (found['kept'], found['left_out']) == ([0, 1], [])
    assert (times[0], times[-1], len(times)) == (-10.0, 9.0, 1141)
    assert values.shape == (2, 1141)
    wanted = {1.0: (11.0, 13.0),
              4.5: (15.5, 16.5),
              2.5: (13.5, 14.5),
              2.5 - 1 / 60: (12.5 - 1 / 60, 14.5 - 1 / 60),
              -10.0: (0.0, 2.0),
              9.0: (20.0, 21.0),
              0.0: (10.0, 12.0),
              5.0: (16.0, 17.0),
              }
    for moment, own in wanted.items():
        place = int(np.argmin(np.abs(times - moment)))
        assert times[place] == pytest.approx(moment)
        assert tuple(values[:, place]) == pytest.approx(own)
    assert np.isfinite(values).all()

    # ---- 2 Time 0 at the second addition, or at one they do not have -----------------
    for zero in (1, 7):
        found = traces_aligner(traces, zero)
        assert found['additions_min'] == [-5.0, 0.0]
        assert found['breaks_min'] == [-2.5]
        assert (found['times_min'][0], found['times_min'][-1]) == (-15.0, 4.0)
        place = int(np.argmin(np.abs(found['times_min'] + 0.5)))
        assert tuple(found['values'][:, place]) == pytest.approx((15.5, 16.5))

    # ---- 3 The same gap in both: no break --------------------------------------------
    same = [_clock_trace_maker(20.0, [10.0, 15.0]),
            _clock_trace_maker(25.0, [12.0, 17.0]),
            ]
    assert traces_aligner(same, 0)['breaks_min'] == []


# ---- test_another_number_of_additions_is_left_out ------------------------------------
def test_another_number_of_additions_is_left_out() -> None:
    """
    ---- Summary ----
    Main function to check which experiments are lined up: one with another number
    of additions than most is left out; with a tie, the number met first is kept;
    lined up on the start of the recordings, or without any addition, every
    experiment is kept on its own clock, as far as they all go; an empty stretch of
    a trace stays empty; and no experiment gives no times.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    On their own clocks, traces of 0 to 20 and 0 to 25 min share 0 to 20 min: 20 x
    60 + 1 = 1201 times, each experiment at its own time. A trace of 1, empty, 3, 4
    at 0, 1, 2, 3 min read at 2.5 min is 3 + (4 - 3) x 0.5 = 3.5, and empty at 0.5
    and 1.5 min, beside the empty point.

    ---- Helpers ----
    _clock_trace_maker
    """

    # ---- 1 Another number of additions -----------------------------------------------
    two, other, one = (_clock_trace_maker(20.0, [10.0, 16.0]),
                       _clock_trace_maker(25.0, [12.0, 17.0]),
                       _clock_trace_maker(25.0, [12.0]),
                       )
    found = traces_aligner([two, one, other], 0)
    assert (found['kept'], found['left_out']) == ([0, 2], [1])
    assert found['values'].shape[0] == 2 and found['additions_min'] == [0.0, 5.0]
    found = traces_aligner([one, two], 0)
    assert (found['kept'], found['left_out']) == ([0], [1])
    assert found['additions_min'] == [0.0] and found['breaks_min'] == []
    assert (found['times_min'][0], found['times_min'][-1]) == (-12.0, 13.0)

    # ---- 2 On their own clocks -------------------------------------------------------
    for traces, zero in (([two, one, other], None),
                         ([_clock_trace_maker(20.0, []), _clock_trace_maker(25.0, [])],
                          0,
                          ),
                         ):
        found = traces_aligner(traces, zero)
        assert found['left_out'] == [] and found['additions_min'] == []
        assert (found['times_min'][0], found['times_min'][-1]) == (0.0, 20.0)
        assert len(found['times_min']) == 1201
        for row in found['values']:
            assert row == pytest.approx(found['times_min'])

    # ---- 3 An empty stretch, and no experiment ---------------------------------------
    holed = {'times_min': np.arange(4.0),
             'values': np.array([1.0, np.nan, 3.0, 4.0]),
             'additions_min': [],
             }
    found = traces_aligner([holed], None)
    by_time = dict(
        zip(np.round(found['times_min'] * 60).astype(int), found['values'][0]),
        )
    assert by_time[150] == pytest.approx(3.5)
    assert np.isnan(by_time[30]) and np.isnan(by_time[90])
    found = traces_aligner([], 0)
    assert len(found['times_min']) == 0 and found['values'].shape == (0, 0)


# ---- test_the_mean_and_the_band ------------------------------------------------------
def test_the_mean_and_the_band() -> None:
    """
    ---- Summary ----
    Main function to check the mean, the SD and the SEM of lined-up traces at each
    time, worked out by hand (the example of MATHS.md section 10.3): of three
    experiments, of the two that have a value, of one alone and of none.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    4, 6 and 8: mean 18 / 3 = 6; SD = sqrt(((-2)² + 0² + 2²) / 2) = 2; SEM = 2 /
    sqrt(3) = 1.1547. 1 and 5 (the third empty): mean 3; SD = sqrt((4 + 4) / 1) =
    2.8284; SEM = 2.8284 / sqrt(2) = 2. 7 alone: mean 7, no SD and no SEM.

    ---- Helpers ----
    None.
    """

    values = np.array([[4.0, 1.0, np.nan, np.nan],
                       [6.0, 5.0, np.nan, np.nan],
                       [8.0, np.nan, 7.0, np.nan],
                       ],
                      )
    found = traces_averager(values)
    assert list(found['n']) == [3, 2, 1, 0]
    assert found['mean'][:3] == pytest.approx([6.0, 3.0, 7.0])
    assert found['sd'][:2] == pytest.approx([2.0, 2.8284271])
    assert found['sem'][:2] == pytest.approx([1.1547005, 2.0])
    assert np.isnan(found['mean'][3])
    assert np.isnan(found['sd'][2:]).all() and np.isnan(found['sem'][2:]).all()


# ---- test_a_line_is_broken_where_a_gap_was_shortened ---------------------------------
def test_a_line_is_broken_where_a_gap_was_shortened() -> None:
    """
    ---- Summary ----
    Main function to check that a line gets an empty point at each break, before
    the time of the break itself, so it is not drawn across the spare middle that
    was left out; and that a line without breaks stays as it is.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times, values = np.arange(4.0), np.array([10.0, 11.0, 12.0, 13.0])
    broken, drawn = line_breaker(times, values, [2.0])
    assert list(broken) == [0.0, 1.0, 2.0, 2.0, 3.0]
    assert list(drawn[:2]) == [10.0, 11.0] and list(drawn[3:]) == [12.0, 13.0]
    assert np.isnan(drawn[2])
    broken, drawn = line_breaker(times, values, [])
    assert list(broken) == list(times) and list(drawn) == list(values)
