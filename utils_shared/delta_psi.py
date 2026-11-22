"""
The maths of delta psi, the membrane potential, from how reduced the two b haems (bH
and bL) are.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import HAEM_NAME_PREFIXES, name_simplifier
from utils_shared.schema import (measurement_column_finder,
                                 SPECTRUM_INDEX_COLUMN,
                                 TIME_COLUMN,
                                 value_getter,
                                 )


# ---- CONSTANTS -----------------------------------------------------------------------
# The method is that of Kim, Ripple and Springett, Biophys J 2012, 102:1194-1203
# (doi 10.1016/j.bpj.2012.02.003), "Equilibrium measurement of membrane potential".
# The four midpoint potentials of the method: each haem's with the other haem oxidised
# (its first electron) and with the other haem reduced (its second electron).
MIDPOINT_KEYS = ('bH_first', 'bL_first', 'bH_second', 'bL_second')
GAS_CONSTANT_J_PER_MOL_K = 8.314462618
FARADAY_C_PER_MOL = 96485.33212
ZERO_CELSIUS_K = 273.15
# The two haems by their simplified names, without "Cyt" or "haem" in front.
BH_NAME = 'bh'
BL_NAME = 'bl'
# The columns of the table of results.
DELTA_PSI_COLUMN = 'Δψ (mV)'
BH_POTENTIAL_COLUMN = 'Eh bH (mV)'
BL_POTENTIAL_COLUMN = 'Eh bL (mV)'
# how far the two drops of the midpoints may differ and still count as equal (mV)
MIDPOINT_TOLERANCE_MV = 1e-6


# ---- DELTA PSI HELPERS ---------------------------------------------------------------


# ---- _settings_validator -------------------------------------------------------------
def _settings_validator(midpoints_mV: Dict[str, float],
                        share: float,
                        temperature_c: float,
                        limits_percent: Sequence[float],
                        ) -> None:
    """
    ---- Summary ----
    Helper function to refuse numbers of the method that would give a wrong delta psi,
    each with a plain sentence saying what to change.

    ---- Inputs ----
    midpoints_mV : Dict[str, float]
        {bH_first, bL_first, bH_second, bL_second}: the midpoint potentials (mV).
    share : float
        Share of the membrane potential between the two haems (0.5 is half).
    temperature_c : float
        Temperature of the sample (°C).
    limits_percent : Sequence[float]
        (lowest, highest) % reduced at which delta psi is still given.

    ---- Globals read ----
    MIDPOINT_KEYS, MIDPOINT_TOLERANCE_MV, ZERO_CELSIUS_K.

    ---- Outputs ----
    None
        Nothing. Raises ValueError for a missing or blank midpoint, two drops that
        differ, a share not above 0, a temperature at or below absolute zero, and
        limits that are not 0 < lowest < highest < 100.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    bH_first - bH_second must equal bL_first - bL_second: both are the push of one
    electron on the other, so the two orders of filling the haems cost the same.

    ---- Helpers ----
    None.
    """

    # ---- 1 The four midpoints --------------------------------------------------------
    missing = [key for key in MIDPOINT_KEYS
               if key not in midpoints_mV or not np.isfinite(float(midpoints_mV[key]))
               ]
    if missing:
        raise ValueError(f"Δψ needs the four midpoint potentials of bH and bL, and "
                         f"{', '.join(missing)} has no number. Give each a number in "
                         f'mV.',
                         )
    drop_bH = float(midpoints_mV['bH_first']) - float(midpoints_mV['bH_second'])
    drop_bL = float(midpoints_mV['bL_first']) - float(midpoints_mV['bL_second'])
    if abs(drop_bH - drop_bL) > MIDPOINT_TOLERANCE_MV:
        raise ValueError(f'The midpoint of bH drops by {drop_bH:g} mV when bL is '
                         f'reduced and that of bL by {drop_bL:g} mV when bH is '
                         f'reduced. The two drops must be the same; change the '
                         f'midpoint potentials so that they are.',
                         )

    # ---- 2 The share, the temperature and the limits ---------------------------------
    if not np.isfinite(share) or share <= 0:
        raise ValueError(f'The share of the membrane potential between bH and bL is '
                         f'{share:g}. It must be above 0 (0.5 is half).',
                         )
    if not np.isfinite(temperature_c) or temperature_c <= -ZERO_CELSIUS_K:
        raise ValueError(f'The temperature is {temperature_c:g} °C. It must be above '
                         f'{-ZERO_CELSIUS_K:g} °C; 37 is the usual one.',
                         )
    lowest, highest = (float(limit) for limit in limits_percent)
    if not 0 < lowest < highest < 100:
        raise ValueError(f'Δψ is given between {lowest:g} and {highest:g} % reduced. '
                         f'The first must be above 0, the second below 100 and above '
                         f'the first.',
                         )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- b_haem_column_finder ------------------------------------------------------------
def b_haem_column_finder(haem_table: pd.DataFrame) -> Optional[Tuple[str, str]]:
    """
    ---- Summary ----
    Main function to find the bH and the bL column of a haem table by their names,
    however they are written ("Cyt $b_H$", "cyt bH", "bH").

    ---- Inputs ----
    haem_table : pd.DataFrame
        Haem table (time, spectrum index and one column per haem).

    ---- Globals read ----
    BH_NAME, BL_NAME; HAEM_NAME_PREFIXES.

    ---- Outputs ----
    Optional[Tuple[str, str]]
        (bH column, bL column), or None when the table does not have exactly one of
        each, so delta psi cannot be worked out from it.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    measurement_column_finder
    name_simplifier
    """

    found: Dict[str, list] = {BH_NAME: [], BL_NAME: []}
    for column in measurement_column_finder(haem_table):
        simple = name_simplifier(column)
        for prefix in HAEM_NAME_PREFIXES:
            if simple.startswith(prefix):
                simple = simple[len(prefix):]
                break
        if simple in found:
            found[simple].append(column)
    if len(found[BH_NAME]) != 1 or len(found[BL_NAME]) != 1:
        return None
    return found[BH_NAME][0], found[BL_NAME][0]


# ---- delta_psi_calculator ------------------------------------------------------------
def delta_psi_calculator(percent_bH: Sequence[float],
                         percent_bL: Sequence[float],
                         midpoints_mV: Dict[str, float],
                         share: float,
                         temperature_c: float,
                         limits_percent: Sequence[float],
                         ) -> Dict[str, np.ndarray]:
    """
    ---- Summary ----
    Main function to work out delta psi, and the redox potential at each of the two
    b haems, from their % oxidised in every spectrum.

    ---- Inputs ----
    percent_bH : Sequence[float]
        % oxidised of bH, shape (n_spectra,).
    percent_bL : Sequence[float]
        % oxidised of bL, shape (n_spectra,).
    midpoints_mV : Dict[str, float]
        {bH_first, bL_first, bH_second, bL_second}: the midpoint potential of each
        haem with the other oxidised (first) and with the other reduced (second), mV.
    share : float
        Share of the membrane potential that lies between the two haems (0.5 is half).
    temperature_c : float
        Temperature of the sample (°C).
    limits_percent : Sequence[float]
        (lowest, highest) % reduced of a haem at which delta psi is still given.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, np.ndarray]
        {'delta_psi', 'potential_bH', 'potential_bL'}: mV, each of shape (n_spectra,),
        float64. All three are NaN in a spectrum where bH or bL is blank, or less
        reduced than the lowest limit, or more reduced than the highest. Raises
        ValueError for numbers of the method that cannot be used (_settings_validator)
        and for two haems of different lengths.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    R_H = 1 - P_H / 100; R_L = 1 - P_L / 100 (fractions reduced).
    s = R x T / F (mV); k = exp(-(bH_first - bH_second) / s).
    n, h, l, b: state_fractions_solver.
    E_H = bH_first - s x ln(h / n); E_L = bL_first - s x ln(l / n).
    delta psi = (E_H - E_L) / share.

    ---- Helpers ----
    _settings_validator
    state_fractions_solver
    thermal_voltage_finder
    """

    # ---- 1 Check the numbers of the method -------------------------------------------
    _settings_validator(midpoints_mV, share, temperature_c, limits_percent)
    reduced_bH = 1.0 - np.asarray(percent_bH, dtype=float) / 100.0
    reduced_bL = 1.0 - np.asarray(percent_bL, dtype=float) / 100.0
    if reduced_bH.shape != reduced_bL.shape:
        raise ValueError('bH and bL do not have the same number of spectra, so Δψ '
                         'cannot be worked out. This is a fault in the program; '
                         'please report it.',
                         )

    # ---- 2 Leave out the spectra outside the limits ----------------------------------
    # Compared in %, so that a haem exactly at a limit (90 % oxidised) is kept.
    lowest, highest = (float(limit) for limit in limits_percent)
    reduced_percent_bH = 100.0 - np.asarray(percent_bH, dtype=float)
    reduced_percent_bL = 100.0 - np.asarray(percent_bL, dtype=float)
    with np.errstate(invalid='ignore'):
        usable = ((reduced_percent_bH >= lowest) & (reduced_percent_bH <= highest) &
                  (reduced_percent_bL >= lowest) & (reduced_percent_bL <= highest)
                  )
    result = {key: np.full(reduced_bH.shape, np.nan)
              for key in ('delta_psi', 'potential_bH', 'potential_bL')
              }
    if not usable.any():
        return result

    # ---- 3 The four states of the pair of haems --------------------------------------
    thermal_mV = thermal_voltage_finder(temperature_c)
    drop_mV = float(midpoints_mV['bH_first']) - float(midpoints_mV['bH_second'])
    factor = float(np.exp(-drop_mV / thermal_mV))
    neither, only_bH, only_bL, _ = state_fractions_solver(reduced_bH[usable],
                                                          reduced_bL[usable],
                                                          factor,
                                                          )

    # ---- 4 The potential at each haem, and delta psi ---------------------------------
    potential_bH = (float(midpoints_mV['bH_first']) -
                    thermal_mV * np.log(only_bH / neither)
                    )
    potential_bL = (float(midpoints_mV['bL_first']) -
                    thermal_mV * np.log(only_bL / neither)
                    )
    result['potential_bH'][usable] = potential_bH
    result['potential_bL'][usable] = potential_bL
    result['delta_psi'][usable] = (potential_bH - potential_bL) / float(share)
    return result


# ---- delta_psi_table_builder ---------------------------------------------------------
def delta_psi_table_builder(haem_percent: pd.DataFrame,
                            midpoints_mV: Dict[str, float],
                            share: float,
                            temperature_c: float,
                            limits_percent: Sequence[float],
                            ) -> Optional[pd.DataFrame]:
    """
    ---- Summary ----
    Main function to build the delta psi table of a file from its % oxidised table.

    ---- Inputs ----
    haem_percent : pd.DataFrame
        % oxidised table of the file (time, spectrum index and one column per haem).
    midpoints_mV : Dict[str, float]
        The four midpoint potentials (mV); see delta_psi_calculator.
    share : float
        Share of the membrane potential between the two haems.
    temperature_c : float
        Temperature of the sample (°C).
    limits_percent : Sequence[float]
        (lowest, highest) % reduced at which delta psi is still given.

    ---- Globals read ----
    DELTA_PSI_COLUMN, BH_POTENTIAL_COLUMN, BL_POTENTIAL_COLUMN; TIME_COLUMN,
    SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    Optional[pd.DataFrame]
        The time and spectrum index of the % table, then delta psi and the potential
        at bH and at bL (mV), one row per spectrum; or None when the table does not
        have one bH and one bL. table.attrs['delta_psi'] holds the numbers used:
        {'midpoints_mV', 'share', 'temperature_c', 'limits_percent', 'bH', 'bL' (the
        two columns), 'spectra_with_value'}. Raises ValueError as
        delta_psi_calculator does.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    delta_psi_calculator.

    ---- Helpers ----
    b_haem_column_finder
    delta_psi_calculator
    value_getter
    """

    columns = b_haem_column_finder(haem_percent)
    if columns is None:
        return None
    column_bH, column_bL = columns
    values = delta_psi_calculator(value_getter(haem_percent, column_bH),
                                  value_getter(haem_percent, column_bL),
                                  midpoints_mV,
                                  share,
                                  temperature_c,
                                  limits_percent,
                                  )
    kept = [column for column in (TIME_COLUMN, SPECTRUM_INDEX_COLUMN)
            if column in haem_percent.columns
            ]
    table = haem_percent[kept].copy()
    table.attrs = {}
    table[DELTA_PSI_COLUMN] = values['delta_psi']
    table[BH_POTENTIAL_COLUMN] = values['potential_bH']
    table[BL_POTENTIAL_COLUMN] = values['potential_bL']
    table.attrs['delta_psi'] = {
        'midpoints_mV': {key: float(value) for key, value in midpoints_mV.items()},
        'share': float(share),
        'temperature_c': float(temperature_c),
        'limits_percent': tuple(float(limit) for limit in limits_percent),
        'bH': str(column_bH),
        'bL': str(column_bL),
        'spectra_with_value': int(np.isfinite(values['delta_psi']).sum()),
        }
    return table


# ---- state_fractions_solver ----------------------------------------------------------
def state_fractions_solver(reduced_bH: Sequence[float],
                           reduced_bL: Sequence[float],
                           factor: float,
                           ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Main function to split the pair of b haems into its four states (neither reduced,
    only bH, only bL, both) from how reduced each haem is.

    ---- Inputs ----
    reduced_bH : Sequence[float]
        Fraction of bH that is reduced, above 0 and below 1, shape (n,).
    reduced_bL : Sequence[float]
        Fraction of bL that is reduced, above 0 and below 1, shape (n,).
    factor : float
        k, how much rarer "both reduced" is made by the push of one electron on the
        other (1 for no push), above 0.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        (n, h, l, b): the fractions of the pairs with neither haem reduced, only bH,
        only bL and both, each of shape (n,), adding up to 1.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    R_H = h + b; R_L = l + b; n + h + l + b = 1; (b x n) / (h x l) = k. Together:
    (1 - k) b^2 + B b - k R_H R_L = 0 with B = 1 - (1 - k)(R_H + R_L), whose one
    answer between 0 and the smaller of R_H and R_L is
    b = 2 k R_H R_L / (B + sqrt(B^2 + 4 (1 - k) k R_H R_L)).
    Then h = R_H - b, l = R_L - b, n = 1 - R_H - R_L + b.

    ---- Helpers ----
    None.
    """

    reduced_bH = np.asarray(reduced_bH, dtype=float)
    reduced_bL = np.asarray(reduced_bL, dtype=float)
    product = factor * reduced_bH * reduced_bL
    middle = 1.0 - (1.0 - factor) * (reduced_bH + reduced_bL)
    both = 2.0 * product / (middle + np.sqrt(middle**2 + 4.0 * (1.0 - factor) * product))
    only_bH = reduced_bH - both
    only_bL = reduced_bL - both
    neither = 1.0 - reduced_bH - reduced_bL + both
    return neither, only_bH, only_bL, both


# ---- thermal_voltage_finder ----------------------------------------------------------
def thermal_voltage_finder(temperature_c: float) -> float:
    """
    ---- Summary ----
    Main function to give s = R x T / F, the voltage that goes with a temperature, in
    mV (26.7 mV at 37 °C).

    ---- Inputs ----
    temperature_c : float
        Temperature (°C), above absolute zero.

    ---- Globals read ----
    GAS_CONSTANT_J_PER_MOL_K, FARADAY_C_PER_MOL, ZERO_CELSIUS_K.

    ---- Outputs ----
    float
        s (mV).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    s = R x (temperature + 273.15) / F x 1000.

    ---- Helpers ----
    None.
    """

    kelvin = float(temperature_c) + ZERO_CELSIUS_K
    return GAS_CONSTANT_J_PER_MOL_K * kelvin / FARADAY_C_PER_MOL * 1000.0
