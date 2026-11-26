"""
What the page of a dataset figure is given of the dataset: the slim copy of each experiment, the roles a plot keeps in place of file names, the sets of a plot, the fields of a plot's form and the caption lines.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.dataset_setup import (COLOUR_KEY,
                                        LABEL_COLUMNS,
                                        LABEL_KEYS,
                                        labels_lister,
                                        NO_LABELS,
                                        replicates_numberer,
                                        SET_JOINER,
                                        )
from utils_shared.difference_spectra import (difference_decomposer,
                                             difference_spectrum_builder,
                                             haem_bands_finder,
                                             MOD_PER_OD,
                                             )
from utils_shared.figure_page import FigurePage, panel_letters_finder


# ---- CONSTANTS -----------------------------------------------------------------------
# The tables of a processed experiment a plot of the page may draw (DATA_FORMAT.md,
# experiment); the whole spectra ('raw_spectra') are never kept.
TABLE_KEYS = ('CcO2',
              'CsO2',
              'VoO2',
              'VoO2_OD',
              'VoO2_percent',
              'VoO2_baseline',
              'haem_conc',
              'haem_abs',
              'haem_delta_abs',
              'haem_OD',
              'haem_abs_OD',
              'haem_delta_abs_OD',
              'haem_percent',
              'delta_psi',
              )
OTHER_KEYS = ('experiment_name', 'metadata', 'haem_levels', 'averages')
# The role of one experiment: the place of each of its labels among the labels of its
# column (1 for the first, 0 for a blank cell) and its replicate, never its file name,
# so a template fits a dataset whose labels are spelt differently.
EXPERIMENT_ROLE = 'experiment'
ROLE_WORDS = 'Group 1: {}, Group 2: {}, time point: {}, replicate: {}'
ROLE_PATTERN = re.compile(r'Group 1: (\d+), Group 2: (\d+), time point: (\d+), '
                          r'replicate: (\d+)',
                          )
# What a group drop-down of a form is set to, as it is kept in the roles of a plot
SPLIT = 'Split'
TOGETHER = 'All together'
ONLY_WORDS = 'Only label {}'
ONLY_PATTERN = re.compile(r'Only label (\d+)')
SPLIT_WORDS = 'Split: each label on its own'
TICK_ON, TICK_OFF = 'yes', 'no'
# The plot types that show sets of experiments (the group drop-downs) and the ones that
# show one experiment (the experiment picker)
SET_TYPES = ('P3', 'P8', 'P9', 'P10', 'P11', 'P12')
# The plot type whose plots each add a caption line with the times of their two
# regions, and that line
DIFFERENCE_TYPE = 'P2'
DIFFERENCE_WORDS = ('{}: reduced, {:.1f} to {:.1f} min, minus oxidised, {:.1f} to '
                    '{:.1f} min.')
# The plot type whose plots each add a caption line saying what their lines and bands
# are and what they are lined up on, with the two roles that line reads: the band
# (the first of BAND_CHOICES when the roles hold none) and where time 0 is (START_ROLE,
# or ADDITION_WORDS with the number of the addition, the first when the roles hold none)
MEAN_TYPE = 'P8'
BAND_KEY = 'band'
BAND_CHOICES = (('sem', 'SEM'), ('sd', 'SD'), ('none', 'None'))
ZERO_KEY = 'time_zero'
START_ROLE = 'start'
ADDITION_WORDS = 'addition {}'
ADDITION_PATTERN = re.compile(r'addition (\d+)')
MEAN_WORDS = '{}: each line is the mean of its experiments{}; lined up on {}.'
MEAN_BAND_WORDS = ', the band ± {}'
START_WORDS = 'the start of each recording'
# The fields of each plot type's form, {plot type: (setup, roles, answers) -> fields},
# answers being the answers of the run (config.DEFAULT_ANSWERS); a plot type that is
# not here asks nothing. Each plot type adds its own (utils_shared/page_plots.py).
FORM_MAKERS: Dict[str, Callable[[dict, Dict[str, str], dict], List[dict]]] = {}
# What a plot of each type adds to the caption lines after its letter, {plot type:
# (plot, setup, experiments, answers) -> the sentences, or None for nothing}; a plot
# type that is not here adds nothing this way. Each plot type adds its own
# (utils_shared/page_plots.py).
CAPTION_WRITERS: Dict[str, Callable[..., Optional[str]]] = {}
# Group 2 is told apart by the line style and the time point by the shade: the first
# time point in the colour itself, the last with LIGHTEST_SHADE of white mixed in
LINE_STYLES = ('-', '--', ':', '-.')
LINE_STYLE_WORDS = {'-': 'solid line',
                    '--': 'dashed line',
                    ':': 'dotted line',
                    '-.': 'dash-dot line',
                    }
LIGHTEST_SHADE = 0.7
NO_GROUP_COLOUR = '#000000'  # a set that is not one Group 1 label
ALL_EXPERIMENTS = 'All experiments'  # the name of the set when nothing is split
# The plain name of a colour, for the caption: the nearest of these
COLOUR_WORDS = {'black': '#000000',
                'grey': '#7f7f7f',
                'light grey': '#c8c8c8',
                'blue': '#0072b2',
                'light blue': '#56b4e9',
                'dark blue': '#00008b',
                'green': '#009e73',
                'light green': '#90ee90',
                'orange': '#e69f00',
                'red-orange': '#d55e00',
                'red': '#d62728',
                'pink': '#cc79a7',
                'purple': '#7b3fa0',
                'yellow': '#f0e442',
                'brown': '#8c564b',
                'cyan': '#17becf',
                }


# ---- SET-UP HELPERS ------------------------------------------------------------------


# ---- _column_namer -------------------------------------------------------------------
def _column_namer(setup: dict, key: str) -> str:
    """
    ---- Summary ----
    Helper function to name a label column of the set-up: the name the user gave a
    group column, or "Group 1", "Group 2" or "Time point".

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    key : str
        The column, one of LABEL_KEYS.

    ---- Globals read ----
    LABEL_COLUMNS, LABEL_KEYS (imported).

    ---- Outputs ----
    str
        The name.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    place = LABEL_KEYS.index(key)
    names = setup.get('group_names') or []
    given = names[place] if place < len(names) else ''
    return given or dict(LABEL_COLUMNS)[key]


# ---- _label_placer -------------------------------------------------------------------
def _label_placer(labels: Sequence[str], label: str) -> int:
    """
    ---- Summary ----
    Helper function to give the place of a label among the labels of its column.

    ---- Inputs ----
    labels : Sequence[str]
        The labels of the column, in the order first seen.
    label : str
        The label; '' for a blank cell.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        1 for the first label, 2 for the second...; 0 for a blank cell.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return labels.index(label) + 1 if label else 0


# ---- _rgb_reader ---------------------------------------------------------------------
def _rgb_reader(colour: str) -> Tuple[int, int, int]:
    """
    ---- Summary ----
    Helper function to read a colour written as '#rrggbb'.

    ---- Inputs ----
    colour : str
        The colour.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[int, int, int]
        (red, green, blue), each 0 to 255.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return (int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16))


# ---- _rows_lister --------------------------------------------------------------------
def _rows_lister(setup: Optional[dict]) -> List[dict]:
    """
    ---- Summary ----
    Helper function to list the rows of the set-up that are in use, each with its
    replicate number.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[dict]
        The rows in use, in the order of the table, each with 'replicate' (int).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    replicates_numberer
    """

    rows = (setup or {}).get('rows') or []
    return [dict(row, replicate=number)
            for row, number in zip(rows, replicates_numberer(rows))
            if row['use']
            ]


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- caption_lines_builder -----------------------------------------------------------
def caption_lines_builder(page: FigurePage,
                          setup: Optional[dict],
                          experiments: Optional[Dict[str, dict]] = None,
                          answers: Optional[dict] = None,
                          ) -> List[str]:
    """
    ---- Summary ----
    Main function to write, for the caption of the figure, what each colour, line
    style and shade on the page means: one line for the colours of the Group 1 labels,
    one for the line styles of the Group 2 labels and one for the shades of the time
    points, each only when a plot of the page uses it. Each Difference spectrum (P2)
    then adds a line with its letter and the times of its two regions, each Mean
    trace (P8) a line with its letter, what its lines and bands are and what it is
    lined up on, and each plot whose type has a caption writer (the plots per
    region) a line with its letter and the sentences of that writer.

    ---- Inputs ----
    page : FigurePage
        The page.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Optional[Dict[str, dict]]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md), for the
        regions of the difference spectra and the numbers of the plots per region;
        None for none.
    answers : Optional[dict]
        The answers of the run, for the plots per region; None for none.

    ---- Globals read ----
    ADDITION_PATTERN, ADDITION_WORDS, BAND_CHOICES, BAND_KEY, CAPTION_WRITERS,
    DIFFERENCE_TYPE, DIFFERENCE_WORDS, EXPERIMENT_ROLE, LINE_STYLE_WORDS,
    MEAN_BAND_WORDS, MEAN_TYPE, MEAN_WORDS, SET_TYPES, START_ROLE, START_WORDS,
    ZERO_KEY.

    ---- Outputs ----
    List[str]
        The lines, such as 'Colours (strain): control, blue; knockdown, red-orange.',
        'b: reduced, 12.0 to 14.0 min, minus oxidised, 2.0 to 4.0 min.', 'c: each
        line is the mean of its experiments, the band ± SEM; lined up on addition
        1.' and 'd: Each dot is one experiment, and the bars are the mean ± SEM of
        each set (control n = 3).'; empty when no plot of the page shows sets of
        experiments, a difference spectrum or a mean trace.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _column_namer
    colour_namer
    panel_letters_finder
    plot_sets_lister
    role_experiment_finder
    """

    # ---- 1 What the plots of the page use --------------------------------------------
    colours: Dict[str, str] = {}
    styles: Dict[str, str] = {}
    shades: Dict[str, float] = {}
    for plot in page.plots:
        if plot.plot_type not in SET_TYPES:
            continue
        for entry in plot_sets_lister(setup, plot.roles):
            labels = entry['labels']
            if labels.get('group_1'):
                colours.setdefault(labels['group_1'], entry['base_colour'])
            if labels.get('group_2'):
                styles.setdefault(labels['group_2'], entry['line_style'])
            if labels.get('time_point'):
                shades.setdefault(labels['time_point'], entry['shade'])

    # ---- 2 One line for each ---------------------------------------------------------
    lines = []
    if colours:
        parts = '; '.join(f'{label}, {colour_namer(colour)}'
                          for label, colour in colours.items()
                          )
        lines.append(f"Colours ({_column_namer(setup, 'group_1')}): {parts}.")
    if styles:
        parts = '; '.join(f'{label}, {LINE_STYLE_WORDS[style]}'
                          for label, style in styles.items()
                          )
        lines.append(f"Line styles ({_column_namer(setup, 'group_2')}): {parts}.")
    if len(shades) > 1:
        ordered = sorted(shades, key=lambda label: shades[label])
        lines.append(f"Shades ({_column_namer(setup, 'time_point')}), from dark to "
                     f"light: {', '.join(ordered)}.",
                     )

    # ---- 3 The regions of each difference spectrum -----------------------------------
    letters = panel_letters_finder(page)
    for index, plot in enumerate(page.plots):
        if plot.plot_type != DIFFERENCE_TYPE:
            continue
        name = role_experiment_finder(setup, plot.roles.get(EXPERIMENT_ROLE, ''))
        difference = ((experiments or {}).get(name) or {}).get('difference')
        if difference:
            lines.append(DIFFERENCE_WORDS.format(letters[index],
                                                 *difference['reduced_region'],
                                                 *difference['oxidised_region'],
                                                 ),
                         )

    # ---- 4 The lines and bands of each mean trace ------------------------------------
    bands = dict(BAND_CHOICES)
    for index, plot in enumerate(page.plots):
        if plot.plot_type != MEAN_TYPE:
            continue
        band = plot.roles.get(BAND_KEY)
        band = band if band in bands else BAND_CHOICES[0][0]
        zero = plot.roles.get(ZERO_KEY, '')
        if zero != START_ROLE and not ADDITION_PATTERN.fullmatch(zero):
            zero = ADDITION_WORDS.format(1)
        lines.append(MEAN_WORDS.format(letters[index],
                                       ('' if band == BAND_CHOICES[-1][0]
                                        else MEAN_BAND_WORDS.format(bands[band])
                                        ),
                                       START_WORDS if zero == START_ROLE else zero,
                                       ),
                     )

    # ---- 5 What each plot with a caption writer says of itself -----------------------
    for index, plot in enumerate(page.plots):
        writer = CAPTION_WRITERS.get(plot.plot_type)
        if writer is None:
            continue
        sentences = writer(plot, setup, experiments or {}, answers or {})
        if sentences:
            lines.append(f'{letters[index]}: {sentences}')
    return lines


# ---- choice_field_maker --------------------------------------------------------------
def choice_field_maker(key: str,
                       label: str,
                       choices: Sequence[Tuple[str, str]],
                       roles: Dict[str, str],
                       start: str,
                       ) -> dict:
    """
    ---- Summary ----
    Main function to make a drop-down of a form from a fixed list of choices.

    ---- Inputs ----
    key : str
        The name the drop-down has in the roles of the plot.
    label : str
        The words beside the drop-down.
    choices : Sequence[Tuple[str, str]]
        (the role kept, the words shown) for each choice, in the order shown.
    roles : Dict[str, str]
        The roles the plot has so far.
    start : str
        The role the drop-down starts at, for a plot whose roles do not hold one of
        the choices.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The field (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    value = roles.get(key)
    if value not in [role for role, _ in choices]:
        value = start
    return {'key': key,
            'kind': 'choice',
            'label': label,
            'choices': list(choices),
            'value': value,
            }


# ---- colour_namer --------------------------------------------------------------------
def colour_namer(colour: str) -> str:
    """
    ---- Summary ----
    Main function to give the plain name of a colour, for the caption: the nearest of
    the colours that have a name.

    ---- Inputs ----
    colour : str
        The colour as '#rrggbb'.

    ---- Globals read ----
    COLOUR_WORDS.

    ---- Outputs ----
    str
        The name, such as 'blue' or 'red-orange'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The nearest is the named colour with the smallest (r - r')² + (g - g')² +
    (b - b')².

    ---- Helpers ----
    _rgb_reader
    """

    rgb = _rgb_reader(colour)
    return min(COLOUR_WORDS,
               key=lambda name: sum((a - b) ** 2
                                    for a, b in zip(rgb,
                                                    _rgb_reader(COLOUR_WORDS[name]),
                                                    )
                                    ),
               )


# ---- colour_shader -------------------------------------------------------------------
def colour_shader(colour: str, share: float) -> str:
    """
    ---- Summary ----
    Main function to make a colour lighter by mixing white into it.

    ---- Inputs ----
    colour : str
        The colour as '#rrggbb'.
    share : float
        The share of white, 0 (the colour itself) to 1 (white).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The lighter colour as '#rrggbb'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Each of red, green and blue: c' = c + (255 - c) x share, rounded.

    ---- Helpers ----
    _rgb_reader
    """

    return '#' + ''.join(f'{round(part + (255 - part) * share):02x}'
                         for part in _rgb_reader(colour)
                         )


# ---- experiment_field_maker ----------------------------------------------------------
def experiment_field_maker(setup: Optional[dict], roles: Dict[str, str]) -> dict:
    """
    ---- Summary ----
    Main function to make the experiment picker of a form: one drop-down of every
    experiment in use by its file name, kept in the roles as the experiment's role.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles the plot has so far.

    ---- Globals read ----
    EXPERIMENT_ROLE.

    ---- Outputs ----
    dict
        The field (form_field, DATA_FORMAT.md): its value is the role the plot has
        when an experiment of this dataset fits it, otherwise the first experiment's;
        '' with no choices when no experiment is in use.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _rows_lister
    experiment_role_maker
    role_experiment_finder
    """

    names = [row['name'] for row in _rows_lister(setup)]
    choices = [(experiment_role_maker(setup, name), name) for name in names]
    value = roles.get(EXPERIMENT_ROLE, '')
    if role_experiment_finder(setup, value) is None:
        value = choices[0][0] if choices else ''
    return {'key': EXPERIMENT_ROLE,
            'kind': 'choice',
            'label': 'Experiment',
            'choices': choices,
            'value': value,
            }


# ---- experiment_role_maker -----------------------------------------------------------
def experiment_role_maker(setup: Optional[dict], name: str) -> Optional[str]:
    """
    ---- Summary ----
    Main function to give the role of an experiment: the place of each of its labels
    in its column and its replicate, which a template keeps in place of its file name.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    name : str
        The experiment name.

    ---- Globals read ----
    LABEL_KEYS (imported), ROLE_WORDS.

    ---- Outputs ----
    Optional[str]
        'Group 1: 1, Group 2: 0, time point: 2, replicate: 1' (the first label of
        Group 1, a blank Group 2, the second time point, replicate 1); None for an
        experiment that is not in use or not in the table.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_placer
    _rows_lister
    labels_lister
    """

    rows = _rows_lister(setup)
    for row in rows:
        if row['name'] == name:
            places = [_label_placer(labels_lister(rows, key), row[key])
                      for key in LABEL_KEYS
                      ]
            return ROLE_WORDS.format(*places, row['replicate'])
    return None


# ---- experiment_slimmer --------------------------------------------------------------
def experiment_slimmer(experiment: dict,
                       dataset: Optional[str],
                       fit: Optional[dict] = None,
                       background: Optional[str] = None,
                       haem_factor: float = 1.0,
                       ) -> dict:
    """
    ---- Summary ----
    Main function to keep, of a processed experiment, only what the plots of the page
    need: its traces, its additions, its averages and levels, its difference spectrum
    with its haems, the haem bands of the fit and the mean spectrum of each averaging
    region. The whole spectra are left out, as those of every file together would
    fill the computer's memory.

    ---- Inputs ----
    experiment : dict
        The processed experiment (DATA_FORMAT.md), still with its 'raw_spectra'.
    dataset : Optional[str]
        The spectrometer whose spectra hold the haems (the answer
        decomposition_dataset); None for none.
    fit : Optional[dict]
        The fit in use ('data' and 'haem_list'); None when the haems are not worked
        out.
    background : Optional[str]
        The background fitted under the haems (the answer haem_background); None
        when the haems are not worked out.
    haem_factor : float
        Scale factor of the fit shapes (config.HAEM_FACTOR).

    ---- Globals read ----
    OTHER_KEYS, TABLE_KEYS; MOD_PER_OD (imported).

    ---- Outputs ----
    dict
        The slim copy (page_experiment, DATA_FORMAT.md). 'difference' is None for a
        file without both regions or without spectra of that spectrometer;
        'difference_parts' is None without a difference, a fit or a background;
        'haem_bands' is None without a fit; 'region_spectra' is None for a file
        without those spectra.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The mean spectrum of a region, at each wavelength: the mean of the attenuation
    of the spectra whose time is inside the region, x 1000 for mOD.

    ---- Helpers ----
    difference_decomposer
    difference_spectrum_builder
    haem_bands_finder
    """

    # ---- 1 The traces, the additions, the averages and the levels --------------------
    slim: Dict[str, Any] = {key: experiment[key]
                            for key in OTHER_KEYS + TABLE_KEYS
                            if key in experiment
                            }
    slim['difference'], slim['difference_parts'] = None, None
    slim['haem_bands'] = None if fit is None else haem_bands_finder(fit)
    slim['region_spectra'] = None

    # ---- 2 The difference spectrum and the mean spectrum of each region --------------
    data = (experiment.get('raw_spectra') or {}).get(dataset)
    if data is None or 'attenuation' not in data:
        return slim
    slim['difference'] = difference_spectrum_builder(experiment, dataset)
    if slim['difference'] is not None and fit is not None and background is not None:
        slim['difference_parts'] = difference_decomposer(slim['difference'],
                                                         fit,
                                                         background,
                                                         haem_factor,
                                                         )
    times = np.asarray(data['time'], dtype=float)
    spectra = np.asarray(data['attenuation'], dtype=float)
    means = {}
    windows = (experiment.get('averages') or {}).get('windows') or {}
    for name, window in windows.items():
        inside = (times >= window['start_time']) & (times <= window['end_time'])
        if inside.any():  # a region with no spectrum has no mean
            means[name] = spectra[inside].mean(axis=0) * MOD_PER_OD
    slim['region_spectra'] = {'dataset': dataset,
                              'wavelengths_nm': np.asarray(data['wavelengths'],
                                                           dtype=float,
                                                           ),
                              'mean_mOD': means,
                              }
    return slim


# ---- form_fields_lister --------------------------------------------------------------
def form_fields_lister(plot_type: str,
                       setup: Optional[dict],
                       roles: Dict[str, str],
                       answers: Optional[dict] = None,
                       ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list the fields of the form of a plot, under its plot type and
    its cells: what the plot type asks, each field starting as the roles of the plot
    say, or as the plot type starts.

    ---- Inputs ----
    plot_type : str
        The plot type, such as 'P1'.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : Optional[dict]
        The answers of the run (config.DEFAULT_ANSWERS), for what a form offers from
        them (the haems of the fit); None for none.

    ---- Globals read ----
    FORM_MAKERS.

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md); empty for a plot
        type that asks nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    maker = FORM_MAKERS.get(plot_type)
    return maker(setup or {}, roles, answers or {}) if maker else []


# ---- form_roles_reader ---------------------------------------------------------------
def form_roles_reader(fields: List[dict], values: Dict[str, Any]) -> Dict[str, str]:
    """
    ---- Summary ----
    Main function to turn a filled-in form into the roles of its plot.

    ---- Inputs ----
    fields : List[dict]
        The fields of the form (form_fields_lister).
    values : Dict[str, Any]
        {key of the field: what the form holds}: the words picked in a drop-down, or
        True or False for a tick. A field that is not here keeps its value.

    ---- Globals read ----
    TICK_OFF, TICK_ON.

    ---- Outputs ----
    Dict[str, str]
        {key: role}; a drop-down with nothing to pick from is left out.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    roles = {}
    for field in fields:
        key = field['key']
        if field['kind'] == 'tick':
            is_on = values.get(key, field['value'] == TICK_ON)
            roles[key] = TICK_ON if is_on else TICK_OFF
            continue
        if not field['choices']:
            continue
        by_words = {words: role for role, words in field['choices']}
        roles[key] = by_words.get(values.get(key), field['value'])
    return roles


# ---- group_choices_lister ------------------------------------------------------------
def group_choices_lister(setup: Optional[dict], key: str) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Main function to list what the drop-down of one label column offers: Split (each
    label its own set), Only <label> for each of its labels, or All together.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    key : str
        The column, one of LABEL_KEYS.

    ---- Globals read ----
    ONLY_WORDS, SPLIT, SPLIT_WORDS, TOGETHER.

    ---- Outputs ----
    List[Tuple[str, str]]
        (the role kept, the words shown) for each choice: ('Split', 'Split: each label
        on its own'), ('Only label 1', 'Only control'), ..., ('All together', 'All
        together').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _rows_lister
    labels_lister
    """

    labels = labels_lister(_rows_lister(setup), key)
    return ([(SPLIT, SPLIT_WORDS)]
            + [(ONLY_WORDS.format(place), f'Only {label}')
               for place, label in enumerate(labels, start=1)
               ]
            + [(TOGETHER, TOGETHER)]
            )


# ---- group_columns_lister ------------------------------------------------------------
def group_columns_lister(setup: Optional[dict]) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Main function to list the label columns a form has a drop-down for: each of Group
    1, Group 2 and the time point that has a label filled in.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.

    ---- Globals read ----
    LABEL_KEYS (imported).

    ---- Outputs ----
    List[Tuple[str, str]]
        (the column's key, its name: the one the user gave or "Group 1", "Group 2",
        "Time point").

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _column_namer
    _rows_lister
    labels_lister
    """

    rows = _rows_lister(setup)
    return [(key, _column_namer(setup or {}, key))
            for key in LABEL_KEYS
            if labels_lister(rows, key)
            ]


# ---- group_fields_lister -------------------------------------------------------------
def group_fields_lister(setup: Optional[dict],
                        roles: Dict[str, str],
                        splits: Sequence[str] = (COLOUR_KEY,),
                        ) -> List[dict]:
    """
    ---- Summary ----
    Main function to make the group drop-downs of a form: one for each label column
    that has a label.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles the plot has so far.
    splits : Sequence[str]
        The columns that start as Split; the others start as All together.

    ---- Globals read ----
    SPLIT, TOGETHER.

    ---- Outputs ----
    List[dict]
        The fields (form_field, DATA_FORMAT.md): each keeps the role the plot has when
        the column still offers it, otherwise how it starts.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    group_choices_lister
    group_columns_lister
    """

    fields = []
    for key, name in group_columns_lister(setup):
        choices = group_choices_lister(setup, key)
        value = roles.get(key)
        if value not in [role for role, _ in choices]:
            value = SPLIT if key in splits else TOGETHER
        fields.append({'key': key,
                       'kind': 'choice',
                       'label': name,
                       'choices': choices,
                       'value': value,
                       },
                      )
    return fields


# ---- page_experiments_lister ---------------------------------------------------------
def page_experiments_lister(page: FigurePage, setup: Optional[dict]) -> List[str]:
    """
    ---- Summary ----
    Main function to list the experiments the plots of a page show: the one a plot's
    experiment picker names, and those of the sets of a plot that shows sets.

    ---- Inputs ----
    page : FigurePage
        The page.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.

    ---- Globals read ----
    EXPERIMENT_ROLE, SET_TYPES.

    ---- Outputs ----
    List[str]
        The experiment names, each once, in the order first shown.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    plot_sets_lister
    role_experiment_finder
    """

    names: List[Optional[str]] = []
    for plot in page.plots:
        if EXPERIMENT_ROLE in plot.roles:
            names.append(role_experiment_finder(setup, plot.roles[EXPERIMENT_ROLE]))
        if plot.plot_type in SET_TYPES:
            for entry in plot_sets_lister(setup, plot.roles):
                names.extend(entry['names'])
    return list(dict.fromkeys(name for name in names if name))


# ---- plot_sets_lister ----------------------------------------------------------------
def plot_sets_lister(setup: Optional[dict], roles: Dict[str, str]) -> List[dict]:
    """
    ---- Summary ----
    Main function to list the sets of experiments a plot shows, from its group
    drop-downs: Only <label> keeps the experiments with that label, Split gives each
    label its own set (split by two columns: every combination there is), All together
    leaves the column out. A drop-down the roles do not hold is Split for Group 1 and
    All together for the others.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot.

    ---- Globals read ----
    ALL_EXPERIMENTS, LIGHTEST_SHADE, LINE_STYLES, NO_GROUP_COLOUR, ONLY_PATTERN,
    SPLIT, TOGETHER; COLOUR_KEY, LABEL_KEYS, NO_LABELS, SET_JOINER (imported).

    ---- Outputs ----
    List[dict]
        The sets in the order first seen (plot_set, DATA_FORMAT.md): each with its
        'name', the 'names' of its experiments, its 'labels', its 'base_colour' (the
        colour of its Group 1 label, black when it is not one label), its
        'line_style' (by its Group 2 label when Group 2 is split), its 'shade' (by its
        time point when the time point is split) and its 'colour' (the base colour
        with that shade). Empty when no experiment is left.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The line style of the Group 2 label in place i (from 0) of its column is
    LINE_STYLES[i mod 4]. The shade of the time point in place i of n is
    LIGHTEST_SHADE x i / (n - 1), 0 for one time point, so the same label looks the
    same on every plot.

    ---- Helpers ----
    _rows_lister
    colour_shader
    labels_lister
    """

    # ---- 1 What each drop-down says --------------------------------------------------
    rows = _rows_lister(setup)
    labels = {key: labels_lister(rows, key) for key in LABEL_KEYS}
    split_keys = []
    only_labels = {}
    for key in LABEL_KEYS:
        choice = roles.get(key, SPLIT if key == COLOUR_KEY else TOGETHER)
        only = ONLY_PATTERN.fullmatch(choice)
        if only:
            place = int(only.group(1))
            wanted = labels[key][place - 1] if 0 < place <= len(labels[key]) else None
            rows = [row for row in rows if wanted is not None and row[key] == wanted]
            only_labels[key] = wanted
        elif choice == SPLIT and labels[key]:
            split_keys.append(key)

    # ---- 2 The experiments of each set -----------------------------------------------
    grouped: Dict[tuple, List[dict]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in split_keys), []).append(row)

    # ---- 3 How each set looks --------------------------------------------------------
    colours = (setup or {}).get('colours') or {}
    sets = []
    for split_labels, members in grouped.items():
        # a set kept to one label by Only has that label too
        own = dict(only_labels, **dict(zip(split_keys, split_labels)))
        group_1 = {row[COLOUR_KEY] for row in members}
        base = colours.get(group_1.pop()) if len(group_1) == 1 else None
        base = base or NO_GROUP_COLOUR
        style, shade = LINE_STYLES[0], 0.0
        if 'group_2' in split_keys and own['group_2']:
            place = labels['group_2'].index(own['group_2'])
            style = LINE_STYLES[place % len(LINE_STYLES)]
        if 'time_point' in split_keys and own['time_point']:
            count = len(labels['time_point'])
            place = labels['time_point'].index(own['time_point'])
            shade = LIGHTEST_SHADE * place / (count - 1) if count > 1 else 0.0
        if split_keys:
            name = SET_JOINER.join(label for label in split_labels if label) or NO_LABELS
        else:
            name = ALL_EXPERIMENTS
        sets.append({'name': name,
                     'names': [row['name'] for row in members],
                     'labels': {key: own.get(key, '') for key in LABEL_KEYS},
                     'base_colour': base,
                     'line_style': style,
                     'shade': shade,
                     'colour': colour_shader(base, shade),
                     },
                    )
    return sets


# ---- role_experiment_finder ----------------------------------------------------------
def role_experiment_finder(setup: Optional[dict], role: str) -> Optional[str]:
    """
    ---- Summary ----
    Main function to find the experiment of this dataset that fits a role.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    role : str
        The role (experiment_role_maker).

    ---- Globals read ----
    LABEL_KEYS (imported), ROLE_PATTERN.

    ---- Outputs ----
    Optional[str]
        The experiment name; None when no experiment in use fits, or the role cannot
        be read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_placer
    _rows_lister
    labels_lister
    """

    found = ROLE_PATTERN.fullmatch(role or '')
    if not found:
        return None
    *places, replicate = (int(number) for number in found.groups())
    rows = _rows_lister(setup)
    labels = [labels_lister(rows, key) for key in LABEL_KEYS]
    for row in rows:
        own = [_label_placer(column, row[key])
               for column, key in zip(labels, LABEL_KEYS)
               ]
        if own == places and row['replicate'] == replicate:
            return row['name']
    return None


# ---- tick_field_maker ----------------------------------------------------------------
def tick_field_maker(key: str,
                     label: str,
                     roles: Dict[str, str],
                     is_on: bool,
                     ) -> dict:
    """
    ---- Summary ----
    Main function to make a tick of a form.

    ---- Inputs ----
    key : str
        The name the tick has in the roles of the plot.
    label : str
        The words beside the tick.
    roles : Dict[str, str]
        The roles the plot has so far.
    is_on : bool
        Whether the tick starts ticked, for a plot whose roles do not hold it.

    ---- Globals read ----
    TICK_OFF, TICK_ON.

    ---- Outputs ----
    dict
        The field (form_field, DATA_FORMAT.md), its value 'yes' or 'no'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    value = roles.get(key)
    if value not in (TICK_ON, TICK_OFF):
        value = TICK_ON if is_on else TICK_OFF
    return {'key': key, 'kind': 'tick', 'label': label, 'choices': [], 'value': value}
