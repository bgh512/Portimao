"""
Tests of the parts of the settings strip and the OD table that need no window: the
widths a journal allows, the check of a typed height, the check of values meant for the
strip, and the reading of one cell of the table.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_viewer.viewer_od_table import cell_reader
from utils_viewer.viewer_strip import (height_checker,
                                       NO_JOURNAL,
                                       strip_values_checker,
                                       width_choices_lister,
                                       )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_cell_of_the_od_table -------------------------------------------------------
def test_cell_of_the_od_table() -> None:
    """
    ---- Summary ----
    Main function to check that a cell gives its number (with a point or a comma), that
    an empty cell is "not filled in" and not wrong, and that words, zero, negative
    numbers and numbers that are not finite are wrong.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert cell_reader('1.2') == (pytest.approx(1.2), True)
    assert cell_reader(' 50 ') == (pytest.approx(50.0), True)
    assert cell_reader('0,8') == (pytest.approx(0.8), True)
    assert cell_reader('') == (None, True)
    assert cell_reader('   ') == (None, True)
    for wrong in ('abc', '0', '-1', '1.2.3', 'nan', 'inf'):
        assert cell_reader(wrong) == (None, False)


# ---- test_height_typed_in_the_strip --------------------------------------------------
def test_height_typed_in_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check that a height between 0 and 1 is taken and written in
    millimetres on the page of the journal, and that 0, a height over a page and words
    are refused with a reason.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A Nature page is 170 mm: 0.5 of it is 85 mm and the whole is 170 mm. A Science
    page is 230 mm: 0.25 of it is 57.5 mm. "None" uses the Nature page.

    ---- Helpers ----
    None.
    """

    assert height_checker('0.5', 'nature') == (pytest.approx(0.5), 'of a page (85 mm)')
    assert height_checker('1', 'nature') == (pytest.approx(1.0), 'of a page (170 mm)')
    assert height_checker('0,25', 'science') == (pytest.approx(0.25),
                                                 'of a page (57.5 mm)',
                                                 )
    assert height_checker('0.5', NO_JOURNAL) == (pytest.approx(0.5),
                                                 'of a page (85 mm)',
                                                 )
    for wrong in ('0', '1.2', '-0.5', 'abc', ''):
        height, reason = height_checker(wrong, 'nature')
        assert height is None
        assert 'above 0 and up to 1' in reason


# ---- test_values_meant_for_the_strip -------------------------------------------------
def test_values_meant_for_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check that values the strip can show pass, and that an unknown
    name, an unknown journal, a width the journal does not allow and a height over a
    page are each refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    strip_values_checker({'plot_haems': True,
                          'fit_file': 'made_up.csv',
                          'journal': 'cell',
                          'columns': 1.5,
                          'height': 0.75,
                          },
                         )
    strip_values_checker({'journal': NO_JOURNAL})
    strip_values_checker({})
    for wrong in ({'colour': 'red'},
                  {'journal': 'lancet'},
                  {'journal': 'nature', 'columns': 3},
                  {'height': 1.5},
                  {'height': 'tall'},
                  ):
        with pytest.raises(ValueError):
            strip_values_checker(wrong)


# ---- test_widths_of_each_journal -----------------------------------------------------
def test_widths_of_each_journal() -> None:
    """
    ---- Summary ----
    Main function to check that the widths offered are those of the journal in the
    settings, in their order and with their millimetres, and that "None" offers the
    widths of the standard journal.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Nature allows 1 column (89 mm), 1.5 columns (120 mm) and 2 columns (183 mm).

    ---- Helpers ----
    None.
    """

    assert width_choices_lister('nature') == [(1, '1 column (89 mm)'),
                                              (1.5, '1.5 columns (120 mm)'),
                                              (2, '2 columns (183 mm)'),
                                              ]
    assert width_choices_lister(NO_JOURNAL) == width_choices_lister('nature')
    for journal, spec in settings.JOURNAL_SPECS.items():
        choices = width_choices_lister(journal)
        assert [columns for columns, _ in choices] == list(spec['widths_mm'])
        for (columns, text), width_mm in zip(choices, spec['widths_mm'].values()):
            assert f'({width_mm:g} mm)' in text
    with pytest.raises(ValueError):
        width_choices_lister('lancet')
