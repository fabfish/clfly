"""`e322` asks whether the benchmark's trial carries any time, so the tests pin the scan's classification, the
invariance statistic, the per-step probe, and both faces of the five claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e322_the_benchmark_has_no_time_in_it as e322


class _Task:
    """The four attributes `invariance` and `time_axis` read, so a suite can be built without a connectome."""

    def __init__(self, name, u, tau, n_classes=4, readout=None, y=None):
        self.name = name
        self.tau = tau
        self.u_train = np.asarray(u, dtype=float)
        self.u_test = self.u_train
        self.y_train = np.asarray(y if y is not None else np.zeros(len(self.u_train), dtype=int))
        self.y_test = self.y_train
        self.n_classes = n_classes
        self.readout_neurons = np.asarray(readout if readout is not None else np.arange(self.u_train.shape[2]))


def test_the_scan_separates_a_slice_from_a_time_index(tmp_path):
    (tmp_path / "a.py").write_text("u[:, :, inp] = stim[:, None, :]\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("u[:, t, inp] = stim\n", encoding="utf-8")
    (tmp_path / "c.py").write_text("v[:, :, 0] = 1.0\nw = 2\n", encoding="utf-8")
    sites = e322.scan_stimulus_writers(dirs=(str(tmp_path),))
    by_file = {Path(s["file"]).name: s for s in sites}
    assert set(by_file) == {"a.py", "b.py", "c.py"}, sites
    # the full slice writes one value along the whole time axis; the name does not
    assert by_file["a.py"]["time_is_full_slice"] is True, by_file["a.py"]
    assert by_file["c.py"]["time_is_full_slice"] is True, by_file["c.py"]
    assert by_file["b.py"]["time_is_full_slice"] is False, by_file["b.py"]
    assert by_file["b.py"]["ndim"] == 3, by_file["b.py"]


def test_the_scan_ignores_a_store_with_no_slice(tmp_path):
    (tmp_path / "d.py").write_text("u[t, i, j] = 1.0\n", encoding="utf-8")
    assert e322.scan_stimulus_writers(dirs=(str(tmp_path),)) == []


def test_invariance_is_exact_and_reads_both_splits():
    tau, k = 5, 4
    constant = np.zeros((6, tau, k))
    constant[:, :, 0] = 1.0
    assert e322.invariance("ok", [_Task("t", constant, tau)])["worst"] == 0.0
    moving = constant.copy()
    moving[:, 3, 0] = 2.0
    r = e322.invariance("bad", [_Task("t", moving, tau)])
    assert abs(r["worst"] - 1.0) < 1e-12, r
    assert r["per_task"]["t"] > 0, r
    # a deviation in the test split alone is still a deviation
    task = _Task("t", constant, tau)
    task.u_test = moving
    assert e322.invariance("bad", [task])["worst"] > 0


def _coded(y, tau, k, from_step):
    z = np.ones((len(y), tau, k), dtype=float)
    for t in range(from_step, tau):
        z[:, t, :] = 0.0
        z[np.arange(len(y)), t, np.asarray(y) % k] = 3.0
    return z


def test_the_probe_is_fitted_per_step():
    rng = np.random.default_rng(0)
    tau, k, step = 6, 6, 3
    y = rng.integers(0, 3, size=48)
    yt = rng.integers(0, 3, size=24)
    acc = e322.probe(_coded(y, tau, k, step), y, _coded(yt, tau, k, step), yt, np.arange(k))
    assert len(acc) == tau
    assert acc[step - 1] < 0.6, acc          # before the code arrives there is nothing to read
    assert acc[step] > 0.95, acc             # and at the step it arrives the read is exact
    assert acc[-1] > 0.95, acc


def _reading(**kw):
    rows = {}
    for suite in ("assembly", "overlap0"):
        rows[suite] = {}
        for task in ("a", "b"):
            rows[suite][task] = {"chance": 0.25, "step_sizes": [0.1, 0.2], "settled_fraction": 2.0,
                                 "last_over_max": 1.0, "first_over_max": 0.5,
                                 "probe": [0.25, 1.0, 1.0], "probe_final": 1.0, "probe_midpoint": 1.0,
                                 "probe_gap": 0.0}
    r = {"invariance": [{"suite": "assembly", "circuit": "MB", "size": 300, "n_tasks": 2,
                         "worst": 0.0, "per_task": {}}],
         "scan": [{"file": "clfly/network/tasks.py", "line": 121, "ndim": 3, "time_is_full_slice": True}],
         "sizes": [300],
         "time_axis": [{"suite": s, "circuit": "MB", "size": 300, "chance": 0.25, "tasks": t}
                       for s, t in rows.items()],
         "corpus": {"artifacts": 100, "scanned": True, "assembly_names": ["heading"], "overlap_names": ["ov0_t0"],
                    "unclassified": []}}
    r.update(kw)
    return r


def test_the_five_claims_read_both_faces():
    j = {row["id"]: row for row in e322.judge(_reading())}
    for cid in ("T1", "T2", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1's falsifier: a task whose stimulus moves
    bad = _reading()
    bad["invariance"][0]["worst"] = 1e-9
    assert e322.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED"), e322.judge(bad)[0]

    # T2's falsifier: a second authored site, or one writing along time
    second = _reading()
    second["scan"] = second["scan"] + [{"file": "experiments/e9.py", "line": 3, "ndim": 3,
                                        "time_is_full_slice": False}]
    assert e322.judge(second)[1]["verdict"].startswith("FALSIFIER FIRED"), e322.judge(second)[1]
    only_test = _reading()
    only_test["scan"] = [{"file": "tests/t.py", "line": 1, "ndim": 3, "time_is_full_slice": False}]
    assert e322.judge(only_test)[1]["verdict"].startswith("FALSIFIER FIRED"), e322.judge(only_test)[1]

    # T3 is decided by the first-step denominator, and the MET case needs a settling trajectory
    settled = _reading()
    for suite in settled["time_axis"]:
        for v in suite["tasks"].values():
            v["settled_fraction"] = 1e-3
    assert e322.judge(settled)[2]["verdict"].startswith("MET"), e322.judge(settled)[2]
    assert e322.judge(_reading())[2]["verdict"].startswith("FALSIFIER FIRED"), e322.judge(_reading())[2]

    # T4's falsifier: an above-chance task that gains a tenth of its accuracy after the midpoint
    late = _reading()
    for suite in late["time_axis"]:
        for v in suite["tasks"].values():
            v["probe_midpoint"] = 0.80
            v["probe_gap"] = 0.20
    assert e322.judge(late)[3]["verdict"].startswith("FALSIFIER FIRED"), e322.judge(late)[3]
    # a gap between the window and the falsifier is the registered null, not a MET
    between = _reading()
    for suite in between["time_axis"]:
        for v in suite["tasks"].values():
            v["probe_gap"] = (e322.IN_PLACE + e322.GAP) / 2
    assert e322.judge(between)[3]["verdict"].startswith("NULL"), e322.judge(between)[3]
    # and a corpus of tasks all at chance refuses rather than reading
    chance = _reading()
    for suite in chance["time_axis"]:
        for v in suite["tasks"].values():
            v["probe_final"] = 0.25
            v["probe_gap"] = None
    assert e322.judge(chance)[3]["verdict"].startswith("REFUSED"), e322.judge(chance)[3]

    # T5 refuses when the corpus was not scanned rather than firing
    unscanned = _reading(corpus={"artifacts": 0, "scanned": False})
    assert e322.judge(unscanned)[4]["verdict"].startswith("REFUSED"), e322.judge(unscanned)[4]
    foreign = _reading(corpus={"artifacts": 9, "scanned": True, "assembly_names": ["visual_motion"],
                               "overlap_names": [], "unclassified": ["visual_motion"]})
    assert e322.judge(foreign)[4]["verdict"].startswith("FALSIFIER FIRED"), e322.judge(foreign)[4]

    # and nothing measured refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e322.judge({"invariance": [], "time_axis": []}))


def test_the_tree_really_has_one_authored_writer():
    """The structural claim, asserted on this repository rather than on a fixture."""
    authored = [s for s in e322.scan_stimulus_writers()
                if any(s["file"].startswith(d + "/") for d in e322.AUTHOR_DIRS)]
    assert len(authored) == 1, authored
    assert authored[0]["time_is_full_slice"] is True, authored[0]
    assert authored[0]["file"].endswith("clfly/network/tasks.py"), authored[0]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e322_the_benchmark_has_no_time_in_it.json")
    if not p.exists():
        return                      # the artifact is written by the run this unit reads
    d = json.loads(p.read_text(encoding="utf-8"))
    claims = {row["id"]: row["verdict"] for row in d["claims"]}
    for cid in ("T1", "T2", "T5"):
        assert claims[cid].startswith("MET"), claims[cid]
    # T3's falsifier is the finding: the registered denominator is the zero-state first step
    assert claims["T3"].startswith("FALSIFIER FIRED"), claims["T3"]
    # and T4's measured gap lands in the registered null rather than under the window
    assert claims["T4"].startswith(("MET", "NULL")), claims["T4"]
    assert not claims["T4"].startswith("FALSIFIER FIRED"), claims["T4"]
    # the read-out peaks early rather than late, which is what the null above is made of
    rows = [v for x in d["time_axis"] for v in x["tasks"].values()]
    assert rows, d
    early = sum(1 for v in rows if v["probe_best_step"] <= 2)
    assert early * 2 >= len(rows), (early, len(rows))
    lost = sum(1 for v in rows if v["probe_last_minus_best"] < 0)
    assert lost * 2 >= len(rows), (lost, len(rows))
    # the invariance is exact wherever it was measured, and the corpus is inside the two builders
    assert all(x["worst"] == 0.0 for x in d["invariance"]), d["invariance"]
    assert d["corpus"]["artifacts"] > 0 and not d["corpus"]["unclassified"], d["corpus"]
    # the unbiased denominator is reported beside the registered one and does not settle either
    worst = max(v["last_over_max"] for x in d["time_axis"] for v in x["tasks"].values())
    assert worst > e322.SETTLED, worst
