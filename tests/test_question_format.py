"""
Tests of the question format: what Enter gives at the end of each kind of question, the
one sentence after a wrong answer, both shapes of the accept question, an instruction
carried out in a table, a question's own number and the shared reader of typed numbers.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from typing import List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import utils_shared.questions as questions
from utils_shared.questions import (_number_hint_builder,
                                    _unit_highlighter,
                                    accept_asker,
                                    choice_asker,
                                    COLOUR_DEFAULT,
                                    COLOUR_QUIET,
                                    COLOUR_RETRY,
                                    COLOUR_UNIT,
                                    confirm_waiter,
                                    multi_asker,
                                    number_asker,
                                    text_asker,
                                    typed_number_reader,
                                    yes_no_asker,
                                    )


# ---- CONSTANTS -----------------------------------------------------------------------
CODE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


# ---- HELPERS -------------------------------------------------------------------------


# ---- _lines_reader -------------------------------------------------------------------
def _lines_reader(printed: str) -> List[str]:
    """
    ---- Summary ----
    Helper function to give the printed lines without their colour codes or blank
    lines.

    ---- Inputs ----
    printed : str
        What the questions printed.

    ---- Globals read ----
    CODE_PATTERN (module constant).

    ---- Outputs ----
    List[str]
        The lines with text, without spaces at either end.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [line.strip()
            for line in CODE_PATTERN.sub('', printed).splitlines()
            if line.strip()
            ]


# ---- _typist_setter ------------------------------------------------------------------
def _typist_setter(monkeypatch: pytest.MonkeyPatch, typed: List[str]) -> None:
    """
    ---- Summary ----
    Helper function to have the questions read the given answers, one per question
    asked or wrong answer, in place of the window's answer box.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answer for the test only.
    typed : List[str]
        The answers, in order; each is taken once.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. The reader of the questions is restored by monkeypatch.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    answers = list(typed)
    monkeypatch.setattr(questions,
                        '_input_reader',
                        lambda text, indent='': answers.pop(0),
                        )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_accept_question_shapes -----------------------------------------------------
def test_accept_question_shapes(monkeypatch: pytest.MonkeyPatch,
                                capsys: pytest.CaptureFixture,
                                ) -> None:
    """
    ---- Summary ----
    Main function to check both shapes of a "Do you accept ...?" question: with one
    way to change it is a yes or no question with what n does on the quiet line just
    above; with more it is a numbered list starting "1) Yes, accept"; with none it is
    refused.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    COLOUR_QUIET.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _typist_setter
    accept_asker
    """

    # ---- 1 One way to change: yes or no ----------------------------------------------
    _typist_setter(monkeypatch, ['n', ''])
    one = [('no', 'change the labels again')]
    assert accept_asker('Do you accept these event labels?', one) == 'no'
    assert accept_asker('Do you accept these event labels?', one) == 'yes'
    printed = capsys.readouterr().out
    lines = _lines_reader(printed)
    note = lines.index('Type n to change the labels again.')
    assert lines[note + 1].endswith('Do you accept these event labels? (Y/n)')
    assert f'{COLOUR_QUIET}Type n to change the labels again.' in printed

    # ---- 2 More ways to change: a numbered list --------------------------------------
    _typist_setter(monkeypatch, ['3'])
    more = [('signals', 'change the oxygen and OCR'),
            ('angle', 'change the angle of the event labels'),
            ]
    assert accept_asker('Do you accept this figure?', more) == 'angle'
    lines = _lines_reader(capsys.readouterr().out)
    assert lines[0].endswith('Do you accept this figure? (1/2/3)')
    assert lines[1:] == ['1) Yes, accept',
                         '2) No, change the oxygen and OCR',
                         '3) No, change the angle of the event labels',
                         ]

    # ---- 3 No way to change ----------------------------------------------------------
    with pytest.raises(ValueError):
        accept_asker('Do you accept this?', [])


# ---- test_choice_endings -------------------------------------------------------------
def test_choice_endings(monkeypatch: pytest.MonkeyPatch,
                        capsys: pytest.CaptureFixture,
                        ) -> None:
    """
    ---- Summary ----
    Main function to check the end of a question answered from a numbered list: every
    number up to five options with the default brighter, a range beyond with the
    default option brighter in the list, and one sentence after a wrong answer.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    COLOUR_DEFAULT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _typist_setter
    choice_asker
    """

    # ---- 1 Up to five: every number, the default brighter ----------------------------
    _typist_setter(monkeypatch, [''])
    options = [('a', 'First'), ('b', 'Second'), ('c', 'Third')]
    assert choice_asker('Which one?', options, 'b') == 'b'
    printed = capsys.readouterr().out
    assert _lines_reader(printed)[0].endswith('Which one? (1/2/3)')
    assert f'{COLOUR_DEFAULT}2' in printed

    # ---- 2 More than five: a range, the default brighter in the list -----------------
    _typist_setter(monkeypatch, ['9', 'x', ''])
    options = [(str(n), f'Option {n}') for n in range(1, 8)]
    assert choice_asker('Which fit?', options, '3') == '3'
    printed = capsys.readouterr().out
    lines = _lines_reader(printed)
    assert lines[0].endswith('Which fit? (1–7)')
    assert f'{COLOUR_DEFAULT}3) Option 3' in printed
    assert lines.count('Type a number from 1 to 7.') == 2
    assert sum('Which fit?' in line for line in lines) == 1


# ---- test_given_number_is_shown ------------------------------------------------------
def test_given_number_is_shown(monkeypatch: pytest.MonkeyPatch,
                               capsys: pytest.CaptureFixture,
                               ) -> None:
    """
    ---- Summary ----
    Main function to check that a question given its own number shows exactly that
    number, every time it is asked and at the indent of its depth, and leaves the
    numbering of the other questions as it was; a number not like 3.5 is refused.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    CODE_PATTERN (module constant); questions.INDENT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets the numbering of the questions module (each test sets its own).

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _typist_setter
    accept_asker
    text_asker
    yes_no_asker
    """

    # ---- 1 Ask numbered questions in the middle of section 4 -------------------------
    questions.numbering_setter(0, 4)
    questions.numbering_setter(1, 2)
    _typist_setter(monkeypatch, ['', 'n', '', '', ''])
    yes_no_asker('Do you want to provide OD values?', False, number='3.2')
    one = [('no', 'change the labels again')]
    assert accept_asker('Do you accept these event labels?', one, number='3.5') == 'no'
    for _ in range(2):
        text_asker('What was added at 15.01 min?', 'KCN', number='3.4.1')
    yes_no_asker('Do you want to average around the events?', False)

    # ---- 2 Check the numbers and the indent ------------------------------------------
    printed = capsys.readouterr().out
    lines = _lines_reader(printed)
    assert lines[0] == '3.2 Do you want to provide OD values? (y/N)'
    assert lines[2] == '3.5 Do you accept these event labels? (Y/n)'
    assert lines[3:5] == ['3.4.1 What was added at 15.01 min? [KCN]'] * 2
    assert lines[5] == '4.3 Do you want to average around the events? (y/N)'
    plain = CODE_PATTERN.sub('', printed).splitlines()
    assert f'{questions.INDENT}3.4.1 What was added at 15.01 min? [KCN]' in plain
    assert '3.2 Do you want to provide OD values? (y/N)' in plain

    # ---- 3 A number not like 3.5 -----------------------------------------------------
    with pytest.raises(ValueError):
        yes_no_asker('Do you want to provide OD values?', False, number='3')


# ---- test_number_endings_and_hints ---------------------------------------------------
def test_number_endings_and_hints(monkeypatch: pytest.MonkeyPatch,
                                  capsys: pytest.CaptureFixture,
                                  ) -> None:
    """
    ---- Summary ----
    Main function to check a number question: [skip] or the default at the end, the
    unit highlighted, and after a wrong answer one sentence giving the kind of number,
    its limits and an example within them, the question waiting for the next answer.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    COLOUR_RETRY, COLOUR_UNIT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _number_hint_builder
    _typist_setter
    _unit_highlighter
    number_asker
    """

    # ---- 1 Enter leaves it empty: [skip]; wrong answers wait -------------------------
    _typist_setter(monkeypatch, ['', 'abc', '-1', '8'])
    question = 'What was the final concentration (µM)?'
    assert number_asker(question, None, minimum=0, allow_blank=True) is None
    assert number_asker(question, None, minimum=0, allow_blank=True) == 8
    printed = capsys.readouterr().out
    lines = _lines_reader(printed)
    assert lines[0].endswith('What was the final concentration (µM)? [skip]')
    assert f'{COLOUR_UNIT}µM' in printed
    assert lines[2:] == ['Type a number of 0 or more, for example 2.5.'] * 2
    assert f'{COLOUR_RETRY}Type a number' in printed

    # ---- 2 A whole number with a default ---------------------------------------------
    _typist_setter(monkeypatch, ['2.5', '4'])
    assert number_asker('How many?', 3, minimum=1, maximum=8, is_whole=True) == 4
    lines = _lines_reader(capsys.readouterr().out)
    assert lines[0].endswith('How many? [3]')
    assert lines[1] == 'Type a whole number from 1 to 8, for example 3.'

    # ---- 3 The sentence for other limits ---------------------------------------------
    assert (_number_hint_builder(0, 1, True, False)
            == 'Type a number above 0 and up to 1, for example 0.5.'
            )
    assert _number_hint_builder(None, None, False, False) == ('Type a number, for '
                                                              'example 2.5.'
                                                              )
    assert _number_hint_builder(400, None, False, False) == ('Type a number of 400 or '
                                                             'more, for example 401.'
                                                             )

    # ---- 4 Only a unit is highlighted ------------------------------------------------
    assert COLOUR_UNIT in _unit_highlighter('How long a window (s) should it be?')
    plain = 'Over how many nm should they be smoothed (0 for none)?'
    assert _unit_highlighter(plain) == plain


# ---- test_several_numbers ------------------------------------------------------------
def test_several_numbers(monkeypatch: pytest.MonkeyPatch,
                         capsys: pytest.CaptureFixture,
                         ) -> None:
    """
    ---- Summary ----
    Main function to check a question answered by several numbers: the quiet line just
    above saying to separate them with commas, the numbers at the end, the options
    Enter gives brighter in the list, and one sentence after a wrong answer.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    COLOUR_DEFAULT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _typist_setter
    multi_asker
    """

    _typist_setter(monkeypatch, ['1,9', '3,1', ''])
    names = ['a', 'b', 'c', 'd', 'e']
    assert multi_asker('Which haems?', names, keep_order=True) == ['c', 'a']
    assert multi_asker('Which haems?', names, default_values=['b', 'd']) == ['b', 'd']
    printed = capsys.readouterr().out
    lines = _lines_reader(printed)
    note = lines.index('Type one or more numbers, separated by commas.')
    assert lines[note + 1].endswith('Which haems? (1/2/3/4/5)')
    assert 'Type numbers from 1 to 5, separated by commas, for example 1,3.' in lines
    assert f'{COLOUR_DEFAULT}2) b' in printed and f'{COLOUR_DEFAULT}4) d' in printed


# ---- test_table_instruction_waits ----------------------------------------------------
def test_table_instruction_waits(monkeypatch: pytest.MonkeyPatch,
                                 capsys: pytest.CaptureFixture,
                                 ) -> None:
    """
    ---- Summary ----
    Main function to check an instruction carried out in a table: its quiet line above
    it, its own number and no ending, and, when Confirm is pressed with the table not
    yet filled in, the checker's one sentence while the instruction waits.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the window's Confirm.
    capsys : pytest.CaptureFixture
        Captures what the instruction prints.

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
    _lines_reader
    _typist_setter
    """

    _typist_setter(monkeypatch, ['', ''])
    sentences = ['Fill in these empty cells: a: OD.', None]
    confirm_waiter('Fill in the table, then press CONFIRM.',
                   lambda: sentences.pop(0),
                   note='One row per file.',
                   number='3.2.1',
                   )
    printed = capsys.readouterr().out
    assert _lines_reader(printed) == ['One row per file.',
                                      '3.2.1 Fill in the table, then press CONFIRM.',
                                      'Fill in these empty cells: a: OD.',
                                      ]
    assert f'{COLOUR_QUIET}One row per file.' in printed
    assert f'{COLOUR_RETRY}Fill in these empty cells' in printed
    assert not sentences


# ---- test_text_question_waits --------------------------------------------------------
def test_text_question_waits(monkeypatch: pytest.MonkeyPatch,
                             capsys: pytest.CaptureFixture,
                             ) -> None:
    """
    ---- Summary ----
    Main function to check that a text answer the checker refuses, the default given by
    Enter included, gets the checker's sentence while the question waits, printed once.

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
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _typist_setter
    text_asker
    """

    _typist_setter(monkeypatch, ['', 'wrong', 'ok'])
    def checker(text: Optional[str]) -> Optional[str]:
        return None if text == 'ok' else 'Type ok.'
    assert text_asker('Which folder?', 'old', checker=checker) == 'ok'
    lines = _lines_reader(capsys.readouterr().out)
    assert lines[0].endswith('Which folder? [old]')
    assert lines[1:] == ['Type ok.', 'Type ok.']


# ---- test_typed_number_reader --------------------------------------------------------
def test_typed_number_reader() -> None:
    """
    ---- Summary ----
    Main function to check the one reader of typed numbers: a point or a comma as the
    decimal sign, spaces around it, and None for nothing, words, "nan" and infinities.

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
    typed_number_reader
    """

    assert typed_number_reader('2.5') == pytest.approx(2.5)
    assert typed_number_reader(' 2,5 ') == pytest.approx(2.5)
    assert typed_number_reader('-3') == pytest.approx(-3.0)
    assert typed_number_reader('1e3') == pytest.approx(1000.0)
    for wrong in ('', '   ', 'abc', '1.2.3', 'nan', 'inf', '-inf'):
        assert typed_number_reader(wrong) is None


# ---- test_yes_no_endings -------------------------------------------------------------
def test_yes_no_endings(monkeypatch: pytest.MonkeyPatch,
                        capsys: pytest.CaptureFixture,
                        ) -> None:
    """
    ---- Summary ----
    Main function to check a yes or no question: (Y/n) or (y/N) with the letter Enter
    gives brighter, y, yes, n and no in any capitals, and one sentence after a wrong
    answer while the question waits.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Replaces the reading of the answers.
    capsys : pytest.CaptureFixture
        Captures what the questions print.

    ---- Globals read ----
    COLOUR_DEFAULT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _lines_reader
    _typist_setter
    yes_no_asker
    """

    _typist_setter(monkeypatch, ['', 'YES', 'maybe', 'No'])
    assert yes_no_asker('Do you want it?', True) is True
    assert yes_no_asker('Do you want it?', False) is True
    assert yes_no_asker('Do you want it?', True) is False
    printed = capsys.readouterr().out
    lines = _lines_reader(printed)
    assert lines[0].endswith('Do you want it? (Y/n)')
    assert lines[1].endswith('Do you want it? (y/N)')
    assert lines[3] == 'Type y or n.' and len(lines) == 4
    assert f'{COLOUR_DEFAULT}Y' in printed and f'{COLOUR_DEFAULT}N' in printed
