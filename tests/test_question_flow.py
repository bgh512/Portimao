"""
Tests that every question is in QUESTION_FLOW.md, worded and numbered as in the code.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import ast
import re
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CODE_PATTERNS = ('main.py',
                 'utils_shared/*.py',
                 'utils_viewer/*.py',
                 'utils_custom/*.py',
                 )
LIST_NAME = 'QUESTION_FLOW.md'
QUESTION_NAME = 'question'  # the input every asker and wrapper takes its question in
NUMBER_NAME = 'number'  # the input a question's own number is given in
MINIMUM_QUESTIONS = 50  # fewer found than this means the reading itself has broken
VARYING = '\x00'  # stands for a part filled in at run time ({name}, {time})
HANDED_ON = '\x01'  # stands for a number handed on from another input
NUMBERED_SECTIONS = ('1',
                     '2',
                     '3',
                     '4',
                     '5',
                     '9',
                     )  # every question here shows its number
NOT_YET_NUMBERED = ('5.8',)  # asked through the going-back list, renumbered with it


# ---- HELPERS -------------------------------------------------------------------------


# ---- _binding_resolver ---------------------------------------------------------------
def _binding_resolver(name: str,
                      function: ast.AST,
                      functions: List[ast.AST],
                      seen: FrozenSet[str],
                      ) -> Optional[List[str]]:
    """
    ---- Summary ----
    Helper function to find the texts a local variable can hold, from its assignments
    and from the loops that fill it out of a list written in the code.

    ---- Inputs ----
    name : str
        Name of the variable.
    function : ast.AST
        The function (or module) the variable lives in.
    functions : List[ast.AST]
        The functions around the place the variable is used, nearest first.
    seen : FrozenSet[str]
        Names already being followed, so a name defined by itself ends.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[List[str]]
        The texts, or None when any value cannot be read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _text_resolver
    """

    # ---- 1 Gather the values the name is given ---------------------------------------
    values: List[ast.AST] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                values.append(node.value)
        elif isinstance(node, ast.For) and isinstance(node.iter, (ast.Tuple, ast.List)):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                values.extend(node.iter.elts)
            elif isinstance(node.target, ast.Tuple):
                places = [i
                          for i, t in enumerate(node.target.elts)
                          if isinstance(t, ast.Name) and t.id == name
                          ]
                for row in node.iter.elts if places else []:
                    if not isinstance(row, (ast.Tuple, ast.List)):
                        return None
                    values.append(row.elts[places[0]])
    if not values:
        return None

    # ---- 2 Read each value -----------------------------------------------------------
    texts: List[str] = []
    for value in values:
        found = _text_resolver(value, functions, seen | {name})
        if found is None:
            return None
        texts.extend(found)
    return texts


# ---- _carrier_finder -----------------------------------------------------------------
def _carrier_finder(trees: Dict[str, ast.Module]) -> Dict[str, int]:
    """
    ---- Summary ----
    Helper function to find every function that takes a question: the askers and the
    wrappers that hand a question on to them.

    ---- Inputs ----
    trees : Dict[str, ast.Module]
        {file name: parsed code}.

    ---- Globals read ----
    QUESTION_NAME (module constant).

    ---- Outputs ----
    Dict[str, int]
        {function name: position of its question input}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    carriers: Dict[str, int] = {}
    for tree in trees.values():
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names = [a.arg for a in node.args.posonlyargs + node.args.args]
                if QUESTION_NAME in names:
                    carriers[node.name] = names.index(QUESTION_NAME)
    return carriers


# ---- _list_reader --------------------------------------------------------------------
def _list_reader() -> str:
    """
    ---- Summary ----
    Helper function to read the question list as plain text: without the marks for
    italics, bold and code, and with single spaces.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, LIST_NAME (module constants).

    ---- Outputs ----
    str
        The text of the list.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    text = (ROOT / LIST_NAME).read_text(encoding='utf-8')
    return ' '.join(re.sub(r'[*`]', '', text).split())


# ---- _number_matcher -----------------------------------------------------------------
def _number_matcher(number: str,
                    question: str,
                    rows: List[Tuple[str, str]],
                    ) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a question sits in a row of its own number in the
    list, in the same words: in the row's question, or in a cell of that row for a
    question asked inside its step (a name for each component, replacing a file).

    ---- Inputs ----
    number : str
        The number the code gives the question, such as '3.5'.
    question : str
        Question text from the code, with VARYING for each part filled in at run time.
    rows : List[Tuple[str, str]]
        The numbered rows of the list from _row_reader.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when a row of that number holds the question.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _rows_finder
    """

    return number in _rows_finder(question, rows)


# ---- _question_collector -------------------------------------------------------------
def _question_collector() -> Tuple[List[Tuple[str, str, Optional[str]]], List[str]]:
    """
    ---- Summary ----
    Helper function to collect the text of every question in the code, without running
    it: the question given in each call to a function that takes one, with the number
    written in that call, and each 'question' entry of a dictionary.

    ---- Inputs ----
    None.

    ---- Globals read ----
    HANDED_ON, NUMBER_NAME, QUESTION_NAME (module constants).

    ---- Outputs ----
    Tuple[List[Tuple[str, str, Optional[str]]], List[str]]
        ([(question text, 'file:line', its own number or None)], ['file:line' of each
        question that could not be read]). VARYING stands for each part filled in at
        run time. A number handed on from another input is not one written in the call,
        so it gives HANDED_ON.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _carrier_finder
    _text_resolver
    _tree_reader
    """

    # ---- 1 Read the code and find the functions that take a question -----------------
    trees = _tree_reader()
    carriers = _carrier_finder(trees)

    # ---- 2 Take the question from every call and dictionary --------------------------
    questions: List[Tuple[str, str, Optional[str]]] = []
    unreadable: List[str] = []
    for file_name, tree in trees.items():
        for node in ast.walk(tree):
            values: List[Optional[ast.AST]] = []
            number = None
            if isinstance(node, ast.Call):
                name = getattr(node.func, 'id', getattr(node.func, 'attr', None))
                if name not in carriers:
                    continue
                given = [k.value for k in node.keywords if k.arg == NUMBER_NAME]
                if (given and
                    isinstance(given[0], ast.Constant) and
                    isinstance(given[0].value, str)
                    ):
                    number = given[0].value
                elif given and not (isinstance(given[0], ast.Constant) and
                                    given[0].value is None
                                    ):
                    number = HANDED_ON
                keyword = [k.value for k in node.keywords if k.arg == QUESTION_NAME]
                place = carriers[name]
                if keyword:
                    values.append(keyword[0])
                elif (place < len(node.args) and
                      not any(isinstance(a, ast.Starred) for a in node.args)
                      ):
                    values.append(node.args[place])
                else:
                    values.append(None)
            elif isinstance(node, ast.Dict):
                values.extend(v
                              for k, v in zip(node.keys, node.values)
                              if isinstance(k, ast.Constant) and k.value == QUESTION_NAME
                              )
            for value in values:
                where = f'{file_name}:{node.lineno}'
                texts = (None
                         if value is None
                         else _text_resolver(value, node.functions, frozenset())
                         )
                if texts is None:
                    unreadable.append(where)
                else:
                    questions.extend((text, where, number) for text in texts)
    return questions, unreadable


# ---- _question_matcher ---------------------------------------------------------------
def _question_matcher(question: str, list_text: str) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a question is in the list in the same words. The
    parts filled in at run time match any words.

    ---- Inputs ----
    question : str
        Question text from the code, with VARYING for each part filled in at run time.
    list_text : str
        Text of the list from _list_reader.

    ---- Globals read ----
    VARYING (module constant).

    ---- Outputs ----
    bool
        True when the question is in the list.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    parts = ' '.join(question.split()).split(VARYING)
    return re.search('.+?'.join(re.escape(part) for part in parts),
                     list_text,
                     ) is not None


# ---- _row_reader ---------------------------------------------------------------------
def _row_reader() -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to read the numbered rows of the question list, each as plain text
    without the marks for italics, bold and code, and with single spaces.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, LIST_NAME (module constants).

    ---- Outputs ----
    List[Tuple[str, str]]
        [(the row's number, such as '4.1.7', the text of the whole row)], in the
        order of the list.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    rows: List[Tuple[str, str]] = []
    for line in (ROOT / LIST_NAME).read_text(encoding='utf-8').splitlines():
        text = ' '.join(re.sub(r'[*`]', '', line).split())
        found = re.match(r'\| (\d+(?:\.\d+)*) \|', text)
        if found:
            rows.append((found.group(1), text))
    return rows


# ---- _rows_finder --------------------------------------------------------------------
def _rows_finder(question: str, rows: List[Tuple[str, str]]) -> List[str]:
    """
    ---- Summary ----
    Helper function to find the numbers of the rows of the list that hold a question in
    the same words, anywhere in the row. The parts filled in at run time match any
    words within one cell.

    ---- Inputs ----
    question : str
        Question text from the code, with VARYING for each part filled in at run time.
    rows : List[Tuple[str, str]]
        The numbered rows of the list from _row_reader.

    ---- Globals read ----
    VARYING (module constant).

    ---- Outputs ----
    List[str]
        The numbers of the rows that hold the question, in the order of the list.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    parts = ' '.join(question.split()).split(VARYING)
    pattern = '[^|]+?'.join(re.escape(part) for part in parts)
    return [number for number, text in rows if re.search(pattern, text)]


# ---- _text_resolver ------------------------------------------------------------------
def _text_resolver(node: ast.AST,
                   functions: List[ast.AST],
                   seen: FrozenSet[str],
                   ) -> Optional[List[str]]:
    """
    ---- Summary ----
    Helper function to read the question texts an expression can give.

    ---- Inputs ----
    node : ast.AST
        The expression given as the question.
    functions : List[ast.AST]
        The functions around the expression, nearest first, the module last.
    seen : FrozenSet[str]
        Names already being followed.

    ---- Globals read ----
    QUESTION_NAME, VARYING (module constants).

    ---- Outputs ----
    Optional[List[str]]
        The texts; an empty list for a question handed on from the function's own
        question input or read from a 'question' entry (it is collected where it is
        first written); None when the expression cannot be read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _binding_resolver
    """

    # ---- 1 Text written in place -----------------------------------------------------
    if isinstance(node, ast.Constant):
        return [node.value] if isinstance(node.value, str) else None
    if isinstance(node, ast.JoinedStr):
        return [''.join(part.value if isinstance(part, ast.Constant) else VARYING
                        for part in node.values
                        ),
                ]

    # ---- 2 A choice between expressions ----------------------------------------------
    if isinstance(node, (ast.BoolOp, ast.IfExp)):
        options = node.values if isinstance(node, ast.BoolOp) else [node.body,
                                                                    node.orelse,
                                                                    ]
        texts: List[str] = []
        for option in options:
            found = _text_resolver(option, functions, seen)
            if found is None:
                return None
            texts.extend(found)
        return texts

    # ---- 3 A 'question' entry read back from a dictionary ----------------------------
    if (isinstance(node, ast.Call) and
        getattr(node.func, 'attr', None) == 'get' and
        node.args and
        isinstance(node.args[0], ast.Constant) and
        node.args[0].value == QUESTION_NAME
        ):
        return []

    # ---- 4 A name: the function's own input, or a local variable ---------------------
    if isinstance(node, ast.Name) and node.id not in seen:
        for function in functions:
            arguments = getattr(function, 'args', None)
            if arguments and node.id in [a.arg for a in ast.walk(arguments)
                                         if isinstance(a, ast.arg)
                                         ]:
                return [] if node.id == QUESTION_NAME else None
            found = _binding_resolver(node.id, function, functions, seen)
            if found is not None:
                return found
    return None


# ---- _tree_reader --------------------------------------------------------------------
def _tree_reader() -> Dict[str, ast.Module]:
    """
    ---- Summary ----
    Helper function to parse the program's code files and note, on every part, the
    functions it sits in.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, CODE_PATTERNS (module constants).

    ---- Outputs ----
    Dict[str, ast.Module]
        {file name from the project folder: parsed code}. Every node has a
        ``functions`` list: the functions around it, nearest first, the module last.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    trees: Dict[str, ast.Module] = {}
    for pattern in CODE_PATTERNS:
        for path in sorted(ROOT.glob(pattern)):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            tree.functions = [tree]
            for node in ast.walk(tree):  # parents come before their children
                inside = ([node] + node.functions
                          if isinstance(node, (ast.FunctionDef, ast.Lambda))
                          else node.functions
                          )
                for child in ast.iter_child_nodes(node):
                    child.functions = inside
            trees[path.relative_to(ROOT).as_posix()] = tree
    return trees


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_question_texts_can_be_read -------------------------------------------------
def test_question_texts_can_be_read() -> None:
    """
    ---- Summary ----
    Main function to check that the text of every question can be read from the code,
    so that none escapes the check against the list.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MINIMUM_QUESTIONS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _question_collector
    """

    questions, unreadable = _question_collector()
    assert not unreadable, (
        'The question text cannot be read at: ' + ', '.join(unreadable) + '. Write the '
        'text in the call, or hand it on through an input called "question".'
    )
    assert len(questions) >= MINIMUM_QUESTIONS, (
        f'Only {len(questions)} questions were found in the code, so the test is no '
        'longer reading them all.'
    )


# ---- test_questions_are_in_the_list --------------------------------------------------
def test_questions_are_in_the_list() -> None:
    """
    ---- Summary ----
    Main function to check that every question in the code is in QUESTION_FLOW.md in
    the same words.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VARYING, LIST_NAME (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _list_reader
    _question_collector
    _question_matcher
    """

    list_text = _list_reader()
    questions, _ = _question_collector()
    missing = [f"{where}: {' '.join(text.split()).replace(VARYING, '...')}"
               for text, where, _ in questions
               if not _question_matcher(text, list_text)
               ]
    assert not missing, (
        f'{len(missing)} question(s) are not in {LIST_NAME} in these words:\n'
        + '\n'.join(missing)
    )


# ---- test_question_numbers_match_the_list --------------------------------------------
def test_question_numbers_match_the_list() -> None:
    """
    ---- Summary ----
    Main function to check that every question the code gives its own number sits in
    the row of that number in QUESTION_FLOW.md, so the number on screen is the number
    in the list.

    ---- Inputs ----
    None.

    ---- Globals read ----
    HANDED_ON, VARYING, LIST_NAME (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_matcher
    _question_collector
    _row_reader
    """

    rows = _row_reader()
    questions, _ = _question_collector()
    numbered = [(text, where, number)
                for text, where, number in questions
                if number and number != HANDED_ON
                ]
    assert numbered, (
        'No question in the code is given its own number, so the test is no longer '
        'reading the numbers.'
    )
    wrong = [f"{where}: {number} {' '.join(text.split()).replace(VARYING, '...')}"
             for text, where, number in numbered
             if not _number_matcher(number, text, rows)
             ]
    assert not wrong, (
        f'{len(wrong)} question(s) are not in the row of their number in {LIST_NAME}:\n'
        + '\n'.join(wrong)
    )


# ---- test_questions_have_their_own_number --------------------------------------------
def test_questions_have_their_own_number() -> None:
    """
    ---- Summary ----
    Main function to check that every question of the numbered sections of
    QUESTION_FLOW.md (set-up to experiment export, and the summary) is given its own
    number in the code, so none is shown on screen without it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LIST_NAME, NOT_YET_NUMBERED, NUMBERED_SECTIONS, VARYING (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _question_collector
    _row_reader
    _rows_finder
    """

    rows = _row_reader()
    questions, _ = _question_collector()
    missing = []
    for text, where, number in questions:
        if number:
            continue
        found = [n
                 for n in _rows_finder(text, rows)
                 if n.split('.')[0] in NUMBERED_SECTIONS and n not in NOT_YET_NUMBERED
                 ]
        if found:
            missing.append(f"{where}: {' '.join(text.split()).replace(VARYING, '...')} "
                           f"(row {found[0]})",
                           )
    assert not missing, (
        f'{len(missing)} question(s) of the numbered sections of {LIST_NAME} are not '
        'given their own number in the code:\n' + '\n'.join(missing)
    )
