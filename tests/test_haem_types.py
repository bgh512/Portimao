"""
Tests of the haem types read from the haem names, the order of the haems and their
colours, worked out by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from config import haem_colour_mapper
from utils_shared.helpers import haem_order_finder, haem_type_finder
from utils_shared.spectral_decomposer import fit_importer


# ---- CONSTANTS -----------------------------------------------------------------------
# the order of the haems in the Rowan fit 11-2026, with a component of no known type
FILE_ORDER = ['Cyt cc', 'Cyt b557', 'PC1', 'Cyt bH', 'Cyt bL', 'Cyt a605', 'Cyt a3']


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_fit_file_is_read_in_that_order -------------------------------------------
def test_a_fit_file_is_read_in_that_order(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file listing its haems c, b, a is read with the
    a haem first, then the b, then the c, each haem's shape moved with its name.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    path = tmp_path / 'c_b_a.csv'
    path.write_text('Cyt cc,,Cyt bH,,Cyt a605,\n'
                    '500,1e-5,505,2e-5,510,3e-5\n'
                    '520,1e-5,525,2e-5,530,3e-5\n'
                    '540,1e-5,545,2e-5,,\n',
                    )
    fit = fit_importer(path)
    assert fit['haem_list'] == ['Cyt a605', 'Cyt bH', 'Cyt cc']
    expected = np.array([[510.0, 3e-5, 505.0, 2e-5, 500.0, 1e-5],
                         [530.0, 3e-5, 525.0, 2e-5, 520.0, 1e-5],
                         [np.nan, np.nan, 545.0, 2e-5, 540.0, 1e-5],
                         ],
                        )
    assert np.array_equal(fit['data'].to_numpy(), expected, equal_nan=True)


# ---- test_haems_are_ordered_a_then_b_then_c ------------------------------------------
def test_haems_are_ordered_a_then_b_then_c() -> None:
    """
    ---- Summary ----
    Main function to check the order of the haems: every a haem, then every b, then
    every c, then a name of no known type, each type in alphabetical order (a digit
    before a letter, so a3 before a605 and b557 before bH).

    ---- Inputs ----
    None.

    ---- Globals read ----
    FILE_ORDER (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    order = haem_order_finder(FILE_ORDER)
    assert [FILE_ORDER[i] for i in order] == ['Cyt a3',
                                              'Cyt a605',
                                              'Cyt b557',
                                              'Cyt bH',
                                              'Cyt bL',
                                              'Cyt cc',
                                              'PC1',
                                              ]
    assert haem_order_finder(['Cyt $c_1$', 'Cyt $b_H$']) == [1, 0]
    assert haem_order_finder([]) == []


# ---- test_haem_types_come_from_the_name ----------------------------------------------
@pytest.mark.parametrize(('name', 'expected'),
                         [('Cyt bH', 'b'),
                          ('Cyt $b_{557}$', 'b'),
                          ('Cyt c1', 'c'),
                          ('Cyt cc', 'c'),
                          ('Cyt a605', 'a'),
                          ('Cyt $aa_3$', 'a'),
                          ('cytochrome c', 'c'),
                          ('Haem a3', 'a'),
                          ('b-like', 'b'),
                          ('c1', 'c'),
                          ('PC1', 'other'),
                          ('Cyt d', 'other'),
                          ('Cyt', 'other'),
                          ('', 'other'),
                          ],
                         )
def test_haem_types_come_from_the_name(name: str, expected: str) -> None:
    """
    ---- Summary ----
    Main function to check that a haem's type is the first letter after a leading
    'Cyt', 'cytochrome' or 'haem', and 'other' for any other name.

    ---- Inputs ----
    name : str
        Haem name, plain or in figure form.
    expected : str
        Its type, worked out by hand.

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

    assert haem_type_finder(name) == expected


# ---- test_haems_are_coloured_by_type -------------------------------------------------
def test_haems_are_coloured_by_type() -> None:
    """
    ---- Summary ----
    Main function to check the colours: the usual haems keep their own, a haem without
    one takes the first free shade of its type, two haems with the same usual colour
    get different shades, and a name of no known type a colour no haem type has.

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

    # ---- 1 The haems of the standard fit keep their own colours ----------------------
    own = settings.HAEM_COLOURS
    shades = settings.HAEM_TYPE_COLOURS
    standard = ['Cyt a605', 'Cyt b557', 'Cyt bH', 'Cyt bL', 'Cyt cc']
    assert haem_colour_mapper(standard) == {'Cyt a605': own['cyta605'],
                                            'Cyt b557': own['cytb557'],
                                            'Cyt bH': own['cytbh'],
                                            'Cyt bL': own['cytbl'],
                                            'Cyt cc': own['cytcc'],
                                            }
    assert haem_colour_mapper(['Cyt $b_H$'])['Cyt $b_H$'] == own['cytbh']

    # ---- 2 The others take a free shade of their type --------------------------------
    colours = haem_colour_mapper(['Cyt a3', 'Cyt a605', 'Cyt c1', 'Cyt c2', 'PC1'])
    assert colours == {'Cyt a3': shades['a'][1],  # a605 has the first green
                       'Cyt a605': own['cyta605'],
                       'Cyt c1': own['cytc1'],
                       'Cyt c2': shades['c'][1],  # c1 has the first red
                       'PC1': shades['other'][0],
                       }
    assert haem_colour_mapper(['Cyt a'])['Cyt a'] == shades['a'][0]

    # ---- 3 Two haems with the same usual colour get different shades -----------------
    assert own['cytc1'] == own['cytcc']
    assert haem_colour_mapper(['Cyt c1', 'Cyt cc']) == {'Cyt c1': own['cytc1'],
                                                        'Cyt cc': shades['c'][1],
                                                        }
