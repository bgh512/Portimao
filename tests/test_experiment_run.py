"""
Tests of the run of one file: a workbook that cannot be saved does not take the file out of the later figures.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import errno
import io
from pathlib import Path
from typing import Iterator

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import main as program
from utils_shared.run_logging import details_place_setter


# ---- TEST HELPERS --------------------------------------------------------------------


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


# ---- test_a_workbook_open_in_excel_keeps_the_file ------------------------------------
def test_a_workbook_open_in_excel_keeps_the_file(tmp_path: Path,
                                                 monkeypatch: pytest.MonkeyPatch,
                                                 capsys: pytest.CaptureFixture,
                                                 _quiet_details: io.StringIO,
                                                 ) -> None:
    """
    ---- Summary ----
    Main function to check the run of a file whose workbook is open in Excel: the file
    is still handed on to the later figures, its name is noted as not saved, and the
    user is told in one sentence to close the workbook, with Python's own words in the
    log only. The reading, the plot and the workbook are stood in for.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the reading, the plot and the workbook.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.
    _quiet_details : io.StringIO
        The made-up log.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 A made-up file whose workbook cannot be written ---------------------------
    experiment = {'experiment_name': 'run1', 'metadata': {}, 'raw_spectra': {}}

    def exporter(*_args: object, **_kwargs: object) -> None:
        raise PermissionError(errno.EACCES,
                              'Permission denied',
                              str(tmp_path / 'run1' / 'run1.xlsx'),
                              )

    monkeypatch.setattr(program,
                        'experiment_data_processor',
                        lambda *args: {'experiment': experiment,
                                       'od_available': False,
                                       'vo2_source': 'raw',
                                       'haem_source': None,
                                       'plotted_haem_source': None,
                                       },
                        )
    monkeypatch.setattr(program, 'experiment_plotter', lambda *args: None)
    monkeypatch.setattr(program, 'experiment_workbook_exporter', exporter)
    monkeypatch.setattr(program,
                        'experiment_preparer',
                        lambda *args: {'time_response': None},
                        )
    info = {'name': 'run1',
            'ignore_start': 5.0,
            'ignore_end': 0.0,
            'custom': {},
            'keep': True,
            }
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS, decompose=False))

    # ---- 2 The file is kept, and named as not saved ----------------------------------
    unsaved = []
    result = program.experiment_processor(info, cfg, None, tmp_path, unsaved)
    assert result == {'experiment': experiment,
                      'vo2_source': 'raw',
                      'haem_source': None,
                      'prepared': {'time_response': None},
                      }
    assert unsaved == ['run1']

    # ---- 3 One plain sentence on screen, Python's words in the log only --------------
    shown = capsys.readouterr().out
    assert ('  The workbook of run1 was not saved (the figures still use this file): '
            'run1.xlsx could not be opened or saved, perhaps because it is open in '
            'another program such as Excel: close it there and try again.'
            ) in shown
    assert 'Permission denied' not in shown
    assert 'Permission denied' in _quiet_details.getvalue()
