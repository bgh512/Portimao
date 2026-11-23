"""
The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import copy
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.averaging import (quick_span_lister,
                                    window_layout_finder,
                                    window_pointer_reader,
                                    window_span_lister,
                                    window_value_setter,
                                    )
from utils_shared.helpers import (file_name_sanitiser,
                                  panel_name_teller,
                                  panel_order_merger,
                                  )
from utils_shared.master_page_exporter import master_page_exporter
from utils_shared.individual_experiment_exporter import (size_describer,
                                                         spectra_size_estimator,
                                                         workbook_size_estimator,
                                                         )
from utils_shared.pca_fitter import (component_builder,
                                     component_classifier,
                                     component_count_suggester,
                                     component_finder,
                                     decomposition_example_finder,
                                     fit_saver,
                                     fit_table_builder,
                                     TYPE_NAMES,
                                     )
from utils_shared.questions import (accept_asker,
                                    choice_asker,
                                    confirm_waiter,
                                    enter_waiter,
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
from utils_shared.redox_regions import (REGION_KEYS,
                                        region_edge_copier,
                                        region_edge_setter,
                                        region_edges_builder,
                                        region_layout_finder,
                                        region_pointer_reader,
                                        region_span_reader,
                                        short_region_closer,
                                        )
from utils_shared.spectral_decomposer import (answers_fit_loader,
                                              BACKGROUND_SHORT_NAMES,
                                              fit_describer,
                                              fit_names_lister,
                                              library_haems_lister,
                                              OWN_HAEMS_NAME,
                                              PRESETS_FOLDER_NAME,
                                              )
from utils_shared.survey import (decomposition_asker,
                                 delta_psi_asker,
                                 event_asker,
                                 haem_choice_asker,
                                 IGNORE_LABEL,
                                 label_angle_asker,
                                 ocr_kind_lister,
                                 od_scaling_asker,
                                 saved_values_reader,
                                 signal_asker,
                                 temperature_asker,
                                 trim_layout_finder,
                                 trim_limits_builder,
                                 trim_minutes_builder,
                                 trim_minutes_setter,
                                 trim_pointer_reader,
                                 )
from utils_shared.user_notices import problem_shower, problem_teller, warning_shower
from utils_viewer.viewer_edges import EdgeChoice
from utils_viewer.viewer_preview import (BROWSING_ANSWERS,
                                         EXPORT_PARTS,
                                         import_data_exporter,
                                         pca_example_picture_builder,
                                         pca_picture_builder,
                                         pca_spectra_gatherer,
                                         preview_drawer,
                                         preview_figure_builder,
                                         PreviewSpec,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_gui import active_gui_getter
from utils_viewer.viewer_strip import (BACK_CHANGE,
                                       form_answers_builder,
                                       HAEM_FORM_TEXTS,
                                       kept_decomposition_builder,
                                       MASTER_CHANGE,
                                       OCR_FORM_TEXTS,
                                       PANEL_ORDER_CHANGE,
                                       psi_answers_builder,
                                       psi_change_describer,
                                       size_answers_builder,
                                       strip_values_builder,
                                       )
from utils_viewer.viewer_table import (label_entries_reader,
                                       label_table_builder,
                                       od_rows_reader,
                                       od_table_builder,
                                       table_problem_teller,
                                       )


# ---- CONSTANTS -----------------------------------------------------------------------
WARNING_COLOUR = '\x1b[1;31m'  # bold red
# what the event labels show, as the terminal says it when Labels as is changed
LABEL_CHANGE_TEXTS = {'chamber': 'the concentration in the chamber (400 µM KCN)',
                      'added': 'what was added (10 µL of 200 mM KCN)',
                      }
PCA_COMPONENTS_TITLE = 'PCA components'
PCA_EXAMPLES_TITLE = 'PCA examples (smallest and largest residual)'
STAGE_TITLES = {'trim': 'Trimming and ignoring',
                'details': 'OD values and event labels',
                'processing': 'Processing',
                'plots': 'Individual experiment plots',
                }
# The boxes of the trimming step in the strip, in the order of survey.TRIM_KEYS.
TRIM_FIELDS = [('trim_start', 'Trim start'),
               ('trim_end', 'end'),
               ('ignore_start', 'Ignore first'),
               ('ignore_end', 'last'),
               ]
TRIM_KEY_TEXT = 'grey hatched = trimmed away, amber = ignored in calculations'
# The numbers of the haem fit questions of the processing, from QUESTION_FLOW.md 4.A.
PROCESSING_FIT_NUMBERS = {'decompose': '4.1', 'fit': '4.1.1', 'spectrometer': '4.1.2'}
TRIM_NUDGE = ('Type the times in the strip under the plot, or drag the edges; press '
              'Enter with this box empty when every file looks right.')
# The boxes of the regions step in the strip, in the order of redox_regions.REGION_KEYS.
REGION_FIELDS = [('oxidised_start', 'Oxidised from'),
                 ('oxidised_end', 'to'),
                 ('reduced_start', 'Reduced from'),
                 ('reduced_end', 'to'),
                 ]
REGION_KEY_TEXT = 'red = oxidised region, blue = reduced region'
REGION_NUDGE = ('Type the times in the strip under the plot, or pull the regions out on '
                'the plot; press Enter with this box empty when every file looks right.')
# The boxes of the window step in the strip, and its tick boxes (averaging.WINDOW_KEYS):
# one row for the settled windows, one for the quick windows.
WINDOW_FIELDS = [('window_s', 'Settled window'),
                 ('gap_s', 'Gap before the next addition'),
                 ]
WINDOW_SWITCH = ('is_on', 'Settled windows')
QUICK_FIELDS = [('quick_s', 'Quick window'), ('delay_s', 'Start after the addition')]
QUICK_SWITCH = ('quick_is_on', 'Quick windows')
WINDOW_KEY_TEXT = ('gold = baseline, blue = settled window, green = quick window, red '
                   'hatched = a window that does not fit')
WINDOW_NUDGE = ('Type the numbers of the windows in the strip under the plot, or drag '
                'the edges of a window; press Enter with this box empty when the '
                'windows look right.')


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


# ---- _answers_previewer --------------------------------------------------------------
def _answers_previewer(answers: dict,
                       fit: Optional[dict],
                       kind: str,
                       has_od: bool = False,
                       ) -> dict:
    """
    ---- Summary ----
    Helper function to build the answers used to draw a preview: the raw data while
    browsing and trimming, and the processing chosen so far afterwards. The haems and
    the OCR are shown as the answers say (the strip under the plot sets them), per OD
    only once OD values were entered.

    ---- Inputs ----
    answers : dict
        Answers given so far.
    fit : Optional[dict]
        Fit dictionary, used to list the haems to show.
    kind : str
        'raw' (O2 and the raw OCR only), 'standard' (the standard plot: O2, the OCR
        and, when a fit is given, every haem of it), 'analysis' (also the averaging
        windows, and the haems only when they are decomposed) or 'final' (exactly as
        the figure will be).
    has_od : bool
        True when OD values were entered in this run; without them nothing is per OD,
        whatever the answers say.

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
    if not (has_od and result['normalise_od']) or kind == 'raw':
        result.update({'normalise_od': False, 'haem_per_od': False})
        if result['ocr_mode'] == 'od' or kind == 'raw':
            result['ocr_mode'] = 'raw'
    if kind in ('raw', 'standard'):
        result.update({'decompose': False, 'averaging': False})
        if kind == 'standard' and fit is not None:
            result.update({'decompose': True,
                           'plot_haems': True,
                           'haems': list(fit['haem_list']),
                           },
                          )
        return result
    if result['decompose'] and fit is not None:
        result.update({'plot_haems': True, 'haems': list(fit['haem_list'])})
    return result


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
    text_asker
    yes_no_asker
    """

    names = [f'PC{i + 1}' for i in range(result['components'].shape[1])]
    if not yes_no_asker('Do you want to name the components?',
                        False,
                        depth=depth,
                        number='4.1.1.7',
                        ):
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
        def name_checker(text: Optional[str]) -> Optional[str]:
            name = (text or '').strip()
            if name and ',' not in name and name not in names[:i]:
                return None
            return ('Type a name that is not empty, has no commas and is not used by '
                    'another component.'
                    )
        names[i] = text_asker(f'What is component {i + 1} ({TYPE_NAMES[types[i]]}, '
                              f'largest peak at {peak:.0f} nm) called?',
                              suggestions[i],
                              depth=depth,
                              checker=name_checker,
                              ).strip()
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


# ---- _export_asker -------------------------------------------------------------------
def _export_asker(session: ViewerSession,
                  limits: Dict[str, dict],
                  details: Dict[str, dict],
                  ) -> None:
    """
    ---- Summary ----
    Helper function to ask, at the end of the import, whether to export the files of
    each experiment now so they can be plotted outside the program (nothing; the
    workbook of the trimmed data; that and the whole recording of each trimmed file;
    either of those with the spectra as csv files; each with its size worked out for
    these files), and to do it. Enter gives nothing. The choice and the limits exported
    are kept in the session, so new edges can export again.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file, as entered in section 3.

    ---- Globals read ----
    WARNING_COLOUR (module constant); settings.SPECTRA_CSV_BYTES,
    settings.WORKBOOK_POINT_BYTES; EXPORT_PARTS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal, writes the files and sets
    session.export_choice and session.export_limits (side effects).

    ---- Equations ----
    Size of a choice = the trimmed workbooks, + the whole recordings' workbooks when
    it writes them, + the spectra of each when it writes them.

    ---- Helpers ----
    choice_asker
    import_data_exporter
    info_printer
    progress_clearer
    progress_printer
    size_describer
    spectra_size_estimator
    text_colourer
    workbook_size_estimator
    """

    # ---- 1 Ask what to export, with the size of each choice --------------------------
    sheets_bytes = workbook_size_estimator(session.summaries,
                                           limits,
                                           settings.WORKBOOK_POINT_BYTES,
                                           )
    spectra_bytes = spectra_size_estimator(session.summaries,
                                           limits,
                                           settings.SPECTRA_CSV_BYTES,
                                           )
    sizes = {}
    for key, (with_full, with_spectra) in EXPORT_PARTS.items():
        size = sheets_bytes[0] + (sheets_bytes[1] if with_full else 0.0)
        if with_spectra:
            size += spectra_bytes[0] + (spectra_bytes[1] if with_full else 0.0)
        sizes[key] = size_describer(size)
    options = [('none', 'No'),
               ('summary', f"Summary sheet, trimmed ({sizes['summary']})"),
               ('summary_full',
                f"Summary sheet, trimmed and full ({sizes['summary_full']})",
                ),
               ('spectra',
                f"Summary sheet and raw CSVs, trimmed ({sizes['spectra']})",
                ),
               ('spectra_full',
                'Summary sheet and raw CSVs, trimmed and full '
                f"({sizes['spectra_full']})",
                ),
               ]
    info_printer('The summary sheet is a workbook for each file; the raw CSVs are its '
                 'spectra, which are large and take a while to write.',
                 )
    if sheets_bytes[1] <= 0:
        info_printer('No file is trimmed, so "trimmed and full" writes the same as '
                     '"trimmed".',
                     )
    choice = choice_asker('Would you like to export the individual experiment files '
                          'now?',
                          options,
                          'none',
                          number='3.4',
                          )
    if choice == 'none':
        return

    # ---- 2 Export --------------------------------------------------------------------
    problems = import_data_exporter(
        session,
        limits,
        details,
        choice,
        progress=lambda n, total: progress_printer(f'Exporting file {n} of {total} ...'),
    )
    progress_clearer()
    for problem in problems:
        info_printer(text_colourer(f'Not exported: {problem}', WARNING_COLOUR), depth=2)
    session.export_choice = choice
    session.export_limits = {name: dict(values) for name, values in limits.items()}
    full_text = ('; the whole recording of a trimmed file is in the full folder inside '
                 'its own'
                 if EXPORT_PARTS[choice][0]
                 else ''
                 )
    info_printer(
        f'Exported {len(session.summaries) - len(problems)} file(s) to '
        f'{session.export_root}, one folder each{full_text}. Nothing is scaled '
        f'by OD, decomposed or averaged, and the ignored parts are included.',
        depth=2,
        )


# ---- _export_refresher ---------------------------------------------------------------
def _export_refresher(session: ViewerSession,
                      limits: Dict[str, dict],
                      details: Dict[str, dict],
                      ) -> None:
    """
    ---- Summary ----
    Helper function to export again, with the same choice, the files whose trimmed or
    ignored edges changed since the export of the import, so the results folder holds
    the edges in use. The whole recording of a file is written only when the file has
    just become trimmed, and taken away when it is no longer trimmed. Nothing happens
    when nothing was exported in this run.

    ---- Inputs ----
    session : ViewerSession
        The browser session, with the export's choice and limits.
    limits : Dict[str, dict]
        Trim and ignore limits of every file, as just accepted.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    WARNING_COLOUR (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal, writes the files and updates session.export_limits
    (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    import_data_exporter
    info_printer
    progress_clearer
    progress_printer
    text_colourer
    """

    if not session.export_choice:
        return
    changed = [s['name']
               for s in session.summaries
               if limits.get(s['name']) != session.export_limits.get(s['name'])
               ]
    if not changed:
        return
    info_printer(f'The edges of {len(changed)} file(s) changed since the export, so '
                 f'their trimmed data is exported again.',
                 )
    problems = import_data_exporter(
        session,
        limits,
        details,
        session.export_choice,
        names=changed,
        keep_full=True,
        progress=lambda n, total: progress_printer(f'Exporting file {n} of {total} ...'),
    )
    progress_clearer()
    for problem in problems:
        info_printer(text_colourer(f'Not exported: {problem}', WARNING_COLOUR), depth=2)
    session.export_limits = {name: dict(values) for name, values in limits.items()}


# ---- _figure_starter -----------------------------------------------------------------
def _figure_starter(answers: dict,
                    defaults: dict,
                    fit: Optional[dict],
                    include_percent: bool = True,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to set the figure of each file from the standard settings or the
    ones last saved for the dataset, keeping only what this run allows: the OCR per OD
    and the haems scaled by OD only when OD values were entered, the OCR as % of
    baseline only when the averaging windows are set up, the haems in %
    oxidised only when a file has both regions (delta D otherwise), and the haems only
    when they are decomposed, limited to those of the fit in use (all of them when none
    of the saved ones is in it). The Haems box of the settings strip says whether the
    haems are worked out and shown, so the figure has them whenever they are decomposed.
    How the haems and the OCR are shown, the journal and the size are left as the
    answers hold them, which the settings strip may have changed.

    ---- Inputs ----
    answers : dict
        Answers dictionary the figure settings are stored in; must hold normalise_od,
        decompose, averaging, ocr_mode, haem_mode and haem_per_od.
    defaults : dict
        The standard or saved answers (plot_o2, plot_ocr, haems, event_label_angle).
    fit : Optional[dict]
        Fit dictionary (haem_list), or None when the haems are not decomposed.
    include_percent : bool
        True when at least one file has an oxidised and a reduced region, so the
        haems can be shown in % oxidised.

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

    kinds = ocr_kind_lister(answers['normalise_od'], bool(answers['averaging']))
    haem_mode = answers['haem_mode']
    if haem_mode == 'percent' and not include_percent:
        haem_mode = 'delta'
    has_haems = bool(answers['decompose'] and fit is not None)
    haem_list = list(fit['haem_list']) if has_haems else []
    haems = [name for name in defaults['haems'] if name in haem_list]
    # The per OD box of the haems keeps its tick while they are in % oxidised, which
    # has no per OD, so it is as it was when they go back to delta D.
    answers.update({'plot_o2': defaults['plot_o2'],
                    'plot_ocr': defaults['plot_ocr'],
                    'ocr_mode': (answers['ocr_mode']
                                 if answers['ocr_mode'] in kinds
                                 else kinds[0]
                                 ),
                    'plot_haems': has_haems,
                    'haems': haems or haem_list,
                    'haem_mode': haem_mode,
                    'haem_per_od': bool(answers['haem_per_od'] and
                                        answers['normalise_od'],
                                        ),
                    'event_label_angle': defaults['event_label_angle'],
                    },
                   )


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
    them. A preset's name is refused, as the preset is what that name loads.

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
    spectral_decomposer.PRESETS_FOLDER_NAME.

    ---- Outputs ----
    Optional[str]
        Name of the file saved, or None when nothing was saved.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and writes the fit file (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    fit_saver
    info_printer
    problem_teller
    text_asker
    yes_no_asker
    """

    if not yes_no_asker('Do you want to save these components as a fit file in the '
                        'fits folder?',
                        True,
                        depth=depth,
                        number='4.1.1.8',
                        ):
        return None
    default = f'pca_{count}_components_{window[0]:g}-{window[1]:g}nm'
    def stem_finder(text: Optional[str]) -> str:
        raw = (text or '').strip()
        stem = raw[:-4] if raw.lower().endswith('.csv') else raw
        return file_name_sanitiser(stem, default='')
    def stem_checker(text: Optional[str]) -> Optional[str]:
        return None if stem_finder(text) else 'Type a name for the fit file.'
    while True:
        stem = stem_finder(text_asker('What should the fit file be called (without '
                                      '.csv)?',
                                      default,
                                      depth=depth,
                                      checker=stem_checker,
                                      number='4.1.1.9',
                                      ),
                           )
        path = fits_folder / f'{stem}.csv'
        if (fits_folder / PRESETS_FOLDER_NAME / path.name).is_file():
            info_printer(f'{path.name} is the name of a preset, so the components '
                         'could not be chosen under it. Type another name.',
                         depth=depth,
                         )
            continue
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
            info_printer(problem_teller('The fit file could not be saved', exc),
                         depth=depth,
                         )
            return None
        info_printer(f'Saved {path.name} in the fits folder. It is in the list of fits '
                     f'from now on.',
                     depth=depth,
                     )
        return path.name


# ---- _kept_restorer ------------------------------------------------------------------
def _kept_restorer(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Helper function to go back to the decomposition kept to compare with: its fit, its
    haems ticked, its background, its spectrometer, its numbers of delta psi and the
    regions of every file are in use again, and nothing is kept any more. While the
    regions are being chosen on the plot they are left as they are, and one sentence
    says so.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its kept decomposition (not None) becomes its fit and its
        regions, and is dropped.
    answers : dict
        Answers dictionary the kept answers are put back in.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes ``answers`` and the session and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    """

    kept = session.kept
    fit = kept['fit']
    haems = [haem for haem in answers['haems'] if haem in fit['haem_list']]
    answers.update(kept['answers'])
    answers.update({'decompose': True,
                    'plot_haems': True,
                    'haems': haems or list(fit['haem_list']),
                    },
                   )
    session.fit = fit
    session.kept = None
    info_printer(f"Back to {kept['text']}. The one kept to compare is no longer "
                 'shown.',
                 )
    if session.is_choosing_regions:
        info_printer('The regions stay as they are on the plot while you are '
                     'choosing them.',
                     tight=True,
                     )
    else:
        session.regions = copy.deepcopy(kept['regions'])


# ---- _label_table_filler -------------------------------------------------------------
def _label_table_filler(session: ViewerSession,
                        entries: Dict[str, List[dict]],
                        ) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Helper function to have the label, the stock and the volume added (or the
    concentration in the chamber) of every event filled in in the labels table of the
    window (3.2).

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    entries : Dict[str, List[dict]]
        {file name: [event entry, ...]} to start from (event_entries_builder,
        event_entries in DATA_FORMAT.md).

    ---- Globals read ----
    IGNORE_LABEL (imported constant); settings.CHAMBER_VOLUME_ML.

    ---- Outputs ----
    Dict[str, List[dict]]
        The events with the labels, stocks, volumes and concentrations typed.

    ---- Globals mutated ----
    None. Shows and hides the table and reads from and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _table_filler
    label_entries_reader
    label_table_builder
    """

    table = label_table_builder(session.summaries,
                                entries,
                                IGNORE_LABEL,
                                settings.CHAMBER_VOLUME_ML,
                                )
    chamber = f'{settings.CHAMBER_VOLUME_ML:g} mL'
    values = _table_filler(session,
                           table,
                           question='Fill in the label, the stock and the volume added '
                           'of each event, then press Confirm.',
                           note=f'One row per event. Write {IGNORE_LABEL} as the label '
                           'to leave an event out. Type the stock with its unit (nM, '
                           'µM, mM or M; a number alone is mM) and the volume added, '
                           f'and the concentration in the chamber ({chamber}) is '
                           'worked out, the same label added again adding up. Or '
                           'leave them empty and type the concentration in the '
                           'chamber (a number alone is µM).',
                           number='3.2',
                           )
    return label_entries_reader(table, values, entries)


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


# ---- _master_page_saver --------------------------------------------------------------
def _master_page_saver(session: ViewerSession,
                       answers: dict,
                       limits: Dict[str, dict],
                       details: Dict[str, dict],
                       ) -> None:
    """
    ---- Summary ----
    Helper function to save the master page of the file shown: its figure, drawn as it
    will be saved, on one page of the journal of the strip (the standard journal for
    "None"), as a PDF in the results folder. What was saved, or why it was not, is
    said in one sentence.

    ---- Inputs ----
    session : ViewerSession
        The browser session (the file shown, the fit in use, the regions, the results
        folder).
    answers : dict
        The answers the figure is drawn with.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the PDF and prints to the terminal; the details of a problem go to
    the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    info_printer
    master_page_exporter
    preview_figure_builder
    problem_shower
    warning_shower
    """

    # ---- 1 Draw the figure of the file shown, as it will be saved --------------------
    name = session.summaries[session.current]['name']
    spec = PreviewSpec(answers=_answers_previewer(answers, session.fit, 'final'),
                       limits=copy.deepcopy(limits),
                       fit=session.fit,
                       details=copy.deepcopy(details),
                       show_ignored=False,
                       regions=copy.deepcopy(session.regions),
                       )
    figure, notes = preview_figure_builder(session, spec, name)
    if figure is None:
        warning_shower(f'The master page of {name} was not saved. {notes}')
        return

    # ---- 2 Save it on a page of the journal ------------------------------------------
    journal = spec.answers['journal']
    try:
        path = master_page_exporter(figure,
                                    settings.JOURNAL_SPECS[journal],
                                    journal,
                                    name,
                                    session.export_root,
                                    )
    except Exception as exc:  # a page that cannot be saved must never stop the questions
        problem_shower(f'The master page of {name} was not saved', exc)
        return
    info_printer(f'Saved the master page of {name} '
                 f"({settings.JOURNAL_SPECS[journal]['name']}) as {path.name} in "
                 f'{session.export_root}.',
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
    Helper function to have the OD, volume and dilution of every file filled in in the
    OD table of the window (3.1.1).

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    rows : Dict[str, Dict[str, Optional[float]]]
        The rows to start from (od_rows, DATA_FORMAT.md); None leaves a cell empty.

    ---- Globals read ----
    settings.OD_RESUSPENDED_ML.

    ---- Outputs ----
    Dict[str, Dict[str, Optional[float]]]
        The rows as filled in, every value a number above 0.

    ---- Globals mutated ----
    None. Shows and hides the table and reads from and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _table_filler
    od_rows_reader
    od_table_builder
    """

    table = od_table_builder(rows)
    values = _table_filler(session,
                           table,
                           question='Fill in the OD, volume and dilution of each '
                           'file, then press Confirm.',
                           note='One row per file: the OD of the cells added, the '
                           'volume of cells (mL) spun down and resuspended in '
                           f'{settings.OD_RESUSPENDED_ML:g} mL, and the dilution '
                           'factor if the cells were diluted mid run.',
                           number='3.1.1',
                           )
    return od_rows_reader(table, values)


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
    problem_teller
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
        info_printer(problem_teller('The PCA pictures could not be drawn', exc),
                     depth=depth,
                     )


# ---- _region_rules_lister ------------------------------------------------------------
def _region_rules_lister(summaries: List[dict],
                         limits: Dict[str, dict],
                         dataset: Optional[str],
                         ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to give, for every file, what the edges of its regions are kept
    within on the time axis of the processing plot (which starts at 0 where the trimmed
    data starts): the used part of the run and the least length of a region.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    limits : Dict[str, dict]
        Trim and ignore limits of every file; the trim times are on the original
        recording, the ignore times are minutes from the trimmed edges.
    dataset : Optional[str]
        The spectrometer whose spectra hold the haems; None when it is not known.

    ---- Globals read ----
    settings.REGION_MINIMUM_POINTS.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'used_span': (first, last) time of the used part (min on the
        plot), 'minimum_min': least length of a region (min), 'shift': trim start
        (min), to add to a time on the plot for the time on the recording}}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    first = ignore start; last = (trim end - trim start) - ignore end, never before
    first. least length = least number of spectra x duration / number of spectra (the
    number of time points when the file does not say how many spectra it holds).

    ---- Helpers ----
    None.
    """

    rules = {}
    for summary in summaries:
        name = summary['name']
        own = limits.get(name) or {}
        duration = float(summary['duration_min'])
        shift = float(own.get('trim_start') or 0.0)
        kept_end = float(own.get('trim_end') or duration) - shift
        first = float(own.get('ignore_start') or 0.0)
        last = max(kept_end - float(own.get('ignore_end') or 0.0), first)
        shape = (summary.get('spectra_shapes') or {}).get(dataset)
        count = (shape[0] if shape else 0) or summary.get('frames') or 1
        rules[name] = {'used_span': (first, last),
                       'minimum_min': settings.REGION_MINIMUM_POINTS * duration / count,
                       'shift': shift,
                       }
    return rules


# ---- _regions_chooser ----------------------------------------------------------------
def _regions_chooser(session: ViewerSession,
                     answers: dict,
                     limits: Dict[str, dict],
                     details: Dict[str, dict],
                     remembered: Optional[Dict[str, Dict[str, float]]],
                     ) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Helper function to run the regions step on the plot of every file: the oxidised and
    the reduced region are pulled out on the plot or typed in the strip under it, and
    Enter accepts them. With "Every file" ticked, an edge set on the file shown is
    copied to every file at the same distance from its nearest addition. Enter with no
    region on any file means no regions; when only some files have both, a question
    names the others and asks whether to continue without them, and No goes back to
    the edges as they were. The regions are then listed, with the files a copy could
    not reach.

    ---- Inputs ----
    session : ViewerSession
        The browser session, with the processing plot drawn.
    answers : dict
        Answers so far; decomposition_dataset names the spectra the haems come from.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file; an edge is copied by the additions not
        ignored there.
    remembered : Optional[Dict[str, Dict[str, float]]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
        times on the original recording (min), which the edges start at; None, or a
        file missing, for regions not chosen.

    ---- Globals read ----
    REGION_FIELDS, REGION_KEY_TEXT, REGION_NUDGE (module constants).

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
        times on the original recording (min), so a later change of the trim leaves
        them on the same data. A region not chosen, or too short to count, has its two
        edges together.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and draws on the plot window (side
    effects).

    ---- Equations ----
    time on the recording = time on the plot + trim start.

    ---- Helpers ----
    _addition_time_lister
    _region_rules_lister
    _regions_lister
    enter_waiter
    info_printer
    region_edge_copier
    region_edge_setter
    region_edges_builder
    region_layout_finder
    region_pointer_reader
    region_span_reader
    short_region_closer
    yes_no_asker
    EdgeChoice
    """

    # ---- 1 The limits, the additions and the starting edges of every file ------------
    rules = _region_rules_lister(session.summaries,
                                 limits,
                                 answers.get('decomposition_dataset'),
                                 )
    additions = _addition_time_lister(session.summaries, limits, details)
    start = {}
    for name, rule in rules.items():
        own = (remembered or {}).get(name)
        on_plot = ({key: own[key] - rule['shift'] for key in REGION_KEYS}
                   if own
                   else None
                   )
        start[name] = region_edges_builder(rule['used_span'],
                                           on_plot,
                                           rule['minimum_min'],
                                           )

    # ---- 2 The rules of the edges ----------------------------------------------------
    # The edges of each file a copy could not reach, until they are set another way.
    unreached: Dict[str, Set[str]] = {}
    def setter(name: str,
               values: Dict[str, float],
               key: str,
               value: float,
               ) -> Dict[str, float]:
        unreached.get(name, set()).discard(key)
        return region_edge_setter(values,
                                  key,
                                  value,
                                  rules[name]['used_span'],
                                  rules[name]['minimum_min'],
                                  )
    def copier(shown: str, name: str, key: str, value: float) -> Optional[float]:
        copied = region_edge_copier(value, additions[shown], additions[name])
        if copied is None:
            unreached.setdefault(name, set()).add(key)
        return copied
    choice = EdgeChoice(fields=list(REGION_FIELDS),
                        values=start,
                        layout_finder=lambda name, values: (
                            region_layout_finder(values, rules[name]['minimum_min'])),
                        pointer_reader=lambda name, values, key, time_min: (
                            region_pointer_reader(time_min)),
                        value_setter=setter,
                        key_text=REGION_KEY_TEXT,
                        value_copier=copier,
                        )

    # ---- 3 Pull out or type the regions until Enter ----------------------------------
    info_printer('OXIDISED and REDUCED regions = where the haems are fully oxidised '
                 "and fully reduced. Each haem's level in them gives its % oxidised.",
                 )
    info_printer('Red is oxidised, blue is reduced; with "Every file" ticked, an edge '
                 'is copied to every file at the same distance from its nearest '
                 'addition.',
                 tight=True,
                 )
    info_printer('With no regions the haems cannot be shown in % oxidised; everything '
                 'else is the same.',
                 tight=True,
                 )
    session.window.edges_shower(choice)
    # While the edges are on the plot they are the regions being chosen, so a click on
    # Go back to kept leaves the regions alone.
    session.is_choosing_regions = True
    try:
        while True:
            enter_waiter('Pull the oxidised and the reduced region out on the plot, '
                         'or type their times in the strip under it. Press Enter when '
                         'every file looks right, or straight away for no regions.',
                         REGION_NUDGE,
                         number='4.4',
                         )
            values = {name: short_region_closer(own, rules[name]['minimum_min'])
                      for name, own in session.window.edges_reader().items()
                      }

            # ---- 3.1 Ask again when only some files have both regions ----------------
            # No region anywhere means none are wanted, so nothing is asked.
            spans = {name: region_span_reader(own, rules[name]['minimum_min'])
                     for name, own in values.items()
                     }
            missing = [summary['name']
                       for summary in session.summaries
                       if None in spans[summary['name']].values()
                       ]
            is_any_open = any(span is not None
                              for own in spans.values()
                              for span in own.values()
                              )
            if not missing or not is_any_open:
                break
            info_printer(f"Without both an oxidised and a reduced region: "
                         f"{', '.join(missing)}. A file needs both to be shown in % "
                         'oxidised.',
                         )
            if yes_no_asker('Do you want to continue without them?',
                            False,
                            number='4.4.1',
                            ):
                break
    finally:
        session.is_choosing_regions = False
        session.window.edges_hider()

    # ---- 4 List the regions ----------------------------------------------------------
    _regions_lister(session.summaries,
                    values,
                    rules,
                    [name for name in values if unreached.get(name)],
                    )
    return {name: {key: own[key] + rules[name]['shift'] for key in REGION_KEYS}
            for name, own in values.items()
            }


# ---- _regions_lister -----------------------------------------------------------------
def _regions_lister(summaries: List[dict],
                    values: Dict[str, Dict[str, float]],
                    rules: Dict[str, dict],
                    unreached: List[str],
                    ) -> None:
    """
    ---- Summary ----
    Helper function to print the two regions of every file in one list, then name the
    files that kept an edge of their own because they have fewer additions than the
    file it was copied from.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    values : Dict[str, Dict[str, float]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} on
        the time axis of the plot (min).
    rules : Dict[str, dict]
        The limits of every file (_region_rules_lister).
    unreached : List[str]
        The files a copied edge could not reach.

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
    region_span_reader
    warning_shower
    """

    info_printer('Regions (minutes on the plot):')
    for summary in summaries:
        name = summary['name']
        spans = region_span_reader(values[name], rules[name]['minimum_min'])
        texts = [f'{region} not chosen'
                 if span is None
                 else f'{region} {round(span[0], 2):g} to {round(span[1], 2):g}'
                 for region, span in spans.items()
                 ]
        info_printer(f"  {name}: {', '.join(texts)}")
    if unreached:
        kept = ('has fewer additions, so it kept the region it had'
                if len(unreached) == 1
                else 'have fewer additions, so they kept the regions they had'
                )
        warning_shower(f"{', '.join(unreached)}: {kept} when an edge was copied to "
                       'every file. Go back to the processing step to set it on that '
                       'file alone, with "Every file" unticked.',
                       )


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
    standard fit for a dataset never saved. It also loads a fit picked, or haems
    ticked, in the settings strip. When the haems cannot be shown, one line says why
    and the plot keeps to the oxygen and the OCR.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md); the spectrometers in common are used.
    defaults : dict
        Default answers (decompose, fit_file, haem_files, decomposition_dataset).
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
    answers_fit_loader
    fit_names_lister
    info_printer
    problem_teller
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
    if not name or (name != OWN_HAEMS_NAME and name not in fit_names_lister(fits_folder)):
        info_printer(f'{lead}: the fit {name} is not in {fits_folder}. '
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
        return answers_fit_loader(fits_folder,
                                  name,
                                  defaults.get('haem_files') or [],
                                  ), dataset
    except (OSError, ValueError) as exc:
        problem = problem_teller(f'{lead}: the fit {name} could not be read', exc)
        info_printer(f'{problem} '
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
    run; ticking them, picking a fit or ticking library haems under Build a fit works
    them out with the fit in the strip; a new background works them out again, and so
    does another spectrometer. A new way of showing the haems or the OCR, a per OD box,
    or a new choice of what the event labels show, redraws the plot with it. A panel moved with the arrow beside it, or the Standard order
    button, changes the order kept for the panels of every file, said in the terminal.
    A number typed in the Δψ row is kept in the answers (the two
    filled-in midpoints with it), said in the terminal and Δψ worked out again. A fit
    that cannot be used is reported and the strip is set back. Keep to compare keeps
    the fit, the background, the regions and the numbers of Δψ in use, drawn dashed
    over the haems and over Δψ until one of the two is chosen (Keep this one carries
    on with what is on the plot, Go back to kept puts the kept one back in use) or
    the haems are left out. A new journal, width or height redraws only the figure of
    each file, the one plot drawn at its size. A click on Export master saves the
    master page of the file shown while that figure is on the plot, and says when it
    can be saved otherwise.

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
    LABEL_CHANGE_TEXTS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes ``answers`` and the session, prints to the terminal, shows the strip
    and redraws the plot (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _kept_restorer
    _standard_fit_loader
    _strip_shower
    form_answers_builder
    info_printer
    kept_decomposition_builder
    panel_name_teller
    panel_order_merger
    psi_answers_builder
    psi_change_describer
    size_answers_builder
    """

    # ---- 0 The master page: a click, which changes nothing ---------------------------
    if changes.get(MASTER_CHANGE):
        if session.is_figure and session.master_exporter is not None:
            session.master_exporter()
        else:
            info_printer('The master page shows the figure of a file on a page of the '
                         'journal, so it can be exported once that figure is on the '
                         'plot, in the individual experiment plots.',
                         )
        return

    # ---- 1 The journal, the width and the height -------------------------------------
    sizes = size_answers_builder(changes)
    answers.update(sizes)
    is_redrawn = bool(sizes) and session.is_figure

    # ---- 2 The background under the haems --------------------------------------------
    if 'haem_background' in changes:
        answers['haem_background'] = changes['haem_background']
        info_printer('The background under the haems is now '
                     f"{BACKGROUND_SHORT_NAMES[answers['haem_background']]}.",
                     )
        is_redrawn = is_redrawn or session.fit is not None

    # ---- 2.1 The spectrometer, and how the haems and the OCR are shown ---------------
    forms = form_answers_builder(changes)
    answers.update(forms)
    if 'spectra' in changes:
        info_printer(f"The haems are now read from the {changes['spectra']} spectra.")
    if 'haem_mode' in changes:
        info_printer('The haems are now shown as '
                     f"{HAEM_FORM_TEXTS[changes['haem_mode']]}.",
                     )
    if 'haem_per_od' in changes:
        info_printer('The haems are '
                     f"{'now' if changes['haem_per_od'] else 'no longer'} shown per "
                     'OD.',
                     )
    if 'ocr_mode' in changes:
        info_printer(f"The OCR is now shown as {OCR_FORM_TEXTS[changes['ocr_mode']]}.")
    if 'label_mode' in changes:
        info_printer('The event labels now show '
                     f"{LABEL_CHANGE_TEXTS[changes['label_mode']]}.",
                     )
    is_redrawn = is_redrawn or bool(forms)

    # ---- 2.2 The order of the panels -------------------------------------------------
    if PANEL_ORDER_CHANGE in changes:
        shown = list(changes[PANEL_ORDER_CHANGE])
        answers['panel_order'] = panel_order_merger(answers.get('panel_order') or [],
                                                    shown,
                                                    ) if shown else []
        info_printer('The panels are now, from the top: '
                     f"{', '.join(panel_name_teller(key) for key in shown)}."
                     if shown
                     else 'The panels are back in the standard order.',
                     )
        is_redrawn = True

    # ---- 2.3 The numbers of delta psi ------------------------------------------------
    psi_answers = psi_answers_builder(changes, answers)
    if psi_answers:
        answers.update(psi_answers)
        for line in psi_change_describer(changes, answers):
            info_printer(line)
        is_redrawn = True

    # ---- 3 The haems and the fit -----------------------------------------------------
    if changes.get('plot_haems') is False:
        answers.update({'decompose': False, 'plot_haems': False})
        session.fit = None
        session.kept = None
        info_printer('The haems are left out of the run.')
        is_redrawn = True
    elif ('fit_file' in changes or
          'haem_files' in changes or
          changes.get('plot_haems')
          ):
        name = changes.get('fit_file') or answers['fit_file']
        ticked = list(changes.get('haem_files', answers.get('haem_files', [])))
        fit, dataset = _standard_fit_loader(session.summaries,
                                            dict(answers,
                                                 decompose=True,
                                                 fit_file=name,
                                                 haem_files=ticked,
                                                 ),
                                            fits_folder,
                                            is_from_strip=True,
                                            )
        if fit is not None:
            haems = [haem for haem in answers['haems'] if haem in fit['haem_list']]
            answers.update({'decompose': True,
                            'plot_haems': True,
                            'fit_file': name,
                            'haem_files': ticked if name == OWN_HAEMS_NAME else [],
                            'decomposition_dataset': dataset,
                            'haems': haems or list(fit['haem_list']),
                            },
                           )
            session.fit = fit
            info_printer('The haems are worked out with '
                         f'{fit_describer(name, ticked)}.',
                         )
            is_redrawn = True

    # ---- 4 Keep the decomposition in use to compare with, or choose one of the two ---
    if changes.get(BACK_CHANGE) and session.kept is not None:
        _kept_restorer(session, answers)
        is_redrawn = True
    elif 'compare' in changes and session.fit is not None:
        in_use = kept_decomposition_builder(answers, session.fit, session.regions)
        session.kept = in_use if changes['compare'] else None
        info_printer(f"Kept {in_use['text']} to compare: change the haems, the "
                     'background, the regions or the Δψ numbers, and the kept lines '
                     'show dashed on the plot. Then click Keep this one or Go back '
                     'to kept.'
                     if changes['compare']
                     else f"Carrying on with {in_use['text']}. The one kept to "
                          'compare is no longer shown.',
                     )
        is_redrawn = True
    elif changes.get('compare'):
        info_printer('There are no haems worked out yet to keep: they are worked out '
                     'in the processing.',
                     )

    # ---- 5 Show what is in use and redraw --------------------------------------------
    _strip_shower(session, answers)
    if is_redrawn and session.redraw is not None:
        session.redraw()


# ---- _strip_shower -------------------------------------------------------------------
def _strip_shower(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Helper function to show in the settings strip what the run uses now: the haems
    ticked when they are worked out, the fit, the decomposition kept to compare with,
    the spectrometer, how the haems and the OCR are shown, the journal and the size.
    It also says what the strip offers: the spectrometers every file has, % oxidised
    when at least one file has both regions, per OD when OD values were entered, and
    the OCR as % of baseline once the averaging windows are set up
    (session.has_windows). Haems in % oxidised go back to delta D when no file has
    both regions any more.

    ---- Inputs ----
    session : ViewerSession
        The browser session (its window, fit, limits, regions and whether OD values
        were entered).
    answers : dict
        Answers so far.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. May change haem_mode in ``answers``, and shows the values in the strip
    (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    region_files_lister
    strip_values_builder
    """

    common = set(session.summaries[0]['datasets'])
    for summary in session.summaries[1:]:
        common &= set(summary['datasets'])
    has_percent = bool(region_files_lister(session.summaries,
                                           session.limits,
                                           session.regions,
                                           answers.get('decomposition_dataset'),
                                           ),
                       )
    if answers['haem_mode'] == 'percent' and not has_percent:
        answers['haem_mode'] = 'delta'
    session.window.strip_choices_setter(sorted(common),
                                        has_percent,
                                        session.has_od,
                                        session.has_windows,
                                        )
    fit = session.fit
    session.window.strip_setter(strip_values_builder(answers,
                                                     fit is not None,
                                                     fit.get('haem_files', [])
                                                     if fit is not None
                                                     else [],
                                                     session.kept['text']
                                                     if session.kept is not None
                                                     else '',
                                                     ),
                                )


# ---- _table_filler -------------------------------------------------------------------
def _table_filler(session: ViewerSession,
                  table: dict,
                  question: str,
                  note: str,
                  number: str,
                  ) -> List[Dict[str, Any]]:
    """
    ---- Summary ----
    Helper function to have a table filled in in the window: the table fills the
    terminal side, the instruction waits for Confirm, and while a cell is wrong or a
    needed cell empty one sentence names those cells and the instruction goes on
    waiting. The table is then taken away.

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    table : dict
        The table to show (table_rows, DATA_FORMAT.md).
    question : str
        The instruction, ending "then press Confirm.".
    note : str
        What the table needs, said above the instruction in the quieter colour.
    number : str
        The instruction's own number from QUESTION_FLOW.md, such as '3.2'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Dict[str, Any]]
        The values typed, one {name of the value: value} per row of the table
        (AnswerTable.values_reader).

    ---- Globals mutated ----
    None. Shows and hides the table and reads from and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    confirm_waiter
    table_problem_teller
    """

    window = session.window
    window.table_shower(table)
    def table_checker() -> Optional[str]:
        return table_problem_teller(window.table_reader()[1])
    try:
        confirm_waiter(question, table_checker, note=note, number=number)
        return window.table_reader()[0]
    finally:
        window.table_hider()


# ---- _unfit_windows_lister -----------------------------------------------------------
def _unfit_windows_lister(spans: List[Tuple[str, float, float, Optional[str]]],
                          quick: List[Tuple[str, float, float, Optional[str]]],
                          ) -> List[str]:
    """
    ---- Summary ----
    Helper function to name, in plain words, the averaging windows of one file that do
    not fit.

    ---- Inputs ----
    spans : List[Tuple[str, float, float, Optional[str]]]
        The baseline and the settled windows of the file, as window_span_lister gives
        them (the baseline alone when there are no settled windows).
    quick : List[Tuple[str, float, float, Optional[str]]]
        The quick windows of the file, as quick_span_lister gives them; empty when
        there are none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        One name for each window with a problem: 'the baseline before addition 1',
        'the settled one before addition 3', 'the settled one after the last
        addition', 'the quick one after addition 2'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    names = []
    for index, (_, _, _, problem) in enumerate(spans):
        if problem is None:
            continue
        if index == 0:
            names.append('the baseline before addition 1')
        elif index == len(spans) - 1:
            names.append('the settled one after the last addition')
        else:
            names.append(f'the settled one before addition {index + 1}')
    names += [f'the quick one after addition {index}'
              for index, (_, _, _, problem) in enumerate(quick, start=1)
              if problem is not None
              ]
    return names


# ---- _windows_chooser ----------------------------------------------------------------
def _windows_chooser(session: ViewerSession,
                     answers: dict,
                     defaults: dict,
                     limits: Dict[str, dict],
                     details: Dict[str, dict],
                     ) -> None:
    """
    ---- Summary ----
    Helper function to run the window step on the plot of every file: the averaging
    windows are shaded on the plot, the baseline before the first addition in gold
    with its name. The settled windows (blue) have one length and one
    gap before the next addition for every window of every file: pulling the start of
    any of them changes the length, pulling its end the gap. The quick windows (green)
    have one length and one start after their addition: pulling the start of any of
    them changes how long after the addition they start, pulling its end the length.
    All four are also typed in the two rows of the strip under the plot, where each
    kind has its tick box; with both unticked there are no windows. Enter accepts. The
    windows that do not fit are shaded red and named in a warning after Enter. When no
    file has an addition, nothing is asked and nothing is averaged.

    ---- Inputs ----
    session : ViewerSession
        The browser session, with the processing plot drawn without windows.
    answers : dict
        Answers dictionary the values are stored in; final_gap_minutes is how long
        before the end of the recording the last window ends.
    defaults : dict
        Default answers the step starts with (averaging, settled_windows,
        window_minutes, gap_minutes, quick_windows, quick_minutes, delay_minutes).
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file; the windows go around the additions not
        ignored there.

    ---- Globals read ----
    QUICK_FIELDS, QUICK_SWITCH, WINDOW_FIELDS, WINDOW_KEY_TEXT, WINDOW_NUDGE,
    WINDOW_SWITCH (module constants); settings.BASELINE_MINIMUM_SECONDS,
    settings.DRAG_STEP_SECONDS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores averaging (True with either kind ticked), settled_windows,
    window_minutes, gap_minutes, quick_windows, quick_minutes and delay_minutes in
    ``answers``, reads from and prints to the terminal and draws on the plot window
    (side effects).

    ---- Equations ----
    minutes = seconds / 60. The data of a file runs from 0 to (trim end - trim start)
    on the time axis of the plot.

    ---- Helpers ----
    _addition_time_lister
    _unfit_windows_lister
    enter_waiter
    info_printer
    quick_span_lister
    warning_shower
    window_layout_finder
    window_pointer_reader
    window_span_lister
    window_value_setter
    EdgeChoice
    """

    # ---- 1 The additions and the data of every file ----------------------------------
    additions = _addition_time_lister(session.summaries, limits, details)
    if not any(additions.values()):
        answers['averaging'] = False
        info_printer('None of the files has an addition, so there are no averaging '
                     'windows.',
                     )
        return
    final_gap = float(answers['final_gap_minutes'])
    minimum_s = float(settings.BASELINE_MINIMUM_SECONDS)
    step_s = float(settings.DRAG_STEP_SECONDS)
    spans = {}
    for summary in session.summaries:
        own = limits.get(summary['name']) or {}
        shift = float(own.get('trim_start') or 0.0)
        spans[summary['name']] = (0.0,
                                  float(own.get('trim_end') or summary['duration_min'])
                                  - shift,
                                  )

    # ---- 2 The rules of the edges ----------------------------------------------------
    is_averaging = bool(defaults['averaging'])
    start = {'window_s': round(defaults['window_minutes'] * 60.0, 2),
             'gap_s': round(defaults['gap_minutes'] * 60.0, 2),
             'is_on': 1.0 if is_averaging and defaults['settled_windows'] else 0.0,
             'quick_s': round(defaults['quick_minutes'] * 60.0, 2),
             'delay_s': round(defaults['delay_minutes'] * 60.0, 2),
             'quick_is_on': 1.0 if is_averaging and defaults['quick_windows'] else 0.0,
             }
    choice = EdgeChoice(fields=list(WINDOW_FIELDS),
                        values={name: dict(start) for name in additions},
                        layout_finder=lambda name, values: (
                            window_layout_finder(values,
                                                 additions[name],
                                                 spans[name],
                                                 final_gap,
                                                 minimum_s,
                                                 )),
                        pointer_reader=lambda name, values, key, time_min: (
                            window_pointer_reader(values,
                                                  key,
                                                  time_min,
                                                  additions[name],
                                                  spans[name],
                                                  final_gap,
                                                  step_s,
                                                  )),
                        value_setter=lambda name, values, key, value: (
                            window_value_setter(values, key, value)),
                        key_text=WINDOW_KEY_TEXT,
                        unit='s',
                        switch=WINDOW_SWITCH,
                        second_fields=list(QUICK_FIELDS),
                        second_switch=QUICK_SWITCH,
                        )

    # ---- 3 Drag or type the windows until Enter --------------------------------------
    info_printer('AVERAGING WINDOWS = the stretches around each addition that its '
                 'averages are taken over.',
                 )
    info_printer('The baseline (gold) is the window before the first addition, as '
                 'long as a settled window; every other window is compared with it.',
                 tight=True,
                 )
    info_printer('A settled window (blue) ends a set time before the next addition, '
                 f'the last one {final_gap:g} min before the end of the recording; a '
                 'quick window (green) starts a set time after its addition. Each '
                 'kind has one length, in every file.',
                 tight=True,
                 )
    info_printer('Pull the start of a settled window to change its length, its end to '
                 'change the gap before the addition; pull the start of a quick window '
                 'to change how long after the addition it starts, its end to change '
                 'its length.',
                 tight=True,
                 )
    session.window.edges_shower(choice)
    try:
        enter_waiter('Drag an edge of any window on the plot, or type the numbers in '
                     'the strip under it, where each kind of window has its tick box. '
                     'Press Enter when the windows look right, or untick both kinds '
                     'for none.',
                     WINDOW_NUDGE,
                     number='4.6',
                     )
        chosen = next(iter(session.window.edges_reader().values()))
    finally:
        session.window.edges_hider()

    # ---- 4 Keep the windows and name those that do not fit ---------------------------
    answers['settled_windows'] = bool(chosen['is_on'])
    answers['quick_windows'] = bool(chosen['quick_is_on'])
    answers['averaging'] = answers['settled_windows'] or answers['quick_windows']
    answers['window_minutes'] = chosen['window_s'] / 60.0
    answers['gap_minutes'] = chosen['gap_s'] / 60.0
    answers['quick_minutes'] = chosen['quick_s'] / 60.0
    answers['delay_minutes'] = chosen['delay_s'] / 60.0
    if not answers['averaging']:
        info_printer('No averaging windows: nothing is averaged around the additions.')
        return
    if answers['settled_windows']:
        info_printer(f"Settled windows: {round(chosen['window_s'], 2):g} s long, "
                     f"ending {round(chosen['gap_s'], 2):g} s before the next "
                     'addition.',
                     )
    else:
        info_printer(f"Baseline: {round(chosen['window_s'], 2):g} s long, ending "
                     f"{round(chosen['gap_s'], 2):g} s before the first addition. No "
                     'settled windows.',
                     )
    if answers['quick_windows']:
        info_printer(f"Quick windows: {round(chosen['quick_s'], 2):g} s long, "
                     f"starting {round(chosen['delay_s'], 2):g} s after their "
                     'addition.',
                     tight=True,
                     )
    unfit = []
    for summary in session.summaries:
        name = summary['name']
        if not additions[name]:
            continue
        settled = window_span_lister(additions[name],
                                     spans[name],
                                     answers['window_minutes'],
                                     answers['gap_minutes'],
                                     final_gap,
                                     minimum_s,
                                     )
        quick = (quick_span_lister(additions[name],
                                   spans[name],
                                   answers['quick_minutes'],
                                   answers['delay_minutes'],
                                   )
                 if answers['quick_windows']
                 else []
                 )
        names = _unfit_windows_lister(settled
                                      if answers['settled_windows']
                                      else settled[:1],
                                      quick,
                                      )
        if names:
            unfit.append(f"{name}: {', '.join(names)}")
    if unfit:
        warning_shower('These averaging windows do not fit (not enough time), so they '
                       f"are left out: {'; '.join(unfit)}. They are red on the plot. "
                       'Go back to the processing step to shorten them or move them '
                       'if they are needed.',
                       )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- browser_stage_runner ------------------------------------------------------------
def browser_stage_runner(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Main function to show the standard plot of the files in the plot window (the set
    and measured O2, the OCR and, when the session has a fit, the haems, with the
    events as written in the file) before any question is asked about them. The user can
    look through them in the window while answering, so the questions carry straight
    on.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its redraw is set.
    answers : dict
        Answers so far, used for the figure style of the preview.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws the plot window (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    preview_drawer
    """

    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers,
                                                 session.fit,
                                                 'standard',
                                                 session.has_od,
                                                 ),
                              {},
                              session.fit,
                              {},
                              show_ignored=False,
                              )
    session.redraw = redraw
    redraw()


# ---- details_stage_runner ------------------------------------------------------------
def details_stage_runner(session: ViewerSession,
                         answers: dict,
                         defaults: dict,
                         limits: Dict[str, dict],
                         remembered: Dict[str, dict],
                         details_before: Optional[Dict[str, dict]] = None,
                         ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the last questions of the import, on the standard plot cut to
    the limits: the OD values, the temperature of the runs, then the event labels, the
    OD values and the labels each in a table of the window.
    Once OD values are entered, the strip shows its per OD boxes and a line says so.
    The plot is redrawn with the labels once they are entered, and they are accepted or
    typed again; with no events in any file there is nothing to accept. Last, the
    export of what was imported is offered. The haems are those of the session's fit.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its redraw is set.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file (trim_stage_runner).
    remembered : Dict[str, dict]
        The files part of the dataset's settings, with the OD values and events saved
        before (dataset_settings, DATA_FORMAT.md).
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
    None. Stores normalise_od and temperature_c in ``answers`` and whether OD values
    were entered in the
    session, shows the strip and writes the export when one is chosen (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _export_asker
    _label_table_filler
    _od_lister
    _od_table_filler
    _strip_shower
    accept_asker
    event_asker
    info_printer
    od_scaling_asker
    preview_drawer
    saved_values_reader
    temperature_asker
    """

    # ---- 1 Read the values saved for the dataset -------------------------------------
    summaries = session.summaries
    details: Dict[str, dict] = {s['name']: {} for s in summaries}
    saved = saved_values_reader(summaries, remembered)
    for name, values in (details_before or {}).items():
        saved[name] = dict(saved.get(name) or {}, **values)
    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers,
                                                 session.fit,
                                                 'standard',
                                                 session.has_od,
                                                 ),
                              limits,
                              session.fit,
                              details,
                              )
    session.redraw = redraw

    # ---- 2 OD values -----------------------------------------------------------------
    # They are filled in in a table, which is its own check. The per OD boxes of the
    # strip then say whether the OCR and the haems are scaled by them.
    def table_filler(rows: Dict[str, dict]) -> Dict[str, dict]:
        return _od_table_filler(session, rows)
    details = od_scaling_asker(summaries, answers, defaults, saved, table_filler)
    session.has_od = bool(answers['normalise_od'])
    _strip_shower(session, answers)
    if answers['normalise_od']:
        _od_lister(details)
        info_printer('The OCR and the haems can now be shown per OD, in the strip '
                     'under the plot: the per OD box beside Haems as, and per OD '
                     'under OCR as.',
                     )

    # ---- 2.1 The temperature of the runs ---------------------------------------------
    # One value for the dataset, asked of everyone: delta psi is worked out with it.
    # The delta psi row of the strip holds the same value, so the one in use (the
    # strip may have changed it) is offered, and the strip shows the answer.
    temperature_asker(answers, dict(defaults, temperature_c=answers['temperature_c']))
    _strip_shower(session, answers)

    # ---- 3 Event labels --------------------------------------------------------------
    # The table opens again with the labels as last typed until they are accepted.
    def label_filler(entries: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
        return _label_table_filler(session, entries)
    has_events = any(s['events'] for s in summaries)
    kept: Set[str] = set()
    while True:
        for name, events in event_asker(summaries, saved, label_filler, kept).items():
            details[name]['events'] = events
            saved[name] = dict(saved.get(name) or {}, events=events)
        redraw()
        if not has_events or accept_asker('Do you accept these event labels?',
                                          [('no', 'change the labels again')],
                                          number='3.3',
                                          ) == 'yes':
            break

    # ---- 4 Offer the export of what was imported -------------------------------------
    _export_asker(session, limits, details)
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
        Trim and ignore limits of every file (trim_stage_runner).
    fits_folder : Path
        Folder holding the fit .csv files.
    dataset : str
        Spectral dataset holding the haem spectra.
    depth : int
        Numbering depth of the questions.

    ---- Globals read ----
    settings.PCA_WINDOW_NM, settings.PCA_SMOOTHING_NM.

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
    accept_asker
    component_builder
    component_classifier
    component_count_suggester
    component_finder
    decomposition_example_finder
    fit_table_builder
    info_printer
    number_asker
    pca_spectra_gatherer
    problem_teller
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
    start = float(defaults.get('pca_start') or settings.PCA_WINDOW_NM[0])
    end = float(defaults.get('pca_end') or settings.PCA_WINDOW_NM[1])
    rotate = bool(defaults.get('pca_rotate', True))
    count = int(defaults.get('pca_count') or 0)
    smoothing = float(defaults.get('pca_smoothing_nm', settings.PCA_SMOOTHING_NM))
    while True:
        # ---- 1 Choose the window and read the spectra --------------------------------
        start = number_asker('Where should the spectral window start (nm)?',
                             start,
                             minimum=0,
                             depth=depth,
                             number='4.1.1.1',
                             )
        end = number_asker('Where should the spectral window end (nm)?',
                           max(end, start + 20.0),
                           minimum=start,
                           exclusive_minimum=True,
                           depth=depth,
                           number='4.1.1.2',
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
            info_printer(text_colourer(problem_teller('The analysis could not be run',
                                                      exc,
                                                      ),
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
            count = int(number_asker(f'How many components should be found? (The data '
                                     f'suggest {suggestion}; use as few as describe '
                                     f'the data, extra ones only fit noise.)',
                                     count,
                                     minimum=1,
                                     maximum=available,
                                     depth=depth,
                                     is_whole=True,
                                     number='4.1.1.3',
                                     ),
                        )
            rotate = yes_no_asker('Do you want to rotate the components so each is as '
                                  'peak-like as possible (varimax)?',
                                  rotate,
                                  depth=depth,
                                  number='4.1.1.4',
                                  )
            smoothing = number_asker('Over how many nm should the components be '
                                     'smoothed to remove their noise (0 for none)?',
                                     smoothing,
                                     minimum=0,
                                     maximum=(end - start) / 4,
                                     depth=depth,
                                     number='4.1.1.5',
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
                info_printer(problem_teller('No example decomposition could be made',
                                            exc,
                                            ),
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
            choice = accept_asker('Do you accept these components?',
                                  [('count', 'change the number of components'),
                                   ('window', 'change the spectral window'),
                                   ('fit', 'choose a fit file instead'),
                                   ],
                                  depth=depth,
                                  number='4.1.1.6',
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
    the angle of the event labels): only that part's questions are asked, with the
    current choices as the defaults, and the figure is drawn and asked about again. The
    settings strip turns the haems on or off and sets how they and the OCR are shown,
    the journal and the size, so 'which haems' asks only which ones in which
    order, and none of those is asked. The OCR asked for as % of baseline with no
    averaging windows set up offers the window step of the processing.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its fit is the one in use, its regions say which files
        have % oxidised, and its redraw is set.
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
    _figure_starter
    _strip_shower
    _windows_chooser
    accept_asker
    haem_choice_asker
    info_printer
    label_angle_asker
    preview_drawer
    region_files_lister
    signal_asker
    """

    # ---- 1 Start from the standard or saved settings ---------------------------------
    info_printer('The figure saved for each file is drawn with the standard settings, '
                 'or with the ones last saved for this dataset. Change only what you '
                 'want different; you can look at every file before accepting it.',
                 )
    info_printer('How the haems are shown, the journal and the size are in the strip '
                 'under the plot; each change redraws the figure.',
                 tight=True,
                 )
    # % oxidised is offered when at least one file has both regions.
    include_percent = bool(region_files_lister(session.summaries,
                                               limits,
                                               session.regions,
                                               answers.get('decomposition_dataset'),
                                               ),
                           )
    _figure_starter(answers, defaults, session.fit, include_percent)
    session.has_windows = bool(answers['averaging'])
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
    # the Export master button of the strip saves a journal page with this figure
    def master_exporter() -> None:
        if is_plotted():
            _master_page_saver(session, answers, limits, details)
        else:
            info_printer('Nothing is set to be plotted, so there is no figure to put '
                         'on a master page.',
                         )
    session.master_exporter = master_exporter
    # The OCR as % of baseline needs the averaging windows: with none set up, the
    # window step of the processing is run here, over the processing plot.
    def windows_adder() -> bool:
        def processing_redraw() -> bool:
            return preview_drawer(session,
                                  _answers_previewer(dict(answers, averaging=False),
                                                     session.fit,
                                                     'analysis',
                                                     session.has_od,
                                                     ),
                                  limits,
                                  session.fit,
                                  details,
                                  )
        session.redraw, session.is_figure = processing_redraw, False
        session.window.strip_state_setter(False)
        try:
            processing_redraw()
            # with neither kind kept, the settled windows are the ones ticked
            is_any = answers['settled_windows'] or answers['quick_windows']
            _windows_chooser(session,
                             answers,
                             dict(answers,
                                  averaging=True,
                                  settled_windows=(answers['settled_windows']
                                                   or not is_any
                                                   ),
                                  ),
                             limits,
                             details,
                             )
        finally:
            session.window.strip_state_setter(True)
            session.redraw, session.is_figure = redraw, True
        session.has_windows = bool(answers['averaging'])
        return session.has_windows

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
        # The Haems box turns the haems on and off, and the strip holds how they are
        # shown, the journal and the size.
        changes = [('signals', 'change the oxygen and OCR')]
        if answers['plot_haems']:
            changes.append(('haems', 'change which haems are shown'))
        if plotted:
            changes.append(('angle', 'change the angle of the event labels'))
        choice = accept_asker('Do you accept this figure?', changes)
        if choice == 'yes':
            return is_plotted()

        # ---- 2.3 Ask that part's questions -------------------------------------------
        current = dict(answers)
        if choice == 'signals':
            signal_asker(answers, current, windows_adder)
        elif choice == 'haems':
            haem_choice_asker(answers, current, session.fit)
        else:
            label_angle_asker(answers, current)
        _strip_shower(session, answers)  # the OCR chosen shows under OCR as


# ---- processing_stage_runner ---------------------------------------------------------
def processing_stage_runner(session: ViewerSession,
                            answers: dict,
                            defaults: dict,
                            limits: Dict[str, dict],
                            fits_folder: Path,
                            details: Dict[str, dict],
                            trim_runner: Callable[[], Dict[str, dict]],
                            regions: Optional[Dict[str, Dict[str, float]]] = None,
                            ) -> Optional[Dict[str, Dict[str, float]]]:
    """
    ---- Summary ----
    Main function to talk the user through the processing, with the plot redrawn after
    each answer: first the haem fit, then, now that the haems are seen, an offer to
    change the trim and ignore times, then the oxidised and the reduced region of every
    file (when the haems are shown), then whether to work out Δψ (when it can be), and
    last the averaging windows, dragged on the plot (they are drawn in the plot only
    once that step is answered). A line
    points to the strip at the start, and another to its % oxidised once a file has
    both regions. The
    settings strip picks the fit and leaves the haems out, so the decomposition
    question only offers to find the components from the data instead. While those
    questions are asked the strip is greyed out.

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
        Trim and ignore limits of every file (trim_stage_runner).
    fits_folder : Path
        Folder holding the fit .csv files.
    details : Dict[str, dict]
        OD values and events of every file (details_stage_runner); the averaging
        windows are drawn around the events not ignored there.
    trim_runner : Callable[[], Dict[str, dict]]
        Function that asks the trim and ignore questions again with the haems of the
        session's fit on the plot, and returns the new limits.
    regions : Optional[Dict[str, Dict[str, float]]]
        The regions the step starts with (_regions_chooser), from the last time it
        was answered in this run; None for regions not chosen.

    ---- Globals read ----
    settings.DELTA_PSI_LIMIT_ANSWERS.

    ---- Outputs ----
    Optional[Dict[str, Dict[str, float]]]
        The regions of every file as _regions_chooser gives them; those given, when
        the haems are not decomposed and the step is not asked. The fit is in
        session.fit (None when the haems are not decomposed).

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` and the fit in the session, reads from and
    prints to the terminal and redraws the window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _windows_chooser
    _decomposition_storer
    _regions_chooser
    _strip_shower
    accept_asker
    decomposition_asker
    delta_psi_asker
    fit_names_lister
    info_printer
    pca_stage_runner
    preview_drawer
    region_files_lister
    yes_no_asker
    """

    summaries = session.summaries
    # The windows are drawn in the plot only once their step is answered: until then
    # they are edges over it, and the steps before it show none. The answers keep the
    # windows of the last time meanwhile, so a run stopped here loses nothing.
    drawn = {'windows': False}
    session.has_windows = False
    def redraw() -> bool:
        shown = dict(answers, averaging=answers['averaging'] and drawn['windows'])
        return preview_drawer(session,
                              _answers_previewer(shown,
                                                 session.fit,
                                                 'analysis',
                                                 session.has_od,
                                                 ),
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
            session.window.strip_fits_setter(fit_names_lister(fits_folder))
            session.window.strip_state_setter(True)

    # ---- 1 The haem fit --------------------------------------------------------------
    # The strip is pointed to first, as it changes the decomposition at any time.
    common = set(summaries[0]['datasets'])
    for summary in summaries[1:]:
        common &= set(summary['datasets'])
    info_printer('Use the strip under the plot to change the fit, the background'
                 f"{', the spectrometer (Spectra)' if len(common) > 1 else ''} and how "
                 'the haems are shown (Haems as); the plot is redrawn after each '
                 'change.',
                 )

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
                                                  numbers=PROCESSING_FIT_NUMBERS,
                                                  ),
                              )
    else:
        answers['decompose'] = True
        info_printer(
            'The haems are worked out with '
            f"{fit_describer(answers['fit_file'], answers.get('haem_files', []))}.",
            )

    # ---- 1.2 Accept the fit or find the components from the data ---------------------
    # The strip picks another fit and leaves the haems out.
    while answers['decompose']:
        redraw()
        if accept_asker('Do you accept this decomposition?',
                        [('pca', 'find the components from the data')],
                        number='4.2',
                        ) == 'yes':
            break
        name, fit = pca_finder(answers['decomposition_dataset'], 2)
        if fit is not None:
            answers.update({'decompose': True, 'fit_file': name})
            session.fit = fit
            _strip_shower(session, answers)
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

    # ---- 3 The oxidised and the reduced region ---------------------------------------
    # The regions go to the session at once, so the plots that follow and the strip
    # have their % oxidised.
    if answers['decompose']:
        regions = _regions_chooser(session, answers, limits, details, regions)
        session.regions = regions or {}
        _strip_shower(session, answers)
        if region_files_lister(summaries,
                               limits,
                               regions,
                               answers.get('decomposition_dataset'),
                               ):
            info_printer('The haems can now be shown in % oxidised: choose it under '
                         'Haems as in the strip under the plot.',
                         )

    # ---- 4 Delta psi -----------------------------------------------------------------
    # Asked only when it can be worked out; the plot then gets or loses its panel.
    if answers['decompose'] and session.fit is not None:
        was_on = bool(answers['delta_psi'])
        is_on = delta_psi_asker(answers,
                                defaults,
                                list(session.fit['haem_list']),
                                region_files_lister(summaries,
                                                    limits,
                                                    regions,
                                                    answers.get('decomposition_dataset',
                                                                ),
                                                    ),
                                )
        _strip_shower(session, answers)  # the delta psi row comes or goes with it
        if is_on != was_on:
            redraw()
        if is_on:
            lowest, highest = (answers[answer]
                               for answer in settings.DELTA_PSI_LIMIT_ANSWERS
                               )
            info_printer('Δψ (mV) has its own panel on the plot, for the files with '
                         'both regions; it has gaps where bH or bL is less than '
                         f'{lowest:g} % or more than {highest:g} % reduced. Change '
                         'the numbers of the method in the Δψ row of the strip under '
                         'the plot.',
                         )
            info_printer('To compare fits, click Keep to compare, change the fit or '
                         'the background, then click Keep this one or Go back to '
                         'kept.',
                         tight=True,
                         )
    else:
        # without haems there is no delta psi, whatever the dataset was saved with
        answers['delta_psi'] = False
        _strip_shower(session, answers)

    # ---- 5 The averaging windows -----------------------------------------------------
    # Without haems nothing has drawn this step's plot yet: it may still show the plot
    # of another step.
    if not answers['decompose']:
        redraw()
    _windows_chooser(session, answers, defaults, limits, details)
    drawn['windows'] = True
    # the strip now offers the OCR as % of baseline, when there are windows
    session.has_windows = bool(answers['averaging'])
    _strip_shower(session, answers)
    if answers['averaging']:
        redraw()
    # Read now: Go back to kept may have put the kept regions back since they were
    # chosen.
    return session.regions if answers['decompose'] else regions


# ---- region_files_lister -------------------------------------------------------------
def region_files_lister(summaries: List[dict],
                        limits: Dict[str, dict],
                        regions: Optional[Dict[str, Dict[str, float]]],
                        dataset: Optional[str],
                        ) -> List[str]:
    """
    ---- Summary ----
    Main function to list the files that have both an oxidised and a reduced region
    under the trim and ignore limits as they are now: the files whose haems have two
    levels, and so a % oxidised.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    regions : Optional[Dict[str, Dict[str, float]]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
        times on the original recording (min); None, or a file missing, for none.
    dataset : Optional[str]
        The spectrometer whose spectra hold the haems; None when it is not known.

    ---- Globals read ----
    REGION_KEYS.

    ---- Outputs ----
    List[str]
        Names of the files with both regions, in the order of the summaries.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time on the plot = time on the recording - trim start; a region kept within the
    used part of the run counts when it is at least the least length.

    ---- Helpers ----
    _region_rules_lister
    region_edges_builder
    region_span_reader
    """

    rules = _region_rules_lister(summaries, limits, dataset)
    names = []
    for summary in summaries:
        name = summary['name']
        own = (regions or {}).get(name)
        if not own or any(key not in own for key in REGION_KEYS):
            continue
        rule = rules[name]
        values = region_edges_builder(rule['used_span'],
                                      {key: own[key] - rule['shift']
                                       for key in REGION_KEYS
                                       },
                                      rule['minimum_min'],
                                      )
        if None not in region_span_reader(values, rule['minimum_min']).values():
            names.append(name)
    return names


# ---- trim_stage_runner ---------------------------------------------------------------
def trim_stage_runner(session: ViewerSession,
                      answers: dict,
                      remembered: Dict[str, dict],
                      previous: Optional[Dict[str, dict]] = None,
                      ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to run the trimming step on the standard plot of the whole recording
    of every file: the trimmed and ignored edges are dragged on the plot or typed in
    the strip under it, and Enter accepts them. When the step is opened again, the
    limits it had stay on the plot as red dashed lines. The limits are then listed and
    the trimmed data is drawn. The haems are those of the session's fit (none when it
    has none).

    ---- Inputs ----
    session : ViewerSession
        The browser session; its redraw is set.
    answers : dict
        Answers so far, used for the figure style of the preview.
    remembered : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} the edges start
        at (from the last run, or this run's when the step is opened again).
    previous : Optional[Dict[str, dict]]
        Limits in the same layout drawn as red dashed lines while the edges are
        dragged; None for none.

    ---- Globals read ----
    TRIM_FIELDS, TRIM_KEY_TEXT, TRIM_NUDGE (module constants).

    ---- Outputs ----
    Dict[str, dict]
        The limits of every file, as trim_limits_builder gives them.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and draws the plot window (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _limits_lister
    enter_waiter
    info_printer
    preview_drawer
    trim_layout_finder
    trim_limits_builder
    trim_minutes_builder
    trim_minutes_setter
    trim_pointer_reader
    EdgeChoice
    """

    # ---- draw ------------------------------------------------------------------------
    def draw(limits: Optional[Dict[str, dict]] = None) -> bool:
        # None: the whole recording, for the edges; limits: the data they keep
        return preview_drawer(session,
                              _answers_previewer(answers,
                                                 session.fit,
                                                 'standard',
                                                 session.has_od,
                                                 ),
                              limits or {},
                              session.fit,
                              {},
                              show_trim=limits is None,
                              )
    session.redraw = draw
    draw()

    # ---- 2 Drag or type the edges until Enter ----------------------------------------
    by_name = {s['name']: s for s in session.summaries}
    choice = EdgeChoice(fields=list(TRIM_FIELDS),
                        values=trim_minutes_builder(session.summaries, remembered),
                        layout_finder=lambda name, minutes: trim_layout_finder(by_name[name],
                                                                               minutes,
                                                                               ),
                        pointer_reader=lambda name, minutes, key, time_min: (
                            trim_pointer_reader(by_name[name], minutes, key, time_min)),
                        value_setter=lambda name, minutes, key, value: (
                            trim_minutes_setter(by_name[name], minutes, key, value)),
                        key_text=TRIM_KEY_TEXT,
                        previous=(trim_minutes_builder(session.summaries, previous)
                                  if previous
                                  else {}
                                  ),
                        )
    info_printer('TRIM = data that is not imported, plotted or used.')
    info_printer('IGNORE = data that is plotted but not used for calculations.')
    info_printer('Grey edges trim, amber edges ignore; with "Every file" ticked, a '
                 'change moves every file.',
                 tight=True,
                 )
    session.window.edges_shower(choice)
    try:
        enter_waiter('Drag the edges on the plot, or type the times in the strip under '
                     'it. Press Enter when every file looks right.',
                     TRIM_NUDGE,
                     number='2.1',
                     )
        minutes = session.window.edges_reader()
    finally:
        session.window.edges_hider()

    # ---- 3 List the limits and draw what they keep -----------------------------------
    limits = trim_limits_builder(session.summaries, minutes)
    _limits_lister(session.summaries, limits)
    session.redraw = lambda: draw(limits)
    draw(limits)
    return limits


# ---- viewer_asker --------------------------------------------------------------------
def viewer_asker(summaries: List[dict],
                 answers: dict,
                 defaults: dict,
                 remembered: Dict[str, dict],
                 fits_folder: Path,
                 export_root: Path,
                 exported: Optional[List[Path]] = None,
                 ) -> Tuple[Dict[str, dict],
                            Optional[dict],
                            Dict[str, dict],
                            bool,
                            Dict[str, Dict[str, float]],
                            bool,
                            ]:
    """
    ---- Summary ----
    Main function to ask the questions of the experiment browser: the file browser,
    trimming and ignoring, the OD values and the event labels (which end the import),
    the processing (the haem fit, the trim and ignore times again if wanted, the
    oxidised and reduced regions, which start where they were saved with the dataset,
    the averaging) and the individual figures. The standard plot of every file (oxygen,
    OCR and the haems of the dataset's fit) is shown first, with no question asked. The
    plot window is redrawn after each answer, and at the end any step can be gone back
    to. The settings strip can be changed while these questions wait (except those of
    the components found from the data); it is greyed out afterwards.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    remembered : Dict[str, dict]
        The files part of the dataset's settings: {file name: limits, OD values,
        events and regions} from the last run (dataset_settings, DATA_FORMAT.md).
    fits_folder : Path
        Folder holding the fit .csv files.
    export_root : Path
        Results folder.
    exported : Optional[List[Path]]
        List the results folder is added to once the export of the import writes into
        it, so the caller can say it is kept even when the questions are stopped; None
        when the caller does not need to know.

    ---- Globals read ----
    STAGE_TITLES (module constant); settings.STANDARD_FIT; REGION_KEYS; EXPORT_PARTS.

    ---- Outputs ----
    Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool, Dict[str, dict], bool]
        (limits, fit, details, plotted, regions, has_spectra): the trim and ignore
        limits of every file, the fit (None when the haems are not decomposed), the OD
        values and events of every file, whether the figure of each file has at least
        one panel, the oxidised and reduced region of every file as _regions_chooser
        gives them (those saved with the dataset when the step was not asked), and
        whether the export of the import wrote the spectra as csv files.

    ---- Globals mutated ----
    None. Stores the answers in ``answers``, reads from and prints to the terminal,
    draws and closes the plot window, sets up the settings strip, writes the export
    when one is chosen and adds to ``exported`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_refresher
    _standard_fit_loader
    _strip_change_applier
    _strip_shower
    active_gui_getter
    browser_stage_runner
    choice_asker
    details_stage_runner
    fit_names_lister
    heading_printer
    library_haems_lister
    info_printer
    numbering_getter
    numbering_setter
    plots_stage_runner
    processing_stage_runner
    section_starter
    trim_stage_runner
    """

    window = active_gui_getter()
    session = ViewerSession(summaries, export_root, window)
    if exported is not None:
        session.exported = exported  # the same list, so the caller sees what is added
    window.session_attacher(session)
    # The regions saved with the dataset are where the regions step starts, and give
    # the first plots their % oxidised.
    saved_regions = {name: dict(entry['regions'])
                     for name, entry in remembered.items()
                     if isinstance(entry.get('regions'), dict) and
                     all(isinstance(entry['regions'].get(key), (int, float))
                         for key in REGION_KEYS
                         )
                     }
    state: dict = {'regions': saved_regions}
    session.regions = saved_regions

    # ---- 1 Load the fit of the standard plot -----------------------------------------
    # A dataset saved without haems has no fit name; the strip then offers the standard
    # fit.
    answers['fit_file'] = answers.get('fit_file') or settings.STANDARD_FIT
    session.fit, dataset = _standard_fit_loader(summaries, answers, fits_folder)
    if session.fit is not None:
        answers['decomposition_dataset'] = dataset

    # ---- 2 Set up the settings strip -------------------------------------------------
    window.strip_fits_setter(fit_names_lister(fits_folder))
    window.strip_library_setter(library_haems_lister(fits_folder))
    _strip_shower(session, answers)
    window.strip_listener_setter(lambda changes: _strip_change_applier(session,
                                                                       answers,
                                                                       fits_folder,
                                                                       changes,
                                                                       ),
                                 )
    window.strip_state_setter(True)

    def run_trim() -> Dict[str, dict]:
        old = state.get('limits') or remembered
        state['limits'] = trim_stage_runner(session, answers, old, state.get('limits'))
        # the strip offers % oxidised for the regions that hold under these limits
        session.limits = state['limits']
        _strip_shower(session, answers)
        answers['ignore_first_minutes'] = max(v['ignore_start']
                                              for v in state['limits'].values()
                                              )
        answers['ignore_last_minutes'] = max(v['ignore_end']
                                             for v in state['limits'].values()
                                             )
        # asked again (4.3, or going back): an export already made follows the edges
        if state.get('details') is not None:
            _export_refresher(session, state['limits'], state['details'])
        return state['limits']
    def run_details() -> None:
        old_defaults = dict(answers) if state.get('details') else defaults
        state['details'] = details_stage_runner(session,
                                                answers,
                                                old_defaults,
                                                state['limits'],
                                                remembered,
                                                state.get('details'),
                                                )
    def run_processing() -> None:
        old_defaults = dict(answers) if state.get('fit_asked') else defaults
        state['regions'] = processing_stage_runner(session,
                                                   answers,
                                                   old_defaults,
                                                   state['limits'],
                                                   fits_folder,
                                                   state['details'],
                                                   run_trim,
                                                   session.regions,
                                                   ) or {}
        session.regions = state['regions']
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
    steps = [('trim', run_trim),
             ('details', run_details),
             ('processing', run_processing),
             ('plots', run_plots),
             ]

    # ---- 3 Ask every step once -------------------------------------------------------
    # Only the figure of each file is drawn at its size, so only there does a new
    # journal or size in the strip redraw the plot (the plots step sets it again).
    try:
        session.is_figure = False
        browser_stage_runner(session, answers)  # it asks nothing, so needs no section
        for key, runner in steps:
            session.is_figure = False
            section_starter(STAGE_TITLES[key])
            runner()
        last_section, last_question = numbering_getter(0), numbering_getter(1)

        # ---- 4 Go back to any step ---------------------------------------------------
        options = [('done', 'No, continue')]
        options += [(key, STAGE_TITLES[key]) for key, _ in steps]
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
            number = index + 2  # section 1 is the files
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
        window.strip_listener_setter(None)
        window.strip_state_setter(False)
        session.redraw = None
        session.window.window_closer()

    # ---- 5 Return the answers --------------------------------------------------------
    # Read now: the strip may have changed the haems, or gone back to the kept regions,
    # after the figure was accepted.
    plotted = bool(answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems'])
    has_spectra = EXPORT_PARTS.get(session.export_choice, (False, False))[1]
    return (state['limits'],
            session.fit,
            state['details'],
            plotted,
            session.regions,
            has_spectra,
            )


# ---- windows_stage_runner ------------------------------------------------------------
def windows_stage_runner(context: dict) -> bool:
    """
    ---- Summary ----
    Main function to run the window step of the processing (4.6) by itself, after the
    browser steps have ended, for a later figure that needs the averaging windows when
    none are set up. The processing plot of every file is drawn again, with the trim
    and ignore limits, the fit and the regions already chosen, and the windows are
    dragged or typed on it as in the processing; they start ticked. Nothing else is
    asked, and the settings strip stays greyed out.

    ---- Inputs ----
    context : dict
        {answers, fit, summaries, limits, details, regions, export_root} of the run so
        far (everything_asker of main.py). The answers are changed in place.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the averaging windows are set up after the step.

    ---- Globals mutated ----
    None. Stores averaging, window_minutes and gap_minutes in the answers of the
    context, reads from and prints to the terminal and draws in the plot window (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _windows_chooser
    active_gui_getter
    preview_drawer
    """

    # ---- 1 Open the files in the window again ----------------------------------------
    answers, fit = context['answers'], context['fit']
    limits, details = context['limits'], context['details']
    window = active_gui_getter()
    session = ViewerSession(context['summaries'], context['export_root'], window)
    session.fit = fit
    session.regions = context.get('regions') or {}
    session.limits = limits
    session.has_od = bool(answers['normalise_od'])
    window.session_attacher(session)

    # ---- 2 Draw the processing plot and run the window step --------------------------
    # The windows are edges over the plot in this step, so the plot is drawn without
    # them, as in the processing.
    try:
        preview_drawer(session,
                       _answers_previewer(dict(answers, averaging=False),
                                          fit,
                                          'analysis',
                                          session.has_od,
                                          ),
                       limits,
                       fit,
                       details,
                       )
        # with neither kind kept, the settled windows are the ones ticked
        is_any = answers['settled_windows'] or answers['quick_windows']
        _windows_chooser(session,
                         answers,
                         dict(answers,
                              averaging=True,
                              settled_windows=answers['settled_windows'] or not is_any,
                              ),
                         limits,
                         details,
                         )
    finally:
        window.window_closer()
    return bool(answers['averaging'])
