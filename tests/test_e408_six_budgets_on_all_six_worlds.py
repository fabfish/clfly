"""`e408` puts the six worlds at six budgets each, so the tests pin both faces of the five claims, the run map that
names five units' artifacts, the refusal when one is absent, and the live stretch the unit samples.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e408_six_budgets_on_all_six_worlds as e408

#: the corpus's shape: the card's world leads at five of the six budgets and the span widens by a hundred
BODY = {
    "card": {1: 0.6792, 2: 0.6281, 5: 0.5979, 20: 0.5740, 100: 0.7000, 500: 0.7729},
    "cue14": {1: 0.6677, 2: 0.6438, 5: 0.5396, 20: 0.5490, 100: 0.6100, 500: 0.5396},
    "cue3": {1: 0.6521, 2: 0.6375, 5: 0.5510, 20: 0.5219, 100: 0.5800, 500: 0.5240},
    "cue1": {1: 0.6469, 2: 0.5854, 5: 0.5615, 20: 0.4990, 100: 0.5200, 500: 0.5062},
    "cue6": {1: 0.6729, 2: 0.6427, 5: 0.5458, 20: 0.5177, 100: 0.5400, 500: 0.4792},
    "cue9": {1: 0.6188, 2: 0.5760, 5: 0.4802, 20: 0.5115, 100: 0.4700, 500: 0.4625},
}
SEEDS = {"card": None, "cue14": 14, "cue3": 3, "cue1": 1, "cue6": 6, "cue9": 9}


def _settings(cueseed, iters, extra=None):
    return {"iters": iters, "lr": 0.003, "batch": 32, "circuit_size": 300, "basis": "cell_class", "seed0": 0,
            "cue_seed": cueseed, "save_theta": f"runs/theta_{cueseed}_{iters}",
            "json_out": f"runs/x_{cueseed}_{iters}.json", **(extra or {})}


def _doc(body=None, settings=None, initial=0.6875, previous=True, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run or its weights is absent
        return {"ok": False, "worlds": {}, "spread": {}, "correlation_with_far": {}, "previous": None, "reason": reason}
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
    readings = {b: [worlds[n]["budgets"][b]["body_task_0"] for n in order] for b in e408.BUDGETS}
    return {"ok": True, "worlds": worlds, "budgets": list(e408.BUDGETS), "arm": e408.NAIVE, "reps": e408.REPS,
            "previous": ({"artifact": "e407.json", "span_at_twenty": 0.0750} if previous else None),
            "spread": {**{str(b): max(readings[b]) - min(readings[b]) for b in e408.BUDGETS}, "initial": 0.0},
            "correlation_with_far": {str(b): e408._spearman(readings[b], readings[500])
                                     for b in e408.BUDGETS}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e408.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: one configuration at a hundred, the card on top there, and the span above the twenty one
    j = _judge()
    for cid in ("AK1", "AK2", "AK3", "AK4", "AK5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AK1: a field other than the cue seed varying at a hundred, and the cue seed not varying
    moved = {n: {b: _settings(SEEDS[n], b, {"loop_world_leak": (1.0 if n == "cue6" else 0.35)})
                 for b in e408.BUDGETS} for n in BODY}
    assert _judge(settings=moved)["AK1"].startswith("FALSIFIER")
    same = {n: {b: {**_settings(SEEDS[n], b), "cue_seed": None} for b in e408.BUDGETS} for n in BODY}
    assert _judge(settings=same)["AK1"].startswith("FALSIFIER")

    # AK2: another world above the card's at a hundred, and not
    lifted = {n: dict(v) for n, v in BODY.items()}
    lifted["cue9"][100] = 0.95
    assert _judge(body=lifted)["AK2"].startswith("FALSIFIER")
    assert _judge()["AK2"].startswith("MET")

    # AK3: a hundred-update order that barely agrees with the far end, and one between the bars
    flat = {n: dict(v) for n, v in BODY.items()}
    for i, n in enumerate(["cue9", "cue6", "cue1", "cue3", "cue14", "card"]):
        flat[n][100] = 0.80 - 0.02 * i
    assert _judge(body=flat)["AK3"].startswith("FALSIFIER")

    # AK4: a span at a hundred below the twenty-update one, and the previous artifact absent
    narrow = {n: dict(v) for n, v in BODY.items()}
    for n in narrow:
        narrow[n][100] = 0.60
    assert _judge(body=narrow)["AK4"].startswith("FALSIFIER")
    assert _judge(previous=False)["AK4"].startswith("REFUSED")

    # AK5: an initial reading that moves, and one between the bars
    assert _judge(initial=0.50)["AK5"].startswith("MET"), "one initial for every world and budget"
    moved_init = {n: dict(v) for n, v in BODY.items()}
    assert _judge(body=moved_init)["AK5"].startswith("MET")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e408.judge(_doc(ok=False)))


def test_the_run_map_names_five_units():
    #: the six budgets are read from five units' artifacts, and the hundred is this unit's own
    assert e408.BUDGETS == (1, 2, 5, 20, 100, 500), e408.BUDGETS
    assert e408.NEW == (100,), e408.NEW
    assert sorted(e408.SEEDS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e408.SEEDS)
    assert sorted(e408.FAR) == sorted(e408.SEEDS), "one far point per world"
    #: the helper's own names: `e405` and `e406` by world alone, `e407` and this unit's by world and budget
    assert e408.run_for("card", 1)[1].name == "e405_theta_card", e408.run_for("card", 1)[1].name
    assert e408.run_for("cue3", 2)[1].name == "e406_theta_cue3", e408.run_for("cue3", 2)[1].name
    assert e408.run_for("cue3", 5)[1].name == "e407_theta_cue3_5", e408.run_for("cue3", 5)[1].name
    assert e408.run_for("cue3", 20)[1].name == "e407_theta_cue3_20", e408.run_for("cue3", 20)[1].name
    assert e408.run_for("cue3", 100)[1].name == "e408_theta_cue3_100", e408.run_for("cue3", 100)[1].name
    assert e408.run_for("card", 500)[0].name.startswith("e380"), e408.run_for("card", 500)[0].name
    assert (e408.KEEPS, e408.RESHUFFLES) == (0.8, 0.6)


def test_the_live_stretch_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e408_six_budgets_on_all_six_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e408.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e408.judge(d)}
    #: the configuration and the initial reading are structural facts
    assert verdicts["AK1"].startswith("MET") and verdicts["AK5"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: every world carries all six budgets, the series is the artifact's own, and the correlation with the far end is 1
    for n, w in d["worlds"].items():
        assert sorted(int(b) for b in w["budgets"]) == list(e408.BUDGETS), n
    assert set(d["correlation_with_far"]) == {str(b) for b in e408.BUDGETS}, sorted(d["correlation_with_far"])
    assert d["correlation_with_far"]["500"] == 1.0, d["correlation_with_far"]
    assert d["previous"] and d["previous"]["span_at_twenty"] > 0, d["previous"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
