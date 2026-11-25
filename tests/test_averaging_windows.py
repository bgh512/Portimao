"""
Tests that the averaging windows of both kinds (settled, ending before the next
addition, and quick, starting after each addition) fall, and follow a pulled edge, as
worked out by hand, that a figure needing them offers the window step when none are set
up, and that it asks which kind it uses only when both are.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from types import SimpleNamespace

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.spectral_difference import spectral_averager
from utils_shared import survey
from utils_shared.averaging import (baseline_percent_adder,
                                    experiment_averages_calculator,
                                    kind_span_lister,
                                    LEFT_OUT_PROBLEM,
                                    quick_span_lister,
                                    window_kind_picker,
                                    window_layout_finder,
                                    window_pick_lister,
                                    window_plan_finder,
                                    window_plan_reader,
                                    window_pointer_reader,
                                    window_row_teller,
                                    window_shown_maker,
                                    window_span_lister,
                                    window_value_setter,
                                    window_values_maker,
                                    )
from utils_shared.delta_psi import DELTA_PSI_COLUMN
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.individual_experiment_exporter import averages_table_builder
from utils_shared.schema import TIME_COLUMN
from utils_viewer import viewer_stages
from utils_viewer.viewer_edges import every_file_setter, PART_STYLES
from utils_viewer.viewer_stages import _unfit_windows_lister, _windows_keeper


# ---- CONSTANTS -----------------------------------------------------------------------
# A made-up run of 30 min with additions at 10 and 20 min. The settled windows are
# 120 s long and end 30 s before the next addition; the last ends 0.5 min before the
# end of the run; the baseline needs 10 s; an edge moves in steps of 5 s. The quick
# windows are 60 s long and start 30 s after their addition; they are unticked in
# VALUES and ticked in BOTH.
ADDITIONS = [10.0, 20.0]
RECORDING = (0.0, 30.0)
FINAL_GAP_MIN = 0.5
BASELINE_MINIMUM_S = 10.0
STEP_S = 5.0
VALUES = {'window_s': 120.0,
          'gap_s': 30.0,
          'is_on': 1.0,
          'quick_s': 60.0,
          'delay_s': 30.0,
          'quick_is_on': 0.0,
          }
BOTH = dict(VALUES, quick_is_on=1.0)
VO2_COLUMN = 'VoO2'
# The windows of a dataset as the answers keep them: 2 min settled windows ending
# 0.5 min before the next addition and the last 0.5 min before the end of the run;
# 1 min quick windows starting 0.5 min after their addition.
PLAN = {'window_minutes': 2.0,
        'gap_minutes': 0.5,
        'final_gap_minutes': 0.5,
        'quick_minutes': 1.0,
        'delay_minutes': 0.5,
        'each_window': {},
        }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _response_experiment_builder ----------------------------------------------------
def _response_experiment_builder() -> dict:
    """
    ---- Summary ----
    Helper function to build an experiment whose oxygen consumption dips just after
    each addition and then settles on another level, so the quick and the settled
    windows give different averages.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS, VO2_COLUMN (module constants); TIME_COLUMN.

    ---- Outputs ----
    dict
        Experiment with a point every 0.25 min from 0 to 30 min and additions at 10
        and 20 min. VoO2 is 10 before 10 min, 4 from 10 to 12 min, 6 from 12 to
        20 min, 1 from 20 to 22 min and 2 from 22 min on.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(121) * 0.25
    values = np.select([times < 10, times < 12, times < 20, times < 22],
                       [10.0, 4.0, 6.0, 1.0],
                       2.0,
                       )
    return {'experiment_name': 'responses',
            'VoO2': pd.DataFrame({TIME_COLUMN: times, VO2_COLUMN: values}),
            'raw_spectra': {},
            'metadata': {'events': [{'time': time, 'label': 'addition'}
                                    for time in ADDITIONS
                                    ],
                         },
            }


# ---- _views_experiment_builder -------------------------------------------------------
def _views_experiment_builder() -> dict:
    """
    ---- Summary ----
    Helper function to build the experiment of _response_experiment_builder with one
    haem, bH, in its three views, and a delta psi that has no value for part of the
    run.

    ---- Inputs ----
    None.

    ---- Globals read ----
    DELTA_PSI_COLUMN, TIME_COLUMN (imported).

    ---- Outputs ----
    dict
        The experiment with a spectrum every 0.25 min from 0 to 30 min. Before 10 min,
        from 10 to 20 min and after 20 min bH is 0.5, -2.0 and -3.5 as ΔD
        ('haem_delta_abs'), 12.5, 10.0 and 8.5 as absorbance ('haem_abs') and 80, 50
        and 20 as % oxidised ('haem_percent'). Δψ ('delta_psi') is 130 mV before
        10 min, then empty but for 116 at 18.5 and 18.75 min, 118 at 19 min and 120 at
        19.25 and 19.5 min.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _response_experiment_builder
    """

    experiment = _response_experiment_builder()
    times = np.arange(121) * 0.25
    for key, levels in (('haem_delta_abs', (0.5, -2.0, -3.5)),
                        ('haem_abs', (12.5, 10.0, 8.5)),
                        ('haem_percent', (80.0, 50.0, 20.0)),
                        ):
        values = np.select([times < 10, times < 20], levels[:2], levels[2])
        experiment[key] = pd.DataFrame({TIME_COLUMN: times, 'bH': values})
    delta_psi_mV = np.where(times < 10, 130.0, np.nan)
    for time, value in ((18.5, 116.0),
                        (18.75, 116.0),
                        (19.0, 118.0),
                        (19.25, 120.0),
                        (19.5, 120.0),
                        ):
        delta_psi_mV[times == time] = value
    experiment['delta_psi'] = pd.DataFrame({TIME_COLUMN: times,
                                            DELTA_PSI_COLUMN: delta_psi_mV,
                                            },
                                           )
    return experiment


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_figure_asks_which_windows_only_with_both_kinds ---------------------------
def test_a_figure_asks_which_windows_only_with_both_kinds(
    monkeypatch: pytest.MonkeyPatch,
    ) -> None:
    """
    ---- Summary ----
    Main function to check which kind of window a figure uses: with both kinds set up
    one question (4.6.2) asks, offering the kind the figure used last time; with one
    kind the figure uses it and nothing is asked. The question is stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the stand-in for the question in place, and takes it away afterwards.

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

    asked = []
    def asker(question: str, options: list, default: str, **kwargs: object) -> str:
        asked.append(
            (question, [kind for kind, _ in options], default, kwargs['number']),
            )
        return 'quick'
    monkeypatch.setattr(survey, 'choice_asker', asker)
    monkeypatch.setattr(survey, 'info_printer', lambda *args, **kwargs: None)

    # ---- 1 Both kinds: the question, with the kind used last time --------------------
    answers = {'settled_windows': True, 'quick_windows': True}
    kind = survey.window_kind_asker(answers,
                                    {'tr_window_kind': 'settled'},
                                    'tr_window_kind',
                                    )
    assert kind == 'quick' and answers['tr_window_kind'] == 'quick'
    assert asked == [('Which averaging regions should this figure use?',
                      ['settled', 'quick'],
                      'settled',
                      '4.6.2',
                      ),
                     ]
    survey.window_kind_asker(answers, {'ho_window_kind': 'quick'}, 'ho_window_kind')
    assert asked[-1][2] == 'quick'

    # ---- 2 One kind: it is used, and nothing is asked --------------------------------
    answers = {'settled_windows': False, 'quick_windows': True}
    assert survey.window_kind_asker(answers, {}, 'ex_window_kind') == 'quick'
    answers = {'settled_windows': True, 'quick_windows': False}
    assert survey.window_kind_asker(answers,
                                    {'ex_window_kind': 'quick'},
                                    'ex_window_kind',
                                    ) == 'settled'
    assert answers['ex_window_kind'] == 'settled'
    assert len(asked) == 2


# ---- test_a_figure_without_windows_offers_the_window_step ----------------------------
def test_a_figure_without_windows_offers_the_window_step(
    monkeypatch: pytest.MonkeyPatch,
    ) -> None:
    """
    ---- Summary ----
    Main function to check what a figure that needs the averaging windows does: with
    windows set up nothing is asked; with none, one question offers the window step of
    the processing, and the figure is made only when windows are set up after it. No
    window or gap is asked for by the figure itself. The question and the window step
    are stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the stand-in for the question in place, and takes it away afterwards.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    asked, runs = [], []
    reply = {'answer': True}
    def asker(question: str, default: bool = False, **kwargs: object) -> bool:
        asked.append((question, default, kwargs.get('number')))
        return reply['answer']
    def adder_maker(answers: dict, is_added: bool):
        def adder() -> bool:
            runs.append(is_added)
            answers['averaging'] = is_added
            return is_added
        return adder
    monkeypatch.setattr(survey, 'yes_no_asker', asker)
    monkeypatch.setattr(survey, 'info_printer', lambda *args, **kwargs: None)

    # ---- 1 Windows set up: nothing is asked ------------------------------------------
    answers = {'averaging': True}
    assert survey.windows_ensurer(answers, adder_maker(answers, True)) is True
    assert asked == [] and runs == []

    # ---- 2 None, yes, and windows are added ------------------------------------------
    answers = {'averaging': False}
    assert survey.windows_ensurer(answers, adder_maker(answers, True)) is True
    assert asked == [('Do you want to add them now?', True, '4.6.1')]
    assert runs == [True]

    # ---- 3 None, yes, but the windows are left unticked ------------------------------
    answers = {'averaging': False}
    assert survey.windows_ensurer(answers, adder_maker(answers, False)) is False
    assert runs == [True, False]

    # ---- 4 None, and no: the window step is not run ----------------------------------
    reply['answer'] = False
    answers = {'averaging': False}
    assert survey.windows_ensurer(answers, adder_maker(answers, True)) is False
    assert len(asked) == 3 and runs == [True, False]

    # ---- 5 None, and the step cannot be run: nothing is asked ------------------------
    assert survey.windows_ensurer({'averaging': False}, None) is False
    assert len(asked) == 3


# ---- test_a_window_can_be_switched_off_and_set ---------------------------------------
def test_a_window_can_be_switched_off_and_set() -> None:
    """
    ---- Summary ----
    Main function to check the values typed or ticked in the window step: a length or
    a gap that can be used is taken, a length of 0 and a gap below 0 change nothing,
    the tick box switches the windows off and on, and one change reaches every file.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VALUES (module constant).

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

    assert window_value_setter(VALUES, 'window_s', 60) == dict(VALUES, window_s=60.0)
    assert window_value_setter(VALUES, 'gap_s', 0) == dict(VALUES, gap_s=0.0)
    assert window_value_setter(VALUES, 'window_s', 0) == VALUES
    assert window_value_setter(VALUES, 'gap_s', -1) == VALUES
    off = window_value_setter(VALUES, 'is_on', 0.0)
    assert off == dict(VALUES, is_on=0.0)
    assert window_value_setter(off, 'is_on', 1.0) == VALUES
    # the quick windows: their length, how long after the addition, their tick box
    assert window_value_setter(VALUES, 'quick_s', 45) == dict(VALUES, quick_s=45.0)
    assert window_value_setter(VALUES, 'delay_s', 0) == dict(VALUES, delay_s=0.0)
    assert window_value_setter(VALUES, 'quick_s', 0) == VALUES
    assert window_value_setter(VALUES, 'delay_s', -1) == VALUES
    assert window_value_setter(VALUES, 'quick_is_on', 1.0) == BOTH
    assert window_value_setter(BOTH, 'quick_is_on', 0.0) == VALUES
    assert VALUES == {'window_s': 120.0,  # not changed
                      'gap_s': 30.0,
                      'is_on': 1.0,
                      'quick_s': 60.0,
                      'delay_s': 30.0,
                      'quick_is_on': 0.0,
                      }

    changed = every_file_setter({'one': dict(VALUES), 'two': dict(VALUES)},
                                ['one', 'two'],
                                'window_s',
                                90.0,
                                lambda name, values, key, value: (
                                    window_value_setter(values, key, value)),
                                )
    assert changed == {'one': dict(VALUES, window_s=90.0),
                       'two': dict(VALUES, window_s=90.0),
                       }


# ---- test_a_pulled_end_gives_the_gap -------------------------------------------------
def test_a_pulled_end_gives_the_gap() -> None:
    """
    ---- Summary ----
    Main function to check that the end of a window pulled to a time gives how long
    before the next addition the windows end, in whole steps of 5 s and never below 0.

    ---- Inputs ----
    None.

    ---- Globals read ----
    The module constants.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The ends that can be pulled are at 9.5 and 19.5 min (the last window's cannot).
    Pulled to 19.0 min: the nearest is 19.5, before the addition at 20, so 1 min =
    60 s. To 9.82 min: nearest 9.5, before the addition at 10, 0.18 min = 10.8 s ->
    10 s. To 20.3 min: nearest 19.5, past its addition at 20, -18 s -> 0 s.

    ---- Helpers ----
    None.
    """

    def gap(time_min: float) -> float:
        return window_pointer_reader(VALUES,
                                     'gap_s',
                                     time_min,
                                     ADDITIONS,
                                     RECORDING,
                                     FINAL_GAP_MIN,
                                     STEP_S,
                                     )
    assert gap(19.0) == pytest.approx(60.0)
    assert gap(9.82) == pytest.approx(10.0)
    assert gap(20.3) == pytest.approx(0.0)
    # without settled windows only the end of the baseline, at 9.5 min, can be pulled:
    # to 9.0 min it is 1 min = 60 s before the addition at 10; to 19.0 min it is past
    # that addition, so 0 s
    only_quick = dict(BOTH, is_on=0.0)
    assert window_pointer_reader(only_quick,
                                 'gap_s',
                                 9.0,
                                 ADDITIONS,
                                 RECORDING,
                                 FINAL_GAP_MIN,
                                 STEP_S,
                                 ) == pytest.approx(60.0)
    assert window_pointer_reader(only_quick,
                                 'gap_s',
                                 19.0,
                                 ADDITIONS,
                                 RECORDING,
                                 FINAL_GAP_MIN,
                                 STEP_S,
                                 ) == pytest.approx(0.0)


# ---- test_a_pulled_quick_window_gives_its_start_and_length ---------------------------
def test_a_pulled_quick_window_gives_its_start_and_length() -> None:
    """
    ---- Summary ----
    Main function to check that the start of a quick window pulled to a time gives how
    long after their addition the quick windows start (never below 0), and its end
    their length (at least one step), in whole steps of 5 s.

    ---- Inputs ----
    None.

    ---- Globals read ----
    The module constants.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The quick windows run from 10.5 to 11.5 and from 20.5 to 21.5 min. A start pulled
    to 21.0 min: the nearest is 20.5, of the addition at 20, so 1 min = 60 s. To
    10.07 min: nearest 10.5, addition at 10, 0.07 min = 4.2 s -> 5 s. To 9.8 min:
    before its addition at 10, -12 s -> 0 s. An end pulled to 12.0 min: the nearest
    is 11.5, of the window starting at 10.5, so 1.5 min = 90 s. To 21.93 min: nearest
    21.5, starting at 20.5, 1.43 min = 85.8 s -> 85 s. To 20.51 min: nearest 21.5,
    starting at 20.5, 0.6 s -> 0 -> one step, 5 s.

    ---- Helpers ----
    None.
    """

    def pulled(key: str, time_min: float) -> float:
        return window_pointer_reader(BOTH,
                                     key,
                                     time_min,
                                     ADDITIONS,
                                     RECORDING,
                                     FINAL_GAP_MIN,
                                     STEP_S,
                                     )
    assert pulled('delay_s', 21.0) == pytest.approx(60.0)
    assert pulled('delay_s', 10.07) == pytest.approx(5.0)
    assert pulled('delay_s', 9.8) == pytest.approx(0.0)
    assert pulled('quick_s', 12.0) == pytest.approx(90.0)
    assert pulled('quick_s', 21.93) == pytest.approx(85.0)
    assert pulled('quick_s', 20.51) == pytest.approx(5.0)


# ---- test_a_pulled_start_gives_the_length --------------------------------------------
def test_a_pulled_start_gives_the_length() -> None:
    """
    ---- Summary ----
    Main function to check that the start of a window pulled to a time gives the
    length of the windows, in whole steps of 5 s and of at least one step, and that a
    file without additions keeps the length it had.

    ---- Inputs ----
    None.

    ---- Globals read ----
    The module constants.

    ---- Outputs ----
    None
        Nothing.

    ---- Equations ----
    The starts are at 7.5, 17.5 and 27.5 min, the ends at 9.5, 19.5 and 29.5 min.
    Pulled to 17.0 min: the nearest start is 17.5, of the window ending at 19.5, so
    2.5 min = 150 s. To 27.93 min: nearest 27.5, ending at 29.5, 1.57 min = 94.2 s ->
    95 s. To 19.49 min: nearest 17.5, ending at 19.5, 0.6 s -> 0 -> one step, 5 s.

    ---- Globals mutated ----
    None.

    ---- Helpers ----
    None.
    """

    def length(time_min: float) -> float:
        return window_pointer_reader(VALUES,
                                     'window_s',
                                     time_min,
                                     ADDITIONS,
                                     RECORDING,
                                     FINAL_GAP_MIN,
                                     STEP_S,
                                     )
    assert length(17.0) == pytest.approx(150.0)
    assert length(27.93) == pytest.approx(95.0)
    assert length(19.49) == pytest.approx(5.0)
    assert window_pointer_reader(VALUES,
                                 'window_s',
                                 17.0,
                                 [],
                                 RECORDING,
                                 FINAL_GAP_MIN,
                                 STEP_S,
                                 ) == 120.0


# ---- test_the_plot_shows_the_windows -------------------------------------------------
def test_the_plot_shows_the_windows() -> None:
    """
    ---- Summary ----
    Main function to check what the window step draws for a file: the start and the
    end of every window as edges named by their window, the end of the last settled
    window as the edge of how long before the end of the file it ends, the first of
    each kind with its words, the baseline as a part of its own kind that says "baseline", the windows
    as blue parts and those that do not fit as red ones, and nothing when the windows
    are unticked or the file has no additions.

    ---- Inputs ----
    None.

    ---- Globals read ----
    The module constants; PART_STYLES of the window.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    120 s and 30 s: windows 7.5 to 9.5, 17.5 to 19.5 and 27.5 to 29.5 min. 720 s
    (12 min): the baseline 0 to 9.5 (cut at the start of the run, it fits), 7.5 to
    19.5 (starts before its addition at 10) and 17.5 to 29.5 (before its addition at
    20) do not fit.

    ---- Helpers ----
    None.
    """

    def layout(values: dict, additions: list = ADDITIONS) -> tuple:
        return window_layout_finder(values,
                                    additions,
                                    RECORDING,
                                    FINAL_GAP_MIN,
                                    BASELINE_MINIMUM_S,
                                    )

    # ---- 1 Windows that fit ----------------------------------------------------------
    edges, parts = layout(VALUES)
    assert edges == [('window_s@average0', 7.5, 'baseline 120 s', 'baseline'),
                     ('gap_s@average0', 9.5, '', 'baseline_end'),
                     ('window_s@average1', 17.5, 'region 120 s', 'average'),
                     ('gap_s@average1',
                      19.5,
                      'ends 30 s before the addition',
                      'average_end',
                      ),
                     ('window_s@average2', 27.5, '', 'average'),
                     ('final_gap_s',
                      29.5,
                      'ends 30 s before the end of the file',
                      'average_end',
                      ),
                     ]
    assert parts == [(7.5, 9.5, 'baseline'),
                     (17.5, 19.5, 'average'),
                     (27.5, 29.5, 'average'),
                     ]

    # ---- 2 Windows too long to fit ---------------------------------------------------
    _, parts = layout(dict(VALUES, window_s=720.0))
    assert parts == [(0.0, 9.5, 'baseline'),
                     (7.5, 19.5, 'average_unfit'),
                     (17.5, 29.5, 'average_unfit'),
                     ]

    # ---- 3 No windows ----------------------------------------------------------------
    assert layout(dict(VALUES, is_on=0.0)) == ([], [])
    assert layout(VALUES, []) == ([], [])
    assert layout(BOTH, []) == ([], [])

    # ---- 4 Both kinds: the quick windows after the settled ones ----------------------
    quick_edges = [('delay_s@quick1', 10.5, 'starts 30 s after the addition', 'quick'),
                   ('quick_s@quick1', 11.5, 'quick region 60 s', 'quick_end'),
                   ('delay_s@quick2', 20.5, '', 'quick'),
                   ('quick_s@quick2', 21.5, '', 'quick_end'),
                   ]
    quick_parts = [(10.5, 11.5, 'quick'), (20.5, 21.5, 'quick')]
    assert layout(BOTH) == (edges + quick_edges,
                            [(7.5, 9.5, 'baseline'),
                             (17.5, 19.5, 'average'),
                             (27.5, 29.5, 'average'),
                             ]
                            + quick_parts,
                            )

    # ---- 5 Quick windows alone: the baseline stays, with both its edges --------------
    assert layout(dict(BOTH, is_on=0.0)) == (
        [('window_s@average0', 7.5, 'baseline 120 s', 'baseline'),
         ('gap_s@average0', 9.5, 'ends 30 s before the addition', 'baseline_end'),
         ]
        + quick_edges,
        [(7.5, 9.5, 'baseline')] + quick_parts,
        )

    # ---- 6 Quick windows too long to fit ---------------------------------------------
    _, parts = layout(dict(BOTH, quick_s=720.0))
    assert parts[3:] == [(10.5, 22.5, 'average_unfit'), (20.5, 32.5, 'average_unfit')]

    # ---- 7 The window knows how to draw every kind -----------------------------------
    assert {'average', 'average_end', 'average_unfit', 'quick', 'quick_end'} <= set(
        PART_STYLES,
        )
    assert PART_STYLES['average'][3] != PART_STYLES['average_end'][3]  # two rows
    assert PART_STYLES['quick'][3] != PART_STYLES['quick_end'][3]
    assert PART_STYLES['quick'][0] != PART_STYLES['average'][0]  # green, not blue
    # the baseline has a colour of its own, and its two edges their own rows
    assert {'baseline', 'baseline_end'} <= set(PART_STYLES)
    assert PART_STYLES['baseline'][3] != PART_STYLES['baseline_end'][3]
    assert PART_STYLES['baseline'][0] not in (PART_STYLES['average'][0],
                                              PART_STYLES['quick'][0],
                                              PART_STYLES['average_unfit'][0],
                                              )


# ---- test_the_quick_windows_fall_after_the_additions ---------------------------------
def test_the_quick_windows_fall_after_the_additions() -> None:
    """
    ---- Summary ----
    Main function to check where the quick windows of a file fall and which do not
    fit, what a figure that uses one kind of window is given, and how the windows that
    do not fit are named.

    ---- Inputs ----
    None.

    ---- Globals read ----
    The module constants.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Starting 0.5 min after the addition and 1 min long: 10 + 0.5 = 10.5 to 11.5, and
    20 + 0.5 = 20.5 to 21.5. 12 min long: 10.5 to 22.5 ends after the addition at 20,
    and 20.5 to 32.5 after the end of the run at 30, so neither fits. Starting at the
    addition and 10 min long: 10 to 20 and 20 to 30 end exactly at the next addition
    and at the end of the run, so both fit.

    ---- Helpers ----
    None.
    """

    # ---- 1 Windows that fit ----------------------------------------------------------
    assert quick_span_lister(ADDITIONS, RECORDING, 1.0, 0.5) == [
        ('quick1', 10.5, 11.5, None),
        ('quick2', 20.5, 21.5, None),
        ]
    assert quick_span_lister(ADDITIONS, RECORDING, 10.0, 0.0) == [
        ('quick1', 10.0, 20.0, None),
        ('quick2', 20.0, 30.0, None),
        ]

    # ---- 2 Windows too long to fit ---------------------------------------------------
    unfit = quick_span_lister(ADDITIONS, RECORDING, 12.0, 0.5)
    assert unfit == [
        ('quick1', 10.5, 22.5, 'Insufficient time between additions 1 and 2.'),
        ('quick2', 20.5, 32.5, 'Insufficient recording time after the final addition.'),
        ]

    # ---- 3 What a figure that uses one kind is given ---------------------------------
    settled = window_span_lister(ADDITIONS, RECORDING, 2.0, 0.5, FINAL_GAP_MIN)
    def spans(kind: str) -> list:
        return kind_span_lister(kind,
                                ADDITIONS,
                                RECORDING,
                                2.0,
                                0.5,
                                FINAL_GAP_MIN,
                                1.0,
                                0.5,
                                )
    assert spans('settled') == settled
    assert spans('quick') == [('average0', 7.5, 9.5, None),
                              ('average1', 10.5, 11.5, None),
                              ('average2', 20.5, 21.5, None),
                              ]
    with pytest.raises(ValueError, match='not known'):
        spans('slow')

    # ---- 4 The names of the windows that do not fit ----------------------------------
    long = window_span_lister(ADDITIONS, RECORDING, 12.0, 0.5, FINAL_GAP_MIN)
    assert _unfit_windows_lister(settled, []) == []
    assert _unfit_windows_lister(long, unfit) == [
        'the settled one before addition 2',
        'the settled one after the last addition',
        'the quick one after addition 1',
        'the quick one after addition 2',
        ]
    assert _unfit_windows_lister(settled[:1], unfit[:1]) == [
        'the quick one after addition 1',
        ]


# ---- test_both_kinds_are_averaged_from_one_baseline ----------------------------------
def test_both_kinds_are_averaged_from_one_baseline() -> None:
    """
    ---- Summary ----
    Main function to check the averages of the settled and the quick windows of one
    file, their change from the one baseline, what a figure that uses one kind reads,
    and the averaged spectra of the quick windows.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The trace is 10 before 10 min, 4 until 12, 6 until 20, 1 until 22 and 2 after.
    Baseline 7.5 to 9.5: 10. Settled windows 17.5 to 19.5 and 27.5 to 29.5: 6 and 2,
    so 60 and 20 % of the baseline, -4 and -8 from it. Quick windows 10.5 to 11.5 and
    20.5 to 21.5: 4 and 1, so 40 and 10 %, -6 and -9. Spectra, one every 0.5 min for
    12 min with additions at 4 and 8 min: (2, 0) before 4 min, (5, 1) until 6, (3, 1)
    until 8, (9, 4) until 10 and (7, 4) after; the quick windows 4.5 to 5.5 and 8.5
    to 9.5 hold three spectra each, (5, 1) and (9, 4), where the settled ones would
    give (3, 1) and (7, 4).

    ---- Helpers ----
    _response_experiment_builder
    """

    def averages(**quick: object) -> dict:
        return experiment_averages_calculator(_response_experiment_builder(),
                                              window_minutes=2.0,
                                              gap_minutes=0.5,
                                              final_window_gap_minutes=0.5,
                                              baseline_minimum_seconds=10.0,
                                              vo2_source='raw',
                                              haem_source=None,
                                              **quick,
                                              )['averages']

    # ---- 1 Both kinds ----------------------------------------------------------------
    both = averages(quick_minutes=1.0, delay_minutes=0.5)
    expected = {'average0': ('baseline', 7.5, 9.5, 10.0, 100.0, 0.0),
                'average1': ('settled', 17.5, 19.5, 6.0, 60.0, -4.0),
                'average2': ('settled', 27.5, 29.5, 2.0, 20.0, -8.0),
                'quick1': ('quick', 10.5, 11.5, 4.0, 40.0, -6.0),
                'quick2': ('quick', 20.5, 21.5, 1.0, 10.0, -9.0),
                }
    assert list(both['windows']) == list(expected)
    assert both['skipped'] == {}
    for name, (kind, start, end, mean, change, delta) in expected.items():
        window = both['windows'][name]
        stats = window['vo2'][VO2_COLUMN]
        assert window['kind'] == kind
        assert (window['start_time'], window['end_time']) == pytest.approx((start, end))
        assert stats['mean'] == pytest.approx(mean)
        assert stats['change'] == pytest.approx(change)
        assert stats['delta'] == pytest.approx(delta)

    # ---- 2 One kind, or the other ----------------------------------------------------
    assert list(averages()['windows']) == ['average0', 'average1', 'average2']
    only_quick = averages(quick_minutes=1.0, delay_minutes=0.5, is_settled=False)
    assert list(only_quick['windows']) == ['average0', 'quick1', 'quick2']

    # ---- 3 What a figure that uses one kind reads ------------------------------------
    quick = window_kind_picker(both, 'quick')['windows']
    assert list(quick) == ['average0', 'average1', 'average2']
    assert [quick[name]['vo2'][VO2_COLUMN]['mean'] for name in quick] == pytest.approx(
        [10.0, 4.0, 1.0],
        )
    settled = window_kind_picker(both, 'settled')['windows']
    assert [settled[name]['vo2'][VO2_COLUMN]['mean'] for name in settled] == (
        pytest.approx([10.0, 6.0, 2.0])
        )
    assert list(both['windows']) == list(expected)  # not changed
    with pytest.raises(ValueError, match='not known'):
        window_kind_picker(both, 'slow')

    # ---- 4 Quick windows that do not fit are left out, and named ---------------------
    long = averages(quick_minutes=12.0, delay_minutes=0.5)
    assert list(long['windows']) == ['average0', 'average1', 'average2']
    assert {name: window['kind'] for name, window in long['skipped'].items()} == {
        'quick1': 'quick',
        'quick2': 'quick',
        }
    assert list(window_kind_picker(long, 'quick')['skipped']) == ['average1',
                                                                  'average2',
                                                                  ]

    # ---- 5 The averaged spectra of the quick windows ---------------------------------
    times = np.arange(25) * 0.5
    spectra = np.select([times[:, None] < 4,
                         times[:, None] < 6,
                         times[:, None] < 8,
                         times[:, None] < 10,
                         ],
                        [[2.0, 0.0], [5.0, 1.0], [3.0, 1.0], [9.0, 4.0]],
                        [7.0, 4.0],
                        )
    experiment = {'experiment_name': 'spectra',
                  'raw_spectra': {'Cyt': {'wavelengths': np.array([550.0, 600.0]),
                                          'time': times,
                                          'attenuation': spectra,
                                          },
                                  },
                  'metadata': {'events': [{'time': 4.0}, {'time': 8.0}]},
                  }
    result = spectral_averager(experiment,
                               'Cyt',
                               'attenuation',
                               window_minutes=2.0,
                               gap_minutes=0.5,
                               final_window_gap_minutes=0.5,
                               kind='quick',
                               quick_minutes=1.0,
                               delay_minutes=0.5,
                               )['spectral_averages']
    assert list(result['windows']) == ['average0', 'average1', 'average2']
    assert result['roles'] == {'penultimate': 'average1', 'final': 'average2'}
    assert [result['windows'][name]['n_spectra'] for name in result['windows']] == [5,
                                                                                    3,
                                                                                    3,
                                                                                    ]
    assert np.allclose(result['windows']['average0']['mean'], [2.0, 0.0])
    assert np.allclose(result['windows']['average1']['mean'], [5.0, 1.0])
    assert np.allclose(result['windows']['average2']['mean'], [9.0, 4.0])


# ---- test_the_ocr_is_put_on_its_percent_of_baseline ----------------------------------
def test_the_ocr_is_put_on_its_percent_of_baseline() -> None:
    """
    ---- Summary ----
    Main function to check the OCR as % of baseline at every time of a run, the
    numbers kept with it, and that a file without a baseline, or with a baseline of
    0, gets none.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant); TIME_COLUMN.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The trace is 10 before 10 min, 4 until 12, 6 until 20, 1 until 22 and 2 after.
    Baseline 7.5 to 9.5: b = 10. y = x / 10 x 100: 100, 40, 60, 10 and 20 %. With
    additions at 0.1 and 20 min the baseline would end before the run starts, so the
    file has none. A trace of 0 before 10 min has b = 0, which nothing can be
    divided by.

    ---- Helpers ----
    _response_experiment_builder
    """

    def averaged(experiment: dict) -> dict:
        return experiment_averages_calculator(experiment,
                                              window_minutes=2.0,
                                              gap_minutes=0.5,
                                              final_window_gap_minutes=0.5,
                                              baseline_minimum_seconds=10.0,
                                              vo2_source='raw',
                                              haem_source=None,
                                              )

    # ---- 1 A file with a baseline ----------------------------------------------------
    experiment = averaged(_response_experiment_builder())
    assert baseline_percent_adder(experiment) is True
    table = experiment['VoO2_baseline']
    times = table[TIME_COLUMN].to_numpy()
    expected = np.select([times < 10, times < 12, times < 20, times < 22],
                         [100.0, 40.0, 60.0, 10.0],
                         20.0,
                         )
    assert table[VO2_COLUMN].to_numpy() == pytest.approx(expected)
    assert list(table.columns) == [TIME_COLUMN, VO2_COLUMN]
    used = table.attrs['baseline_percent']
    assert (used['start_time'], used['end_time']) == pytest.approx((7.5, 9.5))
    assert used['baseline_mean'] == {VO2_COLUMN: pytest.approx(10.0)}
    # the OCR itself is left as it was
    assert experiment['VoO2'][VO2_COLUMN].iloc[0] == pytest.approx(10.0)

    # ---- 2 No averages, or no baseline: no table, and an old one is taken away -------
    experiment = _response_experiment_builder()
    experiment['VoO2_baseline'] = table
    assert baseline_percent_adder(experiment) is False
    assert 'VoO2_baseline' not in experiment
    experiment = _response_experiment_builder()
    experiment['metadata']['events'][0]['time'] = 0.1
    experiment = averaged(experiment)
    assert 'average0' in experiment['averages']['skipped']
    assert baseline_percent_adder(experiment) is False
    assert 'VoO2_baseline' not in experiment

    # ---- 3 A baseline of 0 -----------------------------------------------------------
    experiment = _response_experiment_builder()
    experiment['VoO2'].loc[experiment['VoO2'][TIME_COLUMN] < 10, VO2_COLUMN] = 0.0
    assert baseline_percent_adder(averaged(experiment)) is False


# ---- test_a_file_without_a_baseline_keeps_its_usual_ocr ------------------------------
def test_a_file_without_a_baseline_keeps_its_usual_ocr(capsys: pytest.CaptureFixture,
                                                       ) -> None:
    """
    ---- Summary ----
    Main function to check what the processing of a made-up file gives when the OCR
    is asked for as % of baseline: that view for a file with a baseline, its averages
    still in µM min⁻¹; the usual OCR and one line saying so for a file without one;
    the usual OCR and no line while no windows are set up; and the % of baseline kept
    for the workbook whichever way the OCR is plotted.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        Reads what the processing printed.

    ---- Globals read ----
    VO2_COLUMN (module constant); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The trace of _response_experiment_builder: 10 in the baseline (7.5 to 9.5 min)
    and 6 in the settled window 17.5 to 19.5 min, so 100 and 60 % of baseline.

    ---- Helpers ----
    _response_experiment_builder
    """

    def processed(first_addition_min: float = 10.0, **changed: object) -> dict:
        experiment = _response_experiment_builder()
        experiment['CcO2'] = experiment['VoO2'].copy()
        experiment['metadata']['events'][0]['time'] = first_addition_min
        for number, event in enumerate(experiment['metadata']['events']):
            event['datapoint'] = number
        answers = dict(settings.DEFAULT_ANSWERS,
                       decompose=False,
                       plot_haems=False,
                       normalise_od=False,
                       plot_ocr=True,
                       ocr_mode='baseline',
                       averaging=True,
                       settled_windows=True,
                       quick_windows=False,
                       window_minutes=2.0,
                       gap_minutes=0.5,
                       final_gap_minutes=0.5,
                       )
        answers.update(changed)
        info = {'path': 'made_up.paf',
                'name': 'made_up',
                'ignore_start': 0.0,
                'ignore_end': 0.0,
                }
        capsys.readouterr()
        return experiment_data_processor(info,
                                         settings.Config(answers),
                                         None,
                                         experiment,
                                         )

    # ---- 1 A file with a baseline ----------------------------------------------------
    result = processed()
    assert result['vo2_source'] == 'baseline'
    experiment = result['experiment']
    assert experiment['VoO2_baseline'][VO2_COLUMN].iloc[0] == pytest.approx(100.0)
    assert experiment['averages']['settings']['vo2_key'] == 'VoO2'
    settled = experiment['averages']['windows']['average1']['vo2'][VO2_COLUMN]
    assert (settled['mean'], settled['change']) == pytest.approx((6.0, 60.0))
    assert 'no baseline' not in capsys.readouterr().out

    # ---- 2 A file without one: its usual OCR, and one line ---------------------------
    result = processed(first_addition_min=0.1)
    assert result['vo2_source'] == 'raw'
    assert 'VoO2_baseline' not in result['experiment']
    printed = capsys.readouterr().out
    assert printed.count('This file has no baseline') == 1
    assert 'µM min⁻¹, not as % of baseline' in printed

    # ---- 3 No windows set up: its usual OCR, and nothing said ------------------------
    result = processed(averaging=False)
    assert result['vo2_source'] == 'raw'
    assert 'VoO2_baseline' not in result['experiment']
    assert 'no baseline' not in capsys.readouterr().out

    # ---- 4 Another view on the plot: the % of baseline is still kept -----------------
    result = processed(ocr_mode='raw')
    assert result['vo2_source'] == 'raw'
    assert 'VoO2_baseline' in result['experiment']


# ---- test_the_ocr_turns_per_od -------------------------------------------------------
def test_the_ocr_turns_per_od(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the step once the OD values are in (3.2.2): the OCR is set
    per OD, unless the dataset was saved with it as % of the range (µM min⁻¹, % of
    baseline and none saved all become per OD), and the step waits for Continue with
    its own number. The figures of several files are not offered % of baseline. The
    instruction is stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the stand-ins for the questions in place, and takes them away afterwards.

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

    numbers = []
    def waiter(question: str, nudge: str, **kwargs: object) -> str:
        numbers.append(kwargs.get('number'))
        return ''
    monkeypatch.setattr(survey, 'enter_waiter', waiter)
    monkeypatch.setattr(survey, 'info_printer', lambda *args, **kwargs: None)
    monkeypatch.setattr(survey, 'guide_step_starter', lambda key: None)

    # ---- 1 Per OD, whatever was saved but % of the range -----------------------------
    for saved, shown in (('od', 'od'),
                         ('raw', 'od'),
                         ('baseline', 'od'),
                         (None, 'od'),
                         ('percent', 'percent'),
                         ):
        answers = {}
        seen = []
        def shower() -> None:
            seen.append(answers['ocr_mode'])
        assert survey.ocr_view_teller(answers, {'ocr_mode': saved}, shower) == shown
        assert answers['ocr_mode'] == shown and seen == [shown]
    assert numbers == ['3.2.2'] * 5

    # ---- 2 The figures of several files are not offered % of baseline ----------------
    assert survey.ocr_kind_lister(True) == ['raw', 'od', 'percent']


# ---- test_every_haem_view_and_delta_psi_are_averaged ---------------------------------
def test_every_haem_view_and_delta_psi_are_averaged() -> None:
    """
    ---- Summary ----
    Main function to check that every view of the haems and delta psi are averaged in
    the windows with their difference from the one baseline and no percentage of it,
    that delta psi is averaged over the spectra that have a value and says how many
    that was, and that a view the file does not have is left out.

    ---- Inputs ----
    None.

    ---- Globals read ----
    DELTA_PSI_COLUMN (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Windows of 2 min ending 0.5 min before the next addition: the baseline 7.5 to 9.5,
    then 17.5 to 19.5 and 27.5 to 29.5 min, nine spectra each. bH as ΔD is 0.5, -2.0
    and -3.5 mOD in them: differences 0, -2.0 - 0.5 = -2.5 and -3.5 - 0.5 = -4.0. As
    absorbance 12.5, 10.0 and 8.5: 0, -2.5 and -4.0. As % oxidised 80, 50 and 20: 0,
    -30 and -60. Δψ is 130 mV in the baseline; in the second window it has a value for
    the last five spectra only, 116, 116, 118, 120 and 120: mean 590 / 5 = 118, SD =
    sqrt((4 + 4 + 0 + 4 + 4) / 4) = 2, difference 118 - 130 = -12, 5 of 9 spectra; in
    the third window it has no value: 0 of 9.

    ---- Helpers ----
    _views_experiment_builder
    """

    views = {'delta': 'delta_abs', 'abs': 'abs', 'percent': 'percent'}

    def averages(experiment: dict) -> dict:
        return experiment_averages_calculator(experiment,
                                              window_minutes=2.0,
                                              gap_minutes=0.5,
                                              final_window_gap_minutes=0.5,
                                              baseline_minimum_seconds=10.0,
                                              vo2_source='raw',
                                              haem_source='delta_abs',
                                              haem_views=views,
                                              )['averages']['windows']

    # ---- 1 The three views -----------------------------------------------------------
    windows = averages(_views_experiment_builder())
    expected = {'delta': [(0.5, 0.0), (-2.0, -2.5), (-3.5, -4.0)],
                'abs': [(12.5, 0.0), (10.0, -2.5), (8.5, -4.0)],
                'percent': [(80.0, 0.0), (50.0, -30.0), (20.0, -60.0)],
                }
    for view, levels in expected.items():
        for window, (mean, delta) in zip(windows.values(), levels):
            stats = window['haem_views'][view]['bH']
            assert stats['mean'] == pytest.approx(mean)
            assert stats['delta'] == pytest.approx(delta)
            assert np.isnan(stats['change'])
    # the view on the plot is still where the figures read it
    assert windows['average1']['haem']['bH']['mean'] == pytest.approx(-2.0)

    # ---- 2 Delta psi -----------------------------------------------------------------
    baseline, partly, empty = (window['delta_psi'] for window in windows.values())
    assert baseline['mean'] == pytest.approx(130.0)
    assert (baseline['spectra_used'], baseline['spectra_in_window']) == (9, 9)
    assert partly['mean'] == pytest.approx(118.0)
    assert partly['sd'] == pytest.approx(2.0)
    assert partly['delta'] == pytest.approx(-12.0)
    assert (partly['spectra_used'], partly['spectra_in_window']) == (5, 9)
    assert np.isnan(empty['mean']) and np.isnan(empty['delta'])
    assert (empty['spectra_used'], empty['spectra_in_window']) == (0, 9)

    # ---- 3 A file without both regions, and one without delta psi --------------------
    without = _views_experiment_builder()
    del without['haem_percent'], without['delta_psi']
    windows = averages(without)
    assert list(windows['average1']['haem_views']) == ['delta', 'abs']
    assert 'delta_psi' not in windows['average1']


# ---- test_the_averages_sheet_holds_every_view ----------------------------------------
def test_the_averages_sheet_holds_every_view() -> None:
    """
    ---- Summary ----
    Main function to check the columns of the Averages sheet: the OCR with its
    difference from and its percentage of the baseline, each haem in every view with
    its difference only, delta psi with the spectra it used, the one averaged view
    when the windows hold no views, and the unit that ends every heading.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The experiment of test_every_haem_view_and_delta_psi_are_averaged, whose OCR is 10
    in the baseline and 6 in the second window (17.5 to 19.5 min): difference 6 - 10
    = -4, 6 / 10 x 100 = 60 % of the baseline. bH there: ΔD -2.0 (difference -2.5),
    % oxidised 50 (difference -30), Δψ 118 mV (difference -12, 5 of 9 spectra).
    Per OD, at an OD of 0.5: absorbance 10.0 / 0.5 = 20 mOD per OD.

    ---- Helpers ----
    _views_experiment_builder
    """

    def table(experiment: dict, haem_views: object) -> pd.DataFrame:
        result = experiment_averages_calculator(experiment,
                                                window_minutes=2.0,
                                                gap_minutes=0.5,
                                                final_window_gap_minutes=0.5,
                                                baseline_minimum_seconds=10.0,
                                                vo2_source='raw',
                                                haem_source='delta_abs',
                                                haem_views=haem_views,
                                                )
        return averages_table_builder(result['averages'])

    # ---- 1 Every view ----------------------------------------------------------------
    # the views are written ΔD first, in whatever order they were averaged
    sheet = table(_views_experiment_builder(),
                  {'abs': 'abs', 'delta': 'delta_abs', 'percent': 'percent'},
                  )
    assert list(sheet.columns) == ['Average',
                                   'Kind',
                                   'Start time (min)',
                                   'End time (min)',
                                   'OCR mean (µM min⁻¹)',
                                   'OCR SD (µM min⁻¹)',
                                   'OCR difference from baseline (µM min⁻¹)',
                                   'OCR (% of baseline)',
                                   'bH ΔD mean (mOD)',
                                   'bH ΔD SD (mOD)',
                                   'bH ΔD difference from baseline (mOD)',
                                   'bH absorbance mean (mOD)',
                                   'bH absorbance SD (mOD)',
                                   'bH absorbance difference from baseline (mOD)',
                                   'bH mean (% oxidised)',
                                   'bH SD (% oxidised)',
                                   'bH difference from baseline (% oxidised)',
                                   'Δψ mean (mV)',
                                   'Δψ SD (mV)',
                                   'Δψ difference from baseline (mV)',
                                   'Δψ spectra used',
                                   ]
    assert not any('VoO2' in column or '/' in column for column in sheet.columns)
    row = sheet.iloc[1]
    assert (row['Average'], row['Kind']) == ('average1', 'settled')
    assert row['OCR mean (µM min⁻¹)'] == pytest.approx(6.0)
    assert row['OCR difference from baseline (µM min⁻¹)'] == pytest.approx(-4.0)
    assert row['OCR (% of baseline)'] == pytest.approx(60.0)
    assert row['bH ΔD mean (mOD)'] == pytest.approx(-2.0)
    assert row['bH ΔD difference from baseline (mOD)'] == pytest.approx(-2.5)
    assert row['bH difference from baseline (% oxidised)'] == pytest.approx(-30.0)
    assert row['Δψ difference from baseline (mV)'] == pytest.approx(-12.0)
    assert sheet['Δψ spectra used'].tolist() == ['9 of 9', '5 of 9', '0 of 9']
    assert sheet['OCR (% of baseline)'].iloc[0] == pytest.approx(100.0)

    # ---- 2 Windows without views: the one averaged view, and no delta psi ------------
    plain = _views_experiment_builder()
    del plain['delta_psi']
    sheet = table(plain, None)
    assert list(sheet.columns)[8:] == ['bH mean (mOD)',
                                       'bH SD (mOD)',
                                       'bH difference from baseline (mOD)',
                                       ]
    assert sheet['bH difference from baseline (mOD)'].tolist() == pytest.approx(
        [0.0, -2.5, -4.0],
        )

    # ---- 3 A view shown per OD says so in its unit, as a power of -1 -----------------
    scaled = _views_experiment_builder()
    del scaled['delta_psi']
    scaled['haem_abs_OD'] = scaled['haem_abs'].assign(bH=scaled['haem_abs']['bH'] / 0.5)
    sheet = table(scaled, {'abs': 'abs_od'})
    assert list(sheet.columns)[8:] == ['bH absorbance mean (mOD OD⁻¹)',
                                       'bH absorbance SD (mOD OD⁻¹)',
                                       'bH absorbance difference from baseline '
                                       '(mOD OD⁻¹)',
                                       ]
    assert sheet['bH absorbance mean (mOD OD⁻¹)'].iloc[1] == pytest.approx(20.0)


# ---- test_the_windows_fall_before_the_additions --------------------------------------
def test_the_windows_fall_before_the_additions() -> None:
    """
    ---- Summary ----
    Main function to check where the windows of a file fall and which do not fit: the
    baseline before the first addition, one window before each later addition and one
    before the end of the run.

    ---- Inputs ----
    None.

    ---- Globals read ----
    The module constants.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    2 min and 0.5 min: baseline 10 - 0.5 = 9.5, from 7.5; then 20 - 0.5 = 19.5, from
    17.5; then 30 - 0.5 = 29.5, from 27.5. 12 min: the baseline would start at -2.5,
    so at 0; 19.5 - 12 = 7.5 is before the addition at 10, and 29.5 - 12 = 17.5 is
    before the addition at 20, so neither fits. A first addition at 0.6 min: the
    baseline runs from 0 to 0.1 min, 6 s, less than the 10 s it needs.

    ---- Helpers ----
    None.
    """

    # ---- 1 Windows that fit ----------------------------------------------------------
    assert window_span_lister(ADDITIONS, RECORDING, 2.0, 0.5, FINAL_GAP_MIN) == [
        ('average0', 7.5, 9.5, None),
        ('average1', 17.5, 19.5, None),
        ('average2', 27.5, 29.5, None),
        ]

    # ---- 2 Windows too long to fit ---------------------------------------------------
    assert window_span_lister(ADDITIONS, RECORDING, 12.0, 0.5, FINAL_GAP_MIN) == [
        ('average0', 0.0, 9.5, None),
        ('average1', 7.5, 19.5, 'Insufficient time between additions 1 and 2.'),
        ('average2',
         17.5,
         29.5,
         'Insufficient recording time after the final addition.',
         ),
        ]

    # ---- 3 A baseline too short ------------------------------------------------------
    name, start, end, problem = window_span_lister([0.6, 10.0],
                                                   RECORDING,
                                                   2.0,
                                                   0.5,
                                                   FINAL_GAP_MIN,
                                                   BASELINE_MINIMUM_S,
                                                   )[0]
    assert (name, start) == ('average0', 0.0)
    assert end == pytest.approx(0.1)
    assert problem == 'Less than 10 s of data before the first addition.'
    # a caller that checks the data inside the baseline itself asks for no least length
    assert window_span_lister([0.6, 10.0],
                              RECORDING,
                              2.0,
                              0.5,
                              FINAL_GAP_MIN,
                              )[0][3] is None


# ---- test_each_window_falls_on_its_own -----------------------------------------------
def test_each_window_falls_on_its_own() -> None:
    """
    ---- Summary ----
    Main function to check where the windows set on their own fall: each with its own
    length, gap or start, the others as shared, the last settled window always its set
    time before the end of the run, and a window left out with its tick.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS, RECORDING (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Shared: 2 min long, ending 0.5 min before the next addition; the last ends 1 min
    before the end of the run. The baseline 3 min long: 10 - 0.5 = 9.5, 9.5 - 3 = 6.5.
    average1 ending 1.5 min before the next addition: 20 - 1.5 = 18.5, 18.5 - 2 =
    16.5. average2, the last, 4 min long (its own gap of 5 min is not used): 30 - 1 =
    29, 29 - 4 = 25. Quick, shared 1 min long, starting 0.5 min after the addition:
    quick1 starting 1 min after and 0.5 min long, 10 + 1 = 11 to 11.5; quick2 left out,
    still at 20 + 0.5 = 20.5 to 21.5.

    ---- Helpers ----
    None.
    """

    # ---- 1 The settled windows -------------------------------------------------------
    own = {'average0': {'length_min': 3.0},
           'average1': {'gap_min': 1.5},
           'average2': {'length_min': 4.0, 'gap_min': 5.0},
           }
    assert window_span_lister(ADDITIONS, RECORDING, 2.0, 0.5, 1.0, each_window=own) == [
        ('average0', 6.5, 9.5, None),
        ('average1', 16.5, 18.5, None),
        ('average2', 25.0, 29.0, None),
        ]

    # ---- 2 A settled window left out -------------------------------------------------
    own['average1']['is_used'] = False
    assert window_span_lister(ADDITIONS,
                              RECORDING,
                              2.0,
                              0.5,
                              1.0,
                              each_window=own,
                              )[1] == ('average1', 16.5, 18.5, LEFT_OUT_PROBLEM)
    # the baseline is never left out: every change is measured from it
    assert window_span_lister(ADDITIONS,
                              RECORDING,
                              2.0,
                              0.5,
                              1.0,
                              each_window={'average0': {'is_used': False}},
                              )[0] == ('average0', 7.5, 9.5, None)

    # ---- 3 The quick windows ---------------------------------------------------------
    quick_own = {'quick1': {'delay_min': 1.0, 'length_min': 0.5},
                 'quick2': {'is_used': False},
                 }
    assert quick_span_lister(ADDITIONS, RECORDING, 1.0, 0.5, quick_own) == [
        ('quick1', 11.0, 11.5, None),
        ('quick2', 20.5, 21.5, LEFT_OUT_PROBLEM),
        ]
    # a figure that uses the quick windows reads them under the settled names
    assert kind_span_lister('quick',
                            ADDITIONS,
                            RECORDING,
                            2.0,
                            0.5,
                            1.0,
                            1.0,
                            0.5,
                            quick_own,
                            )[1:] == [('average1', 11.0, 11.5, None),
                                      ('average2', 20.5, 21.5, LEFT_OUT_PROBLEM),
                                      ]

    # ---- 4 A value that cannot be used -----------------------------------------------
    with pytest.raises(ValueError, match='longer than 0 min'):
        window_span_lister(ADDITIONS,
                           RECORDING,
                           2.0,
                           0.5,
                           1.0,
                           each_window={'average1': {'length_min': 0.0}},
                           )
    with pytest.raises(ValueError, match='wrong side'):
        quick_span_lister(ADDITIONS, RECORDING, 1.0, 0.5, {'quick1': {'delay_min': -1}})


# ---- test_a_window_left_out_keeps_its_row --------------------------------------------
def test_a_window_left_out_keeps_its_row() -> None:
    """
    ---- Summary ----
    Main function to check the averages of a file with one window left out and one
    set on its own: the window left out is not averaged and is not warned of, it keeps
    its row in the Averages sheet with its numbers empty, and the one set on its own is
    averaged where it falls.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The experiment of _response_experiment_builder, 2 min windows ending 0.5 min
    before the next addition and the end of the run. Baseline 7.5 to 9.5 min, OCR 10.
    average1 (17.5 to 19.5 min) left out. average2 4 min long: 29.5 - 4 = 25.5 to
    29.5 min, OCR 2: difference 2 - 10 = -8, 2 / 10 x 100 = 20 % of the baseline.

    ---- Helpers ----
    _response_experiment_builder
    """

    # ---- 1 The averages --------------------------------------------------------------
    own = {'average1': {'is_used': False}, 'average2': {'length_min': 4.0}}
    averages = experiment_averages_calculator(_response_experiment_builder(),
                                              window_minutes=2.0,
                                              gap_minutes=0.5,
                                              final_window_gap_minutes=0.5,
                                              baseline_minimum_seconds=10.0,
                                              vo2_source='raw',
                                              haem_source=None,
                                              each_window=own,
                                              )['averages']
    assert list(averages['windows']) == ['average0', 'average2']
    assert averages['skipped']['average1'] == {'start_time': 17.5,
                                               'end_time': 19.5,
                                               'reason': LEFT_OUT_PROBLEM,
                                               'kind': 'settled',
                                               'left_out': True,
                                               }
    last = averages['windows']['average2']
    assert (last['start_time'], last['end_time']) == (25.5, 29.5)
    stats = last['vo2'][VO2_COLUMN]
    assert stats['mean'] == pytest.approx(2.0)
    assert stats['delta'] == pytest.approx(-8.0)
    assert stats['change'] == pytest.approx(20.0)
    assert averages['settings']['each_window'] == own

    # ---- 2 The Averages sheet --------------------------------------------------------
    sheet = averages_table_builder(averages)
    assert list(sheet['Average']) == ['average0', 'average1', 'average2']
    assert list(sheet['Kind']) == ['baseline', 'settled (left out)', 'settled']
    assert np.isnan(sheet['OCR mean (µM min⁻¹)'][1])
    assert sheet['OCR mean (µM min⁻¹)'][2] == pytest.approx(2.0)


# ---- test_each_file_finds_its_own_windows --------------------------------------------
def test_each_file_finds_its_own_windows() -> None:
    """
    ---- Summary ----
    Main function to check the windows each file is given: those of the dataset with
    every window set on its own, or, for a file fixed by hand, its own, taking from the
    dataset any value it does not hold; a dataset saved before windows could be set on
    their own has none.

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

    shared = {'window_minutes': 2.0,
              'gap_minutes': 0.5,
              'final_gap_minutes': 0.5,
              'quick_minutes': 1.0,
              'delay_minutes': 0.25,
              }
    answers = dict(shared,
                   each_window={'average1': {'length_min': 3.0}},
                   file_windows={'fixed': {'window_minutes': 4.0,
                                           'final_gap_minutes': 1.0,
                                           'each_window': {'quick2': {'is_used': False},
                                                           },
                                           },
                                 },
                   )
    assert window_plan_finder(answers, 'run1') == dict(shared,
                                                       each_window={
                                                           'average1': {
                                                               'length_min': 3.0,
                                                               },
                                                           },
                                                       )
    assert window_plan_finder(answers, 'fixed') == dict(shared,
                                                        window_minutes=4.0,
                                                        final_gap_minutes=1.0,
                                                        each_window={
                                                            'quick2': {'is_used': False,
                                                                       },
                                                            },
                                                        )
    # a copy: changing it leaves the answers as they were
    window_plan_finder(answers, 'run1')['each_window']['average1']['length_min'] = 9.0
    assert answers['each_window']['average1']['length_min'] == 3.0
    assert window_plan_finder(shared, 'run1') == dict(shared, each_window={})


# ---- test_the_window_step_holds_the_windows ------------------------------------------
def test_the_window_step_holds_the_windows() -> None:
    """
    ---- Summary ----
    Main function to check that the values the window step starts a file with hold
    its windows, in seconds, each window's own values and ticks under its name, and
    give the same windows back; "Adjust region manually" starts on, with window 1
    picked, only when a window has a length, a gap or a start of its own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PLAN (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    2 min = 120 s, 0.5 min = 30 s, 1 min = 60 s; average1 3 min = 180 s.

    ---- Helpers ----
    None.
    """

    plan = dict(PLAN,
                final_gap_minutes=1.0,
                each_window={'average1': {'length_min': 3.0},
                             'quick2': {'is_used': False},
                             },
                )
    values = window_values_maker(plan, True, False)
    assert values == {'window_s': 120.0,
                      'gap_s': 30.0,
                      'is_on': 1.0,
                      'quick_s': 60.0,
                      'delay_s': 30.0,
                      'quick_is_on': 0.0,
                      'final_gap_s': 60.0,
                      'each_is_on': 1.0,
                      'settled_picked': 1.0,
                      'quick_picked': -1.0,
                      'average1:window_s': 180.0,
                      'quick2:is_used': 0.0,
                      }
    assert window_plan_reader(values) == plan
    # a tick alone leaves Adjust each window off; a window ticked again is not kept
    only_tick = dict(plan, each_window={'quick2': {'is_used': False}})
    assert window_values_maker(only_tick, True, True)['each_is_on'] == 0.0
    ticked = window_plan_reader(dict(values, **{'quick2:is_used': 1.0}))
    assert ticked['each_window'] == {'average1': {'length_min': 3.0}}


# ---- test_a_change_moves_one_window_or_every_window ----------------------------------
def test_a_change_moves_one_window_or_every_window() -> None:
    """
    ---- Summary ----
    Main function to check what a drag, a typed number and a tick change in the window
    step: with Adjust each window off every window of the kind; with it on only the
    window dragged, which the boxes then show and a typed number then changes; its
    own values kept when it is switched off, until the next change of that field
    puts every window back to one value; a tick per window, never the baseline's; the
    end of the last window; and values that cannot be used.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PLAN (module constant).

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

    # ---- 1 Every window of the kind --------------------------------------------------
    step = window_values_maker(PLAN, True, True)
    assert window_value_setter(step, 'window_s@average2', 90.0) == dict(step,
                                                                        window_s=90.0,
                                                                        )

    # ---- 2 Only the window dragged, then typed in ------------------------------------
    on = window_value_setter(step, 'each_is_on', 1.0)
    dragged = window_value_setter(on, 'window_s@average2', 90.0)
    assert dragged == dict(on, **{'average2:window_s': 90.0, 'settled_picked': 2.0})
    typed = window_value_setter(dragged, 'gap_s', 45.0)
    assert typed == dict(dragged, **{'average2:gap_s': 45.0})
    assert window_shown_maker(typed) == {'window_s': 90.0, 'gap_s': 45.0}
    # no quick window was dragged, so a typed quick value is every quick window's
    assert window_value_setter(typed, 'quick_s', 30.0) == dict(typed, quick_s=30.0)
    assert window_value_setter(on, 'window_s@average2', 0.0) == on

    # ---- 3 Switched off: kept until the next change of the field ---------------------
    kept = window_value_setter(typed, 'each_is_on', 0.0)
    assert kept['average2:window_s'] == 90.0
    assert window_shown_maker(kept) == {}
    back = window_value_setter(kept, 'window_s@average1', 100.0)
    expected = {key: value for key, value in kept.items() if key != 'average2:window_s'}
    assert back == dict(expected, window_s=100.0)
    assert back['average2:gap_s'] == 45.0  # another field keeps its own

    # ---- 4 The ticks and the end of the last window ----------------------------------
    assert window_value_setter(step, 'average1:is_used', 0.0) == dict(
        step,
        **{
            'average1:is_used': 0.0,
            },
        )
    assert window_value_setter(step, 'average0:is_used', 0.0) == step
    assert window_value_setter(step, 'final_gap_s', 60.0) == dict(step,
                                                                  final_gap_s=60.0,
                                                                  )
    assert window_value_setter(step, 'final_gap_s', -1.0) == step


# ---- test_a_pulled_window_on_its_own -------------------------------------------------
def test_a_pulled_window_on_its_own() -> None:
    """
    ---- Summary ----
    Main function to check that an edge of a named window pulled to a time gives the
    value of that window, with its own values, in whole steps of 5 s, and that the
    end of the last settled window gives how long before the end of the run it ends.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS, RECORDING, FINAL_GAP_MIN, STEP_S, PLAN (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    average1 ends at 20 - 0.5 = 19.5: its start pulled to 17 gives (19.5 - 17) x 60 =
    150 s; its end pulled to 19 gives (20 - 19) x 60 = 60 s. The baseline's end
    pulled to 9 gives (10 - 9) x 60 = 60 s. average2, 3 min of its own, ends at
    30 - 0.5 = 29.5: its start pulled to 26 gives 210 s. The last end pulled to 29
    gives (30 - 29) x 60 = 60 s, to 30.4 below 0, so 0 s. quick2 starts after 20:
    pulled to 21, 60 s. quick1 starts 1 min after its addition of its own, at 11: its
    end pulled to 12 gives 60 s.

    ---- Helpers ----
    None.
    """

    values = dict(window_values_maker(PLAN, True, True),
                  **{'average2:window_s': 180.0, 'quick1:delay_s': 60.0},
                  )
    def pulled(key: str, time_min: float) -> float:
        return window_pointer_reader(values,
                                     key,
                                     time_min,
                                     ADDITIONS,
                                     RECORDING,
                                     FINAL_GAP_MIN,
                                     STEP_S,
                                     )
    assert pulled('window_s@average1', 17.0) == pytest.approx(150.0)
    assert pulled('gap_s@average1', 19.0) == pytest.approx(60.0)
    assert pulled('gap_s@average0', 9.0) == pytest.approx(60.0)
    assert pulled('window_s@average2', 26.0) == pytest.approx(210.0)
    assert pulled('final_gap_s', 29.0) == pytest.approx(60.0)
    assert pulled('final_gap_s', 30.4) == pytest.approx(0.0)
    assert pulled('delay_s@quick2', 21.0) == pytest.approx(60.0)
    assert pulled('quick_s@quick1', 12.0) == pytest.approx(60.0)
    # the last settled window has no gap of its own to pull
    assert pulled('gap_s@average2', 25.0) == 30.0


# ---- test_the_plot_shows_windows_on_their_own ----------------------------------------
def test_the_plot_shows_windows_on_their_own() -> None:
    """
    ---- Summary ----
    Main function to check what the window step draws with windows set on their own:
    each where its own values put it, with its own length in the words, the windows
    left out grey and without edges, and the numbered ticks and the note of each row.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS, RECORDING, FINAL_GAP_MIN, BASELINE_MINIMUM_S, PLAN (module constants);
    PART_STYLES of the window.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The baseline 7.5 to 9.5. average1 1 min of its own: 19.5 - 1 = 18.5 to 19.5.
    average2 left out, ending 1 min before the end of the run: 29 - 2 = 27 to 29.
    quick1 left out, 10.5 to 11.5; quick2 20.5 to 21.5.

    ---- Helpers ----
    None.
    """

    plan = dict(PLAN,
                final_gap_minutes=1.0,
                each_window={'average1': {'length_min': 1.0},
                             'average2': {'is_used': False},
                             'quick1': {'is_used': False},
                             },
                )
    # with "Adjust region manually" off, every window has its edges
    values = dict(window_values_maker(plan, True, True), each_is_on=0.0)
    edges, parts = window_layout_finder(values,
                                        ADDITIONS,
                                        RECORDING,
                                        FINAL_GAP_MIN,
                                        BASELINE_MINIMUM_S,
                                        )
    assert edges == [('window_s@average0', 7.5, 'baseline 120 s', 'baseline'),
                     ('gap_s@average0', 9.5, '', 'baseline_end'),
                     ('window_s@average1', 18.5, 'region 60 s', 'average'),
                     ('gap_s@average1',
                      19.5,
                      'ends 30 s before the addition',
                      'average_end',
                      ),
                     ('delay_s@quick2',
                      20.5,
                      'starts 30 s after the addition',
                      'quick',
                      ),
                     ('quick_s@quick2', 21.5, 'quick region 60 s', 'quick_end'),
                     ]
    assert parts == [(7.5, 9.5, 'baseline'),
                     (18.5, 19.5, 'average'),
                     (27.0, 29.0, 'left_out'),
                     (10.5, 11.5, 'left_out'),
                     (20.5, 21.5, 'quick'),
                     ]
    assert 'left_out' in PART_STYLES

    # ---- The ticks of each row: the quick windows are hidden for now -----------------
    assert window_row_teller(values, 2) == [('',
                                             [('average1:is_used', '1', True),
                                              ('average2:is_used', '2', False),
                                              ],
                                             ),
                                            ('', []),
                                            ]
    assert window_row_teller(dict(values, is_on=0.0), 2)[0] == ('', [])


# ---- test_one_window_is_adjusted_by_hand ---------------------------------------------
def test_one_window_is_adjusted_by_hand() -> None:
    """
    ---- Summary ----
    Main function to check "Adjust region manually": ticking it picks window 1; the
    buttons beside it (Baseline 1 2) with the one picked; only the window picked has
    edges on the plot, the others grey; a click picks another; a typed number changes
    only that window; with the last window picked the time before the next addition is
    the time before the end of the file, shown and typed; nothing with it off.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS, RECORDING, FINAL_GAP_MIN, BASELINE_MINIMUM_S, PLAN (module constants);
    PART_STYLES of the window.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Additions at 10 and 20, the run 0 to 30, windows 2 min ending 0.5 min before the
    next addition: the baseline 7.5 to 9.5, window 1 17.5 to 19.5, window 2 (the last)
    ending 0.5 min before the end of the run, 27.5 to 29.5. With window 2 picked and
    60 s typed for its time before the end: 30 - 1 = 29, so 27 to 29.

    ---- Helpers ----
    None.
    """

    # ---- 1 Ticking it picks window 1 -------------------------------------------------
    step = window_values_maker(PLAN, True, False)
    assert window_pick_lister(step, 2) == ([], '')
    on = window_value_setter(step, 'each_is_on', 1.0, 2)
    assert on['settled_picked'] == 1.0
    assert window_pick_lister(on, 2) == ([('settled_picked', 0.0, 'Baseline', False),
                                          ('settled_picked', 1.0, '1', True),
                                          ('settled_picked', 2.0, '2', False),
                                          ],
                                         '',
                                         )

    # ---- layout ----------------------------------------------------------------------
    def layout(values: dict) -> tuple:
        return window_layout_finder(values,
                                    ADDITIONS,
                                    RECORDING,
                                    FINAL_GAP_MIN,
                                    BASELINE_MINIMUM_S,
                                    )
    edges, parts = layout(on)
    assert edges == [('window_s@average1', 17.5, 'region 120 s', 'average'),
                     ('gap_s@average1',
                      19.5,
                      'ends 30 s before the addition',
                      'average_end',
                      ),
                     ]
    assert parts == [(7.5, 9.5, 'not_picked'),
                     (17.5, 19.5, 'average'),
                     (27.5, 29.5, 'not_picked'),
                     ]
    assert 'not_picked' in PART_STYLES

    # ---- 3 A click picks another; a typed number changes only it ---------------------
    baseline = window_value_setter(on, 'settled_picked', 0.0, 2)
    assert [key for key, _, _, _ in layout(baseline)[0]] == ['window_s@average0',
                                                             'gap_s@average0',
                                                             ]
    typed = window_value_setter(baseline, 'window_s', 90.0, 2)
    assert typed == dict(baseline, **{'average0:window_s': 90.0})

    # ---- 4 The last window ends before the end of the file ---------------------------
    last = window_value_setter(on, 'settled_picked', 2.0, 2)
    assert window_pick_lister(last, 2)[1] == ('the last region: its time is before '
                                              'the end of the file')
    assert window_shown_maker(last, 2) == {'window_s': 120.0, 'gap_s': 30.0}
    ended = window_value_setter(last, 'gap_s', 60.0, 2)
    assert ended == dict(last, final_gap_s=60.0)
    assert layout(ended)[1][2] == (27.0, 29.0, 'average')

    # ---- 5 Off: every window has its edges again -------------------------------------
    off = window_value_setter(ended, 'each_is_on', 0.0, 2)
    assert window_pick_lister(off, 2) == ([], '')
    assert len(layout(off)[0]) == 6


# ---- test_the_window_step_keeps_each_file --------------------------------------------
def test_the_window_step_keeps_each_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check what the window step keeps: the windows most files share
    as the dataset's, with their windows set on their own and how long before the end
    of the file the last ends, a file whose windows differ as fixed by hand, and a
    warning naming only the windows that do not fit, not those left out.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the printing of the step.

    ---- Globals read ----
    ADDITIONS, RECORDING, PLAN (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    File c, 1.5 min windows: average2 from 29 - 1.5 = 27.5 to 29, after its addition
    at 20, so it fits. With 12 min windows: average1 (left out) would start at 7.5;
    average2 starts at 29 - 12 = 17, before its addition at 20, so it does not fit;
    the baseline is cut at the start of the run and fits.

    ---- Helpers ----
    None.
    """

    # ---- 1 Two files share, one is fixed by hand -------------------------------------
    printed, warned = [], []
    monkeypatch.setattr(viewer_stages,
                        'info_printer',
                        lambda text, **kwargs: printed.append(text),
                        )
    monkeypatch.setattr(viewer_stages,
                        'warning_shower',
                        lambda text, **kwargs: warned.append(text),
                        )
    plan = dict(PLAN,
                final_gap_minutes=1.0,
                each_window={'average1': {'is_used': False}},
                )
    base = window_values_maker(plan, True, False)
    session = SimpleNamespace(summaries=[{'name': name} for name in 'abc'])
    context = {'additions': {name: ADDITIONS for name in 'abc'},
               'spans': {name: RECORDING for name in 'abc'},
               'final_gap': 0.5,
               'minimum_s': 10.0,
               }
    answers: dict = {}
    _windows_keeper(session,
                    answers,
                    {'a': base, 'b': dict(base), 'c': dict(base, window_s=90.0)},
                    context,
                    )
    assert answers['averaging'] and answers['settled_windows']
    assert not answers['quick_windows']
    assert {key: answers[key] for key in plan} == plan
    assert answers['file_windows'] == {'c': dict(plan, window_minutes=1.5)}
    assert 'Left out: settled region 1.' in printed
    assert any('c' in text and 'Apply to all' in text for text in printed)
    assert warned == []

    # ---- 2 A window that does not fit is named, one left out is not ------------------
    _windows_keeper(session,
                    answers,
                    {'a': base, 'b': dict(base), 'c': dict(base, window_s=720.0)},
                    context,
                    )
    assert len(warned) == 1
    assert 'c: the settled one after the last addition.' in warned[0]
    assert 'before addition 2' not in warned[0]
