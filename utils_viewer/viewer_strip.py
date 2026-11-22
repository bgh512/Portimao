"""
The settings strip under the plot: the haems, the fit, the background, the decomposition
kept to compare with, the journal, the figure size and the times of the edges dragged on
the plot.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.questions import typed_number_reader
from utils_shared.spectral_decomposer import (BACKGROUND_SHORT_NAMES,
                                              fit_describer,
                                              OWN_HAEMS_NAME,
                                              )
from utils_shared.survey import JOURNAL_NAMES


# ---- CONSTANTS -----------------------------------------------------------------------
# The journal shown as "None": the standard size, on the page of the standard journal.
NO_JOURNAL = 'none'
NO_JOURNAL_TEXT = 'None (standard size)'
VALUE_NAMES = ('plot_haems',
               'fit_file',
               'haem_background',
               'haem_files',
               'compare',
               'kept',
               'journal',
               'columns',
               'height',
               )
# The button that folds the tick boxes of the library haems out and away.
BUILD_CLOSED_TEXT = 'Build a fit ▸'
BUILD_OPEN_TEXT = 'Build a fit ▾'
# The button that keeps the decomposition in use to compare the next ones with, and the
# line under the first row that says which one is kept.
KEEP_TEXT = 'Keep to compare'
STOP_TEXT = 'Stop comparing'
KEPT_PREFIX = 'Kept to compare (dashed on the plot): '
LAST_TICK_NOTE = 'One haem at least stays ticked: tick another first, or choose a preset.'
HEIGHT_HELP = 'a share of a page: a number above 0 and up to 1, such as 0.5'
ERROR_BACKGROUND = '#ffd6d6'
ERROR_TEXT = '#b00020'
NOTE_TEXT = '#404040'
MINUTES_HELP = 'Type a number of minutes, 0 or more.'


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
        self._every_file = tk.BooleanVar(master=parent, value=True)
        tk.Checkbutton(self.frame,
                       text='Every file',
                       variable=self._every_file,
                       command=self._every_file_handler,
                       bg=background,
                       activebackground=background,
                       highlightthickness=0,
                       ).pack(side='left', padx=(12, 4))
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
            value, note = minutes_checker(text)
            if value is None:
                box.configure(bg=ERROR_BACKGROUND)
                self._note.configure(text=note, fg=ERROR_TEXT)
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
                      ) -> None:
        """
        ---- Summary ----
        Method to make one typing box for each field, each after its name, followed by
        "min", and set the tick box.

        ---- Inputs ----
        fields : List[Tuple[str, str]]
            [(field, name shown before its box)] in order.
        is_every_file : bool
            Whether "Every file" is ticked.

        ---- Globals read ----
        None.

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
        tk.Label(self._boxes_frame, text='min', bg=background).pack(side='left',
                                                                    padx=(4, 0),
                                                                    )
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
    kept), a drop-down of the journal, a drop-down of the widths that journal allows and
    a typing box for the height. It tells the window what the user changed and can be
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
    _background_handler
    _build_toggler
    _change_reporter
    _compare_handler
    _fit_handler
    _haems_handler
    _height_handler
    _journal_handler
    _size_refresher
    _tick_handler
    _width_handler
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
        _background_handler
        _build_toggler
        _compare_handler
        _fit_handler
        _haems_handler
        _height_handler
        _journal_handler
        _size_refresher
        _width_handler
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
                                        'journal': NO_JOURNAL,
                                        'columns': standard['columns'],
                                        'height': standard['height'],
                                        }
        self._journals = [NO_JOURNAL] + list(JOURNAL_NAMES)
        self._backgrounds = list(BACKGROUND_SHORT_NAMES)
        self._width_columns: List[float] = []
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

        # ---- 3 Second row: the journal, the width and the height ---------------------
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

        # ---- 4 What the user does ----------------------------------------------------
        self._fit_combo.bind('<<ComboboxSelected>>', self._fit_handler)
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
        or stops comparing. The program says which one is kept (the value 'kept').

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

    # ---- _size_refresher -------------------------------------------------------------
    def _size_refresher(self) -> None:
        """
        ---- Summary ----
        Method to show the kept values in every part of the strip: the widths offered
        follow the journal, the width and the height are greyed for "None", the button
        that keeps a decomposition is greyed while no haems are shown, the line saying
        which one is kept shows only while one is, and the whole strip is greyed while
        the program is not listening.

        ---- Inputs ----
        None.

        ---- Globals read ----
        KEEP_TEXT, KEPT_PREFIX, NO_JOURNAL, NOTE_TEXT, STOP_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        height_checker
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
        if values['kept']:
            self._kept_label.configure(text=KEPT_PREFIX + values['kept'])
            self._kept_label.pack(before=self._lower, pady=(0, 3), fill='x')
        else:
            self._kept_label.pack_forget()
        self._journal_combo.configure(state=choice_state)
        if is_standard or not self._is_enabled:
            self._width_combo.configure(state='disabled')
            self._height_entry.configure(state='disabled')

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
def kept_decomposition_builder(answers: dict, fit: dict) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to keep the decomposition in use, to compare the next ones with: the
    fit, the answers it was worked out with and its name in words.

    ---- Inputs ----
    answers : dict
        The answers in use (fit_file, haem_files, haem_background,
        decomposition_dataset).
    fit : dict
        The fit in use (spectral_decomposer.fit_importer); it is kept as it is, as a
        fit is never changed once read.

    ---- Globals read ----
    BACKGROUND_SHORT_NAMES.

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
                    }
    background = BACKGROUND_SHORT_NAMES.get(answers['haem_background'],
                                            answers['haem_background'],
                                            )
    text = (f"{fit_describer(answers['fit_file'], kept_answers['haem_files'])} with "
            f'the {background} background'
            )
    return {'fit': fit, 'answers': kept_answers, 'text': text}


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
        The answers (fit_file, haem_background, journal, columns, height, size_mode);
        a fit_file of None shows an empty fit.
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
        (size_mode other than 'custom') shows the journal as "None".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    is_custom = answers['size_mode'] == 'custom'
    return {'plot_haems': bool(has_haems),
            'fit_file': str(answers['fit_file'] or ''),
            'haem_background': answers['haem_background'],
            'haem_files': list(haem_files),
            'compare': bool(kept),
            'kept': str(kept),
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
    words, the journal, a width the journal allows and a height the page allows. The
    width and the height are checked against the journal given with them.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md).

    ---- Globals read ----
    VALUE_NAMES, HEIGHT_HELP, BACKGROUND_SHORT_NAMES.

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
