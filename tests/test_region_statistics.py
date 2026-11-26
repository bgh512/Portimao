"""
Tests of the numbers of the plots per region of a dataset figure, worked out by hand on made-up experiments (the numbers of MATHS.md section 11): the value of an experiment in a region, the mean, SD and SEM of a set, Student's, Welch's and the paired t-test, the Holm correction, the marks and the legend sentence.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import math

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest
from scipy import stats as scipy_stats

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.delta_psi import DELTA_PSI_COLUMN
from utils_shared.region_statistics import (legend_sentence_writer,
                                            p_value_marker,
                                            p_values_corrector,
                                            paired_statistics_builder,
                                            pairs_tester,
                                            plot_statistics_builder,
                                            region_value_reader,
                                            set_statistics_calculator,
                                            set_values_lister,
                                            sets_tester,
                                            )
from utils_shared.schema import TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
B_HAEM = 'Cyt $b_H$'
# The two sets of the examples of MATHS.md section 11, and a third beside them
CONTROL = [10.0, 11.0, 12.0]
KNOCKDOWN = [20.0, 25.0, 30.0]
RESCUE = [11.0, 12.0, 13.0]
# How far a p value worked out by hand may be from the program's
P_TOLERANCE = 2e-5


# ---- MAKERS --------------------------------------------------------------------------


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(scale: float = 1.0) -> dict:
    """
    ---- Summary ----
    Helper function to make the slim copy of a made-up experiment at 0 to 5 min,
    with the baseline from 0 to 1 min, the quick region of its one addition from 2
    to 3 min and the settled one from 4 to 5 min: an OCR of 10, 10, 4, 4, 6, 6 µM
    min⁻¹ (times the scale; half of it per OD); bH 80, 80, 60, 60, 50, 50 %
    oxidised; Δψ 130, 130, none, 120, 118, 118 mV.

    ---- Inputs ----
    scale : float
        What the OCR is multiplied by.

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

    times = np.arange(6.0)
    ocr = np.array([10.0, 10.0, 4.0, 4.0, 6.0, 6.0]) * scale
    percent = pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr / (10.0 * scale) * 100.0})
    percent.attrs['baseline_percent'] = {'start_time': 0.0,
                                         'end_time': 1.0,
                                         'baseline_mean': {'VoO2': 10.0 * scale},
                                         }
    windows = {'average0': {'start_time': 0.0,
                            'end_time': 1.0,
                            'kind': 'baseline',
                            'delta_psi': {'mean': 130.0},
                            },
               'quick1': {'start_time': 2.0, 'end_time': 3.0, 'kind': 'quick'},
               'average1': {'start_time': 4.0, 'end_time': 5.0, 'kind': 'settled'},
               }
    return {'experiment_name': 'made up',
            'metadata': {'events': [{'time': 1.5, 'label': 'KCN'}]},
            'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr}),
            'VoO2_OD': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr / 2.0}),
            'VoO2_baseline': percent,
            'haem_percent': pd.DataFrame({TIME_COLUMN: times,
                                          B_HAEM: [80.0, 80.0, 60.0, 60.0, 50.0, 50.0],
                                          },
                                         ),
            'delta_psi': pd.DataFrame({TIME_COLUMN: times,
                                       DELTA_PSI_COLUMN: [130.0,
                                                          130.0,
                                                          np.nan,
                                                          120.0,
                                                          118.0,
                                                          118.0,
                                                          ],
                                       },
                                      ),
            'averages': {'windows': windows},
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_set_of_one_is_drawn_but_not_tested ---------------------------------------
def test_a_set_of_one_is_drawn_but_not_tested() -> None:
    """
    ---- Summary ----
    Main function to check a set with one experiment: it keeps its value and its
    mean, has no SD and no SEM, is in no test, and the legend sentence says so.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CONTROL, KNOCKDOWN.

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

    single = set_statistics_calculator([15.0, None])
    assert (single['values'], single['n'], single['mean']) == ([15.0], 1, 15.0)
    assert math.isnan(single['sd']) and math.isnan(single['sem'])
    assert sets_tester(CONTROL, [15.0]) is None
    assert sets_tester([15.0], CONTROL, 'welch') is None

    sets = [{'name': 'control', 'values': CONTROL},
            {'name': 'knockdown', 'values': KNOCKDOWN},
            {'name': 'rescue', 'values': [15.0]},
            ]
    statistics = plot_statistics_builder([{'label': 'Baseline', 'sets': sets}])
    assert [(one['first'], one['second']) for one in statistics['tests']] == [
        ('control', 'knockdown'),
        ]
    assert legend_sentence_writer(statistics) == (
        'Each dot is one experiment, and the bars are the mean ± SEM of each set '
        '(control n = 3, knockdown n = 3, rescue n = 1). rescue has one experiment '
        'in a region, so it has no bar and was not tested. The sets were compared '
        "with Student's t-test (two-tailed, unpaired): * p < 0.05, ** p < 0.01, "
        '*** p < 0.001; a comparison without a mark gave p ≥ 0.05.'
        )


# ---- test_each_pair_of_sets_is_tested ------------------------------------------------
def test_each_pair_of_sets_is_tested() -> None:
    """
    ---- Summary ----
    Main function to check a plot of three sets in two columns: each pair of sets is
    tested in each column, and the Holm correction counts every test of the plot.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CONTROL, KNOCKDOWN, P_TOLERANCE, RESCUE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    First column: control and knockdown p = 0.008934, control and rescue 0.287864,
    knockdown and rescue 0.011548. Holm over those three: 0.008934 x 3 = 0.026802;
    0.011548 x 2 = 0.023096, raised to 0.026802; 0.287864 x 1. With a second column
    of control against 10, 12, 11 (the same mean, so t = 0 and p = 1) beside control
    against knockdown: 0.008934 x 2 = 0.017868, and 1 x 1 = 1.

    ---- Helpers ----
    None.
    """

    # ---- 1 One column, three sets: three tests ---------------------------------------
    sets = [{'name': 'control', 'values': CONTROL},
            {'name': 'knockdown', 'values': KNOCKDOWN},
            {'name': 'rescue', 'values': RESCUE},
            ]
    statistics = plot_statistics_builder([{'label': 'Baseline', 'sets': sets}])
    tests = statistics['tests']
    assert [(one['column'], one['first'], one['second']) for one in tests] == [
        (0, 'control', 'knockdown'),
        (0, 'control', 'rescue'),
        (0, 'knockdown', 'rescue'),
        ]
    assert [one['p'] for one in tests] == pytest.approx([0.008934, 0.287864, 0.011548],
                                                        abs=P_TOLERANCE,
                                                        )
    assert [one['p_corrected'] for one in tests] == pytest.approx(
        [0.026802, 0.287864, 0.026802],
        abs=3 * P_TOLERANCE,
        )
    assert statistics['is_paired'] is False
    assert [one['mean'] for one in statistics['columns'][0]['sets']] == [11.0,
                                                                         25.0,
                                                                         12.0,
                                                                         ]

    # ---- 2 Two columns: the correction counts the tests of both ----------------------
    after = [{'name': 'control', 'values': CONTROL},
             {'name': 'knockdown', 'values': [10.0, 12.0, 11.0]},
             ]
    statistics = plot_statistics_builder([{'label': 'Baseline', 'sets': sets[:2]},
                                          {'label': 'After KCN', 'sets': after},
                                          ],
                                         )
    tests = statistics['tests']
    assert [one['column'] for one in tests] == [0, 1]
    assert tests[1]['t'] == pytest.approx(0.0, abs=1e-12)
    assert [one['p_corrected'] for one in tests] == pytest.approx([0.017868, 1.0],
                                                                  abs=2 * P_TOLERANCE,
                                                                  )
    assert legend_sentence_writer(statistics, error='sd', marks='p').endswith(
        'the bars are the mean ± SD of each set (control n = 3, knockdown n = 3). '
        "The sets were compared with Student's t-test (two-tailed, unpaired), with "
        'the Holm correction across the 2 tests of the plot: the p values under '
        '0.05 are shown; a comparison without a mark gave p ≥ 0.05.',
        )
    assert 'compared' not in legend_sentence_writer(statistics, marks='none')
    assert "Welch's t-test (two-tailed, unpaired, unequal variances)" in (
        legend_sentence_writer(statistics, test='welch')
        )


# ---- test_the_holm_correction --------------------------------------------------------
def test_the_holm_correction() -> None:
    """
    ---- Summary ----
    Main function to check the Holm correction on the examples of MATHS.md section
    11.5: the smallest p value times the number of tests, the next times one fewer,
    never under the one before, never over 1, and a comparison that was not tested
    not counted.

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
    0.01, 0.04, 0.03: sorted 0.01, 0.03, 0.04; 0.01 x 3 = 0.03, 0.03 x 2 = 0.06,
    0.04 x 1 = 0.04 raised to 0.06. 0.5, 0.6: 0.5 x 2 = 1, 0.6 x 1 raised to 1.

    ---- Helpers ----
    None.
    """

    assert p_values_corrector([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert p_values_corrector([0.5, 0.6]) == pytest.approx([1.0, 1.0])
    assert p_values_corrector([0.01, None, 0.04]) == [pytest.approx(0.02),
                                                      None,
                                                      pytest.approx(0.04),
                                                      ]
    assert p_values_corrector([0.03]) == pytest.approx([0.03])
    assert p_values_corrector([]) == []


# ---- test_the_marks ------------------------------------------------------------------
def test_the_marks() -> None:
    """
    ---- Summary ----
    Main function to check the mark over a comparison: stars or the p value where
    the two differ, and nothing, never "ns", where they do not or were not tested.

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

    assert [p_value_marker(p_value) for p_value in (0.0005, 0.005, 0.03)] == ['***',
                                                                              '**',
                                                                              '*',
                                                                              ]
    assert [p_value_marker(p_value) for p_value in (0.05, 0.2, 1.0, None)] == [''] * 4
    assert p_value_marker(0.0179, 'p') == 'p = 0.018'
    assert p_value_marker(0.0005, 'p') == 'p < 0.001'
    assert p_value_marker(0.2, 'p') == ''
    assert p_value_marker(0.0005, 'none') == ''
    with pytest.raises(ValueError):
        p_value_marker(0.01, 'ns')


# ---- test_the_mean_sd_and_sem_of_a_set -----------------------------------------------
def test_the_mean_sd_and_sem_of_a_set() -> None:
    """
    ---- Summary ----
    Main function to check the mean, the SD and the SEM of the two sets of MATHS.md
    section 11.2, an experiment without a value not counted.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CONTROL, KNOCKDOWN.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    10, 11, 12: mean 11, SD sqrt((1 + 0 + 1) / 2) = 1, SEM 1 / sqrt(3) = 0.577.
    20, 25, 30: mean 25, SD sqrt((25 + 0 + 25) / 2) = 5, SEM 5 / sqrt(3) = 2.887.

    ---- Helpers ----
    None.
    """

    control = set_statistics_calculator(CONTROL + [None, float('nan')])
    assert control['values'] == CONTROL
    assert (control['n'], control['mean']) == (3, 11.0)
    assert control['sd'] == pytest.approx(1.0)
    assert control['sem'] == pytest.approx(0.57735, abs=1e-5)
    knockdown = set_statistics_calculator(KNOCKDOWN)
    assert knockdown['mean'] == 25.0
    assert knockdown['sd'] == pytest.approx(5.0)
    assert knockdown['sem'] == pytest.approx(2.88675, abs=1e-5)
    empty = set_statistics_calculator([])
    assert empty['n'] == 0 and math.isnan(empty['mean'])


# ---- test_the_paired_test_of_before_and_after ----------------------------------------
def test_the_paired_test_of_before_and_after() -> None:
    """
    ---- Summary ----
    Main function to check the paired t-test of MATHS.md section 11.4, the numbers
    of a Before and after plot, and its legend sentence.

    ---- Inputs ----
    None.

    ---- Globals read ----
    P_TOLERANCE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Before 10, 12, 14 and after 7, 8, 12: d = -3, -4, -2; mean -3, SD 1; t = -3 /
    (1 / sqrt(3)) = -5.196; df = 2; p = 1 - 5.196152 / sqrt(5.196152² + 2) =
    0.035099.

    ---- Helpers ----
    None.
    """

    # ---- 1 The test ------------------------------------------------------------------
    before, after = [10.0, 12.0, 14.0], [7.0, 8.0, 12.0]
    result = pairs_tester(before, after)
    assert result['t'] == pytest.approx(-5.196152, abs=1e-6)
    assert (result['df'], result['n']) == (2.0, 3)
    assert result['p'] == pytest.approx(0.035099, abs=P_TOLERANCE)
    checked = scipy_stats.ttest_rel(after, before)
    assert result['t'] == pytest.approx(checked.statistic)
    assert result['p'] == pytest.approx(checked.pvalue)

    # ---- 2 What cannot be tested -----------------------------------------------------
    assert pairs_tester([5.0, 6.0], [5.0, None]) is None  # one pair
    assert pairs_tester([1.0, 2.0, 3.0], [2.0, 3.0, 4.0]) is None  # the same change
    with pytest.raises(ValueError):
        pairs_tester([1.0, 2.0], [1.0])

    # ---- 3 The plot ------------------------------------------------------------------
    statistics = paired_statistics_builder([{'name': 'control',
                                             'before': before,
                                             'after': after,
                                             },
                                            {'name': 'knockdown',
                                             'before': [5.0, 6.0],
                                             'after': [5.0, None],
                                             },
                                            ],
                                           ['Baseline', 'After KCN'],
                                           )
    assert [column['label'] for column in statistics['columns']] == ['Baseline',
                                                                     'After KCN',
                                                                     ]
    assert [one['mean'] for one in statistics['columns'][1]['sets']] == [9.0, 5.0]
    assert [one['set'] for one in statistics['tests']] == ['control']
    assert statistics['tests'][0]['p_corrected'] == pytest.approx(0.035099,
                                                                  abs=P_TOLERANCE,
                                                                  )
    assert legend_sentence_writer(statistics) == (
        'Each line is one experiment, and the mean of each set is marked (control '
        'n = 3, knockdown n = 1 to 2). knockdown has one experiment, so it was not '
        'tested. The two regions of each set were compared with a paired t-test '
        '(two-tailed): * p < 0.05, ** p < 0.01, *** p < 0.001; a comparison '
        'without a mark gave p ≥ 0.05.'
        )


# ---- test_the_two_tests_between_sets -------------------------------------------------
def test_the_two_tests_between_sets() -> None:
    """
    ---- Summary ----
    Main function to check Student's and Welch's t-test on the two sets of MATHS.md
    section 11.3, by hand and against scipy's own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CONTROL, KNOCKDOWN, P_TOLERANCE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Student's: sp² = (2 x 1 + 2 x 25) / 4 = 13; e = sqrt(13 x 2 / 3) = 2.943920;
    t = (11 - 25) / 2.943920 = -4.755564; df = 4; p = 0.008934. Welch's: e =
    sqrt(1 / 3 + 25 / 3) = 2.943920, the same t; df = 8.666667² / (0.333333² / 2 +
    8.333333² / 2) = 75.111111 / 34.777778 = 2.159744; p = 0.035635.

    ---- Helpers ----
    None.
    """

    # ---- 1 Student's -----------------------------------------------------------------
    student = sets_tester(CONTROL, KNOCKDOWN)
    assert student['t'] == pytest.approx(-4.755564, abs=1e-6)
    assert student['df'] == 4.0
    assert student['p'] == pytest.approx(0.008934, abs=P_TOLERANCE)
    checked = scipy_stats.ttest_ind(CONTROL, KNOCKDOWN, equal_var=True)
    assert student['p'] == pytest.approx(checked.pvalue)

    # ---- 2 Welch's -------------------------------------------------------------------
    welch = sets_tester(CONTROL, KNOCKDOWN, 'welch')
    assert welch['t'] == pytest.approx(-4.755564, abs=1e-6)
    assert welch['df'] == pytest.approx(2.159744, abs=1e-6)
    assert welch['p'] == pytest.approx(0.035635, abs=P_TOLERANCE)
    checked = scipy_stats.ttest_ind(CONTROL, KNOCKDOWN, equal_var=False)
    assert welch['p'] == pytest.approx(checked.pvalue)

    # ---- 3 Sets of different sizes, and what cannot be tested ------------------------
    uneven = sets_tester(CONTROL + [None], [20.0, 30.0])
    checked = scipy_stats.ttest_ind(CONTROL, [20.0, 30.0], equal_var=True)
    assert (uneven['df'], uneven['t']) == (3.0, pytest.approx(checked.statistic))
    assert uneven['p'] == pytest.approx(checked.pvalue)
    assert sets_tester([5.0, 5.0], [7.0, 7.0]) is None  # no spread in either
    with pytest.raises(ValueError):
        sets_tester(CONTROL, KNOCKDOWN, 'anova')


# ---- test_the_value_of_an_experiment_in_a_region -------------------------------------
def test_the_value_of_an_experiment_in_a_region() -> None:
    """
    ---- Summary ----
    Main function to check the value of a made-up experiment in each region, in each
    value it can be shown in (the numbers of MATHS.md section 11.1), nothing for
    what it does not have, a haem never as % of baseline, and the values of the
    experiments of a set.

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
    OCR: baseline 10, quick region 4, settled region 6; from baseline 6 - 10 = -4;
    % of baseline 6 / 10 x 100 = 60 and 4 / 10 x 100 = 40; per OD 6 / 2 = 3. Δψ:
    settled (118 + 118) / 2 = 118, change 118 - 130 = -12; the quick region has one
    spectrum with a value, 120.

    ---- Helpers ----
    _experiment_maker
    """

    # ---- 1 The OCR in each value -----------------------------------------------------
    experiment = _experiment_maker()
    assert region_value_reader(experiment, 'vo2', 'raw', 0) == pytest.approx(10.0)
    assert region_value_reader(experiment, 'vo2', 'raw', 1) == pytest.approx(6.0)
    assert region_value_reader(experiment, 'vo2', 'raw', 1, 'quick') == pytest.approx(
        4.0,
        )
    assert region_value_reader(experiment, 'vo2', 'raw', 0, 'quick') == pytest.approx(
        10.0,
        )
    assert region_value_reader(experiment, 'vo2', 'change', 1) == pytest.approx(-4.0)
    assert region_value_reader(experiment, 'vo2', 'baseline', 1) == pytest.approx(60.0)
    assert region_value_reader(experiment,
                               'vo2',
                               'baseline',
                               1,
                               'quick',
                               ) == pytest.approx(40.0)
    assert region_value_reader(experiment, 'vo2', 'od', 1) == pytest.approx(3.0)

    # ---- 2 A haem and Δψ -------------------------------------------------------------
    assert region_value_reader(experiment, 'haem_cytbh', 'percent', 1) == pytest.approx(
        50.0,
        )
    assert region_value_reader(experiment, 'haem_cytbh', 'baseline', 1) is None
    assert region_value_reader(experiment, 'haem_cytbh', 'change', 1) is None
    assert region_value_reader(experiment, 'delta_psi', 'raw', 1) == pytest.approx(
        118.0,
        )
    assert region_value_reader(experiment, 'delta_psi', 'change', 1) == pytest.approx(
        -12.0,
        )
    assert region_value_reader(experiment,
                               'delta_psi',
                               'raw',
                               1,
                               'quick',
                               ) == pytest.approx(120.0)

    # ---- 3 What the file does not have -----------------------------------------------
    assert region_value_reader(experiment, 'vo2', 'raw', 2) is None
    assert region_value_reader(experiment, 'haem_cytcc', 'percent', 1) is None
    assert region_value_reader(None, 'vo2', 'raw', 0) is None
    with pytest.raises(ValueError):
        region_value_reader(experiment, 'vo2', 'raw', 1, 'slow')

    # ---- 4 The experiments of a set --------------------------------------------------
    sets = [{'name': 'control', 'names': ['one', 'two', 'gone'], 'colour': '#000000'}]
    experiments = {'one': experiment, 'two': _experiment_maker(scale=2.0)}
    filled = set_values_lister(sets, experiments, 'vo2', 'raw', 1)
    assert filled[0]['values'] == [pytest.approx(6.0), pytest.approx(12.0), None]
    assert filled[0]['colour'] == '#000000' and 'values' not in sets[0]
    percent = set_values_lister(sets, experiments, 'vo2', 'baseline', 1)
    assert percent[0]['values'] == [pytest.approx(60.0), pytest.approx(60.0), None]
