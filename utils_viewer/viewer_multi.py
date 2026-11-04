"""
Previews of the multi-experiment figures while their questions are answered.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.custom_runner import experiment_preparer
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.helpers import figure_capture_setter
from utils_shared.questions import choice_asker, info_printer
from utils_viewer.viewer_gui import active_gui_getter
from utils_viewer.viewer_preview import PREVIEW_DPI, preview_info_builder
from utils_viewer.viewer_stages import PREVIEW_FILE
from utils_viewer.viewer_window import PictureWindow


# ---- CONSTANTS -----------------------------------------------------------------------
SUMMARY_KINDS = ('time_response', 'haem_ocr')
WARNING_WORDS = ('Not made', 'not made', 'skipped', 'Warning')


# ---- MULTI-FIGURE HELPERS ------------------------------------------------------------


# ---- _kept_builder -------------------------------------------------------------------
def _kept_builder(names: List[str],
                  customs: Dict[str, dict],
                  answers: dict,
                  fit: Optional[dict],
                  context: dict,
                  ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to read and process the files a multi-experiment figure needs, the
    way the real run does (without plotting or exporting them).

    ---- Inputs ----
    names : List[str]
        Names of the files the figure uses.
    customs : Dict[str, dict]
        {file name: {'time_response_group', 'haem_ocr'}} for the summary figures.
    answers : dict
        Answers so far, ready to build the figure style from.
    fit : Optional[dict]
        Fit dictionary, or None.
    context : dict
        {summaries, limits, details, export_root} of the run so far. The processed
        files are kept in it (key '_processed') while one figure is being built.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {experiment, vo2_source, haem_source, prepared}}, as the run keeps
        them for the special figures.

    ---- Globals mutated ----
    None. Reads the files and prints what the processing says (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    preview_info_builder
    experiment_data_processor
    experiment_preparer
    """

    cfg = settings.Config(answers)
    by_name = {s['name']: s for s in context['summaries']}
    kept = {}
    for name in names:
        info = preview_info_builder(by_name[name],
                                    context['limits'],
                                    context['details'],
                                    )
        info['custom'] = customs.get(name, {'time_response_group': None,
                                            'haem_ocr': False,
                                            },
                              )
        key = (name, repr(info['custom']), id(fit))
        processed = context.setdefault('_processed', {}).get(key)
        if processed is None:  # reading and decomposing is slow, so it is kept
            processed = experiment_data_processor(info, cfg, fit)
            context['_processed'][key] = processed
        experiment = processed['experiment']
        haem_panels = answers['plot_haems'] and 'haem_conc' in experiment
        kept[name] = {'experiment': experiment,
                      'vo2_source': processed['vo2_source'],
                      'haem_source': processed['haem_source'] if haem_panels else None,
                      'prepared': experiment_preparer(experiment,
                                                      info['custom'],
                                                      answers,
                                                      fit,
                                                      processed['od_available'],
                                                      ),
                      }
    return kept


# ---- _pictures_builder ---------------------------------------------------------------
def _pictures_builder(kind: str,
                      payload: dict,
                      context: dict,
                      makers: Dict[str, Callable],
                      window: Any,
                      ) -> Tuple[List[Tuple[str, bytes]], str]:
    """
    ---- Summary ----
    Helper function to make one multi-experiment figure the way the run will, but hand
    the finished figure over as a picture instead of saving files.

    ---- Inputs ----
    kind : str
        'comparison', 'exemplar', 'time_response' or 'haem_ocr'.
    payload : dict
        What the questions decided: {'comparison': ...}, {'exemplar_names': ...} or
        {'fit': ..., 'custom': {...}} (see the figure_checker of the askers).
    context : dict
        {answers, fit, summaries, limits, details, export_root} of the run so far.
    makers : Dict[str, Callable]
        {'comparison': comparison_maker, 'special': special_figures_maker} of main.py.
    window : Any
        The browser window (or the picture fallback), which captures the printed text.

    ---- Globals read ----
    PREVIEW_DPI, WARNING_WORDS (module constants).

    ---- Outputs ----
    Tuple[List[Tuple[str, bytes]], str]
        ([(title, PNG bytes)], notes). The notes are the lines saying why a figure was
        not made, and may be empty.

    ---- Globals mutated ----
    None. Reads the files, switches figure saving to preview mode while it runs and
    puts it back (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _kept_builder
    figure_capture_setter
    """

    # ---- 1 Decide the files and the settings -----------------------------------------
    answers = dict(context['answers'], export_spectra=False)
    fit = payload.get('fit', context['fit'])
    customs: Dict[str, dict] = {}
    exemplar_names = payload.get('exemplar_names')
    comparison = payload.get('comparison')
    if kind == 'comparison':
        names = list(comparison['runs'])
    elif kind == 'exemplar':
        names = list(exemplar_names)
    else:
        groups = payload['custom'].get('time_response') or {}
        members = payload['custom'].get('haem_ocr') or []
        names = list(groups) if kind == 'time_response' else list(members)
        customs = {name: {'time_response_group': groups.get(name),
                          'haem_ocr': name in members,
                          }
                   for name in names
                   }
    answers.update({'plot_time_response': kind == 'time_response',
                    'plot_haem_ocr': kind == 'haem_ocr',
                    'plot_exemplar': kind == 'exemplar',
                    })

    # ---- 2 Make the figure, keeping the picture instead of the files -----------------
    pictures: List[Tuple[str, bytes]] = []
    def capture(figure: Any, stem: str) -> None:
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', dpi=PREVIEW_DPI)
        pictures.append((stem.replace('_', ' '), buffer.getvalue()))
    cfg = settings.Config(answers)
    plt.rcParams.update(cfg.RC_PARAMS)
    with window.output_capturer() as printed:
        try:
            figure_capture_setter(capture)
            kept = _kept_builder(names, customs, answers, fit, context)
            if kind == 'comparison':
                makers['comparison'](comparison, kept, cfg, context['export_root'])
            else:
                makers['special'](kept,
                                  cfg,
                                  fit,
                                  context['export_root'],
                                  exemplar_names,
                                  True,
                                  )
        except Exception as exc:  # a preview problem must never stop the questions
            print(f'Not made: {type(exc).__name__}: {exc}')
        finally:
            figure_capture_setter(None)
            plt.close('all')
    notes = '\n'.join(line.strip()
                      for line in printed.getvalue().splitlines()
                      if any(word in line for word in WARNING_WORDS)
                      )
    return pictures, notes


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- multi_figure_checker_builder ----------------------------------------------------
def multi_figure_checker_builder(context: dict,
                                 makers: Dict[str, Callable],
                                 ) -> Callable[[str, dict], bool]:
    """
    ---- Summary ----
    Main function to build the figure checker the multi-experiment questions call after
    each figure: it draws the figure from the data, shows it in the browser window and
    asks whether to accept it.

    ---- Inputs ----
    context : dict
        {answers, fit, summaries, limits, details, export_root} of the run so far. The
        dictionary is read each time, so later changes to it are seen.
    makers : Dict[str, Callable]
        {'comparison': comparison_maker, 'special': special_figures_maker} of main.py.

    ---- Globals read ----
    PREVIEW_FILE (imported constant).

    ---- Outputs ----
    Callable[[str, dict], bool]
        Function (kind, payload) that returns True when the figure is accepted, or when
        it could not be previewed (the questions then carry on). A payload with
        'question' and 'change' is a step of a figure being built, which is asked with
        that wording; without them it is the finished figure.

    ---- Globals mutated ----
    None. The checker reads the files and prints to the terminal (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _pictures_builder
    active_gui_getter
    choice_asker
    info_printer
    """

    def checker(kind: str, payload: dict) -> bool:
        window = active_gui_getter() or PictureWindow(PREVIEW_FILE)
        info_printer('Drawing the figure from the data (this can take a moment) ...',
                     depth=2,
                     )
        question_asked = payload.get('question')
        pictures, notes = _pictures_builder(kind, payload, context, makers, window)
        if notes:
            info_printer(notes, depth=2)
        if not pictures:
            info_printer('This figure could not be previewed, so it is kept as it is.',
                         depth=2,
                         )
            if question_asked is None:
                context.pop('_processed', None)
            return True
        window.pictures_publisher(pictures)
        question = payload.get('question')
        choice = choice_asker(question or 'Do you accept this figure?',
                              [('yes', 'Yes, accept'),
                               ('no', payload.get('change', 'No, change its settings')),
                               ],
                              'yes',
                              depth=2 if question else 1,
                              )
        if question is None:  # the finished figure: the processed files are not needed
            context.pop('_processed', None)
        return choice == 'yes'
    return checker
