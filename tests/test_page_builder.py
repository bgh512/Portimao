"""
Tests of the page of a dataset figure in the window, without the window: the cell under a point, a drag as a plot, where a plot and its buttons are, the page fitted to the plot area and to the journals, the templates listed and the step that builds the page.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from dataclasses import replace
from pathlib import Path
from typing import List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_stages as viewer_stages
from utils_shared.figure_layout import figure_size_calculator
from utils_shared.figure_page import (FigurePage,
                                      page_plainer,
                                      PagePlot,
                                      panel_letters_finder,
                                      plot_lifter,
                                      plot_placer,
                                      template_reader,
                                      )
from utils_shared.journal_files import STANDARD_JOURNAL
from utils_viewer.viewer_page import (cells_describer,
                                      drag_plot_maker,
                                      page_box_finder,
                                      page_cell_finder,
                                      page_journal_fitter,
                                      page_offer_checker,
                                      page_picture_maker,
                                      PageBuilder,
                                      plot_box_finder,
                                      plot_button_finder,
                                      plot_buttons_placer,
                                      template_names_lister,
                                      )


# ---- CONSTANTS -----------------------------------------------------------------------
# A page drawn 600 px wide and 300 px tall, its top left corner at (100, 50): each of
# the 6 x 6 cells is 100 px wide and 50 px tall.
BOX = (100.0, 50.0, 600.0, 300.0)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_point_on_the_page_gives_its_cell -----------------------------------------
def test_a_point_on_the_page_gives_its_cell() -> None:
    """
    ---- Summary ----
    Main function to check the cell under a point, worked out by hand: inside the
    page, off the page (none), and off the page at the end of a drag (the nearest).

    ---- Inputs ----
    None.

    ---- Globals read ----
    BOX (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    column = floor((x - 100) / 100); row = floor((y - 50) / 50).

    ---- Helpers ----
    None.
    """

    assert page_cell_finder(150, 75, BOX) == (0, 0)
    assert page_cell_finder(420, 260, BOX) == (4, 3)
    assert page_cell_finder(699, 349, BOX) == (5, 5)
    assert page_cell_finder(99, 75, BOX) is None
    assert page_cell_finder(150, 351, BOX) is None
    assert page_cell_finder(99, 75, BOX, is_clamped=True) == (0, 0)
    assert page_cell_finder(900, 20, BOX, is_clamped=True) == (0, 5)
    assert page_cell_finder(320, 900, BOX, is_clamped=True) == (5, 2)


# ---- test_a_drag_becomes_a_plot ------------------------------------------------------
def test_a_drag_becomes_a_plot() -> None:
    """
    ---- Summary ----
    Main function to check that a drag gives the rectangle between its two cells
    whichever way it went, one cell for a click, and keeps the roles given.

    ---- Inputs ----
    None.

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

    down = drag_plot_maker((1, 2), (3, 4), 'P7', {'value': 'OCR'})
    up = drag_plot_maker((3, 4), (1, 2), 'P7', {'value': 'OCR'})
    assert down == up == PagePlot('P7', 1, 2, 3, 3, {'value': 'OCR'})
    assert drag_plot_maker((5, 0), (5, 0), 'P1', {}) == PagePlot('P1', 5, 0, 1, 1)
    # a drag that fits is placed, and one over it is refused by the page
    page = plot_placer(FigurePage(), down)
    with pytest.raises(ValueError):
        plot_placer(page, drag_plot_maker((0, 0), (1, 2), 'P1', {}))


# ---- test_where_a_plot_and_its_buttons_are -------------------------------------------
def test_where_a_plot_and_its_buttons_are() -> None:
    """
    ---- Summary ----
    Main function to check where the cells of a plot are in the plot area, where its
    ✎ and ✕ sit (18 px squares, 4 px from the top right corner and from each other)
    and which button a click finds, worked out by hand.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BOX (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    plot = PagePlot('P1', row=1, column=2, n_rows=2, n_columns=3)
    assert plot_box_finder(plot, BOX) == (300.0, 100.0, 600.0, 200.0)
    assert plot_buttons_placer(plot, BOX) == {'edit': (556.0, 104.0, 574.0, 122.0),
                                              'remove': (578.0, 104.0, 596.0, 122.0),
                                              }
    page = plot_placer(plot_placer(FigurePage(), PagePlot('P2', 0, 0)), plot)
    assert plot_button_finder(587, 110, page, BOX) == ('remove', 1)
    assert plot_button_finder(560, 110, page, BOX) == ('edit', 1)
    assert plot_button_finder(185, 60, page, BOX) == ('remove', 0)
    assert plot_button_finder(400, 150, page, BOX) is None
    assert plot_button_finder(576, 110, page, BOX) is None  # between the two


# ---- test_the_cells_in_words ---------------------------------------------------------
def test_the_cells_in_words() -> None:
    """
    ---- Summary ----
    Main function to check the words of the form for the cells of a plot, counted
    from 1.

    ---- Inputs ----
    None.

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

    assert cells_describer(PagePlot('P1', 0, 0)) == 'row 1, column 1 (1 cell)'
    assert (cells_describer(PagePlot('P1', 0, 2, 2, 4))
            == 'rows 1 to 2, columns 3 to 6 (8 cells)')
    assert cells_describer(PagePlot('P1', 5, 0, 1, 6),
                           ) == 'row 6, columns 1 to 6 (6 cells)'


# ---- test_the_page_fits_the_plot_area ------------------------------------------------
def test_the_page_fits_the_plot_area() -> None:
    """
    ---- Summary ----
    Main function to check the dots per inch that fit a page in the plot area, worked
    out by hand, and the picture drawn with them.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A page of 8 x 6 in in an area of 1000 x 600 px: 0.96 x min(125, 100) = 96 dpi.

    ---- Helpers ----
    None.
    """

    assert page_box_finder((1000, 600), (8.0, 6.0)) == pytest.approx(96.0)
    assert page_box_finder((600, 1000), (8.0, 6.0)) == pytest.approx(72.0)
    assert page_box_finder((20, 20), (8.0, 6.0)) == 10.0
    # a plot type that is not built yet, so it is drawn as its grey stand-in
    page = plot_placer(FigurePage(), PagePlot('P14', 0, 0, 3, 3))
    spec = settings.JOURNAL_SPECS[page.journal]
    width_in, height_in = figure_size_calculator(spec, page.columns, page.height)
    picture = page_picture_maker(page, spec, 50.0)
    assert picture.mode == 'RGB'
    assert picture.width == pytest.approx(width_in * 50.0, abs=1)
    assert picture.height == pytest.approx(height_in * 50.0, abs=1)
    # the stand-in of the plot is grey, and a free cell is white
    assert picture.getpixel((picture.width // 4, picture.height // 4)) != (255,
                                                                           255,
                                                                           255,
                                                                           )
    assert picture.getpixel((picture.width * 3 // 4,
                             picture.height * 3 // 4,
                             ),
                            ) == (255, 255, 255)


# ---- test_a_page_is_fitted_to_the_journals -------------------------------------------
def test_a_page_is_fitted_to_the_journals() -> None:
    """
    ---- Summary ----
    Main function to check a page read from a template against made-up journals: one
    that fits is left alone, a journal that is gone becomes the standard journal, and
    a width the journal lacks becomes two columns, or its first width, each said in a
    sentence.

    ---- Inputs ----
    None.

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

    specs = {STANDARD_JOURNAL: {'name': 'Standard', 'widths_mm': {1: 89.0, 2: 183.0}},
             'narrow': {'name': 'Narrow', 'widths_mm': {1: 80.0, 3: 170.0}},
             }
    page = FigurePage(journal='narrow', columns=3, height=0.5)
    assert page_journal_fitter(page, specs) == (page, None)
    fitted, words = page_journal_fitter(FigurePage('gone', 1, 0.5), specs)
    assert (fitted.journal, fitted.columns, fitted.height) == (STANDARD_JOURNAL, 1, 0.5)
    assert 'gone' in words and 'Standard' in words
    fitted, words = page_journal_fitter(FigurePage(STANDARD_JOURNAL, 1.5, 0.5), specs)
    assert fitted.columns == 2 and '1.5 columns' in words
    fitted, words = page_journal_fitter(FigurePage('narrow', 2, 0.5), specs)
    assert fitted.columns == 1 and 'Narrow' in words
    # the plots stay as they were
    full = plot_placer(FigurePage('gone', 2, 0.8), PagePlot('P1', 0, 0))
    assert page_journal_fitter(full, specs)[0].plots == full.plots


# ---- test_the_templates_are_listed ---------------------------------------------------
def test_the_templates_are_listed(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the templates offered from the layouts folder: its .json
    files by name, A to Z whatever their case, and none for a folder that is missing.

    ---- Inputs ----
    tmp_path : Path
        The layouts folder for the test.

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

    for name in ('time response.json', 'Haem and OCR.json', 'notes.txt'):
        (tmp_path / name).write_text('{}', encoding='utf-8')
    (tmp_path / 'folder.json').mkdir()
    assert template_names_lister(tmp_path) == ['Haem and OCR', 'time response']
    assert template_names_lister(tmp_path / 'missing') == []


# ---- test_a_plot_being_changed_is_kept -----------------------------------------------
def test_a_plot_being_changed_is_kept() -> None:
    """
    ---- Summary ----
    Main function to check the page read while a plot is off the page for ✎ (Continue
    with its form still open, or Cancel): the plot is where it was, with its letter,
    and a new plot whose form is still open is left out. The window is not made.

    ---- Inputs ----
    None.

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

    first, second = PagePlot('P1', 0, 0, 2, 3), PagePlot('P9', 0, 3, 2, 3)
    page = plot_placer(plot_placer(FigurePage(), first), second)
    builder = PageBuilder.__new__(PageBuilder)  # its state only, without its widgets
    builder.page, builder._lifted = plot_lifter(page, 0)
    builder._pending = PagePlot('P1', 4, 0, 2, 6)  # dragged elsewhere, not yet Done
    read = builder.page_reader()
    assert sorted(read.plots, key=lambda plot: plot.plot_type) == [first, second]
    letters = panel_letters_finder(read)
    assert {read.plots[i].plot_type: letter for i, letter in letters.items()} == {
        'P1': 'a',
        'P9': 'b',
        }
    # a new plot whose form is open is not on the page yet
    builder.page, builder._lifted = page, None
    assert builder.page_reader() == page


# ---- test_the_step_that_builds_the_page ----------------------------------------------
def test_the_step_that_builds_the_page(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch,
                                       ) -> None:
    """
    ---- Summary ----
    Main function to check the Build a figure step: it starts its step of the guide,
    shows an empty page with the layouts folder, the set-up and the experiments, asks
    6.2 and gives the page the window holds once Continue is clicked; with a page
    saved with the dataset it shows that page and says so, and with one that cannot
    be read the empty page after one warning; without a window it gives the page it
    started from and asks nothing. The window and the question are stood in for.

    ---- Inputs ----
    tmp_path : Path
        The layouts folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for the stand-ins.

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

    built = plot_placer(FigurePage(), PagePlot('P3', 2, 2, 2, 2))
    done: List[tuple] = []

    class FakeWindow:
        def page_shower(self,
                        page: FigurePage,
                        folder: Path,
                        setup: dict,
                        experiments: dict,
                        answers: dict,
                        ) -> None:
            done.append(('shown', page, folder, setup, experiments, answers))

        def page_hider(self) -> FigurePage:
            done.append(('hidden',))
            return built

        def page_kept_reader(self) -> FigurePage:
            return FigurePage()

    def waiter(question: str, nudge: str, number: str) -> str:
        done.append(('asked', number))
        return ''

    def offerer(page: FigurePage, kept: FigurePage, folder: Path) -> None:
        done.append(('offered', page, kept, folder))

    monkeypatch.setattr(viewer_stages, 'guide_step_starter', lambda key: done.append(('step', key)))
    monkeypatch.setattr(viewer_stages, 'info_printer', lambda *args, **kwargs: None)
    monkeypatch.setattr(viewer_stages, 'enter_waiter', waiter)
    monkeypatch.setattr(viewer_stages, '_template_offer_asker', offerer)
    monkeypatch.setattr(viewer_stages, 'active_gui_getter', lambda: FakeWindow())
    setup = {'group_names': ['', ''], 'colours': {}, 'rows': []}
    experiments = {'run1': {'experiment_name': 'run1'}}
    answers = {'haems': ['Cyt cc']}
    assert viewer_stages.page_stage_runner(tmp_path,
                                           setup,
                                           experiments,
                                           answers,
                                           ) == built
    assert done == [('step', 'page'),
                    ('shown', FigurePage(), tmp_path, setup, experiments, answers),
                    ('asked', '6.2'),
                    ('hidden',),
                    ('offered', built, FigurePage(), tmp_path),
                    ]

    # ---- 2 The page saved with the dataset is the page it starts with ----------------
    done.clear()
    saved = plot_placer(FigurePage(journal='science', columns=1, height=0.5),
                        PagePlot('P1', 0, 0, 2, 3, roles={'experiment': 'Group 1: 1'}),
                        )
    told: List[str] = []
    monkeypatch.setattr(viewer_stages, 'info_printer', lambda text, **kwargs: told.append(text))
    monkeypatch.setattr(viewer_stages, 'warning_shower', lambda text: done.append(('warned', text)))
    viewer_stages.page_stage_runner(tmp_path,
                                    setup,
                                    experiments,
                                    answers,
                                    page_plainer(saved),
                                    )
    assert done[1] == ('shown', saved, tmp_path, setup, experiments, answers)
    assert not any(step[0] == 'warned' for step in done)
    assert told[-1] == viewer_stages.SAVED_PAGE_NOTE

    # ---- 3 A saved page that cannot be read: the empty page and one warning ----------
    for broken in ({'plots': 'none'}, ['a'], dict(page_plainer(saved), version=7)):
        done.clear()
        told.clear()
        viewer_stages.page_stage_runner(tmp_path, setup, experiments, answers, broken)
        assert done[:3] == [('step', 'page'),
                            ('warned', viewer_stages.SAVED_PAGE_PROBLEM),
                            ('shown',
                             FigurePage(),
                             tmp_path,
                             setup,
                             experiments,
                             answers,
                             ),
                            ]
        assert viewer_stages.SAVED_PAGE_NOTE not in told

    # ---- 4 Without the window the page is as it started ------------------------------
    done.clear()
    monkeypatch.setattr(viewer_stages, 'active_gui_getter', lambda: None)
    assert viewer_stages.page_stage_runner(tmp_path) == FigurePage()
    assert done == [('step', 'page')]
    assert viewer_stages.page_stage_runner(tmp_path,
                                           saved_page=page_plainer(saved),
                                           ) == saved


# ---- test_when_the_template_offer_is_made --------------------------------------------
def test_when_the_template_offer_is_made() -> None:
    """
    ---- Summary ----
    Main function to check when a built page is offered to be saved as a template:
    only with a plot on it, and only when it is not the page last saved as a template,
    loaded from one, or started from; and that the page in the window keeps track of
    that page. The window is not made.

    ---- Inputs ----
    None.

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

    empty = FigurePage()
    built = plot_placer(empty, PagePlot('P9', 0, 0, 2, 3))
    assert not page_offer_checker(empty, empty)  # nothing to save
    assert page_offer_checker(built, empty)  # built from an empty page
    assert not page_offer_checker(built, built)  # saved or loaded, not changed since
    assert page_offer_checker(replace(built, columns=1), built)  # its size changed
    assert page_offer_checker(plot_placer(built, PagePlot('P1', 3, 0, 3, 6)), built)
    assert not page_offer_checker(empty, built)  # every plot removed
    builder = PageBuilder.__new__(PageBuilder)  # its state only, without its widgets
    builder._kept = built
    assert builder.kept_reader() == built


# ---- test_the_template_offer_saves_the_page ------------------------------------------
def test_the_template_offer_saves_the_page(tmp_path: Path,
                                           monkeypatch: pytest.MonkeyPatch,
                                           ) -> None:
    """
    ---- Summary ----
    Main function to check the offer made once the page is built: nothing is asked
    for a page that has not changed; No to 6.3 saves nothing; Yes asks the name (6.4)
    and writes the template, which reads back as the page; a name already there is
    asked about (6.5), where No asks the name again and Yes writes over it. The
    questions are stood in for.

    ---- Inputs ----
    tmp_path : Path
        The layouts folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for the stand-ins.

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

    empty = FigurePage()
    built = plot_placer(empty, PagePlot('P9', 0, 0, 2, 3))
    asked: List[str] = []
    replies: List[object] = []

    def yes_no(question: str, default: bool, number: str) -> bool:
        asked.append(number)
        return replies.pop(0)

    def text(question: str, checker: object, number: str) -> str:
        asked.append(number)
        return replies.pop(0)

    monkeypatch.setattr(viewer_stages, 'yes_no_asker', yes_no)
    monkeypatch.setattr(viewer_stages, 'text_asker', text)
    monkeypatch.setattr(viewer_stages, 'info_printer', lambda *args, **kwargs: None)

    # ---- 1 Not changed, or No: nothing saved -----------------------------------------
    assert viewer_stages._template_offer_asker(built, built, tmp_path) is None
    assert asked == []
    replies[:] = [False]
    assert viewer_stages._template_offer_asker(built, empty, tmp_path) is None
    assert asked == ['6.3']
    assert list(tmp_path.iterdir()) == []

    # ---- 2 Yes and a name: the template is written -----------------------------------
    del asked[:]
    replies[:] = [True, ' bars ']
    path = viewer_stages._template_offer_asker(built, empty, tmp_path)
    assert path == tmp_path / 'bars.json'
    assert asked == ['6.3', '6.4']
    assert template_reader(path) == built

    # ---- 3 The name is taken: No asks again, Yes writes over -------------------------
    wider = plot_placer(built, PagePlot('P1', 3, 0, 3, 6))
    del asked[:]
    replies[:] = [True, 'bars', False, 'bars two']
    path = viewer_stages._template_offer_asker(wider, built, tmp_path)
    assert path == tmp_path / 'bars two.json'
    assert asked == ['6.3', '6.4', '6.5', '6.4']
    assert template_reader(tmp_path / 'bars.json') == built
    del asked[:]
    replies[:] = [True, 'bars', True]
    assert viewer_stages._template_offer_asker(wider, built, tmp_path) == (
        tmp_path / 'bars.json')
    assert asked == ['6.3', '6.4', '6.5']
    assert template_reader(tmp_path / 'bars.json') == wider
