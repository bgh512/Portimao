"""
Tests of what the page of a dataset figure is given of the dataset, worked out by hand on made-up experiments.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import utils_shared.page_data as page_data
from utils_shared.figure_page import (FigurePage,
                                      PagePlot,
                                      plot_placer,
                                      template_reader,
                                      template_saver,
                                      )
from utils_shared.page_data import (caption_lines_builder,
                                    colour_namer,
                                    colour_shader,
                                    experiment_field_maker,
                                    experiment_role_maker,
                                    experiment_slimmer,
                                    form_fields_lister,
                                    form_roles_reader,
                                    group_choices_lister,
                                    group_columns_lister,
                                    group_fields_lister,
                                    page_experiments_lister,
                                    plot_sets_lister,
                                    role_experiment_finder,
                                    tick_field_maker,
                                    )


# ---- CONSTANTS -----------------------------------------------------------------------
BLUE, RED_ORANGE = '#0072b2', '#d55e00'
C1_ROLE = 'Group 1: 1, Group 2: 1, time point: 1, replicate: 1'
C2_ROLE = 'Group 1: 1, Group 2: 1, time point: 1, replicate: 2'
K1_ROLE = 'Group 1: 2, Group 2: 1, time point: 2, replicate: 1'
K2_ROLE = 'Group 1: 2, Group 2: 2, time point: 0, replicate: 1'


# ---- MAKERS --------------------------------------------------------------------------


# ---- _setup_maker --------------------------------------------------------------------
def _setup_maker() -> dict:
    """
    ---- Summary ----
    Helper function to make the set-up of a made-up dataset of five experiments: two
    controls (order A, 2 h, runs 1 and 2), a knockdown (order A, 7 h), a knockdown
    (order B, no time point) and a control that is not in use.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BLUE, RED_ORANGE.

    ---- Outputs ----
    dict
        The set-up table (dataset_setup, DATA_FORMAT.md); Group 1 is named "strain".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    rows = [('c1', True, 'control', 'order A', '2 h', 1),
            ('c2', True, 'control', 'order A', '2 h', 2),
            ('k1', True, 'knockdown', 'order A', '7 h', 1),
            ('k2', True, 'knockdown', 'order B', '', None),
            ('x', False, 'control', 'order A', '2 h', 3),
            ]
    return {'group_names': ['strain', ''],
            'colours': {'control': BLUE, 'knockdown': RED_ORANGE},
            'rows': [{'name': name,
                      'use': use,
                      'group_1': group_1,
                      'group_2': group_2,
                      'time_point': time_point,
                      'run': run,
                      }
                     for name, use, group_1, group_2, time_point, run in rows
                     ],
            }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_the_slim_copy_of_an_experiment ---------------------------------------------
def test_the_slim_copy_of_an_experiment(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the slim copy of a processed experiment: its traces, its
    additions, averages and levels are kept as they are, the whole spectra are left
    out, and the difference spectrum and the mean spectrum of each averaging region
    are as worked out by hand; a region with no spectrum has no mean, and a file
    without spectra of that spectrometer has neither. With the fit of the run it
    also keeps the haem bands and the difference split into its haems (the
    decomposition stood in for).

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Stands in for the decomposition.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Six spectra at 0 to 5 min of three wavelengths; spectrum i is (0.001 i, 0.002 i,
    0) OD. The baseline (0 to 1 min) holds spectra 0 and 1: mean (0.0005, 0.001, 0) OD
    = (0.5, 1, 0) mOD. The region of 2 to 3 min: (2.5, 5, 0) mOD. Reduced (4 to 5
    min) is (4.5, 9, 0) mOD and oxidised (0 to 1 min) is (0.5, 1, 0) mOD, so reduced
    minus oxidised is (4, 8, 0) mOD.

    ---- Helpers ----
    None.
    """

    # ---- 1 A file with spectra -------------------------------------------------------
    trace = pd.DataFrame({'Time (min)': [0.0, 1.0], 'VoO2': [5.0, 6.0]})
    spectra = np.array([[0.001 * i, 0.002 * i, 0.0] for i in range(6)])
    windows = {'average0': {'start_time': 0.0, 'end_time': 1.0},
               'average1': {'start_time': 2.0, 'end_time': 3.0},
               'average2': {'start_time': 10.0, 'end_time': 11.0},
               }
    experiment = {'experiment_name': 'run1',
                  'metadata': {'events': [{'label': 'KCN', 'time': 2.0}]},
                  'VoO2': trace,
                  'haem_levels': {'oxidised': {},
                                  'reduced': {},
                                  'oxidised_region': (0.0, 1.0),
                                  'reduced_region': (4.0, 5.0),
                                  },
                  'averages': {'windows': windows},
                  'raw_spectra': {'Cyt': {'wavelengths': [540.0, 550.0, 560.0],
                                          'time': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                                          'attenuation': spectra,
                                          },
                                  },
                  }
    slim = experiment_slimmer(experiment, 'Cyt')
    assert 'raw_spectra' not in slim
    assert slim['VoO2'] is trace and slim['experiment_name'] == 'run1'
    assert slim['metadata'] is experiment['metadata']
    assert slim['averages'] is experiment['averages']
    assert slim['haem_levels'] is experiment['haem_levels']
    assert 'haem_abs' not in slim  # a table the file does not have
    regions = slim['region_spectra']
    assert regions['dataset'] == 'Cyt'
    assert list(regions['wavelengths_nm']) == [540.0, 550.0, 560.0]
    assert set(regions['mean_mOD']) == {'average0', 'average1'}
    assert regions['mean_mOD']['average0'] == pytest.approx([0.5, 1.0, 0.0])
    assert regions['mean_mOD']['average1'] == pytest.approx([2.5, 5.0, 0.0])
    assert slim['difference']['difference_mOD'] == pytest.approx([4.0, 8.0, 0.0])
    assert (slim['difference']['n_oxidised'], slim['difference']['n_reduced']) == (2, 2)

    # ---- 2 Without both regions, and without spectra ---------------------------------
    no_levels = {key: value for key, value in experiment.items() if key != 'haem_levels'}
    slim = experiment_slimmer(no_levels, 'Cyt')
    assert slim['difference'] is None and slim['region_spectra'] is not None
    for dataset in ('NIR', None):
        slim = experiment_slimmer(experiment, dataset)
        assert slim['difference'] is None and slim['region_spectra'] is None
    bare = experiment_slimmer({'experiment_name': 'run2', 'metadata': {}}, 'Cyt')
    assert bare == {'experiment_name': 'run2',
                    'metadata': {},
                    'difference': None,
                    'difference_parts': None,
                    'haem_bands': None,
                    'region_spectra': None,
                    }

    # ---- 3 With the fit of the run ---------------------------------------------------
    # the bands come from the fit alone; the parts of the difference are those the
    # decomposition gives for the fit, the background and the scale of the run
    fit = {'haem_list': ['A'],
           'data': pd.DataFrame({'A': [540.0, 550.0, 560.0],
                                 'A response': [0.0, 2.0, 1.0],
                                 },
                                ),
           }
    monkeypatch.setattr(page_data,
                        'difference_decomposer',
                        lambda *given: {'given': given},
                        )
    slim = experiment_slimmer(experiment, 'Cyt', fit, 'scatter_1', 1000.0)
    assert slim['haem_bands'] == {'A': (547.5, 552.5)}
    assert slim['difference_parts'] == {'given': (slim['difference'],
                                                  fit,
                                                  'scatter_1',
                                                  1000.0,
                                                  ),
                                        }
    slim = experiment_slimmer(no_levels, 'Cyt', fit, 'scatter_1', 1000.0)
    assert slim['difference_parts'] is None and slim['haem_bands'] is not None
    slim = experiment_slimmer(experiment, None, fit, 'scatter_1', 1000.0)
    assert slim['difference_parts'] is None and slim['haem_bands'] is not None


# ---- test_an_experiment_and_its_role -------------------------------------------------
def test_an_experiment_and_its_role(tmp_path: Path) -> None:
    """
    ---- Summary ----
    Main function to check the role of an experiment, both ways: the place of each of
    its labels in its column and its replicate, none for an experiment not in use;
    the experiment a role fits, none for a role nothing fits or that cannot be read;
    the same role on a dataset with other labels; and a template that keeps it.

    ---- Inputs ----
    tmp_path : Path
        Folder given by pytest, for the template.

    ---- Globals read ----
    C1_ROLE, C2_ROLE, K1_ROLE, K2_ROLE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The labels in the order first seen: Group 1 control (1), knockdown (2); Group 2
    order A (1), order B (2); time point 2 h (1), 7 h (2); a blank cell is 0. c1 and
    c2 share their three labels, so they are replicates 1 and 2 by run number.

    ---- Helpers ----
    _setup_maker
    """

    setup = _setup_maker()
    roles = {name: experiment_role_maker(setup, name) for name in ('c1', 'c2', 'k1', 'k2')}
    assert roles == {'c1': C1_ROLE, 'c2': C2_ROLE, 'k1': K1_ROLE, 'k2': K2_ROLE}
    assert experiment_role_maker(setup, 'x') is None  # not in use
    assert experiment_role_maker(setup, 'gone') is None
    assert experiment_role_maker(None, 'c1') is None
    for name, role in roles.items():
        assert role_experiment_finder(setup, role) == name
    nothing_fits = 'Group 1: 3, Group 2: 1, time point: 1, replicate: 1'
    for role in (nothing_fits, 'c1.paf', '', C1_ROLE + ' and more'):
        assert role_experiment_finder(setup, role) is None
    assert role_experiment_finder(None, C1_ROLE) is None

    # the same role on a dataset whose labels are spelt differently
    other = {'group_names': ['', ''],
             'colours': {},
             'rows': [{'name': 'wild type 1',
                       'use': True,
                       'group_1': 'WT',
                       'group_2': 'succinate first',
                       'time_point': '1 h',
                       'run': 1,
                       },
                      {'name': 'mutant 1',
                       'use': True,
                       'group_1': 'mutant',
                       'group_2': 'succinate first',
                       'time_point': '4 h',
                       'run': 1,
                       },
                      ],
             }
    assert role_experiment_finder(other, C1_ROLE) == 'wild type 1'
    assert role_experiment_finder(other, K1_ROLE) == 'mutant 1'
    assert role_experiment_finder(other, C2_ROLE) is None

    # a template takes the role, as it names no file
    page = plot_placer(FigurePage(),
                       PagePlot('P1', 0, 0, roles={'experiment': K1_ROLE}),
                       )
    path = template_saver(page, tmp_path, 'one experiment')
    assert template_reader(path) == page


# ---- test_the_sets_of_a_plot ---------------------------------------------------------
def test_the_sets_of_a_plot() -> None:
    """
    ---- Summary ----
    Main function to check the sets a plot shows for each choice of its group
    drop-downs: split by Group 1 when nothing is chosen, all together, only one
    label, split by two columns, and a label the dataset does not have.

    ---- Inputs ----
    None.

    ---- Globals read ----
    BLUE, RED_ORANGE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Group 2: order A is the first label (solid line), order B the second (dashed).
    Time point: 2 h is the first of two (shade 0), 7 h the last (shade 0.7). The
    knockdown colour #d55e00 (213, 94, 0) with 0.7 of white: 213 + 42 x 0.7 = 242.4,
    94 + 161 x 0.7 = 206.7, 0 + 255 x 0.7 = 178.5, so (242, 207, 178) = #f2cfb2.

    ---- Helpers ----
    _setup_maker
    """

    setup = _setup_maker()

    # ---- 1 Nothing chosen: split by Group 1 ------------------------------------------
    sets = plot_sets_lister(setup, {})
    assert [(s['name'], s['names']) for s in sets] == [('control', ['c1', 'c2']),
                                                       ('knockdown', ['k1', 'k2']),
                                                       ]
    assert [s['colour'] for s in sets] == [BLUE, RED_ORANGE]
    assert all(s['line_style'] == '-' and s['shade'] == 0.0 for s in sets)
    assert sets[0]['labels'] == {'group_1': 'control', 'group_2': '', 'time_point': ''}

    # ---- 2 All together --------------------------------------------------------------
    sets = plot_sets_lister(setup, {'group_1': 'All together'})
    assert len(sets) == 1
    assert sets[0]['name'] == 'All experiments'
    assert sets[0]['names'] == ['c1', 'c2', 'k1', 'k2']
    assert sets[0]['colour'] == '#000000'

    # ---- 3 Only the knockdown, split by Group 2 --------------------------------------
    sets = plot_sets_lister(setup, {'group_1': 'Only label 2', 'group_2': 'Split'})
    assert [(s['name'], s['names'], s['line_style']) for s in sets] == [
        ('order A', ['k1'], '-'),
        ('order B', ['k2'], '--'),
        ]
    assert all(s['base_colour'] == RED_ORANGE for s in sets)
    assert sets[1]['labels'] == {'group_1': 'knockdown',
                                 'group_2': 'order B',
                                 'time_point': '',
                                 }

    # ---- 4 Split by Group 1 and the time point ---------------------------------------
    sets = plot_sets_lister(setup, {'time_point': 'Split'})
    assert [(s['name'], s['names']) for s in sets] == [('control · 2 h', ['c1', 'c2']),
                                                       ('knockdown · 7 h', ['k1']),
                                                       ('knockdown', ['k2']),
                                                       ]
    assert [s['shade'] for s in sets] == pytest.approx([0.0, 0.7, 0.0])
    assert [s['colour'] for s in sets] == [BLUE, '#f2cfb2', RED_ORANGE]
    assert colour_shader('#000000', 0.5) == '#808080'
    assert colour_shader(BLUE, 0.0) == BLUE

    # ---- 5 A label the dataset does not have, and no set-up --------------------------
    assert plot_sets_lister(setup, {'group_1': 'Only label 5'}) == []
    assert plot_sets_lister(None, {}) == []


# ---- test_the_fields_of_a_form -------------------------------------------------------
def test_the_fields_of_a_form(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the shared parts of a form: the experiment picker (every
    experiment in use by its file name, starting at the first or at the one the plot
    has), the group drop-downs (one per column that has a label, under the name the
    user gave it), a tick, the roles a filled-in form gives, and that a plot type
    asks what was set for it and otherwise nothing.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        Gives a made-up plot type its form.

    ---- Globals read ----
    C1_ROLE, C2_ROLE, K1_ROLE, K2_ROLE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _setup_maker
    """

    setup = _setup_maker()

    # ---- 1 The experiment picker -----------------------------------------------------
    picker = experiment_field_maker(setup, {})
    assert picker == {'key': 'experiment',
                      'kind': 'choice',
                      'label': 'Experiment',
                      'choices': [(C1_ROLE, 'c1'),
                                  (C2_ROLE, 'c2'),
                                  (K1_ROLE, 'k1'),
                                  (K2_ROLE, 'k2'),
                                  ],
                      'value': C1_ROLE,
                      }
    assert experiment_field_maker(setup, {'experiment': K1_ROLE})['value'] == K1_ROLE
    gone = 'Group 1: 9, Group 2: 1, time point: 1, replicate: 1'
    assert experiment_field_maker(setup, {'experiment': gone})['value'] == C1_ROLE
    empty = experiment_field_maker(None, {})
    assert empty['choices'] == [] and empty['value'] == ''

    # ---- 2 The group drop-downs ------------------------------------------------------
    assert group_columns_lister(setup) == [('group_1', 'strain'),
                                           ('group_2', 'Group 2'),
                                           ('time_point', 'Time point'),
                                           ]
    assert group_choices_lister(setup, 'group_1') == [
        ('Split', 'Split: each label on its own'),
        ('Only label 1', 'Only control'),
        ('Only label 2', 'Only knockdown'),
        ('All together', 'All together'),
        ]
    groups = group_fields_lister(setup, {})
    assert [(f['key'], f['label'], f['value']) for f in groups] == [
        ('group_1', 'strain', 'Split'),
        ('group_2', 'Group 2', 'All together'),
        ('time_point', 'Time point', 'All together'),
        ]
    kept = group_fields_lister(setup,
                               {'group_1': 'Only label 2', 'group_2': 'Only label 7'},
                               )
    assert [f['value'] for f in kept] == ['Only label 2',
                                          'All together',
                                          'All together',
                                          ]
    # a column with no label has no drop-down
    for row in setup['rows']:
        row['time_point'] = ''
    assert [key for key, _ in group_columns_lister(setup)] == ['group_1', 'group_2']
    assert group_columns_lister(None) == []

    # ---- 3 A tick, and the roles of a filled-in form ---------------------------------
    tick = tick_field_maker('bands', 'Haem bands', {}, True)
    assert tick == {'key': 'bands',
                    'kind': 'tick',
                    'label': 'Haem bands',
                    'choices': [],
                    'value': 'yes',
                    }
    assert tick_field_maker('bands',
                            'Haem bands',
                            {'bands': 'no'},
                            True,
                            )['value'] == 'no'
    fields = [picker, groups[0], tick, empty]
    assert form_roles_reader(fields,
                             {'experiment': 'k1',
                              'group_1': 'Only knockdown',
                              'bands': False,
                              },
                             ) == {'experiment': K1_ROLE,
                                   'group_1': 'Only label 2',
                                   'bands': 'no',
                                   }
    # a field the form does not hold keeps its value
    assert form_roles_reader(fields, {}) == {'experiment': C1_ROLE,
                                             'group_1': 'Split',
                                             'bands': 'yes',
                                             }

    # ---- 4 What a plot type asks -----------------------------------------------------
    assert form_fields_lister('P17', setup, {}) == []
    monkeypatch.setitem(page_data.FORM_MAKERS,
                        'P1',
                        lambda setup, roles, answers: [experiment_field_maker(setup,
                                                                              roles,
                                                                              ),
                                                       ],
                        )
    assert form_fields_lister('P1',
                              setup,
                              {'experiment': K2_ROLE},
                              )[0]['value'] == K2_ROLE


# ---- test_the_caption_lines ----------------------------------------------------------
def test_the_caption_lines() -> None:
    """
    ---- Summary ----
    Main function to check what is written under the page for the caption: nothing
    for a page whose plots show no sets, the colours of the Group 1 labels for a plot
    split by Group 1, then the line styles and the shades once a plot is split by
    Group 2 and by the time point; the plain name of a colour; and the experiments
    the plots of a page show.

    ---- Inputs ----
    None.

    ---- Globals read ----
    K1_ROLE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    #101010 is nearest black (16² x 3 = 768 from it, far less than from grey).

    ---- Helpers ----
    _setup_maker
    """

    setup = _setup_maker()
    page = plot_placer(FigurePage(), PagePlot('P17', 5, 0))
    page = plot_placer(page, PagePlot('P1', 0, 0, roles={'experiment': K1_ROLE}))
    assert caption_lines_builder(page, setup) == []
    assert page_experiments_lister(page, setup) == ['k1']
    page = plot_placer(page, PagePlot('P10', 1, 0, roles={'group_1': 'Only label 1'}))
    assert caption_lines_builder(page, setup) == ['Colours (strain): control, blue.']
    assert page_experiments_lister(page, setup) == ['k1', 'c1', 'c2']
    page = plot_placer(page,
                       PagePlot('P9',
                                2,
                                0,
                                roles={'group_2': 'Split', 'time_point': 'Split'},
                                ),
                       )
    assert caption_lines_builder(page, setup) == [
        'Colours (strain): control, blue; knockdown, red-orange.',
        'Line styles (Group 2): order A, solid line; order B, dashed line.',
        'Shades (Time point), from dark to light: 2 h, 7 h.',
        ]
    assert caption_lines_builder(page, None) == []
    assert (colour_namer('#0072b2'), colour_namer('#d55e00')) == ('blue', 'red-orange')
    assert colour_namer('#101010') == 'black'
    assert colour_namer('#e69f00') == 'orange'


# ---- test_a_difference_spectrum_adds_its_regions_to_the_caption ----------------------
def test_a_difference_spectrum_adds_its_regions_to_the_caption() -> None:
    """
    ---- Summary ----
    Main function to check the caption line of each Difference spectrum of a page:
    its letter and the times of its two regions, after the lines of the colours;
    none for one whose experiment has no difference spectrum or was not read.

    ---- Inputs ----
    None.

    ---- Globals read ----
    C1_ROLE, C2_ROLE, K1_ROLE.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The plots are lettered in reading order: a (c1), b (k1), c (c2), d (the plot
    of sets).

    ---- Helpers ----
    _setup_maker
    """

    setup = _setup_maker()
    page = FigurePage()
    for row, role in enumerate((C1_ROLE, K1_ROLE, C2_ROLE)):
        page = plot_placer(page, PagePlot('P2', row, 0, roles={'experiment': role}))
    experiments = {'c1': {'difference': {'oxidised_region': (2.0, 4.0),
                                         'reduced_region': (12.0, 14.25),
                                         },
                          },
                   'k1': {'difference': None},
                   'c2': {'difference': {'oxidised_region': (0.0, 1.0),
                                         'reduced_region': (3.0, 4.0),
                                         },
                          },
                   }
    first = 'a: reduced, 12.0 to 14.2 min, minus oxidised, 2.0 to 4.0 min.'
    last = 'c: reduced, 3.0 to 4.0 min, minus oxidised, 0.0 to 1.0 min.'
    assert caption_lines_builder(page, setup, experiments) == [first, last]
    assert caption_lines_builder(page, setup, {'c1': experiments['c1']}) == [first]
    assert caption_lines_builder(page, setup) == []
    page = plot_placer(page, PagePlot('P10', 3, 0, roles={'group_1': 'Only label 1'}))
    assert caption_lines_builder(page, setup, experiments) == [
        'Colours (strain): control, blue.',
        first,
        last,
        ]


# ---- test_a_mean_trace_adds_its_line_to_the_caption ----------------------------------
def test_a_mean_trace_adds_its_line_to_the_caption() -> None:
    """
    ---- Summary ----
    Main function to check the caption line of each Mean trace of a page: its
    letter, what its lines and its band are and what it is lined up on, after the
    lines of the colours; as a new plot starts (SEM, the first addition), with the
    SD from another addition, and without a band from the start of each recording.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _setup_maker
    """

    setup = _setup_maker()
    page = FigurePage()
    for row, roles in enumerate(({},
                                 {'band': 'sd', 'time_zero': 'addition 3'},
                                 {'band': 'none', 'time_zero': 'start'},
                                 ),
                                ):
        page = plot_placer(page, PagePlot('P8', row, 0, roles=roles))
    start = 'each line is the mean of its experiments'
    assert caption_lines_builder(page, setup) == [
        'Colours (strain): control, blue; knockdown, red-orange.',
        f'a: {start}, the band ± SEM; lined up on addition 1.',
        f'b: {start}, the band ± SD; lined up on addition 3.',
        f'c: {start}; lined up on the start of each recording.',
        ]
