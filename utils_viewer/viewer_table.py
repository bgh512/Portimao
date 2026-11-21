"""
The tables of the window, filled in by clicking a cell and typing: the OD values of each
file and the label and concentration of each event.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.questions import typed_number_reader


# ---- CONSTANTS -----------------------------------------------------------------------
# The kinds of cell: a number above 0 that must be filled in, a number of 0 or more that
# may be left empty, and a label that must be filled in.
ABOVE_ZERO = 'above_zero'
ZERO_OR_MORE = 'zero_or_more'
LABEL = 'label'
NEEDED_KINDS = (ABOVE_ZERO, LABEL)
EMPTY = 'empty'  # the problem of a needed cell left empty
# what to type in a wrong cell of each kind, in the sentence said after Confirm
KIND_HINTS = {ABOVE_ZERO: 'a number above 0',
              ZERO_OR_MORE: 'a number of 0 or more',
              }
# The cells of each table: (name of the value, column heading, kind of cell).
OD_COLUMNS = (('OD', 'OD', ABOVE_ZERO),
              ('volume', 'Volume (mL)', ABOVE_ZERO),
              ('dilution_factor', 'Dilution', ABOVE_ZERO),
              )
LABEL_COLUMNS = (('label', 'Label', LABEL),
                 ('concentration_uM', 'Concentration (µM)', ZERO_OR_MORE),
                 )
CELL_WIDTHS = {ABOVE_ZERO: 11, ZERO_OR_MORE: 11, LABEL: 26}  # characters
# The table takes the room the terminal leaves it, and never less than this.
MINIMUM_HEIGHT_PX = 120
NAMED_PROBLEMS = 5  # cells named in the sentence after Confirm; the others are counted
# the mouse wheel: <MouseWheel> on Windows and the Mac, buttons 4 (up) and 5 (down) on
# Linux
WHEEL_EVENTS = ('<MouseWheel>', '<Button-4>', '<Button-5>')
ERROR_BACKGROUND = '#6b2b33'
HEADING_TEXT = '#808080'
SKIPPED_BACKGROUND = '#252526'
SKIPPED_TEXT = '#5a5a5a'


# ---- AnswerTable ---------------------------------------------------------------------
class AnswerTable:
    """
    ---- Summary ----
    A table of the window, filled in by clicking a cell and typing: a fixed first
    column (the file, or the time of an event), then cells of three kinds (a number
    above 0, a number of 0 or more or nothing, a label), the rows grouped under the
    name of their file where the table says so. Tab moves across, Enter and the arrows
    move down and up, and Enter in the last row goes on to Confirm. A cell that cannot
    be used turns red; in a row whose label is the skip word the other cells are greyed
    out and not read. Entering a cell tells the window which file it belongs to. The
    table tells nothing else by itself: the program reads it when Confirm is pressed.
    Every method runs on the window thread, except problems_lister and values_reader.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the table, for the window to place.

    ---- Globals read ----
    CELL_WIDTHS, MINIMUM_HEIGHT_PX, ERROR_BACKGROUND, HEADING_TEXT, SKIPPED_BACKGROUND,
    SKIPPED_TEXT, LABEL.

    ---- Methods ----
    __init__
    _cell_checker
    _cell_mover
    _cell_revealer
    _focus_handler
    _problem_finder
    _row_skipper
    _size_follower
    _skip_checker
    _wheel_binder
    _wheel_scroller
    cell_focuser
    problems_lister
    rows_setter
    symbol_inserter
    values_reader
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 ttk: Any,
                 parent: Any,
                 font: Tuple[str, int],
                 colours: Dict[str, str],
                 on_finish: Callable[[], None],
                 on_file: Callable[[str], None],
                 ) -> None:
        """
        ---- Summary ----
        Method to build the empty table; rows_setter fills it.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        ttk : Any
            The tkinter.ttk module.
        parent : Any
            The widget the table is built in.
        font : Tuple[str, int]
            (family, size) of the text.
        colours : Dict[str, str]
            {'background', 'text', 'cell', 'edge'}: the colours of the table, its
            text, its cells and the edge of the cell being typed in.
        on_finish : Callable[[], None]
            Called when Enter is pressed in the last row.
        on_file : Callable[[str], None]
            Called with the name of the file a cell belongs to when the cell is
            entered.

        ---- Globals read ----
        MINIMUM_HEIGHT_PX.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_follower
        _wheel_binder
        """

        self._tk = tk
        self._font = font
        self._colours = colours
        self._on_finish = on_finish
        self._on_file = on_file
        self._columns: List[Tuple[str, str, str]] = []
        self._kinds: Dict[str, str] = {}
        self._skip_word: Optional[str] = None
        self._rows: List[dict] = []
        self._texts: List[Dict[str, str]] = []
        self._variables: List[Dict[str, Any]] = []
        self._cells: List[Dict[str, Any]] = []
        self._last_cell: Any = None
        self.frame = tk.Frame(parent, bg=colours['background'])
        self._canvas = tk.Canvas(self.frame,
                                 bg=colours['background'],
                                 highlightthickness=0,
                                 height=MINIMUM_HEIGHT_PX,
                                 )
        self._scroll = ttk.Scrollbar(self.frame, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll.set)
        self._scroll.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=6)
        self._inner = tk.Frame(self._canvas, bg=colours['background'])
        self._window = self._canvas.create_window((0, 0),
                                                  window=self._inner,
                                                  anchor='nw',
                                                  )
        self._inner.bind('<Configure>', self._size_follower)
        self._canvas.bind('<Configure>',
                          lambda e: self._canvas.itemconfigure(self._window,
                                                               width=e.width,
                                                               ),
                          )
        self._wheel_binder(self._canvas)

    # ---- TABLE HELPERS ---------------------------------------------------------------

    # ---- _cell_checker ---------------------------------------------------------------
    def _cell_checker(self, row: int, key: str) -> None:
        """
        ---- Summary ----
        Method to keep what was typed in one cell, to turn the cell red when it cannot
        be used, and, for a label, to grey out or bring back the other cells of its
        row as the label is or is not the skip word.

        ---- Inputs ----
        row : int
            Row of the cell, from 0.
        key : str
            Name of its value, such as 'OD' or 'label'.

        ---- Globals read ----
        ERROR_BACKGROUND, LABEL.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the text and colours the cell (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _row_skipper
        cell_reader
        """

        text = self._variables[row][key].get()
        self._texts[row][key] = text
        kind = self._kinds[key]
        _, is_valid = cell_reader(text, kind)
        self._cells[row][key].configure(
            bg=self._colours['cell'] if is_valid else ERROR_BACKGROUND,
            )
        if kind == LABEL and self._skip_word:
            self._row_skipper(row)

    # ---- _cell_mover -----------------------------------------------------------------
    def _cell_mover(self, row: int, key: str, step: int) -> str:
        """
        ---- Summary ----
        Method to move to the same cell of the row below or above, passing greyed-out
        cells. Past the last row the table is left, for Confirm.

        ---- Inputs ----
        row : int
            Row of the cell being typed in, from 0.
        key : str
            Name of its value.
        step : int
            +1 for the row below, -1 for the row above.

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            'break', so Tk does nothing more with the key.

        ---- Globals mutated ----
        None. Moves the typing cursor (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        target = row + step
        while (0 <= target < len(self._cells) and
               str(self._cells[target][key].cget('state')) == 'disabled'
               ):
            target += step
        if 0 <= target < len(self._cells):
            cell = self._cells[target][key]
            cell.focus_set()
            cell.selection_range(0, 'end')
            cell.icursor('end')
        elif target >= len(self._cells):
            self._on_finish()
        return 'break'

    # ---- _cell_revealer --------------------------------------------------------------
    def _cell_revealer(self, cell: Any) -> None:
        """
        ---- Summary ----
        Method to scroll a long table so the cell being typed in can be seen.

        ---- Inputs ----
        cell : Any
            The Tk entry of the cell that was entered.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Scrolls the table (side effect).

        ---- Equations ----
        The table is moved so the cell sits one row height under the top:
        share = (top of the cell - its height) / height of the whole table.

        ---- Helpers ----
        None.
        """

        total = self._inner.winfo_height()
        shown = self._canvas.winfo_height()
        if total <= shown:
            return
        top = self._canvas.canvasy(0)
        if cell.winfo_y() < top or cell.winfo_y() + cell.winfo_height() > top + shown:
            share = (cell.winfo_y() - cell.winfo_height()) / total
            self._canvas.yview_moveto(max(0.0, share))

    # ---- _focus_handler --------------------------------------------------------------
    def _focus_handler(self, row: int, key: str) -> None:
        """
        ---- Summary ----
        Method to follow the cell being typed in: it is remembered for the Symbols
        row, scrolled into sight, and its file is told to the window.

        ---- Inputs ----
        row : int
            Row of the cell, from 0.
        key : str
            Name of its value.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Scrolls the table and calls on_file (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _cell_revealer
        """

        self._last_cell = self._cells[row][key]
        self._cell_revealer(self._last_cell)
        self._on_file(self._rows[row]['file'])

    # ---- _problem_finder -------------------------------------------------------------
    def _problem_finder(self) -> List[Tuple[int, str, str]]:
        """
        ---- Summary ----
        Method to find the cells that hold something that cannot be used, and the
        needed cells left empty, in the order of the table. The greyed-out cells of a
        skipped row are not looked at.

        ---- Inputs ----
        None.

        ---- Globals read ----
        EMPTY, LABEL, NEEDED_KINDS.

        ---- Outputs ----
        List[Tuple[int, str, str]]
            (row, name of the value, problem) for each such cell; the problem is the
            kind of the cell when what it holds is wrong, or EMPTY.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        _skip_checker
        cell_reader
        """

        found = []
        for row, texts in enumerate(self._texts):
            is_skipped = self._skip_checker(row)
            for key, _, kind in self._columns:
                if is_skipped and kind != LABEL:
                    continue
                value, is_valid = cell_reader(texts[key], kind)
                if not is_valid:
                    found.append((row, key, kind))
                elif value is None and kind in NEEDED_KINDS:
                    found.append((row, key, EMPTY))
        return found

    # ---- _row_skipper ----------------------------------------------------------------
    def _row_skipper(self, row: int) -> None:
        """
        ---- Summary ----
        Method to grey out the cells of a row beside its label while the label is the
        skip word (an event left out), and to bring them back when it is not.

        ---- Inputs ----
        row : int
            Row, from 0.

        ---- Globals read ----
        LABEL.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the state of the cells (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _skip_checker
        """

        state = 'disabled' if self._skip_checker(row) else 'normal'
        for key, _, kind in self._columns:
            if kind != LABEL:
                self._cells[row][key].configure(state=state)

    # ---- _size_follower --------------------------------------------------------------
    def _size_follower(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to let the table scroll over all its rows when they change size.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the scrolled region (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._canvas.configure(scrollregion=(0,
                                             0,
                                             self._inner.winfo_reqwidth(),
                                             self._inner.winfo_reqheight(),
                                             ),
                               )

    # ---- _skip_checker ---------------------------------------------------------------
    def _skip_checker(self, row: int) -> bool:
        """
        ---- Summary ----
        Method to say whether a row is left out: its label is the skip word, in any
        capitals.

        ---- Inputs ----
        row : int
            Row, from 0.

        ---- Globals read ----
        LABEL.

        ---- Outputs ----
        bool
            True when the row is left out; always False for a table with no skip word.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._skip_word:
            return False
        return any(self._texts[row][key].strip().lower() == self._skip_word
                   for key, _, kind in self._columns
                   if kind == LABEL
                   )

    # ---- _wheel_binder ---------------------------------------------------------------
    def _wheel_binder(self, widget: Any) -> None:
        """
        ---- Summary ----
        Method to make the mouse wheel over a part of the table scroll it, on Windows,
        the Mac and Linux alike.

        ---- Inputs ----
        widget : Any
            The Tk widget (the table, a heading, a name or a cell).

        ---- Globals read ----
        WHEEL_EVENTS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Binds the wheel events of the widget (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _wheel_scroller
        """

        for event in WHEEL_EVENTS:
            widget.bind(event, self._wheel_scroller)

    # ---- _wheel_scroller -------------------------------------------------------------
    def _wheel_scroller(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to scroll a long table with the mouse wheel.

        ---- Inputs ----
        event : Any
            The Tk mouse wheel event, or the button 4 or 5 event of Linux.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Scrolls the table (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        wheel_step_finder
        """

        step = wheel_step_finder(event)
        if step and self._inner.winfo_height() > self._canvas.winfo_height():
            self._canvas.yview_scroll(step, 'units')

    # ---- TABLE FUNCTIONS -------------------------------------------------------------

    # ---- cell_focuser ----------------------------------------------------------------
    def cell_focuser(self) -> None:
        """
        ---- Summary ----
        Method to put the typing cursor in the first cell that still needs something,
        or else in the first cell, with what it holds selected so typing replaces it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Moves the typing cursor (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _problem_finder
        """

        if not self._cells:
            return
        problems = self._problem_finder()
        if problems:
            row, key = problems[0][0], problems[0][1]
        else:
            row, key = 0, self._columns[0][0]
        cell = self._cells[row][key]
        cell.focus_set()
        cell.selection_range(0, 'end')
        cell.icursor('end')

    # ---- problems_lister -------------------------------------------------------------
    def problems_lister(self) -> List[Tuple[str, str]]:
        """
        ---- Summary ----
        Method to list the cells that hold something that cannot be used and the needed
        cells left empty. It can be called from any thread.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[Tuple[str, str]]
            ('row name: column heading', problem) for each such cell, in the order of
            the table; the problem is the kind of the cell, or EMPTY. Empty when every
            cell can be used.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        _problem_finder
        """

        headings = {key: heading for key, heading, _ in self._columns}
        return [(f"{self._rows[row]['name']}: {headings[key]}", problem)
                for row, key, problem in self._problem_finder()
                ]

    # ---- rows_setter -----------------------------------------------------------------
    def rows_setter(self, table: dict) -> None:
        """
        ---- Summary ----
        Method to fill the table with its headings and rows, the rows of a file under
        its name where they are grouped.

        ---- Inputs ----
        table : dict
            The table to show (table_rows, DATA_FORMAT.md).

        ---- Globals read ----
        CELL_WIDTHS, HEADING_TEXT, LABEL, SKIPPED_BACKGROUND, SKIPPED_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Rebuilds the rows of the table (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _cell_checker
        _cell_mover
        _focus_handler
        _wheel_binder
        """

        # ---- 1 Clear the old rows ----------------------------------------------------
        tk = self._tk
        colours = self._colours
        for child in self._inner.winfo_children():
            child.destroy()
        self._columns = [tuple(column) for column in table['columns']]
        self._kinds = {key: kind for key, _, kind in self._columns}
        self._skip_word = table.get('skip_word')
        self._rows = [dict(row) for row in table['rows']]
        self._texts, self._variables, self._cells = [], [], []
        self._last_cell = None

        # ---- 2 The column widths and headings ----------------------------------------
        # A label column takes the spare width; without one, the first column does.
        has_label = LABEL in self._kinds.values()
        self._inner.columnconfigure(0, weight=0 if has_label else 1)
        for column, (_, _, kind) in enumerate(self._columns, start=1):
            self._inner.columnconfigure(column, weight=1 if kind == LABEL else 0)
        headings = [table['first_heading'],
                    ] + [heading for _, heading, _ in self._columns]
        for column, heading in enumerate(headings):
            label = tk.Label(self._inner,
                             text=heading,
                             bg=colours['background'],
                             fg=HEADING_TEXT,
                             font=(self._font[0], self._font[1] - 2),
                             anchor='w',
                             )
            label.grid(row=0, column=column, sticky='w', padx=(0, 6), pady=(0, 2))
            self._wheel_binder(label)

        # ---- 3 One row per file or event, under its file's name ----------------------
        place = 1
        group = None
        for row, entry in enumerate(self._rows):
            if entry.get('group') and entry['group'] != group:
                group = entry['group']
                label = tk.Label(self._inner,
                                 text=group,
                                 bg=colours['background'],
                                 fg=colours['text'],
                                 font=(self._font[0], self._font[1], 'bold'),
                                 anchor='w',
                                 )
                label.grid(row=place,
                           column=0,
                           columnspan=len(self._columns) + 1,
                           sticky='w',
                           pady=(6, 2),
                           )
                self._wheel_binder(label)
                place += 1
            label = tk.Label(self._inner,
                             text=entry['first'],
                             bg=colours['background'],
                             fg=HEADING_TEXT if entry.get('group') else colours['text'],
                             font=self._font,
                             anchor='e' if entry.get('group') else 'w',
                             )
            label.grid(row=place, column=0, sticky='ew', padx=(0, 6), pady=1)
            self._wheel_binder(label)
            texts, variables, cells = {}, {}, {}
            for column, (key, _, kind) in enumerate(self._columns, start=1):
                texts[key] = entry['cells'].get(key) or ''
                variables[key] = tk.StringVar(master=self._inner, value=texts[key])
                cell = tk.Entry(self._inner,
                                textvariable=variables[key],
                                width=CELL_WIDTHS[kind],
                                bg=colours['cell'],
                                fg=colours['text'],
                                disabledbackground=SKIPPED_BACKGROUND,
                                disabledforeground=SKIPPED_TEXT,
                                insertbackground=colours['text'],
                                font=self._font,
                                relief='flat',
                                highlightthickness=1,
                                highlightbackground='#3c3c3c',
                                highlightcolor=colours['edge'],
                                justify='left' if kind == LABEL else 'right',
                                )
                cell.grid(row=place,
                          column=column,
                          sticky='ew',
                          padx=(0, 6),
                          pady=1,
                          ipady=2,
                          )
                cell.bind('<Return>', lambda e, r=row, k=key: self._cell_mover(r, k, 1))
                cell.bind('<Down>', lambda e, r=row, k=key: self._cell_mover(r, k, 1))
                cell.bind('<Up>', lambda e, r=row, k=key: self._cell_mover(r, k, -1))
                cell.bind('<FocusIn>', lambda e, r=row, k=key: self._focus_handler(r, k))
                self._wheel_binder(cell)
                cells[key] = cell
            self._texts.append(texts)
            self._variables.append(variables)
            self._cells.append(cells)
            place += 1

        # ---- 4 Check each cell as it is typed in -------------------------------------
        for row, variables in enumerate(self._variables):
            for key, _, _ in self._columns:
                variables[key].trace_add('write',
                                         lambda *_, r=row, k=key: self._cell_checker(r,
                                                                                     k,
                                                                                     ),
                                         )
                self._cell_checker(row, key)
        self._canvas.yview_moveto(0.0)

    # ---- symbol_inserter -------------------------------------------------------------
    def symbol_inserter(self, symbol: str) -> None:
        """
        ---- Summary ----
        Method to type a symbol (µ, a superscript -1, ...) into the cell last typed in,
        at its cursor, in place of what is selected there.

        ---- Inputs ----
        symbol : str
            The characters to add.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the text of the cell (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        cell = self._last_cell
        if cell is None or str(cell.cget('state')) == 'disabled':
            return
        if cell.selection_present():
            cell.delete('sel.first', 'sel.last')
        cell.insert('insert', symbol)
        cell.focus_set()

    # ---- values_reader ---------------------------------------------------------------
    def values_reader(self) -> List[Dict[str, Any]]:
        """
        ---- Summary ----
        Method to give the values typed in the table, row by row. It can be called
        from any thread.

        ---- Inputs ----
        None.

        ---- Globals read ----
        LABEL.

        ---- Outputs ----
        List[Dict[str, Any]]
            One {name of the value: value} per row, in the order of the rows: a number
            or a label without its outer spaces; None for a cell that is empty, wrong,
            or greyed out in a skipped row.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        _skip_checker
        cell_reader
        """

        values = []
        for row, texts in enumerate(self._texts):
            is_skipped = self._skip_checker(row)
            values.append({key: (None
                                 if is_skipped and kind != LABEL
                                 else cell_reader(texts[key], kind)[0]
                                 )
                           for key, _, kind in self._columns
                           },
                          )
        return values


# ---- CELL HELPERS --------------------------------------------------------------------


# ---- _cell_name_joiner ---------------------------------------------------------------
def _cell_name_joiner(names: Sequence[str]) -> str:
    """
    ---- Summary ----
    Helper function to name cells in a sentence: the first few, then how many more.

    ---- Inputs ----
    names : Sequence[str]
        Names of the cells, at least one.

    ---- Globals read ----
    NAMED_PROBLEMS.

    ---- Outputs ----
    str
        For example 'a: OD, b: OD' or 'a: OD, ..., e: OD and 3 more'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    shown = ', '.join(names[:NAMED_PROBLEMS])
    extra = len(names) - NAMED_PROBLEMS
    return f'{shown} and {extra} more' if extra > 0 else shown


# ---- _number_writer ------------------------------------------------------------------
def _number_writer(value: Optional[float]) -> str:
    """
    ---- Summary ----
    Helper function to write a value in a cell: the number as short as it goes, or
    nothing.

    ---- Inputs ----
    value : Optional[float]
        The value, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '0.5' or ''.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return '' if value is None else f'{value:g}'


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- cell_reader ---------------------------------------------------------------------
def cell_reader(text: str, kind: str = ABOVE_ZERO) -> Tuple[Any, bool]:
    """
    ---- Summary ----
    Main function to read what was typed in one cell: a number (with a point or a comma
    as the decimal sign) above 0 or of 0 or more, as the kind asks, or a label; or
    nothing yet, which is never wrong here (a needed cell left empty is found when
    Confirm is pressed).

    ---- Inputs ----
    text : str
        What the cell holds.
    kind : str
        ABOVE_ZERO, ZERO_OR_MORE or LABEL.

    ---- Globals read ----
    ABOVE_ZERO, LABEL.

    ---- Outputs ----
    Tuple[Any, bool]
        (value, is_valid): (the number or the label without its outer spaces, True)
        when it can be used; (None, True) for an empty cell; (None, False) for a
        number that is not one, or is below its limit.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    typed_number_reader
    """

    if not text.strip():
        return None, True
    if kind == LABEL:
        return text.strip(), True
    value = typed_number_reader(text)
    if value is None or value < 0 or (kind == ABOVE_ZERO and value == 0):
        return None, False
    return value, True


# ---- label_entries_reader ------------------------------------------------------------
def label_entries_reader(table: dict,
                         values: List[Dict[str, Any]],
                         entries: Dict[str, List[dict]],
                         ) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Main function to take the labels and concentrations typed in the labels table back
    into the events of each file.

    ---- Inputs ----
    table : dict
        The labels table that was shown (label_table_builder, table_rows,
        DATA_FORMAT.md).
    values : List[Dict[str, Any]]
        What AnswerTable.values_reader gave for it, row by row.
    entries : Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]} the
        table was built from; not changed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, List[dict]]
        A copy of ``entries`` with each event's label and concentration_uM as typed;
        a label left empty keeps the one it had.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    result = {name: [dict(entry) for entry in events]
              for name, events in entries.items()
              }
    for row, found in zip(table['rows'], values):
        entry = result[row['file']][row['position']]
        entry['label'] = found.get('label') or entry['label']
        entry['concentration_uM'] = found.get('concentration_uM')
    return result


# ---- label_table_builder -------------------------------------------------------------
def label_table_builder(summaries: List[dict],
                        entries: Dict[str, List[dict]],
                        skip_word: str,
                        ) -> dict:
    """
    ---- Summary ----
    Main function to lay out the labels table: one row per event, with its time, label
    and concentration, under the name of its file; files without events have no rows.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md), in the order of the files.
    entries : Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}, one
        per event of the summary, in the same order.
    skip_word : str
        The label that leaves an event out; its row's concentration is greyed out.

    ---- Globals read ----
    LABEL_COLUMNS.

    ---- Outputs ----
    dict
        The table to show (table_rows, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_writer
    """

    rows = []
    for summary in summaries:
        name = summary['name']
        for position, (event, entry) in enumerate(zip(summary['events'],
                                                      entries.get(name, []),
                                                      ),
                                                  ):
            time = f"{event['time']:.2f}"
            rows.append({'file': name,
                         'position': position,
                         'group': name,
                         'first': time,
                         'name': f'{name} at {time} min',
                         'cells': {'label': entry['label'],
                                   'concentration_uM': _number_writer(
                                       entry['concentration_uM'],
                                       ),
                                   },
                         },
                        )
    return {'first_heading': 'Time (min)',
            'columns': LABEL_COLUMNS,
            'skip_word': skip_word,
            'rows': rows,
            }


# ---- od_rows_reader ------------------------------------------------------------------
def od_rows_reader(table: dict,
                   values: List[Dict[str, Any]],
                   ) -> Dict[str, Dict[str, Optional[float]]]:
    """
    ---- Summary ----
    Main function to take the values typed in the OD table back as the OD values of
    each file.

    ---- Inputs ----
    table : dict
        The OD table that was shown (od_table_builder, table_rows, DATA_FORMAT.md).
    values : List[Dict[str, Any]]
        What AnswerTable.values_reader gave for it, row by row.

    ---- Globals read ----
    OD_COLUMNS.

    ---- Outputs ----
    Dict[str, Dict[str, Optional[float]]]
        {file name: {'OD', 'volume', 'dilution_factor'}} in the order of the rows
        (od_rows, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {row['file']: {key: found.get(key) for key, _, _ in OD_COLUMNS}
            for row, found in zip(table['rows'], values)
            }


# ---- od_table_builder ----------------------------------------------------------------
def od_table_builder(rows: Dict[str, Dict[str, Optional[float]]]) -> dict:
    """
    ---- Summary ----
    Main function to lay out the OD table: one row per file, with its OD, volume and
    dilution.

    ---- Inputs ----
    rows : Dict[str, Dict[str, Optional[float]]]
        {file name: {'OD', 'volume', 'dilution_factor'}} in the order of the files; a
        value that is None or missing leaves its cell empty (od_rows, DATA_FORMAT.md).

    ---- Globals read ----
    OD_COLUMNS.

    ---- Outputs ----
    dict
        The table to show (table_rows, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_writer
    """

    return {'first_heading': 'File',
            'columns': OD_COLUMNS,
            'skip_word': None,
            'rows': [{'file': name,
                      'position': 0,
                      'group': None,
                      'first': name,
                      'name': name,
                      'cells': {key: _number_writer(values.get(key))
                                for key, _, _ in OD_COLUMNS
                                },
                      }
                     for name, values in rows.items()
                     ],
            }


# ---- table_problem_teller ------------------------------------------------------------
def table_problem_teller(problems: List[Tuple[str, str]]) -> Optional[str]:
    """
    ---- Summary ----
    Main function to say in one sentence what is still wrong in a table when Confirm is
    pressed: the cells that hold something that cannot be used first, then the needed
    cells left empty.

    ---- Inputs ----
    problems : List[Tuple[str, str]]
        What AnswerTable.problems_lister gave: (cell name, problem).

    ---- Globals read ----
    EMPTY, KIND_HINTS.

    ---- Outputs ----
    Optional[str]
        The sentence, or None when the table can be used.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _cell_name_joiner
    """

    wrong = [(name, problem) for name, problem in problems if problem != EMPTY]
    if wrong:
        hints = ' or '.join(dict.fromkeys(KIND_HINTS[problem] for _, problem in wrong))
        return (f'Type {hints} in these cells: '
                f'{_cell_name_joiner([name for name, _ in wrong])}.'
                )
    empty = [name for name, problem in problems if problem == EMPTY]
    if empty:
        return f'Fill in these empty cells: {_cell_name_joiner(empty)}.'
    return None


# ---- wheel_step_finder ---------------------------------------------------------------
def wheel_step_finder(event: Any) -> int:
    """
    ---- Summary ----
    Main function to say which way a turn of the mouse wheel scrolls, whichever system
    sent it: Windows and the Mac give a turn as a positive or negative amount, Linux as
    a press of button 4 (up) or 5 (down).

    ---- Inputs ----
    event : Any
        The Tk event, with ``num`` (the button) and ``delta`` (the amount turned).

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        -1 to scroll up, 1 to scroll down, 0 when the event says neither.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    button = getattr(event, 'num', None)
    if button in (4, 5):
        return -1 if button == 4 else 1
    delta = getattr(event, 'delta', 0) or 0
    if delta == 0:
        return 0
    return -1 if delta > 0 else 1
