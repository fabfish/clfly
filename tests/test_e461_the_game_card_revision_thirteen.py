"""`e461` writes the card's thirteenth revision, so the tests pin both faces of the five claims and the refusal when an
artifact it is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e461_the_game_card_revision_thirteen as e461

#: the six cells of the card's own world's head table: fixed true values, so a mutation moves one of them
CELLS = {
    "world_eight/ewc-block": (8, -0.0302, 1.77, -0.1177, 3.71),
    "world_eight/ewc-block-rand": (8, -0.0365, 2.16, -0.1135, 4.49),
    "neurons_thirty_two/ewc-block": (32, 0.0187, 1.03, -0.0115, 0.78),
    "neurons_thirty_two/ewc-block-rand": (32, 0.0104, 0.59, -0.0323, 2.77),
    "neurons_eight/ewc-block": (8, 0.0017, 0.12, -0.0615, 4.48),
    "neurons_eight/ewc-block-rand": (8, -0.0271, 1.80, -0.0594, 4.18),
}
BASIS = {"world_eight": (0.0063, 0.36), "neurons_thirty_two": (0.0083, 0.49), "neurons_eight": (0.0288, 1.70)}
#: the fields the revision-12 card carries, which this unit may not rewrite
OLD = {"name": "the closed-loop earned-label game", "head": {"buffer": "replay"}, "method": {"rolls": 10}}


def _rolls(cells=None) -> dict:
    spec = CELLS if cells is None else cells
    out = {}
    for label, (width, st, st_sig, pr, pr_sig) in spec.items():
        head, anchor = label.split("/")
        out[label] = {"artifact": label.replace("/", "_") + ".json", "head": head, "anchor": anchor,
                      "replicates": 20, "width": width,
                      "standing": {"n": 20, "mean": st, "sd": 0.05, "se": 0.01, "sigma": st_sig},
                      "price": {"n": 20, "mean": pr, "sd": 0.05, "se": 0.01, "sigma": pr_sig},
                      "from_world": head == "world_eight"}
    return out


def _clause(rolls: dict, basis=None) -> dict:
    ba = BASIS if basis is None else basis
    return {"artifact": [v["artifact"] for v in rolls.values()],
            "heads": {h: dict(v) for h, v in e461.HEADS.items()},
            "buffer": e461.BUFFER, "anchors": list(e461.ANCHORS),
            "anchor_over_naive": {l: v["standing"]["mean"] for l, v in rolls.items()},
            "anchor_over_naive_sigma": {l: v["standing"]["sigma"] for l, v in rolls.items()},
            "newest_task": {l: v["price"]["mean"] for l, v in rolls.items()},
            "newest_task_sigma": {l: v["price"]["sigma"] for l, v in rolls.items()},
            "basis_accuracy": {h: ba[h][0] for h in ba},
            "basis_accuracy_sigma": {h: ba[h][1] for h in ba}}


def _basis(acc=None) -> dict:
    ba = BASIS if acc is None else acc
    return {h: {"accuracy": {"mean": ba[h][0], "sigma": ba[h][1]}} for h in e461.HEADS}


def _doc(cells=None, clause=None, basis=None, same_differ=None, revision=e461.REVISION, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": {}, "revision12": {}, "pair": {}, "rolls": {}, "basis": {}}
    rr = _rolls(cells)
    c = _clause(rr) if clause is None else clause
    card = {k: (dict(v) if isinstance(v, dict) else v) for k, v in OLD.items()}
    card["revision"] = revision
    card["pair"] = c
    if same_differ:
        card[same_differ] = "rewritten"
    return {"ok": True, "reason": None, "card": card, "revision12": dict(OLD), "pair": c, "rolls": rr,
            "basis": _basis() if basis is None else basis}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e461.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the twelfth revision carried and the pair clause reading as the six rolls do
    j = _judge()
    for cid in ("DH1", "DH2", "DH3", "DH4", "DH5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DH1: a field rewritten and a revision that did not move
    assert _judge(same_differ="head")["DH1"].startswith("FALSIFIER")
    assert _judge(revision=12)["DH1"].startswith("FALSIFIER")

    # DH2: a price, a standing and a basis contrast the clause gets wrong
    c = _clause(_rolls())
    c["newest_task"] = dict(c["newest_task"])
    c["newest_task"]["neurons_eight/ewc-block"] = -0.9000
    assert _judge(clause=c)["DH2"].startswith("FALSIFIER")
    c = _clause(_rolls())
    c["anchor_over_naive"] = dict(c["anchor_over_naive"])
    c["anchor_over_naive"]["world_eight/ewc-block"] = 0.4000
    assert _judge(clause=c)["DH2"].startswith("FALSIFIER")
    c = _clause(_rolls())
    c["basis_accuracy"] = dict(c["basis_accuracy"])
    c["basis_accuracy"]["neurons_eight"] = 0.9000
    assert _judge(clause=c)["DH2"].startswith("FALSIFIER")

    # DH3: an eight-column price gap past the falsifier, and a wide gap under the floor
    odd = dict(CELLS)
    odd["neurons_eight/ewc-block-rand"] = (8, -0.0271, 1.80, -0.2000, 4.00)
    assert _judge(cells=odd)["DH3"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons_thirty_two/ewc-block-rand"] = (32, 0.0104, 0.59, -0.0150, 1.00)
    assert _judge(cells=odd)["DH3"].startswith("FALSIFIER")

    # DH4: a narrow standing gap under the floor, and a wide one past the falsifier
    odd = dict(CELLS)
    odd["neurons_eight/ewc-block-rand"] = (8, 0.0017, 0.12, -0.0594, 4.18)
    assert _judge(cells=odd)["DH4"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons_thirty_two/ewc-block-rand"] = (32, 0.1500, 1.50, -0.0323, 2.77)
    assert _judge(cells=odd)["DH4"].startswith("FALSIFIER")

    # DH5: a basis contrast at the falsifier, and one between the bars
    c = _clause(_rolls())
    c["basis_accuracy"] = dict(c["basis_accuracy"])
    c["basis_accuracy"]["neurons_eight"] = 0.1500
    assert _judge(clause=c)["DH5"].startswith("FALSIFIER")
    c = _clause(_rolls())
    c["basis_accuracy"] = dict(c["basis_accuracy"])
    c["basis_accuracy"]["neurons_eight"] = 0.0700
    assert _judge(clause=c)["DH5"].startswith("NULL")

    #: an artifact the revision is read from absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e461.judge(_doc(ok=False)))


def test_the_card_and_the_cells_are_registered():
    #: the revision-12 card is what is added to, and the six cells are its world's three heads by two anchors
    assert e461.CARD12.name == "e459_the_game_card_revision_twelve.json"
    assert len(e461.ROLLS) == 6 and len(e461.HEADS) == 3
    assert {k: v.name for k, v in e461.ROLLS.items()}["neurons_eight/ewc-block-rand"] == \
        "e460_earned_label_rand_neurons8_20reps.json"
    assert {k: v.name for k, v in e461.ROLLS.items()}["world_eight/ewc-block-rand"] == \
        "e439_earned_label_rand_20reps.json"
    assert e461.HEADS["world_eight"] == {"width": 8, "source": "the world's own state", "from_world": True}
    assert e461.HEADS["neurons_thirty_two"]["width"] == 32
    assert e461.HEADS["neurons_eight"]["width"] == 8
    assert e461.ANCHORS == ("ewc-block", "ewc-block-rand")
    assert e461.REVISION == 13 and e461.NEW == ("revision", "pair")
    assert (e461.BASELINE, e461.BUFFER) == ("naive", "replay")
    assert e461.N_TASKS == 3 and e461.MIN_REPS == 20 and e461.TOL == 0.002
    assert (e461.ALIKE, e461.ALIKE_FIRES) == (0.05, 0.10)
    assert (e461.WIDE_GAP, e461.WIDE_GAP_FLOOR) == (0.02, 0.01)


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e461_the_game_card_revision_thirteen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e461.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the card at revision 13, its twelfth revision carried, six cells over three heads
    assert d["card"]["revision"] == e461.REVISION, d["card"]["revision"]
    assert len(d["revision12"]) >= 20, len(d["revision12"])
    assert sorted(d["rolls"]) == sorted(e461.ROLLS), sorted(d["rolls"])
    assert len(d["pair"]["artifact"]) == len(d["rolls"]), d["pair"]["artifact"]
    assert sorted(d["pair"]["basis_accuracy"]) == sorted(e461.HEADS), sorted(d["pair"]["basis_accuracy"])
    for label, got in d["rolls"].items():
        assert got["replicates"] >= e461.MIN_REPS, label
        assert got["anchor"] == label.split("/")[1], label
        assert got["width"] == e461.HEADS[label.split("/")[0]]["width"], label
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
