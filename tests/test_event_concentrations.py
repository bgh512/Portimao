"""
Tests of the concentration of each addition, worked out by hand: the stock with its unit, the concentration in the chamber adding up, a concentration typed, an ignored event, the text of the labels and what the text in the file gives.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.event_concentrations import (addition_calculator,
                                               CHAMBER_UNIT,
                                               concentration_reader,
                                               event_concentration_filler,
                                               event_text_reader,
                                               event_text_writer,
                                               STOCK_UNIT,
                                               unit_concentration_writer,
                                               )
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
    Main function to check the labels on the plot: in the chamber in its tidiest unit
    ('1.2 mM KCN', not 1200 µM; '500 nM'); what was added with the stock in its
    tidiest unit ('10 µL of 200 mM KCN', and a 1 M stock as 1 M); an event with only a
    typed concentration shows it either way; an event with no concentration shows its
    label alone; the labels table keeps its fixed units.

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
    # 20 µL of a 1 M stock: 1 000 000 × 20 ÷ 5000 = 4000 µM
    dithionite = {'label': 'dithi', 'stock_uM': 1_000_000.0, 'added_uL': 20.0}
    filled = event_concentration_filler([dithionite], CHAMBER_ML)[0]
    assert event_text_writer(filled, 'chamber') == '4 mM dithi'
    assert event_text_writer(filled, 'added') == '20 µL of 1 M dithi'
    # 0.5 µM is 500 nM; 999.96 µM is 1000 µM to four figures, so 1 mM
    assert event_text_writer({'label': 'x', 'concentration_uM': 0.5}, 'chamber') == (
        '500 nM x'
        )
    assert event_text_writer({'label': 'x', 'concentration_uM': 999.96}, 'chamber') == (
        '1 mM x'
        )
    assert event_text_writer({'label': 'x', 'concentration_uM': 0.0}, 'chamber') == (
        '0 µM x'
        )
    # 1 µL of an 8 mM stock: 8000 × 1 ÷ 5000 = 1.6 µM
    small = {'label': 'nd-011992', 'stock_uM': 8000.0, 'added_uL': 1.0}
    filled = event_concentration_filler([small], CHAMBER_ML)[0]
    assert event_text_writer(filled, 'chamber') == '1.6 µM nd-011992'
    assert unit_concentration_writer(200_000.0, STOCK_UNIT) == '200 mM'
    assert unit_concentration_writer(0.5, CHAMBER_UNIT) == '0.5 µM'
    assert unit_concentration_writer(1200.0, CHAMBER_UNIT, 10, False) == '1200'


# ---- test_the_text_in_the_file_read --------------------------------------------------
def test_the_text_in_the_file_read() -> None:
    """
    ---- Summary ----
    Main function to check what the text the instrument keeps with an addition gives,
    on the texts of the example run and a few made up: a number with a volume unit is
    the volume added (µL; 1 mL = 1000 µL), a number with a molar unit the stock (8mm
    = 8 mM = 8000 µM; 1m = 1 M = 1 000 000 µM), or the concentration in the chamber
    when no volume is given (100uM = 100 µM), and what is left the chemical; a text
    with nothing of these keeps it all as the chemical, and one with only a volume
    leaves the chemical empty.

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

    def read(text: str) -> tuple:
        found = event_text_reader(text)
        return (found['added_uL'],
                found['stock_uM'],
                found['label'],
                found['concentration_uM'],
                )

    assert read('1ul 8mm nd-011992') == (1.0, 8000.0, 'nd-011992', None)
    assert read('10ul 8mm nd-011992') == (10.0, 8000.0, 'nd-011992', None)
    assert read('9ul 10mm kcn') == (9.0, 10_000.0, 'kcn', None)
    assert read('4ul 100mm kcn') == (4.0, 100_000.0, 'kcn', None)
    assert read('20ul 1m dithi') == (20.0, 1_000_000.0, 'dithi', None)
    assert read('2.5 µL 0,5 M KCN') == (2.5, 500_000.0, 'KCN', None)
    assert read('0.01ml 200mM KCN') == (pytest.approx(10.0), 200_000.0, 'KCN', None)
    assert read('100uM KCN') == (None, None, 'KCN', 100.0)
    assert read('bubble') == (None, None, 'bubble', None)
    assert read('2 ul') == (2.0, None, '', None)
    assert read('') == (None, None, '', None)
    # numbers inside a name, or minutes, are not taken for a unit
    assert read('5 min wait') == (None, None, '5 min wait', None)
    assert read('8ug ml-1 DAP') == (None, None, '8ug ml-1 DAP', None)


# ---- test_the_table_fills_in_the_chamber ---------------------------------------------
def test_the_table_fills_in_the_chamber() -> None:
    """
    ---- Summary ----
    Main function to check what the labels table fills in as it is typed: the rows
    with a stock and a volume get their concentration in the chamber (10, 400 and 800
    µM, the second KCN adding up); a row left out (IGNORE in any capitals) and a row
    typed by hand are not
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
              {'label': 'Ignore', 'stock_uM': None, 'added_uL': None},
              dict(kcn),
              {'label': None, 'concentration_uM': 10.0},
              ]
    # the cells are in µM, the unit of their heading
    shown = label_worked_writer(rows, values, 'IGNORE', CHAMBER_ML)
    assert shown == ['10', '400', '800', None, '400', None]
