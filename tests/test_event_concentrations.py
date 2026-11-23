"""
Tests of the concentration of each addition, worked out by hand: the stock with its unit, the concentration in the chamber adding up, a concentration typed, an ignored event and the text of the labels.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.event_concentrations import (addition_calculator,
                                               concentration_reader,
                                               event_concentration_filler,
                                               event_text_writer,
                                               )
from utils_shared.helpers import concentration_formatter
from utils_viewer.viewer_table import label_worked_writer


# ---- CONSTANTS -----------------------------------------------------------------------
CHAMBER_ML = 5.0
# One made-up run, as typed in the labels table: 5 µL of a 10 mM BD stock, then three
# times 10 µL of a 200 mM KCN stock, one event left out between them.
RUN = [{'label': 'BD', 'stock_uM': 10_000.0, 'added_uL': 5.0, 'ignored': False},
       {'label': 'KCN', 'stock_uM': 200_000.0, 'added_uL': 10.0, 'ignored': False},
       {'label': 'kcn ', 'stock_uM': 200_000.0, 'added_uL': 10.0, 'ignored': False},
       {'label': 'ignore', 'stock_uM': 1.0, 'added_uL': 1.0, 'ignored': True},
       {'label': 'KCN', 'stock_uM': 200_000.0, 'added_uL': 10.0, 'ignored': False},
       ]


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_one_addition ---------------------------------------------------------------
def test_one_addition() -> None:
    """
    ---- Summary ----
    Main function to check the concentration one addition gives, the example of
    MATHS.md: 10 µL of a 200 mM stock in the 5 mL chamber gives
    200 000 µM × 10 µL ÷ 5000 µL = 400 µM, and 5 µL of 10 mM gives 10 µM.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CHAMBER_ML.

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

    assert addition_calculator(200_000.0, 10.0, CHAMBER_ML) == pytest.approx(400.0)
    assert addition_calculator(10_000.0, 5.0, CHAMBER_ML) == pytest.approx(10.0)


# ---- test_the_same_thing_added_again_adds_up -----------------------------------------
def test_the_same_thing_added_again_adds_up() -> None:
    """
    ---- Summary ----
    Main function to check the concentrations in the chamber of a run: BD 10 µM; KCN
    400, then 800 (400 + 400), then 1200 µM (800 + 400), "kcn " counting as KCN and
    the event left out between them holding nothing and changing nothing.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CHAMBER_ML, RUN.

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

    filled = event_concentration_filler(RUN, CHAMBER_ML)
    assert [e['concentration_uM'] for e in filled] == [pytest.approx(10.0),
                                                       pytest.approx(400.0),
                                                       pytest.approx(800.0),
                                                       None,
                                                       pytest.approx(1200.0),
                                                       ]
    assert [e['addition_uM'] for e in filled] == [pytest.approx(10.0),
                                                  pytest.approx(400.0),
                                                  pytest.approx(400.0),
                                                  None,
                                                  pytest.approx(400.0),
                                                  ]
    assert (filled[3]['stock_uM'], filled[3]['added_uL']) == (None, None)
    assert RUN[1].get('concentration_uM') is None  # the events given are not changed


# ---- test_a_concentration_typed ------------------------------------------------------
def test_a_concentration_typed() -> None:
    """
    ---- Summary ----
    Main function to check a concentration in the chamber typed by hand: BD typed as
    10 µM; then 5 µL of 10 mM BD gives 10 + 10 = 20 µM; then BD typed as 50 µM adds
    50 − 20 = 30 µM. A stock without a volume is dropped, and the event then has no
    concentration.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CHAMBER_ML.

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

    events = [{'label': 'BD', 'concentration_uM': 10.0},
              {'label': 'BD', 'stock_uM': 10_000.0, 'added_uL': 5.0},
              {'label': 'BD', 'concentration_uM': 50.0},
              {'label': 'azide', 'stock_uM': 1000.0, 'added_uL': None},
              ]
    filled = event_concentration_filler(events, CHAMBER_ML)
    assert [e['concentration_uM'] for e in filled] == [pytest.approx(10.0),
                                                       pytest.approx(20.0),
                                                       pytest.approx(50.0),
                                                       None,
                                                       ]
    assert [e['addition_uM'] for e in filled] == [pytest.approx(10.0),
                                                  pytest.approx(10.0),
                                                  pytest.approx(30.0),
                                                  None,
                                                  ]
    assert filled[3]['stock_uM'] is None


# ---- test_a_stock_typed_with_its_unit ------------------------------------------------
def test_a_stock_typed_with_its_unit() -> None:
    """
    ---- Summary ----
    Main function to check a concentration typed with or without its unit: '200 mM',
    '200' (mM when none is typed) and '0,2 M' are 200 000 µM; '500 uM' is 500 µM;
    '10 nM' is 0.01 µM; a word is wrong; 0 is wrong for a stock but not in the chamber;
    nothing typed is "not filled in".

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
    None.
    """

    for typed in ('200 mM', '200', '0,2 M', '200MM', ' 200 mm '):
        value, is_valid = concentration_reader(typed, 'mm', False)
        assert is_valid and value == pytest.approx(200_000.0)
    assert concentration_reader('500 uM', 'mm', False) == (pytest.approx(500.0), True)
    assert concentration_reader('500 µM', 'mm', False) == (pytest.approx(500.0), True)
    assert concentration_reader('10 nM', 'mm', False) == (pytest.approx(0.01), True)
    assert concentration_reader('400', 'um', True) == (pytest.approx(400.0), True)
    assert concentration_reader('0', 'um', True) == (pytest.approx(0.0), True)
    assert concentration_reader('', 'mm', False) == (None, True)
    for wrong in ('KCN', '0', '-5 mM', '200 mL', '1.2.3'):
        assert concentration_reader(wrong, 'mm', False) == (None, False)


# ---- test_the_text_of_the_labels -----------------------------------------------------
def test_the_text_of_the_labels() -> None:
    """
    ---- Summary ----
    Main function to check the labels on the plot: in the chamber '1.2 mM KCN' (from
    1200 µM, in its most readable unit); what was added '10 µL of 200 mM KCN'; an
    event with only a typed concentration shows it either way; an event with no
    concentration shows its label alone. Concentrations below 1 µM are written in nM.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CHAMBER_ML, RUN.

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

    last = event_concentration_filler(RUN, CHAMBER_ML)[4]
    assert event_text_writer(last, 'chamber') == '1.2 mM KCN'
    assert event_text_writer(last, 'added') == '10 µL of 200 mM KCN'
    typed = {'label': 'BD', 'concentration_uM': 10.0}
    assert event_text_writer(typed, 'added') == '10 µM BD'
    assert event_text_writer({'label': 'nd-011992'}, 'chamber') == 'nd-011992'
    assert concentration_formatter(0.5) == '500 nM'
    assert concentration_formatter(1200.0) == '1.2 mM'


# ---- test_the_table_fills_in_the_chamber ---------------------------------------------
def test_the_table_fills_in_the_chamber() -> None:
    """
    ---- Summary ----
    Main function to check what the labels table fills in as it is typed: the rows
    with a stock and a volume get their concentration in the chamber (10 µM, 400 µM,
    800 µM, the second KCN adding up); a row left out and a row typed by hand are not
    filled in; each file adds up on its own.

    ---- Inputs ----
    None.

    ---- Globals read ----
    CHAMBER_ML.

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

    rows = [{'file': 'run1', 'cells': {'label': 'BD'}},
            {'file': 'run1', 'cells': {'label': 'KCN'}},
            {'file': 'run1', 'cells': {'label': 'KCN'}},
            {'file': 'run1', 'cells': {'label': 'Event 4'}},
            {'file': 'run2', 'cells': {'label': 'KCN'}},
            {'file': 'run2', 'cells': {'label': 'BD'}},
            ]
    kcn = {'label': 'KCN', 'stock_uM': 200_000.0, 'added_uL': 10.0}
    values = [{'label': 'BD', 'stock_uM': 10_000.0, 'added_uL': 5.0},
              dict(kcn),
              dict(kcn, concentration_uM=400.0),  # the value shown before is not used
              {'label': 'ignore', 'stock_uM': None, 'added_uL': None},
              dict(kcn),
              {'label': None, 'concentration_uM': 10.0},
              ]
    shown = label_worked_writer(rows, values, 'ignore', CHAMBER_ML)
    assert shown == ['10 µM', '400 µM', '800 µM', None, '400 µM', None]
