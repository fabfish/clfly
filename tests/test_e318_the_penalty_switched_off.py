"""`e318` asks the controlled version of `e317`'s question -- one arm, one suite, the penalty dialled -- so the tests
pin the four-run layout, the config diff between settings, the per-arm contrast, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e318_the_penalty_switched_off as e318


def _run(names, learned, order="as-built", lam=0.0, circuit="MB", sha="abc", arms=("naive", "ewc"), extra=None):
    payload = {"tasks": [{"name": n} for n in names], "circuit": circuit,
               "config": dict({"task_order": order, "lam": lam,
                               "circuit_size": 300, "readout_size": 32, "seed0": 0}, **(extra or {})),
               "readout": {"subset_sha1": sha}, "methods": {}}
    for a in arms:
        payload["methods"][a] = {"replicates": [{"learned": l, "seed": 100 * i}
                                                for i, l in enumerate(learned)]}
    return payload


def _settings(tmp_path, off_learned, on_learned, names=("odour_identity", "heading", "odour_input")):
    """The four runs on disk, with the two settings given their own replicate lists."""
    for lam, learned in ((0.0, off_learned), (1.0, on_learned)):
        tag = f"lam{int(lam)}"
        (tmp_path / f"e318_{tag}_as_built.json").write_text(
            json.dumps(_run(names, learned, lam=lam)), encoding="utf-8")
        (tmp_path / f"e318_{tag}_reverse.json").write_text(
            json.dumps(_run(names[::-1], learned, order="reverse", lam=lam)), encoding="utf-8")


def test_the_reading_is_four_runs_at_two_settings(tmp_path):
    off = [[1.0, 0.5, 0.6], [1.0, 0.5, 0.6]]
    on = [[1.0, 0.5, 0.6], [0.8, 0.4, 0.5]]
    _settings(tmp_path, off, on)
    r = e318.reading(tmp_path)
    assert r["runs"] == 4 and set(r["settings"]) == {"0.0", "1.0"}, r
    assert r["config_fields_differing_between_settings"] == ["lam"], r
    for lam in ("0.0", "1.0"):
        v = r["settings"][lam]
        assert v["same_circuit"] and v["same_readout"] and v["reversed_names"], (lam, v)
        assert v["seeds"][0] == v["seeds"][1] and v["n"] == 2, (lam, v)
    # the arms and the control are read for the arm under test
    assert set(r["settings"]["1.0"]["tasks"]) == {"odour_identity", "heading", "odour_input"}, r
    assert r["settings"]["1.0"]["tasks"]["heading"]["moved"] is False, r["settings"]["1.0"]["tasks"]
    assert set(r["settings"]["1.0"]["ride_along"]) == {"odour_identity", "heading", "odour_input"}, r
    # and a missing run refuses rather than reading three of four
    (tmp_path / "e318_lam1_reverse.json").unlink()
    assert e318.reading(tmp_path)["runs"] == 0, e318.reading(tmp_path)


def test_the_pairing_is_by_replicate_and_reports_a_sigma():
    assert e318.paired([1.0, 1.0], [0.9, 0.9])["sigma"] == float("inf")
    q = e318.paired([1.0, 0.8, 0.6, 0.4], [0.9, 0.5, 0.4, 0.1])
    assert q["n"] == 4 and q["delta"] > 0 and 0 < q["sigma"] < float("inf"), q
    assert e318.paired([1.0], [0.5])["delta"] is None


def _reading(off_sigma=0.3, on_sigma=3.0, off_control=False, on_control=True,
             fields=("lam",), reversed_names=True):
    def rows(sigma):
        return {"odour_identity": {"forward_position": 0, "backward_position": 2, "moved": True, "n": 5,
                                   "delta": 0.05, "sem": 0.01, "sigma": sigma},
                "odour_input": {"forward_position": 2, "backward_position": 0, "moved": True, "n": 5,
                                "delta": -0.04, "sem": 0.01, "sigma": sigma},
                "heading": {"forward_position": 1, "backward_position": 1, "moved": False, "n": 5,
                            "delta": 0.001, "sem": 0.01, "sigma": 0.1}}

    def setting(sigma, control):
        return {"circuit": ["MB", "MB"], "same_circuit": True, "readout": ["abc", "abc"], "same_readout": True,
                "orders": ["as-built", "reverse"], "reversed_names": reversed_names, "seeds": [[0, 100], [0, 100]],
                "n": 5, "tasks": rows(sigma), "ride_along": rows(0.2), "control_smallest": control}
    return {"runs": 4, "settings": {"0.0": setting(off_sigma, off_control), "1.0": setting(on_sigma, on_control)},
            "config_fields_differing_between_settings": list(fields)}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e318.judge(_reading())}
    for cid in ("S1", "S2", "S3", "S4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a config that differs in more than `lam`, or a pair that is not a reversal, is S1's
    assert e318.judge(_reading(fields=("lam", "seed0")))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e318.judge(_reading(reversed_names=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a penalty-off contrast that clears the threshold is S2's
    assert e318.judge(_reading(off_sigma=2.0))[1]["verdict"].startswith("FALSIFIER FIRED")
    # a penalty-on contrast below it, or one against the position, is S3's
    assert e318.judge(_reading(on_sigma=0.5))[2]["verdict"].startswith("FALSIFIER FIRED")
    flipped = _reading()
    flipped["settings"]["1.0"]["tasks"]["odour_identity"] = dict(
        flipped["settings"]["1.0"]["tasks"]["odour_identity"], delta=-0.05)
    assert e318.judge(flipped)[2]["verdict"].startswith("FALSIFIER FIRED")
    # a control that does not separate the settings is S4's
    assert e318.judge(_reading(off_control=True))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e318.judge(_reading(on_control=False))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e318.judge({"runs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_four_runs_are_what_the_finding_says():
    r = e318.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["runs"] == 4 and set(r["settings"]) == {"0.0", "1.0"}, r
    assert r["config_fields_differing_between_settings"] == ["lam"], r
    for lam, v in r["settings"].items():
        assert v["same_circuit"] and v["same_readout"] and v["reversed_names"], (lam, v)
        assert v["seeds"][0] == v["seeds"][1] and v["n"] >= 5, (lam, v)
        moved = [x for x in v["tasks"].values() if x["moved"]]
        still = [x for x in v["tasks"].values() if not x["moved"]]
        assert len(moved) == 2 and len(still) == 1, (lam, v["tasks"])
        assert still[0]["forward_position"] == still[0]["backward_position"] == 1, still[0]
    claims = {x["id"]: x["verdict"] for x in e318.judge(r)}
    # as they read: the design is right, the penalty-on arm carries the direction at 2.75 and 4.33 sigma, the
    # control separates the settings -- and S2 fires because the penalty-off arm's larger contrast sits
    # exactly on the line, at 1.00 sigma
    for cid in ("S1", "S3", "S4"):
        assert claims[cid].startswith("MET"), claims[cid]
    assert claims["S2"].startswith("FALSIFIER FIRED"), claims["S2"]
    off = [x["sigma"] for x in r["settings"]["0.0"]["tasks"].values() if x["moved"]]
    on = [x["sigma"] for x in r["settings"]["1.0"]["tasks"].values() if x["moved"]]
    assert max(off) <= 1.0 < min(on), (off, on)


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e318_the_penalty_switched_off.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["runs"] == 4 and set(d["settings"]) == {"0.0", "1.0"}, d
    claims = {x["id"]: x["verdict"] for x in d["claims"]}
    for cid in ("S1", "S3", "S4"):
        assert claims[cid].startswith("MET"), claims[cid]
    assert claims["S2"].startswith("FALSIFIER FIRED"), claims["S2"]
