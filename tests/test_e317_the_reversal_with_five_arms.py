"""`e317` reverses the assembly suite with all five arms, so the tests pin the penalty/non-penalty split, the position
map, the within-arm control, both faces of the four claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e317_the_reversal_with_five_arms as e317


def _run(names, learned, order="as-built", circuit="MB", sha="abc", arms=("naive",)):
    payload = {"tasks": [{"name": n} for n in names], "circuit": circuit,
               "config": {"task_order": order}, "readout": {"subset_sha1": sha}, "methods": {}}
    for a in arms:
        payload["methods"][a] = {"replicates": [{"learned": l, "seed": 100 * i}
                                                for i, l in enumerate(learned)]}
    return payload


def test_the_reading_splits_the_arms_that_read_a_penalty_from_those_that_do_not(tmp_path):
    names = ("odour_identity", "heading", "odour_input")
    fwd = tmp_path / "f.json"
    bwd = tmp_path / "b.json"
    fwd.write_text(json.dumps(_run(names, [[1.0, 0.5, 0.6], [1.0, 0.5, 0.6]], arms=e317.ARMS)), encoding="utf-8")
    bwd.write_text(json.dumps(_run(names[::-1], [[0.4, 0.5, 0.7], [0.4, 0.5, 0.7]], order="reverse",
                                   arms=e317.ARMS)), encoding="utf-8")
    r = e317.reading(fwd, bwd)
    assert r["same_circuit"] is True and r["same_readout"] is True and r["reversed_names"] is True, r
    assert set(r["by_method"]) == set(e317.ARMS), sorted(r["by_method"])
    assert [m for m, v in r["by_method"].items() if v["reads_a_penalty"]] == list(e317.PENALTY), r["by_method"]
    for m, v in r["by_method"].items():
        moved = [x for x in v["tasks"].values() if x["moved"]]
        still = [x for x in v["tasks"].values() if not x["moved"]]
        assert len(moved) == 2 and len(still) == 1, (m, v["tasks"])
        assert still[0]["forward_position"] == still[0]["backward_position"] == 1, still[0]
        # the middle task does not move at all, so it is the quietest contrast
        assert v["control_smallest"] is True, (m, v)
    # and the pairing is by replicate: odour_identity forwards 1.0 against backwards 0.7
    assert abs(r["by_method"]["naive"]["tasks"]["odour_identity"]["delta"] - 0.3) < 1e-12, r["by_method"]["naive"]


def test_the_pairing_reports_a_sigma_and_refuses_too_few_replicates():
    assert e317.paired([1.0, 1.0], [0.9, 0.9])["sigma"] == float("inf")
    q = e317.paired([1.0, 0.8, 0.6, 0.4], [0.9, 0.5, 0.4, 0.1])
    assert q["n"] == 4 and q["delta"] > 0 and 0 < q["sigma"] < float("inf"), q
    assert e317.paired([1.0], [0.5])["delta"] is None


def _tasks(sigma_forward=2.0, sigma_back=2.0, control=0.1):
    return {"odour_identity": {"forward_position": 0, "backward_position": 2, "moved": True, "n": 5,
                               "delta": 0.05, "sem": 0.01, "sigma": sigma_forward},
            "odour_input": {"forward_position": 2, "backward_position": 0, "moved": True, "n": 5,
                            "delta": -0.04, "sem": 0.01, "sigma": sigma_back},
            "heading": {"forward_position": 1, "backward_position": 1, "moved": False, "n": 5,
                        "delta": 0.001, "sem": 0.01, "sigma": control}}


def _reading(methods=None):
    if methods is None:
        methods = {}
        for m in e317.ARMS:
            tasks = _tasks(2.0, 2.0) if m in e317.PENALTY else _tasks(0.5, 0.5)
            moved = [x for x in tasks.values() if x["moved"]]
            still = [x for x in tasks.values() if not x["moved"]]
            methods[m] = {"n": 5, "tasks": tasks, "reads_a_penalty": m in e317.PENALTY,
                          "control_smallest": min(x["sigma"] for x in still) < min(x["sigma"] for x in moved)}
    return {"runs": 2, "circuits": ["MB", "MB"], "same_circuit": True, "readout_subsets": ["abc", "abc"],
            "same_readout": True, "orders": ["as-built", "reverse"],
            "names": [["a", "b", "c"], ["c", "b", "a"]], "reversed_names": True, "same_seeds": True,
            "by_method": methods}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e317.judge(_reading())}
    for cid in ("R1", "R2", "R3", "R4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a differing circuit, read-out or task list is R1's
    bad = _reading()
    bad["same_readout"] = False
    assert e317.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED")
    bad = _reading()
    bad["reversed_names"] = False
    assert e317.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED")
    # a minority of the arms carrying the direction is R2's
    late = {}
    for m in e317.ARMS:
        tasks = _tasks(2.0, 2.0) if m == "ewc" else _tasks(0.5, 0.5)
        tasks["odour_identity"] = dict(tasks["odour_identity"], delta=-abs(tasks["odour_identity"]["delta"]))
        tasks["odour_input"] = dict(tasks["odour_input"], delta=abs(tasks["odour_input"]["delta"]))
        late[m] = {"n": 5, "tasks": tasks, "reads_a_penalty": m in e317.PENALTY, "control_smallest": True}
    assert e317.judge(_reading(methods=late))[1]["verdict"].startswith("FALSIFIER FIRED")
    # a non-penalty arm clearing one sigma is R3's
    loud = _reading()
    loud["by_method"]["replay"]["tasks"] = _tasks(3.0, 3.0)
    assert e317.judge(loud)[2]["verdict"].startswith("FALSIFIER FIRED")
    # fewer than three arms with the control quietest is R4's
    few = _reading()
    for m in ("naive", "replay", "ewc-block"):
        few["by_method"][m]["control_smallest"] = False
    assert e317.judge(few)[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e317.judge({"runs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_two_runs_are_what_the_finding_says():
    r = e317.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["same_circuit"] is True and r["same_readout"] is True and r["reversed_names"] is True, r
    assert r["orders"] == ["as-built", "reverse"] and r["same_seeds"] is True, r
    assert set(r["by_method"]) == set(e317.ARMS), sorted(r["by_method"])
    for m, v in r["by_method"].items():
        assert v["n"] == 5, (m, v["n"])
        moved = [x for x in v["tasks"].values() if x["moved"]]
        still = [x for x in v["tasks"].values() if not x["moved"]]
        assert len(moved) == 2 and len(still) == 1, (m, v["tasks"])
    claims = {x["id"]: x["verdict"] for x in e317.judge(r)}
    # as they read: the direction is nearly unanimous, the control holds in exactly the penalty arms, and
    # R3 fires on one `naive` contrast that sits on the threshold
    for cid in ("R1", "R2", "R4"):
        assert claims[cid].startswith("MET"), claims[cid]
    assert claims["R3"].startswith("FALSIFIER FIRED"), claims["R3"]
    moved = [(m, x) for m, v in r["by_method"].items() for x in v["tasks"].values() if x["moved"]]
    firsts = [1 for m, x in moved
              if (x["forward_position"] == 0 and x["delta"] > 0)
              or (x["backward_position"] == 0 and x["delta"] < 0)]
    assert len(moved) == 10 and len(firsts) == 9, (len(moved), len(firsts))
    cleared = {m for m, x in moved if x["sigma"] >= 1.0}
    assert cleared == set(e317.PENALTY) | {"naive"}, cleared
    assert sum(1 for m, x in moved if m == "replay" and x["sigma"] >= 1.0) == 0, "replay cleared"
    held = {m for m, v in r["by_method"].items() if v["control_smallest"]}
    assert held == set(e317.PENALTY), held


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e317_the_reversal_with_five_arms.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["reversed_names"] is True and d["runs"] == 2, d
    claims = {x["id"]: x["verdict"] for x in d["claims"]}
    for cid in ("R1", "R2", "R4"):
        assert claims[cid].startswith("MET"), claims[cid]
    assert claims["R3"].startswith("FALSIFIER FIRED"), claims["R3"]
