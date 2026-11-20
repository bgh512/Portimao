"""
Makes the program's folders importable from the tests, however pytest is started.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import sys
from pathlib import Path


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent

# pytest reads this file before it collects the tests, so the path is set in time
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
