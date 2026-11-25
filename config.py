"""
Settings and defaults of Portimao: figure styles, journal sizes and colours.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import (figure_size_calculator,
                                        font_family_lister,
                                        figure_style_builder,
                                        figure_style_checker,
                                        )
from utils_shared.helpers import haem_type_finder, name_simplifier
from utils_shared.journal_files import (journal_specs_loader,
                                        journals_folder_lister,
                                        STANDARD_JOURNAL,
                                        )
from utils_shared.user_places import user_places_finder


# ---- CONSTANTS -----------------------------------------------------------------------
# The standard settings: a dataset never opened before starts from them, and a dataset
# opened before from the settings kept in its own folder (utils_shared.dataset_settings).
# The standard fit is the preset (fits/presets/) used for the haems of the standard plot.
STANDARD_FIT = 'bswitch_no2_mycobl_b557.csv'
# The volume of the instrument's chamber (mL), always the same: the concentration of an
# addition is worked out from its stock and the volume added into it.
CHAMBER_VOLUME_ML = 5.0
# the results folder offered, inside the data folder, for a dataset never run before
RESULTS_FOLDER_NAME = 'results'
DEFAULT_ANSWERS = {'ignore_first_minutes': 5.0,  # left out of baselines and ranges
                   # the same at the end of the recording
                   'ignore_last_minutes': 0.0,
                   'decompose': True,
                   'fit_file': STANDARD_FIT,
                   # the library haems ticked under Build a fit in the strip, used when
                   # fit_file is "Your own haems" (spectral_decomposer.OWN_HAEMS_NAME)
                   'haem_files': [],
                   # the background fitted under the haems (names and words in
                   # utils_shared.spectral_decomposer.BACKGROUND_LABELS): the lab's own
                   # chamber scripts' background, which can bend, as bL needs to fall
                   # when reduced as the instrument's own trace does
                   'haem_background': 'rowan_scatter',
                   'decomposition_dataset': 'Cyt',
                   'normalise_od': False,
                   # the window step starts with windows, which the user can untick
                   # 'averaging' is True when either kind of window is ticked: the
                   # settled windows (ending gap_minutes before the next addition) or
                   # the quick windows (starting delay_minutes after each addition)
                   'averaging': True,
                   'settled_windows': True,
                   'window_minutes': 2.0,
                   'gap_minutes': 0.5,
                   'final_gap_minutes': 0.5,
                   'quick_windows': False,
                   'quick_minutes': 0.5,
                   'delay_minutes': 10.0 / 60.0,
                   # the windows set on their own and the files whose windows were
                   # fixed by hand (each_window and file_windows, DATA_FORMAT.md)
                   'each_window': {},
                   'file_windows': {},
                   # the kind of window ("settled" or "quick") the 2x2 grid, the time
                   # response and the haem and OCR response average over, asked only
                   # when both kinds are ticked
                   'ex_window_kind': 'settled',
                   'tr_window_kind': 'settled',
                   'ho_window_kind': 'settled',
                   'plot_o2': True,
                   'plot_ocr': True,
                   # "raw", "od" or "percent"
                   'ocr_mode': 'od',
                   # event label rotation in degrees: 0 = horizontal, 90 = vertical
                   'event_label_angle': 45,
                   # what the event labels show (Labels as in the strip): "chamber",
                   # the concentration in the chamber after the addition ("400 µM
                   # KCN"), or "added", the volume and the stock added ("10 µL of
                   # 200 mM KCN")
                   'label_mode': 'chamber',
                   # the haems of the fit, when decomposed, in the figure of each file
                   'plot_haems': True,
                   'haems': [],
                   # how a decomposition kept to compare with is shown: "side", a plot
                   # of its own on the left of the plot in use, or "overlaid", dashed
                   # over it
                   'compare_layout': 'side',
                   # the plot of each file shows its difference spectrum (reduced minus
                   # oxidised, utils_shared.difference_spectra) in place of the standard
                   # plot, for a file with both regions; the switch under the boxes
                   'difference_spectra': False,
                   # the panels of the plot of each file in the order the user moved
                   # them to, top first, by their keys ("oxygen", "vo2", "haem:Cyt bH",
                   # "delta_psi"); empty for the standard order (oxygen, OCR, the haems
                   # a then b then c, delta psi)
                   'panel_order': [],
                   # "abs", "delta" or "percent" (% oxidised, for the files with an
                   # oxidised and a reduced region); no haem amounts, as only cells are
                   # measured and an amount depends on the size of its shape
                   'haem_mode': 'delta',
                   # divide the haem values (not "percent") by OD x volume x dilution
                   # when OD scaling is on
                   'haem_per_od': True,
                   # Delta psi, the membrane potential, from how reduced bH and bL are
                   # (utils_shared.delta_psi, MATHS.md): worked out for the files with
                   # both regions only when switched on. Its numbers start from those of
                   # Kim, Ripple and Springett (Biophys J 2012, 102:1194), measured on
                   # mitochondria, and are kept with the dataset so they can be changed:
                   # the temperature of the sample, each haem's midpoint potential with
                   # the other haem oxidised (first) and reduced (second), the share of
                   # the membrane potential that lies between the two haems, and the
                   # limits: delta psi is given only where bH and bL are both between
                   # these % reduced, as outside them a small error in the % gives a
                   # large error in delta psi (the method's own rule)
                   'delta_psi': False,
                   'temperature_c': 37.0,
                   'psi_bH_first_mV': 40.0,
                   'psi_bL_first_mV': -20.0,
                   'psi_bH_second_mV': -30.0,
                   'psi_bL_second_mV': -90.0,
                   'psi_share': 0.5,
                   'psi_reduced_lowest_percent': 10.0,
                   'psi_reduced_highest_percent': 90.0,
                   # Figure sizes. Each figure has its own journal, width (columns) and
                   # height (fraction of a page).
                   # The *_size_mode answer is "default" (the journal question was
                   # answered None: Nature and the size below) or "custom".
                   # The standard figure: Nature, 1 column wide, 0.5 of a page tall.
                   'journal': STANDARD_JOURNAL,
                   'columns': 1,
                   'height': 0.5,
                   'size_mode': 'default',
                   'plot_comparison': False,
                   'comparison_journal': STANDARD_JOURNAL,
                   'comparison_columns': 1.5,
                   'comparison_height': 0.5,
                   'comparison_size_mode': 'default',
                   'plot_exemplar': False,
                   'ho_exemplar_run': 1,
                   'ex_journal': STANDARD_JOURNAL,
                   'ho_ex_columns': 2,
                   'ho_ex_height': 0.75,
                   'ex_watermark': True,
                   'ex_size_mode': 'default',
                   'export_spectra': False,
                   # special figures (see utils_custom): time response, and haem and OCR
                   # response
                   'plot_time_response': False,
                   'plot_haem_ocr': False,
                   'tr_groups': ['knockdown', 'control'],
                   'tr_examples': [],
                   'tr_decompositions': [],
                   'tr_skip_hours': [],
                   'tr_journal': STANDARD_JOURNAL,
                   'tr_columns': 2,
                   'tr_height': 1.0,
                   'tr_size_mode': 'default',
                   'ho_haem_mode': 'delta',
                   'ho_per_od': True,
                   'ho_metric': 'delta',
                   'ho_haems': [],
                   'ho_ocr_mode': 'od',
                   'ho_journal': STANDARD_JOURNAL,
                   'ho_pub_columns': 2,
                   'ho_pub_height': 0.75,
                   'ho_size_mode': 'default',
                   }
# scatter terms the component finder takes out of the spectra; it does not follow the
# 'haem_background' answer yet
DEGREE_OF_SCATTER = 1
HAEM_FACTOR = 1_000_000
# points whose median is a reference level (50 points are 25 s when a point is taken
# every 0.5 s). The 0 of delta D is where each haem starts: its first points after the
# ignored start. The 0 % and the 100 % of the OCR's % of the range are its lowest and
# its highest points in a row, wherever they are in the run.
REFERENCE_WINDOW_POINTS = 50
# least number of spectra an oxidised or a reduced region must hold for a haem's level
# in it (its median there); a shorter region counts as not chosen (10 spectra are 5 s)
REGION_MINIMUM_POINTS = 10
# the answers that hold the lowest and the highest % reduced at which delta psi is
# still given
DELTA_PSI_LIMIT_ANSWERS = ('psi_reduced_lowest_percent', 'psi_reduced_highest_percent')
# the answer that holds each midpoint potential of the delta psi maths
# (utils_shared.delta_psi.MIDPOINT_KEYS)
DELTA_PSI_MIDPOINT_ANSWERS = {'bH_first': 'psi_bH_first_mV',
                              'bL_first': 'psi_bL_first_mV',
                              'bH_second': 'psi_bH_second_mV',
                              'bL_second': 'psi_bL_second_mV',
                              }
# least data the baseline average (before the first addition) must span
BASELINE_MINIMUM_SECONDS = 10
# an edge of an averaging window dragged on the plot moves in whole steps of this
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
# bytes a spectra csv file takes per value of each kind, for the sizes the export
# question gives: measured on 200 spectra of each spectrometer of
# data_instrument_check/example.paf (18.9, 8.0 and 20.9), so about 1.2 GB for that 100 MB
# file
SPECTRA_CSV_BYTES = {'transmission': 19, 'intensity': 8, 'attenuation': 21}
# bytes one data point takes in the workbook of an imported file (its Measured O2, Set
# O2 and OCR sheets together), for the sizes the export question gives: measured on
# data_instrument_check/example.paf (49.9), so about 0.3 MB for that 100 MB file
WORKBOOK_POINT_BYTES = 50
# axis-label size. Tick labels, legends and event labels are 1 pt smaller and titles 1
# pt larger; panel letters follow the journal. A journal that takes no text this small
# or this large moves it, and the paddings with it (figure_style_builder).
BASE_FONT_PT = 6
# all paddings and gaps: 1.0 = default, 1.2 = 20 % looser, 0.8 = 20 % tighter
SPACING = 1.0
# data lines; axes, reference and event lines, error bars and markers are scaled from it
LINE_WIDTH_PT = 0.75
# Plot source names (see utils_shared.schema): chosen in the terminal as a "kind" and,
# when OD scaling is on, "per OD".
HAEM_SOURCE_BY_MODE = {'abs': ('abs', 'abs_od'),
                       'delta': ('delta_abs', 'delta_abs_od'),
                       'percent': ('percent', 'percent'),
                       }
FALLBACK_WITHOUT_OD = {'od': 'raw', 'abs_od': 'abs', 'delta_abs_od': 'delta_abs'}
# Colours of the set oxygen, the measured oxygen and the OCR lines on the plot of one
# experiment. The set and measured oxygen share a panel, so they also differ in line
# style (solid and dashed) and stay apart in grey scale.
TRACE_COLOURS = {'set_O2': '#1f77b4', 'measured_O2': '#ff7f0e', 'OCR': '#1f77b4'}
# The baseline window (the averaging window before the first addition): the colour of
# its shading and of its edge and name, gold to stand apart from the blue settled and
# the green quick windows
BASELINE_WINDOW_COLOURS = ('#E6B800', '#A88600')
# An averaging window that could not be worked out, shown in the previews only
SKIPPED_WINDOW_COLOUR = '#d62728'
# Usual reduced-minus-oxidised peaks (nm) of each haem type, drawn as guide lines on the
# figure of the components found
HAEM_USUAL_PEAKS_NM = {'a': (604.0, 444.0),
                       'b': (563.0, 430.0),
                       'c': (551.0, 418.0),
                       }
# Greys and line widths (points) of the two component figures: the components found,
# and the spectra described best and worst
COMPONENT_FIGURE_STYLE = {'measured_colour': '0.65',
                          'measured_line_width': 2.6,
                          'part_line_width': 1.2,
                          'background_colour': '0.55',
                          'fitted_colour': 'black',
                          'fitted_line_width': 1.0,
                          'residual_colour': '0.3',
                          'residual_line_width': 1.0,
                          'zero_colour': '0.75',
                          'zero_line_width': 0.5,
                          'peak_line_width': 0.7,
                          'peak_alpha': 0.45,
                          'component_line_width': 1.5,
                          }
# White space between the two plots of the side-by-side figure, beyond what their labels
# need (in multiples of the padding at the figure's edge)
COMPARISON_GAP_PADS = 8
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
# What each journal asks of a figure, read from the journals folder, one .json file
# per journal (utils_shared/journal_files.py, DATA_FORMAT.md): its widths, its tallest
# figure ('page_height_mm', of which the height of a figure is chosen as a part), its
# text sizes, panel letters, fonts, thinnest and thickest line, the sharpness of saved
# pictures and its printed page. Each file says where its numbers were read and what
# was confirmed by hand. JOURNAL_PROBLEMS holds one sentence for each file left out,
# shown when the program starts.
JOURNAL_SPECS, JOURNAL_PROBLEMS = journal_specs_loader(
    journals_folder_lister(user_places_finder()),
    )


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
    haem_view_lister
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
        font_family_lister
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
        self.STYLE_WARNINGS = figure_style_checker(self.SPEC, self.FONTS)

        # ---- 3 Build the matplotlib settings -----------------------------------------
        style, fonts, spec = self.STYLE, self.FONTS, self.SPEC
        fallback_fonts = ['Liberation Sans', 'DejaVu Sans']
        # The fonts are named one by one, those on this computer only: text is drawn
        # in the first, and a character it lacks (Arial has no subscripts and no
        # raised minus) in the next that has it. Under the one name 'sans-serif' such
        # a character is drawn as an empty box.
        self.RC_PARAMS = {'font.family': font_family_lister(spec['font_family']
                                                            + fallback_fonts,
                                                            ),
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

    # ---- haem_view_lister ------------------------------------------------------------
    def haem_view_lister(self, od_available: bool = True) -> Dict[str, str]:
        """
        ---- Summary ----
        Method to list every way the haems can be shown with the source of each, so the
        averages cover every view and not only the one on the plot.

        ---- Inputs ----
        od_available : bool
            True when the experiment has OD, volume and dilution factor.

        ---- Globals read ----
        HAEM_SOURCE_BY_MODE (module constant).

        ---- Outputs ----
        Dict[str, str]
            {view: haem source} in the order of HAEM_SOURCE_BY_MODE, for example
            {'abs': 'abs_od', 'delta': 'delta_abs_od', 'percent': 'percent'}; per OD
            exactly when source_chooser gives the plot a per OD source. Empty when
            nothing is decomposed.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        a = self.answers
        if not a['decompose']:
            return {}
        is_per_od = a['normalise_od'] and od_available and a.get('haem_per_od', True)
        return {view: pair[1] if is_per_od else pair[0]
                for view, pair in HAEM_SOURCE_BY_MODE.items()
                }

    # ---- percent_need_checker --------------------------------------------------------
    def percent_need_checker(self) -> bool:
        """
        ---- Summary ----
        Method to say whether the percent-of-range version of the OCR has to be
        calculated. The % oxidised of the haems needs no asking: every file with an
        oxidised and a reduced region has it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            True when the OCR is plotted as a % of its range.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        a = self.answers
        return bool(a['plot_ocr'] and a['ocr_mode'] == 'percent')

    # ---- plot_config_builder ---------------------------------------------------------
    def plot_config_builder(self,
                            vo2_source: str,
                            haem_source: Optional[str],
                            ignore_first: Optional[float] = None,
                            ignore_last: Optional[float] = None,
                            delta_psi: bool = False,
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
        delta_psi : bool
            True to draw a Δψ panel under the haems, for a file that has Δψ; the
            figures of several files leave it out.

        ---- Globals read ----
        SKIPPED_WINDOW_COLOUR, TRACE_COLOURS (module constants); the style, font and
        size attributes of the instance.

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
        return {'SAVE_FIGURES': True,
                'FIGURE_SIZE': self.FIGURE_SIZE,
                'FIGURE_DPI': self.FIGURE_DPI,
                'LAYOUT_PAD_PT': style['edge_pad'],
                'HIDE_TOUCHING_TICK_LABELS': True,
                'FIGURE_TITLE': '{experiment_name}',
                'WATERMARK_FONT_SIZE': fonts['tick'],
                'WATERMARK_COLOUR': '0.35',
                'WATERMARK_ALPHA': 0.5,
                'LABEL_FONT_SIZE': fonts['label'],
                'SUBPLOT_HSPACE': 0.0,
                'PANEL_HEIGHT_RATIOS': {'oxygen': 2,
                                        'vo2': 2,
                                        'haem': 5,
                                        'delta_psi': 2,
                                        },
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
                # the thinnest and thickest line the journal takes, for every line of
                # the figure (figure_canvas_fitter)
                'LINE_LIMITS_PT': style['line_limits'],
                'EVENT_LINE_COLOUR': '0.35',
                'EVENT_LINE_ALPHA': 0.8,
                'EVENT_LABELS': True,
                'EVENT_LABELS_ON_TOP': True,
                'EVENT_LABEL_ROTATION': a['event_label_angle'],
                # "chamber" or "added" (utils_shared.event_concentrations.LABEL_MODES)
                'EVENT_LABEL_MODE': a['label_mode'],
                'EVENT_LABEL_FONTSIZE': fonts['tick'],
                'EVENT_LABEL_ANCHOR': 'start',
                'EVENT_LABEL_OFFSET': style['event_label_offset'],
                # Averaging windows
                'PLOT_AVERAGING_WINDOWS': a['averaging'],
                'AVERAGING_WINDOW_COLOUR': '#4C9BE8',
                'AVERAGING_WINDOW_ALPHA': 0.18,
                'AVERAGING_WINDOW_EDGE_COLOUR': '#2878B5',
                # the quick windows (starting after each addition) are green
                'QUICK_WINDOW_COLOUR': '#5DBB63',
                'QUICK_WINDOW_EDGE_COLOUR': '#2E8B3D',
                # the baseline (the window before the first addition) is orange, with
                # its name above it
                'BASELINE_WINDOW_COLOUR': BASELINE_WINDOW_COLOURS[0],
                'BASELINE_WINDOW_EDGE_COLOUR': BASELINE_WINDOW_COLOURS[1],
                'BASELINE_WINDOW_LABEL': 'Baseline',
                'BASELINE_WINDOW_LABEL_FONTSIZE': fonts['tick'],
                'AVERAGING_WINDOW_EDGE_LINE_WIDTH': style['thin_line_width'],
                'SKIPPED_WINDOW_COLOUR': SKIPPED_WINDOW_COLOUR,
                # Oxygen panel
                'PLOT_SET_AND_MEASURED_O2': a['plot_o2'],
                'O2_AXIS_LABEL': '[O$_2$]\n(µM)',
                'SET_O2_LABEL': 'Set [O$_2$]',
                'MEASURED_O2_LABEL': 'Measured [O$_2$]',
                'SET_O2_COLOUR': TRACE_COLOURS['set_O2'],
                'MEASURED_O2_COLOUR': TRACE_COLOURS['measured_O2'],
                'SET_O2_LINE_STYLE': '-',
                'MEASURED_O2_LINE_STYLE': '--',
                'O2_Y_MIN': None,
                'O2_Y_MAX': None,
                'O2_Y_NUM_TICKS': None,
                # OCR panel
                'PLOT_VO2': a['plot_ocr'],
                'VO2_LABEL': 'OCR',
                'VO2_COLOUR': TRACE_COLOURS['OCR'],
                'VO2_PLOT_VALUES': vo2_source,
                'VO2_AXIS_LABELS': {'raw': 'OCR (µM\nmin$^{-1}$)',
                                    'od': 'OCR (µM\nmin$^{-1}$\nOD$^{-1}$)',
                                    'percent': 'OCR (% of range)',
                                    'baseline': 'OCR (% of\nbaseline)',
                                    },
                'VO2_Y_MIN': 0,
                'VO2_Y_MAX': None,
                'VO2_Y_NUM_TICKS': None,
                'VO2_Y_SPIKE_WINDOW_FRACTION': 0.02,
                'VO2_Y_HEADROOM': 0.05,
                # Haem panels (one per selected haem)
                'HAEM_PLOT_VALUES': haem_source,
                'HAEM_AXIS_LABELS': {'percent': 'Oxidised haem (%)',
                                     'abs': 'Haem absorbance (mOD)',
                                     'abs_od': 'Haem absorbance (mOD OD$^{-1}$)',
                                     'delta_abs': 'ΔD (mOD)',
                                     'delta_abs_od': 'ΔD (mOD OD$^{-1}$)',
                                     },
                'HAEM_Y_MIN': None,
                'HAEM_Y_MAX': None,
                'HAEM_Y_NUM_TICKS': None,
                'HAEM_SPAN_LABEL_PAD': style['label_pad'],
                'HAEM_PANELS': [{'label': '', 'haems': [name]} for name in haems],
                'HAEM_COLOURS': haem_colour_mapper(haems),
                # The panels in the order the user gave them (empty: the standard one)
                'PANEL_ORDER': list(a.get('panel_order') or []),
                # Delta psi panel (the lowest in the standard order, only for a file
                # that has delta psi)
                'PLOT_DELTA_PSI': bool(delta_psi),
                'DELTA_PSI_AXIS_LABEL': 'Δψ (mV)',
                'DELTA_PSI_COLOUR': '0.15',
                # Legend
                'SHOW_LEGENDS': {'oxygen': True,
                                 'vo2': False,
                                 'haem': True,
                                 'delta_psi': False,
                                 },
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
            without OD. The OCR source 'baseline' (% of baseline) is what was asked
            for: the processing gives a file without a baseline its usual OCR.

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
