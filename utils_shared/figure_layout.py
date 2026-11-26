"""
Journal-aware figure sizing and automatic layout.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import math
from typing import Any, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import Collection
from matplotlib.figure import Figure
from matplotlib.font_manager import findfont, FontProperties
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.textpath import TextPath
from matplotlib.transforms import Bbox, ScaledTranslation


# ---- CONSTANTS -----------------------------------------------------------------------
MM_PER_INCH = 25.4
POINTS_PER_INCH = 72.0
# A plot is fitted into its room (axes_room_fitter) in a few passes, as the tick
# numbers can change when the axes shrink; it stops once nothing sticks out by more
# than FIT_TOLERANCE of the figure, and never shrinks the axes under SMALLEST_AXES of
# the room.
FIT_PASSES = 4
FIT_TOLERANCE = 1e-4
SMALLEST_AXES = 0.2
# The corners a small legend is tried in, in this order, the columns it has when it
# goes under the axes, and the points along each piece of a line that are checked
# against the legend
LEGEND_CORNERS = ('upper right', 'upper left', 'lower right', 'lower left')
LEGEND_COLUMNS = 3
LINE_CHECK_POINTS = 8
# The attribute of something drawn faintly behind a plot (a haem band): a legend may
# sit over it, as it hides nothing there
BACKDROP_MARK = 'is_backdrop'
# The fonts every figure names after the journal's own: a character the journal's font
# lacks (Arial has no subscripts and no raised minus) is drawn in the first of these
# that has it, in place of an empty box
FALLBACK_FONTS = ('Liberation Sans', 'DejaVu Sans')
# How the name of a font collection file ends (several fonts in one file). A figure
# never names a font kept in one: on a Mac, Helvetica is, and a text with a raised
# minus or a subscript drawn in it stops the drawing ("failed to load glyph")
COLLECTION_ENDINGS = ('.ttc', '.otc', '.dfont')
# what the user is told each text size of the figures is (figure_style_builder's
# 'fonts'), in the warning about a journal's text sizes; panel letters follow the journal
TEXT_NAMES = {'tick': 'tick labels and legends',
              'label': 'axis titles',
              'title': 'panel titles',
              }


# ---- FIGURE LAYOUT HELPERS -----------------------------------------------------------


# ---- _installed_fonts_lister ---------------------------------------------------------
def _installed_fonts_lister(families: Sequence[str]) -> List[str]:
    """
    ---- Summary ----
    Helper function to list the font names that are on this computer and that a
    figure can be drawn in.

    ---- Inputs ----
    families : Sequence[str]
        Font names.

    ---- Globals read ----
    COLLECTION_ENDINGS (module constant). Reads the list of installed fonts (side
    effect).

    ---- Outputs ----
    List[str]
        The names that are installed, in the order given; a name given twice is
        kept once. A font kept in a collection file is left out, as the plotting
        library cannot draw every figure in one.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    installed = []
    for family in dict.fromkeys(families):
        try:
            path = findfont(family, fallback_to_default=False)
        except ValueError:  # that font is not on this computer
            continue
        if str(path).lower().endswith(COLLECTION_ENDINGS):
            continue
        installed.append(family)
    return installed


# ---- _renderer_getter ----------------------------------------------------------------
def _renderer_getter(fig: Figure) -> Any:
    """
    ---- Summary ----
    Helper function to get the renderer of a figure canvas.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Any
        Matplotlib renderer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        return fig.canvas.get_renderer()
    except AttributeError:
        return fig._get_renderer()


# ---- _legend_cover_checker -----------------------------------------------------------
def _legend_cover_checker(ax: Axes, box: Bbox, renderer: Any) -> bool:
    """
    ---- Summary ----
    Helper function to check whether a rectangle of the figure covers anything drawn
    in a set of axes: a line, a bar or other patch, or a filled band. What is marked
    as a backdrop (a faint haem band behind the lines) does not count.

    ---- Inputs ----
    ax : Axes
        The axes.
    box : Bbox
        The rectangle (of a legend), in pixels of the figure.
    renderer : Any
        The renderer of the figure.

    ---- Globals read ----
    BACKDROP_MARK, LINE_CHECK_POINTS.

    ---- Outputs ----
    bool
        True when the rectangle covers a part of something drawn.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Each piece of a line, between two of its points, is checked at
    LINE_CHECK_POINTS places evenly spaced along it; a patch or a band is checked by
    the rectangle round it.

    ---- Helpers ----
    None.
    """

    # ---- 1 The lines -----------------------------------------------------------------
    shares = np.linspace(0.0, 1.0, LINE_CHECK_POINTS)
    for line in ax.lines:
        if not line.get_visible():
            continue
        points = line.get_transform().transform(np.asarray(line.get_xydata(),
                                                           dtype=float,
                                                           ),
                                                )
        points = points[np.isfinite(points).all(axis=1)]
        if len(points) == 0:
            continue
        if len(points) > 1:
            starts, steps = points[:-1], np.diff(points, axis=0)
            points = (starts[:, None, :] + steps[:, None, :] * shares[None, :, None]
                      ).reshape(-1, 2)
        is_inside = ((points[:, 0] >= box.x0)
                     & (points[:, 0] <= box.x1)
                     & (points[:, 1] >= box.y0)
                     & (points[:, 1] <= box.y1)
                     )
        if is_inside.any():
            return True

    # ---- 2 The bars and the bands ----------------------------------------------------
    for artist in list(ax.patches) + list(ax.collections):
        if getattr(artist, BACKDROP_MARK, False):
            continue
        if artist.get_visible() and box.overlaps(artist.get_window_extent(renderer)):
            return True
    return False


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- axes_room_fitter ----------------------------------------------------------------
def axes_room_fitter(fig: Figure,
                     axes: List[Axes],
                     room: Tuple[float, float, float, float],
                     ) -> None:
    """
    ---- Summary ----
    Main function to fit the axes of one plot into its room on a page: the axes are
    made smaller until their tick numbers, axis titles and legend are all inside the
    room, so none of the plot's text falls into the cells of another plot.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    axes : List[Axes]
        The axes of the plot, already drawn into; several keep their places beside
        one another.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room, as fractions of the figure.

    ---- Globals read ----
    FIT_PASSES, FIT_TOLERANCE, SMALLEST_AXES.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Moves the axes (side effect).

    ---- Equations ----
    With (L, B, R, T) how far the text sticks out of the room at the left, bottom,
    right and top, the rectangle round all the axes (x0, y0, x1, y1) becomes
    (x0 + L, y0 + B, x1 - R, y1 - T), never narrower or lower than SMALLEST_AXES of
    the room, and each axes keeps its share of it. It is done again, at most
    FIT_PASSES times, until nothing sticks out.

    ---- Helpers ----
    _renderer_getter
    """

    if not axes:
        return
    renderer = _renderer_getter(fig)
    x0, y0, x1, y1 = room
    for _ in range(FIT_PASSES):
        # ---- 1 How far the text sticks out -------------------------------------------
        boxes = [ax.get_tightbbox(renderer) for ax in axes]
        boxes = [box for box in boxes if box is not None]
        if not boxes:
            return
        tight = Bbox.union(boxes).transformed(fig.transFigure.inverted())
        over = (max(x0 - tight.x0, 0.0),
                max(y0 - tight.y0, 0.0),
                max(tight.x1 - x1, 0.0),
                max(tight.y1 - y1, 0.0),
                )
        if max(over) < FIT_TOLERANCE:
            return

        # ---- 2 The axes made smaller by that much ------------------------------------
        old = Bbox.union([ax.get_position() for ax in axes])
        width = max(old.width - over[0] - over[2], SMALLEST_AXES * (x1 - x0))
        height = max(old.height - over[1] - over[3], SMALLEST_AXES * (y1 - y0))
        left = min(old.x0 + over[0], x1 - width)
        bottom = min(old.y0 + over[1], y1 - height)
        for ax in axes:
            place = ax.get_position()
            ax.set_position(((left + (place.x0 - old.x0) / old.width * width),
                             (bottom + (place.y0 - old.y0) / old.height * height),
                             place.width / old.width * width,
                             place.height / old.height * height,
                             ),
                            )


# ---- figure_canvas_fitter ------------------------------------------------------------
def figure_canvas_fitter(fig: Figure,
                         pad_pt: float,
                         suptitle: Optional[Any] = None,
                         suptitle_gap_pt: float = 0.0,
                         iterations: int = 8,
                         tolerance_pt: float = 0.2,
                         line_limits_pt: Optional[Tuple[Optional[float],
                                                        Optional[float],
                                                        ]] = None,
                         ) -> None:
    """
    ---- Summary ----
    Main function to set the figure margins so that everything drawn sits a fixed
    padding inside the figure edge, whatever the figure size, font size or label
    lengths. Every figure is fitted here before it is shown or saved, so this is also
    where its lines are kept to the widths the journal takes.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    pad_pt : float
        Whitespace between the content and the figure edge in points.
    suptitle : Optional[Any]
        Optional figure title (Text from fig.suptitle); it is placed pad_pt below the
        top edge.
    suptitle_gap_pt : float
        Gap between the title and the content in points.
    iterations : int
        Maximum number of fitting passes.
    tolerance_pt : float
        Stop when no margin moves by more than this many points.
    line_limits_pt : Optional[Tuple[Optional[float], Optional[float]]]
        (thinnest, thickest) line the journal takes in points, as in
        figure_style_builder()['line_limits']; None to leave the lines as drawn.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing; the figure margins are changed in place. Raises ValueError when the
        contents leave no room for the axes.

    ---- Globals mutated ----
    None. Changes the line widths and the subplot margins of ``fig`` and the layout
    flag and position of ``suptitle`` (side effect).

    ---- Equations ----
    Each margin = (pad + width of the decoration outside the axes) / figure size,
    repeated until the largest change is below tolerance_pt.

    ---- Helpers ----
    _renderer_getter
    figure_lines_fitter
    """

    # ---- 0 Keep the lines to the journal's widths ------------------------------------
    if line_limits_pt is not None:
        figure_lines_fitter(fig, *line_limits_pt)

    # ---- 1 Measure the figure --------------------------------------------------------
    width_pt, height_pt = (float(v) * 72.0 for v in fig.get_size_inches())
    renderer = _renderer_getter(fig)
    scale = 72.0 / fig.dpi
    top_limit = height_pt - pad_pt
    if suptitle is not None:
        suptitle.set_in_layout(False)
        suptitle.set_va('top')
        suptitle.set_y(1.0 - pad_pt / height_pt)
        title_height = suptitle.get_window_extent(renderer).height * scale
        top_limit = height_pt - pad_pt - title_height - suptitle_gap_pt

    # ---- 2 Fit the margins -----------------------------------------------------------
    for _ in range(iterations):
        box = fig.get_tightbbox(renderer)
        params = fig.subplotpars
        left_deco = params.left * width_pt - box.x0 * 72.0
        right_deco = box.x1 * 72.0 - params.right * width_pt
        bottom_deco = params.bottom * height_pt - box.y0 * 72.0
        top_deco = box.y1 * 72.0 - params.top * height_pt
        left = (pad_pt + left_deco) / width_pt
        right = (width_pt - pad_pt - right_deco) / width_pt
        bottom = (pad_pt + bottom_deco) / height_pt
        top = (top_limit - top_deco) / height_pt
        if not (0 <= left < right <= 1 and 0 <= bottom < top <= 1):
            raise ValueError('The figure is too small for its contents (labels, ticks '
                             'and gaps leave no room for the axes). '
                             'Use a larger figure, a smaller font size or less '
                             'spacing.',
                             )
        change = max(abs(left - params.left) * width_pt,
                     abs(right - params.right) * width_pt,
                     abs(bottom - params.bottom) * height_pt,
                     abs(top - params.top) * height_pt,
                     )
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        if change < tolerance_pt:
            break

    # ---- 3 Keep the title in the layout ----------------------------------------------
    if suptitle is not None:
        suptitle.set_in_layout(True)


# ---- figure_finisher -----------------------------------------------------------------
def figure_finisher(fig: Figure,
                    config: dict,
                    panels: list,
                    suptitle: Any,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to fit the margins to the drawn content, add the panel letters at
    the top-left of each panel and fit again.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    config : dict
        Figure settings dictionary (plot_config_builder, config.py).
    panels : list
        List of (letter, main axes, [axes of the panel]) tuples.
    suptitle : Any
        Figure title text object, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Resizes the layout of ``fig`` and adds text to it (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_canvas_fitter
    panel_letter_adder
    """

    pad, gap = config['EDGE_PAD_PT'], config['TITLE_GAP_PT']
    limits = config.get('LINE_LIMITS_PT')
    figure_canvas_fitter(fig, pad, suptitle, gap, line_limits_pt=limits)
    if config['PANEL_LETTERS'] and panels:
        panel_letter_adder(fig,
                           panels,
                           config['PANEL_LETTER_FONT_SIZE'],
                           config['PANEL_LETTER_CASE'],
                           )
        figure_canvas_fitter(fig, pad, suptitle, gap, line_limits_pt=limits)


# ---- figure_lines_fitter -------------------------------------------------------------
def figure_lines_fitter(fig: Figure,
                        thinnest_pt: Optional[float],
                        thickest_pt: Optional[float],
                        ) -> int:
    """
    ---- Summary ----
    Main function to keep every line drawn in a figure between the thinnest and the
    thickest line a journal takes, whatever width it was drawn with: the data lines,
    the axes and their ticks, the edges of markers, boxes, shadings and legends. A
    width of 0 (no line) is left alone.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure, with everything drawn in it.
    thinnest_pt : Optional[float]
        Thinnest line the journal takes in points; None when it gives none.
    thickest_pt : Optional[float]
        Thickest line the journal takes in points; None when it gives none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        How many widths were changed.

    ---- Globals mutated ----
    None. Changes the line widths of ``fig`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    line_width_fitter
    """

    if thinnest_pt is None and thickest_pt is None:
        return 0
    changed = 0
    for artist in fig.findobj():
        # ---- 1 Lines: their own width, and the edge of their markers (the ticks) -----
        if isinstance(artist, Line2D):
            for getter, setter in ((artist.get_linewidth, artist.set_linewidth),
                                   (artist.get_markeredgewidth,
                                    artist.set_markeredgewidth,
                                    ),
                                   ):
                width = float(getter())
                fitted = line_width_fitter(width, thinnest_pt, thickest_pt)
                if fitted != width:
                    setter(fitted)
                    changed += 1

        # ---- 2 Groups of lines and shapes: one width each ----------------------------
        elif isinstance(artist, Collection):
            widths = [float(width) for width in artist.get_linewidths()]
            fitted = [line_width_fitter(width, thinnest_pt, thickest_pt)
                      for width in widths
                      ]
            if fitted != widths:
                artist.set_linewidths(fitted)
                changed += 1

        # ---- 3 Shapes: the width of their edge ---------------------------------------
        elif isinstance(artist, Patch):
            width = float(artist.get_linewidth())
            fitted = line_width_fitter(width, thinnest_pt, thickest_pt)
            if fitted != width:
                artist.set_linewidth(fitted)
                changed += 1
    return changed


# ---- figure_size_calculator ----------------------------------------------------------
def figure_size_calculator(spec: dict,
                           columns: float,
                           height: float,
                           ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to calculate the (width, height) of a figure in inches from a journal
    specification.

    ---- Inputs ----
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    columns : float
        Key of spec["widths_mm"]: 1, 1.5 or 2 columns wide.
    height : float
        Fraction of the journal page height (spec["page_height_mm"]), above 0 and at
        most 1; 0.5 is half a page.

    ---- Globals read ----
    MM_PER_INCH (module constant).

    ---- Outputs ----
    Tuple[float, float]
        (width, height) in inches. Raises ValueError for an unknown column count or a
        height outside (0, 1].

    ---- Globals mutated ----
    None.

    ---- Equations ----
    width_in = widths_mm[columns] / 25.4; height_in = page_height_mm x height / 25.4.

    ---- Helpers ----
    None.
    """

    widths = spec['widths_mm']
    if columns not in widths:
        raise ValueError(f'columns must be one of {sorted(widths)}; got {columns!r}.')
    if not 0 < height <= 1:
        raise ValueError(f'height is a fraction of the page height (0 < height <= 1); '
                         f'got {height!r}.',
                         )
    return widths[columns] / MM_PER_INCH, spec['page_height_mm'] * height / MM_PER_INCH


# ---- figure_style_builder ------------------------------------------------------------
def figure_style_builder(spec: dict,
                         base_font_pt: float = 6.0,
                         spacing: float = 1.0,
                         line_width_pt: float = 0.75,
                         ) -> dict:
    """
    ---- Summary ----
    Main function to derive every font size, padding and line width of the figures from
    the journal specification and three master settings.

    ---- Inputs ----
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    base_font_pt : float
        Axis-label size wanted, in points; tick labels are 1 pt smaller and titles 1 pt
        larger. It is moved to fit the journal: at least spec['font_min_pt'] + 1 and,
        where that leaves room, at most spec['font_max_pt'] - 1 (no upper limit for a
        journal whose font_max_pt is None).
    spacing : float
        Tightness of all paddings and gaps: 1.0 is the default, 1.2 is 20 % looser, 0.8
        is 20 % tighter.
    line_width_pt : float
        Width of the data lines in points; axes, reference and event lines are scaled
        from it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Style dictionary with 'fonts' {tick, label, title, panel_letter} and the points
        values unit, tick_length, tick_pad, label_pad, title_pad, edge_pad, title_gap,
        event_label_offset, line_width, axes_line_width and thin_line_width, and
        'line_limits' (thinnest, thickest), the line widths the journal takes in
        points, None where it gives none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    base_font_pt = max(min(base_font_pt, font_max_pt - 1), font_min_pt + 1) (6 pt
    stays 6 for 5 to 7 pt and becomes 7 for 6 to 8 pt);
    unit = base_font_pt x spacing; every padding is a multiple of unit (for example
    title_pad = 0.8 x unit); axes_line_width = 0.65 x line_width_pt; thin_line_width =
    0.5 x line_width_pt; each line width is then kept between the journal's thinnest
    and thickest line (0.75, 0.49 and 0.38 pt become 0.75, 0.5 and 0.5 pt for a
    journal whose thinnest line is 0.5 pt).

    ---- Helpers ----
    line_width_fitter
    """

    # ---- 1 Fit the text to the journal -----------------------------------------------
    # The smallest text is 1 pt under the axis titles and the largest 1 pt over, so the
    # axis titles are moved until both are inside what the journal takes; the paddings
    # follow, as they are multiples of the same size. A journal whose range is narrower
    # than 2 pt keeps its smallest text legal (figure_style_checker names the rest).
    # A journal that gives no largest text only lifts text that is too small.
    low, high = spec['font_min_pt'], spec.get('font_max_pt')
    if high is not None:
        base_font_pt = min(base_font_pt, high - 1.0)
    base_font_pt = max(base_font_pt, low + 1.0)

    # ---- 2 Calculate the base unit ---------------------------------------------------
    unit = base_font_pt * spacing

    # ---- 3 Build the style -----------------------------------------------------------
    limits = (spec.get('line_min_pt'), spec.get('line_max_pt'))
    return {'fonts': {'tick': base_font_pt - 1.0,
                      'label': base_font_pt,
                      'title': base_font_pt + 1.0,
                      'panel_letter': spec['panel_letter_pt'],
                      },
            'unit': unit,  # the padding unit in points
            'tick_length': 0.5 * unit,
            'tick_pad': 0.5 * unit,
            'label_pad': 0.5 * unit,
            'title_pad': 0.8 * unit,
            # whitespace between the content and the edge of the figure
            'edge_pad': 0.5 * unit,
            'title_gap': 1.0 * unit,  # figure title to content
            'event_label_offset': 0.8 * unit,
            'line_width': line_width_fitter(line_width_pt, *limits),
            'axes_line_width': line_width_fitter(round(0.65 * line_width_pt, 3),
                                                 *limits,
                                                 ),
            'thin_line_width': line_width_fitter(round(0.5 * line_width_pt, 3),
                                                 *limits,
                                                 ),
            # the thinnest and the thickest line the journal takes (None: no limit),
            # for the lines drawn with a width of their own (figure_lines_fitter)
            'line_limits': limits,
            }


# ---- figure_style_checker ------------------------------------------------------------
def figure_style_checker(spec: dict, fonts: dict) -> List[str]:
    """
    ---- Summary ----
    Main function to list, one plain sentence each, the kinds of text of the figures
    that are smaller or larger than the journal asks for. The height of a figure needs
    no check: it is chosen as a part of the tallest figure the journal takes.

    ---- Inputs ----
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry); its 'name', 'font_min_pt'
        and 'font_max_pt' are used (a font_max_pt of None: no text is too large).
    fonts : dict
        Font sizes in points keyed by role, as in figure_style_builder()['fonts'].

    ---- Globals read ----
    TEXT_NAMES (module constant).

    ---- Outputs ----
    List[str]
        Warning sentences, in the order of TEXT_NAMES; empty when the text fits the
        journal.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check each kind of text ---------------------------------------------------
    warnings = []
    low, high = spec['font_min_pt'], spec.get('font_max_pt')
    for role, text_name in TEXT_NAMES.items():
        size = fonts[role]
        if size < low:
            warnings.append(f'The {text_name} of the figures ({size:g} pt) are smaller '
                            f"than the {low:g} pt {spec['name']} asks for.",
                            )
        elif high is not None and size > high:
            warnings.append(f'The {text_name} of the figures ({size:g} pt) are larger '
                            f"than the {high:g} pt {spec['name']} allows.",
                            )
    return warnings


# ---- font_family_lister --------------------------------------------------------------
def font_family_lister(families: List[str],
                       fallbacks: Sequence[str] = (),
                       ) -> List[str]:
    """
    ---- Summary ----
    Main function to list the fonts a figure names: the journal's first font that is
    on this computer and can be drawn in, then the fallback fonts that are, so a
    character the journal's font cannot draw (a subscript, a raised minus) is drawn
    in the next one that can.

    ---- Inputs ----
    families : List[str]
        The journal's font names, the wanted one first and its other choices after it.
    fallbacks : Sequence[str]
        The fonts named after the journal's, for the characters it lacks; () for none.

    ---- Globals read ----
    None. Reads the list of installed fonts (side effect).

    ---- Outputs ----
    List[str]
        The journal's first usable font, then the usable fallbacks in their order; a
        name given twice is kept once. A font kept in a collection file is not
        usable (_installed_fonts_lister): on a Mac a journal that asks for
        Helvetica, then Arial, is drawn in Arial, as it is on Windows, where there
        is no Helvetica. The journal's other choices are left out, as text is drawn
        in the first font anyway. ['sans-serif'] when no name is usable, which is
        the plotting library's own font.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installed_fonts_lister
    """

    journal = _installed_fonts_lister(families)[:1]
    named = journal + [family
                       for family in _installed_fonts_lister(fallbacks)
                       if family not in journal
                       ]
    return named or ['sans-serif']


# ---- gap_space_calculator ------------------------------------------------------------
def gap_space_calculator(gap_pt: float, extent_pt: float, n: int) -> float:
    """
    ---- Summary ----
    Main function to calculate the GridSpec wspace or hspace that leaves a given gap
    between equal cells.

    ---- Inputs ----
    gap_pt : float
        Wanted gap between neighbouring cells in points.
    extent_pt : float
        Total width or height covered by the cells and gaps in points.
    n : int
        Number of equal cells.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        GridSpec spacing as a fraction of the average cell size; 0 for a single cell.
        Raises ValueError when the gaps do not fit in extent_pt.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    room = extent_pt - gap_pt x (n - 1); space = gap_pt x n / room.

    ---- Helpers ----
    None.
    """

    if n <= 1:
        return 0.0
    room = extent_pt - gap_pt * (n - 1)
    if room <= 0:
        raise ValueError('The figure is too small for the requested gaps; use a larger'
                         ' figure or a smaller font/spacing.',
                         )
    return gap_pt * n / room


# ---- line_width_fitter ---------------------------------------------------------------
def line_width_fitter(width_pt: float,
                      thinnest_pt: Optional[float],
                      thickest_pt: Optional[float],
                      ) -> float:
    """
    ---- Summary ----
    Main function to keep a line width between the thinnest and the thickest line a
    journal takes.

    ---- Inputs ----
    width_pt : float
        Line width in points; 0 means no line and stays 0.
    thinnest_pt : Optional[float]
        Thinnest line the journal takes in points; None when it gives none.
    thickest_pt : Optional[float]
        Thickest line the journal takes in points; None when it gives none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The width, lifted to thinnest_pt or lowered to thickest_pt where it was
        outside them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    width = min(max(width_pt, thinnest_pt), thickest_pt) for a width above 0 (0.375 pt
    becomes 0.5 pt with a thinnest line of 0.5 pt; 2.6 pt becomes 1.5 pt with a
    thickest line of 1.5 pt).

    ---- Helpers ----
    None.
    """

    if not width_pt > 0:
        return width_pt
    if thinnest_pt is not None:
        width_pt = max(width_pt, thinnest_pt)
    if thickest_pt is not None:
        width_pt = min(width_pt, thickest_pt)
    return width_pt


# ---- panel_letter_adder --------------------------------------------------------------
def panel_letter_adder(fig: Figure,
                       panels: list,
                       font_pt: float,
                       case: str = 'upper',
                       weight: str = 'bold',
                       gap_pt: float = 0.0,
                       ) -> list:
    """
    ---- Summary ----
    Main function to write each panel letter just above the top edge of its panel's
    main axes, to the left of everything the panel draws on that side.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    panels : list
        [(letter, main axes, [axes of the panel]), ...]; a fourth item (text, text
        keyword arguments) adds a small note after the letter.
    font_pt : float
        Letter size in points.
    case : str
        'upper' or 'lower'.
    weight : str
        Matplotlib font weight of the letters.
    gap_pt : float
        Extra gap above the panel in points.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        The annotation artists created. Raises ValueError for an unknown case.

    ---- Globals mutated ----
    None. Adds annotations to the main axes of each panel (side effect); call
    figure_canvas_fitter afterwards so the letters are inside the margins.

    ---- Equations ----
    None.

    ---- Helpers ----
    _renderer_getter
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    if case not in ('upper', 'lower'):
        raise ValueError('The panel letter case must be "upper" or "lower".')

    # ---- 2 Measure the panels --------------------------------------------------------
    renderer = _renderer_getter(fig)
    scale = 72.0 / fig.dpi
    rows = []
    for letter, main, members, *extra in panels:
        boxes = [b
                 for b in (ax.get_tightbbox(renderer) for ax in members)
                 if b is not None
                 ]
        main_box = main.get_window_extent(renderer)
        left = min(b.x0 for b in boxes)
        # Never closer to the axes than one letter width, so a panel with nothing to
        # its left still keeps its letter clear of the axes and the labels above them.
        reach = max((main_box.x0 - left) * scale, 1.3 * font_pt)
        rows.append((letter,
                     main,
                     reach,
                     0.0,
                     round(main_box.x0 / 2.0),
                     extra[0] if extra else None,
                     ),
                    )

    # ---- 3 Align the letters ---------------------------------------------------------
    column_offset = {}
    for _, _, dx, _, key, _ in rows:
        column_offset[key] = max(column_offset.get(key, 0.0), dx)

    # ---- 4 Draw the letters ----------------------------------------------------------
    artists = []
    for letter, main, _, dy, key, note in rows:
        text = letter.lower() if case == 'lower' else letter.upper()
        artists.append(main.annotate(text,
                                     xy=(0, 1),
                                     xycoords='axes fraction',
                                     xytext=(-column_offset[key], dy + gap_pt),
                                     textcoords='offset points',
                                     ha='left',
                                     va='bottom',
                                     fontsize=font_pt,
                                     fontweight=weight,
                                     annotation_clip=False,
                                     ),
                       )
        if note:
            note_text, note_kwargs = note
            artists.append(main.annotate(note_text,
                                         xy=(0, 1),
                                         xycoords='axes fraction',
                                         xytext=(-column_offset[key] + 1.3 * font_pt,
                                                 dy + gap_pt,
                                                 ),
                                         textcoords='offset points',
                                         ha='left',
                                         va='bottom',
                                         annotation_clip=False,
                                         **note_kwargs,
                                         ),
                           )
    return artists


# ---- plot_legend_placer --------------------------------------------------------------
def plot_legend_placer(fig: Figure,
                       ax: Axes,
                       style: dict,
                       fonts: List[str],
                       ) -> Optional[Legend]:
    """
    ---- Summary ----
    Main function to give a plot its own small legend, where it hides nothing: in the
    first corner of the axes where it covers no line, bar or band, and under the axes
    when every corner covers something. A plot with fewer than two named lines or
    colours has no legend.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    ax : Axes
        The axes, already drawn into, with a label on each line or bar to name.
    style : dict
        The style of the figure (figure_style_builder).
    fonts : List[str]
        The font families of the journal (font_family_lister).

    ---- Globals read ----
    LEGEND_COLUMNS, LEGEND_CORNERS, POINTS_PER_INCH.

    ---- Outputs ----
    Optional[Legend]
        The legend, or None when there is none. Under the axes it is outside them, so
        axes_room_fitter is run after it.

    ---- Globals mutated ----
    None. Draws the legend (side effect).

    ---- Equations ----
    Under the axes, the top of the legend is below the bottom of the axes by the
    height of the tick numbers and the axis title there, plus half the padding unit
    of the style, in points, so it stays clear of them when the axes change size.

    ---- Helpers ----
    _legend_cover_checker
    _renderer_getter
    """

    # ---- 1 What there is to name -----------------------------------------------------
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) < 2:
        return None
    renderer = _renderer_getter(fig)
    look = {'prop': {'family': fonts, 'size': style['fonts']['tick']},
            'frameon': False,
            'handlelength': 1.6,
            'handletextpad': 0.5,
            'labelspacing': 0.3,
            'columnspacing': 1.0,
            }

    # ---- 2 The first corner that covers nothing --------------------------------------
    for corner in LEGEND_CORNERS:
        legend = ax.legend(handles, labels, loc=corner, borderaxespad=0.3, **look)
        if not _legend_cover_checker(ax, legend.get_window_extent(renderer), renderer):
            return legend
        legend.remove()

    # ---- 3 Otherwise under the axes --------------------------------------------------
    drop_px = ax.get_window_extent(renderer).y0 - ax.get_tightbbox(renderer).y0
    drop_pt = max(drop_px, 0.0) * POINTS_PER_INCH / fig.dpi + 0.5 * style['unit']
    place = ax.transAxes + ScaledTranslation(0.0,
                                             -drop_pt / POINTS_PER_INCH,
                                             fig.dpi_scale_trans,
                                             )
    return ax.legend(handles,
                     labels,
                     loc='upper center',
                     bbox_to_anchor=(0.5, 0.0),
                     bbox_transform=place,
                     borderaxespad=0.0,
                     ncol=min(len(handles), LEGEND_COLUMNS),
                     **look,
                     )


# ---- stack_legend_drawer -------------------------------------------------------------
def stack_legend_drawer(axes: List[Axes],
                        config: dict,
                        bottom: Optional[Axes] = None,
                        below_pt: Optional[float] = None,
                        columns: int = 1,
                        ) -> Optional[Any]:
    """
    ---- Summary ----
    Main function to draw one legend for a vertical stack of axes (an individual
    experiment plot). By default it sits in the white space to the right of the stack,
    centred on the height of the stack (or on the span down to ``bottom``); with
    ``below_pt`` it sits centred under the stack instead. It holds every labelled line
    of the stack (set and measured O2, then each haem) except the OCR trace.

    ---- Inputs ----
    axes : List[Axes]
        Axes of the stack, top first.
    config : dict
        Settings; uses LEGEND_FONT_SIZE, LEGEND_FRAME and LEGEND_FRAME_LINE_WIDTH
        (optional).
    bottom : Optional[Axes]
        Lowest axes of the span to centre on (for example the bottom row of a grid of
        stacks), or None for the stack itself.
    below_pt : Optional[float]
        When set, the legend hangs this many points below the stack's lowest axes
        instead of sitting at the right.
    columns : int
        Number of legend columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Any]
        The legend, or None when the stack has no labelled lines.

    ---- Globals mutated ----
    None. Adds a legend to an axes of the stack (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Collect the lines ---------------------------------------------------------
    handles, labels = [], []
    for ax in axes:
        if getattr(ax, 'is_ocr', False):
            continue
        for handle, label in zip(*ax.get_legend_handles_labels()):
            if not label.startswith('_'):
                handles.append(handle)
                labels.append(label)
    if not handles:
        return None

    # ---- 2 Draw the legend -----------------------------------------------------------
    options = {'frameon': config['LEGEND_FRAME'],
               'fontsize': config['LEGEND_FONT_SIZE'],
               'ncol': columns,
               'borderaxespad': 0,
               }
    if below_pt is not None:
        anchor_ax = axes[-1]
        shift = ScaledTranslation(0, -below_pt / 72.0, anchor_ax.figure.dpi_scale_trans)
        legend = anchor_ax.legend(handles,
                                  labels,
                                  loc='upper center',
                                  bbox_to_anchor=(0.5, 0.0),
                                  bbox_transform=anchor_ax.transAxes + shift,
                                  **options,
                                  )
    else:
        # Anchored to the top axes, at the vertical middle of the whole span.
        top = axes[0].get_position()
        low = (bottom or axes[-1]).get_position()
        middle = ((top.y1 + low.y0) / 2 - top.y0) / top.height
        legend = axes[0].legend(handles,
                                labels,
                                loc='center left',
                                bbox_to_anchor=(1.02, middle),
                                **options,
                                )
    if config['LEGEND_FRAME']:
        legend.get_frame().set_linewidth(config.get('LEGEND_FRAME_LINE_WIDTH', 0.4))
    return legend


# ---- text_extent_calculator ----------------------------------------------------------
def text_extent_calculator(text: str,
                           size_pt: float,
                           rotation_deg: float = 0.0,
                           ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to calculate the width and height of the bounding box of a piece of
    text after rotating it.

    ---- Inputs ----
    text : str
        Plain text without mathtext.
    size_pt : float
        Font size in points.
    rotation_deg : float
        Rotation of the text in degrees.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (width, height) in points of the rotated bounding box; the unrotated height is
        at least 1.2 x size_pt.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    w = |W cos(a)| + |H sin(a)|; h = |W sin(a)| + |H cos(a)|, where W and H are the
    unrotated text width and height and a is the rotation angle.

    ---- Helpers ----
    None.
    """

    extents = TextPath((0, 0), text, size=size_pt, prop=FontProperties()).get_extents()
    width, height = extents.width, max(extents.height, 1.2 * size_pt)
    angle = math.radians(rotation_deg)
    return (abs(width * math.cos(angle)) + abs(height * math.sin(angle)),
            abs(width * math.sin(angle)) + abs(height * math.cos(angle)),
            )
