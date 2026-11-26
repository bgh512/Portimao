"""
Tests the parts of the Mac app's build recipe that run anywhere: what goes inside the
app and the version written into Info.plist.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import plistlib
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from launchers.mac_app_builder import _arguments_builder, _info_plist_writer


# ---- CONSTANTS -----------------------------------------------------------------------
# a few of the keys PyInstaller writes, which must be kept
PYINSTALLER_KEYS = {'CFBundleIdentifier': 'io.github.bgh512.portimao',
                    'CFBundleExecutable': 'Portimao',
                    'CFBundleShortVersionString': '0.0.0',
                    }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _plist_maker --------------------------------------------------------------------
def _plist_maker(tmp_path: Path) -> Path:
    """
    ---- Summary ----
    Helper function to write a made-up Info.plist, as PyInstaller leaves it.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    PYINSTALLER_KEYS (module constant).

    ---- Outputs ----
    Path
        The file.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    path = tmp_path / 'Info.plist'
    with open(path, 'wb') as stream:
        plistlib.dump(PYINSTALLER_KEYS, stream)
    return path


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_app_carries_program_files --------------------------------------------------
def test_app_carries_program_files() -> None:
    """
    ---- Summary ----
    Main function to check that the app starts from the app's start (which updates it),
    and that the build puts the fits, the window's icon, the question list (which gives
    the version), the Mac report and the swap script inside the app, and the details of
    each package asked for.

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
    _arguments_builder
    """

    arguments = _arguments_builder(['numpy', 'pillow'])
    assert Path(arguments[0]).name == 'mac_app_starter.py'
    assert Path(arguments[0]).exists()
    added = [arguments[i + 1]
             for i, word in enumerate(arguments)
             if word == '--add-data'
             ]
    targets = {Path(entry.rsplit(':', 1)[0]).name: entry.rsplit(':', 1)[1]
               for entry in added
               }
    assert targets == {'fits': 'fits',
                       'journals': 'journals',
                       'layouts': 'layouts',
                       'icon.png': 'assets',
                       'QUESTION_FLOW.md': '.',
                       'mac_report.sh': 'launchers',
                       'mac_app_swapper.sh': 'launchers',
                       }
    for entry in added:
        assert Path(entry.rsplit(':', 1)[0]).exists()
    copied = [arguments[i + 1]
              for i, word in enumerate(arguments)
              if word == '--copy-metadata'
              ]
    assert copied == ['numpy', 'pillow']
    assert '--windowed' in arguments


# ---- test_plist_gets_version_and_keeps_keys ------------------------------------------
def test_plist_gets_version_and_keeps_keys(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the version and the folder reasons are written into
    Info.plist, and that PyInstaller's other keys are kept.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _info_plist_writer
    _plist_maker
    """

    path = _plist_maker(tmp_path)
    _info_plist_writer(path, '2.10.1')
    with open(path, 'rb') as stream:
        values = plistlib.load(stream)
    assert values['CFBundleShortVersionString'] == '2.10.1'
    assert values['CFBundleVersion'] == '2.10.1'
    assert values['CFBundleIdentifier'] == 'io.github.bgh512.portimao'
    assert values['CFBundleExecutable'] == 'Portimao'
    assert values['NSDocumentsFolderUsageDescription'].startswith('Portimao reads')


# ---- test_plist_refuses_unknown_version ----------------------------------------------
def test_plist_refuses_unknown_version(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a version that is not numbers and dots (the program
    gives "unknown" when it finds none) stops the build and leaves the file as it was.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    PYINSTALLER_KEYS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _info_plist_writer
    _plist_maker
    """

    path = _plist_maker(tmp_path)
    with pytest.raises(ValueError):
        _info_plist_writer(path, 'unknown')
    with open(path, 'rb') as stream:
        assert plistlib.load(stream) == PYINSTALLER_KEYS
