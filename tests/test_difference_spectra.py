"""
Tests of the difference spectrum of a file (reduced minus oxidised), its decomposition into the haems, its figure and its switch under the boxes, the haem bands of a fit, and the mean and the stacking of spectra for a waterfall, on made-up spectra worked out by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.difference_spectra import (difference_decomposer,
                                             difference_figure_drawer,
                                             difference_spectrum_builder,
                                             haem_bands_drawer,
                                             haem_bands_finder,
                                             spectra_averager,
                                             spectra_stacker,
                                             WAVELENGTH_FIGURE_MARK,
                                             )
from utils_shared.figure_layout import BACKDROP_MARK
from utils_shared.spectral_decomposer import fit_importer
from utils_viewer.viewer_preview import time_axis_finder
from utils_viewer.viewer_strip import strip_values_builder, strip_values_checker


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FIT_FILE = ROOT / 'tests' / 'synthetic_test_fit.csv'
HAEM_FACTOR = 1000000.0  # the scale the program gives the fit shapes
# The haems of the test fit in the order the program reads them (a, then b, then c).
FIT_ORDER = ['Cyt a605', 'Cyt b557', 'Cyt bH', 'Cyt bL', 'Cyt cc']
# How much more of each haem is reduced in the reduced region than in the oxidised one,
# in FIT_ORDER: with the test fit (peaks of 1e-5) haem signals of 1 to 5 mOD.
AMOUNTS = np.array([1.0, 2.0, 3.0, 4.0, 5.0]) * 1e-4
# The background of the difference (OD): a flat part and a sloping part.
OFFSET = 0.001
SLOPE = 0.002
# How closely the decomposition must give back what the difference was built from.
EXACT = 1e-9
# The three small spectra worked out by hand (OD), at 500, 550 and 600 nm: three in the
# oxidised region (0 to 1 min), one between the regions that must be left out, three in
# the reduced region (3 to 4 min).
WAVELENGTHS_NM = np.array([500.0, 550.0, 600.0])
TIMES_MIN = np.array([0.0, 0.5, 1.0, 2.0, 3.0, 3.5, 4.0])
ATTENUATION_OD = np.array([[0.400, 0.500, 0.600],
                           [0.410, 0.510, 0.610],
                           [0.420, 0.520, 0.620],
                           [9.000, 9.000, 9.000],
                           [0.412, 0.515, 0.610],
                           [0.414, 0.517, 0.612],
                           [0.416, 0.519, 0.614],
                           ],
                          )
# mean oxidised = (0.41, 0.51, 0.61), mean reduced = (0.414, 0.517, 0.612), so the
# difference is (0.004, 0.007, 0.002) OD = (4, 7, 2) mOD
EXPECTED_MOD = np.array([4.0, 7.0, 2.0])


# ---- TEST HELPERS --------------------------------------------------------------------


# ---- _background_builder -------------------------------------------------------------
def _background_builder(wavelengths: np.ndarray) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to build the sloping background shape: it falls with wavelength
    from 1 at the shortest to 0 at the longest, as test_haem_decomposition's does.

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


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(wavelengths: np.ndarray,
                      times: np.ndarray,
                      spectra: np.ndarray,
                      has_levels: bool = True,
                      ) -> dict:
    """
    ---- Summary ----
    Helper function to make a processed file holding only what the difference spectrum
    reads: its Cyt spectra and, unless told not to, its two regions (oxidised 0 to 1
    min, reduced 3 to 4 min).

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths (nm), shape (n_wavelengths).
    times : np.ndarray
        Time of each spectrum (min), shape (n_spectra).
    spectra : np.ndarray
        Attenuation (OD), shape (n_spectra, n_wavelengths).
    has_levels : bool
        False for a file without both regions (no haem_levels).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The experiment (DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    experiment = {'experiment_name': 'made_up',
                  'raw_spectra': {'Cyt': {'wavelengths': wavelengths,
                                          'time': times,
                                          'attenuation': spectra,
                                          },
                                  },
                  }
    if has_levels:
        experiment['haem_levels'] = {'oxidised': {},
                                     'reduced': {},
                                     'oxidised_region': (0.0, 1.0),
                                     'reduced_region': (3.0, 4.0),
                                     }
    return experiment


# ---- _haem_experiment_maker ----------------------------------------------------------
def _haem_experiment_maker() -> tuple:
    """
    ---- Summary ----
    Helper function to make a file on the wavelengths of the test fit whose reduced
    spectra are its oxidised spectra plus known amounts of the five haems and a
    background.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, FIT_ORDER, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE.

    ---- Outputs ----
    tuple
        (the experiment, the haem shapes as columns in FIT_ORDER).

    ---- Globals mutated ----
    None. Reads the fit file (side effect).

    ---- Equations ----
    oxidised = 0.4 + 0.05 x background; reduced = oxidised + sum(amount_i x shape_i)
    x HAEM_FACTOR + OFFSET + SLOPE x background.

    ---- Helpers ----
    _background_builder
    _experiment_maker
    """

    table = pd.read_csv(FIT_FILE)
    wavelengths = table.iloc[:, 0].to_numpy(dtype=float)
    shapes = table[[f'{name} response' for name in FIT_ORDER]].to_numpy(dtype=float)
    slope = _background_builder(wavelengths)
    oxidised = 0.4 + 0.05 * slope
    reduced = oxidised + (shapes @ AMOUNTS) * HAEM_FACTOR + OFFSET + SLOPE * slope
    spectra = np.vstack([oxidised, oxidised, reduced, reduced])
    times = np.array([0.0, 1.0, 3.0, 4.0])
    return _experiment_maker(wavelengths, times, spectra), shapes


# ---- TESTS ---------------------------------------------------------------------------


# ---- test_mean_difference ------------------------------------------------------------
def test_mean_difference() -> None:
    """
    ---- Summary ----
    Main function to check that the difference spectrum is the mean of the three
    reduced spectra minus the mean of the three oxidised ones, in mOD, leaving out the
    spectrum between the regions.

    ---- Inputs ----
    None.

    ---- Globals read ----
    WAVELENGTHS_NM, TIMES_MIN, ATTENUATION_OD, EXPECTED_MOD.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    (0.414 - 0.41, 0.517 - 0.51, 0.612 - 0.61) x 1000 = (4, 7, 2) mOD.

    ---- Helpers ----
    _experiment_maker
    """

    experiment = _experiment_maker(WAVELENGTHS_NM, TIMES_MIN, ATTENUATION_OD)
    difference = difference_spectrum_builder(experiment, 'Cyt')
    assert np.allclose(difference['difference_mOD'], EXPECTED_MOD, rtol=0, atol=1e-9)
    assert np.array_equal(difference['wavelengths_nm'], WAVELENGTHS_NM)
    assert difference['n_oxidised'] == 3
    assert difference['n_reduced'] == 3
    assert difference['oxidised_region'] == (0.0, 1.0)
    assert difference['reduced_region'] == (3.0, 4.0)


# ---- test_known_haems_come_back ------------------------------------------------------
def test_known_haems_come_back() -> None:
    """
    ---- Summary ----
    Main function to check that a difference built from known haem amounts on a
    background is decomposed into those amounts, each haem's line being its amount
    times its shape, with a residual of about 0.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, FIT_ORDER, HAEM_FACTOR, AMOUNTS, EXACT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    haem_i (mOD) = amount_i x shape_i x HAEM_FACTOR x 1000.

    ---- Helpers ----
    _haem_experiment_maker
    """

    experiment, shapes = _haem_experiment_maker()
    fit = fit_importer(FIT_FILE)
    assert fit['haem_list'] == FIT_ORDER
    difference = difference_spectrum_builder(experiment, 'Cyt')
    found = difference_decomposer(difference, fit, 'scatter_1', HAEM_FACTOR)
    assert list(found['haems_mOD']) == FIT_ORDER
    amounts = np.array([found['amounts'][name] for name in FIT_ORDER])
    assert np.allclose(amounts, AMOUNTS, rtol=EXACT, atol=0.0)
    for i, name in enumerate(FIT_ORDER):
        assert np.allclose(found['haems_mOD'][name],
                           AMOUNTS[i] * shapes[:, i] * HAEM_FACTOR * 1000.0,
                           rtol=0,
                           atol=1e-9,
                           )
    assert np.max(np.abs(found['residual_mOD'])) < 1e-9
    assert np.allclose(found['fit_mOD'], found['measured_mOD'], rtol=0, atol=1e-9)


# ---- test_no_regions_no_difference ---------------------------------------------------
def test_no_regions_no_difference() -> None:
    """
    ---- Summary ----
    Main function to check that a file without both regions has no difference
    spectrum, and that a file without the spectrometer asked for is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    WAVELENGTHS_NM, TIMES_MIN, ATTENUATION_OD.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _experiment_maker
    """

    without = _experiment_maker(WAVELENGTHS_NM, TIMES_MIN, ATTENUATION_OD, False)
    assert difference_spectrum_builder(without, 'Cyt') is None
    with_regions = _experiment_maker(WAVELENGTHS_NM, TIMES_MIN, ATTENUATION_OD)
    with pytest.raises(ValueError, match='no NADH spectra'):
        difference_spectrum_builder(with_regions, 'NADH')


# ---- test_figure_panels --------------------------------------------------------------
def test_figure_panels() -> None:
    """
    ---- Summary ----
    Main function to check the figure, drawn off screen: two panels, one line for each
    haem in its colour, the regions' times in the key, and no time axis for the window.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, FIT_ORDER, HAEM_FACTOR, settings.COMPONENT_FIGURE_STYLE.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_experiment_maker
    """

    experiment, _ = _haem_experiment_maker()
    fit = fit_importer(FIT_FILE)
    difference = difference_spectrum_builder(experiment, 'Cyt')
    found = difference_decomposer(difference, fit, 'scatter_1', HAEM_FACTOR)
    colours = settings.haem_colour_mapper(FIT_ORDER)
    fig = Figure()
    axes = difference_figure_drawer(fig,
                                    difference,
                                    found,
                                    colours,
                                    settings.COMPONENT_FIGURE_STYLE,
                                    )
    assert len(fig.axes) == 2
    assert axes[0] is fig.axes[0]
    labels = [line.get_label() for line in axes[0].lines]
    for name in FIT_ORDER:
        assert labels.count(name) == 1
        line = axes[0].lines[labels.index(name)]
        assert line.get_color() == colours[name]
    assert 'Measured' in labels
    assert 'Background' in labels
    assert axes[1].get_xlabel() == 'Wavelength (nm)'
    title = axes[0].get_legend().get_title().get_text()
    assert '3.0–4.0 min' in title
    assert '0.0–1.0 min' in title
    assert getattr(fig, WAVELENGTH_FIGURE_MARK)
    assert time_axis_finder(fig) is None


# ---- test_strip_switch_value ---------------------------------------------------------
def test_strip_switch_value() -> None:
    """
    ---- Summary ----
    Main function to check the switch's value in the strip: the standard plot unless
    the answers ask for the difference spectrum, and only True or False accepted.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    standard = dict(settings.DEFAULT_ANSWERS)
    assert standard['difference_spectra'] is False
    assert strip_values_builder(standard, True, [])['difference_spectra'] is False
    values = strip_values_builder(dict(standard, difference_spectra=True), True, [])
    assert values['difference_spectra'] is True
    strip_values_checker(values)
    strip_values_checker({'difference_spectra': False})
    for wrong in ('yes', 1, None):
        with pytest.raises(ValueError, match='difference spectrum'):
            strip_values_checker({'difference_spectra': wrong})


# ---- test_the_haem_bands -------------------------------------------------------------
def test_the_haem_bands() -> None:
    """
    ---- Summary ----
    Main function to check the band of each haem of a made-up fit, worked out by
    hand: 2.5 nm each side of where its shape is strongest, whichever its sign; a
    shorter haem read to its own end; none for a haem of only zeros; and the bands
    as drawn: in the colour of the haem, marked as a backdrop, the x range kept.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Haem A is 0, -3, 1, 0 at 540, 550, 560, 570 nm: strongest (3) at 550, so its
    band is 547.5 to 552.5 nm. Haem B is 1, 2 at 600, 605 nm and then empty:
    strongest at 605, band 602.5 to 607.5 nm; with 1 nm each side, 604 to 606 nm.

    ---- Helpers ----
    None.
    """

    table = pd.DataFrame({'A': [540.0, 550.0, 560.0, 570.0],
                          'A response': [0.0, -3.0, 1.0, 0.0],
                          'B': [600.0, 605.0, np.nan, np.nan],
                          'B response': [1.0, 2.0, np.nan, np.nan],
                          'C': [540.0, 550.0, 560.0, 570.0],
                          'C response': [0.0, 0.0, 0.0, 0.0],
                          },
                         )
    fit = {'haem_list': ['A', 'B', 'C'], 'data': table}
    bands = haem_bands_finder(fit)
    assert bands == {'A': (547.5, 552.5), 'B': (602.5, 607.5)}
    assert haem_bands_finder(fit, 1.0)['B'] == (604.0, 606.0)
    ax = Figure().add_subplot()
    ax.set_xlim(500.0, 580.0)
    haem_bands_drawer(ax, bands, {'A': '#00b050'})
    assert [(band.get_x(), band.get_x() + band.get_width())
            for band in ax.patches
            ] == [(547.5, 552.5), (602.5, 607.5)]
    assert all(getattr(band, BACKDROP_MARK) for band in ax.patches)
    assert ax.patches[0].get_facecolor()[:3] == pytest.approx(
        (0.0, 176 / 255, 80 / 255),
        )
    assert ax.get_xlim() == (500.0, 580.0)


# ---- test_spectra_averaged_and_stacked -----------------------------------------------
def test_spectra_averaged_and_stacked() -> None:
    """
    ---- Summary ----
    Main function to check, by hand, the mean of spectra on different wavelengths
    and the stacking of a waterfall: lined up on the highest point inside a band,
    or anywhere without one, and spread 0.75 of the tallest spectrum apart.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The mean: 1, 2, 3 at 500, 510, 520 nm and 0, 2, 4 at 495, 505, 515 nm. The
    second read at 500 nm is 0 + (2 - 0) x 5 / 10 = 1, at 510 nm 3, and it does not
    reach 520 nm: mean (1 + 1) / 2 = 1, (2 + 3) / 2 = 2.5, and 3 alone.
    The stack, at 540, 550, 560, 570 nm: 1, 5, 2, 9 and 0, 2, 4, 1, with the band
    545 to 565 nm. The first has 5 as its highest point in the band: -4, 0, -3, 4,
    8 high; the second 4: -4, -2, 0, -3, 4 high. The gap is 0.75 x 8 = 6, so the
    first is drawn at 2, 6, 3, 10 and the second stays. Without a band the first is
    lined up on 9: -8, -4, -7, 0, drawn at -2, 2, -1, 6.

    ---- Helpers ----
    None.
    """

    wavelengths, mean = spectra_averager([(np.array([500.0, 510.0, 520.0]),
                                           np.array([1.0, 2.0, 3.0]),
                                           ),
                                          (np.array([495.0, 505.0, 515.0]),
                                           np.array([0.0, 2.0, 4.0]),
                                           ),
                                          ],
                                         )
    assert list(wavelengths) == [500.0, 510.0, 520.0]
    assert list(mean) == pytest.approx([1.0, 2.5, 3.0])
    with pytest.raises(ValueError, match='no spectrum'):
        spectra_averager([])
    grid = np.array([540.0, 550.0, 560.0, 570.0])
    spectra = [(grid, np.array([1.0, 5.0, 2.0, 9.0])),
               (grid, np.array([0.0, 2.0, 4.0, 1.0])),
               ]
    first, second = spectra_stacker(spectra, (545.0, 565.0))
    assert list(first) == [2.0, 6.0, 3.0, 10.0]
    assert list(second) == [-4.0, -2.0, 0.0, -3.0]
    first, second = spectra_stacker(spectra)
    assert list(first) == [-2.0, 2.0, -1.0, 6.0]
    assert list(second) == [-4.0, -2.0, 0.0, -3.0]
    # a band no spectrum reaches lines each up on its highest point anywhere
    assert list(spectra_stacker(spectra, (700.0, 710.0))[0]) == [-2.0, 2.0, -1.0, 6.0]
