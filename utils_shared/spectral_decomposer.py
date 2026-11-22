"""
Spectral fit loading and haem decomposition routines.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import csv
import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import (haem_order_finder,
                                  haem_type_finder,
                                  HAEM_TYPE_ORDER,
                                  name_simplifier,
                                  )
from utils_shared.reference_level import (start_level_finder,
                                          window_seconds_calculator,
                                          )
from utils_shared.schema import (measurement_column_finder,
                                 SPECTRUM_INDEX_COLUMN,
                                 TIME_COLUMN,
                                 time_getter,
                                 value_getter,
                                 )


# ---- CONSTANTS -----------------------------------------------------------------------
# The standard scale of a fit: the highest point of its shapes (largest |response| in
# the file) lies inside this band. The bswitch fits, at about 2e-5 to 3e-5, set it.
FIT_PEAK_BAND = (1e-7, 1e-3)
# Some fit files hold the same shapes a million times larger; they are divided by this.
FIT_LARGE_SCALE = 1_000_000.0
# The first cell of a fit file in the layout with heading lines, and the newest format
# of that layout this reader knows (written in the second cell as 'format 1').
FIT_FILE_MARK = 'Portimao fit file'
FIT_FILE_FORMAT = 1
# The haem library: one fit file per haem, each at the size its source fit gives it, in
# this folder of the fits folder; and the presets, each a list of library files (with
# the haems per protein of each beside it, for the reader only), in the other. Only cells
# are measured, so a shape's size never changes the absorbance, delta A or %. A preset's
# first cell is PRESET_FILE_MARK, its second the format.
HAEMS_FOLDER_NAME = 'haems'
PRESETS_FOLDER_NAME = 'presets'
PRESET_FILE_MARK = 'Portimao preset'
PRESET_FILE_FORMAT = 1
# The units a fit file may give its shapes in, each with what its values are divided by
# to reach the standard scale (OD/mM/cm divided by a million, the instrument's own).
# 'relative' is for components found from data, scaled to a largest point of 1.
FIT_UNITS = {'OD/mM/cm': 1_000_000.0,
             'OD/µM/cm': 1_000.0,
             'OD/nM/cm': 1.0,
             'relative': 1_000_000.0,
             }
# Which way up the shapes of a fit file are, with the sign that turns them the way the
# decomposition uses them (oxidised minus reduced) and the words a file says it with.
FIT_WAY_UP = {'oxidised minus reduced': 1.0, 'reduced minus oxidised': -1.0}
FIT_WAY_UP_TEXTS = {'oxidised minus reduced': "oxidised minus reduced: each haem's α "
                                              'peak is a dip, so the amount found '
                                              'rises as the haem is oxidised and falls '
                                              'as it is reduced',
                    'reduced minus oxidised': "reduced minus oxidised: each haem's α "
                                              'peak points up, so Portimao turns the '
                                              'shapes over when it reads them',
                    }
FIT_NAMES_TEXT = ('In the figures the haem letters are in italics and a capital letter '
                  'or number after them is written below the line (Cyt bH, Cyt a605)')
# A word of a haem name put in figure form: one to three haem letters, in italics, then
# a capital letter or a number written below the line (bH, a605, cc, aa3).
HAEM_NAME_WORD = re.compile(r'([abcdo]{1,3})([A-Z]|[0-9]+)?')
# The backgrounds a decomposition can fit under the haems, by name, with the words the
# messages use; 'haem_background' in config.DEFAULT_ANSWERS names the standard one. The
# Valencia one is the shape of the instrument's own fit file, which follows
# 1/wavelength^2 exactly. Rowan scatter is the additive background of the lab's own
# chamber scripts, term for term (tests/test_haem_decomposition.py checks it against
# their lines).
BACKGROUND_LABELS = {'scatter_1': 'flat + 1/wavelength',
                     'scatter_2': 'flat + 1/wavelength + 1/wavelength²',
                     'linear': 'flat + straight line',
                     'rowan_scatter': 'flat + wavelength + (wavelength - centre)² '
                                      '(Rowan scatter)',
                     'valencia': 'flat + 1/wavelength² (Valencia)',
                     }
# The same backgrounds in a few words, as the drop-down in the strip lists them, the
# standard first.
BACKGROUND_SHORT_NAMES = {'rowan_scatter': 'Rowan scatter',
                          'valencia': 'Valencia',
                          'scatter_1': 'Flat + 1/wavelength',
                          'scatter_2': 'Flat + 1/wavelength + 1/wavelength²',
                          'linear': 'Straight line',
                          }
# The fit name of a set of library haems ticked in the strip, in place of a preset or a
# fit file (not a file name, so it never clashes with one); the files are in the answer
# 'haem_files'.
OWN_HAEMS_NAME = 'Your own haems'


# ---- SPECTRAL DECOMPOSER HELPERS -----------------------------------------------------


# ---- _fit_heading_reader -------------------------------------------------------------
def _fit_heading_reader(lines: List[str], label: str) -> Tuple[Dict[str, str], int]:
    """
    ---- Summary ----
    Helper function to read the lines at the top of a fit file in the layout with
    heading lines: its format, then one 'name,text' line each, up to the first empty
    line.

    ---- Inputs ----
    lines : List[str]
        The lines of the file; the first holds FIT_FILE_MARK.
    label : str
        Name of the fit file, used in the messages.

    ---- Globals read ----
    FIT_FILE_MARK, FIT_FILE_FORMAT (module constants).

    ---- Outputs ----
    Tuple[Dict[str, str], int]
        ({name of each heading line, in lower case: its text, the cells after the name
        joined by ', '}, index in lines of the haem names: the first line that is not
        empty after the heading lines). A name used twice keeps its first text. Raises
        ValueError, with a message for the user, when the first line gives no format,
        the format is newer than FIT_FILE_FORMAT, or no table follows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None. A line is empty when all its cells are, as a spreadsheet saves an empty line
    (',,,,').

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the format ----------------------------------------------------------
    first = next(csv.reader(lines[:1]), [])
    version = re.search(r'[0-9]+', ' '.join(first[1:]))
    if version is None:
        raise ValueError(f'{label}: its first line must say "{FIT_FILE_MARK},format '
                         f'{FIT_FILE_FORMAT}". Correct it, or choose another fit file.',
                         )
    if int(version.group()) > FIT_FILE_FORMAT:
        raise ValueError(
            f'{label} is a fit file of format {version.group()}, newer than '
            f'this Portimao can read (format {FIT_FILE_FORMAT}). Download '
            'Portimao again, or choose another fit file.',
            )

    # ---- 2 Read the heading lines up to the first empty line -------------------------
    no_table = (f'{label}: no table of shapes was found. Leave one empty line under the '
                'lines that describe the fit, then write the haem names, the row saying '
                'what each column holds, and the numbers.'
                )
    headings: Dict[str, str] = {}
    for index in range(1, len(lines)):
        cells = [cell.strip() for cell in next(csv.reader([lines[index]]), [])]
        if not any(cells):
            break
        name = ' '.join(cells[0].lower().split())
        if name and name not in headings:
            headings[name] = ', '.join(cell for cell in cells[1:] if cell)
    else:
        raise ValueError(no_table)

    # ---- 3 Find the haem names below the empty lines ---------------------------------
    for names_at in range(index + 1, len(lines)):
        if any(cell.strip() for cell in next(csv.reader([lines[names_at]]), [])):
            return headings, names_at
    raise ValueError(no_table)


# ---- _fit_table_cleaner --------------------------------------------------------------
def _fit_table_cleaner(data: pd.DataFrame,
                       label: str,
                       first_row: int = 2,
                       ) -> Tuple[pd.DataFrame, List[str]]:
    """
    ---- Summary ----
    Helper function to check the table of a fit file and to give every haem clean rows:
    numbers only, no blank rows, wavelengths going upwards.

    ---- Inputs ----
    data : pd.DataFrame
        The fit table as read: (wavelength, response) column pairs, one pair per haem;
        the header of each wavelength column names the haem.
    label : str
        Name of the fit file, used in the messages.
    first_row : int
        Row of the file that holds row 0 of the table (counted from 1), so that the
        messages name the row as the file has it: 2 for a file whose only heading is
        the haem names.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[pd.DataFrame, List[str]]
        (the table with the same headers, each haem's rows at the top and blanks below
        the shorter haems; the notes for the user, one sentence per haem whose leftover
        rows were left out). Raises ValueError, with a message for the user, when the
        columns are not in pairs, a haem has no name, a cell is not a number, a row
        holds only one of wavelength and response, or a haem has fewer than two rows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A haem whose wavelengths all go downwards is turned round. Where the wavelengths
    of a haem jump backwards, the rows before the jump are kept and the rest left out:
    such rows are leftovers of another column, not data.

    ---- Helpers ----
    _number_column_reader
    """

    # ---- 1 Check the columns come in pairs -------------------------------------------
    if (data.shape[1] % 2
        and str(data.columns[-1]).startswith('Unnamed')
        and data.iloc[:, -1].isna().all()
        ):
        data = data.iloc[:, :-1]  # an empty last column, as a spreadsheet may add
    if data.shape[1] == 0 or data.shape[1] % 2:
        raise ValueError(f'{label} has {data.shape[1]} columns, but a fit file needs '
                         'two columns per haem (wavelength, then response). Correct '
                         'the file, or choose another fit file.',
                         )

    # ---- 2 Clean each haem -----------------------------------------------------------
    notes: List[str] = []
    shapes: List[Tuple[np.ndarray, np.ndarray]] = []
    for i in range(data.shape[1] // 2):
        haem = str(data.columns[2 * i])
        if haem.startswith('Unnamed'):
            raise ValueError(f'{label}: columns {2 * i + 1} and {2 * i + 2} have no '
                             'haem name in the first row. Write the name of the haem '
                             'above its wavelength column, or delete the columns if '
                             'they are empty.',
                             )
        x = _number_column_reader(data.iloc[:, 2 * i],
                                  haem,
                                  'wavelength',
                                  label,
                                  first_row,
                                  )
        y = _number_column_reader(data.iloc[:, 2 * i + 1],
                                  haem,
                                  'response',
                                  label,
                                  first_row,
                                  )
        half = np.isnan(x) != np.isnan(y)
        if half.any():
            row = int(np.nonzero(half)[0][0]) + first_row
            raise ValueError(f'{label}: row {row} of {haem} has a wavelength without '
                             'a response, or a response without a wavelength. Fill in '
                             'or empty both cells, or choose another fit file.',
                             )
        filled = ~np.isnan(x)
        x, y = x[filled], y[filled]
        steps = np.diff(x)
        if steps.size and np.all(steps <= 0) and np.any(steps < 0):
            x, y = x[::-1], y[::-1]
            steps = np.diff(x)
        backwards = np.nonzero(steps < 0)[0]
        if backwards.size:
            kept = int(backwards[0]) + 1
            notes.append(f'{label}: the rows of {haem} after {x[kept - 1]:.2f} nm go '
                         'backwards in wavelength and were left out, so it is used '
                         f'from {x[0]:.2f} to {x[kept - 1]:.2f} nm.',
                         )
            x, y = x[:kept], y[:kept]
        if len(x) < 2:
            raise ValueError(f'{label}: {haem} has fewer than two rows of numbers, too '
                             'few to make a shape. Fill in its columns, or choose '
                             'another fit file.',
                             )
        shapes.append((x, y))

    # ---- 3 Rebuild the table ---------------------------------------------------------
    n_rows = max(len(x) for x, _ in shapes)
    values = np.full((n_rows, data.shape[1]), np.nan)
    for i, (x, y) in enumerate(shapes):
        values[:len(x), 2 * i] = x
        values[:len(y), 2 * i + 1] = y
    return pd.DataFrame(values, columns=data.columns), notes


# ---- _fit_unit_finder ----------------------------------------------------------------
def _fit_unit_finder(text: str) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find which of the fit units the Unit line of a fit file names,
    however it is spaced, capitalised or written with a micro sign.

    ---- Inputs ----
    text : str
        Text of the Unit line, for example 'OD/mM/cm' or 'od / uM / cm'.

    ---- Globals read ----
    FIT_UNITS (module constant).

    ---- Outputs ----
    Optional[str]
        The unit as FIT_UNITS writes it, or None when the text names none of them.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None. The Greek mu (μ) and a u in place of µ count as the micro sign.

    ---- Helpers ----
    None.
    """

    key = re.sub(r'\s+', '', text).lower().replace('μ', 'µ').replace('/um/', '/µm/')
    for unit in FIT_UNITS:
        if key == unit.lower():
            return unit
    return None


# ---- _haem_shape_getter --------------------------------------------------------------
def _haem_shape_getter(fit_data: pd.DataFrame,
                       index: int,
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Helper function to give the filled rows of one haem of a fit table, so that the
    blanks below a shorter haem never reach a calculation.

    ---- Inputs ----
    fit_data : pd.DataFrame
        Fit table from fit_importer.
    index : int
        Number of the haem in the table, from 0.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray]
        (wavelengths in nm, responses) of that haem, each of shape (n_rows of the
        haem).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    x = fit_data.iloc[:, 2 * index].to_numpy(dtype=float)
    y = fit_data.iloc[:, 2 * index + 1].to_numpy(dtype=float)
    filled = np.isfinite(x) & np.isfinite(y)
    return x[filled], y[filled]


# ---- _headed_fit_reader --------------------------------------------------------------
def _headed_fit_reader(lines: List[str],
                       label: str,
                       ) -> Tuple[pd.DataFrame, float, List[str]]:
    """
    ---- Summary ----
    Helper function to read a fit file in the layout with heading lines (DATA_FORMAT.md,
    "fit csv") and bring it to the standard scale, the way up the decomposition uses
    and the haem names in figure form.

    ---- Inputs ----
    lines : List[str]
        The lines of the file; the first holds FIT_FILE_MARK.
    label : str
        Name of the fit file, used in the messages.

    ---- Globals read ----
    FIT_UNITS, FIT_WAY_UP, FIT_PEAK_BAND (module constants).

    ---- Outputs ----
    Tuple[pd.DataFrame, float, List[str]]
        (the cleaned table, as _fit_table_cleaner gives it, on the standard scale with
        each haem's name in figure form; what the values of the file were divided by;
        the notes for the user). Raises ValueError, with a message for the user, when
        the Unit line is missing or names no fit unit, the Way up line is not one of
        the two ways, the row under the haem names does not say what the columns
        hold, or the table cannot be read.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    response = value of the file x way-up sign (+1, or -1 for 'reduced minus
    oxidised') / divisor of the unit (FIT_UNITS). A file with no Way up line is used
    as it is written.

    ---- Helpers ----
    _fit_heading_reader
    _fit_table_cleaner
    _fit_unit_finder
    haem_name_typesetter
    """

    # ---- 1 Read the heading lines, the unit and the way up ---------------------------
    headings, names_at = _fit_heading_reader(lines, label)
    units = ', '.join(FIT_UNITS)
    if 'unit' not in headings:
        raise ValueError(f'{label} has no Unit line, so the size of its shapes is not '
                         f'known. Add a line "Unit,OD/mM/cm" (or another of: {units}) '
                         'above the empty line, or choose another fit file.',
                         )
    unit = _fit_unit_finder(headings['unit'])
    if unit is None:
        raise ValueError(f'{label}: its Unit line says "{headings["unit"]}", but the '
                         f'unit must be one of: {units}. Correct the line, or choose '
                         'another fit file.',
                         )
    sign = 1.0
    if 'way up' in headings:
        way_up = ' '.join(headings['way up'].split(':')[0].lower().split())
        if way_up not in FIT_WAY_UP:
            raise ValueError(f'{label}: its Way up line says "{headings["way up"]}", '
                             "but it must start with 'oxidised minus reduced' or "
                             "'reduced minus oxidised'. Correct the line, or choose "
                             'another fit file.',
                             )
        sign = FIT_WAY_UP[way_up]

    # ---- 2 Check the row that says what each column holds ----------------------------
    rows = list(csv.reader(lines[names_at:names_at + 2]))
    if len(rows) < 2 or not all(i < len(rows[1])
                                and rows[1][i].strip().lower().startswith('wavelength')
                                for i in range(0, len(rows[0]), 2)
                                if rows[0][i].strip()
                                ):
        raise ValueError(f'{label}: the row under the haem names (row {names_at + 2}) '
                         'must say what each column holds: "Wavelength (nm)", then the '
                         'unit. Add that row, or choose another fit file.',
                         )

    # ---- 3 Read and clean the table --------------------------------------------------
    try:
        raw = pd.read_csv(io.StringIO('\n'.join(lines[names_at:])), skiprows=[1])
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        raise ValueError(
            f'{label}: the table of shapes under its first lines could not '
            'be read. Open it to check it, or choose another fit file.',
            ) from None
    cleaned, notes = _fit_table_cleaner(raw, label, first_row=names_at + 3)

    # ---- 4 Bring it to the standard scale, way up and names --------------------------
    divisor = FIT_UNITS[unit]
    data = cleaned.copy()
    data.iloc[:, 1::2] = sign * cleaned.iloc[:, 1::2].to_numpy(dtype=float) / divisor
    data.columns = [haem_name_typesetter(column) if i % 2 == 0 else column
                    for i, column in enumerate(cleaned.columns)
                    ]
    peak = float(np.nanmax(np.abs(data.iloc[:, 1::2].to_numpy(dtype=float))))
    low, high = FIT_PEAK_BAND
    if not low <= peak <= high:
        notes.append(
            f'Warning: {label}: the highest point of its shapes is '
            f'{peak * divisor:.3g} {unit}, far from the usual size in that unit '
            f'({low * divisor:g} to {high * divisor:g}). Check its Unit line. '
            'mOD and % are not affected; the raw haem amounts are.',
            )
    return data, divisor, notes


# ---- _number_column_reader -----------------------------------------------------------
def _number_column_reader(column: pd.Series,
                          haem: str,
                          kind: str,
                          label: str,
                          first_row: int,
                          ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to read one column of a fit file as numbers.

    ---- Inputs ----
    column : pd.Series
        The column as read from the file; row i is row i + first_row of the file.
    haem : str
        Name of the haem the column belongs to, used in the message.
    kind : str
        'wavelength' or 'response', used in the message.
    label : str
        Name of the fit file, used in the message.
    first_row : int
        Row of the file that holds row 0 of the column (counted from 1).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The numbers, shape (n_rows), NaN where the cell is empty. Raises ValueError,
        with a message for the user, for a cell that holds anything but a number.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    blank = (column.isna() | column.astype(str).str.strip().eq('')).to_numpy()
    numbers = np.array(pd.to_numeric(column, errors='coerce'), dtype=float)
    numbers[blank] = np.nan
    unreadable = ~blank & ~np.isfinite(numbers)
    if unreadable.any():
        row = int(np.nonzero(unreadable)[0][0])
        raise ValueError(
            f'{label}: the {kind} of {haem} in row {row + first_row} is not a '
            f'number ("{column.iloc[row]}"). Correct the cell, or choose '
            'another fit file.',
            )
    return numbers


# ---- _preset_reader ------------------------------------------------------------------
def _preset_reader(path: Path) -> List[str]:
    """
    ---- Summary ----
    Helper function to read the names of the library files a preset lists.

    ---- Inputs ----
    path : Path
        Preset file (DATA_FORMAT.md, "preset csv").

    ---- Globals read ----
    PRESET_FILE_MARK, PRESET_FILE_FORMAT (module constants).

    ---- Outputs ----
    List[str]
        The file names, in the order the preset lists them. Raises ValueError, with a
        message for the user, when the file cannot be read, is not a preset, is of a
        newer format, or lists no file.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None. The heading lines end at the first empty line; the first line after it is
    the column name, and each line below names one file in its first cell.

    ---- Helpers ----
    None.
    """

    # ---- 1 Read the lines ------------------------------------------------------------
    label = path.name
    try:
        rows = list(csv.reader(path.read_text(encoding='utf-8-sig').splitlines()))
    except (OSError, UnicodeDecodeError, csv.Error):
        raise ValueError(f'The preset {label} could not be read. Open it to check it, '
                         'or choose another fit.',
                         ) from None

    # ---- 2 Check the first line ------------------------------------------------------
    first = [cell.strip() for cell in rows[0]] if rows else []
    if not first or first[0].lower() != PRESET_FILE_MARK.lower():
        raise ValueError(f'{label} is in the presets folder but its first line does '
                         f'not say "{PRESET_FILE_MARK},format {PRESET_FILE_FORMAT}". '
                         'Correct it, or move it out of the presets folder.',
                         )
    version = re.search(r'[0-9]+', ' '.join(first[1:]))
    if version is not None and int(version.group()) > PRESET_FILE_FORMAT:
        raise ValueError(f'{label} is a preset of format {version.group()}, newer '
                         f'than this Portimao can read (format {PRESET_FILE_FORMAT}). '
                         'Download Portimao again, or choose another fit.',
                         )

    # ---- 3 Read the file names under the heading lines -------------------------------
    filled = [any(cell.strip() for cell in row) for row in rows]
    gap = filled.index(False) if False in filled else len(rows)
    listed = [row[0].strip() for row, is_filled in zip(rows[gap:], filled[gap:])
              if is_filled and row[0].strip()
              ]
    names = listed[1:]  # the first is the column name
    if not names:
        raise ValueError(f'The preset {label} lists no haem file. Write one library '
                         'file name per line under its "Haem file" line.',
                         )
    return names


# ---- _unit_scaler --------------------------------------------------------------------
def _unit_scaler(values: np.ndarray) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to scale one background shape to run from 0 to 1.

    ---- Inputs ----
    values : np.ndarray
        The shape at each wavelength, shape (n_wavelengths).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The scaled shape, same shape; all 0 when the values do not change (one
        wavelength), and empty when there are none, so that the solver can say there
        are too few wavelengths.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    scaled = (values - min) / (max - min).

    ---- Helpers ----
    None.
    """

    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return values
    shifted = values - values.min()
    spread = shifted.max()
    return shifted / spread if spread > 0 else shifted


# ---- _wavelength_masker --------------------------------------------------------------
def _wavelength_masker(wavelengths: np.ndarray, fit_data: pd.DataFrame) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to select the wavelengths inside the range shared by all fits.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths of the spectrum (nm).
    fit_data : pd.DataFrame
        Fit table from fit_importer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Boolean mask, True inside the shared range. Raises ValueError, with a message
        for the user, when a haem of the fit has no rows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    fit_range_finder
    """

    wmin, wmax = fit_range_finder(fit_data)
    return (wavelengths >= wmin) & (wavelengths <= wmax)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- answers_fit_loader --------------------------------------------------------------
def answers_fit_loader(fits_folder: Path,
                       fit_file: str,
                       haem_files: Sequence[str],
                       ) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to load the fit the answers name: the library haems ticked in the
    strip when the fit is OWN_HAEMS_NAME, otherwise the preset or fit file of that name.

    ---- Inputs ----
    fits_folder : Path
        The fits folder, holding the haems and presets folders and the user's own fit
        files.
    fit_file : str
        The answer 'fit_file': OWN_HAEMS_NAME, or a name as fit_names_lister gives it.
    haem_files : Sequence[str]
        The answer 'haem_files': the library file names ticked; used only with
        OWN_HAEMS_NAME.

    ---- Globals read ----
    HAEMS_FOLDER_NAME, OWN_HAEMS_NAME (module constants).

    ---- Outputs ----
    Dict[str, Any]
        Fit dictionary, as fit_loader or haem_files_combiner gives it. Raises
        ValueError, with a message for the user, when it cannot be loaded (no haem
        ticked, a ticked file missing, or the fit unreadable).

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    fit_loader
    haem_files_combiner
    """

    if fit_file != OWN_HAEMS_NAME:
        return fit_loader(fits_folder, fit_file)
    if not haem_files:
        raise ValueError('No haem is ticked under Build a fit. Tick at least one haem, '
                         'or choose a preset.',
                         )
    return haem_files_combiner([fits_folder / HAEMS_FOLDER_NAME / name
                                for name in haem_files
                                ],
                               )


# ---- background_builder --------------------------------------------------------------
def background_builder(wavelengths: np.ndarray, background: str) -> np.ndarray:
    """
    ---- Summary ----
    Main function to build the background terms that a haem decomposition fits beside
    its shapes: a flat level and the shapes of the chosen background.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths of the spectra (nm), shape (n_wavelengths).
    background : str
        Name of the background, a key of BACKGROUND_LABELS.

    ---- Globals read ----
    BACKGROUND_LABELS (module constant).

    ---- Outputs ----
    np.ndarray
        The terms as columns, shape (n_wavelengths, n_terms): the flat 1 first, then
        the shapes, each running from 0 to 1 over the wavelengths. Raises ValueError,
        with a message for the user, for a background the program does not know.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    scatter_1: 1, 1/wl; scatter_2: 1, 1/wl, 1/wl^2 (scatter_background_builder);
    linear: 1, wl; rowan_scatter: 1, wl, (wl - centre)^2 with the centre halfway
    between the shortest and the longest wavelength; valencia: 1, 1/wl^2. Scaling a
    shape to run from 0 to 1 changes only the size of its amount, not the fit.

    ---- Helpers ----
    _unit_scaler
    scatter_background_builder
    """

    # ---- 1 Check the name ------------------------------------------------------------
    if background not in BACKGROUND_LABELS:
        choices = '; '.join(f'{name} ({label})'
                            for name, label in BACKGROUND_LABELS.items()
                            )
        raise ValueError(f'The program has no background called "{background}". '
                         f'Choose one of: {choices}.',
                         )
    wavelengths = np.asarray(wavelengths, dtype=float)

    # ---- 2 Build the terms -----------------------------------------------------------
    if background in ('scatter_1', 'scatter_2'):
        return scatter_background_builder(wavelengths, int(background[-1]))
    line = _unit_scaler(wavelengths)
    shapes = {'linear': [line],
              'rowan_scatter': [line, _unit_scaler((line - 0.5) ** 2)],
              'valencia': [_unit_scaler(1 / wavelengths ** 2)],
              }[background]
    return np.column_stack([np.ones_like(wavelengths)] + shapes)


# ---- basis_solver --------------------------------------------------------------------
def basis_solver(basis: np.ndarray, spectra: np.ndarray) -> np.ndarray:
    """
    ---- Summary ----
    Main function to find how much of each column of a basis (the shapes and the
    background terms) is in one spectrum, or in each spectrum of a run. It is the one
    solver of every decomposition in the program.

    ---- Inputs ----
    basis : np.ndarray
        The shapes to fit as columns, shape (n_wavelengths, n_components).
    spectra : np.ndarray
        One spectrum, shape (n_wavelengths), or a run of them, shape (n_spectra,
        n_wavelengths), on the wavelengths of the basis.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The amounts, shape (n_components) for one spectrum or (n_spectra,
        n_components) for a run. A spectrum holding a blank value gives blank amounts
        for that spectrum only. Raises ValueError, with a message for the user, when
        there are fewer wavelengths than components or when the columns cannot be told
        apart.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Least squares: the c that makes |B c - a| smallest. Each column of B is first
    divided by its length (root of its summed squares), so shapes on very different
    scales are solved equally well; B_scaled = U S V^T (singular value decomposition);
    c = V S^-1 U^T a / column length. S^T S is never inverted, as that squares the
    rounding errors.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the basis -----------------------------------------------------------
    basis = np.asarray(basis, dtype=float)
    values = np.asarray(spectra, dtype=float)
    n_wavelengths, n_components = basis.shape
    if n_wavelengths < n_components:
        raise ValueError(
            f'The spectra and the shapes to fit share only {n_wavelengths}'
            f' wavelengths, too few to work out {n_components} amounts. '
            'Choose a fit file that covers the wavelengths of the spectra.',
            )
    unusable = ('Two of the shapes to fit cannot be told apart over these wavelengths '
                '(they are the same, or one of them is empty), so the amounts cannot '
                'be worked out. Choose another fit file.'
                )
    lengths = np.linalg.norm(basis, axis=0)
    if not np.all(np.isfinite(lengths)) or np.any(lengths == 0):
        raise ValueError(unusable)

    # ---- 2 Solve ---------------------------------------------------------------------
    u, s, vt = np.linalg.svd(basis / lengths, full_matrices=False)
    if s[-1] <= s[0] * max(basis.shape) * np.finfo(float).eps:
        raise ValueError(unusable)
    return ((values @ u) / s) @ vt / lengths


# ---- data_filterer -------------------------------------------------------------------
def data_filterer(experimental_data: np.ndarray, fit_data: pd.DataFrame) -> np.ndarray:
    """
    ---- Summary ----
    Main function to restrict experimental data to the wavelength range shared by all
    fits.

    ---- Inputs ----
    experimental_data : np.ndarray
        Array of (wavelength, value) rows, shape (n_wavelengths, 2).
    fit_data : pd.DataFrame
        Fit table from fit_importer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The rows inside the shared range.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _wavelength_masker
    """

    return experimental_data[_wavelength_masker(experimental_data[:, 0], fit_data)]


# ---- decomposition_gap_calculator ----------------------------------------------------
def decomposition_gap_calculator(new: pd.DataFrame,
                                 kept: pd.DataFrame,
                                 ) -> Dict[str, Tuple[float, float]]:
    """
    ---- Summary ----
    Main function to say how far apart the haem traces of two decompositions of the
    same spectra are: for each haem in both, the largest gap and the average gap. The
    spectra are matched by their index, and a haem is matched by its plain name, so
    "Cyt cc" and "cyt c c" are the same haem.

    ---- Inputs ----
    new : pd.DataFrame
        Haem table of the decomposition in use (DATA_FORMAT.md, 'haem_conc' or any
        table made from it), with SPECTRUM_INDEX_COLUMN.
    kept : pd.DataFrame
        Haem table of the kept decomposition, of the same kind and units.

    ---- Globals read ----
    SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    Dict[str, Tuple[float, float]]
        {haem name as in ``new``: (largest gap, average gap)}, in the units of the
        tables, in the order of ``new``. A haem with no spectrum where both have a
        value is left out. Raises KeyError when a table has no spectrum index.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    gap_i = new_i - kept_i at each spectrum i found in both
    largest gap = max |gap_i|
    average gap = mean |gap_i|

    ---- Helpers ----
    measurement_column_finder
    name_simplifier
    value_getter
    """

    # ---- 1 Match the spectra ---------------------------------------------------------
    for table in (new, kept):
        if SPECTRUM_INDEX_COLUMN not in table.columns:
            raise KeyError(f'A haem table has no {SPECTRUM_INDEX_COLUMN!r} column, so '
                           'its spectra cannot be matched.',
                           )
    kept_columns = {name_simplifier(column): column
                    for column in measurement_column_finder(kept)
                    }
    kept_rows = kept.set_index(SPECTRUM_INDEX_COLUMN)

    # ---- 2 The gaps of each haem in both ---------------------------------------------
    gaps: Dict[str, Tuple[float, float]] = {}
    for column in measurement_column_finder(new):
        partner = kept_columns.get(name_simplifier(column))
        if partner is None:
            continue
        kept_values = pd.to_numeric(kept_rows[partner], errors='coerce')
        matched = kept_values.reindex(new[SPECTRUM_INDEX_COLUMN]).to_numpy(dtype=float)
        sizes = np.abs(value_getter(new, column) - matched)
        sizes = sizes[np.isfinite(sizes)]
        if sizes.size:
            gaps[column] = (float(sizes.max()), float(sizes.mean()))
    return gaps


# ---- delta_abs_calculator ------------------------------------------------------------
def delta_abs_calculator(haem_abs: pd.DataFrame,
                         exclude_first_minutes: float,
                         window_points: int,
                         label: str = 'haem_abs',
                         exclude_last_minutes: float = 0.0,
                         ) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to shift each haem absorbance so that it is 0 where the haem starts,
    giving delta D, the change from the start (mOD). The start of each haem is the
    median of its first spectra after the ignored start, so one spike does not set it.

    ---- Inputs ----
    haem_abs : pd.DataFrame
        Haem absorbance table in mOD (time, spectrum index and one column per haem).
    exclude_first_minutes : float
        Minutes after the first measurement that are ignored at the start.
    window_points : int
        Number of spectra the start is taken from (>= 1).
    label : str
        Name used in error messages.
    exclude_last_minutes : float
        Minutes before the last measurement that are ignored at the end; the start is
        never taken from them.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Shifted copy; result.attrs["delta_abs_baseline"] holds {'level_by_haem': the
        level subtracted from each haem (mOD), 'window_by_haem': the (first, last)
        time of the spectra each haem's start was taken from (min), 'window_points',
        'window_seconds': how long that many spectra last}. Raises ValueError, with a
        message for the user, for invalid settings or when fewer than window_points
        spectra are left after the ignored parts.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    delta D = D - D_start, per haem, with D_start = median(D of the first
    window_points spectra with a value after the ignored start) (start_level_finder).
    Only a constant is subtracted, so differences between points are unchanged.

    ---- Helpers ----
    measurement_column_finder
    start_level_finder
    time_getter
    value_getter
    window_seconds_calculator
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    if exclude_first_minutes < 0 or exclude_last_minutes < 0:
        raise ValueError('The time ignored at the start or the end of the run cannot '
                         'be negative. Correct it where the program asks for it.',
                         )

    # ---- 2 Find the usable part of the run -------------------------------------------
    columns = measurement_column_finder(haem_abs)
    times = time_getter(haem_abs)
    finite_times = times[np.isfinite(times)]
    if not columns or finite_times.size == 0:
        raise ValueError(f'{label}: there are no haems, or no times, to find the zero '
                         'of ΔD from. Check that the fit file holds haems and that '
                         'the file was read fully.',
                         )
    start = float(finite_times.min()) + exclude_first_minutes
    stop = float(finite_times.max()) - exclude_last_minutes

    # ---- 3 Subtract the start of each haem -------------------------------------------
    result = haem_abs.copy()
    reference: Dict[str, float] = {}
    windows: Dict[str, Tuple[float, float]] = {}
    for column in columns:
        values = value_getter(haem_abs, column)
        found = start_level_finder(times, values, start, stop, window_points)
        if found is None:
            raise ValueError(f'{label}: fewer than {window_points} {column} values '
                             f'are left between {start:.2f} and {stop:.2f} min, too '
                             'few to find the zero of ΔD (the median of the first '
                             f'{window_points} spectra after the ignored start). '
                             'Ignore less of the start or the end of the run.',
                             )
        reference[str(column)] = found['level']
        windows[str(column)] = (found['start_time'], found['end_time'])
        result[column] = values - found['level']
    window_seconds = window_seconds_calculator(times, window_points)
    result.attrs['delta_abs_baseline'] = {'level_by_haem': reference,
                                          'window_by_haem': windows,
                                          'window_points': int(window_points),
                                          'window_seconds': window_seconds,
                                          }
    return result


# ---- experiment_decomposer -----------------------------------------------------------
def experiment_decomposer(experiment: dict,
                          fit: dict,
                          dataset_name: str,
                          background: str,
                          haemfactor: float,
                          delta_exclude_first_minutes: float,
                          delta_window_points: int,
                          spectrum_type: str = 'attenuation',
                          delta_exclude_last_minutes: float = 0.0,
                          is_change_from_first: bool = False,
                          ) -> dict:
    """
    ---- Summary ----
    Main function to decompose every spectrum of one dataset into haem concentrations
    and absorbances.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    fit : dict
        Fit dictionary from fit_importer (or fit_haem_selector).
    dataset_name : str
        Spectral dataset to decompose.
    background : str
        Background fitted under the haems, a key of BACKGROUND_LABELS.
    haemfactor : float
        Scale factor applied to the haem basis spectra.
    delta_exclude_first_minutes : float
        Minutes after the first spectrum that are ignored when finding where each
        haem starts, the 0 of delta D.
    delta_window_points : int
        Number of spectra after the ignored start that each haem's start is taken
        from.
    spectrum_type : str
        Field of the dataset to decompose, e.g. 'attenuation'.
    delta_exclude_last_minutes : float
        Minutes before the last spectrum that are ignored; the start is never taken
        from them.
    is_change_from_first : bool
        True fits the change of every spectrum from the first one (the first kept, in
        a trimmed run), as the instrument does; False fits the spectra themselves.

    ---- Globals read ----
    schema.TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError for an invalid fit, dataset
        or background, inconsistent array shapes, or, for the change from the first
        spectrum, a first spectrum with blank values inside the fitted wavelengths.

    ---- Globals mutated ----
    experiment: adds haem_conc (time, spectrum index, one column per haem), haem_abs
    (mOD, same layout; attrs["peak_amplitude_OD"]) and haem_delta_abs
    (delta_abs_calculator). With is_change_from_first, haem_conc and haem_abs are the
    changes from the first spectrum. The three are added together at the end; when
    anything fails, the experiment holds none of them, not even those of an earlier
    decomposition.

    ---- Equations ----
    a = each spectrum, or each spectrum - the first spectrum; c = the least-squares
    amounts of the basis S in a (basis_solver); haem_abs = c x peak amplitude of the
    haem basis spectrum x 1000 (OD to mOD); haem_delta_abs = haem_abs - median of the
    haem's first spectra after the ignored start. The fit is linear, so with the same
    basis the change from the first spectrum gives each amount minus that of the first
    spectrum, and the same haem_delta_abs.

    ---- Helpers ----
    _wavelength_masker
    basis_solver
    delta_abs_calculator
    s_array_generator
    """

    # ---- 1 Validate the fit and dataset ----------------------------------------------
    for key in ('haem_conc', 'haem_abs', 'haem_delta_abs'):
        experiment.pop(key, None)  # a failure must not leave an older result behind
    name = experiment.get('experiment_name', 'This file')
    if fit is None or 'data' not in fit or 'haem_list' not in fit:
        raise ValueError('No fit file was loaded, so the haems cannot be worked out. '
                         'Choose a fit file when the program asks for one.',
                         )
    raw_spectra = experiment.get('raw_spectra', {})
    if dataset_name not in raw_spectra:
        raise ValueError(
            f'{name}: the file has no {dataset_name} spectra to decompose '
            f"(it has: {', '.join(raw_spectra) or 'none'}). Choose spectra "
            'that the file holds.',
            )
    dataset = raw_spectra[dataset_name]
    if spectrum_type not in dataset:
        raise ValueError(f'{name}: the {dataset_name} spectra were not converted to '
                         f'{spectrum_type}, so they cannot be decomposed. This is a '
                         'fault in the program; please report it.',
                         )

    # ---- 2 Read and check the spectra ------------------------------------------------
    wavelengths = np.asarray(dataset['wavelengths'], dtype=float)
    spectra = np.asarray(dataset[spectrum_type], dtype=float)
    spectrum_indices = np.asarray(dataset['spectrum_indices'])
    times = np.asarray(dataset['time'], dtype=float)
    damaged = (f'{name}: the {dataset_name} spectra cannot be decomposed, because '
               'their wavelengths, spectra and times do not have matching lengths. '
               'The file may be damaged; save it again from the instrument software.'
               )
    if wavelengths.ndim != 1:
        raise ValueError(damaged)
    if spectra.ndim != 2 or spectra.shape[1] != len(wavelengths):
        raise ValueError(damaged)
    if len(spectrum_indices) != len(spectra) or len(times) != len(spectra):
        raise ValueError(damaged)
    if not np.all(np.isfinite(times)):
        raise ValueError(f'{name}: the times of the {dataset_name} spectra are not '
                         'known (the file holds a different number of spectra and of '
                         'oxygen points), so the haems cannot be worked out.',
                         )
    if len(spectra) == 0:
        raise ValueError(f'{name}: there are no {dataset_name} spectra left to '
                         'decompose. Trim less of the run.',
                         )

    # ---- 3 Decompose the spectra -----------------------------------------------------
    fit_data = fit['data']
    haem_names = list(fit['haem_list'])
    mask = _wavelength_masker(wavelengths, fit_data)
    s_array = s_array_generator(np.column_stack((wavelengths, spectra[0])),
                                fit_data,
                                background,
                                haemfactor,
                                )
    fitted = spectra[:, mask]
    if is_change_from_first:
        if not np.all(np.isfinite(fitted[0])):
            raise ValueError(f'{name}: the first {dataset_name} spectrum has blank '
                             'values inside the wavelengths of the fit, so the change '
                             'from it cannot be worked out. Trim the start of the run '
                             'past it, or fit the spectra themselves.',
                             )
        fitted = fitted - fitted[0]
    coefficients = basis_solver(s_array, fitted)  # (n_spectra, n_components)
    haem_conc = pd.DataFrame(coefficients[:, :len(haem_names)], columns=haem_names)
    haem_conc.insert(0, SPECTRUM_INDEX_COLUMN, spectrum_indices)
    haem_conc.insert(0, TIME_COLUMN, times)

    # ---- 4 Calculate the absorbances -------------------------------------------------
    # Peak amplitude (OD per unit coefficient) of each haem's basis spectrum; x1000
    # converts OD to mOD.
    peak_amplitude = np.max(np.abs(s_array[:, :len(haem_names)]), axis=0)
    haem_abs = haem_conc.copy()
    haem_abs[haem_names] = coefficients[:, :len(haem_names)] * peak_amplitude * 1000.0
    haem_abs.attrs['peak_amplitude_OD'] = dict(zip(haem_names, peak_amplitude.tolist()))
    haem_delta_abs = delta_abs_calculator(
        haem_abs,
        delta_exclude_first_minutes,
        delta_window_points,
        label=name,
        exclude_last_minutes=delta_exclude_last_minutes,
        )

    # ---- 5 Store the three tables together -------------------------------------------
    experiment['haem_conc'] = haem_conc
    experiment['haem_abs'] = haem_abs
    experiment['haem_delta_abs'] = haem_delta_abs
    return experiment


# ---- fit_describer -------------------------------------------------------------------
def fit_describer(fit_file: str, haem_files: Sequence[str]) -> str:
    """
    ---- Summary ----
    Main function to name the fit in use in words, for the messages and the workbook:
    the preset or fit file as it is, or the library haems ticked under Build a fit.

    ---- Inputs ----
    fit_file : str
        The answer 'fit_file'.
    haem_files : Sequence[str]
        The answer 'haem_files'; used only when fit_file is OWN_HAEMS_NAME.

    ---- Globals read ----
    OWN_HAEMS_NAME (module constant).

    ---- Outputs ----
    str
        fit_file, or 'Your own haems: c1_myco, bH_bswitch' (the files without .csv).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if fit_file != OWN_HAEMS_NAME:
        return str(fit_file)
    return f"{OWN_HAEMS_NAME}: {', '.join(Path(name).stem for name in haem_files)}"


# ---- fit_file_writer -----------------------------------------------------------------
def fit_file_writer(fit: Dict[str, Any],
                    path: Path,
                    unit: str,
                    holds: str,
                    way_up: Optional[str] = None,
                    notes: Sequence[Tuple[str, str]] = (),
                    ) -> Path:
    """
    ---- Summary ----
    Main function to save a fit as a fit file in the layout with heading lines
    (DATA_FORMAT.md, "fit csv"), which fit_importer reads back as the same fit.

    ---- Inputs ----
    fit : Dict[str, Any]
        Fit dictionary, as fit_importer or fit_table_builder give it: names in figure
        form or plain, the table on the standard scale.
    path : Path
        File to write (.csv).
    unit : str
        Unit of the values written, one of FIT_UNITS.
    holds : str
        What the file holds, in words, for its Holds line.
    way_up : Optional[str]
        One of FIT_WAY_UP for a file of haem shapes, which then has a Way up line;
        None for no Way up line (the shapes are written as the decomposition uses them).
    notes : Sequence[Tuple[str, str]]
        Further heading lines for people, as (name, text), for example ('Made from',
        'the instrument's fit ...'), written in this order under the Names line.

    ---- Globals read ----
    FIT_FILE_MARK, FIT_FILE_FORMAT, FIT_UNITS, FIT_WAY_UP, FIT_WAY_UP_TEXTS,
    FIT_NAMES_TEXT (module constants).

    ---- Outputs ----
    Path
        The file written. Raises ValueError when the unit or the way up is not one
        this module knows, or two haems have the same plain name or one has none.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    value written = response x divisor of the unit (FIT_UNITS) x way-up sign
    (FIT_WAY_UP), to 15 significant digits: a value typed with fewer digits is written
    as typed, and any other moves by less than 1e-14 of itself. Rows blank in every
    haem are left out, so no leftover rows are written.

    ---- Helpers ----
    haem_name_plainer
    """

    # ---- 1 Check the unit, the way up and the names ----------------------------------
    if unit not in FIT_UNITS:
        raise ValueError(f'"{unit}" is not a fit unit; use one of: '
                         f"{', '.join(FIT_UNITS)}.",
                         )
    if way_up is not None and way_up not in FIT_WAY_UP:
        raise ValueError(f'"{way_up}" is not a way up; use one of: '
                         f"{', '.join(FIT_WAY_UP)}.",
                         )
    names = [haem_name_plainer(name).strip() for name in fit['haem_list']]
    if not all(names) or len(set(names)) != len(names):
        raise ValueError('Every haem of a fit file needs its own name (the names: '
                         f"{'; '.join(names)}). Name the haems again.",
                         )

    # ---- 2 Build the heading lines ---------------------------------------------------
    rows = [[FIT_FILE_MARK, f'format {FIT_FILE_FORMAT}'],
            ['Holds', holds],
            ['Unit', unit],
            ]
    if way_up is not None:
        rows.append(['Way up', FIT_WAY_UP_TEXTS[way_up]])
    rows.append(['Names', FIT_NAMES_TEXT])
    rows += [[name, text] for name, text in notes]
    rows.append([])

    # ---- 3 Build the table -----------------------------------------------------------
    rows.append([cell for name in names for cell in (name, '')])
    rows.append([cell for _ in names for cell in ('Wavelength (nm)', unit)])
    values = fit['data'].to_numpy(dtype=float).copy()
    values[:, 1::2] *= FIT_UNITS[unit] * FIT_WAY_UP.get(way_up, 1.0)
    for row in values:
        if not np.isnan(row).all():
            rows.append(['' if np.isnan(value) else f'{value:.15g}' for value in row])

    # ---- 4 Write the file ------------------------------------------------------------
    with open(path, 'w', encoding='utf-8-sig', newline='') as handle:
        csv.writer(handle, lineterminator='\r\n').writerows(rows)
    return path


# ---- fit_haem_selector ---------------------------------------------------------------
def fit_haem_selector(fit: Dict[str, Any], haems: List[str]) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to keep only some of the haems of a fit, so that a decomposition fits
    those alone.

    ---- Inputs ----
    fit : Dict[str, Any]
        Fit dictionary from fit_importer.
    haems : List[str]
        Names of the haems to keep, as the fit names them; their order does not matter.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        A new fit dictionary with the same keys: 'haem_list' and 'data' hold only the
        kept haems, in the order of the fit, without the rows that are blank in all of
        them. The fit given is not changed. Raises ValueError, with a message for the
        user, when no haem is named or a name is not in the fit.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None. The wavelengths a decomposition uses are those shared by the kept haems
    (fit_range_finder), so leaving out a short haem can widen them.

    ---- Helpers ----
    None.
    """

    names = [str(name) for name in fit['haem_list']]
    if not haems:
        raise ValueError('No haem was chosen to fit. Choose at least one haem of the '
                         'fit file.',
                         )
    unknown = [str(haem) for haem in haems if str(haem) not in names]
    if unknown:
        raise ValueError(f"{', '.join(unknown)}: not in the fit file, which holds "
                         f"{', '.join(names)}. Choose haems the fit file holds.",
                         )
    kept = [i for i, name in enumerate(names) if name in {str(h) for h in haems}]
    columns = [column for i in kept for column in (2 * i, 2 * i + 1)]
    data = fit['data'].iloc[:, columns].dropna(how='all').reset_index(drop=True)
    return dict(fit, haem_list=[names[i] for i in kept], data=data)


# ---- fit_importer --------------------------------------------------------------------
def fit_importer(filename: Path) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to import a haem spectral fit CSV, checked and on the standard scale.

    ---- Inputs ----
    filename : Path
        CSV with (wavelength, response) column pairs, one pair per haem, the haem's
        name over its wavelength column; the haems may have different lengths. Either
        in the layout with heading lines (first cell FIT_FILE_MARK, then a Unit line;
        see DATA_FORMAT.md, "fit csv"), or the older layout whose first row is the haem
        names.

    ---- Globals read ----
    FIT_FILE_MARK (module constant).

    ---- Outputs ----
    Dict[str, Any]
        {'haem_list': haem names, the a haems first, then the b, then the c
        (haem_order_finder), 'data': the cleaned table (_fit_table_cleaner) on the
        standard scale, its column pairs in that order, 'scale_divisor': what the values
        of the file were divided by (1, 1 000 or 1 000 000), 'notes': sentences for
        the user about rows left out and the scale}. A file with heading lines gives
        its names in figure form (haem_name_typesetter); an older file gives them as
        written. Raises ValueError, with a message for the user, when the file cannot
        be read as a fit.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_table_cleaner
    _headed_fit_reader
    fit_scale_standardiser
    haem_order_finder
    """

    # ---- 1 Read the text -------------------------------------------------------------
    label = Path(filename).name
    unreadable = (f'{label} could not be read as a table with commas between its '
                  'columns. Open it to check it, or choose another fit file.'
                  )
    try:
        text = Path(filename).read_text(encoding='utf-8-sig')
        lines = text.splitlines()
        first = next(csv.reader(lines[:1]), [])
    except (OSError, UnicodeDecodeError, csv.Error):
        raise ValueError(unreadable) from None

    # ---- 2 Read the layout with heading lines, or the older one ----------------------
    if first and first[0].strip().lower() == FIT_FILE_MARK.lower():
        data, divisor, notes = _headed_fit_reader(lines, label)
    else:
        try:
            raw = pd.read_csv(io.StringIO(text), delimiter=',')
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            raise ValueError(unreadable) from None
        cleaned, notes = _fit_table_cleaner(raw, label)
        data, divisor, scale_notes = fit_scale_standardiser(cleaned, label)
        notes = notes + scale_notes

    # ---- 3 Put the haems in order: the a haems, then the b, then the c ---------------
    # every list, figure and workbook follows this order, whatever the file's own
    names = [str(name) for name in data.columns[::2]]
    order = haem_order_finder(names)
    data = data.iloc[:, [column for i in order for column in (2 * i, 2 * i + 1)]]
    return {'haem_list': [names[i] for i in order],
            'data': data,
            'scale_divisor': divisor,
            'notes': notes,
            }


# ---- fit_loader ----------------------------------------------------------------------
def fit_loader(fits_folder: Path, name: str) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to load a fit by the name the fit list and the answers give it: the
    preset of that name, otherwise the fit file of that name in the fits folder.

    ---- Inputs ----
    fits_folder : Path
        The fits folder, holding the haems and presets folders and the user's own fit
        files.
    name : str
        File name of the fit, as fit_names_lister gives it ('<name>.csv').

    ---- Globals read ----
    HAEMS_FOLDER_NAME, PRESETS_FOLDER_NAME (module constants).

    ---- Outputs ----
    Dict[str, Any]
        Fit dictionary, as fit_importer gives it (with 'haem_files' for a preset).
        Raises ValueError, with a message for the user, when there is no such fit or
        it cannot be read.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    fit_importer
    preset_importer
    """

    preset = fits_folder / PRESETS_FOLDER_NAME / name
    if preset.is_file():
        return preset_importer(preset, fits_folder / HAEMS_FOLDER_NAME)
    own = fits_folder / name
    if own.is_file():
        return fit_importer(own)
    raise ValueError(f'There is no preset or fit file called {name} in {fits_folder}. '
                     'Choose another fit.',
                     )


# ---- fit_names_lister ----------------------------------------------------------------
def fit_names_lister(fits_folder: Path) -> List[str]:
    """
    ---- Summary ----
    Main function to list the fits offered in the fit question and the settings strip:
    the presets, then the user's own fit files.

    ---- Inputs ----
    fits_folder : Path
        The fits folder.

    ---- Globals read ----
    PRESETS_FOLDER_NAME (module constant).

    ---- Outputs ----
    List[str]
        File names ('<name>.csv'): the presets, then the .csv files of the fits folder
        itself, each group sorted without regard to case. A file of the fits folder
        with a preset's name is left out, as the preset is what that name loads (an
        old copy of the fit, kept in the Mac app's Portimao folder). Empty when there
        is nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    def name_sorter(folder: Path) -> List[str]:
        return sorted((path.name for path in folder.glob('*.csv')), key=str.lower)
    presets = name_sorter(fits_folder / PRESETS_FOLDER_NAME)
    taken = {name.lower() for name in presets}
    return presets + [name for name in name_sorter(fits_folder)
                      if name.lower() not in taken
                      ]


# ---- fit_range_finder ----------------------------------------------------------------
def fit_range_finder(fit_data: pd.DataFrame) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to find the wavelength range shared by all the haems of a fit: the
    only part of a spectrum the decomposition uses.

    ---- Inputs ----
    fit_data : pd.DataFrame
        Fit table from fit_importer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (lowest, highest) wavelength of the shared range (nm). Raises ValueError, with
        a message for the user, when a haem of the fit has no rows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    lowest = the highest of the haems' first wavelengths; highest = the lowest of
    their last wavelengths.

    ---- Helpers ----
    _haem_shape_getter
    """

    ranges = [_haem_shape_getter(fit_data, i)[0]
              for i in range(fit_data.shape[1] // 2)
              ]
    if not ranges or any(x.size == 0 for x in ranges):
        raise ValueError('One of the haems of the fit has no values, so the amounts '
                         'cannot be worked out. Choose another fit file.',
                         )
    return (max(float(x.min()) for x in ranges), min(float(x.max()) for x in ranges))


# ---- fit_scale_standardiser ----------------------------------------------------------
def fit_scale_standardiser(data: pd.DataFrame,
                           label: str,
                           ) -> Tuple[pd.DataFrame, float, List[str]]:
    """
    ---- Summary ----
    Main function to bring a fit table to the standard scale, so that the raw haem
    amounts are on the same scale whichever fit is used.

    ---- Inputs ----
    data : pd.DataFrame
        Fit table: (wavelength, response) column pairs, one pair per haem.
    label : str
        Name of the fit, used in the notes.

    ---- Globals read ----
    FIT_PEAK_BAND, FIT_LARGE_SCALE (module constants).

    ---- Outputs ----
    Tuple[pd.DataFrame, float, List[str]]
        (the table on the standard scale, what its responses were divided by, the
        notes for the user). A fit a million above the standard is divided by a
        million, with a note; a fit on neither scale is returned unchanged, with a
        warning.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    peak = largest |response| in the table. Standard: low <= peak <= high
    (FIT_PEAK_BAND). Large: low x 1e6 <= peak <= high x 1e6, then response = response
    / 1e6. The mOD and % values do not depend on the scale; the raw amounts do.

    ---- Helpers ----
    None.
    """

    responses = data.iloc[:, 1::2].to_numpy(dtype=float)
    peak = float(np.nanmax(np.abs(responses))) if np.isfinite(responses).any() else 0.0
    low, high = FIT_PEAK_BAND
    if low <= peak <= high:
        return data, 1.0, []
    if low * FIT_LARGE_SCALE <= peak <= high * FIT_LARGE_SCALE:
        scaled = data.copy()
        scaled.iloc[:, 1::2] = responses / FIT_LARGE_SCALE
        return scaled, FIT_LARGE_SCALE, [
            f'{label}: its shapes are a million times larger than the standard scale, '
            'so they were divided by 1 000 000. The raw haem amounts are then on the '
            'same scale as with the other fits; mOD and % are the same on any scale.',
            ]
    return data, 1.0, [
        f'Warning: {label}: the highest point of its shapes is {peak:.3g}, far from '
        f'the standard scale ({low:g} to {high:g}), so the raw haem amounts will be '
        'on another scale than with the other fits. mOD and % are not affected.',
        ]


# ---- haem_files_combiner -------------------------------------------------------------
def haem_files_combiner(paths: Sequence[Path]) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to join library files, one haem each, into one fit, so a
    decomposition can use any set of haems of the library.

    ---- Inputs ----
    paths : Sequence[Path]
        The library files (fit csv, one haem each), in any order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        Fit dictionary with the keys of fit_importer ('haem_list', 'data',
        'scale_divisor', 'notes') and 'haem_files': the file name of each haem, in the
        order of 'haem_list' (the a haems, then the b, then the c). Raises ValueError,
        with a message for the user, when no file is given, a file is missing, cannot
        be read or holds more than one haem, two haems have the same name, or the files
        are on different scales.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None. Each haem keeps its own rows; shorter haems end in blanks.

    ---- Helpers ----
    fit_importer
    haem_name_plainer
    haem_order_finder
    """

    # ---- 1 Read each file ------------------------------------------------------------
    if not paths:
        raise ValueError('No haem file was chosen. Choose at least one haem.')
    fits = []
    for path in paths:
        path = Path(path)
        if not path.is_file():
            raise ValueError(f'The haem file {path.name} is not in {path.parent}. Put '
                             'it back, or choose other haems.',
                             )
        fit = fit_importer(path)
        if len(fit['haem_list']) != 1:
            raise ValueError(f'{path.name} holds {len(fit["haem_list"])} haems, but a '
                             'file of the haem library holds one. Split it into one '
                             'file per haem, or move it to the fits folder itself.',
                             )
        fits.append((path.name, fit))

    # ---- 2 Check the names and the scales --------------------------------------------
    names = [str(fit['haem_list'][0]) for _, fit in fits]
    plain = [haem_name_plainer(name) for name in names]
    twice = sorted({name for name in plain if plain.count(name) > 1})
    if twice:
        raise ValueError(f"Two of the chosen haems are both called {', '.join(twice)}, "
                         'so they could not be told apart in the figures. Choose only '
                         'one of them.',
                         )
    divisors = {fit['scale_divisor'] for _, fit in fits}
    if len(divisors) > 1:
        raise ValueError('The chosen haem files give their shapes in different units, '
                         'so their amounts could not be compared. Check their Unit '
                         'lines.',
                         )

    # ---- 3 Join the tables in the order a, b, c --------------------------------------
    order = haem_order_finder(names)
    data = pd.concat([fits[i][1]['data'].reset_index(drop=True) for i in order],
                     axis=1,
                     )
    return {'haem_list': [names[i] for i in order],
            'data': data,
            'scale_divisor': divisors.pop(),
            'notes': [note for _, fit in fits for note in fit['notes']],
            'haem_files': [fits[i][0] for i in order],
            }


# ---- haem_name_plainer ---------------------------------------------------------------
def haem_name_plainer(name: str) -> str:
    """
    ---- Summary ----
    Main function to write a haem name in plain words, without the plotting codes of
    its figure form: 'Cyt $b_{557}$' becomes 'Cyt b557'. The reverse of
    haem_name_typesetter for the names it makes.

    ---- Inputs ----
    name : str
        Haem name, in figure form or plain.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The name with each $...$ part written without its $, _, { and } signs; a
        name without such a part is returned as it is.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return re.sub(r'\$([^$]*)\$',
                  lambda found: re.sub(r'[_{}\\]', '', found.group(1)),
                  str(name),
                  )


# ---- haem_name_typesetter ------------------------------------------------------------
def haem_name_typesetter(name: str) -> str:
    """
    ---- Summary ----
    Main function to put a plain haem name in the form the figures draw: the haem
    letters in italics and a capital letter or number after them below the line, so
    'Cyt bH' becomes 'Cyt $b_H$', 'Cyt a605' 'Cyt $a_{605}$' and 'Cyt cc' 'Cyt $cc$'.

    ---- Inputs ----
    name : str
        Plain haem name, words separated by spaces.

    ---- Globals read ----
    HAEM_NAME_WORD (module constant).

    ---- Outputs ----
    str
        The name with each haem word (HAEM_NAME_WORD: one to three of the letters a,
        b, c, d, o, then a capital letter or a number) in figure form; other words,
        such as 'Cyt', 'PC1' or 'a-like', as written.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    words = []
    for word in str(name).split(' '):
        found = HAEM_NAME_WORD.fullmatch(word)
        if found is None:
            words.append(word)
            continue
        letters, below = found.groups()
        if not below:
            words.append(f'${letters}$')
        elif len(below) == 1:
            words.append(f'${letters}_{below}$')
        else:
            words.append(f'${letters}_{{{below}}}$')
    return ' '.join(words)


# ---- library_haems_lister ------------------------------------------------------------
def library_haems_lister(fits_folder: Path) -> List[Dict[str, str]]:
    """
    ---- Summary ----
    Main function to list the haems of the library, for the tick boxes of Build a fit
    in the strip, reading only the top of each file.

    ---- Inputs ----
    fits_folder : Path
        The fits folder, holding the haems folder.

    ---- Globals read ----
    HAEMS_FOLDER_NAME (module constant); helpers.HAEM_TYPE_ORDER.

    ---- Outputs ----
    List[Dict[str, str]]
        [{'file': file name, 'haem': plain haem name, 'type': 'a', 'b', 'c' or
        'other'}], in the order a, b, c, then by file name ignoring case. A file whose
        top cannot be read is listed under its own name, type 'other', so ticking it
        says what is wrong. Empty when there is no haems folder.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_heading_reader
    haem_name_plainer
    haem_type_finder
    """

    listed = []
    for path in (fits_folder / HAEMS_FOLDER_NAME).glob('*.csv'):
        try:
            lines = path.read_text(encoding='utf-8-sig').splitlines()
            _, names_at = _fit_heading_reader(lines, path.name)
            cells = next(csv.reader([lines[names_at]]), [])
            haem = haem_name_plainer(next(cell.strip() for cell in cells
                                          if cell.strip()
                                          ),
                                     )
            kind = haem_type_finder(haem)
        except (OSError, UnicodeDecodeError, ValueError, StopIteration, csv.Error):
            haem, kind = path.stem, 'other'
        listed.append({'file': path.name, 'haem': haem, 'type': kind})
    ranks = HAEM_TYPE_ORDER + ('other',)
    return sorted(listed,
                  key=lambda item: (ranks.index(item['type']), item['file'].lower()),
                  )


# ---- preset_importer -----------------------------------------------------------------
def preset_importer(path: Path, haems_folder: Path) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to load a preset: the haem library files it lists, joined into one
    fit.

    ---- Inputs ----
    path : Path
        Preset file (DATA_FORMAT.md, "preset csv").
    haems_folder : Path
        The haem library folder the listed files are in.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        Fit dictionary, as haem_files_combiner gives it. Raises ValueError, with a
        message for the user, when the preset or one of its files cannot be used.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _preset_reader
    haem_files_combiner
    """

    names = _preset_reader(Path(path))
    try:
        return haem_files_combiner([haems_folder / name for name in names])
    except ValueError as exc:
        raise ValueError(f'The preset {Path(path).name} cannot be used: {exc}',
                         ) from None


# ---- s_array_generator ---------------------------------------------------------------
def s_array_generator(experimental_data: np.ndarray,
                      fit_data: pd.DataFrame,
                      background: str,
                      haemfactor: float,
                      ) -> np.ndarray:
    """
    ---- Summary ----
    Main function to generate the haem and background basis components for one
    spectrum.

    ---- Inputs ----
    experimental_data : np.ndarray
        Array of (wavelength, value) rows.
    fit_data : pd.DataFrame
        Fit table from fit_importer.
    background : str
        Background fitted under the haems, a key of BACKGROUND_LABELS.
    haemfactor : float
        Scale factor applied to the haem basis spectra.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Basis matrix, shape (n_filtered_wavelengths, n_haems + n_background_terms):
        haem fits (interpolated, times haemfactor), then the terms of the background.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    haem column = interp(fit) x haemfactor; the background terms are those of
    background_builder.

    ---- Helpers ----
    _haem_shape_getter
    background_builder
    data_filterer
    """

    # ---- 1 Find the wavelengths ------------------------------------------------------
    filtered = data_filterer(experimental_data, fit_data)
    wavelengths = filtered[:, 0]

    # ---- 2 Stack the haem spectra and the background ---------------------------------
    haems = [np.interp(wavelengths, *_haem_shape_getter(fit_data, i)) * haemfactor
             for i in range(fit_data.shape[1] // 2)
             ]
    return np.column_stack(haems + [background_builder(wavelengths, background)])


# ---- scatter_background_builder ------------------------------------------------------
def scatter_background_builder(wavelengths: np.ndarray,
                               degree_of_scatter: int,
                               ) -> np.ndarray:
    """
    ---- Summary ----
    Main function to build a flat level and the scatter terms 1/wavelength^k: the
    scatter backgrounds of the haem decomposition, and what the component finder takes
    out of the spectra.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths of the spectra (nm), shape (n_wavelengths).
    degree_of_scatter : int
        Number of 1/wavelength^k scatter terms (>= 0).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The terms as columns, shape (n_wavelengths, degree_of_scatter + 1): the
        constant 1 first, then scatter term k = 1, 2, ... Each scatter term runs from 1
        at the shortest wavelength to 0 at the longest.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    scatter term k = (1/wl^k - min) / (max - min) of 1/wl^k.

    ---- Helpers ----
    _unit_scaler
    """

    wavelengths = np.asarray(wavelengths, dtype=float)
    columns = [np.ones_like(wavelengths)]
    for k in range(1, degree_of_scatter + 1):
        columns.append(_unit_scaler(1 / wavelengths ** k))
    return np.column_stack(columns)


# ---- spectrum_decomposer -------------------------------------------------------------
def spectrum_decomposer(experimental_data: np.ndarray,
                        fit_data: pd.DataFrame,
                        background: str,
                        haemfactor: float,
                        ) -> Tuple[np.ndarray,
                                   np.ndarray,
                                   np.ndarray,
                                   np.ndarray,
                                   np.ndarray,
                                   List[np.ndarray],
                                   np.ndarray,
                                   ]:
    """
    ---- Summary ----
    Main function to decompose one experimental spectrum into haem contributions and
    background.

    ---- Inputs ----
    experimental_data : np.ndarray
        Array of (wavelength, value) rows.
    fit_data : pd.DataFrame
        Fit table from fit_importer.
    background : str
        Background fitted under the haems, a key of BACKGROUND_LABELS.
    haemfactor : float
        Scale factor applied to the haem basis spectra.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
    List[np.ndarray], np.ndarray]
        (c_array, filtered_data, background, background_subtracted, haems,
        haem_individual, residual); the spectra are (wavelength, value) columns.
        c_array holds the haem amounts, then the amounts of the background terms.
        Useful for inspecting one fit; experiment_decomposer uses an equivalent,
        faster route.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    c = the least-squares amounts of the basis S in the spectrum a (basis_solver);
    background = the background columns of S x their amounts; residual = a - (haems +
    background).

    ---- Helpers ----
    basis_solver
    data_filterer
    s_array_generator
    """

    # ---- 1 Prepare the fit data ------------------------------------------------------
    no_haems = int(len(fit_data.columns) / 2)
    filtered = data_filterer(experimental_data, fit_data)
    wavelengths = filtered[:, 0]
    absorbances = filtered[:, 1]

    # ---- 2 Solve for the coefficients ------------------------------------------------
    s_array = s_array_generator(experimental_data, fit_data, background, haemfactor)
    c_array = basis_solver(s_array, absorbances)

    # ---- 3 Rebuild the components ----------------------------------------------------
    scatter = s_array[:, no_haems:] @ c_array[no_haems:]
    haems = np.zeros_like(absorbances)
    haem_individual = []
    for i in range(no_haems):
        component = s_array[:, i] * c_array[i]
        haem_individual.append(np.column_stack((wavelengths, component)))
        haems += component

    # ---- 4 Calculate the residuals ---------------------------------------------------
    residual = absorbances - (haems + scatter)
    background_subtracted = absorbances - scatter
    return (c_array,
            filtered,
            np.column_stack((wavelengths, scatter)),
            np.column_stack((wavelengths, background_subtracted)),
            np.column_stack((wavelengths, haems)),
            haem_individual,
            np.column_stack((wavelengths, residual)),
            )
