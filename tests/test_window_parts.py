"""
Tests of the parts of the window that need no window: the widths a journal allows, the
check of a typed height, the check of values meant for the strip, the answers shown in
the strip and taken back from it, the ways of showing the haems it offers and the
answers each kind of plot is drawn with, the cells and rows of the OD and labels tables and
the sentence said when one is confirmed too early, the way a turn of the mouse wheel
scrolls, the time axis title of a preview and which files the window keeps read and
redraws.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_preview as viewer_preview
import utils_viewer.viewer_stages as viewer_stages
from utils_shared.spectral_decomposer import OWN_HAEMS_NAME
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
from utils_viewer.viewer_stages import _answers_previewer
from utils_viewer.viewer_strip import (BACK_CHANGE,
                                       form_answers_builder,
                                       haem_form_choices_lister,
                                       haem_ticks_resolver,
                                       height_checker,
                                       kept_decomposition_builder,
                                       NO_JOURNAL,
                                       ocr_form_choices_lister,
                                       psi_answers_builder,
                                       psi_change_describer,
                                       psi_number_checker,
                                       psi_seconds_filler,
                                       psi_summary_writer,
                                       psi_values_builder,
                                       SettingsStrip,
                                       size_answers_builder,
                                       strip_values_builder,
                                       strip_values_checker,
                                       width_choices_lister,
                                       )
from utils_viewer.viewer_table import (ABOVE_ZERO,
                                       ABOVE_ZERO_OR_EMPTY,
                                       cell_reader,
                                       CHAMBER,
                                       EMPTY,
                                       label_entries_reader,
                                       label_table_builder,
                                       LABEL,
                                       od_rows_reader,
                                       od_table_builder,
                                       STOCK,
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
    Main function to check the kinds of cell: a number above 0 (with a point or a
    comma), a number of 0 or more, a label without its outer spaces, a volume added,
    a stock and a concentration in the chamber with or without their unit; an empty
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

    # ---- 4 A volume added, which may be left empty -----------------------------------
    assert cell_reader('10', ABOVE_ZERO_OR_EMPTY) == (pytest.approx(10.0), True)
    assert cell_reader('', ABOVE_ZERO_OR_EMPTY) == (None, True)
    assert cell_reader('0', ABOVE_ZERO_OR_EMPTY) == (None, False)

    # ---- 5 A stock (mM alone) and a concentration in the chamber (µM alone) ----------
    assert cell_reader('200', STOCK) == (pytest.approx(200_000.0), True)
    assert cell_reader('200 µM', STOCK) == (pytest.approx(200.0), True)
    assert cell_reader('0', STOCK) == (None, False)
    assert cell_reader('400', CHAMBER) == (pytest.approx(400.0), True)
    assert cell_reader('1.2 mM', CHAMBER) == (pytest.approx(1200.0), True)
    assert cell_reader('0', CHAMBER) == (pytest.approx(0.0), True)
    assert cell_reader('KCN', CHAMBER) == (None, False)


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
                      'stock_uM': None,
                      'added_uL': None,
                      'addition_uM': None,
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
    table = label_table_builder(SUMMARIES, entries, IGNORE_LABEL, 5.0)
    assert table['skip_word'] == IGNORE_LABEL
    assert [(r['group'], r['first'], r['position']) for r in table['rows']] == [
        ('kd_run1', '15.00', 0),
        ('kd_run1', '20.50', 1),
        ('kd_run1', '31.25', 2),
        ]
    assert table['rows'][0]['name'] == 'kd_run1 at 15.00 min'
    assert table['rows'][0]['shown'] == {'text': '100uM KCN'}
    assert table['rows'][0]['cells'] == {'label': '100 µM KCN',
                                         'stock_uM': '',
                                         'added_uL': '',
                                         'concentration_uM': '100 µM',
                                         }
    assert table['rows'][1]['cells']['concentration_uM'] == ''

    # ---- 3 The typed values go back to their events ----------------------------------
    values = [{'label': 'KCN',
               'stock_uM': 200_000.0,
               'added_uL': 10.0,
               'concentration_uM': None,
               },
              {'label': None,
               'stock_uM': None,
               'added_uL': None,
               'concentration_uM': 1.5,
               },
              {'label': IGNORE_LABEL,
               'stock_uM': None,
               'added_uL': None,
               'concentration_uM': None,
               },
              ]
    result = label_entries_reader(table, values, entries)
    assert [e['label'] for e in result['kd_run1']] == ['KCN',
                                                       'nd-011992',
                                                       IGNORE_LABEL,
                                                       ]
    assert [e['stock_uM'] for e in result['kd_run1']] == [200_000.0, None, None]
    assert [e['added_uL'] for e in result['kd_run1']] == [10.0, None, None]
    assert [e['concentration_uM'] for e in result['kd_run1']] == [None, 1.5, None]
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
    page is 199 mm: 0.5 of it is 99.5 mm. "None" uses the Nature page.

    ---- Helpers ----
    None.
    """

    assert height_checker('0.5', 'nature') == (pytest.approx(0.5), 'of a page (85 mm)')
    assert height_checker('1', 'nature') == (pytest.approx(1.0), 'of a page (170 mm)')
    assert height_checker('0,5', 'science') == (pytest.approx(0.5),
                                                'of a page (99.5 mm)',
                                                )
    assert height_checker('0.5', NO_JOURNAL) == (pytest.approx(0.5),
                                                 'of a page (85 mm)',
                                                 )
    for wrong in ('0', '1.2', '-0.5', 'abc', ''):
        height, reason = height_checker(wrong, 'nature')
        assert height is None
        assert 'above 0 and up to 1' in reason


# ---- test_the_decomposition_kept_to_compare ------------------------------------------
def test_the_decomposition_kept_to_compare() -> None:
    """
    ---- Summary ----
    Main function to check that keeping a decomposition keeps its fit as it is, the
    answers it was worked out with (the fit, the background, the spectrometer and the
    numbers of delta psi, and nothing else), a copy of the regions that later changes
    leave alone, and its name in words, for a fit file and for haems ticked under
    Build a fit, with delta psi on and off and without regions.

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

    # ---- 1 Delta psi on: the fit, the answers and a copy of the regions --------------
    fit = {'haem_list': ['bL']}
    psi_numbers = {'psi_bH_first_mV': 45.0,
                   'psi_bL_first_mV': -25.0,
                   'psi_bH_second_mV': -15.0,
                   'psi_bL_second_mV': -85.0,
                   'psi_share': 0.4,
                   'temperature_c': 30.0,
                   'psi_reduced_lowest_percent': 5.0,
                   'psi_reduced_highest_percent': 95.0,
                   }
    answers = {'fit_file': 'made_up.csv',
               'haem_files': [],
               'haem_background': 'valencia',
               'decomposition_dataset': 'Spectra',
               'journal': 'cell',
               'delta_psi': True,
               **psi_numbers,
               }
    regions = {'run1': {'oxidised_start': 1.0,
                        'oxidised_end': 3.0,
                        'reduced_start': 20.0,
                        'reduced_end': 22.0,
                        },
               }
    kept = kept_decomposition_builder(answers, fit, regions)
    assert kept['fit'] is fit
    assert kept['answers'] == {'fit_file': 'made_up.csv',
                               'haem_files': [],
                               'haem_background': 'valencia',
                               'decomposition_dataset': 'Spectra',
                               **psi_numbers,
                               }
    assert kept['text'] == ('made_up.csv with the Valencia background, its regions '
                            'and Δψ numbers'
                            )

    # ---- 2 The regions and the numbers changed later leave the kept ones alone -------
    regions['run1']['oxidised_end'] = 5.0
    answers['psi_bH_first_mV'] = 60.0
    assert kept['regions']['run1']['oxidised_end'] == 3.0
    assert kept['answers']['psi_bH_first_mV'] == 45.0

    # ---- 3 The words with delta psi off, with and without regions --------------------
    off = dict(answers, delta_psi=False)
    assert kept_decomposition_builder(off, fit, regions)['text'] == (
        'made_up.csv with the Valencia background and its regions'
        )
    assert kept_decomposition_builder(off, fit, {})['text'] == (
        'made_up.csv with the Valencia background'
        )
    assert kept_decomposition_builder(off, fit, {})['regions'] == {}
    own = dict(off,
               fit_file=OWN_HAEMS_NAME,
               haem_files=['c1_myco.csv', 'bH_bswitch.csv'],
               haem_background='rowan_scatter',
               )
    assert kept_decomposition_builder(own, fit, {})['text'] == (
        f'{OWN_HAEMS_NAME}: c1_myco, bH_bswitch with the Rowan scatter background'
        )


# ---- test_keep_to_compare_keeps_the_regions_in_use -----------------------------------
def test_keep_to_compare_keeps_the_regions_in_use(monkeypatch: pytest.MonkeyPatch,
                                                  ) -> None:
    """
    ---- Summary ----
    Main function to check that a click on Keep to compare keeps the fit, the regions
    and the numbers of delta psi in use at that moment and redraws the plot, and that
    Keep this one drops them. The showing of the strip is stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the showing of the strip.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The stand-in is undone after the test.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 A session with a fit and regions ------------------------------------------
    monkeypatch.setattr(viewer_stages, '_strip_shower', lambda session, answers: None)
    redraws = []
    session = ViewerSession(summaries=[], export_root=Path('.'), window=None)
    session.fit = {'haem_list': ['bH', 'bL']}
    session.regions = {'run1': {'oxidised_start': 1.0,
                                'oxidised_end': 3.0,
                                'reduced_start': 20.0,
                                'reduced_end': 22.0,
                                },
                       }
    session.redraw = lambda: redraws.append(True) or True
    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   decomposition_dataset='Spectra',
                   delta_psi=True,
                   psi_share=0.4,
                   )

    # ---- 2 Keep to compare -----------------------------------------------------------
    viewer_stages._strip_change_applier(session, answers, Path('.'), {'compare': True})
    assert session.kept['fit'] is session.fit
    assert session.kept['regions'] == session.regions
    assert session.kept['regions'] is not session.regions
    assert session.kept['answers']['psi_share'] == 0.4
    assert redraws == [True]

    # ---- 3 Keep this one -------------------------------------------------------------
    viewer_stages._strip_change_applier(session, answers, Path('.'), {'compare': False})
    assert session.kept is None
    assert redraws == [True, True]


# ---- test_go_back_to_kept_puts_the_kept_one_back -------------------------------------
def test_go_back_to_kept_puts_the_kept_one_back(monkeypatch: pytest.MonkeyPatch,
                                                ) -> None:
    """
    ---- Summary ----
    Main function to check the two ways of choosing after Keep to compare. Go back to
    kept puts the kept fit, background, number of delta psi and regions back in use,
    drops the kept one and redraws the plot; while the regions are being chosen on the
    plot it leaves the regions as they are; with nothing kept it does nothing. Keep
    this one leaves what is in use as it is and drops the kept one. The strip tells
    the click on Go back to kept only while one is kept. The showing of the strip is
    stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the showing of the strip.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The stand-in is undone after the test.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 A session with a fit and regions, kept to compare -------------------------
    monkeypatch.setattr(viewer_stages, '_strip_shower', lambda session, answers: None)
    redraws = []
    first_fit = {'haem_list': ['bH', 'bL']}
    first_regions = {'run1': {'oxidised_start': 1.0,
                              'oxidised_end': 3.0,
                              'reduced_start': 20.0,
                              'reduced_end': 22.0,
                              },
                     }
    session = ViewerSession(summaries=[], export_root=Path('.'), window=None)
    session.fit = first_fit
    session.regions = {name: dict(own) for name, own in first_regions.items()}
    session.redraw = lambda: redraws.append(True) or True
    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   decomposition_dataset='Spectra',
                   delta_psi=True,
                   haems=['bH', 'bL'],
                   haem_background='rowan_scatter',
                   psi_share=0.4,
                   )
    first_name = answers['fit_file']
    def changer() -> None:
        # another fit, background, number of delta psi and oxidised region
        session.fit = {'haem_list': ['bH', 'bL', 'c1']}
        session.regions['run1']['oxidised_end'] = 5.0
        answers.update({'fit_file': 'made_up.csv',
                        'haem_background': 'valencia',
                        'psi_share': 0.6,
                        },
                       )
    viewer_stages._strip_change_applier(session, answers, Path('.'), {'compare': True})
    changer()

    # ---- 2 Go back to kept -----------------------------------------------------------
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {BACK_CHANGE: True},
                                        )
    assert session.fit is first_fit
    assert session.regions == first_regions
    assert answers['fit_file'] == first_name
    assert answers['haem_background'] == 'rowan_scatter'
    assert answers['psi_share'] == 0.4
    assert answers['haems'] == ['bH', 'bL']
    assert session.kept is None
    assert redraws == [True, True]

    # ---- 3 While the regions are being chosen, they stay -----------------------------
    viewer_stages._strip_change_applier(session, answers, Path('.'), {'compare': True})
    changer()
    session.is_choosing_regions = True
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {BACK_CHANGE: True},
                                        )
    assert session.fit is first_fit
    assert answers['psi_share'] == 0.4
    assert session.regions['run1']['oxidised_end'] == 5.0
    assert session.kept is None
    session.is_choosing_regions = False

    # ---- 4 Nothing kept: nothing happens ---------------------------------------------
    drawn = len(redraws)
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {BACK_CHANGE: True},
                                        )
    assert session.fit is first_fit
    assert len(redraws) == drawn

    # ---- 5 Keep this one: what is in use stays, the kept one goes --------------------
    viewer_stages._strip_change_applier(session, answers, Path('.'), {'compare': True})
    changer()
    viewer_stages._strip_change_applier(session, answers, Path('.'), {'compare': False})
    assert session.fit == {'haem_list': ['bH', 'bL', 'c1']}
    assert answers['haem_background'] == 'valencia'
    assert answers['psi_share'] == 0.6
    assert session.kept is None

    # ---- 6 The strip tells the click only while one is kept --------------------------
    # Every widget is the same stand-in, so only what the strip tells is checked.
    told: list = []
    strip = SettingsStrip(MagicMock(), MagicMock(), MagicMock(), 'white', told.append)
    strip.state_setter(True)
    strip._back_handler()
    assert told == []
    strip.values_setter({'plot_haems': True, 'compare': True, 'kept': 'made_up.csv'})
    strip._back_handler()
    assert told == [{BACK_CHANGE: True}]


# ---- test_answers_shown_in_the_strip -------------------------------------------------
def test_answers_shown_in_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check that the answers of a run are shown in the strip as they
    are meant (the standard size as the journal "None", a chosen journal by its name,
    the box ticked only when the haems are worked out, the OCR as the answers have
    it), that the strip can show them, and that its journal, width and
    height give the same answers back.

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
    values = strip_values_builder(standard, True, ['c1_myco.csv', 'bH_bswitch.csv'])
    assert values == {'plot_haems': True,
                      'fit_file': settings.STANDARD_FIT,
                      'haem_background': 'rowan_scatter',
                      'haem_files': ['c1_myco.csv', 'bH_bswitch.csv'],
                      'compare': False,
                      'kept': '',
                      'spectra': 'Cyt',
                      'haem_mode': 'delta',
                      'haem_per_od': True,
                      'ocr_mode': 'od',
                      'label_mode': 'chamber',
                      'delta_psi': False,
                      'psi_bH_mV': 40.0,
                      'psi_bL_mV': -20.0,
                      'psi_fall_mV': 70.0,
                      'psi_share': 0.5,
                      'temperature_c': 37.0,
                      'psi_lowest_percent': 10.0,
                      'psi_highest_percent': 90.0,
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
                  haem_background='linear',
                  decomposition_dataset='NADH',
                  haem_mode='percent',
                  haem_per_od=False,
                  ocr_mode='percent',
                  label_mode='added',
                  )
    values = strip_values_builder(chosen, False, [], kept='made_up.csv, Valencia')
    assert values == {'plot_haems': False,
                      'fit_file': '',
                      'haem_background': 'linear',
                      'haem_files': [],
                      'compare': True,
                      'kept': 'made_up.csv, Valencia',
                      'spectra': 'NADH',
                      'haem_mode': 'percent',
                      'haem_per_od': False,
                      'ocr_mode': 'percent',
                      'label_mode': 'added',
                      'delta_psi': False,
                      'psi_bH_mV': 40.0,
                      'psi_bL_mV': -20.0,
                      'psi_fall_mV': 70.0,
                      'psi_share': 0.5,
                      'temperature_c': 37.0,
                      'psi_lowest_percent': 10.0,
                      'psi_highest_percent': 90.0,
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
    name, an unknown journal, a width the journal does not allow, a height over a page,
    an unknown background, haems ticked that are not a list of names, a comparing that
    is not True or False, a kept decomposition not in words, a spectrometer not given
    by its name, a way of showing the haems or the OCR the strip does not have and a
    per OD box that is not True or False are each refused.

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
    strip_values_checker({'haem_background': 'valencia', 'haem_files': ['bL_og.csv']})
    strip_values_checker({'spectra': 'NADH',
                          'haem_mode': 'percent',
                          'haem_per_od': False,
                          'ocr_mode': 'baseline',
                          'label_mode': 'added',
                          },
                         )
    strip_values_checker({})
    for wrong in ({'colour': 'red'},
                  {'journal': 'lancet'},
                  {'journal': 'nature', 'columns': 3},
                  {'height': 1.5},
                  {'height': 'tall'},
                  {'haem_background': 'wavy'},
                  {'haem_files': 'bL_og.csv'},
                  {'haem_files': [3]},
                  {'compare': 'yes'},
                  {'kept': None},
                  {'spectra': None},
                  {'haem_mode': 'conc'},
                  {'haem_per_od': 'yes'},
                  {'ocr_mode': 'per_cell'},
                  {'label_mode': 'both'},
                  {'ocr_per_od': True},
                  ):
        with pytest.raises(ValueError):
            strip_values_checker(wrong)


# ---- test_numbers_of_the_delta_psi_row -----------------------------------------------
def test_numbers_of_the_delta_psi_row() -> None:
    """
    ---- Summary ----
    Main function to check the Δψ row of the strip: the midpoints filled in from the
    ones typed and the fall, the answers a change gives, the sentence that says it,
    the row shown only with the haems and Δψ switched on, the numbers refused with a
    reason, the values the strip cannot show, and what the row keeps and tells when a
    number is typed, refused, or the paper's values are put back (not the
    temperature).

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
    second = first - fall. The paper's: 40 - 70 = -30 and -20 - 70 = -90. A fall of 60
    typed: 40 - 60 = -20 and -20 - 60 = -80. bH typed as 50 with the fall of 70 kept:
    50 - 70 = -20, and bL stays at -20 and -90. From answers of 50 and -20 the fall
    shown is 50 - (-20) = 70.

    ---- Helpers ----
    None.
    """

    # ---- 1 The midpoints filled in ---------------------------------------------------
    assert psi_seconds_filler(40.0, -20.0, 70.0) == (-30.0, -90.0)
    assert psi_seconds_filler(40.0, -20.0, 60.0) == (-20.0, -80.0)
    assert psi_seconds_filler(50.0, -20.0, 70.0) == (-20.0, -90.0)

    # ---- 2 The answers a change gives ------------------------------------------------
    standard = dict(settings.DEFAULT_ANSWERS)
    assert psi_answers_builder({'psi_fall_mV': 60.0}, standard) == {
        'psi_bH_first_mV': 40.0,
        'psi_bL_first_mV': -20.0,
        'psi_bH_second_mV': -20.0,
        'psi_bL_second_mV': -80.0,
        }
    typed = psi_answers_builder({'psi_bH_mV': 50.0}, standard)
    assert typed == {'psi_bH_first_mV': 50.0,
                     'psi_bL_first_mV': -20.0,
                     'psi_bH_second_mV': -20.0,
                     'psi_bL_second_mV': -90.0,
                     }
    assert psi_answers_builder({'psi_share': 0.4,
                                'temperature_c': 30,
                                'psi_lowest_percent': 20.0,
                                'psi_highest_percent': 80.0,
                                },
                               standard,
                               ) == {'psi_share': 0.4,
                                     'temperature_c': 30.0,
                                     'psi_reduced_lowest_percent': 20.0,
                                     'psi_reduced_highest_percent': 80.0,
                                     }
    assert psi_answers_builder({'haem_mode': 'abs', 'height': 0.3}, standard) == {}

    # ---- 3 The sentences that say it -------------------------------------------------
    changed = dict(standard, **typed)
    assert psi_change_describer({'psi_bH_mV': 50.0}, changed) == [
        'Δψ is now worked out with bH at 50 mV (-20 mV with bL reduced) and bL at '
        '-20 mV (-90 mV with bH reduced): a fall of 70 mV.',
        ]
    assert psi_change_describer({'psi_share': 0.4,
                                 'temperature_c': 30.0,
                                 'psi_lowest_percent': 20.0,
                                 },
                                dict(standard,
                                     psi_share=0.4,
                                     temperature_c=30.0,
                                     psi_reduced_lowest_percent=20.0,
                                     ),
                                ) == [
                                    'The share of the membrane potential between bH and bL is now 0.4.',
                                    'The temperature of the runs is now 30 °C.',
                                    'Δψ is now given where bH and bL are between 20 and 90 % reduced.',
                                    ]
    assert psi_change_describer({'height': 0.3}, standard) == []

    # ---- 4 What the row shows --------------------------------------------------------
    assert psi_values_builder(changed, True) == {'delta_psi': True,
                                                 'psi_bH_mV': 50.0,
                                                 'psi_bL_mV': -20.0,
                                                 'psi_fall_mV': 70.0,
                                                 'psi_share': 0.5,
                                                 'temperature_c': 37.0,
                                                 'psi_lowest_percent': 10.0,
                                                 'psi_highest_percent': 90.0,
                                                 }
    assert psi_summary_writer(psi_values_builder(standard, True)) == (
        'share 0.5 · 37 °C · given between 10 and 90 % reduced'
        )
    switched_on = dict(standard, delta_psi=True)
    assert strip_values_builder(switched_on, True, [])['delta_psi'] is True
    assert strip_values_builder(switched_on, False, [])['delta_psi'] is False
    assert strip_values_builder(standard, True, [])['delta_psi'] is False

    # ---- 5 The numbers typed ---------------------------------------------------------
    values = psi_values_builder(standard, True)
    assert psi_number_checker('psi_bH_mV', ' 45,5 ', values) == (45.5, '')
    assert psi_number_checker('psi_bL_mV', '-25', values) == (-25.0, '')
    assert psi_number_checker('psi_fall_mV', '0', values) == (0.0, '')
    assert psi_number_checker('psi_share', '0.4', values) == (0.4, '')
    assert psi_number_checker('temperature_c', '30', values) == (30.0, '')
    assert psi_number_checker('psi_lowest_percent', '20', values) == (20.0, '')
    assert psi_number_checker('psi_highest_percent', '80', values) == (80.0, '')
    for name, wrong, words in (('psi_bH_mV', 'high', 'a number of mV'),
                               ('psi_fall_mV', '', 'a number of mV'),
                               ('psi_share', '0', 'a share above 0'),
                               ('psi_share', '-0.5', 'a share above 0'),
                               ('temperature_c', '-300', 'from 0 to 100 °C'),
                               ('temperature_c', 'warm', 'from 0 to 100 °C'),
                               ('psi_lowest_percent', '0', 'above 0 and below 90'),
                               ('psi_lowest_percent', '90', 'above 0 and below 90'),
                               ('psi_highest_percent', '100', 'above 10 and below 100'),
                               ('psi_highest_percent', '5', 'above 10 and below 100'),
                               ):
        number, reason = psi_number_checker(name, wrong, values)
        assert number is None
        assert words in reason

    # ---- 6 The values the strip can show ---------------------------------------------
    strip_values_checker(values)
    strip_values_checker({'psi_lowest_percent': 20.0})
    for wrong in ({'delta_psi': 'yes'},
                  {'psi_bH_mV': '40'},
                  {'psi_fall_mV': True},
                  {'psi_bL_mV': float('nan')},
                  {'psi_share': 0},
                  {'psi_lowest_percent': 0.0},
                  {'psi_highest_percent': 100.0},
                  {'psi_lowest_percent': 90.0, 'psi_highest_percent': 10.0},
                  {'psi_lowest_percent': 50.0, 'psi_highest_percent': 50.0},
                  ):
        with pytest.raises(ValueError):
            strip_values_checker(wrong)

    # ---- 7 The row itself, its widgets stood in for ----------------------------------
    # Every widget is the same stand-in, so only what the strip keeps and tells is
    # checked: a number typed, a number refused, and the paper's values put back.
    tk = MagicMock()
    told: list = []
    strip = SettingsStrip(tk, MagicMock(), MagicMock(), 'white', told.append)
    strip.state_setter(True)
    strip.values_setter({'delta_psi': True, 'psi_share': 0.4, 'temperature_c': 30.0})
    box = tk.Entry.return_value
    box.cget.return_value = 'normal'
    box.get.return_value = '60'
    strip._psi_handler('psi_fall_mV')
    box.get.return_value = 'far'
    strip._psi_handler('psi_bH_mV')
    assert told == [{'psi_fall_mV': 60.0}]
    assert strip.values_reader()['psi_bH_mV'] == 40.0
    strip._paper_handler()
    assert told[1:] == [{'psi_fall_mV': 70.0, 'psi_share': 0.5}]
    assert strip.values_reader()['temperature_c'] == 30.0


# ---- test_haems_and_ocr_shown_from_the_strip -----------------------------------------
def test_haems_and_ocr_shown_from_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check the "Haems as" and the "OCR as" drop-downs and the per OD
    box: % oxidised is in the list only when a file has both regions, the OCR per OD
    only when OD values were entered and its % of baseline only when the averaging
    windows are set up; and the spectrometer, the ways of showing the haems and the
    OCR and the box give the answers of the run, only for what changed.

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

    # ---- 1 The list of the drop-down -------------------------------------------------
    assert haem_form_choices_lister(False) == [('delta', 'ΔD (mOD)'),
                                               ('abs', 'Absorbance (mOD)'),
                                               ]
    assert haem_form_choices_lister(True) == [('delta', 'ΔD (mOD)'),
                                              ('percent', '% oxidised'),
                                              ('abs', 'Absorbance (mOD)'),
                                              ]

    assert ocr_form_choices_lister(False, False) == [('raw', 'µM min⁻¹'),
                                                     ('percent', '% of the range'),
                                                     ]
    assert ocr_form_choices_lister(True, True) == [('raw', 'µM min⁻¹'),
                                                   ('od', 'per OD (µM min⁻¹ OD⁻¹)'),
                                                   ('percent', '% of the range'),
                                                   ('baseline', '% of baseline'),
                                                   ]
    assert [key for key, _ in ocr_form_choices_lister(False, True)] == ['raw',
                                                                        'percent',
                                                                        'baseline',
                                                                        ]

    # ---- 2 The strip values as answers -----------------------------------------------
    assert form_answers_builder({'spectra': 'NADH',
                                 'haem_mode': 'percent',
                                 'haem_per_od': False,
                                 'ocr_mode': 'od',
                                 },
                                ) == {'decomposition_dataset': 'NADH',
                                      'haem_mode': 'percent',
                                      'haem_per_od': False,
                                      'ocr_mode': 'od',
                                      }
    assert form_answers_builder({'ocr_mode': 'baseline'}) == {'ocr_mode': 'baseline'}
    assert form_answers_builder({'label_mode': 'added'}) == {'label_mode': 'added'}
    assert form_answers_builder({'journal': 'cell', 'plot_haems': True}) == {}


# ---- test_plots_follow_the_strip -----------------------------------------------------
def test_plots_follow_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check the answers each kind of plot is drawn with: the standard
    and the processing plot show the haems and the OCR as the answers say (the strip
    sets them), per OD only once OD values were entered; the figure of each file is
    drawn with the answers as they are.

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

    fit = {'haem_list': ['Cyt bH', 'Cyt c1']}
    answers = dict(settings.DEFAULT_ANSWERS,
                   normalise_od=True,
                   decompose=True,
                   haem_mode='percent',
                   haem_per_od=True,
                   ocr_mode='od',
                   averaging=True,
                   plot_ocr=False,
                   )
    def shown(result: dict) -> dict:
        return {key: result[key]
                for key in ('normalise_od',
                            'ocr_mode',
                            'haem_mode',
                            'haem_per_od',
                            'decompose',
                            'plot_haems',
                            'haems',
                            'averaging',
                            'plot_ocr',
                            )
                }

    # ---- 1 Before the OD values are entered: nothing per OD --------------------------
    assert shown(_answers_previewer(answers, fit, 'standard')) == {
        'normalise_od': False,
        'ocr_mode': 'raw',
        'haem_mode': 'percent',
        'haem_per_od': False,
        'decompose': True,
        'plot_haems': True,
        'haems': ['Cyt bH', 'Cyt c1'],
        'averaging': False,
        'plot_ocr': True,
        }

    # ---- 2 Once they are: as the answers say -----------------------------------------
    assert shown(_answers_previewer(answers, fit, 'analysis', True)) == {
        'normalise_od': True,
        'ocr_mode': 'od',
        'haem_mode': 'percent',
        'haem_per_od': True,
        'decompose': True,
        'plot_haems': True,
        'haems': ['Cyt bH', 'Cyt c1'],
        'averaging': True,
        'plot_ocr': True,
        }
    # the OCR's % of the range is no per OD, so it stays without OD values too
    ranged = _answers_previewer(dict(answers, ocr_mode='percent'), None, 'standard')
    assert (ranged['ocr_mode'], ranged['plot_haems']) == ('percent', False)
    # nor is its % of baseline: asked for, it stays, and the file is drawn with its
    # usual OCR while the plot has no windows
    based = _answers_previewer(dict(answers, ocr_mode='baseline'), None, 'standard')
    assert (based['ocr_mode'], based['averaging']) == ('baseline', False)

    # ---- 3 The raw plot and the figure of each file ----------------------------------
    raw = shown(_answers_previewer(answers, fit, 'raw', True))
    assert (raw['ocr_mode'], raw['normalise_od'], raw['plot_haems']) == ('raw',
                                                                         False,
                                                                         False,
                                                                         )
    assert _answers_previewer(answers, fit, 'final') == answers
    assert answers['haem_mode'] == 'percent'  # the answers themselves are not changed


# ---- test_haems_ticked_in_the_strip --------------------------------------------------
def test_haems_ticked_in_the_strip() -> None:
    """
    ---- Summary ----
    Main function to check the tick boxes of Build a fit: a haem ticked is added; a
    haem with the same name as one ticked takes its place, with a note naming both; a
    haem unticked is taken away; the last cannot be unticked, with a note; and a box
    not ticked before changes nothing when unticked.

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

    names = {'c1_myco.csv': 'Cyt cc',
             'c1_037v.csv': 'Cyt cc',
             'c1_og.csv': 'Cyt c1',
             'bH_og.csv': 'Cyt bH',
             }
    assert haem_ticks_resolver(['c1_myco.csv'], 'bH_og.csv', True, names) == (
        ['c1_myco.csv', 'bH_og.csv'],
        '',
        )
    assert haem_ticks_resolver(['c1_og.csv'], 'c1_myco.csv', True, names) == (
        ['c1_og.csv', 'c1_myco.csv'],
        '',
        )
    ticked, note = haem_ticks_resolver(['c1_myco.csv', 'bH_og.csv'],
                                       'c1_037v.csv',
                                       True,
                                       names,
                                       )
    assert ticked == ['bH_og.csv', 'c1_037v.csv']
    assert 'c1_037v.csv' in note and 'c1_myco.csv' in note and 'Cyt cc' in note
    assert haem_ticks_resolver(['c1_myco.csv', 'bH_og.csv'],
                               'c1_myco.csv',
                               False,
                               names,
                               ) == (['bH_og.csv'], '')
    ticked, note = haem_ticks_resolver(['bH_og.csv'], 'bH_og.csv', False, names)
    assert ticked == ['bH_og.csv'] and note
    assert haem_ticks_resolver(['bH_og.csv'], 'c1_og.csv', False, names) == (
        ['bH_og.csv'],
        '',
        )


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
