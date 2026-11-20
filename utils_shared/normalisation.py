"""
Normalisation of OCR and haem data by OD and to a relative scale.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Union

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.reference_level import (reference_level_finder,
                                          window_seconds_calculator,
                                          )
from utils_shared.schema import measurement_column_finder, time_getter


# ---- NORMALISATION HELPERS -----------------------------------------------------------


# ---- _frame_normaliser ---------------------------------------------------------------
def _frame_normaliser(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    """
    ---- Summary ----
    Helper function to OD-normalise the measurement columns of a data frame, leaving the
    time and index columns untouched.

    ---- Inputs ----
    df : pd.DataFrame
        Data frame with a time column and measurement columns.
    **kwargs : Any
        optical_density, volume, dilution_factor and label, passed to data_normaliser.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Scaled copy of the data frame.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    data_normaliser
    measurement_column_finder
    """

    result = df.copy()
    columns = measurement_column_finder(df)
    if columns:
        result[columns] = data_normaliser(df[columns], **kwargs)
    return result


# ---- _number_reader ------------------------------------------------------------------
def _number_reader(column: pd.Series, label: str) -> pd.Series:
    """
    ---- Summary ----
    Helper function to read one column as numbers, by the one rule of the scalings: an
    empty cell stays empty, anything else that is not a number stops the scaling.

    ---- Inputs ----
    column : pd.Series
        The column as it is in the table.
    label : str
        Name of the experiment or data, used in the message.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.Series
        The column as float64, NaN where the cell is empty. Raises ValueError, with a
        message for the user, when a cell holds something that is not a number.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    numbers = pd.to_numeric(column, errors='coerce').astype(float)
    unreadable = numbers.isna() & column.notna()
    if unreadable.any():
        example = column[unreadable].iloc[0]
        raise ValueError(f'{label}: the {column.name} values hold something that is '
                         f'not a number ({str(example)[:20]!r}), so they cannot be '
                         'scaled. The file may be damaged; save it again from the '
                         'instrument software.',
                         )
    return numbers


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- data_normaliser -----------------------------------------------------------------
def data_normaliser(data: Union[pd.DataFrame, pd.Series, np.ndarray],
                    optical_density: float,
                    volume: float,
                    dilution_factor: float,
                    label: str = 'data',
                    ) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
    """
    ---- Summary ----
    Main function to divide numeric data by dilution factor x optical density x volume.

    ---- Inputs ----
    data : Union[pd.DataFrame, pd.Series, np.ndarray]
        Numeric data to scale.
    optical_density : float
        OD of the sample (> 0).
    volume : float
        Volume of the sample (> 0).
    dilution_factor : float
        Dilution factor (> 0).
    label : str
        Name used in error messages.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Union[pd.DataFrame, pd.Series, np.ndarray]
        Scaled data of the same kind as the input; empty cells stay empty. Raises
        ValueError, with a message for the user, if the denominator is not positive
        and finite or a cell holds something that is not a number.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    scaled = data / (dilution_factor x optical_density x volume).

    ---- Helpers ----
    _number_reader
    """

    denominator = float(dilution_factor) * float(optical_density) * float(volume)
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError('The OD, the volume and the dilution factor must all be above '
                         '0. Correct them where the program asks for the OD.',
                         )
    if isinstance(data, pd.DataFrame):
        return data.apply(lambda column: _number_reader(column, label)) / denominator
    if isinstance(data, pd.Series):
        return _number_reader(data, label) / denominator
    try:
        return np.asarray(data, dtype=float) / denominator
    except (TypeError, ValueError):
        raise ValueError(f'{label}: the values hold something that is not a number, '
                         'so they cannot be scaled. The file may be damaged; save it '
                         'again from the instrument software.',
                         ) from None


# ---- experiment_normaliser -----------------------------------------------------------
def experiment_normaliser(experiment: dict) -> dict:
    """
    ---- Summary ----
    Main function to OD-normalise VoO2 and, when present, the haem data of an
    experiment.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.

    ---- Globals read ----
    None. Calls schema.measurement_columns.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError, with a message for the user,
        if dilution_factor, OD or volume is missing from the metadata, or if VoO2 has no
        measurement columns.

    ---- Globals mutated ----
    experiment: adds VoO2_OD and, for each of haem_conc, haem_abs and haem_delta_abs
    that exists, haem_OD, haem_abs_OD and haem_delta_abs_OD.

    ---- Equations ----
    x_OD = x / (dilution_factor x OD x volume). Dividing by a constant commutes with the
    shift behind delta abs, so haem_delta_abs_OD equals the shifted haem_abs_OD.

    ---- Helpers ----
    _frame_normaliser
    measurement_column_finder
    """

    # ---- 1 Check the required settings -----------------------------------------------
    metadata = experiment['metadata']
    missing = [key for key in ('dilution_factor', 'OD', 'volume') if key not in metadata
               ]
    if missing:
        raise ValueError(f"{experiment['experiment_name']}: the OD, the volume or the "
                         'dilution factor is missing, so the values cannot be scaled '
                         'by OD. Enter them where the program asks for the OD.',
                         )

    # ---- 2 Normalise the data --------------------------------------------------------
    kwargs = {'optical_density': metadata['OD'],
              'volume': metadata['volume'],
              'dilution_factor': metadata['dilution_factor'],
              'label': experiment['experiment_name'],
              }
    if not measurement_column_finder(experiment['VoO2']):
        raise ValueError(f"{experiment['experiment_name']}: the file has no oxygen "
                         'consumption (VO2) values to scale by OD.',
                         )
    experiment['VoO2_OD'] = _frame_normaliser(experiment['VoO2'], **kwargs)
    for source_key, target_key in (('haem_conc', 'haem_OD'),
                                   ('haem_abs', 'haem_abs_OD'),
                                   ('haem_delta_abs', 'haem_delta_abs_OD'),
                                   ):
        if isinstance(experiment.get(source_key), pd.DataFrame):
            experiment[target_key] = _frame_normaliser(experiment[source_key], **kwargs)
    return experiment


# ---- percent_converter ---------------------------------------------------------------
def percent_converter(experiment: dict,
                      source_key: str,
                      target_key: str,
                      **scaling_kwargs: Any,
                      ) -> dict:
    """
    ---- Summary ----
    Main function to scale one table of an experiment to 0-100 % and store it under a
    new key.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    source_key : str
        Key of the table to scale, e.g. 'haem_conc' or 'VoO2'.
    target_key : str
        Key the scaled table is stored under, e.g. 'haem_percent'.
    **scaling_kwargs : Any
        exclude_first_minutes, exclude_last_minutes and window_points, passed to
        percent_scaler.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError if the source table is
        unavailable.

    ---- Globals mutated ----
    experiment: adds experiment[target_key].

    ---- Equations ----
    None.

    ---- Helpers ----
    percent_scaler
    """

    # ---- 1 Check the source ----------------------------------------------------------
    source = experiment.get(source_key)
    if not isinstance(source, pd.DataFrame):
        raise ValueError(f"{experiment['experiment_name']}: the values to put on the % "
                         'scale are missing (an earlier step was skipped).',
                         )

    # ---- 2 Convert to percentages ----------------------------------------------------
    experiment[target_key] = percent_scaler(source,
                                            label=experiment['experiment_name'],
                                            **scaling_kwargs,
                                            )
    return experiment


# ---- percent_scaler ------------------------------------------------------------------
def percent_scaler(df: pd.DataFrame,
                   window_points: int,
                   label: str = 'data',
                   exclude_first_minutes: float = 0.0,
                   exclude_last_minutes: float = 0.0,
                   ) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to scale each measurement column of a data frame to a relative 0-100 %
    range.

    ---- Inputs ----
    df : pd.DataFrame
        Data frame with a time column (minutes) and measurement columns.
    window_points : int
        Number of points in a row that make a reference window (>= 1).
    label : str
        Name used in error messages.
    exclude_first_minutes : float
        Minutes after the first measurement that are ignored at the start.
    exclude_last_minutes : float
        Minutes before the last measurement that are ignored at the end.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Scaled copy; result.attrs["percent_scaling"] holds, per column,
        {'zero_percent_window', 'hundred_percent_window': the windows found
        (reference_level_finder), 'zero_percent_level', 'hundred_percent_level': their
        medians, 'window_seconds': the length of such a window}. A constant column
        becomes NaN. Raises ValueError, with a message for the user, for invalid
        settings, when a cell holds something that is not a number, or when fewer
        than window_points values are left after the ignored parts.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    percent = (value - low) / (high - low) x 100, where low and high are the medians of
    the lowest and of the highest points in a row (reference_level_finder). Values
    outside the range are kept.

    ---- Helpers ----
    _number_reader
    measurement_column_finder
    reference_level_finder
    time_getter
    window_seconds_calculator
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    if exclude_first_minutes < 0 or exclude_last_minutes < 0:
        raise ValueError('The time ignored at the start or the end of the run cannot '
                         'be negative. Correct it where the program asks for it.',
                         )

    # ---- 2 Find the usable part of the run -------------------------------------------
    columns = measurement_column_finder(df)
    if not columns:
        raise ValueError(f'{label}: there are no values to put on the % scale.')
    times = time_getter(df)
    finite_times = times[np.isfinite(times)]
    if finite_times.size == 0:
        raise ValueError(f'{label}: the times of the values could not be read, so '
                         'the % scale cannot be found.',
                         )
    start = float(finite_times.min()) + exclude_first_minutes
    stop = float(finite_times.max()) - exclude_last_minutes
    window_seconds = window_seconds_calculator(times, window_points)

    # ---- 3 Scale each column ---------------------------------------------------------
    result = df.copy()
    scaling_info = {}
    for column in columns:
        values = _number_reader(df[column], label).to_numpy(dtype=float)
        lowest = reference_level_finder(times,
                                        values,
                                        start,
                                        stop,
                                        window_points,
                                        is_highest=False,
                                        )
        highest = reference_level_finder(times, values, start, stop, window_points)
        if lowest is None or highest is None:
            raise ValueError(f'{label}: fewer than {window_points} {column} values '
                             'are left after the ignored start and end, too few to '
                             'find the 0 % and the 100 % (the medians of the lowest '
                             f'and of the highest {window_points} points in a row). '
                             'Ignore less of the start or the end of the run.',
                             )
        low, span = lowest['level'], highest['level'] - lowest['level']
        # A constant signal has no measurable relative range.
        result[column] = (np.nan
                          if np.isclose(span, 0.0)
                          else (values - low) / span * 100.0
                          )
        scaling_info[column] = {'zero_percent_window': lowest,
                                'hundred_percent_window': highest,
                                'zero_percent_level': low,
                                'hundred_percent_level': highest['level'],
                                'window_seconds': window_seconds,
                                }
    result.attrs['percent_scaling'] = scaling_info
    return result
