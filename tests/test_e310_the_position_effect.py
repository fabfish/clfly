"""`e310` reads the position effect off the corpus's retention diagonals, so the tests pin the suite families, the
ordering predicate, both faces of the four claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e310_the_position_effect as e310


def test_the_suite_families_are_told_apart_by_the_names_a_run_writes(tmp_path):
    def art(name, names):
        (tmp_path / name).write_text(json.dumps({"tasks": [{"name": n} for n in names]}), encoding="utf-8")
    art("a.json", ("ov0_t0", "ov0_t1", "ov0_t2"))
    art("b.json", ("odour_identity", "heading", "odour_input"))
    art("c.json", [])
    (tmp_path / "d.json").write_text(json.dumps({"summary": {}}), encoding="utf-8")
    names = e310.task_names(tmp_path)
    assert set(names) == {"a.json", "b.json"}, names
    assert e310.family(names["a.json"]) == "overlap" and e310.family(names["b.json"]) == "assembly"
    # an empty list is not a task list, so it is not read as a suite of no tasks
    assert e310.family([]) == "assembly"


def test_the_ordering_is_first_above_last_above_middle():
    assert e310.aligned([0.96, 0.91, 0.93]) is True
    assert e310.aligned([0.96, 0.93, 0.91]) is False          # last and middle the other way round
    assert e310.aligned([0.91, 0.96, 0.93]) is False          # the first is not the best
    assert e310.aligned([0.96, 0.93, 0.93]) is False          # a tie is not an ordering


def _reading(means=(0.96, 0.9168, 0.9345), fm=0.69, lm=0.54, fl=0.60,
             powered=99, powered_ok=89, families=None):
    families = families if families is not None else {
        "overlap": {"arms": 4715, "means": [0.9617, 0.9289, 0.9382], "first_above_middle": 0.67},
        "assembly": {"arms": 866, "means": [0.9537, 0.8507, 0.9142], "first_above_middle": 0.78}}
    return {"arms": 5581, "means": list(means), "first_above_middle": fm, "last_above_middle": lm,
            "first_above_last": fl, "artifacts_powered": powered, "powered_first_above_middle": powered_ok,
            "families": families, "suites": {}}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e310.judge(_reading())}
    for cid in ("W1", "W2", "W3", "W4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a different order, or a gap too small to matter, is W1's
    assert e310.judge(_reading(means=(0.96, 0.93, 0.91)))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e310.judge(_reading(means=(0.93, 0.9168, 0.9345)))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a paired share below the majority is W2's, and one below four fifths of the artifacts is W3's
    assert e310.judge(_reading(fm=0.55))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e310.judge(_reading(powered=100, powered_ok=70))[2]["verdict"].startswith("FALSIFIER FIRED")
    # a family where the ordering is absent is W4's, and so is having only one family to compare
    one = {"overlap": {"arms": 4715, "means": [0.9617, 0.9289, 0.9382], "first_above_middle": 0.67}}
    assert e310.judge(_reading(families=one))[3]["verdict"].startswith("FALSIFIER FIRED")
    two = dict(one, assembly={"arms": 866, "means": [0.91, 0.95, 0.93], "first_above_middle": 0.4})
    assert e310.judge(_reading(families=two))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e310.judge({"arms": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    r = e310.reading()
    assert r["arms"] >= 5000, r["arms"]
    assert e310.aligned(r["means"]), r["means"]
    assert r["means"][0] - r["means"][1] > 0.02, r["means"]
    assert r["first_above_middle"] >= 0.6, r["first_above_middle"]
    # the last beats the middle too, and the first beats the last, both more often than not; 0.597 is the exact
    # first-above-last share, which the module's report rounds to 60%
    assert r["first_above_last"] > 0.5 and r["last_above_middle"] > 0.5, (r["first_above_last"],
                                                                         r["last_above_middle"])
    assert r["artifacts_powered"] >= 90 and r["powered_first_above_middle"] / r["artifacts_powered"] >= 0.8, r
    # both families, and the overlap one is the larger: the tasks there are drawn per artifact
    assert set(r["families"]) == {"overlap", "assembly"}, sorted(r["families"])
    assert all(e310.aligned(v["means"]) for v in r["families"].values()), r["families"]
    assert r["families"]["overlap"]["arms"] > r["families"]["assembly"]["arms"], r["families"]
    claims = {x["id"]: x["verdict"] for x in e310.judge(r)}
    for cid in ("W1", "W2", "W3", "W4"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e310_the_position_effect.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert e310.aligned(d["means"]) and d["means"][0] - d["means"][1] > 0.02, d["means"]
    assert set(d["families"]) == {"overlap", "assembly"}, sorted(d["families"])
    assert all(e310.aligned(v["means"]) for v in d["families"].values()), d["families"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("W1", "W2", "W3", "W4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
