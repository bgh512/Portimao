"""
Tests of the settings kept with each run of a dataset, the earlier runs offered, the name
of a run and the list of data folders.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.dataset_settings import (dataset_settings_reader,
                                           dataset_settings_saver,
                                           earlier_runs_lister,
                                           file_settings_merger,
                                           SETTINGS_FILE_NAME,
                                           )
from utils_shared.figure_page import (FigurePage,
                                      page_plainer,
                                      PagePlot,
                                      plain_page_reader,
                                      plot_placer,
                                      )
from utils_shared.survey import (data_folder_lister,
                                 data_folder_resolver,
                                 haem_form_option_builder,
                                 run_name_checker,
                                 run_name_finder,
                                 save_place_checker,
                                 saved_values_reader,
                                 )


# ---- CONSTANTS -----------------------------------------------------------------------
FILES = {'run1': {'trim_start': 2.0,
                  'trim_end': None,
                  'ignore_start': 5.0,
                  'ignore_end': 0.0,
                  },
         }
ANSWERS = {'fit_file': 'some_fit.csv', 'columns': 1.5, 'haems': ['Cyt a', 'Cyt b']}


# ---- HELPERS -------------------------------------------------------------------------


# ---- _program_folder_maker -----------------------------------------------------------
def _program_folder_maker(root: Path) -> None:
    """
    ---- Summary ----
    Helper function to make a pretend program folder: two folders with .paf files, one
    without, one hidden work folder with a .paf file, and a loose .paf file.

    ---- Inputs ----
    root : Path
        Empty folder to fill.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes the folders and files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for folder, file_name in (('data_10hours', 'a.paf'),
                              ('data_2hours', 'b.PAF'),
                              ('fits', 'fit.csv'),
                              ('_work', 'c.paf'),
                              ):
        (root / folder).mkdir()
        (root / folder / file_name).write_text('')
    (root / 'loose.paf').write_text('')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_broken_settings_file_gives_nothing -----------------------------------------
def test_broken_settings_file_gives_nothing(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a settings file that is not readable JSON, or is not a
    dictionary, gives no settings, so the standard ones are used.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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

    (tmp_path / SETTINGS_FILE_NAME).write_text('{not json', encoding='utf-8')
    assert dataset_settings_reader(tmp_path) == {}
    (tmp_path / SETTINGS_FILE_NAME).write_text('[1, 2]', encoding='utf-8')
    assert dataset_settings_reader(tmp_path) == {}


# ---- test_data_folders_are_listed ----------------------------------------------------
def test_data_folders_are_listed(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that only the folders holding .paf files are listed, in
    natural order (2 hours before 10 hours), without the folders starting with an
    underscore.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _program_folder_maker
    """

    _program_folder_maker(tmp_path)
    # the run the tests check the reading against is never offered as a dataset
    hidden = tmp_path / 'data_instrument_check'
    hidden.mkdir()
    (hidden / 'example.paf').write_bytes(b'')
    assert [p.name for p in data_folder_lister(tmp_path)] == ['data_2hours',
                                                              'data_10hours',
                                                              ]


# ---- test_folder_answer_is_resolved --------------------------------------------------
def test_folder_answer_is_resolved(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the three ways of answering the folder question: a number
    from the list, a name from the list (capitals do not matter), or another path; a
    number that is not in the list is taken as a path.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _program_folder_maker
    """

    _program_folder_maker(tmp_path)
    listed = data_folder_lister(tmp_path)
    assert data_folder_resolver('2', listed) == tmp_path / 'data_10hours'
    assert data_folder_resolver(' 1 ', listed) == tmp_path / 'data_2hours'
    assert data_folder_resolver('DATA_2Hours', listed) == tmp_path / 'data_2hours'
    assert data_folder_resolver(str(tmp_path / 'fits'), listed) == tmp_path / 'fits'
    assert data_folder_resolver('3', listed) == Path('3')


# ---- test_missing_settings_file_gives_nothing ----------------------------------------
def test_missing_settings_file_gives_nothing(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a dataset never saved gives no settings.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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

    assert dataset_settings_reader(tmp_path) == {}


# ---- test_od_values_and_labels_are_kept ----------------------------------------------
def test_od_values_and_labels_are_kept(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the OD values and event labels of a run are kept in the
    dataset's settings beside its limits and offered back from there: an OD not asked
    this run (no OD scaling) stays as saved, a file not in this run is kept, and the
    values are written as plain numbers and text.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Saved before: OD values for run1, and another file ------------------------
    remembered = {'run1': dict(FILES['run1'], OD=0.5, volume=1.0, dilution_factor=1.0),
                  'old_run': {'trim_start': None, 'OD': 0.7},
                  }
    limits = {'run1': {'trim_start': 3.0,
                       'trim_end': 40.0,
                       'ignore_start': 5.0,
                       'ignore_end': 0.0,
                       },
              }
    events = [{'datapoint': np.int64(120),
               'label': 'KCN',
               'stock_uM': np.float64(10_000.0),
               'added_uL': 1,
               'addition_uM': np.float64(2.0),
               'concentration_uM': np.float64(2.0),
               'ignored': np.bool_(False),
               },
              {'datapoint': 300,
               'label': 'ignore',
               'concentration_uM': None,
               'ignored': True,
               },
              ]

    # ---- 2 This run: no OD scaling, new labels ---------------------------------------
    files = file_settings_merger(remembered, limits, {'run1': {'events': events}})
    assert files['run1']['trim_start'] == 3.0
    assert files['run1']['OD'] == 0.5
    assert files['run1']['events'][0] == {'datapoint': 120,
                                          'label': 'KCN',
                                          'stock_uM': 10_000.0,
                                          'added_uL': 1.0,
                                          'addition_uM': 2.0,
                                          'concentration_uM': 2.0,
                                          'ignored': False,
                                          }
    # an event saved before the stock and the volume were asked keeps them empty
    assert files['run1']['events'][1]['stock_uM'] is None
    assert files['old_run'] == {'trim_start': None, 'OD': 0.7}

    # ---- 3 Saved, read back and offered ----------------------------------------------
    assert dataset_settings_saver(tmp_path,files, ANSWERS)
    saved = dataset_settings_reader(tmp_path)['files']
    offered = saved_values_reader([{'name': 'run1'}, {'name': 'new_run'}],
                                  saved,
                                  )
    assert offered['run1'] == {'OD': 0.5,
                               'volume': 1.0,
                               'dilution_factor': 1.0,
                               'events': files['run1']['events'],
                               }
    assert offered['new_run'] is None

    # ---- 4 This run scaled by OD: the new values replace the old ---------------------
    files = file_settings_merger(remembered,
                                 limits,
                                 {'run1': {'OD': 0.8,
                                           'volume': 2.0,
                                           'dilution_factor': 1.0,
                                           'events': [],
                                           },
                                  },
                                 )
    assert (files['run1']['OD'], files['run1']['volume']) == (0.8, 2.0)
    assert files['run1']['events'] == []


# ---- test_earlier_runs_are_listed ----------------------------------------------------
def test_earlier_runs_are_listed(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the earlier runs offered at 1.2: none for data never
    processed; every folder in the export folder that holds a settings file, in the
    order of their names with the numbers counted (run_2 before run_10); a folder
    without a settings file, or with one that cannot be read, left out; and the
    settings saved beside the data first, as one run named after the results folder
    they used, or after the export folder when they name none.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS, SETTINGS_FILE_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Data never processed ------------------------------------------------------
    data = tmp_path / 'data'
    data.mkdir()
    assert earlier_runs_lister(data, 'export') == []
    (data / 'export' / 'loose_results').mkdir(parents=True)
    assert earlier_runs_lister(data, 'export') == []

    # ---- 2 The runs in the export folder ---------------------------------------------
    for name, fit in (('run_10', 'ten.csv'),
                      ('run_2', 'two.csv'),
                      ('Trimmed', 't.csv'),
                      ):
        (data / 'export' / name).mkdir()
        assert dataset_settings_saver(data / 'export' / name,
                                      FILES,
                                      dict(ANSWERS, fit_file=fit),
                                      )
    (data / 'export' / 'broken').mkdir()
    (data / 'export' / 'broken' / SETTINGS_FILE_NAME).write_text('{not json')
    (data / 'export' / 'notes.txt').write_text('')
    runs = earlier_runs_lister(data, 'export')
    assert [name for name, _ in runs] == ['run_2', 'run_10', 'Trimmed']
    assert [saved['answers']['fit_file'] for _, saved in runs] == ['two.csv',
                                                                   'ten.csv',
                                                                   't.csv',
                                                                   ]
    assert runs[0][1]['files'] == FILES
    assert runs[0][1]['export_folder'] is None

    # ---- 3 The settings saved beside the data come first -----------------------------
    beside = {'export_folder': 'old_results', 'files': FILES, 'answers': ANSWERS}
    (data / SETTINGS_FILE_NAME).write_text(json.dumps(beside), encoding='utf-8')
    runs = earlier_runs_lister(data, 'export')
    assert [name for name, _ in runs] == ['old_results', 'run_2', 'run_10', 'Trimmed']
    assert runs[0][1]['answers'] == ANSWERS
    del beside['export_folder']
    (data / SETTINGS_FILE_NAME).write_text(json.dumps(beside), encoding='utf-8')
    assert earlier_runs_lister(data, 'export')[0][0] == 'export'


# ---- test_results_folder_beside_the_data_is_read -------------------------------------
def test_results_folder_beside_the_data_is_read(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the results folder named in a settings file saved beside
    the data: a path without a drive or root is taken inside the data folder, so it
    still holds after the data is copied; a full path is given as it is; and the file
    of a run names none.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS, SETTINGS_FILE_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    values = {'export_folder': 'results/run', 'files': FILES, 'answers': ANSWERS}
    (tmp_path / SETTINGS_FILE_NAME).write_text(json.dumps(values), encoding='utf-8')
    assert dataset_settings_reader(tmp_path)['export_folder'] == (
        tmp_path / 'results' / 'run')
    outside = (tmp_path / 'paper').resolve()
    values['export_folder'] = str(outside)
    (tmp_path / SETTINGS_FILE_NAME).write_text(json.dumps(values), encoding='utf-8')
    assert dataset_settings_reader(tmp_path)['export_folder'] == outside
    assert dataset_settings_saver(tmp_path, FILES, ANSWERS)
    written = json.loads((tmp_path / SETTINGS_FILE_NAME).read_text('utf-8'))
    assert 'export_folder' not in written
    assert dataset_settings_reader(tmp_path)['export_folder'] is None


# ---- test_run_name_is_checked --------------------------------------------------------
def test_run_name_is_checked(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the name of a run (1.3): the name offered is the first of
    run_1, run_2 and so on that is not there; a name of letters, digits, spaces, -
    and _ is accepted, also one already there as a folder; an empty name, a path, a
    name with other characters and the name of a file there are refused with one
    sentence each.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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

    # ---- 1 The name offered ----------------------------------------------------------
    export = tmp_path / 'export'
    assert run_name_finder(export) == 'run_1'
    (export / 'run_1').mkdir(parents=True)
    (export / 'run_2').write_text('')
    (export / 'run_4').mkdir()
    assert run_name_finder(export) == 'run_3'

    # ---- 2 The names accepted and refused --------------------------------------------
    plain = 'Type a name of letters, digits, spaces, - and _ only.'
    for name in ('run_1', 'run_3', ' trimmed less ', 'KCN-first 2', 'après'):
        assert run_name_checker(name, export) is None
    for name in ('', '   ', None):
        assert run_name_checker(name, export) == 'Type a name.'
    for name in ('a/b', 'a\\b', '..', 'run.1', 'C:', 'what?', str(tmp_path)):
        assert run_name_checker(name, export) == plain
    assert run_name_checker('run_2', export) == ('A file with this name is already '
                                                 'there. Type another name.')


# ---- test_save_place_is_checked ------------------------------------------------------
def test_save_place_is_checked(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check whether a folder can be saved to: a folder there and one
    not made yet can; a file, and a folder under a file, cannot; and checking leaves
    nothing behind.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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

    a_file = tmp_path / 'notes.txt'
    a_file.write_text('')
    assert save_place_checker(tmp_path)
    assert save_place_checker(tmp_path / 'new' / 'export')
    assert not save_place_checker(a_file)
    assert not save_place_checker(a_file / 'export')
    assert [p.name for p in tmp_path.iterdir()] == ['notes.txt']


# ---- test_regions_are_kept_with_the_dataset ------------------------------------------
def test_regions_are_kept_with_the_dataset(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the oxidised and the reduced region of each file are
    saved with the dataset and read back: a lone region is kept as it was left, a file
    with neither region chosen has none saved (one saved before is cleared), a file
    not in this run keeps its own, and a run that did not handle the regions leaves
    those saved before.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Saved before: regions for run2 and for a file not in this run -------------
    both = {'oxidised_start': 6.0,
            'oxidised_end': 9.5,
            'reduced_start': 41.0,
            'reduced_end': 44.0,
            }
    old = {'oxidised_start': 1.0,
           'oxidised_end': 2.0,
           'reduced_start': 8.0,
           'reduced_end': 9.0,
           }
    remembered = {'run2': {'trim_start': None, 'regions': dict(old)},
                  'old_run': {'trim_start': None, 'regions': dict(old)},
                  }
    limits = {name: {'trim_start': 3.0,
                     'trim_end': 50.0,
                     'ignore_start': 5.0,
                     'ignore_end': 0.0,
                     }
              for name in ('run1', 'run2', 'run3')
              }

    # ---- 2 This run: both for run1, neither for run2, only the oxidised for run3 -----
    regions = {'run1': {key: np.float64(value) for key, value in both.items()},
               'run2': dict(both, oxidised_end=6.0, reduced_start=44.0),
               'run3': dict(both, reduced_start=44.0),
               }
    files = file_settings_merger(remembered, limits, {}, regions)
    assert files['run1']['regions'] == both
    assert all(type(value) is float for value in files['run1']['regions'].values())
    assert 'regions' not in files['run2']
    assert files['run3']['regions'] == dict(both, reduced_start=44.0)
    assert files['old_run']['regions'] == old

    # ---- 3 Saved and read back -------------------------------------------------------
    assert dataset_settings_saver(tmp_path,files, ANSWERS)
    saved = dataset_settings_reader(tmp_path)['files']
    assert saved['run1']['regions'] == both
    assert 'regions' not in saved['run2']

    # ---- 4 A run that did not handle the regions leaves them -------------------------
    kept = file_settings_merger(remembered, limits, {})
    assert kept['run2']['regions'] == old
    assert 'regions' not in kept['run1']


# ---- test_saved_haem_amounts_open_as_delta_d -----------------------------------------
def test_saved_haem_amounts_open_as_delta_d(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that, with only cells measured, the haem amounts are not
    offered as a way of showing the haems, that % oxidised is offered only when asked
    for, and that a dataset saved showing the amounts opens showing delta D, the other
    answers unchanged.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for include_percent in (True, False):
        keys = [key for key, _ in haem_form_option_builder(include_percent)]
        assert 'conc' not in keys
        assert keys == ['abs', 'delta'] + (['percent'] if include_percent else [])
    labels = dict(haem_form_option_builder(True))
    assert labels['delta'].startswith('ΔD (mOD)')
    assert labels['percent'].startswith('% oxidised')
    old = dict(ANSWERS, haem_mode='conc')
    assert dataset_settings_saver(tmp_path,FILES, old)
    answers = dataset_settings_reader(tmp_path)['answers']
    assert answers == dict(ANSWERS, haem_mode='delta')


# ---- test_saved_old_figure_answers_are_left_out --------------------------------------
def test_saved_old_figure_answers_are_left_out(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a dataset saved with the answers of the fixed figures
    that are no longer made (side by side, the 2x2 grid, the time response, the haem
    and OCR response) still opens, without them and with every other answer unchanged,
    the export choice among them.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    kept = dict(ANSWERS, export_choice='trimmed', export_spectra=True)
    old = dict(kept,
               plot_comparison=True,
               comparison_journal='nature',
               comparison_columns=1.5,
               plot_exemplar=True,
               ex_journal='nature',
               ex_window_kind='quick',
               ho_exemplar_run=2,
               plot_time_response=True,
               tr_groups=['knockdown', 'control'],
               tr_window_kind='settled',
               plot_haem_ocr=True,
               ho_haems=['Cyt bH'],
               ho_haem_mode='conc',
               )
    assert dataset_settings_saver(tmp_path,FILES, old)
    assert dataset_settings_reader(tmp_path)['answers'] == kept


# ---- test_saved_old_names_open_with_the_new_ones -------------------------------------
def test_saved_old_names_open_with_the_new_ones(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a dataset saved with the Valencia scatter opens with
    Palencia, one saved with the preset temp_fit_037v opens with the Rowan fit 11-2026,
    and the other answers, and other names, are left as they were.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    old = dict(ANSWERS, haem_background='valencia', fit_file='temp_fit_037v.csv')
    assert dataset_settings_saver(tmp_path,FILES, old)
    answers = dataset_settings_reader(tmp_path)['answers']
    assert answers == dict(ANSWERS,
                           haem_background='palencia',
                           fit_file='rowan_fit_11_2026.csv',
                           )
    kept = dict(ANSWERS, haem_background='linear', fit_file='OGfit.csv')
    assert dataset_settings_saver(tmp_path,FILES, kept)
    assert dataset_settings_reader(tmp_path)['answers'] == kept


# ---- test_settings_are_read_back -----------------------------------------------------
def test_settings_are_read_back(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the trim and ignore times and the answers saved with a
    dataset are read back unchanged.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert dataset_settings_saver(tmp_path,FILES, ANSWERS)
    saved = dataset_settings_reader(tmp_path)
    assert saved['files'] == FILES
    assert saved['answers'] == ANSWERS


# ---- test_the_page_is_kept_with_the_dataset ------------------------------------------
def test_the_page_is_kept_with_the_dataset(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the page of the dataset figure is saved with the
    dataset and read back as the same page, every pick included; that a page with no
    plot and no page write none; and that a settings file without a page gives none.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    FILES, ANSWERS, SETTINGS_FILE_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 A page with two plots, one with its pick ----------------------------------
    pick = 'Group 1: 2, Group 2: 0, time point: 0, replicate: 1'
    page = plot_placer(FigurePage(journal='science', columns=1, height=0.5),
                       PagePlot('P1', 0, 0, 2, 3, roles={'experiment': pick}),
                       )
    page = plot_placer(page, PagePlot('P9', 2, 0, 2, 2, roles={'group_1': 'Split'}))
    assert dataset_settings_saver(tmp_path,
                                  FILES,
                                  ANSWERS,
                                  None,
                                  page_plainer(page),
                                  )
    written = json.loads((tmp_path / SETTINGS_FILE_NAME).read_text('utf-8'))
    assert written['page']['plots'][0]['roles'] == {'experiment': pick}
    read = dataset_settings_reader(tmp_path)
    assert plain_page_reader(read['page'], 'The saved page cannot be used') == page
    assert read['files'] == FILES and read['answers'] == ANSWERS

    # ---- 2 No plot, or no page: none written -----------------------------------------
    for empty in (page_plainer(FigurePage()), None):
        assert dataset_settings_saver(tmp_path,
                                      FILES,
                                      ANSWERS,
                                      None,
                                      empty,
                                      )
        written = json.loads((tmp_path / SETTINGS_FILE_NAME).read_text('utf-8'))
        assert 'page' not in written
        assert dataset_settings_reader(tmp_path)['page'] is None


# ---- test_unwritable_folder_is_reported ----------------------------------------------
def test_unwritable_folder_is_reported(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that saving into a folder that is not there says so (False)
    and does not raise.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

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

    missing = tmp_path / 'not_there'
    assert not dataset_settings_saver(missing, FILES, ANSWERS)
