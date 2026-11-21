"""
Mirror console output to a timestamped log file from the results folder question to the
end of the run, and keep the details of each problem in a log the user does not see.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.output_capture import captured_buffer_getter


# ---- CONSTANTS -----------------------------------------------------------------------
# Where the details of a problem go (details_writer): the log of the run being logged,
# else the stream and place set by details_place_setter.
_details_targets: dict = {'session': None, 'stream': None, 'place': ''}
# the colour codes of the window's terminal, which a log opened in a text editor would
# show as stray characters
COLOUR_CODE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


# ---- _Tee ----------------------------------------------------------------------------
class _Tee:
    """
    ---- Summary ----
    File-like object that writes everything to several streams at once: to the first
    as it is, to the others without the terminal's colour codes.

    ---- Attributes ----
    streams : Tuple[Any, ...]
        File-like objects every write is copied to.

    ---- Globals read ----
    COLOUR_CODE_PATTERN (module constant).

    ---- Methods ----
    __init__
    __getattr__
    flush
    isatty
    write
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, *streams: Any) -> None:
        """
        ---- Summary ----
        Method to store the streams that every write is copied to.

        ---- Inputs ----
        *streams : Any
            File-like objects (for example the console and the log file).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the streams attribute on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.streams = streams

    # ---- SPECIAL METHODS -------------------------------------------------------------

    # ---- __getattr__ -----------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        """
        ---- Summary ----
        Method to pass any other attribute lookup (such as encoding) to the first
        stream.

        ---- Inputs ----
        name : str
            Attribute name that was not found on the instance.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Any
            The attribute of the first stream.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return getattr(self.streams[0], name)

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- flush -----------------------------------------------------------------------
    def flush(self) -> None:
        """
        ---- Summary ----
        Method to flush every stream. The name is fixed by the file-like protocol.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Flushes every stream (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        for stream in self.streams:
            stream.flush()

    # ---- isatty ----------------------------------------------------------------------
    def isatty(self) -> bool:
        """
        ---- Summary ----
        Method to say whether the first stream is a terminal. The name is fixed by the
        file-like protocol.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when the first stream is an interactive terminal.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self.streams[0].isatty()

    # ---- write -----------------------------------------------------------------------
    def write(self, text: str) -> int:
        """
        ---- Summary ----
        Method to write text to every stream and flush it, unless the current thread is
        capturing its output (see output_capture), in which case it is kept by the
        capture. Every stream after the first gets the text without colour codes. The
        name is fixed by the file-like protocol.

        ---- Inputs ----
        text : str
            Text to write.

        ---- Globals read ----
        COLOUR_CODE_PATTERN (module constant).

        ---- Outputs ----
        int
            Number of characters written.

        ---- Globals mutated ----
        None. Writes to and flushes every stream (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        captured_buffer_getter
        """

        captured = captured_buffer_getter()
        if captured is not None:  # a thread that is capturing its output
            return captured.write(text)
        plain = COLOUR_CODE_PATTERN.sub('', text)
        for index, stream in enumerate(self.streams):
            stream.write(text if index == 0 else plain)
            stream.flush()
        return len(text)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- answer_logger -------------------------------------------------------------------
def answer_logger(text: str) -> None:
    """
    ---- Summary ----
    Main function to add an answer the user gave to the log of the run being logged,
    under its question; the window shows the answer itself. Nothing is done while no
    run is being logged.

    ---- Inputs ----
    text : str
        The answer as it is to read in the log, for example "   > 12".

    ---- Globals read ----
    _details_targets (module state).

    ---- Outputs ----
    None
        Nothing. An answer that cannot be written (a full disk) is left out.

    ---- Globals mutated ----
    None. Writes to the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    session = _details_targets['session']
    if session is None or session['closed']:
        return
    try:
        session['log_file'].write(f'{text}\n')
    except (OSError, ValueError):  # the answer is still used; only its record is lost
        pass


# ---- details_place_setter ------------------------------------------------------------
def details_place_setter(stream: Any, place: str) -> None:
    """
    ---- Summary ----
    Main function to set where the details of a problem go while no run is being
    logged: the error stream the program had before its window took the output over
    (the start-up log, or the terminal it was started from).

    ---- Inputs ----
    stream : Any
        File-like object for the details, or None for nowhere.
    place : str
        That place in words for the user, to complete "The details are in ...".

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    _details_targets (module state).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    _details_targets.update({'stream': stream, 'place': place})


# ---- details_writer ------------------------------------------------------------------
def details_writer(text: str) -> str:
    """
    ---- Summary ----
    Main function to write the details of a problem where the user does not see them:
    the log of the run being logged, or else the place set by details_place_setter.
    Never to the window, even while a thread's output is captured.

    ---- Inputs ----
    text : str
        The details, for example Python's own report of an error.

    ---- Globals read ----
    _details_targets (module state).

    ---- Outputs ----
    str
        Where they were written, in words for the user; empty when they could not be
        written anywhere.

    ---- Globals mutated ----
    None. Writes to the log or the stream (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    session = _details_targets['session']
    if session is not None and not session['closed']:
        target = session['log_file']
        place = (f"the log file {session['log_path'].name} (in the logs folder of the "
                 f'results folder)'
                 )
    else:
        target, place = _details_targets['stream'], _details_targets['place']
    if target is None:
        return ''
    try:
        target.write(text if text.endswith('\n') else f'{text}\n')
        target.flush()
    except (OSError, ValueError):  # a full disk or a closed stream: the sentence stays
        return ''
    return place


# ---- logging_starter -----------------------------------------------------------------
def logging_starter(export_root: Path, title: str, data_folder: Path) -> dict:
    """
    ---- Summary ----
    Main function to start copying everything printed to a timestamped log file, as
    soon as the results folder is known, so the questions and their answers are kept
    even when Portimao is closed before the run.

    ---- Inputs ----
    export_root : Path
        Results folder; the log goes to <export_root>/logs/YYYY_MM_DD-HH_MM_SS.log.
    title : str
        Program name, branch and version (program_title_builder), written on the first
        line of the log.
    data_folder : Path
        Folder of the .paf files, written at the top of the log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Session dictionary {log_path, log_file, original_stdout, original_stderr,
        tee_stdout, tee_stderr, closed}, to be passed to settings_logger and
        logging_stopper.

    ---- Globals mutated ----
    _details_targets (module state), so the details of a problem and the answers go to
    this log. Creates the log folder and file, writes the title, seed and folders to
    its first lines, replaces sys.stdout and sys.stderr with copying streams and prints
    the log location (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Prepare the log file ------------------------------------------------------
    export_root = Path(export_root)
    log_folder = export_root / 'logs'
    log_folder.mkdir(parents=True, exist_ok=True)
    log_path = log_folder / f'{datetime.now():%Y_%m_%d-%H_%M_%S}.log'
    log_file = log_path.open('w', encoding='utf-8', buffering=1)
    log_file.write(f'{title}\n')
    log_file.write('Random seed: none (the program does not use random numbers)\n')
    log_file.write(f'Data folder: {data_folder}\n')
    log_file.write(f'Results folder: {export_root}\n\n')
    session = {'log_path': log_path,
               'log_file': log_file,
               'original_stdout': sys.stdout,
               'original_stderr': sys.stderr,
               'closed': False,
               }

    # ---- 2 Redirect the output streams -----------------------------------------------
    session['tee_stdout'] = _Tee(sys.stdout, log_file)
    session['tee_stderr'] = _Tee(sys.stderr, log_file)
    sys.stdout, sys.stderr = session['tee_stdout'], session['tee_stderr']
    _details_targets['session'] = session
    print(f'Logging output to: {log_path.relative_to(export_root)}')
    return session


# ---- logging_stopper -----------------------------------------------------------------
def logging_stopper(session: Optional[dict]) -> None:
    """
    ---- Summary ----
    Main function to restore the console streams and close the log file.

    ---- Inputs ----
    session : Optional[dict]
        Session dictionary from logging_starter, or None.

    ---- Globals read ----
    _details_targets (module state).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    _details_targets (module state), so the details of a problem no longer go to this
    log. Restores sys.stdout and sys.stderr, closes the log file and marks the session
    closed (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the session ---------------------------------------------------------
    if session is None or session['closed']:
        return

    # ---- 2 Flush the files and restore the streams -----------------------------------
    if _details_targets['session'] is session:
        _details_targets['session'] = None
    try:
        session['tee_stdout'].flush()
        session['tee_stderr'].flush()
    finally:
        # Only restore streams we installed ourselves.
        if sys.stdout is session['tee_stdout']:
            sys.stdout = session['original_stdout']
        if sys.stderr is session['tee_stderr']:
            sys.stderr = session['original_stderr']
        try:
            session['log_file'].flush()
        finally:
            session['log_file'].close()
            session['closed'] = True


# ---- settings_logger -----------------------------------------------------------------
def settings_logger(session: Optional[dict], settings: dict) -> None:
    """
    ---- Summary ----
    Main function to write every setting of the run to its log, once all the questions
    are answered and before anything is processed. The window does not show them.

    ---- Inputs ----
    session : Optional[dict]
        Session dictionary from logging_starter, or None.
    settings : dict
        The answers of the run, by name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. Settings that cannot be written (a full disk) are left out.

    ---- Globals mutated ----
    None. Writes to the log (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if session is None or session['closed']:
        return
    lines = ['', 'Settings:']
    lines += [f'  {key}: {json.dumps(value, default=str)}'
              for key, value in sorted(settings.items())
              ]
    try:
        session['log_file'].write('\n'.join(lines) + '\n\n')
    except (OSError, ValueError):  # the run still goes ahead; only the record is lost
        pass
