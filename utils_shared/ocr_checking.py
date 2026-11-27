"""
Checks the instrument's oxygen consumption rate (OCR) against our own calculation from its oxygen traces.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, Mapping, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np


# ---- CONSTANTS -----------------------------------------------------------------------
# the traces the check needs, one value per point of the clock
OCR_TRACES = ('CcO2', 'PcO2', 'PtO2', 'VrO2', 'DgO2', 'VoO2')

# our recipe (DATA_FORMAT.md, "Our OCR check"); a change here changes the fixed values
# in tests/test_paf_reading.py, which are then rewritten on purpose
FALL_POINTS = 29  # straight line through this many points centred on each point
LEAK_POINTS = 40  # mean of the pressure gap over this many points ending at each point
SECONDS_PER_MINUTE = 60.0

# how the instrument's numbers are compared with ours
ADDITION_POINTS = 30  # points left out on each side of an addition (15 s at 0.5 s)
MIN_COMPARED_POINTS = 100  # fewer points than this cannot be compared

# part -> (largest allowed difference, unit); set from the 33 sample files on
# 2026-11-20, about three times the worst seen (sum and pressure 0.0001, typical fall
# 0.87 and leak 0.55 µM/min, size of the fall 11 % and of the leak 1.6 %)
MARGINS = {'sum': (0.001, 'µM min⁻¹'),
           'pressure': (0.001, 'mmHg'),
           'fall': (3.0, 'µM min⁻¹'),
           'fall_size': (35.0, '%'),
           'leak': (2.0, 'µM min⁻¹'),
           'leak_size': (5.0, '%'),
           }
# part -> what a disagreement means, for the warning
PART_LABELS = {'sum': "the instrument's OCR is not its fall of oxygen plus its leak",
               'pressure': ('the chamber oxygen pressure does not follow the measured '
                            'oxygen by one fixed factor'
                            ),
               'fall': "the instrument's fall of the measured oxygen differs from ours",
               'fall_size': ("the instrument's fall of the measured oxygen is not the "
                             'same size as ours'
                             ),
               'leak': ("the instrument's oxygen leak through the chamber wall differs "
                        'from ours'
                        ),
               'leak_size': ("the instrument's oxygen leak through the chamber wall is "
                             'not the same size as ours'
                             ),
               }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _agreement_finder ---------------------------------------------------------------
def _agreement_finder(instrument: np.ndarray,
                      ours: np.ndarray,
                      addition_rows: Sequence[int],
                      ) -> Optional[Tuple[float, float]]:
    """
    ---- Summary ----
    Helper function to measure how closely the instrument's rate follows ours away
    from the additions: the typical difference and the difference in overall size.

    ---- Inputs ----
    instrument : np.ndarray
        The instrument's rate, one value per point of the clock (µM/min), NaN where it
        has none.
    ours : np.ndarray
        Our rate on the same points (µM/min), NaN where we have none.
    addition_rows : Sequence[int]
        Row of the clock of each addition (0 = first point).

    ---- Globals read ----
    ADDITION_POINTS, MIN_COMPARED_POINTS (module constants).

    ---- Outputs ----
    Optional[Tuple[float, float]]
        (typical difference in µM/min, difference in size in %), or None when fewer
        than MIN_COMPARED_POINTS can be compared or our rate is zero throughout.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Compared points: both rates have a value and the point is more than
    ADDITION_POINTS away from every addition. Over them:
        typical difference = median of |instrument - ours|
        factor = sum(instrument x ours) / sum(ours^2) (least squares through zero)
        difference in size = |factor - 1| x 100 %.

    ---- Helpers ----
    None.
    """

    is_compared = np.isfinite(instrument) & np.isfinite(ours)
    for row in addition_rows:
        is_compared[max(0, row - ADDITION_POINTS):row + ADDITION_POINTS + 1] = False
    theirs, mine = instrument[is_compared], ours[is_compared]
    size = float(mine @ mine)
    if len(mine) < MIN_COMPARED_POINTS or size == 0.0:
        return None
    factor = float(theirs @ mine) / size
    return float(np.median(np.abs(theirs - mine))), abs(factor - 1.0) * 100.0


# ---- _leak_finder --------------------------------------------------------------------
def _leak_finder(outside_mmHg: np.ndarray,
                 chamber_mmHg: np.ndarray,
                 permeability: float,
                 ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to work out the oxygen leaking into the chamber through its wall.

    ---- Inputs ----
    outside_mmHg : np.ndarray
        Oxygen pressure outside the chamber wall (PtO2, mmHg), one value per point.
    chamber_mmHg : np.ndarray
        Oxygen pressure in the chamber (PcO2, mmHg), on the same points.
    permeability : float
        Oxygen permeability of the chamber wall (µM/min/mmHg), as stored in the file.

    ---- Globals read ----
    LEAK_POINTS (module constant).

    ---- Outputs ----
    np.ndarray
        Leak (µM/min), one value per point; NaN for the first LEAK_POINTS - 1 points.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    leak[j] = permeability x mean of (PtO2 - PcO2)[j - 39 ... j] (40 points, 20 s at
    0.5 s, ending at the point itself).

    ---- Helpers ----
    None.
    """

    gap = np.asarray(outside_mmHg, dtype=float) - np.asarray(chamber_mmHg, dtype=float)
    leak = np.full(len(gap), np.nan)
    if len(gap) >= LEAK_POINTS:
        means = np.convolve(gap, np.ones(LEAK_POINTS) / LEAK_POINTS, mode='valid')
        leak[LEAK_POINTS - 1:] = permeability * means
    return leak


# ---- _oxygen_fall_finder -------------------------------------------------------------
def _oxygen_fall_finder(oxygen_uM: np.ndarray, step_s: float) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to work out how fast the measured oxygen falls at each point.

    ---- Inputs ----
    oxygen_uM : np.ndarray
        Measured oxygen (CcO2, µM), one value per point of the clock.
    step_s : float
        Time between two points (s).

    ---- Globals read ----
    FALL_POINTS, SECONDS_PER_MINUTE (module constants).

    ---- Outputs ----
    np.ndarray
        Fall (µM/min, positive when the oxygen goes down), one value per point; NaN for
        the first and last FALL_POINTS // 2 points.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The slope of the least-squares straight line through the 29 points centred on
    point j:
        fall[j] = -60 x sum(k x CcO2[j + k]) / (step_s x sum(k^2)), k = -14 ... 14,
        sum(k^2) = 2030.

    ---- Helpers ----
    None.
    """

    oxygen_uM = np.asarray(oxygen_uM, dtype=float)
    half = FALL_POINTS // 2
    k = np.arange(-half, half + 1, dtype=float)
    weights = -SECONDS_PER_MINUTE * k / (step_s * float(k @ k))
    fall = np.full(len(oxygen_uM), np.nan)
    if len(oxygen_uM) >= FALL_POINTS:
        # correlate gives sum over n of oxygen[i + n] x weights[n], centred at i + half
        fall[half:len(oxygen_uM) - half] = np.correlate(oxygen_uM,
                                                        weights,
                                                        mode='valid',
                                                        )
    return fall


# ---- _pressure_factor_finder ---------------------------------------------------------
def _pressure_factor_finder(oxygen_uM: np.ndarray,
                            chamber_mmHg: np.ndarray,
                            ) -> Tuple[Optional[float], Optional[float]]:
    """
    ---- Summary ----
    Helper function to find the fixed factor between the measured oxygen and the
    chamber oxygen pressure, and how far the pressure strays from it.

    ---- Inputs ----
    oxygen_uM : np.ndarray
        Measured oxygen (CcO2, µM), one value per point.
    chamber_mmHg : np.ndarray
        Oxygen pressure in the chamber (PcO2, mmHg), on the same points.

    ---- Globals read ----
    MIN_COMPARED_POINTS (module constant).

    ---- Outputs ----
    Tuple[Optional[float], Optional[float]]
        (factor in mmHg/µM, largest |PcO2 - factor x CcO2| in mmHg), or (None, None)
        when fewer than MIN_COMPARED_POINTS points have both values or the oxygen is
        zero throughout.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    factor = sum(CcO2 x PcO2) / sum(CcO2^2) (least squares through zero).

    ---- Helpers ----
    None.
    """

    is_usable = np.isfinite(oxygen_uM) & np.isfinite(chamber_mmHg)
    oxygen, pressure = oxygen_uM[is_usable], chamber_mmHg[is_usable]
    size = float(oxygen @ oxygen)
    if len(oxygen) < MIN_COMPARED_POINTS or size == 0.0:
        return None, None
    factor = float(oxygen @ pressure) / size
    return factor, float(np.abs(pressure - factor * oxygen).max())


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- ocr_calculator ------------------------------------------------------------------
def ocr_calculator(traces: Mapping[str, np.ndarray],
                   permeability: float,
                   step_s: float,
                   ) -> Dict[str, np.ndarray]:
    """
    ---- Summary ----
    Main function to work out our own OCR from the instrument's oxygen traces.

    ---- Inputs ----
    traces : Mapping[str, np.ndarray]
        At least 'CcO2' (µM), 'PcO2' and 'PtO2' (mmHg), one value per point of the
        clock, NaN where the file has none.
    permeability : float
        Oxygen permeability of the chamber wall (µM/min/mmHg), as stored in the file.
    step_s : float
        Time between two points (s).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, np.ndarray]
        {'fall': fall of the measured oxygen, 'leak': oxygen leaking in, 'ocr': their
        sum}, each in µM/min with one value per point, NaN where it cannot be worked
        out.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    our OCR = fall + leak (see _oxygen_fall_finder and _leak_finder; written out in
    DATA_FORMAT.md, "Our OCR check").

    ---- Helpers ----
    _leak_finder
    _oxygen_fall_finder
    """

    fall = _oxygen_fall_finder(traces['CcO2'], step_s)
    leak = _leak_finder(traces['PtO2'], traces['PcO2'], permeability)
    return {'fall': fall, 'leak': leak, 'ocr': fall + leak}


# ---- ocr_check_describer -------------------------------------------------------------
def ocr_check_describer(check: dict, file_name: str) -> str:
    """
    ---- Summary ----
    Main function to say in plain words what the OCR check of one file found.

    ---- Inputs ----
    check : dict
        Result of ocr_checker (ocr_check in DATA_FORMAT.md).
    file_name : str
        Name of the file, written first.

    ---- Globals read ----
    PART_LABELS (module constant).

    ---- Outputs ----
    str
        An empty string when the instrument's OCR agrees with ours; otherwise one
        sentence saying which parts disagree, or why the file could not be checked.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not check['is_checked']:
        return (f"{file_name}: the instrument's OCR could not be checked against our "
                f"own calculation, because {check['reason']}. The figures use it as "
                f'it is.'
                )
    if check['is_agreeing']:
        return ''
    details = [f"{PART_LABELS[name]} (off by {part['difference']:.3g} "
               f"{part['unit']}, {part['margin']:g} {part['unit']} allowed)"
               for name, part in check['parts'].items()
               if not part['is_agreeing']
               ]
    return (f"{file_name}: the instrument's OCR does not agree with our own calculation "
            f"from its oxygen traces: {'; '.join(details)}. The figures still use the "
            f"instrument's OCR, so look at this run in the instrument software before "
            f'relying on it.'
            )


# ---- ocr_checker ---------------------------------------------------------------------
def ocr_checker(traces: Mapping[str, Optional[np.ndarray]],
                permeability: Optional[float],
                addition_rows: Sequence[int],
                step_s: float,
                ) -> dict:
    """
    ---- Summary ----
    Main function to check that the instrument worked out its OCR as we expect, from
    its own oxygen traces.

    ---- Inputs ----
    traces : Mapping[str, Optional[np.ndarray]]
        The traces of OCR_TRACES, one value per point of the clock (NaN where the file
        has none); a trace the file lacks is None or left out.
    permeability : Optional[float]
        Oxygen permeability of the chamber wall (µM/min/mmHg) from the file, or None
        when the file does not store it.
    addition_rows : Sequence[int]
        Row of the clock of each addition (0 = first point).
    step_s : float
        Time between two points (s).

    ---- Globals read ----
    MARGINS, OCR_TRACES (module constants).

    ---- Outputs ----
    dict
        ocr_check (DATA_FORMAT.md): 'is_checked', 'is_agreeing', 'reason' (why it was
        not checked, else empty), 'permeability', 'pressure_factor' and 'parts' (for
        each key of MARGINS: 'difference', 'margin', 'unit' and 'is_agreeing').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    sum: largest |VoO2 - (VrO2 + DgO2)|.
    pressure: largest |PcO2 - factor x CcO2|.
    fall and leak: the typical difference, and the difference in size (%), of the
    instrument's VrO2 and DgO2 from ours, away from the additions (_agreement_finder).
    Each part agrees when its difference is at most its margin.

    ---- Helpers ----
    _agreement_finder
    _pressure_factor_finder
    ocr_calculator
    """

    # ---- 1 Look for what is missing --------------------------------------------------
    result = {'is_checked': False,
              'is_agreeing': False,
              'reason': '',
              'permeability': permeability,
              'pressure_factor': None,
              'parts': {},
              }
    missing = [name for name in OCR_TRACES if traces.get(name) is None]
    if missing:
        result['reason'] = (f"the file has no {' and '.join(missing)} "
                            f"trace{'s' if len(missing) > 1 else ''}"
                            )
        return result
    if permeability is None:
        result['reason'] = ('the file does not store the oxygen permeability of the '
                            'chamber wall'
                            )
        return result
    data = {name: np.asarray(traces[name], dtype=float) for name in OCR_TRACES}

    # ---- 2 Work out ours and compare -------------------------------------------------
    ours = ocr_calculator(data, permeability, step_s)
    is_summed = (np.isfinite(data['VoO2'])
                 & np.isfinite(data['VrO2'])
                 & np.isfinite(data['DgO2'])
                 )
    factor, pressure_gap = _pressure_factor_finder(data['CcO2'], data['PcO2'])
    summed_gap = (float(np.abs(data['VoO2'][is_summed]
                               - data['VrO2'][is_summed]
                               - data['DgO2'][is_summed],
                               ).max(),
                        )
                  if np.count_nonzero(is_summed) >= MIN_COMPARED_POINTS
                  else None
                  )
    fall = _agreement_finder(data['VrO2'], ours['fall'], addition_rows)
    leak = _agreement_finder(data['DgO2'], ours['leak'], addition_rows)
    if None in (summed_gap, pressure_gap, fall, leak):
        result['reason'] = 'the recording is too short to compare'
        return result
    differences = {'sum': summed_gap,
                   'pressure': pressure_gap,
                   'fall': fall[0],
                   'fall_size': fall[1],
                   'leak': leak[0],
                   'leak_size': leak[1],
                   }

    # ---- 3 Judge each part -----------------------------------------------------------
    for name, difference in differences.items():
        margin, unit = MARGINS[name]
        result['parts'][name] = {'difference': difference,
                                 'margin': margin,
                                 'unit': unit,
                                 'is_agreeing': difference <= margin,
                                 }
    result['is_checked'] = True
    result['is_agreeing'] = all(part['is_agreeing']
                                for part in result['parts'].values()
                                )
    result['pressure_factor'] = factor
    return result
