#!/usr/bin/env bash
# The full gate: the test suite, then every experiment module in this repo that carries a registered claim.
#
#   bash tools/gates.sh            # silent except for non-zero exits and "ALL DONE"
#
# Each unit's output goes to /tmp/gate_<name>.log, so a failure can be read back without re-running the sweep.
# The units read their inputs from `runs/`, which is gitignored: a fresh clone has no corpus, and the readers
# report REFUSED for the claims they cannot compute rather than inventing a number. Regenerate the corpus with
# the runners the plan's rows name (`experiments/e2_topology_gap.py` and the modules beside it).
set -u
[ -d "$HOME/.local/bin" ] && export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."

run() {
  name="$1"; shift
  uv run "$@" > "/tmp/gate_${name}.log" 2>&1
  code=$?
  echo "EXIT $code : $name"
}

run pytest pytest -q
run e127 python -m experiments.e127_programme_table_audit
run e163 python -m experiments.e163_repeat_floor
run e126 python -m experiments.e126_enumeration_audit
run e132 python -m experiments.e132_derivation_audit
run e182 python -m experiments.e182_command_prose_audit
run e184 python -m experiments.e184_artifact_citation_census
run e185 python -m experiments.e185_benchmark_spec_audit
run e187 python -m experiments.e187_suite_provenance
run e188 python -m experiments.e188_overlap_contrast
run e189 python -m experiments.e189_overlap_sign_across_lines
run e190 python -m experiments.e190_side_rung_read
run e191 python -m experiments.e191_interference_across_lines
run e192 python -m experiments.e192_paper_numbers
run e194 python -m experiments.e194_s_claims_read
run e198 python -m experiments.e198_artifact_draw_census
run e200 python -m experiments.e200_draw_confound_audit
run e201 python -m experiments.e201_single_draw_family_census
run e203 python -m experiments.e203_ladder_draw_read
run e97 python -m experiments.e97_findings_corpus_audit
run e105 python -m experiments.e105_table_audit --findings docs/findings
run e205 python -m experiments.e205_duration_field_census
run e229 python -m experiments.e229_read_rho_sweep
run e230 python -m experiments.e230_rank_draw_census
run e244 python -m experiments.e244_drawing_spread_by_kind --json-out runs/e244_drawing_spread_by_kind.json
run e246 python -m experiments.e246_spread_volatility_by_family --json-out runs/e246_spread_volatility_by_family.json
run e247 python -m experiments.e247_count_matched_spread --json-out runs/e247_count_matched_spread.json
run e248 python -m experiments.e248_equal_count_base --json-out runs/e248_equal_count_base.json
run e249 python -m experiments.e249_third_cell_margin --json-out runs/e249_third_cell_margin.json
run e250 python -m experiments.e250_second_count_three_base --json-out runs/e250_second_count_three_base.json
run e251 python -m experiments.e251_rho_axis_margin --json-out runs/e251_rho_axis_margin.json
run e252 python -m experiments.e252_spread_domain --json-out runs/e252_spread_domain.json
run e253 python -m experiments.e253_two_drawings_at_high_rho --json-out runs/e253_two_drawings_at_high_rho.json
run e254 python -m experiments.e254_quoted_figure_census --json-out runs/e254_quoted_figure_census.json
run e255 python -m experiments.e255_low_rho_cells --json-out runs/e255_low_rho_cells.json
run e256 python -m experiments.e256_cs800_rank_curve --json-out runs/e256_cs800_rank_curve.json
run e257 python -m experiments.e257_audit_on_means --json-out runs/e257_audit_on_means.json
run e258 python -m experiments.e258_floor_task_draw_band --json-out runs/e258_floor_task_draw_band.json
run e259 python -m experiments.e259_c2b_null_power --json-out runs/e259_c2b_null_power.json
run e260 python -m experiments.e260_domain_in_the_readers --json-out runs/e260_domain_in_the_readers.json
run e261 python -m experiments.e261_three_rep_floor_measured --json-out runs/e261_three_rep_floor_measured.json

run e262 python -m experiments.e262_replicate_order_is_not_a_variable --json-out runs/e262_replicate_order_is_not_a_variable.json

run e263 python -m experiments.e263_what_the_pairing_shares --json-out runs/e263_what_the_pairing_shares.json

run e264 python -m experiments.e264_the_third_arm --json-out runs/e264_the_third_arm.json

run e265 python -m experiments.e265_the_arm_ladder_over_the_corpus --json-out runs/e265_the_arm_ladder_over_the_corpus.json

run e267 python -m experiments.e267_the_test_set_the_benchmark_would_need --json-out runs/e267_the_test_set_the_benchmark_would_need.json

run e268 python -m experiments.e268_paper_supersession_audit --json-out runs/e268_paper_supersession_audit.json

run e269 python -m experiments.e269_the_price_of_a_held_out_item --json-out runs/e269_the_price_of_a_held_out_item.json

run e270 python -m experiments.e270_an_existence_premise_falsified --json-out runs/e270_an_existence_premise_falsified.json

run e271 python -m experiments.e271_the_pairing_is_not_uniformly_a_gain --json-out runs/e271_the_pairing_is_not_uniformly_a_gain.json

run e266 python -m experiments.e266_matched_settings_read --json-out runs/e266_matched_settings_read.json

run e272 python -m experiments.e272_the_budget_the_ordering_needs --json-out runs/e272_the_budget_the_ordering_needs.json

run e273 python -m experiments.e273_the_pairing_falls_with_the_overlap --json-out runs/e273_the_pairing_falls_with_the_overlap.json

run e274 python -m experiments.e274_the_leader_is_not_bought_either --json-out runs/e274_the_leader_is_not_bought_either.json

run e276 python -m experiments.e276_replay_against_the_penalty --json-out runs/e276_replay_against_the_penalty.json

run e277 python -m experiments.e277_a_count_is_not_a_scope --json-out runs/e277_a_count_is_not_a_scope.json

run e278 python -m experiments.e278_on_disk_is_not_a_definition --json-out runs/e278_on_disk_is_not_a_definition.json

run e279 python -m experiments.e279_every_one_of_the_77 --json-out runs/e279_every_one_of_the_77.json

run e280 python -m experiments.e280_the_positive_control --json-out runs/e280_the_positive_control.json

run e281 python -m experiments.e281_the_correction_ledger --json-out runs/e281_the_correction_ledger.json

run e282 python -m experiments.e282_the_coverage_of_the_series --json-out runs/e282_the_coverage_of_the_series.json

run e283 python -m experiments.e283_the_registry_it_names --json-out runs/e283_the_registry_it_names.json

run e284 python -m experiments.e284_the_last_row_without_an_artifact --json-out runs/e284_the_last_row_without_an_artifact.json

run e275 python -m experiments.e275_the_suite_makes_it_visible --json-out runs/e275_the_suite_makes_it_visible.json

run e285 python -m experiments.e285_two_runs_one_model --json-out runs/e285_two_runs_one_model.json

run e286 python -m experiments.e286_the_fall_is_not_the_samples_size --json-out runs/e286_the_fall_is_not_the_samples_size.json

run e287 python -m experiments.e287_the_rejections_and_the_prefix --json-out runs/e287_the_rejections_and_the_prefix.json

run e289 python -m experiments.e289_the_share_is_solved_for --json-out runs/e289_the_share_is_solved_for.json

run e290 python -m experiments.e290_the_floor_is_not_an_independent_draw --json-out runs/e290_the_floor_is_not_an_independent_draw.json

run e291 python -m experiments.e291_what_the_suite_bought --json-out runs/e291_what_the_suite_bought.json

run e292 python -m experiments.e292_the_readout_sets_the_floor_share --json-out runs/e292_the_readout_sets_the_floor_share.json

run e293 python -m experiments.e293_how_many_draws_a_draw_sd_needs --json-out runs/e293_how_many_draws_a_draw_sd_needs.json

run e294 python -m experiments.e294_the_pairing_in_the_corpus --json-out runs/e294_the_pairing_in_the_corpus.json

run e295 python -m experiments.e295_which_metric_selects_the_basis --json-out runs/e295_which_metric_selects_the_basis.json

run e296 python -m experiments.e296_the_matched_random_control --json-out runs/e296_the_matched_random_control.json

run e297 python -m experiments.e297_the_ordering_of_the_arms --json-out runs/e297_the_ordering_of_the_arms.json

run e298 python -m experiments.e298_the_recommendation_needs_a_comparator --json-out runs/e298_the_recommendation_needs_a_comparator.json

run e299 python -m experiments.e299_the_front_page_claim --json-out runs/e299_the_front_page_claim.json

run e300 python -m experiments.e300_the_abstracts_findings --json-out runs/e300_the_abstracts_findings.json

run e301 python -m experiments.e301_the_corpus_holds_repeats --json-out runs/e301_the_corpus_holds_repeats.json

run e302 python -m experiments.e302_the_benchmark_metrics --json-out runs/e302_the_benchmark_metrics.json

run e303 python -m experiments.e303_the_metrics_against_definitions --json-out runs/e303_the_metrics_against_definitions.json

run e304 python -m experiments.e304_the_decomposition_the_block_asked_for --json-out runs/e304_the_decomposition_the_block_asked_for.json

run e305 python -m experiments.e305_the_arms_that_forget_nothing --json-out runs/e305_the_arms_that_forget_nothing.json

run e306 python -m experiments.e306_the_ordering_in_the_other_currency --json-out runs/e306_the_ordering_in_the_other_currency.json

run e307 python -m experiments.e307_the_scope_in_the_fields_currency --json-out runs/e307_the_scope_in_the_fields_currency.json

run e308 python -m experiments.e308_the_unit_of_the_vote --json-out runs/e308_the_unit_of_the_vote.json

run e309 python -m experiments.e309_the_conformance_contract --json-out runs/e309_the_conformance_contract.json

run e310 python -m experiments.e310_the_position_effect --json-out runs/e310_the_position_effect.json

run e311 python -m experiments.e311_the_two_tasks_the_metric_averages --json-out runs/e311_the_two_tasks_the_metric_averages.json

run e312 python -m experiments.e312_the_shortfall_is_the_accuracy --json-out runs/e312_the_shortfall_is_the_accuracy.json

run e313 python -m experiments.e313_the_decomposition_is_three_fields --json-out runs/e313_the_decomposition_is_three_fields.json

run e314 python -m experiments.e314_the_contract_with_the_result_block --json-out runs/e314_the_contract_with_the_result_block.json

run e315 python -m experiments.e315_the_order_the_runner_never_took --json-out runs/e315_the_order_the_runner_never_took.json

run e316 python -m experiments.e316_the_reversal_in_the_other_family --json-out runs/e316_the_reversal_in_the_other_family.json

run e317 python -m experiments.e317_the_reversal_with_five_arms --json-out runs/e317_the_reversal_with_five_arms.json

run e318 python -m experiments.e318_the_penalty_switched_off --json-out runs/e318_the_penalty_switched_off.json

run e319 python -m experiments.e319_the_penalty_four_times --json-out runs/e319_the_penalty_four_times.json

run e320 python -m experiments.e320_the_order_sentence --json-out runs/e320_the_order_sentence.json

run e321 python -m experiments.e321_the_replay_contrast_survives_the_order --json-out runs/e321_the_replay_contrast_survives_the_order.json

run e322 python -m experiments.e322_the_benchmark_has_no_time_in_it --json-out runs/e322_the_benchmark_has_no_time_in_it.json

run e323 python -m experiments.e323_the_trial_gets_a_second_half --json-out runs/e323_the_trial_gets_a_second_half.json

run e324 python -m experiments.e324_what_the_time_axis_costs --json-out runs/e324_what_the_time_axis_costs.json

run e325 python -m experiments.e325_the_loop_closes --json-out runs/e325_the_loop_closes.json

run e326 python -m experiments.e326_training_through_the_loop --json-out runs/e326_training_through_the_loop.json

run e327 python -m experiments.e327_the_feedback_is_a_dose --json-out runs/e327_the_feedback_is_a_dose.json

run e328 python -m experiments.e328_is_the_middling_loop_worse --json-out runs/e328_is_the_middling_loop_worse.json

run e329 python -m experiments.e329_the_environment_gets_a_noisy_cue --json-out runs/e329_the_environment_gets_a_noisy_cue.json

run e330 python -m experiments.e330_the_cost_needs_the_ceiling --json-out runs/e330_the_cost_needs_the_ceiling.json

run e331 python -m experiments.e331_the_ordering_under_the_loop --json-out runs/e331_the_ordering_under_the_loop.json

run e332 python -m experiments.e332_the_world_answers_with_a_state --json-out runs/e332_the_world_answers_with_a_state.json

run e333 python -m experiments.e333_the_world_gets_a_rule --json-out runs/e333_the_world_gets_a_rule.json

run e334 python -m experiments.e334_what_replay_is_scored_on --json-out runs/e334_what_replay_is_scored_on.json

run e335 python -m experiments.e335_what_replay_stores --json-out runs/e335_what_replay_stores.json

run e336 python -m experiments.e336_the_direction_of_the_update --json-out runs/e336_the_direction_of_the_update.json

run e337 python -m experiments.e337_does_it_replicate_on_another_stream --json-out runs/e337_does_it_replicate_on_another_stream.json

run e338 python -m experiments.e338_the_same_body_asked_both_questions --json-out runs/e338_the_same_body_asked_both_questions.json

run e339 python -m experiments.e339_is_the_ordering_immune_to_the_redraw --json-out runs/e339_is_the_ordering_immune_to_the_redraw.json

run e340 python -m experiments.e340_the_clean_seed_stream --json-out runs/e340_the_clean_seed_stream.json

run e341 python -m experiments.e341_forty_replicates_on_the_clean_stream --json-out runs/e341_forty_replicates_on_the_clean_stream.json

run e342 python -m experiments.e342_the_channel_across_strengths --json-out runs/e342_the_channel_across_strengths.json

run e343 python -m experiments.e343_a_readout_that_looks --json-out runs/e343_a_readout_that_looks.json

run e344 python -m experiments.e344_the_latch_hypothesis --json-out runs/e344_the_latch_hypothesis.json

run e345 python -m experiments.e345_a_wider_readout --json-out runs/e345_a_wider_readout.json

run e346 python -m experiments.e346_does_the_method_contrast_travel --json-out runs/e346_does_the_method_contrast_travel.json

run e347 python -m experiments.e347_the_family_that_disagrees --json-out runs/e347_the_family_that_disagrees.json

run e348 python -m experiments.e348_can_the_world_be_the_readout --json-out runs/e348_can_the_world_be_the_readout.json

run e349 python -m experiments.e349_the_body_writes_the_cue --json-out runs/e349_the_body_writes_the_cue.json

run e350 python -m experiments.e350_the_world_gets_a_dimension --json-out runs/e350_the_world_gets_a_dimension.json

run e351 python -m experiments.e351_one_number_two_channels --json-out runs/e351_one_number_two_channels.json

run e352 python -m experiments.e352_the_earned_label_suite --json-out runs/e352_the_earned_label_suite.json

run e353 python -m experiments.e353_the_class_incremental_earned_label --json-out runs/e353_the_class_incremental_earned_label.json

run e354 python -m experiments.e354_both_protocols_in_one_module --json-out runs/e354_both_protocols_in_one_module.json

run e355 python -m experiments.e355_the_earned_label_through_the_runner --json-out runs/e355_the_earned_label_through_the_runner.json

run e356 python -m experiments.e356_the_earned_label_at_twenty_replicates --json-out runs/e356_the_earned_label_at_twenty_replicates.json

run e357 python -m experiments.e357_the_basis_contrast_on_the_earned_label --json-out runs/e357_the_basis_contrast_on_the_earned_label.json

run e358 python -m experiments.e358_the_frozen_body_on_the_earned_label --json-out runs/e358_the_frozen_body_on_the_earned_label.json

run e359 python -m experiments.e359_the_world_gets_its_own_dynamics --json-out runs/e359_the_world_gets_its_own_dynamics.json

run e360 python -m experiments.e360_the_world_gets_a_nonlinearity --json-out runs/e360_the_world_gets_a_nonlinearity.json

run e361 python -m experiments.e361_the_world_memory --json-out runs/e361_the_world_memory.json

run e362 python -m experiments.e362_the_cue_at_the_read_step --json-out runs/e362_the_cue_at_the_read_step.json

run e363 python -m experiments.e363_where_the_cue_can_reach_the_world --json-out runs/e363_where_the_cue_can_reach_the_world.json

run e364 python -m experiments.e364_can_training_beat_the_interface --json-out runs/e364_can_training_beat_the_interface.json

run e365 python -m experiments.e365_the_interface_knob_as_a_task --json-out runs/e365_the_interface_knob_as_a_task.json

run e366 python -m experiments.e366_what_the_probes_gap_is_made_of --json-out runs/e366_what_the_probes_gap_is_made_of.json

run e367 python -m experiments.e367_the_world_the_agent_drives --json-out runs/e367_the_world_the_agent_drives.json

run e368 python -m experiments.e368_how_long_the_channel_takes_to_fill --json-out runs/e368_how_long_the_channel_takes_to_fill.json

run e369 python -m experiments.e369_why_the_cliff_is_where_it_is --json-out runs/e369_why_the_cliff_is_where_it_is.json

run e370 python -m experiments.e370_the_distance_moves_the_cliff --json-out runs/e370_the_distance_moves_the_cliff.json

run e371 python -m experiments.e371_the_game_the_agent_can_play --json-out runs/e371_the_game_the_agent_can_play.json

run e372 python -m experiments.e372_what_acting_costs --json-out runs/e372_what_acting_costs.json

run e373 python -m experiments.e373_the_price_of_acting_across_the_window --json-out runs/e373_the_price_of_acting_across_the_window.json

run e374 python -m experiments.e374_the_tightest_step --json-out runs/e374_the_tightest_step.json

run e375 python -m experiments.e375_is_it_the_body --json-out runs/e375_is_it_the_body.json

run e376 python -m experiments.e376_the_heads_own_fitting --json-out runs/e376_the_heads_own_fitting.json

run e377 python -m experiments.e377_was_it_the_step_size --json-out runs/e377_was_it_the_step_size.json

run e378 python -m experiments.e378_the_cue_source_at_the_tight_step --json-out runs/e378_the_cue_source_at_the_tight_step.json

run e379 python -m experiments.e379_what_the_body_did --json-out runs/e379_what_the_body_did.json

run e380 python -m experiments.e380_what_the_training_built --json-out runs/e380_what_the_training_built.json

run e381 python -m experiments.e381_the_representations_retention_matrix --json-out runs/e381_the_representations_retention_matrix.json

run e382 python -m experiments.e382_when_the_world_loses_it --json-out runs/e382_when_the_world_loses_it.json

run e383 python -m experiments.e383_the_collapse_at_two_step_sizes --json-out runs/e383_the_collapse_at_two_step_sizes.json

run e384 python -m experiments.e384_the_other_end_of_the_window --json-out runs/e384_the_other_end_of_the_window.json

run e385 python -m experiments.e385_the_valleys_shape --json-out runs/e385_the_valleys_shape.json

run e386 python -m experiments.e386_a_wider_world --json-out runs/e386_a_wider_world.json

run e387 python -m experiments.e387_the_window_as_one_setting --json-out runs/e387_the_window_as_one_setting.json

run e388 python -m experiments.e388_the_floor_between_five_and_twenty --json-out runs/e388_the_floor_between_five_and_twenty.json

run e389 python -m experiments.e389_the_interval_at_twenty_replicates --json-out runs/e389_the_interval_at_twenty_replicates.json

run e390 python -m experiments.e390_where_the_climb_starts --json-out runs/e390_where_the_climb_starts.json

run e391 python -m experiments.e391_the_far_stretch --json-out runs/e391_the_far_stretch.json

run e392 python -m experiments.e392_the_game_card --json-out runs/e392_the_game_card.json

run e393 python -m experiments.e393_the_card_on_four_more_worlds --json-out runs/e393_the_card_on_four_more_worlds.json

run e394 python -m experiments.e394_the_card_on_three_more_streams --json-out runs/e394_the_card_on_three_more_streams.json

run e395 python -m experiments.e395_the_far_point_on_more_worlds --json-out runs/e395_the_far_point_on_more_worlds.json

run e396 python -m experiments.e396_the_far_point_on_all_five_worlds --json-out runs/e396_the_far_point_on_all_five_worlds.json

run e397 python -m experiments.e397_the_two_hop_world --json-out runs/e397_the_two_hop_world.json

run e398 python -m experiments.e398_the_cue_population_alone --json-out runs/e398_the_cue_population_alone.json

run e399 python -m experiments.e399_the_rest_of_the_two_hop_class --json-out runs/e399_the_rest_of_the_two_hop_class.json

run e400 python -m experiments.e400_five_candidates_for_the_one --json-out runs/e400_five_candidates_for_the_one.json

run e401 python -m experiments.e401_the_heaviest_untrained_draw --json-out runs/e401_the_heaviest_untrained_draw.json

run e402 python -m experiments.e402_the_trained_bodies --json-out runs/e402_the_trained_bodies.json

run e403 python -m experiments.e403_the_far_point_on_the_clean_stream --json-out runs/e403_the_far_point_on_the_clean_stream.json

run e404 python -m experiments.e404_the_cue_population_in_the_annotation_table --json-out runs/e404_the_cue_population_in_the_annotation_table.json

run e405 python -m experiments.e405_one_update_on_all_six_worlds --json-out runs/e405_one_update_on_all_six_worlds.json

run e406 python -m experiments.e406_two_updates_on_all_six_worlds --json-out runs/e406_two_updates_on_all_six_worlds.json

run e407 python -m experiments.e407_five_budgets_on_all_six_worlds --json-out runs/e407_five_budgets_on_all_six_worlds.json

run e408 python -m experiments.e408_six_budgets_on_all_six_worlds --json-out runs/e408_six_budgets_on_all_six_worlds.json

run e409 python -m experiments.e409_the_game_card_revision_two --json-out runs/e409_the_game_card_revision_two.json

run e410 python -m experiments.e410_the_benchmarks_own_metric --json-out runs/e410_the_benchmarks_own_metric.json

run e411 python -m experiments.e411_the_rehearsal_on_the_six_worlds --json-out runs/e411_the_rehearsal_on_the_six_worlds.json

run e412 python -m experiments.e412_the_aid_turns_on --json-out runs/e412_the_aid_turns_on.json

run e413 python -m experiments.e413_the_aid_turns_on_in_every_world --json-out runs/e413_the_aid_turns_on_in_every_world.json

run e414 python -m experiments.e414_the_game_card_revision_three --json-out runs/e414_the_game_card_revision_three.json

run e415 python -m experiments.e415_the_penalty_on_the_cards_world --json-out runs/e415_the_penalty_on_the_cards_world.json

run e416 python -m experiments.e416_the_penalty_ledger --json-out runs/e416_the_penalty_ledger.json

run e417 python -m experiments.e417_the_aid_needs_a_plastic_body --json-out runs/e417_the_aid_needs_a_plastic_body.json

run e418 python -m experiments.e418_the_game_card_revision_four --json-out runs/e418_the_game_card_revision_four.json

run e419 python -m experiments.e419_what_the_buffer_buys --json-out runs/e419_what_the_buffer_buys.json

run e420 python -m experiments.e420_the_trade_is_a_constant --json-out runs/e420_the_trade_is_a_constant.json

run e421 python -m experiments.e421_the_trade_turns_on --json-out runs/e421_the_trade_turns_on.json

run e422 python -m experiments.e422_the_buffer_buys_retention --json-out runs/e422_the_buffer_buys_retention.json

run e423 python -m experiments.e423_the_penalty_buys_a_tenth --json-out runs/e423_the_penalty_buys_a_tenth.json

run e424 python -m experiments.e424_the_game_card_revision_five --json-out runs/e424_the_game_card_revision_five.json

run e425 python -m experiments.e425_the_trade_follows_the_position --json-out runs/e425_the_trade_follows_the_position.json

run e426 python -m experiments.e426_the_damage_lands_by_arm --json-out runs/e426_the_damage_lands_by_arm.json

run e427 python -m experiments.e427_most_of_the_aid_needs_a_plastic_bias --json-out runs/e427_most_of_the_aid_needs_a_plastic_bias.json

run e428 python -m experiments.e428_the_game_card_revision_six --json-out runs/e428_the_game_card_revision_six.json

run e429 python -m experiments.e429_the_front_page_gets_the_benchmark --json-out runs/e429_the_front_page_gets_the_benchmark.json

run e430 python -m experiments.e430_where_the_bias_goes --json-out runs/e430_where_the_bias_goes.json

run e431 python -m experiments.e431_the_bias_ledger --json-out runs/e431_the_bias_ledger.json

run e432 python -m experiments.e432_the_interference_runs_through_the_bias --json-out runs/e432_the_interference_runs_through_the_bias.json

run e433 python -m experiments.e433_the_penalties_hold_the_weights --json-out runs/e433_the_penalties_hold_the_weights.json

run e434 python -m experiments.e434_the_game_card_revision_seven --json-out runs/e434_the_game_card_revision_seven.json

run e435 python -m experiments.e435_the_front_pages_second_region --json-out runs/e435_the_front_pages_second_region.json

run e436 python -m experiments.e436_the_order_the_world_is_taught_in --json-out runs/e436_the_order_the_world_is_taught_in.json

run e437 python -m experiments.e437_three_orders_on_the_world --json-out runs/e437_the_three_orders_on_the_world.json

run e438 python -m experiments.e438_the_penalty_arm_on_the_card --json-out runs/e438_the_penalty_arm_on_the_card.json

run e439 python -m experiments.e439_the_matched_random_partition_on_the_card --json-out runs/e439_the_matched_random_partition_on_the_card.json

run e440 python -m experiments.e440_where_the_anchors_movement_goes --json-out runs/e440_where_the_anchors_movement_goes.json

run e441 python -m experiments.e441_the_anchors_price_under_another_order --json-out runs/e441_the_anchors_price_under_another_order.json

run e442 python -m experiments.e442_the_two_parameters_under_two_orders --json-out runs/e442_the_two_parameters_under_two_orders.json

run e443 python -m experiments.e443_the_ledger_on_a_second_world --json-out runs/e443_the_ledger_on_a_second_world.json

run e444 python -m experiments.e444_the_decoders_draw --json-out runs/e444_the_decoders_draw.json

echo "ALL DONE"
