"""
Tests of the settings kept with a dataset, the results folder check and the list of data
folders.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.dataset_settings import (dataset_settings_reader,
                                           dataset_settings_saver,
                                           file_settings_merger,
                                           SETTINGS_FILE_NAME,
                                           )
from utils_shared.survey import (data_folder_lister,
                                 data_folder_resolver,
                                 free_folder_finder,
                                 haem_form_option_builder,
                                 results_counter,
                                 results_folder_checker,
                                 results_folder_resolver,
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
               'label': '1 µL 10 mM KCN',
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
                                          'label': '1 µL 10 mM KCN',
                                          'concentration_uM': 2.0,
                                          'ignored': False,
                                          }
    assert files['old_run'] == {'trim_start': None, 'OD': 0.7}

    # ---- 3 Saved, read back and offered ----------------------------------------------
    assert dataset_settings_saver(tmp_path, tmp_path / 'results', files, ANSWERS)
    saved = dataset_settings_reader(tmp_path)['files']
    offered = saved_values_reader([{'name': 'run1'}, {'name': 'new_run'}],
                                  saved,
                                  tmp_path / 'results',
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


# ---- test_results_folder_inside_is_kept_relative -------------------------------------
def test_results_folder_inside_is_kept_relative(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a results folder inside the dataset folder is written
    relative to it, so the settings still hold after the dataset is copied: the copy
    gives the results folder inside the copy.

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

    first, copy = tmp_path / 'first', tmp_path / 'copy'
    first.mkdir()
    copy.mkdir()
    assert dataset_settings_saver(first, first / 'results' / 'run', FILES, ANSWERS)
    text = (first / SETTINGS_FILE_NAME).read_text(encoding='utf-8')
    assert json.loads(text)['export_folder'] == 'results/run'
    (copy / SETTINGS_FILE_NAME).write_text(text, encoding='utf-8')
    assert dataset_settings_reader(copy)['export_folder'] == copy / 'results' / 'run'


# ---- test_results_folder_is_checked --------------------------------------------------
def test_results_folder_is_checked(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the results folder answer: a file, or a folder under a file,
    is refused with one sentence; an existing folder and one not made yet are accepted,
    and checking leaves nothing behind.

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
    not_a_file = 'Type or drag in a folder, not a file.'
    assert results_folder_checker(str(a_file)) == not_a_file
    assert results_folder_checker(f'"{a_file / "results"}"') == not_a_file
    assert results_folder_checker('') == 'Type or drag in a folder.'
    assert results_folder_checker(str(tmp_path)) is None
    assert results_folder_checker(str(tmp_path / 'new' / 'results')) is None
    assert [p.name for p in tmp_path.iterdir()] == ['notes.txt']


# ---- test_results_folder_names_and_old_results ---------------------------------------
def test_results_folder_names_and_old_results(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the results folder answer against the data folder: a name
    without a path is taken inside the data folder and a full path as it is; the files
    that already have results there are counted (an empty folder of one does not
    count); and the free name offered beside a folder skips the names already used.

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

    # ---- 1 A plain name goes inside the data folder ----------------------------------
    data = tmp_path / 'data'
    data.mkdir()
    elsewhere = tmp_path / 'elsewhere'
    assert results_folder_resolver('quadratic_scatter_results', data) == (
        data / 'quadratic_scatter_results')
    assert results_folder_resolver(f'"{elsewhere}"', data) == elsewhere
    assert results_folder_checker('quadratic_scatter_results', data) is None
    (data / 'notes.txt').write_text('')
    assert results_folder_checker('notes.txt', data) == ('Type or drag in a folder, '
                                                         'not a file.')

    # ---- 2 Count the files with results ----------------------------------------------
    results = data / 'results'
    summaries = [{'name': 'run1'}, {'name': 'run2'}, {'name': 'run3'}]
    assert results_counter(results, summaries) == 0
    (results / 'run1').mkdir(parents=True)
    (results / 'run1' / 'run1.xlsx').write_text('')
    (results / 'run2').mkdir()
    (results / 'logs').mkdir()
    (results / 'logs' / 'run.log').write_text('')
    assert results_counter(results, summaries) == 1

    # ---- 3 A free name beside the folder ---------------------------------------------
    assert free_folder_finder(results) == data / 'results_2'
    (data / 'results_2').mkdir()
    assert free_folder_finder(results) == data / 'results_3'


# ---- test_results_folder_outside_is_kept_whole ---------------------------------------
def test_results_folder_outside_is_kept_whole(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a results folder outside the dataset folder is written
    and read back as its full path.

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

    dataset, results = tmp_path / 'dataset', tmp_path / 'results'
    dataset.mkdir()
    assert dataset_settings_saver(dataset, results, FILES, ANSWERS)
    assert dataset_settings_reader(dataset)['export_folder'] == results.resolve()


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
    assert dataset_settings_saver(tmp_path, tmp_path / 'results', files, ANSWERS)
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
    old = dict(ANSWERS, haem_mode='conc', ho_haem_mode='conc')
    assert dataset_settings_saver(tmp_path, tmp_path / 'results', FILES, old)
    answers = dataset_settings_reader(tmp_path)['answers']
    assert answers == dict(ANSWERS, haem_mode='delta', ho_haem_mode='delta')


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

    assert dataset_settings_saver(tmp_path, tmp_path / 'results', FILES, ANSWERS)
    saved = dataset_settings_reader(tmp_path)
    assert saved['files'] == FILES
    assert saved['answers'] == ANSWERS


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
    assert not dataset_settings_saver(missing, missing / 'results', FILES, ANSWERS)
