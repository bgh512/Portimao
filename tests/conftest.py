"""
Makes the program's folders importable from the tests, however pytest is started, and
keeps every window shut while the tests run.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tkinter
except ImportError:  # a Python without Tk can open no window anyway
    tkinter = None

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
# on Windows a program started without this flag opens a console window of its own when
# the tests run without one (as they do when Claude runs them)
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
WINDOW_REFUSAL = 'The tests open no windows.'

# pytest reads this file before it collects the tests, so the path is set in time
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---- HiddenPopen ---------------------------------------------------------------------
class HiddenPopen(subprocess.Popen):
    """
    ---- Summary ----
    Starts a program as subprocess.Popen does, but on Windows without a console window
    of its own, so a test never puts a window on the screen.

    ---- Attributes ----
    As subprocess.Popen.

    ---- Globals read ----
    HIDDEN (module constant).

    ---- Methods ----
    __init__
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        ---- Summary ----
        Main function to start the program with the hidden flag added to any flags the
        caller gave.

        ---- Inputs ----
        *args : Any
            As subprocess.Popen.
        **kwargs : Any
            As subprocess.Popen.

        ---- Globals read ----
        HIDDEN (module constant).

        ---- Outputs ----
        None.

        ---- Globals mutated ----
        None. Starts the program (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        kwargs['creationflags'] = kwargs.get('creationflags', 0) | HIDDEN
        super().__init__(*args, **kwargs)


# ---- CONFTEST HELPERS ----------------------------------------------------------------


# ---- _window_refuser -----------------------------------------------------------------
def _window_refuser(*args: Any, **kwargs: Any) -> None:
    """
    ---- Summary ----
    Helper function to stand in for tkinter.Tk: it refuses to open a window, as Tk does
    on a computer without a screen, so the program goes on without its window.

    ---- Inputs ----
    *args : Any
        As tkinter.Tk (not used).
    **kwargs : Any
        As tkinter.Tk (not used).

    ---- Globals read ----
    WINDOW_REFUSAL (module constant).

    ---- Outputs ----
    None. Always raises tkinter.TclError.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    raise tkinter.TclError(WINDOW_REFUSAL)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- pytest_configure ----------------------------------------------------------------
def pytest_configure(config: pytest.Config) -> None:
    """
    ---- Summary ----
    Main function to keep every window shut while the tests run, set before any test
    is collected: plots are drawn off screen, no Tk window can open (a Toplevel without
    its own window asks for a Tk one, so it cannot either), and on Windows every
    program a test starts runs without a console window.

    ---- Inputs ----
    config : pytest.Config
        pytest's settings (not used).

    ---- Globals read ----
    HIDDEN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    os.environ['MPLBACKEND'], tkinter.Tk and, on Windows, subprocess.Popen, for this
    run of the tests only; the programs the tests start draw their plots off screen
    too.

    ---- Equations ----
    None.

    ---- Helpers ----
    _window_refuser
    HiddenPopen
    """

    os.environ['MPLBACKEND'] = 'Agg'
    if 'matplotlib' in sys.modules:  # a pytest plugin may have imported it already
        sys.modules['matplotlib'].use('Agg')
    if tkinter is not None:
        tkinter.Tk = _window_refuser
    if HIDDEN:
        subprocess.Popen = HiddenPopen
