"""
The Mac app's own update at each start: asks GitHub for the newest release and, when it
is newer, puts it in place of the app.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
import os
import platform
import plistlib
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.app_messages import RELEASES_LINK, update_notice_shower
from utils_shared.user_places import UserPlaces


# ---- CONSTANTS -----------------------------------------------------------------------
RELEASE_URL = 'https://api.github.com/repos/bgh512/Portimao/releases/latest'
# asked when GitHub refuses the question above: the Releases page (RELEASES_LINK) leads
# to the newest release's own page, and its zips are here, under its tag
RELEASE_DOWNLOAD_URL = 'https://github.com/bgh512/Portimao/releases/download'
TAG_ADDRESS_PATTERN = re.compile(r'/releases/tag/([^/?#\s]+)$')
# the zips the Mac check puts on the Releases page (.github/workflows/mac_check.yml)
APPLE_SILICON_ZIP = 'Portimao-mac-apple-silicon.zip'
INTEL_ZIP = 'Portimao-mac-intel.zip'
UPDATE_FOLDER_NAME = '.Portimao-update'  # beside the app; Finder does not show it
SWAPPER = Path('launchers') / 'mac_app_swapper.sh'  # inside the program folder
LOG_NAME = 'update.log'
LOG_KEPT_LINES = 200
ASK_TIMEOUT_S = 5  # GitHub's answer holds up every start, so it is kept short
RETRY_WAIT_S = 3  # before asking again when GitHub did not answer
# GitHub's answer when it refuses, mostly for too many questions from one network
REFUSED_STATUSES = (403, 429)
# curl's own codes for the usual ways of getting no answer
CURL_REASONS = {6: 'the Mac could not find GitHub: no internet?',
                7: 'GitHub could not be reached',
                28: f'no answer within {ASK_TIMEOUT_S} s',
                }
CONNECT_TIMEOUT_S = 10
# a download slower than this for this long has stalled and stops
STALL_BYTES_PER_S = 1000
STALL_S = 30
PROGRESS_STEP_S = 0.5
VERSION_PATTERN = re.compile(r'V?(\d+(?:\.\d+)*)')
TEMPORARY_COPY_MARK = '/AppTranslocation/'  # where macOS runs a copy it made
SELF_TEST_SWITCH = 'PORTIMAO_SELF_TEST'
# only matters when the tests run the swap on Windows: no window flashes up
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


# ---- UPDATE HELPERS ------------------------------------------------------------------


# ---- _app_finder ---------------------------------------------------------------------
def _app_finder(executable: str) -> Optional[Path]:
    """
    ---- Summary ----
    Helper function to find the .app folder the running program is in.

    ---- Inputs ----
    executable : str
        Path of the running program, <app>.app/Contents/MacOS/<name> in the app.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Path]
        The .app folder, or None when the program is not inside one.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    path = Path(executable)
    if len(path.parents) < 3:
        return None
    app = path.parents[2]
    if app.suffix != '.app' or path.parents[1].name != 'Contents':
        return None
    return app


# ---- _app_unpacker -------------------------------------------------------------------
def _app_unpacker(zip_path: Path, folder: Path) -> Optional[Path]:
    """
    ---- Summary ----
    Helper function to unpack the downloaded zip with macOS's ditto, which keeps the
    app's links and signature (Python's zip module would break them).

    ---- Inputs ----
    zip_path : Path
        The downloaded zip.
    folder : Path
        Folder to unpack into.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Path]
        The one .app folder unpacked, or None when unpacking failed.

    ---- Globals mutated ----
    None. Writes the app into the folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        done = subprocess.run(['ditto', '-x', '-k', str(zip_path), str(folder)],
                              capture_output=True,
                              text=True,
                              )
    except OSError:
        return None
    apps = [path for path in folder.glob('*.app') if path.is_dir()]
    return apps[0] if done.returncode == 0 and len(apps) == 1 else None


# ---- _ask_problem_describer ----------------------------------------------------------
def _ask_problem_describer(curl_code: int,
                           http_status: int,
                           body: str,
                           errors: str,
                           ) -> Tuple[str, bool]:
    """
    ---- Summary ----
    Helper function to say in plain words why a question to GitHub got no answer, and
    whether GitHub refused it.

    ---- Inputs ----
    curl_code : int
        curl's exit code; 0 when it had an answer of any kind.
    http_status : int
        GitHub's status code (200 when it answered); 0 when there was none, as for a
        file:// address.
    body : str
        GitHub's answer; a refusal says why in it.
    errors : str
        What curl printed as its error.

    ---- Globals read ----
    CURL_REASONS, REFUSED_STATUSES (module constants).

    ---- Outputs ----
    Tuple[str, bool]
        (the reason, empty when there is an answer to read; True when GitHub refused).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if curl_code == 0 and (http_status == 0 or 200 <= http_status < 300):
        return '', False
    if curl_code == 0 and http_status in REFUSED_STATUSES:
        if 'rate limit' in body.lower():
            return ('GitHub refused: too many questions from this network in the last '
                    'hour',
                    True,
                    )
        return f'GitHub refused (error {http_status})', True
    if curl_code == 0:
        kind = 'error' if http_status >= 400 else 'code'
        return f'GitHub answered with {kind} {http_status}', False
    if curl_code in CURL_REASONS:
        return CURL_REASONS[curl_code], False
    lines = errors.strip().splitlines()
    detail = f' ({lines[-1].strip()})' if lines else ''
    return f'curl ended with code {curl_code}{detail}', False


# ---- _blocker_finder -----------------------------------------------------------------
def _blocker_finder(app: Path) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find what stops the app from replacing itself where it is.

    ---- Inputs ----
    app : Path
        The .app folder.

    ---- Globals read ----
    TEMPORARY_COPY_MARK (module constant).

    ---- Outputs ----
    Optional[str]
        Why it cannot replace itself, in plain words, or None when it can.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if TEMPORARY_COPY_MARK in app.as_posix():
        return 'macOS opened it from a temporary copy'
    if not (os.access(app.parent, os.W_OK) and os.access(app, os.W_OK)):
        return 'its folder cannot be written to'
    return None


# ---- _leftover_cleaner ---------------------------------------------------------------
def _leftover_cleaner(app: Path) -> None:
    """
    ---- Summary ----
    Helper function to delete what an earlier update left beside the app: the update
    folder, with a download that did not finish or the old app.

    ---- Inputs ----
    app : Path
        The .app folder.

    ---- Globals read ----
    UPDATE_FOLDER_NAME (module constant).

    ---- Outputs ----
    None
        Nothing. Whatever cannot be deleted is left for the next start.

    ---- Globals mutated ----
    None. Deletes files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    shutil.rmtree(app.parent / UPDATE_FOLDER_NAME, ignore_errors=True)


# ---- _log_opener ---------------------------------------------------------------------
def _log_opener(logs_folder: Path) -> Tuple[Path, Callable[[str], None]]:
    """
    ---- Summary ----
    Helper function to open the update log: keeps its last lines and gives a function
    that adds a line with the date and time.

    ---- Inputs ----
    logs_folder : Path
        The user's logs folder; made when missing.

    ---- Globals read ----
    LOG_KEPT_LINES, LOG_NAME (module constants).

    ---- Outputs ----
    Tuple[Path, Callable[[str], None]]
        (the log's path, the function that adds a line). A log that cannot be written
        just loses its lines; the update goes on.

    ---- Globals mutated ----
    None. Writes the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    path = logs_folder / LOG_NAME
    try:
        logs_folder.mkdir(parents=True, exist_ok=True)
        if path.exists():
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
            kept = ''.join(f'{line}\n' for line in lines[-LOG_KEPT_LINES:])
            path.write_text(kept, encoding='utf-8')
    except OSError:
        pass

    def add(text: str) -> None:
        try:
            with open(path, 'a', encoding='utf-8') as log:
                log.write(f'{datetime.now():%Y-%m-%d %H:%M:%S} {text}\n')
        except OSError:
            pass

    return path, add


# ---- _new_app_checker ----------------------------------------------------------------
def _new_app_checker(new_app: Path, version: str) -> bool:
    """
    ---- Summary ----
    Helper function to check that the unpacked app is the version offered and has its
    program inside.

    ---- Inputs ----
    new_app : Path
        The unpacked .app folder.
    version : str
        The version offered, for example "2.5".

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the app's Info.plist gives that version and its program is there.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _version_splitter
    """

    try:
        with open(new_app / 'Contents' / 'Info.plist', 'rb') as stream:
            values = plistlib.load(stream)
        program = new_app / 'Contents' / 'MacOS' / str(values['CFBundleExecutable'])
        found = _version_splitter(str(values['CFBundleShortVersionString']))
    except (OSError, KeyError, ValueError, plistlib.InvalidFileException):
        return False
    return found is not None and found == _version_splitter(version,
                                                            ) and program.is_file()


# ---- _new_app_fetcher ----------------------------------------------------------------
def _new_app_fetcher(url: str,
                     size_bytes: int,
                     version: str,
                     folder: Path,
                     show: Callable[[str], None],
                     log: Callable[[str], None],
                     ) -> Optional[Path]:
    """
    ---- Summary ----
    Helper function to download the zip of the new app, unpack it and check it.

    ---- Inputs ----
    url : str
        Where the zip is.
    size_bytes : int
        Size of the zip as GitHub gives it; 0 when not known.
    version : str
        The version offered.
    folder : Path
        The update folder beside the app; made here.
    show : Callable[[str], None]
        Shows a line of progress.
    log : Callable[[str], None]
        Adds a line to the update log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Path]
        The new .app folder, ready to be moved in, or None when any step failed (the
        reason is in the log).

    ---- Globals mutated ----
    None. Writes into the update folder (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_unpacker
    _new_app_checker
    _zip_downloader
    """

    # ---- 1 Download the zip ----------------------------------------------------------
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log(f'The update folder {folder} could not be made ({exc.strerror}).')
        return None
    zip_path = folder / 'download.zip'
    problem = _zip_downloader(url, zip_path, size_bytes, version, show)
    if problem:
        log(f'The download did not finish: {problem}')
        return None

    # ---- 2 Unpack and check it -------------------------------------------------------
    show(f'Updating Portimao to V{version}: unpacking ...')
    new_app = _app_unpacker(zip_path, folder)
    zip_path.unlink(missing_ok=True)
    if new_app is None:
        log('The download could not be unpacked.')
        return None
    if not _new_app_checker(new_app, version):
        log(f'The app downloaded is not a whole Portimao V{version}.')
        return None
    return new_app


# ---- _newer_checker ------------------------------------------------------------------
def _newer_checker(own: Optional[str], offered: str) -> bool:
    """
    ---- Summary ----
    Helper function to say whether the version offered is newer than the app's own.

    ---- Inputs ----
    own : Optional[str]
        The app's version, for example "2.9"; None when it could not be read.
    offered : str
        The version offered, with or without its V, for example "V2.10".

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True only when both versions can be read and the one offered is newer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Versions are compared number by number from the left: 2.10 > 2.9, 2.3.1 > 2.3,
    2.3.0 = 2.3.

    ---- Helpers ----
    _version_splitter
    """

    own_parts = _version_splitter(own or '')
    offered_parts = _version_splitter(offered)
    if own_parts is None or offered_parts is None:
        return False
    return offered_parts > own_parts


# ---- _newest_release_finder ----------------------------------------------------------
def _newest_release_finder(release_url: str,
                           log: Callable[[str], None],
                           ) -> Optional[Tuple[str, Dict[str, Tuple[str, int]]]]:
    """
    ---- Summary ----
    Helper function to find GitHub's newest release. With no answer it asks once more
    after a few seconds; when GitHub refuses, it asks the Releases page instead, which
    GitHub does not count in the same way. Each try and its reason go to the log.

    ---- Inputs ----
    release_url : str
        The address of GitHub's answer (a file:// address in the tests).
    log : Callable[[str], None]
        Adds a line to the update log.

    ---- Globals read ----
    RELEASE_DOWNLOAD_URL, RELEASES_LINK, RETRY_WAIT_S (module constants).

    ---- Outputs ----
    Optional[Tuple[str, Dict[str, Tuple[str, int]]]]
        (the version without its V, {zip name: (address, size in bytes, 0 when not
        known)}), or None when no release was found, so the app starts as it is.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _release_asker
    _release_page_asker
    _release_page_reader
    _release_reader
    """

    # ---- 1 Ask GitHub, and once more when it did not answer --------------------------
    answer, reason, is_refused = _release_asker(release_url)
    if answer is None and not is_refused:
        log(f'GitHub did not answer ({reason}); asking again in {RETRY_WAIT_S} s.')
        time.sleep(RETRY_WAIT_S)
        answer, reason, is_refused = _release_asker(release_url)
    if answer is not None:
        release = _release_reader(answer)
        if release is None:
            log("GitHub's answer could not be read: starting as it is.")
        return release
    if not is_refused:
        log(f'GitHub did not answer again ({reason}): starting as it is.')
        return None

    # ---- 2 Ask the Releases page when GitHub refused ---------------------------------
    log(f'{reason}; asking the Releases page instead.')
    address, page_reason = _release_page_asker(RELEASES_LINK)
    release = _release_page_reader(address, RELEASE_DOWNLOAD_URL) if address else None
    if release is None:
        log(f'The Releases page did not say which release is the newest '
            f'({page_reason or address}): starting as it is.',
            )
    return release


# ---- _own_version_reader -------------------------------------------------------------
def _own_version_reader(app: Path) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to read the app's version from its Info.plist, where the build
    writes it.

    ---- Inputs ----
    app : Path
        The .app folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The version, for example "2.4", or None when it cannot be read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        with open(app / 'Contents' / 'Info.plist', 'rb') as stream:
            return str(plistlib.load(stream)['CFBundleShortVersionString'])
    except (OSError, KeyError, ValueError, plistlib.InvalidFileException):
        return None


# ---- _release_asker ------------------------------------------------------------------
def _release_asker(url: str) -> Tuple[Optional[str], str, bool]:
    """
    ---- Summary ----
    Helper function to ask GitHub for its newest release with macOS's own curl, which
    uses the Mac's certificates (the app's Python cannot find any), keeping the reason
    when there is no answer.

    ---- Inputs ----
    url : str
        The address of GitHub's answer (a file:// address in the tests).

    ---- Globals read ----
    ASK_TIMEOUT_S, HIDDEN (module constants).

    ---- Outputs ----
    Tuple[Optional[str], str, bool]
        (GitHub's answer as JSON text, or None when there is none; why there is none,
        empty when there is one; True when GitHub refused the question).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _ask_problem_describer
    """

    try:
        asked = subprocess.run(['curl',
                                '-sS',
                                '--max-time',
                                str(ASK_TIMEOUT_S),
                                '-H',
                                'Accept: application/vnd.github+json',
                                '-w',
                                '\n%{http_code}',
                                url,
                                ],
                               capture_output=True,
                               text=True,
                               timeout=ASK_TIMEOUT_S + 5,
                               creationflags=HIDDEN,
                               )
    except OSError as exc:
        return None, f'curl could not be run ({exc.strerror})', False
    except subprocess.SubprocessError:
        return None, f'no answer within {ASK_TIMEOUT_S} s', False
    body, _, status = (asked.stdout or '').rpartition('\n')
    http_status = int(status) if status.strip().isdigit() else 0
    reason, is_refused = _ask_problem_describer(asked.returncode,
                                                http_status,
                                                body,
                                                asked.stderr or '',
                                                )
    return (None if reason else body), reason, is_refused


# ---- _release_page_asker -------------------------------------------------------------
def _release_page_asker(page_url: str) -> Tuple[Optional[str], str]:
    """
    ---- Summary ----
    Helper function to ask the Releases page where its newest release is, with macOS's
    own curl. The page leads to the release's own page, whose address ends in its tag.

    ---- Inputs ----
    page_url : str
        The Releases page's address for the newest release.

    ---- Globals read ----
    ASK_TIMEOUT_S, HIDDEN (module constants).

    ---- Outputs ----
    Tuple[Optional[str], str]
        (the address the page leads to, or None when there is none; why there is none,
        empty when there is one).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _ask_problem_describer
    """

    try:
        asked = subprocess.run(['curl',
                                '-sS',
                                '--max-time',
                                str(ASK_TIMEOUT_S),
                                '-o',
                                os.devnull,
                                '-w',
                                '%{http_code}\n%{redirect_url}',
                                page_url,
                                ],
                               capture_output=True,
                               text=True,
                               timeout=ASK_TIMEOUT_S + 5,
                               creationflags=HIDDEN,
                               )
    except OSError as exc:
        return None, f'curl could not be run ({exc.strerror})'
    except subprocess.SubprocessError:
        return None, f'no answer within {ASK_TIMEOUT_S} s'
    status, _, address = (asked.stdout or '').partition('\n')
    if asked.returncode != 0:
        reason, _ = _ask_problem_describer(asked.returncode, 0, '', asked.stderr or '')
        return None, reason
    if not address.strip():
        return None, f'it answered with code {status.strip() or "none"}'
    return address.strip(), ''


# ---- _release_page_reader ------------------------------------------------------------
def _release_page_reader(address: str,
                         download_url: str,
                         ) -> Optional[Tuple[str, Dict[str, Tuple[str, int]]]]:
    """
    ---- Summary ----
    Helper function to read the newest release's version from the address the Releases
    page leads to, and to make the addresses of its zips.

    ---- Inputs ----
    address : str
        The newest release's own page, ending in /releases/tag/V<version>.
    download_url : str
        Where the releases' zips are, each under its tag.

    ---- Globals read ----
    APPLE_SILICON_ZIP, INTEL_ZIP, TAG_ADDRESS_PATTERN, VERSION_PATTERN (module
    constants).

    ---- Outputs ----
    Optional[Tuple[str, Dict[str, Tuple[str, int]]]]
        (the version without its V, {zip name: (address, 0 as the size is not
        known)}), or None when the address does not end in a release's tag.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    found = TAG_ADDRESS_PATTERN.search(address.strip())
    if found is None:
        return None
    tag = found.group(1)
    match = VERSION_PATTERN.fullmatch(tag)
    if match is None:
        return None
    zips = {name: (f'{download_url}/{tag}/{name}', 0)
            for name in (APPLE_SILICON_ZIP, INTEL_ZIP)
            }
    return match.group(1), zips


# ---- _release_reader -----------------------------------------------------------------
def _release_reader(text: str) -> Optional[Tuple[str, Dict[str, Tuple[str, int]]]]:
    """
    ---- Summary ----
    Helper function to read the version and the zips from GitHub's answer about its
    newest release.

    ---- Inputs ----
    text : str
        GitHub's answer: JSON with "tag_name" (V<version>) and "assets", each with
        "name", "browser_download_url" and "size".

    ---- Globals read ----
    VERSION_PATTERN (module constant).

    ---- Outputs ----
    Optional[Tuple[str, Dict[str, Tuple[str, int]]]]
        (the version without its V, {zip name: (address, size in bytes)}), or None
        when the answer is not of that form.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        answer = json.loads(text)
        match = VERSION_PATTERN.fullmatch(str(answer['tag_name']))
        zips = {str(asset['name']): (str(asset['browser_download_url']),
                                     int(asset.get('size') or 0),
                                     )
                for asset in answer.get('assets', [])
                }
    except (ValueError, KeyError, TypeError, AttributeError):
        return None
    return (match.group(1), zips) if match else None


# ---- _start_command_maker ------------------------------------------------------------
def _start_command_maker(app: Path) -> List[str]:
    """
    ---- Summary ----
    Helper function to give the command that opens the app once it is swapped: macOS's
    open, as a click does, passing on the check switch when it is set.

    ---- Inputs ----
    app : Path
        The .app folder.

    ---- Globals read ----
    SELF_TEST_SWITCH (module constant); os.environ['PORTIMAO_SELF_TEST'].

    ---- Outputs ----
    List[str]
        The command and its arguments.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    command = ['open', '-n']
    switch = os.environ.get(SELF_TEST_SWITCH)
    if switch:  # the Mac check follows the update through to the new app's self-test
        command += ['--env', f'{SELF_TEST_SWITCH}={switch}']
    return command + [app.as_posix()]


# ---- _status_window_maker ------------------------------------------------------------
def _status_window_maker(version: str) -> Optional[Callable[[str], None]]:
    """
    ---- Summary ----
    Helper function to open a small window that shows how the update is going. The
    caller runs it with the returned function's ``mainloop`` attribute.

    ---- Inputs ----
    version : str
        The version being installed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Callable[[str], None]]
        Function that shows a line of text in the window (safe from any thread), with
        the attributes ``mainloop`` and ``close``; None when no window can open.

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
        root = tk.Tk()
    except Exception:  # no window: the update goes on without one
        return None
    root.title('Portimao')
    root.resizable(False, False)
    # closing it would leave the download running with nobody waiting for it
    root.protocol('WM_DELETE_WINDOW', lambda: None)
    label = ttk.Label(root,
                      text=f'Updating Portimao to V{version} ...',
                      padding=(24, 18, 24, 6),
                      )
    label.pack()
    bar = ttk.Progressbar(root, mode='indeterminate', length=320)
    bar.pack(padx=24, pady=(0, 18))
    bar.start(12)
    messages: 'queue.Queue' = queue.Queue()

    def poll() -> None:
        while not messages.empty():
            text = messages.get()
            if text is None:  # close, asked for by the download thread
                root.destroy()
                return
            label.configure(text=text)
        root.after(100, poll)

    def show(text: str) -> None:
        messages.put(text)

    # Tk is only touched by the main thread (other threads crash it on macOS)
    show.mainloop = lambda: (poll(), root.mainloop())  # type: ignore[attr-defined]
    show.close = lambda: messages.put(None)  # type: ignore[attr-defined]
    return show


# ---- _translation_checker ------------------------------------------------------------
def _translation_checker() -> bool:
    """
    ---- Summary ----
    Helper function to say whether the app runs under Rosetta (an Intel app on an Apple
    Silicon Mac).

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True under Rosetta.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        asked = subprocess.run(['sysctl', '-n', 'sysctl.proc_translated'],
                               capture_output=True,
                               text=True,
                               )
    except OSError:
        return False
    return asked.stdout.strip() == '1'


# ---- _version_splitter ---------------------------------------------------------------
def _version_splitter(text: str) -> Optional[Tuple[int, ...]]:
    """
    ---- Summary ----
    Helper function to turn a version into its numbers, for comparing.

    ---- Inputs ----
    text : str
        A version such as "2.3.1" or "V2.3.1".

    ---- Globals read ----
    VERSION_PATTERN (module constant).

    ---- Outputs ----
    Optional[Tuple[int, ...]]
        The numbers without trailing zeros, so 2.3.0 and 2.3 are equal; None when the
        text is not a version.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    match = VERSION_PATTERN.fullmatch(text.strip())
    if not match:
        return None
    parts = [int(part) for part in match.group(1).split('.')]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


# ---- _zip_downloader -----------------------------------------------------------------
def _zip_downloader(url: str,
                    target: Path,
                    size_bytes: int,
                    version: str,
                    show: Callable[[str], None],
                    ) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to download the zip with macOS's own curl, showing how much has
    come.

    ---- Inputs ----
    url : str
        Where the zip is.
    target : Path
        File to write.
    size_bytes : int
        Size of the zip as GitHub gives it; 0 when not known.
    version : str
        The version being installed, for the progress line.
    show : Callable[[str], None]
        Shows a line of progress.

    ---- Globals read ----
    CONNECT_TIMEOUT_S, HIDDEN, PROGRESS_STEP_S, STALL_BYTES_PER_S, STALL_S (module
    constants).

    ---- Outputs ----
    Optional[str]
        None when the whole zip came; otherwise what went wrong.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    total_mb = f' of {size_bytes / 1e6:.0f}' if size_bytes else ''
    try:
        download = subprocess.Popen(['curl',
                                     '-fsSL',
                                     '--connect-timeout',
                                     str(CONNECT_TIMEOUT_S),
                                     '--speed-limit',
                                     str(STALL_BYTES_PER_S),
                                     '--speed-time',
                                     str(STALL_S),
                                     '-o',
                                     str(target),
                                     url,
                                     ],
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    creationflags=HIDDEN,
                                    )
    except OSError as exc:
        return f'curl could not be run ({exc.strerror})'
    while download.poll() is None:
        done_mb = target.stat().st_size / 1e6 if target.exists() else 0.0
        show(f'Updating Portimao to V{version} ... {done_mb:.0f}{total_mb} MB')
        time.sleep(PROGRESS_STEP_S)
    _, errors = download.communicate()
    if download.returncode != 0:
        return (errors or '').strip() or f'curl ended with {download.returncode}'
    if size_bytes and target.stat().st_size != size_bytes:
        return 'the zip is not whole'
    return None


# ---- _zip_namer ----------------------------------------------------------------------
def _zip_namer(machine: str, is_translated: bool) -> str:
    """
    ---- Summary ----
    Helper function to name the zip for this kind of Mac.

    ---- Inputs ----
    machine : str
        The chip the app runs on, as platform.machine() gives it ('arm64' or 'x86_64').
    is_translated : bool
        True when an Intel app runs under Rosetta on an Apple Silicon Mac.

    ---- Globals read ----
    APPLE_SILICON_ZIP, INTEL_ZIP (module constants).

    ---- Outputs ----
    str
        The zip's name: Apple Silicon also under Rosetta, so the Mac moves to the app
        made for it; Intel otherwise.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return APPLE_SILICON_ZIP if machine == 'arm64' or is_translated else INTEL_ZIP


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- swap_starter --------------------------------------------------------------------
def swap_starter(swapper_text: str,
                 closing_pid: int,
                 app: Path,
                 new_app: Path,
                 log_path: Path,
                 start_command: Sequence[str],
                 ) -> 'subprocess.Popen':
    """
    ---- Summary ----
    Main function to start the swap on its own (launchers/mac_app_swapper.sh), so it
    goes on once the app has closed: it waits for the app to close, moves the new app
    into its place and opens it.

    ---- Inputs ----
    swapper_text : str
        The text of the swap script; run with sh -c, so nothing is read from the app
        being replaced.
    closing_pid : int
        Process id of the app that closes first.
    app : Path
        The .app folder to replace.
    new_app : Path
        The new .app folder, in the update folder beside it.
    log_path : Path
        The update log, which the swap adds its lines to.
    start_command : Sequence[str]
        The command that opens the app afterwards.

    ---- Globals read ----
    HIDDEN (module constant).

    ---- Outputs ----
    subprocess.Popen
        The swap, running on its own.

    ---- Globals mutated ----
    None. Starts a process (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return subprocess.Popen(['sh',
                             '-c',
                             swapper_text,
                             'mac_app_swapper',
                             str(closing_pid),
                             app.as_posix(),
                             new_app.as_posix(),
                             log_path.as_posix(),
                             *start_command,
                             ],
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True,
                            creationflags=HIDDEN,
                            )


# ---- update_installer ----------------------------------------------------------------
def update_installer(places: UserPlaces,
                     executable: Optional[str] = None,
                     release_url: str = RELEASE_URL,
                     closing_pid: Optional[int] = None,
                     start_command: Optional[Sequence[str]] = None,
                     shows_messages: bool = True,
                     ) -> bool:
    """
    ---- Summary ----
    Main function to update the Mac app at its start. It asks GitHub for the newest
    release (a few seconds at most) and, when it is newer, downloads the zip for this
    kind of Mac with a small "Updating Portimao" window, and starts the swap, which puts
    it in place once this app has closed and opens it. When GitHub does not answer it
    asks once more, and when GitHub refuses it asks the Releases page; with no answer at
    all it starts as it is and says nothing. When it cannot replace itself, or the
    download fails, it starts as it is with a message saying where to download the new
    one. Run from source, nothing is done. Every step, with the reason for any failure,
    is written to logs/update.log.

    ---- Inputs ----
    places : UserPlaces
        Where the user's things are kept, and whether this is the app.
    executable : Optional[str]
        Path of the running program; None for this one (sys.executable).
    release_url : str
        Where GitHub's answer about its newest release is (a file:// address in the
        tests).
    closing_pid : Optional[int]
        Process id the swap waits for; None for this program.
    start_command : Optional[Sequence[str]]
        Command that opens the app after the swap; None for macOS's open.
    shows_messages : bool
        False to show no window and no message (for the tests).

    ---- Globals read ----
    RELEASE_URL, SWAPPER, UPDATE_FOLDER_NAME (module constants).

    ---- Outputs ----
    bool
        True when the swap has started, so the app must close now; False when the app
        starts as it is.

    ---- Globals mutated ----
    None. Writes the update log, downloads into the update folder beside the app,
    shows a window or a message and starts the swap (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _app_finder
    _blocker_finder
    _leftover_cleaner
    _log_opener
    _new_app_fetcher
    _newer_checker
    _newest_release_finder
    _own_version_reader
    _start_command_maker
    _status_window_maker
    _translation_checker
    _zip_namer
    swap_starter
    update_notice_shower
    """

    # ---- 1 Find the app --------------------------------------------------------------
    if not places.is_app:
        return False
    app = _app_finder(executable or sys.executable)
    if app is None:
        return False
    log_path, log = _log_opener(places.logs_folder)
    _leftover_cleaner(app)
    own = _own_version_reader(app)
    log(f'Looking for a newer Portimao; this app is V{own} at {app}')

    # ---- 2 Find GitHub's newest release ----------------------------------------------
    release = _newest_release_finder(release_url, log)
    if release is None:
        return False
    version, zips = release
    if not _newer_checker(own, version):
        log(f'The newest release is V{version}: nothing to update.')
        return False
    zip_name = _zip_namer(platform.machine(), _translation_checker())
    log(f'V{version} is out; this Mac needs {zip_name}.')

    # ---- 3 Check the app can replace itself ------------------------------------------
    blocker = _blocker_finder(app)
    if blocker is None and zip_name not in zips:
        blocker = f'the release has no {zip_name}'
    if blocker is None:
        try:
            swapper_text = (places.program_folder / SWAPPER).read_text(encoding='utf-8')
        except OSError:
            blocker = 'the app has lost its swap script'
    if blocker is not None:
        log(f'This app cannot update itself ({blocker}): starting as it is.')
        if shows_messages:
            update_notice_shower(version, blocker)
        return False

    # ---- 4 Download and unpack the new app -------------------------------------------
    url, size_bytes = zips[zip_name]
    folder = app.parent / UPDATE_FOLDER_NAME
    window = _status_window_maker(version) if shows_messages else None
    if window is None:
        new_app = _new_app_fetcher(url,
                                   size_bytes,
                                   version,
                                   folder,
                                   lambda text: None,
                                   log,
                                   )
    else:
        fetched: List[Optional[Path]] = []

        def work() -> None:
            fetched.append(_new_app_fetcher(url,
                                            size_bytes,
                                            version,
                                            folder,
                                            window,
                                            log,
                                            ),
                           )
            window.close()  # type: ignore[attr-defined]

        threading.Thread(target=work, daemon=True).start()
        window.mainloop()  # type: ignore[attr-defined]
        new_app = fetched[0] if fetched else None
    if new_app is None:
        _leftover_cleaner(app)
        log('Starting as it is.')
        if shows_messages:
            update_notice_shower(version, 'the download did not finish')
        return False

    # ---- 5 Start the swap ------------------------------------------------------------
    try:
        swap_starter(swapper_text,
                     os.getpid() if closing_pid is None else closing_pid,
                     app,
                     new_app,
                     log_path,
                     _start_command_maker(app,
                                          ) if start_command is None else start_command,
                     )
    except OSError as exc:
        _leftover_cleaner(app)
        log(f'The swap could not be started ({exc.strerror}): starting as it is.')
        if shows_messages:
            update_notice_shower(version, 'the new app could not be put in place')
        return False
    log(f'V{version} is downloaded; it goes in place of this app once it has closed.')
    return True
