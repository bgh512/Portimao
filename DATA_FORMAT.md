# Portimao - Data Format

## 1. Structures

### 1.1 Dictionaries

#### `experiment`

One experiment (one `.paf` file) as passed between the processing functions. Created by `experiment_paf_loader` and extended by the processing steps. Keys marked optional exist only when the matching analysis was switched on.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'experiment_name'` | str | | | File stem of the `.paf` file |
| `'metadata'` | dict | | | What is known about the file and the run (see `metadata`) |
| `'CcO2'` | pd.DataFrame | (n_points, 2) | µM | Measured O2: `Time (min)` and the measurement column, titled with the unit stored in the file (`Measured O2 (µM)`; `uM` when the file stores none). Missing when the file has no such trace (a warning is printed) |
| `'CsO2'` | pd.DataFrame | (n_points, 2) | µM | Set O2, titled in the same way (`Set O2 (µM)`). Missing when the file has no such trace |
| `'VoO2'` | pd.DataFrame | (n_ocr_points, 2) | µM/min | Oxygen consumption rate (OCR): `Time (min)` and `VoO2`. Always there: a file without it is refused. It has fewer rows than the oxygen tables, as the time points where the instrument has no OCR value (the start of a recording, and the end when the trace is shorter than the clock) are left out |
| `'VoO2_OD'` | pd.DataFrame | (n_points, 2) | | Optional. OCR divided by dilution factor x OD x volume |
| `'VoO2_percent'` | pd.DataFrame | (n_points, 2) | % | Optional. OCR scaled to 0-100 % of its range |
| `'haem_conc'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mM for a 1 cm light path | Optional. Fitted haem concentrations; columns `Time (min)`, `spectrum_index` and one per haem. The fit shapes times `HAEM_FACTOR` are in OD/mM/cm, so the amounts are mM x cm; with components found from data they are in arbitrary units. Fitted beside the background named by the answer `'haem_background'` (kept with the dataset's answers; the standard, in `config.DEFAULT_ANSWERS`, is `rowan_scatter`; the choices are `BACKGROUND_LABELS` in `spectral_decomposer.py`). When the change from the first spectrum is fitted, these are the changes from the first spectrum (the first kept, in a trimmed run) |
| `'haem_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. Haem concentration x peak of the fit spectrum; a change from the first spectrum when `haem_conc` is |
| `'haem_delta_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. ΔD, the change from the start: `haem_abs` shifted so that each haem is 0 where it starts, the median of its first 50 spectra with a value after the ignored start (`REFERENCE_WINDOW_POINTS` in `config.py`). `attrs['delta_abs_baseline']` holds what was subtracted: `'level_by_haem'` (mOD), `'window_by_haem'` (the first and last time, in min, of the spectra each start was taken from), `'window_points'` and `'window_seconds'`. The maths is in `MATHS.md` |
| `'haem_OD'`, `'haem_abs_OD'`, `'haem_delta_abs_OD'` | pd.DataFrame | (n_spectra, 2 + n_haems) | | Optional. The matching tables divided by dilution factor x OD x volume |
| `'haem_percent'` | pd.DataFrame | (n_spectra, 2 + n_haems) | % | Optional: only for a file with both an oxidised and a reduced region. % oxidised: `haem_abs` put between each haem's reduced level (0 %) and its oxidised level (100 %) by `percent_oxidised_calculator`; values above 100 and below 0 are kept, and a haem whose two levels are equal has an empty column. `attrs['percent_oxidised']` holds the levels used. The maths is in `MATHS.md` |
| `'haem_levels'` | dict | | mOD, min | Optional: only for a file with both regions (`haem_levels_finder`). `'oxidised'` and `'reduced'`: `{haem: its level}`, the median of `haem_abs` in that region (mOD); `'oxidised_region'` and `'reduced_region'`: `(start, end)` of the region on the time of the trimmed data (min), kept within the used part of the run |
| `'delta_psi'` | pd.DataFrame | (n_spectra, 5) | mV | Optional: only when the answer `'delta_psi'` is on, for a file with `haem_percent` whose fit has one bH and one bL. Columns `Time (min)`, `spectrum_index`, `Δψ (mV)` (the membrane potential), `Eh bH (mV)` and `Eh bL (mV)` (the redox potential at each haem), built by `delta_psi_table_builder`; empty (NaN) in a spectrum where bH or bL is less than 10 % or more than 90 % reduced (`config.DELTA_PSI_REDUCED_LIMITS_PERCENT`). `attrs['delta_psi']` holds the numbers used: `'midpoints_mV'`, `'share'`, `'temperature_c'`, `'limits_percent'`, `'bH'` and `'bL'` (the two columns of `haem_percent`) and `'spectra_with_value'`. The maths is in `MATHS.md` |
| `'raw_spectra'` | dict | | | `{dataset: {'wavelengths', 'spectrum_indices', 'time', 'transmission', 'intensity', 'attenuation'}}`; every spectrum has a time, and the transmission is NaN where it cannot be worked out (zero counts in the reference); dropped after the special figures are prepared |
| `'averages'` | dict | | | Event-window statistics (see `averages`) |

Example:

```python
experiment = {'experiment_name': 'control_7hours',
              'metadata': metadata,
              'VoO2': vo2_table,
              'averages': averages,
              }
```

#### `metadata`

What is known about one experiment, stored as `experiment['metadata']`. The first four keys are set by `experiment_paf_loader`; the others are added while the experiment is processed and exist only from that step on.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'paf_file'` | str | | | Name of the `.paf` file, with its extension |
| `'events'` | List[dict] | (n_events,) | | The additions in time order (see `event`); once the answers are merged, without the ignored ones |
| `'acquisition'` | List[dict] | (n_datasets,) | | One entry per spectrometer: `'dataset'`, `'spectrometer'` (its name in the file), `'frames'`, `'wavelengths'` (their number), `'wavelength_range_nm'` (first and last) and, when the file gives them, `'centre_wavelength_nm'` and `'slit_um'` |
| `'notes'` | str | | | The notes typed in the instrument software, as plain text; empty when there are none |
| `'OD'`, `'volume'`, `'dilution_factor'` | float | | | Optional. As entered by the user, used for the OD scaling |
| `'ignored_events'` | List[dict] | | | The additions the user chose to ignore; they are kept only for the workbook. After a start trim their times are counted from the new 0 like those of the other additions, so one made before the cut has a negative time |
| `'trimmed_before_minutes'`, `'trimmed_after_minutes'` | float | | min | Optional. Where the recording was cut, on the original time |
| `'ignore_first_minutes'`, `'ignore_last_minutes'` | float | | min | Start and end left out of the averages and references |
| `'fit_file'` | str or None | | | Fit (preset or fit file) of the decomposition, or `Your own haems: <files without .csv>` for haems ticked under Build a fit (`fit_describer`); None when the haems were not decomposed |
| `'processed'` | str | | | Date and time of the run, `YYYY-MM-DD HH:MM` |

#### `event`

One addition (a text event of the instrument software). Created by `experiment_paf_loader`, one per addition stored inside the recording; an addition stored outside it is left out, with a warning when the files are first read.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'datapoint'` | int | | | Spectrum number stored with the addition, counted from 1 |
| `'text'` | str | | | What was typed in the instrument software, e.g. `1ul 8mm nd-011992`. The file holds no concentration |
| `'label'` | str | | | Name shown in the figures: the text, until the user renames it |
| `'concentration_uM'` | float or None | | µM | Final concentration entered by the user; None when none was given |
| `'time'` | float | | min | Time of the addition; counted from the new 0 after a start trim |
| `'row_index'` | int | | | Row of the time base, `datapoint` - 1; removed when the experiment is trimmed |
| `'ignored'` | bool | | | Set when the answers are merged: True for an addition the user chose to ignore |

#### `experiment_summary`

Quick description of one `.paf` file, read before the questions are asked. Created by `experiment_summary_reader`, which refuses a file that could not be processed later (one without an OCR trace, for example), so such a file is skipped before any question is asked.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'name'` | str | | | File stem |
| `'duration_min'` | float | | min | Length of the recording |
| `'frames'` | int | | | Number of time points |
| `'datasets'` | List[str] | | | Spectral datasets in the file |
| `'spectra_shapes'` | dict | | | `{dataset: [number of spectra, number of wavelengths]}`, read from the headers without reading the spectra; gives the size of the spectra csv files offered by the export of the import |
| `'events'` | List[dict] | | | The additions stored inside the recording, in the order of their spectrum numbers, each with `'name'` (the software's name for it, `Event 1`), `'text'`, `'datapoint'`, `'time'` (min) and `'row_index'` as in `event`. They are the same additions, with the same times, as `experiment_paf_loader` gives |
| `'traces'` | List[str] | | | Names of the recorded traces |
| `'ocr_check'` | dict | | | The check of the instrument's OCR against ours (`ocr_check`); a warning is printed when it disagrees or cannot be done |

#### `ocr_check`

Result of checking the instrument's OCR against our own calculation from its traces. Created by `ocr_checker` (`utils_shared/ocr_checking.py`) once per file, in `experiment_summary_reader`, and turned into the warning by `ocr_check_describer`. How it is worked out is under "Our OCR check" below.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'is_checked'` | bool | | | True when the six traces and the permeability are there and the recording is long enough to compare (100 points) |
| `'is_agreeing'` | bool | | | True when every part agrees; False when the file was not checked |
| `'reason'` | str | | | Why the file was not checked, in plain words (`the file has no PtO2 trace`); empty when it was |
| `'permeability'` | float or None | | µM/min/mmHg | Oxygen permeability of the chamber wall, from `ocr_settings`; None when the file does not store it |
| `'pressure_factor'` | float or None | | mmHg/µM | `PcO2` / `CcO2` fitted over the run (the oxygen solubility the instrument used); None when not checked |
| `'parts'` | dict | | | For `'sum'`, `'pressure'`, `'fall'`, `'fall_size'`, `'leak'` and `'leak_size'`: `'difference'`, `'margin'`, `'unit'` (µM/min, mmHg or %) and `'is_agreeing'` (difference at most the margin). Empty when not checked |

##### Our OCR check

The program uses the instrument's OCR (`VoO2`) as it is. The instrument does not say exactly how it smooths its rates, so each file is checked once, when its folder is read, against our own calculation from the same traces. A file that disagrees gets one warning that names the part. Below, Δt is the clock's step (s), Kp the permeability from `VoO2Math` and j a point of the clock.

Our recipe (`ocr_calculator`):
- fall[j] = -60 × Σ k × CcO2[j + k] / (Δt × Σ k²), for k = -14 … 14 (Σ k² = 2030): the slope of the least-squares straight line through the 29 points centred on j, in µM/min, positive when the oxygen falls; empty for the first and last 14 points
- leak[j] = Kp × mean of (PtO2 - PcO2)[j - 39 … j]: the 40 points (20 s at 0.5 s) ending at j; empty for the first 39 points
- our OCR = fall + leak

What is compared (`ocr_checker`), part by part:

| Part | Compared | Margin |
|---|---|---|
| `sum` | Largest difference between `VoO2` and `VrO2` + `DgO2` | 0.001 µM/min |
| `pressure` | Largest difference between `PcO2` and α × `CcO2`, α = Σ CcO2 × PcO2 / Σ CcO2² | 0.001 mmHg |
| `fall` | Median difference between `VrO2` and our fall | 3 µM/min |
| `fall_size` | (f - 1) × 100, without its sign, f = Σ VrO2 × fall / Σ fall² | 35 % |
| `leak` | Median difference between `DgO2` and our leak | 2 µM/min |
| `leak_size` | (f - 1) × 100, without its sign, f = Σ DgO2 × leak / Σ leak² | 5 % |

- The fall and leak parts use only the points where both have a value and that are more than 30 points (15 s) from every addition.
- The two smoothings differ most where the oxygen changes fast: after an addition (up to 240 µM/min), or when the outside oxygen jumps with a new oxygen setting (up to 46 µM/min for tens of seconds). So these parts look at the typical difference and at the overall size, not at every point. They catch a wrong permeability, a wrong unit or sign, and maths broken over most of a run.
- The margins are about three times the worst seen in the 33 sample files on 2026-11-20: 0.0001 for the sum and the pressure; 0.87 µM/min and 11 % for the fall; 0.55 µM/min and 1.6 % for the leak.
- To change the recipe, for example once the instrument's developer gives the exact smoothing: change `FALL_POINTS`, `LEAK_POINTS` or the helpers in `utils_shared/ocr_checking.py`, then this section. Then rewrite the fixed values in `tests/test_paf_reading.py` (`FIXED_*`), which hold our results on the example run so the maths never changes by accident. `tests/test_ocr_checking.py` holds the cases worked out by hand.

#### `ocr_settings`

How the instrument works out its oxygen rates, read from the `VoO2Math` record by `PafFile.ocr_settings_reader`. None when the file has no such record or it is not laid out as expected.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'permeability'` | float | | µM/min/mmHg | Oxygen permeability of the chamber wall (0.050 to 0.264 in the files seen) |
| `'fall_edge_points'` | int | | | Points without a `VrO2` value at each end of the recording (20); the three rates all lack this many at the end |
| `'leak_start_points'` | int | | | Points without a `DgO2` or `VoO2` value at the start (60) |

#### `averages`

Event-window statistics of one experiment. Created by `experiment_averages_calculator`, stored as `experiment['averages']`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'settings'` | dict | | | `window_minutes`, `gap_minutes`, `final_window_gap_minutes`, `vo2_source`, `vo2_key`, `haem_source`, `haem_key`, `baseline_minimum_seconds` |
| `'windows'` | dict | | | `{window name: window record}`; `average0` is the baseline window (it starts at the start of the recording when the recording starts later than the window would), then `average1` ... one per event |
| `'skipped'` | dict | | | `{window name: {start_time, end_time, reason}}` of the windows that do not fit between two additions (or after the last one), and of `average0` when its data span less than `baseline_minimum_seconds` (the run then has no baseline); they have no record in `'windows'` and are drawn red in the previews |

Window record:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'start_time'` | float | | min | Start of the window |
| `'end_time'` | float | | min | End of the window |
| `'vo2'` | dict | | | `{measurement: statistics}` for the OCR |
| `'haem'` | dict | | | `{haem name: statistics}` |

Statistics of one measurement in one window:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'mean'` | float | | as the source | Mean over the window |
| `'sd'` | float | | as the source | Sample standard deviation (n - 1) over the window |
| `'delta'` | float | | as the source | Mean minus the mean of `average0` (NaN when the run has no baseline) |
| `'change'` | float | | % | Mean as a percentage of the mean of `average0` (NaN for delta sources, a zero baseline or a run without a baseline) |

#### `triplicate`

One condition (strain and addition order, e.g. `knockdown_kcn_then_bd`) with its runs combined. Created by `triplicate_averager`, returned as `{condition: triplicate}`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'runs'` | dict | | | `{run number: experiment name}` |
| `'run_numbers'` | List[int] | (n_runs,) | | Run numbers in order |
| `'windows'` | List[str] | | | Window names in order |
| `'window_times'` | dict | | min | `{window name: (start, end)}` taken from the first run holding the window |
| `'settings'` | dict | | | Copy of the `settings` of the runs' `averages` |
| `'vo2'` | dict | | | `{measurement: {window name: run statistics}}` |
| `'haem'` | dict | | | `{haem name: {window name: run statistics}}` |

Run statistics of one measurement in one window. The `run_*` values are the per-run window values; the rest are calculated over the runs.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'run_means'` | dict | | as the source | `{run number: window mean}` |
| `'run_sds'` | dict | | as the source | `{run number: window SD}` |
| `'run_changes'` | dict | | % | `{run number: change from baseline}` |
| `'run_deltas'` | dict | | as the source | `{run number: delta from baseline}` |
| `'mean'`, `'sd'`, `'sem'`, `'n'` | float, float, float, int | | as the source | Mean, sample SD, SEM (SD / sqrt(n)) and count of the run means |
| `'change_mean'`, `'change_sd'`, `'change_sem'`, `'change_n'` | float, float, float, int | | % | The same for the run changes |
| `'delta_mean'`, `'delta_sd'`, `'delta_sem'`, `'delta_n'` | float, float, float, int | | as the source | The same for the run deltas |

#### `test_record`

One significance test drawn on the OCR and haem response figure. Appended to a list by the plotter and written to `ocr_and_haem_response.xlsx`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'panel'` | str | | | Panel name, e.g. `haem response bd then kcn` |
| `'measurement'` | str | | | OCR or haem name |
| `'metric'` | str | | | Compared statistic (`mean`, `change` or `delta`) |
| `'window'` | str | | | Window name |
| `'group_a'`, `'group_b'` | str | | | The two groups compared |
| `'values_a'`, `'values_b'` | dict | | as the metric | `{run number: value}` of each group (finite values only) |
| `'t'` | float | | | Student t statistic (equal variances) |
| `'p'` | float | | | Two-sided p value |
| `'p_adjusted'` | float | | | p value after the correction across the windows of the panel |
| `'correction'` | str | | | `holm` or `none` |
| `'alpha'` | float | | | Significance level |
| `'significant'` | bool | | | `p_adjusted < alpha` |
| `'mark'` | str | | | `*`, `**`, `***` or empty |

#### `difference_spectrum` and `difference_decomposition`

Added to each experiment of the time response figure by `utils_custom`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'group'` | str | | | Group word of the file name, e.g. `knockdown` |
| `'spectral_averages'` | dict | | | `{window name: {'time_range', 'wavelengths', 'attenuation'}}` |
| `'difference_spectrum'` | dict | | | `'wavelengths'` (n_wavelengths,), `'spectrum'` (n_wavelengths,), `'minuend'`, `'subtrahend'` (window names; the spectrum is minuend minus subtrahend) |
| `'difference_decomposition'` | dict | | | `'haem_names'` (n_haems), `'coefficients'` (n_haems), `'haem_percentages'` (n_haems, %), `'percent_basis'` (signed or absolute), `'filtered_data'`, `'scatter'`, `'no_scatter'`, `'haem_total'` (each n_wavelengths) and `'haem_individual'` (n_haems arrays of n_wavelengths) |

#### `fit`

A haem fit, as `fit_importer` reads a fit file, `preset_importer` joins the library files of a preset (`haem_files_combiner`, which `fit_loader` calls for a preset's name) and `fit_table_builder` builds the components found by the principal component analysis.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'haem_list'` | List[str] | (n_haems) | | Haem (or component) names. From `fit_importer` the a haems come first, then the b, then the c, then any other name, each type in alphabetical order (`helpers.haem_order_finder`: a605, b557, bH, bL, cc), whatever the order of the file, and `'data'` follows; from `fit_table_builder`, in the order of the components. Every list, figure and workbook keeps this order. `config.haem_colour_mapper` colours the haems by the type their name gives (`helpers.haem_type_finder`): a usual haem keeps its own colour (`HAEM_COLOURS`), any other takes a free shade of its type (`HAEM_TYPE_COLOURS`: green for a, blue for b, red for c). From a fit file with heading lines they are in figure form (`haem_name_typesetter`: `Cyt bH` becomes `Cyt $b_H$`); from an older file, as written |
| `'data'` | pd.DataFrame | (n_wavelengths, 2 x n_haems) | nm, OD/mM/cm ÷ 1 000 000 | (wavelength, response) column pairs, one pair per haem. The decomposition uses the response as the basis spectrum; it has the sign of the attenuation, -log10(T), oxidised minus reduced (each haem's α peak is a dip). Each haem's rows are at the top, with wavelengths going upwards and blanks (NaN) below a shorter haem. The responses are on the standard scale, OD/mM/cm divided by a million (the instrument's own scale, which `HAEM_FACTOR` multiplies back): the highest point of the shapes lies between 1e-7 and 1e-3 |
| `'scale_divisor'` | float | | | What the values of the file were divided by to reach the standard scale: set by the Unit line of a file with heading lines (1 000 000 for OD/mM/cm and relative, 1 000 for OD/µM/cm, 1 for OD/nM/cm); for an older file, 1, or 1 000 000 when it is a million above the standard |
| `'notes'` | List[str] | | | Sentences for the user: leftover rows left out of a haem, an older fit divided by a million, a fit far from the usual size of its unit or on neither scale |
| `'haem_files'` | List[str] | (n_haems) | | Only from a preset or `haem_files_combiner`: the library file name of each haem, in the order of `'haem_list'` |

#### `pca_analysis`

Returned by `component_finder` (`utils_shared/pca_fitter.py`): the principal component analysis of the spectra of all files inside a spectral window.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'wavelengths'` | np.ndarray | (n_wavelengths) | nm | The common grid inside the window |
| `'eigenvectors'` | np.ndarray | (n_wavelengths, n_components) | | Orthonormal principal components as columns, largest first |
| `'eigenvalues'` | np.ndarray | (n_components) | OD^2 | Variance of each principal component (sum of squares over all spectra) |
| `'gram'` | np.ndarray | (n_wavelengths, n_wavelengths) | OD^2 | Sum over files of X^T X, where X are the cleaned spectra |
| `'total_variance'` | float | | OD^2 | Trace of `'gram'` |
| `'n_values'` | int | | | Number of spectra x number of wavelengths |
| `'n_spectra'` | int | | | Number of spectra used |
| `'counts'` | dict | | | `{file name: number of spectra used}` |
| `'window'` | Tuple[float, float] | | nm | First and last wavelength used |
| `'degree_of_scatter'` | int | | | Scatter terms taken out of every spectrum first |

#### `pca_result`

Returned by `component_builder`: the chosen number of components, optionally rotated and in the convention of the fit files.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'wavelengths'` | np.ndarray | (n_wavelengths) | nm | As in `pca_analysis` |
| `'components'` | np.ndarray | (n_wavelengths, count) | | Components as columns, each with its largest peak equal to +1, ordered by the variance they explain |
| `'explained'` | np.ndarray | (count) | | Fraction of the total variance of each component |
| `'residual_rms'` | float | | OD | Root mean square of what the components leave unexplained |
| `'peaks'` | np.ndarray | (count) | nm | Wavelength of each component's largest peak |
| `'count'` | int | | | Number of components |
| `'rotated'` | bool | | | True when the varimax rotation was applied |
| `'smoothing_nm'` | float | | nm | Width of the Savitzky-Golay smoothing of the components; 0 when not smoothed. `'explained'` and `'residual_rms'` are those of the components before smoothing |

The haem type of each component (`'a'`, `'b'`, `'c'`, `'mixed'` or `'unknown'`) is worked out separately by `component_classifier`, from where its clear peaks and troughs are: the alpha and Soret bands of haem c (545-556.5 and 410-423 nm), b (556.5-570 and 423-437 nm) and a (595-612 and 437-450 nm). `config.pca_colour_mapper` turns the types into colours (`HAEM_TYPE_COLOURS`, the same shades as the haems of the fit files).

#### `pca_spectra_set`

One entry of the list `pca_spectra_gatherer` (`utils_viewer/viewer_preview.py`) returns, and `component_finder` and `decomposition_example_finder` read: the spectra of one file kept after trimming and ignoring.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'name'` | str | | | File name |
| `'wavelengths'` | np.ndarray | (n_wavelengths) | nm | Wavelengths, ascending (the window plus 2 nm either side) |
| `'spectra'` | np.ndarray | (n_spectra, n_wavelengths) | OD | Attenuation spectra |
| `'times'` | np.ndarray | (n_spectra) | min | Time of each spectrum (optional for the analysis) |

#### `pca_examples`

Returned by `decomposition_example_finder`: every spectrum decomposed with the components plus the offset and scatter terms, exactly as the haem decomposition does, and the two extremes.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'wavelengths'` | np.ndarray | (n_wavelengths) | nm | As in `pca_result` |
| `'best'`, `'worst'` | dict | | | The spectrum with the smallest and the largest residual RMS (keys below) |
| `'median_rms'` | float | | OD | Residual RMS of a typical spectrum |
| `'n_spectra'` | int | | | Number of spectra decomposed |

| Key of `'best'` and `'worst'` | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'name'` | str | | | File the spectrum is from |
| `'time_min'` | float | | min | Time of the spectrum; NaN when unknown |
| `'spectrum'` | np.ndarray | (n_wavelengths) | OD | The measured spectrum |
| `'contributions'` | np.ndarray | (n_wavelengths, count) | OD | Coefficient x component, one column per component |
| `'background'` | np.ndarray | (n_wavelengths) | OD | Offset and scatter part of the fit |
| `'fitted'` | np.ndarray | (n_wavelengths) | OD | Sum of the fit |
| `'residual'` | np.ndarray | (n_wavelengths) | OD | `'spectrum'` - `'fitted'` |
| `'rms'` | float | | OD | Root mean square of `'residual'` |

#### `last_answers`

Saved to `last_answers.json` in the user's own folder (`UserPlaces`): the data folder offered on the next run. The answers themselves are kept with each dataset (`dataset_settings`).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'data_folder'` | str | | | Full path of the folder of the `.paf` files used last |

#### `dataset_settings`

The settings last saved for a dataset. Returned by `dataset_settings_reader` (`utils_shared/dataset_settings.py`), written by `dataset_settings_saver` to `portimao_settings.json` in the data folder, and laid over `config.DEFAULT_ANSWERS` (the standard settings) when the dataset is opened again. Empty for a dataset never saved.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'export_folder'` | Optional[Path] | | | Results folder; `None` when none was kept or it was a full path on another computer. In the file it is text: relative to the data folder with forward slashes when inside it (`results`), otherwise the full path |
| `'answers'` | dict | | | Terminal answers |
| `'answers'['delta_psi']` | bool | | | Whether Δψ is worked out for the files with both regions (`utils_shared/delta_psi.py`) and drawn as the lowest panel of the plot of each; off unless switched on at question 4.5, which is asked only when a file has both regions and the fit has one bH and one bL |
| `'answers'['temperature_c']` | float | | °C | Temperature of the runs, for Δψ; asked once per dataset in the import (question 3.1.2), from 0 to 100, 37 unless changed |
| `'answers'['psi_bH_first_mV']`, `['psi_bL_first_mV']`, `['psi_bH_second_mV']`, `['psi_bL_second_mV']` | float | | mV | The midpoint potentials of the Δψ maths: of bH and of bL with the other haem oxidised (first) and reduced (second); +40, −20, −30 and −90 unless changed. `config.DELTA_PSI_MIDPOINT_ANSWERS` names them for the maths |
| `'answers'['psi_share']` | float | | | Share of the membrane potential between bH and bL; 0.5 unless changed |
| `'files'` | dict | | | `{file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end', 'OD', 'volume', 'dilution_factor', 'events', 'regions'}}`, built by `file_settings_merger`; a file or key may be missing (a dataset saved before the OD values and labels were kept has only the four limits) |
| `'files'[name]['trim_start']`, `['trim_end']`, `['ignore_start']`, `['ignore_end']` | Optional[float] | | min | Trim times are on the original recording (`None` for no trim), ignore times count from the new 0 after trimming |
| `'files'[name]['OD']`, `['volume']`, `['dilution_factor']` | float | | OD, mL, none | The OD values last entered (3.1.1); kept when a later run does not scale by OD, so they are offered again |
| `'files'[name]['events']` | List[dict] | (n_events,) | | `[{'datapoint': int, 'label': str ('ignore' for an event left out), 'concentration_uM': Optional[float] (µM), 'ignored': bool}]`, one per event of the file, in its order |
| `'files'[name]['regions']` | Dict[str, float] | | min | `{'oxidised_start', 'oxidised_end', 'reduced_start', 'reduced_end'}`: the oxidised and the reduced region of the file as times on the original recording, so a later change of the trim leaves them on the same data. A region not chosen has its two edges together; a file with neither chosen has no `'regions'` |

#### `strip_values`

What the settings strip under the plot shows (`SettingsStrip`, `utils_viewer/viewer_strip.py`). Built from the answers by `strip_values_builder`, given by `ViewerGui.strip_reader`, and taken in part or whole by `ViewerGui.strip_setter` (checked by `strip_values_checker`). Each change the user makes is told once, as a dict of the values it changed (a new journal can change the width and the height too), to the function registered with `ViewerGui.strip_listener_setter`. That function runs on the program thread while a question waits. `size_answers_builder` turns the journal, width and height back into answers, and `form_answers_builder` the spectrometer, the way of showing the haems and the per OD boxes. The names are those of the answers in `config.DEFAULT_ANSWERS`, except `spectra` and `ocr_per_od`. What the strip offers is given apart, with `ViewerGui.strip_choices_setter(spectra, has_percent, has_od)`: the spectrometers every file has (the drop-down shows only with more than one), whether at least one file has both regions (% oxidised is then in the list, `haem_form_choices_lister`), and whether OD values were entered (the per OD boxes then show).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'plot_haems'` | bool | | | Whether the haems are worked out and shown (the answers `decompose` and `plot_haems` together) |
| `'fit_file'` | str | | | File name of the fit: a preset, or a fit file of the fits folder itself (`fit_loader` looks for a preset first), normally one of the list given with `ViewerGui.strip_fits_setter` (`fit_names_lister`); the description of components found from the data and not saved; `'Your own haems'` (`spectral_decomposer.OWN_HAEMS_NAME`) for library haems ticked under Build a fit; `''` when none is named |
| `'haem_background'` | str | | | The background fitted under the haems, a key of `spectral_decomposer.BACKGROUND_SHORT_NAMES` (the words of the drop-down) |
| `'haem_files'` | List[str] | (n_haems,) | | The library files ticked under Build a fit: those of the fit in use (a preset's, or your own haems), none for a fit file of the user's own or components from the data. The library itself is given with `ViewerGui.strip_library_setter` (`library_haems_lister`: `[{'file', 'haem', 'type'}]`, in the order a, b, c). The answer of the same name keeps the haems ticked, used when `fit_file` is `'Your own haems'` and saved with the dataset's settings |
| `'compare'` | bool | | | Whether a decomposition is kept to compare with: the button reads *Stop comparing* when True. The user's click changes it; the program then keeps the decomposition in use (`kept_decomposition`) or drops the kept one |
| `'kept'` | str | | | The kept decomposition in words (the `'text'` of `kept_decomposition`), shown in a line of the strip; `''` when none is kept. Set by the program only |
| `'spectra'` | str | | | The spectrometer whose spectra hold the haems (the answer `decomposition_dataset`), e.g. `'Cyt'`; `''` when none is known |
| `'haem_mode'` | str | | | How the haems are shown: `'delta'` (ΔD), `'percent'` (% oxidised) or `'abs'` (absorbance), the keys of `viewer_strip.HAEM_FORM_TEXTS` (the words of the drop-down) |
| `'haem_per_od'` | bool | | | Whether the haems are scaled by OD (the answer of the same name); not used for % oxidised |
| `'ocr_per_od'` | bool | | | Whether the OCR is per OD: True for the answer `ocr_mode` `'od'`, False for `'raw'` and `'percent'`. A click gives `'od'` or `'raw'` |
| `'journal'` | str | | | `'none'` (the standard size, on the page of the standard journal) or a key of `config.JOURNAL_SPECS` |
| `'columns'` | float | | columns | Width, one of the widths the journal allows (`'widths_mm'`) |
| `'height'` | float | | fraction of a page | Height, above 0 and up to 1 |

#### `kept_decomposition`

The decomposition kept with *Keep to compare* in the strip, built by `kept_decomposition_builder` (`utils_viewer/viewer_strip.py`) and held in `ViewerSession.kept` until *Stop comparing* or the haems are left out. Each preview works the file out a second time with it and draws its haem traces dashed over the ones in use (`_kept_haems_drawer`); the distance between the two is from `decomposition_gap_calculator`. It is not saved with the dataset's settings.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'fit'` | dict | | | The `fit` it was worked out with |
| `'answers'` | dict | | | The answers that set it: `fit_file`, `haem_files`, `haem_background`, `decomposition_dataset`. Every other answer (trimming, OD, how the haems are shown) is the one in use, so only the decomposition differs |
| `'text'` | str | | | Its name in words, for example `bswitch_no2_mycobl_b557.csv with the Rowan scatter background` |

#### `od_rows`

The OD values of every file as the OD table of the window starts and ends them, in the order of the rows: the same layout as the OD values the questions give. Laid out as a table by `od_table_builder` and read back by `od_rows_reader` (`utils_viewer/viewer_table.py`).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| *file name* | dict | | | `{'OD', 'volume', 'dilution_factor'}` of that file |
| `'OD'` | Optional[float] | | OD | OD of the cells added; `None` for a cell that is empty or not a number above 0 |
| `'volume'` | Optional[float] | | mL | Volume of cells spun down; `None` as above |
| `'dilution_factor'` | Optional[float] | | | Dilution factor; `None` as above |

#### `table_rows`

A table to fill in on the terminal side of the window (`AnswerTable`, `utils_viewer/viewer_table.py`): the OD table (`od_table_builder`, one row per file) or the labels table (`label_table_builder`, one row per event under the name of its file). Taken by `ViewerGui.table_shower`. `ViewerGui.table_reader` gives back the values row by row (one `{name of the value: value}` per row: a float, a label, or `None` for a cell that is empty, wrong or greyed out) and the cells that cannot be used, as `('row name: column heading', problem)` with the problem `'empty'` or the kind of the cell.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'first_heading'` | str | | | Heading of the fixed first column: `'File'` or `'Time (min)'` |
| `'columns'` | Sequence[Tuple[str, str, str]] | (n_columns,) | | `(name of the value, column heading, kind)` for each column typed in; the kind is `'above_zero'` (a number above 0, needed), `'zero_or_more'` (a number of 0 or more, or nothing) or `'label'` (text, needed) |
| `'skip_word'` | Optional[str] | | | A label that leaves its row out (`'ignore'`): the row's other cells are greyed out and not read; `None` for none |
| `'rows'` | List[dict] | (n_rows,) | | One per row, in the order shown; the keys below |
| `'file'` | str | | | File the row belongs to; entering one of its cells shows that file on the plot |
| `'position'` | int | | | Place of the event in its file, from 0 (0 in the OD table) |
| `'group'` | Optional[str] | | | Heading the row sits under (the file name), shown above the first row of each group; `None` for none |
| `'first'` | str | | | Text of the fixed first column: the file name, or the time of the event in min with two decimals |
| `'name'` | str | | | How the row is named in the sentence after Confirm, such as `'run1 at 15.01 min'` |
| `'cells'` | Dict[str, str] | | | `{name of the value: text the cell starts with}`; `''` for an empty cell |

### 1.2 Dataclasses

#### `Spectra`

Defined in `utils_shared/paf_reader.py`. Created by `spectra_parser`, used by `record_scanner` and `PafFile`.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `offset` | int | | bytes | `0` | Position of the record in the file |
| `name` | str | | | `''` | Spectrometer name |
| `nframes` | int | | | `0` | Number of spectra |
| `npix` | int | | | `0` | Number of pixels (wavelengths) |
| `wl_off` | Optional[int] | | bytes | `None` | Position of the wavelength axis |
| `wavelengths` | Optional[np.ndarray] | (npix,) | nm | `None` | Wavelength of each pixel |
| `data_off` | int | | bytes | `0` | Position of the spectra block |
| `data_end` | int | | bytes | `0` | End of the spectra block |
| `log` | Optional[np.ndarray] | (nframes + 2, npix) | | `None` | Raw rows, as log10 of the counts: a row of zeros, the reference row, then one row per spectrum (see `.paf file`) |
| `rec_end` | int | | bytes | `0` | End of the record |
| `params` | dict | | | `{}` | Acquisition parameters found in the record |
| `checks` | dict | | | `{}` | Warnings raised while parsing |

#### `EdgeChoice`

Defined in `utils_viewer/viewer_edges.py`. Created by a step that lets the user choose parts of the plot by dragging edges (`trim_stage_runner`, for the trimmed and ignored parts; `_regions_chooser` in `utils_viewer/viewer_stages.py`, for the oxidised and reduced regions) and handed to the window with `ViewerGui.edges_shower`. The window's `EdgeOverlay` draws and drags the edges, the edges row of the strip (`EdgeRow`, `utils_viewer/viewer_strip.py`) shows and takes the values of the file shown, and `ViewerGui.edges_reader` gives back the values the user set. The three rules run on the window thread.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `fields` | List[Tuple[str, str]] | (n_fields,) | | | `(field, name shown before its box in the strip)`, in order; in the trimming step `trim_start` "Trim start", `trim_end` "end", `ignore_start` "Ignore first", `ignore_end` "last"; in the regions step `oxidised_start` "Oxidised from", `oxidised_end` "to", `reduced_start` "Reduced from", `reduced_end` "to" |
| `values` | Dict[str, Dict[str, float]] | | min | | `{file name: {field: value}}` the edges start at; in the trimming step the minutes taken off each edge (`trim_minutes_builder`): the trim end from the end of the recording, the ignore times from the trimmed edges; in the regions step the time of each edge on the time axis of the processing plot (`region_edges_builder`), a region not chosen having its two edges together (the step gives them back as times on the original recording) |
| `layout_finder` | Callable | | | | `(file name, its values) -> (edges, parts)`: edges as `[(field, time_min, words by its handle, kind)]`, shaded parts as `[(start_min, end_min, kind)]`, times on the time axis of the plot; kind is a key of `PART_STYLES` (`'trim'` grey and hatched, handles in the top row; `'ignore'` amber, handles in the row under it; `'oxidised'` red, top row; `'reduced'` blue, the row under it) |
| `pointer_reader` | Callable | | | | `(file name, its values, field, time_min pointed at) -> value` that puts that edge there |
| `value_setter` | Callable | | | | `(file name, its values, field, value) -> its new values`, kept within the file's own limits |
| `key_text` | str | | | `''` | Words under the plot explaining the colours |
| `previous` | Dict[str, Dict[str, float]] | | min | `{}` | Values drawn as red dashed lines: in the trimming step, the limits it had when it was opened again |
| `is_every_file` | bool | | | `True` | Whether "Every file" starts ticked: a moved or typed edge then moves on every file |
| `value_copier` | Optional[Callable] | | | `None` | `(file shown, other file, field, value on the file shown) -> value for the other file`, or None to leave that file as it is. With it, an edge set on every file is set on the file shown first and each other file gets the value this rule gives, within its own limits (the regions step: the same distance from the addition of the same number), and the drop-down no longer marks files with times of their own. None: every file gets the same value (the trimming step) |

#### `PreviewSpec`

Defined in `utils_viewer/viewer_preview.py`. Created by `preview_drawer`; every file is drawn with the same spec.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `answers` | dict | | | | Answers so far (missing keys come from `config.DEFAULT_ANSWERS`) |
| `limits` | dict | | min | | `{file name: {trim_start, trim_end, ignore_start, ignore_end}}` |
| `fit` | Optional[dict] | | | | Fit dictionary from `fit_importer`, or None |
| `details` | dict | | | | `{file name: {OD, volume, dilution_factor, events}}` |
| `show_trim` | bool | | | `False` | Draw the whole recording without shading, for the trimming step (the window draws the edges and the shading over it) |
| `show_ignored` | bool | | | `True` | Shade the ignored start and end (not with `show_trim`) |
| `kept` | Optional[dict] | | | `None` | The `kept_decomposition` drawn dashed over the haems, or None |
| `regions` | dict | | min | `{}` | The oxidised and reduced region of every file (`ViewerSession.regions`), which give a file with both its % oxidised |

#### `UserPlaces`

Defined in `utils_shared/user_places.py`. Created by `user_places_finder` when `main.py` is loaded (`PLACES`); the app's folders are made, and the program's fits copied in, by `user_folder_preparer`. Run from source (Windows, Linux, developers), every folder is the program folder. Run as the Mac app (`sys.frozen`), the program's own files are inside the app, which is never written to, and the user's things are in `Portimao` in the home folder.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `program_folder` | Path | | | | The program's own files (`fits/`, `assets/`, `QUESTION_FLOW.md`): the folder of `main.py`, or `sys._MEIPASS` inside the app |
| `own_folder` | Path | | | | The user's own folder; the data folders directly inside it are offered by number at question 1.1. The program folder, or `~/Portimao` in the app |
| `fits_folder` | Path | | | | `<own_folder>/fits`: the haem library (`haems/`), the presets (`presets/`), the user's own fit files, and where fits saved from the components go. In the app, each file of the program's fits folder that is missing (subfolders included) is copied in at every start; one already there is never overwritten |
| `last_answers_file` | Path | | | | `<own_folder>/last_answers.json` (`last_answers`) |
| `logs_folder` | Path | | | | `<own_folder>/logs`: the self-test log and, in the app, the launch log and the update log |
| `is_app` | bool | | | | True when running as the Mac app |

#### `TimeAxis`

Defined in `utils_viewer/viewer_preview.py`. Created by `time_axis_finder` from a drawn preview and passed to the window with its picture, so the mouse can point at a time. The fractions are measured from the bottom left corner of the picture.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `left` | float | | fraction of the width | | Left edge of the panels |
| `right` | float | | fraction of the width | | Right edge of the panels |
| `bottom` | float | | fraction of the height | | Bottom edge of the lowest panel |
| `top` | float | | fraction of the height | | Top edge of the highest panel |
| `start_min` | float | | min | | Time at the left edge |
| `end_min` | float | | min | | Time at the right edge |

#### `ViewerSession`

Defined in `utils_viewer/viewer_preview.py`. Created by `viewer_asker`, used by the stage runners, `preview_drawer`, the preview thread and the settings strip (`_strip_change_applier`).

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `summaries` | List[dict] | (n_files,) | | | The `experiment_summary` of each file |
| `export_root` | Path | | | | Results folder |
| `window` | ViewerGui | | | | The browser window |
| `current` | int | | | `0` | Index of the file being looked at |
| `cache` | OrderedDict | | | empty | `{file name: {'experiment': experiment}}` of the files nearest the one being looked at (`WINDOW_KEPT_FILES` in `config.py`, 3: that file and the one on each side); each preview works on a deep copy |
| `fit` | Optional[dict] | | | `None` | The `fit` the haems are worked out with: the standard or saved fit at first, then the one chosen in the processing or the strip; `None` when the haems are left out |
| `kept` | Optional[dict] | | | `None` | The `kept_decomposition` to compare with, set by *Keep to compare* in the strip; `None` when none is kept |
| `regions` | Dict[str, Dict[str, float]] | | min | `{}` | `{file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}}` as times on the original recording: those saved with the dataset at first, then those of the regions step (4.4). A region not chosen has its two edges together |
| `limits` | Dict[str, dict] | | | `{}` | The trim and ignore limits of every file as last answered (section 2), which say whether a file's regions still hold; empty before the trimming step |
| `has_od` | bool | | | `False` | True once OD values were entered in this run (3.1): the strip then shows its per OD boxes and the plots can be per OD |
| `redraw` | Optional[Callable[[], bool]] | | | `None` | Draws the plot of the step being asked again (set by each stage runner), for a change in the strip |
| `is_figure` | bool | | | `False` | True while the plot is the figure of each file at its saved size (section 5), so a new journal or size in the strip redraws it |
| `export_choice` | Optional[str] | | | `None` | What the export of the import (3.4) wrote: `'summary'`, `'trimmed'` or `'all'`; `None` before anything is exported. New edges export again with it |
| `export_limits` | Dict[str, dict] | | | empty | The trim and ignore limits of each file when it was last exported, to find the files whose edges changed |
| `full_exports` | Dict[str, List[Path]] | | | empty | `{file name: files written in its full/ folder}` in this run, so they are not written again when only the edges change, and are taken away when the file is no longer trimmed |
| `exported` | List[Path] | | | empty | The results folder, once the export has written into it; `viewer_asker` can share the caller's list, so the caller can say the export is kept when the questions are stopped |

### 1.3 Arrays

#### `spectra`

Attenuation (or transmission, or intensity) of one spectral dataset.

| Axis | Name | Length | Description |
|---|---|---|---|
| 0 | spectrum | `n_spectra` | One row per spectrum, in time order |
| 1 | wavelength | `n_wavelengths` | One column per wavelength |

- **dtype:** float64
- **Units of the values:** OD for attenuation, fraction for transmission, counts for intensity

### 1.4 Files

#### `.paf file`

A recording of the instrument software, read by `utils_shared/paf_reader.py`. The format is not published: this is the layout as the reader understands it, checked against the instrument software's own export of one recording (the wavelengths, counts, transmission and traces agree at every point).

| Property | Value |
|---|---|
| File type | Binary, little-endian |
| Text | UTF-16, each string after the four bytes `02 00 00 00` and its number of characters (unsigned 32-bit) |
| Location and name | `<data folder>/<experiment>.paf`; the file stem is the experiment name |

The file is one record after another. Each record starts with the byte `06`, the word `Espana`, five zero bytes and a 16-byte identifier, followed by its strings: the kind of record, the vendor and a name. The reader uses the first four kinds; the others were found in the four recordings looked at (one from each sample folder and the example run) and are not read:

| Kind of record | What it holds |
|---|---|
| `DataItem`, then `Measurement` | One trace (the clock `Time`, `CcO2`, `CsO2`, `VoO2` and others). The number of values is stored twice near the end of the `DataItem` (28 and 20 bytes before it); the `Measurement` ends with that many 32-bit floats and 8 closing bytes, and its strings give the quantity and the unit (the first unit named is the one used) |
| `Spectra: CCD` | One spectrometer: the number of spectra and of wavelengths, a table numbering the spectra 1, 2, 3 and so on, a block of settings, the wavelengths (32-bit floats, nm), the rows of spectra, then the date, grating and light source as strings |
| `Text Event` | One addition: its name (`Event 1`), the text typed, and its spectrum number (unsigned 32-bit, 20 bytes after the name) |
| `PaneNote` | The notes of the experiment, as rich text |
| `VoO2Math` | How the oxygen rates are worked out: the names of the traces used (`Time`, `CcO2`, `PcO2`, `PtO2`, `DgO2`, `VrO2`, `VoO2`), then, counting from the end of the last name, two empty strings, four zero bytes, the oxygen permeability (32-bit float at byte 20, µM/min/mmHg), a 32-bit float not known (byte 24), and the whole numbers 0, 20 and 60 (bytes 28, 32 and 36) |
| `SpectraFitting`, `FIT: NIR` | The haem fit used: its name, the spectrometer, the names of its shapes, the path of its `.fit` file on the instrument computer, the fit range and number of shapes (32-bit floats 520 and 630 nm, then 9, in the files seen) and the kind of spectra fitted (`ΔAttenuation`). Each shape follows as a `Plot: Scatter` with its wavelengths (nm) and its values (`Specific Absorption`, OD/mM/cm named first). Other fits that were open in the software are kept as further `FIT: NIR` records |
| `CellItem` | Cell culture data: four numbers (-1 when not filled in), three names (`Unknown` when not filled in) and a list of media. Not filled in, in the files seen |
| `ExptPart` | The time step of the recording (s) and two 32-bit floats not known (the first is the length of the recording in three of the four files) |
| `EspanaItem` | One of these is named after a date |
| `TriggerItem`, `StreamInteger`, `StreamList`, `StreamArray`, `ExptItem` | Not known |
| `ScrnList`, `ScrnItem`, `PaneList`, `PaneGraph`, `PanePage`, `PlotList`, `Plot: ...`, `AxisList`, `Axis`, `TickItem`, `FontItem`, `EspanaActive`, `FitList`, `Worksheet`, `ColStyle`, `RowStyle` | How the software shows the run (screens, graphs, axes, fonts); no data |

- **Clock:** the `Time` trace, in seconds from the start (0.5 s steps in the recordings seen). When a file holds it twice, the longer one is used.
- **Traces:** a trace is used when it has at least 90 % of the clock's length. A shorter trace is lined up with the clock from the start, so only its end is empty. A trace whose two stored lengths disagree, that holds no values or that does not fit in its record is not read; this is reported, with the reason, only for the traces the program uses.
- **Spectra rows:** (number of spectra + 2) rows of 32-bit floats, one value per wavelength: a row of zeros, log10 of the reference spectrum, then log10 of the counts of each spectrum. So counts = 10^row, rounded to a whole number, and transmission = 10^(row - reference row). Spectrum 1 belongs to the first time point of the clock, and so on.
- **Additions:** each addition is stored more than once; the first copy has the spectrum number 0 and the later ones the real number.
- **Not read:** files whose spectra are not numbered 1, 2, 3 without gaps, or that have more spectra than time points, are refused with a message.
- **Rate traces:** `VrO2` has no value for the first 20 and the last 20 points of the clock, `DgO2` and `VoO2` none for the first 60 and the last 20 (the 20 and 60 stored in `VoO2Math`), so these three are stored 20 values shorter than the clock. A rate trace short by just these 20 values is not reported as short.

What the file holds, each item marked **recorded** (taken as true), **calculated by the instrument** (can be checked) or **not known**. Checked on four recordings: the example run, against the software's own export, and one from each sample folder.

| What | Units | Kind | How we know | In every file seen |
|---|---|---|---|---|
| Clock (`Time`) | s | recorded | Agrees with the export | Yes; some files hold a second, shorter or unreadable copy |
| Counts of each spectrum, per spectrometer (`Cytochromes`, `NADH`) | counts | recorded | Agree with the export at every point | Yes |
| Reference spectrum (second stored row) | counts | recorded | Gives the export's transmission | Yes |
| First stored row | | not known | Always zeros | Yes |
| Wavelengths | nm | recorded | Agree with the export | Yes |
| Centre wavelength and slit of each spectrometer | nm, µm | recorded | Read from the settings block; the slit agrees with the notes | Yes |
| Other numbers of the settings block | | not known | One is 300 where the notes give a light source of 300 mA | Yes |
| Date, grating and light source of each spectrometer (strings after the spectra) | | recorded | For example `600g/mm@500nm`, `4000K-90 Luxeon-CZ` | Yes |
| Transmission and attenuation | fraction, OD | calculated (by this program; the software's export gives the same) | Agree with the export at every point | |
| Lifetimes of the two oxygen sensors (`Tau-cO2`, `Tau-tO2`) | µs | recorded | The sensors' own readings; `CcO2` and `PtO2` follow them | Yes |
| Measured oxygen (`CcO2`) | µM | calculated by the instrument from `Tau-cO2` | Follows 1 / `Tau-cO2` closely but not exactly: the sensor calibration is not stored in a form we can read, so it cannot be checked | Yes |
| Oxygen pressure in the chamber (`PcO2`) | mmHg | calculated by the instrument: `CcO2` × 0.744 to 0.748 (an oxygen solubility set per run) | Exact to the last stored digit; checked on every file read (`ocr_check`) | Yes |
| Oxygen pressure outside the chamber wall (`PtO2`) | mmHg | calculated by the instrument from `Tau-tO2` | Follows 1 / `Tau-tO2` loosely; cannot be checked, as for `CcO2` | Yes |
| `FtO2` | % | not known | An oxygen percentage that follows `PtO2` closely (about `PtO2` / 7.7) | Yes |
| Set oxygen (`CsO2`) | µM | recorded (set by the user) | A few steps | Yes |
| Oxygen permeability of the chamber wall (`KpO2`) | µM/min/mmHg | recorded (a setting of the run: 0.050 to 0.264 in the files seen) | Stored in `VoO2Math`; the `KpO2` trace itself holds no values | Yes |
| Second number of `VoO2Math` | | not known | 1.7 to 6.0 in the files seen | Yes |
| Fall of the measured oxygen (`VrO2`) | µM/min | calculated by the instrument: the fall of `CcO2` per minute, smoothed over the 41 points around each point | Checked on every file read (`ocr_check`). In the 33 sample files our straight line through 29 points is within 0.01 to 0.87 µM/min for half the points and the same size within 11 %, but up to 240 µM/min off just after an addition: the smoothing is not known exactly | Yes |
| Oxygen leaking in (`DgO2`) | µM/min | calculated by the instrument: the permeability × (`PtO2` - `PcO2`), smoothed | Checked on every file read. In the 33 sample files our 20 s mean is within 0.001 to 0.55 µM/min for half the points and the same size within 1.6 %, but up to 46 µM/min off for tens of seconds after the outside oxygen jumps: the smoothing is not known exactly | Yes |
| Oxygen consumption rate, OCR (`VoO2`) | µM/min | calculated by the instrument: `VrO2` + `DgO2` | Exact to the last stored digit (within 0.0001 µM/min in the 33 sample files); checked on every file read | Yes |
| Haem traces (`Cyt...`, named after the shapes of the fit) | µM | calculated by the instrument from the spectra with the fit stored in the file | Ours move the same way (`tests/test_haem_direction.py`); the amounts are not reproduced | Yes; their names and number change with the fit |
| The fit used (`SpectraFitting`, `FIT: NIR`) | OD/mM/cm | recorded | | Yes |
| `Expt Pt` | au | not known | Zero throughout | Yes |
| Additions (`Text Event`) | spectrum number | recorded (typed by the user) | Agree with the export | Only in files with additions (`wt_1.paf` has none) |
| Notes (`PaneNote`) | | recorded (typed by the user) | | Yes |
| Cell culture data (`CellItem`) | | recorded | Not filled in | Yes |
| A date (`EspanaItem`) | | not known | Probably the day of the recording | Yes |
| Time step (`ExptPart`) | s | recorded | Agrees with the clock | Yes |

#### `individual experiment workbook`

| Property | Value |
|---|---|
| File type | xlsx |
| Sheets | `CcO2`, `CsO2`, `VoO2` and, for the full export, `VoO2_OD`, `VoO2_percent`, `haem_abs`, `haem_delta_abs`, `haem_abs_OD`, `haem_delta_abs_OD`, `haem_percent` (% oxidised, for a file with both regions; no haem amounts: only cells are measured, and an amount depends on the size of its shape), `delta_psi` (Δψ and the potential at bH and at bL, when worked out); plus `Averages`, `Events` and `Metadata` when available |
| Location and name | `<results>/<experiment>/<experiment>.xlsx`: the trimmed data (all of it when the file is not trimmed), written by the export at the end of the import and again, with the run's results added, by the run; for a trimmed file the export of the import also writes `<results>/<experiment>/full/<experiment>.xlsx`, the whole recording |

The export of the import writes only `CcO2`, `CsO2`, `VoO2`, `Events` and `Metadata`. In the trimmed workbook the Metadata holds the edges (`trimmed_before_minutes`, `trimmed_after_minutes` when trimmed, `ignore_first_minutes`, `ignore_last_minutes`); the whole recording's holds none, so it does not change when they do.

| Column (data sheets) | Type | Units | Description |
|---|---|---|---|
| `Time (min)` | float | min | Time of the point |
| `spectrum_index` | int | | Spectrum number (haem sheets only) |
| measurement columns | float | see `experiment` | One per trace or haem |

The `Averages` sheet has one row per window: `Average`, `Start time (min)`, `End time (min)` and, per measurement, `<name> mean`, `<name> SD` and `<name> change from baseline (%)`.

#### `fit csv`

| Property | Value |
|---|---|
| File type | CSV |
| Delimiter | comma |
| Encoding | UTF-8 with the byte-order mark, so that Excel shows µ and α (line ends CRLF when written by the program); read with or without the mark |
| Location and name | `fits/haems/<haem>_<source>.csv`: the haem library, one haem per file, each with the values of its source fit unchanged (`c1_myco.csv`, `bL_037v.csv`; `c1_037v.csv` is drawn for the two haems of the cc, as the presets' haems per protein say); `fits/<name>.csv`: the user's own fits of one haem or several, and the components found by the principal component analysis, which the program saves here |

The file holds one haem or several, written by `fit_file_writer` and read by `fit_importer`. A library file holds one haem, and its `Made from` line names the fit and haem it was taken from (`_USER_REVIEW` keeps a table of all of them). It starts with heading lines, one `name,text` line each, down to the first empty line:

| Line | Read by the program | Description |
|---|---|---|
| `Portimao fit file,format 1` | Yes | Always first. A newer format than the program knows is refused |
| `Holds,<text>` | No | What the file holds, in words |
| `Unit,<unit>` | Yes, required | `OD/mM/cm`, `OD/µM/cm`, `OD/nM/cm`, or `relative` for components found from data (each scaled so its largest point is 1). Spaces, capitals, the Greek μ and `uM` are accepted |
| `Way up,<text>` | Yes, if there | Starts with `oxidised minus reduced` (as the decomposition uses the shapes: each haem's α peak is a dip) or `reduced minus oxidised` (turned over when read). Without this line the shapes are used as written |
| `Names,<text>` | No | How the names show in the figures |
| any other `<name>,<text>` | No | For people, for example `Made from` |

Then the table:

| Row or column | Type | Units | Description |
|---|---|---|---|
| First row | str | | The haem names, each over its wavelength column, the cell over its value column empty. Plain words: in the figures the haem letters (one to three of a, b, c, d, o) are in italics and a capital letter or number after them is written below the line (`haem_name_typesetter`); other words show as typed |
| Second row | str | | What each column holds: `Wavelength (nm)`, then the unit |
| Wavelength columns (every second, from the first) | float | nm | Wavelengths of one haem, going upwards |
| Value columns | float | the unit | The haem's shape at those wavelengths. Shorter haems end in empty cells |

Example (the top of `fits/haems/c1_myco.csv`, the cc of the standard fit):

```text
Portimao fit file,format 1
Holds,"The shape of one haem: how much 1 mM of the haem in a 1 cm light path changes the attenuation, -log10(T), at each wavelength between its oxidised and reduced states"
Unit,OD/mM/cm
Way up,"oxidised minus reduced: each haem's α peak is a dip, so the amount found rises as the haem is oxidised and falls as it is reduced"
Names,"In the figures the haem letters are in italics and a capital letter or number after them is written below the line (Cyt bH, Cyt a605)"
Made from,"Cyt cc of bswitch_no2_mycobl_b557.csv, the shape of the instrument's fit 20240913_Myco_b557_nolamda.fit (...)"

Cyt cc,
Wavelength (nm),OD/mM/cm
508.1799927,1.89
```

Rules, checked by `fit_importer`: the columns come in pairs and every wavelength column has a haem name; every cell is a number or empty; a row holds both a wavelength and a response, or neither; each haem has at least two rows. The haems may have different lengths, and empty rows are skipped wherever they are. Within a haem the wavelengths go upwards (a haem written wholly downwards is turned round); where they jump backwards, the rows from the jump on are left out and the user is told. The values are divided by the unit's number (1 000 000 for OD/mM/cm and relative, 1 000 for OD/µM/cm, 1 for OD/nM/cm) to reach the standard scale; a file whose shapes then fall outside 1e-7 to 1e-3 is used with a warning to check its Unit line. Each message names the row as the file has it.

**Older layout** (still read, for fit files made elsewhere): no heading lines, the first row is the haem names (the header over each value column is not used), the names are used as written (plotting codes such as `Cyt $b_H$` included), and the values have no stated unit. The same rules apply, and the scale is guessed: a file whose highest point is between 1e-7 and 1e-3 is used as it is, a file a million above that (0.1 to 1000) is divided by a million, and a file on neither scale is used as it is with a warning.

#### `preset csv`

| Property | Value |
|---|---|
| File type | CSV |
| Delimiter | comma |
| Encoding | UTF-8 with the byte-order mark; read with or without the mark, and with either line end |
| Location and name | `fits/presets/<name>.csv`. The six presets keep the names of the fit files they replaced, so a dataset saved with one of those names finds it; the standard fit is `bswitch_no2_mycobl_b557.csv` (`config.STANDARD_FIT`) |

A preset is a set of haems of the library, offered by its name in the fit question and the strip, before the user's own fit files. A fit file of the fits folder with a preset's name is not offered. Read by `preset_importer`:

| Line | Read by the program | Description |
|---|---|---|
| `Portimao preset,format 1` | Yes | Always first. A newer format than the program knows is refused |
| `Holds,<text>` | No | What the preset is, in words |
| (empty line) | Yes | Ends the heading lines |
| `Haem file,Haems per protein` | No | Names the columns |
| `<file>.csv,<number>`, one per line | The file name only | A file of `fits/haems/`, in any order: the haems are put in the order a, b, c. A missing file, a file of more than one haem, and two haems of the same name are refused, each with a message. The number, for the reader only, is how many haems the shape was drawn for in its source fit: 2 for `c1_037v.csv` (the two haems of the cc), 1 for every other. Only cells are measured, so a shape's size never changes the absorbance, ΔD or % |

Example (`fits/presets/temp_fit_037v.csv`):

```text
Portimao preset,format 1
Holds,"The haems of temp_fit_037v, the latest fit, each at the size that fit gives it"

Haem file,Haems per protein
c1_037v.csv,2
b557_037v.csv,1
bH_037v.csv,1
bL_037v.csv,1
a605_037v.csv,1
a3_037v.csv,1
```

#### `spectral csv`

| Property | Value |
|---|---|
| File type | CSV |
| Delimiter | comma |
| Encoding | UTF-8 |
| Location and name | `<results>/<experiment>/<dataset>_<type>.csv` (the trimmed spectra) and, for a trimmed file exported with the whole recordings' spectra, `<results>/<experiment>/full/<dataset>_<type>.csv`; type `transmiss`, `intensity` or `attenuation` |
| Size | About 19, 8 and 21 bytes per value for the three types (`SPECTRA_CSV_BYTES` in `config.py`), so about 1.2 GB for a 100 MB `.paf` file |

| Column | Type | Units | Description |
|---|---|---|---|
| `Wavelength (nm)` | float | nm | Wavelength |
| `<time> min` | float | see the type | One column per spectrum |

#### `ocr_and_haem_response.xlsx`

| Property | Value |
|---|---|
| File type | xlsx (live formulas with stored values) |
| Sheets | `Notes`, `Baseline OCR`, one sheet per condition, `Tests` |
| Location and name | `<results>/ocr_and_haem_response.xlsx` |

- **Notes:** how to read the workbook and the formulas used.
- **Baseline OCR:** the baseline OCR of every run (`Run`, `Experiment`, `Baseline OCR`), then `N`, `Mean`, `SD`, `SEM` per group and the baseline t-test.
- **One sheet per condition:** for each measurement, a table with one row per window and one column per run (the run means), then `N`, `Mean`, `SD`, `SEM`; the same for the change from baseline. The window times are not repeated per run.
- **Tests:** one row per test record: group A and B run values, means, variances, pooled variance, `t`, degrees of freedom, `p`, Holm rank, multiplier and adjusted `p`, `alpha` and the mark, so each result can be checked independently.

| Column (Tests) | Type | Units | Description |
|---|---|---|---|
| panel, measurement, metric, window | str | | Which comparison the row is |
| group A / B values, n, mean, variance | float | as the metric | Inputs of the test |
| `t`, `df`, `p` | float | | Student t-test, equal variances, two-sided |
| rank, multiplier, `p adjusted` | float | | Holm correction across the windows of the panel |
| `alpha`, `significant`, mark | | | Result |

#### `time_response.xlsx`

| Property | Value |
|---|---|
| File type | xlsx (live formulas with stored values) |
| Sheets | `Notes`, `Figure panels`, `Difference spectra`, `Haem percentages`, `Waterfall` (when a shared baseline is used) |
| Location and name | `<results>/time_response.xlsx` |

- **Figure panels:** `Panel`, `Group`, `Time point`, `Experiment` for every experiment drawn.
- **Difference spectra:** per experiment, the minuend and subtrahend window averages by wavelength and their difference.
- **Haem percentages:** per experiment, the fitted haem coefficients and the percentages calculated from them.
- **Waterfall:** the difference spectra with the shared baseline fit (`INTERCEPT` and `SLOPE` formulas) and the corrected spectra.

#### `last_answers.json`

| Property | Value |
|---|---|
| File type | JSON |
| Encoding | UTF-8 |
| Location and name | `last_answers.json` in the user's own folder (`UserPlaces`): next to `main.py` (not committed), or in `~/Portimao` in the Mac app |

Structure: see `last_answers` in section 1.1.

#### `portimao_settings.json`

| Property | Value |
|---|---|
| File type | JSON |
| Encoding | UTF-8 |
| Location and name | `portimao_settings.json` in the folder of the `.paf` files, so it travels with the dataset |

Structure: see `dataset_settings` in section 1.1.

#### `log file`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `<results>/logs/YYYY_MM_DD-HH_MM_SS.log` |

It starts as soon as the results folder is chosen, and is kept when Portimao is closed before the run. The first lines are the project version, the random seed (none: the program uses no random numbers), `Data folder: <path>` and `Results folder: <path>`. Then come the questions as the window's terminal shows them (without its colour codes), each answer on the line under its question, starting `> ` (indented as the question; an answer given with the mouse is logged as if typed). Once every question is answered, `Settings:` lists every answer of the run, one `  <name>: <value as JSON>` per line, then everything printed during the run follows. The window shows each problem as one sentence; its details (what was being done, then Python's own report of the error) go only here, under a line `---- Details of a problem, HH:MM:SS: <what was being done> ----`.

#### `self-test log`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `logs/self_test.log` in the user's own folder (`UserPlaces`): next to `main.py` (not committed), or in `~/Portimao` in the Mac app; overwritten by each check |

Written only with the check switch (the environment variable `PORTIMAO_SELF_TEST` set to any value), which opens the window, shows a made-up experiment as a preview and closes the window by itself. The same lines go to the terminal. In order:

- the program name and version, and the date and time;
- whether it runs from source or as the Mac app, and where the user's own folder is;
- the computer: Python, the system and its chip, Tk, and the versions of the main packages;
- each step of the check;
- any error, with its traceback;
- last, `Self-test passed.` or a line starting `Self-test failed`.

The line starting `The made-up preview is on show` tells the Mac check (`.github/workflows/mac_check.yml`) when to take its picture of the window.

#### `launch log`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `logs/launch.log`: next to `main.py` when the launcher starts the program (not committed), or in `~/Portimao` in the Mac app; kept from start to start |

Everything the program prints from its start, written by the launcher (`launchers/bootstrap.pyw`) or, in the Mac app, which has no launcher, by `app_output_logger`; both open it with `launch_log_opener` (`utils_shared/user_places.py`). Each start is added after the starts before, under a line `==== Portimao started YYYY-MM-DD HH:MM:SS ====` (a blank line before it). When the log is bigger than 1 MB (`LAUNCH_LOG_MAX_BYTES`) at a start, only its newest half is kept, from the first start line in that half. When the launcher itself stops, it adds the details there instead (a line `The launcher stopped, YYYY-MM-DD HH:MM:SS:`, then what Python, pip or the error said), while its message to the user stays one sentence. When the Mac app stops while starting, or its update stops, the app's start (`launchers/mac_app_starter.py`) adds a line saying which, with the date and time and the error's traceback. The details of a problem met before the run's own log starts (while the questions are asked), and what Tk said when the window could not open, go here too, laid out as in the `log file`.

Beside it, the program makes an empty file `logs/window_opened` once its window is up, at the place the launcher gives it in `PORTIMAO_OPENED_FILE`; the launcher then closes its small window and deletes the file. Started any other way, the program makes none.

When a git copy cannot update itself (git missing, no branch on GitHub followed, or git refusing the update because of files changed here), the launcher gives the program one sentence saying why and what to do in `PORTIMAO_UPDATE_NOTE`; the program shows it under the version line, with "(does not update itself)" after the version in the window title. A copy without `.git` (from a zip) says so itself (`update_note_finder`), however it was started.

#### `update log`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `logs/update.log` in `~/Portimao`, the Mac app's own folder; added to at each start, after cutting it to its last 200 lines |

Written only by the Mac app: at each start by its update (`update_installer`), and during a swap by `launchers/mac_app_swapper.sh`. One line per step, each starting with the date and time (`YYYY-MM-DD HH:MM:SS`):

- the app's version and where it is;
- what GitHub's newest release is; or, for each question with no answer, why (curl's reason, or GitHub refusing too many questions from the network), the second try a few seconds later, and, after a refusal, the Releases page asked instead;
- the zip this Mac needs, or why the app cannot update itself;
- why a download did not finish, when it did not;
- from the swap: `The new app is in place.`, or why the old app was kept.

The Mac report shows its last 30 lines.

#### `move log`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `logs/move_to_app.log` in the folder of an old launcher install on a Mac (usually `~/Portimao`, which becomes the Mac app's own folder); added to at each try, never cut |

Written by the launcher on a Mac (`launchers/mac_app_mover.py`), when it moves a git clone on main to the Mac app. One line per step, each starting with the date and time (`YYYY-MM-DD HH:MM:SS`):

- the folder being moved and the macOS version;
- each line `install_mac.sh` printed while it installed the app;
- why the app was not installed and the program started the old way, when it was not;
- how many old program files and folders were taken away, and any that could not be;
- when the folder is not `~/Portimao`, what was copied into it (fits and last answers);
- the Desktop link pointed at the app, and the app opening.

A move that stops in a way the mover did not foresee adds `The move stopped:` and the traceback. The Mac report of the app shows its last 30 lines.

#### Figure files

| Property | Value |
|---|---|
| File type | `.png` and `.svg` |
| Location and name | `<results>/<experiment>.*` per experiment, `<results>/2x2_comparison.*`, `<results>/ocr_and_haem_response.*`, `<results>/time_response.*` |

## 2. Conventions

Project-wide choices, written once. The tables above use these units and symbols.

### 2.1 Units

| Quantity | Unit | Name suffix |
|---|---|---|
| Time | min | `(min)` in column names, `_min` in keys |
| Wavelength | nm | none |
| Oxygen concentration | µM | none |
| Oxygen consumption rate | µM/min | none |
| Concentration of an addition | µM | `_uM` in keys; written by `concentration_formatter` as µM, mM or M, and `? µM` when none was given |
| Haem absorbance | mOD | none |
| Fractions of a range or baseline | % | none |

Terminal questions that ask for hours or minutes say which.

### 2.2 Dtypes

float64 for all arrays unless stated otherwise in the tables above. The wavelength axis is stored in the file as float32.

### 2.3 Axis order and shape symbols

| Data | Axis order |
|---|---|
| Time-resolved tables | One row per time point, `Time (min)` first |
| Spectral arrays | `(n_spectra, n_wavelengths)`: time first, then the spectral axis |

| Symbol | Meaning |
|---|---|
| `n_points` | Number of time points of a trace |
| `n_ocr_points` | Number of time points with an OCR value (fewer than `n_points`) |
| `n_spectra` | Number of spectra (frames) |
| `n_wavelengths` | Number of wavelengths (pixels) |
| `n_haems` | Number of haems in the fit |
| `n_runs` | Number of runs of a condition |
