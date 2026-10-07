"""`e452` censuses what a fresh clone would report, so the tests pin both faces of the five claims and the refusal when
the gate's entry list is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e452_what_a_fresh_clone_reports as e452

#: the shape of the census: fixed true values, so a mutation under test moves one of them
SPANS = {"entries": 230, "pytest": 1, "python": 229, "dependent": 157, "source_only": 72, "refusing": 144,
         "no_refusal": 13, "dependent_share": 0.686, "refusal_share": 0.917, "json_out": 206,
         "files": 4164, "mib": 947.4, "largest": "e427.json", "largest_mib": 5.0, "over_big": 0, "missing": 0}


def _doc(spans=None, missing=None, no_refusal=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "entries": [], "by_kind": {}, "dependent": [], "source_only": [],
                "no_refusal": [], "missing": [], "corpus": {}, "spans": {}}
    s = dict(SPANS if spans is None else spans)
    return {"ok": True, "reason": None, "entries": [{"name": "x"}], "by_kind": {}, "dependent": ["a"],
            "source_only": [], "no_refusal": list(no_refusal or []), "missing": list(missing or []),
            "corpus": {}, "spans": s}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e452.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the ledger carried, an artifact-dependent gate and a corpus larger than a repository
    j = _judge()
    for cid in ("CY1", "CY2", "CY3", "CY4", "CY5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # CY1: a module the entry list names that is not on disk
    assert _judge(missing=["experiments/gone.py"])["CY1"].startswith("FALSIFIER")

    # CY2: a gate that is mostly independent of the corpus, and one between the bars
    assert _judge(spans={**SPANS, "dependent_share": 0.200})["CY2"].startswith("FALSIFIER")
    assert _judge(spans={**SPANS, "dependent_share": 0.400})["CY2"].startswith("NULL")

    # CY3: a gate with almost no source-only entries, and one between the bars
    assert _judge(spans={**SPANS, "source_only": 2})["CY3"].startswith("FALSIFIER")
    assert _judge(spans={**SPANS, "source_only": 5})["CY3"].startswith("NULL")

    # CY4: a gate where most dependent modules have no refusal, and one between the bars
    assert _judge(spans={**SPANS, "refusal_share": 0.500})["CY4"].startswith("FALSIFIER")
    assert _judge(spans={**SPANS, "refusal_share": 0.700})["CY4"].startswith("NULL")

    # CY5: a corpus that would fit a repository, and one between the bars
    assert _judge(spans={**SPANS, "mib": 10.0, "files": 100})["CY5"].startswith("FALSIFIER")
    assert _judge(spans={**SPANS, "mib": 50.0, "files": 500})["CY5"].startswith("NULL")

    #: the gate's entry list absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e452.judge(_doc(ok=False)))


def test_the_paths_and_the_bars_are_registered():
    #: the gate, the corpus and the two literals the classification reads
    assert e452.GATES.name == "gates.sh" and e452.GATES.parent.name == "tools"
    assert e452.RUNS.name == "runs"
    assert e452.ARTIFACT == "runs/" and e452.REFUSAL == "REFUSED"
    assert e452.MODULE.search("python -m experiments.e438_x --json-out runs/e438_y.json").group(1) == "experiments.e438_x"
    assert e452.MODULE.search("uv run pytest -q") is None
    assert (e452.CLAIM_SHARE, e452.CLAIM_FLOOR) == (0.5, 0.25)
    assert (e452.SOURCE_ONLY_BAR, e452.SOURCE_ONLY_FLOOR) == (10, 3)
    assert (e452.REFUSAL_SHARE, e452.REFUSAL_FLOOR) == (0.8, 0.6)
    assert e452.TOTAL_BAR == 100 * 1024 * 1024 and e452.TOTAL_FLOOR == 20 * 1024 * 1024
    assert e452.FILE_BAR == 1000


def test_the_live_census_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e452_what_a_fresh_clone_reports.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e452.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: every entry parses and the split is the gate's own
    s = d["spans"]
    assert s["entries"] == s["pytest"] + s["python"], s
    assert s["dependent"] + s["source_only"] == s["python"], s
    assert s["refusing"] + s["no_refusal"] == s["dependent"], s
    assert s["refusing"] == len(d["dependent"]) - len(d["no_refusal"]), (len(d["dependent"]), len(d["no_refusal"]))
    assert s["missing"] == len(d["missing"]), (s["missing"], d["missing"])
    assert not d["missing"], d["missing"]
    assert d["corpus"]["files"] >= 1 and d["corpus"]["bytes"] >= 1, d["corpus"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
