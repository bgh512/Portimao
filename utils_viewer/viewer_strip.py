"""
The settings strip under the plot: the haems, the fit, the background, the decomposition
kept to compare with, the spectrometer, how the haems and the OCR are shown, the numbers
of Δψ, the journal, the figure size and the times of the edges dragged on the plot.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import copy
import math
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.questions import typed_number_reader
from utils_shared.spectral_decomposer import (BACKGROUND_SHORT_NAMES,
                                              fit_describer,
                                              OWN_HAEMS_NAME,
                                              )
from utils_shared.survey import JOURNAL_NAMES, TEMPERATURE_LIMITS_C


# ---- CONSTANTS -----------------------------------------------------------------------
# The numbers of the Δψ row: each haem's midpoint potential with the other haem
# oxidised and how far it falls when the other is reduced (mV), which the user types,
# then the numbers opened by "More".
PSI_MIDPOINT_FIELDS = ('psi_bH_mV', 'psi_bL_mV', 'psi_fall_mV')
PSI_MORE_FIELDS = ('psi_share',
                   'temperature_c',
                   'psi_lowest_percent',
                   'psi_highest_percent',
                   )
PSI_FIELDS = PSI_MIDPOINT_FIELDS + PSI_MORE_FIELDS
# The answer each number of the "More" line is kept in.
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
               'spectra',
               'haem_mode',
               'haem_per_od',
               'ocr_per_od',
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
# The button that folds the tick boxes of the library haems out and away.
BUILD_CLOSED_TEXT = 'Build a fit ▸'
BUILD_OPEN_TEXT = 'Build a fit ▾'
# The button that keeps the decomposition in use to compare the next ones with, the two
# that choose between it and the one on the plot, and the line under the first row that
# says which one is kept.
KEEP_TEXT = 'Keep to compare'
STOP_TEXT = 'Keep this one'
BACK_TEXT = 'Go back to kept'
# What a click on BACK_TEXT is told as: a click, not a value the strip keeps.
BACK_CHANGE = 'go_back'
KEPT_PREFIX = 'Kept to compare (dashed on the plot): '
LAST_TICK_NOTE = 'One haem at least stays ticked: tick another first, or choose a preset.'
HEIGHT_HELP = 'a share of a page: a number above 0 and up to 1, such as 0.5'
ERROR_BACKGROUND = '#ffd6d6'
ERROR_TEXT = '#b00020'
NOTE_TEXT = '#404040'
MINUTES_HELP = 'Type a number of minutes, 0 or more.'
# What to type in a box of the edges row, by the unit of the step.
UNIT_HELP = {'min': MINUTES_HELP, 's': 'Type a number of seconds, 0 or more.'}
EVERY_FILE_TEXT = 'Every file'


# ---- EdgeRow -------------------------------------------------------------------------
class EdgeRow:
    """
    ---- Summary ----
    The row of the strip shown while edges are dragged on the plot: a typing box for
    each edge, holding its value for the file shown, and the "Every file" tick box. It
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
    _value_handler
    fields_setter
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
                 ) -> None:
        """
        ---- Summary ----
        Method to build the row, with no boxes until fields_setter.

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
        self._boxes: Dict[str, Any] = {}
        self._shown: Dict[str, str] = {}
        self.frame = tk.Frame(parent, bg=background)
        self._boxes_frame = tk.Frame(self.frame, bg=background)
        self._boxes_frame.pack(side='left')
        self._help = UNIT_HELP['min']
        self._every_file = tk.BooleanVar(master=parent, value=True)
        self._tick = tk.Checkbutton(self.frame,
                                    text=EVERY_FILE_TEXT,
                                    variable=self._every_file,
                                    command=self._every_file_handler,
                                    bg=background,
                                    activebackground=background,
                                    highlightthickness=0,
                                    )
        self._tick.pack(side='left', padx=(12, 4))
        self._note = tk.Label(self.frame, text='', bg=background, fg=NOTE_TEXT)
        self._note.pack(side='left', padx=(0, 4))

    # ---- ROW HELPERS -----------------------------------------------------------------

    # ---- _every_file_handler ---------------------------------------------------------
    def _every_file_handler(self) -> None:
        """
        ---- Summary ----
        Method to pass on the new state of the "Every file" tick box.

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

    # ---- fields_setter ---------------------------------------------------------------
    def fields_setter(self,
                      fields: List[Tuple[str, str]],
                      is_every_file: bool,
                      unit: str = 'min',
                      tick_text: str = EVERY_FILE_TEXT,
                      ) -> None:
        """
        ---- Summary ----
        Method to make one typing box for each field, each after its name, followed by
        the unit, and set the tick box and its words.

        ---- Inputs ----
        fields : List[Tuple[str, str]]
            [(field, name shown before its box)] in order.
        is_every_file : bool
            Whether the tick box is ticked.
        unit : str
            The unit written after the boxes: 'min' or 's' (a key of UNIT_HELP).
        tick_text : str
            The words of the tick box: "Every file", or those of the step's own
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
        for index, (key, name) in enumerate(fields):
            gap = 12 if index and name[:1].isupper() else 4
            tk.Label(self._boxes_frame,
                     text=name,
                     bg=background,
                     ).pack(side='left', padx=(gap, 4))
            box = tk.Entry(self._boxes_frame,
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
        tk.Label(self._boxes_frame, text=unit, bg=background).pack(side='left',
                                                                   padx=(4, 0),
                                                                   )
        self._help = UNIT_HELP[unit]
        self._tick.configure(text=tick_text)
        self._every_file.set(is_every_file)
        self._note.configure(text='')

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
    The strip under the plot that always shows the current choices: a tick box for the
    haems, a drop-down of the fits, a drop-down of the backgrounds, a button that folds
    out a tick box for each haem of the library (Build a fit), a button that keeps the
    decomposition in use to compare the next ones with (with a line saying which one is
    kept; while one is kept it reads "Keep this one", and a second button goes back to
    the kept one), a drop-down of the spectrometer whose spectra hold the haems (shown when the
    files share more than one), a drop-down of how the haems are shown with a "per OD"
    box, an "OCR per OD" box (both boxes shown only when OD values were entered), a
    row of the numbers of Δψ (shown only while Δψ is worked out: the midpoint of bH
    and of bL and the fall typed, each midpoint with the other haem reduced filled in,
    a button for the paper's values, and the share, the temperature and the limits as
    text, or as boxes when "More" is ticked), a drop-down of the journal, a drop-down of the widths that journal allows and a typing
    box for the height. It tells the window what the user changed and can be
    set by the program; it changes nothing by itself. It starts greyed out, until the
    program says it is listening. Every method runs on the window thread, except
    values_reader.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the strip, for the window to place.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS, JOURNAL_NAMES,
    BACKGROUND_SHORT_NAMES, OWN_HAEMS_NAME and the module constants.

    ---- Methods ----
    __init__
    _back_handler
    _background_handler
    _build_toggler
    _change_reporter
    _compare_handler
    _fit_handler
    _form_handler
    _haems_handler
    _height_handler
    _journal_handler
    _more_toggler
    _paper_handler
    _per_od_handler
    _psi_handler
    _size_refresher
    _spectra_handler
    _tick_handler
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
        _back_handler
        _background_handler
        _build_toggler
        _compare_handler
        _fit_handler
        _form_handler
        _haems_handler
        _height_handler
        _journal_handler
        _more_toggler
        _paper_handler
        _per_od_handler
        _psi_handler
        _size_refresher
        _spectra_handler
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
                                        'spectra': standard['decomposition_dataset'],
                                        'haem_mode': standard['haem_mode'],
                                        'haem_per_od': bool(standard['haem_per_od']),
                                        'ocr_per_od': standard['ocr_mode'] == 'od',
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
        self._has_percent = False
        self._has_od = False
        self._fit_names: List[str] = [self._values['fit_file']]
        self._haems_by_file: Dict[str, str] = {}
        self._tick_vars: Dict[str, Any] = {}
        self._tick_boxes: Dict[str, Any] = {}
        self._is_enabled = False
        self._is_panel_open = False
        self._tk = tk
        self._background = background
        self.frame = tk.Frame(parent, bg=background)

        # ---- 2 First row: the haems and the fit --------------------------------------
        upper = tk.Frame(self.frame, bg=background)
        upper.pack(pady=(0, 3))
        self._haems = tk.BooleanVar(master=parent, value=self._values['plot_haems'])
        self._haems_box = tk.Checkbutton(upper,
                                         text='Haems',
                                         variable=self._haems,
                                         command=self._haems_handler,
                                         bg=background,
                                         activebackground=background,
                                         highlightthickness=0,
                                         )
        self._haems_box.pack(side='left', padx=(4, 12))
        tk.Label(upper, text='Fit', bg=background).pack(side='left', padx=(0, 4))
        self._fit_combo = ttk.Combobox(upper,
                                       state='readonly',
                                       width=36,
                                       values=[self._values['fit_file']],
                                       )
        self._fit_combo.set(self._values['fit_file'])
        self._fit_combo.pack(side='left', padx=(0, 12))
        tk.Label(upper, text='Background', bg=background).pack(side='left', padx=(0, 4))
        self._background_combo = ttk.Combobox(upper,
                                              state='readonly',
                                              width=30,
                                              values=list(
                                                  BACKGROUND_SHORT_NAMES.values(),
                                                  ),
                                              )
        self._background_combo.pack(side='left', padx=(0, 12))
        self._build_button = tk.Button(upper,
                                       text=BUILD_CLOSED_TEXT,
                                       command=self._build_toggler,
                                       )
        self._build_button.pack(side='left', padx=(0, 4))
        self._compare_button = tk.Button(upper,
                                         text=KEEP_TEXT,
                                         command=self._compare_handler,
                                         )
        self._compare_button.pack(side='left', padx=(0, 4))
        # _size_refresher places it only while a decomposition is kept.
        self._back_button = tk.Button(upper,
                                      text=BACK_TEXT,
                                      command=self._back_handler,
                                      )
        self._upper = upper

        # ---- 2.1 The tick boxes of the library haems, folded away at first -----------
        # library_setter fills them in.
        self._panel = tk.Frame(self.frame, bg=background)

        # ---- 2.2 The line saying which decomposition is kept, hidden until one is ----
        self._kept_label = tk.Label(self.frame,
                                    text='',
                                    bg=background,
                                    fg=NOTE_TEXT,
                                    anchor='w',
                                    )

        # ---- 3 Second row: the spectrometer and how the haems and the OCR are shown --
        # _size_refresher places the parts in use: the spectrometer only when there is
        # a choice, the per OD boxes only when OD values were entered.
        middle = tk.Frame(self.frame, bg=background)
        middle.pack(pady=(0, 3))
        self._spectra_label = tk.Label(middle, text='Spectra', bg=background)
        self._spectra_combo = ttk.Combobox(middle, state='readonly', width=8)
        self._form_label = tk.Label(middle, text='Haems as', bg=background)
        self._form_combo = ttk.Combobox(middle, state='readonly', width=17)
        self._haem_od = tk.BooleanVar(master=parent, value=self._values['haem_per_od'])
        self._haem_od_box = tk.Checkbutton(
            middle,
            text='per OD',
            variable=self._haem_od,
            command=lambda: self._per_od_handler('haem_per_od'),
            bg=background,
            activebackground=background,
            highlightthickness=0,
            )
        self._ocr_od = tk.BooleanVar(master=parent, value=self._values['ocr_per_od'])
        self._ocr_od_box = tk.Checkbutton(
            middle,
            text='OCR per OD',
            variable=self._ocr_od,
            command=lambda: self._per_od_handler('ocr_per_od'),
            bg=background,
            activebackground=background,
            highlightthickness=0,
            )

        # ---- 3.1 The Δψ row, placed only while Δψ is worked out ----------------------
        # First line: each haem's midpoint, typed, then (after the arrow) its midpoint
        # with the other haem reduced, filled in and not typed in; the fall; the
        # button of the paper's values; the box that opens the second line. Second
        # line: the other numbers as text, or as boxes when "More" is ticked.
        self._psi_row = tk.Frame(self.frame, bg=background)
        first = tk.Frame(self._psi_row, bg=background)
        first.pack()
        self._psi_boxes: Dict[str, Any] = {}
        self._psi_seconds: Dict[str, Any] = {}

        def box_maker(parent_line: Any, name: str, gap: Tuple[int, int]) -> None:
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

        tk.Label(first, text='Δψ', bg=background).pack(side='left', padx=(4, 8))
        for haem, name in (('bH', 'psi_bH_mV'), ('bL', 'psi_bL_mV')):
            tk.Label(first, text=haem, bg=background).pack(side='left', padx=(0, 4))
            box_maker(first, name, (0, 2))
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
            second.pack(side='left', padx=(0, 12))
            self._psi_seconds[name] = second
        tk.Label(first, text='fall', bg=background).pack(side='left', padx=(0, 4))
        box_maker(first, 'psi_fall_mV', (0, 2))
        tk.Label(first, text='mV', bg=background).pack(side='left', padx=(0, 12))
        self._paper_button = tk.Button(first,
                                       text=PAPER_TEXT,
                                       command=self._paper_handler,
                                       )
        self._paper_button.pack(side='left', padx=(0, 8))
        self._more = tk.BooleanVar(master=parent, value=False)
        self._more_box = tk.Checkbutton(first,
                                        text='More',
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
                                     )
        self._psi_more = tk.Frame(self._psi_row, bg=background)
        for words, name, after in (('Share', 'psi_share', ''),
                                   ('Temperature', 'temperature_c', '°C'),
                                   ('Given between', 'psi_lowest_percent', ''),
                                   ('and', 'psi_highest_percent', '% reduced'),
                                   ):
            tk.Label(self._psi_more, text=words, bg=background).pack(side='left',
                                                                     padx=(4, 4),
                                                                     )
            box_maker(self._psi_more, name, (0, 2))
            tk.Label(self._psi_more, text=after, bg=background).pack(side='left',
                                                                     padx=(0, 8),
                                                                     )
        self._psi_note = tk.Label(self._psi_row, text='', bg=background, fg=ERROR_TEXT)

        # ---- 4 Third row: the journal, the width and the height ----------------------
        lower = tk.Frame(self.frame, bg=background)
        lower.pack()
        self._lower = lower
        tk.Label(lower, text='Journal', bg=background).pack(side='left', padx=(4, 4))
        self._journal_combo = ttk.Combobox(lower,
                                           state='readonly',
                                           width=19,
                                           values=[NO_JOURNAL_TEXT]
                                           + list(JOURNAL_NAMES.values()),
                                           )
        self._journal_combo.pack(side='left', padx=(0, 12))
        tk.Label(lower, text='Width', bg=background).pack(side='left', padx=(0, 4))
        self._width_combo = ttk.Combobox(lower, state='readonly', width=20)
        self._width_combo.pack(side='left', padx=(0, 12))
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

        # ---- 5 What the user does ----------------------------------------------------
        self._fit_combo.bind('<<ComboboxSelected>>', self._fit_handler)
        self._spectra_combo.bind('<<ComboboxSelected>>', self._spectra_handler)
        self._form_combo.bind('<<ComboboxSelected>>', self._form_handler)
        self._background_combo.bind('<<ComboboxSelected>>', self._background_handler)
        self._journal_combo.bind('<<ComboboxSelected>>', self._journal_handler)
        self._width_combo.bind('<<ComboboxSelected>>', self._width_handler)
        self._height_entry.bind('<Return>', self._height_handler)
        self._height_entry.bind('<FocusOut>', self._height_handler)
        self._size_refresher()

    # ---- STRIP HELPERS ---------------------------------------------------------------

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
        self._values['fit_file'] = self._fit_combo.get()
        self._fit_combo.selection_clear()
        self._size_refresher()
        self._change_reporter(before)

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

    # ---- _more_toggler ---------------------------------------------------------------
    def _more_toggler(self) -> None:
        """
        ---- Summary ----
        Method to take the "More" box of the Δψ row: ticked, the share, the temperature
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

    # ---- _per_od_handler -------------------------------------------------------------
    def _per_od_handler(self, name: str) -> None:
        """
        ---- Summary ----
        Method to take one of the two per OD tick boxes.

        ---- Inputs ----
        name : str
            'haem_per_od' or 'ocr_per_od', the value of the box clicked.

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
        box = self._haem_od if name == 'haem_per_od' else self._ocr_od
        self._values[name] = bool(box.get())
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

    # ---- _size_refresher -------------------------------------------------------------
    def _size_refresher(self) -> None:
        """
        ---- Summary ----
        Method to show the kept values in every part of the strip: the widths offered
        follow the journal, the width and the height are greyed for "None", the button
        that keeps a decomposition is greyed while no haems are shown, the button that
        goes back to the kept one and the line saying which one is kept show only
        while one is, the spectrometer shows only when
        there is a choice, the per OD boxes only when OD values were entered (the one
        of the haems greyed for % oxidised, which has no per OD), the Δψ row only
        while Δψ is worked out (its filled-in midpoints following the typed ones and
        the fall), and the whole strip is greyed while the program is not listening.

        ---- Inputs ----
        None.

        ---- Globals read ----
        HAEM_FORM_TEXTS, KEEP_TEXT, KEPT_PREFIX, NO_JOURNAL, NOTE_TEXT, STOP_TEXT.
        (BACK_TEXT is set on its button once, when it is built.)

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        haem_form_choices_lister
        height_checker
        psi_seconds_filler
        psi_summary_writer
        width_choices_lister
        """

        values = self._values
        is_standard = values['journal'] == NO_JOURNAL
        self._haems.set(values['plot_haems'])
        is_own = values['fit_file'] == OWN_HAEMS_NAME
        self._fit_combo.configure(values=self._fit_names + ([OWN_HAEMS_NAME]
                                                            if is_own
                                                            else []
                                                            ),
                                  )
        self._fit_combo.set(values['fit_file'])
        if values['haem_background'] in self._backgrounds:
            self._background_combo.current(
                self._backgrounds.index(values['haem_background']),
                )
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
        self._fit_combo.configure(state=choice_state)
        self._background_combo.configure(state=choice_state)
        self._build_button.configure(state=button_state)
        for box in self._tick_boxes.values():
            box.configure(state=button_state)
        can_compare = self._is_enabled and values['plot_haems']
        self._compare_button.configure(
            text=STOP_TEXT if values['compare'] else KEEP_TEXT,
            state='normal' if can_compare else 'disabled',
            )
        if values['compare']:
            self._back_button.configure(state='normal' if can_compare else 'disabled')
            self._back_button.pack(side='left', padx=(0, 4))
        else:
            self._back_button.pack_forget()
        if values['kept']:
            self._kept_label.configure(text=KEPT_PREFIX + values['kept'])
            self._kept_label.pack(before=self._lower, pady=(0, 3), fill='x')
        else:
            self._kept_label.pack_forget()
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
        self._ocr_od.set(values['ocr_per_od'])
        can_scale = (self._is_enabled and
                     values['plot_haems'] and
                     values['haem_mode'] != 'percent'
                     )
        self._haem_od_box.configure(state='normal' if can_scale else 'disabled')
        self._ocr_od_box.configure(state=button_state)
        has_choice = len(self._spectra_names) > 1
        parts = [(self._spectra_label, has_choice, (4, 4)),
                 (self._spectra_combo, has_choice, (0, 12)),
                 (self._form_label, True, (4, 4)),
                 (self._form_combo, True, (0, 4)),
                 (self._haem_od_box, self._has_od, (0, 12)),
                 (self._ocr_od_box, self._has_od, (0, 4)),
                 ]
        for part, _, _ in parts:
            part.pack_forget()
        for part, is_shown, gap in parts:
            if is_shown:
                part.pack(side='left', padx=gap)
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
        (self._psi_more if self._is_more_open else self._psi_summary).pack()
        if values['delta_psi']:
            self._psi_row.pack(before=self._lower, pady=(0, 3))
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
                       ) -> None:
        """
        ---- Summary ----
        Method to say what the strip offers: the spectrometers of the "Spectra"
        drop-down (shown only with more than one), whether % oxidised is in the "Haems
        as" drop-down, and whether the two per OD boxes are shown. The values stay.

        ---- Inputs ----
        spectra : List[str]
            The spectrometers every file has, as they are to be listed.
        has_percent : bool
            True when at least one file has both regions, so % oxidised is offered.
        has_od : bool
            True when OD values were entered, so the per OD boxes are shown.

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
        self._size_refresher()

    # ---- fits_setter -----------------------------------------------------------------
    def fits_setter(self, names: List[str]) -> None:
        """
        ---- Summary ----
        Method to give the drop-down of the fits its list. The fit shown stays.

        ---- Inputs ----
        names : List[str]
            File names of the fits, as they are to be listed.

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

        self._fit_names = list(names)
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
        for child in self._panel.winfo_children():
            child.destroy()
        self._haems_by_file = {item['file']: item['haem'] for item in haems}
        self._tick_vars, self._tick_boxes = {}, {}
        lines: Dict[str, Any] = {}
        for item in haems:
            if item['type'] not in lines:
                lines[item['type']] = tk.Frame(self._panel, bg=self._background)
                lines[item['type']].pack(anchor='w')
                tk.Label(lines[item['type']],
                         text=item['type'],
                         width=6,
                         anchor='w',
                         bg=self._background,
                         ).pack(side='left', padx=(4, 4))
            name = item['file']
            self._tick_vars[name] = tk.BooleanVar(master=self._panel, value=False)
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
    Main function to turn the spectrometer and the ways of showing the haems and the
    OCR of the strip into the answers of the run.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md), as checked by
        strip_values_checker.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        The answers to update: decomposition_dataset for the spectrometer, haem_mode
        and haem_per_od as given, and ocr_mode 'od' for the OCR per OD box ticked,
        'raw' for it unticked. Empty when the values hold none of them.

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
    for name in ('haem_mode', 'haem_per_od'):
        if name in values:
            answers[name] = values[name]
    if 'ocr_per_od' in values:
        answers['ocr_mode'] = 'od' if values['ocr_per_od'] else 'raw'
    return answers


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
                     f"with bH reduced): a fall of {values['psi_fall_mV']:g} mV.",
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
    line of text shown in the Δψ row while "More" is not ticked.

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
        haem_per_od, ocr_mode, delta_psi and the numbers of Δψ, journal, columns,
        height, size_mode); a fit_file of None shows an empty fit.
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
        (size_mode other than 'custom') shows the journal as "None"; the OCR per OD
        box is ticked for the OCR per OD, unticked for the plain OCR and its % of the
        range; the Δψ row shows when the haems are worked out and Δψ is switched on.

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
            'spectra': str(answers.get('decomposition_dataset') or ''),
            'haem_mode': answers['haem_mode'],
            'haem_per_od': bool(answers['haem_per_od']),
            'ocr_per_od': answers['ocr_mode'] == 'od',
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
    words, the spectrometer, the way of showing the haems, the per OD boxes, the
    numbers of the Δψ row (numbers, a share above 0, limits above 0 and below 100
    with the lowest first), the journal, a width the journal allows and a height the
    page allows. The width and the height are checked against the journal given with
    them.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md).

    ---- Globals read ----
    VALUE_NAMES, HEIGHT_HELP, BACKGROUND_SHORT_NAMES, HAEM_FORM_TEXTS, PSI_FIELDS.

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
    if 'spectra' in values and not isinstance(values['spectra'], str):
        raise ValueError('The spectrometer of the strip is given by its name; '
                         f"{values['spectra']!r} is not.",
                         )
    if 'haem_mode' in values and values['haem_mode'] not in HAEM_FORM_TEXTS:
        raise ValueError(f"The strip cannot show the haems as '{values['haem_mode']}'; "
                         f"it has {', '.join(HAEM_FORM_TEXTS)}.",
                         )
    for name in ('haem_per_od', 'ocr_per_od'):
        if name in values and not isinstance(values[name], bool):
            raise ValueError('A per OD box of the strip is True or False; '
                             f'{values[name]!r} is not.',
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
