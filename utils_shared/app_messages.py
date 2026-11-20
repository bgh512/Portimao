"""
The Mac app's own messages: why it could not start, with the Mac report to copy, and
where to download a newer version.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import subprocess
from pathlib import Path
from typing import Sequence

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.user_places import UserPlaces


# ---- CONSTANTS -----------------------------------------------------------------------
FORM_LINK = 'https://github.com/bgh512/Portimao/issues/new?template=mac_problem.yml'
RELEASES_LINK = 'https://github.com/bgh512/Portimao/releases/latest'
REPORT_SCRIPT = Path('launchers') / 'mac_report.sh'  # inside the program folder
REPORT_TIMEOUT_S = 120  # the report checks the app's signature, which takes a while
COPY_BUTTON = 'Copy details'
DOWNLOAD_BUTTON = 'Open the download page'
# the end of every sentence that asks for the details to be sent
SEND_DETAILS = ('click Copy details, then paste them (Cmd + V) into the Mac problem '
                'form that opens')


# ---- MESSAGE HELPERS -----------------------------------------------------------------


# ---- _applescript_quoter -------------------------------------------------------------
def _applescript_quoter(text: str) -> str:
    """
    ---- Summary ----
    Helper function to write a text as an AppleScript string, so quotes and backslashes
    in it (a folder name, for example) cannot end the string early.

    ---- Inputs ----
    text : str
        Any text.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The text between double quotes, with backslashes and double quotes escaped.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


# ---- _dialog_script_maker ------------------------------------------------------------
def _dialog_script_maker(text: str,
                         title: str,
                         buttons: Sequence[str],
                         icon: str,
                         ) -> str:
    """
    ---- Summary ----
    Helper function to write the AppleScript of a macOS message with buttons, the last
    button being the one Enter presses.

    ---- Inputs ----
    text : str
        The message.
    title : str
        Title of the message window.
    buttons : Sequence[str]
        Button names, left to right.
    icon : str
        'caution' for a problem, 'note' for news.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        One AppleScript statement; osascript prints "button returned:<name>".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _applescript_quoter
    """

    names = ', '.join(_applescript_quoter(button) for button in buttons)
    return (f'display dialog {_applescript_quoter(text)} '
            f'with title {_applescript_quoter(title)} '
            f'buttons {{{names}}} '
            f'default button {_applescript_quoter(buttons[-1])} '
            f'with icon {icon}'
            )


# ---- _report_copier ------------------------------------------------------------------
def _report_copier(places: UserPlaces) -> bool:
    """
    ---- Summary ----
    Helper function to run the Mac report that comes inside the app and copy what it
    prints to the clipboard.

    ---- Inputs ----
    places : UserPlaces
        Where the program's own files are (the report is in its launchers folder).

    ---- Globals read ----
    REPORT_SCRIPT, REPORT_TIMEOUT_S (module constants).

    ---- Outputs ----
    bool
        True when the report was copied; False when it could not be run or copied.

    ---- Globals mutated ----
    None. Runs the report and fills the clipboard (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        report = subprocess.run(['sh', str(places.program_folder / REPORT_SCRIPT)],
                                capture_output=True,
                                text=True,
                                timeout=REPORT_TIMEOUT_S,
                                )
        if not report.stdout.strip():
            return False
        copied = subprocess.run(['pbcopy'], input=report.stdout, text=True)
        return copied.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- start_problem_shower ------------------------------------------------------------
def start_problem_shower(sentence: str, places: UserPlaces) -> None:
    """
    ---- Summary ----
    Main function to say why Portimao could not start. The sentence is always printed
    (to the terminal, or to the app's launch log). In the Mac app, which has no
    terminal, a macOS message also shows it, with a Copy details button that copies the
    Mac report and opens the Mac problem form to paste it into.

    ---- Inputs ----
    sentence : str
        One sentence that says what went wrong and what to do.
    places : UserPlaces
        Where the program's files are, and whether this is the app.

    ---- Globals read ----
    COPY_BUTTON, FORM_LINK (module constants).

    ---- Outputs ----
    None
        Nothing. Waits until the message is closed. A message that cannot be shown
        leaves only the printed sentence.

    ---- Globals mutated ----
    None. Prints, shows a message, may fill the clipboard and open the form in the
    browser (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _dialog_script_maker
    _report_copier
    """

    print(sentence)
    if not places.is_app:
        return
    script = _dialog_script_maker(sentence,
                                  'Portimao could not start',
                                  [COPY_BUTTON, 'OK'],
                                  'caution',
                                  )
    try:
        answer = subprocess.run(['osascript', '-e', script],
                                capture_output=True,
                                text=True,
                                )
        if f'button returned:{COPY_BUTTON}' in answer.stdout:
            if not _report_copier(places):
                print('The details could not be copied: send logs/launch.log from '
                      'the Portimao folder in your home folder instead.',
                      )
            subprocess.run(['open', FORM_LINK])
    except OSError:  # no macOS message here: the printed sentence is all there is
        pass


# ---- update_notice_shower ------------------------------------------------------------
def update_notice_shower(version: str, reason: str) -> None:
    """
    ---- Summary ----
    Main function to say, in a macOS message that does not hold up the start, that a
    newer Portimao is out but this copy could not update itself, with a button that
    opens the download page.

    ---- Inputs ----
    version : str
        The newer version, for example "2.5".
    reason : str
        Why this copy could not update itself, in plain words.

    ---- Globals read ----
    DOWNLOAD_BUTTON, RELEASES_LINK (module constants).

    ---- Outputs ----
    None
        Nothing. Returns at once; the message stays until it is closed.

    ---- Globals mutated ----
    None. Shows a message, and opens the page in the browser when asked (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _applescript_quoter
    _dialog_script_maker
    """

    text = (f'Portimao V{version} is out, but this copy could not update itself '
            f'({reason}): download the new one from the Releases page and put it in '
            f'place of this one.'
            )
    asked = _dialog_script_maker(text,
                                 'Portimao update',
                                 ['Later', DOWNLOAD_BUTTON],
                                 'note',
                                 )
    script = (f'set answer to button returned of ({asked})\n'
              f'if answer is {_applescript_quoter(DOWNLOAD_BUTTON)} then '
              f'open location {_applescript_quoter(RELEASES_LINK)}'
              )
    try:
        subprocess.Popen(['osascript', '-e', script],
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True,
                         )
    except OSError:  # no macOS message here: the update log still says it
        pass
