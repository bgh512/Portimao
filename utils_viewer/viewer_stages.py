"""
The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.helpers import file_name_sanitiser
from utils_shared.individual_experiment_exporter import (size_describer,
                                                         spectra_size_estimator,
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
from utils_shared.survey import (averaging_asker,
                                 decomposition_asker,
                                 event_asker,
                                 haem_choice_asker,
                                 haem_form_asker,
                                 haem_scaling_asker,
                                 IGNORE_LABEL,
                                 label_angle_asker,
                                 ocr_kind_lister,
                                 od_scaling_asker,
                                 saved_values_reader,
                                 signal_asker,
                                 trim_layout_finder,
                                 trim_limits_builder,
                                 trim_minutes_builder,
                                 trim_minutes_setter,
                                 trim_pointer_reader,
                                 )
from utils_shared.user_notices import problem_teller, warning_shower
from utils_viewer.viewer_edges import EdgeChoice
from utils_viewer.viewer_preview import (BROWSING_ANSWERS,
                                         import_data_exporter,
                                         pca_example_picture_builder,
                                         pca_picture_builder,
                                         pca_spectra_gatherer,
                                         preview_drawer,
                                         skipped_windows_finder,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_gui import active_gui_getter
from utils_viewer.viewer_strip import (kept_decomposition_builder,
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
    or answer again. A drag across the plot of a file gives the window and the gap,
    from the additions of that file.

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
    _skipped_lister
    accept_asker
    averaging_asker
    """

    additions = _addition_time_lister(session.summaries, limits, details)
    while True:
        averaging_asker(answers, defaults, additions=additions)
        if not answers['averaging']:
            return
        redraw()
        _skipped_lister(session, answers, limits, details)
        if accept_asker('Do you accept these averaging windows?',
                        [('no', 'change the window and gap')],
                        ) == 'yes':
            return
        defaults = dict(defaults, averaging=True)
        defaults.update({k: answers[k] for k in ('window_minutes', 'gap_minutes')})


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
    Helper function to ask, at the end of the import, what to export now so it can be
    plotted outside the program (nothing, the workbooks, the workbooks and the trimmed
    spectra, or the spectra of the whole recordings too, with the size of the spectra
    worked out for these files), and to do it. Enter gives nothing. The choice and the
    limits exported are kept in the session, so new edges can export again.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file, as entered in section 3.

    ---- Globals read ----
    WARNING_COLOUR (module constant); settings.SPECTRA_CSV_BYTES.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal, writes the files and sets
    session.export_choice and session.export_limits (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    import_data_exporter
    info_printer
    progress_clearer
    progress_printer
    size_describer
    spectra_size_estimator
    text_colourer
    """

    # ---- 1 Ask what to export, with the size of the spectra --------------------------
    trimmed_bytes, full_bytes = spectra_size_estimator(session.summaries,
                                                       limits,
                                                       settings.SPECTRA_CSV_BYTES,
                                                       )
    options = [('none', 'Nothing'),
               ('summary', 'The summary: a workbook for each file (a few MB)'),
               ('trimmed',
                'The trimmed data: the summaries and the trimmed spectra as '
                f'csv files ({size_describer(trimmed_bytes)})',
                ),
               ('all',
                'All the data: the summaries and the spectra, trimmed and full '
                f'({size_describer(trimmed_bytes + full_bytes)})',
                ),
               ]
    info_printer('The spectra are large, and writing them takes a while.')
    choice = choice_asker('What would you like to export now, so you can plot it '
                          'yourself?',
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
    info_printer(
        f'Exported {len(session.summaries) - len(problems)} file(s) to '
        f'{session.export_root}, one folder each; the whole recording of a '
        f'trimmed file is in the full folder inside its own. Nothing is scaled '
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
    and the haems scaled by OD only when OD values were entered, the haems in %
    oxidised only when a file has both regions (delta D otherwise), and the haems only
    when they are decomposed, limited to those of the fit in use (all of them when none
    of the saved ones is in it). The Haems box of the settings strip says whether the
    haems are worked out and shown, so the figure has them whenever they are decomposed.
    The journal and size are left as the answers hold them, which the settings strip
    may have changed.

    ---- Inputs ----
    answers : dict
        Answers dictionary the figure settings are stored in; must hold normalise_od
        and decompose.
    defaults : dict
        The standard or saved answers (plot_o2, plot_ocr, ocr_mode, haems, haem_mode,
        haem_per_od, event_label_angle).
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

    kinds = ocr_kind_lister(answers['normalise_od'])
    haem_mode = defaults['haem_mode']
    if haem_mode == 'percent' and not include_percent:
        haem_mode = 'delta'
    has_haems = bool(answers['decompose'] and fit is not None)
    haem_list = list(fit['haem_list']) if has_haems else []
    haems = [name for name in defaults['haems'] if name in haem_list]
    answers.update({'plot_o2': defaults['plot_o2'],
                    'plot_ocr': defaults['plot_ocr'],
                    'ocr_mode': (defaults['ocr_mode']
                                 if defaults['ocr_mode'] in kinds
                                 else kinds[0]
                                 ),
                    'plot_haems': has_haems,
                    'haems': haems or haem_list,
                    'haem_mode': haem_mode,
                    'haem_per_od': bool(defaults['haem_per_od'] and
                                        answers['normalise_od'] and
                                        haem_mode != 'percent',
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


# ---- _label_table_filler -------------------------------------------------------------
def _label_table_filler(session: ViewerSession,
                        entries: Dict[str, List[dict]],
                        ) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Helper function to have the label and concentration of every event filled in in
    the labels table of the window (3.2).

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    entries : Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]} to
        start from (event_entries_builder).

    ---- Globals read ----
    IGNORE_LABEL (imported constant).

    ---- Outputs ----
    Dict[str, List[dict]]
        The events with the labels and concentrations typed.

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

    table = label_table_builder(session.summaries, entries, IGNORE_LABEL)
    values = _table_filler(session,
                           table,
                           question='Fill in the label and the concentration of each '
                           'event, then press Confirm.',
                           note=f'One row per event. Write {IGNORE_LABEL} as the label '
                           'to leave an event out.',
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
    them out with the fit in the strip; a new background works them out again. A fit
    that cannot be used is reported and the strip is set back. Keep to compare keeps
    the fit and background in use, drawn dashed over the haems until Stop comparing or
    the haems are left out. A new journal, width or height redraws only the figure of
    each file, the one plot drawn at its size.

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
    kept_decomposition_builder
    size_answers_builder
    """

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

    # ---- 4 Keep the decomposition in use to compare with, or stop --------------------
    if 'compare' in changes and session.fit is not None:
        kept = (kept_decomposition_builder(answers, session.fit)
                if changes['compare']
                else None
                )
        session.kept = kept
        info_printer(f"Kept {kept['text']} to compare: change the haems or the "
                     'background, and the kept haems show dashed on the plot.'
                     if kept is not None
                     else 'The kept decomposition is no longer shown.',
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
    the journal and the size.

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
                              _answers_previewer(answers, session.fit, 'standard'),
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
    the limits: the OD values, then the event labels, each in a table of the window.
    The OD values are only checked: the data is scaled by OD in the individual plots.
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
    None. Stores normalise_od in ``answers`` and writes the export when one is chosen
    (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _export_asker
    _label_table_filler
    _od_lister
    _od_table_filler
    accept_asker
    event_asker
    od_scaling_asker
    preview_drawer
    saved_values_reader
    """

    # ---- 1 Read the values of earlier runs -------------------------------------------
    summaries = session.summaries
    details: Dict[str, dict] = {s['name']: {} for s in summaries}
    saved = saved_values_reader(summaries, remembered, session.export_root)
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
    # Only checked here; the data is scaled by OD in the individual plots. They are
    # filled in in a table, which is its own check.
    def table_filler(rows: Dict[str, dict]) -> Dict[str, dict]:
        return _od_table_filler(session, rows)
    details = od_scaling_asker(summaries, answers, defaults, saved, table_filler)
    if answers['normalise_od']:
        _od_lister(details)

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
    how the haems are shown, the angle of the event labels): only that part's questions
    are asked, with the current choices as the defaults, and the figure is drawn and
    asked about again. The settings strip turns the haems on or off and sets the
    journal and size, so 'which haems' asks only which ones in which order, and the
    journal and size are not asked. The haems can be shown in % oxidised when at least
    one file has both regions.

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
    accept_asker
    haem_choice_asker
    haem_form_asker
    haem_scaling_asker
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
    # % oxidised is offered when at least one file has both regions.
    include_percent = bool(region_files_lister(session.summaries,
                                               limits,
                                               session.regions,
                                               answers.get('decomposition_dataset'),
                                               ),
                           )
    _figure_starter(answers, defaults, session.fit, include_percent)
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
        # The Haems box turns the haems on and off, and the strip holds the journal and
        # size.
        changes = [('signals', 'change the oxygen and OCR')]
        if answers['plot_haems']:
            changes.append(('haems', 'change which haems are shown'))
            changes.append(('form', 'change how the haems are shown'))
        if plotted:
            changes.append(('angle', 'change the angle of the event labels'))
        choice = accept_asker('Do you accept this figure?', changes)
        if choice == 'yes':
            return is_plotted()

        # ---- 2.3 Ask that part's questions -------------------------------------------
        current = dict(answers)
        if choice == 'signals':
            signal_asker(answers, current)
        elif choice == 'haems':
            haem_choice_asker(answers, current, session.fit)
        elif choice == 'form':
            haem_form_asker(answers, current, include_percent)
            haem_scaling_asker(answers, current)
        else:
            label_angle_asker(answers, current)


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
    file (when the haems are shown), and last the averaging around the events. The
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
    None.

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
    _averaging_reviewer
    _decomposition_storer
    _regions_chooser
    _strip_shower
    accept_asker
    decomposition_asker
    fit_names_lister
    info_printer
    pca_stage_runner
    preview_drawer
    yes_no_asker
    """

    summaries = session.summaries
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
            session.window.strip_fits_setter(fit_names_lister(fits_folder))
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
    if answers['decompose']:
        regions = _regions_chooser(session, answers, limits, details, regions)

    # ---- 4 Averaging around the events -----------------------------------------------
    _averaging_reviewer(session, answers, defaults, limits, details, redraw)
    return regions


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
                              _answers_previewer(answers, session.fit, 'standard'),
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
    STAGE_TITLES (module constant); settings.STANDARD_FIT; REGION_KEYS.

    ---- Outputs ----
    Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool, Dict[str, dict]]
        (limits, fit, details, plotted, regions): the trim and ignore limits of every
        file, the fit (None when the haems are not decomposed), the OD values and
        events of every file, whether the figure of each file has at least one panel,
        and the oxidised and reduced region of every file as _regions_chooser gives
        them (those saved with the dataset when the step was not asked).

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
                                                   state.get('regions'),
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
    # Read now: the strip may have changed the haems after the figure was accepted.
    plotted = bool(answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems'])
    return state['limits'], session.fit, state['details'], plotted, state['regions']
