"""`e298` reads the paper's basis recommendations for their scope, so the tests pin the paragraph-aware sentence rule,
the whitespace flattening, the basis-noun list (`anchor` is the advice and not a basis), both faces of the three
claims, and the live state after the correction.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e298_the_recommendation_needs_a_comparator as e298


def test_the_sentence_rule_is_paragraph_aware():
    # a paragraph opening with bold text starts a new sentence, because the blank line is a hard boundary -- whereas a
    # split on punctuation alone would carry the previous paragraph's tail into it
    text = "One claim is stated.\n\n**And the next paragraph opens with bold.** It continues."
    ss = e298.sentences(text)
    assert ss == ["One claim is stated.", "**And the next paragraph opens with bold.** It continues."], ss
    assert "One claim" not in ss[1], ss
    # and a hard-wrapped phrase is flattened before matching
    rows = e298.recommendations("We recommend the coarsest rung, because a better place to anchor a Fisher\n"
                                "than the diagonal on accuracy is what we mean.")
    assert rows and rows[0]["comparators"] == ["than the diagonal"], rows
    assert rows[0]["metrics"] == ["accuracy"], rows


def test_the_lists_decide_what_counts_as_a_recommendation():
    # an advice cue plus a basis noun
    assert len(e298.recommendations("We recommend pooling the rarest cell types.")) == 1
    # `anchor` is the advice and not a basis noun
    assert e298.recommendations('We choose to quote "Anchor gently" and nothing else.') == []
    # a cue with no basis noun, and a basis noun with no cue
    assert e298.recommendations("We recommend running more seeds.") == []
    assert e298.recommendations("The rung ladder has five entries.") == []
    assert "anchor" not in e298.BASIS, e298.BASIS


def _reading(texts=None, metrics=None, comparators=None, citations=None):
    texts = texts if texts is not None else [
        "we recommend the coarsest rung on accuracy than the diagonal (`docs/findings/a.md`)",
        "we prefer cell types on forgetting than a matched random partition (`docs/findings/b.md`)",
        "we recommend the rung on forgetting than the diagonal (`docs/findings/c.md`)"]
    metrics = metrics if metrics is not None else [["accuracy"], ["forgetting"], ["forgetting"]]
    comparators = comparators if comparators is not None else [["than the diagonal"], ["than a matched"],
                                                              ["than the diagonal"]]
    return {"recommendations": [{"sentence": i, "text": t, "metrics": m, "comparators": c, "cues": ["recommend"],
                                 "basis_nouns": ["rung"]}
                                for i, (t, m, c) in enumerate(zip(texts, metrics, comparators))]}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e298.judge(_reading())}
    for cid in ("N1", "N2", "N3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a recommendation with no metric is N1's falsifier
    j = {r["id"]: r for r in e298.judge(_reading(metrics=[["accuracy"], [], ["forgetting"]]))}
    assert j["N1"]["verdict"].startswith("FALSIFIER FIRED"), j["N1"]
    # one with no comparator is N2's
    j = {r["id"]: r for r in e298.judge(_reading(comparators=[["than the diagonal"], [], ["than the diagonal"]]))}
    assert j["N2"]["verdict"].startswith("FALSIFIER FIRED"), j["N2"]
    # one that cites nothing is N3's
    j = {r["id"]: r for r in e298.judge(_reading(texts=["a claim on accuracy than the diagonal",
                                                       "another on forgetting than a matched",
                                                       "one on forgetting than the diagonal"]))}
    assert j["N3"]["verdict"].startswith("FALSIFIER FIRED"), j["N3"]
    assert e298.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e298.judge({"recommendations": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_paper_is_scoped_after_the_correction():
    if not e298.PAPER.exists():
        return
    rows = e298.recommendations(e298.PAPER.read_text(encoding="utf-8"))
    assert len(rows) == 3, [(x["sentence"], x["text"][:60]) for x in rows]
    assert all(x["metrics"] for x in rows), rows
    assert all(x["comparators"] for x in rows), rows
    assert all("docs/findings/" in x["text"] for x in rows), rows
    # the scope names the metric pair and a comparator in each case
    assert all({"forgetting", "accuracy"} <= set(x["metrics"]) for x in rows), [x["metrics"] for x in rows]
    sentences = [x["sentence"] for x in rows]
    assert len(set(sentences)) == 3, sentences


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e298_the_recommendation_needs_a_comparator.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["recommendations"]) == 3, d["recommendations"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("N1", "N2", "N3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "3 of them name a metric" in claims["N1"]["measured"], claims["N1"]
