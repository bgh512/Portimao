"""
Launcher: checks for updates, moves a Mac install to the Mac app, sets up the
environment, makes the icon, starts Portimao.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import hashlib
import os
import queue
import shutil
import socket
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Callable, List, Optional, TextIO, Tuple


# ---- CONSTANTS -----------------------------------------------------------------------
APP_NAME = 'Portimao'
ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
ENVIRONMENT = ROOT / ('.venv' if IS_WINDOWS else '.venv_unix')
ENVIRONMENT_PYTHON = ENVIRONMENT / ('Scripts/python.exe'
                                    if IS_WINDOWS
                                    else 'bin/python'
                                    )
ENVIRONMENT_WINDOWLESS = ENVIRONMENT / 'Scripts/pythonw.exe'
# holds the fingerprint of the package list the environment was last installed from
PACKAGE_STAMP = ENVIRONMENT / '.complete'
REQUIREMENTS = ROOT / 'requirements.txt'
LOG_FILE = ROOT / 'logs' / 'launch.log'
# Portimao's window makes this file once it is up (utils_viewer/viewer_gui.py), told
# where by this switch, so the small window closes then
OPENED_FILE = ROOT / 'logs' / 'window_opened'
OPENED_SWITCH = 'PORTIMAO_OPENED_FILE'
SHORTCUT_MARK = ROOT / '.portimao_shortcut'  # git-ignored: each computer makes its own
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
REQUIRED_IMPORTS = 'import numpy, pandas, scipy, matplotlib, xlsxwriter, openpyxl, PIL'
# the update check holds up every start, so a computer with no connection is found in
# a few seconds; git waits longer only once GitHub has answered
GITHUB_ADDRESS = ('github.com', 443)
KNOCK_TIMEOUT_S = 5
ASK_TIMEOUT_S = 15
FETCH_TIMEOUT_S = 120
OPEN_WAIT_S = 60.0  # the small window closes by then even if Portimao's has not opened
MINIMUM_TK = 8.6  # Tk 8.5 (the one Apple's own Python uses) draws blank windows
# the end of every message that asks for the details to be sent
SEND_LOG = ('send the file logs/launch.log from the Portimao folder through the Issues '
            'page (see Feedback at the top of the README)')
APT_LINE = 'type {} in a terminal (on Ubuntu or Debian), then open Portimao again'
# Why this git copy cannot update itself, handed to Portimao in this switch so it is
# said beside the version (utils_shared/helpers.py says it for a copy from a zip).
UPDATE_NOTE_SWITCH = 'PORTIMAO_UPDATE_NOTE'
NO_GIT_NOTE = ('This copy cannot update itself, as git is not installed: install git '
               '(README, section 1.2), then open Portimao again.')
NO_BRANCH_NOTE = ('This copy cannot update itself, as it follows no branch on GitHub: '
                  'install Portimao again (README, section 1).')
REFUSED_NOTE = 'A newer Portimao is out, but this copy could not update itself ({}): {}.'
SHOWN_FILES = 3  # changed files named in the note; the others are counted


# ---- LaunchProblemError ----
class LaunchProblemError(Exception):
    """
    ---- Summary ----
    A problem that stops the launcher, with one plain sentence for the user saying
    what went wrong and what to do; the details are already in logs/launch.log.

    ---- Attributes ----
    args : tuple
        The sentence, as the only item.

    ---- Globals read ----
    None.

    ---- Methods ----
    None.
    """


# ---- LAUNCHER HELPERS ----------------------------------------------------------------


# ---- _app_move_trier -----------------------------------------------------------------
def _app_move_trier(show: Callable[[str], None]) -> bool:
    """
    ---- Summary ----
    Helper function to move this folder to the Mac app on a Mac (mac_app_mover). A move
    that stops in a way it did not foresee leaves the program to start the old way,
    with what happened in logs/move_to_app.log.

    ---- Inputs ----
    show : Callable[[str], None]
        Function that shows a line of progress text.

    ---- Globals read ----
    ROOT (module constant).

    ---- Outputs ----
    bool
        True when the app is opening in place of this folder, so the launcher closes.

    ---- Globals mutated ----
    None. May install the app and take away the program files (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _mac_mover_loader
    app_mover
    """

    try:
        return _mac_mover_loader().app_mover(ROOT, Path.home(), show)
    except Exception:  # the old way still works, so the start goes on
        try:
            log = ROOT / 'logs' / 'move_to_app.log'
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, 'a', encoding='utf-8') as stream:
                stream.write(f'The move stopped:\n{traceback.format_exc()}')
        except OSError:
            pass
        return False


# ---- _changed_files_lister -----------------------------------------------------------
def _changed_files_lister() -> List[str]:
    """
    ---- Summary ----
    Helper function to list the program files changed by hand in this git copy (files
    git does not know are left out), which stop an update that changes them too.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The changed files, as paths inside the Portimao folder; empty when there are
        none or git cannot say.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    """

    asked = _command_runner(['git', 'status', '--porcelain', '--untracked-files=no'])
    if asked.returncode != 0:
        return []
    # each line is two status letters, a space and the path ("old -> new" when renamed)
    return [line[3:].split(' -> ')[-1].strip('"')
            for line in asked.stdout.splitlines()
            if len(line) > 3
            ]


# ---- _command_runner -----------------------------------------------------------------
def _command_runner(command: List[str],
                    timeout: Optional[float] = None,
                    ) -> 'subprocess.CompletedProcess':
    """
    ---- Summary ----
    Helper function to run a command without opening a window and keep its output.

    ---- Inputs ----
    command : List[str]
        Program and arguments.
    timeout : Optional[float]
        Seconds to wait, or None to wait for ever.

    ---- Globals read ----
    ROOT, HIDDEN (module constants).

    ---- Outputs ----
    subprocess.CompletedProcess
        The finished command (return code and text output).

    ---- Globals mutated ----
    None. Runs a program (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return subprocess.run(command,
                          cwd=ROOT,
                          capture_output=True,
                          text=True,
                          timeout=timeout,
                          creationflags=HIDDEN,
                          )


# ---- _details_writer ----
def _details_writer(text: str) -> None:
    """
    ---- Summary ----
    Helper function to add the details of a launcher problem to logs/launch.log, after
    the starts before, so the message to the user can stay one plain sentence.

    ---- Inputs ----
    text : str
        The details: a program's own error text, or a traceback.

    ---- Globals read ----
    LOG_FILE (module constant).

    ---- Outputs ----
    None
        Nothing. Details that cannot be written are lost, the message still shows.

    ---- Globals mutated ----
    None. Writes the log file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8', errors='replace') as log:
            log.write(f'\nThe launcher stopped, {datetime.now():%Y-%m-%d %H:%M:%S}:\n'
                      f'{text.strip()}\n',
                      )
    except OSError:
        pass


# ---- _github_knocker ----
def _github_knocker() -> bool:
    """
    ---- Summary ----
    Helper function to find out within a few seconds whether GitHub can be reached, by
    opening a plain connection to it (no certificates needed, so any Python can).

    ---- Inputs ----
    None.

    ---- Globals read ----
    GITHUB_ADDRESS, KNOCK_TIMEOUT_S (module constants).

    ---- Outputs ----
    bool
        True when GitHub answered.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        with socket.create_connection(GITHUB_ADDRESS, timeout=KNOCK_TIMEOUT_S):
            return True
    except OSError:
        return False


# ---- _launch_log_opener --------------------------------------------------------------
def _launch_log_opener() -> TextIO:
    """
    ---- Summary ----
    Helper function to open logs/launch.log for this start with the program's own
    opener (launch_log_opener), so it keeps the starts before as the Mac app's does.
    If the opener cannot be loaded, the log is opened for adding text without it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LOG_FILE (module constant).

    ---- Outputs ----
    TextIO
        The log, open for adding text. Raises OSError when it cannot be opened.

    ---- Globals mutated ----
    None. Makes the logs folder and writes the start line (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _user_places_loader
    launch_log_opener
    """

    try:
        opener = _user_places_loader().launch_log_opener
    except Exception:  # a log without its start line still takes the output
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        return open(LOG_FILE, 'a', encoding='utf-8', errors='replace')
    return opener(LOG_FILE)


# ---- _mac_mover_loader ---------------------------------------------------------------
def _mac_mover_loader() -> ModuleType:
    """
    ---- Summary ----
    Helper function to load the Mac's move to the app (launchers/mac_app_mover.py),
    only on a Mac, from the launchers folder.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT (module constant).

    ---- Outputs ----
    ModuleType
        The module mac_app_mover.

    ---- Globals mutated ----
    sys.path: the launchers folder is put first when it is missing.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    folder = str(ROOT / 'launchers')
    if folder not in sys.path:
        sys.path.insert(0, folder)
    import mac_app_mover
    return mac_app_mover


# ---- _message_shower -----------------------------------------------------------------
def _message_shower(title: str, text: str) -> None:
    """
    ---- Summary ----
    Helper function to show a message without a terminal: a message box where there is
    one, otherwise the standard error stream.

    ---- Inputs ----
    title : str
        Heading of the message.
    text : str
        The message.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Opens a message box (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        if IS_WINDOWS:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)
            return
        if sys.platform == 'darwin':
            safe = text.replace('\\', ' ').replace('"', "'").replace('\n', ' ')
            script = f'display dialog "{safe}" with title "{title}" buttons {{"OK"}}'
            subprocess.run(['osascript', '-e', script], check=False)
            return
        for tool in (['zenity', '--error', '--title', title, '--text', text],
                     ['kdialog', '--error', text, '--title', title],
                     ['xmessage', '-center', f'{title}: {text}'],
                     ):
            if shutil.which(tool[0]):
                subprocess.run(tool, check=False)
                return
    except Exception:  # a message that cannot be shown is still in the log
        pass
    print(f'{title}: {text}', file=sys.stderr)


# ---- _package_list_stamper ----
def _package_list_stamper(requirements: Path) -> str:
    """
    ---- Summary ----
    Helper function to make a fingerprint of the package list, so a change in it (a
    new package, or a newer version asked for) is seen at the next start.

    ---- Inputs ----
    requirements : Path
        The package list (requirements.txt).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The fingerprint (64 hexadecimal characters); empty when the list cannot be
        read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    SHA-256 of the list's text, with Windows line endings made plain, so a copy
    checked out on Windows gives the same fingerprint.

    ---- Helpers ----
    None.
    """

    try:
        text = requirements.read_text(encoding='utf-8')
    except OSError:
        return ''
    return hashlib.sha256(text.replace('\r\n', '\n').encode('utf-8')).hexdigest()


# ---- _tk_version_getter --------------------------------------------------------------
def _tk_version_getter(python: str) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to find which version of Tk (the toolkit of the program's window) a
    Python has.

    ---- Inputs ----
    python : str
        Path of the Python program to ask.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The Tk version (for example 8.6), or None when that Python has no Tk.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    """

    try:
        asked = _command_runner([python,
                                 '-c',
                                 'import tkinter; print(tkinter.TkVersion)',
                                 ])
        return float(asked.stdout.strip()) if asked.returncode == 0 else None
    except (ValueError, OSError):
        return None


# ---- _python_finder ------------------------------------------------------------------
def _python_finder() -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find a Python 3.9 or newer to build the private environment
    with: one with a Tk of at least 8.6 when there is one (the window is blank with the
    Tk 8.5 of Apple's own Python), otherwise any Python 3.9 or newer.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MINIMUM_TK (module constant).

    ---- Outputs ----
    Optional[str]
        Path of the program, or None when there is none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    _tk_version_getter
    """

    candidates = [sys.executable] if sys.version_info >= (3, 9) else []
    candidates += [shutil.which(name) for name in ('python3', 'python')]
    if sys.platform == 'darwin':
        framework = '/Library/Frameworks/Python.framework/Versions'
        candidates += [f'{framework}/Current/bin/python3',
                       '/opt/homebrew/bin/python3',
                       '/usr/local/bin/python3',
                       ]
        candidates += [f'{framework}/3.{minor}/bin/python3'
                       for minor in range(14, 8, -1)
                       ]
    usable = []
    for candidate in dict.fromkeys(c for c in candidates if c and Path(c).exists()):
        check = _command_runner([candidate,
                                 '-c',
                                 'import sys; sys.exit(sys.version_info < (3, 9))',
                                 ])
        if check.returncode == 0:
            usable.append(candidate)
    for candidate in usable:
        if (_tk_version_getter(candidate) or 0) >= MINIMUM_TK:
            return candidate
    return usable[0] if usable else None


# ---- _refused_note_maker -------------------------------------------------------------
def _refused_note_maker() -> str:
    """
    ---- Summary ----
    Helper function to say why git refused this copy's update, and what to do: the
    files changed here, when there are some, or else that the copy has changes of its
    own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    REFUSED_NOTE, SHOWN_FILES (module constants).

    ---- Outputs ----
    str
        The sentence for the user, for example "A newer Portimao is out, but this copy
        could not update itself (changed here: config.py): put that file back as it
        was, or install Portimao again (README, section 1)."

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _changed_files_lister
    """

    again = 'install Portimao again (README, section 1)'
    changed = _changed_files_lister()
    if not changed:
        return REFUSED_NOTE.format('it has changes of its own', again)
    names = ', '.join(changed[:SHOWN_FILES])
    if len(changed) > SHOWN_FILES:
        names += f' and {len(changed) - SHOWN_FILES} more'
    back = ('put that file back as it was'
            if len(changed) == 1
            else 'put those files back as they were'
            )
    return REFUSED_NOTE.format(f'changed here: {names}', f'{back}, or {again}')


# ---- _status_window_maker ------------------------------------------------------------
def _status_window_maker() -> Optional[Callable[[str], None]]:
    """
    ---- Summary ----
    Helper function to open a small window that shows what the launcher is doing, when
    Tkinter is available. The window is run by the caller through the returned
    function's ``mainloop`` attribute.

    ---- Inputs ----
    None.

    ---- Globals read ----
    APP_NAME, MINIMUM_TK (module constants).

    ---- Outputs ----
    Optional[Callable[[str], None]]
        Function that shows a line of text in the window (thread safe), with the
        attributes ``mainloop`` and ``close``; None when there is no Tkinter.

    ---- Globals mutated ----
    None. Opens a window (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        import tkinter as tk
        from tkinter import ttk
        if tk.TkVersion < MINIMUM_TK:  # it would be a blank window
            return None
        root = tk.Tk()
    except Exception:
        return None
    root.title(APP_NAME)
    root.resizable(False, False)
    icon = ROOT / 'assets' / 'icon.png'
    try:
        root.iconphoto(True, tk.PhotoImage(file=str(icon)))
    except Exception:
        pass
    label = ttk.Label(root, text=f'Starting {APP_NAME} ...', padding=(24, 18, 24, 6))
    label.pack()
    bar = ttk.Progressbar(root, mode='indeterminate', length=300)
    bar.pack(padx=24, pady=(0, 18))
    bar.start(12)
    messages: 'queue.Queue' = queue.Queue()
    def poll() -> None:
        while not messages.empty():
            text = messages.get()
            if text is None:  # close, asked for by the launcher thread
                root.destroy()
                return
            label.configure(text=text)
        root.after(100, poll)
    def show(text: str) -> None:
        messages.put(text)
    # Tk is only touched by the main thread (other threads crash it on macOS), so the
    # launcher thread asks for the window to close through the queue
    show.mainloop = lambda: (poll(), root.mainloop())  # type: ignore[attr-defined]
    show.close = lambda: messages.put(None)  # type: ignore[attr-defined]
    return show


# ---- _user_places_loader -------------------------------------------------------------
def _user_places_loader() -> ModuleType:
    """
    ---- Summary ----
    Helper function to load the program's module of the user's places
    (utils_shared/user_places.py, standard library only), for the launch log's opener.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT (module constant).

    ---- Outputs ----
    ModuleType
        The module user_places.

    ---- Globals mutated ----
    sys.path: the Portimao folder is put first when it is missing.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    folder = str(ROOT)
    if folder not in sys.path:
        sys.path.insert(0, folder)
    from utils_shared import user_places
    return user_places


# ---- _window_waiter ----
def _window_waiter(process: 'subprocess.Popen') -> Optional[int]:
    """
    ---- Summary ----
    Helper function to wait until Portimao's window is up (it makes the file the
    launcher named), Portimao has stopped, or the longest wait has passed.

    ---- Inputs ----
    process : subprocess.Popen
        The running program.

    ---- Globals read ----
    OPEN_WAIT_S, OPENED_FILE (module constants).

    ---- Outputs ----
    Optional[int]
        Portimao's exit code when it stopped before its window opened; None while it
        runs.

    ---- Globals mutated ----
    None. Deletes the file the window made (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    deadline = time.time() + OPEN_WAIT_S
    while (time.time() < deadline
           and process.poll() is None
           and not OPENED_FILE.exists()):
        time.sleep(0.2)
    try:
        OPENED_FILE.unlink(missing_ok=True)
    except OSError:
        pass
    return process.poll()


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- environment_builder -------------------------------------------------------------
def environment_builder(show: Callable[[str], None]) -> None:
    """
    ---- Summary ----
    Main function to make sure the private Python environment exists and has every
    package on the package list, installing them the first time and again whenever the
    list has changed (needs internet). When an update of the packages fails but the
    ones it has still load, Portimao opens with them and the next start tries again.

    ---- Inputs ----
    show : Callable[[str], None]
        Function that shows a line of progress text.

    ---- Globals read ----
    APP_NAME, APT_LINE, ENVIRONMENT, ENVIRONMENT_PYTHON, IS_LINUX, MINIMUM_TK,
    PACKAGE_STAMP, REQUIRED_IMPORTS, REQUIREMENTS, SEND_LOG (module constants).

    ---- Outputs ----
    None
        Nothing. Raises LaunchProblemError with a plain sentence when it fails, after
        writing the details to logs/launch.log.

    ---- Globals mutated ----
    None. Creates the environment folder, installs packages and writes the package
    fingerprint (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    _details_writer
    _package_list_stamper
    _python_finder
    _tk_version_getter
    """

    # ---- 1 Rebuild an environment whose Python draws blank windows -------------------
    if ENVIRONMENT_PYTHON.exists() and (
        (_tk_version_getter(str(ENVIRONMENT_PYTHON)) or 0) < MINIMUM_TK
    ):
        better = _python_finder()
        if better and (_tk_version_getter(better) or 0) >= MINIMUM_TK:
            show('Rebuilding the environment with a newer Python ...')
            shutil.rmtree(ENVIRONMENT, ignore_errors=True)

    # ---- 2 Make the environment the first time ---------------------------------------
    if not ENVIRONMENT_PYTHON.exists():
        show('First run: setting things up (a minute or two, needs internet) ...')
        python = _python_finder()
        if python is None:
            fix = (APT_LINE.format('sudo apt install python3 python3-venv python3-tk')
                   if IS_LINUX
                   else 'install it from https://www.python.org/downloads/, then open '
                   f'{APP_NAME} again'
                   )
            raise LaunchProblemError(f'{APP_NAME} needs Python 3.9 or newer, and none '
                                     f'was found: {fix}.',
                                     )
        made = _command_runner([python, '-m', 'venv', str(ENVIRONMENT)])
        if made.returncode != 0:
            shutil.rmtree(ENVIRONMENT, ignore_errors=True)
            _details_writer(f'Making the environment with {python} failed:\n'
                            f'{made.stdout}\n{made.stderr}',
                            )
            fix = (APT_LINE.format('sudo apt install python3-venv')
                   if IS_LINUX
                   else f'open {APP_NAME} again; if this message comes back, {SEND_LOG}'
                   )
            raise LaunchProblemError(f'{APP_NAME} could not make its own copy of '
                                     f'Python: {fix}.',
                                     )

    # ---- 3 Install the packages when the list has changed ----------------------------
    stamp = _package_list_stamper(REQUIREMENTS)
    try:
        is_listed = PACKAGE_STAMP.read_text(encoding='utf-8').strip() == stamp
    except OSError:
        is_listed = False
    if is_listed:
        ready = _command_runner([str(ENVIRONMENT_PYTHON), '-c', REQUIRED_IMPORTS])
        if ready.returncode == 0:
            return
    is_installed = PACKAGE_STAMP.exists()
    show('Updating the packages ...' if is_installed else 'Installing the packages ...')
    command = [str(ENVIRONMENT_PYTHON),
               '-m',
               'pip',
               'install',
               '--quiet',
               '--disable-pip-version-check',
               '-r',
               str(REQUIREMENTS),
               ]
    installed = _command_runner(command)
    if installed.returncode == 0:
        PACKAGE_STAMP.write_text(stamp, encoding='utf-8')
        return

    # ---- 4 Open with the packages it has, or stop ------------------------------------
    ready = _command_runner([str(ENVIRONMENT_PYTHON), '-c', REQUIRED_IMPORTS])
    if is_installed and ready.returncode == 0:
        show(f'The packages could not be updated, so {APP_NAME} opens with the ones it '
             f'has.',
             )
        return
    if not is_installed:
        shutil.rmtree(ENVIRONMENT, ignore_errors=True)
    _details_writer(f'Installing the packages failed:\n{installed.stdout}\n'
                    f'{installed.stderr}',
                    )
    raise LaunchProblemError(f'{APP_NAME} could not download the packages it needs. '
                             f'Check the internet connection, then open {APP_NAME} '
                             f'again; if this message comes back, {SEND_LOG}.',
                             )


# ---- launcher_runner -----------------------------------------------------------------
def launcher_runner(show: Callable[[str], None]) -> int:
    """
    ---- Summary ----
    Main function to do every launcher step in order, close the small window once
    Portimao's own window is up, and report a failure in a message box of one plain
    sentence, with the details in logs/launch.log.

    ---- Inputs ----
    show : Callable[[str], None]
        Function that shows a line of progress text.

    ---- Globals read ----
    APP_NAME, APT_LINE, ENVIRONMENT, ENVIRONMENT_PYTHON, IS_LINUX, MINIMUM_TK,
    SEND_LOG (module constants).

    ---- Outputs ----
    int
        0 when the program started, 1 otherwise.

    ---- Globals mutated ----
    None. Starts the program, may restart this launcher, and on a Mac may move this
    folder to the Mac app (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_move_trier
    _details_writer
    _message_shower
    _tk_version_getter
    _window_waiter
    environment_builder
    program_starter
    shortcut_maker
    update_checker
    """

    title = f'{APP_NAME} could not start'
    try:
        # ---- 1 Update, or move a Mac install to the app ------------------------------
        show('Checking for updates ...')
        is_updated, update_note = update_checker()
        if is_updated:
            environment = dict(os.environ, PORTIMAO_UPDATED='1')
            subprocess.Popen([sys.executable, str(Path(__file__).resolve())],
                             env=environment,
                             )
            return 0
        if sys.platform == 'darwin' and _app_move_trier(show):
            return 0  # the Mac app is opening in place of this folder

        # ---- 2 Check the environment can draw the window -----------------------------
        environment_builder(show)
        tk_version = _tk_version_getter(str(ENVIRONMENT_PYTHON))
        if tk_version is None and IS_LINUX:
            raise LaunchProblemError('The Python on this computer cannot draw windows '
                                     '(it has no Tk): '
                                     + APT_LINE.format('sudo apt install python3-tk')
                                     + '.',
                                     )
        if tk_version is None or tk_version < MINIMUM_TK:
            reason = ('has no Tk (its window toolkit)'
                      if tk_version is None
                      else f'uses Tk {tk_version:g}, which draws blank windows'
                      )
            raise LaunchProblemError(f'The Python found on this computer {reason}. '
                                     f'Install Python 3.12 or newer from '
                                     f'https://www.python.org/downloads/ (it includes '
                                     f'a good Tk), then delete the hidden folder '
                                     f'{ENVIRONMENT.name} inside the {APP_NAME} '
                                     f'folder and open {APP_NAME} again.',
                                     )

        # ---- 3 Open Portimao and wait for its window ---------------------------------
        shortcut_maker()
        opening = f'Opening {APP_NAME} ...'
        if is_updated is None:
            opening = f'No connection to GitHub, so updates were not checked. {opening}'
        show(opening)
        code = _window_waiter(program_starter(update_note))
        if code not in (None, 0):  # what it printed is already in logs/launch.log
            raise LaunchProblemError(f'{APP_NAME} stopped as it opened. Open it again; '
                                     f'if it stops again, {SEND_LOG}.',
                                     )
        return 0
    except LaunchProblemError as problem:
        _message_shower(title, str(problem))
        return 1
    except Exception:  # anything unforeseen still ends in a plain message
        _details_writer(traceback.format_exc())
        _message_shower(title,
                        f"{APP_NAME}'s launcher stopped because of a problem. Open "
                        f'{APP_NAME} again; if it happens again, {SEND_LOG}.',
                        )
        return 1


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function to run the launcher, with a small progress window when Tkinter is
    available and without one when it is not.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        Exit code.

    ---- Globals mutated ----
    None. Opens a window and starts the program (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _status_window_maker
    launcher_runner
    """

    show = _status_window_maker()
    if show is None:
        return launcher_runner(lambda text: None)
    result: List[int] = []
    def work() -> None:
        result.append(launcher_runner(show))
        show.close()  # type: ignore[attr-defined]
    threading.Thread(target=work, daemon=True).start()
    show.mainloop()  # type: ignore[attr-defined]
    return result[0] if result else 1


# ---- program_starter -----------------------------------------------------------------
def program_starter(update_note: str = '') -> 'subprocess.Popen':
    """
    ---- Summary ----
    Main function to start the program in the private environment, with no terminal
    window. What it prints goes to logs/launch.log, after the starts before; it is
    told which file to make once its window is up, and why this copy cannot update
    itself, if it cannot.

    ---- Inputs ----
    update_note : str
        Why this copy cannot update itself, from update_checker; empty when it can.

    ---- Globals read ----
    ROOT, ENVIRONMENT_PYTHON, ENVIRONMENT_WINDOWLESS, IS_WINDOWS, OPENED_FILE,
    OPENED_SWITCH, UPDATE_NOTE_SWITCH (module constants).

    ---- Outputs ----
    subprocess.Popen
        The running program.

    ---- Globals mutated ----
    None. Starts a process, writes the log file and deletes a window file left from
    before (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _launch_log_opener
    """

    log = _launch_log_opener()
    OPENED_FILE.unlink(missing_ok=True)
    program = str(ROOT / 'main.py')
    environment = dict(os.environ,
                       PYTHONIOENCODING='utf-8',
                       PYTHONUTF8='1',
                       **{OPENED_SWITCH: str(OPENED_FILE)},
                       )
    environment.pop(UPDATE_NOTE_SWITCH, None)
    if update_note:
        environment[UPDATE_NOTE_SWITCH] = update_note
    if IS_WINDOWS:
        python = ENVIRONMENT_WINDOWLESS
        if not python.exists():
            python = ENVIRONMENT_PYTHON
        flags = HIDDEN | getattr(subprocess, 'DETACHED_PROCESS', 0)
        return subprocess.Popen([str(python), program],
                                cwd=ROOT,
                                env=environment,
                                stdin=subprocess.DEVNULL,
                                stdout=log,
                                stderr=log,
                                creationflags=flags,
                                )
    return subprocess.Popen([str(ENVIRONMENT_PYTHON), program],
                            cwd=ROOT,
                            env=environment,
                            stdin=subprocess.DEVNULL,
                            stdout=log,
                            stderr=log,
                            start_new_session=True,
                            )


# ---- shortcut_maker ------------------------------------------------------------------
def shortcut_maker() -> None:
    """
    ---- Summary ----
    Main function to make the clickable icon the first time (and again if the folder
    is moved): Desktop and Start menu shortcuts on Windows, an entry in the
    applications menu and on the Desktop on Linux. A Mac that runs Portimao from this
    folder (one that cannot run the Mac app) gets a Portimao file on the Desktop, which
    also takes the place of the old link to Portimao.app at any start.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, SHORTCUT_MARK, APP_NAME (module constants).

    ---- Outputs ----
    None
        Nothing. A missing shortcut never stops the program.

    ---- Globals mutated ----
    None. Writes shortcut files and a marker file (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    _mac_mover_loader
    desktop_file_maker
    """

    try:
        is_made = SHORTCUT_MARK.exists() and SHORTCUT_MARK.read_text() == str(ROOT)
        if sys.platform == 'darwin':
            # at every start, as the update takes away what the old link opened
            _mac_mover_loader().desktop_file_maker(ROOT,
                                                   Path.home(),
                                                   sys.executable,
                                                   not is_made,
                                                   )
        if is_made:
            return
        if IS_WINDOWS:
            script = ROOT / 'launchers' / 'make_shortcut.ps1'
            windowless = Path(sys.executable).with_name('pythonw.exe')
            target = windowless if windowless.exists() else Path(sys.executable)
            _command_runner(['powershell',
                             '-NoProfile',
                             '-ExecutionPolicy',
                             'Bypass',
                             '-WindowStyle',
                             'Hidden',
                             '-File',
                             str(script),
                             str(ROOT),
                             str(target),
                             str(ROOT / 'Portimao.pyw'),
                             ])
        elif sys.platform.startswith('linux'):
            python = shutil.which('python3') or 'python3'
            launcher = ROOT / 'launchers' / 'bootstrap.pyw'
            icon = ROOT / 'assets' / 'icon.png'
            entry = (f'[Desktop Entry]\nType=Application\nName={APP_NAME}\n'
                     'Comment=Convert chamber .paf files to figures and data\n'
                     f'Exec={python} "{launcher}"\n'
                     f'Path={ROOT}\nIcon={icon}\n'
                     'Terminal=false\nCategories=Science;Education;\n'
                     )
            data_home = os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')
            menu = Path(data_home) / 'applications'
            for folder in (menu, Path.home() / 'Desktop'):
                if folder.is_dir() or folder == menu:
                    folder.mkdir(parents=True, exist_ok=True)
                    path = folder / f'{APP_NAME}.desktop'
                    path.write_text(entry, encoding='utf-8')
                    path.chmod(0o755)
                    if shutil.which('gio'):
                        _command_runner(['gio',
                                         'set',
                                         str(path),
                                         'metadata::trusted',
                                         'true',
                                         ])
        SHORTCUT_MARK.write_text(str(ROOT))
    except Exception:  # a missing shortcut must never stop the program
        pass


# ---- update_checker ------------------------------------------------------------------
def update_checker() -> Tuple[Optional[bool], str]:
    """
    ---- Summary ----
    Main function to install a newer version from GitHub when this folder is a git
    clone and one is available. It first finds out within a few seconds whether GitHub
    can be reached, then asks only for GitHub's newest commit, and downloads only when
    that is new. When this copy cannot update (git missing, no branch followed, files
    changed here that the update changes too) the current version runs, and the reason
    is given for Portimao to say beside its version. A copy from a zip has no reason
    here: Portimao finds that out itself.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ASK_TIMEOUT_S, FETCH_TIMEOUT_S, NO_BRANCH_NOTE, NO_GIT_NOTE, ROOT (module
    constants); os.environ['PORTIMAO_UPDATED'].

    ---- Outputs ----
    Tuple[Optional[bool], str]
        (True when an update was installed, so the launcher must start again; False
        when there is nothing newer, or this copy cannot update; None when GitHub
        could not be reached. Why this copy cannot update, in one sentence for the
        user; empty when it can.)

    ---- Globals mutated ----
    None. May change the files of the program (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    _github_knocker
    _refused_note_maker
    """

    # ---- 1 Check this copy can update and GitHub can be reached ----------------------
    if not (ROOT / '.git').exists() or os.environ.get('PORTIMAO_UPDATED'):
        return False, ''
    if shutil.which('git') is None:
        return False, NO_GIT_NOTE
    if not _github_knocker():
        return None, ''
    try:
        # ---- 2 Ask for GitHub's newest commit of this copy's branch ------------------
        upstream = _command_runner(['git',
                                    'rev-parse',
                                    '--abbrev-ref',
                                    '--symbolic-full-name',
                                    '@{u}',
                                    ])
        remote, _, branch = upstream.stdout.strip().partition('/')
        if upstream.returncode != 0 or not branch:
            return False, NO_BRANCH_NOTE
        asked = _command_runner(['git', 'ls-remote', remote, f'refs/heads/{branch}'],
                                timeout=ASK_TIMEOUT_S,
                                )
        words = asked.stdout.split()
        if asked.returncode != 0 or not words:
            return None, ''
        is_current = _command_runner(['git',
                                      'merge-base',
                                      '--is-ancestor',
                                      words[0],
                                      'HEAD',
                                      ]).returncode == 0
        if is_current:
            return False, ''

        # ---- 3 Download and install it -----------------------------------------------
        fetched = _command_runner(['git', 'fetch', '--quiet'], timeout=FETCH_TIMEOUT_S)
        if fetched.returncode != 0:
            return None, ''
        behind = _command_runner(['git', 'rev-list', '--count', 'HEAD..@{u}'])
        if behind.returncode != 0 or int(behind.stdout.strip() or 0) == 0:
            return False, ''
        if _command_runner(['git', 'pull', '--ff-only', '--quiet']).returncode == 0:
            return True, ''
        return False, _refused_note_maker()
    except subprocess.TimeoutExpired:
        return None, ''
    except (OSError, ValueError):
        return False, ''


if __name__ == '__main__':
    sys.exit(main())
