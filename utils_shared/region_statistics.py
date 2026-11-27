"""
The numbers of the plots per region of a dataset figure: the value of each experiment in an averaging region, the mean, SD and SEM of each set, the t-tests between sets and between two regions, the Holm correction, the marks and the legend sentence.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from itertools import combinations
from typing import Dict, List, Optional, Sequence

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
from scipy import stats as scipy_stats

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.trace_alignment import trace_reader


# ---- CONSTANTS -----------------------------------------------------------------------
# The kinds of averaging region a plot can read, and the start of the name of the
# regions of each kind in experiment['averages'] (DATA_FORMAT.md); region 0 is the
# baseline of both kinds ('average0')
REGION_STARTS = {'settled': 'average', 'quick': 'quick'}
BASELINE_NAME = 'average0'
# The t-tests between two sets, (the role kept, the words shown); the first is the one
# a new plot starts at
TEST_CHOICES = (('student', "Student's t-test"), ('welch', "Welch's t-test"))
TEST_WORDS = {'student': "Student's t-test (two-tailed, unpaired)",
              'welch': "Welch's t-test (two-tailed, unpaired, unequal variances)",
              }
PAIRED_WORDS = 'a paired t-test (two-tailed)'
# What the bars show, and how a difference is marked
ERROR_CHOICES = (('sem', 'SEM'), ('sd', 'SD'))
MARK_CHOICES = (('stars', 'Stars'), ('p', 'p values'), ('none', 'None'))
# A corrected p value under the first number gets the stars beside it; one that is not
# under SIGNIFICANT_BELOW gets no mark at all
STAR_LIMITS = ((0.001, '***'), (0.01, '**'), (0.05, '*'))
SIGNIFICANT_BELOW = 0.05
STARS_WORDS = '* p < 0.05, ** p < 0.01, *** p < 0.001'
P_WORDS = 'the p values under 0.05 are shown'


# ---- NUMBER HELPERS ------------------------------------------------------------------


# ---- _finite_values_lister -----------------------------------------------------------
def _finite_values_lister(values: Sequence[Optional[float]]) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to keep the values of a set that are numbers: an experiment
    without a value (None, NaN) is left out.

    ---- Inputs ----
    values : Sequence[Optional[float]]
        One value per experiment.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        The values that are numbers, shape (n,).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    numbers = np.array([np.nan if value is None else float(value) for value in values],
                       dtype=float,
                       )
    return numbers[np.isfinite(numbers)]


# ---- _p_value_finder -----------------------------------------------------------------
def _p_value_finder(t_value: float, freedom: float) -> float:
    """
    ---- Summary ----
    Helper function to find the two-tailed p value of a t.

    ---- Inputs ----
    t_value : float
        The t of the test.
    freedom : float
        Its degrees of freedom.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The chance of a t at least that far from 0, either side, when the two means
        are really the same.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    p = 2 x (the share of the t distribution with that many degrees of freedom that
    lies above |t|).

    ---- Helpers ----
    None.
    """

    return float(2.0 * scipy_stats.t.sf(abs(t_value), freedom))


# ---- _region_namer -------------------------------------------------------------------
def _region_namer(region: int, kind: str) -> str:
    """
    ---- Summary ----
    Helper function to name an averaging region as experiment['averages'] does.

    ---- Inputs ----
    region : int
        0 for the baseline, 1 for the region of the first addition, and so on.
    kind : str
        'settled' or 'quick'.

    ---- Globals read ----
    BASELINE_NAME, REGION_STARTS.

    ---- Outputs ----
    str
        'average0', 'average2', 'quick1' ... Raises ValueError for a kind that is
        neither, or a region under 0.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if kind not in REGION_STARTS:
        raise ValueError(f'The kind of averaging region {kind!r} is not known.')
    if region < 0:
        raise ValueError(f'There is no averaging region number {region}.')
    return BASELINE_NAME if region == 0 else f'{REGION_STARTS[kind]}{region}'


# ---- SENTENCE HELPERS ----------------------------------------------------------------


# ---- _counts_teller ------------------------------------------------------------------
def _counts_teller(columns: Sequence[dict]) -> Dict[str, List[int]]:
    """
    ---- Summary ----
    Helper function to list how many experiments each set has in each column of a
    plot.

    ---- Inputs ----
    columns : Sequence[dict]
        The columns of the plot (plot_statistics, DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, List[int]]
        {the name of the set: its n in each column that has it}, in the order first
        seen.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    counts: Dict[str, List[int]] = {}
    for column in columns:
        for one in column['sets']:
            counts.setdefault(one['name'], []).append(one['n'])
    return counts


# ---- _names_joiner -------------------------------------------------------------------
def _names_joiner(names: Sequence[str]) -> str:
    """
    ---- Summary ----
    Helper function to write a list of names as words: 'a', 'a and b', 'a, b and c'.

    ---- Inputs ----
    names : Sequence[str]
        The names, at least one.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The names in one phrase.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} and {names[-1]}"


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- legend_sentence_writer ----------------------------------------------------------
def legend_sentence_writer(statistics: dict,
                           error: str = 'sem',
                           test: str = 'student',
                           marks: str = 'stars',
                           ) -> str:
    """
    ---- Summary ----
    Main function to write the sentences of a plot per region for the legend of the
    paper: what the dots and bars are, how many experiments each set has, which set
    has only one, and which test and correction the marks come from.

    ---- Inputs ----
    statistics : dict
        The numbers of the plot (plot_statistics, DATA_FORMAT.md), from
        plot_statistics_builder or paired_statistics_builder.
    error : str
        What the bars show, 'sem' or 'sd'; not used for a paired plot, which has no
        bars.
    test : str
        The test between sets, 'student' or 'welch'; not used for a paired plot.
    marks : str
        'stars', 'p' or 'none'; with 'none' nothing is said of the test.

    ---- Globals read ----
    ERROR_CHOICES, P_WORDS, PAIRED_WORDS, STARS_WORDS, TEST_WORDS.

    ---- Outputs ----
    str
        The sentences, on one line. Raises ValueError for bars, a test or marks that
        are not known.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _counts_teller
    _names_joiner
    """

    # ---- 1 The words asked for -------------------------------------------------------
    error_words = dict(ERROR_CHOICES)
    if error not in error_words:
        raise ValueError(f'The bars {error!r} are not known.')
    if test not in TEST_WORDS:
        raise ValueError(f'The test {test!r} is not known.')
    if marks not in ('stars', 'p', 'none'):
        raise ValueError(f'The marks {marks!r} are not known.')
    is_paired = bool(statistics.get('is_paired'))

    # ---- 2 What is drawn, and how many experiments each set has ----------------------
    counts = _counts_teller(statistics['columns'])
    told = []
    for name, numbers in counts.items():
        low, high = min(numbers), max(numbers)
        told.append(
            f'{name} n = {low}' if low == high else f'{name} n = {low} to {high}',
            )
    if is_paired:
        drawn = 'Each line is one experiment, and the mean of each set is marked'
    else:
        drawn = ('Each dot is one experiment, and the bars are the mean ± '
                 f'{error_words[error]} of each set')
    sentences = [f"{drawn} ({', '.join(told)})." if told else f'{drawn}.']

    # ---- 3 The sets with one experiment ----------------------------------------------
    singles = [name for name, numbers in counts.items() if min(numbers) == 1]
    if singles:
        names, is_many = _names_joiner(singles), len(singles) > 1
        has = 'each have' if is_many else 'has'
        if is_paired:
            end = 'they were not tested' if is_many else 'it was not tested'
            sentences.append(f'{names} {has} one experiment, so {end}.')
        else:
            end = ('they have no bar and were not tested'
                   if is_many
                   else 'it has no bar and was not tested'
                   )
            sentences.append(f'{names} {has} one experiment in a region, so {end}.')

    # ---- 4 The test, the correction and the marks ------------------------------------
    count = len(statistics['tests'])
    if marks != 'none' and count:
        if is_paired:
            compared = ('The two regions of each set were compared with '
                        f'{PAIRED_WORDS}')
        else:
            compared = f'The sets were compared with {TEST_WORDS[test]}'
        if count > 1:
            compared += f', with the Holm correction across the {count} tests of the plot'
        shown = STARS_WORDS if marks == 'stars' else P_WORDS
        sentences.append(f'{compared}: {shown}; a comparison without a mark gave '
                         'p ≥ 0.05.',
                         )
    return ' '.join(sentences)


# ---- p_value_marker ------------------------------------------------------------------
def p_value_marker(p_value: Optional[float], marks: str = 'stars') -> str:
    """
    ---- Summary ----
    Main function to give the mark drawn over a comparison: stars or the p value
    where the two differ, and nothing where they do not (never "ns").

    ---- Inputs ----
    p_value : Optional[float]
        The corrected p value of the comparison; None for one that was not tested.
    marks : str
        'stars', 'p' or 'none'.

    ---- Globals read ----
    SIGNIFICANT_BELOW, STAR_LIMITS.

    ---- Outputs ----
    str
        '***', '**' or '*'; or 'p = 0.018', 'p < 0.001'; '' for no mark. Raises
        ValueError for marks that are not known.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Stars: *** for p < 0.001, ** for p < 0.01, * for p < 0.05 (MATHS.md section
    11.6).

    ---- Helpers ----
    None.
    """

    if marks not in ('stars', 'p', 'none'):
        raise ValueError(f'The marks {marks!r} are not known.')
    if (marks == 'none'
            or p_value is None
            or not np.isfinite(p_value)
            or p_value >= SIGNIFICANT_BELOW):
        return ''
    if marks == 'stars':
        return next(stars for limit, stars in STAR_LIMITS if p_value < limit)
    smallest = STAR_LIMITS[0][0]
    return f'p < {smallest:g}' if p_value < smallest else f'p = {p_value:.3f}'


# ---- p_values_corrector --------------------------------------------------------------
def p_values_corrector(p_values: Sequence[Optional[float]]) -> List[Optional[float]]:
    """
    ---- Summary ----
    Main function to correct the p values of every test of one plot with Holm's
    rule, so the chance of a mark by luck anywhere on the plot stays under 1 in 20.

    ---- Inputs ----
    p_values : Sequence[Optional[float]]
        The p value of each test; None for a comparison that was not tested, which
        is not counted.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Optional[float]]
        The corrected p values, in the order given; None where None was given.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With the m p values sorted smallest first, p_(1) <= ... <= p_(m): corrected
    p_(i) = min(1, max(corrected p_(i-1), (m - i + 1) x p_(i))) (MATHS.md section
    11.5).

    ---- Helpers ----
    None.
    """

    places = [place for place, value in enumerate(p_values) if value is not None]
    places.sort(key=lambda place: p_values[place])
    corrected: List[Optional[float]] = [None] * len(p_values)
    highest = 0.0
    for rank, place in enumerate(places):
        highest = max(highest, min(1.0, (len(places) - rank) * float(p_values[place])))
        corrected[place] = highest
    return corrected


# ---- paired_statistics_builder -------------------------------------------------------
def paired_statistics_builder(sets: Sequence[dict], labels: Sequence[str]) -> dict:
    """
    ---- Summary ----
    Main function to work out the numbers of a Before and after plot: each set in
    its two regions, the paired t-test between the two regions inside each set, and
    the Holm correction across the sets.

    ---- Inputs ----
    sets : Sequence[dict]
        One per set: 'name', and 'before' and 'after', the value of each of its
        experiments in the first and in the second region, in the same order (None
        for an experiment without one).
    labels : Sequence[str]
        The names of the two regions.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The numbers of the plot (plot_statistics, DATA_FORMAT.md) with 'is_paired'
        True: two columns, and one test per set with at least two experiments that
        have both values, each with the 'set' it is of.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See pairs_tester and p_values_corrector.

    ---- Helpers ----
    p_values_corrector
    pairs_tester
    set_statistics_calculator
    """

    columns = [{'label': label,
                'sets': [dict(set_statistics_calculator(one[key]), name=one['name'])
                         for one in sets
                         ],
                }
               for label, key in zip(labels, ('before', 'after'))
               ]
    tests = []
    for one in sets:
        result = pairs_tester(one['before'], one['after'])
        if result is not None:
            tests.append(dict(result, set=one['name']))
    corrected = p_values_corrector([result['p'] for result in tests])
    for result, value in zip(tests, corrected):
        result['p_corrected'] = value
    return {'columns': columns, 'tests': tests, 'is_paired': True}


# ---- pairs_tester --------------------------------------------------------------------
def pairs_tester(before: Sequence[Optional[float]],
                 after: Sequence[Optional[float]],
                 ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to test whether the experiments of one set changed from one region
    to another, with the paired t-test: each experiment is compared with itself.

    ---- Inputs ----
    before : Sequence[Optional[float]]
        The value of each experiment in the first region; None for none.
    after : Sequence[Optional[float]]
        Its value in the second region, in the same order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[dict]
        't', 'df', 'p' (two-tailed, not corrected) and 'n' (the experiments with
        both values); None when fewer than two experiments have both, or when every
        experiment changed by exactly the same amount (no spread to test against).
        Raises ValueError when the two lists are not the same length.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    d_i = after_i - before_i; t = mean(d) / (SD(d) / sqrt(n)); df = n - 1 (MATHS.md
    section 11.4).

    ---- Helpers ----
    _p_value_finder
    """

    if len(before) != len(after):
        raise ValueError('The two regions do not have the same number of experiments.')
    changes = _finite_values_lister([None
                                     if first is None or second is None
                                     else float(second) - float(first)
                                     for first, second in zip(before, after)
                                     ],
                                    )
    count = len(changes)
    if count < 2:
        return None
    error = float(np.std(changes, ddof=1)) / np.sqrt(count)
    if error == 0.0:
        return None
    t_value = float(np.mean(changes)) / error
    return {'t': t_value,
            'df': float(count - 1),
            'p': _p_value_finder(t_value, count - 1),
            'n': count,
            }


# ---- plot_statistics_builder ---------------------------------------------------------
def plot_statistics_builder(columns: Sequence[dict], test: str = 'student') -> dict:
    """
    ---- Summary ----
    Main function to work out the numbers of a plot per region: the mean, SD and SEM
    of each set in each column (a region, or a time point), the t-test of each pair
    of sets in each column, and the Holm correction across every test of the plot.

    ---- Inputs ----
    columns : Sequence[dict]
        One per column of the plot: 'label' (its name) and 'sets', each with its
        'name' and 'values' (one per experiment; None for an experiment without
        one).
    test : str
        'student' or 'welch'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The numbers of the plot (plot_statistics, DATA_FORMAT.md): 'columns', each
        with its 'label' and the statistics of its 'sets'; 'tests', one per pair of
        sets that could be tested, with its 'column' (from 0), 'first' and 'second'
        (the names of the two sets), 't', 'df', 'p' and 'p_corrected'; 'is_paired'
        False.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    See set_statistics_calculator, sets_tester and p_values_corrector.

    ---- Helpers ----
    p_values_corrector
    set_statistics_calculator
    sets_tester
    """

    # ---- 1 Each set in each column ---------------------------------------------------
    worked = [{'label': column['label'],
               'sets': [dict(set_statistics_calculator(one['values']), name=one['name'])
                        for one in column['sets']
                        ],
               }
              for column in columns
              ]

    # ---- 2 Each pair of sets in each column ------------------------------------------
    tests = []
    for place, column in enumerate(worked):
        for first, second in combinations(column['sets'], 2):
            result = sets_tester(first['values'], second['values'], test)
            if result is not None:
                tests.append(dict(result,
                                  column=place,
                                  first=first['name'],
                                  second=second['name'],
                                  ),
                             )

    # ---- 3 The correction across every test of the plot ------------------------------
    corrected = p_values_corrector([result['p'] for result in tests])
    for result, value in zip(tests, corrected):
        result['p_corrected'] = value
    return {'columns': worked, 'tests': tests, 'is_paired': False}


# ---- region_value_reader -------------------------------------------------------------
def region_value_reader(experiment: Optional[dict],
                        trace: str,
                        value: str,
                        region: int,
                        kind: str = 'settled',
                        is_per_od: bool = False,
                        ) -> Optional[float]:
    """
    ---- Summary ----
    Main function to read the value of one experiment in one averaging region: the
    mean, over the region, of the trace in the value picked.

    ---- Inputs ----
    experiment : Optional[dict]
        The slim copy of the experiment (page_experiment, DATA_FORMAT.md); None for
        an experiment that is not there.
    trace : str
        The trace, as trace_reader takes it: the OCR, Δψ or a haem.
    value : str
        The value it is shown in, as trace_reader takes it. A haem has no % of
        baseline and no change from baseline.
    region : int
        0 for the baseline, 1 for the region of the first addition, and so on.
    kind : str
        'settled' or 'quick'; the baseline is the same for both.
    is_per_od : bool
        True when the run shows its haems per OD.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The value, in the unit of the value picked; None when the file does not have
        that region (too few additions, a region that does not fit or was left out),
        does not have the trace in that value, or has no measurement inside the
        region.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    value = (y_1 + ... + y_k) / k, with y the trace in the value picked at the k
    times inside the region that have a number (MATHS.md section 11.1).

    ---- Helpers ----
    _region_namer
    trace_reader
    """

    name = _region_namer(region, kind)
    if experiment is None:
        return None
    window = ((experiment.get('averages') or {}).get('windows') or {}).get(name)
    if window is None:
        return None
    read = trace_reader(experiment, trace, value, is_per_od)
    if read is None:
        return None
    times, values = read['times_min'], read['values']
    inside = ((times >= window['start_time'])
              & (times <= window['end_time'])
              & np.isfinite(values)
              )
    if not inside.any():
        return None
    return float(np.mean(values[inside]))


# ---- set_statistics_calculator -------------------------------------------------------
def set_statistics_calculator(values: Sequence[Optional[float]]) -> dict:
    """
    ---- Summary ----
    Main function to work out the mean, the spread (SD) and the standard error of
    the mean (SEM) of the experiments of one set.

    ---- Inputs ----
    values : Sequence[Optional[float]]
        The value of each experiment; None for an experiment without one, which is
        not counted.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        'values' (the numbers counted, List[float]), 'n', 'mean', 'sd' and 'sem';
        the mean is NaN for an empty set, the SD and the SEM for a set of fewer than
        two.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mean = (y_1 + ... + y_n) / n; SD = sqrt(((y_1 - mean)² + ... + (y_n - mean)²) /
    (n - 1)); SEM = SD / sqrt(n) (MATHS.md section 11.2).

    ---- Helpers ----
    _finite_values_lister
    """

    numbers = _finite_values_lister(values)
    count = len(numbers)
    mean = float(np.mean(numbers)) if count else np.nan
    spread = float(np.std(numbers, ddof=1)) if count > 1 else np.nan
    return {'values': [float(number) for number in numbers],
            'n': count,
            'mean': mean,
            'sd': spread,
            'sem': spread / np.sqrt(count) if count > 1 else np.nan,
            }


# ---- set_values_lister ---------------------------------------------------------------
def set_values_lister(sets: Sequence[dict],
                      experiments: Dict[str, dict],
                      trace: str,
                      value: str,
                      region: int,
                      kind: str = 'settled',
                      is_per_od: bool = False,
                      ) -> List[dict]:
    """
    ---- Summary ----
    Main function to give each set of a plot the value of each of its experiments in
    one averaging region.

    ---- Inputs ----
    sets : Sequence[dict]
        The sets of the plot, from the set-up table (plot_set, DATA_FORMAT.md); not
        changed.
    experiments : Dict[str, dict]
        {experiment name: its slim copy (page_experiment, DATA_FORMAT.md)}.
    trace : str
        The trace, as region_value_reader takes it.
    value : str
        The value it is shown in.
    region : int
        0 for the baseline, 1 for the region of the first addition, and so on.
    kind : str
        'settled' or 'quick'.
    is_per_od : bool
        True when the run shows its haems per OD.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[dict]
        A copy of each set with 'values': one per experiment of its 'names', in that
        order, None for an experiment that is not there or has no value in that
        region.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    region_value_reader
    """

    return [dict(one,
                 values=[region_value_reader(experiments.get(name),
                                             trace,
                                             value,
                                             region,
                                             kind,
                                             is_per_od,
                                             )
                         for name in one['names']
                         ],
                 )
            for one in sets
            ]


# ---- sets_tester ---------------------------------------------------------------------
def sets_tester(first: Sequence[Optional[float]],
                second: Sequence[Optional[float]],
                test: str = 'student',
                ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to test whether two sets of experiments differ, with Student's
    t-test (the two sets are taken to scatter equally, and their spreads are pooled)
    or Welch's (each set keeps its own spread).

    ---- Inputs ----
    first : Sequence[Optional[float]]
        The value of each experiment of one set; None for none.
    second : Sequence[Optional[float]]
        The same for the other set.
    test : str
        'student' or 'welch'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[dict]
        't', 'df' and 'p' (two-tailed, not corrected); None when either set has
        fewer than two experiments, or when neither set has any spread. Raises
        ValueError for a test that is not known.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    With n, m and s the number, mean and SD of each set, t = (m1 - m2) / e.
    Student's: sp² = ((n1 - 1) s1² + (n2 - 1) s2²) / (n1 + n2 - 2); e = sqrt(sp² x
    (1 / n1 + 1 / n2)); df = n1 + n2 - 2. Welch's: e = sqrt(s1² / n1 + s2² / n2);
    df = (s1² / n1 + s2² / n2)² / ((s1² / n1)² / (n1 - 1) + (s2² / n2)² / (n2 - 1))
    (MATHS.md section 11.3).

    ---- Helpers ----
    _finite_values_lister
    _p_value_finder
    """

    if test not in ('student', 'welch'):
        raise ValueError(f'The test {test!r} is not known.')
    one, other = _finite_values_lister(first), _finite_values_lister(second)
    count_1, count_2 = len(one), len(other)
    if count_1 < 2 or count_2 < 2:
        return None
    share_1 = float(np.var(one, ddof=1)) / count_1
    share_2 = float(np.var(other, ddof=1)) / count_2
    if test == 'student':
        freedom = float(count_1 + count_2 - 2)
        pooled = ((count_1 - 1) * share_1 * count_1
                  + (count_2 - 1) * share_2 * count_2
                  ) / freedom
        error = np.sqrt(pooled * (1.0 / count_1 + 1.0 / count_2))
    else:
        error = np.sqrt(share_1 + share_2)
    if error == 0.0:
        return None
    if test == 'welch':
        freedom = (share_1 + share_2) ** 2 / (share_1 ** 2 / (count_1 - 1)
                                              + share_2 ** 2 / (count_2 - 1)
                                              )
    t_value = (float(np.mean(one)) - float(np.mean(other))) / float(error)
    return {'t': t_value, 'df': float(freedom), 'p': _p_value_finder(t_value, freedom)}
