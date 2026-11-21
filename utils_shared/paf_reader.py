"""
Direct reader of Espana Scientific Software .paf files.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import bisect
import mmap
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.ocr_checking import ocr_check_describer, ocr_checker, OCR_TRACES
from utils_shared.schema import TIME_COLUMN
from utils_shared.user_notices import warning_shower


# ---- CONSTANTS -----------------------------------------------------------------------
# the layout of a .paf file is described in DATA_FORMAT.md, under Files
MARK =b'\x06Espana\x00\x00\x00\x00\x00'

# spectrometer name in the file -> dataset name used by the rest of the program
DATASET_ALIAS = {'Cytochromes': 'Cyt'}
LN10 = float(np.log(10.0))

TRACE_COLUMNS = {'CsO2': 'Set O2', 'CcO2': 'Measured O2', 'VoO2': 'VoO2'}
# unit the rest of the program assumes for each trace (the figure labels are written
# for these)
TRACE_UNITS = {'CsO2': 'µM', 'CcO2': 'µM', 'VoO2': 'µM/min'}
# traces whose column title carries the unit; the VoO2 column is looked up by its name
UNIT_IN_TITLE = ('CsO2', 'CcO2')
# written in a title when the file stores no unit for the trace
FALLBACK_UNIT = 'uM'

# a trace covers the recording when it has at least this fraction of the clock's length
MIN_TRACE_FRACTION = 0.9
# a trace missing more than this fraction of the clock's length is reported
SHORT_TRACE_FRACTION = 0.01
# the oxygen rates; the instrument leaves their last points empty (the number is stored
# in the VoO2Math record), which is not reported
RATE_TRACES = ('VrO2', 'DgO2', 'VoO2')

# the VoO2Math record (DATA_FORMAT.md, under Files): after the last trace name come
# two empty strings and four zero bytes, then the settings at these byte offsets
OCR_SETTINGS_RECORD = 'VoO2Math'
OCR_SETTINGS_START = b'\x02\x00\x00\x00' + bytes(4) + b'\x02\x00\x00\x00' + bytes(8)
PERMEABILITY_OFFSET = 20  # 32-bit float, µM/min/mmHg
FALL_EDGE_OFFSET = 32  # whole number of points
LEAK_START_OFFSET = 36  # whole number of points
OCR_SETTINGS_BYTES = 40
# what a permeability and a number of points can be; outside these the record is not
# understood
PERMEABILITY_RANGE = (0.0, 10.0)
POINTS_RANGE = (1, 1000)

# how each trace the program uses is called in a message
TRACE_LABELS = {'CsO2': 'set oxygen (CsO2)',
                'CcO2': 'measured oxygen (CcO2)',
                'VoO2': 'OCR (VoO2)',
                }

SEND_FILE_ADVICE = 'Please send the file to the person who looks after this program.'
COPY_AGAIN_ADVICE = 'Copy it again from the instrument computer.'
CANNOT_OPEN = ('the file could not be opened. Close it in any other program (the '
               'instrument software, for example), check that you are allowed to read '
               'it, then start this program again to include it.'
               )
NOT_A_PAF = ('this is not a recording of the instrument software (it does not start '
             'the way a .paf file does). Check that the right file is in the folder.'
             )
TOO_SMALL = ('the file is too small to be a recording (it may not have finished '
             f'copying). {COPY_AGAIN_ADVICE}'
             )
UNKNOWN_LAYOUT = ('the file is laid out in a way this program does not know, so it '
                  f'cannot be read. {SEND_FILE_ADVICE}'
                  )
# what reading a file with an unknown layout can raise
LAYOUT_ERRORS = (ArithmeticError, LookupError, struct.error, TypeError, ValueError)


# ---- PafError ------------------------------------------------------------------------
class PafError(Exception):
    """
    ---- Summary ----
    Raised when the file cannot be opened, is not a .paf, is cut short, has a layout
    this reader does not know or lacks what the program needs. The message starts with
    the file name and says in plain words what is wrong and what to do, so it can be
    shown to the user as it is.

    ---- Attributes ----
    None.

    ---- Globals read ----
    None.

    ---- Methods ----
    None.
    """


# ---- Spectra -------------------------------------------------------------------------
@dataclass
class Spectra:
    """
    ---- Summary ----
    One parsed 'Spectra: CCD' record (one spectrometer) of a .paf file.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    offset: int = 0
    name: str = ''
    nframes: int = 0
    npix: int = 0
    wl_off: Optional[int] = None
    wavelengths: Optional[np.ndarray] = None
    data_off: int = 0
    data_end: int = 0
    log: Optional[np.ndarray] = None
    rec_end: int = 0
    params: dict = field(default_factory=dict)
    checks: dict = field(default_factory=dict)


# ---- PafFile -------------------------------------------------------------------------
class PafFile:
    """
    ---- Summary ----
    An open .paf file (memory-mapped, so a 100 MB file is not read into RAM). Use ``with
    PafFile(path) as paf:``. Everything handed out by the methods is a copy, so it stays
    valid after the file is closed.

    ---- Attributes ----
    path : Path
        Path to the .paf file.
    records : List[dict]
        Record table from record_scanner (see DATA_FORMAT.md).
    spectra : List[Spectra]
        Parsed spectrometer records.
    time_s : np.ndarray
        Time of every frame in seconds, shape (n_frames,).

    ---- Globals read ----
    None.

    ---- Methods ----
    __init__
    __enter__
    __exit__
    acquisition_reader
    closer
    dataset_name_lister
    duration_finder
    events_reader
    frame_counter
    missing_trace_describer
    notes_reader
    ocr_settings_reader
    ocr_trace_checker
    spectra_dataset_reader
    stream_name_lister
    stream_reader
    stream_unit_reader
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, path: Union[str, Path]) -> None:
        """
        ---- Summary ----
        Main method to open a .paf file, memory-map it, scan its records and find the
        time base and the traces that cover it.

        ---- Inputs ----
        path : Union[str, Path]
            Path to the .paf file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing. Sets path, records, spectra, time_s (seconds) and the private
            stream tables. Raises PafError, starting with the file name and saying in
            plain words what is wrong and what to do, for a file that cannot be opened,
            is too small, has no Time stream or has a layout this reader does not know.

        ---- Globals mutated ----
        None. Opens the file and the memory map (side effect); closes them again if
        reading fails.

        ---- Equations ----
        None.

        ---- Helpers ----
        closer
        record_scanner
        stream_extractor
        """

        # ---- 1 Open the file ---------------------------------------------------------
        self.path = Path(path)
        name = self.path.name
        self._fh = None
        self._mm = None
        self._skipped = {}
        try:
            self._fh = open(self.path, 'rb')

            # ---- 2 Map the file and scan its records ---------------------------------
            if self.path.stat().st_size < 1024:
                raise PafError(TOO_SMALL)
            self._mm = mmap.mmap(self._fh.fileno(), 0, access=mmap.ACCESS_READ)
            self.records, self.spectra = record_scanner(self._mm, name)
            self._streams, skipped = stream_extractor(self._mm, self.records, name)

            # ---- 3 Find the time axis and main streams -------------------------------
            times = [s for s in self._streams if s['name'] == 'Time']
            if not times:
                raise PafError('the file has no clock (Time trace), so nothing in it '
                               f'can be placed in time. {SEND_FILE_ADVICE}',
                               )
            main = max(times, key=lambda s: s['n'])
            self.time_s = np.array(main['values'], dtype=float)
            # a file can hold its clock twice; no copy of it is a trace to show
            self._main = {}
            for s in self._streams:
                if s['name'] == 'Time' or s['name'] in self._main:
                    continue
                if s['n'] >= MIN_TRACE_FRACTION * len(self.time_s):
                    self._main[s['name']] = s
                else:
                    skipped.setdefault(s['name'],
                                       f"it has only {s['n']} of the "
                                       f'{len(self.time_s)} points of the recording',
                                       )
            # a trace stored twice is not missing when one of its copies can be read
            self._skipped = {key: reason
                             for key, reason in skipped.items()
                             if key not in self._main
                             }
        except PafError as exc:
            self.closer()
            raise PafError(f'{name}: {exc}') from None
        except OSError as exc:
            self.closer()
            raise PafError(f'{name}: {CANNOT_OPEN}') from exc
        # an unexpected layout is a problem of the file, said in plain words
        except LAYOUT_ERRORS as exc:
            self.closer()
            raise PafError(f'{name}: {UNKNOWN_LAYOUT}') from exc

    # ---- SPECIAL METHODS -------------------------------------------------------------

    # ---- __enter__ -------------------------------------------------------------------
    def __enter__(self) -> 'PafFile':
        """
        ---- Summary ----
        Main method to support `with PafFile(path) as paf:`.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        PafFile
            The open file itself.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return self

    # ---- __exit__ --------------------------------------------------------------------
    def __exit__(self, *exc: Any) -> None:
        """
        ---- Summary ----
        Main method to close the file when the `with` block ends.

        ---- Inputs ----
        *exc : Any
            Exception information passed by Python (ignored).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing. The exception, if any, is not suppressed.

        ---- Globals mutated ----
        None. Closes the file (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        closer
        """

        self.closer()

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- acquisition_reader ----------------------------------------------------------
    def acquisition_reader(self) -> List[dict]:
        """
        ---- Summary ----
        Main method to summarise the acquisition settings of every spectrometer.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[dict]
            One dictionary per spectrometer: dataset, spectrometer, frames, wavelengths,
            wavelength_range_nm and the parameters read from the file.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        dataset_namer
        """

        return [{'dataset': dataset_namer(sp.name),
                 'spectrometer': sp.name,
                 'frames': sp.nframes,
                 'wavelengths': sp.npix,
                 'wavelength_range_nm': [round(float(sp.wavelengths[0]), 2),
                                         round(float(sp.wavelengths[-1]), 2),
                                         ],
                 **sp.params,
                 }
                for sp in self.spectra
                ]

    # ---- closer ----------------------------------------------------------------------
    def closer(self) -> None:
        """
        ---- Summary ----
        Main method to release the memory map and the file handle and clear the parsed
        tables.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing. Anything handed out earlier stays valid because it is a copy.

        ---- Globals mutated ----
        None. Resets the records, spectra and stream tables of the instance and closes
        the file (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self.records, self.spectra, self._streams, self._main = [], [], [], {}
        try:
            if self._mm is not None:
                self._mm.close()
        except BufferError:
            pass  # a view is still alive; it is released when it is garbage collected
        self._mm = None
        if self._fh is not None and not self._fh.closed:
            self._fh.close()

    # ---- dataset_name_lister ---------------------------------------------------------
    def dataset_name_lister(self) -> List[str]:
        """
        ---- Summary ----
        Main method to list the spectral datasets in the file.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[str]
            Dataset names in file order.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        dataset_namer
        """

        return [dataset_namer(sp.name) for sp in self.spectra]

    # ---- duration_finder -------------------------------------------------------------
    @property
    def duration_finder(self) -> float:
        """
        ---- Summary ----
        Main property to give the length of the recording in minutes.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        float
            Largest time value, in minutes.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        duration (min) = max(time_s) / 60.

        ---- Helpers ----
        None.
        """

        return float(np.nanmax(self.time_s)) / 60.0

    # ---- events_reader ---------------------------------------------------------------
    def events_reader(self) -> List[dict]:
        """
        ---- Summary ----
        Main method to read the text events (additions) stored in the file.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[dict]
            [{'name', 'text', 'datapoint'}] sorted by datapoint; datapoint is the
            1-based spectrum number stored with the event. Events with no stored
            position are ignored with a warning.

        ---- Globals mutated ----
        None. Prints warnings (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _event_lister
        u32_reader
        """

        found = []
        for r in self.records:
            if r['type'] != 'Text Event' or len(r['tokens']) < 4:
                continue
            name, text = r['tokens'][2], r['tokens'][3]
            vpos = name[2] + 20
            value = u32_reader(self._mm, vpos) if vpos + 4 <= text[1] else 0
            found.append((name[0], text[0], value))
        return _event_lister(found, self.path.name)

    # ---- frame_counter ---------------------------------------------------------------
    @property
    def frame_counter(self) -> int:
        """
        ---- Summary ----
        Main property to give the number of time points (frames) in the recording.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        int
            Length of the time base.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return len(self.time_s)

    # ---- missing_trace_describer -----------------------------------------------------
    def missing_trace_describer(self, name: str) -> str:
        """
        ---- Summary ----
        Main method to say in plain words why one trace the program uses cannot be
        given.

        ---- Inputs ----
        name : str
            Trace name, a key of TRACE_LABELS ('CsO2', 'CcO2' or 'VoO2').

        ---- Globals read ----
        TRACE_LABELS (module constant).

        ---- Outputs ----
        str
            For example 'run1.paf: the file has no OCR (VoO2) trace', or 'run1.paf: the
            OCR (VoO2) trace cannot be read, because ...' with the reason noted when
            the trace was skipped. No full stop at the end.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        reason = self._skipped.get(name)
        if reason is None:
            return f'{self.path.name}: the file has no {TRACE_LABELS[name]} trace'
        return (f'{self.path.name}: the {TRACE_LABELS[name]} trace cannot be read, '
                f'because {reason}'
                )

    # ---- notes_reader ----------------------------------------------------------------
    def notes_reader(self) -> str:
        """
        ---- Summary ----
        Main method to read the experiment notes (PaneNote record) as plain text.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            Notes text, or an empty string if there are none.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        rtf_converter
        """

        for r in self.records:
            if r['type'] == 'PaneNote':
                m = self._mm.find(b'{\\rtf1', r['off'], r['end'])
                if m >= 0:
                    return rtf_converter(bytes(self._mm[m:r['end']],
                                               ).rstrip(b'\x00 \r\n'),
                                         )
        return ''

    # ---- ocr_settings_reader ---------------------------------------------------------
    def ocr_settings_reader(self) -> Optional[dict]:
        """
        ---- Summary ----
        Main method to read how the instrument works out its oxygen rates (the
        VoO2Math record).

        ---- Inputs ----
        None.

        ---- Globals read ----
        FALL_EDGE_OFFSET, LEAK_START_OFFSET, OCR_SETTINGS_BYTES, OCR_SETTINGS_RECORD,
        OCR_SETTINGS_START, PERMEABILITY_OFFSET, PERMEABILITY_RANGE, POINTS_RANGE,
        LAYOUT_ERRORS (module constants).

        ---- Outputs ----
        Optional[dict]
            ocr_settings (DATA_FORMAT.md): 'permeability' (µM/min/mmHg),
            'fall_edge_points' and 'leak_start_points'; None when the file has no such
            record or it is not laid out as expected.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        token_reader
        u32_reader
        """

        for r in self.records:
            if r['type'] != OCR_SETTINGS_RECORD:
                continue
            try:
                tokens = token_reader(self._mm, r['off'] + 40, r['end'])
                start = tokens[-1][2]
                tail = bytes(self._mm[start:min(start + OCR_SETTINGS_BYTES, r['end'])])
                if len(tail) < OCR_SETTINGS_BYTES or not tail.startswith(
                    OCR_SETTINGS_START,
                    ):
                    return None
                permeability = struct.unpack_from('<f', tail, PERMEABILITY_OFFSET)[0]
                fall_edge = u32_reader(tail, FALL_EDGE_OFFSET)
                leak_start = u32_reader(tail, LEAK_START_OFFSET)
            except LAYOUT_ERRORS:
                return None
            is_understood = (PERMEABILITY_RANGE[0] < permeability < PERMEABILITY_RANGE[1]
                             and POINTS_RANGE[0] <= fall_edge <= POINTS_RANGE[1]
                             and POINTS_RANGE[0] <= leak_start <= POINTS_RANGE[1]
                             )
            if not is_understood:
                return None
            return {'permeability': float(permeability),
                    'fall_edge_points': int(fall_edge),
                    'leak_start_points': int(leak_start),
                    }
        return None

    # ---- ocr_trace_checker -----------------------------------------------------------
    def ocr_trace_checker(self) -> None:
        """
        ---- Summary ----
        Main method to refuse a file whose OCR trace (VoO2) cannot be given, as nothing
        can be processed without it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        SEND_FILE_ADVICE (module constant).

        ---- Outputs ----
        None
            Nothing. Raises PafError saying why the trace is missing and what to do.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        missing_trace_describer
        """

        if 'VoO2' in self._main:
            return
        advice = (SEND_FILE_ADVICE
                  if 'VoO2' in self._skipped
                  else 'Check in the instrument software that the oxygen consumption '
                       'rate was recorded.'
                  )
        raise PafError(f"{self.missing_trace_describer('VoO2')}, and this program "
                       f'cannot process a file without it. {advice}',
                       )

    # ---- spectra_dataset_reader ------------------------------------------------------
    def spectra_dataset_reader(self,
                               name: str,
                               with_intensity: bool = False,
                               chunk: int = 128,
                               ) -> dict:
        """
        ---- Summary ----
        Main method to read one spectrometer as the dictionary used by the rest of the
        program.

        ---- Inputs ----
        name : str
            Dataset name from dataset_name_lister, e.g. 'Cyt'.
        with_intensity : bool
            True to also return the integer counts.
        chunk : int
            Number of spectra converted at a time (limits memory use).

        ---- Globals read ----
        None.

        ---- Outputs ----
        dict
            {'wavelengths' (nm, n_wavelengths), 'spectrum_indices' (n_spectra), 'time'
            (min, n_spectra), 'transmission' (n_spectra x n_wavelengths; NaN where it
            cannot be worked out)[, 'intensity']}; float64 copies. Raises PafError for
            an unknown dataset or one with more spectra than time points.

        ---- Globals mutated ----
        None. Prints a warning when there are fewer spectra than time points or when
        the transmission is empty at some wavelengths (side effect).

        ---- Equations ----
        intensity = round(10^log), log being the stored log10 row. The transmission is
        given under _transmission_converter.

        ---- Helpers ----
        _spectrum_time_finder
        _transmission_converter
        dataset_name_lister
        dataset_namer
        warning_printer
        """

        # ---- 1 Find the dataset ------------------------------------------------------
        sp = next((s for s in self.spectra if dataset_namer(s.name) == name), None)
        if sp is None:
            raise PafError(f'{self.path.name}: the file has no spectra called {name!r} '
                           f'(it has: '
                           f"{', '.join(self.dataset_name_lister()) or 'none'}). "
                           f'Choose spectra the file has.',
                           )

        # ---- 2 Find the time of every spectrum ---------------------------------------
        # before the spectra are read, so a file that is refused costs no memory
        times = _spectrum_time_finder(self.time_s, sp.nframes, name, self.path.name)

        # ---- 3 Read the spectra in chunks --------------------------------------------
        transmission = np.empty((sp.nframes, sp.npix))
        intensity = np.empty((sp.nframes, sp.npix)) if with_intensity else None
        ref = sp.log[1].astype('f8')
        is_empty = np.zeros(sp.npix, dtype=bool)
        for i0 in range(0, sp.nframes, chunk):
            i1 = min(sp.nframes, i0 + chunk)
            lg = sp.log[2 + i0:2 + i1].astype('f8')
            transmission[i0:i1] = _transmission_converter(lg, ref)
            is_empty |= np.isnan(transmission[i0:i1]).any(axis=0)
            if with_intensity:
                raw = 10.0 ** lg
                raw[~np.isfinite(raw)] = 0.0
                # identical to the software's integer counts
                intensity[i0:i1] = np.round(raw)
        if is_empty.any():
            empty_nm = np.asarray(sp.wavelengths, dtype=float)[is_empty]
            warning_printer(f'{self.path.name}, {name}: the transmission cannot be '
                            f'worked out at {int(is_empty.sum())} wavelengths (between '
                            f'{empty_nm.min():.0f} and {empty_nm.max():.0f} nm), most '
                            f'likely because the reference spectrum has no counts '
                            f'there. It is left empty at these wavelengths.',
                            )

        # ---- 4 Assemble the output ---------------------------------------------------
        out = {'wavelengths': np.array(sp.wavelengths, dtype=float),
               'spectrum_indices': np.arange(1, sp.nframes + 1, dtype='<u4'),
               'time': times,
               'transmission': transmission,
               }
        if with_intensity:
            out['intensity'] = intensity
        return out

    # ---- stream_name_lister ----------------------------------------------------------
    def stream_name_lister(self) -> List[str]:
        """
        ---- Summary ----
        Main method to list the traces that cover the whole recording.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[str]
            Trace names, e.g. 'CsO2', 'CcO2', 'VoO2'.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return list(self._main)

    # ---- stream_reader ---------------------------------------------------------------
    def stream_reader(self, name: str, is_quiet: bool = False) -> Optional[np.ndarray]:
        """
        ---- Summary ----
        Main method to read one trace on the common time base.

        ---- Inputs ----
        name : str
            Trace name, e.g. 'VoO2'.
        is_quiet : bool
            True to read the trace without the warning about a short trace, when it is
            given elsewhere.

        ---- Globals read ----
        RATE_TRACES (module constant).

        ---- Outputs ----
        Optional[np.ndarray]
            float64 array with one value per time point (NaN where the software has no
            value, e.g. the start of VoO2, and at the end of a trace that is shorter
            than the clock), or None if the trace does not exist.

        ---- Globals mutated ----
        None. Prints a warning when the trace is short (see _short_trace_describer)
        (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _short_trace_describer
        ocr_settings_reader
        warning_printer
        """

        s = self._main.get(name)
        if s is None:
            return None
        # A shorter trace is lined up from the start: the software stores the values
        # it does not have at the start (VoO2, DgO2, VrO2) as NaN, so only the end is
        # short. Its own export of these traces has the same values at the same times.
        out = np.full(len(self.time_s), np.nan)
        n = min(len(out), s['n'])
        out[:n] = np.asarray(s['values'][:n], dtype=float)
        n_missing = len(out) - n
        if n_missing and not is_quiet:
            settings = self.ocr_settings_reader() if name in RATE_TRACES else None
            message = _short_trace_describer(name,
                                             n_missing,
                                             len(out),
                                             float(np.nanmedian(np.diff(self.time_s))),
                                             settings['fall_edge_points'] if settings
                                             else 0,
                                             )
            if message:
                warning_printer(message, self.path.name)
        return out

    # ---- stream_unit_reader ----------------------------------------------------------
    def stream_unit_reader(self, name: str) -> str:
        """
        ---- Summary ----
        Main method to give the unit the file stores for one trace.

        ---- Inputs ----
        name : str
            Trace name, e.g. 'CcO2'.

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            The unit as written in the file (for example 'µM'), or an empty string when
            the trace does not exist or has no unit.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return str(self._main.get(name, {}).get('unit', '')).strip()


# ---- READER HELPERS ------------------------------------------------------------------


# ---- _event_lister -------------------------------------------------------------------
def _event_lister(found: Sequence[Tuple[str, str, int]],
                  file_name: str = '',
                  ) -> List[dict]:
    """
    ---- Summary ----
    Helper function to turn the stored copies of the text events (additions) into one
    entry per addition.

    ---- Inputs ----
    found : Sequence[Tuple[str, str, int]]
        One (name, text, position) per 'Text Event' record, in file order: the name the
        software gives the event ('Event 1'), the text the user typed and the 1-based
        spectrum number (0 in the template copy of an event).
    file_name : str
        File name, for the warnings.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[dict]
        [{'name', 'text', 'datapoint'}] sorted by datapoint. A name stored at several
        different positions gives one entry per position, each with the text stored
        beside it. Names with no stored position are left out with a warning.

    ---- Globals mutated ----
    None. Prints warnings (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    warning_printer
    """

    # ---- 1 Collect the positions stored under each name ------------------------------
    groups = {}
    for name, text, position in found:
        positions = groups.setdefault(name, {})
        # the copies of one addition repeat its position; the first text is kept
        if position and position not in positions:
            positions[position] = text

    # ---- 2 Build the list ------------------------------------------------------------
    events = []
    for name, positions in groups.items():
        if not positions:
            warning_printer(f'the addition {name!r} has no stored position in the '
                            f'file and is left out',
                            file_name,
                            )
            continue
        if len(positions) > 1:
            warning_printer(f'the file stores {len(positions)} additions under the '
                            f'name {name!r} (at spectra {sorted(positions)}); each is '
                            f'kept as an addition of its own',
                            file_name,
                            )
        for position, text in positions.items():
            events.append({'name': name, 'text': text, 'datapoint': int(position)})
    return sorted(events, key=lambda e: e['datapoint'])


# ---- _event_time_adder ---------------------------------------------------------------
def _event_time_adder(events: Sequence[dict],
                      time_min: np.ndarray,
                      file_name: str,
                      is_quiet: bool = False,
                      ) -> List[dict]:
    """
    ---- Summary ----
    Helper function to give every addition its time, and to leave out the additions
    stored outside the recording. The quick look and the full reading both use it, so
    they always give the same additions.

    ---- Inputs ----
    events : Sequence[dict]
        Additions from events_reader, each with 'datapoint' (1-based spectrum number)
        and 'text'.
    time_min : np.ndarray
        Clock of the recording in minutes, shape (n_timepoints,).
    file_name : str
        File name, for the warning.
    is_quiet : bool
        True to leave an addition out without the warning, when the user was already
        told about it by the quick look.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[dict]
        The additions inside the recording, in the order given, each with 'time' (min)
        and 'row_index' (0-based row of the clock) added.

    ---- Globals mutated ----
    None. Prints a warning for each addition left out (side effect).

    ---- Equations ----
    row_index = datapoint - 1; time = time_min[row_index].

    ---- Helpers ----
    warning_printer
    """

    timed = []
    for event in events:
        row = event['datapoint'] - 1
        if not 0 <= row < len(time_min):
            if not is_quiet:
                warning_printer(f"the addition {event['text']!r} is stored at "
                                f"spectrum {event['datapoint']}, but the recording "
                                f'has only {len(time_min)} time points, so it has no '
                                f'time and is left out.',
                                file_name,
                                )
            continue
        timed.append(dict(event, time=float(time_min[row]), row_index=row))
    return timed


# ---- _short_trace_describer ----------------------------------------------------------
def _short_trace_describer(name: str,
                           n_missing: int,
                           n_clock: int,
                           step_s: float,
                           n_expected: int,
                           ) -> str:
    """
    ---- Summary ----
    Helper function to say whether a trace shorter than the clock is worth a warning,
    and in what words.

    ---- Inputs ----
    name : str
        Trace name, e.g. 'VoO2'.
    n_missing : int
        Points of the clock the trace has no value for at the end.
    n_clock : int
        Points of the clock.
    step_s : float
        Time between two points (s).
    n_expected : int
        Points the instrument always leaves empty at the end of this trace (the fall
        edge of VoO2Math for the oxygen rates, else 0).

    ---- Globals read ----
    SHORT_TRACE_FRACTION (module constant).

    ---- Outputs ----
    str
        The warning, without the file name; empty when the trace is short by no more
        than n_expected points or by no more than SHORT_TRACE_FRACTION of the clock.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if n_missing <= n_expected or n_missing <= SHORT_TRACE_FRACTION * n_clock:
        return ''
    return (f'the {name} trace is {n_missing} points shorter than the recording, so '
            f'its last {n_missing * step_s:.0f} s are left empty.'
            )


# ---- _spectrum_time_finder -----------------------------------------------------------
def _spectrum_time_finder(time_s: np.ndarray,
                          n_spectra: int,
                          dataset: str,
                          file_name: str,
                          ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to give the time of every spectrum of one spectrometer.

    ---- Inputs ----
    time_s : np.ndarray
        Clock of the recording in seconds, shape (n_timepoints,).
    n_spectra : int
        Number of spectra of the spectrometer; the file numbers them 1 to n_spectra.
    dataset : str
        Dataset name, for the messages.
    file_name : str
        File name, for the messages.

    ---- Globals read ----
    SEND_FILE_ADVICE (module constant).

    ---- Outputs ----
    np.ndarray
        Times in minutes, shape (n_spectra,). Raises PafError when there are more
        spectra than time points, as the last spectra then have no time.

    ---- Globals mutated ----
    None. Prints a warning when there are fewer spectra than time points (side
    effect).

    ---- Equations ----
    time of spectrum i (min) = time_s[i - 1] / 60, for i = 1 to n_spectra.

    ---- Helpers ----
    warning_printer
    """

    n_times = len(time_s)
    if n_spectra > n_times:
        raise PafError(f'{file_name}: the {dataset} spectrometer has {n_spectra} '
                       f'spectra but the recording has only {n_times} time points, so '
                       f'its last spectra have no time. This file cannot be '
                       f'processed. {SEND_FILE_ADVICE}',
                       )
    if n_spectra < n_times:
        warning_printer(f'{file_name}: the {dataset} spectrometer has {n_spectra} '
                        f'spectra but the recording has {n_times} time points. '
                        f'Spectrum 1 is taken to belong to the first time point and so '
                        f'on, so the last {n_times - n_spectra} time points have no '
                        f'spectrum.',
                        )
    return np.asarray(time_s[:n_spectra], dtype=float) / 60.0


# ---- _trace_title_maker --------------------------------------------------------------
def _trace_title_maker(key: str, unit: str) -> str:
    """
    ---- Summary ----
    Helper function to write the column title of one trace, with the unit the file
    stores for it.

    ---- Inputs ----
    key : str
        Trace name, a key of TRACE_COLUMNS ('CsO2', 'CcO2' or 'VoO2').
    unit : str
        Unit as written in the file; may be empty.

    ---- Globals read ----
    TRACE_COLUMNS, UNIT_IN_TITLE, FALLBACK_UNIT (module constants).

    ---- Outputs ----
    str
        For example 'Measured O2 (µM)'; with FALLBACK_UNIT when the file has no unit,
        and without a unit for the traces not in UNIT_IN_TITLE ('VoO2').

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _unit_cleaner
    """

    if key not in UNIT_IN_TITLE:
        return TRACE_COLUMNS[key]
    return f'{TRACE_COLUMNS[key]} ({_unit_cleaner(unit) or FALLBACK_UNIT})'


# ---- _transmission_converter ---------------------------------------------------------
def _transmission_converter(log_counts: np.ndarray,
                            log_reference: np.ndarray,
                            ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to work out the transmission of a block of spectra from the stored
    logarithms.

    ---- Inputs ----
    log_counts : np.ndarray
        Stored log10 of the counts, shape (n_spectra, n_wavelengths), float64.
    log_reference : np.ndarray
        Stored log10 of the reference spectrum, shape (n_wavelengths,), float64.

    ---- Globals read ----
    LN10 (module constant).

    ---- Outputs ----
    np.ndarray
        Transmission, shape (n_spectra, n_wavelengths), float64. NaN where it is not a
        finite number, as where the reference has zero counts (its logarithm is then
        not finite).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    transmission = 10^(log - log_ref) = exp((log - log_ref) ln 10).

    ---- Helpers ----
    None.
    """

    with np.errstate(over='ignore', invalid='ignore'):
        # this form matches the software's export to 1 ulp
        transmission = np.exp((log_counts - log_reference[None, :]) * LN10)
    transmission[~np.isfinite(transmission)] = np.nan
    return transmission


# ---- _unit_cleaner -------------------------------------------------------------------
def _unit_cleaner(unit: str) -> str:
    """
    ---- Summary ----
    Helper function to write a unit from the file in one way, so that two spellings of
    the same unit compare equal.

    ---- Inputs ----
    unit : str
        Unit as written in the file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The unit without spaces around it and with the Greek letter mu (U+03BC)
        replaced by the micro sign (U+00B5).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return unit.strip().replace('μ', 'µ')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- dataset_namer -------------------------------------------------------------------
def dataset_namer(spectra_name: str) -> str:
    """
    ---- Summary ----
    Main function to turn a spectrometer name in the file into the dataset name used by
    the rest of the program.

    ---- Inputs ----
    spectra_name : str
        Spectrometer name as stored in the file, e.g. 'Cytochromes'.

    ---- Globals read ----
    DATASET_ALIAS (module constant).

    ---- Outputs ----
    str
        Alias from DATASET_ALIAS (e.g. 'Cyt'), otherwise the name with non-word
        characters replaced by underscores.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return DATASET_ALIAS.get(spectra_name, re.sub(r'\W+', '_', spectra_name))


# ---- experiment_paf_loader -----------------------------------------------------------
def experiment_paf_loader(path: Union[str, Path],
                          spectral_datasets: Optional[Sequence[str]] = ('Cyt',),
                          with_intensity: bool = False,
                          ) -> dict:
    """
    ---- Summary ----
    Main function to build the experiment dictionary straight from a .paf file.

    ---- Inputs ----
    path : Union[str, Path]
        Path to the .paf file.
    spectral_datasets : Optional[Sequence[str]]
        Spectrometers to read (None = all, () = none). Spectra are the memory-heavy
        part, so read only what is needed.
    with_intensity : bool
        True to also read the integer counts of each spectrum.

    ---- Globals read ----
    TRACE_COLUMNS, TRACE_UNITS (module constants), schema.TIME_COLUMN.

    ---- Outputs ----
    dict
        Experiment dictionary (DATA_FORMAT.md) with CsO2, CcO2 and VoO2 data frames,
        raw_spectra and metadata (paf_file, events, acquisition, notes). Raises PafError
        if the VoO2 trace is missing.

    ---- Globals mutated ----
    None. Prints warnings for missing traces and for units the figures do not expect
    (side effect). An addition outside the recording is left out without a warning, as
    experiment_summary_reader gives it at the start.

    ---- Equations ----
    None.

    ---- Helpers ----
    _event_time_adder
    _trace_title_maker
    _unit_cleaner
    acquisition_reader
    dataset_name_lister
    events_reader
    missing_trace_describer
    notes_reader
    ocr_trace_checker
    spectra_dataset_reader
    stream_reader
    stream_unit_reader
    warning_printer
    """

    # ---- 1 Open the file -------------------------------------------------------------
    path = Path(path)
    with PafFile(path) as paf:
        # ---- 2 Read the traces -------------------------------------------------------
        paf.ocr_trace_checker()
        time_min = paf.time_s / 60.0
        experiment = {'experiment_name': path.stem, 'raw_spectra': {}}
        for key in TRACE_COLUMNS:
            values = paf.stream_reader(key)
            if values is None:
                warning_printer(f'{paf.missing_trace_describer(key)}. The figures and '
                                f'tables are made without it.',
                                )
                continue
            unit = paf.stream_unit_reader(key)
            if unit and _unit_cleaner(unit) != TRACE_UNITS[key]:
                warning_printer(f'{path.name}: the file gives {key} in {unit}, not in '
                                f'{TRACE_UNITS[key]}. The numbers are kept as they '
                                f'are, but the labels of the figures still say '
                                f'{TRACE_UNITS[key]}.',
                                )
            column = _trace_title_maker(key, unit)
            frame = pd.DataFrame({TIME_COLUMN: time_min, column: values})
            if key == 'VoO2':
                # the software's .txt export omits these rows
                frame = frame.dropna(subset=[column]).reset_index(drop=True)
            experiment[key] = frame

        # ---- 3 Read the spectra ------------------------------------------------------
        wanted = (paf.dataset_name_lister()
                  if spectral_datasets is None
                  else list(spectral_datasets)
                  )
        for name in wanted:
            dataset = paf.spectra_dataset_reader(name,
                                                 with_intensity=with_intensity,
                                                 )
            experiment['raw_spectra'][name] = dataset

        # ---- 4 Read the events -------------------------------------------------------
        events = [{'datapoint': event['datapoint'],
                   'text': event['text'],
                   'label': event['text'],
                   'concentration_uM': None,
                   'time': event['time'],
                   'row_index': event['row_index'],
                   }
                  for event in _event_time_adder(paf.events_reader(),
                                                 time_min,
                                                 path.name,
                                                 is_quiet=True,
                                                 )
                  ]

        # ---- 5 Store the metadata ----------------------------------------------------
        experiment['metadata'] = {'paf_file': path.name,
                                  'events': sorted(events, key=lambda e: e['time']),
                                  'acquisition': paf.acquisition_reader(),
                                  'notes': paf.notes_reader(),
                                  }
    return experiment


# ---- experiment_summary_reader -------------------------------------------------------
def experiment_summary_reader(path: Union[str, Path]) -> dict:
    """
    ---- Summary ----
    Main function to take a quick look at a .paf file without reading its spectra.

    ---- Inputs ----
    path : Union[str, Path]
        Path to the .paf file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {'name' (file stem), 'duration_min', 'frames', 'datasets', 'spectra_shapes'
        ({dataset: [number of spectra, number of wavelengths]}, from the headers),
        'events' (the additions inside the recording, each with 'time' in minutes),
        'traces', 'ocr_check' (ocr_check in DATA_FORMAT.md)}. Raises PafError if the
        VoO2 trace is missing, so a file that cannot be processed is refused before any
        question is asked about it.

    ---- Globals mutated ----
    None. Prints a warning for each addition outside the recording, and one when the
    instrument's OCR does not agree with ours or cannot be checked (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _event_time_adder
    acquisition_reader
    dataset_name_lister
    duration_finder
    events_reader
    frame_counter
    ocr_check_describer
    ocr_checker
    ocr_settings_reader
    ocr_trace_checker
    stream_name_lister
    stream_reader
    warning_printer
    """

    with PafFile(path) as paf:
        # ---- 1 Read the event times --------------------------------------------------
        paf.ocr_trace_checker()
        events = _event_time_adder(paf.events_reader(),
                                   paf.time_s / 60.0,
                                   paf.path.name,
                                   )

        # ---- 2 Check the instrument's OCR against ours -------------------------------
        settings = paf.ocr_settings_reader()
        check = ocr_checker({name: paf.stream_reader(name, is_quiet=True)
                             for name in OCR_TRACES
                             },
                            settings['permeability'] if settings else None,
                            [event['row_index'] for event in events],
                            (float(np.median(np.diff(paf.time_s)))
                             if len(paf.time_s) > 1
                             else float('nan')
                             ),
                            )
        message = ocr_check_describer(check, paf.path.name)
        if message:
            warning_printer(message)

        # ---- 3 Assemble the summary --------------------------------------------------
        return {'name': Path(path).stem,
                'duration_min': paf.duration_finder,
                'frames': paf.frame_counter,
                'datasets': paf.dataset_name_lister(),
                # for the size of the spectra csv files the export question gives
                'spectra_shapes': {acquisition['dataset']: [acquisition['frames'],
                                                            acquisition['wavelengths'],
                                                            ]
                                   for acquisition in paf.acquisition_reader()
                                   },
                'events': events,
                'traces': paf.stream_name_lister(),
                'ocr_check': check,
                }


# ---- record_scanner ------------------------------------------------------------------
def record_scanner(mm: mmap.mmap,
                   file_name: str = '',
                   ) -> Tuple[List[dict], List[Spectra]]:
    """
    ---- Summary ----
    Main function to split the whole file into records and parse the spectra records.

    ---- Inputs ----
    mm : mmap.mmap
        Read-only memory map of the .paf file.
    file_name : str
        File name, for the warnings.

    ---- Globals read ----
    MARK, NOT_A_PAF (module constants).

    ---- Outputs ----
    Tuple[List[dict], List[Spectra]]
        (records, spectra). Each record is {off, end, type, tokens}; spectra holds one
        parsed Spectra per spectrometer. Raises PafError if the file does not start with
        an Espana record.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    spectra_parser
    token_reader
    """

    # ---- 1 Find the record markers ---------------------------------------------------
    markers = [m.start() for m in re.finditer(re.escape(MARK), mm)]
    if not markers or markers[0] > 64:
        raise PafError(NOT_A_PAF)

    # ---- 2 Walk through the records --------------------------------------------------
    recs, spectra, skip_until = [], [], 0
    all_markers = markers
    for i, off in enumerate(all_markers):
        if off < skip_until:
            continue  # marker-like bytes inside a spectra block
        tok = token_reader(mm, off + 40, min(off + 1200, len(mm)))
        typ = tok[0][0] if tok else None
        if typ == 'Spectra: CCD':
            sp = spectra_parser(mm, off, all_markers, file_name)
            spectra.append(sp)
            skip_until = sp.data_end
            recs.append(dict(off=off, end=sp.rec_end, type=typ, tokens=tok[:3]))
            continue
        k = bisect.bisect_right(all_markers, off)
        end = all_markers[k] if k < len(all_markers) else len(mm)
        recs.append(dict(off=off, end=end, type=typ, tokens=tok))

    # ---- 3 Finalise the records ------------------------------------------------------
    # tokens were scanned over up to 1200 bytes: cut to the real record
    for r in recs:
        r['tokens'] = [t for t in r['tokens'] if t[2] <= r['end']]
    return recs, spectra


# ---- rtf_converter -------------------------------------------------------------------
def rtf_converter(rtf: bytes) -> str:
    """
    ---- Summary ----
    Main function to convert the rich text of a PaneNote record to plain text.

    ---- Inputs ----
    rtf : bytes
        RTF bytes (cp1252).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Plain text with one line per paragraph, trailing spaces removed and a final
        newline.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Prepare the decoder -------------------------------------------------------
    s = rtf.decode('cp1252', errors='replace')
    skip_dest = {'fonttbl', 'colortbl', 'stylesheet', 'info', 'generator', 'pict'}
    out, stack, ignore, i = [], [], False, 0

    # ---- 2 Parse the control words and text ------------------------------------------
    while i < len(s):
        c = s[i]
        if c == '{':
            stack.append(ignore)
            i += 1
        elif c == '}':
            ignore = stack.pop() if stack else False
            i += 1
        elif c == '\\':
            i += 1
            if i >= len(s):
                break
            c = s[i]
            if c in '\\{}':
                if not ignore:
                    out.append(c)
                i += 1
            elif c == "'":
                if not ignore:
                    out.append(bytes([int(s[i + 1:i + 3], 16)],
                                     ).decode('cp1252', 'replace'),
                               )
                i += 3
            elif c == '*':
                ignore = True
                i += 1
            else:
                m = re.match(r'([a-zA-Z]+)(-?\d+)? ?', s[i:])
                if not m:
                    i += 1
                    continue
                word, arg = m.group(1), m.group(2)
                i += m.end()
                if word in skip_dest:
                    ignore = True
                elif word in ('par', 'line') and not ignore:
                    out.append('\n')
                elif word == 'tab' and not ignore:
                    out.append('\t')
                elif word == 'u' and arg is not None and not ignore:
                    out.append(chr(int(arg) % 65536))
                    if i < len(s):
                        i += 1  # the fallback character
        else:
            if not ignore and c not in '\r\n':
                out.append(c)
            i += 1

    # ---- 3 Tidy the text -------------------------------------------------------------
    text = ''.join(out)
    return '\n'.join(line.rstrip() for line in text.split('\n')).strip('\n') + '\n'


# ---- spectra_parser ------------------------------------------------------------------
def spectra_parser(mm: mmap.mmap,
                   off: int,
                   markers: List[int],
                   file_name: str = '',
                   ) -> Spectra:
    """
    ---- Summary ----
    Main function to parse one 'Spectra: CCD' record: frame count, wavelength axis,
    log10 data block and acquisition parameters.

    ---- Inputs ----
    mm : mmap.mmap
        Read-only memory map of the .paf file.
    off : int
        Byte offset of the record marker.
    markers : List[int]
        Byte offsets of every record marker in the file, ascending.
    file_name : str
        File name, for the warnings.

    ---- Globals read ----
    COPY_AGAIN_ADVICE, SEND_FILE_ADVICE (module constants). Calls the Spectra class,
    token_reader, u32_reader and warning_printer.

    ---- Outputs ----
    Spectra
        Object with offset, name, nframes, npix, wl_off, wavelengths, data_off,
        data_end, log (nrows x npix float32 view), rec_end, params and checks
        attributes. Raises PafError, in plain words and without the file name, if the
        layout is not recognised, implausible or cut short.

    ---- Globals mutated ----
    None. Prints a warning for unexpected trailing bytes and for a first stored row
    that is not all zeros (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    token_reader
    u32_reader
    warning_printer
    """

    # ---- 1 Read the record header ----------------------------------------------------
    sp = Spectra()
    sp.offset = off
    limit = min(len(mm), off + 4096)
    tok = token_reader(mm, off + 40, limit)
    unknown = ('are stored in a way this program does not know, so the file cannot be '
               f'read. {SEND_FILE_ADVICE}'
               )
    if len(tok) < 3:
        raise PafError(f'some spectra in the file have no name and {unknown}')
    sp.name = tok[2][0]

    # ---- 2 Find the frame index ------------------------------------------------------
    idx_pat = struct.pack('<4I', 1, 2, 3, 4)
    p = mm.find(idx_pat, tok[2][2], limit)
    # the table is found by its first numbers, so spectra that are not numbered from 1
    # without gaps (sparse spectra) cannot be read
    not_numbered = (f"the spectra of '{sp.name}' are not numbered 1, 2, 3 and so on "
                    f'in this file (some may have been skipped during the recording). '
                    f'This program cannot read such a file yet. {SEND_FILE_ADVICE}'
                    )
    if p < 0:
        raise PafError(not_numbered)
    sp.nframes, sp.npix = u32_reader(mm, p - 12), u32_reader(mm, p - 8)
    if not (0 < sp.nframes < 10**7 and 0 < sp.npix < 10**5):
        raise PafError(f"the '{sp.name}' spectra have a size that cannot be right "
                       f'({sp.nframes} spectra of {sp.npix} wavelengths) and {unknown}',
                       )
    index = np.frombuffer(mm, dtype='<u4', count=sp.nframes, offset=p)
    if not np.array_equal(index, np.arange(1, sp.nframes + 1, dtype='<u4')):
        raise PafError(not_numbered)

    # ---- 3 Locate the wavelengths ----------------------------------------------------
    e = p + 4 * sp.nframes
    # wavelength axis: npix strictly increasing float32, a few dozen bytes after the
    # index table
    sp.wl_off = None
    for o in range(e, min(e + 512, len(mm) - 4 * sp.npix)):
        a = struct.unpack_from('<3f', mm, o)
        if not (150 < a[0] < 2500 and a[0] < a[1] < a[2] < a[0] + 5):
            continue
        w = np.frombuffer(mm, dtype='<f4', count=sp.npix, offset=o)
        if 150 < w[-1] < 3000 and np.all(np.diff(w) > 0):
            sp.wl_off = o
            break
    if sp.wl_off is None:
        raise PafError(f"the wavelengths of the '{sp.name}' spectra were not found "
                       f'where this program expects them: the spectra {unknown}',
                       )

    # ---- 4 Map the data block --------------------------------------------------------
    sp.wavelengths = np.frombuffer(mm, dtype='<f4', count=sp.npix, offset=sp.wl_off)
    sp.data_off = sp.wl_off + 4 * sp.npix
    nrows = sp.nframes + 2
    sp.data_end = sp.data_off + 4 * sp.npix * nrows
    if sp.data_end > len(mm):
        raise PafError(f"the file is cut short: it ends before the '{sp.name}' "
                       f'spectra do (it may not have finished copying). '
                       f'{COPY_AGAIN_ADVICE}',
                       )
    sp.log = np.frombuffer(mm,
                           dtype='<f4',
                           count=sp.npix * nrows,
                           offset=sp.data_off,
                           ).reshape(nrows, sp.npix)

    # ---- 5 Find the record end -------------------------------------------------------
    k = bisect.bisect_left(markers, sp.data_end)
    sp.rec_end = markers[k] if k < len(markers) else len(mm)
    if sp.rec_end - sp.data_end > 4096:
        warning_printer(f"the '{sp.name}' spectra are followed by data this program "
                        f'does not know, which is left unread. Compare the spectra '
                        f"with the instrument software's before trusting them.",
                        file_name,
                        )

    # ---- 6 Read the parameters -------------------------------------------------------
    # acquisition parameters (layout verified on one file only); the value at byte 40
    # and the text after the data block are not understood well enough to show
    gap = bytes(mm[e:sp.wl_off])
    sp.params = {}
    if len(gap) == 56:
        sp.params = {'centre_wavelength_nm': round(struct.unpack_from('<f', gap, 24)[0],
                                                   3,
                                                   ),
                     'slit_um': struct.unpack_from('<f', gap, 32)[0],
                     }
    sp.checks = {}
    if np.any(sp.log[0] != 0):
        sp.checks['row0_not_zero'] = True
        warning_printer(f"the first stored row of the '{sp.name}' spectra should be "
                        f'all zeros and is not, so this file may be laid out in a way '
                        f'this program does not know. Compare its spectra with the '
                        f"instrument software's before trusting them.",
                        file_name,
                        )
    return sp


# ---- stream_extractor ----------------------------------------------------------------
def stream_extractor(mm: Union[bytes, mmap.mmap],
                     recs: List[dict],
                     file_name: str = '',
                     ) -> Tuple[List[dict], dict]:
    """
    ---- Summary ----
    Main function to extract every trace (DataItem followed by Measurement record) as a
    float32 array, and to note why each trace it cannot read was skipped.

    ---- Inputs ----
    mm : Union[bytes, mmap.mmap]
        Read-only memory map of the .paf file (or its bytes).
    recs : List[dict]
        Records from record_scanner, in file order.
    file_name : str
        File name, for the warning.

    ---- Globals read ----
    TRACE_COLUMNS (module constant).

    ---- Outputs ----
    Tuple[List[dict], dict]
        (traces, skipped). traces has one {name, n, offset, values, quantity, unit}
        dictionary per trace. skipped is {name: reason} for the traces with disagreeing
        lengths, no values or a record that is too short; the reason is in plain words
        and completes "the trace cannot be read, because ...". A file holds many traces
        the program does not use, so nothing is printed here: the caller reports the
        skipped traces it needs.

    ---- Globals mutated ----
    None. Prints a warning when a trace the program uses ends in an unexpected way
    (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    token_reader
    u32_reader
    warning_printer
    """

    # ---- 1 Prepare the output --------------------------------------------------------
    streams, skipped = [], {}

    # ---- 2 Extract the streams from the record gaps ----------------------------------
    for a, b in zip(recs, recs[1:]):
        if a['type'] != 'DataItem' or b['type'] != 'Measurement':
            continue
        if len(a['tokens']) < 3:
            continue
        name = a['tokens'][2][0]
        n1, n2 = u32_reader(mm, a['end'] - 28), u32_reader(mm, a['end'] - 20)
        if n1 != n2:
            skipped.setdefault(name,
                               f'its length is stored twice in the file and the two '
                               f'numbers disagree ({n1} and {n2})',
                               )
            continue
        if n1 == 0:
            skipped.setdefault(name, 'it holds no values')
            continue
        arr_off = b['end'] - 8 - 4 * n1
        hdr_tokens = token_reader(mm, b['off'] + 40, arr_off)
        if arr_off < b['off'] + 60 or not hdr_tokens:
            skipped.setdefault(name,
                               'its values do not fit in the part of the file that '
                               'holds them',
                               )
            continue
        if (bytes(mm[b['end'] - 8:b['end']]) != b'\x02\x00\x00\x00\x00\x00\x00\x00' and
            (name in TRACE_COLUMNS or name == 'Time')
            ):
            warning_printer(f'the {name} trace ends in a way this program does not '
                            f'expect. Compare it with the export of the instrument '
                            f'software before trusting it.',
                            file_name,
                            )
        vals = np.frombuffer(mm, dtype='<f4', count=n1, offset=arr_off)
        strs = [t[0] for t in hdr_tokens]
        streams.append(dict(name=name,
                            n=n1,
                            offset=arr_off,
                            values=vals,
                            quantity=strs[2] if len(strs) > 2 else '',
                            unit=strs[4] if len(strs) > 4 else '',
                            ),
                       )
    return streams, skipped


# ---- token_reader --------------------------------------------------------------------
def token_reader(buf: Union[bytes, mmap.mmap],
                 start: int,
                 end: int,
                 ) -> List[Tuple[str, int, int]]:
    """
    ---- Summary ----
    Main function to find the length-prefixed UTF-16LE strings inside a byte range of
    the file.

    ---- Inputs ----
    buf : Union[bytes, mmap.mmap]
        Buffer to search.
    start : int
        First byte offset of the range.
    end : int
        Offset one past the last byte of the range.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, int, int]]
        One (text, start offset, end offset) tuple per string found, in file order.
        Empty strings and strings with control characters are skipped.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A string is stored as 02 00 00 00, n (uint32), then n UTF-16LE characters (2n
    bytes).

    ---- Helpers ----
    u32_reader
    """

    # ---- 1 Set up the scan -----------------------------------------------------------
    out = []
    p = start
    pat = b'\x02\x00\x00\x00'

    # ---- 2 Read the tokens -----------------------------------------------------------
    while True:
        p = buf.find(pat, p, end - 8)
        if p < 0:
            break
        n = u32_reader(buf, p + 4)
        # empty strings are skipped (they only produced false hits)
        if 1 <= n <= 4096 and p + 8 + 2 * n <= end:
            try:
                s = bytes(buf[p + 8:p + 8 + 2 * n]).decode('utf-16-le')
            except UnicodeDecodeError:
                s = None
            if s is not None and all(c >= ' ' or c in '\r\n\t' for c in s):
                out.append((s, p, p + 8 + 2 * n))
                p += 8 + 2 * n
                continue
        p += 1
    return out


# ---- u32_reader ----------------------------------------------------------------------
def u32_reader(buf: Union[bytes, mmap.mmap], off: int) -> int:
    """
    ---- Summary ----
    Main function to read one little-endian unsigned 32-bit integer from a buffer.

    ---- Inputs ----
    buf : Union[bytes, mmap.mmap]
        Buffer to read from.
    off : int
        Byte offset of the integer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        The integer value.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return struct.unpack_from('<I', buf, off)[0]


# ---- warning_printer -----------------------------------------------------------------
def warning_printer(msg: str, file_name: str = '') -> None:
    """
    ---- Summary ----
    Main function to show a reader warning, in the terminal and, while a preview is
    drawn, under the plot.

    ---- Inputs ----
    msg : str
        Warning text, without the "WARNING" prefix.
    file_name : str
        File the warning is about, written in front of the text; empty when the text
        already names it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Shows the warning (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    warning_shower
    """

    warning_shower(f"  WARNING: {file_name + ': ' if file_name else ''}{msg}")
