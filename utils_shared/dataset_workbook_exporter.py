"""
The workbook of a dataset figure: a sheet per plot with the numbers it draws (the number of every experiment behind each mean), and a sheet with every test, each number beside the Excel formula that repeats it.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import xlsxwriter
from xlsxwriter.exceptions import FileCreateError
from xlsxwriter.utility import xl_range, xl_range_abs, xl_rowcol_to_cell

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_page import (EMPTY_TYPES,
                                      figure_file_namer,
                                      FigurePage,
                                      FigurePageError,
                                      panel_letters_finder,
                                      PLOT_TYPES,
                                      )
from utils_shared.helpers import excel_sheet_namer, file_name_sanitiser
from utils_shared.page_data import (BAND_CHOICES,
                                    caption_lines_builder,
                                    page_experiments_lister,
                                    )
from utils_shared.page_plots import (bar_numbers_lister,
                                     before_after_numbers_lister,
                                     difference_numbers_lister,
                                     mean_lines_lister,
                                     NO_MEAN,
                                     NO_PAIRS,
                                     NO_POINTS,
                                     NO_RESPONSE,
                                     NO_VALUES,
                                     response_numbers_lister,
                                     standard_numbers_lister,
                                     time_points_numbers_lister,
                                     trace_numbers_lister,
                                     waterfall_numbers_lister,
                                     )
from utils_shared.region_statistics import (ERROR_CHOICES,
                                            p_value_marker,
                                            PAIRED_WORDS,
                                            TEST_CHOICES,
                                            TEST_WORDS,
                                            )
from utils_shared.spectral_decomposer import haem_name_plainer
from utils_shared.workbook_helpers import (formula_writer,
                                           number_writer,
                                           workbook_formats_builder,
                                           )


# ---- CONSTANTS -----------------------------------------------------------------------
FIGURE_SHEET = 'Figure'
TESTS_SHEET = 'Tests'
EXPERIMENTS_TITLE = 'Each experiment'
SETS_TITLE = 'Each set'
# What the Figure sheet says of a plot that has no sheet (NOT_YET: a plot type whose
# numbers nothing lays out)
NOT_YET = 'The numbers of this plot are not in this workbook yet.'
NO_NUMBERS = 'A space for a drawing has no numbers.'
NO_TESTS = 'No plot of this figure has a test.'
# The type Excel's T.TEST takes for each test (its fourth input)
PAIRED_KIND = 1
TEST_KINDS = {'student': 2, 'welch': 3}
PAIRED_NAME = 'Paired t-test'
# The digits of a power written in a plot's text ('min$^{-1}$'), as plain characters
POWER_PATTERN = re.compile(r'\$\^\{?(-?\d+)\}?\$')
POWER_CHARACTERS = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
UNIT_PATTERN = re.compile(r'\(([^()]*)\)\s*$')
# The columns of the Tests sheet, in order; the places of those the formulas read
TEST_HEADINGS = ('Plot',
                 'Measurement',
                 'Region or time point',
                 'First set',
                 'Second set',
                 'Test',
                 'n of the first set',
                 'n of the second set',
                 'Mean of the first set',
                 'Mean of the second set',
                 't',
                 'Degrees of freedom',
                 'p',
                 'p by Excel',
                 'Place of p in its plot (smallest = 1)',
                 'p × tests left (tests of the plot − place + 1)',
                 'Corrected p (Holm)',
                 'Corrected p by Excel',
                 'Mark on the plot',
                 )
EXCEL_P_COLUMN = 13
PLACE_COLUMN = 14
STEP_COLUMN = 15
TEST_NOTES = (
    "Every test of the figure, in the order drawn. 'p by Excel' is Excel's own "
    't-test (T.TEST) on the cells of the experiments in the sheet of the plot.',
    'Corrected p (Holm, MATHS.md section 11.5): the p values of one plot are '
    'placed smallest first; each is multiplied by the number of tests of the '
    'plot minus its place plus 1, is never smaller than the corrected p placed '
    'before it, and never above 1.',
    'A mark is drawn on the plot only where the corrected p is under 0.05.',
    )
# The Excel formula of a column of a table worked out from the cells beside it
TABLE_FORMULAS = {'mean': '=AVERAGE({0})',
                  'sd': '=_xlfn.STDEV.S({0})',
                  'sem': '=_xlfn.STDEV.S({0})/SQRT(COUNT({0}))',
                  }
# What the sheets of the plots without sets say
OWN_WORKBOOK = ('The numbers of this plot are in the workbook of the experiment, '
                '{0}/{0}.xlsx in the folder of this workbook: a sheet for each of its '
                'traces, its averages and how it was worked out.')
BACKGROUND_OFF = ('The measured difference and the fit are given with the background '
                  'taken off, as the plot draws them.')
BACKGROUND_ON = 'The measured difference and the fit are given with the background.'
BEFORE_STACKING = ('The lines are listed from the top of the plot down, each as it is '
                   'before the plot moves it to stack them (MATHS.md section 9.2).')
LINED_UP = ('Each experiment is read at the shared times, lined up on the additions '
            '(MATHS.md section 10.2). The mean of a set at one time is of its '
            'experiments that have a value there (MATHS.md section 10.3).')
LEFT_OUT_TRACES = ('Left out, for nothing to show for the trace and value picked or '
                   'another number of additions than most experiments of the plot: '
                   '{}.')
LEFT_OUT_SPECTRA = 'Left out, for having no difference spectrum: {}.'


# ---- CONTENT HELPERS -----------------------------------------------------------------


# ---- _bar_content_builder ------------------------------------------------------------
def _bar_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Bar chart for its sheet.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (bar_numbers_lister).

    ---- Globals read ----
    NO_VALUES (imported).

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _form_lines_lister
    _label_plainer
    _set_rows_lister
    _tests_lister
    """

    if not numbers['sets']:
        return {'lines': [], 'notes': [], 'sentence': NO_VALUES, 'blocks': []}
    label = _label_plainer(numbers['label'])
    rows, ranges = _set_rows_lister(numbers['sets'],
                                    [[one['values']] for one in numbers['sets']],
                                    )
    block = {'title': '',
             'headings': ['Set', 'Experiment', label],
             'rows': rows,
             'ranges': ranges,
             'columns': numbers['statistics']['columns'],
             'column_title': None,
             'label': label,
             'tests': _tests_lister(numbers['statistics'], label, numbers),
             }
    lines = [f'Measurement: {label}', f"Region: {numbers['region']}"]
    return {'lines': lines + _form_lines_lister(numbers),
            'notes': [],
            'sentence': None,
            'blocks': [block],
            }


# ---- _before_after_content_builder ---------------------------------------------------
def _before_after_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Before and after for its sheet: the
    two regions of each experiment side by side, with their difference as a formula.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (before_after_numbers_lister).

    ---- Globals read ----
    NO_PAIRS (imported).

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The difference of an experiment is its value in the second region minus its value
    in the first (MATHS.md section 11.4).

    ---- Helpers ----
    _form_lines_lister
    _label_plainer
    _set_rows_lister
    _tests_lister
    """

    if not numbers['sets']:
        return {'lines': [], 'notes': [], 'sentence': NO_PAIRS, 'blocks': []}
    label = _label_plainer(numbers['label'])
    first, second = (_label_plainer(words) for words in numbers['regions'])
    rows, ranges = _set_rows_lister(
        numbers['sets'],
        [[one['before'], one['after']] for one in numbers['sets']],
        )
    for cells in rows:
        before, after = cells[2], cells[3]
        cells.append(('difference',
                      None if before is None or after is None else after - before,
                      ),
                     )
    block = {'title': '',
             'headings': ['Set',
                          'Experiment',
                          f'{first}: {label}',
                          f'{second}: {label}',
                          f'Second region − first region: {label}',
                          ],
             'rows': rows,
             'ranges': ranges,
             'columns': numbers['statistics']['columns'],
             'column_title': 'Region',
             'label': label,
             'tests': _tests_lister(numbers['statistics'], label, numbers),
             }
    lines = [f'Measurement: {label}', f'Regions: {first}, then {second}']
    return {'lines': lines + _form_lines_lister(numbers),
            'notes': [],
            'sentence': None,
            'blocks': [block],
            }


# ---- _difference_content_builder -----------------------------------------------------
def _difference_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Difference spectrum for its sheet:
    the wavelength, then the difference and each part its form ticks, and whether
    the background is taken off.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (difference_numbers_lister).

    ---- Globals read ----
    BACKGROUND_OFF, BACKGROUND_ON.

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_plainer
    """

    if numbers['sentence'] is not None:
        return {'lines': [], 'notes': [], 'sentence': numbers['sentence'], 'blocks': []}
    background = BACKGROUND_ON if numbers['is_background_shown'] else BACKGROUND_OFF
    lines = [f"Experiment: {numbers['name']}",
             f'Reduced minus oxidised, in mOD (MATHS.md section 9). {background}',
             ]
    if numbers['bands']:
        bands = '; '.join(f'{_label_plainer(haem)} {low:g} to {high:g}'
                          for haem, (low, high) in numbers['bands'].items()
                          )
        lines.append(f'Haem bands (nm): {bands}')
    columns = [{'heading': 'Wavelength (nm)', 'values': numbers['wavelengths_nm']}]
    columns += [{'heading': f'{_label_plainer(name)} (mOD)', 'values': values}
                for name, values in numbers['columns']
                ]
    return {'lines': lines,
            'notes': [],
            'sentence': None,
            'blocks': [],
            'table': {'title': '', 'columns': columns},
            }


# ---- _form_lines_lister --------------------------------------------------------------
def _form_lines_lister(numbers: dict) -> List[str]:
    """
    ---- Summary ----
    Helper function to write the lines at the top of a sheet that say what the form of
    the plot picked: the kind of averaging region, the bars and the test.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot, with its 'kind' and, but for a Before and after,
        its 'error' and 'test'.

    ---- Globals read ----
    ERROR_CHOICES, PAIRED_WORDS, TEST_WORDS (imported).

    ---- Outputs ----
    List[str]
        The lines.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    lines = [f"Kind of averaging region after an addition: {numbers['kind']}"]
    if 'test' not in numbers:
        return lines + [f'Test between the two regions of each set: {PAIRED_WORDS}']
    return lines + [f"Bars on the plot: mean ± {dict(ERROR_CHOICES)[numbers['error']]}",
                    f"Test between two sets: {TEST_WORDS[numbers['test']]}",
                    ]


# ---- _label_plainer ------------------------------------------------------------------
def _label_plainer(text: str) -> str:
    """
    ---- Summary ----
    Helper function to write a text of a plot in plain characters for a cell: a power
    as raised digits ('min$^{-1}$' becomes 'min⁻¹') and a haem name without its
    plotting codes ('Cyt $b_H$' becomes 'Cyt bH').

    ---- Inputs ----
    text : str
        The text as the plot draws it.

    ---- Globals read ----
    POWER_CHARACTERS, POWER_PATTERN.

    ---- Outputs ----
    str
        The plain text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    haem_name_plainer
    """

    raised = POWER_PATTERN.sub(lambda found: found.group(1).translate(POWER_CHARACTERS),
                               str(text),
                               )
    return haem_name_plainer(raised)


# ---- _mean_content_builder -----------------------------------------------------------
def _mean_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Mean trace for its sheet: the shared
    time, then for each set the lined-up trace of each of its experiments, their
    mean and the band, and beside them the mean and the band as Excel formulas over
    the cells of the experiments in the same row.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (mean_lines_lister).

    ---- Globals read ----
    LEFT_OUT_TRACES, LINED_UP; BAND_CHOICES, NO_MEAN (imported).

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None: see _table_writer for the Excel formulas.

    ---- Helpers ----
    _label_plainer
    _minutes_writer
    """

    # ---- 1 What the form picked ------------------------------------------------------
    lines = [line for line in numbers['lines'] if np.isfinite(line['mean']).any()]
    notes = []
    if numbers['left_out']:
        notes.append(LEFT_OUT_TRACES.format(', '.join(numbers['left_out'])))
    if not lines:
        return {'lines': [], 'notes': notes, 'sentence': NO_MEAN, 'blocks': []}
    label, band = _label_plainer(numbers['label']), numbers['band']
    words = dict(BAND_CHOICES)[band]
    texts = [f'Trace: {label}',
             f"Band on the plot: {'none' if band == 'none' else f'mean ± {words}'}",
             ]
    if numbers['additions_min']:
        texts.append('Additions at (minutes, on the shared time): '
                     f"{_minutes_writer(numbers['additions_min'])}",
                     )
    if numbers['breaks_min']:
        texts.append('The spare middle of a longer gap between two additions is left '
                     'out at (minutes, on the shared time): '
                     f"{_minutes_writer(numbers['breaks_min'])}",
                     )
    texts.append(LINED_UP)

    # ---- 2 The shared time, then each set --------------------------------------------
    columns = [{'heading': _label_plainer(numbers['time_label']),
                'values': numbers['times_min'],
                },
               ]
    for line in lines:
        first = len(columns)
        columns += [{'heading': f"{line['name']}, {name}: {label}", 'values': trace}
                    for name, trace in zip(line['names'], line['traces'])
                    ]
        over = (first, len(columns) - 1)
        spread = line['spread']
        has_band = spread is not None and bool(np.isfinite(spread).any())
        columns.append({'heading': f"{line['name']}, mean: {label}",
                        'values': line['mean'],
                        },
                       )
        if has_band:
            columns.append({'heading': f"{line['name']}, {words}: {label}",
                            'values': spread,
                            },
                           )
        columns.append({'heading': f"{line['name']}, mean by Excel: {label}",
                        'values': line['mean'],
                        'formula': 'mean',
                        'over': over,
                        },
                       )
        if has_band:
            columns.append({'heading': f"{line['name']}, {words} by Excel: {label}",
                            'values': spread,
                            'formula': band,
                            'over': over,
                            },
                           )
    return {'lines': texts,
            'notes': notes,
            'sentence': None,
            'blocks': [],
            'table': {'title': '', 'columns': columns},
            }


# ---- _minutes_writer -----------------------------------------------------------------
def _minutes_writer(times_min: Any) -> str:
    """
    ---- Summary ----
    Helper function to write a list of times in a line of a sheet.

    ---- Inputs ----
    times_min : Any
        The times, in minutes.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The times with a comma between them, each with as many decimals as it needs
        ('0, 5.5').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return ', '.join(f'{round(float(moment), 4):g}' for moment in times_min)


# ---- _response_content_builder -------------------------------------------------------
def _response_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Response by region for its sheet: one
    block per row of the plot (the OCR, or each haem), with a column per region.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (response_numbers_lister).

    ---- Globals read ----
    NO_RESPONSE (imported).

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _form_lines_lister
    _label_plainer
    _set_rows_lister
    _tests_lister
    """

    if not numbers['rows']:
        return {'lines': [], 'notes': [], 'sentence': NO_RESPONSE, 'blocks': []}
    regions = [_label_plainer(words) for words in numbers['regions']]
    blocks = []
    for row in numbers['rows']:
        label = _label_plainer(row['label'])
        rows, ranges = _set_rows_lister(row['sets'],
                                        [one['regions'] for one in row['sets']],
                                        )
        blocks.append({'title': label,
                       'headings': ['Set', 'Experiment'] + [f'{region}: {label}'
                                                            for region in regions
                                                            ],
                       'rows': rows,
                       'ranges': ranges,
                       'columns': row['statistics']['columns'],
                       'column_title': 'Region',
                       'label': label,
                       'tests': _tests_lister(row['statistics'], label, numbers),
                       },
                      )
    notes = []
    if numbers['left_out']:
        notes.append('Left out, for another number of additions than most experiments '
                     f"of the plot: {', '.join(numbers['left_out'])}.",
                     )
    if numbers['differing']:
        notes.append('Other additions than the first experiment of the plot, which '
                     f"names the regions: {', '.join(numbers['differing'])}.",
                     )
    lines = [f"Regions: {', '.join(regions)}"]
    return {'lines': lines + _form_lines_lister(numbers),
            'notes': notes,
            'sentence': None,
            'blocks': blocks,
            }


# ---- _set_rows_lister ----------------------------------------------------------------
def _set_rows_lister(
    sets: List[dict],
    values: List[List[List[Optional[float]]]],
    ) -> Tuple[List[list], Dict[Tuple[int, str], Tuple[int, int, int]]]:
    """
    ---- Summary ----
    Helper function to list the experiments of each set one under the other, each
    with its value in each column of the plot, and to note which cells hold the
    values of each set in each column.

    ---- Inputs ----
    sets : List[dict]
        The sets of the plot (plot_set, DATA_FORMAT.md).
    values : List[List[List[Optional[float]]]]
        For each set, for each column of the plot, the value of each of its
        experiments (None for none).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[List[list], Dict[Tuple[int, str], Tuple[int, int, int]]]
        (the rows of the table: the name of the set, the experiment, then its value
        in each column; {(column of the plot, name of the set): (its first row, its
        last row, its column in the table)}, the rows from 0).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    rows: List[list] = []
    ranges = {}
    for one, columns in zip(sets, values):
        first, last = len(rows), len(rows) + len(one['names']) - 1
        for place in range(len(columns)):
            ranges[(place, one['name'])] = (first, last, 2 + place)
        for index, name in enumerate(one['names']):
            rows.append([one['name'], name] + [column[index] for column in columns])
    return rows, ranges


# ---- _standard_content_builder -------------------------------------------------------
def _standard_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the sheet of a Standard experiment: its experiment,
    the panels it draws and where its numbers are, the experiment's own workbook.
    The traces are not copied in, so each number is kept in one place.

    ---- Inputs ----
    numbers : dict
        What the plot shows (standard_numbers_lister).

    ---- Globals read ----
    OWN_WORKBOOK.

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_plainer
    file_name_sanitiser
    """

    if numbers['sentence'] is not None:
        return {'lines': [], 'notes': [], 'sentence': numbers['sentence'], 'blocks': []}
    panels = ', '.join(_label_plainer(panel) for panel in numbers['panels'])
    lines = [f"Experiment: {numbers['name']}", f'Panels: {panels}']
    if numbers['view'] is not None:
        lines.append(f"Haems shown as: {numbers['view']}")
    lines.append(OWN_WORKBOOK.format(file_name_sanitiser(numbers['name'])))
    return {'lines': lines, 'notes': [], 'sentence': None, 'blocks': []}


# ---- _tests_lister -------------------------------------------------------------------
def _tests_lister(statistics: dict, measurement: str, numbers: dict) -> List[dict]:
    """
    ---- Summary ----
    Helper function to list the tests of one block of a plot for the Tests sheet,
    each with the two sets it compares and where their values are.

    ---- Inputs ----
    statistics : dict
        The numbers of the block (plot_statistics, DATA_FORMAT.md).
    measurement : str
        What the block measures, with its unit.
    numbers : dict
        The numbers of the plot, for its 'marks' and, but for a paired plot, its
        'test'.

    ---- Globals read ----
    PAIRED_KIND, PAIRED_NAME, TEST_KINDS; TEST_CHOICES (imported).

    ---- Outputs ----
    List[dict]
        One per test: 'measurement', 'column' (its region or time point), 'first'
        and 'second' (the two sets), 'words' (the test), 'counts' and 'means' (of
        the two sets), 't', 'df', 'p', 'p_corrected', 'mark' (as on the plot),
        'kind' (the type Excel's T.TEST takes) and 'keys' (the two sets as
        _set_rows_lister notes their cells).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_plainer
    p_value_marker
    """

    columns = statistics['columns']
    labels = [_label_plainer(column['label']) for column in columns]
    listed = []
    for result in statistics['tests']:
        if statistics['is_paired']:
            places, names = (0, 1), (result['set'], result['set'])
            shown = [f'{name} ({labels[place]})' for place, name in zip(places, names)]
            column = f'{labels[0]}, then {labels[1]}'
            words, kind = PAIRED_NAME, PAIRED_KIND
        else:
            places = (result['column'], result['column'])
            names = (result['first'], result['second'])
            shown, column = list(names), labels[result['column']]
            words, kind = dict(TEST_CHOICES,
                               )[numbers['test']], TEST_KINDS[numbers['test']]
        members = [next(one for one in columns[place]['sets'] if one['name'] == name)
                   for place, name in zip(places, names)
                   ]
        listed.append({'measurement': measurement,
                       'column': column,
                       'first': shown[0],
                       'second': shown[1],
                       'words': words,
                       'counts': ((result['n'], result['n'])
                                  if statistics['is_paired']
                                  else tuple(one['n'] for one in members)
                                  ),
                       'means': tuple(one['mean'] for one in members),
                       't': result['t'],
                       'df': result['df'],
                       'p': result['p'],
                       'p_corrected': result['p_corrected'],
                       'mark': p_value_marker(result['p_corrected'], numbers['marks']),
                       'kind': kind,
                       'keys': tuple(zip(places, names)),
                       },
                      )
    return listed


# ---- _time_points_content_builder ----------------------------------------------------
def _time_points_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Time points for its sheet: the
    experiments of each set in the order of the time points, so those of one set at
    one time point sit one under the other; an experiment without a time point comes
    last in its set and is in no mean.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (time_points_numbers_lister).

    ---- Globals read ----
    NO_POINTS (imported).

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _form_lines_lister
    _label_plainer
    _tests_lister
    """

    if not numbers['sets']:
        return {'lines': [], 'notes': [], 'sentence': NO_POINTS, 'blocks': []}
    label, points = _label_plainer(numbers['label']), numbers['time_points']
    rows: List[list] = []
    ranges = {}
    for one in numbers['sets']:
        members = sorted(zip(one['names'], one['points'], one['values']),
                         key=lambda member: (points.index(member[1])
                                             if member[1] in points
                                             else len(points)
                                             ),
                         )
        for place, point in enumerate(points):
            count = sum(1 for member in members if member[1] == point)
            if count:
                start = len(rows)
                rows.extend([one['name'], name, own, number]
                            for name, own, number in members
                            if own == point
                            )
                ranges[(place, one['name'])] = (start, start + count - 1, 3)
        rows.extend([one['name'], name, own, number]
                    for name, own, number in members
                    if own not in points
                    )
    block = {'title': '',
             'headings': ['Set', 'Experiment', 'Time point', label],
             'rows': rows,
             'ranges': ranges,
             'columns': numbers['statistics']['columns'],
             'column_title': 'Time point',
             'label': label,
             'tests': _tests_lister(numbers['statistics'], label, numbers),
             }
    lines = [f'Measurement: {label}', f"Region: {numbers['region']}"]
    return {'lines': lines + _form_lines_lister(numbers),
            'notes': [],
            'sentence': None,
            'blocks': [block],
            }


# ---- _trace_content_builder ----------------------------------------------------------
def _trace_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Single trace for its sheet: the
    time as the plot counts it and the value; with time 0 at an addition, also the
    time in the file, which is the one in the experiment's own workbook.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (trace_numbers_lister).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Time in the file = time on the plot + the time of the addition picked.

    ---- Helpers ----
    _label_plainer
    _minutes_writer
    """

    if numbers['sentence'] is not None:
        return {'lines': [], 'notes': [], 'sentence': numbers['sentence'], 'blocks': []}
    label = _label_plainer(numbers['label'])
    lines = [f"Experiment: {numbers['name']}", f'Trace: {label}']
    if numbers['additions_min']:
        lines.append('Additions at (minutes, on the time of the plot): '
                     f"{_minutes_writer(numbers['additions_min'])}",
                     )
    columns = [{'heading': _label_plainer(numbers['time_label']),
                'values': numbers['times_min'],
                },
               {'heading': label, 'values': numbers['values']},
               ]
    if numbers['shift_min']:
        lines.append('Time 0 of the plot is at '
                     f"{_minutes_writer([numbers['shift_min']])} minutes in the file.",
                     )
        columns.insert(0,
                       {'heading': 'Time in the file (minutes)',
                        'values': numbers['times_min'] + numbers['shift_min'],
                        },
                       )
    return {'lines': lines,
            'notes': [],
            'sentence': None,
            'blocks': [],
            'table': {'title': '', 'columns': columns},
            }


# ---- _waterfall_content_builder ------------------------------------------------------
def _waterfall_content_builder(numbers: dict) -> dict:
    """
    ---- Summary ----
    Helper function to lay out the numbers of a Waterfall for its sheet: the
    wavelength or the shared time, then each line from the top of the plot down, as
    it is before the stacking. Lines that are not all at the same wavelengths each
    have their own wavelength column.

    ---- Inputs ----
    numbers : dict
        The numbers of the plot (waterfall_numbers_lister).

    ---- Globals read ----
    BEFORE_STACKING, LEFT_OUT_SPECTRA, LEFT_OUT_TRACES.

    ---- Outputs ----
    dict
        The content of the sheet (_plot_sheet_writer).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _label_plainer
    _minutes_writer
    """

    # ---- 1 What it shows and what it left out ----------------------------------------
    notes = []
    if numbers['left_out']:
        words = LEFT_OUT_SPECTRA if numbers['is_spectra'] else LEFT_OUT_TRACES
        notes.append(words.format(', '.join(numbers['left_out'])))
    if numbers['sentence'] is not None:
        return {'lines': [],
                'notes': notes,
                'sentence': numbers['sentence'],
                'blocks': [],
                }
    label, x_label = (_label_plainer(numbers[key]) for key in ('label', 'x_label'))
    lines = [f'Each line: {label}', BEFORE_STACKING]
    if numbers['additions_min']:
        lines.append('Additions at (minutes, on the shared time): '
                     f"{_minutes_writer(numbers['additions_min'])}",
                     )

    # ---- 2 One column of wavelengths or times when every line has the same -----------
    first = numbers['lines'][0]['x']
    is_shared = all(line['x'].shape == first.shape and np.allclose(line['x'], first)
                    for line in numbers['lines']
                    )
    columns = [{'heading': x_label, 'values': first}] if is_shared else []
    for line in numbers['lines']:
        if not is_shared:
            columns.append({'heading': f"{line['label']}: {x_label}",
                            'values': line['x'],
                            },
                           )
        columns.append({'heading': f"{line['label']}: {label}",
                        'values': line['values'],
                        },
                       )
    return {'lines': lines,
            'notes': notes,
            'sentence': None,
            'blocks': [],
            'table': {'title': '', 'columns': columns},
            }


# ---- SHEET HELPERS -------------------------------------------------------------------


# ---- _block_writer -------------------------------------------------------------------
def _block_writer(sheet: Any,
                  formats: dict,
                  top: int,
                  block: dict,
                  ) -> Tuple[int, Dict[Tuple[int, str], str]]:
    """
    ---- Summary ----
    Helper function to write one block of a plot's sheet: the table of every
    experiment, then the table of every set with its n, mean, SD and SEM as the
    program worked them out and, beside them, as Excel formulas over the cells of
    its experiments.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    formats : dict
        The cell formats (workbook_formats_builder, with 'bold').
    top : int
        The first row of the block (from 0).
    block : dict
        'title' (what it measures; '' for none), 'headings' and 'rows' of the
        table of experiments (a cell is a text, a number, None for an empty cell,
        or ('difference', value) for the cell before it minus the one before
        that), 'ranges' (_set_rows_lister), 'columns' (those of its
        plot_statistics, DATA_FORMAT.md), 'column_title' (the heading of the
        column that names them; None to leave it out) and 'label' (the
        measurement with its unit).

    ---- Globals read ----
    EXPERIMENTS_TITLE, SETS_TITLE, UNIT_PATTERN.

    ---- Outputs ----
    Tuple[int, Dict[Tuple[int, str], str]]
        (the first free row under the block, {(column of the plot, name of the
        set): the cells of its values, as '$C$6:$C$8'}).

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    Mean: =AVERAGE(cells); SD: =STDEV.S(cells); SEM: =STDEV.S(cells)/SQRT(COUNT(cells))
    (MATHS.md section 11.2).

    ---- Helpers ----
    _label_plainer
    formula_writer
    number_writer
    """

    # ---- 1 Every experiment ----------------------------------------------------------
    row = top
    if block['title']:
        sheet.write_string(row, 0, block['title'], formats['title'])
        row += 1
    sheet.write_string(row, 0, EXPERIMENTS_TITLE, formats['bold'])
    for column, heading in enumerate(block['headings']):
        sheet.write_string(row + 1, column, heading, formats['header'])
    first = row + 2
    for place, cells in enumerate(block['rows']):
        for column, cell in enumerate(cells):
            if isinstance(cell, tuple):
                if cell[1] is not None:
                    formula_writer(sheet,
                                   first + place,
                                   column,
                                   f'={xl_rowcol_to_cell(first + place, column - 1)}'
                                   f'-{xl_rowcol_to_cell(first + place, column - 2)}',
                                   cell[1],
                                   formats['number'],
                                   )
            elif isinstance(cell, str):
                sheet.write_string(first + place, column, cell, formats['text'])
            elif cell is not None:
                number_writer(sheet, first + place, column, cell, formats['number'])
    cells_of = {key: xl_range_abs(first + start, column, first + end, column)
                for key, (start, end, column) in block['ranges'].items()
                }

    # ---- 2 Every set -----------------------------------------------------------------
    row = first + len(block['rows']) + 1
    found = UNIT_PATTERN.search(block['label'])
    unit = f' ({found.group(1)})' if found else ''
    names = ['Set'] + ([block['column_title']] if block['column_title'] else [])
    headings = names + ['n'] + [f'{words}{unit}'
                                for words in ('Mean',
                                              'SD',
                                              'SEM',
                                              'Mean by Excel',
                                              'SD by Excel',
                                              'SEM by Excel',
                                              )
                                ]
    sheet.write_string(row, 0, SETS_TITLE, formats['bold'])
    for column, heading in enumerate(headings):
        sheet.write_string(row + 1, column, heading, formats['header'])
    row += 2
    start = len(names)
    for place, column in enumerate(block['columns']):
        for one in column['sets']:
            sheet.write_string(row, 0, one['name'], formats['text'])
            if block['column_title']:
                sheet.write_string(row,
                                   1,
                                   _label_plainer(column['label']),
                                   formats['text'],
                                   )
            number_writer(sheet, row, start, one['n'], formats['integer'])
            for step, key in enumerate(('mean', 'sd', 'sem'), start=1):
                number_writer(sheet, row, start + step, one[key], formats['number'])
            cells = cells_of.get((place, one['name']))
            if cells and one['n']:
                formula_writer(sheet,
                               row,
                               start + 4,
                               f'=AVERAGE({cells})',
                               one['mean'],
                               formats['number'],
                               )
            if cells and one['n'] > 1:
                formula_writer(sheet,
                               row,
                               start + 5,
                               f'=_xlfn.STDEV.S({cells})',
                               one['sd'],
                               formats['number'],
                               )
                formula_writer(sheet,
                               row,
                               start + 6,
                               f'=_xlfn.STDEV.S({cells})/SQRT(COUNT({cells}))',
                               one['sem'],
                               formats['number'],
                               )
            row += 1
    return row + 1, cells_of


# ---- _figure_sheet_writer ------------------------------------------------------------
def _figure_sheet_writer(sheet: Any,
                         formats: dict,
                         title: str,
                         listed: List[dict],
                         lines: List[str],
                         notes: List[str],
                         ) -> None:
    """
    ---- Summary ----
    Helper function to write the first sheet of the workbook: one row per plot with
    its letter, its plot type, a link to its sheet and its sentences for the
    caption; then the lines of the caption that are of the whole figure, and the
    experiments left out.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    formats : dict
        The cell formats (workbook_formats_builder, with 'bold').
    title : str
        The title of the sheet.
    listed : List[dict]
        One per plot, in the order of the letters: 'letter', 'type' (its name),
        'sheet' (the name of its sheet; '' for none), 'words' (what is said in
        place of a sheet) and 'caption' (its sentences; '' for none).
    lines : List[str]
        The caption lines of the whole figure (the colours, line styles, shades).
    notes : List[str]
        What was left out, one sentence each.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    sheet.write_string(0, 0, title, formats['title'])
    for column, heading in enumerate(('Plot', 'Plot type', 'Sheet', 'For the caption')):
        sheet.write_string(2, column, heading, formats['header'])
    row = 3
    for entry in listed:
        sheet.write_string(row, 0, entry['letter'], formats['text'])
        sheet.write_string(row, 1, entry['type'], formats['text'])
        if entry['sheet']:
            name = entry['sheet'].replace("'", "''")
            sheet.write_url(row, 2, f"internal:'{name}'!A1", string=entry['sheet'])
        else:
            sheet.write_string(row, 2, entry['words'], formats['text'])
        sheet.write_string(row, 3, entry['caption'], formats['text'])
        row += 1
    for heading, texts in (('For the caption, of the whole figure', lines),
                           ('Left out', notes),
                           ):
        if texts:
            sheet.write_string(row + 1, 0, heading, formats['bold'])
            for place, text in enumerate(texts):
                sheet.write_string(row + 2 + place, 0, text, formats['text'])
            row += 2 + len(texts)
    sheet.set_column(0, 0, 8)
    sheet.set_column(1, 2, 28)
    sheet.set_column(3, 3, 100)


# ---- _plot_sheet_writer --------------------------------------------------------------
def _plot_sheet_writer(sheet: Any,
                       formats: dict,
                       name: str,
                       title: str,
                       content: dict,
                       ) -> List[dict]:
    """
    ---- Summary ----
    Helper function to write the sheet of one plot: its title, what its form picked,
    what it left out, then each of its blocks; or, for a plot with nothing to show,
    the sentence the plot shows.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    formats : dict
        The cell formats (workbook_formats_builder, with 'bold').
    name : str
        The name of the sheet.
    title : str
        Its title: the letter of the plot and its plot type.
    content : dict
        'lines' (what the form picked), 'notes' (what was left out), 'sentence'
        (in place of the numbers; None when there are numbers), 'blocks'
        (_block_writer, each with its 'tests' from _tests_lister) and, for a plot
        without sets, 'table' (_table_writer), written under the blocks.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[dict]
        The tests of the plot (_tests_lister), each with 'cells': the cells of the
        values of its two sets, with the name of the sheet
        ("'a Bar chart'!$C$6:$C$8").

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _block_writer
    _table_writer
    """

    sheet.write_string(0, 0, title, formats['title'])
    texts = [content['sentence']] if content['sentence'] else []
    texts = content['lines'] + content['notes'] + texts
    for place, text in enumerate(texts):
        sheet.write_string(1 + place, 0, text, formats['text'])
    row = len(texts) + 2
    quoted = "'" + name.replace("'", "''") + "'!"
    tests = []
    for block in content['blocks']:
        row, cells_of = _block_writer(sheet, formats, row, block)
        for result in block['tests']:
            tests.append(dict(result,
                              cells=tuple(quoted + cells_of[key]
                                          for key in result['keys']
                                          ),
                              ),
                         )
    table = content.get('table')
    if table is not None:
        _table_writer(sheet, formats, row, table)
    sheet.set_column(0, 1, 24)
    sheet.set_column(2, max(12, len(table['columns']) if table else 0), 18)
    return tests


# ---- _table_writer -------------------------------------------------------------------
def _table_writer(sheet: Any, formats: dict, top: int, table: dict) -> int:
    """
    ---- Summary ----
    Helper function to write the one table of a plot without sets: a heading per
    column, then its numbers down the rows. A column worked out from the cells
    beside it is written as an Excel formula, with the program's number kept in it.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    formats : dict
        The cell formats (workbook_formats_builder, with 'bold').
    top : int
        The first row of the table (from 0).
    table : dict
        'title' ('' for none) and 'columns', each {'heading', 'values': its numbers
        down the rows (NaN for an empty cell)} and, for a column that is a formula,
        'formula' (a key of TABLE_FORMULAS) and 'over' (the first and the last
        column of the table, from 0, it is worked out from, in the same row). The
        columns need not be as long as one another.

    ---- Globals read ----
    TABLE_FORMULAS.

    ---- Outputs ----
    int
        The first free row under the table.

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    Mean: =AVERAGE(cells); SD: =STDEV.S(cells); SEM: =STDEV.S(cells)/SQRT(COUNT(cells))
    (MATHS.md section 10.3). A formula is written only where the program has a
    number, so a time with no value, or a spread of one experiment, stays empty.

    ---- Helpers ----
    formula_writer
    number_writer
    """

    row = top
    if table['title']:
        sheet.write_string(row, 0, table['title'], formats['bold'])
        row += 1
    sheet.set_row(row, 48)
    first, longest = row + 1, 0
    for place, column in enumerate(table['columns']):
        sheet.write_string(row, place, column['heading'], formats['header'])
        values = np.asarray(column['values'], dtype=float)
        longest = max(longest, len(values))
        over = column.get('over')
        for step, value in enumerate(values):
            if over is None:
                number_writer(sheet, first + step, place, value, formats['number'])
            elif np.isfinite(value):
                cells = xl_range(first + step, over[0], first + step, over[1])
                formula_writer(sheet,
                               first + step,
                               place,
                               TABLE_FORMULAS[column['formula']].format(cells),
                               value,
                               formats['number'],
                               )
    return first + longest + 1


# ---- _tests_sheet_writer -------------------------------------------------------------
def _tests_sheet_writer(sheet: Any,
                        formats: dict,
                        plots: List[Tuple[str, List[dict]]],
                        ) -> None:
    """
    ---- Summary ----
    Helper function to write the sheet of the tests: one row per test of the figure,
    with t, the degrees of freedom, p and the corrected p as the program worked them
    out and, beside them, p and the corrected p as Excel formulas.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    formats : dict
        The cell formats (workbook_formats_builder, with 'bold').
    plots : List[Tuple[str, List[dict]]]
        (the letter of a plot, its tests from _plot_sheet_writer), in the order of
        the letters.

    ---- Globals read ----
    EXCEL_P_COLUMN, NO_TESTS, PLACE_COLUMN, STEP_COLUMN, TEST_HEADINGS, TEST_NOTES,
    TESTS_SHEET.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    p by Excel: =T.TEST(first set, second set, 2, type), type 1 for the paired test,
    2 for Student's, 3 for Welch's (MATHS.md sections 11.3 and 11.4). With the m
    tests of one plot: place = RANK.EQ(p, the p values of the plot, smallest first);
    step = p x (m - place + 1); corrected p = min(1, the largest step among the
    tests of the plot whose p is not above this one) (MATHS.md section 11.5).

    ---- Helpers ----
    formula_writer
    number_writer
    """

    # ---- 1 The notes and the headings ------------------------------------------------
    sheet.write_string(0, 0, TESTS_SHEET, formats['title'])
    for place, note in enumerate(TEST_NOTES):
        sheet.write_string(1 + place, 0, note, formats['text'])
    top = len(TEST_NOTES) + 2
    for column, heading in enumerate(TEST_HEADINGS):
        sheet.write_string(top, column, heading, formats['header'])
    sheet.set_row(top, 48)
    sheet.set_column(0, 0, 8)
    sheet.set_column(1, len(TEST_HEADINGS) - 1, 20)
    if not any(tests for _, tests in plots):
        sheet.write_string(top + 1, 0, NO_TESTS, formats['text'])
        return

    # ---- 2 Each test, plot by plot ---------------------------------------------------
    row = top + 1
    for letter, tests in plots:
        last = row + len(tests) - 1
        p_cells = xl_range_abs(row, EXCEL_P_COLUMN, last, EXCEL_P_COLUMN)
        step_cells = xl_range_abs(row, STEP_COLUMN, last, STEP_COLUMN)
        for result in tests:
            place = 1 + sum(1 for other in tests if other['p'] < result['p'])
            texts = (letter,
                     result['measurement'],
                     result['column'],
                     result['first'],
                     result['second'],
                     result['words'],
                     )
            for column, text in enumerate(texts):
                sheet.write_string(row, column, text, formats['text'])
            for column, number in enumerate(result['counts'], start=6):
                number_writer(sheet, row, column, number, formats['integer'])
            for column, number in enumerate(result['means'], start=8):
                number_writer(sheet, row, column, number, formats['number'])
            number_writer(sheet, row, 10, result['t'], formats['number'])
            number_writer(sheet, row, 11, result['df'], formats['number'])
            number_writer(sheet, row, 12, result['p'], formats['p_value'])
            formula_writer(sheet,
                           row,
                           EXCEL_P_COLUMN,
                           f"=_xlfn.T.TEST({result['cells'][0]},{result['cells'][1]},2,"
                           f"{result['kind']})",
                           result['p'],
                           formats['p_value'],
                           )
            own = xl_rowcol_to_cell(row, EXCEL_P_COLUMN)
            formula_writer(sheet,
                           row,
                           PLACE_COLUMN,
                           f'=_xlfn.RANK.EQ({own},{p_cells},1)',
                           place,
                           formats['integer'],
                           )
            formula_writer(sheet,
                           row,
                           STEP_COLUMN,
                           f'={own}*(COUNT({p_cells})'
                           f'-{xl_rowcol_to_cell(row, PLACE_COLUMN)}+1)',
                           result['p'] * (len(tests) - place + 1),
                           formats['p_value'],
                           )
            number_writer(sheet, row, 16, result['p_corrected'], formats['p_value'])
            formula_writer(sheet,
                           row,
                           17,
                           f'=MIN(1,SUMPRODUCT(MAX(({p_cells}<={own})*{step_cells})))',
                           result['p_corrected'],
                           formats['p_value'],
                           )
            sheet.write_string(row, 18, result['mark'], formats['text'])
            row += 1


# ---- MAIN FUNCTIONS ------------------------------------------------------------------
# What lists the numbers of each plot type that has a sheet, and what lays them out
CONTENT_BUILDERS = {'P1': (standard_numbers_lister, _standard_content_builder),
                    'P2': (difference_numbers_lister, _difference_content_builder),
                    'P3': (waterfall_numbers_lister, _waterfall_content_builder),
                    'P7': (trace_numbers_lister, _trace_content_builder),
                    'P8': (mean_lines_lister, _mean_content_builder),
                    'P9': (bar_numbers_lister, _bar_content_builder),
                    'P10': (before_after_numbers_lister, _before_after_content_builder),
                    'P11': (response_numbers_lister, _response_content_builder),
                    'P12': (time_points_numbers_lister, _time_points_content_builder),
                    }


# ---- dataset_workbook_exporter -------------------------------------------------------
def dataset_workbook_exporter(page: FigurePage,
                              folder: Path,
                              setup: Optional[dict] = None,
                              experiments: Optional[Dict[str, dict]] = None,
                              answers: Optional[dict] = None,
                              ) -> Path:
    """
    ---- Summary ----
    Main function to write the workbook of a dataset figure, so its numbers can be
    worked out again by hand: a first sheet that lists the plots, a sheet for each
    plot, and a last sheet with every test. A plot per region (Bar chart, Before
    and after, Response by region, Time points) has the number of every experiment
    and the n, mean, SD and SEM of each set; a Single trace, a Mean trace (with the
    lined-up trace of every experiment behind each mean), a Difference spectrum and
    a Waterfall have one table of what they draw; a Standard experiment names the
    experiment's own workbook, where its traces are. Each mean, SD, SEM, p and
    corrected p is written as the program worked it out and, beside it, as an Excel
    formula over the cells of the experiments. The numbers are those the plots are
    drawn from.

    ---- Inputs ----
    page : FigurePage
        The page; it must hold at least one plot.
    folder : Path
        Folder the workbook is saved in; it is made when missing.
    setup : Optional[dict]
        The set-up table (dataset_setup, DATA_FORMAT.md); None for none.
    experiments : Optional[Dict[str, dict]]
        {experiment name: its slim copy} (page_experiment, DATA_FORMAT.md); None
        for none.
    answers : Optional[dict]
        The answers of the run; None for none.

    ---- Globals read ----
    CONTENT_BUILDERS, FIGURE_SHEET, NO_NUMBERS, NOT_YET, TESTS_SHEET; EMPTY_TYPES,
    PLOT_TYPES (imported).

    ---- Outputs ----
    Path
        The workbook that was saved (dataset workbook, DATA_FORMAT.md). Raises
        FigurePageError for a page with no plot, and OSError when the workbook
        cannot be written (a PermissionError when it is open in Excel).

    ---- Globals mutated ----
    None. Writes the workbook (side effect).

    ---- Equations ----
    None: see _block_writer and _tests_sheet_writer for the Excel formulas.

    ---- Helpers ----
    _figure_sheet_writer
    _plot_sheet_writer
    _tests_sheet_writer
    caption_lines_builder
    dataset_workbook_namer
    excel_sheet_namer
    page_experiments_lister
    panel_letters_finder
    workbook_formats_builder
    """

    # ---- 1 The workbook and its first sheet ------------------------------------------
    if not page.plots:
        raise FigurePageError('The page has no plot on it, so there are no numbers to '
                              'save.',
                              )
    experiments, answers = experiments or {}, answers or {}
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / dataset_workbook_namer(page.journal)
    workbook = xlsxwriter.Workbook(str(path))
    formats = dict(workbook_formats_builder(workbook),
                   bold=workbook.add_format({'bold': True}),
                   )
    used = {TESTS_SHEET.lower()}
    figure_sheet = workbook.add_worksheet(excel_sheet_namer(FIGURE_SHEET, used))

    # ---- 2 A sheet for each plot that has numbers ------------------------------------
    letters = panel_letters_finder(page)
    captions = caption_lines_builder(page, setup, experiments, answers)
    starts = tuple(f'{letter}: ' for letter in letters.values())
    listed, plots = [], []
    notes = [f'{name} could not be read, so it is in no plot.'
             for name in page_experiments_lister(page, setup)
             if experiments.get(name) is None
             ]
    for index in sorted(letters, key=lambda place: (page.plots[place].row,
                                                    page.plots[place].column,
                                                    )):
        plot, letter = page.plots[index], letters[index]
        kind = PLOT_TYPES.get(plot.plot_type, plot.plot_type)
        entry = {'letter': letter,
                 'type': kind,
                 'sheet': '',
                 'words': NO_NUMBERS if plot.plot_type in EMPTY_TYPES else NOT_YET,
                 'caption': ' '.join(line[len(letter) + 2:]
                                     for line in captions
                                     if line.startswith(f'{letter}: ')
                                     ),
                 }
        listed.append(entry)
        if plot.plot_type not in CONTENT_BUILDERS:
            continue
        lister, builder = CONTENT_BUILDERS[plot.plot_type]
        content = builder(lister(setup, plot.roles, experiments, answers))
        entry['sheet'] = excel_sheet_namer(f'{letter} {kind}', used)
        tests = _plot_sheet_writer(workbook.add_worksheet(entry['sheet']),
                                   formats,
                                   entry['sheet'],
                                   f'{letter}: {kind}',
                                   content,
                                   )
        plots.append((letter, tests))
        notes.extend(f'{letter}: {note}' for note in content['notes'])

    # ---- 3 The tests, the first sheet, and the file ----------------------------------
    _tests_sheet_writer(workbook.add_worksheet(TESTS_SHEET), formats, plots)
    _figure_sheet_writer(figure_sheet,
                         formats,
                         f'The numbers of {figure_file_namer(page.journal)}',
                         listed,
                         [line for line in captions if not line.startswith(starts)],
                         notes,
                         )
    try:
        workbook.close()
    except FileCreateError as exc:
        # xlsxwriter wraps the problem of the file system: hand on the problem itself,
        # which says which file it is and why
        cause = exc.args[0] if exc.args else None
        if isinstance(cause, OSError):
            raise cause from exc
        raise OSError(f'{path.name} could not be written.') from exc
    return path


# ---- dataset_workbook_namer ----------------------------------------------------------
def dataset_workbook_namer(journal: str) -> str:
    """
    ---- Summary ----
    Main function to name the workbook of the dataset figure for a journal: the name
    of the figure's PDF, as an Excel file.

    ---- Inputs ----
    journal : str
        The journal as the settings name it (a key of config.JOURNAL_SPECS).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        'dataset_figure_<journal>.xlsx'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_file_namer
    """

    return str(Path(figure_file_namer(journal)).with_suffix('.xlsx'))
