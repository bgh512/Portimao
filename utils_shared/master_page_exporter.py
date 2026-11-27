"""
The master page: one page of a journal as a PDF, with a figure on it at its printed
size, a box where its legend goes and grey lines where the text of the paper goes.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import file_name_sanitiser


# ---- CONSTANTS -----------------------------------------------------------------------
MM_PER_INCH = 25.4
POINTS_PER_MM = 72.0 / MM_PER_INCH
# the page of a journal whose file gives no page size
A4_MM = (210.0, 297.0)
A4_NOTE = 'page size not given: A4 used'
# The figure is put on the page as a picture this sharp: the page is for looking at how
# the figure sits in print, and the figure files themselves are saved elsewhere.
MASTER_DPI = 600
GUTTER_MM = 5.0  # between the columns of text
LEGEND_GAP_MM = 3.0  # figure to its legend
LEGEND_HEIGHT_MM = 18.0
LEGEND_TEXT = 'Figure legend'
TEXT_GAP_MM = 4.0  # legend to the text under it
# the grey lines standing for text of about 9 pt: one every 4.2 mm, 1.3 mm thick, the
# last line of each paragraph of nine shorter
TEXT_STEP_MM = 4.2
TEXT_THICKNESS_MM = 1.3
PARAGRAPH_LINES = 9
SHORT_LINE_SHARE = 0.55
TEXT_COLOUR = '#c9cdd1'
NOTE_COLOUR = '#707070'
NOTE_FONT_PT = 6.0


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- master_file_namer ---------------------------------------------------------------
def master_file_namer(name: str, journal: str) -> str:
    """
    ---- Summary ----
    Main function to name the master page of a file for a journal.

    ---- Inputs ----
    name : str
        Name of the experiment file, without its ending.
    journal : str
        The journal as the settings name it (a key of config.JOURNAL_SPECS).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        '<name>_master_<journal>.pdf', cleaned by the rule every file name goes through.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    """

    return f"{file_name_sanitiser(f'{name}_master_{journal}')}.pdf"


# ---- master_page_drawer --------------------------------------------------------------
def master_page_drawer(picture: Any, layout: Dict[str, Any], header: str) -> Figure:
    """
    ---- Summary ----
    Main function to draw the master page: the picture of the figure, the box of its
    legend, the grey lines of the text and one small line at the top saying what the
    page is.

    ---- Inputs ----
    picture : Any
        The figure as a picture: an array (rows, columns, 3 or 4) of colours.
    layout : Dict[str, Any]
        Where everything sits, from master_page_layout_builder.
    header : str
        The small line at the top of the page.

    ---- Globals read ----
    LEGEND_TEXT, MM_PER_INCH, NOTE_COLOUR, NOTE_FONT_PT, POINTS_PER_MM, TEXT_COLOUR,
    TEXT_THICKNESS_MM.

    ---- Outputs ----
    Figure
        The page, of the page's own size, with one axes over all of it measured in mm
        from the top left corner.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    master_text_lines_lister
    """

    # ---- 1 The page, measured in mm from its top left corner -------------------------
    page_w, page_h = layout['page_mm']
    page = Figure(figsize=(page_w / MM_PER_INCH, page_h / MM_PER_INCH))
    ax = page.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()

    # ---- 2 The figure, its legend and the text ---------------------------------------
    x, y, width, height = layout['figure_mm']
    # interpolation 'none' keeps every dot of the picture in the PDF
    ax.imshow(picture,
              extent=(x, x + width, y + height, y),
              interpolation='none',
              aspect='auto',
              )
    x, y, width, height = layout['legend_mm']
    ax.add_patch(Rectangle((x, y),
                           width,
                           height,
                           fill=False,
                           edgecolor=NOTE_COLOUR,
                           linewidth=0.5,
                           ),
                 )
    ax.text(x + width / 2,
            y + height / 2,
            LEGEND_TEXT,
            ha='center',
            va='center',
            fontsize=NOTE_FONT_PT + 1,
            color=NOTE_COLOUR,
            )
    lines = master_text_lines_lister(layout)
    if lines:
        ax.hlines([line_y + TEXT_THICKNESS_MM / 2 for _, line_y, _ in lines],
                  [line_x for line_x, _, _ in lines],
                  [line_x + line_w for line_x, _, line_w in lines],
                  colors=TEXT_COLOUR,
                  linewidth=TEXT_THICKNESS_MM * POINTS_PER_MM,
                  capstyle='butt',
                  )
    ax.text(layout['margin_mm'],
            layout['margin_mm'] / 2,
            header,
            ha='left',
            va='center',
            fontsize=NOTE_FONT_PT,
            color=NOTE_COLOUR,
            )
    ax.set_xlim(0.0, page_w)
    ax.set_ylim(page_h, 0.0)
    return page


# ---- master_page_exporter ------------------------------------------------------------
def master_page_exporter(fig: Figure,
                         spec: dict,
                         journal: str,
                         name: str,
                         folder: Path,
                         ) -> Path:
    """
    ---- Summary ----
    Main function to save the master page of a figure: one page of the journal as a
    PDF, the figure on it exactly as large as it is printed.

    ---- Inputs ----
    fig : Figure
        The figure, drawn at its printed size.
    spec : dict
        What the journal asks (config.JOURNAL_SPECS entry).
    journal : str
        The journal as the settings name it, for the file name.
    name : str
        Name of the experiment file, without its ending.
    folder : Path
        Folder the PDF is saved in; it is made when missing.

    ---- Globals read ----
    A4_NOTE, MASTER_DPI, MM_PER_INCH.

    ---- Outputs ----
    Path
        The PDF that was saved. Raises OSError when it cannot be written (a
        PermissionError when it is open in another program).

    ---- Globals mutated ----
    None. Writes the PDF (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    master_file_namer
    master_page_drawer
    master_page_layout_builder
    """

    # ---- 1 The figure as a sharp picture ---------------------------------------------
    width_mm, height_mm = (float(side) * MM_PER_INCH for side in fig.get_size_inches())
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=MASTER_DPI)
    buffer.seek(0)
    picture = np.asarray(Image.open(buffer).convert('RGB'))

    # ---- 2 The page ------------------------------------------------------------------
    layout = master_page_layout_builder(spec, (width_mm, height_mm))
    page_w, page_h = layout['page_mm']
    header = (f"{spec['name']} page, {page_w:g} × {page_h:g} mm"
              + ('' if layout['is_page_given'] else f' ({A4_NOTE})')
              + f' · {name} · figure {width_mm:.0f} × {height_mm:.0f} mm'
              )
    page = master_page_drawer(picture, layout, header)

    # ---- 3 Save it -------------------------------------------------------------------
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / master_file_namer(name, journal)
    page.savefig(path, format='pdf', dpi=MASTER_DPI)
    return path


# ---- master_page_layout_builder ------------------------------------------------------
def master_page_layout_builder(spec: dict,
                               figure_size_mm: Tuple[float, float],
                               ) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to work out where everything sits on the master page. The widest
    figure the journal takes is centred on the page, which gives the margin at the
    sides, and the same margin is used at the top and the bottom. The figure starts at
    the top left of that area, its legend sits under it, and the text fills the
    journal's columns: from the top in a column beside the figure, from under the
    legend in a column the figure covers.

    ---- Inputs ----
    spec : dict
        What the journal asks (config.JOURNAL_SPECS entry): its 'widths_mm' and its
        'paper_mm' (None: A4).
    figure_size_mm : Tuple[float, float]
        (width, height) of the figure in mm.

    ---- Globals read ----
    A4_MM, GUTTER_MM, LEGEND_GAP_MM, LEGEND_HEIGHT_MM, TEXT_GAP_MM.

    ---- Outputs ----
    Dict[str, Any]
        In mm, measured from the top left corner of the page: 'page_mm' (width,
        height), 'is_page_given' (False when A4 stands in), 'margin_mm', 'column_mm'
        (the width of a column of text), 'figure_mm' and 'legend_mm' (left, top,
        width, height) and 'columns_mm', one (left, top, width, bottom) per column
        of text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    margin = (page width - widest figure) / 2;
    column = (widest figure - gutter x (columns - 1)) / columns, with as many columns
    as the widest figure spans (Nature: (210 - 183) / 2 = 13.5 mm and
    (183 - 5) / 2 = 89 mm on an A4 page).

    ---- Helpers ----
    None.
    """

    # ---- 1 The page and its text area ------------------------------------------------
    page_w, page_h = spec.get('paper_mm') or A4_MM
    widths = spec['widths_mm']
    widest = float(max(widths.values()))
    margin = (page_w - widest) / 2.0
    n_columns = max(1, int(max(widths)))
    column = (widest - GUTTER_MM * (n_columns - 1)) / n_columns

    # ---- 2 The figure and its legend -------------------------------------------------
    width, height = figure_size_mm
    legend_top = margin + height + LEGEND_GAP_MM
    under = legend_top + LEGEND_HEIGHT_MM + TEXT_GAP_MM

    # ---- 3 The columns of text -------------------------------------------------------
    columns = []
    for index in range(n_columns):
        left = margin + index * (column + GUTTER_MM)
        is_beside = left >= margin + width
        columns.append((left, margin if is_beside else under, column, page_h - margin))
    return {'page_mm': (float(page_w), float(page_h)),
            'is_page_given': spec.get('paper_mm') is not None,
            'margin_mm': margin,
            'column_mm': column,
            'figure_mm': (margin, margin, width, height),
            'legend_mm': (margin, legend_top, width, LEGEND_HEIGHT_MM),
            'columns_mm': columns,
            }


# ---- master_text_lines_lister --------------------------------------------------------
def master_text_lines_lister(layout: Dict[str, Any],
                             ) -> List[Tuple[float, float, float]]:
    """
    ---- Summary ----
    Main function to list the grey lines that stand for the text of the paper: every
    column filled from its top to its bottom, the last line of each paragraph shorter.

    ---- Inputs ----
    layout : Dict[str, Any]
        Where everything sits, from master_page_layout_builder.

    ---- Globals read ----
    PARAGRAPH_LINES, SHORT_LINE_SHARE, TEXT_STEP_MM, TEXT_THICKNESS_MM.

    ---- Outputs ----
    List[Tuple[float, float, float]]
        (left, top, width) of each line in mm, column by column from the top.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The n-th line of a column (from 0) has its top at top + n x TEXT_STEP_MM, and is
    drawn while its bottom is not below the bottom of the column.

    ---- Helpers ----
    None.
    """

    lines = []
    for left, top, width, bottom in layout['columns_mm']:
        count = 0
        while top + count * TEXT_STEP_MM + TEXT_THICKNESS_MM <= bottom:
            is_short = count % PARAGRAPH_LINES == PARAGRAPH_LINES - 1
            lines.append((left,
                          top + count * TEXT_STEP_MM,
                          width * SHORT_LINE_SHARE if is_short else width,
                          ),
                         )
            count += 1
    return lines
