"""
The Mac app's start: updates the app, then runs the program, and says what to do when
it cannot start.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import sys
import traceback
from datetime import datetime

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.app_messages import SEND_DETAILS, start_problem_shower
from utils_shared.app_updater import update_installer
from utils_shared.user_places import LAUNCH_LOG_NAME, UserPlaces, user_places_finder


# ---- CONSTANTS -----------------------------------------------------------------------
STOPPED_SENTENCE = f'Portimao stopped because of a problem: {SEND_DETAILS}.'


# ---- START HELPERS -------------------------------------------------------------------


# ---- _problem_logger -----------------------------------------------------------------
def _problem_logger(places: UserPlaces, heading: str) -> None:
    """
    ---- Summary ----
    Helper function to add the error being handled, with its traceback, to the app's
    launch log, which the Mac report shows.

    ---- Inputs ----
    places : UserPlaces
        Where the logs folder is.
    heading : str
        What was going on when the error came.

    ---- Globals read ----
    LAUNCH_LOG_NAME (imported constant).

    ---- Outputs ----
    None
        Nothing. A log that cannot be written is left as it is.

    ---- Globals mutated ----
    None. Writes the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        sys.stdout.flush()  # the program may have the same log open already
    except (AttributeError, OSError, ValueError):
        pass
    try:
        places.logs_folder.mkdir(parents=True, exist_ok=True)
        with open(places.logs_folder / LAUNCH_LOG_NAME,
                  'a',
                  encoding='utf-8',
                  errors='replace',
                  ) as log:
            log.write(f'\n{heading}, {datetime.now():%Y-%m-%d %H:%M:%S}:\n'
                      f'{traceback.format_exc()}',
                      )
    except OSError:
        pass


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function of the Mac app (PyInstaller builds it from this file): it updates the
    app from GitHub's newest release first, then runs the program (main.py). Anything
    that stops the program is written to the launch log and shown in a message with a
    Copy details button.

    ---- Inputs ----
    None.

    ---- Globals read ----
    STOPPED_SENTENCE (module constant).

    ---- Outputs ----
    int
        0 when the new version opens in place of this one, otherwise the program's exit
        code (1 when it stopped because of a problem).

    ---- Globals mutated ----
    None. May replace the app, runs the program and shows messages (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _problem_logger
    start_problem_shower
    update_installer
    user_places_finder
    """

    # ---- 1 Update the app ------------------------------------------------------------
    places = user_places_finder()
    try:
        if update_installer(places):
            return 0  # the new version opens once this one has closed
    except Exception:  # an update must never stop the start: the app starts as it is
        _problem_logger(places, 'The update stopped')

    # ---- 2 Run the program -----------------------------------------------------------
    try:
        import main as program
        return program.main()
    except Exception:  # whatever it is, the user is told what to do with it
        _problem_logger(places, 'Portimao stopped')
        start_problem_shower(STOPPED_SENTENCE, places)
        return 1


if __name__ == '__main__':
    sys.exit(main())
