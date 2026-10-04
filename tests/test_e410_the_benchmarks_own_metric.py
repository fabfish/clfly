"""`e410` reads the retention the six worlds' 500-update runs already carry, so the tests pin both faces of the five
claims, the refusal when a world's matrices are absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e410_the_benchmarks_own_metric as e410

#: the corpus's shape: the world's reading is the highest on the card's world and its final accuracy the lowest
WORLD = {
    "card": {"reading": 0.7729, "learned": [0.743, 0.760, 0.804], "final": [0.324, 0.429, 0.804],
             "forget": [0.419, 0.331, 0.0], "meanf": 0.3750, "finacc": 0.5191},
    "cue3": {"reading": 0.5240, "learned": [0.798, 0.801, 0.824], "final": [0.354, 0.472, 0.824],
             "forget": [0.444, 0.329, 0.0], "meanf": 0.3865, "finacc": 0.5500},
    "cue1": {"reading": 0.5062, "learned": [0.677, 0.764, 0.854], "final": [0.325, 0.465, 0.854],
             "forget": [0.352, 0.299, 0.0], "meanf": 0.3255, "finacc": 0.5479},
    "cue14": {"reading": 0.5396, "learned": [0.742, 0.839, 0.827], "final": [0.340, 0.464, 0.827],
              "forget": [0.402, 0.375, 0.0], "meanf": 0.3885, "finacc": 0.5434},
    "cue9": {"reading": 0.4625, "learned": [0.747, 0.849, 0.811], "final": [0.350, 0.435, 0.811],
             "forget": [0.397, 0.414, 0.0], "meanf": 0.4052, "finacc": 0.5323},
    "cue6": {"reading": 0.4792, "learned": [0.706, 0.798, 0.873], "final": [0.275, 0.417, 0.873],
             "forget": [0.431, 0.381, 0.0], "meanf": 0.4063, "finacc": 0.5215},
}


def _doc(worlds=None, reps=20, matrices=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a world's matrices are absent
        return {"ok": False, "worlds": {}, "correlation_reading_vs_accuracy": 0.0, "spread": {}, "reason": reason}
    worlds = worlds if worlds is not None else {k: dict(v) for k, v in WORLD.items()}
    out = {}
    for n, w in worlds.items():
        out[n] = {"artifact": f"{n}.json", "replicates": reps,
                  "matrices": reps if matrices is None else matrices, "world_reading_task_0": w["reading"],
                  "learned": w["learned"], "final": w["final"], "forgetting": w["forget"],
                  "mean_forgetting": w["meanf"], "final_accuracy": w["finacc"]}
    names = list(out)
    return {"ok": True, "worlds": out, "arm": e410.ARM,
            "correlation_reading_vs_accuracy": e410._spearman(
                [out[n]["world_reading_task_0"] for n in names], [out[n]["final_accuracy"] for n in names]),
            "spread": {"final_accuracy": max(out[n]["final_accuracy"] for n in names)
                       - min(out[n]["final_accuracy"] for n in names),
                       "mean_forgetting": max(out[n]["mean_forgetting"] for n in names)
                       - min(out[n]["mean_forgetting"] for n in names)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e410.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the matrices carried, the last task kept, the first lost, and the reading not tracking
    j = _judge()
    for cid in ("AO1", "AO2", "AO3", "AO4", "AO5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AO1: too few replicates, too few matrices, and too few worlds
    assert _judge(reps=19)["AO1"].startswith("FALSIFIER")
    assert _judge(matrices=19)["AO1"].startswith("FALSIFIER")
    assert _judge(worlds={k: v for k, v in list(WORLD.items())[:4]})["AO1"].startswith("FALSIFIER")

    # AO2: a world that forgets the last task
    forgets = {k: dict(v) for k, v in WORLD.items()}
    forgets["cue9"]["forget"] = [0.397, 0.414, 0.05]
    assert _judge(worlds=forgets)["AO2"].startswith("FALSIFIER")

    # AO3: a world that keeps the first task, and one between the bars
    keeps = {k: dict(v) for k, v in WORLD.items()}
    keeps["cue1"]["forget"] = [0.10, 0.299, 0.0]
    assert _judge(worlds=keeps)["AO3"].startswith("FALSIFIER")
    between = {k: dict(v) for k, v in WORLD.items()}
    between["cue1"]["forget"] = [0.25, 0.299, 0.0]
    assert _judge(worlds=between)["AO3"].startswith("NULL")

    # AO4: the card's world on top of the benchmark's metric
    top = {k: dict(v) for k, v in WORLD.items()}
    top["card"]["finacc"] = 0.90
    assert _judge(worlds=top)["AO4"].startswith("FALSIFIER")

    # AO5: a reading that does track the accuracy, and one between the bars
    tracks = {k: dict(v) for k, v in WORLD.items()}
    for i, n in enumerate(sorted(tracks, key=lambda x: tracks[x]["reading"])):
        tracks[n]["finacc"] = 0.50 + 0.01 * i
    assert _judge(worlds=tracks)["AO5"].startswith("FALSIFIER")

    #: a world's matrices absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e410.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the six worlds' 500-update runs, each beside the far-point reading `e396` gave it
    assert sorted(e410.RUNS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e410.RUNS)
    for n, (path, reading) in e410.RUNS.items():
        assert "iters500" in path.name or "e380" in path.name, n
        assert 0.0 <= reading <= 1.0, n
    assert e410.ARM == "naive" and e410.N_TASKS == 3
    assert (e410.MIN_WORLDS, e410.MIN_REPS) == (5, 20)
    assert (e410.LOST, e410.LOST_FIRES, e410.TRACKS, e410.TRACKS_FIRES) == (0.30, 0.20, 0.5, 0.7)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e410_the_benchmarks_own_metric.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e410.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e410.judge(d)}
    #: the matrices being carried and the last task being kept are structural facts
    assert verdicts["AO1"].startswith("MET") and verdicts["AO2"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: every world carries three per-task lists, and the correlation is the artifact's own
    for n, w in d["worlds"].items():
        assert len(w["learned"]) == len(w["final"]) == len(w["forgetting"]) == e410.N_TASKS, n
    assert -1.0 <= d["correlation_reading_vs_accuracy"] <= 1.0, d["correlation_reading_vs_accuracy"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
