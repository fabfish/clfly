"""`e474` reads the held-out task across four draws, so the tests pin both faces of the four claims, the two spreads the
fourth is about, and the refusal when a roll is absent.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from experiments import e474_the_held_out_level_across_four_draws as e474

DRAWS = e474.DRAWS
SIDES = e474.SIDES
#: the shape: the level moves ~0.128 across draws while the change moves ~0.003, and every change resolves
LEVELS = {"3": 0.7594, "7": 0.6312, "11": 0.7000, "19": 0.6800}
CHANGES = {"3": 0.0719, "7": 0.0688, "11": 0.0700, "19": 0.0705}
INITIAL = 0.6875
PAIR_SIGMA = -0.30


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same_differ=None, seeds=None, identical=None, change_sigma=None, pair_sigma=PAIR_SIGMA, levels=None,
         thin=False, short=False, ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "curve": {}, "levels": {},
                "pairs": {}, "spans": {}}
    lv = dict(levels or LEVELS)
    curve = {}
    for d in DRAWS:
        curve[d] = {}
        for side in SIDES:
            anchor = e474.ANCHOR_OF[side]
            arms = {}
            for arm in (e474.BASELINE, anchor, e474.BUFFER):
                arms[arm] = {"initial": INITIAL, "trained": lv[d],
                             "change": _paired(CHANGES[d] if arm == e474.BASELINE else 0.0500,
                                              (CHANGES[d] * 70 if change_sigma is None else change_sigma)
                                              if arm == e474.BASELINE else 3.0),
                             "against_baseline": _paired(0.0 if arm == e474.BASELINE else -0.02,
                                                         0.0 if arm == e474.BASELINE else -1.0)}
            curve[d][side] = {"draw": e474.SEEDS[d], "side": side, "anchor": anchor, "initial": INITIAL,
                              "trained": lv[d],
                              "change": _paired(CHANGES[d], CHANGES[d] * 70 if change_sigma is None else change_sigma),
                              "arms": arms}
    same = {f"{side}.{k}": True for side in SIDES for k in ("circuit_size", "readout_size", "iters", "repeats")}
    same.update({f"{side}.circuit": True for side in SIDES})
    same.update({f"{side}.tasks": True for side in SIDES})
    if same_differ:
        same[same_differ] = False
    ident = {f"{side}:{arm}": {"equal": True, "n": 20, "agrees": 3}
             for side in SIDES for arm in (e474.BASELINE, e474.ANCHOR_OF[side], e474.BUFFER)}
    if identical:
        ident[identical] = {"equal": False, "n": 20, "agrees": 2}
    pairs = {side: {f"{x}-{y}": {"level": _paired(lv[y] - lv[x], 0.6),
                                 "change": _paired(CHANGES[y] - CHANGES[x], pair_sigma)}
                    for x, y in itertools.combinations(DRAWS, 2)} for side in SIDES}
    seed_map = {d: e474.SEEDS[d] for d in DRAWS}
    if seeds == "same":
        seed_map = {d: 5 for d in DRAWS}
    reps = 19 if thin else 20
    levels_out = {side: {"trained": dict(lv), "change": dict(CHANGES),
                         "level_spread": max(lv.values()) - min(lv.values()),
                         "change_spread": max(CHANGES.values()) - min(CHANGES.values()),
                         "level_sd": 0.05 * (max(lv.values()) - min(lv.values())),
                         "change_sd": 0.05 * (max(CHANGES.values()) - min(CHANGES.values()))} for side in SIDES}
    return {"ok": True, "reason": None, "runs": {}, "same": same, "identical": ident, "curve": curve,
            "levels": levels_out, "pairs": pairs,
            "spans": {"draws": list(DRAWS), "seeds": seed_map, "sides": list(SIDES), "runs": 8,
                      "same_fields": len(same),
                      "counts": [("loop_holdout", (96,), (48,))], "thin": {"x": reps} if thin else {},
                      "identical": len(ident),
                      "identical_equal": sum(1 for v in ident.values() if v["equal"]),
                      "replicates": [reps], "short": {"x": ["naive"]} if short else {}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e474.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: four draws of the held-out task, every change resolved and agreeing, and the level moving far more
    j = _judge()
    for cid in ("AA1", "AA2", "AA3", "AA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AA1: another field differing, seeds that are not the four, a trained arm that is not bit-identical, thin and short
    assert _judge(same_differ="bio.circuit_size")["AA1"].startswith("FALSIFIER")
    assert _judge(seeds="same")["AA1"].startswith("FALSIFIER")
    assert _judge(identical="bio:naive")["AA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["AA1"].startswith("FALSIFIER")
    assert _judge(short=True)["AA1"].startswith("FALSIFIER")

    # AA2: a draw whose change does not resolve -- the fake's sigma is the change times seventy, so a level that
    # makes one change tiny makes that change unresolvable, which is the cleanest way to fire this
    assert _judge(change_sigma=1.20)["AA2"].startswith("FALSIFIER")

    # AA3: a pair of draws whose changes differ by enough to resolve, in either direction
    assert _judge(pair_sigma=-2.40)["AA3"].startswith("FALSIFIER")
    assert _judge(pair_sigma=2.40)["AA3"].startswith("FALSIFIER")
    assert _judge(pair_sigma=-1.90)["AA3"].startswith("MET")

    # AA4: a level that does not move between the draws at all
    flat = {d: 0.7000 for d in DRAWS}
    assert _judge(levels=flat)["AA4"].startswith("FALSIFIER")

    #: a roll that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e474.judge(_doc(ok=False)))


def test_the_runs_the_draws_and_the_bounds_are_registered():
    assert e474.RUNS["11/bio"].name == "e474_earned_label_neurons_holdout_iters100_seed11_20reps.json"
    assert e474.RUNS["19/bio"].name == "e474_earned_label_neurons_holdout_iters100_seed19_20reps.json"
    assert e474.RUNS["11/rand"].name == "e474_earned_label_rand_neurons_holdout_iters100_seed11_20reps.json"
    assert e474.RUNS["19/rand"].name == "e474_earned_label_rand_neurons_holdout_iters100_seed19_20reps.json"
    assert e474.RUNS["3/bio"].name == "e471_earned_label_neurons_holdout_iters100_20reps.json"
    assert e474.RUNS["7/bio"].name == "e473_earned_label_neurons_holdout_iters100_seed7_20reps.json"
    assert e474.DRAWS == ("3", "7", "11", "19"), e474.DRAWS
    assert e474.SEEDS == {"3": 3, "7": 7, "11": 11, "19": 19}, e474.SEEDS
    assert e474.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e474.ANCHOR_OF
    assert (e474.BASELINE, e474.BUFFER, e474.SIGMA) == ("naive", "replay", 2.0)
    assert set(e474.IGNORED) == {"loop_holdout_seed", "json_out", "save_theta"}, e474.IGNORED


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e474_the_held_out_level_across_four_draws.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e474.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: eight rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["curve"]) == sorted(DRAWS), sorted(d["curve"])
    for draw, sides in d["curve"].items():
        assert sorted(sides) == sorted(SIDES), (draw, sorted(sides))
        for side, cell in sides.items():
            assert cell["draw"] == e474.SEEDS[draw] and cell["side"] == side, (draw, side)
            assert set(cell["arms"]) == {e474.BASELINE, e474.ANCHOR_OF[side], e474.BUFFER}, (draw, side)
            for arm, got in cell["arms"].items():
                assert 0.0 <= got["initial"] <= 1.0 and 0.0 <= got["trained"] <= 1.0, (draw, side, arm)
    assert sorted(d["levels"]) == sorted(SIDES), sorted(d["levels"])
    for side, got in d["levels"].items():
        assert len(got["trained"]) == len(DRAWS) and len(got["change"]) == len(DRAWS), (side, got)
        assert got["level_spread"] > 0.0, (side, got)
    assert sorted(d["pairs"]) == sorted(SIDES), sorted(d["pairs"])
    assert len(d["pairs"][SIDES[0]]) == 6, sorted(d["pairs"][SIDES[0]])
    assert sorted(set(d["spans"]["seeds"].values())) == [3, 7, 11, 19], d["spans"]["seeds"]
    assert d["spans"]["identical_equal"] == d["spans"]["identical"], d["spans"]
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
