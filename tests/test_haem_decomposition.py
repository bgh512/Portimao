"""
Tests that the haem decomposition gives back the amounts a spectrum was built from,
whatever its background (the one the dataset's answers name, Rowan scatter exactly as
the lab's chamber scripts fit it), with only some haems or from the first spectrum, and
that the component finder gives back the shapes its spectra were mixed from.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
from pathlib import Path
from typing import Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared import experiment_processing
from utils_shared.pca_fitter import (component_builder,
                                     component_count_suggester,
                                     component_finder,
                                     decomposition_example_finder,
                                     fit_saver,
                                     fit_table_builder,
                                     )
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN
from utils_shared.spectral_decomposer import (background_builder,
                                              decomposition_gap_calculator,
                                              delta_abs_calculator,
                                              experiment_decomposer,
                                              FIT_FILE_MARK,
                                              fit_file_writer,
                                              fit_haem_selector,
                                              fit_importer,
                                              fit_loader,
                                              fit_names_lister,
                                              fit_range_finder,
                                              haem_name_plainer,
                                              HAEMS_FOLDER_NAME,
                                              haem_name_typesetter,
                                              spectrum_decomposer,
                                              )


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FIT_FILE = ROOT / 'tests' / 'synthetic_test_fit.csv'
FITS_FOLDER = ROOT / 'fits'  # the fit files users choose from
HAEM_FACTOR = 1000000.0  # the scale the program gives the fit shapes
# What the values of a fit file in each unit are divided by to reach the standard scale
# (OD/mM/cm divided by a million), written out by hand.
UNIT_DIVISORS = {'OD/mM/cm': 1e6, 'OD/µM/cm': 1e3, 'OD/nM/cm': 1.0}
# How closely a fit written to a file and read back must give the same shapes: the file
# keeps 15 significant digits.
ROUND_TRIP = 1e-14
# The haems of the test fit in the order the program reads them, the a haem first, then
# the b, then the c; the file itself lists them a605, cc, bH, bL, b557.
FIT_ORDER = ['Cyt a605', 'Cyt b557', 'Cyt bH', 'Cyt bL', 'Cyt cc']
# Amounts of the five haems, in FIT_ORDER. With the test fit (peaks of 1e-5) they give
# haem signals of 1 to 5 mOD, as in a real run; far smaller signals would be lost in
# the rounding of the 0.4 OD background itself, whatever the maths.
AMOUNTS = np.array([1.0, 2.0, 3.0, 4.0, 5.0]) * 1e-4
OFFSET = 0.4  # a flat background under the haems (OD)
SLOPE = 0.05  # size of the scatter background (OD)
# the backgrounds the program offers, each fitted by a test of its own
BACKGROUNDS = ('scatter_1', 'scatter_2', 'linear', 'rowan_scatter', 'valencia')
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


# ---- _background_shape_builder -------------------------------------------------------
def _background_shape_builder(background: str, wavelengths: np.ndarray) -> list:
    """
    ---- Summary ----
    Helper function to write out, by hand and in other units than the program's, the
    shapes a background of the program must be able to fit beside a flat level.

    ---- Inputs ----
    background : str
        Name of the background, as the program names it.
    wavelengths : np.ndarray
        Wavelengths (nm), shape (n_wavelengths).

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        The shapes, each of shape (n_wavelengths).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    x = wl / 100 nm. scatter_1: 1/x; scatter_2: 1/x and 1/x^2; linear: x - 5.5;
    rowan_scatter: x - 5.5 and (x - 6)^2, a curve with its bottom off the middle;
    valencia: 1/x^2.

    ---- Helpers ----
    None.
    """

    x = wavelengths / 100.0
    return {'scatter_1': [1.0 / x],
            'scatter_2': [1.0 / x, 1.0 / x ** 2],
            'linear': [x - 5.5],
            'rowan_scatter': [x - 5.5, (x - 6.0) ** 2],
            'valencia': [1.0 / x ** 2],
            }[background]


# ---- _file_values_reader -------------------------------------------------------------
def _file_values_reader(path: Path) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to read the shape values of a fit file in the layout with heading
    lines exactly as they are written in it, before any unit or way up is applied.

    ---- Inputs ----
    path : Path
        The fit file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The values, shape (n_rows, n_haems), NaN below a shorter haem.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None. The table starts at the first line after the first empty line: the haem
    names, the row saying what each column holds, then the numbers.

    ---- Helpers ----
    None.
    """

    lines = path.read_text(encoding='utf-8-sig').splitlines()
    empty = lines.index('')
    table = pd.read_csv(io.StringIO('\n'.join(lines[empty + 3:])), header=None)
    return table.iloc[:, 1::2].to_numpy(dtype=float)


# ---- _haem_spectrum_builder ----------------------------------------------------------
def _haem_spectrum_builder() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Helper function to build one spectrum from known amounts of the five haems of the
    test fit file, on a flat and a sloping background.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, FIT_ORDER, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (wavelengths in nm, the spectrum, the haem shapes as columns in FIT_ORDER); the
        wavelengths are those of the fit file.

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
    shapes = table[[f'{name} response' for name in FIT_ORDER]].to_numpy(dtype=float)
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
def _series_decomposer(fit: dict, is_change_from_first: bool = False) -> dict:
    """
    ---- Summary ----
    Helper function to decompose, with a given fit, a run of four spectra holding 1, 4,
    3 and 2 times the known amounts of the five haems of the test fit file.

    ---- Inputs ----
    fit : dict
        Fit dictionary from fit_importer, holding the five haems of the test fit file.
    is_change_from_first : bool
        True fits the change of each spectrum from the first.

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
                                 background='scatter_1',
                                 haemfactor=HAEM_FACTOR,
                                 delta_exclude_first_minutes=0.0,
                                 delta_window_points=1,
                                 is_change_from_first=is_change_from_first,
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
                                background='scatter_1',
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
                       standard['data'].iloc[:, 1::2].to_numpy() * 1e3,
                       rtol=1e-12,
                       atol=0.0,
                       )


# ---- test_every_fit_file_is_read -----------------------------------------------------
def test_every_fit_file_is_read() -> None:
    """
    ---- Summary ----
    Main function to check that every file of the haem library is in the layout with
    heading lines, in OD/mM/cm, holds one haem, and is read without an error or a note,
    with wavelengths that go upwards, on the standard scale; that every fit offered (the
    presets, and any fit file shipped in the fits folder itself) is read the same way;
    and that every library file is in a preset. Leftover rows and the million scale of
    the older layout are tested on made-up files.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FITS_FOLDER, UNIT_DIVISORS (module constants); HAEMS_FOLDER_NAME.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Standard scale: the highest point of the shapes lies between 1e-7 and 1e-3.

    ---- Helpers ----
    None.
    """

    # ---- 1 Every library file --------------------------------------------------------
    paths = sorted((FITS_FOLDER / HAEMS_FOLDER_NAME).glob('*.csv'))
    assert paths
    for path in paths:
        lines = path.read_text(encoding='utf-8-sig').splitlines()
        assert lines[0].startswith(f'{FIT_FILE_MARK},'), path.name
        assert 'Unit,OD/mM/cm' in lines, path.name
        assert len(fit_importer(path)['haem_list']) == 1, path.name

    # ---- 2 Every fit offered ---------------------------------------------------------
    names = fit_names_lister(FITS_FOLDER)
    assert names
    used = set()
    for name in names:
        fit = fit_loader(FITS_FOLDER, name)
        used |= set(fit.get('haem_files', []))
        data = fit['data']
        assert len(fit['haem_list']) == data.shape[1] // 2
        for i in range(len(fit['haem_list'])):
            pair = data.iloc[:, [2 * i, 2 * i + 1]].dropna().to_numpy()
            assert len(pair) >= 2
            assert np.all(np.diff(pair[:, 0]) >= 0)
        peak = np.nanmax(np.abs(data.iloc[:, 1::2].to_numpy()))
        assert 1e-7 <= peak <= 1e-3
        assert fit['scale_divisor'] == UNIT_DIVISORS['OD/mM/cm']
        assert fit['notes'] == [], name
    assert used == {path.name for path in paths}


# ---- test_haem_names_go_to_figure_form_and_back --------------------------------------
@pytest.mark.parametrize(('plain', 'figure'),
                         [('Cyt bH', 'Cyt $b_H$'),
                          ('Cyt bL', 'Cyt $b_L$'),
                          ('Cyt b557', 'Cyt $b_{557}$'),
                          ('Cyt a605', 'Cyt $a_{605}$'),
                          ('Cyt cc', 'Cyt $cc$'),
                          ('Cyt c1', 'Cyt $c_1$'),
                          ('Cyt aa3', 'Cyt $aa_3$'),
                          ('PC1', 'PC1'),
                          ('a-like', 'a-like'),
                          ('other', 'other'),
                          ],
                         )
def test_haem_names_go_to_figure_form_and_back(plain: str, figure: str) -> None:
    """
    ---- Summary ----
    Main function to check that a plain haem name is put in the form the figures draw
    (haem letters in italics, a capital letter or number after them below the line),
    that other words are left alone, and that the figure form gives the plain name
    back.

    ---- Inputs ----
    plain : str
        The name as a fit file writes it.
    figure : str
        The name the figures draw, written out by hand.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert haem_name_typesetter(plain) == figure
    assert haem_name_plainer(figure) == plain


# ---- test_a_fit_file_reads_back_the_same_in_each_unit --------------------------------
@pytest.mark.parametrize('unit', sorted(UNIT_DIVISORS))
def test_a_fit_file_reads_back_the_same_in_each_unit(tmp_path: Path, unit: str) -> None:
    """
    ---- Summary ----
    Main function to check that the test fit, written in the layout with heading lines
    in one of the units, holds its shapes in that unit and is read back as the same
    shapes, names in figure form and amounts.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.
    unit : str
        The unit written.

    ---- Globals read ----
    FIT_FILE, UNIT_DIVISORS, ROUND_TRIP, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    The shapes of the test fit are on the standard scale (OD/mM/cm divided by a
    million), so the file holds them x 1e6 in OD/mM/cm, x 1e3 in OD/µM/cm and x 1 in
    OD/nM/cm.

    ---- Helpers ----
    _file_values_reader
    _series_decomposer
    """

    standard = fit_importer(FIT_FILE)
    path = fit_file_writer(standard,
                           tmp_path / 'unit.csv',
                           unit,
                           'made-up shapes',
                           'oxidised minus reduced',
                           )
    written = _file_values_reader(path)
    shapes = standard['data'].iloc[:, 1::2].to_numpy(dtype=float)
    assert np.allclose(written,
                       shapes * UNIT_DIVISORS[unit],
                       rtol=ROUND_TRIP,
                       atol=0.0,
                       equal_nan=True,
                       )

    found = fit_importer(path)
    assert found['haem_list'] == [haem_name_typesetter(name)
                                  for name in standard['haem_list']
                                  ]
    assert found['scale_divisor'] == UNIT_DIVISORS[unit]
    assert found['notes'] == []
    assert np.allclose(found['data'].to_numpy(),
                       standard['data'].to_numpy(),
                       rtol=ROUND_TRIP,
                       atol=0.0,
                       equal_nan=True,
                       )
    expected = _series_decomposer(standard)['haem_conc'][standard['haem_list']]
    amounts = _series_decomposer(found)['haem_conc'][found['haem_list']]
    assert np.allclose(amounts.to_numpy(), expected.to_numpy(), rtol=EXACT, atol=0.0)


# ---- test_reduced_minus_oxidised_is_turned_over --------------------------------------
def test_reduced_minus_oxidised_is_turned_over(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file whose Way up line says 'reduced minus
    oxidised' holds its shapes upside down and is turned over when read, so it gives
    the same shapes as the same fit written the way the decomposition uses them.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    FIT_FILE, UNIT_DIVISORS, ROUND_TRIP (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    value written = -shape x 1e6 (OD/mM/cm).

    ---- Helpers ----
    _file_values_reader
    """

    standard = fit_importer(FIT_FILE)
    path = fit_file_writer(standard,
                           tmp_path / 'upside_down.csv',
                           'OD/mM/cm',
                           'made-up shapes',
                           'reduced minus oxidised',
                           )
    shapes = standard['data'].iloc[:, 1::2].to_numpy(dtype=float)
    assert np.allclose(_file_values_reader(path),
                       -shapes * UNIT_DIVISORS['OD/mM/cm'],
                       rtol=ROUND_TRIP,
                       atol=0.0,
                       equal_nan=True,
                       )
    assert np.allclose(fit_importer(path)['data'].to_numpy(),
                       standard['data'].to_numpy(),
                       rtol=ROUND_TRIP,
                       atol=0.0,
                       equal_nan=True,
                       )


# ---- test_a_single_haem_file_reads_back_the_same -------------------------------------
def test_a_single_haem_file_reads_back_the_same(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file holding one haem only is written and read
    back as that haem.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    FIT_FILE, ROUND_TRIP (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    single = fit_haem_selector(fit_importer(FIT_FILE), ['Cyt bL'])
    path = fit_file_writer(single,
                           tmp_path / 'bL.csv',
                           'OD/mM/cm',
                           'one made-up shape',
                           'oxidised minus reduced',
                           )
    found = fit_importer(path)
    assert found['haem_list'] == ['Cyt $b_L$']
    assert found['notes'] == []
    assert np.allclose(found['data'].to_numpy(),
                       single['data'].to_numpy(),
                       rtol=ROUND_TRIP,
                       atol=0.0,
                       )


# ---- test_wrong_headed_fit_files_are_refused -----------------------------------------
@pytest.mark.parametrize(('text', 'message'),
                         [('Portimao fit file\nUnit,OD/mM/cm\n\na,\n'
                           'Wavelength (nm),OD/mM/cm\n1,2\n2,3\n',
                           'its first line must say',
                           ),
                          ('Portimao fit file,format 2\nUnit,OD/mM/cm\n\na,\n'
                           'Wavelength (nm),OD/mM/cm\n1,2\n2,3\n',
                           'newer than',
                           ),
                          ('Portimao fit file,format 1\nHolds,shapes\n\na,\n'
                           'Wavelength (nm),OD/mM/cm\n1,2\n2,3\n',
                           'has no Unit line',
                           ),
                          ('Portimao fit file,format 1\nUnit,OD/M/cm\n\na,\n'
                           'Wavelength (nm),OD/M/cm\n1,2\n2,3\n',
                           'the unit must be one of',
                           ),
                          ('Portimao fit file,format 1\nUnit,OD/mM/cm\n'
                           'Way up,upside down\n\na,\nWavelength (nm),OD/mM/cm\n'
                           '1,2\n2,3\n',
                           'Way up line says',
                           ),
                          ('Portimao fit file,format 1\nUnit,OD/mM/cm\n\na,\n1,2\n'
                           '2,3\n',
                           r'the row under the haem names \(row 5\)',
                           ),
                          ('Portimao fit file,format 1\nUnit,OD/mM/cm\n',
                           'no table of shapes',
                           ),
                          ('Portimao fit file,format 1\nUnit,OD/mM/cm\n\na,\n'
                           'Wavelength (nm),OD/mM/cm\n1,2\nx,3\n',
                           'row 7 is not a number',
                           ),
                          ],
                         )
def test_wrong_headed_fit_files_are_refused(tmp_path: Path,
                                            text: str,
                                            message: str,
                                            ) -> None:
    """
    ---- Summary ----
    Main function to check that a fit file in the layout with heading lines is refused
    with a message that says what is wrong and where: no format, a newer format, no
    Unit line, an unknown unit, an unknown way up, no row saying what the columns
    hold, no table, and a cell that is not a number (named by its row in the file).

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.
    text : str
        Contents of the fit file.
    message : str
        Words the message must hold (a regular expression).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    In the last file the lines are: the format, the unit, an empty line, the names,
    the row saying what the columns hold, then '1,2' and 'x,3': the x is in row 7.

    ---- Helpers ----
    None.
    """

    path = tmp_path / 'wrong.csv'
    path.write_text(text, encoding='utf-8')
    with pytest.raises(ValueError, match=message):
        fit_importer(path)


# ---- test_saved_components_read_back_the_same ----------------------------------------
def test_saved_components_read_back_the_same(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that components found by the component finder and saved as
    a fit file hold their shapes as found (largest point 1, unit 'relative') and are
    read back as the same fit.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    ROUND_TRIP (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    value written = response x 1e6 = the component as found, whose largest point is 1.

    ---- Helpers ----
    _file_values_reader
    _mixed_spectra_builder
    """

    _, _, files = _mixed_spectra_builder()
    result = component_builder(component_finder(files, (500.0, 650.0)), 2)
    fit = fit_table_builder(result, ['b-like', 'c-like'])
    path = fit_saver(fit, tmp_path / 'components.csv')
    assert 'Unit,relative' in path.read_text(encoding='utf-8-sig').splitlines()
    assert np.allclose(np.nanmax(_file_values_reader(path), axis=0),
                       1.0,
                       rtol=ROUND_TRIP,
                       )
    found = fit_importer(path)
    assert found['haem_list'] == ['b-like', 'c-like']
    assert found['notes'] == []
    assert np.allclose(found['data'].to_numpy(),
                       fit['data'].to_numpy(),
                       rtol=ROUND_TRIP,
                       atol=0.0,
                       )


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
        background='scatter_1',
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
                          background='scatter_1',
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
                              background='scatter_1',
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
                          background='scatter_1',
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
                            background='scatter_1',
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
                              background='scatter_1',
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


# ---- test_the_gap_between_two_decompositions -----------------------------------------
def test_the_gap_between_two_decompositions() -> None:
    """
    ---- Summary ----
    Main function to check the largest and the average gap between the haem traces of
    two decompositions: the spectra are matched by their index, not their row; a haem
    is matched by its plain name; a haem in only one of them, and a spectrum with no
    value, are left out; a table without the spectrum index is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    bL new 1.0, 2.0, 3.0 and kept 1.0, 1.5, 3.5 (spectra 1 to 3): gaps 0, 0.5, -0.5,
    so the largest is 0.5 and the average (0 + 0.5 + 0.5) / 3 = 1/3. Cyt cc new 4.0,
    4.0, 4.0 and kept 3.0, (no value), 5.0: gaps 1 and -1, so both are 1. The kept
    table lists its spectra in the order 3, 1, 2.

    ---- Helpers ----
    None.
    """

    new = pd.DataFrame({TIME_COLUMN: [0.0, 1.0, 2.0],
                        SPECTRUM_INDEX_COLUMN: [1, 2, 3],
                        'bL': [1.0, 2.0, 3.0],
                        'Cyt cc': [4.0, 4.0, 4.0],
                        'a605': [7.0, 7.0, 7.0],
                        },
                       )
    kept = pd.DataFrame({TIME_COLUMN: [2.0, 0.0, 1.0],
                         SPECTRUM_INDEX_COLUMN: [3, 1, 2],
                         'bL': [3.5, 1.0, 1.5],
                         'cyt c c': [5.0, 3.0, np.nan],
                         'bH': [0.0, 0.0, 0.0],
                         },
                        )
    gaps = decomposition_gap_calculator(new, kept)
    assert list(gaps) == ['bL', 'Cyt cc']
    assert np.allclose(gaps['bL'], (0.5, 1.0 / 3.0))
    assert np.allclose(gaps['Cyt cc'], (1.0, 1.0))
    with pytest.raises(KeyError):
        decomposition_gap_calculator(new.drop(columns=SPECTRUM_INDEX_COLUMN), kept)


# ---- test_each_background_gives_back_the_amounts -------------------------------------
@pytest.mark.parametrize('background', BACKGROUNDS)
def test_each_background_gives_back_the_amounts(background: str) -> None:
    """
    ---- Summary ----
    Main function to check that a spectrum built from known amounts of each haem on a
    background of one kind decomposes, with that background, into those amounts and
    that background, with nothing left over.

    ---- Inputs ----
    background : str
        Name of the background, as the program names it.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    spectrum = sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x each shape of
    the background (_background_shape_builder). The amounts found must be AMOUNTS, and
    the background found the part of the spectrum that is not haem.

    ---- Helpers ----
    _background_shape_builder
    _haem_spectrum_builder
    """

    wavelengths, _, shapes = _haem_spectrum_builder()
    haem_part = (shapes @ AMOUNTS) * HAEM_FACTOR
    spectrum = haem_part + OFFSET
    for shape in _background_shape_builder(background, wavelengths):
        spectrum = spectrum + SLOPE * shape
    found, _, fitted_background, _, _, _, residual = spectrum_decomposer(
        np.column_stack((wavelengths, spectrum)),
        fit_importer(FIT_FILE)['data'],
        background=background,
        haemfactor=HAEM_FACTOR,
        )
    assert np.allclose(found[:5], AMOUNTS, rtol=EXACT, atol=0.0)
    assert np.allclose(fitted_background[:, 1], spectrum - haem_part, atol=1e-9)
    assert np.abs(residual[:, 1]).max() < 1e-9


# ---- test_an_unknown_background_is_refused -------------------------------------------
def test_an_unknown_background_is_refused() -> None:
    """
    ---- Summary ----
    Main function to check that a background the program does not know is refused with
    a message that names it and the ones it knows, and that the standard background in
    config.py is one it knows.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BACKGROUNDS (module constant); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    wavelengths = np.array([500.0, 550.0, 600.0])
    with pytest.raises(ValueError, match='no background called "cubic"'):
        background_builder(wavelengths, 'cubic')
    standard = settings.DEFAULT_ANSWERS['haem_background']
    assert standard in BACKGROUNDS
    assert background_builder(wavelengths, standard).shape[0] == 3


# ---- test_the_background_answered_is_the_one_used ------------------------------------
def test_the_background_answered_is_the_one_used(monkeypatch: pytest.MonkeyPatch,
                                                 ) -> None:
    """
    ---- Summary ----
    Main function to check that the processing of a file decomposes its haems with the
    background named in the dataset's answers, not the standard one.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the attenuation and the decomposition, so no file is read.

    ---- Globals read ----
    FIT_FILE (module constant); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- _DecompositionReached -------------------------------------------------------
    class _DecompositionReached(Exception):
        """Stops the processing once the decomposition is asked for."""

    used = []

    def _decomposer_stand_in(*args, **kwargs) -> None:
        used.append(kwargs['background'])
        raise _DecompositionReached()

    monkeypatch.setattr(experiment_processing,
                        'experiment_attenuation_adder',
                        lambda *args, **kwargs: None,
                        )
    monkeypatch.setattr(experiment_processing,
                        'experiment_decomposer',
                        _decomposer_stand_in,
                        )

    # ---- 2 Process a made-up file with another background than the standard ----------
    assert settings.DEFAULT_ANSWERS['haem_background'] != 'linear'
    answers = dict(settings.DEFAULT_ANSWERS, haem_background='linear')
    info = {'path': Path('made_up.paf'),
            'name': 'made_up',
            'ignore_start': 5.0,
            'ignore_end': 0.0,
            }
    experiment = {'metadata': {'events': []}, 'CcO2': [0.0, 0.0]}
    with pytest.raises(_DecompositionReached):
        experiment_processing.experiment_data_processor(info,
                                                        settings.Config(answers),
                                                        fit_importer(FIT_FILE),
                                                        experiment,
                                                        )
    assert used == ['linear']


# ---- test_rowan_scatter_is_the_chamber_scripts_background ----------------------------
def test_rowan_scatter_is_the_chamber_scripts_background() -> None:
    """
    ---- Summary ----
    Main function to check that the background called Rowan scatter is the additive
    background of the lab's own chamber scripts: their lines build the same terms, and
    a spectrum that neither can fit exactly gives the same haem amounts and the same
    leftover with both.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The scripts' terms over the fitted wavelengths cw, as their lines write them (only
    their basis S is called s_array here): blank = 1; scatter2 = cw, and scatter3 =
    (cw - centre)^2 with centre = (cw[0] + cw[-1]) / 2, each scaled as (f - min f) /
    max(f - min f). Their amounts are the least-squares solution of [haem shapes x
    HAEM_FACTOR, blank, scatter2, scatter3]. The spectrum's background, OFFSET + SLOPE
    / x^2 (x = wl / 100 nm), is not of that kind, so about 3e-5 OD is left over.

    ---- Helpers ----
    _haem_spectrum_builder
    """

    # ---- 1 Build a spectrum Rowan scatter cannot fit exactly -------------------------
    wavelengths, _, shapes = _haem_spectrum_builder()
    spectrum = ((shapes @ AMOUNTS) * HAEM_FACTOR
                + OFFSET
                + SLOPE / (wavelengths / 100.0) ** 2
                )

    # ---- 2 Fit it with the scripts' own lines ----------------------------------------
    cw = wavelengths
    centre = (cw[0] + cw[-1]) / 2
    blank = np.zeros(len(cw)) + 1.0
    scatter2_function = cw
    scatter2 = ((scatter2_function - np.amin(scatter2_function))
                / np.amax(scatter2_function - np.amin(scatter2_function))
                )
    scatter3_function = (cw - centre) ** 2
    scatter3 = ((scatter3_function - np.amin(scatter3_function))
                / np.amax(scatter3_function - np.amin(scatter3_function))
                )
    s_array = shapes * HAEM_FACTOR
    s_array = np.column_stack((s_array, blank))
    s_array = np.column_stack((s_array, scatter2))
    s_array = np.column_stack((s_array, scatter3))
    theirs = np.linalg.lstsq(s_array, spectrum, rcond=None)[0]
    their_leftover = spectrum - s_array @ theirs

    # ---- 3 Fit it with ours and compare ----------------------------------------------
    assert np.allclose(background_builder(cw, 'rowan_scatter'),
                       s_array[:, len(AMOUNTS):],
                       rtol=0.0,
                       atol=1e-12,
                       )
    found, _, _, _, _, _, leftover = spectrum_decomposer(
        np.column_stack((wavelengths, spectrum)),
        fit_importer(FIT_FILE)['data'],
        background='rowan_scatter',
        haemfactor=HAEM_FACTOR,
        )
    assert np.abs(their_leftover).max() > 1e-6
    assert np.allclose(found[:len(AMOUNTS)],
                       theirs[:len(AMOUNTS)],
                       rtol=EXACT,
                       atol=0.0,
                       )
    assert np.allclose(leftover[:, 1], their_leftover, rtol=0.0, atol=1e-12)


# ---- test_some_haems_only_give_back_their_amounts ------------------------------------
def test_some_haems_only_give_back_their_amounts(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a fit can keep only some of its haems: they are kept in
    the order of the file, a spectrum built from them alone decomposes into their
    amounts, leaving out a short haem widens the wavelengths used, the fit given is not
    changed, and naming no haem or one the fit does not hold is refused.

    ---- Inputs ----
    tmp_path : Path
        Empty folder given by pytest.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes a fit file in tmp_path (side effect).

    ---- Equations ----
    The test fit runs from 400 to 700 nm in 1 nm steps; Cyt cc is ended at 650 nm (row
    251), so the five haems share 400 to 650 nm and the four others 400 to 700 nm.
    spectrum = AMOUNTS of Cyt cc and Cyt bL only x their shapes x HAEM_FACTOR + OFFSET
    + SLOPE x background.

    ---- Helpers ----
    _background_builder
    _haem_spectrum_builder
    """

    # ---- 1 Keep two haems and decompose a spectrum made of them ----------------------
    wavelengths, _, shapes = _haem_spectrum_builder()
    fit = fit_importer(FIT_FILE)
    kept = fit_haem_selector(fit, ['Cyt bL', 'Cyt cc'])
    assert kept['haem_list'] == ['Cyt bL', 'Cyt cc']
    assert len(fit['haem_list']) == 5
    spectrum = ((shapes[:, [3, 4]] @ AMOUNTS[[3, 4]]) * HAEM_FACTOR
                + OFFSET
                + SLOPE * _background_builder(wavelengths)
                )
    found = spectrum_decomposer(np.column_stack((wavelengths, spectrum)),
                                kept['data'],
                                background='scatter_1',
                                haemfactor=HAEM_FACTOR,
                                )[0]
    assert len(found) == 4  # two haems, the flat level and the scatter term
    assert np.allclose(found[:2], AMOUNTS[[3, 4]], rtol=EXACT, atol=0.0)

    # ---- 2 Leave out a short haem ----------------------------------------------------
    table = pd.read_csv(FIT_FILE)
    table.iloc[251:, 2:4] = np.nan
    table.to_csv(tmp_path / 'short.csv', index=False)
    short = fit_importer(tmp_path / 'short.csv')
    assert fit_range_finder(short['data']) == (400.0, 650.0)
    others = [name for name in short['haem_list'] if name != 'Cyt cc']
    assert fit_range_finder(fit_haem_selector(short, others)['data']) == (400.0, 700.0)
    alone = fit_haem_selector(short, ['Cyt cc'])
    assert alone['data'].shape == (251, 2)  # its blank rows below 650 nm are gone

    # ---- 3 Refuse what cannot be kept ------------------------------------------------
    with pytest.raises(ValueError, match='No haem was chosen'):
        fit_haem_selector(fit, [])
    with pytest.raises(ValueError, match='Cyt x: not in the fit file'):
        fit_haem_selector(fit, ['Cyt cc', 'Cyt x'])


# ---- test_the_change_from_the_first_spectrum -----------------------------------------
def test_the_change_from_the_first_spectrum() -> None:
    """
    ---- Summary ----
    Main function to check that fitting the change of each spectrum from the first, as
    the instrument does, gives each amount and absorbance minus that of the first
    spectrum, and the same change from the highest point (delta A) as fitting the
    spectra themselves; and that a first spectrum with a blank value is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIT_FILE, HAEM_FACTOR, AMOUNTS, EXACT (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The run holds 1, 4, 3 and 2 times AMOUNTS (_series_decomposer), so its changes from
    the first spectrum are 0, 3, 2 and 1 times AMOUNTS; absorbance = amount x highest
    point of |shape_i| x HAEM_FACTOR x 1000.

    ---- Helpers ----
    _haem_spectrum_builder
    _series_decomposer
    """

    # ---- 1 The change of a run -------------------------------------------------------
    fit = fit_importer(FIT_FILE)
    names = list(fit['haem_list'])
    change = _series_decomposer(fit, is_change_from_first=True)
    itself = _series_decomposer(fit)
    expected = np.outer([0.0, 3.0, 2.0, 1.0], AMOUNTS)
    assert np.allclose(change['haem_conc'][names].to_numpy(),
                       expected,
                       rtol=EXACT,
                       atol=EXACT * expected.max(),
                       )
    _, _, shapes = _haem_spectrum_builder()
    absorbances = expected * np.abs(shapes).max(axis=0)[None, :] * HAEM_FACTOR * 1000.0
    assert np.allclose(change['haem_abs'][names].to_numpy(),
                       absorbances,
                       rtol=EXACT,
                       atol=EXACT * absorbances.max(),
                       )
    delta = itself['haem_delta_abs'][names].to_numpy()
    assert np.allclose(change['haem_delta_abs'][names].to_numpy(),
                       delta,
                       rtol=EXACT,
                       atol=EXACT * np.abs(delta).max(),
                       )

    # ---- 2 A first spectrum with a blank value ---------------------------------------
    blank = _series_decomposer(fit)
    blank['raw_spectra']['Cyt']['attenuation'][0, 100] = np.nan
    with pytest.raises(ValueError, match='first Cyt spectrum has blank values'):
        experiment_decomposer(blank,
                              fit,
                              dataset_name='Cyt',
                              background='scatter_1',
                              haemfactor=HAEM_FACTOR,
                              delta_exclude_first_minutes=0.0,
                              delta_window_points=1,
                              is_change_from_first=True,
                              )


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
