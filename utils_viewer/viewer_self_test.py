"""
The check switch (PORTIMAO_SELF_TEST): opens the window, shows one made-up preview and
closes by itself.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import platform
import sys
import time
import traceback
from collections import OrderedDict
from datetime import datetime
from functools import partial
from importlib import metadata as package_metadata
from pathlib import Path
from typing import Callable, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.schema import TIME_COLUMN
from utils_shared.user_places import UserPlaces
from utils_viewer.viewer_gui import (active_gui_getter,
                                     GuiUnavailableError,
                                     ViewerGui,
                                     window_opener,
                                     )
from utils_viewer.viewer_preview import (PREVIEW_DPI,
                                         preview_figure_builder,
                                         PreviewSpec,
                                         ViewerSession,
                                         )


# ---- CONSTANTS -----------------------------------------------------------------------
LOG_NAME = 'self_test.log'
# The Mac check (.github/workflows/mac_check.yml) waits for this line before it takes
# its picture of the window, so the two must stay the same.
SHOWN_MARK = 'The made-up preview is on show'
DRAWN_WAIT_S = 1.0  # the window shows a picture within a few tenths of a second
SHOW_S = 6.0  # long enough for the Mac check to take its picture
CLOSE_AFTER_S = 2.0
PACKAGES = ('numpy',
            'pandas',
            'scipy',
            'matplotlib',
            'pillow',
            'openpyxl',
            'xlsxwriter',
            )
MADE_UP_NAME = 'made_up_experiment'
DURATION_MIN = 30.0
STEP_MIN = 0.05
ADDITION_TIMES_MIN = (10.0, 20.0)
OCR_LEVELS_UM_PER_MIN = (6.0, 9.0, 1.0)  # before, between and after the additions
START_O2_UM = 220.0


# ---- SELF-TEST HELPERS ---------------------------------------------------------------


# ---- _computer_describer -------------------------------------------------------------
def _computer_describer() -> List[str]:
    """
    ---- Summary ----
    Helper function to describe the computer the check runs on: Python, the system and
    its chip, Tk and the versions of the main packages.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PACKAGES (module constant).

    ---- Outputs ----
    List[str]
        One line of text per item, for the log.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Python and the system -----------------------------------------------------
    lines = [f'Python {platform.python_version()} ({sys.executable})',
             f'System: {platform.platform()}, chip {platform.machine()}',
             ]

    # ---- 2 Tk ------------------------------------------------------------------------
    try:
        import tkinter
        lines.append(f'Tk {tkinter.TkVersion:g} '
                     f"(Tcl {tkinter.Tcl().eval('info patchlevel')})",
                     )
    except Exception as exc:  # the window check that follows fails with its reason
        lines.append(f'Tk: not available ({type(exc).__name__}: {exc})')

    # ---- 3 The packages --------------------------------------------------------------
    versions = []
    for name in PACKAGES:
        try:
            versions.append(f'{name} {package_metadata.version(name)}')
        except package_metadata.PackageNotFoundError:
            versions.append(f'{name} missing')
    lines.append(f"Packages: {', '.join(versions)}")
    return lines


# ---- _made_up_experiment_builder -----------------------------------------------------
def _made_up_experiment_builder() -> Tuple[dict, dict]:
    """
    ---- Summary ----
    Helper function to build a made-up experiment as the reader would give it from a
    file, with the summary of that file.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITION_TIMES_MIN, DURATION_MIN, MADE_UP_NAME, OCR_LEVELS_UM_PER_MIN, START_O2_UM,
    STEP_MIN, TIME_COLUMN (module constants).

    ---- Outputs ----
    Tuple[dict, dict]
        (experiment, experiment_summary), as in DATA_FORMAT.md: a point every 0.05 min
        from 0 to 30 min, additions at 10 and 20 min, the OCR at 6, 9 and then
        1 uM/min, the measured O2 falling from 220 uM at that rate and the set O2 at
        220 uM. No spectra.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    O2(t_i) = O2(0) - sum over j < i of OCR(t_j) x step.

    ---- Helpers ----
    None.
    """

    # ---- 1 The traces ----------------------------------------------------------------
    times_min = np.round(np.arange(0.0, DURATION_MIN + STEP_MIN / 2.0, STEP_MIN), 6)
    first_min, second_min = ADDITION_TIMES_MIN
    ocr = np.select([times_min < first_min, times_min < second_min],
                    list(OCR_LEVELS_UM_PER_MIN[:2]),
                    OCR_LEVELS_UM_PER_MIN[2],
                    )
    o2_um = START_O2_UM - np.concatenate(([0.0], np.cumsum(ocr[:-1] * STEP_MIN)))

    # ---- 2 The additions -------------------------------------------------------------
    events, listed = [], []
    for number, time_min in enumerate(ADDITION_TIMES_MIN, start=1):
        row = int(round(time_min / STEP_MIN))
        text = f'made-up addition {number}'
        common = {'datapoint': row + 1,
                  'text': text,
                  'time': float(times_min[row]),
                  'row_index': row,
                  }
        events.append(dict(common, label=f'Addition {number}', concentration_uM=None))
        listed.append(dict(common, name=f'Event {number}'))

    # ---- 3 The experiment and its summary --------------------------------------------
    experiment = {'experiment_name': MADE_UP_NAME,
                  'metadata': {'paf_file': f'{MADE_UP_NAME}.paf',
                               'events': events,
                               'acquisition': [],
                               'notes': '',
                               },
                  'CcO2': pd.DataFrame({TIME_COLUMN: times_min,
                                        'Measured O2 (µM)': o2_um,
                                        },
                                       ),
                  'CsO2': pd.DataFrame({TIME_COLUMN: times_min,
                                        'Set O2 (µM)': np.full_like(times_min,
                                                                    START_O2_UM,
                                                                    ),
                                        },
                                       ),
                  'VoO2': pd.DataFrame({TIME_COLUMN: times_min, 'VoO2': ocr}),
                  'raw_spectra': {},
                  }
    summary = {'name': MADE_UP_NAME,
               'path': Path(f'{MADE_UP_NAME}.paf'),
               'duration_min': DURATION_MIN,
               'frames': len(times_min),
               'datasets': [],
               'events': listed,
               'traces': ['CsO2', 'CcO2', 'VoO2'],
               }
    return experiment, summary


# ---- _preview_shower -----------------------------------------------------------------
def _preview_shower(report: Callable[[str], None], log_folder: Path) -> int:
    """
    ---- Summary ----
    Helper function, run as the program of the window, to draw the made-up experiment
    with the preview code of the program and show it in the window for a few seconds.

    ---- Inputs ----
    report : Callable[[str], None]
        Writes one line to the log, the window's terminal and the real terminal.
    log_folder : Path
        The logs folder, given as the results folder of the preview (nothing is
        written to it).

    ---- Globals read ----
    settings.DEFAULT_ANSWERS; DRAWN_WAIT_S, PREVIEW_DPI, SHOW_S, SHOWN_MARK (module
    constants).

    ---- Outputs ----
    int
        0 when the preview was drawn and handed to the window, 1 otherwise (the reason
        and its traceback are reported).

    ---- Globals mutated ----
    None. Shows the picture in the window and waits (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _made_up_experiment_builder
    active_gui_getter
    preview_figure_builder
    """

    try:
        # ---- 1 Draw the made-up experiment as a preview ------------------------------
        # The experiment is put in the session's cache, so no file is read.
        window = active_gui_getter()
        experiment, summary = _made_up_experiment_builder()
        name = summary['name']
        session = ViewerSession(summaries=[summary],
                                export_root=log_folder,
                                window=window,
                                cache=OrderedDict({name: {'experiment': experiment}}),
                                )
        answers = dict(settings.DEFAULT_ANSWERS, decompose=False, plot_haems=False)
        figure, notes = preview_figure_builder(session,
                                               PreviewSpec(answers=answers,
                                                           limits={},
                                                           fit=None,
                                                           details={},
                                                           ),
                                               name,
                                               )
        if figure is None:
            report(f'Self-test failed: the made-up preview was not drawn. {notes}')
            return 1
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', dpi=PREVIEW_DPI)
        width, height = (round(inches * PREVIEW_DPI)
                         for inches in figure.get_size_inches()
                         )
        report(f'Made-up preview drawn ({width} x {height} pixels).')
        for line in notes.splitlines():
            report(f'  Note: {line}')

        # ---- 2 Show it in the window -------------------------------------------------
        window.extra_publisher('Made-up experiment (self-test)', buffer.getvalue())
        time.sleep(DRAWN_WAIT_S)
        report(f'{SHOWN_MARK}; the window closes by itself in about '
               f'{SHOW_S + CLOSE_AFTER_S:g} s.',
               )
        time.sleep(SHOW_S)
        return 0
    except Exception:  # any problem here is what the check is for: it is reported
        report('Self-test failed: the made-up preview could not be shown.\n'
               + traceback.format_exc(),
               )
        return 1


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- self_test_runner ----------------------------------------------------------------
def self_test_runner(title: str, places: UserPlaces) -> int:
    """
    ---- Summary ----
    Main function to check that the program works on this computer: it opens the
    window, shows one made-up preview, closes the window by itself after a few seconds
    and says the result. Everything is written to self_test.log in the logs folder as
    well as to the terminal.

    ---- Inputs ----
    title : str
        Program name, branch and version (program_title_builder).
    places : UserPlaces
        Where the user's things are kept (user_places_finder); the log goes to its logs
        folder, which is the program folder's logs folder when run from source.

    ---- Globals read ----
    CLOSE_AFTER_S, LOG_NAME (module constants).

    ---- Outputs ----
    int
        0 when the check passed, 1 when it failed (the reason is in the log).

    ---- Globals mutated ----
    None. Writes the log, opens and closes the window and prints (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _computer_describer
    _preview_shower
    ViewerGui
    window_opener
    """

    # ---- 1 Start the log -------------------------------------------------------------
    log_folder = places.logs_folder
    log_folder.mkdir(parents=True, exist_ok=True)
    console = sys.stdout
    with (log_folder / LOG_NAME).open('w', encoding='utf-8') as log:
        def report(text: str) -> None:
            print(text)
            if sys.stdout is not console:  # the window's terminal: copy to the real one
                console.write(text + '\n')
                console.flush()
            log.write(text + '\n')
            log.flush()

        report(f'{title}: self-test, {datetime.now():%Y-%m-%d %H:%M:%S}')
        report(f"Running {'as the Mac app' if places.is_app else 'from source'}; the "
               f"user's own folder is {places.own_folder}",
               )
        for line in _computer_describer():
            report(line)

        # ---- 2 Open the window -------------------------------------------------------
        try:
            tk, root = window_opener()
        except GuiUnavailableError as exc:
            report(f'Self-test failed: the window could not open ({exc}).')
            return 1
        report('Window opened.')

        # ---- 3 Show the made-up preview, then close ----------------------------------
        try:
            window = ViewerGui(tk,
                               root,
                               partial(_preview_shower, report, log_folder),
                               title,
                               close_after_s=CLOSE_AFTER_S,
                               )
            code = window.run()
        except Exception:  # any problem here is what the check is for: it is reported
            report('Self-test failed: the window stopped.\n' + traceback.format_exc())
            return 1
        for error in window.window_errors:
            report(f'Self-test failed: the window met an error.\n{error}')
        if window.window_errors:
            code = 1

        # ---- 4 Say the result --------------------------------------------------------
        report('Self-test passed.' if code == 0 else 'Self-test failed (see above).')
        return code
