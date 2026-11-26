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
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')  # figures are saved to files; no window is needed
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.app_messages import SEND_DETAILS, start_problem_shower
from utils_shared.dataset_settings import dataset_settings_saver, file_settings_merger
from utils_shared.dataset_setup import setup_plainer
from utils_shared.dataset_workbook_exporter import dataset_workbook_exporter
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.figure_page import (FIGURE_NAME,
                                      figure_page_exporter,
                                      FigurePage,
                                      page_plainer,
                                      )
from utils_shared.individual_experiment_exporter import experiment_workbook_exporter
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.journal_files import journal_answers_fitter
from utils_shared.master_page_exporter import master_page_exporter
from utils_shared.output_capture import output_capturer
from utils_shared.page_data import experiment_slimmer, page_experiments_lister
# loading page_plots also adds the plot types to the page
from utils_shared.page_plots import (response_checks_lister,
                                     traces_left_out_lister,
                                     waterfall_left_out_lister,
                                     )
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
from utils_viewer.viewer_stages import (page_stage_runner,
                                        setup_stage_runner,
                                        viewer_asker,
                                        )


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


# ---- dataset_figure_saver ------------------------------------------------------------
def dataset_figure_saver(page: FigurePage,
                         export_root: Path,
                         setup: Optional[dict] = None,
                         experiments: Optional[Dict[str, dict]] = None,
                         answers: Optional[dict] = None,
                         ) -> List[Path]:
    """
    ---- Summary ----
    Main function to save the dataset figure built on the page: the figure as a PDF of
    its printed size, with text that can still be changed, then its master page, the
    figure on a page of its journal, then its workbook, the numbers of its plots and
    its tests. A page with no plot saves nothing. A file that cannot be saved is said
    in one sentence and the run goes on. An experiment a plot
    shows that could not be read when the plots were saved is named in one warning,
    and the plot is drawn without it; so is an experiment a waterfall leaves out for
    having no difference spectrum, and one a mean trace (or a waterfall of traces)
    leaves out for having nothing to show or another number of additions.

    ---- Inputs ----
    page : FigurePage
        The page as built in the Build a figure step.
    export_root : Path
        Results folder.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Optional[Dict[str, dict]]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md), kept when
        the plot and the workbook of each file were saved; None for none.
    answers : Optional[dict]
        The answers of the run, for the plots drawn as the run was set up; None for
        none.

    ---- Globals read ----
    settings.JOURNAL_SPECS; FIGURE_NAME (imported).

    ---- Outputs ----
    List[Path]
        The files saved: none when the figure could not be saved; otherwise the
        figure, then its master page and its workbook, each when it was saved.

    ---- Globals mutated ----
    None. Writes the two PDFs and the workbook and prints the outcome; the details
    of a problem go to the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    dataset_workbook_exporter
    figure_page_exporter
    master_page_exporter
    page_experiments_lister
    problem_shower
    response_checks_lister
    traces_left_out_lister
    warning_shower
    waterfall_left_out_lister
    """

    # ---- 1 The figure ----------------------------------------------------------------
    if not page.plots:
        return []
    print('\nDataset figure')
    spec = settings.JOURNAL_SPECS[page.journal]
    missing = [name
               for name in page_experiments_lister(page, setup)
               if name not in (experiments or {})
               ]
    if missing:
        warning_shower(f"  The dataset figure is drawn without {', '.join(missing)}: "
                       f"{'it' if len(missing) == 1 else 'they'} could not be read "
                       f'when the plots were saved (the reason is above). Run '
                       f'Portimao again once that is put right.',
                       )
    left_out = waterfall_left_out_lister(page, setup, experiments or {})
    if left_out:
        warning_shower(f"  The waterfall is drawn without {', '.join(left_out)}: "
                       f"{'it has' if len(left_out) == 1 else 'they have'} no "
                       f'difference spectrum, which needs an oxidised and a reduced '
                       f'region. Set both regions for '
                       f"{'it' if len(left_out) == 1 else 'them'} to have "
                       f"{'it' if len(left_out) == 1 else 'them'} in the waterfall.",
                       )
    left_out = traces_left_out_lister(page, setup, experiments or {}, answers or {})
    if left_out:
        warning_shower(f"  The mean of the traces is worked out without "
                       f"{', '.join(left_out)}: "
                       f"{'it has' if len(left_out) == 1 else 'they have'} nothing "
                       f'for the trace and value picked, or another number of '
                       f'additions than the other experiments of the plot, so '
                       f"{'its' if len(left_out) == 1 else 'their'} additions cannot "
                       f'be lined up with theirs.',
                       )
    checks = response_checks_lister(page, setup, experiments or {}, answers or {})
    left_out, differing = checks['left_out'], checks['differing']
    if left_out:
        warning_shower(f"  The response by region is worked out without "
                       f"{', '.join(left_out)}: "
                       f"{'it has' if len(left_out) == 1 else 'they have'} another "
                       f'number of additions than most experiments of the plot, so '
                       f"{'its' if len(left_out) == 1 else 'their'} regions are not "
                       f'the same as theirs.',
                       )
    if differing:
        warning_shower(f'  The regions of the response by region are named by the '
                       f'additions of the first experiment of the plot, but '
                       f"{', '.join(differing)} "
                       f"{'has' if len(differing) == 1 else 'have'} other additions. "
                       f'Check that the experiments of the plot belong together.',
                       )
    try:
        path, figure = figure_page_exporter(page,
                                            spec,
                                            export_root,
                                            setup,
                                            experiments,
                                            answers,
                                            )
    except Exception as exc:  # the figure must not lose the rest of the run
        problem_shower('  The dataset figure was not saved', exc)
        return []
    width_in, height_in = figure.get_size_inches()
    print(f"  Saved {path.name} ({spec['name']}, {width_in * 25.4:.0f} x "
          f'{height_in * 25.4:.0f} mm)',
          )

    # ---- 2 Its master page -----------------------------------------------------------
    saved = [path]
    try:
        master = master_page_exporter(figure,
                                      spec,
                                      page.journal,
                                      FIGURE_NAME,
                                      export_root,
                                      )
    except Exception as exc:  # the figure itself is saved
        problem_shower('  The master page of the dataset figure was not saved', exc)
    else:
        print(f'  Saved {master.name} (the figure on a page of the journal)')
        saved.append(master)

    # ---- 3 Its workbook --------------------------------------------------------------
    try:
        workbook = dataset_workbook_exporter(page,
                                             export_root,
                                             setup,
                                             experiments,
                                             answers,
                                             )
    except Exception as exc:  # the figure itself is saved
        problem_shower('  The workbook of the dataset figure was not saved', exc)
    else:
        print(f'  Saved {workbook.name} (the numbers of the figure and its tests, to '
              f'check by hand)',
              )
        saved.append(workbook)
    return saved


# ---- everything_asker ----------------------------------------------------------------
def everything_asker(folder: Path,
                     summaries: List[dict],
                     export_root: Path,
                     saved: dict,
                     exported: Optional[List[Path]] = None,
                     saved_plots: Optional[List[str]] = None,
                     saved_workbooks: Optional[List[str]] = None,
                     page_data: Optional[dict] = None,
                     ) -> Tuple[dict,
                                List[dict],
                                Optional[dict],
                                FigurePage,
                                ]:
    """
    ---- Summary ----
    Main function to ask every question of the run after the files, in numbered
    sections (trimming and ignoring, analysis, plots, export, dataset figures), and to
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
    page_data : Optional[dict]
        Dictionary that gets what the dataset figure is drawn from: 'setup' (the
        set-up table, dataset_setup) and 'experiments' ({experiment name: its slim
        copy}, page_experiment, DATA_FORMAT.md); None when not needed.

    ---- Globals read ----
    PLACES, JOURNAL_NAMES (module constants); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    Tuple[dict, List[dict], Optional[dict], FigurePage]
        (answers, per-experiment info dictionaries, fit, the page of the dataset
        figure as built). Raises UserQuitError if the user declines to start.

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
    dataset_settings_saver
    experiment_files_saver
    file_settings_merger
    haem_name_formatter
    journal_answers_fitter
    last_answers_saver
    page_plainer
    page_stage_runner
    section_starter
    setup_plainer
    setup_stage_runner
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
               # the slim copy of each file, kept for the plots of the dataset figure
               'page_experiments': {},
               }
    plot_fit = fit  # a fit changed later means the files are saved again in the run
    saved_plots = [] if saved_plots is None else saved_plots
    saved_workbooks = [] if saved_workbooks is None else saved_workbooks
    experiment_files_saver(context, saved_plots, active_gui_getter(), saved_workbooks)

    # ---- 2.3 Dataset figures ---------------------------------------------------------
    # Which experiment is which comes first: the plots of the page split the
    # experiments into sets by it.
    section_starter('Dataset figures: set-up')
    setup = setup_stage_runner(names, saved.get('setup'))
    section_starter('Dataset figures: build a figure')
    page = page_stage_runner(PLACES.layouts_folder,
                             setup,
                             context['page_experiments'],
                             answers,
                             saved.get('page'),
                             )
    if page_data is not None:
        page_data.update(setup=setup, experiments=context['page_experiments'])

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
                'has_spectra_csv': has_spectra_csv,
                'write_spectra': bool(answers['export_spectra'],
                                      ) and not has_spectra_csv,
                # a plot or workbook saved with the fit of the run is not written again
                'is_plot_saved': name in saved_plots and fit is plot_fit,
                'is_workbook_saved': name in saved_workbooks and fit is plot_fit,
                }
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
                                   if k != 'haems' or v
                                   },
                                  setup_plainer(setup, saved.get('setup')),
                                  page_plainer(page),
                                  ):
        print(f'  The settings could not be saved in {folder} (the folder cannot be '
              f'written to), so this dataset will start from the standard settings '
              f'next time.',
              )
    return answers, experiments, fit, page


# ---- experiment_file_saver -----------------------------------------------------------
def experiment_file_saver(info: dict,
                          cfg: settings.Config,
                          fit: Optional[dict],
                          export_root: Path,
                          page_experiments: Optional[Dict[str, dict]] = None,
                          ) -> Tuple[Optional[bytes], bool]:
    """
    ---- Summary ----
    Main function to read and process one .paf file once, then save its plot as the run
    does, handing back a picture of it for the window, and write its workbook. A plot
    that cannot be saved is said in one sentence and the workbook is still written.
    A slim copy of the file is kept for the plots of the dataset figure, so the file
    is not read again for them.

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
    page_experiments : Optional[Dict[str, dict]]
        Dictionary that gets the slim copy of the file under its name
        (page_experiment, DATA_FORMAT.md); None keeps none.

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
    experiment_slimmer
    experiment_workbook_saver
    output_capturer
    problem_shower
    """

    # ---- 1 Read and process the file -------------------------------------------------
    a = cfg.answers
    with output_capturer():
        processed = experiment_data_processor(info, cfg, fit)
    if page_experiments is not None:
        page_experiments[info['name']] = experiment_slimmer(processed['experiment'],
                                                            a.get(
                                                                'decomposition_dataset',
                                                                ),
                                                            fit,
                                                            a.get('haem_background'),
                                                            settings.HAEM_FACTOR,
                                                            )

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
        csv files are written already, and is set once they are written here. With
        'page_experiments' (a dictionary), the slim copy of each file read is put in
        it for the dataset figure, in place of what it held.
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
    page_experiments = context.get('page_experiments')
    if page_experiments is not None:
        page_experiments.clear()
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
                                                        page_experiments,
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
                         ) -> None:
    """
    ---- Summary ----
    Main function to read, process, plot and export one .paf file. Each step reports its
    own problem so the next step still runs: a figure that could not be saved does not
    stop the workbook, and a workbook that could not be saved does not stop the run.

    ---- Inputs ----
    info : dict
        Per-file information from everything_asker: path, name, trim and ignore times,
        OD values, events, is_plot_saved and is_workbook_saved
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
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the figure and the workbook files, prints progress and adds to
    ``unsaved`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_plotter
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
    vo2_source = processed['vo2_source']
    plotted_haem_source = processed['plotted_haem_source']

    # ---- 3 Plot the experiment -------------------------------------------------------
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

    # ---- 4 Export the workbook -------------------------------------------------------
    # A workbook saved once the figure was accepted is not written again. One that
    # cannot be written (open in Excel, a full disk) does not stop the run: its name
    # is noted, and the dataset figure still uses the file.
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
    folder, ask the other questions, process every file, then save the dataset
    figure. The log keeps each answer from the results folder on, also when
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
    exported: List[Path] = []  # the trim step's export adds the results folder
    saved_plots: List[str] = []  # the files whose plot is saved before the run
    saved_workbooks: List[str] = []  # the files whose workbook is written before it
    page_data: dict = {}  # the set-up and the slim experiments of the dataset figure
    try:
        try:
            (answers,
             experiments,
             fit,
             page,
             ) = everything_asker(folder,
                                  summaries,
                                  export_root,
                                  saved,
                                  exported,
                                  saved_plots,
                                  saved_workbooks,
                                  page_data,
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
                experiment_processor(info, cfg, fit, export_root, unsaved)
            except Exception as exc:
                problem_shower(f"  {info['name']} was not finished", exc)
                failed.append(info['name'])
            finally:
                plt.close('all')
                gc.collect()
        dataset_figure_saver(page,
                             export_root,
                             page_data.get('setup'),
                             page_data.get('experiments'),
                             answers,
                             )
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


if __name__ == '__main__':
    sys.exit(main())
