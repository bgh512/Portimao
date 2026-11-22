"""
Tests that the edges of the oxidised and reduced regions start, move, stop, are copied
to the other files and are shaded as worked out by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.redox_regions import (region_edge_copier,
                                        region_edge_setter,
                                        region_edges_builder,
                                        region_layout_finder,
                                        region_pointer_reader,
                                        region_span_reader,
                                        )
from utils_viewer.viewer_edges import every_file_setter, shaded_picture_maker


# ---- CONSTANTS -----------------------------------------------------------------------
# A made-up run whose used part goes from 5 to 55 min; a region needs 0.5 min.
USED_SPAN = (5.0, 55.0)
MINIMUM_MIN = 0.5
PARKED = {'oxidised_start': 5.0,
          'oxidised_end': 5.0,
          'reduced_start': 55.0,
          'reduced_end': 55.0,
          }
# Three made-up files: the additions of 'one' and 'two' as in the to-do's example (the
# 3rd at 20 and at 22 min), and 'few' with two additions only.
ADDITIONS = {'one': [10.0, 15.0, 20.0],
             'two': [11.0, 16.0, 22.0],
             'few': [9.0, 14.0],
             }


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _edge_setter --------------------------------------------------------------------
def _edge_setter(values: Dict[str, float], key: str, value: float) -> Dict[str, float]:
    """
    Helper function to set one edge with the limits of the made-up run. See
    region_edge_setter.
    """

    return region_edge_setter(values, key, value, USED_SPAN, MINIMUM_MIN)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_copy_to_every_file_or_one_file ---------------------------------------------
def test_copy_to_every_file_or_one_file() -> None:
    """
    ---- Summary ----
    Main function to check that an edge set on every file is set on the file shown
    first and copied to the others by their additions, that a file with fewer
    additions keeps what it had, and that an edge set on one file leaves the others
    alone.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS, PARKED (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Oxidised end set to 18.5 on 'one': 1.5 min before its 3rd addition (20). 'two':
    22 - 1.5 = 20.5. 'few' has no 3rd addition: it keeps 5. Typed as 70 on 'one': it
    stops at 55, which is 35 min after its 3rd addition; 'two' gets 22 + 35 = 57,
    stopped at 55.

    ---- Helpers ----
    _edge_setter
    """

    def setter(name: str,
               values: Dict[str, float],
               key: str,
               value: float,
               ) -> Dict[str, float]:
        return _edge_setter(values, key, value)
    def copier(shown: str, name: str, key: str, value: float) -> Optional[float]:
        return region_edge_copier(value, ADDITIONS[shown], ADDITIONS[name])
    values = {name: dict(PARKED) for name in ADDITIONS}
    names = list(values)
    everywhere = every_file_setter(values,
                                   names,
                                   'oxidised_end',
                                   18.5,
                                   setter,
                                   shown='one',
                                   copier=copier,
                                   )
    assert [everywhere[name]['oxidised_end'] for name in names] == pytest.approx(
        [18.5, 20.5, 5.0],
        )
    assert everywhere['few'] == PARKED
    beyond = every_file_setter(values,
                               names,
                               'oxidised_end',
                               70.0,
                               setter,
                               shown='one',
                               copier=copier,
                               )
    assert [beyond[name]['oxidised_end'] for name in names] == pytest.approx(
        [55.0, 55.0, 5.0],
        )
    alone = every_file_setter(values,
                              ['two'],
                              'oxidised_end',
                              18.5,
                              setter,
                              shown='two',
                              copier=copier,
                              )
    assert [alone[name]['oxidised_end'] for name in names] == pytest.approx(
        [5.0, 18.5, 5.0],
        )
    assert values['one'] == PARKED


# ---- test_edge_copied_by_its_nearest_addition ----------------------------------------
def test_edge_copied_by_its_nearest_addition() -> None:
    """
    ---- Summary ----
    Main function to check the time an edge is copied to in another file: the same
    distance from the addition of the same number, from the first addition for an edge
    before it, and not at all to a file with fewer additions or from a file with none.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ADDITIONS (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    18.5 on 'one' is 1.5 before its 3rd addition (20): 22 - 1.5 = 20.5 on 'two'. 7 on
    'one' is 3 before its 1st (10): 11 - 3 = 8 on 'two', 9 - 3 = 6 on 'few'. 12 on
    'one' is 2 after its 1st: 9 + 2 = 11 on 'few'.

    ---- Helpers ----
    None.
    """

    one, two, few = ADDITIONS['one'], ADDITIONS['two'], ADDITIONS['few']
    assert region_edge_copier(18.5, one, two) == pytest.approx(20.5)
    assert region_edge_copier(7.0, one, two) == pytest.approx(8.0)
    assert region_edge_copier(7.0, one, few) == pytest.approx(6.0)
    assert region_edge_copier(12.0, one, few) == pytest.approx(11.0)
    assert region_edge_copier(18.5, one, few) is None
    assert region_edge_copier(18.5, [], two) is None


# ---- test_edges_stay_in_the_used_part ------------------------------------------------
def test_edges_stay_in_the_used_part() -> None:
    """
    ---- Summary ----
    Main function to check that a region is pulled out from its side, that an edge
    stops at the ends of the used part, and that an edge moved past the other edge of
    its region pushes it along.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PARKED (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Used part 5 to 55. Oxidised end to 12: 5 to 12. Reduced start to 40: 40 to 55.
    Oxidised end to 2: stops at 5, so 5 to 5. Reduced end to 70: stops at 55. Oxidised
    start to 20 with the end at 12: the end is pushed to 20. Reduced end to 30 with
    the start at 40: the start is pushed to 30.

    ---- Helpers ----
    _edge_setter
    """

    values = _edge_setter(PARKED, 'oxidised_end', 12.0)
    assert (values['oxidised_start'], values['oxidised_end']) == (5.0, 12.0)
    values = _edge_setter(values, 'reduced_start', 40.0)
    assert (values['reduced_start'], values['reduced_end']) == (40.0, 55.0)
    assert PARKED['oxidised_end'] == 5.0
    low = _edge_setter(values, 'oxidised_end', 2.0)
    assert (low['oxidised_start'], low['oxidised_end']) == (5.0, 5.0)
    assert _edge_setter(values, 'reduced_end', 70.0)['reduced_end'] == 55.0
    pushed = _edge_setter(values, 'oxidised_start', 20.0)
    assert (pushed['oxidised_start'], pushed['oxidised_end']) == (20.0, 20.0)
    pushed = _edge_setter(values, 'reduced_end', 30.0)
    assert (pushed['reduced_start'], pushed['reduced_end']) == (30.0, 30.0)


# ---- test_layout_of_the_regions ------------------------------------------------------
def test_layout_of_the_regions() -> None:
    """
    ---- Summary ----
    Main function to check the handles, their words and the shading: one handle
    reading "not chosen" and no shading for a region not chosen, two edges and one
    shaded part for a chosen one, and a region shorter than the least length drawn as
    not chosen.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PARKED, MINIMUM_MIN (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Least length 0.5 min: 5 to 12.25 is chosen, 54.6 to 55 (0.4 min) is not, 54.5 to
    55 (0.5 min) is.

    ---- Helpers ----
    None.
    """

    edges, parts = region_layout_finder(PARKED, MINIMUM_MIN)
    assert edges == [('oxidised_end', 5.0, 'oxidised: not chosen', 'oxidised'),
                     ('reduced_start', 55.0, 'reduced: not chosen', 'reduced'),
                     ]
    assert parts == []
    values = dict(PARKED, oxidised_end=12.25, reduced_start=54.6)
    edges, parts = region_layout_finder(values, MINIMUM_MIN)
    assert edges == [('oxidised_start', 5.0, '', 'oxidised'),
                     ('oxidised_end', 12.25, 'oxidised 5 to 12.25 min', 'oxidised'),
                     ('reduced_start', 54.6, 'reduced: not chosen', 'reduced'),
                     ]
    assert parts == [(5.0, 12.25, 'oxidised')]
    edges, parts = region_layout_finder(dict(values, reduced_start=54.5), MINIMUM_MIN)
    assert edges[2:] == [('reduced_start', 54.5, 'reduced 54.5 to 55 min', 'reduced'),
                         ('reduced_end', 55.0, '', 'reduced'),
                         ]
    assert parts == [(5.0, 12.25, 'oxidised'), (54.5, 55.0, 'reduced')]


# ---- test_pointer_gives_the_time_in_steps --------------------------------------------
def test_pointer_gives_the_time_in_steps() -> None:
    """
    ---- Summary ----
    Main function to check that a time pointed at gives the edge in steps of 0.1 min.

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
    12.34 -> 12.3; 12.36 -> 12.4.

    ---- Helpers ----
    None.
    """

    assert region_pointer_reader(12.34) == pytest.approx(12.3)
    assert region_pointer_reader(12.36) == pytest.approx(12.4)


# ---- test_regions_a_file_ends_with ---------------------------------------------------
def test_regions_a_file_ends_with() -> None:
    """
    ---- Summary ----
    Main function to check the regions read from the edges: none for a file left as it
    started, one alone (which the program counts as none) and both.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PARKED, MINIMUM_MIN (module constants).

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

    assert region_span_reader(PARKED, MINIMUM_MIN) == {'oxidised': None,
                                                       'reduced': None,
                                                       }
    one = dict(PARKED, oxidised_end=12.0)
    assert region_span_reader(one, MINIMUM_MIN) == {'oxidised': (5.0, 12.0),
                                                    'reduced': None,
                                                    }
    both = dict(one, reduced_start=40.0)
    assert region_span_reader(both, MINIMUM_MIN) == {'oxidised': (5.0, 12.0),
                                                     'reduced': (40.0, 55.0),
                                                     }


# ---- test_regions_never_overlap ------------------------------------------------------
def test_regions_never_overlap() -> None:
    """
    ---- Summary ----
    Main function to check that an edge moved into the other region stops at its
    nearer side, that past its middle it comes out on the far side with the edge not
    being set giving way, and that a region not chosen is in nobody's way.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PARKED (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Reduced 20 to 30, oxidised not chosen at 5. Oxidised end to 22 (2 from 20, 8 from
    30): stops at 20, so 5 to 20. Oxidised end to 27 (7 from 20, 3 from 30): goes to
    30, and the start gives way to 30, so 30 to 30, not chosen. Oxidised end to 40:
    the reduced region would lie inside 5 to 40, so the start gives way to 30: 30 to
    40. Then the oxidised start to 10: the end gives way to 20: 10 to 20. With the
    reduced region not chosen (55 to 55), the oxidised end goes to 55.

    ---- Helpers ----
    _edge_setter
    """

    values = dict(PARKED, reduced_start=20.0, reduced_end=30.0)
    near = _edge_setter(values, 'oxidised_end', 22.0)
    assert (near['oxidised_start'], near['oxidised_end']) == (5.0, 20.0)
    far = _edge_setter(values, 'oxidised_end', 27.0)
    assert (far['oxidised_start'], far['oxidised_end']) == (30.0, 30.0)
    after = _edge_setter(values, 'oxidised_end', 40.0)
    assert (after['oxidised_start'], after['oxidised_end']) == (30.0, 40.0)
    assert (after['reduced_start'], after['reduced_end']) == (20.0, 30.0)
    before = _edge_setter(after, 'oxidised_start', 10.0)
    assert (before['oxidised_start'], before['oxidised_end']) == (10.0, 20.0)
    free = _edge_setter(PARKED, 'oxidised_end', 55.0)
    assert (free['oxidised_start'], free['oxidised_end']) == (5.0, 55.0)


# ---- test_shaded_regions -------------------------------------------------------------
def test_shaded_regions() -> None:
    """
    ---- Summary ----
    Main function to check that the oxidised region is shaded see-through red and the
    reduced one see-through blue on a white picture.

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
    At 18 % (46 of 255) over white, 255 - (255 - channel) * 46 / 255. Red #d62728 =
    (214, 39, 40): (247.6, 216.0, 216.2), so (248, 216, 216). Blue #1f77b4 = (31, 119,
    180): (214.6, 230.5, 241.5), so (215, 230, 241).

    ---- Helpers ----
    None.
    """

    white = Image.new('RGB', (40, 10), (255, 255, 255))
    shaded = shaded_picture_maker(white,
                                  [(5.0, 15.0, 0.0, 10.0, 'oxidised'),
                                   (25.0, 35.0, 0.0, 10.0, 'reduced'),
                                   ],
                                  )
    assert shaded.getpixel((20, 5)) == (255, 255, 255)
    assert shaded.getpixel((10, 5)) == pytest.approx((248, 216, 216), abs=1)
    assert shaded.getpixel((30, 5)) == pytest.approx((215, 230, 241), abs=1)


# ---- test_starting_edges -------------------------------------------------------------
def test_starting_edges() -> None:
    """
    ---- Summary ----
    Main function to check the edges a file starts with: both regions not chosen at
    the sides of the used part, or the regions remembered, kept within the used part,
    one that no longer fits being not chosen again.

    ---- Inputs ----
    None.

    ---- Globals read ----
    USED_SPAN, MINIMUM_MIN, PARKED (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Remembered oxidised 2 to 12 and reduced 56 to 60, used part 5 to 55: the oxidised
    region becomes 5 to 12; the reduced one becomes 55 to 55, so it is parked at 55.

    ---- Helpers ----
    None.
    """

    assert region_edges_builder(USED_SPAN, None, MINIMUM_MIN) == PARKED
    remembered = {'oxidised_start': 2.0,
                  'oxidised_end': 12.0,
                  'reduced_start': 56.0,
                  'reduced_end': 60.0,
                  }
    assert region_edges_builder(USED_SPAN, remembered, MINIMUM_MIN) == {
        'oxidised_start': 5.0,
        'oxidised_end': 12.0,
        'reduced_start': 55.0,
        'reduced_end': 55.0,
        }
