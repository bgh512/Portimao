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
| `'haem_conc'` | pd.DataFrame | (n_spectra, 2 + n_haems) | | Optional. Fitted haem concentrations; columns `Time (min)`, `spectrum_index` and one per haem |
| `'haem_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. Haem concentration x peak of the fit spectrum |
| `'haem_delta_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. `haem_abs` shifted so that, for each haem, the median of its highest 50 spectra in a row (outside the ignored start and end; `REFERENCE_WINDOW_POINTS` in `config.py`) is 0 |
| `'haem_OD'`, `'haem_abs_OD'`, `'haem_delta_abs_OD'` | pd.DataFrame | (n_spectra, 2 + n_haems) | | Optional. The matching tables divided by dilution factor x OD x volume |
| `'haem_percent'` | pd.DataFrame | (n_spectra, 2 + n_haems) | % | Optional. `haem_conc` scaled to 0-100 % |
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
| `'fit_file'` | str or None | | | Fit file of the decomposition; None when the haems were not decomposed |
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
| `'events'` | List[dict] | | | The additions stored inside the recording, in the order of their spectrum numbers, each with `'name'` (the software's name for it, `Event 1`), `'text'`, `'datapoint'`, `'time'` (min) and `'row_index'` as in `event`. They are the same additions, with the same times, as `experiment_paf_loader` gives |
| `'traces'` | List[str] | | | Names of the recorded traces |

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

A haem fit, as `fit_importer` reads a fit file and `fit_table_builder` builds the components found by the principal component analysis.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'haem_list'` | List[str] | (n_haems) | | Haem (or component) names, in file order |
| `'data'` | pd.DataFrame | (n_wavelengths, 2 x n_haems) | nm, OD per unit | (wavelength, response) column pairs, one pair per haem. The decomposition uses the response as the basis spectrum; it has the sign of the attenuation, -log10(T). Each haem's rows are at the top, with wavelengths going upwards and blanks (NaN) below a shorter haem. The responses are on the standard scale: the highest point of the shapes lies between 1e-7 and 1e-3 |
| `'scale_divisor'` | float | | | What the responses were divided by to reach the standard scale: 1, or 1 000 000 |
| `'notes'` | List[str] | | | Sentences for the user: leftover rows left out of a haem, a fit divided by a million, a fit on neither scale |

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

The haem type of each component (`'a'`, `'b'`, `'c'`, `'mixed'` or `'unknown'`) is worked out separately by `component_classifier`, from where its clear peaks and troughs are: the alpha and Soret bands of haem c (545-556.5 and 410-423 nm), b (556.5-570 and 423-437 nm) and a (595-612 and 437-450 nm). `config.pca_colour_mapper` turns the types into colours (`PCA_TYPE_COLOURS`).

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

Saved to `last_answers.json` next to `main.py`: the data folder offered on the next run. The answers themselves are kept with each dataset (`dataset_settings`).

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'data_folder'` | str | | | Full path of the folder of the `.paf` files used last |

#### `dataset_settings`

The settings last saved for a dataset. Returned by `dataset_settings_reader` (`utils_shared/dataset_settings.py`), written by `dataset_settings_saver` to `portimao_settings.json` in the data folder, and laid over `config.DEFAULT_ANSWERS` (the standard settings) when the dataset is opened again. Empty for a dataset never saved.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'export_folder'` | Optional[Path] | | | Results folder; `None` when none was kept or it was a full path on another computer. In the file it is text: relative to the data folder with forward slashes when inside it (`export`), otherwise the full path |
| `'answers'` | dict | | | Terminal answers |
| `'files'` | dict | | min | `{file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end'}}`; trim times are on the original recording, ignore times count from the new 0 after trimming |

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

#### `PreviewSpec`

Defined in `utils_viewer/viewer_preview.py`. Created by `preview_drawer`; every file is drawn with the same spec.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `answers` | dict | | | | Answers so far (missing keys come from `config.DEFAULT_ANSWERS`) |
| `limits` | dict | | min | | `{file name: {trim_start, trim_end, ignore_start, ignore_end}}` |
| `fit` | Optional[dict] | | | | Fit dictionary from `fit_importer`, or None |
| `details` | dict | | | | `{file name: {OD, volume, dilution_factor, events}}` |
| `show_trim` | bool | | | `False` | Draw the whole recording and shade the trimmed part |
| `show_ignored` | bool | | | `True` | Shade the ignored start and end |

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

Defined in `utils_viewer/viewer_preview.py`. Created by `viewer_asker`, used by the stage runners, `preview_drawer` and the preview thread.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `summaries` | List[dict] | (n_files,) | | | The `experiment_summary` of each file |
| `export_root` | Path | | | | Results folder |
| `window` | ViewerGui or PictureWindow | | | | The browser window, or the preview picture file when no window can open |
| `current` | int | | | `0` | Index of the file being looked at |
| `cache` | OrderedDict | | | empty | `{file name: {'experiment': experiment}}` of the last 3 files read; each preview works on a deep copy |

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

The file is one record after another. Each record starts with the byte `06`, the word `Espana`, five zero bytes and a 16-byte identifier, followed by its strings: the kind of record, the vendor and a name. The reader uses these kinds:

| Kind of record | What it holds |
|---|---|
| `DataItem`, then `Measurement` | One trace (the clock `Time`, `CcO2`, `CsO2`, `VoO2` and others). The number of values is stored twice near the end of the `DataItem` (28 and 20 bytes before it); the `Measurement` ends with that many 32-bit floats and 8 closing bytes, and its strings give the quantity and the unit |
| `Spectra: CCD` | One spectrometer: the number of spectra and of wavelengths, a table numbering the spectra 1, 2, 3 and so on, a block of settings, the wavelengths (32-bit floats, nm), then the rows of spectra |
| `Text Event` | One addition: its name (`Event 1`), the text typed, and its spectrum number (unsigned 32-bit, 20 bytes after the name) |
| `PaneNote` | The notes of the experiment, as rich text |

- **Clock:** the `Time` trace, in seconds from the start (0.5 s steps in the recordings seen). When a file holds it twice, the longer one is used.
- **Traces:** a trace is used when it has at least 90 % of the clock's length. A shorter trace is lined up with the clock from the start, so only its end is empty. A trace whose two stored lengths disagree, that holds no values or that does not fit in its record is not read; this is reported, with the reason, only for the traces the program uses.
- **Spectra rows:** (number of spectra + 2) rows of 32-bit floats, one value per wavelength: a row of zeros, log10 of the reference spectrum, then log10 of the counts of each spectrum. So counts = 10^row, rounded to a whole number, and transmission = 10^(row - reference row). Spectrum 1 belongs to the first time point of the clock, and so on.
- **Additions:** each addition is stored more than once; the first copy has the spectrum number 0 and the later ones the real number.
- **Not read:** files whose spectra are not numbered 1, 2, 3 without gaps, or that have more spectra than time points, are refused with a message.

#### `individual experiment workbook`

| Property | Value |
|---|---|
| File type | xlsx |
| Sheets | `CcO2`, `CsO2`, `VoO2` and, for the full export, `VoO2_OD`, `VoO2_percent`, `haem_conc`, `haem_abs`, `haem_delta_abs`, `haem_OD`, `haem_abs_OD`, `haem_delta_abs_OD`, `haem_percent`; plus `Averages`, `Events` and `Metadata` when available |
| Location and name | `<results>/<run folder>/<experiment>/<experiment>.xlsx` |

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
| Encoding | UTF-8 (line ends CRLF when written by the program) |
| Location and name | `fits/<name>.csv`; the program saves the components found by the principal component analysis here |

| Column | Type | Units | Description |
|---|---|---|---|
| `<haem>` | float | nm | Wavelength column of one haem; the header names the haem (every second column, starting with the first) |
| `<haem> response` | float | | Response of that haem at those wavelengths; the header of this column is not used. Components from the principal component analysis have a largest peak of 1e-6 (the component divided by a million) |

Rules, checked by `fit_importer`: the columns come in pairs and every wavelength column has a haem name; every cell is a number or empty; a row holds both a wavelength and a response, or neither; each haem has at least two rows. The haems may have different lengths, and empty rows are skipped wherever they are. Within a haem the wavelengths go upwards (a haem written wholly downwards is turned round); where they jump backwards, the rows from the jump on are left out and the user is told. Scale: the highest point of the shapes (largest |response| in the file) is between 1e-7 and 1e-3; a file a million above that (0.1 to 1000) is divided by a million when read, and a file on neither scale is used as it is with a warning.

#### `spectral csv`

| Property | Value |
|---|---|
| File type | CSV |
| Delimiter | comma |
| Encoding | UTF-8 |
| Location and name | `<results>/<run folder>/<experiment>/<dataset>_<type>.csv`, type `transmiss`, `intensity` or `attenuation` |

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
| Location and name | `last_answers.json` next to `main.py` (not committed) |

Structure: see `last_answers` in section 1.1.

#### `portimao_settings.json`

| Property | Value |
|---|---|
| File type | JSON |
| Encoding | UTF-8 |
| Location and name | `portimao_settings.json` in the folder of the `.paf` files, so it travels with the dataset |

Structure: see `dataset_settings` in section 1.1.

#### `preview picture`

| Property | Value |
|---|---|
| File type | `.png` |
| Location and name | `Portimao_preview.png` in the system temporary folder |

Written, and opened in the default picture viewer, only when the experiment browser window cannot open. Overwritten by each preview. Extra pictures, such as the PCA components and examples, are written next to it as `Portimao_preview_<title>.png` (the title in lower case, with every other character as `_`).

#### `log file`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `<results>/logs/YYYY_MM_DD-HH_MM_SS.log` |

The first lines are the project version, the random seed (none: the program uses no random numbers) and the settings of the run, then everything printed during the run.

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
