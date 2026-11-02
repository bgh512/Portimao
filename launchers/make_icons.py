"""
Makes every icon file from one picture: put the new icon at assets/icon.png (square,
at least 512 x 512 pixels, ideally 1024 x 1024) and run this file once with the Python
of the private environment, or any Python that has Pillow installed.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import sys
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from PIL import Image


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'assets' / 'icon.png'
WINDOWS_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128),
                 (256, 256)]
MAC_FILE = ROOT / 'Albufeira.app' / 'Contents' / 'Resources' / 'Albufeira.icns'


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function to turn assets/icon.png into the Windows icon (assets/icon.ico) and
    the Mac icon (inside Albufeira.app).

    ---- Inputs ----
    None.

    ---- Globals read ----
    ROOT, SOURCE, WINDOWS_SIZES, MAC_FILE (module constants).

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
    MAC_FILE.parent.mkdir(parents=True, exist_ok=True)
    square.resize((1024, 1024)).save(MAC_FILE, format='ICNS')
    print('Made assets/icon.ico and Albufeira.app/Contents/Resources/Albufeira.icns.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
