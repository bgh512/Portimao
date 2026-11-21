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
from typing import Any, Callable, Dict, List, Optional, Tuple

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
from utils_shared.user_notices import problem_teller


# ---- CONSTANTS -----------------------------------------------------------------------
# Size and style of the preview while browsing, trimming and checking the analysis: the
# default journal settings, exactly as the figures are saved until they are customised.
BROWSING_ANSWERS = {key: settings.DEFAULT_ANSWERS[key]
                    for key in ('journal', 'columns', 'height', 'size_mode')
                    }
_cache_lock = threading.Lock()
KEY_PREFIX = 'Key: '
IGNORE_COLOUR = '#e8a317'  # also the ignored parts in the trimming step (viewer_edges)


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


# ---- TimeAxis ------------------------------------------------------------------------
@dataclass
class TimeAxis:
    """
    ---- Summary ----
    Where the time axis shared by the panels sits in a preview picture, and the times at
    its two ends, so a point of the picture can be turned into a time.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    left: float
    right: float
    bottom: float
    top: float
    start_min: float
    end_min: float


# ---- ViewerSession -------------------------------------------------------------------
@dataclass
class ViewerSession:
    """
    ---- Summary ----
    Everything the experiment browser keeps between steps: the files, the window, the
    recently read experiments, the fit in use and how to redraw the step being asked.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    summaries: List[dict]
    export_root: Path
    window: Any
    current: int = 0
    cache: OrderedDict = field(default_factory=OrderedDict)
    fit: Optional[dict] = None
    redraw: Optional[Callable[[], bool]] = None
    is_figure: bool = False


# ---- PREVIEW HELPERS -----------------------------------------------------------------


# ---- _loaded_experiment_getter -------------------------------------------------------
def _loaded_experiment_getter(session: ViewerSession,
                              summary: dict,
                              dataset: Optional[str],
                              ) -> dict:
    """
    ---- Summary ----
    Helper function to give a fresh copy of an experiment read from its file. The file
    is read once and kept for the next previews while it is one of the files nearest
    the one shown (kept_file_lister), and read again when the spectra of a dataset are
    needed that were not read before.

    ---- Inputs ----
    session : ViewerSession
        The browser session holding the cache.
    summary : dict
        File summary (DATA_FORMAT.md).
    dataset : Optional[str]
        Spectral dataset needed for the haem decomposition, or None for no spectra.

    ---- Globals read ----
    settings.WINDOW_KEPT_FILES.

    ---- Outputs ----
    dict
        A deep copy of the experiment dictionary, safe to trim and process in place.

    ---- Globals mutated ----
    None. Updates the cache of the session (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_paf_loader
    kept_file_lister
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

        # ---- 2 Keep only the files nearest the one shown -----------------------------
        # A file read for every file at once (the component finder) is let go at once,
        # so the files around the one shown are not read again.
        if len(session.cache) > settings.WINDOW_KEPT_FILES:
            names = [s['name'] for s in session.summaries]
            kept = {names[i]
                    for i in kept_file_lister(session.current,
                                              len(names),
                                              settings.WINDOW_KEPT_FILES,
                                              )
                    }
            for cached in [n for n in session.cache if n not in kept]:
                del session.cache[cached]

    # ---- 3 Hand out a copy -----------------------------------------------------------
    return copy.deepcopy(entry['experiment'])


# ---- _overlay_drawer -----------------------------------------------------------------
def _overlay_drawer(axes: list, regions: List[Tuple[float, float]]) -> None:
    """
    ---- Summary ----
    Helper function to shade the ignored parts of the time axis in amber on every panel
    of the preview.

    ---- Inputs ----
    axes : list
        Panels of the preview, top to bottom.
    regions : List[Tuple[float, float]]
        [(start_min, end_min)] of the ignored parts; an empty one is left out.

    ---- Globals read ----
    IGNORE_COLOUR (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds shaded regions to the figure (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for start, end in regions:
        if end <= start:
            continue
        for ax in axes:
            ax.axvspan(start,
                       end,
                       facecolor=IGNORE_COLOUR,
                       alpha=0.22,
                       linewidth=0,
                       zorder=1,
                       )


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
    problem_teller
    """

    folder = session.export_root / 'all_data'
    problems: List[str] = []
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS,
                               decompose=False,
                               normalise_od=False,
                               averaging=False,
                               export_spectra=include_spectra,
                               ),
                          )
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
            problems.append(problem_teller(summary['name'], exc))
        if progress is not None:
            progress(number, len(session.summaries))
    return folder, problems


# ---- kept_file_lister ----------------------------------------------------------------
def kept_file_lister(current: int, total: int, count: int) -> List[int]:
    """
    ---- Summary ----
    Main function to list the files the window keeps read and draws after each answer:
    the file shown, then the nearest ones around the list (the arrows go round it), the
    next one before the previous one at the same distance.

    ---- Inputs ----
    current : int
        Position of the file shown in the list of files.
    total : int
        Number of files.
    count : int
        How many files to list (settings.WINDOW_KEPT_FILES); at least 1.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[int]
        Positions of the files, nearest first, at most count and at most total.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Distance of file i = min((i - current) mod total, (current - i) mod total).

    ---- Helpers ----
    None.
    """

    if total <= 0:
        return []
    start = current % total
    order = sorted(range(total),
                   key=lambda i: (min((i - start) % total, (start - i) % total),
                                  (i - start) % total,
                                  ),
                   )
    return order[:max(count, 1)]


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
    settings.pca_colour_mapper, settings.PREVIEW_DPI; BROWSING_ANSWERS (module
    constant).

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
    fig = Figure(figsize=(width, width * 1.1), dpi=settings.PREVIEW_DPI)
    pca_example_figure_builder(examples, names, settings.pca_colour_mapper(types), fig)
    fig.set_layout_engine('constrained')
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=settings.PREVIEW_DPI)
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
    settings.PCA_TYPE_COLOURS, settings.pca_colour_mapper, settings.PREVIEW_DPI;
    BROWSING_ANSWERS (module constant).

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
    fig = Figure(figsize=(width, height), dpi=settings.PREVIEW_DPI)
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
    fig.savefig(buffer, format='png', dpi=settings.PREVIEW_DPI)
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
    problem_teller
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
                experiment_attenuation_adder(experiment, datasets=(dataset,))
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
                             },
                            )
        except Exception as exc:  # one unreadable file must not stop the others
            problems.append(problem_teller(name, exc))
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
                   ) -> bool:
    """
    ---- Summary ----
    Main function to show the answers given so far in the window: the window is given
    the settings and draws every file the user looks at with them. Problems are
    reported, never raised, so the questions carry on.

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
        True to draw the whole recording without shading, for the trimming step, where
        the window draws the edges and the shading over it (viewer_edges). False draws
        the trimmed data.
    show_ignored : bool
        True to shade the ignored start and end in amber (not with show_trim).
    name : Optional[str]
        File to show; None keeps the file being looked at.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True: the settings were handed to the window, which draws them.

    ---- Globals mutated ----
    None. Draws in the window (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Collect the settings ------------------------------------------------------
    spec = PreviewSpec(answers=dict(answers),
                       limits=copy.deepcopy(limits),
                       fit=fit,
                       details=copy.deepcopy(details),
                       show_trim=show_trim,
                       show_ignored=show_ignored,
                       )

    # ---- 2 Hand them to the window ---------------------------------------------------
    session.window.spec_publisher(spec, name)
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
    settings.Config, settings.PREVIEW_DPI.

    ---- Outputs ----
    Tuple[Optional[Figure], str]
        (figure, notes). The figure is None when the preview could not be drawn, and
        the notes then say why in one sentence. Otherwise the notes are the warnings
        shown while it was drawn (a skipped step, a missing OD), one per line, and may
        be empty. A line starting with KEY_PREFIX explains the shading and belongs by
        the controls.

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style; the details of a problem
    go to the log (side effects). Nothing is printed; the caller decides where the
    notes go.

    ---- Equations ----
    None.

    ---- Helpers ----
    _loaded_experiment_getter
    _overlay_drawer
    experiment_data_processor
    experiment_plotter
    preview_info_builder
    problem_teller
    time_title_chooser
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
    fig = Figure(dpi=settings.PREVIEW_DPI)
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
                                'FIGURE_DPI': settings.PREVIEW_DPI,
                                'TIME_AXIS_LABEL': time_title_chooser(spec.show_trim,
                                                                      own.get(
                                                                          'trim_start',
                                                                          ),
                                                                      ),
                                **plot_extras,
                                },
                               )
            _, axes = experiment_plotter(experiment,
                                         plot_config,
                                         session.export_root,
                                         fig=fig,
                                         )
    except Exception as exc:  # a preview problem must never stop the questions
        return None, problem_teller(f'Preview not drawn for {name}', exc)
    notes = '\n'.join(buffer.warnings)

    # ---- 3 Shade the ignored parts ---------------------------------------------------
    # In the trimming step the window shades the whole recording itself, so the shading
    # can follow the edges dragged without the figure being drawn again.
    regions = []
    if spec.show_ignored and not spec.show_trim:
        duration = float(experiment['CcO2'].iloc[-1, 0])
        regions = [(0.0, own.get('ignore_start') or 0.0),
                   (duration - (own.get('ignore_end') or 0.0), duration),
                   ]
    _overlay_drawer(axes, regions)
    if any(end > start for start, end in regions):  # shown above the file selector
        notes = '\n'.join(line
                          for line in (notes,
                                       f'{KEY_PREFIX}amber = ignored in calculations',
                                       )
                          if line
                          )
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


# ---- time_axis_finder ----------------------------------------------------------------
def time_axis_finder(fig: Figure) -> Optional[TimeAxis]:
    """
    ---- Summary ----
    Main function to find where the time axis of a drawn preview sits in its picture:
    the panels that share the x axis of the first panel. Call it once the figure has
    its final layout (after it is saved).

    ---- Inputs ----
    fig : Figure
        The drawn preview figure.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[TimeAxis]
        The place and the range of the time axis, or None when the figure has no panel
        or its axis has no length.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    left, right, bottom, top = the outer edges of the panels, as fractions of the
    figure measured from its bottom left corner.

    ---- Helpers ----
    None.
    """

    if not fig.axes:
        return None
    first = fig.axes[0]
    shared = first.get_shared_x_axes()
    boxes = [ax.get_position()
             for ax in fig.axes
             if ax is first or shared.joined(first, ax)
             ]
    start, end = (float(value) for value in first.get_xlim())
    left = min(box.x0 for box in boxes)
    right = max(box.x1 for box in boxes)
    if end == start or right <= left:
        return None
    return TimeAxis(left=left,
                    right=right,
                    bottom=min(box.y0 for box in boxes),
                    top=max(box.y1 for box in boxes),
                    start_min=start,
                    end_min=end,
                    )


# ---- time_title_chooser --------------------------------------------------------------
def time_title_chooser(show_trim: bool, trim_start_min: Optional[float]) -> str:
    """
    ---- Summary ----
    Main function to choose the time axis title of a file's preview, so the user knows
    which time it shows: while trimming the whole recording is drawn, and afterwards 0
    is where the kept part starts.

    ---- Inputs ----
    show_trim : bool
        True while trimming (the whole recording is drawn).
    trim_start_min : Optional[float]
        Where the kept part of the file starts in the recording, in minutes; None or 0
        when its start is not trimmed.

    ---- Globals read ----
    settings.PREVIEW_TIME_TITLES.

    ---- Outputs ----
    str
        "Time from the trimmed start" for a file trimmed at its start, once trimming is
        over; otherwise "Time in the recording" (the two times are then the same).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    is_shifted = not show_trim and (trim_start_min or 0.0) > 0.0
    return settings.PREVIEW_TIME_TITLES['trimmed' if is_shifted else 'recording']
