"""
Tests that the averaged spectra, their difference and the averages over repeated runs
give the results worked out by hand from small made-up data.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.spectral_difference import (difference_spectrum_calculator,
                                              spectral_averager,
                                              )
from utils_custom.triplicate_averager import triplicate_averager


# ---- CONSTANTS -----------------------------------------------------------------------
VO2_COLUMN = 'VoO2'


# ---- HELPERS -------------------------------------------------------------------------


# ---- _run_builder --------------------------------------------------------------------
def _run_builder(name: str, means: dict) -> dict:
    """
    ---- Summary ----
    Helper function to build one run that already has its averages, as the averaging
    step leaves them.

    ---- Inputs ----
    name : str
        Name of the run, ending in 'run<number>'.
    means : dict
        {window name: mean of the oxygen consumption in that window}.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    dict
        Experiment with 'averages'. In each window the spread is 0.1, the change is
        10 x the mean and the difference is the mean - 1.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    windows = {window: {'start_time': 1.0,
                        'end_time': 3.0,
                        'vo2': {VO2_COLUMN: {'mean': mean,
                                             'sd': 0.1,
                                             'change': mean * 10.0,
                                             'delta': mean - 1.0,
                                             },
                                },
                        'haem': {},
                        }
               for window, mean in means.items()
               }
    return {'experiment_name': name,
            'averages': {'settings': {'window_minutes': 2.0},
                         'windows': windows,
                         'skipped': {},
                         },
            }


# ---- _spectra_experiment_builder -----------------------------------------------------
def _spectra_experiment_builder() -> dict:
    """
    ---- Summary ----
    Helper function to build an experiment whose spectra change at each of two
    additions.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Experiment with a spectrum of three wavelengths every 0.5 min from 0 to
        12 min and additions at 4 and 8 min. Before 4 min a spectrum is (t, 2 t, 0),
        with t its time; from 4 to 8 min it is (1, 2, 3); from 8 min on (0.5, 1, 4).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(25) * 0.5
    spectra = np.empty((25, 3))
    for row, time in enumerate(times):
        if time < 4:
            spectra[row] = (time, 2 * time, 0.0)
        elif time < 8:
            spectra[row] = (1.0, 2.0, 3.0)
        else:
            spectra[row] = (0.5, 1.0, 4.0)
    return {'experiment_name': 'spectra',
            'raw_spectra': {'Cyt': {'wavelengths': np.array([500.0, 550.0, 600.0]),
                                    'time': times,
                                    'attenuation': spectra,
                                    },
                            },
            'metadata': {'events': [{'time': 4.0}, {'time': 8.0}]},
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_averaged_spectra_around_the_additions --------------------------------------
def test_averaged_spectra_around_the_additions() -> None:
    """
    ---- Summary ----
    Main function to check the average spectrum, and its spread, in the window before
    each addition and in the last window.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    2 min windows ending 0.5 min before the next addition (or the end): 1.5 to 3.5,
    5.5 to 7.5 and 9.5 to 11.5 min, five spectra each. In the first, t = 1.5, 2, 2.5,
    3, 3.5: mean 2.5, spread sqrt((1 + 0.25 + 0 + 0.25 + 1) / 4) = 0.7906, so the
    spectrum (t, 2 t, 0) averages to (2.5, 5, 0) with spread (0.7906, 1.5811, 0).

    ---- Helpers ----
    _spectra_experiment_builder
    """

    experiment = spectral_averager(_spectra_experiment_builder(),
                                   'Cyt',
                                   'attenuation',
                                   window_minutes=2.0,
                                   gap_minutes=0.5,
                                   final_window_gap_minutes=0.5,
                                   expected_events=2,
                                   )
    averages = experiment['spectral_averages']
    windows = averages['windows']
    assert list(windows) == ['average0', 'average1', 'average2']
    assert averages['roles'] == {'penultimate': 'average1', 'final': 'average2'}
    assert np.allclose(averages['wavelengths'], [500.0, 550.0, 600.0])
    assert [windows[name]['n_spectra'] for name in windows] == [5, 5, 5]
    assert np.allclose(windows['average0']['mean'], [2.5, 5.0, 0.0])
    assert np.allclose(windows['average0']['sd'],
                       [np.sqrt(0.625), 2 * np.sqrt(0.625), 0.0],
                       )
    assert np.allclose(windows['average1']['mean'], [1.0, 2.0, 3.0])
    assert np.allclose(windows['average2']['mean'], [0.5, 1.0, 4.0])
    assert np.allclose(windows['average2']['sd'], 0.0)
    assert np.isclose(windows['average1']['start_time'], 5.5)
    assert np.isclose(windows['average1']['end_time'], 7.5)


# ---- test_baseline_starts_with_the_recording -----------------------------------------
def test_baseline_starts_with_the_recording() -> None:
    """
    ---- Summary ----
    Main function to check that the baseline window of the averaged spectra starts
    where the recording starts when the window would begin before it, as the windows
    of the processing do.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Additions at 2 and 8 min, 2 min windows ending 0.5 min before the next addition:
    the baseline ends at 1.5 min and would start at -0.5 min, so it starts at 0. Its
    spectra are at t = 0, 0.5, 1 and 1.5 min: mean 0.75, so (t, 2 t, 0) averages to
    (0.75, 1.5, 0). The next window runs from 5.5 to 7.5 min, after the addition at 2.

    ---- Helpers ----
    _spectra_experiment_builder
    """

    made_up = _spectra_experiment_builder()
    made_up['metadata']['events'] = [{'time': 2.0}, {'time': 8.0}]
    experiment = spectral_averager(made_up,
                                   'Cyt',
                                   'attenuation',
                                   window_minutes=2.0,
                                   gap_minutes=0.5,
                                   final_window_gap_minutes=0.5,
                                   )
    windows = experiment['spectral_averages']['windows']
    assert list(windows) == ['average0', 'average1', 'average2']
    assert np.isclose(windows['average0']['start_time'], 0.0)
    assert np.isclose(windows['average0']['end_time'], 1.5)
    assert windows['average0']['n_spectra'] == 4
    assert np.allclose(windows['average0']['mean'], [0.75, 1.5, 0.0])
    assert np.isclose(windows['average1']['start_time'], 5.5)


# ---- test_difference_of_two_known_spectra --------------------------------------------
def test_difference_of_two_known_spectra() -> None:
    """
    ---- Summary ----
    Main function to check that the difference spectrum is the first averaged spectrum
    minus the second, for the usual pair (before and after the last addition) and for
    a pair chosen by name.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    (1, 2, 3) - (0.5, 1, 4) = (0.5, 1, -1); (2.5, 5, 0) - (1, 2, 3) = (1.5, 3, -3).

    ---- Helpers ----
    _spectra_experiment_builder
    """

    experiment = spectral_averager(_spectra_experiment_builder(),
                                   'Cyt',
                                   'attenuation',
                                   window_minutes=2.0,
                                   gap_minutes=0.5,
                                   )
    difference = difference_spectrum_calculator(experiment)['difference_spectrum']
    assert np.allclose(difference['spectrum'], [0.5, 1.0, -1.0])
    assert difference['minuend'] == 'average1'
    assert difference['subtrahend'] == 'average2'
    assert np.allclose(difference['wavelengths'], [500.0, 550.0, 600.0])
    chosen = difference_spectrum_calculator(experiment, 'average0', 'average1')
    assert np.allclose(chosen['difference_spectrum']['spectrum'], [1.5, 3.0, -3.0])


# ---- test_difference_needs_its_averages ----------------------------------------------
def test_difference_needs_its_averages() -> None:
    """
    ---- Summary ----
    Main function to check that a difference is refused when the averaged spectra have
    not been worked out, when a window does not exist, and when the last window does
    not fit after the last addition.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A 4 min window ending at 11.5 min starts at 7.5 min, before the addition at 8 min.

    ---- Helpers ----
    _spectra_experiment_builder
    """

    with pytest.raises(ValueError):
        difference_spectrum_calculator(_spectra_experiment_builder())
    experiment = spectral_averager(_spectra_experiment_builder(),
                                   'Cyt',
                                   'attenuation',
                                   window_minutes=2.0,
                                   gap_minutes=0.5,
                                   )
    with pytest.raises(ValueError):
        difference_spectrum_calculator(experiment, 'average7', 'final')
    with pytest.raises(ValueError):
        spectral_averager(_spectra_experiment_builder(),
                          'Cyt',
                          'attenuation',
                          window_minutes=4.0,
                          gap_minutes=0.5,
                          )


# ---- test_average_over_three_runs ----------------------------------------------------
def test_average_over_three_runs() -> None:
    """
    ---- Summary ----
    Main function to check the mean, spread, standard error and number of runs over
    three repeats, and that a run without a window is left out of that window only.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    First window: 1, 2, 3 -> mean 2, spread sqrt((1 + 0 + 1) / 2) = 1, standard error
    1 / sqrt(3) = 0.5774, N 3. Second window (run 3 has none): 4, 6 -> mean 5, spread
    sqrt((1 + 1) / 1) = 1.4142, standard error 1.4142 / sqrt(2) = 1, N 2. The changes
    are 10 x the means, the differences the means - 1.

    ---- Helpers ----
    _run_builder
    """

    runs = {'control_run1': _run_builder('control_run1',
                                         {'average0': 1.0, 'average1': 4.0},
                                         ),
            'control_run2': _run_builder('control_run2',
                                         {'average0': 2.0, 'average1': 6.0},
                                         ),
            'control_run3': _run_builder('control_run3', {'average0': 3.0}),
            }
    results = triplicate_averager(runs)
    assert list(results) == ['control']
    result = results['control']
    assert result['run_numbers'] == [1, 2, 3]
    assert result['windows'] == ['average0', 'average1']
    first = result['vo2'][VO2_COLUMN]['average0']
    assert first['n'] == 3
    assert np.isclose(first['mean'], 2.0)
    assert np.isclose(first['sd'], 1.0)
    assert np.isclose(first['sem'], 1.0 / np.sqrt(3.0))
    assert np.isclose(first['change_mean'], 20.0)
    assert np.isclose(first['change_sd'], 10.0)
    assert np.isclose(first['delta_mean'], 1.0)
    assert first['run_means'] == {1: 1.0, 2: 2.0, 3: 3.0}
    second = result['vo2'][VO2_COLUMN]['average1']
    assert second['n'] == 2
    assert np.isclose(second['mean'], 5.0)
    assert np.isclose(second['sd'], np.sqrt(2.0))
    assert np.isclose(second['sem'], 1.0)
    assert np.isnan(second['run_means'][3])


# ---- test_average_needs_two_runs -----------------------------------------------------
def test_average_needs_two_runs() -> None:
    """
    ---- Summary ----
    Main function to check that a condition with a single run gives no average, and
    that two runs give a mean and spread but are kept apart from other conditions.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VO2_COLUMN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Knockdown: 10, 20 -> mean 15, spread sqrt((25 + 25) / 1) = 7.0711, N 2.

    ---- Helpers ----
    _run_builder
    """

    runs = {'control_run1': _run_builder('control_run1', {'average0': 1.0}),
            'knockdown_run1': _run_builder('knockdown_run1', {'average0': 10.0}),
            'knockdown_run2': _run_builder('knockdown_run2', {'average0': 20.0}),
            }
    results = triplicate_averager(runs)
    assert list(results) == ['knockdown']
    stats = results['knockdown']['vo2'][VO2_COLUMN]['average0']
    assert stats['n'] == 2
    assert np.isclose(stats['mean'], 15.0)
    assert np.isclose(stats['sd'], np.sqrt(50.0))
