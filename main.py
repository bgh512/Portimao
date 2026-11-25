"""
Main program: read .paf files, process them and export figures and workbooks.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import gc
import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')  # figures are saved to files; no window is needed
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.custom_runner import (exemplar_runner,
                                        experiment_preparer,
                                        ocr_and_haem_response_runner,
                                        time_response_runner,
                                        )
from utils_shared.app_messages import SEND_DETAILS, start_problem_shower
from utils_shared.comparison_plotter import comparison_figure_plotter
from utils_shared.dataset_settings import dataset_settings_saver, file_settings_merger
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.figure_layout import figure_size_calculator
from utils_shared.figure_page import FIGURE_NAME, figure_page_exporter, FigurePage
from utils_shared.individual_experiment_exporter import experiment_workbook_exporter
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.journal_files import journal_answers_fitter
from utils_shared.master_page_exporter import master_page_exporter
from utils_shared.output_capture import output_capturer
from utils_shared.questions import (guide_step_starter,
                                    info_printer,
                                    section_starter,
                                    UserQuitError,
                                    yes_no_asker,
                                    )
from utils_shared.helpers import (program_title_builder,
                                  program_version_reader,
                                  update_note_finder,
                                  )
from utils_shared.run_logging import (details_place_setter,
                                      logging_starter,
                                      logging_stopper,
                                      settings_logger,
                                      )
from utils_shared.spectral_decomposer import BACKGROUND_SHORT_NAMES, fit_describer
from utils_shared.survey import files_asker, haem_name_formatter, JOURNAL_NAMES
from utils_shared.user_notices import problem_shower, warning_shower
from utils_shared.user_places import (app_output_logger,
                                      user_folder_preparer,
                                      user_places_finder,
                                      )
from utils_viewer.viewer_gui import active_gui_getter, gui_runner, GuiUnavailableError
from utils_viewer.viewer_preview import preview_info_builder
from utils_viewer.viewer_stages import page_stage_runner, viewer_asker


# ---- CONSTANTS -----------------------------------------------------------------------
# From source everything is in this folder; the Mac app keeps the user's things in a
# folder of their own (utils_shared/user_places.py).
PLACES = user_places_finder()
VERSION = program_version_reader(PLACES.program_folder)
PROGRAM_TITLE = program_title_builder(PLACES.program_folder, VERSION)
# why this copy does not update itself, said beside the version; empty when it does
UPDATE_NOTE = update_note_finder(PLACES.program_folder, PLACES.is_app)
WINDOW_TITLE = PROGRAM_TITLE + (' (does not update itself)' if UPDATE_NOTE else '')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- cancel_sentence_builder ---------------------------------------------------------
def cancel_sentence_builder(exported: List[Path],
                            saved_plots: List[str],
                            export_root: Path,
                            saved_workbooks: Optional[List[str]] = None,
                            ) -> str:
    """
    ---- Summary ----
    Main function to say what a run cancelled during the questions left in the results
    folder: the data exported with the trim step's export buttons, the plots and the workbooks of the files
    saved once their processing and figure were accepted, any of these, or nothing.

    ---- Inputs ----
    exported : List[Path]
        The results folder, once an export button wrote into it; else empty.
    saved_plots : List[str]
        Names of the files whose plot was saved; empty when none was.
    export_root : Path
        Results folder.
    saved_workbooks : Optional[List[str]]
        Names of the files whose workbook was written; empty or None when none was.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The sentence, without its full stop.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    files = ' and '.join(text
                         for text, is_kept in (('plots', bool(saved_plots)),
                                               ('workbooks', bool(saved_workbooks)),
                                               )
                         if is_kept
                         )
    kept = [text
            for text, is_kept in (('data you exported', bool(exported)),
                                  (f'{files} of your files', bool(files)),
                                  )
            if is_kept
            ]
    if not kept:
        return 'Nothing was changed'
    verb = 'are' if files else 'is'
    return (f"The {' and the '.join(kept)} {verb} kept in {export_root}; nothing else "
            f'was changed'
            )


# ---- comparison_maker ----------------------------------------------------------------
def comparison_maker(comparison: dict,
                     kept: dict,
                     cfg: settings.Config,
                     export_root: Path,
                     ) -> None:
    """
    ---- Summary ----
    Main function to draw the side-by-side figure of two chosen experiments, or to say
    why it cannot be made.

    ---- Inputs ----
    comparison : dict
        Side-by-side settings: {runs: (left, right), columns, height}.
    kept : dict
        Results of experiment_processor keyed by experiment name.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    export_root : Path
        Results folder.

    ---- Globals read ----
    settings.Config (the comparison journal is read from the answers).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the comparison figure files and prints the outcome (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    comparison_figure_plotter
    figure_size_calculator
    plot_config_builder
    problem_shower
    warning_shower
    """

    # ---- 1 Set up the comparison -----------------------------------------------------
    cfg = settings.Config(dict(cfg.answers, journal=cfg.answers['comparison_journal']))
    # The side-by-side figure of the two chosen runs (skipped, with the reason, if
    # either one failed or they were plotted differently).
    names = comparison['runs']
    first, second = (kept.get(name) for name in names)
    print(f'\nComparison: {names[0]} (a) vs {names[1]} (b)')

    # ---- 2 Check both runs can be compared -------------------------------------------
    if not (first and second):
        warning_shower('  Not made: one of the two runs did not finish.')
        return
    if (first['vo2_source'], first['haem_source']) != (second['vo2_source'],
                                                       second['haem_source'],
                                                       ):
        warning_shower('  Not made: the two runs were plotted with different data (for '
                       'example only one has an OD entered).',
                       )
        return

    # ---- 3 Draw and save the figure --------------------------------------------------
    try:
        size = figure_size_calculator(cfg.SPEC,
                                      comparison['columns'],
                                      comparison['height'],
                                      )
        stem = comparison_figure_plotter(first['experiment'],
                                         second['experiment'],
                                         cfg.plot_config_builder(first['vo2_source'],
                                                                 first['haem_source'],
                                                                 ),
                                         export_root,
                                         size,
                                         cfg.SPEC,
                                         settings.COMPARISON_GAP_PADS,
                                         )
        print(f'  Saved {stem} ({size[0] * 25.4:.0f} x {size[1] * 25.4:.0f}'
              f' mm)',
              )
    except Exception as exc:
        problem_shower('  Not made', exc)
        plt.close('all')


# ---- dataset_figure_saver ------------------------------------------------------------
def dataset_figure_saver(page: FigurePage, export_root: Path) -> List[Path]:
    """
    ---- Summary ----
    Main function to save the dataset figure built on the page: the figure as a PDF of
    its printed size, with text that can still be changed, then its master page, the
    figure on a page of its journal. A page with no plot saves nothing. A file that
    cannot be saved is said in one sentence and the run goes on.

    ---- Inputs ----
    page : FigurePage
        The page as built in the Build a figure step.
    export_root : Path
        Results folder.

    ---- Globals read ----
    settings.JOURNAL_SPECS; FIGURE_NAME (imported).

    ---- Outputs ----
    List[Path]
        The files saved: none, the figure, or the figure and its master page.

    ---- Globals mutated ----
    None. Writes the two PDFs and prints the outcome; the details of a problem go to
    the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_page_exporter
    master_page_exporter
    problem_shower
    """

    # ---- 1 The figure ----------------------------------------------------------------
    if not page.plots:
        return []
    print('\nDataset figure')
    spec = settings.JOURNAL_SPECS[page.journal]
    try:
        path, figure = figure_page_exporter(page, spec, export_root)
    except Exception as exc:  # the figure must not lose the rest of the run
        problem_shower('  The dataset figure was not saved', exc)
        return []
    width_in, height_in = figure.get_size_inches()
    print(f"  Saved {path.name} ({spec['name']}, {width_in * 25.4:.0f} x "
          f'{height_in * 25.4:.0f} mm)',
          )

    # ---- 2 Its master page -----------------------------------------------------------
    try:
        master = master_page_exporter(figure,
                                      spec,
                                      page.journal,
                                      FIGURE_NAME,
                                      export_root,
                                      )
    except Exception as exc:  # the figure itself is saved
        problem_shower('  The master page of the dataset figure was not saved', exc)
        return [path]
    print(f'  Saved {master.name} (the figure on a page of the journal)')
    return [path, master]


# ---- everything_asker ----------------------------------------------------------------
def everything_asker(folder: Path,
                     summaries: List[dict],
                     export_root: Path,
                     saved: dict,
                     exported: Optional[List[Path]] = None,
                     saved_plots: Optional[List[str]] = None,
                     saved_workbooks: Optional[List[str]] = None,
                     ) -> Tuple[dict,
                                List[dict],
                                Optional[dict],
                                Optional[dict],
                                Optional[List[str]],
                                FigurePage,
                                ]:
    """
    ---- Summary ----
    Main function to ask every question of the run after the files, in numbered
    sections (trimming and ignoring, analysis, plots, summary figures, export), and to
    build the per-file information. The plot and the workbook of every file are saved
    as soon as the figures are finalised and the export chosen (5.9), with the spectra
    when chosen, so the later sections show the plot.

    ---- Inputs ----
    folder : Path
        Data folder, from files_asker.
    summaries : List[dict]
        Summary of each readable file, from files_asker.
    export_root : Path
        Results folder, from files_asker.
    saved : dict
        Settings saved with the dataset, from files_asker; empty for a dataset never
        run.
    exported : Optional[List[Path]]
        List the results folder is added to once an export button of the trimming
        step (3.4) writes into it; None when not needed.
    saved_plots : Optional[List[str]]
        List that holds the names of the files whose plot is saved in the results
        folder before the run starts; None when not needed.
    saved_workbooks : Optional[List[str]]
        List that holds the names of the files whose workbook is written before the
        run starts; None when not needed.

    ---- Globals read ----
    PLACES, JOURNAL_NAMES (module constants); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    Tuple[dict, List[dict], Optional[dict], Optional[dict], Optional[List[str]],
          FigurePage]
        (answers, per-experiment info dictionaries, fit, side-by-side comparison
        settings or None, names of the 2x2 grid experiments or None, the page of the
        dataset figure as built). Raises UserQuitError if the user declines to start.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal; writes last_answers.json through
    last_answers_saver, the settings file of the dataset through
    dataset_settings_saver, the export of the trim step when one is chosen, adding to
    ``exported``, and the plot and the workbook of every file, filling
    ``saved_plots`` and ``saved_workbooks`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    active_gui_getter
    comparison_maker
    dataset_settings_saver
    experiment_files_saver
    file_settings_merger
    haem_name_formatter
    journal_answers_fitter
    last_answers_saver
    page_stage_runner
    section_starter
    viewer_asker
    yes_no_asker
    """

    # ---- 1 Load the settings of the dataset ------------------------------------------
    # A dataset never saved starts from the standard settings (config.py); a dataset
    # saved before starts from the settings kept in its own folder.
    names = [s['name'] for s in summaries]
    # A journal or a width saved with the dataset that the journals folder no longer
    # has is moved to one it has, and the user is told.
    defaults, journal_notes = journal_answers_fitter(dict(settings.DEFAULT_ANSWERS,
                                                          **saved.get('answers', {}),
                                                          ),
                                                     settings.JOURNAL_SPECS,
                                                     )
    for note in journal_notes:
        warning_shower(note)
    answers = dict(defaults)
    remembered = saved.get('files', {})

    # ---- 2 Ask the questions ---------------------------------------------------------
    # ---- 2.1 Trimming and ignoring, analysis and individual plots --------------------
    (limits,
     fit,
     details,
     plotted,
     regions,
     has_spectra,
     ) = viewer_asker(summaries,
                      answers,
                      defaults,
                      remembered,
                      PLACES.fits_folder,
                      export_root,
                      exported,
                      )

    # ---- 2.2 Save the plot and the workbook of every file ----------------------------
    # The figures are finalised and the export chosen (5.9, which wrote the whole
    # recordings' csv files), so the plots and workbooks are saved now, with the
    # trimmed csv files when chosen, and the later sections show each file as it is
    # saved, not as it was last previewed.
    print('  Every experiment gets a workbook with everything worked out for it: the '
          'measured and set oxygen, the OCR, the haems, Δψ, the averages, the events '
          'and your OD/volume/dilution entries.',
          )
    if has_spectra and answers['export_spectra']:
        print('  The trimmed csv files were written by the quick export of the trim '
              'step with these edges, so they are not written again; the workbook of '
              'each experiment lists them.',
              )
    context = {'answers': answers,
               'fit': fit,
               'summaries': summaries,
               'limits': limits,
               'details': details,
               'regions': regions,
               'export_root': export_root,
               'has_spectra': has_spectra,
               }
    plot_fit = fit  # a fit changed later means the files are saved again in the run
    saved_plots = [] if saved_plots is None else saved_plots
    saved_workbooks = [] if saved_workbooks is None else saved_workbooks
    experiment_files_saver(context, saved_plots, active_gui_getter(), saved_workbooks)

    # ---- 2.3 Dataset figures ---------------------------------------------------------
    # The figure builder takes the place of the fixed figures (side by side, the 2x2
    # grid, the time response, the haem and OCR response), whose questions are no
    # longer asked; the page is exported with the dataset figures.
    section_starter('Dataset figures: build a figure')
    page = page_stage_runner(PLACES.layouts_folder)
    comparison, exemplar_names = None, None
    custom = {'time_response': None, 'haem_ocr': None}
    answers['plot_time_response'] = answers['plot_haem_ocr'] = False

    # ---- 3 Read the experiments ------------------------------------------------------
    experiments = []
    for s in summaries:
        name = s['name']
        # the spectra csv files written by the trim step's export or with the workbooks stay listed
        has_spectra_csv = (has_spectra or
                           (bool(answers['export_spectra']) and name in saved_workbooks)
                           )
        info = {'path': s['path'],
                'name': name,
                'duration': s['duration_min'],
                'trim_start': limits[name]['trim_start'],
                'trim_end': limits[name]['trim_end'],
                'ignore_start': limits[name]['ignore_start'],
                'ignore_end': limits[name]['ignore_end'],
                'regions': regions.get(name),
                'custom': {'time_response_group': (custom['time_response'] or {}
                                                   ).get(name),
                           'haem_ocr': name in (custom['haem_ocr'] or []),
                           },
                'exemplar': name in (exemplar_names or []),
                'has_spectra_csv': has_spectra_csv,
                'write_spectra': bool(answers['export_spectra'],
                                      ) and not has_spectra_csv,
                # a plot or workbook saved with the fit of the run is not written again
                'is_plot_saved': name in saved_plots and fit is plot_fit,
                'is_workbook_saved': name in saved_workbooks and fit is plot_fit,
                }
        info['keep'] = ((bool(comparison) and name in comparison['runs']) or
                        info['exemplar'] or
                        bool(info['custom']['time_response_group']) or
                        info['custom']['haem_ocr']
                        )
        info.update(details[name])
        experiments.append(info)

    # ---- 4 Print the summary ---------------------------------------------------------
    section_starter('Dataset export: summary')
    guide_step_starter('start')
    print(f'  Files:           {len(experiments)} from {folder}')
    print(f'  Results to:       {export_root}')
    spans = {}
    for name, v in limits.items():
        if v['trim_start'] or v['trim_end']:
            spans.setdefault((v['trim_start'] or 0, v['trim_end']), []).append(name)
    trimmed = [f"{('all files' if len(names) == len(limits) else ', '.join(names))}: "
               f"{'from %g ' % start if start else ''}{'to %g ' % end if end else ''}"
               f'min'
               for (start, end), names in spans.items()
               ]
    print(f"  Trimmed:          {', '.join(trimmed) or 'none'}")
    ignore_spans = {}
    for name, v in limits.items():
        if v['ignore_start'] or v['ignore_end']:  # files with nothing ignored stay out
            ignore_spans.setdefault((v['ignore_start'] or 0, v['ignore_end'] or 0),
                                    [],
                                    ).append(name)
    ignored = [f"{('all files' if len(names) == len(limits) else ', '.join(names))}: "
               + ', '.join(part
                           for part in (f'first {start:g} min' if start else '',
                                        f'last {end:g} min' if end else '',
                                        )
                           if part
                           )
               for (start, end), names in ignore_spans.items()
               ]
    print(f"  Ignored:          {'; '.join(ignored) or 'none'}")
    fit_text = fit_describer(answers['fit_file'], answers['haem_files'])
    print(f'  Decomposition:    '
          f"{fit_text if answers['decompose'] else 'no'}, "
          f"{BACKGROUND_SHORT_NAMES.get(answers['haem_background'], '?')} background",
          )
    print(f"  OD scaling:       {'yes' if answers['normalise_od'] else 'no'}")
    print(f"  Temperature:      {answers['temperature_c']:g} °C")
    psi_text = 'yes, for the files with both regions' if answers['delta_psi'] else 'no'
    print(f'  Δψ:               {psi_text}')
    averaging_text = 'none'
    if answers['averaging']:
        kinds = []
        if answers['settled_windows']:
            kinds.append('settled, %g s long, ending %g s before the next addition'
                         % (round(answers['window_minutes'] * 60.0, 2),
                            round(answers['gap_minutes'] * 60.0, 2),
                            ),
                         )
        if answers['quick_windows']:
            kinds.append('quick, %g s long, starting %g s after their addition'
                         % (round(answers['quick_minutes'] * 60.0, 2),
                            round(answers['delay_minutes'] * 60.0, 2),
                            ),
                         )
        if answers.get('each_window'):
            kinds.append('some regions set on their own or left out')
        if answers.get('file_windows'):
            count = len(answers['file_windows'])
            kinds.append(f"fixed by hand in {count} file{'' if count == 1 else 's'}")
        averaging_text = '; '.join(kinds)
    print(f'  Averaging regions: {averaging_text}')
    haem_names = [haem_name_formatter(name) for name in answers['haems']]
    shown = [name
             for name, on in (('O2', answers['plot_o2']),
                              (f"OCR ({answers['ocr_mode']})", answers['plot_ocr']),
                              (f"haems {', '.join(haem_names)} ("
                               f"{answers['haem_mode']})",
                               answers['plot_haems'],
                               ),
                              )
             if on
             ]
    print(f"  Plots:            {'; '.join(shown) or 'none'}")
    print(f"  Individual:       {JOURNAL_NAMES[answers['journal']]}, "
          f"{answers['columns']:g} column(s), height {answers['height']:g} of a page",
          )
    if comparison:
        print(f"  Side by side:     {comparison['runs'][0]} (a) vs "
              f"{comparison['runs'][1]} (b), "
              f"{JOURNAL_NAMES[answers['comparison_journal']]}, "
              f"{comparison['columns']:g} column(s), height {comparison['height']:g}",
              )
    if exemplar_names:
        print(f"  2x2 grid:         run {answers['ho_exemplar_run']}, "
              f"{JOURNAL_NAMES[answers['ex_journal']]}, {answers['ho_ex_columns']:g} "
              f"column(s), height {answers['ho_ex_height']:g}",
              )
    if answers['plot_time_response']:
        print(f"  Time response:    groups {', '.join(answers['tr_groups'])}, "
              f"{JOURNAL_NAMES[answers['tr_journal']]}, {answers['tr_columns']:g} "
              f"column(s), height {answers['tr_height']:g}",
              )
    if answers['plot_haem_ocr']:
        print(f"  Haem and OCR:     {len(custom['haem_ocr'])} file(s), "
              f"{JOURNAL_NAMES[answers['ho_journal']]}, {answers['ho_pub_columns']:g} "
              f"column(s), height {answers['ho_pub_height']:g}",
              )
    spectra_text = {'trimmed': ' + the trimmed csv',
                    'full': ' + the trimmed and full csv',
                    }.get(answers.get('export_choice'), '')
    written = len(saved_workbooks) if fit is plot_fit else 0
    workbooks_text = (f'written for {written} of {len(names)} file(s), with every table'
                      if written
                      else 'every table, written when the run starts'
                      )
    print(f'  Workbooks:        {workbooks_text}{spectra_text}')
    if page.plots:
        count = len(page.plots)
        print(f"  Dataset figure:   {count} plot{'' if count == 1 else 's'}, "
              f'{JOURNAL_NAMES[page.journal]}, {page.columns:g} column(s), height '
              f'{page.height:g}; saved as a PDF with its master page',
              )

    # ---- 5 Confirm the start ---------------------------------------------------------
    if not yes_no_asker('Do you want to start?', True, number='9.1'):
        raise UserQuitError()

    # ---- 6 Remember the answers ------------------------------------------------------
    last_answers_saver({'data_folder': str(folder.resolve())})
    if not dataset_settings_saver(folder,
                                  export_root,
                                  file_settings_merger(remembered,
                                                       limits,
                                                       details,
                                                       regions,
                                                       ),
                                  {k: v
                                   for k, v in answers.items()
                                   if k not in ('haems', 'ho_haems') or v
                                   },
                                  ):
        print(f'  The settings could not be saved in {folder} (the folder cannot be '
              f'written to), so this dataset will start from the standard settings '
              f'next time.',
              )
    return answers, experiments, fit, comparison, exemplar_names, page


# ---- experiment_file_saver -----------------------------------------------------------
def experiment_file_saver(info: dict,
                          cfg: settings.Config,
                          fit: Optional[dict],
                          export_root: Path,
                          ) -> Tuple[Optional[bytes], bool]:
    """
    ---- Summary ----
    Main function to read and process one .paf file once, then save its plot as the run
    does, handing back a picture of it for the window, and write its workbook. A plot
    that cannot be saved is said in one sentence and the workbook is still written.

    ---- Inputs ----
    info : dict
        Per-file information: path, name, trim and ignore times, OD values, events and
        regions (preview_info_builder), with write_spectra and has_spectra_csv
        (experiment_workbook_saver).
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    export_root : Path
        Results folder.

    ---- Globals read ----
    settings.PREVIEW_DPI.

    ---- Outputs ----
    Tuple[Optional[bytes], bool]
        (PNG picture of the saved plot, or None when the file has nothing to plot (no
        oxygen, no OCR and no haems) or its plot could not be saved; True when the
        workbook was written). Raises what the reading and processing raise.

    ---- Globals mutated ----
    None. Writes the figure files, the workbook and the spectra files; what the
    processing and the plot print is kept from the terminal, as the run says it
    again (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_plotter
    experiment_workbook_saver
    output_capturer
    problem_shower
    """

    # ---- 1 Read and process the file -------------------------------------------------
    a = cfg.answers
    with output_capturer():
        processed = experiment_data_processor(info, cfg, fit)

    # ---- 2 Save the plot -------------------------------------------------------------
    picture = None
    haem_source = processed['plotted_haem_source']
    if a['plot_o2'] or a['plot_ocr'] or haem_source is not None:
        try:
            with output_capturer():
                # a figure of its own (not pyplot's), so the picture can be taken after
                # the save
                figure = Figure(dpi=cfg.FIGURE_DPI)
                experiment_plotter(processed['experiment'],
                                   cfg.plot_config_builder(processed['vo2_source'],
                                                           haem_source,
                                                           info['ignore_start'],
                                                           info['ignore_end'],
                                                           delta_psi=a['delta_psi'],
                                                           ),
                                   export_root,
                                   figure,
                                   )
                buffer = io.BytesIO()
                figure.savefig(buffer, format='png', dpi=settings.PREVIEW_DPI)
            picture = buffer.getvalue()
        except Exception as exc:  # a plot problem must not lose the workbook
            problem_shower(f"  The plot of {info['name']} was not saved (it is tried "
                           f'again when the run starts)',
                           exc,
                           )

    # ---- 3 Write the workbook --------------------------------------------------------
    is_written = experiment_workbook_saver(processed['experiment'],
                                           info,
                                           cfg,
                                           export_root,
                                           'it is tried again when the run starts',
                                           )
    return picture, is_written


# ---- experiment_files_saver ----------------------------------------------------------
def experiment_files_saver(context: dict,
                           saved_plots: List[str],
                           window: Any,
                           saved_workbooks: Optional[List[str]] = None,
                           ) -> None:
    """
    ---- Summary ----
    Main function to save the plot and write the workbook of every file with the
    answers so far, once the processing and the figure are accepted, and to show each
    saved plot in the window. The spectra are written as csv files the first time
    only, when they were chosen. A file that cannot be read says so in one sentence and
    the others carry on; what was not saved is tried again in the run.

    ---- Inputs ----
    context : dict
        {answers, fit, summaries, limits, details, regions, export_root, has_spectra}
        of the run so far (everything_asker); has_spectra is True when the spectra
        csv files are written already, and is set once they are written here.
    saved_plots : List[str]
        List emptied, then filled with the name of each file whose plot was saved.
    window : Any
        The browser window, which is given each saved plot; None shows nothing.
    saved_workbooks : Optional[List[str]]
        List emptied, then filled with the name of each file whose workbook was
        written; None keeps no list.

    ---- Globals read ----
    plt (matplotlib.pyplot).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style, writes the figure files,
    the workbooks and the spectra files, prints its progress, fills ``saved_plots``
    and ``saved_workbooks`` and sets has_spectra in ``context`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_file_saver
    info_printer
    preview_info_builder
    problem_shower
    """

    # ---- 1 Set up the figure style ---------------------------------------------------
    cfg = settings.Config(context['answers'])
    plt.rcParams.update(cfg.RC_PARAMS)
    summaries = context['summaries']
    has_spectra = bool(context.get('has_spectra'))
    write_spectra = bool(context['answers'].get('export_spectra')) and not has_spectra
    saved_workbooks = [] if saved_workbooks is None else saved_workbooks
    del saved_plots[:]
    del saved_workbooks[:]
    info_printer(f"Saving the plot and the workbook of each file in "
                 f"{context['export_root']} (each file is read again, so this can take "
                 f'a moment) ...',
                 )

    # ---- 2 Save the plot and the workbook of each file -------------------------------
    for number, summary in enumerate(summaries, start=1):
        name = summary['name']
        info_printer(f'Saving file {number} of {len(summaries)}: {name}', depth=2)
        info = preview_info_builder(summary,
                                    context['limits'],
                                    context['details'],
                                    context.get('regions'),
                                    )
        info.update(write_spectra=write_spectra, has_spectra_csv=has_spectra)
        try:
            picture, is_written = experiment_file_saver(info,
                                                        cfg,
                                                        context['fit'],
                                                        context['export_root'],
                                                        )
        except Exception as exc:  # one file must not stop the questions
            problem_shower(f'  The plot and the workbook of {name} were not saved '
                           f'(they are tried again when the run starts)',
                           exc,
                           )
            continue
        finally:
            plt.close('all')
            gc.collect()
        if is_written:
            saved_workbooks.append(name)
        if picture is None:
            continue
        saved_plots.append(name)
        if window is not None:
            window.saved_plot_publisher(name, picture)

    # ---- 3 The spectra are written once ----------------------------------------------
    # Written again later (new averaging windows), the workbooks list them.
    if write_spectra:
        context['has_spectra'] = True


# ---- experiment_processor ------------------------------------------------------------
def experiment_processor(info: dict,
                         cfg: settings.Config,
                         fit: Optional[dict],
                         export_root: Path,
                         unsaved: Optional[List[str]] = None,
                         ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to read, process, plot and export one .paf file. Each step reports its
    own problem so the next step still runs: a figure or a workbook that could not be
    saved does not take the file out of the later figures.

    ---- Inputs ----
    info : dict
        Per-file information from everything_asker: path, name, trim and ignore times,
        OD values, events, custom and keep flags, is_plot_saved and is_workbook_saved
        (True when the plot or the workbook was saved once the figure was accepted, so
        it is not written again), write_spectra and has_spectra_csv.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    export_root : Path
        Results folder.
    unsaved : Optional[List[str]]
        List the file's name is added to when its workbook could not be saved (open
        in Excel, a full disk); None keeps no list.

    ---- Globals read ----
    plt (matplotlib.pyplot).

    ---- Outputs ----
    Optional[dict]
        {experiment, vo2_source, haem_source, prepared} when the experiment is needed
        again for the comparison or special figures (info["keep"]), otherwise None.

    ---- Globals mutated ----
    None. Writes the figure and the workbook files, prints progress and adds to
    ``unsaved`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_plotter
    experiment_preparer
    experiment_workbook_saver
    plot_config_builder
    problem_shower
    """

    # ---- 1 Set up the run ------------------------------------------------------------
    a = cfg.answers
    name = info['name']
    ignore_first, ignore_last = info['ignore_start'], info['ignore_end']
    print(f'\nProcessing: {name}')

    # ---- 2 Read and process the data -------------------------------------------------
    processed = experiment_data_processor(info, cfg, fit)
    experiment = processed['experiment']
    od_available = processed['od_available']
    vo2_source = processed['vo2_source']
    plotted_haem_source = processed['plotted_haem_source']

    # ---- 6 Plot the experiment -------------------------------------------------------
    # Figure. A plot saved once its questions were accepted is not drawn again.
    if info.get('is_plot_saved'):
        print('  Plot already saved.')
    elif a['plot_o2'] or a['plot_ocr'] or plotted_haem_source is not None:
        try:
            print('  Plotting ...')
            experiment_plotter(experiment,
                               cfg.plot_config_builder(vo2_source,
                                                       plotted_haem_source,
                                                       ignore_first,
                                                       ignore_last,
                                                       delta_psi=a['delta_psi'],
                                                       ),
                               export_root,
                               )
        except Exception as exc:  # a figure problem must not lose the data export
            problem_shower('  Figure not made', exc)
            plt.close('all')

    # ---- 7 Export the workbook -------------------------------------------------------
    # A workbook saved once the figure was accepted is not written again. One that
    # cannot be written (open in Excel, a full disk) must not lose the file from the
    # later figures: its data was worked out all the same.
    if info.get('is_workbook_saved'):
        print('  Workbook already saved.')
    elif not experiment_workbook_saver(experiment,
                                       info,
                                       cfg,
                                       export_root,
                                       'the figures still use this file',
                                       ):
        if unsaved is not None:
            unsaved.append(name)

    # ---- 8 Prepare the special figures -----------------------------------------------
    # the special figures
    prepared = experiment_preparer(experiment, info['custom'], a, fit, od_available)
    if info.get('keep'):  # needed again for the comparison and special figures
        experiment['raw_spectra'] = {}
        for item in prepared.values():
            if item is not None:
                item['raw_spectra'] = {}
        return {'experiment': experiment,
                'vo2_source': vo2_source,
                'haem_source': plotted_haem_source,
                'prepared': prepared,
                }
    return None


# ---- experiment_workbook_saver -------------------------------------------------------
def experiment_workbook_saver(experiment: dict,
                              info: dict,
                              cfg: settings.Config,
                              export_root: Path,
                              later: str,
                              ) -> bool:
    """
    ---- Summary ----
    Main function to write the workbook of one processed file, with the trimming, the
    fit and when it was processed in its metadata, and its spectra as csv files when
    they are to be written. A workbook that cannot be written (open in Excel, a full
    disk) is said in one sentence, with what happens instead.

    ---- Inputs ----
    experiment : dict
        The processed experiment (experiment_data_processor); its metadata is added
        to.
    info : dict
        Per-file information: name, ignore_start, ignore_end, write_spectra (True to
        write the spectra as csv files) and has_spectra_csv (True when they were
        written before, so the workbook lists them).
    cfg : settings.Config
        Settings derived from the answers (decompose, fit_file, haem_files,
        haem_background).
    export_root : Path
        Results folder.
    later : str
        What happens when the workbook cannot be written, said in brackets after the
        sentence, such as 'the figures still use this file'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the workbook was written.

    ---- Globals mutated ----
    None. Writes the workbook and the spectra files and prints to the terminal; the
    details of a problem go to the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_workbook_exporter
    fit_describer
    problem_shower
    """

    a = cfg.answers
    experiment['metadata'].update({
        'ignore_first_minutes': info['ignore_start'],
        'ignore_last_minutes': info['ignore_end'],
        'fit_file': (fit_describer(a['fit_file'], a['haem_files'])
                     if a['decompose']
                     else None
                     ),
        'haem_background': (BACKGROUND_SHORT_NAMES.get(a['haem_background'],
                                                       a['haem_background'],
                                                       )
                            if a['decompose']
                            else None
                            ),
        'processed': datetime.now().strftime('%Y-%m-%d %H:%M'),
        },
                                  )
    print('  Exporting ...')
    try:
        experiment_workbook_exporter(experiment,
                                     export_root,
                                     spectra=bool(info.get('write_spectra')),
                                     keeps_spectra_list=bool(
                                         info.get('has_spectra_csv'),
                                         ),
                                     )
    except OSError as exc:
        problem_shower(f"  The workbook of {info['name']} was not saved ({later})", exc)
        return False
    return True


# ---- last_answers_loader -------------------------------------------------------------
def last_answers_loader() -> dict:
    """
    ---- Summary ----
    Main function to read which data folder was used in the last run.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PLACES (module constant; its last_answers_file).

    ---- Outputs ----
    dict
        Contents of last_answers.json ({data_folder}); an empty dict when the file is
        missing or unreadable. The answers themselves are kept with each dataset
        (utils_shared.dataset_settings).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        return json.loads(PLACES.last_answers_file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


# ---- last_answers_saver --------------------------------------------------------------
def last_answers_saver(values: dict) -> None:
    """
    ---- Summary ----
    Main function to remember the data folder of this run for the next one.

    ---- Inputs ----
    values : dict
        Content to write to last_answers.json: {data_folder}.

    ---- Globals read ----
    PLACES (module constant; its last_answers_file).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes last_answers.json (side effect); a read-only folder is ignored
    silently.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        PLACES.last_answers_file.write_text(json.dumps(values, indent=2),
                                            encoding='utf-8',
                                            )
    except OSError:
        pass  # a read-only folder just means the defaults are not remembered


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function of the program: run it in the experiment browser window (terminal on
    the left, plots on the right). Portimao needs its window: when it cannot open, one
    sentence says why and what to do, and nothing is asked. With the check switch
    (PORTIMAO_SELF_TEST set to any value) it only checks that the window opens and shows
    a made-up preview, then closes by itself. The Mac app first makes its own folder and
    sends what it prints to its log; it has no terminal, so when its folder cannot be
    made or the window cannot open, a message says what to do.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PLACES, PROGRAM_TITLE, WINDOW_TITLE (module constants);
    os.environ['PORTIMAO_SELF_TEST'].

    ---- Outputs ----
    int
        0 when every file finished, 1 when the run was cancelled, a file failed, the
        app's own folder could not be made or the window could not open. With the check
        switch: 0 when the check passed, 1 when it failed.

    ---- Globals mutated ----
    None. Opens the window, or prints why it could not; the app makes its own folder
    and replaces sys.stdout and sys.stderr by its log; the app may show a message; the
    details of a problem met before a run is logged go to the error stream it starts
    with (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    app_output_logger
    details_place_setter
    gui_runner
    program_runner
    self_test_runner
    start_problem_shower
    user_folder_preparer
    """

    try:
        user_folder_preparer(PLACES)
    except OSError:
        start_problem_shower(f'Portimao could not make its folder {PLACES.own_folder}: '
                             f'check that your home folder can be written to, then '
                             f'open Portimao again.',
                             PLACES,
                             )
        return 1
    app_output_logger(PLACES)
    # until a run is logged, the details of a problem go where the start-up output goes
    if sys.stderr is not None and sys.stderr.isatty():
        details_place_setter(sys.stderr, 'the terminal Portimao was started from')
    else:
        details_place_setter(sys.stderr,
                             'the start-up log (logs/launch.log in the Portimao folder'
                             + (' in your home folder)' if PLACES.is_app else ')'),
                             )
    if os.environ.get('PORTIMAO_SELF_TEST'):
        # Imported only for the check, so a normal start never depends on its file.
        from utils_viewer.viewer_self_test import self_test_runner
        return self_test_runner(PROGRAM_TITLE, PLACES)
    try:
        return gui_runner(program_runner, WINDOW_TITLE)
    except GuiUnavailableError as exc:
        if PLACES.is_app:  # the reason says what to do from source, not in the app
            print(f'The window could not open: {exc}.')
            sentence = f"Portimao's window could not open: {SEND_DETAILS}."
        else:
            sentence = f'Portimao needs its window, which could not open: {exc}.'
        start_problem_shower(sentence, PLACES)
        return 1


# ---- program_runner ------------------------------------------------------------------
def program_runner() -> int:
    """
    ---- Summary ----
    Main function to run the program: ask for the files, start the log in the results
    folder, ask the other questions, process every file, then draw the comparison and
    special figures. The log keeps each answer from the results folder on, also when
    the run is cancelled or the window closed part way.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PLACES, PROGRAM_TITLE (written to the log), UPDATE_NOTE (module constants).

    ---- Outputs ----
    int
        0 when every file finished, 1 when the run was cancelled, a file failed or a
        workbook could not be saved.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal, sets the matplotlib rcParams, writes
    results and a log file, and replaces sys.stdout and sys.stderr while logging (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    cancel_sentence_builder
    comparison_maker
    dataset_figure_saver
    everything_asker
    experiment_processor
    files_asker
    last_answers_loader
    logging_starter
    logging_stopper
    problem_shower
    section_starter
    settings_logger
    special_figures_maker
    warning_shower
    """

    # ---- 1 Make the output safe for symbols ------------------------------------------
    for stream in (sys.stdout, sys.stderr):
        try:
            # symbols such as the delta never stop the program
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass

    # ---- 2 Ask for the files ---------------------------------------------------------
    print(PROGRAM_TITLE)
    if UPDATE_NOTE:
        print(UPDATE_NOTE)
    for problem in settings.JOURNAL_PROBLEMS:  # a journal file that cannot be used
        warning_shower(problem)
    section_starter('Import')
    try:
        folder, summaries, export_root, saved = files_asker(last_answers_loader(),
                                                            PLACES.own_folder,
                                                            )
    except UserQuitError:
        print('\nCancelled. Nothing was changed.')
        return 1

    # ---- 3 Ask the other questions, logged -------------------------------------------
    # the log starts as soon as it has a folder, so the answers are kept even when
    # Portimao is closed before the run
    log_session = logging_starter(export_root, PROGRAM_TITLE, folder)
    failed = []
    unsaved: List[str] = []  # files whose workbook could not be saved
    kept = {}
    exported: List[Path] = []  # the trim step's export adds the results folder
    saved_plots: List[str] = []  # the files whose plot is saved before the run
    saved_workbooks: List[str] = []  # the files whose workbook is written before it
    try:
        try:
            (answers,
             experiments,
             fit,
             comparison,
             exemplar_names,
             page,
             ) = everything_asker(folder,
                                  summaries,
                                  export_root,
                                  saved,
                                  exported,
                                  saved_plots,
                                  saved_workbooks,
                                  )
        except UserQuitError:
            changed = cancel_sentence_builder(exported,
                                              saved_plots,
                                              export_root,
                                              saved_workbooks,
                                              )
            print(f"\nCancelled. {changed}; the questions you answered are in the log "
                  f"{log_session['log_path'].name} in the logs folder of the results "
                  f'folder.',
                  )
            return 1

        # ---- 4 Set up the run --------------------------------------------------------
        settings_logger(log_session, answers)
        cfg = settings.Config(answers)
        plt.rcParams.update(cfg.RC_PARAMS)
        start = time.perf_counter()

        # ---- 5 Process every file ----------------------------------------------------
        for warning in cfg.STYLE_WARNINGS:
            warning_shower(warning)
        for info in experiments:
            try:
                result = experiment_processor(info, cfg, fit, export_root, unsaved)
                if result:
                    kept[info['name']] = result
            except Exception as exc:
                problem_shower(f"  {info['name']} was not finished", exc)
                failed.append(info['name'])
            finally:
                plt.close('all')
                gc.collect()
        if comparison:
            comparison_maker(comparison, kept, cfg, export_root)
        special_figures_maker(kept, cfg, fit, export_root, exemplar_names)
        dataset_figure_saver(page, export_root)
        minutes, seconds = divmod(time.perf_counter() - start, 60)
        print(f'\nFinished {len(experiments) - len(failed)} of {len(experiments)} '
              f'file(s) in {int(minutes)} min {seconds:.0f} s.',
              )
        if failed:
            print('Not completed: ' + ', '.join(failed) + ' (the reason for each is '
                  'above)',
                  )
        if unsaved:
            warning_shower('Workbook not saved for: ' + ', '.join(unsaved) + '. Close '
                           'these workbooks in Excel and run Portimao again to write '
                           'them; the figures were made with these files.',
                           )
        print(f'Results are in: {export_root}')
    finally:
        logging_stopper(log_session)
    return 1 if failed or unsaved else 0


# ---- special_figures_maker -----------------------------------------------------------
def special_figures_maker(kept: dict,
                          cfg: settings.Config,
                          fit: Optional[dict],
                          export_root: Path,
                          exemplar_names: Optional[List[str]],
                          is_preview: bool = False,
                          ) -> None:
    """
    ---- Summary ----
    Main function to draw the time response, haem and OCR response and 2x2 grid figures;
    each is skipped, with the reason, if it cannot be made.

    ---- Inputs ----
    kept : dict
        Results of experiment_processor keyed by experiment name.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    export_root : Path
        Results folder.
    exemplar_names : Optional[List[str]]
        Names of the four experiments of the 2x2 grid, or None.
    is_preview : bool
        True to draw the figures only (for the experiment browser): no workbook is
        written.

    ---- Globals read ----
    settings.Config; time_response_runner, ocr_and_haem_response_runner and
    exemplar_runner (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the figure files and prints the outcome (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    exemplar_runner
    ocr_and_haem_response_runner
    problem_shower
    time_response_runner
    warning_shower
    """

    # ---- 1 Set up the figures --------------------------------------------------------
    a = cfg.answers
    journals = {'time_response': 'tr_journal', 'haem_ocr': 'ho_journal'}

    # ---- 2 Draw the summary figures --------------------------------------------------
    for key, enabled, title, runner in (('time_response',
                                         a['plot_time_response'],
                                         'Time response',
                                         time_response_runner,
                                         ),
                                        ('haem_ocr',
                                         a['plot_haem_ocr'],
                                         'Haem and OCR response',
                                         ocr_and_haem_response_runner,
                                         ),
                                        ):
        if not enabled:
            continue
        print(f'\n{title}')
        prepared = {name: item['prepared'][key]
                    for name, item in kept.items()
                    if item['prepared'].get(key) is not None
                    }
        if len(prepared) < 2:
            warning_shower(f'  Not made: only {len(prepared)} file(s) could be '
                           f'prepared (at least two are needed).',
                           )
            continue
        try:
            figure_cfg = settings.Config(dict(a, journal=a[journals[key]]))
            runner(prepared, figure_cfg, a, fit, export_root, is_preview)
        except Exception as exc:  # one special figure must not stop the others
            problem_shower('  Not made', exc)
            plt.close('all')

    # ---- 3 Draw the exemplar figure --------------------------------------------------
    if a['plot_exemplar']:
        print('\n2x2 figure')
        chosen = {name: kept[name] for name in (exemplar_names or []) if name in kept}
        if len(chosen) < 4:
            warning_shower(f'  Not made: only {len(chosen)} of the four experiments '
                           f'finished.',
                           )
            return
        try:
            exemplar_runner(chosen,
                            settings.Config(dict(a, journal=a['ex_journal'])),
                            a,
                            fit,
                            export_root,
                            )
        except Exception as exc:
            problem_shower('  Not made', exc)
            plt.close('all')


if __name__ == '__main__':
    sys.exit(main())
