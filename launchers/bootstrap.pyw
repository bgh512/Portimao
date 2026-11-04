"""
Launcher of the program without a terminal window: checks for updates, sets up the
private Python environment the first time, makes the desktop icon and starts the
program. Needs only the Python standard library. Started by the Portimao icon on
Windows (with pythonw), by Portimao.app on a Mac and by the menu entry on Linux.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import traceback
import venv
from pathlib import Path
from typing import Callable, List, Optional


# ---- CONSTANTS -----------------------------------------------------------------------
APP_NAME = 'Portimao'
ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = sys.platform == 'win32'
ENVIRONMENT = ROOT / ('.venv' if IS_WINDOWS else '.venv_unix')
ENVIRONMENT_PYTHON = ENVIRONMENT / ('Scripts/python.exe'
                                    if IS_WINDOWS
                                    else 'bin/python'
                                    )
ENVIRONMENT_WINDOWLESS = ENVIRONMENT / 'Scripts/pythonw.exe'
LOG_FILE = ROOT / 'logs' / 'launch.log'
SHORTCUT_MARK = ROOT / '.shortcut_made_portimao'  # the old program used .shortcut_made
OLD_NAMES = ('DePalencify', 'Albufeira')  # the names the program had before
REPOSITORY_NAME = 'Portimao'  # the name of the GitHub repository after it is renamed
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
REQUIRED_IMPORTS = 'import numpy, pandas, scipy, matplotlib, xlsxwriter, openpyxl, PIL'
WAIT_SECONDS = 8.0
MINIMUM_TK = 8.6  # Tk 8.5 (the one Apple's own Python uses) draws blank windows


# ---- LAUNCHER HELPERS ----------------------------------------------------------------


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


# ---- _old_shortcut_remover -----------------------------------------------------------
def _old_shortcut_remover() -> None:
    """
    ---- Summary ----
    Helper function to delete the shortcuts of the program under its old name, so only
    the Portimao ones are left after an update.

    ---- Inputs ----
    None.

    ---- Globals read ----
    OLD_NAMES, IS_WINDOWS (module constants).

    ---- Outputs ----
    None
        Nothing. Anything that cannot be deleted is left.

    ---- Globals mutated ----
    None. Deletes shortcut files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    home = Path.home()
    places = [home / 'Desktop']
    if IS_WINDOWS:
        appdata = Path(os.environ.get('APPDATA', home / 'AppData/Roaming'))
        places += [appdata / 'Microsoft/Windows/Start Menu/Programs']
        names = [f'{old}.lnk' for old in OLD_NAMES]
    else:
        places += [Path(os.environ.get('XDG_DATA_HOME',
                                       home / '.local/share')) / 'applications']
        names = [f'{old}{ending}'
                 for old in OLD_NAMES
                 for ending in ('.desktop', '.app')
                 ]
    for place in places:
        for name in names:
            target = place / name
            try:
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.exists():
                    target.unlink()
            except OSError:
                pass


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


# ---- _remote_renamer -----------------------------------------------------------------
def _remote_renamer() -> None:
    """
    ---- Summary ----
    Helper function to point the git remote of an old install at the renamed
    repository, so updates no longer depend on GitHub's redirect from the old name. The
    remote is only changed when the new address answers.

    ---- Inputs ----
    None.

    ---- Globals read ----
    OLD_NAMES, REPOSITORY_NAME (module constants).

    ---- Outputs ----
    None
        Nothing. Any problem leaves the remote as it was.

    ---- Globals mutated ----
    None. May change the git remote of the folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    """

    try:
        shown = _command_runner(['git', 'remote', 'get-url', 'origin'])
        url = shown.stdout.strip()
        old = next((o for o in OLD_NAMES if o.lower() in url.lower()), None)
        if shown.returncode != 0 or old is None:
            return
        start = url.lower().rindex(old.lower())
        new_url = url[:start] + REPOSITORY_NAME + url[start + len(old):]
        if _command_runner(['git', 'ls-remote', new_url, 'HEAD'],
                           timeout=20).returncode == 0:
            _command_runner(['git', 'remote', 'set-url', 'origin', new_url])
    except Exception:
        pass


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
            label.configure(text=messages.get())
        root.after(100, poll)

    def show(text: str) -> None:
        messages.put(text)

    show.mainloop = lambda: (poll(), root.mainloop())  # type: ignore[attr-defined]
    show.close = lambda: root.after(0, root.destroy)  # type: ignore[attr-defined]
    return show


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- environment_builder -------------------------------------------------------------
def environment_builder(show: Callable[[str], None]) -> None:
    """
    ---- Summary ----
    Main function to make sure the private Python environment exists and has every
    package the program needs, installing them the first time (needs internet).

    ---- Inputs ----
    show : Callable[[str], None]
        Function that shows a line of progress text.

    ---- Globals read ----
    ROOT, ENVIRONMENT, ENVIRONMENT_PYTHON, MINIMUM_TK, REQUIRED_IMPORTS (module
    constants).

    ---- Outputs ----
    None
        Nothing. Raises RuntimeError with a readable message when it fails.

    ---- Globals mutated ----
    None. Creates the environment folder and installs packages (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    _python_finder
    _tk_version_getter
    """

    if ENVIRONMENT_PYTHON.exists() and (
        (_tk_version_getter(str(ENVIRONMENT_PYTHON)) or 0) < MINIMUM_TK
    ):
        better = _python_finder()
        if better and (_tk_version_getter(better) or 0) >= MINIMUM_TK:
            show('Rebuilding the environment with a newer Python ...')
            shutil.rmtree(ENVIRONMENT, ignore_errors=True)
    if ENVIRONMENT_PYTHON.exists():
        ready = _command_runner([str(ENVIRONMENT_PYTHON), '-c', REQUIRED_IMPORTS])
        if ready.returncode == 0:
            return
        show('Updating the packages ...')
    else:
        show('First run: setting things up (a minute or two, needs internet) ...')
        python = _python_finder()
        if python is None:
            raise RuntimeError('Python 3.9 or newer was not found. Install it from '
                               'https://www.python.org/downloads/ and open '
                               f'{APP_NAME} again.')
        made = _command_runner([python, '-m', 'venv', str(ENVIRONMENT)])
        if made.returncode != 0:
            shutil.rmtree(ENVIRONMENT, ignore_errors=True)
            raise RuntimeError('The private Python environment could not be created.\n'
                               + made.stderr[-600:])
    show('Installing the packages ...')
    command = [str(ENVIRONMENT_PYTHON), '-m', 'pip', 'install', '--quiet',
               '--disable-pip-version-check', '-r', str(ROOT / 'requirements.txt')]
    installed = _command_runner(command)
    if installed.returncode != 0:
        if not (ENVIRONMENT / '.complete').exists():
            shutil.rmtree(ENVIRONMENT, ignore_errors=True)
        raise RuntimeError('The packages could not be installed. Check the internet '
                           'connection and try again.\n' + installed.stderr[-600:])
    (ENVIRONMENT / '.complete').write_text('ok')


# ---- launcher_runner -----------------------------------------------------------------
def launcher_runner(show: Callable[[str], None]) -> int:
    """
    ---- Summary ----
    Main function to do every launcher step in order and report a failure in a
    message box.

    ---- Inputs ----
    show : Callable[[str], None]
        Function that shows a line of progress text.

    ---- Globals read ----
    APP_NAME, ENVIRONMENT, ENVIRONMENT_PYTHON, LOG_FILE, MINIMUM_TK, WAIT_SECONDS
    (module constants).

    ---- Outputs ----
    int
        0 when the program started, 1 otherwise.

    ---- Globals mutated ----
    None. Starts the program and may restart this launcher (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _message_shower
    _tk_version_getter
    environment_builder
    program_starter
    shortcut_maker
    update_checker
    """

    try:
        show('Checking for updates ...')
        if update_checker():
            environment = dict(os.environ, PORTIMAO_UPDATED='1')
            subprocess.Popen([sys.executable, str(Path(__file__).resolve())],
                             env=environment)
            return 0
        environment_builder(show)
        tk_version = _tk_version_getter(str(ENVIRONMENT_PYTHON))
        if tk_version is None or tk_version < MINIMUM_TK:
            reason = ('has no Tk (its window toolkit)'
                      if tk_version is None
                      else f'uses Tk {tk_version:g}, which draws blank windows'
                      )
            _message_shower(f'{APP_NAME} needs a newer Python',
                            f'The Python found on this computer {reason}. Install '
                            f'Python 3.12 or newer from '
                            f'https://www.python.org/downloads/ (it includes a good '
                            f'Tk), then delete the hidden folder '
                            f'{ENVIRONMENT.name} inside the {APP_NAME} folder and open '
                            f'{APP_NAME} again.')
            return 1
        shortcut_maker()
        show(f'Opening {APP_NAME} ...')
        process = program_starter()
        deadline = time.time() + WAIT_SECONDS
        while time.time() < deadline and process.poll() is None:
            time.sleep(0.2)
        if process.poll() not in (None, 0):
            tail = LOG_FILE.read_text(encoding='utf-8', errors='replace')[-700:]
            _message_shower(f'{APP_NAME} could not start',
                            f'The program stopped straight away.\n\n{tail}')
            return 1
        return 0
    except Exception as exc:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.write_text(traceback.format_exc(), encoding='utf-8')
        _message_shower(f'{APP_NAME} could not start', str(exc))
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
def program_starter() -> 'subprocess.Popen':
    """
    ---- Summary ----
    Main function to start the program in the private environment, with no terminal
    window. What it prints goes to logs/launch.log.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, LOG_FILE, ENVIRONMENT_PYTHON, ENVIRONMENT_WINDOWLESS, IS_WINDOWS.

    ---- Outputs ----
    subprocess.Popen
        The running program.

    ---- Globals mutated ----
    None. Starts a process and writes the log file (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, 'w', encoding='utf-8')
    program = str(ROOT / 'main.py')
    environment = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    if IS_WINDOWS:
        python = ENVIRONMENT_WINDOWLESS
        if not python.exists():
            python = ENVIRONMENT_PYTHON
        flags = HIDDEN | getattr(subprocess, 'DETACHED_PROCESS', 0)
        return subprocess.Popen([str(python), program], cwd=ROOT, env=environment,
                                stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                creationflags=flags)
    return subprocess.Popen([str(ENVIRONMENT_PYTHON), program], cwd=ROOT,
                            env=environment, stdin=subprocess.DEVNULL, stdout=log,
                            stderr=log, start_new_session=True)


# ---- shortcut_maker ------------------------------------------------------------------
def shortcut_maker() -> None:
    """
    ---- Summary ----
    Main function to make the clickable icon the first time (and again if the folder
    is moved): Desktop and Start menu shortcuts on Windows, an entry in the applications
    menu and on the Desktop on Linux. A Mac uses the Portimao.app in the folder.

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
    _old_shortcut_remover
    """

    try:
        if SHORTCUT_MARK.exists() and SHORTCUT_MARK.read_text() == str(ROOT):
            return
        _old_shortcut_remover()
        if IS_WINDOWS:
            script = ROOT / 'launchers' / 'make_shortcut.ps1'
            windowless = Path(sys.executable).with_name('pythonw.exe')
            target = windowless if windowless.exists() else Path(sys.executable)
            _command_runner(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                             '-WindowStyle', 'Hidden', '-File', str(script),
                             str(ROOT), str(target), str(ROOT / 'Portimao.pyw')])
        elif sys.platform.startswith('linux'):
            entry = (f'[Desktop Entry]\nType=Application\nName={APP_NAME}\n'
                     'Comment=Convert chamber .paf files to figures and data\n'
                     f'Exec={shutil.which("python3") or "python3"} '
                     f'"{ROOT / "launchers" / "bootstrap.pyw"}"\n'
                     f'Path={ROOT}\nIcon={ROOT / "assets" / "icon.png"}\n'
                     'Terminal=false\nCategories=Science;Education;\n')
            menu = Path(os.environ.get('XDG_DATA_HOME',
                                       Path.home() / '.local/share')) / 'applications'
            for folder in (menu, Path.home() / 'Desktop'):
                if folder.is_dir() or folder == menu:
                    folder.mkdir(parents=True, exist_ok=True)
                    path = folder / f'{APP_NAME}.desktop'
                    path.write_text(entry, encoding='utf-8')
                    path.chmod(0o755)
                    if shutil.which('gio'):
                        _command_runner(['gio', 'set', str(path),
                                         'metadata::trusted', 'true'])
        SHORTCUT_MARK.write_text(str(ROOT))
    except Exception:  # a missing shortcut must never stop the program
        pass


# ---- update_checker ------------------------------------------------------------------
def update_checker() -> bool:
    """
    ---- Summary ----
    Main function to install a newer version from GitHub when this folder is a git
    clone and one is available. Anything that goes wrong (no internet, files edited
    here) is ignored and the current version runs.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT (module constant); os.environ["PORTIMAO_UPDATED"].

    ---- Outputs ----
    bool
        True when an update was installed, so the launcher must start again.

    ---- Globals mutated ----
    None. May change the files of the program (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_runner
    _remote_renamer
    """

    if not (ROOT / '.git').exists() or os.environ.get('PORTIMAO_UPDATED'):
        return False
    if shutil.which('git') is None:
        return False
    try:
        _remote_renamer()
        if _command_runner(['git', 'fetch', '--quiet'], timeout=20).returncode != 0:
            return False
        behind = _command_runner(['git', 'rev-list', '--count', 'HEAD..@{u}'])
        if behind.returncode != 0 or int(behind.stdout.strip() or 0) == 0:
            return False
        return _command_runner(['git', 'pull', '--ff-only', '--quiet']).returncode == 0
    except Exception:
        return False


if __name__ == '__main__':
    sys.exit(main())
