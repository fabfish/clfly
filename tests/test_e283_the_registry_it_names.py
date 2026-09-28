"""`e283` checks the paper's `e151` row: the registry's rows against its arms, the registry against the corpus at
forty replicates, and the extension's date against git. The tests pin the reading, both faces of the three claims, and
the live numbers as bounds, since a new run at forty replicates lands in the corpus and moves the counts.

The reference is the paper's row, which is `docs/paper/clfly-v1.md`'s line for `e151`:

    over the 27 arms it names
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e283_the_registry_it_names as e283


def _rows(n=2):
    return [{"label": f"r{i}", "a": {"path": "runs/a.json", "method": "naive"},
             "b": {"path": "runs/b.json", "method": "ewc"}} for i in range(n)]


def _artifact(tmp, name, arms):
    p = Path(tmp) / name
    p.write_text(json.dumps({"methods": {m: {"replicates": [{}] * n} for m, n in arms.items()}}), encoding="utf-8")
    return p.as_posix()


def _reading(registry_arms=22, forty=62, registered=14, unregistered=("runs/e116_r32_40reps.json",),
             named=("runs/e116_r32_40reps.json",), history=None, record="a record naming runs/e116_r32_40reps.json"):
    rows = [{"label": f"r{i}", "a": {"path": "runs/a.json", "method": "naive"},
             "b": {"path": "runs/b.json", "method": "ewc"}} for i in range(27)]
    return {"rows": rows, "arms": {(f"runs/a{i}.json", "naive") for i in range(registry_arms)},
            "corpus": {}, "n_forty_artifacts": forty, "n_forty_arms": 97, "n_registered": registered,
            "n_unregistered": forty - registered, "unregistered": list(unregistered),
            "n_unregistered_arms": 75, "named_by_record": list(named), "record": record,
            "history": history if history is not None else [{"sha": "a574d3bc", "date": "2026-09-24", "rows": 27},
                                                           {"sha": "59f85dd0", "date": "2026-09-24", "rows": 22}]}


def test_arms_are_the_distinct_pairs_behind_the_rows():
    rs = _rows(3)
    assert len(rs) == 3 and len(e283.arms(rs)) == 2, e283.arms(rs)
    # a row that is not a pair is not a contrast
    assert e283.judge(_reading())[0]["verdict"].startswith("MET")
    bad = _reading()
    bad["rows"] = [{"label": "r", "a": {"path": "runs/a.json", "method": "naive"}}]
    assert e283.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED")


def test_corpus_arms_reads_only_the_replicate_count_asked_for(tmp_path):
    a = _artifact(tmp_path, "a.json", {"naive": 40, "ewc": 39})
    b = _artifact(tmp_path, "b.json", {"replay": 40})
    _artifact(tmp_path, "c.json", {"naive": 3})
    (Path(tmp_path) / "d.json").write_text("not json", encoding="utf-8")
    (Path(tmp_path) / "e.json").write_text(json.dumps({"methods": [{"method": "naive", "replicates": [{}] * 40}]}),
                                           encoding="utf-8")
    got = e283.corpus_arms(tmp_path, 40)
    # the 39-replicate arm is out, the unparseable file is skipped, and a list-shaped `methods` is not a dict
    assert got == {a: ["naive"], b: ["replay"]}, got
    assert e283.corpus_arms(tmp_path, 39) == {a: ["ewc"]}, e283.corpus_arms(tmp_path, 39)


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e283.judge(_reading())}
    for cid in ("U1", "U2", "U3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # 27 rows over 27 arms is not the sentence's pair
    j = {r["id"]: r for r in e283.judge(_reading(registry_arms=27))}
    assert j["U1"]["verdict"].startswith("FALSIFIER FIRED"), j["U1"]
    # a registry that covers its population, or misses only what the record never names
    j = {r["id"]: r for r in e283.judge(_reading(registered=31))}
    assert j["U2"]["verdict"].startswith("FALSIFIER FIRED"), j["U2"]
    j = {r["id"]: r for r in e283.judge(_reading(named=(), record="no path here"))}
    assert j["U2"]["verdict"].startswith("FALSIFIER FIRED"), j["U2"]
    # an extension that was never 22 rows, or landed on another day
    j = {r["id"]: r for r in e283.judge(_reading(history=[{"sha": "x", "date": "2026-09-24", "rows": 27}]))}
    assert j["U3"]["verdict"].startswith("FALSIFIER FIRED"), j["U3"]
    j = {r["id"]: r for r in e283.judge(_reading(history=[{"sha": "x", "date": "2026-09-25", "rows": 22},
                                                         {"sha": "y", "date": "2026-09-25", "rows": 27}]))}
    assert j["U3"]["verdict"].startswith("FALSIFIER FIRED"), j["U3"]
    assert e283.judge({"rows": []})[0]["verdict"].startswith("REFUSED")
    assert e283.judge(None)[0]["verdict"].startswith("REFUSED")


def test_the_git_leg_reads_the_module_history():
    hist = e283.registry_sizes()
    assert hist and all(set(h) == {"sha", "date", "rows"} for h in hist), hist
    assert any(h["rows"] == 22 for h in hist), hist
    assert any(h["rows"] == 27 and h["date"] == "2026-09-24" for h in hist), hist


def test_the_live_registry_and_corpus_are_what_the_finding_says():
    rs = e283.rows()
    assert len(rs) == 27 and len(e283.arms(rs)) == 22, (len(rs), len(e283.arms(rs)))
    reg_paths = {p for p, _ in e283.arms(rs)}
    corpus = e283.corpus_arms(n=40)
    assert len(corpus) >= 60, len(corpus)
    named = [p for p in corpus if p in reg_paths]
    assert len(named) <= len(corpus) / 2, (len(named), len(corpus))
    text = e283.record_text()
    unnamed_named = [p for p in corpus if p not in reg_paths and p in text]
    assert len(unnamed_named) >= 5, unnamed_named


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e283_the_registry_it_names.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["registry"]["rows"] == 27, d["registry"]
    # the nouns are exchanged: the rows are contrasts and the arms are fewer
    assert d["registry"]["arms"] == 22 and d["registry"]["artifacts_named"] == 14, d["registry"]
    # the band, not the digit: a forty-replicate run landing moves the corpus counts
    c = d["corpus"]
    live = e283.corpus_arms(n=40)
    assert abs(c["artifacts_with_a_forty_replicate_arm"] - len(live)) <= 0.1 * len(live), (c, len(live))
    assert c["named_in_the_registry"] <= c["artifacts_with_a_forty_replicate_arm"] / 2, c
    assert c["not_named"] == c["artifacts_with_a_forty_replicate_arm"] - c["named_in_the_registry"], c
    assert len(c["unnamed_artifacts_the_record_names"]) >= 5, c
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("U1", "U2", "U3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert any(h["rows"] == 22 for h in d["history"]) and any(h["rows"] == 27 for h in d["history"]), d["history"]
