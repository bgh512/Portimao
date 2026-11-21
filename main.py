"""
Main program: read .paf files, process them and export figures and workbooks.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import gc
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')  # figures are saved to files; no window is needed
import matplotlib.pyplot as plt

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.custom_questions import summary_figure_asker
from utils_custom.custom_runner import (exemplar_runner,
                                        experiment_preparer,
                                        ocr_and_haem_response_runner,
                                        time_response_runner,
                                        )
from utils_shared.app_messages import SEND_DETAILS, start_problem_shower
from utils_shared.comparison_plotter import comparison_figure_plotter
from utils_shared.dataset_settings import dataset_settings_saver
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.figure_layout import figure_size_calculator
from utils_shared.individual_experiment_exporter import experiment_workbook_exporter
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.questions import section_starter, UserQuitError, yes_no_asker
from utils_shared.helpers import (program_title_builder,
                                  program_version_reader,
                                  update_note_finder,
                                  )
from utils_shared.run_logging import (details_place_setter,
                                      logging_starter,
                                      logging_stopper,
                                      settings_logger,
                                      )
from utils_shared.survey import (files_asker,
                                 haem_name_formatter,
                                 JOURNAL_NAMES,
                                 multi_experiment_asker,
                                 )
from utils_shared.user_notices import problem_shower, warning_shower
from utils_shared.user_places import (app_output_logger,
                                      user_folder_preparer,
                                      user_places_finder,
                                      )
from utils_viewer.viewer_gui import gui_runner, GuiUnavailableError
from utils_viewer.viewer_multi import multi_figure_checker_builder
from utils_viewer.viewer_stages import viewer_asker


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
                                         )
        print(f'  Saved {stem} ({size[0] * 25.4:.0f} x {size[1] * 25.4:.0f}'
              f' mm)',
              )
    except Exception as exc:
        problem_shower('  Not made', exc)
        plt.close('all')


# ---- everything_asker ----------------------------------------------------------------
def everything_asker(folder: Path,
                     summaries: List[dict],
                     export_root: Path,
                     saved: dict,
                     ) -> Tuple[dict,
                                List[dict],
                                Optional[dict],
                                Optional[dict],
                                Optional[List[str]],
                                ]:
    """
    ---- Summary ----
    Main function to ask every question of the run after the files, in numbered
    sections (trimming and ignoring, analysis, plots, summary figures, export), and to
    build the per-file information.

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

    ---- Globals read ----
    PLACES, JOURNAL_NAMES (module constants); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    Tuple[dict, List[dict], Optional[dict], Optional[dict], Optional[List[str]]]
        (answers, per-experiment info dictionaries, fit, side-by-side comparison
        settings or None, names of the 2x2 grid experiments or None). Raises
        UserQuitError if the user declines to start.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal; writes last_answers.json through
    last_answers_saver and the settings file of the dataset through
    dataset_settings_saver (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    comparison_maker
    dataset_settings_saver
    haem_name_formatter
    last_answers_saver
    multi_experiment_asker
    multi_figure_checker_builder
    section_starter
    special_figures_maker
    summary_figure_asker
    viewer_asker
    yes_no_asker
    """

    # ---- 1 Load the settings of the dataset ------------------------------------------
    # A dataset never saved starts from the standard settings (config.py); a dataset
    # saved before starts from the settings kept in its own folder.
    names = [s['name'] for s in summaries]
    defaults = dict(settings.DEFAULT_ANSWERS, **saved.get('answers', {}))
    answers = dict(defaults)
    remembered = saved.get('files', {})

    # ---- 2 Ask the questions ---------------------------------------------------------
    # ---- 2.1 Trimming and ignoring, analysis and individual plots --------------------
    limits, fit, details, plotted = viewer_asker(summaries,
                                                 answers,
                                                 defaults,
                                                 remembered,
                                                 PLACES.fits_folder,
                                                 export_root,
                                                 )

    # ---- 2.2 Multi-experiment plots --------------------------------------------------
    context = {'answers': answers,
               'fit': fit,
               'summaries': summaries,
               'limits': limits,
               'details': details,
               'export_root': export_root,
               }
    checker = multi_figure_checker_builder(context,
                                           {'comparison': comparison_maker,
                                            'special': special_figures_maker,
                                            },
                                           )
    section_starter('Multi-experiment plots')
    comparison, exemplar_names = multi_experiment_asker(summaries,
                                                        answers,
                                                        defaults,
                                                        plotted,
                                                        checker,
                                                        )

    # ---- 2.3 Experiment summaries ----------------------------------------------------
    section_starter('Experiment summaries')
    fit, custom = summary_figure_asker(names,
                                       answers,
                                       defaults,
                                       summaries,
                                       fit,
                                       PLACES.fits_folder,
                                       checker,
                                       )

    # ---- 2.4 Data export -------------------------------------------------------------
    section_starter('Data export')
    print('  Every experiment always gets a workbook with CcO2, CsO2, VoO2, the events'
          ' and your OD/volume/dilution entries.',
          )
    answers['export_full'] = yes_no_asker('Do you want to put every processed table in'
                                          ' the workbook (OD-scaled, haems, percent, '
                                          '...)?',
                                          defaults['export_full'],
                                          )
    answers['export_spectra'] = yes_no_asker('Do you want to export the spectra as csv'
                                             ' files (large, and it takes a while)?',
                                             defaults['export_spectra'],
                                             )

    # ---- 3 Read the experiments ------------------------------------------------------
    experiments = []
    for s in summaries:
        name = s['name']
        info = {'path': s['path'],
                'name': name,
                'duration': s['duration_min'],
                'trim_start': limits[name]['trim_start'],
                'trim_end': limits[name]['trim_end'],
                'ignore_start': limits[name]['ignore_start'],
                'ignore_end': limits[name]['ignore_end'],
                'custom': {'time_response_group': (custom['time_response'] or {}
                                                   ).get(name),
                           'haem_ocr': name in (custom['haem_ocr'] or []),
                           },
                'exemplar': name in (exemplar_names or []),
                }
        info['keep'] = ((bool(comparison) and name in comparison['runs']) or
                        info['exemplar'] or
                        bool(info['custom']['time_response_group']) or
                        info['custom']['haem_ocr']
                        )
        info.update(details[name])
        experiments.append(info)

    # ---- 4 Print the summary ---------------------------------------------------------
    section_starter('Summary')
    print(f'  Files:            {len(experiments)} from {folder}')
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
    print(f'  Decomposition:    '
          f"{answers['fit_file'] if answers['decompose'] else 'no'}",
          )
    print(f"  OD scaling:       {'yes' if answers['normalise_od'] else 'no'}")
    averaging_text = 'no'
    if answers['averaging']:
        averaging_text = ('%g s window, ending %g s before the next addition'
                          % (round(answers['window_minutes'] * 60.0, 2),
                             round(answers['gap_minutes'] * 60.0, 2),
                             )
                          )
    print(f'  Event averaging:  {averaging_text}')
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
    print(f'  Workbooks:        '
          f"{'all processed data' if answers['export_full'] else 'CcO2, CsO2, VoO2'}"
          f"{' + spectra csv' if answers['export_spectra'] else ''}",
          )

    # ---- 5 Confirm the start ---------------------------------------------------------
    if not yes_no_asker('Do you want to start?', True):
        raise UserQuitError()

    # ---- 6 Remember the answers ------------------------------------------------------
    files = dict(remembered)
    files.update({name: dict(v) for name, v in limits.items()})
    last_answers_saver({'data_folder': str(folder.resolve())})
    if not dataset_settings_saver(folder,
                                  export_root,
                                  files,
                                  {k: v
                                   for k, v in answers.items()
                                   if k not in ('haems', 'ho_haems') or v
                                   },
                                  ):
        print(f'  The settings could not be saved in {folder} (the folder cannot be '
              f'written to), so this dataset will start from the standard settings '
              f'next time.',
              )
    return answers, experiments, fit, comparison, exemplar_names


# ---- experiment_processor ------------------------------------------------------------
def experiment_processor(info: dict,
                         cfg: settings.Config,
                         fit: Optional[dict],
                         export_root: Path,
                         ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to read, process, plot and export one .paf file. Each step reports its
    own problem so the next step still runs.

    ---- Inputs ----
    info : dict
        Per-file information from everything_asker: path, name, trim and ignore times,
        OD values, events, custom and keep flags.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    export_root : Path
        Results folder.

    ---- Globals read ----
    plt (matplotlib.pyplot).

    ---- Outputs ----
    Optional[dict]
        {experiment, vo2_source, haem_source, prepared} when the experiment is needed
        again for the comparison or special figures (info["keep"]), otherwise None.

    ---- Globals mutated ----
    None. Writes the figure and the workbook files and prints progress (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_plotter
    experiment_preparer
    experiment_workbook_exporter
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
    metadata = experiment['metadata']
    od_available = processed['od_available']
    vo2_source, haem_source = processed['vo2_source'], processed['haem_source']

    # ---- 6 Plot the experiment -------------------------------------------------------
    # Figure.
    haem_panels = a['plot_haems'] and 'haem_conc' in experiment
    if a['plot_o2'] or a['plot_ocr'] or haem_panels:
        try:
            print('  Plotting ...')
            experiment_plotter(experiment,
                               cfg.plot_config_builder(vo2_source,
                                                       haem_source
                                                       if haem_panels
                                                       else None,
                                                       ignore_first,
                                                       ignore_last,
                                                       ),
                               export_root,
                               )
        except Exception as exc:  # a figure problem must not lose the data export
            problem_shower('  Figure not made', exc)
            plt.close('all')

    # ---- 7 Export the workbook -------------------------------------------------------
    # Workbook.
    metadata.update({'ignore_first_minutes': ignore_first,
                     'ignore_last_minutes': ignore_last,
                     'fit_file': a['fit_file'] if a['decompose'] else None,
                     'processed': datetime.now().strftime('%Y-%m-%d %H:%M'),
                     },
                    )
    print('  Exporting ...')
    experiment_workbook_exporter(experiment,
                                 export_root,
                                 full=a['export_full'],
                                 spectra=a['export_spectra'],
                                 )

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
                'haem_source': haem_source if haem_panels else None,
                'prepared': prepared,
                }
    return None


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
        0 when every file finished, 1 when the run was cancelled or a file failed.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal, sets the matplotlib rcParams, writes
    results and a log file, and replaces sys.stdout and sys.stderr while logging (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    comparison_maker
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
    section_starter('Your files')
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
    kept = {}
    try:
        try:
            (answers,
             experiments,
             fit,
             comparison,
             exemplar_names,
             ) = everything_asker(folder, summaries, export_root, saved)
        except UserQuitError:
            print(
                f"\nCancelled. Nothing was changed; the questions you answered are in "
                f"the log {log_session['log_path'].name} in the logs folder of the "
                f'results folder.',
                )
            return 1

        # ---- 4 Set up the run --------------------------------------------------------
        settings_logger(log_session, answers)
        cfg = settings.Config(answers)
        plt.rcParams.update(cfg.RC_PARAMS)
        start = time.perf_counter()

        # ---- 5 Process every file ----------------------------------------------------
        for warning in cfg.STYLE_WARNINGS:
            warning_shower(f'Figure style warning: {warning}')
        for info in experiments:
            try:
                result = experiment_processor(info, cfg, fit, export_root)
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
        minutes, seconds = divmod(time.perf_counter() - start, 60)
        print(f'\nFinished {len(experiments) - len(failed)} of {len(experiments)} '
              f'file(s) in {int(minutes)} min {seconds:.0f} s.',
              )
        if failed:
            print('Not completed: ' + ', '.join(failed) + ' (the reason for each is '
                  'above)',
                  )
        print(f'Results are in: {export_root}')
    finally:
        logging_stopper(log_session)
    return 1 if failed else 0


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
