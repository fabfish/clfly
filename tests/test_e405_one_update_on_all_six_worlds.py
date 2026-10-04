"""`e405` runs all six measured worlds for one update and puts them against their five-hundred-update readings, so the
tests pin both faces of the five claims, the plumbing the configuration check must ignore, and the live result.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e405_one_update_on_all_six_worlds as e405

#: the corpus's shape: the card's world loses least after one update and the six are already ordered
GOOD_ONE = {"card": 0.6792, "cue6": 0.6729, "cue14": 0.6677, "cue3": 0.6521, "cue1": 0.6469, "cue9": 0.6188}
GOOD_FAR = {"card": 0.7729, "cue14": 0.5396, "cue3": 0.5240, "cue1": 0.5062, "cue6": 0.4792, "cue9": 0.4625}
SEEDS = {"card": None, "cue6": 6, "cue14": 14, "cue3": 3, "cue1": 1, "cue9": 9}


def _settings(cueseed, extra=None):
    return {"iters": 1, "lr": 0.003, "batch": 32, "circuit_size": 300, "basis": "cell_class", "seed0": 0,
            "cue_seed": cueseed, "save_theta": f"runs/theta_{cueseed}", "json_out": f"runs/x_{cueseed}.json",
            **(extra or {})}


def _doc(one=None, far=None, settings=None, initial=0.6875, initials=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run or its weights is absent
        return {"ok": False, "worlds": {}, "spread": {}, "reason": reason}
    one = one if one is not None else dict(GOOD_ONE)
    far = far if far is not None else dict(GOOD_FAR)
    worlds = {}
    for n in one:
        settings_n = (settings or {}).get(n) if settings else _settings(SEEDS[n])
        init_n = (initials or {}).get(n, initial)
        worlds[n] = {"cueseed": SEEDS[n],
                     "one": {"artifact": "o.json", "iters": 1, "initial_task_0": init_n, "body_task_0": one[n],
                             "cue_sha1": f"c{SEEDS[n]}", "cue_seed": SEEDS[n], "settings": settings_n},
                     "far": {"artifact": "f.json", "iters": 500, "initial_task_0": init_n, "body_task_0": far[n],
                             "cue_sha1": f"c{SEEDS[n]}", "cue_seed": SEEDS[n], "settings": settings_n},
                     "one_gain": one[n] - init_n, "far_gain": far[n] - init_n}
    ones = [w["one"]["body_task_0"] for w in worlds.values()]
    fars = [w["far"]["body_task_0"] for w in worlds.values()]
    inits = [w["one"]["initial_task_0"] for w in worlds.values()]
    return {"ok": True, "worlds": worlds, "arm": e405.NAIVE, "reps": e405.REPS,
            "spread": {"one": max(ones) - min(ones), "far": max(fars) - min(fars),
                       "initial": max(inits) - min(inits)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e405.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the configuration held, the first update mild but not uniformly, and the ordering present
    j = _judge()
    assert j["AH1"].startswith("MET"), j["AH1"]
    assert j["AH2"].startswith("NULL"), j["AH2"]
    assert j["AH3"].startswith("FALSIFIER"), j["AH3"]
    assert j["AH4"].startswith("MET"), j["AH4"]
    assert j["AH5"].startswith("FALSIFIER"), j["AH5"]

    # AH1: a field other than the cue seed varying, and a corpus where the cue seed does not vary
    moved = {n: _settings(SEEDS[n], {"loop_world_leak": (1.0 if n == "cue6" else 0.35)}) for n in GOOD_ONE}
    assert _judge(settings=moved)["AH1"].startswith("FALSIFIER")
    same = {n: _settings(SEEDS[n]) for n in GOOD_ONE}
    for n in same:
        same[n] = {**same[n], "cue_seed": None}
    assert _judge(settings=same)["AH1"].startswith("FALSIFIER")

    # AH2: a first update that costs one world more than the falsifier's bar, and one between the bars
    assert _judge(one={**GOOD_ONE, "cue9": 0.50})["AH2"].startswith("FALSIFIER")
    assert _judge(one={**GOOD_ONE, "cue9": 0.63})["AH2"].startswith("NULL")
    #: and a corpus where every world's first update is mild, which is the other face
    mild = {n: 0.6875 - 0.001 * (i + 1) for i, n in enumerate(GOOD_ONE)}
    assert _judge(one=mild)["AH2"].startswith("MET")

    # AH3: a one-update span inside the bar with a far span above its own, and a narrow far span
    assert _judge(one={n: 0.6875 - 0.002 * i for i, n in enumerate(GOOD_ONE)})["AH3"].startswith("MET")
    assert _judge(far={n: 0.70 - 0.001 * i for i, n in enumerate(GOOD_FAR)})["AH3"].startswith("FALSIFIER")
    #: and a corpus whose one-update span is the wide one
    assert _judge(one={**GOOD_ONE, "cue9": 0.50})["AH3"].startswith("FALSIFIER")

    # AH4: an initial reading that moves, and one between the bars
    assert _judge(initials={**{n: 0.6875 for n in GOOD_ONE}, "cue9": 0.55})["AH4"].startswith("FALSIFIER")
    assert _judge(initials={**{n: 0.6875 for n in GOOD_ONE}, "cue9": 0.60})["AH4"].startswith("NULL")

    # AH5: the card's world inside the failing range, which is the other face
    assert _judge(one={**GOOD_ONE, "card": 0.65})["AH5"].startswith("MET")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e405.judge(_doc(ok=False)))


def test_the_plumbing_is_not_a_setting():
    #: the runner writes where a run's artifact and weights went into its own namespace, and that is not a setting
    keys = set(_settings(1))
    assert {"save_theta", "json_out"} <= keys, "the fixture must carry the plumbing"
    settings = {n: _settings(SEEDS[n]) for n in GOOD_ONE}
    varying = sorted(k for k in keys
                     if len({json.dumps(s.get(k)) for s in settings.values()}) > 1)
    assert varying == ["cue_seed", "json_out", "save_theta"], varying
    #: and the six worlds are the registered ones, one update against five hundred
    assert sorted(e405.WORLDS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e405.WORLDS)
    for n, spec in e405.WORLDS.items():
        assert spec["one"][0].name.endswith("iters1_20reps.json"), n
        assert "iters500" in spec["far"][0].name or "e380" in spec["far"][0].name, n


def test_the_live_result_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e405_one_update_on_all_six_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e405.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e405.judge(d)}
    #: the configuration and the initial reading are structural facts
    assert verdicts["AH1"].startswith("MET") and verdicts["AH4"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: every world carries both budgets, and the two spans are the artifact's own
    for n, w in d["worlds"].items():
        assert w["one"]["iters"] == 1 and w["far"]["iters"] == 500, n
        assert w["one_gain"] == w["one"]["body_task_0"] - w["one"]["initial_task_0"], n
    assert d["spread"]["far"] > d["spread"]["one"], d["spread"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
