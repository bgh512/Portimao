"""
Export of one processed experiment to an Excel workbook.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import excel_sheet_namer, file_name_sanitiser
from utils_shared.schema import DELTA_HAEM_SOURCES


# ---- CONSTANTS -----------------------------------------------------------------------
# Sheets written when the whole data set is exported (the short export holds only the
# first three).
BASIC_SHEETS = ('CcO2', 'CsO2', 'VoO2')
# Sheets are written in this order; any that are absent from the experiment are skipped.
# (experiment dictionary key, worksheet name). The haem amounts (haem_conc, haem_OD) are
# left out: only cells are measured, and an amount depends on the size of its shape.
DATA_SHEETS = (('CcO2', 'CcO2'),
               ('CsO2', 'CsO2'),
               ('VoO2', 'VoO2'),
               ('VoO2_OD', 'VoO2_OD'),
               ('VoO2_percent', 'VoO2_percent'),
               ('haem_abs', 'haem_abs'),
               ('haem_delta_abs', 'haem_delta_abs'),
               ('haem_abs_OD', 'haem_abs_OD'),
               ('haem_delta_abs_OD', 'haem_delta_abs_OD'),
               ('haem_percent', 'haem_percent'),
               ('delta_psi', 'delta_psi'),
               )
# Spectral arrays exported to CSV (they are far too large for worksheets).
SPECTRAL_CSV_TYPES = (('transmission', 'transmiss'),
                      ('intensity', 'intensity'),
                      ('attenuation', 'attenuation'),
                      )
# folder, inside the folder of a trimmed experiment, that holds its whole recording
FULL_FOLDER = 'full'

# What the user typed for an experiment (OD, volume, dilution factor, event labels and
# concentrations) is kept in the workbook, on the
# "Metadata" and "Events" sheets, and read back on the next run so it does not have to
# be typed again.
SETTINGS_KEYS = ('OD', 'volume', 'dilution_factor')


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


# ---- _spectral_csv_exporter ----------------------------------------------------------
def _spectral_csv_exporter(experiment: dict, folder: Path) -> List[dict]:
    """
    ---- Summary ----
    Helper function to write one CSV per spectral dataset and data type, with
    wavelengths down and one column per spectrum.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    folder : Path
        Existing folder the CSV files are written to.

    ---- Globals read ----
    SPECTRAL_CSV_TYPES (module constant).

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
            # unavailable.
            labels = [f'{t:g} min' if np.isfinite(t) else f'Spectrum {i}'
                      for t, i in zip(times, indices)
                      ]
            frame = pd.DataFrame(spectra.T, columns=labels)
            frame.insert(0, 'Wavelength (nm)', wavelengths)
            csv_name = f'{dataset_name}_{file_suffix}.csv'
            frame.to_csv(folder / csv_name, index=False)
            records.append({'Dataset': dataset_name,
                            'Data type': data_key,
                            'CSV file': csv_name,
                            'Wavelengths': len(wavelengths),
                            'Timepoints': spectra.shape[0],
                            },
                           )
    return records


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- averages_table_builder ----------------------------------------------------------
def averages_table_builder(averages: dict) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to build the Averages worksheet table: one row per window with the
    mean, SD and change from baseline of VoO2 and of each haem.

    ---- Inputs ----
    averages : dict
        Event-window averages, as added to the experiment by
        calculate_experiment_averages (DATA_FORMAT.md); uses averages['windows'].

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Columns Average, Kind (baseline, settled or quick), Start time (min), End time
        (min), then mean, SD and change from baseline (%) for VoO2 and each haem.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Change from baseline = window mean as a percentage of the average0 mean (calculated
    in the averaging step).

    ---- Helpers ----
    _name_lister
    """

    # ---- 1 Get the measurement names -------------------------------------------------
    windows = averages['windows']
    vo2_names, haem_names = _name_lister(windows, 'vo2'), _name_lister(windows, 'haem')

    # ---- 2 Define the column groups --------------------------------------------------
    groups = [('vo2', m, 'VoO2' if len(vo2_names) == 1 else f'VoO2 ({m})')
              for m in vo2_names
              ]
    groups += [('haem', m, str(m)) for m in haem_names]

    # ---- 3 Build the rows ------------------------------------------------------------
    rows = []
    for window_name, window in windows.items():
        # a record without a kind is the baseline or a settled window
        kind = window.get('kind',
                          'baseline' if window_name == 'average0' else 'settled',
                          )
        row = {'Average': window_name,
               'Kind': kind,
               'Start time (min)': window['start_time'],
               'End time (min)': window['end_time'],
               }
        for kind, measurement, label in groups:
            stats = window[kind].get(measurement, {})
            row[f'{label} mean'] = stats.get('mean', np.nan)
            row[f'{label} SD'] = stats.get('sd', np.nan)
            row[f'{label} change from baseline (%)'] = stats.get('change', np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


# ---- experiment_workbook_exporter ----------------------------------------------------
def experiment_workbook_exporter(experiment: dict,
                                 output_dir: Path,
                                 full: bool = False,
                                 spectra: bool = False,
                                 subfolder: str = '',
                                 ) -> List[Path]:
    """
    ---- Summary ----
    Main function to export one experiment to <output_dir>/<name>/<name>.xlsx (or into
    a folder inside that, such as the full/ of a trimmed experiment's whole recording),
    with the CcO2, CsO2 and VoO2 sheets, Averages, Events and Metadata, and optionally
    every processed table and the spectral CSV files.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    output_dir : Path
        Results folder.
    full : bool
        True adds every processed table in the order of DATA_SHEETS.
    spectra : bool
        True also writes the spectral CSV files next to the workbook (large and slow)
        and an index sheet linking to them.
    subfolder : str
        Folder inside the experiment's folder to write into (FULL_FOLDER); '' for the
        experiment's folder itself.

    ---- Globals read ----
    BASIC_SHEETS, DATA_SHEETS and schema.DELTA_HAEM_SOURCES.

    ---- Outputs ----
    List[Path]
        Paths of the files written: the workbook first, then any CSV files.

    ---- Globals mutated ----
    None. Creates the folder, the workbook and optional CSV files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _frame_writer
    _spectral_csv_exporter
    averages_table_builder
    file_name_sanitiser
    """

    # ---- 1 Set up the output paths ---------------------------------------------------
    name = file_name_sanitiser(experiment.get('experiment_name', 'experiment'))
    folder = Path(output_dir) / name / subfolder if subfolder else Path(output_dir,
                                                                        ) / name
    folder.mkdir(parents=True, exist_ok=True)
    output_path = folder / f'{name}.xlsx'
    spectral_records = _spectral_csv_exporter(experiment, folder) if spectra else []

    # ---- 2 Write the workbook --------------------------------------------------------
    used_sheets = set()
    sheet_keys = DATA_SHEETS if full else tuple((k, k) for k in BASIC_SHEETS)
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
                                      'Spectral data',
                                      first_col_width=14,
                                      )
            for row, record in enumerate(spectral_records, start=1):
                worksheet.write_url(row,
                                    2,
                                    f"external:{record['CSV file']}",
                                    link_format,
                                    string=record['CSV file'],
                                    )
            worksheet.set_column(2, 2, 28)
        # 2. Time-resolved datasets.
        for key, sheet_title in sheet_keys:
            frame = experiment.get(key)
            if isinstance(frame, pd.DataFrame) and not frame.empty:
                _frame_writer(sheets, frame, sheet_title)
        # 3. Event-window averages.
        averages = experiment.get('averages')
        if averages and averages.get('windows'):
            table = averages_table_builder(averages)
            worksheet = _frame_writer(sheets, table, 'Averages', first_col_width=14)
            settings = averages['settings']
            used = [f'{label} source: {key}'
                    for label, key in (('VoO2', settings.get('vo2_key')),
                                       ('haem', settings.get('haem_key')),
                                       )
                    if key
                    ]
            notes = ['; '.join(used) + '.',
                     f"The baseline (average0) is {settings['window_minutes']:g} min "
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
            notes.append('Change from baseline = window mean as a percentage of the '
                         'average0 mean (average0 = 100 %).',
                         )
            if settings.get('haem_source') in DELTA_HAEM_SOURCES:
                notes.append('Haem change from baseline (%) is not calculated for '
                             'delta abs sources (they start at 0).',
                             )
            for offset, note in enumerate(notes, start=2):
                worksheet.write(len(table) + offset, 0, note)
        metadata = experiment.get('metadata')
        if not isinstance(metadata, dict):
            metadata = {}
        # 4. Events, with the label and concentration the user entered.
        all_events = (list(metadata.get('events', [])) +
                      list(metadata.get('ignored_events', []))
                      )
        events = sorted(all_events,
                        key=lambda e: e.get('time') if e.get('time') is not None else 0,
                        )
        # always written, so the sheet exists even for a file with no events
        event_frame = pd.DataFrame({'event': [f'Event {i}'
                                              for i in range(1, len(events) + 1)
                                              ],
                                    'datapoint': [e.get('datapoint') for e in events],
                                    'time_min': [e.get('time') for e in events],
                                    'paf_text': [e.get('text', '') for e in events],
                                    'label': [e.get('label', '') for e in events],
                                    'concentration_uM': [e.get('concentration_uM')
                                                         for e in events
                                                         ],
                                    'ignored': [bool(e.get('ignored', False))
                                                for e in events
                                                ],
                                    },
                                   )
        _frame_writer(sheets, event_frame, 'Events', first_col_width=12)
        # 5. Metadata (OD, volume, dilution factor, settings used, notes, acquisition
        # details).
        fields = [(k, v)
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
    return [output_path] + [folder / record['CSV file'] for record in spectral_records]


# ---- saved_settings_reader -----------------------------------------------------------
def saved_settings_reader(output_dir: Path, experiment_name: str) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to read the OD, volume, dilution factor and events saved in the
    workbook of an earlier export.

    ---- Inputs ----
    output_dir : Path
        Results folder.
    experiment_name : str
        Experiment name (file name without the extension).

    ---- Globals read ----
    SETTINGS_KEYS (module constant).

    ---- Outputs ----
    Optional[dict]
        {'OD', 'volume', 'dilution_factor', 'events': [{'datapoint', 'label',
        'concentration_uM', 'ignored'}]}, or None when there is no readable workbook or
        nothing was saved.

    ---- Globals mutated ----
    None. Reads the workbook from disk.

    ---- Equations ----
    None.

    ---- Helpers ----
    workbook_path_builder
    """

    # ---- 1 Find the workbook ---------------------------------------------------------
    path = workbook_path_builder(output_dir, experiment_name)
    if not path.is_file():
        return None

    # ---- 2 Read the sheets -----------------------------------------------------------
    try:
        # every sheet; older workbooks may lack "Events"
        sheets = pd.read_excel(path, sheet_name=None)
    except Exception:  # a file open in Excel, a damaged file: just ask again
        return None
    if 'Metadata' not in sheets:
        return None

    # ---- 3 Read the metadata ---------------------------------------------------------
    saved = {}
    metadata = sheets['Metadata']
    for field, value in zip(metadata['Field'], metadata['Value']):
        if field in SETTINGS_KEYS and pd.notna(value):
            try:
                saved[field] = float(value)
            except (TypeError, ValueError):
                pass

    # ---- 4 Read the events -----------------------------------------------------------
    events = []
    for _, row in sheets.get('Events', pd.DataFrame()).iterrows():
        concentration = row.get('concentration_uM')
        events.append({'datapoint': int(row['datapoint']),
                       'label': '' if pd.isna(row.get('label')) else str(row['label']),
                       'concentration_uM': None
                       if pd.isna(concentration)
                       else float(concentration),
                       'ignored': bool(row.get('ignored', False))
                       if pd.notna(row.get('ignored', False))
                       else False,
                       },
                      )
    saved['events'] = events
    return saved if any(k in saved for k in SETTINGS_KEYS) or events else None


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
    kept fraction = (trim end - trim start) / duration, the trim end being the duration
    and the trim start 0 when not trimmed, kept within 0 to 1.
    trimmed bytes = sum over files and spectrometers of
        n_spectra x kept fraction x n_wavelengths x sum(bytes_per_value).
    full bytes = the same with a fraction of 1, over the trimmed files only.

    ---- Helpers ----
    None.
    """

    per_value = float(sum(bytes_per_value.values()))
    trimmed_bytes, full_bytes = 0.0, 0.0
    for summary in summaries:
        duration = float(summary['duration_min'])
        own = limits.get(summary['name']) or {}
        start, end = own.get('trim_start'), own.get('trim_end')
        is_trimmed = start is not None or end is not None
        kept = ((duration if end is None else float(end)) -
                (0.0 if start is None else float(start))
                )
        fraction = min(max(kept / duration, 0.0), 1.0) if duration > 0 else 1.0
        for n_spectra, n_wavelengths in (summary.get('spectra_shapes') or {}).values():
            whole = float(n_spectra) * float(n_wavelengths) * per_value
            trimmed_bytes += whole * fraction
            if is_trimmed:
                full_bytes += whole
    return trimmed_bytes, full_bytes


# ---- workbook_path_builder -----------------------------------------------------------
def workbook_path_builder(output_dir: Path, experiment_name: str) -> Path:
    """
    ---- Summary ----
    Main function to build the path of the workbook of an experiment.

    ---- Inputs ----
    output_dir : Path
        Results folder.
    experiment_name : str
        Experiment name; made safe for file names.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        <output_dir>/<name>/<name>.xlsx.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    """

    name = file_name_sanitiser(experiment_name)
    return Path(output_dir) / name / f'{name}.xlsx'
