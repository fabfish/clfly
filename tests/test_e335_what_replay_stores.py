"""`e335` reads what `replay`'s buffer actually holds, so the tests pin the buffer comparison, the source scan that
identifies the stored object, the drift comparison, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e335_what_replay_stores as e335


def test_the_buffer_holds_the_environment_s_arrays_and_not_the_world_s():
    b = e335.buffer_contents()
    assert b["n_train"] == 8 and b["n_test"] == 8, b
    assert b["leaks"] == [1.0, 0.35], b["leaks"]
    # the world's channel is added by the feedback closure, so it never reaches the arrays a buffer is filled from
    assert b["u_train_identical"] and b["u_test_identical"], b
    assert b["y_train_identical"] and b["y_test_identical"], b


def test_the_source_scan_reads_the_statement_it_reports(tmp_path):
    good = tmp_path / "good.py"
    good.write_text("def f():\n    replay.extend((task.u_train[i], int(task.y_train[i]), k) for i in idx)\n",
                    encoding="utf-8")
    r = e335.buffer_source(good)
    assert r["stores_an_input"] and not r["mentions_a_feature"], r
    assert "u_train" in r["statement"], r
    bad = tmp_path / "bad.py"
    bad.write_text("def f():\n    replay.extend((traj[i], int(task.y_train[i]), k) for i in idx)\n", encoding="utf-8")
    r = e335.buffer_source(bad)
    assert r["mentions_a_feature"], r
    # a file with no buffer at all reports nothing rather than crashing
    empty = tmp_path / "empty.py"
    empty.write_text("x = 1\n", encoding="utf-8")
    assert e335.buffer_source(empty)["statement"] == ""


def _run(drift, forget=0.05, leak=1.0, n=5):
    reps = [{"theta_drift": [d + 0.0001 * i for d in drift], "mean_forgetting": forget,
             "final_accuracy": 0.6} for i in range(n)]
    return {"config": {"circuit_size": 300, "loop_world_leak": leak},
            "circuit": "MB", "readout": {"subset_sha1": "abc"}, "tasks": [{"name": "t"}],
            "env_draw": {"world_leak": leak, "world_modes": 2},
            "methods": {e335.ARM: {"final_accuracy": 0.6, "mean_forgetting": forget, "replicates": reps}}}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _reading(instant=(0.0613, 0.0592, 0.0575), carry=(0.0663, 0.0642, 0.0625),
             forget=(0.0479, 0.0854)):
    a = _write(_run(list(instant), forget=forget[0], leak=1.0))
    b = _write(_run(list(carry), forget=forget[1], leak=0.35))
    return {"buffer": {"n_train": 8, "n_test": 8, "leaks": [1.0, 0.35], "u_train_identical": True,
                       "u_test_identical": True, "y_train_identical": True, "y_test_identical": True},
            "source": {"calls": [], "statement": "replay.extend((task.u_train[i], int(task.y_train[i]), k) "
                                                 "for i in idx)", "stores_an_input": True,
                       "mentions_a_feature": False},
            "drift": e335.drifts(a, b)}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e335.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: an array that differs is the falsifier
    bad = _reading()
    bad["buffer"]["u_train_identical"] = False
    assert e335.judge(bad)[0]["verdict"].startswith("FALSIFIER")
    # T2: a buffer that stores something else is the falsifier
    bad = _reading()
    bad["source"] = {"statement": "replay.extend((traj[i], y, k) for i in idx)", "stores_an_input": False,
                     "mentions_a_feature": True}
    assert e335.judge(bad)[1]["verdict"].startswith("FALSIFIER")
    # T3: bodies that moved by the same amount are the falsifier, and a small difference is the null
    same = _reading(carry=(0.0613, 0.0592, 0.0575))
    assert e335.judge(same)[2]["verdict"].startswith("FALSIFIER")
    tiny = _reading(carry=(0.0614, 0.0593, 0.0576))
    assert e335.judge(tiny)[2]["verdict"].startswith("NULL")
    # T4: the carried body moving LESS is the falsifier even when T3 is met
    assert e335.judge(_reading(carry=(0.0563, 0.0542, 0.0525)))[3]["verdict"].startswith("FALSIFIER")
    assert e335.judge(_reading())[3]["verdict"].startswith("MET")

    # and a missing artifact refuses the two drift claims and not the other two
    r = _reading()
    r["drift"] = {"runs": 0, "missing": ["runs/b.json"]}
    j = {row["id"]: row for row in e335.judge(r)}
    assert j["T1"]["verdict"].startswith("MET") and j["T2"]["verdict"].startswith("MET"), j
    assert j["T3"]["verdict"].startswith("REFUSED") and j["T4"]["verdict"].startswith("REFUSED"), j


def test_the_drift_reader_refuses_when_one_artifact_is_missing(tmp_path):
    a = _write(_run([0.06, 0.059, 0.058]))
    d = e335.drifts(a, tmp_path / "absent.json")
    assert d["runs"] == 0 and d["missing"], d


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e335_what_replay_stores.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e335.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["claims"][1]["verdict"].startswith("MET"), d["claims"][1]
    assert d["buffer"]["u_train_identical"], d["buffer"]
