"""`e466` reads the width ladder at a hundred updates beside the far point's, so the tests pin both faces of the four
claims, the two ladders the second and third are about, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e466_the_width_ladder_at_another_budget as e466

CELLS = e466.CELLS
WIDTHS = e466.WIDTHS
#: the far point's own readings, which this unit reads beside its own rather than recomputing
FAR_PRICE = {"bio": {8: -0.0615, 16: -0.0406, 32: -0.0115}, "rand": {8: -0.0594, 16: -0.0396, 32: -0.0323}}
FAR_STANDING = {"bio": {8: 0.0017, 16: 0.0215, 32: 0.0187}, "rand": {8: -0.0271, 16: 0.0042, 32: 0.0104}}
#: the shape at the middle point: both magnitudes ordered, the pair alike at every width, the buffer ahead everywhere
MID_PRICE = {"bio": {8: (-0.0400, 3.00), 16: (-0.0300, 2.60), 32: (-0.0200, 2.20)},
             "rand": {8: (-0.0380, 2.80), 16: (-0.0290, 2.40), 32: (-0.0220, 2.10)}}
MID_STANDING = {"bio": {8: (0.0100, 0.70), 16: (0.0050, 0.40), 32: (0.0020, 0.20)},
                "rand": {8: (-0.0050, 0.40), 16: (0.0030, 0.30), 32: (0.0010, 0.10)}}
OVER = (0.1500, 8.00)


def _doc(mid_price=MID_PRICE, mid_standing=MID_STANDING, over=OVER, same_differ=None, readout=None,
         from_world=False, thin=False, short=False, ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "readouts": {}, "table": {}, "gaps": {},
                "spans": {}}
    table = {"far": {}, "mid": {}}
    gaps = {"far": {}, "mid": {}}
    for point, price, standing in (("far", FAR_PRICE, FAR_STANDING),
                                   ("mid", {s: {w: v[0] for w, v in d.items()} for s, d in mid_price.items()},
                                    {s: {w: v[0] for w, v in d.items()} for s, d in mid_standing.items()})):
        for w in WIDTHS:
            for side in ("bio", "rand"):
                cell = f"{w}/{side}"
                if point == "mid":
                    p, ps = mid_price[side][w]
                    st, ss = mid_standing[side][w]
                else:
                    p, ps, st, ss = price[side][w], 3.0, standing[side][w], 1.0
                table[point][cell] = {"width": w, "side": side, "anchor": e466.ANCHOR_OF[side],
                                      "standing": st, "standing_sigma": ss, "price": p, "price_sigma": ps,
                                      "buffer_over_anchor": over[0], "buffer_over_anchor_sigma": over[1]}
        for w in WIDTHS:
            gaps[point][str(w)] = {"price": abs(table[point][f"{w}/bio"]["price"] -
                                                 table[point][f"{w}/rand"]["price"]),
                                   "standing": abs(table[point][f"{w}/bio"]["standing"] -
                                                   table[point][f"{w}/rand"]["standing"])}
    ro = {cell: (int(cell.split("/")[0]) if readout is None else readout) for cell in CELLS}
    fromw = {f"{point}/{cell}": (from_world if point == "mid" else False) for point in ("far", "mid") for cell in CELLS}
    same = {f"{cell}.config.circuit_size": True for cell in CELLS}
    same.update({f"{cell}.circuit": True for cell in CELLS})
    same.update({f"{cell}.tasks": True for cell in CELLS})
    if same_differ:
        same[same_differ] = False
    reps = 19 if thin else 20
    return {"ok": True, "reason": None,
            "runs": {f"{point}/{cell}": {"arms": {a: {"replicates": reps} for a in
                                                  (e466.BASELINE, e466.ANCHOR_OF[cell.split("/")[1]], e466.BUFFER)[
                                                      :2 if short else 3]},
                                         "readouts": [ro[cell]] * 3, "from_world": fromw[f"{point}/{cell}"]}
                     for point in ("far", "mid") for cell in CELLS},
            "same": same, "readouts": fromw, "table": table, "gaps": gaps,
            "spans": {"cells": len(CELLS), "runs": 12, "replicates": [reps],
                      "same_fields": len(same), "thin": {f"x/{c}": reps for c in CELLS} if thin else {},
                      "short": {"x": ["naive"]} if short else {},
                      "mid_readout": ro, "far_readout": ro, "from_world": fromw,
                      "mag": {s: [abs(mid_price[s][w][0]) for w in WIDTHS] for s in ("bio", "rand")},
                      "mag_far": {s: [abs(FAR_PRICE[s][w]) for w in WIDTHS] for s in ("bio", "rand")},
                      "budget": dict(e466.BUDGET)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e466.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: both magnitudes ordered at a hundred updates, the pair alike at every width, the buffer ahead
    j = _judge()
    for cid in ("SA1", "SA2", "SA3", "SA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # SA1: a field differing, a read-out at another width, one read from the world, thin replicates, a short arm list
    assert _judge(same_differ="8/bio.config.iters")["SA1"].startswith("FALSIFIER")
    assert _judge(readout=32)["SA1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["SA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["SA1"].startswith("FALSIFIER")
    assert _judge(short=True)["SA1"].startswith("FALSIFIER")

    # SA2: an arm whose magnitude rises as the head widens, at either arm
    rising = {"bio": {8: (-0.0200, 2.00), 16: (-0.0400, 3.00), 32: (-0.0300, 2.50)},
              "rand": MID_PRICE["rand"]}
    assert _judge(mid_price=rising)["SA2"].startswith("FALSIFIER")

    # SA3: a pair that separates at the middle point, and one between the bars
    wide = {"bio": MID_PRICE["bio"], "rand": {8: (-0.0380, 2.80), 16: (-0.0290, 2.40), 32: (-0.1500, 4.00)}}
    assert _judge(mid_price=wide)["SA3"].startswith("FALSIFIER")
    mid = {"bio": MID_PRICE["bio"], "rand": {8: (-0.0380, 2.80), 16: (-0.0290, 2.40), 32: (-0.1000, 3.00)}}
    assert _judge(mid_price=mid)["SA3"].startswith("NULL")

    # SA4: a buffer that is behind its anchor, and one that does not resolve
    assert _judge(over=(-0.0300, -2.50))["SA4"].startswith("FALSIFIER")
    assert _judge(over=(0.0300, 1.20))["SA4"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e466.judge(_doc(ok=False)))


def test_the_runs_and_the_budgets_are_registered():
    #: the six new rolls are this unit's and the six beside them are the far point's own
    assert e466.MID["8/bio"].name == "e466_earned_label_neurons8_iters100_20reps.json"
    assert e466.MID["8/rand"].name == "e466_earned_label_rand_neurons8_iters100_20reps.json"
    assert e466.MID["32/bio"].name == "e466_earned_label_neurons32_iters100_20reps.json"
    assert e466.FAR["8/bio"].name == "e458_earned_label_neurons8_20reps.json"
    assert e466.FAR["8/rand"].name == "e460_earned_label_rand_neurons8_20reps.json"
    assert e466.FAR["16/bio"].name == "e462_earned_label_neurons16_20reps.json"
    assert e466.FAR["32/bio"].name == "e455_earned_label_neurons_20reps.json"
    assert e466.FAR["32/rand"].name == "e456_earned_label_rand_neurons_20reps.json"
    assert e466.WIDTHS == (8, 16, 32), e466.WIDTHS
    assert e466.BUDGET == {"far": 500, "mid": 100}, e466.BUDGET
    assert e466.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e466.ANCHOR_OF
    assert (e466.BASELINE, e466.BIO, e466.RAND, e466.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e466.SIGMA, e466.ALIKE, e466.ALIKE_FIRES) == (2.0, 0.05, 0.10)
    #: the budget is the one field a roll may differ in, and the point of the unit is that it is allowed to
    assert set(e466.IGNORED) == {"json_out", "iters"}, e466.IGNORED
    assert e466.N_TASKS == 3 and e466.N_ARMS == 3 and e466.MIN_REPS == 20


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e466_the_width_ladder_at_another_budget.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e466.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: twelve rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["runs"]) == [f"{point}/{cell}" for point in ("far", "mid") for cell in sorted(CELLS)], \
        sorted(d["runs"])
    for label, roll in d["runs"].items():
        assert len(roll["arms"]) >= e466.N_ARMS, label
        for arm, got in roll["arms"].items():
            assert got["replicates"] >= e466.MIN_REPS, (label, arm)
    assert sorted(d["table"]) == ["far", "mid"], sorted(d["table"])
    for point, cells in d["table"].items():
        assert sorted(cells) == sorted(CELLS), (point, sorted(cells))
        for cell, got in cells.items():
            assert got["width"] == int(cell.split("/")[0]), (point, cell)
            assert got["side"] == cell.split("/")[1], (point, cell)
    assert sorted(d["gaps"]["mid"]) == sorted(e466.WK), sorted(d["gaps"]["mid"])
    assert d["spans"]["same_fields"] >= 30, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
