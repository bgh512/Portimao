"""
Tests of the plots and workbooks saved once the processing and figure of each file are accepted: every file saved once and shown in the window, a failed file, the run not writing a saved plot or workbook again, and the sentence when the run is cancelled.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import main as program
from utils_shared.figure_page import FigurePage, page_plainer, PagePlot, plot_placer
from utils_shared.questions import UserQuitError
from utils_shared.run_logging import details_place_setter


# ---- CONSTANTS -----------------------------------------------------------------------
NAMES = ['run1', 'run2', 'run3']


# ---- FakeWindow ----------------------------------------------------------------------
class FakeWindow:
    """
    ---- Summary ----
    Stand-in for the browser window that only notes the saved plots it is given.

    ---- Attributes ----
    shown : List[Tuple[str, bytes]]
        (file name, picture) of each saved plot, in the order given.

    ---- Globals read ----
    None.

    ---- Methods ----
    __init__
    saved_plot_publisher
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self) -> None:
        """
        ---- Summary ----
        Method to start with no plot shown.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the attribute on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.shown: List[Tuple[str, bytes]] = []

    # ---- saved_plot_publisher --------------------------------------------------------
    def saved_plot_publisher(self, name: str, png: bytes) -> None:
        """
        ---- Summary ----
        Method to note a saved plot, as the window's own method of this name shows it.

        ---- Inputs ----
        name : str
            Name of the file.
        png : bytes
            Picture of the saved plot.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Adds to ``shown``.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.shown.append((name, png))


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _context_builder ----------------------------------------------------------------
def _context_builder(export_root: Path) -> dict:
    """
    ---- Summary ----
    Helper function to build the answers so far of a made-up dataset of three files,
    as everything_asker hands them to experiment_files_saver.

    ---- Inputs ----
    export_root : Path
        Results folder.

    ---- Globals read ----
    NAMES (module constant); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    dict
        {answers, fit, summaries, limits, details, regions, export_root, has_spectra}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _summaries_builder
    """

    return {'answers': dict(settings.DEFAULT_ANSWERS, decompose=False),
            'fit': None,
            'summaries': _summaries_builder(),
            'limits': {},
            'details': {},
            'regions': {},
            'export_root': export_root,
            'has_spectra': False,
            }


# ---- _questions_stander --------------------------------------------------------------
def _questions_stander(monkeypatch: pytest.MonkeyPatch,
                       starts: bool = True,
                       ) -> List[int]:
    """
    ---- Summary ----
    Helper function to stand in for every question of everything_asker, the window and
    the saving of the plots and workbooks, so only its own steps run: the questions
    about each file give the three made-up files and one fit, the page of the dataset
    figure is built with nothing on it, and the saver names every file as saved.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for the stand-ins.
    starts : bool
        The answer to "Do you want to start?".

    ---- Globals read ----
    NAMES (module constant).

    ---- Outputs ----
    List[int]
        A list that gets one entry each time the plots and workbooks of the files are
        saved.

    ---- Globals mutated ----
    None. Replaces names of main.py for the test (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    fit = {'haem_list': [], 'data': None}
    limits = {name: {'trim_start': None,
                     'trim_end': None,
                     'ignore_start': 0.0,
                     'ignore_end': 0.0,
                     }
              for name in NAMES
              }
    saves: List[int] = []

    def files_saver(_context: dict,
                    saved_plots: List[str],
                    _window: object,
                    saved_workbooks: Optional[List[str]] = None,
                    ) -> None:
        saves.append(1)
        saved_plots[:] = NAMES
        if saved_workbooks is not None:
            saved_workbooks[:] = NAMES

    stand_ins = {'viewer_asker': lambda *args: (limits,
                                                fit,
                                                {name: {} for name in NAMES},
                                                True,
                                                {},
                                                False,
                                                ),
                 'page_stage_runner': lambda *args: FigurePage(),
                 'setup_stage_runner': lambda *args: {'group_names': ['', ''],
                                                      'colours': {},
                                                      'rows': [],
                                                      },
                 'yes_no_asker': lambda *args, **kwargs: starts,
                 'experiment_files_saver': files_saver,
                 'guide_step_starter': lambda *args: None,
                 'active_gui_getter': lambda: None,
                 'section_starter': lambda *args: None,
                 'last_answers_saver': lambda *args: None,
                 'dataset_settings_saver': lambda *args: True,
                 'file_settings_merger': lambda *args: {},
                 }
    for name, stand_in in stand_ins.items():
        monkeypatch.setattr(program, name, stand_in)
    return saves


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


# ---- _summaries_builder --------------------------------------------------------------
def _summaries_builder() -> List[dict]:
    """
    ---- Summary ----
    Helper function to build the summaries of the three made-up files.

    ---- Inputs ----
    None.

    ---- Globals read ----
    NAMES (module constant).

    ---- Outputs ----
    List[dict]
        [{name, path, duration_min}], one per file.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [{'name': name, 'path': Path(f'{name}.paf'), 'duration_min': 30.0}
            for name in NAMES
            ]


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_failed_file_does_not_stop_the_others -------------------------------------
def test_a_failed_file_does_not_stop_the_others(tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch,
                                                capsys: pytest.CaptureFixture,
                                                _quiet_details: io.StringIO,
                                                ) -> None:
    """
    ---- Summary ----
    Main function to check a file that cannot be read: the files after it are still
    saved and shown, it is left out of the saved plots and workbooks, and the user is
    told in one sentence, with Python's own words in the log only. The saving of one
    file is stood in for.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the saving of one plot.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.
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
    _context_builder
    """

    def saver(info: dict, *_args: object) -> Tuple[bytes, bool]:
        if info['name'] == 'run2':
            raise RuntimeError('made-up detail')
        return b'picture of ' + info['name'].encode(), True

    monkeypatch.setattr(program, 'experiment_file_saver', saver)
    window = FakeWindow()
    saved_plots: List[str] = []
    saved_workbooks: List[str] = []
    program.experiment_files_saver(_context_builder(tmp_path),
                                   saved_plots,
                                   window,
                                   saved_workbooks,
                                   )
    assert saved_plots == saved_workbooks == ['run1', 'run3']
    assert [name for name, _ in window.shown] == ['run1', 'run3']
    shown = capsys.readouterr().out
    assert ('  The plot and the workbook of run2 were not saved (they are tried again '
            'when the run starts)'
            ) in shown
    assert 'made-up detail' not in shown
    assert 'made-up detail' in _quiet_details.getvalue()


# ---- test_a_file_with_nothing_to_plot_is_not_saved -----------------------------------
def test_a_file_with_nothing_to_plot_is_not_saved(tmp_path: Path,
                                                  monkeypatch: pytest.MonkeyPatch,
                                                  ) -> None:
    """
    ---- Summary ----
    Main function to check the saving of one file: with a panel to plot, the plot is
    drawn once into the results folder and a PNG picture of it is handed back; with no
    oxygen, no OCR and no haems, nothing is drawn and None is handed back; the
    workbook is written either way, with the spectra only when asked for; the slim
    copy of the file is kept for the dataset figure when a place for it is given. The
    reading, the plot and the workbook are stood in for.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the reading and the plot.

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

    # ---- 1 A made-up file, its reading and its plot stood in for ---------------------
    experiment = {'experiment_name': 'run1', 'metadata': {}}
    drawn = []

    def plotter(given: dict, _config: dict, folder: Path, figure: Figure) -> None:
        drawn.append((given, folder, isinstance(figure, Figure)))

    monkeypatch.setattr(program,
                        'experiment_data_processor',
                        lambda *args: {'experiment': experiment,
                                       'od_available': False,
                                       'vo2_source': 'raw',
                                       'haem_source': None,
                                       'plotted_haem_source': None,
                                       },
                        )
    monkeypatch.setattr(program, 'experiment_plotter', plotter)
    written = []
    monkeypatch.setattr(program,
                        'experiment_workbook_exporter',
                        lambda given, folder, **kwargs: written.append((given, folder, kwargs),
                                                                       ),
                        )
    info = {'name': 'run1',
            'ignore_start': 5.0,
            'ignore_end': 0.0,
            'write_spectra': True,
            'has_spectra_csv': False,
            }

    # ---- 2 With the oxygen plotted: drawn once, a PNG picture, the workbook ----------
    answers = dict(settings.DEFAULT_ANSWERS, decompose=False, plot_o2=True)
    picture, is_written = program.experiment_file_saver(info,
                                                        settings.Config(answers),
                                                        None,
                                                        tmp_path,
                                                        )
    assert drawn == [(experiment, tmp_path, True)]
    assert picture[:8] == b'\x89PNG\r\n\x1a\n'
    assert is_written
    assert written == [(experiment,
                        tmp_path,
                        {'spectra': True, 'keeps_spectra_list': False},
                        ),
                       ]
    assert experiment['metadata']['ignore_first_minutes'] == 5.0

    # ---- 3 With nothing plotted: not drawn, no picture, the workbook still -----------
    answers.update(plot_o2=False, plot_ocr=False, plot_haems=False)
    kept: dict = {}
    picture, is_written = program.experiment_file_saver(dict(info, write_spectra=False),
                                                        settings.Config(answers),
                                                        None,
                                                        tmp_path,
                                                        kept,
                                                        )
    assert picture is None and is_written
    assert len(drawn) == 1
    assert written[-1][2] == {'spectra': False, 'keeps_spectra_list': False}
    # the slim copy of the file is kept for the dataset figure
    assert kept == {'run1': {'experiment_name': 'run1',
                             'metadata': experiment['metadata'],
                             'difference': None,
                             'difference_parts': None,
                             'haem_bands': None,
                             'region_spectra': None,
                             },
                    }


# ---- test_a_failed_plot_still_writes_the_workbook ------------------------------------
def test_a_failed_plot_still_writes_the_workbook(tmp_path: Path,
                                                 monkeypatch: pytest.MonkeyPatch,
                                                 capsys: pytest.CaptureFixture,
                                                 _quiet_details: io.StringIO,
                                                 ) -> None:
    """
    ---- Summary ----
    Main function to check one file whose plot cannot be drawn: no picture is handed
    back, the user is told in one sentence, and the workbook is still written; and one
    whose workbook cannot be written (open in Excel): False is handed back, with its
    sentence. The reading, the plot and the workbook are stood in for.

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

    # ---- plotter ---------------------------------------------------------------------
    def plotter(*_args: object) -> None:
        raise RuntimeError('made-up plot detail')

    monkeypatch.setattr(program,
                        'experiment_data_processor',
                        lambda *args: {'experiment': {'metadata': {}},
                                       'od_available': False,
                                       'vo2_source': 'raw',
                                       'plotted_haem_source': None,
                                       },
                        )
    monkeypatch.setattr(program, 'experiment_plotter', plotter)
    written = []
    monkeypatch.setattr(program,
                        'experiment_workbook_exporter',
                        lambda *args, **kwargs: written.append(1),
                        )
    info = {'name': 'run1', 'ignore_start': 0.0, 'ignore_end': 0.0}
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS, decompose=False, plot_o2=True))
    picture, is_written = program.experiment_file_saver(info, cfg, None, tmp_path)
    assert picture is None and is_written and written == [1]
    shown = capsys.readouterr().out
    assert ('  The plot of run1 was not saved (it is tried again when the run starts)'
            ) in shown
    assert 'made-up plot detail' not in shown

    # ---- exporter --------------------------------------------------------------------
    def exporter(*_args: object, **_kwargs: object) -> None:
        raise PermissionError('made-up workbook detail')

    monkeypatch.setattr(program, 'experiment_workbook_exporter', exporter)
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS,
                               decompose=False,
                               plot_o2=False,
                               plot_ocr=False,
                               plot_haems=False,
                               ),
                          )
    picture, is_written = program.experiment_file_saver(info, cfg, None, tmp_path)
    assert picture is None and not is_written
    assert ('  The workbook of run1 was not saved (it is tried again when the run '
            'starts)') in capsys.readouterr().out


# ---- test_a_saved_plot_is_not_drawn_again --------------------------------------------
def test_a_saved_plot_is_not_drawn_again(tmp_path: Path,
                                         monkeypatch: pytest.MonkeyPatch,
                                         capsys: pytest.CaptureFixture,
                                         ) -> None:
    """
    ---- Summary ----
    Main function to check the run of one file: a file whose plot and workbook were
    saved once its figure was accepted is not drawn or written a second time, and says
    so; a file whose were not is drawn and written. The reading, the plot and the
    workbook are stood in for.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the reading, the plot and the workbook.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.

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

    # ---- 1 A made-up file, with the plots counted ------------------------------------
    experiment = {'experiment_name': 'run1', 'metadata': {}, 'raw_spectra': {}}
    drawn = []
    monkeypatch.setattr(program,
                        'experiment_data_processor',
                        lambda *args: {'experiment': experiment,
                                       'od_available': False,
                                       'vo2_source': 'raw',
                                       'haem_source': None,
                                       'plotted_haem_source': None,
                                       },
                        )
    monkeypatch.setattr(program, 'experiment_plotter', lambda *args: drawn.append(1))
    written = []
    monkeypatch.setattr(program,
                        'experiment_workbook_exporter',
                        lambda *a, **k: written.append(1),
                        )
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS, decompose=False, plot_o2=True))
    info = {'name': 'run1', 'ignore_start': 0.0, 'ignore_end': 0.0}

    # ---- 2 Saved already: not drawn or written again ---------------------------------
    program.experiment_processor(dict(info, is_plot_saved=True, is_workbook_saved=True),
                                 cfg,
                                 None,
                                 tmp_path,
                                 )
    assert drawn == [] and written == []
    shown = capsys.readouterr().out
    assert '  Plot already saved.' in shown
    assert '  Workbook already saved.' in shown

    # ---- 3 Not saved: drawn and written ----------------------------------------------
    program.experiment_processor(dict(info, is_plot_saved=False), cfg, None, tmp_path)
    assert drawn == [1] and written == [1]
    shown = capsys.readouterr().out
    assert 'Plot already saved' not in shown and 'Workbook already saved' not in shown


# ---- test_every_file_is_saved_once_and_shown -----------------------------------------
def test_every_file_is_saved_once_and_shown(tmp_path: Path,
                                            monkeypatch: pytest.MonkeyPatch,
                                            capsys: pytest.CaptureFixture,
                                            ) -> None:
    """
    ---- Summary ----
    Main function to check the saving of the plots and workbooks of a dataset of three
    files: each file is saved once, in order, into the results folder; the window is
    given the picture of each; the lists of saved plots and workbooks are emptied first
    and then name every file; the spectra are written the first time only; a file with
    nothing to plot is left out of the plots; and the terminal counts the files. The
    saving of one file is stood in for.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the saving of one plot.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.

    ---- Globals read ----
    NAMES (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _context_builder
    """

    # ---- 1 Every file saved once and shown -------------------------------------------
    calls = []

    def saver(info: dict,
              _cfg: object,
              fit: object,
              folder: Path,
              _page_experiments: object,
              ) -> Tuple[bytes, bool]:
        calls.append((info['name'],
                      fit,
                      folder,
                      info['write_spectra'],
                      info['has_spectra_csv'],
                      ),
                     )
        return b'picture of ' + info['name'].encode(), True

    monkeypatch.setattr(program, 'experiment_file_saver', saver)
    window = FakeWindow()
    saved_plots = ['left from before']
    saved_workbooks = ['left from before']
    context = _context_builder(tmp_path)
    context['answers']['export_spectra'] = True
    program.experiment_files_saver(context, saved_plots, window, saved_workbooks)
    assert calls == [(name, None, tmp_path, True, False) for name in NAMES]
    assert saved_plots == saved_workbooks == NAMES
    assert window.shown == [('run1', b'picture of run1'),
                            ('run2', b'picture of run2'),
                            ('run3', b'picture of run3'),
                            ]
    shown = capsys.readouterr().out
    assert 'Saving file 1 of 3: run1' in shown
    assert 'Saving file 3 of 3: run3' in shown

    # ---- 2 Saved again: the spectra are not written a second time, only listed -------
    calls.clear()
    program.experiment_files_saver(context, saved_plots, window, saved_workbooks)
    assert calls == [(name, None, tmp_path, False, True) for name in NAMES]

    # ---- 3 A file with nothing to plot is left out, and no window is needed ----------
    monkeypatch.setattr(program,
                        'experiment_file_saver',
                        lambda info, *args: (None if info['name'] == 'run2' else b'p',
                                             True,
                                             ),
                        )
    program.experiment_files_saver(_context_builder(tmp_path), saved_plots, None)
    assert saved_plots == ['run1', 'run3']


# ---- test_the_cancel_sentence --------------------------------------------------------
def test_the_cancel_sentence(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check what a cancelled run says it left in the results folder:
    nothing, the exported data, the saved plots, the saved workbooks, or several.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.

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

    builder = program.cancel_sentence_builder
    assert builder([], [], tmp_path) == 'Nothing was changed'
    assert builder([tmp_path], [], tmp_path) == (
        f'The data you exported is kept in {tmp_path}; nothing else was changed'
        )
    assert builder([], ['run1'], tmp_path) == (
        f'The plots of your files are kept in {tmp_path}; nothing else was changed'
        )
    assert builder([tmp_path], ['run1'], tmp_path) == (
        f'The data you exported and the plots of your files are kept in {tmp_path}; '
        f'nothing else was changed'
        )
    assert builder([], [], tmp_path, ['run1']) == (
        f'The workbooks of your files are kept in {tmp_path}; nothing else was changed'
        )
    assert builder([tmp_path], ['run1'], tmp_path, ['run1']) == (
        f'The data you exported and the plots and workbooks of your files are kept in '
        f'{tmp_path}; nothing else was changed'
        )


# ---- test_the_page_is_handed_on_and_saved --------------------------------------------
def test_the_page_is_handed_on_and_saved(tmp_path: Path,
                                         monkeypatch: pytest.MonkeyPatch,
                                         capsys: pytest.CaptureFixture,
                                         ) -> None:
    """
    ---- Summary ----
    Main function to check that the questions hand the page saved with the dataset
    to the Build a figure step, and save the page as built with the settings of the
    dataset once the run is started. Every question, the window and the saving are
    stood in for.

    ---- Inputs ----
    tmp_path : Path
        Data and results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for the stand-ins.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed, which is not checked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _questions_stander
    _summaries_builder
    """

    built = plot_placer(FigurePage(), PagePlot('P9', 0, 0, 2, 2, roles={'bars': 'sd'}))
    before = page_plainer(plot_placer(FigurePage(), PagePlot('P17', 5, 0)))
    given: List[object] = []
    written: List[tuple] = []

    def page_runner(*args: object) -> FigurePage:
        given.append(args[-1])
        return built

    def settings_saver(*args: object) -> bool:
        written.append(args)
        return True

    _questions_stander(monkeypatch)
    monkeypatch.setattr(program, 'page_stage_runner', page_runner)
    monkeypatch.setattr(program, 'dataset_settings_saver', settings_saver)
    page = program.everything_asker(tmp_path,
                                    _summaries_builder(),
                                    tmp_path,
                                    {'page': before},
                                    )[-1]
    assert page == built
    assert given == [before]
    assert written[0][-1] == page_plainer(built)

    # a dataset never saved hands on no page
    given.clear()
    program.everything_asker(tmp_path, _summaries_builder(), tmp_path, {})
    assert given == [None]


# ---- test_the_plots_are_saved_after_the_file_questions -------------------------------
def test_the_plots_are_saved_after_the_file_questions(tmp_path: Path,
                                                      monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture,
                                                      ) -> None:
    """
    ---- Summary ----
    Main function to check when the questions save the plots and when the run draws
    them again: saved once after the questions about each file, and not drawn again in
    the run; and named as saved when the run is cancelled at its last question. Every
    question, the window and the saving are stood in for.

    ---- Inputs ----
    tmp_path : Path
        Data and results folder for the test.
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for the stand-ins.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed, which is not checked.

    ---- Globals read ----
    NAMES (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _questions_stander
    _summaries_builder
    """

    def flags_reader(saved_plots: Optional[List[str]] = None) -> List[bool]:
        page_data: dict = {}
        experiments = program.everything_asker(tmp_path,
                                               _summaries_builder(),
                                               tmp_path,
                                               {},
                                               None,
                                               saved_plots,
                                               None,
                                               page_data,
                                               )[1]
        # the dataset figure is handed the set-up and the slim copy of each file read
        assert page_data == {'setup': {'group_names': ['', ''],
                                       'colours': {},
                                       'rows': [],
                                       },
                             'experiments': {},
                             }
        # the workbook is saved with the plot, so both flags are the same
        assert all(info['is_plot_saved'] == info['is_workbook_saved']
                   for info in experiments
                   )
        return [info['is_plot_saved'] for info in experiments]

    # ---- 1 Nothing changes later: saved once, not drawn again ------------------------
    saves = _questions_stander(monkeypatch)
    assert flags_reader() == [True, True, True]
    assert len(saves) == 1

    # ---- 2 Cancelled at the last question: the saved plots are named -----------------
    _questions_stander(monkeypatch, starts=False)
    saved_plots: List[str] = []
    with pytest.raises(UserQuitError):
        flags_reader(saved_plots)
    assert saved_plots == NAMES
