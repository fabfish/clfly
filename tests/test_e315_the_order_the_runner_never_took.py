"""`e315` reads one suite trained in two orders, so the tests pin the level reader, the pairing, the position map,
both faces of the four claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e315_the_order_the_runner_never_took as e315


def _run(names, learned_by_replicate, order="as-built", fingerprint="abc"):
    return {"tasks": [{"name": n} for n in names],
            "config": {"task_order": order},
            "support_draw": {"fingerprint_sha1": fingerprint},
            "methods": {"naive": {"replicates": [{"learned": l, "seed": 100 * i}
                                                 for i, l in enumerate(learned_by_replicate)]}}}


def test_the_levels_and_the_positions_come_off_the_run(tmp_path):
    a = _run(("ov1_t0", "ov1_t1", "ov1_t2"), [[1.0, 0.9, 0.8], [1.0, 0.9, 0.8]])
    assert e315.positions(a) == ["ov1_t0", "ov1_t1", "ov1_t2"]
    assert e315.levels(a, "naive") == [[1.0, 0.9, 0.8], [1.0, 0.9, 0.8]], e315.levels(a, "naive")
    # a replicate that did not record the levels is not a replicate with zeros in it
    a["methods"]["naive"]["replicates"].append({"seed": 999})
    assert e315.levels(a, "naive") == [], e315.levels(a, "naive")
    assert e315.load(tmp_path / "absent.json") is None


def test_the_pairing_is_by_replicate_and_reports_a_sigma():
    p = e315.paired([1.0, 1.0, 1.0], [0.9, 0.9, 0.9])
    assert p["n"] == 3 and abs(p["delta"] - 0.1) < 1e-12 and p["sem"] < 1e-12, p
    assert p["sigma"] == float("inf"), p
    # a difference that moves with the replicate has a spread and a finite sigma
    q = e315.paired([1.0, 0.9, 0.8, 0.7], [0.5, 0.4, 0.35, 0.2])
    assert q["n"] == 4 and q["delta"] > 0 and 0 < q["sigma"] < float("inf"), q
    assert e315.paired([1.0], [0.5])["delta"] is None


def test_the_reading_maps_positions_and_marks_which_task_moved(tmp_path):
    fwd = tmp_path / "f.json"
    bwd = tmp_path / "b.json"
    fwd.write_text(json.dumps(_run(("ov1_t0", "ov1_t1", "ov1_t2"),
                                   [[1.0, 0.5, 0.6], [1.0, 0.5, 0.6]])), encoding="utf-8")
    bwd.write_text(json.dumps(_run(("ov1_t2", "ov1_t1", "ov1_t0"),
                                   [[0.4, 0.5, 0.7], [0.4, 0.5, 0.7]], order="reverse")), encoding="utf-8")
    r = e315.reading(fwd, bwd)
    assert r["same_fingerprint"] is True and r["reversed_names"] is True, r
    assert r["orders"] == ["as-built", "reverse"], r["orders"]
    tasks = r["by_method"]["naive"]["tasks"]
    # ov1_t0 is first forwards and last backwards, ov1_t1 is in the middle both ways
    assert tasks["ov1_t0"]["moved"] is True and (tasks["ov1_t0"]["forward_position"],
                                                tasks["ov1_t0"]["backward_position"]) == (0, 2), tasks["ov1_t0"]
    assert tasks["ov1_t2"]["moved"] is True, tasks["ov1_t2"]
    assert tasks["ov1_t1"]["moved"] is False, tasks["ov1_t1"]
    # and the pairing is by replicate: t0 forwards 1.0 against t0 backwards 0.7
    assert abs(tasks["ov1_t0"]["delta"] - 0.3) < 1e-12, tasks["ov1_t0"]


def _reading(moved=None, still=None, fingerprint=("abc", "abc"), reversed_names=True):
    moved = moved if moved is not None else {
        "ov1_t0": {"forward_position": 0, "backward_position": 2, "moved": True,
                   "n": 5, "delta": 0.05, "sem": 0.01, "sigma": 5.0},
        "ov1_t2": {"forward_position": 2, "backward_position": 0, "moved": True,
                   "n": 5, "delta": -0.04, "sem": 0.01, "sigma": 4.0}}
    still = still if still is not None else {
        "ov1_t1": {"forward_position": 1, "backward_position": 1, "moved": False,
                   "n": 5, "delta": 0.001, "sem": 0.01, "sigma": 0.1}}
    return {"runs": 2, "orders": ["as-built", "reverse"],
            "same_fingerprint": fingerprint[0] == fingerprint[1], "fingerprints": list(fingerprint),
            "reversed_names": reversed_names, "names": [["ov1_t0", "ov1_t1", "ov1_t2"],
                                                        ["ov1_t2", "ov1_t1", "ov1_t0"]],
            "by_method": {"naive": {"n": 5, "tasks": dict(moved, **still)}}, "same_seeds": True}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e315.judge(_reading())}
    for cid in ("P1", "P2", "P3", "P4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a moved fingerprint is P1's, and so is a task list that is not a reversal
    assert e315.judge(_reading(fingerprint=("abc", "def")))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e315.judge(_reading(reversed_names=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a moved task that does not clear a sigma is P2's
    weak = dict(_reading()["by_method"]["naive"]["tasks"])
    weak["ov1_t0"] = dict(weak["ov1_t0"], sigma=0.3)
    assert e315.judge(_reading(moved={"ov1_t0": weak["ov1_t0"], "ov1_t2": weak["ov1_t2"]}))[1][
        "verdict"].startswith("FALSIFIER FIRED")
    # a task higher in the run that trains it LAST is P3's
    flipped = {"ov1_t0": dict(weak["ov1_t0"], sigma=5.0, delta=-0.05),
               "ov1_t2": dict(weak["ov1_t2"], sigma=4.0, delta=0.04)}
    assert e315.judge(_reading(moved=flipped))[2]["verdict"].startswith("FALSIFIER FIRED")
    # and a control that moves as much as the tasks that did is P4's
    loud = {"ov1_t1": dict(_reading()["by_method"]["naive"]["tasks"]["ov1_t1"], sigma=9.0)}
    assert e315.judge(_reading(still=loud))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e315.judge({"runs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_two_runs_are_what_the_finding_says():
    r = e315.reading()
    if not r.get("runs"):
        return                       # the artifacts are written by the runs this unit reads
    assert r["same_fingerprint"] is True and r["reversed_names"] is True, r
    assert r["orders"] == ["as-built", "reverse"], r["orders"]
    assert r["same_seeds"] is True, r["same_seeds"]
    assert r["by_method"], r
    moved_all, control_held = [], []
    for m, v in r["by_method"].items():
        moved = [x for x in v["tasks"].values() if x["moved"]]
        still = [x for x in v["tasks"].values() if not x["moved"]]
        assert len(moved) == 2 and len(still) == 1, (m, v["tasks"])
        # the design: the middle task keeps its position under a reversal of three
        assert still[0]["forward_position"] == still[0]["backward_position"] == 1, still[0]
        moved_all += moved
        control_held.append(still[0]["sigma"] < min(x["sigma"] for x in moved))
    claims = {x["id"]: x["verdict"] for x in e315.judge(r)}
    # the registered claims, as they read: the direction is unanimous and the magnitude is partial
    assert claims["P1"].startswith("MET"), claims["P1"]
    assert claims["P3"].startswith("MET"), claims["P3"]
    assert claims["P2"].startswith("FALSIFIER FIRED"), claims["P2"]
    assert claims["P4"].startswith("FALSIFIER FIRED"), claims["P4"]
    # and the substance the two registered wordings turned on
    favours_first = all((x["forward_position"] == 0 and x["delta"] > 0) or
                        (x["backward_position"] == 0 and x["delta"] < 0) for x in moved_all)
    assert favours_first and len(moved_all) == 6, (favours_first, moved_all)
    assert sum(1 for x in moved_all if x["sigma"] >= 1.0) == 4, [x["sigma"] for x in moved_all]
    assert sum(control_held) == 2, control_held


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e315_the_order_the_runner_never_took.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["same_fingerprint"] is True and d["reversed_names"] is True, d
    claims = {x["id"]: x["verdict"] for x in d["claims"]}
    assert claims["P1"].startswith("MET"), claims["P1"]
    assert claims["P3"].startswith("MET"), claims["P3"]
    assert claims["P2"].startswith("FALSIFIER FIRED"), claims["P2"]
    assert claims["P4"].startswith("FALSIFIER FIRED"), claims["P4"]
