"""
Spectral fit loading and haem decomposition routines.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import (measurement_column_finder,
                                 SPECTRUM_INDEX_COLUMN,
                                 TIME_COLUMN,
                                 time_getter,
                                 value_getter,
                                 )


# ---- SPECTRAL DECOMPOSER HELPERS -----------------------------------------------------


# ---- _best_window_finder -------------------------------------------------------------
def _best_window_finder(times: np.ndarray,
                        values: np.ndarray,
                        start: float,
                        stop: float,
                        width: float,
                        ) -> Optional[Tuple[float, float, float]]:
    """
    ---- Summary ----
    Helper function to find the window of a given length with the highest average.

    ---- Inputs ----
    times : np.ndarray
        Time of each spectrum in minutes.
    values : np.ndarray
        Value at each spectrum.
    start : float
        Earliest time that may be used.
    stop : float
        Latest time that may be used.
    width : float
        Window length in minutes.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Tuple[float, float, float]]
        (highest average, time of its first spectrum, time of its last spectrum), or
        None when there is no finite value between start and stop. When the usable
        part is shorter than the window, all of it is one window.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Window average = (running sum at the window end - running sum at its start) /
    number of spectra in the window.

    ---- Helpers ----
    None.
    """

    order = np.argsort(times)
    times, values = times[order], values[order]
    usable = (np.isfinite(times) & np.isfinite(values)
              & (times >= start) & (times <= stop))
    times, values = times[usable], values[usable]
    if times.size == 0:
        return None
    firsts = np.arange(times.size)
    ends = np.searchsorted(times, times + width, side='right')
    running = np.concatenate(([0.0], np.cumsum(values)))
    means = (running[ends] - running[firsts]) / (ends - firsts)
    fits = times + width <= stop + 1e-9
    if fits.any():
        means = np.where(fits, means, -np.inf)
    best = int(np.argmax(means))
    return float(means[best]), float(times[best]), float(times[ends[best] - 1])


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
        Boolean mask, True inside the shared range.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    fit_wavelength = fit_data.iloc[:, ::2]
    wmax = min(np.nanmax(fit_wavelength, axis=0))
    wmin = max(np.nanmin(fit_wavelength, axis=0))
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
    None. Calls _wavelength_masker.

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
                         exclude_first_minutes: float = 5.0,
                         window_seconds: float = 30.0,
                         label: str = 'haem_abs',
                         exclude_last_minutes: float = 0.0,
                         ) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to shift each haem absorbance so that its reference level is 0, giving
    a change in absorbance (mOD). The reference level of each haem is the average of its
    highest window (for example the fully oxidised point), wherever it occurs in the
    run outside the ignored start and end.

    ---- Inputs ----
    haem_abs : pd.DataFrame
        Haem absorbance table in mOD (time, spectrum index and one column per haem).
    exclude_first_minutes : float
        Minutes after the first measurement that are ignored at the start.
    window_seconds : float
        Length of the reference window, in seconds (> 0).
    label : str
        Name used in error messages.
    exclude_last_minutes : float
        Minutes before the last measurement that are ignored at the end.

    ---- Globals read ----
    schema.get_times, get_values, measurement_columns.

    ---- Outputs ----
    pd.DataFrame
        Shifted copy; the means and the window of each haem are stored in
        result.attrs["delta_abs_baseline"]. Raises ValueError for invalid settings or
        when no spectra are left after the ignored parts.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    delta_abs = abs - max over windows of mean(abs inside the window), per haem. The
    windows start at each spectrum and last window_seconds. Only a constant is
    subtracted, so differences between points are unchanged.

    ---- Helpers ----
    _best_window_finder
    measurement_column_finder
    time_getter
    value_getter
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    if window_seconds <= 0:
        raise ValueError('window_seconds must be positive.')
    if exclude_first_minutes < 0 or exclude_last_minutes < 0:
        raise ValueError('The ignored minutes cannot be negative.')

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
        found = _best_window_finder(times, values, start, stop, window_seconds / 60.0)
        if found is None:
            raise ValueError(f'{label}: no {column} values are left between '
                             f'{start:.2f} and {stop:.2f} min to find the zero of '
                             'delta A from. Ignore less of the start or the end of '
                             'the run.',
                             )
        reference[str(column)], first, last = found
        windows[str(column)] = (first, last)
        result[column] = values - reference[str(column)]
    spans = list(windows.values())
    result.attrs['delta_abs_baseline'] = {'mean_by_haem': reference,
                                          'window_by_haem': windows,
                                          'start_time': min(w[0] for w in spans),
                                          'end_time': max(w[1] for w in spans),
                                          }
    return result


# ---- experiment_decomposer -----------------------------------------------------------
def experiment_decomposer(experiment: dict,
                          fit: dict,
                          dataset_name: str = 'Cyt',
                          spectrum_type: str = 'attenuation',
                          degree_of_scatter: int = 1,
                          haemfactor: float = 1000000,
                          delta_exclude_first_minutes: float = 5.0,
                          delta_window_seconds: float = 30.0,
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
    spectrum_type : str
        Field of the dataset to decompose, e.g. 'attenuation'.
    degree_of_scatter : int
        Number of scatter terms.
    haemfactor : float
        Scale factor applied to the haem basis spectra.
    delta_exclude_first_minutes : float
        Start of the delta absorbance reference window, in minutes after the first
        spectrum.
    delta_window_seconds : float
        Length of the delta absorbance reference window, in seconds.
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
    haem_delta_abs = haem_abs - mean of the highest window.

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
        delta_window_seconds,
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
    Main function to import a haem spectral fit CSV.

    ---- Inputs ----
    filename : Path
        CSV with (wavelength, response) column pairs, one pair per haem; the header of
        each wavelength column names the haem.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Any]
        {"haem_list": haem names in file order, "data": the table as a data frame}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    data = pd.read_csv(filename, delimiter=',')
    headers = data.columns
    haem_names = [str(headers[i]) for i in range(len(headers)) if i % 2 == 0]
    return {'haem_list': haem_names, 'data': data}


# ---- s_array_generator ---------------------------------------------------------------
def s_array_generator(experimental_data: np.ndarray,
                      fit_data: pd.DataFrame,
                      degree_of_scatter: int = 1,
                      haemfactor: float = 1000000,
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
    background_builder
    data_filterer
    """

    # ---- 1 Prepare the array ---------------------------------------------------------
    filtered = data_filterer(experimental_data, fit_data)
    no_haems = int(len(fit_data.columns) / 2)
    s_array = np.zeros((len(filtered[:, 0]), no_haems + degree_of_scatter + 1))

    # ---- 2 Fill the haem spectra -----------------------------------------------------
    for i in range(no_haems):
        fit_x = fit_data.iloc[:, 2 * i]
        fit_y = fit_data.iloc[:, 2 * i + 1]
        s_array[:, i] = np.interp(filtered[:, 0], fit_x, fit_y) * haemfactor

    # ---- 3 Add the scatter terms -----------------------------------------------------
    s_array[:, no_haems:] = background_builder(filtered[:, 0], degree_of_scatter)
    return s_array


# ---- spectrum_decomposer -------------------------------------------------------------
def spectrum_decomposer(experimental_data: np.ndarray,
                        fit_data: pd.DataFrame,
                        degree_of_scatter: int = 1,
                        haemfactor: float = 1000000,
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
