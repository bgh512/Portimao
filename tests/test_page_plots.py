"""
Tests of the plot types of a dataset figure on made-up experiments, drawn off screen: the form of the Standard experiment, its panels, its views, its ticks, its sentences and the scales its plots share; the form, the lines and the sentences of the Difference spectrum; the form, the lines, the stacking and the sentence of the Waterfall, also of traces; the forms, the lines, the bands and the sentences of the Single trace and the Mean trace, worked out by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
import numpy as np
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.transforms import Bbox

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.delta_psi import DELTA_PSI_COLUMN
from utils_shared.figure_page import (figure_page_drawer,
                                      FigurePage,
                                      PagePlot,
                                      plot_placer,
                                      )
from utils_shared.journal_files import STANDARD_SPEC
from utils_shared.figure_layout import BACKDROP_MARK, font_family_lister
from utils_shared.page_data import experiment_role_maker, form_fields_lister
from utils_shared.page_plots import (mean_lines_lister,
                                     NO_DIFFERENCE,
                                     NO_MEAN,
                                     NO_PANEL,
                                     NO_TRACE,
                                     NO_WATERFALL,
                                     NOT_READ,
                                     NOT_THERE,
                                     traces_left_out_lister,
                                     waterfall_left_out_lister,
                                     waterfall_lines_lister,
                                     waterfall_traces_lister,
                                     )
from utils_shared.schema import TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
HAEMS = ['Cyt $b_H$', 'Cyt cc']
B_KEY, C_KEY = 'haem:Cyt $b_H$', 'haem:Cyt cc'
NO_SUCH_ROLE = 'Group 1: 9, Group 2: 0, time point: 0, replicate: 1'
# where each haem of each made-up experiment starts and ends, in a straight line from
# 0 to 30 min: {experiment: {table: (bH, cc)}}
HAEM_ENDS = {'c1': {'haem_delta_abs': ((0.0, 2.0), (0.0, 1.0)),
                    'haem_abs': ((10.0, 12.0), (5.0, 6.0)),
                    'haem_percent': ((0.0, 50.0), (0.0, 100.0)),
                    },
             'k1': {'haem_delta_abs': ((0.0, -4.0), (0.0, 1.0)),
                    'haem_abs': ((10.0, 6.0), (5.0, 6.0)),
                    'haem_percent': ((0.0, 100.0), (0.0, 100.0)),
                    },
             }
# the made-up time series of the spectrum plots: the height of the peak of bH (at 560
# nm) and of cc (at 550 nm) in the difference spectrum of each experiment (mOD), and
# the band of each haem (nm)
PEAKS_MOD = {'a1': (4.0, 1.0), 'a2': (6.0, 3.0), 'a3': (2.0, 8.0), 'k1': (1.0, 1.0)}
BANDS = {'Cyt $b_H$': (557.5, 562.5), 'Cyt cc': (547.5, 552.5)}
BLUE = '#0072b2'
# the made-up time series of the plots over time: the OCR of each experiment before
# its first addition (µM min⁻¹; half of it from that addition on), the times of its
# additions and its last time (min)
OCR_RUNS = {'a1': (4.0, [10.0, 16.0], 20.0),
            'a2': (6.0, [12.0, 17.0], 25.0),
            'a3': (2.0, [10.0, 15.0], 20.0),
            'a4': (8.0, [10.0], 20.0),
            'k1': (10.0, [10.0, 15.0], 20.0),
            }


# ---- MAKERS --------------------------------------------------------------------------


# ---- _answers_maker ------------------------------------------------------------------
def _answers_maker(**changed: object) -> dict:
    """
    ---- Summary ----
    Helper function to make the answers of a made-up run: two haems worked out and
    shown, Δψ worked out, nothing left out of the y ranges at the start or the end.

    ---- Inputs ----
    **changed : object
        Answers that differ (decompose=False).

    ---- Globals read ----
    HAEMS.

    ---- Outputs ----
    dict
        The answers.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   plot_haems=True,
                   haems=list(HAEMS),
                   delta_psi=True,
                   ignore_first_minutes=0.0,
                   ignore_last_minutes=0.0,
                   )
    answers.update(changed)
    return answers


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(name: str) -> dict:
    """
    ---- Summary ----
    Helper function to make the slim copy of a made-up experiment of 0 to 30 min: set
    oxygen at 60 µM, measured oxygen falling from 50 µM (to 40 for c1, to 20 for k1),
    an OCR rising from 0 (to 3 for c1, to 6 for k1), two haems in ΔD, absorbance and
    % oxidised (HAEM_ENDS), one addition at 10 min, a baseline region from 2 to 8 min
    and a settled region from 20 to 28 min; c1 also has Δψ, from 100 to 130 mV.

    ---- Inputs ----
    name : str
        'c1' or 'k1'.

    ---- Globals read ----
    HAEM_ENDS, HAEMS; DELTA_PSI_COLUMN, TIME_COLUMN (imported).

    ---- Outputs ----
    dict
        The slim copy (page_experiment, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Each trace is a straight line: value = start + (end - start) x time / 30.

    ---- Helpers ----
    None.
    """

    times = np.arange(0.0, 31.0)
    share = times / 30.0
    is_control = name == 'c1'
    experiment = {'experiment_name': name,
                  'CsO2': pd.DataFrame({TIME_COLUMN: times, 'Set O2': 60.0}),
                  'CcO2': pd.DataFrame({TIME_COLUMN: times,
                                        'Measured O2': (50.0 -
                                                        (10.0 if is_control else 30.0)
                                                        * share
                                                        ),
                                        },
                                       ),
                  'VoO2': pd.DataFrame({TIME_COLUMN: times,
                                        'VoO2': (3.0 if is_control else 6.0) * share,
                                        },
                                       ),
                  'metadata': {'events': [{'time': 10.0, 'label': 'KCN'}]},
                  'averages': {'windows': {'average0': {'start_time': 2.0,
                                                        'end_time': 8.0,
                                                        },
                                           'average1': {'start_time': 20.0,
                                                        'end_time': 28.0,
                                                        },
                                           },
                               },
                  }
    for table, ends in HAEM_ENDS[name].items():
        experiment[table] = pd.DataFrame({TIME_COLUMN: times,
                                          **{haem: start + (end - start) * share
                                             for haem, (start, end) in zip(HAEMS, ends)
                                             },
                                          },
                                         )
    if is_control:
        experiment['delta_psi'] = pd.DataFrame({TIME_COLUMN: times,
                                                DELTA_PSI_COLUMN: 100.0 + 30.0 * share,
                                                },
                                               )
    return experiment


# ---- _page_drawer --------------------------------------------------------------------
def _page_drawer(roles_by_name: List[Tuple[str, Dict[str, str]]],
                 answers: Optional[dict] = None,
                 experiments: Optional[Dict[str, dict]] = None,
                 ) -> Tuple[Figure, List[Dict[str, Axes]]]:
    """
    ---- Summary ----
    Helper function to draw a page of Standard experiments side by side, each three
    columns wide and three rows tall, from the left.

    ---- Inputs ----
    roles_by_name : List[Tuple[str, Dict[str, str]]]
        (the experiment, the other roles of its plot) of each plot, at most two.
    answers : Optional[dict]
        The answers of the run; None for those of _answers_maker.
    experiments : Optional[Dict[str, dict]]
        The slim copies; None for c1 and k1 of _experiment_maker.

    ---- Globals read ----
    NO_SUCH_ROLE; STANDARD_SPEC (imported).

    ---- Outputs ----
    Tuple[Figure, List[Dict[str, Axes]]]
        (the figure, for each plot {the key of the panel: its axes}; the axes of a
        sentence are under 'sentence').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _experiment_maker
    _setup_maker
    experiment_role_maker
    figure_page_drawer
    """

    setup = _setup_maker()
    page = FigurePage()
    for place, (name, roles) in enumerate(roles_by_name):
        # an experiment the set-up does not have gets a role nothing fits
        role = experiment_role_maker(setup, name) or NO_SUCH_ROLE
        page = plot_placer(page,
                           PagePlot('P1',
                                    row=0,
                                    column=3 * place,
                                    n_rows=3,
                                    n_columns=3,
                                    roles=dict(roles, experiment=role),
                                    ),
                           )
    if experiments is None:
        experiments = {name: _experiment_maker(name) for name in ('c1', 'k1')}
    fig, _ = figure_page_drawer(page,
                                STANDARD_SPEC,
                                setup,
                                experiments,
                                _answers_maker() if answers is None else answers,
                                )
    panels: List[Dict[str, Axes]] = [{} for _ in roles_by_name]
    for ax in fig.axes:
        place = 0 if ax.get_position().x0 < 0.5 else 1
        if hasattr(ax, 'panel_key'):
            panels[place][ax.panel_key] = ax
        elif not ax.axison:
            panels[place]['sentence'] = ax
    return fig, panels


# ---- _setup_maker --------------------------------------------------------------------
def _setup_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make the set-up of a made-up dataset of three experiments: a
    control (c1), a knockdown (k1) and a second knockdown (k2), which is never read.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The set-up table (dataset_setup, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {'group_names': ['', ''],
            'colours': {'control': '#0072b2', 'knockdown': '#d55e00'},
            'rows': [{'name': name,
                      'use': True,
                      'group_1': group,
                      'group_2': '',
                      'time_point': '',
                      'run': run,
                      }
                     for name, group, run in (('c1', 'control', 1),
                                              ('k1', 'knockdown', 1),
                                              ('k2', 'knockdown', 2),
                                              )
                     ],
            }


# ---- _spectrum_drawer ----------------------------------------------------------------
def _spectrum_drawer(plot_type: str,
                     roles: Dict[str, str],
                     experiments: Optional[Dict[str, dict]] = None,
                     ) -> Tuple[Figure, Axes]:
    """
    ---- Summary ----
    Helper function to draw a page with one spectrum plot (a Difference spectrum or
    a Waterfall) of the made-up time series, three columns wide and three rows tall
    at the top left.

    ---- Inputs ----
    plot_type : str
        'P2' or 'P3'.
    roles : Dict[str, str]
        The roles of the plot.
    experiments : Optional[Dict[str, dict]]
        The slim copies; None for those of _spectrum_experiments_maker.

    ---- Globals read ----
    STANDARD_SPEC (imported).

    ---- Outputs ----
    Tuple[Figure, Axes]
        (the figure, the first axes of the plot).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _series_setup_maker
    _spectrum_experiments_maker
    figure_page_drawer
    """

    page = plot_placer(FigurePage(),
                       PagePlot(plot_type,
                                row=0,
                                column=0,
                                n_rows=3,
                                n_columns=3,
                                roles=roles,
                                ),
                       )
    if experiments is None:
        experiments = _spectrum_experiments_maker()
    fig, axes = figure_page_drawer(page,
                                   STANDARD_SPEC,
                                   _series_setup_maker(),
                                   experiments,
                                   _answers_maker(),
                                   )
    return fig, axes[0]


# ---- _spectrum_experiments_maker -----------------------------------------------------
def _spectrum_experiments_maker() -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to make the slim copies of the made-up time series, as far as
    the spectrum plots read them: each difference spectrum is 0 mOD from 500 to 600
    nm (every 5 nm) but for the peak of bH at 560 nm and that of cc at 550 nm
    (PEAKS_MOD); its parts are those two peaks and a background of 0.5 mOD
    everywhere, so the fit is 0.5 mOD above the difference and the residual -0.5 mOD.
    a4 was read but has no difference spectrum.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BANDS, HAEMS, PEAKS_MOD.

    ---- Outputs ----
    Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    wavelengths = np.arange(500.0, 601.0, 5.0)
    experiments: Dict[str, dict] = {'a4': {'experiment_name': 'a4',
                                           'difference': None,
                                           'difference_parts': None,
                                           'haem_bands': dict(BANDS),
                                           },
                                    }
    for name, (b_peak, c_peak) in PEAKS_MOD.items():
        b_part = np.where(wavelengths == 560.0, b_peak, 0.0)
        c_part = np.where(wavelengths == 550.0, c_peak, 0.0)
        measured = b_part + c_part
        background = np.full(len(wavelengths), 0.5)
        experiments[name] = {'experiment_name': name,
                             'difference': {'wavelengths_nm': wavelengths,
                                            'difference_mOD': measured,
                                            'oxidised_region': (2.0, 4.0),
                                            'reduced_region': (12.0, 14.0),
                                            },
                             'difference_parts': {'wavelengths_nm': wavelengths,
                                                  'measured_mOD': measured,
                                                  'haems_mOD': dict(
                                                      zip(HAEMS, (b_part, c_part)),
                                                      ),
                                                  'background_mOD': background,
                                                  'fit_mOD': measured + background,
                                                  'residual_mOD': -background,
                                                  },
                             'haem_bands': dict(BANDS),
                             }
    return experiments


# ---- _series_setup_maker -------------------------------------------------------------
def _series_setup_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make the set-up of the made-up time series: four controls
    (a1 and a2 at 2 h, a3 and a4 at 7 h) and one knockdown (k1, at 2 h).

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The set-up table (dataset_setup, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {'group_names': ['strain', ''],
            'colours': {'control': '#0072b2', 'knockdown': '#d55e00'},
            'rows': [{'name': name,
                      'use': True,
                      'group_1': group,
                      'group_2': '',
                      'time_point': time_point,
                      'run': run,
                      }
                     for name, group, time_point, run in (('a1', 'control', '2 h', 1),
                                                          ('a2', 'control', '2 h', 2),
                                                          ('a3', 'control', '7 h', 1),
                                                          ('a4', 'control', '7 h', 2),
                                                          ('k1', 'knockdown', '2 h', 1),
                                                          )
                     ],
            }


# ---- _trace_experiments_maker --------------------------------------------------------
def _trace_experiments_maker() -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to make the slim copies of the made-up time series, as far as
    the plots over time read them (OCR_RUNS): each has an OCR every half minute from
    0 min, at its level before its first addition and at half of it from then on,
    so 100 then 50 % of baseline; its additions, named add 1 and add 2; a baseline
    region from 2 to 8 min and a settled region 2 min long from 1 min after its
    first addition.

    ---- Inputs ----
    None.

    ---- Globals read ----
    OCR_RUNS; TIME_COLUMN (imported).

    ---- Outputs ----
    Dict[str, dict]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    experiments = {}
    for name, (level, additions, end) in OCR_RUNS.items():
        times = np.arange(0.0, end + 0.25, 0.5)
        ocr = np.where(times < additions[0], level, level / 2.0)
        percent = pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr / level * 100.0})
        percent.attrs['baseline_percent'] = {'start_time': 2.0,
                                             'end_time': 8.0,
                                             'baseline_mean': {'VoO2': level},
                                             }
        windows = {'average0': {'start_time': 2.0, 'end_time': 8.0, 'kind': 'baseline'},
                   'average1': {'start_time': additions[0] + 1.0,
                                'end_time': additions[0] + 3.0,
                                'kind': 'settled',
                                },
                   }
        experiments[name] = {'experiment_name': name,
                             'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr}),
                             'VoO2_baseline': percent,
                             'metadata': {'events': [{'time': moment,
                                                      'label': f'add {place + 1}',
                                                      }
                                                     for place, moment
                                                     in enumerate(additions)
                                                     ],
                                          },
                             'averages': {'windows': windows},
                             }
    return experiments


# ---- _value_finder -------------------------------------------------------------------
def _value_finder(times: np.ndarray, values: np.ndarray, moment: float) -> float:
    """
    ---- Summary ----
    Helper function to read a line at the last of its points nearest to a time.

    ---- Inputs ----
    times : np.ndarray
        The times of the line, shape (n_points,) (min).
    values : np.ndarray
        Its values, shape (n_points,).
    moment : float
        The time (min).

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The value there.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.asarray(times, dtype=float)
    near = np.flatnonzero(np.isclose(times, moment, atol=1e-6))
    return float(np.asarray(values, dtype=float)[near[-1]])


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_the_form_of_a_standard_experiment ------------------------------------------
def test_the_form_of_a_standard_experiment() -> None:
    """
    ---- Summary ----
    Main function to check what the form of a Standard experiment asks and how it
    starts: the first experiment; a tick per panel, all on, a haem named in plain
    letters; ΔD; the labels on, the regions off and the same scales on. A run without
    haems or Δψ has no tick for them and no view; a plot keeps the choices it has,
    and a view that does not exist starts again at ΔD.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _setup_maker
    experiment_role_maker
    form_fields_lister
    """

    # ---- 1 A new plot ----------------------------------------------------------------
    setup = _setup_maker()
    fields = form_fields_lister('P1', setup, {}, _answers_maker())
    assert [(f['key'], f['kind'], f['label'], f['value']) for f in fields] == [
        ('experiment', 'choice', 'Experiment', experiment_role_maker(setup, 'c1')),
        ('panel_oxygen', 'tick', 'Panel: oxygen', 'yes'),
        ('panel_vo2', 'tick', 'Panel: OCR', 'yes'),
        ('panel_haem_cytbh', 'tick', 'Panel: Cyt bH', 'yes'),
        ('panel_haem_cytcc', 'tick', 'Panel: Cyt cc', 'yes'),
        ('panel_delta_psi', 'tick', 'Panel: Δψ', 'yes'),
        ('haem_view', 'choice', 'Haems shown as', 'delta'),
        ('addition_labels', 'tick', 'Labels of the additions', 'yes'),
        ('regions_shaded', 'tick', 'Averaging regions shaded', 'no'),
        ('same_scales', 'tick', 'Same scales as the other standard plots', 'yes'),
        ]
    assert [words for _, words in fields[0]['choices']] == ['c1', 'k1', 'k2']
    assert fields[6]['choices'] == [('delta', 'ΔD'),
                                    ('abs', 'Absorbance'),
                                    ('percent', '% oxidised'),
                                    ]

    # ---- 2 A run without haems or Δψ, and no answers at all --------------------------
    plain = ['experiment',
             'panel_oxygen',
             'panel_vo2',
             'addition_labels',
             'regions_shaded',
             'same_scales',
             ]
    bare = _answers_maker(decompose=False, delta_psi=False)
    assert [f['key'] for f in form_fields_lister('P1', setup, {}, bare)] == plain
    assert [f['key'] for f in form_fields_lister('P1', setup, {})] == plain

    # ---- 3 A plot keeps its choices --------------------------------------------------
    roles = {'experiment': experiment_role_maker(setup, 'k1'),
             'panel_vo2': 'no',
             'haem_view': 'abs',
             'regions_shaded': 'yes',
             }
    kept = {f['key']: f['value']
            for f in form_fields_lister('P1', setup, roles, _answers_maker())
            }
    assert kept['experiment'] == roles['experiment']
    assert (kept['panel_vo2'], kept['haem_view'], kept['regions_shaded']) == ('no',
                                                                              'abs',
                                                                              'yes',
                                                                              )
    again = form_fields_lister('P1', setup, {'haem_view': 'raw'}, _answers_maker())
    assert again[6]['value'] == 'delta'


# ---- test_the_panels_of_a_standard_experiment ----------------------------------------
def test_the_panels_of_a_standard_experiment() -> None:
    """
    ---- Summary ----
    Main function to check the panels a Standard experiment draws: every panel the
    file has to start with (Δψ only for the file that has it), in the order oxygen,
    OCR, haems, Δψ; only the ones ticked otherwise; and the haems in the view picked,
    read from the title of their axis.

    ---- Inputs ----
    None.

    ---- Globals read ----
    B_KEY, C_KEY.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _page_drawer
    """

    # ---- 1 Every panel, top first ----------------------------------------------------
    fig, (first, second) = _page_drawer([('c1', {}), ('k1', {})])
    assert list(first) == ['oxygen', 'vo2', B_KEY, C_KEY, 'delta_psi']
    assert list(second) == ['oxygen', 'vo2', B_KEY, C_KEY]
    tops = [ax.get_position().y1 for ax in first.values()]
    assert tops == sorted(tops, reverse=True)

    # ---- 2 Only the panels ticked ----------------------------------------------------
    _, (first,) = _page_drawer([('c1',
                                 {'panel_oxygen': 'no',
                                  'panel_haem_cytcc': 'no',
                                  'panel_delta_psi': 'no',
                                  },
                                 ),
                                ],
                               )
    assert list(first) == ['vo2', B_KEY]

    # ---- 3 The view of the haems -----------------------------------------------------
    for view, title in (('delta', 'ΔD (mOD)'),
                        ('abs', 'Haem absorbance (mOD)'),
                        ('percent', 'Oxidised haem (%)'),
                        ):
        fig, (first,) = _page_drawer([('c1', {'haem_view': view})])
        titles = [ax.get_ylabel() for ax in fig.axes if not hasattr(ax, 'panel_key')]
        assert titles == [title]
        line = first[B_KEY].lines[0]
        ends = {'delta': 2.0, 'abs': 12.0, 'percent': 50.0}
        assert line.get_ydata()[-1] == pytest.approx(ends[view])


# ---- test_the_labels_and_the_regions_of_a_standard_experiment ------------------------
def test_the_labels_and_the_regions_of_a_standard_experiment() -> None:
    """
    ---- Summary ----
    Main function to check the two ticks of what is drawn over the panels: the label
    of each addition above the top panel (on to start with, its dashed line staying
    when it is off), and the averaging regions shaded behind every panel (off to
    start with), the baseline with its name.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The made-up file has two regions, so each panel has two shaded spans.

    ---- Helpers ----
    _page_drawer
    """

    # ---- 1 As a plot starts ----------------------------------------------------------
    _, (first,) = _page_drawer([('c1', {})])
    top = first['oxygen']
    assert [text.get_text() for text in top.texts] == ['KCN']
    assert all(not ax.patches for ax in first.values())

    # ---- 2 The labels off, the regions on --------------------------------------------
    _, (first,) = _page_drawer([('c1',
                                 {'addition_labels': 'no', 'regions_shaded': 'yes'},
                                 ),
                                ],
                               )
    top = first['oxygen']
    assert [text.get_text() for text in top.texts] == ['Baseline']
    assert all(len(ax.patches) == 2 for ax in first.values())
    dashed = [line for line in top.lines if list(line.get_xdata()) == [10.0, 10.0]]
    assert len(dashed) == 1


# ---- test_standard_experiments_share_their_scales ------------------------------------
def test_standard_experiments_share_their_scales() -> None:
    """
    ---- Summary ----
    Main function to check the scales of two Standard experiments on one page, worked
    out by hand: with the tick on (as a plot starts) every haem panel of both has the
    one range in ΔD and the one height of range in absorbance, the oxygen panels and
    the OCR panels have the range that holds both; in % oxidised, and with the tick
    of one plot off, each plot keeps its own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    B_KEY, C_KEY.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A panel alone runs from its lowest value less 5 % of its range to its highest
    plus 5 %. ΔD: c1 has bH 0 to 2 (-0.1 to 2.1) and cc 0 to 1 (-0.05 to 1.05), so
    alone its haems run from -0.1 to 2.1; k1 has bH 0 to -4 (-4.2 to 0.2) and cc 0 to
    1, so alone -4.2 to 1.05; together -4.2 to 2.1. Absorbance: c1 has bH 10 to 12
    (9.9 to 12.1, height 2.2, middle 11) and cc 5 to 6 (middle 5.5); k1 has bH 10 to
    6 (5.8 to 10.2, height 4.4, middle 8) and cc 5 to 6; the largest height is 4.4,
    so c1's bH runs from 11 - 2.2 = 8.8 to 13.2, k1's from 5.8 to 10.2 and both cc
    from 5.5 - 2.2 = 3.3 to 7.7.

    ---- Helpers ----
    _page_drawer
    """

    # ---- 1 ΔD: one range -------------------------------------------------------------
    _, (first, second) = _page_drawer([('c1', {}), ('k1', {})])
    for panels in (first, second):
        for key in (B_KEY, C_KEY):
            assert panels[key].get_ylim() == pytest.approx((-4.2, 2.1))

    # ---- 2 The oxygen and the OCR: the range that holds both -------------------------
    _, (alone_c,) = _page_drawer([('c1', {})])
    _, (alone_k,) = _page_drawer([('k1', {})])
    for key in ('oxygen', 'vo2'):
        low_c, high_c = alone_c[key].get_ylim()
        low_k, high_k = alone_k[key].get_ylim()
        assert (low_c, high_c) != pytest.approx((low_k, high_k))
        together = (min(low_c, low_k), max(high_c, high_k))
        assert first[key].get_ylim() == pytest.approx(together)
        assert second[key].get_ylim() == pytest.approx(together)
    # one plot on the page shares with nothing
    assert alone_c[B_KEY].get_ylim() == pytest.approx((-0.1, 2.1))
    assert alone_k[C_KEY].get_ylim() == pytest.approx((-4.2, 1.05))

    # ---- 3 Absorbance: one height of range -------------------------------------------
    view = {'haem_view': 'abs'}
    _, (first, second) = _page_drawer([('c1', view), ('k1', view)])
    assert first[B_KEY].get_ylim() == pytest.approx((8.8, 13.2))
    assert second[B_KEY].get_ylim() == pytest.approx((5.8, 10.2))
    assert first[C_KEY].get_ylim() == pytest.approx((3.3, 7.7))
    assert second[C_KEY].get_ylim() == pytest.approx((3.3, 7.7))

    # ---- 4 % oxidised: each haem its own ---------------------------------------------
    view = {'haem_view': 'percent'}
    _, (first, second) = _page_drawer([('c1', view), ('k1', view)])
    assert first[B_KEY].get_ylim() == pytest.approx((-2.5, 52.5))
    assert second[B_KEY].get_ylim() == pytest.approx((-5.0, 105.0))

    # ---- 5 The tick of one plot off: each plot its own -------------------------------
    _, (first, second) = _page_drawer([('c1', {}), ('k1', {'same_scales': 'no'})])
    assert first[B_KEY].get_ylim() == pytest.approx((-0.1, 2.1))
    assert second[B_KEY].get_ylim() == pytest.approx((-4.2, 1.05))
    assert first['vo2'].get_ylim() == pytest.approx(alone_c['vo2'].get_ylim())
    # plots in different views share the oxygen and the OCR, not the haems
    _, (first, second) = _page_drawer([('c1', {}), ('k1', {'haem_view': 'abs'})])
    assert first[B_KEY].get_ylim() == pytest.approx((-0.1, 2.1))
    assert first['vo2'].get_ylim() == pytest.approx(second['vo2'].get_ylim())


# ---- test_a_standard_experiment_that_cannot_be_drawn_says_why ------------------------
def test_a_standard_experiment_that_cannot_be_drawn_says_why() -> None:
    """
    ---- Summary ----
    Main function to check the one sentence written in the cells in place of the
    plot: for a plot whose experiment is not in the dataset, for an experiment that
    could not be read, for a plot with no panel ticked, and for haems asked in a view
    the file does not have; the plot beside it is still drawn.

    ---- Inputs ----
    None.

    ---- Globals read ----
    B_KEY; NO_PANEL, NOT_READ, NOT_THERE (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _experiment_maker
    _page_drawer
    """

    # ---- sentence_reader -------------------------------------------------------------
    def sentence_reader(panels: Dict[str, Axes]) -> str:
        assert list(panels) == ['sentence']
        return ' '.join(panels['sentence'].texts[0].get_text().split())

    _, (first, second) = _page_drawer([('gone', {}), ('k2', {})])
    assert sentence_reader(first) == NOT_THERE
    assert sentence_reader(second) == NOT_READ.format('k2')
    off = {'panel_oxygen': 'no',
           'panel_vo2': 'no',
           'panel_haem_cytbh': 'no',
           'panel_haem_cytcc': 'no',
           'panel_delta_psi': 'no',
           }
    _, (first, second) = _page_drawer([('c1', off), ('k1', {})])
    assert sentence_reader(first) == NO_PANEL
    assert B_KEY in second
    bare = _experiment_maker('c1')
    del bare['haem_percent']
    _, (first,) = _page_drawer([('c1', {'haem_view': 'percent'})],
                               experiments={'c1': bare},
                               )
    assert sentence_reader(first) == ('c1 has no haems to show as % oxidised. Open '
                                      'the form of this plot (✎) and pick another '
                                      'view of the haems, or untick the haems.'
                                      )


# ---- test_a_standard_experiment_stays_inside_its_cells -------------------------------
def test_a_standard_experiment_stays_inside_its_cells() -> None:
    """
    ---- Summary ----
    Main function to check that everything a Standard experiment draws is inside its
    cells: its panels, their numbers and titles, the shared title of the haems, the
    labels of the additions above the top panel and the name of the baseline.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The first plot takes columns 0 to 2 and rows 0 to 2: x from 0 to 0.5 and y from
    0.5 to 1 of the figure; the second x from 0.5 to 1.

    ---- Helpers ----
    _page_drawer
    """

    roles = {'regions_shaded': 'yes'}
    fig, _ = _page_drawer([('c1', roles), ('k1', roles)])
    renderer = fig._get_renderer()
    for is_left in (True, False):
        boxes = [ax.get_tightbbox(renderer)
                 for ax in fig.axes
                 if (ax.get_position().x0 < 0.5) == is_left
                 ]
        tight = Bbox.union(boxes).transformed(fig.transFigure.inverted())
        left = 0.0 if is_left else 0.5
        assert left <= tight.x0 and tight.x1 <= left + 0.5
        assert 0.5 <= tight.y0 and tight.y1 <= 1.0


# ---- test_a_standard_experiment_has_the_font_of_the_page -----------------------------
def test_a_standard_experiment_has_the_font_of_the_page() -> None:
    """
    ---- Summary ----
    Main function to check that every number and title of a Standard experiment is in
    the font of the page's journal, also when the run was set up for a journal with
    another font and the numbers of the axes are only made when the page is drawn.

    ---- Inputs ----
    None.

    ---- Globals read ----
    STANDARD_SPEC (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _page_drawer
    """

    fonts = font_family_lister(STANDARD_SPEC['font_family'])
    with matplotlib.rc_context({'font.family': ['Courier New']}):  # the run's journal
        fig, _ = _page_drawer([('c1', {}), ('k1', {})])
        fig.set_size_inches(*(2 * fig.get_size_inches()))  # more room: new numbers
        fig.canvas.draw()
        families = {tuple(text.get_fontfamily())
                    for text in fig.findobj(Text)
                    if text.get_text() and text.get_visible()
                    }
    assert families  # a text with symbols may add a font for them after the page's
    assert all(family[:len(fonts)] == tuple(fonts) for family in families)
    assert not any('Courier New' in family for family in families)


# ---- test_the_form_of_a_difference_spectrum ------------------------------------------
def test_the_form_of_a_difference_spectrum() -> None:
    """
    ---- Summary ----
    Main function to check what the form of a Difference spectrum asks and how it
    starts: the first experiment; the haem parts, the fit and the residual on; the
    background and the haem bands off; and that it keeps the roles a plot has.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _series_setup_maker
    """

    setup = _series_setup_maker()
    fields = form_fields_lister('P2', setup, {}, _answers_maker())
    assert [(field['key'], field['value']) for field in fields] == [
        ('experiment', experiment_role_maker(setup, 'a1')),
        ('haem_components', 'yes'),
        ('background', 'no'),
        ('overall_fit', 'yes'),
        ('residual', 'yes'),
        ('haem_bands', 'no'),
        ]
    assert [words for _, words in fields[0]['choices']] == ['a1',
                                                            'a2',
                                                            'a3',
                                                            'a4',
                                                            'k1',
                                                            ]
    kept = {'experiment': experiment_role_maker(setup, 'k1'),
            'background': 'yes',
            'residual': 'no',
            }
    fields = form_fields_lister('P2', setup, kept, _answers_maker())
    values = {field['key']: field['value'] for field in fields}
    assert {key: values[key] for key in kept} == kept


# ---- test_the_lines_of_a_difference_spectrum -----------------------------------------
def test_the_lines_of_a_difference_spectrum() -> None:
    """
    ---- Summary ----
    Main function to check what a Difference spectrum draws: as it starts, the
    measured difference in black, each haem in its colour and the fit, in mOD, with
    the residual in a panel underneath and a small legend; then the background, the
    haem bands (marked as a backdrop) and no residual, as ticked; everything inside
    its cells.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BANDS, HAEMS; BACKDROP_MARK (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    a1 has a bH peak of 4 mOD at 560 nm and a cc peak of 1 mOD at 550 nm, the 13th
    and the 11th of its 21 wavelengths; its fit is 0.5 mOD higher everywhere and its
    residual -0.5 mOD. The plot takes x from 0 to 0.5 and y from 0.5 to 1 of the
    figure.

    ---- Helpers ----
    _series_setup_maker
    _spectrum_drawer
    """

    # ---- 1 As it starts --------------------------------------------------------------
    role = experiment_role_maker(_series_setup_maker(), 'a1')
    fig, main = _spectrum_drawer('P2', {'experiment': role})
    lines = {line.get_label(): line for line in main.lines}
    assert [label for label in lines if not label.startswith('_')] == ['Measured',
                                                                       *HAEMS,
                                                                       'Fit',
                                                                       ]
    measured = lines['Measured'].get_ydata()
    assert (measured[12], measured[10], measured[0]) == (4.0, 1.0, 0.0)
    assert lines['Measured'].get_color() == 'black'
    colours = settings.haem_colour_mapper(HAEMS)
    for haem in HAEMS:
        assert lines[haem].get_color() == colours[haem]
    assert lines[HAEMS[0]].get_ydata()[12] == 4.0
    assert lines['Fit'].get_ydata()[12] == 4.5
    assert main.get_ylabel() == 'Reduced − oxidised (mOD)'
    assert main.get_xlim() == (500.0, 600.0)
    assert main.get_legend() is not None and not main.patches
    lower = [ax for ax in fig.axes if ax is not main and ax.axison]
    assert len(lower) == 1
    assert lower[0].get_xlabel() == 'Wavelength (nm)'
    assert lower[0].get_ylabel() == 'Residual (mOD)'
    assert list(lower[0].lines[0].get_ydata()) == [-0.5] * 21
    assert lower[0].get_position().y1 < main.get_position().y0
    tight = Bbox.union([ax.get_tightbbox(fig._get_renderer()) for ax in fig.axes])
    tight = tight.transformed(fig.transFigure.inverted())
    assert 0.0 <= tight.x0 and tight.x1 <= 0.5
    assert 0.5 <= tight.y0 and tight.y1 <= 1.0

    # ---- 2 As ticked -----------------------------------------------------------------
    roles = {'experiment': role,
             'haem_components': 'no',
             'background': 'yes',
             'overall_fit': 'no',
             'residual': 'no',
             'haem_bands': 'yes',
             }
    fig, main = _spectrum_drawer('P2', roles)
    labels = [line.get_label() for line in main.lines]
    assert [label for label in labels if not label.startswith('_')] == ['Measured',
                                                                        'Background',
                                                                        ]
    assert [ax for ax in fig.axes if ax.axison] == [main]
    assert main.get_xlabel() == 'Wavelength (nm)'
    assert [(band.get_x(), band.get_x() + band.get_width())
            for band in main.patches
            ] == list(BANDS.values())
    assert all(getattr(band, BACKDROP_MARK) for band in main.patches)
    assert main.get_xlim() == (500.0, 600.0)


# ---- test_a_difference_spectrum_that_cannot_be_drawn_says_why ------------------------
def test_a_difference_spectrum_that_cannot_be_drawn_says_why() -> None:
    """
    ---- Summary ----
    Main function to check the one sentence written in the cells of a Difference
    spectrum whose experiment is not in the dataset, could not be read, or has no
    difference spectrum.

    ---- Inputs ----
    None.

    ---- Globals read ----
    NO_SUCH_ROLE; NO_DIFFERENCE, NOT_READ, NOT_THERE (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _series_setup_maker
    _spectrum_drawer
    _spectrum_experiments_maker
    """

    setup = _series_setup_maker()
    experiments = _spectrum_experiments_maker()
    del experiments['a2']
    for role, sentence in ((NO_SUCH_ROLE, NOT_THERE),
                           (experiment_role_maker(setup, 'a2'), NOT_READ.format('a2')),
                           (experiment_role_maker(setup, 'a4'),
                            NO_DIFFERENCE.format('a4'),
                            ),
                           ):
        _, ax = _spectrum_drawer('P2', {'experiment': role}, experiments)
        assert not ax.axison
        assert ' '.join(ax.texts[0].get_text().split()) == sentence


# ---- test_the_form_of_a_waterfall ----------------------------------------------------
def test_the_form_of_a_waterfall() -> None:
    """
    ---- Summary ----
    Main function to check what the form of a Waterfall asks and how it starts: one
    line for each time point, the first group, the difference spectrum stacked (or
    a trace, with how it is shown and its time 0), lined up on the first b haem, the
    haem bands on, the labels of the additions on; no question about the time
    points for a set-up without any; no question about the haems in a run that
    works out none.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _series_setup_maker
    _setup_maker
    """

    setup = _series_setup_maker()
    fields = form_fields_lister('P3', setup, {}, _answers_maker())
    assert [(field['key'], field['label'], field['value']) for field in fields] == [
        ('time_point', 'One line for', 'Split'),
        ('group_1', 'strain', 'Only label 1'),
        ('trace', 'Stacked', 'difference'),
        ('vo2_value', 'OCR shown as', 'baseline'),
        ('haem_view', 'Haems shown as', 'delta'),
        ('delta_psi_value', 'Δψ shown as', 'raw'),
        ('time_zero', 'Time 0 at', 'addition 1'),
        ('align_haem', 'Spectra lined up on', 'cytbh'),
        ('haem_bands', 'Haem bands', 'yes'),
        ('addition_labels', 'Labels of the additions', 'yes'),
        ]
    assert fields[0]['choices'] == [
        ('Split', 'Each time point (the mean of its replicates)'),
        ('All together', 'Each experiment'),
        ]
    assert fields[1]['choices'] == [('Only label 1', 'control'),
                                    ('Only label 2', 'knockdown'),
                                    ]
    assert fields[2]['choices'] == [('difference', 'The difference spectrum'),
                                    ('oxygen', 'O₂'),
                                    ('vo2', 'OCR'),
                                    ('haem_cytbh', 'Cyt bH'),
                                    ('haem_cytcc', 'Cyt cc'),
                                    ('delta_psi', 'Δψ'),
                                    ]
    assert fields[7]['choices'] == [('cytbh', 'Cyt bH'), ('cytcc', 'Cyt cc')]
    # a c haem first: the waterfall still starts on the first b haem
    turned = _answers_maker(haems=['Cyt cc', 'Cyt $b_H$'])
    assert form_fields_lister('P3', setup, {}, turned)[7]['value'] == 'cytbh'
    kept = {'time_point': 'All together', 'group_1': 'Only label 2', 'trace': 'vo2'}
    fields = form_fields_lister('P3', setup, kept, _answers_maker())
    assert [field['value'] for field in fields[:3]] == list(kept.values())
    fields = form_fields_lister('P3', _setup_maker(), {}, _answers_maker())
    assert [field['key'] for field in fields][:2] == ['group_1', 'trace']
    fields = form_fields_lister('P3',
                                setup,
                                {},
                                _answers_maker(decompose=False, delta_psi=False),
                                )
    assert [field['key'] for field in fields] == ['time_point',
                                                  'group_1',
                                                  'trace',
                                                  'vo2_value',
                                                  'time_zero',
                                                  'addition_labels',
                                                  ]


# ---- test_the_lines_of_a_waterfall ---------------------------------------------------
def test_the_lines_of_a_waterfall() -> None:
    """
    ---- Summary ----
    Main function to check the lines of a waterfall, worked out by hand: as a time
    series, one line per time point, the mean of its replicates, named with how many
    and lighter for the later time point; as experiments, one line each, lighter
    down the stack; an experiment without a difference spectrum left out and named,
    one that was not read only missing; another group; and the experiments the
    waterfalls of a page leave out.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BLUE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The controls at 2 h are a1 (bH 4, cc 1 mOD) and a2 (6, 3): mean 5 and 2 mOD, at
    the 13th and the 11th wavelength. At 7 h only a3 (2, 8) has a difference
    spectrum. Blue #0072b2 with 0.7 of white: 0 + 255 x 0.7 = 178 (b2), 114 + 141 x
    0.7 = 213 (d5), 178 + 77 x 0.7 = 232 (e8); with 0.35 of white: 89 (59), 163
    (a3), 205 (cd).

    ---- Helpers ----
    _series_setup_maker
    _spectrum_experiments_maker
    """

    # ---- 1 A time series -------------------------------------------------------------
    setup, experiments = _series_setup_maker(), _spectrum_experiments_maker()
    lines, left_out = waterfall_lines_lister(setup, {}, experiments)
    assert [line['label'] for line in lines] == ['2 h (n = 2)', '7 h (n = 1)']
    assert [line['colour'] for line in lines] == [BLUE, '#b2d5e8']
    assert [(line['values_mOD'][12], line['values_mOD'][10], line['values_mOD'][0])
            for line in lines
            ] == [(5.0, 2.0, 0.0), (2.0, 8.0, 0.0)]
    assert left_out == ['a4']

    # ---- 2 Each experiment -----------------------------------------------------------
    roles = {'time_point': 'All together'}
    lines, left_out = waterfall_lines_lister(setup, roles, experiments)
    assert [line['label'] for line in lines] == ['a1', 'a2', 'a3']
    assert [line['colour'] for line in lines] == [BLUE, '#59a3cd', '#b2d5e8']
    assert [line['values_mOD'][12] for line in lines] == [4.0, 6.0, 2.0]
    assert left_out == ['a4']
    without = {name: slim for name, slim in experiments.items() if name != 'a2'}
    lines, left_out = waterfall_lines_lister(setup, roles, without)
    assert [line['label'] for line in lines] == ['a1', 'a3'] and left_out == ['a4']

    # ---- 3 The other group, and what a page leaves out -------------------------------
    knockdown = {'group_1': 'Only label 2'}
    lines, left_out = waterfall_lines_lister(setup, knockdown, experiments)
    assert [(line['label'], line['colour']) for line in lines] == [('2 h (n = 1)',
                                                                    '#d55e00',
                                                                    ),
                                                                   ]
    assert left_out == []
    page = FigurePage()
    for row, plot_roles in enumerate(({}, roles, knockdown)):
        page = plot_placer(page, PagePlot('P3', row=row, column=0, roles=plot_roles))
    assert waterfall_left_out_lister(page, setup, experiments) == ['a4']
    page = plot_placer(FigurePage(), PagePlot('P3', row=0, column=0, roles=knockdown))
    assert waterfall_left_out_lister(page, setup, experiments) == []


# ---- test_a_waterfall_drawn ----------------------------------------------------------
def test_a_waterfall_drawn() -> None:
    """
    ---- Summary ----
    Main function to check a Waterfall as drawn, worked out by hand: the time series
    lined up on bH and stacked from the top down, no numbers on the y axis, the haem
    bands behind with the legend still inside the axes, everything inside its cells;
    then lined up on cc without bands; and the sentence of a waterfall with no
    spectrum to show.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BANDS; NO_WATERFALL (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The lines are 2 h (bH 5, cc 2 mOD, else 0) and 7 h (bH 2, cc 8). Lined up on bH
    (its highest point in 557.5 to 562.5 nm moved to 0): 2 h is -5, with 0 at 560
    and -3 at 550 nm, 5 high; 7 h is -2, with 0 at 560 and 6 at 550 nm, 8 high. The
    gap is 0.75 x 8 = 6, so 2 h is drawn 6 higher: 1, with 6 at 560 and 3 at 550 nm;
    7 h stays. The y range is -2 to 6 with 2 % of 8 at each end: -2.16 to 6.16.
    Lined up on cc: 2 h is -2, with 0 at 550 and 3 at 560 nm, drawn 6 higher: 4, 6
    and 9; 7 h is -8, with 0 at 550 and -6 at 560 nm.

    ---- Helpers ----
    _spectrum_drawer
    _spectrum_experiments_maker
    """

    # ---- 1 Lined up on bH, with the bands --------------------------------------------
    fig, ax = _spectrum_drawer('P3', {})
    drawn = [line.get_ydata() for line in ax.lines]
    assert [line.get_label() for line in ax.lines] == ['2 h (n = 2)', '7 h (n = 1)']
    assert [(values[0], values[12], values[10]) for values in drawn] == [
        (1.0, 6.0, 3.0),
        (-2.0, 0.0, 6.0),
        ]
    assert ax.get_ylim() == pytest.approx((-2.16, 6.16))
    assert ax.get_xlim() == (500.0, 600.0)
    assert list(ax.get_yticks()) == []
    assert ax.get_xlabel() == 'Wavelength (nm)'
    assert ax.get_ylabel() == 'Reduced − oxidised (stacked)'
    assert [(band.get_x(), band.get_x() + band.get_width())
            for band in ax.patches
            ] == list(BANDS.values())
    renderer = fig._get_renderer()
    legend = ax.get_legend().get_window_extent(renderer)
    inside = ax.get_window_extent(renderer)
    assert inside.y0 <= legend.y0 and legend.y1 <= inside.y1  # a band is no cover
    tight = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
    assert 0.0 <= tight.x0 and tight.x1 <= 0.5
    assert 0.5 <= tight.y0 and tight.y1 <= 1.0

    # ---- 2 Lined up on cc, without the bands -----------------------------------------
    _, ax = _spectrum_drawer('P3', {'align_haem': 'cytcc', 'haem_bands': 'no'})
    drawn = [line.get_ydata() for line in ax.lines]
    assert [(values[0], values[10], values[12]) for values in drawn] == [
        (4.0, 6.0, 9.0),
        (-8.0, 0.0, -6.0),
        ]
    assert not ax.patches

    # ---- 3 Nothing to show -----------------------------------------------------------
    only_bad = {'a4': _spectrum_experiments_maker()['a4']}
    _, ax = _spectrum_drawer('P3', {}, only_bad)
    assert not ax.axison
    assert ' '.join(ax.texts[0].get_text().split()) == NO_WATERFALL


# ---- test_the_forms_of_the_plots_over_time -------------------------------------------
def test_the_forms_of_the_plots_over_time() -> None:
    """
    ---- Summary ----
    Main function to check what the forms of a Single trace and of a Mean trace ask
    and how they start: the OCR as % of baseline, the haems as ΔD, Δψ in mV, time 0
    at the first addition; for a Single trace the experiment, the labels on and the
    regions off; for a Mean trace the group drop-downs, split by Group 1, the SEM
    and the labels on; the OCR per OD only in a run with OD values; no question
    about the haems or Δψ in a run without them; and what the roles hold is kept.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _series_setup_maker
    experiment_role_maker
    """

    # ---- 1 A Single trace ------------------------------------------------------------
    setup = _series_setup_maker()
    fields = form_fields_lister('P7', setup, {}, _answers_maker())
    assert [(field['key'], field['label'], field['value']) for field in fields[1:]] == [
        ('trace', 'Trace', 'vo2'),
        ('vo2_value', 'OCR shown as', 'baseline'),
        ('haem_view', 'Haems shown as', 'delta'),
        ('delta_psi_value', 'Δψ shown as', 'raw'),
        ('time_zero', 'Time 0 at', 'addition 1'),
        ('addition_labels', 'Labels of the additions', 'yes'),
        ('regions_shaded', 'Averaging regions shaded', 'no'),
        ]
    assert fields[0]['key'] == 'experiment'
    assert fields[0]['value'] == experiment_role_maker(setup, 'a1')
    assert fields[1]['choices'] == [('oxygen', 'O₂'),
                                    ('vo2', 'OCR'),
                                    ('haem_cytbh', 'Cyt bH'),
                                    ('haem_cytcc', 'Cyt cc'),
                                    ('delta_psi', 'Δψ'),
                                    ]
    assert fields[2]['choices'] == [('baseline', '% of baseline'),
                                    ('raw', 'As measured'),
                                    ('change', 'Change from baseline'),
                                    ]
    assert fields[4]['choices'] == [('raw', 'mV'), ('change', 'Change from baseline')]
    assert fields[5]['choices'][:3] == [('start', 'The start of the recording'),
                                        ('addition 1', 'Addition 1'),
                                        ('addition 2', 'Addition 2'),
                                        ]
    assert len(fields[5]['choices']) == 11
    with_od = form_fields_lister('P7', setup, {}, _answers_maker(normalise_od=True))
    assert with_od[2]['choices'][-1] == ('od', 'Per OD')
    plain = form_fields_lister('P7',
                               setup,
                               {},
                               _answers_maker(decompose=False, delta_psi=False),
                               )
    assert [field['key'] for field in plain] == ['experiment',
                                                 'trace',
                                                 'vo2_value',
                                                 'time_zero',
                                                 'addition_labels',
                                                 'regions_shaded',
                                                 ]
    assert plain[1]['choices'] == [('oxygen', 'O₂'), ('vo2', 'OCR')]

    # ---- 2 A Mean trace --------------------------------------------------------------
    fields = form_fields_lister('P8', setup, {}, _answers_maker())
    assert [(field['key'], field['value']) for field in fields] == [('trace', 'vo2'),
                                                                    ('vo2_value',
                                                                     'baseline',
                                                                     ),
                                                                    ('haem_view',
                                                                     'delta',
                                                                     ),
                                                                    ('delta_psi_value',
                                                                     'raw',
                                                                     ),
                                                                    ('group_1',
                                                                     'Split',
                                                                     ),
                                                                    ('time_point',
                                                                     'All together',
                                                                     ),
                                                                    ('time_zero',
                                                                     'addition 1',
                                                                     ),
                                                                    ('band', 'sem'),
                                                                    ('addition_labels',
                                                                     'yes',
                                                                     ),
                                                                    ]
    assert fields[7]['choices'] == [('sem', 'SEM'), ('sd', 'SD'), ('none', 'None')]
    kept = {'trace': 'haem_cytcc',
            'haem_view': 'percent',
            'time_zero': 'start',
            'band': 'sd',
            'group_1': 'Only label 2',
            }
    fields = form_fields_lister('P8', setup, kept, _answers_maker())
    values = {field['key']: field['value'] for field in fields}
    assert {key: values[key] for key in kept} == kept
    # a role this run does not have starts afresh
    stale = {'trace': 'haem_cyta', 'vo2_value': 'od', 'band': 'range'}
    fields = form_fields_lister('P8', setup, stale, _answers_maker())
    values = {field['key']: field['value'] for field in fields}
    assert (values['trace'], values['vo2_value'], values['band']) == ('vo2',
                                                                      'baseline',
                                                                      'sem',
                                                                      )


# ---- test_a_single_trace_drawn -------------------------------------------------------
def test_a_single_trace_drawn() -> None:
    """
    ---- Summary ----
    Main function to check a Single trace as drawn, worked out by hand: the OCR of
    one experiment as measured, its time counted from its first addition, in the
    colour of the OCR, with a dashed line and a label at each addition, no legend
    and everything inside its cells; as % of baseline when the roles say nothing;
    its time from the start, from the second addition and from an addition it does
    not have; the regions shaded as a backdrop; and the sentences of a plot that
    cannot be drawn.

    ---- Inputs ----
    None.

    ---- Globals read ----
    NO_SUCH_ROLE; NO_TRACE, NOT_READ, NOT_THERE (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    a1 runs from 0 to 20 min with additions at 10 and 16 min; its OCR is 4 before
    10 min and 2 from then on. From its first addition, t = x - 10: the trace runs
    from -10 to 10, is 4 at -1 and 2 at 1, and its additions are at 0 and 6. From
    its second (or from a fifth it does not have, taken as its last), t = x - 16:
    -16 to 4. Its baseline region, 2 to 8 min, is at -8 to -2; its settled region,
    11 to 13 min, at 1 to 3.

    ---- Helpers ----
    _series_setup_maker
    _spectrum_drawer
    _trace_experiments_maker
    _value_finder
    experiment_role_maker
    """

    # ---- 1 As measured, from the first addition --------------------------------------
    experiments = _trace_experiments_maker()
    role = {'experiment': experiment_role_maker(_series_setup_maker(), 'a1')}
    fig, ax = _spectrum_drawer('P7', dict(role, vo2_value='raw'), experiments)
    trace = ax.lines[0]
    times, values = trace.get_xdata(), trace.get_ydata()
    assert (times[0], times[-1]) == (-10.0, 10.0)
    assert _value_finder(times, values, -1.0) == 4.0
    assert _value_finder(times, values, 1.0) == 2.0
    assert trace.get_color() == settings.TRACE_COLOURS['OCR']
    assert [line.get_xdata()[0] for line in ax.lines[1:]] == [0.0, 6.0]
    assert [line.get_linestyle() for line in ax.lines[1:]] == ['--', '--']
    assert [text.get_text() for text in ax.texts] == ['add 1', 'add 2']
    assert ax.get_xlim() == (-10.0, 10.0)
    assert ax.get_xlabel() == 'Time from addition 1 (minutes)'
    assert ax.get_ylabel() == 'OCR (µM min$^{-1}$)'
    assert ax.get_legend() is None and not ax.patches
    tight = ax.get_tightbbox(fig._get_renderer()).transformed(
        fig.transFigure.inverted(),
        )
    assert 0.0 <= tight.x0 and tight.x1 <= 0.5
    assert 0.5 <= tight.y0 and tight.y1 <= 1.0

    # ---- 2 As a new plot starts, and its other times ---------------------------------
    _, ax = _spectrum_drawer('P7', role, experiments)
    assert ax.get_ylabel() == 'OCR (% of baseline)'
    assert _value_finder(*ax.lines[0].get_data(), -1.0) == 100.0
    assert _value_finder(*ax.lines[0].get_data(), 1.0) == 50.0
    _, ax = _spectrum_drawer('P7', dict(role, time_zero='start'), experiments)
    assert ax.get_xlim() == (0.0, 20.0) and ax.get_xlabel() == 'Time (minutes)'
    assert [line.get_xdata()[0] for line in ax.lines[1:]] == [10.0, 16.0]
    for moment in ('addition 2', 'addition 5'):
        _, ax = _spectrum_drawer('P7', dict(role, time_zero=moment), experiments)
        assert ax.get_xlim() == (-16.0, 4.0)
        assert ax.get_xlabel() == 'Time from addition 2 (minutes)'

    # ---- 3 The regions, without the labels -------------------------------------------
    ticked = dict(role, regions_shaded='yes', addition_labels='no')
    _, ax = _spectrum_drawer('P7', ticked, experiments)
    assert [(span.get_x(), span.get_x() + span.get_width())
            for span in ax.patches
            ] == [(-8.0, -2.0), (1.0, 3.0)]
    assert all(getattr(span, BACKDROP_MARK, False) for span in ax.patches)
    assert not ax.texts

    # ---- 4 What cannot be drawn ------------------------------------------------------
    sentences = (({'experiment': NO_SUCH_ROLE}, experiments, NOT_THERE),
                 (role, {}, NOT_READ.format('a1')),
                 (dict(role, trace='haem_cytbh'), experiments, NO_TRACE.format('a1')),
                 )
    for roles, slim_copies, sentence in sentences:
        _, ax = _spectrum_drawer('P7', roles, slim_copies)
        assert not ax.axison
        assert ' '.join(ax.texts[0].get_text().split()) == sentence


# ---- test_the_lines_of_a_mean_trace --------------------------------------------------
def test_the_lines_of_a_mean_trace() -> None:
    """
    ---- Summary ----
    Main function to check the lines of a Mean trace, worked out by hand: one line
    per group, the mean of its experiments lined up on their additions, with the
    SEM, the SD or no band; an experiment with another number of additions left
    out and named; the sets split by time point, in their shades; and the
    experiments the plots of a page leave out.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BLUE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    a4 has one addition and the others two, so it is left out. The gaps are 6 (a1)
    and 5 min (a2, a3, k1): the additions are at 0 and 5, with a break at 2.5. The
    shortest run before the first addition is 10 min and after the last 4 (a1):
    the times run from -10 to 9. The controls a1, a2, a3 are 4, 6, 2 before their
    first addition: mean 4, SD sqrt((0 + 4 + 4) / 2) = 2, SEM 2 / sqrt(3) = 1.1547;
    and 2, 3, 1 after: mean 2, SD 1, SEM 0.5774. k1 alone is 10 then 5, with no
    spread. As % of baseline every experiment is 100 then 50. Split by time point,
    2 h is a1 and a2: mean 5 then 2.5, SD sqrt(2) = 1.4142 then 0.7071; 7 h is a3
    alone, in blue with 0.7 of white (#b2d5e8).

    ---- Helpers ----
    _answers_maker
    _series_setup_maker
    _trace_experiments_maker
    _value_finder
    """

    # ---- 1 Split by group, as measured -----------------------------------------------
    setup, experiments = _series_setup_maker(), _trace_experiments_maker()
    answers = _answers_maker()
    found = mean_lines_lister(setup, {'vo2_value': 'raw'}, experiments, answers)
    times = found['times_min']
    assert (times[0], times[-1]) == (-10.0, 9.0)
    assert found['additions_min'] == [0.0, 5.0] and found['breaks_min'] == [2.5]
    assert found['left_out'] == ['a4']
    assert found['label'] == 'OCR (µM min$^{-1}$)'
    assert [event['label'] for event in found['events']] == ['add 1', 'add 2']
    control, knockdown = found['lines']
    assert (control['label'], control['colour']) == ('control (n = 3)', BLUE)
    assert (knockdown['label'], knockdown['colour']) == ('knockdown (n = 1)', '#d55e00')
    for moment, mean, error in ((-1.0, 4.0, 1.1547005),
                                (1.0, 2.0, 0.5773503),
                                (4.5, 2.0, 0.5773503),
                                ):
        assert _value_finder(times, control['mean'], moment) == pytest.approx(mean)
        assert _value_finder(times, control['spread'], moment) == pytest.approx(error)
    assert _value_finder(times, knockdown['mean'], -1.0) == 10.0
    assert _value_finder(times, knockdown['mean'], 1.0) == 5.0
    assert np.isnan(knockdown['spread']).all()

    # ---- 2 The SD, no band, and % of baseline ----------------------------------------
    roles = {'vo2_value': 'raw', 'band': 'sd'}
    control = mean_lines_lister(setup, roles, experiments, answers)['lines'][0]
    assert _value_finder(times, control['spread'], -1.0) == pytest.approx(2.0)
    assert _value_finder(times, control['spread'], 1.0) == pytest.approx(1.0)
    roles = {'vo2_value': 'raw', 'band': 'none'}
    lines = mean_lines_lister(setup, roles, experiments, answers)['lines']
    assert [line['spread'] for line in lines] == [None, None]
    found = mean_lines_lister(setup, {}, experiments, answers)
    assert found['label'] == 'OCR (% of baseline)'
    for line in found['lines']:
        assert _value_finder(times, line['mean'], -1.0) == pytest.approx(100.0)
        assert _value_finder(times, line['mean'], 1.0) == pytest.approx(50.0)

    # ---- 3 Split by time point -------------------------------------------------------
    roles = {'vo2_value': 'raw',
             'band': 'sd',
             'group_1': 'Only label 1',
             'time_point': 'Split',
             }
    found = mean_lines_lister(setup, roles, experiments, answers)
    early, late = found['lines']
    assert (early['label'], early['colour']) == ('2 h (n = 2)', BLUE)
    assert (late['label'], late['colour']) == ('7 h (n = 1)', '#b2d5e8')
    assert _value_finder(times, early['mean'], -1.0) == pytest.approx(5.0)
    assert _value_finder(times, early['mean'], 1.0) == pytest.approx(2.5)
    assert _value_finder(times, early['spread'], -1.0) == pytest.approx(1.4142136)
    assert _value_finder(times, early['spread'], 1.0) == pytest.approx(0.7071068)
    assert _value_finder(times, late['mean'], -1.0) == 2.0

    # ---- 4 What a page leaves out ----------------------------------------------------
    page = FigurePage()
    for row, plot_roles in enumerate(({}, roles, {'group_1': 'Only label 2'})):
        page = plot_placer(page, PagePlot('P8', row=row, column=0, roles=plot_roles))
    assert traces_left_out_lister(page, setup, experiments, answers) == ['a4']
    page = plot_placer(FigurePage(), PagePlot('P8', 0, 0, roles={'trace': 'oxygen'}))
    assert traces_left_out_lister(page, setup, experiments, answers) == list(OCR_RUNS)
    page = plot_placer(FigurePage(),
                       PagePlot('P8', 0, 0, roles={'group_1': 'Only label 2'}),
                       )
    assert traces_left_out_lister(page, setup, experiments, answers) == []


# ---- test_a_mean_trace_drawn ---------------------------------------------------------
def test_a_mean_trace_drawn() -> None:
    """
    ---- Summary ----
    Main function to check a Mean trace as drawn: a named line per group, broken at
    the break, with a band only for the group of more than one experiment; a dashed
    line and a label at each addition and a break mark on the time axis; its own
    small legend, and everything inside its cells; no labels when unticked; and the
    sentence of a plot with nothing to show.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BLUE; NO_MEAN (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The numbers of test_the_lines_of_a_mean_trace: the controls are 4 at -1 min and
    2 at 1 min, the knockdown 10 and 5. The times run from -10 to 9 min, one every
    second: 19 x 60 + 1 = 1141, and 1142 with the empty point of the break at 2.5.

    ---- Helpers ----
    _spectrum_drawer
    _trace_experiments_maker
    _value_finder
    """

    # ---- 1 The lines, the band, the additions and the break --------------------------
    experiments = _trace_experiments_maker()
    fig, ax = _spectrum_drawer('P8', {'vo2_value': 'raw'}, experiments)
    named = [line for line in ax.lines if not line.get_label().startswith('_')]
    assert [line.get_label() for line in named] == ['control (n = 3)',
                                                    'knockdown (n = 1)',
                                                    ]
    assert [line.get_color() for line in named] == [BLUE, '#d55e00']
    for line, (before, after) in zip(named, ((4.0, 2.0), (10.0, 5.0))):
        times, values = line.get_data()
        assert len(times) == 1142 and np.isnan(values).sum() == 1
        assert np.isnan(values[np.flatnonzero(np.isclose(times, 2.5))[0]])
        assert _value_finder(times, values, -1.0) == pytest.approx(before)
        assert _value_finder(times, values, 1.0) == pytest.approx(after)
    others = [line for line in ax.lines if line not in named]
    assert [line.get_xdata()[0] for line in others] == [0.0, 5.0]
    assert len(ax.collections) == 1  # the band of the controls; one knockdown has none
    assert [text.get_text() for text in ax.texts] == ['add 1', 'add 2', '//']
    assert ax.get_xlim() == (-10.0, 9.0)
    assert ax.get_xlabel() == 'Time from addition 1 (minutes)'
    assert ax.get_ylabel() == 'OCR (µM min$^{-1}$)'
    assert ax.get_legend() is not None
    tight = ax.get_tightbbox(fig._get_renderer()).transformed(
        fig.transFigure.inverted(),
        )
    assert 0.0 <= tight.x0 and tight.x1 <= 0.5
    assert 0.5 <= tight.y0 and tight.y1 <= 1.0

    # ---- 2 Without the labels, and from the start ------------------------------------
    roles = {'vo2_value': 'raw', 'addition_labels': 'no'}
    _, ax = _spectrum_drawer('P8', roles, experiments)
    assert [text.get_text() for text in ax.texts] == ['//']
    _, ax = _spectrum_drawer('P8', {'time_zero': 'start'}, experiments)
    assert ax.get_xlim() == (0.0, 20.0) and ax.get_xlabel() == 'Time (minutes)'
    assert not ax.texts
    assert [line.get_label() for line in ax.lines] == ['control (n = 4)',
                                                       'knockdown (n = 1)',
                                                       ]

    # ---- 3 Nothing to show -----------------------------------------------------------
    _, ax = _spectrum_drawer('P8', {'trace': 'oxygen'}, experiments)
    assert not ax.axison
    assert ' '.join(ax.texts[0].get_text().split()) == NO_MEAN


# ---- test_a_waterfall_of_traces ------------------------------------------------------
def test_a_waterfall_of_traces() -> None:
    """
    ---- Summary ----
    Main function to check a Waterfall that stacks a trace in place of the
    difference spectrum, worked out by hand: as a time series, one line per time
    point, the mean of its replicates lined up on their additions; as experiments,
    one line each, lighter down the stack; the experiment left out, named by the
    list of the traces and not by that of the spectra; and the stack as drawn.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BLUE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The controls a1, a2 and a3 have two additions (a4, with one, is left out): the
    times run from -10 to 9 min. 2 h is the mean of a1 and a2: 5 before the first
    addition and 2.5 after; 7 h is a3: 2 and 1. Each is moved so its highest point
    is at 0: 0 and -2.5, 2.5 high; 0 and -1, 1 high. The gap is 0.75 x 2.5 = 1.875,
    so 2 h is drawn at 1.875 and -0.625, and 7 h stays at 0 and -1. The y range is
    -1 to 1.875 with 2 % of 2.875 at each end: -1.0575 to 1.9325.

    ---- Helpers ----
    _answers_maker
    _series_setup_maker
    _spectrum_drawer
    _trace_experiments_maker
    _value_finder
    """

    # ---- 1 The lines -----------------------------------------------------------------
    setup, experiments = _series_setup_maker(), _trace_experiments_maker()
    answers = _answers_maker()
    roles = {'trace': 'vo2', 'vo2_value': 'raw'}
    found = waterfall_traces_lister(setup, roles, experiments, answers)
    times = found['times_min']
    assert (times[0], times[-1]) == (-10.0, 9.0) and found['left_out'] == ['a4']
    assert [(line['label'], line['colour']) for line in found['lines']] == [
        ('2 h (n = 2)', BLUE),
        ('7 h (n = 1)', '#b2d5e8'),
        ]
    assert [(_value_finder(times, line['values'], -1.0),
             _value_finder(times, line['values'], 1.0),
             )
            for line in found['lines']
            ] == [(5.0, 2.5), (2.0, 1.0)]
    each = dict(roles, time_point='All together')
    found = waterfall_traces_lister(setup, each, experiments, answers)
    assert [(line['label'], line['colour']) for line in found['lines']] == [
        ('a1', BLUE),
        ('a2', '#59a3cd'),
        ('a3', '#b2d5e8'),
        ]
    page = plot_placer(FigurePage(), PagePlot('P3', row=0, column=0, roles=roles))
    assert waterfall_left_out_lister(page, setup, experiments) == []
    assert traces_left_out_lister(page, setup, experiments, answers) == ['a4']

    # ---- 2 The stack as drawn --------------------------------------------------------
    _, ax = _spectrum_drawer('P3', roles, experiments)
    named = [line for line in ax.lines if not line.get_label().startswith('_')]
    assert [line.get_label() for line in named] == ['2 h (n = 2)', '7 h (n = 1)']
    assert [(_value_finder(*line.get_data(), -1.0), _value_finder(*line.get_data(), 1.0))
            for line in named
            ] == [(1.875, -0.625), (0.0, -1.0)]
    assert ax.get_ylim() == pytest.approx((-1.0575, 1.9325))
    assert list(ax.get_yticks()) == []
    assert ax.get_xlabel() == 'Time from addition 1 (minutes)'
    assert ax.get_ylabel() == 'OCR (µM min$^{-1}$), stacked'
    assert [text.get_text() for text in ax.texts] == ['add 1', 'add 2', '//']
    assert not ax.patches  # no haem bands behind traces
