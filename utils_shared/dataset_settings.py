"""
The settings kept with a dataset: read from and written to a file in its folder.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Dict, Optional


# ---- CONSTANTS -----------------------------------------------------------------------
# what is known about each run, kept beside its trim and ignore limits
SAVED_VALUE_KEYS = ('OD', 'volume', 'dilution_factor', 'events')
SETTINGS_FILE_NAME = 'portimao_settings.json'
# Only cells are measured, so the haem amounts, which depend on the size of each shape,
# are no longer shown: a dataset saved showing them opens showing delta A.
RETIRED_HAEM_MODES = {'conc': 'delta'}
RETIRED_HAEM_MODE_KEYS = ('haem_mode', 'ho_haem_mode')


# ---- HELPERS -------------------------------------------------------------------------


# ---- _event_plainer ------------------------------------------------------------------
def _event_plainer(event: dict) -> dict:
    """
    ---- Summary ----
    Helper function to keep an event's label, concentration and whether it is ignored
    as plain numbers and text, so it can be written to the settings file.

    ---- Inputs ----
    event : dict
        {'datapoint', 'label', 'concentration_uM', 'ignored'} as the event questions
        give it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The same keys, as int, str, float or None, and bool.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    concentration = event.get('concentration_uM')
    return {'datapoint': int(event['datapoint']),
            'label': str(event.get('label') or ''),
            'concentration_uM': None if concentration is None else float(concentration),
            'ignored': bool(event.get('ignored', False)),
            }


# ---- _export_folder_resolver ---------------------------------------------------------
def _export_folder_resolver(folder: Path, text: Optional[str]) -> Optional[Path]:
    """
    ---- Summary ----
    Helper function to turn the results folder written in the settings file back into
    a full path.

    ---- Inputs ----
    folder : Path
        The dataset folder.
    text : Optional[str]
        The results folder as written in the file: relative to the dataset folder, or
        a full path; None or empty when none was kept.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Path]
        The results folder, or None when none was kept or a full path was written on
        another computer (its drive or root folder is not there).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not text or not isinstance(text, str):
        return None
    path = Path(text)
    if not path.is_absolute():
        return folder / path
    return path if Path(path.anchor).exists() else None


# ---- _export_folder_shortener --------------------------------------------------------
def _export_folder_shortener(folder: Path, export_root: Path) -> str:
    """
    ---- Summary ----
    Helper function to write the results folder relative to the dataset folder when it
    is inside it, so the settings still hold after the dataset is copied elsewhere.

    ---- Inputs ----
    folder : Path
        The dataset folder.
    export_root : Path
        The results folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The path from the dataset folder with forward slashes ('results'), or the full
        path when the results folder is somewhere else.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        return Path(export_root).resolve().relative_to(Path(folder).resolve(),
                                                       ).as_posix()
    except ValueError:  # not inside the dataset folder
        return str(Path(export_root).resolve())


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- dataset_settings_reader ---------------------------------------------------------
def dataset_settings_reader(folder: Path) -> dict:
    """
    ---- Summary ----
    Main function to read the settings last saved for a dataset from the file in its
    folder.

    ---- Inputs ----
    folder : Path
        The dataset folder (the folder of the .paf files).

    ---- Globals read ----
    SETTINGS_FILE_NAME, RETIRED_HAEM_MODES, RETIRED_HAEM_MODE_KEYS (module constants).

    ---- Outputs ----
    dict
        {'export_folder': Optional[Path], 'files': dict, 'answers': dict}
        (DATA_FORMAT.md, dataset_settings). An empty dict when the dataset was never
        saved or its file cannot be read, so the standard settings are used. A haem
        way of showing no longer offered (RETIRED_HAEM_MODES) is given as its successor.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_folder_resolver
    """

    # ---- 1 Read the file -------------------------------------------------------------
    try:
        values = json.loads((Path(folder) / SETTINGS_FILE_NAME).read_text('utf-8'))
    except (OSError, ValueError):
        return {}
    if not isinstance(values, dict):
        return {}

    # ---- 2 Keep the parts that have the right form -----------------------------------
    files = values.get('files')
    answers = dict(values.get('answers')) if isinstance(values.get('answers'),
                                                        dict,
                                                        ) else {}

    # ---- 3 Read a way of showing the haems no longer offered as its successor --------
    for key in RETIRED_HAEM_MODE_KEYS:
        if answers.get(key) in RETIRED_HAEM_MODES:
            answers[key] = RETIRED_HAEM_MODES[answers[key]]
    return {'export_folder': _export_folder_resolver(Path(folder),
                                                     values.get('export_folder'),
                                                     ),
            'files': files if isinstance(files, dict) else {},
            'answers': answers,
            }


# ---- dataset_settings_saver ----------------------------------------------------------
def dataset_settings_saver(folder: Path,
                           export_root: Path,
                           files: dict,
                           answers: dict,
                           ) -> bool:
    """
    ---- Summary ----
    Main function to save the settings of a dataset in a file in its folder, so the
    dataset opens with them next time, on this computer or another.

    ---- Inputs ----
    folder : Path
        The dataset folder (the folder of the .paf files).
    export_root : Path
        The results folder.
    files : dict
        {file name: limits in minutes, OD values and events} as file_settings_merger
        builds it.
    answers : dict
        The answers of the run.

    ---- Globals read ----
    SETTINGS_FILE_NAME (module constant).

    ---- Outputs ----
    bool
        True when the file was written; False when the folder cannot be written to.

    ---- Globals mutated ----
    None. Writes the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_folder_shortener
    """

    values = {'export_folder': _export_folder_shortener(Path(folder), export_root),
              'files': files,
              'answers': answers,
              }
    try:
        (Path(folder) / SETTINGS_FILE_NAME).write_text(json.dumps(values, indent=2),
                                                       encoding='utf-8',
                                                       )
    except OSError:
        return False
    return True


# ---- file_settings_merger ------------------------------------------------------------
def file_settings_merger(remembered: Dict[str, dict],
                         limits: Dict[str, dict],
                         details: Dict[str, dict],
                         ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to build the files part of the dataset's settings: for each file of
    this run its limits, OD values and events laid over what was saved before. A value
    not asked this run (the OD when not scaling by OD) stays as it was saved, so it is
    offered next time; files not in this run are kept as they were.

    ---- Inputs ----
    remembered : Dict[str, dict]
        The files part saved before (dataset_settings, DATA_FORMAT.md); empty for a
        dataset never saved.
    limits : Dict[str, dict]
        {file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end'}} of this
        run.
    details : Dict[str, dict]
        {file name: {'OD', 'volume', 'dilution_factor', 'events'}} of this run; the OD
        values only when scaling by OD.

    ---- Globals read ----
    SAVED_VALUE_KEYS (module constant).

    ---- Outputs ----
    Dict[str, dict]
        {file name: limits, then 'OD', 'volume', 'dilution_factor' (floats) and
        'events' (DATA_FORMAT.md, dataset_settings) where known}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _event_plainer
    """

    files = {name: dict(entry) for name, entry in remembered.items()}
    for name, limit in limits.items():
        entry = files.setdefault(name, {})
        entry.update(limit)
        values = details.get(name) or {}
        for key in SAVED_VALUE_KEYS:
            if values.get(key) is None:
                continue
            entry[key] = ([_event_plainer(e) for e in values[key]]
                          if key == 'events'
                          else float(values[key])
                          )
    return files
