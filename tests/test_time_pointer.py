"""
Tests that the mouse over a preview gives the times and answers worked out by hand,
that the time axis of a figure is found, and that a question the mouse can answer
tells the window.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared import questions
from utils_shared.survey import averaging_drag_reader
from utils_viewer.viewer_gui import pointed_time_finder
from utils_viewer.viewer_preview import time_axis_finder, TimeAxis


# ---- CONSTANTS -----------------------------------------------------------------------
# A picture 800 x 400 pixels placed at (100, 50) in the plot area. Its panels run from
# 1/8 to 7/8 of its width (pixels 200 to 800 of the plot area) and from 1/4 to 3/4 of
# its height (pixels 150 to 350), and show 0 to 60 min.
PICTURE_BOX = (100.0, 50.0, 800.0, 400.0)
TIME_AXIS = TimeAxis(left=0.125,
                     right=0.875,
                     bottom=0.25,
                     top=0.75,
                     start_min=0.0,
                     end_min=60.0,
                     )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_drag_gives_the_window_and_gap ----------------------------------------------
def test_drag_gives_the_window_and_gap() -> None:
    """
    ---- Summary ----
    Main function to check that a drag across one averaging window gives its length
    and how long before the next addition it ends, in seconds rounded to whole 5 s,
    worked out by hand for additions at 10 and 20 min.

    ---- Inputs ----
    None.

    ---- Globals read ----
    config.DRAG_STEP_SECONDS (5 s, checked first).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    18.5 to 19 min: 30 s long, 60 s before the addition at 20. 9 to 9.82 min: 49.2 s
    -> 50 s, and 10.8 s before the addition at 10 -> 10 s. 25 to 25.4 min, after the
    last addition: 24 s -> 25 s, no gap. 5 to 5.01 min: 0.6 s -> one step (5 s), and
    299.4 s -> 300 s before the addition at 10.

    ---- Helpers ----
    None.
    """

    assert settings.DRAG_STEP_SECONDS == 5
    additions = [10.0, 20.0]
    assert averaging_drag_reader(additions, 18.5, 19.0) == pytest.approx((30.0, 60.0))
    assert averaging_drag_reader(additions, 9.0, 9.82) == pytest.approx((50.0, 10.0))
    length_s, gap_s = averaging_drag_reader(additions, 25.0, 25.4)
    assert length_s == pytest.approx(25.0)
    assert gap_s is None
    assert averaging_drag_reader(additions, 5.0, 5.01) == pytest.approx((5.0, 300.0))


# ---- test_pointed_time_inside_the_panels ---------------------------------------------
def test_pointed_time_inside_the_panels() -> None:
    """
    ---- Summary ----
    Main function to check the time under the mouse in the middle and at both ends of
    the time axis, for an axis that starts at zero and one that does not.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PICTURE_BOX, TIME_AXIS (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    x = 500 is half way along the axis (200 to 800): 30 min. With an axis from 10 to
    50 min, x = 350 is a quarter of the way: 10 + 0.25 * 40 = 20 min.

    ---- Helpers ----
    None.
    """

    assert pointed_time_finder(500, 250, PICTURE_BOX, TIME_AXIS) == pytest.approx(30.0)
    assert pointed_time_finder(200, 250, PICTURE_BOX, TIME_AXIS) == pytest.approx(0.0)
    assert pointed_time_finder(800, 250, PICTURE_BOX, TIME_AXIS) == pytest.approx(60.0)
    later = TimeAxis(left=0.125,
                     right=0.875,
                     bottom=0.25,
                     top=0.75,
                     start_min=10.0,
                     end_min=50.0,
                     )
    assert pointed_time_finder(350, 160, PICTURE_BOX, later) == pytest.approx(20.0)


# ---- test_pointed_time_off_the_panels ------------------------------------------------
def test_pointed_time_off_the_panels() -> None:
    """
    ---- Summary ----
    Main function to check that no time is given left or right of the time axis, above
    or below the panels, or for a picture with no size.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PICTURE_BOX, TIME_AXIS (module constants).

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

    assert pointed_time_finder(180, 250, PICTURE_BOX, TIME_AXIS) is None
    assert pointed_time_finder(820, 250, PICTURE_BOX, TIME_AXIS) is None
    assert pointed_time_finder(500, 140, PICTURE_BOX, TIME_AXIS) is None
    assert pointed_time_finder(500, 360, PICTURE_BOX, TIME_AXIS) is None
    assert pointed_time_finder(500, 250, (100.0, 50.0, 0.0, 0.0), TIME_AXIS) is None


# ---- test_pointed_time_on_a_scaled_picture -------------------------------------------
def test_pointed_time_on_a_scaled_picture() -> None:
    """
    ---- Summary ----
    Main function to check that the time follows the picture when it is shown at
    another size and place.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_AXIS (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A picture 1600 x 800 at (0, 0): the axis runs from x = 200 to 1400, so x = 500 is
    a quarter of the way: 15 min.

    ---- Helpers ----
    None.
    """

    box = (0.0, 0.0, 1600.0, 800.0)
    assert pointed_time_finder(500, 400, box, TIME_AXIS) == pytest.approx(15.0)


# ---- test_question_wanting_a_time_tells_the_window -----------------------------------
def test_question_wanting_a_time_tells_the_window(monkeypatch: pytest.MonkeyPatch,
                                                  ) -> None:
    """
    ---- Summary ----
    Main function to check that a number question the mouse can answer hands its rule
    to the registered window before it reads (a drag rule as 'span') and takes it back
    once it has a valid answer, that other number questions leave the window alone,
    and that a question still works when no window is registered (the window has
    closed).

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answer and restores the module state afterwards.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The registered function of the questions is restored by monkeypatch.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Answers typed: one that is not a number, then numbers ---------------------
    typed = ['abc', '4,5', '7', '3']
    monkeypatch.setattr(questions, '_input_reader', lambda text, indent='': typed.pop(0))
    monkeypatch.setattr(questions, '_time_requester', None)
    calls: List[tuple] = []
    questions.time_request_setter(lambda kind, reader: calls.append((kind, reader)))
    def drag(name: str, start_min: float, end_min: float) -> float:
        return end_min - start_min

    # ---- 2 A question a drag answers -------------------------------------------------
    assert questions.number_asker('How long?', span_reader=drag) == pytest.approx(4.5)
    assert calls == [('span', drag), (None, None)]

    # ---- 3 A question the mouse cannot answer ----------------------------------------
    assert questions.number_asker('How many?') == pytest.approx(7.0)
    assert len(calls) == 2

    # ---- 4 No window registered ------------------------------------------------------
    questions.time_request_setter(None)
    assert questions.number_asker('How long?', span_reader=drag) == pytest.approx(3.0)
    assert len(calls) == 2


# ---- test_time_axis_of_a_figure ------------------------------------------------------
def test_time_axis_of_a_figure() -> None:
    """
    ---- Summary ----
    Main function to check that the time axis of a figure is found from the panels
    that share the x axis of the first one, and that a figure with no panel has none.

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
    Two panels from 0.2 to 0.9 of the width, the lower from 0.1 and the upper to 0.9
    of the height, showing 0 to 45 min; a small panel with its own x axis is left out.

    ---- Helpers ----
    None.
    """

    fig = Figure(figsize=(4.0, 3.0))
    upper = fig.add_axes([0.2, 0.55, 0.7, 0.35])
    fig.add_axes([0.2, 0.1, 0.7, 0.35], sharex=upper)
    fig.add_axes([0.0, 0.0, 0.05, 0.05])
    upper.set_xlim(0.0, 45.0)
    found = time_axis_finder(fig)
    assert found is not None
    assert (found.left, found.right) == pytest.approx((0.2, 0.9))
    assert (found.bottom, found.top) == pytest.approx((0.1, 0.9))
    assert (found.start_min, found.end_min) == pytest.approx((0.0, 45.0))
    assert time_axis_finder(Figure()) is None
