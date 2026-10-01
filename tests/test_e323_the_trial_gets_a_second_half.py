"""`e323` gives the suite its first time-varying stimulus, so the tests pin the builder's two halves, the second
writer the AST scan is meant to catch, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from clfly.network import tasks as rate_tasks
from experiments import e322_the_benchmark_has_no_time_in_it as e322
from experiments import e323_the_trial_gets_a_second_half as e323


class _Circ:
    """A stand-in for a `Circuit`: `_heads` never touches it when both supports are given."""

    n_neurons = 40


def _task(k=2, tau=6, n_train=24, n_test=12, noise=0.0, seed=0):
    return rate_tasks.make_sequence_task(
        _Circ(), "seq_t", None, None, k=k, tau=tau, n_train=n_train, n_test=n_test, noise=noise, seed=seed,
        input_support=np.arange(6), readout_subset=np.arange(6, 12))


def test_the_builder_writes_two_constant_halves():
    t = _task()
    u = t.u_train
    half = t.tau // 2
    assert u.shape == (24, 6, 40), u.shape
    # each half is the same vector at every step inside it -- the property e322 measured as zero for the
    # sustained builders, now holding per half rather than per trial
    for step in range(1, half):
        assert np.array_equal(u[:, step], u[:, 0]), step
    for step in range(half + 1, t.tau):
        assert np.array_equal(u[:, step], u[:, half]), step
    # noise = 0 makes the pattern the template itself, so with two symbols the halves differ exactly when the
    # symbols do -- and coincide exactly when they are the same symbol, which is what makes the next assertion
    # about the label rather than about the noise
    first, second = t.y_train // 2, t.y_train % 2
    differ = first != second
    assert differ.any() and not differ.all(), differ
    assert np.all(np.any(u[differ, half] != u[differ, 0], axis=1)), "a symbol change moves the drive"
    same = np.flatnonzero(first == second)
    assert np.all(u[same, 0] == u[same, half]), "and the same symbol twice is the same pattern"
    assert set(np.unique(t.y_train).tolist()) <= {0, 1, 2, 3}, np.unique(t.y_train)
    # with noise on, the redraw at the boundary moves the drive for every example even when the symbol repeats
    noisy = _task(noise=1.0)
    assert np.all(np.any(noisy.u_train[:, half] != noisy.u_train[:, 0], axis=1))


def test_a_larger_alphabet_is_more_classes_and_the_same_two_halves():
    t = _task(k=3)
    assert t.n_classes == 9, t.n_classes
    assert set(np.unique(t.y_train).tolist()) <= set(range(9)), np.unique(t.y_train)
    half = t.tau // 2
    assert np.array_equal(t.u_train[:, 1], t.u_train[:, 0]), "the half is still constant"
    first, second = t.y_train // 3, t.y_train % 3
    differ = first != second
    assert differ.any()
    assert np.all(np.any(t.u_train[differ, half] != t.u_train[differ, 0], axis=1))


def test_the_sequence_builder_is_the_second_writer():
    """`e322`'s scan is what was supposed to notice this, so it is asserted on this repository.

    `e325` has since added a third authored writer (the closed-loop environment's cue), so what is pinned here is
    where the sequence builder sits rather than how many writers there are: a timed site in the same module as the
    sustained builder, later in the file than it.
    """
    authored = [s for s in e322.scan_stimulus_writers()
                if any(s["file"].startswith(d + "/") for d in e322.AUTHOR_DIRS)]
    sustained = [s for s in authored if s["time_is_full_slice"] and s["file"].endswith("tasks.py")]
    assert len(sustained) == 1, authored
    timed = sorted((s for s in authored if not s["time_is_full_slice"] and s["file"].endswith("tasks.py")),
                   key=lambda s: s["line"])
    assert timed, authored
    assert timed[0]["line"] > sustained[0]["line"], (sustained, timed)
    assert all(s["file"].endswith("clfly/network/tasks.py") for s in sustained + timed), authored


def _reading(readout="narrow", within=0.0, boundary=1.0, pair_last=0.80, pair_half=0.26, first_last=0.90,
             chance_pair=0.25, chance_first=0.5):
    tasks = {name: {"pair": [0.25] * 12, "first": [0.5] * 12, "second": [0.5] * 12,
                    "pair_last": pair_last, "pair_at_half": pair_half,
                    "first_last": first_last, "second_at_half": 0.5}
             for name in ("seq_odour_identity", "seq_heading")}
    return {"sequence": [{"circuit": "MB", "size": 300, "readout": readout, "chance_pair": chance_pair,
                          "chance_first": chance_first,
                          "checks": [{"task": n, "tau": 12, "half": 6, "within_half_worst": within,
                                      "boundary_least": boundary, "at_boundary_max": boundary}
                                     for n in tasks],
                          "tasks": tasks}],
            "constant": [], "configs": []}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e323.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1's falsifier: a half that is not internally constant, or a boundary that never moves
    assert e323.judge(_reading(within=1e-9))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e323.judge(_reading(boundary=0.0))[0]["verdict"].startswith("FALSIFIER FIRED")

    # T2: below the falsifier at 0.05, between it and the bar is the registered null
    assert e323.judge(_reading(pair_last=0.28))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e323.judge(_reading(pair_last=0.35))[1]["verdict"].startswith("NULL")
    # T3 is inverted: a high mid-trial reading fires and a low one is the MET
    assert e323.judge(_reading(pair_half=0.45))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e323.judge(_reading(pair_half=0.35))[2]["verdict"].startswith("NULL")
    # T4: the memory claim
    assert e323.judge(_reading(first_last=0.52))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e323.judge(_reading(first_last=0.60))[3]["verdict"].startswith("NULL")
    # and nothing measured refuses every claim rather than reading a number
    assert all(row["verdict"].startswith("REFUSED") for row in e323.judge({"sequence": []}))


def test_the_head_reading_is_reported_beside_the_narrow_one():
    r = _reading()
    r["sequence"].append(dict(r["sequence"][0], readout="head", tasks={
        n: dict(v, pair_last=0.95) for n, v in r["sequence"][0]["tasks"].items()}))
    j = {row["id"]: row for row in e323.judge(r)}
    # T2 is decided on the narrow read-out and the head is a description of it
    assert "+0.5500" in j["T2"]["measured"], j["T2"]["measured"]
    assert j["T2"]["verdict"].startswith("MET"), j["T2"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e323_the_trial_gets_a_second_half.json")
    if not p.exists():
        return                      # the artifact is written by the run this unit reads
    d = json.loads(p.read_text(encoding="utf-8"))
    # the artifact's own claims are the ones its own reading produces, whether or not they are the ones the
    # finding was written from
    assert {r["id"]: r["verdict"] for r in e323.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["id"] == "T1" and d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    # the two halves are constant in every configuration the run measured
    for x in d["sequence"]:
        for c in x["checks"]:
            assert c["within_half_worst"] == 0.0, c
            assert c["boundary_least"] > 0, c
    # and every probe curve is a curve over the trial's own length
    for x in d["sequence"] + d["constant"]:
        for v in x["tasks"].values():
            assert len(v["pair"]) == 12 and len(v["first"]) == 12 and len(v["second"]) == 12, v
