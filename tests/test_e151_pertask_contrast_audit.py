"""`e151`'s labels have to be a function of the statistics, not of what a reader wants.

The failure modes worth a test are the two that have cost this project fires already: a **missing artifact must
read as missing** rather than as a zero, and **two labels that describe different defects must not be reachable by
one rule** -- `hidden` (the aggregate does not resolve while a term does) and `cancelling` (the terms disagree)
were both printed as prose before this script existed, one contrast at a time, and a catalogue that mixed them
would be worse than the hand search it replaces.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e151_pertask_contrast_audit as e151


def _diff(n: int, mean: float, sd: float) -> np.ndarray:
    """A paired difference with this mean and this sample sd, exactly -- so every sigma below is arithmetic."""
    d = np.zeros(n)
    d[0] = 1.0
    d = d - d.mean()
    d = d / d.std(ddof=1)
    return mean + sd * d


def _contrast(n: int, agg, terms, newest=(0.0, 0.0)) -> tuple[dict, list[dict], dict]:
    """A and B whose A-minus-B difference is prescribed on the aggregate, both terms and the newest task."""
    a = {"forgetting": np.full(n, agg), "terms": np.tile(np.asarray(terms, float), (n, 1)),
         "newest": np.full(n, newest[0]), "n": n}
    b = {"forgetting": a["forgetting"] - _diff(n, agg, 0.05),
         "terms": np.stack([a["terms"][:, k] - _diff(n, terms[k], 0.05) for k in range(2)], axis=1),
         "newest": a["newest"] - _diff(n, newest[1], 0.05), "n": n}
    return a, b


def _labels(n: int, agg, terms) -> tuple[dict, list[dict], str]:
    a, b = _contrast(n, agg, terms)
    aggregate = e151.paired(a["forgetting"], b["forgetting"])
    per_term = [e151.paired(a["terms"][:, k], b["terms"][:, k]) for k in range(2)]
    return aggregate, per_term, e151.classify(aggregate, per_term)


def test_every_label_is_reachable_and_the_two_defects_are_distinguished():
    # forty seeds, sd 0.05 -> sem 0.0079, so a 0.03 change is 3.8 sigma and a 0.004 change is 0.5 sigma
    agg, terms, label = _labels(40, -0.030, (-0.030, -0.030))
    assert terms[0]["sigma"] > 2 and label == "fair"
    _, _, label = _labels(40, -0.030, (-0.030, -0.004))
    assert label == "one term"
    # the two terms disagree while the aggregate resolves: a difference, not a summary
    _, terms, label = _labels(40, -0.070, (+0.030, -0.030))
    assert label == "cancelling" and len({np.sign(t["change"]) for t in terms}) == 2
    # the aggregate resolves only because two sub-threshold terms add
    assert _labels(40, -0.020, (-0.010, -0.010))[2] == "weak pair"
    # the aggregate does not resolve while a term does: the printed number is not the effect
    assert _labels(40, -0.004, (+0.030, -0.020))[2] == "hidden"
    assert _labels(40, -0.004, (-0.004, -0.004))[2] == "null"


def test_the_resolution_is_the_paired_sem_and_not_the_size():
    big_and_noisy = _labels(40, -0.030, (-0.030, -0.030))[0]
    assert abs(big_and_noisy["sem"] - 0.05 / np.sqrt(40)) < 1e-12
    assert abs(big_and_noisy["sigma"] - 0.030 / (0.05 / np.sqrt(40))) < 1e-9


def test_a_missing_artifact_reads_as_missing_and_contributes_no_row(tmp_path):
    assert e151.load_arm(tmp_path / "nope.json", "ewc") is None
    payload = {"methods": {"naive": {"replicates": [
        {"mean_forgetting": 0.1, "forgetting_per_task": [0.05, 0.05, 0.0], "final_per_task": [0.7, 0.8, 0.9]}]}}}
    part = tmp_path / "part.json"
    part.write_text(json.dumps(payload), encoding="utf-8")
    assert e151.load_arm(part, "naive") is not None
    assert e151.load_arm(part, "ewc") is None
    res = e151.audit((("missing one", str(part), "ewc", str(part), "naive"),))
    assert res["n_contrasts"] == 0 and len(res["missing"]) == 1 and res["rows"] == []


def test_the_newest_task_comes_from_final_per_task_and_not_from_a_forgetting_term(tmp_path):
    """`final_per_task[-1]` is the task no forgetting term covers -- the column the aggregate cannot hold."""
    payload = {"methods": {"naive": {"replicates": [
        {"mean_forgetting": 0.1, "forgetting_per_task": [0.05, 0.05, 0.0], "final_per_task": [0.7, 0.8, 0.9]}] * 3}}}
    p = tmp_path / "part.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    loaded = e151.load_arm(p, "naive")
    assert list(loaded["newest"]) == [0.9, 0.9, 0.9]
    assert loaded["terms"].shape == (3, 2)
    assert not np.allclose(loaded["newest"], loaded["terms"][:, 1])


def test_the_registry_names_only_artifacts_that_exist_so_the_audit_cannot_shrink_silently():
    missing = [c[0] for c in e151.CONTRASTS if not Path(c[1]).is_file() or not Path(c[3]).is_file()]
    assert missing == [], f"the registry names artifacts that are not on disk: {missing}"
    res = e151.audit()
    assert res["n_contrasts"] == len(e151.CONTRASTS) and res["missing"] == []
    assert set(res["counts"]) <= {"fair", "one term", "weak pair", "cancelling", "hidden", "null"}
