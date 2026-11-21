"""
Tests of the parts of the window that need no window: the widths a journal allows, the
check of a typed height, the check of values meant for the strip, the answers shown in
the strip and taken back from it, the reading of one cell of the OD table, the way a
turn of the mouse wheel scrolls, the time axis title of a preview and which files the
window keeps read and redraws.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from types import SimpleNamespace

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_preview as viewer_preview
from utils_viewer.viewer_od_table import cell_reader, wheel_step_finder
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


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_cell_of_the_od_table -------------------------------------------------------
def test_cell_of_the_od_table() -> None:
    """
    ---- Summary ----
    Main function to check that a cell gives its number (with a point or a comma), that
    an empty cell is "not filled in" and not wrong, and that words, zero, negative
    numbers and numbers that are not finite are wrong.

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

    assert cell_reader('1.2') == (pytest.approx(1.2), True)
    assert cell_reader(' 50 ') == (pytest.approx(50.0), True)
    assert cell_reader('0,8') == (pytest.approx(0.8), True)
    assert cell_reader('') == (None, True)
    assert cell_reader('   ') == (None, True)
    for wrong in ('abc', '0', '-1', '1.2.3', 'nan', 'inf'):
        assert cell_reader(wrong) == (None, False)


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
    Main function to check that a turn of the mouse wheel scrolls the OD table the
    right way on Windows (steps of 120), the Mac (small steps) and Linux (buttons 4 and
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
