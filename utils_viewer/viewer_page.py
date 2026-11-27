"""
The page of a dataset figure in the window: the page in the plot area, its strip, and the form of a plot on the left.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import math
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_shared.page_plots  # noqa: F401  (loading it adds the plot types to the page)
from utils_shared.figure_layout import figure_size_calculator
from utils_shared.figure_page import (EMPTY_TYPES,
                                      FIRST_TYPES,
                                      figure_page_drawer,
                                      FigurePage,
                                      FigurePageError,
                                      GRID_COLUMNS,
                                      GRID_ROWS,
                                      PagePlot,
                                      panel_letters_finder,
                                      PLOT_TYPES,
                                      plot_lifter,
                                      plot_placer,
                                      plot_remover,
                                      STANDARD_COLUMNS,
                                      template_path_finder,
                                      template_reader,
                                      template_saver,
                                      )
from utils_shared.journal_files import STANDARD_JOURNAL
from utils_shared.page_data import (caption_lines_builder,
                                    form_fields_lister,
                                    form_roles_reader,
                                    TICK_ON,
                                    )
from utils_viewer.viewer_edges import photo_maker
from utils_viewer.viewer_guide import CARD_BACKGROUND
from utils_viewer.viewer_strip import height_checker, width_choices_lister


# ---- CONSTANTS -----------------------------------------------------------------------
PAGE_SHARE = 0.96  # of the plot area the page takes at most, in width or height
SMALLEST_DPI = 10.0
REDRAW_DELAY_MS = 120  # after the plot area is resized
# the ✎ and ✕ buttons in the top right corner of each plot: their side and the space
# round them
BUTTON_PX = 18
BUTTON_GAP_PX = 4
EDIT_MARK = '✎'
REMOVE_MARK = '✕'
BUTTON_FILL = '#ffffff'
BUTTON_EDGE = '#7a7a7a'
GRID_COLOUR = '#c8d4e3'
DRAG_FREE_COLOUR = '#2e7d32'
DRAG_TAKEN_COLOUR = '#c62828'
OPEN_PLOT_COLOUR = '#0b62c4'  # the plot whose form is open
OLD_CELLS_COLOUR = '#8a8a8a'  # the cells a plot had before ✎
NOTE_COLOUR = '#404040'
PROBLEM_COLOUR = '#b00020'
FORM_TEXT = '#d4d4d4'
FORM_TITLE = '#ffffff'
FORM_QUIET = '#a0a0a0'
FORM_PROBLEM = '#ff7b86'
PICKED_RELIEF = 'sunken'
UNPICKED_RELIEF = 'raised'
TYPES_PER_ROW = 6
NO_TEMPLATES = '(no templates yet)'
PAGE_HINT = ('Drag across the grid to place a plot, then fill in its form on the left. '
             f'{EDIT_MARK} changes a plot, {REMOVE_MARK} removes it.')
# the line under the page while no plot on it has colours or line styles to explain
NO_CAPTION = ('For the caption: what each colour and line style means is written here '
              'once a plot on the page uses them.')
EMPTY_PLOT_COLOUR = '#9a9a9a'  # the outline of a plot that is drawn as nothing


# ---- PageBuilder ---------------------------------------------------------------------
class PageBuilder:
    """
    ---- Summary ----
    The page of a dataset figure while it is built: its strip (the page size, the
    plot types and the templates), a line for what was done or refused, the page drawn
    in the plot area with its grid, and the form of a plot that takes the place of the
    guide's text. It runs on the window thread; the window packs its frames.

    ---- Attributes ----
    page : FigurePage
        The page as placed so far, without the plot whose form is open.
    strip : Any
        The frame of the strip, above the page.
    note : Any
        The line under the strip.
    canvas : Any
        The plot area the page is drawn in.
    caption : Any
        The frame under the page: what each colour and line style on the page means,
        for the caption, with its Copy button.
    form : Any
        The frame of the form, packed by the window in place of the guide's text.

    ---- Globals read ----
    The colour and size constants (module constants); settings.JOURNAL_SPECS.

    ---- Methods ----
    __init__
    _button_taker
    _canvas_drawer
    _caption_copier
    _caption_setter
    _form_clearer
    _form_closer
    _form_opener
    _form_roles_reader
    _height_taker
    _journal_taker
    _load_form_shower
    _load_taker
    _loader
    _mover
    _note_setter
    _plot_cancel_taker
    _plot_done_taker
    _plot_form_shower
    _presser
    _redraw_asker
    _releaser
    _replace_form_shower
    _save_form_shower
    _saver
    _size_controls_setter
    _template_list_setter
    _type_button_taker
    _type_list_taker
    _width_taker
    closer
    kept_reader
    opener
    page_reader
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 ttk: Any,
                 right: Any,
                 card: Any,
                 fonts: Tuple[str, int],
                 background: str,
                 on_form: Callable[[bool], None],
                 ) -> None:
        """
        ---- Summary ----
        Method to build the strip, the note line, the plot area and the form, none of
        them packed.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        ttk : Any
            The tkinter.ttk module.
        right : Any
            The right side of the window, which holds the strip and the plot area.
        card : Any
            The card of the open step on the left, which holds the form.
        fonts : Tuple[str, int]
            (family, size) of the guide's text.
        background : str
            The colour behind the plot area.
        on_form : Callable[[bool], None]
            Called with True when the form is to take the place of the guide's text,
            and with False when the text comes back.

        ---- Globals read ----
        FIRST_TYPES, PLOT_TYPES, TYPES_PER_ROW, settings.JOURNAL_SPECS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _caption_copier
        _height_taker
        _journal_taker
        _load_taker
        _mover
        _presser
        _redraw_asker
        _releaser
        _save_form_shower
        _type_button_taker
        _width_taker
        """

        # ---- 1 The state -------------------------------------------------------------
        self._tk, self._ttk = tk, ttk
        self._family, self._size = fonts
        self._on_form = on_form
        self.page = FigurePage()
        # the page as it was last saved as a template, loaded from one, or started
        self._kept = FigurePage()
        self._folder = Path('.')
        self._pending: Optional[PagePlot] = None  # the plot whose form is open
        self._lifted: Optional[PagePlot] = None  # the plot as it was before ✎
        self._picked_type: Optional[str] = None
        self._drag_start: Optional[Tuple[int, int]] = None
        self._box: Optional[Tuple[float, float, float, float]] = None
        self._photo: Any = None
        self._redraw_job: Any = None
        self._form_mode: Optional[str] = None
        self._journal_keys = {spec['name']: key
                              for key, spec in settings.JOURNAL_SPECS.items()
                              }
        self._width_keys: Dict[str, float] = {}
        # the plot types and the widgets of the form of a plot, while it is open
        self._form_keys: Dict[str, str] = {}
        self._form_type: Any = None
        self._form_cells: Any = None
        self._form_title = ''
        # what the plot type asks, and the drop-down or the tick of each field
        self._form_fields: List[dict] = []
        self._form_inputs: Dict[str, Any] = {}
        # the set-up table and the slim copy of each experiment the plots are drawn from
        self._setup: Optional[dict] = None
        self._experiments: Dict[str, dict] = {}
        self._answers: dict = {}  # the answers of the run
        self._caption_text = ''

        # ---- 2 The strip: the page size and the templates ----------------------------
        self.strip = tk.Frame(right, bg=background)
        sizes = tk.Frame(self.strip, bg=background)
        sizes.pack(side='top', anchor='w', pady=(0, 4))
        tk.Label(sizes, text='Journal', bg=background).pack(side='left', padx=(0, 4))
        self._journal_box = ttk.Combobox(sizes,
                                         state='readonly',
                                         width=16,
                                         values=list(self._journal_keys),
                                         )
        self._journal_box.pack(side='left', padx=(0, 10))
        self._journal_box.bind('<<ComboboxSelected>>', lambda e: self._journal_taker())
        tk.Label(sizes, text='Width', bg=background).pack(side='left', padx=(0, 4))
        self._width_box = ttk.Combobox(sizes, state='readonly', width=20)
        self._width_box.pack(side='left', padx=(0, 10))
        self._width_box.bind('<<ComboboxSelected>>', lambda e: self._width_taker())
        tk.Label(sizes, text='Height', bg=background).pack(side='left', padx=(0, 4))
        self._height_box = ttk.Entry(sizes, width=6)
        self._height_box.pack(side='left')
        self._height_box.bind('<Return>', lambda e: self._height_taker())
        self._height_box.bind('<FocusOut>', lambda e: self._height_taker())
        self._height_words = tk.Label(sizes, text='', bg=background, fg=NOTE_COLOUR)
        self._height_words.pack(side='left', padx=(4, 16))
        tk.Label(sizes, text='Template', bg=background).pack(side='left', padx=(0, 4))
        self._template_box = ttk.Combobox(sizes, state='readonly', width=18)
        self._template_box.pack(side='left', padx=(0, 4))
        self._load_button = ttk.Button(sizes,
                                       text='Load template',
                                       command=self._load_taker,
                                       )
        self._load_button.pack(side='left', padx=(0, 4))
        ttk.Button(sizes,
                   text='Save template',
                   command=self._save_form_shower,
                   ).pack(side='left')

        # ---- 3 The strip: a button per plot type that can be used now ----------------
        types = tk.Frame(self.strip, bg=background)
        types.pack(side='top', anchor='w')
        tk.Label(types,
                 text='Plot types',
                 bg=background,
                 ).grid(row=0, column=0, rowspan=2, sticky='n', padx=(0, 6))
        self._type_buttons: Dict[str, Any] = {}
        for place, key in enumerate(FIRST_TYPES):
            button = tk.Button(types,
                               text=PLOT_TYPES[key],
                               relief=UNPICKED_RELIEF,
                               padx=4,
                               pady=1,
                               command=lambda k=key: self._type_button_taker(k),
                               )
            button.grid(row=place // TYPES_PER_ROW,
                        column=1 + place % TYPES_PER_ROW,
                        sticky='we',
                        padx=1,
                        pady=1,
                        )
            self._type_buttons[key] = button

        # ---- 4 The note line, the plot area and the form -----------------------------
        self.note = tk.Label(right,
                             text=PAGE_HINT,
                             bg=background,
                             fg=NOTE_COLOUR,
                             wraplength=900,
                             justify='left',
                             anchor='w',
                             )
        self.canvas = tk.Canvas(right,
                                bg=background,
                                highlightthickness=0,
                                cursor='crosshair',
                                )
        self.canvas.bind('<Configure>', lambda e: self._redraw_asker())
        self.canvas.bind('<Button-1>', self._presser)
        self.canvas.bind('<B1-Motion>', self._mover)
        self.canvas.bind('<ButtonRelease-1>', self._releaser)
        self.caption = tk.Frame(right, bg=background)
        self._caption_button = ttk.Button(self.caption,
                                          text='Copy',
                                          command=self._caption_copier,
                                          )
        self._caption_button.pack(side='right', anchor='n', padx=(8, 0))
        self._caption_words = tk.Label(self.caption,
                                       text=NO_CAPTION,
                                       bg=background,
                                       fg=NOTE_COLOUR,
                                       wraplength=820,
                                       justify='left',
                                       anchor='w',
                                       )
        self._caption_words.pack(side='left', fill='x', expand=True)
        self.form = tk.Frame(card, bg=CARD_BACKGROUND)

    # ---- PAGE HELPERS ----------------------------------------------------------------

    # ---- _button_taker ---------------------------------------------------------------
    def _button_taker(self, kind: str, index: int) -> None:
        """
        ---- Summary ----
        Method to take a click on ✎ or ✕ of a plot: ✎ takes the plot off the page and
        opens its form, ✕ removes it.

        ---- Inputs ----
        kind : str
            'edit' (✎) or 'remove' (✕).
        index : int
            Place of the plot in page.plots.

        ---- Globals read ----
        PLOT_TYPES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _note_setter
        _plot_form_shower
        panel_letters_finder
        plot_lifter
        plot_remover
        """

        letter = panel_letters_finder(self.page).get(index)
        name = PLOT_TYPES[self.page.plots[index].plot_type]
        which = f'Plot {letter} ({name})' if letter else f'The {name.lower()}'
        if kind == 'remove':
            self.page = plot_remover(self.page, index)
            self._note_setter(f'{which} is removed.')
            self._canvas_drawer()
            return
        self.page, self._lifted = plot_lifter(self.page, index)
        self._pending = self._lifted
        self._plot_form_shower(f'Change {which[0].lower()}{which[1:]}')
        self._note_setter('Drag a new rectangle for it anywhere on the page, its old '
                          'cells included, or change its plot type on the left.',
                          )
        self._canvas_drawer()

    # ---- _canvas_drawer --------------------------------------------------------------
    def _canvas_drawer(self) -> None:
        """
        ---- Summary ----
        Method to draw the page in the plot area as large as it fits: the page with
        its plots and letters (with the plot whose form is open), the grid over it,
        a plot that is drawn as nothing outlined in grey dashes with its name, the
        open plot outlined in blue, the old cells of a plot being changed in grey
        dashes, and ✎ and ✕ on each placed plot; then the caption lines under it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        The colour and size constants (module constants); settings.JOURNAL_SPECS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area (side effect).

        ---- Equations ----
        See page_box_finder.

        ---- Helpers ----
        _caption_setter
        page_box_finder
        page_picture_maker
        photo_maker
        plot_box_finder
        plot_buttons_placer
        """

        # ---- 1 The page, as large as the plot area takes -----------------------------
        canvas = self.canvas
        self._redraw_job = None
        canvas.delete('all')
        width_px, height_px = canvas.winfo_width(), canvas.winfo_height()
        if width_px < 20 or height_px < 20:
            return
        shown = self.page
        if self._pending is not None:
            shown = replace(shown, plots=shown.plots + (self._pending,))
        self._caption_setter(shown)
        spec = settings.JOURNAL_SPECS[shown.journal]
        size_in = figure_size_calculator(spec, shown.columns, shown.height)
        dpi = page_box_finder((width_px, height_px), size_in)
        picture = page_picture_maker(shown,
                                     spec,
                                     dpi,
                                     self._setup,
                                     self._experiments,
                                     self._answers,
                                     )
        left = (width_px - picture.width) / 2.0
        top = (height_px - picture.height) / 2.0
        self._box = (left, top, float(picture.width), float(picture.height))
        self._photo = photo_maker(self._tk, picture)
        canvas.create_image(left, top, image=self._photo, anchor='nw')

        # ---- 2 The grid --------------------------------------------------------------
        for column in range(1, GRID_COLUMNS):
            x = left + picture.width * column / GRID_COLUMNS
            canvas.create_line(x,
                               top,
                               x,
                               top + picture.height,
                               fill=GRID_COLOUR,
                               dash=(3, 3),
                               )
        for row in range(1, GRID_ROWS):
            y = top + picture.height * row / GRID_ROWS
            canvas.create_line(left,
                               y,
                               left + picture.width,
                               y,
                               fill=GRID_COLOUR,
                               dash=(3, 3),
                               )
        canvas.create_rectangle(left,
                                top,
                                left + picture.width,
                                top + picture.height,
                                outline=GRID_COLOUR,
                                )

        # ---- 3 The plot being changed, and the old cells of one changed with ✎ -------
        # a plot drawn as nothing is shown here only, never in the saved figure
        for plot in shown.plots:
            if plot.plot_type not in EMPTY_TYPES:
                continue
            x0, y0, x1, y1 = plot_box_finder(plot, self._box)
            canvas.create_rectangle(x0 + BUTTON_GAP_PX,
                                    y0 + BUTTON_GAP_PX,
                                    x1 - BUTTON_GAP_PX,
                                    y1 - BUTTON_GAP_PX,
                                    outline=EMPTY_PLOT_COLOUR,
                                    dash=(2, 4),
                                    )
            canvas.create_text((x0 + x1) / 2.0,
                               (y0 + y1) / 2.0,
                               text=PLOT_TYPES[plot.plot_type],
                               fill=EMPTY_PLOT_COLOUR,
                               font=(self._family, max(self._size - 2, 8)),
                               )
        if self._lifted is not None:
            canvas.create_rectangle(*plot_box_finder(self._lifted, self._box),
                                    outline=OLD_CELLS_COLOUR,
                                    width=2,
                                    dash=(6, 4),
                                    )
        if self._pending is not None:
            canvas.create_rectangle(*plot_box_finder(self._pending, self._box),
                                    outline=OPEN_PLOT_COLOUR,
                                    width=3,
                                    )

        # ---- 4 ✎ and ✕ on each placed plot -------------------------------------------
        for index, plot in enumerate(self.page.plots):
            for kind, (x0, y0, x1, y1) in plot_buttons_placer(plot, self._box).items():
                canvas.create_rectangle(x0,
                                        y0,
                                        x1,
                                        y1,
                                        fill=BUTTON_FILL,
                                        outline=BUTTON_EDGE,
                                        )
                canvas.create_text((x0 + x1) / 2.0,
                                   (y0 + y1) / 2.0,
                                   text=EDIT_MARK if kind == 'edit' else REMOVE_MARK,
                                   font=(self._family, max(self._size - 3, 8)),
                                   )

    # ---- _caption_copier -------------------------------------------------------------
    def _caption_copier(self) -> None:
        """
        ---- Summary ----
        Method to take Copy under the page: the caption lines go to the clipboard, to
        paste into the caption of the figure.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the clipboard and the note line (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _note_setter
        """

        if not self._caption_text:
            return
        self.canvas.clipboard_clear()
        self.canvas.clipboard_append(self._caption_text)
        self._note_setter('Copied: paste it into the caption of the figure.')

    # ---- _caption_setter -------------------------------------------------------------
    def _caption_setter(self, page: FigurePage) -> None:
        """
        ---- Summary ----
        Method to write under the page what each colour, line style and shade on it
        means, for the caption; Copy is greyed out while there is nothing to explain.

        ---- Inputs ----
        page : FigurePage
            The page as shown, with the plot whose form is open.

        ---- Globals read ----
        NO_CAPTION.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        caption_lines_builder
        """

        self._caption_text = '\n'.join(caption_lines_builder(page,
                                                             self._setup,
                                                             self._experiments,
                                                             self._answers,
                                                             ),
                                       )
        self._caption_words.configure(text=self._caption_text or NO_CAPTION)
        self._caption_button.configure(state='normal' if self._caption_text
                                       else 'disabled',
                                       )

    # ---- _form_clearer ---------------------------------------------------------------
    def _form_clearer(self) -> None:
        """
        ---- Summary ----
        Method to empty the form, so it can be filled for another use.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Destroys the widgets of the form (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        for child in self.form.winfo_children():
            child.destroy()

    # ---- _form_closer ----------------------------------------------------------------
    def _form_closer(self) -> None:
        """
        ---- Summary ----
        Method to close the form, so the guide's text comes back on the left.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_clearer
        """

        self._form_clearer()
        if self._form_mode is not None:
            self._form_mode = None
            self._on_form(False)

    # ---- _form_opener ----------------------------------------------------------------
    def _form_opener(self, mode: str, title: str, words: str = '') -> Any:
        """
        ---- Summary ----
        Method to fill the form with its title and a line of words, open it in place
        of the guide's text, and give the frame its fields and buttons go in.

        ---- Inputs ----
        mode : str
            'plot', 'save', 'replace' or 'load'.
        title : str
            The title of the form.
        words : str
            A line under the title; empty for none.

        ---- Globals read ----
        FORM_QUIET, FORM_TITLE.

        ---- Outputs ----
        Any
            The frame under the title.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_clearer
        """

        tk = self._tk
        self._form_clearer()
        tk.Label(self.form,
                 text=title,
                 bg=CARD_BACKGROUND,
                 fg=FORM_TITLE,
                 anchor='w',
                 font=(self._family, self._size + 2, 'bold'),
                 ).pack(side='top', fill='x', padx=10, pady=(10, 4))
        if words:
            tk.Label(self.form,
                     text=words,
                     bg=CARD_BACKGROUND,
                     fg=FORM_QUIET,
                     anchor='w',
                     justify='left',
                     wraplength=480,
                     font=(self._family, self._size - 1),
                     ).pack(side='top', fill='x', padx=10, pady=(0, 6))
        body = tk.Frame(self.form, bg=CARD_BACKGROUND)
        body.pack(side='top', fill='x', padx=10)
        if self._form_mode is None:
            self._on_form(True)
        self._form_mode = mode
        return body

    # ---- _form_roles_reader ----------------------------------------------------------
    def _form_roles_reader(self) -> Dict[str, str]:
        """
        ---- Summary ----
        Method to read the form of a plot as it is filled in: the roles of the plot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Dict[str, str]
            The roles (form_roles_reader); empty for a plot type that asks nothing.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        form_roles_reader
        """

        values = {key: widget.get() for key, widget in self._form_inputs.items()}
        return form_roles_reader(self._form_fields, values)

    # ---- _height_taker ---------------------------------------------------------------
    def _height_taker(self) -> None:
        """
        ---- Summary ----
        Method to take the height typed in the strip: a share of the journal's page,
        which redraws the page; a height that cannot be used is said on the note line.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _note_setter
        height_checker
        """

        height, words = height_checker(self._height_box.get(), self.page.journal)
        if height is None:
            self._note_setter(
                f'The height is not changed: {words[0].lower()}{words[1:]}',
                is_problem=True,
                )
            return
        self._height_words.configure(text=words)
        if height != self.page.height:
            self.page = replace(self.page, height=height)
            self._canvas_drawer()

    # ---- _journal_taker --------------------------------------------------------------
    def _journal_taker(self) -> None:
        """
        ---- Summary ----
        Method to take the journal picked in the strip: the page takes its page and
        widths, keeping its width when the journal has it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _size_controls_setter
        page_journal_fitter
        """

        journal = self._journal_keys.get(self._journal_box.get())
        if journal is None or journal == self.page.journal:
            return
        self.page, _ = page_journal_fitter(replace(self.page, journal=journal),
                                           settings.JOURNAL_SPECS,
                                           )
        self._size_controls_setter()
        self._canvas_drawer()

    # ---- _load_form_shower -----------------------------------------------------------
    def _load_form_shower(self, name: str) -> None:
        """
        ---- Summary ----
        Method to ask, in the form, before a template takes the place of the plots on
        the page.

        ---- Inputs ----
        name : str
            The template's name.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_closer
        _form_opener
        _loader
        """

        count = len(self.page.plots) + (self._pending is not None)
        body = self._form_opener('load',
                                 f'Load the template {name}',
                                 f"It takes the place of the {count} plot"
                                 f"{'' if count == 1 else 's'} on the page.",
                                 )
        ttk = self._ttk
        ttk.Button(body,
                   text='Replace them',
                   command=lambda: self._loader(name),
                   ).pack(side='left', padx=(0, 6), pady=6)
        ttk.Button(body, text='Cancel', command=self._form_closer).pack(side='left',
                                                                        pady=6,
                                                                        )

    # ---- _load_taker -----------------------------------------------------------------
    def _load_taker(self) -> None:
        """
        ---- Summary ----
        Method to take a click on Load template: the template picked is loaded, after
        asking when the page already has plots.

        ---- Inputs ----
        None.

        ---- Globals read ----
        NO_TEMPLATES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _load_form_shower
        _loader
        _note_setter
        """

        name = self._template_box.get()
        if not name or name == NO_TEMPLATES:
            self._note_setter('Pick a template in the list beside Load template first.',
                              is_problem=True,
                              )
            return
        if self._form_mode in ('save', 'replace'):
            self._note_setter('Save the template or cancel it first.', is_problem=True)
            return
        if self.page.plots or self._pending is not None:
            self._load_form_shower(name)
        else:
            self._loader(name)

    # ---- _loader ---------------------------------------------------------------------
    def _loader(self, name: str) -> None:
        """
        ---- Summary ----
        Method to load a template in place of the page: a template that cannot be used
        is said on the note line and the page stays as it was; a journal or width the
        journals here do not have is changed, and the note line says so.

        ---- Inputs ----
        name : str
            The template's name (its file name without .json).

        ---- Globals read ----
        settings.JOURNAL_SPECS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _form_closer
        _note_setter
        _size_controls_setter
        page_journal_fitter
        template_reader
        """

        path = self._folder / f'{name}.json'
        try:
            page = template_reader(path)
        except FigurePageError as exc:
            self._form_closer()
            self._note_setter(str(exc), is_problem=True)
            return
        except OSError:
            self._form_closer()
            self._note_setter(f'The template {name} could not be read from '
                              f'{self._folder}: check that it is still there.',
                              is_problem=True,
                              )
            return
        page, change = page_journal_fitter(page, settings.JOURNAL_SPECS)
        self.page, self._pending, self._lifted = page, None, None
        self._kept = page
        self._form_closer()
        self._size_controls_setter()
        self._note_setter(
            f'The template {name} is loaded.' + (f' {change}' if change else ''),
            )
        self._canvas_drawer()

    # ---- _mover ----------------------------------------------------------------------
    def _mover(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to follow a drag across the page: the rectangle of cells from where it
        started to the cell under the mouse is drawn, green where it can go and red
        over another plot.

        ---- Inputs ----
        event : Any
            The Tk motion event.

        ---- Globals read ----
        DRAG_FREE_COLOUR, DRAG_TAKEN_COLOUR.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        drag_plot_maker
        page_cell_finder
        plot_box_finder
        plot_placer
        """

        if self._drag_start is None or self._box is None:
            return
        end = page_cell_finder(event.x, event.y, self._box, is_clamped=True)
        plot = drag_plot_maker(self._drag_start, end, FIRST_TYPES[0], {})
        try:
            plot_placer(self.page, plot)
            colour = DRAG_FREE_COLOUR
        except FigurePageError:
            colour = DRAG_TAKEN_COLOUR
        self.canvas.delete('drag')
        self.canvas.create_rectangle(*plot_box_finder(plot, self._box),
                                     outline=colour,
                                     width=3,
                                     tags=('drag',),
                                     )

    # ---- _note_setter ----------------------------------------------------------------
    def _note_setter(self, text: str, is_problem: bool = False) -> None:
        """
        ---- Summary ----
        Method to write one line under the strip: what was done, or in red why it
        could not be.

        ---- Inputs ----
        text : str
            The sentence.
        is_problem : bool
            True for a red line.

        ---- Globals read ----
        NOTE_COLOUR, PROBLEM_COLOUR.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.note.configure(text=text, fg=PROBLEM_COLOUR if is_problem else NOTE_COLOUR)

    # ---- _plot_cancel_taker ----------------------------------------------------------
    def _plot_cancel_taker(self) -> None:
        """
        ---- Summary ----
        Method to take Cancel in the form of a plot: a new plot goes, and a plot
        changed with ✎ goes back to its cells and plot type.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _form_closer
        _note_setter
        plot_placer
        """

        if self._lifted is not None:
            self.page = plot_placer(self.page, self._lifted)
        self._pending, self._lifted = None, None
        self._form_closer()
        self._note_setter(PAGE_HINT)
        self._canvas_drawer()

    # ---- _plot_done_taker ------------------------------------------------------------
    def _plot_done_taker(self) -> None:
        """
        ---- Summary ----
        Method to take Done in the form of a plot: what the form holds becomes the
        roles of the plot, and the plot is placed on the page and drawn in its cells.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PLOT_TYPES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _form_closer
        _form_roles_reader
        _note_setter
        panel_letters_finder
        plot_placer
        """

        if self._pending is None:
            return
        self._pending = replace(self._pending, roles=self._form_roles_reader())
        self.page = plot_placer(self.page, self._pending)
        index = len(self.page.plots) - 1
        letter = panel_letters_finder(self.page).get(index)
        name = PLOT_TYPES[self._pending.plot_type]
        self._pending, self._lifted = None, None
        self._form_closer()
        self._note_setter(f'Plot {letter} ({name}) is on the page.' if letter
                          else f'The {name.lower()} is on the page.',
                          )
        self._canvas_drawer()

    # ---- _plot_form_shower -----------------------------------------------------------
    def _plot_form_shower(self, title: str) -> None:
        """
        ---- Summary ----
        Method to open the form of the plot whose form is open: its plot type, the
        cells it takes, what its plot type asks (a drop-down or a tick for each
        field, starting as the roles of the plot say), and Done and Cancel.

        ---- Inputs ----
        title : str
            The title of the form ("New plot", "Change plot b").

        ---- Globals read ----
        FIRST_TYPES, FORM_QUIET, FORM_TEXT, PLOT_TYPES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_opener
        _plot_cancel_taker
        _plot_done_taker
        _type_list_taker
        cells_describer
        form_fields_lister
        """

        # ---- 1 The plot type and the cells -------------------------------------------
        tk, ttk = self._tk, self._ttk
        plot = self._pending
        self._form_title = title
        body = self._form_opener('plot',
                                 title,
                                 'Drag across the page again to move it or change its '
                                 'size. What it shows comes with each plot type.',
                                 )
        keys = list(FIRST_TYPES)
        if plot.plot_type not in keys:  # a plot type of a template, not built yet
            keys.append(plot.plot_type)
        self._form_keys = {PLOT_TYPES[key]: key for key in keys}
        tk.Label(body,
                 text='Plot type',
                 bg=CARD_BACKGROUND,
                 fg=FORM_TEXT,
                 font=(self._family, self._size),
                 ).grid(row=0, column=0, sticky='w', pady=4)
        self._form_type = ttk.Combobox(body,
                                       state='readonly',
                                       width=28,
                                       values=list(self._form_keys),
                                       )
        self._form_type.set(PLOT_TYPES[plot.plot_type])
        self._form_type.grid(row=0, column=1, sticky='w', padx=(8, 0), pady=4)
        self._form_type.bind('<<ComboboxSelected>>', lambda e: self._type_list_taker())
        tk.Label(body,
                 text='Cells',
                 bg=CARD_BACKGROUND,
                 fg=FORM_TEXT,
                 font=(self._family, self._size),
                 ).grid(row=1, column=0, sticky='w', pady=4)
        self._form_cells = tk.Label(body,
                                    text=cells_describer(plot),
                                    bg=CARD_BACKGROUND,
                                    fg=FORM_TEXT,
                                    font=(self._family, self._size),
                                    )
        self._form_cells.grid(row=1, column=1, sticky='w', padx=(8, 0), pady=4)

        # ---- 2 What the plot type asks -----------------------------------------------
        self._form_fields = form_fields_lister(plot.plot_type,
                                               self._setup,
                                               plot.roles,
                                               self._answers,
                                               )
        self._form_inputs = {}
        row = 2
        for field in self._form_fields:
            if field['kind'] == 'tick':
                ticked = tk.BooleanVar(body, value=field['value'] == TICK_ON)
                tk.Checkbutton(body,
                               text=field['label'],
                               variable=ticked,
                               bg=CARD_BACKGROUND,
                               fg=FORM_TEXT,
                               activebackground=CARD_BACKGROUND,
                               activeforeground=FORM_TEXT,
                               selectcolor=CARD_BACKGROUND,
                               font=(self._family, self._size),
                               ).grid(row=row, column=0, columnspan=2, sticky='w')
                self._form_inputs[field['key']] = ticked
            elif field['choices']:
                tk.Label(body,
                         text=field['label'],
                         bg=CARD_BACKGROUND,
                         fg=FORM_TEXT,
                         font=(self._family, self._size),
                         ).grid(row=row, column=0, sticky='w', pady=4)
                words = [shown for _, shown in field['choices']]
                picker = ttk.Combobox(body, state='readonly', width=28, values=words)
                picker.set(dict(field['choices'])[field['value']])
                picker.grid(row=row, column=1, sticky='w', padx=(8, 0), pady=4)
                self._form_inputs[field['key']] = picker
            row += 1

        # ---- 3 Done and Cancel -------------------------------------------------------
        buttons = tk.Frame(body, bg=CARD_BACKGROUND)
        buttons.grid(row=row, column=0, columnspan=2, sticky='w', pady=(8, 4))
        ttk.Button(buttons,
                   text='Done',
                   command=self._plot_done_taker,
                   ).pack(side='left', padx=(0, 6))
        ttk.Button(buttons, text='Cancel', command=self._plot_cancel_taker).pack(
            side='left',
            )

    # ---- _presser --------------------------------------------------------------------
    def _presser(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to take a press on the page: on ✎ or ✕ of a plot, that button; on a
        cell, the start of a drag.

        ---- Inputs ----
        event : Any
            The Tk press event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _button_taker
        _note_setter
        page_cell_finder
        plot_button_finder
        """

        if self._box is None:
            return
        if self._form_mode in ('save', 'replace', 'load'):
            self._note_setter('Finish with the template on the left first.',
                              is_problem=True,
                              )
            return
        hit = plot_button_finder(event.x, event.y, self.page, self._box)
        if hit is not None:
            if self._form_mode == 'plot':
                self._note_setter('Click Done or Cancel on the left first.',
                                  is_problem=True,
                                  )
            else:
                self._button_taker(*hit)
            return
        self._drag_start = page_cell_finder(event.x, event.y, self._box)

    # ---- _redraw_asker ---------------------------------------------------------------
    def _redraw_asker(self) -> None:
        """
        ---- Summary ----
        Method to draw the page again shortly after the plot area is resized, once for
        a run of resizes.

        ---- Inputs ----
        None.

        ---- Globals read ----
        REDRAW_DELAY_MS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Schedules the drawing (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        """

        if self._redraw_job is not None:
            self.canvas.after_cancel(self._redraw_job)
        self._redraw_job = self.canvas.after(REDRAW_DELAY_MS, self._canvas_drawer)

    # ---- _releaser -------------------------------------------------------------------
    def _releaser(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to end a drag across the page: the rectangle becomes the cells of the
        plot whose form is open, or of a new plot of the plot type picked (the first
        one when none is), and its form opens. A rectangle over another plot is
        refused on the note line.

        ---- Inputs ----
        event : Any
            The Tk release event.

        ---- Globals read ----
        FIRST_TYPES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _note_setter
        _plot_form_shower
        cells_describer
        drag_plot_maker
        page_cell_finder
        plot_placer
        """

        start, self._drag_start = self._drag_start, None
        self.canvas.delete('drag')
        if start is None or self._box is None:
            return
        end = page_cell_finder(event.x, event.y, self._box, is_clamped=True)
        if self._pending is not None:
            plot_type, roles = self._pending.plot_type, self._pending.roles
        else:
            plot_type, roles = self._picked_type or FIRST_TYPES[0], {}
        plot = drag_plot_maker(start, end, plot_type, roles)
        try:
            plot_placer(self.page, plot)
        except FigurePageError as exc:
            self._note_setter(str(exc), is_problem=True)
            return
        is_new = self._pending is None
        self._pending = plot
        if is_new:
            self._plot_form_shower('New plot')
        else:
            self._form_cells.configure(text=cells_describer(plot))
        self._note_setter('Click Done on the left to keep it, or drag again.')
        self._canvas_drawer()

    # ---- _replace_form_shower --------------------------------------------------------
    def _replace_form_shower(self, name: str) -> None:
        """
        ---- Summary ----
        Method to ask, in the form, before a template of the same name is written over.

        ---- Inputs ----
        name : str
            The name typed.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_opener
        _save_form_shower
        _saver
        template_path_finder
        """

        stem = template_path_finder(self._folder, name).stem
        body = self._form_opener('replace',
                                 'Save the page as a template',
                                 f'A template called {stem} is already there.',
                                 )
        ttk = self._ttk
        ttk.Button(body,
                   text='Replace it',
                   command=lambda: self._saver(name, may_replace=True),
                   ).pack(side='left', padx=(0, 6), pady=6)
        ttk.Button(body,
                   text='Choose another name',
                   command=lambda: self._save_form_shower(name),
                   ).pack(side='left', pady=6)

    # ---- _save_form_shower -----------------------------------------------------------
    def _save_form_shower(self, name: str = '', problem: str = '') -> None:
        """
        ---- Summary ----
        Method to take a click on Save template: the form asks for the template's name,
        with Save and Cancel.

        ---- Inputs ----
        name : str
            The name to start the box with.
        problem : str
            A sentence in red under the box; empty for none.

        ---- Globals read ----
        FORM_PROBLEM.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_closer
        _form_opener
        _note_setter
        _saver
        """

        if self._form_mode == 'plot':
            self._note_setter('Click Done or Cancel on the left first.',
                              is_problem=True,
                              )
            return
        if not self.page.plots:
            self._note_setter(
                'Place a plot on the page before saving it as a template.',
                is_problem=True,
                )
            return
        tk, ttk = self._tk, self._ttk
        body = self._form_opener('save',
                                 'Save the page as a template',
                                 'It keeps the page size and each plot, so it can be '
                                 'loaded for another dataset.',
                                 )
        tk.Label(body,
                 text='Name',
                 bg=CARD_BACKGROUND,
                 fg=FORM_TEXT,
                 font=(self._family, self._size),
                 ).grid(row=0, column=0, sticky='w', pady=4)
        entry = ttk.Entry(body, width=30)
        entry.insert(0, name)
        entry.grid(row=0, column=1, sticky='w', padx=(8, 0), pady=4)
        entry.bind('<Return>', lambda e: self._saver(entry.get()))
        if problem:
            tk.Label(body,
                     text=problem,
                     bg=CARD_BACKGROUND,
                     fg=FORM_PROBLEM,
                     wraplength=440,
                     justify='left',
                     font=(self._family, self._size - 1),
                     ).grid(row=1, column=0, columnspan=2, sticky='w')
        buttons = tk.Frame(body, bg=CARD_BACKGROUND)
        buttons.grid(row=2, column=0, columnspan=2, sticky='w', pady=(8, 4))
        ttk.Button(buttons,
                   text='Save',
                   command=lambda: self._saver(entry.get()),
                   ).pack(side='left', padx=(0, 6))
        ttk.Button(buttons, text='Cancel', command=self._form_closer).pack(side='left')
        entry.focus_set()

    # ---- _saver ----------------------------------------------------------------------
    def _saver(self, name: str, may_replace: bool = False) -> None:
        """
        ---- Summary ----
        Method to save the page as a template under the name typed, asking first when
        one of that name is there; a template that cannot be saved is said in the form.

        ---- Inputs ----
        name : str
            The name typed.
        may_replace : bool
            True once the user has said to write over the one of that name.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Writes the template file and changes the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_closer
        _note_setter
        _replace_form_shower
        _save_form_shower
        _template_list_setter
        template_path_finder
        template_saver
        """

        name = name.strip()
        if not name:
            self._save_form_shower(problem='Type a name for the template.')
            return
        if not may_replace and template_path_finder(self._folder, name).exists():
            self._replace_form_shower(name)
            return
        try:
            path = template_saver(self.page,
                                  self._folder,
                                  name,
                                  may_replace=may_replace,
                                  )
        except FigurePageError as exc:
            self._save_form_shower(name, str(exc))
            return
        except OSError:
            self._save_form_shower(name,
                                   f'The template could not be written in '
                                   f'{self._folder}: check that the folder can be '
                                   f'written to.',
                                   )
            return
        self._kept = self.page
        self._form_closer()
        self._template_list_setter(path.stem)
        self._note_setter(f'The page is saved as the template {path.stem}.')

    # ---- _size_controls_setter -------------------------------------------------------
    def _size_controls_setter(self) -> None:
        """
        ---- Summary ----
        Method to show the page's journal, width and height in the strip.

        ---- Inputs ----
        None.

        ---- Globals read ----
        settings.JOURNAL_SPECS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        height_checker
        width_choices_lister
        """

        page = self.page
        self._journal_box.set(settings.JOURNAL_SPECS[page.journal]['name'])
        choices = width_choices_lister(page.journal)
        self._width_keys = {words: columns for columns, words in choices}
        self._width_box.configure(values=list(self._width_keys))
        self._width_box.set(
            next(words for columns, words in choices if columns == page.columns),
            )
        self._height_box.delete(0, 'end')
        self._height_box.insert(0, f'{page.height:g}')
        self._height_words.configure(
            text=height_checker(f'{page.height:g}', page.journal)[1],
            )

    # ---- _template_list_setter -------------------------------------------------------
    def _template_list_setter(self, picked: Optional[str] = None) -> None:
        """
        ---- Summary ----
        Method to fill the list of templates from the layouts folder, with Load
        template greyed when there is none.

        ---- Inputs ----
        picked : Optional[str]
            The template to show picked; None for the first.

        ---- Globals read ----
        NO_TEMPLATES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        template_names_lister
        """

        names = template_names_lister(self._folder)
        self._template_box.configure(values=names or [NO_TEMPLATES])
        self._template_box.set(
            picked if picked in names else (names or [NO_TEMPLATES])[0],
            )
        self._load_button.configure(state='normal' if names else 'disabled')

    # ---- _type_button_taker ----------------------------------------------------------
    def _type_button_taker(self, key: str) -> None:
        """
        ---- Summary ----
        Method to take a plot-type button of the strip: it becomes the plot type of
        the plot whose form is open, or of the next plot dragged.

        ---- Inputs ----
        key : str
            The plot type, such as 'P7'.

        ---- Globals read ----
        PICKED_RELIEF, PLOT_TYPES, UNPICKED_RELIEF.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _note_setter
        """

        self._picked_type = key
        for other, button in self._type_buttons.items():
            button.configure(relief=PICKED_RELIEF if other == key else UNPICKED_RELIEF)
        if self._form_mode == 'plot' and self._pending is not None:
            # another plot type asks other things, so its form starts afresh
            self._pending = replace(self._pending, plot_type=key, roles={})
            self._plot_form_shower(self._form_title)
            self._canvas_drawer()
            return
        self._note_setter(f'Drag across the grid to place a {PLOT_TYPES[key].lower()}.')

    # ---- _type_list_taker ------------------------------------------------------------
    def _type_list_taker(self) -> None:
        """
        ---- Summary ----
        Method to take the plot type picked in the form.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        """

        key = self._form_keys.get(self._form_type.get())
        if key is None or self._pending is None:
            return
        if key != self._pending.plot_type:
            # another plot type asks other things, so its form starts afresh
            self._pending = replace(self._pending, plot_type=key, roles={})
            # once the list has closed, as the form is built again with a new list
            self.canvas.after_idle(lambda: self._pending is not None
                                   and self._plot_form_shower(self._form_title),
                                   )
        self._canvas_drawer()

    # ---- _width_taker ----------------------------------------------------------------
    def _width_taker(self) -> None:
        """
        ---- Summary ----
        Method to take the width picked in the strip, which redraws the page.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the page and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        """

        columns = self._width_keys.get(self._width_box.get())
        if columns is not None and columns != self.page.columns:
            self.page = replace(self.page, columns=columns)
            self._canvas_drawer()

    # ---- PUBLIC METHODS --------------------------------------------------------------

    # ---- closer ----------------------------------------------------------------------
    def closer(self) -> None:
        """
        ---- Summary ----
        Method to end the building once the step is answered: a form still open is
        cancelled, so the page is as page_reader gave it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _form_closer
        plot_placer
        """

        if self._lifted is not None:
            self.page = plot_placer(self.page, self._lifted)
        self._pending, self._lifted, self._drag_start = None, None, None
        self._form_closer()

    # ---- kept_reader -----------------------------------------------------------------
    def kept_reader(self) -> FigurePage:
        """
        ---- Summary ----
        Method to give the page as it was last saved as a template, loaded from one,
        or started, so the step can tell whether the page has changed since. It may be
        called from the question thread once the step is answered.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        FigurePage
            That page.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self._kept

    # ---- opener ----------------------------------------------------------------------
    def opener(self,
               page: FigurePage,
               folder: Path,
               setup: Optional[dict] = None,
               experiments: Optional[Dict[str, dict]] = None,
               answers: Optional[dict] = None,
               ) -> None:
        """
        ---- Summary ----
        Method to start building a page: its size in the strip, the templates of the
        layouts folder in their list, and the page drawn.

        ---- Inputs ----
        page : FigurePage
            The page to start from.
        folder : Path
            The layouts folder, where templates are saved and read.
        setup : Optional[dict]
            The set-up table (dataset_setup, DATA_FORMAT.md), which the forms of the
            plots offer their choices from; None for none.
        experiments : Optional[Dict[str, dict]]
            {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md), which
            the plots are drawn from; None for none.
        answers : Optional[dict]
            The answers of the run, for what the forms offer from them and the plots
            drawn as the run was set up; None for none.

        ---- Globals read ----
        PAGE_HINT; settings.JOURNAL_SPECS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canvas_drawer
        _note_setter
        _size_controls_setter
        _template_list_setter
        page_journal_fitter
        """

        self.page, change = page_journal_fitter(page, settings.JOURNAL_SPECS)
        self._kept = self.page
        self._folder = folder
        self._setup, self._experiments = setup, experiments or {}
        self._answers = answers or {}
        self._pending, self._lifted, self._drag_start = None, None, None
        self._size_controls_setter()
        self._template_list_setter()
        self._note_setter(PAGE_HINT + (f' {change}' if change else ''))
        self._redraw_asker()

    # ---- page_reader -----------------------------------------------------------------
    def page_reader(self) -> FigurePage:
        """
        ---- Summary ----
        Method to give the page as placed: a plot whose form is still open is left out,
        and a plot changed with ✎ is where it was. It may be called from the question
        thread once the step is answered.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        FigurePage
            The page.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        plot_placer
        """

        page, lifted = self.page, self._lifted
        return page if lifted is None else plot_placer(page, lifted)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- cells_describer -----------------------------------------------------------------
def cells_describer(plot: PagePlot) -> str:
    """
    ---- Summary ----
    Main function to say in words which cells of the grid a plot takes, counted from 1
    at the top left.

    ---- Inputs ----
    plot : PagePlot
        The plot.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Such as 'rows 1 to 2, columns 3 to 6 (8 cells)' or 'row 1, column 1 (1 cell)'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    def span(word: str, first: int, count: int) -> str:
        if count == 1:
            return f'{word} {first + 1}'
        return f'{word}s {first + 1} to {first + count}'
    cells = plot.n_rows * plot.n_columns
    return (f"{span('row', plot.row, plot.n_rows)}, "
            f"{span('column', plot.column, plot.n_columns)} "
            f"({cells} cell{'' if cells == 1 else 's'})"
            )


# ---- drag_plot_maker -----------------------------------------------------------------
def drag_plot_maker(start: Tuple[int, int],
                    end: Tuple[int, int],
                    plot_type: str,
                    roles: Dict[str, str],
                    ) -> PagePlot:
    """
    ---- Summary ----
    Main function to turn a drag from one cell to another into a plot: the rectangle
    with those two cells at opposite corners, whichever way the drag went.

    ---- Inputs ----
    start : Tuple[int, int]
        (row, column) where the drag started, from 0 at the top left.
    end : Tuple[int, int]
        (row, column) where it ended.
    plot_type : str
        The plot type, such as 'P1'.
    roles : Dict[str, str]
        The roles of the plot (kept when a plot is dragged again).

    ---- Globals read ----
    None.

    ---- Outputs ----
    PagePlot
        The plot.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    row = min(start row, end row); n_rows = |end row - start row| + 1; the same for
    the columns.

    ---- Helpers ----
    None.
    """

    return PagePlot(plot_type=plot_type,
                    row=min(start[0], end[0]),
                    column=min(start[1], end[1]),
                    n_rows=abs(end[0] - start[0]) + 1,
                    n_columns=abs(end[1] - start[1]) + 1,
                    roles=dict(roles),
                    )


# ---- page_box_finder -----------------------------------------------------------------
def page_box_finder(area_px: Tuple[int, int], size_in: Tuple[float, float]) -> float:
    """
    ---- Summary ----
    Main function to find the dots per inch that draw a page as large as it fits in
    the plot area, its shape kept.

    ---- Inputs ----
    area_px : Tuple[int, int]
        (width, height) of the plot area in pixels.
    size_in : Tuple[float, float]
        (width, height) of the page in inches, at its printed size.

    ---- Globals read ----
    PAGE_SHARE, SMALLEST_DPI.

    ---- Outputs ----
    float
        The dots per inch, at least SMALLEST_DPI.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    dpi = PAGE_SHARE x min(area width / page width, area height / page height).

    ---- Helpers ----
    None.
    """

    dpi = PAGE_SHARE * min(area_px[0] / size_in[0], area_px[1] / size_in[1])
    return max(dpi, SMALLEST_DPI)


# ---- page_cell_finder ----------------------------------------------------------------
def page_cell_finder(x: float,
                     y: float,
                     box: Tuple[float, float, float, float],
                     is_clamped: bool = False,
                     ) -> Optional[Tuple[int, int]]:
    """
    ---- Summary ----
    Main function to find the cell of the grid under a point of the plot area.

    ---- Inputs ----
    x, y : float
        The point, in pixels of the plot area.
    box : Tuple[float, float, float, float]
        (left, top, width, height) of the page drawn, in pixels.
    is_clamped : bool
        True to give the nearest cell for a point off the page (the end of a drag).

    ---- Globals read ----
    GRID_COLUMNS, GRID_ROWS.

    ---- Outputs ----
    Optional[Tuple[int, int]]
        (row, column) from 0 at the top left; None for a point off the page unless
        is_clamped.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    column = floor((x - left) / width x GRID_COLUMNS); row = floor((y - top) / height
    x GRID_ROWS).

    ---- Helpers ----
    None.
    """

    left, top, width, height = box
    column = math.floor((x - left) / width * GRID_COLUMNS)
    row = math.floor((y - top) / height * GRID_ROWS)
    is_inside = 0 <= column < GRID_COLUMNS and 0 <= row < GRID_ROWS
    if not is_inside and not is_clamped:
        return None
    return (min(max(row, 0), GRID_ROWS - 1), min(max(column, 0), GRID_COLUMNS - 1))


# ---- page_journal_fitter -------------------------------------------------------------
def page_journal_fitter(page: FigurePage,
                        specs: Dict[str, dict],
                        ) -> Tuple[FigurePage, Optional[str]]:
    """
    ---- Summary ----
    Main function to fit a page to the journals there are: a journal not in the
    journals folder becomes the standard journal, and a width the journal does not
    have becomes two columns, or its first width.

    ---- Inputs ----
    page : FigurePage
        The page, as made or as read from a template.
    specs : Dict[str, dict]
        The journals (config.JOURNAL_SPECS); the standard journal is among them.

    ---- Globals read ----
    STANDARD_COLUMNS, STANDARD_JOURNAL.

    ---- Outputs ----
    Tuple[FigurePage, Optional[str]]
        (the page fitted, one or two plain sentences on what was changed, or None).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    notes: List[str] = []
    journal = page.journal
    if journal not in specs:
        journal = STANDARD_JOURNAL
        notes.append(f'The journal {page.journal} is not in the journals folder, so '
                     f"the page is {specs[journal]['name']}'s.",
                     )
    widths = specs[journal]['widths_mm']
    columns = page.columns
    if columns not in widths:
        columns = STANDARD_COLUMNS if STANDARD_COLUMNS in widths else next(iter(widths))
        notes.append(f"{specs[journal]['name']} has no figure {page.columns:g} columns "
                     f'wide, so the page is {columns:g} columns wide.',
                     )
    fitted = replace(page, journal=journal, columns=columns)
    return fitted, ' '.join(notes) or None


# ---- page_offer_checker --------------------------------------------------------------
def page_offer_checker(page: FigurePage, kept: FigurePage) -> bool:
    """
    ---- Summary ----
    Main function to say whether to offer, once the page is built, to save it as a
    template: only when it holds a plot and is not the page last saved as a template,
    loaded from one, or started from.

    ---- Inputs ----
    page : FigurePage
        The page as built.
    kept : FigurePage
        The page as it was last saved, loaded or started (PageBuilder.kept_reader).

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True to offer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return bool(page.plots) and page != kept


# ---- page_picture_maker --------------------------------------------------------------
def page_picture_maker(page: FigurePage,
                       spec: dict,
                       dpi: float,
                       setup: Optional[dict] = None,
                       experiments: Optional[Dict[str, dict]] = None,
                       answers: Optional[dict] = None,
                       ) -> Image.Image:
    """
    ---- Summary ----
    Main function to draw a page as a picture for the plot area, off screen.

    ---- Inputs ----
    page : FigurePage
        The page.
    spec : dict
        What the page's journal asks (config.JOURNAL_SPECS entry).
    dpi : float
        Dots per inch (page_box_finder).
    setup : Optional[dict]
        The set-up table, as for figure_page_drawer.
    experiments : Optional[Dict[str, dict]]
        The slim copy of each experiment, as for figure_page_drawer.
    answers : Optional[dict]
        The answers of the run, as for figure_page_drawer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Image.Image
        The picture, in RGB.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_page_drawer
    """

    fig, _ = figure_page_drawer(page, spec, setup, experiments, answers)
    FigureCanvasAgg(fig)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=dpi, facecolor='white')
    buffer.seek(0)
    return Image.open(buffer).convert('RGB')


# ---- plot_box_finder -----------------------------------------------------------------
def plot_box_finder(plot: PagePlot,
                    box: Tuple[float, float, float, float],
                    ) -> Tuple[float, float, float, float]:
    """
    ---- Summary ----
    Main function to find where the cells of a plot are in the plot area.

    ---- Inputs ----
    plot : PagePlot
        The plot.
    box : Tuple[float, float, float, float]
        (left, top, width, height) of the page drawn, in pixels.

    ---- Globals read ----
    GRID_COLUMNS, GRID_ROWS.

    ---- Outputs ----
    Tuple[float, float, float, float]
        (x0, y0, x1, y1) in pixels, top left then bottom right.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    x0 = left + column / GRID_COLUMNS x width; x1 = left + (column + n_columns) /
    GRID_COLUMNS x width; the same down the rows.

    ---- Helpers ----
    None.
    """

    left, top, width, height = box
    return (left + plot.column / GRID_COLUMNS * width,
            top + plot.row / GRID_ROWS * height,
            left + (plot.column + plot.n_columns) / GRID_COLUMNS * width,
            top + (plot.row + plot.n_rows) / GRID_ROWS * height,
            )


# ---- plot_button_finder --------------------------------------------------------------
def plot_button_finder(x: float,
                       y: float,
                       page: FigurePage,
                       box: Tuple[float, float, float, float],
                       ) -> Optional[Tuple[str, int]]:
    """
    ---- Summary ----
    Main function to find the ✎ or ✕ button under a point of the plot area.

    ---- Inputs ----
    x, y : float
        The point, in pixels of the plot area.
    page : FigurePage
        The page.
    box : Tuple[float, float, float, float]
        (left, top, width, height) of the page drawn, in pixels.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Tuple[str, int]]
        ('edit' or 'remove', place of the plot in page.plots), or None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    plot_buttons_placer
    """

    for index, plot in enumerate(page.plots):
        for kind, (x0, y0, x1, y1) in plot_buttons_placer(plot, box).items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                return kind, index
    return None


# ---- plot_buttons_placer -------------------------------------------------------------
def plot_buttons_placer(plot: PagePlot,
                        box: Tuple[float, float, float, float],
                        ) -> Dict[str, Tuple[float, float, float, float]]:
    """
    ---- Summary ----
    Main function to place the ✎ and ✕ buttons of a plot in the top right corner of
    its cells, ✕ in the corner and ✎ left of it.

    ---- Inputs ----
    plot : PagePlot
        The plot.
    box : Tuple[float, float, float, float]
        (left, top, width, height) of the page drawn, in pixels.

    ---- Globals read ----
    BUTTON_GAP_PX, BUTTON_PX.

    ---- Outputs ----
    Dict[str, Tuple[float, float, float, float]]
        {'edit': (x0, y0, x1, y1), 'remove': (x0, y0, x1, y1)} in pixels.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    plot_box_finder
    """

    _, top, right, _ = plot_box_finder(plot, box)
    y0 = top + BUTTON_GAP_PX
    remove_x0 = right - BUTTON_GAP_PX - BUTTON_PX
    edit_x0 = remove_x0 - BUTTON_GAP_PX - BUTTON_PX
    return {'edit': (edit_x0, y0, edit_x0 + BUTTON_PX, y0 + BUTTON_PX),
            'remove': (remove_x0, y0, remove_x0 + BUTTON_PX, y0 + BUTTON_PX),
            }


# ---- template_names_lister -----------------------------------------------------------
def template_names_lister(folder: Path) -> List[str]:
    """
    ---- Summary ----
    Main function to list the templates in the layouts folder by name, A to Z.

    ---- Inputs ----
    folder : Path
        The layouts folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The names (file names without .json); empty when the folder is missing or
        cannot be read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        return sorted((path.stem for path in folder.glob('*.json') if path.is_file()),
                      key=str.lower,
                      )
    except OSError:
        return []
