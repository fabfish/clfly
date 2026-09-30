"""`e304` writes the module `clfly/lgcl/model.py`'s note defers to and applies it to every arm's retention matrix,
so the tests pin the split's exactness, the malformed-matrix refusals, the rank correlation, both faces of the four
claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from clfly.lgcl import metrics
from experiments import e304_the_decomposition_the_block_asked_for as e304


def _matrix(reached, ended):
    """A lower-triangular matrix whose diagonal is `reached` and whose last row is `ended`."""
    n = len(reached)
    assert n >= 1 and reached[-1] == ended[-1], "the last row is also the last diagonal cell"
    return [[reached[j] if j <= t else None for j in range(n)] for t in range(n - 1)] + [list(ended)]


def _close(a, b, tol=1e-9):
    return len(a) == len(b) and all(abs(x - y) < tol for x, y in zip(a, b))


def test_the_split_is_exact_and_has_no_free_parameter():
    R = _matrix([1.0, 0.8, 0.6], [0.9, 0.5, 0.6])
    d = metrics.decompose_forgetting(R)
    assert d["reached"] == [1.0, 0.8, 0.6] and _close(d["ended"], [0.9, 0.5, 0.6]), d
    assert _close(d["lost"], [0.1, 0.3, 0.0]), d["lost"]
    assert _close(d["unlearned"], [0.0, 0.2, 0.4]), d["unlearned"]
    assert metrics.residual(d) < 1e-12, metrics.residual(d)
    assert abs(d["unlearned_share"] - 0.6) < 1e-12, d
    # the ceiling is a parameter, so the split can be taken against a floor other than one
    e = metrics.decompose_forgetting(R, ceiling=0.5)
    assert metrics.residual(e) < 1e-12 and e["unlearned"][1] < 0, e


def test_a_perfect_arm_has_no_share_and_a_malformed_matrix_is_refused():
    perfect = metrics.decompose_forgetting(_matrix([1.0, 1.0], [1.0, 1.0]))
    assert perfect["unlearned_share"] is None, perfect
    # a None where a number is required is an error, not a zero: an unrecorded cell is not a score of nothing
    for bad in ([], [[1.0, None]], [[1.0, None], [None, 1.0]], [[1.0, None], [1.0, None]]):
        try:
            metrics.decompose_forgetting(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted {bad}")


def test_the_rank_correlation_is_spearman_and_survives_ties():
    assert abs(e304.rank_correlation([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-9
    assert abs(e304.rank_correlation([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9
    # a flat side has no rank spread, so there is no correlation to report rather than a zero
    assert e304.rank_correlation([1, 1, 1, 1], [1, 2, 3, 4]) is None
    assert e304.rank_correlation([1, 2], [2, 1]) is None
    # ties take the mean rank, so a monotone series with one tie keeps its sign
    assert abs(e304.rank_correlation([1, 2, 2, 3], [1, 2, 2, 3]) - 1.0) < 1e-9
    # and a partially tied pair is strictly between the two, which is the case the corpus is full of
    rho = e304.rank_correlation([1, 2, 2, 3], [3, 2, 1, 1])
    assert -1.0 < rho < 0, rho


def test_the_reading_is_taken_from_the_retention_matrix(tmp_path):
    def art(name, arm, retention, per_task, metric, reps=1):
        (tmp_path / name).write_text(json.dumps({"methods": {arm: {"replicates": [
            {"retention": retention, "forgetting_per_task": per_task, "mean_forgetting": metric}
            for _ in range(reps)]}}}), encoding="utf-8")
    art("a.json", "naive", _matrix([1.0, 0.8, 0.7], [0.9, 0.5, 0.7]), [0.1, 0.3, 0.0], 0.2, reps=2)
    art("b.json", "naive", _matrix([0.6, 0.6, 0.6], [0.6, 0.5, 0.6]), [0.0, 0.1, 0.0], 0.05)
    r = e304.reading(tmp_path)
    assert r["arm_replicates"] == 3 and r["n_arms"] == 2, (r["arm_replicates"], r["n_arms"])
    assert r["max_residual"] == 0.0 and r["n_disagreements"] == 0, r
    a = [x for x in r["arms"] if x["artifact"] == "a.json"][0]
    assert a["replicates"] == 2 and abs(a["lost_mean"] - (0.4 / 3)) < 1e-9, a
    # the arm with the lower stored metric is the arm that learned less, which is D4's shape
    assert r["rho"] is None or r["rho"] < 0, r["rho"]
    # and a stored `forgetting_per_task` that disagrees with the split is counted rather than ignored
    art("c.json", "naive", _matrix([1.0, 0.8, 0.7], [0.9, 0.5, 0.7]), [0.9, 0.3, 0.0], 0.2)
    assert e304.reading(tmp_path)["n_disagreements"] == 1, e304.reading(tmp_path)["n_disagreements"]


def _reading(arms=3, residual_=0.0, disagree=0, share=0.6, rho=-0.8):
    return {"arm_replicates": 10, "n_arms": arms, "refused": [],
            "arms": [{"artifact": f"a{i}.json", "arm": "naive", "replicates": 1, "mean_forgetting": 0.1 * i,
                      "lost_mean": 0.1, "unlearned_mean": 0.2, "shortfall_mean": 0.3,
                      "unlearned_share": share, "n_tasks": 3} for i in range(arms)],
            "max_residual": residual_, "n_disagreements": disagree, "max_disagreement": 0.0,
            "median_unlearned_share": share, "rho": rho, "n_scored": arms}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e304.judge(_reading())}
    for cid in ("D1", "D2", "D3", "D4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    assert e304.judge(_reading(residual_=1e-6))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e304.judge(_reading(disagree=2))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e304.judge(_reading(share=0.5))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e304.judge(_reading(rho=-0.4))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e304.judge(_reading(rho=None))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e304.judge({"n_arms": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    r = e304.reading()
    assert r["n_arms"] >= 300 and r["arm_replicates"] >= 5000, (r["n_arms"], r["arm_replicates"])
    assert r["max_residual"] is not None and r["max_residual"] <= 1e-9, r["max_residual"]
    assert r["n_disagreements"] == 0 and r["max_disagreement"] <= 1e-9, r["max_disagreement"]
    assert r["median_unlearned_share"] > 0.5, r["median_unlearned_share"]
    assert r["rho"] is not None and r["rho"] < -0.5, r["rho"]
    # and the arms the metric scores best are the ones whose share is largest
    scored = [a for a in r["arms"] if isinstance(a["mean_forgetting"], (int, float))]
    best = sorted(scored, key=lambda a: a["mean_forgetting"])[:20]
    worst = sorted(scored, key=lambda a: -a["mean_forgetting"])[:20]
    assert min(a["unlearned_share"] for a in best) > max(a["unlearned_share"] for a in worst), \
        (min(a["unlearned_share"] for a in best), max(a["unlearned_share"] for a in worst))
    claims = {x["id"]: x["verdict"] for x in e304.judge(r)}
    for cid in ("D1", "D2", "D3", "D4"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e304_the_decomposition_the_block_asked_for.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["n_arms"] >= 300 and d["max_residual"] <= 1e-9, (d["n_arms"], d["max_residual"])
    assert d["n_disagreements"] == 0 and d["median_unlearned_share"] > 0.5 and d["rho"] < -0.5, d["rho"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("D1", "D2", "D3", "D4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
