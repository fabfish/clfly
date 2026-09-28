"""`e277` checks the paper's counts against the corpus, so the tests pin the pattern extraction, the noun inference,
both faces of the three claims and the live ratios.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from experiments import e277_a_count_is_not_a_scope as e277


def _art(path: Path, *, rate_network=True, fisher=32):
    cfg = {"circuit_size": 800, "iters": 500, "methods": "naive,ewc", "fisher_batches": fisher} if rate_network \
        else {"basis": "side", "seeds": 3}
    path.write_text(json.dumps({"config": cfg, "methods": {"naive": {"replicates": []}}}), encoding="utf-8")


def test_the_rate_network_signature_and_the_corpus_counts(tmp_path):
    _art(tmp_path / "a.json")
    _art(tmp_path / "b.json", fisher=128)
    _art(tmp_path / "ladder.json", rate_network=False)
    have = e277.corpora(tmp_path)
    assert have["artifacts"] == 3 and have["rate-network runs"] == 2, have
    assert {r["artifact"] for r in have["_rate_network"]} == {"a.json", "b.json"}, have["_rate_network"]
    assert have["findings"] >= 100, have["findings"]


def test_the_patterns_extract_a_count_and_its_noun_including_the_every_form():
    text = ("Some prose. 13 of 216 artifacts were refused by the parser. And the 25 rate-network runs used 8 or 32, "
            "so every one of the 25 is covered. A sentence with no count.")
    found = e277.counts(text)
    matched = {c["matched"] for c in found}
    assert "13 of 216 artifacts" in matched and "the 25 rate-network runs" in matched and "every one of the 25" in matched, matched
    of = next(c for c in found if c["matched"] == "13 of 216 artifacts")
    assert of["noun"] == "artifacts" and of["numbers"] == ["13", "216"], of
    every = next(c for c in found if c["matched"] == "every one of the 25")
    assert every["noun"] == "rate-network runs", "the noun comes from the sentence, not the match"
    assert e277.counts("Nothing countable here.") == []


def _found(stated=25, noun="rate-network runs", form="every", statement="every one of the 25"):
    return [{"form": form, "matched": statement, "numbers": [str(stated)], "noun": noun, "sentence": statement,
             "stated": stated, "statement": statement}]


def _have(artifacts=529, rn=161, fisher=(32, 32, 128)):
    return {"artifacts": artifacts, "rate-network runs": rn, "findings": 411,
            "_rate_network": [{"artifact": f"a{i}.json", "fisher_batches": f, "methods": "naive"} for i, f in
                              enumerate(fisher)]}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e277.judge(_found(), _have())}
    for cid in ("W1", "W2", "W3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    assert "16%" in j["W2"]["measured"], j["W2"]
    # a count above the corpus is W1's falsifier
    j = {r["id"]: r for r in e277.judge(_found(stated=1000), _have())}
    assert j["W1"]["verdict"].startswith("FALSIFIER FIRED"), j["W1"]
    # a universal naming most of the record is W2's
    j = {r["id"]: r for r in e277.judge(_found(stated=150), _have())}
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]
    # and every artifact inside 8 or 32 is W3's
    j = {r["id"]: r for r in e277.judge(_found(), _have(fisher=(8, 32, 32)))}
    assert j["W3"]["verdict"].startswith("FALSIFIER FIRED"), j["W3"]
    assert e277.judge([], _have())[0]["verdict"].startswith("REFUSED")


def test_the_live_counts_are_all_below_the_corpus():
    """The finding's numbers on the artifact: 216 against the corpus's artifacts, 25 against its rate-network runs,
    and a universal that now covers 16% of them."""
    p = Path("runs/e277_a_count_is_not_a_scope.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    mapped = [c for c in d["counts"] if c["noun"] in d["corpora"]]
    assert len(mapped) >= 3, mapped
    for c in mapped:
        now = d["corpora"][c["noun"]]
        assert now > c["stated"], c
    ratios = {c["noun"]: d["corpora"][c["noun"]] / c["stated"] for c in mapped if c["stated"]}
    assert ratios["artifacts"] > 2.0 and ratios["rate-network runs"] > 5.0, ratios
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("W1", "W2", "W3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    # the universal's coverage of its noun falls as the corpus grows, so the bound and not the two digits
    shares = [int(x.split("%")[0]) for x in re.findall(r"\d+%", claims["W2"]["measured"])]
    assert shares and max(shares) <= 20, shares
    assert re.search(r"\d+ of \d+", claims["W2"]["measured"]), claims["W2"]
