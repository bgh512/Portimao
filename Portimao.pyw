"""
Double-click this file to start the program without a terminal window.
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / 'launchers' / 'bootstrap.pyw'),
               run_name='__main__',
               )
