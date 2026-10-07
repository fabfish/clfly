"""`e459` writes the card's twelfth revision, so the tests pin both faces of the five claims and the refusal when an
artifact it is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e459_the_game_card_revision_twelve as e459

#: the three heads of the card's own world: fixed true values, so a mutation moves one of them
CELLS = {
    "world/8": (8, "the world's own state", -0.0302, 1.77, -0.1177, 3.71, [0.2896, 0.2490, -0.0604], 0.1896, 10.89),
    "neurons/32": (32, "the circuit's own neurons", 0.0187, 1.03, -0.0115, 0.78, [0.2323, 0.1812, -0.0302], 0.1090,
                   7.66),
    "neurons/8": (8, "the circuit's own neurons", 0.0017, 0.12, -0.0615, 4.48, [0.3281, 0.2958, -0.0833], 0.1785, 10.48),
}
#: the fields the revision-11 card carries, which this unit may not rewrite
OLD = {"name": "the closed-loop earned-label game", "readout": {"buffer": "replay"}, "method": {"rolls": 10}}


def _rolls(cells=None) -> dict:
    spec = CELLS if cells is None else cells
    out = {}
    for label, (width, source, st, st_sig, pr, pr_sig, gain, over, over_sig) in spec.items():
        out[label] = {"artifact": label.replace("/", "_") + ".json", "width": width, "source": source,
                      "from_world": source.startswith("the world"), "replicates": 20,
                      "standing": {"n": 20, "mean": st, "sd": 0.05, "se": 0.01, "sigma": st_sig},
                      "price": {"n": 20, "mean": pr, "sd": 0.05, "se": 0.01, "sigma": pr_sig},
                      "buffer_gain": list(gain),
                      "buffer_over_anchor": {"n": 20, "mean": over, "sd": 0.05, "se": 0.01, "sigma": over_sig}}
    return out


def _clause(rolls: dict) -> dict:
    return {"artifact": [v["artifact"] for v in rolls.values()],
            "heads": {l: {"width": v["width"], "source": v["source"], "from_world": v["from_world"]}
                      for l, v in rolls.items()},
            "buffer": e459.BUFFER, "anchor": e459.ANCHOR,
            "anchor_over_naive": {l: v["standing"]["mean"] for l, v in rolls.items()},
            "anchor_over_naive_sigma": {l: v["standing"]["sigma"] for l, v in rolls.items()},
            "newest_task": {l: v["price"]["mean"] for l, v in rolls.items()},
            "newest_task_sigma": {l: v["price"]["sigma"] for l, v in rolls.items()},
            "buffer_gain": {l: list(v["buffer_gain"]) for l, v in rolls.items()},
            "buffer_over_anchor": {l: v["buffer_over_anchor"]["mean"] for l, v in rolls.items()},
            "buffer_over_anchor_sigma": {l: v["buffer_over_anchor"]["sigma"] for l, v in rolls.items()}}


def _doc(cells=None, clause=None, same_differ=None, revision=e459.REVISION, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": {}, "revision11": {}, "head": {}, "rolls": {}}
    rr = _rolls(cells)
    c = _clause(rr) if clause is None else clause
    card = {k: (dict(v) if isinstance(v, dict) else v) for k, v in OLD.items()}
    card["revision"] = revision
    card["head"] = c
    if same_differ:
        card[same_differ] = "rewritten"
    return {"ok": True, "reason": None, "card": card, "revision11": dict(OLD), "head": c, "rolls": rr}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e459.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the eleventh revision carried and the head clause reading as the three rolls do
    j = _judge()
    for cid in ("DF1", "DF2", "DF3", "DF4", "DF5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DF1: a field rewritten and a revision that did not move
    assert _judge(same_differ="readout")["DF1"].startswith("FALSIFIER")
    assert _judge(revision=11)["DF1"].startswith("FALSIFIER")

    # DF2: a price, a standing and a per-position gain the clause gets wrong
    rr = _rolls()
    c = _clause(rr)
    c["newest_task"] = dict(c["newest_task"])
    c["newest_task"]["neurons/8"] = -0.9000
    assert _judge(clause=c)["DF2"].startswith("FALSIFIER")
    c = _clause(rr)
    c["anchor_over_naive"] = dict(c["anchor_over_naive"])
    c["anchor_over_naive"]["world/8"] = 0.4000
    assert _judge(clause=c)["DF2"].startswith("FALSIFIER")
    c = _clause(rr)
    c["buffer_gain"] = dict(c["buffer_gain"])
    c["buffer_gain"]["world/8"] = [0.1, 0.2, 0.3]
    assert _judge(clause=c)["DF2"].startswith("FALSIFIER")

    # DF3: an eight-column head whose price does not resolve, and a thirty-two column one where it does
    odd = dict(CELLS)
    odd["neurons/8"] = (8, "the circuit's own neurons", 0.0017, 0.12, -0.0200, 1.00, [0.3281, 0.2958, -0.0833], 0.1785,
                        10.48)
    assert _judge(cells=odd)["DF3"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons/32"] = (32, "the circuit's own neurons", 0.0187, 1.03, -0.1177, 3.00, [0.2323, 0.1812, -0.0302],
                         0.1090, 7.66)
    assert _judge(cells=odd)["DF3"].startswith("FALSIFIER")

    # DF4: a standing that resolves at one head
    odd = dict(CELLS)
    odd["neurons/32"] = (32, "the circuit's own neurons", 0.0300, 2.50, -0.0115, 0.78, [0.2323, 0.1812, -0.0302],
                         0.1090, 7.66)
    assert _judge(cells=odd)["DF4"].startswith("FALSIFIER")

    # DF5: a head with no first-position gain, and one where the buffer is not ahead of the anchor
    odd = dict(CELLS)
    odd["neurons/32"] = (32, "the circuit's own neurons", 0.0187, 1.03, -0.0115, 0.78, [0.0200, 0.1812, -0.0302],
                         0.1090, 7.66)
    assert _judge(cells=odd)["DF5"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["neurons/32"] = (32, "the circuit's own neurons", 0.0187, 1.03, -0.0115, 0.78, [0.2323, 0.1812, -0.0302],
                         -0.0500, -3.00)
    assert _judge(cells=odd)["DF5"].startswith("FALSIFIER")

    #: an artifact the revision is read from absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e459.judge(_doc(ok=False)))


def test_the_card_and_the_heads_are_registered():
    #: the revision-11 card is what is added to, and the three heads are its world's
    assert e459.CARD11.name == "e457_the_game_card_revision_eleven.json"
    assert {k: v.name for k, v in e459.ROLLS.items()} == {
        "world/8": "e438_earned_label_three_arms_20reps.json",
        "neurons/32": "e455_earned_label_neurons_20reps.json",
        "neurons/8": "e458_earned_label_neurons8_20reps.json"}
    assert e459.WIDTHS == {"world/8": 8, "neurons/32": 32, "neurons/8": 8}
    assert e459.SOURCES["world/8"] == "the world's own state"
    assert e459.SOURCES["neurons/32"] == e459.SOURCES["neurons/8"] == "the circuit's own neurons"
    assert e459.REVISION == 12 and e459.NEW == ("revision", "head")
    assert (e459.BASELINE, e459.ANCHOR, e459.BUFFER) == ("naive", "ewc-block", "replay")
    assert e459.N_TASKS == 3 and e459.MIN_REPS == 20 and e459.SIGMA == 2.0 and e459.TOL == 0.002
    assert e459.FIRST_BAR == 0.05


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e459_the_game_card_revision_twelve.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e459.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the card at revision 12, its eleventh revision carried, three heads under the clause
    assert d["card"]["revision"] == e459.REVISION, d["card"]["revision"]
    assert len(d["revision11"]) >= 20, len(d["revision11"])
    assert sorted(d["rolls"]) == sorted(e459.ROLLS), sorted(d["rolls"])
    assert len(d["head"]["artifact"]) == len(d["rolls"]), d["head"]["artifact"]
    assert sorted(d["head"]["heads"]) == ["neurons/32", "neurons/8", "world/8"], d["head"]["heads"]
    seen = {(v["width"], v["source"]) for v in d["head"]["heads"].values()}
    assert (8, "the world's own state") in seen and (32, "the circuit's own neurons") in seen, seen
    for label, got in d["rolls"].items():
        assert got["replicates"] >= e459.MIN_REPS, label
        assert len(got["buffer_gain"]) == e459.N_TASKS, label
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
