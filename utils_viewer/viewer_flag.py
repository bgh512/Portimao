"""
The developer's Flag button: a picture of the window, a comment and the log so far, saved
together in the inbox.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.run_logging import details_writer, run_log_path_getter
from utils_shared.user_notices import warning_shower
from utils_shared.user_places import LAUNCH_LOG_NAME, LAUNCH_LOG_START


# ---- CONSTANTS -----------------------------------------------------------------------
# Only the developer's copy has both: `.style/` is left off main and out of the Mac app,
# and `_USER_REVIEW/` is never in git.
DEV_MARKS = (('.style', 'VERSION'), ('_USER_REVIEW',))
INBOX_PARTS = ('_USER_REVIEW', 'inbox')
FLAG_PREFIX = 'flag_'
SCREEN_NAME = 'screen.png'
NOTE_NAME = 'note.md'
LOG_NAME = 'log.txt'
FLAG_BUTTON_TEXT = 'Flag'
BOX_HEADING = 'Flag saved: type or paste what is wrong.'
NO_PICTURE_SENTENCE = ('No picture of the window could be taken; the comment and the '
                       'log are still saved.'
                       )
NO_FOLDER_SENTENCE = ('The flag could not be saved: check that _USER_REVIEW/inbox can be '
                      'written to.'
                      )


# ---- FlagBox -------------------------------------------------------------------------
class FlagBox:
    """
    ---- Summary ----
    The small box that takes the comment of a flag, above the window but not blocking
    it: Save (or Ctrl+Enter) writes the note and the log into the flag's folder, Cancel
    (or closing the box) removes the folder.

    ---- Attributes ----
    folder : Path
        The flag's folder, which already holds the picture.
    details : Dict[str, str]
        What was on screen at the click (see flag_saver).
    moment : datetime
        When Flag was clicked.
    launch_log : Path
        The start-up log, used while no run is being logged.
    window : Any
        The box (a Tk Toplevel).
    text : Any
        The text area of the comment.

    ---- Globals read ----
    BOX_HEADING, NO_PICTURE_SENTENCE (module constants).

    ---- Methods ----
    __init__
    _canceller
    _saver
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 parent: Any,
                 folder: Path,
                 details: Dict[str, str],
                 moment: datetime,
                 has_picture: bool,
                 launch_log: Path,
                 ) -> None:
        """
        ---- Summary ----
        Method to open the box above the window, with the cursor in its text area.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        parent : Any
            The program's window.
        folder : Path
            The flag's folder.
        details : Dict[str, str]
            What was on screen at the click.
        moment : datetime
            When Flag was clicked.
        has_picture : bool
            False when no picture of the window could be taken, which the box says.
        launch_log : Path
            The start-up log.

        ---- Globals read ----
        BOX_HEADING, NO_PICTURE_SENTENCE (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Opens the box (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _canceller
        _saver
        """

        self.folder = folder
        self.details = details
        self.moment = moment
        self.launch_log = launch_log
        window = tk.Toplevel(parent)
        window.title(f'Flag {moment:%H:%M:%S}')
        window.transient(parent)
        window.attributes('-topmost', True)
        window.protocol('WM_DELETE_WINDOW', self._canceller)
        tk.Label(window, text=BOX_HEADING, anchor='w').pack(fill='x',
                                                            padx=10,
                                                            pady=(8, 2),
                                                            )
        if not has_picture:
            tk.Label(window,
                     text=NO_PICTURE_SENTENCE,
                     anchor='w',
                     fg='#b04040',
                     ).pack(fill='x', padx=10)
        self.text = tk.Text(window, width=60, height=8, wrap='word', undo=True)
        self.text.pack(fill='both', expand=True, padx=10, pady=4)
        buttons = tk.Frame(window)
        tk.Button(buttons, text='Cancel', command=self._canceller).pack(side='right')
        tk.Button(buttons, text='Save', command=self._saver).pack(side='right', padx=6)
        buttons.pack(fill='x', padx=10, pady=(0, 8))
        self.text.bind('<Control-Return>', self._saver)
        self.window = window
        self.text.focus_set()

    # ---- _canceller ------------------------------------------------------------------
    def _canceller(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to drop the flag: its folder is removed and the box closed.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Removes the folder and closes the box (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        flag_canceller
        """

        flag_canceller(self.folder)
        self.window.destroy()

    # ---- _saver ----------------------------------------------------------------------
    def _saver(self, event: Any = None) -> str:
        """
        ---- Summary ----
        Method to save the comment with the flag and close the box.

        ---- Inputs ----
        event : Any
            The Tk event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            'break', so Ctrl+Enter adds no new line to the text area.

        ---- Globals mutated ----
        None. Writes the flag's files and closes the box (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        flag_saver
        """

        comment = self.text.get('1.0', 'end').strip()
        try:
            flag_saver(self.folder, comment, self.details, self.moment, self.launch_log)
        except OSError:
            warning_shower(NO_FOLDER_SENTENCE)
        self.window.destroy()
        return 'break'


# ---- FLAG HELPERS --------------------------------------------------------------------


# ---- _log_copier ---------------------------------------------------------------------
def _log_copier(source: Optional[Path], target: Path) -> bool:
    """
    ---- Summary ----
    Helper function to copy the log in use into the flag's folder; of the start-up log,
    which keeps the starts before, only this start is copied.

    ---- Inputs ----
    source : Optional[Path]
        The log in use, or None when there is none.
    target : Path
        Where the copy goes.

    ---- Globals read ----
    LAUNCH_LOG_NAME, LAUNCH_LOG_START (imported constants).

    ---- Outputs ----
    bool
        True when the log was copied; False when there is none or it cannot be read.

    ---- Globals mutated ----
    None. Writes the copy (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if source is None or not source.is_file():
        return False
    try:
        text = source.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False
    if source.name == LAUNCH_LOG_NAME:
        start = text.rfind(LAUNCH_LOG_START)
        text = text[max(start, 0):]
    target.write_text(text, encoding='utf-8')
    return True


# ---- _note_builder -------------------------------------------------------------------
def _note_builder(comment: str,
                  details: Dict[str, str],
                  moment: datetime,
                  has_log: bool,
                  ) -> str:
    """
    ---- Summary ----
    Helper function to write the text of a flag's note: the comment first, then what was
    on screen at the click, then the guide's last lines.

    ---- Inputs ----
    comment : str
        What the developer typed or pasted; may be empty.
    details : Dict[str, str]
        What was on screen at the click (see flag_saver).
    moment : datetime
        When Flag was clicked.
    has_log : bool
        Whether the log was copied beside the note.

    ---- Globals read ----
    LOG_NAME, SCREEN_NAME (module constants).

    ---- Outputs ----
    str
        The note, in Markdown.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    lines = [f'# Flag {moment:%Y-%m-%d %H:%M:%S}',
             '',
             comment or '(no comment)',
             '',
             '## On screen',
             f"- Version: {details.get('version', '')}",
             f"- File shown: {details.get('file', '') or 'none'}",
             f"- Step: {details.get('step', '') or 'none'}",
             f'- Picture: {SCREEN_NAME}',
             f"- Log: {LOG_NAME if has_log else 'none found'}",
             '',
             '## The last lines of the guide',
             '',
             '```text',
             details.get('guide_text', '').rstrip(),
             '```',
             '',
             ]
    return '\n'.join(lines)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- dev_copy_checker ----------------------------------------------------------------
def dev_copy_checker(program_folder: Path) -> bool:
    """
    ---- Summary ----
    Main function to say whether the program runs from the developer's own copy, the
    only one that shows the Flag button.

    ---- Inputs ----
    program_folder : Path
        Folder with the program's own files.

    ---- Globals read ----
    DEV_MARKS (module constant).

    ---- Outputs ----
    bool
        True when both `.style/VERSION` and `_USER_REVIEW/` are in the folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return all(program_folder.joinpath(*parts).exists() for parts in DEV_MARKS)


# ---- flag_canceller ------------------------------------------------------------------
def flag_canceller(folder: Path) -> None:
    """
    ---- Summary ----
    Main function to remove a flag's folder and everything in it.

    ---- Inputs ----
    folder : Path
        The flag's folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. A folder already gone is left as it is.

    ---- Globals mutated ----
    None. Removes the folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    shutil.rmtree(folder, ignore_errors=True)


# ---- flag_folder_maker ---------------------------------------------------------------
def flag_folder_maker(program_folder: Path, moment: datetime) -> Path:
    """
    ---- Summary ----
    Main function to make the folder of a new flag in the inbox, named by its time.

    ---- Inputs ----
    program_folder : Path
        Folder with the program's own files.
    moment : datetime
        When Flag was clicked.

    ---- Globals read ----
    FLAG_PREFIX, INBOX_PARTS (module constants).

    ---- Outputs ----
    Path
        The new, empty folder, for example `_USER_REVIEW/inbox/flag_2026_11_25-14_03_12`;
        a second flag in the same second gets `_2` after it.

    ---- Globals mutated ----
    None. Makes the folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    inbox = program_folder.joinpath(*INBOX_PARTS)
    name = f'{FLAG_PREFIX}{moment:%Y_%m_%d-%H_%M_%S}'
    folder, count = inbox / name, 1
    while folder.exists():
        count += 1
        folder = inbox / f'{name}_{count}'
    folder.mkdir(parents=True)
    return folder


# ---- flag_saver ----------------------------------------------------------------------
def flag_saver(folder: Path,
               comment: str,
               details: Dict[str, str],
               moment: datetime,
               launch_log: Path,
               ) -> bool:
    """
    ---- Summary ----
    Main function to finish a flag: a FLAG line with the comment goes into the log in
    use at that point, then that log is copied into the flag's folder beside the note.

    ---- Inputs ----
    folder : Path
        The flag's folder.
    comment : str
        What the developer typed or pasted; may be empty.
    details : Dict[str, str]
        What was on screen at the click: 'version', 'file' (the file shown), 'step'
        (the stage and step the program waits at) and 'guide_text' (the guide's last
        lines).
    moment : datetime
        When Flag was clicked.
    launch_log : Path
        The start-up log, used while no run is being logged.

    ---- Globals read ----
    LOG_NAME, NOTE_NAME (module constants).

    ---- Outputs ----
    bool
        True when a log was copied beside the note.

    ---- Globals mutated ----
    None. Writes the FLAG line into the log, and the note and the log's copy into the
    folder (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _log_copier
    _note_builder
    details_writer
    run_log_path_getter
    """

    one_line = ' '.join(comment.split()) or '(no comment)'
    details_writer(f'==== FLAG {moment:%H:%M:%S} ({folder.name}): {one_line} ====')
    has_log = _log_copier(run_log_path_getter() or launch_log, folder / LOG_NAME)
    note = _note_builder(comment, details, moment, has_log)
    (folder / NOTE_NAME).write_text(note, encoding='utf-8')
    return has_log


# ---- flag_starter --------------------------------------------------------------------
def flag_starter(tk: Any,
                 root: Any,
                 program_folder: Path,
                 details: Dict[str, str],
                 launch_log: Path,
                 ) -> Optional[FlagBox]:
    """
    ---- Summary ----
    Main function to answer a click on Flag: the picture of the window is saved first,
    as it is, then the box for the comment opens.

    ---- Inputs ----
    tk : Any
        The tkinter module.
    root : Any
        The program's window.
    program_folder : Path
        Folder with the program's own files.
    details : Dict[str, str]
        What is on screen (see flag_saver).
    launch_log : Path
        The start-up log.

    ---- Globals read ----
    NO_FOLDER_SENTENCE, SCREEN_NAME (module constants).

    ---- Outputs ----
    Optional[FlagBox]
        The box, or None when the flag's folder could not be made (said under the
        plot).

    ---- Globals mutated ----
    None. Makes the folder, saves the picture and opens the box (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    flag_folder_maker
    screen_saver
    FlagBox
    """

    moment = datetime.now()
    try:
        folder = flag_folder_maker(program_folder, moment)
    except OSError:
        warning_shower(NO_FOLDER_SENTENCE)
        return None
    root.update_idletasks()
    box = (root.winfo_rootx(),
           root.winfo_rooty(),
           root.winfo_rootx() + root.winfo_width(),
           root.winfo_rooty() + root.winfo_height(),
           )
    has_picture = screen_saver(folder / SCREEN_NAME, box)
    return FlagBox(tk, root, folder, details, moment, has_picture, launch_log)


# ---- screen_saver --------------------------------------------------------------------
def screen_saver(path: Path,
                 box: Tuple[int, int, int, int],
                 grabber: Optional[Callable[..., Any]] = None,
                 ) -> bool:
    """
    ---- Summary ----
    Main function to save a picture of part of the screen.

    ---- Inputs ----
    path : Path
        Where the picture goes (.png).
    box : Tuple[int, int, int, int]
        Left, top, right and bottom of the part, in screen pixels.
    grabber : Optional[Callable[..., Any]]
        Takes the picture (bbox=, all_screens=) and gives an image with a save method;
        None for Pillow's ImageGrab.grab.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the picture was saved; False when the computer gives none (Linux
        without a screen grabber, a Mac without the right to record the screen).

    ---- Globals mutated ----
    None. Writes the picture (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        if grabber is None:
            from PIL import ImageGrab
            grabber = ImageGrab.grab
        grabber(bbox=box, all_screens=True).save(path)
    except (ImportError, OSError, RuntimeError, ValueError):
        return False
    return True
