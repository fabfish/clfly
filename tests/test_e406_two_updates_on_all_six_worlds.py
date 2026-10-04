"""`e406` runs the second step on all six worlds, so the tests pin both faces of the five claims, the plumbing the
configuration check ignores, and the live reshuffle the unit measures.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e406_two_updates_on_all_six_worlds as e406

#: the corpus's shape: the card's world is first after one update, fourth after two and first again at five hundred
ONE = {"card": 0.6792, "cue6": 0.6729, "cue14": 0.6677, "cue3": 0.6521, "cue1": 0.6469, "cue9": 0.6188}
TWO = {"card": 0.6281, "cue6": 0.6427, "cue14": 0.6438, "cue3": 0.6375, "cue1": 0.5854, "cue9": 0.5760}
FAR = {"card": 0.7729, "cue14": 0.5396, "cue3": 0.5240, "cue1": 0.5062, "cue6": 0.4792, "cue9": 0.4625}
SEEDS = {"card": None, "cue6": 6, "cue14": 14, "cue3": 3, "cue1": 1, "cue9": 9}
SPANS = {"one": 0.0604, "far": 0.3104}


def _settings(cueseed, extra=None):
    return {"iters": 2, "lr": 0.003, "batch": 32, "circuit_size": 300, "basis": "cell_class", "seed0": 0,
            "cue_seed": cueseed, "save_theta": f"runs/theta_{cueseed}", "json_out": f"runs/x_{cueseed}.json",
            **(extra or {})}


def _doc(one=None, two=None, far=None, settings=None, initial=0.6875, previous=True, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run or its weights is absent
        return {"ok": False, "worlds": {}, "spread": {}, "previous": None, "reason": reason}
    one = one if one is not None else dict(ONE)
    two = two if two is not None else dict(TWO)
    far = far if far is not None else dict(FAR)
    worlds = {}
    for n in one:
        s = (settings or {}).get(n) if settings else _settings(SEEDS[n])
        worlds[n] = {"cueseed": SEEDS[n],
                     "one": {"artifact": "o.json", "iters": 1, "initial_task_0": initial, "body_task_0": one[n],
                             "settings": s},
                     "two": {"artifact": "t.json", "iters": 2, "initial_task_0": initial, "body_task_0": two[n],
                             "settings": s},
                     "far": {"artifact": "f.json", "iters": 500, "initial_task_0": initial, "body_task_0": far[n],
                             "settings": s}}
    #: the three lists must be read in **one** order, or a reshuffled `two` would be paired against the wrong world
    names = list(one)
    ones = [worlds[n]["one"]["body_task_0"] for n in names]
    twos = [worlds[n]["two"]["body_task_0"] for n in names]
    fars = [worlds[n]["far"]["body_task_0"] for n in names]
    return {"ok": True, "worlds": worlds, "arm": e406.NAIVE, "reps": e406.REPS,
            "previous": ({"artifact": "e405.json", "one_span": SPANS["one"], "far_span": SPANS["far"]}
                         if previous else None),
            "spread": {"one": max(ones) - min(ones), "two": max(twos) - min(twos), "far": max(fars) - min(fars),
                       "initial": 0.0},
            "correlation_one_two": e406._spearman(ones, twos),
            "correlation_two_far": e406._spearman(twos, fars)}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e406.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: one configuration, a reshuffle at the second step, and a span between the two others
    j = _judge()
    assert j["AI1"].startswith("MET"), j["AI1"]
    assert j["AI2"].startswith("NULL"), j["AI2"]
    assert j["AI3"].startswith("FALSIFIER"), j["AI3"]
    assert j["AI4"].startswith("MET"), j["AI4"]
    assert j["AI5"].startswith("MET"), j["AI5"]

    # AI1: a field other than the cue seed varying, and a corpus where the cue seed does not vary
    moved = {n: _settings(SEEDS[n], {"loop_world_leak": (1.0 if n == "cue6" else 0.35)}) for n in ONE}
    assert _judge(settings=moved)["AI1"].startswith("FALSIFIER")
    same = {n: {**_settings(SEEDS[n]), "cue_seed": None} for n in ONE}
    assert _judge(settings=same)["AI1"].startswith("FALSIFIER")

    # AI2: an order that survives (the two-update readings in the one-update's order), and one that reshuffles
    kept = {n: 0.70 - 0.01 * i for i, n in enumerate(sorted(ONE, key=lambda x: -ONE[x]))}
    assert _judge(two=kept)["AI2"].startswith("MET")
    assert _judge(two={n: 0.70 - 0.01 * i for i, n in enumerate(sorted(ONE, key=lambda x: ONE[x]))})[
        "AI2"].startswith("FALSIFIER")
    #: and one between the bars
    #: with six worlds the rank correlation is discrete, and this assignment puts it at 0.771 -- in the null band
    between = {"card": 0.68, "cue6": 0.69, "cue14": 0.70, "cue3": 0.67, "cue1": 0.66, "cue9": 0.65}
    assert _judge(two=between)["AI2"].startswith("NULL")

    # AI3: the card's world still on top after two updates, and not
    assert _judge(two={**TWO, "card": 0.70})["AI3"].startswith("MET")
    assert _judge(two={**TWO, "cue14": 0.90})["AI3"].startswith("FALSIFIER")

    # AI4: an initial reading that moves, and one between the bars
    assert _judge(two={**TWO, "cue9": 0.55}, initial=0.6875)["AI4"].startswith("MET"), "one initial for all six"
    flat = {**TWO}
    assert _judge(two=flat)["AI4"].startswith("MET")

    # AI5: a two-update span at or below the one-update one, and one at or above the five-hundred one
    assert _judge(two={n: 0.6875 - 0.001 * i for i, n in enumerate(TWO)})["AI5"].startswith("FALSIFIER")
    assert _judge(two={n: 0.6875 - 0.1 * i for i, n in enumerate(TWO)})["AI5"].startswith("FALSIFIER")
    assert _judge(previous=False)["AI5"].startswith("REFUSED")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e406.judge(_doc(ok=False)))


def test_the_three_budgets_and_the_plumbing():
    #: the six worlds carry a one-, a two- and a five-hundred-update run each, and the plumbing is not a setting
    assert sorted(e406.WORLDS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e406.WORLDS)
    for n, spec in e406.WORLDS.items():
        assert spec["one"][0].name.endswith("iters1_20reps.json"), n
        assert spec["two"][0].name.endswith("iters2_20reps.json"), n
        assert "iters500" in spec["far"][0].name or "e380" in spec["far"][0].name, n
    keys = set(_settings(1))
    assert {"save_theta", "json_out"} <= keys
    settings = {n: _settings(SEEDS[n]) for n in ONE}
    varying = sorted(k for k in keys if len({json.dumps(s.get(k)) for s in settings.values()}) > 1)
    assert varying == ["cue_seed", "json_out", "save_theta"], varying
    assert (e406.KEEPS, e406.RESHUFFLES) == (0.8, 0.6)


def test_the_live_reshuffle_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e406_two_updates_on_all_six_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e406.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e406.judge(d)}
    #: the configuration and the initial reading are structural facts
    assert verdicts["AI1"].startswith("MET") and verdicts["AI4"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: every world carries all three budgets, and the correlations are the artifact's own
    for n, w in d["worlds"].items():
        assert [w[b]["iters"] for b in ("one", "two", "far")] == [1, 2, 500], n
    assert -1.0 <= d["correlation_one_two"] <= 1.0 and -1.0 <= d["correlation_two_far"] <= 1.0, d
    assert d["previous"] and d["previous"]["one_span"] < d["previous"]["far_span"], d["previous"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
