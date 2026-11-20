"""
The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.pca_fitter import (component_builder,
                                     component_classifier,
                                     component_count_suggester,
                                     component_finder,
                                     decomposition_example_finder,
                                     fit_saver,
                                     fit_table_builder,
                                     TYPE_NAMES,
                                     )
from utils_shared.questions import (choice_asker,
                                    heading_printer,
                                    info_printer,
                                    number_asker,
                                    numbering_getter,
                                    numbering_setter,
                                    progress_clearer,
                                    progress_printer,
                                    section_starter,
                                    text_asker,
                                    text_colourer,
                                    yes_no_asker,
                                    )
from utils_shared.spectral_decomposer import fit_importer
from utils_shared.survey import (averaging_asker,
                                 decomposition_asker,
                                 event_asker,
                                 file_focus_setter,
                                 haem_choice_asker,
                                 haem_form_asker,
                                 haem_scaling_asker,
                                 label_angle_asker,
                                 ocr_kind_lister,
                                 od_scaling_asker,
                                 saved_values_reader,
                                 signal_asker,
                                 size_asker,
                                 trim_asker,
                                 )
from utils_viewer.viewer_preview import (all_data_exporter,
                                         BROWSING_ANSWERS,
                                         pca_example_picture_builder,
                                         pca_picture_builder,
                                         pca_spectra_gatherer,
                                         preview_drawer,
                                         skipped_windows_finder,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_gui import active_gui_getter
from utils_viewer.viewer_od_table import COLUMNS
from utils_viewer.viewer_strip import size_answers_builder, strip_values_builder
from utils_viewer.viewer_window import PictureWindow


# ---- CONSTANTS -----------------------------------------------------------------------
PREVIEW_FILE = Path(tempfile.gettempdir()) / 'Portimao_preview.png'
WARNING_COLOUR = '\x1b[1;31m'  # bold red
PCA_COMPONENTS_TITLE = 'PCA components'
PCA_EXAMPLES_TITLE = 'PCA examples (smallest and largest residual)'
DEFAULT_SMOOTHING_NM = 4.0  # offered width of the smoothing of the PCA components
STAGE_TITLES = {'browser': 'Experiment browser',
                'trim': 'Trimming and ignoring',
                'details': 'OD values and event labels',
                'processing': 'Processing',
                'plots': 'Individual experiment plots',
                }


# ---- STAGE HELPERS -------------------------------------------------------------------


# ---- _addition_time_lister -----------------------------------------------------------
def _addition_time_lister(summaries: List[dict],
                          limits: Dict[str, dict],
                          details: Dict[str, dict],
                          ) -> Dict[str, List[float]]:
    """
    ---- Summary ----
    Helper function to list the times of the additions of every file on the time axis
    of the processing plot, which starts at 0 where the trimmed data starts. Events
    marked ignore are left out, as the averaging leaves them out.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md), with the events as the file holds them.
    limits : Dict[str, dict]
        Trim and ignore limits of every file; 'trim_start' is on the original
        recording.
    details : Dict[str, dict]
        OD values and events of every file (details_stage_runner); an event's
        'ignored' says it was marked ignore.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, List[float]]
        {file name: addition times (min), in order}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time on the plot = time in the file - trim start.

    ---- Helpers ----
    None.
    """

    found = {}
    for summary in summaries:
        name = summary['name']
        shift = (limits.get(name) or {}).get('trim_start') or 0.0
        ignored = {event['datapoint']
                   for event in (details.get(name) or {}).get('events', [])
                   if event.get('ignored')
                   }
        found[name] = sorted(float(event['time']) - shift
                             for event in summary['events']
                             if event['datapoint'] not in ignored
                             )
    return found


# ---- _all_data_asker -----------------------------------------------------------------
def _all_data_asker(session: ViewerSession, limits: Dict[str, dict]) -> None:
    """
    ---- Summary ----
    Helper function to ask whether to export the data of every file now, cut to the
    limits just accepted, so it can be plotted outside the program, and to do it.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and writes the files (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    all_data_exporter
    info_printer
    progress_clearer
    progress_printer
    text_colourer
    yes_no_asker
    """

    if not yes_no_asker('Do you want to export all the data now, cut to these limits, '
                        'so you can plot it yourself?',
                        False,
                        ):
        return
    include_spectra = yes_no_asker('Do you want to include the spectra as csv files '
                                   '(large, and it takes a while)?',
                                   False,
                                   depth=2,
                                   )
    folder, problems = all_data_exporter(
        session,
        limits,
        include_spectra,
        lambda n, total: progress_printer(f'Exporting file {n} of {total} ...'),
    )
    progress_clearer()
    for problem in problems:
        info_printer(text_colourer(f'Not exported: {problem}', WARNING_COLOUR), depth=2)
    info_printer(f'Exported the data of {len(session.summaries) - len(problems)} '
                 f'file(s) to {folder}. It is not scaled by OD, decomposed or '
                 f'averaged, and the event labels are the ones in the files. The '
                 f'ignored parts are included.',
                 depth=2,
                 )


# ---- _answers_previewer --------------------------------------------------------------
def _answers_previewer(answers: dict, fit: Optional[dict], kind: str) -> dict:
    """
    ---- Summary ----
    Helper function to build the answers used to draw a preview: the raw data while
    browsing and trimming, and the processing chosen so far afterwards.

    ---- Inputs ----
    answers : dict
        Answers given so far.
    fit : Optional[dict]
        Fit dictionary, used to list the haems to show.
    kind : str
        'raw' (O2 and the raw OCR only), 'standard' (the standard plot: O2, the raw OCR
        and, when a fit is given, every haem of it as the change from the start),
        'analysis' (also the haems and the averaging windows, still without OD
        scaling) or 'final' (exactly as the figure will be).

    ---- Globals read ----
    BROWSING_ANSWERS (module constant).

    ---- Outputs ----
    dict
        A copy of the answers with the preview settings; ``answers`` is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    result = dict(answers)
    if kind == 'final':
        return result
    result.update(BROWSING_ANSWERS)
    result.update({'plot_o2': True, 'plot_ocr': True, 'plot_haems': False})
    if kind in ('raw', 'standard'):
        result.update({'decompose': False,
                       'normalise_od': False,
                       'averaging': False,
                       'ocr_mode': 'raw',
                       },
                      )
        if kind == 'standard' and fit is not None:
            result.update({'decompose': True,
                           'plot_haems': True,
                           'haems': list(fit['haem_list']),
                           'haem_mode': 'delta',
                           'haem_per_od': False,
                           },
                          )
        return result
    result.update({'normalise_od': False, 'ocr_mode': 'raw', 'haem_per_od': False})
    if result['decompose'] and fit is not None:
        result.update({'plot_haems': True,
                       'haems': list(fit['haem_list']),
                       'haem_mode': 'delta',
                       },
                      )
    return result


# ---- _averaging_reviewer -------------------------------------------------------------
def _averaging_reviewer(session: ViewerSession,
                        answers: dict,
                        defaults: dict,
                        limits: Dict[str, dict],
                        details: Dict[str, dict],
                        redraw: Callable[[], bool],
                        ) -> None:
    """
    ---- Summary ----
    Helper function to ask whether to average around the events and over which window,
    draw the windows, list in red those that do not fit, and ask whether to accept them
    or answer again. In the window, a drag across the plot of a file gives the window
    and the gap, from the additions of that file.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file; the windows are drawn around the events
        not ignored there.
    redraw : Callable[[], bool]
        Function that draws the preview of the current file with the answers so far.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the answers in ``answers``, reads from and prints to the terminal and
    redraws the window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _addition_time_lister
    _review_asker
    _skipped_lister
    averaging_asker
    """

    additions = (_addition_time_lister(session.summaries, limits, details)
                 if session.window.is_interactive
                 else None
                 )
    while True:
        averaging_asker(answers, defaults, additions=additions)
        if not answers['averaging']:
            return
        redraw()
        _skipped_lister(session, answers, limits, details)
        if _review_asker(session,
                         'Do you accept these averaging windows?',
                         'No, change the window and gap',
                         redraw,
                         ):
            return
        defaults = dict(defaults, averaging=True)
        defaults.update({k: answers[k] for k in ('window_minutes', 'gap_minutes')})


# ---- _choice_reviewer ----------------------------------------------------------------
def _choice_reviewer(session: ViewerSession,
                     question: str,
                     options: List[Tuple[str, str]],
                     redraw: Callable[[], bool],
                     ) -> str:
    """
    ---- Summary ----
    Helper function to ask whether the user accepts what the plot window shows, with as
    many answers as the step needs. In the browser window the user flicks through the
    files while the question waits; with the picture fallback a last answer lets the
    user look at another file, which redraws it, before the question is asked again.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file may be changed.
    question : str
        The accept question, for example 'Do you accept this figure?'.
    options : List[Tuple[str, str]]
        (key, label) of each answer; the first is the one Enter gives. The key 'file'
        is kept for looking at another file.
    redraw : Callable[[], bool]
        Function that draws the preview of the current file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Key of the answer chosen (never 'file').

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and redraws the window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _file_chooser
    choice_asker
    """

    options = list(options)
    if len(session.summaries) > 1 and not session.window.is_interactive:
        options.append(('file', 'Look at another file in the plot window first'))
    while True:
        choice = choice_asker(question, options, options[0][0])
        if choice != 'file':
            return choice
        _file_chooser(session)
        redraw()


# ---- _component_namer ----------------------------------------------------------------
def _component_namer(result: dict, types: List[str], depth: int) -> List[str]:
    """
    ---- Summary ----
    Helper function to ask whether to name the components and, if so, a name for each.
    The suggested names follow the haem type each component looks like (a-like,
    b-like, c-like, with a number when a type comes again).

    ---- Inputs ----
    result : dict
        Result of component_builder.
    types : List[str]
        Haem type of each component (component_classifier).
    depth : int
        Numbering depth of the questions.

    ---- Globals read ----
    TYPE_NAMES (pca_fitter constant).

    ---- Outputs ----
    List[str]
        Name of each component: PC1, PC2, ... when the user does not name them. Names
        are not empty, have no commas and are all different.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    text_asker
    yes_no_asker
    """

    names = [f'PC{i + 1}' for i in range(result['components'].shape[1])]
    if not yes_no_asker('Do you want to name the components?', False, depth=depth):
        return names
    seen: Dict[str, int] = {}
    suggestions = []
    for i, kind in enumerate(types):
        if kind in ('a', 'b', 'c'):
            seen[kind] = seen.get(kind, 0) + 1
            number = f' {seen[kind]}' if seen[kind] > 1 else ''
            suggestions.append(f'{kind}-like{number}')
        else:
            suggestions.append(names[i])
    for i, peak in enumerate(result['peaks']):
        while True:
            name = (text_asker(f'What is component {i + 1} ({TYPE_NAMES[types[i]]}, '
                               f'largest peak at {peak:.0f} nm) called?',
                               suggestions[i],
                               depth=depth,
                               ) or '').strip()
            if name and ',' not in name and name not in names[:i]:
                names[i] = name
                break
            info_printer('Use a name that is not empty, has no commas and is not used '
                         'by another component.',
                         depth=depth,
                         )
    return names


# ---- _decomposition_storer -----------------------------------------------------------
def _decomposition_storer(session: ViewerSession, answers: dict, chosen: tuple) -> None:
    """
    ---- Summary ----
    Helper function to keep what the fit questions decided as the fit in use, and show
    it in the settings strip. A run without haems keeps the name of the last fit, so
    the strip still offers it.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its fit is set.
    answers : dict
        Answers dictionary (decompose, fit_file, decomposition_dataset are set).
    chosen : tuple
        (decompose, fit_file, fit, dataset) as decomposition_asker returns it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes ``answers`` and the session, and shows the strip (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _strip_shower
    """

    decompose, name, fit, dataset = chosen
    answers.update({'decompose': decompose, 'decomposition_dataset': dataset})
    if name:
        answers['fit_file'] = name
    session.fit = fit if decompose else None
    _strip_shower(session, answers)


# ---- _empty_limits_builder -----------------------------------------------------------
def _empty_limits_builder(summaries: List[dict]) -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to build limits that trim and ignore nothing, for drawing the data
    before any question is answered.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} with None for the
        trims and 0.0 for the ignores.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {s['name']: {'trim_start': None,
                        'trim_end': None,
                        'ignore_start': 0.0,
                        'ignore_end': 0.0,
                        }
            for s in summaries
            }


# ---- _figure_starter -----------------------------------------------------------------
def _figure_starter(answers: dict,
                    defaults: dict,
                    fit: Optional[dict],
                    is_strip: bool,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to set the figure of each file from the standard settings or the
    ones last saved for the dataset, keeping only what this run allows: the OCR per OD
    and the haems scaled by OD only when OD values were entered, and the haems only
    when they are decomposed, limited to those of the fit in use (all of them when none
    of the saved ones is in it). The journal and size are left as the answers hold
    them, which the settings strip may have changed.

    ---- Inputs ----
    answers : dict
        Answers dictionary the figure settings are stored in; must hold normalise_od
        and decompose.
    defaults : dict
        The standard or saved answers (plot_o2, plot_ocr, ocr_mode, plot_haems, haems,
        haem_mode, haem_per_od, event_label_angle).
    fit : Optional[dict]
        Fit dictionary (haem_list), or None when the haems are not decomposed.
    is_strip : bool
        True in the window, where the Haems box of the settings strip says whether the
        haems are worked out and shown: the figure then has them whenever they are
        decomposed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the figure settings in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    ocr_kind_lister
    """

    kinds = ocr_kind_lister(answers['normalise_od'])
    has_haems = bool(answers['decompose'] and fit is not None)
    haem_list = list(fit['haem_list']) if has_haems else []
    haems = [name for name in defaults['haems'] if name in haem_list]
    answers.update({
        'plot_o2': defaults['plot_o2'],
        'plot_ocr': defaults['plot_ocr'],
        'ocr_mode': (defaults['ocr_mode']
                     if defaults['ocr_mode'] in kinds
                     else kinds[0]
                     ),
        'plot_haems': has_haems and (is_strip or bool(defaults['plot_haems'])),
        'haems': haems or haem_list,
        'haem_mode': defaults['haem_mode'],
        'haem_per_od': bool(defaults['haem_per_od'] and
                            answers['normalise_od'] and
                            defaults['haem_mode'] != 'percent',
                            ),
        'event_label_angle': defaults['event_label_angle'],
        },
                   )


# ---- _file_chooser -------------------------------------------------------------------
def _file_chooser(session: ViewerSession) -> None:
    """
    ---- Summary ----
    Helper function to ask which file to look at and make it the current one.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file is changed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets session.current and reads from and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    """

    options = [(str(number), summary['name'])
               for number, summary in enumerate(session.summaries)
               ]
    chosen = choice_asker('Which file would you like to look at?',
                          options,
                          str(session.current),
                          )
    session.current = int(chosen)


# ---- _fit_file_saver -----------------------------------------------------------------
def _fit_file_saver(fit: dict,
                    fits_folder: Path,
                    count: int,
                    window: Tuple[float, float],
                    depth: int,
                    ) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to ask whether to keep the components found as a fit file in the
    fits folder, so they can be chosen like any other fit in later runs, and to save
    them.

    ---- Inputs ----
    fit : dict
        Fit dictionary from fit_table_builder.
    fits_folder : Path
        Folder holding the fit .csv files.
    count : int
        Number of components (used in the suggested file name).
    window : Tuple[float, float]
        Spectral window used (nm), also used in the suggested file name.
    depth : int
        Numbering depth of the questions.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        Name of the file saved, or None when nothing was saved.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and writes the fit file (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    fit_saver
    info_printer
    text_asker
    yes_no_asker
    """

    if not yes_no_asker('Do you want to save these components as a fit file in the '
                        'fits folder?',
                        True,
                        depth=depth,
                        ):
        return None
    default = f'pca_{count}_components_{window[0]:g}-{window[1]:g}nm'
    while True:
        raw = (text_asker('What should the fit file be called (without .csv)?',
                          default,
                          depth=depth,
                          ) or '').strip()
        stem = re.sub(r'[^A-Za-z0-9 _.\-]', '_', raw)
        stem = stem[:-4] if stem.lower().endswith('.csv') else stem
        stem = stem.strip('. ')
        if not stem:
            info_printer('Please give the file a name.', depth=depth)
            continue
        path = fits_folder / f'{stem}.csv'
        if path.exists() and not yes_no_asker(f'{path.name} already exists. Do you '
                                              f'want to replace it?',
                                              False,
                                              depth=depth,
                                              ):
            continue
        try:
            fits_folder.mkdir(parents=True, exist_ok=True)
            fit_saver(fit, path)
        except OSError as exc:
            info_printer(f'The fit file could not be saved ({exc}).', depth=depth)
            return None
        info_printer(f'Saved {path.name} in the fits folder. It is in the list of fits '
                     f'from now on.',
                     depth=depth,
                     )
        return path.name


# ---- _fit_names_lister ---------------------------------------------------------------
def _fit_names_lister(fits_folder: Path) -> List[str]:
    """
    ---- Summary ----
    Helper function to list the fit files the settings strip offers, in the order the
    fit question lists them.

    ---- Inputs ----
    fits_folder : Path
        Folder holding the fit .csv files.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        File names of the .csv files, sorted without regard to case; empty when the
        folder holds none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return sorted((path.name for path in fits_folder.glob('*.csv')), key=str.lower)


# ---- _limits_lister ------------------------------------------------------------------
def _limits_lister(summaries: List[dict], limits: Dict[str, dict]) -> None:
    """
    ---- Summary ----
    Helper function to print the trim and ignore limits of every file in one list.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    limits : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.

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
    info_printer
    """

    info_printer('Limits (minutes):')
    for summary in summaries:
        v = limits[summary['name']]
        start = 'from 0' if not v['trim_start'] else f"from {v['trim_start']:g}"
        end = ('to the end'
               if v['trim_end'] is None
               else f"to {v['trim_end']:g}"
               )
        info_printer(f"  {summary['name']}: keep {start} {end}; ignore the first "
                     f"{v['ignore_start']:g} and the last {v['ignore_end']:g}",
                     )


# ---- _od_lister ----------------------------------------------------------------------
def _od_lister(details: Dict[str, dict]) -> None:
    """
    ---- Summary ----
    Helper function to print the OD values entered for every file in one list, so they
    can be checked.

    ---- Inputs ----
    details : Dict[str, dict]
        {file name: {OD, volume, dilution_factor, ...}} as od_scaling_asker returns it.

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
    info_printer
    """

    info_printer('OD values:')
    for name, values in details.items():
        info_printer(f"  {name}: OD {values['OD']:g}, volume {values['volume']:g} mL, "
                     f"dilution factor {values['dilution_factor']:g}",
                     )


# ---- _od_table_filler ----------------------------------------------------------------
def _od_table_filler(session: ViewerSession,
                     rows: Dict[str, Dict[str, Optional[float]]],
                     ) -> Dict[str, Dict[str, Optional[float]]]:
    """
    ---- Summary ----
    Helper function to have the OD values filled in in the table of the window: the
    table is shown with the given rows, one question waits for Enter, and it is asked
    again, naming the cells, while a cell is empty or not a number above 0. The table
    is then taken away.

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    rows : Dict[str, Dict[str, Optional[float]]]
        The rows to start from (od_rows, DATA_FORMAT.md); None leaves a cell empty.

    ---- Globals read ----
    COLUMNS (imported constant).

    ---- Outputs ----
    Dict[str, Dict[str, Optional[float]]]
        The rows as filled in, every value a number above 0.

    ---- Globals mutated ----
    None. Shows and hides the table and reads from and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    text_asker
    """

    window = session.window
    window.od_table_shower(rows)
    try:
        while True:
            text_asker(
                'Fill in the table under this text for each file: the OD of the '
                'cells added, the volume of cells (mL) spun down and resuspended '
                'in 5 mL, and the dilution factor if the cells were diluted mid '
                'run. Then press Enter here.',
                )
            filled, wrong = window.od_table_reader()
            empty = [f'{name}: {heading}'
                     for name, values in filled.items()
                     for key, heading in COLUMNS
                     if values.get(key) is None and f'{name}: {heading}' not in wrong
                     ]
            if not (wrong or empty):
                return filled
            if wrong:
                info_printer('These cells need a number above 0: '
                             + ', '.join(wrong) + '.',
                             depth=2,
                             )
            if empty:
                info_printer('These cells are empty: ' + ', '.join(empty) + '.',
                             depth=2,
                             )
    finally:
        window.od_table_hider()


# ---- _pca_pictures_publisher ---------------------------------------------------------
def _pca_pictures_publisher(session: ViewerSession,
                            analysis: dict,
                            result: dict,
                            examples: Optional[dict],
                            names: List[str],
                            types: List[str],
                            depth: int,
                            ) -> None:
    """
    ---- Summary ----
    Helper function to put the two PCA pictures in the plot window: the examples of
    how the spectra are decomposed (listed only) and the components (shown). The
    "Drawing ..." sign is on the plot while they are made.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    analysis : dict
        Result of component_finder.
    result : dict
        Result of component_builder.
    examples : Optional[dict]
        Result of decomposition_example_finder; None leaves the examples out.
    names : List[str]
        Name of each component.
    types : List[str]
        Haem type of each component (component_classifier).
    depth : int
        Numbering depth of the messages.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. A picture that cannot be drawn is reported, never raised.

    ---- Globals mutated ----
    None. Draws in the plot window (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    pca_example_picture_builder
    pca_picture_builder
    """

    session.window.drawing_sign_shower()
    try:
        if examples is not None:
            session.window.extra_publisher(PCA_EXAMPLES_TITLE,
                                           pca_example_picture_builder(examples,
                                                                       names,
                                                                       types,
                                                                       ),
                                           is_shown=False,
                                           )
        session.window.extra_publisher(PCA_COMPONENTS_TITLE,
                                       pca_picture_builder(analysis,
                                                           result,
                                                           names,
                                                           types,
                                                           ),
                                       )
    except Exception as exc:  # a drawing problem must never stop the questions
        info_printer(f'The PCA pictures could not be drawn ({exc}).', depth=depth)


# ---- _review_asker -------------------------------------------------------------------
def _review_asker(session: ViewerSession,
                  question: str,
                  change_label: str,
                  redraw: Callable[[], bool],
                  ) -> bool:
    """
    ---- Summary ----
    Helper function to ask whether the user accepts what the plot window shows, with
    the two answers yes and no (see _choice_reviewer).

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file may be changed.
    question : str
        The accept question, for example 'Do you accept these limits?'.
    change_label : str
        Label of the answer that asks the questions of the step again.
    redraw : Callable[[], bool]
        Function that draws the preview of the current file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when accepted, False when the user wants to answer the step again.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and redraws the window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _choice_reviewer
    """

    options = [('yes', 'Yes, accept'),
               ('no', change_label),
               ]
    return _choice_reviewer(session, question, options, redraw) == 'yes'


# ---- _skipped_lister -----------------------------------------------------------------
def _skipped_lister(session: ViewerSession,
                    answers: dict,
                    limits: Dict[str, dict],
                    details: Dict[str, dict],
                    ) -> None:
    """
    ---- Summary ----
    Helper function to tell the user, in red, which averaging windows were skipped in
    which files because there is not enough time for them, so they can be checked before
    the averaging is accepted. Prints nothing when every window fits.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers so far, with the averaging window and gap.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    WARNING_COLOUR (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads the files and prints to the terminal (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    info_printer
    skipped_windows_finder
    text_colourer
    """

    info_printer('Checking that the averaging windows fit in every file ...')
    skipped = skipped_windows_finder(session,
                                     _answers_previewer(answers, None, 'analysis'),
                                     limits,
                                     details,
                                     )
    if not skipped:
        return
    info_printer(text_colourer('WARNING: averaging was skipped for these windows '
                               '(not enough time). They are shown in red with a '
                               'warning sign in the plot. Please check this is OK:',
                               WARNING_COLOUR,
                               ),
                 )
    for name, windows in skipped.items():
        info_printer(f"  {name}: {', '.join(windows)}")


# ---- _standard_fit_loader ------------------------------------------------------------
def _standard_fit_loader(summaries: List[dict],
                         defaults: dict,
                         fits_folder: Path,
                         is_from_strip: bool = False,
                         ) -> Tuple[Optional[dict], Optional[str]]:
    """
    ---- Summary ----
    Helper function to load the fit the standard plot shows the haems with, before any
    question about the haems is asked: the fit last saved for the dataset, or the
    standard fit for a dataset never saved. It also loads a fit picked in the settings
    strip. When the haems cannot be shown, one line says why and the plot keeps to the
    oxygen and the OCR.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md); the spectrometers in common are used.
    defaults : dict
        Default answers (decompose, fit_file, decomposition_dataset).
    fits_folder : Path
        Folder holding the fit .csv files.
    is_from_strip : bool
        True when the fit was picked in the settings strip: the message then says the
        strip is set back, instead of pointing to the processing.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Optional[dict], Optional[str]]
        (fit, spectrometer the haems are read from), or (None, None) when the haems
        are not shown: the dataset was saved without haems, the fit file is missing or
        unreadable, or the files share no spectrometer the fit can be used on.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    fit_importer
    info_printer
    """

    # ---- 1 Find the fit file ---------------------------------------------------------
    if not defaults['decompose']:  # the dataset was saved without haems
        return None, None
    lead = ('The haems cannot be worked out'
            if is_from_strip
            else 'The haems are not shown yet'
            )
    def advice(text: str) -> str:
        return 'The strip is set back to what is in use.' if is_from_strip else text
    name = defaults.get('fit_file')
    if not name or not (fits_folder / name).is_file():
        info_printer(f'{lead}: the fit file {name} is not in {fits_folder}. '
                     f"{advice('You can choose a fit in the processing.')}",
                     )
        return None, None

    # ---- 2 Find the spectrometer every file has --------------------------------------
    common = set(summaries[0]['datasets'])
    for summary in summaries[1:]:
        common &= set(summary['datasets'])
    dataset = defaults['decomposition_dataset']
    if dataset not in common:
        if len(common) != 1:
            info_printer(f'{lead}: the files do not all have the {dataset} '
                         'spectrometer. '
                         f"{advice('You can choose one in the processing.')}",
                         )
            return None, None
        dataset = next(iter(common))

    # ---- 3 Read the fit --------------------------------------------------------------
    try:
        return fit_importer(fits_folder / name), dataset
    except (OSError, ValueError) as exc:
        info_printer(f'{lead}: the fit file {name} could not be read ({exc}). '
                     f"{advice('You can choose another fit in the processing.')}",
                     )
        return None, None


# ---- _strip_change_applier -----------------------------------------------------------
def _strip_change_applier(session: ViewerSession,
                          answers: dict,
                          fits_folder: Path,
                          changes: Dict[str, object],
                          ) -> None:
    """
    ---- Summary ----
    Helper function to make a change in the settings strip what the run uses, and
    redraw the plot of the step being asked. Unticking the haems leaves them out of the
    run; ticking them, or picking a fit, works them out with the fit in the strip. A
    fit that cannot be used is reported and the strip is set back. A new journal, width
    or height redraws only the figure of each file, the one plot drawn at its size.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its fit is changed and its redraw called.
    answers : dict
        Answers dictionary the values are stored in.
    fits_folder : Path
        Folder holding the fit .csv files.
    changes : Dict[str, object]
        {name: new value} of the strip values that changed (DATA_FORMAT.md,
        strip_values).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes ``answers`` and the session, prints to the terminal, shows the strip
    and redraws the plot (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _standard_fit_loader
    _strip_shower
    info_printer
    size_answers_builder
    """

    # ---- 1 The journal, the width and the height -------------------------------------
    sizes = size_answers_builder(changes)
    answers.update(sizes)
    is_redrawn = bool(sizes) and session.is_figure

    # ---- 2 The haems and the fit -----------------------------------------------------
    if changes.get('plot_haems') is False:
        answers.update({'decompose': False, 'plot_haems': False})
        session.fit = None
        info_printer('The haems are left out of the run.')
        is_redrawn = True
    elif 'fit_file' in changes or changes.get('plot_haems'):
        name = changes.get('fit_file') or answers['fit_file']
        fit, dataset = _standard_fit_loader(session.summaries,
                                            dict(answers,
                                                 decompose=True,
                                                 fit_file=name,
                                                 ),
                                            fits_folder,
                                            is_from_strip=True,
                                            )
        if fit is not None:
            haems = [haem for haem in answers['haems'] if haem in fit['haem_list']]
            answers.update({'decompose': True,
                            'plot_haems': True,
                            'fit_file': name,
                            'decomposition_dataset': dataset,
                            'haems': haems or list(fit['haem_list']),
                            },
                           )
            session.fit = fit
            info_printer(f'The haems are worked out with {name}.')
            is_redrawn = True

    # ---- 3 Show what is in use and redraw --------------------------------------------
    _strip_shower(session, answers)
    if is_redrawn and session.redraw is not None:
        session.redraw()


# ---- _strip_shower -------------------------------------------------------------------
def _strip_shower(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Helper function to show in the settings strip what the run uses now: the haems
    ticked when they are worked out, the fit, the journal and the size. Without a
    window it does nothing.

    ---- Inputs ----
    session : ViewerSession
        The browser session (its window and fit).
    answers : dict
        Answers so far.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Shows the values in the strip (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    strip_values_builder
    """

    session.window.strip_setter(strip_values_builder(answers, session.fit is not None))


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- browser_stage_runner ------------------------------------------------------------
def browser_stage_runner(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Main function to show the standard plot of the files in the plot window (the set
    and measured O2, the OCR and, when the session has a fit, the haems, with the
    events as written in the file) before any question is asked about them. In the
    browser window the user can look through them while answering, so the questions
    carry straight on; with the picture fallback a small menu steps through the files.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file is changed and its redraw set.
    answers : dict
        Answers so far, used for the figure style of the preview.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and draws the plot window (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _file_chooser
    choice_asker
    info_printer
    preview_drawer
    """

    total = len(session.summaries)
    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, session.fit, 'standard'),
                              {},
                              session.fit,
                              {},
                              show_ignored=False,
                              )
    session.redraw = redraw
    if session.window.is_interactive:
        redraw()
        return
    options = [('next', 'Next file'),
               ('previous', 'Previous file'),
               ('goto', 'Go to a specific file'),
               ('continue', 'Continue to trimming and ignoring'),
               ]
    while True:
        summary = session.summaries[session.current]
        redraw()
        info_printer(f'\nCurrent file: {session.current + 1} of {total}')
        info_printer(f"Filename: {summary['name']} ({summary['duration_min']:.1f} "
                     f"min, {len(summary['events'])} event(s))",
                     )
        choice = choice_asker('What would you like to do?', options, 'continue')
        if choice == 'continue':
            return
        if choice == 'goto':
            _file_chooser(session)
        elif choice == 'next' and session.current + 1 < total:
            session.current += 1
        elif choice == 'previous' and session.current > 0:
            session.current -= 1
        else:
            info_printer('There is no file in that direction.')


# ---- details_stage_runner ------------------------------------------------------------
def details_stage_runner(session: ViewerSession,
                         answers: dict,
                         defaults: dict,
                         limits: Dict[str, dict],
                         details_before: Optional[Dict[str, dict]] = None,
                         ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the last questions of the import, on the standard plot cut to
    the limits: the OD values (in the table of the window, or with questions per file
    and an accept question), then the event labels. The OD values are only checked:
    the data is scaled by OD in the individual plots. The plot is redrawn with the
    labels once they are entered. The haems are those of the session's fit.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its redraw is set.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file (trim_asker).
    details_before : Optional[Dict[str, dict]]
        OD values and events from an earlier pass, offered as defaults when the step is
        asked again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'OD', 'volume', 'dilution_factor', 'events'}}; the OD entries are
        only present when scaling by OD.

    ---- Globals mutated ----
    None. Stores normalise_od in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _od_lister
    _od_table_filler
    _review_asker
    event_asker
    od_scaling_asker
    preview_drawer
    saved_values_reader
    """

    # ---- 1 Read the values of earlier runs -------------------------------------------
    summaries = session.summaries
    details: Dict[str, dict] = {s['name']: {} for s in summaries}
    saved = saved_values_reader(summaries, session.export_root)
    for name, values in (details_before or {}).items():
        saved[name] = dict(saved.get(name) or {}, **values)
    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, session.fit, 'standard'),
                              limits,
                              session.fit,
                              details,
                              )
    session.redraw = redraw

    # ---- 2 OD values -----------------------------------------------------------------
    # Only checked here; the data is scaled by OD in the individual plots. In the window
    # they are filled in in a table, which is its own check.
    is_table = session.window.is_interactive
    def table_filler(rows: Dict[str, dict]) -> Dict[str, dict]:
        return _od_table_filler(session, rows)
    while True:
        details = od_scaling_asker(summaries,
                                   answers,
                                   defaults,
                                   saved,
                                   table_filler=table_filler if is_table else None,
                                   )
        if not answers['normalise_od']:
            break
        _od_lister(details)
        if is_table or _review_asker(session,
                         'Do you accept these OD values?',
                         'No, enter the OD values again',
                         lambda: True,
                         ):
            break
        defaults = dict(defaults, normalise_od=True)
        for name, values in details.items():
            saved[name] = dict(saved.get(name) or {}, **values)

    # ---- 3 Event labels --------------------------------------------------------------
    is_again = False
    while True:
        for name, events in event_asker(summaries, saved, is_again).items():
            details[name]['events'] = events
            saved[name] = dict(saved.get(name) or {}, events=events)
        redraw()
        if _review_asker(session,
                         'Do you accept these event labels?',
                         'No, change the labels again',
                         redraw,
                         ):
            break
        is_again = True
    return details


# ---- pca_stage_runner ----------------------------------------------------------------
def pca_stage_runner(session: ViewerSession,
                     answers: dict,
                     defaults: dict,
                     limits: Dict[str, dict],
                     fits_folder: Path,
                     dataset: str,
                     depth: int = 2,
                     ) -> Tuple[Optional[str], Optional[dict]]:
    """
    ---- Summary ----
    Main function to find the components of the haem spectra from the data itself with
    a principal component analysis, instead of using a fit file. The user chooses the
    spectral window and the number of components, sees each component in its own
    panel and the best and worst described spectrum in the plot window, and can save
    the components as a fit file in the fits folder.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary; the choices are stored in it (pca_start, pca_end,
        pca_rotate, pca_count, pca_smoothing_nm).
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file (trim_asker).
    fits_folder : Path
        Folder holding the fit .csv files.
    dataset : str
        Spectral dataset holding the haem spectra.
    depth : int
        Numbering depth of the questions.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Optional[str], Optional[dict]]
        (fit file name, fit dictionary as fit_importer gives). (None, None) when the
        user prefers to choose a fit file instead. The name is a description when the
        fit was not saved.

    ---- Globals mutated ----
    None. Reads the files, reads from and prints to the terminal, draws the plot window
    and may write a fit file (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _component_namer
    _fit_file_saver
    _pca_pictures_publisher
    choice_asker
    component_builder
    component_classifier
    component_count_suggester
    component_finder
    decomposition_example_finder
    fit_table_builder
    info_printer
    number_asker
    pca_spectra_gatherer
    progress_clearer
    progress_printer
    text_colourer
    yes_no_asker
    """

    info_printer('This finds the components from your own data instead of using a fit '
                 'file. All the spectra of all the files (after trimming, without the '
                 'ignored parts) are analysed together, so choose a spectral window '
                 'where the haems you are interested in absorb. The components are '
                 'abstract shapes that explain the changes in the spectra; where '
                 'haem spectra overlap strongly they may be mixtures of haems rather '
                 'than single ones.',
                 depth=depth,
                 )
    start = float(defaults.get('pca_start') or 500.0)
    end = float(defaults.get('pca_end') or 630.0)
    rotate = bool(defaults.get('pca_rotate', True))
    count = int(defaults.get('pca_count') or 0)
    smoothing = float(defaults.get('pca_smoothing_nm', DEFAULT_SMOOTHING_NM))
    while True:
        # ---- 1 Choose the window and read the spectra --------------------------------
        start = number_asker('Where should the spectral window start (nm)?',
                             start,
                             minimum=0,
                             depth=depth,
                             )
        end = number_asker('Where should the spectral window end (nm)?',
                           max(end, start + 20.0),
                           minimum=start,
                           exclusive_minimum=True,
                           depth=depth,
                           )
        sets, problems = pca_spectra_gatherer(
            session,
            dataset,
            limits,
            (start, end),
            lambda n, total: progress_printer(f'Reading the spectra: file {n} of '
                                              f'{total} ...',
                                              ),
        )
        progress_clearer()
        for problem in problems:
            info_printer(text_colourer(f'Not used: {problem}', WARNING_COLOUR),
                         depth=depth,
                         )
        try:
            analysis = component_finder(sets,
                                        (start, end),
                                        degree_of_scatter=settings.DEGREE_OF_SCATTER,
                                        )
        except ValueError as exc:
            info_printer(text_colourer(f'The analysis could not be run: {exc}',
                                       WARNING_COLOUR,
                                       ),
                         depth=depth,
                         )
            continue
        suggestion = component_count_suggester(analysis)
        available = len(analysis['eigenvalues'])
        info_printer(f"Read {analysis['n_spectra']} spectra from "
                     f"{len(analysis['counts'])} files between "
                     f"{analysis['window'][0]:g} and {analysis['window'][1]:g} nm.",
                     depth=depth,
                     )

        # ---- 2 Find the components ---------------------------------------------------
        count = min(count or suggestion, available)
        while True:
            # ---- 2.1 Ask how many and whether to rotate ------------------------------
            while True:
                value = number_asker(f'How many components should be found? (The data '
                                     f'suggest {suggestion}; use as few as describe '
                                     f'the data, extra ones only fit noise.)',
                                     count,
                                     minimum=1,
                                     maximum=available,
                                     depth=depth,
                                     )
                if value == int(value):
                    count = int(value)
                    break
                info_printer('Please enter a whole number.', depth=depth)
            rotate = yes_no_asker('Do you want to rotate the components so each is as '
                                  'peak-like as possible (varimax)?',
                                  rotate,
                                  depth=depth,
                                  )
            smoothing = number_asker('Over how many nm should the components be '
                                     'smoothed to remove their noise (0 for none)?',
                                     smoothing,
                                     minimum=0,
                                     maximum=(end - start) / 4,
                                     depth=depth,
                                     )

            # ---- 2.2 Build, describe and draw them -----------------------------------
            result = component_builder(analysis, count, rotate, smoothing)
            types = component_classifier(result['wavelengths'], result['components'])
            names = [f'PC{i + 1}' for i in range(count)]
            try:
                examples = decomposition_example_finder(sets,
                                                        result,
                                                        settings.DEGREE_OF_SCATTER,
                                                        )
            except ValueError as exc:
                examples = None
                info_printer(f'No example decomposition could be made ({exc}).',
                             depth=depth,
                             )
            _pca_pictures_publisher(session,
                                    analysis,
                                    result,
                                    examples,
                                    names,
                                    types,
                                    depth,
                                    )
            for i, kind in enumerate(types):
                info_printer(f"PC{i + 1}: {TYPE_NAMES[kind]}, largest peak "
                             f"{result['peaks'][i]:.0f} nm, "
                             f"{result['explained'][i] * 100:.1f}% of the change.",
                             depth=depth,
                             )
            if examples is not None:
                info_printer(f"Residual RMS: {examples['median_rms']:.2g} OD for a "
                             f"typical spectrum, from {examples['best']['rms']:.2g} "
                             f"to {examples['worst']['rms']:.2g} OD. The '"
                             f"{PCA_EXAMPLES_TITLE}' picture shows the two extremes.",
                             depth=depth,
                             )

            # ---- 2.3 Accept or change them -------------------------------------------
            choice = choice_asker('Do you accept these components?',
                                  [('yes', 'Yes, accept'),
                                   ('count', 'No, change the number of components'),
                                   ('window', 'No, change the spectral window'),
                                   ('fit', 'No, choose a fit file instead'),
                                   ],
                                  'yes',
                                  depth=depth,
                                  )
            if choice != 'count':
                break
        if choice == 'fit':
            return None, None
        if choice == 'yes':
            break

    # ---- 3 Name and save the components ----------------------------------------------
    names = _component_namer(result, types, depth)
    if names != [f'PC{i + 1}' for i in range(count)]:
        _pca_pictures_publisher(session,
                                analysis,
                                result,
                                examples,
                                names,
                                types,
                                depth,
                                )
    fit = fit_table_builder(result, names)
    saved = _fit_file_saver(fit, fits_folder, count, analysis['window'], depth)
    answers.update({'pca_start': start,
                    'pca_end': end,
                    'pca_rotate': rotate,
                    'pca_count': count,
                    'pca_smoothing_nm': smoothing,
                    },
                   )
    return (saved or f'PCA, {count} components, {start:g}-{end:g} nm (not saved)'), fit


# ---- plots_stage_runner --------------------------------------------------------------
def plots_stage_runner(session: ViewerSession,
                       answers: dict,
                       defaults: dict,
                       limits: Dict[str, dict],
                       details: Dict[str, dict],
                       ) -> bool:
    """
    ---- Summary ----
    Main function to show the figure saved for each file, drawn as it will be saved
    from the standard settings or the ones last saved for the dataset, and ask whether
    it is accepted. Each 'No' answer names one part (the oxygen and OCR, which haems,
    how the haems are shown, the angle of the event labels, the journal and size): only
    that part's questions are asked, with the current choices as the defaults, and the
    figure is drawn and asked about again. In the window the settings strip turns the
    haems on or off and sets the journal and size, so 'which haems' asks only which
    ones in which order, and the journal and size are not asked.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its fit is the one in use, and its redraw is set.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when at least one panel is plotted.

    ---- Globals mutated ----
    None. Stores the answers in ``answers``, and the redraw in the session (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _choice_reviewer
    _figure_starter
    _strip_shower
    haem_choice_asker
    haem_form_asker
    haem_scaling_asker
    info_printer
    label_angle_asker
    preview_drawer
    signal_asker
    size_asker
    """

    # ---- 1 Start from the standard or saved settings ---------------------------------
    info_printer('The figure saved for each file is drawn with the standard settings, '
                 'or with the ones last saved for this dataset. Change only what you '
                 'want different; you can look at every file before accepting it.',
                 )
    is_strip = session.window.is_interactive
    _figure_starter(answers, defaults, session.fit, is_strip)
    _strip_shower(session, answers)
    def is_plotted() -> bool:
        return bool(answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems'])
    def redraw() -> bool:
        if not is_plotted():
            return False  # a figure with no panel cannot be drawn
        return preview_drawer(session,
                              _answers_previewer(answers, session.fit, 'final'),
                              limits,
                              session.fit,
                              details,
                              show_ignored=False,
                              )
    session.redraw, session.is_figure = redraw, True

    # ---- 2 Change one part at a time until the figure is accepted --------------------
    while True:
        # ---- 2.1 Draw the figure -----------------------------------------------------
        plotted = is_plotted()
        redraw()
        if not plotted:
            info_printer('Nothing is set to be plotted, so no individual figures will '
                         'be made.',
                         )

        # ---- 2.2 Ask whether it is accepted, or which part to change -----------------
        # In the window the Haems box turns the haems on and off, and the strip holds
        # the journal and size.
        has_haems = bool(answers['decompose'] and session.fit is not None)
        options = [('yes', 'Yes, accept'),
                   ('signals', 'No, change the oxygen and OCR'),
                   ]
        if answers['plot_haems'] if is_strip else has_haems:
            options.append(('haems', 'No, change which haems are shown'))
        if answers['plot_haems']:
            options.append(('form', 'No, change how the haems are shown'))
        if plotted:
            options.append(('angle', 'No, change the angle of the event labels'))
        if not is_strip:
            options.append(('size', 'No, change the journal or size'))
        choice = _choice_reviewer(session,
                                  'Do you accept this figure?',
                                  options,
                                  redraw,
                                  )
        if choice == 'yes':
            return is_plotted()

        # ---- 2.3 Ask that part's questions -------------------------------------------
        current = dict(answers)
        if choice == 'signals':
            signal_asker(answers, current)
        elif choice == 'haems':
            haem_choice_asker(answers,
                              current,
                              session.fit,
                              is_shown_asked=not is_strip,
                              )
        elif choice == 'form':
            haem_form_asker(answers, current)
            haem_scaling_asker(answers, current)
        elif choice == 'angle':
            label_angle_asker(answers, current)
        else:
            size_asker(answers,
                       current,
                       {'journal': 'journal',
                        'columns': 'columns',
                        'height': 'height',
                        'mode': 'size_mode',
                        },
                       (1, 0.5),
                       )


# ---- processing_stage_runner ---------------------------------------------------------
def processing_stage_runner(session: ViewerSession,
                            answers: dict,
                            defaults: dict,
                            limits: Dict[str, dict],
                            fits_folder: Path,
                            details: Dict[str, dict],
                            trim_runner: Callable[[], Dict[str, dict]],
                            ) -> None:
    """
    ---- Summary ----
    Main function to talk the user through the processing, with the plot redrawn after
    each answer: first the haem fit (the fit already shown is accepted, another is
    tried, or the haems are left out), then, now that the haems are seen, an offer to
    change the trim and ignore times, and last the averaging around the events. In the
    window the settings strip picks the fit and leaves the haems out, so the
    decomposition question only offers to find the components from the data instead.
    While those questions are asked the strip is greyed out.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its fit is the fit shown so far (None when the plot shows
        no haems), and is set to the fit chosen. Its redraw is set.
    answers : dict
        Answers dictionary the values are stored in; fit_file and
        decomposition_dataset name the fit shown.
    defaults : dict
        Default answers offered by the questions; whether to decompose and which fit
        follow the answers so far (the strip may have changed them).
    limits : Dict[str, dict]
        Trim and ignore limits of every file (trim_asker).
    fits_folder : Path
        Folder holding the fit .csv files.
    details : Dict[str, dict]
        OD values and events of every file (details_stage_runner); the averaging
        windows are drawn around the events not ignored there.
    trim_runner : Callable[[], Dict[str, dict]]
        Function that asks the trim and ignore questions again with the haems of the
        session's fit on the plot, and returns the new limits.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. The fit is in session.fit (None when the haems are not decomposed).

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` and the fit in the session, reads from and
    prints to the terminal and redraws the window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _averaging_reviewer
    _choice_reviewer
    _decomposition_storer
    _fit_names_lister
    _strip_shower
    decomposition_asker
    info_printer
    pca_stage_runner
    preview_drawer
    yes_no_asker
    """

    summaries = session.summaries
    is_strip = session.window.is_interactive
    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, session.fit, 'analysis'),
                              limits,
                              session.fit,
                              details,
                              )
    session.redraw = redraw
    def pca_finder(dataset: str, depth: int) -> Tuple[Optional[str], Optional[dict]]:
        session.window.strip_state_setter(False)
        try:
            return pca_stage_runner(session,
                                    answers,
                                    defaults,
                                    limits,
                                    fits_folder,
                                    dataset,
                                    depth,
                                    )
        finally:
            session.window.strip_fits_setter(_fit_names_lister(fits_folder))
            session.window.strip_state_setter(True)

    # ---- 1 The haem fit --------------------------------------------------------------
    # ---- 1.1 Ask whether to decompose, when no haems are shown yet -------------------
    if session.fit is None:
        # the Haems box and the fit of the strip are the defaults
        asked = dict(defaults,
                     decompose=answers['decompose'],
                     fit_file=answers['fit_file'],
                     decomposition_dataset=answers['decomposition_dataset'],
                     )
        _decomposition_storer(session,
                              answers,
                              decomposition_asker(summaries,
                                                  asked,
                                                  fits_folder,
                                                  pca_runner=pca_finder,
                                                  ),
                              )
    else:
        answers['decompose'] = True
        info_printer(f"The haems are worked out with {answers['fit_file']}.")

    # ---- 1.2 Accept the fit, try another or leave the haems out ----------------------
    # In the window the strip picks the fit and leaves the haems out.
    if is_strip:
        options = [('yes', 'Yes, accept'),
                   ('pca', 'No, find the components from the data'),
                   ]
    else:
        options = [('yes', 'Yes, accept'),
                   ('fit', 'No, try another fit'),
                   ('none', 'No, do not decompose the haems'),
                   ]
    while answers['decompose']:
        redraw()
        choice = _choice_reviewer(session,
                                  'Do you accept this decomposition?',
                                  options,
                                  redraw,
                                  )
        if choice == 'yes':
            break
        if choice == 'none':
            answers['decompose'] = False
            break
        if choice == 'pca':
            name, fit = pca_finder(answers['decomposition_dataset'], 2)
            if fit is not None:
                answers.update({'decompose': True, 'fit_file': name})
                session.fit = fit
                _strip_shower(session, answers)
            continue
        _decomposition_storer(session,
                              answers,
                              decomposition_asker(summaries,
                                                  dict(defaults,
                                                       fit_file=answers['fit_file'],
                                                       decomposition_dataset=answers[
                                                           'decomposition_dataset'],
                                                       ),
                                                  fits_folder,
                                                  forced=True,
                                                  depth=2,
                                                  pca_runner=pca_finder,
                                                  ),
                              )
    if not answers['decompose']:
        session.fit = None
        _strip_shower(session, answers)

    # ---- 2 Offer to change the trim and ignore times ---------------------------------
    if (answers['decompose'] and
        yes_no_asker('Do you want to change the trim and ignore times now that the '
                     'haems are shown?',
                     False,
                     )
        ):
        limits = trim_runner()
        session.redraw = redraw
        redraw()

    # ---- 3 Averaging around the events -----------------------------------------------
    _averaging_reviewer(session, answers, defaults, limits, details, redraw)


# ---- trim_stage_runner ---------------------------------------------------------------
def trim_stage_runner(session: ViewerSession,
                      answers: dict,
                      remembered: Dict[str, dict],
                      ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the trim and ignore questions on the standard plot, adding the
    shaded trimmed and ignored parts to the plot window after every answer, and ask
    whether to accept them. When the limits are asked again, the earlier ones stay on
    the plot as dashed lines. After they are accepted, it offers to export all the data
    cut to them. The haems are those of the session's fit (none when it has none).

    ---- Inputs ----
    session : ViewerSession
        The browser session; its redraw is set.
    answers : dict
        Answers so far, used for the figure style of the preview.
    remembered : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} offered as the
        defaults (from the last run, or from the previous attempt).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        The limits of every file, exactly as trim_asker returns them.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and draws the plot window (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _all_data_asker
    _answers_previewer
    _empty_limits_builder
    _limits_lister
    _review_asker
    preview_drawer
    trim_asker
    """

    previous: Dict[str, dict] = {}
    shown = {'limits': _empty_limits_builder(session.summaries)}
    def draw(limits: Dict[str, dict]) -> bool:
        shown['limits'] = limits  # what a change in the strip redraws
        return preview_drawer(session,
                              _answers_previewer(answers, session.fit, 'standard'),
                              limits,
                              session.fit,
                              {},
                              show_trim=True,
                              previous_limits=previous,
                              )
    session.redraw = lambda: draw(shown['limits'])
    while True:
        draw(_empty_limits_builder(session.summaries))
        limits = trim_asker(session.summaries, remembered, draw)
        _limits_lister(session.summaries, limits)
        draw(limits)
        if _review_asker(session,
                         'Do you accept these limits?',
                         'No, enter the limits again',
                         lambda: draw(limits),
                         ):
            _all_data_asker(session, limits)
            return limits
        remembered = dict(remembered, **limits)
        previous.clear()
        previous.update(limits)


# ---- viewer_asker --------------------------------------------------------------------
def viewer_asker(summaries: List[dict],
                 answers: dict,
                 defaults: dict,
                 remembered: Dict[str, dict],
                 fits_folder: Path,
                 export_root: Path,
                 ) -> Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool]:
    """
    ---- Summary ----
    Main function to ask the questions of the experiment browser: the file browser,
    trimming and ignoring, the OD values and the event labels (which end the import),
    the processing (the haem fit, the trim and ignore times again if wanted, the
    averaging) and the individual figures. The standard plot of every file (oxygen, OCR
    and the haems of the dataset's fit) is shown first, with no question asked. The
    plot window is redrawn after each answer, and at the end any step can be gone back
    to. In the window the settings strip can be changed while these questions wait
    (except those of the components found from the data); it is greyed out afterwards.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    remembered : Dict[str, dict]
        {file name: limits} from the last run.
    fits_folder : Path
        Folder holding the fit .csv files.
    export_root : Path
        Results folder.

    ---- Globals read ----
    PREVIEW_FILE, STAGE_TITLES (module constants); settings.STANDARD_FIT.

    ---- Outputs ----
    Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool]
        (limits, fit, details, plotted) as the same questions return them when they are
        asked without the browser.

    ---- Globals mutated ----
    None. Stores the answers in ``answers``, reads from and prints to the terminal,
    draws and closes the plot window and sets up the settings strip (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_names_lister
    _standard_fit_loader
    _strip_change_applier
    _strip_shower
    active_gui_getter
    browser_stage_runner
    choice_asker
    details_stage_runner
    file_focus_setter
    heading_printer
    info_printer
    numbering_getter
    numbering_setter
    plots_stage_runner
    processing_stage_runner
    section_starter
    trim_stage_runner
    """

    window = active_gui_getter() or PictureWindow(PREVIEW_FILE)
    session = ViewerSession(summaries, export_root, window)
    window.session_attacher(session)
    names = [s['name'] for s in summaries]
    def focus(name: str) -> None:
        session.current = names.index(name)
        window.file_focuser(name)
    file_focus_setter(focus)
    state: dict = {}

    # ---- 1 Load the fit of the standard plot -----------------------------------------
    # A dataset saved without haems has no fit name; the strip then offers the standard
    # fit.
    answers['fit_file'] = answers.get('fit_file') or settings.STANDARD_FIT
    session.fit, dataset = _standard_fit_loader(summaries, answers, fits_folder)
    if session.fit is not None:
        answers['decomposition_dataset'] = dataset

    # ---- 2 Set up the settings strip (the window only) -------------------------------
    window.strip_fits_setter(_fit_names_lister(fits_folder))
    _strip_shower(session, answers)
    window.strip_listener_setter(lambda changes: _strip_change_applier(session,
                                                                       answers,
                                                                       fits_folder,
                                                                       changes,
                                                                       ),
                                 )
    window.strip_state_setter(True)

    # ---- run_browser -----------------------------------------------------------------
    def run_browser() -> None:
        browser_stage_runner(session, answers)
    def run_trim() -> Dict[str, dict]:
        old = state.get('limits') or remembered
        state['limits'] = trim_stage_runner(session, answers, old)
        answers['ignore_first_minutes'] = max(v['ignore_start']
                                              for v in state['limits'].values()
                                              )
        answers['ignore_last_minutes'] = max(v['ignore_end']
                                             for v in state['limits'].values()
                                             )
        return state['limits']
    def run_details() -> None:
        old_defaults = dict(answers) if state.get('details') else defaults
        state['details'] = details_stage_runner(session,
                                                answers,
                                                old_defaults,
                                                state['limits'],
                                                state.get('details'),
                                                )
    def run_processing() -> None:
        old_defaults = dict(answers) if state.get('fit_asked') else defaults
        processing_stage_runner(session,
                                answers,
                                old_defaults,
                                state['limits'],
                                fits_folder,
                                state['details'],
                                run_trim,
                                )
        state['fit_asked'] = True
    def run_plots() -> None:
        old_defaults = dict(answers) if state.get('plots_asked') else defaults
        plots_stage_runner(session,
                           answers,
                           old_defaults,
                           state['limits'],
                           state['details'],
                           )
        state['plots_asked'] = True
    steps = [('browser', run_browser),
             ('trim', run_trim),
             ('details', run_details),
             ('processing', run_processing),
             ('plots', run_plots),
             ]

    # ---- 3 Ask every step once -------------------------------------------------------
    # Only the figure of each file is drawn at its size, so only there does a new
    # journal or size in the strip redraw the plot (the plots step sets it again).
    try:
        for key, runner in steps:
            session.is_figure = False
            if key == 'browser' and window.is_interactive:
                runner()  # the window needs no section of its own
                continue
            section_starter(STAGE_TITLES[key])
            runner()
        last_section, last_question = numbering_getter(0), numbering_getter(1)

        # ---- 4 Go back to any step ---------------------------------------------------
        visible = [key for key, _ in steps
                   if not (key == 'browser' and window.is_interactive)
                   ]
        options = [('done', 'No, continue')]
        options += [(key, STAGE_TITLES[key]) for key in visible]
        while True:
            numbering_setter(0, last_section)
            numbering_setter(1, last_question)
            chosen = choice_asker('Do you want to go back to any of these steps?',
                                  options,
                                  'done',
                                  )
            if chosen == 'done':
                break
            index = [key for key, _ in steps].index(chosen)
            number = visible.index(chosen) + 2
            numbering_setter(0, number)
            heading_printer(f'{number}. {STAGE_TITLES[chosen]} (again)')
            session.is_figure = False
            steps[index][1]()
            if index < len(steps) - 1:
                later = ', '.join(STAGE_TITLES[k] for k, _ in steps[index + 1:])
                info_printer(f'Your answers to the later steps ({later}) were kept. '
                             f'Go back to them if this change affects them.',
                             )
    finally:
        file_focus_setter(None)
        window.strip_listener_setter(None)
        window.strip_state_setter(False)
        session.redraw = None
        session.window.window_closer()

    # ---- 5 Return the answers --------------------------------------------------------
    # Read now: the strip may have changed the haems after the figure was accepted.
    plotted = bool(answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems'])
    return state['limits'], session.fit, state['details'], plotted
