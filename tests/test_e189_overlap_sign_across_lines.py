"""`e189` compares the two task lines' overlap responses, and its own first version over-claimed twice.

Both mistakes are pinned here: it declared a component "rises" when the corpus's tally was mixed, and it printed
that the *far* trend is shared between the lines when the network's own standard errors leave the far change
unresolved in eight of nine comparisons. A direction is called resolved only when the paired change clears twice the
sum-in-quadrature sem, so a rounding artefact cannot be read as a sign.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e189_overlap_sign_across_lines as e189


def test_direction_needs_a_sign_and_carries_no_threshold():
    assert e189.direction(1.0, 2.0) == "rises" and e189.direction(2.0, 1.0) == "falls"
    assert e189.direction(1.0, 1.0) == "flat"


def test_the_split_is_by_task_distance():
    """(1->0) and (2->1) are adjacent; (2->0) is distant -- the three ordered pairs a three-task run realises."""
    costs = {(1, 0): np.array([0.1, 0.1]), (2, 1): np.array([0.2, 0.2]), (2, 0): np.array([0.3, 0.3])}
    s = e189.split(costs)
    assert s["near"]["n_pairs"] == 2 and abs(s["near"]["mean"] - 0.15) < 1e-12
    assert s["far"]["n_pairs"] == 1 and abs(s["far"]["mean"] - 0.3) < 1e-12


def test_an_unresolved_change_is_not_a_direction(tmp_path):
    """A change inside its own error must not be counted as a fall, which is the bug the live table produced on a
    change of 1e-5."""
    runs = tmp_path / "runs"
    runs.mkdir()
    old = {"config": {"input_overlap": 0.0, "lam": 0.003, "methods": "naive"}, "controlled": []}
    for name, near in (("lo.json", 0.050), ("hi.json", 0.0504)):
        R = [[1.0, None, None], [1.0 - near, 1.0, None], [0.9, 0.9, 1.0]]
        (runs / name).write_text(json.dumps({
            "config": dict(old["config"], input_overlap=0.0 if name == "lo.json" else 1.0),
            "methods": {"naive": {"replicates": [{"retention": R}] * 4}},
        }), encoding="utf-8")
    (runs / e189.ANALYTIC).write_text(json.dumps({"controlled": [
        {"level": 0.0, "achieved_overlap": 0.0, "mean_interference": 0.02,
         "mean_interference_near": 0.03, "mean_interference_far": 0.01},
        {"level": 1.0, "achieved_overlap": 1.0, "mean_interference": 0.01,
         "mean_interference_near": -0.001, "mean_interference_far": 0.011}]}), encoding="utf-8")
    res = e189.audit(runs, pairs=[("the pair", "naive", "lo.json", "hi.json", "pair")])
    row = res["network_comparisons"][0]
    assert row["near_direction"] == "unresolved", row
    assert res["analytic_directions"] == {"near": "falls", "far": "rises", "mean": "falls"}


def test_the_live_comparison_localises_the_disagreement_to_the_adjacent_pairs():
    """The gate, and the result: the near component is resolved and opposite in the two lines, the far one is
    unresolved in both."""
    res = e189.audit(Path("runs"))
    assert res["n_mismatches"] == 0, res["mismatches"]
    assert res["analytic_directions"]["near"] == "falls"
    assert res["analytic_directions"]["far"] == "rises"
    assert res["network_tally"]["near"]["rises"] >= 5, res["network_tally"]
    assert res["network_tally"]["near"]["falls"] == 0
    assert res["network_tally"]["far"]["unresolved"] >= 6, "the far component is not resolved on the network side"
    assert len(res["network_comparisons"]) >= 8
    assert len(res["refused"]) == 1, res["refused"]
