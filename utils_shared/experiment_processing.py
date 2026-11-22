"""
Reading and processing of one experiment (everything before the figure and the export).
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.attenuation import experiment_attenuation_adder
from utils_shared.averaging import experiment_averages_calculator
from utils_shared.normalisation import experiment_normaliser, percent_converter
from utils_shared.paf_reader import experiment_paf_loader, PafError
from utils_shared.redox_regions import haem_levels_finder, percent_oxidised_calculator
from utils_shared.schema import time_getter
from utils_shared.spectral_decomposer import (BACKGROUND_LABELS,
                                              experiment_decomposer,
                                              fit_range_finder,
                                              )
from utils_shared.trimming import experiment_trimmer
from utils_shared.user_notices import problem_shower, warning_shower


# ---- EXPERIMENT PROCESSING HELPERS ---------------------------------------------------


# ---- _skip_reporter ------------------------------------------------------------------
def _skip_reporter(step: str, error: Exception) -> None:
    """
    ---- Summary ----
    Helper function to tell the user in plain words that a step was skipped for this
    file, why, and what to do.

    ---- Inputs ----
    step : str
        The step in plain words, to complete "Warning: ... was skipped".
    error : Exception
        The error that stopped the step. The messages the processing steps write for
        the user are shown as they are; Python's own error text never is.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Shows the warning; the details go to the log (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    problem_shower
    """

    problem_shower(f'  Warning: {step} was skipped for this file; the rest carries on '
                   f'without it',
                   error,
                   )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- event_settings_merger -----------------------------------------------------------
def event_settings_merger(experiment: dict, events: List[dict]) -> None:
    """
    ---- Summary ----
    Main function to copy the label, concentration and ignored flag entered for each
    event onto the experiment, and to move ignored events out of the working event list.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    events : List[dict]
        Entered events: {datapoint, label, concentration_uM, ignored}.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Updates experiment["metadata"]["events"] in place and adds
    experiment["metadata"]["ignored_events"] (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Apply the entered settings to the events ----------------------------------
    entered = {e['datapoint']: e for e in events}
    for event in experiment['metadata'].get('events', []):
        item = entered.get(event['datapoint'])
        if item:
            event['label'] = item['label'] or event['text']
            event['concentration_uM'] = item['concentration_uM']
            event['ignored'] = bool(item.get('ignored', False))

    # ---- 2 Separate the ignored events -----------------------------------------------
    # Ignored events leave the working list (so nothing plots or averages them) but are
    # kept in metadata["ignored_events"] so the workbook still records them.
    metadata = experiment['metadata']
    events = metadata.get('events', [])
    metadata['ignored_events'] = [e for e in events if e.get('ignored')]
    metadata['events'] = [e for e in events if not e.get('ignored')]


# ---- experiment_data_processor -------------------------------------------------------
def experiment_data_processor(info: dict,
                              cfg: settings.Config,
                              fit: Optional[dict],
                              experiment: Optional[dict] = None,
                              ) -> dict:
    """
    ---- Summary ----
    Main function to read (or take) one experiment and process its data: trim, decompose
    into haems, find each haem's oxidised and reduced level and its % oxidised (a file
    with both regions), scale by OD, put the OCR on its % of the range, choose the
    plotted sources and average around the events. It draws and saves nothing.

    ---- Inputs ----
    info : dict
        Per-file information from everything_asker: path, name, trim and ignore times,
        OD values, events and, when kept for the file, 'regions' (the four edges of
        its oxidised and reduced region, as times on the original recording, min).
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    experiment : Optional[dict]
        An experiment already read from the file (the experiment browser keeps a copy
        so the file is not read again). It is processed in place. None reads the file.

    ---- Globals read ----
    settings.HAEM_FACTOR, settings.REFERENCE_WINDOW_POINTS,
    settings.REGION_MINIMUM_POINTS, settings.BASELINE_MINIMUM_SECONDS;
    BACKGROUND_LABELS.

    ---- Outputs ----
    dict
        {experiment, od_available, vo2_source, haem_source}. A file with both regions
        has experiment['haem_levels'] and experiment['haem_percent'] (DATA_FORMAT.md);
        when % oxidised is asked for a file without them, its haem source is
        'delta_abs'. Prints progress and the reason when a step is skipped (side
        effect).

    ---- Globals mutated ----
    None. Processes the experiment dictionary in place (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _skip_reporter
    event_settings_merger
    experiment_attenuation_adder
    experiment_averages_calculator
    experiment_decomposer
    experiment_normaliser
    experiment_paf_loader
    experiment_trimmer
    fit_range_finder
    haem_levels_finder
    percent_converter
    percent_need_checker
    percent_oxidised_calculator
    source_chooser
    time_getter
    warning_shower
    """

    # ---- 1 Set up the run ------------------------------------------------------------
    a = cfg.answers
    ignore_first, ignore_last = info['ignore_start'], info['ignore_end']
    window_points = settings.REFERENCE_WINDOW_POINTS

    # ---- 2 Read the file -------------------------------------------------------------
    if experiment is None:
        datasets = (None
                    if a['export_spectra']
                    else ((a['decomposition_dataset'],) if a['decompose'] else ())
                    )
        experiment = experiment_paf_loader(info['path'],
                                           spectral_datasets=datasets,
                                           with_intensity=a['export_spectra'],
                                           )
    metadata = experiment['metadata']
    for key in ('OD', 'volume', 'dilution_factor'):
        if info.get(key) is not None:
            metadata[key] = info[key]
    event_settings_merger(experiment, info.get('events', []))
    skipped = len(metadata.get('ignored_events', []))
    print(f"  Read {len(experiment['CcO2'])} points, "
          f"{len(metadata['events'])} event(s)" +
          (f' ({skipped} ignored)' if skipped else ''),
          )

    # ---- 3 Trim the experiment -------------------------------------------------------
    if info.get('trim_start') is not None or info.get('trim_end') is not None:
        experiment_trimmer(experiment,
                           start_time=info.get('trim_start'),
                           end_time=info.get('trim_end'),
                           )
        if info.get('trim_start') is not None:
            print(f"  Trimmed: data before {info['trim_start']:g} min discarded (that "
                  f'point is now time 0)',
                  )
        if info.get('trim_end') is not None:
            print(f"  Trimmed: data after {info['trim_end']:g} min discarded")

    # ---- 4 Prepare the data ----------------------------------------------------------
    # ---- 4.1 Check OD scaling is possible --------------------------------------------
    od_available = False
    if a['normalise_od']:
        od_available = all(metadata.get(k) for k in ('OD', 'volume', 'dilution_factor'))
        if not od_available:
            warning_shower('  Warning: OD, volume or dilution factor is missing, so '
                           'this file is not scaled by OD (raw values are used '
                           'instead).',
                           )

    # ---- 4.2 Decompose into haems ----------------------------------------------------
    # Attenuation and decomposition into haems.
    if a['decompose']:
        try:
            attenuation_datasets = (None
                                    if a['export_spectra']
                                    else (a['decomposition_dataset'],)
                                    )
            if fit is None or 'data' not in fit:
                raise ValueError('No fit file was loaded, so the haems cannot be '
                                 'worked out. Choose a fit file when the program asks '
                                 'for one.',
                                 )
            experiment_attenuation_adder(experiment,
                                         datasets=attenuation_datasets,
                                         checked_range_nm=fit_range_finder(fit['data']),
                                         )
            print('  Decomposing ...')
            experiment_decomposer(experiment,
                                  fit,
                                  dataset_name=a['decomposition_dataset'],
                                  spectrum_type='attenuation',
                                  background=a['haem_background'],
                                  haemfactor=settings.HAEM_FACTOR,
                                  delta_exclude_first_minutes=ignore_first,
                                  delta_window_points=window_points,
                                  delta_exclude_last_minutes=ignore_last,
                                  )
            reference = experiment['haem_delta_abs'].attrs['delta_abs_baseline']
            spans = ', '.join(f'{haem} {first:.2f}-{last:.2f} min'
                              for haem, (first, last)
                              in reference['window_by_haem'].items()
                              )
            print(f"  Decomposed with {a['fit_file']} and a "
                  f"{BACKGROUND_LABELS[a['haem_background']]} background; the zero "
                  f'of ΔD is where each haem starts, the median of its first '
                  f"{window_points} spectra ({reference['window_seconds']:.3g} s) "
                  f'after the ignored start: {spans}',
                  )
            for note in fit.get('notes', []):
                warning_shower(f'  {note}')
        except (KeyError, ValueError, PafError) as exc:
            _skip_reporter('the decomposition into haems', exc)
    elif a['export_spectra']:
        experiment_attenuation_adder(experiment)

    # ---- 4.3 Find each haem's two levels and its % oxidised --------------------------
    # Only for a file with both regions; any other has no % oxidised.
    if 'haem_abs' in experiment:
        try:
            times = time_getter(experiment['haem_abs'])
            last = float(np.nanmax(times)) - ignore_last
            levels = haem_levels_finder(experiment['haem_abs'],
                                        info.get('regions'),
                                        info.get('trim_start') or 0.0,
                                        (ignore_first, max(last, ignore_first)),
                                        settings.REGION_MINIMUM_POINTS,
                                        label=info['name'],
                                        )
            if levels is not None:
                experiment['haem_levels'] = levels
                experiment['haem_percent'] = percent_oxidised_calculator(
                    experiment['haem_abs'],
                    levels['oxidised'],
                    levels['reduced'],
                    )
                spans = ', '.join(f'{region} {start:.2f}-{end:.2f} min'
                                  for region, (start, end)
                                  in (('oxidised', levels['oxidised_region']),
                                      ('reduced', levels['reduced_region']),
                                      )
                                  )
                print(f"  Each haem's oxidised and reduced level is its median in "
                      f'the regions: {spans}',
                      )
        except (KeyError, ValueError, TypeError) as exc:
            _skip_reporter('the % oxidised of the haems', exc)

    # ---- 4.4 Normalise by OD ---------------------------------------------------------
    if od_available:
        try:
            experiment_normaliser(experiment)
            print(f"  OD scaling: OD {metadata['OD']:g}, volume {metadata['volume']:g}"
                  f", dilution factor {metadata['dilution_factor']:g}",
                  )
        except (KeyError, ValueError) as exc:
            od_available = False
            _skip_reporter('the scaling by OD', exc)

    # ---- 4.5 Put the OCR on its % of the range ---------------------------------------
    if cfg.percent_need_checker() and 'VoO2' in experiment:
        try:
            percent_converter(experiment,
                              'VoO2',
                              'VoO2_percent',
                              exclude_first_minutes=ignore_first,
                              exclude_last_minutes=ignore_last,
                              window_points=window_points,
                              )
        except (KeyError, ValueError, TypeError) as exc:
            _skip_reporter('the % scale of the oxygen consumption', exc)

    # ---- 5 Choose the sources and average --------------------------------------------
    vo2_source, haem_source = cfg.source_chooser(od_available)
    if haem_source is not None and not (a['plot_haems'] or a['averaging']):
        haem_source = None
    # A file without both regions has no % oxidised, so its haems stay in delta D.
    if haem_source == 'percent' and 'haem_percent' not in experiment:
        haem_source = 'delta_abs'
        if 'haem_delta_abs' in experiment:
            print('  This file has no oxidised and reduced region, so its haems are '
                  'shown as ΔD.',
                  )
    # Event-window averages.
    if a['averaging']:
        if not metadata['events']:
            warning_shower('  Averaging skipped: this file has no events.')
        else:
            try:
                average_haem_source = (haem_source
                                       if 'haem_conc' in experiment
                                       else None
                                       )
                final_gap = a['final_gap_minutes']
                minimum_seconds = settings.BASELINE_MINIMUM_SECONDS
                experiment_averages_calculator(experiment,
                                               window_minutes=a['window_minutes'],
                                               gap_minutes=a['gap_minutes'],
                                               final_window_gap_minutes=final_gap,
                                               vo2_source=vo2_source,
                                               haem_source=average_haem_source,
                                               baseline_minimum_seconds=minimum_seconds,
                                               )
                print(f"  Calculated {len(experiment['averages']['windows'])} event "
                      f'averages',
                      )
                skipped = dict(experiment['averages']['skipped'])
                if skipped.pop('average0', None):
                    warning_shower(f'  Warning: there is less than {minimum_seconds:g} '
                                   's of data before the first addition, so this run '
                                   'has no baseline and its changes from baseline are '
                                   'left empty. Trim less of the start, or shorten the '
                                   'gap before the additions.',
                                   )
                if skipped:
                    warning_shower(f'  Warning: averaging skipped for '
                                   f"{', '.join(skipped)} (not enough time for the "
                                   f'window and gap)',
                                   )
            except (KeyError, ValueError, TypeError) as exc:
                _skip_reporter('the averaging around the additions', exc)

    # ---- 6 Return the processed experiment -------------------------------------------
    return {'experiment': experiment,
            'od_available': od_available,
            'vo2_source': vo2_source,
            'haem_source': haem_source,
            }
