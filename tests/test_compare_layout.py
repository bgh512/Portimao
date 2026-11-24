"""
Tests of how a decomposition kept to compare with is shown: side by side or overlaid.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Iterator

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import utils_viewer.viewer_preview as viewer_preview
import utils_viewer.viewer_stages as viewer_stages
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN
from utils_viewer.viewer_preview import (KEPT_ALPHA,
                                         preview_figure_builder,
                                         preview_picture_maker,
                                         PreviewSpec,
                                         SIDE_GAP_PX,
                                         SIDE_HEADING_PX,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_strip import kept_decomposition_builder


# ---- CONSTANTS -----------------------------------------------------------------------
HAEMS = ['Cyt a605', 'Cyt bH', 'Cyt cc']
# the kept haems lie this far above the haems in use (mOD) at every spectrum
KEPT_SHIFT = 2.0


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(shift: float) -> dict:
    """
    ---- Summary ----
    Helper function to make a file worked out with one decomposition: oxygen and OCR
    from 0 to 30 min, and three haems with a value each minute, haem i at
    i + 0.1 t + shift.

    ---- Inputs ----
    shift : float
        Added to every haem value (mOD).

    ---- Globals read ----
    HAEMS, SPECTRUM_INDEX_COLUMN, TIME_COLUMN.

    ---- Outputs ----
    dict
        The experiment, with its haems as 'haem_delta_abs'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(0.0, 31.0)
    haems = pd.DataFrame({TIME_COLUMN: times,
                          SPECTRUM_INDEX_COLUMN: np.arange(1, 32),
                          },
                         )
    for i, name in enumerate(HAEMS):
        haems[name] = i + 0.1 * times + shift
    return {'experiment_name': 'made_up',
            'CsO2': pd.DataFrame({TIME_COLUMN: times, 'Set O2': 60.0}),
            'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 50.0}),
            'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': 1.0}),
            'metadata': {'events': []},
            'haem_delta_abs': haems,
            }


# ---- _preview_drawer -----------------------------------------------------------------
def _preview_drawer(monkeypatch: pytest.MonkeyPatch,
                    tmp_path: Path,
                    layout: str,
                    ) -> Figure:
    """
    ---- Summary ----
    Helper function to draw the preview of a made-up file with a decomposition kept, as
    the window does. The reading and the processing are stood in for: the kept fit
    gives haems KEPT_SHIFT above those of the fit in use.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the reading and the processing.
    tmp_path : Path
        Pytest's folder for this test.
    layout : str
        The answer compare_layout: 'side' or 'overlaid'.

    ---- Globals read ----
    HAEMS, KEPT_SHIFT.

    ---- Outputs ----
    Figure
        The preview drawn.

    ---- Globals mutated ----
    None. The stand-ins are undone after the test.

    ---- Equations ----
    None.

    ---- Helpers ----
    _experiment_maker
    """

    # ---- processor -------------------------------------------------------------------
    def processor(info: dict, cfg: settings.Config, fit: dict, fresh: dict) -> dict:
        is_kept = cfg.answers['fit_file'] == 'kept.csv'
        return {'experiment': _experiment_maker(KEPT_SHIFT if is_kept else 0.0),
                'vo2_source': 'raw',
                'plotted_haem_source': 'delta_abs',
                'haem_source': 'delta_abs',
                }

    monkeypatch.setattr(viewer_preview, 'experiment_data_processor', processor)
    monkeypatch.setattr(viewer_preview,
                        '_loaded_experiment_getter',
                        lambda session, summary, dataset: {},
                        )

    @contextmanager
    def capturer() -> Iterator[SimpleNamespace]:
        yield SimpleNamespace(warnings=[])

    # ---- 2 A session with one file and a decomposition kept --------------------------
    summary = {'name': 'made_up', 'path': tmp_path / 'made_up.paf', 'duration_min': 30}
    session = ViewerSession([summary],
                            tmp_path,
                            SimpleNamespace(output_capturer=capturer),
                            )
    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   plot_haems=True,
                   haems=list(HAEMS),
                   compare_layout=layout,
                   )
    kept = kept_decomposition_builder(dict(answers, fit_file='kept.csv'),
                                      {'haem_list': list(HAEMS)},
                                      {},
                                      )
    spec = PreviewSpec(answers=answers,
                       limits={},
                       fit={'haem_list': list(HAEMS)},
                       details={},
                       kept=kept,
                       )
    fig, notes = preview_figure_builder(session, spec, 'made_up')
    assert fig is not None, notes
    fig.test_notes = notes
    return fig


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_side_by_side_draws_the_kept_plot_on_the_left -------------------------------
def test_side_by_side_draws_the_kept_plot_on_the_left(monkeypatch: pytest.MonkeyPatch,
                                                      tmp_path: Path,
                                                      ) -> None:
    """
    ---- Summary ----
    Main function to check the preview with a decomposition kept, side by side: the
    kept file drawn as a plot of its own of the same size with the same panels, no
    dashed lines on the plot in use, matching panels with the same y range holding
    both, and the key and the gaps worked out by hand.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the reading and the processing.
    tmp_path : Path
        Pytest's folder for this test.

    ---- Globals read ----
    HAEMS, KEPT_SHIFT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Each haem in use is i + 0.1 t and kept i + 0.1 t + 2 (mOD), so the gap is 2 mOD
    at every spectrum: largest 2, average 2. Haem i then reaches from i (in use, at
    0 min) to i + 3 + 2 = i + 5 (kept, at 30 min), and both panels hold that range.

    ---- Helpers ----
    _preview_drawer
    """

    # ---- 1 Two plots of the same size with the same panels ---------------------------
    fig = _preview_drawer(monkeypatch, tmp_path, 'side')
    kept_fig = fig.kept_figure
    assert tuple(kept_fig.get_size_inches()) == tuple(fig.get_size_inches())
    new_panels = {ax.panel_key: ax for ax in fig.axes if getattr(ax, 'panel_key', '')}
    kept_panels = {ax.panel_key: ax
                   for ax in kept_fig.axes
                   if getattr(ax, 'panel_key', '')
                   }
    assert list(new_panels) == list(kept_panels)

    # ---- 2 Nothing dashed on the plot in use, the same y range on both ---------------
    for key, ax in new_panels.items():
        assert ax.get_ylim() == kept_panels[key].get_ylim()
    for i, name in enumerate(HAEMS):
        lines = new_panels[f'haem:{name}'].get_lines()
        assert [line.is_dashed() for line in lines] == [False]
        low, high = new_panels[f'haem:{name}'].get_ylim()
        assert low <= i and high >= i + 3.0 + KEPT_SHIFT
    # the haems in ΔD keep one scale: the same range on every haem panel
    ranges = {new_panels[f'haem:{name}'].get_ylim() for name in HAEMS}
    assert len(ranges) == 1

    # ---- 3 The key and the gaps ------------------------------------------------------
    key, gaps = fig.test_notes.split('\n')
    assert key == 'Key: Old = kept, New = in use'
    assert gaps.startswith('Gap to the kept decomposition, largest / average')
    assert gaps.count(' 2 / 2') == len(HAEMS)


# ---- test_overlaid_draws_the_old_faint_and_the_new_bold ------------------------------
def test_overlaid_draws_the_old_faint_and_the_new_bold(monkeypatch: pytest.MonkeyPatch,
                                                       tmp_path: Path,
                                                       ) -> None:
    """
    ---- Summary ----
    Main function to check the preview with a decomposition kept, overlaid: one plot,
    each haem panel with the haem in use drawn bold and the kept one faint and thin
    under it, in the same colour, none dashed, and the key of the two.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the reading and the processing.
    tmp_path : Path
        Pytest's folder for this test.

    ---- Globals read ----
    HAEMS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _preview_drawer
    """

    fig = _preview_drawer(monkeypatch, tmp_path, 'overlaid')
    assert getattr(fig, 'kept_figure', None) is None
    for name in HAEMS:
        ax = next(ax for ax in fig.axes if getattr(ax, 'panel_key', '') == f'haem:{name}')
        new, old = ax.get_lines()
        assert not new.is_dashed() and not old.is_dashed()
        assert old.get_alpha() == KEPT_ALPHA and new.get_alpha() is None
        assert old.get_linewidth() < new.get_linewidth()
        assert old.get_color() == new.get_color()
        assert old.get_zorder() < new.get_zorder()
    assert fig.test_notes.split('\n')[0] == 'Key: faint = old (kept), bold = new'


# ---- test_the_picture_puts_the_plot_in_use_on_the_right ------------------------------
def test_the_picture_puts_the_plot_in_use_on_the_right() -> None:
    """
    ---- Summary ----
    Main function to check the picture shown side by side: the headings Old and New
    above, the kept plot on the left, a white gap, the plot in use on the right
    exactly as it is on its own, and the time axis of the plot in use moved into the
    whole picture, so the edges dragged, the arrows and the shading fall on the plot
    in use.

    ---- Inputs ----
    None.

    ---- Globals read ----
    SIDE_GAP_PX, SIDE_HEADING_PX.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With the kept plot k pixels wide, the gap g, the plot in use n wide and h high,
    under headings t high, in a picture W = k + g + n wide and H high:
    x' = (k + g + x n) / W and y' = (H - t - h + y h) / H. The kept plot here is wider
    and taller, so both change.

    ---- Helpers ----
    None.
    """

    # ---- 1 The plot in use, and a kept plot wider and taller -------------------------
    fig = Figure(figsize=(2.0, 1.0))
    ax = fig.add_axes((0.2, 0.1, 0.6, 0.8))
    ax.panel_key = 'oxygen'
    ax.set_xlim(0.0, 10.0)
    kept_fig = Figure(figsize=(3.0, 1.5))
    kept_fig.add_axes((0.1, 0.1, 0.8, 0.8))

    # ---- 2 On its own, then with the kept plot on its left ---------------------------
    alone, axis = preview_picture_maker(fig)
    fig.kept_figure = kept_fig
    joined, moved = preview_picture_maker(fig)
    plain = Image.open(io.BytesIO(alone)).convert('RGBA')
    picture = Image.open(io.BytesIO(joined)).convert('RGBA')
    n, h = plain.size
    width, height = picture.size
    k = width - SIDE_GAP_PX - n
    t = SIDE_HEADING_PX
    assert height > h + t and k > n
    assert picture.crop((k + SIDE_GAP_PX, t, width, t + h)).tobytes() == plain.tobytes()
    gap = picture.crop((k, t, k + SIDE_GAP_PX, height))
    assert set(gap.getdata()) == {(255, 255, 255, 255)}
    # a heading written above each plot
    for start, end in ((0, k), (k + SIDE_GAP_PX, width)):
        heading = picture.crop((start, 0, end, t))
        assert set(heading.getdata()) != {(255, 255, 255, 255)}

    # ---- 3 The time axis of the plot in use, in the whole picture --------------------
    assert moved.left == pytest.approx((k + SIDE_GAP_PX + axis.left * n) / width)
    assert moved.right == pytest.approx((k + SIDE_GAP_PX + axis.right * n) / width)
    assert moved.bottom == pytest.approx((height - t - h + axis.bottom * h) / height)
    assert moved.top == pytest.approx((height - t - h + axis.top * h) / height)
    assert (moved.start_min, moved.end_min) == (0.0, 10.0)
    assert [key for key, _, _ in moved.panels] == ['oxygen']
    assert moved.panels[0][1] == pytest.approx(moved.bottom)


# ---- test_the_switch_keeps_the_layout_and_redraws ------------------------------------
def test_the_switch_keeps_the_layout_and_redraws(monkeypatch: pytest.MonkeyPatch,
                                                 capsys: pytest.CaptureFixture,
                                                 ) -> None:
    """
    ---- Summary ----
    Main function to check a click on the switch beside Keep new: the layout is kept in
    the answers (so it is saved with the dataset) and said in the terminal, and the
    plot is redrawn only while a decomposition is kept. Side by side is the standard.
    The showing of the boxes is stood in for.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the showing of the boxes.
    capsys : pytest.CaptureFixture
        Pytest's capture of what is printed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. The stand-in is undone after the test.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Nothing kept: kept in the answers, no redraw ------------------------------
    assert settings.DEFAULT_ANSWERS['compare_layout'] == 'side'
    monkeypatch.setattr(viewer_stages, '_strip_shower', lambda session, answers: None)
    redraws = []
    session = ViewerSession(summaries=[], export_root=Path('.'), window=None)
    session.redraw = lambda: redraws.append(True) or True
    answers = dict(settings.DEFAULT_ANSWERS)
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {'compare_layout': 'overlaid'},
                                        )
    assert answers['compare_layout'] == 'overlaid'
    assert 'faint under the plot in use, drawn bold' in capsys.readouterr().out
    assert redraws == []

    # ---- 2 A decomposition kept: redrawn ---------------------------------------------
    session.kept = {'text': 'made_up.csv'}
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        Path('.'),
                                        {'compare_layout': 'side'},
                                        )
    assert answers['compare_layout'] == 'side'
    assert 'on the left of the plot in use' in capsys.readouterr().out
    assert redraws == [True]
