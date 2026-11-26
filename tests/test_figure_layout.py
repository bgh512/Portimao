"""
Tests of the journal sizes of the figures: the size of a figure from the journal's
widths and height, the sentences about text a journal finds too small or too large,
and the lines kept between the thinnest and the thickest a journal takes.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pytest
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared import figure_layout
from utils_shared.figure_layout import (axes_room_fitter,
                                        figure_canvas_fitter,
                                        figure_lines_fitter,
                                        figure_size_calculator,
                                        figure_style_builder,
                                        figure_style_checker,
                                        font_family_lister,
                                        line_width_fitter,
                                        plot_legend_placer,
                                        )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- test_science_figure_sizes -------------------------------------------------------
def test_science_figure_sizes() -> None:
    """
    ---- Summary ----
    Main function to check the Science widths and height against its figure guide, the
    size of a figure worked out from them, and the height Cell recommends.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Science prints in three columns: 1 column is 5.7 cm, 2 columns are 12.1 cm and 3
    columns 18.4 cm; the tallest figure is 199 mm. A 3 column figure of half the
    height is 184 / 25.4 = 7.244 in wide and 199 x 0.5 / 25.4 = 3.917 in tall. Cell
    recommends figures of at most 16.5 x 20 cm, so its tallest figure is 200 mm.

    ---- Helpers ----
    None.
    """

    spec = settings.JOURNAL_SPECS['science']
    assert spec['widths_mm'] == {1: 57, 2: 121, 3: 184}
    assert spec['page_height_mm'] == 199
    width_in, height_in = figure_size_calculator(spec, 3, 0.5)
    assert width_in == pytest.approx(7.244, abs=0.001)
    assert height_in == pytest.approx(3.917, abs=0.001)
    with pytest.raises(ValueError):
        figure_size_calculator(spec, 1.5, 0.5)
    assert settings.JOURNAL_SPECS['cell']['page_height_mm'] == 200


# ---- test_figure_never_taller_than_the_journal_takes ---------------------------------
def test_figure_never_taller_than_the_journal_takes() -> None:
    """
    ---- Summary ----
    Main function to check that the tallest figure of every journal is the journal's
    own tallest, and that a taller one is refused.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The whole height (1) of a Nature figure is 170 / 25.4 = 6.693 in.

    ---- Helpers ----
    None.
    """

    for spec in settings.JOURNAL_SPECS.values():
        _, height_in = figure_size_calculator(spec, 1, 1)
        assert height_in * 25.4 == pytest.approx(spec['page_height_mm'])
        with pytest.raises(ValueError):
            figure_size_calculator(spec, 1, 1.1)
    _, height_in = figure_size_calculator(settings.JOURNAL_SPECS['nature'], 1, 1)
    assert height_in == pytest.approx(6.693, abs=0.001)


# ---- test_text_size_sentences --------------------------------------------------------
def test_text_size_sentences() -> None:
    """
    ---- Summary ----
    Main function to check the sentences about text sizes a journal does not take: one
    plain sentence for each kind of text, with its size, the journal's limit and the
    journal's name, and none when every size fits.

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
    A made-up journal takes 6 to 7 pt. Text of 5, 6 and 7 pt: only the 5 pt is too
    small. Text of 6.5, 7.5 and 8.5 pt: the 7.5 and the 8.5 pt are too large.

    ---- Helpers ----
    None.
    """

    spec = {'name': 'Made Up', 'font_min_pt': 6, 'font_max_pt': 7}
    small = {'tick': 5.0, 'label': 6.0, 'title': 7.0, 'panel_letter': 8}
    assert figure_style_checker(spec, small) == [
        'The tick labels and legends of the figures (5 pt) are smaller than the 6 pt '
        'Made Up asks for.',
        ]
    large = {'tick': 6.5, 'label': 7.5, 'title': 8.5, 'panel_letter': 8}
    assert figure_style_checker(spec, large) == [
        'The axis titles of the figures (7.5 pt) are larger than the 7 pt Made Up '
        'allows.',
        'The panel titles of the figures (8.5 pt) are larger than the 7 pt Made Up '
        'allows.',
        ]
    fitting = {'tick': 6.0, 'label': 6.5, 'title': 7.0, 'panel_letter': 12}
    assert figure_style_checker(spec, fitting) == []


# ---- test_standard_text_fits_the_standard_journal ------------------------------------
def test_standard_text_fits_the_standard_journal() -> None:
    """
    ---- Summary ----
    Main function to check that the standard text sizes give no sentence with the
    standard journal, Nature.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.BASE_FONT_PT, settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    The standard text is 5, 6 and 7 pt; Nature takes 5 to 7 pt.

    ---- Helpers ----
    None.
    """

    spec = settings.JOURNAL_SPECS['nature']
    fonts = figure_style_builder(spec, settings.BASE_FONT_PT)['fonts']
    assert figure_style_checker(spec, fonts) == []


# ---- test_text_fitted_to_the_journal -------------------------------------------------
def test_text_fitted_to_the_journal() -> None:
    """
    ---- Summary ----
    Main function to check that the text sizes and the paddings are moved to fit the
    journal chosen, so that no journal of the settings gives a sentence.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.BASE_FONT_PT, settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Axis titles of 6 pt wanted. A journal taking 5 to 7 pt keeps 5, 6 and 7 pt, with a
    padding unit of 6 pt. One taking 6 to 8 pt gets 6, 7 and 8 pt, with a unit of 7 pt.
    One taking 4 to 5.5 pt gets 3.5, 4.5 and 5.5 pt: the largest text is brought down
    to its 5.5 pt, but then the smallest would be under 4 pt, so the smallest is kept
    at 4 pt: 4, 5 and 6 pt.

    ---- Helpers ----
    None.
    """

    same = figure_style_builder(
        {'font_min_pt': 5, 'font_max_pt': 7, 'panel_letter_pt': 8},
        6,
        )
    assert (same['fonts']['tick'], same['fonts']['label'], same['fonts']['title']) == (
        5,
        6,
        7,
        )
    assert same['unit'] == 6
    larger = figure_style_builder({'font_min_pt': 6,
                                   'font_max_pt': 8,
                                   'panel_letter_pt': 8,
                                   },
                                  6,
                                  )
    assert (larger['fonts']['tick'],
            larger['fonts']['label'],
            larger['fonts']['title'],
            ) == (6, 7, 8)
    assert larger['unit'] == 7
    narrow = figure_style_builder({'font_min_pt': 4,
                                   'font_max_pt': 5.5,
                                   'panel_letter_pt': 8,
                                   },
                                  6,
                                  )
    assert (narrow['fonts']['tick'],
            narrow['fonts']['label'],
            narrow['fonts']['title'],
            ) == (4, 5, 6)
    for spec in settings.JOURNAL_SPECS.values():
        fonts = figure_style_builder(spec, settings.BASE_FONT_PT)['fonts']
        assert figure_style_checker(spec, fonts) == []


# ---- test_journal_with_no_largest_text -----------------------------------------------
def test_journal_with_no_largest_text() -> None:
    """
    ---- Summary ----
    Main function to check a journal that gives a smallest text and no largest: text
    that is too small is lifted, nothing is brought down, and no text is named as too
    large.

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
    Axis titles of 6 pt wanted. A journal taking 4.5 pt and up keeps 5, 6 and 7 pt
    (5 pt is above 4.5 pt). One taking 8 pt and up gets 8, 9 and 10 pt, with a padding
    unit of 9 pt.

    ---- Helpers ----
    None.
    """

    open_top = {'name': 'Made Up', 'font_min_pt': 4.5, 'font_max_pt': None}
    kept = figure_style_builder(dict(open_top, panel_letter_pt=8), 6)
    assert (kept['fonts']['tick'], kept['fonts']['label'], kept['fonts']['title']) == (
        5,
        6,
        7,
        )
    lifted = figure_style_builder({'font_min_pt': 8,
                                   'font_max_pt': None,
                                   'panel_letter_pt': 8,
                                   },
                                  6,
                                  )
    assert (lifted['fonts']['tick'],
            lifted['fonts']['label'],
            lifted['fonts']['title'],
            ) == (8, 9, 10)
    assert lifted['unit'] == 9
    huge = {'tick': 20.0, 'label': 30.0, 'title': 40.0, 'panel_letter': 8}
    assert figure_style_checker(open_top, huge) == []
    small = {'tick': 4.0, 'label': 5.0, 'title': 6.0, 'panel_letter': 8}
    assert figure_style_checker(open_top, small) == [
        'The tick labels and legends of the figures (4 pt) are smaller than the 4.5 '
        'pt Made Up asks for.',
        ]


# ---- test_lines_kept_to_what_the_journal_takes ---------------------------------------
def test_lines_kept_to_what_the_journal_takes() -> None:
    """
    ---- Summary ----
    Main function to check that every line of a figure is kept between the thinnest
    and the thickest line the journal takes: the line widths of the figure style, and
    the lines, tick marks, edges and groups of lines of a made-up figure drawn with
    widths of their own. A width of 0 (no line) and a journal with no limits change
    nothing.

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
    Data lines of 0.75 pt give axis lines of 0.65 x 0.75 = 0.488 pt and thin lines of
    0.5 x 0.75 = 0.375 pt. With a thinnest line of 0.5 pt they become 0.75, 0.5 and
    0.5 pt; with a thickest line of 0.6 pt, 0.6, 0.488 and 0.375 pt. In the made-up
    figure, between 0.5 and 1.5 pt: 0.2 pt becomes 0.5 pt, 3 pt becomes 1.5 pt and
    1 pt stays.

    ---- Helpers ----
    None.
    """

    # ---- 1 One width -----------------------------------------------------------------
    assert line_width_fitter(0.375, 0.5, None) == 0.5
    assert line_width_fitter(2.6, 0.5, 1.5) == 1.5
    assert line_width_fitter(1.0, 0.5, 1.5) == 1.0
    assert line_width_fitter(0.0, 0.5, 1.5) == 0.0
    assert line_width_fitter(0.1, None, None) == 0.1

    # ---- 2 The line widths of the figure style ---------------------------------------
    text = {'font_min_pt': 5, 'font_max_pt': 7, 'panel_letter_pt': 8}
    free = figure_style_builder(text, 6, 1.0, 0.75)
    assert (free['line_width'], free['axes_line_width'], free['thin_line_width']) == (
        0.75,
        0.488,
        0.375,
        )
    assert free['line_limits'] == (None, None)
    thick = figure_style_builder(dict(text, line_min_pt=0.5, line_max_pt=None),
                                 6,
                                 1.0,
                                 0.75,
                                 )
    assert (thick['line_width'],
            thick['axes_line_width'],
            thick['thin_line_width'],
            ) == (0.75, 0.5, 0.5)
    assert thick['line_limits'] == (0.5, None)
    thin = figure_style_builder(dict(text, line_min_pt=None, line_max_pt=0.6),
                                6,
                                1.0,
                                0.75,
                                )
    assert (thin['line_width'], thin['axes_line_width'], thin['thin_line_width']) == (
        0.6,
        0.488,
        0.375,
        )

    # ---- 3 Every line of a made-up figure --------------------------------------------
    fig = Figure()
    ax = fig.subplots()
    hair, = ax.plot([0, 1], [0, 1], linewidth=0.2)
    fat, = ax.plot([0, 1], [1, 0], linewidth=3.0)
    fine, = ax.plot([0, 1], [0.5, 0.5], linewidth=1.0)
    group = ax.vlines([0.2, 0.8], 0, 1, linewidth=0.1)
    box = ax.axvspan(0.4, 0.6, linewidth=0.0)
    edged = ax.axvspan(0.1, 0.2, linewidth=4.0)
    for spine in ax.spines.values():
        spine.set_linewidth(0.3)
    ax.tick_params(width=0.3)
    before = [(hair.get_linewidth(), fat.get_linewidth())]
    assert figure_lines_fitter(fig, None, None) == 0
    assert before == [(0.2, 3.0)]
    assert figure_lines_fitter(fig, 0.5, 1.5) > 0
    assert (hair.get_linewidth(), fat.get_linewidth(), fine.get_linewidth()) == (0.5,
                                                                                 1.5,
                                                                                 1.0,
                                                                                 )
    assert list(group.get_linewidths()) == [0.5]
    assert box.get_linewidth() == 0.0
    assert edged.get_linewidth() == 1.5
    assert all(spine.get_linewidth() == 0.5 for spine in ax.spines.values())
    assert all(tick.tick1line.get_markeredgewidth() == 0.5
               for tick in ax.xaxis.get_major_ticks()
               )
    assert figure_lines_fitter(fig, 0.5, 1.5) == 0  # nothing left to change

    # ---- 4 Fitting the margins keeps the lines too -----------------------------------
    again = Figure()
    line, = again.subplots().plot([0, 1], [0, 1], linewidth=0.2)
    figure_canvas_fitter(again, 3.0, line_limits_pt=(0.5, None))
    assert line.get_linewidth() == 0.5


# ---- test_axes_are_fitted_into_their_room --------------------------------------------
def test_axes_are_fitted_into_their_room() -> None:
    """
    ---- Summary ----
    Main function to check the room a plot keeps for its own text: axes that fill
    their room are made smaller until the tick numbers and axis titles are inside it;
    two sets of axes one above the other keep their shares of the height; axes whose
    text is already inside are left where they are.

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
    The room is x 0.1 to 0.6 and y 0.2 to 0.9 of the figure. The upper axes take the
    top 0.42 of its height and the lower the bottom 0.28, so the upper is 1.5 times
    as tall as the lower, before and after.

    ---- Helpers ----
    None.
    """

    # ---- 1 Two sets of axes that fill the room ---------------------------------------
    room = (0.1, 0.2, 0.6, 0.9)
    fig = Figure(figsize=(6.0, 4.0))
    lower = fig.add_axes((0.1, 0.2, 0.5, 0.28))
    upper = fig.add_axes((0.1, 0.48, 0.5, 0.42))
    for ax in (lower, upper):
        ax.plot([0, 10], [0, 123456])
        ax.set_ylabel('Oxygen (µM)')
    lower.set_xlabel('Time (min)')
    axes_room_fitter(fig, [lower, upper], room)
    renderer = fig._get_renderer()
    for ax in (lower, upper):
        tight = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
        assert room[0] - 1e-3 <= tight.x0 and tight.x1 <= room[2] + 1e-3
        assert room[1] - 1e-3 <= tight.y0 and tight.y1 <= room[3] + 1e-3
    low, high = lower.get_position(), upper.get_position()
    assert low.x0 > 0.1 and low.y0 > 0.2  # room made for the numbers and the titles
    assert low.x0 == pytest.approx(high.x0) and low.width == pytest.approx(high.width)
    assert high.height / low.height == pytest.approx(1.5)
    assert high.y0 == pytest.approx(low.y1)

    # ---- 2 Axes whose text is inside the room stay where they are --------------------
    small = fig.add_axes((0.75, 0.4, 0.1, 0.2))
    axes_room_fitter(fig, [small], (0.62, 0.2, 1.0, 0.9))
    assert small.get_position().bounds == pytest.approx((0.75, 0.4, 0.1, 0.2))
    axes_room_fitter(fig, [], room)  # nothing to fit


# ---- test_fonts_a_figure_names -------------------------------------------------------
def test_fonts_a_figure_names(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ---- Summary ----
    Main function to check the fonts a figure names, with the fonts on the computer
    stood in for: the journal's first installed font, then the installed fallback
    fonts; never the journal's second choice once the first is there; a name kept
    once; the plotting library's own font when none is installed.

    ---- Inputs ----
    monkeypatch : pytest.MonkeyPatch
        pytest's tool to stand in for the fonts on the computer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. figure_layout.findfont is stood in for during the test.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    installed = set()

    def font_finder(family: str, fallback_to_default: bool = True) -> str:
        if family not in installed:
            raise ValueError(f'{family} is not installed.')
        return family + '.ttf'

    monkeypatch.setattr(figure_layout, 'findfont', font_finder)
    journal, fallbacks = ['Arial', 'Helvetica'], ('Liberation Sans', 'DejaVu Sans')

    # a Mac: both of the journal's fonts, one fallback
    installed.update({'Arial', 'Helvetica', 'DejaVu Sans'})
    assert font_family_lister(journal, fallbacks) == ['Arial', 'DejaVu Sans']
    assert font_family_lister(journal) == ['Arial']
    # the journal's first font is missing: its second is the one drawn in
    installed.discard('Arial')
    assert font_family_lister(journal, fallbacks) == ['Helvetica', 'DejaVu Sans']
    # every font, in the order given
    installed.update({'Arial', 'Liberation Sans'})
    assert font_family_lister(journal, fallbacks) == ['Arial',
                                                      'Liberation Sans',
                                                      'DejaVu Sans',
                                                      ]
    # a journal whose font is a fallback too
    assert font_family_lister(['DejaVu Sans'], fallbacks) == ['DejaVu Sans',
                                                              'Liberation Sans',
                                                              ]
    # none of the journal's fonts, then nothing at all
    installed.difference_update({'Arial', 'Helvetica'})
    assert font_family_lister(journal, fallbacks) == ['Liberation Sans', 'DejaVu Sans']
    installed.clear()
    assert font_family_lister(journal, fallbacks) == ['sans-serif']
    assert font_family_lister([], ()) == ['sans-serif']


# ---- test_a_small_legend_hides_nothing -----------------------------------------------
def test_a_small_legend_hides_nothing() -> None:
    """
    ---- Summary ----
    Main function to check the small legend of a plot: none for one named line; in
    the top right corner when nothing is drawn there; in the next corner when a line
    runs through the top right; and under the axes, below the tick numbers and the
    axis title, when a line runs through every corner.

    ---- Inputs ----
    None.

    ---- Globals read ----
    settings.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Two lines along the bottom of the axes leave every upper corner free: the legend
    goes top right. A line from bottom left to top right covers the top right corner
    and leaves the top left free. Lines along the top and the bottom cover all four
    corners.

    ---- Helpers ----
    None.
    """

    style = figure_style_builder(settings.JOURNAL_SPECS['nature'])
    fonts = ['sans-serif']

    # ---- axes_maker ------------------------------------------------------------------
    def axes_maker(lines: list) -> tuple:
        fig = Figure(figsize=(3.0, 2.0))
        ax = fig.add_axes((0.2, 0.3, 0.7, 0.6))
        for number, (x, y) in enumerate(lines, start=1):
            ax.plot(x, y, label=f'set {number}')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xlabel('Time (min)')
        return fig, ax

    # ---- 1 One named line: no legend -------------------------------------------------
    fig, ax = axes_maker([([0, 10], [1, 1])])
    assert plot_legend_placer(fig, ax, style, fonts) is None
    assert ax.get_legend() is None

    # ---- 2 Nothing in the top right: the legend goes there ---------------------------
    fig, ax = axes_maker([([0, 10], [1, 1]), ([0, 10], [2, 2])])
    legend = plot_legend_placer(fig, ax, style, fonts)
    renderer = fig._get_renderer()
    box, frame = legend.get_window_extent(renderer), ax.get_window_extent(renderer)
    assert [text.get_text() for text in legend.get_texts()] == ['set 1', 'set 2']
    assert box.x1 > frame.x0 + 0.8 * frame.width and box.y1 > frame.y0 + 0.8 * frame.height
    assert box.x1 <= frame.x1 and box.y1 <= frame.y1
    assert all(text.get_fontsize() == style['fonts']['tick'] for text in legend.get_texts())

    # ---- 3 A line through the top right: the top left --------------------------------
    fig, ax = axes_maker([([0, 10], [0, 10]), ([0, 10], [1, 1])])
    legend = plot_legend_placer(fig, ax, style, fonts)
    renderer = fig._get_renderer()
    box, frame = legend.get_window_extent(renderer), ax.get_window_extent(renderer)
    assert box.x0 < frame.x0 + 0.2 * frame.width and box.y1 > frame.y0 + 0.8 * frame.height

    # ---- 4 A line through every corner: under the axes -------------------------------
    fig, ax = axes_maker([([0, 10], [9.7, 9.7]), ([0, 10], [0.3, 0.3])])
    labels_bottom = ax.get_tightbbox(fig._get_renderer()).y0
    legend = plot_legend_placer(fig, ax, style, fonts)
    renderer = fig._get_renderer()
    box, frame = legend.get_window_extent(renderer), ax.get_window_extent(renderer)
    assert box.y1 < labels_bottom < frame.y0  # below the numbers and the axis title
    assert frame.x0 < (box.x0 + box.x1) / 2 < frame.x1
