"""
Tests of the page of a dataset figure: plots placed on the grid, refused over another
or past the edge, taken off and placed again, removed; the letters in reading order;
the page size per journal; the page drawn off screen; the templates saved and read
back; the PDF of the page (its size, its fonts) and what the run saves of it.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import errno
import io
import json
import re
from dataclasses import replace
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import main as program
import utils_shared.figure_page as figure_page
from utils_shared.figure_page import (figure_file_namer,
                                      figure_page_drawer,
                                      figure_page_exporter,
                                      FigurePage,
                                      FigurePageError,
                                      page_plainer,
                                      PagePlot,
                                      panel_letters_finder,
                                      plain_page_reader,
                                      plot_lifter,
                                      plot_placer,
                                      plot_remover,
                                      template_reader,
                                      template_saver,
                                      )
from utils_shared.journal_files import STANDARD_SPEC
from utils_shared.page_plots import NO_MEAN, NO_VALUES, NOT_THERE
from utils_shared.run_logging import details_place_setter


# ---- PAGE MAKERS ---------------------------------------------------------------------


# ---- _page_maker ---------------------------------------------------------------------
def _page_maker() -> FigurePage:
    """
    ---- Summary ----
    Helper function to make a page of four plots: a standard experiment over the top
    left two rows and three columns, a bar chart top right, a mean trace below them
    and a drawing along the bottom row, placed out of reading order.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    FigurePage
        The page; its plots in the order placed: drawing, bar chart, standard
        experiment, mean trace.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    page = FigurePage()
    for plot in (PagePlot('P17', row=5, column=0, n_rows=1, n_columns=6),
                 PagePlot('P9',
                          row=0,
                          column=3,
                          n_rows=2,
                          n_columns=3,
                          roles={'group_1': 'Split'},
                          ),
                 PagePlot('P1',
                          row=0,
                          column=0,
                          n_rows=2,
                          n_columns=3,
                          roles={'experiment': 'Group 1, first label, replicate 1'},
                          ),
                 PagePlot('P8', row=2, column=0, n_rows=1, n_columns=6),
                 ):
        page = plot_placer(page, plot)
    return page


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_new_page_is_two_columns_and_0_8_tall -------------------------------------
def test_a_new_page_is_two_columns_and_0_8_tall() -> None:
    """
    ---- Summary ----
    Main function to check the size of a new page, drawn for Nature and for Science.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Nature: 183 mm wide for two columns, 170 mm tallest; 183 / 25.4 = 7.205 in and
    170 x 0.8 / 25.4 = 5.354 in. Science: 121 mm for two columns, 199 mm tallest;
    121 / 25.4 = 4.764 in and 199 x 0.8 / 25.4 = 6.268 in.

    ---- Helpers ----
    None.
    """

    page = FigurePage()
    assert (page.journal, page.columns, page.height) == ('nature', 2, 0.8)
    fig, _ = figure_page_drawer(page, STANDARD_SPEC)
    assert fig.get_size_inches() == pytest.approx((7.205, 5.354), abs=0.001)
    science = replace(page, journal='science')
    fig, _ = figure_page_drawer(science, settings.JOURNAL_SPECS['science'])
    assert fig.get_size_inches() == pytest.approx((4.764, 6.268), abs=0.001)


# ---- test_a_plot_is_refused_over_another_or_past_the_edge ----------------------------
def test_a_plot_is_refused_over_another_or_past_the_edge() -> None:
    """
    ---- Summary ----
    Main function to check that a plot is refused over a plot already there (named by
    its letter), past the edge of the grid, of no cells, of an unknown type, or of
    the Legend, which is no longer a plot type, and that the page is left as it was.

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
    _page_maker
    """

    page = _page_maker()
    with pytest.raises(FigurePageError, match=r'covers plot b \(Bar chart\)'):
        plot_placer(page, PagePlot('P7', row=1, column=5))
    with pytest.raises(FigurePageError, match=r'covers plot c \(Mean trace\)'):
        plot_placer(page, PagePlot('P7', row=2, column=2, n_rows=2))
    with pytest.raises(FigurePageError, match='Legend is no longer a plot type'):
        plot_placer(page, PagePlot('P16', row=3, column=0))
    with pytest.raises(FigurePageError, match='past the edge'):
        plot_placer(page, PagePlot('P7', row=3, column=4, n_rows=1, n_columns=3))
    with pytest.raises(FigurePageError, match='past the edge'):
        plot_placer(page, PagePlot('P7', row=3, column=0, n_rows=0))
    with pytest.raises(FigurePageError, match='no plot type'):
        plot_placer(page, PagePlot('P99', row=3, column=0))
    assert len(page.plots) == 4
    fitted = plot_placer(page, PagePlot('P7', row=3, column=0, n_rows=2, n_columns=6))
    assert len(fitted.plots) == 5


# ---- test_a_plot_taken_off_and_placed_again ------------------------------------------
def test_a_plot_taken_off_and_placed_again() -> None:
    """
    ---- Summary ----
    Main function to check ✎ and ✕: a plot taken off frees its cells, keeps its type
    and roles, and can be placed over its old cells made larger; Cancel puts it back as
    it was; a removed plot is gone.

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
    _page_maker
    """

    page = _page_maker()
    lifted_page, plot = plot_lifter(page, 1)
    assert plot.plot_type == 'P9' and plot.roles == {'group_1': 'Split'}
    assert len(lifted_page.plots) == 3
    wider = plot_placer(lifted_page,
                        replace(plot, row=0, column=3, n_rows=2, n_columns=3),
                        )
    assert wider.plots[-1].roles == {'group_1': 'Split'}
    taller = plot_placer(lifted_page,
                         replace(plot, row=3, column=3, n_rows=2, n_columns=3),
                         )
    assert taller.plots[-1].row == 3
    cancelled = plot_placer(lifted_page, plot)
    assert cancelled.plots[-1] == plot
    assert sorted(cancelled.plots, key=repr) == sorted(page.plots, key=repr)
    removed = plot_remover(page, 1)
    assert [p.plot_type for p in removed.plots] == ['P17', 'P1', 'P8']
    with pytest.raises(IndexError):
        plot_remover(page, 4)


# ---- test_letters_in_reading_order ---------------------------------------------------
def test_letters_in_reading_order() -> None:
    """
    ---- Summary ----
    Main function to check the letters: by each plot's top left cell, left to right
    then down, whatever the order the plots were placed in, every plot with one; and
    the letters follow when a plot is removed.

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
    Plots placed: drawing (row 5), bar chart (row 0, column 3), standard experiment
    (row 0, column 0), mean trace (row 2). Reading order: standard experiment a, bar
    chart b, mean trace c, drawing d. Without the standard experiment: bar chart a,
    mean trace b, drawing c.

    ---- Helpers ----
    _page_maker
    """

    page = _page_maker()
    assert panel_letters_finder(page) == {2: 'a', 1: 'b', 3: 'c', 0: 'd'}
    assert panel_letters_finder(plot_remover(page, 2)) == {1: 'a', 2: 'b', 0: 'c'}


# ---- test_the_page_drawn_off_screen --------------------------------------------------
def test_the_page_drawn_off_screen() -> None:
    """
    ---- Summary ----
    Main function to check the page as drawn: one sentence over the cells of a bar
    chart, of a standard experiment and of a mean trace with no experiment to show,
    a grey stand-in named by its plot type over those of a plot whose plot type is
    not built yet, a Space for a
    drawing left empty, and the letters bold at the journal's size, at the top left
    of their plots, lower case for Nature and upper case for a journal that asks for
    it.

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
    The standard experiment takes columns 0 to 2 and rows 0 and 1: its axes lie inside
    x 0 to 0.5 and y 1 - 2 / 6 = 0.667 to 1. The bar chart lies inside x 0.5 to 1.

    ---- Helpers ----
    _page_maker
    """

    page = _page_maker()
    fig, axes = figure_page_drawer(page, STANDARD_SPEC)
    assert set(axes) == {0, 1, 2, 3}
    names = [' '.join(axes[i].texts[0].get_text().split()) for i in range(1, 4)]
    # with no experiment to show, each plot says so
    assert names == [NO_VALUES, NOT_THERE, NO_MEAN]
    # a plot type that is not built yet is a grey stand-in with its name
    later = plot_placer(FigurePage(), PagePlot('P14', row=0, column=0))
    _, stand_ins = figure_page_drawer(later, STANDARD_SPEC)
    assert stand_ins[0].texts[0].get_text() == 'Scatter of two numbers'
    # the space for a drawing draws nothing: no box, no text, only its letter
    assert not axes[0].axison and not axes[0].texts and not axes[0].lines
    box = axes[2].get_position()
    assert 0 < box.x0 < box.x1 < 0.5
    assert 2 / 3 < box.y0 < box.y1 < 1
    assert axes[1].get_position().x0 > 0.5
    letters = sorted(fig.texts, key=lambda t: t.get_text())
    assert [t.get_text() for t in letters] == ['a', 'b', 'c', 'd']
    assert all(t.get_fontweight() == 'bold' for t in letters)
    assert all(t.get_fontsize() == STANDARD_SPEC['panel_letter_pt'] for t in letters)
    a_x, a_y = letters[0].get_position()
    assert a_x == pytest.approx(box.x0) and a_y > box.y1
    upper = dict(STANDARD_SPEC, panel_letter_case='upper')
    fig, _ = figure_page_drawer(page, upper)
    assert sorted(t.get_text() for t in fig.texts) == ['A', 'B', 'C', 'D']


# ---- test_a_plot_keeps_its_text_inside_its_cells -------------------------------------
def test_a_plot_keeps_its_text_inside_its_cells(monkeypatch: pytest.MonkeyPatch,
                                                ) -> None:
    """
    ---- Summary ----
    Main function to check a plot that is drawn for real, with a made-up plot type
    that fills its room and has long tick numbers, axis titles and two named lines:
    after the page is drawn, the tick numbers, the axis titles and the legend are all
    inside the cells of the plot, the axes are smaller than the room they were given,
    the legend covers neither line, and the drawer was handed the set-up and the
    experiments.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the made-up plot type in place of the standard experiment's.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The plot takes rows 2 and 3 and columns 0 to 2: x from 0 to 0.5 and y from
    1 - 4 / 6 = 0.333 to 1 - 2 / 6 = 0.667 of the figure.

    ---- Helpers ----
    None.
    """

    given = {}

    # ---- drawer ----------------------------------------------------------------------
    def drawer(fig: object, room: tuple, plot: PagePlot, context: dict) -> list:
        given.update(context, room=room)
        x0, y0, x1, y1 = room
        ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
        ax.plot([0, 1, 2, 3], [100000, 250000, 250000, 250000], label='control')
        ax.plot([0, 1, 2, 3], [100000, 100000, 100000, 240000], label='knockdown')
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('OCR (µM min⁻¹)')
        return [ax]

    monkeypatch.setitem(figure_page.PLOT_DRAWERS, 'P1', drawer)
    setup = {'group_names': ['', ''], 'colours': {}, 'rows': []}
    experiments = {'run1': {'experiment_name': 'run1'}}
    page = plot_placer(FigurePage(),
                       PagePlot('P1', row=2, column=0, n_rows=2, n_columns=3),
                       )
    fig, axes = figure_page_drawer(page, STANDARD_SPEC, setup, experiments)
    assert given['setup'] is setup and given['experiments'] is experiments
    ax = axes[0]
    renderer = fig._get_renderer()
    tight = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
    assert 0 <= tight.x0 and tight.x1 <= 0.5
    assert 1 / 3 <= tight.y0 and tight.y1 <= 2 / 3
    place = ax.get_position()
    x0, y0, x1, y1 = given['room']
    assert place.x0 > x0 and place.y0 > y0  # room made for the numbers and titles
    assert place.x1 <= x1 + 1e-6 and place.y1 <= y1 + 1e-6
    legend = ax.get_legend()
    assert [text.get_text() for text in legend.get_texts()] == ['control', 'knockdown']
    box = legend.get_window_extent(renderer)
    for line in ax.lines:
        points = line.get_transform().transform(line.get_xydata())
        assert not any(box.contains(x, y) for x, y in points)


# ---- test_a_template_saved_and_read_back ---------------------------------------------
def test_a_template_saved_and_read_back(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check a template: saved under a cleaned name with the page size,
    each plot's type, cells and roles and no file names; read back into the same page,
    also from the layouts folder of another dataset; not written over unless asked.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

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
    _page_maker
    """

    page = replace(_page_maker(), journal='science', columns=1, height=0.5)
    layouts = tmp_path / 'layouts'
    path = template_saver(page, layouts, 'My figure: two/strains')
    assert path == layouts / 'My figure_ two_strains.json'
    content = json.loads(path.read_text(encoding='utf-8'))
    assert content['journal'] == 'science'
    assert content['plots'][1] == {'type': 'P9',
                                   'cells': {'row': 0,
                                             'column': 3,
                                             'rows': 2,
                                             'columns': 3,
                                             },
                                   'roles': {'group_1': 'Split'},
                                   }
    assert '.paf' not in path.read_text(encoding='utf-8')
    assert template_reader(path) == page
    other_dataset = tmp_path / 'another_dataset' / 'layouts'
    other_dataset.mkdir(parents=True)
    copy = other_dataset / path.name
    copy.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
    assert template_reader(copy) == page
    with pytest.raises(FigurePageError, match='already there'):
        template_saver(page, layouts, 'My figure: two/strains')
    assert template_saver(replace(page, height=0.6),
                          layouts,
                          'My figure: two/strains',
                          may_replace=True,
                          ) == path
    assert template_reader(path).height == 0.6


# ---- test_a_template_with_a_file_name_is_not_saved -----------------------------------
def test_a_template_with_a_file_name_is_not_saved(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a plot whose roles name a file of the dataset stops
    the template being saved, and that no file is written.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

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

    page = plot_placer(FigurePage(),
                       PagePlot('P1',
                                row=0,
                                column=0,
                                roles={'experiment': 'control-bd_then_kcn-run1.paf'},
                                ),
                       )
    with pytest.raises(FigurePageError, match='names a file'):
        template_saver(page, tmp_path, 'figure')
    assert list(tmp_path.iterdir()) == []


# ---- test_a_broken_template_is_refused -----------------------------------------------
def test_a_broken_template_is_refused(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a file that is not a template, one of another version,
    one with a page size that cannot be read, and one whose plots overlap, run past the
    grid or name a file are each refused with one sentence naming the file.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

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

    good = {'kind': 'Portimao figure template',
            'version': 1,
            'journal': 'nature',
            'columns': 2,
            'height': 0.8,
            'plots': [{'type': 'P9',
                       'cells': {'row': 0, 'column': 0, 'rows': 2, 'columns': 2},
                       'roles': {},
                       },
                      ],
            }
    plot_over = dict(good['plots'][0],
                     cells={'row': 1, 'column': 1, 'rows': 1, 'columns': 1},
                     )
    plot_past = dict(good['plots'][0],
                     cells={'row': 5, 'column': 5, 'rows': 2, 'columns': 1},
                     )
    plot_file = dict(good['plots'][0], roles={'experiment': 'data/run1.paf'})
    cases = {'not_json': ('{not json', 'not a template'),
             'other_kind': (json.dumps(dict(good, kind='fit')), 'not a template'),
             'other_version': (json.dumps(dict(good, version=2)), 'another version'),
             'bad_height': (json.dumps(dict(good, height=1.5)), 'page size'),
             'no_plots': (json.dumps(dict(good, plots=None)), 'no list of plots'),
             'over': (json.dumps(dict(good, plots=good['plots'] + [plot_over])),
                      'covers plot a',
                      ),
             'past': (json.dumps(dict(good, plots=[plot_past])), 'past the edge'),
             'file': (json.dumps(dict(good, plots=[plot_file])), 'names a file'),
             'no_cells': (json.dumps(dict(good, plots=[{'type': 'P9'}])), 'no cells'),
             }
    for name, (text, words) in cases.items():
        path = tmp_path / f'{name}.json'
        path.write_text(text, encoding='utf-8')
        with pytest.raises(FigurePageError, match=words) as caught:
            template_reader(path)
        assert str(caught.value).startswith(f'The template {name}.json cannot be used')
    good_path = tmp_path / 'good.json'
    good_path.write_text(json.dumps(good), encoding='utf-8')
    assert len(template_reader(good_path).plots) == 1


# ---- test_a_page_as_plain_values_and_back --------------------------------------------
def test_a_page_as_plain_values_and_back(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the plain values of a page: what a template file holds,
    read back into the same page with every role, and refused with one sentence that
    starts as asked when they are not a page, or hold a plot that cannot be placed.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

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
    _page_maker
    """

    page = replace(_page_maker(), journal='science', columns=1, height=0.5)
    plain = page_plainer(page)
    assert plain['kind'] == 'Portimao figure template' and plain['version'] == 1
    assert (plain['journal'], plain['columns'], plain['height']) == ('science', 1, 0.5)
    assert [entry['type'] for entry in plain['plots']] == [plot.plot_type
                                                           for plot in page.plots
                                                           ]
    path = template_saver(page, tmp_path, 'figure')
    assert json.loads(path.read_text(encoding='utf-8')) == plain
    # as a settings file gives it back: through JSON
    start = 'The saved page cannot be used'
    assert plain_page_reader(json.loads(json.dumps(plain)), start) == page
    assert plain_page_reader(page_plainer(FigurePage()), start) == FigurePage()
    over = dict(plain, plots=plain['plots'] + [plain['plots'][0]])
    for broken, words in ((None, 'not a template'),
                          (['a'], 'not a template'),
                          ({'plots': []}, 'not a template'),
                          (dict(plain, version=2), 'another version'),
                          (dict(plain, height='tall'), 'page size'),
                          (dict(plain, plots='none'), 'no list of plots'),
                          (over, 'covers plot'),
                          ):
        with pytest.raises(FigurePageError, match=words) as caught:
            plain_page_reader(broken, start)
        assert str(caught.value).startswith(start)


# ---- test_an_empty_page_saves_no_figure ----------------------------------------------
def test_an_empty_page_saves_no_figure(tmp_path: Path,
                                       capsys: pytest.CaptureFixture,
                                       ) -> None:
    """
    ---- Summary ----
    Main function to check a page with no plot: the saving of the PDF refuses it in
    one sentence, and the run saves nothing and says nothing.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.
    capsys : pytest.CaptureFixture
        What is shown on screen.

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

    with pytest.raises(FigurePageError, match='no plot'):
        figure_page_exporter(FigurePage(), STANDARD_SPEC, tmp_path / 'results')
    assert program.dataset_figure_saver(FigurePage(), tmp_path / 'results') == []
    assert not (tmp_path / 'results').exists()
    assert capsys.readouterr().out == ''


# ---- test_a_file_that_was_not_read_is_named ------------------------------------------
def test_a_file_that_was_not_read_is_named(tmp_path: Path,
                                           capsys: pytest.CaptureFixture,
                                           ) -> None:
    """
    ---- Summary ----
    Main function to check the run with a plot that shows experiments of which one
    could not be read when the plots were saved: it is named in one warning, and the
    figure is still saved; with every experiment read, nothing is said about them.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.
    capsys : pytest.CaptureFixture
        What is shown on screen.

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

    setup = {'group_names': ['', ''],
             'colours': {'control': '#0072b2'},
             'rows': [{'name': name,
                       'use': True,
                       'group_1': 'control',
                       'group_2': '',
                       'time_point': '',
                       'run': run,
                       }
                      for run, name in enumerate(('run1', 'run2'), start=1)
                      ],
             }
    page = plot_placer(FigurePage(),
                       PagePlot('P8', row=0, column=0, n_rows=2, n_columns=3),
                       )
    figure = tmp_path / 'dataset_figure_nature.pdf'
    read = {'run1': {'experiment_name': 'run1'}}
    assert program.dataset_figure_saver(page, tmp_path, setup, read)[0] == figure
    shown = ' '.join(capsys.readouterr().out.split())
    assert ('The dataset figure is drawn without run2: it could not be read when the '
            'plots were saved'
            ) in shown
    both = dict(read, run2={'experiment_name': 'run2'})
    assert program.dataset_figure_saver(page, tmp_path, setup, both)[0] == figure
    assert 'drawn without' not in capsys.readouterr().out

    # a waterfall names the experiments it leaves out for having no difference spectrum
    page = plot_placer(FigurePage(),
                       PagePlot('P3', row=0, column=0, n_rows=2, n_columns=3),
                       )
    spectrum = {'wavelengths_nm': [540.0, 550.0, 560.0],
                'difference_mOD': [0.0, 2.0, 1.0],
                }
    both = {'run1': {'experiment_name': 'run1', 'difference': spectrum},
            'run2': {'experiment_name': 'run2', 'difference': None},
            }
    assert program.dataset_figure_saver(page, tmp_path, setup, both)[0] == figure
    shown = ' '.join(capsys.readouterr().out.split())
    assert ('The waterfall is drawn without run2: it has no difference spectrum, '
            'which needs an oxidised and a reduced region.'
            ) in shown
    both['run2']['difference'] = spectrum
    assert program.dataset_figure_saver(page, tmp_path, setup, both)[0] == figure
    assert 'drawn without' not in capsys.readouterr().out


# ---- test_the_figure_pdf_has_its_printed_size ----------------------------------------
def test_the_figure_pdf_has_its_printed_size(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the PDF of a page for Nature and for Science: its name, its
    folder (made when missing) and that its one page is exactly the printed size of
    the figure, worked out by hand.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A PDF measures its page in points of 1/72 in. Nature, two columns and 0.8 of the
    tallest: 183 mm by 170 x 0.8 = 136 mm, so 183 / 25.4 x 72 = 518.7 by
    136 / 25.4 x 72 = 385.5 points. Science, two columns and 0.8: 121 mm by
    199 x 0.8 = 159.2 mm, so 121 / 25.4 x 72 = 343.0 by 159.2 / 25.4 x 72 = 451.3
    points.

    ---- Helpers ----
    _page_maker
    """

    assert figure_file_namer('nature') == 'dataset_figure_nature.pdf'
    assert figure_file_namer('plos_one') == 'dataset_figure_plos_one.pdf'
    sizes = {}
    for journal in ('nature', 'science'):
        page = replace(_page_maker(), journal=journal)
        path, fig = figure_page_exporter(page,
                                         settings.JOURNAL_SPECS[journal],
                                         tmp_path / 'results',
                                         )
        assert path == tmp_path / 'results' / f'dataset_figure_{journal}.pdf'
        boxes = re.findall(rb'/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]',
                           path.read_bytes(),
                           )
        assert len(boxes) == 1  # one page
        sizes[journal] = tuple(float(side) for side in boxes[0])
        # the figure handed back for the master page is the one that was saved
        assert tuple(fig.get_size_inches() * 72) == pytest.approx(sizes[journal],
                                                                  abs=0.1,
                                                                  )
    assert sizes['nature'] == pytest.approx((518.7, 385.5), abs=0.1)
    assert sizes['science'] == pytest.approx((343.0, 451.3), abs=0.1)


# ---- test_the_figure_pdf_keeps_its_text ----------------------------------------------
def test_the_figure_pdf_keeps_its_text(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the PDF of a page holds its fonts as TrueType (PDF
    font type 42), whatever the font type set elsewhere, so the text stays text and
    can be changed in a drawing program; and that nothing in it is a picture.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

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
    _page_maker
    """

    with matplotlib.rc_context({'pdf.fonttype': 3}):  # letters as drawings: not wanted
        path, _ = figure_page_exporter(_page_maker(), STANDARD_SPEC, tmp_path)
    content = path.read_bytes()
    assert b'/FontFile2' in content  # a TrueType font file is in the PDF
    assert b'/Type3' not in content  # no letter is kept as a drawing
    assert b'/Subtype /Image' not in content  # and the figure is not a picture


# ---- test_the_run_saves_the_figure_and_its_master_page -------------------------------
def test_the_run_saves_the_figure_and_its_master_page(tmp_path: Path,
                                                      monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture,
                                                      ) -> None:
    """
    ---- Summary ----
    Main function to check what the run does with a page that holds plots: the figure
    and its master page are saved in the results folder, the master page on the
    journal's page (A4 for Nature, which gives none), and each is named on screen; a
    master page that is open in another program gives one plain sentence, with the
    words of Python in the log only, and the figure is still saved; a figure that
    cannot be saved gives its sentence and no master page is tried.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for the saving that fails.
    capsys : pytest.CaptureFixture
        What is shown on screen.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A4 is 210 / 25.4 x 72 = 595.3 by 297 / 25.4 x 72 = 841.9 points.

    ---- Helpers ----
    _page_maker
    """

    # ---- 1 Both files are saved ------------------------------------------------------
    page = _page_maker()
    figure = tmp_path / 'dataset_figure_nature.pdf'
    master = tmp_path / 'dataset_figure_master_nature.pdf'
    assert program.dataset_figure_saver(page, tmp_path) == [figure, master]
    boxes = re.findall(rb'/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]',
                       master.read_bytes(),
                       )
    assert [tuple(float(side) for side in box) for box in boxes] == [
        pytest.approx((595.3, 841.9), abs=0.1),
        ]
    shown = capsys.readouterr().out
    assert 'Saved dataset_figure_nature.pdf (Nature, 183 x 136 mm)' in shown
    assert 'Saved dataset_figure_master_nature.pdf' in shown

    # ---- refuser ---------------------------------------------------------------------
    def refuser(*_args: object) -> Path:
        raise PermissionError(errno.EACCES, 'Permission denied', str(master))

    # ---- 2 The master page is open in another program --------------------------------
    log = io.StringIO()
    details_place_setter(log, 'the test log')
    try:
        monkeypatch.setattr(program, 'master_page_exporter', refuser)
        assert program.dataset_figure_saver(page, tmp_path) == [figure]
        shown = ' '.join(capsys.readouterr().out.split())
        assert ('The master page of the dataset figure was not saved: '
                'dataset_figure_master_nature.pdf could not be opened or saved, perhaps '
                'because it is open in another program'
                ) in shown
        assert 'Permission denied' not in shown
        assert 'Permission denied' in log.getvalue()

        # ---- 3 The figure cannot be saved: no master page is tried -------------------
        tried = []
        monkeypatch.setattr(program, 'figure_page_exporter', refuser)
        monkeypatch.setattr(program,
                            'master_page_exporter',
                            lambda *args: tried.append(args),
                            )
        assert program.dataset_figure_saver(page, tmp_path) == []
        assert tried == []
        shown = ' '.join(capsys.readouterr().out.split())
        assert 'The dataset figure was not saved: ' in shown
        assert 'Permission denied' not in shown
    finally:
        details_place_setter(None, '')
