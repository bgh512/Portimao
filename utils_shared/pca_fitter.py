"""
Principal component analysis of the spectra of several experiments, to build a fit.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd


# ---- CONSTANTS -----------------------------------------------------------------------
ENOUGH_VARIANCE = 0.99
MAX_COMPONENTS = 10
MINIMUM_RATIO = 2.0  # smallest drop between neighbouring components counted as a gap


# ---- PCA FITTER HELPERS --------------------------------------------------------------


# ---- _component_orienter -------------------------------------------------------------
def _component_orienter(vectors: np.ndarray) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to give each component the same convention as the fit files: its
    largest peak positive and equal to 1.

    ---- Inputs ----
    vectors : np.ndarray
        Components as columns, shape (n_wavelengths, n_components).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The components, each divided by its largest absolute value and with the sign
        that makes that value positive.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    e = v x sign(v[i]) / |v[i]|, with i the position of the largest |v|.

    ---- Helpers ----
    None.
    """

    oriented = np.array(vectors, dtype=float)
    for j in range(oriented.shape[1]):
        peak = oriented[np.argmax(np.abs(oriented[:, j])), j]
        if peak != 0:
            oriented[:, j] /= peak
    return oriented


# ---- _nuisance_basis_builder ---------------------------------------------------------
def _nuisance_basis_builder(wavelengths: np.ndarray,
                            degree_of_scatter: int,
                            ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to build the offset and scatter terms that the haem decomposition
    fits alongside the haems, as an orthonormal basis, so they can be taken out of the
    spectra before the components are searched for.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths of the spectra (nm).
    degree_of_scatter : int
        Number of 1/wavelength^k scatter terms.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Orthonormal columns spanning the constant and the scatter terms, shape
        (n_wavelengths, degree_of_scatter + 1).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The columns are 1 and (1/wl^k - min) / (max - min) as in s_array_generator,
    orthonormalised by QR.

    ---- Helpers ----
    None.
    """

    columns = [np.ones_like(wavelengths)]
    for k in range(1, degree_of_scatter + 1):
        scatter = 1 / wavelengths ** k
        shifted = scatter - np.amin(scatter)
        columns.append(shifted / np.amax(shifted))
    q, _ = np.linalg.qr(np.column_stack(columns))
    return q


# ---- _spectra_gridder ----------------------------------------------------------------
def _spectra_gridder(wavelengths: np.ndarray,
                     spectra: np.ndarray,
                     grid: np.ndarray,
                     ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to put the spectra of one file on the common wavelength grid.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths of the file (nm), ascending.
    spectra : np.ndarray
        Spectra of the file, shape (n_spectra, n_wavelengths).
    grid : np.ndarray
        The wavelengths to give the spectra at (nm).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Spectra on the grid, shape (n_spectra, len(grid)). Spectra already on the grid
        are returned as they are.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Linear interpolation of each spectrum at the grid wavelengths.

    ---- Helpers ----
    None.
    """

    if len(wavelengths) == len(grid) and np.allclose(wavelengths, grid):
        return np.asarray(spectra, dtype=float)
    return np.array([np.interp(grid, wavelengths, row) for row in spectra],
                    dtype=float,
                    )


# ---- _varimax_rotator ----------------------------------------------------------------
def _varimax_rotator(loadings: np.ndarray,
                     max_iterations: int = 500,
                     tolerance: float = 1e-9,
                     ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to find the rotation that makes the components as simple as
    possible (each concentrated on a few wavelengths), which makes them look more like
    single haem spectra than the plain principal components do.

    ---- Inputs ----
    loadings : np.ndarray
        Components as columns, shape (n_wavelengths, n_components).
    max_iterations : int
        Most iterations to run.
    tolerance : float
        The iteration stops when the criterion improves by less than this fraction.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Orthogonal rotation matrix, shape (n_components, n_components).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Varimax: maximise the variance of the squared loadings of every component. Each
    step is R = U V^T from the SVD of L^T (Lr^3 - Lr diag(sum Lr^2) / p), Lr = L R.

    ---- Helpers ----
    None.
    """

    points, count = loadings.shape
    rotation = np.eye(count)
    criterion = 0.0
    for _ in range(max_iterations):
        rotated = loadings @ rotation
        target = rotated ** 3 - rotated @ np.diag(np.sum(rotated ** 2, axis=0)) / points
        u, s, vt = np.linalg.svd(loadings.T @ target)
        rotation = u @ vt
        previous, criterion = criterion, float(np.sum(s))
        if previous != 0 and criterion < previous * (1 + tolerance):
            break
    return rotation


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- component_builder ---------------------------------------------------------------
def component_builder(analysis: dict,
                      count: int,
                      rotate: bool = True,
                      ) -> dict:
    """
    ---- Summary ----
    Main function to take the first components of an analysis, optionally rotate them
    to simpler shapes, and give them the conventions of the fit files.

    ---- Inputs ----
    analysis : dict
        Result of component_finder.
    count : int
        Number of components to keep.
    rotate : bool
        True to apply the varimax rotation (the components then span the same space and
        leave the same residual, but are more peak-like).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {'wavelengths', 'components' (columns, largest peak = +1), 'explained' (fraction
        of the variance of each component), 'residual_rms' (OD left unexplained),
        'peaks' (wavelength of each peak), 'count', 'rotated'}. Components are ordered
        by the variance they explain. Raises ValueError for an impossible count.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    residual RMS = sqrt((total variance - variance of the kept components) / number of
    values).

    ---- Helpers ----
    _component_orienter
    _varimax_rotator
    """

    # ---- 1 Check the count -----------------------------------------------------------
    available = analysis['eigenvectors'].shape[1]
    if not 1 <= count <= available:
        raise ValueError(f'The number of components must be from 1 to {available}.')

    # ---- 2 Rotate and order the components -------------------------------------------
    vectors = analysis['eigenvectors'][:, :count]
    do_rotate = bool(rotate and count > 1)
    if do_rotate:
        vectors = vectors @ _varimax_rotator(vectors)
    gram = analysis['gram']
    variance = np.array([float(v @ gram @ v) for v in vectors.T])
    order = np.argsort(-variance)
    vectors, variance = vectors[:, order], variance[order]

    # ---- 3 Describe them -------------------------------------------------------------
    total = analysis['total_variance']
    left = max(total - float(np.sum(variance)), 0.0)
    components = _component_orienter(vectors)
    peaks = analysis['wavelengths'][np.argmax(np.abs(components), axis=0)]
    return {'wavelengths': analysis['wavelengths'],
            'components': components,
            'explained': variance / total,
            'residual_rms': float(np.sqrt(left / analysis['n_values'])),
            'peaks': peaks,
            'count': count,
            'rotated': do_rotate,
            }


# ---- component_count_suggester -------------------------------------------------------
def component_count_suggester(analysis: dict) -> int:
    """
    ---- Summary ----
    Main function to suggest how many components to use. This is a rule of thumb, not a
    proof: it looks for the biggest drop between neighbouring principal components
    (where the signal ends and the noise starts) and, when there is no clear drop,
    takes enough components to explain nearly all of the variance.

    ---- Inputs ----
    analysis : dict
        Result of component_finder.

    ---- Globals read ----
    ENOUGH_VARIANCE, MINIMUM_RATIO (module constants).

    ---- Outputs ----
    int
        Suggested number of components, at least 2 when two or more are available.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Singular value s_j = sqrt(eigenvalue j). Suggested k = the k from 2 to K-1 with the
    largest s_k / s_(k+1), if that ratio is at least 2; otherwise the smallest k with
    cumulative variance >= 99%.

    ---- Helpers ----
    None.
    """

    values = np.sqrt(np.clip(analysis['eigenvalues'], 1e-300, None))
    available = len(values)
    if available <= 2:
        return available
    ratios = values[1:-1] / values[2:]  # entry i is the drop after component i + 2
    best = int(np.argmax(ratios))
    if ratios[best] >= MINIMUM_RATIO:
        return best + 2
    cumulative = np.cumsum(analysis['eigenvalues']) / analysis['total_variance']
    enough = np.nonzero(cumulative >= ENOUGH_VARIANCE)[0]
    return int(enough[0]) + 1 if len(enough) else available


# ---- component_finder ----------------------------------------------------------------
def component_finder(spectra_sets: List[dict],
                     window: Tuple[float, float],
                     max_components: int = MAX_COMPONENTS,
                     degree_of_scatter: int = 1,
                     ) -> dict:
    """
    ---- Summary ----
    Main function to run a principal component analysis on the spectra of all the files
    together, inside a spectral window. The offset and scatter terms that the haem
    decomposition fits as well are removed from every spectrum first, and each file's
    average spectrum is removed, so the components describe how the spectra change and
    differences between preparations do not become components.

    ---- Inputs ----
    spectra_sets : List[dict]
        One entry per file: {'name', 'wavelengths' (nm), 'spectra' (n_spectra x
        n_wavelengths, the same attenuation the decomposition uses)}; only the part
        kept after trimming and ignoring.
    window : Tuple[float, float]
        (start, end) wavelength of the analysis, in nm.
    max_components : int
        Most components worked out.
    degree_of_scatter : int
        Number of scatter terms (the same as the haem decomposition uses).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {'wavelengths', 'eigenvectors' (columns, orthonormal), 'eigenvalues',
        'gram', 'total_variance', 'n_values', 'n_spectra', 'counts' ({file name: number
        of spectra used}), 'window', 'degree_of_scatter'}. Raises ValueError when the
        window or the data cannot be analysed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    X = spectra with the nuisance terms projected out and the file mean removed;
    G = sum over files of X^T X; the components are the eigenvectors of G.

    ---- Helpers ----
    _nuisance_basis_builder
    _spectra_gridder
    """

    # ---- 1 Find the wavelengths to analyse -------------------------------------------
    start, end = float(window[0]), float(window[1])
    if end <= start:
        raise ValueError('The end of the window must be above its start.')
    usable = [s for s in spectra_sets if len(s['spectra']) >= 2]
    if not usable:
        raise ValueError('There are no spectra to analyse (a file needs at least two '
                         'spectra after trimming).',
                         )
    first = np.asarray(usable[0]['wavelengths'], dtype=float)
    grid = first[(first >= start) & (first <= end)]
    if len(grid) < degree_of_scatter + 6:
        raise ValueError('The window holds too few wavelengths; widen it.')
    low = max(np.min(s['wavelengths']) for s in usable)
    high = min(np.max(s['wavelengths']) for s in usable)
    if grid[0] < low or grid[-1] > high:
        grid = grid[(grid >= low) & (grid <= high)]
        if len(grid) < degree_of_scatter + 6:
            raise ValueError(f'The files only share {low:g} to {high:g} nm; choose a '
                             f'window inside that.',
                             )

    # ---- 2 Clean the spectra and add up the covariance -------------------------------
    nuisance = _nuisance_basis_builder(grid, degree_of_scatter)
    gram = np.zeros((len(grid), len(grid)))
    counts: Dict[str, int] = {}
    for entry in usable:
        data = _spectra_gridder(np.asarray(entry['wavelengths'], dtype=float),
                                np.asarray(entry['spectra'], dtype=float),
                                grid,
                                )
        data = data[np.all(np.isfinite(data), axis=1)]
        if len(data) < 2:
            continue
        data = data - (data @ nuisance) @ nuisance.T
        data = data - data.mean(axis=0)
        gram += data.T @ data
        counts[entry['name']] = len(data)
    if not counts:
        raise ValueError('No file had usable spectra inside the window.')

    # ---- 3 Find the components -------------------------------------------------------
    values, vectors = np.linalg.eigh(gram)
    values, vectors = values[::-1], vectors[:, ::-1]
    total = float(np.sum(np.clip(values, 0.0, None)))
    if total <= 0:
        raise ValueError('The spectra do not change inside the window.')
    keep = min(max_components, len(grid) - degree_of_scatter - 2)
    n_spectra = sum(counts.values())
    return {'wavelengths': grid,
            'eigenvectors': vectors[:, :keep],
            'eigenvalues': np.clip(values[:keep], 0.0, None),
            'gram': gram,
            'total_variance': total,
            'n_values': n_spectra * len(grid),
            'n_spectra': n_spectra,
            'counts': counts,
            'window': (float(grid[0]), float(grid[-1])),
            'degree_of_scatter': degree_of_scatter,
            }


# ---- fit_saver -----------------------------------------------------------------------
def fit_saver(fit: dict, path: Path) -> Path:
    """
    ---- Summary ----
    Main function to save a fit in the layout of the fit files in the fits folder
    (a header naming each haem over its wavelength column, one (wavelength, response)
    pair of columns per haem).

    ---- Inputs ----
    fit : dict
        Fit dictionary from fit_table_builder.
    path : Path
        File to write (.csv).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The file written.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    header = []
    for name in fit['haem_list']:
        header += [name, f'{name} response']
    fit['data'].to_csv(path,
                       index=False,
                       header=header,
                       lineterminator='\r\n',
                       float_format='%.6g',
                       )
    return path


# ---- fit_table_builder ---------------------------------------------------------------
def fit_table_builder(result: dict, names: Optional[List[str]] = None) -> dict:
    """
    ---- Summary ----
    Main function to turn the components found into a fit dictionary, exactly as
    fit_importer gives for a fit file, so the haem decomposition can use it.

    ---- Inputs ----
    result : dict
        Result of component_builder.
    names : Optional[List[str]]
        Name of each component; None names them PC1, PC2, ...

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {'haem_list': names, 'data': table of (wavelength, response) column pairs}.
        The responses are the negated components (a peak of -1), as in the fit files,
        because the decomposition negates the fit again.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    response = -component.

    ---- Helpers ----
    None.
    """

    count = result['components'].shape[1]
    names = list(names) if names else [f'PC{i + 1}' for i in range(count)]
    columns = {}
    for i, name in enumerate(names):
        columns[name] = result['wavelengths']
        columns[f'Unnamed: {2 * i + 1}'] = -result['components'][:, i]
    return {'haem_list': names, 'data': pd.DataFrame(columns)}
