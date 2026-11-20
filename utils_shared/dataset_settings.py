"""
The settings kept with a dataset: read from and written to a file in its folder.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Optional


# ---- CONSTANTS -----------------------------------------------------------------------
SETTINGS_FILE_NAME = 'portimao_settings.json'


# ---- HELPERS -------------------------------------------------------------------------


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
        The path from the dataset folder with forward slashes ('export'), or the full
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
    SETTINGS_FILE_NAME (module constant).

    ---- Outputs ----
    dict
        {'export_folder': Optional[Path], 'files': dict, 'answers': dict}
        (DATA_FORMAT.md, dataset_settings). An empty dict when the dataset was never
        saved or its file cannot be read, so the standard settings are used.

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
    answers = values.get('answers')
    return {'export_folder': _export_folder_resolver(Path(folder),
                                                     values.get('export_folder'),
                                                     ),
            'files': files if isinstance(files, dict) else {},
            'answers': answers if isinstance(answers, dict) else {},
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
        {file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end'}} in
        minutes.
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
