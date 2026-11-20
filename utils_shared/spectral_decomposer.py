"""
Spectral fit loading and haem decomposition routines.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.reference_level import (reference_level_finder,
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


# ---- SPECTRAL DECOMPOSER HELPERS -----------------------------------------------------


# ---- _fit_table_cleaner --------------------------------------------------------------
def _fit_table_cleaner(data: pd.DataFrame,
                       label: str,
                       ) -> Tuple[pd.DataFrame, List[str]]:
    """
    ---- Summary ----
    Helper function to check the table of a fit file and to give every haem clean rows:
    numbers only, no blank rows, wavelengths going upwards.

    ---- Inputs ----
    data : pd.DataFrame
        The fit file as read: (wavelength, response) column pairs, one pair per haem;
        the header of each wavelength column names the haem. Row i of the table is row
        i + 2 of the file.
    label : str
        Name of the fit file, used in the messages.

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
        x = _number_column_reader(data.iloc[:, 2 * i], haem, 'wavelength', label)
        y = _number_column_reader(data.iloc[:, 2 * i + 1], haem, 'response', label)
        half = np.isnan(x) != np.isnan(y)
        if half.any():
            row = int(np.nonzero(half)[0][0]) + 2
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


# ---- _number_column_reader -----------------------------------------------------------
def _number_column_reader(column: pd.Series,
                          haem: str,
                          kind: str,
                          label: str,
                          ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to read one column of a fit file as numbers.

    ---- Inputs ----
    column : pd.Series
        The column as read from the file; row i is row i + 2 of the file.
    haem : str
        Name of the haem the column belongs to, used in the message.
    kind : str
        'wavelength' or 'response', used in the message.
    label : str
        Name of the fit file, used in the message.

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
        raise ValueError(f'{label}: the {kind} of {haem} in row {row + 2} is not a '
                         f'number ("{column.iloc[row]}"). Correct the cell, or choose '
                         'another fit file.',
                         )
    return numbers


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


# ---- background_builder --------------------------------------------------------------
def background_builder(wavelengths: np.ndarray,
                       degree_of_scatter: int = 1,
                       ) -> np.ndarray:
    """
    ---- Summary ----
    Main function to build the background terms that every decomposition fits beside
    its shapes: a constant and the scatter terms.

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
    None.
    """

    wavelengths = np.asarray(wavelengths, dtype=float)
    columns = [np.ones_like(wavelengths)]
    for k in range(1, degree_of_scatter + 1):
        scatter = 1 / wavelengths ** k
        shifted = scatter - np.amin(scatter)
        columns.append(shifted / np.amax(shifted))
    return np.column_stack(columns)


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


# ---- delta_abs_calculator ------------------------------------------------------------
def delta_abs_calculator(haem_abs: pd.DataFrame,
                         exclude_first_minutes: float,
                         window_points: int,
                         label: str = 'haem_abs',
                         exclude_last_minutes: float = 0.0,
                         ) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to shift each haem absorbance so that its reference level is 0, giving
    a change in absorbance (mOD). The reference level of each haem is the median of its
    highest points in a row (for example the fully oxidised point), wherever they occur
    in the run outside the ignored start and end.

    ---- Inputs ----
    haem_abs : pd.DataFrame
        Haem absorbance table in mOD (time, spectrum index and one column per haem).
    exclude_first_minutes : float
        Minutes after the first measurement that are ignored at the start.
    window_points : int
        Number of spectra in a row that make the reference window (>= 1).
    label : str
        Name used in error messages.
    exclude_last_minutes : float
        Minutes before the last measurement that are ignored at the end.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Shifted copy; result.attrs["delta_abs_baseline"] holds {'level_by_haem': the
        level subtracted from each haem (mOD), 'window_by_haem': the (first, last)
        time of each haem's window (min), 'window_points', 'window_seconds': the
        length of such a window}. Raises ValueError, with a message for the user, for
        invalid settings or when fewer than window_points spectra are left after the
        ignored parts.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    delta_abs = abs - max over windows of median(abs inside the window), per haem
    (reference_level_finder). Only a constant is subtracted, so differences between
    points are unchanged.

    ---- Helpers ----
    measurement_column_finder
    reference_level_finder
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
                         'of delta A from. Check that the fit file holds haems and '
                         'that the file was read fully.',
                         )
    start = float(finite_times.min()) + exclude_first_minutes
    stop = float(finite_times.max()) - exclude_last_minutes

    # ---- 3 Subtract the highest window of each haem ----------------------------------
    result = haem_abs.copy()
    reference: Dict[str, float] = {}
    windows: Dict[str, Tuple[float, float]] = {}
    for column in columns:
        values = value_getter(haem_abs, column)
        found = reference_level_finder(times, values, start, stop, window_points)
        if found is None:
            raise ValueError(f'{label}: fewer than {window_points} {column} values '
                             f'are left between {start:.2f} and {stop:.2f} min, too '
                             'few to find the zero of delta A (the median of the '
                             f'highest {window_points} points in a row). Ignore less '
                             'of the start or the end of the run.',
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
                          degree_of_scatter: int,
                          haemfactor: float,
                          delta_exclude_first_minutes: float,
                          delta_window_points: int,
                          spectrum_type: str = 'attenuation',
                          delta_exclude_last_minutes: float = 0.0,
                          ) -> dict:
    """
    ---- Summary ----
    Main function to decompose every spectrum of one dataset into haem concentrations
    and absorbances.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    fit : dict
        Fit dictionary from fit_importer.
    dataset_name : str
        Spectral dataset to decompose.
    degree_of_scatter : int
        Number of scatter terms.
    haemfactor : float
        Scale factor applied to the haem basis spectra.
    delta_exclude_first_minutes : float
        Minutes after the first spectrum that are ignored when finding the delta
        absorbance reference.
    delta_window_points : int
        Number of spectra in a row that make the delta absorbance reference window.
    spectrum_type : str
        Field of the dataset to decompose, e.g. 'attenuation'.
    delta_exclude_last_minutes : float
        Minutes before the last spectrum that are ignored when finding the delta
        absorbance reference.

    ---- Globals read ----
    schema.TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError for an invalid fit or dataset
        or inconsistent array shapes.

    ---- Globals mutated ----
    experiment: adds haem_conc (time, spectrum index, one column per haem), haem_abs
    (mOD, same layout; attrs["peak_amplitude_OD"]) and haem_delta_abs
    (delta_abs_calculator). The three are added together at the end; when anything
    fails, the experiment holds none of them, not even those of an earlier
    decomposition.

    ---- Equations ----
    c = the least-squares amounts of the basis S in every spectrum (basis_solver);
    haem_abs = c x peak amplitude of the haem basis spectrum x 1000 (OD to mOD);
    haem_delta_abs = haem_abs - median of the highest points in a row.

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
                                degree_of_scatter,
                                haemfactor,
                                )
    coefficients = basis_solver(s_array, spectra[:, mask])  # (n_spectra, n_components)
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


# ---- fit_importer --------------------------------------------------------------------
def fit_importer(filename: Path) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to import a haem spectral fit CSV, checked and on the standard scale.

    ---- Inputs ----
    filename : Path
        CSV with (wavelength, response) column pairs, one pair per haem; the header of
        each wavelength column names the haem. The haems may have different lengths.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        {'haem_list': haem names in file order, 'data': the cleaned table
        (_fit_table_cleaner) on the standard scale, 'scale_divisor': what the responses
        of the file were divided by (1 or 1 000 000), 'notes': sentences for the user
        about rows left out and the scale}. Raises ValueError, with a message for the
        user, when the file cannot be read as a fit.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _fit_table_cleaner
    fit_scale_standardiser
    """

    label = Path(filename).name
    try:
        raw = pd.read_csv(filename, delimiter=',')
    except (OSError,
            UnicodeDecodeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            ):
        raise ValueError(f'{label} could not be read as a table with commas between '
                         'its columns. Open it to check it, or choose another fit '
                         'file.',
                         ) from None
    cleaned, notes = _fit_table_cleaner(raw, label)
    data, divisor, scale_notes = fit_scale_standardiser(cleaned, label)
    return {'haem_list': [str(name) for name in data.columns[::2]],
            'data': data,
            'scale_divisor': divisor,
            'notes': notes + scale_notes,
            }


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


# ---- fit_scale_standardiser----------------------------------------------------------


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


# ---- s_array_generator ---------------------------------------------------------------
def s_array_generator(experimental_data: np.ndarray,
                      fit_data: pd.DataFrame,
                      degree_of_scatter: int,
                      haemfactor: float,
                      ) -> np.ndarray:
    """
    ---- Summary ----
    Main function to generate the haem and scatter basis components for one spectrum.

    ---- Inputs ----
    experimental_data : np.ndarray
        Array of (wavelength, value) rows.
    fit_data : pd.DataFrame
        Fit table from fit_importer.
    degree_of_scatter : int
        Number of 1/wavelength^k scatter terms.
    haemfactor : float
        Scale factor applied to the haem basis spectra.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Basis matrix, shape (n_filtered_wavelengths, n_haems + degree_of_scatter + 1):
        haem fits (interpolated, times haemfactor), a constant column, then the
        normalised scatter terms.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    haem column = interp(fit) x haemfactor; the constant and the scatter terms are
    those of background_builder.

    ---- Helpers ----
    _haem_shape_getter
    background_builder
    data_filterer
    """

    # ---- 1 Prepare the array ---------------------------------------------------------
    filtered = data_filterer(experimental_data, fit_data)
    no_haems = int(len(fit_data.columns) / 2)
    s_array = np.zeros((len(filtered[:, 0]), no_haems + degree_of_scatter + 1))

    # ---- 2 Fill the haem spectra -----------------------------------------------------
    for i in range(no_haems):
        fit_x, fit_y = _haem_shape_getter(fit_data, i)
        s_array[:, i] = np.interp(filtered[:, 0], fit_x, fit_y) * haemfactor

    # ---- 3 Add the scatter terms -----------------------------------------------------
    s_array[:, no_haems:] = background_builder(filtered[:, 0], degree_of_scatter)
    return s_array


# ---- spectrum_decomposer -------------------------------------------------------------
def spectrum_decomposer(experimental_data: np.ndarray,
                        fit_data: pd.DataFrame,
                        degree_of_scatter: int,
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
    scatter.

    ---- Inputs ----
    experimental_data : np.ndarray
        Array of (wavelength, value) rows.
    fit_data : pd.DataFrame
        Fit table from fit_importer.
    degree_of_scatter : int
        Number of scatter terms.
    haemfactor : float
        Scale factor applied to the haem basis spectra.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
    List[np.ndarray], np.ndarray]
        (c_array, filtered_data, scatter, background_subtracted, haems, haem_individual,
        residual); the spectra are (wavelength, value) columns. Useful for inspecting
        one fit; experiment_decomposer uses an equivalent, faster route.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    c = the least-squares amounts of the basis S in the spectrum a (basis_solver);
    residual = a - (haems + scatter).

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
    s_array = s_array_generator(experimental_data,
                                fit_data,
                                degree_of_scatter,
                                haemfactor,
                                )
    c_array = basis_solver(s_array, absorbances)

    # ---- 3 Rebuild the components ----------------------------------------------------
    scatter = np.zeros_like(absorbances)
    for i in range(degree_of_scatter + 1):
        scatter += s_array[:, -(i + 1)] * c_array[-(i + 1)]
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
