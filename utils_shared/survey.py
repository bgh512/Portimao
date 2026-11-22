"""
Numbered terminal questions of the main program (sections 1 to 5) and the trimming rules.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.run_namer import run_name_lister
from utils_shared.dataset_settings import dataset_settings_reader, SAVED_VALUE_KEYS
from utils_shared.delta_psi import b_haem_column_finder
from utils_shared.helpers import concentration_formatter, file_name_sanitiser
from utils_shared.individual_experiment_exporter import saved_settings_reader
from utils_shared.paf_reader import experiment_summary_reader, PafError
from utils_shared.questions import (choice_asker,
                                    info_printer,
                                    multi_asker,
                                    number_asker,
                                    path_cleaner,
                                    progress_clearer,
                                    progress_printer,
                                    text_asker,
                                    text_italiser,
                                    yes_no_asker,
                                    )
from utils_shared.spectral_decomposer import fit_loader, fit_names_lister
from utils_shared.user_notices import problem_teller


# ---- CONSTANTS -----------------------------------------------------------------------
IGNORE_LABEL = 'ignore'  # the label that leaves an event out, in any capitals
JOURNAL_NAMES = {'nature': 'Nature',
                 'science': 'Science',
                 'cell': 'Cell',
                 'pnas': 'PNAS',
                 }
OCR_LABELS = {'raw': 'OCR (µM min⁻¹)',
              'od': 'OCR / OD (µM min⁻¹ OD⁻¹)',
              'percent': 'OCR (% of the range)',
              }
PCA_CHOICE = '__pca__'
# raised form of the characters of an exponent typed as -1 or ^2
SUPERSCRIPT_TABLE = str.maketrans('-+0123456789', '⁻⁺⁰¹²³⁴⁵⁶⁷⁸⁹')
# the temperatures of a run the temperature question takes (°C): liquid water
TEMPERATURE_LIMITS_C = (0.0, 100.0)
# the four edges of the trimming step, in the order they are shown
TRIM_KEYS = ('trim_start', 'trim_end', 'ignore_start', 'ignore_end')
# the units a label is tidied around; a name with numbers (nd-011992) is none of them
UNIT_PATTERN = r'(?:[mµnpk]?(?:M|L|g|mol)|min|s|h|OD)'


# ---- SURVEY HELPERS ------------------------------------------------------------------


# ---- _columns_text_builder -----------------------------------------------------------
def _columns_text_builder(columns: float) -> str:
    """
    ---- Summary ----
    Helper function to write a figure width in columns, e.g. '1 column' or
    '1.5 columns'.

    ---- Inputs ----
    columns : float
        Number of journal columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Text such as '2 columns'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return f"{columns:g} column{'' if columns == 1 else 's'}"


# ---- _event_line_builder -------------------------------------------------------------
def _event_line_builder(event: dict, entry: dict) -> str:
    """
    ---- Summary ----
    Helper function to write one event as 'label, time' for the event listings.

    ---- Inputs ----
    event : dict
        Event from the file summary (time in minutes).
    entry : dict
        Current label, concentration_uM and ignored flag of that event.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '  15.01 min: nd-011992' or with the concentration (in µM, mM or
        M) and '[IGNORED]' when they apply.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    concentration_formatter
    """

    conc = (''
            if entry['concentration_uM'] is None
            else f", {concentration_formatter(entry['concentration_uM'])}"
            )
    note = '  [IGNORED]' if entry['ignored'] else ''
    return f"  {event['time']:.2f} min: {entry['label']}{conc}{note}"


# ---- _first_event_finder -------------------------------------------------------------
def _first_event_finder(summary: dict) -> float:
    """
    ---- Summary ----
    Helper function to find the time of the first event of an experiment.

    ---- Inputs ----
    summary : dict
        Experiment summary with events and duration_min.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        First event time in minutes; the duration when there are no events.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return min((e['time'] for e in summary['events']),
               default=summary['duration_min'],
               )


# ---- _last_event_finder --------------------------------------------------------------
def _last_event_finder(summary: dict) -> float:
    """
    ---- Summary ----
    Helper function to find the time of the last event of an experiment.

    ---- Inputs ----
    summary : dict
        Experiment summary with events.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Last event time in minutes; 0 when there are no events.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return max((e['time'] for e in summary['events']), default=0.0)


# ---- _limit_converter ----------------------------------------------------------------
def _limit_converter(summary: dict,
                     kind: str,
                     edge: str,
                     minutes: float,
                     ) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to turn the minutes a user typed into the value the program keeps
    for a trim or ignore limit.

    ---- Inputs ----
    summary : dict
        Experiment summary with duration_min.
    kind : str
        'trim' or 'ignore'.
    edge : str
        'start' or 'end'.
    minutes : float
        Minutes to remove from that edge of the recording; 0 means none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        Trim limits: the time on the original recording, or None for no trim. Ignore
        limits: the minutes (0.0 for none).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trim start = minutes. Trim end = duration - minutes.

    ---- Helpers ----
    None.
    """

    if kind == 'ignore':
        return float(minutes or 0.0)
    if not minutes:
        return None
    return float(minutes) if edge == 'start' else summary['duration_min'] - minutes


# ---- _limit_maximum_getter -----------------------------------------------------------
def _limit_maximum_getter(summary: dict,
                          kind: str,
                          edge: str,
                          so_far: dict,
                          ) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to find the most minutes that can be trimmed from an edge of a file
    without cutting off an event.

    ---- Inputs ----
    summary : dict
        Experiment summary with events and duration_min.
    kind : str
        'trim' or 'ignore'.
    edge : str
        'start' or 'end'.
    so_far : dict
        Limits already asked for this file ({key: value}).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        Largest accepted number of minutes, or None when there is no limit (ignore).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Start: the first event time. End: duration - the later of the last event time and
    the trim start.

    ---- Helpers ----
    _first_event_finder
    _last_event_finder
    """

    if kind == 'ignore':
        return None
    if edge == 'start':
        return _first_event_finder(summary)
    kept_from = max(_last_event_finder(summary), so_far.get('trim_start') or 0.0)
    return max(summary['duration_min'] - kept_from, 0.0)


# ---- _maths_converter ----------------------------------------------------------------
def _maths_converter(match: 're.Match') -> str:
    """
    ---- Summary ----
    Helper function to convert the contents of one $...$ maths span to plain text
    with Unicode subscripts and italic letters.

    ---- Inputs ----
    match : re.Match
        Match whose group 1 is the text between the dollar signs.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The converted text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _subscript_stripper
text_italiser
    """

    inner = re.sub(r'_\{([^}]*)\}|_(.)', _subscript_stripper, match.group(1))
    return text_italiser(inner.replace('\\', ''))


# ---- _minutes_recaller ---------------------------------------------------------------
def _minutes_recaller(summary: dict, remembered: dict, key: str) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to turn a limit remembered from the last run back into the minutes
    the question asks for.

    ---- Inputs ----
    summary : dict
        Experiment summary with name and duration_min.
    remembered : dict
        {file name: {key: value}} from the last run.
    key : str
        'trim_start', 'trim_end', 'ignore_start' or 'ignore_end'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        Minutes removed from that edge (0.0 when the file was remembered as not
        trimmed there), or None when nothing is remembered for the file.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trim end minutes = duration - remembered end time.

    ---- Helpers ----
    None.
    """

    entry = remembered.get(summary['name'])
    if not entry or key not in entry:
        return None
    value = entry[key]
    if value is None:  # remembered as "not trimmed"
        return 0.0
    return summary['duration_min'] - value if key == 'trim_end' else value


# ---- _natural_sorter -----------------------------------------------------------------
def _natural_sorter(name: str) -> list:
    """
    ---- Summary ----
    Helper function to build a sort key that puts numbers in numerical order, so
    'control_7hours' comes before 'control_24hours'.

    ---- Inputs ----
    name : str
        File or experiment name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Key of alternating lower-case text and integer parts (text first).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    parts = re.split(r'(\d+)', name.lower())
    return [int(part) if part.isdigit() else part for part in parts]


# ---- _subscript_stripper -------------------------------------------------------------
def _subscript_stripper(match: 're.Match') -> str:
    """
    ---- Summary ----
    Helper function to turn a matched subscript (_x or _{xy}) into plain text, since
    Unicode subscripts are hard to read in a terminal.

    ---- Inputs ----
    match : re.Match
        Match whose group 1 or 2 holds the subscript text.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The subscript text without the underscore.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return match.group(1) if match.group(1) is not None else match.group(2)


# ---- _tidy_labels_offerer ------------------------------------------------------------
def _tidy_labels_offerer(with_events: List[dict],
                         result: Dict[str, List[dict]],
                         kept: Set[str],
                         ) -> None:
    """
    ---- Summary ----
    Helper function to list the event labels that could be written more tidily (8 ug
    ml-1 as 8 µg mL⁻¹) beside their tidy forms, and to ask once whether to use them
    all. Asks nothing when every label is tidy already or was kept as it is before.

    ---- Inputs ----
    with_events : List[dict]
        File summaries (DATA_FORMAT.md) of the files that have events.
    result : Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}; the
        labels are replaced by their tidy forms when the user agrees.
    kept : Set[str]
        Labels the user chose to keep as they are; the labels kept this time are
        added, so they are not offered again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes the labels in ``result``, adds to ``kept`` and reads from and prints
    to the terminal (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    tidy_labels_finder
    yes_no_asker
    """

    found = tidy_labels_finder(with_events, result, kept)
    if not found:
        return
    info_printer('These labels can be written more tidily:')
    for name, time, entry, tidy in found:
        info_printer(f"  {name}, {time:.2f} min: {entry['label']} -> {tidy}", depth=2)
    if yes_no_asker('Do you want to use these tidy forms?', True, number='3.2.1'):
        for _, _, entry, tidy in found:
            entry['label'] = tidy
    else:
        kept.update(entry['label'] for _, _, entry, _ in found)


# ---- _trim_minutes_clamper -----------------------------------------------------------
def _trim_minutes_clamper(summary: dict,
                          minutes: Dict[str, float],
                          key: str,
                          ) -> Dict[str, float]:
    """
    ---- Summary ----
    Helper function to keep the four edges of one file within its limits: no edge below
    0 minutes, a trimmed edge never cutting off an event, and the ignored parts inside
    the kept part without crossing. When the ignored parts no longer fit, the one on
    the side of ``key`` gives way first, so an edge pushed against another stops there.

    ---- Inputs ----
    summary : dict
        Experiment summary with events and duration_min.
    minutes : Dict[str, float]
        {trim_start, trim_end, ignore_start, ignore_end} in minutes taken off each edge.
    key : str
        The edge just set (one of TRIM_KEYS); its side gives way first.

    ---- Globals read ----
    TRIM_KEYS.

    ---- Outputs ----
    Dict[str, float]
        The minutes kept within the limits; the dictionary given is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Kept length = duration - trim start - trim end; the ignore time on the side of
    ``key`` is at most kept length - the other ignore time.

    ---- Helpers ----
    _limit_maximum_getter
    """

    # ---- 1 The trimmed edges stop at the first and last event ------------------------
    kept = {name: max(float(minutes[name]), 0.0) for name in TRIM_KEYS}
    kept['trim_start'] = min(kept['trim_start'],
                             _limit_maximum_getter(summary, 'trim', 'start', {}),
                             )
    kept['trim_end'] = min(kept['trim_end'],
                           _limit_maximum_getter(summary, 'trim', 'end', kept),
                           )

    # ---- 2 The ignored parts fit inside the kept part --------------------------------
    length = max(float(summary['duration_min']) - kept['trim_start'] - kept['trim_end'],
                 0.0,
                 )
    near = 'ignore_end' if key.endswith('_end') else 'ignore_start'
    far = 'ignore_start' if near == 'ignore_end' else 'ignore_end'
    kept[near] = min(kept[near], max(length - kept[far], 0.0))
    kept[far] = min(kept[far], length - kept[near])
    return kept


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- averaging_asker -----------------------------------------------------------------
def averaging_asker(answers: dict,
                    defaults: dict,
                    forced: bool = False,
                    depth: int = 1,
                    additions: Optional[Dict[str, List[float]]] = None,
                    ) -> None:
    """
    ---- Summary ----
    Main function to ask whether to average around the events, and the window
    settings, in seconds. When the plot shows the files, a drag across one window on
    the plot gives its length, and the gap from where the drag ended to the next
    addition is then offered as the default of the gap question; a drag during the gap
    question gives the gap alone.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers (averaging, window_minutes, gap_minutes).
    forced : bool
        True to skip the yes/no question and only ask the window settings (a figure
        that needs the averages was chosen). The averaging answer is not changed.
    depth : int
        Numbering depth of the first question.
    additions : Optional[Dict[str, List[float]]]
        {file name: times of its additions (min, not those marked ignore), on the time
        axis of the plot}, so a drag on the plot of a file can be read; None when the
        plot does not show the files (the answers are then typed).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores window_minutes and gap_minutes (in minutes) and averaging in
    ``answers``.

    ---- Equations ----
    minutes = seconds / 60.

    ---- Helpers ----
    averaging_drag_reader
    number_asker
    yes_no_asker
    """

    # ---- 1 Ask whether to average ----------------------------------------------------
    if not forced:
        answers['averaging'] = yes_no_asker('Do you want to average around the events?',
                                            defaults['averaging'],
                                            depth=depth,
                                            )
        if not answers['averaging']:
            return

    # ---- 2 Set up the reading of a drag on the plot ----------------------------------
    dragged: Dict[str, Optional[float]] = {}
    def length_reader(name: str, start_min: float, end_min: float) -> Optional[float]:
        if name not in additions:
            return None
        length_s, dragged['gap_s'] = averaging_drag_reader(additions[name],
                                                           start_min,
                                                           end_min,
                                                           )
        return length_s
    def gap_reader(name: str, start_min: float, end_min: float) -> Optional[float]:
        if name not in additions:
            return None
        return averaging_drag_reader(additions[name], start_min, end_min)[1]

    # ---- 3 Ask for the window and gap ------------------------------------------------
    sub = depth if forced else depth + 1
    window_s = number_asker('How long a window (s) should the average be taken over?',
                            round(defaults['window_minutes'] * 60.0, 2),
                            minimum=0,
                            exclusive_minimum=True,
                            depth=sub,
                            span_reader=length_reader if additions else None,
                            )
    gap_default = dragged.get('gap_s')
    if gap_default is None:
        gap_default = round(defaults['gap_minutes'] * 60.0, 2)
    gap_s = number_asker('How long before the next addition should the averaging '
                         'window end (s)?',
                         gap_default,
                         minimum=0,
                         depth=sub,
                         span_reader=gap_reader if additions else None,
                         )
    answers['window_minutes'] = window_s / 60.0
    answers['gap_minutes'] = gap_s / 60.0
    answers['window_asked'] = True


# ---- averaging_drag_reader -----------------------------------------------------------
def averaging_drag_reader(additions_min: List[float],
                          start_min: float,
                          end_min: float,
                          ) -> Tuple[float, Optional[float]]:
    """
    ---- Summary ----
    Main function to turn a drag across one averaging window on the plot of a file into
    the window's length and how long before the next addition it ends, both in seconds
    rounded to whole steps.

    ---- Inputs ----
    additions_min : List[float]
        Times of the file's additions on the time axis of the plot (min), not those
        marked ignore.
    start_min : float
        Where the drag started (min).
    end_min : float
        Where the drag ended (min); after ``start_min``.

    ---- Globals read ----
    config.DRAG_STEP_SECONDS (the rounding step).

    ---- Outputs ----
    Tuple[float, Optional[float]]
        (length_s, gap_s): the length is at least one step; the gap is at least 0, and
        None when no addition comes after the end of the drag (the last window ends a
        set time before the end of the recording instead).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    length_s = round((end - start) x 60 / step) x step, at least one step;
    gap_s = round((first addition at or after the end - end) x 60 / step) x step.

    ---- Helpers ----
    None.
    """

    step = float(settings.DRAG_STEP_SECONDS)
    length_s = max(round((end_min - start_min) * 60.0 / step) * step, step)
    later = [time for time in additions_min if time >= end_min]
    if not later:
        return length_s, None
    gap_s = max(round((min(later) - end_min) * 60.0 / step) * step, 0.0)
    return length_s, gap_s


# ---- data_folder_lister --------------------------------------------------------------
def data_folder_lister(root: Path) -> List[Path]:
    """
    ---- Summary ----
    Main function to list the folders directly inside a folder that hold .paf files,
    so they can be offered by number.

    ---- Inputs ----
    root : Path
        Folder to look in (the user's own folder, UserPlaces.own_folder).

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Path]
        The folders with at least one .paf file directly inside, in natural name
        order. Folders whose name starts with a dot or an underscore, and folders that
        cannot be read, are left out.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _natural_sorter
    paf_finder
    """

    found = []
    for path in Path(root).iterdir():
        if not path.is_dir() or path.name.startswith(('.', '_')):
            continue
        try:
            if paf_finder(path):
                found.append(path)
        except OSError:  # a folder that cannot be read holds no data for us
            continue
    return sorted(found, key=lambda p: _natural_sorter(p.name))


# ---- data_folder_resolver ------------------------------------------------------------
def data_folder_resolver(text: str, listed: List[Path]) -> Path:
    """
    ---- Summary ----
    Main function to turn the answer to the folder question into a folder: a number or
    a name from the list of data folders, or any other path.

    ---- Inputs ----
    text : str
        The answer as typed (or dragged in).
    listed : List[Path]
        The data folders offered, in the order they were numbered from 1.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The listed folder of that number or name (capitals do not matter), otherwise
        the answer as a path. It is not checked to exist.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    path_cleaner
    """

    cleaned = path_cleaner(text)
    if cleaned.isdigit() and 1 <= int(cleaned) <= len(listed):
        return listed[int(cleaned) - 1]
    for folder in listed:
        if folder.name.lower() == cleaned.lower():
            return folder
    return Path(cleaned).expanduser()


# ---- decomposition_asker -------------------------------------------------------------
def decomposition_asker(summaries: List[dict],
                        defaults: dict,
                        fits_folder: Path,
                        forced: bool = False,
                        depth: int = 1,
                        pca_runner: Optional[Callable] = None,
                        numbers: Optional[Dict[str, str]] = None,
                        ) -> tuple:
    """
    ---- Summary ----
    Main function to ask whether to decompose the spectra into haems and which fit to
    use: a fit file, or (when a pca_runner is given) components found from the data
    with a principal component analysis.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md); the spectrometers in common are used.
    defaults : dict
        Default answers (decompose, fit_file, decomposition_dataset).
    fits_folder : Path
        Folder holding the fit .csv files.
    forced : bool
        True to skip the yes/no question (a figure that needs the haems was chosen).
    depth : int
        Numbering depth of the questions (1 = 3.1, 2 = 3.1.1).
    pca_runner : Optional[Callable]
        Function (dataset, depth) that finds the components with a principal component
        analysis and returns (fit file name, fit), or (None, None) when the user wants
        a fit file instead. None leaves the option out.
    numbers : Optional[Dict[str, str]]
        The questions' own numbers from QUESTION_FLOW.md, by 'decompose', 'fit' and
        'spectrometer'; None numbers them in the order asked.

    ---- Globals read ----
    PCA_CHOICE (module constant).

    ---- Outputs ----
    tuple
        (decompose, fit_file, fit, dataset). fit is the dictionary from import_fit,
        or None when no decomposition will be done.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    fit_loader
    fit_names_lister
    info_printer
    problem_teller
    yes_no_asker
    """

    # ---- 1 Find the available fits ---------------------------------------------------
    numbers = numbers or {}
    none_chosen = (False, None, None, defaults['decomposition_dataset'])
    names = fit_names_lister(fits_folder)
    if not names and pca_runner is None:
        info_printer(f'No presets or fit files (.csv) were found in {fits_folder}, so '
                     'haems cannot be decomposed this time. Put a fit .csv in that '
                     'folder and run again.',
                     )
        return none_chosen
    if (not forced and
        not yes_no_asker('Do you want to decompose the haems?',
                         defaults['decompose'],
                         depth=depth,
                         number=numbers.get('decompose'),
                         )
        ):
        return none_chosen
    def dataset_chooser(extra_depth: int) -> Optional[str]:
        common = set(summaries[0]['datasets'])
        for summary in summaries[1:]:
            common &= set(summary['datasets'])
        if not common:
            info_printer('The files have no spectrometer in common, so haems cannot '
                         'be decomposed.',
                         )
            return None
        chosen = defaults['decomposition_dataset']
        if chosen not in common:
            options = sorted(common)
            chosen = options[0]
            if len(options) > 1:
                chosen = choice_asker('Which spectrometer holds the haem spectra?',
                                      [(o, o) for o in options],
                                      options[0],
                                      depth=depth + extra_depth,
                                      number=numbers.get('spectrometer'),
                                      )
        return chosen

    # ---- 2 Choose the fit, and the spectral dataset ----------------------------------
    default_fit = defaults.get('fit_file')
    choices = [(n, n) for n in names]
    if pca_runner is not None:
        choices.append((PCA_CHOICE,
                        'Find the components from the data (principal '
                        'component analysis)',
                        ),
                       )
    dataset = None
    while True:
        fit_file = choice_asker('Which fit would you like to use?',
                                choices,
                                default_fit if default_fit in names else choices[0][0],
                                depth=depth + (0 if forced else 1),
                                number=numbers.get('fit'),
                                )
        if fit_file == PCA_CHOICE:
            dataset = dataset or dataset_chooser(1)
            if dataset is None:
                return none_chosen
            fit_file, fit = pca_runner(dataset, depth + (0 if forced else 1) + 1)
            if fit is None:
                continue
            break
        try:
            fit = fit_loader(fits_folder, fit_file)
        except (OSError, ValueError) as exc:
            info_printer(f"{problem_teller('The fit file could not be read', exc)} The "
                         f'haems will not be decomposed.',
                         )
            return none_chosen
        break
    dataset = dataset or dataset_chooser(1)
    if dataset is None:
        return none_chosen
    return True, fit_file, fit, dataset


# ---- delta_psi_asker -----------------------------------------------------------------
def delta_psi_asker(answers: dict,
                    defaults: dict,
                    haems: List[str],
                    region_files: List[str],
                    ) -> bool:
    """
    ---- Summary ----
    Main function to ask whether to work out Δψ, the membrane potential. The question
    is asked only when Δψ can be worked out; otherwise the run has no Δψ, and a line
    says why when the dataset had it switched on.

    ---- Inputs ----
    answers : dict
        Answers dictionary the value is stored in.
    defaults : dict
        Default answers (delta_psi).
    haems : List[str]
        Names of the haems of the fit in use.
    region_files : List[str]
        Names of the files with both an oxidised and a reduced region.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when Δψ is worked out in this run.

    ---- Globals mutated ----
    None. Stores delta_psi in ``answers`` and reads from and prints to the terminal
    (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    delta_psi_offer_checker
    info_printer
    yes_no_asker
    """

    # ---- 1 Leave the question out when delta psi cannot be worked out ----------------
    if not delta_psi_offer_checker(haems, region_files):
        if defaults['delta_psi']:
            info_printer('Δψ is not worked out: it needs an oxidised and a reduced '
                         'region on at least one file, and a fit with one bH and one '
                         'bL.',
                         )
        answers['delta_psi'] = False
        return False

    # ---- 2 Ask -----------------------------------------------------------------------
    answers['delta_psi'] = yes_no_asker(
        'Do you want to work out Δψ?',
        defaults['delta_psi'],
        note='Δψ is the membrane potential, worked out from how reduced bH and bL are.',
        number='4.5',
        )
    return answers['delta_psi']


# ---- delta_psi_offer_checker ---------------------------------------------------------
def delta_psi_offer_checker(haems: List[str], region_files: List[str]) -> bool:
    """
    ---- Summary ----
    Main function to say whether Δψ can be worked out, and so whether its question is
    asked: at least one file has both regions, and the fit has one bH and one bL.

    ---- Inputs ----
    haems : List[str]
        Names of the haems of the fit in use, however they are written.
    region_files : List[str]
        Names of the files with both an oxidised and a reduced region.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when Δψ can be worked out for at least one file.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    b_haem_column_finder
    """

    if not region_files:
        return False
    return b_haem_column_finder(pd.DataFrame(columns=list(haems))) is not None


# ---- event_asker ---------------------------------------------------------------------
def event_asker(summaries: List[dict],
                saved: dict,
                table_filler: Callable[[Dict[str, List[dict]]], Dict[str, List[dict]]],
                kept: Set[str],
                ) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Main function to have the label and concentration of every event filled in in the
    labels table, starting from the saved or file values, an event being left out by
    writing ignore as its label. Labels that could be written more tidily (8 ug ml-1
    as 8 µg mL⁻¹) are then offered in their tidy forms, once. Nothing is asked when no
    file has events.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    saved : dict
        {file name: OD values and events saved before} (saved_values_reader).
    table_filler : Callable[[Dict[str, List[dict]]], Dict[str, List[dict]]]
        Function that shows the labels table filled in with the given events, waits
        until it is confirmed, and returns the events with the labels and
        concentrations typed.
    kept : Set[str]
        Labels the user chose to keep as they are; they are not offered in their tidy
        forms again, and the labels kept this time are added.

    ---- Globals read ----
    IGNORE_LABEL.

    ---- Outputs ----
    Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}.
        An event labelled ignore is left out and has no concentration.

    ---- Globals mutated ----
    None. Adds to ``kept`` and reads from and prints to the terminal (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _event_line_builder
    _tidy_labels_offerer
    event_entries_builder
    info_printer
    """

    # ---- 1 Start from the saved or file values ---------------------------------------
    result = event_entries_builder(summaries, saved)
    with_events = [s for s in summaries if s['events']]
    if not with_events:
        return result

    # ---- 2 Fill in the table ---------------------------------------------------------
    result = table_filler(result)
    for events in result.values():
        for entry in events:
            entry['ignored'] = entry['label'].strip().lower() == IGNORE_LABEL
            if entry['ignored']:
                entry['label'] = IGNORE_LABEL
                entry['concentration_uM'] = None

    # ---- 3 Offer the tidy forms and list the labels ----------------------------------
    _tidy_labels_offerer(with_events, result, kept)
    info_printer('Event labels:')
    for summary in with_events:
        info_printer(f"{summary['name']}:", depth=2)
        for event, entry in zip(summary['events'], result[summary['name']]):
            info_printer(_event_line_builder(event, entry), depth=2)
    return result


# ---- event_entries_builder -----------------------------------------------------------
def event_entries_builder(summaries: List[dict], saved: dict) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Main function to give the events of every file as the labels table starts them:
    the label, concentration and whether it is left out as saved for the dataset, or
    else the file's own text, with no concentration.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    saved : dict
        {file name: OD values and events saved before} (saved_values_reader).

    ---- Globals read ----
    IGNORE_LABEL.

    ---- Outputs ----
    Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}, one
        per event of the file, in its order; an event left out is labelled ignore.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    result = {}
    for summary in summaries:
        old = {e['datapoint']: e
               for e in (saved.get(summary['name']) or {}).get('events', [])
               }
        events = []
        for event in summary['events']:
            before = old.get(event['datapoint'], {})
            ignored = bool(before.get('ignored', False))
            events.append({'datapoint': event['datapoint'],
                           'label': (IGNORE_LABEL
                                     if ignored
                                     else (before.get('label') or event['text'])
                                     ),
                           'concentration_uM': before.get('concentration_uM'),
                           'ignored': ignored,
                           },
                          )
        result[summary['name']] = events
    return result


# ---- files_asker ---------------------------------------------------------------------
def files_asker(last: dict, own_folder: Path) -> Tuple[Path, List[dict], Path, dict]:
    """
    ---- Summary ----
    Main function to ask for the folder of .paf files (1.1), offering the data folders
    found in the user's own folder, and the results folder (1.2), and to read a summary
    of every file and the settings saved with the dataset. A results folder named
    without a path is made inside the data folder; one that already holds results of
    these files is taken only once the user agrees to write over them (1.2.1), and
    otherwise asked again with a free name offered.

    ---- Inputs ----
    last : dict
        Contents of last_answers.json; uses data_folder (the folder used last).
    own_folder : Path
        Folder whose data folders are offered by number (UserPlaces.own_folder): the
        program folder from source, the Portimao folder in the home folder in the Mac
        app.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Path, List[dict], Path, dict]
        (data folder, summary of each readable file, results folder, settings saved
        with the dataset). Each summary has name, path, duration_min, events and
        datasets; the settings are those of dataset_settings_reader, empty for a
        dataset never saved (DATA_FORMAT.md).

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    data_folder_lister
    data_folder_resolver
    dataset_settings_reader
    experiment_summary_reader
    free_folder_finder
    info_printer
    paf_finder
    progress_clearer
    progress_printer
    results_counter
    results_folder_checker
    results_folder_resolver
    text_asker
    yes_no_asker
    """

    # ---- 1 Ask for the .paf folder ---------------------------------------------------
    listed = data_folder_lister(own_folder)
    if listed:
        info_printer(f'Data folders found in {own_folder}:')
        for number, found in enumerate(listed, start=1):
            count = len(paf_finder(found))
            info_printer(f"  {number}) {found.name} ({count} file"
                         f"{'' if count == 1 else 's'})",
                         )
        info_printer('Type a number or a name from this list, or the path of another '
                     'folder.',
                     )
    def folder_checker(text: Optional[str]) -> Optional[str]:
        if not text:
            return 'Type or drag in a folder.'
        found = data_folder_resolver(text, listed)
        if not found.is_dir():
            return 'Type or drag in a folder that exists.'
        if not paf_finder(found):
            return 'Type or drag in a folder with .paf files directly inside it.'
        return None
    text = text_asker('What is the directory with the .paf files?',
                      last.get('data_folder'),
                      checker=folder_checker,
                      number='1.1',
                      )
    folder = data_folder_resolver(text, listed)
    files = paf_finder(folder)

    # ---- 2 Read every file -----------------------------------------------------------
    summaries = []
    for number, path in enumerate(files, start=1):
        progress_printer(f'Reading file {number} of {len(files)}: {path.name} ...')
        try:
            summary = experiment_summary_reader(path)
        except PafError as exc:
            progress_clearer()
            # the message starts with the file name
            info_printer(f'Skipping {exc}')
            continue
        summary['path'] = path
        summaries.append(summary)
    progress_clearer()
    if not summaries:
        raise SystemExit('None of the .paf files could be read (the reason for each is '
                         'above). Open Portimao again and choose another folder.',
                         )
    info_printer(f'\nFound {len(summaries)} readable file(s):')
    for summary in summaries:
        info_printer(f"  {summary['name']}: {summary['duration_min']:.1f} min, "
                     f"{len(summary['events'])} event(s)",
                     )

    # ---- 3 Ask for the results folder ------------------------------------------------
    saved = dataset_settings_reader(folder)
    if saved:
        info_printer('This dataset was opened before: the settings saved in its folder '
                     'are offered as the defaults.',
                     )
    offered = saved.get('export_folder') or folder / settings.RESULTS_FOLDER_NAME
    while True:
        text = text_asker('To which directory would you like the results to be saved?',
                          str(offered),
                          checker=lambda typed: results_folder_checker(typed, folder),
                          number='1.2',
                          )
        export_root = results_folder_resolver(text, folder)

        # ---- 3.1 Warn before results already there are written over ------------------
        count = results_counter(export_root, summaries)
        if not count:
            break
        info_printer(f'{export_root.name} already holds results of {count} of these '
                     f'{len(summaries)} files.',
                     )
        if yes_no_asker('Do you want to write over them?', False, number='1.2.1'):
            break
        offered = free_folder_finder(export_root)
        info_printer(
            'Type another folder, or a new name: a name without a path is made '
            'inside the data folder.',
            )
    return folder, summaries, export_root, saved


# ---- free_folder_finder --------------------------------------------------------------
def free_folder_finder(folder: Path) -> Path:
    """
    ---- Summary ----
    Main function to find a folder name beside the one given that is not used yet, by
    adding _2, _3 and so on, to offer when the user keeps the results already there.

    ---- Inputs ----
    folder : Path
        The folder whose name is taken (results).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The first of <folder>_2, <folder>_3, ... that does not exist.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    number = 2
    while (folder.parent / f'{folder.name}_{number}').exists():
        number += 1
    return folder.parent / f'{folder.name}_{number}'


# ---- haem_choice_asker ---------------------------------------------------------------
def haem_choice_asker(answers: dict, defaults: dict, fit: Optional[dict]) -> bool:
    """
    ---- Summary ----
    Main function to ask which haems are plotted, and in which order, when they are
    plotted: whether they are is answered by the Haems box of the window's settings
    strip, in answers['plot_haems'].

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    fit : Optional[dict]
        Fit dictionary (haem_list) used to list the haems, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the haems are plotted.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    haem_name_formatter
    multi_asker
    """

    if not (answers['decompose'] and fit is not None):
        answers['plot_haems'] = False
        return False
    if answers['plot_haems']:
        answers['haems'] = multi_asker('Which haems would you like to plot, and in '
                                       'which order?',
                                       list(fit['haem_list']),
                                       default_all=True,
                                       keep_order=True,
                                       depth=2,
                                       default_values=(defaults['haems']
                                                       or list(fit['haem_list'])
                                                       ),
                                       label_formatter=haem_name_formatter,
                                       )
    return answers['plot_haems']


# ---- haem_form_option_builder --------------------------------------------------------
def haem_form_option_builder(include_percent: bool) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to build the (key, label) choices for the 'how to show the
    haems' question of the haem and OCR response. The delta D line explains itself in
    italics.

    ---- Inputs ----
    include_percent : bool
        True to offer the % oxidised choice: the files asked about have an oxidised
        and a reduced region.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, str]]
        [(key, label), ...]: abs, delta and optionally percent.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    text_italiser
    """

    # No concentration: only cells are measured, and a haem amount depends on the size
    # of its shape, which the absorbance, delta D and % do not.
    delta = f"ΔD (mOD), {text_italiser('the change from the start')}"
    options = [('abs', 'Absorbance (mOD)'),
               ('delta', delta),
               ]
    if include_percent:
        options.append(('percent',
                        '% oxidised (reduced region = 0 %, oxidised region = 100 %)',
                        ),
                       )
    return options


# ---- haem_name_formatter -------------------------------------------------------------
def haem_name_formatter(name: str) -> str:
    """
    ---- Summary ----
    Main function to write a haem name for the terminal: the $...$ maths markers are
    removed, subscripts are written as plain characters (Unicode subscripts are hard to
    read) and the maths part is shown in italics, e.g. 'Cyt $b_H$' becomes 'Cyt bH'.

    ---- Inputs ----
    name : str
        Haem name as written in the fit file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Name for display only; the original name is still used everywhere else.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _maths_converter
    """

    # ---- 1 Convert the maths spans ---------------------------------------------------
    return re.sub(r'\$([^$]*)\$', _maths_converter, str(name))


# ---- label_angle_asker ---------------------------------------------------------------
def label_angle_asker(answers: dict, defaults: dict) -> None:
    """
    ---- Summary ----
    Main function to ask at what angle the event labels are written.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the answer in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    number_asker
    """

    answers['event_label_angle'] = number_asker('At what angle should the event labels '
                                                'be plotted (0 = horizontal, 90 = '
                                                'vertical)?',
                                                defaults['event_label_angle'],
                                                minimum=0,
                                                maximum=90,
                                                )


# ---- label_tidier --------------------------------------------------------------------
def label_tidier(text: str) -> str:
    """
    ---- Summary ----
    Main function to write the units of an event label the tidy way: u as µ, l as L, a
    space between a number and its unit, and exponents raised. Only units are changed;
    a name with numbers in it (nd-011992, Q203) and a chemical formula (H2O2) are left
    as they are, since the two cannot be told apart.

    ---- Inputs ----
    text : str
        The label as typed or as written in the file.

    ---- Globals read ----
    SUPERSCRIPT_TABLE, UNIT_PATTERN (module constants).

    ---- Outputs ----
    str
        The tidy label, for example '8 µg mL⁻¹ rifampicin' for '8ug ml-1 rifampicin';
        the same text when nothing can be tidied.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Micro and litre -----------------------------------------------------------
    text = re.sub(r'(?<![A-Za-z])u(?=(?:M|L|l|g|mol)(?![A-Za-z]))', 'µ', text)
    text = re.sub(r'(?<![A-Za-zµ])([mµn])l(?![A-Za-z])', r'\1L', text)
    # a litre by itself only where it cannot be a word: after a slash or with an exponent
    text = re.sub(r'(?<=/)l(?![A-Za-z])|(?<![A-Za-z0-9µ])l(?=\^?-\d)', 'L', text)

    # ---- 2 A space between a number and its unit -------------------------------------
    text = re.sub(rf'(\d)(?={UNIT_PATTERN}(?![A-Za-z]))', r'\1 ', text)

    # ---- 3 Raised exponents: -1 after a unit, anything after ^ -----------------------
    text = re.sub(rf'(?<![A-Za-z0-9µ])({UNIT_PATTERN})\^?(-\d)(?![\dA-Za-z])',
                  lambda match: match.group(1) + match.group(2).translate(SUPERSCRIPT_TABLE,
                                                                          ),
                  text,
                  )
    return re.sub(r'\^([-+]?\d+)',
                  lambda match: match.group(1).translate(SUPERSCRIPT_TABLE),
                  text,
                  )


# ---- multi_experiment_asker ----------------------------------------------------------
def multi_experiment_asker(summaries: List[dict],
                           answers: dict,
                           defaults: dict,
                           plotted: bool,
                           figure_checker: Optional[Callable[[str, dict], bool]] = None,
                           ) -> tuple:
    """
    ---- Summary ----
    Main function to ask the multi-experiment plots: the side-by-side figure of two
    experiments and the 2x2 figure of four experiments.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    plotted : bool
        True when the individual experiment plots show at least one panel (both
        figures reuse their choices).
    figure_checker : Optional[Callable[[str, dict], bool]]
        Function called after the questions of each figure with a name and a dictionary:
        ('comparison', {'comparison': ...}) or ('exemplar', {'exemplar_names': ...}). It
        shows the figure and returns True when the user accepts it. When it returns
        False the figure's questions are asked again with the answers as the defaults.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (comparison, exemplar_names). comparison is {'runs': (left, right),
        'columns', 'height'} or None; exemplar_names is the list of the four
        experiments of the 2x2 figure, or None.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    averaging_asker
    choice_asker
    info_printer
    run_name_lister
    size_asker
    yes_no_asker
    """

    comparison = None
    exemplar_names = None
    answers['plot_comparison'] = False
    answers['plot_exemplar'] = False
    if not plotted:
        info_printer('The figures below reuse the panels chosen for the individual '
                     'experiment plots, and nothing is plotted there, so they are '
                     'skipped.',
                     )
        return comparison, exemplar_names

    # ---- 1 Two experiments side by side ----------------------------------------------
    while True:
        comparison = None
        answers['plot_comparison'] = False
        if (len(summaries) >= 2 and
            yes_no_asker('Do you want to plot two experiments side ' 'by side?',
                         defaults['plot_comparison'],
                         )
            ):
            names = [(s['name'], s['name']) for s in summaries]
            first = choice_asker('Which experiment goes on the left?', names, depth=2)
            second = choice_asker('Which experiment goes on the right?',
                                  [n for n in names if n[0] != first],
                                  depth=2,
                                  )
            size_asker(answers,
                       defaults,
                       {'journal': 'comparison_journal',
                        'columns': 'comparison_columns',
                        'height': 'comparison_height',
                        'mode': 'comparison_size_mode',
                        },
                       (1.5, 0.5),
                       depth=2,
                       )
            comparison = {'runs': (first, second),
                          'columns': answers['comparison_columns'],
                          'height': answers['comparison_height'],
                          }
            answers['plot_comparison'] = True
        if (comparison is None or figure_checker is None or
                figure_checker('comparison', {'comparison': comparison})
                ):
            break
        defaults = dict(answers)

    # ---- 2 Four experiments in a 2x2 grid --------------------------------------------
    while True:
        exemplar_names = None
        answers['plot_exemplar'] = False
        if (len(summaries) >= 4 and
            yes_no_asker('Do you want to plot four experiments in a '
                         '2x2 grid (knockdown and control, two '
                         'addition orders)?',
                         defaults['plot_exemplar'],
                         )
            ):
            info_printer('Names are read as <strain>_<order>_run<N>, e.g. '
                         "'knockdown_kcn_then_bd_run1'.",
                         depth=2,
                         )
            rows = [r
                    for r in run_name_lister([s['name'] for s in summaries])
                    if all(r[k] is not None for k in ('strain', 'order', 'run'))
                    ]
            runs = sorted({r['run'] for r in rows})
            if not runs:
                info_printer('No file name fits, so this figure is skipped.', depth=2)
            else:
                old = defaults['ho_exemplar_run']
                run = choice_asker('Which run number should be shown?',
                                   [(r, f'run {r}') for r in runs],
                                   old if old in runs else runs[0],
                                   depth=2,
                                   )
                answers['ho_exemplar_run'] = int(run)
                if not answers['averaging']:
                    info_printer('This figure starts at the baseline averaging window, '
                                 'so the events are averaged as in the processing.',
                                 depth=2,
                                 )
                    averaging_asker(answers, defaults, forced=True, depth=2)
                    answers['averaging'] = True
                exemplar_names = [r['name'] for r in rows if r['run'] == int(run)]
                info_printer(f"Using: {', '.join(exemplar_names)}", depth=2)
                answers['ex_watermark'] = yes_no_asker(
                    'Do you want the run name written faintly on each plot?',
                    defaults['ex_watermark'],
                    depth=2,
                    )
                size_asker(answers,
                           defaults,
                           {'journal': 'ex_journal',
                            'columns': 'ho_ex_columns',
                            'height': 'ho_ex_height',
                            'mode': 'ex_size_mode',
                            },
                           (2, 0.75),
                           depth=2,
                           )
                answers['plot_exemplar'] = True
        if (exemplar_names is None or figure_checker is None or
                figure_checker('exemplar', {'exemplar_names': exemplar_names})
                ):
            break
        defaults = dict(answers)
    return comparison, exemplar_names


# ---- ocr_kind_lister -----------------------------------------------------------------
def ocr_kind_lister(has_od: bool) -> List[str]:
    """
    ---- Summary ----
    Main function to list the kinds of OCR that can be offered: the OCR itself, the OCR
    per OD when OD values were entered, and the OCR as a percentage of its range.

    ---- Inputs ----
    has_od : bool
        True when OD values were entered (scaling by OD is on).

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The keys 'raw', 'od' (only with OD values) and 'percent', in the order they are
        offered.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return ['raw'] + (['od'] if has_od else []) + ['percent']


# ---- ocr_option_builder --------------------------------------------------------------
def ocr_option_builder(keys: List[str]) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to build the (key, label) choices for the OCR questions, using
    the units of the plot axes.

    ---- Inputs ----
    keys : List[str]
        OCR kinds offered: 'raw', 'od' and/or 'percent'.

    ---- Globals read ----
    OCR_LABELS (module constant).

    ---- Outputs ----
    List[Tuple[str, str]]
        [(key, label), ...] in the order of ``keys``.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [(key, OCR_LABELS[key]) for key in keys]


# ---- od_scaling_asker ----------------------------------------------------------------
def od_scaling_asker(summaries: List[dict],
                     answers: dict,
                     defaults: dict,
                     saved: dict,
                     table_filler: Callable[[Dict[str, dict]], Dict[str, dict]],
                     ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask whether to scale by OD and, if so, have the OD, volume and
    dilution factor of every file filled in in the table, starting from the stored
    values.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers (normalise_od).
    saved : dict
        {file name: OD values and events saved before} (saved_values_reader).
    table_filler : Callable[[Dict[str, dict]], Dict[str, dict]]
        Function that shows the OD table filled in with the given rows (od_rows,
        DATA_FORMAT.md), waits until every cell is right, and returns the rows.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'OD', 'volume', 'dilution_factor'}}; the dictionaries are empty
        when not scaling by OD.

    ---- Globals mutated ----
    None. Stores normalise_od in ``answers`` and reads from and prints to the terminal
    (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    yes_no_asker
    """

    # ---- 1 Ask whether to scale ------------------------------------------------------
    answers['normalise_od'] = yes_no_asker(
        'Do you want to scale by OD?',
        defaults['normalise_od'],
        note='Scaling by OD divides the OCR and the haems by '
        'dilution factor × OD × volume; a per OD box for '
        'each then shows in the strip under the plot.',
        number='3.1',
        )
    details = {s['name']: {} for s in summaries}
    if not answers['normalise_od']:
        return details

    # ---- 2 Fill in the table ---------------------------------------------------------
    rows = {}
    for summary in summaries:
        old = saved.get(summary['name']) or {}
        rows[summary['name']] = {'OD': old.get('OD'),
                                 'volume': old.get('volume'),
                                 'dilution_factor': old.get('dilution_factor') or 1.0,
                                 }
    for name, values in table_filler(rows).items():
        details[name].update(values)
    return details


# ---- paf_finder ----------------------------------------------------------------------
def paf_finder(folder: Path) -> List[Path]:
    """
    ---- Summary ----
    Helper function to list the .paf files directly inside a folder, by name.

    ---- Inputs ----
    folder : Path
        Existing folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Path]
        The .paf files, sorted case-insensitively by name.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _natural_sorter
    """

    files = [p
             for p in Path(folder).iterdir()
             if p.is_file() and p.suffix.lower() == '.paf'
             ]
    return sorted(files, key=lambda p: _natural_sorter(p.name))


# ---- results_counter -----------------------------------------------------------------
def results_counter(export_root: Path, summaries: List[dict]) -> int:
    """
    ---- Summary ----
    Main function to count the files that already have results in a results folder:
    their own folder there (named as the export names it) holds something.

    ---- Inputs ----
    export_root : Path
        The results folder; it may not exist yet.
    summaries : List[dict]
        File summaries (DATA_FORMAT.md); uses 'name'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        How many of the files have results there.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    """

    count = 0
    for summary in summaries:
        own = Path(export_root) / file_name_sanitiser(summary['name'])
        if own.is_dir() and any(own.iterdir()):
            count += 1
    return count


# ---- results_folder_checker ----------------------------------------------------------
def results_folder_checker(text: Optional[str],
                           data_folder: Optional[Path] = None,
                           ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to check the results folder as soon as it is given: it must not be a
    file, and it must be a folder that can be saved to. A folder that does not exist yet
    is checked at the nearest folder above it that does; nothing is left behind.

    ---- Inputs ----
    text : Optional[str]
        The answer as typed or dragged in (quotes and a leading ~ are allowed).
    data_folder : Optional[Path]
        The data folder a name without a path is made in; None for the folder the
        program runs in.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        None when the folder can be used, otherwise the one sentence saying what to
        type instead.

    ---- Globals mutated ----
    None. Makes and removes a temporary file in the nearest existing folder (side
    effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    results_folder_resolver
    """

    # ---- 1 Find the nearest folder that exists ---------------------------------------
    if not text:
        return 'Type or drag in a folder.'
    nearest = results_folder_resolver(text, data_folder)
    while not nearest.exists():
        if nearest.parent == nearest:  # a drive or root that is not there
            return 'Type or drag in a folder you can save to.'
        nearest = nearest.parent
    if not nearest.is_dir():
        return 'Type or drag in a folder, not a file.'

    # ---- 2 Try to save in it ---------------------------------------------------------
    try:
        with tempfile.TemporaryFile(dir=nearest):
            pass
    except OSError:  # read-only, or not allowed: the run's log could not start there
        return 'Type or drag in a folder you can save to.'
    return None


# ---- results_folder_resolver ---------------------------------------------------------
def results_folder_resolver(text: str, data_folder: Optional[Path] = None) -> Path:
    """
    ---- Summary ----
    Main function to turn the results folder answer into its path: a name or path
    without a drive or root (quadratic_scatter_results) is taken inside the data
    folder, so a second set of results sits beside the first.

    ---- Inputs ----
    text : str
        The answer as typed or dragged in (quotes and a leading ~ are allowed).
    data_folder : Optional[Path]
        The data folder; None leaves such a name to the folder the program runs in.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The results folder.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    path_cleaner
    """

    path = Path(path_cleaner(text)).expanduser()
    if data_folder is not None and not path.is_absolute():
        return Path(data_folder) / path
    return path


# ---- saved_values_reader -------------------------------------------------------------
def saved_values_reader(summaries: List[dict],
                        remembered: Dict[str, dict],
                        export_root: Path,
                        ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to gather the OD values and event labels saved for each file, so they
    can be offered as defaults: those in the dataset's settings file, or, for a file
    with none there yet, those in its workbook from an earlier run.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    remembered : Dict[str, dict]
        The files part of the dataset's settings (dataset_settings, DATA_FORMAT.md).
    export_root : Path
        Results folder, where the workbooks of an earlier run are looked for.

    ---- Globals read ----
    SAVED_VALUE_KEYS (imported constant).

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'OD', 'volume', 'dilution_factor', 'events'} as far as saved, or
        None when nothing is}.

    ---- Globals mutated ----
    None. Prints progress and a note when values come from the workbooks (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    progress_clearer
    progress_printer
    saved_settings_reader
    """

    saved = {}
    from_workbooks = False
    for number, summary in enumerate(summaries, start=1):
        name = summary['name']
        entry = remembered.get(name) or {}
        kept = {k: entry[k] for k in SAVED_VALUE_KEYS if entry.get(k) is not None}
        if kept:
            saved[name] = kept
            continue
        progress_printer(f'Looking for earlier values, file {number} of '
                         f'{len(summaries)} ...',
                         )
        saved[name] = saved_settings_reader(export_root, name)
        from_workbooks = from_workbooks or bool(saved[name])
    progress_clearer()
    if from_workbooks:
        info_printer(
            '\nOD values and event labels from the workbooks of an earlier run '
            'are offered as defaults.',
            )
    return saved


# ---- signal_asker --------------------------------------------------------------------
def signal_asker(answers: dict, defaults: dict) -> bool:
    """
    ---- Summary ----
    Main function to ask whether the oxygen traces and the OCR are plotted, and which
    OCR.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in; must hold normalise_od.
    defaults : dict
        Default answers.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the oxygen or the OCR is plotted.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    ocr_kind_lister
    ocr_option_builder
    yes_no_asker
    """

    answers['plot_o2'] = yes_no_asker('Do you want to plot the set and measured [O2] '
                                      '(CsO2 and CcO2)?',
                                      defaults['plot_o2'],
                                      )
    answers['plot_ocr'] = yes_no_asker('Do you want to plot the OCR?',
                                       defaults['plot_ocr'],
                                       )
    if answers['plot_ocr']:
        keys = ocr_kind_lister(answers['normalise_od'])
        answers['ocr_mode'] = choice_asker('Which OCR would you like to plot?',
                                           ocr_option_builder(keys),
                                           defaults['ocr_mode']
                                           if defaults['ocr_mode'] in keys
                                           else keys[0],
                                           depth=2,
                                           )
    return answers['plot_o2'] or answers['plot_ocr']


# ---- size_asker ----------------------------------------------------------------------
def size_asker(answers: dict,
               defaults: dict,
               keys: dict,
               fallback: Tuple[float, float],
               depth: int = 1,
               ) -> None:
    """
    ---- Summary ----
    Main function to ask the journal, width and height of one figure. Answering None
    to the journal question uses Nature with the fallback width and height.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    keys : dict
        Names of the answers: {'journal', 'columns', 'height', 'mode'}.
    fallback : Tuple[float, float]
        (columns, height) used when the journal is None.
    depth : int
        Numbering depth of the journal question.

    ---- Globals read ----
    config.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the four answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _columns_text_builder
    choice_asker
    number_asker
    """

    # ---- 1 Build the journal options -------------------------------------------------
    columns_default, height_default = fallback
    options = [('none',
                'None (use the default: Nature, '
                f'{_columns_text_builder(columns_default)} wide, '
                f'{height_default:g} of a page tall)',
                ),
               ]
    options += [(key, name) for key, name in JOURNAL_NAMES.items()]
    remembered = (defaults[keys['journal']]
                  if defaults[keys['mode']] == 'custom'
                  else 'none'
                  )

    # ---- 2 Ask for the journal -------------------------------------------------------
    journal = choice_asker('Which journal format would you like?',
                           options,
                           remembered if remembered in dict(options) else 'none',
                           depth=depth,
                           )
    if journal == 'none':
        answers[keys['mode']] = 'default'
        answers[keys['journal']] = 'nature'
        answers[keys['columns']] = columns_default
        answers[keys['height']] = height_default
        return

    # ---- 3 Ask for the width ---------------------------------------------------------
    answers[keys['mode']] = 'custom'
    answers[keys['journal']] = journal
    spec = settings.JOURNAL_SPECS[journal]
    widths = [(c, f'{_columns_text_builder(c)} wide ({mm} mm)')
              for c, mm in spec['widths_mm'].items()
              ]
    old = defaults[keys['columns']]
    answers[keys['columns']] = choice_asker('How wide should the figure be?',
                                            widths,
                                            old
                                            if old in spec['widths_mm']
                                            else widths[0][0],
                                            depth=depth + 1,
                                            )

    # ---- 4 Ask for the height --------------------------------------------------------
    page = spec['page_height_mm']
    answers[keys['height']] = number_asker('How tall should the figure be, as a '
                                           f'fraction of the page height (1 = a full '
                                           f'page = {page:g} mm)?',
                                           defaults[keys['height']],
                                           minimum=0,
                                           exclusive_minimum=True,
                                           maximum=1,
                                           depth=depth + 1,
                                           )


# ---- temperature_asker ---------------------------------------------------------------
def temperature_asker(answers: dict, defaults: dict) -> None:
    """
    ---- Summary ----
    Main function to ask the temperature of the runs, once for the dataset; Δψ is
    worked out with it.

    ---- Inputs ----
    answers : dict
        Answers dictionary the value is stored in.
    defaults : dict
        Default answers (temperature_c).

    ---- Globals read ----
    TEMPERATURE_LIMITS_C (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores temperature_c (°C) in ``answers`` and reads from and prints to the
    terminal (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    number_asker
    """

    answers['temperature_c'] = number_asker('What was the temperature of the runs '
                                            '(°C)?',
                                            defaults['temperature_c'],
                                            minimum=TEMPERATURE_LIMITS_C[0],
                                            maximum=TEMPERATURE_LIMITS_C[1],
                                            number='3.1.2',
                                            )


# ---- tidy_labels_finder --------------------------------------------------------------
def tidy_labels_finder(with_events: List[dict],
                       result: Dict[str, List[dict]],
                       kept: Set[str],
                       ) -> List[Tuple[str, float, dict, str]]:
    """
    ---- Summary ----
    Main function to find the event labels that could be written more tidily (8 ug
    ml-1 as 8 µg mL⁻¹), leaving out the events left out and the labels the user chose
    to keep as they are.

    ---- Inputs ----
    with_events : List[dict]
        File summaries (DATA_FORMAT.md) of the files that have events.
    result : Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}, one
        per event of the summary, in the same order.
    kept : Set[str]
        Labels the user chose to keep as they are.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, float, dict, str]]
        (file name, time of the event in min, its entry in ``result``, tidy form) for
        each such label, in the order of the files and events.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    label_tidier
    """

    found = []
    for summary in with_events:
        for event, entry in zip(summary['events'], result[summary['name']]):
            tidy = label_tidier(entry['label'])
            is_left_alone = entry['ignored'] or entry['label'] in kept
            if tidy != entry['label'] and not is_left_alone:
                found.append((summary['name'], event['time'], entry, tidy))
    return found


# ---- trim_layout_finder --------------------------------------------------------------
def trim_layout_finder(summary: dict,
                       minutes: Dict[str, float],
                       ) -> Tuple[List[Tuple[str, float, str, str]],
                                  List[Tuple[float, float, str]],
                                  ]:
    """
    ---- Summary ----
    Main function to say where the four edges of one file sit on the plot of its whole
    recording, with the words by each handle, and which parts are shaded.

    ---- Inputs ----
    summary : dict
        Experiment summary with duration_min.
    minutes : Dict[str, float]
        {trim_start, trim_end, ignore_start, ignore_end}: the minutes taken off each
        edge (trim end from the end of the recording, ignore times from the trimmed
        edges), as kept by trim_minutes_setter.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
        (edges, parts): edges as [(key, time_min, words, kind)] with kind 'trim' or
        'ignore', in the order of TRIM_KEYS; parts as [(start_min, end_min, kind)],
        times on the whole recording.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Kept start = trim start; kept end = duration - trim end; ignore start edge = kept
    start + ignore start; ignore end edge = kept end - ignore end.

    ---- Helpers ----
    None.
    """

    duration = float(summary['duration_min'])
    start = minutes['trim_start']
    end = duration - minutes['trim_end']
    first = start + minutes['ignore_start']
    last = end - minutes['ignore_end']
    words = {key: f"{'trimmed' if key.startswith('trim') else 'ignored'} "
                  f'{round(minutes[key], 2):g} min'
             for key in TRIM_KEYS
             }
    edges = [('trim_start', start, words['trim_start'], 'trim'),
             ('trim_end', end, words['trim_end'], 'trim'),
             ('ignore_start', first, words['ignore_start'], 'ignore'),
             ('ignore_end', last, words['ignore_end'], 'ignore'),
             ]
    parts = [(0.0, start, 'trim'),
             (end, duration, 'trim'),
             (start, first, 'ignore'),
             (last, end, 'ignore'),
             ]
    return edges, parts


# ---- trim_limits_builder -------------------------------------------------------------
def trim_limits_builder(summaries: List[dict],
                        minutes: Dict[str, Dict[str, float]],
                        ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to turn the minutes chosen for every file into the trim and ignore
    limits the rest of the program uses and saves.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    minutes : Dict[str, Dict[str, float]]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes taken
        off each edge (trim_minutes_builder).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'trim_start', 'trim_end' (times on the original recording, or None
        for no trim), 'ignore_start', 'ignore_end' (minutes, counted from the trimmed
        edges)}}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trim start = minutes; trim end = duration - minutes.

    ---- Helpers ----
    _limit_converter
    """

    limits = {}
    for summary in summaries:
        own = minutes[summary['name']]
        limits[summary['name']] = {
            'trim_start': _limit_converter(summary, 'trim', 'start', own['trim_start']),
            'trim_end': _limit_converter(summary, 'trim', 'end', own['trim_end']),
            'ignore_start': float(own['ignore_start']),
            'ignore_end': float(own['ignore_end']),
            }
    return limits


# ---- trim_minutes_builder ------------------------------------------------------------
def trim_minutes_builder(summaries: List[dict],
                         remembered: Dict[str, dict],
                         ) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Main function to give the minutes each file starts the trimming step with: those
    remembered for it, otherwise the standard settings (only the start ignored), kept
    within the file's own limits.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    remembered : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} as the limits are
        kept (trim_limits_builder), from the last run or the last time the step was
        answered; a file or key may be missing.

    ---- Globals read ----
    config.DEFAULT_ANSWERS (the minutes ignored at the start); TRIM_KEYS.

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes taken
        off each edge.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trim end minutes = duration - remembered end time.

    ---- Helpers ----
    _minutes_recaller
    _trim_minutes_clamper
    """

    standard = {key: 0.0 for key in TRIM_KEYS}
    standard['ignore_start'] = float(settings.DEFAULT_ANSWERS['ignore_first_minutes'])
    minutes = {}
    for summary in summaries:
        own = {}
        for key in TRIM_KEYS:
            recalled = _minutes_recaller(summary, remembered, key)
            own[key] = standard[key] if recalled is None else float(recalled)
        minutes[summary['name']] = _trim_minutes_clamper(summary, own, 'trim_start')
    return minutes


# ---- trim_minutes_setter -------------------------------------------------------------
def trim_minutes_setter(summary: dict,
                        minutes: Dict[str, float],
                        key: str,
                        value: float,
                        ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to set one edge of one file to a number of minutes, kept within the
    file's limits: a trimmed edge never cuts off an event, and the ignored parts stay
    inside the kept part without crossing. When the ignored parts no longer fit, the
    one on the side of the edge being set gives way first.

    ---- Inputs ----
    summary : dict
        Experiment summary with events and duration_min.
    minutes : Dict[str, float]
        {trim_start, trim_end, ignore_start, ignore_end} of the file, in minutes taken
        off each edge.
    key : str
        The edge set: one of TRIM_KEYS.
    value : float
        Minutes wanted for it; below 0 counts as 0.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, float]
        New minutes of the file; the dictionary given is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _trim_minutes_clamper
    """

    return _trim_minutes_clamper(summary, {**minutes, key: float(value)}, key)


# ---- trim_pointer_reader -------------------------------------------------------------
def trim_pointer_reader(summary: dict,
                        minutes: Dict[str, float],
                        key: str,
                        time_min: float,
                        ) -> float:
    """
    ---- Summary ----
    Main function to turn a time pointed at on the plot of the whole recording into the
    minutes that put one edge there, in steps of 0.1 min.

    ---- Inputs ----
    summary : dict
        Experiment summary with duration_min.
    minutes : Dict[str, float]
        {trim_start, trim_end, ignore_start, ignore_end} of the file now, in minutes
        taken off each edge; the ignore times count from the trimmed edges.
    key : str
        The edge being moved: one of TRIM_KEYS.
    time_min : float
        The time pointed at, on the original recording (min).

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Minutes for that edge, rounded to 0.1; 0 when the time is beyond the edge.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trim start = t. Trim end = duration - t. Ignore start = t - trim start. Ignore end
    = (duration - trim end) - t.

    ---- Helpers ----
    None.
    """

    duration = float(summary['duration_min'])
    found = {'trim_start': time_min,
             'trim_end': duration - time_min,
             'ignore_start': time_min - minutes['trim_start'],
             'ignore_end': duration - minutes['trim_end'] - time_min,
             }[key]
    return round(max(float(found), 0.0), 1)
