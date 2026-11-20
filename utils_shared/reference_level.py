"""
The one finder of the reference level of a trace: the median of its highest or lowest
points in a row.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- reference_level_finder ----------------------------------------------------------
def reference_level_finder(times: np.ndarray,
                           values: np.ndarray,
                           start: float,
                           stop: float,
                           n_points: int,
                           is_highest: bool = True,
                           ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to find the reference level of a trace: the median of its highest (or
    lowest) points in a row. It is the one rule behind the 0 of delta A and the 0 % and
    100 % of the % scale.

    ---- Inputs ----
    times : np.ndarray
        Time of each point in minutes, shape (n_timepoints).
    values : np.ndarray
        Value at each point, shape (n_timepoints).
    start : float
        Earliest time that may be used, in minutes.
    stop : float
        Latest time that may be used, in minutes.
    n_points : int
        Number of points in a row that make one window (>= 1).
    is_highest : bool
        True for the window with the highest median, False for the lowest.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[dict]
        {'level': the median of the chosen window, 'start_time' and 'end_time': the
        times of its first and last point (min), 'n_points': n_points}, or None when
        fewer than n_points usable points lie between start and stop. Of equal windows
        the earliest is chosen. Raises ValueError when n_points is below 1.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The points are put in time order; points with a blank time or value, or outside
    start to stop, are dropped, so the points on either side of a blank count as
    neighbours. Window i = points i to i + n_points - 1; level = max (or min) over i
    of median(window i). The windows are counted in points, not in time, and the last
    one ends at the last usable point.

    ---- Helpers ----
    None.
    """

    # ---- 1 Keep the usable points, in time order -------------------------------------
    if n_points < 1:
        raise ValueError('The number of points of the reference level must be at '
                         'least 1. Correct it in config.py.',
                         )
    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=float)
    order = np.argsort(times, kind='stable')
    times, values = times[order], values[order]
    usable = (np.isfinite(times) & np.isfinite(values)
              & (times >= start) & (times <= stop))
    times, values = times[usable], values[usable]
    if times.size < n_points:
        return None

    # ---- 2 Choose the window ---------------------------------------------------------
    windows = np.lib.stride_tricks.sliding_window_view(values, n_points)
    medians = np.median(windows, axis=1)
    best = int(np.argmax(medians) if is_highest else np.argmin(medians))
    return {'level': float(medians[best]),
            'start_time': float(times[best]),
            'end_time': float(times[best + n_points - 1]),
            'n_points': int(n_points),
            }


# ---- window_seconds_calculator -------------------------------------------------------
def window_seconds_calculator(times: np.ndarray, n_points: int) -> float:
    """
    ---- Summary ----
    Main function to work out how long a window of points in a row lasts, for the
    messages to the user.

    ---- Inputs ----
    times : np.ndarray
        Time of each point in minutes, shape (n_timepoints).
    n_points : int
        Number of points in a row that make one window.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Length of the window in seconds; NaN when fewer than two times are known.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    seconds = n_points x median time between neighbouring points (min) x 60.

    ---- Helpers ----
    None.
    """

    times = np.asarray(times, dtype=float)
    times = np.sort(times[np.isfinite(times)])
    if times.size < 2:
        return float('nan')
    return float(n_points * np.median(np.diff(times)) * 60.0)
