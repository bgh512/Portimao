"""
Tests that the attenuation, normalising, percent, averaging and trimming give the results
worked out by hand from small made-up data.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.attenuation import attenuation_converter, experiment_attenuation_adder
from utils_shared.averaging import (experiment_averages_calculator,
                                    window_statistics_calculator,
                                    )
from utils_shared.normalisation import (data_normaliser,
                                        experiment_normaliser,
                                        percent_scaler,
                                        )
from utils_shared.schema import TIME_COLUMN
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
    whether it is given as a fraction, as counts against a reference or as a percentage.

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
    assert np.allclose(attenuation_converter([100.0, 10.0, 1.0], mode='percentage'),
                       expected,
                       atol=1e-12,
                       )
    assert np.allclose(attenuation_converter([0.5]), [0.30103], atol=1e-6)
    already = np.array([0.3, -0.2])
    assert np.array_equal(attenuation_converter(already, mode='absorbance'), already)


# ---- test_attenuation_of_impossible_values -------------------------------------------
def test_attenuation_of_impossible_values() -> None:
    """
    ---- Summary ----
    Main function to check that a transmission with no logarithm (zero, negative or
    missing) becomes a blank, and that an unknown kind of input is refused.

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
    with pytest.raises(ValueError):
        attenuation_converter([0.5], mode='counts')


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
    A point every 6 s for 12 min: 2 for the first 4 min, then 6, then 4 from 8 min.
    percent = (value - 2) / (6 - 2) x 100, so 2 -> 0, 6 -> 100 and 4 -> 50.

    ---- Helpers ----
    None.
    """

    number = np.arange(121)
    values = np.where(number < 40, 2.0, np.where(number < 80, 6.0, 4.0))
    frame = pd.DataFrame({TIME_COLUMN: number * 0.1, VO2_COLUMN: values})
    result = percent_scaler(frame, window_seconds=30.0)
    expected = np.where(number < 40, 0.0, np.where(number < 80, 100.0, 50.0))
    assert np.allclose(result[VO2_COLUMN], expected, atol=1e-9)
    assert np.allclose(result[TIME_COLUMN], number * 0.1)
    scaling = result.attrs['percent_scaling'][VO2_COLUMN]
    assert np.isclose(scaling['minimum_mean'], 2.0)
    assert np.isclose(scaling['maximum_mean'], 6.0)
    assert scaling['zero_percent_window']['end_time'] < 4.0
    assert 4.0 <= scaling['hundred_percent_window']['start_time'] < 8.0


# ---- test_percent_of_a_flat_trace ----------------------------------------------------
def test_percent_of_a_flat_trace() -> None:
    """
    ---- Summary ----
    Main function to check that a trace that never changes has no percent scale (every
    value blank), and that a window longer than the trace is refused.

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
    assert np.all(np.isnan(percent_scaler(frame, window_seconds=30.0)[VO2_COLUMN]))
    with pytest.raises(ValueError):
        percent_scaler(frame, window_seconds=600.0)


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
                                                vo2_source='raw',
                                                haem_source=None,
                                                )
    averages = experiment['averages']
    assert list(averages['windows']) == ['average0']
    assert sorted(averages['skipped']) == ['average1', 'average2']
    assert np.isclose(averages['windows']['average0']['vo2'][VO2_COLUMN]['mean'], 10.0)


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
