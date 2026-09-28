"""`e275` was registered before its run landed, so the tests pin the arithmetic, both faces of the three claims and the
refusal that keeps the module from reporting a number while the second run is absent.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e275_the_suite_makes_it_visible as e275


def _art(path: Path, n_eval=144, n=4, fraction=2.0, arms=("naive", "ewc"), train=None):
    """A stand-in run: each arm's replicates spread so that its floor is `fraction` of its own variance."""
    payload = {"config": {"circuit_size": 800, "test": n_eval // 3}, "evaluation_noise": {"n_eval": n_eval},
               "methods": {}}
    for a in arms:
        xs = [0.5 + 0.01 * i for i in range(n)]
        mean = sum(xs) / len(xs)
        v = sum((x - mean) ** 2 for x in xs) / (n - 1)
        payload["methods"][a] = {"replicates": [{"final_accuracy": v, "mean_forgetting": v,
                                                 "learned": (train or [0.9, 0.9, 0.9])} for v in xs]}
        payload["evaluation_noise"][a] = {"binomial_sem": math.sqrt(fraction * v)}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_module_refuses_while_the_second_run_is_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(e275, "NEW", str(tmp_path / "absent.json"))
    monkeypatch.setattr(e275, "OLD", str(tmp_path / "absent.json"))
    j = {r["id"]: r for r in e275.judge(None, None)}
    for cid in ("Z1", "Z2", "Z3"):
        assert j[cid]["verdict"].startswith("REFUSED"), j[cid]


def test_the_fraction_reader_and_the_training_column(tmp_path):
    p = tmp_path / "a.json"
    _art(p, fraction=2.0)
    d = json.loads(p.read_text(encoding="utf-8"))
    r = e275.reading(d)
    assert r["n_eval"] == 144 and r["n"] == 4 and r["arms"] == ["ewc", "naive"], r["arms"]
    for key, f in r["fractions"].items():
        assert abs(f - 2.0) < 1e-9, (key, f)
    assert r["training"]["naive"] == [[0.9, 0.9, 0.9]] * 4, r["training"]


def _reading(n_eval=144, n=40, fraction=2.086):
    return {"n_eval": n_eval, "n": n, "arms": ["naive"], "seconds": 100.0,
            "fractions": {"naive/final_accuracy": fraction}, "training": {"naive": [[1.0]] * n},
            "metrics": {}}


def test_the_three_claims_read_both_faces():
    old, new = _reading(144, 40, 2.086), _reading(600, 40, 2.086 * 144 / 600)
    j = {r["id"]: r for r in e275.judge(old, new)}
    for cid in ("Z1", "Z2", "Z3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a training column that moved is Z1's falsifier
    moved = _reading(600, 40, 0.5)
    moved["training"] = {"naive": [[0.5]] * 40}
    j = {r["id"]: r for r in e275.judge(old, moved)}
    assert j["Z1"]["verdict"].startswith("FALSIFIER FIRED"), j["Z1"]
    # a floor that did not fall is Z2's, and one still above 1 is Z3's
    j = {r["id"]: r for r in e275.judge(old, _reading(600, 40, 2.086))}
    assert j["Z2"]["verdict"].startswith("FALSIFIER FIRED"), j["Z2"]
    assert j["Z3"]["verdict"].startswith("FALSIFIER FIRED"), j["Z3"]
    assert e275.judge(old, None)[0]["verdict"].startswith("REFUSED")


def test_the_live_pair_reads_the_suite_if_the_run_has_landed():
    p = Path("runs/e275_the_suite_makes_it_visible.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    claims = {r["id"]: r for r in d["claims"]}
    if d["new_n_eval"] is None:
        assert claims["Z1"]["verdict"].startswith("REFUSED"), claims["Z1"]
        return
    assert d["old_n_eval"] == 144 and d["new_n_eval"] == 600, (d["old_n_eval"], d["new_n_eval"])
    for cid in ("Z1", "Z2", "Z3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert all(v < 1.0 for v in d["fractions_new"].values()), d["fractions_new"]
