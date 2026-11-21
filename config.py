"""
Settings and defaults of Portimao: figure styles, journal sizes and colours.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import (figure_size_calculator,
                                        figure_style_builder,
                                        figure_style_checker,
                                        )
from utils_shared.helpers import haem_type_finder, name_simplifier


# ---- CONSTANTS -----------------------------------------------------------------------
# The standard settings: a dataset never opened before starts from them, and a dataset
# opened before from the settings kept in its own folder (utils_shared.dataset_settings).
# The standard fit is the file in fits/ used for the haems of the standard plot.
STANDARD_FIT = 'bswitch_no2_mycobl_b557.csv'
DEFAULT_ANSWERS = {'ignore_first_minutes': 5.0,  # left out of baselines and ranges
                   # the same at the end of the recording
                   'ignore_last_minutes': 0.0,
                   'decompose': True,
                   'fit_file': STANDARD_FIT,
                   'decomposition_dataset': 'Cyt',
                   'normalise_od': False,
                   'averaging': False,
                   'window_minutes': 2.0,
                   'gap_minutes': 0.5,
                   'final_gap_minutes': 0.5,
                   'plot_o2': True,
                   'plot_ocr': True,
                   # "raw", "od" or "percent"
                   'ocr_mode': 'od',
                   # event label rotation in degrees: 0 = horizontal, 90 = vertical
                   'event_label_angle': 45,
                   # the haems of the fit, when decomposed, in the figure of each file
                   'plot_haems': True,
                   'haems': [],
                   # "abs", "delta", "conc" or "percent"
                   'haem_mode': 'delta',
                   # divide the haem values (not "percent") by OD x volume x dilution
                   # when OD scaling is on
                   'haem_per_od': True,
                   # Figure sizes. Each figure has its own journal, width (columns) and
                   # height (fraction of a page).
                   # The *_size_mode answer is "default" (the journal question was
                   # answered None: Nature and the size below) or "custom".
                   # The standard figure: Nature, 1 column wide, 0.5 of a page tall.
                   'journal': 'nature',
                   'columns': 1,
                   'height': 0.5,
                   'size_mode': 'default',
                   'plot_comparison': False,
                   'comparison_journal': 'nature',
                   'comparison_columns': 1.5,
                   'comparison_height': 0.5,
                   'comparison_size_mode': 'default',
                   'plot_exemplar': False,
                   'ho_exemplar_run': 1,
                   'ex_journal': 'nature',
                   'ho_ex_columns': 2,
                   'ho_ex_height': 0.75,
                   'ex_watermark': True,
                   'ex_size_mode': 'default',
                   'export_full': False,
                   'export_spectra': False,
                   # special figures (see utils_custom): time response, and haem and OCR
                   # response
                   'plot_time_response': False,
                   'plot_haem_ocr': False,
                   'tr_groups': ['knockdown', 'control'],
                   'tr_window_minutes': 1.0,
                   'tr_gap_minutes': 0.5,
                   'tr_final_gap_minutes': 0.5,
                   'tr_examples': [],
                   'tr_decompositions': [],
                   'tr_skip_hours': [],
                   'tr_journal': 'nature',
                   'tr_columns': 2,
                   'tr_height': 1.0,
                   'tr_size_mode': 'default',
                   'ho_haem_mode': 'delta',
                   'ho_per_od': True,
                   'ho_metric': 'delta',
                   'ho_haems': [],
                   'ho_ocr_mode': 'od',
                   'ho_window_minutes': 2.0,
                   'ho_gap_minutes': 0.5,
                   'ho_final_gap_minutes': 0.5,
                   'ho_journal': 'nature',
                   'ho_pub_columns': 2,
                   'ho_pub_height': 0.75,
                   'ho_size_mode': 'default',
                   }
# the background fitted under the haems (names and words in
# utils_shared.spectral_decomposer.BACKGROUND_LABELS); one that can bend is needed for bL
# to fall when reduced, as the instrument's own trace does
HAEM_BACKGROUND = 'scatter_2'
# scatter terms the component finder takes out of the spectra; it does not follow
# HAEM_BACKGROUND yet
DEGREE_OF_SCATTER = 1
HAEM_FACTOR = 1_000_000
# points in a row whose median is a reference level: the 0 of delta A, the 0 % and the
# 100 % of the % scale (50 points are 25 s when a point is taken every 0.5 s)
REFERENCE_WINDOW_POINTS = 50
# least data the baseline average (before the first addition) must span
BASELINE_MINIMUM_SECONDS = 10
# an averaging window dragged across the plot is rounded to whole steps of this
DRAG_STEP_SECONDS = 5
# The window. Resolution of its plots, in dots per inch.
PREVIEW_DPI = 200
# files the window keeps read in memory and redraws after each answer: the one shown and
# the nearest ones beside it, so the arrows lead to a drawn file (any other is drawn when
# it is looked at); a big file takes several hundred MB
WINDOW_KEPT_FILES = 3
# time axis title of each file's plot in the window: while trimming, and afterwards for
# a file trimmed at its start (its 0 is then where the kept part starts); the saved
# figures use TIME_AXIS_LABEL
PREVIEW_TIME_TITLES = {'recording': 'Time in the recording (minutes)',
                       'trimmed': 'Time from the trimmed start (minutes)',
                       }
# spectral window (nm) and smoothing (nm) first offered by the component finder (PCA)
PCA_WINDOW_NM = (500.0, 630.0)
PCA_SMOOTHING_NM = 4.0
# volume (mL) the spun-down cells are resuspended in, as the OD questions say
OD_RESUSPENDED_ML = 5
# axis-label size. Tick labels, legends and event labels are 1 pt smaller and titles 1
# pt larger; panel letters follow the journal.
BASE_FONT_PT = 6
# all paddings and gaps: 1.0 = default, 1.2 = 20 % looser, 0.8 = 20 % tighter
SPACING = 1.0
# data lines; axes, reference and event lines, error bars and markers are scaled from it
LINE_WIDTH_PT = 0.75
# Plot source names (see utils_shared.schema): chosen in the terminal as a "kind" and,
# when OD scaling is on, "per OD".
HAEM_SOURCE_BY_MODE = {'conc': ('raw', 'od'),
                       'abs': ('abs', 'abs_od'),
                       'delta': ('delta_abs', 'delta_abs_od'),
                       'percent': ('percent', 'percent'),
                       }
OCR_SOURCES = ('raw', 'od', 'percent')
FALLBACK_WITHOUT_OD = {'od': 'raw', 'abs_od': 'abs', 'delta_abs_od': 'delta_abs'}
HAEM_COLOURS = {'cytc1': '#ff3636',
                'cytcc': '#ff3636',
                'cytbh': '#3131ff',
                'cytbl': '#0d0d87',
                'cyta605': '#00b050',
                'cytb557': '#00b0db',
                }
# Colours by haem type, green for a, blue for b and red for c: the colours of the usual
# haems, then darker and lighter shades. They colour the components the PCA finds, by
# the type their peaks look like (pca_fitter.component_classifier), and the haems of a
# fit file that have no colour of their own above, by the type their name gives
# (haem_colour_mapper). 'other' (peaks of more than one type, none in a known band, or
# a name of no known type) uses colours no haem type has.
HAEM_TYPE_COLOURS = {'a': ['#00b050', '#006b30', '#7fd8a8'],
                     'b': ['#3131ff', '#0d0d87', '#8f8fff'],
                     'c': ['#ff3636', '#a00000', '#ff9b9b'],
                     'other': ['#e69f00',
                               '#cc79a7',
                               '#7b3294',
                               '#8c510a',
                               '#d55e00',
                               '#7f7f7f',
                               ],
                     }
# What each journal asks for. Only the Nature numbers were checked against the journal's
# own figure guide (research-figure-guide.nature.com;
# its 170 mm height is the maximum when the legend sits under the figure, 247 mm is the
# full page). The PNAS widths are from the PNAS
# template; every other number (marked "check") came from secondary sources: confirm it
# in the journal's author instructions before submitting.
JOURNAL_SPECS = {'nature': {'widths_mm': {1: 89, 1.5: 120, 2: 183},
                            'page_height_mm': 170,
                            'max_height_mm': 170,
                            'font_min_pt': 5,
                            'font_max_pt': 7,
                            # 8 pt bold lowercase a, b, c
                            'panel_letter_pt': 8,
                            'panel_letter_case': 'lower',
                            'font_family': ['Arial', 'Helvetica'],
                            'dpi': 300,
                            },
                 # check: sources disagree on the widths
                 'science': {'widths_mm': {1: 55, 1.5: 120, 2: 175},
                             'page_height_mm': 230,
                             'max_height_mm': 230,
                             'font_min_pt': 5,
                             'font_max_pt': 8,
                             'panel_letter_pt': 8,
                             'panel_letter_case': 'upper',
                             'font_family': ['Arial', 'Helvetica'],
                             'dpi': 300,
                             },
                 # check: widths 85 / 114 / 174 mm are widely quoted; heights and fonts
                 # are not confirmed
                 'cell': {'widths_mm': {1: 85, 1.5: 114, 2: 174},
                          'page_height_mm': 225,
                          'max_height_mm': 225,
                          'font_min_pt': 6,
                          'font_max_pt': 8,
                          'panel_letter_pt': 8,
                          'panel_letter_case': 'upper',
                          'font_family': ['Arial', 'Helvetica'],
                          'dpi': 300,
                          },
                 # widths from the PNAS template; check height and fonts
                 'pnas': {'widths_mm': {1: 87, 1.5: 114, 2: 178},
                          'page_height_mm': 225,
                          'max_height_mm': 225,
                          'font_min_pt': 6,
                          'font_max_pt': 8,
                          'panel_letter_pt': 8,
                          'panel_letter_case': 'upper',
                          'font_family': ['Arial', 'Helvetica'],
                          'dpi': 300,
                          },
                 }


# ---- Config --------------------------------------------------------------------------
class Config:
    """
    ---- Summary ----
    Everything derived from the answers: figure style and sizes, matplotlib settings,
    and the settings of the individual plot.

    ---- Attributes ----
    answers : dict
        Terminal answers merged over DEFAULT_ANSWERS.
    SPEC : dict
        Journal specification (widths, fonts, dpi) of the chosen journal.
    STYLE : dict
        Figure style from figure_style_builder (fonts, unit and spacing in points).
    FONTS : dict
        Font sizes in points.
    UNIT : float
        Spacing unit in points.
    FIGURE_SIZE : Tuple[float, float]
        Figure width and height in inches.
    FIGURE_DPI : int
        Resolution of saved figures in dots per inch.
    STYLE_WARNINGS : List[str]
        Warnings about the figure style, printed by the caller.
    RC_PARAMS : dict
        matplotlib rcParams of the figure style.

    ---- Globals read ----
    BASE_FONT_PT, DEFAULT_ANSWERS, JOURNAL_SPECS, LINE_WIDTH_PT, SPACING.

    ---- Methods ----
    __init__
    percent_need_checker
    plot_config_builder
    source_chooser
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, answers: dict) -> None:
        """
        ---- Summary ----
        Method to build the figure style, matplotlib settings and sizes of one figure
        from the terminal answers.

        ---- Inputs ----
        answers : dict
            Terminal answers; missing keys are filled from DEFAULT_ANSWERS.

        ---- Globals read ----
        DEFAULT_ANSWERS, JOURNAL_SPECS, BASE_FONT_PT, SPACING, LINE_WIDTH_PT (module
        constants); make_style, check_style, figure_size_inches (imported).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the answers, SPEC, STYLE, FONTS, UNIT, FIGURE_SIZE, FIGURE_DPI,
        STYLE_WARNINGS and RC_PARAMS attributes on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        figure_size_calculator
        figure_style_builder
        figure_style_checker
        """

        # ---- 1 Store the answers -----------------------------------------------------
        self.answers = dict(DEFAULT_ANSWERS, **answers)
        a = self.answers

        # ---- 2 Build the figure style ------------------------------------------------
        self.SPEC = JOURNAL_SPECS[a['journal']]
        self.STYLE = figure_style_builder(self.SPEC,
                                          BASE_FONT_PT,
                                          SPACING,
                                          LINE_WIDTH_PT,
                                          )
        self.FONTS, self.UNIT = self.STYLE['fonts'], self.STYLE['unit']
        self.FIGURE_SIZE = figure_size_calculator(self.SPEC, a['columns'], a['height'])
        self.FIGURE_DPI = self.SPEC['dpi']
        self.STYLE_WARNINGS = figure_style_checker(a['journal'],
                                                   self.SPEC,
                                                   self.FONTS,
                                                   self.FIGURE_SIZE,
                                                   'individual figure: ',
                                                   )

        # ---- 3 Build the matplotlib settings -----------------------------------------
        style, fonts, spec = self.STYLE, self.FONTS, self.SPEC
        fallback_fonts = ['Liberation Sans', 'DejaVu Sans']
        self.RC_PARAMS = {'font.family': 'sans-serif',
                          # the first one installed is used
                          'font.sans-serif': spec['font_family'] + fallback_fonts,
                          'font.size': fonts['tick'],
                          'axes.labelsize': fonts['label'],
                          'axes.titlesize': fonts['title'],
                          'axes.titlepad': style['title_pad'],
                          'axes.labelpad': style['label_pad'],
                          'lines.linewidth': style['line_width'],
                          'axes.linewidth': style['axes_line_width'],
                          'xtick.major.width': style['axes_line_width'],
                          'ytick.major.width': style['axes_line_width'],
                          'xtick.major.size': style['tick_length'],
                          'ytick.major.size': style['tick_length'],
                          'xtick.major.pad': style['tick_pad'],
                          'ytick.major.pad': style['tick_pad'],
                          'legend.fontsize': fonts['tick'],
                          'legend.handlelength': 1.6,
                          'legend.borderpad': 0.3,
                          'legend.labelspacing': 0.25,
                          'legend.handletextpad': 0.5,
                          'legend.borderaxespad': 0.4,
                          'legend.edgecolor': '0.25',
                          'legend.fancybox': False,
                          'legend.framealpha': 0.9,
                          # keeps text as editable text in the SVG
                          'svg.fonttype': 'none',
                          'pdf.fonttype': 42,
                          }

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- percent_need_checker --------------------------------------------------------
    def percent_need_checker(self) -> Tuple[bool, bool]:
        """
        ---- Summary ----
        Method to say whether the percent-of-range versions of the OCR and haem data
        have to be calculated.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Tuple[bool, bool]
            (OCR percent needed, haem percent needed).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        a = self.answers
        return (a['plot_ocr'] and a['ocr_mode'] == 'percent',
                a['decompose'] and a['plot_haems'] and a['haem_mode'] == 'percent',
                )

    # ---- plot_config_builder ---------------------------------------------------------
    def plot_config_builder(self,
                            vo2_source: str,
                            haem_source: Optional[str],
                            ignore_first: Optional[float] = None,
                            ignore_last: Optional[float] = None,
                            ) -> dict:
        """
        ---- Summary ----
        Method to build the settings dictionary of one individual-experiment figure.

        ---- Inputs ----
        vo2_source : str
            OCR source plotted: "raw", "od" or "percent".
        haem_source : Optional[str]
            Haem source plotted, for example "delta_abs_od", or None for no haem panels.
        ignore_first : Optional[float]
            Minutes ignored at the start for the axis limits; None uses the answers.
        ignore_last : Optional[float]
            Minutes ignored at the end for the axis limits; None uses the answers.

        ---- Globals read ----
        haem_colours (module function); the style, font and size attributes of the
        instance.

        ---- Outputs ----
        dict
            Plot settings in the format used by plot_experiment.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        haem_colour_mapper
        """

        # ---- 1 Gather the settings ---------------------------------------------------
        a, style, fonts = self.answers, self.STYLE, self.FONTS
        haems = (list(a['haems'])
                 if (a['decompose'] and a['plot_haems'] and haem_source)
                 else []
                 )

        # ---- 2 Build the plot configuration ------------------------------------------
        # Output
        return {'SHOW_INDIVIDUAL_FIGURES': False,
                'SAVE_FIGURES': True,
                'FIGURE_SIZE': self.FIGURE_SIZE,
                'FIGURE_DPI': self.FIGURE_DPI,
                'TIGHT_BBOX': False,
                'FIT_MARGINS': True,
                'LAYOUT_PAD_PT': style['edge_pad'],
                'TITLE_GAP_PT': style['title_gap'],
                'TITLE_PAD_PT': style['title_pad'],
                'HIDE_TOUCHING_TICK_LABELS': True,
                'FIGURE_TITLE': '{experiment_name}',
                'TITLE_STYLE': 'watermark',
                'WATERMARK_FONT_SIZE': fonts['tick'],
                'WATERMARK_COLOUR': '0.35',
                'WATERMARK_ALPHA': 0.5,
                'TITLE_FONT_SIZE': fonts['title'],
                'LABEL_FONT_SIZE': fonts['label'],
                'SUBPLOT_HSPACE': 0.0,
                'PANEL_HEIGHT_RATIOS': {'oxygen': 2, 'vo2': 2, 'haem': 5},
                'EQUAL_PANEL_HEIGHTS': True,
                # Time axis
                'TIME_AXIS_LABEL': 'Time (minutes)',
                'TIME_AXIS_LABEL_PAD': style['label_pad'],
                'X_MIN': None,
                'X_MAX': None,
                'X_NUM_TICKS': None,
                'Y_SCALE_IGNORE_FIRST_MINUTES': (a['ignore_first_minutes']
                                                 if ignore_first is None
                                                 else ignore_first
                                                 ),
                'Y_SCALE_IGNORE_LAST_MINUTES': (a['ignore_last_minutes']
                                                if ignore_last is None
                                                else ignore_last
                                                ),
                'Y_LABEL_PAD': style['label_pad'],
                'ALIGN_Y_LABELS': True,
                'TICK_FONT_SIZE': fonts['tick'],
                'LINE_WIDTH': style['line_width'],
                'AXES_TOP_SPINE': False,
                'AXES_RIGHT_SPINE': False,
                # Events
                'PLOT_EVENTS': True,
                'EVENT_LINE_STYLE': '--',
                'EVENT_LINE_WIDTH': style['thin_line_width'],
                'EVENT_LINE_COLOUR': '0.35',
                'EVENT_LINE_ALPHA': 0.8,
                'EVENT_LABELS': True,
                'EVENT_LABELS_ON_TOP': True,
                'EVENT_LABEL_ROTATION': a['event_label_angle'],
                'EVENT_LABEL_FONTSIZE': fonts['tick'],
                'EVENT_LABEL_ANCHOR': 'start',
                'EVENT_LABEL_OFFSET': style['event_label_offset'],
                # Averaging windows
                'PLOT_AVERAGING_WINDOWS': a['averaging'],
                'AVERAGING_WINDOW_COLOUR': '#4C9BE8',
                'AVERAGING_WINDOW_ALPHA': 0.18,
                'AVERAGING_WINDOW_EDGE_COLOUR': '#2878B5',
                'AVERAGING_WINDOW_EDGE_LINE_WIDTH': style['thin_line_width'],
                'AVERAGING_WINDOW_LABEL_FORMAT': '',
                'AVERAGING_WINDOW_LABEL_FONT_SIZE': fonts['tick'],
                # Oxygen panel
                'PLOT_SET_AND_MEASURED_O2': a['plot_o2'],
                'O2_PANEL_TITLE': 'Oxygen concentration',
                'O2_AXIS_LABEL': '[O$_2$]\n(µM)',
                'SET_O2_LABEL': 'Set [O$_2$]',
                'MEASURED_O2_LABEL': 'Measured [O$_2$]',
                'SET_O2_COLOUR': None,
                'MEASURED_O2_COLOUR': None,
                'SET_O2_LINE_STYLE': '-',
                'MEASURED_O2_LINE_STYLE': '--',
                'O2_Y_MIN': None,
                'O2_Y_MAX': None,
                'O2_Y_NUM_TICKS': None,
                # VO2 panel
                'PLOT_VO2': a['plot_ocr'],
                'VO2_PANEL_TITLE': 'Oxygen consumption',
                'VO2_LABEL': 'VO2',
                'VO2_COLOUR': None,
                'VO2_PLOT_VALUES': vo2_source,
                'VO2_AXIS_LABELS': {'raw': 'OCR (µM\nmin$^{-1}$)',
                                    'od': 'OCR (µM\nmin$^{-1}$\nOD$^{-1}$)',
                                    'percent': 'OCR (% of range)',
                                    },
                'VO2_Y_MIN': 0,
                'VO2_Y_MAX': None,
                'VO2_Y_NUM_TICKS': None,
                'VO2_Y_SPIKE_WINDOW_FRACTION': 0.02,
                'VO2_Y_HEADROOM': 0.05,
                # Haem panels (one per selected haem)
                'HAEM_PLOT_VALUES': haem_source,
                'HAEM_AXIS_LABELS': {'raw': 'Haem concentration',
                                     'od': 'Haem concentration (/OD)',
                                     'percent': 'Oxidised haem (%)',
                                     'abs': 'Haem absorbance (mOD)',
                                     'abs_od': 'Haem absorbance (mOD OD$^{-1}$)',
                                     'delta_abs': 'ΔA (mOD)',
                                     'delta_abs_od': 'ΔA (mOD OD$^{-1}$)',
                                     },
                'HAEM_Y_MIN': None,
                'HAEM_Y_MAX': None,
                'HAEM_Y_NUM_TICKS': None,
                'HAEM_SPAN_LABEL_PAD': style['label_pad'],
                'HAEM_PANELS': [{'label': '', 'haems': [name]} for name in haems],
                'HAEM_COLOURS': haem_colour_mapper(haems),
                # Legend
                'SHOW_LEGENDS': {'oxygen': True, 'vo2': False, 'haem': True},
                'LEGEND_FONT_SIZE': fonts['tick'],
                'LEGEND_LOCATION': 'upper right',
                'LEGEND_COLUMNS': 1,
                'LEGEND_FRAME': True,
                'LEGEND_FRAME_LINE_WIDTH': style['thin_line_width'],
                'HAEM_LEGEND_TEXT_ONLY': True,
                }

    # ---- source_chooser --------------------------------------------------------------
    def source_chooser(self, od_available: bool = True) -> Tuple[str, Optional[str]]:
        """
        ---- Summary ----
        Method to choose the OCR source and haem source used for the plot and the event
        averages.

        ---- Inputs ----
        od_available : bool
            True when the experiment has OD, volume and dilution factor.

        ---- Globals read ----
        FALLBACK_WITHOUT_OD, HAEM_SOURCE_BY_MODE (module constants).

        ---- Outputs ----
        Tuple[str, Optional[str]]
            (OCR source, haem source), for example ("od", "delta_abs_od"). The haem
            source is None when nothing is decomposed; OD sources fall back to raw ones
            without OD.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        # ---- 1 Choose the VO2 source -------------------------------------------------
        a = self.answers
        use_od = a['normalise_od'] and od_available
        vo2 = a['ocr_mode'] if a['plot_ocr'] else ('od' if use_od else 'raw')
        if vo2 == 'od' and not use_od:
            vo2 = FALLBACK_WITHOUT_OD['od']

        # ---- 2 Choose the haem source ------------------------------------------------
        haem = None
        if a['decompose']:
            haem_mode = a['haem_mode'] if a['plot_haems'] else 'delta'
            per_od_pair = HAEM_SOURCE_BY_MODE[haem_mode]
            haem = (per_od_pair[1]
                    if (use_od and a.get('haem_per_od', True))
                    else per_od_pair[0]
                    )
        return vo2, haem


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- haem_colour_mapper --------------------------------------------------------------
def haem_colour_mapper(names: List[str]) -> Dict[str, str]:
    """
    ---- Summary ----
    Main function to give each haem a plot colour of its type: shades of green for the
    a haems, blue for the b and red for the c. A usual haem keeps its own colour
    unless a haem before it in the list took that colour; any other haem takes the
    first shade of its type no haem of the list has yet.

    ---- Inputs ----
    names : List[str]
        Haem names as written in the fit file, plain or in figure form.

    ---- Globals read ----
    HAEM_COLOURS, HAEM_TYPE_COLOURS (module constants).

    ---- Outputs ----
    Dict[str, str]
        {haem name: hex colour}. A name of no known type takes a colour no haem type
        has. Colours repeat only when a type has more haems than shades.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    haem_type_finder
    name_simplifier
    """

    # ---- 1 The usual haems keep their own colour -------------------------------------
    colours: Dict[str, str] = {}
    for name in names:
        own = HAEM_COLOURS.get(name_simplifier(name))
        if own and own not in colours.values():
            colours[name] = own

    # ---- 2 Every other haem takes a free shade of its type ---------------------------
    for name in names:
        if name in colours:
            continue
        kind = haem_type_finder(name)
        shades = HAEM_TYPE_COLOURS[kind]
        free = [shade for shade in shades if shade not in colours.values()]
        same_type = [other for other in colours if haem_type_finder(other) == kind]
        colours[name] = free[0] if free else shades[len(same_type) % len(shades)]
    return {name: colours[name] for name in names}


# ---- pca_colour_mapper ---------------------------------------------------------------
def pca_colour_mapper(types: List[str]) -> List[str]:
    """
    ---- Summary ----
    Main function to give each PCA component a plot colour from the haem type its peaks
    look like: green for a-like, blue for b-like, red for c-like, with a darker then a
    lighter shade for each further component of the same type, and a colour no haem
    type has for mixed or unknown components.

    ---- Inputs ----
    types : List[str]
        Type of each component: 'a', 'b', 'c', 'mixed' or 'unknown'
        (pca_fitter.component_classifier).

    ---- Globals read ----
    HAEM_TYPE_COLOURS (module constant).

    ---- Outputs ----
    List[str]
        Hex colour of each component, in the same order. Colours repeat only when a
        type has more components than shades.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    used = {key: 0 for key in HAEM_TYPE_COLOURS}
    colours = []
    for kind in types:
        key = kind if kind in ('a', 'b', 'c') else 'other'
        shades = HAEM_TYPE_COLOURS[key]
        colours.append(shades[used[key] % len(shades)])
        used[key] += 1
    return colours
