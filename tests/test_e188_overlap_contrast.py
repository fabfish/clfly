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

import pytest

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


# --- the dose read ----------------------------------------------------------------------------------------------

def dose_payload(path: Path, method: str, forgetting: list[float], accuracy: list[float],
                 overlap: float) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "config": {"input_overlap": overlap, "lam": 0.003, "methods": method},
        "methods": {method: {"replicates": [{"mean_forgetting": f, "final_acc": a, "final_accuracy": a,
                                             "forgetting_per_task": [f, f, f],
                                             "final_per_task": [a, a, a]}
                                            for f, a in zip(forgetting, accuracy)]}},
    }), encoding="utf-8")
    return path


def test_the_dose_read_pairs_a_level_against_the_baseline_on_both_quantities(tmp_path):
    d = tmp_path / "runs"
    base = dose_payload(d / "base.json", "naive", [0.07, 0.08, 0.075, 0.075], [0.90, 0.86, 0.88, 0.88], 0.0)
    level = dose_payload(d / "half.json", "naive", [0.10, 0.11, 0.105, 0.105], [0.84, 0.80, 0.82, 0.82], 0.5)
    res = e188.dose_read([level], base)
    row = res["levels"][0]
    assert row["target_overlap"] == 0.5 and row["achieved_overlap"] == 0.3333
    assert row["arms"]["naive"]["forgetting"]["change"] == pytest.approx(0.03, abs=1e-9)
    assert row["arms"]["naive"]["accuracy"]["change"] == pytest.approx(-0.06, abs=1e-9)
    assert row["arms"]["naive"]["half_done"] is True, "0.03 > 0.0159"
    weak = dose_payload(d / "weak.json", "naive", [0.075, 0.085, 0.08, 0.08], [0.90, 0.86, 0.88, 0.88], 0.25)
    assert e188.dose_read([weak], base)["levels"][0]["arms"]["naive"]["half_done"] is False


def test_the_dose_read_refuses_a_level_that_is_not_written_yet(tmp_path):
    res = e188.dose_read([tmp_path / "nope.json"], tmp_path / "also-nope.json")
    assert e188.report_dose(res) == 1


def test_the_live_registration_names_three_levels_and_none_exists_yet():
    levels = [Path(f"runs/e193_r32_overlap{n}_methods_40reps.json") for n in (25, 50, 75)]
    res = e188.dose_read(levels)
    assert all(lv.get("status") == "not written yet" for lv in res["levels"])
    assert e188.ACHIEVED_OVERLAP[0.5] == 0.3333


def test_the_launched_dose_response_is_a_near_pair_with_its_baseline_on_inert_fields_only():
    """The pairing is certified BEFORE the artifacts exist, which is the point of declaring the inert fields.

    The three `e193` commands were launched with `--methods naive,ewc-block,ewc-block-rand` and one `--input-overlap`
    each, everything else copied from `e140` (the disjoint baseline the dose read pairs against). So the config diff
    must be exactly `{input_overlap, methods}` and both must be inert for the three compared arms -- if anyone edits
    the design (a different basis, a different read-out) the read would otherwise refuse the pair only after a
    multi-hour run.
    """
    base = json.loads(Path("runs/e140_r32_methods_plastic_40reps.json").read_text(encoding="utf-8"))["config"]
    launched = dict(base, methods="naive,ewc-block,ewc-block-rand", input_overlap=0.25)
    diff = e188.differing_fields(base, launched)
    # `input_overlap` is not in the diff by construction: it IS the manipulation, and `differing_fields` excludes it
    assert set(diff) == {"methods"}, diff
    for method in ("naive", "ewc-block", "ewc-block-rand"):
        assert set(diff) <= e188.INERT_FOR[method], (method, e188.INERT_FOR[method])
    # and the target the row registers is one of the levels whose ACHIEVED overlap is tabulated
    assert launched["input_overlap"] in e188.ACHIEVED_OVERLAP


def test_the_seed_price_reproduces_rule_42s_own_published_values():
    """Carried here as well as in `e191` because the two reads are imported in opposite directions, so the helper is
    duplicated rather than shared -- and a duplicated constant that stops matching the rule it came from is exactly
    what a test is for. Rule 42's published prices are 4 seeds at 9.35 sigma and 169 at 1.46 sigma."""
    assert e188.seeds_for_three_sigma(9.35) == pytest.approx(4, abs=0.5)
    assert e188.seeds_for_three_sigma(1.46) == pytest.approx(169, abs=1)
    assert e188.seeds_for_three_sigma(0.0) is None, "no sem, no price"
    assert e188.seeds_for_three_sigma(9.35) == pytest.approx(e191_price(9.35), rel=1e-12)


def e191_price(sigma: float) -> float:
    """The same identity, written out, so the duplication above is checked rather than asserted."""
    return 40 * (3 / sigma) ** 2


def test_the_progress_fraction_is_per_quantity_and_an_overshoot_uses_the_anchors_own_sem(tmp_path):
    """A fraction above 100% is a reading and not an error: the cost at an intermediate overlap can exceed its own
    0 -> 1 endpoint change. Its sem has to come from the level-against-anchor pairing, because the two deltas share
    the admitted baseline -- subtracting their sems in quadrature would overstate how well the overshoot is pinned."""
    d = tmp_path / "runs"
    base = dose_payload(d / "base.json", "naive", [0.07, 0.08, 0.075, 0.075], [0.90, 0.86, 0.88, 0.88], 0.0)
    level = dose_payload(d / "half.json", "naive", [0.10, 0.11, 0.105, 0.105], [0.84, 0.80, 0.82, 0.82], 0.5)
    anchor = dose_payload(d / "one.json", "naive", [0.09, 0.10, 0.095, 0.095], [0.88, 0.84, 0.86, 0.86], 1.0)
    arm = e188.dose_read([level], base, overlap1=anchor)["levels"][0]["arms"]["naive"]
    assert arm["full_change"]["forgetting"]["change"] == pytest.approx(0.02, abs=1e-9)
    assert arm["progress_fraction"]["forgetting"] == pytest.approx(1.5, abs=1e-9)
    assert arm["progress_fraction"]["accuracy"] == pytest.approx(3.0, abs=1e-9)
    assert arm["overshoot_vs_anchor"]["forgetting"]["change"] == pytest.approx(0.01, abs=1e-9)
    assert arm["overshoot_vs_anchor"]["accuracy"]["change"] == pytest.approx(-0.04, abs=1e-9)
    # an anchor that is not at overlap 1.0 is refused, with the reason, rather than divided by
    refused = e188.dose_read([level], base, overlap1=base)["levels"][0]["arms"]["naive"]
    assert "progress_fraction" not in refused
    assert "not a 0 -> 1 change" in refused["progress_refused"], refused["progress_refused"]


def test_the_live_level_050_accuracy_cost_overshoots_its_own_endpoint_change():
    """The shape the interference account could not show: on the account `e188` reads, the registered midpoint's
    accuracy cost is 1.77x its own 0 -> 1 endpoint change while its forgetting is at 26% of one -- and the overshoot
    is 1.56 sigma against `e144`, where quadrature would have said 1.41."""
    arm = e188.dose_read([Path("runs/e193_r32_overlap050_methods_40reps.json")])["levels"][0]["arms"]["naive"]
    assert arm["progress_fraction"]["accuracy"] == pytest.approx(1.77, abs=0.02), arm["progress_fraction"]
    assert arm["progress_fraction"]["forgetting"] == pytest.approx(0.26, abs=0.02), arm["progress_fraction"]
    o = arm["overshoot_vs_anchor"]["accuracy"]
    assert o["change"] == pytest.approx(-0.01424, abs=1e-4)
    assert abs(o["change"]) / o["sem"] == pytest.approx(1.56, abs=0.05), "the anchor pairing's own sem"
