"""
Tests that a haem's level in a region, % oxidised and an edge copied to another file
come out as worked out by hand on made-up data.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.redox_regions import (edge_anchor_finder,
                                        edge_time_finder,
                                        haem_levels_finder,
                                        percent_oxidised_calculator,
                                        region_level_finder,
                                        short_region_closer,
                                        )
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
# A made-up run of ten spectra, one a minute from 0 to 9 min, with three haems (mOD):
# bH is oxidised at first (with one spike of 30) and reduced at the end; cc has a blank
# value at 1 min; a605 never changes.
RUN = pd.DataFrame({TIME_COLUMN: np.arange(10, dtype=float),
                    SPECTRUM_INDEX_COLUMN: np.arange(1, 11),
                    'bH': [12.0, 13.0, 11.0, 12.0, 30.0, 10.0, 4.0, 5.0, 3.0, 4.0],
                    'cc': [6.0, np.nan, 6.0, 8.0, 7.0, 5.0, 2.0, 2.0, 2.0, 2.0],
                    'a605': [5.0] * 10,
                    },
                   )
OXIDISED_MIN = (0.0, 4.0)  # the oxidised region of the run: its first five spectra
REDUCED_MIN = (6.0, 9.0)  # the reduced region: its last four
# Least number of spectra in a region in these tests, small enough to work out by hand;
# the program's own is checked in test_the_least_spectra_of_the_program.
FEW = 3
# Times of the additions of three made-up files (min): the second file is run the same
# way a little later, the third has only two additions.
FIRST_FILE = [5.0, 12.0, 20.0, 30.0]
LATER_FILE = [6.0, 13.0, 22.0, 31.0]
SHORT_FILE = [5.0, 12.0]


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_level_is_the_median_in_the_region ----------------------------------------
def test_a_level_is_the_median_in_the_region() -> None:
    """
    ---- Summary ----
    Main function to check that a haem's level in a region is the median of its values
    there, with the spectra at both edges counted, so that one spike does not set it
    and a blank value is left out; and that a region with too few spectra, or one that
    ends before it starts, is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    RUN, OXIDISED_MIN, REDUCED_MIN, FEW (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Oxidised region, 0 to 4 min. bH: 12, 13, 11, 12, 30; in order 11, 12, 12, 13, 30,
    so the median is 12 (the mean, 15.6, would follow the spike). cc: 6, 6, 8, 7 (the
    blank left out); in order 6, 6, 7, 8, so the median is (6 + 7) / 2 = 6.5. a605: 5.
    Reduced region, 6 to 9 min. bH: 4, 5, 3, 4; in order 3, 4, 4, 5, so the median is
    4. cc: 2. a605: 5.
    From 1 to 3 min bH is 13, 11, 12: median 12. From 1.5 to 3.5 min only the spectra
    at 2 and 3 min are inside: two, fewer than three. From 0 to 2 min cc has only two
    values (6, 6), as the one at 1 min is blank.

    ---- Helpers ----
    None.
    """

    # ---- 1 The two regions of the run ------------------------------------------------
    oxidised = region_level_finder(RUN, *OXIDISED_MIN, minimum_points=FEW)
    assert oxidised == {'bH': 12.0, 'cc': 6.5, 'a605': 5.0}
    reduced = region_level_finder(RUN, *REDUCED_MIN, minimum_points=FEW)
    assert reduced == {'bH': 4.0, 'cc': 2.0, 'a605': 5.0}

    # ---- 2 The edges count, and too few spectra are refused --------------------------
    only_bH = RUN[[TIME_COLUMN, SPECTRUM_INDEX_COLUMN, 'bH']]
    assert region_level_finder(only_bH, 1.0, 3.0, minimum_points=FEW) == {'bH': 12.0}
    with pytest.raises(ValueError, match='holds 2 spectra with a value for bH'):
        region_level_finder(only_bH, 1.5, 3.5, minimum_points=FEW)
    with pytest.raises(ValueError, match='holds 2 spectra with a value for cc'):
        region_level_finder(RUN, 0.0, 2.0, minimum_points=FEW)

    # ---- 3 A region that cannot be used ----------------------------------------------
    with pytest.raises(ValueError, match='no start and end'):
        region_level_finder(RUN, 4.0, 0.0, minimum_points=FEW)
    with pytest.raises(ValueError, match='no start and end'):
        region_level_finder(RUN, np.nan, 4.0, minimum_points=FEW)
    with pytest.raises(ValueError, match='no haems'):
        region_level_finder(RUN[[TIME_COLUMN, SPECTRUM_INDEX_COLUMN]],
                            *OXIDISED_MIN,
                            minimum_points=FEW,
                            )


# ---- test_a_file_needs_both_regions_for_its_levels -----------------------------------
def test_a_file_needs_both_regions_for_its_levels() -> None:
    """
    ---- Summary ----
    Main function to check the two levels of every haem of a file from the regions
    kept for it: the regions are kept as times on the recording, so the trim start is
    taken off; a region is kept within the used part of the run; and a file with no
    regions, with only one, or with one that no longer holds enough spectra has no
    levels. A region too short to count is closed.

    ---- Inputs ----
    None.

    ---- Globals read ----
    RUN, OXIDISED_MIN, REDUCED_MIN, FEW (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The run was trimmed 2 min from its start, so its regions, 0 to 4 and 6 to 9 min
    on the run, are 2 to 6 and 8 to 11 min on the recording. The levels are those of
    test_a_level_is_the_median_in_the_region: bH 12 and 4, cc 6.5 and 2, a605 5 and 5.
    With the first minute ignored the used part is 1 to 9 min, and the oxidised region
    is kept to 1 to 4 min. bH: 13, 11, 12, 30; in order 11, 12, 13, 30, so the median
    is (12 + 13) / 2 = 12.5. cc: 6, 8, 7 (the blank left out), median 7.
    With the last two minutes ignored the used part ends at 7 min: the reduced region
    is kept to 6 to 7 min, two spectra, fewer than three, so the file has no levels.
    A region of 0.05 min with a least length of 0.1 min is closed at the edge that
    opens it: the end of the oxidised region, the start of the reduced one.

    ---- Helpers ----
    None.
    """

    # ---- 1 Both regions, on a run trimmed at its start -------------------------------
    regions = {'oxidised_start': 2.0,
               'oxidised_end': 6.0,
               'reduced_start': 8.0,
               'reduced_end': 11.0,
               }
    levels = haem_levels_finder(RUN, regions, 2.0, (0.0, 9.0), FEW)
    assert levels == {'oxidised': {'bH': 12.0, 'cc': 6.5, 'a605': 5.0},
                      'oxidised_region': OXIDISED_MIN,
                      'reduced': {'bH': 4.0, 'cc': 2.0, 'a605': 5.0},
                      'reduced_region': REDUCED_MIN,
                      }

    # ---- 2 A region is kept within the used part -------------------------------------
    ignored = haem_levels_finder(RUN, regions, 2.0, (1.0, 9.0), FEW)
    assert ignored['oxidised'] == {'bH': 12.5, 'cc': 7.0, 'a605': 5.0}
    assert ignored['oxidised_region'] == (1.0, 4.0)
    assert ignored['reduced'] == levels['reduced']

    # ---- 3 No regions, only one, or one with too few spectra left --------------------
    assert haem_levels_finder(RUN, None, 2.0, (0.0, 9.0), FEW) is None
    assert haem_levels_finder(RUN, {}, 2.0, (0.0, 9.0), FEW) is None
    alone = dict(regions, reduced_start=11.0)
    assert haem_levels_finder(RUN, alone, 2.0, (0.0, 9.0), FEW) is None
    assert haem_levels_finder(RUN, regions, 2.0, (0.0, 7.0), FEW) is None
    assert haem_levels_finder(RUN,
                              {'oxidised_start': 2.0},
                              2.0,
                              (0.0, 9.0),
                              FEW,
                              ) is None

    # ---- 4 A region too short to count is closed -------------------------------------
    short = {'oxidised_start': 0.0,
             'oxidised_end': 0.05,
             'reduced_start': 8.95,
             'reduced_end': 9.0,
             }
    assert short_region_closer(short, 0.1) == {'oxidised_start': 0.05,
                                               'oxidised_end': 0.05,
                                               'reduced_start': 8.95,
                                               'reduced_end': 8.95,
                                               }
    kept = {'oxidised_start': 0.0,
            'oxidised_end': 4.0,
            'reduced_start': 6.0,
            'reduced_end': 9.0,
            }
    assert short_region_closer(kept, 0.1) == kept


# ---- test_an_edge_is_copied_by_its_nearest_addition ----------------------------------
def test_an_edge_is_copied_by_its_nearest_addition() -> None:
    """
    ---- Summary ----
    Main function to check that an edge is copied to another file at the same distance
    from the addition nearest to it, counted in order; that an edge before the first
    addition goes by the first and one after the last by the last; and that a file
    with fewer additions, or with none, gives no time.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIRST_FILE, LATER_FILE, SHORT_FILE (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Additions of the first file at 5, 12, 20 and 30 min; of the later file at 6, 13,
    22 and 31 min.
    An edge at 18.5 min is 13.5, 6.5, 1.5 and 11.5 min from the four additions, so the
    third is nearest and the edge is 1.5 min before it: 20 - 1.5 = 18.5 min in the
    first file again, 22 - 1.5 = 20.5 min in the later file. The short file has no
    third addition.
    An edge at 2 min is 3 min before the first addition: 6 - 3 = 3 min in the later
    file. An edge at 33 min is 3 min after the fourth: 31 + 3 = 34 min.
    An edge at 8.5 min is 3.5 min from both the first and the second addition: the
    earlier is taken, so it is 3.5 min after the first: 6 + 3.5 = 9.5 min.

    ---- Helpers ----
    None.
    """

    # ---- 1 Between the additions -----------------------------------------------------
    anchor = edge_anchor_finder(18.5, FIRST_FILE)
    assert anchor == (2, -1.5)
    assert edge_time_finder(anchor, FIRST_FILE) == 18.5
    assert edge_time_finder(anchor, LATER_FILE) == 20.5
    assert edge_time_finder(anchor, SHORT_FILE) is None

    # ---- 2 Before the first addition and after the last ------------------------------
    before = edge_anchor_finder(2.0, FIRST_FILE)
    assert before == (0, -3.0)
    assert edge_time_finder(before, LATER_FILE) == 3.0
    after = edge_anchor_finder(33.0, FIRST_FILE)
    assert after == (3, 3.0)
    assert edge_time_finder(after, LATER_FILE) == 34.0

    # ---- 3 Halfway, out of order, and no additions -----------------------------------
    halfway = edge_anchor_finder(8.5, FIRST_FILE)
    assert halfway == (0, 3.5)
    assert edge_time_finder(halfway, LATER_FILE) == 9.5
    assert edge_anchor_finder(18.5, [30.0, 20.0, 5.0, 12.0]) == (2, -1.5)
    assert edge_time_finder(anchor, [31.0, 22.0, 13.0, 6.0]) == 20.5
    assert edge_anchor_finder(18.5, []) is None
    assert edge_anchor_finder(float('nan'), FIRST_FILE) is None
    assert edge_time_finder(anchor, []) is None


# ---- test_percent_oxidised_runs_between_the_two_levels -------------------------------
def test_percent_oxidised_runs_between_the_two_levels() -> None:
    """
    ---- Summary ----
    Main function to check that % oxidised is 100 at the oxidised level and 0 at the
    reduced one, with the right share in between; that values above 100 and below 0
    are kept; that a haem whose two levels are equal has an empty column; and that a
    haem without a level is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    RUN, OXIDISED_MIN, REDUCED_MIN, FEW (module constants); TIME_COLUMN,
    SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    percent = (D - D_red) / (D_ox - D_red) x 100, with the levels of
    test_a_level_is_the_median_in_the_region.
    bH: D_ox = 12, D_red = 4, so percent = (D - 4) / 8 x 100. D = 10 gives 6 / 8 x 100
    = 75 %; 12, 13, 11, 12, 30, 10, 4, 5, 3, 4 give 100, 112.5, 87.5, 100, 325, 75, 0,
    12.5, -12.5, 0.
    cc: D_ox = 6.5, D_red = 2, so percent = (D - 2) / 4.5 x 100. 6, blank, 6, 8, 7, 5,
    2, 2, 2, 2 give 800/9, blank, 800/9, 400/3, 1000/9, 200/3, 0, 0, 0, 0.
    a605: D_ox = D_red = 5, so there is nothing to divide by: an empty column.

    ---- Helpers ----
    None.
    """

    # ---- 1 The three haems of the run ------------------------------------------------
    oxidised = region_level_finder(RUN, *OXIDISED_MIN, minimum_points=FEW)
    reduced = region_level_finder(RUN, *REDUCED_MIN, minimum_points=FEW)
    percent = percent_oxidised_calculator(RUN, oxidised, reduced)
    assert np.allclose(percent['bH'],
                       [100.0, 112.5, 87.5, 100.0, 325.0, 75.0, 0.0, 12.5, -12.5, 0.0],
                       )
    assert np.allclose(percent['cc'],
                       [800 / 9,
                        np.nan,
                        800 / 9,
                        400 / 3,
                        1000 / 9,
                        200 / 3,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        ],
                       equal_nan=True,
                       )
    assert percent['a605'].isna().all()
    assert percent[TIME_COLUMN].equals(RUN[TIME_COLUMN])
    assert percent[SPECTRUM_INDEX_COLUMN].equals(RUN[SPECTRUM_INDEX_COLUMN])
    assert RUN['bH'].iloc[0] == 12.0  # the table given is not changed
    record = percent.attrs['percent_oxidised']
    assert record == {'oxidised_level_by_haem': {'bH': 12.0, 'cc': 6.5, 'a605': 5.0},
                      'reduced_level_by_haem': {'bH': 4.0, 'cc': 2.0, 'a605': 5.0},
                      'empty_haems': ['a605'],
                      }

    # ---- 2 The example of the notes: 12, 4 and 10 give 75 % --------------------------
    one = pd.DataFrame({TIME_COLUMN: [0.0], SPECTRUM_INDEX_COLUMN: [1], 'haem': [10.0]})
    example = percent_oxidised_calculator(one, {'haem': 12.0}, {'haem': 4.0})
    assert example['haem'].iloc[0] == 75.0

    # ---- 3 A haem without a level ----------------------------------------------------
    with pytest.raises(ValueError, match='cc: no oxidised or reduced level'):
        percent_oxidised_calculator(RUN, {'bH': 12.0, 'a605': 5.0}, reduced)


# ---- test_the_least_spectra_of_the_program -------------------------------------------
def test_the_least_spectra_of_the_program() -> None:
    """
    ---- Summary ----
    Main function to check the least number of spectra the program asks of a region:
    ten, which are 5 s of a run with a spectrum every 0.5 s; a region of nine is
    refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.REGION_MINIMUM_POINTS; TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Twenty spectra 0.5 s apart, at 0/120, 1/120, ... 19/120 min, with the values 1 to
    20. From 0 to 9/120 min there are ten, 1 to 10: median (5 + 6) / 2 = 5.5. From 0
    to 8/120 min there are nine.

    ---- Helpers ----
    None.
    """

    assert settings.REGION_MINIMUM_POINTS == 10
    run = pd.DataFrame({TIME_COLUMN: np.arange(20) / 120.0,
                        SPECTRUM_INDEX_COLUMN: np.arange(1, 21),
                        'haem': np.arange(1.0, 21.0),
                        },
                       )
    ten = region_level_finder(run,
                              0.0,
                              9 / 120.0,
                              minimum_points=settings.REGION_MINIMUM_POINTS,
                              )
    assert ten == {'haem': 5.5}
    with pytest.raises(ValueError, match='fewer than the 10 a level needs'):
        region_level_finder(run,
                            0.0,
                            8 / 120.0,
                            minimum_points=settings.REGION_MINIMUM_POINTS,
                            )
