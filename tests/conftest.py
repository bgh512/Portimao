"""
Makes the program's folders importable from the tests, however pytest is started,
keeps every window shut while the tests run, and names the font file that fails when a
figure cannot be drawn.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

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


# ---- _glyph_fault_lister -------------------------------------------------------------
def _glyph_fault_lister(text: str, families: Sequence[str]) -> str:
    """
    ---- Summary ----
    Helper function to say which font file fails on which character of a text, for
    the message of a test whose figure could not be drawn: each character is loaded
    from the first of the fonts that has it, as the plotting library does.

    ---- Inputs ----
    text : str
        The text that was drawn.
    families : Sequence[str]
        The font names the figure named, in their order.

    ---- Globals read ----
    None. Reads the font files (side effect).

    ---- Outputs ----
    str
        One line per font named with its file, then one per character that failed
        ('U+208B in <file>: <what the font reader said>') or that no font has.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # the plotting library is imported here, after pytest_configure chose its backend
    from matplotlib import font_manager
    from matplotlib.backends.backend_agg import get_hinting_flag
    from matplotlib.ft2font import FT2Font

    # ---- 1 Open the fonts named ------------------------------------------------------
    lines, fonts = [], []
    for family in families:
        try:
            path = font_manager.findfont(family, fallback_to_default=False)
        except ValueError:
            lines.append(f'{family}: not on this computer')
            continue
        lines.append(f'{family}: {path}')
        try:
            fonts.append((path, FT2Font(path)))
        except (OSError, RuntimeError) as error:
            lines.append(f'{path} cannot be opened: {error}')

    # ---- 2 Load each character from the first font that has it -----------------------
    for character in sorted(set(text)):
        code = f'U+{ord(character):04X}'
        holders = [(path, font)
                   for path, font in fonts
                   if font.get_char_index(ord(character))
                   ]
        if not holders:
            lines.append(f'{code} is in none of these fonts')
            continue
        path, font = holders[0]
        try:
            font.load_char(ord(character), flags=get_hinting_flag())
        except RuntimeError as error:
            lines.append(f'{code} in {path}: {error}')
    return '\n'.join(lines)


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


# ---- glyph_fault_lister --------------------------------------------------------------
@pytest.fixture
def glyph_fault_lister() -> Callable[[str, Sequence[str]], str]:
    """Main function to give a test the font file that fails. See _glyph_fault_lister."""

    return _glyph_fault_lister


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
