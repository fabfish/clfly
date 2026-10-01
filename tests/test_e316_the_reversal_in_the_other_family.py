"""`e316` runs the reversal a second time on the assembly family, so the tests pin the pair reader, the position map,
the within-method control, both faces of the four claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e316_the_reversal_in_the_other_family as e316


def _run(names, learned, order="as-built", circuit="MB", sha="abc"):
    return {"tasks": [{"name": n} for n in names], "circuit": circuit,
            "config": {"task_order": order},
            "readout": {"subset_sha1": sha},
            "methods": {"naive": {"replicates": [{"learned": l, "seed": 100 * i}
                                                 for i, l in enumerate(learned)]}}}


def test_the_pair_reading_maps_positions_and_flags_the_control(tmp_path):
    fwd = tmp_path / "f.json"
    bwd = tmp_path / "b.json"
    fwd.write_text(json.dumps(_run(("odour_identity", "heading", "odour_input"),
                                   [[1.0, 0.5, 0.6], [1.0, 0.5, 0.6]])), encoding="utf-8")
    bwd.write_text(json.dumps(_run(("odour_input", "heading", "odour_identity"),
                                   [[0.4, 0.5, 0.7], [0.4, 0.5, 0.7]], order="reverse")), encoding="utf-8")
    r = e316.pair_reading(e316.load(fwd), e316.load(bwd))
    assert r["same_circuit"] is True and r["same_readout"] is True, r
    assert r["reversed_names"] is True and r["orders"] == ["as-built", "reverse"], r
    tasks = r["by_method"]["naive"]["tasks"]
    assert tasks["odour_identity"]["forward_position"] == 0 and tasks["odour_identity"]["backward_position"] == 2
    assert tasks["heading"]["moved"] is False and tasks["heading"]["forward_position"] == 1, tasks["heading"]
    # t0 forwards 1.0 against t0 backwards 0.7, paired by replicate
    assert abs(tasks["odour_identity"]["delta"] - 0.3) < 1e-12, tasks["odour_identity"]
    # the control is the middle task and its sigma is the smallest of the three, since it does not move at all
    assert r["by_method"]["naive"]["control_smallest"] is True, r["by_method"]["naive"]
    # and a read-out that differs is caught rather than assumed equal
    assert e316.pair_reading(e316.load(fwd), {**e316.load(bwd), "readout": {"subset_sha1": "zzz"}})[
        "same_readout"] is False


def test_the_pairing_reports_a_sigma_and_refuses_too_few_replicates():
    p = e316.paired([1.0, 1.0], [0.9, 0.9])
    assert abs(p["delta"] - 0.1) < 1e-12 and p["sigma"] == float("inf"), p
    q = e316.paired([1.0, 0.8, 0.6, 0.4], [0.9, 0.5, 0.4, 0.1])
    assert q["n"] == 4 and q["delta"] > 0 and 0 < q["sigma"] < float("inf"), q
    assert e316.paired([1.0], [0.5])["delta"] is None


def _reading(moved=None, control=None, same_circuit=True, same_readout=True, reversed_names=True, n=10):
    moved = moved if moved is not None else {
        "odour_identity": {"forward_position": 0, "backward_position": 2, "moved": True,
                           "n": n, "delta": 0.08, "sem": 0.02, "sigma": 4.0},
        "odour_input": {"forward_position": 2, "backward_position": 0, "moved": True,
                        "n": n, "delta": -0.07, "sem": 0.02, "sigma": 3.5}}
    control = control if control is not None else {
        "heading": {"forward_position": 1, "backward_position": 1, "moved": False,
                    "n": n, "delta": 0.001, "sem": 0.02, "sigma": 0.05}}
    tasks = dict(moved, **control)
    # derived from the tasks rather than set independently, so the fixture cannot be inconsistent with itself --
    # which is what the module does, and what the Q3 falsifier has to be able to reach
    smallest = (min((x["sigma"] or 0) for x in tasks.values() if not x["moved"])
                < min((x["sigma"] or 0) for x in tasks.values() if x["moved"]))
    return {"runs": 2, "circuits": ["MB", "MB"], "same_circuit": same_circuit,
            "readout_subsets": ["abc", "abc"], "same_readout": same_readout,
            "orders": ["as-built", "reverse"], "names": [["a", "b", "c"], ["c", "b", "a"]],
            "reversed_names": reversed_names, "same_seeds": True,
            "by_method": {"naive": {"n": n, "tasks": tasks, "control_smallest": smallest}},
            "earlier": {"present": False}}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e316.judge(_reading())}
    for cid in ("Q1", "Q2", "Q3", "Q4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a differing circuit, read-out or task list is Q1's
    assert e316.judge(_reading(same_circuit=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e316.judge(_reading(same_readout=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e316.judge(_reading(reversed_names=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a moved task that is higher in the run that trains it last is Q2's
    flipped = dict(_reading()["by_method"]["naive"]["tasks"])
    flipped["odour_identity"] = dict(flipped["odour_identity"], delta=-0.08)
    assert e316.judge(_reading(moved={"odour_identity": flipped["odour_identity"],
                                      "odour_input": flipped["odour_input"]}))[1][
        "verdict"].startswith("FALSIFIER FIRED")
    # a control that is not the quietest contrast in a method is Q3's
    loud = {"heading": dict(_reading()["by_method"]["naive"]["tasks"]["heading"], sigma=9.0)}
    assert e316.judge(_reading(control=loud))[2]["verdict"].startswith("FALSIFIER FIRED")
    # a largest contrast below the threshold is Q4's
    small = {"odour_identity": dict(_reading()["by_method"]["naive"]["tasks"]["odour_identity"], sigma=1.5),
             "odour_input": dict(_reading()["by_method"]["naive"]["tasks"]["odour_input"], sigma=1.2)}
    assert e316.judge(_reading(moved=small))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e316.judge({"runs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_two_runs_are_what_the_finding_says():
    r = e316.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["same_circuit"] is True and r["same_readout"] is True, r
    assert r["reversed_names"] is True and r["orders"] == ["as-built", "reverse"], r
    assert r["same_seeds"] is True and r["by_method"], r
    moved_all = []
    for m, v in r["by_method"].items():
        moved = [x for x in v["tasks"].values() if x["moved"]]
        still = [x for x in v["tasks"].values() if not x["moved"]]
        # the design: the middle task keeps its position under a reversal of three
        assert len(moved) == 2 and len(still) == 1, (m, v["tasks"])
        assert still[0]["forward_position"] == still[0]["backward_position"] == 1, still[0]
        assert v["n"] >= 10, v["n"]
        moved_all += moved
    claims = {x["id"]: x["verdict"] for x in e316.judge(r)}
    # the registered claims as they read: the design is right, the family's direction is not unanimous, its control
    # holds in one method, and the effect it does carry is large
    assert claims["Q1"].startswith("MET"), claims["Q1"]
    assert claims["Q4"].startswith("MET"), claims["Q4"]
    assert claims["Q2"].startswith("FALSIFIER FIRED"), claims["Q2"]
    assert claims["Q3"].startswith("FALSIFIER FIRED"), claims["Q3"]
    # and the substance: one method carries the position effect at several sigma and the other two do not
    by_method = {}
    for m, v in r["by_method"].items():
        by_method[m] = [x for x in v["tasks"].values() if x["moved"]]
    biggest = {m: max(x["sigma"] for x in xs) for m, xs in by_method.items()}
    assert max(biggest.values()) >= 4.0, biggest
    assert sum(1 for v in biggest.values() if v >= 2.0) == 1, biggest
    assert len(moved_all) == 6, moved_all
    assert sum(1 for x in moved_all if x["sigma"] >= 1.0) == 2, [x["sigma"] for x in moved_all]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e316_the_reversal_in_the_other_family.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["reversed_names"] is True and d["runs"] == 2, d
    claims = {x["id"]: x["verdict"] for x in d["claims"]}
    for cid in ("Q1", "Q4"):
        assert claims[cid].startswith("MET"), claims[cid]
    for cid in ("Q2", "Q3"):
        assert claims[cid].startswith("FALSIFIER FIRED"), claims[cid]
