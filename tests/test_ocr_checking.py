"""
Tests that our OCR maths gives the values worked out by hand, and that the OCR check finds what it should.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.ocr_checking import (ocr_calculator,
                                       ocr_check_describer,
                                       ocr_checker,
                                       PART_LABELS,
                                       )


# ---- CONSTANTS -----------------------------------------------------------------------
STEP_S = 0.5  # time between two points, as in the instrument's recordings
PERMEABILITY = 0.1  # µM/min/mmHg
FALL_PER_MIN = 60.0  # the made-up oxygen falls by 1 µM/s
GAP_MMHG = 100.0  # outside minus chamber oxygen pressure
LEAK_PER_MIN = PERMEABILITY * GAP_MMHG  # 10 µM/min
PRESSURE_FACTOR = 0.75  # mmHg per µM
# points the instrument leaves empty: VrO2 at both ends, DgO2 and VoO2 at the start
FALL_EDGE_POINTS = 20
LEAK_START_POINTS = 60


# ---- HELPERS -------------------------------------------------------------------------


# ---- _instrument_maker ---------------------------------------------------------------
def _instrument_maker(n_points: int = 1000) -> Dict[str, np.ndarray]:
    """
    ---- Summary ----
    Helper function to make the traces of a recording whose rates were worked out
    exactly as our maths does.

    ---- Inputs ----
    n_points : int
        Points of the clock (0.5 s apart).

    ---- Globals read ----
    FALL_EDGE_POINTS, FALL_PER_MIN, GAP_MMHG, LEAK_PER_MIN, LEAK_START_POINTS,
    PRESSURE_FACTOR (module constants).

    ---- Outputs ----
    Dict[str, np.ndarray]
        CcO2, PcO2, PtO2, VrO2, DgO2 and VoO2, one value per point, NaN where the
        instrument leaves its rates empty.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    CcO2 = 600 - 0.5 j µM (1 µM/s, so a fall of 60 µM/min); PcO2 = 0.75 x CcO2;
    PtO2 = PcO2 + 100 mmHg; VrO2 = 60, DgO2 = 0.1 x 100 = 10 and VoO2 = 70 µM/min.

    ---- Helpers ----
    None.
    """

    rows = np.arange(n_points, dtype=float)
    oxygen = 600.0 - 0.5 * rows
    fall = np.full(n_points, FALL_PER_MIN)
    fall[:FALL_EDGE_POINTS] = np.nan
    fall[n_points - FALL_EDGE_POINTS:] = np.nan
    leak = np.full(n_points, LEAK_PER_MIN)
    leak[:LEAK_START_POINTS] = np.nan
    leak[n_points - FALL_EDGE_POINTS:] = np.nan
    return {'CcO2': oxygen,
            'PcO2': PRESSURE_FACTOR * oxygen,
            'PtO2': PRESSURE_FACTOR * oxygen + GAP_MMHG,
            'VrO2': fall,
            'DgO2': leak,
            'VoO2': fall + leak,
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_steady_fall_is_its_slope ---------------------------------------------------
def test_steady_fall_is_its_slope() -> None:
    """
    ---- Summary ----
    Main function to check that oxygen falling by 1 µM/s gives a fall of 60 µM/min,
    with no value for the 14 points at each end (29 points centred on each point).

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    0.5 µM every 0.5 s = 1 µM/s = 60 µM/min.

    ---- Helpers ----
    _instrument_maker
    """

    fall = ocr_calculator(_instrument_maker(), PERMEABILITY, STEP_S)['fall']
    assert np.all(np.isnan(fall[:14]))
    assert np.all(np.isnan(fall[-14:]))
    assert np.allclose(fall[14:-14], 60.0)


# ---- test_curved_fall_needs_29_points ------------------------------------------------
def test_curved_fall_needs_29_points() -> None:
    """
    ---- Summary ----
    Main function to check that oxygen curved as c x t^3 gives the slope of a straight
    line through exactly 29 points 0.5 s apart, so any other window length fails.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    For x = c t^3 around t0, the least-squares slope through the points t0 + k dt,
    k = -14 ... 14, is c (3 t0^2 + dt^2 sum(k^4) / sum(k^2)); sum(k^2) = 2030 and
    sum(k^4) = 255374, so the ratio is 125.8 and dt^2 x 125.8 = 31.45 s^2. With
    c = -0.001 µM/s^3 and t0 = 50 s (row 100): slope = -0.001 x (7500 + 31.45) =
    -7.53145 µM/s, so the fall is 60 x 7.53145 = 451.887 µM/min.

    ---- Helpers ----
    _instrument_maker
    """

    traces = _instrument_maker()
    seconds = np.arange(len(traces['CcO2'])) * STEP_S
    traces['CcO2'] = -0.001 * seconds ** 3
    fall = ocr_calculator(traces, PERMEABILITY, STEP_S)['fall']
    assert fall[100] == pytest.approx(451.887, rel=1e-9)


# ---- test_leak_is_permeability_times_gap ---------------------------------------------
def test_leak_is_permeability_times_gap() -> None:
    """
    ---- Summary ----
    Main function to check that a steady pressure gap of 100 mmHg through a wall of
    permeability 0.1 µM/min/mmHg gives a leak of 10 µM/min, with no value for the
    first 39 points, and that our OCR is the fall plus the leak.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    leak = 0.1 x 100 = 10 µM/min; OCR = 60 + 10 = 70 µM/min.

    ---- Helpers ----
    _instrument_maker
    """

    ours = ocr_calculator(_instrument_maker(), PERMEABILITY, STEP_S)
    assert np.all(np.isnan(ours['leak'][:39]))
    assert np.allclose(ours['leak'][39:], 10.0)
    assert np.allclose(ours['ocr'][39:-14], 70.0)


# ---- test_leak_window_is_40_points ---------------------------------------------------
def test_leak_window_is_40_points() -> None:
    """
    ---- Summary ----
    Main function to check that a step in the pressure gap reaches its full size in
    the leak after exactly 40 points, the mean ending at each point.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Gap 0 before row 100 and 100 mmHg from it: leak[99] = 0; leak[100] = 0.1 x 100 x
    1/40 = 0.25; leak[138] = 0.1 x 100 x 39/40 = 9.75; leak[139] = 10 µM/min.

    ---- Helpers ----
    _instrument_maker
    """

    traces = _instrument_maker()
    traces['PtO2'] = traces['PcO2'].copy()
    traces['PtO2'][100:] += 100.0
    leak = ocr_calculator(traces, PERMEABILITY, STEP_S)['leak']
    assert leak[99] == pytest.approx(0.0, abs=1e-9)
    assert leak[100] == pytest.approx(0.25)
    assert leak[138] == pytest.approx(9.75)
    assert leak[139] == pytest.approx(10.0)


# ---- test_agreeing_traces_pass -------------------------------------------------------
def test_agreeing_traces_pass() -> None:
    """
    ---- Summary ----
    Main function to check that a recording worked out as we expect is checked, agrees
    in every part, finds the pressure factor and gives no message.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, PRESSURE_FACTOR, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _instrument_maker
    """

    check = ocr_checker(_instrument_maker(), PERMEABILITY, [], STEP_S)
    assert check['is_checked']
    assert check['is_agreeing']
    assert all(part['is_agreeing'] for part in check['parts'].values())
    assert check['pressure_factor'] == pytest.approx(PRESSURE_FACTOR)
    assert ocr_check_describer(check, 'run1.paf') == ''


# ---- test_wrong_sum_is_caught --------------------------------------------------------
def test_wrong_sum_is_caught() -> None:
    """
    ---- Summary ----
    Main function to check that an OCR 5 µM/min above the fall plus the leak is caught,
    and that the message names that part only.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _instrument_maker
    """

    traces = _instrument_maker()
    traces['VoO2'] = traces['VoO2'] + 5.0
    check = ocr_checker(traces, PERMEABILITY, [], STEP_S)
    disagreeing = [name for name, part in check['parts'].items()
                   if not part['is_agreeing']
                   ]
    assert check['is_checked'] and not check['is_agreeing']
    assert disagreeing == ['sum']
    assert check['parts']['sum']['difference'] == pytest.approx(5.0)
    message = ocr_check_describer(check, 'run1.paf')
    assert message.startswith('run1.paf: ')
    assert PART_LABELS['sum'] in message
    # a per is a power of -1 in the sentence, never a slash
    assert '(off by 5 µM min⁻¹, 0.001 µM min⁻¹ allowed)' in message
    assert 'µM/min' not in message


# ---- test_wrong_leak_is_caught -------------------------------------------------------
def test_wrong_leak_is_caught() -> None:
    """
    ---- Summary ----
    Main function to check that a leak twice ours (as from a permeability twice the
    one stored) is caught in its typical difference and in its size, and named.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The instrument's leak is 20 µM/min against our 10: typical difference 10 µM/min,
    size 100 % off. Its OCR is still its fall plus its leak.

    ---- Helpers ----
    _instrument_maker
    """

    traces = _instrument_maker()
    traces['DgO2'] = traces['DgO2'] * 2.0
    traces['VoO2'] = traces['VrO2'] + traces['DgO2']
    check = ocr_checker(traces, PERMEABILITY, [], STEP_S)
    disagreeing = [name for name, part in check['parts'].items()
                   if not part['is_agreeing']
                   ]
    assert disagreeing == ['leak', 'leak_size']
    assert check['parts']['leak']['difference'] == pytest.approx(10.0)
    assert check['parts']['leak_size']['difference'] == pytest.approx(100.0)
    assert PART_LABELS['leak'] in ocr_check_describer(check, 'run1.paf')


# ---- test_addition_stretch_is_left_out -----------------------------------------------
def test_addition_stretch_is_left_out() -> None:
    """
    ---- Summary ----
    Main function to check that a large spike in the instrument's fall next to an
    addition is left out of the comparison, and is caught when no addition is there.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The spike adds 5000 µM/min to rows 490 to 510. Without the addition at row 500,
    the 960 compared points give a factor of 1 + 21 x 5000 / (60 x 960) = 2.82, so
    the size is 182 % off.

    ---- Helpers ----
    _instrument_maker
    """

    traces = _instrument_maker()
    traces['VrO2'][490:511] += 5000.0
    traces['VoO2'] = traces['VrO2'] + traces['DgO2']
    assert ocr_checker(traces, PERMEABILITY, [500], STEP_S)['is_agreeing']
    check = ocr_checker(traces, PERMEABILITY, [], STEP_S)
    assert not check['parts']['fall_size']['is_agreeing']
    assert check['parts']['fall_size']['difference'] == pytest.approx(182.29, abs=0.01)


# ---- test_missing_trace_is_not_checked -----------------------------------------------
def test_missing_trace_is_not_checked() -> None:
    """
    ---- Summary ----
    Main function to check that a file without the outside oxygen pressure, or without
    the wall's permeability, is not checked, and that the message says why.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _instrument_maker
    """

    traces = _instrument_maker()
    traces['PtO2'] = None
    check = ocr_checker(traces, PERMEABILITY, [], STEP_S)
    assert not check['is_checked'] and not check['is_agreeing']
    assert check['reason'] == 'the file has no PtO2 trace'
    message = ocr_check_describer(check, 'run1.paf')
    assert 'could not be checked' in message and 'PtO2' in message
    check = ocr_checker(_instrument_maker(), None, [], STEP_S)
    assert not check['is_checked']
    assert 'permeability' in check['reason']


# ---- test_short_recording_is_not_checked ---------------------------------------------
def test_short_recording_is_not_checked() -> None:
    """
    ---- Summary ----
    Main function to check that a recording too short to compare is not checked.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PERMEABILITY, STEP_S (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    150 points: the instrument's OCR has values at rows 60 to 129 only, 70 points,
    fewer than the 100 needed.

    ---- Helpers ----
    _instrument_maker
    """

    check = ocr_checker(_instrument_maker(150), PERMEABILITY, [], STEP_S)
    assert not check['is_checked']
    assert check['reason'] == 'the recording is too short to compare'
