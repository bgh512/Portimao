"""
The concentration of each addition: the stock typed with its unit, the concentration in the chamber, adding up for the same thing added again, and the text of its label.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from typing import List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import concentration_formatter, name_simplifier
from utils_shared.questions import typed_number_reader


# ---- CONSTANTS -----------------------------------------------------------------------
# The units a concentration may be typed in, lower case, each in micromolar; the micro
# sign may be typed as u, the micro sign or the Greek mu.
UNIT_FACTORS_UM = {'nm': 0.001,
                   'um': 1.0,
                   'µm': 1.0,
                   'μm': 1.0,
                   'mm': 1000.0,
                   'm': 1_000_000.0,
                   }
# A number, then a unit of UNIT_FACTORS_UM or none.
TYPED_CONCENTRATION_PATTERN = re.compile(r'\s*(.*?)\s*([nuµμm]?m)?\s*')
# How the event labels show the concentration: what is in the chamber after the
# addition ("400 µM KCN"), or what was added ("10 µL of 200 mM KCN").
LABEL_MODES = {'chamber': 'In the chamber', 'added': 'What was added'}
UL_PER_ML = 1000.0


# ---- HELPERS -------------------------------------------------------------------------


# ---- _label_key_maker ----------------------------------------------------------------
def _label_key_maker(label: str) -> str:
    """
    ---- Summary ----
    Helper function to give the key by which two additions are taken to be of the same
    thing: their labels alike once capitals, spaces and punctuation are left out, so
    "KCN" and "kcn " add up.

    ---- Inputs ----
    label : str
        Label of the event.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The key.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    name_simplifier
    """

    return name_simplifier(label)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- addition_calculator -------------------------------------------------------------
def addition_calculator(stock_um: float, added_ul: float, chamber_ml: float) -> float:
    """
    ---- Summary ----
    Main function to work out how much one addition raises the concentration in the
    chamber. The volume added is not counted in the chamber's volume.

    ---- Inputs ----
    stock_um : float
        Concentration of the stock (µM), above 0.
    added_ul : float
        Volume of the stock added (µL), above 0.
    chamber_ml : float
        Volume of the chamber (mL), above 0.

    ---- Globals read ----
    UL_PER_ML.

    ---- Outputs ----
    float
        The rise of the concentration in the chamber (µM).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    addition = stock × added ÷ chamber, the chamber in µL (× 1000): 10 µL of a
    200 mM (200 000 µM) stock in 5 mL gives 200 000 × 10 ÷ 5000 = 400 µM.

    ---- Helpers ----
    None.
    """

    return stock_um * added_ul / (chamber_ml * UL_PER_ML)


# ---- concentration_reader ------------------------------------------------------------
def concentration_reader(text: str,
                         default_unit: str,
                         is_zero_allowed: bool,
                         ) -> Tuple[Optional[float], bool]:
    """
    ---- Summary ----
    Main function to read a concentration typed with or without its unit (nM, µM, mM
    or M, in any capitals, the micro sign typed as u if need be).

    ---- Inputs ----
    text : str
        What was typed, such as '200 mM', '0,5M' or '200'.
    default_unit : str
        The unit of a number typed alone: a key of UNIT_FACTORS_UM, such as 'mm'.
    is_zero_allowed : bool
        True when 0 can be used (a concentration in the chamber); False for a stock.

    ---- Globals read ----
    TYPED_CONCENTRATION_PATTERN, UNIT_FACTORS_UM.

    ---- Outputs ----
    Tuple[Optional[float], bool]
        (concentration in µM, True) when it can be used; (None, True) for nothing
        typed; (None, False) for anything else.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    µM = number × UNIT_FACTORS_UM[unit]: '200 mM' gives 200 × 1000 = 200 000 µM.

    ---- Helpers ----
    typed_number_reader
    """

    if not text.strip():
        return None, True
    found = TYPED_CONCENTRATION_PATTERN.fullmatch(text.lower())
    number = typed_number_reader(found.group(1)) if found else None
    if number is None or number < 0 or (number == 0 and not is_zero_allowed):
        return None, False
    return number * UNIT_FACTORS_UM[found.group(2) or default_unit], True


# ---- event_amount_writer -------------------------------------------------------------
def event_amount_writer(event: dict, mode: str) -> str:
    """
    ---- Summary ----
    Main function to write how much of a thing an event holds, as the labels show it:
    the concentration in the chamber after it, or the volume and the stock added (an
    event with no stock shows its concentration either way).

    ---- Inputs ----
    event : dict
        An event with concentration_uM (in the chamber), and stock_uM and added_uL
        when they were typed; each may be None or missing.
    mode : str
        A key of LABEL_MODES: 'chamber' or 'added'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '400 µM', '1.2 mM' or '10 µL of 200 mM'; '' when the event has no
        concentration.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    concentration_formatter
    """

    stock, added = event.get('stock_uM'), event.get('added_uL')
    if mode == 'added' and stock is not None and added is not None:
        return f'{float(added):g} µL of {concentration_formatter(stock)}'
    concentration = event.get('concentration_uM')
    return '' if concentration is None else concentration_formatter(concentration)


# ---- event_concentration_filler ------------------------------------------------------
def event_concentration_filler(events: List[dict], chamber_ml: float) -> List[dict]:
    """
    ---- Summary ----
    Main function to work out, for the events of one file in order, the concentration
    each addition adds and the concentration in the chamber after it. An event with a
    stock and a volume adds stock × volume ÷ chamber to what is already in the chamber
    of the same thing (the same label); an event without them keeps the concentration
    in the chamber that was typed, and adds the difference. Ignored events hold
    nothing and change nothing.

    ---- Inputs ----
    events : List[dict]
        The events of one file, in order: {'label', 'stock_uM', 'added_uL',
        'concentration_uM', 'ignored', ...}; a value may be None or missing.
    chamber_ml : float
        Volume of the chamber (mL), above 0.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[dict]
        A copy of each event with stock_uM, added_uL, addition_uM (what it adds, µM)
        and concentration_uM (in the chamber after it, µM), each None where unknown;
        a stock without a volume, or a volume without a stock, is dropped.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With a stock and a volume: addition = stock × added ÷ chamber (addition_calculator)
    and in the chamber = before + addition, where before is the concentration in the
    chamber after the last event of the same label (0 for the first). Typed:
    addition = in the chamber − before. Three additions of 10 µL of 200 mM KCN in
    5 mL give 400, 800 and 1200 µM in the chamber.

    ---- Helpers ----
    _label_key_maker
    addition_calculator
    """

    totals = {}
    result = []
    for event in events:
        entry = dict(event)
        stock, added = entry.get('stock_uM'), entry.get('added_uL')
        if entry.get('ignored') or stock is None or added is None:
            stock = added = None
        entry.update(stock_uM=stock, added_uL=added, addition_uM=None)
        if entry.get('ignored'):
            entry['concentration_uM'] = None
            result.append(entry)
            continue
        key = _label_key_maker(entry.get('label') or '')
        before = totals.get(key, 0.0)
        if stock is not None:
            entry['addition_uM'] = addition_calculator(float(stock),
                                                       float(added),
                                                       chamber_ml,
                                                       )
            entry['concentration_uM'] = before + entry['addition_uM']
        elif entry.get('concentration_uM') is not None:
            entry['concentration_uM'] = float(entry['concentration_uM'])
            entry['addition_uM'] = entry['concentration_uM'] - before
        else:
            entry['concentration_uM'] = None
        if entry['concentration_uM'] is not None:
            totals[key] = entry['concentration_uM']
        result.append(entry)
    return result


# ---- event_text_writer ---------------------------------------------------------------
def event_text_writer(event: dict, mode: str) -> str:
    """
    ---- Summary ----
    Main function to write the label of an event on a plot: how much of it there is,
    then its label. See event_amount_writer.

    ---- Inputs ----
    event : dict
        An event with its label (see event_amount_writer).
    mode : str
        A key of LABEL_MODES: 'chamber' or 'added'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '400 µM KCN', '10 µL of 200 mM KCN' or 'KCN'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    event_amount_writer
    """

    return f"{event_amount_writer(event, mode)} {event.get('label') or ''}".strip()
