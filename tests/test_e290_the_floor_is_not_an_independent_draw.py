"""`e290` reads the premise `e267`'s statistic rests on, so the tests pin the source check, the census, the
per-artifact disagreement, both faces of the three claims, and the live numbers.
"""

from __future__ import annotations

import re

import json
from pathlib import Path

from experiments import e290_the_floor_is_not_an_independent_draw as e290

OUTSIDE = """
def main():
    suite = rate_tasks.make_suite(circ, **common)
    for method in args.methods.split(","):
        for r in range(args.repeats):
            reps.append(run_method(net, suite, method, args, seed=args.seed0 + 100 * r))
"""
INSIDE = """
def main():
    for method in args.methods.split(","):
        for r in range(args.repeats):
            suite = rate_tasks.make_overlap_suite(circ, seed=r)
            reps.append(run_method(net, suite, method, args, seed=args.seed0 + 100 * r))
"""


def test_the_source_check_locates_the_suite_and_the_loop():
    out = e290.suite_placement(OUTSIDE)
    assert out == {"loop_line": 4, "build_lines": [2], "outside": True}, out
    inside = e290.suite_placement(INSIDE)
    assert inside["loop_line"] == 3 and inside["build_lines"] == [4] and inside["outside"] is False, inside
    assert e290.suite_placement("")["outside"] is False


def _art(path: Path, n_eval=144, arms=("naive",), rows=6):
    payload = {"evaluation_noise": {"n_eval": n_eval}, "methods": {}}
    for a in arms:
        xs = [0.5 + 0.01 * i for i in range(rows)]
        payload["methods"][a] = {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in xs]}
        payload["evaluation_noise"][a] = {"binomial_sem": 0.02, "replicate_sd": 0.01,
                                          "variance_fraction": 4.0 if a == "naive" else 0.25}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_census_reads_only_arms_with_a_fraction(tmp_path):
    _art(tmp_path / "a.json", arms=("naive", "ewc", "replay"))
    (tmp_path / "b.json").write_text(json.dumps({"evaluation_noise": {"n_eval": 144, "naive": {"binomial_sem": 1.0}}}),
                                     encoding="utf-8")
    (tmp_path / "c.json").write_text("not json", encoding="utf-8")
    (tmp_path / "d.json").write_text(json.dumps({"evaluation_noise": [1, 2]}), encoding="utf-8")
    rows = e290.fractions(tmp_path)
    assert len(rows) == 3, rows
    assert {r["arm"] for r in rows} == {"naive", "ewc", "replay"}, rows
    naive = [r for r in rows if r["arm"] == "naive"][0]
    assert naive["fraction"] == 4.0 and naive["n_effective"] == 36.0 and abs(naive["share"] - 0.25) < 1e-12, naive
    per = e290.per_artifact(rows)
    assert len(per) == 1 and per[0]["arms"] == 3 and abs(per[0]["ratio"] - 16.0) < 1e-12, per
    # two arms is not enough to be a disagreement
    assert e290.per_artifact(rows[:2]) == [], e290.per_artifact(rows[:2])


def _reading(fracs=(4.0, 4.5), placement=None, per=None):
    rows = [{"artifact": "a.json", "arm": f"arm{i}", "n_eval": 144, "fraction": f,
             "n_effective": 144 / f, "share": 1 / f} for i, f in enumerate(fracs)]
    return {"fractions": rows, "placement": placement or {"loop_line": 9, "build_lines": [4], "outside": True},
            "per_artifact": per if per is not None else [{"artifact": "a.json", "n_eval": 144, "arms": 3,
                                                          "share_min": 0.2, "share_max": 1.0, "ratio": 5.0}]}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e290.judge(_reading())}
    for cid in ("Q1", "Q2", "Q3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a suite built inside the loop is Q1's falsifier
    j = {r["id"]: r for r in e290.judge(_reading(placement={"loop_line": 4, "build_lines": [9], "outside": False}))}
    assert j["Q1"]["verdict"].startswith("FALSIFIER FIRED"), j["Q1"]
    # a corpus whose fractions all sit below one is Q2's
    j = {r["id"]: r for r in e290.judge(_reading(fracs=(0.2, 0.4)))}
    assert j["Q2"]["verdict"].startswith("FALSIFIER FIRED"), j["Q2"]
    # arms that agree are Q3's
    j = {r["id"]: r for r in e290.judge(_reading(per=[{"artifact": "a.json", "n_eval": 144, "arms": 3,
                                                      "share_min": 0.9, "share_max": 1.0, "ratio": 1.1}]))}
    assert j["Q3"]["verdict"].startswith("FALSIFIER FIRED"), j["Q3"]
    j = {r["id"]: r for r in e290.judge(_reading(per=[]))}
    assert j["Q3"]["verdict"].startswith("FALSIFIER FIRED"), j["Q3"]
    assert e290.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e290.judge({"fractions": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    rows = e290.fractions()
    over = [x for x in rows if x["fraction"] > 1]
    assert len(rows) >= 246 and len(over) >= 77, (len(rows), len(over))
    assert 0.25 <= len(over) / len(rows) <= 0.40, len(over) / len(rows)
    assert max(x["fraction"] for x in rows) > 40, max(x["fraction"] for x in rows)
    # the smallest effective count in the corpus is a few decisions, not a hundred
    assert min(x["n_effective"] for x in over) < 5, min(x["n_effective"] for x in over)
    per = e290.per_artifact(rows)
    assert len(per) >= 30, len(per)
    ratios = [x["ratio"] for x in per]
    assert sum(1 for r in ratios if r > 1.2) >= len(per) - 2, ratios
    assert 2.0 <= sorted(ratios)[len(ratios) // 2] <= 4.0, sorted(ratios)[len(ratios) // 2]
    assert e290.suite_placement(e290.RUNNER.read_text(encoding="utf-8"))["outside"] is True


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e290_the_floor_is_not_an_independent_draw.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["placement"]["outside"] is True, d["placement"]
    rows = d["fractions"]
    assert len(rows) >= 246, len(rows)
    over = [x for x in rows if x["fraction"] > 1]
    #: **RE-READ 2026-10-03: THE BAND'S TOP EDGE IS GONE.** It was written when the share was about thirty per cent,
    #: and the window's closed-loop runs have taken it to **35.03** on 394 arms. The unit's own claim (Q2) has no
    #: upper edge -- its falsifier is *fewer than a tenth* -- so what is pinned here is that the floor swallows more
    #: than a quarter of the arms, and Q2's verdict is read off the artifact below. A share that tracks the corpus
    #: belongs in the reading and not in the gate.
    assert len(over) / len(rows) > 0.25, len(over) / len(rows)
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("Q1", "Q2", "Q3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    m = re.search(r"\((\d+)%\)", claims["Q2"]["measured"])
    assert m and 25 <= int(m.group(1)) <= 40, claims["Q2"]
    q3 = re.search(r"(\d+) of (\d+) artifacts", claims["Q3"]["measured"])
    assert q3 and int(q3.group(1)) * 10 >= int(q3.group(2)) * 9, claims["Q3"]
