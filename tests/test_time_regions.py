"""
Tests of the boxes above the plot that the program runs: the tabs of the Time regions box, the export buttons of the trim step and the figure step that asks only Continue.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_viewer import viewer_stages
from utils_viewer.viewer_preview import ViewerSession


# ---- FakeWindow ----------------------------------------------------------------------
class FakeWindow:
    """
    ---- Summary ----
    Stand-in for the browser window that keeps the edges put on the plot and notes
    what the program asks of it.

    ---- Attributes ----
    shown : List[Any]
        The edges put on the plot, in order (None when they are taken off).
    edges : Dict[str, Dict[str, float]]
        What edges_reader gives: the edges on the plot as the user left them.
    tabs : List[str]
        The tab of the Time regions box shown after each change.

    ---- Globals read ----
    None.

    ---- Methods ----
    __init__
    edges_hider
    edges_reader
    edges_shower
    strip_choices_setter
    strip_setter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self) -> None:
        """
        ---- Summary ----
        Method to start with no edges on the plot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the attributes on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.shown: List[Any] = []
        self.edges: Dict[str, Dict[str, float]] = {}
        self.tabs: List[str] = []

    # ---- edges_hider -----------------------------------------------------------------
    def edges_hider(self) -> None:
        """
        ---- Summary ----
        Method to note the edges taken off the plot.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the attributes.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.shown.append(None)

    # ---- edges_reader ----------------------------------------------------------------
    def edges_reader(self) -> Dict[str, Dict[str, float]]:
        """
        ---- Summary ----
        Method to give the edges on the plot as the user left them.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Dict[str, Dict[str, float]]
            A copy of the edges.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return {name: dict(own) for name, own in self.edges.items()}

    # ---- edges_shower ----------------------------------------------------------------
    def edges_shower(self, choice: Any) -> None:
        """
        ---- Summary ----
        Method to note the edges put on the plot; their values become those read.

        ---- Inputs ----
        choice : Any
            The edges (an EdgeChoice, or a stand-in with values).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the attributes.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.shown.append(choice)
        self.edges = {name: dict(own) for name, own in choice.values.items()}

    # ---- strip_choices_setter --------------------------------------------------------
    def strip_choices_setter(self, *args: Any) -> None:
        """
        ---- Summary ----
        Method to take what the boxes offer, which is not checked here.

        ---- Inputs ----
        args : Any
            What the boxes offer.

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

    # ---- strip_setter ----------------------------------------------------------------
    def strip_setter(self, values: Dict[str, Any]) -> None:
        """
        ---- Summary ----
        Method to note the tab of the Time regions box shown.

        ---- Inputs ----
        values : Dict[str, Any]
            Some of the values of the boxes.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the attributes.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if 'time_tab' in values:
            self.tabs.append(values['time_tab'])


# ---- FakeChoice ----------------------------------------------------------------------
class FakeChoice:
    """
    ---- Summary ----
    Stand-in for the edges of a step: only their values.

    ---- Attributes ----
    values : Dict[str, Dict[str, float]]
        {file name: {field: value}}.

    ---- Globals read ----
    None.

    ---- Methods ----
    __init__
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, values: Dict[str, Dict[str, float]]) -> None:
        """
        ---- Summary ----
        Method to keep the values.

        ---- Inputs ----
        values : Dict[str, Dict[str, float]]
            {file name: {field: value}}.

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

        self.values = values


# ---- HELPERS -------------------------------------------------------------------------


# ---- _kits_maker ---------------------------------------------------------------------
def _kits_maker(log: List[Tuple[str, Any]]) -> Dict[str, Tuple[Any, Any]]:
    """
    ---- Summary ----
    Helper function to give stand-ins for what each tab does, noting each call.

    ---- Inputs ----
    log : List[Tuple[str, Any]]
        Filled with ('open', tab) and ('apply', tab, edges) in order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Tuple[Any, Any]]
        {tab: (opener, applier)}; the opener of 'windows' gives no edges.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    def kit(tab: str, value: float) -> Tuple[Any, Any]:
        def opener() -> Any:
            log.append(('open', tab))
            return None if tab == 'windows' else FakeChoice({'run1': {'edge': value}})
        def applier(edges: Dict[str, Dict[str, float]]) -> None:
            log.append(('apply', tab, edges))
        return opener, applier
    return {'trim': kit('trim', 1.0),
            'regions': kit('regions', 2.0),
            'windows': kit('windows', 3.0),
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_tab_pressed_away_from_its_step -------------------------------------------
def test_a_tab_pressed_away_from_its_step() -> None:
    """
    ---- Summary ----
    Main function to check the tabs of the Time regions box while the regions step
    waits: Trim / Ignore takes the regions off the plot, kept as the user left them,
    and puts the trim edges on; back to Ox / Red, the trim edges moved are used and
    the regions come back as they were left, with their plot; a tab whose edges cannot
    be shown (no addition for the windows) goes back to the step's tab; and the tab
    already pressed changes nothing.

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
    _kits_maker
    """

    # ---- 1 The regions step waits, its edges moved by the user -----------------------
    window, log, drawn = FakeWindow(), [], []
    session = ViewerSession([], Path('.'), window)
    session.redraw = lambda: drawn.append('regions plot') or True
    kits = _kits_maker(log)
    step = FakeChoice({'run1': {'edge': 5.0}})
    viewer_stages._step_edges_shower(session, 'regions', step)
    window.edges = {'run1': {'edge': 6.0}}

    # ---- 2 Trim / Ignore: the regions kept, the trim edges on ------------------------
    viewer_stages._tab_switcher(session, kits, 'trim')
    assert step.values == {'run1': {'edge': 6.0}}
    assert log == [('open', 'trim')]
    assert session.time_tab == 'trim' and window.tabs[-1] == 'trim'
    window.edges = {'run1': {'edge': 1.5}}
    viewer_stages._tab_switcher(session, kits, 'trim')  # pressed already
    assert log == [('open', 'trim')]

    # ---- 3 Back to Ox / Red: the trim used, the regions back -------------------------
    viewer_stages._tab_switcher(session, kits, 'regions')
    assert log[-1] == ('apply', 'trim', {'run1': {'edge': 1.5}})
    assert window.shown[-1] is step and window.edges == {'run1': {'edge': 6.0}}
    assert drawn == ['regions plot'] and session.time_tab == 'regions'

    # ---- 4 A tab without edges: the step's tab stays ---------------------------------
    viewer_stages._tab_switcher(session, kits, 'windows')
    assert log[-1] == ('open', 'windows')
    assert session.time_tab == 'regions' and window.tabs[-1] == 'regions'
    assert window.shown[-1] is step

    # ---- 5 The step answered: its edges read and taken off ---------------------------
    assert viewer_stages._step_edges_reader(session) == {'run1': {'edge': 6.0}}
    assert session.time_tab == session.step_tab == '' and window.tabs[-1] == ''


# ---- test_a_tab_pressed_while_no_step_has_edges --------------------------------------
def test_a_tab_pressed_while_no_step_has_edges() -> None:
    """
    ---- Summary ----
    Main function to check a tab pressed while a question without edges waits (Δψ,
    say): its edges go on the plot over its own plot, and pressing no tab (the
    question answered) uses them and puts the plot of the question back.

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
    _kits_maker
    """

    window, log, drawn = FakeWindow(), [], []
    session = ViewerSession([], Path('.'), window)
    question_plot = lambda: drawn.append('question plot') or True
    session.redraw = question_plot
    kits = _kits_maker(log)
    viewer_stages._tab_switcher(session, kits, 'regions')
    window.edges = {'run1': {'edge': 2.5}}
    viewer_stages._tab_switcher(session, kits, '')
    assert log == [('open', 'regions'), ('apply', 'regions', {'run1': {'edge': 2.5}})]
    assert session.redraw is question_plot and drawn == ['question plot']
    assert session.time_tab == '' and window.tabs[-1] == ''
    assert window.shown[-1] is None


# ---- test_export_csv_in_the_trim_step ------------------------------------------------
def test_export_csv_in_the_trim_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the two export buttons of the trim step: they are offered
    above Continue, each writes the files with the edges as they are (Export full +
    trimmed csv with the whole recordings too), and the step waits again; Continue
    then gives the limits of the edges. Without an exporter there are no buttons. The
    plot, the edges and the questions are stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the stand-ins in place, and takes them away afterwards.

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

    # ---- 1 The stand-ins -------------------------------------------------------------
    answers = iter(['export_full', 'export_trimmed', ''])
    offered, exported = [], []
    def waiter(question: str, nudge: str, **kwargs: Any) -> str:
        offered.append(kwargs.get('extras'))
        return next(answers)
    monkeypatch.setattr(viewer_stages, 'enter_waiter', waiter)
    monkeypatch.setattr(viewer_stages, 'preview_drawer', lambda *args, **kwargs: True)
    monkeypatch.setattr(viewer_stages, 'guide_step_starter', lambda key: None)
    monkeypatch.setattr(viewer_stages, 'info_printer', lambda *args, **kwargs: None)
    monkeypatch.setattr(viewer_stages, '_limits_lister', lambda *args: None)
    monkeypatch.setattr(viewer_stages,
                        '_trim_choice_builder',
                        lambda *args: FakeChoice({'run1': {'trim_start': 1.0}}),
                        )
    monkeypatch.setattr(viewer_stages,
                        'trim_limits_builder',
                        lambda summaries, minutes: {name: dict(own, built=True)
                                                    for name, own in minutes.items()
                                                    },
                        )
    window = FakeWindow()
    session = ViewerSession([], Path('.'), window)

    # ---- 2 Both export buttons, then Continue ----------------------------------------
    standard = dict(settings.DEFAULT_ANSWERS)
    limits = viewer_stages.trim_stage_runner(
        session,
        standard,
        {},
        None,
        lambda limits, with_full: exported.append((limits, with_full)),
        )
    buttons = (('export_full', 'Export full + trimmed csv'),
               ('export_trimmed', 'Export trimmed csv'),
               )
    assert [tuple(own) for own in offered] == [buttons] * 3
    built = {'run1': {'trim_start': 1.0, 'built': True}}
    assert exported == [(built, True), (built, False)]
    assert limits == built
    assert session.time_tab == '' and window.tabs == ['trim', '']

    # ---- 3 No exporter, no buttons ---------------------------------------------------
    answers = iter([''])
    offered.clear()
    viewer_stages.trim_stage_runner(session, standard, {})
    assert [tuple(own) for own in offered] == [()]


# ---- test_the_figure_step_asks_only_continue -----------------------------------------
def test_the_figure_step_asks_only_continue(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the figure of each file (Finalise figures): one
    instruction (5.1) with its button named Export is asked and nothing else; the oxygen and the OCR are plotted whatever the dataset was saved
    with, every haem of the fit is, and the angle of the labels is the one in use. The
    plot and the question are stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Puts the stand-ins in place, and takes them away afterwards.

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

    asked = []
    def waiter(question: str, nudge: str, **kwargs: Any) -> str:
        asked.append((question, kwargs.get('number'), kwargs.get('go_words')))
        return ''
    def refused(*args: Any, **kwargs: Any) -> None:
        raise AssertionError('no other question is asked')
    monkeypatch.setattr(viewer_stages, 'enter_waiter', waiter)
    monkeypatch.setattr(viewer_stages, 'accept_asker', refused)
    monkeypatch.setattr(viewer_stages, 'choice_asker', refused)
    monkeypatch.setattr(viewer_stages, 'yes_no_asker', refused)
    monkeypatch.setattr(viewer_stages, 'preview_drawer', lambda *args, **kwargs: True)
    monkeypatch.setattr(viewer_stages, 'guide_step_starter', lambda key: None)
    monkeypatch.setattr(viewer_stages, 'info_printer', lambda *args, **kwargs: None)
    monkeypatch.setattr(viewer_stages, 'region_files_lister', lambda *args: [])
    summaries = [{'name': 'run1', 'datasets': ['Cyt']}]
    session = ViewerSession(summaries, Path('.'), FakeWindow())
    session.fit = {'haem_list': ['a', 'b', 'c']}
    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   normalise_od=False,
                   averaging=False,
                   plot_o2=False,
                   plot_ocr=False,
                   haems=['b'],
                   event_label_angle=30.0,
                   )
    defaults = dict(answers, event_label_angle=45.0)
    assert viewer_stages.plots_stage_runner(session, answers, defaults, {}, {})
    assert asked == [(
        'Use the arrows to change the order of the panels, or change '
        'earlier settings. When ready, click Export to choose which files '
        'to export.',
        '5.1',
        'Export',
        ),
                     ]
    assert answers['plot_o2'] and answers['plot_ocr'] and answers['plot_haems']
    assert answers['haems'] == ['a', 'b', 'c']
    assert answers['event_label_angle'] == 30.0
