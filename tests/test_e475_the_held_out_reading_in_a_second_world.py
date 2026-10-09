"""`e475` reads the held-out task in a second world, so the tests pin both faces of the four claims, the world axis and
the draw axis, and the refusal when a roll is absent.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from experiments import e475_the_held_out_reading_in_a_second_world as e475

DRAWS = e475.DRAWS
SIDES = e475.SIDES
WORLDS = ("w0", "w1")


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same_differ=None, cross_differ=None, seeds="ok", identical=None, change_sigma=5.0, world_sigma=-0.30,
         pair_sigma=-0.30, worlds_ok=True, thin=False, short=False, ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "cross": {}, "identical": {}, "curve": {},
                "levels": {}, "pairs": {}, "worlds": {}, "spans": {}}
    curve = {}
    for world in WORLDS:
        curve[world] = {}
        for d in DRAWS:
            curve[world][d] = {}
            for side in SIDES:
                curve[world][d][side] = {"draw": e475.SEEDS[d], "side": side, "world": world,
                                         "loop_seed": None if world == "w0" else 1,
                                         "anchor": e475.ANCHOR_OF[side], "initial": 0.6875, "trained": 0.7500,
                                         "change": _paired(0.0700, change_sigma if world == "w1" else 5.0),
                                         "arms": {}}
    same = {f"{side}.{k}": True for side in SIDES for k in ("circuit_size", "readout_size", "iters", "repeats")}
    same.update({f"{side}.circuit": True for side in SIDES})
    same.update({f"{side}.tasks": True for side in SIDES})
    if same_differ:
        same[same_differ] = False
    cross = {f"{d}/{side}.{k}": True for d in DRAWS for side in SIDES
             for k in ("circuit_size", "readout_size", "iters", "repeats")}
    cross.update({f"{d}/{side}.circuit": True for d in DRAWS for side in SIDES})
    cross.update({f"{d}/{side}.tasks": True for d in DRAWS for side in SIDES})
    if cross_differ:
        cross[cross_differ] = False
    ident = {f"{side}:{arm}": {"equal": True, "n": 20, "agrees": 3}
             for side in SIDES for arm in (e475.BASELINE, e475.ANCHOR_OF[side], e475.BUFFER)}
    if identical:
        ident[identical] = {"equal": False, "n": 20, "agrees": 2}
    pairs = {f"world/{d}": {side: {"level": _paired(-0.02, -1.0), "initial": _paired(0.0, 0.0),
                                   "change": _paired(0.010, world_sigma)} for side in SIDES} for d in DRAWS}
    pairs["draw/w1"] = {side: {f"{x}-{y}": {"level": _paired(0.02, 0.6),
                                            "change": _paired(0.010, pair_sigma)}
                               for x, y in itertools.combinations(DRAWS, 2)} for side in SIDES}
    seed_map = {d: e475.SEEDS[d] for d in DRAWS}
    if seeds == "same":
        seed_map = {d: 5 for d in DRAWS}
    reps = 19 if thin else 20
    levels = {f"{world}/{side}": {"trained": {d: 0.7500 for d in DRAWS},
                                  "change": {d: 0.0700 for d in DRAWS},
                                  "level_spread": 0.02, "change_spread": 0.01}
              for world in WORLDS for side in SIDES}
    world_seeds = {"w0": [None], "w1": [1]} if worlds_ok else {"w0": [0], "w1": [1]}
    return {"ok": True, "reason": None, "runs": {}, "same": same, "cross": cross, "identical": ident, "curve": curve,
            "levels": levels, "pairs": pairs, "worlds": {"identical_across": {}},
            "spans": {"worlds": list(WORLDS), "draws": list(DRAWS), "seeds": seed_map, "sides": list(SIDES),
                      "runs": 16, "same_fields": len(same), "cross_fields": len(cross),
                      "counts": [("loop_holdout", (96,), (48,))], "thin": {"x": reps} if thin else {},
                      "identical": len(ident),
                      "identical_equal": sum(1 for v in ident.values() if v["equal"]),
                      "across_worlds": 6, "across_worlds_equal": 0,
                      "world_seeds": world_seeds, "held_out_seeds": sorted(set(seed_map.values())),
                      "replicates": [reps], "short": {"x": ["naive"]} if short else {}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e475.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: sixteen rolls over two worlds, every change resolved, the worlds agreeing and the draws too
    j = _judge()
    for cid in ("BA1", "BA2", "BA3", "BA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BA1: another field differing within a world, across the worlds, seeds that are not the four, a trained arm that
    # is not bit-identical inside world 1, the world's own seed not 1 against null, thin and short
    assert _judge(same_differ="bio.circuit_size")["BA1"].startswith("FALSIFIER")
    assert _judge(cross_differ="11/rand.iters")["BA1"].startswith("FALSIFIER")
    assert _judge(seeds="same")["BA1"].startswith("FALSIFIER")
    assert _judge(identical="bio:naive")["BA1"].startswith("FALSIFIER")
    assert _judge(worlds_ok=False)["BA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["BA1"].startswith("FALSIFIER")
    assert _judge(short=True)["BA1"].startswith("FALSIFIER")

    # BA2: a draw in the second world whose change does not resolve
    assert _judge(change_sigma=1.20)["BA2"].startswith("FALSIFIER")
    assert _judge(change_sigma=2.40)["BA2"].startswith("MET")

    # BA3: a matched held-out seed whose two worlds' changes differ by enough to resolve, in either direction
    assert _judge(world_sigma=-2.40)["BA3"].startswith("FALSIFIER")
    assert _judge(world_sigma=2.40)["BA3"].startswith("FALSIFIER")
    assert _judge(world_sigma=-1.90)["BA3"].startswith("MET")

    # BA4: a pair of draws inside the second world whose changes differ by enough to resolve
    assert _judge(pair_sigma=-2.40)["BA4"].startswith("FALSIFIER")
    assert _judge(pair_sigma=2.40)["BA4"].startswith("FALSIFIER")
    assert _judge(pair_sigma=-1.90)["BA4"].startswith("MET")

    #: a roll that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e475.judge(_doc(ok=False)))


def test_the_runs_the_worlds_and_the_bounds_are_registered():
    assert e475.WORLD0["11/bio"].name == "e474_earned_label_neurons_holdout_iters100_seed11_20reps.json"
    assert e475.WORLD0["3/bio"].name == "e471_earned_label_neurons_holdout_iters100_20reps.json"
    assert e475.WORLD0["7/rand"].name == "e473_earned_label_rand_neurons_holdout_iters100_seed7_20reps.json"
    assert e475.WORLD1["3/bio"].name == "e475_earned_label_bio_neurons_holdout_w1_iters100_seed3_20reps.json"
    assert e475.WORLD1["19/rand"].name == "e475_earned_label_rand_neurons_holdout_w1_iters100_seed19_20reps.json"
    assert sorted(e475.WORLDS) == ["w0", "w1"], sorted(e475.WORLDS)
    assert e475.DRAWS == ("3", "7", "11", "19"), e475.DRAWS
    assert e475.SEEDS == {"3": 3, "7": 7, "11": 11, "19": 19}, e475.SEEDS
    assert e475.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e475.ANCHOR_OF
    assert (e475.BASELINE, e475.BUFFER, e475.SIGMA) == ("naive", "replay", 2.0)
    assert set(e475.IGNORED) == {"loop_holdout_seed", "json_out", "save_theta"}, e475.IGNORED
    assert set(e475.IGNORED_ACROSS) == {"loop_holdout_seed", "json_out", "save_theta", "loop_seed"}, e475.IGNORED_ACROSS


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e475_the_held_out_reading_in_a_second_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e475.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: sixteen rolls over two worlds is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["curve"]) == sorted(WORLDS), sorted(d["curve"])
    for world, draws in d["curve"].items():
        assert sorted(draws) == sorted(DRAWS), (world, sorted(draws))
        for draw, sides in draws.items():
            assert sorted(sides) == sorted(SIDES), (world, draw, sorted(sides))
            for side, cell in sides.items():
                assert cell["draw"] == e475.SEEDS[draw] and cell["side"] == side, (world, draw, side)
                assert cell["world"] == world, (world, draw, side)
                assert set(cell["arms"]) == {e475.BASELINE, e475.ANCHOR_OF[side], e475.BUFFER}, (world, draw, side)
                for arm, got in cell["arms"].items():
                    assert 0.0 <= got["initial"] <= 1.0 and 0.0 <= got["trained"] <= 1.0, (world, draw, side, arm)
    assert sorted(d["levels"]) == sorted(f"{w}/{s}" for w in WORLDS for s in SIDES), sorted(d["levels"])
    for key, got in d["levels"].items():
        assert len(got["trained"]) == len(DRAWS) and len(got["change"]) == len(DRAWS), (key, got)
    assert sorted(k for k in d["pairs"] if k.startswith("world/")) == sorted(f"world/{d_}" for d_ in DRAWS)
    assert sorted(d["pairs"]["draw/w1"]) == sorted(SIDES), sorted(d["pairs"]["draw/w1"])
    assert len(d["pairs"]["draw/w1"][SIDES[0]]) == 6, sorted(d["pairs"]["draw/w1"][SIDES[0]])
    assert d["spans"]["world_seeds"] == {"w0": [None], "w1": [1]}, d["spans"]["world_seeds"]
    assert sorted(d["spans"]["held_out_seeds"]) == [3, 7, 11, 19], d["spans"]["held_out_seeds"]
    assert d["spans"]["identical_equal"] == d["spans"]["identical"], d["spans"]
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
