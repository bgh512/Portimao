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
from utils_shared.helpers import name_simplifier
from utils_shared.individual_experiment_exporter import (experiment_workbook_exporter,
                                                         FULL_FOLDER,
                                                         )
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.paf_reader import experiment_paf_loader
from utils_shared.pca_plotter import (pca_example_figure_builder,
                                      pca_figure_builder,
                                      )
from utils_shared.schema import (HAEM_KEYS,
                                 measurement_column_finder,
                                 time_getter,
                                 value_getter,
                                 )
from utils_shared.spectral_decomposer import (decomposition_gap_calculator,
                                              haem_name_plainer,
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
# the dashes of the kept decomposition's haem traces: points of line, points of gap
KEPT_DASHES = (4, 2)
# how solid they are drawn (1 is solid): paler than the haems in use, so the two can be
# told apart where a noisy trace hides its dashes
KEPT_ALPHA = 0.55
# the share of a kept trace's range left free above and below it when a haem panel is
# widened to hold it, as the panels leave around the haems in use
KEPT_MARGIN = 0.05
IGNORE_COLOUR = '#e8a317'  # also the ignored parts in the trimming step (viewer_edges)
# what the export of the import writes: the workbooks only, with the trimmed spectra, or
# with the spectra of the whole recordings as well
SPECTRA_BY_EXPORT = {'summary': (False, False),
                     'trimmed': (True, False),
                     'all': (True, True),
                     }


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
    kept: Optional[dict] = None
    regions: dict = field(default_factory=dict)


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
    kept: Optional[dict] = None
    regions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    limits: Dict[str, dict] = field(default_factory=dict)
    has_od: bool = False
    redraw: Optional[Callable[[], bool]] = None
    is_figure: bool = False
    export_choice: Optional[str] = None
    export_limits: Dict[str, dict] = field(default_factory=dict)
    full_exports: Dict[str, List[Path]] = field(default_factory=dict)
    exported: List[Path] = field(default_factory=list)


# ---- PREVIEW HELPERS -----------------------------------------------------------------


# ---- _file_exporter ------------------------------------------------------------------
def _file_exporter(session: ViewerSession,
                   summary: dict,
                   limits: dict,
                   details: dict,
                   choice: str,
                   keep_full: bool,
                   ) -> None:
    """
    ---- Summary ----
    Helper function to export the imported data of one file, read once: for a trimmed
    file the whole recording into the full folder of its results folder, then the data
    kept by the trimming (all of it for a file not trimmed) into its results folder,
    with the OD values and labels entered. A file that is no longer trimmed loses the
    whole recording written for it earlier in this run, as it has nothing called full.

    ---- Inputs ----
    session : ViewerSession
        The browser session (results folder, the whole recordings written so far).
    summary : dict
        File summary (DATA_FORMAT.md).
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
    details : dict
        {file name: {OD, volume, dilution_factor, events}}; may lack the file.
    choice : str
        A key of SPECTRA_BY_EXPORT: 'summary', 'trimmed' or 'all'.
    keep_full : bool
        True leaves a whole recording already written in this run as it is (the edges
        changed, and the whole recording does not depend on them).

    ---- Globals read ----
    FULL_FOLDER, SPECTRA_BY_EXPORT (module constants); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads the file, writes or removes the exported files and records the whole
    recordings written in session.full_exports (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_trimmer
    experiment_workbook_exporter
    preview_info_builder
    """

    # ---- 1 Read the whole recording, with the OD values and labels -------------------
    name = summary['name']
    own = limits.get(name) or {}
    start, end = own.get('trim_start'), own.get('trim_end')
    is_trimmed = start is not None or end is not None
    with_spectra, with_full_spectra = SPECTRA_BY_EXPORT[choice]
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS,
                               decompose=False,
                               normalise_od=False,
                               averaging=False,
                               export_spectra=with_spectra,
                               ),
                          )
    experiment = experiment_data_processor(preview_info_builder(summary, {}, details),
                                           cfg,
                                           None,
                                           )['experiment']

    # ---- 2 Write the whole recording, or take away one no longer wanted --------------
    earlier = session.full_exports.get(name)
    if is_trimmed and not (keep_full and earlier):
        session.full_exports[name] = experiment_workbook_exporter(
            experiment,
            session.export_root,
            spectra=with_full_spectra,
            subfolder=FULL_FOLDER,
            )
    elif not is_trimmed and earlier:
        for path in earlier:
            path.unlink(missing_ok=True)
        try:
            earlier[0].parent.rmdir()
        except OSError:
            pass  # something else is in it, which is left alone
        del session.full_exports[name]

    # ---- 3 Trim, then write the data used --------------------------------------------
    if is_trimmed:
        experiment_trimmer(experiment, start_time=start, end_time=end)
    experiment['metadata'].update(
        {'ignore_first_minutes': own.get('ignore_start') or 0.0,
         'ignore_last_minutes': own.get('ignore_end') or 0.0,
         },
        )
    experiment_workbook_exporter(experiment, session.export_root, spectra=with_spectra)


# ---- _kept_haems_drawer --------------------------------------------------------------
def _kept_haems_drawer(session: ViewerSession,
                       summary: dict,
                       info: dict,
                       answers: dict,
                       kept: dict,
                       haem_source: Optional[str],
                       experiment: dict,
                       axes: list,
                       plot_config: dict,
                       ) -> str:
    """
    ---- Summary ----
    Helper function to work one file out again with the kept decomposition (its fit and
    background, everything else as in use), draw its haem traces dashed over the haems
    in use in the same colours, widening a panel a kept trace would leave, and say how
    far apart the two are. Its own warnings are left out, as they repeat those of the
    decomposition in use.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache).
    summary : dict
        File summary (DATA_FORMAT.md).
    info : dict
        Per-file information the decomposition in use was worked out with.
    answers : dict
        Answers the decomposition in use was worked out with.
    kept : dict
        The kept decomposition (DATA_FORMAT.md, kept decomposition).
    haem_source : Optional[str]
        Key of HAEM_KEYS the haem panels show.
    experiment : dict
        The experiment worked out with the decomposition in use.
    axes : list
        Panels of the preview, top to bottom; a haem panel has haem_names.
    plot_config : dict
        Plot settings of the preview (HAEM_COLOURS, LINE_WIDTH, HAEM_Y_MIN,
        HAEM_Y_MAX).

    ---- Globals read ----
    settings.Config, HAEM_KEYS, KEY_PREFIX, KEPT_ALPHA, KEPT_DASHES, KEPT_MARGIN.

    ---- Outputs ----
    str
        The notes: a KEY_PREFIX line for the dashed lines and a line with the largest
        and the average gap of each haem in both; or one sentence saying why the kept
        decomposition is not shown on this file.

    ---- Globals mutated ----
    None. Draws on the haem panels; the details of a problem go to the log (side
    effects).

    ---- Equations ----
    The gaps: decomposition_gap_calculator. A widened panel reaches from
    min - pad to max + pad of the kept trace outside the ignored parts, with
    pad = (max - min) x KEPT_MARGIN, and never shrinks.

    ---- Helpers ----
    _loaded_experiment_getter
    decomposition_gap_calculator
    experiment_data_processor
    haem_name_plainer
    name_simplifier
    problem_teller
    """

    # ---- 1 Work the file out with the kept decomposition -----------------------------
    key = HAEM_KEYS.get(haem_source or '')
    kept_answers = dict(answers, **kept['answers'], decompose=True, averaging=False)
    name = summary['name']
    try:
        with session.window.output_capturer():
            fresh = _loaded_experiment_getter(session,
                                              summary,
                                              kept_answers['decomposition_dataset'],
                                              )
            kept_experiment = experiment_data_processor(info,
                                                        settings.Config(kept_answers),
                                                        kept['fit'],
                                                        fresh,
                                                        )['experiment']
    except Exception as exc:  # the comparison must never stop the preview
        return problem_teller(f'The kept decomposition is not shown for {name}', exc)
    new_table, kept_table = experiment.get(key), kept_experiment.get(key)
    if new_table is None or kept_table is None:
        return ('The kept decomposition is not shown on this file: its haems could not '
                'be worked out.'
                )

    # ---- 2 Draw its traces dashed over the haems in use ------------------------------
    colours = {name_simplifier(k): v for k, v in plot_config['HAEM_COLOURS'].items()}
    kept_columns = {name_simplifier(column): column
                    for column in measurement_column_finder(kept_table)
                    }
    times = time_getter(kept_table)
    # The panels were scaled to the haems in use, outside the ignored parts; they are
    # widened the same way where a kept trace would leave them, unless the scale is set.
    is_scaled = (plot_config['HAEM_Y_MIN'] is None and
                 plot_config['HAEM_Y_MAX'] is None and
                 np.isfinite(times).any()
                 )
    if is_scaled:
        is_used = ((times >= np.nanmin(times) + (info['ignore_start'] or 0.0)) &
                   (times <= np.nanmax(times) - (info['ignore_end'] or 0.0))
                   )
    for ax in axes:
        for haem in getattr(ax, 'haem_names', []):
            if haem not in kept_columns:
                continue
            values = value_getter(kept_table, kept_columns[haem])
            ax.plot(times,
                    values,
                    color=colours.get(haem),
                    linewidth=plot_config['LINE_WIDTH'],
                    dashes=KEPT_DASHES,
                    alpha=KEPT_ALPHA,
                    zorder=2,
                    )
            used = values[is_used & np.isfinite(values)] if is_scaled else values[:0]
            if used.size:
                pad = (used.max() - used.min()) * KEPT_MARGIN
                low, high = ax.get_ylim()
                ax.set_ylim(min(low, used.min() - pad), max(high, used.max() + pad))

    # ---- 3 Say how far apart they are ------------------------------------------------
    gaps = decomposition_gap_calculator(new_table, kept_table)
    if not gaps:
        return f'{KEY_PREFIX}dashed and paler = kept decomposition (no haem in common)'
    words = ', '.join(f'{haem_name_plainer(haem)} {largest:.3g} / {average:.3g}'
                      for haem, (largest, average) in gaps.items()
                      )
    return '\n'.join((f'{KEY_PREFIX}dashed and paler = kept decomposition',
                      f'Gap to the kept decomposition, largest / average, in the units '
                      f'of the haem panels: {words}',
                      ),
                     )


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
def preview_info_builder(summary: dict,
                         limits: dict,
                         details: dict,
                         regions: Optional[dict] = None,
                         ) -> dict:
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
    regions : Optional[dict]
        {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
        times on the original recording (min); None, or a file missing, for none.

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
            'regions': (regions or {}).get(name),
            }
    info.update(details.get(name, {}))
    return info


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- import_data_exporter ------------------------------------------------------------
def import_data_exporter(session: ViewerSession,
                         limits: dict,
                         details: dict,
                         choice: str,
                         names: Optional[List[str]] = None,
                         keep_full: bool = False,
                         progress: Optional[Callable[[int, int], None]] = None,
                         ) -> List[str]:
    """
    ---- Summary ----
    Main function to export the imported data of every file (or of the files named), so
    it can be plotted outside the program: in each file's results folder the workbook
    of the data kept by the trimming (the oxygen, OCR, events with their labels, and the
    OD values and edges), and for a trimmed file the whole recording in its full folder;
    the spectra as csv files beside them if chosen. No haem decomposition, OD scaling
    or averaging is applied; the ignored parts are left in.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, results folder, the whole recordings written).
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
    details : dict
        {file name: {OD, volume, dilution_factor, events}} (details_stage_runner).
    choice : str
        A key of SPECTRA_BY_EXPORT: 'summary' (the workbooks only), 'trimmed' (and the
        trimmed spectra) or 'all' (and the spectra of the whole recordings too).
    names : Optional[List[str]]
        Files to export; None for every file.
    keep_full : bool
        True leaves the whole recordings already written in this run as they are.
    progress : Optional[Callable[[int, int], None]]
        Function called with (number done, number of files); may be None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The problems: a file that could not be exported is named in them and left out.

    ---- Globals mutated ----
    None. Reads the files, writes <results>/<file>/<file>.xlsx (and full/ inside it for
    a trimmed file, and the spectra), and notes the results folder in session.exported
    once something is written (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _file_exporter
    problem_teller
    """

    wanted = [s for s in session.summaries if names is None or s['name'] in names]
    problems: List[str] = []
    for number, summary in enumerate(wanted, start=1):
        try:
            with session.window.output_capturer():
                _file_exporter(session, summary, limits, details, choice, keep_full)
        except Exception as exc:  # one bad file must not stop the others
            problems.append(problem_teller(summary['name'], exc))
        if progress is not None:
            progress(number, len(wanted))
    if len(problems) < len(wanted) and session.export_root not in session.exported:
        session.exported.append(session.export_root)
    return problems


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
    settings.HAEM_TYPE_COLOURS, settings.pca_colour_mapper, settings.PREVIEW_DPI;
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
    type_colours = {kind: settings.HAEM_TYPE_COLOURS[kind][0] for kind in 'abc'}
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
    the settings, with the decomposition kept to compare with (session.kept) and the
    oxidised and reduced regions (session.regions), and draws every file the user looks at with them. Problems are reported, never raised, so the
    questions carry on.

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
                       kept=session.kept,
                       regions=copy.deepcopy(session.regions),
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
        shown while it was drawn (a skipped step, a missing OD), and the gaps to the
        kept decomposition when one is kept, one per line, and may be empty. A line
        starting with KEY_PREFIX explains the shading or the dashed lines and belongs
        by the controls.

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style; the details of a problem
    go to the log (side effects). Nothing is printed; the caller decides where the
    notes go.

    ---- Equations ----
    None.

    ---- Helpers ----
    _kept_haems_drawer
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
                                spec.regions,
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

    # ---- 2.1 Draw the kept decomposition over the haems ------------------------------
    if spec.kept is not None and haem_panels:
        kept_notes = _kept_haems_drawer(session,
                                        summary,
                                        info,
                                        preview_answers,
                                        spec.kept,
                                        processed['haem_source'],
                                        experiment,
                                        axes,
                                        plot_config,
                                        )
        notes = '\n'.join(line for line in (notes, kept_notes) if line)

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
