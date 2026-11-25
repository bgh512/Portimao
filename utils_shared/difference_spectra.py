"""
The difference spectrum of a file, reduced minus oxidised, its decomposition into the haems and its figure.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.spectral_decomposer import spectrum_decomposer


# ---- CONSTANTS -----------------------------------------------------------------------
# OD to mOD
MOD_PER_OD = 1000.0
# The attribute a figure of the difference spectrum carries, so the window knows it has
# no time axis (no time cursor, no edges and no arrows beside its panels).
WAVELENGTH_FIGURE_MARK = 'is_wavelength_figure'
# The residual panel's share of the height of the figure.
RESIDUAL_HEIGHT_SHARE = 0.25
X_LABEL = 'Wavelength (nm)'
Y_LABEL = 'Reduced − oxidised (mOD)'
RESIDUAL_LABEL = 'Residual (mOD)'


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- difference_decomposer -----------------------------------------------------------
def difference_decomposer(difference: dict,
                          fit: dict,
                          background: str,
                          haem_factor: float,
                          ) -> dict:
    """
    ---- Summary ----
    Main function to decompose the difference spectrum into the haems of the fit and
    the background under them, as one spectrum of the run is decomposed (MATHS.md
    section 1.2).

    ---- Inputs ----
    difference : dict
        The difference spectrum (difference_spectrum_builder; DATA_FORMAT.md,
        region_difference).
    fit : dict
        The fit in use: 'data' (the fit table) and 'haem_list' (the haem names in the
        order of its columns).
    background : str
        The background fitted under the haems, a key of BACKGROUND_LABELS (the answer
        haem_background).
    haem_factor : float
        Scale factor of the fit shapes (config.HAEM_FACTOR).

    ---- Globals read ----
    MOD_PER_OD.

    ---- Outputs ----
    dict
        The decomposition (DATA_FORMAT.md, region_difference_decomposition), its spectra on
        the wavelengths the fit covers, in mOD.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    ΔA(w) = Σ c_i S_i(w) + background(w) + residual(w), with c_i found by least
    squares; fit = haems + background.

    ---- Helpers ----
    spectrum_decomposer
    """

    spectrum_OD = np.column_stack(
        (np.asarray(difference['wavelengths_nm'], dtype=float),
         np.asarray(difference['difference_mOD'], dtype=float)
         / MOD_PER_OD,
         ),
        )
    (amounts,
     filtered,
     scatter,
     _,
     haems,
     haem_individual,
     residual,
     ) = spectrum_decomposer(spectrum_OD, fit['data'], background, haem_factor)
    names = list(fit['haem_list'])
    return {'wavelengths_nm': filtered[:, 0],
            'measured_mOD': filtered[:, 1] * MOD_PER_OD,
            'haems_mOD': {name: haem_individual[i][:, 1] * MOD_PER_OD
                          for i, name in enumerate(names)
                          },
            'background_mOD': scatter[:, 1] * MOD_PER_OD,
            'fit_mOD': (haems[:, 1] + scatter[:, 1]) * MOD_PER_OD,
            'residual_mOD': residual[:, 1] * MOD_PER_OD,
            'amounts': {name: float(amounts[i]) for i, name in enumerate(names)},
            }


# ---- difference_figure_drawer --------------------------------------------------------
def difference_figure_drawer(fig: Figure,
                             difference: dict,
                             decomposition: dict,
                             colours: Dict[str, str],
                             style: dict,
                             ) -> List:
    """
    ---- Summary ----
    Main function to draw the difference spectrum on a figure: on top the measured
    difference in black, each haem in its colour, the background dotted and the fit
    (haems + background) dashed, with a key giving the times of the two regions; under
    it a small panel of the residual. The figure is marked as having no time axis.

    ---- Inputs ----
    fig : Figure
        The figure to draw on; it is cleared first.
    difference : dict
        The difference spectrum (difference_spectrum_builder).
    decomposition : dict
        Its decomposition (difference_decomposer).
    colours : Dict[str, str]
        {haem name: colour} (config.haem_colour_mapper).
    style : dict
        Greys and line widths (config.COMPONENT_FIGURE_STYLE).

    ---- Globals read ----
    RESIDUAL_HEIGHT_SHARE, RESIDUAL_LABEL, WAVELENGTH_FIGURE_MARK, X_LABEL, Y_LABEL.

    ---- Outputs ----
    List
        The two axes, the spectrum first.

    ---- Globals mutated ----
    None. Draws on the figure and sets its WAVELENGTH_FIGURE_MARK attribute (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 The two panels, sharing the wavelength axis -------------------------------
    fig.clf()
    grid = fig.add_gridspec(2,
                            1,
                            height_ratios=(1.0 - RESIDUAL_HEIGHT_SHARE,
                                           RESIDUAL_HEIGHT_SHARE,
                                           ),
                            hspace=0.08,
                            )
    main = fig.add_subplot(grid[0])
    lower = fig.add_subplot(grid[1], sharex=main)
    wavelengths = decomposition['wavelengths_nm']

    # ---- 2 The difference, each haem, the background and the fit ---------------------
    main.plot(wavelengths,
              decomposition['measured_mOD'],
              color='black',
              linewidth=style['fitted_line_width'],
              label='Measured',
              )
    for name, values in decomposition['haems_mOD'].items():
        main.plot(wavelengths,
                  values,
                  color=colours.get(name, style['background_colour']),
                  linewidth=style['part_line_width'],
                  label=name,
                  )
    main.plot(wavelengths,
              decomposition['background_mOD'],
              color=style['background_colour'],
              linestyle=':',
              linewidth=style['part_line_width'],
              label='Background',
              )
    main.plot(wavelengths,
              decomposition['fit_mOD'],
              color=style['residual_colour'],
              linestyle='--',
              linewidth=style['fitted_line_width'],
              label='Fit (haems + background)',
              )
    main.axhline(0, color=style['zero_colour'], linewidth=style['zero_line_width'])
    oxidised, reduced = difference['oxidised_region'], difference['reduced_region']
    main.legend(title=(f'Reduced {reduced[0]:.1f}–{reduced[1]:.1f} min − '
                       f'oxidised {oxidised[0]:.1f}–{oxidised[1]:.1f} min'
                       ),
                loc='best',
                frameon=False,
                )
    main.set_ylabel(Y_LABEL)
    main.tick_params(labelbottom=False)

    # ---- 3 The residual underneath ---------------------------------------------------
    lower.plot(wavelengths,
               decomposition['residual_mOD'],
               color=style['residual_colour'],
               linewidth=style['residual_line_width'],
               )
    lower.axhline(0, color=style['zero_colour'], linewidth=style['zero_line_width'])
    lower.set_ylabel(RESIDUAL_LABEL)
    lower.set_xlabel(X_LABEL)
    setattr(fig, WAVELENGTH_FIGURE_MARK, True)
    return [main, lower]


# ---- difference_spectrum_builder -----------------------------------------------------
def difference_spectrum_builder(experiment: dict, dataset: str) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to work out the difference spectrum of a processed file: the mean
    attenuation of its spectra in the reduced region minus that in the oxidised region,
    at each wavelength. There is none for a file without both regions.

    ---- Inputs ----
    experiment : dict
        The processed experiment (DATA_FORMAT.md), with 'raw_spectra' and, for a file
        with both regions, 'haem_levels'.
    dataset : str
        The spectrometer whose spectra hold the haems (the answer
        decomposition_dataset).

    ---- Globals read ----
    MOD_PER_OD.

    ---- Outputs ----
    Optional[dict]
        The difference spectrum (DATA_FORMAT.md, region_difference), or None when the
        file has no 'haem_levels' or a region holds no spectrum. Raises ValueError when
        the file has no attenuation spectra of that spectrometer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    ΔA(w) = mean of A(w) over the spectra in the reduced region - mean of A(w) over
    the spectra in the oxidised region, × 1000 for mOD (MATHS.md section 9).

    ---- Helpers ----
    None.
    """

    # ---- 1 The two regions -----------------------------------------------------------
    levels = experiment.get('haem_levels')
    if not levels:
        return None
    name = experiment.get('experiment_name', 'This file')
    data = experiment.get('raw_spectra', {}).get(dataset)
    if data is None or 'attenuation' not in data:
        raise ValueError(f'{name}: the file has no {dataset} spectra to take the '
                         'difference of. Choose spectra that the file holds.',
                         )

    # ---- 2 The mean spectrum of each region, then their difference -------------------
    times = np.asarray(data['time'], dtype=float)
    spectra = np.asarray(data['attenuation'], dtype=float)
    means, counts = {}, {}
    for region in ('oxidised', 'reduced'):
        start, end = levels[f'{region}_region']
        inside = (times >= start) & (times <= end)
        if not inside.any():
            return None
        means[region] = spectra[inside].mean(axis=0)
        counts[region] = int(inside.sum())
    return {'dataset': dataset,
            'wavelengths_nm': np.asarray(data['wavelengths'], dtype=float),
            'difference_mOD': (means['reduced'] - means['oxidised']) * MOD_PER_OD,
            'oxidised_region': tuple(float(v) for v in levels['oxidised_region']),
            'reduced_region': tuple(float(v) for v in levels['reduced_region']),
            'n_oxidised': counts['oxidised'],
            'n_reduced': counts['reduced'],
            }
