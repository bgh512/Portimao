"""
Numbered terminal questions of the main program (sections 1 to 5).
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.run_namer import run_name_lister
from utils_shared.helpers import name_simplifier
from utils_shared.individual_experiment_exporter import saved_settings_reader
from utils_shared.paf_reader import experiment_summary_reader, PafError
from utils_shared.questions import (choice_asker,
                                    info_printer,
                                    multi_asker,
                                    number_asker,
                                    numbering_restarter,
                                    numbering_setter,
                                    numbers_asker,
                                    path_cleaner,
                                    progress_clearer,
                                    progress_printer,
                                    text_asker,
                                    text_italiser,
                                    yes_no_asker,
                                    )
from utils_shared.spectral_decomposer import fit_importer


# ---- CONSTANTS -----------------------------------------------------------------------
_file_focus_hook: Optional[Callable[[str], None]] = None
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
        For example '  15.01 min: nd-011992' or with the concentration and
        '[IGNORED]' when they apply.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    conc = (''
            if entry['concentration_uM'] is None
            else f", {entry['concentration_uM']:g} uM"
            )
    note = '  [IGNORED]' if entry['ignored'] else ''
    return f"  {event['time']:.2f} min: {entry['label']}{conc}{note}"


# ---- _file_focuser -------------------------------------------------------------------
def _file_focuser(name: str) -> None:
    """
    ---- Summary ----
    Helper function to tell the experiment browser which file the next question is
    about, so its window shows that file. Does nothing without the browser.

    ---- Inputs ----
    name : str
        File name.

    ---- Globals read ----
    _file_focus_hook (module state).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Calls the hook (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if _file_focus_hook is not None:
        _file_focus_hook(name)


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


# ---- _limits_asker -------------------------------------------------------------------
def _limits_asker(summaries: List[dict],
                  remembered: dict,
                  kind: str,
                  edge: str,
                  collected: dict,
                  progress: Callable[[Dict[str, dict]], None],
                  ) -> None:
    """
    ---- Summary ----
    Helper function to ask the questions for one edge of the data (trim start, trim end,
    ignore start or ignore end): whether to do it at all, how many minutes for ALL the
    files, and then optionally how many for each file. The limits are stored and passed
    to ``progress`` after every answer, so a plot can show them building up.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    remembered : dict
        {file name: {key: value}} from the last run, offered as the defaults.
    kind : str
        'trim' or 'ignore'.
    edge : str
        'start' or 'end'.
    collected : dict
        {file name: {key: value}} of the limits asked so far; this question adds its
        own key.
    progress : Callable[[Dict[str, dict]], None]
        Function called with the limits of every file after each answer.

    ---- Globals read ----
    config.DEFAULT_ANSWERS (default ignore time at the start).

    ---- Outputs ----
    None
        Nothing; the answers are stored in ``collected``.

    ---- Globals mutated ----
    collected (adds the key of this question for every file). Reads from and prints to
    the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _file_focuser
    _first_event_finder
    _last_event_finder
    _limit_converter
    _limit_maximum_getter
    _limits_filler
    _minutes_recaller
    info_printer
    number_asker
    yes_no_asker
    """

    key = f'{kind}_{edge}'
    verb, place = kind.upper(), edge.upper()
    past = 'TRIMMED' if kind == 'trim' else 'IGNORED'
    fallback = (settings.DEFAULT_ANSWERS['ignore_first_minutes']
                if key == 'ignore_start' else 0.0
                )
    old = {s['name']: _minutes_recaller(s, remembered, key) for s in summaries}
    known = [value for value in old.values() if value is not None]
    default_yes = any(known) or (fallback > 0 and not known)
    if not yes_no_asker(f'Do you want to {verb} the {place} of any of the data?',
                        default_yes,
                        ):
        for summary in summaries:
            collected[summary['name']][key] = _limit_converter(summary, kind, edge, 0)
        return

    # ---- 1 One value for ALL the data ------------------------------------------------
    maxima = {s['name']: _limit_maximum_getter(s, kind, edge, collected[s['name']])
              for s in summaries
              }
    caps = [value for value in maxima.values() if value is not None]
    common_default = max(set(known), key=known.count) if known else fallback
    if caps:
        common_default = min(common_default, min(caps))
    common = number_asker(f'How many minutes should be {past} from the {place} of '
                          'ALL the data?',
                          common_default,
                          minimum=0,
                          maximum=min(caps, default=None),
                          depth=2,
                          )
    for summary in summaries:
        collected[summary['name']][key] = _limit_converter(summary, kind, edge, common)
    progress(_limits_filler(summaries, collected))
    differs = any(value != common for value in known)
    if not yes_no_asker('Do you want to adjust this for any specific file?',
                        differs,
                        depth=2,
                        ):
        return

    # ---- 2 One value per file, drawn as it is answered -------------------------------
    for summary in summaries:
        name = summary['name']
        _file_focuser(name)
        if kind == 'trim':
            event = (_first_event_finder(summary) if edge == 'start'
                     else _last_event_finder(summary)
                     )
            which = 'first' if edge == 'start' else 'last'
            info_printer(f'{name}: {which} event at {event:.1f} min, recording '
                         f"{summary['duration_min']:.1f} min",
                         depth=2,
                         )
        default = old[name] if old[name] is not None else common
        if maxima[name] is not None:
            default = min(default, maxima[name])
        minutes = number_asker(f'How many minutes should be {past} from the {place} '
                               f'of {name}?',
                               default,
                               minimum=0,
                               maximum=maxima[name],
                               depth=2,
                               )
        collected[name][key] = _limit_converter(summary, kind, edge, minutes)
        progress(_limits_filler(summaries, collected))


# ---- _limits_filler ------------------------------------------------------------------
def _limits_filler(summaries: List[dict], collected: dict) -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to give every file all four limits, using "none" for the ones not
    asked yet.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    collected : dict
        {file name: {key: value}} of the limits asked so far.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}}; the trim limits
        are None and the ignore limits 0.0 when not set.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {s['name']: {'trim_start': collected[s['name']].get('trim_start'),
                        'trim_end': collected[s['name']].get('trim_end'),
                        'ignore_start': collected[s['name']].get('ignore_start') or 0.0,
                        'ignore_end': collected[s['name']].get('ignore_end') or 0.0,
                        }
            for s in summaries
            }


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


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- analysis_asker ------------------------------------------------------------------
def analysis_asker(summaries: List[dict],
                   answers: dict,
                   defaults: dict,
                   fits_folder: Path,
                   export_root: Path,
                   ) -> tuple:
    """
    ---- Summary ----
    Main function to ask section 3: haem decomposition, OD scaling, event averaging
    and the event labels.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    fits_folder : Path
        Folder holding the fit .csv files.
    export_root : Path
        Results folder, where the saved OD and event values are looked for.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fit, details). details is {file name: {'OD', 'volume', 'dilution_factor',
        'events'}}; the OD entries are only present when scaling by OD.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    averaging_asker
    decomposition_asker
    event_asker
    od_scaling_asker
    saved_values_reader
    """

    # ---- 1 Decomposition -------------------------------------------------------------
    (answers['decompose'],
     answers['fit_file'],
     fit,
     answers['decomposition_dataset'],
     ) = decomposition_asker(summaries, defaults, fits_folder)

    # ---- 2 OD scaling ----------------------------------------------------------------
    saved = saved_values_reader(summaries, export_root)
    details = od_scaling_asker(summaries, answers, defaults, saved)

    # ---- 3 Averaging -----------------------------------------------------------------
    averaging_asker(answers, defaults)

    # ---- 4 Event labels --------------------------------------------------------------
    for name, events in event_asker(summaries, saved).items():
        details[name]['events'] = events
    return fit, details


# ---- averaging_asker -----------------------------------------------------------------
def averaging_asker(answers: dict,
                    defaults: dict,
                    forced: bool = False,
                    depth: int = 1,
                    ) -> None:
    """
    ---- Summary ----
    Main function to ask whether to average around the events, and the window
    settings.

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

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores window_minutes and gap_minutes (and averaging) in ``answers``.

    ---- Equations ----
    None.

    ---- Helpers ----
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

    # ---- 2 Ask for the window and gap ------------------------------------------------
    sub = depth if forced else depth + 1
    answers['window_minutes'] = number_asker('How long a window (minutes) should the '
                                             'average be taken over?',
                                             defaults['window_minutes'],
                                             minimum=0,
                                             exclusive_minimum=True,
                                             depth=sub,
                                             )
    answers['gap_minutes'] = number_asker('How long before the next addition should '
                                          'the averaging window end (minutes)?',
                                          defaults['gap_minutes'],
                                          minimum=0,
                                          depth=sub,
                                          )
    answers['window_asked'] = True


# ---- decomposition_asker -------------------------------------------------------------
def decomposition_asker(summaries: List[dict],
                        defaults: dict,
                        fits_folder: Path,
                        forced: bool = False,
                        depth: int = 1,
                        pca_runner: Optional[Callable] = None,
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
    fit_importer
    info_printer
    yes_no_asker
    """

    # ---- 1 Find the available fits ---------------------------------------------------
    none_chosen = (False, None, None, defaults['decomposition_dataset'])
    fits = sorted(fits_folder.glob('*.csv'), key=lambda p: p.name.lower())
    if not fits and pca_runner is None:
        info_printer(f'No fit files (.csv) were found in {fits_folder}, so haems '
                     f'cannot be '
                     'decomposed this time. Put a fit .csv in that folder and run '
                     'again.',
                     )
        return none_chosen
    if (not forced and
        not yes_no_asker('Do you want to decompose the haems?',
                         defaults['decompose'],
                         depth=depth,
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
                                      )
        return chosen

    # ---- 2 Choose the fit, and the spectral dataset ----------------------------------
    names = [p.name for p in fits]
    default_fit = defaults.get('fit_file')
    choices = [(n, n) for n in names]
    if pca_runner is not None:
        choices.append((PCA_CHOICE, 'Find the components from the data (principal '
                                    'component analysis)',
                        ))
    dataset = None
    while True:
        fit_file = choice_asker('Which fit would you like to use?',
                                choices,
                                default_fit if default_fit in names else choices[0][0],
                                depth=depth + (0 if forced else 1),
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
            fit = fit_importer(fits_folder / fit_file)
        except Exception as exc:
            info_printer(f'The fit file could not be read ({exc}); haems will not be '
                         f'decomposed.',
                         )
            return none_chosen
        break
    dataset = dataset or dataset_chooser(1)
    if dataset is None:
        return none_chosen
    return True, fit_file, fit, dataset


# ---- event_asker ---------------------------------------------------------------------
def event_asker(summaries: List[dict],
                saved: dict,
                again: bool = False,
                ) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Main function to ask whether to change the event labels, concentrations and which
    events to ignore, file by file.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    saved : dict
        {file name: values read from its workbook} (read_saved_settings).
    again : bool
        True when the user asked to change the labels again: the yes/no question is
        skipped and the runs are listed straight away.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}.
        A label of 'ignore' marks an event that was not an addition.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _event_line_builder
    _file_focuser
    info_printer
    number_asker
    numbering_setter
    numbers_asker
    text_asker
    yes_no_asker
    """

    # ---- 1 Start from the saved or file values ---------------------------------------
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
                           'label': 'ignore'
                           if ignored
                           else (before.get('label') or event['text']),
                           'concentration_uM': before.get('concentration_uM'),
                           'ignored': ignored,
                           },
                          )
        result[summary['name']] = events
    with_events = [s for s in summaries if s['events']]
    if not with_events:
        return result

    # ---- 2 Show the current events and ask which runs to change ----------------------
    info_printer('Current runs with events are:')
    for number, summary in enumerate(with_events, start=1):
        info_printer(f"{number}) {summary['name']}:")
        for event, entry in zip(summary['events'], result[summary['name']]):
            info_printer(_event_line_builder(event, entry), depth=2)
    if not again and not yes_no_asker('Do you want to change any event labels?', False):
        return result
    chosen = numbers_asker('Which run(s) do you want to change?',
                           len(with_events),
                           depth=2,
                           )

    # ---- 3 Ask about the events of each chosen run -----------------------------------
    for number in chosen:
        summary = with_events[number - 1]
        name = summary['name']
        _file_focuser(name)
        events = result[name]
        info_printer(f'\n{name}:', depth=2)
        for event, entry in zip(summary['events'], events):
            info_printer(_event_line_builder(event, entry), depth=2)
        numbering_setter(2, number)
        for event, entry in zip(summary['events'], events):
            label = text_asker(f"What was added at {event['time']:.2f} min? "
                               "Write 'ignore' to ignore this event.",
                               entry['label'],
                               depth=3,
                               )
            entry['label'] = label or entry['label']
            entry['ignored'] = entry['label'].strip().lower() == 'ignore'
            if entry['ignored']:
                continue
            entry['concentration_uM'] = number_asker('What was the final concentration'
                                                     ' '
                                                     'in uM?',
                                                     entry['concentration_uM'],
                                                     minimum=0,
                                                     allow_blank=True,
                                                     depth=3,
                                                     blank_label='unknown',
                                                     )
    return result


# ---- file_focus_setter ---------------------------------------------------------------
def file_focus_setter(hook: Optional[Callable[[str], None]]) -> None:
    """
    ---- Summary ----
    Main function to set (or clear, with None) the function that is told which file a
    question is about.

    ---- Inputs ----
    hook : Optional[Callable[[str], None]]
        Function taking the file name, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    Sets _file_focus_hook (module state).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _file_focus_hook
    _file_focus_hook = hook


# ---- files_asker ---------------------------------------------------------------------
def files_asker(last: dict) -> Tuple[Path, List[dict], Path]:
    """
    ---- Summary ----
    Main function to ask for the folder of .paf files (1.1) and the results folder
    (1.2), and to read a summary of every file.

    ---- Inputs ----
    last : dict
        Remembered answers (last_answers.json); uses data_folder and export_folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Path, List[dict], Path]
        (data folder, summary of each readable file, results folder). Each summary
        has name, path, duration_min, events and datasets (DATA_FORMAT.md).

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_summary_reader
    info_printer
    paf_finder
    path_cleaner
    progress_clearer
    progress_printer
    text_asker
    """

    # ---- 1 Ask for the .paf folder ---------------------------------------------------
    # A hint only: folders ending _data in the program folder are listed, never chosen.
    root = Path(__file__).resolve().parents[1]
    data_folders = sorted(p.name for p in root.iterdir()
                          if p.is_dir() and p.name.endswith('_data')
                          )
    if data_folders:
        info_printer('_data folders found in ' + str(root) + ': '
                     + ', '.join(data_folders),
                     )
    while True:
        text = text_asker('What is the directory with the .paf files?',
                          last.get('data_folder'),
                          )
        if not text:
            info_printer('Please type or drag in a folder.')
            continue
        folder = Path(path_cleaner(text)).expanduser()
        if not folder.is_dir():
            info_printer('That folder does not exist.')
            continue
        files = paf_finder(folder)
        if not files:
            info_printer('There are no .paf files directly inside that folder.')
            continue
        break

    # ---- 2 Read every file -----------------------------------------------------------
    summaries = []
    for number, path in enumerate(files, start=1):
        progress_printer(f'Reading file {number} of {len(files)}: {path.name} ...')
        try:
            summary = experiment_summary_reader(path)
        except PafError as exc:
            progress_clearer()
            info_printer(f'Skipping {path.name}: {exc}')
            continue
        summary['path'] = path
        summaries.append(summary)
    progress_clearer()
    if not summaries:
        raise SystemExit('None of the .paf files could be read.')
    info_printer(f'\nFound {len(summaries)} readable file(s):')
    for summary in summaries:
        info_printer(f"  {summary['name']}: {summary['duration_min']:.1f} min, "
                     f"{len(summary['events'])} event(s)",
                     )

    # ---- 3 Ask for the results folder ------------------------------------------------
    same_folder = last.get('data_folder') == str(folder)
    default = last.get('export_folder') if same_folder else str(folder / 'export')
    text = text_asker('To which directory would you like the results to be saved?',
                      default,
                      )
    return folder, summaries, Path(path_cleaner(text)).expanduser()


# ---- haem_choice_asker ---------------------------------------------------------------
def haem_choice_asker(answers: dict, defaults: dict, fit: Optional[dict]) -> bool:
    """
    ---- Summary ----
    Main function to ask whether the haems are plotted, and which ones in which order.

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
    haem_name_sorter
    multi_asker
    yes_no_asker
    """

    answers['plot_haems'] = False
    if not (answers['decompose'] and fit is not None):
        return False
    answers['plot_haems'] = yes_no_asker('Do you want to plot the haems?',
                                         defaults['plot_haems'],
                                         )
    if answers['plot_haems']:
        answers['haems'] = multi_asker('Which haems would you like to plot, and in '
                                       'which order?',
                                       haem_name_sorter(fit['haem_list']),
                                       default_all=True,
                                       keep_order=True,
                                       depth=2,
                                       default_values=(defaults['haems']
                                                       or list(fit['haem_list'])
                                                       ),
                                       label_formatter=haem_name_formatter,
                                       )
    return answers['plot_haems']


# ---- haem_form_asker -----------------------------------------------------------------
def haem_form_asker(answers: dict, defaults: dict) -> None:
    """
    ---- Summary ----
    Main function to ask how the haems are shown (absorbance change, concentration,
    percentage and so on).

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
    choice_asker
    haem_form_option_builder
    """

    answers['haem_mode'] = choice_asker('How would you like to plot the haems?',
                                        haem_form_option_builder(True),
                                        defaults['haem_mode'],
                                        )


# ---- haem_form_option_builder --------------------------------------------------------
def haem_form_option_builder(include_percent: bool) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to build the (key, label) choices for the 'how to show the
    haems' questions. The delta A line explains itself in italics.

    ---- Inputs ----
    include_percent : bool
        True to offer the % oxidised choice.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, str]]
        [(key, label), ...]: abs, delta, conc and optionally percent.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    text_italiser
    """

    delta = f"ΔA (mOD), {text_italiser('the change in absorbance from the start')}"
    options = [('abs', 'Absorbance (mOD)'),
               ('delta', delta),
               ('conc', 'Concentration'),
               ]
    if include_percent:
        options.append(('percent', '% oxidised (lowest to highest = 0 to 100 %)'))
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


# ---- haem_name_sorter ----------------------------------------------------------------
def haem_name_sorter(names: List[str]) -> List[str]:
    """
    ---- Summary ----
    Main function to put haem names in alphabetical order of the name as shown (ignoring
    case and punctuation), for example a605, b557, bH, bL, cc.

    ---- Inputs ----
    names : List[str]
        Haem names as written in the fit file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The same names, sorted; the input list is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    name_simplifier
    """

    return sorted(names, key=name_simplifier)


# ---- haem_scaling_asker --------------------------------------------------------------
def haem_scaling_asker(answers: dict, defaults: dict) -> bool:
    """
    ---- Summary ----
    Main function to ask whether the haems are also scaled by OD. Nothing is asked when
    no OD values were entered or the haems are shown as percentages.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
        Must hold normalise_od and haem_mode.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the question was asked.

    ---- Globals mutated ----
    None. Stores the answer in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    yes_no_asker
    """

    answers['haem_per_od'] = False
    if not answers['normalise_od'] or answers['haem_mode'] == 'percent':
        return False
    answers['haem_per_od'] = yes_no_asker('Do you want to scale the haems by OD as '
                                          'well?',
                                          defaults['haem_per_od'],
                                          )
    return True


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


# ---- multi_experiment_asker ----------------------------------------------------------
def multi_experiment_asker(summaries: List[dict],
                           answers: dict,
                           defaults: dict,
                           plotted: bool,
                           figure_checker: Optional[Callable[[str, dict], bool]] = None,
                           ) -> tuple:
    """
    ---- Summary ----
    Main function to ask section 5: the side-by-side figure of two experiments and
    the 2x2 figure of four experiments.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    plotted : bool
        True when section 4 plots at least one panel (both figures reuse its choices).
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
        info_printer('The figures below reuse the panels chosen in section 4, and '
                     'nothing '
                     'is plotted there, so they are skipped.',
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
                                 'so '
                                 'the '
                                 'events are averaged as in section 3.3.',
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


# ---- od_asker ------------------------------------------------------------------------
def od_asker(summaries: List[dict], saved: dict) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the OD, volume and dilution factor of every file, offering the
    values saved in each experiment's workbook.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    saved : dict
        {file name: values read from its workbook} (read_saved_settings).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'OD', 'volume', 'dilution_factor'}}.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _file_focuser
    info_printer
    number_asker
    numbering_restarter
    """

    # ---- 1 Set up the answers --------------------------------------------------------
    values = {}

    # ---- 2 Ask for each experiment ---------------------------------------------------
    for summary in summaries:
        name = summary['name']
        _file_focuser(name)
        old = saved.get(name) or {}
        info_printer(f'\n{name}:', depth=2, tight=True)
        numbering_restarter(2)
        values[name] = {'OD': number_asker('What was the OD of the cells added?',
                                           old.get('OD'),
                                           minimum=0,
                                           exclusive_minimum=True,
                                           depth=2,
                                           ),
                        'volume': number_asker('What volume of cells (mL) were spun '
                                               'down '
                                               'and resuspended in 5 mL?',
                                               old.get('volume'),
                                               minimum=0,
                                               exclusive_minimum=True,
                                               depth=2,
                                               ),
                        'dilution_factor': number_asker('What is the dilution factor, '
                                                        'if '
                                                        'the cells were diluted mid '
                                                        'run?',
                                                        old.get('dilution_factor', 1.0),
                                                        minimum=0,
                                                        exclusive_minimum=True,
                                                        depth=2,
                                                        ),
                        }
    return values


# ---- od_scaling_asker ----------------------------------------------------------------
def od_scaling_asker(summaries: List[dict],
                     answers: dict,
                     defaults: dict,
                     saved: dict,
                     ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask whether to scale by OD and, if so, the OD, volume and dilution
    factor of every file, offering the stored values.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers (normalise_od).
    saved : dict
        {file name: values read from its workbook} (saved_values_reader).

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
    info_printer
    od_asker
    yes_no_asker
    """

    # ---- 1 Ask whether to scale ------------------------------------------------------
    answers['normalise_od'] = yes_no_asker('Do you want to scale by OD (divide by '
                                           'dilution factor x OD x volume)?',
                                           defaults['normalise_od'],
                                           )
    details = {s['name']: {} for s in summaries}
    if not answers['normalise_od']:
        return details

    # ---- 2 List what is stored -------------------------------------------------------
    # List what is already stored for each run and only ask about the rest unless
    # the user wants to change them.
    stored_keys = ('OD', 'volume', 'dilution_factor')
    complete = [s for s in summaries
                if all((saved.get(s['name']) or {}).get(k) for k in stored_keys[:2])
                ]
    if complete:
        info_printer('\nStored OD information:', depth=2, tight=True)
        for summary in summaries:
            old = saved.get(summary['name']) or {}
            if summary in complete:
                text = (f"OD {old['OD']:g}, volume {old['volume']:g} mL, dilution "
                        f"factor {old.get('dilution_factor', 1.0):g}"
                        )
            else:
                text = 'nothing stored'
            info_printer(f"  {summary['name']}: {text}", depth=2, tight=True)

    # ---- 3 Ask for the values --------------------------------------------------------
    change = (not complete) or yes_no_asker('Do you want to change any of these?',
                                            False,
                                            )
    to_ask = summaries if change else [s for s in summaries if s not in complete]
    for summary in complete:
        if summary not in to_ask:
            old = saved[summary['name']]
            dilution = old.get('dilution_factor', 1.0)
            details[summary['name']].update({'OD': old['OD'],
                                             'volume': old['volume'],
                                             'dilution_factor': dilution,
                                             },
                                            )
    if to_ask:
        for name, values in od_asker(to_ask, saved).items():
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


# ---- saved_values_reader -------------------------------------------------------------
def saved_values_reader(summaries: List[dict], export_root: Path) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to read the OD and event values saved in each experiment's workbook
    from an earlier run, so they can be offered as defaults.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    export_root : Path
        Results folder, where the saved workbooks are looked for.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: values read from its workbook, or None when there is none}.

    ---- Globals mutated ----
    None. Prints progress and a note when earlier values are found (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    progress_clearer
    progress_printer
    saved_settings_reader
    """

    saved = {}
    for number, summary in enumerate(summaries, start=1):
        progress_printer(f'Looking for earlier values, file {number} of '
                         f'{len(summaries)} ...',
                         )
        saved[summary['name']] = saved_settings_reader(export_root, summary['name'])
    progress_clearer()
    if any(saved.values()):
        info_printer("\nEarlier OD and event values found in the experiments' "
                     'workbooks are '
                     'offered as defaults.',
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
        keys = ['raw'] + (['od'] if answers['normalise_od'] else []) + ['percent']
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


# ---- trim_asker ----------------------------------------------------------------------
def trim_asker(summaries: List[dict],
               remembered: dict,
               progress: Optional[Callable[[Dict[str, dict]], None]] = None,
               ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask section 2: which data is trimmed away (start, end) and which
    is ignored in the calculations (start, end). Each edge is asked in turn with the
    same questions: do it at all, how many minutes for ALL the data, and optionally how
    many for each file.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    remembered : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} from the last
        run; offered as the defaults.
    progress : Optional[Callable[[Dict[str, dict]], None]]
        Function called with the limits of every file after each answer (so a plot can
        show them building up), or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'trim_start', 'trim_end' (minutes on the original recording, or
        None), 'ignore_start', 'ignore_end' (minutes, counted from the new 0 time)}}.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _limits_asker
    _limits_filler
    info_printer
    """

    # ---- 1 Explain the two words -----------------------------------------------------
    info_printer('TRIM: data that will not be imported, plotted or used.')
    info_printer('IGNORE: data that will be imported and plotted, but not used for '
                 'calculations (baselines, % ranges, axis limits).',
                 )

    # ---- 2 Ask the four edges in turn ------------------------------------------------
    collected: Dict[str, dict] = {s['name']: {} for s in summaries}
    reporter = progress or (lambda limits: None)
    for kind, edge in (('trim', 'start'),
                       ('trim', 'end'),
                       ('ignore', 'start'),
                       ('ignore', 'end'),
                       ):
        _limits_asker(summaries, remembered, kind, edge, collected, reporter)
    return _limits_filler(summaries, collected)
