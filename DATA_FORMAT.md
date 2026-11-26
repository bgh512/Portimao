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
| `'VoO2_baseline'` | pd.DataFrame | (n_points, 2) | % of baseline | Optional: only for a file with a baseline (`baseline_percent_adder`, after the averaging). `VoO2` divided by its average in the baseline (`average0`) x 100. `attrs['baseline_percent']` holds `'start_time'` and `'end_time'` of the baseline (min) and `'baseline_mean'` (`{column: the average in it}`, µM min⁻¹). The maths is in `MATHS.md` |
| `'haem_conc'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mM for a 1 cm light path | Optional. Fitted haem concentrations; columns `Time (min)`, `spectrum_index` and one per haem. The fit shapes times `HAEM_FACTOR` are in OD/mM/cm, so the amounts are mM x cm; with components found from data they are in arbitrary units. Fitted beside the background named by the answer `'haem_background'` (kept with the dataset's answers; the standard, in `config.DEFAULT_ANSWERS`, is `rowan_scatter`; the choices are `BACKGROUND_LABELS` in `spectral_decomposer.py`). When the change from the first spectrum is fitted, these are the changes from the first spectrum (the first kept, in a trimmed run) |
| `'haem_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. Haem concentration x peak of the fit spectrum; a change from the first spectrum when `haem_conc` is |
| `'haem_delta_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. ΔD, the change from the start: `haem_abs` shifted so that each haem is 0 where it starts, the median of its first 50 spectra with a value after the ignored start (`REFERENCE_WINDOW_POINTS` in `config.py`). `attrs['delta_abs_baseline']` holds what was subtracted: `'level_by_haem'` (mOD), `'window_by_haem'` (the first and last time, in min, of the spectra each start was taken from), `'window_points'` and `'window_seconds'`. The maths is in `MATHS.md` |
| `'haem_OD'`, `'haem_abs_OD'`, `'haem_delta_abs_OD'` | pd.DataFrame | (n_spectra, 2 + n_haems) | | Optional. The matching tables divided by dilution factor x OD x volume |
| `'haem_percent'` | pd.DataFrame | (n_spectra, 2 + n_haems) | % | Optional: only for a file with both an oxidised and a reduced region. % oxidised: `haem_abs` put between each haem's reduced level (0 %) and its oxidised level (100 %) by `percent_oxidised_calculator`; values above 100 and below 0 are kept, and a haem whose two levels are equal has an empty column. `attrs['percent_oxidised']` holds the levels used. The maths is in `MATHS.md` |
| `'haem_levels'` | dict | | mOD, min | Optional: only for a file with both regions (`haem_levels_finder`). `'oxidised'` and `'reduced'`: `{haem: its level}`, the median of `haem_abs` in that region (mOD); `'oxidised_region'` and `'reduced_region'`: `(start, end)` of the region on the time of the trimmed data (min), kept within the used part of the run |
| `'delta_psi'` | pd.DataFrame | (n_spectra, 5) | mV | Optional: only when the answer `'delta_psi'` is on, for a file with `haem_percent` whose fit has one bH and one bL. Columns `Time (min)`, `spectrum_index`, `Δψ (mV)` (the membrane potential), `Eh bH (mV)` and `Eh bL (mV)` (the redox potential at each haem), built by `delta_psi_table_builder`; empty (NaN) in a spectrum where bH or bL is less than 10 % or more than 90 % reduced (the two limits of the answers, `config.DELTA_PSI_LIMIT_ANSWERS`, unless changed). `attrs['delta_psi']` holds the numbers used: `'midpoints_mV'`, `'share'`, `'temperature_c'`, `'limits_percent'`, `'bH'` and `'bL'` (the two columns of `haem_percent`) and `'spectra_with_value'`. The maths is in `MATHS.md` |
| `'raw_spectra'` | dict | | | `{dataset: {'wavelengths', 'spectrum_indices', 'time', 'transmission', 'intensity', 'attenuation'}}`; every spectrum has a time, and the transmission is NaN where it cannot be worked out (zero counts in the reference); dropped after the special figures are prepared |
| `'averages'` | dict | | | Statistics of the averaging regions (see `averages`) |

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
| `'haem_background'` | str or None | | | Background fitted under the haems, by its short name (`BACKGROUND_SHORT_NAMES`, `Rowan scatter`); None when the haems were not decomposed |
| `'processed'` | str | | | Date and time of the run, `YYYY-MM-DD HH:MM` |

#### `event`

One addition (a text event of the instrument software). Created by `experiment_paf_loader`, one per addition stored inside the recording; an addition stored outside it is left out, with a warning when the files are first read.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'datapoint'` | int | | | Spectrum number stored with the addition, counted from 1 |
| `'text'` | str | | | What was typed in the instrument software, e.g. `1ul 8mm nd-011992`. The file holds no concentration |
| `'label'` | str | | | Name shown in the figures: the text, until the user renames it |
| `'stock_uM'` | float or None | | µM | Concentration of the stock added, typed by the user with its unit; None when none was given |
| `'added_uL'` | float or None | | µL | Volume of the stock added; None when none was given (a stock and a volume are given together or not at all) |
| `'addition_uM'` | float or None | | µM | How much the addition raised the concentration in the chamber: stock × added ÷ chamber (`config.CHAMBER_VOLUME_ML`), or a typed concentration minus the one before it of the same label (`event_concentration_filler`, MATHS.md section 8); None when unknown |
| `'concentration_uM'` | float or None | | µM | Concentration in the chamber after the addition: worked out from the stock and the volume, the same label in a file adding up, or typed by the user; None when none was given |
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

Statistics of the averaging regions of one experiment. Created by `experiment_averages_calculator`, stored as `experiment['averages']`. The user sees "averaging region" everywhere; the code and every stored name keep the older word "window" (`windows`, `window_minutes`, `each_window` ...), so the settings of a dataset saved before still read back unchanged.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'settings'` | dict | | | `window_minutes`, `gap_minutes`, `final_window_gap_minutes`, `vo2_source`, `vo2_key`, `haem_source`, `haem_key`, `haem_view_keys` (`{view: key of the haem table it was averaged from}`, for example `{'abs': 'haem_abs_OD'}`; it gives the unit of each view), `baseline_minimum_seconds`, `quick_minutes` (None without quick regions), `delay_minutes`, `is_settled` (False without settled regions), `each_window` (the regions of this file set on their own, as in `dataset_settings`; empty for none) |
| `'windows'` | dict | | | `{region name: region record}`; `average0` is the baseline (it starts at the start of the recording when the recording starts later than the region would), then the settled regions `average1` ... one per event (ending before the next addition), then the quick regions `quick1` ... one per event (starting after their own addition) |
| `'skipped'` | dict | | | `{region name: {start_time, end_time, reason, kind, left_out}}` of the regions that do not fit between two additions (or after the last one), of `average0` when its data span less than `baseline_minimum_seconds` (the run then has no baseline), and of the regions the user left out with their tick (`left_out` True, the reason `averaging.LEFT_OUT_PROBLEM`; `left_out` is missing for `average0`); they have no record in `'windows'`. Those that do not fit are drawn red in the previews; those left out are not drawn, are not warned of, and keep their row in the Averages sheet with empty numbers |

A figure that uses one kind of averaging region reads the averages through `window_kind_picker` (`utils_shared/averaging.py`): the baseline and the regions of that kind only, the quick regions under the names of the settled ones (`quick2` as `average2`). The averages of the haem and OCR response and the 2x2 grid, and the `triplicate` built from them, are in this form.

Region record:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'start_time'` | float | | min | Start of the region |
| `'end_time'` | float | | min | End of the region |
| `'kind'` | str | | | `'baseline'`, `'settled'` or `'quick'` (`WINDOW_KINDS`) |
| `'vo2'` | dict | | | `{measurement: statistics}` for the OCR |
| `'haem'` | dict | | | `{haem name: statistics}` of the haems as the plot shows them (the figures read this one) |
| `'haem_views'` | dict | | | `{view: {haem name: statistics}}` for every way the haems can be shown that the experiment has: `'delta'` (ΔD), `'abs'` (absorbance) and `'percent'` (% oxidised), the keys of `config.HAEM_SOURCE_BY_MODE`, per OD when the plot is (`Config.haem_view_lister`). Their `'change'` is always NaN. Empty when no views were asked for |
| `'delta_psi'` | dict | | | Only for an experiment with `'delta_psi'`: the statistics of Δψ (mV) over the spectra of the region that have a value (`'change'` always NaN), with `'spectra_used'` (int, the spectra with a value) and `'spectra_in_window'` (int, all the spectra of the region) |

Statistics of one measurement in one averaging region:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'mean'` | float | | as the source | Mean over the region |
| `'sd'` | float | | as the source | Sample standard deviation (n - 1) over the region |
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

#### `region_difference` and `region_difference_decomposition`

The difference spectrum of one file, reduced region minus oxidised region, shown in the window with the switch *Difference spectrum* under the boxes (`utils_shared/difference_spectra.py`, MATHS.md section 9). `region_difference` is built by `difference_spectrum_builder` from the processed experiment, only for a file with `'haem_levels'`; `region_difference_decomposition` by `difference_decomposer`, drawn by `difference_figure_drawer`. Neither is exported; both are kept in the slim copy of the file (`page_experiment`, as `'difference'` and `'difference_parts'`) for the Difference spectrum and the Waterfall of a dataset figure.

`region_difference`:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'dataset'` | str | | | The spectrometer whose attenuation spectra were used (the answer `decomposition_dataset`) |
| `'wavelengths_nm'` | np.ndarray | (n_wavelengths,) | nm | The wavelengths of those spectra |
| `'difference_mOD'` | np.ndarray | (n_wavelengths,) | mOD | Mean attenuation of the spectra inside the reduced region minus that inside the oxidised region, edges counted |
| `'oxidised_region'`, `'reduced_region'` | Tuple[float, float] | | min | `(start, end)` of each region, as in `'haem_levels'` (time of the trimmed data) |
| `'n_oxidised'`, `'n_reduced'` | int | | | Number of spectra averaged in each region |

`region_difference_decomposition` (every spectrum on the wavelengths every haem shape of the fit covers):

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'wavelengths_nm'` | np.ndarray | (n_fit_wavelengths,) | nm | The wavelengths used |
| `'measured_mOD'` | np.ndarray | (n_fit_wavelengths,) | mOD | The difference on those wavelengths |
| `'haems_mOD'` | Dict[str, np.ndarray] | n_haems x (n_fit_wavelengths,) | mOD | `{haem: its part, amount x shape}`, in the order of the fit's `'haem_list'` |
| `'background_mOD'` | np.ndarray | (n_fit_wavelengths,) | mOD | The background fitted under the haems (the answer `haem_background`) |
| `'fit_mOD'` | np.ndarray | (n_fit_wavelengths,) | mOD | The haems plus the background |
| `'residual_mOD'` | np.ndarray | (n_fit_wavelengths,) | mOD | Measured minus the fit |
| `'amounts'` | Dict[str, float] | | mM for a 1 cm light path | `{haem: its amount}`; negative for a haem more reduced in the reduced region, as the shapes are oxidised minus reduced |

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

Returned by `component_finder` (`utils_shared/pca_fitter.py`): the principal component analysis of the spectra of all files inside a spectral range.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'wavelengths'` | np.ndarray | (n_wavelengths) | nm | The common grid inside the spectral range |
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
| `'wavelengths'` | np.ndarray | (n_wavelengths) | nm | Wavelengths, ascending (the spectral range plus 2 nm either side) |
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
| `'setup'` | dict | | | The dataset set-up table as saved (`saved_setup`); empty for a dataset never set up, and not written in the file then |
| `'answers'['delta_psi']` | bool | | | Whether Δψ is worked out for the files with both regions (`utils_shared/delta_psi.py`) and drawn as a panel of the plot of each (the lowest in the standard order); off unless switched on at question 4.5, which is asked only when a file has both regions and the fit has one bH and one bL |
| `'answers'['panel_order']` | List[str] | (n_panels,) | | The panels of the plot of each file in the order the user moved them to, top first, by their keys: `oxygen`, `vo2`, `delta_psi`, and `haem:` then the name of the haem (`haem:Cyt bH`). Empty for the standard order (oxygen, OCR, the haems a then b then c, Δψ). A panel the order does not know is drawn just above the panel that follows it in the standard order, or at the bottom (`panel_order_placer`); a move made on one file keeps the places of the panels that file does not have (`panel_order_merger`, both in `utils_shared/helpers.py`) |
| `'answers'['temperature_c']` | float | | °C | Temperature of the runs, for Δψ; asked once per dataset in the import (question 3.1), from 0 to 100, 37 unless changed |
| `'answers'['psi_bH_first_mV']`, `['psi_bL_first_mV']`, `['psi_bH_second_mV']`, `['psi_bL_second_mV']` | float | | mV | The midpoint potentials of the Δψ maths: of bH and of bL with the other haem oxidised (first) and reduced (second); +40, −20, −30 and −90 unless changed. `config.DELTA_PSI_MIDPOINT_ANSWERS` names them for the maths |
| `'answers'['psi_share']` | float | | | Share of the membrane potential between bH and bL; 0.5 unless changed |
| `'answers'['psi_reduced_lowest_percent']`, `['psi_reduced_highest_percent']` | float | | % | The limits of Δψ: it is given only where bH and bL are both between these % reduced; 10 and 90 unless changed. `config.DELTA_PSI_LIMIT_ANSWERS` names them for the maths. All the numbers of Δψ are typed in the Δψ row of the strip (`strip_values`) |
| `'files'` | dict | | | `{file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end', 'OD', 'volume', 'dilution_factor', 'events', 'regions'}}`, built by `file_settings_merger`; a file or key may be missing (a dataset saved before the OD values and labels were kept has only the four limits) |
| `'files'[name]['trim_start']`, `['trim_end']`, `['ignore_start']`, `['ignore_end']` | Optional[float] | | min | Trim times are on the original recording (`None` for no trim), ignore times count from the new 0 after trimming |
| `'files'[name]['OD']`, `['volume']`, `['dilution_factor']` | float | | OD, mL, none | The OD values last entered (3.2.1); kept when a later run does not scale by OD, so they are offered again |
| `'files'[name]['events']` | List[dict] | (n_events,) | | `event_entries` of the file, one per event, in its order; the four numbers are missing in a dataset saved before the stock and the volume were asked |
| `'answers'['each_window']` | Dict[str, dict] | | min | The averaging regions set on their own, the same in every file: `{region name: {'length_min', 'gap_min', 'is_used'}}` for the baseline `average0` and a settled region `averageN`, `{region name: {'length_min', 'delay_min', 'is_used'}}` for a quick region `quickN` (`averaging.EACH_WINDOW_FIELDS`). A key not given takes the shared value (`window_minutes`, `gap_minutes`, `quick_minutes`, `delay_minutes`); `is_used` False leaves the region out (never the baseline); the last settled region of a file uses `final_gap_minutes` in place of its own gap (MATHS.md 7.5). Empty unless regions were set on their own |
| `'answers'['file_windows']` | Dict[str, dict] | | min | `{file name: {'window_minutes', 'gap_minutes', 'final_gap_minutes', 'quick_minutes', 'delay_minutes', 'each_window'}}` of the files whose averaging regions were fixed by hand with "Apply to all" unticked; they stand in for the dataset's values for that file, and a key missing takes the dataset's (`window_plan_finder`). Empty unless a file was fixed by hand |
| `'answers'['compare_layout']` | str | | | How a decomposition kept to compare with is shown: `'side'` (a plot of its own headed Old on the left of the plot in use, headed New; the standard) or `'overlaid'` (faint and thin under the plot in use, drawn bold) |
| `'answers'['difference_spectra']` | bool | | | Whether the plot of a file with both regions shows its difference spectrum (`region_difference`) in place of the standard plot, the switch under the boxes; False (the standard plot) unless changed |
| `'answers'['label_mode']` | str | | | What the event labels show (Labels as in the strip), a key of `event_concentrations.LABEL_MODES`: `'chamber'` (the concentration in the chamber, `400 µM KCN`, the standard) or `'added'` (the volume and the stock added, `10 µL of 200 mM KCN`) |
| `'files'[name]['regions']` | Dict[str, float] | | min | `{'oxidised_start', 'oxidised_end', 'reduced_start', 'reduced_end'}`: the oxidised and the reduced region of the file as times on the original recording, so a later change of the trim leaves them on the same data. A region not chosen has its two edges together; a file with neither chosen has no `'regions'` |

#### `strip_values`

What the five boxes above the plot show (`SettingsStrip`, `utils_viewer/viewer_strip.py`; called the strip in the code). Built from the answers by `strip_values_builder`, given by `ViewerGui.strip_reader`, and taken in part or whole by `ViewerGui.strip_setter` (checked by `strip_values_checker`). Each change the user makes is told once, as a dict of the values it changed (a new journal can change the width and the height too), to the function registered with `ViewerGui.strip_listener_setter`. That function runs on the program thread while a question waits. A new order of the panels is told the same way though the strip keeps no value for it: as `{'panel_order': [keys]}` (`viewer_strip.PANEL_ORDER_CHANGE`), the keys of the panels of the file shown, top first, after a click on an arrow beside a panel (the window tells it), or an empty list after a click on *Standard order*. Clicks that change no value are told the same way: `{'export_master': True}`, `{'edit_ods': True}` and `{'edit_labels': True}` (`MASTER_CHANGE`, `EDIT_ODS_CHANGE`, `EDIT_LABELS_CHANGE`), `{'save_fit': name}` with the name typed beside *Save fit* under Build a fit (`SAVE_FIT_CHANGE`; the program saves the haems ticked as a fit file of that name with `built_fit_saver` and names it as the fit in use), `{'do_pca': True}` from *Do PCA* (`PCA_CHANGE`; while the haem step waits, `ViewerSession.pca_runner` asks the questions of the analysis), and `{'export_full': True}` or `{'export_trimmed': True}` from the Export full + trimmed csv or Export trimmed csv button of the trim step opened again in the guide (`viewer_guide.EXPORT_FULL_CHANGE`, `viewer_guide.EXPORT_TRIMMED_CHANGE`). `size_answers_builder` turns the journal, width and height back into answers, and `form_answers_builder` the spectrometer, the ways of showing the haems and the OCR, the per OD box, what the event labels show and their angle. The names are those of the answers in `config.DEFAULT_ANSWERS`, except `spectra`, `time_tab` and the numbers of the Δψ box, which `psi_answers_builder` turns into answers (`psi_values_builder` the other way). What the boxes offer is given apart, with `ViewerGui.strip_choices_setter(spectra, has_percent, has_od, has_baseline, has_psi, region_files)`: the spectrometers every file has (the drop-down shows only with more than one), whether at least one file has both regions (% oxidised is then in the list, `haem_form_choices_lister`), whether OD values were entered (the per OD boxes of the OCR and the haems then show; Edit ODs is always there), whether the averaging regions are set up (% of baseline is then in the "OCR as" list, `ocr_form_choices_lister`), whether Δψ can be worked out (its tick can then be clicked), and the names of the files with both regions (the switch under the boxes can then show their difference spectrum).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'plot_haems'` | bool | | | Whether the haems are worked out and shown (the answers `decompose` and `plot_haems` together) |
| `'fit_file'` | str | | | File name of the fit: a preset, or a fit file of the fits folder itself (`fit_loader` looks for a preset first), normally one of the list given with `ViewerGui.strip_fits_setter` as `{file name: name shown}` (`fit_titles_lister`: a preset's Name line, else the file name without .csv; the drop-down shows the names and keeps the file name); `temp_fit_037v.csv` saved before it was renamed is read as `rowan_fit_11_2026.csv` (`dataset_settings.RENAMED_ANSWERS`); the description of components found from the data and not saved; `'Your own haems'` (`spectral_decomposer.OWN_HAEMS_NAME`) for library haems ticked under Build a fit; `''` when none is named |
| `'haem_background'` | str | | | The background fitted under the haems (the Scatter drop-down), a key of `spectral_decomposer.BACKGROUND_SHORT_NAMES` (the words of the drop-down; `BACKGROUND_FORMULAS` holds each formula, shown under the ⓘ button). `'valencia'` saved before it was renamed is read as `'palencia'` (`dataset_settings.RENAMED_ANSWERS`) |
| `'haem_files'` | List[str] | (n_haems,) | | The library files ticked under Build a fit: those of the fit in use (a preset's, or your own haems), none for a fit file of the user's own or components from the data. The library itself is given with `ViewerGui.strip_library_setter` (`library_haems_lister`: `[{'file', 'haem', 'type'}]`, in the order a, b, c). The answer of the same name keeps the haems ticked, used when `fit_file` is `'Your own haems'` and saved with the dataset's settings |
| `'compare'` | bool | | | Whether a decomposition is kept to compare with: *Keep to compare* is greyed when True, and *Keep old* and *Keep new* show under it. A click on *Keep to compare* sets it, and one on *Keep new* clears it; the program then keeps the decomposition in use (`kept_decomposition`) or drops the kept one. A click on *Keep old* changes no value: it is told as `{'go_back': True}` (`viewer_strip.BACK_CHANGE`), and the program then sets the strip to the kept values |
| `'kept'` | str | | | The kept decomposition in words (the `'text'` of `kept_decomposition`), shown in a line of the strip; `''` when none is kept. Set by the program only |
| `'compare_layout'` | str | | | How the kept decomposition is shown, the switch beside *Keep new* (shown while one is kept), a key of `viewer_strip.COMPARE_LAYOUT_TEXTS`: `'side'` (Side by side, the standard) or `'overlaid'` (Overlaid). The answer of the same name, saved with the dataset's settings |
| `'difference_spectra'` | bool | | | The switch *Standard plot / Difference spectrum* under the boxes (`viewer_strip.DIFFERENCE_TEXTS`; the window packs `SettingsStrip.switch_frame` under them). It can be clicked only while the haems are shown and the file shown (`SettingsStrip.shown_file_setter`, from the window's file arrows) is one of the files with both regions given to `strip_choices_setter`. The answer of the same name, saved with the dataset's settings |
| `'spectra'` | str | | | The spectrometer whose spectra hold the haems (the answer `decomposition_dataset`), e.g. `'Cyt'`; `''` when none is known |
| `'haem_mode'` | str | | | How the haems are shown: `'delta'` (ΔD), `'percent'` (% oxidised) or `'abs'` (absorbance), the keys of `viewer_strip.HAEM_FORM_TEXTS` (the words of the drop-down) |
| `'haem_per_od'` | bool | | | Whether the haems are scaled by OD (the answer of the same name); not used for % oxidised |
| `'ocr_mode'` | str | | | How the OCR is shown, a key of `OCR_FORM_TEXTS`: `'raw'` (µM min⁻¹), `'od'` (per OD: µM min⁻¹ in the "OCR as" drop-down with its per OD box ticked, offered only with OD values), `'percent'` (% of the range) or `'baseline'` (% of baseline, offered only once the averaging regions are set up). `ocr_view_reader` gives the drop-down and the box for it, `ocr_mode_builder` the way back |
| `'label_mode'` | str | | | What the event labels show, a key of `LABEL_FORM_TEXTS` (the "Labels as" drop-down): `'chamber'` (In the chamber) or `'added'` (What was added) |
| `'event_label_angle'` | float | | ° | The angle of the event labels (the "Label angle" box of the View box), from 0 to 90 |
| `'time_tab'` | str | | | The tab of the Time regions box pressed: `'trim'`, `'regions'`, `'windows'` (the keys of `viewer_strip.TIME_TAB_TEXTS`), or `''` for none. A click is told as `{'time_tab': tab}`; the program sets it back with `strip_setter` once the edges are on the plot (`strip_values_builder` leaves it out) |
| `'delta_psi'` | bool | | | Whether Δψ is worked out: the tick of the Δψ box, whose numbers show while it is ticked (the haems are worked out and the answer `delta_psi` is on). The user's click changes it, as question 4.5 does |
| `'psi_bH_mV'`, `'psi_bL_mV'` | float | | mV | The midpoint potential of bH and of bL with the other haem oxidised (the answers `psi_bH_first_mV` and `psi_bL_first_mV`); any number |
| `'psi_fall_mV'` | float | | mV | The "shift" box: how far each midpoint falls when the other haem is reduced: `psi_bH_first_mV` − `psi_bH_second_mV`. The row fills in the two midpoints with the other haem reduced from it (`psi_seconds_filler`), and `psi_answers_builder` turns a change of any of the three into all four midpoint answers |
| `'psi_share'` | float | | | The answer `psi_share`; above 0 |
| `'temperature_c'` | float | | °C | The answer `temperature_c`, the same value as question 3.1; from 0 to 100 |
| `'psi_lowest_percent'`, `'psi_highest_percent'` | float | | % | The answers `psi_reduced_lowest_percent` and `psi_reduced_highest_percent`; above 0 and below 100, the lowest first. A number typed is checked by `psi_number_checker` before it is told |
| `'journal'` | str | | | `'none'` (the standard size, on the page of the standard journal) or a key of `config.JOURNAL_SPECS` |
| `'columns'` | float | | columns | Width, one of the widths the journal allows (`'widths_mm'`) |
| `'height'` | float | | fraction of a page | Height, above 0 and up to 1 |

#### `kept_decomposition`

The decomposition kept with *Keep to compare* in the strip, built by `kept_decomposition_builder` (`utils_viewer/viewer_strip.py`) and held in `ViewerSession.kept` until one of the two is chosen or the haems are left out: *Keep new* drops it and carries on with what is on the plot, *Keep old* puts its fit, answers and regions back in use (`_kept_restorer`, `utils_viewer/viewer_stages.py`) and then drops it. Each preview works the file out a second time with it (`_kept_processor`). Side by side (the answer `compare_layout` `'side'`), it is drawn as a plot of its own, the same size, with the same y range as the plot in use on matching panels (`_kept_side_drawer`); the preview figure carries it as its attribute `kept_figure`, and `preview_picture_maker` puts it on the left of the picture under the heading Old, the plot in use on the right under New, with the time axis that of the plot in use. Overlaid, its haem traces are drawn faint and thin under the ones in use, which are drawn bold (`_kept_haems_drawer`), and its Δψ the same way (`_kept_psi_drawer`). Either way the haem panels keep one scale (`haem_ylim_sharer`). The distance between the two is from `decomposition_gap_calculator`. It is not saved with the dataset's settings.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'fit'` | dict | | | The `fit` it was worked out with |
| `'answers'` | dict | | | The answers that set it: `fit_file`, `haem_files`, `haem_background`, `decomposition_dataset`, and the numbers of Δψ (`psi_bH_first_mV`, `psi_bL_first_mV`, `psi_bH_second_mV`, `psi_bL_second_mV`, `psi_share`, `temperature_c`, `psi_reduced_lowest_percent`, `psi_reduced_highest_percent`). Every other answer (trimming, OD, how the haems are shown, whether Δψ is worked out) is the one in use |
| `'regions'` | dict | | min | A copy of `ViewerSession.regions` as it was when kept: `{file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}}` as times on the original recording; a file missing had no regions, so it has no kept % oxidised or Δψ |
| `'text'` | str | | | Its name in words, for example `bswitch_no2_mycobl_b557.csv with the Rowan scatter background, its regions and Δψ numbers` (`and its regions` when Δψ is not worked out; neither when there are no regions) |

#### `od_rows`

The OD values of every file as the OD table of the window starts and ends them, in the order of the rows: the same layout as the OD values the questions give. Laid out as a table by `od_table_builder` and read back by `od_rows_reader` (`utils_viewer/viewer_table.py`).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| *file name* | dict | | | `{'OD', 'volume', 'dilution_factor'}` of that file |
| `'OD'` | Optional[float] | | OD | OD of the cells added; `None` for a cell that is empty or not a number above 0 |
| `'volume'` | Optional[float] | | mL | Volume of cells spun down; `None` as above |
| `'dilution_factor'` | Optional[float] | | | Dilution factor; `None` as above |

#### `event_entries`

The events of every file as the labels table (question 3.3) starts and ends them: `{file name: [entry, ...]}`, one entry per event of the file, in its order. Built by `event_entries_builder` (`utils_shared/survey.py`) from the dataset's settings or the file's own text, laid out by `label_table_builder` and read back by `label_entries_reader` (`utils_viewer/viewer_table.py`); `event_asker` then works out the concentrations (`event_concentration_filler`, `utils_shared/event_concentrations.py`). Kept in the dataset's settings (`'files'[name]['events']`) and copied onto each `event`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'datapoint'` | int | | | Spectrum number of the event, which ties it to its `event` |
| `'label'` | str | | | The label; `'ignore'` for an event left out |
| `'stock_uM'`, `'added_uL'` | Optional[float] | | µM, µL | The stock and the volume added, as on `event`; None for an event left out |
| `'addition_uM'`, `'concentration_uM'` | Optional[float] | | µM | What the addition adds, and the concentration in the chamber after it, as on `event` |
| `'ignored'` | bool | | | True for an event left out |

#### `dataset_setup`

The dataset set-up table: which experiment is which. Built by `setup_builder` (`utils_shared/dataset_setup.py`) from the file names (`file_name_reader`, `utils_custom/run_namer.py`) laid under what was saved, filled in in the window (`SetupTable`, `utils_viewer/viewer_setup.py`; `ViewerGui.setup_shower` and `setup_hider`) and returned by `setup_stage_runner` (`utils_viewer/viewer_stages.py`).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'group_names'` | List[str] | (2,) | | The names the user gave the two group columns (`'strain'`, `'order of additions'`); `''` for a column left unnamed |
| `'colours'` | Dict[str, str] | | | `{Group 1 label: colour as '#rrggbb'}`, one per label of the table, in the order first seen (`group_colours_filler`: a label keeps its colour, a new one takes the first of `config.GROUP_COLOURS` no label has) |
| `'rows'` | List[dict] | (n_files,) | | One per experiment, in the order of the files; the keys below |
| `'name'` | str | | | Experiment name (the `.paf` file name without the extension) |
| `'use'` | bool | | | Whether the experiment is in the dataset figures |
| `'group_1'`, `'group_2'`, `'time_point'` | str | | | Its labels; `''` for a blank cell. A time point read from a file name is `'<hours> h'` |
| `'run'` | Optional[int] | | | Run number read from the file name (`run<N>`, or a lone number at its end); `None` for none. It orders the replicates and is not saved |

The replicate number of each row is not kept: `replicates_numberer` works it out (the rows in use with the same three labels count 1, 2, 3 by run number, then by place in the table; `None` for a row not in use). `sets_lister` gives the sets as `{'name', 'n', 'colour'}`.

#### `saved_setup`

The set-up as it is kept in the settings file of the dataset, under `'setup'` (`dataset_settings`). Written by `setup_plainer` and read by `saved_setup_reader` (`utils_shared/dataset_setup.py`), which keeps only the parts of the right form. Empty for a dataset never set up.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'group_names'` | List[str] | (2,) | | As in `dataset_setup` |
| `'colours'` | Dict[str, str] | | | As in `dataset_setup`, for the labels in the table when it was saved |
| `'files'` | dict | | | `{file name: {'use': bool, 'group_1': str, 'group_2': str, 'time_point': str}}`; a file saved before and not in a later run is kept. A file in the folder that is not here is filled in from its name |

#### `table_rows`

A table to fill in on the terminal side of the window (`AnswerTable`, `utils_viewer/viewer_table.py`): the OD table (`od_table_builder`, one row per file) or the labels table (`label_table_builder`, one row per event under the name of its file). Taken by `ViewerGui.table_shower`. `ViewerGui.table_reader` gives back the values row by row (one `{name of the value: value}` per row: a float, a concentration in µM, a label, or `None` for a cell that is empty, wrong or greyed out) and the cells that cannot be used, as `('row name: column heading', problem)` with the problem `'empty'`, `'pair'` or the kind of the cell.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'kind'` | str | | | `'od'` or `'labels'`: a table left for another step opens again as it was left, by its kind (`table_texts_filler`) |
| `'first_heading'` | str | | | Heading of the fixed first column: `'File'` or `'Time (min)'` |
| `'shown_columns'` | Sequence[Tuple[str, str]] | (n_shown,) | | Optional. `(name, heading)` of each column shown after the first and not typed in, in grey italics: the labels table's `('text', 'Text in the file')` |
| `'columns'` | Sequence[Tuple[str, str, str]] | (n_columns,) | | `(name of the value, column heading, kind)` for each column typed in; the kind is `'above_zero'` (a number above 0, needed), `'above_zero_or_empty'` (a number above 0, or nothing), `'zero_or_more'` (a number of 0 or more, or nothing), `'label'` (text, needed), `'stock'` (a concentration above 0, written and read in mM unless a unit is typed, or nothing) or `'chamber'` (a concentration of 0 or more, written and read in µM unless a unit is typed, or nothing); the labels table's columns are the volume added (µL), the stock (mM), the chemical (the label) and the concentration in the chamber (µM) |
| `'pairs'` | Sequence[Tuple[str, str]] | (n_pairs,) | | Optional. Names of two values filled in together or not at all (the stock and the volume added); the empty one of a pair filled in by half is a problem `'pair'` |
| `'worked'` | Optional[dict] | | | Optional. `{'key': name of the value, 'writer': function(rows, values) -> [text or None per row]}`: the cell the table fills in itself as the others are typed (the concentration in the chamber, `label_worked_writer`), in green and not typed in; a row given None is typed in as usual |
| `'skip_word'` | Optional[str] | | | A label that leaves its row out (`'IGNORE'`, typed in any capitals): the row's other cells are greyed out and not read; `None` for none |
| `'rows'` | List[dict] | (n_rows,) | | One per row, in the order shown; the keys below |
| `'file'` | str | | | File the row belongs to; entering one of its cells shows that file on the plot |
| `'position'` | int | | | Place of the event in its file, from 0 (0 in the OD table) |
| `'group'` | Optional[str] | | | Heading the row sits under (the file name), shown above the first row of each group; `None` for none |
| `'first'` | str | | | Text of the fixed first column: the file name, or the time of the event in min with two decimals |
| `'name'` | str | | | How the row is named in the sentence after Confirm, such as `'run1 at 15.01 min'` |
| `'shown'` | Dict[str, str] | | | Optional. `{name: text}` of the columns shown and not typed in |
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

Defined in `utils_viewer/viewer_edges.py`. Created by a step that lets the user choose parts of the plot by dragging edges (`trim_stage_runner`, for the trimmed and ignored parts; `_regions_chooser` in `utils_viewer/viewer_stages.py`, for the oxidised and reduced regions; `_windows_chooser` in the same file, for the averaging regions) and handed to the window with `ViewerGui.edges_shower`. The window's `EdgeOverlay` draws and drags the edges, the edges row of the strip (`EdgeRow`, `utils_viewer/viewer_strip.py`) shows and takes the values of the file shown, and `ViewerGui.edges_reader` gives back the values the user set. The three rules run on the window thread.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `fields` | List[Tuple[str, str]] | (n_fields,) | | | `(field, name shown before its box in the strip)`, in order; a name starting with a capital starts a line of its own in the box, each line ending with the unit; in the trimming step `trim_start` "Trim before", `trim_end` "after", `ignore_start` "Ignore before", `ignore_end` "after" (shown as times on the whole recording, `shown_maker`); in the regions step `oxidised_start` "Oxidised from", `oxidised_end` "to", `reduced_start` "Reduced from", `reduced_end` "to"; in the averaging step `window_s` "Region length (s)", `gap_s` "Time before next addition (s)" (names holding the unit end their line without it) |
| `values` | Dict[str, Dict[str, float]] | | min | | `{file name: {field: value}}` the edges start at; in the trimming step the minutes taken off each edge (`trim_minutes_builder`): the trim end from the end of the recording, the ignore times from the trimmed edges; in the regions step the time of each edge on the time axis of the processing plot (`region_edges_builder`), a region not chosen having its two edges together (the step gives them back as times on the original recording); in the averaging step `window_s`, `gap_s` (seconds) and `is_on` (1 or 0) of the settled regions and `quick_s`, `delay_s` (seconds) and `quick_is_on` (1 or 0) of the quick regions (`WINDOW_KEYS`, `utils_shared/averaging.py`), then `final_gap_s` (how long before the end of the recording the last settled region ends, seconds), `each_is_on` ("Adjust region manually", 1 or 0) and `settled_picked`, `quick_picked` (the number of the region of each kind picked with it on, the baseline 0, -1 for none; ticking it picks region 1) (`STEP_EXTRA_KEYS`), and each region's own values as `'<window>:<field>'` in seconds (`'average2:window_s'`, `'quick1:delay_s'`) and its tick as `'<window>:is_used'` (1 or 0); a key missing takes the shared value. Made from the answers of each file by `window_values_maker` and read back by `window_plan_reader` |
| `layout_finder` | Callable | | | | `(file name, its values) -> (edges, parts)`: edges as `[(field, time_min, words by its handle, kind)]`, shaded parts as `[(start_min, end_min, kind)]`, times on the time axis of the plot; kind is a key of `PART_STYLES` (`'trim'` orange and hatched, handles in the top row; `'ignore'` grey, handles in the row under it; `'oxidised'` red, top row; `'reduced'` blue, the row under it; `'baseline'` gold, top row, for the baseline region and its start; `'baseline_end'` gold, the row under it, for its end; `'average'` blue, top row, for a settled averaging region and its start; `'average_end'` blue, the row under it, for its end; `'quick'` green, top row, for a quick averaging region and its start; `'quick_end'` green, the row under it, for its end; `'average_unfit'` red and hatched, for a region of either kind that does not fit; `'left_out'` pale grey, for a region left out with its tick, which has no edges; `'not_picked'` grey, for a region other than the one picked while "Adjust region manually" is on, which has no edges). In the averaging step the field of an edge names its region, `'<field>@<window>'` (`'gap_s@average1'`), and the end of the last settled region is the edge `'final_gap_s'` |
| `pointer_reader` | Callable | | | | `(file name, its values, field, time_min pointed at) -> value` that puts that edge there |
| `value_setter` | Callable | | | | `(file name, its values, field, value) -> its new values`, kept within the file's own limits |
| `key_text` | str | | | `''` | Words under the plot explaining the colours |
| `previous` | Dict[str, Dict[str, float]] | | min | `{}` | Values drawn as red dashed lines: in the trimming step, the limits it had when it was opened again |
| `is_every_file` | bool | | | `False` | Whether "Apply to all" starts ticked: a moved or typed edge then moves on every file. Ticking it copies the edges of the file shown to every file once; it unticks itself when another file is shown |
| `value_copier` | Optional[Callable] | | | `None` | `(file shown, other file, field, value on the file shown) -> value for the other file`, or None to leave that file as it is. With it, an edge set on every file is set on the file shown first and each other file gets the value this rule gives, within its own limits (the regions step: the same distance from the addition of the same number), and the drop-down no longer marks files with times of their own. None: every file gets the same value (the trimming step) |
| `unit` | str | | | `'min'` | The unit written after the boxes of the strip, `'min'` or `'s'`; the values of the fields are in it (the averaging step: `'s'`) |
| `switch` | Optional[Tuple[str, str]] | | | `None` | `(field, words)` of a tick box shown in place of "Apply to all": ticking it sets that field to 1 on every file, unticking it to 0. The field has no box, so it is not in `fields`. In the averaging step `('is_on', 'Averaging regions')`, on the top line of the box with "Apply to all" on a line of its own under the rows: unticked, the file has no averaging regions and the rest of the box is greyed. None: the tick box is "Apply to all" |
| `second_fields` | List[Tuple[str, str]] | (n_fields,) | | empty | The fields of a second row of the strip, under the first, as `fields`. Shown only with `second_switch`; the averaging step has none while the quick regions are hidden |
| `second_switch` | Optional[Tuple[str, str]] | | | `None` | `(field, words)` of the tick box of the second row, as `switch`. None: the step has one row (the averaging step, while the quick regions are hidden) |
| `shown_maker` | Optional[Callable] | | | `None` | `(file name, values) -> {field: value shown}`: the values as the boxes show them; in the trimming step the times on the whole recording (`survey.trim_times_finder`); in the averaging step, with "Adjust region manually" on, those of the region picked, the last region showing its time before the end of the file (`averaging.window_shown_maker`). None: the boxes show the values as kept |
| `typed_reader` | Optional[Callable] | | | `None` | `(file name, values, field, number typed) -> value`: a number typed in a box turned back into the field's value; in the trimming step a time on the whole recording read as a drag to it (`survey.trim_pointer_reader`). None: the number typed is the value |
| `options` | List[Tuple[str, str]] | (n_options,) | | empty | `(field, words)` of toggles on a line of their own between the numbered ticks and the boxes; a toggle sets its field on every file. In the averaging step `('each_is_on', 'Adjust region manually')`, which greys "Apply to all" while it is on. Empty: no such line |
| `row_teller` | Optional[Callable] | | | `None` | `(file name, values) -> [(note, [(field, words, is_ticked)])]`, one for each row: the note beside the numbered ticks above its boxes and the ticks; a tick clicked sets its field to 1 or 0 as a typed value would. In the averaging step `averaging.window_row_teller`: a tick per region to leave it out ("Use: 1 2 3"), no note. None: no ticks |
| `unmarked_fields` | Tuple[str, ...] | | | `()` | Fields that never make the drop-down mark a file as having values of its own (the averaging step: `settled_picked`, `quick_picked`) |
| `pick_lister` | Optional[Callable] | | | `None` | `(file name, values) -> ([(field, value, words, is_picked)], note)`: buttons beside the toggles, a click setting the field to the value on the file shown, the one picked in bold, and a note after them. In the averaging step `averaging.window_pick_lister`: Baseline 1 2 ... while "Adjust region manually" is on, setting `settled_picked`. None: no buttons |

#### `FigurePage`

Defined in `utils_shared/figure_page.py`. The page of a dataset figure; each change (`plot_placer`, `plot_lifter`, `plot_remover`) gives a new page. Drawn off screen by `figure_page_drawer` from the set-up (`dataset_setup`), the slim copy of each experiment (`page_experiment`) and the answers of the run: each plot by the drawer of its plot type (`PLOT_DRAWERS`, filled by `utils_shared/page_plots.py`), the plots of one plot type then put on the same scales where it asks for that (`SCALE_SHARERS`), and each plot fitted into its cells with its text and its own small legend (`axes_room_fitter`, `plot_legend_placer`, `utils_shared/figure_layout.py`); a plot type without a drawer is a grey stand-in, and a Space for a drawing (P17) is empty. Saved by `template_saver` and read by `template_reader`.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `journal` | str | | | `'nature'` | The journal the page is drawn for (a key of `config.JOURNAL_SPECS`) |
| `columns` | float | | columns | `2` | The width, as a key of the journal's `'widths_mm'` |
| `height` | float | | fraction of the tallest figure | `0.8` | The height, above 0 and at most 1 |
| `plots` | Tuple[PagePlot, ...] | (n_plots,) | | `()` | The plots in the order they were placed; their letters come from where they sit (`panel_letters_finder`): a, b, c… by each plot's top left cell, left to right then down |

#### `PagePlot`

Defined in `utils_shared/figure_page.py`. One plot of a `FigurePage`, a rectangle of cells of the 6 × 6 grid that no other plot takes; row 0 and column 0 are the top left cell.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `plot_type` | str | | | | The plot type, `'P1'` to `'P20'` (`PLOT_TYPES`); there is no `'P16'` (the Legend, taken out: a plot of it is refused) |
| `row` | int | | grid cells | | The top row it takes, 0 to 5 |
| `column` | int | | grid cells | | The left column it takes, 0 to 5 |
| `n_rows` | int | | grid cells | `1` | How many rows it takes |
| `n_columns` | int | | grid cells | `1` | How many columns it takes |
| `roles` | Dict[str, str] | | | `{}` | What the plot shows, as roles (below), never a file of the dataset |

The roles are what the form of the plot holds (`form_roles_reader`, `utils_shared/page_data.py`), one per `form_field`:

| Role | Value | Description |
|---|---|---|
| `'experiment'` | `'Group 1: 1, Group 2: 0, time point: 2, replicate: 1'` | One experiment, by the place of each of its labels among the labels of its column in the set-up (1 for the first label, 0 for a blank cell; rows in use only) and its replicate number (`experiment_role_maker`; `role_experiment_finder` gives the experiment of a dataset that fits, or None) |
| `'group_1'`, `'group_2'`, `'time_point'` | `'Split'`, `'Only label 2'` or `'All together'` | A group drop-down: each label its own set, only the experiments of the label in that place, or the column left out. One not in the roles is `'Split'` for Group 1 and `'All together'` for the others (`plot_sets_lister`) |
| the key of a tick | `'yes'` or `'no'` | A tick of the form |

The roles of a Standard experiment (P1), beside `'experiment'` (`standard_form_maker`, `utils_shared/page_plots.py`); one that is not in the roles is as the plot starts:

| Role | Value | Description |
|---|---|---|
| `'panel_oxygen'`, `'panel_vo2'`, `'panel_delta_psi'` | `'yes'` or `'no'` | Whether the oxygen, the OCR and the Δψ panel are drawn; starts `'yes'`. Δψ is asked only in a run that works it out |
| `'panel_haem_<name>'` | `'yes'` or `'no'` | Whether the panel of a haem is drawn, one for each haem the run plots; the name in lower-case letters and digits only (`'panel_haem_cytbh'` for `Cyt $b_H$`); starts `'yes'` |
| `'haem_view'` | `'delta'`, `'abs'` or `'percent'` | The haems as ΔD, absorbance or % oxidised (a key of `config.HAEM_SOURCE_BY_MODE`; per OD as in the run); starts `'delta'`. Asked only in a run that plots haems |
| `'addition_labels'` | `'yes'` or `'no'` | The label of each addition above the top panel; starts `'yes'` |
| `'regions_shaded'` | `'yes'` or `'no'` | The averaging regions shaded behind the panels; starts `'no'` |
| `'same_scales'` | `'yes'` or `'no'` | The same scales as the other Standard experiments of the page whose tick is on (`standard_scales_sharer`); starts `'yes'` |

The roles of a Difference spectrum (P2), beside `'experiment'` (`difference_form_maker`):

| Role | Value | Description |
|---|---|---|
| `'haem_components'`, `'overall_fit'`, `'residual'` | `'yes'` or `'no'` | Whether the part of each haem, the fit and the residual (a small panel underneath) are drawn; each starts `'yes'` |
| `'background'`, `'haem_bands'` | `'yes'` or `'no'` | Whether the background and the haem bands are drawn; each starts `'no'` |

The roles of a Waterfall (P3) (`waterfall_form_maker`); the first two are read as group drop-downs (`plot_sets_lister`), Group 2 always All together:

| Role | Value | Description |
|---|---|---|
| `'group_1'` | `'Only label 1'`, ... | The group whose experiments are stacked; starts at the first label. Not asked for a set-up without Group 1 labels (every experiment in use) |
| `'time_point'` | `'Split'` or `'All together'` | One line per time point, the mean of its replicates, or one line per experiment; starts `'Split'`. Asked only for a set-up with time points; without, one line per experiment |
| `'align_haem'` | str | The haem whose band the spectra are lined up on, its name in lower-case letters and digits (`'cytbh'`); starts at the first b haem. Asked only in a run that works out haems |
| `'haem_bands'` | `'yes'` or `'no'` | Whether the haem bands are drawn; starts `'yes'`. Asked only in a run that works out haems |
| `'trace'` | `'difference'`, or a trace as below | What is stacked: the difference spectrum (starts there), or one trace over time, read with `'vo2_value'`, `'haem_view'`, `'delta_psi_value'` and `'time_zero'` as in a Mean trace (`waterfall_traces_lister`, drawn by `_waterfall_traces_drawer`) |
| `'addition_labels'` | `'yes'` or `'no'` | The label of each addition above a waterfall of traces; starts `'yes'` |

The roles of the plots over time, a Single trace (P7, with `'experiment'`; `trace_form_maker`) and a Mean trace (P8, with the group drop-downs; `mean_form_maker`); one that is not in the roles, or that this run does not have, is as the plot starts (`_trace_roles_reader`):

| Role | Value | Description |
|---|---|---|
| `'trace'` | `'oxygen'`, `'vo2'`, `'haem_<name>'` or `'delta_psi'` | The trace: the measured oxygen, the OCR, a haem of the fit (its name in lower-case letters and digits, `'haem_cytbh'`) or Δψ (only in a run that works it out); starts `'vo2'` |
| `'vo2_value'` | `'baseline'`, `'raw'`, `'change'` or `'od'` | The OCR as % of baseline, as measured, as its change from baseline or per OD (offered only in a run with OD values); starts `'baseline'`. Used when the trace is the OCR |
| `'haem_view'` | `'delta'`, `'abs'` or `'percent'` | A haem as ΔD, absorbance or % oxidised, per OD as in the run; starts `'delta'`. Used when the trace is a haem |
| `'delta_psi_value'` | `'raw'` or `'change'` | Δψ in mV or as its change from baseline; starts `'raw'`. Used when the trace is Δψ |
| `'time_zero'` | `'start'` or `'addition 1'` … `'addition 10'` | Where time 0 is: the start of the recording, or an addition (the last one of a file with fewer); starts `'addition 1'`. A Mean trace lined up on an addition uses every addition as its measuring stick (MATHS.md section 10.2) |
| `'addition_labels'` | `'yes'` or `'no'` | The label of each addition above the plot; starts `'yes'` |
| `'regions_shaded'` | `'yes'` or `'no'` | P7 only: the averaging regions shaded behind the trace; starts `'no'` |
| `'band'` | `'sem'`, `'sd'` or `'none'` | P8 only: the band round each mean; starts `'sem'` |

The lines of a Mean trace, from `mean_lines_lister` (`utils_shared/page_plots.py`): a dictionary with `'times_min'` (np.ndarray, (n_times,), the shared times, one a second), `'additions_min'` and `'breaks_min'` (the shared times of the additions and of the breaks), `'left_out'` (the experiments left out), `'label'` (the title of the y axis), `'events'` (the additions of the first experiment kept, for their labels), `'zero'` (which addition is time 0, from 0; None for the start) and `'lines'`, one per set with an experiment kept: `'label'` (`'control (n = 3)'`), `'colour'`, `'line_style'`, `'mean'` (np.ndarray, (n_times,)) and `'spread'` (the SEM or SD, (n_times,); None for no band). `waterfall_traces_lister` gives the same with lines of `'label'`, `'colour'` and `'values'`. The maths is in `utils_shared/trace_alignment.py` (`trace_reader`, `traces_aligner`, `traces_averager`).

The roles of the plots of numbers per region, beside the group drop-downs: a Bar chart (P9, `bar_form_maker`), a Before and after (P10, `before_after_form_maker`), a Response by region (P11, `response_form_maker`) and a Time points (P12, `time_points_form_maker`: the roles of a Bar chart without `'time_point'`, which is its x axis; its sets are by Group 1 and Group 2 only). One that is not in the roles, or that this run does not have, is as the plot starts:

| Role | Value | Description |
|---|---|---|
| `'trace'` | `'vo2'`, `'haem_<name>'` or `'delta_psi'` | P9, P10, P12: the measurement, as the trace of a Mean trace without the oxygen (`'oxygen'` is read as `'vo2'`); starts `'vo2'` (`_measurement_reader`) |
| `'response_of'` | `'vo2'` or `'haems'` | P11 only: the OCR, or a row per haem ticked (offered only in a run that works out the haems); starts `'vo2'` |
| `'panel_haem_<name>'` | `'yes'` or `'no'` | P11 only: whether a haem has a row when `'response_of'` is `'haems'`, one for each haem of the fit, keyed as in a Standard experiment; starts `'yes'` |
| `'vo2_value'`, `'haem_view'`, `'delta_psi_value'` | as in a Mean trace | How the OCR, a haem and Δψ are shown, the one that fits the measurement being the one used. `'vo2_value'` starts `'baseline'`, in a Before and after `'raw'` (as % of baseline its baseline is 100 for every experiment). P11 has no `'delta_psi_value'` |
| `'region'` | `'baseline'` or `'addition 1'` … `'addition 10'` | P9, P12: the averaging region the numbers are from, the baseline or the one after an addition; starts `'addition 1'` (`_region_reader`) |
| `'region_from'`, `'region_to'` | as `'region'` | P10 only: its two regions; start `'baseline'` and `'addition 1'` |
| `'region_kind'` | `'settled'` or `'quick'` | The kind of averaging region read; asked only in a run with both kinds, otherwise the one the run has (`_kind_reader`); starts `'settled'` |
| `'bars'` | `'sem'` or `'sd'` | P9, P11, P12: what the bars show (`ERROR_CHOICES`, `utils_shared/region_statistics.py`); starts `'sem'` |
| `'test'` | `'student'` or `'welch'` | P9, P11, P12: the test between each pair of sets (`TEST_CHOICES`); starts `'student'`. A Before and after always uses the paired t-test |
| `'marks'` | `'stars'`, `'p'` or `'none'` | The marks over the brackets (`MARK_CHOICES`); starts `'stars'` |

The numbers of each, which the drawer, the caption line and the dataset workbook read, are a dictionary from `bar_numbers_lister`, `before_after_numbers_lister`, `response_numbers_lister` or `time_points_numbers_lister` (`utils_shared/page_plots.py`), each taking (the set-up, the roles, the slim experiments, the answers of the run):

| Key | In | Description |
|---|---|---|
| `'sets'` | P9, P10, P12 | The sets that have a number (`plot_set`), each with `'values'` (one per experiment of its `'names'`, None for none). P10: `'before'` and `'after'` in place of `'values'`. P12: also `'points'`, the time point of each experiment (`''` for none) |
| `'statistics'` | all | The `plot_statistics` of the plot: one column (P9), two columns, paired (P10), a column per time point in the order drawn (P12), or the columns and tests of every row in one, for the caption (P11) |
| `'rows'` | P11 | One per measurement that has a number (the OCR, or each haem ticked): `'trace'` and `'value'` (as `trace_reader` takes them), `'label'` (the title of its y axis), `'sets'` (each `plot_set` with `'regions'`: the number of each of its experiments in each region) and its own `'statistics'` (a column per region), its `'p_corrected'` corrected across the tests of every row |
| `'regions'` | P10, P11 | P10: the names of its two regions. P11: `'Baseline'`, then each addition as written on the plot of the first experiment kept |
| `'region'` | P9, P12 | The name of the region (`'Baseline'`, `'After addition 1'`) |
| `'label'` | P9, P10, P12 | The title of the y axis, with its unit |
| `'time_points'`, `'places'`, `'unit'`, `'ticks'`, `'title'` | P12 | The time points in the order drawn, where each sits on the x axis (its number when all are different numbers with one unit or none, otherwise 0, 1, 2…), that unit, the tick labels and the title of the axis (`_time_points_placer`) |
| `'trace'`, `'value'` | P12 | The measurement and how it is shown, as `trace_reader` takes them |
| `'left_out'`, `'differing'` | P11 | The experiments left out for another number of additions than most, and those kept whose additions are written otherwise than the first one's (`_additions_checker`); `response_checks_lister` gathers both over a page for the warnings at saving |
| `'error'`, `'test'`, `'marks'` | as asked | What the form says of the bars, the test and the marks |

One line of a Waterfall, listed from the top down by `waterfall_lines_lister` (`utils_shared/page_plots.py`): `'label'` (the time point with how many experiments its mean is of, `'2 h (n = 3)'`, or the experiment name), `'colour'` (`'#rrggbb'`: the colour of the set, or the colour of the group made lighter down the stack), `'wavelengths_nm'` and `'values_mOD'` (np.ndarray, (n_wavelengths,)), before the stacking (`spectra_stacker`).

#### `page_experiment`

The slim copy of one processed experiment that the plots of a dataset figure are drawn from. Made by `experiment_slimmer` (`utils_shared/page_data.py`) when the plot and the workbook of the file are saved (`experiment_file_saver`, `main.py`), so the file is not read again; kept as `{experiment name: page_experiment}` and handed, with the answers of the run, to `page_stage_runner`, `figure_page_drawer` and `dataset_figure_saver`. The whole spectra (`'raw_spectra'`) are never in it. A file that could not be read is not in the dictionary.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'experiment_name'`, `'metadata'`, `'haem_levels'`, `'averages'` | | | | As in `experiment`, each only when the experiment has it |
| `'CcO2'`, `'CsO2'`, `'VoO2'`, `'VoO2_OD'`, `'VoO2_percent'`, `'VoO2_baseline'`, `'haem_conc'`, `'haem_abs'`, `'haem_delta_abs'`, `'haem_OD'`, `'haem_abs_OD'`, `'haem_delta_abs_OD'`, `'haem_percent'`, `'delta_psi'` | pd.DataFrame | | | The tables of `experiment`, each only when the experiment has it (`TABLE_KEYS`) |
| `'difference'` | Optional[dict] | | | The difference spectrum, reduced minus oxidised (`region_difference`); None for a file without both regions or without spectra of the spectrometer that holds the haems |
| `'difference_parts'` | Optional[dict] | | | That difference split into the haems of the run's fit, the background, the fit and the residual (`region_difference_decomposition`, by `difference_decomposer` with the answer `haem_background`); None without a difference, or in a run that works out no haems |
| `'haem_bands'` | Optional[Dict[str, Tuple[float, float]]] | | nm | `{haem: (start, end)}` of the band of each haem of the run's fit, 2.5 nm each side of where its shape is strongest (`haem_bands_finder`, MATHS.md section 9.1), in the order of the fit and the same in every file; a haem whose shape is only zeros has none. None in a run that works out no haems |
| `'region_spectra'` | Optional[dict] | | | The mean spectrum of each averaging region: `'dataset'` (the spectrometer), `'wavelengths_nm'` (np.ndarray, (n_wavelengths,), nm) and `'mean_mOD'` (`{region name: np.ndarray (n_wavelengths,)}`, the mean attenuation of the spectra whose time is inside the region, in mOD; a region with no spectrum is left out). None for a file without those spectra |

#### `plot_set`

One set of experiments a plot shows, from its group drop-downs. Listed by `plot_sets_lister` (`utils_shared/page_data.py`), in the order first seen.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'name'` | str | | | The labels the set is split by, joined by ` · `; `'no labels'` when they are all blank; `'All experiments'` when nothing is split |
| `'names'` | List[str] | (n_experiments,) | | The experiments of the set |
| `'labels'` | Dict[str, str] | | | `{'group_1', 'group_2', 'time_point'}`: the label the set is split by or kept to (Only) in each column; `''` for a column left out |
| `'base_colour'` | str | | | The colour of its Group 1 label (`'#rrggbb'`); black for a set that is not one Group 1 label |
| `'line_style'` | str | | | `'-'`, `'--'`, `':'` or `'-.'` by the place of its Group 2 label in its column, when Group 2 is split; otherwise `'-'` |
| `'shade'` | float | | share of white | 0 for the first time point to 0.7 for the last, by the place of its time point in its column, when the time point is split; otherwise 0 |
| `'colour'` | str | | | The base colour with that share of white mixed in (`colour_shader`): what the set is drawn in |

#### `plot_statistics`

The numbers of one plot per region of a dataset figure (a Bar chart, Before and after, Response by region, Time points). Built by `plot_statistics_builder`, or by `paired_statistics_builder` for a Before and after (`utils_shared/region_statistics.py`), from the value of each experiment in a region (`region_value_reader`, `set_values_lister`, which adds `'values'` to each `plot_set`: one per experiment of its `'names'`, None for an experiment without one). The maths is in `MATHS.md` section 11.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'columns'` | List[dict] | (n_columns,) | | One per region (or time point) along the plot: `'label'` (its name) and `'sets'`, one per set: `'name'`, `'values'` (List[float], the experiments counted), `'n'`, `'mean'`, `'sd'` and `'sem'` (in the unit of the value shown; the mean NaN for an empty set, the SD and SEM for a set of fewer than two). A Before and after has two columns |
| `'tests'` | List[dict] | (n_tests,) | | One per comparison that could be tested: `'t'`, `'df'`, `'p'` (two-tailed) and `'p_corrected'` (Holm, across every test of the plot). Between sets: also `'column'` (from 0), `'first'` and `'second'` (the names of the two sets). Paired: also `'set'` (its name) and `'n'` (the experiments with both values). A set with one experiment is in no test |
| `'is_paired'` | bool | | | True for a Before and after |

The mark of a test is `p_value_marker` of its `'p_corrected'`; the legend sentence of the plot is `legend_sentence_writer`.

What a plot adds to the caption lines under the page, after its letter, comes from its plot type's entry in `CAPTION_WRITERS` (`utils_shared/page_data.py`, filled by `utils_shared/page_plots.py` beside `FORM_MAKERS`): a function of (the plot, the set-up, the slim experiments, the answers of the run) that gives the sentences on one line, or None for a plot with nothing to show. P9 to P12 have one (`bar_caption_writer`, `before_after_caption_writer`, `response_caption_writer`, `time_points_caption_writer`), each the legend sentence of its numbers; `caption_lines_builder` calls them.

#### `form_field`

One thing the form of a plot asks, as plain data, so the form is the same in the window and in the tests. Listed for a plot type by `form_fields_lister` (`utils_shared/page_data.py`, from `FORM_MAKERS`, filled by `utils_shared/page_plots.py`); made by `experiment_field_maker` (the experiment picker), `group_fields_lister` (the group drop-downs), `choice_field_maker` (a drop-down of fixed choices) and `tick_field_maker`. Shown by `PageBuilder` (`utils_viewer/viewer_page.py`).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'key'` | str | | | The name of the role it gives |
| `'kind'` | str | | | `'choice'` (a drop-down) or `'tick'` |
| `'label'` | str | | | The words beside it |
| `'choices'` | List[Tuple[str, str]] | (n_choices,) | | For a drop-down: (the role kept, the words shown), in the order shown; empty for a tick, and for a drop-down with nothing to pick from, which is not shown |
| `'value'` | str | | | The role it starts at: one of the choices, or `'yes'` or `'no'` for a tick |

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
| `kept` | Optional[dict] | | | `None` | The `kept_decomposition`, drawn beside the plot or faint under the haems as the answer `compare_layout` says, or None |
| `regions` | dict | | min | `{}` | The oxidised and reduced region of every file (`ViewerSession.regions`), which give a file with both its % oxidised |

#### `UserPlaces`

Defined in `utils_shared/user_places.py`. Created by `user_places_finder` when `main.py` is loaded (`PLACES`); the app's folders are made, and the program's fits copied in, by `user_folder_preparer`. Run from source (Windows, Linux, developers), every folder is the program folder. Run as the Mac app (`sys.frozen`), the program's own files are inside the app, which is never written to, and the user's things are in `Portimao` in the home folder.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `program_folder` | Path | | | | The program's own files (`fits/`, `assets/`, `QUESTION_FLOW.md`): the folder of `main.py`, or `sys._MEIPASS` inside the app |
| `own_folder` | Path | | | | The user's own folder; the data folders directly inside it are offered by number at question 1.1. The program folder, or `~/Portimao` in the app |
| `fits_folder` | Path | | | | `<own_folder>/fits`: the haem library (`haems/`), the presets (`presets/`), the user's own fit files, and where fits saved from the components go. In the app, each file of the program's fits folder that is missing (subfolders included) is copied in at every start; one already there is never overwritten |
| `journals_folder` | Path | | | | `<own_folder>/journals`: one `journal file` per journal. In the app, each file of the program's journals folder that is missing is copied in at every start; one already there is never overwritten, and a journal whose file is missing here is read from the program's own copy |
| `layouts_folder` | Path | | | | `<own_folder>/layouts`: one `figure template` per file. In the app, each template that comes with the program and is missing is copied in at every start; one already there is never overwritten |
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
| `panels` | List[Tuple[str, float, float]] | (n_panels,) | fraction of the height | `[]` | The key, bottom and top of each panel of the standard plot, top first (the keys of `'answers'['panel_order']`), so the window can put the arrows that move a panel beside it; empty for any other picture |

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
| `regions` | Dict[str, Dict[str, float]] | | min | `{}` | `{file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}}` as times on the original recording: those saved with the dataset at first, then those of the regions step (4.4), or the kept ones after *Keep old*. They are the regions saved with the dataset at the end. A region not chosen has its two edges together |
| `limits` | Dict[str, dict] | | | `{}` | The trim and ignore limits of every file as last answered (section 2), which say whether a file's regions still hold; empty before the trimming step |
| `has_od` | bool | | | `False` | True once the OD values of every file were entered in this run (3.2.1): the strip then offers per OD and the plots can be per OD |
| `has_windows` | bool | | | `False` | True once the averaging step (4.6) was answered with averaging regions in this run: the strip then offers the OCR as % of baseline |
| `redraw` | Optional[Callable[[], bool]] | | | `None` | Draws the plot of the step being asked again (set by each stage runner), for a change in the strip |
| `is_figure` | bool | | | `False` | True while the plot is the figure of each file at its saved size (section 5), so a new journal or size in the strip redraws it |
| `master_exporter` | Optional[Callable[[], None]] | | | `None` | Saves the master page of the file shown (set by `plots_stage_runner`); called for a click on *Export master* in the strip while `is_figure` is True |
| `is_choosing_regions` | bool | | | `False` | True while the edges of the regions are on the plot (4.4, or the Ox / Red tab): *Keep old* then leaves the regions as they are |
| `export_choice` | Optional[str] | | | `None` | What the last quick export (*Export full + trimmed csv* or *Export trimmed csv* in the trimming step) wrote, a key of `viewer_preview.EXPORT_PARTS`: `'trimmed'` (the spectra of the trimmed data as csv files) or `'full'` (those and the whole recording's of each trimmed file); `None` before anything is exported. With `export_limits`, it tells whether the trimmed csv files are written again at Export (5.9): not while the trim edges are those they were written with |
| `export_limits` | Dict[str, dict] | | | empty | The trim and ignore limits of each file when it was last exported |
| `full_exports` | Dict[str, List[Path]] | | | empty | `{file name: files written in its full/ folder}` in this run, so they are not written again when only the edges change, and are taken away when the file is no longer trimmed |
| `exported` | List[Path] | | | empty | The results folder, once the export has written into it; `viewer_asker` can share the caller's list, so the caller can say the export is kept when the questions are stopped |
| `time_tab` | str | | | `''` | The tab of the Time regions box whose edges are on the plot: `'trim'`, `'regions'`, `'windows'`, or `''` for none |
| `step_tab` | str | | | `''` | The tab of the step that waits with edges on the plot (2.1, 4.4, 4.6), or `''` |
| `step_choice` | Optional[EdgeChoice] | | | `None` | The edges of that step, kept as the user left them while another tab is pressed |
| `step_redraw` | Optional[Callable[[], bool]] | | | `None` | The plot of that step, drawn again when its tab is pressed again |
| `base_redraw` | Optional[Callable[[], bool]] | | | `None` | The plot of a question without edges, drawn again once a tab pressed meanwhile is left |
| `tab_switcher` | Optional[Callable[[str], None]] | | | `None` | Puts the edges of a tab on the plot (`_tab_switcher`, set by `viewer_asker`); `''` goes back to the step that waits |
| `edit_runner` | Optional[Callable[[str], None]] | | | `None` | Carries out a click on *Edit ODs*, *Edit labels* or an export button of the trim step opened again (`_box_edit_runner`, set by `viewer_asker`) |
| `pca_runner` | Optional[Callable[[], None]] | | | `None` | Carries out a click on *Do PCA*: the questions of the analysis of the whole dataset, then its components as the fit in use; set by `processing_stage_runner` only while the haem step (4.1) waits |

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
| Sheets | Always every table the experiment has, in this order (`DATA_SHEETS`, the experiment's key in brackets): `Measured O2` (`CcO2`), `Set O2` (`CsO2`), `OCR` (`VoO2`), `OCR per OD` (`VoO2_OD`), `OCR % of range` (`VoO2_percent`), `OCR % of baseline` (`VoO2_baseline`, for a file with a baseline region), `Haems ΔD` (`haem_delta_abs`), `Haems absorbance` (`haem_abs`), `Haems % oxidised` (`haem_percent`, for a file with both regions), `Haems ΔD per OD` (`haem_delta_abs_OD`), `Haems absorbance per OD` (`haem_abs_OD`), `Δψ` (`delta_psi`: Δψ and the potential at bH and at bL); then `Averages` (when averaging regions were averaged), `Events`, `How it was worked out` (when anything was) and `Metadata`. No haem amounts: only cells are measured, and an amount depends on the size of its shape |
| Location and name | `<results>/<experiment>/<experiment>.xlsx`: the trimmed data (all of it when the file is not trimmed), written by an export button of the trimming step and again, with its results added, by the experiment export (5.9) once the processing and figure are accepted (or by the run, when it could not be written then or a summary figure changed the fit); for a trimmed file *Export full + trimmed csv* also writes `<results>/<experiment>/full/<experiment>.xlsx`, the whole recording |

The export of the import has nothing worked out, so it writes only `Measured O2`, `Set O2`, `OCR`, `Events` and `Metadata`. In the trimmed workbook the Metadata holds the edges (`Trimmed before (min)`, `Trimmed after (min)` when trimmed, `Ignored at the start (min)`, `Ignored at the end (min)`); the whole recording's holds none, so it does not change when they do. The lines of the Metadata the program adds have plain names (`METADATA_TEXTS`: also `OD`, `Volume (mL)`, `Dilution factor`, `Fit`, `Background fitted`, `Processed on`); what comes from the `.paf` file keeps its name.

| Column (data sheets) | Type | Units | Description |
|---|---|---|---|
| `Time (min)` | float | min | Time of the point |
| `Spectrum number` | int | | The experiment's `spectrum_index` (haem and Δψ sheets only) |
| measurement columns | float | in the heading | One per trace or haem, with its unit: `OCR (µM min⁻¹)`, `OCR per OD (µM min⁻¹ OD⁻¹)`, `OCR (% of range)`, `OCR (% of baseline)`, `<haem> ΔD (mOD)`, `<haem> absorbance (mOD)`, `<haem> (% oxidised)`, `<haem> ΔD (mOD OD⁻¹)`, `<haem> absorbance (mOD OD⁻¹)`; the oxygen and Δψ sheets keep the headings of their tables |

The `Events` sheet has the columns `Event`, `Data point`, `Time (min)`, `Text in the file`, `Label`, `Stock (mM)`, `Added (µL)`, `This addition (µM)`, `In the chamber (µM)` and `Ignored` (the stock, the volume and the two concentrations of `event`, each empty where unknown). Nothing is read back from a workbook: the OD values and labels are kept in the dataset's settings.

The `How it was worked out` sheet has the columns `What`, `For` (a haem, or empty), `Value` and `Unit`, with only the lines the experiment has: `Fit`; `Background fitted`; `Background formula (w in nm)` (OD, its formula in plain text, `B = b₀ + b₁·w`, from `BACKGROUND_PLAIN_FORMULAS`); for each haem `Start of ΔD (what was taken off)` (mOD) and `Start of ΔD, taken from` (`5.00 to 5.41`, min); `Oxidised region` and `Reduced region` (min, on the time of the trimmed data); for each haem `Oxidised level` and `Reduced level` (mOD); `Δψ: haem used` (bH, bL), `Δψ: midpoint potential` (one per midpoint, mV), `Δψ: share`, `Δψ: temperature` (°C), `Δψ: lowest limit` and `Δψ: highest limit` (% reduced), `Δψ: spectra with a value` (`180 of 240`); and, for a file scaled by OD, `OD scaling: OD`, `OD scaling: volume` (mL), `OD scaling: dilution factor` and `OD scaling: how`.

The `Averages` sheet has one row per averaging region, the baseline, then the settled and then the quick regions in time: `Average`, `Kind` (baseline, settled or quick; `settled (left out)` or `quick (left out)` for a region the user left out, whose numbers are empty), `Start time (min)`, `End time (min)` then `OCR mean (<unit>)`, `OCR SD (<unit>)`, `OCR difference from baseline (<unit>)` and `OCR (% of baseline)`, the unit being that of the OCR that was averaged (`µM min⁻¹`, `µM min⁻¹ OD⁻¹` or `% of range`); for each haem in the views `ΔD` and `absorbance` `<haem> <view> mean (<unit>)`, `<haem> <view> SD (<unit>)` and `<haem> <view> difference from baseline (<unit>)`, in `mOD`, or `mOD OD⁻¹` when the plot is per OD, and for % oxidised `<haem> mean (% oxidised)`, `<haem> SD (% oxidised)` and `<haem> difference from baseline (% oxidised)`; and, for an experiment with Δψ, `Δψ mean (mV)`, `Δψ SD (mV)`, `Δψ difference from baseline (mV)` and `Δψ spectra used` (`5 of 9`: the spectra of the region with a value, of all its spectra). A per in a unit is written as a power of -1, never with a slash. The notes under the table say what each column is.

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
| Location and name | `fits/presets/<name>.csv`. Five presets keep the names of the fit files they replaced, so a dataset saved with one of those names finds it; the sixth, `rowan_fit_11_2026.csv`, was `temp_fit_037v.csv`, and a dataset saved with that name opens with it (`dataset_settings.RENAMED_ANSWERS`). The standard fit is `bswitch_no2_mycobl_b557.csv` (`config.STANDARD_FIT`) |

A preset is a set of haems of the library, offered by its name in the fit question and the strip, before the user's own fit files. A fit file of the fits folder with a preset's name is not offered. Read by `preset_importer`:

| Line | Read by the program | Description |
|---|---|---|
| `Portimao preset,format 1` | Yes | Always first. A newer format than the program knows is refused |
| `Name,<text>` | Yes, optional | The name the Fit list shows (`fit_titles_lister`); without it, the file name without .csv |
| `Holds,<text>` | No | What the preset is, in words |
| (empty line) | Yes | Ends the heading lines |
| `Haem file,Haems per protein` | No | Names the columns |
| `<file>.csv,<number>`, one per line | The file name only | A file of `fits/haems/`, in any order: the haems are put in the order a, b, c. A missing file, a file of more than one haem, and two haems of the same name are refused, each with a message. The number, for the reader only, is how many haems the shape was drawn for in its source fit: 2 for `c1_037v.csv` (the two haems of the cc), 1 for every other. Only cells are measured, so a shape's size never changes the absorbance, ΔD or % |

Example (`fits/presets/rowan_fit_11_2026.csv`):

```text
Portimao preset,format 1
Name,Rowan fit 11-2026
Holds,"The haems of the Rowan fit of November 2026 (once temp_fit_037v), each at the size that fit gives it"

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
| Location and name | `<results>/<experiment>/<dataset>_<type>.csv` (the trimmed spectra) and, for a trimmed file exported with the whole recording (*Export full + trimmed csv* in the trimming step, or 3 at Export, 5.9), `<results>/<experiment>/full/<dataset>_<type>.csv`; type `transmiss`, `intensity` or `attenuation`. The workbook beside the trimmed ones lists them on its `Spectral data` sheet, also when it is written later without writing them again (those of the quick export, which writes no workbook, are found by their names in its folder) |
| Size | About 19, 8 and 21 bytes per value for the three types (`SPECTRA_CSV_BYTES` in `config.py`), so about 1.2 GB for a 100 MB `.paf` file |

| Column | Type | Units | Description |
|---|---|---|---|
| `Wavelength (nm)` | float | nm | Wavelength |
| `<time> min` | float | see the type | One column per spectrum, headed by its time in minutes to 6 decimals with the trailing zeros dropped (`0.008333 min`, `2 min`), so no two spectra share a heading |

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

#### `journal file`

What one journal asks of a figure. Read by `journal_specs_loader` (`utils_shared/journal_files.py`) into `config.JOURNAL_SPECS` when the program starts; a file that cannot be used is left out and named in `config.JOURNAL_PROBLEMS`.

| Property | Value |
|---|---|
| File type | JSON: the name of each thing, then its value |
| Encoding | UTF-8 |
| Location and name | `journals/<journal>.json` in the user's own folder (`UserPlaces.journals_folder`); the file name, in lower case, is the journal's name in the answers (`nature.json` is `'nature'`). Nature, Science, Cell and PNAS are offered first, the others by name |

| Name | Type | Units | Kept in `JOURNAL_SPECS` as | Description |
|---|---|---|---|---|
| `name` | text | | `'name'` | The journal as shown to the user |
| `widths_mm` | `{"columns": width}` | columns, mm | `'widths_mm'` (the columns as numbers, narrowest first) | The widths a figure can have, by the number of columns: `{"1": 89, "1.5": 120, "2": 183}` |
| `tallest_figure_mm` | number above 0 | mm | `'page_height_mm'` | The tallest figure; the height of a figure is a share of it |
| `smallest_text_pt` | number above 0 | pt | `'font_min_pt'` | The smallest text; the text of a figure is lifted to it |
| `largest_text_pt` | number above 0, or `null` | pt | `'font_max_pt'` | The largest text; `null` when the journal gives none, and no text is then too large |
| `panel_letter_pt` | number above 0 | pt | `'panel_letter_pt'` | Size of the bold panel letters |
| `panel_letter_case` | `"upper"` or `"lower"` | | `'panel_letter_case'` | A, B, C or a, b, c |
| `fonts` | list of text | | `'font_family'` | The fonts, the wanted one first; the first that is on the computer is used |
| `thinnest_line_pt` | number above 0, or `null` | pt | `'line_min_pt'` | The thinnest line; every thinner line of a figure is thickened to it (`figure_lines_fitter`) |
| `thickest_line_pt` | number above 0, or `null` | pt | `'line_max_pt'` | The thickest line; every thicker line is thinned to it |
| `picture_dpi` | number above 0 | dots per inch | `'dpi'` | Sharpness of the pictures saved of a figure |
| `page_mm` | `[width, height]`, or `null` | mm | `'paper_mm'` | The printed page, for the master page; `null` when not known, and A4 then stands in |
| `read_at`, `confirmed`, `notes` | text | | not kept | Where the numbers were read, which were confirmed by hand and when, and what is still to confirm; for the reader of the file only |

Refused, with the reason in one sentence: a file that is not readable JSON; a missing `name`, width, tallest figure, smallest text, panel letter size or picture sharpness; a number that is not above 0; a largest text under the smallest, or a thickest line under the thinnest; a page smaller than the largest figure. With no usable `nature.json`, the numbers for Nature kept in the program (`STANDARD_SPEC`) are used.

#### `figure template`

The layout of a dataset figure, to use again on any dataset. Written by `template_saver` and read by `template_reader` (`utils_shared/figure_page.py`).

| Property | Value |
|---|---|
| File type | JSON |
| Encoding | UTF-8 |
| Location and name | `layouts/<name>.json` in the user's own folder (`UserPlaces.layouts_folder`); the name as the user typed it, cleaned by `file_name_sanitiser`. A template of the same name is written over only when the user says so |

| Name | Type | Units | Description |
|---|---|---|---|
| `kind` | text | | Always `"Portimao figure template"` |
| `version` | whole number | | `1` |
| `journal`, `columns`, `height` | text, number, number | columns, fraction of the tallest figure | The page size (`FigurePage`) |
| `plots` | list | | One entry per plot, in the order placed: `{"type": "P9", "cells": {"row": 0, "column": 3, "rows": 2, "columns": 3}, "roles": {"group_1": "Split"}}` (`PagePlot`) |

Refused, with the reason in one sentence naming the file: a file that is not readable JSON or not of this kind; another version; a page size that cannot be read; a plot with no cells, of an unknown type, of the Legend (P16, no longer a plot type), past the edge of the grid or over another plot; a role that names a file (ending in `.paf`, `.csv`, `.xlsx`, `.txt`, `.bin`, `.fit` or `.json`, or holding a folder). A page with such a role is not saved.

#### `dataset figure`

| Property | Value |
|---|---|
| File type | PDF, one page of exactly the figure's printed size: the journal's width for the page's columns, and the page's share of the journal's tallest figure |
| Location and name | `<results folder>/dataset_figure_<journal>.pdf`, written in the run by `figure_page_exporter` (`utils_shared/figure_page.py`) for a page with at least one plot, and written over at each run |

Drawn as lines and text, not as a picture; the fonts are embedded as TrueType (PDF font type 42), so the text can still be changed in a drawing program.

#### `master page`

| Property | Value |
|---|---|
| File type | PDF, one page of the journal's page size (A4 when the journal file gives none) |
| Location and name | `<results folder>/<experiment>_master_<journal>.pdf`, written by `master_page_exporter` (`utils_shared/master_page_exporter.py`) for a click on *Export master* in the strip; `<results folder>/dataset_figure_master_<journal>.pdf` for the dataset figure, written in the run by `dataset_figure_saver` (`main.py`) |

The figure of the file as a picture of 600 dots per inch at its printed size, starting at the top left of the text area; under it a box reading "Figure legend"; the journal's columns filled with grey lines standing for text; one small line at the top naming the journal, the page size, the file and the size of the figure. The margin at the sides, top and bottom is (page width - widest figure) / 2 (`master_page_layout_builder`).

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
| Concentration of an addition | µM | `_uM` in keys; written by `concentration_formatter` as nM, µM, mM or M (four significant figures on a label), and `? µM` when none was given; the Events sheet gives the stock in mM |
| Volume added | µL | `_uL` in keys |
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
