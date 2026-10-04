"""`e411` reads the second arm's retention off the same six runs `e410` read, so the tests pin both faces of the five
claims, the refusal when `e410`'s artifact is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e411_the_rehearsal_on_the_six_worlds as e411

#: the corpus's shape: the rehearsal helps on every world, the least on `cue1`, and the cuts are all above a fifth
WORLD = {
    "card": {"naive": 0.5191, "naive_mf": 0.3750, "replay": 0.6785, "replay_mf": 0.0906},
    "cue9": {"naive": 0.5323, "naive_mf": 0.4052, "replay": 0.6896, "replay_mf": 0.0979},
    "cue6": {"naive": 0.5215, "naive_mf": 0.4063, "replay": 0.6757, "replay_mf": 0.0917},
    "cue14": {"naive": 0.5434, "naive_mf": 0.3885, "replay": 0.6969, "replay_mf": 0.1130},
    "cue3": {"naive": 0.5500, "naive_mf": 0.3865, "replay": 0.6990, "replay_mf": 0.1187},
    "cue1": {"naive": 0.5479, "naive_mf": 0.3255, "replay": 0.6809, "replay_mf": 0.0917},
}
SPAN = 0.0309


def _doc(worlds=None, reps=20, matrices=None, previous=True, ok=True, reason="absent"):
    if not ok:
        #: a world's second arm absent refuses the whole unit
        return {"ok": False, "reason": reason, "worlds": {}, "arms": list(e411.ARMS), "previous": None, "spread": {}}
    worlds = worlds if worlds is not None else {k: dict(v) for k, v in WORLD.items()}
    out = {}
    for n, w in worlds.items():
        arms = {}
        for arm in e411.ARMS:
            acc = w[arm]
            mf = w[f"{arm}_mf"]
            arms[arm] = {"replicates": reps, "matrices": reps if matrices is None else matrices,
                         "final_accuracy": acc, "mean_forgetting": mf,
                         "final": [acc] * e411.N_TASKS, "forgetting": [mf] * e411.N_TASKS}
        out[n] = {"artifact": f"{n}.json", "arms": arms,
                  "accuracy_gain": w["replay"] - w["naive"], "forgetting_cut": w["naive_mf"] - w["replay_mf"]}
    names = list(out)
    prev = {"artifact": e411.PREVIOUS.name, "naive_span": SPAN} if previous else None
    return {"ok": True, "reason": None, "worlds": out, "arms": list(e411.ARMS), "previous": prev,
            "spread": {"naive_accuracy": max(out[n]["arms"]["naive"]["final_accuracy"] for n in names)
                       - min(out[n]["arms"]["naive"]["final_accuracy"] for n in names),
                       "replay_accuracy": max(out[n]["arms"]["replay"]["final_accuracy"] for n in names)
                       - min(out[n]["arms"]["replay"]["final_accuracy"] for n in names),
                       "accuracy_gain": max(out[n]["accuracy_gain"] for n in names)
                       - min(out[n]["accuracy_gain"] for n in names),
                       "forgetting_cut": max(out[n]["forgetting_cut"] for n in names)
                       - min(out[n]["forgetting_cut"] for n in names)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e411.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: both arms carried, the aid positive everywhere, the cuts shallow everywhere
    j = _judge()
    for cid in ("AP1", "AP2", "AP3", "AP4", "AP5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AP1: too few replicates, too few matrices, and too few worlds
    assert _judge(reps=19)["AP1"].startswith("FALSIFIER")
    assert _judge(matrices=19)["AP1"].startswith("FALSIFIER")
    assert _judge(worlds={k: v for k, v in list(WORLD.items())[:4]})["AP1"].startswith("FALSIFIER")

    # AP2: a world the rehearsal does not help
    worse = {k: dict(v) for k, v in WORLD.items()}
    worse["cue1"]["replay"] = worse["cue1"]["naive"]
    assert _judge(worlds=worse)["AP2"].startswith("FALSIFIER")

    # AP3: a world under the falsifier bar, and one between the bars
    under = {k: dict(v) for k, v in WORLD.items()}
    under["cue1"]["replay"] = under["cue1"]["naive"] + 0.03
    assert _judge(worlds=under)["AP3"].startswith("FALSIFIER")
    between = {k: dict(v) for k, v in WORLD.items()}
    between["cue1"]["replay"] = between["cue1"]["naive"] + 0.07
    assert _judge(worlds=between)["AP3"].startswith("NULL")

    # AP4: a world under the falsifier bar, and one between the bars
    shallow = {k: dict(v) for k, v in WORLD.items()}
    shallow["cue1"]["replay_mf"] = shallow["cue1"]["naive_mf"] - 0.05
    assert _judge(worlds=shallow)["AP4"].startswith("FALSIFIER")
    mid = {k: dict(v) for k, v in WORLD.items()}
    mid["cue1"]["replay_mf"] = mid["cue1"]["naive_mf"] - 0.12
    assert _judge(worlds=mid)["AP4"].startswith("NULL")

    # AP5: the aid failing to clear twice the draw's own span, and the refusal when `e410` is absent
    thin = {k: dict(v) for k, v in WORLD.items()}
    for n in thin:
        thin[n]["replay"] = thin[n]["naive"] + 0.01
    assert _judge(worlds=thin)["AP5"].startswith("FALSIFIER")
    assert _judge(previous=False)["AP5"].startswith("REFUSED")

    #: a world's second arm absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e411.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the same six 500-update runs `e410` read, the card's from `e380` and the five cues from `e398`/`e399`/`e401`
    assert sorted(e411.RUNS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e411.RUNS)
    for n, path in e411.RUNS.items():
        assert "iters500" in path.name or "e380" in path.name, n
    assert e411.PREVIOUS.name == "e410_the_benchmarks_own_metric.json"
    assert e411.ARMS == ("naive", "replay") and e411.N_TASKS == 3
    assert (e411.MIN_WORLDS, e411.MIN_REPS) == (5, 20)
    assert (e411.GAIN, e411.GAIN_FIRES, e411.CUT, e411.CUT_FIRES) == (0.10, 0.05, 0.15, 0.10)
    assert (e411.SPAN_FALLBACK, e411.TWICE) == (0.0309, 2.0)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e411_the_rehearsal_on_the_six_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e411.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e411.judge(d)}
    #: both arms being carried and the aid being positive on every world are structural facts
    assert verdicts["AP1"].startswith("MET") and verdicts["AP2"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: every world carries both the naive and the replay arm, each with the full per-task lists
    for n, w in d["worlds"].items():
        for arm in e411.ARMS:
            a = w["arms"][arm]
            assert a["replicates"] >= e411.MIN_REPS and a["matrices"] >= e411.MIN_REPS, (n, arm)
            assert len(a["final"]) == len(a["forgetting"]) == e411.N_TASKS, (n, arm)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
