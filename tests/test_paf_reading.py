"""
Tests that what is read from a .paf file equals the instrument software's own export of
the same run, at every point, and that the parts read fit together.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Iterator, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.attenuation import attenuation_converter
from utils_shared.paf_reader import (experiment_paf_loader,
                                     experiment_summary_reader,
                                     PafFile,
                                     )
from utils_shared.schema import TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / 'data_instrument_check'  # local only: one run and its manual export
PAF_FILE = FOLDER / 'example.paf'
SPECTRA_FILES = {'Cyt': 'cyt', 'NADH': 'nadh'}  # dataset -> start of its export names
# trace name in the .paf -> name of its exported text file
TRACE_FILES = {'CcO2': 'CcO2',
               'CsO2': 'CsO2',
               'VoO2': 'VoO2',
               'PcO2': 'PcO2',
               'PtO2': 'PtO2',
               'DgO2': 'DgO2',
               'VrO2': 'VrO2',
               'FtO2': 'FtO2',
               'Cytc1': 'Cytc1',
               'CytbH': 'bH',
               'CytbL': 'bL',
               'Cyta605': 'a605',
               'Cytb557': 'b557',
               }
# the oxygen titles carry the unit stored in the file (µM, with the micro sign)
LOADED_TRACES = {'CcO2': 'Measured O2 (µM)', 'CsO2': 'Set O2 (µM)', 'VoO2': 'VoO2'}
EXPORT_MARK = (0x7073450F, 0x20616E61, 0x63657053, 0x6D757274)  # 'Espana Spectrum'
EXPORT_HEADER_BYTES = 64
EXPECTED_SPECTRA = 6218
EXPECTED_WAVELENGTHS = 2046
EXPECTED_STEP_S = 0.5
# (spectrum number, text) of each addition of the example run
EXPECTED_EVENTS = [(1681, '1ul 8mm nd-011992'),
                   (2278, '2ul 8mm nd-011992'),
                   (2880, '10ul 8mm nd-011992'),
                   (3479, '1ul 10mm kcn'),
                   (4200, '9ul 10mm kcn'),
                   (4801, '4ul 100mm kcn'),
                   (5388, '20ul 1m dithi'),
                   ]
ROUNDING = 0.00051  # the text export has 3 decimals
ROWS_AT_ONCE = 512  # spectra compared at a time, to keep the memory use low

pytestmark = pytest.mark.skipif(
    not PAF_FILE.exists(),
    reason='the example run in data_instrument_check/ (local only, not in git) is '
           'missing, so the reading tests are skipped',
    )


# ---- HELPERS -------------------------------------------------------------------------


# ---- _dataset_loader -----------------------------------------------------------------
@pytest.fixture(name='dataset', scope='module', params=sorted(SPECTRA_FILES))
def _dataset_loader(request: pytest.FixtureRequest) -> Iterator[dict]:
    """
    ---- Summary ----
    Helper function to read one spectrometer of the example run once for all the tests
    that use it.

    ---- Inputs ----
    request : pytest.FixtureRequest
        Gives the dataset name ('Cyt' or 'NADH').

    ---- Globals read ----
    PAF_FILE, ROWS_AT_ONCE (module constants).

    ---- Outputs ----
    Iterator[dict]
        The dictionary of spectra_dataset_reader (with the intensity), plus 'name',
        'reference_counts' (the stored reference spectrum as whole counts) and
        'stored_error' (the largest difference between our attenuation and the stored
        logarithm of the reference minus that of each spectrum).

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    stored attenuation = log10(reference) - log10(counts), both as stored in the file.

    ---- Helpers ----
    None.
    """

    name = request.param
    with PafFile(PAF_FILE) as paf:
        data = paf.spectra_dataset_reader(name, with_intensity=True)
        spectra = paf.spectra[paf.dataset_name_lister().index(name)]
        reference = spectra.log[1].astype('f8')
        stored_error = 0.0
        for start in range(0, spectra.nframes, ROWS_AT_ONCE):
            rows = slice(start, start + ROWS_AT_ONCE)
            stored = reference[None, :] - spectra.log[2:][rows].astype('f8')
            ours = attenuation_converter(data['transmission'][rows])
            stored_error = max(stored_error, float(np.abs(ours - stored).max()))
    data.update(name=name,
                reference_counts=np.round(10.0 ** reference),
                stored_error=stored_error,
                )
    yield data


# ---- _export_reader ------------------------------------------------------------------
def _export_reader(path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Helper function to open a spectrum file exported by the instrument software
    ('Espana Spectrum' format). The test is skipped when the file is not there.

    ---- Inputs ----
    path : Path
        The exported file.

    ---- Globals read ----
    EXPORT_MARK, EXPORT_HEADER_BYTES (module constants).

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (spectrum numbers, wavelengths in nm, spectra as (n_spectra, n_wavelengths));
        the spectra stay on disc and are read as they are used.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    The file is a 64 byte header (the mark as 4 whole numbers, then the version, the
    number of spectra NS, of wavelengths NW and of spectrum numbers NT, then zeros),
    NT whole numbers of 4 bytes, NW wavelengths of 8 bytes and NS x NW values of 8
    bytes: 64 + 4 NT + 8 NW + 8 NS NW bytes in all.

    ---- Helpers ----
    None.
    """

    if not path.exists():
        pytest.skip(f'{path.name} is not in {path.parent.name}/, so it is not compared')
    header = np.fromfile(path, dtype='<u4', count=EXPORT_HEADER_BYTES // 4)
    assert tuple(int(v) for v in header[:4]) == EXPORT_MARK, (
        f'{path.name} does not start with the mark of an exported spectrum file.'
    )
    n_spectra, n_wavelengths, n_numbers = (int(v) for v in header[5:8])
    start = EXPORT_HEADER_BYTES + 4 * n_numbers
    expected_bytes = start + 8 * n_wavelengths + 8 * n_spectra * n_wavelengths
    assert path.stat().st_size == expected_bytes, (
        f'{path.name} is {path.stat().st_size} bytes, but its header ({n_spectra} '
        f'spectra, {n_wavelengths} wavelengths) needs {expected_bytes}.'
    )
    numbers = (np.fromfile(path, dtype='<u4', count=n_numbers, offset=EXPORT_HEADER_BYTES)
               if n_numbers
               else np.arange(1, n_spectra + 1)
               )
    wavelengths = np.fromfile(path, dtype='<f8', count=n_wavelengths, offset=start)
    spectra = np.memmap(path,
                        dtype='<f8',
                        mode='r',
                        offset=start + 8 * n_wavelengths,
                        shape=(n_spectra, n_wavelengths),
                        )
    return numbers, wavelengths, spectra


# ---- _trace_export_reader ------------------------------------------------------------
def _trace_export_reader(path: Path) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to read a trace exported by the instrument software as text. The
    test is skipped when the file is not there.

    ---- Inputs ----
    path : Path
        The exported text file: a time (min) and a value on each line.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The times and the values, shape (n_points, 2). Lines without two numbers (the
        export ends with one) are left out.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not path.exists():
        pytest.skip(f'{path.name} is not in {path.parent.name}/, so it is not compared')
    rows = []
    for line in path.read_text(encoding='latin-1').splitlines():
        parts = line.replace('\x00', '').split()
        if len(parts) == 2:
            rows.append((float(parts[0]), float(parts[1])))
    return np.array(rows, dtype=float)


# ---- _trace_loader -------------------------------------------------------------------
@pytest.fixture(name='traces', scope='module')
def _trace_loader() -> dict:
    """
    ---- Summary ----
    Helper function to read the traces and the times of the example run once.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PAF_FILE, TRACE_FILES (module constants).

    ---- Outputs ----
    dict
        {'time_s': the times in seconds, 'values': {trace name: one value per time,
        blank where the file has none}, 'experiment': the experiment as the program
        loads it, without its spectra}.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    with PafFile(PAF_FILE) as paf:
        time_s = paf.time_s.copy()
        values = {name: paf.stream_reader(name) for name in TRACE_FILES}
    return {'time_s': time_s,
            'values': values,
            'experiment': experiment_paf_loader(PAF_FILE, spectral_datasets=()),
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_known_file_counts ----------------------------------------------------------
def test_known_file_counts() -> None:
    """
    ---- Summary ----
    Main function to check that the example run gives its known numbers of spectra,
    spectrometers and additions, and the additions at their known places.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PAF_FILE, EXPECTED_SPECTRA, EXPECTED_EVENTS, EXPECTED_STEP_S, TRACE_FILES (module
    constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    6,218 spectra 0.5 s apart last (6218 - 1) x 0.5 s = 3108.5 s = 51.808 min; an
    addition at spectrum n is at (n - 1) x 0.5 s.

    ---- Helpers ----
    None.
    """

    summary = experiment_summary_reader(PAF_FILE)
    assert summary['frames'] == EXPECTED_SPECTRA
    assert summary['datasets'] == ['Cyt', 'NADH']
    assert np.isclose(summary['duration_min'],
                      (EXPECTED_SPECTRA - 1) * EXPECTED_STEP_S / 60.0,
                      )
    assert set(TRACE_FILES) <= set(summary['traces'])
    found = [(event['datapoint'], event['text']) for event in summary['events']]
    assert found == EXPECTED_EVENTS
    for event in summary['events']:
        assert np.isclose(event['time'],
                          (event['datapoint'] - 1) * EXPECTED_STEP_S / 60.0,
                          )


# ---- test_spectra_counts_match_the_instrument ----------------------------------------
def test_spectra_counts_match_the_instrument(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that we read as many spectra and wavelengths as the
    instrument exports, with the same spectrum numbers and the same wavelengths.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    FOLDER, SPECTRA_FILES, EXPECTED_SPECTRA, EXPECTED_WAVELENGTHS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_reader
    """

    path = FOLDER / f"{SPECTRA_FILES[dataset['name']]}_trans.bin"
    numbers, wavelengths, spectra = _export_reader(path)
    assert spectra.shape == (EXPECTED_SPECTRA, EXPECTED_WAVELENGTHS)
    assert dataset['transmission'].shape == spectra.shape
    assert np.array_equal(dataset['spectrum_indices'], numbers)
    assert np.array_equal(dataset['wavelengths'], wavelengths)


# ---- test_transmission_matches_the_instrument ----------------------------------------
def test_transmission_matches_the_instrument(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that every transmission we read equals the instrument's.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    FOLDER, SPECTRA_FILES, ROWS_AT_ONCE (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The two may differ by a millionth of a millionth of the value (the last digits a
    computer keeps), no more.

    ---- Helpers ----
    _export_reader
    """

    path = FOLDER / f"{SPECTRA_FILES[dataset['name']]}_trans.bin"
    _, _, spectra = _export_reader(path)
    ours = dataset['transmission']
    worst = 0.0
    for start in range(0, len(ours), ROWS_AT_ONCE):
        rows = slice(start, start + ROWS_AT_ONCE)
        theirs = np.asarray(spectra[rows])
        worst = max(worst, float(np.abs(ours[rows] / theirs - 1.0).max()))
    assert worst < 1e-12


# ---- test_intensity_matches_the_instrument -------------------------------------------
def test_intensity_matches_the_instrument(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that every intensity (whole counts) we read equals the
    instrument's.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    FOLDER, SPECTRA_FILES, ROWS_AT_ONCE (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_reader
    """

    path = FOLDER / f"{SPECTRA_FILES[dataset['name']]}_int.bin"
    _, _, spectra = _export_reader(path)
    ours = dataset['intensity']
    different = 0
    for start in range(0, len(ours), ROWS_AT_ONCE):
        rows = slice(start, start + ROWS_AT_ONCE)
        different += int(np.count_nonzero(ours[rows] != np.asarray(spectra[rows])))
    assert different == 0


# ---- test_attenuation_size_matches_the_instrument ------------------------------------
def test_attenuation_size_matches_the_instrument(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that every attenuation we work out has the size of the
    instrument's own, whatever its sign.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    FOLDER, SPECTRA_FILES, ROWS_AT_ONCE (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    |log10(T)| of ours against |attenuation| of the export, to 12 decimals.

    ---- Helpers ----
    _export_reader
    """

    path = FOLDER / f"{SPECTRA_FILES[dataset['name']]}_att.bin"
    _, _, spectra = _export_reader(path)
    worst = 0.0
    for start in range(0, len(spectra), ROWS_AT_ONCE):
        rows = slice(start, start + ROWS_AT_ONCE)
        ours = attenuation_converter(dataset['transmission'][rows])
        difference = np.abs(ours) - np.abs(np.asarray(spectra[rows]))
        worst = max(worst, float(np.abs(difference).max()))
    assert worst < 1e-12


# ---- test_attenuation_sign_matches_the_instrument ------------------------------------
def test_attenuation_sign_matches_the_instrument(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that our attenuation has the sign of the instrument's own:
    more light than the reference gives a negative attenuation, less a positive one.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    FOLDER, SPECTRA_FILES (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The instrument exports -log10(T); the first spectrum is enough to see the sign.

    ---- Helpers ----
    _export_reader
    """

    path = FOLDER / f"{SPECTRA_FILES[dataset['name']]}_att.bin"
    _, _, spectra = _export_reader(path)
    ours = attenuation_converter(dataset['transmission'][0])
    theirs = np.asarray(spectra[0])
    assert np.allclose(ours, theirs, atol=1e-12), (
        "Our attenuation has the opposite sign to the instrument's: ours is "
        f'{ours[0]:.5f} where the instrument exports {theirs[0]:.5f}.'
    )


# ---- test_spectra_parts_agree --------------------------------------------------------
def test_spectra_parts_agree(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that the transmission, the intensity and the attenuation
    read from one file fit together.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    ROWS_AT_ONCE (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    T = counts / reference counts. Both are whole numbers, each up to half a count
    off, so T may be off by T x (0.5 / counts + 0.5 / reference). Attenuation =
    log10(reference) - log10(counts) as stored in the file.

    ---- Helpers ----
    None.
    """

    assert dataset['stored_error'] < 1e-12
    reference = dataset['reference_counts']
    assert np.all(reference > 0)
    for start in range(0, len(dataset['transmission']), ROWS_AT_ONCE):
        rows = slice(start, start + ROWS_AT_ONCE)
        transmission = dataset['transmission'][rows]
        counts = dataset['intensity'][rows]
        usable = counts > 0
        allowed = transmission * (0.5 / np.where(usable, counts, 1.0)
                                  + 0.5 / reference[None, :]
                                  ) * 1.01
        off = np.abs(transmission - counts / reference[None, :])
        assert np.all(off[usable] <= allowed[usable])


# ---- test_times_and_wavelengths_run_in_order -----------------------------------------
def test_times_and_wavelengths_run_in_order(dataset: dict) -> None:
    """
    ---- Summary ----
    Main function to check that the times and wavelengths of the spectra run in order
    with no gaps, and that the spectra are numbered 1 to N.

    ---- Inputs ----
    dataset : dict
        One spectrometer of the example run, from _dataset_loader.

    ---- Globals read ----
    EXPECTED_SPECTRA, EXPECTED_STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time of spectrum n = (n - 1) x 0.5 s; a gap in the wavelengths would be a step of
    more than 1.5 x the usual one.

    ---- Helpers ----
    None.
    """

    seconds = dataset['time'] * 60.0
    assert np.allclose(seconds,
                       np.arange(EXPECTED_SPECTRA) * EXPECTED_STEP_S,
                       atol=1e-6,
                       )
    assert np.array_equal(dataset['spectrum_indices'],
                          np.arange(1, EXPECTED_SPECTRA + 1),
                          )
    steps = np.diff(dataset['wavelengths'])
    assert np.all(steps > 0)
    assert steps.max() < 1.5 * np.median(steps)


# ---- test_traces_match_the_instrument ------------------------------------------------
@pytest.mark.parametrize('name', sorted(TRACE_FILES))
def test_traces_match_the_instrument(traces: dict, name: str) -> None:
    """
    ---- Summary ----
    Main function to check that a trace read from the file has the instrument's value
    at every time, and has values at exactly the times the instrument exports.

    ---- Inputs ----
    traces : dict
        The traces of the example run, from _trace_loader.
    name : str
        Name of the trace in the file.

    ---- Globals read ----
    FOLDER, TRACE_FILES, ROUNDING (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The export has 3 decimals, so a time (min) or a value may differ by 0.0005.

    ---- Helpers ----
    _trace_export_reader
    """

    exported = _trace_export_reader(FOLDER / f'{TRACE_FILES[name]}.txt')
    values = traces['values'][name]
    assert values is not None
    has_value = np.isfinite(values)
    assert np.count_nonzero(has_value) == len(exported)
    minutes = traces['time_s'][has_value] / 60.0
    assert np.abs(minutes - exported[:, 0]).max() < ROUNDING
    assert np.abs(values[has_value] - exported[:, 1]).max() < ROUNDING


# ---- test_loaded_traces_match_the_instrument -----------------------------------------
@pytest.mark.parametrize('name', sorted(LOADED_TRACES))
def test_loaded_traces_match_the_instrument(traces: dict, name: str) -> None:
    """
    ---- Summary ----
    Main function to check that the oxygen tables the program works with (as loaded,
    with their times in minutes) equal the instrument's export row for row.

    ---- Inputs ----
    traces : dict
        The traces of the example run, from _trace_loader.
    name : str
        Name of the table in the experiment.

    ---- Globals read ----
    FOLDER, TRACE_FILES, LOADED_TRACES, ROUNDING, TIME_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The export has 3 decimals, so a time (min) or a value may differ by 0.0005.

    ---- Helpers ----
    _trace_export_reader
    """

    exported = _trace_export_reader(FOLDER / f'{TRACE_FILES[name]}.txt')
    frame = traces['experiment'][name]
    assert len(frame) == len(exported)
    assert np.abs(frame[TIME_COLUMN].to_numpy() - exported[:, 0]).max() < ROUNDING
    assert np.abs(frame[LOADED_TRACES[name]].to_numpy() - exported[:, 1],
                  ).max() < ROUNDING
