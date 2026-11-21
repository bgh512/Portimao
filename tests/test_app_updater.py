"""
Tests the Mac app's update: the newest release, the zip for each Mac and the swap with a
made-up app.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
import os
import plistlib
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import utils_shared.app_updater as app_updater
from utils_shared.app_updater import (_ask_problem_describer,
                                      _blocker_finder,
                                      _newer_checker,
                                      _release_page_reader,
                                      _release_reader,
                                      _zip_namer,
                                      APPLE_SILICON_ZIP,
                                      INTEL_ZIP,
                                      swap_starter,
                                      update_installer,
                                      UPDATE_FOLDER_NAME,
                                      )
from utils_shared.user_places import user_places_finder


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
SWAPPER_TEXT = (ROOT / 'launchers' / 'mac_app_swapper.sh').read_text(encoding='utf-8')
HAS_SHELL = shutil.which('sh') is not None
HAS_CURL = shutil.which('curl') is not None
HAS_DITTO = shutil.which('ditto') is not None  # macOS only
SWAP_WAIT_S = 30
# on Windows the stand-in program runs without a window of its own
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ---- HELPERS -------------------------------------------------------------------------


# ---- _app_maker ----------------------------------------------------------------------
def _app_maker(app: Path, version: str) -> Path:
    """
    ---- Summary ----
    Helper function to make a made-up app: an Info.plist with its version, a stand-in
    program, and a file that names the version.

    ---- Inputs ----
    app : Path
        The .app folder to make.
    version : str
        Its version, for example "1.0".

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The stand-in program inside the app (Contents/MacOS/Portimao).

    ---- Globals mutated ----
    None. Writes the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    program = app / 'Contents' / 'MacOS' / 'Portimao'
    program.parent.mkdir(parents=True)
    program.write_text('#!/bin/sh\n', encoding='utf-8')
    with open(app / 'Contents' / 'Info.plist', 'wb') as stream:
        plistlib.dump({'CFBundleExecutable': 'Portimao',
                       'CFBundleShortVersionString': version,
                       },
                      stream,
                      )
    (app / 'version.txt').write_text(version, encoding='utf-8')
    return program


# ---- _closed_pid_giver ---------------------------------------------------------------
def _closed_pid_giver() -> int:
    """
    ---- Summary ----
    Helper function to give the process id of a program that has already closed, as
    the app has by the time the swap goes on.

    ---- Inputs ----
    None.

    ---- Globals read ----
    HIDDEN (module constant).

    ---- Outputs ----
    int
        The process id.

    ---- Globals mutated ----
    None. Runs a short program (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    finished = subprocess.Popen([sys.executable, '-c', 'pass'], creationflags=HIDDEN)
    finished.wait()
    return finished.pid


# ---- _release_writer -----------------------------------------------------------------
def _release_writer(folder: Path, tag: str, zip_path: Path) -> str:
    """
    ---- Summary ----
    Helper function to write a made-up answer of GitHub about its newest release, with
    both zips pointing at one made-up zip.

    ---- Inputs ----
    folder : Path
        Folder to write the answer in.
    tag : str
        The release's tag, for example "V99.0".
    zip_path : Path
        The made-up zip; it may not exist when nothing is downloaded.

    ---- Globals read ----
    APPLE_SILICON_ZIP, INTEL_ZIP (imported constants).

    ---- Outputs ----
    str
        The file:// address of the answer.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    size = zip_path.stat().st_size if zip_path.exists() else 0
    assets = [{'name': name,
               'browser_download_url': zip_path.as_uri(),
               'size': size,
               }
              for name in (APPLE_SILICON_ZIP, INTEL_ZIP)
              ]
    answer = folder / 'release.json'
    answer.write_text(json.dumps({'tag_name': tag, 'assets': assets}),
                      encoding='utf-8',
                      )
    return answer.as_uri()


# ---- _swap_folder_maker --------------------------------------------------------------
def _swap_folder_maker(tmp_path: Path) -> Tuple[Path, Path, Path, Path]:
    """
    ---- Summary ----
    Helper function to make an old app in a stand-in Applications folder and a new one
    in the update folder beside it, as the update leaves them before the swap.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    UPDATE_FOLDER_NAME (imported constant).

    ---- Outputs ----
    Tuple[Path, Path, Path, Path]
        (the app, the new app, the update log, the file the stand-in open command
        makes).

    ---- Globals mutated ----
    None. Writes the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_maker
    """

    app = tmp_path / 'Applications' / 'Portimao.app'
    _app_maker(app, '1.0')
    new_app = tmp_path / 'Applications' / UPDATE_FOLDER_NAME / 'Portimao.app'
    _app_maker(new_app, '2.0')
    return app, new_app, tmp_path / 'update.log', tmp_path / 'opened'


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_app_only_waits_for_a_newer_release -----------------------------------------
@pytest.mark.skipif(not HAS_CURL, reason='no curl on this computer')
def test_app_only_waits_for_a_newer_release(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that an app as new as the newest release starts as it is,
    leaves itself alone and says so in its update log, and that a program run from
    source never asks.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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
    _release_writer
    update_installer
    user_places_finder
    """

    app = tmp_path / 'Applications' / 'Portimao.app'
    program = _app_maker(app, '2.4')
    address = _release_writer(tmp_path, 'V2.4.0', tmp_path / 'none.zip')
    places = user_places_finder(is_app=True, home=tmp_path, program_folder=ROOT)
    assert not update_installer(places,
                                executable=str(program),
                                release_url=address,
                                shows_messages=False,
                                )
    assert (app / 'version.txt').read_text(encoding='utf-8') == '2.4'
    log = (places.logs_folder / 'update.log').read_text(encoding='utf-8')
    assert 'nothing to update' in log
    source = user_places_finder(is_app=False, home=tmp_path, program_folder=ROOT)
    assert not update_installer(source, release_url=address, shows_messages=False)


# ---- test_ask_problem_is_described ---------------------------------------------------
def test_ask_problem_is_described() -> None:
    """
    ---- Summary ----
    Main function to check that each way of getting no answer from GitHub is said in
    plain words, and that only GitHub's refusals are taken as refusals.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _ask_problem_describer
    """

    limited = '{"message": "API rate limit exceeded for 203.0.113.7."}'
    assert _ask_problem_describer(0, 200, '{}', '') == ('', False)
    assert _ask_problem_describer(0, 0, '{}', '') == ('', False)
    assert _ask_problem_describer(0, 403, limited, '') == (
        'GitHub refused: too many questions from this network in the last hour',
        True,
        )
    assert _ask_problem_describer(0, 429, '', '') == ('GitHub refused (error 429)',
                                                      True,
                                                      )
    assert _ask_problem_describer(0, 502, '', '') == ('GitHub answered with error 502',
                                                      False,
                                                      )
    assert _ask_problem_describer(6, 0, '', 'curl: (6) Could not resolve host') == (
        'the Mac could not find GitHub: no internet?',
        False,
        )
    assert _ask_problem_describer(28, 0, '', '') == ('no answer within 5 s', False)
    assert _ask_problem_describer(37, 0, '', "curl: (37) Couldn't open file /x") == (
        "curl ended with code 37 (curl: (37) Couldn't open file /x)",
        False,
        )


# ---- test_failed_swap_keeps_the_app --------------------------------------------------
@pytest.mark.skipif(not HAS_SHELL, reason='no sh on this computer')
def test_failed_swap_keeps_the_app(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that when the new app cannot be moved in (here it is
    missing), the old app is kept, still opened and the log says why.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    SWAP_WAIT_S, SWAPPER_TEXT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _closed_pid_giver
    _swap_folder_maker
    swap_starter
    """

    app, new_app, log, opened = _swap_folder_maker(tmp_path)
    shutil.rmtree(new_app)
    swap = swap_starter(SWAPPER_TEXT,
                        _closed_pid_giver(),
                        app,
                        new_app,
                        log,
                        ['touch', opened.as_posix()],
                        )
    swap.wait(timeout=SWAP_WAIT_S)
    assert (app / 'version.txt').read_text(encoding='utf-8') == '1.0'
    assert opened.exists()
    assert 'old one is put back' in log.read_text(encoding='utf-8')


# ---- test_newer_release_is_found -----------------------------------------------------
def test_newer_release_is_found() -> None:
    """
    ---- Summary ----
    Main function to check that versions are compared number by number, and that an
    app whose version cannot be read never updates.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _newer_checker
    """

    assert _newer_checker('2.9', 'V2.10')
    assert _newer_checker('2.3', '2.3.1')
    assert _newer_checker('2.3.1', 'V2.4')
    assert not _newer_checker('2.3.1', 'V2.3.1')
    assert not _newer_checker('2.3', '2.3.0')
    assert not _newer_checker('2.4', 'V2.3.1')
    assert not _newer_checker(None, 'V2.4')
    assert not _newer_checker('2.4', 'nightly')


# ---- test_refused_ask_uses_the_release_page ------------------------------------------
def test_refused_ask_uses_the_release_page(tmp_path: Path,
                                           monkeypatch: pytest.MonkeyPatch,
                                           ) -> None:
    """
    ---- Summary ----
    Main function to check that when GitHub refuses the question, the app finds the
    newest release from the Releases page instead, and starts as it is when that page
    does not answer either; the reasons are in its update log.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for GitHub's two answers.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. The stand-ins last only for this test.

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_maker
    update_installer
    user_places_finder
    """

    refusal = 'GitHub refused: too many questions from this network in the last hour'
    newest = 'https://github.com/bgh512/Portimao/releases/tag/V2.4.0'
    monkeypatch.setattr(app_updater,
                        '_release_asker',
                        lambda url: (None, refusal, True),
                        )
    monkeypatch.setattr(app_updater, '_release_page_asker', lambda url: (newest, ''))
    app = tmp_path / 'Applications' / 'Portimao.app'
    program = _app_maker(app, '2.4')
    places = user_places_finder(is_app=True, home=tmp_path, program_folder=ROOT)
    assert not update_installer(places, executable=str(program), shows_messages=False)
    log_path = places.logs_folder / 'update.log'
    log = log_path.read_text(encoding='utf-8')
    assert f'{refusal}; asking the Releases page instead.' in log
    assert 'The newest release is V2.4.0: nothing to update.' in log
    monkeypatch.setattr(app_updater,
                        '_release_page_asker',
                        lambda url: (None, 'no answer within 5 s'),
                        )
    assert not update_installer(places, executable=str(program), shows_messages=False)
    log = log_path.read_text(encoding='utf-8')
    assert 'did not say which release is the newest (no answer within 5 s)' in log


# ---- test_release_answer_is_read -----------------------------------------------------
def test_release_answer_is_read() -> None:
    """
    ---- Summary ----
    Main function to check that the version and the zips are read from GitHub's answer,
    and that an answer of any other form is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    APPLE_SILICON_ZIP (imported constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _release_reader
    """

    answer = {'tag_name': 'V2.4.1',
              'assets': [{'name': APPLE_SILICON_ZIP,
                          'browser_download_url': 'https://example.org/a.zip',
                          'size': 64598407,
                          },
                         ],
              }
    version, zips = _release_reader(json.dumps(answer))
    assert version == '2.4.1'
    assert zips == {APPLE_SILICON_ZIP: ('https://example.org/a.zip', 64598407)}
    assert _release_reader('not an answer') is None
    assert _release_reader(json.dumps({'assets': []})) is None
    assert _release_reader(json.dumps({'tag_name': 'nightly', 'assets': []})) is None
    assert _release_reader(json.dumps(['V2.4'])) is None


# ---- test_release_page_address_is_read -----------------------------------------------
def test_release_page_address_is_read() -> None:
    """
    ---- Summary ----
    Main function to check that the version is read from the address the Releases page
    leads to, that both zips are found under its tag, and that any other address is
    refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    APPLE_SILICON_ZIP, INTEL_ZIP (imported constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _release_page_reader
    """

    page = 'https://github.com/bgh512/Portimao/releases'
    downloads = f'{page}/download'
    version, zips = _release_page_reader(f'{page}/tag/V2.4.1\n', downloads)
    assert version == '2.4.1'
    assert zips == {APPLE_SILICON_ZIP: (f'{downloads}/V2.4.1/{APPLE_SILICON_ZIP}', 0),
                    INTEL_ZIP: (f'{downloads}/V2.4.1/{INTEL_ZIP}', 0),
                    }
    assert _release_page_reader(f'{page}/latest', downloads) is None
    assert _release_page_reader(f'{page}/tag/nightly', downloads) is None
    assert _release_page_reader('', downloads) is None


# ---- test_swap_puts_the_new_app_in_place ---------------------------------------------
@pytest.mark.skipif(not HAS_SHELL, reason='no sh on this computer')
def test_swap_puts_the_new_app_in_place(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the swap puts the new app in place of the old one,
    deletes the old one, opens the app and writes it in the log.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    SWAP_WAIT_S, SWAPPER_TEXT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _closed_pid_giver
    _swap_folder_maker
    swap_starter
    """

    app, new_app, log, opened = _swap_folder_maker(tmp_path)
    swap = swap_starter(SWAPPER_TEXT,
                        _closed_pid_giver(),
                        app,
                        new_app,
                        log,
                        ['touch', opened.as_posix()],
                        )
    swap.wait(timeout=SWAP_WAIT_S)
    assert (app / 'version.txt').read_text(encoding='utf-8') == '2.0'
    assert list(new_app.parent.iterdir()) == []  # neither app left in the update folder
    assert opened.exists()
    assert 'The new app is in place.' in log.read_text(encoding='utf-8')


# ---- test_swap_waits_for_the_app_to_close --------------------------------------------
@pytest.mark.skipif(os.name != 'posix', reason='Windows process ids mean nothing to sh')
def test_swap_waits_for_the_app_to_close(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the swap leaves the app alone while it is still open,
    and swaps it once it has closed.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    SWAP_WAIT_S, SWAPPER_TEXT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _swap_folder_maker
    swap_starter
    """

    app, new_app, log, opened = _swap_folder_maker(tmp_path)
    still_open = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(2)'])
    swap = swap_starter(SWAPPER_TEXT,
                        still_open.pid,
                        app,
                        new_app,
                        log,
                        ['touch', opened.as_posix()],
                        )
    time.sleep(0.5)
    assert (app / 'version.txt').read_text(encoding='utf-8') == '1.0'
    assert not opened.exists()
    still_open.wait()
    swap.wait(timeout=SWAP_WAIT_S)
    assert (app / 'version.txt').read_text(encoding='utf-8') == '2.0'
    assert opened.exists()


# ---- test_temporary_copy_cannot_update -----------------------------------------------
def test_temporary_copy_cannot_update(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that an app macOS runs from a temporary copy says it cannot
    replace itself, and that an app in a folder that can be written to can.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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
    _blocker_finder
    """

    copy = Path('/private/var/folders/x/AppTranslocation/1A2B/d/Portimao.app')
    assert 'temporary copy' in _blocker_finder(copy)
    app = tmp_path / 'Applications' / 'Portimao.app'
    _app_maker(app, '1.0')
    assert _blocker_finder(app) is None


# ---- test_unanswered_ask_is_asked_again ----------------------------------------------
@pytest.mark.skipif(not HAS_CURL, reason='no curl on this computer')
def test_unanswered_ask_is_asked_again(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch,
                                       ) -> None:
    """
    ---- Summary ----
    Main function to check that when GitHub does not answer, the app asks once more,
    then starts as it is, with curl's own reason in its update log each time.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Takes away the wait before asking again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. The change lasts only for this test.

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_maker
    update_installer
    user_places_finder
    """

    monkeypatch.setattr(app_updater, 'RETRY_WAIT_S', 0)
    app = tmp_path / 'Applications' / 'Portimao.app'
    program = _app_maker(app, '2.4')
    missing = (tmp_path / 'no_answer.json').as_uri()
    places = user_places_finder(is_app=True, home=tmp_path, program_folder=ROOT)
    assert not update_installer(places,
                                executable=str(program),
                                release_url=missing,
                                shows_messages=False,
                                )
    log = (places.logs_folder / 'update.log').read_text(encoding='utf-8')
    assert 'GitHub did not answer (curl ended with code 37' in log
    assert 'asking again in 0 s' in log
    assert 'GitHub did not answer again (curl ended with code 37' in log
    assert 'starting as it is' in log
    assert 'no internet?' not in log


# ---- test_update_from_made_up_zip ----------------------------------------------------
@pytest.mark.skipif(not (HAS_DITTO and HAS_CURL), reason='needs macOS (ditto and curl)')
def test_update_from_made_up_zip(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the whole update on a Mac: a made-up app V1.0 finds a
    made-up release V99.0, downloads and unpacks its zip, and the swap puts V99.0 in
    its place and opens it.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    SWAP_WAIT_S (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_maker
    _closed_pid_giver
    _release_writer
    update_installer
    user_places_finder
    """

    # ---- 1 Make the old app and the release ------------------------------------------
    app = tmp_path / 'Applications' / 'Portimao.app'
    program = _app_maker(app, '1.0')
    built = tmp_path / 'built' / 'Portimao.app'
    _app_maker(built, '99.0')
    zip_path = tmp_path / 'Portimao.zip'
    subprocess.run(['ditto', '-c', '-k', '--keepParent', str(built), str(zip_path)],
                   check=True,
                   )
    address = _release_writer(tmp_path, 'V99.0', zip_path)

    # ---- 2 Update --------------------------------------------------------------------
    opened = tmp_path / 'opened'
    places = user_places_finder(is_app=True, home=tmp_path, program_folder=ROOT)
    assert update_installer(places,
                            executable=str(program),
                            release_url=address,
                            closing_pid=_closed_pid_giver(),
                            start_command=['touch', opened.as_posix()],
                            shows_messages=False,
                            )
    deadline = time.time() + SWAP_WAIT_S
    while not opened.exists() and time.time() < deadline:
        time.sleep(0.2)
    assert opened.exists()
    assert (app / 'version.txt').read_text(encoding='utf-8') == '99.0'
    log = (places.logs_folder / 'update.log').read_text(encoding='utf-8')
    assert 'The new app is in place.' in log
