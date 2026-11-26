"""
Tests of the journal files: the ones that come with the program, a file with a missing
or an impossible number, a journal added by the user, and saved answers fitted to the
journals there are.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Any

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.journal_files import (journal_answers_fitter,
                                        journal_specs_loader,
                                        journals_folder_lister,
                                        )
from utils_shared.user_places import user_places_finder


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
# a journal file with every value in order
MADE_UP = {'name': 'Lab Letters',
           'widths_mm': {'1': 80, '2': 170},
           'tallest_figure_mm': 230,
           'smallest_text_pt': 6,
           'largest_text_pt': 9,
           'panel_letter_pt': 9,
           'panel_letter_case': 'upper',
           'fonts': ['Arial'],
           'thinnest_line_pt': 0.4,
           'thickest_line_pt': None,
           'picture_dpi': 300,
           'page_mm': [210, 297],
           }


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _journal_writer -----------------------------------------------------------------
def _journal_writer(folder: Path, stem: str, **changes: Any) -> None:
    """
    ---- Summary ----
    Helper function to write a made-up journal file, with some of its values changed
    or taken away.

    ---- Inputs ----
    folder : Path
        The journals folder; it is made when missing.
    stem : str
        The file name without its ending.
    **changes : Any
        Values to change; a value of ... takes the entry away.

    ---- Globals read ----
    MADE_UP.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    values = {key: value
              for key, value in dict(MADE_UP, **changes).items()
              if value is not ...
              }
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'{stem}.json').write_text(json.dumps(values), encoding='utf-8')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_shipped_journal_files_are_read ---------------------------------------------
def test_shipped_journal_files_are_read() -> None:
    """
    ---- Summary ----
    Main function to check that every journal file that comes with the program is read
    with no file left out, in the order they are offered, with the numbers of the
    journals' guides.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Science prints in three columns of 57, 121 and 184 mm on a page of 8 1/4 x 10 1/2
    in (209.6 x 266.7 mm); ACS allows 240 points (84.7 mm) and 504 points (177.8 mm)
    and gives no largest text.

    ---- Helpers ----
    journal_specs_loader
    journals_folder_lister
    user_places_finder
    """

    folders = journals_folder_lister(user_places_finder(is_app=False,
                                                        program_folder=ROOT,
                                                        ),
                                     )
    assert folders == [ROOT / 'journals']
    specs, problems = journal_specs_loader(folders)
    assert problems == []
    assert list(specs) == ['nature', 'science', 'cell', 'pnas', 'acs', 'plos_one']
    assert specs['nature']['widths_mm'] == {1: 89, 1.5: 120, 2: 183}
    assert specs['nature']['page_height_mm'] == 170
    assert (specs['nature']['font_min_pt'], specs['nature']['font_max_pt']) == (5, 7)
    assert specs['nature']['paper_mm'] is None
    assert specs['science']['widths_mm'] == {1: 57, 2: 121, 3: 184}
    assert specs['science']['paper_mm'] == (209.6, 266.7)
    assert specs['science']['panel_letter_pt'] == 10
    assert specs['science']['line_min_pt'] == 0.5
    assert specs['cell']['page_height_mm'] == 200
    assert (specs['cell']['line_min_pt'], specs['cell']['line_max_pt']) == (0.5, 1.5)
    assert specs['cell']['font_family'] == ['Arial']
    assert (specs['pnas']['font_min_pt'], specs['pnas']['font_max_pt']) == (6, 12)
    assert specs['acs']['widths_mm'] == {1: 84.7, 2: 177.8}
    assert specs['acs']['font_max_pt'] is None
    assert specs['plos_one']['widths_mm'] == {1: 132, 2: 190.5}
    assert specs['plos_one']['page_height_mm'] == 222.3


# ---- test_journal_file_that_cannot_be_used_is_left_out -------------------------------
def test_journal_file_that_cannot_be_used_is_left_out(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a journal file with a missing number, an impossible
    number, a page smaller than its figures or broken punctuation is left out and
    named in one plain sentence, that the good file beside it is still read, and that
    the standard journal is there even with no file of its own.

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
    _journal_writer
    journal_specs_loader
    """

    folder = tmp_path / 'journals'
    _journal_writer(folder, 'good')
    _journal_writer(folder, 'no_height', tallest_figure_mm=...)
    _journal_writer(folder, 'minus_text', smallest_text_pt=-1)
    _journal_writer(folder, 'small_page', page_mm=[150, 297])
    _journal_writer(folder, 'odd_width', widths_mm={'wide': 170})
    (folder / 'broken.json').write_text('{"name": "Broken"', encoding='utf-8')
    specs, problems = journal_specs_loader([folder])
    assert list(specs) == ['nature', 'good']
    assert specs['good']['name'] == 'Lab Letters'
    assert specs['nature']['widths_mm'] == {1: 89, 1.5: 120, 2: 183}
    end = f'Correct it in {folder}, then open Portimao again.'
    assert problems == [
        'The journal file broken.json is left out: it cannot be read as a .json file '
        f'(a missing comma, bracket or quote mark is the usual reason). {end}',
        "The journal file minus_text.json is left out: its 'smallest_text_pt' (-1) is "
        f'not a number above 0. {end}',
        "The journal file no_height.json is left out: it has no 'tallest_figure_mm'. "
        f'{end}',
        "The journal file odd_width.json is left out: its width 'wide: 170' is not a "
        f'number of columns and a width in mm, both above 0. {end}',
        'The journal file small_page.json is left out: its page is smaller than its '
        f'largest figure. {end}',
        'The journal file nature.json is missing from the journals folder: the '
        'numbers for Nature kept in the program are used.',
        ]


# ---- test_journal_added_by_the_user --------------------------------------------------
def test_journal_added_by_the_user(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a file added to the journals folder is a journal like
    any other, offered after the first four by its name, and that the user's own copy
    of a file is the one read when the program's folder has one of the same name.

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
    _journal_writer
    journal_specs_loader
    """

    own, shipped = tmp_path / 'own', tmp_path / 'shipped'
    _journal_writer(shipped, 'nature', name='Nature')
    _journal_writer(shipped, 'zebra', name='Zebrafish')
    _journal_writer(own, 'zebra', name='Zebrafish', tallest_figure_mm=111)
    _journal_writer(own, 'lab_letters')
    specs, problems = journal_specs_loader([own, shipped, tmp_path / 'not_there'])
    assert problems == []
    assert list(specs) == ['nature', 'lab_letters', 'zebra']
    assert specs['zebra']['page_height_mm'] == 111
    assert specs['lab_letters'] == {'name': 'Lab Letters',
                                    'widths_mm': {1: 80, 2: 170},
                                    'page_height_mm': 230,
                                    'font_min_pt': 6,
                                    'font_max_pt': 9,
                                    'panel_letter_pt': 9,
                                    'panel_letter_case': 'upper',
                                    'font_family': ['Arial'],
                                    'line_min_pt': 0.4,
                                    'line_max_pt': None,
                                    'dpi': 300,
                                    'paper_mm': (210, 297),
                                    }


# ---- test_saved_answers_are_fitted_to_the_journals -----------------------------------
def test_saved_answers_are_fitted_to_the_journals() -> None:
    """
    ---- Summary ----
    Main function to check that a width saved with a dataset that its journal does not
    take becomes the widest it takes that is no wider (the narrowest when there is
    none), that a journal no longer in the folder becomes the standard one, each with
    its sentence, and that answers that fit are left as they are.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Science takes 1, 2 and 3 columns: 1.5 columns saved become 1 column (57 mm). A
    journal taking 2 and 3 columns only: 1 column saved becomes 2 columns (100 mm).

    ---- Helpers ----
    journal_answers_fitter
    """

    specs = {'nature': {'name': 'Nature', 'widths_mm': {1: 89, 1.5: 120, 2: 183}},
             'science': {'name': 'Science', 'widths_mm': {1: 57, 2: 121, 3: 184}},
             'wide': {'name': 'Wide Only', 'widths_mm': {2: 100, 3: 150}},
             }

    # ---- 1 A width the journal does not take -----------------------------------------
    answers = {'journal': 'science', 'columns': 1.5, 'height': 0.5}
    fitted, notes = journal_answers_fitter(answers, specs)
    assert fitted == dict(answers, columns=1)
    assert answers['columns'] == 1.5  # the answers given are not changed
    assert notes == ['Science has no figure 1.5 columns wide: a figure saved at that '
                     'width is now 1 column wide (57 mm).',
                     ]
    assert journal_answers_fitter(fitted, specs) == (fitted, [])

    # ---- 2 A journal that is no longer there -----------------------------------------
    answers = {'journal': 'lancet', 'columns': 1.5, 'height': 0.5}
    fitted, notes = journal_answers_fitter(answers, specs)
    assert fitted == dict(answers, journal='nature')
    assert notes == ["The journal 'lancet' saved with this dataset is not in the "
                     'journals folder: Nature is used in its place.',
                     ]

    # ---- 3 No width as narrow: the narrowest the journal takes -----------------------
    answers = {'journal': 'wide', 'columns': 1, 'height': 0.5}
    fitted, notes = journal_answers_fitter(answers, specs)
    assert fitted == dict(answers, columns=2)
    assert notes == ['Wide Only has no figure 1 column wide: a figure saved at that '
                     'width is now 2 columns wide (100 mm).',
                     ]
