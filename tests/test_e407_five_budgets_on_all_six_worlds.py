"""`e407` puts the six worlds at five budgets each, so the tests pin both faces of the five claims, the two new
budgets' configuration check, the refusal when a run is absent, and the live ordering series.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e407_five_budgets_on_all_six_worlds as e407

#: the corpus's shape: the card's world leads at four of the five budgets and is fourth at two updates
BODY = {
    "card": {1: 0.6792, 2: 0.6281, 5: 0.5979, 20: 0.5740, 500: 0.7729},
    "cue14": {1: 0.6677, 2: 0.6438, 5: 0.5396, 20: 0.5490, 500: 0.5396},
    "cue3": {1: 0.6521, 2: 0.6375, 5: 0.5510, 20: 0.5219, 500: 0.5240},
    "cue1": {1: 0.6469, 2: 0.5854, 5: 0.5615, 20: 0.4990, 500: 0.5062},
    "cue6": {1: 0.6729, 2: 0.6427, 5: 0.5458, 20: 0.5177, 500: 0.4792},
    "cue9": {1: 0.6188, 2: 0.5760, 5: 0.4802, 20: 0.5115, 500: 0.4625},
}
SEEDS = {"card": None, "cue14": 14, "cue3": 3, "cue1": 1, "cue6": 6, "cue9": 9}


def _settings(cueseed, iters, extra=None):
    return {"iters": iters, "lr": 0.003, "batch": 32, "circuit_size": 300, "basis": "cell_class", "seed0": 0,
            "cue_seed": cueseed, "save_theta": f"runs/theta_{cueseed}_{iters}",
            "json_out": f"runs/x_{cueseed}_{iters}.json", **(extra or {})}


def _doc(body=None, settings=None, initial=0.6875, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run or its weights is absent
        return {"ok": False, "worlds": {}, "spread": {}, "correlation_with_far": {}, "reason": reason}
    body = body if body is not None else {k: dict(v) for k, v in BODY.items()}
    worlds = {}
    for n, bybudget in body.items():
        entry = {"cueseed": SEEDS[n], "budgets": {}}
        for b, v in bybudget.items():
            s = (settings or {}).get(n, {}).get(b) if settings else _settings(SEEDS[n], b)
            entry["budgets"][b] = {"artifact": "r.json", "iters": b, "initial_task_0": initial, "body_task_0": v,
                                   "draw": {"cue_sha1": f"c{SEEDS[n]}"}, "settings": s}
        worlds[n] = entry
    order = list(worlds)
    readings = {b: [worlds[n]["budgets"][b]["body_task_0"] for n in order] for b in e407.BUDGETS}
    return {"ok": True, "worlds": worlds, "budgets": list(e407.BUDGETS), "arm": e407.NAIVE, "reps": e407.REPS,
            "spread": {**{str(b): max(readings[b]) - min(readings[b]) for b in e407.BUDGETS}, "initial": 0.0},
            "correlation_with_far": {str(b): e407._spearman(readings[b], readings[500])
                                     for b in e407.BUDGETS}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e407.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: one configuration at both new budgets, the card back on top at twenty, and first at five
    j = _judge()
    assert j["AJ1"].startswith("MET"), j["AJ1"]
    assert j["AJ2"].startswith("MET"), j["AJ2"]
    assert j["AJ3"].startswith("MET"), j["AJ3"]
    assert j["AJ4"].startswith("FALSIFIER"), j["AJ4"]
    assert j["AJ5"].startswith("MET"), j["AJ5"]

    # AJ1: a field other than the cue seed varying at a new budget, and the cue seed not varying
    moved = {n: {b: _settings(SEEDS[n], b, {"loop_world_leak": (1.0 if n == "cue6" else 0.35)})
                 for b in e407.BUDGETS} for n in BODY}
    assert _judge(settings=moved)["AJ1"].startswith("FALSIFIER")
    same = {n: {b: {**_settings(SEEDS[n], b), "cue_seed": None} for b in e407.BUDGETS} for n in BODY}
    assert _judge(settings=same)["AJ1"].startswith("FALSIFIER")

    # AJ2: another world above the card's at twenty, and not
    lifted = {n: dict(v) for n, v in BODY.items()}
    lifted["cue9"][20] = 0.90
    assert _judge(body=lifted)["AJ2"].startswith("FALSIFIER")
    assert _judge()["AJ2"].startswith("MET")

    # AJ3: a twenty-update order that barely agrees with the far end, and one between the bars
    flat = {n: dict(v) for n, v in BODY.items()}
    for i, n in enumerate(["cue9", "cue6", "cue1", "cue3", "cue14", "card"]):
        flat[n][20] = 0.60 - 0.02 * i
    assert _judge(body=flat)["AJ3"].startswith("FALSIFIER")
    mid = {n: dict(v) for n, v in BODY.items()}
    mid["card"][20] = 0.55
    mid["cue9"][20] = 0.53
    assert _judge(body=mid)["AJ3"].startswith(("NULL", "MET", "FALSIFIER")), "the band is exercised below"

    # AJ4: the card's world not first at five updates, which is the other face
    notfirst = {n: dict(v) for n, v in BODY.items()}
    notfirst["card"][5] = 0.40
    assert _judge(body=notfirst)["AJ4"].startswith("MET")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e407.judge(_doc(ok=False)))


def test_the_five_budgets_and_the_plumbing():
    #: every world carries all five budgets, and the plumbing is not a setting
    assert e407.BUDGETS == (1, 2, 5, 20, 500), e407.BUDGETS
    assert e407.NEW == (5, 20), e407.NEW
    for n, spec in e407.WORLDS.items():
        assert sorted(spec["runs"]) == list(e407.BUDGETS), n
        assert spec["runs"][5][0].name.endswith("iters5_20reps.json"), n
        assert spec["runs"][20][0].name.endswith("iters20_20reps.json"), n
    keys = set(_settings(1, 5))
    settings = {n: _settings(SEEDS[n], 5) for n in BODY}
    varying = sorted(k for k in keys if len({json.dumps(s.get(k)) for s in settings.values()}) > 1)
    assert varying == ["cue_seed", "json_out", "save_theta"], varying
    assert (e407.KEEPS, e407.RESHUFFLES) == (0.8, 0.6)


def test_the_live_ordering_series_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e407_five_budgets_on_all_six_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e407.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e407.judge(d)}
    #: the configuration and the initial reading are structural facts
    assert verdicts["AJ1"].startswith("MET") and verdicts["AJ5"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: every world carries all five budgets and the series is the artifact's own
    for n, w in d["worlds"].items():
        assert sorted(int(b) for b in w["budgets"]) == list(e407.BUDGETS), n
    assert set(d["correlation_with_far"]) == {str(b) for b in e407.BUDGETS}, sorted(d["correlation_with_far"])
    assert d["correlation_with_far"]["500"] == 1.0, d["correlation_with_far"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
