"""
Tests of the workbook of a dataset figure: its sheets, the numbers of each plot per region and of each test worked out by hand, the Excel formulas beside them, the units in the headings, the one table of each plot without sets (Single trace, Mean trace, Difference spectrum, Waterfall), what the sheet of a Standard experiment says, and what the run does when it cannot be saved.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import errno
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import openpyxl
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
import main as program
from utils_shared.dataset_workbook_exporter import (_label_plainer,
                                                    BEFORE_STACKING,
                                                    dataset_workbook_exporter,
                                                    dataset_workbook_namer,
                                                    LEFT_OUT_SPECTRA,
                                                    LINED_UP,
                                                    NO_NUMBERS,
                                                    NO_TESTS,
                                                    NOT_YET,
                                                    OWN_WORKBOOK,
                                                    )
from utils_shared.figure_page import (FigurePage,
                                      FigurePageError,
                                      PagePlot,
                                      plot_placer,
                                      )
from utils_shared.page_data import experiment_role_maker, TICK_OFF, TICK_ON, TOGETHER
from utils_shared.page_plots import NO_VALUES, NOT_PICKED
from utils_shared.run_logging import details_place_setter
from utils_shared.schema import TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
# The made-up dataset: the group and the time point of each experiment, and its OCR
# (µM min⁻¹) in its baseline and after its one addition. After the addition the sets
# are those of MATHS.md section 11.5, example 2; the controls change by those of
# section 11.4 (-3, -4, -2)
RUNS = {'c1': ('control', '24 h', (13.0, 10.0)),
        'c2': ('control', '24 h', (15.0, 11.0)),
        'c3': ('control', '2 h', (14.0, 12.0)),
        'k1': ('knockdown', '24 h', (22.0, 20.0)),
        'k2': ('knockdown', '24 h', (26.0, 25.0)),
        'k3': ('knockdown', '2 h', (33.0, 30.0)),
        'r1': ('rescue', '24 h', (11.0, 11.0)),
        'r2': ('rescue', '24 h', (12.0, 12.0)),
        'r3': ('rescue', '', (13.0, 13.0)),
        }
COLOURS = {'control': '#0072b2', 'knockdown': '#d55e00', 'rescue': '#009e73'}
RAW = {'vo2_value': 'raw'}
UNIT = 'OCR (µM min⁻¹)'
# the plots of the made-up page, in the order of their letters a to f
PLOT_TYPES = ('P9', 'P10', 'P11', 'P12', 'P14', 'P17')
# the difference spectra (mOD) of the made-up controls c1 and c2, at these wavelengths
WAVELENGTHS_NM = (540.0, 550.0, 560.0)
DIFFERENCES = {'c1': (1.0, 4.0, 2.0), 'c2': (3.0, 6.0, 4.0)}


# ---- MAKERS --------------------------------------------------------------------------


# ---- _answers_maker ------------------------------------------------------------------
def _answers_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make the answers of a made-up run that works out no haems,
    with nothing left out at the start or the end.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

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

    return dict(settings.DEFAULT_ANSWERS,
                ignore_first_minutes=0.0,
                ignore_last_minutes=0.0,
                )


# ---- _experiments_maker --------------------------------------------------------------
def _experiments_maker() -> Dict[str, dict]:
    """
    ---- Summary ----
    Helper function to make the slim copies of the made-up dataset (RUNS): each has
    an OCR every quarter minute from 0 to 20 min, at its baseline level until its one
    addition at 10 min and at its other level from then on, a baseline region from 2
    to 8 min and a settled region from 14 to 18 min.

    ---- Inputs ----
    None.

    ---- Globals read ----
    RUNS; TIME_COLUMN (imported).

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
    for name, (_, _, (before, after)) in RUNS.items():
        times = np.arange(0.0, 20.125, 0.25)
        ocr = np.where(times < 10.0, before, after)
        percent = pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr / before * 100.0})
        percent.attrs['baseline_percent'] = {'start_time': 2.0,
                                             'end_time': 8.0,
                                             'baseline_mean': {'VoO2': before},
                                             }
        windows = {'average0': {'start_time': 2.0, 'end_time': 8.0},
                   'average1': {'start_time': 14.0, 'end_time': 18.0},
                   }
        experiments[name] = {'experiment_name': name,
                             'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr}),
                             'VoO2_baseline': percent,
                             'metadata': {'events': [{'time': 10.0, 'label': 'KCN'}]},
                             'averages': {'windows': windows},
                             }
    return experiments


# ---- _page_maker ---------------------------------------------------------------------
def _page_maker(plot_types: Tuple[str, ...] = PLOT_TYPES,
                roles: Optional[Dict[str, str]] = None,
                ) -> FigurePage:
    """
    ---- Summary ----
    Helper function to make a page with one plot of each type given, two rows tall
    and three columns wide, placed in reading order so the first is a, the second b.

    ---- Inputs ----
    plot_types : Tuple[str, ...]
        The plot types, at most six.
    roles : Optional[Dict[str, str]]
        The roles of every plot; None for the OCR as measured.

    ---- Globals read ----
    RAW.

    ---- Outputs ----
    FigurePage
        The page.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    page = FigurePage()
    for place, plot_type in enumerate(plot_types):
        page = plot_placer(page,
                           PagePlot(plot_type,
                                    row=2 * (place // 2),
                                    column=3 * (place % 2),
                                    n_rows=2,
                                    n_columns=3,
                                    roles=dict(RAW if roles is None else roles),
                                    ),
                           )
    return page


# ---- _setup_maker --------------------------------------------------------------------
def _setup_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make the set-up of the made-up dataset: three controls, three
    knockdowns and three rescues, each with its time point.

    ---- Inputs ----
    None.

    ---- Globals read ----
    COLOURS, RUNS.

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
            'colours': dict(COLOURS),
            'rows': [{'name': name,
                      'use': True,
                      'group_1': group,
                      'group_2': '',
                      'time_point': point,
                      'run': int(name[1:]),
                      }
                     for name, (group, point, _) in RUNS.items()
                     ],
            }


# ---- READERS -------------------------------------------------------------------------


# ---- _headed_table_reader ------------------------------------------------------------
def _headed_table_reader(sheet: Any, heading: str) -> Tuple[int, List[tuple]]:
    """
    ---- Summary ----
    Helper function to read the one table of the sheet of a plot without sets: from
    the row whose first cell is the heading of its first column down to the first
    empty row.

    ---- Inputs ----
    sheet : Any
        openpyxl worksheet.
    heading : str
        The heading of the first column of the table.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[int, List[tuple]]
        (the row of the headings, from 1; the headings, then each row of the table).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _table_reader
    """

    top = next(row
               for row in range(1, sheet.max_row + 1)
               if sheet.cell(row, 1).value == heading
               )
    return _table_reader(sheet, None, top)


# ---- _table_reader -------------------------------------------------------------------
def _table_reader(sheet: Any,
                  title: Optional[str],
                  start: int = 1,
                  ) -> Tuple[int, List[tuple]]:
    """
    ---- Summary ----
    Helper function to read one table of a sheet: the rows under its title, from its
    headings down to the first empty row.

    ---- Inputs ----
    sheet : Any
        openpyxl worksheet.
    title : Optional[str]
        The text in column A of the row above the headings; None for a table whose
        headings are in the row ``start``.
    start : int
        The row to look from (from 1).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[int, List[tuple]]
        (the row of the headings, from 1; the headings, then each row of the table,
        each without the empty cells at its end).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    top = start
    if title is not None:
        top = next(row
                   for row in range(start, sheet.max_row + 1)
                   if sheet.cell(row, 1).value == title
                   ) + 1
    rows = []
    for cells in sheet.iter_rows(min_row=top, values_only=True):
        if all(cell is None for cell in cells):
            break
        kept = list(cells)
        while kept and kept[-1] is None:
            kept.pop()
        rows.append(tuple(kept))
    return top, rows


# ---- _workbook_reader ----------------------------------------------------------------
def _workbook_reader(tmp_path: Path,
                     page: FigurePage,
                     setup: Optional[dict] = None,
                     experiments: Optional[Dict[str, dict]] = None,
                     ) -> tuple:
    """
    ---- Summary ----
    Helper function to write the workbook of a page of the made-up dataset and read
    it back twice: with its formulas, and with the numbers kept beside them.

    ---- Inputs ----
    tmp_path : Path
        Folder the workbook is written in.
    page : FigurePage
        The page.
    setup : Optional[dict]
        The set-up table; None for that of _setup_maker.
    experiments : Optional[Dict[str, dict]]
        The slim copies; None for those of _experiments_maker.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (the workbook with its formulas as text, the workbook with the number the
        program kept in each formula cell), both openpyxl workbooks.

    ---- Globals mutated ----
    None. Writes the workbook (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_maker
    _experiments_maker
    _setup_maker
    """

    path = dataset_workbook_exporter(page,
                                     tmp_path,
                                     _setup_maker() if setup is None else setup,
                                     (_experiments_maker()
                                      if experiments is None
                                      else experiments
                                      ),
                                     _answers_maker(),
                                     )
    assert path == tmp_path / 'dataset_figure_nature.xlsx'
    return openpyxl.load_workbook(path), openpyxl.load_workbook(path, data_only=True)


# ---- TESTS ---------------------------------------------------------------------------


# ---- test_the_sheets_of_the_workbook -------------------------------------------------
def test_the_sheets_of_the_workbook(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheets of the workbook of a page with a plot of each
    kind: the Figure sheet first, a sheet for each plot per region named by its
    letter and its type, the Tests sheet last; and what the Figure sheet says of
    each plot (also of a plot type whose numbers nothing lays out, and of a space
    for a drawing), with the caption lines of the whole figure under them. A page
    without a plot is refused.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    NO_NUMBERS, NOT_YET (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _page_maker
    _table_reader
    _workbook_reader
    """

    book, _ = _workbook_reader(tmp_path, _page_maker())
    assert book.sheetnames == ['Figure',
                               'a Bar chart',
                               'b Before and after',
                               'c Response by region',
                               'd Time points',
                               'Tests',
                               ]
    sheet = book['Figure']
    assert sheet['A1'].value == 'The numbers of dataset_figure_nature.pdf'
    rows = [tuple(cell.value for cell in row[:3])
            for row in sheet.iter_rows(min_row=3, max_row=9)
            ]
    assert rows == [('Plot', 'Plot type', 'Sheet'),
                    ('a', 'Bar chart', 'a Bar chart'),
                    ('b', 'Before and after', 'b Before and after'),
                    ('c', 'Response by region', 'c Response by region'),
                    ('d', 'Time points', 'd Time points'),
                    ('e', 'Scatter of two numbers', NOT_YET),
                    ('f', 'Space for a drawing', NO_NUMBERS),
                    ]
    assert sheet['C4'].hyperlink.location == "'a Bar chart'!A1"
    assert sheet['D4'].value.startswith('Each dot is one experiment, and the bars are '
                                        'the mean ± SEM of each set',
                                        )
    assert sheet['D8'].value == ''
    _, lines = _table_reader(sheet, 'For the caption, of the whole figure')
    assert lines[0][0].startswith('Colours (strain): control, ')
    assert dataset_workbook_namer('nature') == 'dataset_figure_nature.xlsx'
    with pytest.raises(FigurePageError):
        dataset_workbook_exporter(FigurePage(), tmp_path)


# ---- test_the_sheet_of_a_bar_chart ---------------------------------------------------
def test_the_sheet_of_a_bar_chart(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheet of a Bar chart and its rows of the Tests sheet
    against numbers worked out by hand: every experiment, the n, mean, SD and SEM of
    each set with their Excel formulas, the unit in the headings, and t, the degrees
    of freedom, p and the corrected p of each pair of sets with the formulas that
    repeat p and the correction.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    UNIT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    MATHS.md section 11.5, example 2. Control 10, 11, 12: mean 11, SD 1, SEM
    1 / sqrt(3). Knockdown 20, 25, 30: mean 25, SD 5. Rescue 11, 12, 13: mean 12,
    SD 1. Student's: control and knockdown t = -14 / sqrt(13 x 2 / 3) = -4.756,
    df 4, p = 0.0089; control and rescue t = -1 / sqrt(2 / 3) = -1.225, p = 0.2879;
    knockdown and rescue p = 0.0115. Places 1, 3, 2; p x tests left 0.0089 x 3 =
    0.0268, 0.2879 x 1, 0.0115 x 2 = 0.0231; corrected 0.0268, 0.2879, 0.0268.

    ---- Helpers ----
    _page_maker
    _table_reader
    _workbook_reader
    """

    # ---- 1 Every experiment ----------------------------------------------------------
    book, kept = _workbook_reader(tmp_path, _page_maker(('P9',)))
    sheet = book['a Bar chart']
    assert [sheet.cell(row, 1).value for row in range(1, 7)] == [
        'a: Bar chart',
        f'Measurement: {UNIT}',
        'Region: After addition 1',
        'Kind of averaging region after an addition: settled',
        'Bars on the plot: mean ± SEM',
        "Test between two sets: Student's t-test (two-tailed, unpaired)",
        ]
    top, rows = _table_reader(sheet, 'Each experiment')
    assert rows == [('Set', 'Experiment', UNIT),
                    ('control', 'c1', 10.0),
                    ('control', 'c2', 11.0),
                    ('control', 'c3', 12.0),
                    ('knockdown', 'k1', 20.0),
                    ('knockdown', 'k2', 25.0),
                    ('knockdown', 'k3', 30.0),
                    ('rescue', 'r1', 11.0),
                    ('rescue', 'r2', 12.0),
                    ('rescue', 'r3', 13.0),
                    ]
    cells = [f'$C${top + 1 + 3 * place}:$C${top + 3 + 3 * place}' for place in range(3)]

    # ---- 2 Every set, as worked out and as Excel formulas ----------------------------
    start, rows = _table_reader(sheet, 'Each set')
    assert rows[0] == ('Set',
                       'n',
                       'Mean (µM min⁻¹)',
                       'SD (µM min⁻¹)',
                       'SEM (µM min⁻¹)',
                       'Mean by Excel (µM min⁻¹)',
                       'SD by Excel (µM min⁻¹)',
                       'SEM by Excel (µM min⁻¹)',
                       )
    assert rows[1] == ('control',
                       3,
                       11.0,
                       1.0,
                       pytest.approx(1.0 / np.sqrt(3.0)),
                       f'=AVERAGE({cells[0]})',
                       f'=_xlfn.STDEV.S({cells[0]})',
                       f'=_xlfn.STDEV.S({cells[0]})/SQRT(COUNT({cells[0]}))',
                       )
    assert rows[2][:5] == ('knockdown', 3, 25.0, 5.0, pytest.approx(5.0 / np.sqrt(3.0)))
    assert rows[3][:4] == ('rescue', 3, 12.0, 1.0)
    assert rows[3][5] == f'=AVERAGE({cells[2]})'
    # the number the program worked out is kept in each formula cell
    _, numbers = _table_reader(kept['a Bar chart'], 'Each set')
    assert numbers[2][5:] == pytest.approx((25.0, 5.0, 5.0 / np.sqrt(3.0)))

    # ---- 3 Its tests -----------------------------------------------------------------
    top, rows = _table_reader(book['Tests'], None, 6)
    assert top == 6 and len(rows) == 4
    assert rows[0][:6] == ('Plot',
                           'Measurement',
                           'Region or time point',
                           'First set',
                           'Second set',
                           'Test',
                           )
    assert rows[0][12:] == ('p',
                            'p by Excel',
                            'Place of p in its plot (smallest = 1)',
                            'p × tests left (tests of the plot − place + 1)',
                            'Corrected p (Holm)',
                            'Corrected p by Excel',
                            'Mark on the plot',
                            )
    assert [row[:10] for row in rows[1:]] == [('a',
                                               UNIT,
                                               'After addition 1',
                                               'control',
                                               'knockdown',
                                               "Student's t-test",
                                               3,
                                               3,
                                               11.0,
                                               25.0,
                                               ),
                                              ('a',
                                               UNIT,
                                               'After addition 1',
                                               'control',
                                               'rescue',
                                               "Student's t-test",
                                               3,
                                               3,
                                               11.0,
                                               12.0,
                                               ),
                                              ('a',
                                               UNIT,
                                               'After addition 1',
                                               'knockdown',
                                               'rescue',
                                               "Student's t-test",
                                               3,
                                               3,
                                               25.0,
                                               12.0,
                                               ),
                                              ]
    assert [row[10] for row in rows[1:]] == pytest.approx([-14.0 / np.sqrt(26.0 / 3.0),
                                                           -1.0 / np.sqrt(2.0 / 3.0),
                                                           13.0 / np.sqrt(26.0 / 3.0),
                                                           ],
                                                          )
    assert [row[11] for row in rows[1:]] == [4.0, 4.0, 4.0]
    assert [row[12] for row in rows[1:]] == pytest.approx([0.0089, 0.2879, 0.0115],
                                                          abs=1e-4,
                                                          )
    assert [row[16] for row in rows[1:]] == pytest.approx([0.0268, 0.2879, 0.0268],
                                                          abs=1e-4,
                                                          )
    assert [row[18] for row in rows[1:]] == ['*', '', '*']
    name = "'a Bar chart'!"
    assert [row[13:16] + (row[17],) for row in rows[1:]] == [
        (f'=_xlfn.T.TEST({name}{cells[0]},{name}{cells[1]},2,2)',
         '=_xlfn.RANK.EQ(N7,$N$7:$N$9,1)',
         '=N7*(COUNT($N$7:$N$9)-O7+1)',
         '=MIN(1,SUMPRODUCT(MAX(($N$7:$N$9<=N7)*$P$7:$P$9)))',
         ),
        (f'=_xlfn.T.TEST({name}{cells[0]},{name}{cells[2]},2,2)',
         '=_xlfn.RANK.EQ(N8,$N$7:$N$9,1)',
         '=N8*(COUNT($N$7:$N$9)-O8+1)',
         '=MIN(1,SUMPRODUCT(MAX(($N$7:$N$9<=N8)*$P$7:$P$9)))',
         ),
        (f'=_xlfn.T.TEST({name}{cells[1]},{name}{cells[2]},2,2)',
         '=_xlfn.RANK.EQ(N9,$N$7:$N$9,1)',
         '=N9*(COUNT($N$7:$N$9)-O9+1)',
         '=MIN(1,SUMPRODUCT(MAX(($N$7:$N$9<=N9)*$P$7:$P$9)))',
         ),
        ]
    _, numbers = _table_reader(kept['Tests'], None, 6)
    assert [row[14] for row in numbers[1:]] == [1, 3, 2]
    assert [row[15] for row in numbers[1:]] == pytest.approx([0.0268, 0.2879, 0.0231],
                                                             abs=1e-4,
                                                             )
    assert [row[13] for row in numbers[1:]] == pytest.approx(
        [row[12] for row in rows[1:]],
        )
    assert [row[17] for row in numbers[1:]] == pytest.approx(
        [row[16] for row in rows[1:]],
        )

    # ---- 4 Welch's test is Excel's type 3 --------------------------------------------
    book, _ = _workbook_reader(tmp_path, _page_maker(('P9',), dict(RAW, test='welch')))
    _, rows = _table_reader(book['Tests'], None, 6)
    assert rows[1][5] == "Welch's t-test" and rows[1][13].endswith(',2,3)')


# ---- test_the_sheet_of_a_before_and_after --------------------------------------------
def test_the_sheet_of_a_before_and_after(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheet of a Before and after and its rows of the Tests
    sheet against numbers worked out by hand: the two regions of every experiment
    with their difference as a formula, each set in each region, and the paired test
    of each set whose experiments did not all change by the same amount.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    UNIT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    MATHS.md section 11.4. Control: changes -3, -4, -2, mean -3, SD 1, t =
    -3 / (1 / sqrt(3)) = -5.196, df 2, p = 1 - 5.196 / sqrt(27 + 2) = 0.0351.
    Knockdown: changes -2, -1, -3, t = -2 / (1 / sqrt(3)) = -3.464, p = 1 -
    3.464 / sqrt(12 + 2) = 0.0742. Rescue: no change, so no test. Corrected:
    0.0351 x 2 = 0.0702; 0.0742 x 1 = 0.0742.

    ---- Helpers ----
    _page_maker
    _table_reader
    _workbook_reader
    """

    # ---- 1 Every experiment ----------------------------------------------------------
    book, kept = _workbook_reader(tmp_path, _page_maker(('P10',)))
    sheet = book['a Before and after']
    assert sheet['A3'].value == 'Regions: Baseline, then After addition 1'
    assert sheet['A5'].value == ('Test between the two regions of each set: a paired '
                                 't-test (two-tailed)')
    top, rows = _table_reader(sheet, 'Each experiment')
    assert rows[0] == ('Set',
                       'Experiment',
                       f'Baseline: {UNIT}',
                       f'After addition 1: {UNIT}',
                       f'Second region − first region: {UNIT}',
                       )
    assert rows[1] == ('control', 'c1', 13.0, 10.0, f'=D{top + 1}-C{top + 1}')
    assert rows[9] == ('rescue', 'r3', 13.0, 13.0, f'=D{top + 9}-C{top + 9}')
    _, numbers = _table_reader(kept['a Before and after'], 'Each experiment')
    assert [row[4] for row in numbers[1:]] == [-3.0,
                                               -4.0,
                                               -2.0,
                                               -2.0,
                                               -1.0,
                                               -3.0,
                                               0.0,
                                               0.0,
                                               0.0,
                                               ]

    # ---- 2 Every set in each region --------------------------------------------------
    _, rows = _table_reader(sheet, 'Each set')
    assert rows[0][:3] == ('Set', 'Region', 'n')
    assert [row[:5] for row in rows[1:]] == [('control', 'Baseline', 3, 14.0, 1.0),
                                             ('knockdown',
                                              'Baseline',
                                              3,
                                              27.0,
                                              pytest.approx(np.sqrt(31.0)),
                                              ),
                                             ('rescue', 'Baseline', 3, 12.0, 1.0),
                                             ('control',
                                              'After addition 1',
                                              3,
                                              11.0,
                                              1.0,
                                              ),
                                             ('knockdown',
                                              'After addition 1',
                                              3,
                                              25.0,
                                              5.0,
                                              ),
                                             ('rescue',
                                              'After addition 1',
                                              3,
                                              12.0,
                                              1.0,
                                              ),
                                             ]
    before, after = f'$C${top + 1}:$C${top + 3}', f'$D${top + 1}:$D${top + 3}'
    assert rows[1][6] == f'=AVERAGE({before})' and rows[4][6] == f'=AVERAGE({after})'

    # ---- 3 Its tests -----------------------------------------------------------------
    _, rows = _table_reader(book['Tests'], None, 6)
    assert [row[:10] for row in rows[1:]] == [('a',
                                               UNIT,
                                               'Baseline, then After addition 1',
                                               'control (Baseline)',
                                               'control (After addition 1)',
                                               'Paired t-test',
                                               3,
                                               3,
                                               14.0,
                                               11.0,
                                               ),
                                              ('a',
                                               UNIT,
                                               'Baseline, then After addition 1',
                                               'knockdown (Baseline)',
                                               'knockdown (After addition 1)',
                                               'Paired t-test',
                                               3,
                                               3,
                                               27.0,
                                               25.0,
                                               ),
                                              ]
    assert [row[10] for row in rows[1:]] == pytest.approx([-3.0 * np.sqrt(3.0),
                                                           -2.0 * np.sqrt(3.0),
                                                           ],
                                                          )
    assert [row[11] for row in rows[1:]] == [2.0, 2.0]
    assert [row[12] for row in rows[1:]] == pytest.approx([0.0351, 0.0742], abs=1e-4)
    assert [row[16] for row in rows[1:]] == pytest.approx([0.0702, 0.0742], abs=1e-4)
    name = "'a Before and after'!"
    assert rows[1][13] == f'=_xlfn.T.TEST({name}{before},{name}{after},2,1)'
    # neither is under 0.05 once corrected, so neither has a mark
    assert [row[18] for row in rows[1:]] == ['', '']


# ---- test_the_sheets_of_a_response_and_of_a_time_points ------------------------------
def test_the_sheets_of_a_response_and_of_a_time_points(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheet of a Response by region (a column per region,
    its tests corrected together) and of a Time points (the experiments of a set at
    one time point one under the other, one without a time point last and in no
    mean), with numbers worked out by hand.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    UNIT.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Response by region: three pairs of sets in each of two regions, so 6 tests; the
    smallest p is multiplied by 6. Time points, at 24 h: control 10, 11 (mean 10.5,
    SD sqrt(0.5)), knockdown 20, 25, rescue 11, 12, so three tests; at 2 h each set
    has one experiment, so none.

    ---- Helpers ----
    _page_maker
    _table_reader
    _workbook_reader
    """

    # ---- 1 The Response by region ----------------------------------------------------
    book, kept = _workbook_reader(tmp_path, _page_maker(('P11', 'P12')))
    sheet = book['a Response by region']
    assert sheet['A7'].value == UNIT
    top, rows = _table_reader(sheet, 'Each experiment')
    assert rows[0][:3] == ('Set', 'Experiment', f'Baseline: {UNIT}')
    assert len(rows[0]) == 4 and rows[0][3].endswith(f': {UNIT}',
                                                     ) and 'KCN' in rows[0][3]
    assert rows[1] == ('control', 'c1', 13.0, 10.0)
    _, sets = _table_reader(sheet, 'Each set')
    assert len(sets) == 7 and sets[1][:4] == ('control', 'Baseline', 3, 14.0)
    assert sets[6][6] == f'=AVERAGE($D${top + 7}:$D${top + 9})'
    _, rows = _table_reader(book['Tests'], None, 6)
    _, numbers = _table_reader(kept['Tests'], None, 6)
    response = [place for place, row in enumerate(rows) if row[0] == 'a']
    assert len(response) == 6
    assert [rows[place][2] for place in response[:3]] == ['Baseline'] * 3
    first = min(response, key=lambda place: rows[place][12])
    assert numbers[first][14] == 1
    assert numbers[first][15] == pytest.approx(6.0 * rows[first][12])
    assert rows[response[0]][14] == '=_xlfn.RANK.EQ(N7,$N$7:$N$12,1)'
    assert rows[response[-1]][13] == (
        f"=_xlfn.T.TEST('a Response by region'!$D${top + 4}:$D${top + 6},"
        f"'a Response by region'!$D${top + 7}:$D${top + 9},2,2)"
        )

    # ---- 2 The Time points -----------------------------------------------------------
    sheet = book['b Time points']
    top, rows = _table_reader(sheet, 'Each experiment')
    assert rows[0] == ('Set', 'Experiment', 'Time point', UNIT)
    control = [row for row in rows if row[0] == 'control']
    assert sorted(control) == [('control', 'c1', '24 h', 10.0),
                               ('control', 'c2', '24 h', 11.0),
                               ('control', 'c3', '2 h', 12.0),
                               ]
    # the two experiments of one time point are next to each other
    places = [place for place, row in enumerate(rows) if row[:3:2] == ('control', '24 h')]
    assert places[1] == places[0] + 1
    rescue = [row for row in rows if row[0] == 'rescue']
    assert rescue[-1] == ('rescue', 'r3', '', 13.0)
    _, sets = _table_reader(sheet, 'Each set')
    assert sets[0][:3] == ('Set', 'Time point', 'n')
    found = next(row for row in sets if row[:2] == ('control', '24 h'))
    assert found[2:5] == (2, 10.5, pytest.approx(np.sqrt(0.5)))
    assert found[6] == f'=AVERAGE($D${top + places[0]}:$D${top + places[1]})'
    assert next(row for row in sets if row[:2] == ('rescue', '24 h'))[2:4] == (2, 11.5)
    assert not any(row[:2] == ('rescue', '') for row in sets)
    single = next(row for row in sets if row[:2] == ('control', '2 h'))
    assert single[2:4] == (1, 12.0) and len(single) == 7
    _, rows = _table_reader(book['Tests'], None, 6)
    points = [row for row in rows if row[0] == 'b']
    assert [row[2:5] for row in points] == [('24 h', 'control', 'knockdown'),
                                            ('24 h', 'control', 'rescue'),
                                            ('24 h', 'knockdown', 'rescue'),
                                            ]
    assert points[0][14] == '=_xlfn.RANK.EQ(N13,$N$13:$N$15,1)'


# ---- test_a_plot_without_numbers_and_an_experiment_not_read --------------------------
def test_a_plot_without_numbers_and_an_experiment_not_read(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheet of a plot with nothing to show (the sentence
    the plot shows, and a Tests sheet that says there is no test), an experiment of
    the set-up that was not read (an empty cell in its set, named on the Figure
    sheet), and the plain text of a label.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    NO_TESTS (imported); NO_VALUES (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _page_maker
    _setup_maker
    _table_reader
    _workbook_reader
    """

    # ---- 1 A region no experiment has ------------------------------------------------
    page = _page_maker(('P9',), dict(RAW, region='addition 2'))
    book, _ = _workbook_reader(tmp_path, page)
    assert book['a Bar chart']['A2'].value == NO_VALUES
    assert book['Tests']['A7'].value == NO_TESTS

    # ---- 2 An experiment that was not read -------------------------------------------
    setup = _setup_maker()
    setup['rows'].insert(1, dict(setup['rows'][0], name='c9', run=9))
    book, _ = _workbook_reader(tmp_path, _page_maker(('P9',)), setup)
    top, rows = _table_reader(book['a Bar chart'], 'Each experiment')
    assert rows[1:5] == [('control', 'c1', 10.0),
                         ('control', 'c9'),
                         ('control', 'c2', 11.0),
                         ('control', 'c3', 12.0),
                         ]
    _, sets = _table_reader(book['a Bar chart'], 'Each set')
    assert sets[1][:3] == ('control', 3, 11.0)
    assert sets[1][5] == f'=AVERAGE($C${top + 1}:$C${top + 4})'
    _, notes = _table_reader(book['Figure'], 'Left out')
    assert notes == [('c9 could not be read, so it is in no plot.',)]

    # ---- 3 The text of a plot, in plain characters -----------------------------------
    assert _label_plainer('OCR (µM min$^{-1}$ OD$^{-1}$)') == 'OCR (µM min⁻¹ OD⁻¹)'
    assert _label_plainer('Cyt $b_H$ ΔD (mOD)') == 'Cyt bH ΔD (mOD)'


# ---- test_the_sheets_of_the_traces_over_time -----------------------------------------
def test_the_sheets_of_the_traces_over_time(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheets of a Single trace and of a Mean trace, worked
    out by hand on the made-up dataset: the trace of one experiment with its time
    from its addition and in the file; the lined-up trace of every experiment
    behind the mean of its set, the mean and the SEM, and the Excel formulas beside
    them; the band as the SD, and no band.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    RAW, UNIT; LINED_UP (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The controls are at 13, 15 and 14 µM min⁻¹ before their addition and at 10, 11
    and 12 after it: means 14 and 11, SD 1, SEM 1 / √3. The knockdowns are at 22, 26
    and 33, then 20, 25 and 30: means 27 and 25.

    ---- Helpers ----
    _headed_table_reader
    _page_maker
    _setup_maker
    _workbook_reader
    """

    # ---- 1 A Single trace, its time from its one addition at 10 min ------------------
    roles = dict(RAW, experiment=experiment_role_maker(_setup_maker(), 'c1'))
    book, kept = _workbook_reader(tmp_path, _page_maker(('P7', 'P8'), roles))
    assert book.sheetnames == ['Figure', 'a Single trace', 'b Mean trace', 'Tests']
    assert book['Figure']['C4'].value == 'a Single trace'
    sheet = book['a Single trace']
    assert [sheet.cell(row, 1).value for row in range(1, 6)] == [
        'a: Single trace',
        'Experiment: c1',
        f'Trace: {UNIT}',
        'Additions at (minutes, on the time of the plot): 0',
        'Time 0 of the plot is at 10 minutes in the file.',
        ]
    _, rows = _headed_table_reader(sheet, 'Time in the file (minutes)')
    assert rows[0] == ('Time in the file (minutes)',
                       'Time from addition 1 (minutes)',
                       UNIT,
                       )
    assert len(rows) == 1 + 81
    assert rows[1] == (0.0, -10.0, 13.0)
    assert rows[40] == (9.75, -0.25, 13.0)
    assert rows[41] == (10.0, 0.0, 10.0)
    assert rows[81] == (20.0, 10.0, 10.0)

    # ---- 2 A Mean trace: every experiment behind each mean ---------------------------
    sheet = book['b Mean trace']
    assert [sheet.cell(row, 1).value for row in range(2, 6)] == [
        f'Trace: {UNIT}',
        'Band on the plot: mean ± SEM',
        'Additions at (minutes, on the shared time): 0',
        LINED_UP,
        ]
    top, rows = _headed_table_reader(sheet, 'Time from addition 1 (minutes)')
    assert rows[0][:8] == ('Time from addition 1 (minutes)',
                           f'control, c1: {UNIT}',
                           f'control, c2: {UNIT}',
                           f'control, c3: {UNIT}',
                           f'control, mean: {UNIT}',
                           f'control, SEM: {UNIT}',
                           f'control, mean by Excel: {UNIT}',
                           f'control, SEM by Excel: {UNIT}',
                           )
    assert rows[0][8] == f'knockdown, k1: {UNIT}'
    assert rows[0][15] == f'rescue, r1: {UNIT}'
    assert len(rows[0]) == 22
    assert len(rows) == 1 + 1201  # one row every second from -10 to 10 min
    first = top + 1
    cells = f'B{first}:D{first}'
    assert rows[1][:5] == pytest.approx((-10.0, 13.0, 15.0, 14.0, 14.0))
    assert rows[1][5] == pytest.approx(1.0 / np.sqrt(3.0))
    assert rows[1][6] == f'=AVERAGE({cells})'
    assert rows[1][7] == f'=_xlfn.STDEV.S({cells})/SQRT(COUNT({cells}))'
    assert rows[1][8:12] == pytest.approx((22.0, 26.0, 33.0, 27.0))
    assert rows[1][13] == f'=AVERAGE(I{first}:K{first})'
    assert rows[601][:5] == pytest.approx((0.0, 10.0, 11.0, 12.0, 11.0), abs=1e-9)
    assert rows[601][8:12] == pytest.approx((20.0, 25.0, 30.0, 25.0))
    assert rows[601][6] == f'=AVERAGE(B{top + 601}:D{top + 601})'
    numbers = kept['b Mean trace']
    assert numbers.cell(first, 7).value == pytest.approx(14.0)
    assert numbers.cell(first, 8).value == pytest.approx(1.0 / np.sqrt(3.0))

    # ---- 3 The band as the SD, and no band -------------------------------------------
    book, _ = _workbook_reader(tmp_path, _page_maker(('P8',), dict(RAW, band='sd')))
    sheet = book['a Mean trace']
    assert sheet['A3'].value == 'Band on the plot: mean ± SD'
    top, rows = _headed_table_reader(sheet, 'Time from addition 1 (minutes)')
    assert rows[0][5] == f'control, SD: {UNIT}'
    assert rows[1][5] == pytest.approx(1.0)
    assert rows[1][7] == f'=_xlfn.STDEV.S(B{top + 1}:D{top + 1})'
    book, _ = _workbook_reader(tmp_path, _page_maker(('P8',), dict(RAW, band='none')))
    sheet = book['a Mean trace']
    assert sheet['A3'].value == 'Band on the plot: none'
    _, rows = _headed_table_reader(sheet, 'Time from addition 1 (minutes)')
    assert rows[0][4:7] == (f'control, mean: {UNIT}',
                            f'control, mean by Excel: {UNIT}',
                            f'knockdown, k1: {UNIT}',
                            )


# ---- test_the_sheets_of_the_spectra_and_of_a_standard_experiment ---------------------
def test_the_sheets_of_the_spectra_and_of_a_standard_experiment(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the sheets of a Difference spectrum (the difference and
    each part ticked, the haem bands), of a Waterfall (the mean spectrum of each
    time point, each experiment, and a trace of each experiment, all before the
    stacking, with the experiment left out named) and of a Standard experiment (its
    panels and the experiment's own workbook, no numbers copied in; the sentence of
    one without an experiment), on made-up spectra worked out by hand.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.

    ---- Globals read ----
    DIFFERENCES, RAW, UNIT, WAVELENGTHS_NM; BEFORE_STACKING, LEFT_OUT_SPECTRA,
    NOT_PICKED, OWN_WORKBOOK, TICK_OFF, TICK_ON, TOGETHER (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The mean of the difference spectra of c1 (1, 4, 2) and c2 (3, 6, 4), the two
    controls at 24 h, is 2, 5, 3 mOD.

    ---- Helpers ----
    _experiments_maker
    _headed_table_reader
    _page_maker
    _setup_maker
    _table_reader
    _workbook_reader
    """

    # ---- 1 The made-up spectra: c1 and c2 have a difference, c3 has none -------------
    experiments = _experiments_maker()
    waves = np.array(WAVELENGTHS_NM)
    for name, values in DIFFERENCES.items():
        experiments[name]['difference'] = {'wavelengths_nm': waves,
                                           'difference_mOD': np.array(values),
                                           'reduced_region': (14.0, 18.0),
                                           'oxidised_region': (2.0, 8.0),
                                           }
        experiments[name]['haem_bands'] = {'Cyt $b_H$': (557.5, 562.5)}
    haems = {'Cyt $b_H$': np.array([0.5, 3.0, 1.0]),
             'Cyt c': np.array([0.25, 0.5, 0.5]),
             }
    experiments['c1']['difference_parts'] = {'wavelengths_nm': waves,
                                             'measured_mOD': np.array(DIFFERENCES['c1'],
                                                                      ),
                                             'haems_mOD': haems,
                                             'background_mOD': np.array(
                                                 [0.25, 0.25, 0.25],
                                                 ),
                                             'fit_mOD': np.array([1.0, 3.75, 1.75]),
                                             'residual_mOD': np.array([0.0, 0.25, 0.25],
                                                                      ),
                                             }
    picked = experiment_role_maker(_setup_maker(), 'c1')

    # ---- 2 A Difference spectrum with everything ticked, then with little ------------
    roles = {'experiment': picked, 'background': TICK_ON, 'haem_bands': TICK_ON}
    book, _ = _workbook_reader(tmp_path,
                               _page_maker(('P2', 'P1'), roles),
                               experiments=experiments,
                               )
    assert book.sheetnames == ['Figure',
                               'a Difference spectrum',
                               'b Standard experiment',
                               'Tests',
                               ]
    sheet = book['a Difference spectrum']
    assert sheet['A2'].value == 'Experiment: c1'
    assert sheet['A4'].value == 'Haem bands (nm): Cyt bH 557.5 to 562.5'
    _, rows = _headed_table_reader(sheet, 'Wavelength (nm)')
    assert rows == [('Wavelength (nm)',
                     'Measured (mOD)',
                     'Cyt bH (mOD)',
                     'Cyt c (mOD)',
                     'Background (mOD)',
                     'Fit (mOD)',
                     'Residual (mOD)',
                     ),
                    (540.0, 1.0, 0.5, 0.25, 0.25, 1.0, 0.0),
                    (550.0, 4.0, 3.0, 0.5, 0.25, 3.75, 0.25),
                    (560.0, 2.0, 1.0, 0.5, 0.25, 1.75, 0.25),
                    ]

    # ---- 3 A Standard experiment: where its numbers are, none copied in --------------
    sheet = book['b Standard experiment']
    assert [sheet.cell(row, 1).value for row in range(1, 6)] == [
        'b: Standard experiment',
        'Experiment: c1',
        'Panels: OCR',
        OWN_WORKBOOK.format('c1'),
        None,
        ]
    assert 'c1/c1.xlsx' in sheet['A4'].value
    assert all(cell.value is None for row in sheet.iter_rows(min_row=5) for cell in row)
    little = {'experiment': picked,
              'haem_components': TICK_OFF,
              'residual': TICK_OFF,
              }
    book, _ = _workbook_reader(tmp_path,
                               _page_maker(('P2', 'P1'), little),
                               experiments=experiments,
                               )
    _, rows = _headed_table_reader(book['a Difference spectrum'], 'Wavelength (nm)')
    assert rows[:2] == [('Wavelength (nm)', 'Measured (mOD)', 'Fit (mOD)'),
                        (540.0, 1.0, 1.0),
                        ]
    book, _ = _workbook_reader(tmp_path, _page_maker(('P1',)), experiments=experiments)
    assert book['a Standard experiment']['A2'].value == NOT_PICKED

    # ---- 4 A Waterfall of the controls: each time point, then each experiment --------
    label = 'Reduced − oxidised (mOD)'
    book, _ = _workbook_reader(tmp_path, _page_maker(('P3',)), experiments=experiments)
    sheet = book['a Waterfall']
    left_out = LEFT_OUT_SPECTRA.format('c3')
    assert [sheet.cell(row, 1).value for row in range(2, 5)] == [f'Each line: {label}',
                                                                 BEFORE_STACKING,
                                                                 left_out,
                                                                 ]
    _, rows = _headed_table_reader(sheet, 'Wavelength (nm)')
    assert rows == [('Wavelength (nm)', f'24 h (n = 2): {label}'),
                    (540.0, 2.0),
                    (550.0, 5.0),
                    (560.0, 3.0),
                    ]
    _, notes = _table_reader(book['Figure'], 'Left out')
    assert notes == [(f'a: {left_out}',)]
    book, _ = _workbook_reader(tmp_path,
                               _page_maker(('P3',), {'time_point': TOGETHER}),
                               experiments=experiments,
                               )
    _, rows = _headed_table_reader(book['a Waterfall'], 'Wavelength (nm)')
    assert rows[:2] == [('Wavelength (nm)', f'c1: {label}', f'c2: {label}'),
                        (540.0, 1.0, 3.0),
                        ]

    # ---- 5 A Waterfall of the OCR of each control, lined up on the addition ----------
    traces = dict(RAW, trace='vo2', time_point=TOGETHER)
    book, _ = _workbook_reader(tmp_path,
                               _page_maker(('P3',), traces),
                               experiments=experiments,
                               )
    sheet = book['a Waterfall']
    assert sheet['A2'].value == f'Each line: {UNIT}'
    assert sheet['A4'].value == 'Additions at (minutes, on the shared time): 0'
    _, rows = _headed_table_reader(sheet, 'Time from addition 1 (minutes)')
    assert rows[0] == ('Time from addition 1 (minutes)',
                       f'c1: {UNIT}',
                       f'c2: {UNIT}',
                       f'c3: {UNIT}',
                       )
    assert rows[1] == pytest.approx((-10.0, 13.0, 15.0, 14.0))
    assert len(rows) == 1 + 1201


# ---- test_the_run_saves_the_workbook -------------------------------------------------
def test_the_run_saves_the_workbook(tmp_path: Path,
                                    monkeypatch: pytest.MonkeyPatch,
                                    capsys: pytest.CaptureFixture,
                                    ) -> None:
    """
    ---- Summary ----
    Main function to check what the run does with the workbook of the dataset
    figure: it is saved beside the figure and named on screen; one that is open in
    Excel gives one plain sentence, with the words of Python in the log only, and
    the figure and its master page are still saved.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest.
    monkeypatch : pytest.MonkeyPatch
        Stands in for the saving that fails.
    capsys : pytest.CaptureFixture
        What is shown on screen.

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
    _experiments_maker
    _page_maker
    _setup_maker
    """

    # ---- 1 The workbook is saved -----------------------------------------------------
    page = _page_maker(('P9',))
    filled = (_setup_maker(), _experiments_maker(), _answers_maker())
    workbook = tmp_path / 'dataset_figure_nature.xlsx'
    saved = program.dataset_figure_saver(page, tmp_path, *filled)
    assert saved[-1] == workbook and workbook.exists() and len(saved) == 3
    assert 'Saved dataset_figure_nature.xlsx' in capsys.readouterr().out

    # ---- refuser ---------------------------------------------------------------------
    def refuser(*_args: object) -> Path:
        raise PermissionError(errno.EACCES, 'Permission denied', str(workbook))

    # ---- 2 The workbook is open in Excel ---------------------------------------------
    log = io.StringIO()
    details_place_setter(log, 'the test log')
    try:
        monkeypatch.setattr(program, 'dataset_workbook_exporter', refuser)
        assert program.dataset_figure_saver(page, tmp_path, *filled) == saved[:2]
        shown = ' '.join(capsys.readouterr().out.split())
        assert ('The workbook of the dataset figure was not saved: '
                'dataset_figure_nature.xlsx could not be opened or saved, perhaps '
                'because it is open in another program'
                ) in shown
        assert 'Permission denied' not in shown
        assert 'Permission denied' in log.getvalue()
    finally:
        details_place_setter(None, '')
