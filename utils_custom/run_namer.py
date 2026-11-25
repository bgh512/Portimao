"""
Experiment (run) name parsing: conditions, run numbers, groups and hours.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from typing import Optional, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.user_notices import warning_shower


# ---- CONSTANTS -----------------------------------------------------------------------
ORDER_TITLES = {'kcn_then_bd': 'KCN → BD', 'bd_then_kcn': 'BD → KCN'}
RUN_NAME_PATTERN = re.compile(r'^(?P<condition>.*?)[\s_-]*run[\s_-]*(?P<run>\d+)\s*$',
                              re.IGNORECASE,
                              )
HOURS_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b', re.IGNORECASE)
# a lone number at the end of a name (wt_2), read as the run number when the name has
# no run<N>
LAST_NUMBER_PATTERN = re.compile(r'^(?P<condition>.*?)[\s_-]+(?P<run>\d+)\s*$')
SEPARATORS = ' _-'


# ---- RUN NAMER HELPERS ---------------------------------------------------------------


# ---- _group_matcher ------------------------------------------------------------------
def _group_matcher(name: str, groups: Sequence[str]) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find the first group word that appears in an experiment name.

    ---- Inputs ----
    name : str
        Experiment name.
    groups : Sequence[str]
        Group names in priority order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        Matching group, or None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    lowered = str(name).lower()
    words = re.split(r'[^a-z0-9]+', lowered)
    for group in groups:
        if group.lower() in words or lowered.startswith(group.lower()):
            return group
    return None


# ---- _natural_sorter -----------------------------------------------------------------
def _natural_sorter(name: str) -> list:
    """
    ---- Summary ----
    Helper function to build a sort key that orders numbers inside names numerically.

    ---- Inputs ----
    name : str
        Name to sort.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Alternating text and integer parts.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', str(name))
            ]


# ---- _order_sorter -------------------------------------------------------------------
def _order_sorter(item: tuple, groups: Sequence[str]) -> tuple:
    """
    ---- Summary ----
    Helper function to build the sort key of one (group, name, experiment) item.

    ---- Inputs ----
    item : tuple
        (group, name, experiment).
    groups : Sequence[str]
        Group names in the wanted order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (group index, no-hours flag, hours, natural name key).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _natural_sorter
    hours_parser
    """

    hours = hours_parser(item[1])
    return (list(groups).index(item[0]),
            hours is None,
            hours or 0.0,
            _natural_sorter(item[1]),
            )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- condition_classifier ------------------------------------------------------------
def condition_classifier(condition: str) -> tuple:
    """
    ---- Summary ----
    Main function to identify the strain and the addition order from a condition name.

    ---- Inputs ----
    condition : str
        Condition name such as 'knockdown_kcn_then_bd'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (strain, order). strain is 'knockdown' (the word knockdown or a kd token),
        'control' or None; order is 'bd_then_kcn' or 'kcn_then_bd' from the position of
        the bd and kcn tokens, or None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Split the condition into words --------------------------------------------
    text = str(condition).lower()
    tokens = [token for token in re.split(r'[^a-z0-9]+', text) if token]

    # ---- 2 Find the strain -----------------------------------------------------------
    if 'knockdown' in text or 'kd' in tokens:
        strain = 'knockdown'
    elif 'control' in text:
        strain = 'control'
    else:
        strain = None

    # ---- 3 Find the order ------------------------------------------------------------
    order = None
    if 'bd' in tokens and 'kcn' in tokens:
        order = ('bd_then_kcn'
                 if tokens.index('bd') < tokens.index('kcn')
                 else 'kcn_then_bd'
                 )
    return strain, order


# ---- condition_grouper ---------------------------------------------------------------
def condition_grouper(experiments: dict) -> dict:
    """
    ---- Summary ----
    Main function to group experiments by condition and run number.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {condition: {run number: experiment}}. Experiments without a run suffix are
        skipped with a warning; a duplicate run number raises ValueError.

    ---- Globals mutated ----
    None. Shows a warning for each experiment skipped (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    run_name_parser
    warning_shower
    """

    # ---- 1 Prepare the groups --------------------------------------------------------
    groups = {}

    # ---- 2 Assign each experiment to a condition -------------------------------------
    for name, experiment in experiments.items():
        parsed = run_name_parser(name)
        if parsed is None:
            warning_shower(f"  Skipping {name}: name does not end in 'run<number>'.")
            continue
        condition, run = parsed
        if run in groups.setdefault(condition, {}):
            raise ValueError(f'Duplicate run{run} for condition {condition!r}. Check '
                             f'experiment names.',
                             )
        groups[condition][run] = experiment
    return groups


# ---- experiment_classifier -----------------------------------------------------------
def experiment_classifier(name: str) -> tuple:
    """
    ---- Summary ----
    Helper function to identify the strain, addition order and run number from an
    experiment name.

    ---- Inputs ----
    name : str
        Experiment name such as 'control_kcn_then_bd_run1'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (strain, order, run); entries are None where they cannot be identified.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    condition_classifier
    run_name_parser
    """

    parsed = run_name_parser(name)
    if parsed is None:
        return None, None, None
    condition, run = parsed
    strain, order = condition_classifier(condition)
    return strain, order, run


# ---- file_name_reader ----------------------------------------------------------------
def file_name_reader(name: str) -> Tuple[str, str, str, Optional[int]]:
    """
    ---- Summary ----
    Main function to read from an experiment name what the dataset set-up table is
    filled in with: the run number from its end, the time point from a number of
    hours, and the two groups from what is left.

    ---- Inputs ----
    name : str
        Experiment name (the .paf file name without the extension), for example
        'control-bd_then_kcn-run2', 'knockdown_24hours' or 'WT_8umlDAP_2'.

    ---- Globals read ----
    HOURS_PATTERN, LAST_NUMBER_PATTERN, ORDER_TITLES, RUN_NAME_PATTERN, SEPARATORS
    (module constants).

    ---- Outputs ----
    Tuple[str, str, str, Optional[int]]
        (Group 1, Group 2, time point, run number). A part the name does not show is
        '' (None for the run number). The time point is written '<hours> h'; an
        addition order (bd_then_kcn) is written as in ORDER_TITLES.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 The run number: run<N> at the end, else a lone number at the end ----------
    text, run = str(name).strip(), None
    for pattern in (RUN_NAME_PATTERN, LAST_NUMBER_PATTERN):
        match = pattern.match(text)
        if match:
            text, run = match.group('condition'), int(match.group('run'))
            break

    # ---- 2 The time point: a number of hours -----------------------------------------
    time_point = ''
    match = HOURS_PATTERN.search(text)
    if match:
        time_point = f'{float(match.group(1)):g} h'
        before = text[:match.start()].rstrip(SEPARATORS)
        after = text[match.end():].lstrip(SEPARATORS)
        # what stood round the hours is joined as the name joins its own parts
        joiner = '-' if '-' in text else '_'
        text = joiner.join(part for part in (before, after) if part)

    # ---- 3 The groups: split at a hyphen if there is one, else at the first _ --------
    text = text.strip(SEPARATORS)
    separator = next((mark for mark in ('-', '_', ' ') if mark in text), None)
    if separator is None:
        group_1, group_2 = text, ''
    else:
        group_1, group_2 = text.split(separator, 1)
    group_1, group_2 = group_1.strip(SEPARATORS), group_2.strip(SEPARATORS)
    return group_1, ORDER_TITLES.get(group_2.lower(), group_2), time_point, run


# ---- group_assigner ------------------------------------------------------------------
def group_assigner(experiments: dict, groups: Sequence[str]) -> dict:
    """
    ---- Summary ----
    Main function to give every experiment a group from its name and to order the
    experiments by group and then by hours.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name (DATA_FORMAT.md).
    groups : Sequence[str]
        Group names in the order they should appear, for example
        ('control', 'knockdown'). An experiment belongs to the first group whose name
        is a word (or the start) of its name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Same experiments, ordered, each with a 'group' key added. Experiments that
        match no group are left out with a warning.

    ---- Globals mutated ----
    None. Adds the 'group' key to the experiment dictionaries and shows a warning for
    each experiment left out (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _group_matcher
    _order_sorter
    warning_shower
    """

    # ---- 1 Match the groups ----------------------------------------------------------
    found = []
    for name, experiment in experiments.items():
        group = _group_matcher(name, groups)
        if group is None:
            warning_shower(f'  Skipping {name}: its name does not contain any of the '
                           f'groups {list(groups)}.',
                           )
            continue
        experiment['group'] = group
        found.append((group, name, experiment))
    found.sort(key=lambda item: _order_sorter(item, groups))
    return {name: experiment for _, name, experiment in found}


# ---- hours_parser --------------------------------------------------------------------
def hours_parser(name: str) -> Optional[float]:
    """
    ---- Summary ----
    Main function to read the number of hours from an experiment name.

    ---- Inputs ----
    name : str
        Experiment name such as 'control_7hours'.

    ---- Globals read ----
    HOURS_PATTERN (module constant).

    ---- Outputs ----
    Optional[float]
        Hours, or None if the name has none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    match = HOURS_PATTERN.search(str(name))
    return float(match.group(1)) if match else None


# ---- run_name_lister -----------------------------------------------------------------
def run_name_lister(names: Sequence[str]) -> list:
    """
    ---- Summary ----
    Main function to describe how each experiment name is read by the haem and OCR
    response figures, for showing to the user before they choose.

    ---- Inputs ----
    names : Sequence[str]
        Experiment names (the .paf file names without the extension).

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        One dictionary per name: {name, condition, run, strain, order}; entries are
        None where the name does not identify them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    condition_classifier
    run_name_parser
    """

    # ---- 1 Prepare the rows ----------------------------------------------------------
    rows = []

    # ---- 2 Build a row for each run --------------------------------------------------
    for name in names:
        parsed = run_name_parser(name)
        condition, run = parsed if parsed else (None, None)
        strain, order = condition_classifier(condition) if condition else (None, None)
        rows.append({'name': name,
                     'condition': condition,
                     'run': run,
                     'strain': strain,
                     'order': order,
                     },
                    )
    return rows


# ---- run_name_parser -----------------------------------------------------------------
def run_name_parser(name: str) -> Optional[tuple]:
    """
    ---- Summary ----
    Main function to split an experiment name of the form <condition>_run<N> into its
    condition and run number.

    ---- Inputs ----
    name : str
        Experiment name, for example 'knockdown_kcn_then_bd_run1'.

    ---- Globals read ----
    RUN_NAME_PATTERN (module constant).

    ---- Outputs ----
    Optional[tuple]
        (condition, run number), or None if the name has no run suffix.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    match = RUN_NAME_PATTERN.match(str(name).strip())
    if not match:
        return None
    condition = match.group('condition').strip(' _-')
    return (condition, int(match.group('run'))) if condition else None
