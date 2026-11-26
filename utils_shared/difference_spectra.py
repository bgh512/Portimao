"""
The difference spectrum of a file, reduced minus oxidised, its decomposition into the haems and its figure.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, List, Optional, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import BACKDROP_MARK
from utils_shared.spectral_decomposer import spectrum_decomposer


# ---- CONSTANTS -----------------------------------------------------------------------
# OD to mOD
MOD_PER_OD = 1000.0
# The attribute a figure of the difference spectrum carries, so the window knows it has
# no time axis (no time cursor, no edges and no arrows beside its panels).
WAVELENGTH_FIGURE_MARK = 'is_wavelength_figure'
X_LABEL = 'Wavelength (nm)'
Y_LABEL = 'Reduced − oxidised (mOD)'
# A haem band: this far each side of where the shape of the haem is strongest, and how
# see-through it is drawn
BAND_HALF_WIDTH_NM = 2.5
BAND_ALPHA = 0.15
# How far apart stacked spectra are, as a share of the height of the tallest
STACK_GAP_SHARE = 0.75


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
                             is_background_shown: bool = False,
                             ) -> List:
    """
    ---- Summary ----
    Main function to draw the difference spectrum on a figure, in one panel: the
    measured difference in black, each haem in its colour, the fit dashed and the
    residual as a grey line, with a key giving the times of the two regions. The
    difference and the fit have the background taken off, so they sit on zero; with
    the background shown they are drawn with it, and the background dotted. The
    figure is marked as having no time axis.

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
    is_background_shown : bool
        True to draw the difference and the fit with the background, and the
        background itself; False to take it off both.

    ---- Globals read ----
    WAVELENGTH_FIGURE_MARK, X_LABEL, Y_LABEL.

    ---- Outputs ----
    List
        The one set of axes.

    ---- Globals mutated ----
    None. Draws on the figure and sets its WAVELENGTH_FIGURE_MARK attribute (side
    effects).

    ---- Equations ----
    Without the background: measured = difference - background, and fit = the sum
    of the haems (MATHS.md section 9).

    ---- Helpers ----
    None.
    """

    # ---- 1 The one panel -------------------------------------------------------------
    fig.clf()
    main = fig.add_subplot(1, 1, 1)
    wavelengths = decomposition['wavelengths_nm']

    # ---- 2 The difference, each haem, the background, the fit and the residual -------
    taken_off = (0.0
                 if is_background_shown
                 else np.asarray(decomposition['background_mOD'], dtype=float)
                 )
    main.plot(wavelengths,
              np.asarray(decomposition['measured_mOD'], dtype=float) - taken_off,
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
    if is_background_shown:
        main.plot(wavelengths,
                  decomposition['background_mOD'],
                  color=style['background_colour'],
                  linestyle=':',
                  linewidth=style['part_line_width'],
                  label='Background',
                  )
    main.plot(
        wavelengths,
        np.asarray(decomposition['fit_mOD'], dtype=float) - taken_off,
        color=style['residual_colour'],
        linestyle='--',
        linewidth=style['fitted_line_width'],
        label='Fit (haems + background)' if is_background_shown else 'Fit (haems)',
        )
    main.plot(wavelengths,
              decomposition['residual_mOD'],
              color=style['measured_colour'],
              linewidth=style['residual_line_width'],
              label='Residual',
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
    main.set_xlabel(X_LABEL)
    setattr(fig, WAVELENGTH_FIGURE_MARK, True)
    return [main]


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


# ---- haem_bands_drawer ---------------------------------------------------------------
def haem_bands_drawer(ax: Axes,
                      bands: Dict[str, Tuple[float, float]],
                      colours: Dict[str, str],
                      alpha: float = BAND_ALPHA,
                      ) -> None:
    """
    ---- Summary ----
    Main function to shade the band of each haem behind the spectra of a plot, in the
    colour of the haem, to show where each haem appears. The bands are marked as a
    backdrop, so a legend may sit over them.

    ---- Inputs ----
    ax : Axes
        The axes, with the wavelength on the x axis.
    bands : Dict[str, Tuple[float, float]]
        {haem name: (start, end) of its band in nm} (haem_bands_finder).
    colours : Dict[str, str]
        {haem name: colour} (config.haem_colour_mapper).
    alpha : float
        How see-through a band is, 0 (unseen) to 1 (solid).

    ---- Globals read ----
    BAND_ALPHA; BACKDROP_MARK (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on the axes and leaves its x limits as they were (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    x_limits = ax.get_xlim()
    for name, (start, end) in bands.items():
        band = ax.axvspan(start,
                          end,
                          color=colours.get(name, '0.5'),
                          alpha=alpha,
                          linewidth=0,
                          zorder=0,
                          )
        setattr(band, BACKDROP_MARK, True)
    ax.set_xlim(x_limits)


# ---- haem_bands_finder ---------------------------------------------------------------
def haem_bands_finder(fit: dict,
                      half_width_nm: float = BAND_HALF_WIDTH_NM,
                      ) -> Dict[str, Tuple[float, float]]:
    """
    ---- Summary ----
    Main function to find the band of each haem of a fit: a strip of wavelengths
    round the place where the shape of the haem in the fit file is strongest. The
    bands come from the fit alone, so they are the same on every plot and for every
    file, also for a haem a file has none of.

    ---- Inputs ----
    fit : dict
        The fit in use: 'data' (the fit table, a wavelength column then a shape
        column for each haem) and 'haem_list' (the haem names in that order).
    half_width_nm : float
        How far the band reaches each side of the strongest place (nm).

    ---- Globals read ----
    BAND_HALF_WIDTH_NM.

    ---- Outputs ----
    Dict[str, Tuple[float, float]]
        {haem name: (start, end) of its band in nm}, in the order of the fit; a haem
        whose shape holds no number, or only zeros, has no band.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    centre = the wavelength where |S(w)| is largest; band = centre - half_width_nm
    to centre + half_width_nm (MATHS.md section 9).

    ---- Helpers ----
    None.
    """

    data = fit['data']
    bands = {}
    for place, name in enumerate(fit['haem_list']):
        wavelengths = pd.to_numeric(data.iloc[:, 2 * place], errors='coerce').to_numpy()
        shape = pd.to_numeric(data.iloc[:, 2 * place + 1], errors='coerce').to_numpy()
        is_number = np.isfinite(wavelengths) & np.isfinite(shape)
        if not is_number.any() or np.abs(shape[is_number]).max() == 0:
            continue
        centre = float(wavelengths[is_number][np.abs(shape[is_number]).argmax()])
        bands[name] = (centre - half_width_nm, centre + half_width_nm)
    return bands


# ---- spectra_averager ----------------------------------------------------------------
def spectra_averager(spectra: Sequence[Tuple[np.ndarray, np.ndarray]],
                     ) -> Tuple[np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Main function to average the spectra of several files into one: each is read at
    the wavelengths of the first, then the mean is taken at each wavelength.

    ---- Inputs ----
    spectra : Sequence[Tuple[np.ndarray, np.ndarray]]
        (wavelengths in nm, rising; values) of each spectrum, each of shape
        (n_wavelengths,); at least one.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray]
        (the wavelengths of the first spectrum, the mean at each). Raises ValueError
        for no spectrum.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A spectrum is read at a wavelength w between two of its own, w1 and w2, on the
    straight line between them: y = y1 + (y2 - y1) x (w - w1) / (w2 - w1). A
    wavelength outside a spectrum is left out of the mean there. mean(w) = the sum of
    the spectra read at w / how many there are (MATHS.md section 9).

    ---- Helpers ----
    None.
    """

    if not spectra:
        raise ValueError('There is no spectrum to average.')
    wavelengths = np.asarray(spectra[0][0], dtype=float)
    rows = [np.interp(wavelengths,
                      np.asarray(own, dtype=float),
                      np.asarray(values, dtype=float),
                      left=np.nan,
                      right=np.nan,
                      )
            for own, values in spectra
            ]
    stacked = np.vstack(rows)
    counts = np.isfinite(stacked).sum(axis=0)  # the first spectrum is always there
    return wavelengths, np.nansum(stacked, axis=0) / counts


# ---- spectra_stacker -----------------------------------------------------------------
def spectra_stacker(spectra: Sequence[Tuple[np.ndarray, np.ndarray]],
                    band: Optional[Tuple[float, float]] = None,
                    gap_share: float = STACK_GAP_SHARE,
                    ) -> List[np.ndarray]:
    """
    ---- Summary ----
    Main function to stack spectra for a waterfall: each is moved up or down, never
    stretched, until its highest point inside a band is at 0, so the peaks line up;
    then the spectra are spread out, the first at the top.

    ---- Inputs ----
    spectra : Sequence[Tuple[np.ndarray, np.ndarray]]
        (wavelengths in nm, values) of each spectrum, from the top down.
    band : Optional[Tuple[float, float]]
        (start, end) in nm of the band the spectra are lined up on; None, or a band
        a spectrum has no point in, lines that spectrum up on its highest point
        anywhere.
    gap_share : float
        How far apart two neighbours are, as a share of the height of the tallest
        spectrum.

    ---- Globals read ----
    STACK_GAP_SHARE.

    ---- Outputs ----
    List[np.ndarray]
        The values of each spectrum as drawn, in the order given.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    lined up = y - (the highest y inside the band); height = highest - lowest of a
    spectrum; gap = gap_share x the largest height (1 when every spectrum is flat);
    drawn_i = lined up_i + (n - 1 - i) x gap, i from 0 for the first of n (MATHS.md
    section 9).

    ---- Helpers ----
    None.
    """

    lined_up = []
    for wavelengths, values in spectra:
        wavelengths = np.asarray(wavelengths, dtype=float)
        values = np.asarray(values, dtype=float)
        inside = np.isfinite(values)
        if band is not None:
            in_band = inside & (wavelengths >= band[0]) & (wavelengths <= band[1])
            inside = in_band if in_band.any() else inside
        lined_up.append(values - values[inside].max())
    heights = [np.nanmax(values) - np.nanmin(values) for values in lined_up]
    gap = gap_share * max(heights, default=0.0) or 1.0
    count = len(lined_up)
    return [values + (count - 1 - place) * gap for place, values in enumerate(lined_up)]
