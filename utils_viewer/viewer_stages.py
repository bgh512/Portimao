"""
The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.averaging import (LEFT_OUT_PROBLEM,
                                    PICKED_KEYS,
                                    quick_span_lister,
                                    window_layout_finder,
                                    window_pick_lister,
                                    window_plan_finder,
                                    window_plan_reader,
                                    window_pointer_reader,
                                    window_row_teller,
                                    window_shown_maker,
                                    window_span_lister,
                                    window_value_setter,
                                    window_values_maker,
                                    )
from utils_shared.helpers import (file_name_sanitiser,
                                  panel_name_teller,
                                  panel_order_merger,
                                  )
from utils_shared.dataset_setup import setup_builder
from utils_shared.figure_page import (FigurePage,
                                      FigurePageError,
                                      template_path_finder,
                                      template_saver,
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
                                    guide_step_starter,
                                    info_printer,
                                    number_asker,
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
                                              built_fit_saver,
                                              fit_describer,
                                              fit_names_lister,
                                              fit_titles_lister,
                                              library_haems_lister,
                                              OWN_HAEMS_NAME,
                                              PRESETS_FOLDER_NAME,
                                              )
from utils_shared.survey import (delta_psi_asker,
                                 delta_psi_offer_checker,
                                 event_asker,
                                 IGNORE_LABEL,
                                 ocr_kind_lister,
                                 ocr_view_teller,
                                 od_gaps_finder,
                                 od_scaling_asker,
                                 saved_values_reader,
                                 temperature_asker,
                                 trim_layout_finder,
                                 trim_limits_builder,
                                 trim_minutes_builder,
                                 trim_minutes_setter,
                                 trim_pointer_reader,
                                 trim_times_finder,
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
from utils_viewer.viewer_page import page_offer_checker
from utils_viewer.viewer_guide import (EXPORT_BUTTONS,
                                       EXPORT_FULL_CHANGE,
                                       EXPORT_TRIMMED_CHANGE,
                                       )
from utils_viewer.viewer_strip import (BACK_CHANGE,
                                       EDIT_LABELS_CHANGE,
                                       EDIT_ODS_CHANGE,
                                       form_answers_builder,
                                       HAEM_FORM_TEXTS,
                                       kept_decomposition_builder,
                                       MASTER_CHANGE,
                                       OCR_FORM_TEXTS,
                                       PANEL_ORDER_CHANGE,
                                       PCA_CHANGE,
                                       psi_answers_builder,
                                       psi_change_describer,
                                       PSI_FORMULA,
                                       PSI_FORMULA_NOTE,
                                       SAVE_FIT_CHANGE,
                                       size_answers_builder,
                                       strip_values_builder,
                                       TIME_TAB_CHANGE,
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
# how the kept decomposition is shown, as the terminal says it
COMPARE_LAYOUT_WORDS = {'side': 'the kept one shows as a plot of its own, on the left '
                                'of the plot in use',
                        'overlaid': 'the kept lines show faint under the plot in use, '
                                    'drawn bold',
                        }
PCA_COMPONENTS_TITLE = 'PCA components'
PCA_EXAMPLES_TITLE = 'PCA examples (smallest and largest residual)'
STAGE_TITLES = {'trim': 'Import: trimming and ignoring',
                'details': 'Set-up: OD values, temperature and event labels',
                'processing': 'Experiment processing',
                'plots': 'Experiment export: finalise figures and export',
                }
# The boxes of the trimming step, in the order of survey.TRIM_KEYS.
TRIM_FIELDS = [('trim_start', 'Trim before'),
               ('trim_end', 'after'),
               ('ignore_start', 'Ignore before'),
               ('ignore_end', 'after'),
               ]
TRIM_KEY_TEXT = 'orange hatched = trimmed, grey = ignored in calculations'
# The key above the trim question, its '=' signs lined up (the terminal side is in a
# font of one width).
TRIM_KEY_LINES = ('TRIM (orange)  = data not plotted or used for calculations',
                  'IGNORED (grey) = data plotted but not used for calculations',
                  )
# The key above the OD table, its '=' signs lined up in the same way.
OD_KEY_LINES = ('OD          = measured OD of the sample',
                'Volume (mL) = total volume of cells spun down',
                'Dilution    = any dilution factor after additions',
                )
HAEM_NUDGE = ('Change the fit, the scatter or the spectra in the Haem decomposition '
              'box above the plot; press Continue when the haems look right.')
PSI_NUDGE = ('Type the numbers in the Δψ box above the plot; press Continue when Δψ '
             'looks right.')
TRIM_NUDGE = ('Type the times in the Time regions box above the plot, or drag the '
              'bars; press Continue when every experiment looks right.')
# The boxes of the regions step, in the order of redox_regions.REGION_KEYS.
REGION_FIELDS = [('oxidised_start', 'Oxidised from'),
                 ('oxidised_end', 'to'),
                 ('reduced_start', 'Reduced from'),
                 ('reduced_end', 'to'),
                 ]
REGION_KEY_TEXT = 'red = oxidised region, blue = reduced region'
# The key above the regions question, its '=' signs lined up as the trim key's.
REGION_KEY_LINES = ("OXIDISED (red) = haems fully oxidised: each haem's level here is "
                    '100 %',
                    "REDUCED (blue) = haems fully reduced: each haem's level here is "
                    '0 %',
                    )
REGION_NUDGE = ('Type the times in the Time regions box above the plot, or drag the '
                'regions out on the plot; press Continue when every experiment looks '
                'right.')
# The boxes of the window step, and its tick box (averaging.WINDOW_KEYS): the settled
# windows only. The quick windows are hidden for now; their boxes and tick box stay
# here for when they come back.
WINDOW_FIELDS = [('window_s', 'Region length (s)'),
                 ('gap_s', 'Time before next addition (s)'),
                 ]
WINDOW_SWITCH = ('is_on', 'Averaging regions')
QUICK_FIELDS = [('quick_s', 'Quick region'), ('delay_s', 'Start after the addition')]
QUICK_SWITCH = ('quick_is_on', 'Quick regions')
# the toggle under the Use ticks: while on, only the window picked beside it changes,
# on the file shown
WINDOW_OPTIONS = [('each_is_on', 'Adjust region manually')]
WINDOW_KEY_TEXT = ('gold = baseline, blue = averaging region, grey = left out or not '
                   'picked, red hatched = a region that does not fit')
FIGURE_NUDGE = ('Change the figure in the boxes above the plot, or the order of the '
                'panels with the arrows; click Export when it looks right.')
# The answers of the Export step (5.9): the summary is the plot and the workbook of each
# file; the csv files are the spectra, of the trimmed data and of the whole recording
# of each trimmed file ('full', offered only when a file is trimmed).
EXPORT_CHOICES = (('summary', 'Export the summary'),
                  ('trimmed', 'Export the summary and the trimmed csv'),
                  ('full', 'Export the summary and the trimmed and full csv'),
                  )
PAGE_NUDGE = ('Build the figure on the page on the right; click Continue when it is '
              'ready.')
SETUP_NUDGE = ('Fill in the table on the right; click Continue when it says which '
               'experiment is which.')
WINDOW_NUDGE = ('Type the numbers of the averaging regions in the Time regions box '
                'above the plot, or drag the edges of a region; press Continue when '
                'the regions look right.')


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
                        number='4.1.7',
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
                              number='4.1.7',
                              ).strip()
    return names


# ---- _box_edit_runner ----------------------------------------------------------------
def _box_edit_runner(session: ViewerSession,
                     answers: dict,
                     state: dict,
                     name: str,
                     exporter: Callable[[Dict[str, dict], bool], None],
                     ) -> None:
    """
    ---- Summary ----
    Helper function to carry out a click on Edit ODs or Edit labels in the View box, or
    on an export button of the trim step opened again: the OD table or the labels table
    opens while the question waits and the plot is redrawn after Confirm; an export
    button writes the files with the trim and ignore edges as they are (those on the
    plot while Trim / Ignore is pressed). Before the values exist, one line says where
    they are typed.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers so far (normalise_od, changed after Edit ODs).
    state : dict
        The run so far (viewer_asker): limits and details; the details are changed in
        place.
    name : str
        EDIT_ODS_CHANGE, EDIT_LABELS_CHANGE, EXPORT_FULL_CHANGE or
        EXPORT_TRIMMED_CHANGE.
    exporter : Callable[[Dict[str, dict], bool], None]
        Asks about the spectra and writes the export, given the limits and whether
        the whole recording of each trimmed file is written too.

    ---- Globals read ----
    EDIT_LABELS_CHANGE, EDIT_ODS_CHANGE, EXPORT_FULL_CHANGE, EXPORT_TRIMMED_CHANGE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes the details, and after Edit ODs normalise_od in ``answers`` (True
    once every OD value is in) and the session's has_od; reads from and prints to the
    terminal, writes the export and redraws the plot (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_table_filler
    _od_gaps_teller
    _od_lister
    _od_table_filler
    _strip_shower
    event_asker
    info_printer
    od_gaps_finder
    trim_limits_builder
    """

    # ---- 1 The export buttons --------------------------------------------------------
    if name in (EXPORT_FULL_CHANGE, EXPORT_TRIMMED_CHANGE):
        with_full = name == EXPORT_FULL_CHANGE
        if session.time_tab == 'trim':
            exporter(trim_limits_builder(session.summaries,
                                         session.window.edges_reader(),
                                         ),
                     with_full,
                     )
        elif state.get('limits'):
            exporter(state['limits'], with_full)
        return

    # ---- 2 The OD table and the labels table -----------------------------------------
    details = state.get('details')
    if details is None:
        info_printer('The OD values and the event labels are typed in the set-up; they '
                     'can be edited here once they are.',
                     )
        return
    if name == EDIT_ODS_CHANGE:
        rows ={summary['name']: {'OD': details[summary['name']].get('OD'),
                                 'volume': details[summary['name']].get('volume'),
                                 'dilution_factor': details[summary['name']].get('dilution_factor',
                                                                                 ) or 1.0,
                                 }
                for summary in session.summaries
                }
        for file_name, values in _od_table_filler(session, rows, False).items():
            details[file_name].update(values)
        _od_lister(details)
        _od_gaps_teller(details)
        # the per OD boxes come once every value is in, and go while one is missing
        answers['normalise_od'] = not od_gaps_finder(details)
        session.has_od = answers['normalise_od']
        _strip_shower(session, answers)
    elif name == EDIT_LABELS_CHANGE:
        if not any(summary['events'] for summary in session.summaries):
            info_printer('None of the files has an event, so there are no labels.')
            return
        saved = {file_name: {'events': own.get('events', [])}
                 for file_name, own in details.items()
                 }
        filler = lambda entries: _label_table_filler(session, entries, False)
        for file_name, events in event_asker(session.summaries,
                                             saved,
                                             filler,
                                             ).items():
            details[file_name]['events'] = events
    if session.redraw is not None:
        session.redraw()


# ---- _export_sizes_teller ------------------------------------------------------------
def _export_sizes_teller(session: ViewerSession,
                         limits: Dict[str, dict],
                         ) -> Tuple[str, str, str]:
    """
    ---- Summary ----
    Helper function to put in words how large the files of an export would be for
    these files: the workbooks, the spectra of the trimmed data and those of the whole
    recording of the trimmed files.

    ---- Inputs ----
    session : ViewerSession
        The browser session (the file summaries).
    limits : Dict[str, dict]
        Trim and ignore limits of every file.

    ---- Globals read ----
    settings.SPECTRA_CSV_BYTES, settings.WORKBOOK_POINT_BYTES.

    ---- Outputs ----
    Tuple[str, str, str]
        ('about 0.9 MB' or the like, for the workbooks, the trimmed spectra and the
        whole recordings' spectra), from size_describer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See workbook_size_estimator and spectra_size_estimator.

    ---- Helpers ----
    size_describer
    spectra_size_estimator
    workbook_size_estimator
    """

    sheets = workbook_size_estimator(session.summaries,
                                     limits,
                                     settings.WORKBOOK_POINT_BYTES,
                                     )[0]
    trimmed, full = spectra_size_estimator(session.summaries,
                                           limits,
                                           settings.SPECTRA_CSV_BYTES,
                                           )
    return size_describer(sheets), size_describer(trimmed), size_describer(full)


# ---- _export_chooser -----------------------------------------------------------------
def _export_chooser(session: ViewerSession,
                    answers: dict,
                    defaults: dict,
                    limits: Dict[str, dict],
                    details: Dict[str, dict],
                    ) -> None:
    """
    ---- Summary ----
    Helper function to ask the Export step (5.9) once the figures are finalised: the
    summary (the plot and the workbook of each file, always written), with the spectra
    csv files of the trimmed data, or with those and the whole recording's too (only
    offered when a file is trimmed), each with its size. The whole recordings' csv
    files are written at once, but not those the quick export of the trim step wrote
    already; the plots, the workbooks and the trimmed csv files are written after
    (main.experiment_files_saver).

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, results folder, the whole recordings written).
    answers : dict
        Answers dictionary; export_choice and export_spectra are stored in it.
    defaults : dict
        Default answers; export_choice is the one highlighted.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    EXPORT_CHOICES, WARNING_COLOUR (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Asks in the terminal, writes the csv files of the whole recordings and
    stores the answers in ``answers`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_sizes_teller
    choice_asker
    import_data_exporter
    info_printer
    progress_clearer
    progress_printer
    text_colourer
    """

    # ---- 1 Ask what to export, with the size of each part ----------------------------
    guide_step_starter('export')
    sheets, trimmed, full = _export_sizes_teller(session, limits)
    is_any_trimmed = any((own.get('trim_start') is not None or
                          own.get('trim_end') is not None
                          )
                         for own in limits.values()
                         )
    info_printer(f'The summary is the plot and the workbook of each file ({sheets}). '
                 f'The csv files are the spectra: large (the trimmed {trimmed}'
                 + (f', the full {full}' if is_any_trimmed else '')
                 + '), and they take a while to write.',
                 )
    options = [(key, words)
               for key, words in EXPORT_CHOICES
               if key != 'full' or is_any_trimmed
               ]
    default = defaults.get('export_choice')
    if default not in [key for key, _ in options]:
        default = 'summary'
    choice = choice_asker('What do you want to export?',
                          options,
                          default,
                          number='5.9',
                          )
    answers['export_choice'] = choice
    answers['export_spectra'] = choice != 'summary'

    # ---- 2 Write the whole recordings' csv files -------------------------------------
    if choice != 'full':
        return
    problems = import_data_exporter(
        session,
        limits,
        details,
        'full_only',
        keep_full=True,
        progress=lambda n, total: progress_printer(f'Writing the full csv files of file '
                                                   f'{n} of {total} ...',
                                                   ),
    )
    progress_clearer()
    for problem in problems:
        info_printer(text_colourer(f'Not exported: {problem}', WARNING_COLOUR), depth=2)


# ---- _quick_exporter -----------------------------------------------------------------
def _quick_exporter(session: ViewerSession,
                    limits: Dict[str, dict],
                    details: Dict[str, dict],
                    with_full: bool,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to write the spectra of each file as csv files now, from one of the
    two export buttons of the trim step: those of the trimmed data, with those of the
    whole recording of each trimmed file too from "Export full + trimmed csv". No
    workbook is written and nothing is asked; one line gives the size first. The
    choice and the limits exported are kept in the session; the guide stays where it
    is.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file, as entered so far.
    with_full : bool
        True to write the whole recording of each trimmed file too.

    ---- Globals read ----
    WARNING_COLOUR (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal, writes the csv files and sets
    session.export_choice and session.export_limits (side effects).

    ---- Equations ----
    Size = the trimmed spectra, + the whole recordings' spectra with ``with_full``.

    ---- Helpers ----
    _export_sizes_teller
    import_data_exporter
    info_printer
    progress_clearer
    progress_printer
    text_colourer
    """

    # ---- 1 Say how large it is -------------------------------------------------------
    _, trimmed, full = _export_sizes_teller(session, limits)
    is_any_trimmed = any((own.get('trim_start') is not None or
                          own.get('trim_end') is not None
                          )
                         for own in limits.values()
                         )
    if with_full and not is_any_trimmed:
        info_printer('No file is trimmed, so this writes the same as Export trimmed '
                     'csv.',
                     )
    sizes = f'the trimmed {trimmed}' + (f', the full {full}'
                                        if with_full and is_any_trimmed
                                        else ''
                                        )
    info_printer(f'Writing the spectra of each file as csv files ({sizes}); this '
                 'takes a while.',
                 )
    choice = 'full' if with_full else 'trimmed'

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
    full_text = ('; those of the whole recording of a trimmed file are in the full '
                 'folder inside its own'
                 if with_full and is_any_trimmed
                 else ''
                 )
    info_printer(
        f'Exported the spectra of {len(session.summaries) - len(problems)} file(s) to '
        f'{session.export_root}, one folder each{full_text}. The ignored parts are '
        f'included. The plot and the workbook of each file are written at Export, '
        f'after Finalise figures.',
        depth=2,
        )


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
    oxidised only when a file has both regions (delta D otherwise). The oxygen and the
    OCR are always plotted, and every haem of the fit in use while the Haem
    decomposition box is ticked. How the haems and the OCR are shown, the angle of the
    labels, the journal and the size are left as the answers hold them, which the boxes
    above the plot may have changed.

    ---- Inputs ----
    answers : dict
        Answers dictionary the figure settings are stored in; must hold normalise_od,
        decompose, averaging, ocr_mode, haem_mode and haem_per_od.
    defaults : dict
        The standard or saved answers (event_label_angle, when the answers have none).
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
    # The per OD box of the haems keeps its tick while they are in % oxidised, which
    # has no per OD, so it is as it was when they go back to delta D.
    # The oxygen and the OCR are always in the figure, and every haem of the fit while
    # the haems are shown; the angle of the labels is the one of the View box.
    answers.update({'plot_o2': True,
                    'plot_ocr': True,
                    'ocr_mode': (answers['ocr_mode']
                                 if answers['ocr_mode'] in kinds
                                 else kinds[0]
                                 ),
                    'plot_haems': has_haems,
                    'haems': haem_list,
                    'haem_mode': haem_mode,
                    'haem_per_od': bool(answers['haem_per_od'] and
                                        answers['normalise_od'],
                                        ),
                    'event_label_angle': answers.get('event_label_angle',
                                                     defaults['event_label_angle'],
                                                     ),
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
                        number='4.1.8',
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
                                      number='4.1.9',
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
                                              number='4.1.9',
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
                        is_step: bool = True,
                        ) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Helper function to have the label, the stock and the volume added (or the
    concentration in the chamber) of every event filled in in the labels table of the
    window (3.3).

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    entries : Dict[str, List[dict]]
        {file name: [event entry, ...]} to start from (event_entries_builder,
        event_entries in DATA_FORMAT.md).
    is_step : bool
        True in the set-up, the labels step of the guide; False from Edit labels,
        which leaves the guide at the step that waits.

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

    if is_step:
        guide_step_starter('labels')
    table = label_table_builder(session.summaries,
                                entries,
                                IGNORE_LABEL,
                                settings.CHAMBER_VOLUME_ML,
                                )
    values = _table_filler(session,
                           table,
                           question='Fill the table in with the details of the '
                           'additions, then press Confirm.',
                           note=f'Type {IGNORE_LABEL} as a label to not show it.',
                           number='3.3',
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


# ---- _od_gaps_teller -----------------------------------------------------------------
def _od_gaps_teller(details: Dict[str, dict]) -> None:
    """
    ---- Summary ----
    Helper function to say, once the OD table is confirmed, as a warning, which OD
    values are missing and that the OD scaling stays off until Edit ODs fills them in;
    nothing is said when every value is in.

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
    od_gaps_finder
    warning_shower
    """

    gaps = od_gaps_finder(details)
    if not gaps:
        return
    shown = ', '.join(gaps[:5],
                      ) + (f' and {len(gaps) - 5} more' if len(gaps) > 5 else '')
    warning_shower(
        f'OD values are missing for: {shown}. The OD scaling stays off until '
        f'every file has its values: Edit ODs in the View box fills them in.',
        )


# ---- _od_lister ----------------------------------------------------------------------
def _od_lister(details: Dict[str, dict]) -> None:
    """
    ---- Summary ----
    Helper function to print the OD values entered for every file in one list, so they
    can be checked; a value left empty reads "missing".

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
    def shown(value: Optional[float]) -> str:
        return 'missing' if value is None else f'{value:g}'
    for name, values in details.items():
        info_printer(f"  {name}: OD {shown(values.get('OD'))}, volume "
                     f"{shown(values.get('volume'))} mL, dilution factor "
                     f"{shown(values.get('dilution_factor'))}",
                     )


# ---- _od_table_filler ----------------------------------------------------------------
def _od_table_filler(session: ViewerSession,
                     rows: Dict[str, Dict[str, Optional[float]]],
                     is_step: bool = True,
                     ) -> Dict[str, Dict[str, Optional[float]]]:
    """
    ---- Summary ----
    Helper function to have the OD, volume and dilution of every file filled in in the
    OD table of the window (3.2.1), under the key of its columns.

    ---- Inputs ----
    session : ViewerSession
        The browser session, whose window has the table.
    rows : Dict[str, Dict[str, Optional[float]]]
        The rows to start from (od_rows, DATA_FORMAT.md); None leaves a cell empty.
    is_step : bool
        True in the set-up, the OD step of the guide; False from Edit ODs, which
        leaves the guide at the step that waits.

    ---- Globals read ----
    OD_KEY_LINES (module constant).

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
    info_printer
    od_rows_reader
    od_table_builder
    """

    if is_step:
        guide_step_starter('od_values')
    table = od_table_builder(rows)
    info_printer(OD_KEY_LINES[0])
    for line in OD_KEY_LINES[1:]:
        info_printer(line, tight=True)
    values = _table_filler(session,
                           table,
                           question='Fill in the table, then press Confirm.',
                           note='',
                           number='3.2.1',
                           )
    return od_rows_reader(table, values)


# ---- _own_fit_saver ------------------------------------------------------------------
def _own_fit_saver(session: ViewerSession,
                   answers: dict,
                   fits_folder: Path,
                   name: str,
                   ) -> None:
    """
    ---- Summary ----
    Helper function to take a click on Save fit: the haems ticked under Build a fit are
    saved as a fit file of that name in the fits folder, added to the Fit list and
    named as the fit in use, so the dataset is saved with it. The haems on the plot stay
    as they are, as the fit holds the same haems. Why it cannot be saved is said in one
    sentence, and nothing changes.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its window is told the new list of fits.
    answers : dict
        Answers so far; 'fit_file' and 'haem_files' are read and changed.
    fits_folder : Path
        Folder holding the fit .csv files.
    name : str
        The name typed beside Save fit.

    ---- Globals read ----
    OWN_HAEMS_NAME.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the fit file, changes ``answers`` and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    built_fit_saver
    fit_titles_lister
    info_printer
    problem_teller
    """

    ticked = (list(answers.get('haem_files') or [])
              if answers.get('fit_file') == OWN_HAEMS_NAME
              else []
              )
    try:
        path = built_fit_saver(fits_folder, name, ticked)
    except (ValueError, OSError) as exc:
        info_printer(problem_teller('The fit was not saved', exc))
        return
    answers.update({'fit_file': path.name, 'haem_files': []})
    session.window.strip_fits_setter(fit_titles_lister(fits_folder))
    info_printer(f'Saved the haems ticked as {path.name} in the fits folder. It is the '
                 'fit in use now, and in the Fit list from now on.',
                 )


# ---- _own_windows_teller -------------------------------------------------------------
def _own_windows_teller(each_window: Dict[str, dict]) -> str:
    """
    ---- Summary ----
    Helper function to say in plain words which averaging windows are set on their own
    and which are left out.

    ---- Inputs ----
    each_window : Dict[str, dict]
        The windows set on their own (DATA_FORMAT.md, each_window).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        'Set on their own: the baseline, settled region 2. Left out: quick region 1.',
        each part only when it has a region; '' for none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    def namer(name: str) -> str:
        if name == 'average0':
            return 'the baseline'
        if name.startswith('quick'):
            return f"quick region {name[len('quick'):]}"
        return f"settled region {name[len('average'):]}"
    own = [namer(name)
           for name, values in each_window.items()
           if any(field != 'is_used' for field in values)
           ]
    out = [namer(name)
           for name, values in each_window.items()
           if not values.get('is_used', True)
           ]
    parts = []
    if own:
        parts.append(f"Set on their own: {', '.join(own)}.")
    if out:
        parts.append(f"Left out: {', '.join(out)}.")
    return ' '.join(parts)


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
    the reduced region are dragged out on the plot or typed in the Time regions box
    above it, under the key of their colours, and Continue accepts them. With "Apply to
    all" ticked, an edge set on the file shown is copied to every file at the same
    distance from its nearest addition, or from the end when it lies after the last
    addition. A file without both regions stays in delta D. The regions are then
    listed, with the files a copy could not reach.

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
    REGION_KEY_LINES, REGION_NUDGE (module constants).

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
    _regions_choice_builder
    _regions_finisher
    _step_edges_reader
    _step_edges_shower
    enter_waiter
    guide_step_starter
    info_printer
    short_region_closer
    """

    # ---- 1 The edges of the regions of every file ------------------------------------
    choice, rules, unreached = _regions_choice_builder(session,
                                                       answers,
                                                       limits,
                                                       details,
                                                       remembered,
                                                       )

    # ---- 2 Pull out or type the regions until Continue -------------------------------
    guide_step_starter('regions')
    info_printer(REGION_KEY_LINES[0])
    info_printer(REGION_KEY_LINES[1], tight=True)
    info_printer('Ticking Apply to all copies the regions of the experiment shown to '
                 'every experiment; it unticks itself when the next one is shown.',
                 )
    info_printer('With no regions the haems cannot be shown in % oxidised; everything '
                 'else is the same.',
                 tight=True,
                 )
    _step_edges_shower(session, 'regions', choice)
    # While the edges are on the plot they are the regions being chosen, so a click on
    # Keep old leaves the regions alone.
    session.is_choosing_regions = True
    try:
        enter_waiter('Drag the regions out on the plot, or type the times in the Time '
                     'regions box. Check each experiment, then press Continue.',
                     REGION_NUDGE,
                     number='4.4',
                     )
        values = {name: short_region_closer(own, rules[name]['minimum_min'])
                  for name, own in session.window.edges_reader().items()
                  }
    finally:
        session.is_choosing_regions = False
        _step_edges_reader(session)

    # ---- 3 List the regions ----------------------------------------------------------
    return _regions_finisher(session, values, rules, unreached)


# ---- _regions_choice_builder ---------------------------------------------------------
def _regions_choice_builder(
    session: ViewerSession,
    answers: dict,
    limits: Dict[str, dict],
    details: Dict[str, dict],
    remembered: Optional[Dict[str, Dict[str, float]]],
    ) -> Tuple[EdgeChoice, Dict[str, dict], Dict[str, Set[str]]]:
    """
    ---- Summary ----
    Helper function to build the edges of the oxidised and reduced regions of every
    file, as _regions_chooser describes them, starting where they were left.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers so far; decomposition_dataset names the spectra the haems come from.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file; an edge is copied by the additions not
        ignored there.
    remembered : Optional[Dict[str, Dict[str, float]]]
        The regions to start at, as times on the original recording (min); None, or a
        file missing, for regions not chosen.

    ---- Globals read ----
    REGION_FIELDS, REGION_KEY_TEXT, REGION_KEYS (module constants).

    ---- Outputs ----
    Tuple[EdgeChoice, Dict[str, dict], Dict[str, Set[str]]]
        (the edges, the rules of each file from _region_rules_lister, the edges of each
        file a copy could not reach, filled in as the user copies).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time on the plot = time on the recording - trim start. A copied edge after the
    last addition: end of the other file - (end - edge), the ends being those of the
    used parts on the plot.

    ---- Helpers ----
    _addition_time_lister
    _region_rules_lister
    region_edge_copier
    region_edge_setter
    region_edges_builder
    region_layout_finder
    region_pointer_reader
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
        copied = region_edge_copier(value,
                                    additions[shown],
                                    additions[name],
                                    rules[shown]['used_span'][1],
                                    rules[name]['used_span'][1],
                                    )
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
    return choice, rules, unreached


# ---- _regions_finisher ---------------------------------------------------------------
def _regions_finisher(session: ViewerSession,
                      values: Dict[str, Dict[str, float]],
                      rules: Dict[str, dict],
                      unreached: Dict[str, Set[str]],
                      ) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Helper function to list the regions read from the edges, with the files a copy
    could not reach, and give them as times on the original recording.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    values : Dict[str, Dict[str, float]]
        {file name: region edges on the plot (min)}, short regions already closed.
    rules : Dict[str, dict]
        The rules of each file (_regions_choice_builder), with its trim shift.
    unreached : Dict[str, Set[str]]
        The edges of each file a copy could not reach.

    ---- Globals read ----
    REGION_KEYS (module constant).

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
        times on the original recording (min).

    ---- Globals mutated ----
    None. Prints (side effect).

    ---- Equations ----
    time on the recording = time on the plot + trim start.

    ---- Helpers ----
    _regions_lister
    """

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
                       'file alone, with "Apply to all" unticked.',
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
        return ('The Haem decomposition box is set back to what is in use.'
                if is_from_strip
                else text
                )
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


# ---- _step_edges_reader --------------------------------------------------------------
def _step_edges_reader(session: ViewerSession) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Helper function to read the edges of the step that waited, once it is answered,
    and take them off the plot: the Time regions box then has no tab pressed.

    ---- Inputs ----
    session : ViewerSession
        The browser session, with the step's edges on the plot.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        {file name: {field: value}} as the window gives them (edges_reader).

    ---- Globals mutated ----
    None. Hides the edges and changes the session (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        edges = session.window.edges_reader()
    finally:
        session.window.edges_hider()
        session.step_tab = session.time_tab = ''
        session.step_choice = session.step_redraw = None
        session.window.strip_setter({'time_tab': ''})
    return edges


# ---- _step_edges_shower --------------------------------------------------------------
def _step_edges_shower(session: ViewerSession, tab: str, choice: EdgeChoice) -> None:
    """
    ---- Summary ----
    Helper function to put the edges of the step the program now waits at on the plot,
    and press its tab in the Time regions box. Another tab pressed meanwhile takes them
    off and puts them back as they were left (_tab_switcher).

    ---- Inputs ----
    session : ViewerSession
        The browser session, with the step's plot drawn and its redraw set.
    tab : str
        'trim', 'regions' or 'windows'.
    choice : EdgeChoice
        The edges of the step.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Shows the edges and changes the session (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    session.step_tab = session.time_tab = tab
    session.step_choice = choice
    session.step_redraw = session.redraw
    session.window.edges_shower(choice)
    session.window.strip_setter({'time_tab': tab})


# ---- _tab_kits_builder ---------------------------------------------------------------
def _tab_kits_builder(session: ViewerSession,
                      answers: dict,
                      state: dict,
                      keep_limits: Callable[[Dict[str, dict]], Dict[str, dict]],
                      ) -> Dict[str, Tuple[Callable[[], Optional[EdgeChoice]],
                                           Callable[[Dict[str, Dict[str, float]]],
                                                    None,
                                                    ],
                                           ]]:
    """
    ---- Summary ----
    Helper function to give each tab of the Time regions box what it does when it is
    pressed away from its own step: the plot it draws and its edges, and what is done
    with the edges once another tab is pressed or a question is answered. Trim /
    Ignore draws the whole recording with the edges in use (and those as red dashed
    lines) and keeps the new trim and ignore limits; Ox / Red and Averaging draw the
    processing plot and keep the regions or the averaging windows.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers so far; the windows and the regions' spectrometer are read from them,
        and the windows stored in them.
    state : dict
        The run so far (viewer_asker): limits, details and regions.
    keep_limits : Callable[[Dict[str, dict]], Dict[str, dict]]
        Keeps new trim and ignore limits as the run's limits.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Tuple[Callable[[], Optional[EdgeChoice]], Callable[[Dict[str, Dict[str, float]]], None]]]
        {tab: (opener, applier)} for _tab_switcher.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _limits_lister
    _regions_choice_builder
    _regions_finisher
    _strip_shower
    _trim_choice_builder
    _windows_choice_builder
    _windows_keeper
    preview_drawer
    short_region_closer
    trim_limits_builder
    """

    kept: dict = {}
    def processing_plot() -> bool:
        return preview_drawer(session,
                              _answers_previewer(dict(answers, averaging=False),
                                                 session.fit,
                                                 'analysis',
                                                 session.has_od,
                                                 ),
                              state.get('limits') or {},
                              session.fit,
                              state.get('details') or {},
                              )

    # ---- open_trim -------------------------------------------------------------------
    def open_trim() -> Optional[EdgeChoice]:
        def whole() -> bool:
            return preview_drawer(session,
                                  _answers_previewer(answers,
                                                     session.fit,
                                                     'standard',
                                                     session.has_od,
                                                     ),
                                  {},
                                  session.fit,
                                  {},
                                  show_trim=True,
                                  )
        session.redraw = whole
        whole()
        limits = state.get('limits') or {}
        return _trim_choice_builder(session, limits, limits)
    def apply_trim(edges: Dict[str, Dict[str, float]]) -> None:
        limits = trim_limits_builder(session.summaries, edges)
        _limits_lister(session.summaries, limits)
        keep_limits(limits)

    # ---- open_regions ----------------------------------------------------------------
    def open_regions() -> Optional[EdgeChoice]:
        session.redraw = processing_plot
        processing_plot()
        choice, rules, unreached = _regions_choice_builder(session,
                                                           answers,
                                                           state.get('limits') or {},
                                                           state.get('details') or {},
                                                           session.regions,
                                                           )
        kept['regions'] = (rules, unreached)
        session.is_choosing_regions = True
        return choice
    def apply_regions(edges: Dict[str, Dict[str, float]]) -> None:
        session.is_choosing_regions = False
        rules, unreached = kept['regions']
        values = {name: short_region_closer(own, rules[name]['minimum_min'])
                  for name, own in edges.items()
                  }
        session.regions = state['regions'] = _regions_finisher(session,
                                                               values,
                                                               rules,
                                                               unreached,
                                                               )
        _strip_shower(session, answers)

    # ---- 3 Averaging -----------------------------------------------------------------
    # With neither kind kept, the settled windows are the ones ticked.
    def open_windows() -> Optional[EdgeChoice]:
        is_any = answers['settled_windows'] or answers['quick_windows']
        built = _windows_choice_builder(session,
                                        answers,
                                        dict(answers,
                                             averaging=True,
                                             settled_windows=(answers['settled_windows']
                                                              or not is_any
                                                              ),
                                             ),
                                        state.get('limits') or {},
                                        state.get('details') or {},
                                        )
        if built is None:
            return None
        session.redraw = processing_plot
        processing_plot()
        kept['windows'] = built[1]
        return built[0]
    def apply_windows(edges: Dict[str, Dict[str, float]]) -> None:
        _windows_keeper(session, answers, edges, kept['windows'])
        session.has_windows = bool(answers['averaging'])
        _strip_shower(session, answers)

    return {'trim': (open_trim, apply_trim),
            'regions': (open_regions, apply_regions),
            'windows': (open_windows, apply_windows),
            }


# ---- _tab_switcher -------------------------------------------------------------------
def _tab_switcher(session: ViewerSession,
                  kits: Dict[str, Tuple[Callable[[], Optional[EdgeChoice]],
                                        Callable[[Dict[str, Dict[str, float]]], None],
                                        ]],
                  tab: str,
                  ) -> None:
    """
    ---- Summary ----
    Helper function to put the edges of another tab of the Time regions box on the
    plot. The edges on the plot are taken off first: those of the step that waits are
    kept as they were left, to come back when its tab is pressed again; those of
    another tab are used at once (the trim, the regions or the windows change). An
    empty tab goes back to the step that waits, or to no edges, and its plot.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    kits : Dict[str, Tuple[Callable[[], Optional[EdgeChoice]], Callable[[Dict[str, Dict[str, float]]], None]]]
        {tab: (opener, applier)}: the opener draws the tab's plot and gives its edges
        (None when it has none, having said why); the applier uses the edges read.
    tab : str
        '', 'trim', 'regions' or 'windows'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Shows and hides the edges, redraws the plot and changes the session (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Take the edges on the plot off --------------------------------------------
    # The plot of the question that waits without edges comes back after another tab.
    window = session.window
    current = session.time_tab
    if tab == current:
        return
    if not current:
        session.base_redraw = session.redraw
    if current:
        edges = window.edges_reader()
        window.edges_hider()
        if current == session.step_tab:
            session.step_choice.values = edges
        else:
            kits[current][1](edges)

    # ---- 2 Put the new ones on -------------------------------------------------------
    if tab and tab == session.step_tab:
        session.redraw = session.step_redraw
        if session.redraw is not None:
            session.redraw()
        window.edges_shower(session.step_choice)
    elif tab:
        choice = kits[tab][0]()
        if choice is None:
            tab = ''
        else:
            window.edges_shower(choice)
    if not tab and session.step_tab:
        # no other tab: the step that waits keeps its edges on the plot
        tab = session.step_tab
        session.redraw = session.step_redraw
        if session.redraw is not None:
            session.redraw()
        window.edges_shower(session.step_choice)
    elif not tab and current:
        session.redraw = session.base_redraw
        if session.redraw is not None:
            session.redraw()
    session.time_tab = tab
    window.strip_setter({'time_tab': tab})


# ---- _trim_choice_builder ------------------------------------------------------------
def _trim_choice_builder(session: ViewerSession,
                         remembered: Dict[str, dict],
                         previous: Optional[Dict[str, dict]] = None,
                         ) -> EdgeChoice:
    """
    ---- Summary ----
    Helper function to build the trimmed and ignored edges of every file, starting
    where they were left, with earlier limits drawn as red dashed lines.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    remembered : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} the edges start
        at.
    previous : Optional[Dict[str, dict]]
        Limits in the same layout drawn as red dashed lines; None for none.

    ---- Globals read ----
    TRIM_FIELDS, TRIM_KEY_TEXT (module constants).

    ---- Outputs ----
    EdgeChoice
        The edges.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    trim_layout_finder
    trim_minutes_builder
    trim_minutes_setter
    trim_pointer_reader
    trim_times_finder
    EdgeChoice
    """

    by_name = {s['name']: s for s in session.summaries}
    return EdgeChoice(fields=list(TRIM_FIELDS),
                      values=trim_minutes_builder(session.summaries, remembered),
                      layout_finder=lambda name, minutes: (
                          trim_layout_finder(by_name[name], minutes)),
                      pointer_reader=lambda name, minutes, key, time_min: (
                          trim_pointer_reader(by_name[name], minutes, key, time_min)),
                      value_setter=lambda name, minutes, key, value: (
                          trim_minutes_setter(by_name[name], minutes, key, value)),
                      key_text=TRIM_KEY_TEXT,
                      previous=(trim_minutes_builder(session.summaries, previous)
                                if previous
                                else {}
                                ),
                      # the boxes show and take times on the whole recording
                      shown_maker=lambda name, minutes: (
                          trim_times_finder(by_name[name], minutes)),
                      typed_reader=lambda name, minutes, key, time_min: (
                          trim_pointer_reader(by_name[name], minutes, key, time_min)),
                      )


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
    the fit, the background, the regions and the numbers of Δψ in use, shown as a plot
    of its own on the left or drawn dashed over the haems and over Δψ (the switch
    beside Keep new, kept in the answers), until one of the two is chosen (Keep new
    carries on with what is on the plot, Keep old puts the kept one back in use) or
    the haems are left out. The switch under the boxes shows the difference spectrum
    of each file with both regions in place of the standard plot, or the standard
    plot again, kept in the answers. A click on Save fit saves the haems ticked under Build a fit as a fit file of
    the name typed beside it. A click on Do PCA asks the questions that find the
    components from the data while the haem step waits, and says where to go
    otherwise. A new journal, width or height redraws only the figure
    of each file, the one plot drawn at its size. A click on Export master saves the
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
    COMPARE_LAYOUT_WORDS, LABEL_CHANGE_TEXTS.

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
    _own_fit_saver
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

    # ---- 0 The clicks: the master page, a tab, the tables and the export buttons -----
    if changes.get(MASTER_CHANGE):
        if session.is_figure and session.master_exporter is not None:
            session.master_exporter()
        else:
            info_printer('The master page shows the figure of a file on a page of the '
                         'journal, so it can be exported once that figure is on the '
                         'plot, in the individual experiment plots.',
                         )
        return
    if TIME_TAB_CHANGE in changes:
        if session.tab_switcher is not None:
            session.tab_switcher(changes[TIME_TAB_CHANGE])
        else:
            session.window.strip_setter({TIME_TAB_CHANGE: session.time_tab})
        return
    for name in (EDIT_ODS_CHANGE,
                 EDIT_LABELS_CHANGE,
                 EXPORT_FULL_CHANGE,
                 EXPORT_TRIMMED_CHANGE,
                 ):
        if changes.get(name):
            if session.edit_runner is not None:
                session.edit_runner(name)
            return
    if SAVE_FIT_CHANGE in changes:
        _own_fit_saver(session, answers, fits_folder, str(changes[SAVE_FIT_CHANGE]))
        _strip_shower(session, answers)
        return
    if changes.get(PCA_CHANGE):
        if session.pca_runner is not None:
            session.pca_runner()
        else:
            info_printer('The components are found from the data in the haem step '
                         '(4.1): go back to the processing to do it.',
                         )
        return

    # ---- 1 The journal, the width and the height -------------------------------------
    sizes = size_answers_builder(changes)
    answers.update(sizes)
    is_redrawn = bool(sizes) and session.is_figure

    # ---- 2 The background under the haems --------------------------------------------
    if 'haem_background' in changes:
        answers['haem_background'] = changes['haem_background']
        info_printer('The scatter (the background under the haems) is now '
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
    if 'event_label_angle' in changes:
        info_printer('The event labels are now written at '
                     f"{changes['event_label_angle']:g}°.",
                     )
    is_redrawn = is_redrawn or bool(forms)

    # ---- 2.0 Delta psi switched on or off in its box ---------------------------------
    if 'delta_psi' in changes and changes['delta_psi'] != bool(answers['delta_psi']):
        answers['delta_psi'] = bool(changes['delta_psi'])
        info_printer('Δψ is now worked out, in its own panel.'
                     if answers['delta_psi']
                     else 'Δψ is left out: tick it in its box to work it out again.',
                     )
        is_redrawn = True

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
        layout = answers.get('compare_layout',
                             settings.DEFAULT_ANSWERS['compare_layout'],
                             )
        session.kept = in_use if changes['compare'] else None
        info_printer(f"Kept {in_use['text']} to compare: change the haems, the "
                     'scatter, the regions or the Δψ numbers, and '
                     f"{COMPARE_LAYOUT_WORDS[layout]}. Then click "
                     'Keep new to carry on with the change, or Keep old to undo it.'
                     if changes['compare']
                     else f"Carrying on with {in_use['text']}. The one kept to "
                          'compare is no longer shown.',
                     )
        is_redrawn = True
    elif changes.get('compare'):
        info_printer('There are no haems worked out yet to keep: they are worked out '
                     'in the processing.',
                     )

    # ---- 4.1 The kept decomposition beside the plot or over it -----------------------
    if 'compare_layout' in changes:
        answers['compare_layout'] = changes['compare_layout']
        info_printer(f"Now {COMPARE_LAYOUT_WORDS[answers['compare_layout']]}.")
        is_redrawn = is_redrawn or session.kept is not None

    # ---- 4.2 The standard plot or the difference spectrum ----------------------------
    if 'difference_spectra' in changes:
        answers['difference_spectra'] = bool(changes['difference_spectra'])
        info_printer('The plot now shows the difference spectrum of each file with '
                     'both regions: reduced minus oxidised, with each haem, the fit '
                     'and the residual.'
                     if answers['difference_spectra']
                     else 'The plot shows the standard plot again.',
                     )
        is_redrawn = True

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
    when at least one file has both regions, per OD when every OD value was entered,
    Edit ODs once scaling by OD was chosen, the OCR as % of baseline once the
    averaging windows are set up (session.has_windows), and the files whose difference
    spectrum the switch under the boxes can show. Haems in % oxidised go back to delta D when no file has
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
    region_files = region_files_lister(session.summaries,
                                       session.limits,
                                       session.regions,
                                       answers.get('decomposition_dataset'),
                                       )
    has_percent = bool(region_files)
    if answers['haem_mode'] == 'percent' and not has_percent:
        answers['haem_mode'] = 'delta'
    has_psi = (session.fit is not None and
               delta_psi_offer_checker(list(session.fit['haem_list']), region_files)
               )
    session.window.strip_choices_setter(sorted(common),
                                        has_percent,
                                        session.has_od,
                                        session.has_windows,
                                        has_psi,
                                        region_files,
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
    waiting. A table left for another step (opened from the View box) is taken as it
    is, its wrong cells read as empty. The table is then taken away.

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
        # a table left for another step is taken as it is
        if window.table_leave_taker() is True:
            return None
        return table_problem_teller(window.table_reader()[1])
    try:
        confirm_waiter(question, table_checker, note=note, number=number)
        return window.table_reader()[0]
    finally:
        window.table_hider()


# ---- _template_offer_asker -----------------------------------------------------------
def _template_offer_asker(page: FigurePage,
                          kept: FigurePage,
                          layouts_folder: Path,
                          ) -> Optional[Path]:
    """
    ---- Summary ----
    Helper function to offer, once the page of a dataset figure is built, to save it
    as a template for another dataset, and to save it under the name typed. Nothing
    is asked for a page with no plot, or one already saved as a template or loaded
    from one and not changed since. A template of the same name is written over only
    after asking.

    ---- Inputs ----
    page : FigurePage
        The page as built.
    kept : FigurePage
        The page as it was last saved as a template, loaded from one, or started.
    layouts_folder : Path
        The layouts folder, where templates are saved.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Path]
        The template file written, or None when nothing was saved.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and writes the template file; the
    details of a problem go to the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    page_offer_checker
    problem_teller
    template_path_finder
    template_saver
    text_asker
    yes_no_asker
    """

    if not page_offer_checker(page, kept):
        return None
    if not yes_no_asker('Do you want to save this page as a template, to load it for '
                        'another dataset?',
                        False,
                        number='6.3',
                        ):
        return None
    def name_checker(text: Optional[str]) -> Optional[str]:
        return None if (text or '').strip() else 'Type a name for the template.'
    while True:
        name = text_asker('What should the template be called?',
                          checker=name_checker,
                          number='6.4',
                          ).strip()
        path = template_path_finder(layouts_folder, name)
        if path.exists() and not yes_no_asker(f'A template called {path.stem} is '
                                              f'already there. Do you want to replace '
                                              f'it?',
                                              False,
                                              number='6.5',
                                              ):
            continue
        try:
            saved = template_saver(page, layouts_folder, name, may_replace=True)
        except FigurePageError as exc:  # its message is one plain sentence
            info_printer(str(exc))
            return None
        except OSError as exc:
            info_printer(problem_teller('The template could not be saved', exc))
            return None
        info_printer(f'Saved the template {saved.stem} in {layouts_folder}. It is in '
                     f'the list beside Load template from now on.',
                     )
        return saved


# ---- _unfit_windows_lister -----------------------------------------------------------
def _unfit_windows_lister(spans: List[Tuple[str, float, float, Optional[str]]],
                          quick: List[Tuple[str, float, float, Optional[str]]],
                          ) -> List[str]:
    """
    ---- Summary ----
    Helper function to name, in plain words, the averaging windows of one file that do
    not fit; those left out with their tick are not named.

    ---- Inputs ----
    spans : List[Tuple[str, float, float, Optional[str]]]
        The baseline and the settled windows of the file, as window_span_lister gives
        them (the baseline alone when there are no settled windows).
    quick : List[Tuple[str, float, float, Optional[str]]]
        The quick windows of the file, as quick_span_lister gives them; empty when
        there are none.

    ---- Globals read ----
    LEFT_OUT_PROBLEM (imported).

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
        if problem is None or problem == LEFT_OUT_PROBLEM:
            continue
        if index == 0:
            names.append('the baseline before addition 1')
        elif index == len(spans) - 1:
            names.append('the settled one after the last addition')
        else:
            names.append(f'the settled one before addition {index + 1}')
    names += [f'the quick one after addition {index}'
              for index, (_, _, _, problem) in enumerate(quick, start=1)
              if problem is not None and problem != LEFT_OUT_PROBLEM
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
    with its name. The windows (blue) have a length and a time before the next
    addition: pulling the start of any of them changes the length, pulling its end the
    time before the addition, and pulling the end of the last one how long before the
    end of the file it ends. A change moves every window, on every file while Apply to
    all is ticked, otherwise on the file shown. With Adjust region manually ticked,
    one window picked with the buttons beside it changes, on the file shown only; the
    others are grey and have no edges, and Apply to all is greyed. The two values are
    also typed in the Time regions box, under its Averaging windows tick box (unticked
    there are no windows) and a numbered tick per window to leave it out (grey).
    Continue accepts. The windows that do not fit are shaded red and named in a
    warning after Continue. The quick windows are hidden for now. When no file has an
    addition, nothing is asked and nothing is averaged.

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
    WINDOW_NUDGE (module constant); settings.BASELINE_MINIMUM_SECONDS,
    settings.DRAG_STEP_SECONDS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores averaging (True with either kind ticked), settled_windows,
    window_minutes, gap_minutes, final_gap_minutes, quick_windows, quick_minutes,
    delay_minutes, each_window and file_windows in ``answers`` (_windows_keeper),
    reads from and prints to the terminal and draws on the plot window (side effects).

    ---- Equations ----
    minutes = seconds / 60. The data of a file runs from 0 to (trim end - trim start)
    on the time axis of the plot.

    ---- Helpers ----
    _step_edges_reader
    _step_edges_shower
    _windows_choice_builder
    _windows_keeper
    enter_waiter
    info_printer
    """

    # ---- 1 The edges of the windows of every file ------------------------------------
    built = _windows_choice_builder(session, answers, defaults, limits, details)
    if built is None:
        return
    choice, context = built
    final_gap = context['final_gap']

    # ---- 2 Drag or type the windows until Continue -----------------------------------
    guide_step_starter('windows')
    info_printer('AVERAGING REGIONS = the stretches before each addition that its '
                 'averages are taken over.',
                 )
    info_printer('The baseline (gold) is the region before the first addition; every '
                 'other region (blue) is compared with it.',
                 tight=True,
                 )
    info_printer('Each region ends a set time before the next addition, the last one '
                 f'{final_gap * 60.0:g} s before the end of the recording. Pull the '
                 'start of a region to change its length, its end to change the time '
                 'before the addition.',
                 tight=True,
                 )
    info_printer(
        'A change moves every region, on the file shown; ticking Apply to all '
        'copies its regions to every file, and it unticks itself when the next '
        'file is shown. Untick a number under Use to leave that region out '
        '(grey), or untick Averaging regions for none.',
        tight=True,
        )
    info_printer('Tick Adjust region manually to change one region of one file: pick '
                 'it with the buttons beside it, then drag its edges or type its '
                 'numbers; the other regions are grey until picked.',
                 tight=True,
                 )
    _step_edges_shower(session, 'windows', choice)
    try:
        enter_waiter('Drag the averaging regions on the plot, or type their numbers in '
                     'the Time regions box, press Continue when ready.',
                     WINDOW_NUDGE,
                     number='4.6',
                     )
    finally:
        edges = _step_edges_reader(session)
    _windows_keeper(session, answers, edges, context)


# ---- _windows_choice_builder ---------------------------------------------------------
def _windows_choice_builder(session: ViewerSession,
                            answers: dict,
                            defaults: dict,
                            limits: Dict[str, dict],
                            details: Dict[str, dict],
                            ) -> Optional[Tuple[EdgeChoice, dict]]:
    """
    ---- Summary ----
    Helper function to build the edges of the averaging windows of every file, as
    _windows_chooser describes them, starting from the defaults. When no file has an
    addition there are none: averaging is switched off and one line says so.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers so far; final_gap_minutes is how long before the end of the recording
        the last window ends.
    defaults : dict
        Default answers the windows start with (averaging, settled_windows,
        window_minutes, gap_minutes, quick_windows, quick_minutes, delay_minutes).
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    details : Dict[str, dict]
        OD values and events of every file; the windows go around the additions not
        ignored there.

    ---- Globals read ----
    WINDOW_FIELDS, WINDOW_KEY_TEXT, WINDOW_OPTIONS, WINDOW_SWITCH (module constants);
    PICKED_KEYS (imported);
    settings.BASELINE_MINIMUM_SECONDS, settings.DRAG_STEP_SECONDS.

    ---- Outputs ----
    Optional[Tuple[EdgeChoice, dict]]
        (the edges, {additions, spans, final_gap, minimum_s} for _windows_keeper), or
        None when no file has an addition.

    ---- Globals mutated ----
    None. May switch averaging off in ``answers`` and print (side effects).

    ---- Equations ----
    minutes = seconds / 60. The data of a file runs from 0 to (trim end - trim start)
    on the time axis of the plot.

    ---- Helpers ----
    _addition_time_lister
    info_printer
    window_layout_finder
    window_pick_lister
    window_plan_finder
    window_pointer_reader
    window_row_teller
    window_shown_maker
    window_value_setter
    window_values_maker
    EdgeChoice
    """

    # ---- 1 The additions and the data of every file ----------------------------------
    additions = _addition_time_lister(session.summaries, limits, details)
    if not any(additions.values()):
        answers['averaging'] = False
        info_printer('None of the files has an addition, so there are no averaging '
                     'regions.',
                     )
        return None
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
    # Each file starts from its own windows: those of the dataset, or of the file when
    # it was fixed by hand.
    # The Averaging windows tick box is the settled windows' switch; the quick windows
    # are hidden for now, so they start off.
    is_averaging = bool(defaults['averaging'])
    known = dict(answers, **defaults)
    values = {name: window_values_maker(window_plan_finder(known, name),
                                        is_averaging,
                                        False,
                                        )
              for name in additions
              }
    choice = EdgeChoice(fields=list(WINDOW_FIELDS),
                        values=values,
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
                            window_value_setter(values,
                                                key,
                                                value,
                                                len(additions[name]),
                                                )),
                        key_text=WINDOW_KEY_TEXT,
                        unit='s',
                        switch=WINDOW_SWITCH,
                        shown_maker=lambda name, values: (
                            window_shown_maker(values, len(additions[name]))),
                        options=list(WINDOW_OPTIONS),
                        row_teller=lambda name, values: (
                            window_row_teller(values, len(additions[name]))),
                        unmarked_fields=PICKED_KEYS,
                        pick_lister=lambda name, values: (
                            window_pick_lister(values, len(additions[name]))),
                        )
    return choice, {'additions': additions,
                    'spans': spans,
                    'final_gap': final_gap,
                    'minimum_s': minimum_s,
                    }


# ---- _windows_keeper -----------------------------------------------------------------
def _windows_keeper(session: ViewerSession,
                    answers: dict,
                    chosen: Dict[str, Dict[str, float]],
                    context: dict,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to keep the averaging windows read from the edges, say what they
    are, and name in a warning those that do not fit. The windows most files share
    are the dataset's; a file whose windows differ (fixed by hand with "Apply to all"
    unticked) keeps its own.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary the windows are stored in.
    chosen : Dict[str, Dict[str, float]]
        {file name: its values in the window step} (WINDOW_KEYS, STEP_EXTRA_KEYS and
        the windows' own values); the switches of the two kinds are the same in every
        file.
    context : dict
        {additions, spans, final_gap, minimum_s} from _windows_choice_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores averaging, settled_windows, window_minutes, gap_minutes,
    final_gap_minutes, quick_windows, quick_minutes, delay_minutes, each_window and
    file_windows (DATA_FORMAT.md) in ``answers``, and prints (side effects).

    ---- Equations ----
    minutes = seconds / 60.

    ---- Helpers ----
    _own_windows_teller
    _unfit_windows_lister
    info_printer
    quick_span_lister
    warning_shower
    window_plan_reader
    window_span_lister
    """

    # ---- 1 The windows of the dataset and of each file -------------------------------
    additions, spans = context['additions'], context['spans']
    minimum_s = context['minimum_s']
    first = next(iter(chosen.values()))
    plans = {name: window_plan_reader(values) for name, values in chosen.items()}
    texts = {name: json.dumps(plan, sort_keys=True) for name, plan in plans.items()}
    shared_text = Counter(texts.values()).most_common(1)[0][0]
    shared = json.loads(shared_text)
    answers['settled_windows'] = bool(first['is_on'])
    answers['quick_windows'] = bool(first['quick_is_on'])
    answers['averaging'] = answers['settled_windows'] or answers['quick_windows']
    for key in ('window_minutes',
                'gap_minutes',
                'final_gap_minutes',
                'quick_minutes',
                'delay_minutes',
                'each_window',
                ):
        answers[key] = shared[key]
    answers['file_windows'] = {name: plans[name]
                               for name in chosen
                               if texts[name] != shared_text
                               }

    # ---- 2 What they are -------------------------------------------------------------
    if not answers['averaging']:
        info_printer('No averaging regions: nothing is averaged around the additions.')
        return
    window_s, gap_s = shared['window_minutes'] * 60.0, shared['gap_minutes'] * 60.0
    if answers['settled_windows']:
        info_printer(f'Averaging regions: {round(window_s, 2):g} s long, ending '
                     f'{round(gap_s, 2):g} s before the next addition, the last '
                     f"{round(shared['final_gap_minutes'] * 60.0, 2):g} s before the "
                     'end of the recording.',
                     )
    else:
        info_printer(f'Baseline: {round(window_s, 2):g} s long, ending '
                     f'{round(gap_s, 2):g} s before the first addition. No settled '
                     'regions.',
                     )
    if answers['quick_windows']:
        info_printer(f"Quick regions: {round(shared['quick_minutes'] * 60.0, 2):g} s "
                     f"long, starting {round(shared['delay_minutes'] * 60.0, 2):g} s "
                     'after their addition.',
                     tight=True,
                     )
    told = _own_windows_teller(shared['each_window'])
    if told:
        info_printer(told, tight=True)
    if answers['file_windows']:
        info_printer('Regions of their own (changed with Apply to all unticked): '
                     f"{', '.join(answers['file_windows'])}.",
                     tight=True,
                     )

    # ---- 3 Those that do not fit -----------------------------------------------------
    unfit = []
    for summary in session.summaries:
        name = summary['name']
        if not additions.get(name) or name not in plans:
            continue
        plan = plans[name]
        settled = window_span_lister(additions[name],
                                     spans[name],
                                     plan['window_minutes'],
                                     plan['gap_minutes'],
                                     plan['final_gap_minutes'],
                                     minimum_s,
                                     each_window=plan['each_window'],
                                     )
        quick = (quick_span_lister(additions[name],
                                   spans[name],
                                   plan['quick_minutes'],
                                   plan['delay_minutes'],
                                   plan['each_window'],
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
        warning_shower('These averaging regions do not fit (not enough time), so they '
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
    the limits: the temperature of the runs, the OD values, then the event labels, the
    OD values and the labels each in a table of the window.
    Once the OD table is confirmed, a warning names the OD values missing, the OD
    scaling staying off until Edit ODs fills them in. Once every OD value is in, the
    OCR is shown per OD, the View box shows its per OD boxes, and a line points to them
    (3.2.2).
    The plot is redrawn with the labels once they are saved; Edit labels changes them
    later. The haems are those of the session's fit.

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
        only present when scaling by OD, a value left empty being None.

    ---- Globals mutated ----
    None. Stores normalise_od and temperature_c in ``answers`` and whether scaling by
    OD was chosen and every OD value entered in the session, and shows the strip
    (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _label_table_filler
    _od_gaps_teller
    _od_lister
    _od_table_filler
    _strip_shower
    event_asker
    ocr_view_teller
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

    # ---- 2 The temperature of the runs -----------------------------------------------
    # One value for the dataset, asked of everyone: delta psi is worked out with it.
    # The Δψ box holds the same value, so the one in use (the box may have changed it)
    # is offered, and the box shows the answer.
    temperature_asker(answers, dict(defaults, temperature_c=answers['temperature_c']))
    _strip_shower(session, answers)

    # ---- 3 OD values -----------------------------------------------------------------
    # They are filled in in a table, which is its own check. The per OD boxes of the
    # strip then say whether the OCR and the haems are scaled by them.
    def table_filler(rows: Dict[str, dict]) -> Dict[str, dict]:
        return _od_table_filler(session, rows)
    details = od_scaling_asker(summaries, answers, defaults, saved, table_filler)
    session.has_od = bool(answers['normalise_od'])
    _strip_shower(session, answers)
    if any(details.values()):
        _od_lister(details)
        _od_gaps_teller(details)
    if answers['normalise_od']:
        # ---- shower ------------------------------------------------------------------
        def shower() -> None:
            _strip_shower(session, answers)
            redraw()
        ocr_view_teller(answers, defaults, shower)

    # ---- 3 Event labels --------------------------------------------------------------
    # Edit labels in the View box changes them later, so they are not accepted here.
    def label_filler(entries: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
        return _label_table_filler(session, entries)
    for name, events in event_asker(summaries, saved, label_filler).items():
        details[name]['events'] = events
        saved[name] = dict(saved.get(name) or {}, events=events)
    redraw()
    return details


# ---- page_stage_runner ---------------------------------------------------------------
def page_stage_runner(layouts_folder: Path) -> FigurePage:
    """
    ---- Summary ----
    Main function to build the page of a dataset figure in the window (Build a figure,
    6.2): the page starts empty, plots are placed by dragging across its grid, and a
    template can be loaded or saved; Continue ends the step, after the offer to save
    a page that was changed as a template.

    ---- Inputs ----
    layouts_folder : Path
        The layouts folder (UserPlaces.layouts_folder), where templates are saved and
        read.

    ---- Globals read ----
    PAGE_NUDGE.

    ---- Outputs ----
    FigurePage
        The page as placed; an empty page when there is no window.

    ---- Globals mutated ----
    None. Changes the window, and writes a template when one is asked for (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _template_offer_asker
    active_gui_getter
    enter_waiter
    guide_step_starter
    info_printer
    """

    guide_step_starter('page')
    window = active_gui_getter()
    if window is None:  # the page is built only in the window
        return FigurePage()
    info_printer('The page on the right is the journal page at its printed size, with '
                 'a grid of 6 × 6 cells. Pick a plot type in the strip above it, then '
                 'drag across the cells it should take; its form opens here.',
                 )
    info_printer('Load template puts a layout saved before on the page; Save template '
                 'keeps this one for later.',
                 )
    window.page_shower(FigurePage(), layouts_folder)
    enter_waiter('Drag across the grid to place each plot. When the page is ready, '
                 'click Continue.',
                 PAGE_NUDGE,
                 number='6.2',
                 )
    kept = window.page_kept_reader()
    page = window.page_hider()
    _template_offer_asker(page, kept, layouts_folder)
    return page


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
                 'ignored parts) are analysed together, so choose a spectral range '
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
        start = number_asker('Where should the spectral range start (nm)?',
                             start,
                             minimum=0,
                             depth=depth,
                             number='4.1.1',
                             )
        end = number_asker('Where should the spectral range end (nm)?',
                           max(end, start + 20.0),
                           minimum=start,
                           exclusive_minimum=True,
                           depth=depth,
                           number='4.1.2',
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
                                     number='4.1.3',
                                     ),
                        )
            rotate = yes_no_asker('Do you want to rotate the components so each is as '
                                  'peak-like as possible (varimax)?',
                                  rotate,
                                  depth=depth,
                                  number='4.1.4',
                                  )
            smoothing = number_asker('Over how many nm should the components be '
                                     'smoothed to remove their noise (0 for none)?',
                                     smoothing,
                                     minimum=0,
                                     maximum=(end - start) / 4,
                                     depth=depth,
                                     number='4.1.5',
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
                                   ('window', 'change the spectral range'),
                                   ('fit', 'keep the fit in the box instead'),
                                   ],
                                  depth=depth,
                                  number='4.1.6',
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
    from the standard settings or the ones last saved for the dataset, with the oxygen,
    the OCR and, while Haem decomposition is ticked, every haem of the fit. The boxes
    above the plot change how the OCR, the haems and the labels are shown, the angle
    of the labels, the journal and the size, each redrawing the figure, and the arrows
    the order of the panels (Finalise figures, 5.1); Export accepts it.

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
    _master_page_saver
    _strip_shower
    enter_waiter
    info_printer
    preview_drawer
    region_files_lister
    """

    # ---- 1 Start from the standard or saved settings ---------------------------------
    guide_step_starter('figure')
    info_printer("Use the Figure box above the plot to set the figure to a journal's "
                 'standard.',
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

    # ---- 2 Change the figure in the boxes until Continue -----------------------------
    redraw()
    enter_waiter('Use the arrows to change the order of the panels, or change earlier '
                 'settings. When ready, click Export to choose which files to export.',
                 FIGURE_NUDGE,
                 number='5.1',
                 go_words='Export',
                 )
    return is_plotted()


# ---- processing_stage_runner ---------------------------------------------------------
def processing_stage_runner(session: ViewerSession,
                            answers: dict,
                            defaults: dict,
                            limits: Dict[str, dict],
                            fits_folder: Path,
                            details: Dict[str, dict],
                            regions: Optional[Dict[str, Dict[str, float]]] = None,
                            ) -> Optional[Dict[str, Dict[str, float]]]:
    """
    ---- Summary ----
    Main function to talk the user through the processing, with the plot redrawn after
    each answer: first the haem fit, set in the Haem decomposition box until Continue
    (its Do PCA button asks the questions that find the components from the whole
    dataset, with the boxes greyed out meanwhile), then the oxidised and the reduced
    region of every file (when the haems are shown), then whether to plot Δψ (when it
    can be; on Yes, its formula and a wait for Continue while its numbers are set in
    the Δψ box), and last the averaging windows, dragged on the plot (they are drawn in
    the plot only once that step is answered). The trim and ignore edges stay movable
    under Trim / Ignore in the Time regions box. A line says which fit the haems are
    worked out with at the start, and another points to % oxidised once a file has
    both regions. Haem decomposition unticked at Continue goes on without haems.

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
    regions : Optional[Dict[str, Dict[str, float]]]
        The regions the step starts with (_regions_chooser), from the last time it
        was answered in this run; None for regions not chosen.

    ---- Globals read ----
    settings.DELTA_PSI_LIMIT_ANSWERS, HAEM_NUDGE, PSI_NUDGE, PSI_FORMULA,
    PSI_FORMULA_NOTE.

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
    _regions_chooser
    _strip_shower
    delta_psi_asker
    enter_waiter
    fit_titles_lister
    info_printer
    pca_stage_runner
    preview_drawer
    region_files_lister
    """

    guide_step_starter('haems')
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
    # Do PCA in the Haem decomposition box: the components of the whole dataset become
    # the fit in use; choosing to keep the fit in the box changes nothing.
    common = set(summaries[0]['datasets'])
    for summary in summaries[1:]:
        common &= set(summary['datasets'])
    def pca_finder() -> None:
        if not common:
            info_printer('The files have no spectrometer in common, so the components '
                         'cannot be found from the data.',
                         )
            return
        dataset = (answers.get('decomposition_dataset')
                   if answers.get('decomposition_dataset') in common
                   else sorted(common)[0]
                   )
        session.window.strip_state_setter(False)
        try:
            name, fit = pca_stage_runner(session,
                                         answers,
                                         defaults,
                                         limits,
                                         fits_folder,
                                         dataset,
                                         2,
                                         )
        finally:
            session.window.strip_fits_setter(fit_titles_lister(fits_folder))
            session.window.strip_state_setter(True)
        if fit is not None:
            answers.update({'decompose': True,
                            'plot_haems': True,
                            'fit_file': name,
                            'haem_files': [],
                            'decomposition_dataset': dataset,
                            'haems': list(fit['haem_list']),
                            },
                           )
            session.fit = fit
            session.kept = None
            info_printer(f'The haems are worked out with {name}.')
        _strip_shower(session, answers)
        redraw()

    # ---- 1 The haem fit, set in the Haem decomposition box ---------------------------
    if session.fit is None:
        info_printer(
            'No haems are worked out yet: tick Haem decomposition to work them '
            'out with the fit shown, or leave it unticked to go on without '
            'haems.',
            )
    else:
        info_printer(
            'The haems are worked out with '
            f"{fit_describer(answers['fit_file'], answers.get('haem_files', []))}.",
            )
    redraw()
    session.pca_runner = pca_finder
    try:
        enter_waiter('Edit the haem decomposition using the Haem decomposition box, '
                     'press Continue when ready.',
                     HAEM_NUDGE,
                     number='4.1',
                     )
    finally:
        session.pca_runner = None
    # the box decides: haems with the fit in it while ticked, none while unticked
    answers['decompose'] = session.fit is not None
    _strip_shower(session, answers)

    # ---- 2 The oxidised and the reduced region ---------------------------------------
    # The regions go to the session at once, so the plots that follow and the boxes
    # have their % oxidised. Ox / Red in the Time regions box may change them later.
    if answers['decompose']:
        regions = _regions_chooser(session, answers, limits, details, session.regions)
        session.regions = regions or {}
        _strip_shower(session, answers)
        if region_files_lister(summaries,
                               limits,
                               session.regions,
                               answers.get('decomposition_dataset'),
                               ):
            info_printer('The haems can now be shown in % oxidised: choose it under '
                         'Haems as in the View box above the plot.',
                         )

    # ---- 3 Delta psi -----------------------------------------------------------------
    # Asked only when it can be worked out; the plot then gets or loses its panel.
    if answers['decompose'] and session.fit is not None:
        was_on = bool(answers['delta_psi'])
        # the Δψ box may have been ticked already: its tick is the default
        is_on = delta_psi_asker(answers,
                                dict(defaults, delta_psi=answers['delta_psi']),
                                list(session.fit['haem_list']),
                                region_files_lister(summaries,
                                                    limits,
                                                    session.regions,
                                                    answers.get('decomposition_dataset',
                                                                ),
                                                    ),
                                )
        _strip_shower(session, answers)  # the Δψ box is ticked or not with it
        if is_on != was_on:
            redraw()
        if is_on:
            # Like the haem step: the line with the formula, then Continue while the
            # numbers are set in the Δψ box.
            lowest, highest = (answers[answer]
                               for answer in settings.DELTA_PSI_LIMIT_ANSWERS
                               )
            info_printer('Δψ (mV) is worked out from the bH and bL haems, for the '
                         'files with both regions, and drawn in its own panel:',
                         tight=True,
                         )
            session.window.formula_sender(PSI_FORMULA)
            info_printer(PSI_FORMULA_NOTE, tight=True)
            info_printer(f'It has gaps where bH or bL is less than {lowest:g} % or '
                         f'more than {highest:g} % reduced. To compare two sets of '
                         'numbers, click Keep to compare first.',
                         )
            enter_waiter('Set the midpoints of bH and bL and the shift in the Δψ box, '
                         'press Continue when ready.',
                         PSI_NUDGE,
                         number='4.5.1',
                         )
    else:
        # without haems there is no delta psi, whatever the dataset was saved with
        answers['delta_psi'] = False
        _strip_shower(session, answers)

    # ---- 4 The averaging windows -----------------------------------------------------
    # Without haems nothing has drawn this step's plot yet: it may still show the plot
    # of another step.
    if not answers['decompose']:
        redraw()
    _windows_chooser(session, answers, defaults, limits, details)
    drawn['windows'] = True
    # the View box now offers the OCR as % of baseline, when there are windows
    session.has_windows = bool(answers['averaging'])
    _strip_shower(session, answers)
    if answers['averaging']:
        redraw()
    # Read now: Keep old may have put the kept regions back since they were
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


# ---- setup_stage_runner --------------------------------------------------------------
def setup_stage_runner(names: List[str], saved: Optional[dict] = None) -> dict:
    """
    ---- Summary ----
    Main function to have the dataset set-up table filled in in the window (Dataset
    set-up, 6.1): one row per experiment, as saved with the dataset or filled in
    from the file names, corrected by the user; Continue ends the step.

    ---- Inputs ----
    names : List[str]
        The experiment names (the .paf file names without the extension), in the
        order of the table.
    saved : Optional[dict]
        The set-up saved with the dataset (saved_setup, DATA_FORMAT.md); None or
        empty for a dataset never set up.

    ---- Globals read ----
    SETUP_NUDGE.

    ---- Outputs ----
    dict
        The set-up table (dataset_setup, DATA_FORMAT.md) as filled in; as built from
        what was saved and the file names when there is no window.

    ---- Globals mutated ----
    None. Changes the window (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    active_gui_getter
    enter_waiter
    guide_step_starter
    info_printer
    setup_builder
    """

    guide_step_starter('setup')
    setup = setup_builder(names, saved)
    window = active_gui_getter()
    if window is None:  # the table is filled in only in the window
        return setup
    info_printer('The table on the right says which experiment is which, filled in '
                 'from the file names: check it, and type over what is wrong. The '
                 'dataset figures split the experiments into sets by Group 1, Group '
                 '2 and the time point, and untick Use to leave an experiment out.',
                 )
    info_printer('The replicates are numbered for you: the experiments with the same '
                 'Group 1, Group 2 and time point count 1, 2, 3.',
                 )
    window.setup_shower(setup)
    enter_waiter('Check which experiment is which in the table. When it is right, '
                 'click Continue.',
                 SETUP_NUDGE,
                 number='6.1',
                 )
    return window.setup_hider()


# ---- trim_stage_runner ---------------------------------------------------------------
def trim_stage_runner(session: ViewerSession,
                      answers: dict,
                      remembered: Dict[str, dict],
                      previous: Optional[Dict[str, dict]] = None,
                      exporter: Optional[Callable[[Dict[str, dict], bool],
                                                  None,
                                                  ]] = None,
                      ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to run the trimming step on the standard plot of the whole recording
    of every file: the trimmed and ignored edges are dragged on the plot or typed in
    the Time regions box above it, under the key of their colours, and Continue
    accepts them; the two export buttons write the spectra as csv files with the edges
    as they are (Export full + trimmed csv with the whole recording of each trimmed
    file too), and
    the step waits again. When the step is
    opened again, the limits it had stay on the plot as red dashed lines. The limits
    are then listed and the trimmed data is drawn. The haems are those of the
    session's fit (none when it has none).

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
    exporter : Optional[Callable[[Dict[str, dict], bool], None]]
        Called with the limits of the edges as they are when an export button is
        clicked, and True for Export full + trimmed csv; None for no export buttons.

    ---- Globals read ----
    TRIM_KEY_LINES, TRIM_NUDGE (module constants); EXPORT_BUTTONS,
    EXPORT_FULL_CHANGE.

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
    _step_edges_reader
    _step_edges_shower
    _trim_choice_builder
    enter_waiter
    info_printer
    preview_drawer
    trim_limits_builder
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

    # ---- 2 Drag or type the edges until Continue -------------------------------------
    # An export button writes the files with the edges as they are, and the step waits
    # again.
    choice = _trim_choice_builder(session, remembered, previous)
    guide_step_starter('trim')
    info_printer(TRIM_KEY_LINES[0])
    info_printer(TRIM_KEY_LINES[1], tight=True)
    info_printer('Ticking Apply to all copies the times of the experiment shown to '
                 'every experiment; it unticks itself when the next one is shown.',
                 )
    if exporter is not None:
        info_printer('The export buttons write the spectra of every experiment as csv '
                     'files with these times; Continue skips them.',
                     tight=True,
                     )
    _step_edges_shower(session, 'trim', choice)
    try:
        while True:
            clicked = enter_waiter(
                'Drag the bars on the plot, or type the times in the '
                'Time regions box. Check each experiment, then '
                'press Continue.',
                TRIM_NUDGE,
                number='2.1',
                extras=EXPORT_BUTTONS if exporter is not None else (),
                )
            if not clicked:
                break
            exporter(trim_limits_builder(session.summaries,
                                         session.window.edges_reader(),
                                         ),
                     clicked == EXPORT_FULL_CHANGE,
                     )
    finally:
        minutes = _step_edges_reader(session)

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
    the averaging), the finalised figures and what to export. The standard plot of
    every file (oxygen, OCR and the haems of the dataset's fit) is shown first, with no
    question asked. The plot window is redrawn after each answer; an earlier step is
    opened from the guide. The settings strip can be changed while these questions
    wait (except those of the components found from the data); it is greyed out
    afterwards.

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
        whether the quick export of the trim step wrote the spectra of the trimmed
        data as csv files with the trim edges in use.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (export_choice and export_spectra among
    them), reads from and prints to the terminal, draws and closes the plot window,
    sets up the settings strip, writes the csv files of the quick export and of the
    whole recordings when chosen and adds to ``exported`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_chooser
    _quick_exporter
    _standard_fit_loader
    _strip_change_applier
    _strip_shower
    active_gui_getter
    browser_stage_runner
    details_stage_runner
    fit_titles_lister
    library_haems_lister
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
    window.strip_fits_setter(fit_titles_lister(fits_folder))
    window.strip_library_setter(library_haems_lister(fits_folder))
    _strip_shower(session, answers)
    window.strip_listener_setter(lambda changes: _strip_change_applier(session,
                                                                       answers,
                                                                       fits_folder,
                                                                       changes,
                                                                       ),
                                 )
    window.strip_state_setter(True)

    # ---- 2.1 The tabs of the Time regions box, the edit and export buttons -----------
    # The limits are one record, changed in place, so every step and plot uses the
    # trim and ignore edges of now.
    def keep_limits(new: Dict[str, dict]) -> Dict[str, dict]:
        if state.get('limits') is None:
            state['limits'] = new
        else:
            state['limits'].clear()
            state['limits'].update(new)
        # the boxes offer % oxidised for the regions that hold under these limits
        session.limits = state['limits']
        _strip_shower(session, answers)
        answers['ignore_first_minutes'] = max(v['ignore_start']
                                              for v in state['limits'].values()
                                              )
        answers['ignore_last_minutes'] = max(v['ignore_end']
                                             for v in state['limits'].values()
                                             )
        return state['limits']
    def export_csv(limits: Dict[str, dict], with_full: bool) -> None:
        _quick_exporter(session, limits, state.get('details') or {}, with_full)
    kits = _tab_kits_builder(session, answers, state, keep_limits)
    session.tab_switcher = lambda tab: _tab_switcher(session, kits, tab)
    session.edit_runner = lambda name: _box_edit_runner(session,
                                                        answers,
                                                        state,
                                                        name,
                                                        export_csv,
                                                        )
    # an answer given while another tab is open uses that tab's change first
    window.answer_listener_setter(lambda: (
        session.tab_switcher('')
        if session.time_tab and session.time_tab != session.step_tab
        else None))

    def run_trim() -> Dict[str, dict]:
        old = state.get('limits') or remembered
        return keep_limits(trim_stage_runner(session,
                                             answers,
                                             old,
                                             state.get('limits'),
                                             export_csv,
                                             ),
                           )
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

        # ---- 4 Choose what to export -------------------------------------------------
        # Asked while the boxes still work: an earlier step is opened from the guide.
        _export_chooser(session,
                        answers,
                        defaults,
                        state['limits'],
                        state['details'],
                        )
    finally:
        window.strip_listener_setter(None)
        window.answer_listener_setter(None)
        session.tab_switcher = session.edit_runner = None
        window.strip_state_setter(False)
        session.redraw = None
        session.window.window_closer()

    # ---- 5 Return the answers --------------------------------------------------------
    # Read now: the strip may have changed the haems, or gone back to the kept regions,
    # after the figure was accepted.
    plotted = bool(answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems'])
    # the trimmed csv files of the quick export are used only while the trim edges
    # they were written with are still the ones in use
    has_spectra = (EXPORT_PARTS.get(session.export_choice, (False, False))[0] and
                   all((session.export_limits.get(name) or {}).get(key) == own.get(key)
                       for name, own in state['limits'].items()
                       for key in ('trim_start', 'trim_end')
                       )
                   )
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
