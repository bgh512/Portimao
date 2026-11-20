"""
Makes the Windows icon from assets/icon.png (square, 512 x 512 pixels or larger).
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import sys
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from PIL import Image


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'assets' / 'icon.png'
WINDOWS_SIZES = [(16, 16),
                 (24, 24),
                 (32, 32),
                 (48, 48),
                 (64, 64),
                 (128, 128),
                 (256, 256),
                 ]


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function to square assets/icon.png and turn it into the Windows icon
    (assets/icon.ico). The Mac app's icon is made from assets/icon.png when the app is
    built (launchers/mac_app_builder.py).

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, SOURCE, WINDOWS_SIZES (module constants).

    ---- Outputs ----
    int
        0 when the icons were made, 1 when the picture is missing.

    ---- Globals mutated ----
    None. Writes the icon files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if not SOURCE.exists():
        print(f'Put your icon at {SOURCE} first.')
        return 1
    picture = Image.open(SOURCE).convert('RGBA')
    side = max(picture.size)
    square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    square.paste(picture, ((side - picture.width) // 2, (side - picture.height) // 2))
    square.save(SOURCE)
    square.save(ROOT / 'assets' / 'icon.ico', sizes=WINDOWS_SIZES)
    print('Made assets/icon.ico.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
