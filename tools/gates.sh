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

echo "ALL DONE"
