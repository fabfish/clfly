"""`e419` reads the two arms' per-task final accuracy off the six worlds' far-point runs, so the tests pin both faces of
the five claims, the refusal when a world is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e419_what_the_buffer_buys as e419

#: the corpus's shape: per world, the naive and replay per-task final accuracies at the far point
FINAL = {
    "card": ([0.3240, 0.4292, 0.8042], [0.6135, 0.6781, 0.7438]),
    "cue1": ([0.3250, 0.4646, 0.8542], [0.5885, 0.6646, 0.7896]),
    "cue3": ([0.3542, 0.4719, 0.8240], [0.6563, 0.6906, 0.7500]),
    "cue6": ([0.2750, 0.4167, 0.8729], [0.5906, 0.6667, 0.7698]),
    "cue9": ([0.3500, 0.4354, 0.8115], [0.6542, 0.6812, 0.7333]),
    "cue14": ([0.3396, 0.4635, 0.8271], [0.6208, 0.6854, 0.7844]),
}


def _arms(naive, replay, reps=20, short=None):
    out = {}
    for arm, final in (("naive", naive), ("replay", replay)):
        out[arm] = {"replicates": reps,
                    "learned": list(final),
                    "final": list(final)[:short] if short else list(final),
                    "forgetting": [0.4, 0.33, 0.0]}
    return out


def _doc(worlds=None, reps=20, short=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "worlds": {}, "arms": list(e419.ARMS)}
    worlds = FINAL if worlds is None else worlds
    out = {}
    for name, (naive, replay) in worlds.items():
        arms = _arms(naive, replay, reps=reps, short=short)
        kmax = min(len(arms["replay"]["final"]), len(arms["naive"]["final"]), e419.N_TASKS)
        gains = [arms["replay"]["final"][k] - arms["naive"]["final"][k] for k in range(kmax)]
        gains = gains + [0.0] * (e419.N_TASKS - kmax)
        loss = -gains[e419.NEWEST]
        older = gains[e419.OLDEST] + gains[e419.MIDDLE]
        out[name] = {"artifact": f"{name}.json", "arms": arms, "gain_by_task": gains, "older_gain": older,
                     "newest_loss": loss, "coverage": older / loss if loss > 0 else float("inf")}
    pairs = [w["gain_by_task"][k] for w in out.values() for k in range(e419.N_TASKS)]
    return {"ok": True, "reason": None, "worlds": out, "arms": list(e419.ARMS),
            "spans": {"worlds": len(out),
                      "oldest": [w["gain_by_task"][e419.OLDEST] for w in out.values()],
                      "middle": [w["gain_by_task"][e419.MIDDLE] for w in out.values()],
                      "newest": [w["gain_by_task"][e419.NEWEST] for w in out.values()],
                      "least_oldest": min(w["gain_by_task"][e419.OLDEST] for w in out.values()),
                      "least_middle": min(w["gain_by_task"][e419.MIDDLE] for w in out.values()),
                      "worst_newest": max(w["gain_by_task"][e419.NEWEST] for w in out.values()),
                      "least_coverage": min(w["coverage"] for w in out.values()),
                      "mean_gain": sum(pairs) / len(pairs)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e419.judge(_doc(**kw))}


def _with(world=None, tasks=None):
    """A copy of the corpus with one world's replay per-task readings replaced."""
    out = {k: (list(v[0]), list(v[1])) for k, v in FINAL.items()}
    if tasks is not None:
        out[world] = (out[world][0], list(tasks))
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the ledger carried, gains on the two older tasks, a loss on the newest, five-fold coverage
    j = _judge()
    for cid in ("AT1", "AT2", "AT3", "AT4", "AT5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AT1: too few replicates, a short per-task list, and too few worlds
    assert _judge(reps=19)["AT1"].startswith("FALSIFIER")
    assert _judge(short=2)["AT1"].startswith("FALSIFIER")
    assert _judge(worlds={k: v for k, v in list(FINAL.items())[:4]})["AT1"].startswith("FALSIFIER")

    # AT2: a world with almost no gain on the oldest task, and one between the bars
    quiet = list(FINAL["card"][1])
    quiet[0] = FINAL["card"][0][0] + 0.03
    assert _judge(worlds=_with("card", quiet))["AT2"].startswith("FALSIFIER")
    mid = list(FINAL["card"][1])
    mid[0] = FINAL["card"][0][0] + 0.07
    assert _judge(worlds=_with("card", mid))["AT2"].startswith("NULL")

    # AT3: the same on the middle task
    quiet1 = list(FINAL["card"][1])
    quiet1[1] = FINAL["card"][0][1] + 0.03
    assert _judge(worlds=_with("card", quiet1))["AT3"].startswith("FALSIFIER")
    mid1 = list(FINAL["card"][1])
    mid1[1] = FINAL["card"][0][1] + 0.07
    assert _judge(worlds=_with("card", mid1))["AT3"].startswith("NULL")

    # AT4: a world where the newest task is not cost
    kept = list(FINAL["card"][1])
    kept[2] = FINAL["card"][0][2] + 0.01
    assert _judge(worlds=_with("card", kept))["AT4"].startswith("FALSIFIER")

    # AT5: a coverage under the falsifier bar, and one between the bars
    thin = list(FINAL["card"][1])
    thin[0] = FINAL["card"][0][0] + (1.5 * 0.0604 - 0.2490)
    assert _judge(worlds=_with("card", thin))["AT5"].startswith("FALSIFIER")
    medium = list(FINAL["card"][1])
    medium[0] = FINAL["card"][0][0] + (3.0 * 0.0604 - 0.2490)
    assert _judge(worlds=_with("card", medium))["AT5"].startswith("NULL")

    #: a world's run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e419.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the same six far-point runs `e410`, `e411` and `e413` read
    assert sorted(e419.RUNS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e419.RUNS)
    for n, p in e419.RUNS.items():
        assert "iters500" in p.name or "e380" in p.name, n
    assert e419.ARMS == ("naive", "replay") and e419.N_TASKS == 3
    assert (e419.OLDEST, e419.MIDDLE, e419.NEWEST) == (0, 1, 2)
    assert (e419.MIN_WORLDS, e419.MIN_REPS) == (5, 20)
    assert (e419.GAIN, e419.GAIN_FIRES) == (0.10, 0.05)
    assert (e419.LOSS, e419.RATIO, e419.RATIO_FIRES) == (0.0, 4.0, 2.0)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e419_what_the_buffer_buys.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e419.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e419.judge(d)}
    #: the ledger being carried and the newest task being cost are structural facts
    assert verdicts["AT1"].startswith("MET") and verdicts["AT4"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    for n, w in d["worlds"].items():
        for arm in e419.ARMS:
            assert w["arms"][arm]["replicates"] >= e419.MIN_REPS, (n, arm)
            assert len(w["arms"][arm]["final"]) == e419.N_TASKS, (n, arm)
        #: the per-task gain is the two arms' difference, and the coverage is the two older gains over the newest loss
        for k in range(e419.N_TASKS):
            got = w["arms"]["replay"]["final"][k] - w["arms"]["naive"]["final"][k]
            assert abs(got - w["gain_by_task"][k]) < 1e-12, (n, k)
        assert w["gain_by_task"][e419.NEWEST] < e419.LOSS, n
        older = w["gain_by_task"][e419.OLDEST] + w["gain_by_task"][e419.MIDDLE]
        assert abs(w["coverage"] - older / w["newest_loss"]) < 1e-9, n
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
