"""
Tests that the averaging windows fall, and follow a pulled edge, as worked out by hand,
and that a figure needing them offers the window step when none are set up.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared import survey
from utils_shared.averaging import (window_layout_finder,
                                    window_pointer_reader,
                                    window_span_lister,
                                    window_value_setter,
                                    )
from utils_viewer.viewer_edges import every_file_setter, PART_STYLES


# ---- CONSTANTS -----------------------------------------------------------------------
# A made-up run of 30 min with additions at 10 and 20 min. The windows are 120 s long
# and end 30 s before the next addition; the last ends 0.5 min before the end of the
# run; the baseline needs 10 s; an edge moves in steps of 5 s.
ADDITIONS = [10.0, 20.0]
RECORDING = (0.0, 30.0)
FINAL_GAP_MIN = 0.5
BASELINE_MINIMUM_S = 10.0
STEP_S = 5.0
VALUES = {'window_s': 120.0, 'gap_s': 30.0, 'is_on': 1.0}


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


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
    assert VALUES == {'window_s': 120.0, 'gap_s': 30.0, 'is_on': 1.0}  # not changed

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

    # ---- 4 The window knows how to draw every kind -----------------------------------
    assert {'average', 'average_end', 'average_unfit'} <= set(PART_STYLES)
    assert PART_STYLES['average'][3] != PART_STYLES['average_end'][3]  # two rows


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
