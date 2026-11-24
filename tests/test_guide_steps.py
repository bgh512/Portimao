"""
Tests of the guide on the left of the window: its steps, the step open and the previous processing question.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import ast
import re
from pathlib import Path
from typing import Dict, List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import utils_shared.questions as questions
from utils_shared.questions import (answer_request_setter,
                                    choice_asker,
                                    folder_asker,
                                    multi_asker,
                                    number_asker,
                                    yes_no_asker,
                                    )
from utils_shared.survey import previous_processing_asker
from utils_viewer.viewer_guide import (GUIDE_KEYS,
                                       GUIDE_STAGES,
                                       GUIDE_STEPS,
                                       folder_default_finder,
                                       folder_start_finder,
                                       folder_words_builder,
                                       GuideState,
                                       step_of_change_finder,
                                       )


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CODE_FOLDERS = ('utils_shared', 'utils_viewer', 'utils_custom')
# The first question of each step in QUESTION_FLOW.md, in the order of the guide.
FIRST_QUESTIONS = {'data_folder': '1.1',
                   'results_folder': '1.2',
                   'previous': '1.3',
                   'trim': '2.1',
                   'od_scaling': '3.1',
                   'od_values': '3.1.1',
                   'ocr_view': '3.1.1.1',
                   'temperature': '3.1.2',
                   'labels': '3.2',
                   'haems': '4.1',
                   'regions': '4.4',
                   'delta_psi': '4.5',
                   'windows': '4.6',
                   'figure': '5.1',
                   'go_back': '5.8',
                   'workbooks': '5.9',
                   'side_by_side': '6.1',
                   'grid': '6.3',
                   'time_response': '7.1',
                   'haem_ocr': '7.2',
                   'start': '9.1',
                   }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _started_steps_finder -----------------------------------------------------------
def _started_steps_finder() -> List[str]:
    """
    ---- Summary ----
    Helper function to list the step keys the program's code starts, from every call
    guide_step_starter('<key>') in main.py and the code folders.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CODE_FOLDERS, ROOT (module constants).

    ---- Outputs ----
    List[str]
        The keys, once per call; a call whose key is not written out is listed as
        '<not a key>'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    paths = [ROOT / 'main.py']
    for folder in CODE_FOLDERS:
        paths += sorted((ROOT / folder).glob('*.py'))
    keys = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            is_start = (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == 'guide_step_starter'
                        )
            if not is_start:
                continue
            argument = node.args[0] if node.args else None
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                keys.append(argument.value)
            elif isinstance(argument, ast.Name) and path.name in ('main.py',
                                                                  'custom_questions.py',
                                                                  ):
                continue  # handing the guide back, or the keys of the summary figures
            else:
                keys.append('<not a key>')
    return keys


# ---- _state_maker --------------------------------------------------------------------
def _state_maker(keys: List[str]) -> GuideState:
    """
    ---- Summary ----
    Helper function to make the guide as it is once the given steps have started, in
    order.

    ---- Inputs ----
    keys : List[str]
        The steps, in the order the program starts them.

    ---- Globals read ----
    None.

    ---- Outputs ----
    GuideState
        The guide.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    state = GuideState()
    for key in keys:
        state.step_starter(key)
    return state


# ---- _status_reader ------------------------------------------------------------------
def _status_reader(state: GuideState) -> Dict[str, str]:
    """
    ---- Summary ----
    Helper function to give the status of each step line the guide shows.

    ---- Inputs ----
    state : GuideState
        The guide.

    ---- Globals read ----
    GUIDE_KEYS.

    ---- Outputs ----
    Dict[str, str]
        {step key: status} of the step lines shown.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {GUIDE_KEYS[row['index']]: row['status']
            for row in state.row_lister()
            if row['kind'] == 'step'
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_steps_and_stages -----------------------------------------------------------
def test_steps_and_stages() -> None:
    """
    ---- Summary ----
    Main function to check the stages in their order, each step under one stage with
    the steps of a stage together, the steps in the order of their first questions in
    QUESTION_FLOW.md, and every one of those questions in the list.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIRST_QUESTIONS, ROOT (module constants); GUIDE_STAGES, GUIDE_STEPS, GUIDE_KEYS.

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

    assert GUIDE_STAGES == ('Import',
                            'Set-up',
                            'Experiment processing',
                            'Experiment export',
                            'Dataset figures',
                            'Dataset export',
                            )
    stages = [stage for _, stage, _, _ in GUIDE_STEPS]
    assert [s for i, s in enumerate(stages) if i == 0 or s != stages[i - 1]] == list(
        GUIDE_STAGES,
        )
    assert len(set(GUIDE_KEYS)) == len(GUIDE_KEYS) == 21
    assert list(FIRST_QUESTIONS) == list(GUIDE_KEYS)
    numbers = [tuple(int(n) for n in FIRST_QUESTIONS[key].split('.'))
               for key in GUIDE_KEYS
               ]
    assert numbers == sorted(numbers)
    flow = (ROOT / 'QUESTION_FLOW.md').read_text(encoding='utf-8')
    for number in FIRST_QUESTIONS.values():
        assert re.search(rf'^\| {re.escape(number)} \|', flow, re.MULTILINE), number
    for stage in GUIDE_STAGES:
        assert re.search(rf'^## \d+\. {re.escape(stage)}', flow, re.MULTILINE), stage


# ---- test_every_step_is_started ------------------------------------------------------
def test_every_step_is_started() -> None:
    """
    ---- Summary ----
    Main function to check that every step the code starts is a step of the guide,
    written out as its key, and that every step of the guide is started somewhere
    (the two summary figures by their keys in custom_questions.py).

    ---- Inputs ----
    None.

    ---- Globals read ----
    GUIDE_KEYS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _started_steps_finder
    """

    started = _started_steps_finder()
    assert set(started) <= set(GUIDE_KEYS)
    custom = (ROOT / 'utils_custom' / 'custom_questions.py').read_text(encoding='utf-8')
    started += [key for key in ('time_response', 'haem_ocr') if f"('{key}'," in custom]
    assert set(started) == set(GUIDE_KEYS)


# ---- test_steps_move_on_and_fold -----------------------------------------------------
def test_steps_move_on_and_fold() -> None:
    """
    ---- Summary ----
    Main function to check the lines of the guide as the steps go by: the step
    started is open, the steps asked are done, a step passed without being asked is
    skipped, with "not needed this run", and the steps to come are later; only the
    stage of the open step lists its steps, the others show their name and step
    numbers, with a tick once passed.

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
    _state_maker
    _status_reader
    """

    state = _state_maker(['data_folder',
                          'results_folder',
                          'trim',
                          'od_scaling',
                          'temperature',
                          ],
                         )
    assert _status_reader(state) == {'od_scaling': 'done',
                                     'od_values': 'skipped',
                                     'ocr_view': 'skipped',
                                     'temperature': 'open',
                                     'labels': 'later',
                                     }
    stage_rows = [row for row in state.row_lister() if row['kind'] == 'stage']
    stages = [row['text'] for row in stage_rows]
    # the trim step is the last step of the import
    assert stages[0] == 'Import  ·  steps 1–4  ✓'
    assert stages[1] == 'Set-up'
    assert stages[2] == 'Experiment processing  ·  steps 10–13'
    assert stages[-1] == 'Dataset export  ·  step 21'
    assert [row['is_open'] for row in stage_rows] == [False, True] + [False] * 4
    open_row = next(row for row in state.row_lister() if row.get('status') == 'open')
    assert open_row['text'] == ' 8  Temperature' and open_row['mark'] == '▸'
    # a step not needed this run stays in the list, so the numbers do not jump
    tags = {GUIDE_KEYS[row['index']]: row['tag']
            for row in state.row_lister()
            if row['kind'] == 'step'
            }
    assert tags['od_values'] == tags['ocr_view'] == 'not needed this run'
    assert tags['temperature'] == tags['labels'] == ''
    assert not state.is_back()
    assert state.card_teller() == {'note': '', 'help': '', 'back': '', 'extra': ()}
    with pytest.raises(ValueError):
        state.step_starter('not_a_step')


# ---- test_step_numbers_in_the_words --------------------------------------------------
def test_step_numbers_in_the_words() -> None:
    """
    ---- Summary ----
    Main function to check that every step named with its number in QUESTION_FLOW.md
    ("step 13 (Averaging windows)") and in the guide's own help has the number it
    has in the guide.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT (module constant); GUIDE_STEPS.

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

    numbers = {name: i + 1 for i, (_, _, name, _) in enumerate(GUIDE_STEPS)}
    flow = (ROOT / 'QUESTION_FLOW.md').read_text(encoding='utf-8')
    found = [(int(number), name)
             for number, name in re.findall(r'step (\d+) \(([^)]+)\)', flow)
             if name in numbers
             ]
    assert len(found) >= 4, 'The steps named with their number are no longer found.'
    assert all(numbers[name] == number for number, name in found), found
    help_text = ' '.join(help_words for _, _, _, help_words in GUIDE_STEPS)
    for name, number in re.findall(r'at ([A-Z][a-z ]+) \(step (\d+)\)', help_text):
        assert numbers[name] == int(number), name


# ---- test_hints_under_the_answers ----------------------------------------------------
def test_hints_under_the_answers() -> None:
    """
    ---- Summary ----
    Main function to check the hint under the answers: a box only for a number or a
    name, so no hint asks to type an answer to anything else.

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

    from utils_viewer.viewer_gui import _hint_chooser
    assert _hint_chooser('number', None).startswith('Type a number,')
    assert _hint_chooser('text', None).startswith('Type it in the box,')
    assert _hint_chooser('folder', None).startswith('Click a folder, then Continue.')
    for kind in ('continue', 'yesno', 'choice', 'multi', 'folder', 'confirm', None):
        assert 'Type the answer' not in _hint_chooser(kind, None)
        assert not _hint_chooser(kind, None).startswith('Type')


# ---- test_change_opens_earlier_step --------------------------------------------------
def test_change_opens_earlier_step() -> None:
    """
    ---- Summary ----
    Main function to check that changing the fit while at Δψ opens the haem step,
    with an arrow and "you were here" on Δψ and a button back to it, that going back
    opens Δψ again, and that the Trim / Ignore tab opens the trim step with its two
    export buttons.

    ---- Inputs ----
    None.

    ---- Globals read ----
    GUIDE_KEYS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _state_maker
    _status_reader
    """

    state = _state_maker(list(GUIDE_KEYS[:9]) + ['haems', 'regions', 'delta_psi'])
    assert state.change_opener({'fit_file': 'my_fit.csv'})
    assert state.is_back()
    assert state.shown == GUIDE_KEYS.index('haems')
    statuses = _status_reader(state)
    assert statuses['haems'] == 'open' and statuses['delta_psi'] == 'here'
    here = next(row for row in state.row_lister() if row.get('status') == 'here')
    assert here['mark'] == '→' and here['tag'] == 'you were here'
    card = state.card_teller()
    assert card['back'] == 'Back to Δψ'
    assert card['note'] == ('This is step 10, Haems. When you are done here, go back '
                            'to step 12, Δψ, where you were.')
    assert 'Keep to compare' in card['help'] and card['extra'] == ()
    state.back_taker()
    assert not state.is_back() and _status_reader(state)['delta_psi'] == 'open'

    # Edit ODs and Edit labels open their own step
    assert step_of_change_finder({'edit_ods': True}) == 'od_values'
    assert step_of_change_finder({'edit_labels': True}) == 'labels'

    # the Trim / Ignore tab opens the trim step, which keeps its two export buttons
    assert step_of_change_finder({'time_tab': 'trim'}) == 'trim'
    assert state.change_opener({'time_tab': 'trim'})
    assert state.shown == GUIDE_KEYS.index('trim')
    assert [words for _, words in state.card_teller()['extra']] == [
        'Export full + trimmed csv',
        'Export trimmed csv',
        ]
    state.back_taker()

    # the program going back to an earlier step keeps how far it had reached
    state.step_starter('trim')
    assert _status_reader(state)['trim'] == 'open'
    assert state.reached == GUIDE_KEYS.index('delta_psi')


# ---- test_changes_that_open_nothing --------------------------------------------------
def test_changes_that_open_nothing() -> None:
    """
    ---- Summary ----
    Main function to check the changes that leave the guide where it is: how the
    haems, the OCR and the labels are shown (they belong to every step), a change
    that belongs to the step waited at, and any change before the first step; that a
    change of a later step (or its tab of the Time regions box) only ticks it as done;
    and that a click opens only a step already asked.

    ---- Inputs ----
    None.

    ---- Globals read ----
    GUIDE_KEYS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _state_maker
    """

    assert not GuideState().change_opener({'fit_file': 'x.csv'})
    assert step_of_change_finder({'haem_mode': 'percent', 'ocr_mode': 'od'}) is None
    assert step_of_change_finder({'journal': 'cell', 'psi_share': 0.4}) == 'delta_psi'
    state = _state_maker(['data_folder', 'trim', 'haems'])
    assert not state.change_opener({'haem_mode': 'abs', 'label_mode': 'added'})
    assert not state.change_opener({'haem_background': 'flat'})  # the step waited at
    assert not state.line_opener(GUIDE_KEYS.index('figure'))  # not asked yet
    # a change of a later step ticks it as done, and opens nothing
    assert state.change_opener({'journal': 'cell'})
    assert not state.change_opener({'journal': 'science'})  # ticked already
    assert not state.is_back()
    assert GUIDE_KEYS.index('figure') in state.asked
    assert state.change_opener({'time_tab': 'windows'})
    assert _status_reader(state)['windows'] == 'done' and not state.is_back()
    assert state.line_opener(GUIDE_KEYS.index('trim'))
    assert state.is_back()
    assert state.line_opener(GUIDE_KEYS.index('haems'))  # the step waited at
    assert not state.is_back()


# ---- test_previous_processing_question -----------------------------------------------
def test_previous_processing_question(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check question 1.3: Yes, and Enter, load what was saved with
    the dataset; No starts it fresh, as a dataset never opened.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.

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

    saved = {'limits': {'run1': {'trim_start': 2.0}}, 'fit_file': 'my_fit.csv'}
    typed = ['y', '', 'n']
    monkeypatch.setattr(questions,
                        '_input_reader',
                        lambda text, indent='': typed.pop(0),
                        )
    assert previous_processing_asker(saved) is saved
    assert previous_processing_asker(saved) is saved
    assert previous_processing_asker(saved) == {}


# ---- test_answers_told_to_the_window -------------------------------------------------
def test_answers_told_to_the_window(monkeypatch: pytest.MonkeyPatch,
                                    capsys: pytest.CaptureFixture,
                                    ) -> None:
    """
    ---- Summary ----
    Main function to check what the window is told about each kind of question, to
    show its answers as buttons, and that the question then leaves out what is typed
    (the ending and the numbered options) while the answers still read as before.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The window stand-in is taken away at the end.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    told: List[dict] = []
    typed = ['n', '2', '3,1', '']
    monkeypatch.setattr(questions,
                        '_input_reader',
                        lambda text, indent='': typed.pop(0),
                        )
    answer_request_setter(told.append)
    try:
        assert yes_no_asker('Do you want it?', False) is False
        assert choice_asker('Which one?', [('a', 'First'), ('b', 'Second')], 'a') == 'b'
        assert multi_asker('Which ones?',
                           ['x', 'y', 'z'],
                           default_values=['y'],
                           keep_order=True,
                           ) == ['z', 'x']
        assert number_asker('How long (s)?', 120) == 120
    finally:
        answer_request_setter(None)
    assert [request['kind'] for request in told] == ['yesno',
                                                     'choice',
                                                     'multi',
                                                     'number',
                                                     ]
    assert told[0]['default'] == 'n'
    assert told[1]['options'] == ['First', 'Second'] and told[1]['default'] == 1
    assert told[2]['options'] == ['x', 'y', 'z'] and told[2]['default'] == [2]
    assert told[3]['value'] == '120'
    printed = re.sub(r'\x1b\[[0-9;]*m', '', capsys.readouterr().out)
    assert '(y/N)' not in printed and '[120]' not in printed
    assert '1) First' not in printed
    assert 'Tick one or more, then click Continue.' in printed


# ---- test_folder_question ------------------------------------------------------------
def test_folder_question(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check a folder question (1.1, 1.2): what the window is told (the
    folders, the one highlighted, what the box under Other folder… starts with), that
    a refused folder makes the question wait, and Enter gives the default; and which
    button is highlighted, the words on each and where Browse… opens.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The window stand-in is taken away at the end.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 What the window is told, and the answers ----------------------------------
    told: List[dict] = []
    first = str(tmp_path / 'data_a')
    second = str(tmp_path / 'data_b')
    folders = [(first, 'data_a', '6 files'), (second, 'data_b', '1 file')]
    typed = ['nowhere', second, '']
    monkeypatch.setattr(questions,
                        '_input_reader',
                        lambda text, indent='': typed.pop(0),
                        )
    def checker(text: str) -> object:
        return None if text in (first, second) else 'Choose a folder that exists.'
    answer_request_setter(told.append)
    try:
        assert folder_asker('Choose the folder, then press Continue.',
                            folders,
                            default=first,
                            typed=first,
                            checker=checker,
                            number='1.1',
                            ) == second
        assert folder_asker('Choose the folder, then press Continue.',
                            folders,
                            default=first,
                            number='1.1',
                            ) == first
    finally:
        answer_request_setter(None)
    assert told[0] == {'kind': 'folder',
                       'options': folders,
                       'default': first,
                       'value': first,
                       }

    # ---- 2 The button highlighted ----------------------------------------------------
    answers = [first, second]
    assert folder_default_finder(answers, second) == 1
    assert folder_default_finder(answers, f'"{second}"') == 1
    assert folder_default_finder(answers, str(tmp_path / 'elsewhere')) == -1
    assert folder_default_finder(answers, None) == 0
    assert folder_default_finder([], None) == -1

    # ---- 3 The words on a button, and where Browse… opens ----------------------------
    assert folder_words_builder('data_a', '6 files', True) == '●  data_a  ·  6 files'
    assert folder_words_builder('Other folder…', '', False) == '○  Other folder…'
    assert folder_start_finder(str(tmp_path / 'new' / 'results')) == str(tmp_path)
    assert folder_start_finder(f'"{tmp_path}"') == str(tmp_path)
    assert folder_start_finder('') == str(Path.home())
