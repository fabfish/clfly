"""`e436` reads the card's world rolled both ways, so the tests pin both faces of the five claims, the refusal when a
roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e436_the_order_the_world_is_taught_in as e436

#: the shape of the pair: the as-built order's task list and gains, and the reversed roll's
AS_BUILT_TASKS = ["t0", "t1", "t2"]
AS_BUILT_GAIN = [0.2896, 0.2490, -0.0604]
REVERSE_TASKS = ["t2", "t1", "t0"]
REVERSE_GAIN = [0.2813, 0.2219, -0.0427]


def _roll(label, tasks, gain, reps=20, task_order="as-built", arm_missing=False):
    gains = list(gain)
    doc = {"artifact": f"{label}.json", "tasks": list(tasks), "gain": gains,
           "per_task": dict(zip(tasks, gains)), "replicates": reps, "task_order": task_order,
           "mean_gain": statistics.fmean(gains),
           "shared": {"circuit": "mb+cx+al@n952", "readout": {"size": 32, "subset_sha1": "59926518137c"},
                      "tasks": list(tasks)},
           "draws": {"cue_sha1": "3985fc4e3252", "action_sha1": "f379863d1cf4", "world_read_sha1": "3a7ba76b3619",
                     "world_drive_sha1": "3d88340cf387", "world_coupling_sha1": "5326f4a0edb4"},
           "config": {"circuit_size": 300, "iters": 500, "lr": 0.003, "lam": 1.0, "methods": "naive,replay"}}
    if arm_missing:
        doc["gain"] = None
    return doc


def _doc(as_gain=None, reverse_gain=None, reverse_tasks=None, same=True, reps=20, differ=None, ok=True,
         reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": {}, "same": {}, "same_tasks": False, "orders": {},
                "contrasts": {}, "spans": {}}
    a = _roll("as_built", AS_BUILT_TASKS, AS_BUILT_GAIN if as_gain is None else as_gain, reps=reps,
              task_order="as-built")
    b = _roll("reverse", REVERSE_TASKS if reverse_tasks is None else reverse_tasks,
              REVERSE_GAIN if reverse_gain is None else reverse_gain, reps=reps, task_order="reverse")
    same_map = {k: True for k in e436.SHARED}
    same_map.update({f"env_draw.{k}": True for k in e436.DRAW_FIELDS})
    same_map.update({f"config.{k}": True for k in e436.CONFIG_FIELDS})
    if differ:
        same_map[differ] = False
    contrasts = {}
    for label, first, last in (("as_built_first", a, b), ("reverse_first", b, a)):
        task = first["tasks"][0]
        contrasts[label] = {"task": task, "at_first": first["per_task"].get(task),
                            "at_last": last["per_task"].get(task)}
        contrasts[label]["difference"] = contrasts[label]["at_first"] - contrasts[label]["at_last"]
    return {"ok": True, "reason": None, "rolls": {"as_built": a, "reverse": b}, "same": same_map,
            "same_tasks": same, "orders": {"as_built": "as-built", "reverse": "reverse"},
            "contrasts": contrasts,
            "spans": {"replicates": sorted({a["replicates"], b["replicates"]}),
                      "as_built_mean": a["mean_gain"], "reverse_mean": b["mean_gain"],
                      "rise": b["mean_gain"] - a["mean_gain"],
                      "as_built_first_over_last": a["gain"][0] - a["gain"][-1],
                      "reverse_first_over_last": b["gain"][0] - b["gain"][-1],
                      "reverse_last": b["gain"][-1],
                      "smallest_contrast": min(c["difference"] for c in contrasts.values())}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e436.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the pair carried, the position effect in both rolls, the reversal costing the buffer
    j = _judge()
    for cid in ("BL1", "BL2", "BL3", "BL4", "BL5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BL1: a shared field differing, a task set that is not the reverse, and too few replicates
    assert _judge(differ="config.iters")["BL1"].startswith("FALSIFIER")
    assert _judge(same=False)["BL1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BL1"].startswith("FALSIFIER")

    # BL2: a roll whose last-taught task is ahead of its first-taught one
    assert _judge(reverse_gain=[0.05, 0.2219, 0.10])["BL2"].startswith("FALSIFIER")

    # BL3: a reversed roll whose last-taught task is not cost, and one between the bars
    assert _judge(reverse_gain=[0.2813, 0.2219, 0.10])["BL3"].startswith("FALSIFIER")
    assert _judge(reverse_gain=[0.2813, 0.2219, 0.02])["BL3"].startswith("NULL")

    # BL4: a reversed roll whose mean gain is above the as-built one's
    assert _judge(reverse_gain=[0.40, 0.30, -0.02])["BL4"].startswith("FALSIFIER")

    # BL5: a task that does not move with its position, and one whose margin is between the bars
    assert _judge(as_gain=[-0.04, 0.2490, -0.0604])["BL5"].startswith("FALSIFIER")
    assert _judge(as_gain=[-0.01, 0.2490, -0.0604])["BL5"].startswith("NULL")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e436.judge(_doc(ok=False)))


def test_the_rolls_and_the_thresholds_are_registered():
    #: the as-built roll is the card's world's, and the reversed one is this unit's
    assert e436.AS_BUILT.name == "e380_earned_label_cue0_actionsource_20reps.json"
    assert e436.REVERSE.name == "e436_earned_label_cue0_reverse_20reps.json"
    assert e436.ORDER == "task_order" and e436.ARMS == ("naive", "replay") and e436.N_TASKS == 3
    assert e436.MIN_REPS == 20
    assert (e436.POSITION, e436.LAST_BAR, e436.LAST_FIRES) == (0.0, 0.0, 0.05)
    assert (e436.CONTRAST, e436.CONTRAST_FIRES) == (0.05, 0.02)
    assert "task_order" not in e436.CONFIG_FIELDS, "the order is the field that differs"
    assert "iters" in e436.CONFIG_FIELDS and "loop_world_coupled" in e436.CONFIG_FIELDS


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e436_the_order_the_world_is_taught_in.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e436.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e436.judge(d)}
    #: the pair being carried and the position effect in both rolls are structural facts
    assert verdicts["BL1"].startswith("MET") and verdicts["BL2"].startswith("MET"), verdicts
    rolls = d["rolls"]
    assert sorted(rolls) == ["as_built", "reverse"], sorted(rolls)
    assert rolls["as_built"]["task_order"] == "as-built" and rolls["reverse"]["task_order"] == "reverse", d["orders"]
    assert list(reversed(rolls["as_built"]["tasks"])) == rolls["reverse"]["tasks"], rolls
    for lbl, roll in rolls.items():
        assert roll["replicates"] >= e436.MIN_REPS, lbl
        assert len(roll["gain"]) == e436.N_TASKS, lbl
        assert roll["gain"][0] > roll["gain"][-1], lbl
    assert d["same_tasks"], "the reversed suite is the as-built one reversed"
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
