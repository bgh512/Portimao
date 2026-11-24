"""
Tests of the standard plot of one experiment on a made-up file, drawn off screen: its
panels and their order, its time axis, the colours of its lines, its shared legend,
its baseline window and its OCR as % of baseline.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_hex
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.averaging import (baseline_percent_adder,
                                    experiment_averages_calculator,
                                    )
from utils_shared.figure_layout import stack_legend_drawer
from utils_shared.individual_experiment_plotter import (experiment_drawer,
                                                        haem_ylim_sharer,
                                                        )
from utils_shared.schema import HAEM_KEYS, TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
# the haems in an order no file should be drawn in: c, then b, then a
HAEMS_GIVEN = ['Cyt cc', 'Cyt bL', 'Cyt bH', 'Cyt a605']
HAEMS_DRAWN = ['Cyt a605', 'Cyt bH', 'Cyt bL', 'Cyt cc']


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _plot_drawer --------------------------------------------------------------------
def _plot_drawer(asked: Optional[List[str]] = None,
                 has_haems: bool = True,
                 source: str = 'delta_abs',
                 steps: Optional[List[float]] = None,
                 **changed: object,
                 ) -> list:
    """
    ---- Summary ----
    Helper function to draw the standard plot of a made-up file: oxygen and OCR from 0
    to 30 min, four haems from 5 to 25 min only, listed in the order c, b, b, a.

    ---- Inputs ----
    asked : Optional[List[str]]
        The haems the plot is asked to show; None asks for the four of the file.
    has_haems : bool
        False makes a file whose haems were not worked out.
    source : str
        Key of schema.HAEM_KEYS the haem panels show ('delta_abs', 'abs', 'percent').
    steps : Optional[List[float]]
        How far each haem, in the order of HAEMS_GIVEN, rises from 5 to 25 min, in a
        straight line from its level i; None for haems that stay at i.
    **changed : object
        Answers that differ from the standard ones (plot_o2=False).

    ---- Globals read ----
    HAEMS_GIVEN, HAEM_KEYS, TIME_COLUMN.

    ---- Outputs ----
    list
        (panel specification, axes) of each panel, top first.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_drawer
    """

    # ---- 1 The made-up file ----------------------------------------------------------
    times = np.arange(0.0, 31.0)
    haem_times = np.arange(5.0, 26.0)
    haems = pd.DataFrame({TIME_COLUMN: haem_times})
    for i, name in enumerate(HAEMS_GIVEN):
        rise = 0.0 if steps is None else steps[i]
        haems[name] = float(i) + rise * (haem_times - 5.0) / 20.0
    experiment = {'experiment_name': 'made_up',
                  'CsO2': pd.DataFrame({TIME_COLUMN: times, 'Set O2': 60.0}),
                  'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 50.0}),
                  'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': 1.0}),
                  'metadata': {'events': []},
                  }
    if has_haems:
        experiment[HAEM_KEYS[source]] = haems

    # ---- 2 Its plot ------------------------------------------------------------------
    answers = dict(settings.DEFAULT_ANSWERS)
    answers.update({'decompose': True,
                    'plot_haems': True,
                    'haems': list(HAEMS_GIVEN if asked is None else asked),
                    **changed,
                    },
                   )
    config = settings.Config(answers).plot_config_builder('raw', source, 0.0, 0.0)
    fig = Figure()
    axes, panels = experiment_drawer(fig,
                                     fig.add_gridspec(1, 1)[0, 0],
                                     experiment,
                                     config,
                                     )
    return list(zip(panels, axes))


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_a_plot_that_cannot_show_its_haems_says_so_plainly --------------------------
def test_a_plot_that_cannot_show_its_haems_says_so_plainly(
    capsys: pytest.CaptureFixture,
    ) -> None:
    """
    ---- Summary ----
    Main function to check what the plot says when it cannot show the haems, in words
    the user knows: a haem asked for that the file does not have is named and the
    others are drawn; a file whose haems were not worked out is drawn without them;
    and a file left with nothing to plot is refused in one sentence.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _plot_drawer
    """

    # ---- 1 One haem the file does not have -------------------------------------------
    drawn = _plot_drawer(asked=['Cyt bH', 'Cyt d'])
    assert [panel['type'] for panel, _ in drawn] == ['oxygen', 'vo2', 'haem']
    assert capsys.readouterr().out.strip() == (
        'Warning: Cyt d is not among the haems worked out for this file, so it is not '
        'on the plot.'
        )

    # ---- 2 Haems that were not worked out --------------------------------------------
    drawn = _plot_drawer(has_haems=False)
    assert [panel['type'] for panel, _ in drawn] == ['oxygen', 'vo2']
    assert capsys.readouterr().out.strip() == (
        'Warning: the haems are not on this plot, as they could not be worked out for '
        'this file.'
        )

    # ---- 3 Nothing left to plot ------------------------------------------------------
    with pytest.raises(ValueError) as caught:
        _plot_drawer(asked=['Cyt d', 'Cyt o'], plot_o2=False, plot_ocr=False)
    assert str(caught.value) == ('there is nothing to plot for this file: the oxygen '
                                 'and the OCR are not shown, and it has none of the '
                                 'haems to show.'
                                 )
    assert capsys.readouterr().out.strip() == (
        'Warning: Cyt d, Cyt o are not among the haems worked out for this file, so '
        'they are not on the plot.'
        )


# ---- test_the_baseline_has_its_colour_and_name_and_the_OCR_its_percent ---------------
def test_the_baseline_has_its_colour_and_name_and_the_OCR_its_percent() -> None:
    """
    ---- Summary ----
    Main function to check the plot of a made-up file with averaging windows: the
    baseline window is shaded in its own colour on every panel, with "Baseline"
    written above the top panel, the settled window stays blue, and the OCR asked for
    as % of baseline is drawn in % with its axis saying so.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.BASELINE_WINDOW_COLOURS, settings.DEFAULT_ANSWERS; TIME_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A point a minute from 0 to 30 min, one addition at 10 min, windows 2 min long
    ending 0.5 min before: the baseline 7.5 to 9.5 min, the settled window 27.5 to
    29.5 min. The OCR is 10 before 10 min and 6 after, so b = 10 and the OCR in % of
    baseline is 100 then 60.

    ---- Helpers ----
    baseline_percent_adder
    experiment_averages_calculator
    experiment_drawer
    """

    # ---- 1 The made-up file, averaged ------------------------------------------------
    times = np.arange(0.0, 30.25, 0.25)
    experiment = {'experiment_name': 'made_up',
                  'CsO2': pd.DataFrame({TIME_COLUMN: times, 'Set O2': 60.0}),
                  'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 50.0}),
                  'VoO2': pd.DataFrame({TIME_COLUMN: times,
                                        'VoO2': np.where(times < 10, 10.0, 6.0),
                                        },
                                       ),
                  'metadata': {'events': [{'time': 10.0, 'label': 'addition'}]},
                  }
    experiment_averages_calculator(experiment,
                                   window_minutes=2.0,
                                   gap_minutes=0.5,
                                   final_window_gap_minutes=0.5,
                                   baseline_minimum_seconds=10.0,
                                   vo2_source='raw',
                                   haem_source=None,
                                   )
    assert baseline_percent_adder(experiment) is True

    # ---- 2 Its plot ------------------------------------------------------------------
    answers = dict(settings.DEFAULT_ANSWERS, averaging=True, plot_haems=False)
    config = settings.Config(answers).plot_config_builder('baseline', None, 0.0, 0.0)
    fig = Figure()
    axes, panels = experiment_drawer(fig,
                                     fig.add_gridspec(1, 1)[0, 0],
                                     experiment,
                                     config,
                                     )
    assert [panel['type'] for panel in panels] == ['oxygen', 'vo2']

    # ---- 3 The OCR in % of baseline --------------------------------------------------
    (ocr_line,) = [line for line in axes[1].get_lines() if line.get_label() == 'OCR']
    values = np.asarray(ocr_line.get_ydata(), dtype=float)
    assert values[0] == pytest.approx(100.0) and values[-1] == pytest.approx(60.0)
    assert axes[1].get_ylabel().replace('\n', ' ') == 'OCR (% of baseline)'

    # ---- 4 The windows: the baseline gold and named, the settled one blue ------------
    gold, gold_edge = settings.BASELINE_WINDOW_COLOURS
    for ax in axes:
        faces = [to_hex(patch.get_facecolor()) for patch in ax.patches]
        assert faces == [to_hex(gold), to_hex(config['AVERAGING_WINDOW_COLOUR'])]
    names = [text for text in axes[0].texts if text.get_text() == 'Baseline']
    assert len(names) == 1
    assert names[0].get_position()[0] == pytest.approx(8.5)  # the middle of 7.5 to 9.5
    assert to_hex(names[0].get_color()) == to_hex(gold_edge)
    assert not [text for text in axes[1].texts if text.get_text() == 'Baseline']


# ---- test_the_lines_take_the_colours_of_the_settings ---------------------------------
def test_the_lines_take_the_colours_of_the_settings() -> None:
    """
    ---- Summary ----
    Main function to check that the set oxygen, the measured oxygen and the OCR lines
    are drawn in the colours of the settings, not the plotting library's own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.TRACE_COLOURS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _plot_drawer
    """

    drawn = _plot_drawer()
    set_line, measured_line = drawn[0][1].get_lines()
    (ocr_line,) = drawn[1][1].get_lines()
    colours = settings.TRACE_COLOURS
    assert to_hex(set_line.get_color()) == colours['set_O2']
    assert to_hex(measured_line.get_color()) == colours['measured_O2']
    assert to_hex(ocr_line.get_color()) == colours['OCR']
    assert ocr_line.get_label() == 'OCR'


# ---- test_the_panels_are_oxygen_then_OCR_then_the_haems_a_b_c ------------------------
def test_the_panels_are_oxygen_then_OCR_then_the_haems_a_b_c() -> None:
    """
    ---- Summary ----
    Main function to check the panels of the standard plot: the set and measured
    oxygen, then the OCR, then one panel per haem with every a haem first, then every
    b, then every c, though the haems were listed c, b, b, a.

    ---- Inputs ----
    None.

    ---- Globals read ----
    HAEMS_DRAWN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _plot_drawer
    """

    drawn = _plot_drawer()
    kinds = [panel['type'] for panel, _ in drawn]
    assert kinds == ['oxygen', 'vo2', 'haem', 'haem', 'haem', 'haem']
    assert [panel['haems'] for panel, _ in drawn[2:]] == [[name] for name in HAEMS_DRAWN]


# ---- test_the_shared_legend_leaves_the_OCR_out ---------------------------------------
def test_the_shared_legend_leaves_the_OCR_out() -> None:
    """
    ---- Summary ----
    Main function to check that the one legend of a stack of panels holds the set and
    measured oxygen and each haem, and not the OCR, whatever the OCR axis is titled.

    ---- Inputs ----
    None.

    ---- Globals read ----
    HAEMS_DRAWN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _plot_drawer
    stack_legend_drawer
    """

    drawn = _plot_drawer()
    axes = [ax for _, ax in drawn]
    axes[1].set_ylabel('Oxygen used')  # the legend must not go by this title
    config = {'LEGEND_FONT_SIZE': 6, 'LEGEND_FRAME': False}
    legend = stack_legend_drawer(axes, config)
    labels = [text.get_text() for text in legend.get_texts()]
    assert labels == ['Set [O$_2$]', 'Measured [O$_2$]'] + HAEMS_DRAWN


# ---- test_the_time_axis_covers_every_panel -------------------------------------------
def test_the_time_axis_covers_every_panel() -> None:
    """
    ---- Summary ----
    Main function to check that the time axis runs over the longest panel: the oxygen
    and OCR last from 0 to 30 min and the haems, in the lowest panels, only from 5 to
    25 min, so every panel must show 0 to 30 min.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _plot_drawer
    """

    for _, ax in _plot_drawer():
        assert ax.get_xlim() == (0.0, 30.0)


# ---- test_the_haem_panels_share_one_scale --------------------------------------------
def test_the_haem_panels_share_one_scale() -> None:
    """
    ---- Summary ----
    Main function to check that the haem panels share one scale, so a haem that hardly
    changes looks small beside the others: in ΔD the same range on every panel; in
    absorbance the same height of range, around each haem; in % oxidised each its own.
    Worked out by hand.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The haems cc, bL, bH, a605 start at 0, 1, 2, 3 and rise by -5, 1, 0.2, 2 from 5 to
    25 min. Alone, each panel reaches 5 % of its change beyond it:
    cc (-5.25, 0.25), bL (0.95, 2.05), bH (1.99, 2.21), a605 (2.9, 5.1).
    ΔD: every panel from the lowest low to the highest high, (-5.25, 5.1).
    Absorbance: every panel 5.5 high (that of cc), around its own middle:
    cc -2.5 (-5.25, 0.25), bL 1.5 (-1.25, 4.25), bH 2.1 (-0.65, 4.85),
    a605 4 (1.25, 6.75).

    ---- Helpers ----
    _plot_drawer
    haem_ylim_sharer
    """

    # ---- 1 By hand -------------------------------------------------------------------
    alone = {'Cyt cc': (-5.25, 0.25),
             'Cyt bL': (0.95, 2.05),
             'Cyt bH': (1.99, 2.21),
             'Cyt a605': (2.9, 5.1),
             }
    by_height = {'Cyt cc': (-5.25, 0.25),
                 'Cyt bL': (-1.25, 4.25),
                 'Cyt bH': (-0.65, 4.85),
                 'Cyt a605': (1.25, 6.75),
                 }
    assert haem_ylim_sharer([(0.0, 1.0), (2.0, 5.0)], True) == [(0.0, 5.0),
                                                                (0.0, 5.0),
                                                                ]
    assert haem_ylim_sharer([(0.0, 1.0), (2.0, 5.0)], False) == [(-1.0, 2.0),
                                                                 (2.0, 5.0),
                                                                 ]
    assert haem_ylim_sharer([], True) == []

    # ---- 2 On the plot, in each way of showing the haems -----------------------------
    steps = [-5.0, 1.0, 0.2, 2.0]
    for source, expected in (('delta_abs', {name: (-5.25, 5.1) for name in alone}),
                             ('abs', by_height),
                             ('percent', alone),
                             ):
        panels = _plot_drawer(source=source, steps=steps)
        found = {panel['haems'][0]: ax.get_ylim()
                 for panel, ax in panels
                 if panel['type'] == 'haem'
                 }
        assert set(found) == set(expected), source
        for name, limits in expected.items():
            assert found[name] == pytest.approx(limits), (source, name)
