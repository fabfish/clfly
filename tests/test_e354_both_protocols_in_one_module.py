"""`e354` runs both protocols in one module, so the tests pin the four arms, the paired cost, the buffer's value in
each protocol and both faces of the four claims.
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

from experiments import e354_both_protocols_in_one_module as e354


def _row(protocol, arm, forget, diag=0.80, seed=0, world="w"):
    return {"seed": seed, "protocol": protocol, "arm": arm, "chance": 0.25, "shared_head": protocol == e354.CLASS,
            "diagonal_mean": diag, "mean_forgetting": forget, "final": [0.3, 0.5, 0.8],
            "n_buffer": 2 if arm == e354.REPLAY else 0,
            "retention": [[0.8, None, None], [0.4, 0.8, None], [0.3, 0.5, 0.8]],
            "world_dims": 8, "world_drive_sha1": "d", "world_read_sha1": world, "world_leak": 0.35,
            "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f"}


def _reading(costs=(-0.1667, 0.0313, -0.0937, 0.2813, 0.0521), task=(0.54, 0.32, 0.31, 0.19, 0.30),
             replay_gap=0.0479, seeds=5, cost_override=None, world_override=None):
    rows = []
    for i in range(seeds):
        base = task[i % len(task)]
        rows += [_row(e354.TASK, e354.NAIVE, base, seed=i),
                 _row(e354.TASK, e354.REPLAY, base - 0.2188, seed=i),
                 _row(e354.CLASS, e354.NAIVE, base + costs[i % len(costs)], seed=i),
                 _row(e354.CLASS, e354.REPLAY, base + costs[i % len(costs)] - 0.2188 - replay_gap, seed=i)]
    if world_override is not None:
        #: one cell's world, and only that cell's, so T1's falsifier can be read on a synthetic corpus
        rows[2]["world_read_sha1"] = world_override

    def cell(protocol, arm, field):
        vals = [r[field] for r in rows if r["protocol"] == protocol and r["arm"] == arm]
        return {"n": len(vals), "mean": statistics.fmean(vals),
                "sem": statistics.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else None, "vals": vals}

    out = {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_tasks": 3, "n_classes": 4, "n_symbols": 12,
           "chance": 0.25, "n_train": 96, "n_test": 48, "world_dims": 8, "world_leak": 0.35, "lr": 3e-3,
           "iters": 500, "batch": 32, "protocols": list(e354.PROTOCOLS), "arms": list(e354.ARMS),
           "seeds": list(range(seeds)), "rows": rows}
    for p in e354.PROTOCOLS:
        for a in e354.ARMS:
            out[f"{p}_{a}_forgetting"] = cell(p, a, "mean_forgetting")
            out[f"{p}_{a}_diagonal"] = cell(p, a, "diagonal_mean")
    out["cost"] = {}
    for arm in e354.ARMS:
        paired = [c - t for c, t in zip(cell(e354.CLASS, arm, "mean_forgetting")["vals"],
                                       cell(e354.TASK, arm, "mean_forgetting")["vals"])]
        mean = statistics.fmean(paired)
        sem = statistics.stdev(paired) / math.sqrt(len(paired)) if len(paired) > 1 else None
        out["cost"][arm] = {"n": len(paired), "vals": paired, "mean": mean, "sem": sem,
                            "sigma": abs(mean) / sem if sem else None}
    if cost_override is not None:
        out["cost"][e354.NAIVE] = dict(cost_override)
    out["buffer_value"] = {p: out[f"{p}_{e354.REPLAY}_forgetting"]["mean"]
                           - out[f"{p}_{e354.NAIVE}_forgetting"]["mean"] for p in e354.PROTOCOLS}
    vals = list(out["buffer_value"].values())
    out["buffer_gap"] = max(vals) - min(vals)
    return out


def _judge(r):
    return {row["id"]: row for row in e354.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    #: the paired cost is unresolved at this spread, which is the answer this unit measured
    assert j["T2"]["verdict"].startswith("NULL"), j["T2"]

    # T2: a cost that resolves positive, and one that resolves negative
    assert _judge(_reading(cost_override={"n": 5, "vals": [0.05] * 5, "mean": 0.05, "sem": 0.001,
                                          "sigma": 50.0}))["T2"]["verdict"].startswith("MET")
    assert _judge(_reading(cost_override={"n": 5, "vals": [-0.05] * 5, "mean": -0.05, "sem": 0.001,
                                          "sigma": 50.0}))["T2"]["verdict"].startswith("FALSIFIER")
    # T3: a cost as large as a tenth of the benchmark
    assert _judge(_reading(cost_override={"n": 5, "vals": [0.20] * 5, "mean": 0.20, "sem": 0.01,
                                          "sigma": 20.0}))["T3"]["verdict"].startswith("FALSIFIER")
    # T1: a world fingerprint that is not shared across the arms
    assert _judge(_reading(world_override="other"))["T1"]["verdict"].startswith("FALSIFIER")
    # T4: the buffer worth a tenth more in one protocol than the other
    assert _judge(_reading(replay_gap=0.20))["T4"]["verdict"].startswith("FALSIFIER")
    # fewer than four cells refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e354.judge({"rows": [
        _row(e354.TASK, e354.NAIVE, 0.3), _row(e354.TASK, e354.REPLAY, 0.1)]}))


def test_pairing_can_be_worse_than_not_pairing():
    #: the two protocols' forgetting is not positively correlated across seeds, so the paired sem need not be
    #: smaller than the unpaired one -- the arithmetic the finding leans on
    ts, cs = [0.5417, 0.3229, 0.3125, 0.1875, 0.3021], [0.3750, 0.3542, 0.2188, 0.4688, 0.3542]
    paired = statistics.stdev([c - t for c, t in zip(cs, ts)]) / math.sqrt(5)
    unpaired = math.sqrt((statistics.stdev(ts) / math.sqrt(5)) ** 2 + (statistics.stdev(cs) / math.sqrt(5)) ** 2)
    assert paired > unpaired, (paired, unpaired)
    assert statistics.correlation(ts, cs) < 0, statistics.correlation(ts, cs)


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e354_both_protocols_in_one_module.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e354.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the training landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: four cells per seed over one shared world, and the same seed's own world in both protocols
    assert len({(r["protocol"], r["arm"]) for r in d["rows"]}) == 4, d["rows"]
    assert len({r["world_read_sha1"] for r in d["rows"]}) == 1, d["rows"]
    assert len(d["rows"]) == 4 * len(d["seeds"]), (len(d["rows"]), d["seeds"])
    #: the shared head is the class-incremental cell's and nobody else's
    assert all((r["protocol"] == e354.CLASS) == r["shared_head"] for r in d["rows"]), d["rows"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
