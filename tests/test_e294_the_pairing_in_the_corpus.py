"""`e294` reads the corpus's matched-pair blocks as a population, so the tests pin the reader, the summary arithmetic,
both faces of the three claims, and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e294_the_pairing_in_the_corpus as e294


def _art(path: Path, blocks=None):
    payload = {"matched_pair": blocks if blocks is not None else {
        "final_accuracy": {"n": 40, "corr": 0.5, "sem_paired": 0.003, "sem_unpaired": 0.004,
                           "sigma_paired": 2.5, "sigma_unpaired": 1.8, "delta": 0.01}}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_reader_takes_only_usable_blocks(tmp_path):
    _art(tmp_path / "a.json")
    _art(tmp_path / "b.json", blocks={"final_accuracy": {"n": 40, "corr": -0.4, "sem_paired": 0.005,
                                                         "sem_unpaired": 0.004, "sigma_paired": 0.5,
                                                         "sigma_unpaired": 0.4, "delta": -0.002}})
    # no matched pair, a block without a correlation, and a block with two replicates
    _art(tmp_path / "c.json", blocks=None)
    (tmp_path / "c.json").write_text(json.dumps({"methods": {}}), encoding="utf-8")
    _art(tmp_path / "d.json", blocks={"final_accuracy": {"n": 40, "sem_paired": 0.003}})
    _art(tmp_path / "e.json", blocks={"final_accuracy": {"n": 2, "corr": 0.9, "sem_paired": 0.001,
                                                         "sem_unpaired": 0.002}})
    (tmp_path / "f.json").write_text("not json", encoding="utf-8")
    rows = e294.blocks(tmp_path)
    assert len(rows) == 2, rows
    assert {r["corr"] for r in rows} == {0.5, -0.4}, rows


def test_the_summary_counts_and_the_resolution():
    rows = [{"artifact": "a", "metric": "m", "n": 40, "corr": 0.5, "sem_paired": 0.003, "sem_unpaired": 0.004,
             "sigma_paired": 2.5, "sigma_unpaired": 1.8, "delta": 0.01},
            {"artifact": "b", "metric": "m", "n": 40, "corr": -0.4, "sem_paired": 0.005, "sem_unpaired": 0.004,
             "sigma_paired": 0.5, "sigma_unpaired": 0.4, "delta": -0.002}]
    s = e294.summary(rows)
    assert (s["blocks"], s["positive"], s["negative"], s["paired_smaller"]) == (2, 1, 1, 1), s
    assert s["resolved_paired"] == 1 and s["resolved_unpaired"] == 0, s
    assert abs(s["median_ratio"] - 1.0) < 1e-9, s["median_ratio"]   # the median of 0.75 and 1.25
    assert s["by_n"][40]["blocks"] == 2, s["by_n"]


def _reading(summary=None, blocks=None):
    s = {"blocks": 10, "artifacts": 5, "positive": 8, "negative": 2, "median_corr": 0.3, "paired_smaller": 8,
         "median_ratio": 0.84, "median_predicted": 0.84, "resolved_paired": 4, "resolved_unpaired": 1, "by_n": {}}
    s.update(summary or {})
    rows = blocks if blocks is not None else [
        {"artifact": "a", "metric": "m", "n": 40, "corr": 0.4, "sem_paired": 0.003, "sem_unpaired": 0.004,
         "sigma_paired": 2.5, "sigma_unpaired": 1.8},
        {"artifact": "b", "metric": "m", "n": 40, "corr": -0.4, "sem_paired": 0.005, "sem_unpaired": 0.004,
         "sigma_paired": 0.5, "sigma_unpaired": 0.4}]
    return {"blocks": rows, "summary": s}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e294.judge(_reading())}
    for cid in ("P1", "P2", "P3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a population with few positive correlations is P1's falsifier
    j = {r["id"]: r for r in e294.judge(_reading({"positive": 3, "paired_smaller": 3}))}
    assert j["P1"]["verdict"].startswith("FALSIFIER FIRED"), j["P1"]
    # no negative correlation is P2's
    j = {r["id"]: r for r in e294.judge(_reading({"negative": 0},
                                                blocks=[{"artifact": "a", "metric": "m", "n": 40, "corr": 0.4,
                                                         "sem_paired": 0.003, "sem_unpaired": 0.004}]))}
    assert j["P2"]["verdict"].startswith("FALSIFIER FIRED"), j["P2"]
    # a paired count that is not larger is P3's
    j = {r["id"]: r for r in e294.judge(_reading({"resolved_paired": 1, "resolved_unpaired": 3}))}
    assert j["P3"]["verdict"].startswith("FALSIFIER FIRED"), j["P3"]
    assert e294.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e294.judge({"blocks": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    rows = e294.blocks()
    s = e294.summary(rows)
    assert s["blocks"] >= 60 and s["artifacts"] >= 30, (s["blocks"], s["artifacts"])
    assert s["positive"] >= 50 and s["negative"] >= 5, (s["positive"], s["negative"])
    assert s["positive"] + s["negative"] <= s["blocks"], s
    assert 0.15 < s["median_corr"] < 0.45, s["median_corr"]
    assert s["paired_smaller"] >= 50, s["paired_smaller"]
    assert s["resolved_paired"] > s["resolved_unpaired"], (s["resolved_paired"], s["resolved_unpaired"])
    # every negative correlation has the paired sem the larger, which is the mechanism P2 names
    for x in rows:
        if x["corr"] < 0 and x["sem_paired"] and x["sem_unpaired"]:
            assert x["sem_paired"] > x["sem_unpaired"], x
    assert min(x["corr"] for x in rows) < -0.4, min(x["corr"] for x in rows)


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e294_the_pairing_in_the_corpus.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    s = d["summary"]
    assert s["blocks"] >= 64 and s["positive"] >= 57 and s["negative"] >= 7, s
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("P1", "P2", "P3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "12 under the paired sem against 3" in claims["P3"]["measured"], claims["P3"]
