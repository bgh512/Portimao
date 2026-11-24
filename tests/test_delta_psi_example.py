"""
Tests that Δψ of the example run, worked out from the file with one fixed set-up,
still gives the numbers it gave when they were written down.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.delta_psi import (BH_POTENTIAL_COLUMN,
                                    BL_POTENTIAL_COLUMN,
                                    DELTA_PSI_COLUMN,
                                    )
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.schema import SPECTRUM_INDEX_COLUMN
from utils_shared.spectral_decomposer import fit_loader


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
PAF_FILE = ROOT / 'data_instrument_check' / 'example.paf'  # local only, not in git
FITS_FOLDER = ROOT / 'fits'
# The set-up, written out in full so that a change of the program's standard answers
# does not change it: the standard fit and scatter of 2026-11-24, the first 5 min
# ignored, the oxidised region before the first addition (14.0 min) and the reduced one
# after the dithionite (44.9 min), and the paper's numbers at 37 °C.
SET_UP = {'fit_file': 'bswitch_no2_mycobl_b557.csv',
          'haem_background': 'rowan_scatter',
          'decomposition_dataset': 'Cyt',
          'ignore_first_minutes': 5.0,
          'ignore_last_minutes': 0.0,
          'psi_bH_first_mV': 40.0,
          'psi_bL_first_mV': -20.0,
          'psi_bH_second_mV': -30.0,
          'psi_bL_second_mV': -90.0,
          'psi_share': 0.5,
          'temperature_c': 37.0,
          'psi_reduced_lowest_percent': 10.0,
          'psi_reduced_highest_percent': 90.0,
          }
REGIONS = {'oxidised_start': 6.0,
           'oxidised_end': 13.0,
           'reduced_start': 47.0,
           'reduced_end': 51.5,
           }
# The numbers it gave, written on 2026-11-24 by
# _USER_REVIEW/claude_work/c12_delta_psi_reference.py. Rewrite them only on purpose,
# when the maths of the decomposition, the regions or Δψ is meant to change. mV.
FIXED_SPECTRA_WITH_VALUE = 627  # of 6218
FIXED_SUMMARY = {'mean': 115.04257220140198,
                 'median': 114.148808312597,
                 'lowest': -14.499077000095038,
                 'highest': 267.612116969612,
                 'mean_bH': 37.69780902277045,
                 'mean_bL': -19.823477077930537,
                 }
FIXED_SPECTRA = (111, 4476, 4941, 5205, 5970)  # spectrum numbers of the values below
FIXED_VALUES = (101.3373058214726,
                47.21017950283563,
                143.48972377140367,
                88.64573779019267,
                161.9340111624927,
                )
# "Identical" to a billionth of the size: two computers can differ in the last digit.
RELATIVE = 1e-9

pytestmark = pytest.mark.skipif(
    not PAF_FILE.exists(),
    reason='the example run in data_instrument_check/ (local only, not in git) is '
           'missing, so the fixed Δψ test is skipped',
    )


# ---- DELTA PSI EXAMPLE HELPERS -------------------------------------------------------


# ---- example_table_builder -----------------------------------------------------------
def example_table_builder() -> pd.DataFrame:
    """
    ---- Summary ----
    Helper function to work out the Δψ table of the example run with the fixed set-up,
    through the program's own processing of a file.

    ---- Inputs ----
    None.

    ---- Globals read ----
    PAF_FILE, FITS_FOLDER, SET_UP, REGIONS; settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    pd.DataFrame
        The Δψ table (DATA_FORMAT.md): one row per spectrum, Δψ and the potential at
        bH and bL (mV).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    fit_loader
    """

    answers = dict(settings.DEFAULT_ANSWERS,
                   decompose=True,
                   plot_haems=True,
                   delta_psi=True,
                   normalise_od=False,
                   export_spectra=False,
                   averaging=False,
                   **SET_UP,
                   )
    info = {'path': str(PAF_FILE),
            'name': 'example',
            'trim_start': None,
            'trim_end': None,
            'ignore_start': SET_UP['ignore_first_minutes'],
            'ignore_end': SET_UP['ignore_last_minutes'],
            'regions': dict(REGIONS),
            }
    fit = fit_loader(FITS_FOLDER, SET_UP['fit_file'])
    processed = experiment_data_processor(info, settings.Config(answers), fit)
    return processed['experiment']['delta_psi']


# ---- example_numbers_finder ----------------------------------------------------------
def example_numbers_finder(table: pd.DataFrame) -> dict:
    """
    ---- Summary ----
    Helper function to give the numbers of a Δψ table that the test holds fixed.

    ---- Inputs ----
    table : pd.DataFrame
        The Δψ table of the example run (example_table_builder).

    ---- Globals read ----
    FIXED_SPECTRA; DELTA_PSI_COLUMN, BH_POTENTIAL_COLUMN, BL_POTENTIAL_COLUMN,
    SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    dict
        {'spectra_with_value', 'summary' (mean, median, lowest and highest Δψ, mean
        potential at bH and bL), 'values' (Δψ at FIXED_SPECTRA)}, mV.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The mean, median, lowest and highest over the spectra that have a Δψ.

    ---- Helpers ----
    None.
    """

    psi = table[DELTA_PSI_COLUMN].to_numpy(dtype=float)
    has_value = np.isfinite(psi)
    spectra = table[SPECTRUM_INDEX_COLUMN].to_numpy()
    values = tuple(float(psi[spectra == number][0]) for number in FIXED_SPECTRA
                   if (spectra == number).any()
                   )
    return {'spectra_with_value': int(has_value.sum()),
            'summary': {'mean': float(np.mean(psi[has_value])),
                        'median': float(np.median(psi[has_value])),
                        'lowest': float(np.min(psi[has_value])),
                        'highest': float(np.max(psi[has_value])),
                        'mean_bH': float(np.nanmean(table[BH_POTENTIAL_COLUMN])),
                        'mean_bL': float(np.nanmean(table[BL_POTENTIAL_COLUMN])),
                        },
            'values': values,
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_example_delta_psi_stays_fixed ----------------------------------------------
def test_example_delta_psi_stays_fixed() -> None:
    """
    ---- Summary ----
    Main function to check that Δψ of the example run, with the fixed set-up, gives
    the same number of spectra with a value and the same numbers as when they were
    written down.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FIXED_SPECTRA_WITH_VALUE, FIXED_SUMMARY, FIXED_VALUES, RELATIVE.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Each number within RELATIVE x its size of the one written down.

    ---- Helpers ----
    example_numbers_finder
    example_table_builder
    """

    numbers = example_numbers_finder(example_table_builder())
    assert numbers['spectra_with_value'] == FIXED_SPECTRA_WITH_VALUE
    for name, fixed in FIXED_SUMMARY.items():
        assert numbers['summary'][name] == pytest.approx(fixed, rel=RELATIVE), name
    assert numbers['values'] == pytest.approx(FIXED_VALUES, rel=RELATIVE)
