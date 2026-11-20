"""
Builds the Mac app (Portimao.app) with PyInstaller and signs it ad hoc; run on a Mac.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import plistlib
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence


# ---- CONSTANTS -----------------------------------------------------------------------
APP_NAME = 'Portimao'
ROOT = Path(__file__).resolve().parent.parent
DIST_FOLDER = ROOT / 'dist'  # where the app is made (git-ignored)
WORK_FOLDER = ROOT / 'build'  # PyInstaller's working files (git-ignored)
APP_PATH = DIST_FOLDER / f'{APP_NAME}.app'
# the icon is made from this picture by PyInstaller (with Pillow) until the icon
# masters exist
ICON = ROOT / 'assets' / 'icon.png'
BUNDLE_ID = 'io.github.bgh512.portimao'
# the program's own files read while it runs, and where they go inside the app
INSIDE = ((ROOT / 'fits', 'fits'),
          (ROOT / 'assets' / 'icon.png', 'assets'),
          (ROOT / 'QUESTION_FLOW.md', '.'),  # its title gives the version
          )
VERSION_PATTERN = re.compile(r'\d+(?:\.\d+)*')
# shown by macOS when the app first opens one of these places
FOLDER_REASON = 'Portimao reads your .paf files and saves the results where you choose.'
PLIST_VALUES = {'CFBundleDisplayName': APP_NAME,
                'NSHighResolutionCapable': True,
                'NSDocumentsFolderUsageDescription': FOLDER_REASON,
                'NSDesktopFolderUsageDescription': FOLDER_REASON,
                'NSDownloadsFolderUsageDescription': FOLDER_REASON,
                'NSRemovableVolumesUsageDescription': FOLDER_REASON,
                'NSNetworkVolumesUsageDescription': FOLDER_REASON,
                }


# ---- BUILD HELPERS -------------------------------------------------------------------


# ---- _ad_hoc_signer ------------------------------------------------------------------
def _ad_hoc_signer(app: Path) -> None:
    """
    ---- Summary ----
    Helper function to sign the app ad hoc (no Apple certificate), as Apple Silicon
    Macs need every program to be signed, then to check the signature.

    ---- Inputs ----
    app : Path
        The .app folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing. Raises RuntimeError, with codesign's own words, when the signing or
        the check fails.

    ---- Globals mutated ----
    None. Signs the files of the app (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for command in (['codesign', '--force', '--deep', '--sign', '-', str(app)],
                    ['codesign',
                     '--verify',
                     '--deep',
                     '--strict',
                     '--verbose=2',
                     str(app),
                     ],
                    ):
        done = subprocess.run(command, capture_output=True, text=True)
        if done.returncode != 0:
            raise RuntimeError(f'The app could not be signed ({command[1]} failed): '
                               f'{done.stderr.strip()}',
                               )


# ---- _arguments_builder --------------------------------------------------------------
def _arguments_builder(packages: Sequence[str]) -> List[str]:
    """
    ---- Summary ----
    Helper function to build PyInstaller's arguments: a windowed Mac app made from
    main.py, with its icon, the program's own files and the details of each package.

    ---- Inputs ----
    packages : Sequence[str]
        Names of the packages whose details (version) the app must carry; the
        self-test lists their versions.

    ---- Globals read ----
    APP_NAME, BUNDLE_ID, DIST_FOLDER, ICON, INSIDE, ROOT, WORK_FOLDER (module
    constants).

    ---- Outputs ----
    List[str]
        The arguments, as typed after `pyinstaller`.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    arguments = [str(ROOT / 'main.py'),
                 '--name',
                 APP_NAME,
                 '--windowed',
                 '--noconfirm',
                 '--clean',
                 '--log-level',
                 'WARN',
                 '--icon',
                 str(ICON),
                 '--osx-bundle-identifier',
                 BUNDLE_ID,
                 '--paths',
                 str(ROOT),
                 '--distpath',
                 str(DIST_FOLDER),
                 '--workpath',
                 str(WORK_FOLDER),
                 '--specpath',
                 str(WORK_FOLDER),
                 ]
    for source, target in INSIDE:
        arguments += ['--add-data', f'{source}:{target}']
    for package in packages:
        arguments += ['--copy-metadata', package]
    return arguments


# ---- _info_plist_writer --------------------------------------------------------------
def _info_plist_writer(plist_path: Path, version: str) -> None:
    """
    ---- Summary ----
    Helper function to write the program's version, its name and the reasons macOS
    shows when the app asks for a guarded folder into the app's Info.plist, keeping
    every other key PyInstaller wrote.

    ---- Inputs ----
    plist_path : Path
        The app's Contents/Info.plist.
    version : str
        Program version, for example "2.2" (program_version_reader).

    ---- Globals read ----
    PLIST_VALUES, VERSION_PATTERN (module constants).

    ---- Outputs ----
    None
        Nothing. Raises ValueError when the version is not made of numbers and dots.

    ---- Globals mutated ----
    None. Rewrites the file (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f'The program version was not found (got "{version}"): '
                         'check the title of QUESTION_FLOW.md.',
                         )
    with open(plist_path, 'rb') as stream:
        values = plistlib.load(stream)
    values.update(PLIST_VALUES)
    values['CFBundleShortVersionString'] = version
    values['CFBundleVersion'] = version
    with open(plist_path, 'wb') as stream:
        plistlib.dump(values, stream)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function to build dist/Portimao.app on this Mac, for its own kind of chip: the
    program with Python, Tk and every package inside, the release's version in its
    Info.plist, signed ad hoc. Run it with the program's environment, with PyInstaller
    installed in it.

    ---- Inputs ----
    None.

    ---- Globals read ----
    APP_PATH, ROOT (module constants).

    ---- Outputs ----
    int
        0 when the app was built and its signature checks, 1 otherwise (the reason is
        printed).

    ---- Globals mutated ----
    None. Puts the program folder first on sys.path; writes build/ and dist/ (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _ad_hoc_signer
    _arguments_builder
    _info_plist_writer
    program_version_reader
    """

    # ---- 1 Check this computer can build it ------------------------------------------
    if sys.platform != 'darwin':
        print('The Mac app can only be built on a Mac.')
        return 1
    try:
        import PyInstaller.__main__
    except ImportError:
        print('PyInstaller is missing: install it in this environment with '
              '"python -m pip install pyinstaller", then run this again.',
              )
        return 1

    # ---- 2 Read the version and the package list from the program --------------------
    # The program's folders can be imported only once the program folder is on the path.
    sys.path.insert(0, str(ROOT))
    from utils_shared.helpers import program_version_reader
    from utils_viewer.viewer_self_test import PACKAGES
    version = program_version_reader(ROOT)

    # ---- 3 Build, write the version and sign -----------------------------------------
    PyInstaller.__main__.run(_arguments_builder(PACKAGES))
    plist_path = APP_PATH / 'Contents' / 'Info.plist'
    try:
        _info_plist_writer(plist_path, version)
        _ad_hoc_signer(APP_PATH)
    except OSError:
        print(f'The app was not finished: {plist_path} could not be read or written; '
              f'check that PyInstaller made the app.',
              )
        return 1
    except (RuntimeError, ValueError) as exc:  # their messages are written for people
        print(f'The app was not finished. {exc}')
        return 1
    print(f'Built {APP_PATH} (V{version}), signed ad hoc.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
