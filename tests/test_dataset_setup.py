"""
Tests of the dataset set-up table, without the window: the filling in from the file names, the replicate numbers, the colours, the fill of several rows, the sets, the saving and reading back, and the step that shows the table.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_stages as viewer_stages
from utils_shared.dataset_settings import (dataset_settings_reader,
                                           dataset_settings_saver,
                                           SETTINGS_FILE_NAME,
                                           )
from utils_shared.dataset_setup import (column_filler,
                                        file_name_reader,
                                        group_colours_filler,
                                        labels_lister,
                                        replicates_numberer,
                                        saved_setup_reader,
                                        sets_lister,
                                        setup_builder,
                                        setup_plainer,
                                        )
from utils_viewer.viewer_setup import group_heading_writer


# ---- CONSTANTS -----------------------------------------------------------------------
FIRST, SECOND, THIRD = settings.GROUP_COLOURS[:3]


# ---- HELPERS -------------------------------------------------------------------------


# ---- _row_maker ----------------------------------------------------------------------
def _row_maker(name: str,
               group_1: str = '',
               group_2: str = '',
               time_point: str = '',
               run: object = None,
               use: bool = True,
               ) -> dict:
    """
    ---- Summary ----
    Helper function to make one row of a set-up table.

    ---- Inputs ----
    name : str
        The experiment name.
    group_1 : str
        Its Group 1 label.
    group_2 : str
        Its Group 2 label.
    time_point : str
        Its time point.
    run : object
        Its run number, or None.
    use : bool
        Whether it is in use.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The row (dataset_setup, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {'name': name,
            'use': use,
            'group_1': group_1,
            'group_2': group_2,
            'time_point': time_point,
            'run': run,
            }


# ---- TESTS ---------------------------------------------------------------------------


# ---- test_file_names_read ------------------------------------------------------------
@pytest.mark.parametrize(('name', 'read'),
                         [('control-bd_then_kcn-run2',
                           ('control', 'BD → KCN', '', 2),
                           ),
                          ('knockdown-kcn_then_bd-run3',
                           ('knockdown', 'KCN → BD', '', 3),
                           ),
                          ('control_kcn_then_bd_run1',
                           ('control', 'KCN → BD', '', 1),
                           ),
                          ('control_7hours', ('control', '', '7 h', None)),
                          ('knockdown_24hours', ('knockdown', '', '24 h', None)),
                          ('knockdown_0hours', ('knockdown', '', '0 h', None)),
                          ('control-bd_then_kcn-24h-run1',
                           ('control', 'BD → KCN', '24 h', 1),
                           ),
                          ('wt_1', ('wt', '', '', 1)),
                          ('WT_8umlDAP_2', ('WT', '8umlDAP', '', 2)),
                          ('example', ('example', '', '', None)),
                          ('7.5 hrs', ('', '', '7.5 h', None)),
                          ],
                         )
def test_file_names_read(name: str, read: tuple) -> None:
    """
    ---- Summary ----
    Main function to check what a file name gives the set-up table: run<N> or a lone
    number at its end is the run number, a number of hours the time point ('7 h'),
    and what is left is split at a hyphen, else at the first underscore, into Group
    1 and Group 2; an addition order is written with its arrow.

    ---- Inputs ----
    name : str
        The file name without .paf.
    read : tuple
        (Group 1, Group 2, time point, run number) worked out by hand.

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

    assert file_name_reader(name) == read


# ---- test_the_table_from_the_file_names ----------------------------------------------
def test_the_table_from_the_file_names() -> None:
    """
    ---- Summary ----
    Main function to check the table of a dataset never set up: one row per file in
    the order given, every row in use, a label spelt as it was first seen whatever
    its case (wt, then WT read as wt), the group columns unnamed, and the first
    colour of the list for the one Group 1 label.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIRST.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _row_maker
    """

    setup = setup_builder(['wt_1', 'WT_8umlDAP_2'])
    assert setup == {'group_names': ['', ''],
                     'colours': {'wt': FIRST},
                     'rows': [_row_maker('wt_1', 'wt', run=1),
                              _row_maker('WT_8umlDAP_2', 'wt', '8umlDAP', run=2),
                              ],
                     }


# ---- test_the_table_as_it_was_saved --------------------------------------------------
def test_the_table_as_it_was_saved() -> None:
    """
    ---- Summary ----
    Main function to check the table of a dataset set up before: a file saved keeps
    its cells and its tick, whatever its name says; a file new to the folder is
    filled in from its name and spelt as the saved label (Control, not control); the
    group names and the colour picked come back, and the new label takes the first
    colour not taken.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIRST, SECOND.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _row_maker
    """

    saved = {'group_names': ['strain', ''],
             'colours': {'Control': SECOND},
             'files': {'control_7hours': {'use': False,
                                          'group_1': 'Control',
                                          'group_2': 'typed',
                                          'time_point': 'day 1',
                                          },
                       'gone_file': {'use': True,
                                     'group_1': 'old',
                                     'group_2': '',
                                     'time_point': '',
                                     },
                       },
             }
    setup = setup_builder(['control_7hours', 'control_24hours', 'knockdown_7hours'],
                          saved,
                          )
    assert setup['group_names'] == ['strain', '']
    assert setup['rows'] == [_row_maker('control_7hours',
                                        'Control',
                                        'typed',
                                        'day 1',
                                        use=False,
                                        ),
                             _row_maker('control_24hours', 'Control', '', '24 h'),
                             _row_maker('knockdown_7hours', 'knockdown', '', '7 h'),
                             ]
    assert setup['colours'] == {'Control': SECOND, 'knockdown': FIRST}


# ---- test_the_replicates_numbered ----------------------------------------------------
def test_the_replicates_numbered() -> None:
    """
    ---- Summary ----
    Main function to check the replicate numbers, worked out by hand. The three
    control rows with the same labels count by run number, not by place (runs 3, 1,
    2 are replicates 3, 1, 2); a row of the set with no run number comes after
    them (4); a row with another time point starts again at 1; a row not in use has
    no number and does not take one; rows with no run number count in the order of
    the table.

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
    _row_maker
    """

    rows = [_row_maker('a', 'control', 'x', '', run=3),
            _row_maker('b', 'control', 'x', '', run=1),
            _row_maker('c', 'control', 'x', '', run=2),
            _row_maker('d', 'control', 'x', ''),
            _row_maker('e', 'control', 'x', '24 h', run=2),
            _row_maker('f', 'knockdown', 'x', '', run=1, use=False),
            _row_maker('g', 'knockdown', 'x', '', run=2),
            _row_maker('h'),
            _row_maker('i'),
            ]
    assert replicates_numberer(rows) == [3, 1, 2, 4, 1, None, 1, 1, 2]
    assert replicates_numberer([]) == []


# ---- test_a_colour_per_group_1_label -------------------------------------------------
def test_a_colour_per_group_1_label() -> None:
    """
    ---- Summary ----
    Main function to check the colours of the Group 1 labels: the labels take the
    colours of the list in the order first seen; a label keeps the colour it has; a
    new label takes the first colour no label has (the second is taken, so the
    first, then the third); a label no longer in the table loses its colour, and a
    blank cell has none; with more labels than colours the list starts again.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIRST, SECOND, THIRD.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _row_maker
    """

    rows = [_row_maker('a', 'control'),
            _row_maker('b', 'knockdown'),
            _row_maker('c', 'control'),
            _row_maker('d'),
            _row_maker('e', 'mutant'),
            ]
    assert group_colours_filler(rows, {}) == {'control': FIRST,
                                              'knockdown': SECOND,
                                              'mutant': THIRD,
                                              }
    kept = group_colours_filler(rows, {'knockdown': SECOND, 'gone': FIRST})
    assert kept == {'control': FIRST, 'knockdown': SECOND, 'mutant': THIRD}
    assert list(kept) == ['control', 'knockdown', 'mutant']
    picked = group_colours_filler(rows, {'control': THIRD})
    assert picked == {'control': THIRD, 'knockdown': FIRST, 'mutant': SECOND}

    count = len(settings.GROUP_COLOURS)
    many = [_row_maker(f'file{place}', f'label{place}') for place in range(count + 2)]
    colours = group_colours_filler(many, {})
    assert list(colours.values())[:count] == list(settings.GROUP_COLOURS)
    assert colours[f'label{count}'] == settings.GROUP_COLOURS[0]
    assert colours[f'label{count + 1}'] == settings.GROUP_COLOURS[1]


# ---- test_several_rows_filled --------------------------------------------------------
def test_several_rows_filled() -> None:
    """
    ---- Summary ----
    Main function to check the fill of a Shift-click: every row from the cell
    clicked first to the one Shift-clicked gets the label of the first, down the
    table and up it, in that column only; the rows given are not changed; a column
    that holds no labels and a row the table does not have are refused.

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
    _row_maker
    """

    rows = [_row_maker('a', 'one', 'p'),
            _row_maker('b', 'two', 'q'),
            _row_maker('c', 'three', 'r'),
            _row_maker('d', 'four', 's'),
            ]
    down = column_filler(rows, 'group_1', 1, 3)
    assert [row['group_1'] for row in down] == ['one', 'two', 'two', 'two']
    assert [row['group_2'] for row in down] == ['p', 'q', 'r', 's']
    up = column_filler(rows, 'group_2', 2, 0)
    assert [row['group_2'] for row in up] == ['r', 'r', 'r', 's']
    assert [row['group_1'] for row in rows] == ['one', 'two', 'three', 'four']
    with pytest.raises(ValueError):
        column_filler(rows, 'use', 0, 1)
    with pytest.raises(ValueError):
        column_filler(rows, 'group_1', 0, 4)


# ---- test_the_labels_and_the_sets ----------------------------------------------------
def test_the_labels_and_the_sets() -> None:
    """
    ---- Summary ----
    Main function to check the labels a cell offers and the sets under the table.
    The labels of a column are listed once each, in the order first seen, blank
    cells left out. The sets are the rows in use with the same three labels: two
    control rows with BD → KCN (n = 2), one control row at 24 h, one row with no
    label at all ('no labels', no colour); the knockdown row not in use is in no
    set.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIRST.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _row_maker
    """

    rows = [_row_maker('a', 'control', 'BD → KCN'),
            _row_maker('b', 'control', 'BD → KCN'),
            _row_maker('c', 'control', 'BD → KCN', '24 h'),
            _row_maker('d', 'knockdown', 'BD → KCN', use=False),
            _row_maker('e'),
            ]
    assert labels_lister(rows, 'group_1') == ['control', 'knockdown']
    assert labels_lister(rows, 'time_point') == ['24 h']
    assert sets_lister(rows, {'control': FIRST}) == [
        {'name': 'control · BD → KCN', 'n': 2, 'colour': FIRST},
        {'name': 'control · BD → KCN · 24 h', 'n': 1, 'colour': FIRST},
        {'name': 'no labels', 'n': 1, 'colour': None},
        ]
    assert sets_lister([], {}) == []


# ---- test_the_setup_saved_and_read_back ----------------------------------------------
def test_the_setup_saved_and_read_back(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the set-up is kept with the dataset: what is saved
    holds the group names, the colours of the labels in the table and the cells of
    each file (not its run number, read from the name each time), with a file saved
    before and not in this run kept; read back from the settings file and built
    again, the table is the one saved.

    ---- Inputs ----
    tmp_path : Path
        The dataset folder for the test.

    ---- Globals read ----
    FIRST, SECOND, THIRD.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    names = ['control-bd_then_kcn-run1', 'knockdown-bd_then_kcn-run1']
    setup = setup_builder(names)
    setup['group_names'] = ['strain', 'order of additions']
    setup['rows'][1]['use'] = False
    setup['rows'][0]['time_point'] = 'day 2'
    # the colour picked for control; knockdown keeps the second of the list
    setup['colours']['control'] = THIRD
    setup['colours']['gone'] = FIRST
    remembered = {'files': {'other_file': {'use': True,
                                           'group_1': 'old',
                                           'group_2': '',
                                           'time_point': '',
                                           },
                            },
                  }
    plain = setup_plainer(setup, remembered)
    assert plain == {'group_names': ['strain', 'order of additions'],
                     'colours': {'control': THIRD, 'knockdown': SECOND},
                     'files': {'other_file': remembered['files']['other_file'],
                               names[0]: {'use': True,
                                          'group_1': 'control',
                                          'group_2': 'BD → KCN',
                                          'time_point': 'day 2',
                                          },
                               names[1]: {'use': False,
                                          'group_1': 'knockdown',
                                          'group_2': 'BD → KCN',
                                          'time_point': '',
                                          },
                               },
                     }

    assert dataset_settings_saver(tmp_path,{}, {}, plain)
    read = dataset_settings_reader(tmp_path)['setup']
    assert read == plain
    again = setup_builder(names, read)
    assert again['group_names'] == setup['group_names']
    assert again['rows'] == setup['rows']
    assert again['colours'] == {'control': THIRD, 'knockdown': SECOND}


# ---- test_a_settings_file_without_a_usable_setup -------------------------------------
def test_a_settings_file_without_a_usable_setup(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a settings file never stops the dataset opening: a
    file written before the set-up was kept reads as no set-up, and none is written
    when there is none; of a set-up changed by hand only the parts of the right
    form are kept (a colour that is not '#rrggbb' and a file that is not a table
    are dropped, a missing cell is blank, a missing tick is in use, one group name
    becomes two).

    ---- Inputs ----
    tmp_path : Path
        The dataset folder for the test.

    ---- Globals read ----
    SETTINGS_FILE_NAME (imported).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert dataset_settings_saver(tmp_path,{}, {})
    written = json.loads((tmp_path / SETTINGS_FILE_NAME).read_text('utf-8'))
    assert 'setup' not in written
    assert dataset_settings_reader(tmp_path)['setup'] == {}
    assert saved_setup_reader(None) == {}
    assert saved_setup_reader(['a']) == {}

    odd = {'group_names': [' strain '],
           'colours': {'control': '#0072B2', 'knockdown': 'red', 'mutant': 3},
           'files': {'a': {'group_1': ' control ', 'time_point': 7},
                     'b': 'not a table',
                     'c': {'use': False, 'group_2': 'x'},
                     },
           }
    assert saved_setup_reader(odd) == {'group_names': ['strain', ''],
                                       'colours': {'control': '#0072b2'},
                                       'files': {'a': {'use': True,
                                                       'group_1': 'control',
                                                       'group_2': '',
                                                       'time_point': '',
                                                       },
                                                 'c': {'use': False,
                                                       'group_1': '',
                                                       'group_2': 'x',
                                                       'time_point': '',
                                                       },
                                                 },
                                       }


# ---- test_the_headings_of_the_group_columns ------------------------------------------
def test_the_headings_of_the_group_columns() -> None:
    """
    ---- Summary ----
    Main function to check the heading of a group column: its number, with the name
    typed for it in brackets, and its number alone when it is left unnamed.

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

    assert group_heading_writer(0, 'strain') == 'Group 1 (strain)'
    assert group_heading_writer(1, ' order of additions ') == (
        'Group 2 (order of additions)')
    assert group_heading_writer(0, '') == 'Group 1'
    assert group_heading_writer(1, '   ') == 'Group 2'


# ---- test_the_step_that_shows_the_table ----------------------------------------------
def test_the_step_that_shows_the_table(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the Dataset set-up step: it starts its step of the guide,
    shows the table built from the file names and what was saved, asks 6.1 and gives
    the table the window holds once Continue is clicked; without a window it gives
    the table as built and asks nothing. The window and the question are stood in
    for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for the stand-ins.

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

    names = ['control_7hours', 'knockdown_7hours']
    built = setup_builder(names)
    filled = dict(built, group_names=['strain', ''])
    done: List[tuple] = []

    class FakeWindow:
        def setup_shower(self, setup: dict) -> None:
            done.append(('shown', setup))

        def setup_hider(self) -> dict:
            done.append(('hidden',))
            return filled

    def waiter(question: str, nudge: str, number: str) -> str:
        done.append(('asked', number))
        return ''

    monkeypatch.setattr(viewer_stages,
                        'guide_step_starter',
                        lambda key: done.append(('step', key)),
                        )
    monkeypatch.setattr(viewer_stages, 'info_printer', lambda *args, **kwargs: None)
    monkeypatch.setattr(viewer_stages, 'enter_waiter', waiter)
    monkeypatch.setattr(viewer_stages, 'active_gui_getter', lambda: FakeWindow())
    assert viewer_stages.setup_stage_runner(names) == filled
    assert done == [('step', 'setup'),
                    ('shown', built),
                    ('asked', '6.1'),
                    ('hidden',),
                    ]
    done.clear()
    monkeypatch.setattr(viewer_stages, 'active_gui_getter', lambda: None)
    assert viewer_stages.setup_stage_runner(names, {}) == built
    assert done == [('step', 'setup')]
