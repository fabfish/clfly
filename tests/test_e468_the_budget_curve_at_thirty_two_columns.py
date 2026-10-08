"""`e468` reads the budget curve at thirty-two columns beside the eight-column one, so the tests pin both faces of the
four claims, the two sign sequences the third claim compares, and the refusal when a roll or the narrow curve is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e468_the_budget_curve_at_thirty_two_columns as e468

BUDGETS = e468.BUDGETS
#: the shape: the biological anchor crosses once at thirty-two columns, exactly where it crossed at eight
BIO_STANDING = {100: -0.0243, 200: -0.0180, 350: -0.0110, 500: 0.0187}
RAND_STANDING = {100: -0.0424, 200: -0.0300, 350: -0.0210, 500: 0.0104}
BIO_PRICE = {100: -0.0479, 200: -0.0430, 350: -0.0360, 500: -0.0115}
RAND_PRICE = {100: -0.0729, 200: -0.0650, 350: -0.0580, 500: -0.0323}
NARROW_SIGN = [-1, -1, -1, 1]
NARROW_STANDING = {100: -0.0483, 200: -0.0378, 350: -0.0243, 500: 0.0017}
OVER = (0.1500, 8.00)


def _sign(v):
    return 1 if v > 0 else -1


def _doc(bio_standing=BIO_STANDING, rand_standing=RAND_STANDING, bio_price=BIO_PRICE, rand_price=RAND_PRICE,
         narrow_sign=NARROW_SIGN, narrow_standing=NARROW_STANDING, over=OVER, same_differ=None, readout=None,
         from_world=False, thin=False, short=False, ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "readouts": {}, "curve": {}, "gaps": {},
                "narrow": {}, "spans": {}}
    curve = {}
    for b in BUDGETS:
        curve[str(b)] = {}
        for side, standing, price in (("bio", bio_standing, bio_price), ("rand", rand_standing, rand_price)):
            curve[str(b)][side] = {"budget": b, "side": side, "anchor": e468.ANCHOR_OF[side], "width": e468.WIDTH,
                                   "standing": standing[b],
                                   "standing_sigma": 2.2 if side == "bio" and b == 100 else 1.0,
                                   "price": price[b], "price_sigma": 4.0,
                                   "buffer_over_anchor": over[0], "buffer_over_anchor_sigma": over[1]}
    gaps = {str(b): {"price": abs(bio_price[b] - rand_price[b]),
                     "standing": abs(bio_standing[b] - rand_standing[b])} for b in BUDGETS}
    ro = {f"{b}/{side}": (e468.WIDTH if readout is None else readout) for b in BUDGETS for side in ("bio", "rand")}
    fromw = {f"{b}/{side}": (from_world if str(b) in e468.NEW else False)
             for b in BUDGETS for side in ("bio", "rand")}
    same = {f"{side}.config.circuit_size": True for side in ("bio", "rand")}
    same.update({f"{side}.circuit": True for side in ("bio", "rand")})
    same.update({f"{side}.tasks": True for side in ("bio", "rand")})
    if same_differ:
        same[same_differ] = False
    reps = 19 if thin else 20
    signs = [_sign(bio_standing[b]) for b in BUDGETS]

    def changes(seq):
        return sum(1 for i in range(len(seq) - 1) if seq[i] != seq[i + 1])

    return {"ok": True, "reason": None,
            "runs": {f"{b}/{side}": {"arms": {a: {"replicates": reps} for a in
                                              (e468.BASELINE, e468.ANCHOR_OF[side], e468.BUFFER)[:2 if short else 3]},
                                     "readouts": [ro[f"{b}/{side}"]] * 3, "from_world": fromw[f"{b}/{side}"]}
                     for b in BUDGETS for side in ("bio", "rand")},
            "same": same, "readouts": fromw, "curve": curve, "gaps": gaps,
            "narrow": {"budgets": list(BUDGETS), "sign": narrow_sign, "standing": narrow_standing},
            "spans": {"width": e468.WIDTH, "narrow_width": e468.NARROW_WIDTH, "budgets": list(BUDGETS),
                      "runs": 8, "same_fields": len(same), "replicates": [reps],
                      "thin": {f"x/{c}": reps for c in ("bio", "rand")} if thin else {},
                      "short": {"x": ["naive"]} if short else {}, "readout": ro, "from_world": fromw,
                      "sign": signs, "sign_changes": changes(signs),
                      "narrow_sign": narrow_sign, "narrow_changes": changes(narrow_sign),
                      "standing": {str(b): bio_standing[b] for b in BUDGETS},
                      "standing_sigma": {str(b): (2.2 if b == 100 else 1.0) for b in BUDGETS},
                      "narrow_standing": narrow_standing}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e468.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one crossing at thirty-two columns, in the same place as the eight-column one
    j = _judge()
    for cid in ("UA1", "UA2", "UA3", "UA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # UA1: a field differing, a read-out at another width, one read from the world, thin replicates, a short arm list
    assert _judge(same_differ="bio.config.iters")["UA1"].startswith("FALSIFIER")
    assert _judge(readout=8)["UA1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["UA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["UA1"].startswith("FALSIFIER")
    assert _judge(short=True)["UA1"].startswith("FALSIFIER")

    # UA2: a sequence that crosses twice, and one whose ends do not differ
    assert _judge(bio_standing={100: -0.05, 200: 0.02, 350: -0.01, 500: 0.01})["UA2"].startswith("FALSIFIER")
    assert _judge(bio_standing={100: -0.05, 200: -0.04, 350: -0.02, 500: -0.01})["UA2"].startswith("FALSIFIER")

    # UA3: the narrow rung crossing somewhere else -- earlier, and later
    assert _judge(narrow_sign=[-1, -1, 1, 1])["UA3"].startswith("FALSIFIER")
    assert _judge(narrow_sign=[-1, 1, 1, 1])["UA3"].startswith("FALSIFIER")
    assert _judge(narrow_sign=[-1, -1, -1, 1])["UA3"].startswith("MET")

    # UA4: a pair that separates at some budget, and one between the bars
    assert _judge(rand_price={100: -0.0729, 200: -0.0650, 350: -0.2000, 500: -0.0323})["UA4"].startswith("FALSIFIER")
    assert _judge(rand_price={100: -0.0729, 200: -0.0650, 350: -0.1300, 500: -0.0323})["UA4"].startswith("NULL")

    #: a roll absent, or the narrow curve absent, refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e468.judge(_doc(ok=False)))


def test_the_runs_and_the_widths_are_registered():
    #: the four new rolls are this unit's; the four beside them are the two ends `e466` and `e455` already carried
    assert e468.RUNS["200/bio"].name == "e468_earned_label_neurons32_iters200_20reps.json"
    assert e468.RUNS["200/rand"].name == "e468_earned_label_rand_neurons32_iters200_20reps.json"
    assert e468.RUNS["350/bio"].name == "e468_earned_label_neurons32_iters350_20reps.json"
    assert e468.RUNS["350/rand"].name == "e468_earned_label_rand_neurons32_iters350_20reps.json"
    assert e468.RUNS["100/bio"].name == "e466_earned_label_neurons32_iters100_20reps.json"
    assert e468.RUNS["100/rand"].name == "e466_earned_label_rand_neurons32_iters100_20reps.json"
    assert e468.RUNS["500/bio"].name == "e455_earned_label_neurons_20reps.json"
    assert e468.RUNS["500/rand"].name == "e456_earned_label_rand_neurons_20reps.json"
    assert e468.NARROW.name == "e467_the_budget_curve_at_eight_columns.json"
    assert e468.BUDGETS == (100, 200, 350, 500), e468.BUDGETS
    assert e468.BK == ("100", "200", "350", "500"), e468.BK
    assert (e468.WIDTH, e468.NARROW_WIDTH) == (32, 8)
    assert e468.NEW == ("200", "350"), e468.NEW
    assert e468.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e468.ANCHOR_OF
    assert (e468.BASELINE, e468.BIO, e468.RAND, e468.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e468.SIGMA, e468.ALIKE, e468.ALIKE_FIRES) == (2.0, 0.05, 0.10)
    assert set(e468.IGNORED) == {"json_out", "iters"}, e468.IGNORED
    assert e468.N_TASKS == 3 and e468.N_ARMS == 3 and e468.MIN_REPS == 20


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e468_the_budget_curve_at_thirty_two_columns.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e468.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: eight rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["runs"]) == [f"{b}/{side}" for b in BUDGETS for side in ("bio", "rand")], sorted(d["runs"])
    for label, roll in d["runs"].items():
        assert len(roll["arms"]) >= e468.N_ARMS, label
        for arm, got in roll["arms"].items():
            assert got["replicates"] >= e468.MIN_REPS, (label, arm)
    assert sorted(d["curve"]) == list(e468.BK), sorted(d["curve"])
    for b, sides in d["curve"].items():
        assert sorted(sides) == ["bio", "rand"], (b, sorted(sides))
        for side, got in sides.items():
            assert got["budget"] == int(b) and got["side"] == side and got["width"] == e468.WIDTH, (b, side)
    assert sorted(d["gaps"]) == list(e468.BK), sorted(d["gaps"])
    assert len(d["spans"]["sign"]) == len(BUDGETS), d["spans"]["sign"]
    assert len(d["spans"]["narrow_sign"]) == len(BUDGETS), d["spans"]["narrow_sign"]
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
