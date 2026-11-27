"""
The set-up of a dataset: which experiment is which (its groups, time point and replicate), filled in from the file names, with a colour per Group 1 label.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings


# ---- CONSTANTS -----------------------------------------------------------------------
# The cells of a row that hold a label, in the order of the table: (name of the value,
# column heading).
LABEL_COLUMNS = (('group_1', 'Group 1'),
                 ('group_2', 'Group 2'),
                 ('time_point', 'Time point'),
                 )
LABEL_KEYS = tuple(key for key, _ in LABEL_COLUMNS)
COLOUR_KEY = 'group_1'  # the column whose labels have a colour
GROUP_COUNT = 2  # the group columns the user may name
COLOUR_PATTERN = re.compile(r'^#[0-9a-fA-F]{6}$')
SET_JOINER = ' · '
NO_LABELS = 'no labels'  # the name of the set of the rows with every cell blank
# What a file name is read for (file_name_reader): run<N> at its end, or a lone number
# there (wt_2); a number of hours; an addition order, written as its title.
RUN_NAME_PATTERN = re.compile(r'^(?P<condition>.*?)[\s_-]*run[\s_-]*(?P<run>\d+)\s*$',
                              re.IGNORECASE,
                              )
LAST_NUMBER_PATTERN = re.compile(r'^(?P<condition>.*?)[\s_-]+(?P<run>\d+)\s*$')
HOURS_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b', re.IGNORECASE)
ORDER_TITLES = {'kcn_then_bd': 'KCN → BD', 'bd_then_kcn': 'BD → KCN'}
SEPARATORS = ' _-'


# ---- SETUP HELPERS -------------------------------------------------------------------


# ---- _label_matcher ------------------------------------------------------------------
def _label_matcher(label: str, known: List[str]) -> str:
    """
    ---- Summary ----
    Helper function to spell a label read from a file name as the same label is
    already spelt in its column, whatever its case (wt and WT are one label), and to
    note a new label as known.

    ---- Inputs ----
    label : str
        The label read from the name; '' for none.
    known : List[str]
        The labels of the column so far, in the order first seen; a new label is
        added to it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The label as first spelt.

    ---- Globals mutated ----
    None. Adds a new label to ``known`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not label:
        return ''
    for other in known:
        if other.lower() == label.lower():
            return other
    known.append(label)
    return label


# ---- _text_cleaner -------------------------------------------------------------------
def _text_cleaner(value: Any) -> str:
    """
    ---- Summary ----
    Helper function to give a saved or typed value as the text of a cell.

    ---- Inputs ----
    value : Any
        The value; anything that is not text counts as blank.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The text without the spaces round it; '' for a value that is not text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return value.strip() if isinstance(value, str) else ''


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- column_filler -------------------------------------------------------------------
def column_filler(rows: List[dict], key: str, first: int, last: int) -> List[dict]:
    """
    ---- Summary ----
    Main function to fill several rows of one column with the label of a cell: the
    cell clicked first, then every row up or down to the cell Shift-clicked.

    ---- Inputs ----
    rows : List[dict]
        The rows of the table (dataset_setup, DATA_FORMAT.md).
    key : str
        The column, one of LABEL_KEYS.
    first : int
        The row whose label is copied.
    last : int
        The row Shift-clicked; above or below ``first``.

    ---- Globals read ----
    LABEL_KEYS (module constant).

    ---- Outputs ----
    List[dict]
        The rows, those from ``first`` to ``last`` with the label of ``first`` in the
        column. The rows given are not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if key not in LABEL_KEYS:
        raise ValueError(f'{key!r} is not a column of labels of the set-up table.')
    if not (0 <= first < len(rows) and 0 <= last < len(rows)):
        raise ValueError(f'The table has no rows {first} and {last}.')
    low, high = min(first, last), max(first, last)
    return [dict(row, **{key: rows[first][key]}) if low <= place <= high else dict(row)
            for place, row in enumerate(rows)
            ]


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


# ---- group_colours_filler ------------------------------------------------------------
def group_colours_filler(rows: List[dict], colours: Dict[str, str]) -> Dict[str, str]:
    """
    ---- Summary ----
    Main function to give every Group 1 label of the table a colour: a label keeps
    the colour it has, and a new one takes the first colour of the list no label of
    the table has (the list starts again once every colour is taken).

    ---- Inputs ----
    rows : List[dict]
        The rows of the table (dataset_setup, DATA_FORMAT.md).
    colours : Dict[str, str]
        {Group 1 label: colour as '#rrggbb'} so far.

    ---- Globals read ----
    COLOUR_KEY (module constant); settings.GROUP_COLOURS.

    ---- Outputs ----
    Dict[str, str]
        {Group 1 label: colour} for the labels of the table, in the order first seen;
        a colour of a label no longer in the table is left out.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    labels_lister
    """

    labels = labels_lister(rows, COLOUR_KEY)
    filled = {label: colours[label] for label in labels if label in colours}
    for label in labels:
        if label in filled:
            continue
        free = [colour
                for colour in settings.GROUP_COLOURS
                if colour not in filled.values()
                ]
        filled[label] = (free[0]
                         if free
                         else settings.GROUP_COLOURS[len(filled)
                                                     % len(settings.GROUP_COLOURS)]
                         )
    return {label: filled[label] for label in labels}


# ---- labels_lister -------------------------------------------------------------------
def labels_lister(rows: List[dict], key: str) -> List[str]:
    """
    ---- Summary ----
    Main function to list the labels used in one column of the table, each once, in
    the order first seen: what a cell of the column offers to pick from.

    ---- Inputs ----
    rows : List[dict]
        The rows of the table (dataset_setup, DATA_FORMAT.md).
    key : str
        The column, one of LABEL_KEYS.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The labels; a blank cell gives none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return list(dict.fromkeys(row[key] for row in rows if row[key]))


# ---- replicates_numberer -------------------------------------------------------------
def replicates_numberer(rows: List[dict]) -> List[Optional[int]]:
    """
    ---- Summary ----
    Main function to number the replicates: the rows in use with the same Group 1,
    Group 2 and time point count 1, 2, 3, in the order of their run numbers, a row
    with no run number after those that have one, and otherwise in the order of the
    table.

    ---- Inputs ----
    rows : List[dict]
        The rows of the table (dataset_setup, DATA_FORMAT.md).

    ---- Globals read ----
    LABEL_KEYS (module constant).

    ---- Outputs ----
    List[Optional[int]]
        The replicate number of each row, in the order of the table; None for a row
        not in use.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 The rows of each set, in the order of the table ---------------------------
    sets: Dict[tuple, List[int]] = {}
    for place, row in enumerate(rows):
        if row['use']:
            sets.setdefault(tuple(row[key] for key in LABEL_KEYS), []).append(place)

    # ---- 2 Count each set by run number, then by place in the table ------------------
    numbers: List[Optional[int]] = [None] * len(rows)
    for places in sets.values():
        ordered = sorted(places,
                         key=lambda place: (rows[place]['run'] is None,
                                            rows[place]['run'] or 0,
                                            place,
                                            ),
                         )
        for count, place in enumerate(ordered, start=1):
            numbers[place] = count
    return numbers


# ---- saved_setup_reader --------------------------------------------------------------
def saved_setup_reader(value: Any) -> dict:
    """
    ---- Summary ----
    Main function to keep, of the set-up read from a dataset's settings file, the
    parts that have the right form, so a file changed by hand or written by an older
    Portimao never stops the dataset opening.

    ---- Inputs ----
    value : Any
        What the settings file holds under 'setup'; anything.

    ---- Globals read ----
    COLOUR_PATTERN, GROUP_COUNT, LABEL_KEYS (module constants).

    ---- Outputs ----
    dict
        {'group_names': [str, str], 'colours': {label: '#rrggbb'}, 'files': {file
        name: {'use': bool, 'group_1': str, 'group_2': str, 'time_point': str}}}
        (saved_setup, DATA_FORMAT.md). An empty dict when nothing usable was saved.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _text_cleaner
    """

    if not isinstance(value, dict):
        return {}
    names = value.get('group_names')
    names = list(names) if isinstance(names, (list, tuple)) else []
    names = [_text_cleaner(name) for name in names[:GROUP_COUNT]]
    names += [''] * (GROUP_COUNT - len(names))
    colours = value.get('colours') if isinstance(value.get('colours'), dict) else {}
    files = value.get('files') if isinstance(value.get('files'), dict) else {}
    return {'group_names': names,
            'colours': {label: colour.lower()
                        for label, colour in colours.items()
                        if isinstance(label, str)
                        and isinstance(colour, str)
                        and COLOUR_PATTERN.match(colour)
                        },
            'files': {name: dict({key: _text_cleaner(entry.get(key))
                                  for key in LABEL_KEYS
                                  },
                                 use=entry.get('use') is not False,
                                 )
                      for name, entry in files.items()
                      if isinstance(name, str) and isinstance(entry, dict)
                      },
            }


# ---- sets_lister ---------------------------------------------------------------------
def sets_lister(rows: List[dict], colours: Dict[str, str]) -> List[dict]:
    """
    ---- Summary ----
    Main function to list the sets of the dataset as the table stands: the rows in
    use with the same Group 1, Group 2 and time point, each set with its name, its
    number of experiments and the colour of its Group 1 label.

    ---- Inputs ----
    rows : List[dict]
        The rows of the table (dataset_setup, DATA_FORMAT.md).
    colours : Dict[str, str]
        {Group 1 label: colour as '#rrggbb'}.

    ---- Globals read ----
    COLOUR_KEY, LABEL_KEYS, NO_LABELS, SET_JOINER (module constants).

    ---- Outputs ----
    List[dict]
        One {'name': str, 'n': int, 'colour': Optional[str]} per set, in the order
        first seen. The name is the labels that are filled in, joined by ' · ', or
        'no labels'; the colour is None for a set with no Group 1 label.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    sets: Dict[tuple, dict] = {}
    for row in rows:
        if not row['use']:
            continue
        labels = tuple(row[key] for key in LABEL_KEYS)
        entry = sets.setdefault(labels,
                                {'name': SET_JOINER.join(label
                                                         for label in labels
                                                         if label
                                                         ) or NO_LABELS,
                                 'n': 0,
                                 'colour': colours.get(row[COLOUR_KEY]),
                                 },
                                )
        entry['n'] += 1
    return list(sets.values())


# ---- setup_builder -------------------------------------------------------------------
def setup_builder(names: Sequence[str], saved: Optional[dict] = None) -> dict:
    """
    ---- Summary ----
    Main function to build the set-up table of a dataset: one row per experiment, as
    it was saved for the dataset, and filled in from its file name for an experiment
    never saved. Every Group 1 label has a colour.

    ---- Inputs ----
    names : Sequence[str]
        The experiment names (the .paf file names without the extension), in the
        order of the table.
    saved : Optional[dict]
        The set-up saved with the dataset (saved_setup, DATA_FORMAT.md, as
        saved_setup_reader gives it); None or empty for a dataset never set up.

    ---- Globals read ----
    GROUP_COUNT, LABEL_KEYS (module constants).

    ---- Outputs ----
    dict
        {'group_names': [str, str], 'colours': {Group 1 label: '#rrggbb'}, 'rows':
        [{'name', 'use', 'group_1', 'group_2', 'time_point', 'run'}]}
        (dataset_setup, DATA_FORMAT.md). A label read from a file name is spelt as
        the same label is first spelt in its column, whatever its case.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_matcher
    file_name_reader
    group_colours_filler
    """

    # ---- 1 What was saved ------------------------------------------------------------
    saved = saved or {}
    files = saved.get('files') or {}
    # the labels saved come first, so a new file is spelt as they are
    known = {key: list(dict.fromkeys(files[name][key]
                                     for name in names
                                     if name in files and files[name][key]
                                     ),
                       )
             for key in LABEL_KEYS
             }

    # ---- 2 One row per experiment ----------------------------------------------------
    rows = []
    for name in names:
        *read, run = file_name_reader(name)
        if name in files:
            row = dict(files[name])
        else:
            row = {key: _label_matcher(label, known[key])
                   for key, label in zip(LABEL_KEYS, read)
                   }
            row['use'] = True
        rows.append(dict(row, name=name, run=run))
    return {'group_names': list(saved.get('group_names') or [''] * GROUP_COUNT),
            'colours': group_colours_filler(rows, saved.get('colours') or {}),
            'rows': rows,
            }


# ---- setup_plainer -------------------------------------------------------------------
def setup_plainer(setup: dict, remembered: Optional[dict] = None) -> dict:
    """
    ---- Summary ----
    Main function to give the set-up table as it is saved with the dataset: the group
    names, the colour of each Group 1 label in the table, and the cells of each file.
    A file saved before that is not in this run is kept as it was.

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    remembered : Optional[dict]
        The set-up saved before (saved_setup, DATA_FORMAT.md); None or empty for a
        dataset never set up.

    ---- Globals read ----
    LABEL_KEYS (module constant).

    ---- Outputs ----
    dict
        {'group_names', 'colours', 'files'} (saved_setup, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    group_colours_filler
    """

    files = {name: dict(entry)
             for name, entry in ((remembered or {}).get('files') or {}).items()
             }
    for row in setup['rows']:
        files[row['name']] = dict({key: row[key] for key in LABEL_KEYS},
                                  use=bool(row['use']),
                                  )
    return {'group_names': list(setup['group_names']),
            'colours': group_colours_filler(setup['rows'], setup['colours']),
            'files': files,
            }
