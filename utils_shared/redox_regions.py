"""
The maths of the oxidised and reduced regions: a haem's level in a region, % oxidised
from the two levels, and an edge copied to another file by its nearest addition.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import measurement_column_finder, time_getter, value_getter


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
