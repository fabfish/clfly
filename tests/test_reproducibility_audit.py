"""The reproducibility audit's two checks, on synthetic artifacts.

These are unit tests rather than a run on `runs/`, because `runs/` is gitignored and absent from a fresh
checkout -- the same reason `tests/test_artifact_writers.py` counts AST nodes instead of reading files. The
cases here are the ones that make the audit's answers mean something:

  * a config's identity must ignore `json_out`, or **no two runs of one command ever group** and the audit
    reports "0 repeated configurations" instead of reporting an unreproducible arm;
  * an arm must be compared as a *value* (exactness), with movement reported separately rather than folded in,
    because rule 21 measured that the torch path is environment-shaped at about the fourth digit;
  * a method one member lacks (`--methods naive,replay` against a five-arm run) is absent, not unequal;
  * the epoch check must stay inside a runner's family and off aggregate artifacts, which is what the first
    two drafts of it got wrong -- one reported 50 rows of noise, the next reported a hand-built summary's
    config as an artifact that predates a flag.
"""

from __future__ import annotations

import json

from experiments.e103_reproducibility_audit import (
    arm_matches,
    epoch_flags,
    family,
    group_repeats,
    load_artifacts,
    maximal_keyset,
    signature,
)


def artifact(name, config, methods=None, replicates=None):
    """A payload shaped like a benchmark run's, with one replicate list per named method."""
    payload = {"config": config}
    if methods is not None:
        payload["methods"] = {
            m: {"replicates": replicates[m], "mean_forgetting": replicates[m][0]["mean_forgetting"],
                "final_accuracy": replicates[m][0]["final_accuracy"]} for m in methods}
    return {"name": name, "config": config, "payload": payload, "mtime": 0.0}


def reps(*learned):
    """One replicate list, one entry per seed, from the `learned` vectors given."""
    return [{"learned": list(v), "mean_forgetting": round(0.1 * i, 6),
             "retention": [[1.0, None], [1.0, 1.0]], "final_accuracy": 0.9} for i, v in enumerate(learned)]


BASE = {"circuit_size": 800, "lam": 0.003, "fisher_batches": 8, "json_out": "runs/a.json"}


# --- the config identity ---------------------------------------------------------------------------

def test_signature_ignores_the_output_path():
    """The trap: without this, every artifact is its own group and the audit reports nothing."""
    other = dict(BASE, json_out="runs/b.json")
    assert signature(BASE) == signature(other)


def test_signature_keeps_the_manipulated_variable():
    assert signature(BASE) != signature(dict(BASE, fisher_batches=128))


# --- arm-level comparison --------------------------------------------------------------------------

def test_an_arm_that_reproduces_is_exact():
    a = artifact("x", BASE, ["naive"], {"naive": reps([1.0], [0.9])})
    b = artifact("y", BASE, ["naive"], {"naive": reps([1.0], [0.9])})
    got = arm_matches([a, b], "naive")
    assert got["exact"] is True
    assert got["movement_forgetting"] == 0.0


def test_an_arm_that_does_not_reproduce_reports_its_movement():
    a = artifact("x", BASE, ["naive"], {"naive": reps([1.0], [0.9])})
    b = artifact("y", BASE, ["naive"], {"naive": reps([1.0], [0.5])})
    got = arm_matches([a, b], "naive")
    assert got["exact"] is False
    assert got["movement_forgetting"] == 0.0        # this toy's forgetting is the same in both


def test_a_method_one_member_lacks_is_absent_not_unequal():
    """`--methods naive,replay` against a five-arm run: replay is comparable, the block arms are not there."""
    full = artifact("x", BASE, ["naive", "ewc-block"],
                    {"naive": reps([1.0]), "ewc-block": reps([0.8])})
    pair = artifact("y", BASE, ["naive"], {"naive": reps([1.0])})
    assert arm_matches([full, pair], "ewc-block")["present"] is False
    assert arm_matches([full, pair], "naive")["present"] is True


# --- grouping --------------------------------------------------------------------------------------

def test_grouping_finds_the_repeated_configuration_and_its_differing_arms():
    na = {"naive": reps([1.0], [0.9]), "replay": reps([0.9], [0.8])}
    nb = {"naive": reps([1.0], [0.9]), "replay": reps([0.5], [0.8])}
    arts = [artifact("x1", BASE, list(na), na), artifact("x2", BASE, list(nb), nb)]
    groups = group_repeats(arts, min_runs=2)
    assert len(groups) == 1
    assert groups[0]["arms_identical"] == ["naive"]
    assert groups[0]["arms_differing"] == ["replay"]


def test_a_single_run_is_not_a_repeated_configuration():
    assert group_repeats([artifact("x", BASE, ["naive"], {"naive": reps([1.0])})], min_runs=2) == []


def test_an_artifact_without_arms_is_not_grouped():
    """An aggregate JSON has a `config` and nothing to compare; grouping it would report phantom arms."""
    assert group_repeats([artifact("x", BASE), artifact("y", BASE)], min_runs=2) == []


# --- the epoch check -------------------------------------------------------------------------------

def test_maximal_keyset_picks_the_superset():
    assert maximal_keyset([{"a": 1}, {"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}]) == {"a", "b", "c"}


def test_family_reads_the_runner_from_the_filename():
    assert family("e8_hardened_basis.json") == "e8"
    assert family("e101_rate_fb128.json") == "e101"
    assert family("e92_grid_cs300_flat_k2.json") == "e92"


def test_an_artifact_missing_a_younger_flag_is_reported():
    old = dict(BASE, json_out="runs/old.json")
    old.pop("fisher_batches")
    young = dict(BASE, json_out="runs/y.json")
    third = dict(BASE, json_out="runs/z.json")
    arts = [artifact("e8_old.json", old, ["naive"], {"naive": reps([1.0])}),
            artifact("e8_y.json", young, ["naive"], {"naive": reps([1.0])}),
            artifact("e8_z.json", third, ["naive"], {"naive": reps([1.0])})]
    got = epoch_flags(arts)
    assert [r["name"] for r in got] == ["e8_old.json"]
    assert got[0]["missing"] == ["fisher_batches"]
    assert got[0]["family"] == "e8"


def test_the_epoch_check_stays_off_aggregate_artifacts():
    """A hand-built summary config has no `methods`, so it is not a parser dump and cannot be dated."""
    old = {"report_only": True, "json_out": "runs/agg.json"}
    young = dict(BASE, json_out="runs/y.json")
    arts = [artifact("e8_agg.json", old), artifact("e8_y.json", young, ["naive"], {"naive": reps([1.0])}),
            artifact("e8_z.json", young, ["naive"], {"naive": reps([1.0])})]
    assert epoch_flags(arts) == []


def test_a_family_below_the_minimum_is_skipped():
    old = dict(BASE, json_out="runs/old.json")
    old.pop("fisher_batches")
    arts = [artifact("e8_old.json", old, ["naive"], {"naive": reps([1.0])}),
            artifact("e8_new.json", BASE, ["naive"], {"naive": reps([1.0])})]
    assert epoch_flags(arts, min_family=3) == []
    assert [r["name"] for r in epoch_flags(arts, min_family=2)] == ["e8_old.json"]


# --- loading ---------------------------------------------------------------------------------------

def test_loading_skips_unparseable_files_and_ones_without_a_config(tmp_path):
    (tmp_path / "good.json").write_text(json.dumps({"config": {"a": 1}}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    (tmp_path / "noconfig.json").write_text(json.dumps({"value": 1}), encoding="utf-8")
    (tmp_path / "skipped.json").write_text(json.dumps({"config": {"a": 1}}), encoding="utf-8")
    got = load_artifacts(tmp_path, skip=("skipped.json",))
    assert [a["name"] for a in got] == ["good.json"]


# --- the environment split --------------------------------------------------------------------------

def with_env(a, env):
    """Attach a recorded environment block, as every runner artifact will carry from e102 onwards."""
    a["payload"]["environment"] = env
    return a


def test_two_environments_are_split_out_of_one_group():
    """The difference between "5 of 5 arms do not reproduce" and the answerable question.

    Pooling two environments makes every arm look irreproducible. Within one, `naive` may be bit-identical --
    which is the measurement a reader needs, and which the pooled verdict hides.
    """
    one = {"omp_num_threads": "unset", "torch_num_threads": 20}
    four = {"omp_num_threads": "4", "torch_num_threads": 4}
    reps_a = {"naive": reps([1.0], [0.9])}
    reps_b = {"naive": reps([1.0], [0.5])}
    arts = [with_env(artifact("x1", BASE, ["naive"], reps_a), one),
            with_env(artifact("x2", BASE, ["naive"], reps_a), one),
            with_env(artifact("x3", BASE, ["naive"], reps_b), four)]
    groups = group_repeats(arts, min_runs=2)
    assert len(groups) == 1
    g = groups[0]
    assert g["arms"]["naive"]["exact"] is False           # pooled, as it must be
    assert len(g["environments"]) == 2
    by_runs = {s["runs"]: s for s in g["subgroups"]}
    assert by_runs[2]["arms_identical"] == ["naive"]      # within the shared environment
    assert by_runs[2]["arms_differing"] == []
    assert by_runs[1]["arms"] == {}                       # one run is not comparable


def test_artifacts_written_before_the_environment_field_are_unrecorded_not_shared():
    """`environment` is absent from every artifact written before e102.

    A missing key must not group those runs with each other *as if* they had agreed on an environment, and it
    must not invent a subgroup either -- there is one environment key, "unrecorded", and no split.
    """
    reps_a = {"naive": reps([1.0], [0.9])}
    arts = [artifact("x1", BASE, ["naive"], reps_a), artifact("x2", BASE, ["naive"], reps_a)]
    g = group_repeats(arts, min_runs=2)[0]
    assert list(g["environments"]) == ["unrecorded"]
    assert g["subgroups"] == []
    assert g["arms"]["naive"]["exact"] is True


def test_adding_instrumentation_to_the_runner_does_not_make_an_arm_unreproducible():
    """The bug that this field list exists for, found by running the audit on the corpus.

    `e107`, `e108` and `e109` put `theta_drift`, `interference` and `second_order` into the replicate records.
    Comparing the whole replicate dict then reports "do not reproduce" for seven runs whose forgetting is
    identical to six decimals -- a verdict about the schema rather than about the measurement, which is the
    failure this module exists to catch one level up.
    """
    a = {"naive": [{"learned": [1.0], "mean_forgetting": 0.033333, "retention": [[1.0]],
                    "final_accuracy": 0.9, "forgetting_per_task": [0.0], "final_per_task": [0.9],
                    "losses": [0.1]}]}
    b = {"naive": [{"learned": [1.0], "mean_forgetting": 0.033333, "retention": [[1.0]],
                    "final_accuracy": 0.9, "forgetting_per_task": [0.0], "final_per_task": [0.9],
                    "losses": [0.1], "theta_drift": [0.0195], "interference": [{"task": 0}]}]}
    got = arm_matches([artifact("x", BASE, ["naive"], a), artifact("y", BASE, ["naive"], b)], "naive")
    assert got["exact"] is True
    assert got["instrumentation_beyond_the_arm"] == ["interference", "theta_drift"]


def test_the_comparison_still_sees_a_real_difference_in_an_arm_field():
    a = {"naive": [{"learned": [1.0], "mean_forgetting": 0.033333, "retention": [[1.0]],
                    "final_accuracy": 0.9, "forgetting_per_task": [0.0], "final_per_task": [0.9],
                    "losses": [0.1]}]}
    b = {"naive": [{"learned": [1.0], "mean_forgetting": 0.033333, "retention": [[0.875]],
                    "final_accuracy": 0.9, "forgetting_per_task": [0.0], "final_per_task": [0.9],
                    "losses": [0.1]}]}
    got = arm_matches([artifact("x", BASE, ["naive"], a), artifact("y", BASE, ["naive"], b)], "naive")
    assert got["exact"] is False
