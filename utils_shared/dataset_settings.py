"""
The settings kept with a dataset: read from and written to a file in its folder.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Dict, Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.dataset_setup import saved_setup_reader
from utils_shared.redox_regions import REGION_KEYS, REGION_NAMES


# ---- CONSTANTS -----------------------------------------------------------------------
# what is known about each run, kept beside its trim and ignore limits
SAVED_VALUE_KEYS = ('OD', 'volume', 'dilution_factor', 'events')
SETTINGS_FILE_NAME = 'portimao_settings.json'
# Only cells are measured, so the haem amounts, which depend on the size of each shape,
# are no longer shown: a dataset saved showing them opens showing delta D.
RETIRED_HAEM_MODES = {'conc': 'delta'}
# The answers of the fixed figures the dataset figure took the place of (side by side,
# the 2x2 grid, the time response, the haem and OCR response): a dataset saved with
# them opens without them.
RETIRED_ANSWER_NAMES = ('plot_comparison',
                        'plot_exemplar',
                        'plot_haem_ocr',
                        'plot_time_response',
                        )
RETIRED_ANSWER_STARTS = ('comparison_', 'ex_', 'ho_', 'tr_')
# Answers saved under a name since changed, by answer: {old name: new name}. The Valencia
# scatter is now Palencia, and the preset temp_fit_037v is now the Rowan fit 11-2026.
RENAMED_ANSWERS = {'haem_background': {'valencia': 'palencia'},
                   'fit_file': {'temp_fit_037v.csv': 'rowan_fit_11_2026.csv'},
                   }


# ---- HELPERS -------------------------------------------------------------------------


# ---- _event_plainer ------------------------------------------------------------------
def _event_plainer(event: dict) -> dict:
    """
    ---- Summary ----
    Helper function to keep an event's label, stock, volume added, concentrations and
    whether it is ignored as plain numbers and text, so it can be written to the
    settings file.

    ---- Inputs ----
    event : dict
        {'datapoint', 'label', 'stock_uM', 'added_uL', 'addition_uM',
        'concentration_uM', 'ignored'} as the event questions give it; the numbers
        may be None or missing (a dataset saved before they were asked).

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

    numbers = {key: (None if event.get(key) is None else float(event[key]))
               for key in ('stock_uM', 'added_uL', 'addition_uM', 'concentration_uM')
               }
    return {'datapoint': int(event['datapoint']),
            'label': str(event.get('label') or ''),
            **numbers,
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
    SETTINGS_FILE_NAME, RETIRED_HAEM_MODES, RENAMED_ANSWERS, RETIRED_ANSWER_NAMES,
    RETIRED_ANSWER_STARTS (module constants).

    ---- Outputs ----
    dict
        {'export_folder': Optional[Path], 'files': dict, 'answers': dict, 'setup':
        dict, 'page': Any} (DATA_FORMAT.md, dataset_settings); the set-up is empty
        for a dataset never set up, and the page is as the file holds it, unchecked
        (None for none). An empty dict when the dataset was never
        saved or its file cannot be read, so the standard settings are used. A haem
        way of showing no longer offered (RETIRED_HAEM_MODES) is given as its
        successor, an answer saved under an old name (RENAMED_ANSWERS) under its
        new one, and the answers of the fixed figures that are no longer made
        (RETIRED_ANSWER_NAMES, RETIRED_ANSWER_STARTS) are left out.

    ---- Globals mutated ----
    None. Reads the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _export_folder_resolver
    saved_setup_reader
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
    if answers.get('haem_mode') in RETIRED_HAEM_MODES:
        answers['haem_mode'] = RETIRED_HAEM_MODES[answers['haem_mode']]

    # ---- 4 Read an answer saved under an old name as its new name --------------------
    for key, renamed in RENAMED_ANSWERS.items():
        if isinstance(answers.get(key), str) and answers[key] in renamed:
            answers[key] = renamed[answers[key]]

    # ---- 5 Leave out the answers of the figures that are no longer made --------------
    answers = {key: value
               for key, value in answers.items()
               if key not in RETIRED_ANSWER_NAMES
               and not str(key).startswith(RETIRED_ANSWER_STARTS)
               }
    return {'export_folder': _export_folder_resolver(Path(folder),
                                                     values.get('export_folder'),
                                                     ),
            'files': files if isinstance(files, dict) else {},
            'answers': answers,
            'setup': saved_setup_reader(values.get('setup')),
            'page': values.get('page'),
            }


# ---- dataset_settings_saver ----------------------------------------------------------
def dataset_settings_saver(folder: Path,
                           export_root: Path,
                           files: dict,
                           answers: dict,
                           setup: Optional[dict] = None,
                           page: Optional[dict] = None,
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
    setup : Optional[dict]
        The dataset set-up table as it is saved (saved_setup, DATA_FORMAT.md, from
        setup_plainer); None or empty writes none.
    page : Optional[dict]
        The page of the dataset figure as plain values (plain_page, DATA_FORMAT.md,
        from page_plainer); None or a page with no plot writes none.

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
    if setup:
        values['setup'] = setup
    if page and page.get('plots'):
        values['page'] = page
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
                         regions: Optional[Dict[str, Dict[str, float]]] = None,
                         ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to build the files part of the dataset's settings: for each file of
    this run its limits, OD values, events and regions laid over what was saved before.
    A value not asked this run (the OD when not scaling by OD) stays as it was saved,
    so it is offered next time; files not in this run are kept as they were.

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
    regions : Optional[Dict[str, Dict[str, float]]]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} of
        this run, as times on the original recording (min); a region not chosen has
        its two edges together. None when the regions were not handled this run, so
        those saved before stay.

    ---- Globals read ----
    SAVED_VALUE_KEYS (module constant); REGION_KEYS, REGION_NAMES.

    ---- Outputs ----
    Dict[str, dict]
        {file name: limits, then 'OD', 'volume', 'dilution_factor' (floats),
        'events' and 'regions' (DATA_FORMAT.md, dataset_settings) where known}. A
        file of this run with neither region chosen has no 'regions'.

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
        if regions is None:
            continue
        own = regions.get(name) or {}
        is_chosen = (all(key in own for key in REGION_KEYS) and
                     any(own[f'{region}_end'] > own[f'{region}_start']
                         for region in REGION_NAMES
                         )
                     )
        if is_chosen:
            entry['regions'] = {key: float(own[key]) for key in REGION_KEYS}
        else:
            entry.pop('regions', None)
    return files
