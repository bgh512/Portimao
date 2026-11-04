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
        raise ValueError(f'{label}: no haem columns or finite times available for the '
                         f'delta absorbance.',
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
            raise ValueError(f'{label}: no finite {column!r} values between '
                             f'{start:.2f} and {stop:.2f} min for the delta '
                             'absorbance reference. Reduce the ignored start or end.',
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
    (delta_abs_calculator).

    ---- Equations ----
    c = (S^T S)^-1 S^T a for every spectrum (projector built once); haem_abs = c x peak
    amplitude of the haem basis spectrum x 1000 (OD to mOD); haem_delta_abs = haem_abs -
    mean of the highest window.

    ---- Helpers ----
    _wavelength_masker
    delta_abs_calculator
    s_array_generator
    """

    # ---- 1 Validate the fit and dataset ----------------------------------------------
    name = experiment.get('experiment_name', '<unknown>')
    if fit is None or 'data' not in fit or 'haem_list' not in fit:
        raise ValueError('A valid fit returned by import_fit() is required.')
    raw_spectra = experiment.get('raw_spectra', {})
    if dataset_name not in raw_spectra:
        raise ValueError(f'{name}: unknown spectral dataset {dataset_name!r}. '
                         f"Available datasets: {', '.join(raw_spectra) or '<none>'}",
                         )
    dataset = raw_spectra[dataset_name]
    if spectrum_type not in dataset:
        raise ValueError(f'{name}/{dataset_name}: spectral data type {spectrum_type!r}'
                         f' not found. '
                         f"Available fields: {', '.join(dataset)}",
                         )

    # ---- 2 Read and check the spectra ------------------------------------------------
    wavelengths = np.asarray(dataset['wavelengths'], dtype=float)
    spectra = np.asarray(dataset[spectrum_type], dtype=float)
    spectrum_indices = np.asarray(dataset['spectrum_indices'])
    times = np.asarray(dataset['time'], dtype=float)
    if wavelengths.ndim != 1:
        raise ValueError(f'{name}/{dataset_name}: wavelengths must be a 1D array.')
    if spectra.ndim != 2 or spectra.shape[1] != len(wavelengths):
        raise ValueError(f'{name}/{dataset_name}: {spectrum_type!r} must be a (spectra'
                         f' x wavelengths) array.',
                         )
    if len(spectrum_indices) != len(spectra) or len(times) != len(spectra):
        raise ValueError(f'{name}/{dataset_name}: spectrum index/time count does not '
                         f'match spectra.',
                         )
    if not np.all(np.isfinite(times)):
        raise ValueError(f'{name}/{dataset_name}: spectrum times are unavailable '
                         f'(spectra/CsO2 length mismatch).',
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
    projector = np.linalg.inv(s_array.T @ s_array) @ s_array.T
    coefficients = spectra[:, mask] @ projector.T  # (n_spectra, n_components)
    haem_conc = pd.DataFrame(coefficients[:, :len(haem_names)], columns=haem_names)
    haem_conc.insert(0, SPECTRUM_INDEX_COLUMN, spectrum_indices)
    haem_conc.insert(0, TIME_COLUMN, times)
    experiment['haem_conc'] = haem_conc

    # ---- 4 Calculate the absorbances -------------------------------------------------
    # Peak amplitude (OD per unit coefficient) of each haem's basis spectrum; x1000
    # converts OD to mOD.
    peak_amplitude = np.max(np.abs(s_array[:, :len(haem_names)]), axis=0)
    haem_abs = haem_conc.copy()
    haem_abs[haem_names] = coefficients[:, :len(haem_names)] * peak_amplitude * 1000.0
    haem_abs.attrs['peak_amplitude_OD'] = dict(zip(haem_names, peak_amplitude.tolist()))
    experiment['haem_abs'] = haem_abs
    experiment['haem_delta_abs'] = delta_abs_calculator(
        haem_abs,
        delta_exclude_first_minutes,
        delta_window_seconds,
        label=f'{name}/haem_abs',
        exclude_last_minutes=delta_exclude_last_minutes,
        )
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
        negated haem fits (interpolated, times haemfactor), a constant column, then the
        normalised scatter terms.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    haem column = -interp(fit) x haemfactor; scatter term k = (1/wl^k - min) / (max -
    min) of 1/wl^k.

    ---- Helpers ----
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
        s_array[:, i] = -np.interp(filtered[:, 0], fit_x, fit_y) * haemfactor

    # ---- 3 Add the scatter terms -----------------------------------------------------
    s_array[:, no_haems] = 1.0
    for i in range(degree_of_scatter):
        scatter_function = 1 / filtered[:, 0] ** (i + 1)
        shifted = scatter_function - np.amin(scatter_function)
        s_array[:, no_haems + i + 1] = shifted / np.amax(shifted)
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
    c = (S^T S)^-1 S^T a, where S is the basis matrix and a the spectrum; residual = a -
    (haems + scatter).

    ---- Helpers ----
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
    c_array = np.matmul(np.matmul(np.linalg.inv(np.matmul(np.transpose(s_array),
                                                          s_array,
                                                          ),
                                                ),
                                  np.transpose(s_array),
                                  ),
                        absorbances,
                        )

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
