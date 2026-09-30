"""`e303` re-reads `e302`'s five metrics with the code arm counting definitions rather than mentions, so the tests
pin the prose stripper, the module-path rule, the two counters, both faces of the three claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e303_the_metrics_against_definitions as e303


def test_the_stripper_removes_documentation_and_keeps_definitions():
    src = (
        '"""A module whose docstring mentions decompose_forgetting."""\n'
        "# and a comment about decompose_forgetting\n"
        "NAME = 'decompose_forgetting'\n"          # a string literal is not code either
        "def decompose_forgetting(x):\n"
        "    return x\n"
    )
    code, ok = e303.strip_prose(src)
    assert ok is True
    # the docstring, the comment and the literal are gone, so the one survivor is the definition itself
    assert code.count("decompose_forgetting") == 1, code
    assert "NAME" in code and "'decompose_forgetting'" not in code, code
    # and a module that only mentions the name in prose keeps none of it
    prose_only = '"""decompose_forgetting is what we would use."""\nX = 1\n'
    assert "decompose_forgetting" not in e303.strip_prose(prose_only)[0]


def test_a_file_that_does_not_tokenise_is_flagged_rather_than_read_as_code():
    code, ok = e303.strip_prose("def broken(:\n    '''unterminated\n")
    assert ok is False and "broken" in code, (ok, code)


def test_the_module_path_is_the_reference_minus_its_attribute(tmp_path, monkeypatch):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "real.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert e303.module_path("pkg.real.thing") == "pkg/real.py"
    # the attribute is the last component, so a reference to a module that is not there does not resolve to its
    # package -- resolving the longest prefix that happens to be a file is the defect this rule replaces
    assert e303.module_path("pkg.absent.thing") == ""
    assert e303.module_path("thing") == ""


def _plan(metrics="average accuracy; decomposed forgetting; backward transfer"):
    return "# plan\n\n## The benchmark -- v0\n\nMetrics: " + metrics + ".\n\nMore.\n\n## Next\n\nx\n"


def test_the_two_counters_and_the_dangling_reference(tmp_path, monkeypatch):
    src = tmp_path / "code"
    src.mkdir()
    (src / "m.py").write_text(
        '"""Uses final_accuracy and defers to clfly.lgcl.absent.decompose_forgetting."""\n'
        "FIELD = 'final_accuracy'\n"
        "def final_accuracy(x):\n    return x\n",
        encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(_plan(), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    r = e303.readings(plan=plan, dirs=(src,))
    by = {x["spelling"]: x for x in r["spellings"]}
    assert by["final_accuracy"]["in_text"] > 0 and by["final_accuracy"]["in_code"] == 1, by["final_accuracy"]
    # a name the module only documents is prose only, and its dotted reference names a module that is not there
    assert by["decompose_forgetting"]["in_text"] == 1 and by["decompose_forgetting"]["in_code"] == 0, \
        by["decompose_forgetting"]
    assert [x["spelling"] for x in r["prose_only"]] == ["decompose_forgetting"], r["prose_only"]
    assert [d["names"] for d in r["dangling"]] == ["clfly/lgcl/absent.py"], r["dangling"]
    assert all(not d["resolves_to"] for d in r["dangling"]), r["dangling"]


def _reading(spellings=None, metrics=None, dangling=None):
    metrics = metrics or ["m0", "m1", "m2", "m3", "m4"]
    spellings = spellings if spellings is not None else [
        {"metric": "m0", "spelling": "a", "in_text": 5, "in_code": 1},
        {"metric": "m1", "spelling": "b", "in_text": 1, "in_code": 0}]
    dangling = dangling if dangling is not None else [
        {"module": "x.py", "spelling": "b", "writes": "clfly.lgcl.absent.b",
         "names": "clfly/lgcl/absent.py", "resolves_to": ""}]
    return {"spellings": spellings, "prose_only": [x for x in spellings if not x["in_code"]],
            "implemented": sorted({x["metric"] for x in spellings if x["in_code"]}),
            "unreadable": [], "dangling": dangling, "n_metrics": len(metrics), "metrics": metrics}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e303.judge(_reading())}
    assert j["R1"]["verdict"].startswith("MET"), j["R1"]
    assert j["R2"]["verdict"].startswith("MET"), j["R2"]        # four of five unimplemented
    assert j["R3"]["verdict"].startswith("MET"), j["R3"]
    # nothing in prose only is R1's falsifier
    only_code = [dict(x, in_code=1) for x in _reading()["spellings"]]
    assert e303.judge(_reading(spellings=only_code))[0]["verdict"].startswith("FALSIFIER FIRED")
    # four of five implemented is R2's, and a resolving module is R3's
    impl = [{"metric": m, "spelling": m, "in_text": 1, "in_code": 1} for m in ("m0", "m1", "m2", "m3")]
    assert e303.judge(_reading(spellings=impl))[1]["verdict"].startswith("FALSIFIER FIRED")
    resolved = [{"module": "x.py", "spelling": "b", "writes": "clfly.lgcl.bases.thing",
                 "names": "clfly/lgcl/bases.py", "resolves_to": "clfly/lgcl/bases.py"}]
    assert e303.judge(_reading(dangling=resolved))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e303.judge({"metrics": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_block_is_what_the_finding_says():
    r = e303.readings()
    assert r["metrics"] == ["average accuracy", "decomposed forgetting", "backward transfer",
                            "per-task observability spectrum", "pairwise task principal angles"], r["metrics"]
    prose = {(x["metric"], x["spelling"]) for x in r["prose_only"]}
    assert prose == {("decomposed forgetting", "decompose_forgetting"),
                     ("per-task observability spectrum", "observability")}, prose
    assert r["unreadable"] == [], r["unreadable"]
    # the metric the block prescribes is implemented only through the conventional form it rejects
    impl = {x["metric"]: [y["spelling"] for y in r["spellings"] if y["metric"] == x["metric"] and y["in_code"]]
            for x in r["spellings"] if x["in_code"]}
    assert impl["decomposed forgetting"] == ["mean_forgetting"], impl
    assert "backward transfer" not in impl and "per-task observability spectrum" not in impl, impl
    broken = [d for d in r["dangling"] if not d["resolves_to"]]
    assert [d["spelling"] for d in broken] == ["decompose_forgetting"], r["dangling"]
    assert broken[0]["names"] == "clfly/lgcl/metrics.py" and not Path(broken[0]["names"]).exists(), broken[0]
    claims = {x["id"]: x["verdict"] for x in e303.judge(r)}
    for cid in ("R1", "R2", "R3"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e303_the_metrics_against_definitions.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["metrics"]) == 5 and len(d["spellings"]) == 6, (d["metrics"], d["spellings"])
    assert [x["spelling"] for x in d["prose_only"]] == ["decompose_forgetting", "observability"], d["prose_only"]
    assert [x["spelling"] for x in d["dangling"] if not x["resolves_to"]] == ["decompose_forgetting"], d["dangling"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("R1", "R2", "R3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
