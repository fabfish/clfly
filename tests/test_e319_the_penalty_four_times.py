"""`e319` dials the penalty four times on one arm, so the tests pin the eight-run layout, the config diff between
settings, the median-sigma sequence, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e319_the_penalty_four_times as e319


def _run(names, learned, order="as-built", lam=0.0, circuit="MB", sha="abc", arms=("naive", "ewc")):
    payload = {"tasks": [{"name": n} for n in names], "circuit": circuit,
               "config": {"task_order": order, "lam": lam, "circuit_size": 300, "readout_size": 32, "seed0": 0},
               "readout": {"subset_sha1": sha}, "methods": {}}
    for a in arms:
        payload["methods"][a] = {"replicates": [{"learned": l, "seed": 100 * i}
                                                for i, l in enumerate(learned)]}
    return payload


def _settings(tmp_path, by_lam, names=("odour_identity", "heading", "odour_input")):
    for lam, learned in by_lam.items():
        tag = f"lam{str(lam).replace('.', 'p')}"
        (tmp_path / f"e319_{tag}_asbuilt.json").write_text(
            json.dumps(_run(names, learned, lam=lam)), encoding="utf-8")
        (tmp_path / f"e319_{tag}_reverse.json").write_text(
            json.dumps(_run(names[::-1], learned, order="reverse", lam=lam)), encoding="utf-8")


def test_the_reading_is_eight_runs_at_four_settings(tmp_path):
    # a swap that grows with the penalty, so the median-sigma sequence has a step to read
    _settings(tmp_path, {0.0: [[1.0, 0.5, 0.6]] * 2, 0.1: [[1.02, 0.5, 0.6]] * 2,
                         1.0: [[1.06, 0.5, 0.6]] * 2, 3.0: [[1.06, 0.5, 0.6]] * 2})
    r = e319.reading(tmp_path)
    assert r["runs"] == 8 and set(r["settings"]) == set(e319.LAMBDAS), r
    assert r["config_fields_differing_between_settings"] == [], r
    for lam in e319.LAMBDAS:
        v = r["settings"][lam]
        assert v["same_circuit"] and v["same_readout"] and v["reversed_names"], (lam, v)
        assert v["orders"] == ["as-built", "reverse"] and v["seeds"][0] == v["seeds"][1], (lam, v)
        assert len(v["moved_sigmas"]) == 2 and len(v["ride_along"]) == 3, (lam, v)
    # and a missing run refuses rather than reading seven of eight
    (tmp_path / "e319_lam3p0_reverse.json").unlink()
    assert e319.reading(tmp_path)["runs"] == 0, e319.reading(tmp_path)


def test_the_pairing_reports_a_sigma_and_refuses_too_few_replicates():
    assert e319.paired([1.0, 1.0], [0.9, 0.9])["sigma"] == float("inf")
    q = e319.paired([1.0, 0.8, 0.6, 0.4], [0.9, 0.5, 0.4, 0.1])
    assert q["n"] == 4 and q["delta"] > 0 and 0 < q["sigma"] < float("inf"), q
    assert e319.paired([1.0], [0.5])["delta"] is None


def _reading(medians=(0.5, 1.5, 3.0, 3.0), deltas=(0.001, 0.02, 0.06, 0.06), fields=(), pairs=True):
    settings = {}
    for i, lam in enumerate(e319.LAMBDAS):
        sig = medians[i]
        tasks = {"odour_identity": {"forward_position": 0, "backward_position": 2, "moved": True, "n": 5,
                                    "delta": deltas[i], "sem": 0.01, "sigma": sig},
                 "odour_input": {"forward_position": 2, "backward_position": 0, "moved": True, "n": 5,
                                 "delta": -deltas[i], "sem": 0.01, "sigma": sig},
                 "heading": {"forward_position": 1, "backward_position": 1, "moved": False, "n": 5,
                             "delta": 0.001, "sem": 0.01, "sigma": 0.1}}
        settings[lam] = {"same_circuit": pairs, "same_readout": pairs, "orders": ["as-built", "reverse"],
                         "reversed_names": pairs, "seeds": [[0, 100], [0, 100]], "n": 5, "tasks": tasks,
                         "ride_along": tasks, "median_sigma": sig, "moved_sigmas": [sig, sig],
                         "control_smallest": sig >= 1.0, "config": {}}
    return {"runs": 8, "settings": settings, "config_fields_differing_between_settings": list(fields)}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e319.judge(_reading())}
    for cid in ("D1", "D2", "D3", "D4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a config that differs in more than the ignored keys, or a pair that is not a reversal, is D1's
    assert e319.judge(_reading(fields=("seed0",)))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e319.judge(_reading(pairs=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a median that falls at one step is D2's
    assert e319.judge(_reading(medians=(0.5, 1.5, 1.0, 2.0)))[1]["verdict"].startswith("FALSIFIER FIRED")
    # every penalty above the line, or every penalty below it, is D3's
    assert e319.judge(_reading(medians=(2.0, 2.0, 2.0, 2.0)))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e319.judge(_reading(medians=(0.5, 0.6, 0.7, 0.8)))[2]["verdict"].startswith("FALSIFIER FIRED")
    # a resolved contrast against the position is D4's
    bad = _reading()
    bad["settings"]["1.0"]["tasks"]["odour_identity"] = dict(
        bad["settings"]["1.0"]["tasks"]["odour_identity"], delta=-0.06)
    assert e319.judge(bad)[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e319.judge({"runs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_eight_runs_are_what_the_finding_says():
    r = e319.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["runs"] == 8 and set(r["settings"]) == set(e319.LAMBDAS), r
    assert r["config_fields_differing_between_settings"] == [], r
    for lam, v in r["settings"].items():
        assert v["same_circuit"] and v["same_readout"] and v["reversed_names"], (lam, v)
        assert v["orders"] == ["as-built", "reverse"] and v["seeds"][0] == v["seeds"][1], (lam, v)
        assert v["n"] >= 5, (lam, v["n"])
        moved = [x for x in v["tasks"].values() if x["moved"]]
        still = [x for x in v["tasks"].values() if not x["moved"]]
        assert len(moved) == 2 and len(still) == 1, (lam, v["tasks"])
    claims = {x["id"]: x["verdict"] for x in e319.judge(r)}
    # as they read: the design is right and the direction is the position's wherever it resolves, while D2
    # fires because the effect saturates at the first step and D3 because the range holds no penalty below
    # the line -- the one that would is `lam = 0.0`, whose larger contrast sits exactly on it
    for cid in ("D1", "D4"):
        assert claims[cid].startswith("MET"), claims[cid]
    for cid in ("D2", "D3"):
        assert claims[cid].startswith("FALSIFIER FIRED"), claims[cid]
    med = {lam: r["settings"][lam]["median_sigma"] for lam in e319.LAMBDAS}
    assert med["0.0"] < 1.0 < min(med[lam] for lam in ("0.1", "1.0", "3.0")), med
    # the constant that rides along does not read `lam`, so its contrasts are identical at every setting
    ride = {lam: [round(x["sigma"], 6) for x in r["settings"][lam]["ride_along"].values() if x["moved"]]
            for lam in e319.LAMBDAS}
    assert len({tuple(v) for v in ride.values()}) == 1, ride


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e319_the_penalty_four_times.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["runs"] == 8 and set(d["settings"]) == set(e319.LAMBDAS), d
    claims = {x["id"]: x["verdict"] for x in d["claims"]}
    assert claims["D1"].startswith("MET") and claims["D4"].startswith("MET"), claims
    assert claims["D2"].startswith("FALSIFIER FIRED"), claims["D2"]
    assert claims["D3"].startswith("FALSIFIER FIRED"), claims["D3"]
