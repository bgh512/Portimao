"""
Tests of the parts of the window that need no window: the widths a journal allows, the
check of a typed height, the check of values meant for the strip, the answers shown in
the strip and taken back from it, the cells and rows of the OD and labels tables and
the sentence said when one is confirmed too early, the way a turn of the mouse wheel
scrolls, the time axis title of a preview and which files the window keeps read and
redraws.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from types import SimpleNamespace

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_preview as viewer_preview
from utils_shared.survey import (event_entries_builder,
                                 event_asker,
                                 IGNORE_LABEL,
                                 tidy_labels_finder,
                                 )
from utils_viewer.viewer_preview import (_loaded_experiment_getter,
                                         kept_file_lister,
                                         time_title_chooser,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_strip import (height_checker,
                                       NO_JOURNAL,
                                       size_answers_builder,
                                       strip_values_builder,
                                       strip_values_checker,
                                       width_choices_lister,
                                       )
from utils_viewer.viewer_table import (ABOVE_ZERO,
                                       cell_reader,
                                       EMPTY,
                                       label_entries_reader,
                                       label_table_builder,
                                       LABEL,
                                       od_rows_reader,
                                       od_table_builder,
                                       table_problem_teller,
                                       wheel_step_finder,
                                       ZERO_OR_MORE,
                                       )


# ---- CONSTANTS -----------------------------------------------------------------------
# Two made-up files: one with three events, one with none.
SUMMARIES = [{'name': 'kd_run1',
              'events': [{'datapoint': 10, 'time': 15.0, 'text': '100uM KCN'},
                         {'datapoint': 20, 'time': 20.5, 'text': 'nd-011992'},
                         {'datapoint': 30, 'time': 31.25, 'text': 'bubble'},
                         ],
              },
             {'name': 'kd_run2', 'events': []},
             ]


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_cells_of_the_tables --------------------------------------------------------
def test_cells_of_the_tables() -> None:
    """
    ---- Summary ----
    Main function to check the three kinds of cell: a number above 0 (with a point or
    a comma), a number of 0 or more, and a label without its outer spaces; an empty
    cell is "not filled in" and never wrong; words, numbers below the limit and
    numbers that are not finite are wrong.

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

    # ---- 1 A number above 0 (the OD table) -------------------------------------------
    assert cell_reader('1.2') == (pytest.approx(1.2), True)
    assert cell_reader(' 50 ', ABOVE_ZERO) == (pytest.approx(50.0), True)
    assert cell_reader('0,8') == (pytest.approx(0.8), True)
    assert cell_reader('') == (None, True)
    assert cell_reader('   ') == (None, True)
    for wrong in ('abc', '0', '-1', '1.2.3', 'nan', 'inf'):
        assert cell_reader(wrong) == (None, False)

    # ---- 2 A number of 0 or more (a concentration) -----------------------------------
    assert cell_reader('0', ZERO_OR_MORE) == (pytest.approx(0.0), True)
    assert cell_reader('2,5', ZERO_OR_MORE) == (pytest.approx(2.5), True)
    assert cell_reader('', ZERO_OR_MORE) == (None, True)
    for wrong in ('8mM', '-0.1', 'nan'):
        assert cell_reader(wrong, ZERO_OR_MORE) == (None, False)

    # ---- 3 A label -------------------------------------------------------------------
    assert cell_reader('  10 µM KCN ', LABEL) == ('10 µM KCN', True)
    assert cell_reader('0', LABEL) == ('0', True)
    assert cell_reader(' ', LABEL) == (None, True)


# ---- test_event_labels_from_the_table ------------------------------------------------
def test_event_labels_from_the_table(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the labels as the table is confirmed: a label written
    ignore in any capitals leaves its event out and drops its concentration; a label
    that could be tidier is offered once, and one kept as it is is not offered again.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the answer box.

    ---- Globals read ----
    SUMMARIES (module constant).

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

    # ---- 1 Confirm the table: one tidy form offered and taken ------------------------
    typed = ['y']
    monkeypatch.setattr('utils_shared.questions._input_reader',
                        lambda text, indent='': typed.pop(0),
                        )
    def table_filler(entries: dict) -> dict:
        filled = {name: [dict(entry) for entry in events]
                  for name, events in entries.items()
                  }
        filled['kd_run1'][1].update(label=' Ignore ', concentration_uM=5.0)
        filled['kd_run1'][2].update(label='2 mM azide', concentration_uM=2000.0)
        return filled
    kept: set = set()
    result = event_asker(SUMMARIES, {}, table_filler, kept)
    first, second, third = result['kd_run1']
    assert (first['label'], first['ignored']) == ('100 µM KCN', False)
    assert second == {'datapoint': 20,
                      'label': IGNORE_LABEL,
                      'concentration_uM': None,
                      'ignored': True,
                      }
    assert (third['label'], third['concentration_uM']) == ('2 mM azide', 2000.0)
    assert result['kd_run2'] == [] and not typed and not kept

    # ---- 2 A label kept as it is is not offered again --------------------------------
    typed = ['n']
    result = event_asker(SUMMARIES, {}, lambda entries: entries, kept)
    assert result['kd_run1'][0]['label'] == '100uM KCN'
    assert kept == {'100uM KCN'} and not typed
    with_events = [SUMMARIES[0]]
    assert tidy_labels_finder(with_events, result, kept) == []
    assert len(tidy_labels_finder(with_events, result, set())) == 1


# ---- test_rows_of_the_labels_table ---------------------------------------------------
def test_rows_of_the_labels_table() -> None:
    """
    ---- Summary ----
    Main function to check the labels table: it starts from the saved label, or else
    the file's own text, with ignore for an event left out; it has one row per event
    under its file's name, none for a file without events; and the typed labels and
    concentrations go back to the right events, a label left empty keeping its own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    SUMMARIES (module constant).

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

    # ---- 1 Start from the saved values or the file's text ----------------------------
    saved = {'kd_run1': {'events': [{'datapoint': 10,
                                     'label': '100 µM KCN',
                                     'concentration_uM': 100.0,
                                     'ignored': False,
                                     },
                                    {'datapoint': 30,
                                     'label': 'bubble',
                                     'concentration_uM': None,
                                     'ignored': True,
                                     },
                                    ],
                         },
             }
    entries = event_entries_builder(SUMMARIES, saved)
    assert [e['label'] for e in entries['kd_run1']] == ['100 µM KCN',
                                                        'nd-011992',
                                                        IGNORE_LABEL,
                                                        ]
    assert [e['concentration_uM'] for e in entries['kd_run1']] == [100.0, None, None]
    assert entries['kd_run2'] == []

    # ---- 2 One row per event, under its file's name ----------------------------------
    table = label_table_builder(SUMMARIES, entries, IGNORE_LABEL)
    assert table['skip_word'] == IGNORE_LABEL
    assert [(r['group'], r['first'], r['position']) for r in table['rows']] == [
        ('kd_run1', '15.00', 0),
        ('kd_run1', '20.50', 1),
        ('kd_run1', '31.25', 2),
        ]
    assert table['rows'][0]['name'] == 'kd_run1 at 15.00 min'
    assert table['rows'][0]['cells'] == {'label': '100 µM KCN',
                                         'concentration_uM': '100',
                                         }
    assert table['rows'][1]['cells']['concentration_uM'] == ''

    # ---- 3 The typed values go back to their events ----------------------------------
    values = [{'label': '200 µM KCN', 'concentration_uM': 200.0},
              {'label': None, 'concentration_uM': 1.5},
              {'label': IGNORE_LABEL, 'concentration_uM': None},
              ]
    result = label_entries_reader(table, values, entries)
    assert [e['label'] for e in result['kd_run1']] == ['200 µM KCN',
                                                       'nd-011992',
                                                       IGNORE_LABEL,
                                                       ]
    assert [e['concentration_uM'] for e in result['kd_run1']] == [200.0, 1.5, None]
    assert entries['kd_run1'][0]['label'] == '100 µM KCN'  # the start is not changed


# ---- test_rows_of_the_od_table -------------------------------------------------------
def test_rows_of_the_od_table() -> None:
    """
    ---- Summary ----
    Main function to check the OD table: one row per file named by the file, a value
    written as short as it goes and a missing one as an empty cell, and the typed
    values read back per file.

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

    rows = {'a': {'OD': 0.5, 'volume': None, 'dilution_factor': 1.0},
            'b': {'OD': None, 'volume': 2.0, 'dilution_factor': 1.0},
            }
    table = od_table_builder(rows)
    assert [(r['first'], r['name'], r['group']) for r in table['rows']] == [
        ('a', 'a', None),
        ('b', 'b', None),
        ]
    assert table['rows'][0]['cells'] == {'OD': '0.5',
                                         'volume': '',
                                         'dilution_factor': '1',
                                         }
    values = [{'OD': 0.5, 'volume': 1.5, 'dilution_factor': 1.0},
              {'OD': 0.7, 'volume': 2.0, 'dilution_factor': 2.0},
              ]
    assert od_rows_reader(table, values) == {'a': values[0], 'b': values[1]}


# ---- test_sentence_when_confirmed_too_early ------------------------------------------
def test_sentence_when_confirmed_too_early() -> None:
    """
    ---- Summary ----
    Main function to check the one sentence said when Confirm is pressed with cells
    that cannot be used (named first, with what to type) or needed cells left empty,
    naming five cells at most and counting the others, and none when the table can be
    used.

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

    assert table_problem_teller([]) is None
    problems = [('a: OD', EMPTY), ('b at 5.00 min: Concentration (µM)', ZERO_OR_MORE)]
    assert table_problem_teller(problems) == (
        'Type a number of 0 or more in these cells: b at 5.00 min: Concentration (µM).'
        )
    assert table_problem_teller([('a: OD', ABOVE_ZERO)]) == (
        'Type a number above 0 in these cells: a: OD.'
        )
    empty = [(f'{name}: OD', EMPTY) for name in 'abcdefg']
    assert table_problem_teller(empty) == (
        'Fill in these empty cells: a: OD, b: OD, c: OD, d: OD, e: OD and 2 more.'
        )


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


# ---- test_answers_shown_in_the_strip -------------------------------------------------
def test_answers_shown_in_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check that the answers of a run are shown in the strip as they
    are meant (the standard size as the journal "None", a chosen journal by its name,
    the box ticked only when the haems are worked out), that the strip can show them,
    and that its journal, width and height give the same answers back.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

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

    # ---- 1 The standard size ---------------------------------------------------------
    standard = dict(settings.DEFAULT_ANSWERS)
    values = strip_values_builder(standard, True)
    assert values == {'plot_haems': True,
                      'fit_file': settings.STANDARD_FIT,
                      'journal': NO_JOURNAL,
                      'columns': 1,
                      'height': 0.5,
                      }
    strip_values_checker(values)
    assert size_answers_builder(values) == {'journal': 'nature',
                                            'size_mode': 'default',
                                            'columns': 1,
                                            'height': 0.5,
                                            }

    # ---- 2 A chosen journal, without haems -------------------------------------------
    chosen = dict(standard,
                  journal='cell',
                  columns=1.5,
                  height=0.75,
                  size_mode='custom',
                  fit_file=None,
                  )
    values = strip_values_builder(chosen, False)
    assert values == {'plot_haems': False,
                      'fit_file': '',
                      'journal': 'cell',
                      'columns': 1.5,
                      'height': 0.75,
                      }
    strip_values_checker(values)
    assert size_answers_builder(values) == {'journal': 'cell',
                                            'size_mode': 'custom',
                                            'columns': 1.5,
                                            'height': 0.75,
                                            }

    # ---- 3 Only what changed is given back -------------------------------------------
    assert size_answers_builder({'height': 0.3}) == {'height': 0.3}
    assert size_answers_builder({'plot_haems': False, 'fit_file': 'x.csv'}) == {}


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


# ---- test_time_title_of_a_preview ----------------------------------------------------
def test_time_title_of_a_preview() -> None:
    """
    ---- Summary ----
    Main function to check that a preview's time axis says "in the recording" while
    trimming and for a file whose start is not trimmed, and "from the trimmed start"
    once a file trimmed at its start is drawn trimmed.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.PREVIEW_TIME_TITLES.

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

    recording = settings.PREVIEW_TIME_TITLES['recording']
    trimmed = settings.PREVIEW_TIME_TITLES['trimmed']
    assert time_title_chooser(True, 3.0) == recording
    assert time_title_chooser(True, None) == recording
    assert time_title_chooser(False, 3.0) == trimmed
    assert time_title_chooser(False, None) == recording
    assert time_title_chooser(False, 0.0) == recording


# ---- test_files_drawn_beside_the_one_shown -------------------------------------------
def test_files_drawn_beside_the_one_shown() -> None:
    """
    ---- Summary ----
    Main function to check which files the window keeps read and redraws after an
    answer: the file shown, then the nearest ones around the list, the next one before
    the previous one, never more than there are files.

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

    assert kept_file_lister(0, 12, 3) == [0, 1, 11]
    assert kept_file_lister(5, 12, 3) == [5, 6, 4]
    assert kept_file_lister(11, 12, 3) == [11, 0, 10]
    assert kept_file_lister(3, 12, 4) == [3, 4, 2, 5]
    assert kept_file_lister(0, 2, 3) == [0, 1]
    assert kept_file_lister(1, 2, 3) == [1, 0]
    assert kept_file_lister(0, 1, 3) == [0]
    assert kept_file_lister(0, 0, 3) == []


# ---- test_files_kept_in_memory -------------------------------------------------------
def test_files_kept_in_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check that the window keeps the three files around the one shown
    read: a file read for every file at once (as the component finder does) is let go
    without dropping them, a kept file is not read again, and moving on by one reads
    only the new neighbour. The reading of a file is stood in.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the file reader and sets the number of files kept.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The stand-ins are undone after the test.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Twelve made-up files, read by a stand-in that counts the reads ------------
    read = []
    def loader(path: Path, spectral_datasets: tuple = ()) -> dict:
        read.append(path.stem)
        return {'raw_spectra': {}}
    monkeypatch.setattr(viewer_preview, 'experiment_paf_loader', loader)
    monkeypatch.setattr(settings, 'WINDOW_KEPT_FILES', 3)
    summaries = [{'name': f'run{i}', 'path': Path(f'run{i}.paf')} for i in range(12)]
    session = ViewerSession(summaries=summaries, export_root=Path('.'), window=None)

    # ---- 2 The file shown and the ones beside it -------------------------------------
    session.current = 5
    for i in (5, 6, 4):
        _loaded_experiment_getter(session, summaries[i], None)
    assert set(session.cache) == {'run4', 'run5', 'run6'}

    # ---- 3 A far file is read and let go; the kept ones are not read again -----------
    assert _loaded_experiment_getter(session, summaries[9], None) == {'raw_spectra': {}}
    assert set(session.cache) == {'run4', 'run5', 'run6'}
    _loaded_experiment_getter(session, summaries[5], None)
    assert read == ['run5', 'run6', 'run4', 'run9']

    # ---- 4 One step on reads only the new neighbour ----------------------------------
    session.current = 6
    for i in (6, 7, 5):
        _loaded_experiment_getter(session, summaries[i], None)
    assert set(session.cache) == {'run5', 'run6', 'run7'}
    assert read == ['run5', 'run6', 'run4', 'run9', 'run7']


# ---- test_wheel_turn_on_each_system --------------------------------------------------
def test_wheel_turn_on_each_system() -> None:
    """
    ---- Summary ----
    Main function to check that a turn of the mouse wheel scrolls a table the right
    way on Windows (steps of 120), the Mac (small steps) and Linux (buttons 4 and
    5), and not at all for an event that says neither.

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

    # Tk gives "??" as the button of a wheel event on Windows and the Mac.
    assert wheel_step_finder(SimpleNamespace(num='??', delta=120)) == -1
    assert wheel_step_finder(SimpleNamespace(num='??', delta=-240)) == 1
    assert wheel_step_finder(SimpleNamespace(num='??', delta=1)) == -1
    assert wheel_step_finder(SimpleNamespace(num='??', delta=-3)) == 1
    assert wheel_step_finder(SimpleNamespace(num=4, delta=0)) == -1
    assert wheel_step_finder(SimpleNamespace(num=5, delta=0)) == 1
    assert wheel_step_finder(SimpleNamespace(num='??', delta=0)) == 0
