"""
The settings strip under the plot: the haems, the fit, the journal and the figure size.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.survey import JOURNAL_NAMES


# ---- CONSTANTS -----------------------------------------------------------------------
# The journal shown as "None": the standard size, on the page of the standard journal.
NO_JOURNAL = 'none'
NO_JOURNAL_TEXT = 'None (standard size)'
VALUE_NAMES = ('plot_haems', 'fit_file', 'journal', 'columns', 'height')
HEIGHT_HELP = 'a share of a page: a number above 0 and up to 1, such as 0.5'
ERROR_BACKGROUND = '#ffd6d6'
ERROR_TEXT = '#b00020'
NOTE_TEXT = '#404040'


# ---- SettingsStrip -------------------------------------------------------------------
class SettingsStrip:
    """
    ---- Summary ----
    The strip under the plot that always shows the current choices: a tick box for the
    haems, a drop-down of the fits, a drop-down of the journal, a drop-down of the
    widths that journal allows and a typing box for the height. It tells the window
    what the user changed and can be set by the program; it changes nothing by itself.
    It starts greyed out, until the program says it is listening. Every method runs on
    the window thread, except values_reader.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the strip, for the window to place.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS, JOURNAL_NAMES and the module
    constants.

    ---- Methods ----
    __init__
    _change_reporter
    _fit_handler
    _haems_handler
    _height_handler
    _journal_handler
    _size_refresher
    _width_handler
    fits_setter
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
                                        'journal': NO_JOURNAL,
                                        'columns': standard['columns'],
                                        'height': standard['height'],
                                        }
        self._journals = [NO_JOURNAL] + list(JOURNAL_NAMES)
        self._width_columns: List[float] = []
        self._is_enabled = False
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
        self._fit_combo.pack(side='left', padx=(0, 4))

        # ---- 3 Second row: the journal, the width and the height ---------------------
        lower = tk.Frame(self.frame, bg=background)
        lower.pack()
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
        self._journal_combo.bind('<<ComboboxSelected>>', self._journal_handler)
        self._width_combo.bind('<<ComboboxSelected>>', self._width_handler)
        self._height_entry.bind('<Return>', self._height_handler)
        self._height_entry.bind('<FocusOut>', self._height_handler)
        self._size_refresher()

    # ---- STRIP HELPERS ---------------------------------------------------------------

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
        """

        before = dict(self._values)
        self._values['fit_file'] = self._fit_combo.get()
        self._fit_combo.selection_clear()
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
        follow the journal, the width and the height are greyed for "None", and the
        whole strip is greyed while the program is not listening.

        ---- Inputs ----
        None.

        ---- Globals read ----
        NO_JOURNAL, NOTE_TEXT.

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
        self._fit_combo.set(values['fit_file'])
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
        self._haems_box.configure(state='normal' if self._is_enabled else 'disabled')
        self._fit_combo.configure(state=choice_state)
        self._journal_combo.configure(state=choice_state)
        if is_standard or not self._is_enabled:
            self._width_combo.configure(state='disabled')
            self._height_entry.configure(state='disabled')

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
        None.
        """

        self._fit_combo.configure(values=list(names))

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

        return dict(self._values)

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
        if self._values['journal'] == NO_JOURNAL:
            self._standard_size = (self._values['columns'], self._values['height'])
        else:
            self._custom_size = (self._values['columns'], self._values['height'])
        self._size_refresher()


# ---- HELPERS -------------------------------------------------------------------------


# ---- _number_reader ------------------------------------------------------------------
def _number_reader(text: str) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to read a typed number, with a point or a comma as the decimal
    sign.

    ---- Inputs ----
    text : str
        What was typed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The number, or None when the text is not one.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        number = float(text.strip().replace(',', '.'))
    except ValueError:
        return None
    return number if number == number and abs(number) != float('inf') else None


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
    _number_reader
    _page_journal_finder
    """

    page_mm = settings.JOURNAL_SPECS[_page_journal_finder(journal)]['page_height_mm']
    height = _number_reader(text)
    if height is None or not 0 < height <= 1:
        return None, f'Type {HEIGHT_HELP}.'
    return height, f'of a page ({round(height * page_mm, 1):g} mm)'


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
def strip_values_builder(answers: dict, has_haems: bool) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to give the strip values that show the answers of the run.

    ---- Inputs ----
    answers : dict
        The answers (fit_file, journal, columns, height, size_mode); a fit_file of
        None shows an empty fit.
    has_haems : bool
        True when the haems are worked out and shown, which ticks the box.

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
            'journal': answers['journal'] if is_custom else NO_JOURNAL,
            'columns': answers['columns'],
            'height': answers['height'],
            }


# ---- strip_values_checker ------------------------------------------------------------
def strip_values_checker(values: Dict[str, Any]) -> None:
    """
    ---- Summary ----
    Main function to check values meant for the strip before they are shown: the
    names, the journal, a width the journal allows and a height the page allows. The
    width and the height are checked against the journal given with them.

    ---- Inputs ----
    values : Dict[str, Any]
        Some or all of the strip values (DATA_FORMAT.md).

    ---- Globals read ----
    VALUE_NAMES, HEIGHT_HELP.

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
