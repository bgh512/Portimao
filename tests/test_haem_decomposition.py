"""
Tests that the haem decomposition gives back the amounts a spectrum was built from, and
that the component finder gives back the shapes its spectra were mixed from.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.pca_fitter import (component_builder,
                                     component_count_suggester,
                                     component_finder,
                                     decomposition_example_finder,
                                     )
from utils_shared.schema import TIME_COLUMN
from utils_shared.spectral_decomposer import (experiment_decomposer,
                                              fit_importer,
                                              spectrum_decomposer,
                                              )


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FIT_FILE = ROOT / 'fits' / 'synthetic_test_fit.csv'
HAEM_FACTOR = 1000000.0  # the scale the program gives the fit shapes
# Amounts of the five haems, in file order. With the test fit (peaks of 1e-5) they give
# haem signals of 1 to 5 mOD, as in a real run; far smaller signals would be lost in
# the rounding of the 0.4 OD background itself, whatever the maths.
AMOUNTS = np.array([1.0, 2.0, 3.0, 4.0, 5.0]) * 1e-4
OFFSET = 0.4  # a flat background under the haems (OD)
SLOPE = 0.05  # size of the scatter background (OD)
SEED = 0  # the one random seed, for the noise and amounts of the mixed spectra
PEAKS_NM = (550.0, 605.0)  # where the two mixed shapes have their peaks
WIDTHS_NM = (8.0, 10.0)
# How closely the decomposition must give back what a made-up spectrum was built from:
# 9 digits. Never loosen it: a decomposition that is less exact has gone wrong.
EXACT = 1e-9


# ---- HELPERS -------------------------------------------------------------------------


# ---- _background_builder -------------------------------------------------------------
def _background_builder(wavelengths: np.ndarray) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to build the scatter background shape: it falls with wavelength
    from 1 at the shortest to 0 at the longest.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths (nm), shape (n_wavelengths).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The shape, shape (n_wavelengths).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    (1/wl - min(1/wl)) / (max(1/wl) - min(1/wl)).

    ---- Helpers ----
    None.
    """

    inverse = 1.0 / wavelengths
    return (inverse - inverse.min()) / (inverse.max() - inverse.min())


# ---- _haem_spectrum_builder ----------------------------------------------------------
def _haem_spectrum_builder() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Helper function to build one spectrum from known amounts of the five haems of the
    test fit file, on a flat and a sloping background.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (wavelengths in nm, the spectrum, the haem shapes as columns); the wavelengths
        are those of the fit file.

    ---- Globals mutated ----
    None. Reads the fit file (side effect).

    ---- Equations ----
    spectrum = -sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x background.
    The minus sign is the program's: its attenuation is log10(T).

    ---- Helpers ----
    _background_builder
    """

    table = pd.read_csv(FIT_FILE)
    wavelengths = table.iloc[:, 0].to_numpy(dtype=float)
    for column in range(0, table.shape[1], 2):  # every haem is on the same wavelengths
        assert np.array_equal(table.iloc[:, column].to_numpy(dtype=float), wavelengths)
    shapes = table.iloc[:, 1::2].to_numpy(dtype=float)
    spectrum = (-(shapes @ AMOUNTS) * HAEM_FACTOR
                + OFFSET
                + SLOPE * _background_builder(wavelengths)
                )
    return wavelengths, spectrum, shapes


# ---- _mixed_spectra_builder ----------------------------------------------------------
def _mixed_spectra_builder() -> Tuple[np.ndarray, np.ndarray, list]:
    """
    ---- Summary ----
    Helper function to build two files of 20 spectra each, every spectrum mixed from
    the same two shapes in its own amounts, on its own flat and sloping background,
    with a little noise. The second file also has a fixed extra bump in every spectrum,
    as a different preparation would.

    ---- Inputs ----
    None.

    ---- Globals read ----
    SEED, PEAKS_NM, WIDTHS_NM (module constants).

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, list]
        (wavelengths 500 to 650 nm in 1 nm steps, the two shapes as columns, the two
        files as the component finder takes them).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    shape = exp(-0.5 ((wl - peak) / width)^2); spectrum = a x shape_1 + b x shape_2 +
    offset + slope x background + noise (SD 0.0001), a and b between 0 and 1.

    ---- Helpers ----
    _background_builder
    """

    rng = np.random.default_rng(SEED)
    wavelengths = np.arange(500.0, 651.0)
    shapes = np.column_stack([np.exp(-0.5 * ((wavelengths - peak) / width) ** 2)
                              for peak, width in zip(PEAKS_NM, WIDTHS_NM)
                              ],
                             )
    background = _background_builder(wavelengths)
    bump = 0.5 * np.exp(-0.5 * ((wavelengths - 520.0) / 6.0) ** 2)
    files = []
    for number in range(2):
        amounts = rng.uniform(0.0, 1.0, size=(20, 2))
        spectra = (amounts @ shapes.T
                   + rng.uniform(0.0, 0.5, size=(20, 1))
                   + rng.uniform(0.0, 0.2, size=(20, 1)) * background[None, :]
                   + rng.normal(0.0, 1e-4, size=(20, len(wavelengths)))
                   + number * bump[None, :]
                   )
        files.append({'name': f'file {number + 1}',
                      'wavelengths': wavelengths,
                      'spectra': spectra,
                      },
                     )
    return wavelengths, shapes, files


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_one_spectrum_gives_its_amounts_back ----------------------------------------
def test_one_spectrum_gives_its_amounts_back() -> None:
    """
    ---- Summary ----
    Main function to check that a spectrum built from known amounts of each haem and a
    known background decomposes into those amounts and that background, with nothing
    left over.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See _haem_spectrum_builder: the amounts found must be AMOUNTS, then OFFSET, then
    SLOPE.

    ---- Helpers ----
    _haem_spectrum_builder
    """

    wavelengths, spectrum, _ = _haem_spectrum_builder()
    fit = fit_importer(FIT_FILE)
    assert len(fit['haem_list']) == len(AMOUNTS)
    found, _, scatter, _, haems, single, residual = spectrum_decomposer(
        np.column_stack((wavelengths, spectrum)),
        fit['data'],
        degree_of_scatter=1,
        haemfactor=HAEM_FACTOR,
        )
    assert np.allclose(found[:5], AMOUNTS, rtol=EXACT, atol=0.0)
    assert np.isclose(found[5], OFFSET, rtol=EXACT)
    assert np.isclose(found[6], SLOPE, rtol=EXACT)
    assert np.abs(residual[:, 1]).max() < 1e-9
    assert np.allclose(haems[:, 1] + scatter[:, 1], spectrum, atol=1e-9)
    assert len(single) == len(AMOUNTS)


# ---- test_a_series_gives_its_amounts_back --------------------------------------------
def test_a_series_gives_its_amounts_back() -> None:
    """
    ---- Summary ----
    Main function to check that a run of four spectra holding 1, 4, 3 and 2 times the
    known amounts decomposes into those amounts, and that the haem absorbances and
    their change from the highest point follow from them.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants); TIME_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    amount of haem i in a spectrum = its multiple x AMOUNTS_i; absorbance (mOD) =
    amount x highest point of |shape_i| x HAEM_FACTOR x 1000; change = absorbance - the
    highest absorbance of that haem (the second spectrum), so it is 0 there and
    negative elsewhere. The highest point is looked for in 30 s windows that must end
    before the run does, so the last spectrum can never be it.

    ---- Helpers ----
    _background_builder
    _haem_spectrum_builder
    """

    wavelengths, _, shapes = _haem_spectrum_builder()
    scale = np.array([1.0, 4.0, 3.0, 2.0])
    spectra = (-np.outer(scale, shapes @ AMOUNTS) * HAEM_FACTOR
               + OFFSET
               + SLOPE * _background_builder(wavelengths)[None, :]
               )
    experiment = {'experiment_name': 'series',
                  'raw_spectra': {'Cyt': {'wavelengths': wavelengths,
                                          'spectrum_indices': np.arange(1, 5),
                                          'time': np.arange(4, dtype=float),
                                          'attenuation': spectra,
                                          },
                                  },
                  }
    fit = fit_importer(FIT_FILE)
    experiment_decomposer(experiment,
                          fit,
                          haemfactor=HAEM_FACTOR,
                          delta_exclude_first_minutes=0.0,
                          )
    names = list(fit['haem_list'])
    expected = np.outer(scale, AMOUNTS)
    amounts = experiment['haem_conc']
    assert np.allclose(amounts[names].to_numpy(), expected, rtol=EXACT, atol=0.0)
    assert np.allclose(amounts[TIME_COLUMN], [0.0, 1.0, 2.0, 3.0])
    heights = np.abs(shapes).max(axis=0) * HAEM_FACTOR
    absorbances = expected * heights[None, :] * 1000.0
    assert np.allclose(experiment['haem_abs'][names].to_numpy(),
                       absorbances,
                       rtol=EXACT,
                       atol=0.0,
                       )
    assert np.allclose(experiment['haem_delta_abs'][names].to_numpy(),
                       absorbances - absorbances[1][None, :],
                       rtol=EXACT,
                       atol=EXACT * absorbances.max(),
                       )


# ---- test_the_three_routes_give_the_same_amounts -------------------------------------
def test_the_three_routes_give_the_same_amounts() -> None:
    """
    ---- Summary ----
    Main function to check that the three places that decompose a spectrum (one
    spectrum, a whole run, the component finder's examples) give the same amounts for
    the same spectrum, and that these are the amounts it was built from. It guards the
    one shared solver: never loosen it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See _haem_spectrum_builder. The component finder gives each shape's part of the
    spectrum (amount x shape), so its amount is the best fit of that part to the shape:
    sum(part x shape) / sum(shape^2).

    ---- Helpers ----
    _haem_spectrum_builder
    """

    wavelengths, spectrum, shapes = _haem_spectrum_builder()
    fit = fit_importer(FIT_FILE)
    names = list(fit['haem_list'])
    one = spectrum_decomposer(np.column_stack((wavelengths, spectrum)),
                              fit['data'],
                              degree_of_scatter=1,
                              haemfactor=HAEM_FACTOR,
                              )[0][:len(AMOUNTS)]
    experiment = {'experiment_name': 'twice',
                  'raw_spectra': {'Cyt': {'wavelengths': wavelengths,
                                          'spectrum_indices': np.arange(1, 3),
                                          'time': np.arange(2, dtype=float),
                                          'attenuation': np.vstack((spectrum, spectrum),
                                                                   ),
                                          },
                                  },
                  }
    experiment_decomposer(experiment,
                          fit,
                          haemfactor=HAEM_FACTOR,
                          delta_exclude_first_minutes=0.0,
                          )
    run = experiment['haem_conc'][names].to_numpy()[0]
    components = -shapes * HAEM_FACTOR
    example = decomposition_example_finder([{'name': 'made up',
                                             'wavelengths': wavelengths,
                                             'spectra': spectrum[None, :],
                                             },
                                            ],
                                           {'wavelengths': wavelengths,
                                            'components': components,
                                            },
                                           degree_of_scatter=1,
                                           )['best']
    finder = ((example['contributions'] * components).sum(axis=0)
              / (components ** 2).sum(axis=0))
    for found in (one, run, finder):
        assert np.allclose(found, AMOUNTS, rtol=EXACT, atol=0.0)
    assert np.allclose(run, one, rtol=EXACT, atol=0.0)
    assert np.allclose(finder, one, rtol=EXACT, atol=0.0)


# ---- test_same_shapes_give_a_plain_error ---------------------------------------------
def test_same_shapes_give_a_plain_error() -> None:
    """
    ---- Summary ----
    Main function to check that a fit file in which two haems have the same shape is
    refused with a message that says so, and not with the raw "Singular matrix".

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_spectrum_builder
    """

    wavelengths, spectrum, _ = _haem_spectrum_builder()
    table = fit_importer(FIT_FILE)['data'].copy()
    table.iloc[:, 3] = table.iloc[:, 1]  # the second haem gets the shape of the first
    with pytest.raises(ValueError, match='cannot be told apart'):
        spectrum_decomposer(np.column_stack((wavelengths, spectrum)),
                            table,
                            degree_of_scatter=1,
                            haemfactor=HAEM_FACTOR,
                            )


# ---- test_a_failed_decomposition_leaves_nothing --------------------------------------
def test_a_failed_decomposition_leaves_nothing() -> None:
    """
    ---- Summary ----
    Main function to check that a decomposition that fails at its last step (the whole
    run is ignored, so the zero of the change cannot be found) leaves no haem amounts,
    absorbances or changes in the experiment, not even those of an earlier
    decomposition.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The run lasts 1 min and its first 10 min are ignored, so nothing is left.

    ---- Helpers ----
    _haem_spectrum_builder
    """

    wavelengths, spectrum, _ = _haem_spectrum_builder()
    experiment = {'experiment_name': 'all ignored',
                  'raw_spectra': {'Cyt': {'wavelengths': wavelengths,
                                          'spectrum_indices': np.arange(1, 3),
                                          'time': np.arange(2, dtype=float),
                                          'attenuation': np.vstack((spectrum, spectrum),
                                                                   ),
                                          },
                                  },
                  'haem_conc': 'from an earlier decomposition',
                  }
    with pytest.raises(ValueError, match='Ignore less'):
        experiment_decomposer(experiment,
                              fit_importer(FIT_FILE),
                              haemfactor=HAEM_FACTOR,
                              delta_exclude_first_minutes=10.0,
                              )
    for key in ('haem_conc', 'haem_abs', 'haem_delta_abs'):
        assert key not in experiment


# ---- test_two_mixed_shapes_give_two_components ---------------------------------------
def test_two_mixed_shapes_give_two_components() -> None:
    """
    ---- Summary ----
    Main function to check that spectra mixed from two shapes give two components and
    no more: the third is only noise, two is the number suggested, and a fixed bump in
    one file does not become a component.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The noise (SD 0.0001) is about a thousandth of the changes of the shapes, so the
    third component must hold less than a ten-thousandth of the variance of the second.

    ---- Helpers ----
    _mixed_spectra_builder
    """

    _, _, files = _mixed_spectra_builder()
    analysis = component_finder(files, (500.0, 650.0))
    assert analysis['n_spectra'] == 40
    assert analysis['counts'] == {'file 1': 20, 'file 2': 20}
    values = analysis['eigenvalues']
    assert values[1] > 0
    assert values[2] / values[1] < 1e-4
    assert component_count_suggester(analysis) == 2
    result = component_builder(analysis, 2)
    assert np.sum(result['explained']) > 0.9999
    assert result['residual_rms'] < 2e-4


# ---- test_the_two_shapes_are_found_again ---------------------------------------------
def test_the_two_shapes_are_found_again() -> None:
    """
    ---- Summary ----
    Main function to check that the two components found are the two shapes the
    spectra were mixed from: each shape can be rebuilt from the components (once its
    own flat and sloping part is taken off, as the finder does), and the components
    have their peaks where the shapes have theirs.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PEAKS_NM (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    cleaned shape = shape - its best fit of (1, background); left over = cleaned shape
    - its best fit of the two components; the left over must be under 1 % of the
    cleaned shape (root of the summed squares).

    ---- Helpers ----
    _background_builder
    _mixed_spectra_builder
    """

    wavelengths, shapes, files = _mixed_spectra_builder()
    analysis = component_finder(files, (500.0, 650.0))
    nuisance = np.column_stack((np.ones_like(wavelengths),
                                _background_builder(wavelengths),
                                ),
                               )
    cleaned = shapes - nuisance @ np.linalg.lstsq(nuisance, shapes, rcond=None)[0]
    vectors = analysis['eigenvectors'][:, :2]
    left_over = cleaned - vectors @ np.linalg.lstsq(vectors, cleaned, rcond=None)[0]
    for column in range(2):
        assert (np.linalg.norm(left_over[:, column])
                < 0.01 * np.linalg.norm(cleaned[:, column]))
    result = component_builder(analysis, 2)
    assert np.allclose(np.abs(result['components']).max(axis=0), 1.0)
    assert np.allclose(sorted(result['peaks']), PEAKS_NM, atol=2.0)
