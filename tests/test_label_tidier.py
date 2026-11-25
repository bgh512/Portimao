"""
Tests of the tidy form of an event label, and that the figures can draw its symbols.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import warnings

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
import pytest
from matplotlib import font_manager
from matplotlib.figure import Figure
from matplotlib.ft2font import FT2Font
from matplotlib.lines import Line2D

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.survey import label_tidier, SUPERSCRIPT_TABLE
from utils_viewer.viewer_gui import SYMBOLS


# ---- CONSTANTS -----------------------------------------------------------------------
# the fonts the figures fall back on after the journal's own (ExperimentConfig)
FALLBACK_FONTS = ('Liberation Sans', 'DejaVu Sans')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_exponent_after_a_caret_is_raised -------------------------------------------
def test_exponent_after_a_caret_is_raised() -> None:
    """
    ---- Summary ----
    Main function to check that anything typed after ^ is raised, with or without a
    sign.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert label_tidier('5 nmol min^-1') == '5 nmol min⁻¹'
    assert label_tidier('3 cm^2') == '3 cm²'


# ---- test_exponent_after_a_unit_is_raised --------------------------------------------
def test_exponent_after_a_unit_is_raised() -> None:
    """
    ---- Summary ----
    Main function to check that -1 written straight after a unit is raised, and that a
    litre becomes a capital L.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert label_tidier('8 ug ml-1 rifampicin') == '8 µg mL⁻¹ rifampicin'
    assert label_tidier('2 mg l-1') == '2 mg L⁻¹'
    assert label_tidier('5 mg/l') == '5 mg/L'


# ---- test_micro_is_written_with_its_sign ---------------------------------------------
def test_micro_is_written_with_its_sign() -> None:
    """
    ---- Summary ----
    Main function to check that u in front of a unit becomes the micro sign.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert label_tidier('100 uM KCN') == '100 µM KCN'
    assert label_tidier('20 ul') == '20 µL'
    assert label_tidier('3 umol') == '3 µmol'


# ---- test_names_and_formulas_are_left_alone ------------------------------------------
def test_names_and_formulas_are_left_alone() -> None:
    """
    ---- Summary ----
    Main function to check that a name with numbers in it, a chemical formula, the word
    'ignore' and ordinary words are not changed.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for text in ('nd-011992',
                 'ND-011992',
                 'Q203',
                 'ignore',
                 'H2O2',
                 'NO2',
                 'glucose',
                 'bd then kcn',
                 'ugly sample',
                 '',
                 ):
        assert label_tidier(text) == text


# ---- test_number_and_unit_get_a_space ------------------------------------------------
def test_number_and_unit_get_a_space() -> None:
    """
    ---- Summary ----
    Main function to check that a number written against its unit gets a space.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    assert label_tidier('8ug ml') == '8 µg mL'
    assert label_tidier('100uM KCN') == '100 µM KCN'
    assert label_tidier('2mM azide') == '2 mM azide'


# ---- test_symbols_are_drawn_by_the_figure_settings -----------------------------------
@pytest.mark.parametrize('journal', sorted(settings.JOURNAL_SPECS))
def test_symbols_are_drawn_by_the_figure_settings(journal: str) -> None:
    """
    ---- Summary ----
    Main function to check that a figure drawn with the program's own settings draws
    every symbol: a character the journal's font lacks (Arial has no subscripts and no
    raised minus) is taken from the next font, not drawn as an empty box.

    ---- Inputs ----
    journal : str
        Key of the journal whose figure settings are used.

    ---- Globals read ----
    SYMBOLS, SUPERSCRIPT_TABLE (imported); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    text = ''.join(SYMBOLS) + ''.join(chr(c) for c in SUPERSCRIPT_TABLE.values())
    cfg = settings.Config(dict(settings.DEFAULT_ANSWERS, journal=journal))
    with matplotlib.rc_context(cfg.RC_PARAMS), warnings.catch_warnings():
        # the plotting library warns of each character it draws as an empty box
        warnings.simplefilter('error')
        fig = Figure()
        fig.text(0.5, 0.5, text)
        fig.legend(handles=[Line2D([], [], label=text)])
        fig.savefig(io.BytesIO(), format='png')


# ---- test_symbols_can_be_drawn_in_the_figures ----------------------------------------
def test_symbols_can_be_drawn_in_the_figures() -> None:
    """
    ---- Summary ----
    Main function to check that every symbol of the Symbols row of the window and every
    character a tidy label can hold is in at least one of the fonts the figures use on
    this computer, so that none is drawn as an empty box.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FALLBACK_FONTS (module constant); settings.JOURNAL_SPECS.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Reads the font files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Gather the characters -----------------------------------------------------
    characters = set(''.join(SYMBOLS)) | {'µ'} | {chr(c)
                                                 for c in SUPERSCRIPT_TABLE.values()
                                                 }

    # ---- 2 Open the figure fonts that are installed ----------------------------------
    families = {family
                for spec in settings.JOURNAL_SPECS.values()
                for family in spec['font_family']
                } | set(FALLBACK_FONTS)
    fonts = []
    for family in families:
        try:
            fonts.append(FT2Font(font_manager.findfont(family,
                                                       fallback_to_default=False,
                                                       ),
                                 ),
                         )
        except ValueError:  # that font is not on this computer
            continue
    assert fonts, 'None of the figure fonts is installed.'

    # ---- 3 Look each character up ----------------------------------------------------
    missing = [f'U+{ord(c):04X}'
               for c in sorted(characters)
               if not any(font.get_char_index(ord(c)) for font in fonts)
               ]
    assert not missing, 'No figure font can draw: ' + ', '.join(missing)


# ---- test_tidy_label_stays_as_it_is --------------------------------------------------
def test_tidy_label_stays_as_it_is() -> None:
    """
    ---- Summary ----
    Main function to check that a label that is already tidy is not changed, so its
    tidy form is not offered twice.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for text in ('8 µg mL⁻¹ rifampicin', '100 µM KCN', '5 nmol min⁻¹'):
        assert label_tidier(text) == text
