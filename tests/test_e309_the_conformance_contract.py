"""`e309` reads the corpus against the benchmark's conformance contract, so the tests pin each required field, the
block structure the census reports, both faces of the four claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from clfly.bench import conformance
from experiments import e309_the_conformance_contract as e309


def _payload(**drop):
    """A payload carrying all eight fields, with any of them removed or emptied by name."""
    p = {"tasks": [{"name": "t0"}, {"name": "t1"}], "config": {"seed0": 0},
         "evaluation_noise": {"n_eval": 144}, "readout": {"subset_sha1": "abc"},
         "code_revision": {"commit": "deadbeef"},
         "methods": {"naive": {"replicates": [{"final_accuracy": 0.9, "mean_forgetting": 0.1,
                                               "retention": [[1.0, None], [0.9, 0.9]]}]}}}
    for k, v in drop.items():
        if v is None:
            p.pop(k, None)
        else:
            p[k] = v
    return p


def test_each_required_field_is_read_where_the_corpus_keeps_it():
    assert conformance.carries(_payload()) == list(conformance.NAMES), conformance.carries(_payload())
    assert conformance.conformant(_payload()) is True
    # one field at a time, by the payload key that supplies it, so a predicate reading the wrong key is caught
    for name, drop in (("task list", {"tasks": []}), ("a seed", {"config": {}}),
                       ("an eval size", {"evaluation_noise": {}}), ("a read-out draw", {"readout": None}),
                       ("a code revision", {"code_revision": None, "environment": {}})):
        got = conformance.carries(_payload(**drop))
        assert name not in got, (name, got)
        assert len(got) == len(conformance.FIELDS) - 1, (name, got)
    # the three per-replicate fields are read off the arms rather than the top level
    bare = _payload()
    bare["methods"] = {"naive": {"replicates": [{}]}}
    assert conformance.carries(bare) == list(conformance.NAMES[:3]) + ["a read-out draw", "a code revision"], \
        conformance.carries(bare)
    # and the environment's torch version stands in for a revision when code_revision is absent
    assert conformance.has_revision({"environment": {"torch_version": "2.14.0+cpu"}}) is True
    assert conformance.has_revision({"code_revision": {"commit": "x"}}) is True


def test_the_census_reports_the_blocks_and_not_only_the_totals(tmp_path):
    (tmp_path / "full.json").write_text(json.dumps(_payload()), encoding="utf-8")
    half = _payload()
    for k in ("evaluation_noise", "readout", "code_revision"):
        half.pop(k, None)
    (tmp_path / "blocked.json").write_text(json.dumps(half), encoding="utf-8")
    (tmp_path / "seed.json").write_text(json.dumps({"config": {"seed0": 0}}), encoding="utf-8")
    (tmp_path / "empty.json").write_text(json.dumps({"summary": {}}), encoding="utf-8")
    c = conformance.census(tmp_path)
    assert c["artifacts"] == 4 and c["conformant"] == 1, c
    assert dict(c["by_count"]) == {8: 1, 5: 1, 1: 1, 0: 1}, c["by_count"]
    assert c["gaps"] == [], c["gaps"]
    assert [b["n"] for b in c["blocks"]] == [1, 1, 1, 1], c["blocks"]
    # a payload in the middle is what K4 would fire on
    (tmp_path / "middle.json").write_text(json.dumps({"tasks": [{"name": "t0"}], "config": {"seed0": 0}}),
                                          encoding="utf-8")
    assert conformance.census(tmp_path)["gaps"] == [2], conformance.census(tmp_path)["gaps"]


def _reading(artifacts=547, scarce="a read-out draw", scarce_n=76, conformant=76, gaps=()):
    fields = list(conformance.NAMES)
    per = {n: 200 for n in fields}
    per[scarce] = scarce_n
    return {"artifacts": artifacts, "fields": fields, "per_field": per,
            "rates": {n: v / artifacts for n, v in per.items()}, "scarcest": scarce,
            "by_count": {0: 158, 1: 242, 5: 11, 6: 28, 7: 32, 8: conformant},
            "blocks": [], "conformant": conformant, "gaps": list(gaps)}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e309.judge(_reading())}
    for cid in ("K1", "K2", "K3", "K4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # every field carried by a quarter or more is K1's, and another field being scarcest is K2's
    assert e309.judge(_reading(scarce_n=200))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e309.judge(_reading(scarce="a code revision"))[1]["verdict"].startswith("FALSIFIER FIRED")
    # a conformant quarter is K3's, and one artifact in the middle is K4's
    assert e309.judge(_reading(conformant=200))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e309.judge(_reading(gaps=(3,)))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e309.judge({"artifacts": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    r = e309.reading()
    assert r["artifacts"] >= 500, r["artifacts"]
    assert r["scarcest"] == "a read-out draw", r["scarcest"]
    assert r["rates"]["a read-out draw"] < 0.25, r["rates"]["a read-out draw"]
    assert r["conformant"] / r["artifacts"] < 0.25, r["conformant"]
    assert r["gaps"] == [], r["gaps"]
    # the blocks: nothing, the seed alone, and the result block or most of it
    counts = set(r["by_count"])
    assert {0, 1} <= counts and all(c >= 5 for c in counts if c > 1), r["by_count"]
    claims = {x["id"]: x["verdict"] for x in e309.judge(r)}
    for cid in ("K1", "K2", "K3", "K4"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e309_the_conformance_contract.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["scarcest"] == "a read-out draw" and d["gaps"] == [], (d["scarcest"], d["gaps"])
    assert d["conformant"] / d["artifacts"] < 0.25, d["conformant"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("K1", "K2", "K3", "K4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
