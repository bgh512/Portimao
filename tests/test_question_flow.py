"""
Tests that every question the program can ask is in QUESTION_FLOW.md, in the same words.
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
MINIMUM_QUESTIONS = 50  # fewer found than this means the reading itself has broken
VARYING = '\x00'  # stands for a part filled in at run time ({name}, {time})


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


# ---- _question_collector -------------------------------------------------------------
def _question_collector() -> Tuple[List[Tuple[str, str]], List[str]]:
    """
    ---- Summary ----
    Helper function to collect the text of every question in the code, without running
    it: the question given in each call to a function that takes one, and each
    'question' entry of a dictionary.

    ---- Inputs ----
    None.

    ---- Globals read ----
    QUESTION_NAME (module constant).

    ---- Outputs ----
    Tuple[List[Tuple[str, str]], List[str]]
        ([(question text, 'file:line')], ['file:line' of each question that could not
        be read]). VARYING stands for each part filled in at run time.

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
    questions: List[Tuple[str, str]] = []
    unreadable: List[str] = []
    for file_name, tree in trees.items():
        for node in ast.walk(tree):
            values: List[Optional[ast.AST]] = []
            if isinstance(node, ast.Call):
                name = getattr(node.func, 'id', getattr(node.func, 'attr', None))
                if name not in carriers:
                    continue
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
                    questions.extend((text, where) for text in texts)
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
               for text, where in questions
               if not _question_matcher(text, list_text)
               ]
    assert not missing, (
        f'{len(missing)} question(s) are not in {LIST_NAME} in these words:\n'
        + '\n'.join(missing)
    )
