"""
The guide on the left of the window: the steps under their stage names, the step open and the answer buttons.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.questions import path_cleaner


# ---- CONSTANTS -----------------------------------------------------------------------
# The stages, in order, and the steps of each: (key, stage, name, help). The program
# says which step starts with guide_step_starter(key); the help is shown when the step
# is opened again after it was done.
GUIDE_STEPS: Tuple[Tuple[str, str, str, str], ...] = (
    (
        'data_folder',
        'Import',
        'Data folder',
        'The folder of .paf files is chosen when Portimao opens: to use another, close '
        'Portimao and open it again.',
        ),
    (
        'previous',
        'Import',
        'Previous settings',
        'The settings of an earlier run are loaded, or not, when Portimao opens: to '
        'choose again, close Portimao and open it again.',
        ),
    ('run_name',
     'Import',
     'Save as',
     'The name of this run is typed when Portimao opens; its results are in the '
     'folder of that name, in the export folder of the data folder. To use another, '
     'close Portimao and open it again.',
     ),
    ('trim',
     'Import',
     'Trim and ignore',
     'Drag the bars on the plot, or type the times under "Trim / Ignore" in the Time '
     'regions box above it. Click EXPORT full + trimmed CSV or EXPORT trimmed CSV to '
     'write the csv files with the bars as they are.',
     ),
    (
        'temperature',
        'Set-up',
        'Temperature',
        'The temperature of the runs was typed here. It can also be changed in the Δψ box, '
        'under "More options".',
        ),
    ('od_scaling',
     'Set-up',
     'OD values or not',
     'Whether OD values are given was chosen here. Click "Edit ODs" in the View box '
     'to give them at any time.',
     ),
    ('od_values',
     'Set-up',
     'OD values',
     'The OD, volume and dilution of each file were typed here. Click "Edit ODs" in '
     'the View box to change them.',
     ),
    ('ocr_view',
     'Set-up',
     'OCR view',
     'The OCR was set to per OD here. Change it under "OCR as" in the View '
     'box.',
     ),
    ('labels',
     'Set-up',
     'Event labels',
     'The event labels were typed here. Click "Edit labels" in the View box to '
     'change them.',
     ),
    ('haems',
     'Experiment processing',
     'Haems',
     'Change the spectra, the scatter, the fit and the haems shown in the Haem '
     'decomposition box above the plot: the plot is redrawn after each change. To '
     'compare two, click "Keep to compare" first. Press CONTINUE when ready.',
     ),
    ('regions',
     'Experiment processing',
     'Oxidised and reduced',
     'Pull the oxidised and reduced regions out on the plot, or type them under "Ox / '
     'Red" in the Time regions box above it.',
     ),
    ('delta_psi',
     'Experiment processing',
     'Δψ',
     'Tick "Δψ" in its box above the plot to work it out, and change its numbers there: '
     'the Δψ panel is redrawn at once.',
     ),
    ('windows',
     'Experiment processing',
     'Averaging regions',
     'Drag the averaging regions on the plot, or type them under "Averaging" in the Time '
     'regions box above it.',
     ),
    ('figure',
     'Experiment export',
     'Finalise figures',
     'Use the arrows to change the order of the panels, and the Figure box above the '
     "plot to set the figure to a journal's standard: the figure of each file is "
     'redrawn at its size.',
     ),
    ('export',
     'Experiment export',
     'Export',
     'The plot and the workbook of each file were written here, with the spectra as '
     'csv files when you chose them.',
     ),
    ('setup',
     'Dataset figures',
     'Dataset set-up',
     'Which experiment is which was filled in here: its groups, its time point and '
     'whether it is used in the dataset figures.',
     ),
    ('page',
     'Dataset figures',
     'Build a figure',
     'The page of the dataset figure was built here: drag across the grid to place a '
     'plot, ✎ to change one and ✕ to remove it.',
     ),
    ('start', 'Dataset export', 'Summary and start', 'The summary of your answers is shown here, before the run starts.'),
    )
GUIDE_STAGES = tuple(dict.fromkeys(stage for _, stage, _, _ in GUIDE_STEPS))
GUIDE_KEYS = tuple(key for key, _, _, _ in GUIDE_STEPS)
# The step a change in the boxes above the plot belongs to, by the name of the value
# changed; a value not listed (how the haems, the OCR and the labels are shown, the
# order of the panels) belongs to every step, and opens none. The Time regions box
# belongs to the step of the tab pressed (TAB_STEPS).
TIME_TAB_CHANGE = 'time_tab'
# The tick of the Δψ box: ticked it opens the Δψ step, unticked none.
PSI_TICK_CHANGE = 'delta_psi'
TAB_STEPS = {'trim': 'trim', 'regions': 'regions', 'windows': 'windows'}
CHANGE_STEPS = {'edit_ods': 'od_values',
                'edit_labels': 'labels',
                'plot_haems': 'haems',
                'fit_file': 'haems',
                'haem_background': 'haems',
                'haem_files': 'haems',
                'compare': 'haems',
                'kept': 'haems',
                'spectra': 'haems',
                'go_back': 'haems',
                'save_fit': 'haems',
                'do_pca': 'haems',
                'delta_psi': 'delta_psi',
                'psi_bH_mV': 'delta_psi',
                'psi_bL_mV': 'delta_psi',
                'psi_fall_mV': 'delta_psi',
                'psi_share': 'delta_psi',
                'temperature_c': 'delta_psi',
                'psi_lowest_percent': 'delta_psi',
                'psi_highest_percent': 'delta_psi',
                'journal': 'figure',
                'columns': 'figure',
                'height': 'figure',
                'export_master': 'figure',
                }
# The buttons a step keeps when it is opened again from a later one: (what a click is
# told as, its words). A click is told as {change: True}, as a change in the boxes is.
# The trim step's two export buttons write the spectra of the trimmed data as csv files,
# or those and the whole recording's of each trimmed file.
EXPORT_FULL_TEXT = 'EXPORT full + trimmed CSV'
EXPORT_FULL_CHANGE = 'export_full'
EXPORT_TRIMMED_TEXT = 'EXPORT trimmed CSV'
EXPORT_TRIMMED_CHANGE = 'export_trimmed'
EXPORT_BUTTONS = ((EXPORT_FULL_CHANGE, EXPORT_FULL_TEXT),
                  (EXPORT_TRIMMED_CHANGE, EXPORT_TRIMMED_TEXT),
                  )
STEP_EXTRAS = {'trim': EXPORT_BUTTONS}
MARKS = {'open': '▸', 'here': '→', 'done': '✓', 'skipped': ' ', 'later': ' '}
HERE_TAG = 'you were here'
# beside a step passed without being asked, so the numbers do not seem to jump
SKIPPED_TAG = 'not needed this run'
GUIDE_BACKGROUND = '#1e1e1e'
CARD_BACKGROUND = '#252526'
CARD_EDGE = '#3c6e9f'
# The four levels of the guide: the stage (largest), the step, then in the card the
# explanations and the question (the window sizes those two). Points added to the
# size of the messages.
STAGE_OPEN_POINTS = 7
STAGE_SHUT_POINTS = 4
STEP_POINTS = 2
STAGE_OPEN_COLOUR = '#ffffff'
LINE_COLOURS = {'stage': '#9a9a9a',
                'open': '#ffffff',
                'here': '#9cdcfe',
                'done': '#c0c0c0',
                'skipped': '#6a6a6a',
                'later': '#8c8c8c',
                }
OPEN_BACKGROUND = '#2a3a4c'
MAIN_BACKGROUND = '#264f78'
MAIN_HOVER = '#2f6396'
OTHER_BACKGROUND = '#2d2d30'
OTHER_HOVER = '#3e3e42'
OFF_TEXT = '#707070'
BUTTON_TEXT = '#ffffff'
FOCUS_COLOUR = '#9cdcfe'
# a list of choices longer than this is laid out in two columns
ONE_COLUMN_MOST = 6
TICKED = '☑'
UNTICKED = '☐'
# The folder buttons: the one highlighted is what CONTINUE gives.
PICKED_BACKGROUND = '#1b3a57'
PICKED_MARK = '●'
UNPICKED_MARK = '○'
OTHER_FOLDER_TEXT = 'Other folder…'
BROWSE_TEXT = 'BROWSE…'


# ---- GuideState ----------------------------------------------------------------------
class GuideState:
    """
    ---- Summary ----
    Where the guide is: the step the program waits at, the step open in the guide (an
    earlier one, after a change in the strip that belongs to it or a click on its line)
    and the steps asked so far. It holds no window, so it can be tested without one.

    ---- Attributes ----
    current : Optional[int]
        Index in GUIDE_STEPS of the step the program waits at; None before the first.
    shown : Optional[int]
        Index of the step open in the guide.
    reached : int
        Index of the furthest step asked (-1 before the first).
    asked : Set[int]
        Indexes of the steps asked so far.

    ---- Globals read ----
    GUIDE_STEPS, GUIDE_KEYS, GUIDE_STAGES, CHANGE_STEPS, MARKS, HERE_TAG.

    ---- Methods ----
    __init__
    back_taker
    card_teller
    change_opener
    is_back
    line_opener
    row_lister
    step_starter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self) -> None:
        """
        ---- Summary ----
        Method to start before the first step.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the attributes on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.current: Optional[int] = None
        self.shown: Optional[int] = None
        self.reached = -1
        self.asked: Set[int] = set()

    # ---- back_taker ------------------------------------------------------------------
    def back_taker(self) -> None:
        """
        ---- Summary ----
        Method to open the step the program waits at again ("Back to <step>").

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the step shown.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.shown = self.current

    # ---- card_teller -----------------------------------------------------------------
    def card_teller(self) -> Dict[str, Any]:
        """
        ---- Summary ----
        Method to give what the open step says above its messages when it is an
        earlier step: the step's help, the words of the button that goes back (which
        names the step waited at) and the step's own buttons (the two export buttons
        of the trim step), if it has any.

        ---- Inputs ----
        None.

        ---- Globals read ----
        GUIDE_STEPS, STEP_EXTRAS.

        ---- Outputs ----
        Dict[str, Any]
            {'help', 'back': str, 'extra': tuple of (change, words)}; each
            empty while the step open is the one the program waits at, and 'extra'
            empty for a step without buttons of its own.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        is_back
        """

        if not self.is_back():
            return {'help': '', 'back': '', 'extra': ()}
        key, _, _, help_text = GUIDE_STEPS[self.shown]
        _, _, here, _ = GUIDE_STEPS[self.current]
        return {'help': help_text,
                'back': f'Back to {here}',
                'extra': STEP_EXTRAS.get(key, ()),
                }

    # ---- change_opener ---------------------------------------------------------------
    def change_opener(self, changes: Dict[str, Any]) -> bool:
        """
        ---- Summary ----
        Method to open the earlier step that a change in the boxes above the plot
        belongs to (the fit while at Δψ opens the haems). A change that belongs to a
        later step ticks that step, as done out of order; one that belongs to the step
        the program waits at opens that step again when an earlier one is open (the
        Averaging tab pressed while Δψ is open), and one that belongs to no step opens
        nothing.

        ---- Inputs ----
        changes : Dict[str, Any]
            {name: new value} of the strip values that changed.

        ---- Globals read ----
        GUIDE_KEYS.

        ---- Outputs ----
        bool
            True when the guide changed: another step opened, or a later one ticked.

        ---- Globals mutated ----
        None. Changes the step shown and the steps done.

        ---- Equations ----
        None.

        ---- Helpers ----
        step_of_change_finder
        """

        key = step_of_change_finder(changes)
        if key is None or self.current is None:
            return False
        index = GUIDE_KEYS.index(key)
        if index > self.current:
            is_new = index not in self.asked
            self.asked.add(index)
            return is_new
        if index == self.current and self.shown != self.current:
            # back to the step waited at (the Averaging tab pressed while Δψ is open),
            # so its own text shows again
            self.shown = index
            return True
        if index == self.current or index not in self.asked or index == self.shown:
            return False
        self.shown = index
        return True

    # ---- is_back ---------------------------------------------------------------------
    def is_back(self) -> bool:
        """
        ---- Summary ----
        Method to say whether the step open is an earlier one than the step the program
        waits at.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True while an earlier step is open.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self.shown is not None and self.shown != self.current

    # ---- line_opener -----------------------------------------------------------------
    def line_opener(self, index: int) -> bool:
        """
        ---- Summary ----
        Method to open a step whose line was clicked: one already asked, or the one the
        program waits at. A step not asked yet stays shut.

        ---- Inputs ----
        index : int
            Index in GUIDE_STEPS of the line clicked.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when the step open changed.

        ---- Globals mutated ----
        None. Changes the step shown.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if index not in self.asked or index == self.shown:
            return False
        self.shown = index
        return True

    # ---- row_lister ------------------------------------------------------------------
    def row_lister(self) -> List[Dict[str, Any]]:
        """
        ---- Summary ----
        Method to list the lines of the guide, top first: every stage name, and under
        the stage of the step open (and that of the step the program waits at) one line
        per step. The other stages show their name only, with the numbers of their
        steps, so the open step keeps the room.

        ---- Inputs ----
        None.

        ---- Globals read ----
        GUIDE_STAGES, GUIDE_STEPS, HERE_TAG, MARKS, SKIPPED_TAG.

        ---- Outputs ----
        List[Dict[str, Any]]
            One dict per line: {'kind': 'stage', 'text', 'status', 'is_open'} with
            status 'stage' and is_open True for a stage that lists its steps, or
            {'kind': 'step', 'index', 'text', 'status', 'mark', 'tag'} with status
            'open' (the card is under it), 'here' (the program waits there while an
            earlier step is open; tag HERE_TAG), 'done', 'skipped' (passed without
            being asked; tag SKIPPED_TAG) or 'later'.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        open_stages = {GUIDE_STEPS[i][1]
                       for i in (self.shown, self.current)
                       if i is not None
                       }
        rows: List[Dict[str, Any]] = []
        for stage in GUIDE_STAGES:
            indexes = [i
                       for i, (_, step_stage, _, _) in enumerate(GUIDE_STEPS)
                       if step_stage == stage
                       ]
            if stage in open_stages:
                rows.append({'kind': 'stage',
                             'text': stage,
                             'status': 'stage',
                             'is_open': True,
                             },
                            )
            else:
                is_done = indexes[-1] <= self.reached
                numbers = (f'step {indexes[0] + 1}'
                           if len(indexes) == 1
                           else f'steps {indexes[0] + 1}–{indexes[-1] + 1}'
                           )
                rows.append({'kind': 'stage',
                             'text': (f"{stage}  ·  {numbers}"
                                      f"{'  ✓' if is_done else ''}"
                                      ),
                             'status': 'stage',
                             'is_open': False,
                             },
                            )
                continue
            for i in indexes:
                if i == self.shown:
                    status = 'open'
                elif i == self.current:
                    status = 'here'
                elif i in self.asked:
                    status = 'done'
                elif i < self.reached:
                    status = 'skipped'
                else:
                    status = 'later'
                rows.append({'kind': 'step',
                             'index': i,
                             'text': f'{i + 1:>2}  {GUIDE_STEPS[i][2]}',
                             'status': status,
                             'mark': MARKS[status],
                             'tag': {'here': HERE_TAG,
                                     'skipped': SKIPPED_TAG,
                                     }.get(status, ''),
                             },
                            )
        return rows

    # ---- step_starter ----------------------------------------------------------------
    def step_starter(self, key: str) -> None:
        """
        ---- Summary ----
        Method to take the step the program has started: it becomes the step open and
        the one waited at, also when the program asks an earlier step again (going
        back), and the furthest step reached is kept.

        ---- Inputs ----
        key : str
            Key of the step, one of GUIDE_KEYS.

        ---- Globals read ----
        GUIDE_KEYS.

        ---- Outputs ----
        None
            Nothing. Raises ValueError for a key that is not a step.

        ---- Globals mutated ----
        None. Changes the attributes.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if key not in GUIDE_KEYS:
            raise ValueError(f"'{key}' is not a step of the guide.")
        index = GUIDE_KEYS.index(key)
        self.current = self.shown = index
        self.reached = max(self.reached, index)
        self.asked.add(index)


# ---- GuidePanel ----------------------------------------------------------------------
class GuidePanel:
    """
    ---- Summary ----
    The guide on the left of the window: one line per stage and per step, with the
    card of the open step (its messages, its question and its answers) under the line
    of that step. The card is built by the window; this class places it. Every method
    runs on the window thread.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the guide, for the window to place.
    card : Any
        The Tk frame of the open step, for the window to fill.

    ---- Globals read ----
    CARD_BACKGROUND, CARD_EDGE, GUIDE_BACKGROUND, HERE_TAG, LINE_COLOURS,
    OPEN_BACKGROUND, STAGE_OPEN_COLOUR, STAGE_OPEN_POINTS, STAGE_SHUT_POINTS,
    STEP_POINTS.

    ---- Methods ----
    __init__
    rows_drawer
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 parent: Any,
                 family: str,
                 size: int,
                 on_line: Callable[[int], None],
                 stage_family: Optional[str] = None,
                 ) -> None:
        """
        ---- Summary ----
        Method to build the empty guide and its card.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        parent : Any
            The frame of the left side of the window.
        family : str
            Font family of the window.
        size : int
            Font size of the messages (points).
        stage_family : Optional[str]
            Font family of the stage names (a plain one); None for the window's.
        on_line : Callable[[int], None]
            Called with the index of a step whose line is clicked.

        ---- Globals read ----
        CARD_BACKGROUND, CARD_EDGE, GUIDE_BACKGROUND.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._tk = tk
        self._family = family
        self._stage_family = stage_family or family
        self._size = size
        self._on_line = on_line
        self._lines: List[Any] = []
        self.frame = tk.Frame(parent, bg=GUIDE_BACKGROUND)
        self.card = tk.Frame(self.frame,
                             bg=CARD_BACKGROUND,
                             highlightthickness=1,
                             highlightbackground=CARD_EDGE,
                             )

    # ---- rows_drawer -----------------------------------------------------------------
    def rows_drawer(self, rows: List[Dict[str, Any]]) -> None:
        """
        ---- Summary ----
        Method to draw the lines of the guide again, with the card under the line of
        the open step (at the bottom before the first step): the stage that lists its
        steps large and bold, the other stages a little smaller and paler, the steps
        under it larger than the messages. A step already asked can be clicked to open
        it.

        ---- Inputs ----
        rows : List[Dict[str, Any]]
            The lines, as GuideState.row_lister gives them.

        ---- Globals read ----
        GUIDE_BACKGROUND, HERE_TAG, LINE_COLOURS, OPEN_BACKGROUND, STAGE_OPEN_COLOUR,
        STAGE_OPEN_POINTS, STAGE_SHUT_POINTS, STEP_POINTS.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the line widgets and places the card (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        tk = self._tk
        for line in self._lines:
            line.destroy()
        self._lines = []
        self.card.pack_forget()
        is_card_placed = False
        for row in rows:
            status = row['status']
            if row['kind'] == 'stage':
                is_open = row.get('is_open', False)
                line = tk.Label(
                    self.frame,
                    text=row['text'],
                    bg=GUIDE_BACKGROUND,
                    fg=STAGE_OPEN_COLOUR if is_open else LINE_COLOURS['stage'],
                    font=(self._stage_family,
                          self._size + (STAGE_OPEN_POINTS
                                        if is_open
                                        else STAGE_SHUT_POINTS
                                        ),
                          'bold',
                          ),
                    anchor='w',
                    )
                line.pack(side='top', fill='x', padx=12, pady=(10, 2))
                self._lines.append(line)
                continue
            text = f"{row['mark']} {row['text']}"
            if row['tag'] == HERE_TAG:
                text += f"   ← {row['tag']}"
            elif row['tag']:
                text += f"   · {row['tag']}"
            is_clickable = status in ('done', 'here')
            line = tk.Label(
                self.frame,
                text=text,
                bg=OPEN_BACKGROUND if status == 'open' else GUIDE_BACKGROUND,
                fg=LINE_COLOURS[status],
                font=(self._family,
                      self._size + STEP_POINTS,
                      'bold' if status in ('open', 'here') else 'normal',
                      ),
                pady=2,
                anchor='w',
                padx=6,
                cursor='hand2' if is_clickable else '',
                )
            line.pack(side='top', fill='x', padx=10)
            if is_clickable:
                line.bind('<Button-1>', lambda e, i=row['index']: self._on_line(i))
            self._lines.append(line)
            if status == 'open':
                self.card.pack(side='top',
                               fill='both',
                               expand=True,
                               padx=(22, 10),
                               pady=(2, 6),
                               )
                is_card_placed = True
        if not is_card_placed:
            self.card.pack(side='top', fill='both', expand=True, padx=10, pady=(6, 6))


# ---- AnswerArea ----------------------------------------------------------------------
class AnswerArea:
    """
    ---- Summary ----
    The answers of the question waiting, under its card: one big CONTINUE button for
    something done on the plot or in the strip; Yes and No one above the other; a
    button for each choice; tick buttons and CONTINUE for several choices; a box with
    CONTINUE only for a number or a name to type; folder buttons, Other folder… with a
    box for a full path and Browse…, and CONTINUE for a folder; Confirm for a table;
    or, while an earlier step is open, the button back to the step waited at. The
    answer the program gives with Enter is the highlighted button, which holds the
    keyboard. Every method runs on the window thread.

    ---- Attributes ----
    frame : Any
        The Tk frame holding the answers, for the window to place.
    entry : Any
        The typing box, shown for a number, a name or a folder typed in full.
    confirm : Any
        The Confirm button of a table.

    ---- Globals read ----
    BROWSE_TEXT, BUTTON_TEXT, FOCUS_COLOUR, MAIN_BACKGROUND, MAIN_HOVER, OFF_TEXT,
    ONE_COLUMN_MOST, OTHER_BACKGROUND, OTHER_FOLDER_TEXT, OTHER_HOVER,
    PICKED_BACKGROUND, TICKED, UNTICKED.

    ---- Methods ----
    __init__
    _button_maker
    _choices_placer
    _clearer
    _folder_browser
    _folder_picker
    _folder_sender
    _folder_shower
    _multi_sender
    _ticker
    back_shower
    focuser
    request_shower
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 parent: Any,
                 family: str,
                 size: int,
                 colours: Dict[str, str],
                 on_click: Callable[[str, str], None],
                 on_typed: Callable[[], None],
                 on_confirm: Callable[[], Any],
                 ) -> None:
        """
        ---- Summary ----
        Method to build the empty area, its typing box and its Confirm button.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        parent : Any
            The frame the area sits in.
        family : str
            Font family of the window.
        size : int
            Font size of the messages (points).
        colours : Dict[str, str]
            {'background', 'text', 'cell'}: the card, its text and the typing box.
        on_click : Callable[[str, str], None]
            Called with (answer, words shown) when a button gives the answer.
        on_typed : Callable[[], None]
            Called when the answer typed in the box is sent (CONTINUE or Enter).
        on_confirm : Callable[[], Any]
            Called when Confirm is clicked.

        ---- Globals read ----
        FOCUS_COLOUR, MAIN_BACKGROUND.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets.

        ---- Equations ----
        None.

        ---- Helpers ----
        _button_maker
        """

        self._tk = tk
        self._family = family
        self._size = size
        self._colours = colours
        self._on_click = on_click
        self._on_typed = on_typed
        self._widgets: List[Any] = []
        self._ticked: List[int] = []
        self._ticks: List[Any] = []
        self._multi_go: Any = None
        # the folder buttons: (button, answer, name, note); -1 picks Other folder…
        self._folders: List[Tuple[Any, str, str, str]] = []
        self._other: Any = None
        self._path_row: Any = None
        self._picked = 0
        self.frame = tk.Frame(parent, bg=colours['background'])
        self.entry = tk.Entry(self.frame,
                              bg=colours['cell'],
                              fg=colours['text'],
                              insertbackground=colours['text'],
                              font=(family, size + 1),
                              relief='flat',
                              highlightthickness=1,
                              highlightbackground='#3c3c3c',
                              highlightcolor=FOCUS_COLOUR,
                              )
        self.confirm = self._button_maker('CONFIRM',lambda: on_confirm(), True)

    # ---- _button_maker ---------------------------------------------------------------
    def _button_maker(self,
                      text: str,
                      command: Callable[[], Any],
                      is_main: bool,
                      ) -> Any:
        """
        ---- Summary ----
        Helper method to make one answer button: a label rather than a button, so it
        looks the same on Windows, the Mac and Linux. A click, or the space bar on it,
        carries out the command; Enter does not, as it belongs to the boxes that are
        typed in and to the dialogs.

        ---- Inputs ----
        text : str
            The words on the button.
        command : Callable[[], Any]
            What a click does.
        is_main : bool
            True for a button that gives an answer (blue, its words in the middle);
            False for a row that is only picked or ticked (a folder, a tick, BROWSE…).

        ---- Globals read ----
        BUTTON_TEXT, FOCUS_COLOUR, MAIN_BACKGROUND, MAIN_HOVER, OTHER_BACKGROUND,
        OTHER_HOVER.

        ---- Outputs ----
        Any
            The Tk label, not placed.

        ---- Globals mutated ----
        None. Creates the widget.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        background = MAIN_BACKGROUND if is_main else OTHER_BACKGROUND
        hover = MAIN_HOVER if is_main else OTHER_HOVER
        button = self._tk.Label(self.frame,
                                text=text,
                                bg=background,
                                fg=BUTTON_TEXT if is_main else self._colours['text'],
                                font=(self._family,
                                      self._size + (1 if is_main else 0),
                                      'bold' if is_main else 'normal',
                                      ),
                                anchor='center' if is_main else 'w',
                                justify='left',
                                padx=10,
                                pady=7 if is_main else 5,
                                cursor='hand2',
                                takefocus=1,
                                highlightthickness=1,
                                highlightbackground=self._colours['background'],
                                highlightcolor=FOCUS_COLOUR,
                                wraplength=520,
                                )
        def run(event: Any = None) -> str:
            command()
            return 'break'
        for sequence in ('<Button-1>', '<space>'):
            button.bind(sequence, run)
        button.bind('<Enter>', lambda e: button.configure(bg=hover))
        button.bind('<Leave>', lambda e: button.configure(bg=background))
        return button

    # ---- _choices_placer -------------------------------------------------------------
    def _choices_placer(self, buttons: List[Any]) -> None:
        """
        ---- Summary ----
        Helper method to place the buttons of the choices: one above the other, or in
        two columns for a long list.

        ---- Inputs ----
        buttons : List[Any]
            The buttons, in the order of the choices.

        ---- Globals read ----
        ONE_COLUMN_MOST.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Places the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if len(buttons) <= ONE_COLUMN_MOST:
            for button in buttons:
                button.pack(side='top', fill='x', pady=2)
            return
        grid = self._tk.Frame(self.frame, bg=self._colours['background'])
        grid.columnconfigure(0, weight=1, uniform='choice')
        grid.columnconfigure(1, weight=1, uniform='choice')
        rows = (len(buttons) + 1) // 2
        for i, button in enumerate(buttons):  # down the first column, then the second
            button.lift(grid)
            button.grid(in_=grid,
                        row=i % rows,
                        column=i // rows,
                        sticky='ew',
                        padx=2,
                        pady=2,
                        )
        grid.pack(side='top', fill='x')
        self._widgets.append(grid)

    # ---- _clearer --------------------------------------------------------------------
    def _clearer(self) -> None:
        """
        ---- Summary ----
        Helper method to take away the answers shown.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Destroys or hides the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        # the box may sit in the row of a folder question, which goes with the widgets
        self.entry.pack_forget()
        self.confirm.pack_forget()
        for widget in self._widgets:
            widget.destroy()
        self._widgets = []
        self._ticks = []
        self._ticked = []
        self._multi_go = None
        self._folders = []
        self._other = None
        self._path_row = None

    # ---- _folder_browser -------------------------------------------------------------
    def _folder_browser(self) -> None:
        """
        ---- Summary ----
        Helper method to open the computer's own folder picker (the one window that
        pops up), starting at the folder in the box, and to put the folder picked in
        the box; Cancel leaves the box as it was.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Opens the picker and changes the box (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        folder_start_finder
        """

        picked = filedialog.askdirectory(parent=self.frame.winfo_toplevel(),
                                         initialdir=folder_start_finder(
                                             self.entry.get(),
                                             ),
                                         mustexist=False,
                                         title='Choose a folder',
                                         )
        if picked:
            self.entry.delete(0, 'end')
            self.entry.insert(0, str(Path(picked)))
        self.entry.focus_set()
        self.entry.icursor('end')

    # ---- _folder_picker --------------------------------------------------------------
    def _folder_picker(self, index: int) -> None:
        """
        ---- Summary ----
        Helper method to highlight one folder button, or Other folder… with its box
        and Browse… under it.

        ---- Inputs ----
        index : int
            Place of the folder in the buttons, from 0; -1 for Other folder….

        ---- Globals read ----
        OTHER_BACKGROUND, OTHER_FOLDER_TEXT, OTHER_HOVER, PICKED_BACKGROUND.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the buttons and shows or hides the box (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        folder_words_builder
        """

        self._picked = index
        shown = [(button, name, note, i == index)
                 for i, (button, _, name, note) in enumerate(self._folders)
                 ]
        shown.append((self._other, OTHER_FOLDER_TEXT, '', index == -1))
        for button, name, note, is_picked in shown:
            background = PICKED_BACKGROUND if is_picked else OTHER_BACKGROUND
            button.configure(text=folder_words_builder(name, note, is_picked),
                             bg=background,
                             fg=BUTTON_TEXT if is_picked else self._colours['text'],
                             )
            button.bind('<Leave>', lambda e, b=button, c=background: b.configure(bg=c))
            button.bind('<Enter>', lambda e, b=button: b.configure(bg=OTHER_HOVER))
        if index == -1:
            self._path_row.pack(side='top', fill='x', pady=2, after=self._other)
            self.entry.focus_set()
            self.entry.icursor('end')
        else:
            self._path_row.pack_forget()
            self.frame.focus_set()

    # ---- _folder_sender --------------------------------------------------------------
    def _folder_sender(self) -> None:
        """
        ---- Summary ----
        Helper method to give the folder highlighted (CONTINUE): the path of its
        button, or the path in the box under Other folder…; an empty box gives nothing.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls on_click (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._picked == -1:
            typed = self.entry.get().strip()
            if typed:
                self._on_click(typed, typed)
            return
        _, answer, name, _ = self._folders[self._picked]
        self._on_click(answer, name)

    # ---- _folder_shower --------------------------------------------------------------
    def _folder_shower(self, request: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Helper method to show the answers of a folder question: a button for each
        folder offered, Other folder… with its row (the box for a full path and
        Browse…, shown when it is highlighted), and CONTINUE.

        ---- Inputs ----
        request : Dict[str, Any]
            {'kind': 'folder', 'options', 'default', 'value'}: options the (answer,
            name, note) of each folder, default the answer highlighted at first, value
            what the box starts with.

        ---- Globals read ----
        BROWSE_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates and places the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _button_maker
        _choices_placer
        _folder_browser
        _folder_picker
        _folder_sender
        folder_default_finder
        """

        folders = [tuple(folder) for folder in request['options'] or []]
        buttons = []
        for i, (answer, name, note) in enumerate(folders):
            button = self._button_maker(name,
                                        lambda i=i: self._folder_picker(i),
                                        False,
                                        )
            self._folders.append((button, answer, name, note))
            self._widgets.append(button)
            buttons.append(button)
        self._other = self._button_maker(OTHER_FOLDER_TEXT,
                                         lambda: self._folder_picker(-1),
                                         False,
                                         )
        self._widgets.append(self._other)
        if buttons:
            self._choices_placer(buttons)
        self._other.pack(side='top', fill='x', pady=2)

        # ---- 1 The row under Other folder… -------------------------------------------
        self._path_row = self._tk.Frame(self.frame, bg=self._colours['background'])
        self._widgets.append(self._path_row)
        browse = self._button_maker(BROWSE_TEXT, self._folder_browser, False)
        self._widgets.append(browse)
        browse.lift(self._path_row)
        browse.pack(in_=self._path_row, side='right', padx=(4, 0))
        self.entry.lift(self._path_row)
        self.entry.pack(in_=self._path_row, side='left', fill='x', expand=True, ipady=5)
        self.entry.delete(0, 'end')
        self.entry.insert(0, request['value'] or '')

        # ---- 2 CONTINUE, and the folder highlighted at first -------------------------
        go = self._button_maker('CONTINUE', self._folder_sender, True)
        go.pack(side='top', fill='x', pady=(6, 2))
        self._widgets.append(go)
        self._folder_picker(folder_default_finder([answer for answer, _, _ in folders],
                                                  request['default'],
                                                  ),
                            )

    # ---- _multi_sender ---------------------------------------------------------------
    def _multi_sender(self) -> None:
        """
        ---- Summary ----
        Helper method to send the choices ticked, in the order they were ticked; with
        none ticked the button does nothing.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls on_click (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._ticked:
            return
        self._on_click(','.join(str(n) for n in self._ticked),
                       ', '.join(self._ticks[n - 1].cget('text')[2:]
                                 for n in self._ticked
                                 ),
                       )

    # ---- _ticker ---------------------------------------------------------------------
    def _ticker(self, number: int) -> None:
        """
        ---- Summary ----
        Helper method to tick or untick one choice of several; CONTINUE is greyed
        while none is ticked.

        ---- Inputs ----
        number : int
            Number of the choice, from 1.

        ---- Globals read ----
        BUTTON_TEXT, OFF_TEXT, TICKED, UNTICKED.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the buttons (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if number in self._ticked:
            self._ticked.remove(number)
        else:
            self._ticked.append(number)
        button = self._ticks[number - 1]
        words = button.cget('text')[2:]
        button.configure(
            text=f'{TICKED if number in self._ticked else UNTICKED} {words}',
            )
        if self._multi_go is not None:
            self._multi_go.configure(fg=BUTTON_TEXT if self._ticked else OFF_TEXT)

    # ---- back_shower -----------------------------------------------------------------
    def back_shower(self,
                    text: str,
                    on_back: Callable[[], None],
                    extra: Sequence[Tuple[str, Callable[[], None]]] = (),
                    is_confirm: bool = False,
                    ) -> None:
        """
        ---- Summary ----
        Method to show only the button that goes back to the step waited at, while an
        earlier step is open, under the step's own buttons when it has any. While a
        table waits ("Edit ODs", "Edit labels"), its CONFIRM button stays above them.

        ---- Inputs ----
        text : str
            Its words ("Back to Δψ").
        on_back : Callable[[], None]
            What a click does.
        extra : Sequence[Tuple[str, Callable[[], None]]]
            (words, what a click does) of each of the step's own buttons (the two
            export buttons of the trim step); empty for none.
        is_confirm : bool
            True while the question that waits is a table, so Confirm is shown too.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the answers (side effect).

        ---- Helpers ----
        _button_maker
        _clearer
        """

        self._clearer()
        if is_confirm:
            self.confirm.pack(side='top', fill='x', pady=2)
        for words, on_click in extra:
            own = self._button_maker(words, on_click, True)
            own.pack(side='top', fill='x', pady=2)
            self._widgets.append(own)
        button = self._button_maker(text, on_back, True)
        button.pack(side='top', fill='x', pady=2)
        self._widgets.append(button)

    # ---- focuser ---------------------------------------------------------------------
    def focuser(self) -> None:
        """
        ---- Summary ----
        Method to give the keyboard to the typing box when it is shown, otherwise to
        the frame of the answers, so that Enter presses no button and a key typed
        lands in no box above the plot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Moves the keyboard focus (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        # in a folder question the box is in its row, shown only with Other folder…
        is_typed = self._path_row is None or self._picked == -1
        if self.entry.winfo_manager() and is_typed:
            self.entry.focus_set()
            self.entry.icursor('end')
        else:
            self.frame.focus_set()

    # ---- request_shower --------------------------------------------------------------
    def request_shower(self, request: Optional[Dict[str, Any]]) -> None:
        """
        ---- Summary ----
        Method to show the answers of the question asked.

        ---- Inputs ----
        request : Optional[Dict[str, Any]]
            {'kind', 'options', 'default', 'value'} as the questions send it
            (utils_shared.questions._answer_announcer): kind 'continue', 'yesno',
            'choice', 'multi', 'number', 'text', 'folder' or 'confirm'; options the
            words of each choice ('folder': the (answer, name, note) of each
            folder); default the answer Enter gives ('y' or 'n'; the number of a
            choice; the numbers ticked at first; the folder highlighted at first);
            value what the box starts with. None for no question.

        ---- Globals read ----
        TICKED, UNTICKED, OFF_TEXT.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the answers (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _button_maker
        _choices_placer
        _clearer
        _folder_shower
        _multi_sender
        _ticker
        """

        # ---- 1 Take away the answers of the last question ----------------------------
        self._clearer()
        if request is None:
            return
        kind = request['kind']
        click = self._on_click
        def made(text: str, answer: str, echo: str) -> Any:
            # every answer button looks the same: none is the one Enter gives
            button = self._button_maker(text, lambda: click(answer, echo), True)
            self._widgets.append(button)
            return button

        # ---- 2 Show the answers of this one ------------------------------------------
        if kind == 'continue':
            # the extra buttons of the step (the two export buttons) sit above CONTINUE
            for answer, words in request['options'] or []:
                made(words, answer, words).pack(side='top', fill='x', pady=2)
            # a step may name its button for what it does (Export)
            words = request.get('value') or 'CONTINUE'
            made(words, '', words).pack(side='top', fill='x', pady=2)
        elif kind == 'yesno':
            for answer, words in (('y', 'YES'), ('n', 'NO')):
                made(words, answer, words).pack(side='top', fill='x', pady=2)
        elif kind == 'choice':
            self._choices_placer([made(words, str(number), words)
                                  for number, words in enumerate(request['options'],
                                                                 start=1,
                                                                 )
                                  ],
                                 )
        elif kind == 'multi':
            for number, words in enumerate(request['options'], start=1):
                button = self._button_maker(f'{UNTICKED} {words}',
                                            lambda n=number: self._ticker(n),
                                            False,
                                            )
                self._ticks.append(button)
                self._widgets.append(button)
            self._choices_placer(self._ticks)
            for number in request['default'] or []:
                self._ticker(number)
            self._multi_go = self._button_maker('CONTINUE', self._multi_sender, True)
            self._multi_go.configure(fg=BUTTON_TEXT if self._ticked else OFF_TEXT)
            self._multi_go.pack(side='top', fill='x', pady=(6, 2))
            self._widgets.append(self._multi_go)
        elif kind == 'folder':
            self._folder_shower(request)
        elif kind in ('number', 'text'):
            self.entry.delete(0, 'end')
            self.entry.insert(0, request['value'] or '')
            self.entry.pack(side='top', fill='x', pady=(6, 2), ipady=5)
            go = self._button_maker('CONTINUE', self._on_typed, True)
            go.pack(side='top', fill='x', pady=2)
            self._widgets.append(go)
        elif kind == 'confirm':
            self.confirm.pack(side='top', fill='x', pady=2)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- folder_default_finder -----------------------------------------------------------
def folder_default_finder(answers: Sequence[str], default: Optional[str]) -> int:
    """
    ---- Summary ----
    Main function to choose the folder button highlighted when a folder question is
    asked: the folder offered as the default, else Other folder… when a default not
    among the buttons is given, else the first button.

    ---- Inputs ----
    answers : Sequence[str]
        The full path of each folder button, in order.
    default : Optional[str]
        The folder Enter gives, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        Place of the button, from 0; -1 for Other folder… (also when there is no
        button).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    path_cleaner
    """

    def same(text: str) -> str:
        return str(Path(path_cleaner(text)).expanduser()).lower()

    if default:
        for i, answer in enumerate(answers):
            if same(answer) == same(default):
                return i
        return -1
    return 0 if answers else -1


# ---- folder_start_finder -------------------------------------------------------------
def folder_start_finder(text: str) -> str:
    """
    ---- Summary ----
    Main function to find where the folder picker opens: the folder in the box, or the
    nearest folder above it that exists, else the home folder.

    ---- Inputs ----
    text : str
        What the box holds (quotes and a leading ~ allowed); may be empty.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The folder the picker starts in.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    path_cleaner
    """

    cleaned = path_cleaner(text or '')
    if cleaned:
        path = Path(cleaned).expanduser()
        while True:
            if path.is_dir():
                return str(path)
            if path.parent == path:
                break
            path = path.parent
    return str(Path.home())


# ---- folder_words_builder ------------------------------------------------------------
def folder_words_builder(name: str, note: str, is_picked: bool) -> str:
    """
    ---- Summary ----
    Main function to write the words of a folder button: the mark of the one
    highlighted, the folder's name and what it holds.

    ---- Inputs ----
    name : str
        The folder's name, or "Other folder…".
    note : str
        What it holds ('6 files', 'new folder'); empty for none.
    is_picked : bool
        True for the button highlighted.

    ---- Globals read ----
    PICKED_MARK, UNPICKED_MARK.

    ---- Outputs ----
    str
        The words, such as "●  data_OCR_and_haem  ·  12 files".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    mark = PICKED_MARK if is_picked else UNPICKED_MARK
    return f'{mark}  {name}  ·  {note}' if note else f'{mark}  {name}'


# ---- step_of_change_finder -----------------------------------------------------------
def step_of_change_finder(changes: Dict[str, Any]) -> Optional[str]:
    """
    ---- Summary ----
    Main function to give the earliest step that a change in the strip under the plot
    belongs to.

    ---- Inputs ----
    changes : Dict[str, Any]
        {name: new value} of the strip values that changed.

    ---- Globals read ----
    CHANGE_STEPS, GUIDE_KEYS, PSI_TICK_CHANGE, TAB_STEPS, TIME_TAB_CHANGE.

    ---- Outputs ----
    Optional[str]
        The key of the step, or None when the change belongs to every step (how the
        haems, the OCR and the labels are shown, Δψ unticked).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # Unticking Δψ only takes its panel away, so it opens no step; ticking it opens the
    # Δψ step, where its numbers are set.
    keys = [CHANGE_STEPS[name]
            for name in changes
            if name in CHANGE_STEPS
            and not (name == PSI_TICK_CHANGE and not changes[name])
            ]
    if changes.get(TIME_TAB_CHANGE) in TAB_STEPS:
        keys.append(TAB_STEPS[changes[TIME_TAB_CHANGE]])
    if not keys:
        return None
    return min(keys, key=GUIDE_KEYS.index)
