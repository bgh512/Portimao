"""
One plain sentence for each warning and problem the user meets, with the details of a
problem kept in the log only.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import dis
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.output_capture import captured_buffer_getter
from utils_shared.run_logging import details_writer


# ---- CONSTANTS -----------------------------------------------------------------------
# Portimao's own modules, by the first part of their name: read from the running code,
# so it holds in the Mac app too, which has no source files
OWN_MODULES = ('__main__',
               'config',
               'launchers',
               'main',
               'utils_custom',
               'utils_shared',
               'utils_viewer',
               )
RAISE_OPCODE = dis.opmap['RAISE_VARARGS']  # the step a raise statement runs
SEND_LOG = 'send it through the Issues page (see Feedback at the top of the README)'


# ---- NOTICE HELPERS ------------------------------------------------------------------


# ---- _file_namer ---------------------------------------------------------------------
def _file_namer(error: OSError) -> str:
    """
    ---- Summary ----
    Helper function to name the file a file problem is about, without its folders.

    ---- Inputs ----
    error : OSError
        The problem; its filename is None when the system did not say which file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The file's name, or "A file" when it is not known.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if error.filename is None:
        return 'A file'
    return Path(os.fsdecode(error.filename)).name or 'A file'


# ---- _own_sentence_finder ------------------------------------------------------------
def _own_sentence_finder(error: BaseException) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to give the message of an error that Portimao's own code raised
    with a message of its own, which is written for the user. An error that Python or
    a package raised has none: its last step is not a raise statement in one of
    Portimao's modules (a failed float() in Portimao's code, for example, is Python's).

    ---- Inputs ----
    error : BaseException
        The problem, with its traceback.

    ---- Globals read ----
    OWN_MODULES, RAISE_OPCODE (module constants).

    ---- Outputs ----
    Optional[str]
        The message, or None when the error is not one of Portimao's own or has no
        text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Find the step that raised it ----------------------------------------------
    trace = error.__traceback__
    if trace is None:
        return None
    while trace.tb_next is not None:
        trace = trace.tb_next

    # ---- 2 Check it is a raise in Portimao's code ------------------------------------
    module = str(trace.tb_frame.f_globals.get('__name__', ''))
    if module.split('.')[0] not in OWN_MODULES:
        return None
    code = trace.tb_frame.f_code.co_code
    if not 0 <= trace.tb_lasti < len(code) or code[trace.tb_lasti] != RAISE_OPCODE:
        return None

    # ---- 3 Read its message ----------------------------------------------------------
    if not error.args or not isinstance(error.args[0], str):
        return None
    return error.args[0].strip() or None


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- problem_describer ---------------------------------------------------------------
def problem_describer(error: BaseException, place: str) -> str:
    """
    ---- Summary ----
    Main function to say in plain words what went wrong and what to do, never with
    Python's own error text: Portimao's own message when it wrote one, a sentence of
    its own for a file that is open elsewhere, missing or unreadable and for a lack of
    memory, and otherwise that Portimao met a problem it did not expect, with where the
    details are.

    ---- Inputs ----
    error : BaseException
        The problem, with its traceback.
    place : str
        Where the details were written, in words (details_writer); empty when they
        could not be written anywhere.

    ---- Globals read ----
    SEND_LOG (module constant).

    ---- Outputs ----
    str
        One or two sentences, ending in a full stop.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _file_namer
    _own_sentence_finder
    """

    # ---- 1 Portimao's own message ----------------------------------------------------
    own = _own_sentence_finder(error)
    if own is not None:
        return own if own.endswith(('.', '?', '!')) else f'{own}.'

    # ---- 2 Problems with a known cause -----------------------------------------------
    if isinstance(error, MemoryError):
        return ('The computer ran out of memory: close other programs, or use fewer or '
                'smaller files, and try again.'
                )
    if isinstance(error, PermissionError):
        return (f'{_file_namer(error)} could not be opened or saved, perhaps because '
                f'it is open in another program such as Excel: close it there and try '
                f'again.'
                )
    if isinstance(error, FileNotFoundError):
        return (f'{_file_namer(error)} could not be found: check that it is still in '
                f'its folder and try again.'
                )
    if isinstance(error, OSError) and error.strerror:
        return (f"{_file_namer(error)} could not be read or saved (the computer says: "
                f"{error.strerror.rstrip('.')})."
                )

    # ---- 3 Anything else -------------------------------------------------------------
    if place:
        return (f'Portimao met a problem it did not expect. The details are in '
                f'{place}: {SEND_LOG}.'
                )
    return f'Portimao met a problem it did not expect: please report it ({SEND_LOG}).'


# ---- problem_shower ------------------------------------------------------------------
def problem_shower(lead: str, error: BaseException) -> None:
    """
    Main function to show a problem as a warning, in plain words, with its details in
    the log only. See problem_teller.
    """

    warning_shower(problem_teller(lead, error))


# ---- problem_teller ------------------------------------------------------------------
def problem_teller(lead: str, error: BaseException) -> str:
    """
    ---- Summary ----
    Main function to write the details of a problem (Python's own report of it) to the
    log only, and give the sentence the user sees instead.

    ---- Inputs ----
    lead : str
        What could not be done, for example "Preview not drawn for run1"; it starts the
        sentence and heads the details in the log. Leading spaces are kept in the
        sentence, for the indent of the terminal.
    error : BaseException
        The problem, with its traceback.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        "<lead>: <what went wrong and what to do>" (problem_describer).

    ---- Globals mutated ----
    None. Writes the details to the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    details_writer
    problem_describer
    """

    report = ''.join(traceback.format_exception(type(error),
                                                error,
                                                error.__traceback__,
                                                ),
                     )
    place = details_writer(f'\n---- Details of a problem, {datetime.now():%H:%M:%S}: '
                           f'{lead.strip()} ----\n{report}',
                           )
    return f'{lead}: {problem_describer(error, place)}'


# ---- warning_shower ------------------------------------------------------------------
def warning_shower(text: str) -> None:
    """
    ---- Summary ----
    Main function to show a warning: it is printed as it is, and while the window
    captures the output of a preview it is also kept as a warning, so the window shows
    it under the plot whatever its words.

    ---- Inputs ----
    text : str
        The warning, in plain words; leading spaces indent it in the terminal only.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints the warning and adds it to the capture of the thread, if any (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    captured_buffer_getter
    """

    print(text)
    captured = captured_buffer_getter()
    if captured is not None:
        captured.warnings.append(text.strip())
