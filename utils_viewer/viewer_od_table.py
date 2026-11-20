"""
The OD table of the window: one row per file with its OD, volume and dilution.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---- CONSTANTS -----------------------------------------------------------------------
# The cells of a row: (name of the value in the OD values of a file, column heading).
COLUMNS = (('OD', 'OD'),
           ('volume', 'Volume (mL)'),
           ('dilution_factor', 'Dilution'),
           )
CELL_WIDTH = 11  # characters
MAXIMUM_HEIGHT_PX = 300  # taller tables scroll
ERROR_BACKGROUND = '#6b2b33'
HEADING_TEXT = '#808080'


# ---- ODTable -------------------------------------------------------------------------
class ODTable:
    """
    ---- Summary ----
    The table for the OD values: one row per file with a cell each for the OD, the
    volume and the dilution. A cell is clicked and typed in; Tab moves across, Enter
    and the arrows move down and up. A cell that is not a number above 0 turns red.
    It tells nothing by itself: the program reads the table when the user says it is
    filled in. Every method runs on the window thread, except rows_reader and
    problems_lister.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the table, for the window to place.

    ---- Globals read ----
    COLUMNS, CELL_WIDTH, MAXIMUM_HEIGHT_PX, ERROR_BACKGROUND, HEADING_TEXT.

    ---- Methods ----
    __init__
    _cell_checker
    _cell_mover
    _cell_revealer
    _size_follower
    _wheel_scroller
    problems_lister
    rows_reader
    rows_setter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 ttk: Any,
                 parent: Any,
                 font: Tuple[str, int],
                 colours: Dict[str, str],
                 on_finish: Callable[[], None],
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

        ---- Globals read ----
        MAXIMUM_HEIGHT_PX.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _size_follower
        _wheel_scroller
        """

        self._tk = tk
        self._font = font
        self._colours = colours
        self._on_finish = on_finish
        self._names: List[str] = []
        self._texts: List[Dict[str, str]] = []
        self._variables: List[Dict[str, Any]] = []
        self._cells: List[Dict[str, Any]] = []
        self.frame = tk.Frame(parent, bg=colours['background'])
        self._canvas = tk.Canvas(self.frame,
                                 bg=colours['background'],
                                 highlightthickness=0,
                                 height=1,
                                 )
        self._scroll = ttk.Scrollbar(self.frame, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll.set)
        self._scroll.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=6)
        self._inner = tk.Frame(self._canvas, bg=colours['background'])
        self._inner.columnconfigure(0, weight=1)
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
        self._canvas.bind('<MouseWheel>', self._wheel_scroller)

    # ---- TABLE HELPERS ---------------------------------------------------------------

    # ---- _cell_checker ---------------------------------------------------------------
    def _cell_checker(self, row: int, key: str) -> None:
        """
        ---- Summary ----
        Method to keep what was typed in one cell and to turn the cell red when it
        is not a number above 0.

        ---- Inputs ----
        row : int
            Row of the cell, from 0.
        key : str
            Name of its value ('OD', 'volume' or 'dilution_factor').

        ---- Globals read ----
        ERROR_BACKGROUND.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the text and colours the cell (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        cell_reader
        """

        text = self._variables[row][key].get()
        self._texts[row][key] = text
        _, is_valid = cell_reader(text)
        self._cells[row][key].configure(
            bg=self._colours['cell'] if is_valid else ERROR_BACKGROUND,
            )

    # ---- _cell_mover -----------------------------------------------------------------
    def _cell_mover(self, row: int, key: str, step: int) -> str:
        """
        ---- Summary ----
        Method to move to the same cell of the row below or above. Past the last row
        the table is left, for the answer box.

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
        if 0 <= target < len(self._cells):
            cell = self._cells[target][key]
            cell.focus_set()
            cell.selection_range(0, 'end')
            cell.icursor('end')
        elif target >= len(self._cells):
            self._on_finish()
        return 'break'

    # ---- _cell_revealer --------------------------------------------------------------
    def _cell_revealer(self, row: int) -> None:
        """
        ---- Summary ----
        Method to scroll a long table so the row being typed in can be seen.

        ---- Inputs ----
        row : int
            Row of the cell that was entered, from 0.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Scrolls the table (side effect).

        ---- Equations ----
        The table is moved so the row sits one row height under the top:
        share = (top of the row - its height) / height of the whole table.

        ---- Helpers ----
        None.
        """

        cell = self._cells[row][COLUMNS[0][0]]
        total = self._inner.winfo_height()
        shown = self._canvas.winfo_height()
        if total <= shown:
            return
        top = self._canvas.canvasy(0)
        if cell.winfo_y() < top or cell.winfo_y() + cell.winfo_height() > top + shown:
            share = (cell.winfo_y() - cell.winfo_height()) / total
            self._canvas.yview_moveto(max(0.0, share))

    # ---- _size_follower --------------------------------------------------------------
    def _size_follower(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to give the table the height of its rows, up to the height at which
        it scrolls.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        MAXIMUM_HEIGHT_PX.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Resizes the table (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        needed = self._inner.winfo_reqheight()
        self._canvas.configure(
            scrollregion=(0, 0, self._inner.winfo_reqwidth(), needed),
            height=min(needed, MAXIMUM_HEIGHT_PX),
            )

    # ---- _wheel_scroller -------------------------------------------------------------
    def _wheel_scroller(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to scroll a long table with the mouse wheel.

        ---- Inputs ----
        event : Any
            The Tk mouse wheel event.

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
        None.
        """

        if self._inner.winfo_height() > self._canvas.winfo_height():
            self._canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

    # ---- TABLE FUNCTIONS -------------------------------------------------------------

    # ---- problems_lister -------------------------------------------------------------
    def problems_lister(self) -> List[str]:
        """
        ---- Summary ----
        Method to list the cells that hold something that is not a number above 0.
        It can be called from any thread.

        ---- Inputs ----
        None.

        ---- Globals read ----
        COLUMNS.

        ---- Outputs ----
        List[str]
            One 'file name: column heading' per wrong cell; empty when there is none.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        cell_reader
        """

        return [f'{name}: {heading}'
                for name, texts in zip(self._names, self._texts)
                for key, heading in COLUMNS
                if not cell_reader(texts[key])[1]
                ]

    # ---- rows_reader -----------------------------------------------------------------
    def rows_reader(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        ---- Summary ----
        Method to give the values typed in the table. It can be called from any
        thread.

        ---- Inputs ----
        None.

        ---- Globals read ----
        COLUMNS.

        ---- Outputs ----
        Dict[str, Dict[str, Optional[float]]]
            {file name: {'OD', 'volume', 'dilution_factor'}} in the order of the
            rows; None for a cell that is empty or wrong (DATA_FORMAT.md).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        cell_reader
        """

        return {name: {key: cell_reader(texts[key])[0] for key, _ in COLUMNS}
                for name, texts in zip(self._names, self._texts)
                }

    # ---- rows_setter -----------------------------------------------------------------
    def rows_setter(self, rows: Dict[str, Dict[str, Optional[float]]]) -> None:
        """
        ---- Summary ----
        Method to fill the table: one row per file, in the order given, with the
        values the program already has.

        ---- Inputs ----
        rows : Dict[str, Dict[str, Optional[float]]]
            {file name: {'OD', 'volume', 'dilution_factor'}}; a value that is None
            or missing leaves its cell empty (DATA_FORMAT.md).

        ---- Globals read ----
        COLUMNS, CELL_WIDTH, HEADING_TEXT.

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
        _cell_revealer
        _wheel_scroller
        """

        # ---- 1 Clear the old rows ----------------------------------------------------
        tk = self._tk
        colours = self._colours
        for child in self._inner.winfo_children():
            child.destroy()
        self._names = list(rows)
        self._texts, self._variables, self._cells = [], [], []

        # ---- 2 The headings ----------------------------------------------------------
        headings = ['File'] + [heading for _, heading in COLUMNS]
        for column, heading in enumerate(headings):
            label = tk.Label(self._inner,
                             text=heading,
                             bg=colours['background'],
                             fg=HEADING_TEXT,
                             font=(self._font[0], self._font[1] - 2),
                             anchor='w',
                             )
            label.grid(row=0, column=column, sticky='w', padx=(0, 6), pady=(0, 2))
            label.bind('<MouseWheel>', self._wheel_scroller)

        # ---- 3 One row per file ------------------------------------------------------
        for row, name in enumerate(self._names):
            label = tk.Label(self._inner,
                             text=name,
                             bg=colours['background'],
                             fg=colours['text'],
                             font=self._font,
                             anchor='w',
                             )
            label.grid(row=row + 1, column=0, sticky='ew', padx=(0, 6), pady=1)
            label.bind('<MouseWheel>', self._wheel_scroller)
            texts, variables, cells = {}, {}, {}
            for column, (key, _) in enumerate(COLUMNS, start=1):
                value = rows[name].get(key)
                texts[key] = '' if value is None else f'{value:g}'
                variables[key] = tk.StringVar(master=self._inner, value=texts[key])
                cell = tk.Entry(self._inner,
                                textvariable=variables[key],
                                width=CELL_WIDTH,
                                bg=colours['cell'],
                                fg=colours['text'],
                                insertbackground=colours['text'],
                                font=self._font,
                                relief='flat',
                                highlightthickness=1,
                                highlightbackground='#3c3c3c',
                                highlightcolor=colours['edge'],
                                )
                cell.grid(row=row + 1, column=column, padx=(0, 6), pady=1, ipady=2)
                cell.bind('<Return>', lambda e, r=row, k=key: self._cell_mover(r, k, 1))
                cell.bind('<Down>', lambda e, r=row, k=key: self._cell_mover(r, k, 1))
                cell.bind('<Up>', lambda e, r=row, k=key: self._cell_mover(r, k, -1))
                cell.bind('<FocusIn>', lambda e, r=row: self._cell_revealer(r))
                cell.bind('<MouseWheel>', self._wheel_scroller)
                cells[key] = cell
            self._texts.append(texts)
            self._variables.append(variables)
            self._cells.append(cells)
            for key, _ in COLUMNS:
                variables[key].trace_add('write',
                                         lambda *_, r=row, k=key: self._cell_checker(r,
                                                                                     k,
                                                                                     ),
                                         )
                self._cell_checker(row, key)
        self._canvas.yview_moveto(0.0)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- cell_reader ---------------------------------------------------------------------
def cell_reader(text: str) -> Tuple[Optional[float], bool]:
    """
    ---- Summary ----
    Main function to read what was typed in one cell of the OD table: a number above
    0, with a point or a comma as the decimal sign, or nothing yet.

    ---- Inputs ----
    text : str
        What the cell holds.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Optional[float], bool]
        (value, is_valid): (the number, True) for a number above 0; (None, True) for
        an empty cell; (None, False) for anything else.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    cleaned = text.strip().replace(',', '.')
    if not cleaned:
        return None, True
    try:
        value = float(cleaned)
    except ValueError:
        return None, False
    if not 0 < value < float('inf'):
        return None, False
    return value, True
