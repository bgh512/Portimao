"""
The page of a dataset figure: plots placed on a grid over a journal page, their letters,
the page drawn with each plot in its cells (a stand-in for a plot type not built yet)
and saved as a PDF, and the templates saved and read back.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import (axes_room_fitter,
                                        FALLBACK_FONTS,
                                        figure_size_calculator,
                                        figure_style_builder,
                                        font_family_lister,
                                        MM_PER_INCH,
                                        plot_legend_placer,
                                        )
from utils_shared.helpers import file_name_sanitiser
from utils_shared.journal_files import STANDARD_JOURNAL


# ---- CONSTANTS -----------------------------------------------------------------------
GRID_ROWS = 6
GRID_COLUMNS = 6
STANDARD_COLUMNS = 2  # a new page is two columns wide
STANDARD_HEIGHT = 0.8  # and 0.8 of the journal's tallest figure
# Every plot type of the builder by its number; the first ones (FIRST_TYPES) are the
# ones offered in the strip of the page, the others are not built yet.
PLOT_TYPES = {'P1': 'Standard experiment',
              'P2': 'Difference spectrum',
              'P3': 'Waterfall',
              'P4': 'Spectra at averaging regions',
              'P5': 'Spectral heat map',
              'P6': 'Spectra over time in 3D',
              'P7': 'Single trace',
              'P8': 'Mean trace',
              'P9': 'Bar chart',
              'P10': 'Before and after',
              'P11': 'Response by region',
              'P12': 'Time points',
              'P13': 'Haem amounts',
              'P14': 'Scatter of two numbers',
              'P15': 'Dose response',
              'P17': 'Space for a drawing',
              'P18': 'Numbers table',
              'P19': 'PCA',
              'P20': 'Two experiments compared',
              }
FIRST_TYPES = ('P1',
               'P2',
               'P3',
               'P7',
               'P8',
               'P9',
               'P10',
               'P11',
               'P12',
               'P17',
               )
# A plot type that was taken out, with the sentence a template that still holds one is
# refused with
REMOVED_TYPES = {'P16': 'The Legend is no longer a plot type: each plot has its own '
                        'small legend.',
                 }
# What draws each plot type, {plot type: (fig, room, plot, context) -> its axes}: room
# is (x0, y0, x1, y1) of the plot's cells less the gap and its letter, as fractions of
# the figure, and context holds 'spec', 'style' (figure_style_builder), 'fonts',
# 'setup' (dataset_setup), 'experiments' ({name: page_experiment}), 'answers' (the
# answers of the run) and 'page' (the page). The axes are then fitted into the room
# with their text and given a legend. A plot type that is not here is drawn as a grey
# stand-in. Each plot type adds its own (utils_shared/page_plots.py).
PLOT_DRAWERS: Dict[str, Callable[..., List[Axes]]] = {}
# What puts the plots of one plot type on the same scales, {plot type: (drawn,
# context) -> None}, drawn being [(the plot, its axes)] of every plot of that type on
# the page; it runs once every plot is drawn, before their text is fitted.
SCALE_SHARERS: Dict[str, Callable[[list, dict], None]] = {}
EMPTY_TYPES = ('P17',)  # drawn as nothing but their letter
LETTERS = 'abcdefghijklmnopqrstuvwxyz'
# the space kept round each plot inside its cells, and the grey of a stand-in
PLOT_GAP_MM = 1.5
STAND_IN_GREY = '#e6e6e6'
STAND_IN_EDGE = '#9a9a9a'
# the file of the figure, and how its fonts go into the PDF: 42 embeds them as TrueType,
# so the text stays text that a drawing program can change
FIGURE_NAME = 'dataset_figure'
PDF_FONT_TYPE = 42
# what a template file says it is, so another JSON file is not taken for one
TEMPLATE_KIND = 'Portimao figure template'
TEMPLATE_VERSION = 1
# a template keeps roles ("Group 1, first label"), never a file of the dataset
FILE_NAME_PATTERN = re.compile(r'(\.(paf|csv|xlsx|txt|bin|fit|json)\s*$)|[/\\]',
                               re.IGNORECASE,
                               )


# ---- FigurePageError -----------------------------------------------------------------
class FigurePageError(ValueError):
    """
    ---- Summary ----
    A plot that cannot go where it was put, or a template that cannot be saved or used;
    the message is one plain sentence for the user.

    ---- Attributes ----
    None.

    ---- Globals read ----
    None.

    ---- Methods ----
    None.
    """


# ---- PagePlot ------------------------------------------------------------------------
@dataclass(frozen=True)
class PagePlot:
    """
    ---- Summary ----
    One plot of a dataset figure: its plot type, the rectangle of grid cells it takes
    and the roles it was given.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    plot_type: str
    row: int
    column: int
    n_rows: int = 1
    n_columns: int = 1
    roles: Dict[str, str] = field(default_factory=dict)


# ---- FigurePage ----------------------------------------------------------------------
@dataclass(frozen=True)
class FigurePage:
    """
    ---- Summary ----
    The page of a dataset figure: the journal and size it is drawn at, and its plots in
    the order they were placed.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    journal: str = STANDARD_JOURNAL
    columns: float = STANDARD_COLUMNS
    height: float = STANDARD_HEIGHT
    plots: Tuple[PagePlot, ...] = ()


# ---- PAGE HELPERS --------------------------------------------------------------------


# ---- _cells_lister -------------------------------------------------------------------
def _cells_lister(plot: PagePlot) -> Set[Tuple[int, int]]:
    """
    ---- Summary ----
    Helper function to list the grid cells a plot takes.

    ---- Inputs ----
    plot : PagePlot
        The plot.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Set[Tuple[int, int]]
        {(row, column), ...}, counted from 0 at the top left.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {(row, column)
            for row in range(plot.row, plot.row + plot.n_rows)
            for column in range(plot.column, plot.column + plot.n_columns)
            }


# ---- _placement_problem_finder -------------------------------------------------------
def _placement_problem_finder(page: FigurePage, plot: PagePlot) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find why a plot cannot go on a page: an unknown plot type, a
    rectangle that is not inside the grid, or one over a plot already there.

    ---- Inputs ----
    page : FigurePage
        The page as it is.
    plot : PagePlot
        The plot to place.

    ---- Globals read ----
    GRID_COLUMNS, GRID_ROWS, PLOT_TYPES, REMOVED_TYPES.

    ---- Outputs ----
    Optional[str]
        One plain sentence, or None when the plot fits.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _cells_lister
    panel_letters_finder
    """

    if plot.plot_type in REMOVED_TYPES:
        return REMOVED_TYPES[plot.plot_type]
    if plot.plot_type not in PLOT_TYPES:
        return f'There is no plot type {plot.plot_type!r}.'
    whole_numbers = (plot.row, plot.column, plot.n_rows, plot.n_columns)
    if not all(isinstance(n, int) and not isinstance(n, bool) for n in whole_numbers):
        return 'A plot takes whole grid cells.'
    if (plot.n_rows < 1
            or plot.n_columns < 1
            or plot.row < 0
            or plot.column < 0
            or plot.row + plot.n_rows > GRID_ROWS
            or plot.column + plot.n_columns > GRID_COLUMNS):
        return (f'That rectangle goes past the edge of the page: keep it inside the '
                f'{GRID_ROWS} × {GRID_COLUMNS} grid.')
    cells = _cells_lister(plot)
    letters = panel_letters_finder(page)
    for index, other in enumerate(page.plots):
        if cells & _cells_lister(other):
            name = PLOT_TYPES[other.plot_type]
            return (f'That rectangle covers plot {letters[index]} ({name}): drag over '
                    f'free cells only.')
    return None


# ---- DRAWING HELPERS -----------------------------------------------------------------


# ---- _drawing_space_drawer -----------------------------------------------------------
def _drawing_space_drawer(fig: Figure,
                          room: Tuple[float, float, float, float],
                          plot: PagePlot,
                          context: dict,
                          ) -> List[Axes]:
    """
    ---- Summary ----
    Helper function to draw a Space for a drawing: nothing, so the cells stay empty
    under their letter for a drawing added later in a drawing program.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS); not used.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Axes]
        One set of axes over the room, switched off: it draws nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    ax.set_axis_off()
    return [ax]


# ---- _plot_finisher ------------------------------------------------------------------
def _plot_finisher(fig: Figure,
                   axes: List[Axes],
                   room: Tuple[float, float, float, float],
                   context: dict,
                   ) -> None:
    """
    ---- Summary ----
    Helper function to finish a plot drawn into its room: its axes are made smaller
    until their tick numbers and axis titles are inside the room, each set of axes
    with more than one named line or colour and no legend yet gets its own small
    legend where it hides nothing, and the axes are fitted again for a legend that
    went under them.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    axes : List[Axes]
        The axes of the plot, as its drawer gave them.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' and 'fonts' are used.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Moves the axes and draws the legends (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    axes_room_fitter
    plot_legend_placer
    """

    shown = [ax for ax in axes if ax.axison]
    if not shown:
        return
    axes_room_fitter(fig, shown, room)
    for ax in shown:
        if ax.get_legend() is None:
            plot_legend_placer(fig, ax, context['style'], context['fonts'])
    axes_room_fitter(fig, shown, room)


# ---- _stand_in_drawer ----------------------------------------------------------------
def _stand_in_drawer(fig: Figure,
                     room: Tuple[float, float, float, float],
                     plot: PagePlot,
                     context: dict,
                     ) -> List[Axes]:
    """
    ---- Summary ----
    Helper function to draw the stand-in of a plot type that is not built yet: a grey
    box over its room with the name of the plot type.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'spec' and 'fonts' are used.

    ---- Globals read ----
    PLOT_TYPES, STAND_IN_EDGE, STAND_IN_GREY.

    ---- Outputs ----
    List[Axes]
        The axes of the grey box.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    spec = context['spec']
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    ax.set_facecolor(STAND_IN_GREY)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(STAND_IN_EDGE)
    ax.text(0.5,
            0.5,
            PLOT_TYPES[plot.plot_type],
            ha='center',
            va='center',
            fontsize=spec.get('font_max_pt') or spec['font_min_pt'],
            fontfamily=context['fonts'],
            transform=ax.transAxes,
            )
    return [ax]


# ---- TEMPLATE HELPERS ----------------------------------------------------------------


# ---- _roles_checker ------------------------------------------------------------------
def _roles_checker(roles: Any) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to check the roles of a plot: names and values in words, and no
    value that is a file of the dataset, so a template can be used on another dataset.

    ---- Inputs ----
    roles : Any
        The roles, as given or as read from a file.

    ---- Globals read ----
    FILE_NAME_PATTERN.

    ---- Outputs ----
    Optional[str]
        One plain sentence, or None when the roles can be kept.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not isinstance(roles, dict):
        return 'The roles of a plot must be a list of names and values.'
    for name, value in roles.items():
        if not isinstance(name, str) or not isinstance(value, str):
            return 'The roles of a plot must be names and values in words.'
        if FILE_NAME_PATTERN.search(value):
            return (f'The role {name!r} names a file ({value}); a template keeps '
                    f'roles such as "Group 1, first label", so it fits any dataset.')
    return None


# ---- _template_plot_reader -----------------------------------------------------------
def _template_plot_reader(entry: Any) -> PagePlot:
    """
    ---- Summary ----
    Helper function to read one plot of a template file.

    ---- Inputs ----
    entry : Any
        The plot as read from the file: {"type", "cells": {"row", "column", "rows",
        "columns"}, "roles"}.

    ---- Globals read ----
    None.

    ---- Outputs ----
    PagePlot
        The plot. Raises FigurePageError with one plain sentence when it cannot be
        read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _roles_checker
    """

    if not isinstance(entry, dict) or not isinstance(entry.get('cells'), dict):
        raise FigurePageError('One of its plots has no cells.')
    cells = entry['cells']
    problem = _roles_checker(entry.get('roles', {}))
    if problem:
        raise FigurePageError(problem)
    return PagePlot(plot_type=str(entry.get('type')),
                    row=cells.get('row'),
                    column=cells.get('column'),
                    n_rows=cells.get('rows'),
                    n_columns=cells.get('columns'),
                    roles=dict(entry.get('roles', {})),
                    )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- figure_file_namer ---------------------------------------------------------------
def figure_file_namer(journal: str) -> str:
    """
    ---- Summary ----
    Main function to name the PDF of the dataset figure for a journal.

    ---- Inputs ----
    journal : str
        The journal as the settings name it (a key of config.JOURNAL_SPECS).

    ---- Globals read ----
    FIGURE_NAME.

    ---- Outputs ----
    str
        'dataset_figure_<journal>.pdf', cleaned by the rule every file name goes
        through.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    """

    return f"{file_name_sanitiser(f'{FIGURE_NAME}_{journal}')}.pdf"


# ---- figure_page_drawer --------------------------------------------------------------
def figure_page_drawer(page: FigurePage,
                       spec: dict,
                       setup: Optional[dict] = None,
                       experiments: Optional[Dict[str, dict]] = None,
                       answers: Optional[dict] = None,
                       ) -> Tuple[Figure, Dict[int, Axes]]:
    """
    ---- Summary ----
    Main function to draw a page at its printed size, off screen: each plot drawn by
    its plot type into the cells it takes, the plots of a plot type put on the same
    scales where it asks for that, then room kept inside the cells for each plot's
    own text and legend, and its letter in bold at its top left. A plot type that is
    not built yet is a grey stand-in with its name; a Space for a drawing is empty.

    ---- Inputs ----
    page : FigurePage
        The page.
    spec : dict
        What the page's journal asks (config.JOURNAL_SPECS entry).
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md), for the plots that show
        experiments; None for none.
    experiments : Optional[Dict[str, dict]]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md); None for
        none.
    answers : Optional[dict]
        The answers of the run (config.DEFAULT_ANSWERS), for the plots drawn as the
        run was set up; None for none.

    ---- Globals read ----
    EMPTY_TYPES, GRID_COLUMNS, GRID_ROWS, MM_PER_INCH, PLOT_DRAWERS, PLOT_GAP_MM,
    SCALE_SHARERS; FALLBACK_FONTS (imported).

    ---- Outputs ----
    Tuple[Figure, Dict[int, Axes]]
        (the figure, {place of the plot in page.plots: its axes, the first when it
        has several}). Raises ValueError for a width the journal does not have or a
        height outside (0, 1].

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A plot of cells (row r, column c, n_rows, n_columns) covers the figure fractions
    x from c / 6 to (c + n_columns) / 6 and y from 1 - (r + n_rows) / 6 to 1 - r / 6;
    its room is that rectangle less PLOT_GAP_MM on each side and the height of its
    letter at the top. A stand-in fills its room; the axes of a plot that is drawn
    are made smaller until their text is inside it (axes_room_fitter).

    ---- Helpers ----
    _drawing_space_drawer
    _plot_finisher
    _stand_in_drawer
    figure_size_calculator
    figure_style_builder
    font_family_lister
    panel_letters_finder
    """

    # ---- 1 Make the page at its printed size -----------------------------------------
    width_in, height_in = figure_size_calculator(spec, page.columns, page.height)
    fig = Figure(figsize=(width_in, height_in))
    # the journal's font, then the ones that draw what it lacks (a subscript, a
    # raised minus), so no character of a label is an empty box
    fonts = font_family_lister(list(spec.get('font_family') or []), FALLBACK_FONTS)
    letter_pt = spec['panel_letter_pt']
    case = spec.get('panel_letter_case', 'lower')
    gap_x = PLOT_GAP_MM / MM_PER_INCH / width_in
    gap_y = PLOT_GAP_MM / MM_PER_INCH / height_in
    letter_y = 1.4 * letter_pt / 72.0 / height_in
    context = {'spec': spec,
               'style': figure_style_builder(spec),
               'fonts': fonts,
               'setup': setup,
               'experiments': experiments or {},
               'answers': answers or {},
               'page': page,
               }
    drawers = dict({key: _drawing_space_drawer for key in EMPTY_TYPES}, **PLOT_DRAWERS)

    # ---- 2 Draw each plot and its letter ---------------------------------------------
    letters = panel_letters_finder(page)
    axes = {}
    drawn_plots: List[Tuple[PagePlot, List[Axes], tuple]] = []
    for index, plot in enumerate(page.plots):
        left = plot.column / GRID_COLUMNS
        top = 1 - plot.row / GRID_ROWS
        width = plot.n_columns / GRID_COLUMNS
        height = plot.n_rows / GRID_ROWS
        room = (left + gap_x,
                top - height + gap_y,
                left + width - gap_x,
                top - gap_y - letter_y,
                )
        drawer = drawers.get(plot.plot_type)
        if drawer is None:
            drawn = _stand_in_drawer(fig, room, plot, context)
        else:
            drawn = drawer(fig, room, plot, context)
            drawn_plots.append((plot, drawn, room))
        axes[index] = drawn[0]
        letter = letters[index]
        fig.text(left + gap_x,
                 top - gap_y,
                 letter.upper() if case == 'upper' else letter,
                 ha='left',
                 va='top',
                 fontsize=letter_pt,
                 fontweight='bold',
                 fontfamily=fonts,
                 )

    # ---- 3 Share the scales, then fit the text of each plot --------------------------
    # The scales come first: a changed range changes the tick numbers, and with them
    # the room the text needs.
    for plot_type, sharer in SCALE_SHARERS.items():
        same = [(plot, drawn)
                for plot, drawn, _ in drawn_plots
                if plot.plot_type == plot_type
                ]
        if len(same) > 1:
            sharer(same, context)
    for _, drawn, room in drawn_plots:
        _plot_finisher(fig, drawn, room, context)
    return fig, axes


# ---- figure_page_exporter ------------------------------------------------------------
def figure_page_exporter(page: FigurePage,
                         spec: dict,
                         folder: Path,
                         setup: Optional[dict] = None,
                         experiments: Optional[Dict[str, dict]] = None,
                         answers: Optional[dict] = None,
                         ) -> Tuple[Path, Figure]:
    """
    ---- Summary ----
    Main function to save a page as a PDF of exactly its printed size: drawn as lines
    and text, not as a picture, with its fonts embedded so the text can still be
    changed in a drawing program.

    ---- Inputs ----
    page : FigurePage
        The page; it must hold at least one plot.
    spec : dict
        What the page's journal asks (config.JOURNAL_SPECS entry).
    folder : Path
        Folder the PDF is saved in; it is made when missing.
    setup : Optional[dict]
        The set-up table, as for figure_page_drawer.
    experiments : Optional[Dict[str, dict]]
        The slim copy of each experiment, as for figure_page_drawer.
    answers : Optional[dict]
        The answers of the run, as for figure_page_drawer.

    ---- Globals read ----
    PDF_FONT_TYPE.

    ---- Outputs ----
    Tuple[Path, Figure]
        (the PDF that was saved, the figure as drawn, for its master page). Raises
        FigurePageError for a page with no plot, and OSError when the PDF cannot be
        written (a PermissionError when it is open in another program).

    ---- Globals mutated ----
    None. Writes the PDF (side effect).

    ---- Equations ----
    The PDF's page is the figure: width of the journal for the page's columns, height
    the page's share of the journal's tallest figure (figure_size_calculator), in
    points of 1/72 in.

    ---- Helpers ----
    figure_file_namer
    figure_page_drawer
    """

    if not page.plots:
        raise FigurePageError('The page has no plot on it, so there is no figure to '
                              'save.',
                              )
    fig, _ = figure_page_drawer(page, spec, setup, experiments, answers)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / figure_file_namer(page.journal)
    with matplotlib.rc_context({'pdf.fonttype': PDF_FONT_TYPE}):
        fig.savefig(path, format='pdf')
    return path, fig


# ---- page_plainer --------------------------------------------------------------------
def page_plainer(page: FigurePage) -> dict:
    """
    ---- Summary ----
    Main function to write a page as plain values, the form it has in a template file
    and in the settings file of a dataset: its size, and each plot's type, cells and
    roles.

    ---- Inputs ----
    page : FigurePage
        The page.

    ---- Globals read ----
    TEMPLATE_KIND, TEMPLATE_VERSION.

    ---- Outputs ----
    dict
        {'kind', 'version', 'journal', 'columns', 'height', 'plots': [{'type',
        'cells': {'row', 'column', 'rows', 'columns'}, 'roles'}]} (plain_page,
        DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {'kind': TEMPLATE_KIND,
            'version': TEMPLATE_VERSION,
            'journal': page.journal,
            'columns': page.columns,
            'height': page.height,
            'plots': [{'type': plot.plot_type,
                       'cells': {'row': plot.row,
                                 'column': plot.column,
                                 'rows': plot.n_rows,
                                 'columns': plot.n_columns,
                                 },
                       'roles': dict(plot.roles),
                       }
                      for plot in page.plots
                      ],
            }


# ---- panel_letters_finder------------------------------------------------------------


# ---- panel_letters_finder ------------------------------------------------------------
def panel_letters_finder(page: FigurePage) -> Dict[int, str]:
    """
    ---- Summary ----
    Main function to give each plot of a page its letter, a, b, c... in reading order:
    by the top left cell of each plot, left to right along a row of the grid, then the
    next row down.

    ---- Inputs ----
    page : FigurePage
        The page.

    ---- Globals read ----
    LETTERS.

    ---- Outputs ----
    Dict[int, str]
        {place of the plot in page.plots: its letter, in lower case}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    lettered = sorted(range(len(page.plots)),
                      key=lambda index: (page.plots[index].row,
                                         page.plots[index].column,
                                         ),
                      )
    return {index: LETTERS[place % len(LETTERS)]
            for place, index in enumerate(lettered)
            }


# ---- plain_page_reader ---------------------------------------------------------------
def plain_page_reader(content: Any, start: str) -> FigurePage:
    """
    ---- Summary ----
    Main function to read a page from its plain values (page_plainer), as a template
    file or the settings file of a dataset holds them.

    ---- Inputs ----
    content : Any
        The plain values as read from the file (plain_page, DATA_FORMAT.md).
    start : str
        How the sentence for a page that cannot be read starts ('The template
        bars.json cannot be used').

    ---- Globals read ----
    TEMPLATE_KIND, TEMPLATE_VERSION.

    ---- Outputs ----
    FigurePage
        The page. Raises FigurePageError with one plain sentence when the values are
        not a page saved by Portimao, are of a version this program does not know, or
        hold a plot that cannot be placed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _template_plot_reader
    plot_placer
    """

    # ---- 1 Check what it is ----------------------------------------------------------
    if not isinstance(content, dict) or content.get('kind') != TEMPLATE_KIND:
        raise FigurePageError(f'{start}: it is not a template saved by Portimao.')
    if content.get('version') != TEMPLATE_VERSION:
        raise FigurePageError(f'{start}: it was saved by another version of Portimao.')

    # ---- 2 Check the page size -------------------------------------------------------
    journal = content.get('journal')
    columns = content.get('columns')
    height = content.get('height')
    numbers_ok = all(isinstance(n, (int, float)) and not isinstance(n, bool)
                     for n in (columns, height)
                     )
    if not isinstance(journal, str) or not numbers_ok or not 0 < height <= 1:
        raise FigurePageError(f'{start}: its page size cannot be read.')

    # ---- 3 Place each plot -----------------------------------------------------------
    if not isinstance(content.get('plots'), list):
        raise FigurePageError(f'{start}: it has no list of plots.')
    page = FigurePage(journal=journal, columns=columns, height=height)
    for entry in content['plots']:
        try:
            page = plot_placer(page, _template_plot_reader(entry))
        except FigurePageError as exc:
            raise FigurePageError(f'{start}. {exc}') from exc
    return page


# ---- plot_lifter---------------------------------------------------------------------


# ---- plot_lifter ---------------------------------------------------------------------
def plot_lifter(page: FigurePage, index: int) -> Tuple[FigurePage, PagePlot]:
    """
    ---- Summary ----
    Main function to take a plot off a page, so its cells are free again: to be placed
    again elsewhere (✎, with plot_placer and the new cells) or put back (Cancel).

    ---- Inputs ----
    page : FigurePage
        The page.
    index : int
        Place of the plot in page.plots.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[FigurePage, PagePlot]
        (the page without the plot, the plot with its type and roles kept). Raises
        IndexError for a plot that is not on the page.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not 0 <= index < len(page.plots):
        raise IndexError(f'There is no plot {index} on the page.')
    plots = page.plots[:index] + page.plots[index + 1:]
    return replace(page, plots=plots), page.plots[index]


# ---- plot_placer ---------------------------------------------------------------------
def plot_placer(page: FigurePage, plot: PagePlot) -> FigurePage:
    """
    ---- Summary ----
    Main function to put a plot on a page, as a rectangle of grid cells that none of
    the other plots take.

    ---- Inputs ----
    page : FigurePage
        The page.
    plot : PagePlot
        The plot, with its cells.

    ---- Globals read ----
    None.

    ---- Outputs ----
    FigurePage
        The page with the plot added last. Raises FigurePageError with one plain
        sentence for an unknown plot type, a rectangle past the grid or one over
        another plot.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _placement_problem_finder
    """

    problem = _placement_problem_finder(page, plot)
    if problem:
        raise FigurePageError(problem)
    return replace(page, plots=page.plots + (plot,))


# ---- plot_remover --------------------------------------------------------------------
def plot_remover(page: FigurePage, index: int) -> FigurePage:
    """Main function to take a plot off a page for good (✕). See plot_lifter."""

    return plot_lifter(page, index)[0]


# ---- template_path_finder ------------------------------------------------------------
def template_path_finder(folder: Path, name: str) -> Path:
    """
    ---- Summary ----
    Main function to give the file a template of a given name is saved in, so the
    window can ask before one of the same name is written over.

    ---- Inputs ----
    folder : Path
        The layouts folder (UserPlaces.layouts_folder).
    name : str
        The template's name as the user typed it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        <folder>/<name, made safe for a file name>.json.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    """

    return folder / f'{file_name_sanitiser(name, "figure")}.json'


# ---- template_reader -----------------------------------------------------------------
def template_reader(path: Path) -> FigurePage:
    """
    ---- Summary ----
    Main function to read a template file into a page.

    ---- Inputs ----
    path : Path
        The template file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    FigurePage
        The page. Raises FigurePageError with one plain sentence when the file cannot
        be read, is not a template of a version this program knows, or holds a plot
        that cannot be placed; OSError passes through.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    plain_page_reader
    """

    start = f'The template {path.name} cannot be used'
    try:
        content = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise FigurePageError(f'{start}: it is not a template saved by Portimao.',
                              ) from exc
    return plain_page_reader(content, start)


# ---- template_saver ------------------------------------------------------------------
def template_saver(page: FigurePage,
                   folder: Path,
                   name: str,
                   may_replace: bool = False,
                   ) -> Path:
    """
    ---- Summary ----
    Main function to save a page as a template: its size, and each plot's type, cells
    and roles, never a file of the dataset, so it can be used on another dataset.

    ---- Inputs ----
    page : FigurePage
        The page.
    folder : Path
        The layouts folder (UserPlaces.layouts_folder); made when missing.
    name : str
        The template's name as the user typed it.
    may_replace : bool
        True to write over a template of the same name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The file written, <folder>/<name>.json. Raises FigurePageError with one plain
        sentence for a role that names a file, or a template of that name already
        there without may_replace; OSError passes through.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _roles_checker
    page_plainer
    template_path_finder
    """

    # ---- 1 Check the roles -----------------------------------------------------------
    for plot in page.plots:
        problem = _roles_checker(plot.roles)
        if problem:
            raise FigurePageError(f'The template is not saved. {problem}')

    # ---- 2 Write the file ------------------------------------------------------------
    path = template_path_finder(folder, name)
    if path.exists() and not may_replace:
        raise FigurePageError(f'A template called {path.stem} is already there: '
                              f'choose another name, or replace it.',
                              )
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(page_plainer(page), indent=2, ensure_ascii=False) + '\n',
                    encoding='utf-8',
                    )
    return path
