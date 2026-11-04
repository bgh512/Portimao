"""
Figures of the principal component analysis: the components and example decompositions.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.pca_fitter import TYPE_NAMES


# ---- CONSTANTS -----------------------------------------------------------------------
# Usual reduced-minus-oxidised peaks (nm) of each haem type, drawn as guide lines
REFERENCE_PEAKS = {'a': (604.0, 444.0),
                   'b': (563.0, 430.0),
                   'c': (551.0, 418.0),
                   }


# ---- PLOTTER HELPERS -----------------------------------------------------------------


# ---- _example_drawer -----------------------------------------------------------------
def _example_drawer(main: Axes,
                    lower: Axes,
                    wavelengths: np.ndarray,
                    example: dict,
                    heading: str,
                    names: List[str],
                    colours: List[str],
                    ) -> None:
    """
    ---- Summary ----
    Helper function to draw one decomposed spectrum: the measured spectrum, what each
    component and the offset and scatter add, their sum, and below it the residual.

    ---- Inputs ----
    main : Axes
        Axes for the spectrum and its parts.
    lower : Axes
        Axes for the residual.
    wavelengths : np.ndarray
        Wavelengths (nm), shape (n_wavelengths).
    example : dict
        One example of decomposition_example_finder ('best' or 'worst').
    heading : str
        Start of the title, for example 'Smallest residual'.
    names : List[str]
        Name of each component.
    colours : List[str]
        Colour of each component.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing; draws on the axes.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    main.plot(wavelengths,
              example['spectrum'],
              color='0.65',
              linewidth=2.6,
              label='Measured spectrum',
              )
    for i, name in enumerate(names):
        main.plot(wavelengths,
                  example['contributions'][:, i],
                  color=colours[i],
                  linewidth=1.2,
                  label=name,
                  )
    main.plot(wavelengths,
              example['background'],
              color='0.55',
              linestyle=':',
              linewidth=1.2,
              label='Offset and scatter',
              )
    main.plot(wavelengths,
              example['fitted'],
              color='black',
              linestyle='--',
              linewidth=1.0,
              label='Sum of the fit',
              )
    main.axhline(0, color='0.75', linewidth=0.5)
    when = (f", {example['time_min']:.1f} min" if np.isfinite(example['time_min'])
            else '')
    main.set_title(f"{heading}: {example['name']}{when} (residual RMS "
                   f"{example['rms']:.2g} OD)",
                   loc='left',
                   wrap=True,
                   )
    main.set_ylabel('Attenuation (OD)')
    main.tick_params(labelbottom=False)
    lower.plot(wavelengths, example['residual'], color='0.3', linewidth=1.0)
    lower.axhline(0, color='0.75', linewidth=0.5)
    lower.set_ylabel('Residual (OD)')


# ---- _reference_line_drawer ----------------------------------------------------------
def _reference_line_drawer(ax: Axes,
                           window: tuple,
                           colours: dict,
                           is_labelled: bool,
                           ) -> None:
    """
    ---- Summary ----
    Helper function to draw faint vertical lines at the usual peaks of haems a, b and c
    that fall inside the window, so the peaks of a component can be compared with them.

    ---- Inputs ----
    ax : Axes
        Axes to draw on.
    window : tuple
        (start, end) of the wavelengths shown (nm).
    colours : dict
        {haem type: colour} of the lines.
    is_labelled : bool
        True to write the haem type above each line.

    ---- Globals read ----
    REFERENCE_PEAKS (module constant).

    ---- Outputs ----
    None
        Nothing; draws on the axes.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    shown = []
    for kind, peaks in REFERENCE_PEAKS.items():
        for peak in peaks:
            if window[0] <= peak <= window[1]:
                ax.axvline(peak,
                           color=colours[kind],
                           linestyle='--',
                           linewidth=0.7,
                           alpha=0.45,
                           zorder=0,
                           )
                shown.append((peak, kind))
    if is_labelled and shown:
        shown.sort()
        top = ax.secondary_xaxis('top')
        top.set_xticks([peak for peak, _ in shown],
                       labels=[kind for _, kind in shown],
                       )
        top.tick_params(length=0, pad=1)
        for label, (_, kind) in zip(top.get_xticklabels(), shown):
            label.set_color(colours[kind])


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- pca_example_figure_builder ------------------------------------------------------
def pca_example_figure_builder(examples: dict,
                               names: List[str],
                               colours: List[str],
                               fig: Optional[Figure] = None,
                               ) -> Figure:
    """
    ---- Summary ----
    Main function to show how well the components describe the spectra: the spectrum
    described best and the one described worst, each split into its components, offset
    and scatter, with the residual underneath.

    ---- Inputs ----
    examples : dict
        Result of decomposition_example_finder.
    names : List[str]
        Name of each component.
    colours : List[str]
        Colour of each component.
    fig : Optional[Figure]
        Figure to draw in; None makes a new one.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Figure
        The figure; matplotlib styling is taken from the caller's rcParams. The two
        residual panels share their scale, so their sizes can be compared.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _example_drawer
    """

    # ---- 1 Set up the panels ---------------------------------------------------------
    fig = fig if fig is not None else Figure()
    grid = fig.add_gridspec(4, 1, height_ratios=[3, 1, 3, 1])
    best_main = fig.add_subplot(grid[0])
    best_lower = fig.add_subplot(grid[1], sharex=best_main)
    worst_main = fig.add_subplot(grid[2], sharex=best_main)
    worst_lower = fig.add_subplot(grid[3], sharex=best_main, sharey=best_lower)
    wavelengths = examples['wavelengths']

    # ---- 2 Draw the two examples -----------------------------------------------------
    _example_drawer(best_main,
                    best_lower,
                    wavelengths,
                    examples['best'],
                    'Smallest residual',
                    names,
                    colours,
                    )
    _example_drawer(worst_main,
                    worst_lower,
                    wavelengths,
                    examples['worst'],
                    'Largest residual',
                    names,
                    colours,
                    )
    best_lower.tick_params(labelbottom=False)
    worst_lower.set_xlabel('Wavelength (nm)')
    handles, labels = best_main.get_legend_handles_labels()
    try:  # under the panels, so it never covers the spectra or the title
        fig.legend(handles,
                   labels,
                   loc='outside lower center',
                   ncol=min(len(labels), 4),
                   frameon=False,
                   )
    except ValueError:  # matplotlib older than 3.7
        best_main.legend(frameon=False, ncol=2, fontsize='small')
    fig.suptitle(f"Residual RMS of a typical spectrum: {examples['median_rms']:.2g} OD "
                 f"({examples['n_spectra']} spectra)",
                 )
    return fig


# ---- pca_figure_builder --------------------------------------------------------------
def pca_figure_builder(analysis: dict,
                       result: dict,
                       names: List[str],
                       types: List[str],
                       colours: List[str],
                       type_colours: dict,
                       fig: Optional[Figure] = None,
                       ) -> Figure:
    """
    ---- Summary ----
    Main function to draw the components found, each in a panel of its own, coloured by
    the haem type it looks like, with faint lines at the usual peaks of haems a, b and
    c.

    ---- Inputs ----
    analysis : dict
        Result of component_finder.
    result : dict
        Result of component_builder (the chosen components).
    names : List[str]
        Name of each component.
    types : List[str]
        Haem type of each component (component_classifier).
    colours : List[str]
        Colour of each component.
    type_colours : dict
        {'a', 'b', 'c': colour} of the guide lines.
    fig : Optional[Figure]
        Figure to draw in; None makes a new one.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Figure
        The figure; matplotlib styling (fonts and sizes) is taken from the caller's
        rcParams.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _reference_line_drawer
    """

    # ---- 1 Set up the panels ---------------------------------------------------------
    fig = fig if fig is not None else Figure()
    count = result['count']
    wavelengths = result['wavelengths']
    window = (float(wavelengths[0]), float(wavelengths[-1]))
    axes = fig.subplots(count, 1, sharex=True, squeeze=False)[:, 0]

    # ---- 2 Draw each component -------------------------------------------------------
    for i, ax in enumerate(axes):
        _reference_line_drawer(ax, window, type_colours, is_labelled=i == 0)
        ax.axhline(0, color='0.75', linewidth=0.5)
        ax.plot(wavelengths,
                result['components'][:, i],
                color=colours[i],
                linewidth=1.5,
                )
        ax.set_title(f"{names[i]}: {TYPE_NAMES[types[i]]}, largest peak "
                     f"{result['peaks'][i]:.0f} nm, "
                     f"{result['explained'][i] * 100:.1f}% of the change",
                     loc='left',
                     color=colours[i],
                     )
        ax.set_ylim(min(-0.2, float(np.min(result['components'][:, i])) * 1.1), 1.15)
    axes[-1].set_xlabel('Wavelength (nm)')
    axes[-1].set_xlim(*window)
    fig.supylabel('Component (largest peak = 1)')
    how = ['rotated'] if result['rotated'] else []
    if result['smoothing_nm'] > 0:
        how.append(f"smoothed over {result['smoothing_nm']:g} nm")
    fig.suptitle(f"{count} component{'s' if count != 1 else ''}"
                 f"{' (' + ', '.join(how) + ')' if how else ''}, {window[0]:g} to "
                 f"{window[1]:g} nm, {analysis['n_spectra']} spectra from "
                 f"{len(analysis['counts'])} files",
                 )
    return fig
