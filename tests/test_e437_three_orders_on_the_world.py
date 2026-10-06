"""`e437` reads the card's world under three of the suite's six orders, so the tests pin both faces of the five claims,
the refusal when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e437_three_orders_on_the_world as e437

#: the shape of the ledger: three orders over one suite, fixed true values per roll
TASKS = ["t0", "t1", "t2"]
INDICES = {"as-built": [0, 1, 2], "reverse": [2, 1, 0], "1,0,2": [1, 0, 2]}
AS_BUILT = ("as-built", [0.2896, 0.2490, -0.0604], TASKS)
REVERSE = ("reverse", [0.3385, 0.2333, -0.0208], ["t2", "t1", "t0"])
ROTATE = ("1,0,2", [0.3100, 0.2000, -0.0400], ["t1", "t0", "t2"])


def _roll(order, gain, tasks, reps=20):
    return {"artifact": f"{order}.json", "tasks": list(tasks), "gain": list(gain),
            "per_task": dict(zip(tasks, gain)), "replicates": reps, "mean_gain": statistics.fmean(gain),
            "task_order": order,
            "shared": {"circuit": "mb+cx+al@n952", "readout": {"size": 32, "subset_sha1": "59926518137c"},
                       "tasks": list(tasks)},
            "draws": {"cue_sha1": "3985fc4e3252", "action_sha1": "f379863d1cf4",
                      "world_read_sha1": "3a7ba76b3619", "world_drive_sha1": "3d88340cf387",
                      "world_coupling_sha1": "5326f4a0edb4"},
            "config": {"circuit_size": 300, "iters": 500, "lr": 0.003, "lam": 1.0, "methods": "naive,replay"}}


def _doc(as_gain=None, reverse_gain=None, rotate_gain=None, reverse_tasks=None, rotate_tasks=None,
         same_differ=None, non_permutation=False, reps=20, drop=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": {}, "same": {}, "positions": {}, "by_task": {},
                "permutations": {}, "spans": {}}
    spec = {"as-built": (AS_BUILT[0], AS_BUILT[1] if as_gain is None else as_gain, AS_BUILT[2]),
            "reverse": (REVERSE[0], REVERSE[1] if reverse_gain is None else reverse_gain,
                        REVERSE[2] if reverse_tasks is None else reverse_tasks),
            "rotate": (ROTATE[0], ROTATE[1] if rotate_gain is None else rotate_gain,
                       ROTATE[2] if rotate_tasks is None else rotate_tasks)}
    rolls = {lbl: _roll(order, gain, tasks, reps=reps)
             for lbl, (order, gain, tasks) in spec.items() if lbl != drop}
    same = {}
    for lbl, roll in rolls.items():
        row = {"circuit": True, "readout": True}
        row.update({f"env_draw.{k}": True for k in e437.DRAW_FIELDS})
        row.update({f"config.{k}": True for k in e437.CONFIG_FIELDS})
        row["tasks"] = sorted(roll["tasks"]) == sorted(TASKS)
        same[lbl] = row
    if same_differ:
        for row in same.values():
            row[same_differ] = False
    permutations = {}
    for lbl, roll in rolls.items():
        idx = [0, 0, 2] if (non_permutation and lbl == "rotate") else INDICES[roll["task_order"]]
        permutations[lbl] = {"task_order": roll["task_order"], "indices": idx,
                             "permutation": sorted(idx) == list(range(e437.N_TASKS))}
    ref = rolls.get("as-built") or next(iter(rolls.values()))
    by_task = {t: {lbl: {"position": r["tasks"].index(t), "gain": r["per_task"][t]}
                   for lbl, r in rolls.items()} for t in ref["tasks"]}
    positions = {str(p): {lbl: r["gain"][p] for lbl, r in rolls.items()} for p in range(e437.N_TASKS)}
    firsts = [r["gain"][0] for r in rolls.values()]
    lasts = [r["gain"][-1] for r in rolls.values()]
    means = [r["mean_gain"] for r in rolls.values()]
    return {"ok": True, "reason": None, "rolls": rolls, "same": same, "positions": positions,
            "by_task": by_task, "permutations": permutations,
            "spans": {"rolls": len(rolls), "replicates": sorted({r["replicates"] for r in rolls.values()}),
                      "first_span": max(firsts) - min(firsts), "last_span": max(lasts) - min(lasts),
                      "mean_span": max(means) - min(means),
                      "first_over_last": {lbl: r["gain"][0] - r["gain"][-1] for lbl, r in rolls.items()},
                      "lasts": {lbl: r["gain"][-1] for lbl, r in rolls.items()},
                      "last_tasks": {lbl: r["tasks"][-1] for lbl, r in rolls.items()}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e437.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the three rolls carried, the position effect in all of them, and both positions the position's
    j = _judge()
    for cid in ("BM1", "BM2", "BM3", "BM4", "BM5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BM1: a shared field differing, an order that is not a permutation, thin replicates and a missing roll
    assert _judge(same_differ="config.iters")["BM1"].startswith("FALSIFIER")
    assert _judge(non_permutation=True)["BM1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BM1"].startswith("FALSIFIER")
    assert _judge(drop="rotate")["BM1"].startswith("FALSIFIER")

    # BM2: a roll whose last-taught task is ahead of its first-taught one
    assert _judge(rotate_gain=[0.05, 0.2000, 0.10])["BM2"].startswith("FALSIFIER")

    # BM3: a roll whose last-taught task is not cost, and one between the bars
    assert _judge(rotate_gain=[0.3100, 0.2000, 0.10])["BM3"].startswith("FALSIFIER")
    assert _judge(rotate_gain=[0.3100, 0.2000, 0.02])["BM3"].startswith("NULL")

    # BM4: a third order whose last-taught gain is far from the other two's, and one between the bars
    assert _judge(rotate_gain=[0.3100, 0.2000, -0.2000])["BM4"].startswith("FALSIFIER")
    assert _judge(rotate_gain=[0.3100, 0.2000, -0.0900])["BM4"].startswith("NULL")

    # BM5: a third order whose first-taught gain is far from the other two's, and one between the bars
    assert _judge(rotate_gain=[0.5600, 0.2000, -0.0400])["BM5"].startswith("FALSIFIER")
    assert _judge(rotate_gain=[0.4200, 0.2000, -0.0400])["BM5"].startswith("NULL")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e437.judge(_doc(ok=False)))


def test_the_rolls_and_the_thresholds_are_registered():
    #: the first roll is the card's world's, and the other two are the corpus's reversals of it
    assert {k: v.name for k, v in e437.ROLLS.items()} == {
        "as-built": "e380_earned_label_cue0_actionsource_20reps.json",
        "reverse": "e436_earned_label_cue0_reverse_20reps.json",
        "rotate": "e437_earned_label_cue0_order102_20reps.json"}
    assert e437.ORDER == "task_order" and e437.ARMS == ("naive", "replay") and e437.N_TASKS == 3
    assert e437.MIN_ROLLS == 3 and e437.MIN_REPS == 20
    assert (e437.POSITION, e437.LAST_BAR, e437.LAST_FIRES) == (0.0, 0.0, 0.05)
    assert (e437.LAST_SPAN, e437.LAST_SPAN_FIRES) == (0.05, 0.10)
    assert (e437.FIRST_SPAN, e437.FIRST_SPAN_FIRES) == (0.08, 0.15)
    assert "task_order" not in e437.CONFIG_FIELDS, "the order is the field that differs"
    assert "iters" in e437.CONFIG_FIELDS and "loop_world_coupled" in e437.CONFIG_FIELDS


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e437_the_three_orders_on_the_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e437.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e437.judge(d)}
    #: the three rolls being one configuration and the position effect in all of them are structural facts
    assert verdicts["BM1"].startswith("MET") and verdicts["BM2"].startswith("MET"), verdicts
    rolls = d["rolls"]
    assert sorted(rolls) == ["as-built", "reverse", "rotate"], sorted(rolls)
    assert sorted(p_["task_order"] for p_ in d["permutations"].values()) == ["1,0,2", "as-built", "reverse"]
    assert all(p_["permutation"] for p_ in d["permutations"].values()), d["permutations"]
    for lbl, roll in rolls.items():
        assert roll["replicates"] >= e437.MIN_REPS, lbl
        assert len(roll["gain"]) == e437.N_TASKS, lbl
        assert roll["gain"][0] > roll["gain"][-1], lbl
        assert sorted(roll["tasks"]) == sorted(rolls["as-built"]["tasks"]), lbl
    #: three orders put every task of the suite in at least two of the three positions
    assert len(d["by_task"]) == e437.N_TASKS, sorted(d["by_task"])
    for task, spots in d["by_task"].items():
        assert len({v["position"] for v in spots.values()}) >= 2, (task, spots)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
