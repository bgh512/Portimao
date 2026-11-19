"""
Tests of the parts of the .paf reader that deal with unusual files, on made-up values
with results worked out by hand.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.paf_reader import (_event_lister,
                                     _spectrum_time_finder,
                                     _trace_title_maker,
                                     _transmission_converter,
                                     PafError,
                                     )


# ---- CONSTANTS -----------------------------------------------------------------------
CLOCK_S = np.arange(6) * 0.5  # six time points, 0.5 s apart
MICRO_SIGN = 'µ'
GREEK_MU = 'μ'


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_additions_copies_are_joined ------------------------------------------------
def test_additions_copies_are_joined() -> None:
    """
    ---- Summary ----
    Main function to check that the two stored copies of an addition (the first
    without a position) give one addition, in the order of their positions.

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

    found = [('Event 2', 'second', 0),
             ('Event 2', 'second', 40),
             ('Event 1', 'first', 0),
             ('Event 1', 'first', 10),
             ]
    assert _event_lister(found) == [
        {'name': 'Event 1', 'text': 'first', 'datapoint': 10},
        {'name': 'Event 2', 'text': 'second', 'datapoint': 40},
        ]


# ---- test_additions_under_one_name_are_all_kept --------------------------------------
def test_additions_under_one_name_are_all_kept(capsys: pytest.CaptureFixture) -> None:
    """
    ---- Summary ----
    Main function to check that two additions stored under the same name stay two
    additions, each with its own text, and that the user is told.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        Catches what is printed.

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

    found = [('Event 1', '1 ul', 0),
             ('Event 1', '1 ul', 10),
             ('Event 1', '2 ul', 30),
             ]
    assert _event_lister(found) == [
        {'name': 'Event 1', 'text': '1 ul', 'datapoint': 10},
        {'name': 'Event 1', 'text': '2 ul', 'datapoint': 30},
        ]
    assert 'WARNING' in capsys.readouterr().out


# ---- test_addition_without_position_is_left_out --------------------------------------
def test_addition_without_position_is_left_out(capsys: pytest.CaptureFixture) -> None:
    """
    ---- Summary ----
    Main function to check that an addition with no stored position is left out and
    that the user is told.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        Catches what is printed.

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

    assert _event_lister([('Event 1', 'lost', 0)]) == []
    assert 'WARNING' in capsys.readouterr().out


# ---- test_spectrum_times_with_equal_counts -------------------------------------------
def test_spectrum_times_with_equal_counts(capsys: pytest.CaptureFixture) -> None:
    """
    ---- Summary ----
    Main function to check that as many spectra as time points take the clock's times,
    in minutes, without a message.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        Catches what is printed.

    ---- Globals read ----
    CLOCK_S (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time (min) = time (s) / 60.

    ---- Helpers ----
    None.
    """

    times = _spectrum_time_finder(CLOCK_S, 6, 'Cyt', 'made_up.paf')
    assert np.array_equal(times, CLOCK_S / 60.0)
    assert capsys.readouterr().out == ''


# ---- test_spectrum_times_with_fewer_spectra ------------------------------------------
def test_spectrum_times_with_fewer_spectra(capsys: pytest.CaptureFixture) -> None:
    """
    ---- Summary ----
    Main function to check that fewer spectra than time points take the first times of
    the clock and that the user is told.

    ---- Inputs ----
    capsys : pytest.CaptureFixture
        Catches what is printed.

    ---- Globals read ----
    CLOCK_S (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Four spectra on a clock of 0, 0.5, ... 2.5 s are at 0, 0.5, 1 and 1.5 s.

    ---- Helpers ----
    None.
    """

    times = _spectrum_time_finder(CLOCK_S, 4, 'Cyt', 'made_up.paf')
    assert np.allclose(times * 60.0, [0.0, 0.5, 1.0, 1.5])
    assert 'WARNING' in capsys.readouterr().out


# ---- test_spectrum_times_with_more_spectra -------------------------------------------
def test_spectrum_times_with_more_spectra() -> None:
    """
    ---- Summary ----
    Main function to check that more spectra than time points stop the file, with the
    file's name in the message.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CLOCK_S (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    with pytest.raises(PafError, match='made_up.paf'):
        _spectrum_time_finder(CLOCK_S, 7, 'Cyt', 'made_up.paf')


# ---- test_transmission_from_the_stored_logarithms ------------------------------------
def test_transmission_from_the_stored_logarithms() -> None:
    """
    ---- Summary ----
    Main function to check the transmission worked out from the stored logarithms.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Counts of 50 and 400 over a reference of 100 and 200 give 0.5 and 2.

    ---- Helpers ----
    None.
    """

    counts = np.log10(np.array([[50.0, 400.0]]))
    reference = np.log10(np.array([100.0, 200.0]))
    assert np.allclose(_transmission_converter(counts, reference),
                       [[0.5, 2.0]],
                       rtol=1e-12,
                       )


# ---- test_transmission_is_empty_without_reference_counts -----------------------------
def test_transmission_is_empty_without_reference_counts() -> None:
    """
    ---- Summary ----
    Main function to check that the transmission is empty, never infinite, where the
    reference has zero counts, and is untouched at the other wavelengths.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    log10(0) is minus infinity: 50 counts over 0 would be infinite, and 0 over 0 has
    no value. Both are left empty. 50 over 100 is 0.5.

    ---- Helpers ----
    None.
    """

    with np.errstate(divide='ignore'):
        counts = np.log10(np.array([[50.0, 50.0], [0.0, 50.0]]))
        reference = np.log10(np.array([0.0, 100.0]))
    transmission = _transmission_converter(counts, reference)
    assert np.isnan(transmission[:, 0]).all()
    assert np.allclose(transmission[:, 1], [0.5, 0.5], rtol=1e-12)


# ---- test_trace_titles_follow_the_unit_of_the_file -----------------------------------
def test_trace_titles_follow_the_unit_of_the_file() -> None:
    """
    ---- Summary ----
    Main function to check the column titles of the traces: the oxygen titles carry
    the file's unit, written with the micro sign, and the OCR column keeps its name.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MICRO_SIGN, GREEK_MU (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert _trace_title_maker('CcO2',
                              f'{MICRO_SIGN}M',
                              ) == f'Measured O2 ({MICRO_SIGN}M)'
    assert _trace_title_maker('CsO2', f'{GREEK_MU}M') == f'Set O2 ({MICRO_SIGN}M)'
    assert _trace_title_maker('CcO2', 'kPa') == 'Measured O2 (kPa)'
    assert _trace_title_maker('CcO2', '') == 'Measured O2 (uM)'
    assert _trace_title_maker('VoO2', f'{MICRO_SIGN}M/min') == 'VoO2'
