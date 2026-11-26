"""
Tests of the ready-made templates of the dataset figure shipped in layouts/: each reads back, leaves the pick of an experiment to the user, finds the sets of its plots in the two sample datasets and is drawn off screen.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Dict, List

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.dataset_setup import setup_builder
from utils_shared.figure_page import (figure_page_drawer,
                                      FIRST_TYPES,
                                      FigurePage,
                                      template_reader,
                                      )
from utils_shared.journal_files import STANDARD_SPEC
from utils_shared.page_data import EXPERIMENT_ROLE, plot_sets_lister, SET_TYPES
from utils_shared.page_plots import (NO_RESPONSE,
                                     NO_VALUES,
                                     NO_WATERFALL,
                                     NOT_PICKED,
                                     NOT_THERE,
                                     )
from utils_shared.schema import TIME_COLUMN


# ---- CONSTANTS -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ROOT / 'layouts'
TEMPLATES = ('Haem and OCR response', 'Time response', 'Two standard experiments')
# the plots of one experiment, which a ready-made template leaves the user to pick
PICKED_TYPES = ('P1', 'P2', 'P7')
HAEMS = ['Cyt $b_H$', 'Cyt cc']
# the file names of the two sample datasets, so the tests run without the folders
HOURS = (0, 7, 24, 31, 48, 55, 72)
TIME_NAMES = [f'{group}_{hours}hours'
              for group in ('control', 'knockdown')
              for hours in HOURS
              ]
ORDERS = ('bd_then_kcn', 'kcn_then_bd')
RESPONSE_NAMES = [f'{group}-{order}-run{run}'
                  for group in ('control', 'knockdown')
                  for order in ORDERS
                  for run in (1, 2, 3)
                  ]
# the sentences a plot writes in its cells when it has nothing to draw
SENTENCES = (NO_RESPONSE, NO_VALUES, NO_WATERFALL, NOT_PICKED, NOT_THERE)


# ---- HELPERS -------------------------------------------------------------------------


# ---- _experiment_maker ---------------------------------------------------------------
def _experiment_maker(name: str, level: float) -> dict:
    """
    ---- Summary ----
    Helper function to make the slim copy of one made-up experiment: an OCR that
    halves at the first addition (10 minutes) and falls to a tenth at the second (15
    minutes), two haems that follow it, three averaging regions and a difference
    spectrum with one peak.

    ---- Inputs ----
    name : str
        The experiment name.
    level : float
        Its OCR in the baseline (µM min⁻¹).

    ---- Globals read ----
    HAEMS; TIME_COLUMN (imported).

    ---- Outputs ----
    dict
        The slim copy (page_experiment, DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    times = np.arange(0.0, 20.0, 0.1)
    ocr = np.where(times < 10.0, level, np.where(times < 15.0, level / 2, level / 10))
    percent = pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr / level * 100.0})
    percent.attrs['baseline_percent'] = {'baseline_mean': {'VoO2': level}}
    haems = pd.DataFrame({TIME_COLUMN: times,
                          HAEMS[0]: -0.4 * (ocr - level),
                          HAEMS[1]: 0.25 * (ocr - level),
                          },
                         )
    wavelengths = np.arange(500.0, 601.0, 5.0)
    peak = np.where(wavelengths == 560.0, level, 0.0)
    return {'experiment_name': name,
            'VoO2': pd.DataFrame({TIME_COLUMN: times, 'VoO2': ocr}),
            'VoO2_baseline': percent,
            'haem_delta_abs': haems,
            'metadata': {'events': [{'time': 10.0, 'label': 'KCN'},
                                    {'time': 15.0, 'label': 'Dithionite'},
                                    ],
                         },
            'averages': {'windows': {'average0': {'start_time': 2.0, 'end_time': 8.0},
                                     'average1': {'start_time': 11.0,
                                                  'end_time': 14.0,
                                                  },
                                     'average2': {'start_time': 16.0,
                                                  'end_time': 19.0,
                                                  },
                                     },
                         },
            'difference': {'wavelengths_nm': wavelengths,
                           'difference_mOD': peak,
                           'oxidised_region': (2.0, 8.0),
                           'reduced_region': (16.0, 19.0),
                           },
            'difference_parts': {'wavelengths_nm': wavelengths,
                                 'measured_mOD': peak,
                                 'haems_mOD': {HAEMS[0]: peak, HAEMS[1]: 0.0 * peak},
                                 'background_mOD': 0.0 * peak,
                                 'fit_mOD': peak,
                                 'residual_mOD': 0.0 * peak,
                                 },
            'haem_bands': {HAEMS[0]: (557.5, 562.5), HAEMS[1]: (547.5, 552.5)},
            }


# ---- _sentences_reader ---------------------------------------------------------------
def _sentences_reader(page: FigurePage, names: List[str]) -> List[str]:
    """
    ---- Summary ----
    Helper function to draw a page off screen on made-up experiments of the names
    given, and read what each plot wrote in its cells in place of a plot.

    ---- Inputs ----
    page : FigurePage
        The page.
    names : List[str]
        The experiment names of the dataset.

    ---- Globals read ----
    HAEMS, SENTENCES; settings.DEFAULT_ANSWERS; STANDARD_SPEC (imported).

    ---- Outputs ----
    List[str]
        For each plot in the order of the page: its sentence, or '' when it was
        drawn.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The OCR of the experiment in place i of the names is 5 + i µM min⁻¹ in the
    baseline, so the experiments of a set differ.

    ---- Helpers ----
    _experiment_maker
    figure_page_drawer
    setup_builder
    """

    experiments = {name: _experiment_maker(name, 5.0 + place)
                   for place, name in enumerate(names)
                   }
    answers = dict(settings.DEFAULT_ANSWERS, decompose=True, haems=list(HAEMS))
    fig, axes = figure_page_drawer(page,
                                   STANDARD_SPEC,
                                   setup_builder(names),
                                   experiments,
                                   answers,
                                   )
    written = []
    for place in range(len(page.plots)):
        texts = [' '.join(text.get_text().split()) for text in axes[place].texts]
        written.append(next((text for text in texts if text in SENTENCES), ''))
    plt.close(fig)
    return written


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_each_ready_template_reads_back_without_a_pick ------------------------------
@pytest.mark.parametrize('name', TEMPLATES)
def test_each_ready_template_reads_back_without_a_pick(name: str) -> None:
    """
    ---- Summary ----
    Main function to check that each shipped template is read as a page whose plots
    are all of plot types that are built, and that none of them picks an experiment:
    the user picks the data of each plot in its form.

    ---- Inputs ----
    name : str
        The template's name.

    ---- Globals read ----
    LAYOUTS; EXPERIMENT_ROLE, FIRST_TYPES (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    template_reader
    """

    page = template_reader(LAYOUTS / f'{name}.json')
    assert page.plots
    assert all(plot.plot_type in FIRST_TYPES for plot in page.plots)
    assert all(EXPERIMENT_ROLE not in plot.roles for plot in page.plots)


# ---- test_the_shipped_templates_are_the_three ----------------------------------------
def test_the_shipped_templates_are_the_three() -> None:
    """
    ---- Summary ----
    Main function to check that the layouts folder ships exactly the three ready-made
    templates, under the names the window lists them by.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LAYOUTS, TEMPLATES.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert sorted(path.stem for path in LAYOUTS.glob('*.json')) == sorted(TEMPLATES)


# ---- test_the_time_response_finds_its_sets -------------------------------------------
def test_the_time_response_finds_its_sets() -> None:
    """
    ---- Summary ----
    Main function to check the Time response template on the file names of the time
    response dataset, worked out by hand: its two waterfalls have one line per time
    point, the first of the controls and the second of the knockdowns; drawn on
    made-up experiments, the waterfalls are drawn and the four plots of one
    experiment and the three difference spectra ask for their experiment.

    ---- Inputs ----
    None.

    ---- Globals read ----
    HOURS, LAYOUTS, TIME_NAMES; NOT_PICKED (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Seven time points and two groups: each waterfall has seven sets of one
    experiment, <group>_<hours>hours.

    ---- Helpers ----
    _sentences_reader
    plot_sets_lister
    setup_builder
    template_reader
    """

    page = template_reader(LAYOUTS / 'Time response.json')
    setup = setup_builder(TIME_NAMES)
    assert [plot.plot_type for plot in page.plots] == ['P3',
                                                       'P1',
                                                       'P3',
                                                       'P1',
                                                       'P2',
                                                       'P2',
                                                       'P2',
                                                       ]
    for place, group in ((0, 'control'), (2, 'knockdown')):
        sets = plot_sets_lister(setup, page.plots[place].roles)
        assert [entry['names'] for entry in sets] == [[f'{group}_{hours}hours']
                                                      for hours in HOURS
                                                      ]
    assert _sentences_reader(page, TIME_NAMES) == ['',
                                                   NOT_PICKED,
                                                   '',
                                                   NOT_PICKED,
                                                   NOT_PICKED,
                                                   NOT_PICKED,
                                                   NOT_PICKED,
                                                   ]


# ---- test_the_haem_and_ocr_response_finds_its_sets -----------------------------------
def test_the_haem_and_ocr_response_finds_its_sets() -> None:
    """
    ---- Summary ----
    Main function to check the Haem and OCR response template on the file names of
    the haem and OCR dataset, worked out by hand: the bar chart has the six controls
    and the six knockdowns; each response has the three runs of each strain in one
    order of additions, the left ones the first order and the right ones the second;
    drawn on made-up experiments, every plot is drawn with nothing to pick.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LAYOUTS, ORDERS, RESPONSE_NAMES.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Two strains, two orders and three runs: 12 files; a set of the bar chart is 2 x 3
    = 6 files, a set of a response 3.

    ---- Helpers ----
    _sentences_reader
    plot_sets_lister
    setup_builder
    template_reader
    """

    page = template_reader(LAYOUTS / 'Haem and OCR response.json')
    setup = setup_builder(RESPONSE_NAMES)
    assert [plot.plot_type for plot in page.plots] == ['P9', 'P11', 'P11', 'P11', 'P11']
    bars = plot_sets_lister(setup, page.plots[0].roles)
    assert [entry['names'] for entry in bars] == [RESPONSE_NAMES[:6],
                                                  RESPONSE_NAMES[6:],
                                                  ]
    for place, order in ((1, ORDERS[0]),
                         (2, ORDERS[1]),
                         (3, ORDERS[0]),
                         (4, ORDERS[1]),
                         ):
        sets = plot_sets_lister(setup, page.plots[place].roles)
        assert [entry['names'] for entry in sets] == [
            [f'{group}-{order}-run{run}' for run in (1, 2, 3)]
            for group in ('control', 'knockdown')
            ]
    assert _sentences_reader(page, RESPONSE_NAMES) == ['', '', '', '', '']


# ---- test_the_two_standard_experiments_ask_for_their_experiments ---------------------
def test_the_two_standard_experiments_ask_for_their_experiments() -> None:
    """
    ---- Summary ----
    Main function to check the Two standard experiments template: two Standard
    experiments side by side, each over the whole height and half the width, on the
    same scales, each asking for its experiment until one is picked.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LAYOUTS, RESPONSE_NAMES; NOT_PICKED (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _sentences_reader
    template_reader
    """

    page = template_reader(LAYOUTS / 'Two standard experiments.json')
    assert [(plot.plot_type, plot.row, plot.column, plot.n_rows, plot.n_columns)
            for plot in page.plots
            ] == [('P1', 0, 0, 6, 3), ('P1', 0, 3, 6, 3)]
    assert all(plot.roles == {'same_scales': 'yes'} for plot in page.plots)
    assert _sentences_reader(page, RESPONSE_NAMES) == [NOT_PICKED, NOT_PICKED]


# ---- test_the_templates_fit_the_sample_folders ---------------------------------------
@pytest.mark.parametrize('name, folder',
                         (('Time response', 'data_time_response'),
                          ('Haem and OCR response', 'data_OCR_and_haem'),
                          ('Two standard experiments', 'data_OCR_and_haem'),
                          ),
                         )
def test_the_templates_fit_the_sample_folders(name: str, folder: str) -> None:
    """
    ---- Summary ----
    Main function to check each template on the files that are in its sample data
    folder: every plot of sets finds experiments, and the page is drawn off screen
    with only the plots of one experiment left to pick. Skipped without the folder
    (the sample data is not in git).

    ---- Inputs ----
    name : str
        The template's name.
    folder : str
        The sample data folder, in the program folder.

    ---- Globals read ----
    LAYOUTS, PICKED_TYPES, ROOT; NOT_PICKED, SET_TYPES (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _sentences_reader
    plot_sets_lister
    setup_builder
    template_reader
    """

    names = sorted(path.stem for path in (ROOT / folder).glob('*.paf'))
    if not names:
        pytest.skip(f'{folder}/ is not here')
    page = template_reader(LAYOUTS / f'{name}.json')
    setup = setup_builder(names)
    for plot in page.plots:
        if plot.plot_type in SET_TYPES:
            sets = plot_sets_lister(setup, plot.roles)
            assert sets and all(entry['names'] for entry in sets)
    assert _sentences_reader(page, names) == [
        NOT_PICKED if plot.plot_type in PICKED_TYPES else '' for plot in page.plots
        ]
