"""
Processing and drawing of one experiment as a preview figure.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import copy
import io
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.attenuation import experiment_attenuation_adder
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.individual_experiment_exporter import experiment_workbook_exporter
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.paf_reader import experiment_paf_loader
from utils_shared.pca_plotter import (pca_example_figure_builder,
                                      pca_figure_builder,
                                      )
from utils_shared.trimming import experiment_trimmer


# ---- CONSTANTS -----------------------------------------------------------------------
PREVIEW_DPI = 200
MAX_CACHED_FILES = 3
# Size and style of the preview while browsing, trimming and checking the analysis: the
# default journal settings, exactly as the figures are saved until they are customised.
BROWSING_ANSWERS = {key: settings.DEFAULT_ANSWERS[key]
                    for key in ('journal', 'columns', 'height', 'size_mode')
                    }
_cache_lock = threading.Lock()
KEY_PREFIX = 'Key: '
PREVIOUS_COLOUR = '#d62728'
TRIM_COLOUR = '0.45'
IGNORE_COLOUR = '#e8a317'


# ---- PreviewSpec ---------------------------------------------------------------------
@dataclass
class PreviewSpec:
    """
    ---- Summary ----
    The settings a preview is drawn with: the answers given so far. Every file is drawn
    with the same spec, so the files can be compared.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    answers: dict
    limits: dict
    fit: Optional[dict]
    details: dict
    show_trim: bool = False
    show_ignored: bool = True
    previous_limits: dict = field(default_factory=dict)


# ---- ViewerSession -------------------------------------------------------------------
@dataclass
class ViewerSession:
    """
    ---- Summary ----
    Everything the experiment browser keeps between steps: the files, the window and the
    recently read experiments.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    summaries: List[dict]
    export_root: Path
    window: Any
    current: int = 0
    cache: OrderedDict = field(default_factory=OrderedDict)


# ---- PREVIEW HELPERS -----------------------------------------------------------------


# ---- _loaded_experiment_getter -------------------------------------------------------
def _loaded_experiment_getter(session: ViewerSession,
                              summary: dict,
                              dataset: Optional[str],
                              ) -> dict:
    """
    ---- Summary ----
    Helper function to give a fresh copy of an experiment read from its file. The file
    is read once and kept for the next previews (the last few files only), and read
    again when the spectra of a dataset are needed that were not read before.

    ---- Inputs ----
    session : ViewerSession
        The browser session holding the cache.
    summary : dict
        File summary (DATA_FORMAT.md).
    dataset : Optional[str]
        Spectral dataset needed for the haem decomposition, or None for no spectra.

    ---- Globals read ----
    MAX_CACHED_FILES (module constant).

    ---- Outputs ----
    dict
        A deep copy of the experiment dictionary, safe to trim and process in place.

    ---- Globals mutated ----
    None. Updates the cache of the session (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_paf_loader
    """

    # ---- 1 Read the file if it is not cached -----------------------------------------
    name = summary['name']
    with _cache_lock:
        entry = session.cache.get(name)
        if entry is None or (dataset
                             and dataset not in entry['experiment']['raw_spectra']):
            experiment = experiment_paf_loader(summary['path'],
                                               spectral_datasets=((dataset,)
                                                                  if dataset
                                                                  else ()
                                                                  ),
                                               )
            entry = {'experiment': experiment}
            session.cache[name] = entry
        session.cache.move_to_end(name)
        while len(session.cache) > MAX_CACHED_FILES:
            session.cache.popitem(last=False)

    # ---- 2 Hand out a copy -----------------------------------------------------------
    return copy.deepcopy(entry['experiment'])


# ---- _overlay_drawer -----------------------------------------------------------------
def _overlay_drawer(fig: Figure,
                    axes: list,
                    regions: list,
                    note: str,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to shade regions of the time axis on every panel of the preview.

    ---- Inputs ----
    fig : Figure
        The preview figure.
    axes : list
        Panels of the preview, top to bottom.
    regions : list
        [(start_min, end_min, kind)] with kind 'trim' (grey hatched) or 'ignore'
        (amber).
    note : str
        Short explanation of the shading, written in the corner of the figure; may be
        empty.

    ---- Globals read ----
    IGNORE_COLOUR, TRIM_COLOUR (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds shaded regions and the note to the figure (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for start, end, kind in regions:
        if end <= start:
            continue
        for ax in axes:
            if kind == 'trim':
                ax.axvspan(start,
                           end,
                           facecolor=TRIM_COLOUR,
                           alpha=0.25,
                           hatch='///',
                           edgecolor=TRIM_COLOUR,
                           linewidth=0,
                           zorder=1,
                           )
            else:
                ax.axvspan(start,
                           end,
                           facecolor=IGNORE_COLOUR,
                           alpha=0.22,
                           linewidth=0,
                           zorder=1,
                           )
    if note:
        mark = fig.text(0.995,
                        0.005,
                        note,
                        ha='right',
                        va='bottom',
                        fontsize=6,
                        color='0.35',
                        alpha=0.9,
                        )
        mark.set_in_layout(False)


# ---- preview_info_builder ------------------------------------------------------------
def preview_info_builder(summary: dict, limits: dict, details: dict) -> dict:
    """
    ---- Summary ----
    Helper function to build the per-file information dictionary that
    experiment_data_processor needs, from the answers given so far.

    ---- Inputs ----
    summary : dict
        File summary (DATA_FORMAT.md).
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes; may
        lack the file.
    details : dict
        {file name: {OD, volume, dilution_factor, events}}; may lack the file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Per-file information (as built in everything_asker).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    name = summary['name']
    own = limits.get(name, {})
    info = {'path': summary['path'],
            'name': name,
            'duration': summary['duration_min'],
            'trim_start': own.get('trim_start'),
            'trim_end': own.get('trim_end'),
            'ignore_start': own.get('ignore_start') or 0.0,
            'ignore_end': own.get('ignore_end') or 0.0,
            }
    info.update(details.get(name, {}))
    return info


# ---- _previous_limit_drawer ----------------------------------------------------------
def _previous_limit_drawer(axes: list,
                           previous: dict,
                           duration: float,
                           ) -> bool:
    """
    ---- Summary ----
    Helper function to draw the limits entered before as dashed lines on every panel
    while new limits are being entered, so the user can see how far to move them.

    ---- Inputs ----
    axes : list
        Panels of the preview.
    previous : dict
        {trim_start, trim_end, ignore_start, ignore_end} of this file in minutes, as
        entered before (the trim times are on the original recording).
    duration : float
        Length of the whole recording in minutes.

    ---- Globals read ----
    PREVIOUS_COLOUR (module constant).

    ---- Outputs ----
    bool
        True when at least one line was drawn.

    ---- Globals mutated ----
    None. Adds lines to the panels (side effect).

    ---- Equations ----
    Trim edges at trim_start and trim_end; ignore edges at trim_start + ignore_start and
    (trim_end or duration) - ignore_end.

    ---- Helpers ----
    None.
    """

    start = previous.get('trim_start') or 0.0
    end = previous.get('trim_end') or duration
    edges = []
    if previous.get('trim_start'):
        edges.append(previous['trim_start'])
    if previous.get('trim_end'):
        edges.append(previous['trim_end'])
    if previous.get('ignore_start'):
        edges.append(start + previous['ignore_start'])
    if previous.get('ignore_end'):
        edges.append(end - previous['ignore_end'])
    for edge in edges:
        for ax in axes:
            ax.axvline(edge,
                       color=PREVIOUS_COLOUR,
                       linestyle='--',
                       linewidth=1.0,
                       zorder=5,
                       )
    return bool(edges)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- all_data_exporter ---------------------------------------------------------------
def all_data_exporter(session: ViewerSession,
                      limits: dict,
                      include_spectra: bool,
                      progress: Optional[Any] = None,
                      ) -> Tuple[Path, List[str]]:
    """
    ---- Summary ----
    Main function to export the data of every file, cut to the trim limits, so it can
    be plotted outside the program: one workbook per file with the oxygen, OCR and
    event sheets, and optionally the spectra as csv files. No haem decomposition, OD
    scaling or averaging is applied; the ignored parts are left in.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, results folder).
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
    include_spectra : bool
        True to write the spectra as csv files too (large and slow).
    progress : Optional[Any]
        Function called with (number done, number of files); may be None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Path, List[str]]
        (folder written, problems). A file that could not be exported is named in the
        problems and left out.

    ---- Globals mutated ----
    None. Reads the files and writes <results>/all_data/<file>/<file>.xlsx (and the
    spectra) (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_workbook_exporter
    preview_info_builder
    """

    folder = session.export_root / 'all_data'
    problems: List[str] = []
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS,
                               decompose=False,
                               normalise_od=False,
                               averaging=False,
                               export_spectra=include_spectra,
                               ))
    for number, summary in enumerate(session.summaries, start=1):
        try:
            with session.window.output_capturer():
                info = preview_info_builder(summary, limits, {})
                processed = experiment_data_processor(info, cfg, None)
                experiment_workbook_exporter(processed['experiment'],
                                             folder,
                                             full=True,
                                             spectra=include_spectra,
                                             )
        except Exception as exc:  # one bad file must not stop the others
            problems.append(f"{summary['name']}: {type(exc).__name__}: {exc}")
        if progress is not None:
            progress(number, len(session.summaries))
    return folder, problems


# ---- pca_example_picture_builder -----------------------------------------------------
def pca_example_picture_builder(examples: dict,
                                names: List[str],
                                types: List[str],
                                ) -> bytes:
    """
    ---- Summary ----
    Main function to draw the best and the worst described spectrum of the principal
    component analysis as a picture for the plot window, in the default journal style
    like the other previews.

    ---- Inputs ----
    examples : dict
        Result of decomposition_example_finder.
    names : List[str]
        Name of each component.
    types : List[str]
        Haem type of each component (component_classifier).

    ---- Globals read ----
    settings.pca_colour_mapper; PREVIEW_DPI, BROWSING_ANSWERS (module constants).

    ---- Outputs ----
    bytes
        The picture (PNG).

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    pca_example_figure_builder
    """

    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS, **BROWSING_ANSWERS))
    plt.rcParams.update(cfg.RC_PARAMS)
    width = cfg.FIGURE_SIZE[0]
    fig = Figure(figsize=(width, width * 1.1), dpi=PREVIEW_DPI)
    pca_example_figure_builder(examples, names, settings.pca_colour_mapper(types), fig)
    fig.set_layout_engine('constrained')
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=PREVIEW_DPI)
    return buffer.getvalue()


# ---- pca_picture_builder -------------------------------------------------------------
def pca_picture_builder(analysis: dict,
                        result: dict,
                        names: List[str],
                        types: List[str],
                        ) -> bytes:
    """
    ---- Summary ----
    Main function to draw the components of the principal component analysis, one
    panel each, as a picture for the plot window, in the default journal style like
    the other previews.

    ---- Inputs ----
    analysis : dict
        Result of component_finder.
    result : dict
        Result of component_builder (the chosen components).
    names : List[str]
        Name of each component.
    types : List[str]
        Haem type of each component (component_classifier).

    ---- Globals read ----
    settings.PCA_TYPE_COLOURS, settings.pca_colour_mapper; PREVIEW_DPI,
    BROWSING_ANSWERS (module constants).

    ---- Outputs ----
    bytes
        The picture (PNG).

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    pca_figure_builder
    """

    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS, **BROWSING_ANSWERS))
    plt.rcParams.update(cfg.RC_PARAMS)
    width = cfg.FIGURE_SIZE[0]
    height = max(width * 0.5, 0.35 * width * result['count'] + 0.6)
    fig = Figure(figsize=(width, height), dpi=PREVIEW_DPI)
    type_colours = {kind: settings.PCA_TYPE_COLOURS[kind][0] for kind in 'abc'}
    pca_figure_builder(analysis,
                       result,
                       names,
                       types,
                       settings.pca_colour_mapper(types),
                       type_colours,
                       fig,
                       )
    fig.set_layout_engine('constrained')
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=PREVIEW_DPI)
    return buffer.getvalue()


# ---- pca_spectra_gatherer ------------------------------------------------------------
def pca_spectra_gatherer(session: ViewerSession,
                         dataset: str,
                         limits: dict,
                         window: Tuple[float, float],
                         progress: Optional[Any] = None,
                         ) -> Tuple[List[dict], List[str]]:
    """
    ---- Summary ----
    Main function to collect, from every file, the spectra the principal component
    analysis uses: the part kept after trimming, without the ignored start and end,
    cut to the spectral window.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache).
    dataset : str
        Spectral dataset holding the haem spectra.
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
    window : Tuple[float, float]
        (start, end) wavelength to keep, in nm. A little outside it is kept as well so
        the analysis can put every file on one grid.
    progress : Optional[Any]
        Function called with (number read, number of files); may be None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[List[dict], List[str]]
        ([{'name', 'wavelengths', 'spectra', 'times' (min)}], problems). A file that
        cannot be read or has no spectra left is left out and named in the problems.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    Spectra kept where ignore_start <= t <= duration - ignore_end after trimming.

    ---- Helpers ----
    _loaded_experiment_getter
    experiment_attenuation_adder
    experiment_trimmer
    preview_info_builder
    """

    sets: List[dict] = []
    problems: List[str] = []
    for number, summary in enumerate(session.summaries, start=1):
        name = summary['name']
        try:
            with session.window.output_capturer():
                info = preview_info_builder(summary, limits, {})
                experiment = _loaded_experiment_getter(session, summary, dataset)
                if info['trim_start'] is not None or info['trim_end'] is not None:
                    experiment_trimmer(experiment,
                                       start_time=info['trim_start'],
                                       end_time=info['trim_end'],
                                       )
                experiment_attenuation_adder(experiment,
                                             mode=settings.TRANSMISSION_MODE,
                                             datasets=(dataset,),
                                             )
            data = experiment['raw_spectra'][dataset]
            times = np.asarray(data['time'], dtype=float)
            duration = float(experiment['CcO2'].iloc[-1, 0])
            keep = ((times >= info['ignore_start'])
                    & (times <= duration - info['ignore_end'])
                    & np.isfinite(times)
                    )
            wavelengths = np.asarray(data['wavelengths'], dtype=float)
            inside = (wavelengths >= window[0] - 2.0) & (wavelengths <= window[1] + 2.0)
            spectra = np.asarray(data['attenuation'], dtype=float)[keep][:, inside]
            if len(spectra) < 2:
                problems.append(f'{name}: fewer than two spectra are left after '
                                f'trimming and ignoring.',
                                )
            else:
                sets.append({'name': name,
                             'wavelengths': wavelengths[inside],
                             'spectra': spectra,
                             'times': times[keep],
                             })
        except Exception as exc:  # one unreadable file must not stop the others
            problems.append(f'{name}: {type(exc).__name__}: {exc}')
        if progress is not None:
            progress(number, len(session.summaries))
    return sets, problems


# ---- preview_drawer ------------------------------------------------------------------
def preview_drawer(session: ViewerSession,
                   answers: dict,
                   limits: dict,
                   fit: Optional[dict],
                   details: dict,
                   show_trim: bool = False,
                   show_ignored: bool = True,
                   name: Optional[str] = None,
                   previous_limits: Optional[dict] = None,
                   ) -> bool:
    """
    ---- Summary ----
    Main function to show the answers given so far in the window. A window with its own
    controls (the experiment browser window) is given the settings and draws every file
    the user looks at with them; otherwise the current file is drawn and saved as a
    picture. Problems are reported, never raised, so the questions carry on.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache, current file).
    answers : dict
        Answers so far; missing keys come from config.DEFAULT_ANSWERS.
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
    fit : Optional[dict]
        Fit dictionary from fit_importer, or None.
    details : dict
        {file name: {OD, volume, dilution_factor, events}}.
    show_trim : bool
        True to draw the whole recording and shade the part that would be trimmed, so
        the trim limits can be judged. False draws the trimmed data.
    show_ignored : bool
        True to shade the ignored start and end in amber.
    name : Optional[str]
        File to show; None keeps the file being looked at.
    previous_limits : Optional[dict]
        Limits entered before, drawn as dashed lines while new ones are entered (only
        with show_trim); None draws none.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the preview was drawn (or handed to the window), False when it could
        not be.

    ---- Globals mutated ----
    None. Draws in the window or writes the preview picture (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    preview_figure_builder
    """

    # ---- 1 Collect the settings ------------------------------------------------------
    spec = PreviewSpec(answers=dict(answers),
                       limits=copy.deepcopy(limits),
                       fit=fit,
                       details=copy.deepcopy(details),
                       show_trim=show_trim,
                       show_ignored=show_ignored,
                       previous_limits=copy.deepcopy(previous_limits or {}),
                       )

    # ---- 2 Hand them to the window or draw one picture -------------------------------
    if session.window.is_interactive:
        session.window.spec_publisher(spec, name)
        return True
    figure, notes = preview_figure_builder(
        session,
        spec,
        name or session.summaries[session.current]['name'],
    )
    if notes:
        print('\n'.join(f'  {line}' for line in notes.splitlines()))
    if figure is None:
        return False
    session.window.figure_shower(figure)
    return True


# ---- preview_figure_builder ----------------------------------------------------------
def preview_figure_builder(session: ViewerSession,
                           spec: PreviewSpec,
                           name: str,
                           ) -> Tuple[Optional[Figure], str]:
    """
    ---- Summary ----
    Main function to process one file with the answers of a spec and draw it in a new
    figure. Problems are reported, never raised.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache).
    spec : PreviewSpec
        The settings to draw with.
    name : str
        Name of the file to draw.

    ---- Globals read ----
    settings.Config; PREVIEW_DPI (module constant).

    ---- Outputs ----
    Tuple[Optional[Figure], str]
        (figure, notes). The figure is None when the preview could not be drawn, and
        the notes then say why. Otherwise the notes are the warnings of the processing
        (a skipped step, a missing OD), one per line, and may be empty. A line starting
        with KEY_PREFIX explains the shading and belongs by the controls.

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style (side effect). Nothing is
    printed; the caller decides where the notes go.

    ---- Equations ----
    None.

    ---- Helpers ----
    _loaded_experiment_getter
    _overlay_drawer
    _previous_limit_drawer
    experiment_data_processor
    experiment_plotter
    preview_info_builder
    """

    # ---- 1 Set up the file and the settings ------------------------------------------
    summary = next(s for s in session.summaries if s['name'] == name)
    own = spec.limits.get(name, {})
    info = preview_info_builder(summary,
                                {name: {} if spec.show_trim else own},
                                spec.details,
                                )
    preview_answers = dict(settings.DEFAULT_ANSWERS,
                           **dict(spec.answers, export_spectra=False),
                           )
    cfg = settings.Config(preview_answers)
    plt.rcParams.update(cfg.RC_PARAMS)

    # ---- 2 Process the data and draw the figure --------------------------------------
    plot_extras = {'SHOW_SKIPPED_WINDOWS': True}
    needs_dataset = preview_answers['decompose'] and spec.fit is not None
    fig = Figure(dpi=PREVIEW_DPI)
    try:
        with session.window.output_capturer() as buffer:
            experiment = _loaded_experiment_getter(session,
                                                   summary,
                                                   preview_answers[
                                                       'decomposition_dataset']
                                                   if needs_dataset
                                                   else None,
                                                   )
            processed = experiment_data_processor(info, cfg, spec.fit, experiment)
            experiment = processed['experiment']
            haem_panels = preview_answers['plot_haems'] and 'haem_conc' in experiment
            plot_config = cfg.plot_config_builder(processed['vo2_source'],
                                                  processed['haem_source']
                                                  if haem_panels
                                                  else None,
                                                  info['ignore_start'],
                                                  info['ignore_end'],
                                                  )
            plot_config.update({'SAVE_FIGURES': False,
                                'SHOW_INDIVIDUAL_FIGURES': False,
                                'FIGURE_DPI': PREVIEW_DPI,
                                **plot_extras,
                                })
            _, axes = experiment_plotter(experiment,
                                         plot_config,
                                         session.export_root,
                                         fig=fig,
                                         )
    except Exception as exc:  # a preview problem must never stop the questions
        return None, f'Preview not drawn for {name}: {type(exc).__name__}: {exc}'
    notes = '\n'.join(line.strip()
                      for line in buffer.getvalue().splitlines()
                      if any(word in line for word in ('Warning', 'skipped', 'Not '))
                      )

    # ---- 3 Shade the trimmed and ignored parts ---------------------------------------
    regions = []
    duration = float(experiment['CcO2'].iloc[-1, 0])
    start = (own.get('trim_start') or 0.0) if spec.show_trim else 0.0
    end = ((own.get('trim_end') or summary['duration_min'])
           if spec.show_trim
           else duration
           )
    if spec.show_trim:
        regions += [(0.0, start, 'trim'), (end, summary['duration_min'], 'trim')]
    if spec.show_ignored:
        regions += [(start, start + (own.get('ignore_start') or 0.0), 'ignore'),
                    (end - (own.get('ignore_end') or 0.0), end, 'ignore'),
                    ]
    note = ''
    if spec.show_trim:
        note = 'grey hatched = trimmed away, amber = ignored in calculations'
    elif spec.show_ignored and any(r[2] == 'ignore' and r[1] > r[0] for r in regions):
        note = 'amber = ignored in calculations'
    _overlay_drawer(fig, axes, regions, '')
    if spec.show_trim and spec.previous_limits.get(name):
        if _previous_limit_drawer(axes,
                                  spec.previous_limits[name],
                                  summary['duration_min'],
                                  ):
            note = ((f'{note}; ' if note else '')
                    + 'red dashed = the limits you entered before')
    if note:  # shown above the file selector, not inside the picture
        notes = '\n'.join(line for line in (notes, f'{KEY_PREFIX}{note}') if line)
    return fig, notes


# ---- skipped_windows_finder ----------------------------------------------------------
def skipped_windows_finder(session: ViewerSession,
                           answers: dict,
                           limits: dict,
                           details: dict,
                           ) -> Dict[str, Dict[str, dict]]:
    """
    ---- Summary ----
    Main function to find, for every file, the averaging windows that do not fit
    between the additions (or after the last one) with the current window and gap.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache).
    answers : dict
        Answers so far, with averaging turned on and the window and gap chosen.
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}}.
    details : dict
        {file name: {OD, volume, dilution_factor, events}}.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Dict[str, dict]]
        {file name: {window name: {start_time, end_time, reason}}}; files with nothing
        skipped are left out. A file that cannot be read is left out as well.

    ---- Globals mutated ----
    None. Reads the files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _loaded_experiment_getter
    experiment_data_processor
    preview_info_builder
    """

    found: Dict[str, Dict[str, dict]] = {}
    check = dict(settings.DEFAULT_ANSWERS,
                 **dict(answers, decompose=False, normalise_od=False, averaging=True),
                 )
    cfg = settings.Config(check)
    for summary in session.summaries:
        try:
            with session.window.output_capturer():
                info = preview_info_builder(summary, limits, details)
                experiment = _loaded_experiment_getter(session, summary, None)
                processed = experiment_data_processor(info, cfg, None, experiment)
        except Exception:  # a file that cannot be checked is left out
            continue
        skipped = processed['experiment'].get('averages', {}).get('skipped')
        if skipped:
            found[summary['name']] = skipped
    return found
