"""
Tests that the tests themselves open no windows on the screen (set in conftest.py).
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import subprocess
import sys

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
import pytest


# ---- CONSTANTS -----------------------------------------------------------------------
# a Python that ends with 1 when it was given a console window, 0 when it was not
CONSOLE_CHECK = ('import ctypes, sys; '
                 'sys.exit(1 if ctypes.windll.kernel32.GetConsoleWindow() else 0)'
                 )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_no_tk_window_can_open ------------------------------------------------------
def test_no_tk_window_can_open() -> None:
    """
    ---- Summary ----
    Main function to check that neither a Tk window nor a Toplevel one can open while
    the tests run.

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
    None.
    """

    tkinter = pytest.importorskip('tkinter')
    with pytest.raises(tkinter.TclError):
        tkinter.Tk()
    with pytest.raises(tkinter.TclError):
        tkinter.Toplevel()


# ---- test_plots_are_drawn_off_screen -------------------------------------------------
def test_plots_are_drawn_off_screen() -> None:
    """
    ---- Summary ----
    Main function to check that matplotlib draws the tests' plots off screen, and so
    do the Pythons the tests start.

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
    None.
    """

    assert matplotlib.get_backend().lower() == 'agg'
    started = subprocess.run([sys.executable,
                              '-c',
                              'import matplotlib; print(matplotlib.get_backend())',
                              ],
                             capture_output=True,
                             text=True,
                             )
    assert started.stdout.strip().lower() == 'agg'


# ---- test_started_programs_have_no_console_window ------------------------------------
@pytest.mark.skipif(sys.platform != 'win32',
                    reason='only Windows gives a started program a console window',
                    )
def test_started_programs_have_no_console_window() -> None:
    """
    ---- Summary ----
    Main function to check that on Windows a program a test starts, through
    subprocess.run or subprocess.Popen, gets no console window.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CONSOLE_CHECK (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert subprocess.run([sys.executable, '-c', CONSOLE_CHECK]).returncode == 0
    started = subprocess.Popen([sys.executable, '-c', CONSOLE_CHECK])
    assert started.wait(timeout=60) == 0
