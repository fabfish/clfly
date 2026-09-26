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

echo "ALL DONE"
