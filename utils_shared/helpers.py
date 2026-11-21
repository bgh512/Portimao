"""
Small, generic utilities shared by several modules.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.figure import Figure


# ---- CONSTANTS -----------------------------------------------------------------------
_figure_capture: Optional[Callable[[Figure, str], None]] = None
# written where the user gave no concentration
MISSING_CONCENTRATION = '? µM'
# the version at the end of a title, as the release writes it: "... (V2.7)"
VERSION_TITLE_PATTERN = re.compile(r'\(V(\d+(?:\.\d+)*)\)\s*$')
# why a git copy could not update itself, from the launcher (launchers/bootstrap.pyw)
UPDATE_NOTE_SWITCH = 'PORTIMAO_UPDATE_NOTE'
ZIP_NOTE = ('This copy was downloaded as a zip, so it does not update itself: for '
            'updates, {}.')
ZIP_FIXES = {'darwin': 'install the Portimao app (README, section 1.1)',
             'other': 'install Portimao with git (README, section 1.2)',
             }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- concentration_formatter ---------------------------------------------------------
def concentration_formatter(concentration_um: Any) -> str:
    """
    ---- Summary ----
    Main function to write a concentration given in micromolar with the most readable
    unit: M from 1 000 000 µM, mM from 1000 µM and µM below that. It is the one place
    where a concentration is turned into text.

    ---- Inputs ----
    concentration_um : Any
        Concentration in micromolar (µM); anything float() accepts, or None when the
        user gave none.

    ---- Globals read ----
    MISSING_CONCENTRATION (module constant).

    ---- Outputs ----
    str
        For example '2 µM', '2 mM' (from 2000 µM) or '1.5 mM'; the unit is written
        with the micro sign. MISSING_CONCENTRATION ('? µM') for None. Raises ValueError
        or TypeError if the value is neither None nor a number.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mM = uM / 1000; M = uM / 1 000 000.

    ---- Helpers ----
    None.
    """

    # ---- 1 Choose the unit -----------------------------------------------------------
    if concentration_um is None:
        return MISSING_CONCENTRATION
    value = float(concentration_um)
    if abs(value) >= 1_000_000:
        return f'{value / 1_000_000:g} M'
    if abs(value) >= 1000:
        return f'{value / 1000:g} mM'
    return f'{value:g} µM'


# ---- excel_sheet_namer ---------------------------------------------------------------
def excel_sheet_namer(name: Any, used: set) -> str:
    """
    ---- Summary ----
    Main function to make a valid, unique Excel sheet name (at most 31 characters, no
    special characters).

    ---- Inputs ----
    name : Any
        Proposed sheet name (converted with str).
    used : set
        Lower-cased sheet names already taken; the new name is added to it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Sheet name, with a numeric suffix when the name is already taken.

    ---- Globals mutated ----
    None. Adds the lower-cased result to ``used`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    base = re.sub(r'[\[\]:*?/\\]', '_', str(name)).strip("'") or 'Data'
    base = base[:31]
    candidate, counter = base, 2
    while candidate.lower() in used:
        suffix = f'_{counter}'
        candidate = base[:31 - len(suffix)] + suffix
        counter += 1
    used.add(candidate.lower())
    return candidate


# ---- figure_capture_setter -----------------------------------------------------------
def figure_capture_setter(capture: Optional[Callable[[Figure, str], None]]) -> None:
    """
    ---- Summary ----
    Main function to switch figure saving to preview mode (or back). While a capture
    function is set, figure_saver hands each figure to it and writes no file, so the
    experiment browser can show a figure before it is made for real.

    ---- Inputs ----
    capture : Optional[Callable[[Figure, str], None]]
        Function called with (figure, file name stem) instead of saving, or None for
        normal saving.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    Sets _figure_capture (module state).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _figure_capture
    _figure_capture = capture


# ---- figure_saver --------------------------------------------------------------------
def figure_saver(fig: Figure,
                 folder: Path,
                 stem: str,
                 formats: Sequence[str],
                 size: Tuple[float, float],
                 dpi: int,
                 tight: bool = False,
                 ) -> List[Path]:
    """
    ---- Summary ----
    Main function to save a figure in each requested format at exactly the requested
    size. The size is pinned again just before saving because interactive backends
    resize figures, and tight cropping is off unless requested.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure to save.
    folder : Path
        Output folder; created if missing (not in preview mode).
    stem : str
        File name without the extension.
    formats : Sequence[str]
        File extensions, for example ("svg", "png").
    size : Tuple[float, float]
        Width and height in inches.
    dpi : int
        Resolution in dots per inch; the saved pixel size is size x dpi.
    tight : bool
        True to crop the canvas around the artists (bbox_inches="tight").

    ---- Globals read ----
    _figure_capture (module state).

    ---- Outputs ----
    List[Path]
        Paths of the saved files, in the order of ``formats``; empty in preview mode.

    ---- Globals mutated ----
    None. Resizes the figure to ``size`` and writes the files, or in preview mode only
    hands the figure to the capture function (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Pin the size, and only show the figure in preview mode --------------------
    fig.set_size_inches(*size, forward=False)
    if _figure_capture is not None:  # preview mode: show the figure, write nothing
        _figure_capture(fig, stem)
        return []

    # ---- 2 Save every format ---------------------------------------------------------
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for extension in formats:
        path = folder / f'{stem}.{extension}'
        fig.savefig(path,
                    format=extension,
                    dpi=dpi,
                    **({'bbox_inches': 'tight'} if tight else {}),
                    )
        paths.append(path)
    return paths


# ---- file_name_sanitiser -------------------------------------------------------------
def file_name_sanitiser(name: Any, default: str = 'experiment') -> str:
    """
    ---- Summary ----
    Main function to clean a file name: the one rule every file the program names goes
    through.

    ---- Inputs ----
    name : Any
        Proposed name (converted with str).
    default : str
        Name used when nothing is left after cleaning.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        File name with the characters < > : " / backslash | ? * replaced by underscores,
        and without dots or spaces at either end (a leading dot hides a file on a Mac
        or Linux, and Windows drops a trailing one).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    cleaned = re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip('. ')
    return cleaned or default


# ---- name_simplifier -----------------------------------------------------------------
def name_simplifier(value: Any) -> str:
    """
    ---- Summary ----
    Main function to simplify a name for matching by lower-casing it and removing
    everything except letters and digits, so "Cyt $c_1$" equals "cyt c1".

    ---- Inputs ----
    value : Any
        Name (converted with str).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Lower-case letters and digits only.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return re.sub(r'[^a-z0-9]', '', str(value).lower())


# ---- program_title_builder -----------------------------------------------------------
def program_title_builder(root: Path, version: str) -> str:
    """
    ---- Summary ----
    Main function to build the name shown at the top of the terminal, in the window
    title and in the log: the program name, the git branch it was installed from (when
    the folder is a git clone) and the version.

    ---- Inputs ----
    root : Path
        Program folder.
    version : str
        Version text, from program_version_reader.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example "Portimao dev V2.7"; without a branch (a folder from a zip file)
        "Portimao V2.7".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    branch = ''
    try:
        head = (root / '.git' / 'HEAD').read_text(encoding='utf-8').strip()
        if head.startswith('ref:'):
            branch = head.rsplit('/', 1)[-1]
    except OSError:
        pass
    return ' '.join(part for part in ('Portimao', branch, f'V{version}') if part)


# ---- program_version_reader ----------------------------------------------------------
def program_version_reader(root: Path) -> str:
    """
    ---- Summary ----
    Main function to find the program's version. The release leaves `.style/` off
    main (the user download), so where `.style/VERSION` is missing the version is
    taken from the title of `QUESTION_FLOW.md`, which every release rewrites.

    ---- Inputs ----
    root : Path
        Program folder.

    ---- Globals read ----
    VERSION_TITLE_PATTERN (module constant).

    ---- Outputs ----
    str
        For example "2.7"; "unknown" when neither file gives a version.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        version = (root / '.style' / 'VERSION').read_text(encoding='utf-8').strip()
        if version:
            return version
    except OSError:
        pass
    try:
        with open(root / 'QUESTION_FLOW.md', encoding='utf-8') as flow:
            title = flow.readline()
    except OSError:
        return 'unknown'
    found = VERSION_TITLE_PATTERN.search(title)
    return found.group(1) if found else 'unknown'


# ---- update_note_finder --------------------------------------------------------------
def update_note_finder(root: Path, is_app: bool) -> str:
    """
    ---- Summary ----
    Main function to say why this copy does not update itself, to be shown beside its
    version: a copy from a zip never can; a git copy says what the launcher found when
    it tried. The Mac app updates itself, and says so in its own message when it
    cannot.

    ---- Inputs ----
    root : Path
        Program folder.
    is_app : bool
        True when running as the Mac app.

    ---- Globals read ----
    UPDATE_NOTE_SWITCH, ZIP_FIXES, ZIP_NOTE (module constants);
    os.environ['PORTIMAO_UPDATE_NOTE']; sys.platform.

    ---- Outputs ----
    str
        One sentence saying why, and what to do; empty when this copy updates itself
        (or was not started by the launcher, which alone tries).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if is_app:
        return ''
    if not (root / '.git').exists():
        return ZIP_NOTE.format(ZIP_FIXES.get(sys.platform, ZIP_FIXES['other']))
    return os.environ.get(UPDATE_NOTE_SWITCH, '').strip()
