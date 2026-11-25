"""
Tests of the spectra exports: the size of each part, what the quick export of the trim step and the Export step (5.9) write and where, and the workbook that lists the csv files.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import contextlib
from pathlib import Path
from types import SimpleNamespace

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import utils_viewer.viewer_preview as viewer_preview
import utils_viewer.viewer_stages as viewer_stages
from utils_shared.individual_experiment_exporter import (experiment_workbook_exporter,
                                                         size_describer,
                                                         spectra_csv_exporter,
                                                         spectra_size_estimator,
                                                         workbook_size_estimator,
                                                         )
from utils_shared.schema import TIME_COLUMN
from utils_viewer.viewer_preview import (EXPORT_PARTS,
                                         import_data_exporter,
                                         ViewerSession,
                                         )


# ---- CONSTANTS -----------------------------------------------------------------------
# 2 + 1 + 2 = 5 bytes for one value of the three kinds together
BYTES_PER_VALUE = {'transmission': 2, 'intensity': 1, 'attenuation': 2}
OD_KEYS = ('OD', 'volume', 'dilution_factor')
# one addition at 5 min in each made-up recording of 0 to 10 min
EVENTS = [{'datapoint': 6,
           'time': 5.0,
           'text': '100uM KCN',
           'label': 'KCN',
           'concentration_uM': 100.0,
           },
          ]
# the csv file of the transmission spectra of the made-up spectrometer
CSV_NAME = 'Cyt_transmiss.csv'


# ---- HELPERS -------------------------------------------------------------------------


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(info: dict, cfg: object, fit: object) -> dict:
    """
    ---- Summary ----
    Helper function to stand in for the reading of a file: a made-up recording of 0 to
    10 min, one point and one spectrum of three wavelengths a minute, with the OD
    values and events it is given, as the processing hands them back.

    ---- Inputs ----
    info : dict
        Per-file information (preview_info_builder): name, OD values and events.
    cfg : object
        Settings of the processing; not used.
    fit : object
        Fit of the processing; not used.

    ---- Globals read ----
    EVENTS, OD_KEYS (module constants).

    ---- Outputs ----
    dict
        {'experiment': experiment} (DATA_FORMAT.md), the oxygen and OCR tables equal to
        twice the time, and the transmission spectra of one spectrometer, Cyt, all 1.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(0.0, 10.5, 1.0)
    tables = {key: pd.DataFrame({TIME_COLUMN: times, column: 2.0 * times})
              for key, column in (('CcO2', 'Measured O2 (µM)'),
                                  ('CsO2', 'Set O2 (µM)'),
                                  ('VoO2', 'VoO2'),
                                  )
              }
    metadata = {'paf_file': f"{info['name']}.paf",
                'events': [dict(event) for event in info.get('events', [])],
                'notes': '',
                }
    metadata.update({key: info[key] for key in OD_KEYS if key in info})
    spectra = {'Cyt': {'wavelengths': np.array([500.0, 510.0, 520.0]),
                       'time': times.copy(),
                       'spectrum_indices': np.arange(len(times)),
                       'transmission': np.ones((len(times), 3)),
                       },
               }
    return {'experiment': dict(tables,
                               experiment_name=info['name'],
                               metadata=metadata,
                               raw_spectra=spectra,
                               ),
            }


# ---- _limits_maker -------------------------------------------------------------------
def _limits_maker(run1_trim: tuple, run2_trim: tuple) -> dict:
    """
    ---- Summary ----
    Helper function to build the trim and ignore limits of the two made-up files, with
    nothing ignored.

    ---- Inputs ----
    run1_trim : tuple
        (trim start, trim end) of run1 in minutes, None for no trim.
    run2_trim : tuple
        The same for run2.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {name: {'trim_start': start,
                   'trim_end': end,
                   'ignore_start': 0.0,
                   'ignore_end': 0.0,
                   }
            for name, (start, end) in (('run1', run1_trim), ('run2', run2_trim))
            }


# ---- _session_maker ------------------------------------------------------------------
def _session_maker(root: Path, monkeypatch: pytest.MonkeyPatch) -> ViewerSession:
    """
    ---- Summary ----
    Helper function to set up a session of two made-up files whose reading is stood in
    for by _experiment_maker, with no window.

    ---- Inputs ----
    root : Path
        Results folder.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the reading of the files.

    ---- Globals read ----
    None.

    ---- Outputs ----
    ViewerSession
        The session, with the files run1 and run2 of 10 min each.

    ---- Globals mutated ----
    None. Replaces the processing in viewer_preview for the test (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _experiment_maker
    """

    monkeypatch.setattr(viewer_preview, 'experiment_data_processor', _experiment_maker)
    summaries = [{'name': name, 'path': Path(f'{name}.paf'), 'duration_min': 10.0}
                 for name in ('run1', 'run2')
                 ]
    window = SimpleNamespace(output_capturer=contextlib.nullcontext)
    return ViewerSession(summaries=summaries, export_root=root, window=window)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_size_in_words --------------------------------------------------------------
def test_size_in_words() -> None:
    """
    ---- Summary ----
    Main function to check how a size is put in words: two significant figures, in GB
    from 10^9 bytes and in MB from 10^6, and nothing at all said as such.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    1 234 567 890 bytes = 1.23 GB, about 1.2 GB; 352 000 000 bytes = 352 MB, about 350.

    ---- Helpers ----
    None.
    """

    assert size_describer(0) == 'none in these files'
    assert size_describer(999_999) == 'under 1 MB'
    assert size_describer(1_000_000) == 'about 1 MB'
    assert size_describer(352_000_000) == 'about 350 MB'
    assert size_describer(1_234_567_890) == 'about 1.2 GB'
    assert size_describer(14_480_000_000) == 'about 14 GB'


# ---- test_spectra_size_by_hand -------------------------------------------------------
def test_spectra_size_by_hand() -> None:
    """
    ---- Summary ----
    Main function to check the size of the spectra csv files against sums worked out by
    hand: a file trimmed at both ends, one not trimmed with two spectrometers, one with
    no spectra, and one trimmed at its start only.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BYTES_PER_VALUE (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    run1: 60 min kept from 10 to 40, so half of 600 spectra x 100 wavelengths x 5 bytes
    = 150 000 trimmed; the whole 600 x 100 x 5 = 300 000.
    run2: not trimmed, 2 x 200 x 50 x 5 = 100 000 trimmed and nothing whole.
    run3: no spectra.
    run4: 30 min from 6 to the end, so 24 / 30 = 0.8 of 300 x 10 x 5 = 12 000 trimmed;
    the whole 300 x 10 x 5 = 15 000.

    ---- Helpers ----
    None.
    """

    summaries = [{'name': 'run1',
                  'duration_min': 60.0,
                  'spectra_shapes': {'Cyt': [600, 100]},
                  },
                 {'name': 'run2',
                  'duration_min': 20.0,
                  'spectra_shapes': {'Cyt': [200, 50], 'NADH': [200, 50]},
                  },
                 {'name': 'run3', 'duration_min': 20.0},
                 ]
    limits = {'run1': {'trim_start': 10.0, 'trim_end': 40.0},
              'run2': {'trim_start': None, 'trim_end': None},
              }
    assert spectra_size_estimator(summaries, limits, BYTES_PER_VALUE) == (250_000.0,
                                                                          300_000.0,
                                                                          )
    start_only = [{'name': 'run4',
                   'duration_min': 30.0,
                   'spectra_shapes': {'Cyt': [300, 10]},
                   },
                  ]
    found = spectra_size_estimator(start_only,
                                   {'run4': {'trim_start': 6.0, 'trim_end': None}},
                                   BYTES_PER_VALUE,
                                   )
    assert found == pytest.approx((12_000.0, 15_000.0))


# ---- test_workbook_size_by_hand ------------------------------------------------------
def test_workbook_size_by_hand() -> None:
    """
    ---- Summary ----
    Main function to check the size of the workbooks against sums worked out by hand:
    a file trimmed at both ends, one not trimmed, and one whose number of data points
    is not known.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    At 10 bytes a data point:
    run1: 60 min kept from 10 to 40, so half of 600 points x 10 = 3 000 trimmed; the
    whole 600 x 10 = 6 000.
    run2: not trimmed, 200 x 10 = 2 000 trimmed and nothing whole.
    run3: no number of points, so nothing.
    Together 5 000 trimmed and 6 000 whole.

    ---- Helpers ----
    None.
    """

    summaries = [{'name': 'run1', 'duration_min': 60.0, 'frames': 600},
                 {'name': 'run2', 'duration_min': 20.0, 'frames': 200},
                 {'name': 'run3', 'duration_min': 20.0},
                 ]
    limits = {'run1': {'trim_start': 10.0, 'trim_end': 40.0},
              'run2': {'trim_start': None, 'trim_end': None},
              }
    assert workbook_size_estimator(summaries, limits, 10.0) == (5_000.0, 6_000.0)
    assert workbook_size_estimator(summaries, {}, 10.0) == (8_000.0, 0.0)


# ---- test_each_choice_writes_its_files -----------------------------------------------
def test_each_choice_writes_its_files(tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch,
                                      ) -> None:
    """
    ---- Summary ----
    Main function to check what each choice of a spectra export writes for a trimmed
    file and for one not trimmed: only csv files, never a workbook; the trimmed spectra
    with 'trimmed' and 'full', the whole recording's only for the trimmed file with
    'full' and 'full_only', each cut as its name says.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the reading of the files.

    ---- Globals read ----
    CSV_NAME, EVENTS (module constants); EXPORT_PARTS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A spectrum a minute from 0 to 10 min: 11 spectra in the whole recording, 7 kept
    from 2 to 8 min; a csv file has one column more, the wavelengths.

    ---- Helpers ----
    _limits_maker
    _session_maker
    """

    limits = _limits_maker((2.0, 8.0), (None, None))
    details = {'run1': {'events': EVENTS}, 'run2': {'events': EVENTS}}
    assert EXPORT_PARTS == {'trimmed': (True, False),
                            'full': (True, True),
                            'full_only': (False, True),
                            }
    for choice, (with_trimmed, with_full) in EXPORT_PARTS.items():
        root = tmp_path / choice
        session = _session_maker(root, monkeypatch)
        assert import_data_exporter(session, limits, details, choice) == []
        trimmed, whole = root / 'run1', root / 'run1' / 'full'

        # never a workbook
        assert list(root.rglob('*.xlsx')) == []
        # the trimmed spectra, cut to the trim edges
        assert (trimmed / CSV_NAME).is_file() == with_trimmed
        assert (root / 'run2' / CSV_NAME).is_file() == with_trimmed
        if with_trimmed:
            assert pd.read_csv(trimmed / CSV_NAME).shape == (3, 8)
            assert pd.read_csv(root / 'run2' / CSV_NAME).shape == (3, 12)
        # the whole recording only for the trimmed file
        assert (whole / CSV_NAME).is_file() == with_full
        assert not (root / 'run2' / 'full').exists()
        if with_full:
            assert pd.read_csv(whole / CSV_NAME).shape == (3, 12)


# ---- test_trimmed_and_whole_go_to_their_folders --------------------------------------
def test_trimmed_and_whole_go_to_their_folders(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch,
                                               ) -> None:
    """
    ---- Summary ----
    Main function to check where the quick export writes with the whole recordings
    chosen: a trimmed file's trimmed spectra in its own folder, on the clock of the
    trimmed data, and its whole recording's in full/ on the clock of the recording; a
    file not trimmed has no full/.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the reading of the files.

    ---- Globals read ----
    CSV_NAME, EVENTS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Kept from 2 to 8 min of a spectrum a minute: 7 spectra, at 0 to 6 min on the
    trimmed clock.

    ---- Helpers ----
    _limits_maker
    _session_maker
    """

    root = tmp_path / 'results'
    session = _session_maker(root, monkeypatch)
    limits = _limits_maker((2.0, 8.0), (None, None))
    details = {'run1': {'events': EVENTS}, 'run2': {'events': EVENTS}}
    assert import_data_exporter(session, limits, details, 'full') == []
    assert session.exported == [root]
    trimmed = pd.read_csv(root / 'run1' / CSV_NAME)
    assert list(trimmed.columns)[:2] == ['Wavelength (nm)', '0 min']
    assert list(trimmed.columns)[-1] == '6 min'
    whole = pd.read_csv(root / 'run1' / 'full' / CSV_NAME)
    assert list(whole.columns)[1] == '0 min' and list(whole.columns)[-1] == '10 min'
    assert (root / 'run2' / CSV_NAME).is_file()
    assert not (root / 'run2' / 'full').exists()


# ---- test_new_edges_export_again -----------------------------------------------------
def test_new_edges_export_again(tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch,
                                ) -> None:
    """
    ---- Summary ----
    Main function to check the quick export once the edges change: a whole recording
    already written is left as it is, a file that has just become trimmed gets one,
    and a file no longer trimmed loses the one written for it.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the reading of the files.

    ---- Globals read ----
    CSV_NAME, EVENTS (module constants).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Trimmed from 3 to 8 min: 6 spectra, 7 columns with the wavelengths.

    ---- Helpers ----
    _limits_maker
    _session_maker
    """

    # ---- 1 Export with run1 trimmed --------------------------------------------------
    root = tmp_path / 'results'
    session = _session_maker(root, monkeypatch)
    details = {'run1': {'events': EVENTS}, 'run2': {'events': EVENTS}}
    limits = _limits_maker((2.0, 8.0), (None, None))
    assert import_data_exporter(session, limits, details, 'full') == []
    whole = root / 'run1' / 'full' / CSV_NAME
    whole.write_bytes(b'left as it is')

    # ---- 2 New edges on run1 leave its whole recording alone -------------------------
    limits['run1'] = dict(limits['run1'], trim_start=3.0)
    assert import_data_exporter(session,
                                limits,
                                details,
                                'full',
                                names=['run1'],
                                keep_full=True,
                                ) == []
    assert whole.read_bytes() == b'left as it is'
    assert pd.read_csv(root / 'run1' / CSV_NAME).shape == (3, 7)

    # ---- 3 run2 trimmed now gets a whole recording; run1 untrimmed loses its own -----
    limits['run1'] = dict(limits['run1'], trim_start=None, trim_end=None)
    limits['run2'] = dict(limits['run2'], trim_end=9.0)
    assert import_data_exporter(session, limits, details, 'full', keep_full=True) == []
    assert not (root / 'run1' / 'full').exists()
    assert (root / 'run2' / 'full' / CSV_NAME).is_file()
    assert pd.read_csv(root / 'run1' / CSV_NAME).shape == (3, 12)


# ---- test_workbook_lists_the_quick_csv_files -----------------------------------------
def test_workbook_lists_the_quick_csv_files(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a workbook written after the quick export, without
    writing the spectra again, lists the csv files the quick export left beside it,
    with their number of wavelengths and spectra.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.

    ---- Globals read ----
    CSV_NAME (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The made-up file: 3 wavelengths, 11 spectra.

    ---- Helpers ----
    _experiment_maker
    """

    experiment = _experiment_maker({'name': 'run1'}, None, None)['experiment']
    written = spectra_csv_exporter(experiment, tmp_path)
    assert written == [tmp_path / 'run1' / CSV_NAME]
    assert list((tmp_path / 'run1').glob('*.xlsx')) == []
    experiment_workbook_exporter(experiment, tmp_path, keeps_spectra_list=True)
    listed = pd.read_excel(tmp_path / 'run1' / 'run1.xlsx', sheet_name='Spectral data')
    assert list(listed['CSV file']) == [CSV_NAME]
    assert list(listed['Wavelengths']) == [3]
    assert list(listed['Timepoints']) == [11]


# ---- test_export_step_offers_and_writes ----------------------------------------------
def test_export_step_offers_and_writes(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch,
                                       ) -> None:
    """
    ---- Summary ----
    Main function to check the Export step (5.9): the three choices with a file
    trimmed and the first two with none, the last answer highlighted, the answers it
    stores, and that only the third writes the whole recordings' csv files at once
    (the rest is written with the workbooks). The question, the messages and the
    export are stood in for.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the question, the messages and the export.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _limits_maker
    _session_maker
    """

    asked, exports = [], []
    picked = {'answer': 'full'}
    def chooser(question: str, options: list, default: str, **kwargs: object) -> str:
        asked.append(([key for key, _ in options], default, kwargs.get('number')))
        return picked['answer']
    def exporter(_session: object,
                 _limits: dict,
                 _details: dict,
                 choice: str,
                 **_: object,
                 ) -> list:
        exports.append(choice)
        return []
    for name, stand_in in (('choice_asker', chooser),
                           ('import_data_exporter', exporter),
                           ('info_printer', lambda *args, **kwargs: None),
                           ('guide_step_starter', lambda *args: None),
                           ('progress_clearer', lambda *args: None),
                           ):
        monkeypatch.setattr(viewer_stages, name, stand_in)
    session = _session_maker(tmp_path, monkeypatch)

    # ---- 1 A file trimmed: three choices, the third writes the full csv files --------
    answers = {}
    viewer_stages._export_chooser(session,
                                  answers,
                                  {'export_choice': 'trimmed'},
                                  _limits_maker((2.0, 8.0), (None, None)),
                                  {},
                                  )
    assert asked[-1] == (['summary', 'trimmed', 'full'], 'trimmed', '5.9')
    assert answers == {'export_choice': 'full', 'export_spectra': True}
    assert exports == ['full_only']

    # ---- 2 No file trimmed: no third choice; a saved third falls back to the first ---
    picked['answer'] = 'summary'
    viewer_stages._export_chooser(session,
                                  answers,
                                  {'export_choice': 'full'},
                                  _limits_maker((None, None), (None, None)),
                                  {},
                                  )
    assert asked[-1] == (['summary', 'trimmed'], 'summary', '5.9')
    assert answers == {'export_choice': 'summary', 'export_spectra': False}
    assert exports == ['full_only']
