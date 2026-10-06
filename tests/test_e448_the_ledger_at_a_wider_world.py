"""`e448` reads the ledger at a wider world, so the tests pin both faces of the five claims and the refusal when a roll
is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e448_the_ledger_at_a_wider_world as e448

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
BUFFER_GAIN = [0.3100, 0.2500, -0.0500]
ANCHOR_GAIN = [0.0700, -0.0200, -0.1000]
ANCHOR_SIGMA = -3.50
WIDE = {"width": 16, "readouts": [16, 16, 16]}
BASE = {"width": 8, "readouts": [8, 8, 8]}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(buffer_gain=None, anchor_gain=None, anchor_sigma=ANCHOR_SIGMA, wide=None, base=None, same_differ=None,
         task_names=True, reps=20, arms=e448.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "widths": {}, "contrasts": {}, "spans": {}}
    bg = list(BUFFER_GAIN if buffer_gain is None else buffer_gain)
    ag = list(ANCHOR_GAIN if anchor_gain is None else anchor_gain)
    w = dict(wide or WIDE)
    w["own"] = all(r == w["width"] for r in w["readouts"])
    b = dict(base or BASE)
    b["own"] = all(r == b["width"] for r in b["readouts"])
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "readout_size")}
    same.update({"circuit": True, "task_names": task_names, "task_count": True})
    if same_differ:
        same[same_differ] = False
    contrasts = {"new": {"buffer_gain": bg, "anchor_gain": ag,
                         "buffer_diagonal": _paired(0.1600, 11.5),
                         "anchor_last": _paired(ag[-1], anchor_sigma),
                         "anchor_diagonal": _paired(0.0100, 0.5),
                         "forgetting": {"naive": 0.39, "ewc-block": 0.34, "replay": 0.12}},
                 "card": {"buffer_gain": [0.2896, 0.2490, -0.0604], "anchor_gain": [0.0625, -0.0354, -0.1177],
                          "buffer_diagonal": _paired(0.1594, 11.97),
                          "anchor_last": _paired(-0.1177, -3.71),
                          "anchor_diagonal": _paired(-0.0302, -1.77),
                          "forgetting": {"naive": 0.375, "ewc-block": 0.3276, "replay": 0.0906}}}
    margin_new = bg[0] - bg[-1]
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e448.RUNS},
            "same": same,
            "widths": {"new": w, "card": b,
                       "drawn": {k: (w["width"] != b["width"]) for k in e448.DRAW_FIELDS}},
            "contrasts": contrasts,
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e448.RUNS},
                      "same_fields": len(same), "widths": {"new": w["width"], "card": b["width"]},
                      "margin": {"new": margin_new, "card": e448.CARD_MARGIN,
                                 "move": margin_new - e448.CARD_MARGIN},
                      "last": {"buffer": bg[-1], "anchor": ag[-1], "anchor_sigma": anchor_sigma},
                      "card_last": {"buffer": -0.0604, "anchor": -0.1177}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e448.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the world widened and the ledger reading the same way at twice the columns
    j = _judge()
    for cid in ("BZ1", "BZ2", "BZ3", "BZ4", "BZ5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BZ1: a field differing, a width that did not move, a read-out that is not the world's own, task names
    # differing, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["BZ1"].startswith("FALSIFIER")
    assert _judge(wide=BASE)["BZ1"].startswith("FALSIFIER")
    assert _judge(wide={"width": 16, "readouts": [16, 16, 8]})["BZ1"].startswith("FALSIFIER")
    assert _judge(task_names=False)["BZ1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BZ1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BZ1"].startswith("FALSIFIER")

    # BZ2: a buffer with no first-position gain at the wider world, and one between the bars
    assert _judge(buffer_gain=[0.0000, 0.2500, -0.0500])["BZ2"].startswith("FALSIFIER")
    assert _judge(buffer_gain=[0.0200, 0.2500, -0.0500])["BZ2"].startswith("NULL")

    # BZ3: a last position that is not cost, and one between the bars
    assert _judge(buffer_gain=[0.3100, 0.2500, 0.1000])["BZ3"].startswith("FALSIFIER")
    assert _judge(buffer_gain=[0.3100, 0.2500, 0.0200])["BZ3"].startswith("NULL")

    # BZ4: a margin a long way from the card's, and one between the bars
    assert _judge(buffer_gain=[0.6000, 0.2000, -0.1000])["BZ4"].startswith("FALSIFIER")
    assert _judge(buffer_gain=[0.5000, 0.2000, -0.0500])["BZ4"].startswith("NULL")

    # BZ5: an anchor that is ahead on the newest task, and one whose price does not resolve
    assert _judge(anchor_gain=[0.0700, -0.0200, 0.0500], anchor_sigma=1.10)["BZ5"].startswith("FALSIFIER")
    assert _judge(anchor_gain=[0.0700, -0.0200, -0.0200], anchor_sigma=-1.20)["BZ5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e448.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the wider world is this unit's run, and the card's own roll is what it is read against
    assert e448.RUNS["new"].name == "e448_earned_label_worlddims16_20reps.json"
    assert e448.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e448.ARMS == ("naive", "ewc-block", "replay")
    assert (e448.BASELINE, e448.BUFFER, e448.ANCHOR) == ("naive", "replay", "ewc-block")
    assert e448.WIDTH_FIELD == "loop_world_dims" and e448.WIDTH_FIELD in e448.IGNORED
    assert (e448.BASE_WIDTH, e448.WIDE_WIDTH) == (8, 16)
    assert len(e448.DRAW_FIELDS) == 6, "the six fingerprints `e443` corrected this line's field list to"
    assert e448.N_TASKS == 3 and e448.N_ARMS == 3 and e448.MIN_REPS == 20
    assert (e448.FIRST_BAR, e448.FIRST_FLOOR) == (0.05, 0.0)
    assert (e448.LAST_BAR, e448.LAST_FIRES) == (0.0, 0.05)
    assert e448.CARD_MARGIN == 0.3500, "the card's own margin BZ4 is registered against"
    assert (e448.MARGIN_MOVES, e448.MARGIN_FIRES) == (0.15, 0.25)
    assert e448.SIGMA == 2.0


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e448_the_ledger_at_a_wider_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e448.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates at sixteen columns is structural
    assert sorted(d["runs"]) == ["card", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e448.MIN_REPS, arm
        assert len(got["final"]) == e448.N_TASKS, arm
    assert d["widths"]["new"]["width"] == e448.WIDE_WIDTH, d["widths"]["new"]
    assert d["widths"]["card"]["width"] == e448.BASE_WIDTH, d["widths"]["card"]
    assert d["widths"]["new"]["own"] and d["widths"]["card"]["own"], d["widths"]
    assert sorted(d["contrasts"]) == ["card", "new"], sorted(d["contrasts"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
