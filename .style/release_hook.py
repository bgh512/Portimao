"""
Release hook that writes the new version into the title of QUESTION_FLOW.md at every
release.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
import sys
from pathlib import Path


# ---- CONSTANTS -----------------------------------------------------------------------
QUESTION_FLOW_FILE = 'QUESTION_FLOW.md'
TITLE_PATTERN = re.compile(r'^(?P<title>#\s.*\S)\s*\(V[^)]*\)\s*$')
VERSION_PATTERN = re.compile(r'^\d+(\.\d+)*$')


# ---- TITLE HELPERS -------------------------------------------------------------------


# ---- _title_writer -------------------------------------------------------------------
def _title_writer(path: Path, version: str) -> bool:
    """
    ---- Summary ----
    Helper function to write the version into the title (the first line) of a document
    whose title ends in (V<version>), leaving every other byte as it was.

    ---- Inputs ----
    path : Path
        The document; it must exist.
    version : str
        Version text without the V, e.g. '1.6'.

    ---- Globals read ----
    TITLE_PATTERN : re.Pattern
        A title line ending in (V<version>).

    ---- Outputs ----
    bool
        True when the title now carries the version, False when the first line is not
        a title ending in (V<version>), in which case nothing is written.

    ---- Globals mutated ----
    None. Rewrites the file when its title changes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    text = path.read_bytes().decode('utf-8')
    first, newline, rest = text.partition('\n')
    ending = '\r' if first.endswith('\r') else ''
    match = TITLE_PATTERN.match(first.rstrip('\r'))
    if not match:
        return False
    new_first = f'{match.group("title")} (V{version}){ending}'
    if new_first != first:
        path.write_bytes(f'{new_first}{newline}{rest}'.encode('utf-8'))
    return True


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function to put the version being released into the title of the question
    list, so the title always names the program version the list describes.

    ---- Inputs ----
    None. The version is the one command-line argument, as the release passes it.

    ---- Globals read ----
    QUESTION_FLOW_FILE : str
        Name of the question list, in the project root.
    VERSION_PATTERN : re.Pattern
        A version such as 1.6.
    sys.argv.

    ---- Outputs ----
    int
        0 when the title carries the version; 1 when it could not be written, after
        printing one sentence that says what is wrong and what to do, which stops the
        release.

    ---- Globals mutated ----
    None. Rewrites the title of QUESTION_FLOW.md and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _title_writer
    """

    # ---- 1 Read the version ----------------------------------------------------------
    if len(sys.argv) != 2 or not VERSION_PATTERN.match(sys.argv[1]):
        print('The release hook needs the new version, for example '
              '"python .style/release_hook.py 1.6"; run it again with the version.',
              )
        return 1
    version = sys.argv[1]

    # ---- 2 Write it into the title ---------------------------------------------------
    path = Path(__file__).resolve().parents[1] / QUESTION_FLOW_FILE
    if not path.is_file():
        print(f'{QUESTION_FLOW_FILE} was not found in the project folder, so its '
              f'version could not be updated. Put the file back and release again.',
              )
        return 1
    if not _title_writer(path, version):
        print(f'The first line of {QUESTION_FLOW_FILE} does not end in a version such '
              f'as (V{version}), so it could not be updated. End the title with '
              f'(V{version}) and release again.',
              )
        return 1
    print(f'{QUESTION_FLOW_FILE}: title set to V{version}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
