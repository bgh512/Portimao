"""
The journal files of the journals folder: what each journal asks of a figure, read into
the settings, and the answers of a dataset fitted to the journals there are.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.user_places import JOURNALS_FOLDER_NAME, UserPlaces


# ---- CONSTANTS -----------------------------------------------------------------------
# The journal a figure is drawn for until another is chosen, and what it asks, used when
# its own file is missing or cannot be read, so the program always has one journal.
STANDARD_JOURNAL = 'nature'
STANDARD_SPEC = {'name': 'Nature',
                 'widths_mm': {1: 89, 1.5: 120, 2: 183},
                 'page_height_mm': 170,
                 'font_min_pt': 5,
                 'font_max_pt': 7,
                 'panel_letter_pt': 8,
                 'panel_letter_case': 'lower',
                 'font_family': ['Arial', 'Helvetica'],
                 'line_min_pt': None,
                 'line_max_pt': None,
                 'dpi': 300,
                 'paper_mm': None,
                 }
# the journals offered first, in this order; the others follow by name
JOURNAL_ORDER = ('nature', 'science', 'cell', 'pnas')
# The numbers of a journal file that must be above 0, with the name each has in the
# settings; a journal may leave the ones in OPTIONAL_NUMBERS empty (null).
NUMBER_NAMES = {'tallest_figure_mm': 'page_height_mm',
                'smallest_text_pt': 'font_min_pt',
                'largest_text_pt': 'font_max_pt',
                'panel_letter_pt': 'panel_letter_pt',
                'thinnest_line_pt': 'line_min_pt',
                'thickest_line_pt': 'line_max_pt',
                'picture_dpi': 'dpi',
                }
OPTIONAL_NUMBERS = ('largest_text_pt', 'thinnest_line_pt', 'thickest_line_pt')
# The journal and the width of each figure in the answers (config.DEFAULT_ANSWERS).
JOURNAL_ANSWER_PAIRS = (('journal', 'columns'),)


# ---- JOURNAL FILE HELPERS ------------------------------------------------------------


# ---- _number_checker -----------------------------------------------------------------
def _number_checker(value: Any) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a value of a journal file is a number above 0.

    ---- Inputs ----
    value : Any
        The value read from the file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True for a whole or decimal number above 0 (True and False are not numbers).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


# ---- _widths_reader ------------------------------------------------------------------
def _widths_reader(widths: Any) -> Dict[float, float]:
    """
    ---- Summary ----
    Helper function to read the widths of a journal file: the number of columns, then
    the width in mm.

    ---- Inputs ----
    widths : Any
        The 'widths_mm' of the file, such as {"1": 89, "1.5": 120, "2": 183}.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[float, float]
        {columns: width in mm}, narrowest first, a whole number of columns as an int.
        Raises ValueError, in plain words, for anything else.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_checker
    """

    if not isinstance(widths, dict) or not widths:
        raise ValueError("its 'widths_mm' is not a list of columns and widths, such as "
                         '{"1": 89, "2": 183}',
                         )
    read = {}
    for text, width_mm in widths.items():
        try:
            columns = float(text)
        except (TypeError, ValueError):
            columns = 0.0
        if columns <= 0 or not _number_checker(width_mm):
            raise ValueError(f"its width '{text}: {width_mm}' is not a number of "
                             'columns and a width in mm, both above 0',
                             )
        read[int(columns) if columns == int(columns) else columns] = width_mm
    return dict(sorted(read.items()))


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- journal_answers_fitter ----------------------------------------------------------
def journal_answers_fitter(answers: dict,
                           specs: Dict[str, dict],
                           ) -> Tuple[dict, List[str]]:
    """
    ---- Summary ----
    Main function to fit the journal and the width of every figure in the answers to
    the journals there are: a journal that is no longer in the journals folder becomes
    the standard one, and a width the journal does not take becomes the widest it takes
    that is no wider (its narrowest when there is none).

    ---- Inputs ----
    answers : dict
        The answers (config.DEFAULT_ANSWERS with the ones saved for a dataset).
    specs : Dict[str, dict]
        The journals (config.JOURNAL_SPECS); the standard journal is among them.

    ---- Globals read ----
    JOURNAL_ANSWER_PAIRS, STANDARD_JOURNAL.

    ---- Outputs ----
    Tuple[dict, List[str]]
        (a copy of the answers with every journal and width one that can be drawn, one
        plain sentence for each change, to show the user).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    fitted, notes = dict(answers), []
    for journal_key, columns_key in JOURNAL_ANSWER_PAIRS:
        if journal_key not in fitted or columns_key not in fitted:
            continue
        journal = fitted[journal_key]
        if journal not in specs:
            notes.append(f"The journal '{journal}' saved with this dataset is not in "
                         f'the journals folder: '
                         f"{specs[STANDARD_JOURNAL]['name']} is used in its place.",
                         )
            journal = fitted[journal_key] = STANDARD_JOURNAL
        widths = specs[journal]['widths_mm']
        columns = fitted[columns_key]
        if columns in widths:
            continue
        narrower = [allowed for allowed in widths if allowed <= columns]
        chosen = max(narrower) if narrower else min(widths)
        fitted[columns_key] = chosen
        notes.append(f"{specs[journal]['name']} has no figure {columns:g} "
                     f"column{'' if columns == 1 else 's'} wide: a figure saved at "
                     f'that width is now {chosen:g} '
                     f"column{'' if chosen == 1 else 's'} wide "
                     f'({widths[chosen]:g} mm).',
                     )
    return fitted, notes


# ---- journal_file_reader -------------------------------------------------------------
def journal_file_reader(path: Path) -> dict:
    """
    ---- Summary ----
    Main function to read one journal file into what the settings keep for a journal.

    ---- Inputs ----
    path : Path
        A .json file of the journals folder (DATA_FORMAT.md, journal file).

    ---- Globals read ----
    NUMBER_NAMES, OPTIONAL_NUMBERS.

    ---- Outputs ----
    dict
        The journal as in config.JOURNAL_SPECS: name, widths_mm {columns: mm},
        page_height_mm (the tallest figure), font_min_pt, font_max_pt (None when the
        journal gives no largest text), panel_letter_pt, panel_letter_case ('upper' or
        'lower'), font_family, line_min_pt and line_max_pt (None when not given), dpi
        and paper_mm ((width, height) of the printed page, None when not given).
        Raises ValueError saying, in plain words, what is wrong with the file.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_checker
    _widths_reader
    """

    # ---- 1 Read the file -------------------------------------------------------------
    try:
        values = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, ValueError):
        raise ValueError('it cannot be read as a .json file (a missing comma, bracket '
                         'or quote mark is the usual reason)',
                         ) from None
    if not isinstance(values, dict):
        raise ValueError('it does not hold the name of each thing and then its value')

    # ---- 2 Check the name, the widths and the numbers --------------------------------
    name = values.get('name')
    if not isinstance(name, str) or not name.strip():
        raise ValueError("it has no 'name'")
    spec: Dict[str, Any] = {'name': name.strip(),
                            'widths_mm': _widths_reader(values.get('widths_mm')),
                            }
    for file_name, spec_name in NUMBER_NAMES.items():
        value = values.get(file_name)
        if value is None and file_name in OPTIONAL_NUMBERS:
            spec[spec_name] = None
        elif _number_checker(value):
            spec[spec_name] = value
        else:
            raise ValueError(f"its '{file_name}' ({value!r}) is not a number above 0"
                             if file_name in values
                             else f"it has no '{file_name}'",
                             )
    if spec['font_max_pt'] is not None and spec['font_max_pt'] < spec['font_min_pt']:
        raise ValueError('its largest text is smaller than its smallest text')
    if None not in (spec['line_min_pt'], spec['line_max_pt']) and (
            spec['line_max_pt'] < spec['line_min_pt']):
        raise ValueError('its thickest line is thinner than its thinnest line')

    # ---- 3 Check the panel letters, the fonts and the page ---------------------------
    case = values.get('panel_letter_case')
    if case not in ('upper', 'lower'):
        raise ValueError("its 'panel_letter_case' is not \"upper\" or \"lower\"")
    fonts = values.get('fonts')
    if (not isinstance(fonts, list) or not fonts or
            not all(isinstance(font, str) and font.strip() for font in fonts)):
        raise ValueError("its 'fonts' is not a list of font names, such as [\"Arial\"]")
    page = values.get('page_mm')
    if page is not None:
        if (not isinstance(page, list) or len(page) != 2 or
                not all(_number_checker(side) for side in page)):
            raise ValueError("its 'page_mm' is not the width and the height of the "
                             'page, such as [210, 297], or null',
                             )
        if (page[0] < max(spec['widths_mm'].values()) or
                page[1] < spec['page_height_mm']):
            raise ValueError('its page is smaller than its largest figure')
        page = (page[0], page[1])
    spec.update({'panel_letter_case': case,
                 'font_family': [font.strip() for font in fonts],
                 'paper_mm': page,
                 },
                )
    return spec


# ---- journal_specs_loader ------------------------------------------------------------
def journal_specs_loader(folders: Sequence[Path],
                         ) -> Tuple[Dict[str, dict], List[str]]:
    """
    ---- Summary ----
    Main function to read every journal file of the journals folders. A journal is
    named after its file (nature.json is 'nature'); a file in an earlier folder wins
    over one of the same name in a later folder, so the user's own copy is the one
    used. A file that cannot be used is left out and named in one sentence. The
    standard journal is always there: with no usable file of its own, the numbers kept
    in the program are used.

    ---- Inputs ----
    folders : Sequence[Path]
        The journals folders, the user's own first; a folder that is missing is
        passed over.

    ---- Globals read ----
    JOURNAL_ORDER, STANDARD_JOURNAL, STANDARD_SPEC.

    ---- Outputs ----
    Tuple[Dict[str, dict], List[str]]
        ({journal: what it asks, as journal_file_reader gives it}, in the order of
        JOURNAL_ORDER and then by name; one plain sentence for each file left out).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    journal_file_reader
    """

    # ---- 1 Read each file, the first folder that has it ------------------------------
    specs: Dict[str, dict] = {}
    problems: List[str] = []
    refused = set()
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob('*.json')):
            journal = path.stem.lower()
            if journal in specs or journal in refused:
                continue
            try:
                specs[journal] = journal_file_reader(path)
            except ValueError as exc:
                refused.add(journal)
                problems.append(f'The journal file {path.name} is left out: {exc}. '
                                f'Correct it in {folder}, then open Portimao again.',
                                )

    # ---- 2 Keep the standard journal, and put the journals in order ------------------
    if STANDARD_JOURNAL not in specs:
        specs[STANDARD_JOURNAL] = dict(STANDARD_SPEC)
        if STANDARD_JOURNAL not in refused:
            problems.append(f'The journal file {STANDARD_JOURNAL}.json is missing '
                            f'from the journals folder: the numbers for '
                            f"{STANDARD_SPEC['name']} kept in the program are used.",
                            )
    first = [journal for journal in JOURNAL_ORDER if journal in specs]
    others = sorted((journal for journal in specs if journal not in JOURNAL_ORDER),
                    key=lambda journal: specs[journal]['name'].lower(),
                    )
    return {journal: specs[journal] for journal in first + others}, problems


# ---- journals_folder_lister ----------------------------------------------------------
def journals_folder_lister(places: UserPlaces) -> List[Path]:
    """
    ---- Summary ----
    Main function to list the journals folders in the order they are read: the user's
    own, then the one that comes with the program (the same folder when run from
    source).

    ---- Inputs ----
    places : UserPlaces
        Where the program's own files and the user's things are (user_places_finder).

    ---- Globals read ----
    JOURNALS_FOLDER_NAME (from utils_shared.user_places).

    ---- Outputs ----
    List[Path]
        The folders, each once.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    folders = [places.journals_folder]
    shipped = places.program_folder / JOURNALS_FOLDER_NAME
    if shipped != folders[0]:
        folders.append(shipped)
    return folders
