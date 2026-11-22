"""
Tests that the averaging windows of both kinds (settled, ending before the next
addition, and quick, starting after each addition) fall, and follow a pulled edge, as
worked out by hand, that a figure needing them offers the window step when none are set
up, and that it asks which kind it uses only when both are.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.spectral_difference import spectral_averager
from utils_shared import survey
from utils_shared.averaging import (experiment_averages_calculator,
                                    kind_span_lister,
                                    quick_span_lister,
                                    window_kind_picker,
                                    window_layout_finder,
                                    window_pointer_reader,
                                    window_span_lister,
                                    window_value_setter,
                                    )
from utils_shared.schema import TIME_COLUMN
from utils_viewer.viewer_edges import every_file_setter, PART_STYLES
from utils_viewer.viewer_stages import _unfit_windows_lister


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
    assert asked == [('Which windows should this figure use?',
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
    Main function to check what the window step draws for a file: the start of every
    window and the end of all but the last as edges, the first of each kind with its
    words, the windows as blue parts and those that do not fit as red ones, and
    nothing when the windows are unticked or the file has no additions.

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
    assert edges == [('window_s', 7.5, 'window 120 s', 'average'),
                     ('gap_s', 9.5, 'ends 30 s before the addition', 'average_end'),
                     ('window_s', 17.5, '', 'average'),
                     ('gap_s', 19.5, '', 'average_end'),
                     ('window_s', 27.5, '', 'average'),
                     ]
    assert parts == [(7.5, 9.5, 'average'),
                     (17.5, 19.5, 'average'),
                     (27.5, 29.5, 'average'),
                     ]

    # ---- 2 Windows too long to fit ---------------------------------------------------
    _, parts = layout(dict(VALUES, window_s=720.0))
    assert parts == [(0.0, 9.5, 'average'),
                     (7.5, 19.5, 'average_unfit'),
                     (17.5, 29.5, 'average_unfit'),
                     ]

    # ---- 3 No windows ----------------------------------------------------------------
    assert layout(dict(VALUES, is_on=0.0)) == ([], [])
    assert layout(VALUES, []) == ([], [])
    assert layout(BOTH, []) == ([], [])

    # ---- 4 Both kinds: the quick windows after the settled ones ----------------------
    quick_edges = [('delay_s', 10.5, 'starts 30 s after the addition', 'quick'),
                   ('quick_s', 11.5, 'quick window 60 s', 'quick_end'),
                   ('delay_s', 20.5, '', 'quick'),
                   ('quick_s', 21.5, '', 'quick_end'),
                   ]
    quick_parts = [(10.5, 11.5, 'quick'), (20.5, 21.5, 'quick')]
    assert layout(BOTH) == (edges + quick_edges,
                            [(7.5, 9.5, 'average'),
                             (17.5, 19.5, 'average'),
                             (27.5, 29.5, 'average'),
                             ]
                            + quick_parts,
                            )

    # ---- 5 Quick windows alone: the baseline stays, with both its edges --------------
    assert layout(dict(BOTH, is_on=0.0)) == (
        [('window_s', 7.5, 'window 120 s', 'average'),
         ('gap_s', 9.5, 'ends 30 s before the addition', 'average_end'),
         ]
        + quick_edges,
        [(7.5, 9.5, 'average')] + quick_parts,
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
