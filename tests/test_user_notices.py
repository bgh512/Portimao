"""
Tests of the plain sentences for warnings and problems, with their details in the log.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import errno
import io
import json
from pathlib import Path
from typing import Callable, Iterator

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.output_capture import output_capturer
from utils_shared.run_logging import (details_place_setter,
                                      details_writer,
                                      logging_starter,
                                      logging_stopper,
                                      )
from utils_shared.trimming import experiment_trimmer
from utils_shared.user_notices import (problem_describer,
                                       problem_shower,
                                       problem_teller,
                                       warning_shower,
                                       )


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _caught_getter ------------------------------------------------------------------
def _caught_getter(action: Callable[[], object]) -> BaseException:
    """
    ---- Summary ----
    Helper function to run an action that fails and give its error, with its traceback.

    ---- Inputs ----
    action : Callable[[], object]
        Function without inputs that raises.

    ---- Globals read ----
    None.

    ---- Outputs ----
    BaseException
        The error it raised.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        action()
    except BaseException as exc:
        return exc
    raise AssertionError('the action did not fail')


# ---- _quiet_details ------------------------------------------------------------------
@pytest.fixture
def _quiet_details() -> Iterator[io.StringIO]:
    """
    ---- Summary ----
    Helper function (a pytest fixture) to send the details of a problem to a made-up
    log while a test runs, and to send them nowhere afterwards.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Iterator[io.StringIO]
        The made-up log, named "the test log" for the user.

    ---- Globals mutated ----
    None. Sets the place for the details, and clears it after the test (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    details_place_setter
    """

    log = io.StringIO()
    details_place_setter(log, 'the test log')
    yield log
    details_place_setter(None, '')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_details_go_to_the_log_only -------------------------------------------------
def test_details_go_to_the_log_only(_quiet_details: io.StringIO,
                                    capsys: pytest.CaptureFixture,
                                    ) -> None:
    """
    ---- Summary ----
    Main function to check that a problem Portimao did not expect gives one sentence
    naming the log, with Python's report of it in the log and nowhere else.

    ---- Inputs ----
    _quiet_details : io.StringIO
        The made-up log.
    capsys : pytest.CaptureFixture
        What the test printed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _caught_getter
    problem_teller
    """

    error = _caught_getter(lambda: {}['CcO2'])
    sentence = problem_teller('Preview not drawn for run1', error)
    assert sentence == ('Preview not drawn for run1: Portimao met a problem it did not '
                        'expect. The details are in the test log: send it through the '
                        'Issues page (see Feedback at the top of the README).'
                        )
    details = _quiet_details.getvalue()
    assert 'Preview not drawn for run1' in details
    assert 'Traceback' in details and 'KeyError' in details
    assert capsys.readouterr().out == ''


# ---- test_own_message_is_shown_as_it_is ----------------------------------------------
def test_own_message_is_shown_as_it_is(_quiet_details: io.StringIO) -> None:
    """
    ---- Summary ----
    Main function to check that a message Portimao's own code wrote for the user (here
    the trimming's, raised over several lines) is shown as it is.

    ---- Inputs ----
    _quiet_details : io.StringIO
        The made-up log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _caught_getter
    experiment_trimmer
    problem_describer
    """

    error = _caught_getter(lambda: experiment_trimmer({'experiment_name': 'run1'},
                                                      start_time=5.0,
                                                      end_time=2.0,
                                                      ),
                           )
    expected = 'run1: the end time (2 min) must be after the start time (5 min).'
    assert problem_describer(error, 'the test log') == expected


# ---- test_python_text_is_never_shown -------------------------------------------------
def test_python_text_is_never_shown(_quiet_details: io.StringIO) -> None:
    """
    ---- Summary ----
    Main function to check that Python's own error text is never shown: neither for a
    plain step in Portimao's code that fails (a time that is not a number, a missing
    name) nor for an error raised inside a package or in a test.

    ---- Inputs ----
    _quiet_details : io.StringIO
        The made-up log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _caught_getter
    experiment_trimmer
    problem_describer
    """

    unexpected = ('Portimao met a problem it did not expect. The details are in the '
                  'test log: send it through the Issues page (see Feedback at the top '
                  'of the README).'
                  )
    for action in (lambda: experiment_trimmer({'experiment_name': 'run1'},
                                              start_time='1,5',
                                              ),
                   lambda: experiment_trimmer({}),
                   lambda: json.loads('{'),
                   lambda: float('1,5'),
                   ):
        assert problem_describer(_caught_getter(action), 'the test log') == unexpected
    no_log = problem_describer(_caught_getter(lambda: [][0]), '')
    assert no_log == ('Portimao met a problem it did not expect: please report it '
                      '(send it through the Issues page (see Feedback at the top of the '
                      'README)).'
                      )


# ---- test_file_problems_say_what_to_do -----------------------------------------------
def test_file_problems_say_what_to_do(tmp_path: Path,
                                      _quiet_details: io.StringIO,
                                      ) -> None:
    """
    ---- Summary ----
    Main function to check the sentences for a file open in another program, a missing
    file, another file problem and a lack of memory: each names the file, without its
    folders, and says what to do.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    _quiet_details : io.StringIO
        The made-up log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _caught_getter
    problem_describer
    """

    def locked() -> None:
        raise PermissionError(errno.EACCES,
                              'Permission denied',
                              str(tmp_path / 'run1.xlsx'),
                              )
    def full() -> None:
        raise OSError(errno.ENOSPC, 'No space left on device.', str(tmp_path / 'a.png'))
    def memory() -> None:
        raise MemoryError()
    assert problem_describer(_caught_getter(locked), '') == (
        'run1.xlsx could not be opened or saved, perhaps because it is open in another '
        'program such as Excel: close it there and try again.'
        )
    missing = _caught_getter(lambda: open(tmp_path / 'missing.paf', encoding='utf-8'))
    assert problem_describer(missing, '') == ('missing.paf could not be found: check '
                                              'that it is still in its folder and try '
                                              'again.'
                                              )
    assert problem_describer(_caught_getter(full), '') == (
        'a.png could not be read or saved (the computer says: No space left on device).'
        )
    assert problem_describer(_caught_getter(memory), '').startswith(
        'The computer ran out of memory',
        )


# ---- test_run_log_takes_the_details --------------------------------------------------
def test_run_log_takes_the_details(tmp_path: Path, _quiet_details: io.StringIO) -> None:
    """
    ---- Summary ----
    Main function to check that while a run is logged the details go to its log, which
    is named for the user, and that afterwards they go back to the start-up place.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest, standing in for the results folder.
    _quiet_details : io.StringIO
        The made-up start-up log.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    details_writer
    logging_starter
    logging_stopper
    """

    session = logging_starter(tmp_path, 'Portimao test', tmp_path)
    try:
        place = details_writer('details of the run')
    finally:
        logging_stopper(session)
    assert place == (f"the log file {session['log_path'].name} (in the logs folder of "
                     f'the results folder)'
                     )
    assert 'details of the run' in session['log_path'].read_text(encoding='utf-8')
    assert details_writer('details after the run') == 'the test log'
    assert 'details after the run' in _quiet_details.getvalue()


# ---- test_warnings_are_kept_whatever_their_words -------------------------------------
def test_warnings_are_kept_whatever_their_words(_quiet_details: io.StringIO,
                                                capsys: pytest.CaptureFixture,
                                                ) -> None:
    """
    ---- Summary ----
    Main function to check that while the output is captured (a preview) every warning
    is kept as a warning, whatever its words, ordinary lines are not, and the details of
    a problem are never printed.

    ---- Inputs ----
    _quiet_details : io.StringIO
        The made-up log.
    capsys : pytest.CaptureFixture
        What the test printed (pytest's own stream does not honour the capture).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _caught_getter
    output_capturer
    problem_shower
    warning_shower
    """

    with output_capturer() as captured:
        print('  Read 100 points, 3 event(s)')
        warning_shower('  Left out of the haem and OCR response: the OD is missing.')
        problem_shower('  Not made', _caught_getter(lambda: [][0]))
    assert captured.warnings[0] == ('Left out of the haem and OCR response: the OD is '
                                    'missing.'
                                    )
    assert captured.warnings[1].startswith('Not made: Portimao met a problem')
    assert len(captured.warnings) == 2
    printed = capsys.readouterr().out
    assert 'Read 100 points' in printed and 'Not made: Portimao met' in printed
    assert 'Traceback' not in printed + captured.getvalue()
    assert 'Traceback' in _quiet_details.getvalue()
