"""
Convert transmission spectra to the attenuation spectra used for decomposition.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Optional, Sequence, Tuple, Union

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- attenuation_converter -----------------------------------------------------------
def attenuation_converter(transmission: Union[Sequence[float], np.ndarray],
                          ) -> np.ndarray:
    """
    ---- Summary ----
    Main function to convert transmission spectra to attenuation (minus log10 of the
    transmittance), as the instrument exports it.

    ---- Inputs ----
    transmission : Union[Sequence[float], np.ndarray]
        Transmission as a fraction (0-1), as the .paf files hold it; any shape.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Attenuation with the shape of the input. Zero, negative or non-finite
        transmission becomes NaN.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    attenuation = -log10(T), where T is the transmittance (fraction): less light than
    the reference gives a positive attenuation. The fit shapes are stored with this
    sign, so the decomposition uses them as they are.

    ---- Helpers ----
    None.
    """

    # Zero, negative or non-finite transmission has no logarithm. Those values become
    # NaN (a gap in the decomposition for the spectra that contain them) instead of
    # stopping the whole experiment; the caller reports how many there were.
    transmittance = np.asarray(transmission, dtype=float)
    bad = ~np.isfinite(transmittance) | (transmittance <= 0)
    # Taken from 0.0, not negated: a transmittance of exactly 1 then gives 0.0 and not
    # -0.0, which would be written as "-0.0" in the exported files.
    with np.errstate(divide='ignore', invalid='ignore'):
        attenuation = 0.0 - np.log10(np.where(bad, np.nan, transmittance))
    return attenuation


# ---- experiment_attenuation_adder ----------------------------------------------------
def experiment_attenuation_adder(experiment: dict,
                                 datasets: Optional[Sequence[str]] = None,
                                 checked_range_nm: Optional[Tuple[float, float]] = None,
                                 ) -> dict:
    """
    ---- Summary ----
    Main function to add an attenuation array to the spectral datasets of an experiment.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    datasets : Optional[Sequence[str]]
        Dataset names to convert; None converts all of them.
    checked_range_nm : Optional[Tuple[float, float]]
        (lowest, highest) wavelength (nm) in which blank values are counted for the
        warning: the range of the fit when the spectra are decomposed, since a blank
        outside it changes no haem amount. None counts every wavelength.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError if a transmission array is not
        2D.

    ---- Globals mutated ----
    experiment: adds raw_spectra[dataset]["attenuation"] (n_spectra x n_wavelengths) for
    each converted dataset; prints a warning with the number of blank values inside
    checked_range_nm (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    attenuation_converter
    """

    # ---- 1 Add the attenuation to each raw spectrum ----------------------------------
    for dataset_name, dataset in experiment.get('raw_spectra', {}).items():
        if datasets is not None and dataset_name not in datasets:
            continue
        transmission = np.asarray(dataset.get('transmission'), dtype=float)
        if transmission.ndim != 2:
            raise ValueError(f"{experiment.get('experiment_name', '<unknown>')}: "
                             f'{dataset_name}: '
                             'transmission must be a 2D array before attenuation '
                             'conversion.',
                             )
        dataset['attenuation'] = attenuation_converter(transmission)
        blank = np.isnan(dataset['attenuation'])
        where = ''
        if checked_range_nm is not None:
            lowest, highest = checked_range_nm
            wavelengths = np.asarray(dataset.get('wavelengths'), dtype=float)
            # Only when the wavelengths match the spectra; otherwise every value is
            # counted, and the decomposition reports the mismatch itself.
            if wavelengths.shape == (blank.shape[1],):
                blank = blank[:, (wavelengths >= lowest) & (wavelengths <= highest)]
                where = (f' between {lowest:g} and {highest:g} nm (the range of the '
                         'fit)'
                         )
        n_bad = int(np.count_nonzero(blank))
        if n_bad:
            rows = int(np.count_nonzero(blank.any(axis=1)))
            print(f'  Warning: {dataset_name}: {n_bad} transmission values{where} '
                  'were zero, negative or missing '
                  f'({rows} spectra affected); they are left blank.',
                  )
    return experiment
