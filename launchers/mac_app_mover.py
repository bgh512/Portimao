"""
Moves a Mac install of the old launcher to the Mac app, and makes the Desktop file of a
Mac that cannot run the app.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import platform
import shlex
import shutil
import stat
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple


# ---- CONSTANTS -----------------------------------------------------------------------
APP_NAME = 'Portimao.app'  # the app, and the old launcher's link on the Desktop
COMMAND_NAME = 'Portimao.command'  # the Desktop file of a Mac that cannot run the app
COMMAND_MARK = '# Starts Portimao from its folder: '  # how our Desktop file is known
INSTALLER_NAME = 'install_mac.sh'  # in the program folder
# the app's own folder in the home folder (OWN_FOLDER_NAME in utils_shared/user_places.py)
OWN_FOLDER_NAME = 'Portimao'
FITS_FOLDER_NAME = 'fits'
LAST_ANSWERS_NAME = 'last_answers.json'
KEPT_FOLDERS = (FITS_FOLDER_NAME,)  # git tracks them, but the user adds to them
# what the program made beside the files git tracks; .git last, as git lists the rest
PROGRAM_EXTRAS = ('.venv_unix',
                  '.venv',
                  '.portimao_shortcut',
                  '.shortcut_made',
                  '.shortcut_made_portimao',
                  '.pytest_cache',
                  '.ruff_cache',
                  '.git',
                  )
LOG_NAME = 'move_to_app.log'  # in the folder's logs folder, which is kept
MAIN_BRANCH = 'main'  # the user download; any other branch is a developer's copy
OLDEST_MACOS = 14  # the numpy and scipy builds the app carries need macOS 14
SELF_TEST_SWITCH = 'PORTIMAO_SELF_TEST'
# only matters when the tests run git on Windows: no window flashes up
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ---- MOVE HELPERS --------------------------------------------------------------------


# ---- _app_opener ---------------------------------------------------------------------
def _app_opener(app: Path) -> None:
    """
    ---- Summary ----
    Helper function to open the app as a click does, passing on the check switch when it
    is set, so the Mac check follows the move through to the app's self-test.

    ---- Inputs ----
    app : Path
        The installed .app folder.

    ---- Globals read ----
    SELF_TEST_SWITCH (module constant); os.environ['PORTIMAO_SELF_TEST'].

    ---- Outputs ----
    None
        Nothing. Raises OSError when macOS's open cannot be run.

    ---- Globals mutated ----
    None. Starts the app (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    command = ['open']
    switch = os.environ.get(SELF_TEST_SWITCH)
    if switch:
        command += ['-n', '--env', f'{SELF_TEST_SWITCH}={switch}']
    subprocess.Popen(command + [str(app)],
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session=True,
                     )


# ---- _command_text_maker -------------------------------------------------------------
def _command_text_maker(root: Path, python: str) -> str:
    """
    ---- Summary ----
    Helper function to write the Desktop file that starts Portimao the old way: the
    launcher with the Python that runs it now, or run.sh when that Python has gone.

    ---- Inputs ----
    root : Path
        The program folder.
    python : str
        Path of the Python running the launcher.

    ---- Globals read ----
    COMMAND_MARK (module constant).

    ---- Outputs ----
    str
        The text of the file, a shell script; its second line names the folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    folder = shlex.quote(str(root))
    program = shlex.quote(python)
    return ('#!/bin/sh\n'
            f'{COMMAND_MARK}{root}\n'
            '# Made by its launcher on a Mac that does not run the Portimao app; a\n'
            '# Terminal window opens while it starts.\n'
            f'cd {folder} || exit 1\n'
            'mkdir -p logs\n'
            f'if [ -x {program} ]; then\n'
            f'    nohup {program} launchers/bootstrap.pyw >>logs/launcher_errors.log 2>&1 &\n'
            'else\n'
            '    sh run.sh\n'
            'fi\n'
            )


# ---- _desktop_link_mover -------------------------------------------------------------
def _desktop_link_mover(root: Path,
                        home: Path,
                        app: Path,
                        log: Callable[[str], None],
                        ) -> None:
    """
    ---- Summary ----
    Helper function to point the Desktop at the app: the old launcher's link, or our
    Desktop file, is replaced by a link to the app with the same name, so a double-click
    where the user is used to opens the app. With neither there, nothing is added.

    ---- Inputs ----
    root : Path
        The program folder being moved.
    home : Path
        The home folder.
    app : Path
        The installed .app folder.
    log : Callable[[str], None]
        Adds a line to the move log.

    ---- Globals read ----
    APP_NAME, COMMAND_NAME (module constants).

    ---- Outputs ----
    None
        Nothing. A Desktop that cannot be changed is left as it is (logged).

    ---- Globals mutated ----
    None. Deletes and makes links on the Desktop (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _link_into_checker
    _our_command_checker
    """

    desktop = home / 'Desktop'
    link = desktop / APP_NAME
    command = desktop / COMMAND_NAME
    try:
        had_one = False
        if _link_into_checker(link, root):
            link.unlink()
            had_one = True
        if _our_command_checker(command, root):
            command.unlink()
            had_one = True
        if had_one and not os.path.lexists(link):
            link.symlink_to(app)
            log(f'The Desktop link now opens {app}.')
    except OSError as exc:
        log(f'The Desktop link could not be changed ({exc.strerror}).')


# ---- _git_runner ---------------------------------------------------------------------
def _git_runner(root: Path, arguments: List[str]) -> 'subprocess.CompletedProcess':
    """
    ---- Summary ----
    Helper function to run a git command in the program folder and keep its output.

    ---- Inputs ----
    root : Path
        The program folder.
    arguments : List[str]
        What follows `git`.

    ---- Globals read ----
    HIDDEN (module constant).

    ---- Outputs ----
    subprocess.CompletedProcess
        The finished command; its return code is 127 when git cannot be run.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    command = ['git', '-C', str(root), *arguments]
    try:
        return subprocess.run(command,
                              capture_output=True,
                              text=True,
                              encoding='utf-8',
                              errors='replace',
                              creationflags=HIDDEN,
                              )
    except OSError as exc:
        return subprocess.CompletedProcess(command, 127, '', str(exc))


# ---- _installer_runner ---------------------------------------------------------------
def _installer_runner(root: Path,
                      home: Path,
                      show: Callable[[str], None],
                      log: Callable[[str], None],
                      ) -> Tuple[Optional[Path], str]:
    """
    ---- Summary ----
    Helper function to install the app with the program's own install_mac.sh, as the
    install line does, but without opening it; each line it prints is shown and logged.

    ---- Inputs ----
    root : Path
        The program folder, which holds install_mac.sh.
    home : Path
        The home folder; the app goes in its Applications folder.
    show : Callable[[str], None]
        Shows a line of progress.
    log : Callable[[str], None]
        Adds a line to the move log.

    ---- Globals read ----
    APP_NAME, INSTALLER_NAME (module constants).

    ---- Outputs ----
    Tuple[Optional[Path], str]
        (the installed .app folder, '') or (None, why it was not installed).

    ---- Globals mutated ----
    None. Downloads and installs the app (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _reason_shortener
    """

    command = ['/bin/bash', str(root / INSTALLER_NAME), '--no-open']
    try:
        process = subprocess.Popen(command,
                                   cwd=root,
                                   env=dict(os.environ, HOME=str(home)),
                                   stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   encoding='utf-8',
                                   errors='replace',
                                   )
    except OSError as exc:
        return None, f'the install could not be run ({exc.strerror})'
    last = ''
    for line in process.stdout or []:
        text = line.strip()
        if text:
            last = text
            log(text)
            show(text)
    process.wait()
    app = home / 'Applications' / APP_NAME
    if process.returncode != 0 or not app.is_dir():
        return None, _reason_shortener(
            last,
            ) or f'the install ended with {process.returncode}'
    return app, ''


# ---- _link_into_checker --------------------------------------------------------------
def _link_into_checker(link: Path, root: Path) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a Desktop item is the old launcher's link: a symbolic
    link to something inside the program folder (its Portimao.app, which the update has
    taken away).

    ---- Inputs ----
    link : Path
        The Desktop item.
    root : Path
        The program folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when it is a link into the program folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not link.is_symlink():
        return False
    try:
        target = os.readlink(link)
    except OSError:
        return False
    target_path = os.path.realpath(os.path.join(link.parent, target))
    root_path = os.path.realpath(root)
    return target_path == root_path or target_path.startswith(root_path + os.sep)


# ---- _log_opener ---------------------------------------------------------------------
def _log_opener(root: Path) -> Callable[[str], None]:
    """
    ---- Summary ----
    Helper function to give the function that adds a line, with the date and time, to
    the move log in the folder's logs folder (which the move keeps).

    ---- Inputs ----
    root : Path
        The program folder.

    ---- Globals read ----
    LOG_NAME (module constant).

    ---- Outputs ----
    Callable[[str], None]
        Adds one line. A log that cannot be written just loses its lines.

    ---- Globals mutated ----
    None. Writes the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    path = root / 'logs' / LOG_NAME

    def add(text: str) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'a', encoding='utf-8') as log:
                log.write(f'{datetime.now():%Y-%m-%d %H:%M:%S} {text}\n')
        except OSError:
            pass

    return add


# ---- _macos_too_old_checker ----------------------------------------------------------
def _macos_too_old_checker(version: str) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a macOS version is too old for the app.

    ---- Inputs ----
    version : str
        The macOS version, for example "13.6"; empty when not known.

    ---- Globals read ----
    OLDEST_MACOS (module constant).

    ---- Outputs ----
    bool
        True when it is older than macOS 14; False when newer or unreadable.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    major = version.strip().split('.')[0]
    return major.isdigit() and int(major) < OLDEST_MACOS


# ---- _macos_version_reader -----------------------------------------------------------
def _macos_version_reader() -> str:
    """
    ---- Summary ----
    Helper function to read this Mac's macOS version from sw_vers, which gives the real
    one where a Python built for older Macs is told "10.16".

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The version, for example "15.1"; Python's own reading when sw_vers cannot be
        run, empty when neither knows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        asked = subprocess.run(['sw_vers', '-productVersion'],
                               capture_output=True,
                               text=True,
                               )
    except OSError:
        return platform.mac_ver()[0]
    return asked.stdout.strip() if asked.returncode == 0 else platform.mac_ver()[0]


# ---- _note_shower --------------------------------------------------------------------
def _note_shower(text: str, shows_messages: bool) -> None:
    """
    ---- Summary ----
    Helper function to show a macOS message that holds nothing up: the launcher goes on
    (or closes) while it is on screen.

    ---- Inputs ----
    text : str
        The message.
    shows_messages : bool
        False to show nothing (for the tests).

    ---- Globals read ----
    SELF_TEST_SWITCH (module constant); os.environ['PORTIMAO_SELF_TEST'].

    ---- Outputs ----
    None
        Nothing. No message is shown with the check switch, or where macOS's message
        cannot be shown.

    ---- Globals mutated ----
    None. Shows a message (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not shows_messages or os.environ.get(SELF_TEST_SWITCH):
        return
    quoted = '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'
    script = (f'display dialog {quoted} with title "Portimao" buttons {{"OK"}} '
              'default button "OK" with icon note'
              )
    try:
        subprocess.Popen(['osascript', '-e', script],
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True,
                         )
    except OSError:  # no macOS message here: the move log still says it
        pass


# ---- _our_command_checker ------------------------------------------------------------
def _our_command_checker(command: Path, root: Path) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a Desktop file is the one made for this program
    folder (by desktop_file_maker).

    ---- Inputs ----
    command : Path
        The Desktop file.
    root : Path
        The program folder.

    ---- Globals read ----
    COMMAND_MARK (module constant).

    ---- Outputs ----
    bool
        True when it is a file whose mark names this folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if command.is_symlink() or not command.is_file():
        return False
    try:
        text = command.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False
    return f'{COMMAND_MARK}{root}\n' in text


# ---- _program_file_lister ------------------------------------------------------------
def _program_file_lister(root: Path) -> Optional[List[Path]]:
    """
    ---- Summary ----
    Helper function to list the old program files: what git tracks, apart from the fits
    and any file the user has changed, then what the program made beside them (its
    Python environment, its marks and caches) and git's own folder.

    ---- Inputs ----
    root : Path
        The program folder, a git clone.

    ---- Globals read ----
    KEPT_FOLDERS, PROGRAM_EXTRAS (module constants).

    ---- Outputs ----
    Optional[List[Path]]
        The files and folders to take away, git's folder last; None when git could not
        list them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _git_runner
    """

    tracked = _git_runner(root, ['ls-files', '-z'])
    edited = _git_runner(root, ['ls-files', '-m', '-z'])
    if tracked.returncode != 0 or edited.returncode != 0:
        return None
    kept = set(edited.stdout.split('\0'))
    files = [root / name
             for name in tracked.stdout.split('\0')
             if name and name not in kept and name.split('/', 1)[0] not in KEPT_FOLDERS
             ]
    extras = [root / name for name in PROGRAM_EXTRAS if os.path.lexists(root / name)]
    return files + extras


# ---- _program_file_remover -----------------------------------------------------------
def _program_file_remover(root: Path,
                          paths: List[Path],
                          log: Callable[[str], None],
                          ) -> None:
    """
    ---- Summary ----
    Helper function to take away the old program files, then the folders they leave
    empty (or holding only Python's caches). Nothing outside the program folder is
    touched, and a link is taken away without following it.

    ---- Inputs ----
    root : Path
        The program folder.
    paths : List[Path]
        The files and folders to take away (_program_file_lister).
    log : Callable[[str], None]
        Adds a line to the move log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. What cannot be taken away is left and named in the log.

    ---- Globals mutated ----
    None. Deletes files and folders (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _tree_remover
    """

    # ---- 1 The files and folders -----------------------------------------------------
    root_path = os.path.realpath(root)
    removed = 0
    problems = []
    folders = set()
    for path in paths:
        parent = os.path.realpath(path.parent)
        if parent != root_path and not parent.startswith(root_path + os.sep):
            problems.append(f'{path} (outside the folder)')
            continue
        try:
            if path.is_dir() and not path.is_symlink():
                _tree_remover(path)
            else:
                path.unlink()
        except FileNotFoundError:
            continue
        except OSError as exc:
            problems.append(f'{path.relative_to(root)} ({exc.strerror})')
            continue
        removed += 1
        folders.add(path.parent)

    # ---- 2 The folders left empty, deepest first -------------------------------------
    for folder in sorted(folders, key=lambda f: len(f.parts), reverse=True):
        while folder != root and root in folder.parents:
            shutil.rmtree(folder / '__pycache__', ignore_errors=True)
            try:
                folder.rmdir()
            except OSError:  # something of the user's is still in it
                break
            folder = folder.parent
    log(f'Took away {removed} old program files and folders.')
    if problems:
        log('Could not take away: ' + '; '.join(problems))


# ---- _reason_shortener ---------------------------------------------------------------
def _reason_shortener(sentence: str) -> str:
    """
    ---- Summary ----
    Helper function to keep what went wrong from one of install_mac.sh's sentences,
    which say what went wrong, a colon, then what to do on the command line.

    ---- Inputs ----
    sentence : str
        The last line the install printed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The part before the colon, without a full stop; empty for an empty line.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return sentence.split(':', 1)[0].strip().rstrip('.')


# ---- _tree_remover -------------------------------------------------------------------
def _tree_remover(folder: Path) -> None:
    """
    ---- Summary ----
    Helper function to delete a folder with everything in it, read-only files included
    (git keeps its files read-only, which Windows would refuse to delete).

    ---- Inputs ----
    folder : Path
        The folder; not a link.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. Raises OSError when it cannot be deleted.

    ---- Globals mutated ----
    None. Deletes files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for place, _, names in os.walk(folder):
        for name in names:
            path = os.path.join(place, name)
            if not os.path.islink(path):
                os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    shutil.rmtree(folder)


# ---- _user_things_copier -------------------------------------------------------------
def _user_things_copier(root: Path,
                        own_folder: Path,
                        log: Callable[[str], None],
                        ) -> None:
    """
    ---- Summary ----
    Helper function to copy the user's fits and last answers from a program folder that
    is not the app's own folder into it, so the app finds them. A file already there is
    never overwritten; the data folders stay where they are.

    ---- Inputs ----
    root : Path
        The program folder being moved.
    own_folder : Path
        The app's own folder (Portimao in the home folder); made when missing.
    log : Callable[[str], None]
        Adds a line to the move log.

    ---- Globals read ----
    FITS_FOLDER_NAME, LAST_ANSWERS_NAME (module constants).

    ---- Outputs ----
    None
        Nothing. What cannot be copied is named in the log.

    ---- Globals mutated ----
    None. Makes folders and copies files (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        (own_folder / FITS_FOLDER_NAME).mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log(f'{own_folder} could not be made ({exc.strerror}), so nothing was copied.')
        return
    sources = sorted((root / FITS_FOLDER_NAME).glob('*.csv'))
    sources += [root / LAST_ANSWERS_NAME]
    copied = []
    for source in sources:
        target = own_folder / source.relative_to(root)
        if not source.is_file() or target.exists():
            continue
        try:
            shutil.copy2(source, target)
        except OSError as exc:
            log(f'{source} could not be copied ({exc.strerror}).')
            continue
        copied.append(source.relative_to(root).as_posix())
    log(f"Copied into {own_folder}: {', '.join(copied) if copied else 'nothing new'}.")


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- app_mover -----------------------------------------------------------------------
def app_mover(root: Path,
              home: Path,
              show: Callable[[str], None],
              macos_version: Optional[str] = None,
              installer: Optional[Callable[...,
                                           Tuple[Optional[Path], str],
                                           ]] = None,
              opener: Optional[Callable[[Path], None]] = None,
              shows_messages: bool = True,
              ) -> bool:
    """
    ---- Summary ----
    Main function to move an install of the old launcher to the Mac app, at its first
    start after the update, without asking. Only a git clone on main (the user
    download) on macOS 14 or newer is moved. The app is installed in the user's own
    Applications folder first, and nothing is taken away unless it is in. Then the old
    program files go; the fits, the data folders, the logs, the last answers, any
    program file the user changed and anything else of theirs stay. The Desktop link
    opens the app from then on, the app opens at once and a note beside it says where
    the user's things are. Every step is written to logs/move_to_app.log.

    ---- Inputs ----
    root : Path
        The program folder.
    home : Path
        The home folder.
    show : Callable[[str], None]
        Shows a line in the launcher's small window.
    macos_version : Optional[str]
        The macOS version; None for this Mac's.
    installer : Optional[Callable[..., Tuple[Optional[Path], str]]]
        Installs the app, called with (root, home, show, log); None for install_mac.sh
        (the tests give their own).
    opener : Optional[Callable[[Path], None]]
        Opens the app; None for macOS's open.
    shows_messages : bool
        False to show no message (for the tests).

    ---- Globals read ----
    OWN_FOLDER_NAME (module constant).

    ---- Outputs ----
    bool
        True when the app is installed and opening, so the launcher closes; False when
        this install is not moved, or the app could not be installed (a note says so),
        so the program starts the old way.

    ---- Globals mutated ----
    None. Installs the app, deletes the old program files, copies files, changes the
    Desktop link, opens the app and writes the move log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_opener
    _desktop_link_mover
    _installer_runner
    _log_opener
    _macos_version_reader
    _note_shower
    _program_file_lister
    _program_file_remover
    _user_things_copier
    move_blocker_finder
    """

    # ---- 1 Check this install is moved -----------------------------------------------
    version = _macos_version_reader() if macos_version is None else macos_version
    if move_blocker_finder(root, version) is not None:
        return False
    log = _log_opener(root)
    log(f'Moving {root} to the Mac app (macOS {version}).')
    show('Portimao is now a Mac app: installing it in your Applications folder ...')

    # ---- 2 Install the app; nothing is taken away unless it is in --------------------
    app, problem = (installer or _installer_runner)(root, home, show, log)
    if app is None:
        log(f'The app was not installed ({problem}): starting the old way.')
        _note_shower(
            f'Portimao could not move to the Mac app ({problem}), so it starts '
            f'the old way this time, from the Portimao file on your Desktop; it '
            f'tries again at the next start.',
            shows_messages,
            )
        return False

    # ---- 3 Take away the old program files -------------------------------------------
    show('Taking away the old program files ...')
    paths = _program_file_lister(root)
    if paths is None:
        log('git could not list the program files, so none were taken away.')
    else:
        _program_file_remover(root, paths, log)

    # ---- 4 Point the app at the user's things and the Desktop at the app -------------
    own_folder = home / OWN_FOLDER_NAME
    if os.path.realpath(own_folder) != os.path.realpath(root):
        _user_things_copier(root, own_folder, log)
    _desktop_link_mover(root, home, app, log)

    # ---- 5 Open the app --------------------------------------------------------------
    try:
        (opener or _app_opener)(app)
    except OSError as exc:
        log(f'The app could not be opened ({exc.strerror}).')
    _note_shower(
        f'Portimao is now a Mac app, in your Applications folder, and updates '
        f'itself. Open it as before from the Desktop, or from Launchpad or '
        f'Spotlight. Your fits, data folders, logs and last answers are still in '
        f'{root}; only the old program files were taken away.',
        shows_messages,
        )
    log(f'Moved: {app} is opening.')
    return True


# ---- desktop_file_maker --------------------------------------------------------------
def desktop_file_maker(root: Path,
                       home: Path,
                       python: str,
                       is_first: bool,
                       macos_version: Optional[str] = None,
                       shows_messages: bool = True,
                       ) -> bool:
    """
    ---- Summary ----
    Main function to give a Mac that runs Portimao from its folder (older than macOS
    14, a move that failed, a developer's copy) a file on the Desktop that starts it the
    old way. It takes the place of the old launcher's link, which the update made
    useless, and is made the first time a folder is started; on macOS older than 14 a
    note says why, once.

    ---- Inputs ----
    root : Path
        The program folder.
    home : Path
        The home folder.
    python : str
        Path of the Python running the launcher.
    is_first : bool
        True the first time this folder is started (the launcher's shortcut mark).
    macos_version : Optional[str]
        The macOS version; None for this Mac's.
    shows_messages : bool
        False to show no message (for the tests).

    ---- Globals read ----
    APP_NAME, COMMAND_NAME (module constants).

    ---- Outputs ----
    bool
        True when the old launcher's link was replaced.

    ---- Globals mutated ----
    None. Writes the Desktop file and deletes the old link (side effects). Raises
    OSError when the Desktop cannot be changed.

    ---- Equations ----
    None.

    ---- Helpers ----
    _command_text_maker
    _link_into_checker
    _macos_too_old_checker
    _macos_version_reader
    _note_shower
    """

    desktop = home / 'Desktop'
    link = desktop / APP_NAME
    command = desktop / COMMAND_NAME
    is_replaced = _link_into_checker(link, root)
    if not desktop.is_dir() or not (is_replaced or (is_first and not command.exists())):
        return False
    if is_replaced:
        link.unlink()
    command.write_text(_command_text_maker(root, python), encoding='utf-8')
    command.chmod(0o755)
    version = _macos_version_reader() if macos_version is None else macos_version
    if is_replaced and _macos_too_old_checker(version):
        _note_shower(f'This Mac has macOS {version} and the Portimao app needs macOS '
                     f'14 or newer, so Portimao starts the old way, from the Portimao '
                     f'file on your Desktop (a Terminal window opens while it starts).',
                     shows_messages,
                     )
    return is_replaced


# ---- move_blocker_finder -------------------------------------------------------------
def move_blocker_finder(root: Path, macos_version: str) -> Optional[str]:
    """
    ---- Summary ----
    Main function to say why this install is not moved to the app. Only the user
    download is moved: a git clone on main, with its install script, on macOS 14 or
    newer. A developer's copy on another branch, and a copy from a zip file, are left
    as they are.

    ---- Inputs ----
    root : Path
        The program folder.
    macos_version : str
        The macOS version, for example "15.1".

    ---- Globals read ----
    INSTALLER_NAME, MAIN_BRANCH, OLDEST_MACOS (module constants).

    ---- Outputs ----
    Optional[str]
        Why it is not moved, in plain words; None when it is.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _git_runner
    _macos_too_old_checker
    """

    if _macos_too_old_checker(macos_version):
        return (f'this Mac has macOS {macos_version}, and the app needs macOS '
                f'{OLDEST_MACOS} or newer')
    if not (root / '.git').exists() or shutil.which('git') is None:
        return 'it was not installed with git'
    branch = _git_runner(root, ['rev-parse', '--abbrev-ref', 'HEAD'])
    if branch.returncode != 0 or branch.stdout.strip() != MAIN_BRANCH:
        return 'it is a developer copy, not on main'
    if not (root / INSTALLER_NAME).is_file():
        return 'its install script is missing'
    return None
