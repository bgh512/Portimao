"""
Numbered terminal questions of the time response and the OCR and haem response.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Callable, List, Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import group_assigner, hours_parser, run_name_lister
from utils_shared.questions import (choice_asker,
                                    info_printer,
                                    multi_asker,
                                    text_asker,
                                    yes_no_asker,
                                    )
from utils_shared.survey import (averaging_asker,
                                 decomposition_asker,
                                 haem_form_option_builder,
                                 haem_name_formatter,
                                 haem_name_sorter,
                                 ocr_option_builder,
                                 size_asker,
                                 )


# ---- CUSTOM QUESTIONS HELPERS --------------------------------------------------------


# ---- _example_pair_maker -------------------------------------------------------------
def _example_pair_maker(members: dict, name: str) -> list:
    """
    ---- Summary ----
    Helper function to describe an experiment as the (group, hours) pair that is saved
    with the answers.

    ---- Inputs ----
    members : dict
        {experiment name: group}.
    name : str
        Experiment name with the hours in it, e.g. 'control_7hours'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        [group, hours] of the experiment.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    hours_parser
    """

    return [members[name], hours_parser(name)]


# ---- _haem_ocr_asker -----------------------------------------------------------------
def _haem_ocr_asker(names: List[str],
                    answers: dict,
                    defaults: dict,
                    fit: dict,
                    step_checker: Optional[Callable[[object, str, str], bool]] = None,
                    ) -> Optional[List[str]]:
    """
    ---- Summary ----
    Helper function to ask the settings of the haem and OCR response figure (6.2.x).

    ---- Inputs ----
    names : List[str]
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    fit : dict
        Fit dictionary (haem_list) used to list the haems.
    step_checker : Optional[Callable[[object, str, str], bool]]
        Function (names, question, change label) that draws the figure as built so far,
        asks whether it is accepted and returns True when it is; None skips the
        previews.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[List[str]]
        Names of the experiments that belong to the figure, or None when it cannot be
        made from these files.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _step_checker
    choice_asker
    haem_form_option_builder
    haem_name_formatter
    haem_name_sorter
    info_printer
    multi_asker
    ocr_option_builder
    run_name_lister
    size_asker
    yes_no_asker
    """

    # ---- 1 Show how the file names are read ------------------------------------------
    info_printer('File names need the strain, the addition order and the run number, '
                 'e.g. '
                 "'knockdown_kcn_then_bd_run1'.",
                 depth=2,
                 )
    rows = run_name_lister(names)
    usable = [r
              for r in rows
              if all(r[key] is not None for key in ('strain', 'order', 'run'))
              ]
    left_out = [r['name'] for r in rows if r not in usable]
    if not usable:
        info_printer('None of the file names fit, so the haem and OCR response is '
                     'skipped.',
                     depth=2,
                     )
        return None
    sets = {}
    for row in usable:
        sets.setdefault((row['strain'], row['order']), []).append(row['run'])
    info_printer(f'{len(usable)} file(s) found in {len(sets)} set(s):', depth=2)
    for (strain, order), runs in sets.items():
        runs_text = ', '.join(str(r) for r in sorted(runs))
        info_printer(f'  {len(runs)} replicate(s) of strain: {strain}, additions: '
                     f'{order} '
                     f'(run {runs_text})',
                     depth=2,
                     )
    if left_out:
        left_text = ', '.join(left_out)
        info_printer(f'Left out (name not recognised): {left_text}', depth=2)

    # ---- 2 What is shown, drawn as each choice is made -------------------------------
    names_used = [r['name'] for r in usable]
    ocr_keys = ['raw'] + (['od'] if answers['normalise_od'] else []) + ['percent']
    answers.update({'ho_haem_mode': defaults['ho_haem_mode'],
                    'ho_per_od': False,
                    'ho_metric': 'delta',
                    'ho_haems': [],
                    'ho_blocks': ('baseline', 'ocr_response'),
                    })
    ocr_default = (defaults['ho_ocr_mode']
                   if defaults['ho_ocr_mode'] in ocr_keys
                   else ocr_keys[0]
                   )
    while True:
        answers['ho_ocr_mode'] = choice_asker('Which OCR would you like to use?',
                                              ocr_option_builder(ocr_keys),
                                              ocr_default,
                                              depth=2,
                                              )
        if _step_checker(step_checker,
                         names_used,
                         'Do you accept the OCR plots?',
                         'No, choose the OCR again',
                         ):
            break
        ocr_default = answers['ho_ocr_mode']
    # All the haems are drawn as soon as the way to show them is chosen.
    answers['ho_blocks'] = ('baseline', 'ocr_response', 'haem_response')
    mode_default = defaults['ho_haem_mode']
    while True:
        answers['ho_haem_mode'] = choice_asker('How would you like to show the haems?',
                                               haem_form_option_builder(True),
                                               mode_default,
                                               depth=2,
                                               )
        answers['ho_per_od'] = False
        if answers['normalise_od'] and answers['ho_haem_mode'] != 'percent':
            answers['ho_per_od'] = yes_no_asker('Do you want to scale the haems by OD '
                                                'as well?',
                                                defaults['ho_per_od'],
                                                depth=2,
                                                )
        if _step_checker(step_checker,
                         names_used,
                         'Do you accept these haem plots?',
                         'No, choose how to show the haems again',
                         ):
            break
        mode_default = answers['ho_haem_mode']
    haems_default = defaults['ho_haems'] or list(fit['haem_list'])
    while True:
        answers['ho_haems'] = multi_asker('Which haems should get a row, and in which '
                                          'order?',
                                          haem_name_sorter(fit['haem_list']),
                                          default_all=True,
                                          keep_order=True,
                                          depth=2,
                                          default_values=haems_default,
                                          label_formatter=haem_name_formatter,
                                          )
        if _step_checker(step_checker,
                         names_used,
                         'Do you accept these haem rows?',
                         'No, choose the haems again',
                         ):
            break
        haems_default = answers['ho_haems']
    answers.pop('ho_blocks', None)

    # ---- 3 Figure size ---------------------------------------------------------------
    size_asker(answers,
               defaults,
               {'journal': 'ho_journal',
                'columns': 'ho_pub_columns',
                'height': 'ho_pub_height',
                'mode': 'ho_size_mode',
                },
               (2, 0.75),
               depth=2,
               )
    return names_used


# ---- _hours_reader -------------------------------------------------------------------
def _hours_reader(text: str) -> List[float]:
    """
    ---- Summary ----
    Helper function to read the hours typed for the time points to skip.

    ---- Inputs ----
    text : str
        Numbers separated by commas or semicolons, or "none".

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[float]
        The hours. Words that are not numbers are reported and left out.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    """

    hours: List[float] = []
    for word in (text or '').replace(';', ',').split(','):
        try:
            hours.append(float(word))
        except ValueError:
            if word.strip() and word.strip().lower() != 'none':
                info_printer(f'{word.strip()!r} is not a number, so it is ignored.',
                             depth=2,
                             )
    return hours


# ---- _panel_chooser ------------------------------------------------------------------
def _panel_chooser(question: str,
                   options: list,
                   default: str,
                   slot: tuple,
                   step_checker: Optional[Callable[[object, str, str], bool]],
                   ) -> str:
    """
    ---- Summary ----
    Helper function to ask which experiment a panel of the time response shows, put it
    in the figure and ask whether the figure so far is accepted.

    ---- Inputs ----
    question : str
        The question.
    options : list
        [(experiment name, text)] to choose from.
    default : str
        Experiment offered when only Enter is pressed.
    slot : tuple
        (list the pair is stored in, position in that list, {experiment name: group}).
    step_checker : Optional[Callable[[object, str, str], bool]]
        Function that draws the figure so far and asks whether it is accepted; None
        accepts without drawing.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Name of the experiment chosen.

    ---- Globals mutated ----
    None. Stores the (group, hours) pair in the list of ``slot`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _example_pair_maker
    _step_checker
    choice_asker
    """

    values, position, members = slot
    while True:
        choice = choice_asker(question, options, default, depth=2)
        values[position] = _example_pair_maker(members, choice)
        if _step_checker(step_checker,
                         members,
                         'Do you accept this plot?',
                         'No, choose another experiment',
                         ):
            return choice
        default = choice


# ---- _saved_example_finder -----------------------------------------------------------
def _saved_example_finder(defaults: dict,
                          key: str,
                          members: dict,
                          timed: list,
                          ) -> list:
    """
    ---- Summary ----
    Helper function to find the experiments that match the (group, hours) pairs
    remembered from the last run.

    ---- Inputs ----
    defaults : dict
        Saved answers of the last run.
    key : str
        Answer holding the pairs, e.g. 'tr_examples'.
    members : dict
        {experiment name: group}.
    timed : list
        Names of the experiments that have hours in their name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Names of the experiments that match a saved pair, in the order of the pairs.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    hours_parser
    """

    return [name
            for group, hours in (defaults.get(key) or [])
            for name in timed
            if members[name] == group and hours_parser(name) == hours
            ]


# ---- _step_checker -------------------------------------------------------------------
def _step_checker(step_checker: Optional[Callable[[object, str, str], bool]],
                  members: object,
                  question: str,
                  change: str,
                  ) -> bool:
    """
    ---- Summary ----
    Helper function to show the figure as built so far and ask whether it is accepted.

    ---- Inputs ----
    step_checker : Optional[Callable[[object, str, str], bool]]
        Function (members, question, change label) that draws the figure and returns
        True when it is accepted; None when there is nothing to draw with.
    members : object
        The experiments of the figure: {name: group} or a list of names.
    question : str
        The accept question.
    change : str
        Label of the answer that asks the question again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when accepted (or when there is no way to draw).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return True if step_checker is None else step_checker(members, question, change)


# ---- _step_wirer ---------------------------------------------------------------------
def _step_wirer(figure_checker: Optional[Callable[[str, dict], bool]],
                key: str,
                fit: Optional[dict],
                result: dict,
                ) -> Optional[Callable[[object, str, str], bool]]:
    """
    ---- Summary ----
    Helper function to turn the figure checker of the whole figure into the checker of
    one step: the figure drawn from the choices made so far.

    ---- Inputs ----
    figure_checker : Optional[Callable[[str, dict], bool]]
        The figure checker (see summary_figure_asker), or None.
    key : str
        'time_response' or 'haem_ocr'.
    fit : Optional[dict]
        Fit dictionary.
    result : dict
        {'time_response': ..., 'haem_ocr': ...} of the figures so far.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Callable[[object, str, str], bool]]
        Function (members, question, change label) giving True when the user accepts
        the figure so far, or None when there is no figure checker.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if figure_checker is None:
        return None
    def check(members: object, question: str, change: str) -> bool:
        payload = {'fit': fit,
                   'custom': dict(result, **{key: members}),
                   'question': question,
                   'change': change,
                   }
        return figure_checker(key, payload)
    return check


# ---- _time_response_asker ------------------------------------------------------------
def _time_response_asker(names: List[str],
                         answers: dict,
                         defaults: dict,
                         step_checker: Optional[Callable[[object, str, str], bool]]
                         = None,
                         ) -> Optional[dict]:
    """
    ---- Summary ----
    Helper function to ask the settings of the time response figure (6.1.x).

    ---- Inputs ----
    names : List[str]
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    step_checker : Optional[Callable[[object, str, str], bool]]
        Function (members, question, change label) that draws the figure as built so
        far, asks whether it is accepted and returns True when it is; None skips the
        previews.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[dict]
        {experiment name: group} of the experiments that belong to the figure, or
        None when the figure cannot be made from these files.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _hours_reader
    _panel_chooser
    _saved_example_finder
    _step_checker
    group_assigner
    hours_parser
    info_printer
    size_asker
    text_asker
    """

    # ---- 1 Find the experiments of each group ----------------------------------------
    info_printer("File names need a group word and the hours, e.g. 'control_7hours'.",
                 depth=2,
                 )
    text = text_asker('What are the two group words, separated by a comma?',
                      ','.join(defaults['tr_groups']),
                      depth=2,
                      )
    groups = [word.strip().lower() for word in text.split(',') if word.strip()]
    if len(groups) != 2:
        info_printer('Two group words are needed, so the time response is skipped.',
                     depth=2,
                     )
        return None
    found = group_assigner({name: {} for name in names}, groups)
    members = {name: experiment['group'] for name, experiment in found.items()}
    for group in groups:
        listed = [n for n, g in members.items() if g == group]
        listed_text = ', '.join(listed) if listed else 'no files found'
        info_printer(f'{group}: {listed_text}', depth=2)
    if any(group not in members.values() for group in groups):
        info_printer('Both groups need at least one file, so the time response is '
                     'skipped.',
                     depth=2,
                     )
        return None
    answers['tr_groups'] = groups

    # ---- 2 The time points left out of the waterfalls --------------------------------
    timed = [n for n in members if hours_parser(n) is not None]
    options = [(n, f'{n} ({members[n]}, {hours_parser(n):g} hours)') for n in timed]
    if len(options) < 2:
        info_printer('Two experiments with hours in their name are needed for the '
                     'examples, '
                     'so the time response is skipped.',
                     depth=2,
                     )
        return None
    # Nothing but the waterfalls is chosen yet; the other panels are empty boxes.
    answers['tr_examples'] = [None, None]
    answers['tr_decompositions'] = [None, None, None]
    answers['tr_skip_hours'] = []
    skip_default = ', '.join(f'{h:g}' for h in defaults.get('tr_skip_hours') or [])
    while True:
        skipped = text_asker('Which time points (hours) should be skipped in the '
                             'waterfall plots? Separate them with commas, or type '
                             'none.',
                             skip_default or 'none',
                             depth=2,
                             )
        answers['tr_skip_hours'] = _hours_reader(skipped)
        if _step_checker(step_checker,
                         members,
                         'Do you accept these waterfall plots?',
                         'No, choose the time points again',
                         ):
            break
        skip_default = ', '.join(f'{h:g}' for h in answers['tr_skip_hours']) or 'none'

    # ---- 3 The two kinetic traces and the three decomposition plots ------------------
    first_group = [n for n in timed if members[n] == groups[0]]
    saved = _saved_example_finder(defaults, 'tr_examples', members, timed)[:2]
    top_default = saved[0] if saved else first_group[0]
    left = _panel_chooser('Which experiment should the first kinetic trace show?',
                          options,
                          top_default,
                          (answers['tr_examples'], 0, members),
                          step_checker,
                          )
    if len(saved) > 1:
        bottom_default = saved[1]
    elif first_group[-1] != left:
        bottom_default = first_group[-1]
    else:
        bottom_default = options[-1][0]
    right = _panel_chooser('Which experiment should the second kinetic trace show?',
                           options,
                           bottom_default,
                           (answers['tr_examples'], 1, members),
                           step_checker,
                           )
    saved = _saved_example_finder(defaults,
                                  'tr_decompositions',
                                  members,
                                  timed,
                                  )[:3]
    unused = [n for n, _ in options if n not in (left, right)]
    for number in range(3):
        if number < len(saved):
            default = saved[number]
        elif number == 0:
            default = left
        elif number == 1:
            default = right
        else:
            default = (unused or [options[-1][0]])[0]
        _panel_chooser(f'Which experiment should decomposition plot {number + 1} '
                       f'show?',
                       options,
                       default,
                       (answers['tr_decompositions'], number, members),
                       step_checker,
                       )

    # ---- 3 Figure size ---------------------------------------------------------------
    size_asker(answers,
               defaults,
               {'journal': 'ho_journal',
                'columns': 'ho_pub_columns',
                'height': 'ho_pub_height',
                'mode': 'ho_size_mode',
                },
               (2, 0.75),
               depth=2,
               )
    return members


# ---- _window_ensurer -----------------------------------------------------------------
def _window_ensurer(answers: dict, defaults: dict) -> None:
    """
    ---- Summary ----
    Helper function to make sure the event-window settings exist for the special
    figures: they reuse the section 3 settings, which are asked here if event
    averaging was switched off there.

    ---- Inputs ----
    answers : dict
        Answers dictionary; uses averaging, window_minutes and gap_minutes.
    defaults : dict
        Default answers.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the tr_* and ho_* window answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    averaging_asker
    info_printer
    """

    if not answers['averaging'] and not answers.get('window_asked'):
        info_printer('This figure averages around the events, like section 3.3.',
                     depth=2,
                     )
        averaging_asker(answers, defaults, forced=True, depth=2)
    for prefix in ('tr', 'ho'):
        answers[f'{prefix}_window_minutes'] = answers['window_minutes']
        answers[f'{prefix}_gap_minutes'] = answers['gap_minutes']
        answers[f'{prefix}_final_gap_minutes'] = answers['final_gap_minutes']


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- summary_figure_asker ------------------------------------------------------------
def summary_figure_asker(names: List[str],
                         answers: dict,
                         defaults: dict,
                         summaries: List[dict],
                         fit: Optional[dict],
                         fits_folder: Path,
                         figure_checker: Optional[Callable[[str, dict], bool]] = None,
                         ) -> tuple:
    """
    ---- Summary ----
    Main function to ask section 6: whether to plot a time response and a haem and
    OCR response, and the settings of each one chosen. Both need the haem fit, which
    is asked for here if it was not chosen in section 3.

    ---- Inputs ----
    names : List[str]
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    summaries : List[dict]
        File summaries (DATA_FORMAT.md), used if the fit has to be asked for.
    fit : Optional[dict]
        Fit dictionary chosen in section 3, or None.
    fits_folder : Path
        Folder holding the fit .csv files.
    figure_checker : Optional[Callable[[str, dict], bool]]
        Function called after the questions of each figure with (key, {'fit': fit,
        'custom': result so far}); it shows the figure and returns True when the user
        accepts it. When it returns False the figure's questions are asked again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fit, result). result is {'time_response': {name: group} or None,
        'haem_ocr': [names] or None}; None means that figure will not be made.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_ocr_asker
    _step_wirer
    _time_response_asker
    _window_ensurer
    decomposition_asker
    info_printer
    yes_no_asker
    """

    result = {'time_response': None, 'haem_ocr': None}
    answers['plot_time_response'] = False
    answers['plot_haem_ocr'] = False
    for key, question, asker in (('time_response',
                                  'Do you want to plot a time response?',
                                  None,
                                  ),
                                 ('haem_ocr',
                                  'Do you want to plot a haem and OCR response?',
                                  None,
                                  ),
                                 ):
        while True:
            result[key] = None
            answers[f'plot_{key}'] = False
            if not yes_no_asker(question, defaults[f'plot_{key}']):
                break

            # ---- 1 Make sure the haems are decomposed --------------------------------
            if fit is None:
                info_printer('This figure needs the haems, so they are decomposed.',
                             depth=2,
                             )
                (answers['decompose'],
                 answers['fit_file'],
                 fit,
                 answers['decomposition_dataset'],
                 ) = decomposition_asker(summaries,
                                         defaults,
                                         fits_folder,
                                         forced=True,
                                         depth=2,
                                         )
                if fit is None:
                    info_printer('No haem fit is available, so this figure is skipped.',
                                 depth=2,
                                 )
                    break

            # ---- 2 Ask the settings of the figure ------------------------------------
            _window_ensurer(answers, defaults)
            checker = _step_wirer(figure_checker, key, fit, result)
            if key == 'time_response':
                result[key] = _time_response_asker(names, answers, defaults, checker)
            else:
                result[key] = _haem_ocr_asker(names, answers, defaults, fit, checker)
            answers[f'plot_{key}'] = result[key] is not None
            if (result[key] is None or figure_checker is None or
                    figure_checker(key, {'fit': fit, 'custom': result})
                    ):
                break
            defaults = dict(answers)
    return fit, result
