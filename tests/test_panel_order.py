"""
Tests of the order of the panels of the standard plot, worked out by hand: a panel
moved one place, the order of one file kept in the order of the dataset, the place of
a panel new to the order, the plot drawn in the order given, where the arrows sit
beside the panels, what a click on one changes and the order saved with the dataset.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_stages as viewer_stages
from utils_shared.dataset_settings import (dataset_settings_reader,
                                           dataset_settings_saver,
                                           )
from utils_shared.helpers import (panel_name_teller,
                                  panel_order_merger,
                                  panel_order_mover,
                                  panel_order_placer,
                                  )
from utils_shared.individual_experiment_plotter import experiment_drawer
from utils_shared.schema import TIME_COLUMN
from utils_viewer.viewer_gui import panel_arrow_finder, panel_arrow_placer
from utils_viewer.viewer_preview import time_axis_finder, TimeAxis, ViewerSession
from utils_viewer.viewer_strip import PANEL_ORDER_CHANGE


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _figure_drawer ------------------------------------------------------------------
def _figure_drawer(haems: list, panel_order: list) -> Figure:
    """
    ---- Summary ----
    Helper function to draw the standard plot of a made-up file with oxygen, OCR and
    the haems Cyt a605, Cyt bH and Cyt cc, of which ``haems`` are shown.

    ---- Inputs ----
    haems : list
        Names of the haems the plot shows.
    panel_order : list
        Keys of the panels in the order the user gave them; empty for the standard.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS; TIME_COLUMN.

    ---- Outputs ----
    Figure
        The drawn figure.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_drawer
    """

    times = np.arange(0.0, 31.0)
    table = pd.DataFrame({TIME_COLUMN: times})
    for value, name in enumerate(('Cyt cc', 'Cyt bH', 'Cyt a605')):
        table[name] = float(value)
    experiment = {'experiment_name': 'made_up',
                  'CsO2': pd.DataFrame({TIME_COLUMN: times, 'Set O2': 60.0}),
                  'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 50.0}),
                  'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': 1.0}),
                  'haem_delta_abs': table,
                  'metadata': {'events': []},
                  }
    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   plot_haems=True,
                   haems=list(haems),
                   panel_order=list(panel_order),
                   )
    config = settings.Config(answers).plot_config_builder('raw', 'delta_abs', 0.0, 0.0)
    fig = Figure()
    experiment_drawer(fig, fig.add_gridspec(1, 1)[0, 0], experiment, config)
    return fig


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_click_on_an_arrow_changes_the_order_kept_and_redraws ---------------------
def test_a_click_on_an_arrow_changes_the_order_kept_and_redraws(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    ) -> None:
    """
    ---- Summary ----
    Main function to check what the program does with a panel moved in the window: the
    new order of the panels of the file shown is kept in the order of the dataset,
    said in one line and the plot drawn again; the Standard order button empties the
    order kept. The showing of the strip is stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the showing of the strip.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS; PANEL_ORDER_CHANGE.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. The stand-in is undone after the test.

    ---- Equations ----
    Kept [oxygen, vo2, delta_psi, haem:Cyt bH]; the file shown has no Δψ, and its
    panels after the move are [haem:Cyt bH, oxygen, vo2]. They take the places 1, 2
    and 4 of the kept order: [haem:Cyt bH, oxygen, delta_psi, vo2].

    ---- Helpers ----
    None.
    """

    # ---- 1 A session whose plot can be drawn again -----------------------------------
    monkeypatch.setattr(viewer_stages, '_strip_shower', lambda session, answers: None)
    redraws = []
    session = ViewerSession(summaries=[], export_root=Path('.'), window=None)
    session.redraw = lambda: redraws.append(True) or True
    answers = dict(settings.DEFAULT_ANSWERS,
                   panel_order=['oxygen', 'vo2', 'delta_psi', 'haem:Cyt bH'],
                   )

    # ---- 2 A panel moved -------------------------------------------------------------
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {PANEL_ORDER_CHANGE: ['haem:Cyt bH',
                                                              'oxygen',
                                                              'vo2',
                                                              ],
                                         },
                                        )
    assert answers['panel_order'] == ['haem:Cyt bH', 'oxygen', 'delta_psi', 'vo2']
    assert redraws == [True]
    assert ('The panels are now, from the top: Cyt bH, Oxygen, OCR.'
            in capsys.readouterr().out
            )

    # ---- 3 The Standard order button -------------------------------------------------
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {PANEL_ORDER_CHANGE: []},
                                        )
    assert answers['panel_order'] == []
    assert redraws == [True, True]
    assert 'The panels are back in the standard order.' in capsys.readouterr().out
    assert settings.DEFAULT_ANSWERS['panel_order'] == []


# ---- test_a_move_on_one_file_keeps_the_place_of_a_panel_it_does_not_have -------------
def test_a_move_on_one_file_keeps_the_place_of_a_panel_it_does_not_have() -> None:
    """
    ---- Summary ----
    Main function to check how the order of the panels of one file is kept in the
    order of the dataset: the panels on the plot take the places they had, in their
    new order, a panel the file does not have stays where it was, and a panel new to
    the kept order is added to it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Kept [oxygen, vo2, delta_psi, haem:a] and shown [haem:a, oxygen, vo2]: places 1,
    2 and 4 are filled in that order, [haem:a, oxygen, delta_psi, vo2]. Nothing kept
    and shown [vo2, oxygen]: [vo2, oxygen]. Kept [vo2, oxygen] and shown [oxygen,
    haem:a, vo2]: haem:a is added at the end, then places 1, 2 and 3 are filled,
    [oxygen, haem:a, vo2].

    ---- Helpers ----
    panel_order_merger
    """

    assert panel_order_merger(['oxygen', 'vo2', 'delta_psi', 'haem:a'],
                              ['haem:a', 'oxygen', 'vo2'],
                              ) == ['haem:a', 'oxygen', 'delta_psi', 'vo2']
    assert panel_order_merger([], ['vo2', 'oxygen']) == ['vo2', 'oxygen']
    assert panel_order_merger(['vo2', 'oxygen'],
                              ['oxygen', 'haem:a', 'vo2'],
                              ) == ['oxygen', 'haem:a', 'vo2']


# ---- test_a_panel_moves_one_place_and_stops_at_the_ends ------------------------------
def test_a_panel_moves_one_place_and_stops_at_the_ends() -> None:
    """
    ---- Summary ----
    Main function to check a panel moved with its arrows: it swaps with the panel
    above or under it, the top panel does not go up nor the bottom one down, and the
    order given is left as it was.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    [oxygen, vo2, haem:a]: vo2 up gives [vo2, oxygen, haem:a]; vo2 down gives
    [oxygen, haem:a, vo2].

    ---- Helpers ----
    panel_name_teller
    panel_order_mover
    """

    shown = ['oxygen', 'vo2', 'haem:a']
    assert panel_order_mover(shown, 'vo2', -1) == ['vo2', 'oxygen', 'haem:a']
    assert panel_order_mover(shown, 'vo2', 1) == ['oxygen', 'haem:a', 'vo2']
    assert panel_order_mover(shown, 'oxygen', -1) is None
    assert panel_order_mover(shown, 'haem:a', 1) is None
    assert panel_order_mover(shown, 'delta_psi', 1) is None
    assert shown == ['oxygen', 'vo2', 'haem:a']
    names = [panel_name_teller(key) for key in ('oxygen', 'vo2', 'delta_psi', 'haem:a')]
    assert names == ['Oxygen', 'OCR', 'Δψ', 'a']


# ---- test_a_panel_new_to_the_order_takes_its_standard_place --------------------------
def test_a_panel_new_to_the_order_takes_its_standard_place() -> None:
    """
    ---- Summary ----
    Main function to check where the panels are drawn: in the order given, a panel
    the order does not know just above the panel that follows it in the standard
    order (at the bottom when none does), and a key of the order that is not on the
    plot passed over. With no order, the standard one.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Standard [oxygen, vo2, haem:a, haem:b, delta_psi], places 0 to 4. Order [vo2,
    oxygen, haem:b]: delta_psi, which nothing follows, goes to the bottom and haem:a
    just above haem:b, so [vo2, oxygen, haem:a, haem:b, delta_psi] = places 1, 0, 2,
    3, 4. Order [haem:b, haem:c, oxygen]: haem:c is not on the plot; delta_psi goes
    to the bottom, haem:a just above haem:b, vo2 just above haem:a, so [vo2, haem:a,
    haem:b, oxygen, delta_psi] = places 1, 2, 3, 0, 4.

    ---- Helpers ----
    panel_order_placer
    """

    standard = ['oxygen', 'vo2', 'haem:a', 'haem:b', 'delta_psi']
    assert panel_order_placer(standard, []) == [0, 1, 2, 3, 4]
    assert panel_order_placer(standard, ['vo2', 'oxygen', 'haem:b']) == [1, 0, 2, 3, 4]
    assert panel_order_placer(standard,
                              ['haem:b', 'haem:c', 'oxygen'],
                              ) == [1, 2, 3, 0, 4]


# ---- test_the_arrows_sit_left_of_each_panel ------------------------------------------
def test_the_arrows_sit_left_of_each_panel() -> None:
    """
    ---- Summary ----
    Main function to check where the arrows of the panels are put and which one a
    click finds: an up and a down arrow in the room left of the picture, at the middle
    of each panel, smaller beside a low panel; the up arrow of the top panel and the
    down arrow of the bottom one cannot be used.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The picture is 400 x 300 px with its left at 30 px and its top at 10 px, and 26 px
    are kept for the arrows, so the squares are centred on x = 30 - 13 = 17 px. The
    oxygen panel lies from 0.6 to 0.9 of the height: its middle is at 10 + (1 - 0.75)
    x 300 = 85 px and it is 90 px tall, so the squares are 18 px: from 8 to 26 px
    across, the up one from 66 to 84 px and the down one from 86 to 104 px. The OCR
    panel lies from 0.2 to 0.5: middle 10 + 0.65 x 300 = 205 px, up from 186 to 204
    px, down from 206 to 224 px. A panel from 0 to 0.1 is 30 px tall: squares of
    30 / 2 - 1 = 14 px.

    ---- Helpers ----
    panel_arrow_finder
    panel_arrow_placer
    """

    # ---- 1 Two panels ----------------------------------------------------------------
    axis = TimeAxis(left=0.1,
                    right=0.9,
                    bottom=0.2,
                    top=0.9,
                    start_min=0.0,
                    end_min=30.0,
                    panels=[('oxygen', 0.6, 0.9), ('vo2', 0.2, 0.5)],
                    )
    arrows = panel_arrow_placer((30.0, 10.0, 400.0, 300.0), axis, 26.0)
    assert arrows == [('oxygen', -1, 8.0, 66.0, 26.0, 84.0, False),
                      ('oxygen', 1, 8.0, 86.0, 26.0, 104.0, True),
                      ('vo2', -1, 8.0, 186.0, 26.0, 204.0, True),
                      ('vo2', 1, 8.0, 206.0, 26.0, 224.0, False),
                      ]

    # ---- 2 The arrow under a click ---------------------------------------------------
    assert panel_arrow_finder(17.0, 195.0, arrows) == ('vo2', -1, True)
    assert panel_arrow_finder(17.0, 75.0, arrows) == ('oxygen', -1, False)
    assert panel_arrow_finder(17.0, 85.0, arrows) is None  # between the two squares
    assert panel_arrow_finder(200.0, 195.0, arrows) is None  # on the picture

    # ---- 3 A low panel ---------------------------------------------------------------
    low = TimeAxis(left=0.1,
                   right=0.9,
                   bottom=0.0,
                   top=0.1,
                   start_min=0.0,
                   end_min=30.0,
                   panels=[('vo2', 0.0, 0.1)],
                   )
    (up, down) = panel_arrow_placer((30.0, 10.0, 400.0, 300.0), low, 26.0)
    assert up[2:6] == pytest.approx((10.0, 280.0, 24.0, 294.0))
    assert down[2:6] == pytest.approx((10.0, 296.0, 24.0, 310.0))
    assert (up[6], down[6]) == (False, False)


# ---- test_the_order_is_saved_with_the_dataset ----------------------------------------
def test_the_order_is_saved_with_the_dataset(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the order of the panels is written in the settings
    file of the dataset and read back from it.

    ---- Inputs ----
    tmp_path : Path
        Pytest's temporary folder, used as the dataset folder.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes the settings file in the temporary folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    dataset_settings_reader
    dataset_settings_saver
    """

    order = ['vo2', 'oxygen', 'haem:Cyt bH']
    answers = dict(settings.DEFAULT_ANSWERS, panel_order=order)
    assert dataset_settings_saver(tmp_path,{}, answers) is True
    assert dataset_settings_reader(tmp_path)['answers']['panel_order'] == order


# ---- test_the_plot_is_drawn_in_the_order_given ---------------------------------------
def test_the_plot_is_drawn_in_the_order_given() -> None:
    """
    ---- Summary ----
    Main function to check the plot of a made-up file: with no order it is oxygen,
    OCR, then the haems a, b, c; with an order its panels are drawn in it, a haem new
    to the order in its standard place; and the window is told the key, the bottom
    and the top of each panel, top first.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The order [haem:Cyt cc, vo2, oxygen] with Cyt bH and Cyt cc shown: Cyt bH, which
    the order does not know, goes just above Cyt cc, the panel that follows it in the
    standard order, so [haem:Cyt bH, haem:Cyt cc, vo2, oxygen].

    ---- Helpers ----
    _figure_drawer
    time_axis_finder
    """

    # ---- 1 The standard order --------------------------------------------------------
    axis = time_axis_finder(_figure_drawer(['Cyt cc', 'Cyt bH', 'Cyt a605'], []))
    assert [key for key, _, _ in axis.panels] == ['oxygen',
                                                  'vo2',
                                                  'haem:Cyt a605',
                                                  'haem:Cyt bH',
                                                  'haem:Cyt cc',
                                                  ]

    # ---- 2 An order given ------------------------------------------------------------
    fig = _figure_drawer(['Cyt cc', 'Cyt bH'], ['haem:Cyt cc', 'vo2', 'oxygen'])
    axis = time_axis_finder(fig)
    keys = [key for key, _, _ in axis.panels]
    assert keys == ['haem:Cyt bH', 'haem:Cyt cc', 'vo2', 'oxygen']
    assert [ax.panel_key for ax in fig.axes[:4]] == keys

    # ---- 3 Where the panels sit: one under the other, inside the time axis -----------
    tops = [top for _, _, top in axis.panels]
    bottoms = [bottom for _, bottom, _ in axis.panels]
    assert all(bottom < top for bottom, top in zip(bottoms, tops))
    # a panel may touch the next one, so its bottom is at or above the next one's top
    assert all(upper > lower - 1e-9 for upper, lower in zip(bottoms, tops[1:]))
    assert (tops[0], bottoms[-1]) == pytest.approx((axis.top, axis.bottom))
