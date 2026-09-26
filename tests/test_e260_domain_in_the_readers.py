"""`e260` reads the three readers' own two readings, so the tests pin the pieces it judges on -- a claim that leaves
the table counting as moved, a reader that cannot be run twice refusing rather than tracing back, and the two readings
a synthetic corpus gives -- and then pin the live corpus's three moved claims and the addition's two lists.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import domain_rule
from experiments import e260_domain_in_the_readers as e260


def test_moved_counts_a_claim_that_leaves_the_table_as_moved_and_not_as_absent():
    before = [{"id": "N3", "verdict": "MET -- the ordering holds"}, {"id": "N1", "verdict": "MET -- the same"}]
    after = [{"id": "N1", "verdict": "MET -- the same"}]
    assert e260.moved(before, after) == ["N3"], "an id missing inside the domain is a moved claim"
    assert e260.moved(before, before) == []
    assert e260.moved(before, [{"id": "N3", "verdict": "MET -- the ordering holds"},
                               {"id": "N1", "verdict": "FALSIFIER FIRED -- reversed"}]) == ["N1"]


def _r(moved_map: dict, pairs: dict | None = None) -> dict:
    pairs = pairs or {"e244": ([{"id": "K1", "verdict": "null band"}], [{"id": "K1", "verdict": "MET"}]),
                      "e246": ([{"id": "N3", "verdict": "FALSIFIER FIRED"}], [{"id": "N3", "verdict": "MET"}]),
                      "e247": ([{"id": "R2", "verdict": "null band"}], [{"id": "R2", "verdict": "MET"}])}
    return {"inside": {(800, 80, 0.9)}, "outside": {(300, 30, 0.99)}, "pairs": pairs,
            "moved": moved_map, "e252_moved": sorted({c for m in moved_map.values() for c in m})}


def _run(claims: list[dict], code: int = 0, has_domain: bool = True) -> dict:
    return {"flag": True, "code": code, "claims": claims, "has_domain": has_domain}


def test_F4_refuses_when_a_reader_cannot_be_run_twice_rather_than_tracing_back():
    r = _r({"e244": ["K1"], "e246": ["N3"], "e247": ["R2"]})
    rows = {x["id"]: x for x in e260.judge(r, [{"reader": "all three", "error": "RuntimeError('boom')"}])}
    assert rows["F4"]["verdict"].startswith("REFUSED"), rows["F4"]
    assert "boom" in rows["F4"]["measured"], rows["F4"]
    assert rows["F1"]["verdict"].startswith("MET"), "and the other three are still read"


def test_F1_fires_when_a_claim_leaves_the_table_and_F3_when_the_lists_differ():
    pairs = {"e244": ([{"id": "K1", "verdict": "null band"}], []),
             "e246": ([{"id": "N3", "verdict": "FALSIFIER FIRED"}], [{"id": "N3", "verdict": "MET"}]),
             "e247": ([{"id": "R2", "verdict": "null band"}], [{"id": "R2", "verdict": "null band"}])}
    rows = {x["id"]: x for x in e260.judge(
        _r({"e244": ["K1"], "e246": ["N3"], "e247": []}, pairs),
        [{"reader": "e244", "runs": [_run(pairs["e244"][0]), _run(pairs["e244"][0])]}])}
    assert rows["F1"]["verdict"].startswith("FALSIFIER FIRED"), rows["F1"]
    assert rows["F2"]["verdict"].startswith("FALSIFIER FIRED"), rows["F2"]
    assert rows["F3"]["verdict"].startswith("FALSIFIER FIRED"), "a claim that left the table did not move to MET"
    assert "did not move toward MET" in rows["F3"]["verdict"], rows["F3"]

    # the other F3 falsifier: the readers' moved list and e252's are different lists
    pairs = {"e244": ([{"id": "K1", "verdict": "MET -- ordered"}], [{"id": "K1", "verdict": "MET -- ordered"}]),
             "e246": ([{"id": "N3", "verdict": "MET -- the same"}], [{"id": "N3", "verdict": "MET -- the same"}]),
             "e247": ([{"id": "R2", "verdict": "null band"}], [{"id": "R2", "verdict": "MET -- ordered"}])}
    r = _r({"e244": [], "e246": [], "e247": ["R2"]}, pairs)
    r["e252_moved"] = ["K1"]
    rows = {x["id"]: x for x in e260.judge(
        r, [{"reader": "e244", "runs": [_run(pairs["e244"][0]), _run(pairs["e244"][0])]}])}
    assert rows["F3"]["verdict"].startswith("FALSIFIER FIRED"), rows["F3"]
    assert "is not e252's" in rows["F3"]["verdict"], rows["F3"]


def test_F4_fires_when_the_flag_changes_the_claims_or_the_exit_code_or_adds_no_reading():
    r = _r({"e244": ["K1"], "e246": ["N3"], "e247": ["R2"]})
    same = [{"id": "K1", "verdict": "MET"}]
    assert e260.judge(r, [{"reader": "e244", "runs": [_run(same), _run(same, has_domain=False)]}])[3]["verdict"] \
        .startswith("FALSIFIER FIRED")
    assert e260.judge(r, [{"reader": "e244", "runs": [_run(same), _run(same, code=1)]}])[3]["verdict"] \
        .startswith("FALSIFIER FIRED")
    assert e260.judge(r, [{"reader": "e244", "runs": [_run(same), _run(same)]}])[3]["verdict"].startswith("MET")


def test_reading_gives_each_reader_two_rows_and_the_domain_of_a_synthetic_corpus(tmp_path):
    for rw, ex in ((0, 0.05), (1, 0.052)):
        (tmp_path / f"a{rw}.json").write_text(json.dumps({
            "config": {"circuit_size": 800, "support": 80, "rho": 0.9, "seeds": 3, "rewire_seed": rw},
            "topologies": {"alloy1": {"diagonal(EWC)": {"analytic": {"excess_mean": ex}},
                                      "geometry": {"effective_rank": 30.0}},
                           "swap0.5": {"diagonal(EWC)": {"analytic": {"excess_mean": 0.02}},
                                       "geometry": {"effective_rank": 5.0}},
                           "erdos_renyi": {"diagonal(EWC)": {"analytic": {"excess_mean": 0.10}},
                                           "geometry": {"effective_rank": 90.0}}}}), encoding="utf-8")
    r = e260.reading(tmp_path)
    assert r["inside"] == {(800, 80, 0.9)} and r["outside"] == set(), (r["inside"], r["outside"])
    assert set(r["pairs"]) == {"e244", "e246", "e247"}
    for name, (before, after) in r["pairs"].items():
        assert [x["id"] for x in before] == [x["id"] for x in after], name
        assert r["moved"][name] == [], f"{name} has nothing to move on this corpus"
    assert r["e252_moved"] == [], "and e252's module agrees on the same corpus"
    assert domain_rule.inside_cells(tmp_path) == r["inside"]


def test_the_live_corpus_moves_one_claim_per_reader_and_the_same_three_e252_names():
    """The finding's numbers on the artifact: K1, N3 and R2 are the whole moved list, one per reader, all toward MET,
    and the flag is additive in each of the three."""
    p = Path("runs/e260_domain_in_the_readers.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["moved"] == {"e244": ["K1"], "e246": ["N3"], "e247": ["R2"]}, d["moved"]
    assert d["e252_moved"] == ["K1", "N3", "R2"], d["e252_moved"]
    assert sorted(c for m in d["moved"].values() for c in m) == d["e252_moved"], "the readers and the module agree"
    for name in ("e244", "e246", "e247"):
        before, after = d["readings"][name]["all"], d["readings"][name]["domain"]
        assert [x["id"] for x in before] == [x["id"] for x in after], name
        moved = {x["id"]: x["verdict"] for x in after}
        for x in before:
            if moved[x["id"]] != x["verdict"]:
                assert moved[x["id"]].startswith("MET"), (name, x["id"], moved[x["id"]])
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("F1", "F2", "F3", "F4"):
        assert rows[cid]["verdict"].startswith("MET"), rows[cid]
    assert "3 of 11 claims" in rows["F3"]["verdict"], rows["F3"]
    assert [(a["reader"], a["codes"], a["same_claims"]) for a in d["additive"]] == \
        [("e244", [0, 0], True), ("e246", [0, 0], True), ("e247", [0, 0], True)], d["additive"]
    assert d["T"] == 4.0 and len(d["in_domain"]) > len(d["out_of_domain"]), "the bar the rule was read at"
