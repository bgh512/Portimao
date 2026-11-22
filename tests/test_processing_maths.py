"""
Tests that the attenuation, normalising, percent, averaging, trimming and the % oxidised
of a processed file give the results worked out by hand from small made-up data.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared import experiment_processing
from utils_shared.attenuation import attenuation_converter, experiment_attenuation_adder
from utils_shared.averaging import (experiment_averages_calculator,
                                    window_statistics_calculator,
                                    )
from utils_shared.normalisation import (data_normaliser,
                                        experiment_normaliser,
                                        percent_scaler,
                                        )
from utils_shared.reference_level import (reference_level_finder,
                                          window_seconds_calculator,
                                          )
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN
from utils_shared.trimming import experiment_trimmer


# ---- CONSTANTS -----------------------------------------------------------------------
VO2_COLUMN = 'VoO2'


# ---- HELPERS -------------------------------------------------------------------------


# ---- _plateau_experiment_builder -----------------------------------------------------
def _plateau_experiment_builder() -> dict:
    """
    ---- Summary ----
    Helper function to build an experiment whose oxygen consumption sits on three
    levels, with an addition at each change of level.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    dict
        Experiment with a point every 0.5 min from 0 to 12 min; VoO2 is 10 before
        4 min, 5 from 4 to 8 min and 2 from 8 min on; additions at 4 and 8 min.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(25) * 0.5
    values = np.where(times < 4, 10.0, np.where(times < 8, 5.0, 2.0))
    return {'experiment_name': 'plateaus',
            'VoO2': pd.DataFrame({TIME_COLUMN: times, VO2_COLUMN: values}),
            'raw_spectra': {},
            'metadata': {'events': [{'time': 4.0, 'label': 'first'},
                                    {'time': 8.0, 'label': 'second'},
                                    ],
                         },
            }


# ---- _ramp_experiment_builder --------------------------------------------------------
def _ramp_experiment_builder() -> dict:
    """
    ---- Summary ----
    Helper function to build an experiment in which every value says which time it
    belongs to, so that a cut can be checked point by point.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    dict
        Experiment with a point every minute from 0 to 10 min. VoO2 = 10 x time;
        spectrum number = time + 1; the three transmissions of a spectrum are
        time + 0.1, time + 0.2 and time + 0.3; additions at 3 and 6 min.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(11, dtype=float)
    frame = pd.DataFrame({TIME_COLUMN: times, VO2_COLUMN: times * 10.0})
    spectra = times[:, None] + np.array([0.1, 0.2, 0.3])[None, :]
    return {'experiment_name': 'ramp',
            'VoO2': frame,
            'CcO2': frame.rename(columns={VO2_COLUMN: 'Measured O2 (uM)'}),
            'raw_spectra': {'Cyt': {'wavelengths': np.array([500.0, 550.0, 600.0]),
                                    'spectrum_indices': np.arange(1, 12),
                                    'time': times.copy(),
                                    'transmission': spectra,
                                    },
                            },
            'metadata': {'events': [{'time': 3.0, 'label': 'first', 'row_index': 3},
                                    {'time': 6.0, 'label': 'second', 'row_index': 6},
                                    ],
                         },
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_attenuation_from_known_ratios ----------------------------------------------
def test_attenuation_from_known_ratios() -> None:
    """
    ---- Summary ----
    Main function to check that light cut to a tenth and a hundredth gives 1 and 2,
    whether it is given as a fraction or as counts against a reference.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    attenuation = -log10(T): -log10(1) = 0, -log10(0.1) = 1, -log10(0.01) = 2, the
    sign of the instrument's own export.

    ---- Helpers ----
    None.
    """

    expected = np.array([0.0, 1.0, 2.0])
    assert np.allclose(attenuation_converter([1.0, 0.1, 0.01]), expected, atol=1e-12)
    counts, reference = np.array([1000.0, 100.0, 10.0]), 1000.0
    assert np.allclose(attenuation_converter(counts / reference), expected, atol=1e-12)
    assert np.allclose(attenuation_converter([0.5]), [0.30103], atol=1e-6)


# ---- test_attenuation_of_impossible_values -------------------------------------------
def test_attenuation_of_impossible_values() -> None:
    """
    ---- Summary ----
    Main function to check that a transmission with no logarithm (zero, negative or
    missing) becomes a blank.

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
    None.
    """

    result = attenuation_converter([0.0, -0.5, np.nan, np.inf, 0.1])
    assert np.all(np.isnan(result[:4]))
    assert np.isclose(result[4], 1.0)


# ---- test_attenuation_added_to_an_experiment -----------------------------------------
def test_attenuation_added_to_an_experiment() -> None:
    """
    ---- Summary ----
    Main function to check that the attenuation stored in an experiment is the
    attenuation of its transmission, one value for each one.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    attenuation = -log10(T).

    ---- Helpers ----
    None.
    """

    experiment = {'experiment_name': 'two spectra',
                  'raw_spectra': {'Cyt': {'transmission': np.array([[1.0, 0.1, 0.01],
                                                                    [10.0, 100.0, 1.0],
                                                                    ],
                                                                   ),
                                          },
                                  },
                  }
    experiment_attenuation_adder(experiment)
    assert np.allclose(experiment['raw_spectra']['Cyt']['attenuation'],
                       [[0.0, 1.0, 2.0], [-1.0, -2.0, 0.0]],
                       atol=1e-12,
                       )


# ---- test_blank_warning_counts_the_fitted_range --------------------------------------
def test_blank_warning_counts_the_fitted_range(capsys: pytest.CaptureFixture) -> None:
    """
    ---- Summary ----
    Main function to check that the warning about blank transmission values counts
    only the wavelengths of the fit when a range is given, every wavelength when none
    is, and is not printed when the only blanks are outside the range.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        What the program printed (pytest).

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Three spectra at 500, 550, 600 and 650 nm. Spectrum 1 has a zero at 500 nm,
    spectrum 2 a zero at 550 nm and a missing value at 650 nm, spectrum 3 none. Every
    wavelength: 3 blanks in 2 spectra. Between 540 and 610 nm: 1 blank in 1 spectrum.
    Between 590 and 610 nm: none.

    ---- Helpers ----
    None.
    """

    transmission = np.array([[0.0, 0.5, 0.5, 0.5],
                             [0.5, 0.0, 0.5, np.nan],
                             [0.5, 0.5, 0.5, 0.5],
                             ],
                            )
    experiment = {'experiment_name': 'blanks',
                  'raw_spectra': {'Cyt': {'transmission': transmission,
                                          'wavelengths': np.array([500.0,
                                                                   550.0,
                                                                   600.0,
                                                                   650.0,
                                                                   ],
                                                                  ),
                                          },
                                  },
                  }
    experiment_attenuation_adder(experiment)
    printed = capsys.readouterr().out
    assert '3 transmission values were' in printed
    assert '(2 spectra affected)' in printed
    experiment_attenuation_adder(experiment, checked_range_nm=(540.0, 610.0))
    printed = capsys.readouterr().out
    assert '1 transmission values between 540 and 610 nm' in printed
    assert '(1 spectra affected)' in printed
    experiment_attenuation_adder(experiment, checked_range_nm=(590.0, 610.0))
    assert capsys.readouterr().out == ''
    # the blanks themselves are kept whatever the range
    assert np.count_nonzero(np.isnan(experiment['raw_spectra']['Cyt']['attenuation'],
                                     ),
                            ) == 3


# ---- test_normalising_by_od_volume_and_dilution --------------------------------------
def test_normalising_by_od_volume_and_dilution() -> None:
    """
    ---- Summary ----
    Main function to check that normalising divides by dilution factor x OD x volume,
    and leaves the times alone.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With OD 2, volume 3 and dilution 2 the divisor is 12: 12 -> 1, 24 -> 2, 60 -> 5.

    ---- Helpers ----
    None.
    """

    assert np.allclose(data_normaliser(np.array([12.0, 24.0]), 2.0, 3.0, 2.0),
                       [1.0, 2.0],
                       )
    with pytest.raises(ValueError):
        data_normaliser(np.array([12.0]), 0.0, 3.0, 2.0)
    experiment = {'experiment_name': 'normalised',
                  'VoO2': pd.DataFrame({TIME_COLUMN: [0.0, 1.0, 2.0],
                                        VO2_COLUMN: [12.0, 24.0, 60.0],
                                        },
                                       ),
                  'metadata': {'OD': 2.0, 'volume': 3.0, 'dilution_factor': 2.0},
                  }
    experiment_normaliser(experiment)
    assert np.allclose(experiment['VoO2_OD'][VO2_COLUMN], [1.0, 2.0, 5.0])
    assert np.allclose(experiment['VoO2_OD'][TIME_COLUMN], [0.0, 1.0, 2.0])
    assert np.allclose(experiment['VoO2'][VO2_COLUMN], [12.0, 24.0, 60.0])


# ---- test_unreadable_numbers_stop_both_scalings --------------------------------------
def test_unreadable_numbers_stop_both_scalings() -> None:
    """
    ---- Summary ----
    Main function to check that a value that is not a number stops the OD scaling and
    the % scaling alike, with the same plain message, and that an empty cell stays
    empty in both.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Values 2, 2, empty, 6, 6 with one point in a row: OD 2, volume 3 and dilution 2
    divide by 12, so 2 -> 1/6 and 6 -> 0.5; on the % scale 2 -> 0 and 6 -> 100. The
    empty cell stays empty in both.

    ---- Helpers ----
    None.
    """

    times = np.arange(5) * 0.1
    bad = pd.DataFrame({TIME_COLUMN: times, VO2_COLUMN: [2.0, 2.0, 'n/a', 6.0, 6.0]})
    with pytest.raises(ValueError, match='not a number'):
        percent_scaler(bad, window_points=1, label='bad file')
    with pytest.raises(ValueError, match='not a number'):
        data_normaliser(bad[[VO2_COLUMN]], 2.0, 3.0, 2.0, label='bad file')
    with pytest.raises(ValueError, match='not a number'):
        data_normaliser(bad[VO2_COLUMN], 2.0, 3.0, 2.0, label='bad file')
    gap = pd.DataFrame({TIME_COLUMN: times, VO2_COLUMN: [2.0, 2.0, None, 6.0, 6.0]})
    percent = percent_scaler(gap, window_points=1)[VO2_COLUMN].to_numpy(dtype=float)
    assert np.allclose(percent[[0, 1, 3, 4]], [0.0, 0.0, 100.0, 100.0])
    assert np.isnan(percent[2])
    scaled = data_normaliser(gap[VO2_COLUMN], 2.0, 3.0, 2.0).to_numpy(dtype=float)
    assert np.allclose(scaled[[0, 1, 3, 4]], [1 / 6, 1 / 6, 0.5, 0.5])
    assert np.isnan(scaled[2])


# ---- test_percent_of_a_trace_with_plateaus -------------------------------------------
def test_percent_of_a_trace_with_plateaus() -> None:
    """
    ---- Summary ----
    Main function to check that a trace on three levels gives 0 % on its lowest level,
    100 % on its highest and the right share in between.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A point every 6 s for 12 min: 2 for the first 4 min (40 points), then 6 (40
    points), then 4 from 8 min. With 30 points in a row, the lowest median is 2 and
    the highest 6. percent = (value - 2) / (6 - 2) x 100, so 2 -> 0, 6 -> 100 and
    4 -> 50. 30 points, 6 s apart, last 180 s. The first window of median 2 is points
    0 to 29 (0 to 2.9 min). The first of median 6 is points 26 to 55 (2.6 to 5.5 min):
    it holds 14 twos and 16 sixes, so its two middle values are both 6; a window may
    reach over a step as long as most of it is on the level.

    ---- Helpers ----
    None.
    """

    number = np.arange(121)
    values = np.where(number < 40, 2.0, np.where(number < 80, 6.0, 4.0))
    frame = pd.DataFrame({TIME_COLUMN: number * 0.1, VO2_COLUMN: values})
    result = percent_scaler(frame, window_points=30)
    expected = np.where(number < 40, 0.0, np.where(number < 80, 100.0, 50.0))
    assert np.allclose(result[VO2_COLUMN], expected, atol=1e-9)
    assert np.allclose(result[TIME_COLUMN], number * 0.1)
    scaling = result.attrs['percent_scaling'][VO2_COLUMN]
    assert np.isclose(scaling['zero_percent_level'], 2.0)
    assert np.isclose(scaling['hundred_percent_level'], 6.0)
    assert np.isclose(scaling['zero_percent_window']['start_time'], 0.0)
    assert np.isclose(scaling['zero_percent_window']['end_time'], 2.9)
    assert np.isclose(scaling['hundred_percent_window']['start_time'], 2.6)
    assert np.isclose(scaling['hundred_percent_window']['end_time'], 5.5)
    assert np.isclose(scaling['window_seconds'], 180.0)


# ---- test_percent_of_a_flat_trace ----------------------------------------------------
def test_percent_of_a_flat_trace() -> None:
    """
    ---- Summary ----
    Main function to check that a trace that never changes has no percent scale (every
    value blank), and that a window of more points than the trace has is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    frame = pd.DataFrame({TIME_COLUMN: np.arange(61) * 0.1, VO2_COLUMN: 3.0})
    assert np.all(np.isnan(percent_scaler(frame, window_points=30)[VO2_COLUMN]))
    with pytest.raises(ValueError, match='Ignore less'):
        percent_scaler(frame, window_points=62)


# ---- test_reference_level_from_points_in_a_row ---------------------------------------
def test_reference_level_from_points_in_a_row() -> None:
    """
    ---- Summary ----
    Main function to check the one finder of the reference levels: the median of the
    highest, or the lowest, points in a row, with a blank value, with an ignored start
    and end, and with too few points.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Values 1, 2, 9, 3, 4, 5, 0, 0 at 0 to 7 min, three points in a row. Medians of the
    six windows: 2, 3, 4, 4, 4, 0. Highest: 4, first at 9, 3, 4 (2 to 4 min); lowest:
    0, at 5, 0, 0 (5 to 7 min). With the 3 blank, the points left are 1, 2, 9, 4, 5,
    0, 0 with medians 2, 4, 5, 4, 0: highest 5, at 9, 4, 5 (2 to 5 min, over the
    blank). Between 1 and 5 min only: 2, 9, 3, 4, 5 with medians 3, 4, 4: highest 4
    (2 to 4 min), lowest 3 (1 to 3 min). Three points, 1 min apart, last 180 s.

    ---- Helpers ----
    None.
    """

    times = np.arange(8, dtype=float)
    values = np.array([1.0, 2.0, 9.0, 3.0, 4.0, 5.0, 0.0, 0.0])
    highest = reference_level_finder(times, values, 0.0, 7.0, 3)
    assert highest == {'level': 4.0, 'start_time': 2.0, 'end_time': 4.0, 'n_points': 3}
    lowest = reference_level_finder(times, values, 0.0, 7.0, 3, is_highest=False)
    assert lowest == {'level': 0.0, 'start_time': 5.0, 'end_time': 7.0, 'n_points': 3}
    with_blank = values.copy()
    with_blank[3] = np.nan
    over_blank = reference_level_finder(times, with_blank, 0.0, 7.0, 3)
    assert (over_blank['level'], over_blank['start_time'], over_blank['end_time']) == (
        5.0,
        2.0,
        5.0,
        )
    inner = reference_level_finder(times, values, 1.0, 5.0, 3)
    assert (inner['level'], inner['start_time'], inner['end_time']) == (4.0, 2.0, 4.0)
    inner_low = reference_level_finder(times, values, 1.0, 5.0, 3, is_highest=False)
    assert (inner_low['level'], inner_low['start_time']) == (3.0, 1.0)
    assert reference_level_finder(times, values, 0.0, 7.0, 9) is None
    assert reference_level_finder(times, values, 6.5, 7.0, 3) is None
    with pytest.raises(ValueError):
        reference_level_finder(times, values, 0.0, 7.0, 0)
    assert np.isclose(window_seconds_calculator(times, 3), 180.0)


# ---- test_window_mean_and_spread -----------------------------------------------------
def test_window_mean_and_spread() -> None:
    """
    ---- Summary ----
    Main function to check the mean and spread of the values inside a time window,
    with a blank value, with one value and with none.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Values 1 to 6 at 0 to 5 min. From 1 to 3 min: 2, 3, 4 -> mean 3, spread
    sqrt((1 + 0 + 1) / 2) = 1. With a blank in the middle of 4, 5, 6: 4 and 6 -> mean
    5, spread sqrt((1 + 1) / 1) = 1.414.

    ---- Helpers ----
    None.
    """

    frame = pd.DataFrame({TIME_COLUMN: [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                          'whole': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                          'gap': [1.0, 2.0, 3.0, 4.0, np.nan, 6.0],
                          },
                         )
    stats = window_statistics_calculator(frame, 1.0, 3.0)
    assert np.isclose(stats['whole']['mean'], 3.0)
    assert np.isclose(stats['whole']['sd'], 1.0)
    stats = window_statistics_calculator(frame, 3.0, 5.0)
    assert np.isclose(stats['whole']['mean'], 5.0)
    assert np.isclose(stats['gap']['mean'], 5.0)
    assert np.isclose(stats['gap']['sd'], np.sqrt(2.0))
    one = window_statistics_calculator(frame, 1.5, 2.5)
    assert np.isclose(one['whole']['mean'], 3.0)
    assert np.isnan(one['whole']['sd'])
    none = window_statistics_calculator(frame, 10.0, 11.0)
    assert np.isnan(none['whole']['mean'])
    assert np.isnan(none['whole']['sd'])


# ---- test_averages_around_the_additions ----------------------------------------------
def test_averages_around_the_additions() -> None:
    """
    ---- Summary ----
    Main function to check the averages before and after each addition, and their
    change from the first one.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Additions at 4 and 8 min, run ends at 12 min, 2 min windows ending 0.5 min before
    the next addition (or the end): 1.5 to 3.5, 5.5 to 7.5 and 9.5 to 11.5 min, where
    the trace is 10, 5 and 2. Change = 10/10, 5/10, 2/10 x 100 = 100, 50, 20 %;
    difference = 0, -5, -8.

    ---- Helpers ----
    _plateau_experiment_builder
    """

    experiment = experiment_averages_calculator(_plateau_experiment_builder(),
                                                window_minutes=2.0,
                                                gap_minutes=0.5,
                                                final_window_gap_minutes=0.5,
                                                baseline_minimum_seconds=10.0,
                                                vo2_source='raw',
                                                haem_source=None,
                                                )
    windows = experiment['averages']['windows']
    assert list(windows) == ['average0', 'average1', 'average2']
    assert experiment['averages']['skipped'] == {}
    expected = {'average0': (1.5, 3.5, 10.0, 100.0, 0.0),
                'average1': (5.5, 7.5, 5.0, 50.0, -5.0),
                'average2': (9.5, 11.5, 2.0, 20.0, -8.0),
                }
    for name, (start, end, mean, change, delta) in expected.items():
        stats = windows[name]['vo2'][VO2_COLUMN]
        assert np.isclose(windows[name]['start_time'], start)
        assert np.isclose(windows[name]['end_time'], end)
        assert np.isclose(stats['mean'], mean)
        assert np.isclose(stats['sd'], 0.0)
        assert np.isclose(stats['change'], change)
        assert np.isclose(stats['delta'], delta)


# ---- test_a_file_with_both_regions_gets_percent_oxidised -----------------------------
def test_a_file_with_both_regions_gets_percent_oxidised(monkeypatch: pytest.MonkeyPatch,
                                                        ) -> None:
    """
    ---- Summary ----
    Main function to check that the processing of a file with both regions keeps each
    haem's two levels and its % oxidised line, with the regions (kept as times on the
    recording) put on the time of the trimmed data, and that a file without regions
    has neither and is shown as delta D when % oxidised is asked for. The reading of
    the spectra and the decomposition are stood in for by a made-up haem.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Pytest's tool for standing in for the decomposition.

    ---- Globals read ----
    TIME_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Sixty spectra, one every 0.5 min from 0 to 29.5 min of the trimmed data, which
    was trimmed 2 min from its start. D is 12 mOD before 10 min, 10 mOD from 10 to
    20 min and 4 mOD from 20 min on. Regions on the recording: oxidised 2 to 8 min,
    reduced 24 to 30 min; on the trimmed data 0 to 6 and 22 to 28 min, 13 spectra
    each. D_ox = 12, D_red = 4, so P = (D - 4) / 8 x 100: 100 %, 75 % and 0 %.

    ---- Helpers ----
    None.
    """

    # ---- 1 A made-up file, its decomposition stood in for ----------------------------
    times = np.arange(60) * 0.5
    values = np.where(times < 10, 12.0, np.where(times < 20, 10.0, 4.0))

    def decomposer(experiment: dict, *_args: object, **_kwargs: object) -> None:
        table = pd.DataFrame({TIME_COLUMN: times,
                              SPECTRUM_INDEX_COLUMN: np.arange(1, 61),
                              'bH': values,
                              },
                             )
        delta = table.copy()
        delta['bH'] = values - 12.0
        delta.attrs['delta_abs_baseline'] = {'window_by_haem': {'bH': (0.0, 24.5)},
                                             'window_seconds': 1470.0,
                                             }
        experiment.update({'haem_conc': table.copy(),
                           'haem_abs': table,
                           'haem_delta_abs': delta,
                           },
                          )

    monkeypatch.setattr(experiment_processing, 'experiment_decomposer', decomposer)
    monkeypatch.setattr(experiment_processing,
                        'experiment_attenuation_adder',
                        lambda *args, **kwargs: None,
                        )
    monkeypatch.setattr(experiment_processing,
                        'experiment_trimmer',
                        lambda *args, **kwargs: None,
                        )
    monkeypatch.setattr(experiment_processing,
                        'fit_range_finder',
                        lambda data: (500.0, 630.0),
                        )

    def processor(regions: Optional[dict]) -> dict:
        experiment = {'experiment_name': 'made_up',
                      'CcO2': pd.DataFrame({TIME_COLUMN: times, 'Measured O2': 0.0}),
                      'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': 1.0}),
                      'raw_spectra': {},
                      'metadata': {'events': []},
                      }
        info = {'path': 'made_up.paf',
                'name': 'made_up',
                'trim_start': 2.0,
                'trim_end': None,
                'ignore_start': 0.0,
                'ignore_end': 0.0,
                'regions': regions,
                }
        answers = dict(settings.DEFAULT_ANSWERS,
                       decompose=True,
                       plot_haems=True,
                       haem_mode='percent',
                       haem_per_od=False,
                       )
        return experiment_processing.experiment_data_processor(info,
                                                               settings.Config(answers),
                                                               {'haem_list': ['bH'],
                                                                'data': None,
                                                                },
                                                               experiment,
                                                               )

    # ---- 2 Both regions: the two levels and the % line -------------------------------
    regions = {'oxidised_start': 2.0,
               'oxidised_end': 8.0,
               'reduced_start': 24.0,
               'reduced_end': 30.0,
               }
    processed = processor(regions)
    experiment = processed['experiment']
    assert experiment['haem_levels'] == {'oxidised': {'bH': 12.0},
                                         'oxidised_region': (0.0, 6.0),
                                         'reduced': {'bH': 4.0},
                                         'reduced_region': (22.0, 28.0),
                                         }
    percent = experiment['haem_percent']['bH'].to_numpy(dtype=float)
    expected = np.where(times < 10, 100.0, np.where(times < 20, 75.0, 0.0))
    assert np.allclose(percent, expected)
    assert processed['haem_source'] == 'percent'

    # ---- 3 No regions, or only one: shown as delta D ---------------------------------
    for missing in (None, dict(regions, reduced_start=30.0)):
        processed = processor(missing)
        assert 'haem_levels' not in processed['experiment']
        assert 'haem_percent' not in processed['experiment']
        assert processed['haem_source'] == 'delta_abs'


# ---- test_average_that_does_not_fit --------------------------------------------------
def test_average_that_does_not_fit() -> None:
    """
    ---- Summary ----
    Main function to check that an averaging window too long to fit between two
    additions is left out, and said to be, in place of reaching back over the addition.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A 4 min window ending at 7.5 min starts at 3.5 min, before the addition at 4 min;
    one ending at 11.5 min starts at 7.5 min, before the addition at 8 min. The first
    window (-0.5 to 3.5 min) holds only the level 10.

    ---- Helpers ----
    _plateau_experiment_builder
    """

    experiment = experiment_averages_calculator(_plateau_experiment_builder(),
                                                window_minutes=4.0,
                                                gap_minutes=0.5,
                                                final_window_gap_minutes=0.5,
                                                baseline_minimum_seconds=10.0,
                                                vo2_source='raw',
                                                haem_source=None,
                                                )
    averages = experiment['averages']
    assert list(averages['windows']) == ['average0']
    assert sorted(averages['skipped']) == ['average1', 'average2']
    assert np.isclose(averages['windows']['average0']['vo2'][VO2_COLUMN]['mean'], 10.0)
    assert np.isclose(averages['windows']['average0']['start_time'], 0.0)


# ---- test_baseline_needs_ten_seconds_of_data -----------------------------------------
def test_baseline_needs_ten_seconds_of_data() -> None:
    """
    ---- Summary ----
    Main function to check that a run with less than 10 s of data in its baseline
    window has no baseline, so its changes from baseline are blank while its averages
    are kept, and that a baseline window cut at the start of the recording counts when
    it still holds 10 s.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A point every 0.5 min from 0 min; 2 min windows ending 0.5 min before the next
    addition. First addition at 0.6 min: the baseline window ends at 0.1 min and is
    cut at 0 min, where it holds one point (0 s of data), so there is no baseline;
    the windows 5.5 to 7.5 and 9.5 to 11.5 min still average 5 and 2. First addition
    at 1 min: the window is 0 to 0.5 min and holds two points 30 s apart, so it is
    the baseline (mean 10) and the second window (5) is 50 % of it.

    ---- Helpers ----
    _plateau_experiment_builder
    """

    settings = {'window_minutes': 2.0,
                'gap_minutes': 0.5,
                'final_window_gap_minutes': 0.5,
                'vo2_source': 'raw',
                'haem_source': None,
                'baseline_minimum_seconds': 10.0,
                }
    short = _plateau_experiment_builder()
    short['metadata']['events'][0]['time'] = 0.6
    averages = experiment_averages_calculator(short, **settings)['averages']
    assert list(averages['windows']) == ['average1', 'average2']
    assert list(averages['skipped']) == ['average0']
    assert np.isclose(averages['skipped']['average0']['start_time'], 0.0)
    for name, mean in (('average1', 5.0), ('average2', 2.0)):
        stats = averages['windows'][name]['vo2'][VO2_COLUMN]
        assert np.isclose(stats['mean'], mean)
        assert np.isnan(stats['change'])
        assert np.isnan(stats['delta'])
    enough = _plateau_experiment_builder()
    enough['metadata']['events'][0]['time'] = 1.0
    averages = experiment_averages_calculator(enough, **settings)['averages']
    assert list(averages['windows']) == ['average0', 'average1', 'average2']
    assert averages['skipped'] == {}
    assert np.isclose(averages['windows']['average0']['start_time'], 0.0)
    assert np.isclose(averages['windows']['average0']['end_time'], 0.5)
    assert np.isclose(averages['windows']['average0']['vo2'][VO2_COLUMN]['mean'], 10.0)
    assert np.isclose(averages['windows']['average1']['vo2'][VO2_COLUMN]['change'],
                      50.0,
                      )


# ---- test_trimming_keeps_exactly_the_chosen_times ------------------------------------
def test_trimming_keeps_exactly_the_chosen_times() -> None:
    """
    ---- Summary ----
    Main function to check that cutting a run at 2 and 7 min keeps the points from 2 to
    7 min and no others, in the traces and in the spectra, and counts time from the cut.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Points at 0 to 10 min; kept: 2, 3, 4, 5, 6, 7 -> new times 0 to 5. Their values
    (10 x old time) are 20 to 70; their spectrum numbers 3 to 8; the additions at 3 and
    6 min move to 1 and 4 min.

    ---- Helpers ----
    _ramp_experiment_builder
    """

    experiment = experiment_trimmer(_ramp_experiment_builder(), 2.0, 7.0)
    new_times = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    for key in ('VoO2', 'CcO2'):
        assert np.allclose(experiment[key][TIME_COLUMN], new_times)
    assert np.allclose(experiment['VoO2'][VO2_COLUMN], [20, 30, 40, 50, 60, 70])
    dataset = experiment['raw_spectra']['Cyt']
    assert np.allclose(dataset['time'], new_times)
    assert np.array_equal(dataset['spectrum_indices'], [3, 4, 5, 6, 7, 8])
    assert np.allclose(dataset['transmission'][:, 0], [2.1, 3.1, 4.1, 5.1, 6.1, 7.1])
    assert dataset['transmission'].shape == (6, 3)
    events = experiment['metadata']['events']
    assert [event['time'] for event in events] == [1.0, 4.0]
    assert all('row_index' not in event for event in events)
    assert experiment['metadata']['trimmed_before_minutes'] == 2.0
    assert experiment['metadata']['trimmed_after_minutes'] == 7.0


# ---- test_trimming_moves_the_ignored_additions ---------------------------------------
def test_trimming_moves_the_ignored_additions() -> None:
    """
    ---- Summary ----
    Main function to check that after a cut at the start the ignored additions are
    counted from the new zero like everything else, and that one made before the cut
    gets a negative time.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Cut at 2 and 7 min; ignored additions at 1 and 5 min move to -1 and 3 min, as the
    kept ones at 3 and 6 min move to 1 and 4 min.

    ---- Helpers ----
    _ramp_experiment_builder
    """

    experiment = _ramp_experiment_builder()
    experiment['metadata']['ignored_events'] = [{'time': 1.0, 'row_index': 1},
                                                {'time': 5.0, 'row_index': 5},
                                                ]
    experiment_trimmer(experiment, 2.0, 7.0)
    ignored = experiment['metadata']['ignored_events']
    assert [event['time'] for event in ignored] == [-1.0, 3.0]
    assert all('row_index' not in event for event in ignored)
    assert [event['time'] for event in experiment['metadata']['events']] == [1.0, 4.0]


# ---- test_trimming_never_cuts_an_addition --------------------------------------------
def test_trimming_never_cuts_an_addition() -> None:
    """
    ---- Summary ----
    Main function to check that a cut that would lose an addition, or that ends before
    it starts, is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The additions are at 3 and 6 min, so a start at 4 min or an end at 5 min loses one.

    ---- Helpers ----
    _ramp_experiment_builder
    """

    with pytest.raises(ValueError):
        experiment_trimmer(_ramp_experiment_builder(), 4.0, None)
    with pytest.raises(ValueError):
        experiment_trimmer(_ramp_experiment_builder(), None, 5.0)
    with pytest.raises(ValueError):
        experiment_trimmer(_ramp_experiment_builder(), 7.0, 2.0)


# ---- test_trimming_the_end_only ------------------------------------------------------
def test_trimming_the_end_only() -> None:
    """
    ---- Summary ----
    Main function to check that cutting only the end at 7 min keeps the points from 0
    to 7 min with their times unchanged.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIME_COLUMN, VO2_COLUMN (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Points at 0 to 10 min; kept: 0 to 7 (eight points), values 0 to 70.

    ---- Helpers ----
    _ramp_experiment_builder
    """

    kept_times = np.arange(8, dtype=float)
    experiment = experiment_trimmer(_ramp_experiment_builder(), None, 7.0)
    assert np.allclose(experiment['VoO2'][TIME_COLUMN], kept_times)
    assert np.allclose(experiment['VoO2'][VO2_COLUMN], kept_times * 10.0)
    dataset = experiment['raw_spectra']['Cyt']
    assert np.allclose(dataset['time'], kept_times)
    assert np.array_equal(dataset['spectrum_indices'], np.arange(1, 9))
    assert dataset['transmission'].shape == (8, 3)
    assert [event['time'] for event in experiment['metadata']['events']] == [3.0, 6.0]
    assert experiment['metadata']['trimmed_after_minutes'] == 7.0
