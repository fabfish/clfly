"""`e443` reads the ledger on a second world, so the tests pin both faces of the five claims and the refusal when a roll
is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e443_the_ledger_on_a_second_world as e443

#: the shape of the two ledgers: fixed true values, so a mutation under test moves one of them
GAIN = [0.2896, 0.2490, -0.0604]
FORG = {"naive": 0.3750, "ewc-block": 0.3276, "replay": 0.0906}


def _doc(gain=None, same_differ=None, world_match=False, held_differ=None, reps=20, arms=e443.ARMS,
         ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "redrawn": {}, "gains": {}, "spans": {}}
    g = list(GAIN if gain is None else gain)
    margin = g[0] - g[-1]
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam")}
    same.update({f"env_draw.{k}": True for k in e443.DRAW_FIELDS})
    same.update({"circuit": True, "readout": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    world = {k: (not world_match) for k in e443.WORLD_FIELDS}
    held = {k: True for k in e443.DRAW_FIELDS if k not in e443.WORLD_FIELDS}
    if held_differ:
        held[held_differ] = False
        same[f"env_draw.{held_differ}"] = False
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e443.RUNS},
            "same": same, "redrawn": {"world": world, "held": held, "seed": {"new": 1, "card": None}},
            "gains": {"new.replay-naive": g, "new.ewc-naive": [0.0625, -0.0354, -0.1177],
                      "new.ewc-replay": [-0.2271, -0.2846, -0.0573]},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e443.RUNS},
                      "same_fields": len(same), "runs": len(e443.RUNS),
                      "margins": {"new": margin, "card": e443.CARD_MARGIN},
                      "card_margin": e443.CARD_MARGIN, "move": margin - e443.CARD_MARGIN,
                      "forgetting": {label: dict(FORG) for label in e443.RUNS}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e443.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the world redrawn and the ledger reading the same way on it
    j = _judge()
    for cid in ("BU1", "BU2", "BU3", "BU4", "BU5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BU1: an unexpected field differing, a world fingerprint that did not move, a held draw that did, thin
    # replicates and a short arm list
    assert _judge(same_differ="config.iters")["BU1"].startswith("FALSIFIER")
    assert _judge(world_match=True)["BU1"].startswith("FALSIFIER")
    assert _judge(held_differ="cue_sha1")["BU1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BU1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BU1"].startswith("FALSIFIER")

    # BU2: a buffer with no first-position gain, and one between the bars
    assert _judge(gain=[0.0000, 0.2490, -0.0604])["BU2"].startswith("FALSIFIER")
    assert _judge(gain=[0.0200, 0.2490, -0.0604])["BU2"].startswith("NULL")

    # BU3: a last position that is not cost, and one between the bars
    assert _judge(gain=[0.2896, 0.2490, 0.1000])["BU3"].startswith("FALSIFIER")
    assert _judge(gain=[0.2896, 0.2490, 0.0200])["BU3"].startswith("NULL")

    # BU4: a margin below the floor, and one between the bars
    assert _judge(gain=[-0.1000, 0.2490, -0.0500])["BU4"].startswith("FALSIFIER")
    assert _judge(gain=[0.0200, 0.2490, -0.0200])["BU4"].startswith("NULL")

    # BU5: a margin a long way from the card's, and one between the bars
    assert _judge(gain=[0.6000, 0.2000, -0.1000])["BU5"].startswith("FALSIFIER")
    assert _judge(gain=[0.5000, 0.2000, -0.0500])["BU5"].startswith("NULL")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e443.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the redraw is this unit's run, and the card's own three-arm roll is what it is read against
    assert e443.RUNS["new"].name == "e443_earned_label_worldseed1_20reps.json"
    assert e443.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e443.ARMS == ("naive", "ewc-block", "replay")
    assert (e443.BASELINE, e443.BUFFER, e443.ANCHOR) == ("naive", "replay", "ewc-block")
    assert e443.DRAW_FIELD == "loop_seed" and e443.DRAW_FIELD in e443.IGNORED
    assert set(e443.WORLD_FIELDS) <= set(e443.DRAW_FIELDS)
    assert e443.N_TASKS == 3 and e443.N_ARMS == 3 and e443.MIN_REPS == 20
    assert (e443.FIRST_BAR, e443.FIRST_FLOOR) == (0.05, 0.0)
    assert (e443.LAST_BAR, e443.LAST_FIRES) == (0.0, 0.05)
    assert (e443.MARGIN_BAR, e443.MARGIN_FLOOR) == (0.05, 0.02)
    assert e443.CARD_MARGIN == 0.3500, "the card's own margin BU5 is registered against"
    assert (e443.MARGIN_MOVES, e443.MARGIN_FIRES) == (0.15, 0.25)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e443_the_ledger_on_a_second_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e443.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on two rolls is structural
    assert sorted(d["runs"]) == ["card", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e443.MIN_REPS, arm
        assert len(got["final"]) == e443.N_TASKS, arm
    assert sorted(d["gains"]) == ["card.ewc-naive", "card.ewc-replay", "card.replay-naive",
                                  "new.ewc-naive", "new.ewc-replay", "new.replay-naive"], sorted(d["gains"])
    assert sorted(d["redrawn"]["world"]) == sorted(e443.WORLD_FIELDS), sorted(d["redrawn"]["world"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
