"""
Where the program keeps the user's own things: the program folder from source, a folder
in the home folder in the Mac app.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO


# ---- CONSTANTS -----------------------------------------------------------------------
OWN_FOLDER_NAME = 'Portimao'  # the app's own folder, in the home folder
FITS_FOLDER_NAME = 'fits'
LOGS_FOLDER_NAME = 'logs'
LAST_ANSWERS_NAME = 'last_answers.json'
LAUNCH_LOG_NAME = 'launch.log'  # the name the launcher gives its log, so both read alike
# The launch log keeps the starts before, so a problem met before the run's own log
# starts is still there when Portimao is opened again; past this size only the newest
# half is kept.
LAUNCH_LOG_MAX_BYTES = 1_000_000
LAUNCH_LOG_START = '==== Portimao started'  # begins the line each start adds
_app_log = None  # the app's log file, kept open while the program runs


# ---- UserPlaces ----------------------------------------------------------------------
@dataclass(frozen=True)
class UserPlaces:
    """
    ---- Summary ----
    Where the program's own files are, and where the user's own things are kept: the
    fits, the folder used last, the logs and the data folders offered by number.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    program_folder: Path
    own_folder: Path
    fits_folder: Path
    last_answers_file: Path
    logs_folder: Path
    is_app: bool


# ---- LAUNCH LOG HELPERS --------------------------------------------------------------


# ---- _launch_log_shortener -----------------------------------------------------------
def _launch_log_shortener(path: Path, max_bytes: int) -> None:
    """
    ---- Summary ----
    Helper function to cut the launch log to its newest half once it is bigger than the
    limit, from the first start line in that half (or the first whole line when the
    half holds none).

    ---- Inputs ----
    path : Path
        The launch log; nothing is done when it is missing.
    max_bytes : int
        Size in bytes past which the log is cut.

    ---- Globals read ----
    LAUNCH_LOG_START (module constant).

    ---- Outputs ----
    None
        Nothing. A log that cannot be read or written is left as it is.

    ---- Globals mutated ----
    None. Rewrites the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        if path.stat().st_size <= max_bytes:
            return
        newest = path.read_bytes()[-(max_bytes // 2):]
        start = newest.find(f'\n{LAUNCH_LOG_START}'.encode('utf-8'))
        if start < 0:
            start = newest.find(b'\n')
        path.write_bytes(newest[start + 1:])
    except OSError:  # a long log is better than none
        pass


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- app_output_logger ---------------------------------------------------------------
def app_output_logger(places: UserPlaces) -> None:
    """
    ---- Summary ----
    Main function to send everything the Mac app prints to logs/launch.log in its own
    folder, after the starts before, as the launcher does for a program run from
    source. The app has no launcher and no terminal, so without this its messages
    would be lost. Run from source, nothing changes.

    ---- Inputs ----
    places : UserPlaces
        Where the user's things are kept (user_places_finder); the logs folder must
        exist (user_folder_preparer).

    ---- Globals read ----
    LAUNCH_LOG_NAME (module constant).

    ---- Outputs ----
    None
        Nothing. A log that cannot be opened leaves the output where it was.

    ---- Globals mutated ----
    _app_log (module state); sys.stdout and sys.stderr are replaced by the log file.

    ---- Equations ----
    None.

    ---- Helpers ----
    launch_log_opener
    """

    global _app_log
    if not places.is_app:
        return
    try:
        _app_log = launch_log_opener(places.logs_folder / LAUNCH_LOG_NAME)
    except OSError:  # the program still runs; only its log is missing
        return
    sys.stdout = sys.stderr = _app_log


# ---- launch_log_opener ---------------------------------------------------------------
def launch_log_opener(path: Path, max_bytes: int = LAUNCH_LOG_MAX_BYTES) -> TextIO:
    """
    ---- Summary ----
    Main function to open the launch log for a new start: the starts before are kept
    (cut to the newest half once the log passes the limit), and a line with the date
    and time marks where this start begins. The launcher and the Mac app both open it
    here, so it reads alike.

    ---- Inputs ----
    path : Path
        The launch log (logs/launch.log); its folder is made when missing.
    max_bytes : int
        Size in bytes past which the starts before are cut to the newest half.

    ---- Globals read ----
    LAUNCH_LOG_START (module constant).

    ---- Outputs ----
    TextIO
        The log, open for adding text (UTF-8, line by line), its start line already
        written. Raises OSError when it cannot be opened.

    ---- Globals mutated ----
    None. Makes the folder, may cut the log and writes the start line (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _launch_log_shortener
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    _launch_log_shortener(path, max_bytes)
    log = open(path, 'a', encoding='utf-8', errors='replace', buffering=1)
    gap = '\n' if log.tell() else ''  # a blank line after the start before
    log.write(f'{gap}{LAUNCH_LOG_START} {datetime.now():%Y-%m-%d %H:%M:%S} ====\n')
    # written out now: the launcher hands the same file to Portimao, which writes after
    log.flush()
    return log


# ---- user_folder_preparer ------------------------------------------------------------
def user_folder_preparer(places: UserPlaces) -> None:
    """
    ---- Summary ----
    Main function to make the Mac app's own folder, with its fits and logs folders, and
    to copy in each fit that comes with the program and is not there yet. A fit already
    there is never overwritten, so the user's changes are kept. Run from source,
    nothing is done: everything stays in the program folder.

    ---- Inputs ----
    places : UserPlaces
        Where the user's things are kept (user_places_finder).

    ---- Globals read ----
    FITS_FOLDER_NAME (module constant).

    ---- Outputs ----
    None
        Nothing. Raises OSError when the folders cannot be made; a fit that cannot be
        copied is left out.

    ---- Globals mutated ----
    None. Makes folders and copies files (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not places.is_app:
        return
    places.fits_folder.mkdir(parents=True, exist_ok=True)
    places.logs_folder.mkdir(parents=True, exist_ok=True)
    for fit in sorted((places.program_folder / FITS_FOLDER_NAME).glob('*.csv')):
        target = places.fits_folder / fit.name
        if target.exists():
            continue
        try:
            shutil.copy2(fit, target)
        except OSError:  # that fit is not offered; the others still are
            continue


# ---- user_places_finder --------------------------------------------------------------
def user_places_finder(is_app: Optional[bool] = None,
                       home: Optional[Path] = None,
                       program_folder: Optional[Path] = None,
                       ) -> UserPlaces:
    """
    ---- Summary ----
    Main function to give the places the program uses. Run from source (Windows, Linux,
    developers), everything is in the program folder, as it always was. Run as the Mac
    app, the program's own files are inside the app, which is never written to, and the
    user's things are in a Portimao folder in the home folder.

    ---- Inputs ----
    is_app : Optional[bool]
        True when running as the app; None to find out (the app sets sys.frozen).
    home : Optional[Path]
        Home folder; None for the user's own.
    program_folder : Optional[Path]
        Folder with the program's own files (fits, assets, QUESTION_FLOW.md); None to
        find it (inside the app, or the folder above utils_shared).

    ---- Globals read ----
    FITS_FOLDER_NAME, LAST_ANSWERS_NAME, LOGS_FOLDER_NAME, OWN_FOLDER_NAME (module
    constants); sys.frozen and sys._MEIPASS (set by the app).

    ---- Outputs ----
    UserPlaces
        The places. Nothing is checked or made (user_folder_preparer does that).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if is_app is None:
        is_app = bool(getattr(sys, 'frozen', False))
    if program_folder is None:
        program_folder = (Path(getattr(sys, '_MEIPASS', '')).resolve()
                          if is_app
                          else Path(__file__).resolve().parents[1]
                          )
    own_folder = ((home or Path.home()) / OWN_FOLDER_NAME
                  if is_app
                  else program_folder
                  )
    return UserPlaces(program_folder=program_folder,
                      own_folder=own_folder,
                      fits_folder=own_folder / FITS_FOLDER_NAME,
                      last_answers_file=own_folder / LAST_ANSWERS_NAME,
                      logs_folder=own_folder / LOGS_FOLDER_NAME,
                      is_app=is_app,
                      )
