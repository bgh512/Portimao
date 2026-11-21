"""
Tests of the export at the end of the import: the size of the spectra and where each file goes.
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
from utils_shared.individual_experiment_exporter import (size_describer,
                                                         spectra_size_estimator,
                                                         )
from utils_shared.schema import TIME_COLUMN
from utils_viewer.viewer_preview import import_data_exporter, ViewerSession


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


# ---- HELPERS -------------------------------------------------------------------------


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(info: dict, cfg: object, fit: object) -> dict:
    """
    ---- Summary ----
    Helper function to stand in for the reading of a file: a made-up recording of 0 to
    10 min, one point a minute, with the OD values and events it is given, as the
    processing hands them back.

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
        twice the time.

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
    return {'experiment': dict(tables,
                               experiment_name=info['name'],
                               metadata=metadata,
                               raw_spectra={},
                               ),
            }


# ---- _metadata_reader ----------------------------------------------------------------
def _metadata_reader(path: Path) -> dict:
    """
    ---- Summary ----
    Helper function to read the Metadata sheet of a workbook as {field: value}.

    ---- Inputs ----
    path : Path
        The workbook.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {field: value} of the Metadata sheet.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    sheet = pd.read_excel(path, sheet_name='Metadata')
    return dict(zip(sheet['Field'], sheet['Value']))


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


# ---- test_trimmed_and_whole_go_to_their_folders --------------------------------------
def test_trimmed_and_whole_go_to_their_folders(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch,
                                               ) -> None:
    """
    ---- Summary ----
    Main function to check where the export of the import writes: a trimmed file's
    trimmed data in its own folder, with the edges, OD values and labels, and its whole
    recording in full/ without the edges; a file not trimmed has no full/.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the reading of the files.

    ---- Globals read ----
    EVENTS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Kept from 2 to 8 min of a point a minute: 7 points, the addition at 5 - 2 = 3 min.

    ---- Helpers ----
    _metadata_reader
    _session_maker
    """

    # ---- 1 Export a trimmed and an untrimmed file ------------------------------------
    root = tmp_path / 'results'
    session = _session_maker(root, monkeypatch)
    limits = {'run1': {'trim_start': 2.0,
                       'trim_end': 8.0,
                       'ignore_start': 1.0,
                       'ignore_end': 0.5,
                       },
              'run2': {'trim_start': None,
                       'trim_end': None,
                       'ignore_start': 1.0,
                       'ignore_end': 0.0,
                       },
              }
    details = {'run1': {'OD': 0.5,
                        'volume': 1.0,
                        'dilution_factor': 2.0,
                        'events': EVENTS,
                        },
               'run2': {'events': EVENTS},
               }
    assert import_data_exporter(session, limits, details, 'summary') == []
    assert session.exported == [root]

    # ---- 2 The trimmed data, with the edges, OD values and labels --------------------
    trimmed = root / 'run1' / 'run1.xlsx'
    assert len(pd.read_excel(trimmed, sheet_name='CcO2')) == 7
    metadata = _metadata_reader(trimmed)
    assert float(metadata['trimmed_before_minutes']) == 2.0
    assert float(metadata['trimmed_after_minutes']) == 8.0
    assert float(metadata['ignore_first_minutes']) == 1.0
    assert float(metadata['ignore_last_minutes']) == 0.5
    assert float(metadata['OD']) == 0.5
    events = pd.read_excel(trimmed, sheet_name='Events')
    assert list(events['label']) == ['KCN']
    assert list(events['time_min']) == [3.0]

    # ---- 3 The whole recording, without the edges ------------------------------------
    whole = root / 'run1' / 'full' / 'run1.xlsx'
    assert len(pd.read_excel(whole, sheet_name='CcO2')) == 11
    metadata = _metadata_reader(whole)
    assert 'trimmed_before_minutes' not in metadata
    assert 'ignore_first_minutes' not in metadata
    assert float(metadata['dilution_factor']) == 2.0
    assert list(pd.read_excel(whole, sheet_name='Events')['time_min']) == [5.0]

    # ---- 4 Nothing called full for a file not trimmed --------------------------------
    assert (root / 'run2' / 'run2.xlsx').is_file()
    assert not (root / 'run2' / 'full').exists()


# ---- test_new_edges_export_again -----------------------------------------------------
def test_new_edges_export_again(tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch,
                                ) -> None:
    """
    ---- Summary ----
    Main function to check the export once the edges change: a whole recording already
    written is left as it is, a file that has just become trimmed gets one, and a file
    no longer trimmed loses the one written for it.

    ---- Inputs ----
    tmp_path : Path
        Empty folder from pytest.
    monkeypatch : pytest.MonkeyPatch
        Used to stand in for the reading of the files.

    ---- Globals read ----
    EVENTS (module constant).

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _metadata_reader
    _session_maker
    """

    # ---- 1 Export with run1 trimmed --------------------------------------------------
    root = tmp_path / 'results'
    session = _session_maker(root, monkeypatch)
    details = {'run1': {'events': EVENTS}, 'run2': {'events': EVENTS}}
    limits = {'run1': {'trim_start': 2.0,
                       'trim_end': 8.0,
                       'ignore_start': 0.0,
                       'ignore_end': 0.0,
                       },
              'run2': {'trim_start': None,
                       'trim_end': None,
                       'ignore_start': 0.0,
                       'ignore_end': 0.0,
                       },
              }
    assert import_data_exporter(session, limits, details, 'summary') == []
    whole = root / 'run1' / 'full' / 'run1.xlsx'
    whole.write_bytes(b'left as it is')

    # ---- 2 New edges on run1 leave its whole recording alone -------------------------
    limits['run1'] = dict(limits['run1'], trim_start=3.0)
    assert import_data_exporter(session,
                                limits,
                                details,
                                'summary',
                                names=['run1'],
                                keep_full=True,
                                ) == []
    assert whole.read_bytes() == b'left as it is'
    trimmed = root / 'run1' / 'run1.xlsx'
    assert float(_metadata_reader(trimmed)['trimmed_before_minutes']) == 3.0

    # ---- 3 run2 trimmed now gets a whole recording; run1 untrimmed loses its own -----
    limits['run1'] = dict(limits['run1'], trim_start=None, trim_end=None)
    limits['run2'] = dict(limits['run2'], trim_end=9.0)
    assert import_data_exporter(session,
                                limits,
                                details,
                                'summary',
                                keep_full=True,
                                ) == []
    assert not (root / 'run1' / 'full').exists()
    assert (root / 'run2' / 'full' / 'run2.xlsx').is_file()
    assert 'trimmed_before_minutes' not in _metadata_reader(trimmed)
