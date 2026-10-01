"""`e279` checks a universal about a configuration against the corpus, so the tests pin the population gatherer, both
faces of the three claims and the live tally.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from experiments import e279_every_one_of_the_77 as e279


def _art(path: Path, per_task=16, batch=16, drop=False):
    cfg = {"circuit_size": 800, "methods": "naive,replay"}
    if not drop:
        cfg["replay_per_task"] = per_task
        cfg["replay_batch"] = batch
    path.write_text(json.dumps({"config": cfg, "methods": {}}), encoding="utf-8")


def test_the_population_gathers_either_field_and_their_settings(tmp_path):
    _art(tmp_path / "a.json", 16, 16)
    _art(tmp_path / "b.json", 96, 8)
    _art(tmp_path / "c.json", 16, None)
    _art(tmp_path / "none.json", drop=True)
    rows = e279.population(tmp_path)
    assert len(rows) == 3, rows
    got = sorted((r["per_task"], r["batch"]) for r in rows if r["batch"] is not None)
    assert got == [(16, 16), (96, 8)], rows
    assert [r["batch"] for r in rows if r["artifact"] == "c.json"] == [None], rows


def _rows(*settings):
    return [{"artifact": f"a{i}.json", "per_task": p, "batch": b} for i, (p, b) in enumerate(settings)]


def test_the_three_claims_read_both_faces():
    rows = _rows(*([(16, 16)] * 120), *([(96, 8)] * 10))
    text = "the pool-96 / per-step-8 configuration ..."
    j = {r["id"]: r for r in e279.judge(rows, text)}
    for cid in ("W1", "W2", "W3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    assert "96/8: 10" in j["W2"]["measured"], j["W2"]
    # a population at the sentence's own size is W1's, and a clause everyone satisfies is W2's
    j = {r["id"]: r for r in e279.judge(_rows(*([(16, 16)] * 77)), text)}
    assert j["W1"]["verdict"].startswith("FALSIFIER FIRED"), j["W1"]
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]
    # and a paper that does not name the successor is W3's
    j = {r["id"]: r for r in e279.judge(_rows(*([(16, 16)] * 120), (96, 8)), "no successor named")}
    assert j["W3"]["verdict"].startswith("FALSIFIER FIRED"), j["W3"]
    assert e279.judge([], text)[0]["verdict"].startswith("REFUSED")


def test_the_live_population_is_twice_the_sentence_and_an_eighth_outside_the_clause():
    """The finding's numbers on the artifact: 167 artifacts against the sentence's 77, 144 inside the clause and 16
    recorded outside it, and the paper naming the successor configuration in the same passage."""
    p = Path("runs/e279_every_one_of_the_77.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["population_size"] >= 160, d["population_size"]
    assert d["settings"]["16/16"] >= 140, d["settings"]
    assert d["settings"].get("96/8", 0) >= 14, d["settings"]
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("W1", "W2", "W3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    # the ratio grows with the corpus, so the bound and not the three digits
    ratio = float(re.search(r"\((\d+\.\d+)x\)", claims["W1"]["measured"]).group(1))
    assert 1.5 <= ratio <= 6.0, claims["W1"]
    assert "sentence's 77" in claims["W1"]["measured"], claims["W1"]
    # the count outside the clause grows with the corpus, so the bound and not the two digits
    outside = int(re.search(r"recorded outside: (\d+)", claims["W2"]["measured"]).group(1))
    inside = re.search(r"inside the clause: (\d+)", claims["W2"]["measured"])
    assert outside >= 16 and inside and int(inside.group(1)) >= 140, claims["W2"]
