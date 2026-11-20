"""
Tests of the settings kept with a dataset and of the list of data folders.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.dataset_settings import (dataset_settings_reader,
                                           dataset_settings_saver,
                                           SETTINGS_FILE_NAME,
                                           )
from utils_shared.survey import data_folder_lister, data_folder_resolver


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
    assert dataset_settings_saver(first, first / 'export' / 'run', FILES, ANSWERS)
    text = (first / SETTINGS_FILE_NAME).read_text(encoding='utf-8')
    assert json.loads(text)['export_folder'] == 'export/run'
    (copy / SETTINGS_FILE_NAME).write_text(text, encoding='utf-8')
    assert dataset_settings_reader(copy)['export_folder'] == copy / 'export' / 'run'


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

    assert dataset_settings_saver(tmp_path, tmp_path / 'export', FILES, ANSWERS)
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
    assert not dataset_settings_saver(missing, missing / 'export', FILES, ANSWERS)
