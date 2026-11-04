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
                                     component_count_suggester,
                                     component_finder,
                                     fit_saver,
                                     fit_table_builder,
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
from utils_shared.survey import (averaging_asker,
                                 decomposition_asker,
                                 event_asker,
                                 file_focus_setter,
                                 haem_choice_asker,
                                 haem_form_asker,
                                 haem_scaling_asker,
                                 label_angle_asker,
                                 od_scaling_asker,
                                 saved_values_reader,
                                 signal_asker,
                                 size_asker,
                                 trim_asker,
                                 )
from utils_viewer.viewer_preview import (all_data_exporter,
                                         BROWSING_ANSWERS,
                                         pca_picture_builder,
                                         pca_spectra_gatherer,
                                         preview_drawer,
                                         skipped_windows_finder,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_gui import active_gui_getter
from utils_viewer.viewer_window import PictureWindow


# ---- CONSTANTS -----------------------------------------------------------------------
PREVIEW_FILE = Path(tempfile.gettempdir()) / 'Portimao_preview.png'
WARNING_COLOUR = '\x1b[1;31m'  # bold red
STAGE_TITLES = {'browser': 'Experiment browser',
                'trim': 'Trimming and ignoring',
                'analysis': 'Analysis',
                'plots': 'Individual experiment plots',
                }


# ---- STAGE HELPERS -------------------------------------------------------------------


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
    browsing and trimming, and the analysis chosen so far afterwards.

    ---- Inputs ----
    answers : dict
        Answers given so far.
    fit : Optional[dict]
        Fit dictionary, used to list the haems to show.
    kind : str
        'raw' (O2 and the raw OCR only), 'analysis' (also the haems, still without OD
        scaling), 'plots' (the choices made so far for the individual figures, in a
        wide preview) or 'final' (exactly as the figure will be).

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
    if kind == 'plots':
        return result
    result.update({'plot_o2': True, 'plot_ocr': True, 'plot_haems': False})
    if kind == 'raw':
        result.update({'decompose': False,
                       'normalise_od': False,
                       'averaging': False,
                       'ocr_mode': 'raw',
                       })
        return result
    result.update({'normalise_od': False, 'ocr_mode': 'raw', 'haem_per_od': False})
    if result['decompose'] and fit is not None:
        result.update({'plot_haems': True,
                       'haems': list(fit['haem_list']),
                       'haem_mode': 'delta',
                       })
    return result


# ---- _component_namer ----------------------------------------------------------------
def _component_namer(result: dict, depth: int) -> List[str]:
    """
    ---- Summary ----
    Helper function to ask whether to name the components found (they are called PC1,
    PC2, ... otherwise) and, if so, what each is called.

    ---- Inputs ----
    result : dict
        Result of component_builder.
    depth : int
        Numbering depth of the questions.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The name of each component, all different.

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
    for i, peak in enumerate(result['peaks']):
        others = [n for j, n in enumerate(names) if j != i]
        while True:
            name = (text_asker(f'What is component {i + 1} (largest peak at '
                               f'{peak:.0f} nm) called?',
                               names[i],
                               depth=depth,
                               ) or '').strip()
            if name and ',' not in name and name not in others:
                names[i] = name
                break
            info_printer('Use a name that is not empty, has no commas and is not used '
                         'by another component.',
                         depth=depth,
                         )
    return names


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


# ---- _pca_table_lister ---------------------------------------------------------------
def _pca_table_lister(analysis: dict, suggestion: int, depth: int) -> None:
    """
    ---- Summary ----
    Helper function to print how much of the changes in the spectra each principal
    component explains, and what is left over if only the first few are used, so the
    number of components can be chosen.

    ---- Inputs ----
    analysis : dict
        Result of component_finder.
    suggestion : int
        Number of components suggested.
    depth : int
        Numbering depth of the lines.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    Residual RMS = sqrt((total variance - variance of the first k components) / number
    of values).

    ---- Helpers ----
    info_printer
    """

    values = analysis['eigenvalues']
    total = analysis['total_variance']
    info_printer(f"Analysed {analysis['n_spectra']} spectra from "
                 f"{len(analysis['counts'])} files between "
                 f"{analysis['window'][0]:g} and {analysis['window'][1]:g} nm.",
                 depth=depth,
                 )
    info_printer('  Number   Explained   Total   Residual (OD)', depth=depth)
    running = 0.0
    for k, value in enumerate(values, start=1):
        running += value
        rms = max(total - running, 0.0) / analysis['n_values']
        mark = '  <- suggested' if k == suggestion else ''
        info_printer(f'  {k:>6}   {value / total * 100:8.3f}%   '
                     f'{running / total * 100:6.2f}%   {rms ** 0.5:11.5f}{mark}',
                     depth=depth,
                     )
    info_printer('The suggestion is a rule of thumb: the biggest drop between '
                 'neighbouring components, where the signal ends and the noise '
                 'starts. Use as few components as describe the data; extra ones only '
                 'fit noise.',
                 depth=depth,
                 )


# ---- _review_asker -------------------------------------------------------------------
def _review_asker(session: ViewerSession,
                  question: str,
                  change_label: str,
                  redraw: Callable[[], bool],
                  ) -> bool:
    """
    ---- Summary ----
    Helper function to ask whether the user accepts what the plot window shows. In the
    browser window the user flicks through the files while the question waits; with the
    picture fallback the user can ask to look at another file, which redraws it.

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
    _file_chooser
    choice_asker
    """

    options = [('yes', 'Yes, accept'),
               ('no', change_label),
               ]
    if len(session.summaries) > 1 and not session.window.is_interactive:
        options.append(('file', 'Look at another file in the plot window first'))
    while True:
        choice = choice_asker(question, options, 'yes')
        if choice == 'yes':
            return True
        if choice == 'no':
            return False
        _file_chooser(session)
        redraw()


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


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- analysis_stage_runner -----------------------------------------------------------
def analysis_stage_runner(session: ViewerSession,
                          answers: dict,
                          defaults: dict,
                          limits: Dict[str, dict],
                          fits_folder: Path,
                          details_before: Optional[Dict[str, dict]] = None,
                          ) -> Tuple[Optional[dict], Dict[str, dict]]:
    """
    ---- Summary ----
    Main function to ask the analysis questions (haem decomposition, OD values, event
    averaging and event labels) one at a time. The plot is redrawn after each, except
    the OD values, which are only checked: the data is scaled by OD in the individual
    plots.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file (trim_asker).
    fits_folder : Path
        Folder holding the fit .csv files.
    details_before : Optional[Dict[str, dict]]
        OD values and events from an earlier pass, offered as defaults when the step is
        asked again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Optional[dict], Dict[str, dict]]
        (fit, details) exactly as analysis_asker returns them.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _od_lister
    _review_asker
    _skipped_lister
    averaging_asker
    decomposition_asker
    event_asker
    od_scaling_asker
    pca_stage_runner
    preview_drawer
    saved_values_reader
    """

    summaries = session.summaries
    details: Dict[str, dict] = {s['name']: {} for s in summaries}
    fit: Optional[dict] = None
    saved = saved_values_reader(summaries, session.export_root)
    for name, values in (details_before or {}).items():
        saved[name] = dict(saved.get(name) or {}, **values)
    answers.update({'decompose': False, 'normalise_od': False, 'averaging': False})
    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, fit, 'analysis'),
                              limits,
                              fit,
                              details,
                              )
    def pca_finder(dataset: str, depth: int) -> Tuple[Optional[str], Optional[dict]]:
        return pca_stage_runner(session,
                                answers,
                                defaults,
                                limits,
                                fits_folder,
                                dataset,
                                depth,
                                )

    # ---- 1 Decomposition -------------------------------------------------------------
    while True:
        (answers['decompose'],
         answers['fit_file'],
         fit,
         answers['decomposition_dataset'],
         ) = decomposition_asker(summaries,
                                 defaults,
                                 fits_folder,
                                 pca_runner=pca_finder,
                                 )
        if not answers['decompose']:
            break
        redraw()
        if _review_asker(session,
                         'Do you accept this decomposition?',
                         'No, choose the fit again',
                         redraw,
                         ):
            break
        defaults = dict(defaults, decompose=True, fit_file=answers['fit_file'])

    # ---- 2 OD values -----------------------------------------------------------------
    # Only checked here; the data is scaled by OD in the individual plots
    while True:
        details = od_scaling_asker(summaries, answers, defaults, saved)
        if not answers['normalise_od']:
            break
        _od_lister(details)
        if _review_asker(session,
                         'Do you accept these OD values?',
                         'No, enter the OD values again',
                         lambda: True,
                         ):
            break
        defaults = dict(defaults, normalise_od=True)
        for name, values in details.items():
            saved[name] = dict(saved.get(name) or {}, **values)

    # ---- 3 Averaging -----------------------------------------------------------------
    while True:
        averaging_asker(answers, defaults)
        if not answers['averaging']:
            break
        redraw()
        _skipped_lister(session, answers, limits, details)
        if _review_asker(session,
                         'Do you accept these averaging windows?',
                         'No, change the window and gap',
                         redraw,
                         ):
            break
        defaults = dict(defaults, averaging=True)
        defaults.update({k: answers[k] for k in ('window_minutes', 'gap_minutes')})

    # ---- 4 Event labels --------------------------------------------------------------
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
    return fit, details


# ---- browser_stage_runner ------------------------------------------------------------
def browser_stage_runner(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Main function to show the files in the plot window (the set and measured O2 and the
    OCR, with the events) before any question is asked about them. In the browser window
    the user can look through them while answering, so the questions carry straight on;
    with the picture fallback a small menu steps through the files.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file is changed.
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
    if session.window.is_interactive:
        preview_drawer(session,
                       _answers_previewer(answers, None, 'raw'),
                       {},
                       None,
                       {},
                       show_ignored=False,
                       )
        return
    options = [('next', 'Next file'),
               ('previous', 'Previous file'),
               ('goto', 'Go to a specific file'),
               ('continue', 'Continue to trimming and ignoring'),
               ]
    while True:
        summary = session.summaries[session.current]
        preview_drawer(session,
                       _answers_previewer(answers, None, 'raw'),
                       {},
                       None,
                       {},
                       show_ignored=False,
                       )
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
    spectral window and the number of components, sees the components in the plot
    window, and can save them as a fit file in the fits folder.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary; the window is stored in it (pca_start, pca_end,
        pca_rotate).
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
    _pca_table_lister
    choice_asker
    component_builder
    component_count_suggester
    component_finder
    fit_table_builder
    info_printer
    number_asker
    pca_picture_builder
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
        _pca_table_lister(analysis, suggestion, depth)

        # ---- 2 Choose the components -------------------------------------------------
        count = suggestion
        while True:
            while True:
                value = number_asker('How many components should be used?',
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
            result = component_builder(analysis, count, rotate)
            names = [f'PC{i + 1}' for i in range(count)]
            try:
                session.window.extra_publisher('PCA components',
                                               pca_picture_builder(analysis,
                                                                   result,
                                                                   names,
                                                                   ),
                                               )
            except Exception as exc:  # a drawing problem must never stop the questions
                info_printer(f'The components could not be drawn ({exc}).',
                             depth=depth,
                             )
            info_printer('Components (largest peak): ' + ', '.join(
                f'PC{i + 1} {p:.0f} nm ({e * 100:.1f}%)'
                for i, (p, e) in enumerate(zip(result['peaks'], result['explained']))
            ) + f". Residual {result['residual_rms']:.5f} OD.",
                         depth=depth,
                         )
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
    names = _component_namer(result, depth)
    if names != [f'PC{i + 1}' for i in range(count)]:
        try:
            session.window.extra_publisher('PCA components',
                                           pca_picture_builder(analysis, result, names),
                                           )
        except Exception:  # the unnamed picture stays
            pass
    fit = fit_table_builder(result, names)
    saved = _fit_file_saver(fit, fits_folder, count, analysis['window'], depth)
    answers.update({'pca_start': start, 'pca_end': end, 'pca_rotate': rotate})
    return (saved or f'PCA, {count} components, {start:g}-{end:g} nm (not saved)'), fit


# ---- plots_stage_runner --------------------------------------------------------------
def plots_stage_runner(session: ViewerSession,
                       answers: dict,
                       defaults: dict,
                       limits: Dict[str, dict],
                       fit: Optional[dict],
                       details: Dict[str, dict],
                       ) -> bool:
    """
    ---- Summary ----
    Main function to ask how the figure saved for each file looks, one choice at a
    time: the oxygen and OCR, the haems and their order, how the haems are shown (and
    whether they are scaled by OD), the event labels and finally the journal and size.
    The plot is redrawn after each choice and the user accepts it or chooses again.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    fit : Optional[dict]
        Fit dictionary, or None.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when at least one panel is plotted.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _review_asker
    haem_choice_asker
    haem_form_asker
    haem_scaling_asker
    info_printer
    label_angle_asker
    preview_drawer
    signal_asker
    size_asker
    """

    # ---- 1 Explain the section -------------------------------------------------------
    info_printer('Now you choose how the figure saved for each file will look. The '
                 'plot is redrawn after each choice, and you can look at every file '
                 'before accepting it.',
                 )
    answers.update({'plot_haems': False, 'haem_per_od': False})
    def redraw(kind: str = 'plots') -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, fit, kind),
                              limits,
                              fit,
                              details,
                              show_ignored=False,
                              )

    # ---- 2 Oxygen and OCR ------------------------------------------------------------
    while True:
        if not signal_asker(answers, defaults):
            break
        redraw()
        if _review_asker(session,
                         'Do you accept the oxygen and OCR plots?',
                         'No, choose them again',
                         redraw,
                         ):
            break
        defaults = dict(defaults, **{key: answers[key]
                                     for key in ('plot_o2', 'plot_ocr', 'ocr_mode')
                                     if key in answers
                                     })

    # ---- 3 Haems and their order -----------------------------------------------------
    while True:
        if not haem_choice_asker(answers, defaults, fit):
            break
        redraw()
        if _review_asker(session,
                         'Do you accept these haems and their order?',
                         'No, choose the haems again',
                         redraw,
                         ):
            break
        defaults = dict(defaults, plot_haems=True, haems=answers['haems'])

    # ---- 4 How the haems are shown ---------------------------------------------------
    while answers['plot_haems']:
        haem_form_asker(answers, defaults)
        redraw()
        if haem_scaling_asker(answers, defaults):
            redraw()
        if _review_asker(session,
                         'Do you accept this haem presentation?',
                         'No, choose how the haems are shown again',
                         redraw,
                         ):
            break
        defaults = dict(defaults,
                        haem_mode=answers['haem_mode'],
                        haem_per_od=answers['haem_per_od'],
                        )

    # ---- 5 Event labels --------------------------------------------------------------
    plotted = answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems']
    if not plotted:
        info_printer('Nothing is set to be plotted, so no individual figures will be '
                     'made.',
                     )
    while plotted:
        label_angle_asker(answers, defaults)
        redraw()
        if _review_asker(session,
                         'Do you accept the event labels?',
                         'No, change the angle',
                         redraw,
                         ):
            break
        defaults = dict(defaults, event_label_angle=answers['event_label_angle'])

    # ---- 6 Journal and size ----------------------------------------------------------
    while True:
        size_asker(answers,
                   defaults,
                   {'journal': 'journal',
                    'columns': 'columns',
                    'height': 'height',
                    'mode': 'size_mode',
                    },
                   (1, 0.5),
                   )
        if not plotted:
            return False
        redraw('final')
        if _review_asker(session,
                         'Do you accept this figure?',
                         'No, change the journal or size',
                         lambda: redraw('final'),
                         ):
            return plotted
        defaults = dict(answers)


# ---- trim_stage_runner ---------------------------------------------------------------
def trim_stage_runner(session: ViewerSession,
                      answers: dict,
                      remembered: Dict[str, dict],
                      ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the trim and ignore questions, adding the shaded trimmed and
    ignored parts to the plot window after every answer, and ask whether to accept them.
    When the limits are asked again, the earlier ones stay on the plot as dashed lines.
    After they are accepted, it offers to export all the data cut to them.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
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
    def draw(limits: Dict[str, dict]) -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, None, 'raw'),
                              limits,
                              None,
                              {},
                              show_trim=True,
                              previous_limits=previous,
                              )
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
    trimming and ignoring, the analysis and the individual figures. The plot window is
    redrawn after each answer, and at the end any step can be gone back to.

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
    PREVIEW_FILE, STAGE_TITLES (module constants).

    ---- Outputs ----
    Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool]
        (limits, fit, details, plotted) as the same questions return them when they are
        asked without the browser.

    ---- Globals mutated ----
    None. Stores the answers in ``answers``, reads from and prints to the terminal,
    draws and closes the plot window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    active_gui_getter
    analysis_stage_runner
    browser_stage_runner
    choice_asker
    file_focus_setter
    heading_printer
    info_printer
    numbering_getter
    numbering_setter
    plots_stage_runner
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

    # ---- run_browser -----------------------------------------------------------------
    def run_browser() -> None:
        browser_stage_runner(session, answers)
    def run_trim() -> None:
        old = state.get('limits') or remembered
        state['limits'] = trim_stage_runner(session, answers, old)
        answers['ignore_first_minutes'] = max(v['ignore_start']
                                              for v in state['limits'].values()
                                              )
        answers['ignore_last_minutes'] = max(v['ignore_end']
                                             for v in state['limits'].values()
                                             )
    def run_analysis() -> None:
        old_defaults = dict(answers) if state.get('fit_asked') else defaults
        state['fit'], state['details'] = analysis_stage_runner(session,
                                                               answers,
                                                               old_defaults,
                                                               state['limits'],
                                                               fits_folder,
                                                               state.get('details'),
                                                               )
        state['fit_asked'] = True
    def run_plots() -> None:
        old_defaults = dict(answers) if state.get('plots_asked') else defaults
        state['plotted'] = plots_stage_runner(session,
                                              answers,
                                              old_defaults,
                                              state['limits'],
                                              state['fit'],
                                              state['details'],
                                              )
        state['plots_asked'] = True
    steps = [('browser', run_browser),
             ('trim', run_trim),
             ('analysis', run_analysis),
             ('plots', run_plots),
             ]

    # ---- 2 Ask every step once -------------------------------------------------------
    try:
        for key, runner in steps:
            if key == 'browser' and window.is_interactive:
                runner()  # the window needs no section of its own
                continue
            section_starter(STAGE_TITLES[key])
            runner()
        last_section, last_question = numbering_getter(0), numbering_getter(1)

        # ---- 3 Go back to any step ---------------------------------------------------
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
            steps[index][1]()
            if index < len(steps) - 1:
                later = ', '.join(STAGE_TITLES[k] for k, _ in steps[index + 1:])
                info_printer(f'Your answers to the later steps ({later}) were kept. '
                             f'Go back to them if this change affects them.',
                             )
    finally:
        file_focus_setter(None)
        session.window.window_closer()

    # ---- 4 Return the answers --------------------------------------------------------
    return state['limits'], state['fit'], state['details'], state['plotted']
