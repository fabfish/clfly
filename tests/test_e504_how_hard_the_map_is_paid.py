"""`e504` gives the map its own ascent rate and reads the earning curve at three points, so the tests pin the four
claims' both faces, the curve's own shape, and the refusal when a run is absent.

The falsifier test drives `judge` on synthetic readings rather than on the artifact, so a claim's outcome is never
asserted as the artifact's shape: what is pinned is that each registered falsifier does fire, and that the four claims
read both faces. A second test drives `reading` on synthetic artifacts on disk, so the pipeline that assembles the
curve is exercised as well.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e504_how_hard_the_map_is_paid as e504

ARMS = e504.ARMS
#: the reading's shape: the pass still learned, the payout moved, and the map earned
ACC = {"small": {"naive": 0.8500, "ewc-block": 0.8400, "replay": 0.8600},
       "mid": {"naive": 0.8510, "ewc-block": 0.8410, "replay": 0.8610},
       "large": {"naive": 0.8520, "ewc-block": 0.8420, "replay": 0.8620},
       "meter": {"naive": 0.8538, "ewc-block": 0.8392, "replay": 0.8580}}
REWARD_DIAG = {"small": {"naive": -5.9500, "ewc-block": -6.0500, "replay": -6.1500},
               "mid": {"naive": -6.0000, "ewc-block": -6.1000, "replay": -6.2000},
               "large": {"naive": -4.5000, "ewc-block": -4.6000, "replay": -4.7000},
               "meter": {"naive": -4.5457, "ewc-block": -4.5947, "replay": -5.0295}}
MOVE = {"small": {"naive": 4.0000, "ewc-block": 4.1000, "replay": 4.2000},
        "mid": {"naive": 5.0000, "ewc-block": 5.1000, "replay": 5.2000},
        "large": {"naive": 6.0000, "ewc-block": 6.1000, "replay": 6.2000}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _run(replicates=20):
    return {"artifact": "n", "arms": {a: {"replicates": replicates} for a in ARMS}}


def _against(rate, differ=None, draw_differ=None, added=None, missing=None):
    return {"same": 59, "inert": ["loop_earn_lr"], "differ": {k: [None, 1] for k in (differ or [])},
            "moved": {"loop_earn_lr": rate},
            "draw": {"agree": {"cue_sha1": True, "episode_len": True}, "differ": list(draw_differ or []),
                     "added": list(added or []), "missing": list(missing or [])}}


def _doc(differ=None, rate=None, draw_differ=None, added=None, missing=None, replicates=20,
         reward_small=None, reward_large=None, diag=None, meter_diag=None, travel=None, absent=False):
    reward_small = dict(reward_small or {"naive": (0.0000, 0.00), "ewc-block": (0.0000, 0.00),
                                         "replay": (0.0000, 0.00)})
    reward_large = dict(reward_large or {"naive": (+1.5000, +18.00), "ewc-block": (+1.5000, +16.00),
                                         "replay": (+1.5000, +12.00)})
    travel = dict(travel or {"naive": (+2.0000, +12.00), "ewc-block": (+2.0000, +10.00),
                             "replay": (+2.0000, +8.00)})
    diag = {k: dict(v) for k, v in (diag or ACC).items()}
    moved = {"small": (0.001 if rate is None else rate[0]), "large": (0.01 if rate is None else rate[1])}
    if absent:
        return {"ok": True, "reason": None, "runs": {"small": None, "mid": None, "large": None, "meter": None},
                "map": {}, "reward": {}, "accuracy": {}, "shape": {}, "travel": {}, "spans": {"readable": {}}}
    return {
        "ok": True, "reason": None,
        "runs": {"small": _run(replicates), "mid": _run(replicates), "large": _run(replicates),
                 "meter": _run(replicates)},
        "map": {k: {a: {"replicates": replicates, "above_zero": replicates, "smallest": MOVE[k][a],
                        "mean": MOVE[k][a]} for a in ARMS} for k in ("small", "mid", "large")},
        "reward": {k: {a: _paired(v[a][0], v[a][1]) for a in ARMS}
                   for k, v in (("small", reward_small), ("large", reward_large))},
        "accuracy": {k: {a: _paired(0.0, 0.0) for a in ARMS} for k in ("small", "mid", "large")},
        "shape": {k: {a: _paired(0.3, 5.0) for a in ARMS} for k in ("small", "mid", "large")},
        "travel": {a: _paired(travel[a][0], travel[a][1]) for a in ARMS},
        "spans": {
            "arms": list(ARMS), "rates": e504.RATES, "chance": e504.CHANCE, "bar": e504.BAR, "tol": e504.TOL,
            "floor": e504.FLOOR, "sigma": e504.SIGMA, "arms_needed": e504.ARMS_NEEDED,
            "readable": {k: True for k in ("small", "mid", "large", "meter")},
            "replicates": [replicates],
            "against": {"small": _against(moved["small"], differ, draw_differ, added, missing),
                        "large": _against(moved["large"], differ, draw_differ, added, missing)},
            "accuracy_diagonal": {k: dict(v) for k, v in diag.items()},
            "reward_diagonal": {k: dict(v) for k, v in REWARD_DIAG.items()},
            "reward_last": {k: {a: -5.0000 for a in ARMS} for k in ("small", "mid", "large")},
            "map_move": {k: {a: {"mean": MOVE[k][a], "smallest": MOVE[k][a],
                                 "above_zero": replicates, "replicates": replicates} for a in ARMS}
                         for k in ("small", "mid", "large")},
            "reward_gain": {k: {a: {"mean": 1.0, "sigma": 10.0} for a in ARMS} for k in ("small", "large")},
            "accuracy_change": {},
            "travel": {a: {"mean": travel[a][0], "sigma": travel[a][1]} for a in ARMS},
            "reward_shape": {},
        },
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e504.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    j = _judge()
    for cid in ("UA1", "UA2", "UA3", "UA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # UA1: another config field differing, a recorded rate that is not the one asked for, a draw field differing,
    # added or missing, and a thin run
    assert _judge(differ=["iters"])["UA1"].startswith("FALSIFIER")
    assert _judge(rate=(0.005, 0.01))["UA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["UA1"].startswith("FALSIFIER")
    assert _judge(added=["reward_map_sha1"])["UA1"].startswith("FALSIFIER")
    assert _judge(missing=["boundary_sha1"])["UA1"].startswith("FALSIFIER")
    assert _judge(replicates=19)["UA1"].startswith("FALSIFIER")

    # UA2: fewer than two arms up at the largest rate, and the smallest rate up on two or more arms
    thin_large = {"naive": (+1.5000, +18.00), "ewc-block": (+0.1000, +1.20), "replay": (-0.1000, -1.10)}
    assert _judge(reward_large=thin_large)["UA2"].startswith("FALSIFIER")
    loud_small = {"naive": (+0.8000, +6.00), "ewc-block": (+0.8000, +6.00), "replay": (-0.1000, -1.10)}
    assert _judge(reward_small=loud_small)["UA2"].startswith("FALSIFIER")

    # UA3: one arm in the band only, and an arm within 0.05 of the chance of 0.25
    thin_band = {"small": {"naive": 0.8500, "ewc-block": 0.3200, "replay": 0.3100},
                 "mid": {"naive": 0.8510, "ewc-block": 0.3200, "replay": 0.3100},
                 "large": {"naive": 0.8520, "ewc-block": 0.3200, "replay": 0.3100},
                 "meter": dict(ACC["meter"])}
    assert _judge(diag=thin_band)["UA3"].startswith("FALSIFIER")
    at_chance = {k: dict(v) for k, v in ACC.items()}
    at_chance["small"] = {"naive": 0.8500, "ewc-block": 0.8400, "replay": 0.2900}
    assert _judge(diag=at_chance)["UA3"].startswith("FALSIFIER")

    # UA4: fewer than two arms resolving upward
    thin_travel = {"naive": (+2.0000, +12.00), "ewc-block": (+0.1000, +1.20), "replay": (-0.1000, -1.10)}
    assert _judge(travel=thin_travel)["UA4"].startswith("FALSIFIER")

    #: a reading with no run at all refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e504.judge(_doc(absent=True)))


def test_the_runs_the_rates_the_bars_and_the_refusal_are_registered():
    assert e504.SMALL.name == "e504_earn_lr0.001_episode2_labelfirst_reward_earn_20reps.json"
    assert e504.LARGE.name == "e504_earn_lr0.01_episode2_labelfirst_reward_earn_20reps.json"
    assert e504.MID.name == "e500_earned_label_episode2_labelfirst_reward_earn_20reps.json"
    assert e504.METER.name == "e498_earned_label_episode2_labelfirst_reward_20reps.json"
    assert e504.RUNNER.name == "e8_rate_network.py"
    assert set(e504.MOVED) == {"loop_earn_lr"}, e504.MOVED
    assert set(e504.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e504.RATES == {"small": 0.001, "mid": 0.003, "large": 0.01}
    assert e504.CHANCE == 0.25
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e504.MIN_REPS, e504.SIGMA, e504.BAR, e504.TOL, e504.FLOOR, e504.ARMS_NEEDED) == (20, 2.0, 0.1, 0.1,
                                                                                              0.05, 2)
    assert e504._inert("loop_earn_lr", None, 0.01) and e504._inert("loop_earn_lr", 0.001, 0.01)
    assert not e504._inert("iters", 500, 100)
    #: the flag is a runner argument with None for its default, recorded in the run's config as `loop_earn_lr`
    assert "loop_earn_lr" in e504.DEFAULTS and e504.DEFAULTS["loop_earn_lr"] is None, e504.DEFAULTS.get("loop_earn_lr")
    #: the four claims are registered with their falsifiers beside them, before the reading was opened
    assert [c[0] for c in e504.CLAIMS] == ["UA1", "UA2", "UA3", "UA4"]
    assert all("falsifier:" in c[3] for c in e504.CLAIMS)


def _replicate(k, acc, reward, move):
    return {"learned": [acc] * 4, "final_per_task": [acc] * 3, "policy_move": move,
            "reward_retention": [[reward, 0.0, 0.0], [0.0, reward, 0.0], [0.0, 0.0, reward]]}


def _write(path: Path, cfg: dict, acc: float, reward: float, move: float, acc_slope=0.0, reward_slope=0.0,
           move_slope=0.0) -> None:
    doc = {"config": cfg, "env_draw": {"cue_sha1": "a", "episode_len": 2},
           "methods": {a: {"replicates": [_replicate(k, acc + acc_slope * k, reward + reward_slope * k,
                                                     move + move_slope * k) for k in range(20)]} for a in ARMS}}
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_the_reading_assembles_the_curve_from_artifacts(tmp_path):
    base = {"lr": 0.003, "iters": 500, "loop_earn": True}
    _write(tmp_path / "small.json", {**base, "loop_earn_lr": 0.001}, 0.8500, -6.000, 4.000, reward_slope=0.02)
    _write(tmp_path / "mid.json", base, 0.8510, -6.000, 5.000, reward_slope=0.02)
    _write(tmp_path / "large.json", {**base, "loop_earn_lr": 0.01}, 0.8520, -4.500, 6.000, reward_slope=0.01)
    _write(tmp_path / "meter.json", base, 0.8538, -4.5457, 4.5457)
    r = e504.reading(small=tmp_path / "small.json", mid=tmp_path / "mid.json", large=tmp_path / "large.json",
                     meter=tmp_path / "meter.json")
    assert set(r["runs"]) == {"small", "mid", "large", "meter"}
    assert r["spans"]["readable"] == {k: True for k in ("small", "mid", "large", "meter")}
    assert r["spans"]["replicates"] == [20], r["spans"]["replicates"]
    assert sorted(r["reward"]) == ["large", "small"], sorted(r["reward"])
    assert sorted(r["accuracy"]) == ["large", "mid", "small"], sorted(r["accuracy"])
    assert sorted(r["travel"]) == sorted(ARMS), sorted(r["travel"])
    #: the config is compared inside the spans, so the artifact carries no top-level `config`
    for k in ("small", "large"):
        assert r["spans"]["against"][k]["differ"] == {}, (k, r["spans"]["against"][k])
        assert r["spans"]["against"][k]["moved"]["loop_earn_lr"] == e504.RATES[k]
    assert set(r) == {"ok", "reason", "runs", "map", "reward", "accuracy", "shape", "travel", "spans"}
    #: an absent run reads as absent and refuses, rather than raising
    gone = e504.reading(small=tmp_path / "nope.json", mid=tmp_path / "mid.json", large=tmp_path / "large.json",
                        meter=tmp_path / "meter.json")
    assert gone["runs"]["small"] is None
    assert all(row["verdict"].startswith("REFUSED") or row["verdict"].startswith("FALSIFIER")
               for row in e504.judge(gone))


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e504_how_hard_the_map_is_paid.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e504.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    assert sorted(d["runs"]) == ["large", "meter", "mid", "small"], sorted(d["runs"])
    assert sorted(d["reward"]) == ["large", "small"], sorted(d["reward"])
    assert sorted(d["accuracy"]) == ["large", "mid", "small"], sorted(d["accuracy"])
    assert sorted(d["map"]) == ["large", "meter", "mid", "small"], sorted(d["map"])
    #: the counts that grow with the corpus are read as bounds, so a longer artifact does not break the test
    assert d["spans"]["replicates"] == [e504.MIN_REPS], d["spans"]["replicates"]
    for k in ("small", "large"):
        assert d["spans"]["against"][k] is None or d["spans"]["against"][k]["same"] >= 40, k
        if d["spans"]["against"][k] is not None:
            assert len(d["spans"]["against"][k]["draw"]["agree"]) >= 20, k
        if k in d["reward"]:
            assert d["reward"][k]["naive"]["n"] >= e504.MIN_REPS, k
    for k in ("small", "mid", "large"):
        if d["spans"]["reward_diagonal"][k] is None:
            continue
        for a in ARMS:
            assert d["spans"]["reward_diagonal"][k][a] <= 0.0, (k, a)
            assert 0.0 <= d["spans"]["accuracy_diagonal"][k][a] <= 1.0, (k, a)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
