"""
Tests that the Mac report runs to the end, finds where the folder or the app is and
changes nothing.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'launchers' / 'mac_report.sh'
SHELL = shutil.which('sh')
pytestmark = pytest.mark.skipif(SHELL is None, reason='no sh on this computer')
SECTIONS = ('== Mac ==',
            '== Portimao folder ==',
            '== Pythons',
            '== logs/launch.log ==',
            '== logs/launcher_errors.log ==',
            )
N_LOG_LINES = 50  # the report shows only the last 30
# on Windows the shell runs without a window of its own, so the test stays out of sight
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ---- HELPERS -------------------------------------------------------------------------


# ---- _app_maker ----------------------------------------------------------------------
def _app_maker(home: Path) -> Path:
    """
    ---- Summary ----
    Helper function to make a small Portimao app in Applications, holding the report
    and a question list with a made-up version as the build puts them, and the app's
    own folder in the home folder with a launch log and an update log.

    ---- Inputs ----
    home : Path
        Stand-in home folder.

    ---- Globals read ----
    REPORT (module constant).

    ---- Outputs ----
    Path
        The folder inside the app that holds the report's launchers folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    inside = home / 'Applications' / 'Portimao.app' / 'Contents' / 'Resources'
    (inside / 'launchers').mkdir(parents=True)
    shutil.copy(REPORT, inside / 'launchers' / REPORT.name)
    (inside / 'QUESTION_FLOW.md').write_bytes(b'# Portimao question flow (V9.9)\n\n')
    logs = home / 'Portimao' / 'logs'
    logs.mkdir(parents=True)
    (logs / 'launch.log').write_bytes(b'launch line\n')
    (logs / 'update.log').write_bytes(b'update line\n')
    return inside


# ---- _folder_maker -------------------------------------------------------------------
def _folder_maker(home: Path, place: str) -> Path:
    """
    ---- Summary ----
    Helper function to make a small Portimao folder holding the report, a question
    list with a made-up version and a launch log of 50 numbered lines.

    ---- Inputs ----
    home : Path
        Stand-in home folder.
    place : str
        Folder inside home to put Portimao in ('' for the home folder itself).

    ---- Globals read ----
    N_LOG_LINES, REPORT (module constants).

    ---- Outputs ----
    Path
        The Portimao folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    folder = home / place / 'Portimao'
    (folder / 'launchers').mkdir(parents=True)
    (folder / 'logs').mkdir()
    shutil.copy(REPORT, folder / 'launchers' / REPORT.name)
    (folder / 'QUESTION_FLOW.md').write_bytes(b'# Portimao question flow (V9.9)\n\n')
    lines = ''.join(f'log line {n:03d}\n' for n in range(1, N_LOG_LINES + 1))
    (folder / 'logs' / 'launch.log').write_bytes(lines.encode('utf-8'))
    return folder


# ---- _report_runner ------------------------------------------------------------------
def _report_runner(folder: Path, home: Path) -> str:
    """
    ---- Summary ----
    Helper function to run the report of a Portimao folder as Terminal would, with
    the stand-in home folder as the user's home.

    ---- Inputs ----
    folder : Path
        Portimao folder made by _folder_maker.
    home : Path
        Stand-in home folder.

    ---- Globals read ----
    HIDDEN, SHELL, REPORT (module constants).

    ---- Outputs ----
    str
        What the report printed. The test fails when it does not end with 0.

    ---- Globals mutated ----
    None. Runs the report (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # the shell spells folders its own way on Windows, so the home is spelt by it too
    spelt = subprocess.run([SHELL, '-c', 'cd "$1" && pwd', 'sh', home.as_posix()],
                           capture_output=True,
                           text=True,
                           check=True,
                           creationflags=HIDDEN,
                           )
    # Windows' stand-in python3 only points to the Microsoft Store
    entries = os.environ.get('PATH', '').split(os.pathsep)
    environment = dict(
        os.environ,
        HOME=spelt.stdout.strip(),
        PATH=os.pathsep.join(e for e in entries if 'WindowsApps' not in e),
        )
    script = folder / 'launchers' / REPORT.name
    ran = subprocess.run([SHELL, script.as_posix()],
                         capture_output=True,
                         text=True,
                         encoding='utf-8',
                         errors='replace',
                         env=environment,
                         timeout=120,
                         creationflags=HIDDEN,
                         )
    assert ran.returncode == 0, ran.stdout + ran.stderr
    return ran.stdout


# ---- _snapshot_taker -----------------------------------------------------------------
def _snapshot_taker(folder: Path) -> Dict[str, bytes]:
    """
    ---- Summary ----
    Helper function to read every file of a folder, to compare before and after.

    ---- Inputs ----
    folder : Path
        Folder to read.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, bytes]
        Path inside the folder against the file's contents.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {path.relative_to(folder).as_posix(): path.read_bytes()
            for path in sorted(folder.rglob('*'))
            if path.is_file()
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_report_in_downloads_names_it -----------------------------------------------
def test_report_in_downloads_names_it(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the report of a folder in Downloads ends without an
    error, has every part, names Downloads as guarded, gives the version, shows only
    the last 30 log lines and leaves every file as it was.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    SECTIONS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _folder_maker
    _report_runner
    _snapshot_taker
    """

    folder = _folder_maker(tmp_path, 'Downloads')
    before = _snapshot_taker(folder)
    report = _report_runner(folder, tmp_path)
    for section in SECTIONS:
        assert section in report
    assert 'In a folder macOS guards: yes, Downloads' in report
    assert 'Version: V9.9' in report
    assert 'Installed from a zip file' in report
    assert 'log line 050' in report and 'log line 021' in report
    assert 'log line 020' not in report
    assert '(no such file)' in report  # launcher_errors.log
    assert _snapshot_taker(folder) == before


# ---- test_report_in_home_folder_is_not_guarded ---------------------------------------
def test_report_in_home_folder_is_not_guarded(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a folder straight in the home folder is not named as
    guarded.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _folder_maker
    _report_runner
    """

    folder = _folder_maker(tmp_path, '')
    assert 'In a folder macOS guards: no' in _report_runner(folder, tmp_path)


# ---- test_report_inside_app_describes_it ---------------------------------------------
def test_report_inside_app_describes_it(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the report run from inside the app (as Copy details
    does) describes the app and reads the logs of the app's own folder, leaves out the
    launcher's parts, prints only the report on its output and changes nothing.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_maker
    _report_runner
    _snapshot_taker
    """

    inside = _app_maker(tmp_path)
    before = _snapshot_taker(tmp_path)
    report = _report_runner(inside, tmp_path)
    assert '== Portimao app ==' in report
    assert 'Portimao.app' in report.split('Where: ', 1)[1].splitlines()[0]
    assert 'Opened from a temporary copy macOS made: no' in report
    assert 'Version: V9.9' in report
    assert 'there, can be written to' in report
    assert 'launch line' in report and 'update line' in report
    assert '== Pythons' not in report and '== Portimao folder ==' not in report
    assert 'Mac problem' not in report  # the help lines are not copied
    assert _snapshot_taker(tmp_path) == before
