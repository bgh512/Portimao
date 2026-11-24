"""
The five boxes above the plot: Time regions, View, Haem decomposition, Δψ and Figure.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import base64
import copy
import io
import math
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.event_concentrations import LABEL_MODES
from utils_shared.questions import typed_number_reader
from utils_shared.spectral_decomposer import (BACKGROUND_FORMULAS,
                                              BACKGROUND_SHORT_NAMES,
                                              fit_describer,
                                              fit_title_maker,
                                              OWN_HAEMS_NAME,
                                              )
from utils_shared.survey import JOURNAL_NAMES, TEMPERATURE_LIMITS_C


# ---- CONSTANTS -----------------------------------------------------------------------
# The numbers of the Δψ row: each haem's midpoint potential with the other haem
# oxidised and how far it falls when the other is reduced (mV), which the user types,
# then the numbers opened by "More options".
PSI_MIDPOINT_FIELDS = ('psi_bH_mV', 'psi_bL_mV', 'psi_fall_mV')
PSI_MORE_FIELDS = ('psi_share',
                   'temperature_c',
                   'psi_lowest_percent',
                   'psi_highest_percent',
                   )
PSI_FIELDS = PSI_MIDPOINT_FIELDS + PSI_MORE_FIELDS
# The answer each number of the "More options" line is kept in.
PSI_MORE_ANSWERS = {'psi_share': 'psi_share',
                    'temperature_c': 'temperature_c',
                    'psi_lowest_percent': 'psi_reduced_lowest_percent',
                    'psi_highest_percent': 'psi_reduced_highest_percent',
                    }
# The answers that hold the numbers of Δψ, kept with a decomposition to compare with.
PSI_KEPT_ANSWERS = (tuple(settings.DELTA_PSI_MIDPOINT_ANSWERS.values()) +
                    tuple(PSI_MORE_ANSWERS.values())
                    )
PAPER_TEXT = "Paper's values"
# The journal shown as "None": the standard size, on the page of the standard journal.
NO_JOURNAL = 'none'
NO_JOURNAL_TEXT = 'None (standard size)'
VALUE_NAMES = ('plot_haems',
               'fit_file',
               'haem_background',
               'haem_files',
               'compare',
               'kept',
               'compare_layout',
               'spectra',
               'haem_mode',
               'haem_per_od',
               'ocr_mode',
               'label_mode',
               'event_label_angle',
               'time_tab',
               'delta_psi',
               ) + PSI_FIELDS + ('journal',
                                 'columns',
                                 'height',
                                 )
# The ways of showing the haems, in the order of the "Haems as" drop-down, with its words.
HAEM_FORM_TEXTS = {'delta': 'ΔD (mOD)',
                   'percent': '% oxidised',
                   'abs': 'Absorbance (mOD)',
                   }
# The ways of showing the OCR, in the order of the "OCR as" drop-down, with its words.
OCR_FORM_TEXTS = {'raw': 'µM min⁻¹',
                  'od': 'per OD (µM min⁻¹ OD⁻¹)',
                  'percent': '% of the range',
                  'baseline': '% of baseline',
                  }
# What the event labels show, in the order of the "Labels as" drop-down, with its words.
LABEL_FORM_TEXTS = LABEL_MODES
# The button that folds the tick boxes of the library haems out and away.
BUILD_CLOSED_TEXT = 'Build a fit ▸'
BUILD_OPEN_TEXT = 'Build a fit ▾'
# The button that keeps the decomposition in use to compare the next ones with, the two
# that choose between it and the one on the plot, and the line under the first row that
# says which one is kept.
KEEP_TEXT = 'Keep to compare'
STOP_TEXT = 'Keep new'
BACK_TEXT = 'Keep old'
# What a click on BACK_TEXT is told as: a click, not a value the strip keeps.
BACK_CHANGE = 'go_back'
# The button that finds the components of the haem spectra from the whole dataset (a
# principal component analysis), and what a click on it is told as: a click, not a
# value the strip keeps.
PCA_TEXT = 'Do PCA'
PCA_CHANGE = 'do_pca'
# The button beside the Scatter drop-down that shows the formula of the scatter picked,
# written as a textbook writes it, and the size of that formula's letters (pt) and of
# its picture (dots per inch).
FORMULA_TEXT = 'ⓘ'
FORMULA_FONT_PT = 11
FORMULA_DPI = 100
FORMULA_NOTE = 'w: wavelength (nm); b₀, b₁, b₂: found by the fit'
# The button under Build a fit that saves the haems ticked as a fit file of their own,
# and what a click on it is told as: {SAVE_FIT_CHANGE: the name typed beside it}, not a
# value the strip keeps.
SAVE_FIT_TEXT = 'Save fit'
SAVE_FIT_CHANGE = 'save_fit'
# How the kept decomposition is shown, in the order of the switch beside Keep new, with
# its words, and the line saying which one is kept in each.
COMPARE_LAYOUT_TEXTS = {'side': 'Side by side', 'overlaid': 'Overlaid'}
KEPT_PREFIXES = {'side': 'Kept to compare (Old, the plot on the left): ',
                 'overlaid': 'Kept to compare (Old, faint on the plot): ',
                 }
# The button that saves one page of the journal as a PDF with the figure of the file
# shown on it, and what a click on it is told as: a click, not a value the strip keeps.
MASTER_TEXT = 'Export master'
MASTER_CHANGE = 'export_master'
# What a new order of the panels of the plot is told as: the keys of the panels on the
# plot, top first, after an arrow beside one moved it (the window tells it), or an
# empty list for the standard order, after a click on the button below. Not a value
# the strip keeps.
PANEL_ORDER_CHANGE = 'panel_order'
ORDER_TEXT = 'Standard order'
LAST_TICK_NOTE = 'One haem at least stays ticked: tick another first, or choose a preset.'
HEIGHT_HELP = 'a share of a page: a number above 0 and up to 1, such as 0.5'
ERROR_BACKGROUND = '#ffd6d6'
ERROR_TEXT = '#b00020'
NOTE_TEXT = '#404040'
MINUTES_HELP = 'Type a number of minutes, 0 or more.'
# What to type in a box of the edges row, by the unit of the step.
UNIT_HELP = {'min': MINUTES_HELP, 's': 'Type a number of seconds, 0 or more.'}
EVERY_FILE_TEXT = 'Apply to all'
# The tabs of the Time regions box, each with the edges it puts on the plot, and the
# line shown while none is pressed. A tab pressed is told as {TIME_TAB_CHANGE: tab}.
TIME_TAB_TEXTS = {'trim': 'Trim / Ignore',
                  'regions': 'Ox / Red',
                  'windows': 'Averaging',
                  }
TIME_TAB_CHANGE = 'time_tab'
TAB_NOTE = 'Press a tab to set its edges on the plot.'
# The buttons that open the OD table and the labels table again, and what a click on
# each is told as: a click, not a value the boxes keep.
EDIT_ODS_TEXT = 'Edit ODs'
EDIT_ODS_CHANGE = 'edit_ods'
EDIT_LABELS_TEXT = 'Edit labels'
EDIT_LABELS_CHANGE = 'edit_labels'
# The angle of the event labels (°).
ANGLE_LIMITS = (0.0, 90.0)
ANGLE_HELP = 'Type an angle from 0 (flat) to 90 (upright).'


# ---- EdgeRow -------------------------------------------------------------------------
class EdgeRow:
    """
    ---- Summary ----
    The row of the strip shown while edges are dragged on the plot: a typing box for
    each edge, holding its value for the file shown, and the "Apply to all" tick box.
    It
    follows the drag and passes on what the user types or ticks; it changes nothing by
    itself. Every method runs on the window thread.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the row, for the window to place.

    ---- Globals read ----
    ERROR_BACKGROUND, ERROR_TEXT, NOTE_TEXT.

    ---- Methods ----
    __init__
    _every_file_handler
    _tick_handler
    _value_handler
    every_file_unticker
    fields_setter
    ticks_setter
    toggles_setter
    values_setter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 parent: Any,
                 background: str,
                 on_value: Callable[[str, float], None],
                 on_every_file: Callable[[bool], None],
                 on_return: Callable[[], None],
                 on_tick: Optional[Callable[[str, bool], None]] = None,
                 on_toggle: Optional[Callable[[str, bool], None]] = None,
                 ) -> None:
        """
        ---- Summary ----
        Method to build the row, with no boxes until fields_setter, and no ticks or
        toggles until ticks_setter and toggles_setter.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        parent : Any
            The widget the row is built in.
        background : str
            Background colour of the row.
        on_value : Callable[[str, float], None]
            Called with (field, number) when a number is typed in a box.
        on_every_file : Callable[[bool], None]
            Called with the new state of the tick box when it is clicked.
        on_return : Callable[[], None]
            Called after Enter in a box has passed its number on (or found it as it
            was), so the keyboard can go back to the answer box.
        on_tick : Optional[Callable[[str, bool], None]]
            Called with (field, new state) when a numbered tick is clicked.
        on_toggle : Optional[Callable[[str, bool], None]]
            Called with (field, new state) when a toggle beside the tick box is
            clicked.

        ---- Globals read ----
        NOTE_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _every_file_handler
        """

        self._tk = tk
        self._background = background
        self._on_value = on_value
        self._on_every_file = on_every_file
        self._on_return = on_return
        self._on_tick = on_tick
        self._on_toggle = on_toggle
        self._boxes: Dict[str, Any] = {}
        self._shown: Dict[str, str] = {}
        self._tick_vars: Dict[str, Any] = {}
        self._toggle_vars: Dict[str, Any] = {}
        self.frame = tk.Frame(parent, bg=background)
        self._boxes_frame = tk.Frame(self.frame, bg=background)
        self._boxes_frame.pack(side='top', anchor='w')
        # the numbered ticks of the windows, with the note of which window the boxes
        # show
        self._ticks_frame = tk.Frame(self.frame, bg=background)
        self._ticks_frame.pack(side='top', anchor='w')
        self._row_note: Any = None
        # the tick box and the note on a line of their own, so the row fits its box
        under = tk.Frame(self.frame, bg=background)
        under.pack(side='top', anchor='w')
        self._help = UNIT_HELP['min']
        self._every_file = tk.BooleanVar(master=parent, value=False)
        self._tick = tk.Checkbutton(under,
                                    text=EVERY_FILE_TEXT,
                                    variable=self._every_file,
                                    command=self._every_file_handler,
                                    bg=background,
                                    activebackground=background,
                                    highlightthickness=0,
                                    )
        self._tick.pack(side='left', padx=(0, 4))
        self._toggles_frame = tk.Frame(under, bg=background)
        self._toggles_frame.pack(side='left')
        self._note = tk.Label(under, text='', bg=background, fg=NOTE_TEXT)
        self._note.pack(side='left', padx=(0, 4))

    # ---- ROW HELPERS -----------------------------------------------------------------

    # ---- _every_file_handler ---------------------------------------------------------
    def _every_file_handler(self) -> None:
        """
        ---- Summary ----
        Method to pass on the new state of the "Apply to all" tick box.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_every_file (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._on_every_file(bool(self._every_file.get()))

    # ---- _tick_handler ---------------------------------------------------------------
    def _tick_handler(self, field: str, is_toggle: bool) -> None:
        """
        ---- Summary ----
        Method to pass on the new state of a numbered tick or of a toggle.

        ---- Inputs ----
        field : str
            The field of the tick or toggle.
        is_toggle : bool
            True for a toggle beside the tick box.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_tick or on_toggle (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        kept = self._toggle_vars if is_toggle else self._tick_vars
        handler = self._on_toggle if is_toggle else self._on_tick
        if handler is not None and field in kept:
            handler(field, bool(kept[field].get()))

    # ---- _value_handler --------------------------------------------------------------
    def _value_handler(self, key: str, is_return: bool = False) -> None:
        """
        ---- Summary ----
        Method to take the number typed in one box, when Enter is pressed or the box is
        left; a box left as it was shown passes nothing on. A number that cannot be
        used turns the box red, with the reason beside the tick box, and keeps the
        keyboard; after Enter, any other answer gives it back to the answer box.

        ---- Inputs ----
        key : str
            The field of the box.
        is_return : bool
            True when Enter was pressed in the box.

        ---- Globals read ----
        ERROR_BACKGROUND, ERROR_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the box and calls the function given as on_value (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        minutes_checker
        """

        box = self._boxes.get(key)
        if box is None:
            return
        text = box.get().strip()
        if text != self._shown.get(key):
            value, _ = minutes_checker(text)
            if value is None:
                box.configure(bg=ERROR_BACKGROUND)
                self._note.configure(text=self._help, fg=ERROR_TEXT)
                return
            self._note.configure(text='')
            self._on_value(key, value)
        box.configure(bg='white')
        if is_return:
            self._on_return()

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- every_file_unticker ---------------------------------------------------------
    def every_file_unticker(self) -> None:
        """
        ---- Summary ----
        Method to untick the "Apply to all" tick box without passing anything on, when
        another file is shown.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the tick box (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._every_file.set(False)

    # ---- fields_setter ---------------------------------------------------------------
    def fields_setter(self,
                      fields: List[Tuple[str, str]],
                      is_every_file: bool,
                      unit: str = 'min',
                      tick_text: str = EVERY_FILE_TEXT,
                      ) -> None:
        """
        ---- Summary ----
        Method to make one typing box for each field, each after its name, and set the
        tick box and its words. A name starting with a capital starts a new line (Trim
        before ... after, then Ignore before ... after), and each line ends with the
        unit.

        ---- Inputs ----
        fields : List[Tuple[str, str]]
            [(field, name shown before its box)] in order.
        is_every_file : bool
            Whether the tick box is ticked.
        unit : str
            The unit written after the boxes: 'min' or 's' (a key of UNIT_HELP).
        tick_text : str
            The words of the tick box: "Apply to all", or those of the step's own
            switch.

        ---- Globals read ----
        EVERY_FILE_TEXT, UNIT_HELP.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the boxes (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _value_handler
        """

        tk, background = self._tk, self._background
        for child in self._boxes_frame.winfo_children():
            child.destroy()
        self._boxes, self._shown = {}, {}
        # A name with a capital starts a line of its own (Trim, then Ignore), and each
        # line ends with the unit.
        line = None
        for key, name in fields:
            if line is None or name[:1].isupper():
                if line is not None:
                    tk.Label(line, text=unit, bg=background).pack(side='left',
                                                                  padx=(4, 0),
                                                                  )
                line = tk.Frame(self._boxes_frame, bg=background)
                line.pack(side='top', anchor='w', pady=(0, 1))
                gap = 0
            else:
                gap = 4
            tk.Label(line,
                     text=name,
                     bg=background,
                     ).pack(side='left', padx=(gap, 4))
            box = tk.Entry(line,
                           width=6,
                           justify='right',
                           bg='white',
                           relief='solid',
                           borderwidth=1,
                           )
            box.pack(side='left')
            box.bind('<Return>',
                     lambda event, name=key: self._value_handler(name, True),
                     )
            box.bind('<FocusOut>', lambda event, name=key: self._value_handler(name))
            self._boxes[key] = box
        if line is not None:
            tk.Label(line, text=unit, bg=background).pack(side='left', padx=(4, 0))
        self._help = UNIT_HELP[unit]
        self._tick.configure(text=tick_text)
        self._every_file.set(is_every_file)
        self._note.configure(text='')

    # ---- ticks_setter ----------------------------------------------------------------
    def ticks_setter(self, note: str, ticks: List[Tuple[str, str, bool]]) -> None:
        """
        ---- Summary ----
        Method to show the numbered ticks under the boxes ("Use: 1 2 3"), one per
        window of the file shown, and the note of which window the boxes show. The
        ticks are made again only when they change.

        ---- Inputs ----
        note : str
            The note beside the ticks ('settled window 2'), or ''.
        ticks : List[Tuple[str, str, bool]]
            [(field, words, is_ticked)]; empty for none.

        ---- Globals read ----
        NOTE_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the ticks (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _tick_handler
        """

        tk, background = self._tk, self._background
        if not ticks and not note:
            # nothing to show, so the line takes no room
            for child in self._ticks_frame.winfo_children():
                child.destroy()
            self._tick_vars, self._row_note = {}, None
            return
        fields = [field for field, _, _ in ticks]
        if fields != list(self._tick_vars) or self._row_note is None:
            for child in self._ticks_frame.winfo_children():
                child.destroy()
            self._tick_vars = {}
            if ticks:
                tk.Label(self._ticks_frame,
                         text='Use:',
                         bg=background,
                         ).pack(side='left', padx=(0, 4))
            for field, words, _ in ticks:
                variable = tk.BooleanVar(master=self._ticks_frame, value=True)
                tk.Checkbutton(self._ticks_frame,
                               text=words,
                               variable=variable,
                               command=lambda name=field: self._tick_handler(name,
                                                                             False,
                                                                             ),
                               bg=background,
                               activebackground=background,
                               highlightthickness=0,
                               ).pack(side='left')
                self._tick_vars[field] = variable
            self._row_note = tk.Label(self._ticks_frame,
                                      text='',
                                      bg=background,
                                      fg=NOTE_TEXT,
                                      )
            self._row_note.pack(side='left', padx=(8, 0))
        for field, _, is_ticked in ticks:
            self._tick_vars[field].set(is_ticked)
        self._row_note.configure(text=note)

    # ---- toggles_setter --------------------------------------------------------------
    def toggles_setter(self, toggles: List[Tuple[str, str, bool]]) -> None:
        """
        ---- Summary ----
        Method to show the toggles beside the tick box ("Adjust each window"); they
        are made again only when they change.

        ---- Inputs ----
        toggles : List[Tuple[str, str, bool]]
            [(field, words, is_on)]; empty for none.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the toggles (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _tick_handler
        """

        tk, background = self._tk, self._background
        fields = [field for field, _, _ in toggles]
        if fields != list(self._toggle_vars):
            for child in self._toggles_frame.winfo_children():
                child.destroy()
            self._toggle_vars = {}
            for field, words, _ in toggles:
                variable = tk.BooleanVar(master=self._toggles_frame, value=False)
                tk.Checkbutton(self._toggles_frame,
                               text=words,
                               variable=variable,
                               command=lambda name=field: self._tick_handler(name,
                                                                             True,
                                                                             ),
                               bg=background,
                               activebackground=background,
                               highlightthickness=0,
                               ).pack(side='left', padx=(0, 4))
                self._toggle_vars[field] = variable
        for field, _, is_on in toggles:
            self._toggle_vars[field].set(is_on)

    # ---- values_setter ---------------------------------------------------------------
    def values_setter(self, values: Optional[Dict[str, float]]) -> None:
        """
        ---- Summary ----
        Method to show the values of the file shown in the boxes.

        ---- Inputs ----
        values : Optional[Dict[str, float]]
            {field: value}, or None to empty the boxes.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the boxes (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        for key, box in self._boxes.items():
            text = '' if values is None else f'{round(values[key], 2):g}'
            box.configure(bg='white')
            box.delete(0, 'end')
            box.insert(0, text)
            self._shown[key] = text
        self._note.configure(text='')


# ---- SettingsStrip -------------------------------------------------------------------
class SettingsStrip:
    """
    ---- Summary ----
    The five boxes above the plot, in one row, that always show the current choices.
    Time regions: a tab each for the trim and ignore edges, the oxidised and reduced
    regions and the averaging windows, the one pressed having its edges on the plot
    (the window places their rows in the box). View: how the OCR is shown with its per
    OD box, how the haems are shown with theirs (the per OD boxes and Edit ODs only
    once OD values were entered), what the event labels show, their angle and Edit
    labels. Haem decomposition, with its tick as title, in this order: the
    spectrometer whose spectra hold the haems (shown when the files share more than
    one), the background (the scatter) with a button that shows its formula, the fit
    (each shown by its name), a button that folds out a tick box for each haem of the
    library with a name box and Save fit under them (Build a fit) beside the button
    that finds the components from the data (Do PCA), and a button that keeps the
    decomposition in use to compare the next ones with (greyed while one is kept,
    with a line saying which one, and Keep old and Keep new under it to choose between
    the two). Δψ, with its tick as title (it can be clicked only while Δψ can be worked
    out): the midpoint of bH and of bL (written as in the figures) and the shift typed,
    each midpoint with the other haem reduced filled in, a button for the paper's
    values, and the share, the temperature and the limits as text, or as boxes when
    "More options" is ticked. Figure: the journal, the widths that journal allows, the
    height, a button that exports the master page and a button that puts the panels of
    the plot back in the standard order. It tells the window what the user changed and
    can be set by the program; it changes nothing by itself. It starts greyed out,
    until the program says it is listening. Every method runs on the window thread,
    except values_reader.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the boxes, for the window to place.
    time_box : Any
        The Time regions box, where the window places the rows of the edges.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS, JOURNAL_NAMES,
    BACKGROUND_SHORT_NAMES, OWN_HAEMS_NAME and the module constants.

    ---- Methods ----
    __init__
    _angle_handler
    _back_handler
    _background_handler
    _build_toggler
    _change_reporter
    _compare_handler
    _edit_handler
    _fit_handler
    _fit_saver
    _form_handler
    _formula_toggler
    _haems_handler
    _height_handler
    _journal_handler
    _label_mode_handler
    _master_handler
    _more_toggler
    _ocr_handler
    _order_handler
    _paper_handler
    _pca_handler
    _per_od_handler
    _psi_handler
    _psi_tick_handler
    _size_refresher
    _spectra_handler
    _tick_handler
    _time_tab_handler
    _width_handler
    choices_setter
    fits_setter
    library_setter
    state_setter
    values_reader
    values_setter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 ttk: Any,
                 parent: Any,
                 background: str,
                 on_change: Callable[[Dict[str, Any]], None],
                 ) -> None:
        """
        ---- Summary ----
        Method to build the strip with the standard settings in it.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        ttk : Any
            The tkinter.ttk module.
        parent : Any
            The widget the strip is built in.
        background : str
            Background colour of the strip.
        on_change : Callable[[Dict[str, Any]], None]
            Called once for each change the user makes, with {name: value} of every
            value that changed (a new journal can change the width and the height
            too); the names are those of VALUE_NAMES.

        ---- Globals read ----
        settings.DEFAULT_ANSWERS, JOURNAL_NAMES, NO_JOURNAL, NO_JOURNAL_TEXT,
        NOTE_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _angle_handler
        _back_handler
        _background_handler
        _build_toggler
        _compare_handler
        _edit_handler
        _fit_handler
        _fit_saver
        _form_handler
        _formula_toggler
        _haems_handler
        _height_handler
        _journal_handler
        _label_mode_handler
        _layout_handler
        _master_handler
        _more_toggler
        _ocr_handler
        _order_handler
        _paper_handler
        _pca_handler
        _per_od_handler
        _psi_handler
        _psi_tick_handler
        _size_refresher
        _spectra_handler
        _time_tab_handler
        _width_handler
        psi_values_builder
        """

        # ---- 1 The values, starting from the standard settings -----------------------
        standard = settings.DEFAULT_ANSWERS
        self._on_change = on_change
        self._standard_size = (standard['columns'], standard['height'])
        self._custom_size = self._standard_size
        self._values: Dict[str, Any] = {'plot_haems': standard['plot_haems'],
                                        'fit_file': standard['fit_file'],
                                        'haem_background': standard['haem_background'],
                                        'haem_files': [],
                                        'compare': False,
                                        'kept': '',
                                        'compare_layout': standard['compare_layout'],
                                        'spectra': standard['decomposition_dataset'],
                                        'haem_mode': standard['haem_mode'],
                                        'haem_per_od': bool(standard['haem_per_od']),
                                        'ocr_mode': standard['ocr_mode'],
                                        'label_mode': standard['label_mode'],
                                        'event_label_angle': float(
                                            standard['event_label_angle'],
                                            ),
                                        'time_tab': '',
                                        'journal': NO_JOURNAL,
                                        'columns': standard['columns'],
                                        'height': standard['height'],
                                        **psi_values_builder(standard, False),
                                        }
        self._is_more_open = False
        self._journals = [NO_JOURNAL] + list(JOURNAL_NAMES)
        self._backgrounds = list(BACKGROUND_SHORT_NAMES)
        self._width_columns: List[float] = []
        self._spectra_names: List[str] = []
        self._form_keys: List[str] = []
        self._ocr_keys: List[str] = []
        self._has_percent = False
        self._has_od = False
        self._has_baseline = False
        self._has_psi = False
        self._fit_names: List[str] = [self._values['fit_file']]
        self._fit_titles: Dict[str, str] = {}
        self._haems_by_file: Dict[str, str] = {}
        self._tick_vars: Dict[str, Any] = {}
        self._tick_boxes: Dict[str, Any] = {}
        self._is_enabled = False
        self._is_panel_open = False
        self._tk = tk
        self._background = background
        self.frame = tk.Frame(parent, bg=background)

        # ---- 2 The five boxes, in one row --------------------------------------------
        # The Haem decomposition and Δψ boxes have a tick box as their title.
        def frame_maker(column: int, title: Any) -> Any:
            options = ({'text': title} if isinstance(title, str)
                       else {'labelwidget': title}
                       )
            box = tk.LabelFrame(self.frame,
                                bg=background,
                                padx=4,
                                pady=2,
                                **options,
                                )
            box.grid(row=0, column=column, sticky='nsew', padx=3)
            return box
        def tick_maker(text: str,
                       variable: Any,
                       command: Callable[[], None],
                       holder: Any = None,
                       ) -> Any:
            return tk.Checkbutton(self.frame if holder is None else holder,
                                  text=text,
                                  variable=variable,
                                  command=command,
                                  bg=background,
                                  activebackground=background,
                                  highlightthickness=0,
                                  )
        def line_maker(box: Any) -> Any:
            line = tk.Frame(box, bg=background)
            line.pack(anchor='w', pady=(0, 2))
            return line

        # ---- 2.1 Time regions: one tab of edges at a time ----------------------------
        # The window packs the rows of the edges under the tabs (time_box).
        self.time_box = frame_maker(0, 'Time regions')
        tabs = tk.Frame(self.time_box, bg=background)
        tabs.pack(anchor='w', pady=(0, 2))
        self._tab_buttons: Dict[str, Any] = {}
        for tab, words in TIME_TAB_TEXTS.items():
            button = tk.Button(tabs,
                               text=words,
                               command=lambda chosen=tab: self._time_tab_handler(chosen),
                               )
            button.pack(side='left', padx=(0, 2))
            self._tab_buttons[tab] = button
        self._tab_note = tk.Label(self.time_box,
                                  text=TAB_NOTE,
                                  bg=background,
                                  fg=NOTE_TEXT,
                                  anchor='w',
                                  )

        # ---- 2.2 View: how the OCR, the haems and the labels are shown ---------------
        # _size_refresher places the per OD boxes and Edit ODs only when OD values were
        # entered.
        view = frame_maker(1, 'View')
        line = line_maker(view)
        tk.Label(line, text='OCR as', bg=background).pack(side='left', padx=(0, 4))
        self._ocr_combo = ttk.Combobox(line, state='readonly', width=15)
        self._ocr_combo.pack(side='left', padx=(0, 4))
        self._ocr_od = tk.BooleanVar(master=parent, value=False)
        self._ocr_od_box = tick_maker('per OD', self._ocr_od, self._ocr_handler, line)
        line = line_maker(view)
        self._form_label = tk.Label(line, text='Haems as', bg=background)
        self._form_label.pack(side='left', padx=(0, 4))
        self._form_combo = ttk.Combobox(line, state='readonly', width=15)
        self._form_combo.pack(side='left', padx=(0, 4))
        self._haem_od = tk.BooleanVar(master=parent, value=self._values['haem_per_od'])
        self._haem_od_box = tick_maker('per OD',
                                       self._haem_od,
                                       lambda: self._per_od_handler('haem_per_od'),
                                       line,
                                       )
        line = line_maker(view)
        tk.Label(line, text='Labels as', bg=background).pack(side='left', padx=(0, 4))
        self._label_mode_combo = ttk.Combobox(line,
                                              state='readonly',
                                              width=15,
                                              values=list(LABEL_FORM_TEXTS.values()),
                                              )
        self._label_mode_combo.pack(side='left')
        self._angle_line = line_maker(view)
        tk.Label(self._angle_line,
                 text='Label angle',
                 bg=background,
                 ).pack(side='left', padx=(0, 4))
        self._angle_entry = tk.Entry(self._angle_line,
                                     width=5,
                                     justify='right',
                                     bg='white',
                                     disabledbackground=background,
                                     relief='solid',
                                     borderwidth=1,
                                     )
        self._angle_entry.pack(side='left')
        tk.Label(self._angle_line, text='°', bg=background).pack(side='left',
                                                                 padx=(2, 0),
                                                                 )
        # Edit ODs is always there, so OD values can be given later even after No.
        line = self._edit_line = line_maker(view)
        self._edit_ods_button = tk.Button(line,
                                          text=EDIT_ODS_TEXT,
                                          command=lambda: self._edit_handler(EDIT_ODS_CHANGE,
                                                                             ),
                                          )
        self._edit_ods_button.pack(side='left', padx=(0, 4))
        self._edit_labels_button = tk.Button(line,
                                             text=EDIT_LABELS_TEXT,
                                             command=lambda: self._edit_handler(EDIT_LABELS_CHANGE,
                                                                                ),
                                             )
        self._edit_labels_button.pack(side='left')
        self._angle_note = tk.Label(view, text='', bg=background, fg=ERROR_TEXT)

        # ---- 2.3 Haem decomposition: the fit, the background and the spectra ---------
        self._haems = tk.BooleanVar(master=parent, value=self._values['plot_haems'])
        self._haems_box = tick_maker('Haem decomposition',
                                     self._haems,
                                     self._haems_handler,
                                     )
        haem_box = frame_maker(2, self._haems_box)
        # In order: Spectra (placed only when the files share more than one
        # spectrometer), Scatter with the button of its formula, Fit, then Build a fit
        # with Do PCA, and Keep to compare.
        self._spectra_line = line_maker(haem_box)
        tk.Label(self._spectra_line,
                 text='Spectra',
                 width=7,
                 anchor='w',
                 bg=background,
                 ).pack(side='left', padx=(0, 4))
        self._spectra_combo = ttk.Combobox(self._spectra_line,
                                           state='readonly',
                                           width=8,
                                           )
        self._spectra_combo.pack(side='left')
        self._scatter_line = line_maker(haem_box)
        tk.Label(self._scatter_line,
                 text='Scatter',
                 width=7,
                 anchor='w',
                 bg=background,
                 ).pack(side='left', padx=(0, 4))
        self._background_combo = ttk.Combobox(self._scatter_line,
                                              state='readonly',
                                              width=16,
                                              values=list(
                                                  BACKGROUND_SHORT_NAMES.values(),
                                                  ),
                                              )
        self._background_combo.pack(side='left', padx=(0, 4))
        self._formula_button = tk.Button(self._scatter_line,
                                         text=FORMULA_TEXT,
                                         command=self._formula_toggler,
                                         padx=2,
                                         pady=0,
                                         )
        self._formula_button.pack(side='left')
        # the formula of the scatter picked, shown while the button is pressed in
        self._is_formula_open = False
        self._formula_pictures: Dict[str, Any] = {}
        self._formula_line = tk.Frame(haem_box, bg=background)
        self._formula_label = tk.Label(self._formula_line, bg=background)
        self._formula_label.pack(anchor='w')
        self._formula_note = tk.Label(self._formula_line,
                                      text='',
                                      bg=background,
                                      fg=NOTE_TEXT,
                                      justify='left',
                                      wraplength=260,
                                      )
        self._formula_note.pack(anchor='w')
        self._fit_line = line_maker(haem_box)
        tk.Label(self._fit_line,
                 text='Fit',
                 width=7,
                 anchor='w',
                 bg=background,
                 ).pack(side='left', padx=(0, 4))
        self._fit_combo = ttk.Combobox(self._fit_line,
                                       state='readonly',
                                       width=24,
                                       values=[self._values['fit_file']],
                                       )
        self._fit_combo.set(fit_title_maker(self._values['fit_file'], {}))
        self._fit_combo.pack(side='left')
        upper = line_maker(haem_box)
        self._build_button = tk.Button(upper,
                                       text=BUILD_CLOSED_TEXT,
                                       command=self._build_toggler,
                                       )
        self._build_button.pack(side='left', padx=(0, 4))
        self._pca_button = tk.Button(upper, text=PCA_TEXT, command=self._pca_handler)
        self._pca_button.pack(side='left', padx=(0, 4))
        self._upper = upper
        self._keep_line = line_maker(haem_box)
        self._compare_button = tk.Button(self._keep_line,
                                         text=KEEP_TEXT,
                                         command=self._compare_handler,
                                         )
        self._compare_button.pack(side='left', padx=(0, 4))
        # Keep old and Keep new, on a line under Keep to compare: _size_refresher
        # places it only while a decomposition is kept.
        self._choose_line = tk.Frame(haem_box, bg=background)
        self._back_button = tk.Button(self._choose_line,
                                      text=BACK_TEXT,
                                      command=self._back_handler,
                                      )
        self._back_button.pack(side='left', padx=(0, 4))
        self._new_button = tk.Button(self._choose_line,
                                     text=STOP_TEXT,
                                     command=self._compare_handler,
                                     )
        self._new_button.pack(side='left', padx=(0, 8))
        # the switch between the kept plot beside the one in use and dashed over it
        self._layout_buttons: Dict[str, Any] = {}
        for layout, words in COMPARE_LAYOUT_TEXTS.items():
            button = tk.Button(self._choose_line,
                               text=words,
                               command=lambda chosen=layout: self._layout_handler(chosen),
                               )
            button.pack(side='left', padx=(0, 2))
            self._layout_buttons[layout] = button

        # ---- 2.3.1 The tick boxes of the library haems, folded away at first ---------
        # library_setter fills them in, above the line that saves the haems ticked as a
        # fit of its own.
        self._panel = tk.Frame(haem_box, bg=background)
        self._library = tk.Frame(self._panel, bg=background)
        self._library.pack(anchor='w')
        line = line_maker(self._panel)
        tk.Label(line, text='Name', bg=background).pack(side='left', padx=(4, 4))
        self._fit_name_entry = tk.Entry(line,
                                        width=18,
                                        bg='white',
                                        disabledbackground=background,
                                        relief='solid',
                                        borderwidth=1,
                                        )
        self._fit_name_entry.pack(side='left', padx=(0, 4))
        self._fit_name_entry.bind('<Return>', lambda event: self._fit_saver())
        self._save_button = tk.Button(line, text=SAVE_FIT_TEXT, command=self._fit_saver)
        self._save_button.pack(side='left')

        # ---- 2.3.2 The line saying which decomposition is kept, hidden until one is --
        self._kept_label = tk.Label(haem_box,
                                    text='',
                                    bg=background,
                                    fg=NOTE_TEXT,
                                    anchor='w',
                                    justify='left',
                                    wraplength=260,
                                    )

        # ---- 2.4 Δψ: its tick, then the numbers of the method while it is ticked -----
        # Each haem's midpoint, typed, then (after the arrow) its midpoint with the
        # other haem reduced, filled in and not typed in; the fall; the button of the
        # paper's values and the box that opens the other numbers, as text or as boxes
        # when "More options" is ticked.
        self._psi_on = tk.BooleanVar(master=parent, value=False)
        self._psi_tick = tick_maker('Δψ', self._psi_on, self._psi_tick_handler)
        psi_box = frame_maker(3, self._psi_tick)
        self._psi_row = tk.Frame(psi_box, bg=background)
        self._psi_boxes: Dict[str, Any] = {}
        self._psi_seconds: Dict[str, Any] = {}

        def entry_maker(parent_line: Any, name: str, gap: Tuple[int, int]) -> None:
            box = tk.Entry(parent_line,
                           width=6,
                           justify='right',
                           bg='white',
                           disabledbackground=background,
                           relief='solid',
                           borderwidth=1,
                           )
            box.pack(side='left', padx=gap)
            box.bind('<Return>', lambda event, chosen=name: self._psi_handler(chosen))
            box.bind('<FocusOut>', lambda event, chosen=name: self._psi_handler(chosen))
            self._psi_boxes[name] = box

        # The haem names as in the figures: b in italics, then its letter smaller and
        # lower (the font is read from Tk's own, so it matches the other words).
        fonts = getattr(tk, 'font', None)  # tkinter.font, once the window imported it
        base = (fonts.nametofont('TkDefaultFont').actual() if fonts is not None
                else {'family': 'Helvetica', 'size': 9}
                )
        family, size = base['family'], abs(int(base['size'])) or 9
        for letter, name in (('H', 'psi_bH_mV'), ('L', 'psi_bL_mV')):
            first = line_maker(self._psi_row)
            haem = tk.Frame(first, bg=background, width=34, height=22)
            haem.pack_propagate(False)
            haem.pack(side='left')
            tk.Label(haem,
                     text='b',
                     font=(family, size + 1, 'italic'),
                     bg=background,
                     padx=0,
                     ).pack(side='left', anchor='n')
            tk.Label(haem,
                     text=letter,
                     font=(family, max(size - 2, 6), 'italic'),
                     bg=background,
                     padx=0,
                     ).pack(side='left', anchor='s')
            entry_maker(first, name, (0, 2))
            tk.Label(first, text='→', bg=background).pack(side='left', padx=(0, 2))
            second = tk.Entry(first,
                              width=6,
                              justify='right',
                              readonlybackground=background,
                              fg=NOTE_TEXT,
                              relief='flat',
                              state='readonly',
                              takefocus=0,
                              )
            second.pack(side='left')
            tk.Label(first, text='mV', bg=background).pack(side='left', padx=(2, 0))
            self._psi_seconds[name] = second
        first = line_maker(self._psi_row)
        tk.Label(first, text='shift', width=4, anchor='w', bg=background).pack(
            side='left',
            )
        entry_maker(first, 'psi_fall_mV', (0, 2))
        tk.Label(first, text='mV', bg=background).pack(side='left')
        first = line_maker(self._psi_row)
        self._paper_button = tk.Button(first,
                                       text=PAPER_TEXT,
                                       command=self._paper_handler,
                                       )
        self._paper_button.pack(side='left', padx=(0, 8))
        self._more = tk.BooleanVar(master=parent, value=False)
        self._more_box = tk.Checkbutton(first,
                                        text='More options',
                                        variable=self._more,
                                        command=self._more_toggler,
                                        bg=background,
                                        activebackground=background,
                                        highlightthickness=0,
                                        )
        self._more_box.pack(side='left', padx=(0, 4))
        self._psi_summary = tk.Label(self._psi_row,
                                     text='',
                                     bg=background,
                                     fg=NOTE_TEXT,
                                     justify='left',
                                     wraplength=220,
                                     )
        self._psi_more = tk.Frame(self._psi_row, bg=background)
        for words, name, after in (('Share', 'psi_share', ''),
                                   ('Temperature', 'temperature_c', '°C'),
                                   ('Given between', 'psi_lowest_percent', ''),
                                   ('and', 'psi_highest_percent', '% reduced'),
                                   ):
            more_line = line_maker(self._psi_more)
            tk.Label(more_line, text=words, bg=background).pack(side='left',
                                                                padx=(0, 4),
                                                                )
            entry_maker(more_line, name, (0, 2))
            tk.Label(more_line, text=after, bg=background).pack(side='left')
        self._psi_note = tk.Label(self._psi_row,
                                  text='',
                                  bg=background,
                                  fg=ERROR_TEXT,
                                  justify='left',
                                  wraplength=220,
                                  )

        # ---- 2.5 Figure: the journal, the width and the height -----------------------
        figure_box = frame_maker(4, 'Figure')
        line = line_maker(figure_box)
        tk.Label(line, text='Journal', bg=background).pack(side='left', padx=(0, 4))
        self._journal_combo = ttk.Combobox(line,
                                           state='readonly',
                                           width=19,
                                           values=[NO_JOURNAL_TEXT]
                                           + list(JOURNAL_NAMES.values()),
                                           )
        self._journal_combo.pack(side='left')
        line = line_maker(figure_box)
        tk.Label(line, text='Width', bg=background).pack(side='left', padx=(0, 4))
        self._width_combo = ttk.Combobox(line, state='readonly', width=20)
        self._width_combo.pack(side='left')
        lower = line_maker(figure_box)
        tk.Label(lower, text='Height', bg=background).pack(side='left', padx=(0, 4))
        self._height_entry = tk.Entry(lower,
                                      width=6,
                                      justify='right',
                                      bg='white',
                                      disabledbackground=background,
                                      relief='solid',
                                      borderwidth=1,
                                      )
        self._height_entry.pack(side='left', padx=(0, 4))
        self._note = tk.Label(lower, text='', bg=background, fg=NOTE_TEXT, anchor='w')
        self._note.pack(side='left', padx=(0, 4))
        line = line_maker(figure_box)
        # the button that saves a page of the journal with the figure on it
        self._master_button = tk.Button(line,
                                        text=MASTER_TEXT,
                                        command=self._master_handler,
                                        )
        self._master_button.pack(side='left', padx=(0, 4))
        # the button that puts the panels of the plot back in the standard order
        self._order_button = tk.Button(line,
                                       text=ORDER_TEXT,
                                       command=self._order_handler,
                                       )
        self._order_button.pack(side='left')

        # ---- 3 What the user does ----------------------------------------------------
        self._angle_entry.bind('<Return>', self._angle_handler)
        self._angle_entry.bind('<FocusOut>', self._angle_handler)
        self._fit_combo.bind('<<ComboboxSelected>>', self._fit_handler)
        self._spectra_combo.bind('<<ComboboxSelected>>', self._spectra_handler)
        self._form_combo.bind('<<ComboboxSelected>>', self._form_handler)
        self._ocr_combo.bind('<<ComboboxSelected>>', self._ocr_handler)
        self._label_mode_combo.bind('<<ComboboxSelected>>', self._label_mode_handler)
        self._background_combo.bind('<<ComboboxSelected>>', self._background_handler)
        self._journal_combo.bind('<<ComboboxSelected>>', self._journal_handler)
        self._width_combo.bind('<<ComboboxSelected>>', self._width_handler)
        self._height_entry.bind('<Return>', self._height_handler)
        self._height_entry.bind('<FocusOut>', self._height_handler)
        self._size_refresher()

    # ---- STRIP HELPERS ---------------------------------------------------------------

    # ---- _angle_handler --------------------------------------------------------------
    def _angle_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the angle of the event labels typed in the View box, when Enter
        is pressed or the box is left; a box left as it was shown passes nothing on.
        An angle that cannot be used turns the box red, with the reason under it, and
        the angle in use stays.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        ANGLE_HELP, ANGLE_LIMITS, ERROR_BACKGROUND.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        typed_number_reader
        """

        if str(self._angle_entry.cget('state')) == 'disabled':
            return
        angle = typed_number_reader(self._angle_entry.get())
        if angle == self._values['event_label_angle']:
            self._size_refresher()
            return
        if angle is None or not ANGLE_LIMITS[0] <= angle <= ANGLE_LIMITS[1]:
            self._angle_entry.configure(bg=ERROR_BACKGROUND)
            self._angle_note.configure(text=ANGLE_HELP)
            self._angle_note.pack(anchor='w', before=self._edit_line)
            return
        before = dict(self._values)
        self._values['event_label_angle'] = float(angle)
        self._size_refresher()
        self._change_reporter(before)

    # ---- _background_handler ---------------------------------------------------------
    def _background_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the background picked in the drop-down.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        """

        before = dict(self._values)
        self._values['haem_background'] = self._backgrounds[
            self._background_combo.current()
            ]
        self._background_combo.selection_clear()
        self._change_reporter(before)

    # ---- _back_handler ---------------------------------------------------------------
    def _back_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the button that goes back to the kept decomposition. The strip
        keeps nothing: the click is told as {BACK_CHANGE: True}, and the program sets
        the strip to the kept values.

        ---- Inputs ----
        None.

        ---- Globals read ----
        BACK_CHANGE.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_change (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._values['compare']:
            self._on_change({BACK_CHANGE: True})

    # ---- _build_toggler --------------------------------------------------------------
    def _build_toggler(self) -> None:
        """
        ---- Summary ----
        Method to fold the tick boxes of the library haems out under the first row, or
        away again.

        ---- Inputs ----
        None.

        ---- Globals read ----
        BUILD_CLOSED_TEXT, BUILD_OPEN_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Shows or hides the panel (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._is_panel_open = not self._is_panel_open
        if self._is_panel_open:
            self._panel.pack(after=self._upper, pady=(0, 3), fill='x')
            self._build_button.configure(text=BUILD_OPEN_TEXT)
        else:
            self._panel.pack_forget()
            self._build_button.configure(text=BUILD_CLOSED_TEXT)

    # ---- _change_reporter ------------------------------------------------------------
    def _change_reporter(self, before: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Method to tell the window, in one call, every value that differs from what it
        was; nothing is told when nothing changed.

        ---- Inputs ----
        before : Dict[str, Any]
            The values before the user's change.

        ---- Globals read ----
        VALUE_NAMES.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_change (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        changes = {name: self._values[name]
                   for name in VALUE_NAMES
                   if self._values[name] != before[name]
                   }
        if changes:
            self._on_change(changes)

    # ---- _compare_handler ------------------------------------------------------------
    def _compare_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the button that keeps the decomposition in use to compare with,
        or, while one is kept, carries on with the one on the plot. The program says which one is kept (the value 'kept').

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value, changes the button and reports the change (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        """

        before = dict(self._values)
        self._values['compare'] = not self._values['compare']
        self._size_refresher()
        self._change_reporter(before)

    # ---- _edit_handler ---------------------------------------------------------------
    def _edit_handler(self, name: str) -> None:
        """
        ---- Summary ----
        Method to take a click on Edit ODs or Edit labels. The boxes keep nothing: the
        click is told as {name: True}, and the program opens the table.

        ---- Inputs ----
        name : str
            EDIT_ODS_CHANGE or EDIT_LABELS_CHANGE.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_change (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._is_enabled:
            self._on_change({name: True})

    # ---- _fit_handler ----------------------------------------------------------------
    def _fit_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the fit picked in the drop-down.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        """

        before = dict(self._values)
        index = self._fit_combo.current()
        # the list shows each fit by its name; the value kept is its file name
        self._values['fit_file'] = (self._fit_names[index]
                                    if 0 <= index < len(self._fit_names)
                                    else self._fit_combo.get()
                                    )
        self._fit_combo.selection_clear()
        self._size_refresher()
        self._change_reporter(before)

    # ---- _fit_saver ------------------------------------------------------------------
    def _fit_saver(self) -> None:
        """
        ---- Summary ----
        Method to take a click on Save fit, or Enter in the name box beside it. The
        boxes keep nothing: the click is told as {SAVE_FIT_CHANGE: the name typed},
        and the program saves the haems ticked under that name, or says why it cannot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        SAVE_FIT_CHANGE.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_change (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._is_enabled:
            self._on_change({SAVE_FIT_CHANGE: self._fit_name_entry.get().strip()})

    # ---- _form_handler ---------------------------------------------------------------
    def _form_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the way of showing the haems picked in the drop-down.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        """

        before = dict(self._values)
        self._values['haem_mode'] = self._form_keys[self._form_combo.current()]
        self._form_combo.selection_clear()
        self._size_refresher()
        self._change_reporter(before)

    # ---- _formula_toggler ------------------------------------------------------------
    def _formula_toggler(self) -> None:
        """
        ---- Summary ----
        Method to show the formula of the scatter picked under the Scatter drop-down,
        or hide it again.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Shows or hides the formula (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        """

        self._is_formula_open = not self._is_formula_open
        self._size_refresher()

    # ---- _haems_handler --------------------------------------------------------------
    def _haems_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the tick box of the haems.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        """

        before = dict(self._values)
        self._values['plot_haems'] = bool(self._haems.get())
        self._change_reporter(before)

    # ---- _height_handler -------------------------------------------------------------
    def _height_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the height typed in the box, when Enter is pressed or the box
        is left. A height that cannot be used turns the box red, with the reason
        beside it, and is not passed on.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        ERROR_BACKGROUND, ERROR_TEXT, NO_JOURNAL.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        height_checker
        """

        if self._values['journal'] == NO_JOURNAL:
            return
        height, note = height_checker(self._height_entry.get(), self._values['journal'])
        if height is None:
            self._height_entry.configure(bg=ERROR_BACKGROUND)
            self._note.configure(text=note, fg=ERROR_TEXT)
            return
        before = dict(self._values)
        self._values['height'] = height
        self._custom_size = (self._values['columns'], height)
        self._size_refresher()
        self._change_reporter(before)

    # ---- _journal_handler ------------------------------------------------------------
    def _journal_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the journal picked in the drop-down. "None" gives the standard
        size; a journal gives back the size last chosen for a journal, with the first
        width of the journal when it does not allow the one chosen.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        NO_JOURNAL.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the values and reports the changes (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        width_choices_lister
        """

        before = dict(self._values)
        journal = self._journals[self._journal_combo.current()]
        self._values['journal'] = journal
        if journal == NO_JOURNAL:
            columns, height = self._standard_size
        else:
            columns, height = self._custom_size
            allowed = [choice for choice, _ in width_choices_lister(journal)]
            if columns not in allowed:
                columns = allowed[0]
            self._custom_size = (columns, height)
        self._values['columns'], self._values['height'] = columns, height
        self._journal_combo.selection_clear()
        self._size_refresher()
        self._change_reporter(before)

    # ---- _label_mode_handler ---------------------------------------------------------
    def _label_mode_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take what the event labels show, picked in the drop-down.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        LABEL_FORM_TEXTS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        """

        before = dict(self._values)
        self._values['label_mode'] = list(LABEL_FORM_TEXTS)[
            self._label_mode_combo.current()
            ]
        self._label_mode_combo.selection_clear()
        self._change_reporter(before)

    # ---- _layout_handler -------------------------------------------------------------
    def _layout_handler(self, layout: str) -> None:
        """
        ---- Summary ----
        Method to take a click on the switch beside Keep new: the kept decomposition
        shown as a plot of its own beside the one in use, or dashed over it. A click on
        the layout already in use changes nothing.

        ---- Inputs ----
        layout : str
            A key of COMPARE_LAYOUT_TEXTS: 'side' or 'overlaid'.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value, presses the button in and reports the change (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        """

        if not self._is_enabled:
            return
        before = dict(self._values)
        self._values['compare_layout'] = layout
        self._size_refresher()
        self._change_reporter(before)

    # ---- _master_handler -------------------------------------------------------------
    def _master_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the button that exports the master page: a page of the journal
        with the figure of the file shown on it. The strip keeps nothing: the click is
        told as {MASTER_CHANGE: True}, and the program saves the page.

        ---- Inputs ----
        None.

        ---- Globals read ----
        MASTER_CHANGE.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_change (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._on_change({MASTER_CHANGE: True})

    # ---- _more_toggler ---------------------------------------------------------------
    def _more_toggler(self) -> None:
        """
        ---- Summary ----
        Method to take the "More options" box of the Δψ row: ticked, the share, the temperature
        and the limits are boxes to type in; unticked, they are one line of text.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        """

        self._is_more_open = bool(self._more.get())
        self._size_refresher()

    # ---- _order_handler --------------------------------------------------------------
    def _order_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the button that puts the panels of the plot back in the standard
        order. The strip keeps nothing: the click is told as {PANEL_ORDER_CHANGE: []},
        and the program draws the plots again.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PANEL_ORDER_CHANGE.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Reports the click (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._on_change({PANEL_ORDER_CHANGE: []})

    # ---- _paper_handler --------------------------------------------------------------
    def _paper_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the button that puts the numbers of the paper back in the Δψ
        row: the midpoints, the fall, the share and the limits. The temperature stays,
        as it is that of the runs.

        ---- Inputs ----
        None.

        ---- Globals read ----
        settings.DEFAULT_ANSWERS, PSI_FIELDS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the values and reports the changes (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        psi_values_builder
        """

        before = dict(self._values)
        paper = psi_values_builder(settings.DEFAULT_ANSWERS, True)
        self._values.update({name: paper[name]
                             for name in PSI_FIELDS
                             if name != 'temperature_c'
                             },
                            )
        self._size_refresher()
        self._change_reporter(before)

    # ---- _pca_handler ----------------------------------------------------------------
    def _pca_handler(self) -> None:
        """
        ---- Summary ----
        Method to take a click on Do PCA. The box keeps nothing: the click is told as
        {PCA_CHANGE: True}, and the program asks the questions of the analysis.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PCA_CHANGE.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the function given as on_change (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._is_enabled:
            self._on_change({PCA_CHANGE: True})

    # ---- _ocr_handler ----------------------------------------------------------------
    def _ocr_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the way of showing the OCR picked in the drop-down, or its per
        OD box clicked: together they make the way the OCR is shown.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        ocr_mode_builder
        """

        before = dict(self._values)
        index = self._ocr_combo.current()
        shown = (self._ocr_keys[index]
                 if index >= 0
                 else ocr_view_reader(self._values['ocr_mode'])[0]
                 )
        self._values['ocr_mode'] = ocr_mode_builder(shown,
                                                    self._has_od and
                                                    bool(self._ocr_od.get()),
                                                    )
        self._ocr_combo.selection_clear()
        self._size_refresher()
        self._change_reporter(before)

    # ---- _per_od_handler -------------------------------------------------------------
    def _per_od_handler(self, name: str) -> None:
        """
        ---- Summary ----
        Method to take the per OD tick box of the haems.

        ---- Inputs ----
        name : str
            'haem_per_od', the value of the box clicked.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        """

        before = dict(self._values)
        self._values[name] = bool(self._haem_od.get())
        self._change_reporter(before)

    # ---- _psi_handler ----------------------------------------------------------------
    def _psi_handler(self, name: str) -> None:
        """
        ---- Summary ----
        Method to take the number typed in one box of the Δψ row, when Enter is pressed
        or the box is left; a box left as it was shown passes nothing on. A number that
        cannot be used turns the box red, with the reason under the row, and the value
        in use stays.

        ---- Inputs ----
        name : str
            The value of the box, one of PSI_FIELDS.

        ---- Globals read ----
        ERROR_BACKGROUND.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        psi_number_checker
        typed_number_reader
        """

        box = self._psi_boxes[name]
        if str(box.cget('state')) == 'disabled':
            return
        text = box.get()
        if typed_number_reader(text) == self._values[name]:
            self._size_refresher()
            return
        value, note = psi_number_checker(name, text, self._values)
        if value is None:
            box.configure(bg=ERROR_BACKGROUND)
            self._psi_note.configure(text=note)
            self._psi_note.pack()
            return
        before = dict(self._values)
        self._values[name] = value
        self._size_refresher()
        self._change_reporter(before)

    # ---- _psi_tick_handler -----------------------------------------------------------
    def _psi_tick_handler(self) -> None:
        """
        ---- Summary ----
        Method to take the tick box of the Δψ box: ticked, Δψ is worked out and its
        numbers show under it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        """

        before = dict(self._values)
        self._values['delta_psi'] = bool(self._psi_on.get())
        self._size_refresher()
        self._change_reporter(before)

    # ---- _size_refresher -------------------------------------------------------------
    def _size_refresher(self) -> None:
        """
        ---- Summary ----
        Method to show the kept values in every part of the strip: the widths offered
        follow the journal, the width and the height are greyed for "None", the button
        that keeps a decomposition is greyed while no haems are shown, the button that
        goes back to the kept one and the line saying which one is kept show only
        while one is, the spectrometer shows only when
        there is a choice, the formula of the scatter only while its button is pressed
        in, the fits by their names, the per OD box of the haems only when OD values were
        entered (greyed for % oxidised, which has no per OD), the ways of showing the
        OCR that can be used now, the Δψ row only
        while Δψ is worked out (its filled-in midpoints following the typed ones and
        the fall), and the whole strip is greyed while the program is not listening.

        ---- Inputs ----
        None.

        ---- Globals read ----
        HAEM_FORM_TEXTS, OCR_FORM_TEXTS, LABEL_FORM_TEXTS, KEEP_TEXT, KEPT_PREFIXES,
        NO_JOURNAL, NOTE_TEXT, BACKGROUND_FORMULAS.
        (BACK_TEXT and STOP_TEXT are set on their buttons once, when they are built.)

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        fit_title_maker
        formula_note_writer
        formula_picture_maker
        haem_form_choices_lister
        height_checker
        ocr_form_choices_lister
        psi_seconds_filler
        psi_summary_writer
        width_choices_lister
        """

        values = self._values
        is_standard = values['journal'] == NO_JOURNAL
        self._haems.set(values['plot_haems'])
        is_own = values['fit_file'] == OWN_HAEMS_NAME
        titles = [fit_title_maker(name, self._fit_titles) for name in self._fit_names]
        self._fit_combo.configure(values=titles + ([OWN_HAEMS_NAME] if is_own else []))
        self._fit_combo.set(fit_title_maker(values['fit_file'], self._fit_titles))
        if values['haem_background'] in self._backgrounds:
            self._background_combo.current(
                self._backgrounds.index(values['haem_background']),
                )
        # the formula of the scatter in use, while its button is pressed in
        self._formula_button.configure(relief='sunken'
                                       if self._is_formula_open
                                       else 'raised',
                                       )
        if self._is_formula_open and values['haem_background'] in BACKGROUND_FORMULAS:
            name = values['haem_background']
            if name not in self._formula_pictures:
                self._formula_pictures[name] = self._tk.PhotoImage(
                    master=self.frame,
                    data=base64.b64encode(
                        formula_picture_maker(name),
                        ),
                    )
            self._formula_label.configure(image=self._formula_pictures[name])
            self._formula_note.configure(text=formula_note_writer(name))
            self._formula_line.pack(anchor='w',
                                    pady=(0, 2),
                                    after=self._scatter_line,
                                    )
        else:
            self._formula_line.pack_forget()
        for name, variable in self._tick_vars.items():
            variable.set(name in values['haem_files'])
        self._journal_combo.current(self._journals.index(values['journal']))
        choices = width_choices_lister(values['journal'])
        self._width_columns = [columns for columns, _ in choices]
        self._width_combo.configure(state='readonly',
                                    values=[text for _, text in choices],
                                    )
        if values['columns'] in self._width_columns:
            self._width_combo.current(self._width_columns.index(values['columns']))
        else:
            self._width_combo.set(f"{values['columns']:g} columns")
        text = f"{values['height']:g}"
        self._height_entry.configure(state='normal', bg='white')
        self._height_entry.delete(0, 'end')
        self._height_entry.insert(0, text)
        self._note.configure(text=height_checker(text, values['journal'])[1],
                             fg=NOTE_TEXT,
                             )
        choice_state = 'readonly' if self._is_enabled else 'disabled'
        button_state = 'normal' if self._is_enabled else 'disabled'
        self._haems_box.configure(state=button_state)
        self._master_button.configure(state=button_state)
        self._order_button.configure(state=button_state)
        self._fit_combo.configure(state=choice_state)
        self._background_combo.configure(state=choice_state)
        self._build_button.configure(state=button_state)
        self._pca_button.configure(state=button_state)
        self._formula_button.configure(state=button_state)
        for box in self._tick_boxes.values():
            box.configure(state=button_state)
        self._fit_name_entry.configure(state=button_state)
        self._save_button.configure(state=button_state)
        # Keep to compare is greyed while one is kept: Keep old and Keep new, on the
        # line under it, then choose between the two.
        can_compare = self._is_enabled and values['plot_haems']
        self._compare_button.configure(
            text=KEEP_TEXT,
            state='normal' if can_compare and not values['compare'] else 'disabled',
            )
        if values['compare']:
            for button in (self._back_button, self._new_button):
                button.configure(state='normal' if can_compare else 'disabled')
            # the switch shows the layout in use pressed in
            for layout, button in self._layout_buttons.items():
                button.configure(relief=('sunken'
                                         if values['compare_layout'] == layout
                                         else 'raised'
                                         ),
                                 state='normal' if can_compare else 'disabled',
                                 )
            self._choose_line.pack(anchor='w', pady=(0, 2), after=self._keep_line)
        else:
            self._choose_line.pack_forget()
        if values['kept']:
            self._kept_label.configure(text=KEPT_PREFIXES[values['compare_layout']] +
                                       values['kept'],
                                       )
            self._kept_label.pack(anchor='w', pady=(0, 2), fill='x')
        else:
            self._kept_label.pack_forget()
        # ---- the tabs of the Time regions box: the one whose edges are on the plot
        for tab, button in self._tab_buttons.items():
            is_pressed = values['time_tab'] == tab
            button.configure(relief='sunken' if is_pressed else 'raised',
                             state=button_state,
                             )
        if values['time_tab']:
            self._tab_note.pack_forget()
        else:
            self._tab_note.pack(anchor='w')
        haem_state = choice_state if values['plot_haems'] else 'disabled'
        forms = haem_form_choices_lister(self._has_percent)
        self._form_keys = [key for key, _ in forms]
        self._form_combo.configure(state='readonly', values=[text for _, text in forms])
        if values['haem_mode'] in self._form_keys:
            self._form_combo.current(self._form_keys.index(values['haem_mode']))
        else:
            self._form_combo.set(HAEM_FORM_TEXTS.get(values['haem_mode'], ''))
        self._form_combo.configure(state=haem_state)
        self._spectra_combo.configure(state='readonly', values=self._spectra_names)
        self._spectra_combo.set(values['spectra'])
        self._spectra_combo.configure(state=haem_state)
        self._haem_od.set(values['haem_per_od'])
        # The OCR per OD is µM min⁻¹ with its per OD box ticked. A way of showing the
        # OCR that is not offered now (% of baseline before the windows are set up) is
        # still shown as the choice in use.
        forms = [(key, text)
                 for key, text in ocr_form_choices_lister(False, self._has_baseline)
                 ]
        self._ocr_keys = [key for key, _ in forms]
        shown, is_per_od = ocr_view_reader(values['ocr_mode'])
        self._ocr_combo.configure(state='readonly', values=[text for _, text in forms])
        if shown in self._ocr_keys:
            self._ocr_combo.current(self._ocr_keys.index(shown))
        else:
            self._ocr_combo.set(OCR_FORM_TEXTS.get(shown, ''))
        self._ocr_combo.configure(state=choice_state)
        self._ocr_od.set(is_per_od)
        self._ocr_od_box.configure(state='normal'
                                   if self._is_enabled and shown == 'raw'
                                   else 'disabled',
                                   )
        angle_text = f"{values['event_label_angle']:g}"
        self._angle_entry.configure(state='normal', bg='white')
        self._angle_entry.delete(0, 'end')
        self._angle_entry.insert(0, angle_text)
        self._angle_entry.configure(state=button_state)
        self._angle_note.pack_forget()
        self._edit_ods_button.configure(state=button_state)
        self._edit_labels_button.configure(state=button_state)
        self._label_mode_combo.configure(state='readonly')
        self._label_mode_combo.current(
            list(LABEL_FORM_TEXTS).index(values['label_mode']),
            )
        self._label_mode_combo.configure(state=choice_state)
        can_scale = (self._is_enabled and
                     values['plot_haems'] and
                     values['haem_mode'] != 'percent'
                     )
        self._haem_od_box.configure(state='normal' if can_scale else 'disabled')
        # The spectrometer only when there is a choice; the per OD boxes only once
        # every OD value is in.
        if len(self._spectra_names) > 1:
            self._spectra_line.pack(anchor='w', pady=(0, 2), before=self._scatter_line)
        else:
            self._spectra_line.pack_forget()
        for box in (self._ocr_od_box, self._haem_od_box):
            if self._has_od:
                box.pack(side='left')
            else:
                box.pack_forget()
        # The Δψ row: shown only while Δψ is worked out, its boxes holding the values
        # in use (a number typed and refused is taken away with its reason).
        seconds = psi_seconds_filler(values['psi_bH_mV'],
                                     values['psi_bL_mV'],
                                     values['psi_fall_mV'],
                                     )
        for second, filled in zip(self._psi_seconds.values(), seconds):
            second.configure(state='normal')
            second.delete(0, 'end')
            second.insert(0, f'{filled:g}')
            second.configure(state='readonly')
        for name, box in self._psi_boxes.items():
            box.configure(state='normal', bg='white')
            box.delete(0, 'end')
            box.insert(0, f'{values[name]:g}')
            box.configure(state=button_state)
        self._paper_button.configure(state=button_state)
        self._more.set(self._is_more_open)
        self._psi_summary.configure(text=psi_summary_writer(values))
        self._psi_note.pack_forget()
        self._psi_summary.pack_forget()
        self._psi_more.pack_forget()
        (self._psi_more if self._is_more_open else self._psi_summary).pack(anchor='w')
        # The Δψ box: its tick only while Δψ can be worked out, its numbers while it is
        # ticked.
        self._psi_on.set(values['delta_psi'])
        can_psi = self._is_enabled and (self._has_psi or values['delta_psi'])
        self._psi_tick.configure(state='normal' if can_psi else 'disabled')
        if values['delta_psi']:
            self._psi_row.pack(anchor='w')
        else:
            self._psi_row.pack_forget()
        self._journal_combo.configure(state=choice_state)
        if is_standard or not self._is_enabled:
            self._width_combo.configure(state='disabled')
            self._height_entry.configure(state='disabled')

    # ---- _spectra_handler ------------------------------------------------------------
    def _spectra_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the spectrometer picked in the drop-down.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        """

        before = dict(self._values)
        self._values['spectra'] = self._spectra_combo.get()
        self._spectra_combo.selection_clear()
        self._change_reporter(before)

    # ---- _tick_handler ---------------------------------------------------------------
    def _tick_handler(self, name: str) -> None:
        """
        ---- Summary ----
        Method to take a tick box of Build a fit: the haems ticked become the fit, as
        "Your own haems". Ticking a haem with the same name as one already ticked
        unticks that one, and the last haem ticked cannot be unticked; a note beside
        the height says so.

        ---- Inputs ----
        name : str
            File name of the library haem whose box was clicked.

        ---- Globals read ----
        OWN_HAEMS_NAME, NOTE_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the values, changes the widgets and reports the change (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        haem_ticks_resolver
        """

        before = dict(self._values)
        ticked, note = haem_ticks_resolver(self._values['haem_files'],
                                           name,
                                           bool(self._tick_vars[name].get()),
                                           self._haems_by_file,
                                           )
        if ticked != list(self._values['haem_files']):
            self._values['haem_files'] = ticked
            self._values['fit_file'] = OWN_HAEMS_NAME
        self._size_refresher()
        if note:
            self._note.configure(text=note, fg=NOTE_TEXT)
        self._change_reporter(before)

    # ---- _time_tab_handler -----------------------------------------------------------
    def _time_tab_handler(self, tab: str) -> None:
        """
        ---- Summary ----
        Method to take a tab of the Time regions box pressed: its edges go on the plot.
        The tab already pressed passes nothing on.

        ---- Inputs ----
        tab : str
            A key of TIME_TAB_TEXTS.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        _size_refresher
        """

        if not self._is_enabled or self._values['time_tab'] == tab:
            return
        before = dict(self._values)
        self._values['time_tab'] = tab
        self._size_refresher()
        self._change_reporter(before)

    # ---- _width_handler --------------------------------------------------------------
    def _width_handler(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to take the width picked in the drop-down.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the value and reports the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _change_reporter
        """

        before = dict(self._values)
        columns = self._width_columns[self._width_combo.current()]
        self._values['columns'] = columns
        self._custom_size = (columns, self._values['height'])
        self._width_combo.selection_clear()
        self._change_reporter(before)

    # ---- STRIP FUNCTIONS -------------------------------------------------------------

    # ---- choices_setter --------------------------------------------------------------
    def choices_setter(self,
                       spectra: List[str],
                       has_percent: bool,
                       has_od: bool,
                       has_baseline: bool = False,
                       has_psi: bool = False,
                       ) -> None:
        """
        ---- Summary ----
        Method to say what the boxes offer: the spectrometers of the "Spectra"
        drop-down (shown only with more than one), whether % oxidised is in the "Haems
        as" drop-down, whether the per OD boxes of the OCR and the haems are shown,
        whether % of baseline is in the "OCR as" drop-down, and whether the tick of the
        Δψ box can be clicked. The values stay.

        ---- Inputs ----
        spectra : List[str]
            The spectrometers every file has, as they are to be listed.
        has_percent : bool
            True when at least one file has both regions, so % oxidised is offered.
        has_od : bool
            True when OD values were entered, so per OD is offered.
        has_baseline : bool
            True when the averaging windows are set up, so the OCR is offered as % of
            baseline.
        has_psi : bool
            True when Δψ can be worked out (a file with both regions and a fit with bH
            and bL), so its tick can be clicked.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        """

        self._spectra_names = list(spectra)
        self._has_percent = bool(has_percent)
        self._has_od = bool(has_od)
        self._has_baseline = bool(has_baseline)
        self._has_psi = bool(has_psi)
        self._size_refresher()

    # ---- fits_setter -----------------------------------------------------------------
    def fits_setter(self, fits: Dict[str, str]) -> None:
        """
        ---- Summary ----
        Method to give the drop-down of the fits its list. The fit shown stays.

        ---- Inputs ----
        fits : Dict[str, str]
            {file name: name shown} of the fits, in the order they are to be listed
            (spectral_decomposer.fit_titles_lister).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the drop-down (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        """

        self._fit_names = list(fits)
        self._fit_titles = dict(fits)
        self._size_refresher()

    # ---- library_setter --------------------------------------------------------------
    def library_setter(self, haems: List[Dict[str, str]]) -> None:
        """
        ---- Summary ----
        Method to build the tick boxes of Build a fit: one line for each type of haem
        (a, b, c, then any other), with a box for each library file, named by its file
        without .csv.

        ---- Inputs ----
        haems : List[Dict[str, str]]
            The library, as spectral_decomposer.library_haems_lister gives it: [{'file',
            'haem', 'type'}], in the order to show.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Rebuilds the panel (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        _tick_handler
        """

        tk = self._tk
        for child in self._library.winfo_children():
            child.destroy()
        self._haems_by_file = {item['file']: item['haem'] for item in haems}
        self._tick_vars, self._tick_boxes = {}, {}
        lines: Dict[str, Any] = {}
        for item in haems:
            if item['type'] not in lines:
                lines[item['type']] = tk.Frame(self._library, bg=self._background)
                lines[item['type']].pack(anchor='w')
                tk.Label(lines[item['type']],
                         text=item['type'],
                         width=6,
                         anchor='w',
                         bg=self._background,
                         ).pack(side='left', padx=(4, 4))
            name = item['file']
            self._tick_vars[name] = tk.BooleanVar(master=self._library, value=False)
            box = tk.Checkbutton(lines[item['type']],
                                 text=name[:-4] if name.lower().endswith('.csv') else name,
                                 variable=self._tick_vars[name],
                                 command=lambda chosen=name: self._tick_handler(chosen),
                                 bg=self._background,
                                 activebackground=self._background,
                                 highlightthickness=0,
                                 )
            box.pack(side='left', padx=(0, 6))
            self._tick_boxes[name] = box
        self._size_refresher()

    # ---- state_setter ----------------------------------------------------------------
    def state_setter(self, is_enabled: bool) -> None:
        """
        ---- Summary ----
        Method to let the user change the strip, or grey it out while what it shows
        is not being used. The values stay on show either way.

        ---- Inputs ----
        is_enabled : bool
            True to let the user change the values, False to grey the strip out.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        """

        self._is_enabled = bool(is_enabled)
        self._size_refresher()

    # ---- values_reader ---------------------------------------------------------------
    def values_reader(self) -> Dict[str, Any]:
        """
        ---- Summary ----
        Method to give the values the strip shows now. It can be called from any
        thread.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Dict[str, Any]
            A copy of the strip values (DATA_FORMAT.md).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return dict(self._values, haem_files=list(self._values['haem_files']))

    # ---- values_setter ---------------------------------------------------------------
    def values_setter(self, values: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Method to show the values the program gives. Nothing is reported back, as the
        program made the change itself.

        ---- Inputs ----
        values : Dict[str, Any]
            Some or all of the strip values (DATA_FORMAT.md), already checked by
            strip_values_checker.

        ---- Globals read ----
        NO_JOURNAL.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the values and changes the widgets (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_refresher
        """

        self._values.update(values)
        self._values['haem_files'] = list(self._values['haem_files'])
        if self._values['journal'] == NO_JOURNAL:
            self._standard_size = (self._values['columns'], self._values['height'])
        else:
            self._custom_size = (self._values['columns'], self._values['height'])
        self._size_refresher()


# ---- HELPERS -------------------------------------------------------------------------


# ---- _page_journal_finder ------------------------------------------------------------
def _page_journal_finder(journal: str) -> str:
    """
    ---- Summary ----
    Helper function to give the journal whose page a strip journal is drawn on: the
    journal itself, or the standard journal for "None".

    ---- Inputs ----
    journal : str
        NO_JOURNAL or a key of settings.JOURNAL_SPECS.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS, NO_JOURNAL.

    ---- Outputs ----
    str
        A key of settings.JOURNAL_SPECS. Raises ValueError for an unknown journal.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if journal == NO_JOURNAL:
        return settings.DEFAULT_ANSWERS['journal']
    if journal not in settings.JOURNAL_SPECS:
        raise ValueError(f"The strip has no journal called '{journal}'.")
    return journal


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- form_answers_builder ------------------------------------------------------------
def form_answers_builder(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to turn the spectrometer, the ways of showing the haems and the OCR,
    what the event labels show and their angle into the answers of the run.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md), as checked by
        strip_values_checker.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        The answers to update: decomposition_dataset for the spectrometer, and
        haem_mode, haem_per_od, ocr_mode, label_mode and event_label_angle as given.
        Empty when the values hold none of them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    answers: Dict[str, Any] = {}
    if 'spectra' in values:
        answers['decomposition_dataset'] = values['spectra']
    for name in ('haem_mode',
                 'haem_per_od',
                 'ocr_mode',
                 'label_mode',
                 'event_label_angle',
                 ):
        if name in values:
            answers[name] = values[name]
    return answers


# ---- formula_note_writer -------------------------------------------------------------
def formula_note_writer(background: str) -> str:
    """
    ---- Summary ----
    Main function to say under a scatter's formula what its letters are.

    ---- Inputs ----
    background : str
        A key of BACKGROUND_FORMULAS.

    ---- Globals read ----
    FORMULA_NOTE.

    ---- Outputs ----
    str
        One line: what B, w and the b are, and w_mid for Rowan scatter.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    middle = ('; w_mid: the wavelength halfway along those used'
              if background == 'rowan_scatter'
              else ''
              )
    return f'B: the scatter (OD); {FORMULA_NOTE}{middle}.'


# ---- formula_picture_maker -----------------------------------------------------------
def formula_picture_maker(background: str, colour: str = 'black') -> bytes:
    """
    ---- Summary ----
    Main function to draw a scatter's formula as a textbook writes it (fractions with
    a bar, powers raised, the b with their numbers lowered), as a PNG with a clear
    background for the Haem decomposition box.

    ---- Inputs ----
    background : str
        A key of BACKGROUND_FORMULAS.
    colour : str
        Colour of the letters.

    ---- Globals read ----
    BACKGROUND_FORMULAS, FORMULA_DPI, FORMULA_FONT_PT.

    ---- Outputs ----
    bytes
        The PNG, cut to the formula.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    fig = Figure(figsize=(4.0, 0.6), dpi=FORMULA_DPI)
    fig.text(0.0,
             0.5,
             BACKGROUND_FORMULAS[background],
             fontsize=FORMULA_FONT_PT,
             color=colour,
             va='center',
             )
    buffer = io.BytesIO()
    fig.savefig(buffer,
                format='png',
                dpi=FORMULA_DPI,
                transparent=True,
                bbox_inches='tight',
                pad_inches=0.02,
                )
    return buffer.getvalue()


# ---- haem_form_choices_lister --------------------------------------------------------
def haem_form_choices_lister(has_percent: bool) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Main function to list the ways of showing the haems the "Haems as" drop-down
    offers, each with its words.

    ---- Inputs ----
    has_percent : bool
        True when at least one file has both regions, so % oxidised is offered.

    ---- Globals read ----
    HAEM_FORM_TEXTS.

    ---- Outputs ----
    List[Tuple[str, str]]
        [(haem_mode, words)] in the order of the drop-down: delta D, % oxidised when
        offered, absorbance.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [(key, text)
            for key, text in HAEM_FORM_TEXTS.items()
            if key != 'percent' or has_percent
            ]


# ---- haem_ticks_resolver -------------------------------------------------------------
def haem_ticks_resolver(ticked: Sequence[str],
                        clicked: str,
                        is_on: bool,
                        haems_by_file: Dict[str, str],
                        ) -> Tuple[List[str], str]:
    """
    ---- Summary ----
    Main function to work out the library haems ticked after a click on one tick box of
    Build a fit. Two haems of the same name could not be told apart in the figures, so
    ticking one unticks the other; and a fit needs a haem, so the last cannot be
    unticked.

    ---- Inputs ----
    ticked : Sequence[str]
        File names ticked before the click.
    clicked : str
        File name of the box clicked.
    is_on : bool
        True when the box is ticked after the click.
    haems_by_file : Dict[str, str]
        {file name: plain haem name} of the library.

    ---- Globals read ----
    LAST_TICK_NOTE (module constant).

    ---- Outputs ----
    Tuple[List[str], str]
        (the file names ticked, in the order ticked; a note for the user, '' when
        there is nothing to say).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    ticked = list(ticked)
    if is_on:
        name = haems_by_file.get(clicked)
        same = [file for file in ticked
                if file != clicked and name is not None and haems_by_file.get(file) == name
                ]
        kept = [file for file in ticked if file not in same and file != clicked]
        note = (f'{clicked} takes the place of {same[0]}: both are {name}.'
                if same
                else ''
                )
        return kept + [clicked], note
    if clicked not in ticked:
        return ticked, ''
    if len(ticked) == 1:
        return ticked, LAST_TICK_NOTE
    return [file for file in ticked if file != clicked], ''


# ---- height_checker ------------------------------------------------------------------
def height_checker(text: str, journal: str) -> Tuple[Optional[float], str]:
    """
    ---- Summary ----
    Main function to check a height typed as a share of a page, and to say what it is
    in millimetres on the page of the journal.

    ---- Inputs ----
    text : str
        What was typed, e.g. '0.5' or '0,5'.
    journal : str
        NO_JOURNAL or a key of settings.JOURNAL_SPECS.

    ---- Globals read ----
    settings.JOURNAL_SPECS, HEIGHT_HELP.

    ---- Outputs ----
    Tuple[Optional[float], str]
        (height, 'of a page (85 mm)') for a height above 0 and up to 1, or (None, why
        it cannot be used).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    height in mm = height * page height of the journal in mm.

    ---- Helpers ----
    _page_journal_finder
    typed_number_reader
    """

    page_mm = settings.JOURNAL_SPECS[_page_journal_finder(journal)]['page_height_mm']
    height = typed_number_reader(text)
    if height is None or not 0 < height <= 1:
        return None, f'Type {HEIGHT_HELP}.'
    return height, f'of a page ({round(height * page_mm, 1):g} mm)'


# ---- kept_decomposition_builder ------------------------------------------------------
def kept_decomposition_builder(answers: dict,
                               fit: dict,
                               regions: Dict[str, Dict[str, float]],
                               ) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to keep the decomposition in use, to compare the next ones with: the
    fit, the answers it was worked out with (the fit, the background, the spectrometer
    and the numbers of delta psi), the oxidised and reduced regions of every file, and
    its name in words.

    ---- Inputs ----
    answers : dict
        The answers in use (fit_file, haem_files, haem_background,
        decomposition_dataset, delta_psi and the numbers of delta psi).
    fit : dict
        The fit in use (spectral_decomposer.fit_importer); it is kept as it is, as a
        fit is never changed once read.
    regions : Dict[str, Dict[str, float]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
        times on the original recording (min); may be empty. A copy is kept, so the
        regions changed later leave it as it was.

    ---- Globals read ----
    BACKGROUND_SHORT_NAMES, PSI_KEPT_ANSWERS.

    ---- Outputs ----
    Dict[str, Any]
        The kept decomposition (DATA_FORMAT.md, kept decomposition).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    fit_describer
    """

    kept_answers = {'fit_file': answers['fit_file'],
                    'haem_files': list(answers.get('haem_files', [])),
                    'haem_background': answers['haem_background'],
                    'decomposition_dataset': answers['decomposition_dataset'],
                    **{name: answers[name] for name in PSI_KEPT_ANSWERS},
                    }
    background = BACKGROUND_SHORT_NAMES.get(answers['haem_background'],
                                            answers['haem_background'],
                                            )
    text = (f"{fit_describer(answers['fit_file'], kept_answers['haem_files'])} with "
            f'the {background} background'
            )
    if answers.get('delta_psi'):
        text += ', its regions and Δψ numbers'
    elif regions:
        text += ' and its regions'
    return {'fit': fit,
            'answers': kept_answers,
            'regions': copy.deepcopy(regions),
            'text': text,
            }


# ---- ocr_form_choices_lister ---------------------------------------------------------
def ocr_form_choices_lister(has_od: bool, has_baseline: bool) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Main function to list the ways of showing the OCR the "OCR as" drop-down offers,
    each with its words.

    ---- Inputs ----
    has_od : bool
        True when OD values were entered, so the OCR per OD is offered.
    has_baseline : bool
        True when the averaging windows are set up, so % of baseline is offered.

    ---- Globals read ----
    OCR_FORM_TEXTS.

    ---- Outputs ----
    List[Tuple[str, str]]
        [(ocr_mode, words)] in the order of the drop-down: the OCR, per OD when
        offered, % of the range, % of baseline when offered.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [(key, text)
            for key, text in OCR_FORM_TEXTS.items()
            if (key != 'od' or has_od) and (key != 'baseline' or has_baseline)
            ]


# ---- ocr_mode_builder ----------------------------------------------------------------
def ocr_mode_builder(shown: str, is_per_od: bool) -> str:
    """
    ---- Summary ----
    Main function to give the way the OCR is shown from the "OCR as" drop-down of the
    View box and its per OD box: µM min⁻¹ with per OD ticked is the OCR per OD; the %
    views have no per OD, so the box is left out for them.

    ---- Inputs ----
    shown : str
        The choice of the drop-down: 'raw', 'percent' or 'baseline'.
    is_per_od : bool
        True when the per OD box is ticked (and can be).

    ---- Globals read ----
    OCR_FORM_TEXTS.

    ---- Outputs ----
    str
        The ocr_mode of the answers: 'raw', 'od', 'percent' or 'baseline'. Raises
        ValueError for a choice the drop-down does not have.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if shown not in OCR_FORM_TEXTS or shown == 'od':
        raise ValueError(f"'OCR as' has no choice called '{shown}'.")
    return 'od' if shown == 'raw' and is_per_od else shown


# ---- ocr_view_reader -----------------------------------------------------------------
def ocr_view_reader(ocr_mode: str) -> Tuple[str, bool]:
    """
    ---- Summary ----
    Main function to give what the View box shows for a way of showing the OCR: the
    choice of the "OCR as" drop-down and whether its per OD box is ticked. The
    opposite of ocr_mode_builder.

    ---- Inputs ----
    ocr_mode : str
        'raw', 'od', 'percent' or 'baseline'.

    ---- Globals read ----
    OCR_FORM_TEXTS.

    ---- Outputs ----
    Tuple[str, bool]
        (choice of the drop-down, True when per OD is ticked). Raises ValueError for
        an unknown way.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if ocr_mode not in OCR_FORM_TEXTS:
        raise ValueError(f"The OCR cannot be shown as '{ocr_mode}'.")
    return ('raw', True) if ocr_mode == 'od' else (ocr_mode, False)


# ---- minutes_checker -----------------------------------------------------------------
def minutes_checker(text: str) -> Tuple[Optional[float], str]:
    """
    ---- Summary ----
    Main function to check a number of minutes typed in a box of the edges row.

    ---- Inputs ----
    text : str
        What was typed, e.g. '4.5' or '4,5'.

    ---- Globals read ----
    MINUTES_HELP.

    ---- Outputs ----
    Tuple[Optional[float], str]
        (minutes, '') for a number of 0 or more, or (None, what to type instead).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    typed_number_reader
    """

    minutes = typed_number_reader(text)
    if minutes is None or minutes < 0:
        return None, MINUTES_HELP
    return minutes + 0.0, ''


# ---- psi_answers_builder -------------------------------------------------------------
def psi_answers_builder(changes: Dict[str, Any], answers: dict) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to turn the numbers changed in the Δψ row into the answers of the
    run: the four midpoint potentials from the two typed and the fall, and the share,
    the temperature and the limits as given.

    ---- Inputs ----
    changes : Dict[str, Any]
        {name: new value} of the strip values that changed (DATA_FORMAT.md).
    answers : dict
        The answers in use; the midpoints not changed are read from them.

    ---- Globals read ----
    PSI_MIDPOINT_FIELDS, PSI_MORE_ANSWERS.

    ---- Outputs ----
    Dict[str, float]
        The answers to update: all four midpoints (mV) when a midpoint or the fall
        changed, and psi_share, temperature_c (°C), psi_reduced_lowest_percent and
        psi_reduced_highest_percent when they did. Empty when no number of the row
        changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    psi_seconds_filler.

    ---- Helpers ----
    psi_seconds_filler
    psi_values_builder
    """

    result: Dict[str, float] = {}
    if any(name in changes for name in PSI_MIDPOINT_FIELDS):
        current = psi_values_builder(answers, True)
        bH, bL, fall = (float(changes.get(name, current[name]))
                        for name in PSI_MIDPOINT_FIELDS
                        )
        second_bH, second_bL = psi_seconds_filler(bH, bL, fall)
        result.update({'psi_bH_first_mV': bH,
                       'psi_bL_first_mV': bL,
                       'psi_bH_second_mV': second_bH,
                       'psi_bL_second_mV': second_bL,
                       },
                      )
    for name, answer in PSI_MORE_ANSWERS.items():
        if name in changes:
            result[answer] = float(changes[name])
    return result


# ---- psi_change_describer ------------------------------------------------------------
def psi_change_describer(changes: Dict[str, Any], answers: dict) -> List[str]:
    """
    ---- Summary ----
    Main function to say in plain sentences what the numbers of Δψ are after a change
    in the Δψ row: what was typed and what was filled in from it.

    ---- Inputs ----
    changes : Dict[str, Any]
        {name: new value} of the strip values that changed (DATA_FORMAT.md).
    answers : dict
        The answers in use, already holding the change (psi_answers_builder).

    ---- Globals read ----
    PSI_MIDPOINT_FIELDS.

    ---- Outputs ----
    List[str]
        One sentence for the midpoints and the fall, one for the share, one for the
        temperature and one for the limits, each only when it changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    psi_values_builder
    """

    lines = []
    values = psi_values_builder(answers, True)
    if any(name in changes for name in PSI_MIDPOINT_FIELDS):
        lines.append(f"Δψ is now worked out with bH at {values['psi_bH_mV']:g} mV "
                     f"({answers['psi_bH_second_mV']:g} mV with bL reduced) and bL at "
                     f"{values['psi_bL_mV']:g} mV ({answers['psi_bL_second_mV']:g} mV "
                     f"with bH reduced): a shift of {values['psi_fall_mV']:g} mV.",
                     )
    if 'psi_share' in changes:
        lines.append('The share of the membrane potential between bH and bL is now '
                     f"{values['psi_share']:g}.",
                     )
    if 'temperature_c' in changes:
        lines.append(f"The temperature of the runs is now {values['temperature_c']:g} "
                     '°C.',
                     )
    if 'psi_lowest_percent' in changes or 'psi_highest_percent' in changes:
        lines.append('Δψ is now given where bH and bL are between '
                     f"{values['psi_lowest_percent']:g} and "
                     f"{values['psi_highest_percent']:g} % reduced.",
                     )
    return lines


# ---- psi_number_checker --------------------------------------------------------------
def psi_number_checker(name: str,
                       text: str,
                       values: Dict[str, Any],
                       ) -> Tuple[Optional[float], str]:
    """
    ---- Summary ----
    Main function to check a number typed in one box of the Δψ row.

    ---- Inputs ----
    name : str
        The value of the box, one of PSI_FIELDS.
    text : str
        What was typed, e.g. '40', '-20' or '0,5'.
    values : Dict[str, Any]
        The strip values in use; a limit is checked against the other limit.

    ---- Globals read ----
    TEMPERATURE_LIMITS_C.

    ---- Outputs ----
    Tuple[Optional[float], str]
        (number, '') for a number that can be used, or (None, what to type instead).
        A midpoint or the fall is any number (mV); the share is above 0; the
        temperature is one the temperature question takes; the lowest limit is above
        0 and below the highest, the highest above the lowest and below 100.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    typed_number_reader
    """

    number = typed_number_reader(text)
    if name == 'psi_share':
        if number is None or number <= 0:
            return None, 'Type a share above 0, such as 0.5 for half.'
    elif name == 'temperature_c':
        coldest, hottest = TEMPERATURE_LIMITS_C
        if number is None or not coldest <= number <= hottest:
            return None, (f'Type a temperature from {coldest:g} to {hottest:g} °C, '
                          'such as 37.'
                          )
    elif name == 'psi_lowest_percent':
        highest = values['psi_highest_percent']
        if number is None or not 0 < number < highest:
            return None, (f'Type a lowest % reduced above 0 and below {highest:g}, '
                          'such as 10.'
                          )
    elif name == 'psi_highest_percent':
        lowest = values['psi_lowest_percent']
        if number is None or not lowest < number < 100:
            return None, (f'Type a highest % reduced above {lowest:g} and below 100, '
                          'such as 90.'
                          )
    elif number is None:
        return None, 'Type a number of mV, such as 40 or -20.'
    return number + 0.0, ''


# ---- psi_seconds_filler --------------------------------------------------------------
def psi_seconds_filler(bH_mV: float,
                       bL_mV: float,
                       fall_mV: float,
                       ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to fill in the midpoint potential of each b haem with the other
    haem reduced, from its midpoint with the other oxidised and the fall.

    ---- Inputs ----
    bH_mV : float
        Midpoint potential of bH with bL oxidised (mV).
    bL_mV : float
        Midpoint potential of bL with bH oxidised (mV).
    fall_mV : float
        How far each midpoint falls when the other haem is reduced (mV).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (midpoint of bH with bL reduced, midpoint of bL with bH reduced), in mV.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    second = first - fall, for each haem: 40 and -20 with a fall of 70 give -30 and
    -90. The fall is the same for both, as the maths of delta psi needs.

    ---- Helpers ----
    None.
    """

    return float(bH_mV) - float(fall_mV), float(bL_mV) - float(fall_mV)


# ---- psi_summary_writer --------------------------------------------------------------
def psi_summary_writer(values: Dict[str, Any]) -> str:
    """
    ---- Summary ----
    Main function to write the share, the temperature and the limits of Δψ as the one
    line of text shown in the Δψ row while "More options" is not ticked.

    ---- Inputs ----
    values : Dict[str, Any]
        The strip values (DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        'share 0.5 · 37 °C · given between 10 and 90 % reduced'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return (f"share {values['psi_share']:g} · {values['temperature_c']:g} °C · given "
            f"between {values['psi_lowest_percent']:g} and "
            f"{values['psi_highest_percent']:g} % reduced"
            )


# ---- psi_values_builder --------------------------------------------------------------
def psi_values_builder(answers: dict, is_on: bool) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to give the strip values of the Δψ row that show the answers of the
    run.

    ---- Inputs ----
    answers : dict
        The answers (the four midpoints, psi_share, temperature_c and the two limits).
    is_on : bool
        True when Δψ is worked out, which shows the row.

    ---- Globals read ----
    PSI_MORE_ANSWERS.

    ---- Outputs ----
    Dict[str, Any]
        {'delta_psi', 'psi_bH_mV', 'psi_bL_mV', 'psi_fall_mV', 'psi_share',
        'temperature_c', 'psi_lowest_percent', 'psi_highest_percent'}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    fall = midpoint of bH with bL oxidised - midpoint of bH with bL reduced, rounded
    to a millionth of a mV: 40 - (-30) = 70 mV.

    ---- Helpers ----
    None.
    """

    values: Dict[str, Any] = {'delta_psi': bool(is_on),
                              'psi_bH_mV': float(answers['psi_bH_first_mV']),
                              'psi_bL_mV': float(answers['psi_bL_first_mV']),
                              'psi_fall_mV': round(float(answers['psi_bH_first_mV']) -
                                                   float(answers['psi_bH_second_mV']),
                                                   6,
                                                   ),
                              }
    for name, answer in PSI_MORE_ANSWERS.items():
        values[name] = float(answers[answer])
    return values


# ---- size_answers_builder ------------------------------------------------------------
def size_answers_builder(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to turn the journal, width and height of the strip into the answers
    of the figure of each file. The haems and the fit are left out: they need the fit
    file read, which the questions do.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md), as checked by
        strip_values_checker.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS, NO_JOURNAL.

    ---- Outputs ----
    Dict[str, Any]
        The answers to update: journal and size_mode for a journal ("None" is the
        standard journal with size_mode 'default'), columns and height as given.
        Empty when the values hold none of them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    answers: Dict[str, Any] = {}
    if 'journal' in values:
        if values['journal'] == NO_JOURNAL:
            answers.update({'journal': settings.DEFAULT_ANSWERS['journal'],
                            'size_mode': 'default',
                            },
                           )
        else:
            answers.update({'journal': values['journal'], 'size_mode': 'custom'})
    for name in ('columns', 'height'):
        if name in values:
            answers[name] = values[name]
    return answers


# ---- strip_values_builder ------------------------------------------------------------
def strip_values_builder(answers: dict,
                         has_haems: bool,
                         haem_files: Sequence[str],
                         kept: str = '',
                         ) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to give the strip values that show the answers of the run.

    ---- Inputs ----
    answers : dict
        The answers (fit_file, haem_background, decomposition_dataset, haem_mode,
        haem_per_od, ocr_mode, label_mode, compare_layout, delta_psi and the numbers
        of Δψ, journal, columns, height, size_mode); a fit_file of None shows an empty
        fit, a missing label_mode the labels in the chamber, and a missing
        compare_layout the standard one.
    has_haems : bool
        True when the haems are worked out and shown, which ticks the box.
    haem_files : Sequence[str]
        The library files of the fit in use, ticked under Build a fit (none for a fit
        file of the user's own or components from the data).
    kept : str
        The decomposition kept to compare with, in words (its fit and background), or
        '' when none is kept.

    ---- Globals read ----
    NO_JOURNAL.

    ---- Outputs ----
    Dict[str, Any]
        All the strip values (DATA_FORMAT.md). A figure of the standard size
        (size_mode other than 'custom') shows the journal as "None"; the Δψ row shows when the haems are worked out and Δψ is switched on.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    psi_values_builder
    """

    is_custom = answers['size_mode'] == 'custom'
    return {'plot_haems': bool(has_haems),
            'fit_file': str(answers['fit_file'] or ''),
            'haem_background': answers['haem_background'],
            'haem_files': list(haem_files),
            'compare': bool(kept),
            'kept': str(kept),
            'compare_layout': answers.get('compare_layout',
                                          settings.DEFAULT_ANSWERS['compare_layout'],
                                          ),
            'spectra': str(answers.get('decomposition_dataset') or ''),
            'haem_mode': answers['haem_mode'],
            'haem_per_od': bool(answers['haem_per_od']),
            'ocr_mode': answers['ocr_mode'],
            'label_mode': answers.get('label_mode', 'chamber'),
            'event_label_angle': float(answers.get(
                'event_label_angle',
                settings.DEFAULT_ANSWERS['event_label_angle'],
                ),
                                       ),
            **psi_values_builder(answers, has_haems and answers['delta_psi']),
            'journal': answers['journal'] if is_custom else NO_JOURNAL,
            'columns': answers['columns'],
            'height': answers['height'],
            }


# ---- strip_values_checker ------------------------------------------------------------
def strip_values_checker(values: Dict[str, Any]) -> None:
    """
    ---- Summary ----
    Main function to check values meant for the strip before they are shown: the
    names, the background, the haems ticked, whether a decomposition is kept and its
    words, the spectrometer, the ways of showing the haems and the OCR, the per OD
    box, the
    numbers of the Δψ row (numbers, a share above 0, limits above 0 and below 100
    with the lowest first), the journal, a width the journal allows and a height the
    page allows. The width and the height are checked against the journal given with
    them.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md).

    ---- Globals read ----
    VALUE_NAMES, HEIGHT_HELP, BACKGROUND_SHORT_NAMES, COMPARE_LAYOUT_TEXTS,
    HAEM_FORM_TEXTS, OCR_FORM_TEXTS, LABEL_FORM_TEXTS, PSI_FIELDS.

    ---- Outputs ----
    None
        Nothing. Raises ValueError, in plain words, for a value the strip cannot
        show.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _page_journal_finder
    width_choices_lister
    """

    unknown = [name for name in values if name not in VALUE_NAMES]
    if unknown:
        raise ValueError(f"The strip has no value called '{unknown[0]}'; it has "
                         f"{', '.join(VALUE_NAMES)}.",
                         )
    if ('haem_background' in values and
        values['haem_background'] not in BACKGROUND_SHORT_NAMES
        ):
        raise ValueError(f"The strip has no background called "
                         f"'{values['haem_background']}'; it has "
                         f"{', '.join(BACKGROUND_SHORT_NAMES)}.",
                         )
    if 'haem_files' in values and (
        not isinstance(values['haem_files'], (list, tuple)) or
        not all(isinstance(name, str) for name in values['haem_files'])
        ):
        raise ValueError('The haems ticked in the strip are a list of file names; '
                         f"{values['haem_files']!r} is not.",
                         )
    if 'compare' in values and not isinstance(values['compare'], bool):
        raise ValueError('Whether the strip compares is True or False; '
                         f"{values['compare']!r} is not.",
                         )
    if 'kept' in values and not isinstance(values['kept'], str):
        raise ValueError('The decomposition kept in the strip is given in words; '
                         f"{values['kept']!r} is not.",
                         )
    if ('compare_layout' in values and
        values['compare_layout'] not in COMPARE_LAYOUT_TEXTS
        ):
        raise ValueError('The strip cannot show the kept decomposition as '
                         f"'{values['compare_layout']}'; it has "
                         f"{', '.join(COMPARE_LAYOUT_TEXTS)}.",
                         )
    if 'spectra' in values and not isinstance(values['spectra'], str):
        raise ValueError('The spectrometer of the strip is given by its name; '
                         f"{values['spectra']!r} is not.",
                         )
    if 'haem_mode' in values and values['haem_mode'] not in HAEM_FORM_TEXTS:
        raise ValueError(f"The strip cannot show the haems as '{values['haem_mode']}'; "
                         f"it has {', '.join(HAEM_FORM_TEXTS)}.",
                         )
    if 'ocr_mode' in values and values['ocr_mode'] not in OCR_FORM_TEXTS:
        raise ValueError(f"The strip cannot show the OCR as '{values['ocr_mode']}'; "
                         f"it has {', '.join(OCR_FORM_TEXTS)}.",
                         )
    if 'label_mode' in values and values['label_mode'] not in LABEL_FORM_TEXTS:
        raise ValueError(
            f"The labels of the strip cannot show '{values['label_mode']}'; "
            f"they show {', '.join(LABEL_FORM_TEXTS)}.",
            )
    if 'haem_per_od' in values and not isinstance(values['haem_per_od'], bool):
        raise ValueError('The per OD box of the strip is True or False; '
                         f"{values['haem_per_od']!r} is not.",
                         )
    if 'time_tab' in values and values['time_tab'] not in ('', *TIME_TAB_TEXTS):
        raise ValueError(f"The Time regions box has no tab called "
                         f"'{values['time_tab']}'; it has "
                         f"{', '.join(TIME_TAB_TEXTS)}.",
                         )
    if 'event_label_angle' in values:
        angle = values['event_label_angle']
        is_number = isinstance(angle, (int, float)) and not isinstance(angle, bool)
        if not is_number or not ANGLE_LIMITS[0] <= angle <= ANGLE_LIMITS[1]:
            raise ValueError('The angle of the event labels is from 0 to 90°; '
                             f'{angle!r} is not.',
                             )
    if 'delta_psi' in values and not isinstance(values['delta_psi'], bool):
        raise ValueError('Whether the strip shows the Δψ row is True or False; '
                         f"{values['delta_psi']!r} is not.",
                         )
    for name in PSI_FIELDS:
        if name in values and (isinstance(values[name], bool) or
                               not isinstance(values[name], (int, float)) or
                               not math.isfinite(values[name])
                               ):
            raise ValueError(f"The number '{name}' of the Δψ row is a number; "
                             f'{values[name]!r} is not.',
                             )
    if 'psi_share' in values and values['psi_share'] <= 0:
        raise ValueError('The share of the Δψ row is above 0; '
                         f"{values['psi_share']:g} is not.",
                         )
    limits = [values[name]
              for name in ('psi_lowest_percent', 'psi_highest_percent')
              if name in values
              ]
    if not all(0 < limit < 100 for limit in limits) or limits != sorted(set(limits)):
        raise ValueError('The limits of the Δψ row are above 0 and below 100, the '
                         'lowest first; '
                         f"{' and '.join(f'{limit:g}' for limit in limits)} "
                         f"{'are' if len(limits) > 1 else 'is'} not.",
                         )
    if 'journal' in values:
        _page_journal_finder(values['journal'])
        if 'columns' in values and values['journal'] != NO_JOURNAL:
            allowed = [columns for columns, _ in width_choices_lister(values['journal'])]
            if values['columns'] not in allowed:
                raise ValueError(f"A width of {values['columns']:g} columns is not "
                                 f"one the journal '{values['journal']}' allows "
                                 f"({', '.join(f'{c:g}' for c in allowed)}).",
                                 )
    if 'height' in values:
        height = values['height']
        is_number = isinstance(height, (int, float)) and not isinstance(height, bool)
        if not is_number or not 0 < height <= 1:
            raise ValueError(f'The height of the strip is {HEIGHT_HELP}; '
                             f'{height!r} is not.',
                             )


# ---- width_choices_lister ------------------------------------------------------------
def width_choices_lister(journal: str) -> List[Tuple[float, str]]:
    """
    ---- Summary ----
    Main function to list the widths a journal allows, each with the text shown in
    the drop-down.

    ---- Inputs ----
    journal : str
        NO_JOURNAL or a key of settings.JOURNAL_SPECS.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    List[Tuple[float, str]]
        [(columns, '1 column (89 mm)'), ...] in the order of the settings.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _page_journal_finder
    """

    widths = settings.JOURNAL_SPECS[_page_journal_finder(journal)]['widths_mm']
    return [(columns,
             f"{columns:g} column{'' if columns == 1 else 's'} ({width_mm:g} mm)",
             )
            for columns, width_mm in widths.items()
            ]
