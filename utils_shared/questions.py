"""
Helpers for asking numbered questions in the terminal of the window.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import math
import os
import re
from typing import Callable, List, Optional, Sequence, Set, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.run_logging import answer_logger


# ---- CONSTANTS -----------------------------------------------------------------------
COLOUR_QUESTION = '\x1b[1;38;5;213m'  # bold pink
COLOUR_DEFAULT = '\x1b[1;97m'  # bold white: what Enter gives
COLOUR_QUIET = '\x1b[38;5;245m'  # grey: explanations and loading messages
COLOUR_RETRY = '\x1b[91m'  # soft red: what to type, after a wrong answer
COLOUR_SECTION = '\x1b[1;33m'  # bold yellow
COLOUR_UNIT = '\x1b[1;96m'  # bold cyan: the unit of a number question
ITALIC = '\x1b[3m'
RESET = '\x1b[0m'
INDENT = '   '
# a list this long or shorter shows every number at the end, (1/2/3); a longer one a
# range, (1–7)
LIST_SPELLED_OUT = 5
MAX_DEPTH = 6
NUMBERS_NOTE = 'Type one or more numbers, separated by commas.'
# a unit in brackets in a number question: (s), (nm), (µM); words with spaces are not
UNIT_PATTERN = re.compile(r'\(([^()\s]{1,6})\)')
_counters = [0] * MAX_DEPTH  # [section, question, sub question, ...]
_tight_next = False  # True: the next question follows its heading line directly
# What is told when a question can be answered with the mouse (the window, which then
# takes clicks or drags on the plot); None while no window is open.
_time_requester: Optional[Callable[[Optional[str], Optional[Callable]], None]] = None
# What is told how each question is answered (the window, which then shows its answers
# as buttons and leaves out the typed endings); None while no window is open.
_answer_requester: Optional[Callable[[dict], None]] = None
# What is told which step of the guide starts; None while no window is open.
_step_teller: Optional[Callable[[str], None]] = None
_current_step: Optional[str] = None
CLICK_MULTI_NOTE = 'Tick one or more, then click Continue.'


# ---- UserQuitError -------------------------------------------------------------------
class UserQuitError(Exception):
    """
    ---- Summary ----
    Raised when the input ends (the window closed) so the program can stop cleanly.

    ---- Attributes ----
    None.

    ---- Globals read ----
    None.

    ---- Methods ----
    None.
    """


# ---- QUESTIONS HELPERS ---------------------------------------------------------------


# ---- _answer_announcer ---------------------------------------------------------------
def _answer_announcer(kind: str,
                      options: Sequence = (),
                      default: object = None,
                      value: Optional[str] = None,
                      ) -> None:
    """
    ---- Summary ----
    Helper function to tell the window, when there is one, how the question just asked
    is answered, so it shows the answers as buttons.

    ---- Inputs ----
    kind : str
        'continue', 'yesno', 'choice', 'multi', 'number', 'text', 'folder' or
        'confirm'.
    options : Sequence
        The words of each choice ('choice', 'multi'), the (answer, words) pairs
        offered beside the typing box ('text'), or the (answer, name, note) of each
        folder ('folder'); empty otherwise.
    default : object
        What Enter gives: 'y' or 'n'; the number of a choice (from 1); the numbers of
        the choices ticked at first; the folder highlighted at first; None for none.
    value : Optional[str]
        What the typing box starts with ('number', 'text', 'folder'), or the words of
        the button that goes on ('continue'; None for Continue).

    ---- Globals read ----
    _answer_requester (module state).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Calls the registered function (side effect); nothing happens without one.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if _answer_requester is not None:
        _answer_requester({'kind': kind,
                           'options': list(options),
                           'default': default,
                           'value': value,
                           },
                          )


# ---- _brightener ---------------------------------------------------------------------
def _brightener(text: str, code: str = COLOUR_DEFAULT) -> str:
    """
    ---- Summary ----
    Helper function to set part of a question line in another colour (what Enter
    gives, or a unit) and go back to the question colour after it.

    ---- Inputs ----
    text : str
        The part to colour.
    code : str
        Its colour code (COLOUR_DEFAULT by default).

    ---- Globals read ----
    COLOUR_DEFAULT, COLOUR_QUESTION, RESET (module constants).

    ---- Outputs ----
    str
        The part with its colour, followed by the question colour again.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return f'{RESET}{code}{text}{RESET}{COLOUR_QUESTION}'


# ---- _input_reader -------------------------------------------------------------------
def _input_reader(text: str, indent: str = '') -> str:
    """
    ---- Summary ----
    Helper function to show the answer prompt and read what the user types in the
    window's answer box (the window puts its own reader in place of input while it
    runs). Every answer, typed or given with the mouse, passes here, and is added to
    the run's log once it has started.

    ---- Inputs ----
    text : str
        The question text (not printed; kept so tests can replace this function and
        match on it).
    indent : str
        Indent placed before the "> " prompt.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The typed answer with surrounding spaces removed.

    ---- Globals mutated ----
    None. Reads from the terminal and writes the answer to the run's log; raises
    UserQuitError when the input ends (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    answer_logger
    """

    try:
        answer = input(f'{indent}> ').strip()
    except EOFError:
        raise UserQuitError()
    answer_logger(f'{indent}> {answer}')
    return answer


# ---- _limits_checker -----------------------------------------------------------------
def _limits_checker(value: float,
                    minimum: Optional[float],
                    maximum: Optional[float],
                    exclusive_minimum: bool,
                    is_whole: bool,
                    ) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a number is within the limits of a number question.

    ---- Inputs ----
    value : float
        The number.
    minimum : Optional[float]
        Smallest accepted value, or None.
    maximum : Optional[float]
        Largest accepted value, or None.
    exclusive_minimum : bool
        True when the minimum itself is not accepted.
    is_whole : bool
        True when only whole numbers are accepted.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the number can be used.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if minimum is not None and (value <= minimum if exclusive_minimum else value < minimum):
        return False
    if maximum is not None and value > maximum:
        return False
    return not is_whole or value == int(value)


# ---- _list_ending_builder ------------------------------------------------------------
def _list_ending_builder(count: int, default_number: Optional[int]) -> str:
    """
    ---- Summary ----
    Helper function to write the end of a question answered from a numbered list: every
    number up to LIST_SPELLED_OUT options, (1/2/3) with the default brighter, and a
    range beyond, (1–7), whose default is brighter in the list instead.

    ---- Inputs ----
    count : int
        Number of options.
    default_number : Optional[int]
        Number given by Enter, brightened when every number is shown; None for none.

    ---- Globals read ----
    LIST_SPELLED_OUT (module constant).

    ---- Outputs ----
    str
        The ending, for example "(1/2/3)" or "(1–7)", with colour codes.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _brightener
    """

    if count > LIST_SPELLED_OUT:
        return f'(1–{count})'
    numbers = [_brightener(str(n)) if n == default_number else str(n)
               for n in range(1, count + 1)
               ]
    return f"({'/'.join(numbers)})"


# ---- _number_builder -----------------------------------------------------------------
def _number_builder(depth: int) -> str:
    """
    ---- Summary ----
    Helper function to advance the counters and build the next question number.

    ---- Inputs ----
    depth : int
        Numbering depth (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    MAX_DEPTH (module constant).

    ---- Outputs ----
    str
        Question number such as "3.1.2".

    ---- Globals mutated ----
    None. Increments the module counters _counters at the depth and resets deeper levels
    (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    _counters[depth] += 1
    for level in range(depth + 1, MAX_DEPTH):
        _counters[level] = 0
    return '.'.join(str(c) for c in _counters[:depth + 1])


# ---- _number_depth_finder ------------------------------------------------------------
def _number_depth_finder(number: Optional[str], depth: int) -> int:
    """
    ---- Summary ----
    Helper function to give the numbering depth of a question: that of its own number
    when it has one ('3.4.1' is depth 2), otherwise the depth it was asked at.

    ---- Inputs ----
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '3.5'; None when it is
        numbered in the order asked.
    depth : int
        Numbering depth it was asked at (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        The numbering depth, at least 1. Raises ValueError for a number that is not
        whole numbers joined by dots, below a section.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if number is None:
        return depth
    if not re.fullmatch(r'\d+(\.\d+)+', number):
        raise ValueError(f"The question number '{number}' is not like 3.5 or 3.4.1.")
    return number.count('.')


# ---- _number_hint_builder ------------------------------------------------------------
def _number_hint_builder(minimum: Optional[float],
                         maximum: Optional[float],
                         exclusive_minimum: bool,
                         is_whole: bool,
                         ) -> str:
    """
    ---- Summary ----
    Helper function to write the one sentence shown after a wrong answer to a number
    question: what kind of number, its limits and an example within them.

    ---- Inputs ----
    minimum : Optional[float]
        Smallest accepted value, or None.
    maximum : Optional[float]
        Largest accepted value, or None.
    exclusive_minimum : bool
        True when the minimum itself is not accepted.
    is_whole : bool
        True when only whole numbers are accepted.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example "Type a number of 0 or more, for example 2.5." or "Type a whole
        number from 1 to 8, for example 3."; without the example when none fits.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _limits_checker
    """

    # ---- 1 The kind of number and its limits -----------------------------------------
    kind = 'a whole number' if is_whole else 'a number'
    if minimum is not None and maximum is not None:
        limits = (f' above {minimum:g} and up to {maximum:g}'
                  if exclusive_minimum
                  else f' from {minimum:g} to {maximum:g}'
                  )
    elif minimum is not None:
        limits = f' above {minimum:g}' if exclusive_minimum else f' of {minimum:g} or more'
    elif maximum is not None:
        limits = f' of {maximum:g} or less'
    else:
        limits = ''

    # ---- 2 An example within the limits ----------------------------------------------
    candidates = [3.0 if is_whole else 2.5]
    if minimum is not None and maximum is not None:
        middle = (minimum + maximum) / 2
        candidates.append(float(round(middle)) if is_whole else middle)
    if minimum is not None:
        candidates.append(minimum + 1)
    if maximum is not None:
        candidates.append(maximum)
    example = next(
        (value
         for value in candidates
         if _limits_checker(value, minimum, maximum, exclusive_minimum, is_whole)
         ),
        None,
        )
    if example is None:
        return f'Type {kind}{limits}.'
    return f'Type {kind}{limits}, for example {example:g}.'


# ---- _numbers_hint_builder -----------------------------------------------------------
def _numbers_hint_builder(count: int) -> str:
    """
    ---- Summary ----
    Helper function to write the one sentence shown after a wrong answer to a question
    answered by several numbers from a list.

    ---- Inputs ----
    count : int
        Number of options in the list.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example "Type numbers from 1 to 5, separated by commas, for example 1,3.".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if count < 2:
        return 'Type 1.'
    return (f'Type numbers from 1 to {count}, separated by commas, for example '
            f'1,{min(count, 3)}.'
            )


# ---- _options_printer ----------------------------------------------------------------
def _options_printer(labels: Sequence[str], indent: str, bright: Set[int]) -> None:
    """
    ---- Summary ----
    Helper function to print the numbered options of a list under its question, the
    ones Enter gives brighter where the end of the question does not show them.

    ---- Inputs ----
    labels : Sequence[str]
        The options as shown, numbered 1), 2), ...
    indent : str
        Indent of the question.
    bright : Set[int]
        Numbers (from 1) of the options to show brighter.

    ---- Globals read ----
    COLOUR_DEFAULT, INDENT (module constants); _answer_requester (module state): in
    the window the options are buttons, and are not printed.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    if _answer_requester is not None:
        return
    for number, label in enumerate(labels, start=1):
        line = f'{number}) {label}'
        if number in bright:
            line = text_colourer(line, COLOUR_DEFAULT)
        print(f'{indent}{INDENT}{line}')


# ---- _question_printer ---------------------------------------------------------------
def _question_printer(question: str,
                      depth: int,
                      ending: str = '',
                      note: str = '',
                      has_unit: bool = False,
                      number: Optional[str] = None,
                      ) -> str:
    """
    ---- Summary ----
    Helper function to print the numbered question line in the question colour, ending
    in what Enter gives, with an optional quieter line just above it. A question with
    its own number shows that number and leaves the counters alone; any other takes the
    next number in the order asked.

    ---- Inputs ----
    question : str
        Question text, without its number.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    ending : str
        What Enter gives, such as "[120]" or "(y/N)", with its colour codes; may be
        empty.
    note : str
        A line said just above the question in the quieter colour, such as what "n"
        does; may be empty.
    has_unit : bool
        True for a number question, whose unit in brackets is highlighted.
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '3.5'; None to number
        it in the order asked. When given, ``depth`` must be its depth.

    ---- Globals read ----
    COLOUR_QUIET, INDENT (module constants); _tight_next, _answer_requester (module
    state): in the window the answers are buttons, so the ending is left out.

    ---- Outputs ----
    str
        Indent to use for the answer prompt and the option lines.

    ---- Globals mutated ----
    None. Prints to the terminal and clears the module flag _tight_next (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_builder
    _unit_highlighter
    text_colourer
    """

    global _tight_next
    indent = INDENT * (depth - 1)
    gap = '' if _tight_next else '\n'
    if note:
        print(f'{gap}{indent}{text_colourer(note, COLOUR_QUIET)}')
        gap = ''
    shown = _unit_highlighter(question) if has_unit else question
    line = f'{number or _number_builder(depth)} {shown}'
    if ending and _answer_requester is None:
        line += f' {ending}'
    print(f'{gap}{indent}{text_colourer(line)}')
    _tight_next = False
    return indent


# ---- _time_announcer -----------------------------------------------------------------
def _time_announcer(kind: Optional[str], reader: Optional[Callable]) -> None:
    """
    ---- Summary ----
    Helper function to tell the window, when there is one, that the question being
    asked can be answered with the mouse (a drag across the plot, turned into the
    answer by ``reader``), or no longer can.

    ---- Inputs ----
    kind : Optional[str]
        'span' (a drag), or None once the question has its answer.
    reader : Optional[Callable]
        Turns the drag into the answer: reader(file name, start_min, end_min); it
        returns None when that file or place gives no answer. None with kind None.

    ---- Globals read ----
    _time_requester (module state).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Calls the registered function (side effect); nothing happens without one.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if _time_requester is not None:
        _time_requester(kind, reader)


# ---- _unit_highlighter ---------------------------------------------------------------
def _unit_highlighter(question: str) -> str:
    """
    ---- Summary ----
    Helper function to highlight the unit of a number question, written once in
    brackets after the quantity: "How long a window (s) ...", "... concentration
    (µM)?". Brackets holding words with spaces, such as "(0 for none)", are left alone.

    ---- Inputs ----
    question : str
        Question text.

    ---- Globals read ----
    COLOUR_UNIT, UNIT_PATTERN (module constants).

    ---- Outputs ----
    str
        The question with each unit in the unit colour.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _brightener
    """

    return UNIT_PATTERN.sub(lambda m: f'({_brightener(m.group(1), COLOUR_UNIT)})',
                            question,
                            )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- accept_asker --------------------------------------------------------------------
def accept_asker(question: str,
                 changes: Sequence[Tuple[str, str]],
                 depth: int = 1,
                 number: Optional[str] = None,
                 ) -> str:
    """
    ---- Summary ----
    Main function to ask a "Do you accept ...?" question, the one place its answers are
    written. With one way to change it is a yes or no question, (Y/n), with a quieter
    line above saying what n does; with more it is a numbered list starting
    "1) Yes, accept", then "2) No, <change>" and so on.

    ---- Inputs ----
    question : str
        The accept question, for example 'Do you accept these event labels?'.
    changes : Sequence[Tuple[str, str]]
        The ways to change, at least one, as (key, what it does), for example
        ('no', 'change the labels again').
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '3.5'; None to number
        it in the order asked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        'yes' when accepted, otherwise the key of the change chosen. Raises ValueError
        when no way to change is given.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    yes_no_asker
    """

    if not changes:
        raise ValueError(f"The question '{question}' was given no way to change.")
    if len(changes) == 1:
        key, change = changes[0]
        how = 'Type n' if _answer_requester is None else 'Click No'
        is_accepted = yes_no_asker(question,
                                   True,
                                   depth,
                                   note=f'{how} to {change}.',
                                   number=number,
                                   )
        return 'yes' if is_accepted else key
    options = [('yes', 'Yes, accept'),
               ] + [(key, f'No, {change}') for key, change in changes]
    return choice_asker(question, options, 'yes', depth, number=number)


# ---- answer_request_setter -----------------------------------------------------------
def answer_request_setter(requester: Optional[Callable[[dict], None]]) -> None:
    """
    ---- Summary ----
    Main function to register what is told how each question is answered: the window
    registers itself while it is open, so it shows the answers as buttons, and the
    questions then leave out what is typed ((y/N), [value], the numbered options).

    ---- Inputs ----
    requester : Optional[Callable[[dict], None]]
        Function called with {'kind', 'options', 'default', 'value'} once each question
        is printed (see _answer_announcer); None to register nothing (when the window
        closes).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    _answer_requester (module state).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _answer_requester
    _answer_requester = requester


# ---- choice_asker --------------------------------------------------------------------
def choice_asker(question: str,
                 options: Sequence[Tuple[str, str]],
                 default: Optional[str] = None,
                 depth: int = 1,
                 number: Optional[str] = None,
                 ) -> str:
    """
    ---- Summary ----
    Main function to ask a question answered by choosing one numbered option. The end
    of the question gives the numbers that can be typed: every one up to
    LIST_SPELLED_OUT options, the default brighter, or a range beyond, the default
    option brighter in the list.

    ---- Inputs ----
    question : str
        Question text, without its number.
    options : Sequence[Tuple[str, str]]
        Choices as (key, label) pairs, shown as 1), 2), ...
    default : Optional[str]
        Key chosen when only Enter is pressed.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '5.1'; None to number
        it in the order asked.

    ---- Globals read ----
    LIST_SPELLED_OUT (module constant).

    ---- Outputs ----
    str
        Key of the chosen option.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _input_reader
    _list_ending_builder
    _number_depth_finder
    _options_printer
    _question_printer
    retry_teller
    """

    # ---- 1 Work out the default ------------------------------------------------------
    depth = _number_depth_finder(number, depth)
    default_number = next((i
                           for i, (key, _) in enumerate(options, start=1)
                           if key == default
                           ),
                          None,
                          )

    # ---- 2 Print the question and options --------------------------------------------
    count = len(options)
    indent = _question_printer(question,
                               depth,
                               _list_ending_builder(count, default_number),
                               number=number,
                               )
    bright = {default_number} if default_number and count > LIST_SPELLED_OUT else set()
    _options_printer([label for _, label in options], indent, bright)
    _answer_announcer('choice', [label for _, label in options], default_number)

    # ---- 3 Read and check the answer -------------------------------------------------
    hint = f'Type a number from 1 to {count}.' if count > 1 else 'Type 1.'
    while True:
        answer = _input_reader(question, indent)
        if not answer and default_number:
            return options[default_number - 1][0]
        if answer.isdigit() and 1 <= int(answer) <= count:
            return options[int(answer) - 1][0]
        retry_teller(hint, depth)


# ---- confirm_waiter ------------------------------------------------------------------
def confirm_waiter(question: str,
                   checker: Callable[[], Optional[str]],
                   note: str = '',
                   depth: int = 1,
                   number: Optional[str] = None,
                   ) -> None:
    """
    ---- Summary ----
    Main function to give a numbered instruction carried out in a table of the window
    ("Fill in ..., then press Confirm.") and wait until Confirm is pressed with the
    table filled in. While the checker finds something wrong, its one sentence is said
    and the instruction goes on waiting.

    ---- Inputs ----
    question : str
        The instruction, without its number, ending "then press Confirm.".
    checker : Callable[[], Optional[str]]
        Reads the table and gives None when it can be used, or the sentence saying
        what is still wrong.
    note : str
        Lines said just above the instruction in the quieter colour, such as what each
        column means; may be empty.
    depth : int
        Numbering depth of the instruction (1 = 3.1, 2 = 3.1.1, ...).
    number : Optional[str]
        The instruction's own number from QUESTION_FLOW.md, such as '3.2'; None to
        number it in the order asked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _input_reader
    _number_depth_finder
    _question_printer
    retry_teller
    """

    depth = _number_depth_finder(number, depth)
    indent = _question_printer(question, depth, note=note, number=number)
    _answer_announcer('confirm')
    while True:
        _input_reader(question, indent)
        hint = checker()
        if hint is None:
            return
        retry_teller(hint, depth)


# ---- enter_waiter --------------------------------------------------------------------
def enter_waiter(question: str,
                 nudge: str,
                 depth: int = 1,
                 number: Optional[str] = None,
                 extras: Sequence[Tuple[str, str]] = (),
                 go_words: Optional[str] = None,
                 ) -> str:
    """
    ---- Summary ----
    Main function to give a numbered instruction that is carried out in the window (on
    the plot or in the boxes above it) and wait until Continue (Enter with the answer
    box empty), or the button named in its place, or one of the extra buttons is
    clicked. Anything else typed is answered with ``nudge`` and the instruction goes
    on waiting.

    ---- Inputs ----
    question : str
        The instruction, without its number.
    nudge : str
        One sentence saying where to do it instead of typing in the answer box.
    depth : int
        Numbering depth of the instruction (1 = 3.1, 2 = 3.1.1, ...).
    number : Optional[str]
        The instruction's own number from QUESTION_FLOW.md, such as '2.1'; None to
        number it in the order asked.
    extras : Sequence[Tuple[str, str]]
        (answer, words) of each button shown above Continue, such as ('export',
        'Export trimmed csv'); empty for Continue alone.
    go_words : Optional[str]
        The words of the button that goes on, such as 'Export'; None for Continue.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        '' for Continue (or the button in its place), or the answer of the extra
        button clicked.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _input_reader
    _number_depth_finder
    _question_printer
    retry_teller
    """

    depth = _number_depth_finder(number, depth)
    indent = _question_printer(question, depth, number=number)
    _answer_announcer('continue', list(extras), value=go_words)
    answers = {answer for answer, _ in extras}
    while True:
        answer = _input_reader(question, indent)
        if not answer or answer in answers:
            return answer
        retry_teller(nudge, depth)


# ---- folder_asker --------------------------------------------------------------------
def folder_asker(question: str,
                 folders: Sequence[Tuple[str, str, str]],
                 default: Optional[str] = None,
                 typed: str = '',
                 depth: int = 1,
                 checker: Optional[Callable[[Optional[str]], Optional[str]]] = None,
                 number: Optional[str] = None,
                 ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to ask for a folder. In the window each folder offered is a button
    that a click highlights, "Other folder…" opens a box for a full path with Browse…
    beside it, and Continue gives the folder highlighted; in the terminal the path is
    typed. An answer the checker refuses gets its one sentence of what to do, and the
    question waits for the next answer.

    ---- Inputs ----
    question : str
        Question text, without its number.
    folders : Sequence[Tuple[str, str, str]]
        (answer, name, note) of each folder offered: the answer is its full path, the
        note what it holds ('6 files', 'new folder').
    default : Optional[str]
        Answer used when only Enter is pressed, and the folder highlighted at first;
        one not offered highlights Other folder…. None for none.
    typed : str
        What the box under Other folder… starts with.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    checker : Optional[Callable[[Optional[str]], Optional[str]]]
        Takes the answer and gives None when it can be used, or the sentence saying
        what to do instead; None accepts every answer.
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '1.1'; None to number
        it in the order asked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The folder given (its path as typed or clicked), or the default when Enter is
        pressed.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _brightener
    _input_reader
    _number_depth_finder
    _question_printer
    retry_teller
    """

    depth = _number_depth_finder(number, depth)
    ending = f'[{_brightener(default)}]' if default else ''
    indent = _question_printer(question, depth, ending, number=number)
    _answer_announcer('folder', folders, default=default, value=typed)
    while True:
        answer = _input_reader(question, indent) or default
        hint = checker(answer) if checker is not None else None
        if hint is None:
            return answer
        retry_teller(hint, depth)


# ---- guide_step_getter ---------------------------------------------------------------
def guide_step_getter() -> Optional[str]:
    """
    ---- Summary ----
    Main function to give the step of the guide started last, so a step asked in the
    middle of another (the averaging windows asked for by a figure) can hand the guide
    back to it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    _current_step (module state).

    ---- Outputs ----
    Optional[str]
        The key of the step, or None before the first.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return _current_step


# ---- guide_step_setter ---------------------------------------------------------------
def guide_step_setter(teller: Optional[Callable[[str], None]]) -> None:
    """
    ---- Summary ----
    Main function to register what is told which step of the guide starts: the window
    registers itself while it is open.

    ---- Inputs ----
    teller : Optional[Callable[[str], None]]
        Function called with the key of each step as it starts; None to register
        nothing (when the window closes).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    _step_teller (module state).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _step_teller
    _step_teller = teller


# ---- guide_step_starter --------------------------------------------------------------
def guide_step_starter(key: str) -> None:
    """
    ---- Summary ----
    Main function to say that a step of the guide starts (the keys and their order are
    in utils_viewer/viewer_guide.py, GUIDE_STEPS), so the guide on the left opens it.

    ---- Inputs ----
    key : str
        Key of the step, such as 'trim' or 'delta_psi'.

    ---- Globals read ----
    _step_teller (module state).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    _current_step (module state). Calls the registered function (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _current_step
    _current_step = key
    if _step_teller is not None:
        _step_teller(key)


# ---- heading_printer -----------------------------------------------------------------
def heading_printer(text: str) -> None:
    """
    ---- Summary ----
    Main function to print a plain heading, for example the summary.

    ---- Inputs ----
    text : str
        Heading text.

    ---- Globals read ----
    COLOUR_SECTION (module constant); text_colourer.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    print(f"\n{text_colourer(text, COLOUR_SECTION)}\n{'-' * len(text)}")


# ---- info_printer --------------------------------------------------------------------
def info_printer(text: str, depth: int = 1, tight: bool = False) -> None:
    """
    ---- Summary ----
    Main function to print an information line (not a question) in the quieter colour,
    indented to sit under the question above. A line already coloured (a warning)
    keeps its own colour.

    ---- Inputs ----
    text : str
        Text to print or process.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    tight : bool
        True to make the next question follow this line without a blank line.

    ---- Globals read ----
    COLOUR_QUIET, INDENT (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal and sets the module flag _tight_next (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    global _tight_next
    print(f'{INDENT * (depth - 1)}{text_colourer(text, COLOUR_QUIET)}')
    _tight_next = tight


# ---- multi_asker ---------------------------------------------------------------------
def multi_asker(question: str,
                options: Sequence[str],
                default_all: bool = True,
                keep_order: bool = False,
                depth: int = 1,
                default_values: Optional[Sequence[str]] = None,
                label_formatter: Optional[Callable[[str], str]] = None,
                number: Optional[str] = None,
                ) -> List[str]:
    """
    ---- Summary ----
    Main function to ask a question answered by choosing several numbered options. A
    quieter line above says to type numbers separated by commas; the end of the
    question gives the numbers as for one choice, and the options Enter gives are
    brighter in the list.

    ---- Inputs ----
    question : str
        Question text, without its number.
    options : Sequence[str]
        Option names, shown as 1), 2), ...
    default_all : bool
        True to choose all options when only Enter is pressed and nothing is remembered.
    keep_order : bool
        True to return the options in the order typed instead of list order.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    default_values : Optional[Sequence[str]]
        Choice from last time, used for Enter when given.
    label_formatter : Optional[Callable[[str], str]]
        Function that changes how an option is shown, not what is returned.
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '5.4.1'; None to
        number it in the order asked.

    ---- Globals read ----
    NUMBERS_NOTE (module constant).

    ---- Outputs ----
    List[str]
        The chosen options.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _input_reader
    _list_ending_builder
    _number_depth_finder
    _numbers_hint_builder
    _options_printer
    _question_printer
    retry_teller
    """

    # ---- 1 Work out the defaults -----------------------------------------------------
    depth = _number_depth_finder(number, depth)
    remembered = [v for v in (default_values or []) if v in options]
    fallback = remembered or (list(options) if default_all else [])

    # ---- 2 Print the question and options --------------------------------------------
    indent = _question_printer(question,
                               depth,
                               _list_ending_builder(len(options), None),
                               NUMBERS_NOTE if _answer_requester is None
                               else CLICK_MULTI_NOTE,
                               number=number,
                               )
    shown = [label_formatter(label) if label_formatter else label for label in options]
    _options_printer(shown, indent, {options.index(v) + 1 for v in fallback})
    _answer_announcer('multi', shown, [options.index(v) + 1 for v in fallback])

    # ---- 3 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent)
        if not answer and fallback:
            return list(fallback)
        picked = [p for p in re.split(r'[,\s]+', answer) if p]
        if picked and all(p.isdigit() and 1 <= int(p) <= len(options) for p in picked):
            numbers = (list(dict.fromkeys(int(p) - 1 for p in picked))
                       if keep_order
                       else sorted({int(p) - 1 for p in picked})
                       )
            return [options[i] for i in numbers]
        retry_teller(_numbers_hint_builder(len(options)), depth)


# ---- number_asker --------------------------------------------------------------------
def number_asker(question: str,
                 default: Optional[float] = None,
                 minimum: Optional[float] = None,
                 maximum: Optional[float] = None,
                 exclusive_minimum: bool = False,
                 allow_blank: bool = False,
                 depth: int = 1,
                 span_reader: Optional[Callable[[str, float, float],
                                                Optional[float]]] = None,
                 is_whole: bool = False,
                 number: Optional[str] = None,
                 ) -> Optional[float]:
    """
    ---- Summary ----
    Main function to ask a question answered with a number, waiting until the value is
    valid; after a wrong answer one sentence says what to type. The end of the question
    gives what Enter gives, [120] or [skip], and a unit in brackets is highlighted. A
    question that can be answered with the mouse says so to the window, where a drag
    (``span_reader``) across the plot then writes the answer it gives into the answer
    box.

    ---- Inputs ----
    question : str
        Question text, without its number.
    default : Optional[float]
        Answer used when only Enter is pressed.
    minimum : Optional[float]
        Smallest accepted value.
    maximum : Optional[float]
        Largest accepted value.
    exclusive_minimum : bool
        True when the minimum itself is not accepted.
    allow_blank : bool
        True to accept an empty answer as None when there is no default; shown as
        [skip].
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    span_reader : Optional[Callable[[str, float, float], Optional[float]]]
        Turns a drag across the plot into the answer: (file shown, start min, end min)
        -> answer, or None when that drag gives none. None when the mouse gives
        nothing.
    is_whole : bool
        True when only whole numbers are accepted.
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '3.4.3'; None to
        number it in the order asked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The number, the default, or None for an accepted empty answer.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _brightener
    _input_reader
    _limits_checker
    _number_depth_finder
    _number_hint_builder
    _question_printer
    _time_announcer
    retry_teller
    typed_number_reader
    """

    # ---- 1 Write what Enter gives ----------------------------------------------------
    depth = _number_depth_finder(number, depth)
    if isinstance(default, (int, float)):
        ending = f'[{_brightener(f"{default:g}")}]'
    else:
        ending = f"[{_brightener('skip')}]" if allow_blank else ''

    # ---- 2 Print the question --------------------------------------------------------
    indent = _question_printer(question, depth, ending, has_unit=True, number=number)
    _answer_announcer('number',
                      value=f'{default:g}' if isinstance(default, (int, float)) else '',
                      )

    # ---- 3 Read and check the answer -------------------------------------------------
    hint = _number_hint_builder(minimum, maximum, exclusive_minimum, is_whole)
    if span_reader is not None:
        _time_announcer('span', span_reader)
    try:
        while True:
            answer = _input_reader(question, indent)
            if not answer:
                if default is not None:
                    return default
                if allow_blank:
                    return None
                retry_teller(hint, depth)
                continue
            value = typed_number_reader(answer)
            if value is None or not _limits_checker(value,
                                                    minimum,
                                                    maximum,
                                                    exclusive_minimum,
                                                    is_whole,
                                                    ):
                retry_teller(hint, depth)
                continue
            return value
    finally:
        if span_reader is not None:
            _time_announcer(None, None)


# ---- numbering_getter ----------------------------------------------------------------
def numbering_getter(depth: int) -> int:
    """
    ---- Summary ----
    Main function to read the current number at a depth, so it can be restored with
    numbering_setter after questions are asked again.

    ---- Inputs ----
    depth : int
        Numbering depth to read (0 = the section number).

    ---- Globals read ----
    _counters (module state).

    ---- Outputs ----
    int
        Current number at that depth.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return _counters[depth]


# ---- numbering_setter ----------------------------------------------------------------
def numbering_setter(depth: int, value: int) -> None:
    """
    ---- Summary ----
    Main function to set the current number at a depth, for example so the next
    sub-questions are numbered 3.4.3.1.

    ---- Inputs ----
    depth : int
        Numbering depth to set.
    value : int
        Number to make current at that depth.

    ---- Globals read ----
    MAX_DEPTH (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets and resets entries of the module counters _counters (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    _counters[depth] = value
    for level in range(depth + 1, MAX_DEPTH):
        _counters[level] = 0


# ---- path_cleaner --------------------------------------------------------------------
def path_cleaner(text: str) -> str:
    r"""
    ---- Summary ----
    Main function to clean a path typed or dragged into the window by removing
    surrounding quotes and spaces, and, on macOS and Linux, the backslashes that
    Terminal puts before spaces and other characters when a folder is dragged in.

    ---- Inputs ----
    text : str
        Text as received from the terminal.

    ---- Globals read ----
    os.name.

    ---- Outputs ----
    str
        Path text without surrounding quotes or spaces, or shell escapes.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    text = text.strip().strip('"').strip("'").strip()
    if os.name != 'nt':  # on Windows the backslash separates folders
        text = re.sub(r'\\(.)', r'\1', text)
    return text


# ---- progress_clearer ----------------------------------------------------------------
def progress_clearer() -> None:
    """
    ---- Summary ----
    Main function to remove the progress line from the terminal.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    print('\r' + ' ' * 100 + '\r', end='', flush=True)


# ---- progress_printer ----------------------------------------------------------------
def progress_printer(text: str) -> None:
    """
    ---- Summary ----
    Main function to show a one-line progress message, in the quieter colour, that the
    next message overwrites.

    ---- Inputs ----
    text : str
        Message to show.

    ---- Globals read ----
    COLOUR_QUIET (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal without a new line (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    print(f'\r{text_colourer(text.ljust(99), COLOUR_QUIET)}', end='', flush=True)


# ---- retry_teller --------------------------------------------------------------------
def retry_teller(hint: str, depth: int = 1) -> None:
    """
    ---- Summary ----
    Main function to say, after a wrong answer, in one sentence what to type; the
    question is not printed again and waits for the next answer.

    ---- Inputs ----
    hint : str
        One sentence, for example "Type y or n.".
    depth : int
        Numbering depth of the question it answers (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    COLOUR_RETRY, INDENT (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    print(f'{INDENT * (depth - 1)}{text_colourer(hint, COLOUR_RETRY)}')


# ---- section_starter -----------------------------------------------------------------
def section_starter(title: str) -> None:
    """
    ---- Summary ----
    Main function to start the next numbered section and print its heading.

    ---- Inputs ----
    title : str
        Section title, without its number.

    ---- Globals read ----
    COLOUR_SECTION, MAX_DEPTH (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Advances the module numbering counters _counters and prints the heading (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    _counters[0] += 1
    for level in range(1, MAX_DEPTH):
        _counters[level] = 0
    text = f'{_counters[0]}. {title}'
    print(f"\n{text_colourer(text, COLOUR_SECTION)}\n{'-' * len(text)}")


# ---- text_asker ----------------------------------------------------------------------
def text_asker(question: str,
               default: Optional[str] = None,
               depth: int = 1,
               checker: Optional[Callable[[Optional[str]], Optional[str]]] = None,
               number: Optional[str] = None,
               ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to ask a question answered with a line of text. An answer the checker
    refuses gets its one sentence of what to type, and the question waits for the next
    answer. A folder is asked with folder_asker.

    ---- Inputs ----
    question : str
        Question text, without its number.
    default : Optional[str]
        Answer used when only Enter is pressed; shown brighter as [default].
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    checker : Optional[Callable[[Optional[str]], Optional[str]]]
        Takes the answer (the default for Enter) and gives None when it can be used,
        or the sentence saying what to type instead; None accepts every answer.
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '1.2'; None to number
        it in the order asked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The typed text, or the default when Enter is pressed.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _brightener
    _input_reader
    _number_depth_finder
    _question_printer
    retry_teller
    """

    depth = _number_depth_finder(number, depth)
    ending = f'[{_brightener(default)}]' if default not in (None, '') else ''
    indent = _question_printer(question, depth, ending, number=number)
    _answer_announcer('text', value=default or '')
    while True:
        answer = _input_reader(question, indent) or default
        hint = checker(answer) if checker is not None else None
        if hint is None:
            return answer
        retry_teller(hint, depth)


# ---- text_colourer -------------------------------------------------------------------
def text_colourer(text: str, code: str = COLOUR_QUESTION) -> str:
    """
    ---- Summary ----
    Main function to wrap text in a colour code, which the window's terminal shows.

    ---- Inputs ----
    text : str
        Text to colour.
    code : str
        ANSI colour code (COLOUR_QUESTION by default).

    ---- Globals read ----
    COLOUR_QUESTION, RESET (module constants).

    ---- Outputs ----
    str
        The coloured text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return f'{code}{text}{RESET}'


# ---- text_italiser -------------------------------------------------------------------
def text_italiser(text: str) -> str:
    """
    ---- Summary ----
    Main function to write text in italics, which the window's terminal shows.

    ---- Inputs ----
    text : str
        Text to put in italics.

    ---- Globals read ----
    ITALIC, RESET (module constants).

    ---- Outputs ----
    str
        The italic text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return f'{ITALIC}{text}{RESET}'


# ---- time_request_setter -------------------------------------------------------------
def time_request_setter(requester: Optional[Callable[[Optional[str],
                                                      Optional[Callable],
                                                      ],
                                                     None,
                                                     ]],
                        ) -> None:
    """
    ---- Summary ----
    Main function to register what is told when a question can be answered with the
    mouse: the window registers itself while it is open, so a drag across its plot can
    give the answer.

    ---- Inputs ----
    requester : Optional[Callable[[Optional[str], Optional[Callable]], None]]
        Function called with ('span', reader) when a question starts waiting for an
        answer the mouse can give, and with (None, None) when it has its answer (see
        _time_announcer); None to register nothing (when the window closes).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    _time_requester (module state).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _time_requester
    _time_requester = requester


# ---- typed_number_reader -------------------------------------------------------------
def typed_number_reader(text: str) -> Optional[float]:
    """
    ---- Summary ----
    Main function to read a typed number, the one reader of the answer box, the OD
    table and the boxes of the strip: spaces around it are ignored and a comma may be
    the decimal sign. Each place checks its own limits.

    ---- Inputs ----
    text : str
        What was typed, for example '2.5', ' 2,5 ' or '1e3'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The number, or None for an empty text, a text that is not a number, "nan" or an
        infinity.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    cleaned = text.strip().replace(',', '.')
    if not cleaned:
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


# ---- yes_no_asker --------------------------------------------------------------------
def yes_no_asker(question: str,
                 default: bool = False,
                 depth: int = 1,
                 note: str = '',
                 number: Optional[str] = None,
                 ) -> bool:
    """
    ---- Summary ----
    Main function to ask a yes or no question, ending in (y/N) or (Y/n) with the letter
    Enter gives brighter.

    ---- Inputs ----
    question : str
        Question text, without its number.
    default : bool
        Answer used when only Enter is pressed (the capital letter at the end).
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    note : str
        A line said just above the question in the quieter colour; may be empty.
    number : Optional[str]
        The question's own number from QUESTION_FLOW.md, such as '3.1'; None to number
        it in the order asked.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True for y or yes, False for n or no (in any capitals), the default for Enter.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters when it has no number of its own.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answer_announcer
    _brightener
    _input_reader
    _number_depth_finder
    _question_printer
    retry_teller
    """

    # ---- 1 Print the question --------------------------------------------------------
    depth = _number_depth_finder(number, depth)
    ending = f"({_brightener('Y')}/n)" if default else f"(y/{_brightener('N')})"
    indent = _question_printer(question, depth, ending, note, number=number)
    _answer_announcer('yesno', default='y' if default else 'n')

    # ---- 2 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent).lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        retry_teller('Type y or n.', depth)
