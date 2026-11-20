"""
Tests that an install of the old launcher on a Mac is moved to the app: what goes, what
stays, and when it is not moved.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from launchers.mac_app_mover import (COMMAND_MARK,
                                     app_mover,
                                     desktop_file_maker,
                                     move_blocker_finder,
                                     )


# ---- CONSTANTS -----------------------------------------------------------------------
pytestmark = pytest.mark.skipif(shutil.which('git') is None, reason='no git here')
NEW_MACOS = '15.1'
OLD_MACOS = '13.6'
PYTHON = '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3'
# the program's files, as git tracks them in the made-up install
TRACKED = {
    'main.py': 'program',
    'config.py': 'program',
    'install_mac.sh': 'script',
    '.gitignore': 'logs/\n/data_*/\nlast_answers.json\n.venv_unix/\n__pycache__/\n',
    'utils_shared/reader.py': 'program',
    'launchers/bootstrap.pyw': 'program',
    'fits/standard.csv': 'fit',
    }
# what the user and the program added later, which git does not track
ADDED = {'fits/own_fit.csv': 'own fit',
         'data_check/run1.paf': 'run',
         'logs/launch.log': 'log',
         'last_answers.json': '{}',
         'results_mine/figure.png': 'figure',
         '.venv_unix/bin/python': 'python',
         'utils_shared/__pycache__/reader.cpython-312.pyc': 'cache',
         '.portimao_shortcut': 'mark',
         }
# on Windows git runs without a window of its own, so the test stays out of sight
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ---- HELPERS -------------------------------------------------------------------------


# ---- _git_runner ---------------------------------------------------------------------
def _git_runner(root: Path, *arguments: str) -> None:
    """
    ---- Summary ----
    Helper function to run a git command in the made-up install, as a test user.

    ---- Inputs ----
    root : Path
        The made-up install.
    *arguments : str
        What follows `git`.

    ---- Globals read ----
    HIDDEN (module constant).

    ---- Outputs ----
    None
        Nothing. The test fails when git fails.

    ---- Globals mutated ----
    None. Changes the git copy (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    subprocess.run(['git',
                    '-C',
                    str(root),
                    '-c',
                    'user.name=Test',
                    '-c',
                    'user.email=test@example.invalid',
                    '-c',
                    'commit.gpgsign=false',
                    *arguments,
                    ],
                   check=True,
                   capture_output=True,
                   creationflags=HIDDEN,
                   )


# ---- _installer_faker ----------------------------------------------------------------
def _installer_faker(is_installed: bool,
                     calls: List[Path],
                     ) -> Callable[..., Tuple[Optional[Path], str]]:
    """
    ---- Summary ----
    Helper function to give a stand-in for install_mac.sh, which makes a small app in
    the user's own Applications folder, or fails as a download with no internet does.

    ---- Inputs ----
    is_installed : bool
        False to fail.
    calls : List[Path]
        Gets the program folder of each call.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Callable[..., Tuple[Optional[Path], str]]
        Called with (root, home, show, log) as the mover calls it.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    def install(root: Path,
                home: Path,
                show: Callable[[str], None],
                log: Callable[[str], None],
                ) -> Tuple[Optional[Path], str]:
        calls.append(root)
        if not is_installed:
            return None, 'Portimao could not be downloaded'
        app = home / 'Applications' / 'Portimao.app'
        (app / 'Contents' / 'MacOS').mkdir(parents=True)
        return app, ''

    return install


# ---- _link_tester --------------------------------------------------------------------
def _link_tester(folder: Path) -> None:
    """
    ---- Summary ----
    Helper function to skip the test where symbolic links cannot be made (Windows
    without the right to make them).

    ---- Inputs ----
    folder : Path
        A folder to try in.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. Skips the test when no link can be made.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        os.symlink(folder / 'nowhere', folder / 'link_try')
    except (OSError, NotImplementedError):
        pytest.skip('symbolic links cannot be made here')
    os.unlink(folder / 'link_try')


# ---- _old_install_maker --------------------------------------------------------------
def _old_install_maker(root: Path, branch: str = 'main') -> Path:
    """
    ---- Summary ----
    Helper function to make an install of the old launcher as a git copy: the program's
    files committed on a branch, then the user's things and the program's own leftovers
    added, and one program file changed by the user.

    ---- Inputs ----
    root : Path
        Folder to make it in.
    branch : str
        The branch it is on.

    ---- Globals read ----
    ADDED, TRACKED (module constants).

    ---- Outputs ----
    Path
        The made-up install.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _git_runner
    """

    for name, text in TRACKED.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding='utf-8')
    _git_runner(root, 'init', '-q')
    _git_runner(root, 'config', 'core.autocrlf', 'false')
    _git_runner(root, 'checkout', '-q', '-b', branch)
    _git_runner(root, 'add', '-A')
    _git_runner(root, 'commit', '-q', '-m', 'program')
    for name, text in ADDED.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding='utf-8')
    (root / 'config.py').write_text('edited by the user', encoding='utf-8')
    return root


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_desktop_file_is_made_once --------------------------------------------------
def test_desktop_file_is_made_once(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a Mac run from its folder gets the Desktop file the
    first time the folder is started, naming the folder and the Python, and that it is
    not made again later once the user has deleted it.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    COMMAND_MARK, OLD_MACOS, PYTHON (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    root = tmp_path / 'Portimao'
    root.mkdir()
    (tmp_path / 'Desktop').mkdir()
    command = tmp_path / 'Desktop' / 'Portimao.command'
    assert not desktop_file_maker(root, tmp_path, PYTHON, True, OLD_MACOS, False)
    text = command.read_text(encoding='utf-8')
    assert f'{COMMAND_MARK}{root}\n' in text
    assert PYTHON in text and 'launchers/bootstrap.pyw' in text
    command.unlink()
    assert not desktop_file_maker(root, tmp_path, PYTHON, False, OLD_MACOS, False)
    assert not command.exists()


# ---- test_desktop_file_replaces_the_old_link -----------------------------------------
def test_desktop_file_replaces_the_old_link(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that on a Mac that cannot run the app, the old launcher's
    link (into the program folder, whose Portimao.app the update took away) is replaced
    by the Desktop file at any start, and that a link the user made elsewhere is left.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    OLD_MACOS, PYTHON (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _link_tester
    """

    _link_tester(tmp_path)
    root = tmp_path / 'Portimao'
    root.mkdir()
    desktop = tmp_path / 'Desktop'
    desktop.mkdir()
    link = desktop / 'Portimao.app'
    os.symlink(root / 'Portimao.app', link)
    assert desktop_file_maker(root, tmp_path, PYTHON, False, OLD_MACOS, False)
    assert not os.path.lexists(link)
    assert (desktop / 'Portimao.command').is_file()
    elsewhere = tmp_path / 'Other' / 'Portimao.app'
    os.symlink(elsewhere, link)
    assert not desktop_file_maker(root, tmp_path, PYTHON, False, OLD_MACOS, False)
    assert os.path.lexists(link)


# ---- test_developer_copy_is_not_moved ------------------------------------------------
def test_developer_copy_is_not_moved(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a git copy on another branch than main (a developer's)
    is not moved and nothing is installed.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    NEW_MACOS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installer_faker
    _old_install_maker
    """

    root = _old_install_maker(tmp_path / 'Portimao', branch='dev')
    calls: List[Path] = []
    assert 'developer copy' in move_blocker_finder(root, NEW_MACOS)
    assert not app_mover(root,
                         tmp_path,
                         lambda text: None,
                         NEW_MACOS,
                         _installer_faker(True, calls),
                         lambda app: None,
                         False,
                         )
    assert calls == []
    assert (root / 'main.py').is_file()


# ---- test_failed_install_takes_nothing_away ------------------------------------------
def test_failed_install_takes_nothing_away(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that when the app cannot be installed, no file is taken
    away, nothing is opened, the program starts the old way and the log says why.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    NEW_MACOS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installer_faker
    _old_install_maker
    """

    root = _old_install_maker(tmp_path / 'Portimao')
    opened: List[Path] = []
    assert not app_mover(root,
                         tmp_path,
                         lambda text: None,
                         NEW_MACOS,
                         _installer_faker(False, []),
                         opened.append,
                         False,
                         )
    assert opened == []
    assert (root / 'main.py').is_file() and (root / '.git').is_dir()
    log = (root / 'logs' / 'move_to_app.log').read_text(encoding='utf-8')
    assert 'The app was not installed (Portimao could not be downloaded)' in log


# ---- test_folder_elsewhere_gets_its_fits_copied --------------------------------------
def test_folder_elsewhere_gets_its_fits_copied(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that an install that is not the app's own folder has its
    fits and last answers copied into the app's own folder, while its data stays.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    NEW_MACOS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installer_faker
    _old_install_maker
    """

    root = _old_install_maker(tmp_path / 'Programs' / 'Portimao')
    assert app_mover(root,
                     tmp_path,
                     lambda text: None,
                     NEW_MACOS,
                     _installer_faker(True, []),
                     lambda app: None,
                     False,
                     )
    own = tmp_path / 'Portimao'
    assert (own / 'fits' / 'own_fit.csv').read_text(encoding='utf-8') == 'own fit'
    assert (own / 'fits' / 'standard.csv').is_file()
    assert (own / 'last_answers.json').is_file()
    assert (root / 'data_check' / 'run1.paf').is_file()
    assert not (own / 'data_check').exists()


# ---- test_move_keeps_the_desktop_link_working ----------------------------------------
def test_move_keeps_the_desktop_link_working(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the move points the old launcher's link on the Desktop
    at the app, and replaces the Desktop file left by an earlier failed move with the
    same link.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    NEW_MACOS, PYTHON (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installer_faker
    _link_tester
    _old_install_maker
    """

    _link_tester(tmp_path)
    root = _old_install_maker(tmp_path / 'Portimao')
    desktop = tmp_path / 'Desktop'
    desktop.mkdir()
    link = desktop / 'Portimao.app'
    os.symlink(root / 'Portimao.app', link)
    assert app_mover(root,
                     tmp_path,
                     lambda text: None,
                     NEW_MACOS,
                     _installer_faker(True, []),
                     lambda app: None,
                     False,
                     )
    app = tmp_path / 'Applications' / 'Portimao.app'
    assert os.path.realpath(link) == os.path.realpath(app)

    # an earlier failed move left the Desktop file in place of the link
    root = _old_install_maker(tmp_path / 'Second' / 'Portimao')
    link.unlink()
    shutil.rmtree(app)
    assert not desktop_file_maker(root, tmp_path, PYTHON, True, NEW_MACOS, False)
    assert app_mover(root,
                     tmp_path,
                     lambda text: None,
                     NEW_MACOS,
                     _installer_faker(True, []),
                     lambda app: None,
                     False,
                     )
    assert not (desktop / 'Portimao.command').exists()
    assert os.path.realpath(link) == os.path.realpath(app)


# ---- test_move_takes_away_only_program_files -----------------------------------------
def test_move_takes_away_only_program_files(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the move installs the app, takes away the files git
    tracks (outside fits), git's folder, the Python environment, the mark and the
    folders left empty, keeps the fits, the data, the logs, the last answers, anything
    else of the user's and the program file they changed, opens the app and logs it.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    ADDED, NEW_MACOS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installer_faker
    _old_install_maker
    """

    root = _old_install_maker(tmp_path / 'Portimao')
    opened: List[Path] = []
    calls: List[Path] = []
    assert app_mover(root,
                     tmp_path,
                     lambda text: None,
                     NEW_MACOS,
                     _installer_faker(True, calls),
                     opened.append,
                     False,
                     )
    assert calls == [root]
    assert opened == [tmp_path / 'Applications' / 'Portimao.app']
    for gone in ('main.py',
                 'install_mac.sh',
                 '.gitignore',
                 'utils_shared',
                 'launchers',
                 '.git',
                 '.venv_unix',
                 '.portimao_shortcut',
                 ):
        assert not (root / gone).exists(), gone
    for kept in ADDED:
        if kept.split('/')[0] not in ('.venv_unix',
                                      'utils_shared',
                                      '.portimao_shortcut',
                                      ):
            assert (root / kept).is_file(), kept
    assert (root / 'fits' / 'standard.csv').is_file()
    assert (root / 'config.py').read_text(encoding='utf-8') == 'edited by the user'
    log = (root / 'logs' / 'move_to_app.log').read_text(encoding='utf-8')
    assert 'Took away' in log and 'is opening' in log
    assert 'Could not take away' not in log


# ---- test_old_macos_is_not_moved -----------------------------------------------------
def test_old_macos_is_not_moved(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a Mac older than macOS 14 is not moved, the reason
    naming its version, and nothing is installed.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    OLD_MACOS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _installer_faker
    _old_install_maker
    """

    root = _old_install_maker(tmp_path / 'Portimao')
    calls: List[Path] = []
    assert OLD_MACOS in move_blocker_finder(root, OLD_MACOS)
    assert not app_mover(root,
                         tmp_path,
                         lambda text: None,
                         OLD_MACOS,
                         _installer_faker(True, calls),
                         lambda app: None,
                         False,
                         )
    assert calls == []
    assert (root / '.git').is_dir()
