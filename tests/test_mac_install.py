"""
Tests that the install line puts the right app in the user's own Applications folder,
opens it, and stops with a plain sentence when it cannot.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'install_mac.sh'
SHELL = shutil.which('sh')
pytestmark = pytest.mark.skipif(SHELL is None, reason='no sh on this computer')
RELEASE_URL = 'https://example.invalid/download'
# Stand-ins for the Mac's own commands, written as shell functions before the script,
# so the script runs anywhere: curl notes what it was asked for and writes a zip,
# ditto unpacks a small app, open notes what it opened.
STAND_INS = r"""
uname() { printf '%s\n' '@SYSTEM@'; }
sw_vers() { printf '%s\n' '@MACOS@'; }
sysctl() { printf '%s\n' '@ARM@'; }
pgrep() { return @PGREP@; }
plutil() { printf '%s\n' '9.9'; }
curl() {
    for argument in "$@"; do
        last="$argument"
    done
    printf '%s\n' "$last" >>"$HOME/asked.txt"
    if [ '@DOWNLOADS@' = 'no' ]; then
        return 22
    fi
    while [ "$#" -gt 0 ]; do
        if [ "$1" = '-o' ]; then
            printf 'zip' >"$2"
        fi
        shift
    done
}
ditto() {
    mkdir -p "$4/Portimao.app/Contents/MacOS"
    printf 'plist' >"$4/Portimao.app/Contents/Info.plist"
    printf 'new' >"$4/Portimao.app/Contents/MacOS/Portimao"
}
open() { printf '%s\n' "$*" >>"$HOME/opened.txt"; }
"""
# on Windows the shell runs without a window of its own, so the test stays out of sight
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ---- HELPERS -------------------------------------------------------------------------


# ---- _install_runner -----------------------------------------------------------------
def _install_runner(home: Path,
                    arguments: Sequence[str] = (),
                    system: str = 'Darwin',
                    macos_version: str = '15.1',
                    is_apple_silicon: bool = True,
                    is_open: bool = False,
                    is_downloaded: bool = True,
                    ) -> 'subprocess.CompletedProcess':
    """
    ---- Summary ----
    Helper function to run install_mac.sh as `curl ... | bash` does, its text coming in
    through the shell's input, with the Mac's commands stood in for and a stand-in home
    folder.

    ---- Inputs ----
    home : Path
        Stand-in home folder.
    arguments : Sequence[str]
        Arguments after the script (`--no-open`).
    system : str
        What uname says the system is.
    macos_version : str
        What sw_vers says the macOS version is.
    is_apple_silicon : bool
        True for an Apple Silicon Mac.
    is_open : bool
        True when Portimao is found open.
    is_downloaded : bool
        False when the download fails.

    ---- Globals read ----
    HIDDEN, RELEASE_URL, SCRIPT, SHELL, STAND_INS (module constants).

    ---- Outputs ----
    subprocess.CompletedProcess
        The finished run, with its output as text.

    ---- Globals mutated ----
    None. Runs the script, which writes into the home folder (side effect).

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
    stand_ins = (STAND_INS.replace('@SYSTEM@', system)
                 .replace('@MACOS@', macos_version)
                 .replace('@ARM@', '1' if is_apple_silicon else '0')
                 .replace('@PGREP@', '0' if is_open else '1')
                 .replace('@DOWNLOADS@', 'yes' if is_downloaded else 'no')
                 )
    # bytes, so Windows does not turn the line ends into ones the shell refuses
    text = (stand_ins.encode('utf-8') + SCRIPT.read_bytes()).replace(b'\r\n', b'\n')
    environment = dict(os.environ,
                       HOME=spelt.stdout.strip(),
                       PORTIMAO_RELEASE_URL=RELEASE_URL,
                       )
    environment.pop('PORTIMAO_SELF_TEST', None)
    ran = subprocess.run([SHELL, '-s', '--', *arguments],
                         input=text,
                         capture_output=True,
                         env=environment,
                         timeout=60,
                         creationflags=HIDDEN,
                         )
    return subprocess.CompletedProcess(ran.args,
                                       ran.returncode,
                                       ran.stdout.decode('utf-8', errors='replace'),
                                       ran.stderr.decode('utf-8', errors='replace'),
                                       )


# ---- _old_app_maker ------------------------------------------------------------------
def _old_app_maker(home: Path) -> Path:
    """
    ---- Summary ----
    Helper function to put an older Portimao app, with a file only it has, in the
    user's own Applications folder.

    ---- Inputs ----
    home : Path
        Stand-in home folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The old .app folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    app = home / 'Applications' / 'Portimao.app'
    (app / 'Contents' / 'MacOS').mkdir(parents=True)
    (app / 'Contents' / 'MacOS' / 'Portimao').write_text('old', encoding='utf-8')
    (app / 'Contents' / 'old_only.txt').write_text('old', encoding='utf-8')
    return app


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_download_failure_keeps_the_old_app -----------------------------------------
def test_download_failure_keeps_the_old_app(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a download that fails stops with one sentence saying
    what to do, keeps the app already there and leaves no download folder.

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
    _install_runner
    _old_app_maker
    """

    app = _old_app_maker(tmp_path)
    ran = _install_runner(tmp_path, is_downloaded=False)
    assert ran.returncode == 1
    assert 'could not be downloaded: check the internet connection' in ran.stderr
    assert (app / 'Contents' / 'MacOS' / 'Portimao').read_text(encoding='utf-8',
                                                               ) == 'old'
    assert [p.name for p in (tmp_path / 'Applications').iterdir()] == ['Portimao.app']


# ---- test_intel_mac_gets_the_intel_zip -----------------------------------------------
def test_intel_mac_gets_the_intel_zip(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that an Intel Mac downloads the Intel app.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    RELEASE_URL (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _install_runner
    """

    ran = _install_runner(tmp_path, is_apple_silicon=False)
    assert ran.returncode == 0, ran.stdout + ran.stderr
    asked = (tmp_path / 'asked.txt').read_text(encoding='utf-8').split()
    assert asked == [f'{RELEASE_URL}/Portimao-mac-intel.zip']


# ---- test_line_installs_and_opens_the_app --------------------------------------------
def test_line_installs_and_opens_the_app(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that on an Apple Silicon Mac the line downloads the Apple
    Silicon app, puts it in the user's own Applications folder (made when missing),
    opens it, says so with the version and leaves no download folder behind.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, used as the home folder.

    ---- Globals read ----
    RELEASE_URL (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _install_runner
    """

    ran = _install_runner(tmp_path)
    assert ran.returncode == 0, ran.stdout + ran.stderr
    asked = (tmp_path / 'asked.txt').read_text(encoding='utf-8').split()
    assert asked == [f'{RELEASE_URL}/Portimao-mac-apple-silicon.zip']
    app = tmp_path / 'Applications' / 'Portimao.app'
    assert (app / 'Contents' / 'MacOS' / 'Portimao').read_text(encoding='utf-8',
                                                               ) == 'new'
    assert [p.name for p in (tmp_path / 'Applications').iterdir()] == ['Portimao.app']
    opened = (tmp_path / 'opened.txt').read_text(encoding='utf-8')
    assert opened.strip().endswith('Applications/Portimao.app')
    assert 'Portimao V9.9 is installed in your Applications folder and is opening' in ran.stdout


# ---- test_no_open_replaces_the_old_app -----------------------------------------------
def test_no_open_replaces_the_old_app(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the line run again puts the new app wholly in place of
    the old one, and that --no-open (used by the move) leaves it closed.

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
    _install_runner
    _old_app_maker
    """

    app = _old_app_maker(tmp_path)
    ran = _install_runner(tmp_path, arguments=['--no-open'])
    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert (app / 'Contents' / 'MacOS' / 'Portimao').read_text(encoding='utf-8',
                                                               ) == 'new'
    assert not (app / 'Contents' / 'old_only.txt').exists()
    assert [p.name for p in (tmp_path / 'Applications').iterdir()] == ['Portimao.app']
    assert not (tmp_path / 'opened.txt').exists()
    assert 'Portimao V9.9 is installed in your Applications folder.' in ran.stdout


# ---- test_not_a_mac_is_refused -------------------------------------------------------
def test_not_a_mac_is_refused(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the line run on another system stops with one sentence
    and downloads nothing.

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
    _install_runner
    """

    ran = _install_runner(tmp_path, system='Linux')
    assert ran.returncode == 1
    assert 'This line installs Portimao on a Mac' in ran.stderr
    assert not (tmp_path / 'asked.txt').exists()


# ---- test_old_macos_is_refused -------------------------------------------------------
def test_old_macos_is_refused(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a Mac older than macOS 14 is told, in one sentence
    naming its version, to update macOS, and that nothing is downloaded or made.

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
    _install_runner
    """

    ran = _install_runner(tmp_path, macos_version='13.6')
    assert ran.returncode == 1
    assert ('Portimao needs macOS 14 or newer, and this Mac has macOS 13.6: update macOS'
            in ran.stderr)
    assert not (tmp_path / 'asked.txt').exists()
    assert not (tmp_path / 'Applications').exists()


# ---- test_open_app_is_refused --------------------------------------------------------
def test_open_app_is_refused(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the line asks for Portimao to be closed when it is open,
    and leaves the app as it is.

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
    _install_runner
    _old_app_maker
    """

    app = _old_app_maker(tmp_path)
    ran = _install_runner(tmp_path, is_open=True)
    assert ran.returncode == 1
    assert 'Portimao is open: close it (Cmd + Q), then paste the line again.' in ran.stderr
    assert (app / 'Contents' / 'old_only.txt').exists()
    assert not (tmp_path / 'asked.txt').exists()
