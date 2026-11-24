"""
Tests that the edges of the trimming step move, stop and shade as worked out by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict
from unittest.mock import MagicMock

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.survey import (trim_layout_finder,
                                 trim_limits_builder,
                                 trim_minutes_builder,
                                 trim_minutes_setter,
                                 trim_pointer_reader,
                                 trim_times_finder,
                                 )
from utils_viewer.viewer_edges import (edge_hit_finder,
                                       EdgeChoice,
                                       EdgeOverlay,
                                       every_file_setter,
                                       minute_x_finder,
                                       own_value_lister,
                                       shaded_picture_maker,
                                       x_minute_finder,
                                       )
from utils_viewer.viewer_preview import TimeAxis
from utils_viewer.viewer_strip import minutes_checker


# ---- CONSTANTS -----------------------------------------------------------------------
# A made-up 60 min recording with additions at 10 and 50 min, and a 40 min one with
# additions at 5 and 30 min.
LONG = {'name': 'long',
        'duration_min': 60.0,
        'events': [{'time': 10.0}, {'time': 50.0}],
        }
SHORT = {'name': 'short',
         'duration_min': 40.0,
         'events': [{'time': 5.0}, {'time': 30.0}],
         }
NOTHING = {'trim_start': 0.0, 'trim_end': 0.0, 'ignore_start': 0.0, 'ignore_end': 0.0}
# A picture 800 x 400 pixels placed at (100, 50) in the plot area. Its panels run from
# 1/8 to 7/8 of its width (pixels 200 to 800 of the plot area) and show 0 to 60 min.
PICTURE_BOX = (100.0, 50.0, 800.0, 400.0)
TIME_AXIS = TimeAxis(left=0.125,
                     right=0.875,
                     bottom=0.25,
                     top=0.75,
                     start_min=0.0,
                     end_min=60.0,
                     )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_edge_under_the_mouse -------------------------------------------------------
def test_edge_under_the_mouse() -> None:
    """
    ---- Summary ----
    Main function to check which edge the mouse takes: by its handle in either row, by
    its line, the inner edge where two lines meet, and none away from the lines or
    below the panels.

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
    Handles from y = 10: the top row to 32, the lower row to 54; a handle is 9 px wide,
    so it is taken within 4.5 + 2 px. A line is taken within 6 px, from y = 10 to the
    bottom of the panels at 300.

    ---- Helpers ----
    None.
    """

    edges = [('trim_start', 200.0, 0),
             ('trim_end', 700.0, 0),
             ('ignore_start', 200.0, 1),
             ('ignore_end', 650.0, 1),
             ]
    panel = (60.0, 300.0)
    assert edge_hit_finder(203.0, 20.0, edges, 10.0, panel) == 'trim_start'
    assert edge_hit_finder(198.0, 40.0, edges, 10.0, panel) == 'ignore_start'
    assert edge_hit_finder(202.0, 150.0, edges, 10.0, panel) == 'ignore_start'
    assert edge_hit_finder(695.0, 150.0, edges, 10.0, panel) == 'trim_end'
    assert edge_hit_finder(400.0, 150.0, edges, 10.0, panel) is None
    assert edge_hit_finder(200.0, 320.0, edges, 10.0, panel) is None


# ---- test_every_file_or_one_file -----------------------------------------------------
def test_every_file_or_one_file() -> None:
    """
    ---- Summary ----
    Main function to check that an edge set on every file gives each file the same
    minutes within its own limits, that one set on one file leaves the others alone,
    and that the files whose minutes differ from most files are found.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG, SHORT, NOTHING (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    8 min trimmed from the start: the 60 min files keep 8, the 40 min one stops at its
    first addition, 5. Only on 'long': the others keep 0.

    ---- Helpers ----
    None.
    """

    summaries = {'long': LONG, 'short': SHORT, 'other': dict(LONG, name='other')}
    def setter(name: str,
               minutes: Dict[str, float],
               key: str,
               value: float,
               ) -> Dict[str, float]:
        return trim_minutes_setter(summaries[name], minutes, key, value)
    values = {name: dict(NOTHING) for name in summaries}
    everywhere = every_file_setter(values, list(values), 'trim_start', 8.0, setter)
    assert [everywhere[name]['trim_start'] for name in summaries] == [8.0, 5.0, 8.0]
    assert own_value_lister(everywhere) == ['short']
    alone = every_file_setter(values, ['long'], 'trim_start', 8.0, setter)
    assert [alone[name]['trim_start'] for name in summaries] == [8.0, 0.0, 0.0]
    assert values['long']['trim_start'] == 0.0
    assert own_value_lister({'long': dict(NOTHING)}) == []
    # a value one file has and the others lack is its own; a field left unmarked
    # (which window of the averaging step was dragged last) never marks a file
    assert own_value_lister({'a': {'x': 1.0},
                             'b': {'x': 1.0},
                             'c': {'x': 1.0, 'average2:window_s': 90.0},
                             },
                            ) == ['c']
    assert own_value_lister({'a': {'x': 1.0, 'picked': 1.0},
                             'b': {'x': 1.0, 'picked': 2.0},
                             'c': {'x': 1.0, 'picked': 2.0},
                             },
                            ('picked',),
                            ) == []


# ---- test_ignored_parts_stay_inside_the_kept_part ------------------------------------
def test_ignored_parts_stay_inside_the_kept_part() -> None:
    """
    ---- Summary ----
    Main function to check that the ignored parts never cross, that the one on the side
    of the edge being set gives way, and that minutes below 0 count as 0.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trimmed 4 and 6 min: 50 min kept. Ignore the first 45: allowed. Ignore the last 10:
    only 50 - 45 = 5 fit. Trim 10 from the start: 44 min kept, so the first ignored
    part gives way to 44 - 5 = 39 and the last keeps 5.

    ---- Helpers ----
    None.
    """

    minutes = dict(NOTHING, trim_start=4.0, trim_end=6.0)
    minutes = trim_minutes_setter(LONG, minutes, 'ignore_start', 45.0)
    assert minutes['ignore_start'] == pytest.approx(45.0)
    minutes = trim_minutes_setter(LONG, minutes, 'ignore_end', 10.0)
    assert (minutes['ignore_start'], minutes['ignore_end']) == pytest.approx(
        (45.0, 5.0),
        )
    minutes = trim_minutes_setter(LONG, minutes, 'trim_start', 10.0)
    assert minutes['trim_start'] == pytest.approx(10.0)
    assert (minutes['ignore_start'], minutes['ignore_end']) == pytest.approx(
        (39.0, 5.0),
        )
    assert trim_minutes_setter(LONG, minutes, 'ignore_end', -3.0)['ignore_end'] == 0.0


# ---- test_layout_of_the_edges_and_parts ----------------------------------------------
def test_layout_of_the_edges_and_parts() -> None:
    """
    ---- Summary ----
    Main function to check where the four edges sit on the whole recording, the words
    by their handles, and the parts shaded.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trimmed 4 and 5, ignored 6 and 3 on 60 min: edges at 4, 60 - 5 = 55, 4 + 6 = 10
    and 55 - 3 = 52.

    ---- Helpers ----
    None.
    """

    minutes = {'trim_start': 4.0,
               'trim_end': 5.0,
               'ignore_start': 6.0,
               'ignore_end': 3.0,
               }
    edges, parts = trim_layout_finder(LONG, minutes)
    assert [key for key, _, _, _ in edges] == ['trim_start',
                                               'trim_end',
                                               'ignore_start',
                                               'ignore_end',
                                               ]
    assert [time_min for _, time_min, _, _ in edges] == pytest.approx([4.0,
                                                                       55.0,
                                                                       10.0,
                                                                       52.0,
                                                                       ],
                                                                      )
    assert [words for _, _, words, _ in edges] == ['trimmed 4 min',
                                                   'trimmed 5 min',
                                                   'ignored 6 min',
                                                   'ignored 3 min',
                                                   ]
    assert [kind for _, _, _, kind in edges] == ['trim', 'trim', 'ignore', 'ignore']
    assert [kind for _, _, kind in parts] == ['trim', 'trim', 'ignore', 'ignore']
    assert [time_min for start, end, _ in parts for time_min in (start, end)] == (
        pytest.approx([0.0, 4.0, 55.0, 60.0, 4.0, 10.0, 52.0, 55.0]))


# ---- test_minutes_and_places_on_the_plot ---------------------------------------------
def test_minutes_and_places_on_the_plot() -> None:
    """
    ---- Summary ----
    Main function to check that a time is turned into its place across the plot area
    and back, and that a place beyond the panels gives the time at their edge.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PICTURE_BOX, TIME_AXIS (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The axis runs from x = 200 to 800 for 0 to 60 min: 30 min at x = 500, 12.3 min at
    200 + 12.3 / 60 * 600 = 323.

    ---- Helpers ----
    None.
    """

    assert minute_x_finder(30.0, PICTURE_BOX, TIME_AXIS) == pytest.approx(500.0)
    assert minute_x_finder(12.3, PICTURE_BOX, TIME_AXIS) == pytest.approx(323.0)
    assert x_minute_finder(323.0, PICTURE_BOX, TIME_AXIS) == pytest.approx(12.3)
    assert x_minute_finder(100.0, PICTURE_BOX, TIME_AXIS) == pytest.approx(0.0)
    assert x_minute_finder(900.0, PICTURE_BOX, TIME_AXIS) == pytest.approx(60.0)


# ---- test_minutes_typed_in_the_strip -------------------------------------------------
def test_minutes_typed_in_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check which numbers of minutes the boxes of the strip take.

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

    assert minutes_checker('4,5') == (4.5, '')
    assert minutes_checker(' 0 ') == (0.0, '')
    for wrong in ('', '-1', 'abc', 'nan'):
        value, note = minutes_checker(wrong)
        assert value is None
        assert note


# ---- test_minutes_to_limits_and_back -------------------------------------------------
def test_minutes_to_limits_and_back() -> None:
    """
    ---- Summary ----
    Main function to check that the starting minutes come from the limits remembered,
    or from the standard settings, kept within the file's limits, and that minutes
    turned into limits give the same minutes back.

    ---- Inputs ----
    None.

    ---- Globals read ----
    config.DEFAULT_ANSWERS (5 min ignored at the start, checked first); LONG, SHORT
    (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    'long' remembered as kept from 3 to 57 min: 3 and 60 - 57 = 3 trimmed. 'short'
    remembered with 20 min trimmed from its start: it stops at its first addition, 5.
    'other' has nothing remembered: the standard settings. Back as limits: a trim of 0
    is None, the trim end is 60 - 3 = 57.

    ---- Helpers ----
    None.
    """

    assert settings.DEFAULT_ANSWERS['ignore_first_minutes'] == 5
    other = dict(LONG, name='other')
    remembered = {'long': {'trim_start': 3.0,
                           'trim_end': 57.0,
                           'ignore_start': 2.0,
                           'ignore_end': 0.0,
                           },
                  'short': {'trim_start': 20.0,
                            'trim_end': None,
                            'ignore_start': 0.0,
                            'ignore_end': 1.0,
                            },
                  }
    minutes = trim_minutes_builder([LONG, SHORT, other], remembered)
    assert minutes['long'] == pytest.approx({'trim_start': 3.0,
                                             'trim_end': 3.0,
                                             'ignore_start': 2.0,
                                             'ignore_end': 0.0,
                                             },
                                            )
    assert minutes['short'] == pytest.approx({'trim_start': 5.0,
                                              'trim_end': 0.0,
                                              'ignore_start': 0.0,
                                              'ignore_end': 1.0,
                                              },
                                             )
    assert minutes['other'] == pytest.approx(dict(NOTHING, ignore_start=5.0))
    limits = trim_limits_builder([LONG, SHORT, other], minutes)
    assert limits['long'] == pytest.approx({'trim_start': 3.0,
                                            'trim_end': 57.0,
                                            'ignore_start': 2.0,
                                            'ignore_end': 0.0,
                                            },
                                           )
    assert limits['other']['trim_start'] is None
    assert limits['other']['trim_end'] is None
    back = trim_minutes_builder([LONG, SHORT, other], limits)
    for name, own in minutes.items():
        assert back[name] == pytest.approx(own)


# ---- test_pointer_gives_the_minutes_of_each_edge -------------------------------------
def test_pointer_gives_the_minutes_of_each_edge() -> None:
    """
    ---- Summary ----
    Main function to check that a time pointed at on the whole recording gives the
    minutes that put each edge there, in steps of 0.1 min, and 0 beyond the edge.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG, NOTHING (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trimmed 4 and 5 min of 60. Trim start at 4.04 -> 4.0. Trim end at 55 -> 60 - 55 =
    5. Ignore start at 9.5 -> 9.5 - 4 = 5.5. Ignore end at 50 -> 55 - 50 = 5. Ignore
    start at 2, in the trimmed part: 0. Trim end at 61, past the end: 0.

    ---- Helpers ----
    None.
    """

    minutes = dict(NOTHING, trim_start=4.0, trim_end=5.0)
    assert trim_pointer_reader(LONG, minutes, 'trim_start', 4.04) == pytest.approx(4.0)
    assert trim_pointer_reader(LONG, minutes, 'trim_end', 55.0) == pytest.approx(5.0)
    assert trim_pointer_reader(LONG, minutes, 'ignore_start', 9.5) == pytest.approx(5.5)
    assert trim_pointer_reader(LONG, minutes, 'ignore_end', 50.0) == pytest.approx(5.0)
    assert trim_pointer_reader(LONG, minutes, 'ignore_start', 2.0) == 0.0
    assert trim_pointer_reader(LONG, minutes, 'trim_end', 61.0) == 0.0


# ---- test_full_times_in_the_boxes ----------------------------------------------------
def test_full_times_in_the_boxes() -> None:
    """
    ---- Summary ----
    Main function to check that the Trim / Ignore boxes show the four edges as times
    on the whole recording, that a time typed in a box puts the edge at that time, and
    that with "Apply to all" ticked the other files take the same minutes from their
    own start or end. The window is stood in for.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG, SHORT, NOTHING (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    60 min trimmed 4 and 5 min, ignored 5 and 2 min: trim before 4, after 60 - 5 = 55,
    ignore before 4 + 5 = 9, after 55 - 2 = 53. Trim after typed as 52: 60 - 52 = 8
    min off the end, so the 40 min file is trimmed after 40 - 8 = 32 min.

    ---- Helpers ----
    None.
    """

    # ---- 1 The times shown, and read back --------------------------------------------
    minutes = {'trim_start': 4.0,
               'trim_end': 5.0,
               'ignore_start': 5.0,
               'ignore_end': 2.0,
               }
    shown = trim_times_finder(LONG, minutes)
    assert shown == pytest.approx({'trim_start': 4.0,
                                   'trim_end': 55.0,
                                   'ignore_start': 9.0,
                                   'ignore_end': 53.0,
                                   },
                                  )
    for key, time_min in shown.items():
        assert trim_pointer_reader(LONG, minutes, key, time_min) == pytest.approx(
            minutes[key],
            )

    # ---- 2 A time typed in a box, on every file --------------------------------------
    by_name = {'long': LONG, 'short': SHORT}
    choice = EdgeChoice(fields=[('trim_start', 'Trim before'),
                                ('trim_end', 'after'),
                                ('ignore_start', 'Ignore before'),
                                ('ignore_end', 'after'),
                                ],
                        values={'long': dict(NOTHING), 'short': dict(NOTHING)},
                        layout_finder=lambda name, own: trim_layout_finder(by_name[name], own),
                        pointer_reader=lambda name, own, key, time_min: (
                            trim_pointer_reader(by_name[name], own, key, time_min)),
                        value_setter=lambda name, own, key, value: (
                            trim_minutes_setter(by_name[name], own, key, value)),
                        shown_maker=lambda name, own: trim_times_finder(by_name[name],
                                                                        own,
                                                                        ),
                        typed_reader=lambda name, own, key, time_min: (
                            trim_pointer_reader(by_name[name], own, key, time_min)),
                        )
    overlay = EdgeOverlay(MagicMock(), MagicMock(), 'Courier', lambda: None)
    overlay.choice_setter(choice)
    overlay._name = 'long'  # the file shown, as the window places it
    overlay.all_files_copier()  # "Apply to all" ticked
    overlay.field_setter('trim_end', 52.0)
    assert overlay.values['long']['trim_end'] == pytest.approx(8.0)
    assert overlay.shown_values_reader('long')['trim_end'] == pytest.approx(52.0)
    assert overlay.shown_values_reader('short')['trim_end'] == pytest.approx(32.0)
    assert overlay.shown_values_reader('nothing') is None


# ---- test_apply_to_all_copies_once ---------------------------------------------------
def test_apply_to_all_copies_once() -> None:
    """
    ---- Summary ----
    Main function to check "Apply to all": it starts unticked, so a change moves the
    file shown only; ticking it copies the four edges of the file shown to the other
    file once, and while that file is shown a change moves both; showing the other
    file unticks it (and tells the window), so that file then changes alone. The
    window is stood in for.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG, SHORT, NOTHING, PICTURE_BOX, TIME_AXIS (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The 60 min file trimmed 4 and 5 min, ignored 5 and 2 min. Copied to the 40 min
    file (additions at 5 and 30 min) the same minutes from its own start and end: its
    kept part runs from 4 to 40 - 5 = 35 min, which keeps both additions. Trim before
    typed as 3 on the 60 min file while ticked: 3 min on both. Trim before typed as 2
    on the 40 min file once it is shown: 2 min there, the 60 min file stays at 3.

    ---- Helpers ----
    None.
    """

    # ---- 1 Unticked at the start: the file shown only --------------------------------
    by_name = {'long': LONG, 'short': SHORT}
    trimmed = {'trim_start': 4.0,
               'trim_end': 5.0,
               'ignore_start': 5.0,
               'ignore_end': 2.0,
               }
    choice = EdgeChoice(fields=[('trim_start', 'Trim before'),
                                ('trim_end', 'after'),
                                ('ignore_start', 'Ignore before'),
                                ('ignore_end', 'after'),
                                ],
                        values={'long': dict(trimmed), 'short': dict(NOTHING)},
                        layout_finder=lambda name, own: trim_layout_finder(by_name[name], own),
                        pointer_reader=lambda name, own, key, time_min: (
                            trim_pointer_reader(by_name[name], own, key, time_min)),
                        value_setter=lambda name, own, key, value: (
                            trim_minutes_setter(by_name[name], own, key, value)),
                        )
    unticked = []
    overlay = EdgeOverlay(MagicMock(),
                          MagicMock(),
                          'Courier',
                          lambda: None,
                          on_untick=lambda: unticked.append(True),
                          )
    overlay.choice_setter(choice)
    assert overlay.is_every_file is False
    picture = Image.new('RGB', (800, 400), (255, 255, 255))
    overlay.picture_placer('long', picture, 1, PICTURE_BOX, TIME_AXIS)
    overlay.field_setter('trim_end', 6.0)
    assert overlay.values['long']['trim_end'] == pytest.approx(6.0)
    assert overlay.values['short'] == pytest.approx(NOTHING)
    overlay.field_setter('trim_end', 5.0)

    # ---- 2 Ticked: copied once, and changes go to every file -------------------------
    overlay.all_files_copier()
    assert overlay.is_every_file is True
    assert overlay.values['short'] == pytest.approx(trimmed)
    assert overlay.values['long'] == pytest.approx(trimmed)
    overlay.picture_placer('long', picture, 1, PICTURE_BOX, TIME_AXIS)  # redrawn
    assert overlay.is_every_file is True and unticked == []
    overlay.field_setter('trim_start', 3.0)
    assert overlay.values['long']['trim_start'] == pytest.approx(3.0)
    assert overlay.values['short']['trim_start'] == pytest.approx(3.0)

    # ---- 3 Another file shown: unticked, that file changes alone ---------------------
    overlay.picture_placer('short', picture, 1, PICTURE_BOX, TIME_AXIS)
    assert overlay.is_every_file is False and unticked == [True]
    overlay.field_setter('trim_start', 2.0)
    assert overlay.values['short']['trim_start'] == pytest.approx(2.0)
    assert overlay.values['long']['trim_start'] == pytest.approx(3.0)


# ---- test_shaded_picture -------------------------------------------------------------
def test_shaded_picture() -> None:
    """
    ---- Summary ----
    Main function to check that an ignored part is see-through grey on a white
    picture, that the rest of the picture is untouched, and that a part narrower than
    a pixel is left out.

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
    Grey #8c8c8c = (140, 140, 140) at 22 % (56 of 255) over white:
    255 - (255 - 140) * 56 / 255 = 229.75, so (230, 230, 230).

    ---- Helpers ----
    None.
    """

    white = Image.new('RGB', (20, 10), (255, 255, 255))
    shaded = shaded_picture_maker(white, [(5.0, 15.0, 0.0, 10.0, 'ignore')])
    assert shaded.size == (20, 10)
    assert shaded.getpixel((2, 5)) == (255, 255, 255)
    assert shaded.getpixel((10, 5)) == pytest.approx((230, 230, 230), abs=1)
    narrow = shaded_picture_maker(white, [(5.0, 5.5, 0.0, 10.0, 'trim')])
    assert list(narrow.getdata()) == list(white.getdata())


# ---- test_trimmed_edges_stop_at_the_events -------------------------------------------
def test_trimmed_edges_stop_at_the_events() -> None:
    """
    ---- Summary ----
    Main function to check that a trimmed edge never cuts off an addition.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LONG, NOTHING (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Additions at 10 and 50 of 60 min: at most 10 min trimmed from the start and 60 - 50
    = 10 from the end.

    ---- Helpers ----
    None.
    """

    start = trim_minutes_setter(LONG, dict(NOTHING), 'trim_start', 12.0)
    assert start['trim_start'] == pytest.approx(10.0)
    end = trim_minutes_setter(LONG, dict(NOTHING), 'trim_end', 15.0)
    assert end['trim_end'] == pytest.approx(10.0)
    assert trim_minutes_setter(LONG, dict(NOTHING), 'trim_end', 7.5)['trim_end'] == 7.5
