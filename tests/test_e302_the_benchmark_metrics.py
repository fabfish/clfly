"""`e302` reads the benchmark block's metric list and its comparability promise, so the tests pin the phrase
reading, the code arm, the artifact-key arm, the order reading, both faces of the four claims, and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e302_the_benchmark_metrics as e302


def test_the_metric_list_is_read_from_the_block_in_the_blocks_own_words():
    text = (
        "# plan\n\n## The benchmark -- v0\n\n"
        "Some prose about the substrate.\n\n"
        "Metrics: average accuracy; **decomposed forgetting** \u2014 irreducible drift separated from estimation "
        "degradation, as section 5 recommends, and it is the metric we want; backward transfer; and pairwise task "
        "principal angles.\n\n"
        "More prose.\n\n## Experimental programme\n\nnot the block.\n"
    )
    assert e302.metric_phrases(text) == ["average accuracy", "decomposed forgetting", "backward transfer",
                                         "pairwise task principal angles"], e302.metric_phrases(text)


def test_the_code_arm_does_not_read_the_unit_that_is_looking(tmp_path):
    (tmp_path / "m.py").write_text("x = 'observability'\n", encoding="utf-8")
    assert e302.code_evidence(("observability",), dirs=(tmp_path,)) == {"observability": 1}
    # this unit's own file carries every declared spelling, so it is excluded by name rather than by directory
    (tmp_path / e302.SELF).write_text("x = 'backward_transfer backward transfer bwt'\n", encoding="utf-8")
    assert e302.code_evidence(("backward_transfer", "bwt"), dirs=(tmp_path,)) == {"backward_transfer": 0, "bwt": 0}


def test_the_artifact_arm_counts_payloads_and_not_occurrences(tmp_path):
    for name, n in (("a.json", 3), ("b.json", 1)):
        (tmp_path / name).write_text(json.dumps(
            {"methods": {f"m{i}": {"final_accuracy": 0.5, "mean_forgetting": 0.1} for i in range(n)},
             "nested": [{"locked": True}]}), encoding="utf-8")
    counts = e302.artifact_keys(tmp_path)
    assert counts["final_accuracy"] == 2 and counts["mean_forgetting"] == 2, counts
    assert counts["locked"] == 2 and counts["methods"] == 2, counts


def test_the_order_reading_groups_by_suite(tmp_path):
    def art(name, names):
        (tmp_path / name).write_text(json.dumps(
            {"tasks": [{"name": n} for n in names], "config": {"seed0": 0}}), encoding="utf-8")
    art("a.json", ("t0", "t1", "t2"))
    art("b.json", ("t0", "t1", "t2"))
    art("c.json", ("t2", "t1", "t0"))
    rows = e302.orders(tmp_path)
    assert len(rows) == 3 and all(r["suite"] == ("t0", "t1", "t2") for r in rows), rows
    assert {tuple(r["order"]) for r in rows} == {("t0", "t1", "t2"), ("t2", "t1", "t0")}, rows


def _reading(metrics=None, suites=None, prescribed=0, conventional=163):
    metrics = metrics if metrics is not None else [
        {"metric": f"m{i}", "declared": [f"m{i}"], "code": {f"m{i}": 1} if i < 4 else {},
         "implemented": i < 4, "carried_by": [(f"m{i}", 5)] if i < 2 else [],
         "carried_total": 5 if i < 2 else 0} for i in range(5)]
    suites = suites or {"a,b,c": ["a,b,c"]}
    return {"metrics": metrics, "n_metrics": len(metrics), "orders": [], "n_orders": 164,
            "suites": suites, "seeds": {"0": 163}, "prescribed": prescribed, "conventional": conventional,
            "declared": {}, "plan": "plan"}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e302.judge(_reading())}
    for cid in ("M1", "M2", "M3", "M4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a metric the repository implements everywhere is M1's falsifier
    full = _reading(metrics=[dict(m, implemented=True, code={"x": 1}) for m in _reading()["metrics"]])
    assert e302.judge(full)[0]["verdict"].startswith("FALSIFIER FIRED"), e302.judge(full)[0]
    # three of five carried is M2's
    three = _reading(metrics=[dict(m, carried_by=[("m0", 5)] if i < 3 else [], carried_total=5 if i < 3 else 0)
                              for i, m in enumerate(_reading()["metrics"])])
    assert e302.judge(three)[1]["verdict"].startswith("FALSIFIER FIRED"), e302.judge(three)[1]
    # a corpus carrying the prescribed spelling is M3's
    assert e302.judge(_reading(prescribed=4))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e302.judge(_reading())[2]["verdict"].startswith("MET")
    # a suite recorded in two orders is M4's
    assert e302.judge(_reading(suites={"a,b,c": ["a,b,c", "c,b,a"]}))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e302.judge(_reading())[3]["verdict"].startswith("MET")
    assert e302.judge({"metrics": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_block_is_what_the_finding_says():
    r = e302.audits()
    assert [x["metric"] for x in r["metrics"]] == ["average accuracy", "decomposed forgetting", "backward transfer",
                                                   "per-task observability spectrum",
                                                   "pairwise task principal angles"], r["metrics"]
    absent = [x["metric"] for x in r["metrics"] if not x["implemented"]]
    assert absent == ["backward transfer"], absent
    carried = {x["metric"]: x["carried_by"] for x in r["metrics"] if x["carried_by"]}
    assert set(carried) == {"average accuracy", "decomposed forgetting"}, carried
    assert r["prescribed"] == 0 and r["conventional"] >= 150, (r["prescribed"], r["conventional"])
    assert r["n_orders"] >= 147 and len(r["suites"]) >= 6, (r["n_orders"], len(r["suites"]))
    # `e315` ran the corpus's first permutation of a suite, so M4 has fired and the claim is now about
    # the shape of the violation: exactly one suite records two orders, and they are each other reversed
    two = {k: v for k, v in r["suites"].items() if len(v) > 1}
    assert len(two) == 1, two
    pair = list(two.values())[0]
    assert sorted(pair[0].split(",")) == sorted(pair[1].split(",")), pair
    assert sum(1 for o in r["orders"] if o["seed0"] == 0) >= 140, r["seeds"]
    claims = {x["id"]: x["verdict"] for x in e302.judge(r)}
    for cid in ("M1", "M2", "M3"):
        assert claims[cid].startswith("MET"), claims[cid]
    # M4 was `e302`'s claim about the corpus, and `e315` ended it by running the first permutation
    assert claims["M4"].startswith("FALSIFIER FIRED"), claims["M4"]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e302_the_benchmark_metrics.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["metrics"]) == 5, len(d["metrics"])
    assert not any(x["implemented"] for x in d["metrics"] if x["metric"] == "backward transfer"), d["metrics"]
    assert d["prescribed"] == 0 and d["conventional"] >= 150, (d["prescribed"], d["conventional"])
    assert len({k: v for k, v in d["suites"].items() if len(v) > 1}) == 1, d["suites"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("M1", "M2", "M3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert claims["M4"]["verdict"].startswith("FALSIFIER FIRED"), claims["M4"]
