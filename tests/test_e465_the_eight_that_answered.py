"""`e465` runs the eight that answered on an empty corpus twice, with and without it, so the tests pin both faces of the
four claims and the refusal when the sweep or the copy is not there.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e465_the_eight_that_answered as e465

#: the shape of the comparison: eight modules, seven of which record verdicts and five of which move
EIGHT = [f"experiments/e46{i}.py" for i in range(8)]
FILES = 1357


def _arm(claims, keys=("claims", "n"), crashed=False, timeout=False, exit_code=0, seconds=1.0):
    return {"exit": exit_code, "timeout": timeout, "crashed": crashed, "seconds": seconds,
            "claims": dict(claims), "keys": list(keys), "refused": False, "tail": ""}


def _entry(moved=(), comparable=True, same=None, keys_equal=True, corpus_claims=None, clone_claims=None,
           crashed=False, timeout=False, gate=None):
    base = {"A": "MET", "B": "MET"}
    c = dict(corpus_claims if corpus_claims is not None else base)
    k = dict(clone_claims if clone_claims is not None else base)
    for mid in moved:
        k[mid] = "FALSIFIER FIRED"
    if not comparable:
        c, k = {}, {}
    if same is not None:
        k = dict(c) if same else k
    return {"corpus": _arm(c, crashed=crashed, timeout=timeout), "clone": _arm(k, crashed=crashed, timeout=timeout),
            "gate": dict(gate or c), "keys_equal": keys_equal, "comparable": comparable,
            "same_verdicts": c == k, "moved": sorted(m for m in set(c) | set(k) if c.get(m) != k.get(m))}


def _doc(entries=None, files=FILES, carries_runs=False, ok=True, reason="the sweep is not there"):
    if not ok:
        return {"ok": False, "reason": reason, "eight": [], "entries": {}, "tree": {}, "gate": {}, "spans": {}}
    if entries is None:
        entries = {m: _entry(moved=("B",) if i < 3 else ()) for i, m in enumerate(EIGHT)}
    ents = entries
    unchanged = sorted(m for m, e in ents.items() if e["same_verdicts"])
    changed = sorted(m for m, e in ents.items() if not e["same_verdicts"])
    comparable = [m for m, e in ents.items() if e["comparable"]]
    gate_have = [m for m, e in ents.items() if e["gate"]]
    return {"ok": True, "reason": None, "eight": sorted(ents), "entries": ents, "gate": {},
            "tree": {"files": files, "fingerprint_sha1": "71952c85ea48", "carries_runs": carries_runs},
            "spans": {"eight": len(ents),
                      "with_artifact": sum(1 for e in ents.values() if e["corpus"]["keys"] and e["clone"]["keys"]),
                      "with_claims": sum(1 for e in ents.values() if e["corpus"]["claims"] and e["clone"]["claims"]),
                      "comparable": comparable,
                      "keys_equal": sum(1 for e in ents.values() if e["keys_equal"]),
                      "unchanged": unchanged, "changed": changed,
                      "unchanged_share": len(unchanged) / len(ents) if ents else 0.0,
                      "crashed": sorted(m for m, e in ents.items() if e["corpus"]["crashed"] or e["clone"]["crashed"]),
                      "timed_out": sorted(m for m, e in ents.items()
                                          if e["corpus"]["timeout"] or e["clone"]["timeout"]),
                      "gate_compared": sorted(gate_have),
                      "gate_agree": sorted(m for m in gate_have if ents[m]["gate"] == ents[m]["corpus"]["claims"]),
                      "files": files, "fingerprint": "71952c85ea48", "seconds": 11.0}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e465.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: eight modules run twice, five of them moving a verdict, and the corpus arm matching the gate
    j = _judge()
    for cid in ("RB1", "RB2", "RB3", "RB4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # RB1: an arm with no artifact, a pair whose keys differ, and a module that records no verdicts in both arms
    assert _judge(entries={EIGHT[0]: _entry(keys_equal=False)})["RB1"].startswith("FALSIFIER")
    assert _judge(entries={EIGHT[0]: _entry(comparable=False)})["RB1"].startswith("FALSIFIER")

    # RB2: a share under the floor, and one between the bars
    few_unchanged = {m: _entry(moved=("B",)) for m in EIGHT}
    few_unchanged[EIGHT[0]] = _entry()
    assert _judge(entries=few_unchanged)["RB2"].startswith("FALSIFIER")
    mid = {m: _entry(moved=("B",)) for m in EIGHT[:5]}
    mid.update({m: _entry() for m in EIGHT[5:]})
    assert _judge(entries=mid)["RB2"].startswith("NULL")

    # RB3: nothing moves at all
    assert _judge(entries={m: _entry() for m in EIGHT})["RB3"].startswith("FALSIFIER")

    # RB4: a corpus arm that disagrees with the gate artifact, and no gate artifact to compare with
    disagree = {m: _entry(moved=("B",) if i < 5 else ()) for i, m in enumerate(EIGHT)}
    disagree[EIGHT[0]]["gate"] = {"A": "FALSIFIER FIRED"}
    assert _judge(entries=disagree)["RB4"].startswith("FALSIFIER")
    assert _judge(entries={m: {**_entry(), "gate": {}} for m in EIGHT})["RB4"].startswith("NULL")

    #: a sweep or a copy that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e465.judge(_doc(ok=False)))


def test_the_bounds_and_the_paths_are_registered():
    assert e465.SWEEP.name == "e464_the_fresh_clone_simulated.json"
    assert e465.GATES.name == "gates.sh"
    assert (e465.HALF, e465.QUARTER) == (0.5, 0.25)
    assert e465.TIMEOUT > 0 and e465.WORKERS >= 1
    #: a gate entry's path is not a module name, and passing it to `-m` failed silently once
    assert e465.module_of("experiments/e200_draw_confound_audit.py") == "experiments.e200_draw_confound_audit"
    try:
        e465.module_of("e200_draw_confound_audit.py")
    except ValueError:
        pass
    else:
        raise AssertionError("a path without a package should be refused rather than passed to -m")
    #: the answering set is `e464`'s and not a second parse of the gate
    assert e465.e464.__name__.endswith("e464_the_fresh_clone_simulated")


def test_the_verdicts_are_read_as_classes():
    assert e465.verdicts({"claims": [{"id": "A", "verdict": "MET -- because"}, {"id": "B",
                                                                               "verdict": "REFUSED"}]}) == \
        {"A": "MET", "B": "REFUSED"}
    assert e465.verdicts({}) == {} and e465.verdicts(None) == {}
    assert e465.verdicts({"claims": [{"id": "A"}, {"no_id": 1}, "junk"]}) == {"A": ""}


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e465_the_eight_that_answered.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e465.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the eight are the sweep's own answering set, and the counts that grow with the gate are read as floors
    assert d["spans"]["eight"] >= 1, d["spans"]
    assert sorted(d["entries"]) == d["eight"], (sorted(d["entries"]), d["eight"])
    assert d["tree"]["carries_runs"] is False, d["tree"]
    assert d["tree"]["files"] >= 250, d["tree"]
    assert len(d["spans"]["unchanged"]) + len(d["spans"]["changed"]) == d["spans"]["eight"], d["spans"]
    for m, e in d["entries"].items():
        assert e["keys_equal"] == (e["corpus"]["keys"] == e["clone"]["keys"] and bool(e["corpus"]["keys"])), m
        assert e["same_verdicts"] == (e["corpus"]["claims"] == e["clone"]["claims"]), m
        assert e["comparable"] == bool(e["corpus"]["claims"] and e["clone"]["claims"]), m
        assert e["moved"] == sorted(k for k in set(e["corpus"]["claims"]) | set(e["clone"]["claims"])
                                    if e["corpus"]["claims"].get(k) != e["clone"]["claims"].get(k)), m
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
