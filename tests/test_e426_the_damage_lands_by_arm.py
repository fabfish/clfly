"""`e426` reads every arm of the three both-ways rolls, so the tests pin both faces of the five claims, the refusal
when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e426_the_damage_lands_by_arm as e426

#: the corpus's shape: per configuration and order, each arm's per-position gain against its roll's naive
GAINS = {
    ("overlap", "as_built"): {"ewc": (0.0250, -0.0542, -0.0792), "replay": (0.0542, 0.0542, -0.0000)},
    ("overlap", "reverse"): {"ewc": (0.1083, -0.1000, -0.0333), "replay": (0.1042, -0.0000, -0.0042)},
    ("assembly", "as_built"): {"ewc": (0.1167, -0.1229, -0.0979), "replay": (0.2333, 0.0937, 0.0021)},
    ("assembly", "reverse"): {"ewc": (0.0187, -0.2021, -0.0896), "replay": (0.0875, 0.0667, -0.0104)},
    ("assembly-five", "as_built"): {"ewc": (0.1375, -0.2042, -0.1042), "ewc-block": (0.0001, -0.2250, -0.0458),
                                    "ewc-block-rand": (0.1333, -0.0875, -0.0500),
                                    "replay": (0.2792, 0.0667, -0.0042)},
    ("assembly-five", "reverse"): {"ewc": (0.0083, -0.2292, -0.1000), "ewc-block": (0.0417, -0.0750, -0.0250),
                                   "ewc-block-rand": (-0.0417, -0.0875, -0.0542),
                                   "replay": (0.0667, 0.0875, -0.0208)},
}


def _roll(config, order, arm, gain, reps=5):
    gain = list(gain)
    return {"config": config, "order": order, "arm": arm, "artifact": "x.json", "replicates": reps, "gain": gain,
            "mean": statistics.fmean(gain), "worst": max(range(len(gain)), key=lambda k: -gain[k]),
            "positions": len(gain)}


def _doc(gains=None, reps=5, differing=("task_order",), same=True, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": [], "configs": {}, "spans": {}}
    gains = GAINS if gains is None else gains
    rolls, configs = [], {}
    for (config, order), arms in gains.items():
        configs.setdefault(config, {"differing_config": list(differing), "same_tasks": same,
                                    "arms": sorted(arms)})
        for arm, gain in arms.items():
            rolls.append(_roll(config, order, arm, gain, reps))
    buffer = [r for r in rolls if r["arm"] == e426.BUFFER]
    penalty = [r for r in rolls if r["arm"] != e426.BUFFER]
    return {"ok": True, "reason": None, "rolls": rolls, "configs": configs,
            "spans": {"rolls": len(rolls), "buffer_rolls": len(buffer), "penalty_rolls": len(penalty),
                      "arms": sorted({r["arm"] for r in rolls}),
                      "replicates": sorted({r["replicates"] for r in rolls}),
                      "first_ahead": sum(1 for r in rolls if r["gain"][0] > r["gain"][-1]),
                      "first_positive": sum(1 for r in rolls if r["gain"][0] > 0),
                      "first_positive_min": min([r["gain"][0] for r in rolls if r["gain"][0] > 0] or [None]),
                      "buffer_positive_means": sum(1 for r in buffer if r["mean"] > 0),
                      "penalty_negative_means": sum(1 for r in penalty if r["mean"] < 0),
                      "buffer_worst_last": sum(1 for r in buffer if r["worst"] == r["positions"] - 1),
                      "penalty_worst_middle": sum(1 for r in penalty if r["worst"] == 1),
                      "worst_first_over_last": min(r["gain"][0] - r["gain"][-1] for r in rolls)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e426.judge(_doc(**kw))}


def _with(key, arm, gain):
    out = {k: {a: tuple(v) for a, v in arms.items()} for k, arms in GAINS.items()}
    out[key][arm] = tuple(gain)
    return out


def _flip(spec, k):
    """The corpus with the first position made a loss in ``k`` penalty arm-rolls."""
    out = {}
    for key, arms in spec.items():
        out[key] = {}
        for a, v in arms.items():
            if a != e426.BUFFER and k > 0:
                out[key][a] = (-0.01, v[1], v[1] - 0.05)
                k -= 1
            else:
                out[key][a] = tuple(v)
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: sixteen arm-rolls, the position effect everywhere, only the buffer's trade paying
    j = _judge()
    for cid in ("BB1", "BB2", "BB3", "BB4", "BB5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BB1: another field differing, a task set that is not the reverse, too few replicates, too few configurations
    assert _judge(differing=("task_order", "batch"))["BB1"].startswith("FALSIFIER")
    assert _judge(same=False)["BB1"].startswith("FALSIFIER")
    assert _judge(reps=4)["BB1"].startswith("FALSIFIER")
    two = {k: v for k, v in GAINS.items() if k[0] in ("overlap", "assembly")}
    assert _judge(gains=two)["BB1"].startswith("FALSIFIER")

    # BB2: an arm-roll whose last position is at least its first
    assert _judge(gains=_with(("overlap", "as_built"), "ewc", (0.02, -0.0542, +0.05)))["BB2"].startswith(
        "FALSIFIER")

    # BB3: a ledger whose first position gains in too few arm-rolls, and one that is between the bars
    assert _judge(gains=_flip(GAINS, 10))["BB3"].startswith("FALSIFIER")
    assert _judge(gains=_flip(GAINS, 2))["BB3"].startswith("NULL")

    # BB4: a buffer roll that does not pay, and a penalty roll that does
    assert _judge(gains=_with(("overlap", "as_built"), "replay", (-0.05, -0.05, -0.05)))["BB4"].startswith("FALSIFIER")
    assert _judge(gains=_with(("overlap", "as_built"), "ewc", (0.20, 0.20, 0.20)))["BB4"].startswith("FALSIFIER")

    # BB5: a buffer roll whose worst position is the middle, and a ledger where the penalties are worst at the end
    assert _judge(gains=_with(("overlap", "as_built"), "replay", (0.30, -0.05, 0.10)))["BB5"].startswith("FALSIFIER")
    ended = {k: {a: ((v[0], v[1], min(v) - 0.05) if a != e426.BUFFER else v) for a, v in arms.items()}
             for k, arms in GAINS.items()}
    assert _judge(gains=ended)["BB5"].startswith("FALSIFIER")

    #: a roll absent or carrying no naive arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e426.judge(_doc(ok=False)))


def test_the_pairs_and_the_thresholds_are_registered():
    #: three configurations rolled under both orders, `e315` and `e316`/`e317`'s runs
    assert sorted(e426.PAIRS) == ["assembly", "assembly-five", "overlap"], sorted(e426.PAIRS)
    for n, (a, b) in e426.PAIRS.items():
        assert "as_built" in a.name and "reverse" in b.name, n
    assert e426.BASELINE == "naive" and e426.BUFFER == "replay"
    assert e426.RUN_FIELDS == ("json_out", "save_theta")
    assert (e426.MIN_CONFIGS, e426.MIN_ARMS, e426.MIN_REPS) == (3, 3, 5)
    assert (e426.MIN_FIRST_POSITIVE, e426.FIRST_POSITIVE_FIRES) == (15, 13)
    assert (e426.MIN_MIDDLE_WORST, e426.MIDDLE_FIRST) == (8, 6)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e426_the_damage_lands_by_arm.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e426.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e426.judge(d)}
    #: the ledger being carried and the damage landing by arm are structural facts
    assert verdicts["BB1"].startswith("MET") and verdicts["BB5"].startswith("MET"), verdicts
    assert len(d["configs"]) >= e426.MIN_CONFIGS and len(d["spans"]["arms"]) >= e426.MIN_ARMS
    for n, c in d["configs"].items():
        assert c["differing_config"] == ["task_order"] and c["same_tasks"], n
    for x in d["rolls"]:
        assert x["replicates"] >= e426.MIN_REPS, x["artifact"]
        assert len(x["gain"]) == x["positions"], x["arm"]
        #: each roll's summary is its own gains
        assert abs(x["mean"] - sum(x["gain"]) / len(x["gain"])) < 1e-9, x["arm"]
        assert x["worst"] == max(range(len(x["gain"])), key=lambda k: -x["gain"][k]), x["arm"]
        assert x["gain"][0] > x["gain"][-1], x["arm"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
