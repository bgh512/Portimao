"""
The experiment browser window: the guide with its questions on the left, plots on the right.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import base64
import builtins
import io
import math
import os
import queue
import sys
import threading
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import panel_order_mover
from utils_shared.output_capture import CapturedOutput, output_capturer
from utils_shared.questions import (answer_request_setter,
                                    COLOUR_QUESTION,
                                    COLOUR_QUIET,
                                    COLOUR_SECTION,
                                    guide_step_setter,
                                    time_request_setter,
                                    )
from utils_shared.run_logging import details_writer
from utils_shared.user_notices import problem_shower
from utils_viewer.viewer_edges import (EdgeChoice,
                                       EdgeOverlay,
                                       HANDLE_BAND_PX,
                                       own_value_lister,
                                       )
from utils_viewer.viewer_guide import (AnswerArea,
                                       CARD_BACKGROUND,
                                       GuidePanel,
                                       GuideState,
                                       )
from utils_viewer.viewer_preview import (KEY_PREFIX,
                                         PreviewSpec,
                                         TimeAxis,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_renderer import PreviewRenderer
from utils_viewer.viewer_strip import (EdgeRow,
                                       formula_picture_maker,
                                       PANEL_ORDER_CHANGE,
                                       SettingsStrip,
                                       strip_values_checker,
                                       )
from utils_viewer.viewer_table import AnswerTable, table_texts_filler
from utils_viewer.viewer_terminal import (ansi_splitter,
                                          ansi_style_updater,
                                          OutputRouter,
                                          )


# ---- CONSTANTS -----------------------------------------------------------------------
# The colour of a question line, which the guide writes larger than the rest.
QUESTION_FOREGROUND = ansi_style_updater({'fg': None, 'bold': False, 'italic': False},
                                         COLOUR_QUESTION[2:-1],
                                         )['fg']
QUESTION_EXTRA_POINTS = 3
# The explanations, grey in a terminal, are lighter in the guide so they read easily.
QUIET_FOREGROUND = ansi_style_updater({'fg': None, 'bold': False, 'italic': False},
                                      COLOUR_QUIET[2:-1],
                                      )['fg']
INFO_COLOUR = '#c8c8c8'
# A section heading is the stage name, which the guide shows above the step, so the
# card leaves it out, with the dashes under it.
SECTION_FOREGROUND = ansi_style_updater({'fg': None, 'bold': False, 'italic': False},
                                        COLOUR_SECTION[2:-1],
                                        )['fg']
GUIDE_FONT_POINTS = 12

MONO_FONTS =('Menlo', 'Consolas', 'DejaVu Sans Mono', 'Liberation Mono', 'Courier New')
# the plain font of what is typed in the tables, easier to read than the typewriter one
SANS_FONTS = ('Segoe UI',
              'Helvetica Neue',
              'Helvetica',
              'DejaVu Sans',
              'Liberation Sans',
              'Arial',
              )
TERMINAL_BACKGROUND = '#1e1e1e'
TERMINAL_TEXT = '#d4d4d4'
ANSWER_COLOUR = '#9cdcfe'
ERROR_COLOUR = '#ff7b86'
ICON_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'icon.png'
CLICK_HINT = 'Click an answer. Enter gives the highlighted one.'
# a box is shown only for a number or a name: every other answer is a button
NUMBER_HINT = 'Type a number, then click Continue or press Enter.'
NAME_HINT = 'Type it in the box, then click Continue or press Enter.'
FOLDER_HINT = ('Click a folder, then Continue. Under Other folder…, type a full path '
               'or click Browse….')
# The clicks in the boxes that ask questions of their own while a question waits.
ASKING_CHANGES = ('edit_ods', 'edit_labels', 'export_csv', 'do_pca')
EDGES_HINT = ('Drag the edges on the plot, or type the times in the Time regions box '
              'above it, then click Continue.')
OWN_VALUES_MARK = '  (own times)'  # after a file in the drop-down whose edges differ
SPAN_HINT = ('Drag across the plot to fill in the answer, or type it, then click '
             'Continue.')
TABLE_HINT = ('Click a cell and type; Tab moves across, Enter moves down. Press '
              'Confirm when the table is filled in.')
# While a table is open it fills the open step under this many lines of text; without
# one the text takes the room the guide leaves, at least this many lines.
TABLE_TERMINAL_LINES = 5
TERMINAL_LINES = 6
SIGN_BACKGROUND = '#ffd76a'
SIGN_EDGE = '#e8a317'
SIGN_TEXT = '#5a3d00'
SIGN_WORDS = 'Plotting data …'
SIGN_TEXT_POINTS = 20
# After a click that gives an answer, the sign is shown when the program has not asked
# its next question within this time, so a quick answer does not flash it.
CLICK_SIGN_DELAY_MS = 200
# The spinning wheel of the "Plotting data …" sign, in the middle of the plot: its
# size, the number and thickness of its spokes, and how often it turns one spoke on.
WHEEL_RADIUS_PX = 48
WHEEL_SPOKES = 12
WHEEL_SPOKE_WIDTH_PX = 8
WHEEL_STEP_MS = 80
POINTER_COLOUR = '#0b62c4'
FILES_HELP = ('Select a file using the drop-down, or use the arrows to browse the '
              'data.')
FIGURES_HELP = ('Select a figure using the drop-down, or use the arrows to look at '
                'each one. Experiment plots marked [locked] are final; the figure '
                'being built is listed after them.')
ENTRY_BACKGROUND = '#2b2b2b'
# shown, once the questions about each file are over, for a file whose plot was not
# saved with the last settings (nothing is plotted, or its plot could not be saved)
NOT_DRAWN_TEXT = '{name}\n\nThe plot of this file was not saved with your final settings.'
MINIMUM_TK = 8.6  # Tk 8.5 (Apple's own Python) draws blank windows
# The window opens maximised; un-maximised it takes WINDOW_SIZE_PX, made smaller to
# leave SCREEN_MARGIN_PX for the taskbar, the Dock or the menu bar on a small screen.
WINDOW_SIZE_PX = (1500, 860)
MINIMUM_SIZE_PX = (900, 500)
SCREEN_MARGIN_PX = 100
# set by the launcher (launchers/bootstrap.pyw) to the file to make once the window is
# up, so it can close its small "Opening Portimao" window then
OPENED_SWITCH = 'PORTIMAO_OPENED_FILE'
SYMBOL_FONTS = ('Segoe UI Symbol',
                'Arial Unicode MS',
                'Helvetica Neue',
                'DejaVu Sans',
                'Liberation Sans',
                'Arial',
                )
# Characters that are hard to type, for event labels and other text answers.
SYMBOLS = ('µ',
           '⁻¹',
           '⁻²',
           '⁻³',
           '²',
           '³',
           '₂',
           '₃',
           '₄',
           '⁺',
           '±',
           '°',
           'Δ',
           'α',
           'β',
           'γ',
           'λ',
           '×',
           '·',
           )
PLOT_BACKGROUND = '#f2f2f2'
# The arrows that move a panel of the plot of a file up or down: the room kept for them
# left of the picture, the side of the square of each (smaller beside a low panel) and
# their colours (the arrow that cannot be used, up on the top panel, is paler).
PANEL_ARROW_BAND_PX = 26
PANEL_ARROW_SIZE_PX = 18
PANEL_ARROW_FILL = '#f4f4f2'
PANEL_ARROW_EDGE = '#9a9a96'
PANEL_ARROW_COLOUR = '#222222'
PANEL_ARROW_OFF_COLOUR = '#c8c8c8'
_CLOSED = object()
_active_gui: Optional['ViewerGui'] = None


# ---- GuiUnavailableError -------------------------------------------------------------
class GuiUnavailableError(Exception):
    """
    ---- Summary ----
    Raised when the browser window cannot be opened (no Tkinter, no display, or a Tk
    that draws blank windows); its text says why, and what to do, in plain words.

    ---- Attributes ----
    None.

    ---- Globals read ----
    None.

    ---- Methods ----
    None.
    """


# ---- ViewerGui -----------------------------------------------------------------------
class ViewerGui:
    """
    ---- Summary ----
    The experiment browser window. The program's questions run in their own thread and
    their text and answers pass through the terminal on the left, so the plot on the
    right stays usable while a question waits. Previews are drawn by a third thread.

    ---- Attributes ----
    logic_thread : Optional[threading.Thread]
        The thread running the program, whose output belongs in the terminal.
    exit_code : int
        What the program returned (1 when it was stopped).
    window_errors : List[str]
        The traceback of each error met in the window's own work (its Tk callbacks),
        in order; empty when there was none.

    ---- Globals read ----
    MONO_FONTS and the colour constants (module constants).

    ---- Methods ----
    __init__
    _answer_sender
    _answer_writer
    _axis_box_finder
    _back_taker
    _band_drawer
    _callback_error_keeper
    _click_sign_shower
    _click_sign_starter
    _clicked_answer_sender
    _closing_handler
    _confirm_sender
    _display_name_lister
    _drag_ender
    _dragger
    _drain_runner
    _drawing_sign_drawer
    _edges_refresher
    _event_handler
    _every_file_taker
    _every_file_unticker
    _file_follower
    _formula_writer
    _guide_drawer
    _guide_line_clicker
    _hint_refresher
    _history_stepper
    _icon_setter
    _image_deliverer
    _image_receiver
    _keys_shower
    _lock_drawer
    _logic_runner
    _message_shower
    _nav_state_setter
    _navigator
    _opened_teller
    _pane_writer
    _panel_arrow_checker
    _panel_arrow_clicker
    _panel_arrows_drawer
    _picture_shower
    _pointer_mover
    _resizer
    _screen_filler
    _step_taker
    _strip_change_runner
    _strip_change_teller
    _symbol_inserter
    _table_layout_setter
    _time_clicker
    _time_line_drawer
    _typed_edge_taker
    _wheel_turner
    _widgets_builder
    _window_raiser
    answer_requester
    drawing_sign_shower
    edges_hider
    edges_reader
    edges_shower
    extra_publisher
    formula_sender
    input_reader
    output_capturer
    pictures_publisher
    run
    saved_plot_publisher
    session_attacher
    spec_publisher
    step_teller
    strip_choices_setter
    strip_fits_setter
    strip_library_setter
    strip_listener_setter
    answer_listener_setter
    strip_reader
    strip_setter
    strip_state_setter
    table_hider
    table_reader
    table_shower
    text_sender
    time_reader_setter
    window_closer
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 root: Any,
                 program: Callable[[], int],
                 title: str,
                 close_after_s: Optional[float] = None,
                 ) -> None:
        """
        ---- Summary ----
        Method to build the window and set up the queues between its threads.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        root : Any
            The Tk root window.
        program : Callable[[], int]
            The program to run; it asks the questions and returns its exit code.
        title : str
            Window title.
        close_after_s : Optional[float]
            Seconds after the program finishes when the window closes by itself,
            without asking (the check switch); None leaves it open until the user
            closes it.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the attributes on the instance, builds the widgets and has the root
        window report its errors to _callback_error_keeper.

        ---- Equations ----
        None.

        ---- Helpers ----
        _callback_error_keeper
        _icon_setter
        _widgets_builder
        """

        self._tk = tk
        self._root = root
        self._program = program
        self._close_after_s = close_after_s
        self.logic_thread: Optional[threading.Thread] = None
        self.exit_code = 1
        self.window_errors: List[str] = []
        root.report_callback_exception = self._callback_error_keeper
        self._events: 'queue.Queue' = queue.Queue()
        self._answers: 'queue.Queue' = queue.Queue()
        self._session: Optional[ViewerSession] = None
        self._renderer: Optional[PreviewRenderer] = None
        self._names: List[str] = []
        self._index = 0
        self._version = 0
        self._has_spec = False
        self._images: Dict[str, bytes] = {}
        self._previous: Dict[str, bytes] = {}
        self._notes: Dict[str, str] = {}
        self._failures: Dict[str, str] = {}
        self._axes: Dict[str, Optional[TimeAxis]] = {}
        self._previous_axes: Dict[str, Optional[TimeAxis]] = {}
        self._shown_axis: Optional[TimeAxis] = None
        self._picture_box: Optional[Tuple[float, float, int, int]] = None
        self._pointer: Optional[Tuple[int, int]] = None
        self._time_kind: Optional[str] = None
        self._time_reader: Optional[Callable] = None
        self._drag_start: Optional[Tuple[float, float]] = None
        self._photo: Any = None
        self._decoded: Any = None
        self._resize_job: Any = None
        self._is_waiting = False
        self._is_finished = False
        self._is_destroyed = False
        self._style: Dict[str, Any] = {'fg': None, 'bold': False, 'italic': False}
        self._is_carriage = False
        self._is_heading = False  # a section heading is being left out
        self._history: List[str] = []
        self._history_position = 0
        self._fonts: Dict[tuple, Any] = {}
        root.title(title)
        self._is_pictures = False
        self._is_browsing_over = False
        self._file_count = 0
        self._help_base = ''
        self._is_table_shown = False
        # The open table belongs to one step of the guide: it is shown only while that
        # step is open. A table opened over another (Edit ODs from the labels table)
        # keeps the one under it, as typed, until it closes.
        self._table_shown: Optional[dict] = None
        self._table_step: Optional[int] = None
        self._table_stack: List[Tuple[dict, List[Dict[str, str]], Optional[int]]] = []
        # What was typed in a table left for another step, by kind of table, to open
        # it again as it was left; and whether the program is to take it as it is.
        self._left_texts: Dict[str, List[Dict[str, str]]] = {}
        self._is_table_left = False
        self._is_busy = False
        self._is_wheel_turning = False  # the wheel of the "Plotting data …" sign
        self._click_count = 0  # clicks sent to the program, for the sign after a click
        self._strip_listener: Optional[Callable[[Dict[str, Any]], None]] = None
        self._answer_listener: Optional[Callable[[], None]] = None
        self._is_strip_on = False
        self._is_shown_stale = False
        self._is_arrow_waiting = False
        self._is_over_arrow = False
        self._arrows: List[Tuple[str, int, float, float, float, float, bool]] = []
        self._guide = GuideState()
        self._request: Optional[Dict[str, Any]] = None
        self._is_back_shown = False
        self._widgets_builder()
        self._icon_setter()

    # ---- WINDOW HELPERS --------------------------------------------------------------

    # ---- _answer_sender --------------------------------------------------------------
    def _answer_sender(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to pass the answer typed in the box to the question that is waiting for
        it (Continue under the box, or Enter in it).

        ---- Inputs ----
        event : Any
            The Tk key event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Writes the answer into the open step and wakes the question thread (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _clicked_answer_sender
        """

        if not self._is_waiting or self._is_table_shown:
            return
        answer = self._entry.get()
        if answer.strip():
            self._history.append(answer)
        self._history_position = len(self._history)
        self._drag_start = None
        self._canvas.delete('band')
        self._clicked_answer_sender(answer, answer.strip() or 'Continue')

    # ---- _answer_writer --------------------------------------------------------------
    def _answer_writer(self, value: Optional[float]) -> None:
        """
        ---- Summary ----
        Method to write the answer the mouse gave into the answer box, in place of what
        was there; nothing changes when the mouse gave no answer.

        ---- Inputs ----
        value : Optional[float]
            The answer, or None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the text of the answer box (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if value is None:
            return
        self._entry.delete(0, 'end')
        self._entry.insert(0, f'{round(value, 2):g}')
        self._entry.focus_set()

    # ---- _axis_box_finder ------------------------------------------------------------
    def _axis_box_finder(self) -> Optional[Tuple[float, float, float, float]]:
        """
        ---- Summary ----
        Method to find where the panels of the picture shown sit in the plot area.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Optional[Tuple[float, float, float, float]]
            (left, right, top, bottom) of the panels in pixels from the top left of the
            plot area, or None when the picture has no time axis.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        x = picture left + fraction across * picture width;
        y = picture top + (1 - fraction up) * picture height.

        ---- Helpers ----
        None.
        """

        if self._picture_box is None or self._shown_axis is None:
            return None
        left, top, width, height = self._picture_box
        axis = self._shown_axis
        return (left + axis.left * width,
                left + axis.right * width,
                top + (1.0 - axis.top) * height,
                top + (1.0 - axis.bottom) * height,
                )

    # ---- _back_taker -----------------------------------------------------------------
    def _back_taker(self) -> None:
        """
        ---- Summary ----
        Method to open the step the program waits at again, after an earlier step was
        opened ("Back to <step>"), with the answers of its question.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the guide (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _guide_drawer
        GuideState.back_taker
        """

        self._guide.back_taker()
        self._guide_drawer()

    # ---- _band_drawer ----------------------------------------------------------------
    def _band_drawer(self, x: float) -> None:
        """
        ---- Summary ----
        Method to draw the band of a drag over the panels, from where the drag started
        to ``x`` (kept within the time axis), with its length in seconds above it.

        ---- Inputs ----
        x : float
            Where the mouse is, in pixels from the left of the plot area.

        ---- Globals read ----
        POINTER_COLOUR (module constant).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area (side effect).

        ---- Equations ----
        Length (s) = |time at x - time at the start| x 60.

        ---- Helpers ----
        _axis_box_finder
        pointed_time_finder
        """

        self._canvas.delete('band')
        box = self._axis_box_finder()
        if box is None or self._drag_start is None:
            return
        left, right, top, bottom = box
        start_x, start_min = self._drag_start
        x = min(max(x, left + 0.5), right - 0.5)  # inside the edges despite rounding
        end_min = pointed_time_finder(x,
                                      (top + bottom) / 2.0,
                                      self._picture_box,
                                      self._shown_axis,
                                      )
        if end_min is None:
            return
        self._canvas.create_rectangle(min(start_x, x),
                                      top,
                                      max(start_x, x),
                                      bottom,
                                      outline=POINTER_COLOUR,
                                      width=2,
                                      tags='band',
                                      )
        self._canvas.create_text((start_x + x) / 2.0,
                                 top - 4,
                                 text=f'{abs(end_min - start_min) * 60.0:.0f} s',
                                 anchor='s',
                                 fill=POINTER_COLOUR,
                                 font=(self._family, 10, 'bold'),
                                 tags='band',
                                 )

    # ---- _callback_error_keeper ------------------------------------------------------
    def _callback_error_keeper(self,
                               kind: type,
                               value: BaseException,
                               trace: Any,
                               ) -> None:
        """
        ---- Summary ----
        Method that Tk calls when the window's own work (a Tk callback) meets an error:
        the traceback is printed as Tk does by default, and kept in window_errors so a
        check can tell the window went wrong.

        ---- Inputs ----
        kind : type
            Class of the error.
        value : BaseException
            The error.
        trace : Any
            Its traceback.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Adds to window_errors and prints to the error stream (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        text = ''.join(traceback.format_exception(kind, value, trace))
        self.window_errors.append(text)
        sys.stderr.write(f'Exception in Tkinter callback\n{text}')

    # ---- _click_sign_shower ----------------------------------------------------------
    def _click_sign_shower(self, count: int) -> None:
        """
        ---- Summary ----
        Method to put the "Plotting data …" sign on the plot when the program is still
        working on a click: no question has been asked since, and no other click was
        made. The next question, plot or picture takes it away.

        ---- Inputs ----
        count : int
            Number of the click it was started for.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Marks the window busy and draws the sign (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _picture_shower
        """

        if (self._is_destroyed
            or self._is_waiting
            or self._is_finished
            or self._is_busy
            or count != self._click_count
            ):
            return
        self._is_busy = True
        self._picture_shower()

    # ---- _click_sign_starter ---------------------------------------------------------
    def _click_sign_starter(self) -> None:
        """
        ---- Summary ----
        Method to start the wait after a click that gives an answer: if the program has
        not asked its next question within CLICK_SIGN_DELAY_MS, the "Plotting data …"
        sign goes on the plot, so a redraw never looks like nothing happening.

        ---- Inputs ----
        None.

        ---- Globals read ----
        CLICK_SIGN_DELAY_MS (module constant).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Counts the click and starts a timer (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _click_sign_shower
        """

        self._click_count += 1
        count = self._click_count
        self._root.after(CLICK_SIGN_DELAY_MS, lambda: self._click_sign_shower(count))

    # ---- _clicked_answer_sender ------------------------------------------------------
    def _clicked_answer_sender(self, answer: str, echo: str) -> None:
        """
        ---- Summary ----
        Method to pass the answer of a button (or of the typing box) to the question
        that is waiting for it. The open step then keeps what is said from here on:
        the messages before this answer fold away when the next question is asked.

        ---- Inputs ----
        answer : str
            The answer as the question reads it ('y', '2', '1,3', a typed number ...).
        echo : str
            The words written under the question for it ('Yes', the choice ...).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Writes the answer into the open step, marks where it ends and wakes the
        question thread (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _click_sign_starter
        _pane_writer
        """

        if not self._is_waiting or self._is_table_shown:
            return
        self._is_waiting = False
        self._hint.configure(text='Working ...')
        self._pane_writer(f'→ {echo}\n', 'answer')
        self._text.mark_set('since', 'end-1c')
        self._answers.put(answer)
        self._click_sign_starter()

    # ---- _closing_handler ------------------------------------------------------------
    def _closing_handler(self) -> None:
        """
        ---- Summary ----
        Method to close the window. While the program is still running the user is asked
        first, and a question that is waiting is ended so the program stops cleanly.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stops the threads and closes the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._is_finished:
            from tkinter import messagebox
            if not messagebox.askokcancel('Close Portimao',
                                          'The program has not finished. Close the '
                                          'window and stop it? A file that is being '
                                          'written may be left incomplete.',
                                          parent=self._root,
                                          ):
                return
        self._is_destroyed = True
        self._answers.put(_CLOSED)
        if self._renderer is not None:
            self._renderer.stopper()
        self._root.destroy()

    # ---- _confirm_sender -------------------------------------------------------------
    def _confirm_sender(self, event: Any = None) -> str:
        """
        ---- Summary ----
        Method to answer the instruction waiting on a table: Confirm was clicked, or
        Enter or the space bar pressed on it. The program then reads the table.

        ---- Inputs ----
        event : Any
            The Tk mouse or key event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            'break', so Tk does nothing more with the click or key.

        ---- Globals mutated ----
        None. Writes "Confirm" into the open step and wakes the question thread (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _click_sign_starter
        _pane_writer
        """

        if not self._is_waiting or not self._is_table_shown:
            return 'break'
        self._is_waiting = False
        self._hint.configure(text='Working ...')
        self._pane_writer('→ Confirm\n', 'answer')
        self._text.mark_set('since', 'end-1c')
        self._answers.put('')
        self._click_sign_starter()
        return 'break'

    # ---- _display_name_lister --------------------------------------------------------
    def _display_name_lister(self) -> List[str]:
        """
        ---- Summary ----
        Method to give the names for the drop-down: the experiment files are marked as
        locked once the figures built from them are shown, and, while edges are dragged
        on the plot, the files whose edges differ from most files are marked.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[str]
            One text per entry of the list.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        own_value_lister
        """

        # edges copied by a rule of the step are meant to differ from file to file
        is_marking = (self._edges.is_on
                      and not self._is_pictures
                      and self._edges.choice.value_copier is None
                      )
        if is_marking:
            own = set(own_value_lister(self._edges.values,
                                       self._edges.choice.unmarked_fields,
                                       ),
                      )
            return [f'{name}{OWN_VALUES_MARK}' if name in own else name
                    for name in self._names
                    ]
        if not self._is_pictures:
            return list(self._names)
        return [f'[locked] {name}' if i < self._file_count else name
                for i, name in enumerate(self._names)
                ]

    # ---- _drag_ender -----------------------------------------------------------------
    def _drag_ender(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to end a drag across the plot: an edge being dragged is put where the
        button is let go; otherwise the times where the drag started and ended (kept
        within the time axis) are turned into the answer, which is written into the
        answer box. The band stays until the answer is sent.

        ---- Inputs ----
        event : Any
            The Tk release event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the text of the answer box (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _answer_writer
        _axis_box_finder
        pointed_time_finder
        """

        if self._edges.release_handler(event):
            return
        start = self._drag_start
        self._drag_start = None
        box = self._axis_box_finder()
        if start is None or box is None or not self._is_waiting:
            return
        left, right, top, bottom = box
        end_min = pointed_time_finder(min(max(event.x, left + 0.5), right - 0.5),
                                      (top + bottom) / 2.0,
                                      self._picture_box,
                                      self._shown_axis,
                                      )
        if end_min is None or end_min == start[1] or self._time_reader is None:
            self._canvas.delete('band')
            return
        self._answer_writer(self._time_reader(self._names[self._index],
                                              min(start[1], end_min),
                                              max(start[1], end_min),
                                              ),
                            )

    # ---- _dragger --------------------------------------------------------------------
    def _dragger(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to follow the mouse while the button is held: the time line moves with
        it and the edge being dragged follows it; during any other drag, the band is
        drawn to it.

        ---- Inputs ----
        event : Any
            The Tk motion event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _band_drawer
        _pointer_mover
        """

        self._pointer_mover(event)
        if self._edges.motion_handler(event):
            return
        if self._drag_start is not None:
            self._band_drawer(event.x)

    # ---- _drain_runner ---------------------------------------------------------------
    def _drain_runner(self) -> None:
        """
        ---- Summary ----
        Method that runs on the window thread every few milliseconds and carries out the
        messages the other threads have queued, joining consecutive text into one
        insert.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window and schedules itself again (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _event_handler
        _pane_writer
        """

        if self._is_destroyed:
            return
        pending: List[str] = []
        pending_kind = 'out'
        def flush() -> None:
            if pending:
                self._pane_writer(''.join(pending), pending_kind)
                pending.clear()
        try:
            for _ in range(400):
                event = self._events.get_nowait()
                if event[0] == 'text':
                    if pending and event[2] != pending_kind:
                        flush()
                    pending_kind = event[2]
                    pending.append(event[1])
                    continue
                flush()
                self._event_handler(event)
        except queue.Empty:
            pass
        flush()
        self._root.after(25, self._drain_runner)

    # ---- _drawing_sign_drawer --------------------------------------------------------
    def _drawing_sign_drawer(self, text: str = SIGN_WORDS) -> None:
        """
        ---- Summary ----
        Method to draw the "Plotting data …" sign in the middle of the plot area, a large
        spinning wheel with the words under it, to show that the picture for the
        latest settings is still being made. The wheel turns until the plot area is
        drawn again, which takes the sign away.

        ---- Inputs ----
        text : str
            The words under the wheel.

        ---- Globals read ----
        SIGN_BACKGROUND, SIGN_EDGE, SIGN_TEXT, SIGN_TEXT_POINTS, SIGN_WORDS,
        WHEEL_RADIUS_PX, WHEEL_SPOKES, WHEEL_SPOKE_WIDTH_PX (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area and starts the wheel turning (side effects).

        ---- Equations ----
        Spoke i points at the angle 2 pi i / WHEEL_SPOKES, from 0.45 to 1 radius out
        of the centre.

        ---- Helpers ----
        _wheel_turner
        """

        # ---- 1 The card behind the wheel and its words, in the middle ----------------
        canvas = self._canvas
        centre_x = max(canvas.winfo_width(), 200) // 2
        centre_y = max(canvas.winfo_height(), 160) // 2
        words = canvas.create_text(centre_x,
                                   centre_y + WHEEL_RADIUS_PX + 34,
                                   text=text,
                                   fill=SIGN_TEXT,
                                   font=(self._sign_family, SIGN_TEXT_POINTS, 'bold'),
                                   tags=('drawing_sign',),
                                   )
        left, _, right, bottom = canvas.bbox(words)
        half = max((right - left) // 2, WHEEL_RADIUS_PX) + 32
        back = canvas.create_rectangle(centre_x - half,
                                       centre_y - WHEEL_RADIUS_PX - 24,
                                       centre_x + half,
                                       bottom + 18,
                                       fill=SIGN_BACKGROUND,
                                       outline=SIGN_EDGE,
                                       width=3,
                                       tags=('drawing_sign',),
                                       )
        canvas.tag_raise(words, back)

        # ---- 2 The spokes of the wheel, turned by _wheel_turner ----------------------
        for index in range(WHEEL_SPOKES):
            angle = 2.0 * math.pi * index / WHEEL_SPOKES
            canvas.create_line(centre_x + 0.45 * WHEEL_RADIUS_PX * math.cos(angle),
                               centre_y + 0.45 * WHEEL_RADIUS_PX * math.sin(angle),
                               centre_x + WHEEL_RADIUS_PX * math.cos(angle),
                               centre_y + WHEEL_RADIUS_PX * math.sin(angle),
                               width=WHEEL_SPOKE_WIDTH_PX,
                               capstyle='round',
                               fill=SIGN_EDGE,
                               tags=('drawing_sign', f'wheel_spoke_{index}'),
                               )
        if not self._is_wheel_turning:
            self._is_wheel_turning = True
            self._wheel_turner(0)

    # ---- _edge_tick_taker ------------------------------------------------------------
    def _edge_tick_taker(self, field: str, is_ticked: bool) -> None:
        """
        ---- Summary ----
        Method to take a numbered tick of a row of the edges (an averaging window used
        or left out): on every file when "Apply to all" is ticked,
        otherwise on the file shown.

        ---- Inputs ----
        field : str
            The field of the tick.
        is_ticked : bool
            Its new state.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the overlay and redraws (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_refresher
        """

        self._edges.field_setter(field, 1.0 if is_ticked else 0.0)
        self._edges_refresher()

    # ---- _edge_toggle_taker ----------------------------------------------------------
    def _edge_toggle_taker(self, field: str, is_on: bool) -> None:
        """
        ---- Summary ----
        Method to take a toggle of the step ("Adjust each window"), which holds on
        every file.

        ---- Inputs ----
        field : str
            The field of the toggle.
        is_on : bool
            Its new state.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the overlay and redraws (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_refresher
        """

        self._edges.every_file_field_setter(field, 1.0 if is_on else 0.0)
        self._edges_refresher()

    # ---- _edges_refresher ------------------------------------------------------------
    def _edges_refresher(self) -> None:
        """
        ---- Summary ----
        Method to show where the edges dragged on the plot are: the row of the strip
        holds the values of the file shown, and the drop-down marks the files whose
        edges differ from most files.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the drop-down and the row (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _display_name_lister
        """

        if not self._names:
            return
        self._combo.configure(values=self._display_name_lister())
        self._combo.current(self._index)
        if self._edges.is_on and self._index < self._file_count:
            name = self._names[self._index]
            shown = self._edges.shown_values_reader(name)
            self._edge_row.values_setter(shown)
            # without boxes when the step has one row
            self._second_row.values_setter(shown)
            # the numbered ticks and the note of each row, and the step's toggles
            choice, own = self._edges.choice, self._edges.values.get(name)
            rows = [('', []), ('', [])]
            if choice.row_teller is not None and own is not None:
                rows = choice.row_teller(name, own)
            self._edge_row.ticks_setter(*rows[0])
            self._second_row.ticks_setter(*rows[1])
            self._options_row.toggles_setter([(field,
                                               words,
                                               bool((own or {}).get(field)),
                                               )
                                              for field, words in choice.options
                                              ],
                                             )

    # ---- _event_handler --------------------------------------------------------------
    def _event_handler(self, event: tuple) -> None:
        """
        ---- Summary ----
        Method to carry out one message from the other threads, on the window thread.

        ---- Inputs ----
        event : tuple
            (kind, ...) with kind 'prompt', 'ask' (how the question is answered),
            'step' (a step of the guide starts), 'formula' (a formula for the
            terminal), 'spec', 'session', 'pictures', 'extra',
            'image', 'time', 'edges', 'strip', 'strip_choices', 'strip_fits',
            'strip_library', 'strip_state', 'busy',
            'table_show', 'table_hide', 'closed' or 'finished'. The "Plotting data …"
            sign of 'busy' stays until the next question, preview or picture shown.
            With close_after_s, 'finished' also closes the window after that time.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _closing_handler
        _display_name_lister
        _edges_refresher
        _formula_writer
        _guide_drawer
        _hint_refresher
        _image_deliverer
        _image_receiver
        _keys_shower
        _nav_state_setter
        _navigator
        _pane_writer
        _picture_shower
        _table_layout_setter
        AnswerArea.request_shower
        GuideState.step_starter
        """

        kind = event[0]
        if kind in ('prompt', 'pictures', 'spec') or (kind == 'extra' and event[3]):
            was_busy, self._is_busy = self._is_busy, False
            if was_busy and kind == 'prompt':
                self._picture_shower()  # takes the sign away
        if kind == 'prompt':
            self._is_waiting = True
            if self._is_table_shown:
                # the cell that still needs something, after a refused Confirm
                self._hint.configure(text=TABLE_HINT)
                self._table.cell_focuser()
            else:
                if not self._guide.is_back():
                    self._area.focuser()
                self._hint_refresher()
        elif kind == 'ask':
            # A new question: what was said before the last answer folds away (it
            # stays in the run's log), and its answers are shown.
            self._request = event[1]
            self._text.tag_add('folded', '1.0', 'since')
            self._keys_shower()
            if not self._guide.is_back():
                self._area.request_shower(self._request)
            else:
                # an earlier step is open: its Back to button stays, with Confirm
                # beside it while a table waits
                self._guide_drawer()
        elif kind == 'ask_again':
            # a table or question opened from the boxes is done: the question that
            # waits shows its answers again, in its own step
            self._request = event[1]
            if self._guide.is_back():
                self._guide.back_taker()
                self._guide_drawer()
            elif self._request is not None:
                self._area.request_shower(self._request)
        elif kind == 'step':
            self._guide.step_starter(event[1])
            self._guide_drawer()
        elif kind == 'formula':
            self._formula_writer(event[1])
        elif kind == 'edges':
            # The rows of the edges sit in the Time regions box, under its tabs.
            choice = event[1]
            self._edges.choice_setter(choice)
            self._second_row.frame.pack_forget()
            self._edge_row.frame.pack_forget()
            self._options_row.frame.pack_forget()
            if choice is not None:
                if choice.second_switch is not None:
                    # the second row sits under the first
                    field, words = choice.second_switch
                    self._second_row.fields_setter(choice.second_fields,
                                                   any(own.get(field)
                                                       for own in choice.values.values()
                                                       ),
                                                   choice.unit,
                                                   words,
                                                   )
                if choice.switch is None:
                    self._edge_row.fields_setter(choice.fields,
                                                 choice.is_every_file,
                                                 choice.unit,
                                                 )
                else:
                    # the step's own tick box: ticked when its field is on in any file
                    field, words = choice.switch
                    self._edge_row.fields_setter(choice.fields,
                                                 any(own.get(field)
                                                     for own in choice.values.values()
                                                     ),
                                                 choice.unit,
                                                 words,
                                                 )
                self._edge_row.frame.pack(side='top', anchor='w', pady=(0, 2))
                if choice.second_switch is not None:
                    self._second_row.frame.pack(side='top', anchor='w', pady=(0, 2))
                if choice.options:
                    self._options_row.fields_setter([],
                                                    choice.is_every_file,
                                                    choice.unit,
                                                    )
                    self._options_row.frame.pack(side='top', anchor='w', pady=(0, 2))
            self._picture_shower()
            self._edges_refresher()
            if self._is_waiting and not self._is_table_shown:
                self._hint_refresher()
        elif kind == 'strip':
            self._strip.values_setter(event[1])
        elif kind == 'strip_choices':
            self._strip.choices_setter(*event[1:])
        elif kind == 'strip_fits':
            self._strip.fits_setter(event[1])
        elif kind == 'strip_library':
            self._strip.library_setter(event[1])
        elif kind == 'strip_state':
            self._strip.state_setter(event[1])
            self._is_strip_on = bool(event[1])
            self._picture_shower()  # the arrows of the panels come and go with it
        elif kind == 'busy':
            self._is_busy = True
            self._picture_shower()
        elif kind == 'table_show':
            self._table_opener(event[1])
        elif kind == 'table_hide':
            self._table_closer()
        elif kind == 'time':
            self._time_kind, self._time_reader = event[1], event[2]
            self._drag_start = None
            self._canvas.delete('band')
            self._canvas.configure(cursor='crosshair' if event[1] else '')
            if self._is_waiting and not self._is_table_shown:
                self._hint_refresher()
        elif kind == 'session':
            self._session = event[1]
            self._names = [s['name'] for s in self._session.summaries]
            self._file_count = len(self._names)
            self._combo.configure(values=self._names)
            self._renderer = PreviewRenderer(self._session, self._image_deliverer)
            self._renderer.start()
            self._is_pictures = False
            # a session attached after the browser steps ended (the window step asked
            # for by a later figure) draws its files again
            self._is_browsing_over = False
            self._help_base = FILES_HELP
            self._help.configure(text=FILES_HELP)
            self._nav_state_setter(True)
            self._navigator(self._session.current)
        elif kind == 'pictures':
            # The experiment files stay (locked, as last drawn) and the figures being
            # built are listed after them.
            files = self._names[:self._file_count]
            self._is_pictures = True
            self._names = files + [title for title, _ in event[1]]
            kept = {name: png for name, png in self._images.items() if name in files}
            self._images = {**kept, **{title: png for title, png in event[1]}}
            self._axes = {name: self._axes.get(name) for name in kept}
            for title, _ in event[1]:
                self._failures.pop(title, None)
                self._notes.pop(title, None)
            self._has_spec = True
            self._combo.configure(values=self._display_name_lister())
            self._help_base = FIGURES_HELP
            self._help.configure(text=FIGURES_HELP)
            self._nav_state_setter(len(self._names) > 1)
            self._navigator(len(files))
        elif kind == 'extra':
            # Extra pictures (not files) are listed after the files until the next
            # preview is drawn from the settings; the same title replaces its picture.
            title, png, is_shown = event[1], event[2], event[3]
            if title not in self._names[self._file_count:]:
                self._names = self._names + [title]
            self._images[title] = png
            self._axes.pop(title, None)
            self._failures.pop(title, None)
            self._notes.pop(title, None)
            self._has_spec = True
            self._combo.configure(values=self._display_name_lister())
            self._nav_state_setter(len(self._names) > 1)
            if is_shown:
                self._navigator(self._names.index(title))
            elif self._names[self._index] == title:
                self._picture_shower()
        elif kind == 'spec':
            spec, name = event[1], event[2]
            if not self._is_pictures and len(self._names) > self._file_count:
                self._names = self._names[:self._file_count]
                self._index = min(self._index, self._file_count - 1)
                self._combo.configure(values=self._display_name_lister())
            self._version += 1
            self._previous = {**self._previous, **self._images}
            self._previous_axes = {**self._previous_axes,
                                   **{shown: self._axes.get(shown)
                                      for shown in self._images
                                      },
                                   }
            self._images, self._notes, self._failures = {}, {}, {}
            self._axes = {}
            self._has_spec = True
            if name in self._names:
                self._index = self._names.index(name)
            self._renderer.request_setter(spec, self._version, self._index)
            self._navigator(self._index)
        elif kind == 'image':
            self._image_receiver(*event[1:])
        elif kind == 'saved':
            # The plot saved for a file takes the place of its preview and is shown.
            name, png = event[1], event[2]
            self._images[name] = png
            for kept in (self._failures, self._notes, self._axes, self._previous):
                kept.pop(name, None)
            self._has_spec = True
            if name in self._names:
                self._navigator(self._names.index(name))
        elif kind == 'closed':
            # No file is drawn any more, so an older picture would never be replaced.
            self._is_browsing_over = True
            self._is_busy = False
            self._previous, self._previous_axes = {}, {}
            self._nav_state_setter(False)
            self._picture_shower()
        elif kind == 'finished':
            self._is_finished = True
            if self._is_busy:
                self._is_busy = False
                self._picture_shower()  # takes the sign away
            self._nav_state_setter(False)
            self._hint.configure(text='Finished - close this window when you are done')
            self._area.request_shower(None)
            self._pane_writer('\n[Finished. You can close this window.]\n', 'answer')
            if self._close_after_s is not None:
                self._root.after(round(self._close_after_s * 1000),
                                 self._closing_handler,
                                 )

    # ---- _every_file_taker -----------------------------------------------------------
    def _every_file_taker(self, is_every_file: bool, row: str = 'first') -> None:
        """
        ---- Summary ----
        Method to take the tick box of a row of the edges. As "Apply to all": ticking
        it copies the edges of the file shown to every file once, and until another
        file is shown a moved or typed edge moves on every file; unticked, on the file
        shown only. As the step's own switch (EdgeChoice.switch, or second_switch for
        the second row), it sets the field of the switch to 1 or 0 on every file.

        ---- Inputs ----
        is_every_file : bool
            The new state of the tick box.
        row : str
            'first', 'second' or 'options' (the line of "Apply to all" of a step whose
            rows have switches).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the overlay (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_refresher
        """

        choice = self._edges.choice
        switch = None
        if choice is not None and row != 'options':
            switch = choice.second_switch if row == 'second' else choice.switch
        if switch is not None:
            self._edges.every_file_field_setter(switch[0],
                                                1.0 if is_every_file else 0.0,
                                                )
            self._edges_refresher()
            return
        if row == 'second':
            return
        if is_every_file:
            self._edges.all_files_copier()
        else:
            self._edges.is_every_file = False

    # ---- _every_file_unticker --------------------------------------------------------
    def _every_file_unticker(self) -> None:
        """
        ---- Summary ----
        Method to untick "Apply to all" in the Time regions box when the overlay has
        unticked it, because another file is shown.

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

        choice = self._edges.choice
        if choice is None:
            return
        row = self._edge_row if choice.switch is None else self._options_row
        row.every_file_unticker()

    # ---- _file_follower --------------------------------------------------------------
    def _file_follower(self, name: str) -> None:
        """
        ---- Summary ----
        Method to show on the plot the file whose cell of a table is being typed in,
        when another file is shown.

        ---- Inputs ----
        name : str
            Name of the file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the file shown (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _navigator
        """

        files = self._names[:self._file_count]
        if name in files and files.index(name) != self._index:
            self._navigator(files.index(name))

    # ---- _formula_writer -------------------------------------------------------------
    def _formula_writer(self, formula: str) -> None:
        """
        ---- Summary ----
        Method to add a formula to the terminal on a line of its own, drawn as a
        textbook writes it in the colour of the terminal's text and the size of its
        letters. It folds away with the text around it at the next question.

        ---- Inputs ----
        formula : str
            The formula in matplotlib's maths text.

        ---- Globals read ----
        TERMINAL_TEXT (module constant).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Adds the picture to the terminal and keeps it (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        formula_picture_maker
        """

        picture = self._tk.PhotoImage(master=self._root,
                                      data=base64.b64encode(
                                          formula_picture_maker(formula,
                                                                TERMINAL_TEXT,
                                                                self._size,
                                                                ),
                                          ),
                                      )
        # Tk shows a picture only while something holds it
        self._formulas = getattr(self, '_formulas', []) + [picture]
        widget = self._text
        at_end = widget.yview()[1] > 0.98
        widget.configure(state='normal')
        if widget.get('end-2c', 'end-1c') not in ('\n', ''):
            widget.insert('end', '\n')
        widget.image_create('end', image=picture, padx=12, pady=6)
        widget.insert('end', '\n')
        widget.configure(state='disabled')
        if at_end:
            widget.see('end')

    # ---- _guide_drawer ---------------------------------------------------------------
    def _guide_drawer(self) -> None:
        """
        ---- Summary ----
        Method to draw the guide again: its lines with the open step's card under its
        line and, while an earlier step is open, that step's note and help above its
        messages and the button back to the step waited at in place of the answers.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the left side of the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _back_taker
        AnswerArea.back_shower
        AnswerArea.request_shower
        GuidePanel.rows_drawer
        GuideState.card_teller
        GuideState.row_lister
        _table_step_follower
        """

        self._table_step_follower()
        self._guide_panel.rows_drawer(self._guide.row_lister())
        card = self._guide.card_teller()
        if card['note']:
            self._guide_note.configure(text=f"{card['note']}\n\n{card['help']}")
            self._guide_note.pack(side='top',
                                  fill='x',
                                  padx=10,
                                  pady=(8, 0),
                                  before=self._text_box,
                                  )
            # the trim step opened again keeps its two export buttons
            extra = [(words,
                      lambda change=change: self._strip_change_teller({change: True}),
                      )
                     for change, words in card['extra']
                     ]
            # a table opened from the View box (Edit ODs) keeps its Confirm; one put
            # away while another step is open does not
            is_table = (self._is_table_shown and
                        bool(self._request) and
                        self._request.get('kind') == 'confirm'
                        )
            self._area.back_shower(card['back'], self._back_taker, extra, is_table)
            self._is_back_shown = True
        else:
            self._guide_note.pack_forget()
            if self._is_back_shown:
                self._area.request_shower(self._request)
                if self._is_waiting:
                    self._area.focuser()
            self._is_back_shown = False
        self._text.see('end')

    # ---- _guide_line_clicker ---------------------------------------------------------
    def _guide_line_clicker(self, index: int) -> None:
        """
        ---- Summary ----
        Method to open the step whose line in the guide was clicked: one already
        asked, or the one the program waits at.

        ---- Inputs ----
        index : int
            Index of the step in the guide.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the guide (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _guide_drawer
        GuideState.line_opener
        """

        if self._guide.line_opener(index):
            self._guide_drawer()

    # ---- _hint_refresher -------------------------------------------------------------
    def _hint_refresher(self) -> None:
        """
        ---- Summary ----
        Method to show, under the answers, what to do for the question waiting.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the hint (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _hint_chooser
        """

        kind = self._request['kind'] if self._request else None
        self._hint.configure(text=_hint_chooser(kind,
                                                self._time_kind,
                                                self._edges.is_on,
                                                ),
                             )

    # ---- _history_stepper ------------------------------------------------------------
    def _history_stepper(self, step: int) -> None:
        """
        ---- Summary ----
        Method to recall an earlier answer in the answer box with the up and down keys.

        ---- Inputs ----
        step : int
            -1 for the previous answer, +1 for the next one.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the text of the answer box (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._history:
            return
        position = min(max(self._history_position + step, 0), len(self._history))
        self._history_position = position
        self._entry.delete(0, 'end')
        if position < len(self._history):
            self._entry.insert(0, self._history[position])

    # ---- _icon_setter ----------------------------------------------------------------
    def _icon_setter(self) -> None:
        """
        ---- Summary ----
        Method to give the window (and so the taskbar or dock) the Portimao icon. A
        missing icon file or an unsupported system is ignored.

        ---- Inputs ----
        None.

        ---- Globals read ----
        ICON_PATH (module constant).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the window icon (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        try:
            base = Image.open(ICON_PATH).convert('RGBA')
            resampling = getattr(Image, 'Resampling', Image)
            self._icons = []
            for size in (256, 64, 32):
                buffer = io.BytesIO()
                base.resize((size, size), resampling.LANCZOS).save(buffer, 'PNG')
                self._icons.append(
                    self._tk.PhotoImage(
                        data=base64.b64encode(buffer.getvalue()).decode('ascii'),
                        ),
                    )
            self._root.iconphoto(True, *self._icons)
        except Exception:  # no icon is better than no window
            return
        if sys.platform == 'darwin':
            try:  # the Dock icon needs PyObjC, which is not always installed
                from AppKit import NSApplication, NSImage
                image = NSImage.alloc().initWithContentsOfFile_(str(ICON_PATH))
                NSApplication.sharedApplication().setApplicationIconImage_(image)
            except Exception:
                pass

    # ---- _image_deliverer ------------------------------------------------------------
    def _image_deliverer(self,
                         version: int,
                         name: str,
                         png: Optional[bytes],
                         notes: str,
                         time_axis: Optional[TimeAxis],
                         ) -> None:
        """
        ---- Summary ----
        Method to queue a finished preview from the preview thread for the window.

        ---- Inputs ----
        version : int
            Number of the request it was drawn for.
        name : str
            File name.
        png : Optional[bytes]
            Picture, or None when it could not be drawn.
        notes : str
            Warnings, or the reason when there is no picture.
        time_axis : Optional[TimeAxis]
            Where the time axis sits in the picture, or None when it has none.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the preview (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('image', version, name, png, notes, time_axis))


# ---- MAIN FUNCTIONS ------------------------------------------------------------------

    # ---- _image_receiver -------------------------------------------------------------
    def _image_receiver(self,
                        version: int,
                        name: str,
                        png: Optional[bytes],
                        notes: str,
                        time_axis: Optional[TimeAxis],
                        ) -> None:
        """
        ---- Summary ----
        Method to take a finished preview from the renderer and show it if it is the
        current file. Previews of older settings are dropped.

        ---- Inputs ----
        version : int
            Number of the request the preview was drawn for.
        name : str
            File name.
        png : Optional[bytes]
            Picture, or None when it could not be drawn.
        notes : str
            Warnings, or the reason when there is no picture.
        time_axis : Optional[TimeAxis]
            Where the time axis sits in the picture, or None when it has none.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stores the preview and may redraw the plot area (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _picture_shower
        """

        if version != self._version:
            return
        self._is_arrow_waiting = False  # the plots are drawn with the new order
        if png is None:
            self._failures[name] = notes
        else:
            self._images[name] = png
            self._notes[name] = notes
            self._axes[name] = time_axis
        if self._names and name == self._names[self._index]:
            self._picture_shower()

    # ---- _keys_shower ----------------------------------------------------------------
    def _keys_shower(self) -> None:
        """
        ---- Summary ----
        Method to show the row of symbols (µ, ⁻¹, ...) only where text is typed: a
        name in the typing box, or a table.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Shows or hides the row (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        kind = self._request['kind'] if self._request else None
        if self._is_table_shown or kind == 'text':
            self._keys.pack(fill='x', pady=(4, 0), before=self._hint)
        else:
            self._keys.pack_forget()

    # ---- _lock_drawer ----------------------------------------------------------------
    def _lock_drawer(self) -> None:
        """
        ---- Summary ----
        Method to draw a small padlock and "Locked" in the corner of the plot area, to
        show that this experiment plot is final and cannot be changed any more.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        right = self._canvas.winfo_width() - 14
        top = 10
        colour = '#555555'
        self._canvas.create_arc(right - 44,
                                top,
                                right - 28,
                                top + 16,
                                start=0,
                                extent=180,
                                style='arc',
                                outline=colour,
                                width=2,
                                )
        self._canvas.create_rectangle(right - 48,
                                      top + 8,
                                      right - 24,
                                      top + 24,
                                      fill=colour,
                                      outline=colour,
                                      )
        self._canvas.create_text(right - 54,
                                 top + 16,
                                 text='Locked',
                                 anchor='e',
                                 fill=colour,
                                 )

    # ---- _logic_runner ---------------------------------------------------------------
    def _logic_runner(self) -> None:
        """
        ---- Summary ----
        Method that runs the program in its own thread and reports when it is done.
        When the program stops with a reason, or with a problem, one plain sentence in
        the terminal says so; the details of a problem go to the log only.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets exit_code, prints why the program stopped, if it did, and queues the
        finished message (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        problem_shower
        """

        try:
            self.exit_code = self._program()
        except SystemExit as exc:
            if isinstance(exc.code, str):  # a stop with a reason for the user
                print(f'\n{exc.code}')
            self.exit_code = exc.code if isinstance(exc.code, int) else 1
        except BaseException as exc:  # show the problem in the window, then finish
            problem_shower('\nThe run stopped', exc)
            self.exit_code = 1
        finally:
            self._events.put(('finished',))

    # ---- _message_shower -------------------------------------------------------------
    def _message_shower(self, text: str) -> None:
        """
        ---- Summary ----
        Method to replace the plot with a short message.

        ---- Inputs ----
        text : str
            Message to show.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Redraws the plot area (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._canvas.delete('all')
        self._photo = None
        self._edges.picture_placer(None, None, None, None, None)
        width = max(self._canvas.winfo_width(), 200)
        height = max(self._canvas.winfo_height(), 100)
        self._canvas.create_text(width // 2,
                                 height // 2,
                                 text=text,
                                 fill='#707070',
                                 width=int(width * 0.8),
                                 justify='center',
                                 font=(self._family, 12),
                                 )

    # ---- _nav_state_setter -----------------------------------------------------------
    def _nav_state_setter(self, enabled: bool) -> None:
        """
        ---- Summary ----
        Method to switch the file selector and arrows on or off.

        ---- Inputs ----
        enabled : bool
            True to allow navigation.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widget states (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        state = 'normal' if enabled else 'disabled'
        self._previous_button.configure(state=state)
        self._next_button.configure(state=state)
        self._combo.configure(state='readonly' if enabled else 'disabled')

    # ---- _navigator ------------------------------------------------------------------
    def _navigator(self, index: int, is_from_user: bool = False) -> None:
        """
        ---- Summary ----
        Method to make a file the current one and show it.

        ---- Inputs ----
        index : int
            Position of the file in the list.
        is_from_user : bool
            True when the user chose it, so the answer box gets the keyboard back
            (not while a table is open: its cells keep it).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Updates the selector, the plot and the renderer's order (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_refresher
        _picture_shower
        """

        if not self._names:
            return
        self._index = index % len(self._names)
        self._combo.current(self._index)
        self._counter.configure(text=f'{self._index + 1} of {len(self._names)}')
        if self._session is not None and self._index < self._file_count:
            self._session.current = self._index
        if self._renderer is not None and self._index < self._file_count:
            self._renderer.wanted_setter(self._index)
        self._picture_shower()
        if self._edges.is_on:
            self._edges_refresher()
        if is_from_user and self._is_waiting and not self._is_table_shown:
            self._area.focuser()

    # ---- _opened_teller --------------------------------------------------------------
    def _opened_teller(self) -> None:
        """
        ---- Summary ----
        Helper method to tell the launcher that the window is up, by making the file
        it named, so its small "Opening Portimao" window closes now.

        ---- Inputs ----
        None.

        ---- Globals read ----
        OPENED_SWITCH (module constant); os.environ[OPENED_SWITCH], set only by the
        launcher.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Writes an empty file (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        opened = os.environ.get(OPENED_SWITCH)
        if not opened:
            return
        try:
            Path(opened).write_text('', encoding='utf-8')
        except OSError:  # the launcher's small window then closes after its longest wait
            pass

    # ---- _pane_writer ----------------------------------------------------------------
    def _pane_writer(self, text: str, kind: str = 'out') -> None:
        """
        ---- Summary ----
        Method to add text to the terminal, with its colours, overwriting the line when
        the text starts with a carriage return (progress messages). The explanations
        are written in a lighter grey than in a terminal, and a section heading (the
        stage, shown by the guide) is left out with the dashes under it.

        ---- Inputs ----
        text : str
            Text as printed.
        kind : str
            'out' (normal), 'err' (error text) or 'answer' (what the user typed).

        ---- Globals read ----
        ANSWER_COLOUR, ERROR_COLOUR, INFO_COLOUR, QUESTION_EXTRA_POINTS,
        QUESTION_FOREGROUND, QUIET_FOREGROUND, SECTION_FOREGROUND (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Adds text to the terminal and scrolls it (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        ansi_splitter
        ansi_style_updater
        """

        from tkinter import font as tkfont
        widget = self._text
        at_end = widget.yview()[1] > 0.98
        widget.configure(state='normal')
        for part_kind, value in ansi_splitter(text):
            if part_kind == 'code':
                self._style = ansi_style_updater(self._style, value)
                continue
            if part_kind == 'return':
                self._is_carriage = True
                continue
            # a section heading and the dashes under it are left out: the guide shows
            # the stage above the step
            if kind == 'out' and self._style['fg'] == SECTION_FOREGROUND:
                self._is_heading = True
                continue
            if self._is_heading:
                if not value.strip('\n-'):
                    continue
                self._is_heading = False
            if self._is_carriage:
                widget.delete('end-1c linestart', 'end-1c')
                self._is_carriage = False
            value = ''.join(c if ord(c) <= 0xFFFF else '?' for c in value)
            colour = {'err': ERROR_COLOUR, 'answer': ANSWER_COLOUR}.get(
                kind,
                self._style['fg'],
                )
            if colour == QUIET_FOREGROUND:
                colour = INFO_COLOUR
            bold = self._style['bold'] or kind == 'answer'
            # the question is written larger than the messages around it
            size = self._size + (QUESTION_EXTRA_POINTS
                                 if colour == QUESTION_FOREGROUND
                                 else 0
                                 )
            tag = f"{colour}|{bold}|{self._style['italic']}"
            if tag not in self._fonts:
                self._fonts[tag] = tkfont.Font(family=self._family,
                                               size=size,
                                               weight='bold' if bold else 'normal',
                                               slant=('italic'
                                                      if self._style['italic']
                                                      else 'roman'
                                                      ),
                                               )
                widget.tag_configure(tag,
                                     foreground=colour or TERMINAL_TEXT,
                                     font=self._fonts[tag],
                                     )
            widget.insert('end', value, tag)
        widget.configure(state='disabled')
        if at_end:
            widget.see('end')

    # ---- _picture_shower -------------------------------------------------------------
    def _picture_shower(self) -> None:
        """
        ---- Summary ----
        Method to show the picture of the current file, scaled to fit the plot area, or
        say why there is none yet. While edges are dragged on the plot, room is kept
        above the picture for their handles, and the overlay shades the picture and
        draws them. While the picture for the latest settings is still being made, or
        the program is making pictures of its own (drawing_sign_shower), the
        "Plotting data …" sign is on the plot (over the previous picture when there is
        one). Once the questions about each file are over, a file whose plot was not
        saved with the last settings says so instead.

        ---- Inputs ----
        None.

        ---- Globals read ----
        NOT_DRAWN_TEXT, HANDLE_BAND_PX (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Redraws the plot area and the status line (side effect).

        ---- Equations ----
        scale = min((width - arrow band) / picture width,
        (height - handle band) / picture height), at most 1.5; the arrow band is kept
        left of the picture only while the panels can be moved.

        ---- Helpers ----
        _drawing_sign_drawer
        _panel_arrow_checker
        _lock_drawer
        _message_shower
        _panel_arrows_drawer
        _time_line_drawer
        """

        self._resize_job = None
        if self._is_destroyed or not self._has_spec or not self._names:
            return
        name = self._names[self._index]
        png = self._images.get(name)
        failure = self._failures.get(name)
        is_stale = False
        if png is None and failure is None:
            png = self._previous.get(name)
            is_stale = png is not None
        if png is None:
            self._status.configure(text='')
            self._picture_box = None
            self._shown_axis = None
            self._arrows = []
            if failure is None and self._is_browsing_over:
                failure = NOT_DRAWN_TEXT.format(name=name)
            self._message_shower(failure or '')
            if failure is None:
                self._drawing_sign_drawer()
            return
        key = (name, id(png))
        if self._decoded is None or self._decoded[0] != key:
            self._decoded = (key, Image.open(io.BytesIO(png)))
        picture = self._decoded[1]

        # ---- 1 Fit the picture in the plot area, under the handles of any edges ------
        # and right of the arrows of its panels, while they can be moved
        is_edged = self._edges.is_on and self._index < self._file_count
        self._shown_axis = (self._previous_axes if is_stale else self._axes).get(name)
        self._is_shown_stale = is_stale
        band = HANDLE_BAND_PX if is_edged else 0
        gutter = PANEL_ARROW_BAND_PX if self._panel_arrow_checker() else 0
        room_width = self._canvas.winfo_width()
        room_height = self._canvas.winfo_height()
        width = max(room_width - 4 - gutter, 50)
        height = max(room_height - 4 - band, 50)
        scale = min(width / picture.width, height / picture.height, 1.5)
        size = (max(int(picture.width * scale), 1), max(int(picture.height * scale), 1))
        resampling = getattr(Image, 'Resampling', Image)
        shown = picture.resize(size, resampling.LANCZOS)
        left = gutter + (room_width - gutter - size[0]) // 2
        top = band + (room_height - band - size[1]) // 2
        self._picture_box = (left, top, size[0], size[1])

        # ---- 2 Show it, shaded with its edges while they are dragged -----------------
        self._canvas.delete('all')
        if is_edged and self._shown_axis is not None:
            self._photo = None
            item = self._canvas.create_image(left, top, anchor='nw')
            self._edges.picture_placer(name,
                                       shown,
                                       item,
                                       self._picture_box,
                                       self._shown_axis,
                                       )
        else:
            self._edges.picture_placer(None, None, None, None, None)
            buffer = io.BytesIO()
            shown.save(buffer, format='PNG')
            self._photo = self._tk.PhotoImage(
                data=base64.b64encode(buffer.getvalue()).decode('ascii'),
                )
            self._canvas.create_image(left, top, image=self._photo, anchor='nw')
        if self._is_pictures and self._index < self._file_count:
            self._lock_drawer()
        self._panel_arrows_drawer()
        if is_stale or self._is_busy:
            self._drawing_sign_drawer()

        # ---- 3 The notes and the key under the plot ----------------------------------
        lines = self._notes.get(name, '').splitlines()
        key = [line[len(KEY_PREFIX):] for line in lines if line.startswith(KEY_PREFIX)]
        if is_edged and self._edges.key_teller():
            key.append(self._edges.key_teller())
        note = '\n'.join(line for line in lines if not line.startswith(KEY_PREFIX))
        self._status.configure(text=note)
        self._help.configure(text='\n'.join([self._help_base] + key))
        self._time_line_drawer()

    # ---- _panel_arrow_checker --------------------------------------------------------
    def _panel_arrow_checker(self) -> bool:
        """
        ---- Summary ----
        Method to tell whether the panels of the picture shown can be moved up and
        down: it is the plot of a file with two panels or more, the settings strip is
        in use, no edges are dragged on it and it is not locked.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when the arrows of the panels have their place beside the picture.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return (self._is_strip_on
                and not self._is_pictures
                and not self._edges.is_on
                and self._index < self._file_count
                and self._shown_axis is not None
                and len(self._shown_axis.panels) > 1
                )

    # ---- _panel_arrow_clicker --------------------------------------------------------
    def _panel_arrow_clicker(self, event: Any) -> bool:
        """
        ---- Summary ----
        Method to act on a click on an arrow beside a panel: the panel moves one place
        up or down, told to the program as a change of the settings strip, which draws
        the plots again. The arrows are hidden until they are.

        ---- Inputs ----
        event : Any
            The Tk click event.

        ---- Globals read ----
        PANEL_ORDER_CHANGE.

        ---- Outputs ----
        bool
            True when the click was on an arrow, used or not.

        ---- Globals mutated ----
        None. Queues the change and hides the arrows (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _panel_arrows_drawer
        _strip_change_teller
        panel_arrow_finder
        panel_order_mover
        """

        arrow = panel_arrow_finder(event.x, event.y, self._arrows)
        if arrow is None or self._shown_axis is None:
            return False
        key, step, is_usable = arrow
        order = panel_order_mover([panel[0] for panel in self._shown_axis.panels],
                                  key,
                                  step,
                                  )
        if is_usable and order is not None:
            self._is_arrow_waiting = True
            self._strip_change_teller({PANEL_ORDER_CHANGE: order})
            self._panel_arrows_drawer()
        return True

    # ---- _panel_arrows_drawer --------------------------------------------------------
    def _panel_arrows_drawer(self) -> None:
        """
        ---- Summary ----
        Method to draw an up and a down arrow left of each panel of the plot of a
        file, while its panels can be moved. They are left out while the plot is being
        drawn again, so a click always moves a panel of the order on screen.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PANEL_ARROW_BAND_PX and the PANEL_ARROW colours (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area and keeps where the arrows are (side effects).

        ---- Equations ----
        The triangle of an arrow fills the middle half of its square.

        ---- Helpers ----
        _panel_arrow_checker
        panel_arrow_placer
        """

        self._canvas.delete('panel_arrow')
        self._arrows = []
        if (not self._panel_arrow_checker()
            or self._picture_box is None
            or self._is_shown_stale
            or self._is_busy
            or self._is_arrow_waiting
            ):
            return
        self._arrows = panel_arrow_placer(self._picture_box,
                                          self._shown_axis,
                                          PANEL_ARROW_BAND_PX,
                                          )
        for _, step, x0, y0, x1, y1, is_usable in self._arrows:
            self._canvas.create_rectangle(x0,
                                          y0,
                                          x1,
                                          y1,
                                          fill=PANEL_ARROW_FILL,
                                          outline=PANEL_ARROW_EDGE,
                                          tags='panel_arrow',
                                          )
            middle = (x0 + x1) / 2.0
            quarter = (x1 - x0) / 4.0
            tip, base = ((y0 + quarter, y1 - quarter)
                         if step < 0
                         else (y1 - quarter, y0 + quarter)
                         )
            self._canvas.create_polygon(middle,
                                        tip,
                                        x0 + quarter,
                                        base,
                                        x1 - quarter,
                                        base,
                                        fill=(PANEL_ARROW_COLOUR
                                              if is_usable
                                              else PANEL_ARROW_OFF_COLOUR
                                              ),
                                        tags='panel_arrow',
                                        )

    # ---- _pointer_mover --------------------------------------------------------------
    def _pointer_mover(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to note where the mouse is over the plot area and move the time line
        there; the line goes when the mouse leaves. Over an edge that can be dragged,
        the mouse becomes a two-way arrow.

        ---- Inputs ----
        event : Any
            The Tk motion event, or None when the mouse has left the plot area.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Redraws the time line (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _time_line_drawer
        """

        self._pointer = None if event is None else (event.x, event.y)
        if event is not None:
            self._edges.hover_handler(event)
        # a hand over an arrow of a panel that can be used
        arrow = (None
                 if event is None
                 else panel_arrow_finder(event.x, event.y, self._arrows)
                 )
        is_over_arrow = arrow is not None and arrow[2]
        if is_over_arrow != self._is_over_arrow:
            self._is_over_arrow = is_over_arrow
            self._canvas.configure(cursor='hand2'
                                   if is_over_arrow
                                   else 'crosshair'
                                   if self._time_kind
                                   else '',
                                   )
        self._time_line_drawer()

    # ---- _resizer --------------------------------------------------------------------
    def _resizer(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to redraw the picture at the new size once the window has stopped
        changing size.

        ---- Inputs ----
        event : Any
            The Tk configure event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Schedules a redraw (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _picture_shower
        """

        if self._resize_job is not None:
            self._root.after_cancel(self._resize_job)
        self._resize_job = self._root.after(120, self._picture_shower)

    # ---- _screen_filler --------------------------------------------------------------
    def _screen_filler(self) -> None:
        """
        ---- Summary ----
        Helper method to open the window maximised, as its maximise button does, so the
        answer box is never off a small screen. Un-maximised, it takes its usual size,
        made smaller to fit the screen.

        ---- Inputs ----
        None.

        ---- Globals read ----
        WINDOW_SIZE_PX, MINIMUM_SIZE_PX, SCREEN_MARGIN_PX (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sizes and maximises the window (side effect).

        ---- Equations ----
        size = max(minimum, min(usual, screen - margin)), for the width and the height.

        ---- Helpers ----
        None.
        """

        # ---- 1 The size when it is not maximised -------------------------------------
        root = self._root
        screen = (root.winfo_screenwidth(), root.winfo_screenheight())
        width, height = (max(minimum, min(usual, side - SCREEN_MARGIN_PX))
                         for usual, minimum, side in zip(WINDOW_SIZE_PX,
                                                         MINIMUM_SIZE_PX,
                                                         screen,
                                                         )
                         )
        root.geometry(f'{width}x{height}')
        root.minsize(*MINIMUM_SIZE_PX)

        # ---- 2 Maximise it -----------------------------------------------------------
        try:
            if root.tk.call('tk', 'windowingsystem') == 'x11':  # Linux
                root.attributes('-zoomed', True)
            else:  # Windows and the Mac
                root.state('zoomed')
        except self._tk.TclError:  # a system without maximising: the whole screen
            root.geometry(f'{screen[0]}x{screen[1]}+0+0')

    # ---- _step_taker -----------------------------------------------------------------
    def _step_taker(self, step: int) -> None:
        """
        ---- Summary ----
        Method to move to the next or previous file, looping round at the ends.

        ---- Inputs ----
        step : int
            +1 for the next file, -1 for the previous one.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the current file (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _navigator
        """

        if str(self._combo.cget('state')) == 'disabled':
            return
        self._navigator(self._index + step, True)

    # ---- _strip_change_runner --------------------------------------------------------
    def _strip_change_runner(self, changes: Dict[str, Any], prompt: Any) -> None:
        """
        ---- Summary ----
        Method to hand a change made in the boxes above the plot to the function the
        program registered, on the program thread while a question waits. What it
        prints goes on lines of its own, and the answer prompt is shown again under it.
        A click that asks questions of its own (Edit ODs, Edit labels, the export buttons) is
        not held back, so its questions show as they are asked; afterwards the answers
        of the question that waits come back, and the guide goes back to its step.

        ---- Inputs ----
        changes : Dict[str, Any]
            {name: new value} of the strip values that changed.
        prompt : Any
            The prompt of the question that waits, shown again after a message.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Calls the registered function, prints and queues the prompt (side
        effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        output_capturer
        """

        listener = self._strip_listener
        if listener is None:
            return
        if any(changes.get(name) for name in ASKING_CHANGES):
            waiting = self._request
            print()
            listener(changes)
            self._events.put(('ask_again', waiting))
            self._events.put(('prompt', str(prompt)))
            return
        with output_capturer() as printed:
            listener(changes)
        text = printed.getvalue()
        if text:
            print(f'\n{text}', end='' if text.endswith('\n') else '\n')
            self._events.put(('prompt', str(prompt)))

    # ---- _strip_change_teller --------------------------------------------------------
    def _strip_change_teller(self, changes: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Method to pass a change the user made in the settings strip to the program
        thread: it joins the typed answers, so a question that waits takes it at once
        (input_reader). A change that belongs to an earlier step (the fit while at Δψ)
        opens that step in the guide.

        ---- Inputs ----
        changes : Dict[str, Any]
            {name: new value} of the strip values that changed.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the change and may change the guide (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _guide_drawer
        GuideState.change_opener
        """

        self._answers.put(('strip', dict(changes)))
        if self._guide.change_opener(changes):
            self._guide_drawer()

    # ---- _symbol_inserter ------------------------------------------------------------
    def _symbol_inserter(self, symbol: str) -> None:
        """
        ---- Summary ----
        Method to type a symbol (µ, a superscript -1, ...) into the answer box at the
        cursor when a question is waiting for an answer, or, while a table is open,
        into the cell last typed in.

        ---- Inputs ----
        symbol : str
            The characters to add.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Adds text to the answer box or the cell (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        AnswerTable.symbol_inserter
        """

        if self._is_table_shown:
            self._table.symbol_inserter(symbol)
            return
        if self._is_waiting:
            self._entry.insert('insert', symbol)
        self._entry.focus_set()

    # ---- _table_closer ---------------------------------------------------------------
    def _table_closer(self) -> None:
        """
        ---- Summary ----
        Method to close the open table once the program has read it. A table it was
        opened over comes back as it was typed, shown while its step is open.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the table and the layout of the open step (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _table_layout_setter
        _table_step_follower
        AnswerTable.rows_setter
        table_texts_filler
        """

        self._is_table_left = False
        if not self._table_stack:
            self._table_shown = self._table_step = None
            self._table_layout_setter(False)
            return
        table, texts, self._table_step = self._table_stack.pop()
        self._table_shown = table
        self._table.rows_setter(table_texts_filler(table, texts))
        self._table_step_follower()

    # ---- _table_layout_setter --------------------------------------------------------
    def _table_layout_setter(self, is_shown: bool) -> None:
        """
        ---- Summary ----
        Method to open or close the table in the open step. Open, it fills the step
        under a few lines of its messages, which keep the newest lines in sight and
        scroll, and the question's Confirm button sits under it; closed, the messages
        take the room again.

        ---- Inputs ----
        is_shown : bool
            True to open the table, False to close it.

        ---- Globals read ----
        TABLE_HINT, TABLE_TERMINAL_LINES, TERMINAL_LINES (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the layout of the open step (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _keys_shower
        """

        if is_shown == self._is_table_shown:
            return
        self._is_table_shown = is_shown
        if is_shown:
            # Packed after the answers, the table takes the room the few lines of text
            # leave.
            self._text.configure(height=TABLE_TERMINAL_LINES)
            self._text_box.pack_configure(expand=False)
            self._table.frame.pack(side='bottom',
                                   fill='both',
                                   expand=True,
                                   after=self._bottom,
                                   )
            if self._is_waiting:
                self._hint.configure(text=TABLE_HINT)
        else:
            self._table.frame.pack_forget()
            self._text.configure(height=TERMINAL_LINES)
            self._text_box.pack_configure(expand=True)
        self._keys_shower()
        self._text.see('end')

    # ---- _table_opener ---------------------------------------------------------------
    def _table_opener(self, table: dict) -> None:
        """
        ---- Summary ----
        Method to open a table in the step open in the guide, which it then belongs
        to. A table already open is kept as typed under it; a table of a kind left
        for another step before opens as it was left.

        ---- Inputs ----
        table : dict
            The table to show (table_rows, DATA_FORMAT.md).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the table and the layout of the open step (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _table_layout_setter
        AnswerTable.rows_setter
        AnswerTable.texts_reader
        table_texts_filler
        """

        if self._table_shown is not None:
            self._table_stack.append((self._table_shown,
                                      self._table.texts_reader(),
                                      self._table_step,
                                      ),
                                     )
        guide = self._guide
        self._table_step = guide.shown if guide.shown is not None else guide.current
        self._table_shown = table
        self._is_table_left = False
        left = self._left_texts.pop(table.get('kind') or '', None)
        self._table.rows_setter(table if left is None else table_texts_filler(table,
                                                                              left,
                                                                              ),
                                )
        self._table_layout_setter(True)

    # ---- _table_step_follower --------------------------------------------------------
    def _table_step_follower(self) -> None:
        """
        ---- Summary ----
        Method to keep the open table with its step as the guide changes: shown while
        its step is open. When another step is opened from the step the program waits
        at, the table is put away as typed and comes back with its step. When it was
        opened from the View box (Edit ODs, Edit labels) and another step is opened,
        it is taken as it is, unchecked, and kept to open again as it was left.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the layout of the open step and may wake the question thread
        (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _click_sign_starter
        _pane_writer
        _table_layout_setter
        AnswerTable.texts_reader
        """

        if self._table_shown is None or self._is_table_left:
            return
        guide = self._guide
        open_step = guide.shown if guide.shown is not None else guide.current
        if open_step == self._table_step:
            self._table_layout_setter(True)
            return
        if self._table_step == guide.current or not self._is_waiting:
            self._table_layout_setter(False)
            return

        # ---- 1 Left from the View box: taken as it is --------------------------------
        self._left_texts[self._table_shown.get('kind') or ''] = self._table.texts_reader()
        self._is_table_left = True
        self._is_waiting = False
        self._table_layout_setter(False)
        self._pane_writer('→ Kept as it is\n', 'answer')
        self._text.mark_set('since', 'end-1c')
        self._answers.put('')
        self._click_sign_starter()

    # ---- _time_clicker ---------------------------------------------------------------
    def _time_clicker(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to act on a click on the plot of a file: an arrow beside a panel moves
        the panel; an edge under the mouse is taken, to be dragged; otherwise, while the question waiting can be answered
        with a drag, the drag starts here. Its answer replaces what was in the answer
        box, can still be edited, and is accepted with Enter.

        ---- Inputs ----
        event : Any
            The Tk click event.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the text of the answer box or starts a drag (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _band_drawer
        _panel_arrow_clicker
        pointed_time_finder
        """

        self._drag_start = None
        if self._panel_arrow_clicker(event):
            return
        if self._edges.press_handler(event):
            return
        if not (self._time_kind and self._is_waiting):
            return
        if (self._picture_box is None
            or self._shown_axis is None
            or self._index >= self._file_count
            ):
            return  # only the plot of a file has the times the answer is read from
        time_min = pointed_time_finder(event.x,
                                       event.y,
                                       self._picture_box,
                                       self._shown_axis,
                                       )
        if time_min is None or self._time_kind != 'span':
            return
        self._drag_start = (float(event.x), time_min)
        self._band_drawer(event.x)

    # ---- _time_line_drawer -----------------------------------------------------------
    def _time_line_drawer(self) -> None:
        """
        ---- Summary ----
        Method to draw a vertical line over the panels where the mouse is, with the
        time it points at beside it. Nothing is drawn when the mouse is off the time
        axis or the picture has none.

        ---- Inputs ----
        None.

        ---- Globals read ----
        POINTER_COLOUR (module constant).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Draws on the plot area (side effect).

        ---- Equations ----
        The line runs from the top of the first panel to the bottom of the last:
        y = picture top + (1 - fraction from the bottom) * picture height.

        ---- Helpers ----
        pointed_time_finder
        """

        self._canvas.delete('pointer')
        if (self._pointer is None
            or self._picture_box is None
            or self._shown_axis is None
            ):
            return
        x, y = self._pointer
        axis = self._shown_axis
        time_min = pointed_time_finder(x, y, self._picture_box, axis)
        if time_min is None:
            return
        _, top, _, height = self._picture_box
        line_top = top + (1.0 - axis.top) * height
        line_bottom = top + (1.0 - axis.bottom) * height
        self._canvas.create_line(x,
                                 line_top,
                                 x,
                                 line_bottom,
                                 fill=POINTER_COLOUR,
                                 width=1,
                                 tags='pointer',
                                 )
        # the label sits right of the line, or left of it near the right edge
        is_near_edge = x + 90 > self._canvas.winfo_width()
        text = self._canvas.create_text(x - 6 if is_near_edge else x + 6,
                                        line_top + 4,
                                        text=f'{time_min:.2f} min',
                                        anchor='ne' if is_near_edge else 'nw',
                                        fill=POINTER_COLOUR,
                                        font=(self._family, 10, 'bold'),
                                        tags='pointer',
                                        )
        left, upper, right, lower = self._canvas.bbox(text)
        back = self._canvas.create_rectangle(left - 3,
                                             upper - 1,
                                             right + 3,
                                             lower + 1,
                                             fill='white',
                                             outline=POINTER_COLOUR,
                                             tags='pointer',
                                             )
        self._canvas.tag_raise(text, back)

    # ---- _typed_edge_taker -----------------------------------------------------------
    def _typed_edge_taker(self, key: str, value: float) -> None:
        """
        ---- Summary ----
        Method to take a number typed in the edges row: the edge moves there (on every
        file when "Apply to all" is ticked), within the limits of each file, and the row
        shows where it went.

        ---- Inputs ----
        key : str
            The field typed in.
        value : float
            The number typed.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Moves the edge and redraws (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _edges_refresher
        """

        self._edges.field_setter(key, value)
        self._edges_refresher()

    # ---- _wheel_turner ---------------------------------------------------------------
    def _wheel_turner(self, step: int) -> None:
        """
        ---- Summary ----
        Method to turn the wheel of the "Plotting data …" sign one spoke on: the leading
        spoke dark, the ones behind it fading. It calls itself again while the sign is
        on the plot, and stops once the plot area was drawn again without it.

        ---- Inputs ----
        step : int
            The spoke that leads, from 0.

        ---- Globals read ----
        SIGN_BACKGROUND, SIGN_EDGE, SIGN_TEXT, WHEEL_SPOKES, WHEEL_STEP_MS (module
        constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Recolours the spokes and asks Tk to call it again (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        canvas = self._canvas
        try:
            if not canvas.find_withtag('drawing_sign'):
                self._is_wheel_turning = False
                return
            for index in range(WHEEL_SPOKES):
                behind = (step - index) % WHEEL_SPOKES
                colour = (SIGN_TEXT
                          if behind == 0
                          else SIGN_EDGE if behind < WHEEL_SPOKES // 3 else SIGN_BACKGROUND
                          )
                canvas.itemconfigure(f'wheel_spoke_{index}', fill=colour)
            self._root.after(WHEEL_STEP_MS,
                             self._wheel_turner,
                             (step + 1) % WHEEL_SPOKES,
                             )
        except self._tk.TclError:  # the window was closed while the wheel turned
            self._is_wheel_turning = False

    # ---- _widgets_builder ------------------------------------------------------------
    def _widgets_builder(self) -> None:
        """
        ---- Summary ----
        Method to build the guide on the left: the lines of the steps and the card of
        the open step, with its messages, the table (hidden until a table is asked
        for), the answers, the symbols (shown where text is typed), the hint and the
        Help button (greyed out until the Help box is made); and on the right the file
        controls, under them the plot with the overlay of its edges, then the settings
        strip and the edges row (hidden until edges are dragged).

        ---- Inputs ----
        None.

        ---- Globals read ----
        MONO_FONTS, SANS_FONTS and the colour constants (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _answer_sender
        _clicked_answer_sender
        _closing_handler
        _confirm_sender
        _edges_refresher
        _every_file_taker
        _file_follower
        _guide_line_clicker
        _history_stepper
        _message_shower
        _nav_state_setter
        _navigator
        _pointer_mover
        _resizer
        _screen_filler
        _step_taker
        _strip_change_teller
        _symbol_inserter
        _time_clicker
        _typed_edge_taker
        AnswerArea
        AnswerTable
        EdgeOverlay
        EdgeRow
        GuidePanel
        SettingsStrip
        """

        tk = self._tk
        from tkinter import font as tkfont, ttk
        root = self._root
        self._screen_filler()
        families = set(tkfont.families(root))
        self._family = next((f for f in MONO_FONTS if f in families), 'Courier')
        # the stage names and the sign over the plot in a plain font
        self._sign_family = next((f for f in SANS_FONTS if f in families),
                                 self._family,
                                 )
        self._size = GUIDE_FONT_POINTS
        panes = ttk.PanedWindow(root, orient='horizontal')
        panes.pack(fill='both', expand=True)

        # ---- 1 The guide on the left -------------------------------------------------
        # The lines of the steps, with the card of the open step under its line: the
        # step's note (an earlier step), its messages and question, a table when one
        # is asked for, then the answers, the symbols, the hint and Help.
        left = tk.Frame(panes, bg=TERMINAL_BACKGROUND)
        self._guide_panel = GuidePanel(tk,
                                       left,
                                       self._family,
                                       self._size,
                                       self._guide_line_clicker,
                                       self._sign_family,
                                       )
        self._guide_panel.frame.pack(fill='both', expand=True)
        card = self._guide_panel.card
        self._guide_note = tk.Label(card,
                                    text='',
                                    wraplength=520,
                                    justify='left',
                                    bg=CARD_BACKGROUND,
                                    fg=ANSWER_COLOUR,
                                    anchor='w',
                                    font=(self._family, self._size - 1),
                                    )
        self._text_box = tk.Frame(card, bg=CARD_BACKGROUND)
        self._text = tk.Text(self._text_box,
                             bg=CARD_BACKGROUND,
                             fg=TERMINAL_TEXT,
                             insertbackground=TERMINAL_TEXT,
                             font=(self._family, self._size),
                             wrap='word',
                             state='disabled',
                             borderwidth=0,
                             highlightthickness=0,
                             padx=10,
                             pady=8,
                             width=70,
                             height=TERMINAL_LINES,
                             )
        # what was said before the last answer folds away at the next question
        self._text.tag_configure('folded', elide=True)
        self._text.mark_set('since', '1.0')
        self._text.mark_gravity('since', 'left')
        scroll = ttk.Scrollbar(self._text_box, command=self._text.yview)
        self._text.configure(yscrollcommand=scroll.set)
        bottom = tk.Frame(card, bg=CARD_BACKGROUND)
        self._area = AnswerArea(tk,
                                bottom,
                                self._family,
                                self._size,
                                {'background': CARD_BACKGROUND,
                                 'text': TERMINAL_TEXT,
                                 'cell': ENTRY_BACKGROUND,
                                 },
                                self._clicked_answer_sender,
                                self._answer_sender,
                                self._confirm_sender,
                                )
        self._area.frame.pack(fill='x', padx=10, pady=(4, 0))
        self._entry = self._area.entry
        self._confirm = self._area.confirm
        self._hint = tk.Label(bottom,
                              text='Starting ...',
                              wraplength=520,
                              justify='left',
                              bg=CARD_BACKGROUND,
                              fg='#a0a0a0',
                              anchor='w',
                              font=(self._family, 10),
                              )
        symbol_family = next((f for f in SYMBOL_FONTS if f in families), self._family)
        keys = tk.Frame(bottom, bg=CARD_BACKGROUND)
        self._keys = keys  # shown only where text is typed (_keys_shower)
        tk.Label(keys,
                 text='Symbols:',
                 bg=CARD_BACKGROUND,
                 fg='#808080',
                 font=(self._family, 9),
                 ).pack(side='left', padx=(10, 6))
        for symbol in SYMBOLS:
            key = tk.Label(keys,
                           text=symbol,
                           bg='#333333',
                           fg=TERMINAL_TEXT,
                           font=(symbol_family, self._size),
                           padx=5,
                           cursor='hand2',
                           )
            key.pack(side='left', padx=1)
            key.bind('<Button-1>', lambda e, text=symbol: self._symbol_inserter(text))
            key.bind('<Enter>', lambda e, widget=key: widget.configure(bg='#4a4a4a'))
            key.bind('<Leave>', lambda e, widget=key: widget.configure(bg='#333333'))
        self._hint.pack(fill='x', padx=10, pady=(4, 0))
        row = tk.Frame(bottom, bg=CARD_BACKGROUND)
        # greyed out until the Help box is made
        self._help_button = ttk.Button(row, text='Help', width=6, state='disabled')
        self._help_button.pack(side='right', padx=(0, 10))
        row.pack(fill='x', pady=(2, 8))
        bottom.pack(side='bottom', fill='x')
        self._bottom = bottom
        self._table = AnswerTable(tk,
                                  ttk,
                                  card,
                                  (self._family, self._size),
                                  {'background': CARD_BACKGROUND,
                                   'text': TERMINAL_TEXT,
                                   'cell': ENTRY_BACKGROUND,
                                   'edge': ANSWER_COLOUR,
                                   },
                                  self._confirm.focus_set,
                                  self._file_follower,
                                  next((f for f in SANS_FONTS if f in families), None),
                                  )
        scroll.pack(side='right', fill='y')
        self._text.pack(side='left', fill='both', expand=True)
        self._text_box.pack(side='top', fill='both', expand=True)
        self._guide_panel.rows_drawer(self._guide.row_lister())
        panes.add(left, weight=1)
        self._entry.bind('<Return>', self._answer_sender)
        self._entry.bind('<Up>', lambda e: self._history_stepper(-1))
        self._entry.bind('<Down>', lambda e: self._history_stepper(1))

        # ---- 2 The plot on the right -------------------------------------------------
        right = tk.Frame(panes, bg=PLOT_BACKGROUND)
        controls = tk.Frame(right,
                            bg=PLOT_BACKGROUND,
                            )  # the file arrows, above the boxes and the plot
        controls.pack(side='top', pady=(8, 0))
        self._strip = SettingsStrip(tk,
                                    ttk,
                                    right,
                                    PLOT_BACKGROUND,
                                    self._strip_change_teller,
                                    )
        self._strip.frame.pack(side='top', pady=(6, 0))
        # the rows of the edges sit in the Time regions box, only while edges are
        # dragged; the second for a step with two rows of edges
        self._edge_row = EdgeRow(tk,
                                 self._strip.time_box,
                                 PLOT_BACKGROUND,
                                 self._typed_edge_taker,
                                 self._every_file_taker,
                                 self._area.focuser,
                                 on_tick=self._edge_tick_taker,
                                 )
        self._second_row = EdgeRow(tk,
                                   self._strip.time_box,
                                   PLOT_BACKGROUND,
                                   self._typed_edge_taker,
                                   lambda is_ticked: self._every_file_taker(is_ticked,
                                                                            'second',
                                                                            ),
                                   self._area.focuser,
                                   on_tick=self._edge_tick_taker,
                                   )
        # the "Apply to all" line of a step whose rows have switches of
        # their own, with the step's toggles
        self._options_row = EdgeRow(tk,
                                    self._strip.time_box,
                                    PLOT_BACKGROUND,
                                    self._typed_edge_taker,
                                    lambda is_ticked: self._every_file_taker(is_ticked,
                                                                             'options',
                                                                             ),
                                    self._area.focuser,
                                    on_toggle=self._edge_toggle_taker,
                                    )
        self._help = tk.Label(right,
                              text='',
                              bg=PLOT_BACKGROUND,
                              fg='#404040',
                              wraplength=600,
                              justify='center',
                              )
        self._help.pack(side='bottom', fill='x', pady=(0, 2))
        self._status = tk.Label(right,
                                text='',
                                bg=PLOT_BACKGROUND,
                                fg='#8a5a00',
                                wraplength=600,
                                justify='center',
                                )
        self._status.pack(side='bottom', fill='x')
        self._canvas = tk.Canvas(right,
                                 bg='white',
                                 highlightthickness=0,
                                 )
        self._canvas.pack(side='top', fill='both', expand=True, padx=8, pady=8)
        self._edges = EdgeOverlay(tk,
                                  self._canvas,
                                  self._family,
                                  self._edges_refresher,
                                  on_untick=self._every_file_unticker,
                                  )
        self._previous_button = ttk.Button(controls,
                                           text='< Prev',
                                           width=7,
                                           command=lambda: self._step_taker(-1),
                                           )
        self._combo = ttk.Combobox(controls, state='disabled', width=42)
        self._next_button = ttk.Button(controls,
                                       text='Next >',
                                       width=7,
                                       command=lambda: self._step_taker(1),
                                       )
        self._counter = tk.Label(controls, text='', bg=PLOT_BACKGROUND, width=9)
        self._previous_button.pack(side='left', padx=4)
        self._combo.pack(side='left', padx=4)
        self._next_button.pack(side='left', padx=4)
        self._counter.pack(side='left', padx=4)
        panes.add(right, weight=2)
        self._combo.bind('<<ComboboxSelected>>',
                         lambda e: self._navigator(self._combo.current(), True),
                         )
        self._canvas.bind('<Configure>', self._resizer)
        self._canvas.bind('<Motion>', self._pointer_mover)
        self._canvas.bind('<Leave>', lambda e: self._pointer_mover(None))
        self._canvas.bind('<Button-1>', self._time_clicker)
        self._canvas.bind('<B1-Motion>', self._dragger)
        self._canvas.bind('<ButtonRelease-1>', self._drag_ender)
        root.bind_all('<Prior>', lambda e: self._step_taker(-1))
        root.bind_all('<Next>', lambda e: self._step_taker(1))
        root.protocol('WM_DELETE_WINDOW', self._closing_handler)
        if sys.platform == 'darwin':  # Cmd+Q and Quit in the menu ask first as well
            root.createcommand('tk::mac::Quit', self._closing_handler)
        self._nav_state_setter(False)
        self._message_shower('The plots appear here once the experiment browser '
                             'starts.',
                             )

    # ---- _window_raiser --------------------------------------------------------------
    def _window_raiser(self) -> None:
        """
        ---- Summary ----
        Helper method to bring the window to the front with the keyboard in the answer
        box. A window started by the launcher otherwise opens behind other windows on
        macOS, where the answers typed would go nowhere.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Raises and focuses the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        try:
            self._root.lift()
            self._root.attributes('-topmost', True)
            self._root.after(500, lambda: self._root.attributes('-topmost', False))
            self._root.focus_force()
            self._area.focuser()
        except Exception:  # a window that stays behind still works
            pass

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- answer_requester ------------------------------------------------------------
    def answer_requester(self, request: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Method to say how the question just asked is answered, so the open step shows
        its answers as buttons. It is called from the question thread.

        ---- Inputs ----
        request : Dict[str, Any]
            {'kind', 'options', 'default', 'value'} (AnswerArea.request_shower).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the request for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('ask', dict(request)))

    # ---- drawing_sign_shower ---------------------------------------------------------
    def drawing_sign_shower(self) -> None:
        """
        ---- Summary ----
        Method to put the "Plotting data …" sign on the plot while the program makes
        pictures of its own (the combined figures, the components found from the
        data). The sign goes when the next picture or preview is shown, or the next
        question is asked.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the sign for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('busy',))

    # ---- edges_hider -----------------------------------------------------------------
    def edges_hider(self) -> None:
        """
        ---- Summary ----
        Method to take the edges off the plot and the edges row out of the strip, once
        the choice made with them is read. It is called from the question thread.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the change for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('edges', None))

    # ---- edges_reader ----------------------------------------------------------------
    def edges_reader(self) -> Dict[str, Dict[str, float]]:
        """
        ---- Summary ----
        Method to give the values of the edges as the user has set them. It is meant
        to be called once the user has answered the instruction given after
        edges_shower, which is when the window is sure to hold the choice that was
        sent.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Dict[str, Dict[str, float]]
            {file name: {field: value}} (EdgeChoice in DATA_FORMAT.md); empty when no
            choice is being made.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self._edges.values_reader()

    # ---- edges_shower ----------------------------------------------------------------
    def edges_shower(self, choice: EdgeChoice) -> None:
        """
        ---- Summary ----
        Method to put edges on the plot of every file, to be dragged, with a row of
        typing boxes for them in the strip. It is called from the question thread; the
        rules in the choice run on the window thread.

        ---- Inputs ----
        choice : EdgeChoice
            The fields, the starting values and the rules (DATA_FORMAT.md).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the choice for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('edges', choice))

    # ---- extra_publisher -------------------------------------------------------------
    def extra_publisher(self, title: str, png: bytes, is_shown: bool = True) -> None:
        """
        ---- Summary ----
        Method to show one more picture, such as the components found by the principal
        component analysis, in the selector after the files. The files and the other
        extra pictures stay (a picture with the same title is replaced), and the extra
        pictures go when the next preview is drawn.

        ---- Inputs ----
        title : str
            Name shown in the selector.
        png : bytes
            The picture.
        is_shown : bool
            True to switch the window to the picture; False only lists it.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the picture for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('extra', title, png, is_shown))

    # ---- formula_sender --------------------------------------------------------------
    def formula_sender(self, formula: str) -> None:
        """
        ---- Summary ----
        Method to queue a formula from the program thread, drawn as a textbook writes
        it on a line of its own in the guide, after the text printed before it.

        ---- Inputs ----
        formula : str
            The formula in matplotlib's maths text (viewer_strip.PSI_FORMULA).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the formula (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('formula', formula))

    # ---- input_reader ----------------------------------------------------------------
    def input_reader(self, prompt: Any = '') -> str:
        """
        ---- Summary ----
        Method that replaces the built-in input while the window is open: it shows the
        prompt in the terminal and waits for the answer typed in the answer box. A
        change made in the settings strip meanwhile is handed to the program's listener
        and the question goes on waiting. Other threads still use the real input.

        ---- Inputs ----
        prompt : Any
            The prompt text, for example "   > ".

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            The typed answer. Raises EOFError when the window is closed.

        ---- Globals mutated ----
        None. Waits for the user and runs the strip listener (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _strip_change_runner
        """

        if threading.current_thread() is not self.logic_thread:
            return self._real_input(prompt)
        self._events.put(('prompt', str(prompt)))
        while True:
            answer = self._answers.get()
            if answer is _CLOSED:
                raise EOFError
            if isinstance(answer, str):
                if self._answer_listener is not None:
                    self._answer_listener()
                return answer
            self._strip_change_runner(answer[1], prompt)

    # ---- output_capturer -------------------------------------------------------------
    @contextmanager
    def output_capturer(self) -> Iterator[CapturedOutput]:
        """
        ---- Summary ----
        Method to capture what the current thread prints (the preview thread), without
        touching the terminal or the log file.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Iterator[CapturedOutput]
            The buffer the output is collected in, with the warnings kept apart.

        ---- Globals mutated ----
        None. Captures the output of the current thread (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        output_capturer
        """

        with output_capturer() as buffer:
            yield buffer

    # ---- pictures_publisher ----------------------------------------------------------
    def pictures_publisher(self, pictures: List[Tuple[str, bytes]]) -> None:
        """
        ---- Summary ----
        Method to show finished pictures (the multi-experiment figures) instead of the
        files: the selector then lists the pictures by title.

        ---- Inputs ----
        pictures : List[Tuple[str, bytes]]
            [(title, PNG bytes)] in the order they are listed.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the pictures for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('pictures', list(pictures)))

    # ---- run -------------------------------------------------------------------------
    def run(self) -> int:
        """
        ---- Summary ----
        Method to run the program in the window: take over the output streams and the
        input, start the program thread, and run the window until it is closed.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        int
            The exit code of the program (1 when the window was closed before it
            finished).

        ---- Globals mutated ----
        None. Replaces sys.stdout, sys.stderr and the built-in input while the window
        runs, registers the window with the questions (for a time, for how each is
        answered and for the steps of the guide), and restores them all afterwards
        (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _drain_runner
        _logic_runner
        _opened_teller
        _window_raiser
        input_reader
        text_sender
        """

        global _active_gui
        self._real_input = builtins.input
        original = (sys.stdout, sys.stderr)
        def owner() -> Optional[threading.Thread]:
            return None if self._is_destroyed else self.logic_thread
        sys.stdout = OutputRouter(original[0], self.text_sender, 'out', owner)
        sys.stderr = OutputRouter(original[1], self.text_sender, 'err', owner)
        builtins.input = self.input_reader
        time_request_setter(self.time_reader_setter)
        answer_request_setter(self.answer_requester)
        guide_step_setter(self.step_teller)
        _active_gui = self
        self.logic_thread = threading.Thread(target=self._logic_runner,
                                             name='program',
                                             daemon=True,
                                             )
        try:
            self.logic_thread.start()
            self._root.after(25, self._drain_runner)
            self._root.after(100, self._window_raiser)
            self._root.after(100, self._opened_teller)
            try:
                self._root.mainloop()
            except KeyboardInterrupt:
                self._is_destroyed = True
                self._answers.put(_CLOSED)
            self.logic_thread.join(timeout=3)
        finally:
            sys.stdout, sys.stderr = original
            builtins.input = self._real_input
            time_request_setter(None)
            answer_request_setter(None)
            guide_step_setter(None)
            _active_gui = None
        return self.exit_code

    # ---- saved_plot_publisher --------------------------------------------------------
    def saved_plot_publisher(self, name: str, png: bytes) -> None:
        """
        ---- Summary ----
        Method to show the plot saved for a file, once the questions about each file
        are over: it takes the place of the file's preview, so the file shows its saved
        plot in the later steps. It is called from the question thread, after
        window_closer.

        ---- Inputs ----
        name : str
            Name of the file.
        png : bytes
            Picture of the saved plot.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the picture for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('saved', name, png))

    # ---- session_attacher ------------------------------------------------------------
    def session_attacher(self, session: ViewerSession) -> None:
        """
        ---- Summary ----
        Method to give the window the files of the browser session, which fills the
        file selector and starts the preview thread.

        ---- Inputs ----
        session : ViewerSession
            The browser session.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the session for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('session', session))

    # ---- spec_publisher --------------------------------------------------------------
    def spec_publisher(self, spec: PreviewSpec, name: Optional[str]) -> None:
        """
        ---- Summary ----
        Method to give the window new settings: every file is drawn again with them.

        ---- Inputs ----
        spec : PreviewSpec
            The settings to draw with.
        name : Optional[str]
            File to show first, or None to stay on the current file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the settings for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('spec', spec, name))

    # ---- step_teller -----------------------------------------------------------------
    def step_teller(self, key: str) -> None:
        """
        ---- Summary ----
        Method to say which step of the guide starts, so the guide opens it. It is
        called from the question thread.

        ---- Inputs ----
        key : str
            Key of the step (viewer_guide.GUIDE_KEYS).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the step for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('step', key))

    # ---- strip_choices_setter --------------------------------------------------------
    def strip_choices_setter(self,
                             spectra: List[str],
                             has_percent: bool,
                             has_od: bool,
                             has_baseline: bool = False,
                             has_psi: bool = False,
                             ) -> None:
        """
        ---- Summary ----
        Method to tell the boxes above the plot what they offer: the spectrometers of
        the "Spectra" drop-down, whether % oxidised is in "Haems as", whether per OD is
        offered, whether % of baseline is in "OCR as", and whether Δψ can be ticked.

        ---- Inputs ----
        spectra : List[str]
            The spectrometers every file has.
        has_percent : bool
            True when at least one file has both regions.
        has_od : bool
            True when OD values were entered.
        has_baseline : bool
            True when the averaging windows are set up.
        has_psi : bool
            True when Δψ can be worked out.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the choices for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('strip_choices',
                          list(spectra),
                          bool(has_percent),
                          bool(has_od),
                          bool(has_baseline),
                          bool(has_psi),
                          ),
                         )

    # ---- strip_fits_setter -----------------------------------------------------------
    def strip_fits_setter(self, fits: Dict[str, str]) -> None:
        """
        ---- Summary ----
        Method to give the settings strip the fits listed in its drop-down.

        ---- Inputs ----
        fits : Dict[str, str]
            {file name: name shown} of the fits, in order
            (spectral_decomposer.fit_titles_lister).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the list for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('strip_fits', dict(fits)))

    # ---- strip_library_setter --------------------------------------------------------
    def strip_library_setter(self, haems: List[Dict[str, str]]) -> None:
        """
        ---- Summary ----
        Method to give the settings strip the library haems it shows a tick box for
        under Build a fit.

        ---- Inputs ----
        haems : List[Dict[str, str]]
            The library, as spectral_decomposer.library_haems_lister gives it.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the list for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('strip_library', [dict(item) for item in haems]))

    # ---- strip_listener_setter -------------------------------------------------------
    def strip_listener_setter(self,
                              listener: Optional[Callable[[Dict[str, Any]], None]],
                              ) -> None:
        """
        ---- Summary ----
        Method to register the function that is told what the user changes in the
        settings strip, or None to stop listening.

        ---- Inputs ----
        listener : Optional[Callable[[Dict[str, Any]], None]]
            Called with {name: new value} of the values changed at once, on the
            program thread while a question waits (a change made while the program is
            busy is taken when the next question is asked). What it prints shows under
            the question, which then goes on waiting.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the function on the instance (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._strip_listener = listener

    # ---- answer_listener_setter ------------------------------------------------------
    def answer_listener_setter(self, listener: Optional[Callable[[], None]]) -> None:
        """
        ---- Summary ----
        Method to register the function run just before an answer is handed to the
        question that waits (a tab of the Time regions box left open is used then), or
        None for none.

        ---- Inputs ----
        listener : Optional[Callable[[], None]]
            Called on the program thread with no arguments; what it prints shows above
            the answer.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Keeps the function on the instance (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._answer_listener = listener

    # ---- strip_reader ----------------------------------------------------------------
    def strip_reader(self) -> Dict[str, Any]:
        """
        ---- Summary ----
        Method to give the values the settings strip shows now.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Dict[str, Any]
            The strip values (DATA_FORMAT.md).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self._strip.values_reader()

    # ---- strip_setter ----------------------------------------------------------------
    def strip_setter(self, values: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Method to show values in the settings strip. The listener is not told, as the
        program made the change itself.

        ---- Inputs ----
        values : Dict[str, Any]
            Some or all of the strip values (DATA_FORMAT.md).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing. Raises ValueError for a value the strip cannot show.

        ---- Globals mutated ----
        None. Queues the values for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        strip_values_checker
        """

        strip_values_checker(values)
        self._events.put(('strip', dict(values)))

    # ---- strip_state_setter ----------------------------------------------------------
    def strip_state_setter(self, is_enabled: bool) -> None:
        """
        ---- Summary ----
        Method to let the user change the settings strip, or grey it out while what it
        shows is not being used. It starts greyed out.

        ---- Inputs ----
        is_enabled : bool
            True to let the user change it, False to grey it out.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the change for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('strip_state', bool(is_enabled)))

    # ---- table_hider -----------------------------------------------------------------
    def table_hider(self) -> None:
        """
        ---- Summary ----
        Method to take the table away again and bring back the answer box. What was
        typed can still be read with table_reader.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the change for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('table_hide',))

    # ---- table_leave_taker -----------------------------------------------------------
    def table_leave_taker(self) -> bool:
        """
        ---- Summary ----
        Method to say whether the table that waits was left for another step, so the
        program takes it as it is, without checking it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when the table was left for another step.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self._is_table_left

    # ---- table_reader ----------------------------------------------------------------
    def table_reader(self) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
        """
        ---- Summary ----
        Method to give what the table holds. It is meant to be called once Confirm has
        been pressed for the instruction given after table_shower, which is when the
        table is sure to hold the rows that were sent.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]
            (the values row by row, as AnswerTable.values_reader gives them; the cells
            that cannot be used or are needed and empty, as
            AnswerTable.problems_lister gives them).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        AnswerTable.problems_lister
        AnswerTable.values_reader
        """

        return self._table.values_reader(), self._table.problems_lister()

    # ---- table_shower ----------------------------------------------------------------
    def table_shower(self, table: dict) -> None:
        """
        ---- Summary ----
        Method to open a table on the terminal side, in place of most of the text, with
        Confirm in place of the answer box.

        ---- Inputs ----
        table : dict
            The table to show (table_rows, DATA_FORMAT.md).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the table for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('table_show', table))

    # ---- text_sender -----------------------------------------------------------------
    def text_sender(self, text: str, kind: str) -> None:
        """
        ---- Summary ----
        Method to queue text from the program thread for the terminal.

        ---- Inputs ----
        text : str
            Text as printed.
        kind : str
            'out' or 'err'.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the text (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('text', text, kind))

    # ---- time_reader_setter ----------------------------------------------------------
    def time_reader_setter(self,
                           kind: Optional[str],
                           reader: Optional[Callable],
                           ) -> None:
        """
        ---- Summary ----
        Method to say that the question being asked can be answered with the mouse, so
        a drag across the plot of a file writes the answer it gives into the answer
        box, or that it no longer can. It is called from the question thread.

        ---- Inputs ----
        kind : Optional[str]
            'span' (a drag), or None once the question has its answer.
        reader : Optional[Callable]
            Turns the drag into the answer: reader(file name, start_min, end_min); None
            with kind None. It is called on the window thread.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the change for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('time', kind, reader))

    # ---- window_closer ---------------------------------------------------------------
    def window_closer(self) -> None:
        """
        ---- Summary ----
        Method to end the previews when the browser steps are over: the preview thread
        is stopped (so it cannot clash with the processing that follows) and the file
        controls are switched off. The pictures drawn with the last settings stay
        until the saved plot of each file takes their place (saved_plot_publisher); a
        file without one says its plot was not saved with them.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stops the preview thread and queues the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._renderer is not None:
            self._renderer.stopper()
        self._events.put(('closed',))


# ---- GUI HELPERS ---------------------------------------------------------------------


# ---- _hint_chooser -------------------------------------------------------------------
def _hint_chooser(kind: Optional[str],
                  time_kind: Optional[str],
                  is_edged: bool = False,
                  ) -> str:
    """
    ---- Summary ----
    Helper function to choose the hint shown under the answers: what to do for the
    question waiting, with the mouse or the keyboard.

    ---- Inputs ----
    kind : Optional[str]
        How the question is answered ('continue', 'yesno', 'choice', 'multi',
        'number', 'text', 'folder', 'confirm'), or None before the first question.
    time_kind : Optional[str]
        'span' (a drag gives the answer) or None.
    is_edged : bool
        True while edges are dragged on the plot.

    ---- Globals read ----
    CLICK_HINT, EDGES_HINT, FOLDER_HINT, NAME_HINT, NUMBER_HINT, SPAN_HINT, TABLE_HINT
    (module constants).

    ---- Outputs ----
    str
        The hint.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if is_edged:
        return EDGES_HINT
    if time_kind == 'span':
        return SPAN_HINT
    if kind == 'number':
        return NUMBER_HINT
    if kind == 'text':
        return NAME_HINT
    if kind == 'folder':
        return FOLDER_HINT
    if kind == 'confirm':
        return TABLE_HINT
    return CLICK_HINT


# ---- active_gui_getter ---------------------------------------------------------------
def active_gui_getter() -> Optional[ViewerGui]:
    """
    ---- Summary ----
    Main function to give the browser window that is open, if any.

    ---- Inputs ----
    None.

    ---- Globals read ----
    _active_gui (module state).

    ---- Outputs ----
    Optional[ViewerGui]
        The open window, or None when none is open (outside a run).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return _active_gui


# ---- gui_runner ----------------------------------------------------------------------
def gui_runner(program: Callable[[], int], title: str) -> int:
    """
    ---- Summary ----
    Main function to run the whole program inside the browser window, which the program
    needs: nothing is run when the window cannot open.

    ---- Inputs ----
    program : Callable[[], int]
        The program; it asks the questions and returns its exit code.
    title : str
        Window title.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        The exit code of the program. Raises GuiUnavailableError, with the reason in
        plain words, when the window cannot open.

    ---- Globals mutated ----
    None. Opens the window and runs the program (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    ViewerGui
    window_opener
    """

    tk, root = window_opener()
    return ViewerGui(tk, root, program, title).run()


# ---- pointed_time_finder -------------------------------------------------------------
def pointed_time_finder(x: float,
                        y: float,
                        picture_box: Tuple[float, float, float, float],
                        time_axis: TimeAxis,
                        ) -> Optional[float]:
    """
    ---- Summary ----
    Main function to turn a point of the plot area into the time it points at on the
    time axis of the picture shown there.

    ---- Inputs ----
    x : float
        Distance of the point from the left edge of the plot area, in pixels.
    y : float
        Distance of the point from the top edge of the plot area, in pixels.
    picture_box : Tuple[float, float, float, float]
        (left, top, width, height) of the picture in the plot area, in pixels.
    time_axis : TimeAxis
        Where the time axis sits in the picture, and the times at its ends.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The time in minutes, or None when the point is not over the panels.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    across = (x - left) / width; up = 1 - (y - top) / height;
    time = start + (across - axis left) / (axis right - axis left) * (end - start).

    ---- Helpers ----
    None.
    """

    left, top, width, height = picture_box
    if width <= 0 or height <= 0 or time_axis.right <= time_axis.left:
        return None
    across = (x - left) / width
    up = 1.0 - (y - top) / height
    if not (time_axis.left <= across <= time_axis.right
            and time_axis.bottom <= up <= time_axis.top
            ):
        return None
    share = (across - time_axis.left) / (time_axis.right - time_axis.left)
    return time_axis.start_min + share * (time_axis.end_min - time_axis.start_min)


# ---- panel_arrow_finder --------------------------------------------------------------
def panel_arrow_finder(x: float,
                       y: float,
                       arrows: List[Tuple[str, int, float, float, float, float, bool]],
                       ) -> Optional[Tuple[str, int, bool]]:
    """
    ---- Summary ----
    Main function to find the arrow of a panel under a point of the plot area.

    ---- Inputs ----
    x : float
        Distance from the left edge of the plot area, in pixels.
    y : float
        Distance from the top edge of the plot area, in pixels.
    arrows : List[Tuple[str, int, float, float, float, float, bool]]
        The arrows, as panel_arrow_placer gives them.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Tuple[str, int, bool]]
        (key of the panel, -1 for up or 1 for down, whether the arrow can be used),
        or None when the point is on no arrow.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    On an arrow: left <= x <= right and top <= y <= bottom of its square.

    ---- Helpers ----
    None.
    """

    for key, step, x0, y0, x1, y1, is_usable in arrows:
        if x0 <= x <= x1 and y0 <= y <= y1:
            return key, step, is_usable
    return None


# ---- panel_arrow_placer --------------------------------------------------------------
def panel_arrow_placer(picture_box: Tuple[float, float, float, float],
                       time_axis: TimeAxis,
                       band_px: float,
                       ) -> List[Tuple[str, int, float, float, float, float, bool]]:
    """
    ---- Summary ----
    Main function to place an up and a down arrow left of each panel of a picture, in
    the room kept beside it: the up arrow just above the middle of the panel, the down
    arrow just under it. The up arrow of the top panel and the down arrow of the
    bottom one cannot be used.

    ---- Inputs ----
    picture_box : Tuple[float, float, float, float]
        (left, top, width, height) of the picture in the plot area, in pixels.
    time_axis : TimeAxis
        Where the panels sit in the picture (its panels, top first).
    band_px : float
        Width of the room kept left of the picture, in pixels.

    ---- Globals read ----
    PANEL_ARROW_SIZE_PX (module constant).

    ---- Outputs ----
    List[Tuple[str, int, float, float, float, float, bool]]
        For each arrow: the key of its panel, -1 for up or 1 for down, the left, top,
        right and bottom of its square in pixels, and whether it can be used.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    middle y = picture top + (1 - (panel bottom + panel top) / 2) x picture height;
    side = PANEL_ARROW_SIZE_PX, or half the height of the panel less 1 px when that is
    smaller; the squares are centred on picture left - band / 2, the up one from
    middle - 1 - side to middle - 1, the down one from middle + 1 to middle + 1 + side.

    ---- Helpers ----
    None.
    """

    left, top, _, height = picture_box
    centre = left - band_px / 2.0
    arrows = []
    for place, (key, bottom, panel_top) in enumerate(time_axis.panels):
        middle = top + (1.0 - (bottom + panel_top) / 2.0) * height
        side = min(float(PANEL_ARROW_SIZE_PX),
                   max((panel_top - bottom) * height / 2.0 - 1.0, 1.0),
                   )
        x0, x1 = centre - side / 2.0, centre + side / 2.0
        arrows.append((key, -1, x0, middle - 1.0 - side, x1, middle - 1.0, place > 0))
        arrows.append((key,
                       1,
                       x0,
                       middle + 1.0,
                       x1,
                       middle + 1.0 + side,
                       place < len(time_axis.panels) - 1,
                       ),
                      )
    return arrows


# ---- window_opener -------------------------------------------------------------------
def window_opener() -> Tuple[Any, Any]:
    """
    ---- Summary ----
    Main function to check that the browser window can open here and open its Tk root
    window.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MINIMUM_TK (module constant); os.environ["DISPLAY"] and
    os.environ["WAYLAND_DISPLAY"] (on Linux).

    ---- Outputs ----
    Tuple[Any, Any]
        (the tkinter module, the Tk root window). Raises GuiUnavailableError, with the
        reason and what to do in plain words, when the window cannot open.

    ---- Globals mutated ----
    None. On Windows, makes the text sharp and gives the program its own taskbar group;
    when Tk will not start, what it said goes to the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    details_writer
    """

    # ---- 1 Check that a window can open ----------------------------------------------
    is_linux = sys.platform.startswith('linux')
    try:
        import tkinter as tk
    except ImportError:
        fix = ('install it with "sudo apt install python3-tk"'
               if is_linux
               else 'install Python from python.org, which has it'
               )
        raise GuiUnavailableError(f'this Python has no Tkinter, which draws the '
                                  f'window; {fix}',
                                  )
    has_display = os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
    if is_linux and not has_display:
        raise GuiUnavailableError('there is no screen to show it on; start Portimao on '
                                  'a computer with a screen',
                                  )

    # ---- 2 Prepare Windows -----------------------------------------------------------
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # sharp text
            # own taskbar group, so the taskbar shows our icon, not Python's
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                'Portimao.ExperimentBrowser',
                )
        except Exception:
            pass

    # ---- 3 Open the root window ------------------------------------------------------
    if tk.TkVersion < MINIMUM_TK:
        raise GuiUnavailableError(f'this Python has Tk {tk.TkVersion:g}, which draws '
                                  f'blank windows; install Python from python.org',
                                  )
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        details_writer(f'Tk could not start: {exc}')
        again = ('install it again with "sudo apt install --reinstall python3-tk"'
                 if is_linux
                 else 'install Python from python.org again'
                 )
        raise GuiUnavailableError(f'Tk, which draws the window, would not start; '
                                  f'{again}',
                                  ) from exc
    return tk, root
