"""`e473` reads the held-out task at a second draw, so the tests pin both faces of the four claims, the bit-identity of
the sequence between the draws, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e473_the_held_out_task_at_a_second_draw as e473

DRAWS = e473.DRAWS
SIDES = e473.SIDES
SEEDS = {"draw3": 3, "draw7": 7}
#: the shape: the flag moves the held-out draw only, the sequence's arms are one draw's, and the two readings agree
CHANGE = {"draw3": (0.0719, 4.89), "draw7": (0.0690, 4.50)}
INITIAL = 0.6875
TRAINED = {"draw3": 0.7594, "draw7": 0.7579}
VERSUS = {"draw3": (-0.0396, -1.76), "draw7": (-0.0300, -1.40)}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same_differ=None, seeds=None, identical=False, draw_sigma=-0.30, change_sigma=None, thin=False, short=False,
         ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "curve": {}, "draws": {},
                "spans": {}}
    curve = {}
    for d in DRAWS:
        curve[d] = {}
        for side in SIDES:
            anchor = e473.ANCHOR_OF[side]
            arms = {}
            for arm in (e473.BASELINE, anchor, e473.BUFFER):
                change = CHANGE[d] if arm == e473.BASELINE else (0.0450 if d == "draw3" else 0.0430, 3.00)
                sigma = change_sigma if (change_sigma is not None and arm == e473.BASELINE) else change[1]
                arms[arm] = {"initial": INITIAL, "trained": TRAINED[d],
                             "change": _paired(change[0], sigma),
                             "against_baseline": _paired(0.0 if arm == e473.BASELINE else VERSUS[d][0],
                                                         0.0 if arm == e473.BASELINE else VERSUS[d][1])}
            curve[d][side] = {"draw": DRAWS[d], "side": side, "anchor": anchor, "initial": INITIAL,
                              "trained": TRAINED[d],
                              "change": _paired(CHANGE[d][0],
                                                CHANGE[d][1] if change_sigma is None else change_sigma),
                              "arms": arms}
    same = {f"{side}.{k}": True for side in SIDES for k in ("circuit_size", "readout_size", "iters", "repeats")}
    same.update({f"{side}.circuit": True for side in SIDES})
    same.update({f"{side}.tasks": True for side in SIDES})
    if same_differ:
        same[same_differ] = False
    ident = {f"{side}:{arm}": {"equal": True, "n": 20, "first_differing": None, "fields": []}
             for side in SIDES for arm in (e473.BASELINE, e473.ANCHOR_OF[side], e473.BUFFER)}
    if identical:
        ident[identical] = {"equal": False, "n": 20, "first_differing": 3, "fields": ["final_per_task"]}
    seed_map = {f"{d}/{side}": SEEDS[d] for d in DRAWS for side in SIDES}
    if seeds == "same":
        seed_map = {k: 3 for k in seed_map}
    reps = 19 if thin else 20
    return {"ok": True, "reason": None,
            "runs": {}, "same": same, "identical": ident, "curve": curve,
            "draws": {side: {"initial": _paired(0.0, 0.40), "trained": _paired(TRAINED["draw7"] - TRAINED["draw3"], 0.60),
                             "change": _paired(draw_sigma * 0.01, draw_sigma)} for side in SIDES},
            "spans": {"draws": list(DRAWS), "sides": list(SIDES), "runs": 4, "same_fields": len(same),
                      "seeds": seed_map,
                      "identical": len(ident), "identical_equal": sum(1 for v in ident.values() if v["equal"]),
                      "counts": [("loop_holdout", (96,), (48,))], "thin": {"x": reps} if thin else {},
                      "replicates": [reps],
                      "tasks": {f"{d}/{side}": ["loop_holdout"] for d in DRAWS for side in SIDES},
                      "short": {"x": ["naive"]} if short else {}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e473.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: a redraw of the held-out task alone, both draws resolved, and the two draws agreeing
    j = _judge()
    for cid in ("ZA1", "ZA2", "ZA3", "ZA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # ZA1: another field differing, seeds that are the same, a trained arm that is not bit-identical, thin and short
    assert _judge(same_differ="bio.circuit_size")["ZA1"].startswith("FALSIFIER")
    assert _judge(seeds="same")["ZA1"].startswith("FALSIFIER")
    assert _judge(identical="bio:ewc-block")["ZA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["ZA1"].startswith("FALSIFIER")
    assert _judge(short=True)["ZA1"].startswith("FALSIFIER")

    # ZA2: a draw whose change does not resolve
    assert _judge(change_sigma=1.20)["ZA2"].startswith("FALSIFIER")

    # ZA3: a difference between the draws that resolves, in either direction
    assert _judge(draw_sigma=-2.40)["ZA3"].startswith("FALSIFIER")
    assert _judge(draw_sigma=2.40)["ZA3"].startswith("FALSIFIER")
    assert _judge(draw_sigma=-1.90)["ZA3"].startswith("MET")

    # ZA4: an anchor that resolves against its own baseline at either draw
    #: the fake puts the same `VERSUS` on both draws, so this exercises the check on both
    assert _judge()["ZA4"].startswith("MET")

    #: a roll that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e473.judge(_doc(ok=False)))


def test_the_runs_the_draws_and_the_bounds_are_registered():
    assert e473.RUNS["draw7/bio"].name == "e473_earned_label_neurons_holdout_iters100_seed7_20reps.json"
    assert e473.RUNS["draw7/rand"].name == "e473_earned_label_rand_neurons_holdout_iters100_seed7_20reps.json"
    assert e473.RUNS["draw3/bio"].name == "e471_earned_label_neurons_holdout_iters100_20reps.json"
    assert e473.RUNS["draw3/rand"].name == "e471_earned_label_rand_neurons_holdout_iters100_20reps.json"
    assert e473.DRAWS == {"draw3": 3, "draw7": 7}, e473.DRAWS
    assert e473.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e473.ANCHOR_OF
    assert (e473.BASELINE, e473.BUFFER, e473.SIGMA) == ("naive", "replay", 2.0)
    #: the held-out seed is the manipulation, so it is the one config field the two draws are allowed to move
    assert set(e473.IGNORED) == {"loop_holdout_seed", "json_out", "save_theta"}, e473.IGNORED
    assert set(e473.TRAINED_ARMS) >= {e473.BASELINE, e473.BUFFER}, e473.TRAINED_ARMS


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e473_the_held_out_task_at_a_second_draw.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e473.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: four rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["curve"]) == sorted(DRAWS), sorted(d["curve"])
    for draw, sides in d["curve"].items():
        assert sorted(sides) == sorted(SIDES), (draw, sorted(sides))
        for side, cell in sides.items():
            assert cell["draw"] == DRAWS[draw] and cell["side"] == side, (draw, side)
            assert set(cell["arms"]) == {e473.BASELINE, e473.ANCHOR_OF[side], e473.BUFFER}, (draw, side)
            for arm, got in cell["arms"].items():
                assert 0.0 <= got["initial"] <= 1.0 and 0.0 <= got["trained"] <= 1.0, (draw, side, arm)
    assert sorted(d["draws"]) == sorted(SIDES), sorted(d["draws"])
    assert sorted(set(d["spans"]["seeds"].values())) == [3, 7], d["spans"]["seeds"]
    assert d["spans"]["identical_equal"] == d["spans"]["identical"], d["spans"]
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
