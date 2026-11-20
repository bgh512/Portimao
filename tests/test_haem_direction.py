"""
Tests that our haem amounts move the same way as the instrument's own haem traces of
the example run, that the instrument's traces go down when the haems are reduced, and
that the haem shapes of our fit file are those of the instrument's own fit file.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
import struct
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.attenuation import experiment_attenuation_adder
from utils_shared.paf_reader import experiment_paf_loader, MARK, PafFile, token_reader
from utils_shared.spectral_decomposer import experiment_decomposer, fit_importer


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
PAF_FILE = ROOT / 'data_instrument_check' / 'example.paf'  # local only, not in git
FIT_FILE = ROOT / 'fits' / 'bswitch_no2_mycobl_b557.csv'
# the instrument software's own fit file for the example run (local only)
INSTRUMENT_FIT_FILE = (ROOT / 'data_instrument_check'
                       / '20240913_Myco_b557_nolamda.fit')
POINTS_MARK = struct.pack('<3f', 30.0, 15.0, 10.0)  # stands before a shape's points
# haem name in our fit file -> name of the instrument's own trace in the .paf (the
# traces test_paf_reading.py finds equal to the instrument's text export)
HAEM_TRACES = {'Cyt $cc$': 'Cytc1',
               'Cyt $b_H$': 'CytbH',
               'Cyt $b_L$': 'CytbL',
               'Cyt $a_{605}$': 'Cyta605',
               'Cyt $b_{557}$': 'Cytb557',
               }
FIRST_ADDITION_SPECTRUM = 1681  # everything before it is the cells with oxygen
DITHIONITE_SPECTRUM = 5388  # dithionite reduces every haem fully
WINDOW_SPECTRA = 240  # 2 min of spectra, 0.5 s apart
SAME_WAY = 0.0  # correlation above this: the same way; below it: upside down
SAME_SHAPE = 0.99  # correlation of two shapes above this (or below minus this): the same

pytestmark = pytest.mark.skipif(
    not PAF_FILE.exists(),
    reason='the example run in data_instrument_check/ (local only, not in git) is '
           'missing, so the haem direction tests are skipped',
    )


# ---- HELPERS -------------------------------------------------------------------------


# ---- _instrument_fit_reader ----------------------------------------------------------
def _instrument_fit_reader(path: Path) -> dict:
    """
    ---- Summary ----
    Helper function to read the shapes of the instrument software's own fit file
    (.fit), which is made of the same kind of records as a .paf.

    ---- Inputs ----
    path : Path
        The .fit file.

    ---- Globals read ----
    MARK, POINTS_MARK (module constants).

    ---- Outputs ----
    dict
        {'range_nm': (first, last) wavelength the instrument fits over, 'labels': the
        name of each shape in the instrument's list of traces ('Noname' for a shape
        that gives no trace), 'names': the name each shape was saved under, 'shapes':
        one array per shape, shape (n_points, 2): wavelength (nm), then the value, both
        as the instrument uses them (shifted and scaled), 'shifts_nm' and 'scales':
        the shift and the scale that were applied to the saved points}; the lists are
        in the file's order.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    The first record gives the fit name, then 1, the range (two 4 byte numbers), the
    number of shapes and their labels. Each shape is a 'Plot: Scatter' record (its
    name) followed by a record that holds its points: the numbers 30, 15, 10, then 20
    bytes, then the points as (wavelength, value) pairs of 4 byte numbers; the number
    of points is 32 bytes before the 30. The points are stored as they were imported.
    The 'Plot: Scatter' record ends with the shape as the instrument uses it: its
    first and last wavelength and its lowest and highest value (four 4 byte numbers,
    28 bytes before its end). shift = that first wavelength - the first stored one
    (when both spans are equally wide); scale = (highest - lowest) / (the same of the
    stored values in that span), negative when the shape is used upside down.

    ---- Helpers ----
    None.
    """

    data = path.read_bytes()
    marks = [found.start() for found in re.finditer(re.escape(MARK), data)]
    marks.append(len(data))
    head = token_reader(data, 40, marks[1])
    after_name = head[2][2]
    range_nm = struct.unpack_from('<2f', data, after_name + 4)
    count = struct.unpack_from('<I', data, after_name + 12)[0]
    names, views, shapes, shifts_nm, scales = [], [], [], [], []
    for off, end in zip(marks, marks[1:]):
        tokens = token_reader(data, off + 40, min(end, off + 1200))
        if tokens and tokens[0][0] == 'Plot: Scatter':
            names.append(tokens[2][0])
            views.append(np.frombuffer(data, dtype='<f4', count=4, offset=end - 28))
            continue
        at = data.find(POINTS_MARK, off, end)
        if at < 0:
            continue
        n_points = struct.unpack_from('<I', data, at - 32)[0]
        if n_points == 0 or at + 32 + 8 * n_points > end:
            continue
        pairs = np.frombuffer(data, dtype='<f4', count=2 * n_points, offset=at + 32)
        pairs = pairs.reshape(-1, 2).astype(float)
        first, last, lowest, highest = (float(v) for v in views[len(shapes)])
        is_whole = abs((last - first) - (pairs[-1, 0] - pairs[0, 0])) < 0.01
        shift = first - pairs[0, 0] if is_whole else 0.0
        pairs[:, 0] += shift
        seen = pairs[(pairs[:, 0] >= first - 0.01) & (pairs[:, 0] <= last + 0.01), 1]
        size = (highest - lowest) / (seen.max() - seen.min())
        is_flipped = abs(lowest + size * seen.max()) < abs(lowest - size * seen.min())
        scale = -size if is_flipped else size
        pairs[:, 1] *= scale
        shapes.append(pairs)
        shifts_nm.append(shift)
        scales.append(scale)
    assert len(names) == len(shapes) == count
    return {'range_nm': (float(range_nm[0]), float(range_nm[1])),
            'labels': [token[0] for token in head[3:3 + count]],
            'names': names,
            'shapes': shapes,
            'shifts_nm': shifts_nm,
            'scales': scales,
            }


# ---- _haem_trace_loader --------------------------------------------------------------
@pytest.fixture(name='haems', scope='module')
def _haem_trace_loader() -> dict:
    """
    ---- Summary ----
    Helper function to decompose the example run once, as the program does, and to
    read the instrument's own haem traces of the same run.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PAF_FILE, FIT_FILE, HAEM_TRACES (module constants).

    ---- Outputs ----
    dict
        {'ours': {haem name: our amount at each spectrum}, 'theirs': {haem name: the
        instrument's trace at each spectrum}}; every array has shape (n_spectra).

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    experiment = experiment_paf_loader(PAF_FILE, spectral_datasets=('Cyt',))
    experiment_attenuation_adder(experiment)
    # the program's own standard settings, so the amounts are those a user gets
    answers = settings.DEFAULT_ANSWERS
    experiment_decomposer(experiment,
                          fit_importer(FIT_FILE),
                          dataset_name=answers['decomposition_dataset'],
                          degree_of_scatter=settings.DEGREE_OF_SCATTER,
                          haemfactor=settings.HAEM_FACTOR,
                          delta_exclude_first_minutes=answers['ignore_first_minutes'],
                          delta_window_points=settings.REFERENCE_WINDOW_POINTS,
                          )
    amounts = experiment['haem_conc']
    ours = {name: amounts[name].to_numpy(dtype=float) for name in HAEM_TRACES}
    del experiment  # the spectra are not needed once the amounts are known
    with PafFile(PAF_FILE) as paf:
        theirs = {name: np.asarray(paf.stream_reader(trace), dtype=float)
                  for name, trace in HAEM_TRACES.items()
                  }
    return {'ours': ours, 'theirs': theirs}


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_haem_amounts_move_with_the_instrument --------------------------------------
@pytest.mark.parametrize('name', sorted(HAEM_TRACES))
def test_haem_amounts_move_with_the_instrument(haems: dict, name: str) -> None:
    """
    ---- Summary ----
    Main function to check that our amount of a haem rises where the instrument's own
    trace of it rises, and falls where it falls, over the whole run.

    ---- Inputs ----
    haems : dict
        Our amounts and the instrument's traces, from _haem_trace_loader.
    name : str
        Name of the haem in our fit file.

    ---- Globals read ----
    SAME_WAY (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Correlation of the two traces over the spectra where both have a value: +1 when
    they move together, -1 when one is the other upside down. The size and the zero
    of the two differ (other units, other fit shapes), which the correlation ignores.

    ---- Helpers ----
    None.
    """

    ours, theirs = haems['ours'][name], haems['theirs'][name]
    assert len(ours) == len(theirs)
    usable = np.isfinite(ours) & np.isfinite(theirs)
    correlation = float(np.corrcoef(ours[usable], theirs[usable])[0, 1])
    assert correlation > SAME_WAY, (
        f"Our {name} does not move the same way as the instrument's trace: the "
        f'correlation of the two is {correlation:+.3f} (+1 is the same way, -1 is '
        'upside down).'
    )


# ---- test_haem_amounts_fall_when_reduced ---------------------------------------------
@pytest.mark.parametrize('name', sorted(HAEM_TRACES))
def test_haem_amounts_fall_when_reduced(haems: dict, name: str) -> None:
    """
    ---- Summary ----
    Main function to check that our amount of a haem is lower once dithionite has
    reduced it fully than it was with oxygen, before the first addition, as the
    instrument's own trace is.

    ---- Inputs ----
    haems : dict
        Our amounts and the instrument's traces, from _haem_trace_loader.
    name : str
        Name of the haem in our fit file.

    ---- Globals read ----
    FIRST_ADDITION_SPECTRUM, WINDOW_SPECTRA (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    median of the last 2 min of the run (after the dithionite) - median of the 2 min
    before the first addition < 0.

    ---- Helpers ----
    None.
    """

    ours = haems['ours'][name]
    first = FIRST_ADDITION_SPECTRUM - 1  # spectra are numbered from 1
    with_oxygen = float(np.nanmedian(ours[first - WINDOW_SPECTRA:first]))
    reduced = float(np.nanmedian(ours[-WINDOW_SPECTRA:]))
    assert reduced < with_oxygen, (
        f'Our {name} is {reduced:.4g} after the dithionite and {with_oxygen:.4g} '
        "before the first addition: it does not fall when reduced, as the instrument's "
        'trace does.'
    )


# ---- test_haem_shapes_are_those_of_the_instrument ------------------------------------
@pytest.mark.parametrize('name', sorted(HAEM_TRACES))
def test_haem_shapes_are_those_of_the_instrument(name: str) -> None:
    """
    ---- Summary ----
    Main function to check that the shape of a haem in our fit file is the shape the
    instrument's own fit file uses for it (shifted and scaled as the instrument does),
    whatever its size and whichever way up it is stored.

    ---- Inputs ----
    name : str
        Name of the haem in our fit file.

    ---- Globals read ----
    FIT_FILE, INSTRUMENT_FIT_FILE, HAEM_TRACES, SAME_SHAPE (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Correlation of the two shapes at the instrument's wavelengths inside the range it
    fits over, where our file has the haem too: +1 or -1 for the same shape.

    ---- Helpers ----
    _instrument_fit_reader
    """

    instrument = _instrument_fit_reader(INSTRUMENT_FIT_FILE)
    theirs = instrument['shapes'][instrument['labels'].index(HAEM_TRACES[name])]
    fit = fit_importer(FIT_FILE)
    column = 2 * list(fit['haem_list']).index(name)
    ours = fit['data'].iloc[:, [column, column + 1]].dropna().to_numpy(dtype=float)
    ours = ours[np.argsort(ours[:, 0], kind='stable')]
    first = max(instrument['range_nm'][0], ours[0, 0])
    last = min(instrument['range_nm'][1], ours[-1, 0])
    inside = (theirs[:, 0] >= first) & (theirs[:, 0] <= last)
    assert inside.sum() > 100
    ours_there = np.interp(theirs[inside, 0], ours[:, 0], ours[:, 1])
    correlation = float(np.corrcoef(ours_there, theirs[inside, 1])[0, 1])
    assert abs(correlation) > SAME_SHAPE, (
        f"The {name} shape of our fit file is not the instrument's: the correlation "
        f'of the two is {correlation:+.4f} (+1 or -1 is the same shape).'
    )


# ---- test_instrument_traces_fall_when_reduced ----------------------------------------
@pytest.mark.parametrize('name', sorted(HAEM_TRACES))
def test_instrument_traces_fall_when_reduced(haems: dict, name: str) -> None:
    """
    ---- Summary ----
    Main function to check that the instrument's own trace of a haem is lower once
    dithionite has reduced it fully than it was with oxygen, before the first
    addition: down is reduced.

    ---- Inputs ----
    haems : dict
        Our amounts and the instrument's traces, from _haem_trace_loader.
    name : str
        Name of the haem in our fit file.

    ---- Globals read ----
    FIRST_ADDITION_SPECTRUM, DITHIONITE_SPECTRUM, WINDOW_SPECTRA (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    median of the last 2 min of the run (after the dithionite) - median of the 2 min
    before the first addition < 0.

    ---- Helpers ----
    None.
    """

    theirs = haems['theirs'][name]
    assert len(theirs) - WINDOW_SPECTRA > DITHIONITE_SPECTRUM
    first = FIRST_ADDITION_SPECTRUM - 1  # spectra are numbered from 1
    with_oxygen = float(np.nanmedian(theirs[first - WINDOW_SPECTRA:first]))
    reduced = float(np.nanmedian(theirs[-WINDOW_SPECTRA:]))
    assert reduced < with_oxygen, (
        f"The instrument's {name} trace is {reduced:.3f} after the dithionite and "
        f'{with_oxygen:.3f} before the first addition: it goes up when reduced.'
    )
