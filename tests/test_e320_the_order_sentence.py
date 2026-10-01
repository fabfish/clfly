"""`e320` reads the block's promise of fixed task orders and the scope the runs gave it, so the tests pin the
paragraph detector, the corpus census of orders, both faces of the three claims, and the live invariant.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e320_the_order_sentence as e320


def _plan(body):
    return "# plan\n\n## The benchmark -- v0\n\n" + body + "\n\n## Experimental programme\n\nnot the block.\n"


def test_the_detector_reads_the_paragraph_and_not_one_sentence(tmp_path):
    bare = _plan("Reference framework: `clfly/bench/` with fixed task orders and seeds, so numbers are comparable "
                 "across methods -- a shared protocol that CL-for-SNN work currently lacks.")
    p = tmp_path / "plan.md"
    p.write_text(bare, encoding="utf-8")
    r = e320.reading(p, tmp_path)
    assert r["order_cue"] and r["comparability_cue"], r
    assert r["moves_cues"] == [], r
    # a scope clause added as a second sentence of the same paragraph is inside the unit of reading
    scoped = _plan("Reference framework: `clfly/bench/` with fixed task orders and seeds, so numbers are comparable "
                   "across methods. **Scoped**: reversing moves the arms that read a penalty and leaves the arms "
                   "that read none alone (`e317`).")
    p.write_text(scoped, encoding="utf-8")
    r = e320.reading(p, tmp_path)
    assert r["moves_cues"] and r["units"] == ["e317"], r
    # a paragraph with only one of the two cues is not the order paragraph
    other = _plan("The suite runs on one circuit with a fixed seed.")
    p.write_text(other, encoding="utf-8")
    assert e320.order_sentence(other) == "", e320.order_sentence(other)
    assert e320.judge(e320.reading(p, tmp_path))[0]["verdict"].startswith("REFUSED")


def test_the_order_census_counts_suites_and_not_artifacts(tmp_path):
    def art(name, names):
        (tmp_path / name).write_text(json.dumps({"tasks": [{"name": n} for n in names]}), encoding="utf-8")
    art("a.json", ("t0", "t1", "t2"))
    art("b.json", ("t0", "t1", "t2"))
    art("c.json", ("t2", "t1", "t0"))
    art("d.json", ("u0", "u1", "u2"))
    two = e320.suites_with_two_orders(tmp_path)
    assert list(two) == ["t0,t1,t2"], two
    assert two["t0,t1,t2"] == ["t0,t1,t2", "t2,t1,t0"], two
    (tmp_path / "c.json").unlink()
    assert e320.suites_with_two_orders(tmp_path) == {}, e320.suites_with_two_orders(tmp_path)


def _reading(sentence="Reference framework: with fixed task orders and seeds, so numbers are comparable.",
             cues=(), units=(), two=("t0,t1,t2",)):
    return {"sentence": sentence, "chars": len(sentence), "order_cue": True, "comparability_cue": True,
            "moves_cues": list(cues), "units": list(units), "findings": [],
            "suites_with_two_orders": {k: [] for k in two}, "n_suites_with_two_orders": len(two)}


def test_the_three_claims_read_both_faces():
    live = _reading(cues=("the arms that read a penalty",), units=("e317",))
    j = {r["id"]: r for r in e320.judge(live)}
    for cid in ("O1", "O2", "O3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # the as-found reading: the promise without a clause about what it moves
    as_found = _reading()
    j = {r["id"]: r for r in e320.judge(as_found)}
    assert j["O1"]["verdict"].startswith("MET"), j["O1"]
    assert j["O2"]["verdict"].startswith("FALSIFIER FIRED"), j["O2"]
    # a corpus of one order per suite is O3's falsifier
    assert e320.judge(_reading(two=()))[2]["verdict"].startswith("FALSIFIER FIRED")
    # and no sentence at all is REFUSED
    assert e320.judge(_reading(sentence="", cues=("x",)))[0]["verdict"].startswith("REFUSED")


def test_the_live_block_satisfies_the_invariant():
    r = e320.reading()
    assert r["order_cue"] and r["comparability_cue"], r
    assert r["moves_cues"], r
    assert r["units"], r
    # the corpus's own record: at least one suite in two orders, and the two are the families the runs reversed
    assert r["n_suites_with_two_orders"] >= 1, r["suites_with_two_orders"]
    claims = {x["id"]: x["verdict"] for x in e320.judge(r)}
    for cid in ("O1", "O2", "O3"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e320_the_order_sentence.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["order_cue"] and d["comparability_cue"] and d["moves_cues"] and d["units"], d
    assert d["n_suites_with_two_orders"] >= 1, d["suites_with_two_orders"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("O1", "O2", "O3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
