"""
Double-click this file to start the program without a terminal window.
"""

# ---- STANDARD IMPORTS ----
import runpy
from pathlib import Path


# ---- MAIN FUNCTIONS ----


# ---- main ----
def main() -> None:
    """
    ---- Summary ----
    Main function to start the program by running launchers/bootstrap.pyw as if
    it had been started directly.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """
    runpy.run_path(
        str(Path(__file__).resolve().parent / 'launchers' / 'bootstrap.pyw'),
        run_name='__main__',
    )


if __name__ == '__main__':
    main()
