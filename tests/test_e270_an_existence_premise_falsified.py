"""`e270` falsifies an existence premise the paper states, so the tests pin the scans, the arithmetic, both faces of
the three claims and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e270_an_existence_premise_falsified as e270


def _art(path: Path, n=5, fb=32, size=800, lam=0.003, basis="cell_class"):
    payload = {"config": {"fisher_batches": fb, "circuit_size": size, "lam": lam, "basis": basis},
               "methods": {"naive": {"replicates": [{"final_accuracy": 0.5}] * n},
                           "ewc": {"replicates": [{"final_accuracy": 0.5}] * n}}}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_row_reader_needs_both_a_config_and_a_replicate_list(tmp_path):
    _art(tmp_path / "ok.json")
    (tmp_path / "no_config.json").write_text(json.dumps({"methods": {"naive": {"replicates": [{}]}}}), encoding="utf-8")
    (tmp_path / "no_methods.json").write_text(json.dumps({"config": {"fisher_batches": 8}}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{oops", encoding="utf-8")
    rows = e270.corpus(tmp_path)
    assert [r["artifact"] for r in rows] == ["ok.json"], rows
    assert rows[0]["n"] == 5 and rows[0]["fisher_batches"] == 32


def test_the_sigma_arithmetic_is_the_effect_over_the_sem():
    assert abs(e270.sigma_at(0.0152, 0.051108, 144) - 3.5687) < 1e-3
    assert abs(e270.sigma_at(0.0152, 0.051108, 16) - 1.1896) < 1e-3
    assert math.isnan(e270.sigma_at(0.0152, 0.0, 16))


def _rows():
    return [{"artifact": "big.json", "n": 5, "fisher_batches": 128, "circuit_size": 800, "lam": 0.003,
             "basis": "cell_class", "arms": ["naive"]},
            {"artifact": "e60.json", "n": 16, "fisher_batches": 8, "circuit_size": 800, "lam": 0.1, "basis": "side",
             "arms": ["naive"]},
            {"artifact": "e28.json", "n": 3, "fisher_batches": 8, "circuit_size": 800, "lam": 0.1, "basis": "side",
             "arms": ["naive"]}]


def test_the_three_claims_read_both_faces():
    text = e270.PREMISE + " and again " + e270.PREMISE
    j = {r["id"]: r for r in e270.judge(_rows(), text)}
    assert j["V1"]["verdict"].startswith("MET") and "states the premise 2 time" in j["V1"]["measured"], j["V1"]
    assert j["V2"]["verdict"].startswith("MET"), j["V2"]
    assert j["V3"]["verdict"].startswith("MET"), j["V3"]
    # no 128-batch artifact at all is V1's falsifier, and then V2 has nothing to read
    j = {r["id"]: r for r in e270.judge([_r for _r in _rows() if _r["fisher_batches"] != 128], text)}
    assert j["V1"]["verdict"].startswith("FALSIFIER FIRED"), j["V1"]
    assert j["V2"]["verdict"].startswith("REFUSED"), j["V2"]
    # a powered 128-batch run is V2's falsifier
    powered = [dict(r, n=40) if r["fisher_batches"] == 128 else r for r in _rows()]
    j = {r["id"]: r for r in e270.judge(powered, text)}
    assert j["V2"]["verdict"].startswith("FALSIFIER FIRED"), j["V2"]
    # a hundred replicates at the forwarded number's own cell is V3's
    big = _rows() + [{"artifact": "big_cell.json", "n": 144, "fisher_batches": 8, "circuit_size": 800, "lam": 0.1,
                      "basis": "side", "arms": ["naive"]}]
    j = {r["id"]: r for r in e270.judge(big, text)}
    assert j["V3"]["verdict"].startswith("FALSIFIER FIRED"), j["V3"]
    assert e270.judge([], text)[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_falsifies_the_premise_and_never_ran_the_forwarded_cell():
    """The finding's numbers on the artifact: three 128-batch artifacts at one and five replicates, and the cell whose
    sd the forwarded number uses holding two artifacts whose largest carries sixteen."""
    p = Path("runs/e270_an_existence_premise_falsified.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert sorted(r["n"] for r in d["fisher_128"]) == [1, 5, 5], d["fisher_128"]
    assert {r["artifact"] for r in d["fisher_128"]} == {"e101_rate_fb128.json", "e102_rate_fb128_rerun.json",
                                                        "e96_fisher_batches_128_1seed.json"}, d["fisher_128"]
    assert len(d["cell_rows"]) == 2 and max(r["n"] for r in d["cell_rows"]) == 16, d["cell_rows"]
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("V1", "V2", "V3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    paper = Path("docs/paper/clfly-v1.md").read_text(encoding="utf-8")
    assert paper.count(e270.PREMISE) == 2, "both occurrences are still on the page"
