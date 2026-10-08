"""`e467` reads the budget curve at eight columns, so the tests pin both faces of the four claims, the sign sequence
the second claim is about, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e467_the_budget_curve_at_eight_columns as e467

BUDGETS = e467.BUDGETS
#: the shape of the curve: the biological anchor's standing negative at a hundred and positive at five hundred, one
#: sign change, the pair alike at every budget and the buffer ahead everywhere
BIO_STANDING = {100: -0.0483, 200: -0.0310, 350: 0.0040, 500: 0.0017}
RAND_STANDING = {100: -0.0205, 200: -0.0120, 350: -0.0060, 500: -0.0271}
BIO_PRICE = {100: -0.1031, 200: -0.0800, 350: -0.0700, 500: -0.0615}
RAND_PRICE = {100: -0.0583, 200: -0.0530, 350: -0.0500, 500: -0.0594}
OVER = (0.1500, 8.00)


def _doc(bio_standing=BIO_STANDING, rand_standing=RAND_STANDING, bio_price=BIO_PRICE, rand_price=RAND_PRICE,
         over=OVER, same_differ=None, readout=None, from_world=False, thin=False, short=False, ok=True,
         reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "readouts": {}, "curve": {}, "gaps": {},
                "spans": {}}
    curve = {}
    for b in BUDGETS:
        curve[str(b)] = {}
        for side, standing, price in (("bio", bio_standing, bio_price), ("rand", rand_standing, rand_price)):
            curve[str(b)][side] = {"budget": b, "side": side, "anchor": e467.ANCHOR_OF[side],
                                   "standing": standing[b], "standing_sigma": 2.2 if side == "bio" and b == 100 else 1.0,
                                   "price": price[b], "price_sigma": 4.0,
                                   "buffer_over_anchor": over[0], "buffer_over_anchor_sigma": over[1]}
    gaps = {str(b): {"price": abs(bio_price[b] - rand_price[b]),
                     "standing": abs(bio_standing[b] - rand_standing[b])} for b in BUDGETS}
    ro = {f"{b}/{side}": (8 if readout is None else readout) for b in BUDGETS for side in ("bio", "rand")}
    fromw = {f"{b}/{side}": (from_world if str(b) in e467.NEW else False)
             for b in BUDGETS for side in ("bio", "rand")}
    same = {f"{side}.config.circuit_size": True for side in ("bio", "rand")}
    same.update({f"{side}.circuit": True for side in ("bio", "rand")})
    same.update({f"{side}.tasks": True for side in ("bio", "rand")})
    if same_differ:
        same[same_differ] = False
    reps = 19 if thin else 20

    def sign(v):
        return 1 if v > 0 else -1

    return {"ok": True, "reason": None,
            "runs": {f"{b}/{side}": {"arms": {a: {"replicates": reps} for a in
                                              (e467.BASELINE, e467.ANCHOR_OF[side], e467.BUFFER)[:2 if short else 3]},
                                     "readouts": [ro[f"{b}/{side}"]] * 3, "from_world": fromw[f"{b}/{side}"]}
                     for b in BUDGETS for side in ("bio", "rand")},
            "same": same, "readouts": fromw, "curve": curve, "gaps": gaps,
            "spans": {"budgets": list(BUDGETS), "runs": 8, "same_fields": len(same),
                      "replicates": [reps], "thin": {f"x/{c}": reps for c in ("bio", "rand")} if thin else {},
                      "short": {"x": ["naive"]} if short else {}, "readout": ro, "from_world": fromw,
                      "sign": {side: [sign((bio_standing if side == "bio" else rand_standing)[b])
                                      for b in BUDGETS] for side in ("bio", "rand")},
                      "sign_changes": {side: sum(1 for i in range(len(BUDGETS) - 1)
                                                 if sign((bio_standing if side == "bio" else rand_standing)[BUDGETS[i]])
                                                 != sign((bio_standing if side == "bio" else rand_standing)[BUDGETS[i + 1]]))
                                       for side in ("bio", "rand")},
                      "budget": list(BUDGETS)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e467.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one sign change on the biological anchor, the pair alike at every budget, the buffer ahead everywhere
    j = _judge()
    for cid in ("TA1", "TA2", "TA3", "TA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # TA1: a field differing, a read-out at another width, one read from the world, thin replicates, a short arm list
    assert _judge(same_differ="bio.config.iters")["TA1"].startswith("FALSIFIER")
    assert _judge(readout=16)["TA1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["TA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["TA1"].startswith("FALSIFIER")
    assert _judge(short=True)["TA1"].startswith("FALSIFIER")

    # TA2: a sequence that crosses twice, and one whose ends do not differ
    #: **a sequence of four signs is where a crossing is located**, so the claim is about the count of changes and
    #: not about any one budget's value
    assert _judge(bio_standing={100: -0.05, 200: 0.02, 350: -0.01, 500: 0.01})["TA2"].startswith("FALSIFIER")
    assert _judge(bio_standing={100: -0.05, 200: -0.04, 350: -0.02, 500: -0.01})["TA2"].startswith("FALSIFIER")

    # TA3: a pair that separates at some budget, and one between the bars
    assert _judge(rand_price={100: -0.0583, 200: -0.0530, 350: -0.2000, 500: -0.0594})["TA3"].startswith("FALSIFIER")
    assert _judge(rand_price={100: -0.0583, 200: -0.0530, 350: -0.1300, 500: -0.0594})["TA3"].startswith("NULL")

    # TA4: a buffer that is behind its anchor somewhere, and one that does not resolve
    assert _judge(over=(-0.0300, -2.50))["TA4"].startswith("FALSIFIER")
    assert _judge(over=(0.0300, 1.20))["TA4"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e467.judge(_doc(ok=False)))


def test_the_runs_and_the_budgets_are_registered():
    #: the four new rolls are this unit's and the four beside them are the two budgets `e466` left the flip between
    assert e467.RUNS["200/bio"].name == "e467_earned_label_neurons8_iters200_20reps.json"
    assert e467.RUNS["200/rand"].name == "e467_earned_label_rand_neurons8_iters200_20reps.json"
    assert e467.RUNS["350/bio"].name == "e467_earned_label_neurons8_iters350_20reps.json"
    assert e467.RUNS["350/rand"].name == "e467_earned_label_rand_neurons8_iters350_20reps.json"
    assert e467.RUNS["100/bio"].name == "e466_earned_label_neurons8_iters100_20reps.json"
    assert e467.RUNS["100/rand"].name == "e466_earned_label_rand_neurons8_iters100_20reps.json"
    assert e467.RUNS["500/bio"].name == "e458_earned_label_neurons8_20reps.json"
    assert e467.RUNS["500/rand"].name == "e460_earned_label_rand_neurons8_20reps.json"
    assert e467.BUDGETS == (100, 200, 350, 500), e467.BUDGETS
    assert e467.BK == ("100", "200", "350", "500"), e467.BK
    assert e467.NEW == ("200", "350"), e467.NEW
    assert e467.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e467.ANCHOR_OF
    assert (e467.BASELINE, e467.BIO, e467.RAND, e467.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e467.SIGMA, e467.ALIKE, e467.ALIKE_FIRES) == (2.0, 0.05, 0.10)
    assert set(e467.IGNORED) == {"json_out", "iters"}, e467.IGNORED
    assert e467.N_TASKS == 3 and e467.N_ARMS == 3 and e467.MIN_REPS == 20


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e467_the_budget_curve_at_eight_columns.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e467.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: eight rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["runs"]) == [f"{b}/{side}" for b in BUDGETS for side in ("bio", "rand")], sorted(d["runs"])
    for label, roll in d["runs"].items():
        assert len(roll["arms"]) >= e467.N_ARMS, label
        for arm, got in roll["arms"].items():
            assert got["replicates"] >= e467.MIN_REPS, (label, arm)
    assert sorted(d["curve"]) == list(e467.BK), sorted(d["curve"])
    for b, sides in d["curve"].items():
        assert sorted(sides) == ["bio", "rand"], (b, sorted(sides))
        for side, got in sides.items():
            assert got["budget"] == int(b) and got["side"] == side, (b, side)
    assert sorted(d["gaps"]) == list(e467.BK), sorted(d["gaps"])
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    assert len(d["spans"]["sign"]["bio"]) == len(BUDGETS), d["spans"]["sign"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
