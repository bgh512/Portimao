"""
The dataset set-up table in the window: one row per experiment in the plot area, with its groups, time point, replicate and the colour of its Group 1 label.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.dataset_setup import (COLOUR_KEY,
                                        column_filler,
                                        group_colours_filler,
                                        GROUP_COUNT,
                                        LABEL_COLUMNS,
                                        labels_lister,
                                        replicates_numberer,
                                        sets_lister,
                                        )
from utils_viewer.viewer_table import WHEEL_EVENTS, wheel_step_finder


# ---- CONSTANTS -----------------------------------------------------------------------
SETUP_HINT = ('Type a label in a cell, or pick one already used from its list; a cell '
              'may stay blank. To fill several rows, click a cell, then Shift-click '
              'another cell of the same column. Click the coloured square of a Group '
              '1 label to change its colour.')
USE_HEADING = 'Use'
FILE_HEADING = 'File'
REPLICATE_HEADING = 'Replicate'
NO_REPLICATE = '–'  # the replicate of a row not in use
SETS_HEADING = 'The sets as they stand: '
NO_SETS = 'No experiment is in use.'
SET_MARK = '■'
NOTE_COLOUR = '#404040'
HEADING_COLOUR = '#202020'
UNUSED_COLOUR = '#9a9a9a'
CELL_WIDTH = 22  # characters, of a cell of labels
NAME_WIDTH = 22  # characters, of the box of a group's name
SWATCH_WIDTH = 2  # characters
SETS_LINES = 3  # lines of text under the table
CELL_PAD_PX = 4
BREAK = 'break'  # what a Tk binding returns to stop the click or the wheel there


# ---- SetupTable ----------------------------------------------------------------------
class SetupTable:
    """
    ---- Summary ----
    The dataset set-up table while it is filled in: the names of the two group
    columns, one row per experiment (a tick for Use, the file, the colour and the
    label of Group 1, the labels of Group 2 and the time point, the replicate
    worked out by the program), the colours to pick from once a coloured square is
    clicked, and the sets as they stand under the table. It keeps what is typed as it
    is typed, so the program can read it once the step is answered. It runs on the
    window thread, except setup_reader; the window packs its frame.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the table, packed by the window in place of the file
        controls, the boxes and the plot.

    ---- Globals read ----
    The words, colour and size constants (module constants); settings.GROUP_COLOURS.

    ---- Methods ----
    __init__
    _cell_taker
    _colour_taker
    _fill_taker
    _focus_taker
    _name_taker
    _palette_opener
    _refresher
    _rows_builder
    _use_taker
    _wheel_binder
    _wheel_scroller
    closer
    opener
    setup_reader
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 ttk: Any,
                 right: Any,
                 fonts: Tuple[str, int],
                 background: str,
                 ) -> None:
        """
        ---- Summary ----
        Method to build the frame of the table with its parts, empty and not packed;
        opener fills it.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        ttk : Any
            The tkinter.ttk module.
        right : Any
            The right side of the window, which holds the plot area.
        fonts : Tuple[str, int]
            (family, size) of the guide's text.
        background : str
            The colour behind the plot area.

        ---- Globals read ----
        GROUP_COUNT, NAME_WIDTH, NOTE_COLOUR, SETS_LINES, SETUP_HINT, SWATCH_WIDTH;
        settings.GROUP_COLOURS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _colour_taker
        _name_taker
        _refresher
        _wheel_binder
        """

        # ---- 1 The state -------------------------------------------------------------
        self._tk, self._ttk = tk, ttk
        self._family, self._size = fonts
        self._background = background
        self._rows: List[dict] = []
        self._names: List[str] = [''] * GROUP_COUNT
        self._colours: Dict[str, str] = {}
        self._is_filling = False
        # the cell clicked last, which a Shift-click fills from: (column, row)
        self._anchor: Optional[Tuple[str, int]] = None
        self._palette_label: Optional[str] = None
        self._variables: List[Dict[str, Any]] = []
        self._widgets: List[Dict[str, Any]] = []
        self._headings: Dict[str, Any] = {}
        self.frame = tk.Frame(right, bg=background)

        # ---- 2 The names of the two group columns ------------------------------------
        names = tk.Frame(self.frame, bg=background)
        names.pack(side='top', anchor='w', padx=8, pady=(8, 0))
        self._name_variables = []
        for place in range(GROUP_COUNT):
            tk.Label(names,
                     text=f'Group {place + 1} is:',
                     bg=background,
                     ).pack(side='left', padx=(0, 4))
            variable = tk.StringVar()
            variable.trace_add('write', lambda *_, p=place: self._name_taker(p))
            ttk.Entry(names,
                      textvariable=variable,
                      width=NAME_WIDTH,
                      ).pack(side='left', padx=(0, 16))
            self._name_variables.append(variable)
        self._hint = tk.Label(self.frame,
                              text=SETUP_HINT,
                              bg=background,
                              fg=NOTE_COLOUR,
                              wraplength=900,
                              justify='left',
                              anchor='w',
                              )
        self._hint.pack(side='top', fill='x', padx=8, pady=(4, 0))

        # ---- 3 The colours to pick from, shown once a coloured square is clicked -----
        self._palette = tk.Frame(self.frame, bg=background)
        self._palette_words = tk.Label(self._palette, text='', bg=background)
        self._palette_words.pack(side='left', padx=(0, 6))
        for colour in settings.GROUP_COLOURS:
            tk.Button(self._palette,
                      bg=colour,
                      activebackground=colour,
                      width=SWATCH_WIDTH,
                      relief='raised',
                      command=lambda c=colour: self._colour_taker(c),
                      ).pack(side='left', padx=1)
        ttk.Button(self._palette,
                   text='Cancel',
                   command=lambda: self._colour_taker(None),
                   ).pack(side='left', padx=(8, 0))

        # ---- 4 The sets as they stand, under the table -------------------------------
        self._sets = tk.Text(self.frame,
                             height=SETS_LINES,
                             wrap='word',
                             bg=background,
                             relief='flat',
                             highlightthickness=0,
                             font=(self._family, self._size),
                             cursor='arrow',
                             state='disabled',
                             )
        self._sets.pack(side='bottom', fill='x', padx=8, pady=(0, 8))

        # ---- 5 The table, which scrolls ----------------------------------------------
        holder = tk.Frame(self.frame, bg=background)
        holder.pack(side='top', fill='both', expand=True, padx=8, pady=8)
        self._holder = holder
        self._canvas = tk.Canvas(holder, bg=background, highlightthickness=0)
        scroll = ttk.Scrollbar(holder, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True)
        self._inner = tk.Frame(self._canvas, bg=background)
        self._canvas.create_window((0, 0), window=self._inner, anchor='nw')
        self._inner.bind('<Configure>',
                         lambda e: self._canvas.configure(scrollregion=self._canvas.bbox('all'),
                                                          ),
                         )
        self._wheel_binder(self._canvas)
        self._wheel_binder(self._inner)

    # ---- SETUP HELPERS ---------------------------------------------------------------

    # ---- _cell_taker -----------------------------------------------------------------
    def _cell_taker(self, row: int, key: str) -> None:
        """
        ---- Summary ----
        Method to keep what is typed in a cell as it is typed, so setup_reader gives
        it even when the cell was never left. The rest of the table follows once the
        cell is left (_refresher).

        ---- Inputs ----
        row : int
            The row of the cell.
        key : str
            Its column, one of the keys of LABEL_COLUMNS.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the row kept (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._is_filling:
            self._rows[row][key] = self._variables[row][key].get().strip()

    # ---- _colour_taker ---------------------------------------------------------------
    def _colour_taker(self, colour: Optional[str]) -> None:
        """
        ---- Summary ----
        Method to give the Group 1 label whose coloured square was clicked the colour
        picked, on every row, and take the colours to pick from away again.

        ---- Inputs ----
        colour : Optional[str]
            The colour picked, as '#rrggbb'; None for Cancel.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the colours kept and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _refresher
        """

        if colour is not None and self._palette_label is not None:
            self._colours[self._palette_label] = colour
        self._palette_label = None
        self._palette.pack_forget()
        self._refresher()

    # ---- _fill_taker -----------------------------------------------------------------
    def _fill_taker(self, row: int, key: str) -> Optional[str]:
        """
        ---- Summary ----
        Method to take a Shift-click on a cell: every row from the cell clicked
        before it to this one gets the label of that cell, when both are in the same
        column. Otherwise the click is an ordinary one.

        ---- Inputs ----
        row : int
            The row of the cell Shift-clicked.
        key : str
            Its column, one of the keys of LABEL_COLUMNS.

        ---- Globals read ----
        BREAK.

        ---- Outputs ----
        Optional[str]
            'break' when the rows were filled, so the click does nothing else; None
            for an ordinary click.

        ---- Globals mutated ----
        None. Changes the rows kept and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _refresher
        column_filler
        """

        if self._anchor is None or self._anchor[0] != key or self._anchor[1] == row:
            return None
        # the cell clicked first may still hold a label not yet left
        self._cell_taker(self._anchor[1], key)
        self._rows = column_filler(self._rows, key, self._anchor[1], row)
        self._is_filling = True
        try:
            for place, filled in enumerate(self._rows):
                self._variables[place][key].set(filled[key])
        finally:
            self._is_filling = False
        self._refresher()
        return BREAK

    # ---- _focus_taker ----------------------------------------------------------------
    def _focus_taker(self, row: int, key: str) -> None:
        """
        Method to note the cell clicked or moved into, which a Shift-click on another
        cell of its column fills from. See _fill_taker.
        """

        self._anchor = (key, row)

    # ---- _name_taker -----------------------------------------------------------------
    def _name_taker(self, place: int) -> None:
        """
        ---- Summary ----
        Method to keep the name typed for a group column and show it in the heading
        of the column.

        ---- Inputs ----
        place : int
            0 for Group 1, 1 for Group 2.

        ---- Globals read ----
        LABEL_COLUMNS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the names kept and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        group_heading_writer
        """

        if self._is_filling:
            return
        self._names[place] = self._name_variables[place].get().strip()
        heading = self._headings.get(LABEL_COLUMNS[place][0])
        if heading is not None:
            heading.configure(text=group_heading_writer(place, self._names[place]))

    # ---- _palette_opener -------------------------------------------------------------
    def _palette_opener(self, row: int) -> None:
        """
        ---- Summary ----
        Method to show the colours to pick from for the Group 1 label of a row, above
        the table. A row not in use, or with no Group 1 label, has no colour.

        ---- Inputs ----
        row : int
            The row whose coloured square was clicked.

        ---- Globals read ----
        COLOUR_KEY.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _refresher
        """

        self._refresher()  # a label typed and not yet left has its colour
        label = self._rows[row][COLOUR_KEY]
        if not label or not self._rows[row]['use']:
            return
        self._palette_label = label
        self._palette_words.configure(text=f'Colour of {label}:')
        self._palette.pack(side='top',
                           anchor='w',
                           padx=8,
                           pady=(6, 0),
                           before=self._holder,
                           )

    # ---- _refresher ------------------------------------------------------------------
    def _refresher(self) -> None:
        """
        ---- Summary ----
        Method to bring the table in line with its cells once one was left or
        changed: the colour of each Group 1 label, the replicate numbers, the rows
        not in use greyed out, and the sets under the table.

        ---- Inputs ----
        None.

        ---- Globals read ----
        COLOUR_KEY, LABEL_COLUMNS, NO_REPLICATE, NO_SETS, SET_MARK, SETS_HEADING,
        UNUSED_COLOUR.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the colours kept and the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        group_colours_filler
        replicates_numberer
        sets_lister
        """

        # ---- 1 The colours and the replicates ----------------------------------------
        # a colour picked for a label stays when the label leaves the table, so
        # typing it again brings the colour back
        self._colours.update(group_colours_filler(self._rows, self._colours))
        numbers = replicates_numberer(self._rows)

        # ---- 2 Each row --------------------------------------------------------------
        for row, widgets, number in zip(self._rows, self._widgets, numbers):
            is_used = bool(row['use'])
            colour = self._colours.get(row[COLOUR_KEY]) if is_used else None
            widgets['swatch'].configure(bg=colour or self._background,
                                        relief='raised' if colour else 'flat',
                                        )
            widgets['file'].configure(fg='black' if is_used else UNUSED_COLOUR)
            widgets['replicate'].configure(text=NO_REPLICATE if number is None
                                           else str(number),
                                           )
            for key, _ in LABEL_COLUMNS:
                widgets[key].configure(state='normal' if is_used else 'disabled')

        # ---- 3 The sets under the table ----------------------------------------------
        sets = sets_lister(self._rows, self._colours)
        text = self._sets
        text.configure(state='normal')
        text.delete('1.0', 'end')
        text.insert('end', SETS_HEADING if sets else NO_SETS)
        for place, entry in enumerate(sets):
            tag = f'set{place}'
            text.tag_configure(tag, foreground=entry['colour'] or UNUSED_COLOUR)
            text.insert('end', f'{SET_MARK} ', tag)
            text.insert('end', f"{entry['name']} (n = {entry['n']})    ")
        text.configure(state='disabled')

    # ---- _rows_builder ---------------------------------------------------------------
    def _rows_builder(self) -> None:
        """
        ---- Summary ----
        Method to build the headings and one line of widgets per row of the table, in
        place of those of the table shown before.

        ---- Inputs ----
        None.

        ---- Globals read ----
        CELL_PAD_PX, CELL_WIDTH, FILE_HEADING, HEADING_COLOUR, LABEL_COLUMNS,
        REPLICATE_HEADING, SWATCH_WIDTH, USE_HEADING.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _cell_taker
        _fill_taker
        _focus_taker
        _palette_opener
        _refresher
        _use_taker
        _wheel_binder
        group_heading_writer
        labels_lister
        """

        tk, ttk, background = self._tk, self._ttk, self._background
        for widget in self._inner.winfo_children():
            widget.destroy()
        self._variables, self._widgets, self._headings = [], [], {}
        bold = (self._family, self._size, 'bold')

        # ---- 1 The headings ----------------------------------------------------------
        # columns: Use, File, the coloured square, the three columns of labels,
        # Replicate
        headings = [(0, None, USE_HEADING), (1, None, FILE_HEADING)]
        for place, (key, words) in enumerate(LABEL_COLUMNS):
            if place < len(self._names):
                words = group_heading_writer(place, self._names[place])
            headings.append((3 + place, key, words))
        headings.append((3 + len(LABEL_COLUMNS), None, REPLICATE_HEADING))
        for column, key, words in headings:
            label = tk.Label(self._inner,
                             text=words,
                             bg=background,
                             fg=HEADING_COLOUR,
                             font=bold,
                             anchor='w',
                             )
            label.grid(row=0, column=column, sticky='w', padx=CELL_PAD_PX, pady=(0, 4))
            self._wheel_binder(label)
            if key is not None:
                self._headings[key] = label

        # ---- 2 The rows --------------------------------------------------------------
        for place, row in enumerate(self._rows):
            line = place + 1
            use = tk.BooleanVar(value=bool(row['use']))
            variables: Dict[str, Any] = {'use': use}
            widgets: Dict[str, Any] = {}
            widgets['use'] = tk.Checkbutton(self._inner,
                                            variable=use,
                                            bg=background,
                                            activebackground=background,
                                            command=lambda p=place: self._use_taker(p),
                                            )
            widgets['use'].grid(row=line, column=0, padx=CELL_PAD_PX)
            widgets['file'] = tk.Label(self._inner,
                                       text=row['name'],
                                       bg=background,
                                       anchor='w',
                                       )
            widgets['file'].grid(row=line, column=1, sticky='w', padx=CELL_PAD_PX)
            widgets['swatch'] = tk.Label(self._inner,
                                         text='',
                                         width=SWATCH_WIDTH,
                                         bg=background,
                                         borderwidth=1,
                                         cursor='hand2',
                                         )
            widgets['swatch'].grid(row=line, column=2, padx=(CELL_PAD_PX, 0))
            widgets['swatch'].bind('<Button-1>',
                                   lambda e, p=place: self._palette_opener(p),
                                   )
            for offset, (key, _) in enumerate(LABEL_COLUMNS):
                variable = tk.StringVar(value=row[key])
                variable.trace_add('write',
                                   lambda *_, p=place, k=key: self._cell_taker(p, k),
                                   )
                box = ttk.Combobox(self._inner, textvariable=variable, width=CELL_WIDTH)
                # the labels already used in the column, read as the list opens
                box.configure(postcommand=lambda b=box, k=key: b.configure(values=labels_lister(self._rows, k),
                                                                           ))
                box.grid(row=line, column=3 + offset, padx=CELL_PAD_PX, pady=1)
                box.bind('<FocusIn>',
                         lambda e, p=place, k=key: self._focus_taker(p, k),
                         )
                box.bind('<Shift-Button-1>',
                         lambda e, p=place, k=key: self._fill_taker(p, k),
                         )
                for event in ('<<ComboboxSelected>>', '<FocusOut>', '<Return>'):
                    box.bind(event, lambda e: self._refresher())
                variables[key], widgets[key] = variable, box
            widgets['replicate'] = tk.Label(self._inner,
                                            text='',
                                            bg=background,
                                            anchor='w',
                                            )
            widgets['replicate'].grid(row=line,
                                      column=3 + len(LABEL_COLUMNS),
                                      sticky='w',
                                      padx=CELL_PAD_PX,
                                      )
            for widget in widgets.values():
                self._wheel_binder(widget)
            self._variables.append(variables)
            self._widgets.append(widgets)

    # ---- _use_taker ------------------------------------------------------------------
    def _use_taker(self, row: int) -> None:
        """
        Method to keep the tick of a row (whether its experiment is in the dataset
        figures) and bring the table in line. See _refresher.
        """

        self._rows[row]['use'] = bool(self._variables[row]['use'].get())
        self._refresher()

    # ---- _wheel_binder ---------------------------------------------------------------
    def _wheel_binder(self, widget: Any) -> None:
        """
        Method to have the mouse wheel over a widget scroll the table, and never
        change the label of a cell under the mouse. See _wheel_scroller.
        """

        for event in WHEEL_EVENTS:
            widget.bind(event, self._wheel_scroller)

    # ---- _wheel_scroller -------------------------------------------------------------
    def _wheel_scroller(self, event: Any) -> str:
        """
        ---- Summary ----
        Method to scroll the table with the mouse wheel, when it is taller than its
        room.

        ---- Inputs ----
        event : Any
            The Tk event of the wheel.

        ---- Globals read ----
        BREAK.

        ---- Outputs ----
        str
            'break', so the wheel does nothing else.

        ---- Globals mutated ----
        None. Scrolls the table (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        wheel_step_finder
        """

        if self._inner.winfo_height() > self._canvas.winfo_height():
            self._canvas.yview_scroll(wheel_step_finder(event), 'units')
        return BREAK

    # ---- PUBLIC METHODS --------------------------------------------------------------

    # ---- closer ----------------------------------------------------------------------
    def closer(self) -> None:
        """
        ---- Summary ----
        Method to end the filling in once the step is answered: the colours to pick
        from are taken away. What the table holds stays for setup_reader.

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
        None.
        """

        self._palette_label, self._anchor = None, None
        self._palette.pack_forget()

    # ---- opener ----------------------------------------------------------------------
    def opener(self, setup: dict) -> None:
        """
        ---- Summary ----
        Method to show a set-up table: its group names, its rows and its colours.

        ---- Inputs ----
        setup : dict
            The set-up table (dataset_setup, DATA_FORMAT.md).

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
        _refresher
        _rows_builder
        """

        self._rows = [dict(row) for row in setup['rows']]
        self._names = list(setup['group_names'])
        self._colours = dict(setup['colours'])
        self._anchor, self._palette_label = None, None
        self._palette.pack_forget()
        self._is_filling = True
        try:
            for variable, name in zip(self._name_variables, self._names):
                variable.set(name)
        finally:
            self._is_filling = False
        self._rows_builder()
        self._refresher()
        self._canvas.yview_moveto(0)

    # ---- setup_reader ----------------------------------------------------------------
    def setup_reader(self) -> dict:
        """
        ---- Summary ----
        Method to give the set-up table as filled in. It may be called from the
        question thread once the step is answered.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        dict
            The set-up table (dataset_setup, DATA_FORMAT.md), with a colour for
            every Group 1 label in it.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        group_colours_filler
        """

        rows = [dict(row) for row in self._rows]
        return {'group_names': list(self._names),
                'colours': group_colours_filler(rows, dict(self._colours)),
                'rows': rows,
                }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- group_heading_writer ------------------------------------------------------------
def group_heading_writer(place: int, name: str) -> str:
    """
    ---- Summary ----
    Main function to write the heading of a group column: its number, with the name
    the user gave it in brackets.

    ---- Inputs ----
    place : int
        0 for Group 1, 1 for Group 2.
    name : str
        The name typed for the column; '' or spaces for none.

    ---- Globals read ----
    LABEL_COLUMNS.

    ---- Outputs ----
    str
        'Group 1 (strain)', or 'Group 1' for a column left unnamed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    words = LABEL_COLUMNS[place][1]
    return f'{words} ({name.strip()})' if name.strip() else words
