"""`e449` reads the ledger at a narrower world, so the tests pin both faces of the five claims and the refusal when a
roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e449_the_ledger_at_a_narrower_world as e449

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
BUFFER_GAIN = [0.3100, 0.2500, -0.0700]
ANCHOR_GAIN = [0.0800, -0.0300, -0.1500]
ANCHOR_SIGMA = -4.20
ANCHOR_STANDING_SIGMA = 1.20
NAIVE_DIAGONAL = 0.5191
NARROW = {"width": 4, "readouts": [4, 4, 4]}
BASE = {"width": 8, "readouts": [8, 8, 8]}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(buffer_gain=None, anchor_gain=None, anchor_sigma=ANCHOR_SIGMA, standing_sigma=ANCHOR_STANDING_SIGMA,
         naive_diagonal=NAIVE_DIAGONAL, narrow=None, base=None, same_differ=None, task_names=True, reps=20,
         arms=e449.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "widths": {}, "contrasts": {}, "spans": {}}
    bg = list(BUFFER_GAIN if buffer_gain is None else buffer_gain)
    ag = list(ANCHOR_GAIN if anchor_gain is None else anchor_gain)
    w = dict(narrow or NARROW)
    w["own"] = all(r == w["width"] for r in w["readouts"])
    b = dict(base or BASE)
    b["own"] = all(r == b["width"] for r in b["readouts"])
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "readout_size")}
    same.update({"circuit": True, "task_names": task_names, "task_count": True})
    if same_differ:
        same[same_differ] = False
    contrasts = {"new": {"buffer_gain": bg, "anchor_gain": ag,
                         "buffer_diagonal": _paired(0.1600, 11.0),
                         "anchor_last": _paired(ag[-1], anchor_sigma),
                         "anchor_diagonal": _paired(0.0100, standing_sigma),
                         "naive_diagonal": naive_diagonal,
                         "forgetting": {"naive": 0.36, "ewc-block": 0.31, "replay": 0.11}},
                 "card": {"buffer_gain": [0.2896, 0.2490, -0.0604], "anchor_gain": [0.0625, -0.0354, -0.1177],
                          "buffer_diagonal": _paired(0.1594, 11.97),
                          "anchor_last": _paired(-0.1177, -3.71),
                          "anchor_diagonal": _paired(-0.0302, -1.77),
                          "naive_diagonal": 0.5191,
                          "forgetting": {"naive": 0.375, "ewc-block": 0.3276, "replay": 0.0906}}}
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e449.RUNS},
            "same": same,
            "widths": {"new": w, "card": b,
                       "world_moved": {k: True for k in e449.WORLD_FIELDS},
                       "held": {k: True for k in e449.DRAW_FIELDS if k not in e449.WORLD_FIELDS}},
            "contrasts": contrasts,
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e449.RUNS},
                      "same_fields": len(same), "widths": {"new": w["width"], "card": b["width"]},
                      "naive_diagonal": {"new": naive_diagonal, "card": 0.5191,
                                         "over_chance": naive_diagonal - e449.CHANCE},
                      "margin": {"new": bg[0] - bg[-1], "card": 0.3500},
                      "last": {"buffer": bg[-1], "anchor": ag[-1], "anchor_sigma": anchor_sigma,
                               "card_anchor": -0.1177}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e449.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the world narrowed, still learnable, and the anchor's price larger than at eight columns
    j = _judge()
    for cid in ("CA1", "CA2", "CA3", "CA4", "CA5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # CA1: a field differing, a width that did not move, a read-out that is not the world's own, task names
    # differing, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["CA1"].startswith("FALSIFIER")
    assert _judge(narrow=BASE)["CA1"].startswith("FALSIFIER")
    assert _judge(narrow={"width": 4, "readouts": [4, 4, 8]})["CA1"].startswith("FALSIFIER")
    assert _judge(task_names=False)["CA1"].startswith("FALSIFIER")
    assert _judge(reps=19)["CA1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["CA1"].startswith("FALSIFIER")

    # CA2: a narrower world the baseline cannot learn, and one between the bars
    assert _judge(naive_diagonal=0.3000)["CA2"].startswith("FALSIFIER")
    assert _judge(naive_diagonal=0.3200)["CA2"].startswith("NULL")

    # CA3: a buffer with no first-position gain at the narrower world, and one between the bars
    assert _judge(buffer_gain=[0.0000, 0.2500, -0.0700])["CA3"].startswith("FALSIFIER")
    assert _judge(buffer_gain=[0.0200, 0.2500, -0.0700])["CA3"].startswith("NULL")

    # CA4: a price smaller than the floor, one between the bars, and one of the wrong sign
    assert _judge(anchor_gain=[0.0800, -0.0300, -0.0400], anchor_sigma=-1.00)["CA4"].startswith("FALSIFIER")
    assert _judge(anchor_gain=[0.0800, -0.0300, -0.0900], anchor_sigma=-2.00)["CA4"].startswith("NULL")
    assert _judge(anchor_gain=[0.0800, -0.0300, 0.2000], anchor_sigma=3.00)["CA4"].startswith("FALSIFIER")

    # CA5: a standing that resolves at the narrower world
    assert _judge(standing_sigma=2.50)["CA5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e449.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the narrower world is this unit's run, and the card's own roll is what it is read against
    assert e449.RUNS["new"].name == "e449_earned_label_worlddims4_20reps.json"
    assert e449.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e449.ARMS == ("naive", "ewc-block", "replay")
    assert (e449.BASELINE, e449.BUFFER, e449.ANCHOR) == ("naive", "replay", "ewc-block")
    assert e449.WIDTH_FIELD == "loop_world_dims" and e449.WIDTH_FIELD in e449.IGNORED
    assert (e449.BASE_WIDTH, e449.NARROW_WIDTH) == (8, 4)
    assert set(e449.WORLD_FIELDS) <= set(e449.DRAW_FIELDS) and len(e449.DRAW_FIELDS) == 6
    assert (e449.CHANCE, e449.LEARN_BAR, e449.LEARN_FLOOR) == (0.25, 0.10, 0.05)
    assert (e449.FIRST_BAR, e449.FIRST_FLOOR) == (0.05, 0.0)
    assert (e449.CARD_PRICE, e449.PRICE_FLOOR) == (0.1177, 0.06), "the card's own cost CA4 is registered against"
    assert e449.SIGMA == 2.0
    assert e449.N_TASKS == 3 and e449.N_ARMS == 3 and e449.MIN_REPS == 20


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e449_the_ledger_at_a_narrower_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e449.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates at four columns is structural
    assert sorted(d["runs"]) == ["card", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e449.MIN_REPS, arm
        assert len(got["final"]) == e449.N_TASKS, arm
    assert d["widths"]["new"]["width"] == e449.NARROW_WIDTH, d["widths"]["new"]
    assert d["widths"]["card"]["width"] == e449.BASE_WIDTH, d["widths"]["card"]
    assert d["widths"]["new"]["own"] and d["widths"]["card"]["own"], d["widths"]
    assert sorted(d["contrasts"]) == ["card", "new"], sorted(d["contrasts"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
