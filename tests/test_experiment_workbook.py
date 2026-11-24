"""
Tests of the workbook of one experiment: its sheets, their headings and the sheet that says how the numbers were worked out.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.individual_experiment_exporter import (_processing_table_builder,
                                                         experiment_workbook_exporter,
                                                         )
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
# four spectra, one a minute
TIMES_MIN = np.array([0.0, 1.0, 2.0, 3.0])
# absorbance of the two made-up haems (mOD): oxidised in the first two spectra, reduced
# in the last two
ABSORBANCE_MOD = {'bH': np.array([12.0, 12.0, 4.0, 4.0]),
                  'bL': np.array([6.0, 6.0, 2.0, 2.0]),
                  }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _haem_table_maker ---------------------------------------------------------------
def _haem_table_maker(values: dict) -> pd.DataFrame:
    """
    ---- Summary ----
    Helper function to make a haem table of the made-up experiment: the time, the
    spectrum index and one column per haem.

    ---- Inputs ----
    values : dict
        {haem: its four values}.

    ---- Globals read ----
    TIMES_MIN (module constant); TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    pd.DataFrame
        The table, four rows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return pd.DataFrame({TIME_COLUMN: TIMES_MIN,
                         SPECTRUM_INDEX_COLUMN: np.arange(1, 5),
                         **values,
                         },
                        )


# ---- _imported_experiment_maker ------------------------------------------------------
def _imported_experiment_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make an experiment as the import leaves it: the oxygen and the
    OCR (twice the time), no events, and nothing worked out.

    ---- Inputs ----
    None.

    ---- Globals read ----
    TIMES_MIN (module constant); TIME_COLUMN.

    ---- Outputs ----
    dict
        Experiment dictionary (DATA_FORMAT.md) called run1.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    tables = {key: pd.DataFrame({TIME_COLUMN: TIMES_MIN, column: 2.0 * TIMES_MIN})
              for key, column in (('CcO2', 'Measured O2 (µM)'),
                                  ('CsO2', 'Set O2 (µM)'),
                                  ('VoO2', 'VoO2'),
                                  )
              }
    return dict(tables,
                experiment_name='run1',
                metadata={'paf_file': 'run1.paf', 'events': [], 'notes': ''},
                raw_spectra={},
                )


# ---- _processed_experiment_maker -----------------------------------------------------
def _processed_experiment_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make an experiment as the processing leaves it: the imported
    one with the OCR per OD, two haems in ΔD, absorbance and % oxidised, their levels
    in the two regions, and delta psi, each with the numbers it was worked out with.

    ---- Inputs ----
    None.

    ---- Globals read ----
    ABSORBANCE_MOD, TIMES_MIN (module constants).

    ---- Outputs ----
    dict
        Experiment dictionary (DATA_FORMAT.md) called run1.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    ΔD = absorbance - its start (bH 12, bL 6 mOD); % oxidised = (absorbance - reduced
    level) / (oxidised level - reduced level) x 100 (bH: 12 and 4 mOD; bL: 6 and 2).

    ---- Helpers ----
    _haem_table_maker
    _imported_experiment_maker
    """

    experiment = _imported_experiment_maker()
    experiment['metadata'].update({'OD': 0.5,
                                   'volume': 1.0,
                                   'dilution_factor': 2.0,
                                   'fit_file': 'made-up fit',
                                   'haem_background': 'Rowan scatter',
                                   },
                                  )
    experiment['VoO2_OD'] = experiment['VoO2'].copy()
    experiment['haem_abs'] = _haem_table_maker(ABSORBANCE_MOD)
    delta = _haem_table_maker({'bH': ABSORBANCE_MOD['bH'] - 12.0,
                               'bL': ABSORBANCE_MOD['bL'] - 6.0,
                               },
                              )
    delta.attrs['delta_abs_baseline'] = {'level_by_haem': {'bH': 12.0, 'bL': 6.0},
                                         'window_by_haem': {'bH': (0.0, 1.0),
                                                            'bL': (0.0, 1.0),
                                                            },
                                         'window_points': 2,
                                         'window_seconds': 60.0,
                                         }
    experiment['haem_delta_abs'] = delta
    experiment['haem_percent'] = _haem_table_maker(
        {'bH': (ABSORBANCE_MOD['bH'] - 4.0) / 8.0 * 100.0,
         'bL': (ABSORBANCE_MOD['bL'] - 2.0) / 4.0 * 100.0,
         },
        )
    experiment['haem_levels'] = {'oxidised': {'bH': 12.0, 'bL': 6.0},
                                 'reduced': {'bH': 4.0, 'bL': 2.0},
                                 'oxidised_region': (0.0, 1.0),
                                 'reduced_region': (2.0, 3.0),
                                 }
    psi = _haem_table_maker({'Δψ (mV)': np.array([np.nan, 100.0, 110.0, 120.0])})
    psi.attrs['delta_psi'] = {'midpoints_mV': {'bH_first': 40.0, 'bL_first': -20.0},
                              'share': 0.5,
                              'temperature_c': 37.0,
                              'limits_percent': (10.0, 90.0),
                              'bH': 'bH',
                              'bL': 'bL',
                              'spectra_with_value': 3,
                              }
    experiment['delta_psi'] = psi
    return experiment


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_imported_file_has_only_its_own_sheets --------------------------------------
def test_imported_file_has_only_its_own_sheets(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a file with nothing worked out gets the oxygen, the
    OCR, the events and the metadata, and no sheet for what it does not have.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes a workbook in tmp_path (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _imported_experiment_maker
    """

    path = experiment_workbook_exporter(_imported_experiment_maker(), tmp_path)[0]
    assert path == tmp_path / 'run1' / 'run1.xlsx'
    assert pd.ExcelFile(path).sheet_names == ['Measured O2',
                                              'Set O2',
                                              'OCR',
                                              'Events',
                                              'Metadata',
                                              ]
    assert list(pd.read_excel(path, sheet_name='OCR').columns) == [TIME_COLUMN,
                                                                   'OCR (µM min⁻¹)',
                                                                   ]
    assert list(pd.read_excel(path, sheet_name='Events').columns) == [
        'Event',
        'Data point',
        TIME_COLUMN,
        'Text in the file',
        'Label',
        'Stock (mM)',
        'Added (µL)',
        'This addition (µM)',
        'In the chamber (µM)',
        'Ignored',
        ]


# ---- test_processed_file_has_every_table ---------------------------------------------
def test_processed_file_has_every_table(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a processed file always gets every table it has, each
    under its plain name with the unit in the headings and its values unchanged, and
    the plain names of the metadata.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.

    ---- Globals read ----
    ABSORBANCE_MOD (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes a workbook in tmp_path (side effect).

    ---- Equations ----
    bH ΔD = 12 - 12 = 0 then 4 - 12 = -8 mOD; bL % oxidised = (6 - 2) / 4 x 100 = 100
    then 0.

    ---- Helpers ----
    _processed_experiment_maker
    """

    # ---- 1 The sheets, in order ------------------------------------------------------
    path = experiment_workbook_exporter(_processed_experiment_maker(), tmp_path)[0]
    assert pd.ExcelFile(path).sheet_names == ['Measured O2',
                                              'Set O2',
                                              'OCR',
                                              'OCR per OD',
                                              'Haems ΔD',
                                              'Haems absorbance',
                                              'Haems % oxidised',
                                              'Δψ',
                                              'Events',
                                              'How it was worked out',
                                              'Metadata',
                                              ]

    # ---- 2 The headings and the values -----------------------------------------------
    delta = pd.read_excel(path, sheet_name='Haems ΔD')
    assert list(delta.columns) == [TIME_COLUMN,
                                   'Spectrum number',
                                   'bH ΔD (mOD)',
                                   'bL ΔD (mOD)',
                                   ]
    assert list(delta['bH ΔD (mOD)']) == [0.0, 0.0, -8.0, -8.0]
    absorbance = pd.read_excel(path, sheet_name='Haems absorbance')
    assert list(absorbance['bL absorbance (mOD)']) == list(ABSORBANCE_MOD['bL'])
    percent = pd.read_excel(path, sheet_name='Haems % oxidised')
    assert list(percent['bL (% oxidised)']) == [100.0, 100.0, 0.0, 0.0]
    scaled = pd.read_excel(path, sheet_name='OCR per OD')
    assert list(scaled.columns) == [TIME_COLUMN, 'OCR per OD (µM min⁻¹ OD⁻¹)']
    psi = pd.read_excel(path, sheet_name='Δψ')
    assert list(psi.columns) == [TIME_COLUMN, 'Spectrum number', 'Δψ (mV)']

    # ---- 3 The metadata in plain words -----------------------------------------------
    sheet = pd.read_excel(path, sheet_name='Metadata')
    metadata = dict(zip(sheet['Field'], sheet['Value']))
    assert metadata['Fit'] == 'made-up fit'
    assert metadata['Background fitted'] == 'Rowan scatter'
    assert float(metadata['Volume (mL)']) == 1.0
    assert float(metadata['Dilution factor']) == 2.0
    assert 'dilution_factor' not in metadata


# ---- test_how_it_was_worked_out ------------------------------------------------------
def test_how_it_was_worked_out() -> None:
    """
    ---- Summary ----
    Main function to check every line of the sheet that says how the numbers were
    worked out against the made-up experiment, and that a file only imported has no
    lines.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _imported_experiment_maker
    _processed_experiment_maker
    """

    table = _processing_table_builder(_processed_experiment_maker())
    assert list(table.columns) == ['What', 'For', 'Value', 'Unit']
    assert [tuple(row) for row in table.itertuples(index=False)] == [
        ('Fit', '', 'made-up fit', ''),
        ('Background fitted', '', 'Rowan scatter', ''),
        ('Background formula (w in nm)', '', 'B = b₀ + b₁·w + b₂·(w − w_mid)²', 'OD'),
        ('Start of ΔD (what was taken off)', 'bH', 12.0, 'mOD'),
        ('Start of ΔD (what was taken off)', 'bL', 6.0, 'mOD'),
        ('Start of ΔD, taken from', 'bH', '0.00 to 1.00', 'min'),
        ('Start of ΔD, taken from', 'bL', '0.00 to 1.00', 'min'),
        ('Oxidised region', '', '0.00 to 1.00', 'min'),
        ('Reduced region', '', '2.00 to 3.00', 'min'),
        ('Oxidised level', 'bH', 12.0, 'mOD'),
        ('Oxidised level', 'bL', 6.0, 'mOD'),
        ('Reduced level', 'bH', 4.0, 'mOD'),
        ('Reduced level', 'bL', 2.0, 'mOD'),
        ('Δψ: haem used', 'bH', 'bH', ''),
        ('Δψ: haem used', 'bL', 'bL', ''),
        ('Δψ: midpoint potential', 'bH, first', 40.0, 'mV'),
        ('Δψ: midpoint potential', 'bL, first', -20.0, 'mV'),
        ('Δψ: share', '', 0.5, ''),
        ('Δψ: temperature', '', 37.0, '°C'),
        ('Δψ: lowest limit', '', 10.0, '% reduced'),
        ('Δψ: highest limit', '', 90.0, '% reduced'),
        ('Δψ: spectra with a value', '', '3 of 4', ''),
        ('OD scaling: OD', '', 0.5, ''),
        ('OD scaling: volume', '', 1.0, 'mL'),
        ('OD scaling: dilution factor', '', 2.0, ''),
        ('OD scaling: how', '', 'OCR ÷ (OD × volume × dilution factor)', ''),
        ]
    assert _processing_table_builder(_imported_experiment_maker()).empty


# ---- test_ocr_percent_of_baseline_has_its_sheet --------------------------------------
def test_ocr_percent_of_baseline_has_its_sheet(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check that a file with the OCR as % of baseline gets its sheet
    after the other OCR sheets, with the unit in its heading, and the lines saying
    which baseline it was worked out from.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.

    ---- Globals read ----
    TIMES_MIN (module constant); TIME_COLUMN.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes a workbook in tmp_path (side effect).

    ---- Equations ----
    The OCR is twice the time: 0, 2, 4 and 6. With a baseline of 0 to 1 min its
    average there is (0 + 2) / 2 = 1, so the % of baseline is 0, 200, 400 and 600.

    ---- Helpers ----
    _imported_experiment_maker
    """

    experiment = _imported_experiment_maker()
    table = experiment['VoO2'].copy()
    table['VoO2'] = table['VoO2'] / 1.0 * 100.0
    table.attrs['baseline_percent'] = {'start_time': 0.0,
                                       'end_time': 1.0,
                                       'baseline_mean': {'VoO2': 1.0},
                                       }
    experiment['VoO2_baseline'] = table
    path = experiment_workbook_exporter(experiment, tmp_path)[0]
    assert pd.ExcelFile(path).sheet_names == ['Measured O2',
                                              'Set O2',
                                              'OCR',
                                              'OCR % of baseline',
                                              'Events',
                                              'How it was worked out',
                                              'Metadata',
                                              ]
    sheet = pd.read_excel(path, sheet_name='OCR % of baseline')
    assert list(sheet.columns) == [TIME_COLUMN, 'OCR (% of baseline)']
    assert list(sheet['OCR (% of baseline)']) == [0.0, 200.0, 400.0, 600.0]
    lines = _processing_table_builder(experiment)
    assert [tuple(row) for row in lines.itertuples(index=False)] == [
        ('OCR % of baseline: baseline window', '', '0.00 to 1.00', 'min'),
        ('OCR % of baseline: average OCR in the baseline (100 %)',
         '',
         1.0,
         'µM min⁻¹',
         ),
        ('OCR % of baseline: how', '', 'OCR ÷ its average in the baseline × 100', ''),
        ]


# ---- test_workbook_keeps_its_list_of_spectra -----------------------------------------
def test_workbook_keeps_its_list_of_spectra(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check a workbook written again after its spectra were written as
    csv files: asked to keep its list, it lists the files still beside it without
    writing them again; not asked, or with the files gone, it has no list.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.

    ---- Globals read ----
    TIMES_MIN (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes workbooks and a csv file in tmp_path (side effect).

    ---- Equations ----
    Four spectra of three wavelengths: one csv file, Cyt_transmiss.csv.

    ---- Helpers ----
    _imported_experiment_maker
    """

    # ---- 1 Write the workbook with its spectra ---------------------------------------
    experiment = _imported_experiment_maker()
    experiment['raw_spectra'] = {'Cyt': {'wavelengths': np.array([500.0, 510.0, 520.0]),
                                         'time': TIMES_MIN,
                                         'spectrum_indices': np.arange(4),
                                         'transmission': np.ones((4, 3)),
                                         },
                                 }
    written = experiment_workbook_exporter(experiment, tmp_path, spectra=True)
    path, csv_path = written
    assert csv_path == tmp_path / 'run1' / 'Cyt_transmiss.csv'
    first = pd.read_excel(path, sheet_name='Spectral data')
    assert list(first['CSV file']) == ['Cyt_transmiss.csv']
    assert list(first['Timepoints']) == [4]

    # ---- 2 Written again keeping the list: the same list, the csv file untouched -----
    csv_path.write_bytes(b'not written again')
    experiment['raw_spectra'] = {}  # as in a run that does not read the spectra
    again = experiment_workbook_exporter(experiment, tmp_path, keeps_spectra_list=True)
    assert again == [path, csv_path]
    assert csv_path.read_bytes() == b'not written again'
    kept = pd.read_excel(path, sheet_name='Spectral data')
    assert kept.to_dict('records') == first.to_dict('records')

    # ---- 3 A csv file that is gone is not listed -------------------------------------
    csv_path.unlink()
    assert experiment_workbook_exporter(experiment,
                                        tmp_path,
                                        keeps_spectra_list=True,
                                        ) == [path]
    assert 'Spectral data' not in pd.ExcelFile(path).sheet_names

    # ---- 4 Not asked to keep the list: none, even with the file there ----------------
    experiment_workbook_exporter(experiment, tmp_path, spectra=False)
    assert 'Spectral data' not in pd.ExcelFile(path).sheet_names


# ---- test_every_spectrum_has_its_own_time_heading ------------------------------------
def test_every_spectrum_has_its_own_time_heading(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the headings of a spectra csv file: each spectrum's time in
    minutes to 6 decimals with the trailing zeros dropped, so two spectra late in a
    very long run keep their own heading (to 6 figures both would read 1000.01 min),
    and a spectrum without a time is headed by its number.

    ---- Inputs ----
    tmp_path : Path
        Results folder for the test.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes a workbook and a csv file in tmp_path (side effect).

    ---- Equations ----
    Five spectra at 0, 0.5 s (0.008333... min, so 0.008333), 1000.008 and 1000.012
    min, and one with no time, numbered 7.

    ---- Helpers ----
    _imported_experiment_maker
    """

    experiment = _imported_experiment_maker()
    times_min = np.array([0.0, 0.5 / 60.0, 1000.008, 1000.012, np.nan])
    experiment['raw_spectra'] = {'Cyt': {'wavelengths': np.array([500.0, 510.0]),
                                         'time': times_min,
                                         'spectrum_indices': np.array([3, 4, 5, 6, 7]),
                                         'transmission': np.ones((5, 2)),
                                         },
                                 }
    csv_path = experiment_workbook_exporter(experiment, tmp_path, spectra=True)[1]
    headings = csv_path.read_text(encoding='utf-8').splitlines()[0].split(',')
    assert headings == ['Wavelength (nm)',
                        '0 min',
                        '0.008333 min',
                        '1000.008 min',
                        '1000.012 min',
                        'Spectrum 7',
                        ]
