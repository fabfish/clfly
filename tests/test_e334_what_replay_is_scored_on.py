"""`e334` reads the loss on `replay`'s stored features out, so the tests pin the recording's shape, the
replicate-wise averaging over the tasks that have a buffer, the paired contrasts, and both faces of the four
claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e334_what_replay_is_scored_on as e334


def test_the_average_is_taken_over_the_tasks_with_a_buffer_and_stays_by_replicate():
    run = {"methods": {e334.ARM: {"replicates": [
        {"replay_loss": [{"first": None, "last": None}, {"first": 1.0, "last": 2.0}, {"first": 3.0, "last": 4.0}]},
        {"replay_loss": [{"first": None, "last": None}, {"first": 2.0, "last": 3.0}, {"first": 4.0, "last": 5.0}]},
    ]}}}
    # task 0 has no buffer by construction, so it is not averaged in
    assert run["methods"][e334.ARM]["replicates"][0]["replay_loss"][0]["last"] is None
    assert e334.mean_over_tasks(run, "last") == [3.0, 4.0], e334.mean_over_tasks(run, "last")
    assert e334.mean_over_tasks(run, "first") == [2.0, 3.0], e334.mean_over_tasks(run, "first")
    # a replicate with no entries at all contributes None rather than a zero
    run["methods"][e334.ARM]["replicates"].append({"replay_loss": []})
    assert e334.mean_over_tasks(run, "last")[-1] is None


def test_paired_skips_the_replicates_that_are_missing_rather_than_treating_them_as_zero():
    p = e334.paired([1.0, 2.0, None], [0.5, 1.5, 1.0])
    assert p["n"] == 2 and abs(p["delta"] - 0.5) < 1e-12, p
    assert e334.paired([1.0], [0.5])["delta"] is None
    assert e334.paired([None, None], [1.0, 2.0])["delta"] is None


def _run(first, last, acc=0.62, forget=0.05, leak=1.0, n=5):
    """``first`` and ``last`` are per-task means; the replicate keys carry a spread so a sem is defined."""
    reps = []
    for i in range(n):
        reps.append({"final_accuracy": acc + 0.001 * i, "mean_forgetting": forget + 0.001 * i,
                     "replay_loss": [{"first": None, "last": None},
                                     {"first": first + 0.01 * i, "last": last + 0.01 * i},
                                     {"first": first + 0.01 * i, "last": last + 0.01 * i}]})
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_world_leak": leak, "loop_world_modes": 2},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"world_leak": leak, "world_modes": 2, "noise": 1.0, "n_symbols": 24},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": {e334.ARM: {"final_accuracy": acc, "mean_forgetting": forget, "replicates": reps}}}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _reading(first=(1.0, 1.0), last=(1.2, 1.4), leaks=(1.0, 0.35), counts=True):
    a = _run(first[0], last[0], leak=leaks[0])
    b = _run(first[1], last[1], n=5 if counts else 4, leak=leaks[1])
    return e334.reading({"instant": _write(a), "carry": _write(b)})


def test_the_four_claims_read_both_faces(tmp_path):
    j = {row["id"]: row for row in e334.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: the leaks have to be one and less than one, the counts equal, and nothing else may differ
    assert e334.judge(_reading(leaks=(0.5, 0.35)))[0]["verdict"].startswith("FALSIFIER")
    assert e334.judge(_reading(leaks=(1.0, 1.0)))[0]["verdict"].startswith("FALSIFIER")
    assert e334.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")
    # T2: less stale is the falsifier, inside the band is the null, and more stale is the MET
    assert e334.judge(_reading(last=(1.4, 0.9)))[1]["verdict"].startswith("FALSIFIER")
    assert e334.judge(_reading(last=(1.2, 1.22)))[1]["verdict"].startswith("NULL")
    assert e334.judge(_reading(last=(1.2, 1.4)))[1]["verdict"].startswith("MET")
    # T3: the rise is what differs, so equal rises are the falsifier and a larger one is the MET
    assert e334.judge(_reading(first=(1.0, 1.0), last=(1.2, 1.1)))[2]["verdict"].startswith("FALSIFIER")
    assert e334.judge(_reading(first=(1.0, 1.0), last=(1.2, 1.235)))[2]["verdict"].startswith("NULL")
    # T4: a world whose loss never rises fires
    assert e334.judge(_reading(first=(1.0, 1.0), last=(1.0, 1.2)))[3]["verdict"].startswith("FALSIFIER")

    # a run that never recorded the quantity refuses rather than reading a zero
    a = _run(1.0, 1.2)
    b = _run(1.0, 1.4, leak=0.35)
    for r in b["methods"][e334.ARM]["replicates"]:
        r["replay_loss"] = []
    bad = e334.reading({"instant": _write(a), "carry": _write(b)})
    assert e334.judge(bad)[1]["verdict"].startswith("REFUSED"), e334.judge(bad)[1]

    # and one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e334.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = _write(_run(1.0, 1.2))
    r = e334.reading({"instant": a, "carry": tmp_path / "absent.json"})
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e334.judge(r))


def test_the_live_pair_is_one_configuration_at_two_leaks():
    r = e334.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert r["leaks"] == [1.0, 0.35], r["leaks"]
    assert r["n_replicates"] == [5, 5], r["n_replicates"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e334_what_replay_is_scored_on.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e334.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the two runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["leaks"] == [1.0, 0.35], d["leaks"]
