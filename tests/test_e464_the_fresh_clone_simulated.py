"""`e464` runs the gate's own entries against a tree with no corpus, so the tests pin both faces of the four claims
and the refusal when the gate or the tree is not there.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e464_the_fresh_clone_simulated as e464

#: the shape of a sweep: a big copy, most dependent entries declining, the ledger naming the rest
FILES = 1354
DEPENDENT = 200
SOURCE_ONLY = 39
NO_REFUSAL = 13


def _entry(path, declined, answered, ledger, refused=True, exit_code=0, timeout=False):
    return {"name": path.split("/")[-1], "module": path[:-3].replace("/", "."), "path": path,
            "declined": declined, "answered": answered, "ledger": ledger,
            "refused": refused, "exit": exit_code, "timeout": timeout, "seconds": 1.0, "tail": ""}


def _doc(files=FILES, dependent=DEPENDENT, source_only=SOURCE_ONLY, dependent_declined=None, source_declined=0,
         no_refusal=NO_REFUSAL, outside=None, carries_runs=False, missing=None, ok=True, reason="the gate is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "tree": {}, "entries": [], "ledger": {}, "spans": {}}
    if dependent_declined is None:
        dependent_declined = int(0.95 * dependent)
    dependent_share = dependent_declined / dependent if dependent else 0.0
    source_share = source_declined / source_only if source_only else 0.0
    answered = max(0, dependent - dependent_declined)
    return {"ok": True, "reason": None,
            "tree": {"files": files, "fingerprint_sha1": "10de40d7663d", "carries_runs": carries_runs,
                     "missing": missing or []},
            "entries": [{"path": f"experiments/e{i}.py", "answered": False} for i in range(2)],
            "ledger": {"no_refusal": [f"experiments/led{i}.py" for i in range(no_refusal)],
                       "dependent": [f"experiments/dep{i}.py" for i in range(dependent - no_refusal)],
                       "source_only": [f"experiments/src{i}.py" for i in range(source_only)]},
            "spans": {"entries": dependent + source_only + 1, "python": dependent + source_only,
                      "dependent": dependent, "source_only": source_only,
                      "declined": dependent_declined + source_declined,
                      "refused": dependent_declined, "nonzero": 0, "timeout": 0, "crashed": 0,
                      "answered": answered, "answered_paths": [],
                      "dependent_declined": dependent_declined, "dependent_share": dependent_share,
                      "source_declined": source_declined, "source_share": source_share,
                      "answered_dependent": [f"experiments/ans{i}.py" for i in range(2)],
                      "outside_ledger": outside if outside is not None else [],
                      "seconds": 1.0, "slowest": 2.0, "files": files, "fingerprint": "10de40d7663d"}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e464.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: a corpus-less copy of the repository, most dependent entries declining, nothing outside the ledger
    j = _judge()
    for cid in ("CL1", "CL2", "CL3", "CL4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # CL1: a copy that carries the corpus, one that is missing a gate module, and one that is too small
    assert _judge(carries_runs=True)["CL1"].startswith("FALSIFIER")
    assert _judge(missing=["experiments/e1.py"])["CL1"].startswith("FALSIFIER")
    assert _judge(files=100)["CL1"].startswith("FALSIFIER")

    # CL2: too few dependent entries declining, and one between the bars
    assert _judge(dependent_declined=100)["CL2"].startswith("FALSIFIER")
    assert _judge(dependent_declined=140)["CL2"].startswith("NULL")
    assert _judge(dependent=0)["CL2"].startswith("REFUSED")

    # CL3: an entry that answers and that the ledger does not name
    assert _judge(outside=["experiments/e9.py"])["CL3"].startswith("FALSIFIER")
    assert _judge(outside=[])["CL3"].startswith("MET")

    # CL4: too many entries that do not read the corpus declining, and one between the bars
    assert _judge(source_declined=20)["CL4"].startswith("FALSIFIER")
    assert _judge(source_declined=12)["CL4"].startswith("NULL")
    assert _judge(source_only=0)["CL4"].startswith("REFUSED")

    #: a gate or a tree that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e464.judge(_doc(ok=False)))


def test_the_bounds_and_the_exclusions_are_registered():
    assert e464.GATES.name == "gates.sh"
    assert set(e464.EXCLUDED) >= {"runs", ".git", ".venv", "__pycache__"}, e464.EXCLUDED
    assert (e464.FILES_BAR, e464.FILES_FLOOR) == (500, 250)
    assert (e464.DECLINE_SHARE, e464.DECLINE_FLOOR) == (0.8, 0.6)
    assert (e464.CONTROL_SHARE, e464.CONTROL_FLOOR) == (0.2, 0.4)
    assert e464.REFUSAL == "REFUSED" and e464.ARTIFACT == "runs/"
    assert e464.TIMEOUT > 0 and e464.WORKERS >= 1
    #: the ledger this unit is checked against is `e452`'s own reading and not a second parser
    assert e464.e452.__name__.endswith("e452_what_a_fresh_clone_reports")


def test_the_ignored_names_are_the_corpus_and_the_toolchain():
    for name in ("runs", ".git", ".venv", "__pycache__", ".pytest_cache"):
        assert e464._ignored(name), name
    for name in ("experiments", "tests", "docs", "tools", "clfly"):
        assert not e464._ignored(name), name


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e464_the_fresh_clone_simulated.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e464.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the copy and the sweep are structural; the counts that grow with the repository are read as floors
    assert d["tree"]["files"] >= e464.FILES_FLOOR, d["tree"]
    assert d["tree"]["carries_runs"] is False, d["tree"]
    assert d["tree"]["missing"] == [], d["tree"]
    assert d["spans"]["entries"] >= d["spans"]["python"] >= 1, d["spans"]
    assert d["spans"]["dependent"] + d["spans"]["source_only"] == d["spans"]["python"], d["spans"]
    assert 0.0 <= d["spans"]["dependent_share"] <= 1.0, d["spans"]
    assert 0.0 <= d["spans"]["source_share"] <= 1.0, d["spans"]
    assert len(d["entries"]) == d["spans"]["python"], (len(d["entries"]), d["spans"])
    for e in d["entries"]:
        assert e["ledger"] in ("no refusal path", "refuses", "does not read runs", "not in the ledger"), e
        assert e["declined"] == bool(e["refused"] or e["timeout"] or e["exit"] not in (0, None)), e
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
