"""
Tests of the developer's Flag button: the dev copy check and what a flag saves.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import utils_shared.run_logging as run_logging
from utils_shared.run_logging import (details_place_setter,
                                      logging_starter,
                                      logging_stopper,
                                      )
from utils_shared.user_places import LAUNCH_LOG_NAME, LAUNCH_LOG_START
from utils_viewer.viewer_flag import (dev_copy_checker,
                                      flag_canceller,
                                      flag_folder_maker,
                                      flag_saver,
                                      LOG_NAME,
                                      NOTE_NAME,
                                      screen_saver,
                                      )


# ---- CONSTANTS -----------------------------------------------------------------------
MOMENT = datetime(2026, 11, 25, 14, 3, 12)
DETAILS = {'version': '2.29',
           'file': 'control-run1.paf',
           'step': 'Processing: Haems',
           'guide_text': '4.1 Which fit do you want to use?',
           }


# ---- _FakePicture --------------------------------------------------------------------
class _FakePicture:
    """
    ---- Summary ----
    Stands in for a picture of the screen: saving it writes a few bytes.

    ---- Attributes ----
    None.

    ---- Globals read ----
    None.

    ---- Methods ----
    save
    """

    # ---- save ------------------------------------------------------------------------
    def save(self, path: Path) -> None:
        """
        ---- Summary ----
        Method to write a few bytes where the picture goes.

        ---- Inputs ----
        path : Path
            Where the picture goes.

        ---- Globals read ----
        None.

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

        Path(path).write_bytes(b'picture')


# ---- HELPERS -------------------------------------------------------------------------


# ---- _no_run_log ---------------------------------------------------------------------
@pytest.fixture
def _no_run_log() -> Iterator[None]:
    """
    ---- Summary ----
    Helper function to start each test with no run being logged, and to give back where
    the details of a problem went before it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    run_logging._details_targets (module state).

    ---- Outputs ----
    Iterator[None]
        Nothing, once.

    ---- Globals mutated ----
    run_logging._details_targets (module state), restored at the end.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    before = dict(run_logging._details_targets)
    run_logging._details_targets['session'] = None
    yield
    run_logging._details_targets.update(before)


# ---- _raising_grabber ----------------------------------------------------------------
def _raising_grabber(**kwargs: Any) -> Any:
    """
    ---- Summary ----
    Helper function to stand in for a computer that gives no picture of the screen.

    ---- Inputs ----
    **kwargs : Any
        The part of the screen asked for (unused).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Any
        Never returns.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    raise OSError('X connection failed')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_dev_copy_needs_both_marks --------------------------------------------------
def test_dev_copy_needs_both_marks(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that only a folder with both `.style/VERSION` and
    `_USER_REVIEW/` counts as the developer's copy.

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
    dev_copy_checker
    """

    assert not dev_copy_checker(tmp_path)
    (tmp_path / '.style').mkdir()
    (tmp_path / '.style' / 'VERSION').write_text('2.29', encoding='utf-8')
    assert not dev_copy_checker(tmp_path)  # main from git has no _USER_REVIEW
    (tmp_path / '_USER_REVIEW').mkdir()
    assert dev_copy_checker(tmp_path)
    (tmp_path / '.style' / 'VERSION').unlink()
    assert not dev_copy_checker(tmp_path)


# ---- test_flag_folder_is_named_by_its_time -------------------------------------------
def test_flag_folder_is_named_by_its_time(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a flag's folder goes in the inbox under its time, and a
    second flag in the same second gets its own folder.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    MOMENT (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    flag_folder_maker
    """

    first = flag_folder_maker(tmp_path, MOMENT)
    second = flag_folder_maker(tmp_path, MOMENT)
    inbox = tmp_path / '_USER_REVIEW' / 'inbox'
    assert first == inbox / 'flag_2026_11_25-14_03_12'
    assert second == inbox / 'flag_2026_11_25-14_03_12_2'
    assert first.is_dir() and second.is_dir()


# ---- test_flag_keeps_the_run_log_with_its_line ---------------------------------------
def test_flag_keeps_the_run_log_with_its_line(tmp_path: Path,
                                              _no_run_log: None,
                                              ) -> None:
    """
    ---- Summary ----
    Main function to check that a flag saved during a run writes its FLAG line into the
    run's log, copies that log beside the note, and that the note holds the comment and
    what was on screen.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    _no_run_log : None
        Starts with no run being logged.

    ---- Globals read ----
    DETAILS, MOMENT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    flag_folder_maker
    flag_saver
    logging_starter
    logging_stopper
    """

    folder = flag_folder_maker(tmp_path, MOMENT)
    session = logging_starter(tmp_path / 'results', 'Portimao dev V2.29', tmp_path)
    try:
        has_log = flag_saver(folder,
                             'The legend\ncovers the trace.',
                             DETAILS,
                             MOMENT,
                             tmp_path / 'missing.log',
                             )
    finally:
        logging_stopper(session)
    flag_line = ('==== FLAG 14:03:12 (flag_2026_11_25-14_03_12): The legend covers '
                 'the trace. ===='
                 )
    assert has_log
    copy = (folder / LOG_NAME).read_text(encoding='utf-8')
    assert copy.startswith('Portimao dev V2.29\n')
    assert flag_line in copy
    assert flag_line in session['log_path'].read_text(encoding='utf-8')
    note = (folder / NOTE_NAME).read_text(encoding='utf-8')
    assert note.startswith(
        '# Flag 2026-11-25 14:03:12\n\nThe legend\ncovers the trace.',
        )
    assert '- File shown: control-run1.paf' in note
    assert '- Step: Processing: Haems' in note
    assert '- Log: log.txt' in note
    assert '4.1 Which fit do you want to use?' in note


# ---- test_flag_keeps_only_this_start_of_the_launch_log -------------------------------
def test_flag_keeps_only_this_start_of_the_launch_log(tmp_path: Path,
                                                      _no_run_log: None,
                                                      ) -> None:
    """
    ---- Summary ----
    Main function to check that before a run is logged, the flag's line goes into the
    start-up log and only this start of it is copied.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    _no_run_log : None
        Starts with no run being logged.

    ---- Globals read ----
    DETAILS, MOMENT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    details_place_setter
    flag_folder_maker
    flag_saver
    """

    launch_log = tmp_path / LAUNCH_LOG_NAME
    launch_log.write_text(f'{LAUNCH_LOG_START} 2026-11-24\nold start\n'
                          f'{LAUNCH_LOG_START} 2026-11-25\nthis start\n',
                          encoding='utf-8',
                          )
    folder = flag_folder_maker(tmp_path, MOMENT)
    with open(launch_log, 'a', encoding='utf-8') as stream:
        details_place_setter(stream, 'the start-up log')
        assert flag_saver(folder, '', DETAILS, MOMENT, launch_log)
    copy = (folder / LOG_NAME).read_text(encoding='utf-8')
    assert copy.startswith(f'{LAUNCH_LOG_START} 2026-11-25\nthis start\n')
    assert 'old start' not in copy
    assert '(no comment) ====' in copy


# ---- test_flag_without_a_log ---------------------------------------------------------
def test_flag_without_a_log(tmp_path: Path, _no_run_log: None) -> None:
    """
    ---- Summary ----
    Main function to check that a flag with no log to copy (started from a terminal)
    still saves its note, which says no log was found.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    _no_run_log : None
        Starts with no run being logged.

    ---- Globals read ----
    DETAILS, MOMENT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    details_place_setter
    flag_folder_maker
    flag_saver
    """

    details_place_setter(None, '')
    folder = flag_folder_maker(tmp_path, MOMENT)
    assert not flag_saver(folder, 'odd', DETAILS, MOMENT, tmp_path / 'missing.log')
    assert not (folder / LOG_NAME).exists()
    assert '- Log: none found' in (folder / NOTE_NAME).read_text(encoding='utf-8')


# ---- test_cancel_removes_the_flag ----------------------------------------------------
def test_cancel_removes_the_flag(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that Cancel removes the flag's folder and its picture.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    MOMENT (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    flag_canceller
    flag_folder_maker
    """

    folder = flag_folder_maker(tmp_path, MOMENT)
    (folder / 'screen.png').write_bytes(b'picture')
    flag_canceller(folder)
    assert not folder.exists()
    assert (tmp_path / '_USER_REVIEW' / 'inbox').is_dir()


# ---- test_screen_picture_saved_or_not ------------------------------------------------
def test_screen_picture_saved_or_not(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the picture is saved with the part of the screen asked
    for, and that a computer giving no picture leaves no file and says so.

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
    _raising_grabber
    screen_saver
    """

    asked = {}

    def grabber(**kwargs: Any) -> _FakePicture:
        asked.update(kwargs)
        return _FakePicture()

    path = tmp_path / 'screen.png'
    assert screen_saver(path, (10, 20, 810, 620), grabber)
    assert path.read_bytes() == b'picture'
    assert asked['bbox'] == (10, 20, 810, 620)
    other = tmp_path / 'other.png'
    assert not screen_saver(other, (0, 0, 1, 1), _raising_grabber)
    assert not other.exists()
