"""`e457` writes the card's eleventh revision, so the tests pin both faces of the five claims and the refusal when an
artifact it is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e457_the_game_card_revision_eleven as e457

#: the four rolls, by read-out and anchor: fixed true values, so a mutation moves one of them
CELLS = {
    "earned_label/ewc-block": (-0.0302, 1.77, -0.1177, 3.71),
    "earned_label/ewc-block-rand": (-0.0365, 2.16, -0.1135, 4.49),
    "neurons/ewc-block": (0.0187, 1.03, -0.0115, 0.78),
    "neurons/ewc-block-rand": (0.0104, 0.59, -0.0323, 2.77),
}
BASIS_ACC = {"earned_label": (0.0063, 0.36), "neurons": (0.0083, 0.49)}
BASIS_FRG = {"earned_label": (-0.0245, 1.24), "neurons": (-0.0078, 0.32)}
#: the fields the revision-10 card carries, which this unit may not rewrite
OLD = {"name": "the closed-loop earned-label game", "method": {"rolls": 10}, "width": {"card_width": 8}}


def _rolls(cells=None) -> dict:
    spec = CELLS if cells is None else cells
    out = {}
    for label, (st, st_sig, pr, pr_sig) in spec.items():
        out[label] = {"artifact": label.replace("/", "_") + ".json", "readout": label.split("/")[0],
                      "anchor": label.split("/")[1], "replicates": 20,
                      "standing": {"n": 20, "mean": st, "sd": 0.05, "se": 0.01, "sigma": st_sig},
                      "price": {"n": 20, "mean": pr, "sd": 0.05, "se": 0.01, "sigma": pr_sig},
                      "readout_width": 8 if label.startswith("earned_label") else 32,
                      "from_world": label.startswith("earned_label")}
    return out


def _clause(rolls: dict, basis_acc=None, basis_frg=None) -> dict:
    ba = BASIS_ACC if basis_acc is None else basis_acc
    bf = BASIS_FRG if basis_frg is None else basis_frg
    return {"artifact": [v["artifact"] for v in rolls.values()],
            "readouts": {"earned_label": {"from_world": True, "width": 8},
                         "neurons": {"from_world": False, "width": 32}},
            "buffer": e457.BUFFER,
            "anchor_over_naive": {l: v["standing"]["mean"] for l, v in rolls.items()},
            "anchor_over_naive_sigma": {l: v["standing"]["sigma"] for l, v in rolls.items()},
            "newest_task": {l: v["price"]["mean"] for l, v in rolls.items()},
            "newest_task_sigma": {l: v["price"]["sigma"] for l, v in rolls.items()},
            "basis_accuracy": {r: ba[r][0] for r in ba},
            "basis_accuracy_sigma": {r: ba[r][1] for r in ba},
            "basis_forgetting": {r: bf[r][0] for r in bf},
            "basis_forgetting_sigma": {r: bf[r][1] for r in bf}}


def _basis(acc=None, frg=None) -> dict:
    ba = BASIS_ACC if acc is None else acc
    bf = BASIS_FRG if frg is None else frg
    return {r: {"accuracy": {"mean": ba[r][0], "sigma": ba[r][1]},
                "forgetting": {"mean": bf[r][0], "sigma": bf[r][1]}} for r in e457.READOUTS}


def _doc(cells=None, clause=None, basis=None, same_differ=None, revision=e457.REVISION, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": {}, "revision10": {}, "readout": {}, "rolls": {}, "basis": {}}
    rr = _rolls(cells)
    c = _clause(rr) if clause is None else clause
    card = {k: (dict(v) if isinstance(v, dict) else v) for k, v in OLD.items()}
    card["revision"] = revision
    card["readout"] = c
    if same_differ:
        card[same_differ] = "rewritten"
    return {"ok": True, "reason": None, "card": card, "revision10": dict(OLD), "readout": c, "rolls": rr,
            "basis": _basis() if basis is None else basis}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e457.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the tenth revision carried and the readout clause reading as the four rolls do
    j = _judge()
    for cid in ("DD1", "DD2", "DD3", "DD4", "DD5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DD1: a field rewritten and a revision that did not move
    assert _judge(same_differ="method")["DD1"].startswith("FALSIFIER")
    assert _judge(revision=10)["DD1"].startswith("FALSIFIER")

    # DD2: a standing, a price and a basis contrast the clause gets wrong
    rr = _rolls()
    c = _clause(rr)
    c["anchor_over_naive"] = dict(c["anchor_over_naive"])
    c["anchor_over_naive"]["neurons/ewc-block"] = 0.4000
    assert _judge(clause=c)["DD2"].startswith("FALSIFIER")
    c = _clause(rr)
    c["newest_task"] = dict(c["newest_task"])
    c["newest_task"]["earned_label/ewc-block"] = -0.9000
    assert _judge(clause=c)["DD2"].startswith("FALSIFIER")
    c = _clause(rr)
    c["basis_accuracy"] = dict(c["basis_accuracy"])
    c["basis_accuracy"]["neurons"] = 0.9000
    assert _judge(clause=c)["DD2"].startswith("FALSIFIER")

    # DD3: two standings that disagree under one read-out, and one between the bars
    odd = dict(CELLS)
    odd["neurons/ewc-block-rand"] = (0.1500, 1.50, -0.0323, 2.77)
    assert _judge(cells=odd)["DD3"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons/ewc-block-rand"] = (0.0700, 1.50, -0.0323, 2.77)
    assert _judge(cells=odd)["DD3"].startswith("NULL")

    # DD4: a basis contrast at the falsifier under one read-out, and one between the bars
    c = _clause(_rolls())
    c["basis_accuracy"] = dict(c["basis_accuracy"])
    c["basis_accuracy"]["neurons"] = 0.1500
    assert _judge(clause=c)["DD4"].startswith("FALSIFIER")
    c = _clause(_rolls())
    c["basis_accuracy"] = dict(c["basis_accuracy"])
    c["basis_accuracy"]["neurons"] = 0.0700
    assert _judge(clause=c)["DD4"].startswith("NULL")

    # DD5: a label gap past the falsifier, a neuron gap under the floor, and one between the bars
    odd = dict(CELLS)
    odd["earned_label/ewc-block-rand"] = (-0.0365, 2.16, 0.0500, 1.00)
    assert _judge(cells=odd)["DD5"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons/ewc-block-rand"] = (0.0104, 0.59, -0.0150, 1.00)
    assert _judge(cells=odd)["DD5"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons/ewc-block-rand"] = (0.0104, 0.59, -0.0250, 2.00)
    assert _judge(cells=odd)["DD5"].startswith("NULL")

    #: an artifact the revision is read from absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e457.judge(_doc(ok=False)))


def test_the_card_and_the_rolls_are_registered():
    #: the revision-10 card is what is added to, and the four rolls are its world's two read-outs
    assert e457.CARD10.name == "e454_the_game_card_revision_ten.json"
    assert {k: v.name for k, v in e457.ROLLS.items()} == {
        "earned_label/ewc-block": "e438_earned_label_three_arms_20reps.json",
        "earned_label/ewc-block-rand": "e439_earned_label_rand_20reps.json",
        "neurons/ewc-block": "e455_earned_label_neurons_20reps.json",
        "neurons/ewc-block-rand": "e456_earned_label_rand_neurons_20reps.json"}
    assert e457.READOUTS == {"earned_label": {"from_world": True}, "neurons": {"from_world": False}}
    assert e457.REVISION == 11 and e457.NEW == ("revision", "readout")
    assert (e457.BASELINE, e457.BUFFER) == ("naive", "replay")
    assert e457.N_TASKS == 3 and e457.MIN_REPS == 20 and e457.TOL == 0.002
    assert (e457.ALIKE, e457.ALIKE_FIRES) == (0.05, 0.10)
    assert (e457.LABEL_GAP, e457.NEURON_GAP, e457.NEURON_GAP_FLOOR) == (0.05, 0.02, 0.01)


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e457_the_game_card_revision_eleven.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e457.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the card at revision 11, its tenth revision carried, four rolls over two read-outs
    assert d["card"]["revision"] == e457.REVISION, d["card"]["revision"]
    assert len(d["revision10"]) >= 20, len(d["revision10"])
    assert sorted(d["rolls"]) == sorted(e457.ROLLS), sorted(d["rolls"])
    assert len(d["readout"]["artifact"]) == len(d["rolls"]), d["readout"]["artifact"]
    assert sorted(d["readout"]["basis_accuracy"]) == ["earned_label", "neurons"], d["readout"]["basis_accuracy"]
    for label, got in d["rolls"].items():
        assert got["replicates"] >= e457.MIN_REPS, label
        assert got["anchor"] == label.split("/")[1], label
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
