"""
The plot types of a dataset figure: what the form of each asks, how each is drawn into its cells of the page and how the plots of one type share their scales.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
import textwrap
from collections import Counter
from typing import Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.difference_spectra import (haem_bands_drawer,
                                             RESIDUAL_HEIGHT_SHARE,
                                             RESIDUAL_LABEL,
                                             spectra_averager,
                                             spectra_stacker,
                                             X_LABEL,
                                             Y_LABEL,
                                             )
from utils_shared.event_concentrations import event_text_writer
from utils_shared.figure_layout import BACKDROP_MARK
from utils_shared.figure_page import FigurePage, PagePlot, PLOT_DRAWERS, SCALE_SHARERS
from utils_shared.helpers import haem_type_finder, name_simplifier
from utils_shared.individual_experiment_plotter import (experiment_drawer,
                                                        haem_ylim_sharer,
                                                        )
from utils_shared.page_data import (ADDITION_PATTERN,
                                    ADDITION_WORDS,
                                    BAND_CHOICES,
                                    BAND_KEY,
                                    CAPTION_WRITERS,
                                    choice_field_maker,
                                    colour_shader,
                                    EXPERIMENT_ROLE,
                                    experiment_field_maker,
                                    FORM_MAKERS,
                                    group_choices_lister,
                                    group_columns_lister,
                                    group_fields_lister,
                                    LIGHTEST_SHADE,
                                    ONLY_PATTERN,
                                    plot_sets_lister,
                                    role_experiment_finder,
                                    SPLIT,
                                    START_ROLE,
                                    TICK_ON,
                                    tick_field_maker,
                                    TOGETHER,
                                    ZERO_KEY,
                                    )
from utils_shared.region_statistics import (ERROR_CHOICES,
                                            legend_sentence_writer,
                                            MARK_CHOICES,
                                            p_value_marker,
                                            p_values_corrector,
                                            paired_statistics_builder,
                                            plot_statistics_builder,
                                            set_values_lister,
                                            TEST_CHOICES,
                                            )
from utils_shared.schema import HAEM_KEYS, VO2_KEYS
from utils_shared.trace_alignment import (additions_lister,
                                          CHANGE_VALUE,
                                          HAEM_TRACE_START,
                                          line_breaker,
                                          OXYGEN_TRACE,
                                          PSI_TRACE,
                                          PSI_VALUES,
                                          trace_reader,
                                          traces_aligner,
                                          traces_averager,
                                          VO2_TRACE,
                                          VO2_VALUES,
                                          )


# ---- CONSTANTS -----------------------------------------------------------------------
# The roles of a Standard experiment (P1), beside its experiment: a tick per panel (a
# haem's is HAEM_KEY_START then its name in lower-case letters and digits), the view of
# the haems and three more ticks
OXYGEN_KEY = 'panel_oxygen'
VO2_KEY = 'panel_vo2'
HAEM_KEY_START = 'panel_haem_'
DELTA_PSI_KEY = 'panel_delta_psi'
VIEW_KEY = 'haem_view'
LABELS_KEY = 'addition_labels'
REGIONS_KEY = 'regions_shaded'
SCALES_KEY = 'same_scales'
# The views of the haems, (the role kept: a key of config.HAEM_SOURCE_BY_MODE, the
# words shown), and the one a new plot starts at
VIEW_CHOICES = (('delta', 'ΔD'), ('abs', 'Absorbance'), ('percent', '% oxidised'))
FIRST_VIEW = 'delta'
# What is written in the cells of a plot that cannot be drawn
NOT_THERE = ('The experiment of this plot is not in this dataset. Open its form (✎) '
             'and pick one.')
NOT_PICKED = 'No experiment is picked for this plot yet. Open its form (✎) and pick one.'
NOT_READ = '{} could not be read, so it is not drawn.'
NO_PANEL = 'No panel of this plot has anything to show. Open its form (✎) and tick one.'
NO_HAEMS = ('{} has no haems to show as {}. Open the form of this plot (✎) and pick '
            'another view of the haems, or untick the haems.')
# The roles of a Difference spectrum (P2), beside its experiment: a tick for each
# thing it can show
COMPONENTS_KEY = 'haem_components'
BACKGROUND_KEY = 'background'
FIT_KEY = 'overall_fit'
RESIDUAL_KEY = 'residual'
BANDS_KEY = 'haem_bands'
NO_DIFFERENCE = ('{} has no difference spectrum to show: it needs an oxidised and a '
                 'reduced region, and the haems worked out in this run.')
# The roles of a Waterfall (P3): its group ('group_1', kept to one label), what one
# line is ('time_point': Split for one line per time point, the mean of its
# replicates; All together for one line per experiment), the haem its spectra are
# lined up on (the name in lower-case letters and digits) and the tick of the bands
GROUP_KEY = 'group_1'
STACK_KEY = 'time_point'
ALIGN_KEY = 'align_haem'
STACK_CHOICES = ((SPLIT, 'Each time point (the mean of its replicates)'),
                 (TOGETHER, 'Each experiment'),
                 )
NO_TIME_POINT = 'no time point'
WATERFALL_Y_LABEL = 'Reduced − oxidised (stacked)'
NO_WATERFALL = ('No experiment of this waterfall has a difference spectrum to show: '
                'each needs an oxidised and a reduced region. Open its form (✎) to '
                'pick another group.')
SENTENCE_GREY = '#555555'
# the width of a letter as a share of its height, to break a sentence into lines
LETTER_WIDTH_SHARE = 0.55
# The roles of the plots over time (P7 Single trace, P8 Mean trace, and a Waterfall
# that stacks a trace): the trace (a trace of trace_alignment.py; for a Waterfall
# also SPECTRUM_ROLE, the difference spectrum, which it starts at), the value of the
# OCR and of Δψ (the haems have VIEW_KEY), and where time 0 is (ZERO_KEY: START_ROLE or
# an addition, the first to start with). A Single trace also has LABELS_KEY and
# REGIONS_KEY, a Mean trace LABELS_KEY and BAND_KEY.
TRACE_KEY = 'trace'
VO2_VALUE_KEY = 'vo2_value'
PSI_VALUE_KEY = 'delta_psi_value'
SPECTRUM_ROLE = 'difference'
# how many additions "Time 0 at" offers: a form is made without the experiments, so
# it cannot know how many they have; an addition a file does not have is its last
ADDITIONS_OFFERED = 10
NO_TRACE = ('{} has nothing to show for the trace and the value picked. Open the form '
            'of this plot (✎) and pick another trace or another value.')
NO_MEAN = ('No experiment of this plot has anything to show for the trace and the '
           'value picked. Open its form (✎) to pick another trace, value or group.')
TIME_LABEL = 'Time (minutes)'
ZERO_TIME_LABEL = 'Time from addition {} (minutes)'
STACKED_WORDS = '{}, stacked'
# The additions on a plot over time, as on the plot of one file
ADDITION_LINE = {'linestyle': '--', 'color': '0.35', 'alpha': 0.8, 'zorder': 20}
BREAK_MARK = '//'
# The band of a Mean trace: how see-through it is
MEAN_BAND_ALPHA = 0.25
# The averaging regions shaded behind a Single trace, in the colours of the plot of
# one file: the baseline gold, the quick regions green, the settled ones blue
REGION_COLOURS = {'baseline': settings.BASELINE_WINDOW_COLOURS[0],
                  'quick': '#5DBB63',
                  'settled': '#4C9BE8',
                  }
REGION_ALPHA = 0.18
TRACE_COLOURS = {OXYGEN_TRACE: settings.TRACE_COLOURS['measured_O2'],
                 VO2_TRACE: settings.TRACE_COLOURS['OCR'],
                 PSI_TRACE: '0.15',
                 }
# The roles of the plots per region (P9 Bar chart, P10 Before and after), beside the
# measurement (TRACE_KEY and its "shown as") and the group drop-downs: the region of a
# Bar chart, the two regions of a Before and after (BASELINE_ROLE, or ADDITION_WORDS
# with the number of the addition the region comes after), the kind of region (asked
# only in a run with both kinds), what the bars show, the test and the marks
REGION_KEY = 'region'
FROM_KEY = 'region_from'
TO_KEY = 'region_to'
KIND_KEY = 'region_kind'
ERROR_KEY = 'bars'
TEST_KEY = 'test'
MARKS_KEY = 'marks'
BASELINE_ROLE = 'baseline'
BASELINE_WORDS = 'Baseline'
AFTER_WORDS = 'After addition {}'
# the kinds of averaging region, (the role kept, the words shown, the answer of the
# run that says the run has them)
REGION_KINDS = (('settled', 'Settled', 'settled_windows'),
                ('quick', 'Quick', 'quick_windows'),
                )
# the value a new Before and after shows the OCR in: as % of baseline its first
# region, the baseline, would be 100 for every experiment
PAIRED_VO2_VALUE = 'raw'
NO_VALUES = ('No experiment of this plot has a value in the region picked. Open its '
             'form (✎) to pick another measurement, region or group.')
NO_PAIRS = ('No experiment of this plot has a value in either region picked. Open its '
            'form (✎) to pick another measurement, other regions or another group.')
# A Bar chart: the width of a bar and of the row of its dots (1 is the distance between
# two bars), the share of white in the face of a bar, the colour of the error bars and
# of the brackets, and the width of the cap of an error bar (points)
BAR_WIDTH = 0.6
DOTS_WIDTH = 0.3
BAR_SHADE = 0.65
MARK_COLOUR = '0.15'
CAP_WIDTH_PT = 2.0
# the size of a dot (its width in points is DOT_WIDTHS x the width of a line)
DOT_WIDTHS = 3.0
# A Before and after: the distance from one set to the next (1 is the distance between
# its two regions), and how see-through the line of one experiment is
PAIR_STEP = 2.6
PAIR_ALPHA = 0.55
# A bracket sits this share of the height of everything drawn above what is under it,
# and its ends come down by half of that
BRACKET_STEP_SHARE = 0.07
# the share of the room of a plot its axes are taken to keep once the page has made
# room for the text, to work out how tall a mark is on the y axis
AXES_HEIGHT_SHARE = 0.6
# The roles of a Response by region (P11), beside the "shown as" of the OCR and of the
# haems, the kind of region, the group drop-downs, the bars, the test and the marks:
# what it shows (the OCR, or HAEMS_ROLE for a row per haem ticked) and a tick per haem
# (HAEM_KEY_START then its name, as in a Standard experiment). A Time points (P12) has
# the roles of a Bar chart, without the drop-down of the time point.
RESPONSE_KEY = 'response_of'
HAEMS_ROLE = 'haems'
NO_RESPONSE = ('No experiment of this plot has a value in any region. Open its form '
               '(✎) to pick another measurement or group, or to tick a haem.')
NO_POINTS = ('No experiment of this plot has both a time point and a value in the '
             'region picked. Fill in the time points in the set-up table, or open the '
             'form of this plot (✎) to pick another measurement, region or group.')
TIME_POINT_WORDS = 'Time point'
# a time point that is a number, with or without a unit after it ('24', '2.5 h')
TIME_POINT_PATTERN = re.compile(r'(-?\d+(?:[.,]\d+)?)\s*([^\d\s].*)?')
# The sets of a Response by region and of a Time points sit side by side at each
# column, over this share of the distance between two columns; the dots of one set are
# spread over DOT_SPREAD_SHARE of it and are this much paler than its mean
DODGE_SHARE = 0.4
DOT_SPREAD_SHARE = 0.08
DOT_SHADE = 0.45
# the gap between two rows of a Response by region, as a share of the room of the plot
ROW_GAP_SHARE = 0.05


# ---- SPECTRUM HELPERS ----------------------------------------------------------------


# ---- _align_band_finder --------------------------------------------------------------
def _align_band_finder(bands: Dict[str, Tuple[float, float]],
                       wanted: Optional[str],
                       ) -> Optional[Tuple[float, float]]:
    """
    ---- Summary ----
    Helper function to find the band the spectra of a waterfall are lined up on: that
    of the haem picked in the form, otherwise that of the first b haem, otherwise the
    first band there is.

    ---- Inputs ----
    bands : Dict[str, Tuple[float, float]]
        {haem name: (start, end) of its band in nm}, in the order of the fit.
    wanted : Optional[str]
        The haem picked, its name in lower-case letters and digits; None for none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Tuple[float, float]]
        (start, end) of the band in nm; None when there is no band.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _first_haem_finder
    name_simplifier
    """

    for name, band in bands.items():
        if name_simplifier(name) == wanted:
            return band
    first = _first_haem_finder(list(bands))
    return bands[first] if first is not None else None


# ---- _first_haem_finder --------------------------------------------------------------
def _first_haem_finder(names: List[str]) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find the haem a waterfall starts lined up on: the first b
    haem, otherwise the first haem.

    ---- Inputs ----
    names : List[str]
        The haem names, in the order of the fit.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The name; None for no haem.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    haem_type_finder
    """

    for name in names:
        if haem_type_finder(name) == 'b':
            return name
    return names[0] if names else None


# ---- _fit_haems_lister ---------------------------------------------------------------
def _fit_haems_lister(answers: dict) -> List[str]:
    """
    ---- Summary ----
    Helper function to list the haems the run works out, whether or not it plots
    them.

    ---- Inputs ----
    answers : dict
        The answers of the run; a missing one is as in config.DEFAULT_ANSWERS.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    List[str]
        The haem names, in the order of the answers; empty when there are none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    full = dict(settings.DEFAULT_ANSWERS, **answers)
    return list(full['haems']) if full['decompose'] else []


# ---- _spectrum_axes_styler -----------------------------------------------------------
def _spectrum_axes_styler(ax: Axes,
                          context: dict,
                          x_label: Optional[str],
                          y_label: str,
                          ) -> None:
    """
    ---- Summary ----
    Helper function to give the axes of a spectrum plot the text sizes, the font and
    the line widths of the page's journal, without the top and right edges.

    ---- Inputs ----
    ax : Axes
        The axes.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' and 'fonts' are used.
    x_label : Optional[str]
        The title of the x axis; None for an x axis without title or numbers (the
        panel under it shows them).
    y_label : str
        The title of the y axis.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    style, fonts = context['style'], context['fonts']
    words = {'fontsize': style['fonts']['label'],
             'fontfamily': fonts,
             'labelpad': style['label_pad'],
             }
    ax.set_ylabel(y_label, **words)
    if x_label is None:
        ax.tick_params(labelbottom=False)
    else:
        ax.set_xlabel(x_label, **words)
    ax.tick_params(labelsize=style['fonts']['tick'],
                   length=style['tick_length'],
                   pad=style['tick_pad'],
                   width=style['axes_line_width'],
                   )
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(fonts)
    for side, spine in ax.spines.items():
        spine.set_linewidth(style['axes_line_width'])
        spine.set_visible(side in ('left', 'bottom'))


# ---- _waterfall_roles_reader ---------------------------------------------------------
def _waterfall_roles_reader(setup: Optional[dict],
                            roles: Dict[str, str],
                            ) -> Dict[str, str]:
    """
    ---- Summary ----
    Helper function to read which experiments a waterfall shows, as the group
    drop-downs of a plot say it (plot_sets_lister): one Group 1 label, the first
    when the roles hold none this dataset has; one line per time point when the
    set-up has time points and the roles do not ask for one line per experiment.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot.

    ---- Globals read ----
    GROUP_KEY, STACK_KEY; ONLY_PATTERN, SPLIT, TOGETHER (imported).

    ---- Outputs ----
    Dict[str, str]
        {'group_1': 'Only label 1' (All together for a set-up without Group 1
        labels), 'group_2': 'All together', 'time_point': 'Split' or 'All together'}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    group_choices_lister
    group_columns_lister
    """

    groups = [role
              for role, _ in group_choices_lister(setup, GROUP_KEY)
              if ONLY_PATTERN.fullmatch(role)
              ]
    group = roles.get(GROUP_KEY)
    if group not in groups:
        group = groups[0] if groups else TOGETHER
    has_times = STACK_KEY in [key for key, _ in group_columns_lister(setup)]
    stack = roles.get(STACK_KEY) if roles.get(STACK_KEY) in (SPLIT, TOGETHER) else SPLIT
    return {GROUP_KEY: group,
            'group_2': TOGETHER,
            STACK_KEY: stack if has_times else TOGETHER,
            }


# ---- STANDARD EXPERIMENT HELPERS -----------------------------------------------------


# ---- _haem_namer ---------------------------------------------------------------------
def _haem_namer(name: str) -> str:
    """
    ---- Summary ----
    Helper function to write a haem name for a form: without the marks of the fit
    file, so 'Cyt $b_H$' becomes 'Cyt bH'.

    ---- Inputs ----
    name : str
        The haem name as written in the fit file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The name in plain letters.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return re.sub(r'[$_{}\\]', '', str(name))


# ---- _haems_lister -------------------------------------------------------------------
def _haems_lister(answers: dict) -> List[str]:
    """
    ---- Summary ----
    Helper function to list the haems the run plots: those of the fit, while the
    haems are worked out and shown.

    ---- Inputs ----
    answers : dict
        The answers of the run; a missing one is as in config.DEFAULT_ANSWERS.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    List[str]
        The haem names, in the order of the answers; empty when there are none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    full = dict(settings.DEFAULT_ANSWERS, **answers)
    if not (full['decompose'] and full['plot_haems']):
        return []
    return list(full['haems'])


# ---- _missing_sentence_finder --------------------------------------------------------
def _missing_sentence_finder(roles: Dict[str, str]) -> str:
    """
    ---- Summary ----
    Helper function to give the sentence of a plot of one experiment that has none to
    show: no experiment picked yet (a ready-made template, which leaves the pick to
    the user), or a pick that is not in this dataset.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.

    ---- Globals read ----
    NOT_PICKED, NOT_THERE; EXPERIMENT_ROLE (imported).

    ---- Outputs ----
    str
        NOT_PICKED when the roles hold no experiment, otherwise NOT_THERE.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return NOT_THERE if roles.get(EXPERIMENT_ROLE) else NOT_PICKED


# ---- _sentence_drawer ----------------------------------------------------------------
def _sentence_drawer(fig: Figure,
                     room: Tuple[float, float, float, float],
                     context: dict,
                     sentence: str,
                     ) -> List[Axes]:
    """
    ---- Summary ----
    Helper function to write one sentence in the cells of a plot that cannot be
    drawn, broken into lines that fit the width of the cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' and 'fonts' are used.
    sentence : str
        The sentence.

    ---- Globals read ----
    LETTER_WIDTH_SHARE, SENTENCE_GREY.

    ---- Outputs ----
    List[Axes]
        One set of axes over the room, switched off, with the sentence in its middle.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Letters per line = width of the room in points / (LETTER_WIDTH_SHARE x the size
    of the text in points), at least 12.

    ---- Helpers ----
    None.
    """

    x0, y0, x1, y1 = room
    size_pt = context['style']['fonts']['tick']
    width_pt = (x1 - x0) * fig.get_figwidth() * 72.0
    letters = max(int(width_pt / (LETTER_WIDTH_SHARE * size_pt)), 12)
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    ax.set_axis_off()
    ax.text(0.5,
            0.5,
            textwrap.fill(sentence, letters),
            ha='center',
            va='center',
            fontsize=size_pt,
            fontfamily=context['fonts'],
            color=SENTENCE_GREY,
            transform=ax.transAxes,
            )
    return [ax]


# ---- _standard_config_builder --------------------------------------------------------
def _standard_config_builder(experiment: dict,
                             plot: PagePlot,
                             context: dict,
                             ) -> Tuple[dict, dict, Optional[str]]:
    """
    ---- Summary ----
    Helper function to build the settings a Standard experiment is drawn with: those
    of the plot of one file in the run, at the page's journal and size, with the
    panels, the view of the haems, the addition labels and the averaging regions as
    ticked in the form of the plot. The OCR is shown as chosen in the run.

    ---- Inputs ----
    experiment : dict
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md).
    plot : PagePlot
        The plot, with its roles.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'answers' and 'page' are used.

    ---- Globals read ----
    DELTA_PSI_KEY, FIRST_VIEW, HAEM_KEY_START, LABELS_KEY, NO_HAEMS, NO_PANEL,
    OXYGEN_KEY, REGIONS_KEY, VIEW_CHOICES, VIEW_KEY, VO2_KEY;
    settings.FALLBACK_WITHOUT_OD; HAEM_KEYS, VO2_KEYS (imported).

    ---- Outputs ----
    Tuple[dict, dict, Optional[str]]
        (the settings, in the format of Config.plot_config_builder; the matplotlib
        settings of the page's journal; None, or the sentence to write in the cells
        when the plot cannot be drawn: no panel with anything to show, or haems
        ticked that the file does not have in the view picked).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _haems_lister
    _tick_reader
    name_simplifier
    """

    # ---- 1 The run's settings at the page's journal and size -------------------------
    page, roles = context['page'], plot.roles
    answers = dict(context['answers'],
                   journal=page.journal,
                   columns=page.columns,
                   height=page.height,
                   )
    cfg = settings.Config(answers)
    answers = cfg.answers

    # ---- 2 The OCR as the run shows it, where this file has it -----------------------
    is_per_od = VO2_KEYS['od'] in experiment
    vo2_source, _ = cfg.source_chooser(is_per_od)
    if VO2_KEYS[vo2_source] not in experiment:  # a file without a baseline, or range
        vo2_source = 'od' if answers['normalise_od'] and is_per_od else 'raw'

    # ---- 3 The haems ticked, in the view picked --------------------------------------
    ticked = [name
              for name in _haems_lister(answers)
              if _tick_reader(roles, HAEM_KEY_START + name_simplifier(name), True)
              ]
    views = dict(VIEW_CHOICES)
    view = roles.get(VIEW_KEY) if roles.get(VIEW_KEY) in views else FIRST_VIEW
    haem_source = cfg.haem_view_lister(is_per_od).get(view) if ticked else None
    problem = None
    if haem_source is not None and HAEM_KEYS[haem_source] not in experiment:
        plain = settings.FALLBACK_WITHOUT_OD.get(haem_source)
        if plain is not None and HAEM_KEYS[plain] in experiment:
            haem_source = plain
        else:
            problem = NO_HAEMS.format(experiment.get('experiment_name', 'This file'),
                                      views[view],
                                      )
            haem_source = None

    # ---- 4 The settings of the plot --------------------------------------------------
    has_psi = bool(answers.get('delta_psi')) and _tick_reader(roles,
                                                              DELTA_PSI_KEY,
                                                              True,
                                                              )
    config = cfg.plot_config_builder(vo2_source, haem_source, delta_psi=has_psi)
    config['HAEM_PANELS'] = [panel
                             for panel in config['HAEM_PANELS']
                             if panel['haems'][0] in ticked
                             ]
    config['PLOT_SET_AND_MEASURED_O2'] = (_tick_reader(roles, OXYGEN_KEY, True) and
                                          ('CcO2' in experiment or 'CsO2' in experiment)
                                          )
    config['PLOT_VO2'] = (_tick_reader(roles, VO2_KEY, True) and
                          VO2_KEYS[vo2_source] in experiment
                          )
    config['EVENT_LABELS'] = _tick_reader(roles, LABELS_KEY, True)
    config['PLOT_AVERAGING_WINDOWS'] = (_tick_reader(roles, REGIONS_KEY, False) and
                                        bool(experiment.get('averages'))
                                        )
    has_panel = (config['PLOT_SET_AND_MEASURED_O2'] or
                 config['PLOT_VO2'] or
                 bool(haem_source and config['HAEM_PANELS']) or
                 (config['PLOT_DELTA_PSI'] and 'delta_psi' in experiment)
                 )
    if problem is None and not has_panel:
        problem = NO_PANEL
    return config, cfg.RC_PARAMS, problem


# ---- _tick_reader --------------------------------------------------------------------
def _tick_reader(roles: Dict[str, str], key: str, is_on: bool) -> bool:
    """
    ---- Summary ----
    Helper function to read a tick from the roles of a plot.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.
    key : str
        The name of the tick.
    is_on : bool
        What a plot whose roles do not hold the tick is taken as.

    ---- Globals read ----
    TICK_ON (imported).

    ---- Outputs ----
    bool
        True when the tick is on.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return roles[key] == TICK_ON if key in roles else is_on


# ---- TRACE HELPERS -------------------------------------------------------------------


# ---- _additions_drawer ---------------------------------------------------------------
def _additions_drawer(ax: Axes,
                      moments: List[float],
                      events: List[dict],
                      context: dict,
                      has_labels: bool,
                      ) -> None:
    """
    ---- Summary ----
    Helper function to mark the additions on a plot over time, as on the plot of one
    file: a thin dashed line at each, and its label above the axes when asked.

    ---- Inputs ----
    ax : Axes
        The axes.
    moments : List[float]
        The time of each addition on the x axis (min).
    events : List[dict]
        The addition at each of those times (event, DATA_FORMAT.md), for its label.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style', 'fonts' and 'answers'
        are used.
    has_labels : bool
        True to write the labels.

    ---- Globals read ----
    ADDITION_LINE; settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    event_text_writer
    """

    style = context['style']
    answers = dict(settings.DEFAULT_ANSWERS, **context['answers'])
    for moment, event in zip(moments, events):
        ax.axvline(moment, linewidth=style['thin_line_width'], **ADDITION_LINE)
        if not has_labels:
            continue
        ax.annotate(event_text_writer(event, answers['label_mode']),
                    xy=(moment, 1),
                    xycoords=ax.get_xaxis_transform(),
                    xytext=(0, style.get('event_label_offset', 2.0)),
                    textcoords='offset points',
                    rotation=answers['event_label_angle'],
                    rotation_mode='anchor',
                    ha='left',
                    va='bottom',
                    fontsize=style['fonts']['tick'],
                    fontfamily=context['fonts'],
                    annotation_clip=False,
                    zorder=21,
                    )


# ---- _breaks_drawer ------------------------------------------------------------------
def _breaks_drawer(ax: Axes, breaks: List[float], context: dict) -> None:
    """
    ---- Summary ----
    Helper function to put a break mark on the x axis wherever the spare middle of a
    longer gap between two additions was left out.

    ---- Inputs ----
    ax : Axes
        The axes.
    breaks : List[float]
        The times of the breaks on the x axis (traces_aligner) (min).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' and 'fonts' are used.

    ---- Globals read ----
    BREAK_MARK.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for moment in breaks:
        ax.annotate(BREAK_MARK,
                    xy=(moment, 0),
                    xycoords=ax.get_xaxis_transform(),
                    ha='center',
                    va='center',
                    fontsize=context['style']['fonts']['tick'],
                    fontfamily=context['fonts'],
                    annotation_clip=False,
                    zorder=22,
                    )


# ---- _per_od_checker -----------------------------------------------------------------
def _per_od_checker(answers: dict) -> bool:
    """
    ---- Summary ----
    Helper function to check whether the run shows its haems per OD.

    ---- Inputs ----
    answers : dict
        The answers of the run; a missing one is as in config.DEFAULT_ANSWERS.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    bool
        True when OD values were entered and the haems are divided by them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    full = dict(settings.DEFAULT_ANSWERS, **answers)
    return bool(full['normalise_od'] and full.get('haem_per_od', True))


# ---- _regions_drawer -----------------------------------------------------------------
def _regions_drawer(ax: Axes, experiment: dict, shift_min: float) -> None:
    """
    ---- Summary ----
    Helper function to shade the averaging regions of an experiment behind its
    trace, each in the colour of its kind and marked as a backdrop, so the legend
    and the text may sit over them.

    ---- Inputs ----
    ax : Axes
        The axes.
    experiment : dict
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md).
    shift_min : float
        What is taken off the experiment's own times on the x axis (min).

    ---- Globals read ----
    REGION_ALPHA, REGION_COLOURS; BACKDROP_MARK (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    windows = (experiment.get('averages') or {}).get('windows') or {}
    for name, window in windows.items():
        start, end = window['start_time'], window['end_time']
        if end <= start:
            continue
        kind = window.get('kind', 'baseline' if name == 'average0' else 'settled')
        span = ax.axvspan(start - shift_min,
                          end - shift_min,
                          color=REGION_COLOURS.get(kind, REGION_COLOURS['settled']),
                          alpha=REGION_ALPHA,
                          linewidth=0,
                          zorder=0,
                          )
        setattr(span, BACKDROP_MARK, True)


# ---- _sets_aligner -------------------------------------------------------------------
def _sets_aligner(sets: List[dict],
                  roles: Dict[str, str],
                  experiments: Dict[str, dict],
                  answers: dict,
                  ) -> dict:
    """
    ---- Summary ----
    Helper function to read the trace picked of every experiment of the sets of a
    plot and line them all up on one shared time axis, so the lines of the plot can
    be compared. An experiment without that trace in that value, or with another
    number of additions than most, is left out; one that could not be read is not
    there at all.

    ---- Inputs ----
    sets : List[dict]
        The sets of the plot (plot_set, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles of the plot, for its trace, its value and its time 0.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        'times_min', 'values', 'additions_min' and 'breaks_min' as traces_aligner
        gives them; 'kept': (the place of its set, its name) of the experiment of
        each row of 'values'; 'left_out': the names left out; 'label': the title of
        the y axis ('' with nothing kept); 'events': the additions of the first
        experiment kept, in time order; 'zero': which addition is time 0, from 0, or
        None for the clocks as they are.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See traces_aligner (MATHS.md section 10.2).

    ---- Helpers ----
    _per_od_checker
    _trace_roles_reader
    additions_lister
    trace_reader
    traces_aligner
    """

    # ---- 1 The trace of each experiment ----------------------------------------------
    trace, value, zero = _trace_roles_reader(roles, answers)
    is_per_od = _per_od_checker(answers)
    members, left_out = [], []
    for place, entry in enumerate(sets):
        for name in entry['names']:
            experiment = experiments.get(name)
            if experiment is None:
                continue
            read = trace_reader(experiment, trace, value, is_per_od)
            if read is None:
                left_out.append(name)
                continue
            read['additions_min'] = additions_lister(experiment)
            members.append((place, name, read, experiment))

    # ---- 2 Lined up ------------------------------------------------------------------
    aligned = traces_aligner([read for _, _, read, _ in members], zero)
    left_out += [members[place][1] for place in aligned['left_out']]
    kept = [members[place] for place in aligned['kept']]
    events = []
    if kept:
        events = sorted((kept[0][3].get('metadata') or {}).get('events') or [],
                        key=lambda event: event['time'],
                        )
    return {'times_min': aligned['times_min'],
            'values': aligned['values'],
            'additions_min': aligned['additions_min'],
            'breaks_min': aligned['breaks_min'],
            'kept': [(place, name) for place, name, _, _ in kept],
            'left_out': left_out,
            'label': kept[0][2]['label'] if kept else '',
            'events': events,
            'zero': zero,
            }


# ---- _time_label_writer --------------------------------------------------------------
def _time_label_writer(zero: Optional[int], n_additions: int) -> str:
    """
    ---- Summary ----
    Helper function to write the title of the time axis of a plot over time.

    ---- Inputs ----
    zero : Optional[int]
        Which addition is time 0, from 0; None for the clocks as they are.
    n_additions : int
        How many additions the plot is lined up on.

    ---- Globals read ----
    TIME_LABEL, ZERO_TIME_LABEL.

    ---- Outputs ----
    str
        'Time (minutes)' without an addition at 0, otherwise 'Time from addition 2
        (minutes)', with the last addition when the one picked is not there.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if zero is None or n_additions == 0:
        return TIME_LABEL
    return ZERO_TIME_LABEL.format(min(zero, n_additions - 1) + 1)


# ---- _trace_choices_lister -----------------------------------------------------------
def _trace_choices_lister(answers: dict) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to list the traces a plot over time can show in this run: the
    oxygen, the OCR, each haem of the fit while the haems are worked out, and Δψ
    when the run works it out.

    ---- Inputs ----
    answers : dict
        The answers of the run.

    ---- Globals read ----
    HAEM_TRACE_START, OXYGEN_TRACE, PSI_TRACE, VO2_TRACE (imported).

    ---- Outputs ----
    List[Tuple[str, str]]
        (the role kept, the words shown) of each trace, in the order shown.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_haems_lister
    _haem_namer
    name_simplifier
    """

    choices = [(OXYGEN_TRACE, 'O₂'), (VO2_TRACE, 'OCR')]
    choices += [(HAEM_TRACE_START + name_simplifier(name), _haem_namer(name))
                for name in _fit_haems_lister(answers)
                ]
    if answers.get('delta_psi'):
        choices.append((PSI_TRACE, 'Δψ'))
    return choices


# ---- _trace_colour_finder ------------------------------------------------------------
def _trace_colour_finder(trace: str, answers: dict) -> str:
    """
    ---- Summary ----
    Helper function to find the colour of a trace drawn on its own: that of the
    same trace on the plot of one file.

    ---- Inputs ----
    trace : str
        The trace (a role of _trace_choices_lister).
    answers : dict
        The answers of the run, for the colours of its haems.

    ---- Globals read ----
    HAEM_TRACE_START (imported), TRACE_COLOURS.

    ---- Outputs ----
    str
        The colour.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_haems_lister
    name_simplifier
    """

    if trace in TRACE_COLOURS:
        return TRACE_COLOURS[trace]
    haems = _fit_haems_lister(answers)
    colours = settings.haem_colour_mapper(haems)
    return next((colours[name]
                 for name in haems
                 if HAEM_TRACE_START + name_simplifier(name) == trace
                 ),
                'black',
                )


# ---- _trace_fields_lister ------------------------------------------------------------
def _trace_fields_lister(roles: Dict[str, str],
                         answers: dict,
                         first: Optional[Tuple[str, str]] = None,
                         ) -> Tuple[List[dict], dict]:
    """
    ---- Summary ----
    Helper function to make the drop-downs every plot over time has in its form: the
    trace; how the OCR, the haems and Δψ are shown (the one that fits the trace
    picked is the one used); and where time 0 is.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles the plot has so far.
    answers : dict
        The answers of the run.
    first : Optional[Tuple[str, str]]
        A choice put before the traces, which the plot then starts at (the
        difference spectrum of a Waterfall); None for none, the plot starting at the
        OCR.

    ---- Globals read ----
    ADDITIONS_OFFERED, FIRST_VIEW, PSI_VALUE_KEY, TRACE_KEY, VIEW_CHOICES, VIEW_KEY,
    VO2_VALUE_KEY; ADDITION_WORDS, PSI_TRACE, PSI_VALUES, START_ROLE, ZERO_KEY
    (imported).

    ---- Outputs ----
    Tuple[List[dict], dict]
        (the trace and the "shown as" fields, in the order shown; the "Time 0 at"
        field), each a form_field (DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_haems_lister
    _trace_choices_lister
    _vo2_values_lister
    choice_field_maker
    """

    traces = _trace_choices_lister(answers)
    choices = ([first] if first else []) + traces
    label = 'Stacked' if first else 'Trace'
    start = first[0] if first else VO2_TRACE
    fields = [choice_field_maker(TRACE_KEY, label, choices, roles, start),
              choice_field_maker(VO2_VALUE_KEY,
                                 'OCR shown as',
                                 _vo2_values_lister(answers),
                                 roles,
                                 VO2_VALUES[0][0],
                                 ),
              ]
    if _fit_haems_lister(answers):
        fields.append(choice_field_maker(VIEW_KEY,
                                         'Haems shown as',
                                         VIEW_CHOICES,
                                         roles,
                                         FIRST_VIEW,
                                         ),
                      )
    if PSI_TRACE in dict(traces):
        fields.append(choice_field_maker(PSI_VALUE_KEY,
                                         'Δψ shown as',
                                         PSI_VALUES,
                                         roles,
                                         PSI_VALUES[0][0],
                                         ),
                      )
    moments = [(START_ROLE, 'The start of the recording')]
    moments += [(ADDITION_WORDS.format(number), f'Addition {number}')
                for number in range(1, ADDITIONS_OFFERED + 1)
                ]
    zero = choice_field_maker(ZERO_KEY,
                              'Time 0 at',
                              moments,
                              roles,
                              ADDITION_WORDS.format(1),
                              )
    return fields, zero


# ---- _trace_roles_reader -------------------------------------------------------------
def _trace_roles_reader(roles: Dict[str, str],
                        answers: dict,
                        ) -> Tuple[str, str, Optional[int]]:
    """
    ---- Summary ----
    Helper function to read from the roles of a plot over time its trace, the value
    that fits that trace and where its time 0 is; whatever the roles do not hold, or
    this run does not have, is as a new plot starts.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.
    answers : dict
        The answers of the run.

    ---- Globals read ----
    FIRST_VIEW, PSI_VALUE_KEY, TRACE_KEY, VIEW_CHOICES, VIEW_KEY, VO2_VALUE_KEY;
    ADDITION_PATTERN, OXYGEN_TRACE, PSI_TRACE, PSI_VALUES, START_ROLE, VO2_TRACE,
    VO2_VALUES, ZERO_KEY (imported).

    ---- Outputs ----
    Tuple[str, str, Optional[int]]
        (the trace, the OCR when the roles hold no trace of this run; its value, ''
        for the oxygen; which addition is time 0, from 0, or None for the start of
        the recording).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _trace_choices_lister
    _vo2_values_lister
    """

    # ---- 1 The trace and its value ---------------------------------------------------
    trace = roles.get(TRACE_KEY)
    if trace not in dict(_trace_choices_lister(answers)):
        trace = VO2_TRACE
    if trace == OXYGEN_TRACE:
        value = ''
    elif trace == VO2_TRACE:
        value = roles.get(VO2_VALUE_KEY)
        if value not in dict(_vo2_values_lister(answers)):
            value = VO2_VALUES[0][0]
    elif trace == PSI_TRACE:
        value = roles.get(PSI_VALUE_KEY)
        if value not in dict(PSI_VALUES):
            value = PSI_VALUES[0][0]
    else:
        value = roles.get(VIEW_KEY)
        if value not in dict(VIEW_CHOICES):
            value = FIRST_VIEW

    # ---- 2 Time 0 --------------------------------------------------------------------
    moment = roles.get(ZERO_KEY, '')
    if moment == START_ROLE:
        return trace, value, None
    found = ADDITION_PATTERN.fullmatch(moment)
    return trace, value, max(int(found.group(1)) - 1, 0) if found else 0


# ---- _vo2_values_lister --------------------------------------------------------------
def _vo2_values_lister(answers: dict) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to list the values the OCR can be shown in: per OD only in a run
    with OD values.

    ---- Inputs ----
    answers : dict
        The answers of the run; a missing one is as in config.DEFAULT_ANSWERS.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS; VO2_VALUES (imported).

    ---- Outputs ----
    List[Tuple[str, str]]
        (the role kept, the words shown) of each value, in the order shown.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    has_od = bool(dict(settings.DEFAULT_ANSWERS, **answers)['normalise_od'])
    return [(role, words) for role, words in VO2_VALUES if role != 'od' or has_od]


# ---- _waterfall_traces_drawer --------------------------------------------------------
def _waterfall_traces_drawer(fig: Figure,
                             room: Tuple[float, float, float, float],
                             plot: PagePlot,
                             context: dict,
                             ) -> List[Axes]:
    """
    ---- Summary ----
    Helper function to draw a Waterfall that stacks one trace per line in place of
    the difference spectrum: the traces lined up in time on their additions, then
    stacked from the top down, each moved so its highest point sits on its line. The
    y axis has no numbers. With no trace to show, one sentence in the cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (waterfall_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    LABELS_KEY, NO_MEAN, STACKED_WORDS.

    ---- Outputs ----
    List[Axes]
        The one set of axes of the waterfall, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    The lining up in time: traces_aligner (MATHS.md section 10.2). The stacking:
    spectra_stacker without a band (MATHS.md section 9.2). The y range is from the
    lowest to the highest point drawn, with 2 % of that height added at each end.

    ---- Helpers ----
    _additions_drawer
    _breaks_drawer
    _sentence_drawer
    _spectrum_axes_styler
    _tick_reader
    _time_label_writer
    line_breaker
    spectra_stacker
    waterfall_traces_lister
    """

    # ---- 1 The lines -----------------------------------------------------------------
    found = waterfall_traces_lister(context['setup'],
                                    plot.roles,
                                    context['experiments'],
                                    context['answers'],
                                    )
    lines = [line for line in found['lines'] if np.isfinite(line['values']).any()]
    if not lines:
        return _sentence_drawer(fig, room, context, NO_MEAN)
    times, breaks = found['times_min'], found['breaks_min']
    stacked = spectra_stacker([(times, line['values']) for line in lines])

    # ---- 2 Drawn from the top down ---------------------------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    for line, values in zip(lines, stacked):
        ax.plot(*line_breaker(times, values, breaks),
                color=line['colour'],
                linewidth=context['style']['line_width'],
                label=line['label'],
                )
    low = min(float(np.nanmin(values)) for values in stacked)
    high = max(float(np.nanmax(values)) for values in stacked)
    pad = 0.02 * (high - low) or 1.0
    ax.set_ylim(low - pad, high + pad)
    ax.set_xlim(float(times[0]), float(times[-1]))
    ax.set_yticks([])
    _additions_drawer(ax,
                      found['additions_min'],
                      found['events'],
                      context,
                      _tick_reader(plot.roles, LABELS_KEY, True),
                      )
    _breaks_drawer(ax, breaks, context)
    _spectrum_axes_styler(ax,
                          context,
                          _time_label_writer(found['zero'],
                                             len(found['additions_min']),
                                             ),
                          STACKED_WORDS.format(found['label']),
                          )
    return [ax]


# ---- REGION HELPERS ------------------------------------------------------------------


# ---- _additions_checker --------------------------------------------------------------
def _additions_checker(names: List[str],
                       experiments: Dict[str, dict],
                       answers: dict,
                       ) -> dict:
    """
    ---- Summary ----
    Helper function to check that the experiments of a plot of every region have the
    same additions: those with another number of additions than most are left out,
    and those whose additions are not written as the first one's are named.

    ---- Inputs ----
    names : List[str]
        The experiments of the plot, in the order of its sets.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md); an
        experiment that is not there is not looked at.
    answers : dict
        The answers of the run, for how the additions are written (label_mode).

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    dict
        'kept': the experiments with the number of additions most have (with a tie,
        the number met first); 'left_out': the others that were read; 'additions':
        the additions of the first experiment kept, each as written on the plot of
        one file, in order of time; 'differing': the experiments kept whose
        additions are written otherwise.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    event_text_writer
    """

    mode = dict(settings.DEFAULT_ANSWERS, **answers)['label_mode']
    texts = {}
    for name in dict.fromkeys(names):
        if experiments.get(name) is None:
            continue
        events = (experiments[name].get('metadata') or {}).get('events') or []
        events = sorted(events, key=lambda event: float(event['time']))
        texts[name] = [event_text_writer(event, mode) for event in events]
    counts = [len(found) for found in texts.values()]
    most = Counter(counts).most_common(1)[0][0] if counts else 0
    kept = [name for name, found in texts.items() if len(found) == most]
    first = texts[kept[0]] if kept else []
    return {'kept': kept,
            'left_out': [name for name in texts if name not in kept],
            'additions': first,
            'differing': [name for name in kept if texts[name] != first],
            }


# ---- _bracket_drawer -----------------------------------------------------------------
def _bracket_drawer(ax: Axes,
                    ends: Tuple[float, float],
                    height: float,
                    drop: float,
                    mark: str,
                    context: dict,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to draw a bracket between two places of a plot per region, with
    its mark (stars or a p value) above its middle.

    ---- Inputs ----
    ax : Axes
        The axes of the plot.
    ends : Tuple[float, float]
        The x of its two ends.
    height : float
        The y of its flat part.
    drop : float
        How far its two ends come down from there, in the unit of the y axis.
    mark : str
        The mark.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' and 'fonts' are used.

    ---- Globals read ----
    MARK_COLOUR.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    left, right = ends
    line, = ax.plot([left, left, right, right],
                    [height - drop, height, height, height - drop],
                    color=MARK_COLOUR,
                    linewidth=context['style']['thin_line_width'],
                    zorder=6,
                    )
    line.is_bracket = True
    ax.text((left + right) / 2.0,
            height,
            mark,
            ha='center',
            va='bottom',
            fontsize=context['style']['fonts']['tick'],
            fontfamily=context['fonts'],
            color=MARK_COLOUR,
            )


# ---- _choice_reader ------------------------------------------------------------------
def _choice_reader(roles: Dict[str, str], key: str, choices: tuple) -> str:
    """
    ---- Summary ----
    Helper function to read a drop-down of fixed choices from the roles of a plot:
    the first choice when the roles hold none of them.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.
    key : str
        The name of the drop-down in the roles.
    choices : tuple
        (the role kept, the words shown) of each choice.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The role.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    value = roles.get(key)
    return value if value in [role for role, _ in choices] else choices[0][0]


# ---- _columns_drawer -----------------------------------------------------------------
def _columns_drawer(fig: Figure,
                    ax: Axes,
                    room: Tuple[float, float, float, float],
                    sets: List[dict],
                    statistics: dict,
                    places: List[float],
                    unit: float,
                    shown: Tuple[str, str, bool],
                    context: dict,
                    ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Helper function to draw the sets of a plot with several columns (the regions of
    a Response by region, the time points of a Time points): for each set a line
    through its mean in each column, with its SEM or SD where it has more than one
    experiment, and a paler dot per experiment; the sets side by side at each
    column. A bracket with its mark joins two sets at a column only where they
    differ (corrected p under 0.05).

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    ax : Axes
        The axes to draw on.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room these axes have, as fractions of the figure.
    sets : List[dict]
        The sets drawn (plot_set, DATA_FORMAT.md), each with at least one value.
    statistics : dict
        The numbers (plot_statistics, DATA_FORMAT.md), one column per place.
    places : List[float]
        The x of each column.
    unit : float
        The distance between two columns next to each other, on the x axis.
    shown : Tuple[str, str, bool]
        (the bars, 'sem' or 'sd'; the marks, 'stars', 'p' or 'none'; True to name
        the lines, so the page gives the axes their small legend).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' and 'fonts' are used.

    ---- Globals read ----
    BRACKET_STEP_SHARE, CAP_WIDTH_PT, DODGE_SHARE, DOT_SHADE, DOT_SPREAD_SHARE,
    DOT_WIDTHS, MARK_COLOUR.

    ---- Outputs ----
    Tuple[float, float]
        (the lowest, the highest thing drawn, the marks included), in the unit of
        the y axis.

    ---- Globals mutated ----
    None. Draws on the axes (side effect).

    ---- Equations ----
    The set in place i of n (from 0) sits at x + (i / (n - 1) - 0.5) x DODGE_SHARE
    x unit, at x for one set. Its error bar runs from mean - e to mean + e, with e
    the SEM or the SD (MATHS.md section 11.2). A bracket sits BRACKET_STEP_SHARE of
    the height of everything drawn above the highest thing under it; the narrowest
    brackets are drawn first.

    ---- Helpers ----
    _bracket_drawer
    _mark_height_finder
    colour_shader
    p_value_marker
    """

    # ---- 1 Each set: its dots, its error bars and the line through its means ---------
    error, marks, is_named = shown
    style = context['style']
    dot_pt = DOT_WIDTHS * style['line_width']
    names = [entry['name'] for entry in sets]
    offsets = (np.linspace(-DODGE_SHARE / 2.0, DODGE_SHARE / 2.0, len(sets)) * unit
               if len(sets) > 1
               else np.zeros(1)
               )
    tops: Dict[Tuple[int, int], float] = {}
    lows = []
    for place, entry in enumerate(sets):
        xs, means = [], []
        for column, (told, x) in enumerate(zip(statistics['columns'], places)):
            numbers = next(
                (one for one in told['sets'] if one['name'] == entry['name']),
                None,
                )
            if numbers is None or not numbers['n']:
                continue
            here = x + offsets[place]
            values = numbers['values']
            top, low = max(values), min(values)
            if numbers['n'] > 1:
                mean, spread = numbers['mean'], numbers[error]
                ax.errorbar(here,
                            mean,
                            yerr=spread,
                            color=MARK_COLOUR,
                            linewidth=style['thin_line_width'],
                            capsize=CAP_WIDTH_PT,
                            capthick=style['thin_line_width'],
                            zorder=4,
                            )
                top, low = max(top, mean + spread), min(low, mean - spread)
            width = DOT_SPREAD_SHARE * unit
            spread_x = (np.linspace(-width / 2.0, width / 2.0, len(values))
                        if len(values) > 1
                        else np.zeros(1)
                        )
            ax.scatter(here + spread_x,
                       values,
                       s=dot_pt ** 2,
                       color=colour_shader(entry['colour'], DOT_SHADE),
                       linewidths=0,
                       zorder=3,
                       )
            xs.append(here)
            means.append(numbers['mean'])
            tops[(column, place)] = top
            lows.append(low)
        ax.plot(xs,
                means,
                color=entry['colour'],
                linestyle=entry['line_style'],
                linewidth=style['line_width'],
                marker='o',
                markersize=1.3 * dot_pt,
                markeredgecolor=MARK_COLOUR,
                markeredgewidth=style['thin_line_width'],
                label=entry['name'] if is_named else '_set',
                zorder=5,
                )

    # ---- 2 A bracket where two sets differ at a column, the narrowest first ----------
    lowest = min(lows)
    span = (max(tops.values()) - lowest) or abs(lowest) or 1.0
    step = BRACKET_STEP_SHARE * span
    letter = _mark_height_finder(fig, room, context, span)
    marked = []
    for result in statistics['tests']:
        mark = p_value_marker(result['p_corrected'], marks)
        if mark:
            marked.append((result['column'],
                           names.index(result['first']),
                           names.index(result['second']),
                           mark,
                           ),
                          )
    marked.sort(key=lambda bracket: (bracket[2] - bracket[1], bracket[0], bracket[1]))
    heights = dict(tops)  # the highest thing drawn so far over each set at each column
    for column, left, right, mark in marked:
        between = [(column, place) for place in range(left, right + 1)]
        height = max(heights[key] for key in between if key in heights) + step
        _bracket_drawer(ax,
                        (places[column] + offsets[left],
                         places[column] + offsets[right],
                         ),
                        height,
                        step / 2.0,
                        mark,
                        context,
                        )
        for key in between:
            heights[key] = height + letter
    return lowest, max(heights.values())


# ---- _floor_finder -------------------------------------------------------------------
def _floor_finder(trace: str, value: str, lowest: float) -> float:
    """
    ---- Summary ----
    Helper function to find where the y axis of a plot of several columns starts:
    at 0 for the OCR as measured, per OD or as % of baseline, and at the lowest
    thing drawn for a change from baseline, a haem or Δψ.

    ---- Inputs ----
    trace : str
        The measurement, as trace_reader takes it.
    value : str
        The value it is shown in.
    lowest : float
        The lowest thing drawn.

    ---- Globals read ----
    CHANGE_VALUE, VO2_TRACE (imported).

    ---- Outputs ----
    float
        The start of the axis, before the room _y_range_setter adds.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if trace == VO2_TRACE and value != CHANGE_VALUE:
        return min(lowest, 0.0)
    return lowest


# ---- _kind_reader --------------------------------------------------------------------
def _kind_reader(roles: Dict[str, str], answers: dict) -> str:
    """
    ---- Summary ----
    Helper function to find the kind of averaging region a plot per region reads:
    the one picked in a run with both kinds, otherwise the one the run has.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.
    answers : dict
        The answers of the run.

    ---- Globals read ----
    KIND_KEY, REGION_KINDS.

    ---- Outputs ----
    str
        'settled' or 'quick'; 'settled' for a run with neither.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _kinds_lister
    """

    kinds = _kinds_lister(answers)
    if not kinds:
        return REGION_KINDS[0][0]
    picked = roles.get(KIND_KEY)
    return picked if picked in kinds else kinds[0]


# ---- _kinds_lister -------------------------------------------------------------------
def _kinds_lister(answers: dict) -> List[str]:
    """
    ---- Summary ----
    Helper function to list the kinds of averaging region the run has.

    ---- Inputs ----
    answers : dict
        The answers of the run; a missing one is as in config.DEFAULT_ANSWERS.

    ---- Globals read ----
    REGION_KINDS; settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    List[str]
        'settled' and 'quick', each only when the run has it.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    full = dict(settings.DEFAULT_ANSWERS, **answers)
    return [role for role, _, answer in REGION_KINDS if full.get(answer)]


# ---- _mark_height_finder -------------------------------------------------------------
def _mark_height_finder(fig: Figure,
                        room: Tuple[float, float, float, float],
                        context: dict,
                        span: float,
                        ) -> float:
    """
    ---- Summary ----
    Helper function to work out how tall a mark over a bracket is on the y axis, so
    the next bracket and the top of the axis clear it.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS): its 'style' is used.
    span : float
        The height of everything drawn, in the unit of the y axis.

    ---- Globals read ----
    AXES_HEIGHT_SHARE.

    ---- Outputs ----
    float
        The height of one line of text, in the unit of the y axis.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    height = span x the size of the text in points / (AXES_HEIGHT_SHARE x the height
    of the room in points).

    ---- Helpers ----
    None.
    """

    room_pt = (room[3] - room[1]) * fig.get_figheight() * 72.0
    return span * context['style']['fonts']['tick'] / (AXES_HEIGHT_SHARE * room_pt)


# ---- _measurement_fields_lister ------------------------------------------------------
def _measurement_fields_lister(roles: Dict[str, str],
                               answers: dict,
                               vo2_start: str,
                               ) -> List[dict]:
    """
    ---- Summary ----
    Helper function to make the drop-downs of the measurement of a plot per region:
    the measurement (the OCR, each haem of the fit, Δψ when the run works it out)
    and how the OCR, the haems and Δψ are shown, the one that fits the measurement
    picked being the one used.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles the plot has so far.
    answers : dict
        The answers of the run.
    vo2_start : str
        The value a new plot shows the OCR in (a role of VO2_VALUES).

    ---- Globals read ----
    FIRST_VIEW, PSI_VALUE_KEY, TRACE_KEY, VIEW_CHOICES, VIEW_KEY, VO2_VALUE_KEY;
    OXYGEN_TRACE, PSI_TRACE, PSI_VALUES, VO2_TRACE (imported).

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_haems_lister
    _trace_choices_lister
    _vo2_values_lister
    choice_field_maker
    """

    traces = [choice
              for choice in _trace_choices_lister(answers)
              if choice[0] != OXYGEN_TRACE
              ]
    fields = [choice_field_maker(TRACE_KEY, 'Measurement', traces, roles, VO2_TRACE),
              choice_field_maker(VO2_VALUE_KEY,
                                 'OCR shown as',
                                 _vo2_values_lister(answers),
                                 roles,
                                 vo2_start,
                                 ),
              ]
    if _fit_haems_lister(answers):
        fields.append(choice_field_maker(VIEW_KEY,
                                         'Haems shown as',
                                         VIEW_CHOICES,
                                         roles,
                                         FIRST_VIEW,
                                         ),
                      )
    if PSI_TRACE in dict(traces):
        fields.append(choice_field_maker(PSI_VALUE_KEY,
                                         'Δψ shown as',
                                         PSI_VALUES,
                                         roles,
                                         PSI_VALUES[0][0],
                                         ),
                      )
    return fields


# ---- _measurement_reader -------------------------------------------------------------
def _measurement_reader(roles: Dict[str, str],
                        answers: dict,
                        vo2_start: str,
                        ) -> Tuple[str, str]:
    """
    ---- Summary ----
    Helper function to read from the roles of a plot per region its measurement and
    the value that fits it; whatever the roles do not hold, or this run does not
    have, is as a new plot starts.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.
    answers : dict
        The answers of the run.
    vo2_start : str
        The value a new plot shows the OCR in (a role of VO2_VALUES).

    ---- Globals read ----
    TRACE_KEY, VO2_VALUE_KEY; OXYGEN_TRACE, VO2_TRACE (imported).

    ---- Outputs ----
    Tuple[str, str]
        (the measurement, as trace_reader takes it; its value).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _trace_roles_reader
    _vo2_values_lister
    """

    held = dict(roles)
    if held.get(TRACE_KEY) == OXYGEN_TRACE:  # the oxygen is not offered per region
        held[TRACE_KEY] = VO2_TRACE
    if held.get(VO2_VALUE_KEY) not in dict(_vo2_values_lister(answers)):
        held[VO2_VALUE_KEY] = vo2_start
    trace, value, _ = _trace_roles_reader(held, answers)
    return trace, value


# ---- _region_field_maker -------------------------------------------------------------
def _region_field_maker(key: str,
                        label: str,
                        roles: Dict[str, str],
                        start: int,
                        ) -> dict:
    """
    ---- Summary ----
    Helper function to make the drop-down of an averaging region: the baseline, then
    the region after each addition.

    ---- Inputs ----
    key : str
        The name the drop-down has in the roles of the plot.
    label : str
        The words beside the drop-down.
    roles : Dict[str, str]
        The roles the plot has so far.
    start : int
        The region a new plot starts at: 0 for the baseline, 1 for the region after
        the first addition, and so on.

    ---- Globals read ----
    ADDITIONS_OFFERED, AFTER_WORDS, BASELINE_ROLE, BASELINE_WORDS; ADDITION_WORDS
    (imported).

    ---- Outputs ----
    dict
        The field (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_field_maker
    """

    choices = [(BASELINE_ROLE, BASELINE_WORDS)]
    choices += [(ADDITION_WORDS.format(number), AFTER_WORDS.format(number))
                for number in range(1, ADDITIONS_OFFERED + 1)
                ]
    return choice_field_maker(key, label, choices, roles, choices[start][0])


# ---- _region_reader ------------------------------------------------------------------
def _region_reader(roles: Dict[str, str], key: str, start: int) -> Tuple[int, str]:
    """
    ---- Summary ----
    Helper function to read an averaging region from the roles of a plot.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles of the plot.
    key : str
        The name of the region's drop-down in the roles.
    start : int
        The region of a plot whose roles hold none.

    ---- Globals read ----
    ADDITIONS_OFFERED, AFTER_WORDS, BASELINE_ROLE, BASELINE_WORDS; ADDITION_PATTERN
    (imported).

    ---- Outputs ----
    Tuple[int, str]
        (the region: 0 for the baseline, 1 for the region after the first addition,
        and so on; its name, 'Baseline' or 'After addition 1').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    role = roles.get(key, '')
    found = ADDITION_PATTERN.fullmatch(role)
    region = start
    if role == BASELINE_ROLE:
        region = 0
    elif found and 1 <= int(found.group(1)) <= ADDITIONS_OFFERED:
        region = int(found.group(1))
    return region, AFTER_WORDS.format(region) if region else BASELINE_WORDS


# ---- _regions_kind_fields_lister -----------------------------------------------------
def _regions_kind_fields_lister(roles: Dict[str, str], answers: dict) -> List[dict]:
    """
    ---- Summary ----
    Helper function to make the "Regions" drop-down (settled or quick) of a plot per
    region, only in a run with both kinds.

    ---- Inputs ----
    roles : Dict[str, str]
        The roles the plot has so far.
    answers : dict
        The answers of the run.

    ---- Globals read ----
    KIND_KEY, REGION_KINDS.

    ---- Outputs ----
    List[dict]
        The one field (form_field, DATA_FORMAT.md), or none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _kinds_lister
    choice_field_maker
    """

    if len(_kinds_lister(answers)) < 2:
        return []
    choices = [(role, words) for role, words, _ in REGION_KINDS]
    return [choice_field_maker(KIND_KEY, 'Regions', choices, roles, choices[0][0])]


# ---- _row_titles_splitter ------------------------------------------------------------
def _row_titles_splitter(labels: List[str]) -> Tuple[List[str], str]:
    """
    ---- Summary ----
    Helper function to split the y axis titles of the rows of one plot into the name
    of each row and the words they all end with (the value and its unit), so the unit
    is written once beside the rows.

    ---- Inputs ----
    labels : List[str]
        The title of each row ('Cyt b557 ΔD (mOD)', 'Cyt cc ΔD (mOD)').

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[List[str], str]
        (the name of each row, the words they share with a capital first letter):
        (['Cyt b557', 'Cyt cc'], 'ΔD (mOD)'). The titles as they are and '' for one
        row, for rows that end with no whole word in common, and when a row would be
        left without a name.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The shared words are the longest ending every title has, from its first space
    on, so they start at a whole word.

    ---- Helpers ----
    None.
    """

    if len(labels) < 2:
        return list(labels), ''
    length = 0
    shortest = min(len(label) for label in labels)
    while length < shortest and len({label[-length - 1] for label in labels}) == 1:
        length += 1
    ending = labels[0][len(labels[0]) - length:]
    if ' ' not in ending:
        return list(labels), ''
    ending = ending[ending.index(' '):]
    names = [label[:len(label) - len(ending)].strip() for label in labels]
    shared = ending.strip()
    if not shared or not all(names):
        return list(labels), ''
    return names, shared[:1].upper() + shared[1:]


# ---- _time_points_placer -------------------------------------------------------------
def _time_points_placer(labels: List[str], title: str) -> dict:
    """
    ---- Summary ----
    Helper function to place the time points of a Time points along its x axis: at
    their number when each is a different number (with the same unit after it, or
    none), otherwise evenly in the order given.

    ---- Inputs ----
    labels : List[str]
        The time points, in the order of the set-up table.
    title : str
        The name of the time point column.

    ---- Globals read ----
    TIME_POINT_PATTERN.

    ---- Outputs ----
    dict
        'labels': the time points in the order drawn; 'places': the x of each;
        'unit': the smallest distance between two of them (1 for one time point);
        'ticks': what is written under each; 'title': the title of the x axis, with
        the unit in brackets when the time points are numbers with one.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    As numbers: '2 h', '24 h' and '4 h' sit at x = 2, 4 and 24. Otherwise the time
    point in place i (from 0) sits at x = i.

    ---- Helpers ----
    None.
    """

    found = [TIME_POINT_PATTERN.fullmatch(label.strip()) for label in labels]
    if labels and all(found):
        units = {(match.group(2) or '').strip() for match in found}
        numbers = [float(match.group(1).replace(',', '.')) for match in found]
        if len(units) == 1 and len(set(numbers)) == len(numbers):
            order = sorted(range(len(labels)), key=numbers.__getitem__)
            places = [numbers[place] for place in order]
            gaps = np.diff(places)
            unit_words = units.pop()
            return {'labels': [labels[place] for place in order],
                    'places': places,
                    'unit': float(gaps.min()) if len(gaps) else 1.0,
                    'ticks': [found[place].group(1) for place in order],
                    'title': f'{title} ({unit_words})' if unit_words else title,
                    }
    return {'labels': list(labels),
            'places': [float(place) for place in range(len(labels))],
            'unit': 1.0,
            'ticks': list(labels),
            'title': title,
            }


# ---- _y_label_finder -----------------------------------------------------------------
def _y_label_finder(sets: List[dict],
                    experiments: Dict[str, dict],
                    trace: str,
                    value: str,
                    is_per_od: bool,
                    ) -> str:
    """
    ---- Summary ----
    Helper function to find the title of the y axis of a plot per region, with its
    unit: that of the measurement in the first experiment that has it.

    ---- Inputs ----
    sets : List[dict]
        The sets of the plot (plot_set, DATA_FORMAT.md).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    trace : str
        The measurement, as trace_reader takes it.
    value : str
        The value it is shown in.
    is_per_od : bool
        True when the run shows its haems per OD.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The title; '' when no experiment has the measurement in that value.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    trace_reader
    """

    for entry in sets:
        for name in entry['names']:
            if experiments.get(name) is None:
                continue
            read = trace_reader(experiments[name], trace, value, is_per_od)
            if read is not None:
                return read['label']
    return ''


# ---- _y_range_setter -----------------------------------------------------------------
def _y_range_setter(ax: Axes, low: float, high: float) -> None:
    """
    ---- Summary ----
    Helper function to set the y axis of a plot per region so that it holds
    everything drawn, with a little room above and below.

    ---- Inputs ----
    ax : Axes
        The axes of the plot.
    low : float
        The lowest thing drawn.
    high : float
        The highest thing drawn, the marks included.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes the axes (side effect).

    ---- Equations ----
    The axis runs from low - 0.05 x (high - low) to high + 0.05 x (high - low); an
    end at 0 stays at 0. When high = low, the room is 0.05 x |high|, or 1 at 0.

    ---- Helpers ----
    None.
    """

    room = 0.05 * (high - low) or 0.05 * abs(high) or 1.0
    ax.set_ylim(low if low == 0.0 else low - room, high if high == 0.0 else high + room)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- bar_caption_writer --------------------------------------------------------------
def bar_caption_writer(plot: PagePlot,
                       setup: Optional[dict],
                       experiments: Dict[str, dict],
                       answers: dict,
                       ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to write the sentences a Bar chart (P9) adds to the caption: what
    its dots and bars are, how many experiments each set has, and the test and the
    correction its marks come from.

    ---- Inputs ----
    plot : PagePlot
        The plot, with its roles (bar_form_maker).
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The sentences on one line; None for a plot with nothing to show.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    bar_numbers_lister
    legend_sentence_writer
    """

    found = bar_numbers_lister(setup, plot.roles, experiments, answers)
    if not found['sets']:
        return None
    return legend_sentence_writer(found['statistics'],
                                  found['error'],
                                  found['test'],
                                  found['marks'],
                                  )


# ---- bar_form_maker ------------------------------------------------------------------
def bar_form_maker(setup: dict, roles: Dict[str, str], answers: dict) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Bar chart (P9) asks: the measurement
    (the OCR) and how the OCR (% of baseline), the haems (ΔD) and Δψ (mV) are shown,
    the one that fits the measurement being the one used; the region (after the
    first addition); the kind of region, only in a run with both kinds; the group
    drop-downs (split by Group 1); the bars (SEM); the test (Student's); and the
    marks (stars).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems, its OD values, whether it works out
        Δψ and its kinds of averaging region.

    ---- Globals read ----
    ERROR_KEY, MARKS_KEY, REGION_KEY, TEST_KEY; ERROR_CHOICES, MARK_CHOICES,
    TEST_CHOICES, VO2_VALUES (imported).

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _measurement_fields_lister
    _region_field_maker
    _regions_kind_fields_lister
    choice_field_maker
    group_fields_lister
    """

    return (_measurement_fields_lister(roles, answers, VO2_VALUES[0][0]) +
            [_region_field_maker(REGION_KEY, 'Region', roles, 1)] +
            _regions_kind_fields_lister(roles, answers) +
            group_fields_lister(setup, roles) +
            [choice_field_maker(key, label, choices, roles, choices[0][0])
             for key, label, choices in ((ERROR_KEY, 'Bars', ERROR_CHOICES),
                                         (TEST_KEY, 'Test', TEST_CHOICES),
                                         (MARKS_KEY, 'Marks', MARK_CHOICES),
                                         )
             ]
            )


# ---- bar_numbers_lister --------------------------------------------------------------
def bar_numbers_lister(setup: Optional[dict],
                       roles: Dict[str, str],
                       experiments: Dict[str, dict],
                       answers: dict,
                       ) -> dict:
    """
    ---- Summary ----
    Main function to work out the numbers of a Bar chart: the value of every
    experiment of its sets in the region picked, then the mean, SD and SEM of each
    set and the test of each pair of sets. A set without a value is left out.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (bar_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    ERROR_KEY, MARKS_KEY, REGION_KEY, TEST_KEY; ERROR_CHOICES, MARK_CHOICES,
    TEST_CHOICES, VO2_VALUES (imported).

    ---- Outputs ----
    dict
        'sets': the sets that have a value (plot_set, DATA_FORMAT.md), each with its
        'values'; 'statistics': the numbers of the plot (plot_statistics,
        DATA_FORMAT.md), one column, its sets in the same order; 'label': the title
        of the y axis; 'region': the name of the region; 'error', 'test' and 'marks':
        what the form says.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See region_value_reader and plot_statistics_builder (MATHS.md section 11).

    ---- Helpers ----
    _choice_reader
    _kind_reader
    _measurement_reader
    _per_od_checker
    _region_reader
    _y_label_finder
    plot_sets_lister
    plot_statistics_builder
    set_values_lister
    """

    trace, value = _measurement_reader(roles, answers, VO2_VALUES[0][0])
    region, words = _region_reader(roles, REGION_KEY, 1)
    is_per_od = _per_od_checker(answers)
    sets = set_values_lister(plot_sets_lister(setup, roles),
                             experiments,
                             trace,
                             value,
                             region,
                             _kind_reader(roles, answers),
                             is_per_od,
                             )
    sets = [one for one in sets if any(number is not None for number in one['values'])]
    test = _choice_reader(roles, TEST_KEY, TEST_CHOICES)
    columns = [{
        'label': words,
        'sets': [{'name': one['name'], 'values': one['values']} for one in sets],
        },
               ]
    return {'sets': sets,
            'statistics': plot_statistics_builder(columns, test),
            'label': _y_label_finder(sets, experiments, trace, value, is_per_od),
            'region': words,
            'error': _choice_reader(roles, ERROR_KEY, ERROR_CHOICES),
            'test': test,
            'marks': _choice_reader(roles, MARKS_KEY, MARK_CHOICES),
            }


# ---- bar_plot_drawer -----------------------------------------------------------------
def bar_plot_drawer(fig: Figure,
                    room: Tuple[float, float, float, float],
                    plot: PagePlot,
                    context: dict,
                    ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Bar chart (P9) into the room of its cells: for each set
    a bar up to the mean of its experiments in the region picked, with its SEM or
    SD, and a dot per experiment in the colour of the set; a set of one experiment
    has its dot and no bar. A bracket with its mark joins two sets only where they
    differ (corrected p under 0.05). The y axis holds 0, every dot, bar and mark.
    With nothing to show, one sentence in the cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (bar_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    BAR_SHADE, BAR_WIDTH, BRACKET_STEP_SHARE, CAP_WIDTH_PT, DOT_WIDTHS, DOTS_WIDTH,
    MARK_COLOUR, NO_VALUES.

    ---- Outputs ----
    List[Axes]
        The one set of axes of the plot, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    A bar runs from 0 to the mean, its error bar from mean - e to mean + e, with e
    the SEM or the SD (MATHS.md section 11.2). The n dots of a set are spread evenly
    over DOTS_WIDTH around the middle of its bar. A bracket sits BRACKET_STEP_SHARE
    of the height of everything drawn above the highest thing under it (0 for a bar
    that goes down from 0); the narrowest brackets are drawn first.

    ---- Helpers ----
    _bracket_drawer
    _mark_height_finder
    _sentence_drawer
    _spectrum_axes_styler
    _y_range_setter
    bar_numbers_lister
    colour_shader
    p_value_marker
    """

    # ---- 1 The numbers ---------------------------------------------------------------
    found = bar_numbers_lister(context['setup'],
                               plot.roles,
                               context['experiments'],
                               context['answers'],
                               )
    sets, statistics = found['sets'], found['statistics']
    if not sets:
        return _sentence_drawer(fig, room, context, NO_VALUES)
    style = context['style']

    # ---- 2 Each bar, its error bar and its dots --------------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    tops, lows = [], []
    for place, (entry, numbers) in enumerate(
        zip(sets, statistics['columns'][0]['sets']),
        ):
        values = numbers['values']
        top, low = max(values), min(values)
        if numbers['n'] > 1:
            mean, spread = numbers['mean'], numbers[found['error']]
            ax.bar(place,
                   mean,
                   width=BAR_WIDTH,
                   color=colour_shader(entry['colour'], BAR_SHADE),
                   edgecolor=entry['colour'],
                   linewidth=style['line_width'],
                   linestyle=entry['line_style'],
                   zorder=1,
                   )
            ax.errorbar(place,
                        mean,
                        yerr=spread,
                        color=MARK_COLOUR,
                        linewidth=style['thin_line_width'],
                        capsize=CAP_WIDTH_PT,
                        capthick=style['thin_line_width'],
                        zorder=4,
                        )
            # a bar reaches 0 from either side, so a bracket never crosses it
            top, low = max(top, mean + spread, 0.0), min(low, mean - spread, 0.0)
        offsets = (np.linspace(-DOTS_WIDTH / 2.0, DOTS_WIDTH / 2.0, len(values))
                   if len(values) > 1
                   else np.zeros(1)
                   )
        ax.scatter(place + offsets,
                   values,
                   s=(DOT_WIDTHS * style['line_width']) ** 2,
                   color=entry['colour'],
                   edgecolors='white',
                   linewidths=style['thin_line_width'] / 2.0,
                   zorder=5,
                   )
        tops.append(top)
        lows.append(low)

    # ---- 3 A bracket where two sets differ, the narrowest first ----------------------
    lowest = min(lows + [0.0])
    span = (max(tops + [0.0]) - lowest) or 1.0
    step = BRACKET_STEP_SHARE * span
    letter = _mark_height_finder(fig, room, context, span)
    names = [entry['name'] for entry in sets]
    marked = []
    for result in statistics['tests']:
        mark = p_value_marker(result['p_corrected'], found['marks'])
        if mark:
            marked.append((names.index(result['first']),
                           names.index(result['second']),
                           mark,
                           ),
                          )
    marked.sort(key=lambda bracket: (bracket[1] - bracket[0], bracket[0]))
    heights = list(tops)  # the highest thing drawn so far over each set
    for left, right, mark in marked:
        height = max(heights[left:right + 1]) + step
        _bracket_drawer(ax, (left, right), height, step / 2.0, mark, context)
        for place in range(left, right + 1):
            heights[place] = height + letter

    # ---- 4 The axes ------------------------------------------------------------------
    _y_range_setter(ax, lowest, max(heights + [0.0]))
    if lowest < 0.0:
        ax.axhline(0.0, color=MARK_COLOUR, linewidth=style['axes_line_width'], zorder=2)
    ax.set_xlim(-0.6, len(sets) - 0.4)
    ax.set_xticks(range(len(sets)))
    ax.set_xticklabels(names)
    _spectrum_axes_styler(ax, context, found['region'], found['label'])
    if len(sets) > 3:  # many names side by side run into one another
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment('right')
    return [ax]


# ---- before_after_caption_writer -----------------------------------------------------
def before_after_caption_writer(plot: PagePlot,
                                setup: Optional[dict],
                                experiments: Dict[str, dict],
                                answers: dict,
                                ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to write the sentences a Before and after (P10) adds to the
    caption: what its lines are, how many experiments each set has, and the test and
    the correction its marks come from.

    ---- Inputs ----
    plot : PagePlot
        The plot, with its roles (before_after_form_maker).
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The sentences on one line; None for a plot with nothing to show.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    before_after_numbers_lister
    legend_sentence_writer
    """

    found = before_after_numbers_lister(setup, plot.roles, experiments, answers)
    if not found['sets']:
        return None
    return legend_sentence_writer(found['statistics'], marks=found['marks'])


# ---- before_after_form_maker ---------------------------------------------------------
def before_after_form_maker(setup: dict,
                            roles: Dict[str, str],
                            answers: dict,
                            ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Before and after (P10) asks: the
    measurement (the OCR) and how the OCR (as measured), the haems (ΔD) and Δψ (mV)
    are shown, the one that fits the measurement being the one used; the two regions
    (from the baseline, to after the first addition); the kind of region, only in a
    run with both kinds; the group drop-downs (split by Group 1); and the marks
    (stars).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems, its OD values, whether it works out
        Δψ and its kinds of averaging region.

    ---- Globals read ----
    FROM_KEY, MARKS_KEY, PAIRED_VO2_VALUE, TO_KEY; MARK_CHOICES (imported).

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _measurement_fields_lister
    _region_field_maker
    _regions_kind_fields_lister
    choice_field_maker
    group_fields_lister
    """

    return (_measurement_fields_lister(roles, answers, PAIRED_VO2_VALUE) +
            [_region_field_maker(FROM_KEY, 'From', roles, 0),
             _region_field_maker(TO_KEY, 'To', roles, 1),
             ] +
            _regions_kind_fields_lister(roles, answers) +
            group_fields_lister(setup, roles) +
            [choice_field_maker(MARKS_KEY,
                                'Marks',
                                MARK_CHOICES,
                                roles,
                                MARK_CHOICES[0][0],
                                ),
             ]
            )


# ---- before_after_numbers_lister -----------------------------------------------------
def before_after_numbers_lister(setup: Optional[dict],
                                roles: Dict[str, str],
                                experiments: Dict[str, dict],
                                answers: dict,
                                ) -> dict:
    """
    ---- Summary ----
    Main function to work out the numbers of a Before and after: the value of every
    experiment of its sets in each of the two regions picked, then the mean of each
    set in each region and the paired test between the two regions inside each set.
    A set without a value in either region is left out.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (before_after_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    FROM_KEY, MARKS_KEY, PAIRED_VO2_VALUE, TO_KEY; MARK_CHOICES (imported).

    ---- Outputs ----
    dict
        'sets': the sets that have a value (plot_set, DATA_FORMAT.md), each with
        'before' and 'after', the value of each of its experiments in the first and
        in the second region (None for none); 'statistics': the numbers of the plot
        (plot_statistics, DATA_FORMAT.md), paired, its sets in the same order;
        'label': the title of the y axis; 'regions': the names of the two regions;
        'marks': what the form says.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See region_value_reader and paired_statistics_builder (MATHS.md section 11).

    ---- Helpers ----
    _choice_reader
    _kind_reader
    _measurement_reader
    _per_od_checker
    _region_reader
    _y_label_finder
    paired_statistics_builder
    plot_sets_lister
    set_values_lister
    """

    trace, value = _measurement_reader(roles, answers, PAIRED_VO2_VALUE)
    kind, is_per_od = _kind_reader(roles, answers), _per_od_checker(answers)
    plain = plot_sets_lister(setup, roles)
    words, read = [], []
    for key, start in ((FROM_KEY, 0), (TO_KEY, 1)):
        region, name = _region_reader(roles, key, start)
        words.append(name)
        read.append(set_values_lister(plain,
                                      experiments,
                                      trace,
                                      value,
                                      region,
                                      kind,
                                      is_per_od,
                                      ),
                    )
    sets = [dict(entry, before=first['values'], after=second['values'])
            for entry, first, second in zip(plain, *read)
            ]
    sets = [one
            for one in sets
            if any(number is not None for number in one['before'] + one['after'])
            ]
    return {'sets': sets,
            'statistics': paired_statistics_builder(sets, words),
            'label': _y_label_finder(sets, experiments, trace, value, is_per_od),
            'regions': words,
            'marks': _choice_reader(roles, MARKS_KEY, MARK_CHOICES),
            }


# ---- before_after_plot_drawer --------------------------------------------------------
def before_after_plot_drawer(fig: Figure,
                             room: Tuple[float, float, float, float],
                             plot: PagePlot,
                             context: dict,
                             ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Before and after (P10) into the room of its cells: the
    sets side by side, each with its two regions; every experiment a thin line with
    a dot at each end, from its value in the first region to its value in the
    second, in the colour and line style of its set; the mean of each set of more
    than one experiment a thicker line with a diamond at each end, named, so the
    page gives the plot its small legend. A bracket with its mark sits over a set
    only where its two regions differ (paired test, corrected p under 0.05). The y
    axis holds every dot, mean and mark. With nothing to show, one sentence in the
    cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (before_after_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    BRACKET_STEP_SHARE, DOT_WIDTHS, MARK_COLOUR, NO_PAIRS, PAIR_ALPHA, PAIR_STEP.

    ---- Outputs ----
    List[Axes]
        The one set of axes of the plot, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    The set in place i (from 0) has its first region at x = PAIR_STEP x i and its
    second at x = PAIR_STEP x i + 1. An experiment with a value in one region only is
    a single dot. A bracket sits BRACKET_STEP_SHARE of the height of everything
    drawn above the highest value of its set.

    ---- Helpers ----
    _bracket_drawer
    _mark_height_finder
    _sentence_drawer
    _spectrum_axes_styler
    _y_range_setter
    before_after_numbers_lister
    p_value_marker
    """

    # ---- 1 The numbers ---------------------------------------------------------------
    found = before_after_numbers_lister(context['setup'],
                                        plot.roles,
                                        context['experiments'],
                                        context['answers'],
                                        )
    sets, statistics = found['sets'], found['statistics']
    if not sets:
        return _sentence_drawer(fig, room, context, NO_PAIRS)
    style = context['style']
    dot_pt = DOT_WIDTHS * style['line_width']

    # ---- 2 Each experiment, and the mean of each set ---------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    tops, lows = [], []
    for place, entry in enumerate(sets):
        ends = (PAIR_STEP * place, PAIR_STEP * place + 1.0)
        means = [column['sets'][place] for column in statistics['columns']]
        has_mean = max(numbers['n'] for numbers in means) > 1
        drawn = []
        for pair in zip(entry['before'], entry['after']):
            points = [(x, number) for x, number in zip(ends, pair) if number is not None]
            if not points:
                continue
            drawn += [number for _, number in points]
            ax.plot(*zip(*points),
                    color=entry['colour'],
                    linestyle=entry['line_style'],
                    linewidth=style['thin_line_width'],
                    marker='o',
                    markersize=dot_pt,
                    markeredgewidth=0,
                    alpha=PAIR_ALPHA,
                    # a set of one experiment has no mean: its line carries its name
                    label='_one' if has_mean else entry['name'],
                    zorder=3,
                    )
        if has_mean:
            ax.plot(ends,
                    [numbers['mean'] for numbers in means],
                    color=entry['colour'],
                    linestyle=entry['line_style'],
                    linewidth=2.0 * style['line_width'],
                    marker='D',
                    markersize=1.3 * dot_pt,
                    markeredgecolor=MARK_COLOUR,
                    markeredgewidth=style['thin_line_width'],
                    label=entry['name'],
                    zorder=5,
                    )
        tops.append(max(drawn))
        lows.append(min(drawn))

    # ---- 3 A bracket over each set whose two regions differ --------------------------
    lowest = min(lows)
    span = (max(tops) - lowest) or abs(lowest) or 1.0
    step = BRACKET_STEP_SHARE * span
    letter = _mark_height_finder(fig, room, context, span)
    names = [entry['name'] for entry in sets]
    heights = list(tops)
    for result in statistics['tests']:
        mark = p_value_marker(result['p_corrected'], found['marks'])
        if not mark:
            continue
        place = names.index(result['set'])
        height = tops[place] + step
        _bracket_drawer(ax,
                        (PAIR_STEP * place, PAIR_STEP * place + 1.0),
                        height,
                        step / 2.0,
                        mark,
                        context,
                        )
        heights[place] = height + letter

    # ---- 4 The axes ------------------------------------------------------------------
    _y_range_setter(ax, lowest, max(heights))
    ax.set_xlim(-0.5, PAIR_STEP * (len(sets) - 1) + 1.5)
    ax.set_xticks([PAIR_STEP * place + side
                   for place in range(len(sets))
                   for side in (0.0, 1.0)
                   ],
                  )
    ax.set_xticklabels([words.replace(' addition', '\naddition')
                        for words in found['regions']
                        ] * len(sets),
                       )
    _spectrum_axes_styler(ax, context, '', found['label'])
    return [ax]


# ---- difference_form_maker -----------------------------------------------------------
def difference_form_maker(setup: dict,
                          roles: Dict[str, str],
                          answers: dict,
                          ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Difference spectrum (P2) asks: the
    experiment, then a tick for each thing it can show: the part of each haem (on),
    the background (off), the overall fit (on), the residual in a small panel
    underneath (on) and the haem bands (off).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run; not used.

    ---- Globals read ----
    BACKGROUND_KEY, BANDS_KEY, COMPONENTS_KEY, FIT_KEY, RESIDUAL_KEY.

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_field_maker
    tick_field_maker
    """

    return [experiment_field_maker(setup, roles),
            tick_field_maker(COMPONENTS_KEY, 'The part of each haem', roles, True),
            tick_field_maker(BACKGROUND_KEY, 'Background', roles, False),
            tick_field_maker(FIT_KEY, 'Overall fit', roles, True),
            tick_field_maker(RESIDUAL_KEY, 'Residual underneath', roles, True),
            tick_field_maker(BANDS_KEY, 'Haem bands', roles, False),
            ]


# ---- difference_plot_drawer ----------------------------------------------------------
def difference_plot_drawer(fig: Figure,
                           room: Tuple[float, float, float, float],
                           plot: PagePlot,
                           context: dict,
                           ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Difference spectrum (P2) into the room of its cells: the
    difference of one experiment, reduced minus oxidised, in black, with what its
    form ticks: the part of each haem in its colour, the background dotted, the fit
    dashed, the haem bands behind and the residual in a small panel underneath. The
    lines are named, so the page gives the plot its small legend. An experiment that
    is not in the dataset, could not be read or has no difference spectrum gives one
    sentence in the cells in place of the plot.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (difference_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    BACKGROUND_KEY, BANDS_KEY, COMPONENTS_KEY, FIT_KEY, NO_DIFFERENCE, NOT_READ,
    NOT_THERE, RESIDUAL_KEY; settings.COMPONENT_FIGURE_STYLE; EXPERIMENT_ROLE,
    RESIDUAL_HEIGHT_SHARE, RESIDUAL_LABEL, X_LABEL, Y_LABEL (imported).

    ---- Outputs ----
    List[Axes]
        The axes of the spectrum, then those of the residual when it is ticked; or
        the one set of axes of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    None. Everything is in mOD (MATHS.md section 9).

    ---- Helpers ----
    _sentence_drawer
    _spectrum_axes_styler
    _tick_reader
    haem_bands_drawer
    role_experiment_finder
    """

    # ---- 1 The experiment and its difference spectrum --------------------------------
    roles = plot.roles
    name = role_experiment_finder(context['setup'], roles.get(EXPERIMENT_ROLE, ''))
    if name is None:
        return _sentence_drawer(fig, room, context, _missing_sentence_finder(roles))
    experiment = context['experiments'].get(name)
    if experiment is None:
        return _sentence_drawer(fig, room, context, NOT_READ.format(name))
    parts =experiment.get('difference_parts')
    if parts is None:
        return _sentence_drawer(fig, room, context, NO_DIFFERENCE.format(name))

    # ---- 2 The panels: the spectrum, and the residual underneath ---------------------
    x0, y0, x1, y1 = room
    has_residual = _tick_reader(roles, RESIDUAL_KEY, True)
    if has_residual:
        grid = GridSpec(2,
                        1,
                        figure=fig,
                        left=x0,
                        bottom=y0,
                        right=x1,
                        top=y1,
                        height_ratios=(1.0 - RESIDUAL_HEIGHT_SHARE,
                                       RESIDUAL_HEIGHT_SHARE,
                                       ),
                        hspace=0.08,
                        )
        main = fig.add_subplot(grid[0])
        lower = fig.add_subplot(grid[1], sharex=main)
    else:
        main, lower = fig.add_axes((x0, y0, x1 - x0, y1 - y0)), None

    # ---- 3 The difference and what is ticked -----------------------------------------
    style, look = context['style'], settings.COMPONENT_FIGURE_STYLE
    colours = settings.haem_colour_mapper(list(parts['haems_mOD']))
    wavelengths = parts['wavelengths_nm']
    width = style['line_width']
    main.plot(wavelengths,
              parts['measured_mOD'],
              color='black',
              linewidth=width,
              label='Measured',
              )
    if _tick_reader(roles, COMPONENTS_KEY, True):
        for haem, values in parts['haems_mOD'].items():
            main.plot(wavelengths,
                      values,
                      color=colours[haem],
                      linewidth=width,
                      label=haem,
                      )
    if _tick_reader(roles, BACKGROUND_KEY, False):
        main.plot(wavelengths,
                  parts['background_mOD'],
                  color=look['background_colour'],
                  linestyle=':',
                  linewidth=width,
                  label='Background',
                  )
    if _tick_reader(roles, FIT_KEY, True):
        main.plot(wavelengths,
                  parts['fit_mOD'],
                  color=look['residual_colour'],
                  linestyle='--',
                  linewidth=width,
                  label='Fit',
                  )
    main.axhline(0, color=look['zero_colour'], linewidth=style['thin_line_width'])
    main.set_xlim(float(np.min(wavelengths)), float(np.max(wavelengths)))
    if _tick_reader(roles, BANDS_KEY, False):
        haem_bands_drawer(main, experiment.get('haem_bands') or {}, colours)
    _spectrum_axes_styler(main, context, None if has_residual else X_LABEL, Y_LABEL)
    if lower is None:
        return [main]

    # ---- 4 The residual --------------------------------------------------------------
    lower.plot(wavelengths,
               parts['residual_mOD'],
               color=look['residual_colour'],
               linewidth=width,
               )
    lower.axhline(0, color=look['zero_colour'], linewidth=style['thin_line_width'])
    _spectrum_axes_styler(lower, context, X_LABEL, RESIDUAL_LABEL)
    return [main, lower]


# ---- mean_form_maker -----------------------------------------------------------------
def mean_form_maker(setup: dict,
                    roles: Dict[str, str],
                    answers: dict,
                    ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Mean trace (P8) asks: the trace (the
    OCR) and how the OCR (% of baseline), the haems (ΔD) and Δψ (mV) are shown, the
    one that fits the trace being the one used; the group drop-downs (split by Group
    1); where time 0 is (the first addition); the band (SEM); and a tick for the
    labels of the additions (on).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems, its OD values and whether it works
        out Δψ.

    ---- Globals read ----
    LABELS_KEY; BAND_CHOICES, BAND_KEY (imported).

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _trace_fields_lister
    choice_field_maker
    group_fields_lister
    tick_field_maker
    """

    fields, zero = _trace_fields_lister(roles, answers)
    return (fields +
            group_fields_lister(setup, roles) +
            [zero,
             choice_field_maker(BAND_KEY, 'Band', BAND_CHOICES, roles, BAND_CHOICES[0][0]),
             tick_field_maker(LABELS_KEY, 'Labels of the additions', roles, True),
             ]
            )


# ---- mean_lines_lister ---------------------------------------------------------------
def mean_lines_lister(setup: Optional[dict],
                      roles: Dict[str, str],
                      experiments: Dict[str, dict],
                      answers: dict,
                      ) -> dict:
    """
    ---- Summary ----
    Main function to work out the lines of a Mean trace: the trace picked of every
    experiment of its sets, lined up on the additions on one shared time axis, then
    for each set the mean of its experiments at each shared time, with the SEM or
    the SD for its band.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (mean_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    BAND_CHOICES, BAND_KEY (imported).

    ---- Outputs ----
    dict
        What _sets_aligner gives ('times_min', 'additions_min', 'breaks_min',
        'left_out', 'label', 'events', 'zero', ...), with 'lines': one per set that
        has an experiment kept, each {'label': the name of the set with how many
        experiments its mean is of ('control (n = 3)'), 'colour', 'line_style',
        'mean': np.ndarray (n_times,), 'spread': the SEM or the SD at each time
        (n_times,), or None for no band}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See traces_aligner and traces_averager (MATHS.md section 10).

    ---- Helpers ----
    _sets_aligner
    plot_sets_lister
    traces_averager
    """

    sets = plot_sets_lister(setup, roles)
    found = _sets_aligner(sets, roles, experiments, answers)
    band = roles.get(BAND_KEY)
    if band not in dict(BAND_CHOICES):
        band = BAND_CHOICES[0][0]
    lines = []
    for place, entry in enumerate(sets):
        rows = [row for row, (owner, _) in enumerate(found['kept']) if owner == place]
        if not rows:
            continue
        averages = traces_averager(found['values'][rows])
        lines.append({'label': f"{entry['name']} (n = {len(rows)})",
                      'colour': entry['colour'],
                      'line_style': entry['line_style'],
                      'mean': averages['mean'],
                      'spread': averages.get(band),
                      },
                     )
    return dict(found, lines=lines)


# ---- mean_plot_drawer ----------------------------------------------------------------
def mean_plot_drawer(fig: Figure,
                     room: Tuple[float, float, float, float],
                     plot: PagePlot,
                     context: dict,
                     ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Mean trace (P8) into the room of its cells: one line per
    set, the mean of its experiments lined up on the additions, in the colour, line
    style and shade of the set, with its band (SEM or SD) in a see-through shade of
    the same colour; a thin dashed line at each addition, with its label when
    ticked; a break mark on the time axis where the spare middle of a longer gap was
    left out. The lines are named, so the page gives the plot its small legend. With
    nothing to show, one sentence in the cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (mean_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    LABELS_KEY, MEAN_BAND_ALPHA, NO_MEAN.

    ---- Outputs ----
    List[Axes]
        The one set of axes of the plot, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    The band runs from mean - spread to mean + spread (MATHS.md section 10.3).

    ---- Helpers ----
    _additions_drawer
    _breaks_drawer
    _sentence_drawer
    _spectrum_axes_styler
    _tick_reader
    _time_label_writer
    line_breaker
    mean_lines_lister
    """

    # ---- 1 The lines -----------------------------------------------------------------
    found = mean_lines_lister(context['setup'],
                              plot.roles,
                              context['experiments'],
                              context['answers'],
                              )
    times, breaks = found['times_min'], found['breaks_min']
    lines = [line for line in found['lines'] if np.isfinite(line['mean']).any()]
    if not lines:
        return _sentence_drawer(fig, room, context, NO_MEAN)

    # ---- 2 Each mean and its band ----------------------------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    for line in lines:
        broken, mean = line_breaker(times, line['mean'], breaks)
        ax.plot(broken,
                mean,
                color=line['colour'],
                linestyle=line['line_style'],
                linewidth=context['style']['line_width'],
                label=line['label'],
                )
        spread = line['spread']
        if spread is not None and np.isfinite(spread).any():
            ax.fill_between(broken,
                            line_breaker(times, line['mean'] - spread, breaks)[1],
                            line_breaker(times, line['mean'] + spread, breaks)[1],
                            color=line['colour'],
                            alpha=MEAN_BAND_ALPHA,
                            linewidth=0,
                            )
    ax.set_xlim(float(times[0]), float(times[-1]))

    # ---- 3 The additions, the breaks and the text ------------------------------------
    _additions_drawer(ax,
                      found['additions_min'],
                      found['events'],
                      context,
                      _tick_reader(plot.roles, LABELS_KEY, True),
                      )
    _breaks_drawer(ax, breaks, context)
    _spectrum_axes_styler(ax,
                          context,
                          _time_label_writer(found['zero'],
                                             len(found['additions_min']),
                                             ),
                          found['label'],
                          )
    return [ax]


# ---- response_caption_writer ---------------------------------------------------------
def response_caption_writer(plot: PagePlot,
                            setup: Optional[dict],
                            experiments: Dict[str, dict],
                            answers: dict,
                            ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to write the sentences a Response by region (P11) adds to the
    caption: what its dots and bars are, how many experiments each set has, and the
    test and the correction its marks come from, across every row of the plot.

    ---- Inputs ----
    plot : PagePlot
        The plot, with its roles (response_form_maker).
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The sentences on one line; None for a plot with nothing to show.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    legend_sentence_writer
    response_numbers_lister
    """

    found = response_numbers_lister(setup, plot.roles, experiments, answers)
    if not found['rows']:
        return None
    return legend_sentence_writer(found['statistics'],
                                  found['error'],
                                  found['test'],
                                  found['marks'],
                                  )


# ---- response_checks_lister ----------------------------------------------------------
def response_checks_lister(page: FigurePage,
                           setup: Optional[dict],
                           experiments: Dict[str, dict],
                           answers: dict,
                           ) -> Dict[str, List[str]]:
    """
    ---- Summary ----
    Main function to list what the Responses by region of a page say of their
    experiments: those left out for another number of additions than most of their
    plot, and those whose additions are not the ones written under the regions.

    ---- Inputs ----
    page : FigurePage
        The page.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, List[str]]
        'left_out' and 'differing': the experiment names, each once, in the order
        first met.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    response_numbers_lister
    """

    names: Dict[str, List[str]] = {'left_out': [], 'differing': []}
    for plot in page.plots:
        if plot.plot_type != 'P11':
            continue
        found = response_numbers_lister(setup, plot.roles, experiments, answers)
        for key in names:
            names[key] += found[key]
    return {key: list(dict.fromkeys(found)) for key, found in names.items()}


# ---- response_form_maker -------------------------------------------------------------
def response_form_maker(setup: dict,
                        roles: Dict[str, str],
                        answers: dict,
                        ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Response by region (P11) asks: what it
    shows (the OCR, or the haems in a run that works them out); a tick per haem, all
    on; how the OCR (% of baseline) and the haems (ΔD) are shown; the kind of
    region, only in a run with both kinds; the group drop-downs (split by Group 1);
    the bars (SEM); the test (Student's); and the marks (stars).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems, its OD values and its kinds of
        averaging region.

    ---- Globals read ----
    ERROR_KEY, FIRST_VIEW, HAEM_KEY_START, HAEMS_ROLE, MARKS_KEY, RESPONSE_KEY,
    TEST_KEY, VIEW_CHOICES, VIEW_KEY, VO2_VALUE_KEY; ERROR_CHOICES, MARK_CHOICES,
    TEST_CHOICES, VO2_TRACE, VO2_VALUES (imported).

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_haems_lister
    _haem_namer
    _regions_kind_fields_lister
    _vo2_values_lister
    choice_field_maker
    group_fields_lister
    name_simplifier
    tick_field_maker
    """

    haems = _fit_haems_lister(answers)
    measured = [(VO2_TRACE, 'OCR')] + ([(HAEMS_ROLE, 'Haems')] if haems else [])
    fields = [
        choice_field_maker(RESPONSE_KEY, 'Measurement', measured, roles, VO2_TRACE),
        ]
    fields += [tick_field_maker(HAEM_KEY_START + name_simplifier(name),
                                f'Haem: {_haem_namer(name)}',
                                roles,
                                True,
                                )
               for name in haems
               ]
    fields.append(choice_field_maker(VO2_VALUE_KEY,
                                     'OCR shown as',
                                     _vo2_values_lister(answers),
                                     roles,
                                     VO2_VALUES[0][0],
                                     ),
                  )
    if haems:
        fields.append(choice_field_maker(VIEW_KEY,
                                         'Haems shown as',
                                         VIEW_CHOICES,
                                         roles,
                                         FIRST_VIEW,
                                         ),
                      )
    return (fields +
            _regions_kind_fields_lister(roles, answers) +
            group_fields_lister(setup, roles) +
            [choice_field_maker(key, label, choices, roles, choices[0][0])
             for key, label, choices in ((ERROR_KEY, 'Bars', ERROR_CHOICES),
                                         (TEST_KEY, 'Test', TEST_CHOICES),
                                         (MARKS_KEY, 'Marks', MARK_CHOICES),
                                         )
             ]
            )


# ---- response_numbers_lister ---------------------------------------------------------
def response_numbers_lister(setup: Optional[dict],
                            roles: Dict[str, str],
                            experiments: Dict[str, dict],
                            answers: dict,
                            ) -> dict:
    """
    ---- Summary ----
    Main function to work out the numbers of a Response by region: for the OCR, or
    for each haem ticked (a row each), the value of every experiment of its sets in
    the baseline and in the region after each addition, then the mean, SD and SEM
    of each set and the test of each pair of sets in each region, corrected across
    every test of the plot, all its rows together. An experiment with another
    number of additions than most is left out; a set without a value is left out
    of its row, and of a region where it has none.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (response_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    BASELINE_WORDS, ERROR_KEY, HAEM_KEY_START, HAEMS_ROLE, MARKS_KEY, RESPONSE_KEY,
    TEST_KEY, TRACE_KEY; ERROR_CHOICES, HAEM_TRACE_START, MARK_CHOICES,
    TEST_CHOICES, VO2_TRACE, VO2_VALUES (imported).

    ---- Outputs ----
    dict
        'rows': one per measurement that has a value, each with its 'trace' and
        'value' (as trace_reader takes them), its 'label' (the title of its y
        axis), its 'sets' (plot_set, DATA_FORMAT.md, each with 'regions': the value
        of each of its experiments in each region) and its 'statistics'
        (plot_statistics, DATA_FORMAT.md, a column per region); 'regions': the
        name of each region, 'Baseline' then each addition as the first experiment
        has it; 'statistics': the columns and the tests of every row in one, for
        the caption; 'left_out' and 'differing': the experiments _additions_checker
        names; 'error', 'test' and 'marks': what the form says.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See region_value_reader, plot_statistics_builder and p_values_corrector
    (MATHS.md section 11).

    ---- Helpers ----
    _additions_checker
    _choice_reader
    _fit_haems_lister
    _kind_reader
    _measurement_reader
    _per_od_checker
    _tick_reader
    _y_label_finder
    name_simplifier
    p_values_corrector
    plot_sets_lister
    plot_statistics_builder
    set_values_lister
    """

    # ---- 1 What is shown, and the experiments that have the same regions -------------
    traces = [VO2_TRACE]
    if roles.get(RESPONSE_KEY) == HAEMS_ROLE and _fit_haems_lister(answers):
        traces = [HAEM_TRACE_START + name_simplifier(name)
                  for name in _fit_haems_lister(answers)
                  if _tick_reader(roles, HAEM_KEY_START + name_simplifier(name), True)
                  ]
    kind, is_per_od = _kind_reader(roles, answers), _per_od_checker(answers)
    test = _choice_reader(roles, TEST_KEY, TEST_CHOICES)
    plain = plot_sets_lister(setup, roles)
    checked = _additions_checker([name for entry in plain for name in entry['names']],
                                 experiments,
                                 answers,
                                 )
    kept = {name: experiments[name] for name in checked['kept']}
    regions = [BASELINE_WORDS] + checked['additions']

    # ---- 2 Each row: its values and its numbers --------------------------------------
    rows = []
    for trace in traces:
        trace, value = _measurement_reader(dict(roles, **{TRACE_KEY: trace}),
                                           answers,
                                           VO2_VALUES[0][0],
                                           )
        read = [set_values_lister(plain, kept, trace, value, region, kind, is_per_od)
                for region in range(len(regions))
                ]
        sets = [dict(entry, regions=[found[place]['values'] for found in read])
                for place, entry in enumerate(plain)
                ]
        sets = [one
                for one in sets
                if any(number is not None for found in one['regions'] for number in found)
                ]
        if not sets:
            continue
        columns = [{'label': words,
                    'sets': [{'name': one['name'], 'values': one['regions'][region]}
                             for one in sets
                             if any(number is not None
                                    for number in one['regions'][region]
                                    )
                             ],
                    }
                   for region, words in enumerate(regions)
                   ]
        rows.append({'trace': trace,
                     'value': value,
                     'label': _y_label_finder(sets, kept, trace, value, is_per_od),
                     'sets': sets,
                     'statistics': plot_statistics_builder(columns, test),
                     },
                    )

    # ---- 3 The correction across every test of the plot ------------------------------
    tests = [result for row in rows for result in row['statistics']['tests']]
    corrected = p_values_corrector([result['p'] for result in tests])
    for result, p_value in zip(tests, corrected):
        result['p_corrected'] = p_value
    return {'rows': rows,
            'regions': regions,
            'statistics': {'columns': [column
                                       for row in rows
                                       for column in row['statistics']['columns']
                                       ],
                           'tests': tests,
                           'is_paired': False,
                           },
            'left_out': checked['left_out'],
            'differing': checked['differing'],
            'error': _choice_reader(roles, ERROR_KEY, ERROR_CHOICES),
            'test': test,
            'marks': _choice_reader(roles, MARKS_KEY, MARK_CHOICES),
            }


# ---- response_plot_drawer ------------------------------------------------------------
def response_plot_drawer(fig: Figure,
                         room: Tuple[float, float, float, float],
                         plot: PagePlot,
                         context: dict,
                         ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Response by region (P11) into the room of its cells:
    every region along the bottom, the baseline then each addition by its name; for
    each set a line through its mean in each region, with its SEM or SD and a dot
    per experiment, the sets side by side; a bracket with its mark where two sets
    differ in a region. The OCR is one set of axes; the haems are a row per haem
    ticked, each with its own y axis, the names of the regions and the small legend
    under the last; several rows are each named by their haem, with the value and
    its unit written once beside them. The
    y axis starts at 0 for the OCR as measured, per OD or as % of baseline, and
    holds everything drawn otherwise. With nothing to show, one sentence in the
    cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (response_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    MARK_COLOUR, NO_RESPONSE, ROW_GAP_SHARE.

    ---- Outputs ----
    List[Axes]
        The axes of each row, from the top, then with several rows the unseen axes
        that hold the value and unit they share; or those of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    The region in place i (from 0, the baseline) sits at x = i. With n rows each is
    (1 - ROW_GAP_SHARE x (n - 1)) / n of the height of the room. The shared title
    sits label_pad left of the leftmost text of the rows.

    ---- Helpers ----
    _columns_drawer
    _floor_finder
    _row_titles_splitter
    _sentence_drawer
    _spectrum_axes_styler
    _y_range_setter
    response_numbers_lister
    """

    # ---- 1 The numbers ---------------------------------------------------------------
    found = response_numbers_lister(context['setup'],
                                    plot.roles,
                                    context['experiments'],
                                    context['answers'],
                                    )
    rows, regions = found['rows'], found['regions']
    if not rows:
        return _sentence_drawer(fig, room, context, NO_RESPONSE)

    # ---- 2 Each row ------------------------------------------------------------------
    x0, y0, x1, y1 = room
    gap = ROW_GAP_SHARE * (y1 - y0)
    height = (y1 - y0 - gap * (len(rows) - 1)) / len(rows)
    places = [float(place) for place in range(len(regions))]
    # several rows are named by their haem only: the value and its unit, the same in
    # every row, would run into one another up the short axes
    names, shared = _row_titles_splitter([row['label'] for row in rows])
    axes = []
    for place, row in enumerate(rows):
        top = y1 - place * (height + gap)
        own = (x0, top - height, x1, top)
        # only the last row names its lines, so the one small legend goes under it
        is_last = place == len(rows) - 1
        ax = fig.add_axes((x0, top - height, x1 - x0, height))
        lowest, highest = _columns_drawer(fig,
                                          ax,
                                          own,
                                          row['sets'],
                                          row['statistics'],
                                          places,
                                          1.0,
                                          (found['error'], found['marks'], is_last),
                                          context,
                                          )
        low = _floor_finder(row['trace'], row['value'], lowest)
        _y_range_setter(ax, low, highest)
        if low < 0.0 < highest:
            ax.axhline(0.0,
                       color=MARK_COLOUR,
                       linewidth=context['style']['axes_line_width'],
                       zorder=2,
                       )
        ax.set_xlim(-0.5, len(regions) - 0.5)
        ax.set_xticks(places)
        ax.set_xticklabels(regions)
        _spectrum_axes_styler(ax, context, '' if is_last else None, names[place])
        if len(regions) > 3:  # many names side by side run into one another
            for label in ax.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment('right')
        axes.append(ax)
    if not shared:
        return axes

    # ---- 3 The value and its unit, once beside the rows ------------------------------
    # Unseen axes over every row hold it, so it stays centred on the rows when the
    # page makes them smaller; it sits left of the widest numbers and name of a row.
    style = context['style']
    left = min(ax.get_tightbbox().x0 for ax in axes)
    edge = fig.transFigure.transform((x0, y0))[0]
    span = fig.add_axes((x0, y0, x1 - x0, y1 - y0), frameon=False)
    span.set_xticks([])
    span.set_yticks([])
    span.set_ylabel(shared,
                    fontsize=style['fonts']['label'],
                    fontfamily=context['fonts'],
                    labelpad=(edge - left) * 72.0 / fig.dpi + style['label_pad'],
                    )
    return axes + [span]


# ---- standard_form_maker -------------------------------------------------------------
def standard_form_maker(setup: dict,
                        roles: Dict[str, str],
                        answers: dict,
                        ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Standard experiment (P1) asks: the
    experiment; a tick per panel (the oxygen, the OCR, each haem the run plots, Δψ
    when the run works it out), all on; the view of the haems, ΔD first; and ticks
    for the labels of the additions (on), the averaging regions shaded (off) and the
    same scales as the other standard plots of the page (on).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems and whether it works out Δψ.

    ---- Globals read ----
    DELTA_PSI_KEY, FIRST_VIEW, HAEM_KEY_START, LABELS_KEY, OXYGEN_KEY, REGIONS_KEY,
    SCALES_KEY, VIEW_CHOICES, VIEW_KEY, VO2_KEY.

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_namer
    _haems_lister
    choice_field_maker
    experiment_field_maker
    name_simplifier
    tick_field_maker
    """

    # ---- 1 The experiment and its panels ---------------------------------------------
    haems = _haems_lister(answers)
    fields = [experiment_field_maker(setup, roles),
              tick_field_maker(OXYGEN_KEY, 'Panel: oxygen', roles, True),
              tick_field_maker(VO2_KEY, 'Panel: OCR', roles, True),
              ]
    fields += [tick_field_maker(HAEM_KEY_START + name_simplifier(name),
                                f'Panel: {_haem_namer(name)}',
                                roles,
                                True,
                                )
               for name in haems
               ]
    if answers.get('delta_psi'):
        fields.append(tick_field_maker(DELTA_PSI_KEY, 'Panel: Δψ', roles, True))

    # ---- 2 How it is shown -----------------------------------------------------------
    if haems:
        fields.append(choice_field_maker(VIEW_KEY,
                                         'Haems shown as',
                                         VIEW_CHOICES,
                                         roles,
                                         FIRST_VIEW,
                                         ),
                      )
    fields += [tick_field_maker(LABELS_KEY, 'Labels of the additions', roles, True),
               tick_field_maker(REGIONS_KEY, 'Averaging regions shaded', roles, False),
               tick_field_maker(SCALES_KEY,
                                'Same scales as the other standard plots',
                                roles,
                                True,
                                ),
               ]
    return fields


# ---- standard_plot_drawer ------------------------------------------------------------
def standard_plot_drawer(fig: Figure,
                         room: Tuple[float, float, float, float],
                         plot: PagePlot,
                         context: dict,
                         ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Standard experiment (P1) into the room of its cells: the
    stacked panels of one experiment, as the plot of one file in the run, at the
    page's journal. An experiment that is not in the dataset or could not be read,
    and a plot with nothing to show, give one sentence in the cells in place of the
    plot.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (standard_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    NOT_READ, NOT_THERE; EXPERIMENT_ROLE (imported).

    ---- Outputs ----
    List[Axes]
        The axes of the panels from top to bottom, then the unseen axes that hold the
        shared title of the haem panels; or the one set of axes of the sentence. Each
        panel that can share its scale has 'scale_group': ('oxygen',), ('vo2', the
        OCR source), ('haem', the haem source) or ('delta_psi',); the haems in %
        oxidised have none.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _sentence_drawer
    _standard_config_builder
    experiment_drawer
    role_experiment_finder
    """

    # ---- 1 The experiment ------------------------------------------------------------
    name = role_experiment_finder(context['setup'], plot.roles.get(EXPERIMENT_ROLE, ''))
    if name is None:
        return _sentence_drawer(fig,
                                room,
                                context,
                                _missing_sentence_finder(plot.roles),
                                )
    experiment = context['experiments'].get(name)
    if experiment is None:
        return _sentence_drawer(fig, room, context, NOT_READ.format(name))
    config, rc_params, problem = _standard_config_builder(experiment, plot, context)
    if problem is not None:
        return _sentence_drawer(fig, room, context, problem)

    # ---- 2 Its panels, in the room ---------------------------------------------------
    x0, y0, x1, y1 = room
    cell = GridSpec(1, 1, figure=fig, left=x0, bottom=y0, right=x1, top=y1)[0, 0]
    before = list(fig.axes)
    with matplotlib.rc_context(rc_params):
        axes, panels = experiment_drawer(fig, cell, experiment, config)
    for ax, panel in zip(axes, panels):
        if panel['type'] == 'haem':
            if config['HAEM_PLOT_VALUES'] != 'percent':  # each haem its own 0 to 100 %
                ax.scale_group = ('haem', config['HAEM_PLOT_VALUES'])
        elif panel['type'] == 'vo2':
            ax.scale_group = ('vo2', config['VO2_PLOT_VALUES'])
        else:
            ax.scale_group = (panel['type'],)
    others = [ax for ax in fig.axes if ax not in before and ax not in axes]
    return list(axes) + others


# ---- standard_scales_sharer ----------------------------------------------------------
def standard_scales_sharer(drawn: List[Tuple[PagePlot, List[Axes]]],
                           context: dict,
                           ) -> None:
    """
    ---- Summary ----
    Main function to put the Standard experiments of a page on the same scales, so
    their sizes can be compared: among the plots whose "same scales" tick is on, the
    oxygen panels share one y range, as do the OCR panels shown in the same way and
    the Δψ panels; the haem panels shown in the same way share one y range in ΔD and
    one height of range in absorbance. The haems in % oxidised keep their own.

    ---- Inputs ----
    drawn : List[Tuple[PagePlot, List[Axes]]]
        (the plot, its axes) of every Standard experiment of the page.
    context : dict
        What a plot is drawn with (PLOT_DRAWERS); not used.

    ---- Globals read ----
    SCALES_KEY.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets the y limits of the axes (side effect).

    ---- Equations ----
    Oxygen, OCR, Δψ and the haems in ΔD: low = the smallest of the lows, high = the
    largest of the highs, on every panel of the kind. The haems in absorbance:
    height = the largest (high - low); each panel runs from its own middle -
    height / 2 to its own middle + height / 2 (haem_ylim_sharer).

    ---- Helpers ----
    _tick_reader
    haem_ylim_sharer
    """

    # ---- 1 The panels of each kind ---------------------------------------------------
    groups: Dict[tuple, List[Axes]] = {}
    for plot, axes in drawn:
        if not _tick_reader(plot.roles, SCALES_KEY, True):
            continue
        for ax in axes:
            group = getattr(ax, 'scale_group', None)
            if group is not None:
                groups.setdefault(group, []).append(ax)

    # ---- 2 One scale for each kind ---------------------------------------------------
    for group, members in groups.items():
        limits = [tuple(sorted(ax.get_ylim())) for ax in members]
        is_aligned = group[0] != 'haem' or str(group[1]).startswith('delta')
        for ax, (low, high) in zip(members, haem_ylim_sharer(limits, is_aligned)):
            ax.set_ylim(low, high)


# ---- time_points_caption_writer ------------------------------------------------------
def time_points_caption_writer(plot: PagePlot,
                               setup: Optional[dict],
                               experiments: Dict[str, dict],
                               answers: dict,
                               ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to write the sentences a Time points (P12) adds to the caption:
    the region its values are from, what its dots and bars are, how many
    experiments each set has, and the test and the correction its marks come from.

    ---- Inputs ----
    plot : PagePlot
        The plot, with its roles (time_points_form_maker).
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The sentences on one line; None for a plot with nothing to show.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    legend_sentence_writer
    time_points_numbers_lister
    """

    found = time_points_numbers_lister(setup, plot.roles, experiments, answers)
    if not found['sets']:
        return None
    sentences = legend_sentence_writer(found['statistics'],
                                       found['error'],
                                       found['test'],
                                       found['marks'],
                                       )
    return f"Region: {found['region'].lower()}. {sentences}"


# ---- time_points_form_maker ----------------------------------------------------------
def time_points_form_maker(setup: dict,
                           roles: Dict[str, str],
                           answers: dict,
                           ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Time points (P12) asks: what the form
    of a Bar chart asks, without the drop-down of the time point, which is the x
    axis of the plot. See bar_form_maker.

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run.

    ---- Globals read ----
    STACK_KEY.

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    bar_form_maker
    """

    return [field
            for field in bar_form_maker(setup, roles, answers)
            if field['key'] != STACK_KEY
            ]


# ---- time_points_numbers_lister ------------------------------------------------------
def time_points_numbers_lister(setup: Optional[dict],
                               roles: Dict[str, str],
                               experiments: Dict[str, dict],
                               answers: dict,
                               ) -> dict:
    """
    ---- Summary ----
    Main function to work out the numbers of a Time points: the value of every
    experiment of its sets (by Group 1 and Group 2, never by time point) in the
    region picked, put at the time point the set-up table gives the experiment;
    then the mean, SD and SEM of each set at each time point and the test of each
    pair of sets at each time point. An experiment without a time point is not
    drawn; a set without a value is left out, and left out of a time point where
    it has none.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (time_points_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    ERROR_KEY, MARKS_KEY, REGION_KEY, STACK_KEY, TEST_KEY, TIME_POINT_WORDS;
    ERROR_CHOICES, MARK_CHOICES, TEST_CHOICES, TOGETHER, VO2_VALUES (imported).

    ---- Outputs ----
    dict
        'sets': the sets that have a value at a time point (plot_set,
        DATA_FORMAT.md), each with its 'values' and 'points' (the value and the
        time point of each of its experiments); 'statistics': the numbers of the
        plot (plot_statistics, DATA_FORMAT.md), a column per time point in the
        order drawn; 'time_points', 'places', 'unit', 'ticks' and 'title': the
        time points and where they sit (_time_points_placer); 'label': the title
        of the y axis; 'trace' and 'value': the measurement, as trace_reader takes
        it; 'region': the name of the region; 'error', 'test' and 'marks': what
        the form says.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See region_value_reader and plot_statistics_builder (MATHS.md section 11).

    ---- Helpers ----
    _choice_reader
    _kind_reader
    _measurement_reader
    _per_od_checker
    _region_reader
    _time_points_placer
    _y_label_finder
    group_columns_lister
    plot_sets_lister
    plot_statistics_builder
    set_values_lister
    """

    # ---- 1 The value and the time point of each experiment ---------------------------
    trace, value = _measurement_reader(roles, answers, VO2_VALUES[0][0])
    region, words = _region_reader(roles, REGION_KEY, 1)
    is_per_od = _per_od_checker(answers)
    sets = set_values_lister(
        plot_sets_lister(setup, dict(roles, **{STACK_KEY: TOGETHER})),
        experiments,
        trace,
        value,
        region,
        _kind_reader(roles, answers),
        is_per_od,
        )
    rows = [row for row in (setup or {}).get('rows') or [] if row['use']]
    point_of = {row['name']: row[STACK_KEY] for row in rows}
    sets = [dict(one, points=[point_of.get(name, '') for name in one['names']])
            for one in sets
            ]
    sets = [one
            for one in sets
            if any(number is not None and point
                   for number, point in zip(one['values'], one['points'])
                   )
            ]

    # ---- 2 The time points, and the numbers at each ----------------------------------
    used = {point
            for one in sets
            for number, point in zip(one['values'], one['points'])
            if number is not None and point
            }
    title = dict(group_columns_lister(setup)).get(STACK_KEY, TIME_POINT_WORDS)
    placed = _time_points_placer([point
                                  for point in dict.fromkeys(point_of.values())
                                  if point in used
                                  ],
                                 title,
                                 )
    columns = []
    for point in placed['labels']:
        members = [{'name': one['name'],
                    'values': [number
                               for number, own in zip(one['values'], one['points'])
                               if own == point
                               ],
                    }
                   for one in sets
                   ]
        columns.append({'label': point,
                        'sets': [one
                                 for one in members
                                 if any(number is not None for number in one['values'])
                                 ],
                        },
                       )
    test = _choice_reader(roles, TEST_KEY, TEST_CHOICES)
    return {'sets': sets,
            'statistics': plot_statistics_builder(columns, test),
            'time_points': placed['labels'],
            'places': placed['places'],
            'unit': placed['unit'],
            'ticks': placed['ticks'],
            'title': placed['title'],
            'label': _y_label_finder(sets, experiments, trace, value, is_per_od),
            'trace': trace,
            'value': value,
            'region': words,
            'error': _choice_reader(roles, ERROR_KEY, ERROR_CHOICES),
            'test': test,
            'marks': _choice_reader(roles, MARKS_KEY, MARK_CHOICES),
            }


# ---- time_points_plot_drawer ---------------------------------------------------------
def time_points_plot_drawer(fig: Figure,
                            room: Tuple[float, float, float, float],
                            plot: PagePlot,
                            context: dict,
                            ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Time points (P12) into the room of its cells: the time
    points of the set-up table along the bottom, at their number when they are
    numbers; for each set a line through its mean at each time point, with its SEM
    or SD and a dot per experiment, the sets side by side; a bracket with its mark
    where two sets differ at a time point. The y axis starts at 0 for the OCR as
    measured, per OD or as % of baseline, and holds everything drawn otherwise.
    With nothing to show, one sentence in the cells.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (time_points_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    MARK_COLOUR, NO_POINTS.

    ---- Outputs ----
    List[Axes]
        The one set of axes of the plot, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    The x axis runs from the first time point - unit / 2 to the last + unit / 2,
    with unit the smallest distance between two time points (_time_points_placer).

    ---- Helpers ----
    _columns_drawer
    _floor_finder
    _sentence_drawer
    _spectrum_axes_styler
    _y_range_setter
    time_points_numbers_lister
    """

    # ---- 1 The numbers ---------------------------------------------------------------
    found = time_points_numbers_lister(context['setup'],
                                       plot.roles,
                                       context['experiments'],
                                       context['answers'],
                                       )
    if not found['sets']:
        return _sentence_drawer(fig, room, context, NO_POINTS)

    # ---- 2 The sets at each time point -----------------------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    places, unit = found['places'], found['unit']
    lowest, highest = _columns_drawer(fig,
                                      ax,
                                      room,
                                      found['sets'],
                                      found['statistics'],
                                      places,
                                      unit,
                                      (found['error'], found['marks'], True),
                                      context,
                                      )

    # ---- 3 The axes ------------------------------------------------------------------
    low = _floor_finder(found['trace'], found['value'], lowest)
    _y_range_setter(ax, low, highest)
    if low < 0.0 < highest:
        ax.axhline(0.0,
                   color=MARK_COLOUR,
                   linewidth=context['style']['axes_line_width'],
                   zorder=2,
                   )
    ax.set_xlim(places[0] - unit / 2.0, places[-1] + unit / 2.0)
    ax.set_xticks(places)
    ax.set_xticklabels(found['ticks'])
    _spectrum_axes_styler(ax, context, found['title'], found['label'])
    return [ax]


# ---- trace_form_maker ----------------------------------------------------------------
def trace_form_maker(setup: dict,
                     roles: Dict[str, str],
                     answers: dict,
                     ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Single trace (P7) asks: the experiment;
    the trace (the OCR) and how the OCR (% of baseline), the haems (ΔD) and Δψ (mV)
    are shown, the one that fits the trace being the one used; where time 0 is (the
    first addition); and ticks for the labels of the additions (on) and the
    averaging regions shaded (off).

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems, its OD values and whether it works
        out Δψ.

    ---- Globals read ----
    LABELS_KEY, REGIONS_KEY.

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _trace_fields_lister
    experiment_field_maker
    tick_field_maker
    """

    fields, zero = _trace_fields_lister(roles, answers)
    return ([experiment_field_maker(setup, roles)] +
            fields +
            [zero,
             tick_field_maker(LABELS_KEY, 'Labels of the additions', roles, True),
             tick_field_maker(REGIONS_KEY, 'Averaging regions shaded', roles, False),
             ]
            )


# ---- trace_plot_drawer ---------------------------------------------------------------
def trace_plot_drawer(fig: Figure,
                      room: Tuple[float, float, float, float],
                      plot: PagePlot,
                      context: dict,
                      ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Single trace (P7) into the room of its cells: one trace
    of one experiment in the value picked, in the colour it has on the plot of one
    file, its time counted from the addition picked (or from the start of the
    recording), with a thin dashed line at each addition, its label when ticked and
    the averaging regions shaded behind when ticked. An experiment that is not in
    the dataset or could not be read, or that has nothing for the trace and value
    picked, gives one sentence in the cells in place of the plot.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (trace_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    LABELS_KEY, NO_TRACE, NOT_READ, NOT_THERE, REGIONS_KEY; EXPERIMENT_ROLE
    (imported).

    ---- Outputs ----
    List[Axes]
        The one set of axes of the plot, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    t = x - a, with x a time on the experiment's own clock and a the time of the
    addition picked (its last addition when it has fewer; 0 for the start of the
    recording or a file without additions).

    ---- Helpers ----
    _additions_drawer
    _per_od_checker
    _regions_drawer
    _sentence_drawer
    _spectrum_axes_styler
    _tick_reader
    _time_label_writer
    _trace_colour_finder
    _trace_roles_reader
    additions_lister
    role_experiment_finder
    trace_reader
    """

    # ---- 1 The experiment and its trace ----------------------------------------------
    roles, answers = plot.roles, context['answers']
    name = role_experiment_finder(context['setup'], roles.get(EXPERIMENT_ROLE, ''))
    if name is None:
        return _sentence_drawer(fig, room, context, _missing_sentence_finder(roles))
    experiment = context['experiments'].get(name)
    if experiment is None:
        return _sentence_drawer(fig, room, context, NOT_READ.format(name))
    trace, value, zero = _trace_roles_reader(roles, answers)
    read = trace_reader(experiment, trace, value, _per_od_checker(answers))
    if read is None or not np.isfinite(read['values']).any():
        return _sentence_drawer(fig, room, context, NO_TRACE.format(name))

    # ---- 2 Its time, from the addition picked ----------------------------------------
    additions = additions_lister(experiment)
    shift = 0.0
    if zero is not None and additions:
        shift = additions[min(zero, len(additions) - 1)]
    times = read['times_min'] - shift

    # ---- 3 The trace, the regions and the additions ----------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    ax.plot(times,
            read['values'],
            color=_trace_colour_finder(trace, answers),
            linewidth=context['style']['line_width'],
            )
    ax.set_xlim(float(times[0]), float(times[-1]))
    if _tick_reader(roles, REGIONS_KEY, False):
        _regions_drawer(ax, experiment, shift)
    events = sorted((experiment.get('metadata') or {}).get('events') or [],
                    key=lambda event: event['time'],
                    )
    _additions_drawer(ax,
                      [moment - shift for moment in additions],
                      events,
                      context,
                      _tick_reader(roles, LABELS_KEY, True),
                      )
    _spectrum_axes_styler(ax,
                          context,
                          _time_label_writer(zero, len(additions)),
                          read['label'],
                          )
    return [ax]


# ---- traces_left_out_lister ----------------------------------------------------------
def traces_left_out_lister(page: FigurePage,
                           setup: Optional[dict],
                           experiments: Dict[str, dict],
                           answers: dict,
                           ) -> List[str]:
    """
    ---- Summary ----
    Main function to list the experiments the Mean traces of a page, and its
    Waterfalls that stack a trace, leave out: those that were read but have nothing
    for the trace and value picked, or another number of additions than most of the
    experiments of their plot.

    ---- Inputs ----
    page : FigurePage
        The page.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    SPECTRUM_ROLE, TRACE_KEY.

    ---- Outputs ----
    List[str]
        The experiment names, each once, in the order first met.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    mean_lines_lister
    waterfall_traces_lister
    """

    names: List[str] = []
    for plot in page.plots:
        if plot.plot_type == 'P8':
            found = mean_lines_lister(setup, plot.roles, experiments, answers)
            names += found['left_out']
        elif (plot.plot_type == 'P3' and
              plot.roles.get(TRACE_KEY, SPECTRUM_ROLE) != SPECTRUM_ROLE):
            found = waterfall_traces_lister(setup, plot.roles, experiments, answers)
            names += found['left_out']
    return list(dict.fromkeys(names))


# ---- waterfall_form_maker ------------------------------------------------------------
def waterfall_form_maker(setup: dict,
                         roles: Dict[str, str],
                         answers: dict,
                         ) -> List[dict]:
    """
    ---- Summary ----
    Main function to list what the form of a Waterfall (P3) asks: what one line is
    (each time point, the mean of its replicates, or each experiment; asked only when
    the set-up has time points, and starting at each time point), the group (the
    first), what is stacked (the difference spectrum, or one trace, with how the
    OCR, the haems and Δψ are shown and where time 0 is, as in a Mean trace), the
    haem the spectra are lined up on (the first b haem) and a tick for the haem
    bands (on), these two only in a run that works out haems, and a tick for the
    labels of the additions (on), used when a trace is stacked.

    ---- Inputs ----
    setup : dict
        The set-up table (dataset_setup, DATA_FORMAT.md).
    roles : Dict[str, str]
        The roles the plot has so far; empty for a new plot.
    answers : dict
        The answers of the run, for its haems.

    ---- Globals read ----
    ALIGN_KEY, BANDS_KEY, GROUP_KEY, LABELS_KEY, SPECTRUM_ROLE, STACK_CHOICES,
    STACK_KEY; ONLY_PATTERN, SPLIT (imported).

    ---- Outputs ----
    List[dict]
        The fields in the order shown (form_field, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _first_haem_finder
    _fit_haems_lister
    _haem_namer
    _trace_fields_lister
    choice_field_maker
    group_choices_lister
    group_columns_lister
    name_simplifier
    tick_field_maker
    """

    # ---- 1 What is stacked -----------------------------------------------------------
    fields = []
    columns = dict(group_columns_lister(setup))
    if STACK_KEY in columns:
        fields.append(choice_field_maker(STACK_KEY,
                                         'One line for',
                                         STACK_CHOICES,
                                         roles,
                                         SPLIT,
                                         ),
                      )
    groups = [(role, words.replace('Only ', '', 1))
              for role, words in group_choices_lister(setup, GROUP_KEY)
              if ONLY_PATTERN.fullmatch(role)
              ]
    if groups:
        fields.append(choice_field_maker(GROUP_KEY,
                                         columns[GROUP_KEY],
                                         groups,
                                         roles,
                                         groups[0][0],
                                         ),
                      )

    # ---- 2 What is taken from each: its difference spectrum, or one trace ------------
    traces, zero = _trace_fields_lister(roles,
                                        answers,
                                        (SPECTRUM_ROLE, 'The difference spectrum'),
                                        )
    fields += traces + [zero]

    # ---- 3 The haems of the spectra, and the additions of the traces -----------------
    haems = _fit_haems_lister(answers)
    if haems:
        fields += [choice_field_maker(ALIGN_KEY,
                                      'Spectra lined up on',
                                      [(name_simplifier(name), _haem_namer(name))
                                       for name in haems
                                       ],
                                      roles,
                                      name_simplifier(_first_haem_finder(haems)),
                                      ),
                   tick_field_maker(BANDS_KEY, 'Haem bands', roles, True),
                   ]
    fields.append(tick_field_maker(LABELS_KEY, 'Labels of the additions', roles, True))
    return fields


# ---- waterfall_left_out_lister -------------------------------------------------------
def waterfall_left_out_lister(page: FigurePage,
                              setup: Optional[dict],
                              experiments: Dict[str, dict],
                              ) -> List[str]:
    """
    ---- Summary ----
    Main function to list the experiments the waterfalls of difference spectra of a
    page leave out: those that were read but have no difference spectrum. What a
    waterfall that stacks a trace leaves out is listed by traces_left_out_lister.

    ---- Inputs ----
    page : FigurePage
        The page.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).

    ---- Globals read ----
    SPECTRUM_ROLE, TRACE_KEY.

    ---- Outputs ----
    List[str]
        The experiment names, each once, in the order first met.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    waterfall_lines_lister
    """

    names: List[str] = []
    for plot in page.plots:
        if (plot.plot_type == 'P3' and
                plot.roles.get(TRACE_KEY, SPECTRUM_ROLE) == SPECTRUM_ROLE):
            names += waterfall_lines_lister(setup, plot.roles, experiments)[1]
    return list(dict.fromkeys(names))


# ---- waterfall_lines_lister ----------------------------------------------------------
def waterfall_lines_lister(setup: Optional[dict],
                           roles: Dict[str, str],
                           experiments: Dict[str, dict],
                           ) -> Tuple[List[dict], List[str]]:
    """
    ---- Summary ----
    Main function to list the lines of a waterfall, from the top down: the
    difference spectrum of each experiment of its group, or, for a time series, the
    mean difference spectrum of the replicates of each time point. An experiment
    without a difference spectrum is left out; one that could not be read is not
    there at all.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (waterfall_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).

    ---- Globals read ----
    NO_TIME_POINT, STACK_KEY; LIGHTEST_SHADE, SPLIT (imported).

    ---- Outputs ----
    Tuple[List[dict], List[str]]
        (the lines, each {'label', 'colour', 'wavelengths_nm', 'values_mOD'}; the
        experiments left out, read but without a difference spectrum). A time point
        is named with how many experiments its mean is of ('2 h (n = 3)') and has
        the shade of its set (plot_sets_lister); the experiments of a group are in
        the colour of the group, the first as it is and the last with
        LIGHTEST_SHADE of white mixed in.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The mean of the replicates: spectra_averager. The shade of experiment i of n
    (from 0): LIGHTEST_SHADE x i / (n - 1), 0 for one experiment.

    ---- Helpers ----
    _waterfall_roles_reader
    colour_shader
    plot_sets_lister
    spectra_averager
    """

    # ---- 1 The spectra of each set ---------------------------------------------------
    set_roles = _waterfall_roles_reader(setup, roles)
    lines, left_out, singles = [], [], []
    for entry in plot_sets_lister(setup, set_roles):
        spectra = []
        for name in entry['names']:
            experiment = experiments.get(name)
            if experiment is None:
                continue
            difference = experiment.get('difference')
            if difference is None:
                left_out.append(name)
                continue
            spectrum = (difference['wavelengths_nm'], difference['difference_mOD'])
            spectra.append(spectrum)
            singles.append((name, entry['base_colour'], spectrum))
        if set_roles[STACK_KEY] == SPLIT and spectra:
            # ---- 2 A time series: the mean of the replicates of each time point ------
            wavelengths, mean = spectra_averager(spectra)
            label = entry['labels'][STACK_KEY] or NO_TIME_POINT
            lines.append({'label': f'{label} (n = {len(spectra)})',
                          'colour': entry['colour'],
                          'wavelengths_nm': wavelengths,
                          'values_mOD': mean,
                          },
                         )
    if set_roles[STACK_KEY] == SPLIT:
        return lines, left_out

    # ---- 3 Otherwise each experiment, lighter down the stack -------------------------
    steps = max(len(singles) - 1, 1)
    for place, (name, colour, (wavelengths, values)) in enumerate(singles):
        lines.append({'label': name,
                      'colour': colour_shader(colour, LIGHTEST_SHADE * place / steps),
                      'wavelengths_nm': np.asarray(wavelengths, dtype=float),
                      'values_mOD': np.asarray(values, dtype=float),
                      },
                     )
    return lines, left_out


# ---- waterfall_plot_drawer -----------------------------------------------------------
def waterfall_plot_drawer(fig: Figure,
                          room: Tuple[float, float, float, float],
                          plot: PagePlot,
                          context: dict,
                          ) -> List[Axes]:
    """
    ---- Summary ----
    Main function to draw a Waterfall (P3) into the room of its cells: the
    difference spectra of a group stacked from the top down, each lined up on its
    highest point inside the band of the haem picked, in the colour of the group and
    lighter down the stack, with the haem bands behind when ticked. The y axis has
    no numbers, as each spectrum is moved to sit clear of its neighbours. The lines
    are named, so the page gives the plot its small legend. A waterfall with no
    spectrum to show gives one sentence in its cells. A waterfall that stacks a
    trace in place of the difference spectrum is drawn by _waterfall_traces_drawer.

    ---- Inputs ----
    fig : Figure
        The figure of the page.
    room : Tuple[float, float, float, float]
        (x0, y0, x1, y1) of the room of the plot, as fractions of the figure.
    plot : PagePlot
        The plot, with its roles (waterfall_form_maker).
    context : dict
        What a plot is drawn with (PLOT_DRAWERS).

    ---- Globals read ----
    ALIGN_KEY, BANDS_KEY, NO_WATERFALL, SPECTRUM_ROLE, TRACE_KEY, WATERFALL_Y_LABEL;
    X_LABEL (imported).

    ---- Outputs ----
    List[Axes]
        The one set of axes of the waterfall, or of the sentence.

    ---- Globals mutated ----
    None. Adds axes to the figure (side effect).

    ---- Equations ----
    See spectra_stacker (MATHS.md section 9). The y range is from the lowest to the
    highest point drawn, with 2 % of that height added at each end.

    ---- Helpers ----
    _align_band_finder
    _sentence_drawer
    _spectrum_axes_styler
    _tick_reader
    _waterfall_traces_drawer
    haem_bands_drawer
    spectra_stacker
    waterfall_lines_lister
    """

    # ---- 1 The lines -----------------------------------------------------------------
    roles, experiments = plot.roles, context['experiments']
    if roles.get(TRACE_KEY, SPECTRUM_ROLE) != SPECTRUM_ROLE:
        return _waterfall_traces_drawer(fig, room, plot, context)
    lines, _ = waterfall_lines_lister(context['setup'], roles, experiments)
    if not lines:
        return _sentence_drawer(fig, room, context, NO_WATERFALL)
    bands = next((experiment['haem_bands']
                  for experiment in experiments.values()
                  if experiment.get('haem_bands')
                  ),
                 {},
                 )
    stacked = spectra_stacker([(line['wavelengths_nm'], line['values_mOD'])
                               for line in lines
                               ],
                              _align_band_finder(bands, roles.get(ALIGN_KEY)),
                              )

    # ---- 2 Drawn from the top down ---------------------------------------------------
    x0, y0, x1, y1 = room
    ax = fig.add_axes((x0, y0, x1 - x0, y1 - y0))
    for line, values in zip(lines, stacked):
        ax.plot(line['wavelengths_nm'],
                values,
                color=line['colour'],
                linewidth=context['style']['line_width'],
                label=line['label'],
                )
    low = min(float(np.nanmin(values)) for values in stacked)
    high = max(float(np.nanmax(values)) for values in stacked)
    pad = 0.02 * (high - low) or 1.0
    ax.set_ylim(low - pad, high + pad)
    ax.set_xlim(min(float(np.min(line['wavelengths_nm'])) for line in lines),
                max(float(np.max(line['wavelengths_nm'])) for line in lines),
                )
    ax.set_yticks([])
    if _tick_reader(roles, BANDS_KEY, True):
        haem_bands_drawer(ax, bands, settings.haem_colour_mapper(list(bands)))
    _spectrum_axes_styler(ax, context, X_LABEL, WATERFALL_Y_LABEL)
    return [ax]


# ---- waterfall_traces_lister ---------------------------------------------------------
def waterfall_traces_lister(setup: Optional[dict],
                            roles: Dict[str, str],
                            experiments: Dict[str, dict],
                            answers: dict,
                            ) -> dict:
    """
    ---- Summary ----
    Main function to work out the lines of a waterfall that stacks a trace, from the
    top down: the trace picked of every experiment of its group, lined up on the
    additions on one shared time axis; then one line per experiment, or, for a time
    series, the mean of the replicates of each time point.

    ---- Inputs ----
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    roles : Dict[str, str]
        The roles of the plot (waterfall_form_maker).
    experiments : Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).
    answers : dict
        The answers of the run.

    ---- Globals read ----
    NO_TIME_POINT, STACK_KEY; LIGHTEST_SHADE, SPLIT (imported).

    ---- Outputs ----
    dict
        What _sets_aligner gives ('times_min', 'additions_min', 'breaks_min',
        'left_out', 'label', 'events', 'zero', ...), with 'lines': each {'label',
        'colour', 'values': np.ndarray (n_times,)}, before the stacking, named and
        coloured as the lines of waterfall_lines_lister.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See traces_aligner and traces_averager (MATHS.md section 10); the shades as in
    waterfall_lines_lister.

    ---- Helpers ----
    _sets_aligner
    _waterfall_roles_reader
    colour_shader
    plot_sets_lister
    traces_averager
    """

    # ---- 1 The traces of the group, lined up -----------------------------------------
    set_roles = _waterfall_roles_reader(setup, roles)
    sets = plot_sets_lister(setup, set_roles)
    found = _sets_aligner(sets, roles, experiments, answers)
    lines = []

    # ---- 2 A time series: the mean of the replicates of each time point --------------
    if set_roles[STACK_KEY] == SPLIT:
        for place, entry in enumerate(sets):
            rows = [row
                    for row, (owner, _) in enumerate(found['kept'])
                    if owner == place
                    ]
            if not rows:
                continue
            label = entry['labels'][STACK_KEY] or NO_TIME_POINT
            lines.append({'label': f'{label} (n = {len(rows)})',
                          'colour': entry['colour'],
                          'values': traces_averager(found['values'][rows])['mean'],
                          },
                         )
        return dict(found, lines=lines)

    # ---- 3 Otherwise each experiment, lighter down the stack -------------------------
    steps = max(len(found['kept']) - 1, 1)
    for row, (owner, name) in enumerate(found['kept']):
        lines.append({'label': name,
                      'colour': colour_shader(sets[owner]['base_colour'],
                                              LIGHTEST_SHADE * row / steps,
                                              ),
                      'values': found['values'][row],
                      },
                     )
    return dict(found, lines=lines)


# ---- PLOT TYPES ----------------------------------------------------------------------
# Loading this file adds each plot type to the page: what its form asks, how it is
# drawn and how its plots share their scales.
FORM_MAKERS['P1'] = standard_form_maker
PLOT_DRAWERS['P1'] = standard_plot_drawer
SCALE_SHARERS['P1'] = standard_scales_sharer
FORM_MAKERS['P2'] = difference_form_maker
PLOT_DRAWERS['P2'] = difference_plot_drawer
FORM_MAKERS['P3'] = waterfall_form_maker
PLOT_DRAWERS['P3'] = waterfall_plot_drawer
FORM_MAKERS['P7'] = trace_form_maker
PLOT_DRAWERS['P7'] = trace_plot_drawer
FORM_MAKERS['P8'] = mean_form_maker
PLOT_DRAWERS['P8'] = mean_plot_drawer
FORM_MAKERS['P9'] = bar_form_maker
PLOT_DRAWERS['P9'] = bar_plot_drawer
CAPTION_WRITERS['P9'] = bar_caption_writer
FORM_MAKERS['P10'] = before_after_form_maker
PLOT_DRAWERS['P10'] = before_after_plot_drawer
CAPTION_WRITERS['P10'] = before_after_caption_writer
FORM_MAKERS['P11'] = response_form_maker
PLOT_DRAWERS['P11'] = response_plot_drawer
CAPTION_WRITERS['P11'] = response_caption_writer
FORM_MAKERS['P12'] = time_points_form_maker
PLOT_DRAWERS['P12'] = time_points_plot_drawer
CAPTION_WRITERS['P12'] = time_points_caption_writer
