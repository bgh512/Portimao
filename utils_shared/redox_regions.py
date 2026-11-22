"""
The maths of the oxidised and reduced regions: a haem's level in a region, the two
levels of a file, % oxidised from them, and an edge copied to another file by its
nearest addition.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import measurement_column_finder, time_getter, value_getter


# ---- CONSTANTS -----------------------------------------------------------------------
# The four edges of the two regions of a file, in the order of the boxes in the strip.
REGION_KEYS = ('oxidised_start', 'oxidised_end', 'reduced_start', 'reduced_end')
REGION_NAMES = ('oxidised', 'reduced')
# The edge that stands for a region not chosen: the one pulled out to open it.
CLOSED_KEYS = {'oxidised': 'oxidised_end', 'reduced': 'reduced_start'}
LENGTH_TOLERANCE_MIN = 1e-9  # so a region of exactly the least length counts as open


# ---- REGION HELPERS ------------------------------------------------------------------


# ---- _region_open_checker ------------------------------------------------------------
def _region_open_checker(values: Dict[str, float],
                         region: str,
                         minimum_min: float,
                         ) -> bool:
    """
    ---- Summary ----
    Helper function to say whether a region of a file is chosen: at least as long as
    the least length.

    ---- Inputs ----
    values : Dict[str, float]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
    region : str
        'oxidised' or 'reduced'.
    minimum_min : float
        Least length of a region (min).

    ---- Globals read ----
    LENGTH_TOLERANCE_MIN.

    ---- Outputs ----
    bool
        True when the region is open (chosen).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    open when end - start >= least length.

    ---- Helpers ----
    None.
    """

    length = values[f'{region}_end'] - values[f'{region}_start']
    return bool(length >= minimum_min - LENGTH_TOLERANCE_MIN)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- edge_anchor_finder --------------------------------------------------------------
def edge_anchor_finder(time_min: float,
                       additions_min: Sequence[float],
                       ) -> Optional[Tuple[int, float]]:
    """
    ---- Summary ----
    Main function to say where an edge of a region sits by the addition nearest to it:
    which addition of the file, counted in order, and how far from it. It is the first
    half of copying an edge to another file; edge_time_finder is the second.

    ---- Inputs ----
    time_min : float
        Time of the edge (min), on the same time axis as the additions.
    additions_min : Sequence[float]
        Times of the additions of the file the edge was set on (min), in any order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Tuple[int, float]]
        (number of the nearest addition, counted in time order from 0; distance of the
        edge from it in minutes, negative before the addition), or None when the file
        has no addition or the time is blank, so the edge cannot be copied.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    nearest = the addition with the smallest |time - addition|; of two equally near,
    the earlier. distance = time - nearest. An edge before the first addition is
    nearest to the first, so it is copied by its distance to the first.

    ---- Helpers ----
    None.
    """

    additions = np.sort(np.asarray(additions_min, dtype=float))
    additions = additions[np.isfinite(additions)]
    if additions.size == 0 or not np.isfinite(time_min):
        return None
    nearest = int(np.argmin(np.abs(additions - float(time_min))))
    return nearest, float(time_min) - float(additions[nearest])


# ---- edge_time_finder ----------------------------------------------------------------
def edge_time_finder(anchor: Tuple[int, float],
                     additions_min: Sequence[float],
                     ) -> Optional[float]:
    """
    ---- Summary ----
    Main function to give the time of a copied edge in another file: the same distance
    from the addition of the same number.

    ---- Inputs ----
    anchor : Tuple[int, float]
        (number of the addition, counted in time order from 0; distance from it in
        minutes), from edge_anchor_finder.
    additions_min : Sequence[float]
        Times of the additions of the file the edge is copied to (min), in any order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        Time of the edge in that file (min), on the time axis of its additions, or None
        when the file has no addition of that number (it has fewer additions), so it
        keeps the region it had. The time is not kept within the used part of the run;
        the limits of the edges do that.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time = time of the addition of the same number in this file + distance.

    ---- Helpers ----
    None.
    """

    number, distance = anchor
    additions = np.sort(np.asarray(additions_min, dtype=float))
    additions = additions[np.isfinite(additions)]
    if not 0 <= number < additions.size:
        return None
    return float(additions[number]) + float(distance)


# ---- haem_levels_finder --------------------------------------------------------------
def haem_levels_finder(haem_table: pd.DataFrame,
                       regions: Optional[Dict[str, float]],
                       shift_min: float,
                       used_span: Tuple[float, float],
                       minimum_points: int,
                       label: str = 'This file',
                       ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to find the oxidised and the reduced level of every haem of a file
    from the two regions kept for it. A file needs both regions: with none, with only
    one, or with one that no longer holds enough spectra in the used part of the run
    (the trim or the ignored parts changed), it has no levels.

    ---- Inputs ----
    haem_table : pd.DataFrame
        Haem table (time, spectrum index and one column per haem), in any one unit,
        on the time axis of the trimmed data.
    regions : Optional[Dict[str, float]]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} as times on the
        original recording (min), or None when nothing is kept for the file.
    shift_min : float
        Trim start (min): what is taken off a time on the recording for the time on
        the trimmed data.
    used_span : Tuple[float, float]
        (first, last) time of the used part of the run (min), on the trimmed data.
    minimum_points : int
        Least number of spectra a region must hold (config.REGION_MINIMUM_POINTS).
    label : str
        Name of the file in the messages.

    ---- Globals read ----
    REGION_NAMES.

    ---- Outputs ----
    Optional[dict]
        {'oxidised': {haem: level}, 'reduced': {haem: level}, in the unit of the
        table; 'oxidised_region', 'reduced_region': (start_min, end_min) on the time
        axis of the table, kept within the used part}, or None when the file does not
        have both regions. Raises ValueError (region_level_finder) when a haem has too
        few values inside a region that holds enough spectra.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    start = max(start on the recording - shift, first); end = min(end on the
    recording - shift, last). A region counts when it holds at least minimum_points
    spectra with start <= time <= end. level: region_level_finder.

    ---- Helpers ----
    region_level_finder
    time_getter
    """

    if not regions:
        return None
    first, last = float(used_span[0]), float(used_span[1])
    times = time_getter(haem_table)
    result: dict = {}
    for region in REGION_NAMES:
        try:
            start = max(float(regions[f'{region}_start']) - float(shift_min), first)
            end = min(float(regions[f'{region}_end']) - float(shift_min), last)
        except (KeyError, TypeError, ValueError):  # not the four times of a file
            return None
        if not (np.isfinite(start) and np.isfinite(end)) or end <= start:
            return None
        inside = np.isfinite(times) & (times >= start) & (times <= end)
        if int(inside.sum()) < minimum_points:
            return None
        result[region] = region_level_finder(haem_table,
                                             start,
                                             end,
                                             minimum_points,
                                             region=f'{region} region',
                                             label=label,
                                             )
        result[f'{region}_region'] = (start, end)
    return result


# ---- percent_oxidised_calculator -----------------------------------------------------
def percent_oxidised_calculator(haem_table: pd.DataFrame,
                                oxidised_levels: Dict[str, float],
                                reduced_levels: Dict[str, float],
                                ) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to put every haem of a table on the % oxidised scale, which runs
    from its level in the reduced region (0 %) to its level in the oxidised region
    (100 %).

    ---- Inputs ----
    haem_table : pd.DataFrame
        Haem table (time, spectrum index and one column per haem), in any one unit:
        the scale is the same for the amounts, the absorbances and delta D.
    oxidised_levels : Dict[str, float]
        {haem: its level in the oxidised region}, in the unit of the table
        (region_level_finder).
    reduced_levels : Dict[str, float]
        {haem: its level in the reduced region}, in the same unit.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Copy of the table with every haem in %; values above 100 and below 0 are kept.
        A haem whose two levels are equal, or blank, has an empty column (NaN), as no
        scale can be made from them. result.attrs["percent_oxidised"] holds
        {'oxidised_level_by_haem', 'reduced_level_by_haem': the levels used,
        'empty_haems': the haems with an empty column}. Raises ValueError when a haem
        of the table has no level in one of the two.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    percent = (D - D_red) / (D_ox - D_red) x 100, per haem, with D the value at one
    time, D_ox the oxidised level and D_red the reduced level.

    ---- Helpers ----
    measurement_column_finder
    value_getter
    """

    # ---- 1 Check every haem has its two levels ---------------------------------------
    columns = measurement_column_finder(haem_table)
    missing = [str(column) for column in columns
               if column not in oxidised_levels or column not in reduced_levels
               ]
    if missing:
        raise ValueError(f"{', '.join(missing)}: no oxidised or reduced level was "
                         'worked out, so % oxidised cannot be. This is a fault in '
                         'the program; please report it.',
                         )

    # ---- 2 Scale each haem between its two levels ------------------------------------
    result = haem_table.copy()
    empty: List[str] = []
    for column in columns:
        oxidised = float(oxidised_levels[column])
        reduced = float(reduced_levels[column])
        span = oxidised - reduced
        values = value_getter(haem_table, column)
        if not np.isfinite(span) or span == 0:
            empty.append(str(column))
            result[column] = np.full(values.shape, np.nan)
            continue
        result[column] = (values - reduced) / span * 100.0
    result.attrs['percent_oxidised'] = {
        'oxidised_level_by_haem': {str(column): float(oxidised_levels[column])
                                   for column in columns
                                   },
        'reduced_level_by_haem': {str(column): float(reduced_levels[column])
                                  for column in columns
                                  },
        'empty_haems': empty,
        }
    return result


# ---- region_edge_copier --------------------------------------------------------------
def region_edge_copier(time_min: float,
                       source_additions_min: Sequence[float],
                       target_additions_min: Sequence[float],
                       ) -> Optional[float]:
    """
    ---- Summary ----
    Main function to copy an edge set on one file to another file: the same distance
    from the addition of the same number as the one nearest to it in the first file.

    ---- Inputs ----
    time_min : float
        Time of the edge on the file it was set on (min).
    source_additions_min : Sequence[float]
        Times of the additions of that file (min), on the same time axis.
    target_additions_min : Sequence[float]
        Times of the additions of the file the edge is copied to (min), on that
        file's time axis.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        Time of the edge in the other file (min), not yet kept within its limits, or
        None when it cannot be copied (the first file has no addition, or the other
        has fewer additions), so the other file keeps the edge it had.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    time = time of the same addition in the other file + (edge - nearest addition).

    ---- Helpers ----
    edge_anchor_finder
    edge_time_finder
    """

    anchor = edge_anchor_finder(time_min, source_additions_min)
    if anchor is None:
        return None
    return edge_time_finder(anchor, target_additions_min)


# ---- region_edge_setter --------------------------------------------------------------
def region_edge_setter(values: Dict[str, float],
                       key: str,
                       value: float,
                       used_span: Tuple[float, float],
                       minimum_min: float,
                       ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to set one edge of one region of a file to a time, kept within the
    limits: an edge stays in the used part of the run; moved past the other edge of its
    region it pushes that edge along; and the two regions never overlap. An edge moved
    into the other region stops at that region's nearer side, and when the other region
    would then lie inside this one, the edge not being set gives way to it.

    ---- Inputs ----
    values : Dict[str, float]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
    key : str
        The edge set: one of REGION_KEYS.
    value : float
        Time wanted for it (min).
    used_span : Tuple[float, float]
        (first, last) time of the used part of the run (min): not trimmed, not
        ignored.
    minimum_min : float
        Least length of a region (min); a shorter one counts as not chosen, so the
        other region may cross it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, float]
        New values of the file; the dictionary given is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    t = value kept within the used part. With the other region open from a to b and
    a < t < b: t = a when t - a <= b - t, otherwise b. Start edge set: end = max(end,
    t), and end = a when t <= a < end. End edge set: start = min(start, t), and
    start = b when start < b <= t.

    ---- Helpers ----
    _region_open_checker
    """

    region, side = key.split('_')
    other = 'reduced' if region == 'oxidised' else 'oxidised'
    first, last = used_span
    time_min = min(max(float(value), float(first)), float(last))
    other_start, other_end = values[f'{other}_start'], values[f'{other}_end']
    is_other_open = _region_open_checker(values, other, minimum_min)
    if is_other_open and other_start < time_min < other_end:
        is_nearer_start = time_min - other_start <= other_end - time_min
        time_min = other_start if is_nearer_start else other_end
    changed = dict(values)
    changed[key] = time_min
    if side == 'start':
        end = max(values[f'{region}_end'], time_min)
        if is_other_open and time_min <= other_start < end:
            end = other_start
        changed[f'{region}_end'] = end
    else:
        start = min(values[f'{region}_start'], time_min)
        if is_other_open and start < other_end <= time_min:
            start = other_end
        changed[f'{region}_start'] = start
    return changed


# ---- region_edges_builder ------------------------------------------------------------
def region_edges_builder(used_span: Tuple[float, float],
                         remembered: Optional[Dict[str, float]],
                         minimum_min: float,
                         ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to give the edges a file starts the regions step with: both regions
    not chosen, parked at the sides of the used part (oxidised at its start, reduced at
    its end), or the regions remembered for it, kept within the used part. A
    remembered region that is no longer long enough is parked again.

    ---- Inputs ----
    used_span : Tuple[float, float]
        (first, last) time of the used part of the run (min).
    remembered : Optional[Dict[str, float]]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} (min) on the same
        time axis, or None for a file with nothing remembered.
    minimum_min : float
        Least length of a region (min).

    ---- Globals read ----
    REGION_KEYS, REGION_NAMES.

    ---- Outputs ----
    Dict[str, float]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} (min).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Parked: oxidised start = oxidised end = first; reduced start = reduced end = last.

    ---- Helpers ----
    _region_open_checker
    """

    first, last = float(used_span[0]), float(used_span[1])
    parked = {'oxidised_start': first,
              'oxidised_end': first,
              'reduced_start': last,
              'reduced_end': last,
              }
    if not remembered:
        return parked
    values = {key: min(max(float(remembered.get(key, parked[key])), first), last)
              for key in REGION_KEYS
              }
    for region in REGION_NAMES:
        if not _region_open_checker(values, region, minimum_min):
            values[f'{region}_start'] = parked[f'{region}_start']
            values[f'{region}_end'] = parked[f'{region}_end']
    return values


# ---- region_layout_finder ------------------------------------------------------------
def region_layout_finder(values: Dict[str, float],
                         minimum_min: float,
                         ) -> Tuple[List[Tuple[str, float, str, str]],
                                    List[Tuple[float, float, str]],
                                    ]:
    """
    ---- Summary ----
    Main function to say where the edges of the two regions of one file sit on its
    plot, with the words by each handle, and which parts are shaded. A region not
    chosen has one handle, reading "not chosen", and no shading.

    ---- Inputs ----
    values : Dict[str, float]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min),
        on the time axis of the plot.
    minimum_min : float
        Least length of a region (min); a shorter one is not chosen.

    ---- Globals read ----
    REGION_NAMES, CLOSED_KEYS.

    ---- Outputs ----
    Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
        (edges, parts): edges as [(key, time_min, words, kind)] with kind 'oxidised'
        or 'reduced'; parts as [(start_min, end_min, kind)]. The words of an open
        region are by the edge that opened it (the end of the oxidised region, the
        start of the reduced one), which keeps them clear of its other handle where
        the regions usually are; the other edge has no words.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _region_open_checker
    """

    edges: List[Tuple[str, float, str, str]] = []
    parts: List[Tuple[float, float, str]] = []
    for region in REGION_NAMES:
        start, end = values[f'{region}_start'], values[f'{region}_end']
        if not _region_open_checker(values, region, minimum_min):
            key = CLOSED_KEYS[region]
            edges.append((key, values[key], f'{region}: not chosen', region))
            continue
        words = f'{region} {round(start, 2):g} to {round(end, 2):g} min'
        is_worded = {side: f'{region}_{side}' == CLOSED_KEYS[region]
                     for side in ('start', 'end')
                     }
        edges.append((f'{region}_start',
                      start,
                      words if is_worded['start'] else '',
                      region,
                      ),
                     )
        edges.append((f'{region}_end', end, words if is_worded['end'] else '', region))
        parts.append((start, end, region))
    return edges, parts


# ---- region_level_finder -------------------------------------------------------------
def region_level_finder(haem_table: pd.DataFrame,
                        start_min: float,
                        end_min: float,
                        minimum_points: int,
                        region: str = 'region',
                        label: str = 'This file',
                        ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to find the level of every haem of a table in one region: the median
    of its values there. One region serves every haem of the file.

    ---- Inputs ----
    haem_table : pd.DataFrame
        Haem table (time, spectrum index and one column per haem), in any one unit.
    start_min : float
        First time of the region (min), on the time axis of the table.
    end_min : float
        Last time of the region (min); the spectra at both edges count as inside.
    minimum_points : int
        Least number of spectra with a value a haem must have in the region (>= 1;
        config.REGION_MINIMUM_POINTS in the program).
    region : str
        Name of the region in the messages: 'oxidised region' or 'reduced region'.
    label : str
        Name of the file in the messages.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, float]
        {haem: its level in the region}, in the unit of the table. Raises ValueError,
        with a message for the user, when the region ends before it starts, a time is
        blank, the table holds no haem, or a haem has fewer than minimum_points
        spectra with a value in the region.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    level = median(D at every spectrum with start <= time <= end), per haem. A spectrum
    with a blank value for a haem is left out for that haem.

    ---- Helpers ----
    measurement_column_finder
    time_getter
    value_getter
    """

    # ---- 1 Validate the region -------------------------------------------------------
    if minimum_points < 1:
        raise ValueError('The least number of spectra in a region must be at least 1. '
                         'Correct it in config.py.',
                         )
    if not (np.isfinite(start_min) and np.isfinite(end_min)) or end_min < start_min:
        raise ValueError(f'{label}: the {region} has no start and end that can be '
                         'used. Pull its two edges out on the plot again.',
                         )
    columns = measurement_column_finder(haem_table)
    if not columns:
        raise ValueError(f'{label}: there are no haems to find the level of in the '
                         f'{region}. Check that the fit file holds haems.',
                         )

    # ---- 2 Take the median of each haem inside it ------------------------------------
    times = time_getter(haem_table)
    inside = np.isfinite(times) & (times >= start_min) & (times <= end_min)
    levels: Dict[str, float] = {}
    for column in columns:
        values = value_getter(haem_table, column)[inside]
        values = values[np.isfinite(values)]
        if values.size < minimum_points:
            raise ValueError(f'{label}: the {region} ({start_min:.2f} to '
                             f'{end_min:.2f} min) holds {values.size} spectra with a '
                             f'value for {column}, fewer than the {minimum_points} a '
                             'level needs. Make the region longer.',
                             )
        levels[str(column)] = float(np.median(values))
    return levels


# ---- region_pointer_reader -----------------------------------------------------------
def region_pointer_reader(time_min: float) -> float:
    """
    ---- Summary ----
    Main function to turn a time pointed at on the plot into the time of the edge put
    there, in steps of 0.1 min.

    ---- Inputs ----
    time_min : float
        The time pointed at, on the time axis of the plot (min).

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The time rounded to 0.1 min; the limits of the edges are applied afterwards
        (region_edge_setter).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return round(float(time_min), 1)


# ---- region_span_reader --------------------------------------------------------------
def region_span_reader(values: Dict[str, float],
                       minimum_min: float,
                       ) -> Dict[str, Optional[Tuple[float, float]]]:
    """
    ---- Summary ----
    Main function to give the two regions of a file as they were chosen: each as its
    first and last time, or None when it was not chosen.

    ---- Inputs ----
    values : Dict[str, float]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
    minimum_min : float
        Least length of a region (min); a shorter one is not chosen.

    ---- Globals read ----
    REGION_NAMES.

    ---- Outputs ----
    Dict[str, Optional[Tuple[float, float]]]
        {'oxidised': (start_min, end_min) or None, 'reduced': the same}. A file needs
        both for its haems' levels; one alone counts as none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _region_open_checker
    """

    return {region: ((float(values[f'{region}_start']), float(values[f'{region}_end']))
                     if _region_open_checker(values, region, minimum_min)
                     else None
                     )
            for region in REGION_NAMES
            }


# ---- short_region_closer -------------------------------------------------------------
def short_region_closer(values: Dict[str, float],
                        minimum_min: float,
                        ) -> Dict[str, float]:
    """
    ---- Summary ----
    Main function to give the edges of a file with every region that is too short to
    count closed: its two edges together, where its handle is. A region is then
    chosen exactly when its end is after its start, which is how it is kept with the
    dataset.

    ---- Inputs ----
    values : Dict[str, float]
        {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
    minimum_min : float
        Least length of a region (min); a shorter one is not chosen.

    ---- Globals read ----
    REGION_NAMES, CLOSED_KEYS.

    ---- Outputs ----
    Dict[str, float]
        New values of the file; the dictionary given is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A region with end - start < least length: start = end = the edge that opens it
    (the end of the oxidised region, the start of the reduced one).

    ---- Helpers ----
    _region_open_checker
    """

    closed = {key: float(value) for key, value in values.items()}
    for region in REGION_NAMES:
        if not _region_open_checker(values, region, minimum_min):
            edge = closed[CLOSED_KEYS[region]]
            closed[f'{region}_start'] = edge
            closed[f'{region}_end'] = edge
    return closed
