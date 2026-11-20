"""
Tests of the parts of the .paf reader that deal with unusual files, on made-up values
with results worked out by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import struct
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import concentration_formatter
from utils_shared.paf_reader import (_event_lister,
                                     _event_time_adder,
                                     _short_trace_describer,
                                     _spectrum_time_finder,
                                     _trace_title_maker,
                                     _transmission_converter,
                                     experiment_paf_loader,
                                     experiment_summary_reader,
                                     MARK,
                                     PafError,
                                     stream_extractor,
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


# ---- test_addition_outside_the_recording_is_left_out ---------------------------------
def test_addition_outside_the_recording_is_left_out(capsys: pytest.CaptureFixture,
                                                    ) -> None:
    """
    ---- Summary ----
    Main function to check that an addition stored outside the recording is left out
    with a warning that names it, that the others get their time, and that the quiet
    reading leaves out the same addition without printing.

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
    Spectrum 3 is row 2 of the clock: 1.0 s = 1/60 min.

    ---- Helpers ----
    None.
    """

    events = [{'name': 'Event 1', 'text': 'inside', 'datapoint': 3},
              {'name': 'Event 2', 'text': 'too late', 'datapoint': 7},
              {'name': 'Event 3', 'text': 'too early', 'datapoint': 0},
              ]
    expected = [{'name': 'Event 1',
                 'text': 'inside',
                 'datapoint': 3,
                 'time': 1.0 / 60.0,
                 'row_index': 2,
                 },
                ]
    assert _event_time_adder(events, CLOCK_S / 60.0, 'made_up.paf') == expected
    printed = capsys.readouterr().out
    assert 'made_up.paf' in printed
    assert 'too late' in printed and 'too early' in printed
    assert _event_time_adder(events,
                             CLOCK_S / 60.0,
                             'made_up.paf',
                             is_quiet=True,
                             ) == expected
    assert capsys.readouterr().out == ''


# ---- test_missing_concentration_is_written_by_the_helper -----------------------------
def test_missing_concentration_is_written_by_the_helper() -> None:
    """
    ---- Summary ----
    Main function to check that the shared helper writes every concentration, a
    missing one included.

    ---- Inputs ----
    None.

    ---- Globals read ----
    MICRO_SIGN (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    2000 uM = 2 mM; 1 500 000 uM = 1.5 M.

    ---- Helpers ----
    None.
    """

    assert concentration_formatter(None) == f'? {MICRO_SIGN}M'
    assert concentration_formatter(8) == f'8 {MICRO_SIGN}M'
    assert concentration_formatter(2000) == '2 mM'
    assert concentration_formatter(1_500_000) == '1.5 M'


# ---- test_rate_trace_short_by_its_usual_gap_is_not_reported --------------------------
def test_rate_trace_short_by_its_usual_gap_is_not_reported() -> None:
    """
    ---- Summary ----
    Main function to check that a trace short by the points the instrument always
    leaves empty is not reported, even in a short recording, while one short by more
    is, with its length in seconds.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    In a recording of 1343 points, 20 points are 1.5 %, more than the 1 % that is
    always let pass; 10 points are 0.7 %. 40 points of 0.5 s are 20 s.

    ---- Helpers ----
    None.
    """

    assert _short_trace_describer('VoO2', 20, 1343, 0.5, 20) == ''
    assert _short_trace_describer('CcO2', 10, 1343, 0.5, 0) == ''
    assert '20 points' in _short_trace_describer('CcO2', 20, 1343, 0.5, 0)
    message = _short_trace_describer('VoO2', 40, 1343, 0.5, 20)
    assert '40 points' in message and '20 s' in message


# ---- test_trace_with_disagreeing_lengths_is_noted ------------------------------------
def test_trace_with_disagreeing_lengths_is_noted() -> None:
    """
    ---- Summary ----
    Main function to check that a trace whose two stored lengths disagree is not read
    and is noted under its name with the reason, both numbers included.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The two lengths sit 28 and 20 bytes before the end of the first record.

    ---- Helpers ----
    None.
    """

    data = bytearray(64)
    struct.pack_into('<I', data, 64 - 28, 5)
    struct.pack_into('<I', data, 64 - 20, 4)
    records = [{'type': 'DataItem',
                'off': 0,
                'end': 64,
                'tokens': [('DataItem', 0, 0), ('Espana', 0, 0), ('VoO2', 0, 0)],
                },
               {'type': 'Measurement', 'off': 64, 'end': 64, 'tokens': []},
               ]
    traces, skipped = stream_extractor(bytes(data), records)
    assert traces == []
    assert list(skipped) == ['VoO2']
    assert '5 and 4' in skipped['VoO2']


# ---- test_unreadable_files_give_plain_messages ---------------------------------------
def test_unreadable_files_give_plain_messages(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a file that is missing, too small, not a .paf or
    without a clock is refused with a message that starts with its name and holds no
    Python error name, by both the quick look and the full reading.

    ---- Inputs ----
    tmp_path : Path
        Empty folder made by pytest.

    ---- Globals read ----
    MARK (constant of the reader).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Writes three small files in tmp_path (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    contents = {'too_small.paf': b'abc',
                'not_a_paf.paf': bytes(2048),
                'no_clock.paf': MARK + bytes(2048),
                }
    for name, content in contents.items():
        (tmp_path / name).write_bytes(content)
    words = {'absent.paf': 'could not be opened',
             'too_small.paf': 'too small',
             'not_a_paf.paf': 'not a recording',
             'no_clock.paf': 'no clock',
             }
    for name, word in words.items():
        for reader in (experiment_summary_reader, experiment_paf_loader):
            with pytest.raises(PafError) as caught:
                reader(tmp_path / name)
            message = str(caught.value)
            assert message.startswith(f'{name}: ')
            assert message.count(name) == 1
            assert word in message
            assert 'Error' not in message
