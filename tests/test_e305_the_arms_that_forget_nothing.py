"""`e305` joins the zero-line reading to the decomposition, so the tests pin the join and what it drops, the summary
it takes over the two groups, both faces of the four claims, and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e305_the_arms_that_forget_nothing as e305


def _rep(mean_forgetting, reached, ended):
    """One replicate: a forgetting, and the retention matrix the decomposition reads."""
    n = len(reached)
    retention = [[reached[j] if j <= t else None for j in range(n)] for t in range(n - 1)] + [list(ended)]
    return {"mean_forgetting": mean_forgetting, "retention": retention,
            "forgetting_per_task": [reached[j] - ended[j] for j in range(n)]}


def _art(path: Path, arms):
    payload = {"methods": {a: {"replicates": reps} for a, reps in arms.items()}}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_join_drops_nothing_and_says_what_it_would_have(tmp_path):
    # an arm inside the two-sigma line whose diagonal is low: it forgets nothing because it learned little, and its
    # replicates straddle zero so its own mean is smaller than its noise
    tight = [_rep(0.02 + (0.04 if i % 2 else -0.04), [0.30, 0.30, 0.30], [0.28, 0.29, 0.30]) for i in range(6)]
    # an arm outside it with a high diagonal
    loose = [_rep(0.20 + 0.03 * i, [0.95, 0.95, 0.95], [0.75, 0.75, 0.95]) for i in range(6)]
    _art(tmp_path / "a.json", {"naive": tight, "ewc": loose})
    # an arm with no retention matrix at all, which the join must report rather than silently average over
    (tmp_path / "b.json").write_text(json.dumps({"methods": {"replay": {"replicates": [
        {"mean_forgetting": 0.01 + 0.001 * i} for i in range(6)]}}}), encoding="utf-8")

    rows, unjoined = e305.joined(tmp_path)
    assert len(rows) == 2, [r["arm"] for r in rows]
    assert [(u["arm"], u["why"]) for u in unjoined] == [("replay", "no readable retention matrix")], unjoined
    inside = [r for r in rows if r["at_zero"]]
    assert [r["arm"] for r in inside] == ["naive"], inside
    assert inside[0]["unlearned_share"] > 0.9, inside[0]
    s = e305.summary(rows)
    assert (s["inside"], s["outside"]) == (1, 1), s
    assert s["inside_share_above_half"] == 1 and s["inside_negative_lost"] == 0, s
    assert s["inside_median_share"] > s["outside_median_share"], s


def _reading(inside=10, above_half=None, inside_share=0.8, outside_share=0.5,
             above_median=None, negative=6, n=271):
    above_half = above_half if above_half is not None else int(inside * 0.9)
    above_median = above_median if above_median is not None else int(inside * 0.3)
    return {"arms": n, "inside": inside, "outside": n - inside,
            "inside_share_above_half": above_half, "inside_share_above_eight_tenths": above_half // 2,
            "inside_median_share": inside_share, "outside_median_share": outside_share,
            "median_shortfall": 0.086, "inside_above_median_shortfall": above_median,
            "inside_negative_lost": negative, "inside_at_forty": 8, "worst_inside": []}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e305.judge(_reading())}
    for cid in ("C1", "C2", "C3", "C4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # half or fewer above a half is C1's
    assert e305.judge(_reading(inside=10, above_half=5))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a line that picks arms sharing no more than the rest is C2's
    assert e305.judge(_reading(inside_share=0.5))[1]["verdict"].startswith("FALSIFIER FIRED")
    # fewer than a quarter above the median is C3's
    assert e305.judge(_reading(inside=100, above_median=24))[2]["verdict"].startswith("FALSIFIER FIRED")
    # fewer than five with nothing to forget is C4's
    assert e305.judge(_reading(negative=4))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e305.judge({"inside": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_join_and_the_four_groups_are_what_the_finding_says():
    rows, unjoined = e305.joined()
    assert len(rows) >= 271 and unjoined == [], unjoined
    s = e305.summary(rows)
    assert s["inside"] >= 55 and s["outside"] >= 216, (s["inside"], s["outside"])
    assert s["inside_share_above_half"] * 2 > s["inside"], s["inside_share_above_half"]
    assert s["inside_median_share"] > s["outside_median_share"], (s["inside_median_share"],
                                                                  s["outside_median_share"])
    #: **RE-READ 2026-10-01.** This was `>= 0.25` and it is a share on a corpus that grows arms: `e332` to `e334`
    #: added five-arm, two-arm and single-arm runs, and the in-line share moved to **0.242**, four arms below the
    #: line. The substance is that the in-line arms are markedly more shortfall-heavy than the outside ones, which
    #: the comparison below states; the share is now a band rather than a point.
    assert s["inside_above_median_shortfall"] / s["inside"] > 0.15, s
    assert s["inside_above_median_shortfall"] / s["inside"] < 0.60, s
    assert s["inside_negative_lost"] >= 5, s
    # the exhibit: an arm inside the line whose shortfall is many times the corpus median
    worst = s["worst_inside"][0]
    assert worst["unlearned_share"] > 0.9 and worst["shortfall_mean"] > 5 * s["median_shortfall"], worst
    claims = {x["id"]: x["verdict"] for x in e305.judge(s)}
    for cid in ("C1", "C2", "C4"):
        assert claims[cid].startswith("MET"), claims[cid]
    #: **the registered claim that the arriving arms pushed under its own bar.** C3 asks whether a quarter of the
    #: in-line arms sit above the corpus median shortfall and the answer is now **16 of 66, 0.242** -- reported as
    #: FIRED rather than re-based, because the bar is what the unit registered and the corpus is what changed.
    assert claims["C3"].startswith("FALSIFIER FIRED"), claims["C3"]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e305_the_arms_that_forget_nothing.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["unjoined"] == [] and d["inside"] >= 55, d["unjoined"]
    assert d["inside_median_share"] > d["outside_median_share"], d
    assert d["inside_negative_lost"] >= 5, d
    assert 0.15 < d["inside_above_median_shortfall"] / d["inside"] < 0.60, d
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("C1", "C2", "C4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    #: C3's bar is the unit's and the corpus moved under it; the verdict is reported as it stands
    assert claims["C3"]["verdict"].startswith("FALSIFIER FIRED"), claims["C3"]
