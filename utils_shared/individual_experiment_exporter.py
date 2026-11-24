"""
Export of one processed experiment to an Excel workbook.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.averaging import WINDOW_KINDS
from utils_shared.helpers import excel_sheet_namer, file_name_sanitiser
from utils_shared.schema import SPECTRUM_INDEX_COLUMN, TIME_COLUMN
from utils_shared.spectral_decomposer import (BACKGROUND_PLAIN_FORMULAS,
                                              BACKGROUND_SHORT_NAMES,
                                              )


# ---- CONSTANTS -----------------------------------------------------------------------
# Sheets are written in this order; any that are absent from the experiment are skipped.
# (experiment dictionary key, worksheet name, heading of each measurement column, with
# {name} for the column's own name; None keeps the headings of the table, which carry
# their unit already). The haem amounts (haem_conc, haem_OD) are left out: only cells
# are measured, and an amount depends on the size of its shape.
DATA_SHEETS = (('CcO2', 'Measured O2', None),
               ('CsO2', 'Set O2', None),
               ('VoO2', 'OCR', 'OCR (µM min⁻¹)'),
               ('VoO2_OD', 'OCR per OD', 'OCR per OD (µM min⁻¹ OD⁻¹)'),
               ('VoO2_percent', 'OCR % of range', 'OCR (% of range)'),
               ('VoO2_baseline', 'OCR % of baseline', 'OCR (% of baseline)'),
               ('haem_delta_abs', 'Haems ΔD', '{name} ΔD (mOD)'),
               ('haem_abs', 'Haems absorbance', '{name} absorbance (mOD)'),
               ('haem_percent', 'Haems % oxidised', '{name} (% oxidised)'),
               ('haem_delta_abs_OD', 'Haems ΔD per OD', '{name} ΔD (mOD OD⁻¹)'),
               ('haem_abs_OD',
                'Haems absorbance per OD',
                '{name} absorbance (mOD OD⁻¹)',
                ),
               ('delta_psi', 'Δψ', None),
               )
# the heading of the spectrum numbers in the sheets
SPECTRUM_NUMBER_TEXT = 'Spectrum number'
# The units in the headings of the Averages sheet: of the OCR that was averaged
# (averages['settings']['vo2_key']) and of the table each haem view was averaged from
# (averages['settings']['haem_view_keys']). A per is written as a power of -1, never
# with a slash.
OCR_UNITS = {'VoO2': 'µM min⁻¹',
             'VoO2_OD': 'µM min⁻¹ OD⁻¹',
             'VoO2_percent': '% of range',
             }
HAEM_UNITS = {'haem_delta_abs': 'mOD',
              'haem_abs': 'mOD',
              'haem_percent': '% oxidised',
              'haem_delta_abs_OD': 'mOD OD⁻¹',
              'haem_abs_OD': 'mOD OD⁻¹',
              }
# The lines of the Metadata sheet the program adds itself, in plain words; what comes
# from the .paf file keeps its own name.
METADATA_TEXTS = {'OD': 'OD',
                  'volume': 'Volume (mL)',
                  'dilution_factor': 'Dilution factor',
                  'trimmed_before_minutes': 'Trimmed before (min)',
                  'trimmed_after_minutes': 'Trimmed after (min)',
                  'ignore_first_minutes': 'Ignored at the start (min)',
                  'ignore_last_minutes': 'Ignored at the end (min)',
                  'fit_file': 'Fit',
                  'haem_background': 'Background fitted',
                  'processed': 'Processed on',
                  }
# the sheet that says how the haems, % oxidised and delta psi were worked out
PROCESSING_SHEET = 'How it was worked out'
PROCESSING_COLUMNS = ('What', 'For', 'Value', 'Unit')
# Spectral arrays exported to CSV (they are far too large for worksheets).
SPECTRAL_CSV_TYPES = (('transmission', 'transmiss'),
                      ('intensity', 'intensity'),
                      ('attenuation', 'attenuation'),
                      )
# the sheet that lists the spectral CSV files beside the workbook, and its column of
# file names
# decimals of the time (min) heading each spectrum's column in a spectral CSV file:
# 0.000001 min is 0.06 ms, far below the time between two spectra, however long the run
SPECTRUM_TIME_DECIMALS = 6
SPECTRAL_SHEET = 'Spectral data'
SPECTRAL_FILE_COLUMN = 'CSV file'
# folder, inside the folder of a trimmed experiment, that holds its whole recording
FULL_FOLDER = 'full'
# The ways the haems are shown (the keys of config.HAEM_SOURCE_BY_MODE) and delta psi,
# as the columns of the Averages sheet call them.
HAEM_VIEW_TEXTS = {'delta': 'ΔD', 'abs': 'absorbance', 'percent': '% oxidised'}
DELTA_PSI_TEXT, DELTA_PSI_UNIT = 'Δψ', 'mV'
# the statistics of a measurement in the Averages sheet: (key in the window record,
# what the heading calls it)
AVERAGE_STATISTICS = (('mean', 'mean'),
                      ('sd', 'SD'),
                      ('delta', 'difference from baseline'),
                      )


# ---- INDIVIDUAL EXPERIMENT EXPORTER HELPERS ------------------------------------------


# ---- _frame_writer -------------------------------------------------------------------
def _frame_writer(sheets: tuple,
                  frame: pd.DataFrame,
                  sheet_title: str,
                  first_col_width: float = 18,
                  ) -> Any:
    """
    ---- Summary ----
    Helper function to write a DataFrame as a formatted worksheet.

    ---- Inputs ----
    sheets : tuple
        (open ExcelWriter, header format, set of sheet names already used).
    frame : pd.DataFrame
        Data to write.
    sheet_title : str
        Wanted sheet name; made unique and valid for Excel.
    first_col_width : float
        Width of the first column.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Any
        The xlsxwriter worksheet.

    ---- Globals mutated ----
    None. Adds a sheet to the open workbook and records its name (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    excel_sheet_namer
    """

    writer, header_format, used_sheets = sheets
    sheet = excel_sheet_namer(sheet_title, used_sheets)
    frame.to_excel(writer, sheet_name=sheet, index=False)
    worksheet = writer.sheets[sheet]
    for col, column_name in enumerate(frame.columns):
        worksheet.write(0, col, str(column_name), header_format)
    worksheet.set_row(0, 32)
    worksheet.set_column(0, 0, first_col_width)
    worksheet.set_column(1, max(len(frame.columns), 2), 16)
    worksheet.freeze_panes(1, 0)
    return worksheet


# ---- _kept_fraction_finder -----------------------------------------------------------
def _kept_fraction_finder(summary: dict, limits: Dict[str, dict]) -> Tuple[float, bool]:
    """
    ---- Summary ----
    Helper function to find the share of a recording its trimming keeps, and whether
    the file is trimmed at all.

    ---- Inputs ----
    summary : dict
        File summary (DATA_FORMAT.md), with 'name' and 'duration_min'.
    limits : Dict[str, dict]
        {file name: {'trim_start', 'trim_end' (min on the recording, None for no trim),
        ...}}; a file missing is not trimmed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, bool]
        (share kept, 0 to 1; True when the file is trimmed at either end).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    share kept = (trim end - trim start) / duration, the trim end being the duration
    and the trim start 0 when not trimmed, kept within 0 to 1.

    ---- Helpers ----
    None.
    """

    duration = float(summary['duration_min'])
    own = limits.get(summary['name']) or {}
    start, end = own.get('trim_start'), own.get('trim_end')
    kept = ((duration if end is None else float(end)) -
            (0.0 if start is None else float(start))
            )
    fraction = min(max(kept / duration, 0.0), 1.0) if duration > 0 else 1.0
    return fraction, start is not None or end is not None


# ---- _name_lister --------------------------------------------------------------------
def _name_lister(windows: dict, kind: str) -> List[str]:
    """
    ---- Summary ----
    Helper function to list the measurement names of one kind (vo2 or haem) over all
    windows, in first-seen order.

    ---- Inputs ----
    windows : dict
        Window name -> window record, each holding 'vo2' and 'haem' dicts.
    kind : str
        'vo2' or 'haem'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        Unique measurement names.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return list(dict.fromkeys(m for w in windows.values() for m in w[kind]))


# ---- _processing_table_builder -------------------------------------------------------
def _processing_table_builder(experiment: dict) -> pd.DataFrame:
    """
    ---- Summary ----
    Helper function to build the table of the sheet that says how the numbers of one
    experiment were worked out: the fit and the background, where ΔD starts, the two
    regions and each haem's level in them, the numbers of delta psi, the OD scaling
    and the baseline of the OCR's % of baseline. Only the lines the experiment has are
    written.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md. Read: metadata (fit_file,
        haem_background, OD, volume, dilution_factor), haem_delta_abs
        (attrs['delta_abs_baseline']), haem_levels, delta_psi (attrs['delta_psi']),
        whether VoO2_OD is there and VoO2_baseline (attrs['baseline_percent']).

    ---- Globals read ----
    PROCESSING_COLUMNS (module constant); BACKGROUND_PLAIN_FORMULAS,
    BACKGROUND_SHORT_NAMES.

    ---- Outputs ----
    pd.DataFrame
        Columns What, For (a haem, or empty), Value (a number or text) and Unit; no
        rows for an experiment that was only imported.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Set up --------------------------------------------------------------------
    metadata = experiment.get('metadata')
    if not isinstance(metadata, dict):
        metadata = {}
    rows: List[tuple] = []

    # ---- 2 The fit and the start of ΔD -----------------------------------------------
    if metadata.get('fit_file'):
        rows.append(('Fit', '', metadata['fit_file'], ''))
    if metadata.get('haem_background'):
        rows.append(('Background fitted', '', metadata['haem_background'], ''))
        names = {short: name for name, short in BACKGROUND_SHORT_NAMES.items()}
        name = names.get(metadata['haem_background'], metadata['haem_background'])
        if name in BACKGROUND_PLAIN_FORMULAS:
            rows.append(('Background formula (w in nm)',
                         '',
                         BACKGROUND_PLAIN_FORMULAS[name],
                         'OD',
                         ),
                        )
    delta = experiment.get('haem_delta_abs')
    start = (delta.attrs.get('delta_abs_baseline')
             if isinstance(delta, pd.DataFrame)
             else None
             )
    if start:
        for haem, level in start['level_by_haem'].items():
            rows.append(('Start of ΔD (what was taken off)', haem, float(level), 'mOD'))
        for haem, (first, last) in start['window_by_haem'].items():
            rows.append(('Start of ΔD, taken from',
                         haem,
                         f'{first:.2f} to {last:.2f}',
                         'min',
                         ),
                        )

    # ---- 3 The regions and the levels ------------------------------------------------
    levels = experiment.get('haem_levels')
    if levels:
        for region in ('oxidised', 'reduced'):
            first, last = levels[f'{region}_region']
            rows.append((f'{region.capitalize()} region',
                         '',
                         f'{first:.2f} to {last:.2f}',
                         'min',
                         ),
                        )
        for region in ('oxidised', 'reduced'):
            for haem, level in levels[region].items():
                rows.append((f'{region.capitalize()} level', haem, float(level), 'mOD'))

    # ---- 4 Delta psi -----------------------------------------------------------------
    table = experiment.get('delta_psi')
    used = table.attrs.get('delta_psi') if isinstance(table, pd.DataFrame) else None
    if used:
        for haem in ('bH', 'bL'):
            rows.append(('Δψ: haem used', haem, used[haem], ''))
        for key, value in used['midpoints_mV'].items():
            rows.append(('Δψ: midpoint potential',
                         str(key).replace('_', ', '),
                         float(value),
                         'mV',
                         ),
                        )
        lowest, highest = used['limits_percent']
        rows += [('Δψ: share', '', float(used['share']), ''),
                 ('Δψ: temperature', '', float(used['temperature_c']), '°C'),
                 ('Δψ: lowest limit', '', float(lowest), '% reduced'),
                 ('Δψ: highest limit', '', float(highest), '% reduced'),
                 ('Δψ: spectra with a value',
                  '',
                  f"{used['spectra_with_value']} of {len(table)}",
                  '',
                  ),
                 ]

    # ---- 5 The OD scaling ------------------------------------------------------------
    if isinstance(experiment.get('VoO2_OD'), pd.DataFrame):
        rows += [('OD scaling: OD', '', metadata.get('OD'), ''),
                 ('OD scaling: volume', '', metadata.get('volume'), 'mL'),
                 ('OD scaling: dilution factor',
                  '',
                  metadata.get('dilution_factor'),
                  '',
                  ),
                 ('OD scaling: how',
                  '',
                  'OCR ÷ (OD × volume × dilution factor)',
                  '',
                  ),
                 ]

    # ---- 6 The OCR as % of baseline --------------------------------------------------
    table = experiment.get('VoO2_baseline')
    used = (table.attrs.get('baseline_percent')
            if isinstance(table, pd.DataFrame)
            else None
            )
    if used:
        rows.append(('OCR % of baseline: baseline window',
                     '',
                     f"{used['start_time']:.2f} to {used['end_time']:.2f}",
                     'min',
                     ),
                    )
        for mean in used['baseline_mean'].values():
            rows.append(('OCR % of baseline: average OCR in the baseline (100 %)',
                         '',
                         float(mean),
                         'µM min⁻¹',
                         ),
                        )
        rows.append(('OCR % of baseline: how',
                     '',
                     'OCR ÷ its average in the baseline × 100',
                     '',
                     ),
                    )
    return pd.DataFrame(rows, columns=list(PROCESSING_COLUMNS))


# ---- _sheet_table_builder ------------------------------------------------------------
def _sheet_table_builder(frame: pd.DataFrame, heading: Optional[str]) -> pd.DataFrame:
    """
    ---- Summary ----
    Helper function to give a table of the experiment the headings of its sheet: the
    spectrum numbers in plain words and each measurement with its unit.

    ---- Inputs ----
    frame : pd.DataFrame
        A table of the experiment: the time, for the haems the spectrum index, then
        one column per measurement.
    heading : Optional[str]
        Heading of each measurement column, with {name} for the column's own name
        ('{name} ΔD (mOD)'); None keeps the headings of the table.

    ---- Globals read ----
    SPECTRUM_NUMBER_TEXT (module constant); TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

    ---- Outputs ----
    pd.DataFrame
        A copy with the new headings; the values are unchanged.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    names = {}
    for column in frame.columns:
        if column == SPECTRUM_INDEX_COLUMN:
            names[column] = SPECTRUM_NUMBER_TEXT
        elif column != TIME_COLUMN and heading is not None:
            names[column] = heading.format(name=column)
    return frame.rename(columns=names)


# ---- _spectral_csv_exporter ----------------------------------------------------------
def _spectral_csv_exporter(experiment: dict, folder: Path) -> List[dict]:
    """
    ---- Summary ----
    Helper function to write one CSV per spectral dataset and data type, with
    wavelengths down and one column per spectrum, headed by its time to
    SPECTRUM_TIME_DECIMALS decimals (trailing zeros dropped) so that no two spectra
    share a heading.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    folder : Path
        Existing folder the CSV files are written to.

    ---- Globals read ----
    SPECTRAL_CSV_TYPES, SPECTRUM_TIME_DECIMALS (module constants).

    ---- Outputs ----
    List[dict]
        One record per CSV file: Dataset, Data type, CSV file, Wavelengths, Timepoints.
        Raises ValueError when a spectrum length does not match the wavelengths.

    ---- Globals mutated ----
    None. Writes CSV files into ``folder`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Set up --------------------------------------------------------------------
    name = experiment.get('experiment_name', 'experiment')
    records = []

    # ---- 2 Write every dataset -------------------------------------------------------
    for dataset_name, dataset in experiment.get('raw_spectra', {}).items():
        wavelengths = np.asarray(dataset['wavelengths'])
        times = np.asarray(dataset['time'], dtype=float)
        indices = np.asarray(dataset['spectrum_indices'])
        for data_key, file_suffix in SPECTRAL_CSV_TYPES:
            if dataset.get(data_key) is None:
                continue
            spectra = np.asarray(dataset[data_key], dtype=float)
            if spectra.ndim != 2:
                continue
            if spectra.shape[1] != len(wavelengths):
                raise ValueError(f'{name}/{dataset_name}: {data_key} does not match '
                                 f'the number of wavelengths.',
                                 )
            # Label each spectrum by its time; fall back to its index if times are
            # unavailable. A fixed number of decimals keeps two spectra of a very long
            # run apart, which a fixed number of figures does not.
            labels = [f"{f'{t:.{SPECTRUM_TIME_DECIMALS}f}'.rstrip('0').rstrip('.')} min"
                      if np.isfinite(t)
                      else f'Spectrum {i}'
                      for t, i in zip(times, indices)
                      ]
            frame = pd.DataFrame(spectra.T, columns=labels)
            frame.insert(0, 'Wavelength (nm)', wavelengths)
            csv_name = f'{dataset_name}_{file_suffix}.csv'
            frame.to_csv(folder / csv_name, index=False)
            records.append({'Dataset': dataset_name,
                            'Data type': data_key,
                            SPECTRAL_FILE_COLUMN: csv_name,
                            'Wavelengths': len(wavelengths),
                            'Timepoints': spectra.shape[0],
                            },
                           )
    return records


# ---- _spectral_list_reader -----------------------------------------------------------
def _spectral_list_reader(workbook_path: Path) -> List[dict]:
    """
    ---- Summary ----
    Helper function to read the list of spectral CSV files a workbook already holds, so
    a workbook written again without writing the spectra again still lists them. Only
    the files still beside the workbook are kept.

    ---- Inputs ----
    workbook_path : Path
        The workbook about to be written again; it may not exist.

    ---- Globals read ----
    SPECTRAL_SHEET, SPECTRAL_FILE_COLUMN (module constants).

    ---- Outputs ----
    List[dict]
        The records of _spectral_csv_exporter, one per CSV file listed and still
        there; empty when there is no workbook, it cannot be read or it lists none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        listed = pd.read_excel(workbook_path, sheet_name=SPECTRAL_SHEET)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        return []  # no workbook, no such sheet, or not a workbook: nothing to list
    if SPECTRAL_FILE_COLUMN not in listed.columns:
        return []
    return [record
            for record in listed.to_dict('records')
            if (workbook_path.parent / str(record[SPECTRAL_FILE_COLUMN])).is_file()
            ]


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- averages_table_builder ----------------------------------------------------------
def averages_table_builder(averages: dict) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to build the Averages worksheet table: one row per window with the
    mean, SD and difference from baseline of the OCR, of each haem in every view and
    of delta psi.

    ---- Inputs ----
    averages : dict
        Event-window averages, as added to the experiment by
        experiment_averages_calculator (DATA_FORMAT.md); uses averages['windows'] and
        the windows of averages['skipped'] the user left out.

    ---- Globals read ----
    HAEM_VIEW_TEXTS, HAEM_UNITS, OCR_UNITS, AVERAGE_STATISTICS, DELTA_PSI_TEXT and
    DELTA_PSI_UNIT (module constants); WINDOW_KINDS (imported).

    ---- Outputs ----
    pd.DataFrame
        One row per window, the baseline first, then the settled and the quick windows
        in time; a window left out has the Kind 'settled (left out)' or 'quick (left
        out)' and its numbers empty.
        Columns Average, Kind (baseline, settled or quick), Start time (min), End time
        (min); then for the OCR its mean, SD, difference from baseline and '(% of
        baseline)'; for each haem in each view (the one averaged view, without a view
        name, when the windows hold no views) its mean, SD and difference from
        baseline; and, for an experiment with delta psi, its mean, SD, difference from
        baseline and 'spectra used' ('180 of 240'). Each heading ends in its unit in
        brackets ('OCR mean (µM min⁻¹)', 'bH ΔD SD (mOD)', 'bH mean (% oxidised)'),
        from averages['settings']; a measurement whose source the settings do not
        name gets no unit.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Difference from baseline = window mean - average0 mean; % of baseline = window
    mean / average0 mean x 100 (both calculated in the averaging step).

    ---- Helpers ----
    _name_lister
    """

    # ---- 1 Get the measurement names -------------------------------------------------
    windows = averages['windows']
    vo2_names = _name_lister(windows, 'vo2')
    found = list(dict.fromkeys(view
                               for window in windows.values()
                               for view in window.get('haem_views', {})
                               ),
                 )
    # in the order of HAEM_VIEW_TEXTS, the standard view first
    views = ([view for view in HAEM_VIEW_TEXTS if view in found]
             + [view for view in found if view not in HAEM_VIEW_TEXTS]
             )

    # ---- 2 Define the column groups --------------------------------------------------
    # (where the statistics are in a window record, the measurement, the column label,
    # the unit); a view whose unit says what it is (% oxidised) is not named twice
    settings = averages.get('settings', {})
    view_keys = settings.get('haem_view_keys') or {}
    groups = []
    for view in views:
        text = HAEM_VIEW_TEXTS.get(view, view)
        unit = HAEM_UNITS.get(view_keys.get(view), '')
        for haem in dict.fromkeys(haem
                                  for window in windows.values()
                                  for haem in window.get('haem_views', {}).get(view, {})
                                  ):
            groups.append((('haem_views', view),
                           haem,
                           str(haem) if text == unit else f'{haem} {text}',
                           unit,
                           ),
                          )
    if not views:
        unit = HAEM_UNITS.get(settings.get('haem_key'), '')
        groups = [(('haem',), haem, str(haem), unit)
                  for haem in _name_lister(windows, 'haem')
                  ]
    vo2_unit = OCR_UNITS.get(settings.get('vo2_key'), '')
    has_delta_psi = any('delta_psi' in window for window in windows.values())

    def heading(label: str, statistic: str, unit: str) -> str:
        return f'{label} {statistic} ({unit})' if unit else f'{label} {statistic}'

    # ---- 3 Build the rows ------------------------------------------------------------
    # A window the user left out keeps its row, with its numbers empty, at its place
    # among the others: the baseline, then the settled, then the quick windows in time.
    records = list(windows.items()) + [(window_name, window)
                                       for window_name, window
                                       in averages.get('skipped', {}).items()
                                       if window.get('left_out')
                                       ]

    def kind_finder(window_name: str, window: dict) -> str:
        # a record without a kind is the baseline or a settled window
        return window.get('kind',
                          'baseline' if window_name == 'average0' else 'settled',
                          )

    records.sort(key=lambda record: (WINDOW_KINDS.index(kind_finder(*record)),
                                     record[1]['start_time'],
                                     ))
    rows = []
    for window_name, window in records:
        kind = kind_finder(window_name, window)
        row = {'Average': window_name,
               'Kind': f'{kind} (left out)' if window.get('left_out') else kind,
               'Start time (min)': window['start_time'],
               'End time (min)': window['end_time'],
               }
        for measurement in vo2_names:
            label = 'OCR' if len(vo2_names) == 1 else f'OCR ({measurement})'
            stats = window.get('vo2', {}).get(measurement, {})
            for key, statistic in AVERAGE_STATISTICS:
                row[heading(label, statistic, vo2_unit)] = stats.get(key, np.nan)
            row[f'{label} (% of baseline)'] = stats.get('change', np.nan)
        for path, measurement, label, unit in groups:
            stats = window
            for key in path:
                stats = stats.get(key, {})
            stats = stats.get(measurement, {})
            for key, statistic in AVERAGE_STATISTICS:
                row[heading(label, statistic, unit)] = stats.get(key, np.nan)
        if has_delta_psi:
            stats = window.get('delta_psi', {})
            for key, statistic in AVERAGE_STATISTICS:
                row[heading(DELTA_PSI_TEXT, statistic, DELTA_PSI_UNIT)] = stats.get(
                    key,
                    np.nan,
                    )
            row['Δψ spectra used'] = (f"{stats['spectra_used']} of "
                                      f"{stats['spectra_in_window']}"
                                      if stats
                                      else ''
                                      )
        rows.append(row)
    return pd.DataFrame(rows)


# ---- experiment_workbook_exporter ----------------------------------------------------
def experiment_workbook_exporter(experiment: dict,
                                 output_dir: Path,
                                 spectra: bool = False,
                                 subfolder: str = '',
                                 keeps_spectra_list: bool = False,
                                 ) -> List[Path]:
    """
    ---- Summary ----
    Main function to export one experiment to <output_dir>/<name>/<name>.xlsx (or into
    a folder inside that, such as the full/ of a trimmed experiment's whole recording),
    with a sheet for every table it has (the oxygen, the OCR, the haems in every view,
    delta psi), then Averages, Events, how it was worked out and Metadata, and
    optionally the spectral CSV files.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    output_dir : Path
        Results folder.
    spectra : bool
        True also writes the spectral CSV files next to the workbook (large and slow)
        and an index sheet linking to them.
    subfolder : str
        Folder inside the experiment's folder to write into (FULL_FOLDER); '' for the
        experiment's folder itself.
    keeps_spectra_list : bool
        True, with ``spectra`` False, lists again the spectral CSV files the workbook
        being replaced listed and that are still beside it (those written earlier in
        the same run), without writing them again.

    ---- Globals read ----
    DATA_SHEETS, HAEM_VIEW_TEXTS, METADATA_TEXTS,
    PROCESSING_SHEET, SPECTRAL_SHEET and SPECTRAL_FILE_COLUMN (module constants);
    TIME_COLUMN.

    ---- Outputs ----
    List[Path]
        Paths of the files written: the workbook first, then any CSV files.

    ---- Globals mutated ----
    None. Creates the folder, the workbook and optional CSV files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _frame_writer
    _processing_table_builder
    _sheet_table_builder
    _spectral_csv_exporter
    _spectral_list_reader
    averages_table_builder
    file_name_sanitiser
    """

    # ---- 1 Set up the output paths ---------------------------------------------------
    name = file_name_sanitiser(experiment.get('experiment_name', 'experiment'))
    folder = Path(output_dir) / name / subfolder if subfolder else Path(output_dir,
                                                                        ) / name
    folder.mkdir(parents=True, exist_ok=True)
    output_path = folder / f'{name}.xlsx'
    if spectra:
        spectral_records = _spectral_csv_exporter(experiment, folder)
    elif keeps_spectra_list:
        spectral_records = _spectral_list_reader(output_path)
    else:
        spectral_records = []

    # ---- 2 Write the workbook --------------------------------------------------------
    used_sheets = set()
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({'bold': True,
                                             'bg_color': '#D9EAD3',
                                             'border': 1,
                                             'text_wrap': True,
                                             },
                                            )
        link_format = workbook.add_format({'font_color': 'blue', 'underline': 1})
        sheets = (writer, header_format, used_sheets)
        # 1. Spectral data index (links to the CSVs).
        if spectral_records:
            worksheet = _frame_writer(sheets,
                                      pd.DataFrame(spectral_records),
                                      SPECTRAL_SHEET,
                                      first_col_width=14,
                                      )
            for row, record in enumerate(spectral_records, start=1):
                worksheet.write_url(row,
                                    2,
                                    f'external:{record[SPECTRAL_FILE_COLUMN]}',
                                    link_format,
                                    string=str(record[SPECTRAL_FILE_COLUMN]),
                                    )
            worksheet.set_column(2, 2, 28)
        # 2. Time-resolved datasets.
        for key, sheet_title, heading in DATA_SHEETS:
            frame = experiment.get(key)
            if isinstance(frame, pd.DataFrame) and not frame.empty:
                _frame_writer(sheets, _sheet_table_builder(frame, heading), sheet_title)
        # 3. Event-window averages.
        averages = experiment.get('averages')
        if averages and averages.get('windows'):
            table = averages_table_builder(averages)
            worksheet = _frame_writer(sheets, table, 'Averages', first_col_width=14)
            settings = averages['settings']
            notes = [f"The baseline (average0) is {settings['window_minutes']:g} min "
                     f"long and ends {settings['gap_minutes']:g} min before the first "
                     'addition.',
                     ]
            if settings.get('is_settled', True):
                notes.append(f"Settled windows are {settings['window_minutes']:g} min "
                             f"long, ending {settings['gap_minutes']:g} min before "
                             'the next addition and '
                             f"{settings['final_window_gap_minutes']:g} min before "
                             'the end of the recording.',
                             )
            if settings.get('quick_minutes') is not None:
                notes.append(f"Quick windows are {settings['quick_minutes']:g} min "
                             f"long, starting {settings['delay_minutes']:g} min after "
                             'their addition.',
                             )
            # The windows set on their own say how they differ from the rest; the last
            # settled window always ends its set time before the end of the recording.
            events = (experiment.get('metadata') or {}).get('events') or []
            last_settled = f'average{len(events)}'
            for window_name, own in sorted((settings.get('each_window') or {}).items()):
                parts = []
                if own.get('length_min') is not None:
                    parts.append(f"{own['length_min']:g} min long")
                if own.get('gap_min') is not None and window_name != last_settled:
                    parts.append(f"ending {own['gap_min']:g} min before the next "
                                 'addition',
                                 )
                if own.get('delay_min') is not None:
                    parts.append(f"starting {own['delay_min']:g} min after its "
                                 'addition',
                                 )
                if not own.get('is_used', True) and window_name != 'average0':
                    parts.append('left out of the averages')
                if parts:
                    notes.append(f"{window_name} is set on its own: "
                                 f"{', '.join(parts)}.",
                                 )
            notes += ['Difference from baseline = the average in the window - the '
                      'average in the baseline (average0), in the unit of the '
                      'measurement.',
                      'OCR (% of baseline) = the average in the window / the average '
                      'in the baseline x 100 (100 = no change).',
                      ]
            if any(window.get('haem_views')
                   for window in averages['windows'].values()
                   ):
                notes.append('Each haem is given in every way the program shows it: '
                             + ', '.join(HAEM_VIEW_TEXTS.values())
                             + ' (only for a file with an oxidised and a reduced '
                             'region).',
                             )
            if 'Δψ spectra used' in table.columns:
                notes.append('Δψ is averaged over the spectra of the window that have '
                             'a value (it is empty where bH or bL is outside its '
                             'limits); "spectra used" says how many that was.',
                             )
            for offset, note in enumerate(notes, start=2):
                worksheet.write(len(table) + offset, 0, note)
        metadata = experiment.get('metadata')
        if not isinstance(metadata, dict):
            metadata = {}
        # 4. Events, with the label, the stock and volume added and the concentrations
        # the user entered or the program worked out (the stock in mM, as it is typed).
        all_events = (list(metadata.get('events', [])) +
                      list(metadata.get('ignored_events', []))
                      )
        events = sorted(all_events,
                        key=lambda e: e.get('time') if e.get('time') is not None else 0,
                        )
        # always written, so the sheet exists even for a file with no events
        event_frame = pd.DataFrame({'Event': [f'Event {i}'
                                              for i in range(1, len(events) + 1)
                                              ],
                                    'Data point': [e.get('datapoint') for e in events],
                                    TIME_COLUMN: [e.get('time') for e in events],
                                    'Text in the file': [e.get('text', '')
                                                         for e in events
                                                         ],
                                    'Label': [e.get('label', '') for e in events],
                                    'Stock (mM)': [None
                                                   if e.get('stock_uM') is None
                                                   else e['stock_uM'] / 1000
                                                   for e in events
                                                   ],
                                    'Added (µL)': [e.get('added_uL') for e in events],
                                    'This addition (µM)': [e.get('addition_uM')
                                                           for e in events
                                                           ],
                                    'In the chamber (µM)': [e.get('concentration_uM')
                                                            for e in events
                                                            ],
                                    'Ignored': [bool(e.get('ignored', False))
                                                for e in events
                                                ],
                                    },
                                   )
        _frame_writer(sheets, event_frame, 'Events', first_col_width=12)
        # 5. How the numbers were worked out; nothing for a file only imported.
        processing = _processing_table_builder(experiment)
        if not processing.empty:
            worksheet = _frame_writer(sheets,
                                      processing,
                                      PROCESSING_SHEET,
                                      first_col_width=34,
                                      )
            worksheet.set_column(2, 2, 44)
            worksheet.write(len(processing) + 2,
                            0,
                            'The times are on the clock of the trimmed data, as in '
                            'every other sheet.',
                            )
        # 6. Metadata (OD, volume, dilution factor, settings used, notes, acquisition
        # details).
        fields = [(METADATA_TEXTS.get(k, k), v)
                  for k, v in metadata.items()
                  if k not in ('events', 'ignored_events', 'binary_metadata')
                  ]
        frame = pd.DataFrame({'Field': [k for k, _ in fields],
                              'Value': [json.dumps(v, default=str)
                                        if isinstance(v, (dict, list, tuple))
                                        else v
                                        for _, v in fields
                                        ],
                              },
                             )
        worksheet = _frame_writer(sheets, frame, 'Metadata', first_col_width=24)
        worksheet.set_column(1, 1, 90)

    # ---- 3 Report the export ---------------------------------------------------------
    shown = [Path(output_dir).name, name] + ([subfolder] if subfolder else [])
    print(f"  Exported experiment data to: {'/'.join(shown)}/{name}.xlsx")
    return [output_path] + [folder / str(record[SPECTRAL_FILE_COLUMN])
                            for record in spectral_records
                            ]


# ---- size_describer ------------------------------------------------------------------
def size_describer(size_bytes: float) -> str:
    """
    ---- Summary ----
    Main function to put the size of files to be written in plain words, to two
    significant figures, as the export question shows it.

    ---- Inputs ----
    size_bytes : float
        Size in bytes; 0 or less when there is nothing to write.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        'about 1.2 GB', 'about 350 MB', 'under 1 MB', or 'none in these files' for 0.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    1 GB = 10^9 bytes, 1 MB = 10^6 bytes.

    ---- Helpers ----
    None.
    """

    if size_bytes <= 0:
        return 'none in these files'
    for unit, scale in (('GB', 1e9), ('MB', 1e6)):
        if size_bytes >= scale:
            return f"about {float(f'{size_bytes / scale:.2g}'):g} {unit}"
    return 'under 1 MB'


# ---- spectra_size_estimator ----------------------------------------------------------
def spectra_size_estimator(summaries: List[dict],
                           limits: Dict[str, dict],
                           bytes_per_value: Dict[str, float],
                           ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to work out roughly how large the spectra csv files of an export
    would be, from the number of spectra and wavelengths of each file (read from its
    headers) and the part kept by the trimming.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md), with 'duration_min' and 'spectra_shapes'; a
        summary without 'spectra_shapes' counts as having no spectra.
    limits : Dict[str, dict]
        {file name: {'trim_start', 'trim_end' (min on the recording, None for no trim),
        ...}}; a file missing is not trimmed.
    bytes_per_value : Dict[str, float]
        Bytes one value takes in the csv file of each kind (config.SPECTRA_CSV_BYTES).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (bytes of the trimmed spectra of every file, bytes of the whole recording's
        spectra of the trimmed files only).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    trimmed bytes = sum over files and spectrometers of
        n_spectra x share kept x n_wavelengths x sum(bytes_per_value),
    with the share kept of _kept_fraction_finder.
    full bytes = the same with a share of 1, over the trimmed files only.

    ---- Helpers ----
    _kept_fraction_finder
    """

    per_value = float(sum(bytes_per_value.values()))
    trimmed_bytes, full_bytes = 0.0, 0.0
    for summary in summaries:
        fraction, is_trimmed = _kept_fraction_finder(summary, limits)
        for n_spectra, n_wavelengths in (summary.get('spectra_shapes') or {}).values():
            whole = float(n_spectra) * float(n_wavelengths) * per_value
            trimmed_bytes += whole * fraction
            if is_trimmed:
                full_bytes += whole
    return trimmed_bytes, full_bytes


# ---- workbook_size_estimator ---------------------------------------------------------
def workbook_size_estimator(summaries: List[dict],
                            limits: Dict[str, dict],
                            bytes_per_point: float,
                            ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to work out roughly how large the workbooks of the export of the
    import would be, from the number of data points of each file and the part kept by
    the trimming.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md), with 'duration_min' and 'frames' (the number
        of data points); a summary without 'frames' counts as having none.
    limits : Dict[str, dict]
        {file name: {'trim_start', 'trim_end' (min on the recording, None for no trim),
        ...}}; a file missing is not trimmed.
    bytes_per_point : float
        Bytes one data point takes in the workbook, over its sheets together
        (config.WORKBOOK_POINT_BYTES).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (bytes of the trimmed workbook of every file, bytes of the whole recording's
        workbook of the trimmed files only).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    trimmed bytes = sum over files of n_points x share kept x bytes_per_point, with the
    share kept of _kept_fraction_finder.
    full bytes = the same with a share of 1, over the trimmed files only.

    ---- Helpers ----
    _kept_fraction_finder
    """

    trimmed_bytes, full_bytes = 0.0, 0.0
    for summary in summaries:
        fraction, is_trimmed = _kept_fraction_finder(summary, limits)
        whole = float(summary.get('frames') or 0) * float(bytes_per_point)
        trimmed_bytes += whole * fraction
        if is_trimmed:
            full_bytes += whole
    return trimmed_bytes, full_bytes
