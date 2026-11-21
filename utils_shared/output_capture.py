"""
Per-thread capture of printed output, kept out of the terminal and the log file.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import threading
from contextlib import contextmanager
from typing import Iterator, List, Optional


# ---- CONSTANTS -----------------------------------------------------------------------
_local = threading.local()


# ---- CapturedOutput ------------------------------------------------------------------
class CapturedOutput(io.StringIO):
    """
    ---- Summary ----
    The text a thread printed while its output was captured, with the warnings among
    it also kept apart (user_notices.warning_shower), so the window can show them
    without picking them out by their words.

    ---- Attributes ----
    warnings : List[str]
        Each warning shown during the capture, without its indent, in order.

    ---- Globals read ----
    None.

    ---- Methods ----
    __init__
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self) -> None:
        """
        ---- Summary ----
        Method to start an empty capture with no warnings.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the warnings attribute on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        super().__init__()
        self.warnings: List[str] = []


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- captured_buffer_getter ----------------------------------------------------------
def captured_buffer_getter() -> Optional[CapturedOutput]:
    """
    ---- Summary ----
    Main function to give the buffer that the current thread's output is being captured
    in, if any. Output streams that support the capture check this before they write.

    ---- Inputs ----
    None.

    ---- Globals read ----
    _local (module state).

    ---- Outputs ----
    Optional[CapturedOutput]
        The buffer of the current thread, or None when its output is not captured.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return getattr(_local, 'buffer', None)


# ---- output_capturer -----------------------------------------------------------------
@contextmanager
def output_capturer() -> Iterator[CapturedOutput]:
    """
    ---- Summary ----
    Main function to capture everything the current thread prints, while other threads
    keep printing normally. Only output streams that check captured_buffer_getter honour
    it (the experiment browser window and the log copier do).

    ---- Inputs ----
    None.

    ---- Globals read ----
    _local (module state).

    ---- Outputs ----
    Iterator[CapturedOutput]
        The buffer the output is collected in; read it with getvalue(), and its
        warnings with .warnings.

    ---- Globals mutated ----
    None. Sets and clears the capture of the current thread (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    previous = getattr(_local, 'buffer', None)
    buffer = CapturedOutput()
    _local.buffer = buffer
    try:
        yield buffer
    finally:
        _local.buffer = previous
