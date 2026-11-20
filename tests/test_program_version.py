"""
Tests that the program finds its version on dev and on main, where the release leaves .style/ out.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import program_version_reader


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_version_from_style_folder --------------------------------------------------
def test_version_from_style_folder(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a folder with .style/VERSION (dev) takes its version
    from there, even when the question list carries another one.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, standing in for the program folder.

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

    (tmp_path / '.style').mkdir()
    (tmp_path / '.style' / 'VERSION').write_text('2.7\n', encoding='utf-8')
    (tmp_path / 'QUESTION_FLOW.md').write_text('# Portimao question flow (V2.6)\n',
                                               encoding='utf-8',
                                               )
    assert program_version_reader(tmp_path) == '2.7'


# ---- test_version_from_question_flow -------------------------------------------------
def test_version_from_question_flow(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a folder without .style/ (main, the user download)
    takes its version from the title of QUESTION_FLOW.md.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, standing in for the program folder.

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

    (tmp_path / 'QUESTION_FLOW.md').write_text('# Portimao question flow (V2.10)\n\n'
                                               'Every question (V9.9) in order.\n',
                                               encoding='utf-8',
                                               )
    assert program_version_reader(tmp_path) == '2.10'


# ---- test_version_unknown_without_either_file ----------------------------------------
def test_version_unknown_without_either_file(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a folder with neither file, or with a question list
    whose title has no version, gives "unknown" instead of stopping the program.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest, standing in for the program folder.

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

    assert program_version_reader(tmp_path) == 'unknown'
    (tmp_path / 'QUESTION_FLOW.md').write_text('# Portimao question flow\n',
                                               encoding='utf-8',
                                               )
    assert program_version_reader(tmp_path) == 'unknown'
