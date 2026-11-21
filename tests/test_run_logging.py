"""
Tests the run's log, which keeps the answers from the results folder on, and the
start-up log, which keeps the starts before.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import builtins
import sys
from pathlib import Path
from typing import Callable, List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared import questions
from utils_shared.questions import UserQuitError, yes_no_asker
from utils_shared.run_logging import (answer_logger,
                                      logging_starter,
                                      logging_stopper,
                                      settings_logger,
                                      )
from utils_shared.user_places import LAUNCH_LOG_START, launch_log_opener


# ---- CONSTANTS -----------------------------------------------------------------------
TITLE = 'Portimao test V1.0'


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _typist_maker -------------------------------------------------------------------
def _typist_maker(typed: List[str]) -> Callable[..., str]:
    """
    ---- Summary ----
    Helper function to make a stand-in for the window's answer box: it gives the typed
    answers in turn, then ends the input as closing the window does.

    ---- Inputs ----
    typed : List[str]
        The answers, in order; the list is emptied as they are given.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Callable[..., str]
        Function that takes the place of input.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    def typist(prompt: str = '') -> str:
        if not typed:
            raise EOFError
        return typed.pop(0)

    return typist


# ---- _fresh_numbering ----------------------------------------------------------------
@pytest.fixture
def _fresh_numbering(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Helper function (a pytest fixture) to give the questions their own numbering while
    a test runs, so other tests keep theirs.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the numbering back after the test.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Replaces the questions' counters while the test runs.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    monkeypatch.setattr(questions, '_counters', [0] * questions.MAX_DEPTH)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_answers_are_logged_as_they_come --------------------------------------------
def test_answers_are_logged_as_they_come(tmp_path: Path,
                                         monkeypatch: pytest.MonkeyPatch,
                                         _fresh_numbering: None,
                                         ) -> None:
    """
    ---- Summary ----
    Main function to check that the log starts with the version and the folders, then
    holds each question with its answer under it, without the window's colour codes,
    then the settings, and only then what the run prints.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for the answer box.
    _fresh_numbering : None
        Gives the questions their own numbering.

    ---- Globals read ----
    TITLE (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _typist_maker
    answer_logger
    logging_starter
    logging_stopper
    settings_logger
    yes_no_asker
    """

    monkeypatch.setattr(builtins, 'input', _typist_maker(['maybe', 'n']))
    session = logging_starter(tmp_path / 'results', TITLE, tmp_path / 'data')
    try:
        is_full = yes_no_asker('Do you want every table?', True)
        settings_logger(session, {'export_full': is_full})
        print('Processing run 1')
    finally:
        logging_stopper(session)
    answer_logger('> given after the run')
    lines = session['log_path'].read_text(encoding='utf-8').splitlines()
    assert lines[:4] == [TITLE,
                         'Random seed: none (the program does not use random numbers)',
                         f"Data folder: {tmp_path / 'data'}",
                         f"Results folder: {tmp_path / 'results'}",
                         ]
    assert not any('\x1b' in line for line in lines)
    question = next(i for i, line in enumerate(lines) if 'every table' in line)
    assert lines[question + 1:question + 4] == ['> maybe',
                                                'Type y or n.',
                                                '> n',
                                                ]
    assert lines.index('Settings:') > question + 3
    assert lines[lines.index('Settings:') + 1] == '  export_full: false'
    assert lines.index('Processing run 1') > lines.index('Settings:')
    assert '> given after the run' not in lines


# ---- test_closed_window_keeps_the_log ------------------------------------------------
def test_closed_window_keeps_the_log(tmp_path: Path,
                                     monkeypatch: pytest.MonkeyPatch,
                                     _fresh_numbering: None,
                                     ) -> None:
    """
    ---- Summary ----
    Main function to check that when the window is closed part way through the
    questions, the answers given so far stay in the log, which is closed and gives the
    terminal back.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for the answer box.
    _fresh_numbering : None
        Gives the questions their own numbering.

    ---- Globals read ----
    TITLE (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _typist_maker
    logging_starter
    logging_stopper
    yes_no_asker
    """

    monkeypatch.setattr(builtins, 'input', _typist_maker(['y']))
    console = sys.stdout
    session = logging_starter(tmp_path, TITLE, tmp_path)
    try:
        with pytest.raises(UserQuitError):
            yes_no_asker('First question?')
            yes_no_asker('Second question?')
    finally:
        logging_stopper(session)
    text = session['log_path'].read_text(encoding='utf-8')
    assert 'First question?' in text and '> y' in text
    assert 'Second question?' in text and 'Settings:' not in text
    assert session['closed'] and sys.stdout is console


# ---- test_launch_log_keeps_the_starts_before -----------------------------------------
def test_launch_log_keeps_the_starts_before(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that each start is added to the launch log under its own
    start line, after the starts before.

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
    launch_log_opener
    """

    path = tmp_path / 'logs' / 'launch.log'
    for text in ('first start', 'second start'):
        with launch_log_opener(path) as log:
            log.write(f'{text}\n')
    lines = path.read_text(encoding='utf-8').splitlines()
    assert lines[0].startswith(LAUNCH_LOG_START)
    assert lines[1] == 'first start'
    assert lines[2] == '' and lines[3].startswith(LAUNCH_LOG_START)
    assert lines[4] == 'second start'


# ---- test_launch_log_is_cut_past_its_limit -------------------------------------------
def test_launch_log_is_cut_past_its_limit(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a launch log past its limit keeps only its newest
    half, from a start line, before the new start is added.

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
    launch_log_opener
    """

    path = tmp_path / 'launch.log'
    starts = [f'{LAUNCH_LOG_START} start {number} ====\n' + 'output line\n' * 5
              for number in range(1, 11)
              ]
    path.write_text('\n'.join(starts), encoding='utf-8')
    limit = len(path.read_bytes()) - 1
    with launch_log_opener(path, limit) as log:
        log.write('newest start\n')
    text = path.read_text(encoding='utf-8')
    assert text.startswith(f'{LAUNCH_LOG_START} start ')
    assert 'start 1 ====' not in text and 'start 10 ====' in text
    assert text.rstrip().endswith('newest start')
    assert len(text.encode('utf-8')) < limit
