"""
Tests of the one rule that cleans every file name the program writes.
"""

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import file_name_sanitiser


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_dots_and_spaces_at_the_ends_go ---------------------------------------------
def test_dots_and_spaces_at_the_ends_go() -> None:
    """
    ---- Summary ----
    Main function to check that dots and spaces at either end of a name are taken off,
    and that those inside it stay.

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

    assert file_name_sanitiser('.hidden fit') == 'hidden fit'
    assert file_name_sanitiser(' run 1. ') == 'run 1'
    assert file_name_sanitiser('pca 3 components 500.5-630nm') == ('pca 3 components '
                                                                   '500.5-630nm'
                                                                   )


# ---- test_forbidden_characters_become_underscores ------------------------------------
def test_forbidden_characters_become_underscores() -> None:
    """
    ---- Summary ----
    Main function to check that each character a file name cannot hold on Windows, Mac
    or Linux becomes an underscore, and that other characters (µ, brackets) stay.

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

    assert file_name_sanitiser('a<b>c:d"e/f\\g|h?i*j') == 'a_b_c_d_e_f_g_h_i_j'
    assert file_name_sanitiser('KCN 5 µM (run 2)') == 'KCN 5 µM (run 2)'


# ---- test_nothing_left_gives_the_default ---------------------------------------------
def test_nothing_left_gives_the_default() -> None:
    """
    ---- Summary ----
    Main function to check that a name with nothing left after cleaning gives the
    default, which may be empty so the caller can ask again.

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

    assert file_name_sanitiser(' . ') == 'experiment'
    assert file_name_sanitiser('..', default='') == ''
