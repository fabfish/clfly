"""`e328` buys the resolution `e327`'s sweep lacked, so the tests pin the two-proportion arithmetic, the forgetting
threshold and what it counts, the config comparison, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e328_is_the_middling_loop_worse as e328


def test_the_two_proportion_sem_is_the_independent_one():
    # 8 of 40 against 40 of 40: the difference is 0.2 and its sem is sqrt(0.2*0.8/40), the second being degenerate
    sem = e328.two_proportion_sem(8, 40, 40, 40)
    assert abs(sem - (0.2 * 0.8 / 40) ** 0.5) < 1e-12, sem
    # and the same counts the other way round give the same sem, since it is symmetric
    assert abs(e328.two_proportion_sem(40, 40, 8, 40) - sem) < 1e-12
    # an undefined side refuses rather than dividing by zero
    assert e328.two_proportion_sem(0, 0, 1, 5) is None
    assert e328.proportion(1, 0) is None
    assert e328.proportion(3, 6) == 0.5


def _run(k_forget, n=40, seed0=0.0, learned=None, scale=0.0):
    reps = []
    for i in range(n):
        forgets = i < k_forget
        reps.append({"final_accuracy": 0.9 if forgets else 1.0,
                     "mean_forgetting": 0.2 if forgets else 0.0,
                     "learned": list(learned if learned is not None else [1.0, 1.0, 1.0])})
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_scale": scale, "seed0": 0},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"scale": scale, "n_cue": 12, "cue_sha1": "q"},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": {e328.NAIVE: {"replicates": reps}}}


def test_the_summary_counts_what_it_says_it_counts():
    s = e328.summarise(_run(3))
    assert s["n"] == 40 and s["n_forgetting"] == 3 and abs(s["rate"] - 0.075) < 1e-12, s
    # the threshold is what separates a forgetting replicate from a rounding artefact
    assert e328.summarise({"methods": {e328.NAIVE: {"replicates": [
        {"final_accuracy": 1.0, "mean_forgetting": 0.049, "learned": [1.0]}]}}})["n_forgetting"] == 0
    assert e328.summarise({"methods": {e328.NAIVE: {"replicates": [
        {"final_accuracy": 1.0, "mean_forgetting": 0.051, "learned": [1.0]}]}}})["n_forgetting"] == 1
    # and a replicate that never learned is recorded as such
    s = e328.summarise(_run(2, learned=[1.0, 0.5, 1.0]))
    assert s["n_forgetting"] == 2 and len(s["learned_short_of_perfect"]) == 2, s


def _reading(paths, tmp):
    a, b = tmp / "a.json", tmp / "b.json"
    a.write_text(json.dumps(_run(paths[0], scale=0.0)), encoding="utf-8")
    b.write_text(json.dumps(_run(paths[1], scale=0.5)), encoding="utf-8")
    return e328.reading({"0p00": a, "0p50": b})


def test_the_four_claims_read_both_faces(tmp_path):
    j = {row["id"]: row for row in e328.judge(_reading((2, 12), tmp_path))}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T2: no difference at all is the falsifier, and a small one is the null
    assert e328.judge(_reading((5, 5), tmp_path))[1]["verdict"].startswith("FALSIFIER")
    assert e328.judge(_reading((2, 4), tmp_path))[1]["verdict"].startswith("NULL")
    # T3: an open loop that never forgets
    assert e328.judge(_reading((0, 12), tmp_path))[2]["verdict"].startswith("FALSIFIER")
    assert e328.judge(_reading((1, 12), tmp_path))[2]["verdict"].startswith("NULL")
    # T4: a forgetting replicate that also failed to learn
    a, b = tmp_path / "c.json", tmp_path / "d.json"
    a.write_text(json.dumps(_run(3, learned=[1.0, 1.0, 0.9])), encoding="utf-8")
    b.write_text(json.dumps(_run(12, scale=0.5)), encoding="utf-8")
    assert e328.judge(e328.reading({"0p00": a, "0p50": b}))[3]["verdict"].startswith("FALSIFIER")
    # and one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e328.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = tmp_path / "a.json"
    a.write_text(json.dumps(_run(3)), encoding="utf-8")
    r = e328.reading({"0p00": a, "0p50": tmp_path / "absent.json"})
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e328.judge(r))


def test_the_live_pair_is_one_configuration_at_two_strengths():
    r = e328.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert r["scales"] == [0.0, 0.5], r["scales"]
    assert all(s["n"] == 40 for s in r["settings"].values()), r["settings"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e328_is_the_middling_loop_worse.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e328.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["scales"] == [0.0, 0.5], d["scales"]
