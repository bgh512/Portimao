"""
Tests that delta psi from the b haems comes out as worked out by hand on made-up data.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared import experiment_processing
from utils_shared.delta_psi import (b_haem_column_finder,
                                    BH_POTENTIAL_COLUMN,
                                    BL_POTENTIAL_COLUMN,
                                    DELTA_PSI_COLUMN,
                                    delta_psi_calculator,
                                    delta_psi_table_builder,
                                    state_fractions_solver,
                                    thermal_voltage_finder,
                                    )
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
# The numbers of the method (Kim, Ripple and Springett 2012), as the program starts
# with them: the midpoints (mV), the share of the membrane potential between the two
# haems, the temperature (°C) and the limits (% reduced).
MIDPOINTS_MV = {'bH_first': 40.0,
                'bL_first': -20.0,
                'bH_second': -30.0,
                'bL_second': -90.0,
                }
SHARE = 0.5
TEMPERATURE_C = 37.0
LIMITS_PERCENT = (10.0, 90.0)
# Worked out by hand at 37 °C: s = 8.314462618 x 310.15 / 96485.33212 x 1000 mV, and
# k = exp(-70 / s), the factor for a drop of 70 mV.
THERMAL_MV = 26.72666
FACTOR = 0.072868
# The first example of MATHS.md: the potential at bH is its midpoint (+40 mV) and that
# at bL is its midpoint (-20 mV), so "only bH" and "only bL" are as common as "neither"
# and "both" is k times that. Out of 3 + k: n = h = l = 0.325429, b = 0.023713, so each
# haem is 0.349142 reduced, 65.0858 % oxidised. delta psi = (40 + 20) / 0.5 = 120 mV.
EQUAL_PERCENT = 65.0858
# The second example: the potential at bL is s below its midpoint (-46.727 mV), so
# "only bL" is e = 2.718282 times as common as "neither". Out of 2 + e + e x k =
# 4.916357: n = h = 0.203403, l = 0.552906, b = 0.040289, so bH is 0.243692 reduced
# (75.6308 % oxidised) and bL 0.593195 (40.6805 %). delta psi = (40 + 46.727) / 0.5.
UNEQUAL_PERCENT_BH = 75.6308
UNEQUAL_PERCENT_BL = 40.6805
UNEQUAL_DELTA_PSI_MV = 173.453


# ---- DELTA PSI TEST HELPERS ----------------------------------------------------------


# ---- _calculator ---------------------------------------------------------------------
def _calculator(percent_bH: list, percent_bL: list, **changes: object) -> dict:
    """
    ---- Summary ----
    Helper function to work out delta psi with the numbers of the method, any of them
    changed by name.

    ---- Inputs ----
    percent_bH : list
        % oxidised of bH.
    percent_bL : list
        % oxidised of bL.
    **changes : object
        midpoints_mV, share, temperature_c or limits_percent, in place of the
        standard ones.

    ---- Globals read ----
    MIDPOINTS_MV, SHARE, TEMPERATURE_C, LIMITS_PERCENT.

    ---- Outputs ----
    dict
        What delta_psi_calculator gives.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    numbers = {'midpoints_mV': MIDPOINTS_MV,
               'share': SHARE,
               'temperature_c': TEMPERATURE_C,
               'limits_percent': LIMITS_PERCENT,
               }
    numbers.update(changes)
    return delta_psi_calculator(percent_bH, percent_bL, **numbers)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_delta_psi_is_empty_outside_the_limits --------------------------------------
def test_delta_psi_is_empty_outside_the_limits() -> None:
    """
    ---- Summary ----
    Main function to check that delta psi is given only where bH and bL are both
    between 10 and 90 % reduced, the limits themselves counted, and is left empty for
    a blank value.

    ---- Inputs ----
    None.

    ---- Globals read ----
    EQUAL_PERCENT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    90 % oxidised is 10 % reduced and 10 % oxidised is 90 % reduced: both kept. 90.5
    and 9.5 % oxidised are 9.5 and 90.5 % reduced: left out, whichever haem it is.
    105 % oxidised (above the oxidised level) is -5 % reduced: left out.

    ---- Helpers ----
    _calculator
    """

    percent_bH = [90.0, 10.0, 90.5, EQUAL_PERCENT, 9.5, 105.0, np.nan, EQUAL_PERCENT]
    percent_bL = [10.0, 90.0, EQUAL_PERCENT, 90.5, EQUAL_PERCENT, 50.0, 50.0, np.nan]
    result = _calculator(percent_bH, percent_bL)
    given = np.isfinite(result['delta_psi'])
    assert given.tolist() == [True, True, False, False, False, False, False, False]
    for key in ('potential_bH', 'potential_bL'):
        assert np.isfinite(result[key]).tolist() == given.tolist()
    # with wider limits the same spectra have a value
    wider = _calculator(percent_bH, percent_bL, limits_percent=(5.0, 95.0))
    assert np.isfinite(wider['delta_psi']).tolist() == [True,
                                                        True,
                                                        True,
                                                        True,
                                                        True,
                                                        False,
                                                        False,
                                                        False,
                                                        ]


# ---- test_equal_haems_at_their_midpoints_give_120_mV ---------------------------------
def test_equal_haems_at_their_midpoints_give_120_mV() -> None:
    """
    ---- Summary ----
    Main function to check the first example of MATHS.md: bH and bL both 65.0858 %
    oxidised at 37 °C sit at their midpoints, +40 and -20 mV, which is 120 mV of
    membrane potential.

    ---- Inputs ----
    None.

    ---- Globals read ----
    EQUAL_PERCENT, FACTOR.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    R_H = R_L = 1 - 0.650858 = 0.349142. With k = 0.072868: n = h = l = 1 / (3 + k)
    = 0.325429 and b = k / (3 + k) = 0.023713 (h + b = 0.349142). E_H = 40 - s x
    ln(h / n) = 40 - 0 = 40 mV; E_L = -20 - 0 = -20 mV; delta psi = 60 / 0.5 = 120 mV.
    With a share of 1 it is 60 mV.

    ---- Helpers ----
    _calculator
    """

    # ---- 1 The four states -----------------------------------------------------------
    neither, only_bH, only_bL, both = state_fractions_solver([0.349142],
                                                             [0.349142],
                                                             FACTOR,
                                                             )
    assert neither[0] == pytest.approx(0.325429, abs=2e-6)
    assert only_bH[0] == pytest.approx(0.325429, abs=2e-6)
    assert only_bL[0] == pytest.approx(0.325429, abs=2e-6)
    assert both[0] == pytest.approx(0.023713, abs=2e-6)

    # ---- 2 The potentials and delta psi ----------------------------------------------
    result = _calculator([EQUAL_PERCENT], [EQUAL_PERCENT])
    assert result['potential_bH'][0] == pytest.approx(40.0, abs=0.01)
    assert result['potential_bL'][0] == pytest.approx(-20.0, abs=0.01)
    assert result['delta_psi'][0] == pytest.approx(120.0, abs=0.01)
    whole = _calculator([EQUAL_PERCENT], [EQUAL_PERCENT], share=1.0)
    assert whole['delta_psi'][0] == pytest.approx(60.0, abs=0.01)


# ---- test_numbers_that_cannot_be_used_are_refused ------------------------------------
def test_numbers_that_cannot_be_used_are_refused() -> None:
    """
    ---- Summary ----
    Main function to check that numbers of the method that would give a wrong delta
    psi are refused with a sentence saying which: midpoints whose two drops differ, a
    missing midpoint, a share of 0, a temperature below absolute zero, and limits in
    the wrong order.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MIDPOINTS_MV.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With bL's second midpoint at -80 mV its drop is -20 + 80 = 60 mV, and bH's is
    40 + 30 = 70 mV.

    ---- Helpers ----
    _calculator
    """

    with pytest.raises(ValueError, match='drops by 70 mV .* by 60 mV'):
        _calculator([50.0], [50.0], midpoints_mV=dict(MIDPOINTS_MV, bL_second=-80.0))
    without = {key: value for key, value in MIDPOINTS_MV.items() if key != 'bL_first'}
    with pytest.raises(ValueError, match='bL_first has no number'):
        _calculator([50.0], [50.0], midpoints_mV=without)
    with pytest.raises(ValueError, match='must be above 0'):
        _calculator([50.0], [50.0], share=0.0)
    with pytest.raises(ValueError, match='temperature is -300 °C'):
        _calculator([50.0], [50.0], temperature_c=-300.0)
    with pytest.raises(ValueError, match='between 90 and 10 % reduced'):
        _calculator([50.0], [50.0], limits_percent=(90.0, 10.0))
    with pytest.raises(ValueError, match='same number of spectra'):
        _calculator([50.0, 50.0], [50.0])


# ---- test_the_b_haems_are_found_by_name ----------------------------------------------
def test_the_b_haems_are_found_by_name() -> None:
    """
    ---- Summary ----
    Main function to check that the delta psi table is built from the bH and the bL
    column however they are written, with b557 and the other haems left alone, and
    that a file without one of the two has no table.

    ---- Inputs ----
    None.

    ---- Globals read ----
    EQUAL_PERCENT, UNEQUAL_PERCENT_BH, UNEQUAL_PERCENT_BL, UNEQUAL_DELTA_PSI_MV,
    MIDPOINTS_MV, SHARE, TEMPERATURE_C, LIMITS_PERCENT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Three spectra: the first example (120 mV), the second (173.453 mV), and one with
    bH 100 % oxidised (0 % reduced, below the limit: empty).

    ---- Helpers ----
    None.
    """

    # ---- 1 A table as the decomposition names its haems ------------------------------
    percent = pd.DataFrame({TIME_COLUMN: [0.0, 0.5, 1.0],
                            SPECTRUM_INDEX_COLUMN: [1, 2, 3],
                            'Cyt $c_1$': [50.0, 50.0, 50.0],
                            'Cyt $b_H$': [EQUAL_PERCENT, UNEQUAL_PERCENT_BH, 100.0],
                            'Cyt $b_{557}$': [20.0, 20.0, 20.0],
                            'Cyt $b_L$': [EQUAL_PERCENT, UNEQUAL_PERCENT_BL, 50.0],
                            },
                           )
    percent.attrs['percent_oxidised'] = {'empty_haems': []}
    assert b_haem_column_finder(percent) == ('Cyt $b_H$', 'Cyt $b_L$')
    table = delta_psi_table_builder(percent,
                                    MIDPOINTS_MV,
                                    SHARE,
                                    TEMPERATURE_C,
                                    LIMITS_PERCENT,
                                    )
    assert list(table.columns) == [TIME_COLUMN,
                                   SPECTRUM_INDEX_COLUMN,
                                   DELTA_PSI_COLUMN,
                                   BH_POTENTIAL_COLUMN,
                                   BL_POTENTIAL_COLUMN,
                                   ]
    assert table[TIME_COLUMN].tolist() == [0.0, 0.5, 1.0]
    values = table[DELTA_PSI_COLUMN].to_numpy(dtype=float)
    assert values[0] == pytest.approx(120.0, abs=0.01)
    assert values[1] == pytest.approx(UNEQUAL_DELTA_PSI_MV, abs=0.01)
    assert np.isnan(values[2])
    assert table.attrs == {'delta_psi': {'midpoints_mV': MIDPOINTS_MV,
                                         'share': 0.5,
                                         'temperature_c': 37.0,
                                         'limits_percent': (10.0, 90.0),
                                         'bH': 'Cyt $b_H$',
                                         'bL': 'Cyt $b_L$',
                                         'spectra_with_value': 2,
                                         },
                           }

    # ---- 2 Other spellings, and a file without one of the two ------------------------
    plain = percent.rename(columns={'Cyt $b_H$': 'bH', 'Cyt $b_L$': 'haem bL'})
    assert b_haem_column_finder(plain) == ('bH', 'haem bL')
    without = percent.drop(columns=['Cyt $b_L$'])
    assert b_haem_column_finder(without) is None
    assert delta_psi_table_builder(without,
                                   MIDPOINTS_MV,
                                   SHARE,
                                   TEMPERATURE_C,
                                   LIMITS_PERCENT,
                                   ) is None
    twice = percent.rename(columns={'Cyt $b_{557}$': 'Cyt bH'})
    assert b_haem_column_finder(twice) is None


# ---- test_the_numbers_the_program_starts_with ----------------------------------------
def test_the_numbers_the_program_starts_with() -> None:
    """
    ---- Summary ----
    Main function to check that the program starts with the numbers of the method
    written in MATHS.md, with delta psi switched off, and that the voltage that goes
    with a temperature is the one worked out by hand.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MIDPOINTS_MV, SHARE, TEMPERATURE_C, LIMITS_PERCENT, THERMAL_MV, FACTOR;
    config.DEFAULT_ANSWERS, config.DELTA_PSI_MIDPOINT_ANSWERS,
    config.DELTA_PSI_REDUCED_LIMITS_PERCENT.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    s = 8.314462618 x (37 + 273.15) / 96485.33212 x 1000 = 26.72666 mV; at 25 °C,
    8.314462618 x 298.15 / 96485.33212 x 1000 = 25.69258 mV. k = exp(-70 / 26.72666)
    = exp(-2.619108) = 0.072868.

    ---- Helpers ----
    None.
    """

    answers = settings.DEFAULT_ANSWERS
    assert answers['delta_psi'] is False
    assert answers['temperature_c'] == TEMPERATURE_C
    assert answers['psi_share'] == SHARE
    assert {key: answers[answer]
            for key, answer in settings.DELTA_PSI_MIDPOINT_ANSWERS.items()
            } == MIDPOINTS_MV
    assert settings.DELTA_PSI_REDUCED_LIMITS_PERCENT == LIMITS_PERCENT
    assert thermal_voltage_finder(37.0) == pytest.approx(THERMAL_MV, abs=1e-4)
    assert thermal_voltage_finder(25.0) == pytest.approx(25.69258, abs=1e-4)
    assert np.exp(-70.0 / thermal_voltage_finder(37.0)) == pytest.approx(FACTOR,
                                                                         abs=2e-6,
                                                                         )


# ---- test_the_processing_keeps_delta_psi_when_switched_on ----------------------------
def test_the_processing_keeps_delta_psi_when_switched_on(
    monkeypatch: pytest.MonkeyPatch,
    ) -> None:
    """
    ---- Summary ----
    Main function to check that the processing of a file works out delta psi from its
    % oxidised when delta psi is switched on, and nothing when it is off or when the
    file has no regions.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the decomposition.

    ---- Globals read ----
    EQUAL_PERCENT; TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Sixty spectra, one every 0.5 min. bH is 12 mOD before 10 min and 4 mOD from 20
    min; bL is 20 and 10 mOD. Regions: oxidised 0 to 6 min, reduced 22 to 28 min, so
    D_ox = 12 and D_red = 4 for bH, 20 and 10 for bL. From 10 to 20 min both are
    65.0858 % oxidised: bH = 4 + 8 x 0.650858 = 9.206864 mOD, bL = 10 + 10 x 0.650858
    = 16.50858 mOD, which is 120 mV. Before 10 min both are 100 % oxidised and after
    20 min 0 %: outside the limits, so empty.

    ---- Helpers ----
    None.
    """

    # ---- 1 A made-up file, its decomposition stood in for ----------------------------
    times = np.arange(60) * 0.5
    fraction = EQUAL_PERCENT / 100.0
    values_bH = np.where(times < 10, 12.0, np.where(times < 20, 4 + 8 * fraction, 4.0))
    values_bL = np.where(times < 10,
                         20.0,
                         np.where(times < 20, 10 + 10 * fraction, 10.0),
                         )

    def decomposer(experiment: dict, *_args: object, **_kwargs: object) -> None:
        table = pd.DataFrame({TIME_COLUMN: times,
                              SPECTRUM_INDEX_COLUMN: np.arange(1, 61),
                              'Cyt $b_H$': values_bH,
                              'Cyt $b_L$': values_bL,
                              },
                             )
        delta = table.copy()
        delta.attrs['delta_abs_baseline'] = {
            'window_by_haem': {'Cyt $b_H$': (0.0, 24.5)},
            'window_seconds': 1470.0,
            }
        experiment.update({'haem_conc': table.copy(),
                           'haem_abs': table,
                           'haem_delta_abs': delta,
                           },
                          )

    monkeypatch.setattr(experiment_processing, 'experiment_decomposer', decomposer)
    for name in ('experiment_attenuation_adder', 'experiment_trimmer'):
        monkeypatch.setattr(experiment_processing, name, lambda *args, **kwargs: None)
    monkeypatch.setattr(experiment_processing,
                        'fit_range_finder',
                        lambda data: (500.0, 630.0),
                        )

    def processor(is_on: bool, regions: object) -> dict:
        experiment = {'experiment_name': 'made_up',
                      'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 0.0}),
                      'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': 1.0}),
                      'raw_spectra': {},
                      'metadata': {'events': []},
                      }
        info = {'path': 'made_up.paf',
                'name': 'made_up',
                'trim_start': None,
                'trim_end': None,
                'ignore_start': 0.0,
                'ignore_end': 0.0,
                'regions': regions,
                }
        answers = dict(settings.DEFAULT_ANSWERS,
                       decompose=True,
                       plot_haems=True,
                       haem_per_od=False,
                       delta_psi=is_on,
                       )
        fit = {'haem_list': ['Cyt $b_H$', 'Cyt $b_L$'], 'data': None}
        processed = experiment_processing.experiment_data_processor(info,
                                                                    settings.Config(
                                                                        answers,
                                                                        ),
                                                                    fit,
                                                                    experiment,
                                                                    )
        return processed['experiment']

    # ---- 2 Switched on, with both regions --------------------------------------------
    regions = {'oxidised_start': 0.0,
               'oxidised_end': 6.0,
               'reduced_start': 22.0,
               'reduced_end': 28.0,
               }
    table = processor(True, regions)['delta_psi']
    values = table[DELTA_PSI_COLUMN].to_numpy(dtype=float)
    middle = (times >= 10) & (times < 20)
    assert np.allclose(values[middle], 120.0, atol=0.01)
    assert np.isnan(values[~middle]).all()
    assert table.attrs['delta_psi']['spectra_with_value'] == 20

    # ---- 3 Switched off, or without regions: no delta psi ----------------------------
    assert 'delta_psi' not in processor(False, regions)
    assert 'delta_psi' not in processor(True, None)


# ---- test_unequal_haems_give_173_mV --------------------------------------------------
def test_unequal_haems_give_173_mV() -> None:
    """
    ---- Summary ----
    Main function to check the second example of MATHS.md: bH 75.6308 % and bL
    40.6805 % oxidised at 37 °C give 173.453 mV, and a warmer sample a little more.

    ---- Inputs ----
    None.

    ---- Globals read ----
    UNEQUAL_PERCENT_BH, UNEQUAL_PERCENT_BL, UNEQUAL_DELTA_PSI_MV, FACTOR, THERMAL_MV.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    R_H = 0.243692, R_L = 0.593195. Out of 2 + e + e x k = 2 + 2.718282 + 0.198075 =
    4.916357: n = h = 0.203403, l = 2.718282 / 4.916357 = 0.552906, b = 0.198075 /
    4.916357 = 0.040289 (h + b = 0.243692, l + b = 0.593195, b x n / (h x l) =
    0.072868). E_H = 40 - s x ln(1) = 40 mV; E_L = -20 - s x ln(e) = -20 - 26.727 =
    -46.727 mV; delta psi = 86.727 / 0.5 = 173.453 mV.

    ---- Helpers ----
    _calculator
    """

    # ---- 1 The four states -----------------------------------------------------------
    neither, only_bH, only_bL, both = state_fractions_solver([0.243692],
                                                             [0.593195],
                                                             FACTOR,
                                                             )
    assert neither[0] == pytest.approx(0.203403, abs=2e-6)
    assert only_bH[0] == pytest.approx(0.203403, abs=2e-6)
    assert only_bL[0] == pytest.approx(0.552906, abs=2e-6)
    assert both[0] == pytest.approx(0.040289, abs=2e-6)
    assert neither[0] + only_bH[0] + only_bL[0] + both[0] == pytest.approx(1.0)

    # ---- 2 The potentials and delta psi ----------------------------------------------
    result = _calculator([UNEQUAL_PERCENT_BH], [UNEQUAL_PERCENT_BL])
    assert result['potential_bH'][0] == pytest.approx(40.0, abs=0.01)
    assert result['potential_bL'][0] == pytest.approx(-20.0 - THERMAL_MV, abs=0.01)
    assert result['delta_psi'][0] == pytest.approx(UNEQUAL_DELTA_PSI_MV, abs=0.01)

    # ---- 3 The same haems read at another temperature --------------------------------
    # At 25 °C s is smaller (25.693 mV), so the same % give a different delta psi.
    cooler = _calculator([UNEQUAL_PERCENT_BH], [UNEQUAL_PERCENT_BL], temperature_c=25.0)
    assert cooler['delta_psi'][0] != pytest.approx(UNEQUAL_DELTA_PSI_MV, abs=0.5)
