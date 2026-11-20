"""
Where the program keeps the user's own things: the program folder from source, a folder
in the home folder in the Mac app.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ---- CONSTANTS -----------------------------------------------------------------------
OWN_FOLDER_NAME = 'Portimao'  # the app's own folder, in the home folder
FITS_FOLDER_NAME = 'fits'
LOGS_FOLDER_NAME = 'logs'
LAST_ANSWERS_NAME = 'last_answers.json'
LAUNCH_LOG_NAME = 'launch.log'  # the name the launcher gives its log, so both read alike
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


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- app_output_logger ---------------------------------------------------------------
def app_output_logger(places: UserPlaces) -> None:
    """
    ---- Summary ----
    Main function to send everything the Mac app prints to logs/launch.log in its own
    folder, as the launcher does for a program run from source. The app has no launcher
    and no terminal, so without this its messages would be lost. Run from source,
    nothing changes.

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
    None.
    """

    global _app_log
    if not places.is_app:
        return
    try:
        _app_log = open(places.logs_folder / LAUNCH_LOG_NAME,
                        'w',
                        encoding='utf-8',
                        errors='replace',
                        buffering=1,
                        )
    except OSError:  # the program still runs; only its log is missing
        return
    sys.stdout = sys.stderr = _app_log


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
