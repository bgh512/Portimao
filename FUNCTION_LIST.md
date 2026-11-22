# Portimao - Function List

- **Project:** Portimao
- **Version:** V2.15
- **Date:** 22/11/2026

## Contents

- [`config.py`](#configpy)
    - [`Config`](#config)
    - [`haem_colour_mapper`](#haem_colour_mapper)
    - [`pca_colour_mapper`](#pca_colour_mapper)
- [`launchers/mac_app_builder.py`](#launchersmac_app_builderpy)
    - [`_ad_hoc_signer`](#_ad_hoc_signer)
    - [`_arguments_builder`](#_arguments_builder)
    - [`_info_plist_writer`](#_info_plist_writer)
    - [`main`](#main)
- [`launchers/mac_app_mover.py`](#launchersmac_app_moverpy)
    - [`_app_opener`](#_app_opener)
    - [`_command_text_maker`](#_command_text_maker)
    - [`_desktop_link_mover`](#_desktop_link_mover)
    - [`_git_runner`](#_git_runner)
    - [`_installer_runner`](#_installer_runner)
    - [`_link_into_checker`](#_link_into_checker)
    - [`_log_opener`](#_log_opener)
    - [`_macos_too_old_checker`](#_macos_too_old_checker)
    - [`_macos_version_reader`](#_macos_version_reader)
    - [`_note_shower`](#_note_shower)
    - [`_our_command_checker`](#_our_command_checker)
    - [`_program_file_lister`](#_program_file_lister)
    - [`_program_file_remover`](#_program_file_remover)
    - [`_reason_shortener`](#_reason_shortener)
    - [`_tree_remover`](#_tree_remover)
    - [`_user_things_copier`](#_user_things_copier)
    - [`app_mover`](#app_mover)
    - [`desktop_file_maker`](#desktop_file_maker)
    - [`move_blocker_finder`](#move_blocker_finder)
- [`launchers/mac_app_starter.py`](#launchersmac_app_starterpy)
    - [`_problem_logger`](#_problem_logger)
    - [`main`](#main)
- [`launchers/make_icons.py`](#launchersmake_iconspy)
    - [`main`](#main)
- [`main.py`](#mainpy)
    - [`comparison_maker`](#comparison_maker)
    - [`everything_asker`](#everything_asker)
    - [`experiment_processor`](#experiment_processor)
    - [`last_answers_loader`](#last_answers_loader)
    - [`last_answers_saver`](#last_answers_saver)
    - [`main`](#main)
    - [`program_runner`](#program_runner)
    - [`special_figures_maker`](#special_figures_maker)
- [`tests/conftest.py`](#testsconftestpy)
    - [`HiddenPopen`](#hiddenpopen)
    - [`_window_refuser`](#_window_refuser)
    - [`pytest_configure`](#pytest_configure)
- [`tests/test_app_updater.py`](#teststest_app_updaterpy)
    - [`_app_maker`](#_app_maker)
    - [`_closed_pid_giver`](#_closed_pid_giver)
    - [`_release_writer`](#_release_writer)
    - [`_swap_folder_maker`](#_swap_folder_maker)
    - [`test_app_only_waits_for_a_newer_release`](#test_app_only_waits_for_a_newer_release)
    - [`test_ask_problem_is_described`](#test_ask_problem_is_described)
    - [`test_failed_swap_keeps_the_app`](#test_failed_swap_keeps_the_app)
    - [`test_newer_release_is_found`](#test_newer_release_is_found)
    - [`test_refused_ask_uses_the_release_page`](#test_refused_ask_uses_the_release_page)
    - [`test_release_answer_is_read`](#test_release_answer_is_read)
    - [`test_release_page_address_is_read`](#test_release_page_address_is_read)
    - [`test_swap_puts_the_new_app_in_place`](#test_swap_puts_the_new_app_in_place)
    - [`test_swap_waits_for_the_app_to_close`](#test_swap_waits_for_the_app_to_close)
    - [`test_temporary_copy_cannot_update`](#test_temporary_copy_cannot_update)
    - [`test_unanswered_ask_is_asked_again`](#test_unanswered_ask_is_asked_again)
    - [`test_update_from_made_up_zip`](#test_update_from_made_up_zip)
- [`tests/test_averaging_windows.py`](#teststest_averaging_windowspy)
    - [`_response_experiment_builder`](#_response_experiment_builder)
    - [`test_a_figure_asks_which_windows_only_with_both_kinds`](#test_a_figure_asks_which_windows_only_with_both_kinds)
    - [`test_a_figure_without_windows_offers_the_window_step`](#test_a_figure_without_windows_offers_the_window_step)
    - [`test_a_window_can_be_switched_off_and_set`](#test_a_window_can_be_switched_off_and_set)
    - [`test_a_pulled_end_gives_the_gap`](#test_a_pulled_end_gives_the_gap)
    - [`test_a_pulled_quick_window_gives_its_start_and_length`](#test_a_pulled_quick_window_gives_its_start_and_length)
    - [`test_a_pulled_start_gives_the_length`](#test_a_pulled_start_gives_the_length)
    - [`test_the_plot_shows_the_windows`](#test_the_plot_shows_the_windows)
    - [`test_the_quick_windows_fall_after_the_additions`](#test_the_quick_windows_fall_after_the_additions)
    - [`test_both_kinds_are_averaged_from_one_baseline`](#test_both_kinds_are_averaged_from_one_baseline)
    - [`test_the_windows_fall_before_the_additions`](#test_the_windows_fall_before_the_additions)
- [`tests/test_dataset_settings.py`](#teststest_dataset_settingspy)
    - [`_program_folder_maker`](#_program_folder_maker)
    - [`test_broken_settings_file_gives_nothing`](#test_broken_settings_file_gives_nothing)
    - [`test_data_folders_are_listed`](#test_data_folders_are_listed)
    - [`test_folder_answer_is_resolved`](#test_folder_answer_is_resolved)
    - [`test_missing_settings_file_gives_nothing`](#test_missing_settings_file_gives_nothing)
    - [`test_od_values_and_labels_are_kept`](#test_od_values_and_labels_are_kept)
    - [`test_results_folder_inside_is_kept_relative`](#test_results_folder_inside_is_kept_relative)
    - [`test_results_folder_is_checked`](#test_results_folder_is_checked)
    - [`test_results_folder_names_and_old_results`](#test_results_folder_names_and_old_results)
    - [`test_results_folder_outside_is_kept_whole`](#test_results_folder_outside_is_kept_whole)
    - [`test_regions_are_kept_with_the_dataset`](#test_regions_are_kept_with_the_dataset)
    - [`test_saved_haem_amounts_open_as_delta_d`](#test_saved_haem_amounts_open_as_delta_d)
    - [`test_settings_are_read_back`](#test_settings_are_read_back)
    - [`test_unwritable_folder_is_reported`](#test_unwritable_folder_is_reported)
- [`tests/test_delta_psi.py`](#teststest_delta_psipy)
    - [`_calculator`](#_calculator)
    - [`test_delta_psi_is_empty_outside_the_limits`](#test_delta_psi_is_empty_outside_the_limits)
    - [`test_equal_haems_at_their_midpoints_give_120_mV`](#test_equal_haems_at_their_midpoints_give_120_mv)
    - [`test_numbers_that_cannot_be_used_are_refused`](#test_numbers_that_cannot_be_used_are_refused)
    - [`test_the_b_haems_are_found_by_name`](#test_the_b_haems_are_found_by_name)
    - [`test_the_numbers_the_program_starts_with`](#test_the_numbers_the_program_starts_with)
    - [`test_the_kept_delta_psi_is_drawn_dashed`](#test_the_kept_delta_psi_is_drawn_dashed)
    - [`test_the_kept_regions_and_numbers_work_the_file_out`](#test_the_kept_regions_and_numbers_work_the_file_out)
    - [`test_the_panel_is_drawn_only_for_a_file_with_delta_psi`](#test_the_panel_is_drawn_only_for_a_file_with_delta_psi)
    - [`test_the_processing_keeps_delta_psi_when_switched_on`](#test_the_processing_keeps_delta_psi_when_switched_on)
    - [`test_the_question_is_asked_only_when_delta_psi_can_be_worked_out`](#test_the_question_is_asked_only_when_delta_psi_can_be_worked_out)
    - [`test_unequal_haems_give_173_mV`](#test_unequal_haems_give_173_mv)
- [`tests/test_file_names.py`](#teststest_file_namespy)
    - [`test_dots_and_spaces_at_the_ends_go`](#test_dots_and_spaces_at_the_ends_go)
    - [`test_forbidden_characters_become_underscores`](#test_forbidden_characters_become_underscores)
    - [`test_nothing_left_gives_the_default`](#test_nothing_left_gives_the_default)
- [`tests/test_haem_decomposition.py`](#teststest_haem_decompositionpy)
    - [`_background_builder`](#_background_builder)
    - [`_background_shape_builder`](#_background_shape_builder)
    - [`_file_values_reader`](#_file_values_reader)
    - [`_haem_spectrum_builder`](#_haem_spectrum_builder)
    - [`_mixed_spectra_builder`](#_mixed_spectra_builder)
    - [`_series_decomposer`](#_series_decomposer)
    - [`test_blank_rows_do_not_change_the_shapes`](#test_blank_rows_do_not_change_the_shapes)
    - [`test_leftover_rows_are_left_out`](#test_leftover_rows_are_left_out)
    - [`test_downward_wavelengths_are_turned_round`](#test_downward_wavelengths_are_turned_round)
    - [`test_unusable_fit_files_are_refused`](#test_unusable_fit_files_are_refused)
    - [`test_a_million_times_larger_fit_gives_the_same_amounts`](#test_a_million_times_larger_fit_gives_the_same_amounts)
    - [`test_every_fit_file_is_read`](#test_every_fit_file_is_read)
    - [`test_haem_names_go_to_figure_form_and_back`](#test_haem_names_go_to_figure_form_and_back)
    - [`test_a_fit_file_reads_back_the_same_in_each_unit`](#test_a_fit_file_reads_back_the_same_in_each_unit)
    - [`test_reduced_minus_oxidised_is_turned_over`](#test_reduced_minus_oxidised_is_turned_over)
    - [`test_a_single_haem_file_reads_back_the_same`](#test_a_single_haem_file_reads_back_the_same)
    - [`test_wrong_headed_fit_files_are_refused`](#test_wrong_headed_fit_files_are_refused)
    - [`test_saved_components_read_back_the_same`](#test_saved_components_read_back_the_same)
    - [`test_one_spectrum_gives_its_amounts_back`](#test_one_spectrum_gives_its_amounts_back)
    - [`test_a_series_gives_its_amounts_back`](#test_a_series_gives_its_amounts_back)
    - [`test_the_three_routes_give_the_same_amounts`](#test_the_three_routes_give_the_same_amounts)
    - [`test_same_shapes_give_a_plain_error`](#test_same_shapes_give_a_plain_error)
    - [`test_a_failed_decomposition_leaves_nothing`](#test_a_failed_decomposition_leaves_nothing)
    - [`test_delta_d_zero_is_where_the_haem_starts`](#test_delta_d_zero_is_where_the_haem_starts)
    - [`test_the_gap_between_two_decompositions`](#test_the_gap_between_two_decompositions)
    - [`test_each_background_gives_back_the_amounts`](#test_each_background_gives_back_the_amounts)
    - [`test_an_unknown_background_is_refused`](#test_an_unknown_background_is_refused)
    - [`test_the_background_answered_is_the_one_used`](#test_the_background_answered_is_the_one_used)
    - [`test_rowan_scatter_is_the_chamber_scripts_background`](#test_rowan_scatter_is_the_chamber_scripts_background)
    - [`test_some_haems_only_give_back_their_amounts`](#test_some_haems_only_give_back_their_amounts)
    - [`test_the_change_from_the_first_spectrum`](#test_the_change_from_the_first_spectrum)
    - [`test_two_mixed_shapes_give_two_components`](#test_two_mixed_shapes_give_two_components)
    - [`test_component_names_must_differ`](#test_component_names_must_differ)
    - [`test_the_two_shapes_are_found_again`](#test_the_two_shapes_are_found_again)
- [`tests/test_haem_direction.py`](#teststest_haem_directionpy)
    - [`_instrument_fit_reader`](#_instrument_fit_reader)
    - [`_haem_trace_loader`](#_haem_trace_loader)
    - [`test_haem_amounts_move_with_the_instrument`](#test_haem_amounts_move_with_the_instrument)
    - [`test_haem_amounts_fall_when_reduced`](#test_haem_amounts_fall_when_reduced)
    - [`test_haem_shapes_are_those_of_the_instrument`](#test_haem_shapes_are_those_of_the_instrument)
    - [`test_valencia_background_is_the_instruments`](#test_valencia_background_is_the_instruments)
    - [`test_instrument_traces_fall_when_reduced`](#test_instrument_traces_fall_when_reduced)
- [`tests/test_haem_library.py`](#teststest_haem_librarypy)
    - [`_dip_finder`](#_dip_finder)
    - [`_haem_file_writer`](#_haem_file_writer)
    - [`_preset_writer`](#_preset_writer)
    - [`_library_maker`](#_library_maker)
    - [`test_preset_joins_its_haems_in_order`](#test_preset_joins_its_haems_in_order)
    - [`test_preset_problems_are_refused`](#test_preset_problems_are_refused)
    - [`test_root_file_with_a_preset_name_is_not_offered`](#test_root_file_with_a_preset_name_is_not_offered)
    - [`test_standard_preset_keeps_its_haems`](#test_standard_preset_keeps_its_haems)
    - [`test_own_haems_are_built_from_the_library`](#test_own_haems_are_built_from_the_library)
- [`tests/test_haem_types.py`](#teststest_haem_typespy)
    - [`test_a_fit_file_is_read_in_that_order`](#test_a_fit_file_is_read_in_that_order)
    - [`test_haems_are_ordered_a_then_b_then_c`](#test_haems_are_ordered_a_then_b_then_c)
    - [`test_haem_types_come_from_the_name`](#test_haem_types_come_from_the_name)
    - [`test_haems_are_coloured_by_type`](#test_haems_are_coloured_by_type)
- [`tests/test_import_export.py`](#teststest_import_exportpy)
    - [`_experiment_maker`](#_experiment_maker)
    - [`_metadata_reader`](#_metadata_reader)
    - [`_session_maker`](#_session_maker)
    - [`test_size_in_words`](#test_size_in_words)
    - [`test_spectra_size_by_hand`](#test_spectra_size_by_hand)
    - [`test_trimmed_and_whole_go_to_their_folders`](#test_trimmed_and_whole_go_to_their_folders)
    - [`test_new_edges_export_again`](#test_new_edges_export_again)
- [`tests/test_label_tidier.py`](#teststest_label_tidierpy)
    - [`test_exponent_after_a_caret_is_raised`](#test_exponent_after_a_caret_is_raised)
    - [`test_exponent_after_a_unit_is_raised`](#test_exponent_after_a_unit_is_raised)
    - [`test_micro_is_written_with_its_sign`](#test_micro_is_written_with_its_sign)
    - [`test_names_and_formulas_are_left_alone`](#test_names_and_formulas_are_left_alone)
    - [`test_number_and_unit_get_a_space`](#test_number_and_unit_get_a_space)
    - [`test_symbols_can_be_drawn_in_the_figures`](#test_symbols_can_be_drawn_in_the_figures)
    - [`test_tidy_label_stays_as_it_is`](#test_tidy_label_stays_as_it_is)
- [`tests/test_launcher.py`](#teststest_launcherpy)
    - [`_git_stand_in_maker`](#_git_stand_in_maker)
    - [`_launcher_loader`](#_launcher_loader)
    - [`_stand_in_maker`](#_stand_in_maker)
    - [`test_changed_package_list_is_installed`](#test_changed_package_list_is_installed)
    - [`test_failed_install_stops_with_a_plain_message`](#test_failed_install_stops_with_a_plain_message)
    - [`test_failed_update_keeps_working_packages`](#test_failed_update_keeps_working_packages)
    - [`test_package_fingerprint_ignores_line_endings`](#test_package_fingerprint_ignores_line_endings)
    - [`test_update_note_reaches_portimao`](#test_update_note_reaches_portimao)
    - [`test_update_reasons_are_given`](#test_update_reasons_are_given)
    - [`test_update_reasons_without_git`](#test_update_reasons_without_git)
- [`tests/test_mac_app_builder.py`](#teststest_mac_app_builderpy)
    - [`_plist_maker`](#_plist_maker)
    - [`test_app_carries_program_files`](#test_app_carries_program_files)
    - [`test_plist_gets_version_and_keeps_keys`](#test_plist_gets_version_and_keeps_keys)
    - [`test_plist_refuses_unknown_version`](#test_plist_refuses_unknown_version)
- [`tests/test_mac_app_mover.py`](#teststest_mac_app_moverpy)
    - [`_git_runner`](#_git_runner)
    - [`_installer_faker`](#_installer_faker)
    - [`_link_tester`](#_link_tester)
    - [`_old_install_maker`](#_old_install_maker)
    - [`test_desktop_file_is_made_once`](#test_desktop_file_is_made_once)
    - [`test_desktop_file_replaces_the_old_link`](#test_desktop_file_replaces_the_old_link)
    - [`test_developer_copy_is_not_moved`](#test_developer_copy_is_not_moved)
    - [`test_failed_install_takes_nothing_away`](#test_failed_install_takes_nothing_away)
    - [`test_folder_elsewhere_gets_its_fits_copied`](#test_folder_elsewhere_gets_its_fits_copied)
    - [`test_move_keeps_the_desktop_link_working`](#test_move_keeps_the_desktop_link_working)
    - [`test_move_takes_away_only_program_files`](#test_move_takes_away_only_program_files)
    - [`test_old_macos_is_not_moved`](#test_old_macos_is_not_moved)
- [`tests/test_mac_install.py`](#teststest_mac_installpy)
    - [`_install_runner`](#_install_runner)
    - [`_old_app_maker`](#_old_app_maker)
    - [`test_download_failure_keeps_the_old_app`](#test_download_failure_keeps_the_old_app)
    - [`test_intel_mac_gets_the_intel_zip`](#test_intel_mac_gets_the_intel_zip)
    - [`test_line_installs_and_opens_the_app`](#test_line_installs_and_opens_the_app)
    - [`test_no_open_replaces_the_old_app`](#test_no_open_replaces_the_old_app)
    - [`test_not_a_mac_is_refused`](#test_not_a_mac_is_refused)
    - [`test_old_macos_is_refused`](#test_old_macos_is_refused)
    - [`test_open_app_is_refused`](#test_open_app_is_refused)
- [`tests/test_mac_report.py`](#teststest_mac_reportpy)
    - [`_app_maker`](#_app_maker)
    - [`_folder_maker`](#_folder_maker)
    - [`_report_runner`](#_report_runner)
    - [`_snapshot_taker`](#_snapshot_taker)
    - [`test_report_in_downloads_names_it`](#test_report_in_downloads_names_it)
    - [`test_report_in_home_folder_is_not_guarded`](#test_report_in_home_folder_is_not_guarded)
    - [`test_report_inside_app_describes_it`](#test_report_inside_app_describes_it)
- [`tests/test_no_windows.py`](#teststest_no_windowspy)
    - [`test_no_tk_window_can_open`](#test_no_tk_window_can_open)
    - [`test_plots_are_drawn_off_screen`](#test_plots_are_drawn_off_screen)
    - [`test_started_programs_have_no_console_window`](#test_started_programs_have_no_console_window)
- [`tests/test_ocr_checking.py`](#teststest_ocr_checkingpy)
    - [`_instrument_maker`](#_instrument_maker)
    - [`test_steady_fall_is_its_slope`](#test_steady_fall_is_its_slope)
    - [`test_curved_fall_needs_29_points`](#test_curved_fall_needs_29_points)
    - [`test_leak_is_permeability_times_gap`](#test_leak_is_permeability_times_gap)
    - [`test_leak_window_is_40_points`](#test_leak_window_is_40_points)
    - [`test_agreeing_traces_pass`](#test_agreeing_traces_pass)
    - [`test_wrong_sum_is_caught`](#test_wrong_sum_is_caught)
    - [`test_wrong_leak_is_caught`](#test_wrong_leak_is_caught)
    - [`test_addition_stretch_is_left_out`](#test_addition_stretch_is_left_out)
    - [`test_missing_trace_is_not_checked`](#test_missing_trace_is_not_checked)
    - [`test_short_recording_is_not_checked`](#test_short_recording_is_not_checked)
- [`tests/test_paf_reader_parts.py`](#teststest_paf_reader_partspy)
    - [`test_additions_copies_are_joined`](#test_additions_copies_are_joined)
    - [`test_additions_under_one_name_are_all_kept`](#test_additions_under_one_name_are_all_kept)
    - [`test_addition_without_position_is_left_out`](#test_addition_without_position_is_left_out)
    - [`test_spectrum_times_with_equal_counts`](#test_spectrum_times_with_equal_counts)
    - [`test_spectrum_times_with_fewer_spectra`](#test_spectrum_times_with_fewer_spectra)
    - [`test_spectrum_times_with_more_spectra`](#test_spectrum_times_with_more_spectra)
    - [`test_transmission_from_the_stored_logarithms`](#test_transmission_from_the_stored_logarithms)
    - [`test_transmission_is_empty_without_reference_counts`](#test_transmission_is_empty_without_reference_counts)
    - [`test_trace_titles_follow_the_unit_of_the_file`](#test_trace_titles_follow_the_unit_of_the_file)
    - [`test_addition_outside_the_recording_is_left_out`](#test_addition_outside_the_recording_is_left_out)
    - [`test_missing_concentration_is_written_by_the_helper`](#test_missing_concentration_is_written_by_the_helper)
    - [`test_rate_trace_short_by_its_usual_gap_is_not_reported`](#test_rate_trace_short_by_its_usual_gap_is_not_reported)
    - [`test_trace_with_disagreeing_lengths_is_noted`](#test_trace_with_disagreeing_lengths_is_noted)
    - [`test_unreadable_files_give_plain_messages`](#test_unreadable_files_give_plain_messages)
- [`tests/test_paf_reading.py`](#teststest_paf_readingpy)
    - [`_dataset_loader`](#_dataset_loader)
    - [`_export_reader`](#_export_reader)
    - [`_trace_export_reader`](#_trace_export_reader)
    - [`_trace_loader`](#_trace_loader)
    - [`test_known_file_counts`](#test_known_file_counts)
    - [`test_spectra_counts_match_the_instrument`](#test_spectra_counts_match_the_instrument)
    - [`test_transmission_matches_the_instrument`](#test_transmission_matches_the_instrument)
    - [`test_intensity_matches_the_instrument`](#test_intensity_matches_the_instrument)
    - [`test_attenuation_size_matches_the_instrument`](#test_attenuation_size_matches_the_instrument)
    - [`test_attenuation_sign_matches_the_instrument`](#test_attenuation_sign_matches_the_instrument)
    - [`test_spectra_parts_agree`](#test_spectra_parts_agree)
    - [`test_times_and_wavelengths_run_in_order`](#test_times_and_wavelengths_run_in_order)
    - [`test_traces_match_the_instrument`](#test_traces_match_the_instrument)
    - [`test_loaded_traces_match_the_instrument`](#test_loaded_traces_match_the_instrument)
    - [`test_ocr_settings_fit_the_rate_traces`](#test_ocr_settings_fit_the_rate_traces)
    - [`test_example_ocr_agrees`](#test_example_ocr_agrees)
    - [`test_our_ocr_stays_fixed`](#test_our_ocr_stays_fixed)
- [`tests/test_processing_maths.py`](#teststest_processing_mathspy)
    - [`_plateau_experiment_builder`](#_plateau_experiment_builder)
    - [`_ramp_experiment_builder`](#_ramp_experiment_builder)
    - [`test_attenuation_from_known_ratios`](#test_attenuation_from_known_ratios)
    - [`test_attenuation_of_impossible_values`](#test_attenuation_of_impossible_values)
    - [`test_attenuation_added_to_an_experiment`](#test_attenuation_added_to_an_experiment)
    - [`test_blank_warning_counts_the_fitted_range`](#test_blank_warning_counts_the_fitted_range)
    - [`test_normalising_by_od_volume_and_dilution`](#test_normalising_by_od_volume_and_dilution)
    - [`test_unreadable_numbers_stop_both_scalings`](#test_unreadable_numbers_stop_both_scalings)
    - [`test_percent_of_a_trace_with_plateaus`](#test_percent_of_a_trace_with_plateaus)
    - [`test_percent_of_a_flat_trace`](#test_percent_of_a_flat_trace)
    - [`test_reference_level_from_points_in_a_row`](#test_reference_level_from_points_in_a_row)
    - [`test_window_mean_and_spread`](#test_window_mean_and_spread)
    - [`test_averages_around_the_additions`](#test_averages_around_the_additions)
    - [`test_a_file_with_both_regions_gets_percent_oxidised`](#test_a_file_with_both_regions_gets_percent_oxidised)
    - [`test_average_that_does_not_fit`](#test_average_that_does_not_fit)
    - [`test_baseline_needs_ten_seconds_of_data`](#test_baseline_needs_ten_seconds_of_data)
    - [`test_trimming_keeps_exactly_the_chosen_times`](#test_trimming_keeps_exactly_the_chosen_times)
    - [`test_trimming_moves_the_ignored_additions`](#test_trimming_moves_the_ignored_additions)
    - [`test_trimming_never_cuts_an_addition`](#test_trimming_never_cuts_an_addition)
    - [`test_trimming_the_end_only`](#test_trimming_the_end_only)
- [`tests/test_program_version.py`](#teststest_program_versionpy)
    - [`test_update_note_beside_the_version`](#test_update_note_beside_the_version)
    - [`test_version_from_style_folder`](#test_version_from_style_folder)
    - [`test_version_from_question_flow`](#test_version_from_question_flow)
    - [`test_version_unknown_without_either_file`](#test_version_unknown_without_either_file)
- [`tests/test_question_flow.py`](#teststest_question_flowpy)
    - [`_binding_resolver`](#_binding_resolver)
    - [`_carrier_finder`](#_carrier_finder)
    - [`_list_reader`](#_list_reader)
    - [`_number_matcher`](#_number_matcher)
    - [`_question_collector`](#_question_collector)
    - [`_question_matcher`](#_question_matcher)
    - [`_text_resolver`](#_text_resolver)
    - [`_tree_reader`](#_tree_reader)
    - [`test_question_texts_can_be_read`](#test_question_texts_can_be_read)
    - [`test_questions_are_in_the_list`](#test_questions_are_in_the_list)
    - [`test_question_numbers_match_the_list`](#test_question_numbers_match_the_list)
- [`tests/test_question_format.py`](#teststest_question_formatpy)
    - [`_lines_reader`](#_lines_reader)
    - [`_typist_setter`](#_typist_setter)
    - [`test_accept_question_shapes`](#test_accept_question_shapes)
    - [`test_choice_endings`](#test_choice_endings)
    - [`test_given_number_is_shown`](#test_given_number_is_shown)
    - [`test_number_endings_and_hints`](#test_number_endings_and_hints)
    - [`test_several_numbers`](#test_several_numbers)
    - [`test_table_instruction_waits`](#test_table_instruction_waits)
    - [`test_text_question_waits`](#test_text_question_waits)
    - [`test_typed_number_reader`](#test_typed_number_reader)
    - [`test_yes_no_endings`](#test_yes_no_endings)
- [`tests/test_redox_regions.py`](#teststest_redox_regionspy)
    - [`test_a_level_is_the_median_in_the_region`](#test_a_level_is_the_median_in_the_region)
    - [`test_a_file_needs_both_regions_for_its_levels`](#test_a_file_needs_both_regions_for_its_levels)
    - [`test_an_edge_is_copied_by_its_nearest_addition`](#test_an_edge_is_copied_by_its_nearest_addition)
    - [`test_percent_oxidised_runs_between_the_two_levels`](#test_percent_oxidised_runs_between_the_two_levels)
    - [`test_the_least_spectra_of_the_program`](#test_the_least_spectra_of_the_program)
- [`tests/test_region_edges.py`](#teststest_region_edgespy)
    - [`_edge_setter`](#_edge_setter)
    - [`test_copy_to_every_file_or_one_file`](#test_copy_to_every_file_or_one_file)
    - [`test_edge_copied_by_its_nearest_addition`](#test_edge_copied_by_its_nearest_addition)
    - [`test_edges_stay_in_the_used_part`](#test_edges_stay_in_the_used_part)
    - [`test_layout_of_the_regions`](#test_layout_of_the_regions)
    - [`test_pointer_gives_the_time_in_steps`](#test_pointer_gives_the_time_in_steps)
    - [`test_regions_a_file_ends_with`](#test_regions_a_file_ends_with)
    - [`test_regions_never_overlap`](#test_regions_never_overlap)
    - [`test_shaded_regions`](#test_shaded_regions)
    - [`test_starting_edges`](#test_starting_edges)
- [`tests/test_run_logging.py`](#teststest_run_loggingpy)
    - [`_typist_maker`](#_typist_maker)
    - [`_fresh_numbering`](#_fresh_numbering)
    - [`test_answers_are_logged_as_they_come`](#test_answers_are_logged_as_they_come)
    - [`test_closed_window_keeps_the_log`](#test_closed_window_keeps_the_log)
    - [`test_launch_log_keeps_the_starts_before`](#test_launch_log_keeps_the_starts_before)
    - [`test_launch_log_is_cut_past_its_limit`](#test_launch_log_is_cut_past_its_limit)
- [`tests/test_summary_maths.py`](#teststest_summary_mathspy)
    - [`_run_builder`](#_run_builder)
    - [`_spectra_experiment_builder`](#_spectra_experiment_builder)
    - [`test_averaged_spectra_around_the_additions`](#test_averaged_spectra_around_the_additions)
    - [`test_baseline_starts_with_the_recording`](#test_baseline_starts_with_the_recording)
    - [`test_difference_of_two_known_spectra`](#test_difference_of_two_known_spectra)
    - [`test_difference_needs_its_averages`](#test_difference_needs_its_averages)
    - [`test_average_over_three_runs`](#test_average_over_three_runs)
    - [`test_average_needs_two_runs`](#test_average_needs_two_runs)
- [`tests/test_time_pointer.py`](#teststest_time_pointerpy)
    - [`test_pointed_time_inside_the_panels`](#test_pointed_time_inside_the_panels)
    - [`test_pointed_time_off_the_panels`](#test_pointed_time_off_the_panels)
    - [`test_pointed_time_on_a_scaled_picture`](#test_pointed_time_on_a_scaled_picture)
    - [`test_question_wanting_a_time_tells_the_window`](#test_question_wanting_a_time_tells_the_window)
    - [`test_time_axis_of_a_figure`](#test_time_axis_of_a_figure)
- [`tests/test_trim_edges.py`](#teststest_trim_edgespy)
    - [`test_edge_under_the_mouse`](#test_edge_under_the_mouse)
    - [`test_every_file_or_one_file`](#test_every_file_or_one_file)
    - [`test_ignored_parts_stay_inside_the_kept_part`](#test_ignored_parts_stay_inside_the_kept_part)
    - [`test_layout_of_the_edges_and_parts`](#test_layout_of_the_edges_and_parts)
    - [`test_minutes_and_places_on_the_plot`](#test_minutes_and_places_on_the_plot)
    - [`test_minutes_typed_in_the_strip`](#test_minutes_typed_in_the_strip)
    - [`test_minutes_to_limits_and_back`](#test_minutes_to_limits_and_back)
    - [`test_pointer_gives_the_minutes_of_each_edge`](#test_pointer_gives_the_minutes_of_each_edge)
    - [`test_shaded_picture`](#test_shaded_picture)
    - [`test_trimmed_edges_stop_at_the_events`](#test_trimmed_edges_stop_at_the_events)
- [`tests/test_user_notices.py`](#teststest_user_noticespy)
    - [`_caught_getter`](#_caught_getter)
    - [`_quiet_details`](#_quiet_details)
    - [`test_details_go_to_the_log_only`](#test_details_go_to_the_log_only)
    - [`test_own_message_is_shown_as_it_is`](#test_own_message_is_shown_as_it_is)
    - [`test_python_text_is_never_shown`](#test_python_text_is_never_shown)
    - [`test_file_problems_say_what_to_do`](#test_file_problems_say_what_to_do)
    - [`test_run_log_takes_the_details`](#test_run_log_takes_the_details)
    - [`test_warnings_are_kept_whatever_their_words`](#test_warnings_are_kept_whatever_their_words)
- [`tests/test_user_places.py`](#teststest_user_placespy)
    - [`_app_places_maker`](#_app_places_maker)
    - [`test_app_keeps_things_in_home_folder`](#test_app_keeps_things_in_home_folder)
    - [`test_app_never_overwrites_a_fit`](#test_app_never_overwrites_a_fit)
    - [`test_source_keeps_things_in_program_folder`](#test_source_keeps_things_in_program_folder)
    - [`test_source_program_folder_is_found`](#test_source_program_folder_is_found)
- [`tests/test_window_parts.py`](#teststest_window_partspy)
    - [`test_cells_of_the_tables`](#test_cells_of_the_tables)
    - [`test_event_labels_from_the_table`](#test_event_labels_from_the_table)
    - [`test_rows_of_the_labels_table`](#test_rows_of_the_labels_table)
    - [`test_rows_of_the_od_table`](#test_rows_of_the_od_table)
    - [`test_sentence_when_confirmed_too_early`](#test_sentence_when_confirmed_too_early)
    - [`test_height_typed_in_the_strip`](#test_height_typed_in_the_strip)
    - [`test_the_decomposition_kept_to_compare`](#test_the_decomposition_kept_to_compare)
    - [`test_keep_to_compare_keeps_the_regions_in_use`](#test_keep_to_compare_keeps_the_regions_in_use)
    - [`test_go_back_to_kept_puts_the_kept_one_back`](#test_go_back_to_kept_puts_the_kept_one_back)
    - [`test_answers_shown_in_the_strip`](#test_answers_shown_in_the_strip)
    - [`test_values_meant_for_the_strip`](#test_values_meant_for_the_strip)
    - [`test_numbers_of_the_delta_psi_row`](#test_numbers_of_the_delta_psi_row)
    - [`test_haems_and_ocr_shown_from_the_strip`](#test_haems_and_ocr_shown_from_the_strip)
    - [`test_plots_follow_the_strip`](#test_plots_follow_the_strip)
    - [`test_haems_ticked_in_the_strip`](#test_haems_ticked_in_the_strip)
    - [`test_widths_of_each_journal`](#test_widths_of_each_journal)
    - [`test_time_title_of_a_preview`](#test_time_title_of_a_preview)
    - [`test_files_drawn_beside_the_one_shown`](#test_files_drawn_beside_the_one_shown)
    - [`test_files_kept_in_memory`](#test_files_kept_in_memory)
    - [`test_wheel_turn_on_each_system`](#test_wheel_turn_on_each_system)
- [`utils_custom/custom_config.py`](#utils_customcustom_configpy)
    - [`exemplar_config_builder`](#exemplar_config_builder)
    - [`haem_labeller`](#haem_labeller)
    - [`individual_config_builder`](#individual_config_builder)
    - [`ocr_and_haem_response_config_builder`](#ocr_and_haem_response_config_builder)
    - [`source_selector`](#source_selector)
    - [`time_response_config_builder`](#time_response_config_builder)
- [`utils_custom/custom_figure_saver.py`](#utils_customcustom_figure_saverpy)
    - [`custom_figure_saver`](#custom_figure_saver)
- [`utils_custom/custom_questions.py`](#utils_customcustom_questionspy)
    - [`_example_pair_maker`](#_example_pair_maker)
    - [`_haem_ocr_asker`](#_haem_ocr_asker)
    - [`_hours_reader`](#_hours_reader)
    - [`_panel_chooser`](#_panel_chooser)
    - [`_saved_example_finder`](#_saved_example_finder)
    - [`_step_checker`](#_step_checker)
    - [`_step_wirer`](#_step_wirer)
    - [`_time_response_asker`](#_time_response_asker)
    - [`summary_figure_asker`](#summary_figure_asker)
- [`utils_custom/custom_runner.py`](#utils_customcustom_runnerpy)
    - [`_ocr_and_haem_response_preparer`](#_ocr_and_haem_response_preparer)
    - [`_time_response_preparer`](#_time_response_preparer)
    - [`exemplar_runner`](#exemplar_runner)
    - [`experiment_preparer`](#experiment_preparer)
    - [`ocr_and_haem_response_runner`](#ocr_and_haem_response_runner)
    - [`time_response_runner`](#time_response_runner)
- [`utils_custom/exemplar_plotter.py`](#utils_customexemplar_plotterpy)
    - [`_crop_start_finder`](#_crop_start_finder)
    - [`_exemplar_gap_calculator`](#_exemplar_gap_calculator)
    - [`_exemplar_plotter`](#_exemplar_plotter)
    - [`_exemplar_selector`](#_exemplar_selector)
    - [`_experiment_cropper`](#_experiment_cropper)
    - [`exemplar_figure_plotter`](#exemplar_figure_plotter)
- [`utils_custom/ocr_and_haem_response_exporter.py`](#utils_customocr_and_haem_response_exporterpy)
    - [`_baseline_sheet_writer`](#_baseline_sheet_writer)
    - [`_condition_sheet_writer`](#_condition_sheet_writer)
    - [`_measurement_table_writer`](#_measurement_table_writer)
    - [`_statistics_writer`](#_statistics_writer)
    - [`_test_row_writer`](#_test_row_writer)
    - [`_tests_sheet_writer`](#_tests_sheet_writer)
    - [`ocr_and_haem_response_exporter`](#ocr_and_haem_response_exporter)
- [`utils_custom/ocr_and_haem_response_plotter.py`](#utils_customocr_and_haem_response_plotterpy)
    - [`_axes_styler`](#_axes_styler)
    - [`_baseline_bar_plotter`](#_baseline_bar_plotter)
    - [`_block_gap_calculator`](#_block_gap_calculator)
    - [`_column_chooser`](#_column_chooser)
    - [`_condition_indexer`](#_condition_indexer)
    - [`_finite_run_filter`](#_finite_run_filter)
    - [`_haem_block_plotter`](#_haem_block_plotter)
    - [`_haem_label_finder`](#_haem_label_finder)
    - [`_haem_label_pad_calculator`](#_haem_label_pad_calculator)
    - [`_haem_row_selector`](#_haem_row_selector)
    - [`_haem_source_finder`](#_haem_source_finder)
    - [`_layout_validator`](#_layout_validator)
    - [`_legend_handle_builder`](#_legend_handle_builder)
    - [`_mean_ylim_setter`](#_mean_ylim_setter)
    - [`_measurement_finder`](#_measurement_finder)
    - [`_metric_field_selector`](#_metric_field_selector)
    - [`_ocr_block_plotter`](#_ocr_block_plotter)
    - [`_offset_transformer`](#_offset_transformer)
    - [`_outside_bar_drawer`](#_outside_bar_drawer)
    - [`_p_value_adjuster`](#_p_value_adjuster)
    - [`_panel_labeller`](#_panel_labeller)
    - [`_reference_level_finder`](#_reference_level_finder)
    - [`_reference_selector`](#_reference_selector)
    - [`_response_axes_preparer`](#_response_axes_preparer)
    - [`_response_metric_checker`](#_response_metric_checker)
    - [`_response_series_drawer`](#_response_series_drawer)
    - [`_response_window_tester`](#_response_window_tester)
    - [`_row_ylim_sharer`](#_row_ylim_sharer)
    - [`_significance_bar_drawer`](#_significance_bar_drawer)
    - [`_significance_formatter`](#_significance_formatter)
    - [`_test_bar_drawer`](#_test_bar_drawer)
    - [`_tick_label_builder`](#_tick_label_builder)
    - [`_window_orderer`](#_window_orderer)
    - [`ocr_and_haem_response_figure_plotter`](#ocr_and_haem_response_figure_plotter)
- [`utils_custom/publication_plotter.py`](#utils_custompublication_plotterpy)
    - [`_axes_styler`](#_axes_styler)
    - [`_baseline_bar_plotter`](#_baseline_bar_plotter)
    - [`_block_gap_calculator`](#_block_gap_calculator)
    - [`_column_chooser`](#_column_chooser)
    - [`_condition_indexer`](#_condition_indexer)
    - [`_crop_start_finder`](#_crop_start_finder)
    - [`_exemplar_gap_calculator`](#_exemplar_gap_calculator)
    - [`_exemplar_plotter`](#_exemplar_plotter)
    - [`_exemplar_selector`](#_exemplar_selector)
    - [`_experiment_classifier`](#_experiment_classifier)
    - [`_experiment_cropper`](#_experiment_cropper)
    - [`_figure_finisher`](#_figure_finisher)
    - [`_haem_block_plotter`](#_haem_block_plotter)
    - [`_haem_label_finder`](#_haem_label_finder)
    - [`_haem_label_pad_calculator`](#_haem_label_pad_calculator)
    - [`_haem_row_selector`](#_haem_row_selector)
    - [`_haem_source_finder`](#_haem_source_finder)
    - [`_layout_validator`](#_layout_validator)
    - [`_legend_handle_builder`](#_legend_handle_builder)
    - [`_mean_ylim_setter`](#_mean_ylim_setter)
    - [`_measurement_finder`](#_measurement_finder)
    - [`_metric_field_selector`](#_metric_field_selector)
    - [`_ocr_block_plotter`](#_ocr_block_plotter)
    - [`_outside_bar_drawer`](#_outside_bar_drawer)
    - [`_p_value_adjuster`](#_p_value_adjuster)
    - [`_reference_level_finder`](#_reference_level_finder)
    - [`_reference_selector`](#_reference_selector)
    - [`_response_axes_preparer`](#_response_axes_preparer)
    - [`_response_metric_checker`](#_response_metric_checker)
    - [`_response_series_drawer`](#_response_series_drawer)
    - [`_response_window_tester`](#_response_window_tester)
    - [`_row_ylim_sharer`](#_row_ylim_sharer)
    - [`_significance_bar_drawer`](#_significance_bar_drawer)
    - [`_significance_formatter`](#_significance_formatter)
    - [`_test_bar_drawer`](#_test_bar_drawer)
    - [`_tick_label_builder`](#_tick_label_builder)
    - [`_window_orderer`](#_window_orderer)
    - [`exemplar_figure_plotter`](#exemplar_figure_plotter)
    - [`publication_figure_plotter`](#publication_figure_plotter)
    - [`publication_figure_saver`](#publication_figure_saver)
- [`utils_custom/run_namer.py`](#utils_customrun_namerpy)
    - [`_group_matcher`](#_group_matcher)
    - [`_natural_sorter`](#_natural_sorter)
    - [`_order_sorter`](#_order_sorter)
    - [`condition_classifier`](#condition_classifier)
    - [`condition_grouper`](#condition_grouper)
    - [`experiment_classifier`](#experiment_classifier)
    - [`group_assigner`](#group_assigner)
    - [`hours_parser`](#hours_parser)
    - [`run_name_lister`](#run_name_lister)
    - [`run_name_parser`](#run_name_parser)
- [`utils_custom/spectral_difference.py`](#utils_customspectral_differencepy)
    - [`difference_spectrum_calculator`](#difference_spectrum_calculator)
    - [`difference_spectrum_decomposer`](#difference_spectrum_decomposer)
    - [`spectral_averager`](#spectral_averager)
- [`utils_custom/time_response_exporter.py`](#utils_customtime_response_exporterpy)
    - [`_difference_sheet_writer`](#_difference_sheet_writer)
    - [`_haem_sheet_writer`](#_haem_sheet_writer)
    - [`_picks_sheet_writer`](#_picks_sheet_writer)
    - [`_waterfall_sheet_writer`](#_waterfall_sheet_writer)
    - [`time_response_exporter`](#time_response_exporter)
- [`utils_custom/time_response_plotter.py`](#utils_customtime_response_plotterpy)
    - [`_event_label_height_calculator`](#_event_label_height_calculator)
    - [`_example_finder`](#_example_finder)
    - [`_example_viewer`](#_example_viewer)
    - [`_haem_scale_sharer`](#_haem_scale_sharer)
    - [`_haem_window_drawer`](#_haem_window_drawer)
    - [`_legend_drawer`](#_legend_drawer)
    - [`_placeholder_drawer`](#_placeholder_drawer)
    - [`_time_axes_styler`](#_time_axes_styler)
    - [`_time_gap_calculator`](#_time_gap_calculator)
    - [`_title_styler`](#_title_styler)
    - [`decomposition_plotter`](#decomposition_plotter)
    - [`group_collector`](#group_collector)
    - [`shared_baseline_subtracter`](#shared_baseline_subtracter)
    - [`time_label_builder`](#time_label_builder)
    - [`time_response_figure_plotter`](#time_response_figure_plotter)
    - [`waterfall_plotter`](#waterfall_plotter)
- [`utils_custom/triplicate_averager.py`](#utils_customtriplicate_averagerpy)
    - [`_run_summariser`](#_run_summariser)
    - [`_run_value_getter`](#_run_value_getter)
    - [`_window_sorter`](#_window_sorter)
    - [`triplicate_averager`](#triplicate_averager)
- [`utils_custom/triplicate_exporter.py`](#utils_customtriplicate_exporterpy)
    - [`triplicate_exporter`](#triplicate_exporter)
- [`utils_custom/workbook_helpers.py`](#utils_customworkbook_helperspy)
    - [`formula_writer`](#formula_writer)
    - [`number_writer`](#number_writer)
    - [`workbook_formats_builder`](#workbook_formats_builder)
- [`utils_shared/app_messages.py`](#utils_sharedapp_messagespy)
    - [`_applescript_quoter`](#_applescript_quoter)
    - [`_dialog_script_maker`](#_dialog_script_maker)
    - [`_report_copier`](#_report_copier)
    - [`start_problem_shower`](#start_problem_shower)
    - [`update_notice_shower`](#update_notice_shower)
- [`utils_shared/app_updater.py`](#utils_sharedapp_updaterpy)
    - [`_app_finder`](#_app_finder)
    - [`_app_unpacker`](#_app_unpacker)
    - [`_ask_problem_describer`](#_ask_problem_describer)
    - [`_blocker_finder`](#_blocker_finder)
    - [`_leftover_cleaner`](#_leftover_cleaner)
    - [`_log_opener`](#_log_opener)
    - [`_new_app_checker`](#_new_app_checker)
    - [`_new_app_fetcher`](#_new_app_fetcher)
    - [`_newer_checker`](#_newer_checker)
    - [`_newest_release_finder`](#_newest_release_finder)
    - [`_own_version_reader`](#_own_version_reader)
    - [`_release_asker`](#_release_asker)
    - [`_release_page_asker`](#_release_page_asker)
    - [`_release_page_reader`](#_release_page_reader)
    - [`_release_reader`](#_release_reader)
    - [`_start_command_maker`](#_start_command_maker)
    - [`_status_window_maker`](#_status_window_maker)
    - [`_translation_checker`](#_translation_checker)
    - [`_version_splitter`](#_version_splitter)
    - [`_zip_downloader`](#_zip_downloader)
    - [`_zip_namer`](#_zip_namer)
    - [`swap_starter`](#swap_starter)
    - [`update_installer`](#update_installer)
- [`utils_shared/attenuation.py`](#utils_sharedattenuationpy)
    - [`attenuation_converter`](#attenuation_converter)
    - [`experiment_attenuation_adder`](#experiment_attenuation_adder)
- [`utils_shared/averaging.py`](#utils_sharedaveragingpy)
    - [`_baseline_change_adder`](#_baseline_change_adder)
    - [`experiment_averages_calculator`](#experiment_averages_calculator)
    - [`kind_span_lister`](#kind_span_lister)
    - [`quick_span_lister`](#quick_span_lister)
    - [`window_kind_picker`](#window_kind_picker)
    - [`window_layout_finder`](#window_layout_finder)
    - [`window_pointer_reader`](#window_pointer_reader)
    - [`window_span_lister`](#window_span_lister)
    - [`window_statistics_calculator`](#window_statistics_calculator)
    - [`window_value_setter`](#window_value_setter)
- [`utils_shared/comparison_plotter.py`](#utils_sharedcomparison_plotterpy)
    - [`_overhang_calculator`](#_overhang_calculator)
    - [`_renderer_getter`](#_renderer_getter)
    - [`comparison_figure_plotter`](#comparison_figure_plotter)
- [`utils_shared/dataset_settings.py`](#utils_shareddataset_settingspy)
    - [`_event_plainer`](#_event_plainer)
    - [`_export_folder_resolver`](#_export_folder_resolver)
    - [`_export_folder_shortener`](#_export_folder_shortener)
    - [`dataset_settings_reader`](#dataset_settings_reader)
    - [`dataset_settings_saver`](#dataset_settings_saver)
    - [`file_settings_merger`](#file_settings_merger)
- [`utils_shared/delta_psi.py`](#utils_shareddelta_psipy)
    - [`_settings_validator`](#_settings_validator)
    - [`b_haem_column_finder`](#b_haem_column_finder)
    - [`delta_psi_calculator`](#delta_psi_calculator)
    - [`delta_psi_table_builder`](#delta_psi_table_builder)
    - [`state_fractions_solver`](#state_fractions_solver)
    - [`thermal_voltage_finder`](#thermal_voltage_finder)
- [`utils_shared/experiment_processing.py`](#utils_sharedexperiment_processingpy)
    - [`_skip_reporter`](#_skip_reporter)
    - [`event_settings_merger`](#event_settings_merger)
    - [`experiment_data_processor`](#experiment_data_processor)
- [`utils_shared/figure_layout.py`](#utils_sharedfigure_layoutpy)
    - [`_renderer_getter`](#_renderer_getter)
    - [`figure_canvas_fitter`](#figure_canvas_fitter)
    - [`figure_finisher`](#figure_finisher)
    - [`figure_size_calculator`](#figure_size_calculator)
    - [`figure_style_builder`](#figure_style_builder)
    - [`figure_style_checker`](#figure_style_checker)
    - [`gap_space_calculator`](#gap_space_calculator)
    - [`panel_letter_adder`](#panel_letter_adder)
    - [`stack_legend_drawer`](#stack_legend_drawer)
    - [`text_extent_calculator`](#text_extent_calculator)
- [`utils_shared/helpers.py`](#utils_sharedhelperspy)
    - [`concentration_formatter`](#concentration_formatter)
    - [`excel_sheet_namer`](#excel_sheet_namer)
    - [`figure_capture_setter`](#figure_capture_setter)
    - [`figure_saver`](#figure_saver)
    - [`file_name_sanitiser`](#file_name_sanitiser)
    - [`haem_order_finder`](#haem_order_finder)
    - [`haem_type_finder`](#haem_type_finder)
    - [`name_simplifier`](#name_simplifier)
    - [`program_title_builder`](#program_title_builder)
    - [`program_version_reader`](#program_version_reader)
    - [`update_note_finder`](#update_note_finder)
- [`utils_shared/individual_experiment_exporter.py`](#utils_sharedindividual_experiment_exporterpy)
    - [`_frame_writer`](#_frame_writer)
    - [`_name_lister`](#_name_lister)
    - [`_spectral_csv_exporter`](#_spectral_csv_exporter)
    - [`averages_table_builder`](#averages_table_builder)
    - [`experiment_workbook_exporter`](#experiment_workbook_exporter)
    - [`saved_settings_reader`](#saved_settings_reader)
    - [`size_describer`](#size_describer)
    - [`spectra_size_estimator`](#spectra_size_estimator)
    - [`workbook_path_builder`](#workbook_path_builder)
- [`utils_shared/individual_experiment_plotter.py`](#utils_sharedindividual_experiment_plotterpy)
    - [`_HideTopTickLabels`](#_hidetopticklabels)
    - [`_axes_legend_drawer`](#_axes_legend_drawer)
    - [`_first_series_getter`](#_first_series_getter)
    - [`_haem_data_selector`](#_haem_data_selector)
    - [`_height_ratio_calculator`](#_height_ratio_calculator)
    - [`_min_ticks_setter`](#_min_ticks_setter)
    - [`_panel_builder`](#_panel_builder)
    - [`_vo2_ymax_calculator`](#_vo2_ymax_calculator)
    - [`_skipped_window_drawer`](#_skipped_window_drawer)
    - [`_window_drawer`](#_window_drawer)
    - [`_window_label_builder`](#_window_label_builder)
    - [`_ylim_calculator`](#_ylim_calculator)
    - [`experiment_drawer`](#experiment_drawer)
    - [`experiment_plotter`](#experiment_plotter)
    - [`experiment_title_builder`](#experiment_title_builder)
    - [`watermark_style_builder`](#watermark_style_builder)
- [`utils_shared/normalisation.py`](#utils_sharednormalisationpy)
    - [`_frame_normaliser`](#_frame_normaliser)
    - [`_number_reader`](#_number_reader)
    - [`data_normaliser`](#data_normaliser)
    - [`experiment_normaliser`](#experiment_normaliser)
    - [`percent_converter`](#percent_converter)
    - [`percent_scaler`](#percent_scaler)
- [`utils_shared/ocr_checking.py`](#utils_sharedocr_checkingpy)
    - [`_agreement_finder`](#_agreement_finder)
    - [`_leak_finder`](#_leak_finder)
    - [`_oxygen_fall_finder`](#_oxygen_fall_finder)
    - [`_pressure_factor_finder`](#_pressure_factor_finder)
    - [`ocr_calculator`](#ocr_calculator)
    - [`ocr_check_describer`](#ocr_check_describer)
    - [`ocr_checker`](#ocr_checker)
- [`utils_shared/output_capture.py`](#utils_sharedoutput_capturepy)
    - [`CapturedOutput`](#capturedoutput)
    - [`captured_buffer_getter`](#captured_buffer_getter)
    - [`output_capturer`](#output_capturer)
- [`utils_shared/paf_reader.py`](#utils_sharedpaf_readerpy)
    - [`PafError`](#paferror)
    - [`Spectra`](#spectra)
    - [`PafFile`](#paffile)
    - [`_event_lister`](#_event_lister)
    - [`_event_time_adder`](#_event_time_adder)
    - [`_short_trace_describer`](#_short_trace_describer)
    - [`_spectrum_time_finder`](#_spectrum_time_finder)
    - [`_trace_title_maker`](#_trace_title_maker)
    - [`_transmission_converter`](#_transmission_converter)
    - [`_unit_cleaner`](#_unit_cleaner)
    - [`dataset_namer`](#dataset_namer)
    - [`experiment_paf_loader`](#experiment_paf_loader)
    - [`experiment_summary_reader`](#experiment_summary_reader)
    - [`record_scanner`](#record_scanner)
    - [`rtf_converter`](#rtf_converter)
    - [`spectra_parser`](#spectra_parser)
    - [`stream_extractor`](#stream_extractor)
    - [`token_reader`](#token_reader)
    - [`u32_reader`](#u32_reader)
    - [`warning_printer`](#warning_printer)
- [`utils_shared/pca_fitter.py`](#utils_sharedpca_fitterpy)
    - [`_component_orienter`](#_component_orienter)
    - [`_nuisance_basis_builder`](#_nuisance_basis_builder)
    - [`_peak_finder`](#_peak_finder)
    - [`_spectra_gridder`](#_spectra_gridder)
    - [`_varimax_rotator`](#_varimax_rotator)
    - [`component_builder`](#component_builder)
    - [`component_classifier`](#component_classifier)
    - [`component_count_suggester`](#component_count_suggester)
    - [`component_finder`](#component_finder)
    - [`decomposition_example_finder`](#decomposition_example_finder)
    - [`fit_saver`](#fit_saver)
    - [`fit_table_builder`](#fit_table_builder)
- [`utils_shared/pca_plotter.py`](#utils_sharedpca_plotterpy)
    - [`_example_drawer`](#_example_drawer)
    - [`_reference_line_drawer`](#_reference_line_drawer)
    - [`pca_example_figure_builder`](#pca_example_figure_builder)
    - [`pca_figure_builder`](#pca_figure_builder)
- [`utils_shared/questions.py`](#utils_sharedquestionspy)
    - [`UserQuitError`](#userquiterror)
    - [`_brightener`](#_brightener)
    - [`_input_reader`](#_input_reader)
    - [`_limits_checker`](#_limits_checker)
    - [`_list_ending_builder`](#_list_ending_builder)
    - [`_number_builder`](#_number_builder)
    - [`_number_depth_finder`](#_number_depth_finder)
    - [`_number_hint_builder`](#_number_hint_builder)
    - [`_numbers_hint_builder`](#_numbers_hint_builder)
    - [`_options_printer`](#_options_printer)
    - [`_question_printer`](#_question_printer)
    - [`_time_announcer`](#_time_announcer)
    - [`_unit_highlighter`](#_unit_highlighter)
    - [`accept_asker`](#accept_asker)
    - [`choice_asker`](#choice_asker)
    - [`confirm_waiter`](#confirm_waiter)
    - [`enter_waiter`](#enter_waiter)
    - [`heading_printer`](#heading_printer)
    - [`info_printer`](#info_printer)
    - [`multi_asker`](#multi_asker)
    - [`number_asker`](#number_asker)
    - [`numbering_getter`](#numbering_getter)
    - [`numbering_setter`](#numbering_setter)
    - [`path_cleaner`](#path_cleaner)
    - [`progress_clearer`](#progress_clearer)
    - [`progress_printer`](#progress_printer)
    - [`retry_teller`](#retry_teller)
    - [`section_starter`](#section_starter)
    - [`text_asker`](#text_asker)
    - [`text_colourer`](#text_colourer)
    - [`text_italiser`](#text_italiser)
    - [`time_request_setter`](#time_request_setter)
    - [`typed_number_reader`](#typed_number_reader)
    - [`yes_no_asker`](#yes_no_asker)
- [`utils_shared/redox_regions.py`](#utils_sharedredox_regionspy)
    - [`_region_open_checker`](#_region_open_checker)
    - [`edge_anchor_finder`](#edge_anchor_finder)
    - [`edge_time_finder`](#edge_time_finder)
    - [`haem_levels_finder`](#haem_levels_finder)
    - [`percent_oxidised_calculator`](#percent_oxidised_calculator)
    - [`region_edge_copier`](#region_edge_copier)
    - [`region_edge_setter`](#region_edge_setter)
    - [`region_edges_builder`](#region_edges_builder)
    - [`region_layout_finder`](#region_layout_finder)
    - [`region_level_finder`](#region_level_finder)
    - [`region_pointer_reader`](#region_pointer_reader)
    - [`region_span_reader`](#region_span_reader)
    - [`short_region_closer`](#short_region_closer)
- [`utils_shared/reference_level.py`](#utils_sharedreference_levelpy)
    - [`_usable_point_keeper`](#_usable_point_keeper)
    - [`reference_level_finder`](#reference_level_finder)
    - [`start_level_finder`](#start_level_finder)
    - [`window_seconds_calculator`](#window_seconds_calculator)
- [`utils_shared/run_logging.py`](#utils_sharedrun_loggingpy)
    - [`_Tee`](#_tee)
    - [`answer_logger`](#answer_logger)
    - [`details_place_setter`](#details_place_setter)
    - [`details_writer`](#details_writer)
    - [`logging_starter`](#logging_starter)
    - [`logging_stopper`](#logging_stopper)
    - [`settings_logger`](#settings_logger)
- [`utils_shared/schema.py`](#utils_sharedschemapy)
    - [`finite_float_converter`](#finite_float_converter)
    - [`measurement_column_finder`](#measurement_column_finder)
    - [`source_resolver`](#source_resolver)
    - [`time_getter`](#time_getter)
    - [`value_getter`](#value_getter)
- [`utils_shared/spectral_decomposer.py`](#utils_sharedspectral_decomposerpy)
    - [`_fit_heading_reader`](#_fit_heading_reader)
    - [`_fit_table_cleaner`](#_fit_table_cleaner)
    - [`_fit_unit_finder`](#_fit_unit_finder)
    - [`_haem_shape_getter`](#_haem_shape_getter)
    - [`_headed_fit_reader`](#_headed_fit_reader)
    - [`_number_column_reader`](#_number_column_reader)
    - [`_preset_reader`](#_preset_reader)
    - [`_unit_scaler`](#_unit_scaler)
    - [`_wavelength_masker`](#_wavelength_masker)
    - [`answers_fit_loader`](#answers_fit_loader)
    - [`background_builder`](#background_builder)
    - [`basis_solver`](#basis_solver)
    - [`data_filterer`](#data_filterer)
    - [`decomposition_gap_calculator`](#decomposition_gap_calculator)
    - [`delta_abs_calculator`](#delta_abs_calculator)
    - [`experiment_decomposer`](#experiment_decomposer)
    - [`fit_describer`](#fit_describer)
    - [`fit_file_writer`](#fit_file_writer)
    - [`fit_haem_selector`](#fit_haem_selector)
    - [`fit_importer`](#fit_importer)
    - [`fit_loader`](#fit_loader)
    - [`fit_names_lister`](#fit_names_lister)
    - [`fit_range_finder`](#fit_range_finder)
    - [`fit_scale_standardiser`](#fit_scale_standardiser)
    - [`haem_files_combiner`](#haem_files_combiner)
    - [`haem_name_plainer`](#haem_name_plainer)
    - [`haem_name_typesetter`](#haem_name_typesetter)
    - [`library_haems_lister`](#library_haems_lister)
    - [`preset_importer`](#preset_importer)
    - [`s_array_generator`](#s_array_generator)
    - [`scatter_background_builder`](#scatter_background_builder)
    - [`spectrum_decomposer`](#spectrum_decomposer)
- [`utils_shared/survey.py`](#utils_sharedsurveypy)
    - [`_columns_text_builder`](#_columns_text_builder)
    - [`_event_line_builder`](#_event_line_builder)
    - [`_first_event_finder`](#_first_event_finder)
    - [`_last_event_finder`](#_last_event_finder)
    - [`_limit_converter`](#_limit_converter)
    - [`_limit_maximum_getter`](#_limit_maximum_getter)
    - [`_maths_converter`](#_maths_converter)
    - [`_minutes_recaller`](#_minutes_recaller)
    - [`_natural_sorter`](#_natural_sorter)
    - [`_subscript_stripper`](#_subscript_stripper)
    - [`_tidy_labels_offerer`](#_tidy_labels_offerer)
    - [`_trim_minutes_clamper`](#_trim_minutes_clamper)
    - [`data_folder_lister`](#data_folder_lister)
    - [`data_folder_resolver`](#data_folder_resolver)
    - [`decomposition_asker`](#decomposition_asker)
    - [`delta_psi_asker`](#delta_psi_asker)
    - [`delta_psi_offer_checker`](#delta_psi_offer_checker)
    - [`event_asker`](#event_asker)
    - [`event_entries_builder`](#event_entries_builder)
    - [`files_asker`](#files_asker)
    - [`free_folder_finder`](#free_folder_finder)
    - [`haem_choice_asker`](#haem_choice_asker)
    - [`haem_form_option_builder`](#haem_form_option_builder)
    - [`haem_name_formatter`](#haem_name_formatter)
    - [`label_angle_asker`](#label_angle_asker)
    - [`label_tidier`](#label_tidier)
    - [`multi_experiment_asker`](#multi_experiment_asker)
    - [`ocr_kind_lister`](#ocr_kind_lister)
    - [`ocr_option_builder`](#ocr_option_builder)
    - [`od_scaling_asker`](#od_scaling_asker)
    - [`paf_finder`](#paf_finder)
    - [`results_counter`](#results_counter)
    - [`results_folder_checker`](#results_folder_checker)
    - [`results_folder_resolver`](#results_folder_resolver)
    - [`saved_values_reader`](#saved_values_reader)
    - [`signal_asker`](#signal_asker)
    - [`size_asker`](#size_asker)
    - [`temperature_asker`](#temperature_asker)
    - [`tidy_labels_finder`](#tidy_labels_finder)
    - [`trim_layout_finder`](#trim_layout_finder)
    - [`trim_limits_builder`](#trim_limits_builder)
    - [`trim_minutes_builder`](#trim_minutes_builder)
    - [`trim_minutes_setter`](#trim_minutes_setter)
    - [`trim_pointer_reader`](#trim_pointer_reader)
    - [`window_kind_asker`](#window_kind_asker)
    - [`windows_ensurer`](#windows_ensurer)
- [`utils_shared/trimming.py`](#utils_sharedtrimmingpy)
    - [`experiment_trimmer`](#experiment_trimmer)
- [`utils_shared/user_notices.py`](#utils_shareduser_noticespy)
    - [`_file_namer`](#_file_namer)
    - [`_own_sentence_finder`](#_own_sentence_finder)
    - [`problem_describer`](#problem_describer)
    - [`problem_shower`](#problem_shower)
    - [`problem_teller`](#problem_teller)
    - [`warning_shower`](#warning_shower)
- [`utils_shared/user_places.py`](#utils_shareduser_placespy)
    - [`UserPlaces`](#userplaces)
    - [`_launch_log_shortener`](#_launch_log_shortener)
    - [`app_output_logger`](#app_output_logger)
    - [`launch_log_opener`](#launch_log_opener)
    - [`user_folder_preparer`](#user_folder_preparer)
    - [`user_places_finder`](#user_places_finder)
- [`utils_viewer/viewer_edges.py`](#utils_viewerviewer_edgespy)
    - [`EdgeChoice`](#edgechoice)
    - [`EdgeOverlay`](#edgeoverlay)
    - [`edge_hit_finder`](#edge_hit_finder)
    - [`every_file_setter`](#every_file_setter)
    - [`minute_x_finder`](#minute_x_finder)
    - [`own_value_lister`](#own_value_lister)
    - [`photo_maker`](#photo_maker)
    - [`shaded_picture_maker`](#shaded_picture_maker)
    - [`x_minute_finder`](#x_minute_finder)
- [`utils_viewer/viewer_gui.py`](#utils_viewerviewer_guipy)
    - [`GuiUnavailableError`](#guiunavailableerror)
    - [`ViewerGui`](#viewergui)
    - [`_hint_chooser`](#_hint_chooser)
    - [`active_gui_getter`](#active_gui_getter)
    - [`gui_runner`](#gui_runner)
    - [`pointed_time_finder`](#pointed_time_finder)
    - [`window_opener`](#window_opener)
- [`utils_viewer/viewer_multi.py`](#utils_viewerviewer_multipy)
    - [`_kept_builder`](#_kept_builder)
    - [`_pictures_builder`](#_pictures_builder)
    - [`multi_figure_checker_builder`](#multi_figure_checker_builder)
- [`utils_viewer/viewer_preview.py`](#utils_viewerviewer_previewpy)
    - [`PreviewSpec`](#previewspec)
    - [`TimeAxis`](#timeaxis)
    - [`ViewerSession`](#viewersession)
    - [`_file_exporter`](#_file_exporter)
    - [`_kept_haems_drawer`](#_kept_haems_drawer)
    - [`_kept_psi_drawer`](#_kept_psi_drawer)
    - [`_loaded_experiment_getter`](#_loaded_experiment_getter)
    - [`_overlay_drawer`](#_overlay_drawer)
    - [`preview_info_builder`](#preview_info_builder)
    - [`import_data_exporter`](#import_data_exporter)
    - [`kept_file_lister`](#kept_file_lister)
    - [`pca_example_picture_builder`](#pca_example_picture_builder)
    - [`pca_picture_builder`](#pca_picture_builder)
    - [`pca_spectra_gatherer`](#pca_spectra_gatherer)
    - [`preview_drawer`](#preview_drawer)
    - [`preview_figure_builder`](#preview_figure_builder)
    - [`time_axis_finder`](#time_axis_finder)
    - [`time_title_chooser`](#time_title_chooser)
- [`utils_viewer/viewer_renderer.py`](#utils_viewerviewer_rendererpy)
    - [`PreviewRenderer`](#previewrenderer)
- [`utils_viewer/viewer_self_test.py`](#utils_viewerviewer_self_testpy)
    - [`_computer_describer`](#_computer_describer)
    - [`_made_up_experiment_builder`](#_made_up_experiment_builder)
    - [`_preview_shower`](#_preview_shower)
    - [`self_test_runner`](#self_test_runner)
- [`utils_viewer/viewer_stages.py`](#utils_viewerviewer_stagespy)
    - [`_addition_time_lister`](#_addition_time_lister)
    - [`_answers_previewer`](#_answers_previewer)
    - [`_component_namer`](#_component_namer)
    - [`_decomposition_storer`](#_decomposition_storer)
    - [`_export_asker`](#_export_asker)
    - [`_export_refresher`](#_export_refresher)
    - [`_figure_starter`](#_figure_starter)
    - [`_fit_file_saver`](#_fit_file_saver)
    - [`_kept_restorer`](#_kept_restorer)
    - [`_label_table_filler`](#_label_table_filler)
    - [`_limits_lister`](#_limits_lister)
    - [`_od_lister`](#_od_lister)
    - [`_od_table_filler`](#_od_table_filler)
    - [`_pca_pictures_publisher`](#_pca_pictures_publisher)
    - [`_region_rules_lister`](#_region_rules_lister)
    - [`_regions_chooser`](#_regions_chooser)
    - [`_regions_lister`](#_regions_lister)
    - [`_standard_fit_loader`](#_standard_fit_loader)
    - [`_strip_change_applier`](#_strip_change_applier)
    - [`_strip_shower`](#_strip_shower)
    - [`_table_filler`](#_table_filler)
    - [`_unfit_windows_lister`](#_unfit_windows_lister)
    - [`_windows_chooser`](#_windows_chooser)
    - [`browser_stage_runner`](#browser_stage_runner)
    - [`details_stage_runner`](#details_stage_runner)
    - [`pca_stage_runner`](#pca_stage_runner)
    - [`plots_stage_runner`](#plots_stage_runner)
    - [`processing_stage_runner`](#processing_stage_runner)
    - [`region_files_lister`](#region_files_lister)
    - [`trim_stage_runner`](#trim_stage_runner)
    - [`viewer_asker`](#viewer_asker)
    - [`windows_stage_runner`](#windows_stage_runner)
- [`utils_viewer/viewer_strip.py`](#utils_viewerviewer_strippy)
    - [`EdgeRow`](#edgerow)
    - [`SettingsStrip`](#settingsstrip)
    - [`_page_journal_finder`](#_page_journal_finder)
    - [`form_answers_builder`](#form_answers_builder)
    - [`haem_form_choices_lister`](#haem_form_choices_lister)
    - [`haem_ticks_resolver`](#haem_ticks_resolver)
    - [`height_checker`](#height_checker)
    - [`kept_decomposition_builder`](#kept_decomposition_builder)
    - [`minutes_checker`](#minutes_checker)
    - [`psi_answers_builder`](#psi_answers_builder)
    - [`psi_change_describer`](#psi_change_describer)
    - [`psi_number_checker`](#psi_number_checker)
    - [`psi_seconds_filler`](#psi_seconds_filler)
    - [`psi_summary_writer`](#psi_summary_writer)
    - [`psi_values_builder`](#psi_values_builder)
    - [`size_answers_builder`](#size_answers_builder)
    - [`strip_values_builder`](#strip_values_builder)
    - [`strip_values_checker`](#strip_values_checker)
    - [`width_choices_lister`](#width_choices_lister)
- [`utils_viewer/viewer_table.py`](#utils_viewerviewer_tablepy)
    - [`AnswerTable`](#answertable)
    - [`_cell_name_joiner`](#_cell_name_joiner)
    - [`_number_writer`](#_number_writer)
    - [`cell_reader`](#cell_reader)
    - [`label_entries_reader`](#label_entries_reader)
    - [`label_table_builder`](#label_table_builder)
    - [`od_rows_reader`](#od_rows_reader)
    - [`od_table_builder`](#od_table_builder)
    - [`table_problem_teller`](#table_problem_teller)
    - [`wheel_step_finder`](#wheel_step_finder)
- [`utils_viewer/viewer_terminal.py`](#utils_viewerviewer_terminalpy)
    - [`OutputRouter`](#outputrouter)
    - [`ansi_colour_getter`](#ansi_colour_getter)
    - [`ansi_splitter`](#ansi_splitter)
    - [`ansi_style_updater`](#ansi_style_updater)

## `config.py`

Settings and defaults of Portimao: figure styles, journal sizes and colours.

### CLASSES

#### `Config`

```text
---- Summary ----
Everything derived from the answers: figure style and sizes, matplotlib settings,
and the settings of the individual plot.

---- Attributes ----
answers : dict
    Terminal answers merged over DEFAULT_ANSWERS.
SPEC : dict
    Journal specification (widths, fonts, dpi) of the chosen journal.
STYLE : dict
    Figure style from figure_style_builder (fonts, unit and spacing in points).
FONTS : dict
    Font sizes in points.
UNIT : float
    Spacing unit in points.
FIGURE_SIZE : Tuple[float, float]
    Figure width and height in inches.
FIGURE_DPI : int
    Resolution of saved figures in dots per inch.
STYLE_WARNINGS : List[str]
    Warnings about the figure style, printed by the caller.
RC_PARAMS : dict
    matplotlib rcParams of the figure style.

---- Globals read ----
BASE_FONT_PT, DEFAULT_ANSWERS, JOURNAL_SPECS, LINE_WIDTH_PT, SPACING.

---- Methods ----
__init__
percent_need_checker
plot_config_builder
source_chooser
```

##### `__init__`

```text
---- Summary ----
Method to build the figure style, matplotlib settings and sizes of one figure
from the terminal answers.

---- Inputs ----
answers : dict
    Terminal answers; missing keys are filled from DEFAULT_ANSWERS.

---- Globals read ----
DEFAULT_ANSWERS, JOURNAL_SPECS, BASE_FONT_PT, SPACING, LINE_WIDTH_PT (module
constants); make_style, check_style, figure_size_inches (imported).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the answers, SPEC, STYLE, FONTS, UNIT, FIGURE_SIZE, FIGURE_DPI,
STYLE_WARNINGS and RC_PARAMS attributes on the instance.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
figure_style_builder
figure_style_checker
```

##### `percent_need_checker`

```text
---- Summary ----
Method to say whether the percent-of-range version of the OCR has to be
calculated. The % oxidised of the haems needs no asking: every file with an
oxidised and a reduced region has it.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the OCR is plotted as a % of its range.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `plot_config_builder`

```text
---- Summary ----
Method to build the settings dictionary of one individual-experiment figure.

---- Inputs ----
vo2_source : str
    OCR source plotted: "raw", "od" or "percent".
haem_source : Optional[str]
    Haem source plotted, for example "delta_abs_od", or None for no haem panels.
ignore_first : Optional[float]
    Minutes ignored at the start for the axis limits; None uses the answers.
ignore_last : Optional[float]
    Minutes ignored at the end for the axis limits; None uses the answers.
delta_psi : bool
    True to draw a Δψ panel under the haems, for a file that has Δψ; the
    figures of several files leave it out.

---- Globals read ----
haem_colours (module function); the style, font and size attributes of the
instance.

---- Outputs ----
dict
    Plot settings in the format used by plot_experiment.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
haem_colour_mapper
```

##### `source_chooser`

```text
---- Summary ----
Method to choose the OCR source and haem source used for the plot and the event
averages.

---- Inputs ----
od_available : bool
    True when the experiment has OD, volume and dilution factor.

---- Globals read ----
FALLBACK_WITHOUT_OD, HAEM_SOURCE_BY_MODE (module constants).

---- Outputs ----
Tuple[str, Optional[str]]
    (OCR source, haem source), for example ("od", "delta_abs_od"). The haem
    source is None when nothing is decomposed; OD sources fall back to raw ones
    without OD.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `haem_colour_mapper`

```text
---- Summary ----
Main function to give each haem a plot colour of its type: shades of green for the
a haems, blue for the b and red for the c. A usual haem keeps its own colour
unless a haem before it in the list took that colour; any other haem takes the
first shade of its type no haem of the list has yet.

---- Inputs ----
names : List[str]
    Haem names as written in the fit file, plain or in figure form.

---- Globals read ----
HAEM_COLOURS, HAEM_TYPE_COLOURS (module constants).

---- Outputs ----
Dict[str, str]
    {haem name: hex colour}. A name of no known type takes a colour no haem type
    has. Colours repeat only when a type has more haems than shades.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
haem_type_finder
name_simplifier
```

#### `pca_colour_mapper`

```text
---- Summary ----
Main function to give each PCA component a plot colour from the haem type its peaks
look like: green for a-like, blue for b-like, red for c-like, with a darker then a
lighter shade for each further component of the same type, and a colour no haem
type has for mixed or unknown components.

---- Inputs ----
types : List[str]
    Type of each component: 'a', 'b', 'c', 'mixed' or 'unknown'
    (pca_fitter.component_classifier).

---- Globals read ----
HAEM_TYPE_COLOURS (module constant).

---- Outputs ----
List[str]
    Hex colour of each component, in the same order. Colours repeat only when a
    type has more components than shades.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `launchers/mac_app_builder.py`

Builds the Mac app (Portimao.app) with PyInstaller and signs it ad hoc; run on a Mac.

### BUILD HELPERS

#### `_ad_hoc_signer`

```text
---- Summary ----
Helper function to sign the app ad hoc (no Apple certificate), as Apple Silicon
Macs need every program to be signed, then to check the signature.

---- Inputs ----
app : Path
    The .app folder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Raises RuntimeError, with codesign's own words, when the signing or
    the check fails.

---- Globals mutated ----
None. Signs the files of the app (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_arguments_builder`

```text
---- Summary ----
Helper function to build PyInstaller's arguments: a windowed Mac app made from
the app's start (launchers/mac_app_starter.py, which runs main.py), with its icon,
the program's own files and the details of each package.

---- Inputs ----
packages : Sequence[str]
    Names of the packages whose details (version) the app must carry; the
    self-test lists their versions.

---- Globals read ----
APP_NAME, BUNDLE_ID, DIST_FOLDER, ENTRY, ICON, INSIDE, ROOT, WORK_FOLDER (module
constants).

---- Outputs ----
List[str]
    The arguments, as typed after `pyinstaller`.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_info_plist_writer`

```text
---- Summary ----
Helper function to write the program's version, its name and the reasons macOS
shows when the app asks for a guarded folder into the app's Info.plist, keeping
every other key PyInstaller wrote.

---- Inputs ----
plist_path : Path
    The app's Contents/Info.plist.
version : str
    Program version, for example "2.2" (program_version_reader).

---- Globals read ----
PLIST_VALUES, VERSION_PATTERN (module constants).

---- Outputs ----
None
    Nothing. Raises ValueError when the version is not made of numbers and dots.

---- Globals mutated ----
None. Rewrites the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `main`

```text
---- Summary ----
Main function to build dist/Portimao.app on this Mac, for its own kind of chip: the
program with Python, Tk and every package inside, its update and the Mac report,
the release's version in its Info.plist, signed ad hoc. Run it with the program's environment, with PyInstaller
installed in it.

---- Inputs ----
None.

---- Globals read ----
APP_PATH, ROOT (module constants).

---- Outputs ----
int
    0 when the app was built and its signature checks, 1 otherwise (the reason is
    printed).

---- Globals mutated ----
None. Puts the program folder first on sys.path; writes build/ and dist/ (side
effects).

---- Equations ----
None.

---- Helpers ----
_ad_hoc_signer
_arguments_builder
_info_plist_writer
program_version_reader
```

## `launchers/mac_app_mover.py`

Moves a Mac install of the old launcher to the Mac app, and makes the Desktop file of a

### MOVE HELPERS

#### `_app_opener`

```text
---- Summary ----
Helper function to open the app as a click does, passing on the check switch when it
is set, so the Mac check follows the move through to the app's self-test.

---- Inputs ----
app : Path
    The installed .app folder.

---- Globals read ----
SELF_TEST_SWITCH (module constant); os.environ['PORTIMAO_SELF_TEST'].

---- Outputs ----
None
    Nothing. Raises OSError when macOS's open cannot be run.

---- Globals mutated ----
None. Starts the app (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_command_text_maker`

```text
---- Summary ----
Helper function to write the Desktop file that starts Portimao the old way: the
launcher with the Python that runs it now, or run.sh when that Python has gone.

---- Inputs ----
root : Path
    The program folder.
python : str
    Path of the Python running the launcher.

---- Globals read ----
COMMAND_MARK (module constant).

---- Outputs ----
str
    The text of the file, a shell script; its second line names the folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_desktop_link_mover`

```text
---- Summary ----
Helper function to point the Desktop at the app: the old launcher's link, or our
Desktop file, is replaced by a link to the app with the same name, so a double-click
where the user is used to opens the app. With neither there, nothing is added.

---- Inputs ----
root : Path
    The program folder being moved.
home : Path
    The home folder.
app : Path
    The installed .app folder.
log : Callable[[str], None]
    Adds a line to the move log.

---- Globals read ----
APP_NAME, COMMAND_NAME (module constants).

---- Outputs ----
None
    Nothing. A Desktop that cannot be changed is left as it is (logged).

---- Globals mutated ----
None. Deletes and makes links on the Desktop (side effects).

---- Equations ----
None.

---- Helpers ----
_link_into_checker
_our_command_checker
```

#### `_git_runner`

```text
---- Summary ----
Helper function to run a git command in the program folder and keep its output.

---- Inputs ----
root : Path
    The program folder.
arguments : List[str]
    What follows `git`.

---- Globals read ----
HIDDEN (module constant).

---- Outputs ----
subprocess.CompletedProcess
    The finished command; its return code is 127 when git cannot be run.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_installer_runner`

```text
---- Summary ----
Helper function to install the app with the program's own install_mac.sh, as the
install line does, but without opening it; each line it prints is shown and logged.

---- Inputs ----
root : Path
    The program folder, which holds install_mac.sh.
home : Path
    The home folder; the app goes in its Applications folder.
show : Callable[[str], None]
    Shows a line of progress.
log : Callable[[str], None]
    Adds a line to the move log.

---- Globals read ----
APP_NAME, INSTALLER_NAME (module constants).

---- Outputs ----
Tuple[Optional[Path], str]
    (the installed .app folder, '') or (None, why it was not installed).

---- Globals mutated ----
None. Downloads and installs the app (side effect).

---- Equations ----
None.

---- Helpers ----
_reason_shortener
```

#### `_link_into_checker`

```text
---- Summary ----
Helper function to say whether a Desktop item is the old launcher's link: a symbolic
link to something inside the program folder (its Portimao.app, which the update has
taken away).

---- Inputs ----
link : Path
    The Desktop item.
root : Path
    The program folder.

---- Globals read ----
None.

---- Outputs ----
bool
    True when it is a link into the program folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_log_opener`

```text
---- Summary ----
Helper function to give the function that adds a line, with the date and time, to
the move log in the folder's logs folder (which the move keeps).

---- Inputs ----
root : Path
    The program folder.

---- Globals read ----
LOG_NAME (module constant).

---- Outputs ----
Callable[[str], None]
    Adds one line. A log that cannot be written just loses its lines.

---- Globals mutated ----
None. Writes the log (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_macos_too_old_checker`

```text
---- Summary ----
Helper function to say whether a macOS version is too old for the app.

---- Inputs ----
version : str
    The macOS version, for example "13.6"; empty when not known.

---- Globals read ----
OLDEST_MACOS (module constant).

---- Outputs ----
bool
    True when it is older than macOS 14; False when newer or unreadable.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_macos_version_reader`

```text
---- Summary ----
Helper function to read this Mac's macOS version from sw_vers, which gives the real
one where a Python built for older Macs is told "10.16".

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
str
    The version, for example "15.1"; Python's own reading when sw_vers cannot be
    run, empty when neither knows.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_note_shower`

```text
---- Summary ----
Helper function to show a macOS message that holds nothing up: the launcher goes on
(or closes) while it is on screen.

---- Inputs ----
text : str
    The message.
shows_messages : bool
    False to show nothing (for the tests).

---- Globals read ----
SELF_TEST_SWITCH (module constant); os.environ['PORTIMAO_SELF_TEST'].

---- Outputs ----
None
    Nothing. No message is shown with the check switch, or where macOS's message
    cannot be shown.

---- Globals mutated ----
None. Shows a message (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_our_command_checker`

```text
---- Summary ----
Helper function to say whether a Desktop file is the one made for this program
folder (by desktop_file_maker).

---- Inputs ----
command : Path
    The Desktop file.
root : Path
    The program folder.

---- Globals read ----
COMMAND_MARK (module constant).

---- Outputs ----
bool
    True when it is a file whose mark names this folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_program_file_lister`

```text
---- Summary ----
Helper function to list the old program files: what git tracks, apart from the fits
and any file the user has changed, then what the program made beside them (its
Python environment, its marks and caches) and git's own folder.

---- Inputs ----
root : Path
    The program folder, a git clone.

---- Globals read ----
KEPT_FOLDERS, PROGRAM_EXTRAS (module constants).

---- Outputs ----
Optional[List[Path]]
    The files and folders to take away, git's folder last; None when git could not
    list them.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_git_runner
```

#### `_program_file_remover`

```text
---- Summary ----
Helper function to take away the old program files, then the folders they leave
empty (or holding only Python's caches). Nothing outside the program folder is
touched, and a link is taken away without following it.

---- Inputs ----
root : Path
    The program folder.
paths : List[Path]
    The files and folders to take away (_program_file_lister).
log : Callable[[str], None]
    Adds a line to the move log.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. What cannot be taken away is left and named in the log.

---- Globals mutated ----
None. Deletes files and folders (side effect).

---- Equations ----
None.

---- Helpers ----
_tree_remover
```

#### `_reason_shortener`

```text
---- Summary ----
Helper function to keep what went wrong from one of install_mac.sh's sentences,
which say what went wrong, a colon, then what to do on the command line.

---- Inputs ----
sentence : str
    The last line the install printed.

---- Globals read ----
None.

---- Outputs ----
str
    The part before the colon, without a full stop; empty for an empty line.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_tree_remover`

```text
---- Summary ----
Helper function to delete a folder with everything in it, read-only files included
(git keeps its files read-only, which Windows would refuse to delete).

---- Inputs ----
folder : Path
    The folder; not a link.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Raises OSError when it cannot be deleted.

---- Globals mutated ----
None. Deletes files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_user_things_copier`

```text
---- Summary ----
Helper function to copy the user's fits and last answers from a program folder that
is not the app's own folder into it, so the app finds them. A file already there is
never overwritten; the data folders stay where they are.

---- Inputs ----
root : Path
    The program folder being moved.
own_folder : Path
    The app's own folder (Portimao in the home folder); made when missing.
log : Callable[[str], None]
    Adds a line to the move log.

---- Globals read ----
FITS_FOLDER_NAME, LAST_ANSWERS_NAME (module constants).

---- Outputs ----
None
    Nothing. What cannot be copied is named in the log.

---- Globals mutated ----
None. Makes folders and copies files (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `app_mover`

```text
---- Summary ----
Main function to move an install of the old launcher to the Mac app, at its first
start after the update, without asking. Only a git clone on main (the user
download) on macOS 14 or newer is moved. The app is installed in the user's own
Applications folder first, and nothing is taken away unless it is in. Then the old
program files go; the fits, the data folders, the logs, the last answers, any
program file the user changed and anything else of theirs stay. The Desktop link
opens the app from then on, the app opens at once and a note beside it says where
the user's things are. Every step is written to logs/move_to_app.log.

---- Inputs ----
root : Path
    The program folder.
home : Path
    The home folder.
show : Callable[[str], None]
    Shows a line in the launcher's small window.
macos_version : Optional[str]
    The macOS version; None for this Mac's.
installer : Optional[Callable[..., Tuple[Optional[Path], str]]]
    Installs the app, called with (root, home, show, log); None for install_mac.sh
    (the tests give their own).
opener : Optional[Callable[[Path], None]]
    Opens the app; None for macOS's open.
shows_messages : bool
    False to show no message (for the tests).

---- Globals read ----
OWN_FOLDER_NAME (module constant).

---- Outputs ----
bool
    True when the app is installed and opening, so the launcher closes; False when
    this install is not moved, or the app could not be installed (a note says so),
    so the program starts the old way.

---- Globals mutated ----
None. Installs the app, deletes the old program files, copies files, changes the
Desktop link, opens the app and writes the move log (side effects).

---- Equations ----
None.

---- Helpers ----
_app_opener
_desktop_link_mover
_installer_runner
_log_opener
_macos_version_reader
_note_shower
_program_file_lister
_program_file_remover
_user_things_copier
move_blocker_finder
```

#### `desktop_file_maker`

```text
---- Summary ----
Main function to give a Mac that runs Portimao from its folder (older than macOS
14, a move that failed, a developer's copy) a file on the Desktop that starts it the
old way. It takes the place of the old launcher's link, which the update made
useless, and is made the first time a folder is started; on macOS older than 14 a
note says why, once.

---- Inputs ----
root : Path
    The program folder.
home : Path
    The home folder.
python : str
    Path of the Python running the launcher.
is_first : bool
    True the first time this folder is started (the launcher's shortcut mark).
macos_version : Optional[str]
    The macOS version; None for this Mac's.
shows_messages : bool
    False to show no message (for the tests).

---- Globals read ----
APP_NAME, COMMAND_NAME (module constants).

---- Outputs ----
bool
    True when the old launcher's link was replaced.

---- Globals mutated ----
None. Writes the Desktop file and deletes the old link (side effects). Raises
OSError when the Desktop cannot be changed.

---- Equations ----
None.

---- Helpers ----
_command_text_maker
_link_into_checker
_macos_too_old_checker
_macos_version_reader
_note_shower
```

#### `move_blocker_finder`

```text
---- Summary ----
Main function to say why this install is not moved to the app. Only the user
download is moved: a git clone on main, with its install script, on macOS 14 or
newer. A developer's copy on another branch, and a copy from a zip file, are left
as they are.

---- Inputs ----
root : Path
    The program folder.
macos_version : str
    The macOS version, for example "15.1".

---- Globals read ----
INSTALLER_NAME, MAIN_BRANCH, OLDEST_MACOS (module constants).

---- Outputs ----
Optional[str]
    Why it is not moved, in plain words; None when it is.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_git_runner
_macos_too_old_checker
```

## `launchers/mac_app_starter.py`

The Mac app's start: updates the app, then runs the program, and says what to do when

### START HELPERS

#### `_problem_logger`

```text
---- Summary ----
Helper function to add the error being handled, with its traceback, to the app's
launch log, which the Mac report shows.

---- Inputs ----
places : UserPlaces
    Where the logs folder is.
heading : str
    What was going on when the error came.

---- Globals read ----
LAUNCH_LOG_NAME (imported constant).

---- Outputs ----
None
    Nothing. A log that cannot be written is left as it is.

---- Globals mutated ----
None. Writes the log (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `main`

```text
---- Summary ----
Main function of the Mac app (PyInstaller builds it from this file): it updates the
app from GitHub's newest release first, then runs the program (main.py). Anything
that stops the program is written to the launch log and shown in a message with a
Copy details button.

---- Inputs ----
None.

---- Globals read ----
STOPPED_SENTENCE (module constant).

---- Outputs ----
int
    0 when the new version opens in place of this one, otherwise the program's exit
    code (1 when it stopped because of a problem).

---- Globals mutated ----
None. May replace the app, runs the program and shows messages (side effects).

---- Equations ----
None.

---- Helpers ----
_problem_logger
start_problem_shower
update_installer
user_places_finder
```

## `launchers/make_icons.py`

Makes the Windows icon from assets/icon.png (square, 512 x 512 pixels or larger).

### FUNCTIONS

#### `main`

```text
---- Summary ----
Main function to square assets/icon.png and turn it into the Windows icon
(assets/icon.ico). The Mac app's icon is made from assets/icon.png when the app is
built (launchers/mac_app_builder.py).

---- Inputs ----
None.

---- Globals read ----
ROOT, SOURCE, WINDOWS_SIZES (module constants).

---- Outputs ----
int
    0 when the icons were made, 1 when the picture is missing.

---- Globals mutated ----
None. Writes the icon files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `main.py`

Main program: read .paf files, process them and export figures and workbooks.

### MAIN FUNCTIONS

#### `comparison_maker`

```text
---- Summary ----
Main function to draw the side-by-side figure of two chosen experiments, or to say
why it cannot be made.

---- Inputs ----
comparison : dict
    Side-by-side settings: {runs: (left, right), columns, height}.
kept : dict
    Results of experiment_processor keyed by experiment name.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
export_root : Path
    Results folder.

---- Globals read ----
settings.Config (the comparison journal is read from the answers).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the comparison figure files and prints the outcome (side effects).

---- Equations ----
None.

---- Helpers ----
comparison_figure_plotter
figure_size_calculator
plot_config_builder
problem_shower
warning_shower
```

#### `everything_asker`

```text
---- Summary ----
Main function to ask every question of the run after the files, in numbered
sections (trimming and ignoring, analysis, plots, summary figures, export), and to
build the per-file information.

---- Inputs ----
folder : Path
    Data folder, from files_asker.
summaries : List[dict]
    Summary of each readable file, from files_asker.
export_root : Path
    Results folder, from files_asker.
saved : dict
    Settings saved with the dataset, from files_asker; empty for a dataset never
    run.
exported : Optional[List[Path]]
    List the results folder is added to once the export of the import (3.4) writes
    into it; None when not needed.

---- Globals read ----
PLACES, JOURNAL_NAMES (module constants); settings.DEFAULT_ANSWERS.

---- Outputs ----
Tuple[dict, List[dict], Optional[dict], Optional[dict], Optional[List[str]]]
    (answers, per-experiment info dictionaries, fit, side-by-side comparison
    settings or None, names of the 2x2 grid experiments or None). Raises
    UserQuitError if the user declines to start.

---- Globals mutated ----
None. Reads from and prints to the terminal; writes last_answers.json through
last_answers_saver, the settings file of the dataset through
dataset_settings_saver, and the export of the import when one is chosen, adding to
``exported`` (side effects).

---- Equations ----
None.

---- Helpers ----
comparison_maker
dataset_settings_saver
file_settings_merger
haem_name_formatter
last_answers_saver
multi_experiment_asker
multi_figure_checker_builder
region_files_lister
section_starter
special_figures_maker
summary_figure_asker
viewer_asker
windows_stage_runner
yes_no_asker
```

#### `experiment_processor`

```text
---- Summary ----
Main function to read, process, plot and export one .paf file. Each step reports its
own problem so the next step still runs.

---- Inputs ----
info : dict
    Per-file information from everything_asker: path, name, trim and ignore times,
    OD values, events, custom and keep flags.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
fit : Optional[dict]
    Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
    not decomposed.
export_root : Path
    Results folder.

---- Globals read ----
plt (matplotlib.pyplot).

---- Outputs ----
Optional[dict]
    {experiment, vo2_source, haem_source, prepared} when the experiment is needed
    again for the comparison or special figures (info["keep"]), otherwise None.

---- Globals mutated ----
None. Writes the figure and the workbook files and prints progress (side effects).

---- Equations ----
None.

---- Helpers ----
experiment_data_processor
experiment_plotter
experiment_preparer
experiment_workbook_exporter
plot_config_builder
problem_shower
```

#### `last_answers_loader`

```text
---- Summary ----
Main function to read which data folder was used in the last run.

---- Inputs ----
None.

---- Globals read ----
PLACES (module constant; its last_answers_file).

---- Outputs ----
dict
    Contents of last_answers.json ({data_folder}); an empty dict when the file is
    missing or unreadable. The answers themselves are kept with each dataset
    (utils_shared.dataset_settings).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `last_answers_saver`

```text
---- Summary ----
Main function to remember the data folder of this run for the next one.

---- Inputs ----
values : dict
    Content to write to last_answers.json: {data_folder}.

---- Globals read ----
PLACES (module constant; its last_answers_file).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes last_answers.json (side effect); a read-only folder is ignored
silently.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `main`

```text
---- Summary ----
Main function of the program: run it in the experiment browser window (terminal on
the left, plots on the right). Portimao needs its window: when it cannot open, one
sentence says why and what to do, and nothing is asked. With the check switch
(PORTIMAO_SELF_TEST set to any value) it only checks that the window opens and shows
a made-up preview, then closes by itself. The Mac app first makes its own folder and
sends what it prints to its log; it has no terminal, so when its folder cannot be
made or the window cannot open, a message says what to do.

---- Inputs ----
None.

---- Globals read ----
PLACES, PROGRAM_TITLE, WINDOW_TITLE (module constants);
os.environ['PORTIMAO_SELF_TEST'].

---- Outputs ----
int
    0 when every file finished, 1 when the run was cancelled, a file failed, the
    app's own folder could not be made or the window could not open. With the check
    switch: 0 when the check passed, 1 when it failed.

---- Globals mutated ----
None. Opens the window, or prints why it could not; the app makes its own folder
and replaces sys.stdout and sys.stderr by its log; the app may show a message; the
details of a problem met before a run is logged go to the error stream it starts
with (side effects).

---- Equations ----
None.

---- Helpers ----
app_output_logger
details_place_setter
gui_runner
program_runner
self_test_runner
start_problem_shower
user_folder_preparer
```

#### `program_runner`

```text
---- Summary ----
Main function to run the program: ask for the files, start the log in the results
folder, ask the other questions, process every file, then draw the comparison and
special figures. The log keeps each answer from the results folder on, also when
the run is cancelled or the window closed part way.

---- Inputs ----
None.

---- Globals read ----
PLACES, PROGRAM_TITLE (written to the log), UPDATE_NOTE (module constants).

---- Outputs ----
int
    0 when every file finished, 1 when the run was cancelled or a file failed.

---- Globals mutated ----
None. Reads from and prints to the terminal, sets the matplotlib rcParams, writes
results and a log file, and replaces sys.stdout and sys.stderr while logging (side
effects).

---- Equations ----
None.

---- Helpers ----
comparison_maker
everything_asker
experiment_processor
files_asker
last_answers_loader
logging_starter
logging_stopper
problem_shower
section_starter
settings_logger
special_figures_maker
warning_shower
```

#### `special_figures_maker`

```text
---- Summary ----
Main function to draw the time response, haem and OCR response and 2x2 grid figures;
each is skipped, with the reason, if it cannot be made.

---- Inputs ----
kept : dict
    Results of experiment_processor keyed by experiment name.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
fit : Optional[dict]
    Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
    not decomposed.
export_root : Path
    Results folder.
exemplar_names : Optional[List[str]]
    Names of the four experiments of the 2x2 grid, or None.
is_preview : bool
    True to draw the figures only (for the experiment browser): no workbook is
    written.

---- Globals read ----
settings.Config; time_response_runner, ocr_and_haem_response_runner and
exemplar_runner (imported).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the figure files and prints the outcome (side effects).

---- Equations ----
None.

---- Helpers ----
exemplar_runner
ocr_and_haem_response_runner
problem_shower
time_response_runner
warning_shower
```

## `tests/conftest.py`

Makes the program's folders importable from the tests, however pytest is started, and

### CLASSES

#### `HiddenPopen`

```text
---- Summary ----
Starts a program as subprocess.Popen does, but on Windows without a console window
of its own, so a test never puts a window on the screen.

---- Attributes ----
As subprocess.Popen.

---- Globals read ----
HIDDEN (module constant).

---- Methods ----
__init__
```

##### `__init__`

```text
---- Summary ----
Main function to start the program with the hidden flag added to any flags the
caller gave.

---- Inputs ----
*args : Any
    As subprocess.Popen.
**kwargs : Any
    As subprocess.Popen.

---- Globals read ----
HIDDEN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None. Starts the program (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### CONFTEST HELPERS

#### `_window_refuser`

```text
---- Summary ----
Helper function to stand in for tkinter.Tk: it refuses to open a window, as Tk does
on a computer without a screen, so the program goes on without its window.

---- Inputs ----
*args : Any
    As tkinter.Tk (not used).
**kwargs : Any
    As tkinter.Tk (not used).

---- Globals read ----
WINDOW_REFUSAL (module constant).

---- Outputs ----
None. Always raises tkinter.TclError.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `pytest_configure`

```text
---- Summary ----
Main function to keep every window shut while the tests run, set before any test
is collected: plots are drawn off screen, no Tk window can open (a Toplevel without
its own window asks for a Tk one, so it cannot either), and on Windows every
program a test starts runs without a console window.

---- Inputs ----
config : pytest.Config
    pytest's settings (not used).

---- Globals read ----
HIDDEN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
os.environ['MPLBACKEND'], tkinter.Tk and, on Windows, subprocess.Popen, for this
run of the tests only; the programs the tests start draw their plots off screen
too.

---- Equations ----
None.

---- Helpers ----
_window_refuser
HiddenPopen
```

## `tests/test_app_updater.py`

Tests the Mac app's update: the newest release, the zip for each Mac and the swap with a

### HELPERS

#### `_app_maker`

```text
---- Summary ----
Helper function to make a made-up app: an Info.plist with its version, a stand-in
program, and a file that names the version.

---- Inputs ----
app : Path
    The .app folder to make.
version : str
    Its version, for example "1.0".

---- Globals read ----
None.

---- Outputs ----
Path
    The stand-in program inside the app (Contents/MacOS/Portimao).

---- Globals mutated ----
None. Writes the files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_closed_pid_giver`

```text
---- Summary ----
Helper function to give the process id of a program that has already closed, as
the app has by the time the swap goes on.

---- Inputs ----
None.

---- Globals read ----
HIDDEN (module constant).

---- Outputs ----
int
    The process id.

---- Globals mutated ----
None. Runs a short program (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_release_writer`

```text
---- Summary ----
Helper function to write a made-up answer of GitHub about its newest release, with
both zips pointing at one made-up zip.

---- Inputs ----
folder : Path
    Folder to write the answer in.
tag : str
    The release's tag, for example "V99.0".
zip_path : Path
    The made-up zip; it may not exist when nothing is downloaded.

---- Globals read ----
APPLE_SILICON_ZIP, INTEL_ZIP (imported constants).

---- Outputs ----
str
    The file:// address of the answer.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_swap_folder_maker`

```text
---- Summary ----
Helper function to make an old app in a stand-in Applications folder and a new one
in the update folder beside it, as the update leaves them before the swap.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
UPDATE_FOLDER_NAME (imported constant).

---- Outputs ----
Tuple[Path, Path, Path, Path]
    (the app, the new app, the update log, the file the stand-in open command
    makes).

---- Globals mutated ----
None. Writes the files (side effect).

---- Equations ----
None.

---- Helpers ----
_app_maker
```

### MAIN FUNCTIONS

#### `test_app_only_waits_for_a_newer_release`

```text
---- Summary ----
Main function to check that an app as new as the newest release starts as it is,
leaves itself alone and says so in its update log, and that a program run from
source never asks.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_app_maker
_release_writer
update_installer
user_places_finder
```

#### `test_ask_problem_is_described`

```text
---- Summary ----
Main function to check that each way of getting no answer from GitHub is said in
plain words, and that only GitHub's refusals are taken as refusals.

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
_ask_problem_describer
```

#### `test_failed_swap_keeps_the_app`

```text
---- Summary ----
Main function to check that when the new app cannot be moved in (here it is
missing), the old app is kept, still opened and the log says why.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SWAP_WAIT_S, SWAPPER_TEXT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_closed_pid_giver
_swap_folder_maker
swap_starter
```

#### `test_newer_release_is_found`

```text
---- Summary ----
Main function to check that versions are compared number by number, and that an
app whose version cannot be read never updates.

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
_newer_checker
```

#### `test_refused_ask_uses_the_release_page`

```text
---- Summary ----
Main function to check that when GitHub refuses the question, the app finds the
newest release from the Releases page instead, and starts as it is when that page
does not answer either; the reasons are in its update log.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Stands in for GitHub's two answers.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. The stand-ins last only for this test.

---- Equations ----
None.

---- Helpers ----
_app_maker
update_installer
user_places_finder
```

#### `test_release_answer_is_read`

```text
---- Summary ----
Main function to check that the version and the zips are read from GitHub's answer,
and that an answer of any other form is refused.

---- Inputs ----
None.

---- Globals read ----
APPLE_SILICON_ZIP (imported constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_release_reader
```

#### `test_release_page_address_is_read`

```text
---- Summary ----
Main function to check that the version is read from the address the Releases page
leads to, that both zips are found under its tag, and that any other address is
refused.

---- Inputs ----
None.

---- Globals read ----
APPLE_SILICON_ZIP, INTEL_ZIP (imported constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_release_page_reader
```

#### `test_swap_puts_the_new_app_in_place`

```text
---- Summary ----
Main function to check that the swap puts the new app in place of the old one,
deletes the old one, opens the app and writes it in the log.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SWAP_WAIT_S, SWAPPER_TEXT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_closed_pid_giver
_swap_folder_maker
swap_starter
```

#### `test_swap_waits_for_the_app_to_close`

```text
---- Summary ----
Main function to check that the swap leaves the app alone while it is still open,
and swaps it once it has closed.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SWAP_WAIT_S, SWAPPER_TEXT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_swap_folder_maker
swap_starter
```

#### `test_temporary_copy_cannot_update`

```text
---- Summary ----
Main function to check that an app macOS runs from a temporary copy says it cannot
replace itself, and that an app in a folder that can be written to can.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_app_maker
_blocker_finder
```

#### `test_unanswered_ask_is_asked_again`

```text
---- Summary ----
Main function to check that when GitHub does not answer, the app asks once more,
then starts as it is, with curl's own reason in its update log each time.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Takes away the wait before asking again.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. The change lasts only for this test.

---- Equations ----
None.

---- Helpers ----
_app_maker
update_installer
user_places_finder
```

#### `test_update_from_made_up_zip`

```text
---- Summary ----
Main function to check the whole update on a Mac: a made-up app V1.0 finds a
made-up release V99.0, downloads and unpacks its zip, and the swap puts V99.0 in
its place and opens it.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SWAP_WAIT_S (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_app_maker
_closed_pid_giver
_release_writer
update_installer
user_places_finder
```

## `tests/test_averaging_windows.py`

Tests that the averaging windows of both kinds (settled, ending before the next

### HELPERS

#### `_response_experiment_builder`

```text
---- Summary ----
Helper function to build an experiment whose oxygen consumption dips just after
each addition and then settles on another level, so the quick and the settled
windows give different averages.

---- Inputs ----
None.

---- Globals read ----
ADDITIONS, VO2_COLUMN (module constants); TIME_COLUMN.

---- Outputs ----
dict
    Experiment with a point every 0.25 min from 0 to 30 min and additions at 10
    and 20 min. VoO2 is 10 before 10 min, 4 from 10 to 12 min, 6 from 12 to
    20 min, 1 from 20 to 22 min and 2 from 22 min on.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_a_figure_asks_which_windows_only_with_both_kinds`

```text
---- Summary ----
Main function to check which kind of window a figure uses: with both kinds set up
one question (4.6.2) asks, offering the kind the figure used last time; with one
kind the figure uses it and nothing is asked. The question is stood in for.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Puts the stand-in for the question in place, and takes it away afterwards.

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
```

#### `test_a_figure_without_windows_offers_the_window_step`

```text
---- Summary ----
Main function to check what a figure that needs the averaging windows does: with
windows set up nothing is asked; with none, one question offers the window step of
the processing, and the figure is made only when windows are set up after it. No
window or gap is asked for by the figure itself. The question and the window step
are stood in for.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Puts the stand-in for the question in place, and takes it away afterwards.

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
```

#### `test_a_window_can_be_switched_off_and_set`

```text
---- Summary ----
Main function to check the values typed or ticked in the window step: a length or
a gap that can be used is taken, a length of 0 and a gap below 0 change nothing,
the tick box switches the windows off and on, and one change reaches every file.

---- Inputs ----
None.

---- Globals read ----
VALUES (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_a_pulled_end_gives_the_gap`

```text
---- Summary ----
Main function to check that the end of a window pulled to a time gives how long
before the next addition the windows end, in whole steps of 5 s and never below 0.

---- Inputs ----
None.

---- Globals read ----
The module constants.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
The ends that can be pulled are at 9.5 and 19.5 min (the last window's cannot).
Pulled to 19.0 min: the nearest is 19.5, before the addition at 20, so 1 min =
60 s. To 9.82 min: nearest 9.5, before the addition at 10, 0.18 min = 10.8 s ->
10 s. To 20.3 min: nearest 19.5, past its addition at 20, -18 s -> 0 s.

---- Helpers ----
None.
```

#### `test_a_pulled_quick_window_gives_its_start_and_length`

```text
---- Summary ----
Main function to check that the start of a quick window pulled to a time gives how
long after their addition the quick windows start (never below 0), and its end
their length (at least one step), in whole steps of 5 s.

---- Inputs ----
None.

---- Globals read ----
The module constants.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
The quick windows run from 10.5 to 11.5 and from 20.5 to 21.5 min. A start pulled
to 21.0 min: the nearest is 20.5, of the addition at 20, so 1 min = 60 s. To
10.07 min: nearest 10.5, addition at 10, 0.07 min = 4.2 s -> 5 s. To 9.8 min:
before its addition at 10, -12 s -> 0 s. An end pulled to 12.0 min: the nearest
is 11.5, of the window starting at 10.5, so 1.5 min = 90 s. To 21.93 min: nearest
21.5, starting at 20.5, 1.43 min = 85.8 s -> 85 s. To 20.51 min: nearest 21.5,
starting at 20.5, 0.6 s -> 0 -> one step, 5 s.

---- Helpers ----
None.
```

#### `test_a_pulled_start_gives_the_length`

```text
---- Summary ----
Main function to check that the start of a window pulled to a time gives the
length of the windows, in whole steps of 5 s and of at least one step, and that a
file without additions keeps the length it had.

---- Inputs ----
None.

---- Globals read ----
The module constants.

---- Outputs ----
None
    Nothing.

---- Equations ----
The starts are at 7.5, 17.5 and 27.5 min, the ends at 9.5, 19.5 and 29.5 min.
Pulled to 17.0 min: the nearest start is 17.5, of the window ending at 19.5, so
2.5 min = 150 s. To 27.93 min: nearest 27.5, ending at 29.5, 1.57 min = 94.2 s ->
95 s. To 19.49 min: nearest 17.5, ending at 19.5, 0.6 s -> 0 -> one step, 5 s.

---- Globals mutated ----
None.

---- Helpers ----
None.
```

#### `test_the_plot_shows_the_windows`

```text
---- Summary ----
Main function to check what the window step draws for a file: the start of every
window and the end of all but the last as edges, the first of each kind with its
words, the windows as blue parts and those that do not fit as red ones, and
nothing when the windows are unticked or the file has no additions.

---- Inputs ----
None.

---- Globals read ----
The module constants; PART_STYLES of the window.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
120 s and 30 s: windows 7.5 to 9.5, 17.5 to 19.5 and 27.5 to 29.5 min. 720 s
(12 min): the baseline 0 to 9.5 (cut at the start of the run, it fits), 7.5 to
19.5 (starts before its addition at 10) and 17.5 to 29.5 (before its addition at
20) do not fit.

---- Helpers ----
None.
```

#### `test_the_quick_windows_fall_after_the_additions`

```text
---- Summary ----
Main function to check where the quick windows of a file fall and which do not
fit, what a figure that uses one kind of window is given, and how the windows that
do not fit are named.

---- Inputs ----
None.

---- Globals read ----
The module constants.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Starting 0.5 min after the addition and 1 min long: 10 + 0.5 = 10.5 to 11.5, and
20 + 0.5 = 20.5 to 21.5. 12 min long: 10.5 to 22.5 ends after the addition at 20,
and 20.5 to 32.5 after the end of the run at 30, so neither fits. Starting at the
addition and 10 min long: 10 to 20 and 20 to 30 end exactly at the next addition
and at the end of the run, so both fit.

---- Helpers ----
None.
```

#### `test_both_kinds_are_averaged_from_one_baseline`

```text
---- Summary ----
Main function to check the averages of the settled and the quick windows of one
file, their change from the one baseline, what a figure that uses one kind reads,
and the averaged spectra of the quick windows.

---- Inputs ----
None.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
The trace is 10 before 10 min, 4 until 12, 6 until 20, 1 until 22 and 2 after.
Baseline 7.5 to 9.5: 10. Settled windows 17.5 to 19.5 and 27.5 to 29.5: 6 and 2,
so 60 and 20 % of the baseline, -4 and -8 from it. Quick windows 10.5 to 11.5 and
20.5 to 21.5: 4 and 1, so 40 and 10 %, -6 and -9. Spectra, one every 0.5 min for
12 min with additions at 4 and 8 min: (2, 0) before 4 min, (5, 1) until 6, (3, 1)
until 8, (9, 4) until 10 and (7, 4) after; the quick windows 4.5 to 5.5 and 8.5
to 9.5 hold three spectra each, (5, 1) and (9, 4), where the settled ones would
give (3, 1) and (7, 4).

---- Helpers ----
_response_experiment_builder
```

#### `test_the_windows_fall_before_the_additions`

```text
---- Summary ----
Main function to check where the windows of a file fall and which do not fit: the
baseline before the first addition, one window before each later addition and one
before the end of the run.

---- Inputs ----
None.

---- Globals read ----
The module constants.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
2 min and 0.5 min: baseline 10 - 0.5 = 9.5, from 7.5; then 20 - 0.5 = 19.5, from
17.5; then 30 - 0.5 = 29.5, from 27.5. 12 min: the baseline would start at -2.5,
so at 0; 19.5 - 12 = 7.5 is before the addition at 10, and 29.5 - 12 = 17.5 is
before the addition at 20, so neither fits. A first addition at 0.6 min: the
baseline runs from 0 to 0.1 min, 6 s, less than the 10 s it needs.

---- Helpers ----
None.
```

## `tests/test_dataset_settings.py`

Tests of the settings kept with a dataset, the results folder check and the list of data

### HELPERS

#### `_program_folder_maker`

```text
---- Summary ----
Helper function to make a pretend program folder: two folders with .paf files, one
without, one hidden work folder with a .paf file, and a loose .paf file.

---- Inputs ----
root : Path
    Empty folder to fill.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Writes the folders and files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_broken_settings_file_gives_nothing`

```text
---- Summary ----
Main function to check that a settings file that is not readable JSON, or is not a
dictionary, gives no settings, so the standard ones are used.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SETTINGS_FILE_NAME (imported).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_data_folders_are_listed`

```text
---- Summary ----
Main function to check that only the folders holding .paf files are listed, in
natural order (2 hours before 10 hours), without the folders starting with an
underscore.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_program_folder_maker
```

#### `test_folder_answer_is_resolved`

```text
---- Summary ----
Main function to check the three ways of answering the folder question: a number
from the list, a name from the list (capitals do not matter), or another path; a
number that is not in the list is taken as a path.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_program_folder_maker
```

#### `test_missing_settings_file_gives_nothing`

```text
---- Summary ----
Main function to check that a dataset never saved gives no settings.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

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
```

#### `test_od_values_and_labels_are_kept`

```text
---- Summary ----
Main function to check that the OD values and event labels of a run are kept in the
dataset's settings beside its limits and offered back from there: an OD not asked
this run (no OD scaling) stays as saved, a file not in this run is kept, and the
values are written as plain numbers and text.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
FILES, ANSWERS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_results_folder_inside_is_kept_relative`

```text
---- Summary ----
Main function to check that a results folder inside the dataset folder is written
relative to it, so the settings still hold after the dataset is copied: the copy
gives the results folder inside the copy.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SETTINGS_FILE_NAME (imported).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_results_folder_is_checked`

```text
---- Summary ----
Main function to check the results folder answer: a file, or a folder under a file,
is refused with one sentence; an existing folder and one not made yet are accepted,
and checking leaves nothing behind.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

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
```

#### `test_results_folder_names_and_old_results`

```text
---- Summary ----
Main function to check the results folder answer against the data folder: a name
without a path is taken inside the data folder and a full path as it is; the files
that already have results there are counted (an empty folder of one does not
count); and the free name offered beside a folder skips the names already used.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

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
```

#### `test_results_folder_outside_is_kept_whole`

```text
---- Summary ----
Main function to check that a results folder outside the dataset folder is written
and read back as its full path.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

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
```

#### `test_regions_are_kept_with_the_dataset`

```text
---- Summary ----
Main function to check that the oxidised and the reduced region of each file are
saved with the dataset and read back: a lone region is kept as it was left, a file
with neither region chosen has none saved (one saved before is cleared), a file
not in this run keeps its own, and a run that did not handle the regions leaves
those saved before.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
FILES, ANSWERS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_saved_haem_amounts_open_as_delta_d`

```text
---- Summary ----
Main function to check that, with only cells measured, the haem amounts are not
offered as a way of showing the haems, that % oxidised is offered only when asked
for, and that a dataset saved showing the amounts opens showing delta D, the other
answers unchanged.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
FILES, ANSWERS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_settings_are_read_back`

```text
---- Summary ----
Main function to check that the trim and ignore times and the answers saved with a
dataset are read back unchanged.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
FILES, ANSWERS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_unwritable_folder_is_reported`

```text
---- Summary ----
Main function to check that saving into a folder that is not there says so (False)
and does not raise.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

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
```

## `tests/test_delta_psi.py`

Tests that delta psi from the b haems comes out as worked out by hand on made-up data.

### DELTA PSI TEST HELPERS

#### `_calculator`

```text
---- Summary ----
Helper function to work out delta psi with the numbers of the method, any of them
changed by name.

---- Inputs ----
percent_bH : list
    % oxidised of bH.
percent_bL : list
    % oxidised of bL.
**changes : object
    midpoints_mV, share, temperature_c or limits_percent, in place of the
    standard ones.

---- Globals read ----
MIDPOINTS_MV, SHARE, TEMPERATURE_C, LIMITS_PERCENT.

---- Outputs ----
dict
    What delta_psi_calculator gives.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_delta_psi_is_empty_outside_the_limits`

```text
---- Summary ----
Main function to check that delta psi is given only where bH and bL are both
between 10 and 90 % reduced, the limits themselves counted, and is left empty for
a blank value.

---- Inputs ----
None.

---- Globals read ----
EQUAL_PERCENT.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
90 % oxidised is 10 % reduced and 10 % oxidised is 90 % reduced: both kept. 90.5
and 9.5 % oxidised are 9.5 and 90.5 % reduced: left out, whichever haem it is.
105 % oxidised (above the oxidised level) is -5 % reduced: left out.

---- Helpers ----
_calculator
```

#### `test_equal_haems_at_their_midpoints_give_120_mV`

```text
---- Summary ----
Main function to check the first example of MATHS.md: bH and bL both 65.0858 %
oxidised at 37 °C sit at their midpoints, +40 and -20 mV, which is 120 mV of
membrane potential.

---- Inputs ----
None.

---- Globals read ----
EQUAL_PERCENT, FACTOR.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
R_H = R_L = 1 - 0.650858 = 0.349142. With k = 0.072868: n = h = l = 1 / (3 + k)
= 0.325429 and b = k / (3 + k) = 0.023713 (h + b = 0.349142). E_H = 40 - s x
ln(h / n) = 40 - 0 = 40 mV; E_L = -20 - 0 = -20 mV; delta psi = 60 / 0.5 = 120 mV.
With a share of 1 it is 60 mV.

---- Helpers ----
_calculator
```

#### `test_numbers_that_cannot_be_used_are_refused`

```text
---- Summary ----
Main function to check that numbers of the method that would give a wrong delta
psi are refused with a sentence saying which: midpoints whose two drops differ, a
missing midpoint, a share of 0, a temperature below absolute zero, and limits in
the wrong order.

---- Inputs ----
None.

---- Globals read ----
MIDPOINTS_MV.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
With bL's second midpoint at -80 mV its drop is -20 + 80 = 60 mV, and bH's is
40 + 30 = 70 mV.

---- Helpers ----
_calculator
```

#### `test_the_b_haems_are_found_by_name`

```text
---- Summary ----
Main function to check that the delta psi table is built from the bH and the bL
column however they are written, with b557 and the other haems left alone, and
that a file without one of the two has no table.

---- Inputs ----
None.

---- Globals read ----
EQUAL_PERCENT, UNEQUAL_PERCENT_BH, UNEQUAL_PERCENT_BL, UNEQUAL_DELTA_PSI_MV,
MIDPOINTS_MV, SHARE, TEMPERATURE_C, LIMITS_PERCENT.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Three spectra: the first example (120 mV), the second (173.453 mV), and one with
bH 100 % oxidised (0 % reduced, below the limit: empty).

---- Helpers ----
None.
```

#### `test_the_numbers_the_program_starts_with`

```text
---- Summary ----
Main function to check that the program starts with the numbers of the method
written in MATHS.md, with delta psi switched off, and that the voltage that goes
with a temperature is the one worked out by hand.

---- Inputs ----
None.

---- Globals read ----
MIDPOINTS_MV, SHARE, TEMPERATURE_C, LIMITS_PERCENT, THERMAL_MV, FACTOR;
config.DEFAULT_ANSWERS, config.DELTA_PSI_MIDPOINT_ANSWERS,
config.DELTA_PSI_LIMIT_ANSWERS.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
s = 8.314462618 x (37 + 273.15) / 96485.33212 x 1000 = 26.72666 mV; at 25 °C,
8.314462618 x 298.15 / 96485.33212 x 1000 = 25.69258 mV. k = exp(-70 / 26.72666)
= exp(-2.619108) = 0.072868.

---- Helpers ----
None.
```

#### `test_the_kept_delta_psi_is_drawn_dashed`

```text
---- Summary ----
Main function to check the Δψ kept to compare with on the plot of one file: a
second line in the Δψ panel, dashed and paler, the panel widened to hold it outside
the ignored parts, and the gap between the two worked out by hand; and one
sentence in place of the line for a file with no kept Δψ.

---- Inputs ----
None.

---- Globals read ----
DELTA_PSI_COLUMN, SPECTRUM_INDEX_COLUMN, TIME_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Six spectra, one a minute. In use: empty, 100, 110, 120, 130, empty (mV). Kept:
empty, empty, 115, 110, 150, 140. Both have a value in the 3rd, 4th and 5th: the
gaps are 5, 10 and 20 mV, so the largest is 20 and the average 35 / 3 = 11.7 mV.
The kept line runs from 110 to 150 mV: with 5 % of that range (2 mV) left free,
the panel reaches up to 152 mV. With the last 1.5 min ignored only 115 and 110 mV
count, which the panel already holds, so it stays as it was.

---- Helpers ----
experiment_drawer
```

#### `test_the_kept_regions_and_numbers_work_the_file_out`

```text
---- Summary ----
Main function to check that a file is worked out again for the comparison with
the kept regions and the kept numbers of Δψ, not the ones in use, and with
everything else as in use. The reading and the processing are stood in for.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Pytest's tool for standing in for the reading and the processing.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. The stand-ins are undone after the test.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_the_panel_is_drawn_only_for_a_file_with_delta_psi`

```text
---- Summary ----
Main function to check the Δψ panel of the plot of one file: the lowest panel, one
line with gaps where Δψ is empty, and no panel for a file without Δψ or when the
figure does not ask for it.

---- Inputs ----
None.

---- Globals read ----
DELTA_PSI_COLUMN, TIME_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
experiment_drawer
```

#### `test_the_processing_keeps_delta_psi_when_switched_on`

```text
---- Summary ----
Main function to check that the processing of a file works out delta psi from its
% oxidised when delta psi is switched on, and nothing when it is off or when the
file has no regions, and that a share and a limit typed in place of the paper's
are the ones used.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Pytest's tool for standing in for the decomposition.

---- Globals read ----
EQUAL_PERCENT; TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Sixty spectra, one every 0.5 min. bH is 12 mOD before 10 min and 4 mOD from 20
min; bL is 20 and 10 mOD. Regions: oxidised 0 to 6 min, reduced 22 to 28 min, so
D_ox = 12 and D_red = 4 for bH, 20 and 10 for bL. From 10 to 20 min both are
65.0858 % oxidised: bH = 4 + 8 x 0.650858 = 9.206864 mOD, bL = 10 + 10 x 0.650858
= 16.50858 mOD, which is 120 mV. Before 10 min both are 100 % oxidised and after
20 min 0 %: outside the limits, so empty. With a share of 0.4 typed, the same 60 mV
between the haems is 60 / 0.4 = 150 mV. With a lowest limit of 40 % reduced typed,
both haems (34.9142 % reduced from 10 to 20 min) are under it, so every spectrum
is empty.

---- Helpers ----
None.
```

#### `test_the_question_is_asked_only_when_delta_psi_can_be_worked_out`

```text
---- Summary ----
Main function to check when "Do you want to work out Δψ?" is asked: only with both
regions on at least one file and a fit with one bH and one bL. Otherwise nothing is
asked and the run has no Δψ.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the question, so nothing is read from the terminal.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
delta_psi_asker
delta_psi_offer_checker
```

#### `test_unequal_haems_give_173_mV`

```text
---- Summary ----
Main function to check the second example of MATHS.md: bH 75.6308 % and bL
40.6805 % oxidised at 37 °C give 173.453 mV, and a warmer sample a little more.

---- Inputs ----
None.

---- Globals read ----
UNEQUAL_PERCENT_BH, UNEQUAL_PERCENT_BL, UNEQUAL_DELTA_PSI_MV, FACTOR, THERMAL_MV.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
R_H = 0.243692, R_L = 0.593195. Out of 2 + e + e x k = 2 + 2.718282 + 0.198075 =
4.916357: n = h = 0.203403, l = 2.718282 / 4.916357 = 0.552906, b = 0.198075 /
4.916357 = 0.040289 (h + b = 0.243692, l + b = 0.593195, b x n / (h x l) =
0.072868). E_H = 40 - s x ln(1) = 40 mV; E_L = -20 - s x ln(e) = -20 - 26.727 =
-46.727 mV; delta psi = 86.727 / 0.5 = 173.453 mV.

---- Helpers ----
_calculator
```

## `tests/test_file_names.py`

Tests of the one rule that cleans every file name the program writes.

### MAIN FUNCTIONS

#### `test_dots_and_spaces_at_the_ends_go`

```text
---- Summary ----
Main function to check that dots and spaces at either end of a name are taken off,
and that those inside it stay.

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
```

#### `test_forbidden_characters_become_underscores`

```text
---- Summary ----
Main function to check that each character a file name cannot hold on Windows, Mac
or Linux becomes an underscore, and that other characters (µ, brackets) stay.

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
```

#### `test_nothing_left_gives_the_default`

```text
---- Summary ----
Main function to check that a name with nothing left after cleaning gives the
default, which may be empty so the caller can ask again.

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
```

## `tests/test_haem_decomposition.py`

Tests that the haem decomposition gives back the amounts a spectrum was built from,

### HELPERS

#### `_background_builder`

```text
---- Summary ----
Helper function to build the scatter background shape: it falls with wavelength
from 1 at the shortest to 0 at the longest.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths (nm), shape (n_wavelengths).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The shape, shape (n_wavelengths).

---- Globals mutated ----
None.

---- Equations ----
(1/wl - min(1/wl)) / (max(1/wl) - min(1/wl)).

---- Helpers ----
None.
```

#### `_background_shape_builder`

```text
---- Summary ----
Helper function to write out, by hand and in other units than the program's, the
shapes a background of the program must be able to fit beside a flat level.

---- Inputs ----
background : str
    Name of the background, as the program names it.
wavelengths : np.ndarray
    Wavelengths (nm), shape (n_wavelengths).

---- Globals read ----
None.

---- Outputs ----
list
    The shapes, each of shape (n_wavelengths).

---- Globals mutated ----
None.

---- Equations ----
x = wl / 100 nm. scatter_1: 1/x; scatter_2: 1/x and 1/x^2; linear: x - 5.5;
rowan_scatter: x - 5.5 and (x - 6)^2, a curve with its bottom off the middle;
valencia: 1/x^2.

---- Helpers ----
None.
```

#### `_file_values_reader`

```text
---- Summary ----
Helper function to read the shape values of a fit file in the layout with heading
lines exactly as they are written in it, before any unit or way up is applied.

---- Inputs ----
path : Path
    The fit file.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The values, shape (n_rows, n_haems), NaN below a shorter haem.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None. The table starts at the first line after the first empty line: the haem
names, the row saying what each column holds, then the numbers.

---- Helpers ----
None.
```

#### `_haem_spectrum_builder`

```text
---- Summary ----
Helper function to build one spectrum from known amounts of the five haems of the
test fit file, on a flat and a sloping background.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, FIT_ORDER, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

---- Outputs ----
Tuple[np.ndarray, np.ndarray, np.ndarray]
    (wavelengths in nm, the spectrum, the haem shapes as columns in FIT_ORDER); the
    wavelengths are those of the fit file.

---- Globals mutated ----
None. Reads the fit file (side effect).

---- Equations ----
spectrum = sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x background.

---- Helpers ----
_background_builder
```

#### `_mixed_spectra_builder`

```text
---- Summary ----
Helper function to build two files of 20 spectra each, every spectrum mixed from
the same two shapes in its own amounts, on its own flat and sloping background,
with a little noise. The second file also has a fixed extra bump in every spectrum,
as a different preparation would.

---- Inputs ----
None.

---- Globals read ----
SEED, PEAKS_NM, WIDTHS_NM (module constants).

---- Outputs ----
Tuple[np.ndarray, np.ndarray, list]
    (wavelengths 500 to 650 nm in 1 nm steps, the two shapes as columns, the two
    files as the component finder takes them).

---- Globals mutated ----
None.

---- Equations ----
shape = exp(-0.5 ((wl - peak) / width)^2); spectrum = a x shape_1 + b x shape_2 +
offset + slope x background + noise (SD 0.0001), a and b between 0 and 1.

---- Helpers ----
_background_builder
```

#### `_series_decomposer`

```text
---- Summary ----
Helper function to decompose, with a given fit, a run of four spectra holding 1, 4,
3 and 2 times the known amounts of the five haems of the test fit file.

---- Inputs ----
fit : dict
    Fit dictionary from fit_importer, holding the five haems of the test fit file.
is_change_from_first : bool
    True fits the change of each spectrum from the first.

---- Globals read ----
HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

---- Outputs ----
dict
    The experiment, with its haem amounts, absorbances and changes.

---- Globals mutated ----
None.

---- Equations ----
spectrum k = multiple_k x sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x
background.

---- Helpers ----
_background_builder
_haem_spectrum_builder
```

### MAIN FUNCTIONS

#### `test_blank_rows_do_not_change_the_shapes`

```text
---- Summary ----
Main function to check that a fit file whose haems have different lengths is read
the same wherever the blank rows of the shorter haem are: at the bottom, or between
its numbers.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Writes two small fit files in tmp_path (side effect).

---- Equations ----
Haem a has five rows (500 to 540 nm); haem b has three (505, 515, 525 nm; 4e-5,
5e-5, 6e-5). Both files must give b as those three rows at the top, with two
blank rows below.

---- Helpers ----
None.
```

#### `test_leftover_rows_are_left_out`

```text
---- Summary ----
Main function to check that a haem whose column ends in leftover rows (rows of
another haem, whose wavelengths jump backwards) gives the same amounts as the same
haem ending in blanks, that these are the amounts the spectrum was built from, and
that the user is told which rows were left out.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes two fit files in tmp_path (side effect).

---- Equations ----
The second haem of the test fit (400 to 700 nm in 1 nm steps) is ended at 650 nm
(row 251). In one file the 50 rows below are blank; in the other they hold the
last haem's rows of 420 to 469 nm, so the wavelength jumps from 650 back to 420.
The haems then share 400 to 650 nm, where the spectrum still holds AMOUNTS.

---- Helpers ----
_haem_spectrum_builder
```

#### `test_downward_wavelengths_are_turned_round`

```text
---- Summary ----
Main function to check that a fit file written from the longest wavelength to the
shortest is read as the same fit written the usual way.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
FIT_FILE (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_unusable_fit_files_are_refused`

```text
---- Summary ----
Main function to check that a fit file that cannot give a shape is refused with a
message that says what is wrong and where: columns not in pairs, a haem with no
name, a cell that is not a number, a wavelength with no response, a haem of one
row, and an empty file.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.
text : str
    Contents of the fit file.
message : str
    Words the message must hold.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
The first row of a file is its header, so the second row of numbers is row 3.

---- Helpers ----
None.
```

#### `test_a_million_times_larger_fit_gives_the_same_amounts`

```text
---- Summary ----
Main function to check that the same fit written a million times larger gives the
same raw amounts, absorbances and changes, and says that it was divided; and that
a fit on neither scale is used as it is, with a warning.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
FIT_FILE, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes two fit files in tmp_path (side effect).

---- Equations ----
The shapes of the test fit have peaks of 1e-5 (the standard scale). Times 1e6 the
peaks are 10: a million above the standard, so divided by 1e6. Times 1e3 they are
0.01: on neither scale (the standard ends at 1e-3, the large one starts at 0.1).

---- Helpers ----
_series_decomposer
```

#### `test_every_fit_file_is_read`

```text
---- Summary ----
Main function to check that every file of the haem library is in the layout with
heading lines, in OD/mM/cm, holds one haem, and is read without an error or a note,
with wavelengths that go upwards, on the standard scale; that every fit offered (the
presets, and any fit file shipped in the fits folder itself) is read the same way;
and that every library file is in a preset. Leftover rows and the million scale of
the older layout are tested on made-up files.

---- Inputs ----
None.

---- Globals read ----
FITS_FOLDER, UNIT_DIVISORS (module constants); HAEMS_FOLDER_NAME.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Standard scale: the highest point of the shapes lies between 1e-7 and 1e-3.

---- Helpers ----
None.
```

#### `test_haem_names_go_to_figure_form_and_back`

```text
---- Summary ----
Main function to check that a plain haem name is put in the form the figures draw
(haem letters in italics, a capital letter or number after them below the line),
that other words are left alone, and that the figure form gives the plain name
back.

---- Inputs ----
plain : str
    The name as a fit file writes it.
figure : str
    The name the figures draw, written out by hand.

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
```

#### `test_a_fit_file_reads_back_the_same_in_each_unit`

```text
---- Summary ----
Main function to check that the test fit, written in the layout with heading lines
in one of the units, holds its shapes in that unit and is read back as the same
shapes, names in figure form and amounts.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.
unit : str
    The unit written.

---- Globals read ----
FIT_FILE, UNIT_DIVISORS, ROUND_TRIP, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
The shapes of the test fit are on the standard scale (OD/mM/cm divided by a
million), so the file holds them x 1e6 in OD/mM/cm, x 1e3 in OD/µM/cm and x 1 in
OD/nM/cm.

---- Helpers ----
_file_values_reader
_series_decomposer
```

#### `test_reduced_minus_oxidised_is_turned_over`

```text
---- Summary ----
Main function to check that a fit file whose Way up line says 'reduced minus
oxidised' holds its shapes upside down and is turned over when read, so it gives
the same shapes as the same fit written the way the decomposition uses them.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
FIT_FILE, UNIT_DIVISORS, ROUND_TRIP (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
value written = -shape x 1e6 (OD/mM/cm).

---- Helpers ----
_file_values_reader
```

#### `test_a_single_haem_file_reads_back_the_same`

```text
---- Summary ----
Main function to check that a fit file holding one haem only is written and read
back as that haem.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
FIT_FILE, ROUND_TRIP (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_wrong_headed_fit_files_are_refused`

```text
---- Summary ----
Main function to check that a fit file in the layout with heading lines is refused
with a message that says what is wrong and where: no format, a newer format, no
Unit line, an unknown unit, an unknown way up, no row saying what the columns
hold, no table, and a cell that is not a number (named by its row in the file).

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.
text : str
    Contents of the fit file.
message : str
    Words the message must hold (a regular expression).

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
In the last file the lines are: the format, the unit, an empty line, the names,
the row saying what the columns hold, then '1,2' and 'x,3': the x is in row 7.

---- Helpers ----
None.
```

#### `test_saved_components_read_back_the_same`

```text
---- Summary ----
Main function to check that components found by the component finder and saved as
a fit file hold their shapes as found (largest point 1, unit 'relative') and are
read back as the same fit.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
ROUND_TRIP (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
value written = response x 1e6 = the component as found, whose largest point is 1.

---- Helpers ----
_file_values_reader
_mixed_spectra_builder
```

#### `test_one_spectrum_gives_its_amounts_back`

```text
---- Summary ----
Main function to check that a spectrum built from known amounts of each haem and a
known background decomposes into those amounts and that background, with nothing
left over.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
See _haem_spectrum_builder: the amounts found must be AMOUNTS, then OFFSET, then
SLOPE.

---- Helpers ----
_haem_spectrum_builder
```

#### `test_a_series_gives_its_amounts_back`

```text
---- Summary ----
Main function to check that a run of four spectra holding 1, 4, 3 and 2 times the
known amounts decomposes into those amounts, and that the haem absorbances and
their change from the start follow from them.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE (module constants); TIME_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
amount of haem i in a spectrum = its multiple x AMOUNTS_i; absorbance (mOD) =
amount x highest point of |shape_i| x HAEM_FACTOR x 1000; change = absorbance - the
absorbance of that haem at the start (the first spectrum), so it is 0 there and 3,
2 and 1 times the first absorbance after it. The start is taken from one spectrum
here, as the run has only four.

---- Helpers ----
_background_builder
_haem_spectrum_builder
```

#### `test_the_three_routes_give_the_same_amounts`

```text
---- Summary ----
Main function to check that the three places that decompose a spectrum (one
spectrum, a whole run, the component finder's examples) give the same amounts for
the same spectrum, and that these are the amounts it was built from. It guards the
one shared solver: never loosen it.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
See _haem_spectrum_builder. The component finder gives each shape's part of the
spectrum (amount x shape), so its amount is the best fit of that part to the shape:
sum(part x shape) / sum(shape^2).

---- Helpers ----
_haem_spectrum_builder
```

#### `test_same_shapes_give_a_plain_error`

```text
---- Summary ----
Main function to check that a fit file in which two haems have the same shape is
refused with a message that says so, and not with the raw "Singular matrix".

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_haem_spectrum_builder
```

#### `test_a_failed_decomposition_leaves_nothing`

```text
---- Summary ----
Main function to check that a decomposition that fails at its last step (the whole
run is ignored, so the zero of the change cannot be found) leaves no haem amounts,
absorbances or changes in the experiment, not even those of an earlier
decomposition.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The run lasts 1 min and its first 10 min are ignored, so nothing is left.

---- Helpers ----
_haem_spectrum_builder
```

#### `test_delta_d_zero_is_where_the_haem_starts`

```text
---- Summary ----
Main function to check that the zero of delta D is where the haem starts: the
median of its first spectra after the ignored start, so that neither one spike nor
a higher stretch later in the run sets it; that a blank value is made up for by the
next spectrum; and that a run with too few spectra left is refused in place of
taking the zero from too few.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Absorbances 12, 30, 11, 9.5, 4, 5, 20, 20 at 0 to 7 min, the start taken from three
spectra. The first three are 12, 30, 11; in order 11, 12, 30, so their median is 12
and delta D = absorbance - 12: 0, 18, -1, -2.5, -8, -7, 8, 8. The spike of 30 is
not the zero, and nor is the stretch of 20 at the end (the highest three in a row,
5, 20, 20, have a median of 20). Three spectra one minute apart last 180 s.
With the first minute ignored the first three are 30, 11, 9.5 (1 to 3 min): median
11. With the value at 1 min blank they are 12, 11, 9.5 (0 to 3 min): median 11.
Nine spectra are not to be had from eight; with the last 6 min ignored only the
spectra at 0 and 1 min are left, fewer than three.

---- Helpers ----
None.
```

#### `test_the_gap_between_two_decompositions`

```text
---- Summary ----
Main function to check the largest and the average gap between the haem traces of
two decompositions: the spectra are matched by their index, not their row; a haem
is matched by its plain name; a haem in only one of them, and a spectrum with no
value, are left out; a table without the spectrum index is refused.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
bL new 1.0, 2.0, 3.0 and kept 1.0, 1.5, 3.5 (spectra 1 to 3): gaps 0, 0.5, -0.5,
so the largest is 0.5 and the average (0 + 0.5 + 0.5) / 3 = 1/3. Cyt cc new 4.0,
4.0, 4.0 and kept 3.0, (no value), 5.0: gaps 1 and -1, so both are 1. The kept
table lists its spectra in the order 3, 1, 2.

---- Helpers ----
None.
```

#### `test_each_background_gives_back_the_amounts`

```text
---- Summary ----
Main function to check that a spectrum built from known amounts of each haem on a
background of one kind decomposes, with that background, into those amounts and
that background, with nothing left over.

---- Inputs ----
background : str
    Name of the background, as the program names it.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
spectrum = sum(amount_i x shape_i) x HAEM_FACTOR + OFFSET + SLOPE x each shape of
the background (_background_shape_builder). The amounts found must be AMOUNTS, and
the background found the part of the spectrum that is not haem.

---- Helpers ----
_background_shape_builder
_haem_spectrum_builder
```

#### `test_an_unknown_background_is_refused`

```text
---- Summary ----
Main function to check that a background the program does not know is refused with
a message that names it and the ones it knows, and that the standard background in
config.py is one it knows.

---- Inputs ----
None.

---- Globals read ----
BACKGROUNDS (module constant); settings.DEFAULT_ANSWERS.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_the_background_answered_is_the_one_used`

```text
---- Summary ----
Main function to check that the processing of a file decomposes its haems with the
background named in the dataset's answers, not the standard one.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the attenuation and the decomposition, so no file is read.

---- Globals read ----
FIT_FILE (module constant); settings.DEFAULT_ANSWERS.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_rowan_scatter_is_the_chamber_scripts_background`

```text
---- Summary ----
Main function to check that the background called Rowan scatter is the additive
background of the lab's own chamber scripts: their lines build the same terms, and
a spectrum that neither can fit exactly gives the same haem amounts and the same
leftover with both.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The scripts' terms over the fitted wavelengths cw, as their lines write them (only
their basis S is called s_array here): blank = 1; scatter2 = cw, and scatter3 =
(cw - centre)^2 with centre = (cw[0] + cw[-1]) / 2, each scaled as (f - min f) /
max(f - min f). Their amounts are the least-squares solution of [haem shapes x
HAEM_FACTOR, blank, scatter2, scatter3]. The spectrum's background, OFFSET + SLOPE
/ x^2 (x = wl / 100 nm), is not of that kind, so about 3e-5 OD is left over.

---- Helpers ----
_haem_spectrum_builder
```

#### `test_some_haems_only_give_back_their_amounts`

```text
---- Summary ----
Main function to check that a fit can keep only some of its haems: they are kept in
the order of the file, a spectrum built from them alone decomposes into their
amounts, leaving out a short haem widens the wavelengths used, the fit given is not
changed, and naming no haem or one the fit does not hold is refused.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, OFFSET, SLOPE, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
The test fit runs from 400 to 700 nm in 1 nm steps; Cyt cc is ended at 650 nm (row
251), so the five haems share 400 to 650 nm and the four others 400 to 700 nm.
spectrum = AMOUNTS of Cyt cc and Cyt bL only x their shapes x HAEM_FACTOR + OFFSET
+ SLOPE x background.

---- Helpers ----
_background_builder
_haem_spectrum_builder
```

#### `test_the_change_from_the_first_spectrum`

```text
---- Summary ----
Main function to check that fitting the change of each spectrum from the first, as
the instrument does, gives each amount and absorbance minus that of the first
spectrum, and the same change from the start (delta D) as fitting the spectra
themselves; and that a first spectrum with a blank value is refused.

---- Inputs ----
None.

---- Globals read ----
FIT_FILE, HAEM_FACTOR, AMOUNTS, EXACT (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The run holds 1, 4, 3 and 2 times AMOUNTS (_series_decomposer), so its changes from
the first spectrum are 0, 3, 2 and 1 times AMOUNTS; absorbance = amount x highest
point of |shape_i| x HAEM_FACTOR x 1000.

---- Helpers ----
_haem_spectrum_builder
_series_decomposer
```

#### `test_two_mixed_shapes_give_two_components`

```text
---- Summary ----
Main function to check that spectra mixed from two shapes give two components and
no more: the third is only noise, two is the number suggested, and a fixed bump in
one file does not become a component.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The noise (SD 0.0001) is about a thousandth of the changes of the shapes, so the
third component must hold less than a ten-thousandth of the variance of the second.

---- Helpers ----
_mixed_spectra_builder
```

#### `test_component_names_must_differ`

```text
---- Summary ----
Main function to check that the components found cannot be turned into a fit under
names that would break it once saved (the same name twice, an empty name, a comma,
too few names), and that proper names and no names both give a fit.

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
_mixed_spectra_builder
```

#### `test_the_two_shapes_are_found_again`

```text
---- Summary ----
Main function to check that the two components found are the two shapes the
spectra were mixed from: each shape can be rebuilt from the components (once its
own flat and sloping part is taken off, as the finder does), and the components
have their peaks where the shapes have theirs.

---- Inputs ----
None.

---- Globals read ----
PEAKS_NM (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
cleaned shape = shape - its best fit of (1, background); left over = cleaned shape
- its best fit of the two components; the left over must be under 1 % of the
cleaned shape (root of the summed squares).

---- Helpers ----
_background_builder
_mixed_spectra_builder
```

## `tests/test_haem_direction.py`

Tests that our haem amounts move the same way as the instrument's own haem traces of

### HELPERS

#### `_instrument_fit_reader`

```text
---- Summary ----
Helper function to read the shapes of the instrument software's own fit file
(.fit), which is made of the same kind of records as a .paf.

---- Inputs ----
path : Path
    The .fit file.

---- Globals read ----
MARK, POINTS_MARK (module constants).

---- Outputs ----
dict
    {'range_nm': (first, last) wavelength the instrument fits over, 'labels': the
    name of each shape in the instrument's list of traces ('Noname' for a shape
    that gives no trace), 'names': the name each shape was saved under, 'shapes':
    one array per shape, shape (n_points, 2): wavelength (nm), then the value, both
    as the instrument uses them (shifted and scaled), 'shifts_nm' and 'scales':
    the shift and the scale that were applied to the saved points}; the lists are
    in the file's order.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
The first record gives the fit name, then 1, the range (two 4 byte numbers), the
number of shapes and their labels. Each shape is a 'Plot: Scatter' record (its
name) followed by a record that holds its points: the numbers 30, 15, 10, then 20
bytes, then the points as (wavelength, value) pairs of 4 byte numbers; the number
of points is 32 bytes before the 30. The points are stored as they were imported.
The 'Plot: Scatter' record ends with the shape as the instrument uses it: its
first and last wavelength and its lowest and highest value (four 4 byte numbers,
28 bytes before its end). shift = that first wavelength - the first stored one
(when both spans are equally wide); scale = (highest - lowest) / (the same of the
stored values in that span), negative when the shape is used upside down.

---- Helpers ----
None.
```

#### `_haem_trace_loader`

```text
---- Summary ----
Helper function to decompose the example run once, as the program does, and to
read the instrument's own haem traces of the same run.

---- Inputs ----
None.

---- Globals read ----
PAF_FILE, FITS_FOLDER, HAEM_TRACES (module constants); settings.STANDARD_FIT.

---- Outputs ----
dict
    {'ours': {haem name: our amount at each spectrum}, 'theirs': {haem name: the
    instrument's trace at each spectrum}}; every array has shape (n_spectra).

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_haem_amounts_move_with_the_instrument`

```text
---- Summary ----
Main function to check that our amount of a haem rises where the instrument's own
trace of it rises, and falls where it falls, over the whole run.

---- Inputs ----
haems : dict
    Our amounts and the instrument's traces, from _haem_trace_loader.
name : str
    Name of the haem in our fit file.

---- Globals read ----
SAME_WAY (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Correlation of the two traces over the spectra where both have a value: +1 when
they move together, -1 when one is the other upside down. The size and the zero
of the two differ (other units, other fit shapes), which the correlation ignores.

---- Helpers ----
None.
```

#### `test_haem_amounts_fall_when_reduced`

```text
---- Summary ----
Main function to check that our amount of a haem is lower once dithionite has
reduced it fully than it was with oxygen, before the first addition, as the
instrument's own trace is.

---- Inputs ----
haems : dict
    Our amounts and the instrument's traces, from _haem_trace_loader.
name : str
    Name of the haem in our fit file.

---- Globals read ----
FIRST_ADDITION_SPECTRUM, WINDOW_SPECTRA (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
median of the last 2 min of the run (after the dithionite) - median of the 2 min
before the first addition < 0.

---- Helpers ----
None.
```

#### `test_haem_shapes_are_those_of_the_instrument`

```text
---- Summary ----
Main function to check that the shape of a haem in our fit file is the shape the
instrument's own fit file uses for it (shifted and scaled as the instrument does),
whatever its size and whichever way up it is stored.

---- Inputs ----
name : str
    Name of the haem in our fit file.

---- Globals read ----
FITS_FOLDER, INSTRUMENT_FIT_FILE, HAEM_TRACES, SAME_SHAPE (module constants);
settings.STANDARD_FIT.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Correlation of the two shapes at the instrument's wavelengths inside the range it
fits over, where our file has the haem too: +1 or -1 for the same shape.

---- Helpers ----
_instrument_fit_reader
```

#### `test_valencia_background_is_the_instruments`

```text
---- Summary ----
Main function to check that our Valencia background can make the background shape
of the instrument's own fit file, over the wavelengths the instrument fits.

---- Inputs ----
None.

---- Globals read ----
INSTRUMENT_FIT_FILE, INSTRUMENT_BACKGROUND, SAME_BACKGROUND (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The instrument's shape is matched by the best mix of our flat level and our shape
(least squares); the largest difference left, divided by the instrument's range
(highest - lowest), must be below SAME_BACKGROUND.

---- Helpers ----
_instrument_fit_reader
```

#### `test_instrument_traces_fall_when_reduced`

```text
---- Summary ----
Main function to check that the instrument's own trace of a haem is lower once
dithionite has reduced it fully than it was with oxygen, before the first
addition: down is reduced.

---- Inputs ----
haems : dict
    Our amounts and the instrument's traces, from _haem_trace_loader.
name : str
    Name of the haem in our fit file.

---- Globals read ----
FIRST_ADDITION_SPECTRUM, DITHIONITE_SPECTRUM, WINDOW_SPECTRA (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
median of the last 2 min of the run (after the dithionite) - median of the 2 min
before the first addition < 0.

---- Helpers ----
None.
```

## `tests/test_haem_library.py`

Tests of the haem library: the presets, the joining of library files and the fits offered.

### HELPERS

#### `_dip_finder`

```text
---- Summary ----
Helper function to find the α dip of one haem of a fit.

---- Inputs ----
fit : dict
    Fit dictionary, as fit_loader gives it.
index : int
    Number of the haem in the fit, from 0.

---- Globals read ----
None.

---- Outputs ----
Tuple[float, float]
    (lowest value between 540 and 640 nm in OD/mM/cm, its wavelength in nm).

---- Globals mutated ----
None.

---- Equations ----
value in OD/mM/cm = value on the standard scale x 1 000 000.

---- Helpers ----
None.
```

#### `_haem_file_writer`

```text
---- Summary ----
Helper function to write a made-up fit file in the layout with heading lines.

---- Inputs ----
path : Path
    File to write.
haems : Dict[str, List[Tuple[float, float]]]
    {plain haem name: (wavelength in nm, value in OD/mM/cm) rows}; one haem for a
    library file.

---- Globals read ----
None.

---- Outputs ----
Path
    The file written.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_preset_writer`

```text
---- Summary ----
Helper function to write a made-up preset listing library files.

---- Inputs ----
path : Path
    File to write.
files : List[str]
    Library file names, in the order the preset lists them.

---- Globals read ----
None.

---- Outputs ----
Path
    The file written.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_library_maker`

```text
---- Summary ----
Helper function to make a made-up library of three haems, one file each.

---- Inputs ----
fits : Path
    The made-up fits folder.

---- Globals read ----
HAEMS (module constant); HAEMS_FOLDER_NAME.

---- Outputs ----
None.

---- Globals mutated ----
None. Writes the files (side effect).

---- Equations ----
None.

---- Helpers ----
_haem_file_writer
```

### MAIN FUNCTIONS

#### `test_preset_joins_its_haems_in_order`

```text
---- Summary ----
Main function to check that a preset gives one fit of its library files, the a
haems first, then the b, then the c, whatever order it lists them in, each with its
own rows and values.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
HAEMS (module constant); PRESETS_FOLDER_NAME.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
value on the standard scale = value in OD/mM/cm / 1 000 000.

---- Helpers ----
_library_maker
_preset_writer
```

#### `test_preset_problems_are_refused`

```text
---- Summary ----
Main function to check that a preset listing a missing file, a library file of two
haems, or two haems of the same name is refused with a message naming the problem.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
files : List[str]
    Library files the preset lists.
words : str
    Words the message must hold.

---- Globals read ----
HAEMS (module constant); HAEMS_FOLDER_NAME, PRESETS_FOLDER_NAME.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_haem_file_writer
_library_maker
_preset_writer
```

#### `test_root_file_with_a_preset_name_is_not_offered`

```text
---- Summary ----
Main function to check that the fits offered are the presets, then the user's own
fit files, and that a fit file with a preset's name (an old copy) is neither
offered nor loaded in place of the preset.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
HAEMS (module constant); PRESETS_FOLDER_NAME.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_haem_file_writer
_library_maker
_preset_writer
```

#### `test_standard_preset_keeps_its_haems`

```text
---- Summary ----
Main function to check that the standard fit, now a preset of the haem library,
gives the five haems and α dips of the fit file it replaced, and that the cc of
temp_fit_037v keeps the 35.2 OD/mM/cm of its old file, its preset giving it 2 haems
per protein.

---- Inputs ----
None.

---- Globals read ----
FITS_FOLDER, STANDARD_DIPS (module constants); settings.STANDARD_FIT.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_dip_finder
```

#### `test_own_haems_are_built_from_the_library`

```text
---- Summary ----
Main function to check the haems ticked under Build a fit: the library is listed
for the tick boxes in the order a, b, c with each file's haem name; the haems
ticked load as one fit, named in words with their files; and no haem ticked, or a
ticked file that is missing, is refused with a message, while a preset name still
loads the preset.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
OWN_HAEMS_NAME, PRESETS_FOLDER_NAME.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_library_maker
_preset_writer
```

## `tests/test_haem_types.py`

Tests of the haem types read from the haem names, the order of the haems and their

### MAIN FUNCTIONS

#### `test_a_fit_file_is_read_in_that_order`

```text
---- Summary ----
Main function to check that a fit file listing its haems c, b, a is read with the
a haem first, then the b, then the c, each haem's shape moved with its name.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Writes a fit file in tmp_path (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_haems_are_ordered_a_then_b_then_c`

```text
---- Summary ----
Main function to check the order of the haems: every a haem, then every b, then
every c, then a name of no known type, each type in alphabetical order (a digit
before a letter, so a3 before a605 and b557 before bH).

---- Inputs ----
None.

---- Globals read ----
FILE_ORDER (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_haem_types_come_from_the_name`

```text
---- Summary ----
Main function to check that a haem's type is the first letter after a leading
'Cyt', 'cytochrome' or 'haem', and 'other' for any other name.

---- Inputs ----
name : str
    Haem name, plain or in figure form.
expected : str
    Its type, worked out by hand.

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
```

#### `test_haems_are_coloured_by_type`

```text
---- Summary ----
Main function to check the colours: the usual haems keep their own, a haem without
one takes the first free shade of its type, two haems with the same usual colour
get different shades, and a name of no known type a colour no haem type has.

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
```

## `tests/test_import_export.py`

Tests of the export at the end of the import: the size of the spectra and where each file goes.

### HELPERS

#### `_experiment_maker`

```text
---- Summary ----
Helper function to stand in for the reading of a file: a made-up recording of 0 to
10 min, one point a minute, with the OD values and events it is given, as the
processing hands them back.

---- Inputs ----
info : dict
    Per-file information (preview_info_builder): name, OD values and events.
cfg : object
    Settings of the processing; not used.
fit : object
    Fit of the processing; not used.

---- Globals read ----
EVENTS, OD_KEYS (module constants).

---- Outputs ----
dict
    {'experiment': experiment} (DATA_FORMAT.md), the oxygen and OCR tables equal to
    twice the time.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_metadata_reader`

```text
---- Summary ----
Helper function to read the Metadata sheet of a workbook as {field: value}.

---- Inputs ----
path : Path
    The workbook.

---- Globals read ----
None.

---- Outputs ----
dict
    {field: value} of the Metadata sheet.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_session_maker`

```text
---- Summary ----
Helper function to set up a session of two made-up files whose reading is stood in
for by _experiment_maker, with no window.

---- Inputs ----
root : Path
    Results folder.
monkeypatch : pytest.MonkeyPatch
    Used to stand in for the reading of the files.

---- Globals read ----
None.

---- Outputs ----
ViewerSession
    The session, with the files run1 and run2 of 10 min each.

---- Globals mutated ----
None. Replaces the processing in viewer_preview for the test (side effect).

---- Equations ----
None.

---- Helpers ----
_experiment_maker
```

### MAIN FUNCTIONS

#### `test_size_in_words`

```text
---- Summary ----
Main function to check how a size is put in words: two significant figures, in GB
from 10^9 bytes and in MB from 10^6, and nothing at all said as such.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
1 234 567 890 bytes = 1.23 GB, about 1.2 GB; 352 000 000 bytes = 352 MB, about 350.

---- Helpers ----
None.
```

#### `test_spectra_size_by_hand`

```text
---- Summary ----
Main function to check the size of the spectra csv files against sums worked out by
hand: a file trimmed at both ends, one not trimmed with two spectrometers, one with
no spectra, and one trimmed at its start only.

---- Inputs ----
None.

---- Globals read ----
BYTES_PER_VALUE (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
run1: 60 min kept from 10 to 40, so half of 600 spectra x 100 wavelengths x 5 bytes
= 150 000 trimmed; the whole 600 x 100 x 5 = 300 000.
run2: not trimmed, 2 x 200 x 50 x 5 = 100 000 trimmed and nothing whole.
run3: no spectra.
run4: 30 min from 6 to the end, so 24 / 30 = 0.8 of 300 x 10 x 5 = 12 000 trimmed;
the whole 300 x 10 x 5 = 15 000.

---- Helpers ----
None.
```

#### `test_trimmed_and_whole_go_to_their_folders`

```text
---- Summary ----
Main function to check where the export of the import writes: a trimmed file's
trimmed data in its own folder, with the edges, OD values and labels, and its whole
recording in full/ without the edges; a file not trimmed has no full/.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Used to stand in for the reading of the files.

---- Globals read ----
EVENTS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Kept from 2 to 8 min of a point a minute: 7 points, the addition at 5 - 2 = 3 min.

---- Helpers ----
_metadata_reader
_session_maker
```

#### `test_new_edges_export_again`

```text
---- Summary ----
Main function to check the export once the edges change: a whole recording already
written is left as it is, a file that has just become trimmed gets one, and a file
no longer trimmed loses the one written for it.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Used to stand in for the reading of the files.

---- Globals read ----
EVENTS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_metadata_reader
_session_maker
```

## `tests/test_label_tidier.py`

Tests of the tidy form of an event label, and that the figures can draw its symbols.

### MAIN FUNCTIONS

#### `test_exponent_after_a_caret_is_raised`

```text
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
```

#### `test_exponent_after_a_unit_is_raised`

```text
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
```

#### `test_micro_is_written_with_its_sign`

```text
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
```

#### `test_names_and_formulas_are_left_alone`

```text
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
```

#### `test_number_and_unit_get_a_space`

```text
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
```

#### `test_symbols_can_be_drawn_in_the_figures`

```text
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
```

#### `test_tidy_label_stays_as_it_is`

```text
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
```

## `tests/test_launcher.py`

Tests the launcher: a changed package list installs the packages again, a failed install

### HELPERS

#### `_git_stand_in_maker`

```text
---- Summary ----
Helper function to load the launcher in a made-up git copy, with GitHub reachable
and git stood in: it answers as GIT_ANSWERS says, except where changes says
otherwise.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest; it becomes the git copy.
monkeypatch : pytest.MonkeyPatch
    Says git is installed, and that this start is not the one after an update.
changes : Dict[str, Tuple[int, str]]
    {git command: (return code, output)} in place of GIT_ANSWERS.

---- Globals read ----
GIT_ANSWERS (module constant).

---- Outputs ----
ModuleType
    The launcher.

---- Globals mutated ----
None. Makes the .git folder (side effect).

---- Equations ----
None.

---- Helpers ----
_launcher_loader
```

#### `_launcher_loader`

```text
---- Summary ----
Helper function to load a fresh copy of the launcher from its file, which Python
does not import by name (it ends in .pyw).

---- Inputs ----
None.

---- Globals read ----
LAUNCHER (module constant).

---- Outputs ----
ModuleType
    The launcher; its start (main) is not run.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_stand_in_maker`

```text
---- Summary ----
Helper function to load the launcher with its environment and package list in an
empty folder, and with pip and the check that the packages load stood in.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
PACKAGES, PIP_TEXT (module constants).

---- Outputs ----
Tuple[ModuleType, List[str], Dict[str, bool]]
    (the launcher; the stand-ins run, in order, each 'pip' or 'imports'; whether
    each stand-in works, {'pip': ..., 'imports': ...}, which a test may change).

---- Globals mutated ----
None. Writes the made-up environment and package list (side effects).

---- Equations ----
None.

---- Helpers ----
_launcher_loader
```

### MAIN FUNCTIONS

#### `test_changed_package_list_is_installed`

```text
---- Summary ----
Main function to check that the packages are installed the first time, only
checked at a start with the same list, and installed again when the list changes,
as after an update; an environment made before the fingerprint was kept gets them
installed once.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
NEWER_PACKAGES (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_stand_in_maker
environment_builder
```

#### `test_failed_install_stops_with_a_plain_message`

```text
---- Summary ----
Main function to check that when the packages cannot be installed and none load,
the launcher stops with one plain sentence and keeps pip's text for the log; a
first install that failed leaves no half-made environment.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
PIP_TEXT (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_stand_in_maker
environment_builder
```

#### `test_failed_update_keeps_working_packages`

```text
---- Summary ----
Main function to check that when the list has changed but the packages cannot be
installed (no internet), Portimao opens with the packages it has, and the next
start tries again.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
NEWER_PACKAGES (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_stand_in_maker
environment_builder
```

#### `test_package_fingerprint_ignores_line_endings`

```text
---- Summary ----
Main function to check that the package list gives the same fingerprint with
Windows line endings, a different one when a package changes, and none when it
cannot be read.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
NEWER_PACKAGES, PACKAGES (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_launcher_loader
_package_list_stamper
```

#### `test_update_note_reaches_portimao`

```text
---- Summary ----
Main function to check that Portimao is told why its copy cannot update, and told
nothing when it can, and that its output goes to the launch log after the start
before.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Stands in for starting Portimao, and sets a note left from before.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_launcher_loader
program_starter
```

#### `test_update_reasons_are_given`

```text
---- Summary ----
Main function to check what the update check gives in a git copy: an update
installed, nothing newer, or no update with the reason and what to do.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Stands in for git.
changes : Dict[str, Tuple[int, str]]
    What git answers differently from an update that installs.
expected : Tuple[bool, List[str]]
    (whether the update was installed, the words the reason must hold; none for
    no reason).

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_git_stand_in_maker
update_checker
```

#### `test_update_reasons_without_git`

```text
---- Summary ----
Main function to check that a git copy on a computer without git says so, and that
a copy from a zip gives no reason here (Portimao says it itself).

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Says git is not installed.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_git_stand_in_maker
_launcher_loader
update_checker
```

## `tests/test_mac_app_builder.py`

Tests the parts of the Mac app's build recipe that run anywhere: what goes inside the

### HELPERS

#### `_plist_maker`

```text
---- Summary ----
Helper function to write a made-up Info.plist, as PyInstaller leaves it.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
PYINSTALLER_KEYS (module constant).

---- Outputs ----
Path
    The file.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_app_carries_program_files`

```text
---- Summary ----
Main function to check that the app starts from the app's start (which updates it),
and that the build puts the fits, the window's icon, the question list (which gives
the version), the Mac report and the swap script inside the app, and the details of
each package asked for.

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
_arguments_builder
```

#### `test_plist_gets_version_and_keeps_keys`

```text
---- Summary ----
Main function to check that the version and the folder reasons are written into
Info.plist, and that PyInstaller's other keys are kept.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_info_plist_writer
_plist_maker
```

#### `test_plist_refuses_unknown_version`

```text
---- Summary ----
Main function to check that a version that is not numbers and dots (the program
gives "unknown" when it finds none) stops the build and leaves the file as it was.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
PYINSTALLER_KEYS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_info_plist_writer
_plist_maker
```

## `tests/test_mac_app_mover.py`

Tests that an install of the old launcher on a Mac is moved to the app: what goes, what

### HELPERS

#### `_git_runner`

```text
---- Summary ----
Helper function to run a git command in the made-up install, as a test user.

---- Inputs ----
root : Path
    The made-up install.
*arguments : str
    What follows `git`.

---- Globals read ----
HIDDEN (module constant).

---- Outputs ----
None
    Nothing. The test fails when git fails.

---- Globals mutated ----
None. Changes the git copy (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_installer_faker`

```text
---- Summary ----
Helper function to give a stand-in for install_mac.sh, which makes a small app in
the user's own Applications folder, or fails as a download with no internet does.

---- Inputs ----
is_installed : bool
    False to fail.
calls : List[Path]
    Gets the program folder of each call.

---- Globals read ----
None.

---- Outputs ----
Callable[..., Tuple[Optional[Path], str]]
    Called with (root, home, show, log) as the mover calls it.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_link_tester`

```text
---- Summary ----
Helper function to skip the test where symbolic links cannot be made (Windows
without the right to make them).

---- Inputs ----
folder : Path
    A folder to try in.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Skips the test when no link can be made.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_old_install_maker`

```text
---- Summary ----
Helper function to make an install of the old launcher as a git copy: the program's
files committed on a branch, then the user's things and the program's own leftovers
added, and one program file changed by the user.

---- Inputs ----
root : Path
    Folder to make it in.
branch : str
    The branch it is on.

---- Globals read ----
ADDED, TRACKED (module constants).

---- Outputs ----
Path
    The made-up install.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_git_runner
```

### MAIN FUNCTIONS

#### `test_desktop_file_is_made_once`

```text
---- Summary ----
Main function to check that a Mac run from its folder gets the Desktop file the
first time the folder is started, naming the folder and the Python, and that it is
not made again later once the user has deleted it.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
COMMAND_MARK, OLD_MACOS, PYTHON (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_desktop_file_replaces_the_old_link`

```text
---- Summary ----
Main function to check that on a Mac that cannot run the app, the old launcher's
link (into the program folder, whose Portimao.app the update took away) is replaced
by the Desktop file at any start, and that a link the user made elsewhere is left.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
OLD_MACOS, PYTHON (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_link_tester
```

#### `test_developer_copy_is_not_moved`

```text
---- Summary ----
Main function to check that a git copy on another branch than main (a developer's)
is not moved and nothing is installed.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
NEW_MACOS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_installer_faker
_old_install_maker
```

#### `test_failed_install_takes_nothing_away`

```text
---- Summary ----
Main function to check that when the app cannot be installed, no file is taken
away, nothing is opened, the program starts the old way and the log says why.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
NEW_MACOS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_installer_faker
_old_install_maker
```

#### `test_folder_elsewhere_gets_its_fits_copied`

```text
---- Summary ----
Main function to check that an install that is not the app's own folder has its
fits and last answers copied into the app's own folder, while its data stays.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
NEW_MACOS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_installer_faker
_old_install_maker
```

#### `test_move_keeps_the_desktop_link_working`

```text
---- Summary ----
Main function to check that the move points the old launcher's link on the Desktop
at the app, and replaces the Desktop file left by an earlier failed move with the
same link.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
NEW_MACOS, PYTHON (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_installer_faker
_link_tester
_old_install_maker
```

#### `test_move_takes_away_only_program_files`

```text
---- Summary ----
Main function to check that the move installs the app, takes away the files git
tracks (outside fits), git's folder, the Python environment, the mark and the
folders left empty, keeps the fits, the data, the logs, the last answers, anything
else of the user's and the program file they changed, opens the app and logs it.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
ADDED, NEW_MACOS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_installer_faker
_old_install_maker
```

#### `test_old_macos_is_not_moved`

```text
---- Summary ----
Main function to check that a Mac older than macOS 14 is not moved, the reason
naming its version, and nothing is installed.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
OLD_MACOS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_installer_faker
_old_install_maker
```

## `tests/test_mac_install.py`

Tests that the install line puts the right app in the user's own Applications folder,

### HELPERS

#### `_install_runner`

```text
---- Summary ----
Helper function to run install_mac.sh as `curl ... | bash` does, its text coming in
through the shell's input, with the Mac's commands stood in for and a stand-in home
folder.

---- Inputs ----
home : Path
    Stand-in home folder.
arguments : Sequence[str]
    Arguments after the script (`--no-open`).
system : str
    What uname says the system is.
macos_version : str
    What sw_vers says the macOS version is.
is_apple_silicon : bool
    True for an Apple Silicon Mac.
is_open : bool
    True when Portimao is found open.
is_downloaded : bool
    False when the download fails.

---- Globals read ----
HIDDEN, RELEASE_URL, SCRIPT, SHELL, STAND_INS (module constants).

---- Outputs ----
subprocess.CompletedProcess
    The finished run, with its output as text.

---- Globals mutated ----
None. Runs the script, which writes into the home folder (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_old_app_maker`

```text
---- Summary ----
Helper function to put an older Portimao app, with a file only it has, in the
user's own Applications folder.

---- Inputs ----
home : Path
    Stand-in home folder.

---- Globals read ----
None.

---- Outputs ----
Path
    The old .app folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_download_failure_keeps_the_old_app`

```text
---- Summary ----
Main function to check that a download that fails stops with one sentence saying
what to do, keeps the app already there and leaves no download folder.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
_old_app_maker
```

#### `test_intel_mac_gets_the_intel_zip`

```text
---- Summary ----
Main function to check that an Intel Mac downloads the Intel app.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
RELEASE_URL (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
```

#### `test_line_installs_and_opens_the_app`

```text
---- Summary ----
Main function to check that on an Apple Silicon Mac the line downloads the Apple
Silicon app, puts it in the user's own Applications folder (made when missing),
opens it, says so with the version and leaves no download folder behind.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
RELEASE_URL (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
```

#### `test_no_open_replaces_the_old_app`

```text
---- Summary ----
Main function to check that the line run again puts the new app wholly in place of
the old one, and that --no-open (used by the move) leaves it closed.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
_old_app_maker
```

#### `test_not_a_mac_is_refused`

```text
---- Summary ----
Main function to check that the line run on another system stops with one sentence
and downloads nothing.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
```

#### `test_old_macos_is_refused`

```text
---- Summary ----
Main function to check that a Mac older than macOS 14 is told, in one sentence
naming its version, to update macOS, and that nothing is downloaded or made.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
```

#### `test_open_app_is_refused`

```text
---- Summary ----
Main function to check that the line asks for Portimao to be closed when it is open,
and leaves the app as it is.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_install_runner
_old_app_maker
```

## `tests/test_mac_report.py`

Tests that the Mac report runs to the end, finds where the folder or the app is and

### HELPERS

#### `_app_maker`

```text
---- Summary ----
Helper function to make a small Portimao app in Applications, holding the report
and a question list with a made-up version as the build puts them, and the app's
own folder in the home folder with a launch log, an update log and a move log.

---- Inputs ----
home : Path
    Stand-in home folder.

---- Globals read ----
REPORT (module constant).

---- Outputs ----
Path
    The folder inside the app that holds the report's launchers folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_folder_maker`

```text
---- Summary ----
Helper function to make a small Portimao folder holding the report, a question
list with a made-up version and a launch log of 50 numbered lines.

---- Inputs ----
home : Path
    Stand-in home folder.
place : str
    Folder inside home to put Portimao in ('' for the home folder itself).

---- Globals read ----
N_LOG_LINES, REPORT (module constants).

---- Outputs ----
Path
    The Portimao folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_report_runner`

```text
---- Summary ----
Helper function to run the report of a Portimao folder as Terminal would, with
the stand-in home folder as the user's home.

---- Inputs ----
folder : Path
    Portimao folder made by _folder_maker.
home : Path
    Stand-in home folder.

---- Globals read ----
HIDDEN, SHELL, REPORT (module constants).

---- Outputs ----
str
    What the report printed. The test fails when it does not end with 0.

---- Globals mutated ----
None. Runs the report (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_snapshot_taker`

```text
---- Summary ----
Helper function to read every file of a folder, to compare before and after.

---- Inputs ----
folder : Path
    Folder to read.

---- Globals read ----
None.

---- Outputs ----
Dict[str, bytes]
    Path inside the folder against the file's contents.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_report_in_downloads_names_it`

```text
---- Summary ----
Main function to check that the report of a folder in Downloads ends without an
error, has every part, names Downloads as guarded, gives the version, shows only
the last 30 log lines and leaves every file as it was.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
SECTIONS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_folder_maker
_report_runner
_snapshot_taker
```

#### `test_report_in_home_folder_is_not_guarded`

```text
---- Summary ----
Main function to check that a folder straight in the home folder is not named as
guarded.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_folder_maker
_report_runner
```

#### `test_report_inside_app_describes_it`

```text
---- Summary ----
Main function to check that the report run from inside the app (as Copy details
does) describes the app and reads the logs of the app's own folder (the move log
among them), leaves out the
launcher's parts, prints only the report on its output and changes nothing.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, used as the home folder.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_app_maker
_report_runner
_snapshot_taker
```

## `tests/test_no_windows.py`

Tests that the tests themselves open no windows on the screen (set in conftest.py).

### MAIN FUNCTIONS

#### `test_no_tk_window_can_open`

```text
---- Summary ----
Main function to check that neither a Tk window nor a Toplevel one can open while
the tests run.

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
```

#### `test_plots_are_drawn_off_screen`

```text
---- Summary ----
Main function to check that matplotlib draws the tests' plots off screen, and so
do the Pythons the tests start.

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
```

#### `test_started_programs_have_no_console_window`

```text
---- Summary ----
Main function to check that on Windows a program a test starts, through
subprocess.run or subprocess.Popen, gets no console window.

---- Inputs ----
None.

---- Globals read ----
CONSOLE_CHECK (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `tests/test_ocr_checking.py`

Tests that our OCR maths gives the values worked out by hand, and that the OCR check finds what it should.

### HELPERS

#### `_instrument_maker`

```text
---- Summary ----
Helper function to make the traces of a recording whose rates were worked out
exactly as our maths does.

---- Inputs ----
n_points : int
    Points of the clock (0.5 s apart).

---- Globals read ----
FALL_EDGE_POINTS, FALL_PER_MIN, GAP_MMHG, LEAK_PER_MIN, LEAK_START_POINTS,
PRESSURE_FACTOR (module constants).

---- Outputs ----
Dict[str, np.ndarray]
    CcO2, PcO2, PtO2, VrO2, DgO2 and VoO2, one value per point, NaN where the
    instrument leaves its rates empty.

---- Globals mutated ----
None.

---- Equations ----
CcO2 = 600 - 0.5 j µM (1 µM/s, so a fall of 60 µM/min); PcO2 = 0.75 x CcO2;
PtO2 = PcO2 + 100 mmHg; VrO2 = 60, DgO2 = 0.1 x 100 = 10 and VoO2 = 70 µM/min.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_steady_fall_is_its_slope`

```text
---- Summary ----
Main function to check that oxygen falling by 1 µM/s gives a fall of 60 µM/min,
with no value for the 14 points at each end (29 points centred on each point).

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
0.5 µM every 0.5 s = 1 µM/s = 60 µM/min.

---- Helpers ----
_instrument_maker
```

#### `test_curved_fall_needs_29_points`

```text
---- Summary ----
Main function to check that oxygen curved as c x t^3 gives the slope of a straight
line through exactly 29 points 0.5 s apart, so any other window length fails.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
For x = c t^3 around t0, the least-squares slope through the points t0 + k dt,
k = -14 ... 14, is c (3 t0^2 + dt^2 sum(k^4) / sum(k^2)); sum(k^2) = 2030 and
sum(k^4) = 255374, so the ratio is 125.8 and dt^2 x 125.8 = 31.45 s^2. With
c = -0.001 µM/s^3 and t0 = 50 s (row 100): slope = -0.001 x (7500 + 31.45) =
-7.53145 µM/s, so the fall is 60 x 7.53145 = 451.887 µM/min.

---- Helpers ----
_instrument_maker
```

#### `test_leak_is_permeability_times_gap`

```text
---- Summary ----
Main function to check that a steady pressure gap of 100 mmHg through a wall of
permeability 0.1 µM/min/mmHg gives a leak of 10 µM/min, with no value for the
first 39 points, and that our OCR is the fall plus the leak.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
leak = 0.1 x 100 = 10 µM/min; OCR = 60 + 10 = 70 µM/min.

---- Helpers ----
_instrument_maker
```

#### `test_leak_window_is_40_points`

```text
---- Summary ----
Main function to check that a step in the pressure gap reaches its full size in
the leak after exactly 40 points, the mean ending at each point.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Gap 0 before row 100 and 100 mmHg from it: leak[99] = 0; leak[100] = 0.1 x 100 x
1/40 = 0.25; leak[138] = 0.1 x 100 x 39/40 = 9.75; leak[139] = 10 µM/min.

---- Helpers ----
_instrument_maker
```

#### `test_agreeing_traces_pass`

```text
---- Summary ----
Main function to check that a recording worked out as we expect is checked, agrees
in every part, finds the pressure factor and gives no message.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, PRESSURE_FACTOR, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_instrument_maker
```

#### `test_wrong_sum_is_caught`

```text
---- Summary ----
Main function to check that an OCR 5 µM/min above the fall plus the leak is caught,
and that the message names that part only.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_instrument_maker
```

#### `test_wrong_leak_is_caught`

```text
---- Summary ----
Main function to check that a leak twice ours (as from a permeability twice the
one stored) is caught in its typical difference and in its size, and named.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The instrument's leak is 20 µM/min against our 10: typical difference 10 µM/min,
size 100 % off. Its OCR is still its fall plus its leak.

---- Helpers ----
_instrument_maker
```

#### `test_addition_stretch_is_left_out`

```text
---- Summary ----
Main function to check that a large spike in the instrument's fall next to an
addition is left out of the comparison, and is caught when no addition is there.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The spike adds 5000 µM/min to rows 490 to 510. Without the addition at row 500,
the 960 compared points give a factor of 1 + 21 x 5000 / (60 x 960) = 2.82, so
the size is 182 % off.

---- Helpers ----
_instrument_maker
```

#### `test_missing_trace_is_not_checked`

```text
---- Summary ----
Main function to check that a file without the outside oxygen pressure, or without
the wall's permeability, is not checked, and that the message says why.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_instrument_maker
```

#### `test_short_recording_is_not_checked`

```text
---- Summary ----
Main function to check that a recording too short to compare is not checked.

---- Inputs ----
None.

---- Globals read ----
PERMEABILITY, STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
150 points: the instrument's OCR has values at rows 60 to 129 only, 70 points,
fewer than the 100 needed.

---- Helpers ----
_instrument_maker
```

## `tests/test_paf_reader_parts.py`

Tests of the parts of the .paf reader that deal with unusual files, on made-up values

### MAIN FUNCTIONS

#### `test_additions_copies_are_joined`

```text
---- Summary ----
Main function to check that the two stored copies of an addition (the first
without a position) give one addition, in the order of their positions.

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
```

#### `test_additions_under_one_name_are_all_kept`

```text
---- Summary ----
Main function to check that two additions stored under the same name stay two
additions, each with its own text, and that the user is told.

---- Inputs ----
capsys : pytest.CaptureFixture
    Catches what is printed.

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
```

#### `test_addition_without_position_is_left_out`

```text
---- Summary ----
Main function to check that an addition with no stored position is left out and
that the user is told.

---- Inputs ----
capsys : pytest.CaptureFixture
    Catches what is printed.

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
```

#### `test_spectrum_times_with_equal_counts`

```text
---- Summary ----
Main function to check that as many spectra as time points take the clock's times,
in minutes, without a message.

---- Inputs ----
capsys : pytest.CaptureFixture
    Catches what is printed.

---- Globals read ----
CLOCK_S (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
time (min) = time (s) / 60.

---- Helpers ----
None.
```

#### `test_spectrum_times_with_fewer_spectra`

```text
---- Summary ----
Main function to check that fewer spectra than time points take the first times of
the clock and that the user is told.

---- Inputs ----
capsys : pytest.CaptureFixture
    Catches what is printed.

---- Globals read ----
CLOCK_S (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Four spectra on a clock of 0, 0.5, ... 2.5 s are at 0, 0.5, 1 and 1.5 s.

---- Helpers ----
None.
```

#### `test_spectrum_times_with_more_spectra`

```text
---- Summary ----
Main function to check that more spectra than time points stop the file, with the
file's name in the message.

---- Inputs ----
None.

---- Globals read ----
CLOCK_S (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_transmission_from_the_stored_logarithms`

```text
---- Summary ----
Main function to check the transmission worked out from the stored logarithms.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Counts of 50 and 400 over a reference of 100 and 200 give 0.5 and 2.

---- Helpers ----
None.
```

#### `test_transmission_is_empty_without_reference_counts`

```text
---- Summary ----
Main function to check that the transmission is empty, never infinite, where the
reference has zero counts, and is untouched at the other wavelengths.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
log10(0) is minus infinity: 50 counts over 0 would be infinite, and 0 over 0 has
no value. Both are left empty. 50 over 100 is 0.5.

---- Helpers ----
None.
```

#### `test_trace_titles_follow_the_unit_of_the_file`

```text
---- Summary ----
Main function to check the column titles of the traces: the oxygen titles carry
the file's unit, written with the micro sign, and the OCR column keeps its name.

---- Inputs ----
None.

---- Globals read ----
MICRO_SIGN, GREEK_MU (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_addition_outside_the_recording_is_left_out`

```text
---- Summary ----
Main function to check that an addition stored outside the recording is left out
with a warning that names it, that the others get their time, and that the quiet
reading leaves out the same addition without printing.

---- Inputs ----
capsys : pytest.CaptureFixture
    Catches what is printed.

---- Globals read ----
CLOCK_S (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Spectrum 3 is row 2 of the clock: 1.0 s = 1/60 min.

---- Helpers ----
None.
```

#### `test_missing_concentration_is_written_by_the_helper`

```text
---- Summary ----
Main function to check that the shared helper writes every concentration, a
missing one included.

---- Inputs ----
None.

---- Globals read ----
MICRO_SIGN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
2000 uM = 2 mM; 1 500 000 uM = 1.5 M.

---- Helpers ----
None.
```

#### `test_rate_trace_short_by_its_usual_gap_is_not_reported`

```text
---- Summary ----
Main function to check that a trace short by the points the instrument always
leaves empty is not reported, even in a short recording, while one short by more
is, with its length in seconds.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
In a recording of 1343 points, 20 points are 1.5 %, more than the 1 % that is
always let pass; 10 points are 0.7 %. 40 points of 0.5 s are 20 s.

---- Helpers ----
None.
```

#### `test_trace_with_disagreeing_lengths_is_noted`

```text
---- Summary ----
Main function to check that a trace whose two stored lengths disagree is not read
and is noted under its name with the reason, both numbers included.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The two lengths sit 28 and 20 bytes before the end of the first record.

---- Helpers ----
None.
```

#### `test_unreadable_files_give_plain_messages`

```text
---- Summary ----
Main function to check that a file that is missing, too small, not a .paf or
without a clock is refused with a message that starts with its name and holds no
Python error name, by both the quick look and the full reading.

---- Inputs ----
tmp_path : Path
    Empty folder made by pytest.

---- Globals read ----
MARK (constant of the reader).

---- Outputs ----
None.

---- Globals mutated ----
None. Writes three small files in tmp_path (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `tests/test_paf_reading.py`

Tests that what is read from a .paf file equals the instrument software's own export of

### HELPERS

#### `_dataset_loader`

```text
---- Summary ----
Helper function to read one spectrometer of the example run once for all the tests
that use it.

---- Inputs ----
request : pytest.FixtureRequest
    Gives the dataset name ('Cyt' or 'NADH').

---- Globals read ----
PAF_FILE, ROWS_AT_ONCE (module constants).

---- Outputs ----
Iterator[dict]
    The dictionary of spectra_dataset_reader (with the intensity), plus 'name',
    'reference_counts' (the stored reference spectrum as whole counts) and
    'stored_error' (the largest difference between our attenuation and the stored
    logarithm of the reference minus that of each spectrum).

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
stored attenuation = log10(reference) - log10(counts), both as stored in the file.

---- Helpers ----
None.
```

#### `_export_reader`

```text
---- Summary ----
Helper function to open a spectrum file exported by the instrument software
('Espana Spectrum' format). The test is skipped when the file is not there.

---- Inputs ----
path : Path
    The exported file.

---- Globals read ----
EXPORT_MARK, EXPORT_HEADER_BYTES (module constants).

---- Outputs ----
Tuple[np.ndarray, np.ndarray, np.ndarray]
    (spectrum numbers, wavelengths in nm, spectra as (n_spectra, n_wavelengths));
    the spectra stay on disc and are read as they are used.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
The file is a 64 byte header (the mark as 4 whole numbers, then the version, the
number of spectra NS, of wavelengths NW and of spectrum numbers NT, then zeros),
NT whole numbers of 4 bytes, NW wavelengths of 8 bytes and NS x NW values of 8
bytes: 64 + 4 NT + 8 NW + 8 NS NW bytes in all.

---- Helpers ----
None.
```

#### `_trace_export_reader`

```text
---- Summary ----
Helper function to read a trace exported by the instrument software as text. The
test is skipped when the file is not there.

---- Inputs ----
path : Path
    The exported text file: a time (min) and a value on each line.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The times and the values, shape (n_points, 2). Lines without two numbers (the
    export ends with one) are left out.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_trace_loader`

```text
---- Summary ----
Helper function to read the traces and the times of the example run once.

---- Inputs ----
None.

---- Globals read ----
PAF_FILE, TRACE_FILES (module constants).

---- Outputs ----
dict
    {'time_s': the times in seconds, 'values': {trace name: one value per time,
    blank where the file has none}, 'experiment': the experiment as the program
    loads it, without its spectra}.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_known_file_counts`

```text
---- Summary ----
Main function to check that the example run gives its known numbers of spectra,
spectrometers and additions, and the additions at their known places.

---- Inputs ----
None.

---- Globals read ----
PAF_FILE, EXPECTED_SPECTRA, EXPECTED_EVENTS, EXPECTED_STEP_S, TRACE_FILES (module
constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
6,218 spectra 0.5 s apart last (6218 - 1) x 0.5 s = 3108.5 s = 51.808 min; an
addition at spectrum n is at (n - 1) x 0.5 s.

---- Helpers ----
None.
```

#### `test_spectra_counts_match_the_instrument`

```text
---- Summary ----
Main function to check that we read as many spectra and wavelengths as the
instrument exports, with the same spectrum numbers and the same wavelengths.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
FOLDER, SPECTRA_FILES, EXPECTED_SPECTRA, EXPECTED_WAVELENGTHS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_export_reader
```

#### `test_transmission_matches_the_instrument`

```text
---- Summary ----
Main function to check that every transmission we read equals the instrument's.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
FOLDER, SPECTRA_FILES, ROWS_AT_ONCE (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The two may differ by a millionth of a millionth of the value (the last digits a
computer keeps), no more.

---- Helpers ----
_export_reader
```

#### `test_intensity_matches_the_instrument`

```text
---- Summary ----
Main function to check that every intensity (whole counts) we read equals the
instrument's.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
FOLDER, SPECTRA_FILES, ROWS_AT_ONCE (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_export_reader
```

#### `test_attenuation_size_matches_the_instrument`

```text
---- Summary ----
Main function to check that every attenuation we work out has the size of the
instrument's own, whatever its sign.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
FOLDER, SPECTRA_FILES, ROWS_AT_ONCE (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
|log10(T)| of ours against |attenuation| of the export, to 12 decimals.

---- Helpers ----
_export_reader
```

#### `test_attenuation_sign_matches_the_instrument`

```text
---- Summary ----
Main function to check that our attenuation has the sign of the instrument's own:
more light than the reference gives a negative attenuation, less a positive one.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
FOLDER, SPECTRA_FILES (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The instrument exports -log10(T); the first spectrum is enough to see the sign.

---- Helpers ----
_export_reader
```

#### `test_spectra_parts_agree`

```text
---- Summary ----
Main function to check that the transmission, the intensity and the attenuation
read from one file fit together.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
ROWS_AT_ONCE (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
T = counts / reference counts. Both are whole numbers, each up to half a count
off, so T may be off by T x (0.5 / counts + 0.5 / reference). Attenuation =
log10(reference) - log10(counts) as stored in the file.

---- Helpers ----
None.
```

#### `test_times_and_wavelengths_run_in_order`

```text
---- Summary ----
Main function to check that the times and wavelengths of the spectra run in order
with no gaps, and that the spectra are numbered 1 to N.

---- Inputs ----
dataset : dict
    One spectrometer of the example run, from _dataset_loader.

---- Globals read ----
EXPECTED_SPECTRA, EXPECTED_STEP_S (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
time of spectrum n = (n - 1) x 0.5 s; a gap in the wavelengths would be a step of
more than 1.5 x the usual one.

---- Helpers ----
None.
```

#### `test_traces_match_the_instrument`

```text
---- Summary ----
Main function to check that a trace read from the file has the instrument's value
at every time, and has values at exactly the times the instrument exports.

---- Inputs ----
traces : dict
    The traces of the example run, from _trace_loader.
name : str
    Name of the trace in the file.

---- Globals read ----
FOLDER, TRACE_FILES, ROUNDING (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The export has 3 decimals, so a time (min) or a value may differ by 0.0005.

---- Helpers ----
_trace_export_reader
```

#### `test_loaded_traces_match_the_instrument`

```text
---- Summary ----
Main function to check that the oxygen tables the program works with (as loaded,
with their times in minutes) equal the instrument's export row for row.

---- Inputs ----
traces : dict
    The traces of the example run, from _trace_loader.
name : str
    Name of the table in the experiment.

---- Globals read ----
FOLDER, TRACE_FILES, LOADED_TRACES, ROUNDING, TIME_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The export has 3 decimals, so a time (min) or a value may differ by 0.0005.

---- Helpers ----
_trace_export_reader
```

#### `test_ocr_settings_fit_the_rate_traces`

```text
---- Summary ----
Main function to check the oxygen-rate settings read from the example run: its
permeability, and the 20 and 60 empty points at the start of VrO2 and of DgO2.

---- Inputs ----
traces : dict
    The traces of the example run, from _trace_loader.

---- Globals read ----
PAF_FILE, EXPECTED_PERMEABILITY, EXPECTED_FALL_EDGE_POINTS,
EXPECTED_LEAK_START_POINTS, FIXED_DECIMALS (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_example_ocr_agrees`

```text
---- Summary ----
Main function to check that the instrument's OCR of the example run agrees with
ours, and that the differences stay at their fixed values.

---- Inputs ----
None.

---- Globals read ----
PAF_FILE, FIXED_DIFFERENCES, FIXED_PRESSURE_FACTOR, FIXED_DECIMALS (module
constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_our_ocr_stays_fixed`

```text
---- Summary ----
Main function to check that our fall, leak and OCR of the example run keep their
fixed values, so a change to our maths is never made by accident.

---- Inputs ----
traces : dict
    The traces of the example run, from _trace_loader.

---- Globals read ----
PAF_FILE, FIXED_ROWS, FIXED_FALL, FIXED_LEAK, FIXED_OCR, FIXED_DECIMALS (module
constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `tests/test_processing_maths.py`

Tests that the attenuation, normalising, percent, averaging, trimming and the % oxidised

### HELPERS

#### `_plateau_experiment_builder`

```text
---- Summary ----
Helper function to build an experiment whose oxygen consumption sits on three
levels, with an addition at each change of level.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
dict
    Experiment with a point every 0.5 min from 0 to 12 min; VoO2 is 10 before
    4 min, 5 from 4 to 8 min and 2 from 8 min on; additions at 4 and 8 min.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ramp_experiment_builder`

```text
---- Summary ----
Helper function to build an experiment in which every value says which time it
belongs to, so that a cut can be checked point by point.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
dict
    Experiment with a point every minute from 0 to 10 min. VoO2 = 10 x time;
    spectrum number = time + 1; the three transmissions of a spectrum are
    time + 0.1, time + 0.2 and time + 0.3; additions at 3 and 6 min.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_attenuation_from_known_ratios`

```text
---- Summary ----
Main function to check that light cut to a tenth and a hundredth gives 1 and 2,
whether it is given as a fraction or as counts against a reference.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
attenuation = -log10(T): -log10(1) = 0, -log10(0.1) = 1, -log10(0.01) = 2, the
sign of the instrument's own export.

---- Helpers ----
None.
```

#### `test_attenuation_of_impossible_values`

```text
---- Summary ----
Main function to check that a transmission with no logarithm (zero, negative or
missing) becomes a blank.

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
```

#### `test_attenuation_added_to_an_experiment`

```text
---- Summary ----
Main function to check that the attenuation stored in an experiment is the
attenuation of its transmission, one value for each one.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
attenuation = -log10(T).

---- Helpers ----
None.
```

#### `test_blank_warning_counts_the_fitted_range`

```text
---- Summary ----
Main function to check that the warning about blank transmission values counts
only the wavelengths of the fit when a range is given, every wavelength when none
is, and is not printed when the only blanks are outside the range.

---- Inputs ----
capsys : pytest.CaptureFixture
    What the program printed (pytest).

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Three spectra at 500, 550, 600 and 650 nm. Spectrum 1 has a zero at 500 nm,
spectrum 2 a zero at 550 nm and a missing value at 650 nm, spectrum 3 none. Every
wavelength: 3 blanks in 2 spectra. Between 540 and 610 nm: 1 blank in 1 spectrum.
Between 590 and 610 nm: none.

---- Helpers ----
None.
```

#### `test_normalising_by_od_volume_and_dilution`

```text
---- Summary ----
Main function to check that normalising divides by dilution factor x OD x volume,
and leaves the times alone.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
With OD 2, volume 3 and dilution 2 the divisor is 12: 12 -> 1, 24 -> 2, 60 -> 5.

---- Helpers ----
None.
```

#### `test_unreadable_numbers_stop_both_scalings`

```text
---- Summary ----
Main function to check that a value that is not a number stops the OD scaling and
the % scaling alike, with the same plain message, and that an empty cell stays
empty in both.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Values 2, 2, empty, 6, 6 with one point in a row: OD 2, volume 3 and dilution 2
divide by 12, so 2 -> 1/6 and 6 -> 0.5; on the % scale 2 -> 0 and 6 -> 100. The
empty cell stays empty in both.

---- Helpers ----
None.
```

#### `test_percent_of_a_trace_with_plateaus`

```text
---- Summary ----
Main function to check that a trace on three levels gives 0 % on its lowest level,
100 % on its highest and the right share in between.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
A point every 6 s for 12 min: 2 for the first 4 min (40 points), then 6 (40
points), then 4 from 8 min. With 30 points in a row, the lowest median is 2 and
the highest 6. percent = (value - 2) / (6 - 2) x 100, so 2 -> 0, 6 -> 100 and
4 -> 50. 30 points, 6 s apart, last 180 s. The first window of median 2 is points
0 to 29 (0 to 2.9 min). The first of median 6 is points 26 to 55 (2.6 to 5.5 min):
it holds 14 twos and 16 sixes, so its two middle values are both 6; a window may
reach over a step as long as most of it is on the level.

---- Helpers ----
None.
```

#### `test_percent_of_a_flat_trace`

```text
---- Summary ----
Main function to check that a trace that never changes has no percent scale (every
value blank), and that a window of more points than the trace has is refused.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_reference_level_from_points_in_a_row`

```text
---- Summary ----
Main function to check the one finder of the reference levels: the median of the
highest, or the lowest, points in a row, with a blank value, with an ignored start
and end, and with too few points.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Values 1, 2, 9, 3, 4, 5, 0, 0 at 0 to 7 min, three points in a row. Medians of the
six windows: 2, 3, 4, 4, 4, 0. Highest: 4, first at 9, 3, 4 (2 to 4 min); lowest:
0, at 5, 0, 0 (5 to 7 min). With the 3 blank, the points left are 1, 2, 9, 4, 5,
0, 0 with medians 2, 4, 5, 4, 0: highest 5, at 9, 4, 5 (2 to 5 min, over the
blank). Between 1 and 5 min only: 2, 9, 3, 4, 5 with medians 3, 4, 4: highest 4
(2 to 4 min), lowest 3 (1 to 3 min). Three points, 1 min apart, last 180 s.

---- Helpers ----
None.
```

#### `test_window_mean_and_spread`

```text
---- Summary ----
Main function to check the mean and spread of the values inside a time window,
with a blank value, with one value and with none.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Values 1 to 6 at 0 to 5 min. From 1 to 3 min: 2, 3, 4 -> mean 3, spread
sqrt((1 + 0 + 1) / 2) = 1. With a blank in the middle of 4, 5, 6: 4 and 6 -> mean
5, spread sqrt((1 + 1) / 1) = 1.414.

---- Helpers ----
None.
```

#### `test_averages_around_the_additions`

```text
---- Summary ----
Main function to check the averages before and after each addition, and their
change from the first one.

---- Inputs ----
None.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Additions at 4 and 8 min, run ends at 12 min, 2 min windows ending 0.5 min before
the next addition (or the end): 1.5 to 3.5, 5.5 to 7.5 and 9.5 to 11.5 min, where
the trace is 10, 5 and 2. Change = 10/10, 5/10, 2/10 x 100 = 100, 50, 20 %;
difference = 0, -5, -8.

---- Helpers ----
_plateau_experiment_builder
```

#### `test_a_file_with_both_regions_gets_percent_oxidised`

```text
---- Summary ----
Main function to check that the processing of a file with both regions keeps each
haem's two levels and its % oxidised line, with the regions (kept as times on the
recording) put on the time of the trimmed data, and that a file without regions
has neither and is shown as delta D when % oxidised is asked for. The reading of
the spectra and the decomposition are stood in for by a made-up haem.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Pytest's tool for standing in for the decomposition.

---- Globals read ----
TIME_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Sixty spectra, one every 0.5 min from 0 to 29.5 min of the trimmed data, which
was trimmed 2 min from its start. D is 12 mOD before 10 min, 10 mOD from 10 to
20 min and 4 mOD from 20 min on. Regions on the recording: oxidised 2 to 8 min,
reduced 24 to 30 min; on the trimmed data 0 to 6 and 22 to 28 min, 13 spectra
each. D_ox = 12, D_red = 4, so P = (D - 4) / 8 x 100: 100 %, 75 % and 0 %.

---- Helpers ----
None.
```

#### `test_average_that_does_not_fit`

```text
---- Summary ----
Main function to check that an averaging window too long to fit between two
additions is left out, and said to be, in place of reaching back over the addition.

---- Inputs ----
None.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
A 4 min window ending at 7.5 min starts at 3.5 min, before the addition at 4 min;
one ending at 11.5 min starts at 7.5 min, before the addition at 8 min. The first
window (-0.5 to 3.5 min) holds only the level 10.

---- Helpers ----
_plateau_experiment_builder
```

#### `test_baseline_needs_ten_seconds_of_data`

```text
---- Summary ----
Main function to check that a run with less than 10 s of data in its baseline
window has no baseline, so its changes from baseline are blank while its averages
are kept, and that a baseline window cut at the start of the recording counts when
it still holds 10 s.

---- Inputs ----
None.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
A point every 0.5 min from 0 min; 2 min windows ending 0.5 min before the next
addition. First addition at 0.6 min: the baseline window ends at 0.1 min and is
cut at 0 min, where it holds one point (0 s of data), so there is no baseline;
the windows 5.5 to 7.5 and 9.5 to 11.5 min still average 5 and 2. First addition
at 1 min: the window is 0 to 0.5 min and holds two points 30 s apart, so it is
the baseline (mean 10) and the second window (5) is 50 % of it.

---- Helpers ----
_plateau_experiment_builder
```

#### `test_trimming_keeps_exactly_the_chosen_times`

```text
---- Summary ----
Main function to check that cutting a run at 2 and 7 min keeps the points from 2 to
7 min and no others, in the traces and in the spectra, and counts time from the cut.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Points at 0 to 10 min; kept: 2, 3, 4, 5, 6, 7 -> new times 0 to 5. Their values
(10 x old time) are 20 to 70; their spectrum numbers 3 to 8; the additions at 3 and
6 min move to 1 and 4 min.

---- Helpers ----
_ramp_experiment_builder
```

#### `test_trimming_moves_the_ignored_additions`

```text
---- Summary ----
Main function to check that after a cut at the start the ignored additions are
counted from the new zero like everything else, and that one made before the cut
gets a negative time.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Cut at 2 and 7 min; ignored additions at 1 and 5 min move to -1 and 3 min, as the
kept ones at 3 and 6 min move to 1 and 4 min.

---- Helpers ----
_ramp_experiment_builder
```

#### `test_trimming_never_cuts_an_addition`

```text
---- Summary ----
Main function to check that a cut that would lose an addition, or that ends before
it starts, is refused.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The additions are at 3 and 6 min, so a start at 4 min or an end at 5 min loses one.

---- Helpers ----
_ramp_experiment_builder
```

#### `test_trimming_the_end_only`

```text
---- Summary ----
Main function to check that cutting only the end at 7 min keeps the points from 0
to 7 min with their times unchanged.

---- Inputs ----
None.

---- Globals read ----
TIME_COLUMN, VO2_COLUMN (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Points at 0 to 10 min; kept: 0 to 7 (eight points), values 0 to 70.

---- Helpers ----
_ramp_experiment_builder
```

## `tests/test_program_version.py`

Tests that the program finds its version on dev and on main, where the release leaves .style/ out, and says beside it when its copy does not update itself.

### MAIN FUNCTIONS

#### `test_update_note_beside_the_version`

```text
---- Summary ----
Main function to check the note beside the version: a copy from a zip always says
it does not update itself, a git copy says what the launcher found (nothing when it
updates), and the Mac app says nothing here.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, standing in for the program folder.
monkeypatch : pytest.MonkeyPatch
    Sets and clears the launcher's note.

---- Globals read ----
UPDATE_NOTE_SWITCH (imported constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
update_note_finder
```

#### `test_version_from_style_folder`

```text
---- Summary ----
Main function to check that a folder with .style/VERSION (dev) takes its version
from there, even when the question list carries another one.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, standing in for the program folder.

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
```

#### `test_version_from_question_flow`

```text
---- Summary ----
Main function to check that a folder without .style/ (main, the user download)
takes its version from the title of QUESTION_FLOW.md.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, standing in for the program folder.

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
```

#### `test_version_unknown_without_either_file`

```text
---- Summary ----
Main function to check that a folder with neither file, or with a question list
whose title has no version, gives "unknown" instead of stopping the program.

---- Inputs ----
tmp_path : Path
    Empty folder given by pytest, standing in for the program folder.

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
```

## `tests/test_question_flow.py`

Tests that every question is in QUESTION_FLOW.md, worded and numbered as in the code.

### HELPERS

#### `_binding_resolver`

```text
---- Summary ----
Helper function to find the texts a local variable can hold, from its assignments
and from the loops that fill it out of a list written in the code.

---- Inputs ----
name : str
    Name of the variable.
function : ast.AST
    The function (or module) the variable lives in.
functions : List[ast.AST]
    The functions around the place the variable is used, nearest first.
seen : FrozenSet[str]
    Names already being followed, so a name defined by itself ends.

---- Globals read ----
None.

---- Outputs ----
Optional[List[str]]
    The texts, or None when any value cannot be read.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_text_resolver
```

#### `_carrier_finder`

```text
---- Summary ----
Helper function to find every function that takes a question: the askers and the
wrappers that hand a question on to them.

---- Inputs ----
trees : Dict[str, ast.Module]
    {file name: parsed code}.

---- Globals read ----
QUESTION_NAME (module constant).

---- Outputs ----
Dict[str, int]
    {function name: position of its question input}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_list_reader`

```text
---- Summary ----
Helper function to read the question list as plain text: without the marks for
italics, bold and code, and with single spaces.

---- Inputs ----
None.

---- Globals read ----
ROOT, LIST_NAME (module constants).

---- Outputs ----
str
    The text of the list.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_number_matcher`

```text
---- Summary ----
Helper function to say whether a question sits in the row of its own number in the
list, in the same words. The parts filled in at run time match any words within
that row's question.

---- Inputs ----
number : str
    The number the code gives the question, such as '3.5'.
question : str
    Question text from the code, with VARYING for each part filled in at run time.
list_text : str
    Text of the list from _list_reader.

---- Globals read ----
VARYING (module constant).

---- Outputs ----
bool
    True when the row of that number holds the question.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_question_collector`

```text
---- Summary ----
Helper function to collect the text of every question in the code, without running
it: the question given in each call to a function that takes one, with the number
written in that call, and each 'question' entry of a dictionary.

---- Inputs ----
None.

---- Globals read ----
NUMBER_NAME, QUESTION_NAME (module constants).

---- Outputs ----
Tuple[List[Tuple[str, str, Optional[str]]], List[str]]
    ([(question text, 'file:line', its own number or None)], ['file:line' of each
    question that could not be read]). VARYING stands for each part filled in at
    run time. A number handed on from another input is not one written in the call,
    so it gives None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_carrier_finder
_text_resolver
_tree_reader
```

#### `_question_matcher`

```text
---- Summary ----
Helper function to say whether a question is in the list in the same words. The
parts filled in at run time match any words.

---- Inputs ----
question : str
    Question text from the code, with VARYING for each part filled in at run time.
list_text : str
    Text of the list from _list_reader.

---- Globals read ----
VARYING (module constant).

---- Outputs ----
bool
    True when the question is in the list.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_text_resolver`

```text
---- Summary ----
Helper function to read the question texts an expression can give.

---- Inputs ----
node : ast.AST
    The expression given as the question.
functions : List[ast.AST]
    The functions around the expression, nearest first, the module last.
seen : FrozenSet[str]
    Names already being followed.

---- Globals read ----
QUESTION_NAME, VARYING (module constants).

---- Outputs ----
Optional[List[str]]
    The texts; an empty list for a question handed on from the function's own
    question input or read from a 'question' entry (it is collected where it is
    first written); None when the expression cannot be read.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_binding_resolver
```

#### `_tree_reader`

```text
---- Summary ----
Helper function to parse the program's code files and note, on every part, the
functions it sits in.

---- Inputs ----
None.

---- Globals read ----
ROOT, CODE_PATTERNS (module constants).

---- Outputs ----
Dict[str, ast.Module]
    {file name from the project folder: parsed code}. Every node has a
    ``functions`` list: the functions around it, nearest first, the module last.

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_question_texts_can_be_read`

```text
---- Summary ----
Main function to check that the text of every question can be read from the code,
so that none escapes the check against the list.

---- Inputs ----
None.

---- Globals read ----
MINIMUM_QUESTIONS (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_question_collector
```

#### `test_questions_are_in_the_list`

```text
---- Summary ----
Main function to check that every question in the code is in QUESTION_FLOW.md in
the same words.

---- Inputs ----
None.

---- Globals read ----
VARYING, LIST_NAME (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_list_reader
_question_collector
_question_matcher
```

#### `test_question_numbers_match_the_list`

```text
---- Summary ----
Main function to check that every question the code gives its own number sits in
the row of that number in QUESTION_FLOW.md, so the number on screen is the number
in the list.

---- Inputs ----
None.

---- Globals read ----
VARYING, LIST_NAME (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_list_reader
_number_matcher
_question_collector
```

## `tests/test_question_format.py`

Tests of the question format: what Enter gives at the end of each kind of question, the

### HELPERS

#### `_lines_reader`

```text
---- Summary ----
Helper function to give the printed lines without their colour codes or blank
lines.

---- Inputs ----
printed : str
    What the questions printed.

---- Globals read ----
CODE_PATTERN (module constant).

---- Outputs ----
List[str]
    The lines with text, without spaces at either end.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_typist_setter`

```text
---- Summary ----
Helper function to have the questions read the given answers, one per question
asked or wrong answer, in place of the window's answer box.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answer for the test only.
typed : List[str]
    The answers, in order; each is taken once.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. The reader of the questions is restored by monkeypatch.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_accept_question_shapes`

```text
---- Summary ----
Main function to check both shapes of a "Do you accept ...?" question: with one
way to change it is a yes or no question with what n does on the quiet line just
above; with more it is a numbered list starting "1) Yes, accept"; with none it is
refused.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

---- Globals read ----
COLOUR_QUIET.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_lines_reader
_typist_setter
accept_asker
```

#### `test_choice_endings`

```text
---- Summary ----
Main function to check the end of a question answered from a numbered list: every
number up to five options with the default brighter, a range beyond with the
default option brighter in the list, and one sentence after a wrong answer.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

---- Globals read ----
COLOUR_DEFAULT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_lines_reader
_typist_setter
choice_asker
```

#### `test_given_number_is_shown`

```text
---- Summary ----
Main function to check that a question given its own number shows exactly that
number, every time it is asked and at the indent of its depth, and leaves the
numbering of the other questions as it was; a number not like 3.5 is refused.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

---- Globals read ----
CODE_PATTERN (module constant); questions.INDENT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the numbering of the questions module (each test sets its own).

---- Equations ----
None.

---- Helpers ----
_lines_reader
_typist_setter
accept_asker
text_asker
yes_no_asker
```

#### `test_number_endings_and_hints`

```text
---- Summary ----
Main function to check a number question: [skip] or the default at the end, the
unit highlighted, and after a wrong answer one sentence giving the kind of number,
its limits and an example within them, the question waiting for the next answer.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

---- Globals read ----
COLOUR_RETRY, COLOUR_UNIT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_lines_reader
_number_hint_builder
_typist_setter
_unit_highlighter
number_asker
```

#### `test_several_numbers`

```text
---- Summary ----
Main function to check a question answered by several numbers: the quiet line just
above saying to separate them with commas, the numbers at the end, the options
Enter gives brighter in the list, and one sentence after a wrong answer.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

---- Globals read ----
COLOUR_DEFAULT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_lines_reader
_typist_setter
multi_asker
```

#### `test_table_instruction_waits`

```text
---- Summary ----
Main function to check an instruction carried out in a table: its quiet line above
it, its own number and no ending, and, when Confirm is pressed with the table not
yet filled in, the checker's one sentence while the instruction waits.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the window's Confirm.
capsys : pytest.CaptureFixture
    Captures what the instruction prints.

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
_lines_reader
_typist_setter
```

#### `test_text_question_waits`

```text
---- Summary ----
Main function to check that a text answer the checker refuses, the default given by
Enter included, gets the checker's sentence while the question waits, printed once.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

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
_lines_reader
_typist_setter
text_asker
```

#### `test_typed_number_reader`

```text
---- Summary ----
Main function to check the one reader of typed numbers: a point or a comma as the
decimal sign, spaces around it, and None for nothing, words, "nan" and infinities.

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
typed_number_reader
```

#### `test_yes_no_endings`

```text
---- Summary ----
Main function to check a yes or no question: (Y/n) or (y/N) with the letter Enter
gives brighter, y, yes, n and no in any capitals, and one sentence after a wrong
answer while the question waits.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answers.
capsys : pytest.CaptureFixture
    Captures what the questions print.

---- Globals read ----
COLOUR_DEFAULT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_lines_reader
_typist_setter
yes_no_asker
```

## `tests/test_redox_regions.py`

Tests that a haem's level in a region, % oxidised and an edge copied to another file

### MAIN FUNCTIONS

#### `test_a_level_is_the_median_in_the_region`

```text
---- Summary ----
Main function to check that a haem's level in a region is the median of its values
there, with the spectra at both edges counted, so that one spike does not set it
and a blank value is left out; and that a region with too few spectra, or one that
ends before it starts, is refused.

---- Inputs ----
None.

---- Globals read ----
RUN, OXIDISED_MIN, REDUCED_MIN, FEW (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Oxidised region, 0 to 4 min. bH: 12, 13, 11, 12, 30; in order 11, 12, 12, 13, 30,
so the median is 12 (the mean, 15.6, would follow the spike). cc: 6, 6, 8, 7 (the
blank left out); in order 6, 6, 7, 8, so the median is (6 + 7) / 2 = 6.5. a605: 5.
Reduced region, 6 to 9 min. bH: 4, 5, 3, 4; in order 3, 4, 4, 5, so the median is
4. cc: 2. a605: 5.
From 1 to 3 min bH is 13, 11, 12: median 12. From 1.5 to 3.5 min only the spectra
at 2 and 3 min are inside: two, fewer than three. From 0 to 2 min cc has only two
values (6, 6), as the one at 1 min is blank.

---- Helpers ----
None.
```

#### `test_a_file_needs_both_regions_for_its_levels`

```text
---- Summary ----
Main function to check the two levels of every haem of a file from the regions
kept for it: the regions are kept as times on the recording, so the trim start is
taken off; a region is kept within the used part of the run; and a file with no
regions, with only one, or with one that no longer holds enough spectra has no
levels. A region too short to count is closed.

---- Inputs ----
None.

---- Globals read ----
RUN, OXIDISED_MIN, REDUCED_MIN, FEW (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
The run was trimmed 2 min from its start, so its regions, 0 to 4 and 6 to 9 min
on the run, are 2 to 6 and 8 to 11 min on the recording. The levels are those of
test_a_level_is_the_median_in_the_region: bH 12 and 4, cc 6.5 and 2, a605 5 and 5.
With the first minute ignored the used part is 1 to 9 min, and the oxidised region
is kept to 1 to 4 min. bH: 13, 11, 12, 30; in order 11, 12, 13, 30, so the median
is (12 + 13) / 2 = 12.5. cc: 6, 8, 7 (the blank left out), median 7.
With the last two minutes ignored the used part ends at 7 min: the reduced region
is kept to 6 to 7 min, two spectra, fewer than three, so the file has no levels.
A region of 0.05 min with a least length of 0.1 min is closed at the edge that
opens it: the end of the oxidised region, the start of the reduced one.

---- Helpers ----
None.
```

#### `test_an_edge_is_copied_by_its_nearest_addition`

```text
---- Summary ----
Main function to check that an edge is copied to another file at the same distance
from the addition nearest to it, counted in order; that an edge before the first
addition goes by the first and one after the last by the last; and that a file
with fewer additions, or with none, gives no time.

---- Inputs ----
None.

---- Globals read ----
FIRST_FILE, LATER_FILE, SHORT_FILE (module constants).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Additions of the first file at 5, 12, 20 and 30 min; of the later file at 6, 13,
22 and 31 min.
An edge at 18.5 min is 13.5, 6.5, 1.5 and 11.5 min from the four additions, so the
third is nearest and the edge is 1.5 min before it: 20 - 1.5 = 18.5 min in the
first file again, 22 - 1.5 = 20.5 min in the later file. The short file has no
third addition.
An edge at 2 min is 3 min before the first addition: 6 - 3 = 3 min in the later
file. An edge at 33 min is 3 min after the fourth: 31 + 3 = 34 min.
An edge at 8.5 min is 3.5 min from both the first and the second addition: the
earlier is taken, so it is 3.5 min after the first: 6 + 3.5 = 9.5 min.

---- Helpers ----
None.
```

#### `test_percent_oxidised_runs_between_the_two_levels`

```text
---- Summary ----
Main function to check that % oxidised is 100 at the oxidised level and 0 at the
reduced one, with the right share in between; that values above 100 and below 0
are kept; that a haem whose two levels are equal has an empty column; and that a
haem without a level is refused.

---- Inputs ----
None.

---- Globals read ----
RUN, OXIDISED_MIN, REDUCED_MIN, FEW (module constants); TIME_COLUMN,
SPECTRUM_INDEX_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
percent = (D - D_red) / (D_ox - D_red) x 100, with the levels of
test_a_level_is_the_median_in_the_region.
bH: D_ox = 12, D_red = 4, so percent = (D - 4) / 8 x 100. D = 10 gives 6 / 8 x 100
= 75 %; 12, 13, 11, 12, 30, 10, 4, 5, 3, 4 give 100, 112.5, 87.5, 100, 325, 75, 0,
12.5, -12.5, 0.
cc: D_ox = 6.5, D_red = 2, so percent = (D - 2) / 4.5 x 100. 6, blank, 6, 8, 7, 5,
2, 2, 2, 2 give 800/9, blank, 800/9, 400/3, 1000/9, 200/3, 0, 0, 0, 0.
a605: D_ox = D_red = 5, so there is nothing to divide by: an empty column.

---- Helpers ----
None.
```

#### `test_the_least_spectra_of_the_program`

```text
---- Summary ----
Main function to check the least number of spectra the program asks of a region:
ten, which are 5 s of a run with a spectrum every 0.5 s; a region of nine is
refused.

---- Inputs ----
None.

---- Globals read ----
settings.REGION_MINIMUM_POINTS; TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Twenty spectra 0.5 s apart, at 0/120, 1/120, ... 19/120 min, with the values 1 to
20. From 0 to 9/120 min there are ten, 1 to 10: median (5 + 6) / 2 = 5.5. From 0
to 8/120 min there are nine.

---- Helpers ----
None.
```

## `tests/test_region_edges.py`

Tests that the edges of the oxidised and reduced regions start, move, stop, are copied

### TEST HELPERS

#### `_edge_setter`

```text
Helper function to set one edge with the limits of the made-up run. See
region_edge_setter.
```

### MAIN FUNCTIONS

#### `test_copy_to_every_file_or_one_file`

```text
---- Summary ----
Main function to check that an edge set on every file is set on the file shown
first and copied to the others by their additions, that a file with fewer
additions keeps what it had, and that an edge set on one file leaves the others
alone.

---- Inputs ----
None.

---- Globals read ----
ADDITIONS, PARKED (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Oxidised end set to 18.5 on 'one': 1.5 min before its 3rd addition (20). 'two':
22 - 1.5 = 20.5. 'few' has no 3rd addition: it keeps 5. Typed as 70 on 'one': it
stops at 55, which is 35 min after its 3rd addition; 'two' gets 22 + 35 = 57,
stopped at 55.

---- Helpers ----
_edge_setter
```

#### `test_edge_copied_by_its_nearest_addition`

```text
---- Summary ----
Main function to check the time an edge is copied to in another file: the same
distance from the addition of the same number, from the first addition for an edge
before it, and not at all to a file with fewer additions or from a file with none.

---- Inputs ----
None.

---- Globals read ----
ADDITIONS (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
18.5 on 'one' is 1.5 before its 3rd addition (20): 22 - 1.5 = 20.5 on 'two'. 7 on
'one' is 3 before its 1st (10): 11 - 3 = 8 on 'two', 9 - 3 = 6 on 'few'. 12 on
'one' is 2 after its 1st: 9 + 2 = 11 on 'few'.

---- Helpers ----
None.
```

#### `test_edges_stay_in_the_used_part`

```text
---- Summary ----
Main function to check that a region is pulled out from its side, that an edge
stops at the ends of the used part, and that an edge moved past the other edge of
its region pushes it along.

---- Inputs ----
None.

---- Globals read ----
PARKED (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Used part 5 to 55. Oxidised end to 12: 5 to 12. Reduced start to 40: 40 to 55.
Oxidised end to 2: stops at 5, so 5 to 5. Reduced end to 70: stops at 55. Oxidised
start to 20 with the end at 12: the end is pushed to 20. Reduced end to 30 with
the start at 40: the start is pushed to 30.

---- Helpers ----
_edge_setter
```

#### `test_layout_of_the_regions`

```text
---- Summary ----
Main function to check the handles, their words and the shading: one handle
reading "not chosen" and no shading for a region not chosen, two edges and one
shaded part for a chosen one, and a region shorter than the least length drawn as
not chosen.

---- Inputs ----
None.

---- Globals read ----
PARKED, MINIMUM_MIN (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Least length 0.5 min: 5 to 12.25 is chosen, 54.6 to 55 (0.4 min) is not, 54.5 to
55 (0.5 min) is.

---- Helpers ----
None.
```

#### `test_pointer_gives_the_time_in_steps`

```text
---- Summary ----
Main function to check that a time pointed at gives the edge in steps of 0.1 min.

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
12.34 -> 12.3; 12.36 -> 12.4.

---- Helpers ----
None.
```

#### `test_regions_a_file_ends_with`

```text
---- Summary ----
Main function to check the regions read from the edges: none for a file left as it
started, one alone (which the program counts as none) and both.

---- Inputs ----
None.

---- Globals read ----
PARKED, MINIMUM_MIN (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_regions_never_overlap`

```text
---- Summary ----
Main function to check that an edge moved into the other region stops at its
nearer side, that past its middle it comes out on the far side with the edge not
being set giving way, and that a region not chosen is in nobody's way.

---- Inputs ----
None.

---- Globals read ----
PARKED (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Reduced 20 to 30, oxidised not chosen at 5. Oxidised end to 22 (2 from 20, 8 from
30): stops at 20, so 5 to 20. Oxidised end to 27 (7 from 20, 3 from 30): goes to
30, and the start gives way to 30, so 30 to 30, not chosen. Oxidised end to 40:
the reduced region would lie inside 5 to 40, so the start gives way to 30: 30 to
40. Then the oxidised start to 10: the end gives way to 20: 10 to 20. With the
reduced region not chosen (55 to 55), the oxidised end goes to 55.

---- Helpers ----
_edge_setter
```

#### `test_shaded_regions`

```text
---- Summary ----
Main function to check that the oxidised region is shaded see-through red and the
reduced one see-through blue on a white picture.

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
At 18 % (46 of 255) over white, 255 - (255 - channel) * 46 / 255. Red #d62728 =
(214, 39, 40): (247.6, 216.0, 216.2), so (248, 216, 216). Blue #1f77b4 = (31, 119,
180): (214.6, 230.5, 241.5), so (215, 230, 241).

---- Helpers ----
None.
```

#### `test_starting_edges`

```text
---- Summary ----
Main function to check the edges a file starts with: both regions not chosen at
the sides of the used part, or the regions remembered, kept within the used part,
one that no longer fits being not chosen again.

---- Inputs ----
None.

---- Globals read ----
USED_SPAN, MINIMUM_MIN, PARKED (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Remembered oxidised 2 to 12 and reduced 56 to 60, used part 5 to 55: the oxidised
region becomes 5 to 12; the reduced one becomes 55 to 55, so it is parked at 55.

---- Helpers ----
None.
```

## `tests/test_run_logging.py`

Tests the run's log, which keeps the answers from the results folder on, and the

### TEST HELPERS

#### `_typist_maker`

```text
---- Summary ----
Helper function to make a stand-in for the window's answer box: it gives the typed
answers in turn, then ends the input as closing the window does.

---- Inputs ----
typed : List[str]
    The answers, in order; the list is emptied as they are given.

---- Globals read ----
None.

---- Outputs ----
Callable[..., str]
    Function that takes the place of input.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_fresh_numbering`

```text
---- Summary ----
Helper function (a pytest fixture) to give the questions their own numbering while
a test runs, so other tests keep theirs.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Puts the numbering back after the test.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Replaces the questions' counters while the test runs.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_answers_are_logged_as_they_come`

```text
---- Summary ----
Main function to check that the log starts with the version and the folders, then
holds each question with its answer under it, without the window's colour codes,
then the settings, and only then what the run prints.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Stands in for the answer box.
_fresh_numbering : None
    Gives the questions their own numbering.

---- Globals read ----
TITLE (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_typist_maker
answer_logger
logging_starter
logging_stopper
settings_logger
yes_no_asker
```

#### `test_closed_window_keeps_the_log`

```text
---- Summary ----
Main function to check that when the window is closed part way through the
questions, the answers given so far stay in the log, which is closed and gives the
terminal back.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
monkeypatch : pytest.MonkeyPatch
    Stands in for the answer box.
_fresh_numbering : None
    Gives the questions their own numbering.

---- Globals read ----
TITLE (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_typist_maker
logging_starter
logging_stopper
yes_no_asker
```

#### `test_launch_log_keeps_the_starts_before`

```text
---- Summary ----
Main function to check that each start is added to the launch log under its own
start line, after the starts before.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
launch_log_opener
```

#### `test_launch_log_is_cut_past_its_limit`

```text
---- Summary ----
Main function to check that a launch log past its limit keeps only its newest
half, from a start line, before the new start is added.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
launch_log_opener
```

## `tests/test_summary_maths.py`

Tests that the averaged spectra, their difference and the averages over repeated runs

### HELPERS

#### `_run_builder`

```text
---- Summary ----
Helper function to build one run that already has its averages, as the averaging
step leaves them.

---- Inputs ----
name : str
    Name of the run, ending in 'run<number>'.
means : dict
    {window name: mean of the oxygen consumption in that window}.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
dict
    Experiment with 'averages'. In each window the spread is 0.1, the change is
    10 x the mean and the difference is the mean - 1.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_spectra_experiment_builder`

```text
---- Summary ----
Helper function to build an experiment whose spectra change at each of two
additions.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
dict
    Experiment with a spectrum of three wavelengths every 0.5 min from 0 to
    12 min and additions at 4 and 8 min. Before 4 min a spectrum is (t, 2 t, 0),
    with t its time; from 4 to 8 min it is (1, 2, 3); from 8 min on (0.5, 1, 4).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `test_averaged_spectra_around_the_additions`

```text
---- Summary ----
Main function to check the average spectrum, and its spread, in the window before
each addition and in the last window.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
2 min windows ending 0.5 min before the next addition (or the end): 1.5 to 3.5,
5.5 to 7.5 and 9.5 to 11.5 min, five spectra each. In the first, t = 1.5, 2, 2.5,
3, 3.5: mean 2.5, spread sqrt((1 + 0.25 + 0 + 0.25 + 1) / 4) = 0.7906, so the
spectrum (t, 2 t, 0) averages to (2.5, 5, 0) with spread (0.7906, 1.5811, 0).

---- Helpers ----
_spectra_experiment_builder
```

#### `test_baseline_starts_with_the_recording`

```text
---- Summary ----
Main function to check that the baseline window of the averaged spectra starts
where the recording starts when the window would begin before it, as the windows
of the processing do.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Additions at 2 and 8 min, 2 min windows ending 0.5 min before the next addition:
the baseline ends at 1.5 min and would start at -0.5 min, so it starts at 0. Its
spectra are at t = 0, 0.5, 1 and 1.5 min: mean 0.75, so (t, 2 t, 0) averages to
(0.75, 1.5, 0). The next window runs from 5.5 to 7.5 min, after the addition at 2.

---- Helpers ----
_spectra_experiment_builder
```

#### `test_difference_of_two_known_spectra`

```text
---- Summary ----
Main function to check that the difference spectrum is the first averaged spectrum
minus the second, for the usual pair (before and after the last addition) and for
a pair chosen by name.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
(1, 2, 3) - (0.5, 1, 4) = (0.5, 1, -1); (2.5, 5, 0) - (1, 2, 3) = (1.5, 3, -3).

---- Helpers ----
_spectra_experiment_builder
```

#### `test_difference_needs_its_averages`

```text
---- Summary ----
Main function to check that a difference is refused when the averaged spectra have
not been worked out, when a window does not exist, and when the last window does
not fit after the last addition.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
A 4 min window ending at 11.5 min starts at 7.5 min, before the addition at 8 min.

---- Helpers ----
_spectra_experiment_builder
```

#### `test_average_over_three_runs`

```text
---- Summary ----
Main function to check the mean, spread, standard error and number of runs over
three repeats, and that a run without a window is left out of that window only.

---- Inputs ----
None.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
First window: 1, 2, 3 -> mean 2, spread sqrt((1 + 0 + 1) / 2) = 1, standard error
1 / sqrt(3) = 0.5774, N 3. Second window (run 3 has none): 4, 6 -> mean 5, spread
sqrt((1 + 1) / 1) = 1.4142, standard error 1.4142 / sqrt(2) = 1, N 2. The changes
are 10 x the means, the differences the means - 1.

---- Helpers ----
_run_builder
```

#### `test_average_needs_two_runs`

```text
---- Summary ----
Main function to check that a condition with a single run gives no average, and
that two runs give a mean and spread but are kept apart from other conditions.

---- Inputs ----
None.

---- Globals read ----
VO2_COLUMN (module constant).

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
Knockdown: 10, 20 -> mean 15, spread sqrt((25 + 25) / 1) = 7.0711, N 2.

---- Helpers ----
_run_builder
```

## `tests/test_time_pointer.py`

Tests that the mouse over a preview gives the times and answers worked out by hand,

### MAIN FUNCTIONS

#### `test_pointed_time_inside_the_panels`

```text
---- Summary ----
Main function to check the time under the mouse in the middle and at both ends of
the time axis, for an axis that starts at zero and one that does not.

---- Inputs ----
None.

---- Globals read ----
PICTURE_BOX, TIME_AXIS (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
x = 500 is half way along the axis (200 to 800): 30 min. With an axis from 10 to
50 min, x = 350 is a quarter of the way: 10 + 0.25 * 40 = 20 min.

---- Helpers ----
None.
```

#### `test_pointed_time_off_the_panels`

```text
---- Summary ----
Main function to check that no time is given left or right of the time axis, above
or below the panels, or for a picture with no size.

---- Inputs ----
None.

---- Globals read ----
PICTURE_BOX, TIME_AXIS (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_pointed_time_on_a_scaled_picture`

```text
---- Summary ----
Main function to check that the time follows the picture when it is shown at
another size and place.

---- Inputs ----
None.

---- Globals read ----
TIME_AXIS (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
A picture 1600 x 800 at (0, 0): the axis runs from x = 200 to 1400, so x = 500 is
a quarter of the way: 15 min.

---- Helpers ----
None.
```

#### `test_question_wanting_a_time_tells_the_window`

```text
---- Summary ----
Main function to check that a number question the mouse can answer hands its rule
to the registered window before it reads (a drag rule as 'span') and takes it back
once it has a valid answer, that other number questions leave the window alone,
and that a question still works when no window is registered (the window has
closed).

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Replaces the reading of the answer and restores the module state afterwards.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. The registered function of the questions is restored by monkeypatch.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_time_axis_of_a_figure`

```text
---- Summary ----
Main function to check that the time axis of a figure is found from the panels
that share the x axis of the first one, and that a figure with no panel has none.

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
Two panels from 0.2 to 0.9 of the width, the lower from 0.1 and the upper to 0.9
of the height, showing 0 to 45 min; a small panel with its own x axis is left out.

---- Helpers ----
None.
```

## `tests/test_trim_edges.py`

Tests that the edges of the trimming step move, stop and shade as worked out by hand.

### MAIN FUNCTIONS

#### `test_edge_under_the_mouse`

```text
---- Summary ----
Main function to check which edge the mouse takes: by its handle in either row, by
its line, the inner edge where two lines meet, and none away from the lines or
below the panels.

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
Handles from y = 10: the top row to 32, the lower row to 54; a handle is 9 px wide,
so it is taken within 4.5 + 2 px. A line is taken within 6 px, from y = 10 to the
bottom of the panels at 300.

---- Helpers ----
None.
```

#### `test_every_file_or_one_file`

```text
---- Summary ----
Main function to check that an edge set on every file gives each file the same
minutes within its own limits, that one set on one file leaves the others alone,
and that the files whose minutes differ from most files are found.

---- Inputs ----
None.

---- Globals read ----
LONG, SHORT, NOTHING (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
8 min trimmed from the start: the 60 min files keep 8, the 40 min one stops at its
first addition, 5. Only on 'long': the others keep 0.

---- Helpers ----
None.
```

#### `test_ignored_parts_stay_inside_the_kept_part`

```text
---- Summary ----
Main function to check that the ignored parts never cross, that the one on the side
of the edge being set gives way, and that minutes below 0 count as 0.

---- Inputs ----
None.

---- Globals read ----
LONG (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Trimmed 4 and 6 min: 50 min kept. Ignore the first 45: allowed. Ignore the last 10:
only 50 - 45 = 5 fit. Trim 10 from the start: 44 min kept, so the first ignored
part gives way to 44 - 5 = 39 and the last keeps 5.

---- Helpers ----
None.
```

#### `test_layout_of_the_edges_and_parts`

```text
---- Summary ----
Main function to check where the four edges sit on the whole recording, the words
by their handles, and the parts shaded.

---- Inputs ----
None.

---- Globals read ----
LONG (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Trimmed 4 and 5, ignored 6 and 3 on 60 min: edges at 4, 60 - 5 = 55, 4 + 6 = 10
and 55 - 3 = 52.

---- Helpers ----
None.
```

#### `test_minutes_and_places_on_the_plot`

```text
---- Summary ----
Main function to check that a time is turned into its place across the plot area
and back, and that a place beyond the panels gives the time at their edge.

---- Inputs ----
None.

---- Globals read ----
PICTURE_BOX, TIME_AXIS (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
The axis runs from x = 200 to 800 for 0 to 60 min: 30 min at x = 500, 12.3 min at
200 + 12.3 / 60 * 600 = 323.

---- Helpers ----
None.
```

#### `test_minutes_typed_in_the_strip`

```text
---- Summary ----
Main function to check which numbers of minutes the boxes of the strip take.

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
```

#### `test_minutes_to_limits_and_back`

```text
---- Summary ----
Main function to check that the starting minutes come from the limits remembered,
or from the standard settings, kept within the file's limits, and that minutes
turned into limits give the same minutes back.

---- Inputs ----
None.

---- Globals read ----
config.DEFAULT_ANSWERS (5 min ignored at the start, checked first); LONG, SHORT
(module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
'long' remembered as kept from 3 to 57 min: 3 and 60 - 57 = 3 trimmed. 'short'
remembered with 20 min trimmed from its start: it stops at its first addition, 5.
'other' has nothing remembered: the standard settings. Back as limits: a trim of 0
is None, the trim end is 60 - 3 = 57.

---- Helpers ----
None.
```

#### `test_pointer_gives_the_minutes_of_each_edge`

```text
---- Summary ----
Main function to check that a time pointed at on the whole recording gives the
minutes that put each edge there, in steps of 0.1 min, and 0 beyond the edge.

---- Inputs ----
None.

---- Globals read ----
LONG, NOTHING (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Trimmed 4 and 5 min of 60. Trim start at 4.04 -> 4.0. Trim end at 55 -> 60 - 55 =
5. Ignore start at 9.5 -> 9.5 - 4 = 5.5. Ignore end at 50 -> 55 - 50 = 5. Ignore
start at 2, in the trimmed part: 0. Trim end at 61, past the end: 0.

---- Helpers ----
None.
```

#### `test_shaded_picture`

```text
---- Summary ----
Main function to check that a shaded part is see-through amber on a white picture,
that the rest of the picture is untouched, and that a part narrower than a pixel is
left out.

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
Amber #e8a317 = (232, 163, 23) at 22 % (56 of 255) over white:
255 - (255 - channel) * 56 / 255 = (249.95, 234.8, 204.05), so (250, 235, 204).

---- Helpers ----
None.
```

#### `test_trimmed_edges_stop_at_the_events`

```text
---- Summary ----
Main function to check that a trimmed edge never cuts off an addition.

---- Inputs ----
None.

---- Globals read ----
LONG, NOTHING (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
Additions at 10 and 50 of 60 min: at most 10 min trimmed from the start and 60 - 50
= 10 from the end.

---- Helpers ----
None.
```

## `tests/test_user_notices.py`

Tests of the plain sentences for warnings and problems, with their details in the log.

### TEST HELPERS

#### `_caught_getter`

```text
---- Summary ----
Helper function to run an action that fails and give its error, with its traceback.

---- Inputs ----
action : Callable[[], object]
    Function without inputs that raises.

---- Globals read ----
None.

---- Outputs ----
BaseException
    The error it raised.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_quiet_details`

```text
---- Summary ----
Helper function (a pytest fixture) to send the details of a problem to a made-up
log while a test runs, and to send them nowhere afterwards.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Iterator[io.StringIO]
    The made-up log, named "the test log" for the user.

---- Globals mutated ----
None. Sets the place for the details, and clears it after the test (side effects).

---- Equations ----
None.

---- Helpers ----
details_place_setter
```

### MAIN FUNCTIONS

#### `test_details_go_to_the_log_only`

```text
---- Summary ----
Main function to check that a problem Portimao did not expect gives one sentence
naming the log, with Python's report of it in the log and nowhere else.

---- Inputs ----
_quiet_details : io.StringIO
    The made-up log.
capsys : pytest.CaptureFixture
    What the test printed.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_caught_getter
problem_teller
```

#### `test_own_message_is_shown_as_it_is`

```text
---- Summary ----
Main function to check that a message Portimao's own code wrote for the user (here
the trimming's, raised over several lines) is shown as it is.

---- Inputs ----
_quiet_details : io.StringIO
    The made-up log.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_caught_getter
experiment_trimmer
problem_describer
```

#### `test_python_text_is_never_shown`

```text
---- Summary ----
Main function to check that Python's own error text is never shown: neither for a
plain step in Portimao's code that fails (a time that is not a number, a missing
name) nor for an error raised inside a package or in a test.

---- Inputs ----
_quiet_details : io.StringIO
    The made-up log.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_caught_getter
experiment_trimmer
problem_describer
```

#### `test_file_problems_say_what_to_do`

```text
---- Summary ----
Main function to check the sentences for a file open in another program, a missing
file, another file problem and a lack of memory: each names the file, without its
folders, and says what to do.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.
_quiet_details : io.StringIO
    The made-up log.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_caught_getter
problem_describer
```

#### `test_run_log_takes_the_details`

```text
---- Summary ----
Main function to check that while a run is logged the details go to its log, which
is named for the user, and that afterwards they go back to the start-up place.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest, standing in for the results folder.
_quiet_details : io.StringIO
    The made-up start-up log.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
details_writer
logging_starter
logging_stopper
```

#### `test_warnings_are_kept_whatever_their_words`

```text
---- Summary ----
Main function to check that while the output is captured (a preview) every warning
is kept as a warning, whatever its words, ordinary lines are not, and the details of
a problem are never printed.

---- Inputs ----
_quiet_details : io.StringIO
    The made-up log.
capsys : pytest.CaptureFixture
    What the test printed (pytest's own stream does not honour the capture).

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_caught_getter
output_capturer
problem_shower
warning_shower
```

## `tests/test_user_places.py`

Tests that the user's own things are kept in the program folder from source and in the

### HELPERS

#### `_app_places_maker`

```text
---- Summary ----
Helper function to make a pretend app (its program folder holding two fits) and a
pretend home folder, and give the app's places.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
SHIPPED_FITS (module constant).

---- Outputs ----
UserPlaces
    The places of the app, with its own folder in the pretend home folder.

---- Globals mutated ----
None. Writes the folders and fits (side effect).

---- Equations ----
None.

---- Helpers ----
user_places_finder
```

### MAIN FUNCTIONS

#### `test_app_keeps_things_in_home_folder`

```text
---- Summary ----
Main function to check that the app keeps the fits, the folder used last and the
logs in a Portimao folder in the home folder, and reads its own files from inside
the app.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_app_places_maker
```

#### `test_app_never_overwrites_a_fit`

```text
---- Summary ----
Main function to check that the app makes its folders, copies in the fit that is
missing (the haem library and the presets in their own folders), and leaves a fit
the user changed as it is, also when it starts again.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_app_places_maker
user_folder_preparer
```

#### `test_source_keeps_things_in_program_folder`

```text
---- Summary ----
Main function to check that, run from source, everything stays in the program
folder, as before the app, and that preparing the places changes nothing there.

---- Inputs ----
tmp_path : Path
    Empty folder from pytest.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
user_folder_preparer
user_places_finder
```

#### `test_source_program_folder_is_found`

```text
---- Summary ----
Main function to check that, run from source with nothing given, the program
folder found is the one holding main.py.

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
user_places_finder
```

## `tests/test_window_parts.py`

Tests of the parts of the window that need no window: the widths a journal allows, the

### MAIN FUNCTIONS

#### `test_cells_of_the_tables`

```text
---- Summary ----
Main function to check the three kinds of cell: a number above 0 (with a point or
a comma), a number of 0 or more, and a label without its outer spaces; an empty
cell is "not filled in" and never wrong; words, numbers below the limit and
numbers that are not finite are wrong.

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
```

#### `test_event_labels_from_the_table`

```text
---- Summary ----
Main function to check the labels as the table is confirmed: a label written
ignore in any capitals leaves its event out and drops its concentration; a label
that could be tidier is offered once, and one kept as it is is not offered again.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the answer box.

---- Globals read ----
SUMMARIES (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_rows_of_the_labels_table`

```text
---- Summary ----
Main function to check the labels table: it starts from the saved label, or else
the file's own text, with ignore for an event left out; it has one row per event
under its file's name, none for a file without events; and the typed labels and
concentrations go back to the right events, a label left empty keeping its own.

---- Inputs ----
None.

---- Globals read ----
SUMMARIES (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_rows_of_the_od_table`

```text
---- Summary ----
Main function to check the OD table: one row per file named by the file, a value
written as short as it goes and a missing one as an empty cell, and the typed
values read back per file.

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
```

#### `test_sentence_when_confirmed_too_early`

```text
---- Summary ----
Main function to check the one sentence said when Confirm is pressed with cells
that cannot be used (named first, with what to type) or needed cells left empty,
naming five cells at most and counting the others, and none when the table can be
used.

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
```

#### `test_height_typed_in_the_strip`

```text
---- Summary ----
Main function to check that a height between 0 and 1 is taken and written in
millimetres on the page of the journal, and that 0, a height over a page and words
are refused with a reason.

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
A Nature page is 170 mm: 0.5 of it is 85 mm and the whole is 170 mm. A Science
page is 230 mm: 0.25 of it is 57.5 mm. "None" uses the Nature page.

---- Helpers ----
None.
```

#### `test_the_decomposition_kept_to_compare`

```text
---- Summary ----
Main function to check that keeping a decomposition keeps its fit as it is, the
answers it was worked out with (the fit, the background, the spectrometer and the
numbers of delta psi, and nothing else), a copy of the regions that later changes
leave alone, and its name in words, for a fit file and for haems ticked under
Build a fit, with delta psi on and off and without regions.

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
```

#### `test_keep_to_compare_keeps_the_regions_in_use`

```text
---- Summary ----
Main function to check that a click on Keep to compare keeps the fit, the regions
and the numbers of delta psi in use at that moment and redraws the plot, and that
Keep this one drops them. The showing of the strip is stood in for.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the showing of the strip.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. The stand-in is undone after the test.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_go_back_to_kept_puts_the_kept_one_back`

```text
---- Summary ----
Main function to check the two ways of choosing after Keep to compare. Go back to
kept puts the kept fit, background, number of delta psi and regions back in use,
drops the kept one and redraws the plot; while the regions are being chosen on the
plot it leaves the regions as they are; with nothing kept it does nothing. Keep
this one leaves what is in use as it is and drops the kept one. The strip tells
the click on Go back to kept only while one is kept. The showing of the strip is
stood in for.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the showing of the strip.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. The stand-in is undone after the test.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_answers_shown_in_the_strip`

```text
---- Summary ----
Main function to check that the answers of a run are shown in the strip as they
are meant (the standard size as the journal "None", a chosen journal by its name,
the box ticked only when the haems are worked out, the OCR per OD box ticked only
for the OCR per OD), that the strip can show them, and that its journal, width and
height give the same answers back.

---- Inputs ----
None.

---- Globals read ----
settings.DEFAULT_ANSWERS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_values_meant_for_the_strip`

```text
---- Summary ----
Main function to check that values the strip can show pass, and that an unknown
name, an unknown journal, a width the journal does not allow, a height over a page,
an unknown background, haems ticked that are not a list of names, a comparing that
is not True or False, a kept decomposition not in words, a spectrometer not given
by its name, a way of showing the haems the strip does not have and a per OD box
that is not True or False are each refused.

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
```

#### `test_numbers_of_the_delta_psi_row`

```text
---- Summary ----
Main function to check the Δψ row of the strip: the midpoints filled in from the
ones typed and the fall, the answers a change gives, the sentence that says it,
the row shown only with the haems and Δψ switched on, the numbers refused with a
reason, the values the strip cannot show, and what the row keeps and tells when a
number is typed, refused, or the paper's values are put back (not the
temperature).

---- Inputs ----
None.

---- Globals read ----
settings.DEFAULT_ANSWERS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
second = first - fall. The paper's: 40 - 70 = -30 and -20 - 70 = -90. A fall of 60
typed: 40 - 60 = -20 and -20 - 60 = -80. bH typed as 50 with the fall of 70 kept:
50 - 70 = -20, and bL stays at -20 and -90. From answers of 50 and -20 the fall
shown is 50 - (-20) = 70.

---- Helpers ----
None.
```

#### `test_haems_and_ocr_shown_from_the_strip`

```text
---- Summary ----
Main function to check the "Haems as" drop-down and the per OD boxes: % oxidised is
in the list only when a file has both regions, and the spectrometer, the way of
showing the haems and the two boxes give the answers of the run (the OCR per OD
box ticked is the OCR per OD, unticked the plain OCR), only for what changed.

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
```

#### `test_plots_follow_the_strip`

```text
---- Summary ----
Main function to check the answers each kind of plot is drawn with: the standard
and the processing plot show the haems and the OCR as the answers say (the strip
sets them), per OD only once OD values were entered; the figure of each file is
drawn with the answers as they are.

---- Inputs ----
None.

---- Globals read ----
settings.DEFAULT_ANSWERS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_haems_ticked_in_the_strip`

```text
---- Summary ----
Main function to check the tick boxes of Build a fit: a haem ticked is added; a
haem with the same name as one ticked takes its place, with a note naming both; a
haem unticked is taken away; the last cannot be unticked, with a note; and a box
not ticked before changes nothing when unticked.

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
```

#### `test_widths_of_each_journal`

```text
---- Summary ----
Main function to check that the widths offered are those of the journal in the
settings, in their order and with their millimetres, and that "None" offers the
widths of the standard journal.

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
Nature allows 1 column (89 mm), 1.5 columns (120 mm) and 2 columns (183 mm).

---- Helpers ----
None.
```

#### `test_time_title_of_a_preview`

```text
---- Summary ----
Main function to check that a preview's time axis says "in the recording" while
trimming and for a file whose start is not trimmed, and "from the trimmed start"
once a file trimmed at its start is drawn trimmed.

---- Inputs ----
None.

---- Globals read ----
settings.PREVIEW_TIME_TITLES.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_files_drawn_beside_the_one_shown`

```text
---- Summary ----
Main function to check which files the window keeps read and redraws after an
answer: the file shown, then the nearest ones around the list, the next one before
the previous one, never more than there are files.

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
```

#### `test_files_kept_in_memory`

```text
---- Summary ----
Main function to check that the window keeps the three files around the one shown
read: a file read for every file at once (as the component finder does) is let go
without dropping them, a kept file is not read again, and moving on by one reads
only the new neighbour. The reading of a file is stood in.

---- Inputs ----
monkeypatch : pytest.MonkeyPatch
    Stands in for the file reader and sets the number of files kept.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. The stand-ins are undone after the test.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `test_wheel_turn_on_each_system`

```text
---- Summary ----
Main function to check that a turn of the mouse wheel scrolls a table the right
way on Windows (steps of 120), the Mac (small steps) and Linux (buttons 4 and
5), and not at all for an event that says neither.

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
```

## `utils_custom/custom_config.py`

Settings dictionaries of the custom figures, built from the terminal answers.

### MAIN FUNCTIONS

#### `exemplar_config_builder`

```text
---- Summary ----
Main function to build the settings of the four-run exemplar figure.

---- Inputs ----
cfg : Config
    Figure style derived from the answers (config.py).
answers : dict
    Terminal answers; uses ho_exemplar_run, ho_ex_columns and ho_ex_height.

---- Globals read ----
ORDER_COLUMNS, STRAIN_ROWS, SAVE_FORMATS.

---- Outputs ----
dict
    Settings for exemplar_figure_plotter and custom_figure_saver.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
```

#### `haem_labeller`

```text
---- Summary ----
Main function to give a haem its short y-axis label, for example '$b_H$'.

---- Inputs ----
haem_name : str
    Haem name as written in the fit file, for example 'Cyt bH'.

---- Globals read ----
HAEM_LABELS (module constant).

---- Outputs ----
str
    Short label; the haem name itself when it is not a known haem.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `individual_config_builder`

```text
---- Summary ----
Main function to build the individual-experiment plot settings used inside the
custom figures: oxygen, OCR and one panel per chosen haem.

---- Inputs ----
answers : dict
    Terminal answers (journal, size and label angle are taken from them).
vo2_source : str
    OCR source plotted: 'raw' or 'od'.
haem_source : str
    Haem source plotted, for example 'delta_abs_od'.
haem_names : list
    Haem names, in panel order, matching the decomposition columns.

---- Globals read ----
None.

---- Outputs ----
dict
    Plot settings in the format of Config.plot_config.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
plot_config_builder
```

#### `ocr_and_haem_response_config_builder`

```text
---- Summary ----
Main function to build the settings of the OCR and haem response figure.

---- Inputs ----
cfg : Config
    Figure style derived from the answers (config.py).
answers : dict
    Terminal answers; uses ho_haems, ho_metric, ho_pub_columns and ho_pub_height,
    and ho_blocks (the blocks drawn so far while the figure is being built).
haem_names : list
    Haem names of the fit, in fit order.

---- Globals read ----
ORDER_COLUMNS, STRAIN_ROWS, GROUP_STYLES, SAVE_FORMATS.

---- Outputs ----
dict
    Settings for ocr_and_haem_response_figure_plotter and custom_figure_saver.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
haem_labeller
```

#### `source_selector`

```text
---- Summary ----
Main function to choose the OCR and haem data sources of the haem and OCR response
figures from the answers.

---- Inputs ----
answers : dict
    Terminal answers; uses ho_ocr_mode ('raw', 'od' or 'percent'), ho_haem_mode
    ('delta', 'abs' or 'percent') and ho_per_od.
od_available : bool
    True when the experiment has OD, volume and dilution factor.

---- Globals read ----
None.

---- Outputs ----
tuple
    (vo2_source, haem_source) as used by the averaging and plotting code, for
    example ('od', 'delta_abs_od'). OD sources are only chosen when od_available.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `time_response_config_builder`

```text
---- Summary ----
Main function to build the settings of the time response figure.

---- Inputs ----
cfg : Config
    Figure style derived from the answers (config.py).
answers : dict
    Terminal answers; uses tr_groups, tr_examples, tr_decompositions,
    tr_skip_hours, tr_columns and tr_height. An example that is None has not been
    chosen yet (the figure is being built) and is drawn as an empty box.
haem_names : list
    Haem names of the fit, used to colour the decomposition panels.

---- Globals read ----
SAVE_FORMATS.

---- Outputs ----
dict
    Settings for time_response_figure_plotter, custom_figure_saver and
    time_response_exporter.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
haem_colour_mapper
```

## `utils_custom/custom_figure_saver.py`

Saving of the custom figures into the results folder.

### MAIN FUNCTIONS

#### `custom_figure_saver`

```text
---- Summary ----
Main function to save one of the custom figures (2x2, OCR and haem response, time
response) at its exact size in the results folder.

---- Inputs ----
fig : Figure
    Figure returned by one of the custom figure plotters.
export_root : Path
    Results folder; the files are written straight into it.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Paths of the files written.

---- Globals mutated ----
None. Writes the figure files (side effect).

---- Equations ----
None.

---- Helpers ----
figure_saver
```

## `utils_custom/custom_questions.py`

Numbered terminal questions of the time response and the OCR and haem response.

### CUSTOM QUESTIONS HELPERS

#### `_example_pair_maker`

```text
---- Summary ----
Helper function to describe an experiment as the (group, hours) pair that is saved
with the answers.

---- Inputs ----
members : dict
    {experiment name: group}.
name : str
    Experiment name with the hours in it, e.g. 'control_7hours'.

---- Globals read ----
None.

---- Outputs ----
list
    [group, hours] of the experiment.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `_haem_ocr_asker`

```text
---- Summary ----
Helper function to ask the settings of the haem and OCR response figure (7.2.x).
The figure averages files together, so the haems are offered in % oxidised only
when every file of the figure has an oxidised and a reduced region.

---- Inputs ----
names : List[str]
    Experiment names (file names without the extension).
answers : dict
    Answers dictionary the settings are stored in.
defaults : dict
    Default answers; % oxidised as the default gives delta D when it is not
    offered.
fit : dict
    Fit dictionary (haem_list) used to list the haems.
percent_names : Optional[List[str]]
    Names of the files with both regions; None when no file has them.
step_checker : Optional[Callable[[object, str, str], bool]]
    Function (names, question, change label) that draws the figure as built so far,
    asks whether it is accepted and returns True when it is; None skips the
    previews.

---- Globals read ----
None.

---- Outputs ----
Optional[List[str]]
    Names of the experiments that belong to the figure, or None when it cannot be
    made from these files.

---- Globals mutated ----
None. Stores the settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_step_checker
choice_asker
haem_form_option_builder
haem_name_formatter
info_printer
multi_asker
ocr_option_builder
run_name_lister
size_asker
yes_no_asker
```

#### `_hours_reader`

```text
---- Summary ----
Helper function to read the hours typed for the time points to skip.

---- Inputs ----
text : str
    Numbers separated by commas or semicolons, or "none".

---- Globals read ----
None.

---- Outputs ----
List[float]
    The hours. Words that are not numbers are reported and left out.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
info_printer
```

#### `_panel_chooser`

```text
---- Summary ----
Helper function to ask which experiment a panel of the time response shows, put it
in the figure and ask whether the figure so far is accepted.

---- Inputs ----
question : str
    The question.
options : list
    [(experiment name, text)] to choose from.
default : str
    Experiment offered when only Enter is pressed.
slot : tuple
    (list the pair is stored in, position in that list, {experiment name: group}).
step_checker : Optional[Callable[[object, str, str], bool]]
    Function that draws the figure so far and asks whether it is accepted; None
    accepts without drawing.

---- Globals read ----
None.

---- Outputs ----
str
    Name of the experiment chosen.

---- Globals mutated ----
None. Stores the (group, hours) pair in the list of ``slot`` (side effect).

---- Equations ----
None.

---- Helpers ----
_example_pair_maker
_step_checker
choice_asker
```

#### `_saved_example_finder`

```text
---- Summary ----
Helper function to find the experiments that match the (group, hours) pairs
remembered from the last run.

---- Inputs ----
defaults : dict
    Saved answers of the last run.
key : str
    Answer holding the pairs, e.g. 'tr_examples'.
members : dict
    {experiment name: group}.
timed : list
    Names of the experiments that have hours in their name.

---- Globals read ----
None.

---- Outputs ----
list
    Names of the experiments that match a saved pair, in the order of the pairs.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `_step_checker`

```text
---- Summary ----
Helper function to show the figure as built so far and ask whether it is accepted.

---- Inputs ----
step_checker : Optional[Callable[[object, str, str], bool]]
    Function (members, question, what no does) that draws the figure and returns
    True when it is accepted; None when there is nothing to draw with.
members : object
    The experiments of the figure: {name: group} or a list of names.
question : str
    The accept question.
change : str
    What answering no does, for example 'choose the OCR again'.

---- Globals read ----
None.

---- Outputs ----
bool
    True when accepted (or when there is no way to draw).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_step_wirer`

```text
---- Summary ----
Helper function to turn the figure checker of the whole figure into the checker of
one step: the figure drawn from the choices made so far.

---- Inputs ----
figure_checker : Optional[Callable[[str, dict], bool]]
    The figure checker (see summary_figure_asker), or None.
key : str
    'time_response' or 'haem_ocr'.
fit : Optional[dict]
    Fit dictionary.
result : dict
    {'time_response': ..., 'haem_ocr': ...} of the figures so far.

---- Globals read ----
None.

---- Outputs ----
Optional[Callable[[object, str, str], bool]]
    Function (members, question, change label) giving True when the user accepts
    the figure so far, or None when there is no figure checker.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_time_response_asker`

```text
---- Summary ----
Helper function to ask the settings of the time response figure (6.1.x).

---- Inputs ----
names : List[str]
    Experiment names (file names without the extension).
answers : dict
    Answers dictionary the settings are stored in.
defaults : dict
    Default answers.
step_checker : Optional[Callable[[object, str, str], bool]]
    Function (members, question, change label) that draws the figure as built so
    far, asks whether it is accepted and returns True when it is; None skips the
    previews.

---- Globals read ----
None.

---- Outputs ----
Optional[dict]
    {experiment name: group} of the experiments that belong to the figure, or
    None when the figure cannot be made from these files.

---- Globals mutated ----
None. Stores the settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_hours_reader
_panel_chooser
_saved_example_finder
_step_checker
group_assigner
hours_parser
info_printer
size_asker
text_asker
```

### MAIN FUNCTIONS

#### `summary_figure_asker`

```text
---- Summary ----
Main function to ask section 7: whether to plot a time response and a haem and
OCR response, and the settings of each one chosen. Both need the haem fit, which
is asked for here if it was not chosen in the processing, and the averaging
windows of the processing: with none set up, the window step is offered and the
figure is not made without them; with both kinds set up, each figure asks which
it uses.

---- Inputs ----
names : List[str]
    Experiment names (file names without the extension).
answers : dict
    Answers dictionary the settings are stored in.
defaults : dict
    Default answers.
summaries : List[dict]
    File summaries (DATA_FORMAT.md), used if the fit has to be asked for.
fit : Optional[dict]
    Fit dictionary chosen in section 3, or None.
fits_folder : Path
    Folder holding the fit .csv files.
figure_checker : Optional[Callable[[str, dict], bool]]
    Function called after the questions of each figure with (key, {'fit': fit,
    'custom': result so far}); it shows the figure and returns True when the user
    accepts it. When it returns False the figure's questions are asked again.
percent_names : Optional[List[str]]
    Names of the files with an oxidised and a reduced region, whose haems have a
    % oxidised; None when no file has them.
windows_adder : Optional[Callable[[], bool]]
    Function that runs the window step of the processing (windows_ensurer); None
    when it cannot be run.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fit, result). result is {'time_response': {name: group} or None,
    'haem_ocr': [names] or None}; None means that figure will not be made.

---- Globals mutated ----
None. Stores the settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_haem_ocr_asker
_step_wirer
_time_response_asker
decomposition_asker
info_printer
window_kind_asker
windows_ensurer
yes_no_asker
```

## `utils_custom/custom_runner.py`

Preparation of single experiments and drawing of the custom figures.

### CUSTOM RUNNER HELPERS

#### `_ocr_and_haem_response_preparer`

```text
---- Summary ----
Helper function to calculate the event-window averages used by the haem and OCR
response figures, on a copy of one experiment.

---- Inputs ----
experiment : dict
    Processed experiment (DATA_FORMAT.md).
answers : dict
    Terminal answers; uses the ho_* settings (ho_window_kind is the kind of window
    the figure uses) and the averaging windows of the dataset (window_minutes,
    gap_minutes, final_gap_minutes, quick_minutes, delay_minutes).
od_available : bool
    True when OD, volume and dilution factor were available for this experiment.

---- Globals read ----
None.

---- Outputs ----
Optional[dict]
    Shallow copy with 'averages' added, or None when the experiment lacks the OD
    values the chosen sources need (it would not be comparable with the others).

---- Globals mutated ----
None. Shows a warning when the experiment is left out (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_averages_calculator
source_selector
warning_shower
window_kind_picker
```

#### `_time_response_preparer`

```text
---- Summary ----
Helper function to average the spectra in the event windows, subtract the last two
windows and decompose the difference spectrum, on a copy of one experiment.

---- Inputs ----
experiment : dict
    Processed experiment with attenuation spectra (DATA_FORMAT.md).
group : str
    Group the experiment belongs to.
answers : dict
    Terminal answers; uses decomposition_dataset, haem_background, the kind of
    window the figure uses (tr_window_kind) and the averaging windows of the
    dataset (window_minutes, gap_minutes, final_gap_minutes, quick_minutes,
    delay_minutes).
fit : dict
    Fit dictionary from import_fit.

---- Globals read ----
config.HAEM_FACTOR.

---- Outputs ----
dict
    Shallow copy of the experiment with group, spectral_averages,
    difference_spectrum and difference_decomposition added.

---- Globals mutated ----
None.

---- Equations ----
None. See spectral_difference.py.

---- Helpers ----
difference_spectrum_calculator
difference_spectrum_decomposer
spectral_averager
```

### MAIN FUNCTIONS

#### `exemplar_runner`

```text
---- Summary ----
Main function to draw the 2x2 figure: one experiment for each strain and addition
order, plotted like the individual experiment figures.

---- Inputs ----
chosen : dict
    {experiment name: kept result of process_experiment} with the keys
    experiment, vo2_source and haem_source (DATA_FORMAT.md).
cfg : Config
    Figure style of this figure (its own journal).
answers : dict
    Terminal answers; uses haems, plot_haems, the ho_ex_* and ho_exemplar_run
    settings and the kind of window the figure shows (ex_window_kind).
fit : Optional[dict]
    Fit dictionary, or None when the haems were not decomposed.
export_root : Path
    Results folder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; the figure files are written.

---- Globals mutated ----
None. Writes the figure files (side effect).

---- Equations ----
None.

---- Helpers ----
custom_figure_saver
exemplar_config_builder
exemplar_figure_plotter
individual_config_builder
window_kind_picker
```

#### `experiment_preparer`

```text
---- Summary ----
Main function to prepare one processed experiment for the special figures. Each
figure is prepared on its own, so a problem with one does not stop the other.

---- Inputs ----
experiment : dict
    Processed experiment with its spectra still attached (DATA_FORMAT.md).
custom : dict
    {'time_response_group': group or None, 'haem_ocr': bool} for this experiment.
answers : dict
    Terminal answers.
fit : Optional[dict]
    Fit dictionary from import_fit.
od_available : bool
    True when OD, volume and dilution factor were available.

---- Globals read ----
None.

---- Outputs ----
dict
    {'time_response': prepared experiment or None, 'haem_ocr': prepared
    experiment or None}.

---- Globals mutated ----
None. Shows a warning for a figure this experiment is left out of; the details of
a problem go to the log (side effects).

---- Equations ----
None.

---- Helpers ----
_ocr_and_haem_response_preparer
_time_response_preparer
problem_shower
```

#### `ocr_and_haem_response_runner`

```text
---- Summary ----
Main function to combine the runs of each condition, draw the OCR and haem response
figure and write the workbook behind it. A problem with the figure does not stop
the workbook, and neither stops the 2x2 figure, which is drawn separately.

---- Inputs ----
experiments : dict
    Prepared experiments keyed by name, each with averages (DATA_FORMAT.md).
cfg : Config
    Figure style derived from the answers.
answers : dict
    Terminal answers.
fit : dict
    Fit dictionary from import_fit.
export_root : Path
    Results folder.
is_preview : bool
    True to draw the figure only (for the experiment browser): the workbook is not
    written.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; files are written.

---- Globals mutated ----
None. Writes ocr_and_haem_response.xlsx and the figure files to ``export_root``;
shows a warning for what is not made, with the details of a problem in the log
(side effects).

---- Equations ----
None.

---- Helpers ----
custom_figure_saver
ocr_and_haem_response_config_builder
ocr_and_haem_response_exporter
ocr_and_haem_response_figure_plotter
problem_shower
triplicate_averager
warning_shower
```

#### `time_response_runner`

```text
---- Summary ----
Main function to draw the time response figure from the prepared experiments and
write the workbook behind it.

---- Inputs ----
experiments : dict
    Prepared experiments keyed by name, each with group and
    difference_decomposition (DATA_FORMAT.md).
cfg : Config
    Figure style derived from the answers.
answers : dict
    Terminal answers.
fit : dict
    Fit dictionary from import_fit.
export_root : Path
    Results folder.
is_preview : bool
    True to draw the figure only (for the experiment browser): the workbook is not
    written.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; files are written.

---- Globals mutated ----
None. Writes time_response.xlsx and the figure files to ``export_root`` (side
effect).

---- Equations ----
None.

---- Helpers ----
custom_figure_saver
individual_config_builder
time_response_config_builder
time_response_exporter
time_response_figure_plotter
```

## `utils_custom/exemplar_plotter.py`

Figure of four exemplar experiments in a 2x2 grid.

### EXEMPLAR HELPERS

#### `_crop_start_finder`

```text
---- Summary ----
Helper function to find the time at which an exemplar crop begins.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
mode : str
    'baseline' (start of the average0 window) or 'first_addition'.
before_minutes : float
    Minutes kept before the first addition.
margin_minutes : float
    Extra minutes kept before the baseline window.

---- Globals read ----
None.

---- Outputs ----
float
    Crop start time in minutes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_exemplar_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap between rows and between columns of the
exemplar quadrants.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.
n_rows : int
    Number of group rows.
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (hspace, wspace) as GridSpec fractions.

---- Globals mutated ----
None.

---- Equations ----
row_gap = 1.2 tick + 0.5 unit + label pad + 1.2 label + 1.0 unit; column_gap = lines
x 1.2 label + y label pad + 5 x 0.55 tick + 0.5 unit + 1.5 unit (points) for one
column, 1.5 unit when there are several (the later columns have no y labels).

---- Helpers ----
gap_space_calculator
```

#### `_exemplar_plotter`

```text
---- Summary ----
Helper function to draw one experiment exactly as the individual plotter does.

---- Inputs ----
fig : Figure
    Matplotlib figure.
subplot_spec : SubplotSpec
    Grid cell the experiment is drawn in.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Axes of the stacked panels.

---- Globals mutated ----
None. Adds axes to ``fig`` (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_drawer
```

#### `_exemplar_selector`

```text
---- Summary ----
Helper function to pick the experiment of one run number for every (strain, order)
cell.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
run : int
    Run number shown for each condition.

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): experiment}. Raises ValueError if two experiments match one
    cell.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
experiment_classifier
```

#### `_experiment_cropper`

```text
---- Summary ----
Helper function to copy an experiment cropped to begin at a chosen time, with time
measured from there.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
start : float
    Time in minutes at which the crop begins.

---- Globals read ----
None.

---- Outputs ----
tuple
    (cropped experiment copy, last time in minutes).

---- Globals mutated ----
None.

---- Equations ----
t_new = t - start; rows with t_new < 0 are dropped.

---- Helpers ----
time_getter
```

### MAIN FUNCTIONS

#### `exemplar_figure_plotter`

```text
---- Summary ----
Main function to build the exemplar figure: one run per condition, each drawn by the
individual plotter in its own quadrant.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Exemplar figure settings from custom_config.exemplar_config_builder.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes maps (strain, order) to its list of axes and 'letters' to
    {letter: experiment name}.

---- Globals mutated ----
None. Shows a warning for an empty quadrant or columns whose additions differ (side
effect).

---- Equations ----
None.

---- Helpers ----
_crop_start_finder
_exemplar_gap_calculator
_exemplar_plotter
_exemplar_selector
_experiment_cropper
experiment_title_builder
figure_finisher
stack_legend_drawer
warning_shower
watermark_style_builder
```

## `utils_custom/ocr_and_haem_response_exporter.py`

Export of the OCR and haem response to a workbook that can be checked by hand.

### HELPERS

#### `_baseline_sheet_writer`

```text
---- Summary ----
Helper function to write the baseline OCR of every run with the mean, SD and SEM
of each group.

---- Inputs ----
workbook : Any
    xlsxwriter workbook.
baseline : dict
    Baseline summary from the response plotter: 'strains' and 'runs' ({group:
    {experiment name: baseline OCR}}).
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
Mean = AVERAGE of the runs; SD = STDEV (n - 1); SEM = SD / sqrt(N).

---- Helpers ----
_statistics_writer
number_writer
```

#### `_condition_sheet_writer`

```text
---- Summary ----
Helper function to write the sheet of one condition: the run-by-run window means
with their mean, SD and SEM for the OCR and each haem.

---- Inputs ----
workbook : Any
    xlsxwriter workbook.
name : str
    Sheet name.
condition : str
    Condition name, e.g. 'knockdown_kcn_then_bd'.
result : dict
    Across-run statistics of the condition from triplicate_averager.
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
None.

---- Helpers ----
_measurement_table_writer
```

#### `_measurement_table_writer`

```text
---- Summary ----
Helper function to write the tables of one measurement (OCR or one haem): window
means, % of baseline and change from baseline side by side, one row per window.

---- Inputs ----
sheet : Any
    xlsxwriter worksheet.
top_row : int
    Row index (0-based) of the first row written.
label : str
    Measurement name.
windows : list
    Window names, in order; the first is the baseline window.
stats_by_window : dict
    {window: statistics} of this measurement, from triplicate_averager.
runs : list
    Run numbers, in column order.
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
BASELINE_WINDOW : str
    Name of the baseline window, the reference of the change tables.
FAMILIES : tuple
    (key, title, statistics key) of the three tables.

---- Outputs ----
int
    Index of the first free row below the tables.

---- Globals mutated ----
None. Writes to the worksheet (side effect).

---- Equations ----
% of baseline = window mean / baseline mean x 100; change from baseline = window
mean - baseline mean; both per run, as formulas on the window mean table.

---- Helpers ----
_statistics_writer
finite_float_converter
formula_writer
number_writer
```

#### `_statistics_writer`

```text
---- Summary ----
Helper function to write N, mean, SD and SEM formulas to the right of the run cells
of one row.

---- Inputs ----
sheet : Any
    xlsxwriter worksheet.
row : int
    Row index (0-based).
first_col : int
    Column of the first run cell; the statistics follow the last run cell.
n_runs : int
    Number of run columns.
values : list
    The run values of the row (NaN where a run has none), for the cached results.
formats : dict
    Cell formats from workbook_formats_builder.
cell_format : Any
    Format of the mean, SD and SEM cells.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes to the worksheet (side effect).

---- Equations ----
N = count of the finite values; mean = sum / N; SD = sqrt(sum((x - mean)^2) /
(N - 1)); SEM = SD / sqrt(N). Mean, SD and SEM are empty when N is too small.

---- Helpers ----
finite_float_converter
formula_writer
```

#### `_test_row_writer`

```text
---- Summary ----
Helper function to write one t-test comparison: the run values, the statistics,
the t-test and the multiple comparison correction, as formulas.

---- Inputs ----
sheet : Any
    xlsxwriter worksheet.
row : int
    Row index (0-based) of this comparison.
record : dict
    One t-test record from the response plotter (DATA_FORMAT.md).
columns : dict
    Column indices by name, from _tests_sheet_writer.
panel_first_row : int
    Row index of the first comparison of this panel.
rank : int
    Rank of the comparison in its panel by raw p value, from 1.
panel_size : int
    Number of comparisons in the panel.
running : float
    Running maximum of multiplier x p up to this rank, for the cached result.
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes to the worksheet (side effect).

---- Equations ----
pooled = ((nA - 1) SDA^2 + (nB - 1) SDB^2) / (nA + nB - 2); t = (meanA - meanB) /
sqrt(pooled (1/nA + 1/nB)); df = nA + nB - 2; p = TDIST(|t|, df, 2). Holm: adjusted
p = min(1, max over ranks <= r of (m - rank + 1) p); Bonferroni: min(1, m p).

---- Helpers ----
formula_writer
number_writer
```

#### `_tests_sheet_writer`

```text
---- Summary ----
Helper function to write the t-tests of the figure, one row per comparison, with
everything needed to repeat them.

---- Inputs ----
workbook : Any
    xlsxwriter workbook.
tests : list
    t-test records from the response plotter (DATA_FORMAT.md).
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
See _test_row_writer.

---- Helpers ----
_test_row_writer
```

### MAIN FUNCTIONS

#### `ocr_and_haem_response_exporter`

```text
---- Summary ----
Main function to write the workbook behind the OCR and haem response figure: the
run-by-run values with their mean, SD and SEM, the baseline OCR and the t-tests,
all as formulas so a reader can check the maths.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
tests : list
    t-test records of the figure (``fig.response_tests``); may be empty.
baseline : Optional[dict]
    Baseline summary of the figure (``fig.response_baseline``), or None.
output_path : Path
    Workbook (.xlsx) to write.

---- Globals read ----
NOTE_LINES : tuple
    Text of the Notes sheet.

---- Outputs ----
Path
    The workbook path.

---- Globals mutated ----
None. Writes the workbook (side effect).

---- Equations ----
None. See the Notes sheet of the workbook.

---- Helpers ----
_baseline_sheet_writer
_condition_sheet_writer
_tests_sheet_writer
excel_sheet_namer
workbook_formats_builder
```

## `utils_custom/ocr_and_haem_response_plotter.py`

Figure of the baseline OCR, the OCR response and the haem response.

### OCR AND HAEM RESPONSE HELPERS

#### `_axes_styler`

```text
---- Summary ----
Helper function to apply the tick, grid and spine style of the response and baseline
panels.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.
tick_size : float
    Tick label size in points.
pad : Optional[float]
    Tick label pad in points, or None for the default.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_baseline_bar_plotter`

```text
---- Summary ----
Helper function to draw the baseline OCR (average0) bar chart per group, with every
run overlaid and a Student t-test bracket between the two groups.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.
tests : list
    List collecting one dictionary per t-test comparison.

---- Globals read ----
None.

---- Outputs ----
dict
    Baseline summary for the workbook: 'strains', 'vo2_source' and 'runs' ({group:
    {experiment name: baseline OCR}}).

---- Globals mutated ----
None. Draws on ``ax`` and appends the baseline t-test to ``tests`` (side effects).

---- Equations ----
Bar height = mean of the run baselines; error bar = SEM = SD / sqrt(n). Student
t-test with equal variances between the two groups.

---- Helpers ----
_axes_styler
_column_chooser
_significance_bar_drawer
_significance_formatter
experiment_classifier
finite_float_converter
warning_shower
```

#### `_block_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap below each block of the OCR and haem response
figure (each gap is sized for what it holds) and the gap between the response
columns.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
blocks : list
    Block names from top to bottom ('baseline', 'ocr_response', 'haem_response').
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (gaps in points, one per block but the last; wspace as a GridSpec fraction).

---- Globals mutated ----
None.

---- Equations ----
A gap above the first response block = x tick labels + 0.5 unit + title and legend
row + 1.0 unit. The gap between the OCR and haem responses = two-line tick labels +
0.5 unit + the significance bars' headroom + 0.5 unit. column_gap = 5 x 0.55 tick +
0.5 unit + 1.5 unit (points).

---- Helpers ----
gap_space_calculator
```

#### `_column_chooser`

```text
---- Summary ----
Helper function to choose the OCR column: the preferred one if set, else VoO2, else
the first available.

---- Inputs ----
available : Iterable
    Column names that are available.
preferred : Optional[str]
    Column requested in the settings, or None.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Chosen column name, or None if none is available.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_condition_indexer`

```text
---- Summary ----
Helper function to map each (strain, order) pair to its condition name in the
triplicate results.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): condition name}. Raises ValueError if two conditions match one
    pair.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
```

#### `_finite_run_filter`

```text
---- Summary ----
Helper function to keep the runs that have a finite value.

---- Inputs ----
runs : dict
    {run number or experiment name: value}; values may be NaN.

---- Globals read ----
None.

---- Outputs ----
dict
    The same mapping without the runs whose value is NaN or infinite; values are
    floats.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_block_plotter`

```text
---- Summary ----
Helper function to draw the haem response: one row per haem, one column per addition
order, a line per group.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
rows : list
    Haem row dictionaries {haem, label}.
haem_source : str
    Haem source key, for example 'delta_abs_od'.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.
bars_above : bool
    True draws the top row's significance bars in the white space above the block
    (between it and the block above) instead of inside the axes.

---- Globals read ----
None.

---- Outputs ----
tuple
    (grid of axes [row][column], invisible axes carrying the shared y label).

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_haem_label_finder
_haem_label_pad_calculator
_mean_ylim_setter
_measurement_finder
_outside_bar_drawer
_reference_level_finder
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
warning_shower
```

#### `_haem_label_finder`

```text
---- Summary ----
Helper function to find the shared y label of the haem response rows.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
str
    Label text from HAEM_RESPONSE_AXIS_LABELS for the metric and source.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_label_pad_calculator`

```text
---- Summary ----
Helper function to calculate the points between the shared haem label and the haem
axes.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
float
    Label pad in points.

---- Globals mutated ----
None.

---- Equations ----
pad = 1.2 label font + 0.5 unit + 5 x 0.55 tick font + 0.5 unit (points).

---- Helpers ----
None.
```

#### `_haem_row_selector`

```text
---- Summary ----
Helper function to select the haem response rows to draw, in the order listed in
HAEM_RESPONSE_SHOW.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Row dictionaries {haem, label}. Every row is returned when HAEM_RESPONSE_SHOW is
    empty. Entries are matched to a row label or haem name ignoring case and
    punctuation.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `_haem_source_finder`

```text
---- Summary ----
Helper function to find the haem source that every condition's averages were
calculated from.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
str
    Haem source key, for example 'delta_abs_od'. Raises ValueError if the conditions
    differ.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_layout_validator`

```text
---- Summary ----
Helper function to check that the layout options of the OCR and haem response
figure are recognised and to return the group and order lists.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
ORDER_TITLES, BLOCK_NAMES, RESPONSE_METRICS (module constants).

---- Outputs ----
tuple
    (orders, strains): addition orders (columns) and groups (rows), as tuples.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_legend_handle_builder`

```text
---- Summary ----
Helper function to build legend entries showing each group's colour, line style and
marker.

---- Inputs ----
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Line2D handles, one per group.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_mean_ylim_setter`

```text
---- Summary ----
Helper function to set the y range of a response panel from the group means (and
the baseline level) only, so that a single outlier run or a very large error bar
does not stretch the axis. Points and error bars beyond the range are clipped.

---- Inputs ----
ax : Axes
    Response panel, with the series already drawn.
series_list : list
    One list of window statistics per strain, as drawn by _response_series_drawer.
metric : str
    Response metric, which decides the field holding the mean.
baseline_level : Optional[float]
    Reference level that must stay in view (for example 100 for % of baseline).
margin : float
    Fraction of the mean range added above and below.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Sets the y limits of ``ax`` (side effect); does nothing when no mean is
finite.

---- Equations ----
low = min(means) - margin x range; high = max(means) + margin x range, where the
range is max(means) - min(means) (at least 1 % of the largest absolute mean). When
all means are on one side of the baseline, the baseline side gets a 3 % margin.

---- Helpers ----
_metric_field_selector
```

#### `_measurement_finder`

```text
---- Summary ----
Helper function to find the column matching a wanted name, ignoring case and
punctuation.

---- Inputs ----
available : Iterable
    Column names that are available.
wanted : str
    Name to look for.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Matching column name, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `_metric_field_selector`

```text
---- Summary ----
Helper function to name the keys of the triplicate statistics used by a response
metric.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (mean key, sem key, n key, per-run values key).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ocr_block_plotter`

```text
---- Summary ----
Helper function to draw the OCR response (percent of each run's baseline, mean and
SEM across runs), one axes per addition order.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.

---- Globals read ----
None.

---- Outputs ----
list
    The axes, one per addition order.

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_column_chooser
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
warning_shower
```

#### `_offset_transformer`

```text
---- Summary ----
Helper function to build a transform that shifts data coordinates upward by a
number of points.

---- Inputs ----
ax : Axes
    Matplotlib axes whose data coordinates are shifted.
points : float
    Upward shift in points.

---- Globals read ----
None.

---- Outputs ----
Any
    Matplotlib transform.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_outside_bar_drawer`

```text
---- Summary ----
Helper function to draw the significance bars stored by _response_window_tester in
the white space just above an axes, so the plot keeps its full height.

---- Inputs ----
ax : Axes
    Response panel whose y range is final.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_test_bar_drawer
```

#### `_p_value_adjuster`

```text
---- Summary ----
Helper function to adjust a list of p values for multiple comparisons.

---- Inputs ----
p_values : Iterable
    Raw p values.
method : str
    'none', 'bonferroni' or 'holm'.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Adjusted p values, same order as the input.

---- Globals mutated ----
None.

---- Equations ----
Bonferroni: p_adj = min(n p, 1). Holm: sort ascending, p_adj(i) = min(max over j <=
i of (n - j) p(j), 1) with j counted from 0.

---- Helpers ----
None.
```

#### `_panel_labeller`

```text
---- Summary ----
Helper function to give the next letter to a panel.

---- Inputs ----
state : dict
    Lettering state with keys 'letters' (iterator of letters), 'names' ({letter:
    panel name}) and 'panels' (list of (letter, main axes, member axes)).
main_ax : Axes
    Main axes of the panel.
members : list
    All axes that belong to the panel.
name : str
    Panel name used in the printed panel list.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Advances ``state['letters']`` and appends to ``state['names']`` and
``state['panels']`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_reference_level_finder`

```text
---- Summary ----
Helper function to find the height of the dashed reference line of the haem
response.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    0 for a change, 100 for percent of baseline, 0 for a delta abs value, otherwise
    None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_reference_selector`

```text
---- Summary ----
Helper function to pick, for each addition order, the first run of the first
available group (used for the event tick labels).

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.

---- Globals read ----
None.

---- Outputs ----
dict
    {order: experiment or None}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_response_axes_preparer`

```text
---- Summary ----
Helper function to draw the baseline reference line and set the window ticks of a
response panel.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
window_names : list
    Averaging window names, for example ['average0', 'average1'].
tick_labels : list
    Tick label of every window.
show_xlabels : bool
    True to write the tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
baseline_level : Optional[float]
    Height of the reference line, or None for no line.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    x positions of the windows.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_axes_styler
```

#### `_response_metric_checker`

```text
---- Summary ----
Helper function to reject a percent-of-baseline response for the delta abs sources,
which start at 0.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
DELTA_HAEM_SOURCES (schema constant).

---- Outputs ----
None
    Nothing. Raises ValueError for the combination that is not allowed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_response_series_drawer`

```text
---- Summary ----
Helper function to plot every run as a point, the mean as a line and SEM error bars
for one group.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : Iterable
    x positions of the windows.
stats_list : list
    Statistics dictionary (or None) for each window.
style : dict
    Group style: colour, linestyle, marker.
config : dict
    Figure settings dictionary built in custom_config.py.
label : Optional[str]
    Unused legend text.
metric : str
    Response metric: 'delta', 'change' or 'value'.
offset : float
    Horizontal shift in x units so groups sit side by side.

---- Globals read ----
None.

---- Outputs ----
bool
    True if anything was drawn.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_metric_field_selector
```

#### `_response_window_tester`

```text
---- Summary ----
Helper function to run a Student t-test between the two groups at every window of a
response panel and mark the significant windows.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : np.ndarray
    x positions of the windows.
windows : list
    Window names.
series_by_strain : dict
    {strain: [statistics per window]}.
strains : tuple
    Group names (rows or bars), in drawing order.
metric : str
    Response metric: 'delta', 'change' or 'value'.
config : dict
    Figure settings dictionary built in custom_config.py.
panel_name : str
    Panel name written to the test table.
tests : list
    List collecting one dictionary per t-test comparison.
outside : bool
    True keeps the axis range as it is and stores the marks on ``ax`` for
    _outside_bar_drawer, which draws them in the space above the axes.
measurement : str
    Name of the measurement tested (OCR or haem column), written to the test table.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Appends one dictionary per comparison to ``tests`` (the keys are listed in
DATA_FORMAT.md) and draws on ``ax`` (side effects); with ``outside`` it sets
``ax.outside_marks`` instead of drawing.

---- Equations ----
Equal-variance Student t-test per window; p values adjusted across the windows of
the panel (RESPONSE_TEST_CORRECTION); significant if p_adj < RESPONSE_TEST_ALPHA.

---- Helpers ----
_finite_run_filter
_metric_field_selector
_p_value_adjuster
_test_bar_drawer
```

#### `_row_ylim_sharer`

```text
---- Summary ----
Helper function to give every axes in a row the union of their y ranges.

---- Inputs ----
axes_row : list
    Axes of one row.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the y limits of the axes (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_significance_bar_drawer`

```text
---- Summary ----
Helper function to draw a bracket between two x positions with text centred above
it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end of the bracket (data units).
x_right : float
    Right end of the bracket (data units).
y : float
    Height of the bracket (data units).
text : str
    Text written above the bracket.
tick_size : float
    Tick label size in points.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_significance_formatter`

```text
---- Summary ----
Helper function to format a p value as stars or as text.

---- Inputs ----
p_value : float
    p value.
style : str
    'stars' or 'p'.

---- Globals read ----
None.

---- Outputs ----
str
    '***', '**', '*' or 'ns' (stars style) or the p value text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_test_bar_drawer`

```text
---- Summary ----
Helper function to draw a small bracket joining the two groups' points at one window
with text above it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end (data units).
x_right : float
    Right end (data units).
y : float
    Data height the clearances are measured from.
text : str
    Stars written above the bracket.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_offset_transformer
```

#### `_tick_label_builder`

```text
---- Summary ----
Helper function to build the x tick labels of the averaging windows: Baseline, then
the addition that precedes each window.

---- Inputs ----
experiment : Optional[dict]
    Reference experiment whose events label the windows, or None.
window_names : list
    Averaging window names, for example ['average0', 'average1'].

---- Globals read ----
None.

---- Outputs ----
list
    One label per window; additions are written as label and concentration.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
concentration_formatter
finite_float_converter
```

#### `_window_orderer`

```text
---- Summary ----
Helper function to list the averaging windows present in any condition of one
addition order.

---- Inputs ----
order : str
    Addition order name.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.

---- Globals read ----
None.

---- Outputs ----
list
    Window names in numerical order.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `ocr_and_haem_response_figure_plotter`

```text
---- Summary ----
Main function to build the OCR and haem response figure: baseline OCR, OCR response
and haem response blocks.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics from triplicate_averager.
config : dict
    Figure settings from custom_config.ocr_and_haem_response_config_builder.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes holds 'baseline', 'ocr_response', 'haem_response' and
    'letters' ({letter: panel name}).

---- Globals mutated ----
None. Stores the t-test records on the returned figure as ``fig.response_tests`` and
the baseline summary as ``fig.response_baseline`` (None without a baseline block).

---- Equations ----
None.

---- Helpers ----
_baseline_bar_plotter
_block_gap_calculator
_condition_indexer
_haem_block_plotter
_haem_row_selector
_haem_source_finder
_layout_validator
_legend_handle_builder
_ocr_block_plotter
_panel_labeller
_reference_selector
_response_metric_checker
experiment_classifier
figure_finisher
warning_shower
```

## `utils_custom/publication_plotter.py`

Publication figure (baseline OCR, OCR response, haem response), exemplars.

### PUBLICATION PLOTTER HELPERS

#### `_axes_styler`

```text
---- Summary ----
Helper function to apply the tick, grid and spine style of the response and baseline
panels.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.
tick_size : float
    Tick label size in points.
pad : Optional[float]
    Tick label pad in points, or None for the default.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_baseline_bar_plotter`

```text
---- Summary ----
Helper function to draw the baseline OCR (average0) bar chart per group, with every
run overlaid and a Student t-test bracket between the two groups.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
Bar height = mean of the run baselines; error bar = SEM = SD / sqrt(n). Student
t-test with equal variances between the two groups.

---- Helpers ----
_axes_styler
_column_chooser
_experiment_classifier
_significance_bar_drawer
_significance_formatter
finite_float_converter
```

#### `_block_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap below each block of the publication figure
(each gap is sized for what it holds) and the gap between the response columns.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
blocks : list
    Block names from top to bottom ('baseline', 'ocr_response', 'haem_response').
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (gaps in points, one per block but the last; wspace as a GridSpec fraction).

---- Globals mutated ----
None.

---- Equations ----
A gap above the first response block = x tick labels + 0.5 unit + title and legend
row + 1.0 unit. The gap between the OCR and haem responses = two-line tick labels +
0.5 unit + the significance bars' headroom + 0.5 unit. column_gap = 5 x 0.55 tick +
0.5 unit + 1.5 unit (points).

---- Helpers ----
gap_space_calculator
```

#### `_column_chooser`

```text
---- Summary ----
Helper function to choose the OCR column: the preferred one if set, else VoO2, else
the first available.

---- Inputs ----
available : Iterable
    Column names that are available.
preferred : Optional[str]
    Column requested in the settings, or None.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Chosen column name, or None if none is available.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_condition_indexer`

```text
---- Summary ----
Helper function to map each (strain, order) pair to its condition name in the
triplicate results.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): condition name}. Raises ValueError if two conditions match one
    pair.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
```

#### `_crop_start_finder`

```text
---- Summary ----
Helper function to find the time at which an exemplar crop begins.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
mode : str
    'baseline' (start of the average0 window) or 'first_addition'.
before_minutes : float
    Minutes kept before the first addition.
margin_minutes : float
    Extra minutes kept before the baseline window.

---- Globals read ----
None.

---- Outputs ----
float
    Crop start time in minutes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_exemplar_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap between rows and between columns of the
exemplar quadrants.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.
n_rows : int
    Number of group rows.
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (hspace, wspace) as GridSpec fractions.

---- Globals mutated ----
None.

---- Equations ----
row_gap = 1.2 tick + 0.5 unit + label pad + 1.2 label + 1.0 unit; column_gap = lines
x 1.2 label + y label pad + 5 x 0.55 tick + 0.5 unit + 1.5 unit (points) for one
column, 1.5 unit when there are several (the later columns have no y labels).

---- Helpers ----
gap_space_calculator
```

#### `_exemplar_plotter`

```text
---- Summary ----
Helper function to draw one experiment exactly as the individual plotter does.

---- Inputs ----
fig : Figure
    Matplotlib figure.
subplot_spec : SubplotSpec
    Grid cell the experiment is drawn in.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Axes of the stacked panels.

---- Globals mutated ----
None. Adds axes to ``fig`` (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_drawer
```

#### `_exemplar_selector`

```text
---- Summary ----
Helper function to pick the experiment of one run number for every (strain, order)
cell.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
run : int
    Run number shown for each condition.

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): experiment}. Raises ValueError if two experiments match one
    cell.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_experiment_classifier
```

#### `_experiment_classifier`

```text
---- Summary ----
Helper function to identify the strain, addition order and run number from an
experiment name.

---- Inputs ----
name : str
    Experiment name such as 'control_kcn_then_bd_run1'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (strain, order, run); entries are None where they cannot be identified.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
run_name_parser
```

#### `_experiment_cropper`

```text
---- Summary ----
Helper function to copy an experiment cropped to begin at a chosen time, with time
measured from there.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
start : float
    Time in minutes at which the crop begins.

---- Globals read ----
None.

---- Outputs ----
tuple
    (cropped experiment copy, last time in minutes).

---- Globals mutated ----
None.

---- Equations ----
t_new = t - start; rows with t_new < 0 are dropped.

---- Helpers ----
time_getter
```

#### `_figure_finisher`

```text
---- Summary ----
Helper function to fit the margins to the drawn content, add the panel letters at
the top-left of each panel and fit again.

---- Inputs ----
fig : Figure
    Matplotlib figure.
config : dict
    Figure settings dictionary built in custom_config.py.
panels : list
    List of (letter, main axes, [axes of the panel]) tuples.
suptitle : Any
    Figure title text object, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Resizes the layout of ``fig`` and adds text to it (side effect).

---- Equations ----
None.

---- Helpers ----
figure_canvas_fitter
panel_letter_adder
```

#### `_haem_block_plotter`

```text
---- Summary ----
Helper function to draw the haem response: one row per haem, one column per addition
order, a line per group.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
rows : list
    Haem row dictionaries {haem, label}.
haem_source : str
    Haem source key, for example 'delta_abs_od'.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.
bars_above : bool
    True draws the top row's significance bars in the white space above the block
    (between it and the block above) instead of inside the axes.

---- Globals read ----
None.

---- Outputs ----
tuple
    (grid of axes [row][column], invisible axes carrying the shared y label).

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_haem_label_finder
_haem_label_pad_calculator
_mean_ylim_setter
_measurement_finder
_outside_bar_drawer
_reference_level_finder
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
```

#### `_haem_label_finder`

```text
---- Summary ----
Helper function to find the shared y label of the haem response rows.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
str
    Label text from HAEM_RESPONSE_AXIS_LABELS for the metric and source.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_label_pad_calculator`

```text
---- Summary ----
Helper function to calculate the points between the shared haem label and the haem
axes.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
float
    Label pad in points.

---- Globals mutated ----
None.

---- Equations ----
pad = 1.2 label font + 0.5 unit + 5 x 0.55 tick font + 0.5 unit (points).

---- Helpers ----
None.
```

#### `_haem_row_selector`

```text
---- Summary ----
Helper function to select the haem response rows to draw, in the order listed in
HAEM_RESPONSE_SHOW.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Row dictionaries {haem, label}. Every row is returned when HAEM_RESPONSE_SHOW is
    empty. Entries are matched to a row label or haem name ignoring case and
    punctuation.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `_haem_source_finder`

```text
---- Summary ----
Helper function to find the haem source that every condition's averages were
calculated from.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
str
    Haem source key, for example 'delta_abs_od'. Raises ValueError if the conditions
    differ.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_layout_validator`

```text
---- Summary ----
Helper function to check that the layout options of the publication figure are
recognised and to return the group and order lists.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
ORDER_TITLES, BLOCK_NAMES, RESPONSE_METRICS (module constants).

---- Outputs ----
tuple
    (orders, strains): addition orders (columns) and groups (rows), as tuples.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_legend_handle_builder`

```text
---- Summary ----
Helper function to build legend entries showing each group's colour, line style and
marker.

---- Inputs ----
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Line2D handles, one per group.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_mean_ylim_setter`

```text
---- Summary ----
Helper function to set the y range of a response panel from the group means (and
the baseline level) only, so that a single outlier run or a very large error bar
does not stretch the axis. Points and error bars beyond the range are clipped.

---- Inputs ----
ax : Axes
    Response panel, with the series already drawn.
series_list : list
    One list of window statistics per strain, as drawn by _response_series_drawer.
metric : str
    Response metric, which decides the field holding the mean.
baseline_level : Optional[float]
    Reference level that must stay in view (for example 100 for % of baseline).
margin : float
    Fraction of the mean range added above and below.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Sets the y limits of ``ax`` (side effect); does nothing when no mean is
finite.

---- Equations ----
low = min(means) - margin x range; high = max(means) + margin x range, where the
range is max(means) - min(means) (at least 1 % of the largest absolute mean). When
all means are on one side of the baseline, the baseline side gets a 3 % margin.

---- Helpers ----
_metric_field_selector
```

#### `_measurement_finder`

```text
---- Summary ----
Helper function to find the column matching a wanted name, ignoring case and
punctuation.

---- Inputs ----
available : Iterable
    Column names that are available.
wanted : str
    Name to look for.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Matching column name, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `_metric_field_selector`

```text
---- Summary ----
Helper function to name the keys of the triplicate statistics used by a response
metric.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (mean key, sem key, n key, per-run values key).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ocr_block_plotter`

```text
---- Summary ----
Helper function to draw the OCR response (percent of each run's baseline, mean and
SEM across runs), one axes per addition order.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.

---- Globals read ----
None.

---- Outputs ----
list
    The axes, one per addition order.

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_column_chooser
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
```

#### `_outside_bar_drawer`

```text
---- Summary ----
Helper function to draw the significance bars stored by _response_window_tester in
the white space just above an axes, so the plot keeps its full height.

---- Inputs ----
ax : Axes
    Response panel whose y range is final.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_test_bar_drawer
```

#### `_p_value_adjuster`

```text
---- Summary ----
Helper function to adjust a list of p values for multiple comparisons.

---- Inputs ----
p_values : Iterable
    Raw p values.
method : str
    'none', 'bonferroni' or 'holm'.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Adjusted p values, same order as the input.

---- Globals mutated ----
None.

---- Equations ----
Bonferroni: p_adj = min(n p, 1). Holm: sort ascending, p_adj(i) = min(max over j <=
i of (n - j) p(j), 1) with j counted from 0.

---- Helpers ----
None.
```

#### `_reference_level_finder`

```text
---- Summary ----
Helper function to find the height of the dashed reference line of the haem
response.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    0 for a change, 100 for percent of baseline, 0 for a delta abs value, otherwise
    None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_reference_selector`

```text
---- Summary ----
Helper function to pick, for each addition order, the first run of the first
available group (used for the event tick labels).

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.

---- Globals read ----
None.

---- Outputs ----
dict
    {order: experiment or None}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_response_axes_preparer`

```text
---- Summary ----
Helper function to draw the baseline reference line and set the window ticks of a
response panel.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
window_names : list
    Averaging window names, for example ['average0', 'average1'].
tick_labels : list
    Tick label of every window.
show_xlabels : bool
    True to write the tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
baseline_level : Optional[float]
    Height of the reference line, or None for no line.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    x positions of the windows.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_axes_styler
```

#### `_response_metric_checker`

```text
---- Summary ----
Helper function to reject a percent-of-baseline response for the delta abs sources,
which start at 0.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
DELTA_HAEM_SOURCES (schema constant).

---- Outputs ----
None
    Nothing. Raises ValueError for the combination that is not allowed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_response_series_drawer`

```text
---- Summary ----
Helper function to plot every run as a point, the mean as a line and SEM error bars
for one group.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : Iterable
    x positions of the windows.
stats_list : list
    Statistics dictionary (or None) for each window.
style : dict
    Group style: colour, linestyle, marker.
config : dict
    Figure settings dictionary built in custom_config.py.
label : Optional[str]
    Unused legend text.
metric : str
    Response metric: 'delta', 'change' or 'value'.
offset : float
    Horizontal shift in x units so groups sit side by side.

---- Globals read ----
None.

---- Outputs ----
bool
    True if anything was drawn.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_metric_field_selector
```

#### `_response_window_tester`

```text
---- Summary ----
Helper function to run a Student t-test between the two groups at every window of a
response panel and mark the significant windows.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : np.ndarray
    x positions of the windows.
windows : list
    Window names.
series_by_strain : dict
    {strain: [statistics per window]}.
strains : tuple
    Group names (rows or bars), in drawing order.
metric : str
    Response metric: 'delta', 'change' or 'value'.
config : dict
    Figure settings dictionary built in custom_config.py.
panel_name : str
    Panel name written to the test table.
tests : list
    List collecting one dictionary per t-test comparison.
outside : bool
    True keeps the axis range as it is and stores the marks on ``ax`` for
    _outside_bar_drawer, which draws them in the space above the axes.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Appends one dictionary per comparison to ``tests`` and draws on ``ax`` (side
effects); with ``outside`` it sets ``ax.outside_marks`` instead of drawing.

---- Equations ----
Equal-variance Student t-test per window; p values adjusted across the windows of
the panel (RESPONSE_TEST_CORRECTION); significant if p_adj < RESPONSE_TEST_ALPHA.

---- Helpers ----
_metric_field_selector
_p_value_adjuster
_test_bar_drawer
```

#### `_row_ylim_sharer`

```text
---- Summary ----
Helper function to give every axes in a row the union of their y ranges.

---- Inputs ----
axes_row : list
    Axes of one row.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the y limits of the axes (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_significance_bar_drawer`

```text
---- Summary ----
Helper function to draw a bracket between two x positions with text centred above
it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end of the bracket (data units).
x_right : float
    Right end of the bracket (data units).
y : float
    Height of the bracket (data units).
text : str
    Text written above the bracket.
tick_size : float
    Tick label size in points.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_significance_formatter`

```text
---- Summary ----
Helper function to format a p value as stars or as text.

---- Inputs ----
p_value : float
    p value.
style : str
    'stars' or 'p'.

---- Globals read ----
None.

---- Outputs ----
str
    '***', '**', '*' or 'ns' (stars style) or the p value text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_test_bar_drawer`

```text
---- Summary ----
Helper function to draw a small bracket joining the two groups' points at one window
with text above it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end (data units).
x_right : float
    Right end (data units).
y : float
    Data height the clearances are measured from.
text : str
    Stars written above the bracket.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_offset_transformer
```

#### `_tick_label_builder`

```text
---- Summary ----
Helper function to build the x tick labels of the averaging windows: Baseline, then
the addition that precedes each window.

---- Inputs ----
experiment : Optional[dict]
    Reference experiment whose events label the windows, or None.
window_names : list
    Averaging window names, for example ['average0', 'average1'].

---- Globals read ----
None.

---- Outputs ----
list
    One label per window; additions are written as label and concentration.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
concentration_formatter
finite_float_converter
```

#### `_window_orderer`

```text
---- Summary ----
Helper function to list the averaging windows present in any condition of one
addition order.

---- Inputs ----
order : str
    Addition order name.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.

---- Globals read ----
None.

---- Outputs ----
list
    Window names in numerical order.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `exemplar_figure_plotter`

```text
---- Summary ----
Main function to build the exemplar figure: one run per condition, each drawn by the
individual plotter in its own quadrant.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Exemplar figure settings from custom_config.exemplar_config_builder.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes maps (strain, order) to its list of axes and 'letters' to
    {letter: experiment name}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_crop_start_finder
_exemplar_gap_calculator
_exemplar_plotter
_exemplar_selector
_experiment_cropper
_figure_finisher
experiment_title_builder
stack_legend_drawer
watermark_style_builder
```

#### `publication_figure_plotter`

```text
---- Summary ----
Main function to build the publication figure: baseline OCR, OCR response and haem
response blocks.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics from triplicate_averager.
config : dict
    Publication figure settings from custom_config.publication_config_builder.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes holds 'baseline', 'ocr_response', 'haem_response' and
    'letters' ({letter: panel name}).

---- Globals mutated ----
None. Stores the t-test table on the returned figure as ``fig.response_tests``.

---- Equations ----
None.

---- Helpers ----
_baseline_bar_plotter
_block_gap_calculator
_condition_indexer
_experiment_classifier
_figure_finisher
_haem_block_plotter
_haem_row_selector
_haem_source_finder
_layout_validator
_legend_handle_builder
_ocr_block_plotter
_panel_labeller
_reference_selector
_response_metric_checker
```

#### `publication_figure_saver`

```text
---- Summary ----
Main function to save a publication or exemplar figure at its exact size, plus the
t-test table when there is one.

---- Inputs ----
fig : Figure
    Figure returned by publication_figure_plotter or exemplar_figure_plotter.
export_root : Path
    Results folder.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Paths of the files written.

---- Globals mutated ----
None. Writes the figure under <export_root>/<OUTPUT_SUBFOLDER> and the test table
under <export_root>/<DATA_SUBFOLDER> (side effects).

---- Equations ----
None.

---- Helpers ----
figure_saver
```

## `utils_custom/run_namer.py`

Experiment (run) name parsing: conditions, run numbers, groups and hours.

### RUN NAMER HELPERS

#### `_group_matcher`

```text
---- Summary ----
Helper function to find the first group word that appears in an experiment name.

---- Inputs ----
name : str
    Experiment name.
groups : Sequence[str]
    Group names in priority order.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Matching group, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_natural_sorter`

```text
---- Summary ----
Helper function to build a sort key that orders numbers inside names numerically.

---- Inputs ----
name : str
    Name to sort.

---- Globals read ----
None.

---- Outputs ----
list
    Alternating text and integer parts.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_order_sorter`

```text
---- Summary ----
Helper function to build the sort key of one (group, name, experiment) item.

---- Inputs ----
item : tuple
    (group, name, experiment).
groups : Sequence[str]
    Group names in the wanted order.

---- Globals read ----
None.

---- Outputs ----
tuple
    (group index, no-hours flag, hours, natural name key).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_natural_sorter
hours_parser
```

### MAIN FUNCTIONS

#### `condition_classifier`

```text
---- Summary ----
Main function to identify the strain and the addition order from a condition name.

---- Inputs ----
condition : str
    Condition name such as 'knockdown_kcn_then_bd'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (strain, order). strain is 'knockdown' (the word knockdown or a kd token),
    'control' or None; order is 'bd_then_kcn' or 'kcn_then_bd' from the position of
    the bd and kcn tokens, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `condition_grouper`

```text
---- Summary ----
Main function to group experiments by condition and run number.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.

---- Globals read ----
None.

---- Outputs ----
dict
    {condition: {run number: experiment}}. Experiments without a run suffix are
    skipped with a warning; a duplicate run number raises ValueError.

---- Globals mutated ----
None. Shows a warning for each experiment skipped (side effect).

---- Equations ----
None.

---- Helpers ----
run_name_parser
warning_shower
```

#### `experiment_classifier`

```text
---- Summary ----
Helper function to identify the strain, addition order and run number from an
experiment name.

---- Inputs ----
name : str
    Experiment name such as 'control_kcn_then_bd_run1'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (strain, order, run); entries are None where they cannot be identified.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
run_name_parser
```

#### `group_assigner`

```text
---- Summary ----
Main function to give every experiment a group from its name and to order the
experiments by group and then by hours.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name (DATA_FORMAT.md).
groups : Sequence[str]
    Group names in the order they should appear, for example
    ('control', 'knockdown'). An experiment belongs to the first group whose name
    is a word (or the start) of its name.

---- Globals read ----
None.

---- Outputs ----
dict
    Same experiments, ordered, each with a 'group' key added. Experiments that
    match no group are left out with a warning.

---- Globals mutated ----
None. Adds the 'group' key to the experiment dictionaries and shows a warning for
each experiment left out (side effects).

---- Equations ----
None.

---- Helpers ----
_group_matcher
_order_sorter
warning_shower
```

#### `hours_parser`

```text
---- Summary ----
Main function to read the number of hours from an experiment name.

---- Inputs ----
name : str
    Experiment name such as 'control_7hours'.

---- Globals read ----
HOURS_PATTERN (module constant).

---- Outputs ----
Optional[float]
    Hours, or None if the name has none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `run_name_lister`

```text
---- Summary ----
Main function to describe how each experiment name is read by the haem and OCR
response figures, for showing to the user before they choose.

---- Inputs ----
names : Sequence[str]
    Experiment names (the .paf file names without the extension).

---- Globals read ----
None.

---- Outputs ----
list
    One dictionary per name: {name, condition, run, strain, order}; entries are
    None where the name does not identify them.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
run_name_parser
```

#### `run_name_parser`

```text
---- Summary ----
Main function to split an experiment name of the form <condition>_run<N> into its
condition and run number.

---- Inputs ----
name : str
    Experiment name, for example 'knockdown_kcn_then_bd_run1'.

---- Globals read ----
RUN_NAME_PATTERN (module constant).

---- Outputs ----
Optional[tuple]
    (condition, run number), or None if the name has no run suffix.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_custom/spectral_difference.py`

Event-window spectral averages, their difference spectrum and its decomposition.

### MAIN FUNCTIONS

#### `difference_spectrum_calculator`

```text
---- Summary ----
Main function to subtract one averaged spectrum from another.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
minuend : str
    Window name or role ('penultimate', 'final') to subtract from.
subtrahend : str
    Window name or role to subtract.

---- Globals read ----
None.

---- Outputs ----
dict
    The experiment, with difference_spectrum added (DATA_FORMAT.md).

---- Globals mutated ----
None. Adds ``difference_spectrum`` to the experiment (side effect).

---- Equations ----
difference = mean spectrum of the minuend window - mean spectrum of the subtrahend
window.

---- Helpers ----
None.
```

#### `difference_spectrum_decomposer`

```text
---- Summary ----
Main function to decompose the difference spectrum into haem contributions using the
shared decomposition.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
fit : dict
    Fit dictionary from import_fit: {haem_list, data}.
background : str
    Background fitted under the haems (BACKGROUND_LABELS in spectral_decomposer).
haemfactor : float
    Scale factor applied to the fit spectra.
percent_basis : str
    'signed' (coefficient / sum of coefficients) or 'absolute' (coefficient / sum of
    absolute coefficients).

---- Globals read ----
None.

---- Outputs ----
dict
    The experiment, with difference_decomposition added (DATA_FORMAT.md).

---- Globals mutated ----
None. Adds ``difference_decomposition`` to the experiment (side effect).

---- Equations ----
percent_i = 100 c_i / sum(c) ('signed') or 100 c_i / sum(|c|) ('absolute'); NaN when
the denominator is about 0.

---- Helpers ----
spectrum_decomposer
```

#### `spectral_averager`

```text
---- Summary ----
Main function to average the chosen spectra in each event window: the baseline,
then the settled or the quick window of each addition.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
dataset_name : str
    Spectrometer dataset, for example 'Cyt'.
spectrum_type : str
    Spectrum field, for example 'attenuation'.
window_minutes : float
    Length of each window in minutes.
gap_minutes : float
    Gap between a window and the next addition in minutes.
final_window_gap_minutes : float
    Gap between the last window and the end of the data in minutes.
expected_events : Optional[int]
    Raise if the run has a different number of events; None skips the check.
kind : str
    The kind of window averaged over after each addition: 'settled' (ending
    before the next addition) or 'quick' (starting after its own).
quick_minutes : float
    Length of each quick window in minutes; used for the quick kind.
delay_minutes : float
    How long after its addition each quick window starts, in minutes; used for
    the quick kind.

---- Globals read ----
None.

---- Outputs ----
dict
    The experiment, with spectral_averages added (DATA_FORMAT.md).

---- Globals mutated ----
None. Adds ``spectral_averages`` to the experiment and shows a warning for each
window skipped (side effects).

---- Equations ----
None. The windows fall as kind_span_lister says; a window is left out when it
does not fit or holds no spectrum.

---- Helpers ----
kind_span_lister
warning_shower
```

## `utils_custom/time_response_exporter.py`

Export of the time response to a workbook that can be checked by hand.

### HELPERS

#### `_difference_sheet_writer`

```text
---- Summary ----
Helper function to write the two window means and their difference for every
experiment.

---- Inputs ----
workbook : object
    xlsxwriter workbook.
groups : dict
    {group: [(time label, experiment), ...]} from group_collector.
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
dict
    {experiment name: (first column, first data row, number of rows)} so other
    sheets can refer to the difference column.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
difference = mean spectrum of the minuend window - mean spectrum of the subtrahend
window.

---- Helpers ----
formula_writer
number_writer
```

#### `_haem_sheet_writer`

```text
---- Summary ----
Helper function to write the haem coefficients of every experiment and the
percentages calculated from them.

---- Inputs ----
workbook : object
    xlsxwriter workbook.
groups : dict
    {group: [(time label, experiment), ...]} from group_collector.
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
percentage = 100 c / sum(c) (signed) or 100 c / sum(|c|) (absolute), with c the
fitted haem coefficient.

---- Helpers ----
formula_writer
number_writer
```

#### `_picks_sheet_writer`

```text
---- Summary ----
Helper function to list which experiments the panels of the figure show and which
time points were left out of the waterfalls.

---- Inputs ----
workbook : object
    xlsxwriter workbook.
picks : dict
    Picks of the figure ('kinetic', 'decomposition' as lists of (group, time label,
    experiment name) and 'skipped_hours').
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_waterfall_sheet_writer`

```text
---- Summary ----
Helper function to write the shared-baseline correction of the waterfalls.

---- Inputs ----
workbook : object
    xlsxwriter workbook.
groups : dict
    {group: [(time label, experiment), ...]} of the time points in the waterfalls.
locations : dict
    Difference spectra locations from _difference_sheet_writer.
config : dict
    Time response settings (WATERFALL_BASELINE_* and TIME_LABEL_FORMAT).
formats : dict
    Cell formats from workbook_formats_builder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a worksheet to the workbook (side effect).

---- Equations ----
baseline(w) = intercept + slope w, fitted to the mean difference spectrum between
WATERFALL_BASELINE_X_MIN and WATERFALL_BASELINE_X_MAX; corrected = difference -
baseline. Degrees above 1 are written as calculated values.

---- Helpers ----
formula_writer
number_writer
shared_baseline_subtracter
```

### MAIN FUNCTIONS

#### `time_response_exporter`

```text
---- Summary ----
Main function to write the workbook behind the time response figure: the window
means and difference spectra, the haem coefficients and percentages, and the
waterfall baseline correction, as formulas so a reader can check the maths.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Time response settings from custom_config.time_response_config_builder.
picks : dict
    Experiments shown in the panels (``fig.time_response_picks``).
output_path : Path
    Workbook (.xlsx) to write.

---- Globals read ----
NOTE_LINES : tuple
    Text of the Notes sheet.

---- Outputs ----
Path
    The workbook path.

---- Globals mutated ----
None. Writes the workbook (side effect).

---- Equations ----
None. See the Notes sheet of the workbook.

---- Helpers ----
_difference_sheet_writer
_haem_sheet_writer
_picks_sheet_writer
_waterfall_sheet_writer
group_collector
hours_parser
workbook_formats_builder
```

## `utils_custom/time_response_plotter.py`

Time response figure: waterfalls, example time courses and decompositions.

### TIME RESPONSE PLOTTER HELPERS

#### `_event_label_height_calculator`

```text
---- Summary ----
Helper function to calculate the height the rotated event labels above the example
time courses need.

---- Inputs ----
experiments : list
    Example experiments.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
float
    Height in points; 0 when the labels are not drawn on top.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
concentration_formatter
text_extent_calculator
```

#### `_example_finder`

```text
---- Summary ----
Helper function to find the experiment of one group at a given number of hours.

---- Inputs ----
groups : dict
    {group: [(time label, experiment), ...]}.
group : str
    Group name.
hours : float
    Hours in the experiment name.

---- Globals read ----
None.

---- Outputs ----
tuple
    (time label, experiment). Raises ValueError if there is none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `_example_viewer`

```text
---- Summary ----
Helper function to copy an experiment so that its individual figure shows only the
two windows its difference spectrum came from.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.

---- Globals read ----
None.

---- Outputs ----
dict
    Copy with averages holding the penultimate and final spectral windows.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_scale_sharer`

```text
---- Summary ----
Helper function to give each haem the same y range in every stack, so that all the
a haems share one scale, all the cc haems another, and so on.

---- Inputs ----
stacks : list
    Axes lists of the kinetic traces (each from experiment_drawer).
config : dict
    Figure settings; uses HAEM_Y_MAX_TICKS to thin the tick labels again.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the y limits and ticks of the haem axes (side effect).

---- Equations ----
Limits are the union of the stacks' limits for the same haem.

---- Helpers ----
None.
```

#### `_haem_window_drawer`

```text
---- Summary ----
Helper function to shade, behind the spectra, a window around the peak of every
haem in the haem's own colour, to show where each haem should appear.

---- Inputs ----
ax : Axes
    Matplotlib axes with wavelength on the x axis.
decomposition : dict
    difference_decomposition of an experiment (DATA_FORMAT.md).
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
config keys HAEM_COLOURS, HAEM_WINDOW_HALF_WIDTH_NM and HAEM_WINDOW_ALPHA.

---- Outputs ----
None

---- Globals mutated ----
None. Draws on ``ax`` and leaves its x limits as they were (side effect).

---- Equations ----
window = peak +- HAEM_WINDOW_HALF_WIDTH_NM, where the peak is the wavelength of the
largest absolute value of the haem's fitted component.

---- Helpers ----
name_simplifier
```

#### `_legend_drawer`

```text
---- Summary ----
Helper function to draw a legend in the journal style: small text and an optional
thin box.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.
location : str
    Matplotlib legend location.
columns : Optional[int]
    Number of legend columns, or None for the setting.
outside : bool
    True puts the legend in the white space to the right of the axes.
anchor : Optional[tuple]
    Axes-coordinate anchor of the legend's ``location`` point, which overrides
    ``outside``.

---- Globals read ----
None.

---- Outputs ----
Any
    The legend.

---- Globals mutated ----
None. Adds a legend to ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_placeholder_drawer`

```text
---- Summary ----
Helper function to draw an empty labelled box where a panel has not been chosen yet.

---- Inputs ----
fig : Any
    The figure, already fitted to its final layout.
hidden : dict
    {panel letter: [axes that were hidden]} of the panels not chosen yet.
config : dict
    Time response settings from custom_config.time_response_config_builder.

---- Globals read ----
PLACEHOLDER_NAMES (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Hides the axes and adds a dashed box and its text to the figure (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_time_axes_styler`

```text
---- Summary ----
Helper function to apply the tick direction, label size and spine style.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_time_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gaps of the time response figure: the white space
under the first and under the second row, and the gap between columns.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.
label_height_pt : float
    Height of the event labels in points.
legend_rows : int
    Number of text rows of the legends that hang under the second row.

---- Globals read ----
None.

---- Outputs ----
tuple
    (gap under row 1, gap under row 2, column gap), all in points.

---- Globals mutated ----
None.

---- Equations ----
x_block = 1.2 tick + 0.5 unit + label pad + 1.2 label; gap 1 = x_block + max(event
label height, 1.2 title + 0.8 unit) + 1.0 unit; gap 2 = x_block + legend rows x 1.35
legend font + 1.2 unit + 1.2 title + 0.8 unit + 1.0 unit; column_gap = 1.2 label +
0.5 unit + 5 x 0.55 tick + 0.5 unit + 1.5 unit.

---- Helpers ----
None.
```

#### `_title_styler`

```text
---- Summary ----
Helper function to set a panel title in the figure style.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
text : str
    Title text.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the title of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `decomposition_plotter`

```text
---- Summary ----
Main function to draw a difference spectrum with its scatter-free fit, residual and
each haem contribution.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
decomposition : dict
    difference_decomposition of an experiment (DATA_FORMAT.md).
config : dict
    Figure settings dictionary built in custom_config.py.
show_legend : bool
    True draws the legend inside the axes; False leaves it to the caller.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_haem_window_drawer
_legend_drawer
_time_axes_styler
name_simplifier
```

#### `group_collector`

```text
---- Summary ----
Main function to collect the decomposed experiments of each group, with their time
labels.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
dict
    {group: [(time label, experiment), ...]}. Experiments without a difference
    decomposition are left out with a warning; ValueError if a group is empty.

---- Globals mutated ----
None. Shows a warning for each experiment left out (side effect).

---- Equations ----
None.

---- Helpers ----
time_label_builder
warning_shower
```

#### `shared_baseline_subtracter`

```text
---- Summary ----
Main function to subtract one shared polynomial baseline, fitted to the mean
spectrum, from every spectrum.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths, shape (n_wavelengths, n_spectra), nm.
spectra : np.ndarray
    Spectra, shape (n_wavelengths, n_spectra).
x_min : Optional[float]
    Lower wavelength of the fit range, or None.
x_max : Optional[float]
    Upper wavelength of the fit range, or None.
degree : int
    Polynomial degree, at least 1.

---- Globals read ----
None.

---- Outputs ----
tuple
    (corrected spectra, shared baseline), both shaped like ``spectra``.

---- Globals mutated ----
None.

---- Equations ----
baseline(w) = polynomial fitted to mean over spectra of S(w) within [x_min, x_max];
corrected = S - baseline.

---- Helpers ----
None.
```

#### `time_label_builder`

```text
---- Summary ----
Main function to build the label of a time point from the experiment name.

---- Inputs ----
experiment_name : str
    Experiment name such as 'control_7hours'.
label_format : str
    Format string with an {hours} field.

---- Globals read ----
None.

---- Outputs ----
str
    For example '7 hours'; the experiment name when it contains no hours.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `time_response_figure_plotter`

```text
---- Summary ----
Main function to build the time response figure as a 3 x 3 grid. Plots 1 and 4 are
the waterfalls of the two groups, plots 2-3 and 5-6 are two kinetic traces (each
spanning two columns) and plots 7, 8 and 9 are three decomposition plots.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Time response settings from custom_config.time_response_config_builder.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes maps the panel letters 'A'-'G' (reading order) to axes; the
    kinetic traces give their list of axes.

---- Globals mutated ----
None. Sets ``fig.time_response_picks`` (the examples shown, used by the exporter)
(side effect).

---- Equations ----
The legend of the waterfalls hangs under plot 4 and the legend of the kinetic traces
under plots 5-6, both in the gap above the decomposition row; the three
decomposition plots share the width left of one legend at the far right.

---- Helpers ----
_event_label_height_calculator
_example_finder
_example_viewer
_haem_scale_sharer
_placeholder_drawer
_time_gap_calculator
_title_styler
decomposition_plotter
experiment_drawer
figure_canvas_fitter
gap_space_calculator
group_collector
hours_parser
panel_letter_adder
stack_legend_drawer
waterfall_plotter
```

#### `waterfall_plotter`

```text
---- Summary ----
Main function to draw the offset difference spectra of one group, first time point
at the top, with additive peak alignment.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
items : list
    [(time label, experiment), ...] of one group.
config : dict
    Figure settings dictionary built in custom_config.py.
show_legend : bool
    True to draw the legend.
marked : Optional[dict]
    {time label: text} written in black just past the right end of that trace; the
    text is the letter of the kinetic trace panel drawn from that time point.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
aligned = S + (1 - max of S within [ALIGN_MIN, ALIGN_MAX]); shifted_i = aligned_i -
min(aligned_i) + (n - 1 - i) x offset; offset defaults to 0.75 x the largest span.

---- Helpers ----
_haem_window_drawer
_legend_drawer
_time_axes_styler
shared_baseline_subtracter
```

## `utils_custom/triplicate_averager.py`

Across-run (triplicate) statistics of the event-window averages.

### TRIPLICATE AVERAGER HELPERS

#### `_run_summariser`

```text
---- Summary ----
Helper function to summarise the finite values of one window across runs.

---- Inputs ----
values : Iterable
    Values to summarise (one per run).

---- Globals read ----
None.

---- Outputs ----
tuple
    (mean, sample SD, SEM, N). SD and SEM are NaN for N < 2; all NaN with N = 0 when
    no value is finite.

---- Globals mutated ----
None.

---- Equations ----
SD = sqrt(sum((x - mean)^2) / (N - 1)); SEM = SD / sqrt(N).

---- Helpers ----
None.
```

#### `_run_value_getter`

```text
---- Summary ----
Helper function to read one statistic of one window and measurement for every run.

---- Inputs ----
windows_by_run : dict
    {run number: {window name: window record}} from the runs' averages.
window_name : str
    Window name such as 'average3'.
kind : str
    'vo2' or 'haem'.
measurement : str
    Measurement (column) name.
field : str
    Statistic name: 'mean', 'sd', 'change' or 'delta'.

---- Globals read ----
None.

---- Outputs ----
dict
    {run number: value}, NaN where a run lacks the window.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_window_sorter`

```text
---- Summary ----
Helper function to sort averaging window names numerically.

---- Inputs ----
window_name : str
    Window name such as 'average3'.

---- Globals read ----
None.

---- Outputs ----
int
    Window number.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `triplicate_averager`

```text
---- Summary ----
Main function to combine the per-experiment event averages across the runs of each
condition.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
min_runs : int
    Conditions with fewer runs that have averages are skipped.

---- Globals read ----
None.

---- Outputs ----
dict
    {condition: result}; result holds runs, run_numbers, windows, window_times,
    settings and, for vo2 and haem, per-window statistics (DATA_FORMAT.md).

---- Globals mutated ----
None. Shows a warning for each condition skipped (side effect).

---- Equations ----
None.

---- Helpers ----
_run_summariser
_run_value_getter
_window_sorter
condition_grouper
warning_shower
```

## `utils_custom/triplicate_exporter.py`

Export of the across-run (triplicate) statistics to an Excel workbook.

### MAIN FUNCTIONS

#### `triplicate_exporter`

```text
---- Summary ----
Main function to write one worksheet per condition of the across-run statistics to
an Excel workbook.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
output_path : Path
    Workbook (.xlsx) to write.

---- Globals read ----
None.

---- Outputs ----
Path
    The workbook path.

---- Globals mutated ----
None. Writes the workbook (side effect).

---- Equations ----
None.

---- Helpers ----
_number_writer
excel_sheet_namer
finite_float_converter
```

## `utils_custom/workbook_helpers.py`

Cell formats and cell writers shared by the workbook exporters.

### MAIN FUNCTIONS

#### `formula_writer`

```text
---- Summary ----
Main function to write a formula with the value that the program calculated, so
that the cell shows the right number even before Excel recalculates it.

---- Inputs ----
sheet : Any
    xlsxwriter worksheet.
row : int
    Row index (0-based).
col : int
    Column index (0-based).
formula : str
    Excel formula starting with '='.
value : Any
    Calculated result; NaN is stored as an empty string.
cell_format : Any
    xlsxwriter cell format.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes to the worksheet (side effect).

---- Equations ----
None.

---- Helpers ----
finite_float_converter
```

#### `number_writer`

```text
---- Summary ----
Main function to write a number, or leave the cell empty when it is not finite.

---- Inputs ----
sheet : Any
    xlsxwriter worksheet.
row : int
    Row index (0-based).
col : int
    Column index (0-based).
value : Any
    Value to write.
cell_format : Any
    xlsxwriter cell format.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes to the worksheet (side effect).

---- Equations ----
None.

---- Helpers ----
finite_float_converter
```

#### `workbook_formats_builder`

```text
---- Summary ----
Main function to define the cell formats of the workbook.

---- Inputs ----
workbook : Any
    xlsxwriter workbook.

---- Globals read ----
GROUP_COLOUR, HEADER_COLOUR : str
    Fill colours of the header cells.

---- Outputs ----
dict
    {name: xlsxwriter format} with the keys title, group, header, text, number,
    percent, p_value and integer.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/app_messages.py`

The Mac app's own messages: why it could not start, with the Mac report to copy, and

### MESSAGE HELPERS

#### `_applescript_quoter`

```text
---- Summary ----
Helper function to write a text as an AppleScript string, so quotes and backslashes
in it (a folder name, for example) cannot end the string early.

---- Inputs ----
text : str
    Any text.

---- Globals read ----
None.

---- Outputs ----
str
    The text between double quotes, with backslashes and double quotes escaped.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_dialog_script_maker`

```text
---- Summary ----
Helper function to write the AppleScript of a macOS message with buttons, the last
button being the one Enter presses.

---- Inputs ----
text : str
    The message.
title : str
    Title of the message window.
buttons : Sequence[str]
    Button names, left to right.
icon : str
    'caution' for a problem, 'note' for news.

---- Globals read ----
None.

---- Outputs ----
str
    One AppleScript statement; osascript prints "button returned:<name>".

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_applescript_quoter
```

#### `_report_copier`

```text
---- Summary ----
Helper function to run the Mac report that comes inside the app and copy what it
prints to the clipboard.

---- Inputs ----
places : UserPlaces
    Where the program's own files are (the report is in its launchers folder).

---- Globals read ----
REPORT_SCRIPT, REPORT_TIMEOUT_S (module constants).

---- Outputs ----
bool
    True when the report was copied; False when it could not be run or copied.

---- Globals mutated ----
None. Runs the report and fills the clipboard (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `start_problem_shower`

```text
---- Summary ----
Main function to say why Portimao could not start. The sentence is always printed
(to the terminal, or to the app's launch log). In the Mac app, which has no
terminal, a macOS message also shows it, with a Copy details button that copies the
Mac report and opens the Mac problem form to paste it into.

---- Inputs ----
sentence : str
    One sentence that says what went wrong and what to do.
places : UserPlaces
    Where the program's files are, and whether this is the app.

---- Globals read ----
COPY_BUTTON, FORM_LINK (module constants).

---- Outputs ----
None
    Nothing. Waits until the message is closed. A message that cannot be shown
    leaves only the printed sentence.

---- Globals mutated ----
None. Prints, shows a message, may fill the clipboard and open the form in the
browser (side effects).

---- Equations ----
None.

---- Helpers ----
_dialog_script_maker
_report_copier
```

#### `update_notice_shower`

```text
---- Summary ----
Main function to say, in a macOS message that does not hold up the start, that a
newer Portimao is out but this copy could not update itself, with a button that
opens the download page.

---- Inputs ----
version : str
    The newer version, for example "2.5".
reason : str
    Why this copy could not update itself, in plain words.

---- Globals read ----
DOWNLOAD_BUTTON, RELEASES_LINK (module constants).

---- Outputs ----
None
    Nothing. Returns at once; the message stays until it is closed.

---- Globals mutated ----
None. Shows a message, and opens the page in the browser when asked (side
effects).

---- Equations ----
None.

---- Helpers ----
_applescript_quoter
_dialog_script_maker
```

## `utils_shared/app_updater.py`

The Mac app's own update at each start: asks GitHub for the newest release and, when it

### UPDATE HELPERS

#### `_app_finder`

```text
---- Summary ----
Helper function to find the .app folder the running program is in.

---- Inputs ----
executable : str
    Path of the running program, <app>.app/Contents/MacOS/<name> in the app.

---- Globals read ----
None.

---- Outputs ----
Optional[Path]
    The .app folder, or None when the program is not inside one.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_app_unpacker`

```text
---- Summary ----
Helper function to unpack the downloaded zip with macOS's ditto, which keeps the
app's links and signature (Python's zip module would break them).

---- Inputs ----
zip_path : Path
    The downloaded zip.
folder : Path
    Folder to unpack into.

---- Globals read ----
None.

---- Outputs ----
Optional[Path]
    The one .app folder unpacked, or None when unpacking failed.

---- Globals mutated ----
None. Writes the app into the folder (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ask_problem_describer`

```text
---- Summary ----
Helper function to say in plain words why a question to GitHub got no answer, and
whether GitHub refused it.

---- Inputs ----
curl_code : int
    curl's exit code; 0 when it had an answer of any kind.
http_status : int
    GitHub's status code (200 when it answered); 0 when there was none, as for a
    file:// address.
body : str
    GitHub's answer; a refusal says why in it.
errors : str
    What curl printed as its error.

---- Globals read ----
CURL_REASONS, REFUSED_STATUSES (module constants).

---- Outputs ----
Tuple[str, bool]
    (the reason, empty when there is an answer to read; True when GitHub refused).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_blocker_finder`

```text
---- Summary ----
Helper function to find what stops the app from replacing itself where it is.

---- Inputs ----
app : Path
    The .app folder.

---- Globals read ----
TEMPORARY_COPY_MARK (module constant).

---- Outputs ----
Optional[str]
    Why it cannot replace itself, in plain words, or None when it can.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_leftover_cleaner`

```text
---- Summary ----
Helper function to delete what an earlier update left beside the app: the update
folder, with a download that did not finish or the old app.

---- Inputs ----
app : Path
    The .app folder.

---- Globals read ----
UPDATE_FOLDER_NAME (module constant).

---- Outputs ----
None
    Nothing. Whatever cannot be deleted is left for the next start.

---- Globals mutated ----
None. Deletes files (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_log_opener`

```text
---- Summary ----
Helper function to open the update log: keeps its last lines and gives a function
that adds a line with the date and time.

---- Inputs ----
logs_folder : Path
    The user's logs folder; made when missing.

---- Globals read ----
LOG_KEPT_LINES, LOG_NAME (module constants).

---- Outputs ----
Tuple[Path, Callable[[str], None]]
    (the log's path, the function that adds a line). A log that cannot be written
    just loses its lines; the update goes on.

---- Globals mutated ----
None. Writes the log (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_new_app_checker`

```text
---- Summary ----
Helper function to check that the unpacked app is the version offered and has its
program inside.

---- Inputs ----
new_app : Path
    The unpacked .app folder.
version : str
    The version offered, for example "2.5".

---- Globals read ----
None.

---- Outputs ----
bool
    True when the app's Info.plist gives that version and its program is there.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_version_splitter
```

#### `_new_app_fetcher`

```text
---- Summary ----
Helper function to download the zip of the new app, unpack it and check it.

---- Inputs ----
url : str
    Where the zip is.
size_bytes : int
    Size of the zip as GitHub gives it; 0 when not known.
version : str
    The version offered.
folder : Path
    The update folder beside the app; made here.
show : Callable[[str], None]
    Shows a line of progress.
log : Callable[[str], None]
    Adds a line to the update log.

---- Globals read ----
None.

---- Outputs ----
Optional[Path]
    The new .app folder, ready to be moved in, or None when any step failed (the
    reason is in the log).

---- Globals mutated ----
None. Writes into the update folder (side effect).

---- Equations ----
None.

---- Helpers ----
_app_unpacker
_new_app_checker
_zip_downloader
```

#### `_newer_checker`

```text
---- Summary ----
Helper function to say whether the version offered is newer than the app's own.

---- Inputs ----
own : Optional[str]
    The app's version, for example "2.9"; None when it could not be read.
offered : str
    The version offered, with or without its V, for example "V2.10".

---- Globals read ----
None.

---- Outputs ----
bool
    True only when both versions can be read and the one offered is newer.

---- Globals mutated ----
None.

---- Equations ----
Versions are compared number by number from the left: 2.10 > 2.9, 2.3.1 > 2.3,
2.3.0 = 2.3.

---- Helpers ----
_version_splitter
```

#### `_newest_release_finder`

```text
---- Summary ----
Helper function to find GitHub's newest release. With no answer it asks once more
after a few seconds; when GitHub refuses, it asks the Releases page instead, which
GitHub does not count in the same way. Each try and its reason go to the log.

---- Inputs ----
release_url : str
    The address of GitHub's answer (a file:// address in the tests).
log : Callable[[str], None]
    Adds a line to the update log.

---- Globals read ----
RELEASE_DOWNLOAD_URL, RELEASES_LINK, RETRY_WAIT_S (module constants).

---- Outputs ----
Optional[Tuple[str, Dict[str, Tuple[str, int]]]]
    (the version without its V, {zip name: (address, size in bytes, 0 when not
    known)}), or None when no release was found, so the app starts as it is.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_release_asker
_release_page_asker
_release_page_reader
_release_reader
```

#### `_own_version_reader`

```text
---- Summary ----
Helper function to read the app's version from its Info.plist, where the build
writes it.

---- Inputs ----
app : Path
    The .app folder.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    The version, for example "2.4", or None when it cannot be read.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_release_asker`

```text
---- Summary ----
Helper function to ask GitHub for its newest release with macOS's own curl, which
uses the Mac's certificates (the app's Python cannot find any), keeping the reason
when there is no answer.

---- Inputs ----
url : str
    The address of GitHub's answer (a file:// address in the tests).

---- Globals read ----
ASK_TIMEOUT_S, HIDDEN (module constants).

---- Outputs ----
Tuple[Optional[str], str, bool]
    (GitHub's answer as JSON text, or None when there is none; why there is none,
    empty when there is one; True when GitHub refused the question).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_ask_problem_describer
```

#### `_release_page_asker`

```text
---- Summary ----
Helper function to ask the Releases page where its newest release is, with macOS's
own curl. The page leads to the release's own page, whose address ends in its tag.

---- Inputs ----
page_url : str
    The Releases page's address for the newest release.

---- Globals read ----
ASK_TIMEOUT_S, HIDDEN (module constants).

---- Outputs ----
Tuple[Optional[str], str]
    (the address the page leads to, or None when there is none; why there is none,
    empty when there is one).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_ask_problem_describer
```

#### `_release_page_reader`

```text
---- Summary ----
Helper function to read the newest release's version from the address the Releases
page leads to, and to make the addresses of its zips.

---- Inputs ----
address : str
    The newest release's own page, ending in /releases/tag/V<version>.
download_url : str
    Where the releases' zips are, each under its tag.

---- Globals read ----
APPLE_SILICON_ZIP, INTEL_ZIP, TAG_ADDRESS_PATTERN, VERSION_PATTERN (module
constants).

---- Outputs ----
Optional[Tuple[str, Dict[str, Tuple[str, int]]]]
    (the version without its V, {zip name: (address, 0 as the size is not
    known)}), or None when the address does not end in a release's tag.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_release_reader`

```text
---- Summary ----
Helper function to read the version and the zips from GitHub's answer about its
newest release.

---- Inputs ----
text : str
    GitHub's answer: JSON with "tag_name" (V<version>) and "assets", each with
    "name", "browser_download_url" and "size".

---- Globals read ----
VERSION_PATTERN (module constant).

---- Outputs ----
Optional[Tuple[str, Dict[str, Tuple[str, int]]]]
    (the version without its V, {zip name: (address, size in bytes)}), or None
    when the answer is not of that form.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_start_command_maker`

```text
---- Summary ----
Helper function to give the command that opens the app once it is swapped: macOS's
open, as a click does, passing on the check switch when it is set.

---- Inputs ----
app : Path
    The .app folder.

---- Globals read ----
SELF_TEST_SWITCH (module constant); os.environ['PORTIMAO_SELF_TEST'].

---- Outputs ----
List[str]
    The command and its arguments.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_status_window_maker`

```text
---- Summary ----
Helper function to open a small window that shows how the update is going. The
caller runs it with the returned function's ``mainloop`` attribute.

---- Inputs ----
version : str
    The version being installed.

---- Globals read ----
None.

---- Outputs ----
Optional[Callable[[str], None]]
    Function that shows a line of text in the window (safe from any thread), with
    the attributes ``mainloop`` and ``close``; None when no window can open.

---- Globals mutated ----
None. Opens a window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_translation_checker`

```text
---- Summary ----
Helper function to say whether the app runs under Rosetta (an Intel app on an Apple
Silicon Mac).

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    True under Rosetta.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_version_splitter`

```text
---- Summary ----
Helper function to turn a version into its numbers, for comparing.

---- Inputs ----
text : str
    A version such as "2.3.1" or "V2.3.1".

---- Globals read ----
VERSION_PATTERN (module constant).

---- Outputs ----
Optional[Tuple[int, ...]]
    The numbers without trailing zeros, so 2.3.0 and 2.3 are equal; None when the
    text is not a version.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_zip_downloader`

```text
---- Summary ----
Helper function to download the zip with macOS's own curl, showing how much has
come.

---- Inputs ----
url : str
    Where the zip is.
target : Path
    File to write.
size_bytes : int
    Size of the zip as GitHub gives it; 0 when not known.
version : str
    The version being installed, for the progress line.
show : Callable[[str], None]
    Shows a line of progress.

---- Globals read ----
CONNECT_TIMEOUT_S, HIDDEN, PROGRESS_STEP_S, STALL_BYTES_PER_S, STALL_S (module
constants).

---- Outputs ----
Optional[str]
    None when the whole zip came; otherwise what went wrong.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_zip_namer`

```text
---- Summary ----
Helper function to name the zip for this kind of Mac.

---- Inputs ----
machine : str
    The chip the app runs on, as platform.machine() gives it ('arm64' or 'x86_64').
is_translated : bool
    True when an Intel app runs under Rosetta on an Apple Silicon Mac.

---- Globals read ----
APPLE_SILICON_ZIP, INTEL_ZIP (module constants).

---- Outputs ----
str
    The zip's name: Apple Silicon also under Rosetta, so the Mac moves to the app
    made for it; Intel otherwise.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `swap_starter`

```text
---- Summary ----
Main function to start the swap on its own (launchers/mac_app_swapper.sh), so it
goes on once the app has closed: it waits for the app to close, moves the new app
into its place and opens it.

---- Inputs ----
swapper_text : str
    The text of the swap script; run with sh -c, so nothing is read from the app
    being replaced.
closing_pid : int
    Process id of the app that closes first.
app : Path
    The .app folder to replace.
new_app : Path
    The new .app folder, in the update folder beside it.
log_path : Path
    The update log, which the swap adds its lines to.
start_command : Sequence[str]
    The command that opens the app afterwards.

---- Globals read ----
HIDDEN (module constant).

---- Outputs ----
subprocess.Popen
    The swap, running on its own.

---- Globals mutated ----
None. Starts a process (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `update_installer`

```text
---- Summary ----
Main function to update the Mac app at its start. It asks GitHub for the newest
release (a few seconds at most) and, when it is newer, downloads the zip for this
kind of Mac with a small "Updating Portimao" window, and starts the swap, which puts
it in place once this app has closed and opens it. When GitHub does not answer it
asks once more, and when GitHub refuses it asks the Releases page; with no answer at
all it starts as it is and says nothing. When it cannot replace itself, or the
download fails, it starts as it is with a message saying where to download the new
one. Run from source, nothing is done. Every step, with the reason for any failure,
is written to logs/update.log.

---- Inputs ----
places : UserPlaces
    Where the user's things are kept, and whether this is the app.
executable : Optional[str]
    Path of the running program; None for this one (sys.executable).
release_url : str
    Where GitHub's answer about its newest release is (a file:// address in the
    tests).
closing_pid : Optional[int]
    Process id the swap waits for; None for this program.
start_command : Optional[Sequence[str]]
    Command that opens the app after the swap; None for macOS's open.
shows_messages : bool
    False to show no window and no message (for the tests).

---- Globals read ----
RELEASE_URL, SWAPPER, UPDATE_FOLDER_NAME (module constants).

---- Outputs ----
bool
    True when the swap has started, so the app must close now; False when the app
    starts as it is.

---- Globals mutated ----
None. Writes the update log, downloads into the update folder beside the app,
shows a window or a message and starts the swap (side effects).

---- Equations ----
None.

---- Helpers ----
_app_finder
_blocker_finder
_leftover_cleaner
_log_opener
_new_app_fetcher
_newer_checker
_newest_release_finder
_own_version_reader
_start_command_maker
_status_window_maker
_translation_checker
_zip_namer
swap_starter
update_notice_shower
```

## `utils_shared/attenuation.py`

Convert transmission spectra to the attenuation spectra used for decomposition.

### MAIN FUNCTIONS

#### `attenuation_converter`

```text
---- Summary ----
Main function to convert transmission spectra to attenuation (minus log10 of the
transmittance), as the instrument exports it.

---- Inputs ----
transmission : Union[Sequence[float], np.ndarray]
    Transmission as a fraction (0-1), as the .paf files hold it; any shape.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Attenuation with the shape of the input. Zero, negative or non-finite
    transmission becomes NaN.

---- Globals mutated ----
None.

---- Equations ----
attenuation = -log10(T), where T is the transmittance (fraction): less light than
the reference gives a positive attenuation. The fit shapes are stored with this
sign, so the decomposition uses them as they are.

---- Helpers ----
None.
```

#### `experiment_attenuation_adder`

```text
---- Summary ----
Main function to add an attenuation array to the spectral datasets of an experiment.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
datasets : Optional[Sequence[str]]
    Dataset names to convert; None converts all of them.
checked_range_nm : Optional[Tuple[float, float]]
    (lowest, highest) wavelength (nm) in which blank values are counted for the
    warning: the range of the fit when the spectra are decomposed, since a blank
    outside it changes no haem amount. None counts every wavelength.

---- Globals read ----
None.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError if a transmission array is not
    2D.

---- Globals mutated ----
experiment: adds raw_spectra[dataset]["attenuation"] (n_spectra x n_wavelengths) for
each converted dataset; shows a warning with the number of blank values inside
checked_range_nm (side effect).

---- Equations ----
None.

---- Helpers ----
attenuation_converter
warning_shower
```

## `utils_shared/averaging.py`

Event-window averaging of OCR and haem data for one experiment.

### AVERAGING HELPERS

#### `_baseline_change_adder`

```text
---- Summary ----
Helper function to add the change from the baseline window to the statistics of a
window.

---- Inputs ----
window_stats : Dict[str, Dict[str, float]]
    Statistics of one window, from window_statistics_calculator; modified in place.
baseline_stats : Dict[str, Dict[str, float]]
    Statistics of the baseline window (average0).
percent_of_baseline : bool
    False for sources that already are a change from a reference (baseline near 0),
    where a percentage is meaningless.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
window_stats: adds "delta" and "change" to every column.

---- Equations ----
delta = mean - baseline_mean; change = mean / baseline_mean x 100 (NaN if
percent_of_baseline is False, the baseline is 0 or a value is not finite).

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `experiment_averages_calculator`

```text
---- Summary ----
Main function to calculate event-window statistics for VoO2 and haem data and store
them in the experiment: the baseline, the settled windows (ending before the next
addition) and, when asked for, the quick windows (starting after each addition).

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
window_minutes : float
    Length of each averaging window, in minutes (> 0).
gap_minutes : float
    How long before the next addition each window ends, in minutes (>= 0).
final_window_gap_minutes : float
    How long before the end of the recording the last window ends, in minutes (>=
    0).
baseline_minimum_seconds : float
    Least time the data inside the baseline window (average0) must span, in
    seconds (>= 0).
vo2_source : Optional[str]
    VoO2 source key (e.g. 'od', 'raw', 'percent'); None leaves VoO2 out.
haem_source : Optional[str]
    Haem source key (e.g. 'abs', 'delta_abs_od'); None leaves the haems out.
quick_minutes : Optional[float]
    Length of each quick window, in minutes (> 0); None for no quick windows.
delay_minutes : float
    How long after its addition each quick window starts, in minutes (>= 0).
is_settled : bool
    False leaves the settled windows out (the baseline stays).

---- Globals read ----
schema.VO2_KEYS, HAEM_KEYS and DELTA_HAEM_SOURCES.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError for invalid settings, no
    source, no events or invalid times. A window that does not fit between two
    additions (or after the last one) is skipped, not an error; so is the baseline
    window when it holds too little data, and the run then has no baseline: the
    delta and change of every window are NaN.

---- Globals mutated ----
experiment: adds experiment["averages"] = {"settings", "windows", "skipped"}
(layout in DATA_FORMAT.md).

---- Equations ----
average0 ends gap_minutes before the first event and starts window_minutes before
its end, or at the start of the recording when that is later; it is skipped when
the points inside it span less than baseline_minimum_seconds. averageN ends
gap_minutes before event N+1 (final_window_gap_minutes before the end of the
recording for the last event); each window starts window_minutes before its end
and is skipped when that is before its own event. quickN starts delay_minutes
after event N and ends quick_minutes later; it is skipped when that is after event
N+1 (the end of the recording for the last event). change = mean /
mean(average0) x 100 (NaN for delta abs sources); delta = mean - mean(average0),
for the settled and the quick windows alike.

---- Helpers ----
_baseline_change_adder
quick_span_lister
source_resolver
time_getter
window_span_lister
window_statistics_calculator
```

#### `kind_span_lister`

```text
---- Summary ----
Main function to give the windows a figure that uses one kind of window averages
over: the baseline, then the window of that kind of each addition, all under the
names of the settled windows, so the figure reads either kind in the same way.

---- Inputs ----
kind : str
    'settled' or 'quick'.
event_times_min : List[float]
    Times of the additions (min), in order; at least one.
recording_span_min : Tuple[float, float]
    (first, last) time of the data (min).
window_minutes : float
    Length of the baseline and of each settled window, in minutes.
gap_minutes : float
    How long before the next addition the baseline and each settled window end, in
    minutes.
final_window_gap_minutes : float
    How long before the end of the recording the last settled window ends, in
    minutes.
quick_minutes : float
    Length of each quick window, in minutes.
delay_minutes : float
    How long after its addition each quick window starts, in minutes.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, float, float, Optional[str]]]
    [(name, start, end, problem)] in minutes: 'average0' (the baseline), then
    'average1' for the first addition and so on, as window_span_lister gives them.
    Raises ValueError for a kind that is neither.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
quick_span_lister
window_span_lister
```

#### `quick_span_lister`

```text
---- Summary ----
Main function to give where the quick windows of one file fall, and which do not
fit: one window starting a set time after each addition. The averaging and the plot
of the window step both use it.

---- Inputs ----
event_times_min : List[float]
    Times of the additions (min), in order.
recording_span_min : Tuple[float, float]
    (first, last) time of the data (min).
quick_minutes : float
    Length of each quick window, in minutes.
delay_minutes : float
    How long after its addition each quick window starts, in minutes.

---- Globals read ----
FIT_TOLERANCE_MIN (module constant).

---- Outputs ----
List[Tuple[str, float, float, Optional[str]]]
    [(name, start, end, problem)] in minutes, 'quick1' after the first addition and
    so on. The problem is None for a window that fits, or one sentence saying why
    it does not.

---- Globals mutated ----
None.

---- Equations ----
quickN: start = addition N + delay; end = start + length; it does not fit when end
> addition N + 1 (the end of the recording for the last addition).

---- Helpers ----
None.
```

#### `window_kind_picker`

```text
---- Summary ----
Main function to give a figure that uses one kind of window the averages of an
experiment with the baseline and the windows of that kind only, the quick windows
under the names of the settled ones, so the figure reads either kind in the same
way.

---- Inputs ----
averages : dict
    experiment['averages'] (DATA_FORMAT.md); not changed.
kind : str
    'settled' or 'quick'.

---- Globals read ----
None.

---- Outputs ----
dict
    A copy of the averages whose 'windows' and 'skipped' hold the baseline
    ('average0') and the windows of the kind, named 'average1' ... by the number
    of their addition. Raises ValueError for a kind that is neither.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `window_layout_finder`

```text
---- Summary ----
Main function to give what the window step draws on the plot of one file: the two
edges of every averaging window, and the windows as parts to shade, those that do
not fit apart. The first edge of each kind carries its words. The baseline is
there when either kind of window is switched on.

---- Inputs ----
values : Dict[str, float]
    The settled and the quick windows of the file (WINDOW_KEYS).
event_times_min : List[float]
    Times of the file's additions on the time axis of the plot (min), in order,
    not those marked ignore.
recording_span_min : Tuple[float, float]
    (first, last) time of the data on that axis (min).
final_window_gap_minutes : float
    How long before the end of the recording the last window ends, in minutes.
baseline_minimum_seconds : float
    Least length of the baseline window, in seconds.

---- Globals read ----
None.

---- Outputs ----
Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
    ([(field, time in min, words, kind)], [(start, end, kind)]). The baseline and
    the settled windows first: the start of each is an edge of the field
    'window_s' (kind 'average'), the end of each but the last settled window an
    edge of 'gap_s' (kind 'average_end'; the last window ends a fixed time before
    the end of the recording). Then the quick windows: the start of each is an
    edge of 'delay_s' (kind 'quick'), its end an edge of 'quick_s' (kind
    'quick_end'). A part has the kind 'average', 'quick', or 'average_unfit' for a
    window that does not fit. Both lists are empty when both kinds are switched off
    or the file has no additions.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
quick_span_lister
window_span_lister
```

#### `window_pointer_reader`

```text
---- Summary ----
Main function to turn where the mouse holds an edge of an averaging window into
the value of its field, in seconds rounded to whole steps: for a settled window
its length (a start edge) or how long before the next addition it ends (an end
edge); for a quick window how long after its addition it starts (a start edge) or
its length (an end edge). The edge held is the one of its kind nearest the mouse,
which stays the same edge while it follows the mouse.

---- Inputs ----
values : Dict[str, float]
    The settled and the quick windows of the file now (WINDOW_KEYS).
key : str
    'window_s' for the start and 'gap_s' for the end of a settled window or the
    baseline, 'delay_s' for the start and 'quick_s' for the end of a quick window.
time_min : float
    Time under the mouse on the time axis of the plot (min).
event_times_min : List[float]
    Times of the file's additions on that axis (min), in order.
recording_span_min : Tuple[float, float]
    (first, last) time of the data on that axis (min).
final_window_gap_minutes : float
    How long before the end of the recording the last window ends, in minutes.
step_seconds : float
    The step the result is rounded to, in seconds (> 0).

---- Globals read ----
None.

---- Outputs ----
float
    The new value of the field, in seconds: a length of at least one step, or a
    gap or a start after the addition of at least 0. The value as it is when the
    file has no edge of that kind.

---- Globals mutated ----
None.

---- Equations ----
length_s = round((end of the window held - time) x 60 / step) x step;
gap_s = round((addition after the window held - time) x 60 / step) x step, with
the addition after a window = its end + the gap now;
delay_s = round((time - addition of the quick window held) x 60 / step) x step,
with the addition of a quick window = its start - the delay now;
quick_s = round((time - start of the quick window held) x 60 / step) x step.

---- Helpers ----
quick_span_lister
window_span_lister
```

#### `window_span_lister`

```text
---- Summary ----
Main function to give where the averaging windows of one file fall, and which do
not fit: the baseline window before the first addition, then one window after each
addition. The averaging and the plot of the window step both use it.

---- Inputs ----
event_times_min : List[float]
    Times of the additions (min), in order; at least one.
recording_span_min : Tuple[float, float]
    (first, last) time of the data (min).
window_minutes : float
    Length of each window, in minutes.
gap_minutes : float
    How long before the next addition each window ends, in minutes.
final_window_gap_minutes : float
    How long before the end of the recording the last window ends, in minutes.
baseline_minimum_seconds : float
    Least length of the baseline window, in seconds; 0 (the standard) never finds
    it too short, for a caller that checks the data inside it itself.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, float, float, Optional[str]]]
    [(name, start, end, problem)] in minutes, 'average0' (the baseline) first, then
    'average1' after the first addition and so on. The problem is None for a
    window that fits, or one sentence saying why it does not.

---- Globals mutated ----
None.

---- Equations ----
average0: end = first addition - gap; start = end - window, or the start of the
recording when that is later; too short when end - start < the least length.
averageN: end = addition N + 1 - gap (the end of the recording - final gap for the
last addition); start = end - window; it does not fit when start < addition N.

---- Helpers ----
None.
```

#### `window_statistics_calculator`

```text
---- Summary ----
Main function to calculate the mean and sample SD of every measurement column inside
a time window.

---- Inputs ----
df : pd.DataFrame
    Data frame with a time column and measurement columns (DATA_FORMAT.md).
start_time : float
    Window start, in minutes.
end_time : float
    Window end, in minutes.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Dict[str, float]]
    {column: {"mean", "sd"}}. Values are NaN when no finite point falls in the
    window (SD: fewer than two).

---- Globals mutated ----
None.

---- Equations ----
mean = sum(x) / n; SD = sqrt(sum((x - mean)^2) / (n - 1)) over the finite points
with start_time <= t <= end_time.

---- Helpers ----
measurement_column_finder
time_getter
value_getter
```

#### `window_value_setter`

```text
---- Summary ----
Main function to set one value of the settled or the quick windows (a length, how
long before the next addition or after its own a window ends or starts, or
whether there are windows of that kind), as dragged, typed or ticked in the window
step. A value that cannot be used leaves everything as it is.

---- Inputs ----
values : Dict[str, float]
    The settled and the quick windows now (WINDOW_KEYS); not changed.
key : str
    The field set: one of WINDOW_KEYS.
value : float
    Its new value: seconds, or for 'is_on' and 'quick_is_on' anything but 0 for
    windows.

---- Globals read ----
None.

---- Outputs ----
Dict[str, float]
    The new values. A length of 0 or less, or a gap or a start after the addition
    below 0, changes nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/comparison_plotter.py`

Two experiments side by side in one figure.

### COMPARISON PLOTTER HELPERS

#### `_overhang_calculator`

```text
---- Summary ----
Helper function to measure how far the labels of a plot stick out to the left and
right of its main axes.

---- Inputs ----
fig : Figure
    Matplotlib figure.
members : List[Axes]
    All axes of the plot.
main : Axes
    Main axes the overhang is measured from.

---- Globals read ----
Needs a figure that has been drawn or can be rendered.

---- Outputs ----
Tuple[float, float]
    (points to the left, points to the right).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_renderer_getter
```

#### `_renderer_getter`

```text
---- Summary ----
Helper function to get the renderer of a figure canvas.

---- Inputs ----
fig : Figure
    Matplotlib figure.

---- Globals read ----
None.

---- Outputs ----
Any
    Matplotlib renderer.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `comparison_figure_plotter`

```text
---- Summary ----
Main function to draw two experiments side by side with their own y axes, panel
letters a and b and a gap sized to their labels, and save it as svg and png.

---- Inputs ----
first : dict
    Experiment drawn on the left (panel a).
second : dict
    Experiment drawn on the right (panel b).
config : dict
    Individual-experiment plot settings (config.py); uses LAYOUT_PAD_PT, FIGURE_DPI,
    TITLE_GAP_PT and TIGHT_BBOX.
export_root : Path
    Results folder.
figure_size : Tuple[float, float]
    (width, height) of the whole figure in inches.
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
share_time_axis : bool
    True gives both plots the same time range.

---- Globals read ----
GAP_EXTRA_PT_PER_PAD (module constant).

---- Outputs ----
str
    File stem of the saved figure.

---- Globals mutated ----
None. Writes <export_root>/<stem>.svg and .png (side effect); the figure
is closed before returning.

---- Equations ----
None.

---- Helpers ----
_overhang_calculator
experiment_drawer
figure_canvas_fitter
figure_saver
file_name_sanitiser
gap_space_calculator
panel_letter_adder
watermark_style_builder
```

## `utils_shared/dataset_settings.py`

The settings kept with a dataset: read from and written to a file in its folder.

### HELPERS

#### `_event_plainer`

```text
---- Summary ----
Helper function to keep an event's label, concentration and whether it is ignored
as plain numbers and text, so it can be written to the settings file.

---- Inputs ----
event : dict
    {'datapoint', 'label', 'concentration_uM', 'ignored'} as the event questions
    give it.

---- Globals read ----
None.

---- Outputs ----
dict
    The same keys, as int, str, float or None, and bool.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_export_folder_resolver`

```text
---- Summary ----
Helper function to turn the results folder written in the settings file back into
a full path.

---- Inputs ----
folder : Path
    The dataset folder.
text : Optional[str]
    The results folder as written in the file: relative to the dataset folder, or
    a full path; None or empty when none was kept.

---- Globals read ----
None.

---- Outputs ----
Optional[Path]
    The results folder, or None when none was kept or a full path was written on
    another computer (its drive or root folder is not there).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_export_folder_shortener`

```text
---- Summary ----
Helper function to write the results folder relative to the dataset folder when it
is inside it, so the settings still hold after the dataset is copied elsewhere.

---- Inputs ----
folder : Path
    The dataset folder.
export_root : Path
    The results folder.

---- Globals read ----
None.

---- Outputs ----
str
    The path from the dataset folder with forward slashes ('results'), or the full
    path when the results folder is somewhere else.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `dataset_settings_reader`

```text
---- Summary ----
Main function to read the settings last saved for a dataset from the file in its
folder.

---- Inputs ----
folder : Path
    The dataset folder (the folder of the .paf files).

---- Globals read ----
SETTINGS_FILE_NAME, RETIRED_HAEM_MODES, RETIRED_HAEM_MODE_KEYS (module constants).

---- Outputs ----
dict
    {'export_folder': Optional[Path], 'files': dict, 'answers': dict}
    (DATA_FORMAT.md, dataset_settings). An empty dict when the dataset was never
    saved or its file cannot be read, so the standard settings are used. A haem
    way of showing no longer offered (RETIRED_HAEM_MODES) is given as its successor.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None.

---- Helpers ----
_export_folder_resolver
```

#### `dataset_settings_saver`

```text
---- Summary ----
Main function to save the settings of a dataset in a file in its folder, so the
dataset opens with them next time, on this computer or another.

---- Inputs ----
folder : Path
    The dataset folder (the folder of the .paf files).
export_root : Path
    The results folder.
files : dict
    {file name: limits in minutes, OD values and events} as file_settings_merger
    builds it.
answers : dict
    The answers of the run.

---- Globals read ----
SETTINGS_FILE_NAME (module constant).

---- Outputs ----
bool
    True when the file was written; False when the folder cannot be written to.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
None.

---- Helpers ----
_export_folder_shortener
```

#### `file_settings_merger`

```text
---- Summary ----
Main function to build the files part of the dataset's settings: for each file of
this run its limits, OD values, events and regions laid over what was saved before.
A value not asked this run (the OD when not scaling by OD) stays as it was saved,
so it is offered next time; files not in this run are kept as they were.

---- Inputs ----
remembered : Dict[str, dict]
    The files part saved before (dataset_settings, DATA_FORMAT.md); empty for a
    dataset never saved.
limits : Dict[str, dict]
    {file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end'}} of this
    run.
details : Dict[str, dict]
    {file name: {'OD', 'volume', 'dilution_factor', 'events'}} of this run; the OD
    values only when scaling by OD.
regions : Optional[Dict[str, Dict[str, float]]]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} of
    this run, as times on the original recording (min); a region not chosen has
    its two edges together. None when the regions were not handled this run, so
    those saved before stay.

---- Globals read ----
SAVED_VALUE_KEYS (module constant); REGION_KEYS, REGION_NAMES.

---- Outputs ----
Dict[str, dict]
    {file name: limits, then 'OD', 'volume', 'dilution_factor' (floats),
    'events' and 'regions' (DATA_FORMAT.md, dataset_settings) where known}. A
    file of this run with neither region chosen has no 'regions'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_event_plainer
```

## `utils_shared/delta_psi.py`

The maths of delta psi, the membrane potential, from how reduced the two b haems (bH

### DELTA PSI HELPERS

#### `_settings_validator`

```text
---- Summary ----
Helper function to refuse numbers of the method that would give a wrong delta psi,
each with a plain sentence saying what to change.

---- Inputs ----
midpoints_mV : Dict[str, float]
    {bH_first, bL_first, bH_second, bL_second}: the midpoint potentials (mV).
share : float
    Share of the membrane potential between the two haems (0.5 is half).
temperature_c : float
    Temperature of the sample (°C).
limits_percent : Sequence[float]
    (lowest, highest) % reduced at which delta psi is still given.

---- Globals read ----
MIDPOINT_KEYS, MIDPOINT_TOLERANCE_MV, ZERO_CELSIUS_K.

---- Outputs ----
None
    Nothing. Raises ValueError for a missing or blank midpoint, two drops that
    differ, a share not above 0, a temperature at or below absolute zero, and
    limits that are not 0 < lowest < highest < 100.

---- Globals mutated ----
None.

---- Equations ----
bH_first - bH_second must equal bL_first - bL_second: both are the push of one
electron on the other, so the two orders of filling the haems cost the same.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `b_haem_column_finder`

```text
---- Summary ----
Main function to find the bH and the bL column of a haem table by their names,
however they are written ("Cyt $b_H$", "cyt bH", "bH").

---- Inputs ----
haem_table : pd.DataFrame
    Haem table (time, spectrum index and one column per haem).

---- Globals read ----
BH_NAME, BL_NAME; HAEM_NAME_PREFIXES.

---- Outputs ----
Optional[Tuple[str, str]]
    (bH column, bL column), or None when the table does not have exactly one of
    each, so delta psi cannot be worked out from it.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
measurement_column_finder
name_simplifier
```

#### `delta_psi_calculator`

```text
---- Summary ----
Main function to work out delta psi, and the redox potential at each of the two
b haems, from their % oxidised in every spectrum.

---- Inputs ----
percent_bH : Sequence[float]
    % oxidised of bH, shape (n_spectra,).
percent_bL : Sequence[float]
    % oxidised of bL, shape (n_spectra,).
midpoints_mV : Dict[str, float]
    {bH_first, bL_first, bH_second, bL_second}: the midpoint potential of each
    haem with the other oxidised (first) and with the other reduced (second), mV.
share : float
    Share of the membrane potential that lies between the two haems (0.5 is half).
temperature_c : float
    Temperature of the sample (°C).
limits_percent : Sequence[float]
    (lowest, highest) % reduced of a haem at which delta psi is still given.

---- Globals read ----
None.

---- Outputs ----
Dict[str, np.ndarray]
    {'delta_psi', 'potential_bH', 'potential_bL'}: mV, each of shape (n_spectra,),
    float64. All three are NaN in a spectrum where bH or bL is blank, or less
    reduced than the lowest limit, or more reduced than the highest. Raises
    ValueError for numbers of the method that cannot be used (_settings_validator)
    and for two haems of different lengths.

---- Globals mutated ----
None.

---- Equations ----
R_H = 1 - P_H / 100; R_L = 1 - P_L / 100 (fractions reduced).
s = R x T / F (mV); k = exp(-(bH_first - bH_second) / s).
n, h, l, b: state_fractions_solver.
E_H = bH_first - s x ln(h / n); E_L = bL_first - s x ln(l / n).
delta psi = (E_H - E_L) / share.

---- Helpers ----
_settings_validator
state_fractions_solver
thermal_voltage_finder
```

#### `delta_psi_table_builder`

```text
---- Summary ----
Main function to build the delta psi table of a file from its % oxidised table.

---- Inputs ----
haem_percent : pd.DataFrame
    % oxidised table of the file (time, spectrum index and one column per haem).
midpoints_mV : Dict[str, float]
    The four midpoint potentials (mV); see delta_psi_calculator.
share : float
    Share of the membrane potential between the two haems.
temperature_c : float
    Temperature of the sample (°C).
limits_percent : Sequence[float]
    (lowest, highest) % reduced at which delta psi is still given.

---- Globals read ----
DELTA_PSI_COLUMN, BH_POTENTIAL_COLUMN, BL_POTENTIAL_COLUMN; TIME_COLUMN,
SPECTRUM_INDEX_COLUMN.

---- Outputs ----
Optional[pd.DataFrame]
    The time and spectrum index of the % table, then delta psi and the potential
    at bH and at bL (mV), one row per spectrum; or None when the table does not
    have one bH and one bL. table.attrs['delta_psi'] holds the numbers used:
    {'midpoints_mV', 'share', 'temperature_c', 'limits_percent', 'bH', 'bL' (the
    two columns), 'spectra_with_value'}. Raises ValueError as
    delta_psi_calculator does.

---- Globals mutated ----
None.

---- Equations ----
delta_psi_calculator.

---- Helpers ----
b_haem_column_finder
delta_psi_calculator
value_getter
```

#### `state_fractions_solver`

```text
---- Summary ----
Main function to split the pair of b haems into its four states (neither reduced,
only bH, only bL, both) from how reduced each haem is.

---- Inputs ----
reduced_bH : Sequence[float]
    Fraction of bH that is reduced, above 0 and below 1, shape (n,).
reduced_bL : Sequence[float]
    Fraction of bL that is reduced, above 0 and below 1, shape (n,).
factor : float
    k, how much rarer "both reduced" is made by the push of one electron on the
    other (1 for no push), above 0.

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    (n, h, l, b): the fractions of the pairs with neither haem reduced, only bH,
    only bL and both, each of shape (n,), adding up to 1.

---- Globals mutated ----
None.

---- Equations ----
R_H = h + b; R_L = l + b; n + h + l + b = 1; (b x n) / (h x l) = k. Together:
(1 - k) b^2 + B b - k R_H R_L = 0 with B = 1 - (1 - k)(R_H + R_L), whose one
answer between 0 and the smaller of R_H and R_L is
b = 2 k R_H R_L / (B + sqrt(B^2 + 4 (1 - k) k R_H R_L)).
Then h = R_H - b, l = R_L - b, n = 1 - R_H - R_L + b.

---- Helpers ----
None.
```

#### `thermal_voltage_finder`

```text
---- Summary ----
Main function to give s = R x T / F, the voltage that goes with a temperature, in
mV (26.7 mV at 37 °C).

---- Inputs ----
temperature_c : float
    Temperature (°C), above absolute zero.

---- Globals read ----
GAS_CONSTANT_J_PER_MOL_K, FARADAY_C_PER_MOL, ZERO_CELSIUS_K.

---- Outputs ----
float
    s (mV).

---- Globals mutated ----
None.

---- Equations ----
s = R x (temperature + 273.15) / F x 1000.

---- Helpers ----
None.
```

## `utils_shared/experiment_processing.py`

Reading and processing of one experiment (everything before the figure and the export).

### EXPERIMENT PROCESSING HELPERS

#### `_skip_reporter`

```text
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
```

### MAIN FUNCTIONS

#### `event_settings_merger`

```text
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
```

#### `experiment_data_processor`

```text
---- Summary ----
Main function to read (or take) one experiment and process its data: trim, decompose
into haems, find each haem's oxidised and reduced level and its % oxidised (a file
with both regions), work out delta psi from bH and bL (when switched on), scale by
OD, put the OCR on its % of the range, choose the plotted sources and average
around the events. It draws and saves nothing.

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
settings.REGION_MINIMUM_POINTS, settings.BASELINE_MINIMUM_SECONDS,
settings.DELTA_PSI_MIDPOINT_ANSWERS, settings.DELTA_PSI_LIMIT_ANSWERS;
BACKGROUND_LABELS.

---- Outputs ----
dict
    {experiment, od_available, vo2_source, haem_source}. A file with both regions
    has experiment['haem_levels'] and experiment['haem_percent'] (DATA_FORMAT.md);
    when % oxidised is asked for a file without them, its haem source is
    'delta_abs'. With delta psi switched on, a file with % oxidised, one bH and
    one bL has experiment['delta_psi']. Prints progress and the reason when a step is skipped (side
    effect).

---- Globals mutated ----
None. Processes the experiment dictionary in place (side effect).

---- Equations ----
None.

---- Helpers ----
_skip_reporter
delta_psi_table_builder
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
```

## `utils_shared/figure_layout.py`

Journal-aware figure sizing and automatic layout.

### FIGURE LAYOUT HELPERS

#### `_renderer_getter`

```text
---- Summary ----
Helper function to get the renderer of a figure canvas.

---- Inputs ----
fig : Figure
    Matplotlib figure.

---- Globals read ----
None.

---- Outputs ----
Any
    Matplotlib renderer.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `figure_canvas_fitter`

```text
---- Summary ----
Main function to set the figure margins so that everything drawn sits a fixed
padding inside the figure edge, whatever the figure size, font size or label
lengths.

---- Inputs ----
fig : Figure
    Matplotlib figure.
pad_pt : float
    Whitespace between the content and the figure edge in points.
suptitle : Optional[Any]
    Optional figure title (Text from fig.suptitle); it is placed pad_pt below the
    top edge.
suptitle_gap_pt : float
    Gap between the title and the content in points.
iterations : int
    Maximum number of fitting passes.
tolerance_pt : float
    Stop when no margin moves by more than this many points.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; the figure margins are changed in place. Raises ValueError when the
    contents leave no room for the axes.

---- Globals mutated ----
None. Changes the subplot margins of ``fig`` and the layout flag and position of
``suptitle`` (side effect).

---- Equations ----
Each margin = (pad + width of the decoration outside the axes) / figure size,
repeated until the largest change is below tolerance_pt.

---- Helpers ----
_renderer_getter
```

#### `figure_finisher`

```text
---- Summary ----
Helper function to fit the margins to the drawn content, add the panel letters at
the top-left of each panel and fit again.

---- Inputs ----
fig : Figure
    Matplotlib figure.
config : dict
    Figure settings dictionary built in custom_config.py.
panels : list
    List of (letter, main axes, [axes of the panel]) tuples.
suptitle : Any
    Figure title text object, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Resizes the layout of ``fig`` and adds text to it (side effect).

---- Equations ----
None.

---- Helpers ----
figure_canvas_fitter
panel_letter_adder
```

#### `figure_size_calculator`

```text
---- Summary ----
Main function to calculate the (width, height) of a figure in inches from a journal
specification.

---- Inputs ----
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
columns : float
    Key of spec["widths_mm"]: 1, 1.5 or 2 columns wide.
height : float
    Fraction of the journal page height (spec["page_height_mm"]), above 0 and at
    most 1; 0.5 is half a page.

---- Globals read ----
MM_PER_INCH (module constant).

---- Outputs ----
Tuple[float, float]
    (width, height) in inches. Raises ValueError for an unknown column count or a
    height outside (0, 1].

---- Globals mutated ----
None.

---- Equations ----
width_in = widths_mm[columns] / 25.4; height_in = page_height_mm x height / 25.4.

---- Helpers ----
None.
```

#### `figure_style_builder`

```text
---- Summary ----
Main function to derive every font size, padding and line width of the figures from
the journal specification and three master settings.

---- Inputs ----
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
base_font_pt : float
    Axis-label size in points; tick labels are 1 pt smaller and titles 1 pt larger.
spacing : float
    Tightness of all paddings and gaps: 1.0 is the default, 1.2 is 20 % looser, 0.8
    is 20 % tighter.
line_width_pt : float
    Width of the data lines in points; axes, reference and event lines are scaled
    from it.

---- Globals read ----
None.

---- Outputs ----
dict
    Style dictionary with 'fonts' {tick, label, title, panel_letter} and the points
    values unit, tick_length, tick_pad, label_pad, title_pad, edge_pad, title_gap,
    event_label_offset, line_width, axes_line_width and thin_line_width.

---- Globals mutated ----
None.

---- Equations ----
unit = base_font_pt x spacing; every padding is a multiple of unit (for example
title_pad = 0.8 x unit); axes_line_width = 0.65 x line_width_pt; thin_line_width =
0.5 x line_width_pt.

---- Helpers ----
None.
```

#### `figure_style_checker`

```text
---- Summary ----
Main function to list warnings for fonts outside the journal range or a figure
taller than the journal allows.

---- Inputs ----
journal : str
    Journal name, used in the warning text.
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
fonts : dict
    Font sizes in points keyed by role, as in make_style()['fonts'].
size_inches : Tuple[float, float]
    (width, height) of the figure in inches.
label : str
    Text put in front of each warning.

---- Globals read ----
MM_PER_INCH (module constant).

---- Outputs ----
List[str]
    Warning messages; empty when the style fits the journal.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `gap_space_calculator`

```text
---- Summary ----
Main function to calculate the GridSpec wspace or hspace that leaves a given gap
between equal cells.

---- Inputs ----
gap_pt : float
    Wanted gap between neighbouring cells in points.
extent_pt : float
    Total width or height covered by the cells and gaps in points.
n : int
    Number of equal cells.

---- Globals read ----
None.

---- Outputs ----
float
    GridSpec spacing as a fraction of the average cell size; 0 for a single cell.
    Raises ValueError when the gaps do not fit in extent_pt.

---- Globals mutated ----
None.

---- Equations ----
room = extent_pt - gap_pt x (n - 1); space = gap_pt x n / room.

---- Helpers ----
None.
```

#### `panel_letter_adder`

```text
---- Summary ----
Main function to write each panel letter just above the top edge of its panel's
main axes, to the left of everything the panel draws on that side.

---- Inputs ----
fig : Figure
    Matplotlib figure.
panels : list
    [(letter, main axes, [axes of the panel]), ...]; a fourth item (text, text
    keyword arguments) adds a small note after the letter.
font_pt : float
    Letter size in points.
case : str
    'upper' or 'lower'.
weight : str
    Matplotlib font weight of the letters.
gap_pt : float
    Extra gap above the panel in points.

---- Globals read ----
None.

---- Outputs ----
list
    The annotation artists created. Raises ValueError for an unknown case.

---- Globals mutated ----
None. Adds annotations to the main axes of each panel (side effect); call
figure_canvas_fitter afterwards so the letters are inside the margins.

---- Equations ----
None.

---- Helpers ----
_renderer_getter
```

#### `stack_legend_drawer`

```text
---- Summary ----
Main function to draw one legend for a vertical stack of axes (an individual
experiment plot). By default it sits in the white space to the right of the stack,
centred on the height of the stack (or on the span down to ``bottom``); with
``below_pt`` it sits centred under the stack instead. It holds every labelled line
of the stack (set and measured O2, then each haem) except the OCR trace.

---- Inputs ----
axes : List[Axes]
    Axes of the stack, top first.
config : dict
    Settings; uses LEGEND_FONT_SIZE, LEGEND_FRAME, LEGEND_FRAME_LINE_WIDTH
    (optional) and VO2_LABEL (optional).
bottom : Optional[Axes]
    Lowest axes of the span to centre on (for example the bottom row of a grid of
    stacks), or None for the stack itself.
below_pt : Optional[float]
    When set, the legend hangs this many points below the stack's lowest axes
    instead of sitting at the right.
columns : int
    Number of legend columns.

---- Globals read ----
None.

---- Outputs ----
Optional[Any]
    The legend, or None when the stack has no labelled lines.

---- Globals mutated ----
None. Adds a legend to an axes of the stack (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `text_extent_calculator`

```text
---- Summary ----
Main function to calculate the width and height of the bounding box of a piece of
text after rotating it.

---- Inputs ----
text : str
    Plain text without mathtext.
size_pt : float
    Font size in points.
rotation_deg : float
    Rotation of the text in degrees.

---- Globals read ----
None.

---- Outputs ----
Tuple[float, float]
    (width, height) in points of the rotated bounding box; the unrotated height is
    at least 1.2 x size_pt.

---- Globals mutated ----
None.

---- Equations ----
w = |W cos(a)| + |H sin(a)|; h = |W sin(a)| + |H cos(a)|, where W and H are the
unrotated text width and height and a is the rotation angle.

---- Helpers ----
None.
```

## `utils_shared/helpers.py`

Small, generic utilities shared by several modules.

### MAIN FUNCTIONS

#### `concentration_formatter`

```text
---- Summary ----
Main function to write a concentration given in micromolar with the most readable
unit: M from 1 000 000 µM, mM from 1000 µM and µM below that. It is the one place
where a concentration is turned into text.

---- Inputs ----
concentration_um : Any
    Concentration in micromolar (µM); anything float() accepts, or None when the
    user gave none.

---- Globals read ----
MISSING_CONCENTRATION (module constant).

---- Outputs ----
str
    For example '2 µM', '2 mM' (from 2000 µM) or '1.5 mM'; the unit is written
    with the micro sign. MISSING_CONCENTRATION ('? µM') for None. Raises ValueError
    or TypeError if the value is neither None nor a number.

---- Globals mutated ----
None.

---- Equations ----
mM = uM / 1000; M = uM / 1 000 000.

---- Helpers ----
None.
```

#### `excel_sheet_namer`

```text
---- Summary ----
Main function to make a valid, unique Excel sheet name (at most 31 characters, no
special characters).

---- Inputs ----
name : Any
    Proposed sheet name (converted with str).
used : set
    Lower-cased sheet names already taken; the new name is added to it.

---- Globals read ----
None.

---- Outputs ----
str
    Sheet name, with a numeric suffix when the name is already taken.

---- Globals mutated ----
None. Adds the lower-cased result to ``used`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `figure_capture_setter`

```text
---- Summary ----
Main function to switch figure saving to preview mode (or back). While a capture
function is set, figure_saver hands each figure to it and writes no file, so the
experiment browser can show a figure before it is made for real.

---- Inputs ----
capture : Optional[Callable[[Figure, str], None]]
    Function called with (figure, file name stem) instead of saving, or None for
    normal saving.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
Sets _figure_capture (module state).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `figure_saver`

```text
---- Summary ----
Main function to save a figure in each requested format at exactly the requested
size. The size is pinned again just before saving because interactive backends
resize figures, and tight cropping is off unless requested.

---- Inputs ----
fig : Figure
    Matplotlib figure to save.
folder : Path
    Output folder; created if missing (not in preview mode).
stem : str
    File name without the extension.
formats : Sequence[str]
    File extensions, for example ("svg", "png").
size : Tuple[float, float]
    Width and height in inches.
dpi : int
    Resolution in dots per inch; the saved pixel size is size x dpi.
tight : bool
    True to crop the canvas around the artists (bbox_inches="tight").

---- Globals read ----
_figure_capture (module state).

---- Outputs ----
List[Path]
    Paths of the saved files, in the order of ``formats``; empty in preview mode.

---- Globals mutated ----
None. Resizes the figure to ``size`` and writes the files, or in preview mode only
hands the figure to the capture function (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `file_name_sanitiser`

```text
---- Summary ----
Main function to clean a file name: the one rule every file the program names goes
through.

---- Inputs ----
name : Any
    Proposed name (converted with str).
default : str
    Name used when nothing is left after cleaning.

---- Globals read ----
None.

---- Outputs ----
str
    File name with the characters < > : " / backslash | ? * replaced by underscores,
    and without dots or spaces at either end (a leading dot hides a file on a Mac
    or Linux, and Windows drops a trailing one).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `haem_order_finder`

```text
---- Summary ----
Main function to find the order haems are listed, plotted and exported in: every a
haem, then every b, then every c, then any name of no known type; within a type in
alphabetical order of the name (ignoring case and punctuation), so a605, b557, bH,
bL, cc whatever the order of the fit file.

---- Inputs ----
names : Sequence[Any]
    Haem names, plain or in figure form (converted with str).

---- Globals read ----
HAEM_TYPE_ORDER (module constant).

---- Outputs ----
List[int]
    The position in ``names`` of each haem, in that order; two haems with the same
    name keep the order they were given in.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
haem_type_finder
name_simplifier
```

#### `haem_type_finder`

```text
---- Summary ----
Main function to tell the type of a haem from its name: the first letter after a
leading 'Cyt', 'cytochrome', 'haem' or 'heme', so 'Cyt bH' and 'Cyt $b_{557}$' are
b haems, 'Cyt c1' and 'Cyt cc' c haems, 'Cyt a605' and 'Cyt aa3' a haems.

---- Inputs ----
name : Any
    Haem name, plain or in figure form (converted with str).

---- Globals read ----
HAEM_NAME_PREFIXES, HAEM_TYPE_ORDER (module constants).

---- Outputs ----
str
    'a', 'b' or 'c'; 'other' for any other name (a component named PC1, a haem d
    or o, or a name that is only 'Cyt').

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `name_simplifier`

```text
---- Summary ----
Main function to simplify a name for matching by lower-casing it and removing
everything except letters and digits, so "Cyt $c_1$" equals "cyt c1".

---- Inputs ----
value : Any
    Name (converted with str).

---- Globals read ----
None.

---- Outputs ----
str
    Lower-case letters and digits only.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `program_title_builder`

```text
---- Summary ----
Main function to build the name shown at the top of the terminal, in the window
title and in the log: the program name, the git branch it was installed from (when
the folder is a git clone) and the version.

---- Inputs ----
root : Path
    Program folder.
version : str
    Version text, from program_version_reader.

---- Globals read ----
None.

---- Outputs ----
str
    For example "Portimao dev V2.7"; without a branch (a folder from a zip file)
    "Portimao V2.7".

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `program_version_reader`

```text
---- Summary ----
Main function to find the program's version. The release leaves `.style/` off
main (the user download), so where `.style/VERSION` is missing the version is
taken from the title of `QUESTION_FLOW.md`, which every release rewrites.

---- Inputs ----
root : Path
    Program folder.

---- Globals read ----
VERSION_TITLE_PATTERN (module constant).

---- Outputs ----
str
    For example "2.7"; "unknown" when neither file gives a version.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `update_note_finder`

```text
---- Summary ----
Main function to say why this copy does not update itself, to be shown beside its
version: a copy from a zip never can; a git copy says what the launcher found when
it tried. The Mac app updates itself, and says so in its own message when it
cannot.

---- Inputs ----
root : Path
    Program folder.
is_app : bool
    True when running as the Mac app.

---- Globals read ----
UPDATE_NOTE_SWITCH, ZIP_FIXES, ZIP_NOTE (module constants);
os.environ['PORTIMAO_UPDATE_NOTE']; sys.platform.

---- Outputs ----
str
    One sentence saying why, and what to do; empty when this copy updates itself
    (or was not started by the launcher, which alone tries).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/individual_experiment_exporter.py`

Export of one processed experiment to an Excel workbook.

### INDIVIDUAL EXPERIMENT EXPORTER HELPERS

#### `_frame_writer`

```text
---- Summary ----
Helper function to write a DataFrame as a formatted worksheet.

---- Inputs ----
sheets : tuple
    (open ExcelWriter, header format, set of sheet names already used).
frame : pd.DataFrame
    Data to write.
sheet_title : str
    Wanted sheet name; made unique and valid for Excel.
first_col_width : float
    Width of the first column.

---- Globals read ----
None.

---- Outputs ----
Any
    The xlsxwriter worksheet.

---- Globals mutated ----
None. Adds a sheet to the open workbook and records its name (side effect).

---- Equations ----
None.

---- Helpers ----
excel_sheet_namer
```

#### `_name_lister`

```text
---- Summary ----
Helper function to list the measurement names of one kind (vo2 or haem) over all
windows, in first-seen order.

---- Inputs ----
windows : dict
    Window name -> window record, each holding 'vo2' and 'haem' dicts.
kind : str
    'vo2' or 'haem'.

---- Globals read ----
None.

---- Outputs ----
List[str]
    Unique measurement names.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_spectral_csv_exporter`

```text
---- Summary ----
Helper function to write one CSV per spectral dataset and data type, with
wavelengths down and one column per spectrum.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
folder : Path
    Existing folder the CSV files are written to.

---- Globals read ----
SPECTRAL_CSV_TYPES (module constant).

---- Outputs ----
List[dict]
    One record per CSV file: Dataset, Data type, CSV file, Wavelengths, Timepoints.
    Raises ValueError when a spectrum length does not match the wavelengths.

---- Globals mutated ----
None. Writes CSV files into ``folder`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `averages_table_builder`

```text
---- Summary ----
Main function to build the Averages worksheet table: one row per window with the
mean, SD and change from baseline of VoO2 and of each haem.

---- Inputs ----
averages : dict
    Event-window averages, as added to the experiment by
    calculate_experiment_averages (DATA_FORMAT.md); uses averages['windows'].

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Columns Average, Kind (baseline, settled or quick), Start time (min), End time
    (min), then mean, SD and change from baseline (%) for VoO2 and each haem.

---- Globals mutated ----
None.

---- Equations ----
Change from baseline = window mean as a percentage of the average0 mean (calculated
in the averaging step).

---- Helpers ----
_name_lister
```

#### `experiment_workbook_exporter`

```text
---- Summary ----
Main function to export one experiment to <output_dir>/<name>/<name>.xlsx (or into
a folder inside that, such as the full/ of a trimmed experiment's whole recording),
with the CcO2, CsO2 and VoO2 sheets, Averages, Events and Metadata, and optionally
every processed table and the spectral CSV files.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
output_dir : Path
    Results folder.
full : bool
    True adds every processed table in the order of DATA_SHEETS.
spectra : bool
    True also writes the spectral CSV files next to the workbook (large and slow)
    and an index sheet linking to them.
subfolder : str
    Folder inside the experiment's folder to write into (FULL_FOLDER); '' for the
    experiment's folder itself.

---- Globals read ----
BASIC_SHEETS, DATA_SHEETS and schema.DELTA_HAEM_SOURCES.

---- Outputs ----
List[Path]
    Paths of the files written: the workbook first, then any CSV files.

---- Globals mutated ----
None. Creates the folder, the workbook and optional CSV files (side effect).

---- Equations ----
None.

---- Helpers ----
_frame_writer
_spectral_csv_exporter
averages_table_builder
file_name_sanitiser
```

#### `saved_settings_reader`

```text
---- Summary ----
Main function to read the OD, volume, dilution factor and events saved in the
workbook of an earlier export.

---- Inputs ----
output_dir : Path
    Results folder.
experiment_name : str
    Experiment name (file name without the extension).

---- Globals read ----
SETTINGS_KEYS (module constant).

---- Outputs ----
Optional[dict]
    {'OD', 'volume', 'dilution_factor', 'events': [{'datapoint', 'label',
    'concentration_uM', 'ignored'}]}, or None when there is no readable workbook or
    nothing was saved.

---- Globals mutated ----
None. Reads the workbook from disk.

---- Equations ----
None.

---- Helpers ----
workbook_path_builder
```

#### `size_describer`

```text
---- Summary ----
Main function to put the size of files to be written in plain words, to two
significant figures, as the export question shows it.

---- Inputs ----
size_bytes : float
    Size in bytes; 0 or less when there is nothing to write.

---- Globals read ----
None.

---- Outputs ----
str
    'about 1.2 GB', 'about 350 MB', 'under 1 MB', or 'none in these files' for 0.

---- Globals mutated ----
None.

---- Equations ----
1 GB = 10^9 bytes, 1 MB = 10^6 bytes.

---- Helpers ----
None.
```

#### `spectra_size_estimator`

```text
---- Summary ----
Main function to work out roughly how large the spectra csv files of an export
would be, from the number of spectra and wavelengths of each file (read from its
headers) and the part kept by the trimming.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md), with 'duration_min' and 'spectra_shapes'; a
    summary without 'spectra_shapes' counts as having no spectra.
limits : Dict[str, dict]
    {file name: {'trim_start', 'trim_end' (min on the recording, None for no trim),
    ...}}; a file missing is not trimmed.
bytes_per_value : Dict[str, float]
    Bytes one value takes in the csv file of each kind (config.SPECTRA_CSV_BYTES).

---- Globals read ----
None.

---- Outputs ----
Tuple[float, float]
    (bytes of the trimmed spectra of every file, bytes of the whole recording's
    spectra of the trimmed files only).

---- Globals mutated ----
None.

---- Equations ----
kept fraction = (trim end - trim start) / duration, the trim end being the duration
and the trim start 0 when not trimmed, kept within 0 to 1.
trimmed bytes = sum over files and spectrometers of
    n_spectra x kept fraction x n_wavelengths x sum(bytes_per_value).
full bytes = the same with a fraction of 1, over the trimmed files only.

---- Helpers ----
None.
```

#### `workbook_path_builder`

```text
---- Summary ----
Main function to build the path of the workbook of an experiment.

---- Inputs ----
output_dir : Path
    Results folder.
experiment_name : str
    Experiment name; made safe for file names.

---- Globals read ----
None.

---- Outputs ----
Path
    <output_dir>/<name>/<name>.xlsx.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
file_name_sanitiser
```

## `utils_shared/individual_experiment_plotter.py`

Plot of one experiment: oxygen, OCR and haem panels.

### CLASSES

#### `_HideTopTickLabels`

```text
---- Summary ----
A y-axis formatter that leaves out the tick label nearest the top edge when it would
run into the panel above. Stacked panels touch, so a label at the very top of one
panel overlaps the bottom label of the panel above it; a label is dropped if its
tick lies within 0.7 x ``font_pt`` points (the height of a digit) of the top of the
axis, whatever the panel's height.

---- Attributes ----
_font_pt : float
    Font size of the tick labels in points.

---- Globals read ----
None.

---- Methods ----
__init__
__call__
```

##### `__init__`

```text
---- Summary ----
Helper method to create the formatter.

---- Inputs ----
font_pt : float
    Font size of the tick labels in points.

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
```

##### `__call__`

```text
---- Summary ----
Helper method to format one tick label, returning an empty string for the label
nearest the top edge when it would run into the panel above.

---- Inputs ----
x : float
    Tick value.
pos : Optional[int]
    Tick position, as passed by matplotlib.

---- Globals read ----
None.

---- Outputs ----
str
    Tick label text, or an empty string for a label within 0.7 x font_pt points
    of the top of the axis.

---- Globals mutated ----
None.

---- Equations ----
A label is dropped when x >= high - (high - low) x min(0.5, 0.7 x font_pt /
axes_height_pt), where low and high are the view limits.

---- Helpers ----
None.
```

### INDIVIDUAL EXPERIMENT PLOTTER HELPERS

#### `_axes_legend_drawer`

```text
---- Summary ----
Helper function to draw a legend with an optional thin box.

---- Inputs ----
ax : Axes
    Matplotlib axes.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.
text_only : bool
    True drops the coloured line beside each entry (used for haem panels, where the
    colour already identifies the trace).
location : Optional[str]
    Legend location; None uses config["LEGEND_LOCATION"].

---- Globals read ----
config keys LEGEND_LOCATION, LEGEND_COLUMNS, LEGEND_FRAME, LEGEND_FONT_SIZE,
LEGEND_FRAME_LINE_WIDTH and LEGENDS_OUTSIDE (legend in the white space right of
the axes).

---- Outputs ----
Legend
    The legend that was drawn.

---- Globals mutated ----
None. Adds a legend to ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_first_series_getter`

```text
---- Summary ----
Helper function to get the time and values of the first measurement column of a
DataFrame.

---- Inputs ----
df : pd.DataFrame
    Time-resolved data frame (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray]
    (times, values) of the first measurement column.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
measurement_column_finder
time_getter
value_getter
```

#### `_haem_data_selector`

```text
---- Summary ----
Helper function to pick the haem data frame the haem panels plot.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys HAEM_PANELS and HAEM_PLOT_VALUES; schema.HAEM_KEYS.

---- Outputs ----
Tuple[Optional[pd.DataFrame], Optional[str]]
    (haem data frame or None, source name). None when haem panels are off or the
    source is missing from the experiment (a warning is printed).

---- Globals mutated ----
None. Shows a warning when the source is missing (side effect).

---- Equations ----
None.

---- Helpers ----
problem_shower
source_resolver
```

#### `_height_ratio_calculator`

```text
---- Summary ----
Helper function to calculate the relative panel heights from PANEL_HEIGHT_RATIOS.

---- Inputs ----
panels : List[dict]
    Panel specifications; each has a "type" of oxygen, vo2, haem or delta_psi.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys PANEL_HEIGHT_RATIOS, EQUAL_PANEL_HEIGHTS and HAEM_PANEL_WEIGHT.

---- Outputs ----
List[float]
    Relative height of each panel. The haem weight is shared equally between the
    haem panels. Raises ValueError for a missing or non-positive weight.

---- Globals mutated ----
None.

---- Equations ----
ratio = weight for oxygen, vo2 and delta psi panels; HAEM_PANEL_WEIGHT for each haem panel if
set, else weight / n_haem; 1 for every panel when EQUAL_PANEL_HEIGHTS is set.

---- Helpers ----
None.
```

#### `_min_ticks_setter`

```text
---- Summary ----
Helper function to make sure an axis has at least a given number of ticks, still at
round values.

---- Inputs ----
axis : Any
    Matplotlib axis object (ax.xaxis or ax.yaxis).
count : Optional[int]
    Minimum number of ticks; None leaves the ticks automatic.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; the major locator of the axis is replaced.

---- Globals mutated ----
None. Sets the major locator of ``axis`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_panel_builder`

```text
---- Summary ----
Helper function to list the panels to draw: oxygen, VO2, one for each configured
haem panel with matching data, then delta psi for a file that has it.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.
haem_data : Optional[pd.DataFrame]
    Haem data frame, or None.

---- Globals read ----
config keys PLOT_SET_AND_MEASURED_O2, PLOT_VO2, O2_PANEL_TITLE, VO2_PANEL_TITLE,
HAEM_PANELS, PLOT_DELTA_PSI and DELTA_PSI_AXIS_LABEL.

---- Outputs ----
List[dict]
    Panel specifications {type, title, haems}; type is oxygen, vo2, haem or
    delta_psi (the last only when PLOT_DELTA_PSI is set and the experiment has a
    delta_psi table). Raises ValueError when no panel is selected.

---- Globals mutated ----
None. Shows a warning for haems missing from the data (side effect).

---- Equations ----
None.

---- Helpers ----
measurement_column_finder
name_simplifier
warning_shower
```

#### `_vo2_ymax_calculator`

```text
---- Summary ----
Helper function to choose the top of the OCR axis so that the whole run is shown
(including the start) while a narrow spike, such as the one when dithionite is
added, does not stretch the axis.

---- Inputs ----
y : np.ndarray
    OCR values of the whole run (NaN allowed).
window_fraction : float
    Width of the rolling median as a fraction of the number of points; spikes
    narrower than half of it are removed from the envelope.
headroom : float
    Fraction of the envelope height added above the highest smoothed value.

---- Globals read ----
None.

---- Outputs ----
float
    Top of the axis; NaN when there are no finite values.

---- Globals mutated ----
None.

---- Equations ----
smooth = rolling median of y (window = window_fraction x n points, at least 5);
noise = 95th percentile of |y - smooth|;
top = max(smooth) + noise + headroom x max(smooth).

---- Helpers ----
None.
```

#### `_skipped_window_drawer`

```text
---- Summary ----
Helper function to draw an averaging window that could not be calculated: a red
band on every axis with a warning sign above it. Only used in the previews.

---- Inputs ----
axes : List[Axes]
    Axes of the experiment, top to bottom.
window_name : str
    Window name, for example 'average3'.
window : dict
    {start_time, end_time, reason} of the skipped window.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds a shaded span and a warning sign to the axes (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_window_drawer`

```text
---- Summary ----
Helper function to draw the averaging windows behind the data on every axis.

---- Inputs ----
axes : List[Axes]
    Axes of the experiment, top to bottom.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys PLOT_AVERAGING_WINDOWS, the AVERAGING_WINDOW_* appearance settings and
the QUICK_WINDOW_* colours of the quick windows.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds shaded spans and labels to the axes (side effect).

---- Equations ----
None.

---- Helpers ----
_skipped_window_drawer
_window_label_builder
```

#### `_window_label_builder`

```text
---- Summary ----
Helper function to build the text of an averaging window from
AVERAGING_WINDOW_LABEL_FORMAT.

---- Inputs ----
window_name : str
    Window name, for example 'average3'.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config key AVERAGING_WINDOW_LABEL_FORMAT ({n} is the number, {name} the window
name).

---- Outputs ----
str
    Label text; empty when the format is empty.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ylim_calculator`

```text
---- Summary ----
Helper function to calculate y limits from the data after the ignored start and
before the ignored end, plus a margin.

---- Inputs ----
times : np.ndarray
    Times in minutes.
series : List[np.ndarray]
    Value arrays on the same time axis.
ignore_minutes : float
    Minutes at the start left out of the limits.
margin : float
    Fraction of the data range added on both sides.
ignore_last_minutes : float
    Minutes at the end left out of the limits.

---- Globals read ----
None.

---- Outputs ----
Optional[Tuple[float, float]]
    (low, high), or None when no finite data remain.

---- Globals mutated ----
None.

---- Equations ----
pad = (max - min) x margin (1 if the range is 0); limits = (min - pad, max + pad).

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `experiment_drawer`

```text
---- Summary ----
Main function to draw one experiment's stacked panels into a cell of an existing
figure: the oxygen, the OCR, the haems and, for a file that has it, delta psi as
one line with gaps where it cannot be given. It adds no title, adjusts no margins and saves nothing; event labels hang
below the lowest axis, so room is needed underneath the cell.

---- Inputs ----
fig : Figure
    Matplotlib figure.
subplot_spec : SubplotSpec
    Grid cell the experiment is drawn in.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
Many config keys (panels, axes labels, colours, events, windows; see
Config.plot_config in config.py) and schema.VO2_KEYS.

---- Outputs ----
Tuple[List[Axes], List[dict]]
    (axes from top to bottom, panel specifications drawn).

---- Globals mutated ----
None. Adds axes and artists to ``fig`` (side effect).

---- Equations ----
None.

---- Helpers ----
_axes_legend_drawer
_first_series_getter
_haem_data_selector
_height_ratio_calculator
_min_ticks_setter
_panel_builder
_vo2_ymax_calculator
_window_drawer
_ylim_calculator
concentration_formatter
name_simplifier
source_resolver
time_getter
value_getter
```

#### `experiment_plotter`

```text
---- Summary ----
Main function to plot one experiment in its own figure, optionally save it as svg
and png, then show or close it.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.
export_root : Path
    Results folder.
fig : Optional[Figure]
    An existing figure to clear and draw in (the experiment browser redraws one
    window). It is left open. None makes a new figure.

---- Globals read ----
config keys FIGURE_SIZE, FIGURE_DPI, TITLE_STYLE, LAYOUT_PAD_PT, FIT_MARGINS,
TITLE_GAP_PT, SAVE_FIGURES, TIGHT_BBOX, SHOW_INDIVIDUAL_FIGURES and the title
settings.

---- Outputs ----
Tuple[Figure, List[Axes]]
    The figure (already closed unless SHOW_INDIVIDUAL_FIGURES is set or a figure was
    given) and its axes.

---- Globals mutated ----
None. Writes <export_root>/<name>/<name>.svg and .png and prints a message (side
effect).

---- Equations ----
None.

---- Helpers ----
experiment_drawer
experiment_title_builder
figure_canvas_fitter
figure_saver
watermark_style_builder
```

#### `experiment_title_builder`

```text
---- Summary ----
Main function to build the title of an experiment from the FIGURE_TITLE format.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config key FIGURE_TITLE ({experiment_name} is replaced).

---- Outputs ----
str
    Title text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `watermark_style_builder`

```text
---- Summary ----
Main function to build the text keyword arguments of the faint run-name watermark.

---- Inputs ----
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys WATERMARK_FONT_SIZE, TICK_FONT_SIZE, WATERMARK_COLOUR and
WATERMARK_ALPHA.

---- Outputs ----
dict
    Keyword arguments fontsize, color and alpha for matplotlib text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/normalisation.py`

Normalisation of OCR and haem data by OD and to a relative scale.

### NORMALISATION HELPERS

#### `_frame_normaliser`

```text
---- Summary ----
Helper function to OD-normalise the measurement columns of a data frame, leaving the
time and index columns untouched.

---- Inputs ----
df : pd.DataFrame
    Data frame with a time column and measurement columns.
**kwargs : Any
    optical_density, volume, dilution_factor and label, passed to data_normaliser.

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Scaled copy of the data frame.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
data_normaliser
measurement_column_finder
```

#### `_number_reader`

```text
---- Summary ----
Helper function to read one column as numbers, by the one rule of the scalings: an
empty cell stays empty, anything else that is not a number stops the scaling.

---- Inputs ----
column : pd.Series
    The column as it is in the table.
label : str
    Name of the experiment or data, used in the message.

---- Globals read ----
None.

---- Outputs ----
pd.Series
    The column as float64, NaN where the cell is empty. Raises ValueError, with a
    message for the user, when a cell holds something that is not a number.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `data_normaliser`

```text
---- Summary ----
Main function to divide numeric data by dilution factor x optical density x volume.

---- Inputs ----
data : Union[pd.DataFrame, pd.Series, np.ndarray]
    Numeric data to scale.
optical_density : float
    OD of the sample (> 0).
volume : float
    Volume of the sample (> 0).
dilution_factor : float
    Dilution factor (> 0).
label : str
    Name used in error messages.

---- Globals read ----
None.

---- Outputs ----
Union[pd.DataFrame, pd.Series, np.ndarray]
    Scaled data of the same kind as the input; empty cells stay empty. Raises
    ValueError, with a message for the user, if the denominator is not positive
    and finite or a cell holds something that is not a number.

---- Globals mutated ----
None.

---- Equations ----
scaled = data / (dilution_factor x optical_density x volume).

---- Helpers ----
_number_reader
```

#### `experiment_normaliser`

```text
---- Summary ----
Main function to OD-normalise VoO2 and, when present, the haem data of an
experiment.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.

---- Globals read ----
None. Calls schema.measurement_columns.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError, with a message for the user,
    if dilution_factor, OD or volume is missing from the metadata, or if VoO2 has no
    measurement columns.

---- Globals mutated ----
experiment: adds VoO2_OD and, for each of haem_conc, haem_abs and haem_delta_abs
that exists, haem_OD, haem_abs_OD and haem_delta_abs_OD.

---- Equations ----
x_OD = x / (dilution_factor x OD x volume). Dividing by a constant commutes with the
shift behind delta abs, so haem_delta_abs_OD equals the shifted haem_abs_OD.

---- Helpers ----
_frame_normaliser
measurement_column_finder
```

#### `percent_converter`

```text
---- Summary ----
Main function to scale one table of an experiment to 0-100 % and store it under a
new key.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
source_key : str
    Key of the table to scale, e.g. 'haem_conc' or 'VoO2'.
target_key : str
    Key the scaled table is stored under, e.g. 'haem_percent'.
**scaling_kwargs : Any
    exclude_first_minutes, exclude_last_minutes and window_points, passed to
    percent_scaler.

---- Globals read ----
None.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError if the source table is
    unavailable.

---- Globals mutated ----
experiment: adds experiment[target_key].

---- Equations ----
None.

---- Helpers ----
percent_scaler
```

#### `percent_scaler`

```text
---- Summary ----
Main function to scale each measurement column of a data frame to a relative 0-100 %
range.

---- Inputs ----
df : pd.DataFrame
    Data frame with a time column (minutes) and measurement columns.
window_points : int
    Number of points in a row that make a reference window (>= 1).
label : str
    Name used in error messages.
exclude_first_minutes : float
    Minutes after the first measurement that are ignored at the start.
exclude_last_minutes : float
    Minutes before the last measurement that are ignored at the end.

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Scaled copy; result.attrs["percent_scaling"] holds, per column,
    {'zero_percent_window', 'hundred_percent_window': the windows found
    (reference_level_finder), 'zero_percent_level', 'hundred_percent_level': their
    medians, 'window_seconds': the length of such a window}. A constant column
    becomes NaN. Raises ValueError, with a message for the user, for invalid
    settings, when a cell holds something that is not a number, or when fewer
    than window_points values are left after the ignored parts.

---- Globals mutated ----
None.

---- Equations ----
percent = (value - low) / (high - low) x 100, where low and high are the medians of
the lowest and of the highest points in a row (reference_level_finder). Values
outside the range are kept.

---- Helpers ----
_number_reader
measurement_column_finder
reference_level_finder
time_getter
window_seconds_calculator
```

## `utils_shared/ocr_checking.py`

Checks the instrument's oxygen consumption rate (OCR) against our own calculation from its oxygen traces.

### HELPERS

#### `_agreement_finder`

```text
---- Summary ----
Helper function to measure how closely the instrument's rate follows ours away
from the additions: the typical difference and the difference in overall size.

---- Inputs ----
instrument : np.ndarray
    The instrument's rate, one value per point of the clock (µM/min), NaN where it
    has none.
ours : np.ndarray
    Our rate on the same points (µM/min), NaN where we have none.
addition_rows : Sequence[int]
    Row of the clock of each addition (0 = first point).

---- Globals read ----
ADDITION_POINTS, MIN_COMPARED_POINTS (module constants).

---- Outputs ----
Optional[Tuple[float, float]]
    (typical difference in µM/min, difference in size in %), or None when fewer
    than MIN_COMPARED_POINTS can be compared or our rate is zero throughout.

---- Globals mutated ----
None.

---- Equations ----
Compared points: both rates have a value and the point is more than
ADDITION_POINTS away from every addition. Over them:
    typical difference = median of |instrument - ours|
    factor = sum(instrument x ours) / sum(ours^2) (least squares through zero)
    difference in size = |factor - 1| x 100 %.

---- Helpers ----
None.
```

#### `_leak_finder`

```text
---- Summary ----
Helper function to work out the oxygen leaking into the chamber through its wall.

---- Inputs ----
outside_mmHg : np.ndarray
    Oxygen pressure outside the chamber wall (PtO2, mmHg), one value per point.
chamber_mmHg : np.ndarray
    Oxygen pressure in the chamber (PcO2, mmHg), on the same points.
permeability : float
    Oxygen permeability of the chamber wall (µM/min/mmHg), as stored in the file.

---- Globals read ----
LEAK_POINTS (module constant).

---- Outputs ----
np.ndarray
    Leak (µM/min), one value per point; NaN for the first LEAK_POINTS - 1 points.

---- Globals mutated ----
None.

---- Equations ----
leak[j] = permeability x mean of (PtO2 - PcO2)[j - 39 ... j] (40 points, 20 s at
0.5 s, ending at the point itself).

---- Helpers ----
None.
```

#### `_oxygen_fall_finder`

```text
---- Summary ----
Helper function to work out how fast the measured oxygen falls at each point.

---- Inputs ----
oxygen_uM : np.ndarray
    Measured oxygen (CcO2, µM), one value per point of the clock.
step_s : float
    Time between two points (s).

---- Globals read ----
FALL_POINTS, SECONDS_PER_MINUTE (module constants).

---- Outputs ----
np.ndarray
    Fall (µM/min, positive when the oxygen goes down), one value per point; NaN for
    the first and last FALL_POINTS // 2 points.

---- Globals mutated ----
None.

---- Equations ----
The slope of the least-squares straight line through the 29 points centred on
point j:
    fall[j] = -60 x sum(k x CcO2[j + k]) / (step_s x sum(k^2)), k = -14 ... 14,
    sum(k^2) = 2030.

---- Helpers ----
None.
```

#### `_pressure_factor_finder`

```text
---- Summary ----
Helper function to find the fixed factor between the measured oxygen and the
chamber oxygen pressure, and how far the pressure strays from it.

---- Inputs ----
oxygen_uM : np.ndarray
    Measured oxygen (CcO2, µM), one value per point.
chamber_mmHg : np.ndarray
    Oxygen pressure in the chamber (PcO2, mmHg), on the same points.

---- Globals read ----
MIN_COMPARED_POINTS (module constant).

---- Outputs ----
Tuple[Optional[float], Optional[float]]
    (factor in mmHg/µM, largest |PcO2 - factor x CcO2| in mmHg), or (None, None)
    when fewer than MIN_COMPARED_POINTS points have both values or the oxygen is
    zero throughout.

---- Globals mutated ----
None.

---- Equations ----
factor = sum(CcO2 x PcO2) / sum(CcO2^2) (least squares through zero).

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `ocr_calculator`

```text
---- Summary ----
Main function to work out our own OCR from the instrument's oxygen traces.

---- Inputs ----
traces : Mapping[str, np.ndarray]
    At least 'CcO2' (µM), 'PcO2' and 'PtO2' (mmHg), one value per point of the
    clock, NaN where the file has none.
permeability : float
    Oxygen permeability of the chamber wall (µM/min/mmHg), as stored in the file.
step_s : float
    Time between two points (s).

---- Globals read ----
None.

---- Outputs ----
Dict[str, np.ndarray]
    {'fall': fall of the measured oxygen, 'leak': oxygen leaking in, 'ocr': their
    sum}, each in µM/min with one value per point, NaN where it cannot be worked
    out.

---- Globals mutated ----
None.

---- Equations ----
our OCR = fall + leak (see _oxygen_fall_finder and _leak_finder; written out in
DATA_FORMAT.md, "Our OCR check").

---- Helpers ----
_leak_finder
_oxygen_fall_finder
```

#### `ocr_check_describer`

```text
---- Summary ----
Main function to say in plain words what the OCR check of one file found.

---- Inputs ----
check : dict
    Result of ocr_checker (ocr_check in DATA_FORMAT.md).
file_name : str
    Name of the file, written first.

---- Globals read ----
PART_LABELS (module constant).

---- Outputs ----
str
    An empty string when the instrument's OCR agrees with ours; otherwise one
    sentence saying which parts disagree, or why the file could not be checked.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `ocr_checker`

```text
---- Summary ----
Main function to check that the instrument worked out its OCR as we expect, from
its own oxygen traces.

---- Inputs ----
traces : Mapping[str, Optional[np.ndarray]]
    The traces of OCR_TRACES, one value per point of the clock (NaN where the file
    has none); a trace the file lacks is None or left out.
permeability : Optional[float]
    Oxygen permeability of the chamber wall (µM/min/mmHg) from the file, or None
    when the file does not store it.
addition_rows : Sequence[int]
    Row of the clock of each addition (0 = first point).
step_s : float
    Time between two points (s).

---- Globals read ----
MARGINS, OCR_TRACES (module constants).

---- Outputs ----
dict
    ocr_check (DATA_FORMAT.md): 'is_checked', 'is_agreeing', 'reason' (why it was
    not checked, else empty), 'permeability', 'pressure_factor' and 'parts' (for
    each key of MARGINS: 'difference', 'margin', 'unit' and 'is_agreeing').

---- Globals mutated ----
None.

---- Equations ----
sum: largest |VoO2 - (VrO2 + DgO2)|.
pressure: largest |PcO2 - factor x CcO2|.
fall and leak: the typical difference, and the difference in size (%), of the
instrument's VrO2 and DgO2 from ours, away from the additions (_agreement_finder).
Each part agrees when its difference is at most its margin.

---- Helpers ----
_agreement_finder
_pressure_factor_finder
ocr_calculator
```

## `utils_shared/output_capture.py`

Per-thread capture of printed output, kept out of the terminal and the log file.

### CLASSES

#### `CapturedOutput`

```text
---- Summary ----
The text a thread printed while its output was captured, with the warnings among
it also kept apart (user_notices.warning_shower), so the window can show them
without picking them out by their words.

---- Attributes ----
warnings : List[str]
    Each warning shown during the capture, without its indent, in order.

---- Globals read ----
None.

---- Methods ----
__init__
```

##### `__init__`

```text
---- Summary ----
Method to start an empty capture with no warnings.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the warnings attribute on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `captured_buffer_getter`

```text
---- Summary ----
Main function to give the buffer that the current thread's output is being captured
in, if any. Output streams that support the capture check this before they write.

---- Inputs ----
None.

---- Globals read ----
_local (module state).

---- Outputs ----
Optional[CapturedOutput]
    The buffer of the current thread, or None when its output is not captured.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `output_capturer`

```text
---- Summary ----
Main function to capture everything the current thread prints, while other threads
keep printing normally. Only output streams that check captured_buffer_getter honour
it (the experiment browser window and the log copier do).

---- Inputs ----
None.

---- Globals read ----
_local (module state).

---- Outputs ----
Iterator[CapturedOutput]
    The buffer the output is collected in; read it with getvalue(), and its
    warnings with .warnings.

---- Globals mutated ----
None. Sets and clears the capture of the current thread (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/paf_reader.py`

Direct reader of Espana Scientific Software .paf files.

### CLASSES

#### `PafError`

```text
---- Summary ----
Raised when the file cannot be opened, is not a .paf, is cut short, has a layout
this reader does not know or lacks what the program needs. The message starts with
the file name and says in plain words what is wrong and what to do, so it can be
shown to the user as it is.

---- Attributes ----
None.

---- Globals read ----
None.

---- Methods ----
None.
```

#### `Spectra`

```text
---- Summary ----
One parsed 'Spectra: CCD' record (one spectrometer) of a .paf file.
Detailed structure can be found in DATA_FORMAT.md.
```

#### `PafFile`

```text
---- Summary ----
An open .paf file (memory-mapped, so a 100 MB file is not read into RAM). Use ``with
PafFile(path) as paf:``. Everything handed out by the methods is a copy, so it stays
valid after the file is closed.

---- Attributes ----
path : Path
    Path to the .paf file.
records : List[dict]
    Record table from record_scanner (see DATA_FORMAT.md).
spectra : List[Spectra]
    Parsed spectrometer records.
time_s : np.ndarray
    Time of every frame in seconds, shape (n_frames,).

---- Globals read ----
None.

---- Methods ----
__init__
__enter__
__exit__
acquisition_reader
closer
dataset_name_lister
duration_finder
events_reader
frame_counter
missing_trace_describer
notes_reader
ocr_settings_reader
ocr_trace_checker
spectra_dataset_reader
stream_name_lister
stream_reader
stream_unit_reader
```

##### `__init__`

```text
---- Summary ----
Main method to open a .paf file, memory-map it, scan its records and find the
time base and the traces that cover it.

---- Inputs ----
path : Union[str, Path]
    Path to the .paf file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Sets path, records, spectra, time_s (seconds) and the private
    stream tables. Raises PafError, starting with the file name and saying in
    plain words what is wrong and what to do, for a file that cannot be opened,
    is too small, has no Time stream or has a layout this reader does not know.

---- Globals mutated ----
None. Opens the file and the memory map (side effect); closes them again if
reading fails.

---- Equations ----
None.

---- Helpers ----
closer
record_scanner
stream_extractor
```

##### `__enter__`

```text
---- Summary ----
Main method to support `with PafFile(path) as paf:`.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
PafFile
    The open file itself.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__exit__`

```text
---- Summary ----
Main method to close the file when the `with` block ends.

---- Inputs ----
*exc : Any
    Exception information passed by Python (ignored).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. The exception, if any, is not suppressed.

---- Globals mutated ----
None. Closes the file (side effect).

---- Equations ----
None.

---- Helpers ----
closer
```

##### `acquisition_reader`

```text
---- Summary ----
Main method to summarise the acquisition settings of every spectrometer.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    One dictionary per spectrometer: dataset, spectrometer, frames, wavelengths,
    wavelength_range_nm and the parameters read from the file.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
dataset_namer
```

##### `closer`

```text
---- Summary ----
Main method to release the memory map and the file handle and clear the parsed
tables.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Anything handed out earlier stays valid because it is a copy.

---- Globals mutated ----
None. Resets the records, spectra and stream tables of the instance and closes
the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `dataset_name_lister`

```text
---- Summary ----
Main method to list the spectral datasets in the file.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[str]
    Dataset names in file order.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
dataset_namer
```

##### `duration_finder`

```text
---- Summary ----
Main property to give the length of the recording in minutes.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
float
    Largest time value, in minutes.

---- Globals mutated ----
None.

---- Equations ----
duration (min) = max(time_s) / 60.

---- Helpers ----
None.
```

##### `events_reader`

```text
---- Summary ----
Main method to read the text events (additions) stored in the file.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    [{'name', 'text', 'datapoint'}] sorted by datapoint; datapoint is the
    1-based spectrum number stored with the event. Events with no stored
    position are ignored with a warning.

---- Globals mutated ----
None. Prints warnings (side effect).

---- Equations ----
None.

---- Helpers ----
_event_lister
u32_reader
```

##### `frame_counter`

```text
---- Summary ----
Main property to give the number of time points (frames) in the recording.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
int
    Length of the time base.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `missing_trace_describer`

```text
---- Summary ----
Main method to say in plain words why one trace the program uses cannot be
given.

---- Inputs ----
name : str
    Trace name, a key of TRACE_LABELS ('CsO2', 'CcO2' or 'VoO2').

---- Globals read ----
TRACE_LABELS (module constant).

---- Outputs ----
str
    For example 'run1.paf: the file has no OCR (VoO2) trace', or 'run1.paf: the
    OCR (VoO2) trace cannot be read, because ...' with the reason noted when
    the trace was skipped. No full stop at the end.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `notes_reader`

```text
---- Summary ----
Main method to read the experiment notes (PaneNote record) as plain text.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
str
    Notes text, or an empty string if there are none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
rtf_converter
```

##### `ocr_settings_reader`

```text
---- Summary ----
Main method to read how the instrument works out its oxygen rates (the
VoO2Math record).

---- Inputs ----
None.

---- Globals read ----
FALL_EDGE_OFFSET, LEAK_START_OFFSET, OCR_SETTINGS_BYTES, OCR_SETTINGS_RECORD,
OCR_SETTINGS_START, PERMEABILITY_OFFSET, PERMEABILITY_RANGE, POINTS_RANGE,
LAYOUT_ERRORS (module constants).

---- Outputs ----
Optional[dict]
    ocr_settings (DATA_FORMAT.md): 'permeability' (µM/min/mmHg),
    'fall_edge_points' and 'leak_start_points'; None when the file has no such
    record or it is not laid out as expected.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
token_reader
u32_reader
```

##### `ocr_trace_checker`

```text
---- Summary ----
Main method to refuse a file whose OCR trace (VoO2) cannot be given, as nothing
can be processed without it.

---- Inputs ----
None.

---- Globals read ----
SEND_FILE_ADVICE (module constant).

---- Outputs ----
None
    Nothing. Raises PafError saying why the trace is missing and what to do.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
missing_trace_describer
```

##### `spectra_dataset_reader`

```text
---- Summary ----
Main method to read one spectrometer as the dictionary used by the rest of the
program.

---- Inputs ----
name : str
    Dataset name from dataset_name_lister, e.g. 'Cyt'.
with_intensity : bool
    True to also return the integer counts.
chunk : int
    Number of spectra converted at a time (limits memory use).

---- Globals read ----
None.

---- Outputs ----
dict
    {'wavelengths' (nm, n_wavelengths), 'spectrum_indices' (n_spectra), 'time'
    (min, n_spectra), 'transmission' (n_spectra x n_wavelengths; NaN where it
    cannot be worked out)[, 'intensity']}; float64 copies. Raises PafError for
    an unknown dataset or one with more spectra than time points.

---- Globals mutated ----
None. Prints a warning when there are fewer spectra than time points or when
the transmission is empty at some wavelengths (side effect).

---- Equations ----
intensity = round(10^log), log being the stored log10 row. The transmission is
given under _transmission_converter.

---- Helpers ----
_spectrum_time_finder
_transmission_converter
dataset_name_lister
dataset_namer
warning_printer
```

##### `stream_name_lister`

```text
---- Summary ----
Main method to list the traces that cover the whole recording.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[str]
    Trace names, e.g. 'CsO2', 'CcO2', 'VoO2'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `stream_reader`

```text
---- Summary ----
Main method to read one trace on the common time base.

---- Inputs ----
name : str
    Trace name, e.g. 'VoO2'.
is_quiet : bool
    True to read the trace without the warning about a short trace, when it is
    given elsewhere.

---- Globals read ----
RATE_TRACES (module constant).

---- Outputs ----
Optional[np.ndarray]
    float64 array with one value per time point (NaN where the software has no
    value, e.g. the start of VoO2, and at the end of a trace that is shorter
    than the clock), or None if the trace does not exist.

---- Globals mutated ----
None. Prints a warning when the trace is short (see _short_trace_describer)
(side effect).

---- Equations ----
None.

---- Helpers ----
_short_trace_describer
ocr_settings_reader
warning_printer
```

##### `stream_unit_reader`

```text
---- Summary ----
Main method to give the unit the file stores for one trace.

---- Inputs ----
name : str
    Trace name, e.g. 'CcO2'.

---- Globals read ----
None.

---- Outputs ----
str
    The unit as written in the file (for example 'µM'), or an empty string when
    the trace does not exist or has no unit.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### READER HELPERS

#### `_event_lister`

```text
---- Summary ----
Helper function to turn the stored copies of the text events (additions) into one
entry per addition.

---- Inputs ----
found : Sequence[Tuple[str, str, int]]
    One (name, text, position) per 'Text Event' record, in file order: the name the
    software gives the event ('Event 1'), the text the user typed and the 1-based
    spectrum number (0 in the template copy of an event).
file_name : str
    File name, for the warnings.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    [{'name', 'text', 'datapoint'}] sorted by datapoint. A name stored at several
    different positions gives one entry per position, each with the text stored
    beside it. Names with no stored position are left out with a warning.

---- Globals mutated ----
None. Prints warnings (side effect).

---- Equations ----
None.

---- Helpers ----
warning_printer
```

#### `_event_time_adder`

```text
---- Summary ----
Helper function to give every addition its time, and to leave out the additions
stored outside the recording. The quick look and the full reading both use it, so
they always give the same additions.

---- Inputs ----
events : Sequence[dict]
    Additions from events_reader, each with 'datapoint' (1-based spectrum number)
    and 'text'.
time_min : np.ndarray
    Clock of the recording in minutes, shape (n_timepoints,).
file_name : str
    File name, for the warning.
is_quiet : bool
    True to leave an addition out without the warning, when the user was already
    told about it by the quick look.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    The additions inside the recording, in the order given, each with 'time' (min)
    and 'row_index' (0-based row of the clock) added.

---- Globals mutated ----
None. Prints a warning for each addition left out (side effect).

---- Equations ----
row_index = datapoint - 1; time = time_min[row_index].

---- Helpers ----
warning_printer
```

#### `_short_trace_describer`

```text
---- Summary ----
Helper function to say whether a trace shorter than the clock is worth a warning,
and in what words.

---- Inputs ----
name : str
    Trace name, e.g. 'VoO2'.
n_missing : int
    Points of the clock the trace has no value for at the end.
n_clock : int
    Points of the clock.
step_s : float
    Time between two points (s).
n_expected : int
    Points the instrument always leaves empty at the end of this trace (the fall
    edge of VoO2Math for the oxygen rates, else 0).

---- Globals read ----
SHORT_TRACE_FRACTION (module constant).

---- Outputs ----
str
    The warning, without the file name; empty when the trace is short by no more
    than n_expected points or by no more than SHORT_TRACE_FRACTION of the clock.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_spectrum_time_finder`

```text
---- Summary ----
Helper function to give the time of every spectrum of one spectrometer.

---- Inputs ----
time_s : np.ndarray
    Clock of the recording in seconds, shape (n_timepoints,).
n_spectra : int
    Number of spectra of the spectrometer; the file numbers them 1 to n_spectra.
dataset : str
    Dataset name, for the messages.
file_name : str
    File name, for the messages.

---- Globals read ----
SEND_FILE_ADVICE (module constant).

---- Outputs ----
np.ndarray
    Times in minutes, shape (n_spectra,). Raises PafError when there are more
    spectra than time points, as the last spectra then have no time.

---- Globals mutated ----
None. Prints a warning when there are fewer spectra than time points (side
effect).

---- Equations ----
time of spectrum i (min) = time_s[i - 1] / 60, for i = 1 to n_spectra.

---- Helpers ----
warning_printer
```

#### `_trace_title_maker`

```text
---- Summary ----
Helper function to write the column title of one trace, with the unit the file
stores for it.

---- Inputs ----
key : str
    Trace name, a key of TRACE_COLUMNS ('CsO2', 'CcO2' or 'VoO2').
unit : str
    Unit as written in the file; may be empty.

---- Globals read ----
TRACE_COLUMNS, UNIT_IN_TITLE, FALLBACK_UNIT (module constants).

---- Outputs ----
str
    For example 'Measured O2 (µM)'; with FALLBACK_UNIT when the file has no unit,
    and without a unit for the traces not in UNIT_IN_TITLE ('VoO2').

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_unit_cleaner
```

#### `_transmission_converter`

```text
---- Summary ----
Helper function to work out the transmission of a block of spectra from the stored
logarithms.

---- Inputs ----
log_counts : np.ndarray
    Stored log10 of the counts, shape (n_spectra, n_wavelengths), float64.
log_reference : np.ndarray
    Stored log10 of the reference spectrum, shape (n_wavelengths,), float64.

---- Globals read ----
LN10 (module constant).

---- Outputs ----
np.ndarray
    Transmission, shape (n_spectra, n_wavelengths), float64. NaN where it is not a
    finite number, as where the reference has zero counts (its logarithm is then
    not finite).

---- Globals mutated ----
None.

---- Equations ----
transmission = 10^(log - log_ref) = exp((log - log_ref) ln 10).

---- Helpers ----
None.
```

#### `_unit_cleaner`

```text
---- Summary ----
Helper function to write a unit from the file in one way, so that two spellings of
the same unit compare equal.

---- Inputs ----
unit : str
    Unit as written in the file.

---- Globals read ----
None.

---- Outputs ----
str
    The unit without spaces around it and with the Greek letter mu (U+03BC)
    replaced by the micro sign (U+00B5).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `dataset_namer`

```text
---- Summary ----
Main function to turn a spectrometer name in the file into the dataset name used by
the rest of the program.

---- Inputs ----
spectra_name : str
    Spectrometer name as stored in the file, e.g. 'Cytochromes'.

---- Globals read ----
DATASET_ALIAS (module constant).

---- Outputs ----
str
    Alias from DATASET_ALIAS (e.g. 'Cyt'), otherwise the name with non-word
    characters replaced by underscores.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `experiment_paf_loader`

```text
---- Summary ----
Main function to build the experiment dictionary straight from a .paf file.

---- Inputs ----
path : Union[str, Path]
    Path to the .paf file.
spectral_datasets : Optional[Sequence[str]]
    Spectrometers to read (None = all, () = none). Spectra are the memory-heavy
    part, so read only what is needed.
with_intensity : bool
    True to also read the integer counts of each spectrum.

---- Globals read ----
TRACE_COLUMNS, TRACE_UNITS (module constants), schema.TIME_COLUMN.

---- Outputs ----
dict
    Experiment dictionary (DATA_FORMAT.md) with CsO2, CcO2 and VoO2 data frames,
    raw_spectra and metadata (paf_file, events, acquisition, notes). Raises PafError
    if the VoO2 trace is missing.

---- Globals mutated ----
None. Prints warnings for missing traces and for units the figures do not expect
(side effect). An addition outside the recording is left out without a warning, as
experiment_summary_reader gives it at the start.

---- Equations ----
None.

---- Helpers ----
_event_time_adder
_trace_title_maker
_unit_cleaner
acquisition_reader
dataset_name_lister
events_reader
missing_trace_describer
notes_reader
ocr_trace_checker
spectra_dataset_reader
stream_reader
stream_unit_reader
warning_printer
```

#### `experiment_summary_reader`

```text
---- Summary ----
Main function to take a quick look at a .paf file without reading its spectra.

---- Inputs ----
path : Union[str, Path]
    Path to the .paf file.

---- Globals read ----
None.

---- Outputs ----
dict
    {'name' (file stem), 'duration_min', 'frames', 'datasets', 'spectra_shapes'
    ({dataset: [number of spectra, number of wavelengths]}, from the headers),
    'events' (the additions inside the recording, each with 'time' in minutes),
    'traces', 'ocr_check' (ocr_check in DATA_FORMAT.md)}. Raises PafError if the
    VoO2 trace is missing, so a file that cannot be processed is refused before any
    question is asked about it.

---- Globals mutated ----
None. Prints a warning for each addition outside the recording, and one when the
instrument's OCR does not agree with ours or cannot be checked (side effect).

---- Equations ----
None.

---- Helpers ----
_event_time_adder
acquisition_reader
dataset_name_lister
duration_finder
events_reader
frame_counter
ocr_check_describer
ocr_checker
ocr_settings_reader
ocr_trace_checker
stream_name_lister
stream_reader
warning_printer
```

#### `record_scanner`

```text
---- Summary ----
Main function to split the whole file into records and parse the spectra records.

---- Inputs ----
mm : mmap.mmap
    Read-only memory map of the .paf file.
file_name : str
    File name, for the warnings.

---- Globals read ----
MARK, NOT_A_PAF (module constants).

---- Outputs ----
Tuple[List[dict], List[Spectra]]
    (records, spectra). Each record is {off, end, type, tokens}; spectra holds one
    parsed Spectra per spectrometer. Raises PafError if the file does not start with
    an Espana record.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
spectra_parser
token_reader
```

#### `rtf_converter`

```text
---- Summary ----
Main function to convert the rich text of a PaneNote record to plain text.

---- Inputs ----
rtf : bytes
    RTF bytes (cp1252).

---- Globals read ----
None.

---- Outputs ----
str
    Plain text with one line per paragraph, trailing spaces removed and a final
    newline.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `spectra_parser`

```text
---- Summary ----
Main function to parse one 'Spectra: CCD' record: frame count, wavelength axis,
log10 data block and acquisition parameters.

---- Inputs ----
mm : mmap.mmap
    Read-only memory map of the .paf file.
off : int
    Byte offset of the record marker.
markers : List[int]
    Byte offsets of every record marker in the file, ascending.
file_name : str
    File name, for the warnings.

---- Globals read ----
COPY_AGAIN_ADVICE, SEND_FILE_ADVICE (module constants). Calls the Spectra class,
token_reader, u32_reader and warning_printer.

---- Outputs ----
Spectra
    Object with offset, name, nframes, npix, wl_off, wavelengths, data_off,
    data_end, log (nrows x npix float32 view), rec_end, params and checks
    attributes. Raises PafError, in plain words and without the file name, if the
    layout is not recognised, implausible or cut short.

---- Globals mutated ----
None. Prints a warning for unexpected trailing bytes and for a first stored row
that is not all zeros (side effect).

---- Equations ----
None.

---- Helpers ----
token_reader
u32_reader
warning_printer
```

#### `stream_extractor`

```text
---- Summary ----
Main function to extract every trace (DataItem followed by Measurement record) as a
float32 array, and to note why each trace it cannot read was skipped.

---- Inputs ----
mm : Union[bytes, mmap.mmap]
    Read-only memory map of the .paf file (or its bytes).
recs : List[dict]
    Records from record_scanner, in file order.
file_name : str
    File name, for the warning.

---- Globals read ----
TRACE_COLUMNS (module constant).

---- Outputs ----
Tuple[List[dict], dict]
    (traces, skipped). traces has one {name, n, offset, values, quantity, unit}
    dictionary per trace. skipped is {name: reason} for the traces with disagreeing
    lengths, no values or a record that is too short; the reason is in plain words
    and completes "the trace cannot be read, because ...". A file holds many traces
    the program does not use, so nothing is printed here: the caller reports the
    skipped traces it needs.

---- Globals mutated ----
None. Prints a warning when a trace the program uses ends in an unexpected way
(side effect).

---- Equations ----
None.

---- Helpers ----
token_reader
u32_reader
warning_printer
```

#### `token_reader`

```text
---- Summary ----
Main function to find the length-prefixed UTF-16LE strings inside a byte range of
the file.

---- Inputs ----
buf : Union[bytes, mmap.mmap]
    Buffer to search.
start : int
    First byte offset of the range.
end : int
    Offset one past the last byte of the range.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, int, int]]
    One (text, start offset, end offset) tuple per string found, in file order.
    Empty strings and strings with control characters are skipped.

---- Globals mutated ----
None.

---- Equations ----
A string is stored as 02 00 00 00, n (uint32), then n UTF-16LE characters (2n
bytes).

---- Helpers ----
u32_reader
```

#### `u32_reader`

```text
---- Summary ----
Main function to read one little-endian unsigned 32-bit integer from a buffer.

---- Inputs ----
buf : Union[bytes, mmap.mmap]
    Buffer to read from.
off : int
    Byte offset of the integer.

---- Globals read ----
None.

---- Outputs ----
int
    The integer value.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `warning_printer`

```text
---- Summary ----
Main function to show a reader warning, in the terminal and, while a preview is
drawn, under the plot.

---- Inputs ----
msg : str
    Warning text, without the "WARNING" prefix.
file_name : str
    File the warning is about, written in front of the text; empty when the text
    already names it.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Shows the warning (side effect).

---- Equations ----
None.

---- Helpers ----
warning_shower
```

## `utils_shared/pca_fitter.py`

Principal component analysis of the spectra of several experiments, to build a fit.

### PCA FITTER HELPERS

#### `_component_orienter`

```text
---- Summary ----
Helper function to give each component the same convention as the fit files: its
largest peak positive and equal to 1.

---- Inputs ----
vectors : np.ndarray
    Components as columns, shape (n_wavelengths, n_components).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The components, each divided by its largest absolute value and with the sign
    that makes that value positive.

---- Globals mutated ----
None.

---- Equations ----
e = v x sign(v[i]) / |v[i]|, with i the position of the largest |v|.

---- Helpers ----
None.
```

#### `_nuisance_basis_builder`

```text
---- Summary ----
Helper function to build the offset and scatter terms (one of the scatter
backgrounds of the haem decomposition) as an orthonormal basis, so they can be
taken out of the spectra before the components are searched for.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the spectra (nm).
degree_of_scatter : int
    Number of 1/wavelength^k scatter terms.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Orthonormal columns spanning the constant and the scatter terms, shape
    (n_wavelengths, degree_of_scatter + 1).

---- Globals mutated ----
None.

---- Equations ----
The columns of scatter_background_builder (the haem decomposition's scatter
backgrounds), orthonormalised by QR.

---- Helpers ----
scatter_background_builder
```

#### `_peak_finder`

```text
---- Summary ----
Helper function to find the clear peaks and troughs of a component, ignoring the
small bumps that noise makes.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths (nm), ascending and evenly spaced, shape (n_wavelengths).
values : np.ndarray
    The component, shape (n_wavelengths).

---- Globals read ----
PEAK_SHARE, PROMINENCE_SHARE, SMOOTHING_NM (module constants).

---- Outputs ----
List[float]
    Wavelength of each peak or trough (nm), in order.

---- Globals mutated ----
None.

---- Equations ----
s = running mean of the component over SMOOTHING_NM; a peak is a local maximum of
|s| that is at least PEAK_SHARE x max|s| high and rises at least PROMINENCE_SHARE x
max|s| above the higher of the lowest points between it and the next higher point
on either side (its prominence).

---- Helpers ----
None.
```

#### `_spectra_gridder`

```text
---- Summary ----
Helper function to put the spectra of one file on the common wavelength grid.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the file (nm), ascending.
spectra : np.ndarray
    Spectra of the file, shape (n_spectra, n_wavelengths).
grid : np.ndarray
    The wavelengths to give the spectra at (nm).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Spectra on the grid, shape (n_spectra, len(grid)). Spectra already on the grid
    are returned as they are.

---- Globals mutated ----
None.

---- Equations ----
Linear interpolation of each spectrum at the grid wavelengths.

---- Helpers ----
None.
```

#### `_varimax_rotator`

```text
---- Summary ----
Helper function to find the rotation that makes the components as simple as
possible (each concentrated on a few wavelengths), which makes them look more like
single haem spectra than the plain principal components do.

---- Inputs ----
loadings : np.ndarray
    Components as columns, shape (n_wavelengths, n_components).
max_iterations : int
    Most iterations to run.
tolerance : float
    The iteration stops when the criterion improves by less than this fraction.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Orthogonal rotation matrix, shape (n_components, n_components).

---- Globals mutated ----
None.

---- Equations ----
Varimax: maximise the variance of the squared loadings of every component. Each
step is R = U V^T from the SVD of L^T (Lr^3 - Lr diag(sum Lr^2) / p), Lr = L R.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `component_builder`

```text
---- Summary ----
Main function to take the first components of an analysis, optionally rotate them
to simpler shapes and smooth away their noise, and give them the conventions of the
fit files.

---- Inputs ----
analysis : dict
    Result of component_finder.
count : int
    Number of components to keep.
rotate : bool
    True to apply the varimax rotation (the components then span the same space and
    leave the same residual, but are more peak-like).
smoothing_nm : float
    Width (nm) of the Savitzky-Golay smoothing of each component; 0 (or a width
    under three wavelength steps) leaves them as found.

---- Globals read ----
SMOOTHING_ORDER (module constant).

---- Outputs ----
dict
    {'wavelengths', 'components' (columns, largest peak = +1), 'explained' (fraction
    of the variance of each component), 'residual_rms' (OD left unexplained),
    'peaks' (wavelength of each peak), 'count', 'rotated', 'smoothing_nm' (the
    width used, 0 for none)}. Components are ordered by the variance they explain;
    'explained' and 'residual_rms' are those of the components before smoothing.
    Raises ValueError for an impossible count or a negative smoothing width.

---- Globals mutated ----
None.

---- Equations ----
residual RMS = sqrt((total variance - variance of the kept components) / number of
values). Smoothing fits a polynomial of order SMOOTHING_ORDER over a window of
smoothing_nm (an odd number of points) around every wavelength.

---- Helpers ----
_component_orienter
_varimax_rotator
```

#### `component_classifier`

```text
---- Summary ----
Main function to say which haem type each component looks like, from where its
peaks are: a-like (alpha band near 605 nm, Soret near 445 nm), b-like (near 563 and
430 nm) or c-like (near 551 and 418 nm). This is a guide for the colours and names,
not an identification.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the components (nm), ascending, shape (n_wavelengths).
components : np.ndarray
    Components as columns, shape (n_wavelengths, n_components), each with its
    largest peak equal to +1 (component_builder).

---- Globals read ----
HAEM_BANDS, PEAK_SHARE (module constants).

---- Outputs ----
List[str]
    Type of each component: 'a', 'b' or 'c' when all its peaks inside known bands
    belong to that type, 'mixed' when they belong to more than one type, 'unknown'
    when none falls in a known band.

---- Globals mutated ----
None.

---- Equations ----
Peaks as in _peak_finder; troughs count as peaks, so a component that raises one
haem and lowers another is mixed.

---- Helpers ----
_peak_finder
```

#### `component_count_suggester`

```text
---- Summary ----
Main function to suggest how many components to use. This is a rule of thumb, not a
proof: it looks for the biggest drop between neighbouring principal components
(where the signal ends and the noise starts) and, when there is no clear drop,
takes enough components to explain nearly all of the variance.

---- Inputs ----
analysis : dict
    Result of component_finder.

---- Globals read ----
ENOUGH_VARIANCE, MINIMUM_RATIO (module constants).

---- Outputs ----
int
    Suggested number of components, at least 2 when two or more are available.

---- Globals mutated ----
None.

---- Equations ----
Singular value s_j = sqrt(eigenvalue j). Suggested k = the k from 2 to K-1 with the
largest s_k / s_(k+1), if that ratio is at least 2; otherwise the smallest k with
cumulative variance >= 99%.

---- Helpers ----
None.
```

#### `component_finder`

```text
---- Summary ----
Main function to run a principal component analysis on the spectra of all the files
together, inside a spectral window. The offset and scatter terms that the haem
decomposition fits as well are removed from every spectrum first, and each file's
average spectrum is removed, so the components describe how the spectra change and
differences between preparations do not become components.

---- Inputs ----
spectra_sets : List[dict]
    One entry per file: {'name', 'wavelengths' (nm), 'spectra' (n_spectra x
    n_wavelengths, the same attenuation the decomposition uses)}; only the part
    kept after trimming and ignoring.
window : Tuple[float, float]
    (start, end) wavelength of the analysis, in nm.
max_components : int
    Most components worked out.
degree_of_scatter : int
    Number of scatter terms (the same as the haem decomposition uses).

---- Globals read ----
None.

---- Outputs ----
dict
    {'wavelengths', 'eigenvectors' (columns, orthonormal), 'eigenvalues',
    'gram', 'total_variance', 'n_values', 'n_spectra', 'counts' ({file name: number
    of spectra used}), 'window', 'degree_of_scatter'}. Raises ValueError when the
    window or the data cannot be analysed.

---- Globals mutated ----
None.

---- Equations ----
X = spectra with the nuisance terms projected out and the file mean removed;
G = sum over files of X^T X; the components are the eigenvectors of G.

---- Helpers ----
_nuisance_basis_builder
_spectra_gridder
```

#### `decomposition_example_finder`

```text
---- Summary ----
Main function to decompose every spectrum with the components found, exactly as the
haem decomposition will (components plus offset and scatter, least squares), and
return the spectra that are described best and worst, to show what the components
leave unexplained.

---- Inputs ----
spectra_sets : List[dict]
    As for component_finder, optionally with 'times' (min, one per spectrum).
result : dict
    Result of component_builder.
degree_of_scatter : int
    Number of scatter terms (the same as the haem decomposition uses).

---- Globals read ----
None.

---- Outputs ----
dict
    {'wavelengths', 'best', 'worst', 'median_rms' (OD), 'n_spectra'}. 'best' and
    'worst' are the spectra with the smallest and largest residual RMS, each
    {'name', 'time_min' (NaN when unknown), 'spectrum', 'contributions'
    (n_wavelengths x n_components: coefficient x component), 'background' (offset
    and scatter), 'fitted', 'residual', 'rms' (OD)}. Raises ValueError when no
    spectrum can be decomposed.

---- Globals mutated ----
None.

---- Equations ----
B = [components, offset and scatter terms]; c = the least-squares amounts of B in
each spectrum a (basis_solver, the solver of the haem decomposition); fitted = B c;
residual = a - fitted; RMS = sqrt(mean(residual^2)).

---- Helpers ----
_nuisance_basis_builder
_spectra_gridder
basis_solver
```

#### `fit_saver`

```text
---- Summary ----
Main function to save the components found as a fit file in the fits folder, in
the layout with heading lines (DATA_FORMAT.md, "fit csv"), with the unit
'relative': each component scaled so that its largest point is 1.

---- Inputs ----
fit : dict
    Fit dictionary from fit_table_builder.
path : Path
    File to write (.csv).

---- Globals read ----
None.

---- Outputs ----
Path
    The file written.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
value written = response x 1 000 000: the component as found (fit_file_writer).

---- Helpers ----
fit_file_writer
```

#### `fit_table_builder`

```text
---- Summary ----
Main function to turn the components found into a fit dictionary, exactly as
fit_importer gives for a fit file, so the haem decomposition can use it.

---- Inputs ----
result : dict
    Result of component_builder.
names : Optional[List[str]]
    Name of each component; None names them PC1, PC2, ...

---- Globals read ----
None.

---- Outputs ----
dict
    {'haem_list': names, 'data': table of (wavelength, response) column pairs,
    'scale_divisor', 'notes'}. The responses are the components as found (a
    largest peak of +1) brought to the standard scale of the fit files, so the
    raw amounts are the same whether the components are used at once or saved and
    read back: the spectra they come from and the fit files have the same sign.
    Raises ValueError, with a message for the user, when the names are not one
    per component, or one is empty, holds a comma or is used twice: such a fit
    could not be read back once saved.

---- Globals mutated ----
None.

---- Equations ----
response = component / 1 000 000 (fit_scale_standardiser).

---- Helpers ----
fit_scale_standardiser
```

## `utils_shared/pca_plotter.py`

Figures of the principal component analysis: the components and example decompositions.

### PLOTTER HELPERS

#### `_example_drawer`

```text
---- Summary ----
Helper function to draw one decomposed spectrum: the measured spectrum, what each
component and the offset and scatter add, their sum, and below it the residual.

---- Inputs ----
main : Axes
    Axes for the spectrum and its parts.
lower : Axes
    Axes for the residual.
wavelengths : np.ndarray
    Wavelengths (nm), shape (n_wavelengths).
example : dict
    One example of decomposition_example_finder ('best' or 'worst').
heading : str
    Start of the title, for example 'Smallest residual'.
names : List[str]
    Name of each component.
colours : List[str]
    Colour of each component.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; draws on the axes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_reference_line_drawer`

```text
---- Summary ----
Helper function to draw faint vertical lines at the usual peaks of haems a, b and c
that fall inside the window, so the peaks of a component can be compared with them.

---- Inputs ----
ax : Axes
    Axes to draw on.
window : tuple
    (start, end) of the wavelengths shown (nm).
colours : dict
    {haem type: colour} of the lines.
is_labelled : bool
    True to write the haem type above each line.

---- Globals read ----
REFERENCE_PEAKS (module constant).

---- Outputs ----
None
    Nothing; draws on the axes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `pca_example_figure_builder`

```text
---- Summary ----
Main function to show how well the components describe the spectra: the spectrum
described best and the one described worst, each split into its components, offset
and scatter, with the residual underneath.

---- Inputs ----
examples : dict
    Result of decomposition_example_finder.
names : List[str]
    Name of each component.
colours : List[str]
    Colour of each component.
fig : Optional[Figure]
    Figure to draw in; None makes a new one.

---- Globals read ----
None.

---- Outputs ----
Figure
    The figure; matplotlib styling is taken from the caller's rcParams. The two
    residual panels share their scale, so their sizes can be compared.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_example_drawer
```

#### `pca_figure_builder`

```text
---- Summary ----
Main function to draw the components found, each in a panel of its own, coloured by
the haem type it looks like, with faint lines at the usual peaks of haems a, b and
c.

---- Inputs ----
analysis : dict
    Result of component_finder.
result : dict
    Result of component_builder (the chosen components).
names : List[str]
    Name of each component.
types : List[str]
    Haem type of each component (component_classifier).
colours : List[str]
    Colour of each component.
type_colours : dict
    {'a', 'b', 'c': colour} of the guide lines.
fig : Optional[Figure]
    Figure to draw in; None makes a new one.

---- Globals read ----
None.

---- Outputs ----
Figure
    The figure; matplotlib styling (fonts and sizes) is taken from the caller's
    rcParams.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_reference_line_drawer
```

## `utils_shared/questions.py`

Helpers for asking numbered questions in the terminal of the window.

### CLASSES

#### `UserQuitError`

```text
---- Summary ----
Raised when the input ends (the window closed) so the program can stop cleanly.

---- Attributes ----
None.

---- Globals read ----
None.

---- Methods ----
None.
```

### QUESTIONS HELPERS

#### `_brightener`

```text
---- Summary ----
Helper function to set part of a question line in another colour (what Enter
gives, or a unit) and go back to the question colour after it.

---- Inputs ----
text : str
    The part to colour.
code : str
    Its colour code (COLOUR_DEFAULT by default).

---- Globals read ----
COLOUR_DEFAULT, COLOUR_QUESTION, RESET (module constants).

---- Outputs ----
str
    The part with its colour, followed by the question colour again.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_input_reader`

```text
---- Summary ----
Helper function to show the answer prompt and read what the user types in the
window's answer box (the window puts its own reader in place of input while it
runs). Every answer, typed or given with the mouse, passes here, and is added to
the run's log once it has started.

---- Inputs ----
text : str
    The question text (not printed; kept so tests can replace this function and
    match on it).
indent : str
    Indent placed before the "> " prompt.

---- Globals read ----
None.

---- Outputs ----
str
    The typed answer with surrounding spaces removed.

---- Globals mutated ----
None. Reads from the terminal and writes the answer to the run's log; raises
UserQuitError when the input ends (side effects).

---- Equations ----
None.

---- Helpers ----
answer_logger
```

#### `_limits_checker`

```text
---- Summary ----
Helper function to say whether a number is within the limits of a number question.

---- Inputs ----
value : float
    The number.
minimum : Optional[float]
    Smallest accepted value, or None.
maximum : Optional[float]
    Largest accepted value, or None.
exclusive_minimum : bool
    True when the minimum itself is not accepted.
is_whole : bool
    True when only whole numbers are accepted.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the number can be used.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_list_ending_builder`

```text
---- Summary ----
Helper function to write the end of a question answered from a numbered list: every
number up to LIST_SPELLED_OUT options, (1/2/3) with the default brighter, and a
range beyond, (1–7), whose default is brighter in the list instead.

---- Inputs ----
count : int
    Number of options.
default_number : Optional[int]
    Number given by Enter, brightened when every number is shown; None for none.

---- Globals read ----
LIST_SPELLED_OUT (module constant).

---- Outputs ----
str
    The ending, for example "(1/2/3)" or "(1–7)", with colour codes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_brightener
```

#### `_number_builder`

```text
---- Summary ----
Helper function to advance the counters and build the next question number.

---- Inputs ----
depth : int
    Numbering depth (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
MAX_DEPTH (module constant).

---- Outputs ----
str
    Question number such as "3.1.2".

---- Globals mutated ----
None. Increments the module counters _counters at the depth and resets deeper levels
(side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_number_depth_finder`

```text
---- Summary ----
Helper function to give the numbering depth of a question: that of its own number
when it has one ('3.4.1' is depth 2), otherwise the depth it was asked at.

---- Inputs ----
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '3.5'; None when it is
    numbered in the order asked.
depth : int
    Numbering depth it was asked at (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
None.

---- Outputs ----
int
    The numbering depth, at least 1. Raises ValueError for a number that is not
    whole numbers joined by dots, below a section.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_number_hint_builder`

```text
---- Summary ----
Helper function to write the one sentence shown after a wrong answer to a number
question: what kind of number, its limits and an example within them.

---- Inputs ----
minimum : Optional[float]
    Smallest accepted value, or None.
maximum : Optional[float]
    Largest accepted value, or None.
exclusive_minimum : bool
    True when the minimum itself is not accepted.
is_whole : bool
    True when only whole numbers are accepted.

---- Globals read ----
None.

---- Outputs ----
str
    For example "Type a number of 0 or more, for example 2.5." or "Type a whole
    number from 1 to 8, for example 3."; without the example when none fits.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_limits_checker
```

#### `_numbers_hint_builder`

```text
---- Summary ----
Helper function to write the one sentence shown after a wrong answer to a question
answered by several numbers from a list.

---- Inputs ----
count : int
    Number of options in the list.

---- Globals read ----
None.

---- Outputs ----
str
    For example "Type numbers from 1 to 5, separated by commas, for example 1,3.".

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_options_printer`

```text
---- Summary ----
Helper function to print the numbered options of a list under its question, the
ones Enter gives brighter where the end of the question does not show them.

---- Inputs ----
labels : Sequence[str]
    The options as shown, numbered 1), 2), ...
indent : str
    Indent of the question.
bright : Set[int]
    Numbers (from 1) of the options to show brighter.

---- Globals read ----
COLOUR_DEFAULT, INDENT (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `_question_printer`

```text
---- Summary ----
Helper function to print the numbered question line in the question colour, ending
in what Enter gives, with an optional quieter line just above it. A question with
its own number shows that number and leaves the counters alone; any other takes the
next number in the order asked.

---- Inputs ----
question : str
    Question text, without its number.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
ending : str
    What Enter gives, such as "[120]" or "(y/N)", with its colour codes; may be
    empty.
note : str
    A line said just above the question in the quieter colour, such as what "n"
    does; may be empty.
has_unit : bool
    True for a number question, whose unit in brackets is highlighted.
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '3.5'; None to number
    it in the order asked. When given, ``depth`` must be its depth.

---- Globals read ----
COLOUR_QUIET, INDENT (module constants); _tight_next (module state).

---- Outputs ----
str
    Indent to use for the answer prompt and the option lines.

---- Globals mutated ----
None. Prints to the terminal and clears the module flag _tight_next (side effects).

---- Equations ----
None.

---- Helpers ----
_number_builder
_unit_highlighter
text_colourer
```

#### `_time_announcer`

```text
---- Summary ----
Helper function to tell the window, when there is one, that the question being
asked can be answered with the mouse (a drag across the plot, turned into the
answer by ``reader``), or no longer can.

---- Inputs ----
kind : Optional[str]
    'span' (a drag), or None once the question has its answer.
reader : Optional[Callable]
    Turns the drag into the answer: reader(file name, start_min, end_min); it
    returns None when that file or place gives no answer. None with kind None.

---- Globals read ----
_time_requester (module state).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Calls the registered function (side effect); nothing happens without one.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_unit_highlighter`

```text
---- Summary ----
Helper function to highlight the unit of a number question, written once in
brackets after the quantity: "How long a window (s) ...", "... concentration
(µM)?". Brackets holding words with spaces, such as "(0 for none)", are left alone.

---- Inputs ----
question : str
    Question text.

---- Globals read ----
COLOUR_UNIT, UNIT_PATTERN (module constants).

---- Outputs ----
str
    The question with each unit in the unit colour.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_brightener
```

### MAIN FUNCTIONS

#### `accept_asker`

```text
---- Summary ----
Main function to ask a "Do you accept ...?" question, the one place its answers are
written. With one way to change it is a yes or no question, (Y/n), with a quieter
line above saying what n does; with more it is a numbered list starting
"1) Yes, accept", then "2) No, <change>" and so on.

---- Inputs ----
question : str
    The accept question, for example 'Do you accept these event labels?'.
changes : Sequence[Tuple[str, str]]
    The ways to change, at least one, as (key, what it does), for example
    ('no', 'change the labels again').
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '3.5'; None to number
    it in the order asked.

---- Globals read ----
None.

---- Outputs ----
str
    'yes' when accepted, otherwise the key of the change chosen. Raises ValueError
    when no way to change is given.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
choice_asker
yes_no_asker
```

#### `choice_asker`

```text
---- Summary ----
Main function to ask a question answered by choosing one numbered option. The end
of the question gives the numbers that can be typed: every one up to
LIST_SPELLED_OUT options, the default brighter, or a range beyond, the default
option brighter in the list.

---- Inputs ----
question : str
    Question text, without its number.
options : Sequence[Tuple[str, str]]
    Choices as (key, label) pairs, shown as 1), 2), ...
default : Optional[str]
    Key chosen when only Enter is pressed.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '5.1'; None to number
    it in the order asked.

---- Globals read ----
LIST_SPELLED_OUT (module constant).

---- Outputs ----
str
    Key of the chosen option.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_input_reader
_list_ending_builder
_number_depth_finder
_options_printer
_question_printer
retry_teller
```

#### `confirm_waiter`

```text
---- Summary ----
Main function to give a numbered instruction carried out in a table of the window
("Fill in ..., then press Confirm.") and wait until Confirm is pressed with the
table filled in. While the checker finds something wrong, its one sentence is said
and the instruction goes on waiting.

---- Inputs ----
question : str
    The instruction, without its number, ending "then press Confirm.".
checker : Callable[[], Optional[str]]
    Reads the table and gives None when it can be used, or the sentence saying
    what is still wrong.
note : str
    Lines said just above the instruction in the quieter colour, such as what each
    column means; may be empty.
depth : int
    Numbering depth of the instruction (1 = 3.1, 2 = 3.1.1, ...).
number : Optional[str]
    The instruction's own number from QUESTION_FLOW.md, such as '3.2'; None to
    number it in the order asked.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_input_reader
_number_depth_finder
_question_printer
retry_teller
```

#### `enter_waiter`

```text
---- Summary ----
Main function to give a numbered instruction that is carried out in the window (on
the plot or in the strip under it) and wait until Enter is pressed with the answer
box empty. Anything typed in the box instead is answered with ``nudge`` and the
instruction goes on waiting.

---- Inputs ----
question : str
    The instruction, without its number.
nudge : str
    One sentence saying where to do it instead of typing in the answer box.
depth : int
    Numbering depth of the instruction (1 = 3.1, 2 = 3.1.1, ...).
number : Optional[str]
    The instruction's own number from QUESTION_FLOW.md, such as '2.1'; None to
    number it in the order asked.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_input_reader
_number_depth_finder
_question_printer
retry_teller
```

#### `heading_printer`

```text
---- Summary ----
Main function to print a plain heading, for example the summary.

---- Inputs ----
text : str
    Heading text.

---- Globals read ----
COLOUR_SECTION (module constant); text_colourer.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `info_printer`

```text
---- Summary ----
Main function to print an information line (not a question) in the quieter colour,
indented to sit under the question above. A line already coloured (a warning)
keeps its own colour.

---- Inputs ----
text : str
    Text to print or process.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
tight : bool
    True to make the next question follow this line without a blank line.

---- Globals read ----
COLOUR_QUIET, INDENT (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal and sets the module flag _tight_next (side effects).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `multi_asker`

```text
---- Summary ----
Main function to ask a question answered by choosing several numbered options. A
quieter line above says to type numbers separated by commas; the end of the
question gives the numbers as for one choice, and the options Enter gives are
brighter in the list.

---- Inputs ----
question : str
    Question text, without its number.
options : Sequence[str]
    Option names, shown as 1), 2), ...
default_all : bool
    True to choose all options when only Enter is pressed and nothing is remembered.
keep_order : bool
    True to return the options in the order typed instead of list order.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
default_values : Optional[Sequence[str]]
    Choice from last time, used for Enter when given.
label_formatter : Optional[Callable[[str], str]]
    Function that changes how an option is shown, not what is returned.
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '5.4.1'; None to
    number it in the order asked.

---- Globals read ----
NUMBERS_NOTE (module constant).

---- Outputs ----
List[str]
    The chosen options.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_input_reader
_list_ending_builder
_number_depth_finder
_numbers_hint_builder
_options_printer
_question_printer
retry_teller
```

#### `number_asker`

```text
---- Summary ----
Main function to ask a question answered with a number, waiting until the value is
valid; after a wrong answer one sentence says what to type. The end of the question
gives what Enter gives, [120] or [skip], and a unit in brackets is highlighted. A
question that can be answered with the mouse says so to the window, where a drag
(``span_reader``) across the plot then writes the answer it gives into the answer
box.

---- Inputs ----
question : str
    Question text, without its number.
default : Optional[float]
    Answer used when only Enter is pressed.
minimum : Optional[float]
    Smallest accepted value.
maximum : Optional[float]
    Largest accepted value.
exclusive_minimum : bool
    True when the minimum itself is not accepted.
allow_blank : bool
    True to accept an empty answer as None when there is no default; shown as
    [skip].
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
span_reader : Optional[Callable[[str, float, float], Optional[float]]]
    Turns a drag across the plot into the answer: (file shown, start min, end min)
    -> answer, or None when that drag gives none. None when the mouse gives
    nothing.
is_whole : bool
    True when only whole numbers are accepted.
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '3.4.3'; None to
    number it in the order asked.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    The number, the default, or None for an accepted empty answer.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_brightener
_input_reader
_limits_checker
_number_depth_finder
_number_hint_builder
_question_printer
_time_announcer
retry_teller
typed_number_reader
```

#### `numbering_getter`

```text
---- Summary ----
Main function to read the current number at a depth, so it can be restored with
numbering_setter after questions are asked again.

---- Inputs ----
depth : int
    Numbering depth to read (0 = the section number).

---- Globals read ----
_counters (module state).

---- Outputs ----
int
    Current number at that depth.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `numbering_setter`

```text
---- Summary ----
Main function to set the current number at a depth, for example so the next
sub-questions are numbered 3.4.3.1.

---- Inputs ----
depth : int
    Numbering depth to set.
value : int
    Number to make current at that depth.

---- Globals read ----
MAX_DEPTH (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets and resets entries of the module counters _counters (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `path_cleaner`

```text
---- Summary ----
Main function to clean a path typed or dragged into the window by removing
surrounding quotes and spaces, and, on macOS and Linux, the backslashes that
Terminal puts before spaces and other characters when a folder is dragged in.

---- Inputs ----
text : str
    Text as received from the terminal.

---- Globals read ----
os.name.

---- Outputs ----
str
    Path text without surrounding quotes or spaces, or shell escapes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `progress_clearer`

```text
---- Summary ----
Main function to remove the progress line from the terminal.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `progress_printer`

```text
---- Summary ----
Main function to show a one-line progress message, in the quieter colour, that the
next message overwrites.

---- Inputs ----
text : str
    Message to show.

---- Globals read ----
COLOUR_QUIET (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal without a new line (side effect).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `retry_teller`

```text
---- Summary ----
Main function to say, after a wrong answer, in one sentence what to type; the
question is not printed again and waits for the next answer.

---- Inputs ----
hint : str
    One sentence, for example "Type y or n.".
depth : int
    Numbering depth of the question it answers (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
COLOUR_RETRY, INDENT (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `section_starter`

```text
---- Summary ----
Main function to start the next numbered section and print its heading.

---- Inputs ----
title : str
    Section title, without its number.

---- Globals read ----
COLOUR_SECTION, MAX_DEPTH (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Advances the module numbering counters _counters and prints the heading (side
effects).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `text_asker`

```text
---- Summary ----
Main function to ask a question answered with a line of text or a folder. An answer
the checker refuses gets its one sentence of what to type, and the question waits
for the next answer.

---- Inputs ----
question : str
    Question text, without its number.
default : Optional[str]
    Answer used when only Enter is pressed; shown brighter as [default].
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
checker : Optional[Callable[[Optional[str]], Optional[str]]]
    Takes the answer (the default for Enter) and gives None when it can be used,
    or the sentence saying what to type instead; None accepts every answer.
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '1.2'; None to number
    it in the order asked.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    The typed text, or the default when Enter is pressed.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_brightener
_input_reader
_number_depth_finder
_question_printer
retry_teller
```

#### `text_colourer`

```text
---- Summary ----
Main function to wrap text in a colour code, which the window's terminal shows.

---- Inputs ----
text : str
    Text to colour.
code : str
    ANSI colour code (COLOUR_QUESTION by default).

---- Globals read ----
COLOUR_QUESTION, RESET (module constants).

---- Outputs ----
str
    The coloured text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `text_italiser`

```text
---- Summary ----
Main function to write text in italics, which the window's terminal shows.

---- Inputs ----
text : str
    Text to put in italics.

---- Globals read ----
ITALIC, RESET (module constants).

---- Outputs ----
str
    The italic text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `time_request_setter`

```text
---- Summary ----
Main function to register what is told when a question can be answered with the
mouse: the window registers itself while it is open, so a drag across its plot can
give the answer.

---- Inputs ----
requester : Optional[Callable[[Optional[str], Optional[Callable]], None]]
    Function called with ('span', reader) when a question starts waiting for an
    answer the mouse can give, and with (None, None) when it has its answer (see
    _time_announcer); None to register nothing (when the window closes).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
_time_requester (module state).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `typed_number_reader`

```text
---- Summary ----
Main function to read a typed number, the one reader of the answer box, the OD
table and the boxes of the strip: spaces around it are ignored and a comma may be
the decimal sign. Each place checks its own limits.

---- Inputs ----
text : str
    What was typed, for example '2.5', ' 2,5 ' or '1e3'.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    The number, or None for an empty text, a text that is not a number, "nan" or an
    infinity.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `yes_no_asker`

```text
---- Summary ----
Main function to ask a yes or no question, ending in (y/N) or (Y/n) with the letter
Enter gives brighter.

---- Inputs ----
question : str
    Question text, without its number.
default : bool
    Answer used when only Enter is pressed (the capital letter at the end).
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
note : str
    A line said just above the question in the quieter colour; may be empty.
number : Optional[str]
    The question's own number from QUESTION_FLOW.md, such as '3.1'; None to number
    it in the order asked.

---- Globals read ----
None.

---- Outputs ----
bool
    True for y or yes, False for n or no (in any capitals), the default for Enter.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters when it has no number of its own.

---- Equations ----
None.

---- Helpers ----
_brightener
_input_reader
_number_depth_finder
_question_printer
retry_teller
```

## `utils_shared/redox_regions.py`

The maths of the oxidised and reduced regions: a haem's level in a region, the two

### REGION HELPERS

#### `_region_open_checker`

```text
---- Summary ----
Helper function to say whether a region of a file is chosen: at least as long as
the least length.

---- Inputs ----
values : Dict[str, float]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
region : str
    'oxidised' or 'reduced'.
minimum_min : float
    Least length of a region (min).

---- Globals read ----
LENGTH_TOLERANCE_MIN.

---- Outputs ----
bool
    True when the region is open (chosen).

---- Globals mutated ----
None.

---- Equations ----
open when end - start >= least length.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `edge_anchor_finder`

```text
---- Summary ----
Main function to say where an edge of a region sits by the addition nearest to it:
which addition of the file, counted in order, and how far from it. It is the first
half of copying an edge to another file; edge_time_finder is the second.

---- Inputs ----
time_min : float
    Time of the edge (min), on the same time axis as the additions.
additions_min : Sequence[float]
    Times of the additions of the file the edge was set on (min), in any order.

---- Globals read ----
None.

---- Outputs ----
Optional[Tuple[int, float]]
    (number of the nearest addition, counted in time order from 0; distance of the
    edge from it in minutes, negative before the addition), or None when the file
    has no addition or the time is blank, so the edge cannot be copied.

---- Globals mutated ----
None.

---- Equations ----
nearest = the addition with the smallest |time - addition|; of two equally near,
the earlier. distance = time - nearest. An edge before the first addition is
nearest to the first, so it is copied by its distance to the first.

---- Helpers ----
None.
```

#### `edge_time_finder`

```text
---- Summary ----
Main function to give the time of a copied edge in another file: the same distance
from the addition of the same number.

---- Inputs ----
anchor : Tuple[int, float]
    (number of the addition, counted in time order from 0; distance from it in
    minutes), from edge_anchor_finder.
additions_min : Sequence[float]
    Times of the additions of the file the edge is copied to (min), in any order.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    Time of the edge in that file (min), on the time axis of its additions, or None
    when the file has no addition of that number (it has fewer additions), so it
    keeps the region it had. The time is not kept within the used part of the run;
    the limits of the edges do that.

---- Globals mutated ----
None.

---- Equations ----
time = time of the addition of the same number in this file + distance.

---- Helpers ----
None.
```

#### `haem_levels_finder`

```text
---- Summary ----
Main function to find the oxidised and the reduced level of every haem of a file
from the two regions kept for it. A file needs both regions: with none, with only
one, or with one that no longer holds enough spectra in the used part of the run
(the trim or the ignored parts changed), it has no levels.

---- Inputs ----
haem_table : pd.DataFrame
    Haem table (time, spectrum index and one column per haem), in any one unit,
    on the time axis of the trimmed data.
regions : Optional[Dict[str, float]]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} as times on the
    original recording (min), or None when nothing is kept for the file.
shift_min : float
    Trim start (min): what is taken off a time on the recording for the time on
    the trimmed data.
used_span : Tuple[float, float]
    (first, last) time of the used part of the run (min), on the trimmed data.
minimum_points : int
    Least number of spectra a region must hold (config.REGION_MINIMUM_POINTS).
label : str
    Name of the file in the messages.

---- Globals read ----
REGION_NAMES.

---- Outputs ----
Optional[dict]
    {'oxidised': {haem: level}, 'reduced': {haem: level}, in the unit of the
    table; 'oxidised_region', 'reduced_region': (start_min, end_min) on the time
    axis of the table, kept within the used part}, or None when the file does not
    have both regions. Raises ValueError (region_level_finder) when a haem has too
    few values inside a region that holds enough spectra.

---- Globals mutated ----
None.

---- Equations ----
start = max(start on the recording - shift, first); end = min(end on the
recording - shift, last). A region counts when it holds at least minimum_points
spectra with start <= time <= end. level: region_level_finder.

---- Helpers ----
region_level_finder
time_getter
```

#### `percent_oxidised_calculator`

```text
---- Summary ----
Main function to put every haem of a table on the % oxidised scale, which runs
from its level in the reduced region (0 %) to its level in the oxidised region
(100 %).

---- Inputs ----
haem_table : pd.DataFrame
    Haem table (time, spectrum index and one column per haem), in any one unit:
    the scale is the same for the amounts, the absorbances and delta D.
oxidised_levels : Dict[str, float]
    {haem: its level in the oxidised region}, in the unit of the table
    (region_level_finder).
reduced_levels : Dict[str, float]
    {haem: its level in the reduced region}, in the same unit.

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Copy of the table with every haem in %; values above 100 and below 0 are kept.
    A haem whose two levels are equal, or blank, has an empty column (NaN), as no
    scale can be made from them. result.attrs["percent_oxidised"] holds
    {'oxidised_level_by_haem', 'reduced_level_by_haem': the levels used,
    'empty_haems': the haems with an empty column}. Raises ValueError when a haem
    of the table has no level in one of the two.

---- Globals mutated ----
None.

---- Equations ----
percent = (D - D_red) / (D_ox - D_red) x 100, per haem, with D the value at one
time, D_ox the oxidised level and D_red the reduced level.

---- Helpers ----
measurement_column_finder
value_getter
```

#### `region_edge_copier`

```text
---- Summary ----
Main function to copy an edge set on one file to another file: the same distance
from the addition of the same number as the one nearest to it in the first file.

---- Inputs ----
time_min : float
    Time of the edge on the file it was set on (min).
source_additions_min : Sequence[float]
    Times of the additions of that file (min), on the same time axis.
target_additions_min : Sequence[float]
    Times of the additions of the file the edge is copied to (min), on that
    file's time axis.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    Time of the edge in the other file (min), not yet kept within its limits, or
    None when it cannot be copied (the first file has no addition, or the other
    has fewer additions), so the other file keeps the edge it had.

---- Globals mutated ----
None.

---- Equations ----
time = time of the same addition in the other file + (edge - nearest addition).

---- Helpers ----
edge_anchor_finder
edge_time_finder
```

#### `region_edge_setter`

```text
---- Summary ----
Main function to set one edge of one region of a file to a time, kept within the
limits: an edge stays in the used part of the run; moved past the other edge of its
region it pushes that edge along; and the two regions never overlap. An edge moved
into the other region stops at that region's nearer side, and when the other region
would then lie inside this one, the edge not being set gives way to it.

---- Inputs ----
values : Dict[str, float]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
key : str
    The edge set: one of REGION_KEYS.
value : float
    Time wanted for it (min).
used_span : Tuple[float, float]
    (first, last) time of the used part of the run (min): not trimmed, not
    ignored.
minimum_min : float
    Least length of a region (min); a shorter one counts as not chosen, so the
    other region may cross it.

---- Globals read ----
None.

---- Outputs ----
Dict[str, float]
    New values of the file; the dictionary given is not changed.

---- Globals mutated ----
None.

---- Equations ----
t = value kept within the used part. With the other region open from a to b and
a < t < b: t = a when t - a <= b - t, otherwise b. Start edge set: end = max(end,
t), and end = a when t <= a < end. End edge set: start = min(start, t), and
start = b when start < b <= t.

---- Helpers ----
_region_open_checker
```

#### `region_edges_builder`

```text
---- Summary ----
Main function to give the edges a file starts the regions step with: both regions
not chosen, parked at the sides of the used part (oxidised at its start, reduced at
its end), or the regions remembered for it, kept within the used part. A
remembered region that is no longer long enough is parked again.

---- Inputs ----
used_span : Tuple[float, float]
    (first, last) time of the used part of the run (min).
remembered : Optional[Dict[str, float]]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} (min) on the same
    time axis, or None for a file with nothing remembered.
minimum_min : float
    Least length of a region (min).

---- Globals read ----
REGION_KEYS, REGION_NAMES.

---- Outputs ----
Dict[str, float]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} (min).

---- Globals mutated ----
None.

---- Equations ----
Parked: oxidised start = oxidised end = first; reduced start = reduced end = last.

---- Helpers ----
_region_open_checker
```

#### `region_layout_finder`

```text
---- Summary ----
Main function to say where the edges of the two regions of one file sit on its
plot, with the words by each handle, and which parts are shaded. A region not
chosen has one handle, reading "not chosen", and no shading.

---- Inputs ----
values : Dict[str, float]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min),
    on the time axis of the plot.
minimum_min : float
    Least length of a region (min); a shorter one is not chosen.

---- Globals read ----
REGION_NAMES, CLOSED_KEYS.

---- Outputs ----
Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
    (edges, parts): edges as [(key, time_min, words, kind)] with kind 'oxidised'
    or 'reduced'; parts as [(start_min, end_min, kind)]. The words of an open
    region are by the edge that opened it (the end of the oxidised region, the
    start of the reduced one), which keeps them clear of its other handle where
    the regions usually are; the other edge has no words.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_region_open_checker
```

#### `region_level_finder`

```text
---- Summary ----
Main function to find the level of every haem of a table in one region: the median
of its values there. One region serves every haem of the file.

---- Inputs ----
haem_table : pd.DataFrame
    Haem table (time, spectrum index and one column per haem), in any one unit.
start_min : float
    First time of the region (min), on the time axis of the table.
end_min : float
    Last time of the region (min); the spectra at both edges count as inside.
minimum_points : int
    Least number of spectra with a value a haem must have in the region (>= 1;
    config.REGION_MINIMUM_POINTS in the program).
region : str
    Name of the region in the messages: 'oxidised region' or 'reduced region'.
label : str
    Name of the file in the messages.

---- Globals read ----
None.

---- Outputs ----
Dict[str, float]
    {haem: its level in the region}, in the unit of the table. Raises ValueError,
    with a message for the user, when the region ends before it starts, a time is
    blank, the table holds no haem, or a haem has fewer than minimum_points
    spectra with a value in the region.

---- Globals mutated ----
None.

---- Equations ----
level = median(D at every spectrum with start <= time <= end), per haem. A spectrum
with a blank value for a haem is left out for that haem.

---- Helpers ----
measurement_column_finder
time_getter
value_getter
```

#### `region_pointer_reader`

```text
---- Summary ----
Main function to turn a time pointed at on the plot into the time of the edge put
there, in steps of 0.1 min.

---- Inputs ----
time_min : float
    The time pointed at, on the time axis of the plot (min).

---- Globals read ----
None.

---- Outputs ----
float
    The time rounded to 0.1 min; the limits of the edges are applied afterwards
    (region_edge_setter).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `region_span_reader`

```text
---- Summary ----
Main function to give the two regions of a file as they were chosen: each as its
first and last time, or None when it was not chosen.

---- Inputs ----
values : Dict[str, float]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
minimum_min : float
    Least length of a region (min); a shorter one is not chosen.

---- Globals read ----
REGION_NAMES.

---- Outputs ----
Dict[str, Optional[Tuple[float, float]]]
    {'oxidised': (start_min, end_min) or None, 'reduced': the same}. A file needs
    both for its haems' levels; one alone counts as none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_region_open_checker
```

#### `short_region_closer`

```text
---- Summary ----
Main function to give the edges of a file with every region that is too short to
count closed: its two edges together, where its handle is. A region is then
chosen exactly when its end is after its start, which is how it is kept with the
dataset.

---- Inputs ----
values : Dict[str, float]
    {oxidised_start, oxidised_end, reduced_start, reduced_end} of the file (min).
minimum_min : float
    Least length of a region (min); a shorter one is not chosen.

---- Globals read ----
REGION_NAMES, CLOSED_KEYS.

---- Outputs ----
Dict[str, float]
    New values of the file; the dictionary given is not changed.

---- Globals mutated ----
None.

---- Equations ----
A region with end - start < least length: start = end = the edge that opens it
(the end of the oxidised region, the start of the reduced one).

---- Helpers ----
_region_open_checker
```

## `utils_shared/reference_level.py`

The finders of the reference level of a trace: the median of its highest or lowest

### REFERENCE LEVEL HELPERS

#### `_usable_point_keeper`

```text
---- Summary ----
Helper function to keep the points of a trace a reference level may be taken from,
in time order.

---- Inputs ----
times : np.ndarray
    Time of each point in minutes, shape (n_timepoints).
values : np.ndarray
    Value at each point, shape (n_timepoints).
start : float
    Earliest time that may be used, in minutes.
stop : float
    Latest time that may be used, in minutes.
n_points : int
    Number of points the level is taken from (>= 1).

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray]
    (times, values) of the usable points, in time order, each of shape
    (n_usable). Raises ValueError when n_points is below 1.

---- Globals mutated ----
None.

---- Equations ----
A point is usable when its time and value are not blank and start <= time <= stop.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `reference_level_finder`

```text
---- Summary ----
Main function to find the reference level of a trace: the median of its highest (or
lowest) points in a row. It is the one rule behind the 0 % and 100 % of the %
scale.

---- Inputs ----
times : np.ndarray
    Time of each point in minutes, shape (n_timepoints).
values : np.ndarray
    Value at each point, shape (n_timepoints).
start : float
    Earliest time that may be used, in minutes.
stop : float
    Latest time that may be used, in minutes.
n_points : int
    Number of points in a row that make one window (>= 1).
is_highest : bool
    True for the window with the highest median, False for the lowest.

---- Globals read ----
None.

---- Outputs ----
Optional[dict]
    {'level': the median of the chosen window, 'start_time' and 'end_time': the
    times of its first and last point (min), 'n_points': n_points}, or None when
    fewer than n_points usable points lie between start and stop. Of equal windows
    the earliest is chosen. Raises ValueError when n_points is below 1.

---- Globals mutated ----
None.

---- Equations ----
The points are put in time order; points with a blank time or value, or outside
start to stop, are dropped, so the points on either side of a blank count as
neighbours. Window i = points i to i + n_points - 1; level = max (or min) over i
of median(window i). The windows are counted in points, not in time, and the last
one ends at the last usable point.

---- Helpers ----
_usable_point_keeper
```

#### `start_level_finder`

```text
---- Summary ----
Main function to find the level a trace starts at: the median of its first points.
It is the rule behind the 0 of delta D.

---- Inputs ----
times : np.ndarray
    Time of each point in minutes, shape (n_timepoints).
values : np.ndarray
    Value at each point, shape (n_timepoints).
start : float
    Earliest time that may be used, in minutes (the end of the ignored start).
stop : float
    Latest time that may be used, in minutes.
n_points : int
    Number of points the level is taken from (>= 1).

---- Globals read ----
None.

---- Outputs ----
Optional[dict]
    {'level': the median of the first n_points usable points, 'start_time' and
    'end_time': the times of the first and the last of them (min), 'n_points':
    n_points}, or None when fewer than n_points usable points lie between start
    and stop. Raises ValueError when n_points is below 1.

---- Globals mutated ----
None.

---- Equations ----
The points are put in time order; points with a blank time or value, or outside
start to stop, are dropped. level = median(the first n_points points left). The
points are counted, not timed, so a blank point is made up for by the next one.

---- Helpers ----
_usable_point_keeper
```

#### `window_seconds_calculator`

```text
---- Summary ----
Main function to work out how long a window of points in a row lasts, for the
messages to the user.

---- Inputs ----
times : np.ndarray
    Time of each point in minutes, shape (n_timepoints).
n_points : int
    Number of points in a row that make one window.

---- Globals read ----
None.

---- Outputs ----
float
    Length of the window in seconds; NaN when fewer than two times are known.

---- Globals mutated ----
None.

---- Equations ----
seconds = n_points x median time between neighbouring points (min) x 60.

---- Helpers ----
None.
```

## `utils_shared/run_logging.py`

Mirror console output to a timestamped log file from the results folder question to the

### CLASSES

#### `_Tee`

```text
---- Summary ----
File-like object that writes everything to several streams at once: to the first
as it is, to the others without the terminal's colour codes.

---- Attributes ----
streams : Tuple[Any, ...]
    File-like objects every write is copied to.

---- Globals read ----
COLOUR_CODE_PATTERN (module constant).

---- Methods ----
__init__
__getattr__
flush
isatty
write
```

##### `__init__`

```text
---- Summary ----
Method to store the streams that every write is copied to.

---- Inputs ----
*streams : Any
    File-like objects (for example the console and the log file).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the streams attribute on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__getattr__`

```text
---- Summary ----
Method to pass any other attribute lookup (such as encoding) to the first
stream.

---- Inputs ----
name : str
    Attribute name that was not found on the instance.

---- Globals read ----
None.

---- Outputs ----
Any
    The attribute of the first stream.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `flush`

```text
---- Summary ----
Method to flush every stream. The name is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Flushes every stream (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `isatty`

```text
---- Summary ----
Method to say whether the first stream is a terminal. The name is fixed by the
file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the first stream is an interactive terminal.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `write`

```text
---- Summary ----
Method to write text to every stream and flush it, unless the current thread is
capturing its output (see output_capture), in which case it is kept by the
capture. Every stream after the first gets the text without colour codes. The
name is fixed by the file-like protocol.

---- Inputs ----
text : str
    Text to write.

---- Globals read ----
COLOUR_CODE_PATTERN (module constant).

---- Outputs ----
int
    Number of characters written.

---- Globals mutated ----
None. Writes to and flushes every stream (side effect).

---- Equations ----
None.

---- Helpers ----
captured_buffer_getter
```

### MAIN FUNCTIONS

#### `answer_logger`

```text
---- Summary ----
Main function to add an answer the user gave to the log of the run being logged,
under its question; the window shows the answer itself. Nothing is done while no
run is being logged.

---- Inputs ----
text : str
    The answer as it is to read in the log, for example "   > 12".

---- Globals read ----
_details_targets (module state).

---- Outputs ----
None
    Nothing. An answer that cannot be written (a full disk) is left out.

---- Globals mutated ----
None. Writes to the log (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `details_place_setter`

```text
---- Summary ----
Main function to set where the details of a problem go while no run is being
logged: the error stream the program had before its window took the output over
(the start-up log, or the terminal it was started from).

---- Inputs ----
stream : Any
    File-like object for the details, or None for nowhere.
place : str
    That place in words for the user, to complete "The details are in ...".

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
_details_targets (module state).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `details_writer`

```text
---- Summary ----
Main function to write the details of a problem where the user does not see them:
the log of the run being logged, or else the place set by details_place_setter.
Never to the window, even while a thread's output is captured.

---- Inputs ----
text : str
    The details, for example Python's own report of an error.

---- Globals read ----
_details_targets (module state).

---- Outputs ----
str
    Where they were written, in words for the user; empty when they could not be
    written anywhere.

---- Globals mutated ----
None. Writes to the log or the stream (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `logging_starter`

```text
---- Summary ----
Main function to start copying everything printed to a timestamped log file, as
soon as the results folder is known, so the questions and their answers are kept
even when Portimao is closed before the run.

---- Inputs ----
export_root : Path
    Results folder; the log goes to <export_root>/logs/YYYY_MM_DD-HH_MM_SS.log.
title : str
    Program name, branch and version (program_title_builder), written on the first
    line of the log.
data_folder : Path
    Folder of the .paf files, written at the top of the log.

---- Globals read ----
None.

---- Outputs ----
dict
    Session dictionary {log_path, log_file, original_stdout, original_stderr,
    tee_stdout, tee_stderr, closed}, to be passed to settings_logger and
    logging_stopper.

---- Globals mutated ----
_details_targets (module state), so the details of a problem and the answers go to
this log. Creates the log folder and file, writes the title, seed and folders to
its first lines, replaces sys.stdout and sys.stderr with copying streams and prints
the log location (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `logging_stopper`

```text
---- Summary ----
Main function to restore the console streams and close the log file.

---- Inputs ----
session : Optional[dict]
    Session dictionary from logging_starter, or None.

---- Globals read ----
_details_targets (module state).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
_details_targets (module state), so the details of a problem no longer go to this
log. Restores sys.stdout and sys.stderr, closes the log file and marks the session
closed (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `settings_logger`

```text
---- Summary ----
Main function to write every setting of the run to its log, once all the questions
are answered and before anything is processed. The window does not show them.

---- Inputs ----
session : Optional[dict]
    Session dictionary from logging_starter, or None.
settings : dict
    The answers of the run, by name.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Settings that cannot be written (a full disk) are left out.

---- Globals mutated ----
None. Writes to the log (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/schema.py`

Names and conventions of the experiment data model.

### MAIN FUNCTIONS

#### `finite_float_converter`

```text
---- Summary ----
Main function to convert a value to a finite float, or NaN when that is not
possible.

---- Inputs ----
value : Any
    Value to convert.

---- Globals read ----
None.

---- Outputs ----
float
    The value as a float, or NaN when it is not a number or not finite.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `measurement_column_finder`

```text
---- Summary ----
Main function to list the measurement columns of an experiment DataFrame.

---- Inputs ----
df : pd.DataFrame
    Time-resolved DataFrame with TIME_COLUMN.

---- Globals read ----
TIME_COLUMN, SPECTRUM_INDEX_COLUMN (module constants).

---- Outputs ----
List[str]
    Every column except TIME_COLUMN and SPECTRUM_INDEX_COLUMN.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `source_resolver`

```text
---- Summary ----
Main function to look up a dataset of an experiment by its source name from the
settings.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
source : str
    Source name, one of the keys of ``keys`` (for example "raw", "od", "percent").
keys : Dict[str, str]
    VO2_KEYS or HAEM_KEYS: {source name: experiment dictionary key}.
what : str
    Label used in error messages, for example "VO2" or "haem".

---- Globals read ----
None.

---- Outputs ----
Tuple[str, pd.DataFrame]
    (experiment dictionary key, the DataFrame). Raises ValueError when the source
    name is invalid or the dataset has not been calculated.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `time_getter`

```text
---- Summary ----
Main function to read the time column of an experiment DataFrame.

---- Inputs ----
df : pd.DataFrame
    Time-resolved DataFrame; must hold TIME_COLUMN.

---- Globals read ----
TIME_COLUMN (module constant).

---- Outputs ----
np.ndarray
    Times in minutes as a float array, shape (n_points,); unreadable values are NaN.
    Raises KeyError when the column is missing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `value_getter`

```text
---- Summary ----
Main function to read one measurement column as a float array.

---- Inputs ----
df : pd.DataFrame
    Time-resolved DataFrame.
column : str
    Name of the measurement column.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Values as a float array, shape (n_points,); unreadable values are NaN.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/spectral_decomposer.py`

Spectral fit loading and haem decomposition routines.

### SPECTRAL DECOMPOSER HELPERS

#### `_fit_heading_reader`

```text
---- Summary ----
Helper function to read the lines at the top of a fit file in the layout with
heading lines: its format, then one 'name,text' line each, up to the first empty
line.

---- Inputs ----
lines : List[str]
    The lines of the file; the first holds FIT_FILE_MARK.
label : str
    Name of the fit file, used in the messages.

---- Globals read ----
FIT_FILE_MARK, FIT_FILE_FORMAT (module constants).

---- Outputs ----
Tuple[Dict[str, str], int]
    ({name of each heading line, in lower case: its text, the cells after the name
    joined by ', '}, index in lines of the haem names: the first line that is not
    empty after the heading lines). A name used twice keeps its first text. Raises
    ValueError, with a message for the user, when the first line gives no format,
    the format is newer than FIT_FILE_FORMAT, or no table follows.

---- Globals mutated ----
None.

---- Equations ----
None. A line is empty when all its cells are, as a spreadsheet saves an empty line
(',,,,').

---- Helpers ----
None.
```

#### `_fit_table_cleaner`

```text
---- Summary ----
Helper function to check the table of a fit file and to give every haem clean rows:
numbers only, no blank rows, wavelengths going upwards.

---- Inputs ----
data : pd.DataFrame
    The fit table as read: (wavelength, response) column pairs, one pair per haem;
    the header of each wavelength column names the haem.
label : str
    Name of the fit file, used in the messages.
first_row : int
    Row of the file that holds row 0 of the table (counted from 1), so that the
    messages name the row as the file has it: 2 for a file whose only heading is
    the haem names.

---- Globals read ----
None.

---- Outputs ----
Tuple[pd.DataFrame, List[str]]
    (the table with the same headers, each haem's rows at the top and blanks below
    the shorter haems; the notes for the user, one sentence per haem whose leftover
    rows were left out). Raises ValueError, with a message for the user, when the
    columns are not in pairs, a haem has no name, a cell is not a number, a row
    holds only one of wavelength and response, or a haem has fewer than two rows.

---- Globals mutated ----
None.

---- Equations ----
A haem whose wavelengths all go downwards is turned round. Where the wavelengths
of a haem jump backwards, the rows before the jump are kept and the rest left out:
such rows are leftovers of another column, not data.

---- Helpers ----
_number_column_reader
```

#### `_fit_unit_finder`

```text
---- Summary ----
Helper function to find which of the fit units the Unit line of a fit file names,
however it is spaced, capitalised or written with a micro sign.

---- Inputs ----
text : str
    Text of the Unit line, for example 'OD/mM/cm' or 'od / uM / cm'.

---- Globals read ----
FIT_UNITS (module constant).

---- Outputs ----
Optional[str]
    The unit as FIT_UNITS writes it, or None when the text names none of them.

---- Globals mutated ----
None.

---- Equations ----
None. The Greek mu (μ) and a u in place of µ count as the micro sign.

---- Helpers ----
None.
```

#### `_haem_shape_getter`

```text
---- Summary ----
Helper function to give the filled rows of one haem of a fit table, so that the
blanks below a shorter haem never reach a calculation.

---- Inputs ----
fit_data : pd.DataFrame
    Fit table from fit_importer.
index : int
    Number of the haem in the table, from 0.

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray]
    (wavelengths in nm, responses) of that haem, each of shape (n_rows of the
    haem).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_headed_fit_reader`

```text
---- Summary ----
Helper function to read a fit file in the layout with heading lines (DATA_FORMAT.md,
"fit csv") and bring it to the standard scale, the way up the decomposition uses
and the haem names in figure form.

---- Inputs ----
lines : List[str]
    The lines of the file; the first holds FIT_FILE_MARK.
label : str
    Name of the fit file, used in the messages.

---- Globals read ----
FIT_UNITS, FIT_WAY_UP, FIT_PEAK_BAND (module constants).

---- Outputs ----
Tuple[pd.DataFrame, float, List[str]]
    (the cleaned table, as _fit_table_cleaner gives it, on the standard scale with
    each haem's name in figure form; what the values of the file were divided by;
    the notes for the user). Raises ValueError, with a message for the user, when
    the Unit line is missing or names no fit unit, the Way up line is not one of
    the two ways, the row under the haem names does not say what the columns
    hold, or the table cannot be read.

---- Globals mutated ----
None.

---- Equations ----
response = value of the file x way-up sign (+1, or -1 for 'reduced minus
oxidised') / divisor of the unit (FIT_UNITS). A file with no Way up line is used
as it is written.

---- Helpers ----
_fit_heading_reader
_fit_table_cleaner
_fit_unit_finder
haem_name_typesetter
```

#### `_number_column_reader`

```text
---- Summary ----
Helper function to read one column of a fit file as numbers.

---- Inputs ----
column : pd.Series
    The column as read from the file; row i is row i + first_row of the file.
haem : str
    Name of the haem the column belongs to, used in the message.
kind : str
    'wavelength' or 'response', used in the message.
label : str
    Name of the fit file, used in the message.
first_row : int
    Row of the file that holds row 0 of the column (counted from 1).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The numbers, shape (n_rows), NaN where the cell is empty. Raises ValueError,
    with a message for the user, for a cell that holds anything but a number.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_preset_reader`

```text
---- Summary ----
Helper function to read the names of the library files a preset lists.

---- Inputs ----
path : Path
    Preset file (DATA_FORMAT.md, "preset csv").

---- Globals read ----
PRESET_FILE_MARK, PRESET_FILE_FORMAT (module constants).

---- Outputs ----
List[str]
    The file names, in the order the preset lists them. Raises ValueError, with a
    message for the user, when the file cannot be read, is not a preset, is of a
    newer format, or lists no file.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None. The heading lines end at the first empty line; the first line after it is
the column name, and each line below names one file in its first cell.

---- Helpers ----
None.
```

#### `_unit_scaler`

```text
---- Summary ----
Helper function to scale one background shape to run from 0 to 1.

---- Inputs ----
values : np.ndarray
    The shape at each wavelength, shape (n_wavelengths).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The scaled shape, same shape; all 0 when the values do not change (one
    wavelength), and empty when there are none, so that the solver can say there
    are too few wavelengths.

---- Globals mutated ----
None.

---- Equations ----
scaled = (values - min) / (max - min).

---- Helpers ----
None.
```

#### `_wavelength_masker`

```text
---- Summary ----
Helper function to select the wavelengths inside the range shared by all fits.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the spectrum (nm).
fit_data : pd.DataFrame
    Fit table from fit_importer.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Boolean mask, True inside the shared range. Raises ValueError, with a message
    for the user, when a haem of the fit has no rows.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
fit_range_finder
```

### MAIN FUNCTIONS

#### `answers_fit_loader`

```text
---- Summary ----
Main function to load the fit the answers name: the library haems ticked in the
strip when the fit is OWN_HAEMS_NAME, otherwise the preset or fit file of that name.

---- Inputs ----
fits_folder : Path
    The fits folder, holding the haems and presets folders and the user's own fit
    files.
fit_file : str
    The answer 'fit_file': OWN_HAEMS_NAME, or a name as fit_names_lister gives it.
haem_files : Sequence[str]
    The answer 'haem_files': the library file names ticked; used only with
    OWN_HAEMS_NAME.

---- Globals read ----
HAEMS_FOLDER_NAME, OWN_HAEMS_NAME (module constants).

---- Outputs ----
Dict[str, Any]
    Fit dictionary, as fit_loader or haem_files_combiner gives it. Raises
    ValueError, with a message for the user, when it cannot be loaded (no haem
    ticked, a ticked file missing, or the fit unreadable).

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None.

---- Helpers ----
fit_loader
haem_files_combiner
```

#### `background_builder`

```text
---- Summary ----
Main function to build the background terms that a haem decomposition fits beside
its shapes: a flat level and the shapes of the chosen background.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the spectra (nm), shape (n_wavelengths).
background : str
    Name of the background, a key of BACKGROUND_LABELS.

---- Globals read ----
BACKGROUND_LABELS (module constant).

---- Outputs ----
np.ndarray
    The terms as columns, shape (n_wavelengths, n_terms): the flat 1 first, then
    the shapes, each running from 0 to 1 over the wavelengths. Raises ValueError,
    with a message for the user, for a background the program does not know.

---- Globals mutated ----
None.

---- Equations ----
scatter_1: 1, 1/wl; scatter_2: 1, 1/wl, 1/wl^2 (scatter_background_builder);
linear: 1, wl; rowan_scatter: 1, wl, (wl - centre)^2 with the centre halfway
between the shortest and the longest wavelength; valencia: 1, 1/wl^2. Scaling a
shape to run from 0 to 1 changes only the size of its amount, not the fit.

---- Helpers ----
_unit_scaler
scatter_background_builder
```

#### `basis_solver`

```text
---- Summary ----
Main function to find how much of each column of a basis (the shapes and the
background terms) is in one spectrum, or in each spectrum of a run. It is the one
solver of every decomposition in the program.

---- Inputs ----
basis : np.ndarray
    The shapes to fit as columns, shape (n_wavelengths, n_components).
spectra : np.ndarray
    One spectrum, shape (n_wavelengths), or a run of them, shape (n_spectra,
    n_wavelengths), on the wavelengths of the basis.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The amounts, shape (n_components) for one spectrum or (n_spectra,
    n_components) for a run. A spectrum holding a blank value gives blank amounts
    for that spectrum only. Raises ValueError, with a message for the user, when
    there are fewer wavelengths than components or when the columns cannot be told
    apart.

---- Globals mutated ----
None.

---- Equations ----
Least squares: the c that makes |B c - a| smallest. Each column of B is first
divided by its length (root of its summed squares), so shapes on very different
scales are solved equally well; B_scaled = U S V^T (singular value decomposition);
c = V S^-1 U^T a / column length. S^T S is never inverted, as that squares the
rounding errors.

---- Helpers ----
None.
```

#### `data_filterer`

```text
---- Summary ----
Main function to restrict experimental data to the wavelength range shared by all
fits.

---- Inputs ----
experimental_data : np.ndarray
    Array of (wavelength, value) rows, shape (n_wavelengths, 2).
fit_data : pd.DataFrame
    Fit table from fit_importer.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The rows inside the shared range.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_wavelength_masker
```

#### `decomposition_gap_calculator`

```text
---- Summary ----
Main function to say how far apart the haem traces of two decompositions of the
same spectra are: for each haem in both, the largest gap and the average gap. The
spectra are matched by their index, and a haem is matched by its plain name, so
"Cyt cc" and "cyt c c" are the same haem.

---- Inputs ----
new : pd.DataFrame
    Haem table of the decomposition in use (DATA_FORMAT.md, 'haem_conc' or any
    table made from it), with SPECTRUM_INDEX_COLUMN.
kept : pd.DataFrame
    Haem table of the kept decomposition, of the same kind and units.

---- Globals read ----
SPECTRUM_INDEX_COLUMN.

---- Outputs ----
Dict[str, Tuple[float, float]]
    {haem name as in ``new``: (largest gap, average gap)}, in the units of the
    tables, in the order of ``new``. A haem with no spectrum where both have a
    value is left out. Raises KeyError when a table has no spectrum index.

---- Globals mutated ----
None.

---- Equations ----
gap_i = new_i - kept_i at each spectrum i found in both
largest gap = max |gap_i|
average gap = mean |gap_i|

---- Helpers ----
measurement_column_finder
name_simplifier
value_getter
```

#### `delta_abs_calculator`

```text
---- Summary ----
Main function to shift each haem absorbance so that it is 0 where the haem starts,
giving delta D, the change from the start (mOD). The start of each haem is the
median of its first spectra after the ignored start, so one spike does not set it.

---- Inputs ----
haem_abs : pd.DataFrame
    Haem absorbance table in mOD (time, spectrum index and one column per haem).
exclude_first_minutes : float
    Minutes after the first measurement that are ignored at the start.
window_points : int
    Number of spectra the start is taken from (>= 1).
label : str
    Name used in error messages.
exclude_last_minutes : float
    Minutes before the last measurement that are ignored at the end; the start is
    never taken from them.

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Shifted copy; result.attrs["delta_abs_baseline"] holds {'level_by_haem': the
    level subtracted from each haem (mOD), 'window_by_haem': the (first, last)
    time of the spectra each haem's start was taken from (min), 'window_points',
    'window_seconds': how long that many spectra last}. Raises ValueError, with a
    message for the user, for invalid settings or when fewer than window_points
    spectra are left after the ignored parts.

---- Globals mutated ----
None.

---- Equations ----
delta D = D - D_start, per haem, with D_start = median(D of the first
window_points spectra with a value after the ignored start) (start_level_finder).
Only a constant is subtracted, so differences between points are unchanged.

---- Helpers ----
measurement_column_finder
start_level_finder
time_getter
value_getter
window_seconds_calculator
```

#### `experiment_decomposer`

```text
---- Summary ----
Main function to decompose every spectrum of one dataset into haem concentrations
and absorbances.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
fit : dict
    Fit dictionary from fit_importer (or fit_haem_selector).
dataset_name : str
    Spectral dataset to decompose.
background : str
    Background fitted under the haems, a key of BACKGROUND_LABELS.
haemfactor : float
    Scale factor applied to the haem basis spectra.
delta_exclude_first_minutes : float
    Minutes after the first spectrum that are ignored when finding where each
    haem starts, the 0 of delta D.
delta_window_points : int
    Number of spectra after the ignored start that each haem's start is taken
    from.
spectrum_type : str
    Field of the dataset to decompose, e.g. 'attenuation'.
delta_exclude_last_minutes : float
    Minutes before the last spectrum that are ignored; the start is never taken
    from them.
is_change_from_first : bool
    True fits the change of every spectrum from the first one (the first kept, in
    a trimmed run), as the instrument does; False fits the spectra themselves.

---- Globals read ----
schema.TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError for an invalid fit, dataset
    or background, inconsistent array shapes, or, for the change from the first
    spectrum, a first spectrum with blank values inside the fitted wavelengths.

---- Globals mutated ----
experiment: adds haem_conc (time, spectrum index, one column per haem), haem_abs
(mOD, same layout; attrs["peak_amplitude_OD"]) and haem_delta_abs
(delta_abs_calculator). With is_change_from_first, haem_conc and haem_abs are the
changes from the first spectrum. The three are added together at the end; when
anything fails, the experiment holds none of them, not even those of an earlier
decomposition.

---- Equations ----
a = each spectrum, or each spectrum - the first spectrum; c = the least-squares
amounts of the basis S in a (basis_solver); haem_abs = c x peak amplitude of the
haem basis spectrum x 1000 (OD to mOD); haem_delta_abs = haem_abs - median of the
haem's first spectra after the ignored start. The fit is linear, so with the same
basis the change from the first spectrum gives each amount minus that of the first
spectrum, and the same haem_delta_abs.

---- Helpers ----
_wavelength_masker
basis_solver
delta_abs_calculator
s_array_generator
```

#### `fit_describer`

```text
---- Summary ----
Main function to name the fit in use in words, for the messages and the workbook:
the preset or fit file as it is, or the library haems ticked under Build a fit.

---- Inputs ----
fit_file : str
    The answer 'fit_file'.
haem_files : Sequence[str]
    The answer 'haem_files'; used only when fit_file is OWN_HAEMS_NAME.

---- Globals read ----
OWN_HAEMS_NAME (module constant).

---- Outputs ----
str
    fit_file, or 'Your own haems: c1_myco, bH_bswitch' (the files without .csv).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `fit_file_writer`

```text
---- Summary ----
Main function to save a fit as a fit file in the layout with heading lines
(DATA_FORMAT.md, "fit csv"), which fit_importer reads back as the same fit.

---- Inputs ----
fit : Dict[str, Any]
    Fit dictionary, as fit_importer or fit_table_builder give it: names in figure
    form or plain, the table on the standard scale.
path : Path
    File to write (.csv).
unit : str
    Unit of the values written, one of FIT_UNITS.
holds : str
    What the file holds, in words, for its Holds line.
way_up : Optional[str]
    One of FIT_WAY_UP for a file of haem shapes, which then has a Way up line;
    None for no Way up line (the shapes are written as the decomposition uses them).
notes : Sequence[Tuple[str, str]]
    Further heading lines for people, as (name, text), for example ('Made from',
    'the instrument's fit ...'), written in this order under the Names line.

---- Globals read ----
FIT_FILE_MARK, FIT_FILE_FORMAT, FIT_UNITS, FIT_WAY_UP, FIT_WAY_UP_TEXTS,
FIT_NAMES_TEXT (module constants).

---- Outputs ----
Path
    The file written. Raises ValueError when the unit or the way up is not one
    this module knows, or two haems have the same plain name or one has none.

---- Globals mutated ----
None. Writes the file (side effect).

---- Equations ----
value written = response x divisor of the unit (FIT_UNITS) x way-up sign
(FIT_WAY_UP), to 15 significant digits: a value typed with fewer digits is written
as typed, and any other moves by less than 1e-14 of itself. Rows blank in every
haem are left out, so no leftover rows are written.

---- Helpers ----
haem_name_plainer
```

#### `fit_haem_selector`

```text
---- Summary ----
Main function to keep only some of the haems of a fit, so that a decomposition fits
those alone.

---- Inputs ----
fit : Dict[str, Any]
    Fit dictionary from fit_importer.
haems : List[str]
    Names of the haems to keep, as the fit names them; their order does not matter.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    A new fit dictionary with the same keys: 'haem_list' and 'data' hold only the
    kept haems, in the order of the fit, without the rows that are blank in all of
    them. The fit given is not changed. Raises ValueError, with a message for the
    user, when no haem is named or a name is not in the fit.

---- Globals mutated ----
None.

---- Equations ----
None. The wavelengths a decomposition uses are those shared by the kept haems
(fit_range_finder), so leaving out a short haem can widen them.

---- Helpers ----
None.
```

#### `fit_importer`

```text
---- Summary ----
Main function to import a haem spectral fit CSV, checked and on the standard scale.

---- Inputs ----
filename : Path
    CSV with (wavelength, response) column pairs, one pair per haem, the haem's
    name over its wavelength column; the haems may have different lengths. Either
    in the layout with heading lines (first cell FIT_FILE_MARK, then a Unit line;
    see DATA_FORMAT.md, "fit csv"), or the older layout whose first row is the haem
    names.

---- Globals read ----
FIT_FILE_MARK (module constant).

---- Outputs ----
Dict[str, Any]
    {'haem_list': haem names, the a haems first, then the b, then the c
    (haem_order_finder), 'data': the cleaned table (_fit_table_cleaner) on the
    standard scale, its column pairs in that order, 'scale_divisor': what the values
    of the file were divided by (1, 1 000 or 1 000 000), 'notes': sentences for
    the user about rows left out and the scale}. A file with heading lines gives
    its names in figure form (haem_name_typesetter); an older file gives them as
    written. Raises ValueError, with a message for the user, when the file cannot
    be read as a fit.

---- Globals mutated ----
None. Reads the file (side effect).

---- Equations ----
None.

---- Helpers ----
_fit_table_cleaner
_headed_fit_reader
fit_scale_standardiser
haem_order_finder
```

#### `fit_loader`

```text
---- Summary ----
Main function to load a fit by the name the fit list and the answers give it: the
preset of that name, otherwise the fit file of that name in the fits folder.

---- Inputs ----
fits_folder : Path
    The fits folder, holding the haems and presets folders and the user's own fit
    files.
name : str
    File name of the fit, as fit_names_lister gives it ('<name>.csv').

---- Globals read ----
HAEMS_FOLDER_NAME, PRESETS_FOLDER_NAME (module constants).

---- Outputs ----
Dict[str, Any]
    Fit dictionary, as fit_importer gives it (with 'haem_files' for a preset).
    Raises ValueError, with a message for the user, when there is no such fit or
    it cannot be read.

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None.

---- Helpers ----
fit_importer
preset_importer
```

#### `fit_names_lister`

```text
---- Summary ----
Main function to list the fits offered in the fit question and the settings strip:
the presets, then the user's own fit files.

---- Inputs ----
fits_folder : Path
    The fits folder.

---- Globals read ----
PRESETS_FOLDER_NAME (module constant).

---- Outputs ----
List[str]
    File names ('<name>.csv'): the presets, then the .csv files of the fits folder
    itself, each group sorted without regard to case. A file of the fits folder
    with a preset's name is left out, as the preset is what that name loads (an
    old copy of the fit, kept in the Mac app's Portimao folder). Empty when there
    is nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `fit_range_finder`

```text
---- Summary ----
Main function to find the wavelength range shared by all the haems of a fit: the
only part of a spectrum the decomposition uses.

---- Inputs ----
fit_data : pd.DataFrame
    Fit table from fit_importer.

---- Globals read ----
None.

---- Outputs ----
Tuple[float, float]
    (lowest, highest) wavelength of the shared range (nm). Raises ValueError, with
    a message for the user, when a haem of the fit has no rows.

---- Globals mutated ----
None.

---- Equations ----
lowest = the highest of the haems' first wavelengths; highest = the lowest of
their last wavelengths.

---- Helpers ----
_haem_shape_getter
```

#### `fit_scale_standardiser`

```text
---- Summary ----
Main function to bring a fit table to the standard scale, so that the raw haem
amounts are on the same scale whichever fit is used.

---- Inputs ----
data : pd.DataFrame
    Fit table: (wavelength, response) column pairs, one pair per haem.
label : str
    Name of the fit, used in the notes.

---- Globals read ----
FIT_PEAK_BAND, FIT_LARGE_SCALE (module constants).

---- Outputs ----
Tuple[pd.DataFrame, float, List[str]]
    (the table on the standard scale, what its responses were divided by, the
    notes for the user). A fit a million above the standard is divided by a
    million, with a note; a fit on neither scale is returned unchanged, with a
    warning.

---- Globals mutated ----
None.

---- Equations ----
peak = largest |response| in the table. Standard: low <= peak <= high
(FIT_PEAK_BAND). Large: low x 1e6 <= peak <= high x 1e6, then response = response
/ 1e6. The mOD and % values do not depend on the scale; the raw amounts do.

---- Helpers ----
None.
```

#### `haem_files_combiner`

```text
---- Summary ----
Main function to join library files, one haem each, into one fit, so a
decomposition can use any set of haems of the library.

---- Inputs ----
paths : Sequence[Path]
    The library files (fit csv, one haem each), in any order.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    Fit dictionary with the keys of fit_importer ('haem_list', 'data',
    'scale_divisor', 'notes') and 'haem_files': the file name of each haem, in the
    order of 'haem_list' (the a haems, then the b, then the c). Raises ValueError,
    with a message for the user, when no file is given, a file is missing, cannot
    be read or holds more than one haem, two haems have the same name, or the files
    are on different scales.

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None. Each haem keeps its own rows; shorter haems end in blanks.

---- Helpers ----
fit_importer
haem_name_plainer
haem_order_finder
```

#### `haem_name_plainer`

```text
---- Summary ----
Main function to write a haem name in plain words, without the plotting codes of
its figure form: 'Cyt $b_{557}$' becomes 'Cyt b557'. The reverse of
haem_name_typesetter for the names it makes.

---- Inputs ----
name : str
    Haem name, in figure form or plain.

---- Globals read ----
None.

---- Outputs ----
str
    The name with each $...$ part written without its $, _, { and } signs; a
    name without such a part is returned as it is.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `haem_name_typesetter`

```text
---- Summary ----
Main function to put a plain haem name in the form the figures draw: the haem
letters in italics and a capital letter or number after them below the line, so
'Cyt bH' becomes 'Cyt $b_H$', 'Cyt a605' 'Cyt $a_{605}$' and 'Cyt cc' 'Cyt $cc$'.

---- Inputs ----
name : str
    Plain haem name, words separated by spaces.

---- Globals read ----
HAEM_NAME_WORD (module constant).

---- Outputs ----
str
    The name with each haem word (HAEM_NAME_WORD: one to three of the letters a,
    b, c, d, o, then a capital letter or a number) in figure form; other words,
    such as 'Cyt', 'PC1' or 'a-like', as written.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `library_haems_lister`

```text
---- Summary ----
Main function to list the haems of the library, for the tick boxes of Build a fit
in the strip, reading only the top of each file.

---- Inputs ----
fits_folder : Path
    The fits folder, holding the haems folder.

---- Globals read ----
HAEMS_FOLDER_NAME (module constant); helpers.HAEM_TYPE_ORDER.

---- Outputs ----
List[Dict[str, str]]
    [{'file': file name, 'haem': plain haem name, 'type': 'a', 'b', 'c' or
    'other'}], in the order a, b, c, then by file name ignoring case. A file whose
    top cannot be read is listed under its own name, type 'other', so ticking it
    says what is wrong. Empty when there is no haems folder.

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None.

---- Helpers ----
_fit_heading_reader
haem_name_plainer
haem_type_finder
```

#### `preset_importer`

```text
---- Summary ----
Main function to load a preset: the haem library files it lists, joined into one
fit.

---- Inputs ----
path : Path
    Preset file (DATA_FORMAT.md, "preset csv").
haems_folder : Path
    The haem library folder the listed files are in.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    Fit dictionary, as haem_files_combiner gives it. Raises ValueError, with a
    message for the user, when the preset or one of its files cannot be used.

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
None.

---- Helpers ----
_preset_reader
haem_files_combiner
```

#### `s_array_generator`

```text
---- Summary ----
Main function to generate the haem and background basis components for one
spectrum.

---- Inputs ----
experimental_data : np.ndarray
    Array of (wavelength, value) rows.
fit_data : pd.DataFrame
    Fit table from fit_importer.
background : str
    Background fitted under the haems, a key of BACKGROUND_LABELS.
haemfactor : float
    Scale factor applied to the haem basis spectra.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Basis matrix, shape (n_filtered_wavelengths, n_haems + n_background_terms):
    haem fits (interpolated, times haemfactor), then the terms of the background.

---- Globals mutated ----
None.

---- Equations ----
haem column = interp(fit) x haemfactor; the background terms are those of
background_builder.

---- Helpers ----
_haem_shape_getter
background_builder
data_filterer
```

#### `scatter_background_builder`

```text
---- Summary ----
Main function to build a flat level and the scatter terms 1/wavelength^k: the
scatter backgrounds of the haem decomposition, and what the component finder takes
out of the spectra.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the spectra (nm), shape (n_wavelengths).
degree_of_scatter : int
    Number of 1/wavelength^k scatter terms (>= 0).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    The terms as columns, shape (n_wavelengths, degree_of_scatter + 1): the
    constant 1 first, then scatter term k = 1, 2, ... Each scatter term runs from 1
    at the shortest wavelength to 0 at the longest.

---- Globals mutated ----
None.

---- Equations ----
scatter term k = (1/wl^k - min) / (max - min) of 1/wl^k.

---- Helpers ----
_unit_scaler
```

#### `spectrum_decomposer`

```text
---- Summary ----
Main function to decompose one experimental spectrum into haem contributions and
background.

---- Inputs ----
experimental_data : np.ndarray
    Array of (wavelength, value) rows.
fit_data : pd.DataFrame
    Fit table from fit_importer.
background : str
    Background fitted under the haems, a key of BACKGROUND_LABELS.
haemfactor : float
    Scale factor applied to the haem basis spectra.

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
List[np.ndarray], np.ndarray]
    (c_array, filtered_data, background, background_subtracted, haems,
    haem_individual, residual); the spectra are (wavelength, value) columns.
    c_array holds the haem amounts, then the amounts of the background terms.
    Useful for inspecting one fit; experiment_decomposer uses an equivalent,
    faster route.

---- Globals mutated ----
None.

---- Equations ----
c = the least-squares amounts of the basis S in the spectrum a (basis_solver);
background = the background columns of S x their amounts; residual = a - (haems +
background).

---- Helpers ----
basis_solver
data_filterer
s_array_generator
```

## `utils_shared/survey.py`

Numbered terminal questions of the main program (sections 1 to 5) and the trimming rules.

### SURVEY HELPERS

#### `_columns_text_builder`

```text
---- Summary ----
Helper function to write a figure width in columns, e.g. '1 column' or
'1.5 columns'.

---- Inputs ----
columns : float
    Number of journal columns.

---- Globals read ----
None.

---- Outputs ----
str
    Text such as '2 columns'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_event_line_builder`

```text
---- Summary ----
Helper function to write one event as 'label, time' for the event listings.

---- Inputs ----
event : dict
    Event from the file summary (time in minutes).
entry : dict
    Current label, concentration_uM and ignored flag of that event.

---- Globals read ----
None.

---- Outputs ----
str
    For example '  15.01 min: nd-011992' or with the concentration (in µM, mM or
    M) and '[IGNORED]' when they apply.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
concentration_formatter
```

#### `_first_event_finder`

```text
---- Summary ----
Helper function to find the time of the first event of an experiment.

---- Inputs ----
summary : dict
    Experiment summary with events and duration_min.

---- Globals read ----
None.

---- Outputs ----
float
    First event time in minutes; the duration when there are no events.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_last_event_finder`

```text
---- Summary ----
Helper function to find the time of the last event of an experiment.

---- Inputs ----
summary : dict
    Experiment summary with events.

---- Globals read ----
None.

---- Outputs ----
float
    Last event time in minutes; 0 when there are no events.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_limit_converter`

```text
---- Summary ----
Helper function to turn the minutes a user typed into the value the program keeps
for a trim or ignore limit.

---- Inputs ----
summary : dict
    Experiment summary with duration_min.
kind : str
    'trim' or 'ignore'.
edge : str
    'start' or 'end'.
minutes : float
    Minutes to remove from that edge of the recording; 0 means none.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    Trim limits: the time on the original recording, or None for no trim. Ignore
    limits: the minutes (0.0 for none).

---- Globals mutated ----
None.

---- Equations ----
Trim start = minutes. Trim end = duration - minutes.

---- Helpers ----
None.
```

#### `_limit_maximum_getter`

```text
---- Summary ----
Helper function to find the most minutes that can be trimmed from an edge of a file
without cutting off an event.

---- Inputs ----
summary : dict
    Experiment summary with events and duration_min.
kind : str
    'trim' or 'ignore'.
edge : str
    'start' or 'end'.
so_far : dict
    Limits already asked for this file ({key: value}).

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    Largest accepted number of minutes, or None when there is no limit (ignore).

---- Globals mutated ----
None.

---- Equations ----
Start: the first event time. End: duration - the later of the last event time and
the trim start.

---- Helpers ----
_first_event_finder
_last_event_finder
```

#### `_maths_converter`

```text
    ---- Summary ----
    Helper function to convert the contents of one $...$ maths span to plain text
    with Unicode subscripts and italic letters.

    ---- Inputs ----
    match : re.Match
        Match whose group 1 is the text between the dollar signs.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The converted text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _subscript_stripper
text_italiser
    
```

#### `_minutes_recaller`

```text
---- Summary ----
Helper function to turn a limit remembered from the last run back into the minutes
the question asks for.

---- Inputs ----
summary : dict
    Experiment summary with name and duration_min.
remembered : dict
    {file name: {key: value}} from the last run.
key : str
    'trim_start', 'trim_end', 'ignore_start' or 'ignore_end'.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    Minutes removed from that edge (0.0 when the file was remembered as not
    trimmed there), or None when nothing is remembered for the file.

---- Globals mutated ----
None.

---- Equations ----
Trim end minutes = duration - remembered end time.

---- Helpers ----
None.
```

#### `_natural_sorter`

```text
---- Summary ----
Helper function to build a sort key that puts numbers in numerical order, so
'control_7hours' comes before 'control_24hours'.

---- Inputs ----
name : str
    File or experiment name.

---- Globals read ----
None.

---- Outputs ----
list
    Key of alternating lower-case text and integer parts (text first).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_subscript_stripper`

```text
---- Summary ----
Helper function to turn a matched subscript (_x or _{xy}) into plain text, since
Unicode subscripts are hard to read in a terminal.

---- Inputs ----
match : re.Match
    Match whose group 1 or 2 holds the subscript text.

---- Globals read ----
None.

---- Outputs ----
str
    The subscript text without the underscore.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_tidy_labels_offerer`

```text
---- Summary ----
Helper function to list the event labels that could be written more tidily (8 ug
ml-1 as 8 µg mL⁻¹) beside their tidy forms, and to ask once whether to use them
all. Asks nothing when every label is tidy already or was kept as it is before.

---- Inputs ----
with_events : List[dict]
    File summaries (DATA_FORMAT.md) of the files that have events.
result : Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}; the
    labels are replaced by their tidy forms when the user agrees.
kept : Set[str]
    Labels the user chose to keep as they are; the labels kept this time are
    added, so they are not offered again.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the labels in ``result``, adds to ``kept`` and reads from and prints
to the terminal (side effects).

---- Equations ----
None.

---- Helpers ----
info_printer
tidy_labels_finder
yes_no_asker
```

#### `_trim_minutes_clamper`

```text
---- Summary ----
Helper function to keep the four edges of one file within its limits: no edge below
0 minutes, a trimmed edge never cutting off an event, and the ignored parts inside
the kept part without crossing. When the ignored parts no longer fit, the one on
the side of ``key`` gives way first, so an edge pushed against another stops there.

---- Inputs ----
summary : dict
    Experiment summary with events and duration_min.
minutes : Dict[str, float]
    {trim_start, trim_end, ignore_start, ignore_end} in minutes taken off each edge.
key : str
    The edge just set (one of TRIM_KEYS); its side gives way first.

---- Globals read ----
TRIM_KEYS.

---- Outputs ----
Dict[str, float]
    The minutes kept within the limits; the dictionary given is not changed.

---- Globals mutated ----
None.

---- Equations ----
Kept length = duration - trim start - trim end; the ignore time on the side of
``key`` is at most kept length - the other ignore time.

---- Helpers ----
_limit_maximum_getter
```

### MAIN FUNCTIONS

#### `data_folder_lister`

```text
---- Summary ----
Main function to list the folders directly inside a folder that hold .paf files,
so they can be offered by number.

---- Inputs ----
root : Path
    Folder to look in (the user's own folder, UserPlaces.own_folder).

---- Globals read ----
None.

---- Outputs ----
List[Path]
    The folders with at least one .paf file directly inside, in natural name
    order. Folders whose name starts with a dot or an underscore, and folders that
    cannot be read, are left out.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_natural_sorter
paf_finder
```

#### `data_folder_resolver`

```text
---- Summary ----
Main function to turn the answer to the folder question into a folder: a number or
a name from the list of data folders, or any other path.

---- Inputs ----
text : str
    The answer as typed (or dragged in).
listed : List[Path]
    The data folders offered, in the order they were numbered from 1.

---- Globals read ----
None.

---- Outputs ----
Path
    The listed folder of that number or name (capitals do not matter), otherwise
    the answer as a path. It is not checked to exist.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
path_cleaner
```

#### `decomposition_asker`

```text
---- Summary ----
Main function to ask whether to decompose the spectra into haems and which fit to
use: a fit file, or (when a pca_runner is given) components found from the data
with a principal component analysis.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md); the spectrometers in common are used.
defaults : dict
    Default answers (decompose, fit_file, decomposition_dataset).
fits_folder : Path
    Folder holding the fit .csv files.
forced : bool
    True to skip the yes/no question (a figure that needs the haems was chosen).
depth : int
    Numbering depth of the questions (1 = 3.1, 2 = 3.1.1).
pca_runner : Optional[Callable]
    Function (dataset, depth) that finds the components with a principal component
    analysis and returns (fit file name, fit), or (None, None) when the user wants
    a fit file instead. None leaves the option out.
numbers : Optional[Dict[str, str]]
    The questions' own numbers from QUESTION_FLOW.md, by 'decompose', 'fit' and
    'spectrometer'; None numbers them in the order asked.

---- Globals read ----
PCA_CHOICE (module constant).

---- Outputs ----
tuple
    (decompose, fit_file, fit, dataset). fit is the dictionary from import_fit,
    or None when no decomposition will be done.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
choice_asker
fit_loader
fit_names_lister
info_printer
problem_teller
yes_no_asker
```

#### `delta_psi_asker`

```text
---- Summary ----
Main function to ask whether to work out Δψ, the membrane potential. The question
is asked only when Δψ can be worked out; otherwise the run has no Δψ, and a line
says why when the dataset had it switched on.

---- Inputs ----
answers : dict
    Answers dictionary the value is stored in.
defaults : dict
    Default answers (delta_psi).
haems : List[str]
    Names of the haems of the fit in use.
region_files : List[str]
    Names of the files with both an oxidised and a reduced region.

---- Globals read ----
None.

---- Outputs ----
bool
    True when Δψ is worked out in this run.

---- Globals mutated ----
None. Stores delta_psi in ``answers`` and reads from and prints to the terminal
(side effects).

---- Equations ----
None.

---- Helpers ----
delta_psi_offer_checker
info_printer
yes_no_asker
```

#### `delta_psi_offer_checker`

```text
---- Summary ----
Main function to say whether Δψ can be worked out, and so whether its question is
asked: at least one file has both regions, and the fit has one bH and one bL.

---- Inputs ----
haems : List[str]
    Names of the haems of the fit in use, however they are written.
region_files : List[str]
    Names of the files with both an oxidised and a reduced region.

---- Globals read ----
None.

---- Outputs ----
bool
    True when Δψ can be worked out for at least one file.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
b_haem_column_finder
```

#### `event_asker`

```text
---- Summary ----
Main function to have the label and concentration of every event filled in in the
labels table, starting from the saved or file values, an event being left out by
writing ignore as its label. Labels that could be written more tidily (8 ug ml-1
as 8 µg mL⁻¹) are then offered in their tidy forms, once. Nothing is asked when no
file has events.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
saved : dict
    {file name: OD values and events saved before} (saved_values_reader).
table_filler : Callable[[Dict[str, List[dict]]], Dict[str, List[dict]]]
    Function that shows the labels table filled in with the given events, waits
    until it is confirmed, and returns the events with the labels and
    concentrations typed.
kept : Set[str]
    Labels the user chose to keep as they are; they are not offered in their tidy
    forms again, and the labels kept this time are added.

---- Globals read ----
IGNORE_LABEL.

---- Outputs ----
Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}.
    An event labelled ignore is left out and has no concentration.

---- Globals mutated ----
None. Adds to ``kept`` and reads from and prints to the terminal (side effects).

---- Equations ----
None.

---- Helpers ----
_event_line_builder
_tidy_labels_offerer
event_entries_builder
info_printer
```

#### `event_entries_builder`

```text
---- Summary ----
Main function to give the events of every file as the labels table starts them:
the label, concentration and whether it is left out as saved for the dataset, or
else the file's own text, with no concentration.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
saved : dict
    {file name: OD values and events saved before} (saved_values_reader).

---- Globals read ----
IGNORE_LABEL.

---- Outputs ----
Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}, one
    per event of the file, in its order; an event left out is labelled ignore.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `files_asker`

```text
---- Summary ----
Main function to ask for the folder of .paf files (1.1), offering the data folders
found in the user's own folder, and the results folder (1.2), and to read a summary
of every file and the settings saved with the dataset. A results folder named
without a path is made inside the data folder; one that already holds results of
these files is taken only once the user agrees to write over them (1.2.1), and
otherwise asked again with a free name offered.

---- Inputs ----
last : dict
    Contents of last_answers.json; uses data_folder (the folder used last).
own_folder : Path
    Folder whose data folders are offered by number (UserPlaces.own_folder): the
    program folder from source, the Portimao folder in the home folder in the Mac
    app.

---- Globals read ----
None.

---- Outputs ----
Tuple[Path, List[dict], Path, dict]
    (data folder, summary of each readable file, results folder, settings saved
    with the dataset). Each summary has name, path, duration_min, events and
    datasets; the settings are those of dataset_settings_reader, empty for a
    dataset never saved (DATA_FORMAT.md).

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
data_folder_lister
data_folder_resolver
dataset_settings_reader
experiment_summary_reader
free_folder_finder
info_printer
paf_finder
progress_clearer
progress_printer
results_counter
results_folder_checker
results_folder_resolver
text_asker
yes_no_asker
```

#### `free_folder_finder`

```text
---- Summary ----
Main function to find a folder name beside the one given that is not used yet, by
adding _2, _3 and so on, to offer when the user keeps the results already there.

---- Inputs ----
folder : Path
    The folder whose name is taken (results).

---- Globals read ----
None.

---- Outputs ----
Path
    The first of <folder>_2, <folder>_3, ... that does not exist.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `haem_choice_asker`

```text
---- Summary ----
Main function to ask which haems are plotted, and in which order, when they are
plotted: whether they are is answered by the Haems box of the window's settings
strip, in answers['plot_haems'].

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.
fit : Optional[dict]
    Fit dictionary (haem_list) used to list the haems, or None.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the haems are plotted.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
haem_name_formatter
multi_asker
```

#### `haem_form_option_builder`

```text
---- Summary ----
Helper function to build the (key, label) choices for the 'how to show the
haems' question of the haem and OCR response. The delta D line explains itself in
italics.

---- Inputs ----
include_percent : bool
    True to offer the % oxidised choice: the files asked about have an oxidised
    and a reduced region.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, str]]
    [(key, label), ...]: abs, delta and optionally percent.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
text_italiser
```

#### `haem_name_formatter`

```text
---- Summary ----
Main function to write a haem name for the terminal: the $...$ maths markers are
removed, subscripts are written as plain characters (Unicode subscripts are hard to
read) and the maths part is shown in italics, e.g. 'Cyt $b_H$' becomes 'Cyt bH'.

---- Inputs ----
name : str
    Haem name as written in the fit file.

---- Globals read ----
None.

---- Outputs ----
str
    Name for display only; the original name is still used everywhere else.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_maths_converter
```

#### `label_angle_asker`

```text
---- Summary ----
Main function to ask at what angle the event labels are written.

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the answer in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
number_asker
```

#### `label_tidier`

```text
---- Summary ----
Main function to write the units of an event label the tidy way: u as µ, l as L, a
space between a number and its unit, and exponents raised. Only units are changed;
a name with numbers in it (nd-011992, Q203) and a chemical formula (H2O2) are left
as they are, since the two cannot be told apart.

---- Inputs ----
text : str
    The label as typed or as written in the file.

---- Globals read ----
SUPERSCRIPT_TABLE, UNIT_PATTERN (module constants).

---- Outputs ----
str
    The tidy label, for example '8 µg mL⁻¹ rifampicin' for '8ug ml-1 rifampicin';
    the same text when nothing can be tidied.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `multi_experiment_asker`

```text
---- Summary ----
Main function to ask the multi-experiment plots: the side-by-side figure of two
experiments and the 2x2 figure of four experiments. The 2x2 figure needs the
averaging windows: with none set up it offers the window step of the processing,
and is not made without them; with both kinds set up it asks which it uses.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.
plotted : bool
    True when the individual experiment plots show at least one panel (both
    figures reuse their choices).
figure_checker : Optional[Callable[[str, dict], bool]]
    Function called after the questions of each figure with a name and a dictionary:
    ('comparison', {'comparison': ...}) or ('exemplar', {'exemplar_names': ...}). It
    shows the figure and returns True when the user accepts it. When it returns
    False the figure's questions are asked again with the answers as the defaults.
windows_adder : Optional[Callable[[], bool]]
    Function that runs the window step of the processing (windows_ensurer); None
    when it cannot be run.

---- Globals read ----
None.

---- Outputs ----
tuple
    (comparison, exemplar_names). comparison is {'runs': (left, right),
    'columns', 'height'} or None; exemplar_names is the list of the four
    experiments of the 2x2 figure, or None.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
choice_asker
info_printer
run_name_lister
size_asker
window_kind_asker
windows_ensurer
yes_no_asker
```

#### `ocr_kind_lister`

```text
---- Summary ----
Main function to list the kinds of OCR that can be offered: the OCR itself, the OCR
per OD when OD values were entered, and the OCR as a percentage of its range.

---- Inputs ----
has_od : bool
    True when OD values were entered (scaling by OD is on).

---- Globals read ----
None.

---- Outputs ----
List[str]
    The keys 'raw', 'od' (only with OD values) and 'percent', in the order they are
    offered.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `ocr_option_builder`

```text
---- Summary ----
Helper function to build the (key, label) choices for the OCR questions, using
the units of the plot axes.

---- Inputs ----
keys : List[str]
    OCR kinds offered: 'raw', 'od' and/or 'percent'.

---- Globals read ----
OCR_LABELS (module constant).

---- Outputs ----
List[Tuple[str, str]]
    [(key, label), ...] in the order of ``keys``.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `od_scaling_asker`

```text
---- Summary ----
Main function to ask whether to scale by OD and, if so, have the OD, volume and
dilution factor of every file filled in in the table, starting from the stored
values.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers (normalise_od).
saved : dict
    {file name: OD values and events saved before} (saved_values_reader).
table_filler : Callable[[Dict[str, dict]], Dict[str, dict]]
    Function that shows the OD table filled in with the given rows (od_rows,
    DATA_FORMAT.md), waits until every cell is right, and returns the rows.

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: {'OD', 'volume', 'dilution_factor'}}; the dictionaries are empty
    when not scaling by OD.

---- Globals mutated ----
None. Stores normalise_od in ``answers`` and reads from and prints to the terminal
(side effects).

---- Equations ----
None.

---- Helpers ----
yes_no_asker
```

#### `paf_finder`

```text
---- Summary ----
Helper function to list the .paf files directly inside a folder, by name.

---- Inputs ----
folder : Path
    Existing folder.

---- Globals read ----
None.

---- Outputs ----
List[Path]
    The .paf files, sorted case-insensitively by name.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_natural_sorter
```

#### `results_counter`

```text
---- Summary ----
Main function to count the files that already have results in a results folder:
their own folder there (named as the export names it) holds something.

---- Inputs ----
export_root : Path
    The results folder; it may not exist yet.
summaries : List[dict]
    File summaries (DATA_FORMAT.md); uses 'name'.

---- Globals read ----
None.

---- Outputs ----
int
    How many of the files have results there.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
file_name_sanitiser
```

#### `results_folder_checker`

```text
---- Summary ----
Main function to check the results folder as soon as it is given: it must not be a
file, and it must be a folder that can be saved to. A folder that does not exist yet
is checked at the nearest folder above it that does; nothing is left behind.

---- Inputs ----
text : Optional[str]
    The answer as typed or dragged in (quotes and a leading ~ are allowed).
data_folder : Optional[Path]
    The data folder a name without a path is made in; None for the folder the
    program runs in.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    None when the folder can be used, otherwise the one sentence saying what to
    type instead.

---- Globals mutated ----
None. Makes and removes a temporary file in the nearest existing folder (side
effect).

---- Equations ----
None.

---- Helpers ----
results_folder_resolver
```

#### `results_folder_resolver`

```text
---- Summary ----
Main function to turn the results folder answer into its path: a name or path
without a drive or root (quadratic_scatter_results) is taken inside the data
folder, so a second set of results sits beside the first.

---- Inputs ----
text : str
    The answer as typed or dragged in (quotes and a leading ~ are allowed).
data_folder : Optional[Path]
    The data folder; None leaves such a name to the folder the program runs in.

---- Globals read ----
None.

---- Outputs ----
Path
    The results folder.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
path_cleaner
```

#### `saved_values_reader`

```text
---- Summary ----
Main function to gather the OD values and event labels saved for each file, so they
can be offered as defaults: those in the dataset's settings file, or, for a file
with none there yet, those in its workbook from an earlier run.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
remembered : Dict[str, dict]
    The files part of the dataset's settings (dataset_settings, DATA_FORMAT.md).
export_root : Path
    Results folder, where the workbooks of an earlier run are looked for.

---- Globals read ----
SAVED_VALUE_KEYS (imported constant).

---- Outputs ----
Dict[str, dict]
    {file name: {'OD', 'volume', 'dilution_factor', 'events'} as far as saved, or
    None when nothing is}.

---- Globals mutated ----
None. Prints progress and a note when values come from the workbooks (side
effects).

---- Equations ----
None.

---- Helpers ----
info_printer
progress_clearer
progress_printer
saved_settings_reader
```

#### `signal_asker`

```text
---- Summary ----
Main function to ask whether the oxygen traces and the OCR are plotted, and which
OCR.

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in; must hold normalise_od.
defaults : dict
    Default answers.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the oxygen or the OCR is plotted.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
choice_asker
ocr_kind_lister
ocr_option_builder
yes_no_asker
```

#### `size_asker`

```text
---- Summary ----
Main function to ask the journal, width and height of one figure. Answering None
to the journal question uses Nature with the fallback width and height.

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.
keys : dict
    Names of the answers: {'journal', 'columns', 'height', 'mode'}.
fallback : Tuple[float, float]
    (columns, height) used when the journal is None.
depth : int
    Numbering depth of the journal question.

---- Globals read ----
config.JOURNAL_SPECS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the four answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_columns_text_builder
choice_asker
number_asker
```

#### `temperature_asker`

```text
---- Summary ----
Main function to ask the temperature of the runs, once for the dataset; Δψ is
worked out with it.

---- Inputs ----
answers : dict
    Answers dictionary the value is stored in.
defaults : dict
    Default answers (temperature_c).

---- Globals read ----
TEMPERATURE_LIMITS_C (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores temperature_c (°C) in ``answers`` and reads from and prints to the
terminal (side effects).

---- Equations ----
None.

---- Helpers ----
number_asker
```

#### `tidy_labels_finder`

```text
---- Summary ----
Main function to find the event labels that could be written more tidily (8 ug
ml-1 as 8 µg mL⁻¹), leaving out the events left out and the labels the user chose
to keep as they are.

---- Inputs ----
with_events : List[dict]
    File summaries (DATA_FORMAT.md) of the files that have events.
result : Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}, one
    per event of the summary, in the same order.
kept : Set[str]
    Labels the user chose to keep as they are.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, float, dict, str]]
    (file name, time of the event in min, its entry in ``result``, tidy form) for
    each such label, in the order of the files and events.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
label_tidier
```

#### `trim_layout_finder`

```text
---- Summary ----
Main function to say where the four edges of one file sit on the plot of its whole
recording, with the words by each handle, and which parts are shaded.

---- Inputs ----
summary : dict
    Experiment summary with duration_min.
minutes : Dict[str, float]
    {trim_start, trim_end, ignore_start, ignore_end}: the minutes taken off each
    edge (trim end from the end of the recording, ignore times from the trimmed
    edges), as kept by trim_minutes_setter.

---- Globals read ----
None.

---- Outputs ----
Tuple[List[Tuple[str, float, str, str]], List[Tuple[float, float, str]]]
    (edges, parts): edges as [(key, time_min, words, kind)] with kind 'trim' or
    'ignore', in the order of TRIM_KEYS; parts as [(start_min, end_min, kind)],
    times on the whole recording.

---- Globals mutated ----
None.

---- Equations ----
Kept start = trim start; kept end = duration - trim end; ignore start edge = kept
start + ignore start; ignore end edge = kept end - ignore end.

---- Helpers ----
None.
```

#### `trim_limits_builder`

```text
---- Summary ----
Main function to turn the minutes chosen for every file into the trim and ignore
limits the rest of the program uses and saves.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
minutes : Dict[str, Dict[str, float]]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes taken
    off each edge (trim_minutes_builder).

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: {'trim_start', 'trim_end' (times on the original recording, or None
    for no trim), 'ignore_start', 'ignore_end' (minutes, counted from the trimmed
    edges)}}.

---- Globals mutated ----
None.

---- Equations ----
Trim start = minutes; trim end = duration - minutes.

---- Helpers ----
_limit_converter
```

#### `trim_minutes_builder`

```text
---- Summary ----
Main function to give the minutes each file starts the trimming step with: those
remembered for it, otherwise the standard settings (only the start ignored), kept
within the file's own limits.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
remembered : Dict[str, dict]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} as the limits are
    kept (trim_limits_builder), from the last run or the last time the step was
    answered; a file or key may be missing.

---- Globals read ----
config.DEFAULT_ANSWERS (the minutes ignored at the start); TRIM_KEYS.

---- Outputs ----
Dict[str, Dict[str, float]]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes taken
    off each edge.

---- Globals mutated ----
None.

---- Equations ----
Trim end minutes = duration - remembered end time.

---- Helpers ----
_minutes_recaller
_trim_minutes_clamper
```

#### `trim_minutes_setter`

```text
---- Summary ----
Main function to set one edge of one file to a number of minutes, kept within the
file's limits: a trimmed edge never cuts off an event, and the ignored parts stay
inside the kept part without crossing. When the ignored parts no longer fit, the
one on the side of the edge being set gives way first.

---- Inputs ----
summary : dict
    Experiment summary with events and duration_min.
minutes : Dict[str, float]
    {trim_start, trim_end, ignore_start, ignore_end} of the file, in minutes taken
    off each edge.
key : str
    The edge set: one of TRIM_KEYS.
value : float
    Minutes wanted for it; below 0 counts as 0.

---- Globals read ----
None.

---- Outputs ----
Dict[str, float]
    New minutes of the file; the dictionary given is not changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_trim_minutes_clamper
```

#### `trim_pointer_reader`

```text
---- Summary ----
Main function to turn a time pointed at on the plot of the whole recording into the
minutes that put one edge there, in steps of 0.1 min.

---- Inputs ----
summary : dict
    Experiment summary with duration_min.
minutes : Dict[str, float]
    {trim_start, trim_end, ignore_start, ignore_end} of the file now, in minutes
    taken off each edge; the ignore times count from the trimmed edges.
key : str
    The edge being moved: one of TRIM_KEYS.
time_min : float
    The time pointed at, on the original recording (min).

---- Globals read ----
None.

---- Outputs ----
float
    Minutes for that edge, rounded to 0.1; 0 when the time is beyond the edge.

---- Globals mutated ----
None.

---- Equations ----
Trim start = t. Trim end = duration - t. Ignore start = t - trim start. Ignore end
= (duration - trim end) - t.

---- Helpers ----
None.
```

#### `window_kind_asker`

```text
---- Summary ----
Main function to settle which kind of averaging window a figure uses: the settled
windows (ending before the next addition) or the quick windows (starting after
each addition). It is asked only when both kinds are set up; with one, the figure
uses that one and one line says so.

---- Inputs ----
answers : dict
    Answers dictionary; settled_windows and quick_windows say which kinds are set
    up (windows_ensurer has made sure at least one is).
defaults : dict
    Default answers; holds the kind this figure used last time under ``key``.
key : str
    The answer the kind is stored under: 'ex_window_kind', 'tr_window_kind' or
    'ho_window_kind'.
depth : int
    Depth of the question (how far it is set in).

---- Globals read ----
WINDOW_KIND_OPTIONS (module constant).

---- Outputs ----
str
    'settled' or 'quick'.

---- Globals mutated ----
None. Stores the kind in ``answers``; reads from and prints to the terminal (side
effects).

---- Equations ----
None.

---- Helpers ----
choice_asker
info_printer
```

#### `windows_ensurer`

```text
---- Summary ----
Main function to make sure the averaging windows are set up before the questions
of a figure that needs them. The figure never asks for a window of its own: with
none set up it says so and offers the window step of the processing (4.6), or
carries on without the figure.

---- Inputs ----
answers : dict
    Answers dictionary; averaging says whether the windows are set up.
windows_adder : Optional[Callable[[], bool]]
    Function that runs the window step of the processing, stores what is chosen
    in ``answers`` and returns True when the windows are then set up; None when
    the step cannot be run, so the figure is not made.
depth : int
    Depth of the question (how far it is set in).

---- Globals read ----
None.

---- Outputs ----
bool
    True when the averaging windows are set up, so the figure can be made.

---- Globals mutated ----
None. Reads from and prints to the terminal; the window step stores the windows
in ``answers`` (side effects).

---- Equations ----
None.

---- Helpers ----
info_printer
yes_no_asker
```

## `utils_shared/trimming.py`

Trimming of the start and end of an experiment.

### MAIN FUNCTIONS

#### `experiment_trimmer`

```text
---- Summary ----
Main function to keep only the part of an experiment between a start and an end
time. After a start trim the time axis is re-zeroed so the chosen start becomes 0,
and events keep their original datapoint numbers.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
start_time : Optional[float]
    Start of the part kept, in minutes on the original recording; None keeps the
    start.
end_time : Optional[float]
    End of the part kept, in minutes on the original recording; None keeps the end.

---- Globals read ----
TIME_COLUMN (module constant).

---- Outputs ----
dict
    The same experiment dictionary, trimmed in place. Raises ValueError for an
    invalid time range, events outside the range, no data left, or missing spectrum
    times.

---- Globals mutated ----
None. Trims CcO2, CsO2, VoO2 and the raw spectra, shifts the times of the events
and of the ignored events (one before the new start gets a negative time) and sets
metadata trimmed_before_minutes / trimmed_after_minutes in place (side effects).

---- Equations ----
t_new = t - start_time; rows kept where start_time <= t <= end_time.

---- Helpers ----
None.
```

## `utils_shared/user_notices.py`

One plain sentence for each warning and problem the user meets, with the details of a

### NOTICE HELPERS

#### `_file_namer`

```text
---- Summary ----
Helper function to name the file a file problem is about, without its folders.

---- Inputs ----
error : OSError
    The problem; its filename is None when the system did not say which file.

---- Globals read ----
None.

---- Outputs ----
str
    The file's name, or "A file" when it is not known.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_own_sentence_finder`

```text
---- Summary ----
Helper function to give the message of an error that Portimao's own code raised
with a message of its own, which is written for the user. An error that Python or
a package raised has none: its last step is not a raise statement in one of
Portimao's modules (a failed float() in Portimao's code, for example, is Python's).

---- Inputs ----
error : BaseException
    The problem, with its traceback.

---- Globals read ----
OWN_MODULES, RAISE_OPCODE (module constants).

---- Outputs ----
Optional[str]
    The message, or None when the error is not one of Portimao's own or has no
    text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `problem_describer`

```text
---- Summary ----
Main function to say in plain words what went wrong and what to do, never with
Python's own error text: Portimao's own message when it wrote one, a sentence of
its own for a file that is open elsewhere, missing or unreadable and for a lack of
memory, and otherwise that Portimao met a problem it did not expect, with where the
details are.

---- Inputs ----
error : BaseException
    The problem, with its traceback.
place : str
    Where the details were written, in words (details_writer); empty when they
    could not be written anywhere.

---- Globals read ----
SEND_LOG (module constant).

---- Outputs ----
str
    One or two sentences, ending in a full stop.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_file_namer
_own_sentence_finder
```

#### `problem_shower`

```text
Main function to show a problem as a warning, in plain words, with its details in
the log only. See problem_teller.
```

#### `problem_teller`

```text
---- Summary ----
Main function to write the details of a problem (Python's own report of it) to the
log only, and give the sentence the user sees instead.

---- Inputs ----
lead : str
    What could not be done, for example "Preview not drawn for run1"; it starts the
    sentence and heads the details in the log. Leading spaces are kept in the
    sentence, for the indent of the terminal.
error : BaseException
    The problem, with its traceback.

---- Globals read ----
None.

---- Outputs ----
str
    "<lead>: <what went wrong and what to do>" (problem_describer).

---- Globals mutated ----
None. Writes the details to the log (side effect).

---- Equations ----
None.

---- Helpers ----
details_writer
problem_describer
```

#### `warning_shower`

```text
---- Summary ----
Main function to show a warning: it is printed as it is, and while the window
captures the output of a preview it is also kept as a warning, so the window shows
it under the plot whatever its words.

---- Inputs ----
text : str
    The warning, in plain words; leading spaces indent it in the terminal only.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints the warning and adds it to the capture of the thread, if any (side
effects).

---- Equations ----
None.

---- Helpers ----
captured_buffer_getter
```

## `utils_shared/user_places.py`

Where the program keeps the user's own things: the program folder from source, a folder

### CLASSES

#### `UserPlaces`

```text
---- Summary ----
Where the program's own files are, and where the user's own things are kept: the
fits, the folder used last, the logs and the data folders offered by number.
Detailed structure can be found in DATA_FORMAT.md.
```

### LAUNCH LOG HELPERS

#### `_launch_log_shortener`

```text
---- Summary ----
Helper function to cut the launch log to its newest half once it is bigger than the
limit, from the first start line in that half (or the first whole line when the
half holds none).

---- Inputs ----
path : Path
    The launch log; nothing is done when it is missing.
max_bytes : int
    Size in bytes past which the log is cut.

---- Globals read ----
LAUNCH_LOG_START (module constant).

---- Outputs ----
None
    Nothing. A log that cannot be read or written is left as it is.

---- Globals mutated ----
None. Rewrites the log (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `app_output_logger`

```text
---- Summary ----
Main function to send everything the Mac app prints to logs/launch.log in its own
folder, after the starts before, as the launcher does for a program run from
source. The app has no launcher and no terminal, so without this its messages
would be lost. Run from source, nothing changes.

---- Inputs ----
places : UserPlaces
    Where the user's things are kept (user_places_finder); the logs folder must
    exist (user_folder_preparer).

---- Globals read ----
LAUNCH_LOG_NAME (module constant).

---- Outputs ----
None
    Nothing. A log that cannot be opened leaves the output where it was.

---- Globals mutated ----
_app_log (module state); sys.stdout and sys.stderr are replaced by the log file.

---- Equations ----
None.

---- Helpers ----
launch_log_opener
```

#### `launch_log_opener`

```text
---- Summary ----
Main function to open the launch log for a new start: the starts before are kept
(cut to the newest half once the log passes the limit), and a line with the date
and time marks where this start begins. The launcher and the Mac app both open it
here, so it reads alike.

---- Inputs ----
path : Path
    The launch log (logs/launch.log); its folder is made when missing.
max_bytes : int
    Size in bytes past which the starts before are cut to the newest half.

---- Globals read ----
LAUNCH_LOG_START (module constant).

---- Outputs ----
TextIO
    The log, open for adding text (UTF-8, line by line), its start line already
    written. Raises OSError when it cannot be opened.

---- Globals mutated ----
None. Makes the folder, may cut the log and writes the start line (side effects).

---- Equations ----
None.

---- Helpers ----
_launch_log_shortener
```

#### `user_folder_preparer`

```text
---- Summary ----
Main function to make the Mac app's own folder, with its fits and logs folders, and
to copy in each fit that comes with the program and is not there yet, the haem
library and the presets in their own folders. A fit already there is never
overwritten, so the user's changes are kept. Run from source, nothing is done:
everything stays in the program folder.

---- Inputs ----
places : UserPlaces
    Where the user's things are kept (user_places_finder).

---- Globals read ----
FITS_FOLDER_NAME (module constant).

---- Outputs ----
None
    Nothing. Raises OSError when the folders cannot be made; a fit that cannot be
    copied is left out.

---- Globals mutated ----
None. Makes folders and copies files (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `user_places_finder`

```text
---- Summary ----
Main function to give the places the program uses. Run from source (Windows, Linux,
developers), everything is in the program folder, as it always was. Run as the Mac
app, the program's own files are inside the app, which is never written to, and the
user's things are in a Portimao folder in the home folder.

---- Inputs ----
is_app : Optional[bool]
    True when running as the app; None to find out (the app sets sys.frozen).
home : Optional[Path]
    Home folder; None for the user's own.
program_folder : Optional[Path]
    Folder with the program's own files (fits, assets, QUESTION_FLOW.md); None to
    find it (inside the app, or the folder above utils_shared).

---- Globals read ----
FITS_FOLDER_NAME, LAST_ANSWERS_NAME, LOGS_FOLDER_NAME, OWN_FOLDER_NAME (module
constants); sys.frozen and sys._MEIPASS (set by the app).

---- Outputs ----
UserPlaces
    The places. Nothing is checked or made (user_folder_preparer does that).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_viewer/viewer_edges.py`

Edges dragged on the plot of a file to choose parts of it, such as the trimmed and

### CLASSES

#### `EdgeChoice`

```text
---- Summary ----
What the window needs to let the user choose parts of the plot of every file by
dragging edges, or typing them in the strip: the fields shown, the value of each
field for each file, and the rules of the step that uses it.
Detailed structure can be found in DATA_FORMAT.md.
```

#### `EdgeOverlay`

```text
---- Summary ----
The edges over the plot of the file shown, while a step lets the user choose parts
of the plot with them: the parts are shaded into the picture (see-through, so the
data stays readable), each edge is a line with a handle and its words above the
plot, and the edges entered before are red dashed lines. An edge is dragged by its
handle or its line, and the shading follows the drag without the plot being drawn
again. Every method runs on the window thread, except values_reader.

---- Attributes ----
choice : Optional[EdgeChoice]
    The choice being made, or None while there is none.
values : Dict[str, Dict[str, float]]
    {file name: {field: value}} as the user has set them so far; replaced, never
    changed in place, at each change.
is_every_file : bool
    True: a moved or typed edge moves on every file; False: on the file shown only.

---- Globals read ----
The module constants.

---- Methods ----
__init__
_edges_drawer
_picture_shader
_update_runner
_values_changer
choice_setter
field_setter
hit_layout_finder
hover_handler
is_on
key_teller
motion_handler
picture_placer
press_handler
release_handler
values_reader
```

##### `__init__`

```text
---- Summary ----
Method to set up the overlay, with no choice being made.

---- Inputs ----
tk : Any
    The tkinter module.
canvas : Any
    The Tk canvas the plot is shown on.
family : str
    Font family of the words by the handles.
on_change : Callable[[], None]
    Called after every change of the values, so the window can show them.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_edges_drawer`

```text
---- Summary ----
Method to draw the edges of the file shown over its picture: the edges entered
before as red dashed lines, then each edge as a line from its handle above the
plot to the bottom of the panels, with its words beside the handle, towards
the middle of the plot.

---- Inputs ----
None.

---- Globals read ----
PART_STYLES, PREVIOUS_COLOUR, HANDLE_BAND_PX, HANDLE_ROW_PX, HANDLE_SIZE_PX,
EDGE_WIDTH_PX, WORDS_COLOUR.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on the canvas, tagged 'edges' (side effect).

---- Equations ----
None.

---- Helpers ----
minute_x_finder
```

##### `_picture_shader`

```text
---- Summary ----
Method to show the picture of the file shown with its parts shaded, in place of
the picture on the canvas.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the picture on the canvas (side effect).

---- Equations ----
x in the picture = minute_x_finder with the picture at (0, 0).

---- Helpers ----
minute_x_finder
photo_maker
shaded_picture_maker
```

##### `_update_runner`

```text
---- Summary ----
Method to move the edge being dragged to where the mouse last was, at most
every DRAG_PAUSE_MS while the mouse moves.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Moves the edge (side effect).

---- Equations ----
None.

---- Helpers ----
_values_changer
x_minute_finder
```

##### `_values_changer`

```text
---- Summary ----
Method to set one field of the file shown, or of every file, through the rules
of the step, then show the result. When the step has a rule for copying, the
other files get the value that rule gives them from the file shown.

---- Inputs ----
key : str
    The field set.
value : float
    Its new value, before the rules of each file are applied.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Replaces values, redraws the overlay and tells the window (side
effects).

---- Equations ----
None.

---- Helpers ----
_edges_drawer
_picture_shader
every_file_setter
```

##### `choice_setter`

```text
---- Summary ----
Method to start a choice with its starting values, or end it (None), taking the
edges off the plot.

---- Inputs ----
choice : Optional[EdgeChoice]
    The choice, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Replaces the choice and values and clears the edges (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `field_setter`

```text
---- Summary ----
Method to take a value typed in the strip for one field of the file shown (of
every file when is_every_file).

---- Inputs ----
key : str
    The field typed in.
value : float
    The number typed.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the values and redraws (side effects).

---- Equations ----
None.

---- Helpers ----
_values_changer
```

##### `hit_layout_finder`

```text
---- Summary ----
Method to give where the edges of the file shown sit on the canvas, for
edge_hit_finder.

---- Inputs ----
None.

---- Globals read ----
PART_STYLES, HANDLE_BAND_PX.

---- Outputs ----
Tuple[List[Tuple[str, float, int]], float, Tuple[float, float]]
    ([(key, x in pixels, row of its handle)], top of the handles in pixels,
    (top, bottom) of the panels in pixels).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
minute_x_finder
```

##### `hover_handler`

```text
---- Summary ----
Method to show the mouse as a two-way arrow over an edge it can take.

---- Inputs ----
event : Any
    The Tk motion event.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the cursor of the canvas (side effect).

---- Equations ----
None.

---- Helpers ----
edge_hit_finder
hit_layout_finder
```

##### `is_on`

```text
---- Summary ----
Whether a choice is being made.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    True while a choice is being made.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `key_teller`

```text
---- Summary ----
Method to give the words that explain the colours on the plot.

---- Inputs ----
None.

---- Globals read ----
PREVIOUS_KEY_TEXT.

---- Outputs ----
str
    The key of the choice, with the red dashed lines when they are drawn; empty
    when there is no choice.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `motion_handler`

```text
---- Summary ----
Method to follow the mouse while an edge is dragged; the edge moves at most
every DRAG_PAUSE_MS.

---- Inputs ----
event : Any
    The Tk motion event.

---- Globals read ----
DRAG_PAUSE_MS.

---- Outputs ----
bool
    True when an edge is being dragged (the window then does nothing else
    with the drag).

---- Globals mutated ----
None. Schedules the move (side effect).

---- Equations ----
None.

---- Helpers ----
_update_runner
```

##### `picture_placer`

```text
---- Summary ----
Method to take the picture of a file just put on the canvas, shade it and draw
its edges; with no picture (a message, a figure, a picture without a time
axis) nothing is drawn until the next one.

---- Inputs ----
name : Optional[str]
    Name of the file shown, or None.
picture : Optional[Image.Image]
    The picture at the size shown, without shading.
item : Optional[int]
    The canvas item showing the picture; its picture is replaced.
box : Optional[Tuple[float, float, float, float]]
    (left, top, width, height) of the picture on the canvas, in pixels.
axis : Optional[TimeAxis]
    Where the time axis sits in the picture.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the picture, changes it on the canvas and draws the edges (side
effects).

---- Equations ----
None.

---- Helpers ----
_edges_drawer
_picture_shader
```

##### `press_handler`

```text
---- Summary ----
Method to take the edge under the mouse when the button is pressed.

---- Inputs ----
event : Any
    The Tk click event.

---- Globals read ----
None.

---- Outputs ----
bool
    True when an edge was taken (the window then does nothing else with the
    click).

---- Globals mutated ----
None. Notes the edge taken and redraws the edges (side effects).

---- Equations ----
None.

---- Helpers ----
_edges_drawer
edge_hit_finder
hit_layout_finder
```

##### `release_handler`

```text
---- Summary ----
Method to put the edge being dragged where the button is let go.

---- Inputs ----
event : Any
    The Tk release event.

---- Globals read ----
None.

---- Outputs ----
bool
    True when an edge was being dragged.

---- Globals mutated ----
None. Moves the edge and redraws (side effects).

---- Equations ----
None.

---- Helpers ----
_edges_drawer
_update_runner
```

##### `values_reader`

```text
---- Summary ----
Method to give a copy of the values as they are now; safe to call from the
program thread, as the values are replaced, never changed in place.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Dict[str, float]]
    {file name: {field: value}}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `edge_hit_finder`

```text
---- Summary ----
Main function to find the edge the mouse is on: on its handle, or near its line
between the handles and the bottom of the panels. Where two lines meet, the edge
whose handle is in the lower row (the inner one) is taken; the other is still taken
by its handle.

---- Inputs ----
x : float
    Distance of the mouse from the left of the canvas, in pixels.
y : float
    Distance of the mouse from the top of the canvas, in pixels.
edges : List[Tuple[str, float, int]]
    [(key, x of its line in pixels, row of its handle, 0 the top)].
band_top : float
    Top of the first row of handles, in pixels.
panel : Tuple[float, float]
    (top, bottom) of the panels, in pixels.

---- Globals read ----
GRAB_DISTANCE_PX, HANDLE_ROW_PX, HANDLE_SIZE_PX.

---- Outputs ----
Optional[str]
    The key of the edge, or None when the mouse is on none.

---- Globals mutated ----
None.

---- Equations ----
On a handle: row top <= y <= row top + row height and |x - line| <= half a handle
+ 2 px. On a line: band top <= y <= panel bottom and |x - line| <= grab distance.

---- Helpers ----
None.
```

#### `every_file_setter`

```text
---- Summary ----
Main function to set one field to the same value on some files, each kept within
its own limits by the rules of the step. With a rule for copying, the file shown is
set first, and each other file gets the value the rule gives it from the value the
file shown ended with; a file the rule gives nothing keeps its values.

---- Inputs ----
values : Dict[str, Dict[str, float]]
    {file name: {field: value}} now; not changed.
names : List[str]
    The files to set.
key : str
    The field set.
value : float
    The value wanted, the same for each file.
setter : Callable[[str, Dict[str, float], str, float], Dict[str, float]]
    The rule of the step: (file name, its values, field, value) -> its new values.
shown : Optional[str]
    The file the value was set on; needed only with ``copier``.
copier : Optional[Callable[[str, str, str, float], Optional[float]]]
    The rule for copying: (file shown, other file, field, value on the file
    shown) -> value for the other file, or None to leave that file as it is.
    None (or no file shown): every file gets the same value.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Dict[str, float]]
    New {file name: {field: value}}; the files not named keep their values.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `minute_x_finder`

```text
---- Summary ----
Main function to find where a time falls across the plot area: the inverse of
pointed_time_finder (utils_viewer/viewer_gui.py).

---- Inputs ----
time_min : float
    The time, in minutes on the time axis of the picture.
picture_box : Tuple[float, float, float, float]
    (left, top, width, height) of the picture in the plot area, in pixels.
time_axis : TimeAxis
    Where the time axis sits in the picture, and the times at its ends.

---- Globals read ----
None.

---- Outputs ----
float
    Distance from the left edge of the plot area, in pixels; outside the panels for
    a time outside the axis.

---- Globals mutated ----
None.

---- Equations ----
share = (time - start) / (end - start);
x = left + (axis left + share * (axis right - axis left)) * width.

---- Helpers ----
None.
```

#### `own_value_lister`

```text
---- Summary ----
Main function to list the files whose values differ from those most files have, so
the window can mark them.

---- Inputs ----
values : Dict[str, Dict[str, float]]
    {file name: {field: value}}, every file with the same fields.

---- Globals read ----
None.

---- Outputs ----
List[str]
    The files with a value of their own in any field, in the order given; empty
    for fewer than two files.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `photo_maker`

```text
---- Summary ----
Main function to turn a picture into one Tk can show, quickly enough to follow a
drag: as raw pixels (PPM), or as PNG where this Tk cannot read those.

---- Inputs ----
tk : Any
    The tkinter module.
picture : Image.Image
    The picture, in RGB.

---- Globals read ----
None.

---- Outputs ----
Any
    A tk.PhotoImage of the picture.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `shaded_picture_maker`

```text
---- Summary ----
Main function to shade parts of a picture, see-through so what is under them stays
readable, each in the colour of its kind and hatched where its kind is.

---- Inputs ----
picture : Image.Image
    The picture; not changed.
parts : List[Tuple[float, float, float, float, str]]
    [(left, right, top, bottom, kind)] in pixels of the picture, kind a key of
    PART_STYLES; a part narrower than a pixel is left out.

---- Globals read ----
PART_STYLES, HATCH_SPACING_PX, HATCH_STRENGTH.

---- Outputs ----
Image.Image
    A new RGB picture of the same size.

---- Globals mutated ----
None.

---- Equations ----
Shaded pixel = (1 - strength) * pixel + strength * colour.

---- Helpers ----
None.
```

#### `x_minute_finder`

```text
---- Summary ----
Main function to find the time at a place across the plot area, kept within the
time axis, so an edge dragged past the end of the panels stops at their edge.

---- Inputs ----
x : float
    Distance from the left edge of the plot area, in pixels.
picture_box : Tuple[float, float, float, float]
    (left, top, width, height) of the picture in the plot area, in pixels.
time_axis : TimeAxis
    Where the time axis sits in the picture, and the times at its ends.

---- Globals read ----
None.

---- Outputs ----
float
    The time in minutes, between the times at the two ends of the axis.

---- Globals mutated ----
None.

---- Equations ----
share = ((x - left) / width - axis left) / (axis right - axis left);
time = start + share * (end - start).

---- Helpers ----
None.
```

## `utils_viewer/viewer_gui.py`

The experiment browser window: question terminal on the left, plots on the right.

### CLASSES

#### `GuiUnavailableError`

```text
---- Summary ----
Raised when the browser window cannot be opened (no Tkinter, no display, or a Tk
that draws blank windows); its text says why, and what to do, in plain words.

---- Attributes ----
None.

---- Globals read ----
None.

---- Methods ----
None.
```

#### `ViewerGui`

```text
---- Summary ----
The experiment browser window. The program's questions run in their own thread and
their text and answers pass through the terminal on the left, so the plot on the
right stays usable while a question waits. Previews are drawn by a third thread.

---- Attributes ----
logic_thread : Optional[threading.Thread]
    The thread running the program, whose output belongs in the terminal.
exit_code : int
    What the program returned (1 when it was stopped).
window_errors : List[str]
    The traceback of each error met in the window's own work (its Tk callbacks),
    in order; empty when there was none.

---- Globals read ----
MONO_FONTS and the colour constants (module constants).

---- Methods ----
__init__
_answer_sender
_answer_writer
_axis_box_finder
_band_drawer
_callback_error_keeper
_closing_handler
_confirm_sender
_display_name_lister
_drag_ender
_dragger
_drain_runner
_drawing_sign_drawer
_edges_refresher
_event_handler
_every_file_taker
_file_follower
_history_stepper
_icon_setter
_image_deliverer
_image_receiver
_lock_drawer
_logic_runner
_message_shower
_nav_state_setter
_navigator
_opened_teller
_pane_writer
_picture_shower
_pointer_mover
_resizer
_screen_filler
_step_taker
_strip_change_runner
_strip_change_teller
_symbol_inserter
_table_layout_setter
_time_clicker
_time_line_drawer
_typed_edge_taker
_widgets_builder
_window_raiser
drawing_sign_shower
edges_hider
edges_reader
edges_shower
extra_publisher
input_reader
output_capturer
pictures_publisher
run
session_attacher
spec_publisher
strip_choices_setter
strip_fits_setter
strip_library_setter
strip_listener_setter
strip_reader
strip_setter
strip_state_setter
table_hider
table_reader
table_shower
text_sender
time_reader_setter
window_closer
```

##### `__init__`

```text
---- Summary ----
Method to build the window and set up the queues between its threads.

---- Inputs ----
tk : Any
    The tkinter module.
root : Any
    The Tk root window.
program : Callable[[], int]
    The program to run; it asks the questions and returns its exit code.
title : str
    Window title.
close_after_s : Optional[float]
    Seconds after the program finishes when the window closes by itself,
    without asking (the check switch); None leaves it open until the user
    closes it.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance, builds the widgets and has the root
window report its errors to _callback_error_keeper.

---- Equations ----
None.

---- Helpers ----
_callback_error_keeper
_icon_setter
_widgets_builder
```

##### `_answer_sender`

```text
---- Summary ----
Method to pass the typed answer to the question that is waiting for it. While a
table is open the answer box is hidden and Confirm answers instead.

---- Inputs ----
event : Any
    The Tk key event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the answer into the terminal, clears and disables the answer box
and wakes the question thread (side effects).

---- Equations ----
None.

---- Helpers ----
_pane_writer
```

##### `_answer_writer`

```text
---- Summary ----
Method to write the answer the mouse gave into the answer box, in place of what
was there; nothing changes when the mouse gave no answer.

---- Inputs ----
value : Optional[float]
    The answer, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the text of the answer box (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_axis_box_finder`

```text
---- Summary ----
Method to find where the panels of the picture shown sit in the plot area.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Optional[Tuple[float, float, float, float]]
    (left, right, top, bottom) of the panels in pixels from the top left of the
    plot area, or None when the picture has no time axis.

---- Globals mutated ----
None.

---- Equations ----
x = picture left + fraction across * picture width;
y = picture top + (1 - fraction up) * picture height.

---- Helpers ----
None.
```

##### `_band_drawer`

```text
---- Summary ----
Method to draw the band of a drag over the panels, from where the drag started
to ``x`` (kept within the time axis), with its length in seconds above it.

---- Inputs ----
x : float
    Where the mouse is, in pixels from the left of the plot area.

---- Globals read ----
POINTER_COLOUR (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on the plot area (side effect).

---- Equations ----
Length (s) = |time at x - time at the start| x 60.

---- Helpers ----
_axis_box_finder
pointed_time_finder
```

##### `_callback_error_keeper`

```text
---- Summary ----
Method that Tk calls when the window's own work (a Tk callback) meets an error:
the traceback is printed as Tk does by default, and kept in window_errors so a
check can tell the window went wrong.

---- Inputs ----
kind : type
    Class of the error.
value : BaseException
    The error.
trace : Any
    Its traceback.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds to window_errors and prints to the error stream (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_closing_handler`

```text
---- Summary ----
Method to close the window. While the program is still running the user is asked
first, and a question that is waiting is ended so the program stops cleanly.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stops the threads and closes the window (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_confirm_sender`

```text
---- Summary ----
Method to answer the instruction waiting on a table: Confirm was clicked, or
Enter or the space bar pressed on it. The program then reads the table.

---- Inputs ----
event : Any
    The Tk mouse or key event (unused).

---- Globals read ----
None.

---- Outputs ----
str
    'break', so Tk does nothing more with the click or key.

---- Globals mutated ----
None. Writes "Confirm" into the terminal and wakes the question thread (side
effects).

---- Equations ----
None.

---- Helpers ----
_pane_writer
```

##### `_display_name_lister`

```text
---- Summary ----
Method to give the names for the drop-down: the experiment files are marked as
locked once the figures built from them are shown, and, while edges are dragged
on the plot, the files whose edges differ from most files are marked.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[str]
    One text per entry of the list.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
own_value_lister
```

##### `_drag_ender`

```text
---- Summary ----
Method to end a drag across the plot: an edge being dragged is put where the
button is let go; otherwise the times where the drag started and ended (kept
within the time axis) are turned into the answer, which is written into the
answer box. The band stays until the answer is sent.

---- Inputs ----
event : Any
    The Tk release event.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the text of the answer box (side effect).

---- Equations ----
None.

---- Helpers ----
_answer_writer
_axis_box_finder
pointed_time_finder
```

##### `_dragger`

```text
---- Summary ----
Method to follow the mouse while the button is held: the time line moves with
it and the edge being dragged follows it; during any other drag, the band is
drawn to it.

---- Inputs ----
event : Any
    The Tk motion event.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on the plot area (side effect).

---- Equations ----
None.

---- Helpers ----
_band_drawer
_pointer_mover
```

##### `_drain_runner`

```text
---- Summary ----
Method that runs on the window thread every few milliseconds and carries out the
messages the other threads have queued, joining consecutive text into one
insert.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the window and schedules itself again (side effects).

---- Equations ----
None.

---- Helpers ----
_event_handler
_pane_writer
```

##### `_drawing_sign_drawer`

```text
---- Summary ----
Method to draw the "Drawing ..." sign in the top left corner of the plot area,
to show that the picture for the latest settings is still being made.

---- Inputs ----
None.

---- Globals read ----
SIGN_BACKGROUND, SIGN_EDGE, SIGN_TEXT (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on the plot area (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_edges_refresher`

```text
---- Summary ----
Method to show where the edges dragged on the plot are: the row of the strip
holds the values of the file shown, and the drop-down marks the files whose
edges differ from most files.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the drop-down and the row (side effects).

---- Equations ----
None.

---- Helpers ----
_display_name_lister
```

##### `_event_handler`

```text
---- Summary ----
Method to carry out one message from the other threads, on the window thread.

---- Inputs ----
event : tuple
    (kind, ...) with kind 'prompt', 'spec', 'session', 'pictures', 'extra',
    'image', 'time', 'edges', 'strip', 'strip_choices', 'strip_fits',
    'strip_library', 'strip_state', 'busy',
    'table_show', 'table_hide', 'closed' or 'finished'. The "Drawing ..."
    sign of 'busy' stays until the next question, preview or picture shown.
    With close_after_s, 'finished' also closes the window after that time.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the window (side effects).

---- Equations ----
None.

---- Helpers ----
_closing_handler
_display_name_lister
_edges_refresher
_hint_chooser
_image_deliverer
_image_receiver
_nav_state_setter
_navigator
_pane_writer
_picture_shower
_table_layout_setter
```

##### `_every_file_taker`

```text
---- Summary ----
Method to take the tick box of a row of the edges. As "Every file": ticked, a
moved or typed edge moves on every file; unticked, on the file shown only. As
the step's own switch (EdgeChoice.switch, or second_switch for the second
row), it sets the field of the switch to 1 or 0 on every file.

---- Inputs ----
is_every_file : bool
    The new state of the tick box.
is_second : bool
    True for the tick box of the second row.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the overlay (side effect).

---- Equations ----
None.

---- Helpers ----
_edges_refresher
```

##### `_file_follower`

```text
---- Summary ----
Method to show on the plot the file whose cell of a table is being typed in,
when another file is shown.

---- Inputs ----
name : str
    Name of the file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the file shown (side effect).

---- Equations ----
None.

---- Helpers ----
_navigator
```

##### `_history_stepper`

```text
---- Summary ----
Method to recall an earlier answer in the answer box with the up and down keys.

---- Inputs ----
step : int
    -1 for the previous answer, +1 for the next one.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the text of the answer box (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_icon_setter`

```text
---- Summary ----
Method to give the window (and so the taskbar or dock) the Portimao icon. A
missing icon file or an unsupported system is ignored.

---- Inputs ----
None.

---- Globals read ----
ICON_PATH (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the window icon (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_image_deliverer`

```text
---- Summary ----
Method to queue a finished preview from the preview thread for the window.

---- Inputs ----
version : int
    Number of the request it was drawn for.
name : str
    File name.
png : Optional[bytes]
    Picture, or None when it could not be drawn.
notes : str
    Warnings, or the reason when there is no picture.
time_axis : Optional[TimeAxis]
    Where the time axis sits in the picture, or None when it has none.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the preview (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_image_receiver`

```text
---- Summary ----
Method to take a finished preview from the renderer and show it if it is the
current file. Previews of older settings are dropped.

---- Inputs ----
version : int
    Number of the request the preview was drawn for.
name : str
    File name.
png : Optional[bytes]
    Picture, or None when it could not be drawn.
notes : str
    Warnings, or the reason when there is no picture.
time_axis : Optional[TimeAxis]
    Where the time axis sits in the picture, or None when it has none.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the preview and may redraw the plot area (side effects).

---- Equations ----
None.

---- Helpers ----
_picture_shower
```

##### `_lock_drawer`

```text
---- Summary ----
Method to draw a small padlock and "Locked" in the corner of the plot area, to
show that this experiment plot is final and cannot be changed any more.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on the plot area (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_logic_runner`

```text
---- Summary ----
Method that runs the program in its own thread and reports when it is done.
When the program stops with a reason, or with a problem, one plain sentence in
the terminal says so; the details of a problem go to the log only.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets exit_code, prints why the program stopped, if it did, and queues the
finished message (side effects).

---- Equations ----
None.

---- Helpers ----
problem_shower
```

##### `_message_shower`

```text
---- Summary ----
Method to replace the plot with a short message.

---- Inputs ----
text : str
    Message to show.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Redraws the plot area (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_nav_state_setter`

```text
---- Summary ----
Method to switch the file selector and arrows on or off.

---- Inputs ----
enabled : bool
    True to allow navigation.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the widget states (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_navigator`

```text
---- Summary ----
Method to make a file the current one and show it.

---- Inputs ----
index : int
    Position of the file in the list.
is_from_user : bool
    True when the user chose it, so the answer box gets the keyboard back
    (not while a table is open: its cells keep it).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Updates the selector, the plot and the renderer's order (side effects).

---- Equations ----
None.

---- Helpers ----
_edges_refresher
_picture_shower
```

##### `_opened_teller`

```text
---- Summary ----
Helper method to tell the launcher that the window is up, by making the file
it named, so its small "Opening Portimao" window closes now.

---- Inputs ----
None.

---- Globals read ----
OPENED_SWITCH (module constant); os.environ[OPENED_SWITCH], set only by the
launcher.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes an empty file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_pane_writer`

```text
---- Summary ----
Method to add text to the terminal, with its colours, overwriting the line when
the text starts with a carriage return (progress messages).

---- Inputs ----
text : str
    Text as printed.
kind : str
    'out' (normal), 'err' (error text) or 'answer' (what the user typed).

---- Globals read ----
ANSWER_COLOUR, ERROR_COLOUR (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds text to the terminal and scrolls it (side effects).

---- Equations ----
None.

---- Helpers ----
ansi_splitter
ansi_style_updater
```

##### `_picture_shower`

```text
---- Summary ----
Method to show the picture of the current file, scaled to fit the plot area, or
say why there is none yet. While edges are dragged on the plot, room is kept
above the picture for their handles, and the overlay shades the picture and
draws them. While the picture for the latest settings is still being made, or
the program is making pictures of its own (drawing_sign_shower), the
"Drawing ..." sign is on the plot (over the previous picture when there is
one). Once the questions about each file are over, a file not drawn with the
last settings says so instead.

---- Inputs ----
None.

---- Globals read ----
NOT_DRAWN_TEXT, HANDLE_BAND_PX (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Redraws the plot area and the status line (side effect).

---- Equations ----
scale = min(width / picture width, (height - handle band) / picture height),
at most 1.5.

---- Helpers ----
_drawing_sign_drawer
_lock_drawer
_message_shower
_time_line_drawer
```

##### `_pointer_mover`

```text
---- Summary ----
Method to note where the mouse is over the plot area and move the time line
there; the line goes when the mouse leaves. Over an edge that can be dragged,
the mouse becomes a two-way arrow.

---- Inputs ----
event : Any
    The Tk motion event, or None when the mouse has left the plot area.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Redraws the time line (side effect).

---- Equations ----
None.

---- Helpers ----
_time_line_drawer
```

##### `_resizer`

```text
---- Summary ----
Method to redraw the picture at the new size once the window has stopped
changing size.

---- Inputs ----
event : Any
    The Tk configure event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Schedules a redraw (side effect).

---- Equations ----
None.

---- Helpers ----
_picture_shower
```

##### `_screen_filler`

```text
---- Summary ----
Helper method to open the window maximised, as its maximise button does, so the
answer box is never off a small screen. Un-maximised, it takes its usual size,
made smaller to fit the screen.

---- Inputs ----
None.

---- Globals read ----
WINDOW_SIZE_PX, MINIMUM_SIZE_PX, SCREEN_MARGIN_PX (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sizes and maximises the window (side effect).

---- Equations ----
size = max(minimum, min(usual, screen - margin)), for the width and the height.

---- Helpers ----
None.
```

##### `_step_taker`

```text
---- Summary ----
Method to move to the next or previous file, looping round at the ends.

---- Inputs ----
step : int
    +1 for the next file, -1 for the previous one.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the current file (side effect).

---- Equations ----
None.

---- Helpers ----
_navigator
```

##### `_strip_change_runner`

```text
---- Summary ----
Method to hand a change made in the settings strip to the function the program
registered, on the program thread while a question waits. What it prints goes
on lines of its own, and the answer prompt is shown again under it.

---- Inputs ----
changes : Dict[str, Any]
    {name: new value} of the strip values that changed.
prompt : Any
    The prompt of the question that waits, shown again after a message.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Calls the registered function, prints and queues the prompt (side
effects).

---- Equations ----
None.

---- Helpers ----
output_capturer
```

##### `_strip_change_teller`

```text
---- Summary ----
Method to pass a change the user made in the settings strip to the program
thread: it joins the typed answers, so a question that waits takes it at once
(input_reader).

---- Inputs ----
changes : Dict[str, Any]
    {name: new value} of the strip values that changed.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the change (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_symbol_inserter`

```text
---- Summary ----
Method to type a symbol (µ, a superscript -1, ...) into the answer box at the
cursor when a question is waiting for an answer, or, while a table is open,
into the cell last typed in.

---- Inputs ----
symbol : str
    The characters to add.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds text to the answer box or the cell (side effect).

---- Equations ----
None.

---- Helpers ----
AnswerTable.symbol_inserter
```

##### `_table_layout_setter`

```text
---- Summary ----
Method to open or close the table on the terminal side. Open, it fills the
terminal side under a few lines of terminal text, which keep the newest lines
in sight and scroll, and Confirm takes the place of the answer box; closed, the
terminal and the answer box are as before.

---- Inputs ----
is_shown : bool
    True to open the table, False to close it.

---- Globals read ----
TABLE_HINT, TABLE_TERMINAL_LINES (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the layout of the terminal side (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_time_clicker`

```text
---- Summary ----
Method to act on a click on the plot of a file: an edge under the mouse is
taken, to be dragged; otherwise, while the question waiting can be answered
with a drag, the drag starts here. Its answer replaces what was in the answer
box, can still be edited, and is accepted with Enter.

---- Inputs ----
event : Any
    The Tk click event.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the text of the answer box or starts a drag (side effects).

---- Equations ----
None.

---- Helpers ----
_band_drawer
pointed_time_finder
```

##### `_time_line_drawer`

```text
---- Summary ----
Method to draw a vertical line over the panels where the mouse is, with the
time it points at beside it. Nothing is drawn when the mouse is off the time
axis or the picture has none.

---- Inputs ----
None.

---- Globals read ----
POINTER_COLOUR (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on the plot area (side effect).

---- Equations ----
The line runs from the top of the first panel to the bottom of the last:
y = picture top + (1 - fraction from the bottom) * picture height.

---- Helpers ----
pointed_time_finder
```

##### `_typed_edge_taker`

```text
---- Summary ----
Method to take a number typed in the edges row: the edge moves there (on every
file when "Every file" is ticked), within the limits of each file, and the row
shows where it went.

---- Inputs ----
key : str
    The field typed in.
value : float
    The number typed.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Moves the edge and redraws (side effects).

---- Equations ----
None.

---- Helpers ----
_edges_refresher
```

##### `_widgets_builder`

```text
---- Summary ----
Method to build the terminal, the answer box with its Help button (greyed out
until the Help box is made), Confirm and the table (both hidden until a table
is asked for) on the left, and the plot with the overlay of its edges, its file
controls, the settings strip and the edges row (hidden until edges are dragged)
on the right.

---- Inputs ----
None.

---- Globals read ----
MONO_FONTS and the colour constants (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Creates the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_answer_sender
_closing_handler
_confirm_sender
_edges_refresher
_every_file_taker
_file_follower
_history_stepper
_message_shower
_nav_state_setter
_navigator
_pointer_mover
_resizer
_screen_filler
_step_taker
_strip_change_teller
_symbol_inserter
_time_clicker
_typed_edge_taker
AnswerTable
EdgeOverlay
EdgeRow
SettingsStrip
```

##### `_window_raiser`

```text
---- Summary ----
Helper method to bring the window to the front with the keyboard in the answer
box. A window started by the launcher otherwise opens behind other windows on
macOS, where the answers typed would go nowhere.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Raises and focuses the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `drawing_sign_shower`

```text
---- Summary ----
Method to put the "Drawing ..." sign on the plot while the program makes
pictures of its own (the combined figures, the components found from the
data). The sign goes when the next picture or preview is shown, or the next
question is asked.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the sign for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `edges_hider`

```text
---- Summary ----
Method to take the edges off the plot and the edges row out of the strip, once
the choice made with them is read. It is called from the question thread.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the change for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `edges_reader`

```text
---- Summary ----
Method to give the values of the edges as the user has set them. It is meant
to be called once the user has answered the instruction given after
edges_shower, which is when the window is sure to hold the choice that was
sent.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Dict[str, float]]
    {file name: {field: value}} (EdgeChoice in DATA_FORMAT.md); empty when no
    choice is being made.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `edges_shower`

```text
---- Summary ----
Method to put edges on the plot of every file, to be dragged, with a row of
typing boxes for them in the strip. It is called from the question thread; the
rules in the choice run on the window thread.

---- Inputs ----
choice : EdgeChoice
    The fields, the starting values and the rules (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the choice for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `extra_publisher`

```text
---- Summary ----
Method to show one more picture, such as the components found by the principal
component analysis, in the selector after the files. The files and the other
extra pictures stay (a picture with the same title is replaced), and the extra
pictures go when the next preview is drawn.

---- Inputs ----
title : str
    Name shown in the selector.
png : bytes
    The picture.
is_shown : bool
    True to switch the window to the picture; False only lists it.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the picture for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `input_reader`

```text
---- Summary ----
Method that replaces the built-in input while the window is open: it shows the
prompt in the terminal and waits for the answer typed in the answer box. A
change made in the settings strip meanwhile is handed to the program's listener
and the question goes on waiting. Other threads still use the real input.

---- Inputs ----
prompt : Any
    The prompt text, for example "   > ".

---- Globals read ----
None.

---- Outputs ----
str
    The typed answer. Raises EOFError when the window is closed.

---- Globals mutated ----
None. Waits for the user and runs the strip listener (side effects).

---- Equations ----
None.

---- Helpers ----
_strip_change_runner
```

##### `output_capturer`

```text
---- Summary ----
Method to capture what the current thread prints (the preview thread), without
touching the terminal or the log file.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Iterator[CapturedOutput]
    The buffer the output is collected in, with the warnings kept apart.

---- Globals mutated ----
None. Captures the output of the current thread (side effect).

---- Equations ----
None.

---- Helpers ----
output_capturer
```

##### `pictures_publisher`

```text
---- Summary ----
Method to show finished pictures (the multi-experiment figures) instead of the
files: the selector then lists the pictures by title.

---- Inputs ----
pictures : List[Tuple[str, bytes]]
    [(title, PNG bytes)] in the order they are listed.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the pictures for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `run`

```text
---- Summary ----
Method to run the program in the window: take over the output streams and the
input, start the program thread, and run the window until it is closed.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
int
    The exit code of the program (1 when the window was closed before it
    finished).

---- Globals mutated ----
None. Replaces sys.stdout, sys.stderr and the built-in input while the window
runs, registers the window with the questions that want a time, and restores
them all afterwards (side effects).

---- Equations ----
None.

---- Helpers ----
_drain_runner
_logic_runner
_opened_teller
_window_raiser
input_reader
text_sender
```

##### `session_attacher`

```text
---- Summary ----
Method to give the window the files of the browser session, which fills the
file selector and starts the preview thread.

---- Inputs ----
session : ViewerSession
    The browser session.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the session for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `spec_publisher`

```text
---- Summary ----
Method to give the window new settings: every file is drawn again with them.

---- Inputs ----
spec : PreviewSpec
    The settings to draw with.
name : Optional[str]
    File to show first, or None to stay on the current file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the settings for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `strip_choices_setter`

```text
---- Summary ----
Method to tell the settings strip what it offers: the spectrometers of its
"Spectra" drop-down, whether % oxidised is in "Haems as", and whether the per
OD boxes are shown.

---- Inputs ----
spectra : List[str]
    The spectrometers every file has.
has_percent : bool
    True when at least one file has both regions.
has_od : bool
    True when OD values were entered.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the choices for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `strip_fits_setter`

```text
---- Summary ----
Method to give the settings strip the fits listed in its drop-down.

---- Inputs ----
names : List[str]
    File names of the fits.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the list for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `strip_library_setter`

```text
---- Summary ----
Method to give the settings strip the library haems it shows a tick box for
under Build a fit.

---- Inputs ----
haems : List[Dict[str, str]]
    The library, as spectral_decomposer.library_haems_lister gives it.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the list for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `strip_listener_setter`

```text
---- Summary ----
Method to register the function that is told what the user changes in the
settings strip, or None to stop listening.

---- Inputs ----
listener : Optional[Callable[[Dict[str, Any]], None]]
    Called with {name: new value} of the values changed at once, on the
    program thread while a question waits (a change made while the program is
    busy is taken when the next question is asked). What it prints shows under
    the question, which then goes on waiting.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the function on the instance (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `strip_reader`

```text
---- Summary ----
Method to give the values the settings strip shows now.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    The strip values (DATA_FORMAT.md).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `strip_setter`

```text
---- Summary ----
Method to show values in the settings strip. The listener is not told, as the
program made the change itself.

---- Inputs ----
values : Dict[str, Any]
    Some or all of the strip values (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Raises ValueError for a value the strip cannot show.

---- Globals mutated ----
None. Queues the values for the window (side effect).

---- Equations ----
None.

---- Helpers ----
strip_values_checker
```

##### `strip_state_setter`

```text
---- Summary ----
Method to let the user change the settings strip, or grey it out while what it
shows is not being used. It starts greyed out.

---- Inputs ----
is_enabled : bool
    True to let the user change it, False to grey it out.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the change for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `table_hider`

```text
---- Summary ----
Method to take the table away again and bring back the answer box. What was
typed can still be read with table_reader.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the change for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `table_reader`

```text
---- Summary ----
Method to give what the table holds. It is meant to be called once Confirm has
been pressed for the instruction given after table_shower, which is when the
table is sure to hold the rows that were sent.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]
    (the values row by row, as AnswerTable.values_reader gives them; the cells
    that cannot be used or are needed and empty, as
    AnswerTable.problems_lister gives them).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
AnswerTable.problems_lister
AnswerTable.values_reader
```

##### `table_shower`

```text
---- Summary ----
Method to open a table on the terminal side, in place of most of the text, with
Confirm in place of the answer box.

---- Inputs ----
table : dict
    The table to show (table_rows, DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the table for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `text_sender`

```text
---- Summary ----
Method to queue text from the program thread for the terminal.

---- Inputs ----
text : str
    Text as printed.
kind : str
    'out' or 'err'.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the text (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `time_reader_setter`

```text
---- Summary ----
Method to say that the question being asked can be answered with the mouse, so
a drag across the plot of a file writes the answer it gives into the answer
box, or that it no longer can. It is called from the question thread.

---- Inputs ----
kind : Optional[str]
    'span' (a drag), or None once the question has its answer.
reader : Optional[Callable]
    Turns the drag into the answer: reader(file name, start_min, end_min); None
    with kind None. It is called on the window thread.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the change for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `window_closer`

```text
---- Summary ----
Method to end the previews when the browser steps are over: the preview thread
is stopped (so it cannot clash with the processing that follows) and the file
controls are switched off. The pictures drawn with the last settings stay; a
file without one says it was not drawn with them.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stops the preview thread and queues the change (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

### GUI HELPERS

#### `_hint_chooser`

```text
---- Summary ----
Helper function to choose the hint shown under the answer box: what the mouse can
do for the question waiting, if anything.

---- Inputs ----
time_kind : Optional[str]
    'span' (a drag gives the answer) or None.
is_edged : bool
    True while edges are dragged on the plot.

---- Globals read ----
ANSWER_HINT, EDGES_HINT, SPAN_HINT (module constants).

---- Outputs ----
str
    The hint.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `active_gui_getter`

```text
---- Summary ----
Main function to give the browser window that is open, if any.

---- Inputs ----
None.

---- Globals read ----
_active_gui (module state).

---- Outputs ----
Optional[ViewerGui]
    The open window, or None when none is open (outside a run).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `gui_runner`

```text
---- Summary ----
Main function to run the whole program inside the browser window, which the program
needs: nothing is run when the window cannot open.

---- Inputs ----
program : Callable[[], int]
    The program; it asks the questions and returns its exit code.
title : str
    Window title.

---- Globals read ----
None.

---- Outputs ----
int
    The exit code of the program. Raises GuiUnavailableError, with the reason in
    plain words, when the window cannot open.

---- Globals mutated ----
None. Opens the window and runs the program (side effects).

---- Equations ----
None.

---- Helpers ----
ViewerGui
window_opener
```

#### `pointed_time_finder`

```text
---- Summary ----
Main function to turn a point of the plot area into the time it points at on the
time axis of the picture shown there.

---- Inputs ----
x : float
    Distance of the point from the left edge of the plot area, in pixels.
y : float
    Distance of the point from the top edge of the plot area, in pixels.
picture_box : Tuple[float, float, float, float]
    (left, top, width, height) of the picture in the plot area, in pixels.
time_axis : TimeAxis
    Where the time axis sits in the picture, and the times at its ends.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    The time in minutes, or None when the point is not over the panels.

---- Globals mutated ----
None.

---- Equations ----
across = (x - left) / width; up = 1 - (y - top) / height;
time = start + (across - axis left) / (axis right - axis left) * (end - start).

---- Helpers ----
None.
```

#### `window_opener`

```text
---- Summary ----
Main function to check that the browser window can open here and open its Tk root
window.

---- Inputs ----
None.

---- Globals read ----
MINIMUM_TK (module constant); os.environ["DISPLAY"] and
os.environ["WAYLAND_DISPLAY"] (on Linux).

---- Outputs ----
Tuple[Any, Any]
    (the tkinter module, the Tk root window). Raises GuiUnavailableError, with the
    reason and what to do in plain words, when the window cannot open.

---- Globals mutated ----
None. On Windows, makes the text sharp and gives the program its own taskbar group;
when Tk will not start, what it said goes to the log (side effects).

---- Equations ----
None.

---- Helpers ----
details_writer
```

## `utils_viewer/viewer_multi.py`

Previews of the multi-experiment figures while their questions are answered.

### MULTI-FIGURE HELPERS

#### `_kept_builder`

```text
---- Summary ----
Helper function to read and process the files a multi-experiment figure needs, the
way the real run does (without plotting or exporting them).

---- Inputs ----
names : List[str]
    Names of the files the figure uses.
customs : Dict[str, dict]
    {file name: {'time_response_group', 'haem_ocr'}} for the summary figures.
answers : dict
    Answers so far, ready to build the figure style from.
fit : Optional[dict]
    Fit dictionary, or None.
context : dict
    {summaries, limits, details, regions, export_root} of the run so far. The
    processed files are kept in it (key '_processed') while one figure is being
    built.

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: {experiment, vo2_source, haem_source, prepared}}, as the run keeps
    them for the special figures.

---- Globals mutated ----
None. Reads the files and prints what the processing says (side effects).

---- Equations ----
None.

---- Helpers ----
preview_info_builder
experiment_data_processor
experiment_preparer
```

#### `_pictures_builder`

```text
---- Summary ----
Helper function to make one multi-experiment figure the way the run will, but hand
the finished figure over as a picture instead of saving files.

---- Inputs ----
kind : str
    'comparison', 'exemplar', 'time_response' or 'haem_ocr'.
payload : dict
    What the questions decided: {'comparison': ...}, {'exemplar_names': ...} or
    {'fit': ..., 'custom': {...}} (see the figure_checker of the askers).
context : dict
    {answers, fit, summaries, limits, details, export_root} of the run so far.
makers : Dict[str, Callable]
    {'comparison': comparison_maker, 'special': special_figures_maker} of main.py.
window : Any
    The browser window, which captures the printed text.

---- Globals read ----
settings.PREVIEW_DPI.

---- Outputs ----
Tuple[List[Tuple[str, bytes]], str]
    ([(title, PNG bytes)], notes). The notes are the warnings shown while the
    figure was made (why it, or a part of it, was not made), one per line, and may
    be empty.

---- Globals mutated ----
None. Reads the files, switches figure saving to preview mode while it runs and
puts it back; the details of a problem go to the log (side effects).

---- Equations ----
None.

---- Helpers ----
_kept_builder
figure_capture_setter
problem_shower
```

### MAIN FUNCTIONS

#### `multi_figure_checker_builder`

```text
---- Summary ----
Main function to build the figure checker the multi-experiment questions call after
each figure: it draws the figure from the data (the "Drawing ..." sign is on the
plot meanwhile), shows it in the browser window and asks whether to accept it.

---- Inputs ----
context : dict
    {answers, fit, summaries, limits, details, export_root} of the run so far. The
    dictionary is read each time, so later changes to it are seen.
makers : Dict[str, Callable]
    {'comparison': comparison_maker, 'special': special_figures_maker} of main.py.

---- Globals read ----
None.

---- Outputs ----
Callable[[str, dict], bool]
    Function (kind, payload) that returns True when the figure is accepted, or when
    it could not be previewed (the questions then carry on). A payload with
    'question' and 'change' is a step of a figure being built, which is asked with
    that wording; without them it is the finished figure.

---- Globals mutated ----
None. The checker reads the files and prints to the terminal (side effects).

---- Equations ----
None.

---- Helpers ----
_pictures_builder
accept_asker
active_gui_getter
info_printer
```

## `utils_viewer/viewer_preview.py`

Processing and drawing of one experiment as a preview figure.

### CLASSES

#### `PreviewSpec`

```text
---- Summary ----
The settings a preview is drawn with: the answers given so far. Every file is drawn
with the same spec, so the files can be compared.
Detailed structure can be found in DATA_FORMAT.md.
```

#### `TimeAxis`

```text
---- Summary ----
Where the time axis shared by the panels sits in a preview picture, and the times at
its two ends, so a point of the picture can be turned into a time.
Detailed structure can be found in DATA_FORMAT.md.
```

#### `ViewerSession`

```text
---- Summary ----
Everything the experiment browser keeps between steps: the files, the window, the
recently read experiments, the fit in use and how to redraw the step being asked.
Detailed structure can be found in DATA_FORMAT.md.
```

### PREVIEW HELPERS

#### `_file_exporter`

```text
---- Summary ----
Helper function to export the imported data of one file, read once: for a trimmed
file the whole recording into the full folder of its results folder, then the data
kept by the trimming (all of it for a file not trimmed) into its results folder,
with the OD values and labels entered. A file that is no longer trimmed loses the
whole recording written for it earlier in this run, as it has nothing called full.

---- Inputs ----
session : ViewerSession
    The browser session (results folder, the whole recordings written so far).
summary : dict
    File summary (DATA_FORMAT.md).
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
details : dict
    {file name: {OD, volume, dilution_factor, events}}; may lack the file.
choice : str
    A key of SPECTRA_BY_EXPORT: 'summary', 'trimmed' or 'all'.
keep_full : bool
    True leaves a whole recording already written in this run as it is (the edges
    changed, and the whole recording does not depend on them).

---- Globals read ----
FULL_FOLDER, SPECTRA_BY_EXPORT (module constants); settings.DEFAULT_ANSWERS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Reads the file, writes or removes the exported files and records the whole
recordings written in session.full_exports (side effects).

---- Equations ----
None.

---- Helpers ----
experiment_data_processor
experiment_trimmer
experiment_workbook_exporter
preview_info_builder
```

#### `_kept_haems_drawer`

```text
---- Summary ----
Helper function to work one file out again with the kept decomposition (its fit,
background, regions and numbers of delta psi, everything else as in use), draw its
haem traces dashed over the haems in use in the same colours, widening a panel a
kept trace would leave, and say how far apart the two are; its delta psi is drawn
the same way over the delta psi in use. Its own warnings are left out, as they
repeat those of the decomposition in use.

---- Inputs ----
session : ViewerSession
    The browser session (files, window, cache).
summary : dict
    File summary (DATA_FORMAT.md).
info : dict
    Per-file information the decomposition in use was worked out with.
answers : dict
    Answers the decomposition in use was worked out with.
kept : dict
    The kept decomposition (DATA_FORMAT.md, kept decomposition).
haem_source : Optional[str]
    Key of HAEM_KEYS the haem panels show.
experiment : dict
    The experiment worked out with the decomposition in use.
axes : list
    Panels of the preview, top to bottom; a haem panel has haem_names.
plot_config : dict
    Plot settings of the preview (HAEM_COLOURS, LINE_WIDTH, HAEM_Y_MIN,
    HAEM_Y_MAX).

---- Globals read ----
settings.Config, HAEM_KEYS, KEY_PREFIX, KEPT_ALPHA, KEPT_DASHES, KEPT_MARGIN.

---- Outputs ----
str
    The notes: a KEY_PREFIX line for the dashed lines, a line with the largest
    and the average gap of each haem in both, and the note of the kept delta psi
    (_kept_psi_drawer) when delta psi is shown; or one sentence saying why the
    kept decomposition is not shown on this file.

---- Globals mutated ----
None. Draws on the haem panels; the details of a problem go to the log (side
effects).

---- Equations ----
The gaps: decomposition_gap_calculator. A widened panel reaches from
min - pad to max + pad of the kept trace outside the ignored parts, with
pad = (max - min) x KEPT_MARGIN, and never shrinks.

---- Helpers ----
_kept_psi_drawer
_loaded_experiment_getter
decomposition_gap_calculator
experiment_data_processor
haem_name_plainer
name_simplifier
problem_teller
```

#### `_kept_psi_drawer`

```text
---- Summary ----
Helper function to draw the delta psi of the kept decomposition dashed and paler
over the delta psi in use, widening the panel where the kept line would leave it,
and say how far apart the two are.

---- Inputs ----
experiment : dict
    The experiment worked out with what is in use.
kept_experiment : dict
    The same file worked out with the kept fit, background, regions and numbers
    of delta psi; it has no 'delta_psi' when the file had no regions then, or the
    kept fit has no bH and bL.
axes : list
    Panels of the preview, top to bottom; the delta psi panel has is_delta_psi.
plot_config : dict
    Plot settings of the preview (DELTA_PSI_COLOUR, LINE_WIDTH).
ignore_start_min : float
    Minutes ignored at the start, left out when the panel is widened.
ignore_end_min : float
    Minutes ignored at the end, left out when the panel is widened.

---- Globals read ----
DELTA_PSI_COLUMN, KEPT_ALPHA, KEPT_DASHES, KEPT_MARGIN.

---- Outputs ----
str
    The note: the largest and the average gap between the two in mV, or one
    sentence saying why no kept delta psi is shown on this file; '' when the
    preview has no delta psi panel.

---- Globals mutated ----
None. Draws on the delta psi panel (side effect).

---- Equations ----
The gaps: decomposition_gap_calculator, over the spectra where both have a value.
The widened panel reaches from min - pad to max + pad of the kept line outside
the ignored parts, with pad = (max - min) x KEPT_MARGIN, and never shrinks.

---- Helpers ----
decomposition_gap_calculator
time_getter
value_getter
```

#### `_loaded_experiment_getter`

```text
---- Summary ----
Helper function to give a fresh copy of an experiment read from its file. The file
is read once and kept for the next previews while it is one of the files nearest
the one shown (kept_file_lister), and read again when the spectra of a dataset are
needed that were not read before.

---- Inputs ----
session : ViewerSession
    The browser session holding the cache.
summary : dict
    File summary (DATA_FORMAT.md).
dataset : Optional[str]
    Spectral dataset needed for the haem decomposition, or None for no spectra.

---- Globals read ----
settings.WINDOW_KEPT_FILES.

---- Outputs ----
dict
    A deep copy of the experiment dictionary, safe to trim and process in place.

---- Globals mutated ----
None. Updates the cache of the session (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_paf_loader
kept_file_lister
```

#### `_overlay_drawer`

```text
---- Summary ----
Helper function to shade the ignored parts of the time axis in amber on every panel
of the preview.

---- Inputs ----
axes : list
    Panels of the preview, top to bottom.
regions : List[Tuple[float, float]]
    [(start_min, end_min)] of the ignored parts; an empty one is left out.

---- Globals read ----
IGNORE_COLOUR (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds shaded regions to the figure (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `preview_info_builder`

```text
---- Summary ----
Helper function to build the per-file information dictionary that
experiment_data_processor needs, from the answers given so far.

---- Inputs ----
summary : dict
    File summary (DATA_FORMAT.md).
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes; may
    lack the file.
details : dict
    {file name: {OD, volume, dilution_factor, events}}; may lack the file.
regions : Optional[dict]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
    times on the original recording (min); None, or a file missing, for none.

---- Globals read ----
None.

---- Outputs ----
dict
    Per-file information (as built in everything_asker).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `import_data_exporter`

```text
---- Summary ----
Main function to export the imported data of every file (or of the files named), so
it can be plotted outside the program: in each file's results folder the workbook
of the data kept by the trimming (the oxygen, OCR, events with their labels, and the
OD values and edges), and for a trimmed file the whole recording in its full folder;
the spectra as csv files beside them if chosen. No haem decomposition, OD scaling
or averaging is applied; the ignored parts are left in.

---- Inputs ----
session : ViewerSession
    The browser session (files, results folder, the whole recordings written).
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
details : dict
    {file name: {OD, volume, dilution_factor, events}} (details_stage_runner).
choice : str
    A key of SPECTRA_BY_EXPORT: 'summary' (the workbooks only), 'trimmed' (and the
    trimmed spectra) or 'all' (and the spectra of the whole recordings too).
names : Optional[List[str]]
    Files to export; None for every file.
keep_full : bool
    True leaves the whole recordings already written in this run as they are.
progress : Optional[Callable[[int, int], None]]
    Function called with (number done, number of files); may be None.

---- Globals read ----
None.

---- Outputs ----
List[str]
    The problems: a file that could not be exported is named in them and left out.

---- Globals mutated ----
None. Reads the files, writes <results>/<file>/<file>.xlsx (and full/ inside it for
a trimmed file, and the spectra), and notes the results folder in session.exported
once something is written (side effects).

---- Equations ----
None.

---- Helpers ----
_file_exporter
problem_teller
```

#### `kept_file_lister`

```text
---- Summary ----
Main function to list the files the window keeps read and draws after each answer:
the file shown, then the nearest ones around the list (the arrows go round it), the
next one before the previous one at the same distance.

---- Inputs ----
current : int
    Position of the file shown in the list of files.
total : int
    Number of files.
count : int
    How many files to list (settings.WINDOW_KEPT_FILES); at least 1.

---- Globals read ----
None.

---- Outputs ----
List[int]
    Positions of the files, nearest first, at most count and at most total.

---- Globals mutated ----
None.

---- Equations ----
Distance of file i = min((i - current) mod total, (current - i) mod total).

---- Helpers ----
None.
```

#### `pca_example_picture_builder`

```text
---- Summary ----
Main function to draw the best and the worst described spectrum of the principal
component analysis as a picture for the plot window, in the default journal style
like the other previews.

---- Inputs ----
examples : dict
    Result of decomposition_example_finder.
names : List[str]
    Name of each component.
types : List[str]
    Haem type of each component (component_classifier).

---- Globals read ----
settings.pca_colour_mapper, settings.PREVIEW_DPI; BROWSING_ANSWERS (module
constant).

---- Outputs ----
bytes
    The picture (PNG).

---- Globals mutated ----
None. Sets the matplotlib rcParams of the figure style (side effect).

---- Equations ----
None.

---- Helpers ----
pca_example_figure_builder
```

#### `pca_picture_builder`

```text
---- Summary ----
Main function to draw the components of the principal component analysis, one
panel each, as a picture for the plot window, in the default journal style like
the other previews.

---- Inputs ----
analysis : dict
    Result of component_finder.
result : dict
    Result of component_builder (the chosen components).
names : List[str]
    Name of each component.
types : List[str]
    Haem type of each component (component_classifier).

---- Globals read ----
settings.HAEM_TYPE_COLOURS, settings.pca_colour_mapper, settings.PREVIEW_DPI;
BROWSING_ANSWERS (module constant).

---- Outputs ----
bytes
    The picture (PNG).

---- Globals mutated ----
None. Sets the matplotlib rcParams of the figure style (side effect).

---- Equations ----
None.

---- Helpers ----
pca_figure_builder
```

#### `pca_spectra_gatherer`

```text
---- Summary ----
Main function to collect, from every file, the spectra the principal component
analysis uses: the part kept after trimming, without the ignored start and end,
cut to the spectral window.

---- Inputs ----
session : ViewerSession
    The browser session (files, window, cache).
dataset : str
    Spectral dataset holding the haem spectra.
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
window : Tuple[float, float]
    (start, end) wavelength to keep, in nm. A little outside it is kept as well so
    the analysis can put every file on one grid.
progress : Optional[Any]
    Function called with (number read, number of files); may be None.

---- Globals read ----
None.

---- Outputs ----
Tuple[List[dict], List[str]]
    ([{'name', 'wavelengths', 'spectra', 'times' (min)}], problems). A file that
    cannot be read or has no spectra left is left out and named in the problems.

---- Globals mutated ----
None. Reads the files (side effect).

---- Equations ----
Spectra kept where ignore_start <= t <= duration - ignore_end after trimming.

---- Helpers ----
_loaded_experiment_getter
experiment_attenuation_adder
experiment_trimmer
preview_info_builder
problem_teller
```

#### `preview_drawer`

```text
---- Summary ----
Main function to show the answers given so far in the window: the window is given
the settings, with the decomposition kept to compare with (session.kept) and the
oxidised and reduced regions (session.regions), and draws every file the user looks at with them. Problems are reported, never raised, so the
questions carry on.

---- Inputs ----
session : ViewerSession
    The browser session (files, window, cache, current file).
answers : dict
    Answers so far; missing keys come from config.DEFAULT_ANSWERS.
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
fit : Optional[dict]
    Fit dictionary from fit_importer, or None.
details : dict
    {file name: {OD, volume, dilution_factor, events}}.
show_trim : bool
    True to draw the whole recording without shading, for the trimming step, where
    the window draws the edges and the shading over it (viewer_edges). False draws
    the trimmed data.
show_ignored : bool
    True to shade the ignored start and end in amber (not with show_trim).
name : Optional[str]
    File to show; None keeps the file being looked at.

---- Globals read ----
None.

---- Outputs ----
bool
    True: the settings were handed to the window, which draws them.

---- Globals mutated ----
None. Draws in the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `preview_figure_builder`

```text
---- Summary ----
Main function to process one file with the answers of a spec and draw it in a new
figure. Problems are reported, never raised.

---- Inputs ----
session : ViewerSession
    The browser session (files, window, cache).
spec : PreviewSpec
    The settings to draw with.
name : str
    Name of the file to draw.

---- Globals read ----
settings.Config, settings.PREVIEW_DPI.

---- Outputs ----
Tuple[Optional[Figure], str]
    (figure, notes). The figure is None when the preview could not be drawn, and
    the notes then say why in one sentence. Otherwise the notes are the warnings
    shown while it was drawn (a skipped step, a missing OD), and the gaps to the
    kept decomposition when one is kept, one per line, and may be empty. A line
    starting with KEY_PREFIX explains the shading or the dashed lines and belongs
    by the controls.

---- Globals mutated ----
None. Sets the matplotlib rcParams of the figure style; the details of a problem
go to the log (side effects). Nothing is printed; the caller decides where the
notes go.

---- Equations ----
None.

---- Helpers ----
_kept_haems_drawer
_loaded_experiment_getter
_overlay_drawer
experiment_data_processor
experiment_plotter
preview_info_builder
problem_teller
time_title_chooser
```

#### `time_axis_finder`

```text
---- Summary ----
Main function to find where the time axis of a drawn preview sits in its picture:
the panels that share the x axis of the first panel. Call it once the figure has
its final layout (after it is saved).

---- Inputs ----
fig : Figure
    The drawn preview figure.

---- Globals read ----
None.

---- Outputs ----
Optional[TimeAxis]
    The place and the range of the time axis, or None when the figure has no panel
    or its axis has no length.

---- Globals mutated ----
None.

---- Equations ----
left, right, bottom, top = the outer edges of the panels, as fractions of the
figure measured from its bottom left corner.

---- Helpers ----
None.
```

#### `time_title_chooser`

```text
---- Summary ----
Main function to choose the time axis title of a file's preview, so the user knows
which time it shows: while trimming the whole recording is drawn, and afterwards 0
is where the kept part starts.

---- Inputs ----
show_trim : bool
    True while trimming (the whole recording is drawn).
trim_start_min : Optional[float]
    Where the kept part of the file starts in the recording, in minutes; None or 0
    when its start is not trimmed.

---- Globals read ----
settings.PREVIEW_TIME_TITLES.

---- Outputs ----
str
    "Time from the trimmed start" for a file trimmed at its start, once trimming is
    over; otherwise "Time in the recording" (the two times are then the same).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_viewer/viewer_renderer.py`

The background thread of the experiment browser window that draws the previews.

### CLASSES

#### `PreviewRenderer`

```text
---- Summary ----
Thread that draws the previews with the latest settings: the file being looked at
first, then the ones beside it (the files the window keeps read), so the arrows lead
to a drawn file. Any other file is drawn when it is looked at, so a big dataset is
not read from disk again after every answer. A newer request makes it drop the work
for the older one.

---- Attributes ----
None public.

---- Globals read ----
settings.PREVIEW_DPI, settings.WINDOW_KEPT_FILES.

---- Methods ----
__init__
_next_picker
_picture_maker
request_setter
run
stopper
wanted_setter
```

##### `__init__`

```text
---- Summary ----
Method to set up the thread (it is started by the caller).

---- Inputs ----
session : ViewerSession
    The browser session (files, cache).
deliver : Callable[[int, str, Optional[bytes], str, Optional[TimeAxis]], None]
    Function called with (version, file name, PNG bytes or None, notes, time
    axis of the picture or None) for each finished preview. It is called from
    this thread.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_next_picker`

```text
---- Summary ----
Method to pick the file to draw next: the nearest one to the file being looked
at, among the files the window keeps read, that has not been drawn with the
current settings. The caller holds the lock.

---- Inputs ----
None.

---- Globals read ----
settings.WINDOW_KEPT_FILES.

---- Outputs ----
Optional[str]
    File name, or None when those files are drawn.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
kept_file_lister
```

##### `_picture_maker`

```text
---- Summary ----
Method to draw one file and turn the figure into a PNG picture.

---- Inputs ----
spec : PreviewSpec
    The settings to draw with.
name : str
    Name of the file.

---- Globals read ----
settings.PREVIEW_DPI.

---- Outputs ----
Tuple[Optional[bytes], str, Optional[TimeAxis]]
    (PNG bytes, notes, time axis); the bytes are None when the preview could
    not be drawn and the notes then say why in one sentence. The time axis says
    where the shared time axis sits in the picture, and is None when there is
    none.

---- Globals mutated ----
None. The details of a problem go to the log (side effect).

---- Equations ----
None.

---- Helpers ----
preview_figure_builder
problem_teller
time_axis_finder
```

##### `request_setter`

```text
---- Summary ----
Method to ask for the files to be drawn again with new settings: the file being
looked at and the ones beside it now, any other when it is looked at.

---- Inputs ----
spec : PreviewSpec
    The new settings.
version : int
    Number of this request; results carry it so old ones can be dropped.
wanted : int
    Index of the file being looked at, which is drawn first.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Replaces the work of the thread (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `run`

```text
---- Summary ----
Method that draws previews until stopped. The name is fixed by the thread
protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Passes each finished preview to the window (side effect).

---- Equations ----
None.

---- Helpers ----
_next_picker
_picture_maker
```

##### `stopper`

```text
---- Summary ----
Method to stop the thread and wait until it has finished its current preview.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stops the thread (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `wanted_setter`

```text
---- Summary ----
Method to say which file is being looked at, so it and the ones beside it are
drawn next if they have not been drawn with the current settings.

---- Inputs ----
wanted : int
    Index of the file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the order of the work (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_viewer/viewer_self_test.py`

The check switch (PORTIMAO_SELF_TEST): opens the window, shows one made-up preview and

### SELF-TEST HELPERS

#### `_computer_describer`

```text
---- Summary ----
Helper function to describe the computer the check runs on: Python, the system and
its chip, Tk and the versions of the main packages.

---- Inputs ----
None.

---- Globals read ----
PACKAGES (module constant).

---- Outputs ----
List[str]
    One line of text per item, for the log.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_made_up_experiment_builder`

```text
---- Summary ----
Helper function to build a made-up experiment as the reader would give it from a
file, with the summary of that file.

---- Inputs ----
None.

---- Globals read ----
ADDITION_TIMES_MIN, DURATION_MIN, MADE_UP_NAME, OCR_LEVELS_UM_PER_MIN, START_O2_UM,
STEP_MIN, TIME_COLUMN (module constants).

---- Outputs ----
Tuple[dict, dict]
    (experiment, experiment_summary), as in DATA_FORMAT.md: a point every 0.05 min
    from 0 to 30 min, additions at 10 and 20 min, the OCR at 6, 9 and then
    1 uM/min, the measured O2 falling from 220 uM at that rate and the set O2 at
    220 uM. No spectra.

---- Globals mutated ----
None.

---- Equations ----
O2(t_i) = O2(0) - sum over j < i of OCR(t_j) x step.

---- Helpers ----
None.
```

#### `_preview_shower`

```text
---- Summary ----
Helper function, run as the program of the window, to draw the made-up experiment
with the preview code of the program and show it in the window for a few seconds.

---- Inputs ----
report : Callable[[str], None]
    Writes one line to the log, the window's terminal and the real terminal.
log_folder : Path
    The logs folder, given as the results folder of the preview (nothing is
    written to it).

---- Globals read ----
settings.DEFAULT_ANSWERS, settings.PREVIEW_DPI; DRAWN_WAIT_S, SHOW_S, SHOWN_MARK
(module constants).

---- Outputs ----
int
    0 when the preview was drawn and handed to the window, 1 otherwise (the reason
    and its traceback are reported).

---- Globals mutated ----
None. Shows the picture in the window and waits (side effects).

---- Equations ----
None.

---- Helpers ----
_made_up_experiment_builder
active_gui_getter
preview_figure_builder
```

### MAIN FUNCTIONS

#### `self_test_runner`

```text
---- Summary ----
Main function to check that the program works on this computer: it opens the
window, shows one made-up preview, closes the window by itself after a few seconds
and says the result. Everything is written to self_test.log in the logs folder as
well as to the terminal.

---- Inputs ----
title : str
    Program name, branch and version (program_title_builder).
places : UserPlaces
    Where the user's things are kept (user_places_finder); the log goes to its logs
    folder, which is the program folder's logs folder when run from source.

---- Globals read ----
CLOSE_AFTER_S, LOG_NAME (module constants).

---- Outputs ----
int
    0 when the check passed, 1 when it failed (the reason is in the log).

---- Globals mutated ----
None. Writes the log, opens and closes the window and prints (side effects).

---- Equations ----
None.

---- Helpers ----
_computer_describer
_preview_shower
ViewerGui
window_opener
```

## `utils_viewer/viewer_stages.py`

The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.

### STAGE HELPERS

#### `_addition_time_lister`

```text
---- Summary ----
Helper function to list the times of the additions of every file on the time axis
of the processing plot, which starts at 0 where the trimmed data starts. Events
marked ignore are left out, as the averaging leaves them out.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md), with the events as the file holds them.
limits : Dict[str, dict]
    Trim and ignore limits of every file; 'trim_start' is on the original
    recording.
details : Dict[str, dict]
    OD values and events of every file (details_stage_runner); an event's
    'ignored' says it was marked ignore.

---- Globals read ----
None.

---- Outputs ----
Dict[str, List[float]]
    {file name: addition times (min), in order}.

---- Globals mutated ----
None.

---- Equations ----
time on the plot = time in the file - trim start.

---- Helpers ----
None.
```

#### `_answers_previewer`

```text
---- Summary ----
Helper function to build the answers used to draw a preview: the raw data while
browsing and trimming, and the processing chosen so far afterwards. The haems and
the OCR are shown as the answers say (the strip under the plot sets them), per OD
only once OD values were entered.

---- Inputs ----
answers : dict
    Answers given so far.
fit : Optional[dict]
    Fit dictionary, used to list the haems to show.
kind : str
    'raw' (O2 and the raw OCR only), 'standard' (the standard plot: O2, the OCR
    and, when a fit is given, every haem of it), 'analysis' (also the averaging
    windows, and the haems only when they are decomposed) or 'final' (exactly as
    the figure will be).
has_od : bool
    True when OD values were entered in this run; without them nothing is per OD,
    whatever the answers say.

---- Globals read ----
BROWSING_ANSWERS (module constant).

---- Outputs ----
dict
    A copy of the answers with the preview settings; ``answers`` is not changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_component_namer`

```text
---- Summary ----
Helper function to ask whether to name the components and, if so, a name for each.
The suggested names follow the haem type each component looks like (a-like,
b-like, c-like, with a number when a type comes again).

---- Inputs ----
result : dict
    Result of component_builder.
types : List[str]
    Haem type of each component (component_classifier).
depth : int
    Numbering depth of the questions.

---- Globals read ----
TYPE_NAMES (pca_fitter constant).

---- Outputs ----
List[str]
    Name of each component: PC1, PC2, ... when the user does not name them. Names
    are not empty, have no commas and are all different.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
text_asker
yes_no_asker
```

#### `_decomposition_storer`

```text
---- Summary ----
Helper function to keep what the fit questions decided as the fit in use, and show
it in the settings strip. A run without haems keeps the name of the last fit, so
the strip still offers it.

---- Inputs ----
session : ViewerSession
    The browser session; its fit is set.
answers : dict
    Answers dictionary (decompose, fit_file, decomposition_dataset are set).
chosen : tuple
    (decompose, fit_file, fit, dataset) as decomposition_asker returns it.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes ``answers`` and the session, and shows the strip (side effects).

---- Equations ----
None.

---- Helpers ----
_strip_shower
```

#### `_export_asker`

```text
---- Summary ----
Helper function to ask, at the end of the import, what to export now so it can be
plotted outside the program (nothing, the workbooks, the workbooks and the trimmed
spectra, or the spectra of the whole recordings too, with the size of the spectra
worked out for these files), and to do it. Enter gives nothing. The choice and the
limits exported are kept in the session, so new edges can export again.

---- Inputs ----
session : ViewerSession
    The browser session.
limits : Dict[str, dict]
    Trim and ignore limits of every file.
details : Dict[str, dict]
    OD values and events of every file, as entered in section 3.

---- Globals read ----
WARNING_COLOUR (module constant); settings.SPECTRA_CSV_BYTES.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Reads from and prints to the terminal, writes the files and sets
session.export_choice and session.export_limits (side effects).

---- Equations ----
None.

---- Helpers ----
choice_asker
import_data_exporter
info_printer
progress_clearer
progress_printer
size_describer
spectra_size_estimator
text_colourer
```

#### `_export_refresher`

```text
---- Summary ----
Helper function to export again, with the same choice, the files whose trimmed or
ignored edges changed since the export of the import, so the results folder holds
the edges in use. The whole recording of a file is written only when the file has
just become trimmed, and taken away when it is no longer trimmed. Nothing happens
when nothing was exported in this run.

---- Inputs ----
session : ViewerSession
    The browser session, with the export's choice and limits.
limits : Dict[str, dict]
    Trim and ignore limits of every file, as just accepted.
details : Dict[str, dict]
    OD values and events of every file.

---- Globals read ----
WARNING_COLOUR (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal, writes the files and updates session.export_limits
(side effects).

---- Equations ----
None.

---- Helpers ----
import_data_exporter
info_printer
progress_clearer
progress_printer
text_colourer
```

#### `_figure_starter`

```text
---- Summary ----
Helper function to set the figure of each file from the standard settings or the
ones last saved for the dataset, keeping only what this run allows: the OCR per OD
and the haems scaled by OD only when OD values were entered, the haems in %
oxidised only when a file has both regions (delta D otherwise), and the haems only
when they are decomposed, limited to those of the fit in use (all of them when none
of the saved ones is in it). The Haems box of the settings strip says whether the
haems are worked out and shown, so the figure has them whenever they are decomposed.
How the haems and the OCR are shown, the journal and the size are left as the
answers hold them, which the settings strip may have changed.

---- Inputs ----
answers : dict
    Answers dictionary the figure settings are stored in; must hold normalise_od,
    decompose, ocr_mode, haem_mode and haem_per_od.
defaults : dict
    The standard or saved answers (plot_o2, plot_ocr, haems, event_label_angle).
fit : Optional[dict]
    Fit dictionary (haem_list), or None when the haems are not decomposed.
include_percent : bool
    True when at least one file has an oxidised and a reduced region, so the
    haems can be shown in % oxidised.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the figure settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
ocr_kind_lister
```

#### `_fit_file_saver`

```text
---- Summary ----
Helper function to ask whether to keep the components found as a fit file in the
fits folder, so they can be chosen like any other fit in later runs, and to save
them. A preset's name is refused, as the preset is what that name loads.

---- Inputs ----
fit : dict
    Fit dictionary from fit_table_builder.
fits_folder : Path
    Folder holding the fit .csv files.
count : int
    Number of components (used in the suggested file name).
window : Tuple[float, float]
    Spectral window used (nm), also used in the suggested file name.
depth : int
    Numbering depth of the questions.

---- Globals read ----
spectral_decomposer.PRESETS_FOLDER_NAME.

---- Outputs ----
Optional[str]
    Name of the file saved, or None when nothing was saved.

---- Globals mutated ----
None. Reads from and prints to the terminal and writes the fit file (side
effects).

---- Equations ----
None.

---- Helpers ----
file_name_sanitiser
fit_saver
info_printer
problem_teller
text_asker
yes_no_asker
```

#### `_kept_restorer`

```text
---- Summary ----
Helper function to go back to the decomposition kept to compare with: its fit, its
haems ticked, its background, its spectrometer, its numbers of delta psi and the
regions of every file are in use again, and nothing is kept any more. While the
regions are being chosen on the plot they are left as they are, and one sentence
says so.

---- Inputs ----
session : ViewerSession
    The browser session; its kept decomposition (not None) becomes its fit and its
    regions, and is dropped.
answers : dict
    Answers dictionary the kept answers are put back in.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes ``answers`` and the session and prints to the terminal (side
effects).

---- Equations ----
None.

---- Helpers ----
info_printer
```

#### `_label_table_filler`

```text
---- Summary ----
Helper function to have the label and concentration of every event filled in in
the labels table of the window (3.2).

---- Inputs ----
session : ViewerSession
    The browser session, whose window has the table.
entries : Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]} to
    start from (event_entries_builder).

---- Globals read ----
IGNORE_LABEL (imported constant).

---- Outputs ----
Dict[str, List[dict]]
    The events with the labels and concentrations typed.

---- Globals mutated ----
None. Shows and hides the table and reads from and prints to the terminal (side
effects).

---- Equations ----
None.

---- Helpers ----
_table_filler
label_entries_reader
label_table_builder
```

#### `_limits_lister`

```text
---- Summary ----
Helper function to print the trim and ignore limits of every file in one list.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
limits : Dict[str, dict]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
info_printer
```

#### `_od_lister`

```text
---- Summary ----
Helper function to print the OD values entered for every file in one list, so they
can be checked.

---- Inputs ----
details : Dict[str, dict]
    {file name: {OD, volume, dilution_factor, ...}} as od_scaling_asker returns it.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
info_printer
```

#### `_od_table_filler`

```text
---- Summary ----
Helper function to have the OD, volume and dilution of every file filled in in the
OD table of the window (3.1.1).

---- Inputs ----
session : ViewerSession
    The browser session, whose window has the table.
rows : Dict[str, Dict[str, Optional[float]]]
    The rows to start from (od_rows, DATA_FORMAT.md); None leaves a cell empty.

---- Globals read ----
settings.OD_RESUSPENDED_ML.

---- Outputs ----
Dict[str, Dict[str, Optional[float]]]
    The rows as filled in, every value a number above 0.

---- Globals mutated ----
None. Shows and hides the table and reads from and prints to the terminal (side
effects).

---- Equations ----
None.

---- Helpers ----
_table_filler
od_rows_reader
od_table_builder
```

#### `_pca_pictures_publisher`

```text
---- Summary ----
Helper function to put the two PCA pictures in the plot window: the examples of
how the spectra are decomposed (listed only) and the components (shown). The
"Drawing ..." sign is on the plot while they are made.

---- Inputs ----
session : ViewerSession
    The browser session.
analysis : dict
    Result of component_finder.
result : dict
    Result of component_builder.
examples : Optional[dict]
    Result of decomposition_example_finder; None leaves the examples out.
names : List[str]
    Name of each component.
types : List[str]
    Haem type of each component (component_classifier).
depth : int
    Numbering depth of the messages.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. A picture that cannot be drawn is reported, never raised.

---- Globals mutated ----
None. Draws in the plot window (side effect).

---- Equations ----
None.

---- Helpers ----
info_printer
pca_example_picture_builder
pca_picture_builder
problem_teller
```

#### `_region_rules_lister`

```text
---- Summary ----
Helper function to give, for every file, what the edges of its regions are kept
within on the time axis of the processing plot (which starts at 0 where the trimmed
data starts): the used part of the run and the least length of a region.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
limits : Dict[str, dict]
    Trim and ignore limits of every file; the trim times are on the original
    recording, the ignore times are minutes from the trimmed edges.
dataset : Optional[str]
    The spectrometer whose spectra hold the haems; None when it is not known.

---- Globals read ----
settings.REGION_MINIMUM_POINTS.

---- Outputs ----
Dict[str, dict]
    {file name: {'used_span': (first, last) time of the used part (min on the
    plot), 'minimum_min': least length of a region (min), 'shift': trim start
    (min), to add to a time on the plot for the time on the recording}}.

---- Globals mutated ----
None.

---- Equations ----
first = ignore start; last = (trim end - trim start) - ignore end, never before
first. least length = least number of spectra x duration / number of spectra (the
number of time points when the file does not say how many spectra it holds).

---- Helpers ----
None.
```

#### `_regions_chooser`

```text
---- Summary ----
Helper function to run the regions step on the plot of every file: the oxidised and
the reduced region are pulled out on the plot or typed in the strip under it, and
Enter accepts them. With "Every file" ticked, an edge set on the file shown is
copied to every file at the same distance from its nearest addition. Enter with no
region on any file means no regions; when only some files have both, a question
names the others and asks whether to continue without them, and No goes back to
the edges as they were. The regions are then listed, with the files a copy could
not reach.

---- Inputs ----
session : ViewerSession
    The browser session, with the processing plot drawn.
answers : dict
    Answers so far; decomposition_dataset names the spectra the haems come from.
limits : Dict[str, dict]
    Trim and ignore limits of every file.
details : Dict[str, dict]
    OD values and events of every file; an edge is copied by the additions not
    ignored there.
remembered : Optional[Dict[str, Dict[str, float]]]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
    times on the original recording (min), which the edges start at; None, or a
    file missing, for regions not chosen.

---- Globals read ----
REGION_FIELDS, REGION_KEY_TEXT, REGION_NUDGE (module constants).

---- Outputs ----
Dict[str, Dict[str, float]]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
    times on the original recording (min), so a later change of the trim leaves
    them on the same data. A region not chosen, or too short to count, has its two
    edges together.

---- Globals mutated ----
None. Reads from and prints to the terminal and draws on the plot window (side
effects).

---- Equations ----
time on the recording = time on the plot + trim start.

---- Helpers ----
_addition_time_lister
_region_rules_lister
_regions_lister
enter_waiter
info_printer
region_edge_copier
region_edge_setter
region_edges_builder
region_layout_finder
region_pointer_reader
region_span_reader
short_region_closer
yes_no_asker
EdgeChoice
```

#### `_regions_lister`

```text
---- Summary ----
Helper function to print the two regions of every file in one list, then name the
files that kept an edge of their own because they have fewer additions than the
file it was copied from.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
values : Dict[str, Dict[str, float]]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} on
    the time axis of the plot (min).
rules : Dict[str, dict]
    The limits of every file (_region_rules_lister).
unreached : List[str]
    The files a copied edge could not reach.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
info_printer
region_span_reader
warning_shower
```

#### `_standard_fit_loader`

```text
---- Summary ----
Helper function to load the fit the standard plot shows the haems with, before any
question about the haems is asked: the fit last saved for the dataset, or the
standard fit for a dataset never saved. It also loads a fit picked, or haems
ticked, in the settings strip. When the haems cannot be shown, one line says why
and the plot keeps to the oxygen and the OCR.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md); the spectrometers in common are used.
defaults : dict
    Default answers (decompose, fit_file, haem_files, decomposition_dataset).
fits_folder : Path
    Folder holding the fit .csv files.
is_from_strip : bool
    True when the fit was picked in the settings strip: the message then says the
    strip is set back, instead of pointing to the processing.

---- Globals read ----
None.

---- Outputs ----
Tuple[Optional[dict], Optional[str]]
    (fit, spectrometer the haems are read from), or (None, None) when the haems
    are not shown: the dataset was saved without haems, the fit file is missing or
    unreadable, or the files share no spectrometer the fit can be used on.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
answers_fit_loader
fit_names_lister
info_printer
problem_teller
```

#### `_strip_change_applier`

```text
---- Summary ----
Helper function to make a change in the settings strip what the run uses, and
redraw the plot of the step being asked. Unticking the haems leaves them out of the
run; ticking them, picking a fit or ticking library haems under Build a fit works
them out with the fit in the strip; a new background works them out again, and so
does another spectrometer. A new way of showing the haems, or a per OD box, redraws
the plot with it. A number typed in the Δψ row is kept in the answers (the two
filled-in midpoints with it), said in the terminal and Δψ worked out again. A fit
that cannot be used is reported and the strip is set back. Keep to compare keeps
the fit, the background, the regions and the numbers of Δψ in use, drawn dashed
over the haems and over Δψ until one of the two is chosen (Keep this one carries
on with what is on the plot, Go back to kept puts the kept one back in use) or
the haems are left out. A new journal, width or height redraws only the figure of
each file, the one plot drawn at its size.

---- Inputs ----
session : ViewerSession
    The browser session; its fit is changed and its redraw called.
answers : dict
    Answers dictionary the values are stored in.
fits_folder : Path
    Folder holding the fit .csv files.
changes : Dict[str, object]
    {name: new value} of the strip values that changed (DATA_FORMAT.md,
    strip_values).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes ``answers`` and the session, prints to the terminal, shows the strip
and redraws the plot (side effects).

---- Equations ----
None.

---- Helpers ----
_kept_restorer
_standard_fit_loader
_strip_shower
form_answers_builder
info_printer
kept_decomposition_builder
psi_answers_builder
psi_change_describer
size_answers_builder
```

#### `_strip_shower`

```text
---- Summary ----
Helper function to show in the settings strip what the run uses now: the haems
ticked when they are worked out, the fit, the decomposition kept to compare with,
the spectrometer, how the haems and the OCR are shown, the journal and the size.
It also says what the strip offers: the spectrometers every file has, % oxidised
when at least one file has both regions, and the per OD boxes when OD values were
entered. Haems in % oxidised go back to delta D when no file has both regions any
more.

---- Inputs ----
session : ViewerSession
    The browser session (its window, fit, limits, regions and whether OD values
    were entered).
answers : dict
    Answers so far.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. May change haem_mode in ``answers``, and shows the values in the strip
(side effects).

---- Equations ----
None.

---- Helpers ----
region_files_lister
strip_values_builder
```

#### `_table_filler`

```text
---- Summary ----
Helper function to have a table filled in in the window: the table fills the
terminal side, the instruction waits for Confirm, and while a cell is wrong or a
needed cell empty one sentence names those cells and the instruction goes on
waiting. The table is then taken away.

---- Inputs ----
session : ViewerSession
    The browser session, whose window has the table.
table : dict
    The table to show (table_rows, DATA_FORMAT.md).
question : str
    The instruction, ending "then press Confirm.".
note : str
    What the table needs, said above the instruction in the quieter colour.
number : str
    The instruction's own number from QUESTION_FLOW.md, such as '3.2'.

---- Globals read ----
None.

---- Outputs ----
List[Dict[str, Any]]
    The values typed, one {name of the value: value} per row of the table
    (AnswerTable.values_reader).

---- Globals mutated ----
None. Shows and hides the table and reads from and prints to the terminal (side
effects).

---- Equations ----
None.

---- Helpers ----
confirm_waiter
table_problem_teller
```

#### `_unfit_windows_lister`

```text
---- Summary ----
Helper function to name, in plain words, the averaging windows of one file that do
not fit.

---- Inputs ----
spans : List[Tuple[str, float, float, Optional[str]]]
    The baseline and the settled windows of the file, as window_span_lister gives
    them (the baseline alone when there are no settled windows).
quick : List[Tuple[str, float, float, Optional[str]]]
    The quick windows of the file, as quick_span_lister gives them; empty when
    there are none.

---- Globals read ----
None.

---- Outputs ----
List[str]
    One name for each window with a problem: 'the baseline before addition 1',
    'the settled one before addition 3', 'the settled one after the last
    addition', 'the quick one after addition 2'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_windows_chooser`

```text
---- Summary ----
Helper function to run the window step on the plot of every file: the averaging
windows are shaded on the plot. The settled windows (blue) have one length and one
gap before the next addition for every window of every file: pulling the start of
any of them changes the length, pulling its end the gap. The quick windows (green)
have one length and one start after their addition: pulling the start of any of
them changes how long after the addition they start, pulling its end the length.
All four are also typed in the two rows of the strip under the plot, where each
kind has its tick box; with both unticked there are no windows. Enter accepts. The
windows that do not fit are shaded red and named in a warning after Enter. When no
file has an addition, nothing is asked and nothing is averaged.

---- Inputs ----
session : ViewerSession
    The browser session, with the processing plot drawn without windows.
answers : dict
    Answers dictionary the values are stored in; final_gap_minutes is how long
    before the end of the recording the last window ends.
defaults : dict
    Default answers the step starts with (averaging, settled_windows,
    window_minutes, gap_minutes, quick_windows, quick_minutes, delay_minutes).
limits : Dict[str, dict]
    Trim and ignore limits of every file.
details : Dict[str, dict]
    OD values and events of every file; the windows go around the additions not
    ignored there.

---- Globals read ----
QUICK_FIELDS, QUICK_SWITCH, WINDOW_FIELDS, WINDOW_KEY_TEXT, WINDOW_NUDGE,
WINDOW_SWITCH (module constants); settings.BASELINE_MINIMUM_SECONDS,
settings.DRAG_STEP_SECONDS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores averaging (True with either kind ticked), settled_windows,
window_minutes, gap_minutes, quick_windows, quick_minutes and delay_minutes in
``answers``, reads from and prints to the terminal and draws on the plot window
(side effects).

---- Equations ----
minutes = seconds / 60. The data of a file runs from 0 to (trim end - trim start)
on the time axis of the plot.

---- Helpers ----
_addition_time_lister
_unfit_windows_lister
enter_waiter
info_printer
quick_span_lister
warning_shower
window_layout_finder
window_pointer_reader
window_span_lister
window_value_setter
EdgeChoice
```

### MAIN FUNCTIONS

#### `browser_stage_runner`

```text
---- Summary ----
Main function to show the standard plot of the files in the plot window (the set
and measured O2, the OCR and, when the session has a fit, the haems, with the
events as written in the file) before any question is asked about them. The user can
look through them in the window while answering, so the questions carry straight
on.

---- Inputs ----
session : ViewerSession
    The browser session; its redraw is set.
answers : dict
    Answers so far, used for the figure style of the preview.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws the plot window (side effect).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
preview_drawer
```

#### `details_stage_runner`

```text
---- Summary ----
Main function to ask the last questions of the import, on the standard plot cut to
the limits: the OD values, the temperature of the runs, then the event labels, the
OD values and the labels each in a table of the window.
Once OD values are entered, the strip shows its per OD boxes and a line says so.
The plot is redrawn with the labels once they are entered, and they are accepted or
typed again; with no events in any file there is nothing to accept. Last, the
export of what was imported is offered. The haems are those of the session's fit.

---- Inputs ----
session : ViewerSession
    The browser session; its redraw is set.
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers offered by the questions.
limits : Dict[str, dict]
    Trim and ignore limits of every file (trim_stage_runner).
remembered : Dict[str, dict]
    The files part of the dataset's settings, with the OD values and events saved
    before (dataset_settings, DATA_FORMAT.md).
details_before : Optional[Dict[str, dict]]
    OD values and events from an earlier pass, offered as defaults when the step is
    asked again.

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: {'OD', 'volume', 'dilution_factor', 'events'}}; the OD entries are
    only present when scaling by OD.

---- Globals mutated ----
None. Stores normalise_od and temperature_c in ``answers`` and whether OD values
were entered in the
session, shows the strip and writes the export when one is chosen (side effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_export_asker
_label_table_filler
_od_lister
_od_table_filler
_strip_shower
accept_asker
event_asker
info_printer
od_scaling_asker
preview_drawer
saved_values_reader
temperature_asker
```

#### `pca_stage_runner`

```text
---- Summary ----
Main function to find the components of the haem spectra from the data itself with
a principal component analysis, instead of using a fit file. The user chooses the
spectral window and the number of components, sees each component in its own
panel and the best and worst described spectrum in the plot window, and can save
the components as a fit file in the fits folder.

---- Inputs ----
session : ViewerSession
    The browser session.
answers : dict
    Answers dictionary; the choices are stored in it (pca_start, pca_end,
    pca_rotate, pca_count, pca_smoothing_nm).
defaults : dict
    Default answers offered by the questions.
limits : Dict[str, dict]
    Trim and ignore limits of every file (trim_stage_runner).
fits_folder : Path
    Folder holding the fit .csv files.
dataset : str
    Spectral dataset holding the haem spectra.
depth : int
    Numbering depth of the questions.

---- Globals read ----
settings.PCA_WINDOW_NM, settings.PCA_SMOOTHING_NM.

---- Outputs ----
Tuple[Optional[str], Optional[dict]]
    (fit file name, fit dictionary as fit_importer gives). (None, None) when the
    user prefers to choose a fit file instead. The name is a description when the
    fit was not saved.

---- Globals mutated ----
None. Reads the files, reads from and prints to the terminal, draws the plot window
and may write a fit file (side effects).

---- Equations ----
None.

---- Helpers ----
_component_namer
_fit_file_saver
_pca_pictures_publisher
accept_asker
component_builder
component_classifier
component_count_suggester
component_finder
decomposition_example_finder
fit_table_builder
info_printer
number_asker
pca_spectra_gatherer
problem_teller
progress_clearer
progress_printer
text_colourer
yes_no_asker
```

#### `plots_stage_runner`

```text
---- Summary ----
Main function to show the figure saved for each file, drawn as it will be saved
from the standard settings or the ones last saved for the dataset, and ask whether
it is accepted. Each 'No' answer names one part (the oxygen and OCR, which haems,
the angle of the event labels): only that part's questions are asked, with the
current choices as the defaults, and the figure is drawn and asked about again. The
settings strip turns the haems on or off and sets how they are shown, the per OD
scaling, the journal and the size, so 'which haems' asks only which ones in which
order, and none of those is asked.

---- Inputs ----
session : ViewerSession
    The browser session; its fit is the one in use, its regions say which files
    have % oxidised, and its redraw is set.
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers offered by the questions.
limits : Dict[str, dict]
    Trim and ignore limits of every file.
details : Dict[str, dict]
    OD values and events of every file.

---- Globals read ----
None.

---- Outputs ----
bool
    True when at least one panel is plotted.

---- Globals mutated ----
None. Stores the answers in ``answers``, and the redraw in the session (side
effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_figure_starter
_strip_shower
accept_asker
haem_choice_asker
info_printer
label_angle_asker
preview_drawer
region_files_lister
signal_asker
```

#### `processing_stage_runner`

```text
---- Summary ----
Main function to talk the user through the processing, with the plot redrawn after
each answer: first the haem fit, then, now that the haems are seen, an offer to
change the trim and ignore times, then the oxidised and the reduced region of every
file (when the haems are shown), then whether to work out Δψ (when it can be), and
last the averaging windows, dragged on the plot (they are drawn in the plot only
once that step is answered). A line
points to the strip at the start, and another to its % oxidised once a file has
both regions. The
settings strip picks the fit and leaves the haems out, so the decomposition
question only offers to find the components from the data instead. While those
questions are asked the strip is greyed out.

---- Inputs ----
session : ViewerSession
    The browser session; its fit is the fit shown so far (None when the plot shows
    no haems), and is set to the fit chosen. Its redraw is set.
answers : dict
    Answers dictionary the values are stored in; fit_file and
    decomposition_dataset name the fit shown.
defaults : dict
    Default answers offered by the questions; whether to decompose and which fit
    follow the answers so far (the strip may have changed them).
limits : Dict[str, dict]
    Trim and ignore limits of every file (trim_stage_runner).
fits_folder : Path
    Folder holding the fit .csv files.
details : Dict[str, dict]
    OD values and events of every file (details_stage_runner); the averaging
    windows are drawn around the events not ignored there.
trim_runner : Callable[[], Dict[str, dict]]
    Function that asks the trim and ignore questions again with the haems of the
    session's fit on the plot, and returns the new limits.
regions : Optional[Dict[str, Dict[str, float]]]
    The regions the step starts with (_regions_chooser), from the last time it
    was answered in this run; None for regions not chosen.

---- Globals read ----
settings.DELTA_PSI_LIMIT_ANSWERS.

---- Outputs ----
Optional[Dict[str, Dict[str, float]]]
    The regions of every file as _regions_chooser gives them; those given, when
    the haems are not decomposed and the step is not asked. The fit is in
    session.fit (None when the haems are not decomposed).

---- Globals mutated ----
None. Stores the answers in ``answers`` and the fit in the session, reads from and
prints to the terminal and redraws the window (side effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_windows_chooser
_decomposition_storer
_regions_chooser
_strip_shower
accept_asker
decomposition_asker
delta_psi_asker
fit_names_lister
info_printer
pca_stage_runner
preview_drawer
region_files_lister
yes_no_asker
```

#### `region_files_lister`

```text
---- Summary ----
Main function to list the files that have both an oxidised and a reduced region
under the trim and ignore limits as they are now: the files whose haems have two
levels, and so a % oxidised.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
limits : Dict[str, dict]
    Trim and ignore limits of every file.
regions : Optional[Dict[str, Dict[str, float]]]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
    times on the original recording (min); None, or a file missing, for none.
dataset : Optional[str]
    The spectrometer whose spectra hold the haems; None when it is not known.

---- Globals read ----
REGION_KEYS.

---- Outputs ----
List[str]
    Names of the files with both regions, in the order of the summaries.

---- Globals mutated ----
None.

---- Equations ----
time on the plot = time on the recording - trim start; a region kept within the
used part of the run counts when it is at least the least length.

---- Helpers ----
_region_rules_lister
region_edges_builder
region_span_reader
```

#### `trim_stage_runner`

```text
---- Summary ----
Main function to run the trimming step on the standard plot of the whole recording
of every file: the trimmed and ignored edges are dragged on the plot or typed in
the strip under it, and Enter accepts them. When the step is opened again, the
limits it had stay on the plot as red dashed lines. The limits are then listed and
the trimmed data is drawn. The haems are those of the session's fit (none when it
has none).

---- Inputs ----
session : ViewerSession
    The browser session; its redraw is set.
answers : dict
    Answers so far, used for the figure style of the preview.
remembered : Dict[str, dict]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} the edges start
    at (from the last run, or this run's when the step is opened again).
previous : Optional[Dict[str, dict]]
    Limits in the same layout drawn as red dashed lines while the edges are
    dragged; None for none.

---- Globals read ----
TRIM_FIELDS, TRIM_KEY_TEXT, TRIM_NUDGE (module constants).

---- Outputs ----
Dict[str, dict]
    The limits of every file, as trim_limits_builder gives them.

---- Globals mutated ----
None. Reads from and prints to the terminal and draws the plot window (side
effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_limits_lister
enter_waiter
info_printer
preview_drawer
trim_layout_finder
trim_limits_builder
trim_minutes_builder
trim_minutes_setter
trim_pointer_reader
EdgeChoice
```

#### `viewer_asker`

```text
---- Summary ----
Main function to ask the questions of the experiment browser: the file browser,
trimming and ignoring, the OD values and the event labels (which end the import),
the processing (the haem fit, the trim and ignore times again if wanted, the
oxidised and reduced regions, which start where they were saved with the dataset,
the averaging) and the individual figures. The standard plot of every file (oxygen,
OCR and the haems of the dataset's fit) is shown first, with no question asked. The
plot window is redrawn after each answer, and at the end any step can be gone back
to. The settings strip can be changed while these questions wait (except those of
the components found from the data); it is greyed out afterwards.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers offered by the questions.
remembered : Dict[str, dict]
    The files part of the dataset's settings: {file name: limits, OD values,
    events and regions} from the last run (dataset_settings, DATA_FORMAT.md).
fits_folder : Path
    Folder holding the fit .csv files.
export_root : Path
    Results folder.
exported : Optional[List[Path]]
    List the results folder is added to once the export of the import writes into
    it, so the caller can say it is kept even when the questions are stopped; None
    when the caller does not need to know.

---- Globals read ----
STAGE_TITLES (module constant); settings.STANDARD_FIT; REGION_KEYS.

---- Outputs ----
Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool, Dict[str, dict]]
    (limits, fit, details, plotted, regions): the trim and ignore limits of every
    file, the fit (None when the haems are not decomposed), the OD values and
    events of every file, whether the figure of each file has at least one panel,
    and the oxidised and reduced region of every file as _regions_chooser gives
    them (those saved with the dataset when the step was not asked).

---- Globals mutated ----
None. Stores the answers in ``answers``, reads from and prints to the terminal,
draws and closes the plot window, sets up the settings strip, writes the export
when one is chosen and adds to ``exported`` (side effects).

---- Equations ----
None.

---- Helpers ----
_export_refresher
_standard_fit_loader
_strip_change_applier
_strip_shower
active_gui_getter
browser_stage_runner
choice_asker
details_stage_runner
fit_names_lister
heading_printer
library_haems_lister
info_printer
numbering_getter
numbering_setter
plots_stage_runner
processing_stage_runner
section_starter
trim_stage_runner
```

#### `windows_stage_runner`

```text
---- Summary ----
Main function to run the window step of the processing (4.6) by itself, after the
browser steps have ended, for a later figure that needs the averaging windows when
none are set up. The processing plot of every file is drawn again, with the trim
and ignore limits, the fit and the regions already chosen, and the windows are
dragged or typed on it as in the processing; they start ticked. Nothing else is
asked, and the settings strip stays greyed out.

---- Inputs ----
context : dict
    {answers, fit, summaries, limits, details, regions, export_root} of the run so
    far (everything_asker of main.py). The answers are changed in place.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the averaging windows are set up after the step.

---- Globals mutated ----
None. Stores averaging, window_minutes and gap_minutes in the answers of the
context, reads from and prints to the terminal and draws in the plot window (side
effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_windows_chooser
active_gui_getter
preview_drawer
```

## `utils_viewer/viewer_strip.py`

The settings strip under the plot: the haems, the fit, the background, the decomposition

### CLASSES

#### `EdgeRow`

```text
---- Summary ----
The row of the strip shown while edges are dragged on the plot: a typing box for
each edge, holding its value for the file shown, and the "Every file" tick box. It
follows the drag and passes on what the user types or ticks; it changes nothing by
itself. Every method runs on the window thread.

---- Attributes ----
frame : Any
    The Tk frame holding the row, for the window to place.

---- Globals read ----
ERROR_BACKGROUND, ERROR_TEXT, NOTE_TEXT.

---- Methods ----
__init__
_every_file_handler
_value_handler
fields_setter
values_setter
```

##### `__init__`

```text
---- Summary ----
Method to build the row, with no boxes until fields_setter.

---- Inputs ----
tk : Any
    The tkinter module.
parent : Any
    The widget the row is built in.
background : str
    Background colour of the row.
on_value : Callable[[str, float], None]
    Called with (field, number) when a number is typed in a box.
on_every_file : Callable[[bool], None]
    Called with the new state of the tick box when it is clicked.
on_return : Callable[[], None]
    Called after Enter in a box has passed its number on (or found it as it
    was), so the keyboard can go back to the answer box.

---- Globals read ----
NOTE_TEXT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Creates the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_every_file_handler
```

##### `_every_file_handler`

```text
---- Summary ----
Method to pass on the new state of the "Every file" tick box.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Calls the function given as on_every_file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_value_handler`

```text
---- Summary ----
Method to take the number typed in one box, when Enter is pressed or the box is
left; a box left as it was shown passes nothing on. A number that cannot be
used turns the box red, with the reason beside the tick box, and keeps the
keyboard; after Enter, any other answer gives it back to the answer box.

---- Inputs ----
key : str
    The field of the box.
is_return : bool
    True when Enter was pressed in the box.

---- Globals read ----
ERROR_BACKGROUND, ERROR_TEXT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the box and calls the function given as on_value (side
effects).

---- Equations ----
None.

---- Helpers ----
minutes_checker
```

##### `fields_setter`

```text
---- Summary ----
Method to make one typing box for each field, each after its name, followed by
the unit, and set the tick box and its words.

---- Inputs ----
fields : List[Tuple[str, str]]
    [(field, name shown before its box)] in order.
is_every_file : bool
    Whether the tick box is ticked.
unit : str
    The unit written after the boxes: 'min' or 's' (a key of UNIT_HELP).
tick_text : str
    The words of the tick box: "Every file", or those of the step's own
    switch.

---- Globals read ----
EVERY_FILE_TEXT, UNIT_HELP.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Replaces the boxes (side effect).

---- Equations ----
None.

---- Helpers ----
_value_handler
```

##### `values_setter`

```text
---- Summary ----
Method to show the values of the file shown in the boxes.

---- Inputs ----
values : Optional[Dict[str, float]]
    {field: value}, or None to empty the boxes.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the boxes (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `SettingsStrip`

```text
---- Summary ----
The strip under the plot that always shows the current choices: a tick box for the
haems, a drop-down of the fits, a drop-down of the backgrounds, a button that folds
out a tick box for each haem of the library (Build a fit), a button that keeps the
decomposition in use to compare the next ones with (with a line saying which one is
kept; while one is kept it reads "Keep this one", and a second button goes back to
the kept one), a drop-down of the spectrometer whose spectra hold the haems (shown when the
files share more than one), a drop-down of how the haems are shown with a "per OD"
box, an "OCR per OD" box (both boxes shown only when OD values were entered), a
row of the numbers of Δψ (shown only while Δψ is worked out: the midpoint of bH
and of bL and the fall typed, each midpoint with the other haem reduced filled in,
a button for the paper's values, and the share, the temperature and the limits as
text, or as boxes when "More" is ticked), a drop-down of the journal, a drop-down of the widths that journal allows and a typing
box for the height. It tells the window what the user changed and can be
set by the program; it changes nothing by itself. It starts greyed out, until the
program says it is listening. Every method runs on the window thread, except
values_reader.

---- Attributes ----
frame : Any
    The Tk frame holding the strip, for the window to place.

---- Globals read ----
settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS, JOURNAL_NAMES,
BACKGROUND_SHORT_NAMES, OWN_HAEMS_NAME and the module constants.

---- Methods ----
__init__
_back_handler
_background_handler
_build_toggler
_change_reporter
_compare_handler
_fit_handler
_form_handler
_haems_handler
_height_handler
_journal_handler
_more_toggler
_paper_handler
_per_od_handler
_psi_handler
_size_refresher
_spectra_handler
_tick_handler
_width_handler
choices_setter
fits_setter
library_setter
state_setter
values_reader
values_setter
```

##### `__init__`

```text
---- Summary ----
Method to build the strip with the standard settings in it.

---- Inputs ----
tk : Any
    The tkinter module.
ttk : Any
    The tkinter.ttk module.
parent : Any
    The widget the strip is built in.
background : str
    Background colour of the strip.
on_change : Callable[[Dict[str, Any]], None]
    Called once for each change the user makes, with {name: value} of every
    value that changed (a new journal can change the width and the height
    too); the names are those of VALUE_NAMES.

---- Globals read ----
settings.DEFAULT_ANSWERS, JOURNAL_NAMES, NO_JOURNAL, NO_JOURNAL_TEXT,
NOTE_TEXT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Creates the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_back_handler
_background_handler
_build_toggler
_compare_handler
_fit_handler
_form_handler
_haems_handler
_height_handler
_journal_handler
_more_toggler
_paper_handler
_per_od_handler
_psi_handler
_size_refresher
_spectra_handler
_width_handler
psi_values_builder
```

##### `_background_handler`

```text
---- Summary ----
Method to take the background picked in the drop-down.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
```

##### `_back_handler`

```text
---- Summary ----
Method to take the button that goes back to the kept decomposition. The strip
keeps nothing: the click is told as {BACK_CHANGE: True}, and the program sets
the strip to the kept values.

---- Inputs ----
None.

---- Globals read ----
BACK_CHANGE.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Calls the function given as on_change (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_build_toggler`

```text
---- Summary ----
Method to fold the tick boxes of the library haems out under the first row, or
away again.

---- Inputs ----
None.

---- Globals read ----
BUILD_CLOSED_TEXT, BUILD_OPEN_TEXT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Shows or hides the panel (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_change_reporter`

```text
---- Summary ----
Method to tell the window, in one call, every value that differs from what it
was; nothing is told when nothing changed.

---- Inputs ----
before : Dict[str, Any]
    The values before the user's change.

---- Globals read ----
VALUE_NAMES.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Calls the function given as on_change (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_compare_handler`

```text
---- Summary ----
Method to take the button that keeps the decomposition in use to compare with,
or, while one is kept, carries on with the one on the plot. The program says which one is kept (the value 'kept').

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value, changes the button and reports the change (side
effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
```

##### `_fit_handler`

```text
---- Summary ----
Method to take the fit picked in the drop-down.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
```

##### `_form_handler`

```text
---- Summary ----
Method to take the way of showing the haems picked in the drop-down.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
```

##### `_haems_handler`

```text
---- Summary ----
Method to take the tick box of the haems.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
```

##### `_height_handler`

```text
---- Summary ----
Method to take the height typed in the box, when Enter is pressed or the box
is left. A height that cannot be used turns the box red, with the reason
beside it, and is not passed on.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
ERROR_BACKGROUND, ERROR_TEXT, NO_JOURNAL.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
height_checker
```

##### `_journal_handler`

```text
---- Summary ----
Method to take the journal picked in the drop-down. "None" gives the standard
size; a journal gives back the size last chosen for a journal, with the first
width of the journal when it does not allow the one chosen.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
NO_JOURNAL.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the values and reports the changes (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
width_choices_lister
```

##### `_more_toggler`

```text
---- Summary ----
Method to take the "More" box of the Δψ row: ticked, the share, the temperature
and the limits are boxes to type in; unticked, they are one line of text.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_size_refresher
```

##### `_paper_handler`

```text
---- Summary ----
Method to take the button that puts the numbers of the paper back in the Δψ
row: the midpoints, the fall, the share and the limits. The temperature stays,
as it is that of the runs.

---- Inputs ----
None.

---- Globals read ----
settings.DEFAULT_ANSWERS, PSI_FIELDS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the values and reports the changes (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
psi_values_builder
```

##### `_per_od_handler`

```text
---- Summary ----
Method to take one of the two per OD tick boxes.

---- Inputs ----
name : str
    'haem_per_od' or 'ocr_per_od', the value of the box clicked.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
```

##### `_psi_handler`

```text
---- Summary ----
Method to take the number typed in one box of the Δψ row, when Enter is pressed
or the box is left; a box left as it was shown passes nothing on. A number that
cannot be used turns the box red, with the reason under the row, and the value
in use stays.

---- Inputs ----
name : str
    The value of the box, one of PSI_FIELDS.

---- Globals read ----
ERROR_BACKGROUND.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
psi_number_checker
typed_number_reader
```

##### `_size_refresher`

```text
---- Summary ----
Method to show the kept values in every part of the strip: the widths offered
follow the journal, the width and the height are greyed for "None", the button
that keeps a decomposition is greyed while no haems are shown, the button that
goes back to the kept one and the line saying which one is kept show only
while one is, the spectrometer shows only when
there is a choice, the per OD boxes only when OD values were entered (the one
of the haems greyed for % oxidised, which has no per OD), the Δψ row only
while Δψ is worked out (its filled-in midpoints following the typed ones and
the fall), and the whole strip is greyed while the program is not listening.

---- Inputs ----
None.

---- Globals read ----
HAEM_FORM_TEXTS, KEEP_TEXT, KEPT_PREFIX, NO_JOURNAL, NOTE_TEXT, STOP_TEXT.
(BACK_TEXT is set on its button once, when it is built.)

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
haem_form_choices_lister
height_checker
psi_seconds_filler
psi_summary_writer
width_choices_lister
```

##### `_spectra_handler`

```text
---- Summary ----
Method to take the spectrometer picked in the drop-down.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
```

##### `_tick_handler`

```text
---- Summary ----
Method to take a tick box of Build a fit: the haems ticked become the fit, as
"Your own haems". Ticking a haem with the same name as one already ticked
unticks that one, and the last haem ticked cannot be unticked; a note beside
the height says so.

---- Inputs ----
name : str
    File name of the library haem whose box was clicked.

---- Globals read ----
OWN_HAEMS_NAME, NOTE_TEXT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the values, changes the widgets and reports the change (side
effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
_size_refresher
haem_ticks_resolver
```

##### `_width_handler`

```text
---- Summary ----
Method to take the width picked in the drop-down.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the value and reports the change (side effects).

---- Equations ----
None.

---- Helpers ----
_change_reporter
```

##### `choices_setter`

```text
---- Summary ----
Method to say what the strip offers: the spectrometers of the "Spectra"
drop-down (shown only with more than one), whether % oxidised is in the "Haems
as" drop-down, and whether the two per OD boxes are shown. The values stay.

---- Inputs ----
spectra : List[str]
    The spectrometers every file has, as they are to be listed.
has_percent : bool
    True when at least one file has both regions, so % oxidised is offered.
has_od : bool
    True when OD values were entered, so the per OD boxes are shown.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_size_refresher
```

##### `fits_setter`

```text
---- Summary ----
Method to give the drop-down of the fits its list. The fit shown stays.

---- Inputs ----
names : List[str]
    File names of the fits, as they are to be listed.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the drop-down (side effect).

---- Equations ----
None.

---- Helpers ----
_size_refresher
```

##### `library_setter`

```text
---- Summary ----
Method to build the tick boxes of Build a fit: one line for each type of haem
(a, b, c, then any other), with a box for each library file, named by its file
without .csv.

---- Inputs ----
haems : List[Dict[str, str]]
    The library, as spectral_decomposer.library_haems_lister gives it: [{'file',
    'haem', 'type'}], in the order to show.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Rebuilds the panel (side effect).

---- Equations ----
None.

---- Helpers ----
_size_refresher
_tick_handler
```

##### `state_setter`

```text
---- Summary ----
Method to let the user change the strip, or grey it out while what it shows
is not being used. The values stay on show either way.

---- Inputs ----
is_enabled : bool
    True to let the user change the values, False to grey the strip out.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_size_refresher
```

##### `values_reader`

```text
---- Summary ----
Method to give the values the strip shows now. It can be called from any
thread.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    A copy of the strip values (DATA_FORMAT.md).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `values_setter`

```text
---- Summary ----
Method to show the values the program gives. Nothing is reported back, as the
program made the change itself.

---- Inputs ----
values : Dict[str, Any]
    Some or all of the strip values (DATA_FORMAT.md), already checked by
    strip_values_checker.

---- Globals read ----
NO_JOURNAL.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the values and changes the widgets (side effects).

---- Equations ----
None.

---- Helpers ----
_size_refresher
```

### HELPERS

#### `_page_journal_finder`

```text
---- Summary ----
Helper function to give the journal whose page a strip journal is drawn on: the
journal itself, or the standard journal for "None".

---- Inputs ----
journal : str
    NO_JOURNAL or a key of settings.JOURNAL_SPECS.

---- Globals read ----
settings.DEFAULT_ANSWERS, settings.JOURNAL_SPECS, NO_JOURNAL.

---- Outputs ----
str
    A key of settings.JOURNAL_SPECS. Raises ValueError for an unknown journal.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `form_answers_builder`

```text
---- Summary ----
Main function to turn the spectrometer and the ways of showing the haems and the
OCR of the strip into the answers of the run.

---- Inputs ----
values : Dict[str, Any]
    Some or all of the strip values (DATA_FORMAT.md), as checked by
    strip_values_checker.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    The answers to update: decomposition_dataset for the spectrometer, haem_mode
    and haem_per_od as given, and ocr_mode 'od' for the OCR per OD box ticked,
    'raw' for it unticked. Empty when the values hold none of them.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `haem_form_choices_lister`

```text
---- Summary ----
Main function to list the ways of showing the haems the "Haems as" drop-down
offers, each with its words.

---- Inputs ----
has_percent : bool
    True when at least one file has both regions, so % oxidised is offered.

---- Globals read ----
HAEM_FORM_TEXTS.

---- Outputs ----
List[Tuple[str, str]]
    [(haem_mode, words)] in the order of the drop-down: delta D, % oxidised when
    offered, absorbance.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `haem_ticks_resolver`

```text
---- Summary ----
Main function to work out the library haems ticked after a click on one tick box of
Build a fit. Two haems of the same name could not be told apart in the figures, so
ticking one unticks the other; and a fit needs a haem, so the last cannot be
unticked.

---- Inputs ----
ticked : Sequence[str]
    File names ticked before the click.
clicked : str
    File name of the box clicked.
is_on : bool
    True when the box is ticked after the click.
haems_by_file : Dict[str, str]
    {file name: plain haem name} of the library.

---- Globals read ----
LAST_TICK_NOTE (module constant).

---- Outputs ----
Tuple[List[str], str]
    (the file names ticked, in the order ticked; a note for the user, '' when
    there is nothing to say).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `height_checker`

```text
---- Summary ----
Main function to check a height typed as a share of a page, and to say what it is
in millimetres on the page of the journal.

---- Inputs ----
text : str
    What was typed, e.g. '0.5' or '0,5'.
journal : str
    NO_JOURNAL or a key of settings.JOURNAL_SPECS.

---- Globals read ----
settings.JOURNAL_SPECS, HEIGHT_HELP.

---- Outputs ----
Tuple[Optional[float], str]
    (height, 'of a page (85 mm)') for a height above 0 and up to 1, or (None, why
    it cannot be used).

---- Globals mutated ----
None.

---- Equations ----
height in mm = height * page height of the journal in mm.

---- Helpers ----
_page_journal_finder
typed_number_reader
```

#### `kept_decomposition_builder`

```text
---- Summary ----
Main function to keep the decomposition in use, to compare the next ones with: the
fit, the answers it was worked out with (the fit, the background, the spectrometer
and the numbers of delta psi), the oxidised and reduced regions of every file, and
its name in words.

---- Inputs ----
answers : dict
    The answers in use (fit_file, haem_files, haem_background,
    decomposition_dataset, delta_psi and the numbers of delta psi).
fit : dict
    The fit in use (spectral_decomposer.fit_importer); it is kept as it is, as a
    fit is never changed once read.
regions : Dict[str, Dict[str, float]]
    {file name: {oxidised_start, oxidised_end, reduced_start, reduced_end}} as
    times on the original recording (min); may be empty. A copy is kept, so the
    regions changed later leave it as it was.

---- Globals read ----
BACKGROUND_SHORT_NAMES, PSI_KEPT_ANSWERS.

---- Outputs ----
Dict[str, Any]
    The kept decomposition (DATA_FORMAT.md, kept decomposition).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
fit_describer
```

#### `minutes_checker`

```text
---- Summary ----
Main function to check a number of minutes typed in a box of the edges row.

---- Inputs ----
text : str
    What was typed, e.g. '4.5' or '4,5'.

---- Globals read ----
MINUTES_HELP.

---- Outputs ----
Tuple[Optional[float], str]
    (minutes, '') for a number of 0 or more, or (None, what to type instead).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
typed_number_reader
```

#### `psi_answers_builder`

```text
---- Summary ----
Main function to turn the numbers changed in the Δψ row into the answers of the
run: the four midpoint potentials from the two typed and the fall, and the share,
the temperature and the limits as given.

---- Inputs ----
changes : Dict[str, Any]
    {name: new value} of the strip values that changed (DATA_FORMAT.md).
answers : dict
    The answers in use; the midpoints not changed are read from them.

---- Globals read ----
PSI_MIDPOINT_FIELDS, PSI_MORE_ANSWERS.

---- Outputs ----
Dict[str, float]
    The answers to update: all four midpoints (mV) when a midpoint or the fall
    changed, and psi_share, temperature_c (°C), psi_reduced_lowest_percent and
    psi_reduced_highest_percent when they did. Empty when no number of the row
    changed.

---- Globals mutated ----
None.

---- Equations ----
psi_seconds_filler.

---- Helpers ----
psi_seconds_filler
psi_values_builder
```

#### `psi_change_describer`

```text
---- Summary ----
Main function to say in plain sentences what the numbers of Δψ are after a change
in the Δψ row: what was typed and what was filled in from it.

---- Inputs ----
changes : Dict[str, Any]
    {name: new value} of the strip values that changed (DATA_FORMAT.md).
answers : dict
    The answers in use, already holding the change (psi_answers_builder).

---- Globals read ----
PSI_MIDPOINT_FIELDS.

---- Outputs ----
List[str]
    One sentence for the midpoints and the fall, one for the share, one for the
    temperature and one for the limits, each only when it changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
psi_values_builder
```

#### `psi_number_checker`

```text
---- Summary ----
Main function to check a number typed in one box of the Δψ row.

---- Inputs ----
name : str
    The value of the box, one of PSI_FIELDS.
text : str
    What was typed, e.g. '40', '-20' or '0,5'.
values : Dict[str, Any]
    The strip values in use; a limit is checked against the other limit.

---- Globals read ----
TEMPERATURE_LIMITS_C.

---- Outputs ----
Tuple[Optional[float], str]
    (number, '') for a number that can be used, or (None, what to type instead).
    A midpoint or the fall is any number (mV); the share is above 0; the
    temperature is one the temperature question takes; the lowest limit is above
    0 and below the highest, the highest above the lowest and below 100.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
typed_number_reader
```

#### `psi_seconds_filler`

```text
---- Summary ----
Main function to fill in the midpoint potential of each b haem with the other
haem reduced, from its midpoint with the other oxidised and the fall.

---- Inputs ----
bH_mV : float
    Midpoint potential of bH with bL oxidised (mV).
bL_mV : float
    Midpoint potential of bL with bH oxidised (mV).
fall_mV : float
    How far each midpoint falls when the other haem is reduced (mV).

---- Globals read ----
None.

---- Outputs ----
Tuple[float, float]
    (midpoint of bH with bL reduced, midpoint of bL with bH reduced), in mV.

---- Globals mutated ----
None.

---- Equations ----
second = first - fall, for each haem: 40 and -20 with a fall of 70 give -30 and
-90. The fall is the same for both, as the maths of delta psi needs.

---- Helpers ----
None.
```

#### `psi_summary_writer`

```text
---- Summary ----
Main function to write the share, the temperature and the limits of Δψ as the one
line of text shown in the Δψ row while "More" is not ticked.

---- Inputs ----
values : Dict[str, Any]
    The strip values (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
str
    'share 0.5 · 37 °C · given between 10 and 90 % reduced'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `psi_values_builder`

```text
---- Summary ----
Main function to give the strip values of the Δψ row that show the answers of the
run.

---- Inputs ----
answers : dict
    The answers (the four midpoints, psi_share, temperature_c and the two limits).
is_on : bool
    True when Δψ is worked out, which shows the row.

---- Globals read ----
PSI_MORE_ANSWERS.

---- Outputs ----
Dict[str, Any]
    {'delta_psi', 'psi_bH_mV', 'psi_bL_mV', 'psi_fall_mV', 'psi_share',
    'temperature_c', 'psi_lowest_percent', 'psi_highest_percent'}.

---- Globals mutated ----
None.

---- Equations ----
fall = midpoint of bH with bL oxidised - midpoint of bH with bL reduced, rounded
to a millionth of a mV: 40 - (-30) = 70 mV.

---- Helpers ----
None.
```

#### `size_answers_builder`

```text
---- Summary ----
Main function to turn the journal, width and height of the strip into the answers
of the figure of each file. The haems and the fit are left out: they need the fit
file read, which the questions do.

---- Inputs ----
values : Dict[str, Any]
    Some or all of the strip values (DATA_FORMAT.md), as checked by
    strip_values_checker.

---- Globals read ----
settings.DEFAULT_ANSWERS, NO_JOURNAL.

---- Outputs ----
Dict[str, Any]
    The answers to update: journal and size_mode for a journal ("None" is the
    standard journal with size_mode 'default'), columns and height as given.
    Empty when the values hold none of them.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `strip_values_builder`

```text
---- Summary ----
Main function to give the strip values that show the answers of the run.

---- Inputs ----
answers : dict
    The answers (fit_file, haem_background, decomposition_dataset, haem_mode,
    haem_per_od, ocr_mode, delta_psi and the numbers of Δψ, journal, columns,
    height, size_mode); a fit_file of None shows an empty fit.
has_haems : bool
    True when the haems are worked out and shown, which ticks the box.
haem_files : Sequence[str]
    The library files of the fit in use, ticked under Build a fit (none for a fit
    file of the user's own or components from the data).
kept : str
    The decomposition kept to compare with, in words (its fit and background), or
    '' when none is kept.

---- Globals read ----
NO_JOURNAL.

---- Outputs ----
Dict[str, Any]
    All the strip values (DATA_FORMAT.md). A figure of the standard size
    (size_mode other than 'custom') shows the journal as "None"; the OCR per OD
    box is ticked for the OCR per OD, unticked for the plain OCR and its % of the
    range; the Δψ row shows when the haems are worked out and Δψ is switched on.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
psi_values_builder
```

#### `strip_values_checker`

```text
---- Summary ----
Main function to check values meant for the strip before they are shown: the
names, the background, the haems ticked, whether a decomposition is kept and its
words, the spectrometer, the way of showing the haems, the per OD boxes, the
numbers of the Δψ row (numbers, a share above 0, limits above 0 and below 100
with the lowest first), the journal, a width the journal allows and a height the
page allows. The width and the height are checked against the journal given with
them.

---- Inputs ----
values : Dict[str, Any]
    Some or all of the strip values (DATA_FORMAT.md).

---- Globals read ----
VALUE_NAMES, HEIGHT_HELP, BACKGROUND_SHORT_NAMES, HAEM_FORM_TEXTS, PSI_FIELDS.

---- Outputs ----
None
    Nothing. Raises ValueError, in plain words, for a value the strip cannot
    show.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_page_journal_finder
width_choices_lister
```

#### `width_choices_lister`

```text
---- Summary ----
Main function to list the widths a journal allows, each with the text shown in
the drop-down.

---- Inputs ----
journal : str
    NO_JOURNAL or a key of settings.JOURNAL_SPECS.

---- Globals read ----
settings.JOURNAL_SPECS.

---- Outputs ----
List[Tuple[float, str]]
    [(columns, '1 column (89 mm)'), ...] in the order of the settings.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_page_journal_finder
```

## `utils_viewer/viewer_table.py`

The tables of the window, filled in by clicking a cell and typing: the OD values of each

### CLASSES

#### `AnswerTable`

```text
---- Summary ----
A table of the window, filled in by clicking a cell and typing: a fixed first
column (the file, or the time of an event), then cells of three kinds (a number
above 0, a number of 0 or more or nothing, a label), the rows grouped under the
name of their file where the table says so. Tab moves across, Enter and the arrows
move down and up, and Enter in the last row goes on to Confirm. A cell that cannot
be used turns red; in a row whose label is the skip word the other cells are greyed
out and not read. Entering a cell tells the window which file it belongs to. The
table tells nothing else by itself: the program reads it when Confirm is pressed.
Every method runs on the window thread, except problems_lister and values_reader.

---- Attributes ----
frame : Any
    The Tk frame holding the table, for the window to place.

---- Globals read ----
CELL_WIDTHS, MINIMUM_HEIGHT_PX, ERROR_BACKGROUND, HEADING_TEXT, SKIPPED_BACKGROUND,
SKIPPED_TEXT, LABEL.

---- Methods ----
__init__
_cell_checker
_cell_mover
_cell_revealer
_focus_handler
_problem_finder
_row_skipper
_size_follower
_skip_checker
_wheel_binder
_wheel_scroller
cell_focuser
problems_lister
rows_setter
symbol_inserter
values_reader
```

##### `__init__`

```text
---- Summary ----
Method to build the empty table; rows_setter fills it.

---- Inputs ----
tk : Any
    The tkinter module.
ttk : Any
    The tkinter.ttk module.
parent : Any
    The widget the table is built in.
font : Tuple[str, int]
    (family, size) of the text.
colours : Dict[str, str]
    {'background', 'text', 'cell', 'edge'}: the colours of the table, its
    text, its cells and the edge of the cell being typed in.
on_finish : Callable[[], None]
    Called when Enter is pressed in the last row.
on_file : Callable[[str], None]
    Called with the name of the file a cell belongs to when the cell is
    entered.

---- Globals read ----
MINIMUM_HEIGHT_PX.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Creates the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
_size_follower
_wheel_binder
```

##### `_cell_checker`

```text
---- Summary ----
Method to keep what was typed in one cell, to turn the cell red when it cannot
be used, and, for a label, to grey out or bring back the other cells of its
row as the label is or is not the skip word.

---- Inputs ----
row : int
    Row of the cell, from 0.
key : str
    Name of its value, such as 'OD' or 'label'.

---- Globals read ----
ERROR_BACKGROUND, LABEL.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Keeps the text and colours the cell (side effects).

---- Equations ----
None.

---- Helpers ----
_row_skipper
cell_reader
```

##### `_cell_mover`

```text
---- Summary ----
Method to move to the same cell of the row below or above, passing greyed-out
cells. Past the last row the table is left, for Confirm.

---- Inputs ----
row : int
    Row of the cell being typed in, from 0.
key : str
    Name of its value.
step : int
    +1 for the row below, -1 for the row above.

---- Globals read ----
None.

---- Outputs ----
str
    'break', so Tk does nothing more with the key.

---- Globals mutated ----
None. Moves the typing cursor (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_cell_revealer`

```text
---- Summary ----
Method to scroll a long table so the cell being typed in can be seen.

---- Inputs ----
cell : Any
    The Tk entry of the cell that was entered.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Scrolls the table (side effect).

---- Equations ----
The table is moved so the cell sits one row height under the top:
share = (top of the cell - its height) / height of the whole table.

---- Helpers ----
None.
```

##### `_focus_handler`

```text
---- Summary ----
Method to follow the cell being typed in: it is remembered for the Symbols
row, scrolled into sight, and its file is told to the window.

---- Inputs ----
row : int
    Row of the cell, from 0.
key : str
    Name of its value.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Scrolls the table and calls on_file (side effects).

---- Equations ----
None.

---- Helpers ----
_cell_revealer
```

##### `_problem_finder`

```text
---- Summary ----
Method to find the cells that hold something that cannot be used, and the
needed cells left empty, in the order of the table. The greyed-out cells of a
skipped row are not looked at.

---- Inputs ----
None.

---- Globals read ----
EMPTY, LABEL, NEEDED_KINDS.

---- Outputs ----
List[Tuple[int, str, str]]
    (row, name of the value, problem) for each such cell; the problem is the
    kind of the cell when what it holds is wrong, or EMPTY.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_skip_checker
cell_reader
```

##### `_row_skipper`

```text
---- Summary ----
Method to grey out the cells of a row beside its label while the label is the
skip word (an event left out), and to bring them back when it is not.

---- Inputs ----
row : int
    Row, from 0.

---- Globals read ----
LABEL.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the state of the cells (side effect).

---- Equations ----
None.

---- Helpers ----
_skip_checker
```

##### `_size_follower`

```text
---- Summary ----
Method to let the table scroll over all its rows when they change size.

---- Inputs ----
event : Any
    The Tk event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the scrolled region (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_skip_checker`

```text
---- Summary ----
Method to say whether a row is left out: its label is the skip word, in any
capitals.

---- Inputs ----
row : int
    Row, from 0.

---- Globals read ----
LABEL.

---- Outputs ----
bool
    True when the row is left out; always False for a table with no skip word.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_wheel_binder`

```text
---- Summary ----
Method to make the mouse wheel over a part of the table scroll it, on Windows,
the Mac and Linux alike.

---- Inputs ----
widget : Any
    The Tk widget (the table, a heading, a name or a cell).

---- Globals read ----
WHEEL_EVENTS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Binds the wheel events of the widget (side effect).

---- Equations ----
None.

---- Helpers ----
_wheel_scroller
```

##### `_wheel_scroller`

```text
---- Summary ----
Method to scroll a long table with the mouse wheel.

---- Inputs ----
event : Any
    The Tk mouse wheel event, or the button 4 or 5 event of Linux.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Scrolls the table (side effect).

---- Equations ----
None.

---- Helpers ----
wheel_step_finder
```

##### `cell_focuser`

```text
---- Summary ----
Method to put the typing cursor in the first cell that still needs something,
or else in the first cell, with what it holds selected so typing replaces it.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Moves the typing cursor (side effect).

---- Equations ----
None.

---- Helpers ----
_problem_finder
```

##### `problems_lister`

```text
---- Summary ----
Method to list the cells that hold something that cannot be used and the needed
cells left empty. It can be called from any thread.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, str]]
    ('row name: column heading', problem) for each such cell, in the order of
    the table; the problem is the kind of the cell, or EMPTY. Empty when every
    cell can be used.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_problem_finder
```

##### `rows_setter`

```text
---- Summary ----
Method to fill the table with its headings and rows, the rows of a file under
its name where they are grouped.

---- Inputs ----
table : dict
    The table to show (table_rows, DATA_FORMAT.md).

---- Globals read ----
CELL_WIDTHS, HEADING_TEXT, LABEL, SKIPPED_BACKGROUND, SKIPPED_TEXT.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Rebuilds the rows of the table (side effect).

---- Equations ----
None.

---- Helpers ----
_cell_checker
_cell_mover
_focus_handler
_wheel_binder
```

##### `symbol_inserter`

```text
---- Summary ----
Method to type a symbol (µ, a superscript -1, ...) into the cell last typed in,
at its cursor, in place of what is selected there.

---- Inputs ----
symbol : str
    The characters to add.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the text of the cell (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `values_reader`

```text
---- Summary ----
Method to give the values typed in the table, row by row. It can be called
from any thread.

---- Inputs ----
None.

---- Globals read ----
LABEL.

---- Outputs ----
List[Dict[str, Any]]
    One {name of the value: value} per row, in the order of the rows: a number
    or a label without its outer spaces; None for a cell that is empty, wrong,
    or greyed out in a skipped row.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_skip_checker
cell_reader
```

### CELL HELPERS

#### `_cell_name_joiner`

```text
---- Summary ----
Helper function to name cells in a sentence: the first few, then how many more.

---- Inputs ----
names : Sequence[str]
    Names of the cells, at least one.

---- Globals read ----
NAMED_PROBLEMS.

---- Outputs ----
str
    For example 'a: OD, b: OD' or 'a: OD, ..., e: OD and 3 more'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_number_writer`

```text
---- Summary ----
Helper function to write a value in a cell: the number as short as it goes, or
nothing.

---- Inputs ----
value : Optional[float]
    The value, or None.

---- Globals read ----
None.

---- Outputs ----
str
    For example '0.5' or ''.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `cell_reader`

```text
---- Summary ----
Main function to read what was typed in one cell: a number (with a point or a comma
as the decimal sign) above 0 or of 0 or more, as the kind asks, or a label; or
nothing yet, which is never wrong here (a needed cell left empty is found when
Confirm is pressed).

---- Inputs ----
text : str
    What the cell holds.
kind : str
    ABOVE_ZERO, ZERO_OR_MORE or LABEL.

---- Globals read ----
ABOVE_ZERO, LABEL.

---- Outputs ----
Tuple[Any, bool]
    (value, is_valid): (the number or the label without its outer spaces, True)
    when it can be used; (None, True) for an empty cell; (None, False) for a
    number that is not one, or is below its limit.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
typed_number_reader
```

#### `label_entries_reader`

```text
---- Summary ----
Main function to take the labels and concentrations typed in the labels table back
into the events of each file.

---- Inputs ----
table : dict
    The labels table that was shown (label_table_builder, table_rows,
    DATA_FORMAT.md).
values : List[Dict[str, Any]]
    What AnswerTable.values_reader gave for it, row by row.
entries : Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]} the
    table was built from; not changed.

---- Globals read ----
None.

---- Outputs ----
Dict[str, List[dict]]
    A copy of ``entries`` with each event's label and concentration_uM as typed;
    a label left empty keeps the one it had.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `label_table_builder`

```text
---- Summary ----
Main function to lay out the labels table: one row per event, with its time, label
and concentration, under the name of its file; files without events have no rows.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md), in the order of the files.
entries : Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}, one
    per event of the summary, in the same order.
skip_word : str
    The label that leaves an event out; its row's concentration is greyed out.

---- Globals read ----
LABEL_COLUMNS.

---- Outputs ----
dict
    The table to show (table_rows, DATA_FORMAT.md).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_number_writer
```

#### `od_rows_reader`

```text
---- Summary ----
Main function to take the values typed in the OD table back as the OD values of
each file.

---- Inputs ----
table : dict
    The OD table that was shown (od_table_builder, table_rows, DATA_FORMAT.md).
values : List[Dict[str, Any]]
    What AnswerTable.values_reader gave for it, row by row.

---- Globals read ----
OD_COLUMNS.

---- Outputs ----
Dict[str, Dict[str, Optional[float]]]
    {file name: {'OD', 'volume', 'dilution_factor'}} in the order of the rows
    (od_rows, DATA_FORMAT.md).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `od_table_builder`

```text
---- Summary ----
Main function to lay out the OD table: one row per file, with its OD, volume and
dilution.

---- Inputs ----
rows : Dict[str, Dict[str, Optional[float]]]
    {file name: {'OD', 'volume', 'dilution_factor'}} in the order of the files; a
    value that is None or missing leaves its cell empty (od_rows, DATA_FORMAT.md).

---- Globals read ----
OD_COLUMNS.

---- Outputs ----
dict
    The table to show (table_rows, DATA_FORMAT.md).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_number_writer
```

#### `table_problem_teller`

```text
---- Summary ----
Main function to say in one sentence what is still wrong in a table when Confirm is
pressed: the cells that hold something that cannot be used first, then the needed
cells left empty.

---- Inputs ----
problems : List[Tuple[str, str]]
    What AnswerTable.problems_lister gave: (cell name, problem).

---- Globals read ----
EMPTY, KIND_HINTS.

---- Outputs ----
Optional[str]
    The sentence, or None when the table can be used.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_cell_name_joiner
```

#### `wheel_step_finder`

```text
---- Summary ----
Main function to say which way a turn of the mouse wheel scrolls, whichever system
sent it: Windows and the Mac give a turn as a positive or negative amount, Linux as
a press of button 4 (up) or 5 (down).

---- Inputs ----
event : Any
    The Tk event, with ``num`` (the button) and ``delta`` (the amount turned).

---- Globals read ----
None.

---- Outputs ----
int
    -1 to scroll up, 1 to scroll down, 0 when the event says neither.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_viewer/viewer_terminal.py`

Text terminal of the experiment browser window: colour codes and output streams.

### CLASSES

#### `OutputRouter`

```text
---- Summary ----
File-like object that replaces sys.stdout and sys.stderr while the browser window
is open. What the program's own thread prints goes to the terminal in the window;
what other threads print goes to the real stream; and a thread that is capturing its
output (output_capturer) keeps it to itself.

---- Attributes ----
encoding : str
    Always "utf-8".

---- Globals read ----
None.

---- Methods ----
__init__
__getattr__
fileno
flush
isatty
reconfigure
write
```

##### `__init__`

```text
---- Summary ----
Method to store where the text goes.

---- Inputs ----
original : Any
    The stream that was replaced; used for other threads and after the window is
    closed.
sender : Callable[[str, str], None]
    Function that passes (text, kind) to the window.
kind : str
    'out' for standard output or 'err' for standard error.
owner : Callable[[], Optional[threading.Thread]]
    Function that gives the thread whose output belongs in the window (None
    once the window is closed).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__getattr__`

```text
---- Summary ----
Method to pass any other attribute lookup to the stream that was replaced.

---- Inputs ----
name : str
    Attribute name that was not found on the instance.

---- Globals read ----
None.

---- Outputs ----
Any
    The attribute of the original stream.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `fileno`

```text
---- Summary ----
Method that says there is no file descriptor, so libraries that ask for one fall
back to plain writes. The name is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
int
    Never returns; raises io.UnsupportedOperation.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `flush`

```text
---- Summary ----
Method that does nothing: text is passed on as soon as it is written. The name
is fixed by the file-like protocol.

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
```

##### `isatty`

```text
---- Summary ----
Method to say that the stream shows colour, because the terminal in the window
does. The name is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    Always True.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `reconfigure`

```text
---- Summary ----
Method that accepts and ignores new stream settings, because the window shows
every symbol.

---- Inputs ----
**kwargs : Any
    Stream settings (ignored).

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
```

##### `write`

```text
---- Summary ----
Method to send text where it belongs: the capture of the thread, the window, or
the real stream. The name is fixed by the file-like protocol.

---- Inputs ----
text : str
    Text to write.

---- Globals read ----
None.

---- Outputs ----
int
    Number of characters written.

---- Globals mutated ----
None. Passes text to the window or the real stream (side effect).

---- Equations ----
None.

---- Helpers ----
captured_buffer_getter
```

### TERMINAL HELPERS

#### `ansi_colour_getter`

```text
---- Summary ----
Main function to give the colour of an entry of the 256-colour terminal palette.

---- Inputs ----
index : int
    Palette number, 0 to 255 (0-15 basic, 16-231 colour cube, 232-255 greys).

---- Globals read ----
BASIC_COLOURS (module constant).

---- Outputs ----
str
    The colour as "#rrggbb".

---- Globals mutated ----
None.

---- Equations ----
Cube colours: each of red, green and blue is 0 for level 0 and 55 + 40 * level
for levels 1 to 5, where index - 16 = 36 * red level + 6 * green level + blue
level. Greys: 8 + 10 * (index - 232).

---- Helpers ----
None.
```

#### `ansi_splitter`

```text
---- Summary ----
Main function to cut printed text into plain text, colour codes and carriage
returns, in order, so a text window can colour the text and overwrite progress
lines.

---- Inputs ----
text : str
    Text as printed, possibly with colour codes (ESC[...m) and carriage returns.

---- Globals read ----
_CODE_PATTERN (module constant).

---- Outputs ----
List[Tuple[str, str]]
    [(kind, value)] with kind 'text' (the characters), 'code' (the numbers of a
    colour code, for example "1;33") or 'return' (value empty). A carriage return
    directly before a new line is part of the line ending and is dropped.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `ansi_style_updater`

```text
---- Summary ----
Main function to apply one colour code to the current text style.

---- Inputs ----
style : Dict[str, Any]
    {fg, bold, italic}: colour as "#rrggbb" or None for the default, and two flags.
code : str
    Numbers of the colour code, separated by semicolons ("" means reset).

---- Globals read ----
BASIC_COLOURS (module constant).

---- Outputs ----
Dict[str, Any]
    The new style; ``style`` is not changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
ansi_colour_getter
```
