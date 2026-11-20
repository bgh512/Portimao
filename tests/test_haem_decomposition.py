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
                                     fit_table_builder,
                                     )
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN
from utils_shared.spectral_decomposer import (delta_abs_calculator,
                                              experiment_decomposer,
                                              fit_importer,
                                              spectrum_decomposer,
                                              )


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FIT_FILE = ROOT / 'tests' / 'synthetic_test_fit.csv'
FITS_FOLDER = ROOT / 'fits'  # the fit files users choose from
# Last wavelength (nm, as the note writes it) kept of each haem that ends in leftover
# rows, in the three fit files that have them.
LEFTOVER_ROWS = {'bswitch_no2_mycobl.csv': ('628.38', '630.05', '639.99'),
                 'bswitch_no2_mycobl_b557.csv': ('628.38', '630.05', '639.99'),
                 'bswitch_no2_mycobl_b557_cc.csv': ('628.38', '630.05', '639.99'),
                 }
MILLION_FITS = ('OGfit.csv', 'temp_fit_037v.csv')  # written a million times larger
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
    spectrum = sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x background.

    ---- Helpers ----
    _background_builder
    """

    table = pd.read_csv(FIT_FILE)
    wavelengths = table.iloc[:, 0].to_numpy(dtype=float)
    for column in range(0, table.shape[1], 2):  # every haem is on the same wavelengths
        assert np.array_equal(table.iloc[:, column].to_numpy(dtype=float), wavelengths)
    shapes = table.iloc[:, 1::2].to_numpy(dtype=float)
    spectrum = ((shapes @ AMOUNTS) * HAEM_FACTOR
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


# ---- _series_decomposer --------------------------------------------------------------
def _series_decomposer(fit: dict) -> dict:
    """
    ---- Summary ----
    Helper function to decompose, with a given fit, a run of four spectra holding 1, 4,
    3 and 2 times the known amounts of the five haems of the test fit file.

    ---- Inputs ----
    fit : dict
        Fit dictionary from fit_importer, holding the five haems of the test fit file.

    ---- Globals read ----
    HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

    ---- Outputs ----
    dict
        The experiment, with its haem amounts, absorbances and changes.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    spectrum k = multiple_k x sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x
    background.

    ---- Helpers ----
    _background_builder
    _haem_spectrum_builder
    """

    wavelengths, _, shapes = _haem_spectrum_builder()
    spectra = (np.outer([1.0, 4.0, 3.0, 2.0], shapes @ AMOUNTS) * HAEM_FACTOR
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
    return experiment_decomposer(experiment,
                                 fit,
                                 dataset_name='Cyt',
                                 degree_of_scatter=1,
                                 haemfactor=HAEM_FACTOR,
                                 delta_exclude_first_minutes=0.0,
                                 delta_window_points=1,
                                 )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_blank_rows_do_not_change_the_shapes ----------------------------------------
def test_blank_rows_do_not_change_the_shapes(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file whose haems have different lengths is read
    the same wherever the blank rows of the shorter haem are: at the bottom, or between
    its numbers.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes two small fit files in tmp_path (side effect).

    ---- Equations ----
    Haem a has five rows (500 to 540 nm); haem b has three (505, 515, 525 nm; 4e-5,
    5e-5, 6e-5). Both files must give b as those three rows at the top, with two
    blank rows below.

    ---- Helpers ----
    None.
    """

    bottom = tmp_path / 'bottom.csv'
    bottom.write_text('a,,b,\n'
                      '500,1e-5,505,4e-5\n'
                      '510,2e-5,515,5e-5\n'
                      '520,3e-5,525,6e-5\n'
                      '530,2e-5,,\n'
                      '540,1e-5,,\n',
                      )
    between = tmp_path / 'between.csv'
    between.write_text('a,,b,\n'
                       '500,1e-5,505,4e-5\n'
                       '510,2e-5,,\n'
                       '520,3e-5,515,5e-5\n'
                       '530,2e-5,,\n'
                       '540,1e-5,525,6e-5\n',
                       )
    expected = np.array([[500.0, 1e-5, 505.0, 4e-5],
                         [510.0, 2e-5, 515.0, 5e-5],
                         [520.0, 3e-5, 525.0, 6e-5],
                         [530.0, 2e-5, np.nan, np.nan],
                         [540.0, 1e-5, np.nan, np.nan],
                         ],
                        )
    for path in (bottom, between):
        fit = fit_importer(path)
        assert fit['haem_list'] == ['a', 'b']
        assert np.array_equal(fit['data'].to_numpy(), expected, equal_nan=True)
        assert fit['notes'] == []
        assert fit['scale_divisor'] == 1.0


# ---- test_leftover_rows_are_left_out -------------------------------------------------
def test_leftover_rows_are_left_out(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a haem whose column ends in leftover rows (rows of
    another haem, whose wavelengths jump backwards) gives the same amounts as the same
    haem ending in blanks, that these are the amounts the spectrum was built from, and
    that the user is told which rows were left out.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes two fit files in tmp_path (side effect).

    ---- Equations ----
    The second haem of the test fit (400 to 700 nm in 1 nm steps) is ended at 650 nm
    (row 251). In one file the 50 rows below are blank; in the other they hold the
    last haem's rows of 420 to 469 nm, so the wavelength jumps from 650 back to 420.
    The haems then share 400 to 650 nm, where the spectrum still holds AMOUNTS.

    ---- Helpers ----
    _haem_spectrum_builder
    """

    wavelengths, spectrum, _ = _haem_spectrum_builder()
    table = pd.read_csv(FIT_FILE)
    blank = table.copy()
    blank.iloc[251:, 2:4] = np.nan
    leftover = table.copy()
    leftover.iloc[251:, 2] = table.iloc[20:70, 8].to_numpy()
    leftover.iloc[251:, 3] = table.iloc[20:70, 9].to_numpy()
    fits = {}
    for name, frame in (('blank', blank), ('leftover', leftover)):
        frame.to_csv(tmp_path / f'{name}.csv', index=False)
        fits[name] = fit_importer(tmp_path / f'{name}.csv')
    assert np.array_equal(fits['leftover']['data'].to_numpy(),
                          fits['blank']['data'].to_numpy(),
                          equal_nan=True,
                          )
    assert fits['blank']['notes'] == []
    assert len(fits['leftover']['notes']) == 1
    assert 'Cyt cc' in fits['leftover']['notes'][0]
    assert '650.00 nm' in fits['leftover']['notes'][0]
    found = spectrum_decomposer(np.column_stack((wavelengths, spectrum)),
                                fits['leftover']['data'],
                                degree_of_scatter=1,
                                haemfactor=HAEM_FACTOR,
                                )
    assert found[1][-1, 0] == 650.0  # the last wavelength the haems share
    assert np.allclose(found[0][:5], AMOUNTS, rtol=EXACT, atol=0.0)


# ---- test_downward_wavelengths_are_turned_round --------------------------------------
def test_downward_wavelengths_are_turned_round(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file written from the longest wavelength to the
    shortest is read as the same fit written the usual way.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    FIT_FILE (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    pd.read_csv(FIT_FILE).iloc[::-1].to_csv(tmp_path / 'downwards.csv', index=False)
    fit = fit_importer(tmp_path / 'downwards.csv')
    assert np.array_equal(fit['data'].to_numpy(),
                          fit_importer(FIT_FILE)['data'].to_numpy(),
                          )
    assert fit['notes'] == []


# ---- test_unusable_fit_files_are_refused ---------------------------------------------
@pytest.mark.parametrize(('text', 'message'),
                         [('a,x,b\n1,2,3\n2,3,4\n', 'two columns per haem'),
                          ('a,,,\n1,2,3,4\n2,3,4,5\n', 'no haem name'),
                          ('a,\n1,2\nx,3\n3,4\n', 'row 3 is not a number'),
                          ('a,\n1,2\n2,\n3,4\n', 'row 3 of a has a wavelength without'),
                          ('a,\n1,2\n', 'fewer than two rows'),
                          ('', 'could not be read'),
                          ],
                         )
def test_unusable_fit_files_are_refused(tmp_path: Path,
                                        text: str,
                                        message: str,
                                        ) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file that cannot give a shape is refused with a
    message that says what is wrong and where: columns not in pairs, a haem with no
    name, a cell that is not a number, a wavelength with no response, a haem of one
    row, and an empty file.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.
    text : str
        Contents of the fit file.
    message : str
        Words the message must hold.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    The first row of a file is its header, so the second row of numbers is row 3.

    ---- Helpers ----
    None.
    """

    path = tmp_path / 'unusable.csv'
    path.write_text(text)
    with pytest.raises(ValueError, match=message):
        fit_importer(path)


# ---- test_a_million_times_larger_fit_gives_the_same_amounts --------------------------
def test_a_million_times_larger_fit_gives_the_same_amounts(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that the same fit written a million times larger gives the
    same raw amounts, absorbances and changes, and says that it was divided; and that
    a fit on neither scale is used as it is, with a warning.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    FIT_FILE, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes two fit files in tmp_path (side effect).

    ---- Equations ----
    The shapes of the test fit have peaks of 1e-5 (the standard scale). Times 1e6 the
    peaks are 10: a million above the standard, so divided by 1e6. Times 1e3 they are
    0.01: on neither scale (the standard ends at 1e-3, the large one starts at 0.1).

    ---- Helpers ----
    _series_decomposer
    """

    table = pd.read_csv(FIT_FILE)
    for name, factor in (('million', 1e6), ('thousand', 1e3)):
        larger = table.copy()
        larger.iloc[:, 1::2] = table.iloc[:, 1::2] * factor
        larger.to_csv(tmp_path / f'{name}.csv', index=False)
    standard = fit_importer(FIT_FILE)
    assert standard['scale_divisor'] == 1.0
    assert standard['notes'] == []

    million = fit_importer(tmp_path / 'million.csv')
    assert million['scale_divisor'] == 1e6
    assert len(million['notes']) == 1
    assert 'divided by 1 000 000' in million['notes'][0]
    names = list(standard['haem_list'])
    expected = _series_decomposer(standard)
    found = _series_decomposer(million)
    for key in ('haem_conc', 'haem_abs', 'haem_delta_abs'):
        assert np.allclose(found[key][names].to_numpy(),
                           expected[key][names].to_numpy(),
                           rtol=EXACT,
                           atol=EXACT * np.abs(expected[key][names].to_numpy()).max(),
                           )

    thousand = fit_importer(tmp_path / 'thousand.csv')
    assert thousand['scale_divisor'] == 1.0
    assert len(thousand['notes']) == 1
    assert thousand['notes'][0].startswith('Warning')
    assert np.allclose(thousand['data'].iloc[:, 1::2].to_numpy(),
                       table.iloc[:, 1::2].to_numpy() * 1e3,
                       rtol=1e-12,
                       atol=0.0,
                       )


# ---- test_every_fit_file_is_read -----------------------------------------------------
def test_every_fit_file_is_read() -> None:
    """
    ---- Summary ----
    Main function to check that every fit file users can choose is read without an
    error, with wavelengths that go upwards in every haem, on the standard scale, and
    that the leftover rows of the three files that have them are left out and named.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FITS_FOLDER, LEFTOVER_ROWS, MILLION_FITS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Standard scale: the highest point of the shapes lies between 1e-7 and 1e-3.

    ---- Helpers ----
    None.
    """

    paths = sorted(FITS_FOLDER.glob('*.csv'))
    assert paths
    for path in paths:
        fit = fit_importer(path)
        data = fit['data']
        assert len(fit['haem_list']) == data.shape[1] // 2
        for i in range(len(fit['haem_list'])):
            pair = data.iloc[:, [2 * i, 2 * i + 1]].dropna().to_numpy()
            assert len(pair) >= 2
            assert np.all(np.diff(pair[:, 0]) >= 0)
        peak = np.nanmax(np.abs(data.iloc[:, 1::2].to_numpy()))
        assert 1e-7 <= peak <= 1e-3
        assert fit['scale_divisor'] == (1e6 if path.name in MILLION_FITS else 1.0)
        leftovers = [note for note in fit['notes'] if 'backwards' in note]
        ends = LEFTOVER_ROWS.get(path.name, ())
        assert len(leftovers) == len(ends)
        for note, end in zip(leftovers, ends):
            assert f'after {end} nm' in note


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
    negative elsewhere. The reference window is one spectrum here, as the run has only
    four.

    ---- Helpers ----
    _background_builder
    _haem_spectrum_builder
    """

    wavelengths, _, shapes = _haem_spectrum_builder()
    scale = np.array([1.0, 4.0, 3.0, 2.0])
    spectra = (np.outer(scale, shapes @ AMOUNTS) * HAEM_FACTOR
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
                          dataset_name='Cyt',
                          degree_of_scatter=1,
                          haemfactor=HAEM_FACTOR,
                          delta_exclude_first_minutes=0.0,
                          delta_window_points=1,
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
                          dataset_name='Cyt',
                          degree_of_scatter=1,
                          haemfactor=HAEM_FACTOR,
                          delta_exclude_first_minutes=0.0,
                          delta_window_points=1,
                          )
    run = experiment['haem_conc'][names].to_numpy()[0]
    components = shapes * HAEM_FACTOR
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
                              dataset_name='Cyt',
                              degree_of_scatter=1,
                              haemfactor=HAEM_FACTOR,
                              delta_exclude_first_minutes=10.0,
                              delta_window_points=50,
                              )
    for key in ('haem_conc', 'haem_abs', 'haem_delta_abs'):
        assert key not in experiment


# ---- test_delta_a_zero_is_the_median_of_the_highest_points ---------------------------
def test_delta_a_zero_is_the_median_of_the_highest_points() -> None:
    """
    ---- Summary ----
    Main function to check that the zero of delta A is the median of the highest points
    in a row, so that one spike does not set it, and that a run with fewer points than
    one window is refused in place of taking the zero from too few spectra.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Absorbances 1, 2, 9, 3, 4, 5, 0, 0 at 0 to 7 min, three points in a row. Medians
    of the six windows: 2, 3, 4, 4, 4, 0. The highest is 4, first reached by the
    window 9, 3, 4 (2 to 4 min), so delta A = absorbance - 4 and the spike of 9 is not
    the zero. A window of nine points does not fit in eight.

    ---- Helpers ----
    None.
    """

    values = np.array([1.0, 2.0, 9.0, 3.0, 4.0, 5.0, 0.0, 0.0])
    frame = pd.DataFrame({TIME_COLUMN: np.arange(8, dtype=float),
                          SPECTRUM_INDEX_COLUMN: np.arange(1, 9),
                          'haem': values,
                          },
                         )
    result = delta_abs_calculator(frame, exclude_first_minutes=0.0, window_points=3)
    assert np.allclose(result['haem'], values - 4.0)
    record = result.attrs['delta_abs_baseline']
    assert np.isclose(record['level_by_haem']['haem'], 4.0)
    assert record['window_by_haem']['haem'] == (2.0, 4.0)
    assert np.isclose(record['window_seconds'], 180.0)
    with pytest.raises(ValueError, match='Ignore less'):
        delta_abs_calculator(frame, exclude_first_minutes=0.0, window_points=9)


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


# ---- test_component_names_must_differ ------------------------------------------------
def test_component_names_must_differ() -> None:
    """
    ---- Summary ----
    Main function to check that the components found cannot be turned into a fit under
    names that would break it once saved (the same name twice, an empty name, a comma,
    too few names), and that proper names and no names both give a fit.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _mixed_spectra_builder
    """

    _, _, files = _mixed_spectra_builder()
    result = component_builder(component_finder(files, (500.0, 650.0)), 2)
    for names in (['b-like', 'b-like'], ['b-like', ' '], ['b,like', 'c-like']):
        with pytest.raises(ValueError, match='its own name'):
            fit_table_builder(result, names)
    with pytest.raises(ValueError, match='one name for each'):
        fit_table_builder(result, ['b-like'])
    assert fit_table_builder(result, ['b-like', 'c-like'])['haem_list'] == ['b-like',
                                                                            'c-like',
                                                                            ]
    assert fit_table_builder(result)['haem_list'] == ['PC1', 'PC2']


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
