"""`e188` reads the overlap axis, and every admission rule in it is a claim about the runner's code path.

A pair of payloads is evidence about `input_overlap` only if nothing else that the compared arm reads has changed,
and which fields those are is different for `naive` (nothing but the tasks) and for `ewc-block` (the penalty's
`lam`, the partition's `pool_buckets` and the matched draw's `partition_seed`). So the rules are declared per
method, the declarations are checked against each pair's actual `config` diff, and **one entry in `PAIRS` is meant
to be refused** -- the overlap-1 arm at `lambda = 1.0`, where `lam` is not inert for a penalised method. The exit
code counts declarations the corpus contradicts, so that entry is a test of the admission rules rather than noise
in a reject list.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e188_overlap_contrast as e188


def artifact(path: Path, method: str, forgetting: list[float], config: dict) -> Path:
    """A minimal payload with one method's per-replicate forgetting, in the shape `e151.load_arm` reads."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "config": config,
        "methods": {method: {"replicates": [{"mean_forgetting": f, "forgetting_per_task": [f, f, f],
                                            "final_per_task": [0.9, 0.9, 0.9]} for f in forgetting]}},
    }), encoding="utf-8")
    return path


BASE = {"input_overlap": 0.0, "repeats": 3, "lam": 0.003, "pool_buckets": 1, "partition_seed": None,
        "fisher_batches": 8, "methods": "naive"}
OVER = dict(BASE, input_overlap=1.0)


def pair(tmp_path: Path, method="naive", arm="naive", lo=None, hi=None, lo_cfg=None, hi_cfg=None):
    """`method` is what the pair DECLARES; `arm` is the key actually written into the payloads, so the two can be
    made to disagree (an absent arm)."""
    a = artifact(tmp_path / "runs" / "lo.json", arm, lo or [0.10, 0.10, 0.10], lo_cfg or dict(BASE))
    b = artifact(tmp_path / "runs" / "hi.json", arm, hi or [0.15, 0.15, 0.15], hi_cfg or dict(OVER))
    return tmp_path / "runs", [("the pair", method, "lo.json", "hi.json", "pair")]


def test_an_exact_pair_is_admitted_and_the_contrast_is_overlap_one_minus_zero(tmp_path):
    runs, pairs = pair(tmp_path)
    res = e188.audit(runs, pairs)
    assert res["n_comparisons"] == 1 and res["n_mismatches"] == 0
    r = res["comparisons"][0]
    assert abs(r["change"] - 0.05) < 1e-9
    assert abs(r["level_overlap0"] - 0.10) < 1e-9 and abs(r["level_overlap1"] - 0.15) < 1e-9
    assert r["differs_in"] == []


def test_a_field_the_compared_arm_reads_refuses_the_pair(tmp_path):
    """`lam` is inert for `naive` and NOT inert for `ewc-block`, which is the one refusal in the live table."""
    runs, pairs = pair(tmp_path, method="naive", hi_cfg=dict(OVER, lam=1.0))
    assert e188.audit(runs, pairs)["n_comparisons"] == 1
    runs, pairs = pair(tmp_path / "b", method="ewc-block", hi_cfg=dict(OVER, lam=1.0))
    res = e188.audit(runs, pairs)
    assert res["n_comparisons"] == 0
    assert "lam" in res["rejected"][0]["why"]


def test_none_and_false_are_the_same_state_of_the_bias_flag(tmp_path):
    runs, pairs = pair(tmp_path, lo_cfg=dict(BASE, frozen_bias=None), hi_cfg=dict(OVER, frozen_bias=False))
    res = e188.audit(runs, pairs)
    assert res["n_comparisons"] == 1 and res["comparisons"][0]["differs_in"] == []


def test_a_declaration_the_corpus_contradicts_is_the_exit_code(tmp_path):
    runs, pairs = pair(tmp_path)
    pairs = [(lab, m, a, b, "rejected: lam is read by the penalised arm") for lab, m, a, b, _ in pairs]
    res = e188.audit(runs, pairs)
    assert res["n_comparisons"] == 1 and res["n_mismatches"] == 1
    assert e188.report(res) == 1


def test_different_replicate_counts_and_missing_arms_are_refused(tmp_path):
    runs, pairs = pair(tmp_path, hi=[0.15, 0.15])
    assert e188.audit(runs, pairs)["n_comparisons"] == 0
    assert "replicate counts differ" in e188.audit(runs, pairs)["rejected"][0]["why"]
    runs2, pairs2 = pair(tmp_path / "b", method="replay", arm="naive")   # the payload has only a `naive` arm
    res2 = e188.audit(runs2, pairs2)
    assert res2["n_comparisons"] == 0 and "arm is absent" in res2["rejected"][0]["why"]


def test_the_live_table_is_nine_comparisons_one_unanimous_direction_and_one_declared_refusal():
    """The gate, and the result: every admitted comparison moves the same way, so the direction is not a
    coincidence of which pairs were admitted."""
    res = e188.audit(Path("runs"))
    assert res["n_mismatches"] == 0, res["mismatches"]
    assert res["n_comparisons"] >= 8
    assert res["n_negative"] == 0, "raising the input overlap has raised forgetting in every comparison so far"
    assert res["n_resolved"] >= 6
    assert len(res["rejected"]) == 1 and "lam" in res["rejected"][0]["why"]
