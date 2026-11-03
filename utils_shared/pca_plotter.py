"""
Figure of the components found by the principal component analysis.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
from matplotlib.figure import Figure


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- pca_figure_builder --------------------------------------------------------------
def pca_figure_builder(analysis: dict,
                       result: dict,
                       names: List[str],
                       colours: List[str],
                       fig: Optional[Figure] = None,
                       ) -> Figure:
    """
    ---- Summary ----
    Main function to draw the components found: their spectra (top), the share of the
    variance each principal component explains (bottom left) and the residual left
    after each number of components (bottom right), with the chosen number marked.

    ---- Inputs ----
    analysis : dict
        Result of component_finder.
    result : dict
        Result of component_builder (the chosen components).
    names : List[str]
        Name of each component.
    colours : List[str]
        Colours to give the components, repeated when there are more components.
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
    Residual RMS after k components = sqrt((total variance - sum of the first k
    eigenvalues) / number of values).

    ---- Helpers ----
    None.
    """

    # ---- 1 Set up the panels ---------------------------------------------------------
    fig = fig if fig is not None else Figure()
    grid = fig.add_gridspec(2, 2, height_ratios=[2, 1.2])
    top = fig.add_subplot(grid[0, :])
    bars = fig.add_subplot(grid[1, 0])
    residual = fig.add_subplot(grid[1, 1])
    count = result['count']
    wavelengths = result['wavelengths']

    # ---- 2 Draw the components -------------------------------------------------------
    for i in range(count):
        top.plot(wavelengths,
                 result['components'][:, i],
                 color=colours[i % len(colours)],
                 label=f"{names[i]} ({result['explained'][i] * 100:.1f}%)",
                 )
    top.axhline(0, color='0.6', linewidth=0.5)
    top.set_xlabel('Wavelength (nm)')
    top.set_ylabel('Component (peak = 1)')
    top.set_title(f"{count} component{'s' if count != 1 else ''} found in "
                  f"{analysis['window'][0]:g}-{analysis['window'][1]:g} nm "
                  f"({analysis['n_spectra']} spectra, {len(analysis['counts'])} files)",
                  )
    top.legend(frameon=False, ncol=min(count, 5))

    # ---- 3 Draw the variance and the residual ----------------------------------------
    values = analysis['eigenvalues']
    shares = values / analysis['total_variance'] * 100
    places = np.arange(1, len(values) + 1)
    bars.bar(places,
             shares,
             color=['0.35' if k <= count else '0.8' for k in places],
             )
    bars.set_yscale('log')
    bars.set_xlabel('Principal component')
    bars.set_ylabel('Variance explained (%)')
    bars.set_xticks(places)
    left = np.clip(analysis['total_variance'] - np.cumsum(values), 0.0, None)
    rms = np.maximum(np.sqrt(left / analysis['n_values']), 1e-12)
    residual.plot(places, rms, color='0.35', marker='o', markersize=3)
    residual.plot([count], [rms[count - 1]], color='#d62728', marker='o', markersize=5)
    residual.set_yscale('log')
    residual.set_xlabel('Number of components')
    residual.set_ylabel('Residual RMS (OD)')
    residual.set_xticks(places)
    return fig
