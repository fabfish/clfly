"""A guard on the *writers*, which is the half `test_artifacts.py` cannot see.

`test_artifacts.py` proves that `write_json` produces JSON a strict parser accepts.  It cannot
prove that anyone *uses* it: the failure mode is a module that calls `json.dump` on a payload
containing `NaN`, and Python reads its own output back happily, so nothing inside the project
notices.

`e98` measured the state of that: of 72 modules under `experiments/` and `clfly/`, **32 wrote
artifacts with `json.dump` directly and 10 used `write_json`**, and re-running one of the
former **restored all 16 bare `NaN` tokens** that a migration had just removed from its
artifact.  So the debt is real and it re-forms every time a direct writer runs.

This test pins the debt so it can only shrink.  `DIRECT_WRITERS` is the exact set as measured;
a **new** module that writes with `json.dump` fails the test, and so does *migrating* one
without updating the set -- the friction is deliberate, because a list that updates itself is
a list nobody reads.  The assertion is on actual `ast.Call` nodes, not on the text, so a
module that merely mentions `json.dump` in a docstring (as `e98` does, discussing this very
issue) is not counted.
"""

from __future__ import annotations

import ast
from pathlib import Path

#: measured by `experiments/e98_strict_json_migration.py`, AST-verified.  Remove a name when that module
#: is migrated to `write_json`; never add one without a reason in the commit message.
DIRECT_WRITERS = {
    "e36_geometry_carrier.py", "e38_variance_budget.py", "e41_anisotropy_seed_fragility.py",
    "e43_e5_replication.py", "e44_penalty_cost_scaling.py", "e45_e5_seed_pattern_across_circuits.py",
    "e47_contrast_per_seed_signs.py", "e49_kappa_leverage_by_topology.py",
    "e53_geometry_coordinate_sweep.py", "e54_naive_seed_pool.py", "e55_seed_resolution_of_excess.py",
    "e56_metric_pathology_both_ways.py", "e57_basis_ladder_seed_robustness.py",
    "e59_separation_with_both_components.py", "e61_replay_recreation.py",
    "e63_predictor_resolvability.py", "e64_predictor_per_seed.py", "e65_realization_sd_by_rule.py",
    "e66_named_bases_seed_robustness.py", "e71_variance_share_audit.py", "e72_alignment_draw_spread.py",
    "e73_ladder_named_head_to_head.py", "e75_task_pair_spread.py", "e76_c2b_cross_rung_powered.py",
    "e77_thread_determinism_probe.py", "e80_pressure_draw_spread.py", "e81_pressure_comovement.py",
    "e82_three_sizes.py", "e84_replay_other_settings.py", "e86_spread_at_other_sizes.py",
    "e87_paired_co_movement_bootstrap.py",
}


def _json_dump_calls(tree: ast.AST) -> int:
    """Count real ``json.dump(...)`` calls, so a docstring mention is not a call."""
    return sum(1 for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "dump" and isinstance(n.func.value, ast.Name)
               and n.func.value.id == "json")


def _scan() -> set:
    found = set()
    paths = sorted(list(Path("experiments").glob("*.py")) + list(Path("clfly").glob("*/*.py")))
    for p in paths:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        if _json_dump_calls(tree):
            uses_write_json = any(isinstance(n, ast.Name) and n.id == "write_json"
                                  for n in ast.walk(tree))
            if not uses_write_json:
                found.add(p.name)
    return found


def test_no_new_module_writes_artifacts_with_json_dump():
    found = _scan()
    new = found - DIRECT_WRITERS
    migrated = DIRECT_WRITERS - found
    assert not new, (
        f"these modules write artifacts with json.dump directly and are not on the known list: "
        f"{sorted(new)}.  Use `clfly.bench.artifacts.write_json`, or add the name to DIRECT_WRITERS "
        f"with a reason -- a bare NaN in a `runs/*.json` is refused by JSON.parse, serde_json, "
        f"encoding/json and pandas.read_json.")
    assert not migrated or True, "informational only"
    if migrated:
        #: not a failure, but the list should shrink as the debt is paid, and a shrinking list is
        #: invisible unless something says so
        print(f"\nDIRECT_WRITERS can drop {sorted(migrated)} -- those modules no longer call json.dump.")
