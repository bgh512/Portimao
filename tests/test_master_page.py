"""
Tests of the master page: where the figure, its legend and the text sit on the page of
a journal, the name of the file, the page of the saved PDF, and the one sentence shown
when the PDF is open in another program.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import errno
import io
import re
from pathlib import Path
from typing import Iterator

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.master_page_exporter import (master_file_namer,
                                               master_page_exporter,
                                               master_page_layout_builder,
                                               master_text_lines_lister,
                                               )
from utils_shared.run_logging import details_place_setter
from utils_viewer import viewer_stages
from utils_viewer.viewer_preview import ViewerSession
from utils_viewer.viewer_strip import MASTER_CHANGE


# ---- CONSTANTS -----------------------------------------------------------------------
NATURE = {'name': 'Nature', 'widths_mm': {1: 89, 1.5: 120, 2: 183}, 'paper_mm': None}
SCIENCE = {'name': 'Science',
           'widths_mm': {1: 57, 2: 121, 3: 184},
           'paper_mm': (209.6, 266.7),
           }


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _quiet_details ------------------------------------------------------------------
@pytest.fixture
def _quiet_details() -> Iterator[io.StringIO]:
    """
    ---- Summary ----
    Helper function (a pytest fixture) to send the details of a problem to a made-up
    log while a test runs, and to send them nowhere afterwards.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Iterator[io.StringIO]
        The made-up log, named "the test log" for the user.

    ---- Globals mutated ----
    None. Sets the place for the details, and clears it after the test (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    details_place_setter
    """

    log = io.StringIO()
    details_place_setter(log, 'the test log')
    yield log
    details_place_setter(None, '')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_page_of_a_one_column_figure ------------------------------------------------
def test_page_of_a_one_column_figure() -> None:
    """
    ---- Summary ----
    Main function to check where everything sits for a 1 column Nature figure, on the
    A4 page that stands in while the journal's page size is not given: the text runs
    from the top in the column beside the figure, and from under the legend in the
    column the figure covers.

    ---- Inputs ----
    None.

    ---- Globals read ----
    NATURE.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A4 is 210 x 297 mm and the widest Nature figure 183 mm, so the margin is
    (210 - 183) / 2 = 13.5 mm and each of the 2 columns (183 - 5) / 2 = 89 mm wide,
    the second starting at 13.5 + 89 + 5 = 107.5 mm. A figure of 89 x 85 mm ends at
    13.5 + 85 = 98.5 mm; its legend starts 3 mm lower, at 101.5 mm, and is 18 mm tall;
    the text under it starts 4 mm lower, at 101.5 + 18 + 4 = 123.5 mm. Every column
    ends at 297 - 13.5 = 283.5 mm.

    ---- Helpers ----
    master_page_layout_builder
    """

    layout = master_page_layout_builder(NATURE, (89.0, 85.0))
    assert layout['page_mm'] == (210.0, 297.0)
    assert layout['is_page_given'] is False
    assert layout['margin_mm'] == pytest.approx(13.5)
    assert layout['column_mm'] == pytest.approx(89.0)
    assert layout['figure_mm'] == pytest.approx((13.5, 13.5, 89.0, 85.0))
    assert layout['legend_mm'] == pytest.approx((13.5, 101.5, 89.0, 18.0))
    assert layout['columns_mm'] == [pytest.approx((13.5, 123.5, 89.0, 283.5)),
                                    pytest.approx((107.5, 13.5, 89.0, 283.5)),
                                    ]


# ---- test_page_of_a_journal_with_three_columns ---------------------------------------
def test_page_of_a_journal_with_three_columns() -> None:
    """
    ---- Summary ----
    Main function to check the page of Science, whose page size is given and which
    prints in three columns, for a 2 column figure, and that a figure as wide as the
    page leaves no column beside it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    SCIENCE.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The page is 209.6 x 266.7 mm and the widest figure 184 mm: the margin is
    (209.6 - 184) / 2 = 12.8 mm and each of the 3 columns (184 - 2 x 5) / 3 = 58 mm,
    starting at 12.8, 75.8 and 138.8 mm. A figure of 121 x 100 mm ends at 133.8 mm
    across, so only the third column is beside it; the text under it starts at
    12.8 + 100 + 3 + 18 + 4 = 137.8 mm, and every column ends at 266.7 - 12.8 =
    253.9 mm.

    ---- Helpers ----
    master_page_layout_builder
    """

    layout = master_page_layout_builder(SCIENCE, (121.0, 100.0))
    assert layout['page_mm'] == (209.6, 266.7)
    assert layout['is_page_given'] is True
    assert layout['margin_mm'] == pytest.approx(12.8)
    assert layout['column_mm'] == pytest.approx(58.0)
    assert layout['columns_mm'] == [pytest.approx((12.8, 137.8, 58.0, 253.9)),
                                    pytest.approx((75.8, 137.8, 58.0, 253.9)),
                                    pytest.approx((138.8, 12.8, 58.0, 253.9)),
                                    ]
    wide = master_page_layout_builder(SCIENCE, (184.0, 100.0))
    assert [top for _, top, _, _ in wide['columns_mm']] == pytest.approx([137.8] * 3)


# ---- test_lines_of_the_placeholder_text ----------------------------------------------
def test_lines_of_the_placeholder_text() -> None:
    """
    ---- Summary ----
    Main function to check the grey lines that stand for the text: one every 4.2 mm
    while it fits in its column, the ninth of each paragraph shorter.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A column from 20 to 30 mm: lines at 20, 24.2 and 28.4 mm (the third ends at
    28.4 + 1.3 = 29.7 mm; a fourth at 32.6 mm would not fit). A column from 0 to
    40 mm holds lines at 0, 4.2, ... 37.8 mm, ten of them (37.8 + 1.3 = 39.1 mm), and
    its ninth is 0.55 x 50 = 27.5 mm long.

    ---- Helpers ----
    master_text_lines_lister
    """

    short = master_text_lines_lister({'columns_mm': [(10.0, 20.0, 50.0, 30.0)]})
    assert short == [pytest.approx((10.0, 20.0, 50.0)),
                     pytest.approx((10.0, 24.2, 50.0)),
                     pytest.approx((10.0, 28.4, 50.0)),
                     ]
    two = master_text_lines_lister({'columns_mm': [(0.0, 0.0, 50.0, 40.0),
                                                   (60.0, 38.0, 50.0, 40.0),
                                                   ],
                                    },
                                   )
    assert len(two) == 11  # ten in the first column, one in the second
    assert [width for _, _, width in two[:10]] == pytest.approx([50.0] * 8
                                                                + [27.5, 50.0],
                                                                )
    assert two[9] == pytest.approx((0.0, 37.8, 50.0))
    assert two[10] == pytest.approx((60.0, 38.0, 50.0))
    assert master_text_lines_lister({'columns_mm': [(0.0, 10.0, 50.0, 11.0)]}) == []


# ---- test_master_page_is_saved_at_the_page_size --------------------------------------
def test_master_page_is_saved_at_the_page_size(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the PDF saved for a made-up figure: its name, its folder
    (made when missing), and that its one page has the size of the journal's page, or
    of A4 when the journal gives none.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    NATURE, SCIENCE.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A PDF measures its page in points of 1/72 in: A4 is 210 / 25.4 x 72 = 595.3 by
    297 / 25.4 x 72 = 841.9 points, and the Science page 209.6 / 25.4 x 72 = 594.1 by
    266.7 / 25.4 x 72 = 756.0 points.

    ---- Helpers ----
    master_file_namer
    master_page_exporter
    """

    assert master_file_namer('control-bd_run1', 'nature') == (
        'control-bd_run1_master_nature.pdf')
    assert master_file_namer('KCN: 5 µM', 'plos_one') == 'KCN_ 5 µM_master_plos_one.pdf'
    fig = Figure(figsize=(57 / 25.4, 50 / 25.4))
    fig.subplots().plot([0, 1, 2], [1, 3, 2])
    sizes = {}
    for journal, spec in (('nature', NATURE), ('science', SCIENCE)):
        path = master_page_exporter(fig, spec, journal, 'run1', tmp_path / 'results')
        assert path == tmp_path / 'results' / f'run1_master_{journal}.pdf'
        boxes = re.findall(rb'/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]',
                           path.read_bytes(),
                           )
        assert len(boxes) == 1  # one page
        sizes[journal] = tuple(float(side) for side in boxes[0])
    assert sizes['nature'] == pytest.approx((595.3, 841.9), abs=0.1)
    assert sizes['science'] == pytest.approx((594.1, 756.0), abs=0.1)


# ---- test_master_page_open_elsewhere_is_one_sentence ---------------------------------
def test_master_page_open_elsewhere_is_one_sentence(tmp_path: Path,
                                                    monkeypatch: pytest.MonkeyPatch,
                                                    capsys: pytest.CaptureFixture,
                                                    _quiet_details: io.StringIO,
                                                    ) -> None:
    """
    ---- Summary ----
    Main function to check what the Export master button does: before the figure of
    each file is on the plot it only says when the page can be exported; with it on
    the plot it saves the page of the file shown, for the journal of the answers; and
    a PDF that is open in another program gives one plain sentence, with Python's own
    words in the log only. The drawing of the figure and the saving are stood in for.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for the drawing and the saving.
    capsys : pytest.CaptureFixture
        What is shown on screen.
    _quiet_details : io.StringIO
        The made-up log the details go to.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 A session showing the second of two files ---------------------------------
    session = ViewerSession([{'name': 'run1'}, {'name': 'run2'}], tmp_path, None)
    session.current = 1
    answers = dict(settings.DEFAULT_ANSWERS, journal='science', columns=2)
    saved = []

    def exporter(figure: object,
                 spec: dict,
                 journal: str,
                 name: str,
                 folder: Path,
                 ) -> Path:
        saved.append((figure, spec['name'], journal, name, folder))
        return folder / f'{name}_master_{journal}.pdf'

    monkeypatch.setattr(viewer_stages,
                        'preview_figure_builder',
                        lambda session, spec, name: ('the figure', ''),
                        )
    monkeypatch.setattr(viewer_stages, 'master_page_exporter', exporter)
    monkeypatch.setattr(viewer_stages, '_strip_shower', lambda *args: None)

    # ---- 2 Before the figure of each file is on the plot -----------------------------
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        tmp_path,
                                        {MASTER_CHANGE: True},
                                        )
    assert saved == []
    assert 'it can be exported once that figure is on the plot' in (
        capsys.readouterr().out)

    # ---- 3 With it on the plot: the file shown, the journal of the answers -----------
    session.is_figure = True
    session.master_exporter = lambda: viewer_stages._master_page_saver(session,
                                                                       answers,
                                                                       {},
                                                                       {},
                                                                       )
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        tmp_path,
                                        {MASTER_CHANGE: True},
                                        )
    assert saved == [('the figure', 'Science', 'science', 'run2', tmp_path)]
    shown = capsys.readouterr().out
    assert (f'Saved the master page of run2 (Science) as run2_master_science.pdf in '
            f'{tmp_path}.'
            ) in ' '.join(shown.split())

    # ---- refuser ---------------------------------------------------------------------
    def refuser(*_args: object) -> Path:
        raise PermissionError(errno.EACCES,
                              'Permission denied',
                              str(tmp_path / 'run2_master_science.pdf'),
                              )

    monkeypatch.setattr(viewer_stages, 'master_page_exporter', refuser)
    viewer_stages._strip_change_applier(session,
                                        answers,
                                        tmp_path,
                                        {MASTER_CHANGE: True},
                                        )
    shown = ' '.join(capsys.readouterr().out.split())
    assert ('The master page of run2 was not saved: run2_master_science.pdf could not '
            'be opened or saved, perhaps because it is open in another program such as '
            'Excel: close it there and try again.'
            ) in shown
    assert 'Permission denied' not in shown
    assert 'Permission denied' in _quiet_details.getvalue()
