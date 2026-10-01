"""`e331` asks the line's headline ordering on the environment with headroom, so the tests pin the within-run
pairing, the two-sided loop move, the config comparison, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e331_the_ordering_under_the_loop as e331


def test_paired_and_the_within_run_contrast():
    p = e331.paired([0.9, 0.8, 0.7], [0.5, 0.5, 0.5])
    assert p["n"] == 3 and abs(p["delta"] - 0.3) < 1e-12, p
    assert e331.paired([0.9], [0.5])["delta"] is None, e331.paired([0.9], [0.5])
    run = {"methods": {"a": {"replicates": [{"final_accuracy": 0.9}, {"final_accuracy": 0.8}]},
                       "b": {"replicates": [{"final_accuracy": 0.5}, {"final_accuracy": 0.4}]}}}
    c = e331.arm_contrast(run, "a", "b")
    assert abs(c["delta"] - 0.4) < 1e-12 and c["sigma"] == float("inf"), c


def _run(accs, n=5, scale=0.0, forgets=None):
    """``accs`` maps arm to a base accuracy; each arm's replicates step by 0.01 so a paired sem is defined."""
    methods = {}
    for arm, base in accs.items():
        methods[arm] = {"final_accuracy": base, "mean_forgetting": 0.2,
                        "replicates": [{"final_accuracy": base + 0.01 * i,
                                        "mean_forgetting": (forgets or {}).get(arm, 0.2) + 0.001 * i}
                                       for i in range(n)]}
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_scale": scale, "loop_noise": 1.0},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"scale": scale, "noise": 1.0, "n_symbols": 24, "n_cue": 12},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": methods}


def _reading(replay_gap=0.10, loop_gap=0.15, config_diff=None, env_diff=None, same_counts=True):
    """``replay_gap`` is its lead on the open loop and ``loop_gap`` the one it has under the loop."""
    base = {"naive": 0.50, "ewc": 0.48, "ewc-block": 0.46, "ewc-block-rand": 0.47}
    open_accs = dict(base, **{e331.REPLAY: 0.50 + replay_gap})
    loop_accs = dict(base, **{e331.REPLAY: 0.50 + (loop_gap if loop_gap is not None else replay_gap)})
    a = _run(open_accs, scale=0.0)
    b = _run(loop_accs, n=5 if same_counts else 4, scale=0.5)
    if config_diff:
        b["config"].update({k: v[1] for k, v in config_diff.items()})
    if env_diff:
        b["env_draw"].update({k: v[1] for k, v in env_diff.items()})
    return e331.reading({"0p00": _write(a), "0p50": _write(b)})


def _write(payload, path=None):
    import tempfile
    if path is None:
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, fh)
        fh.close()
        return Path(fh.name)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_the_four_claims_read_both_faces(tmp_path):
    j = {row["id"]: row for row in e331.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a differing circuit, count, or an unexpected config or environment field
    a = _run({"naive": 0.5, "ewc": 0.48, "ewc-block": 0.46, "ewc-block-rand": 0.47, "replay": 0.6}, scale=0.0)
    b = _run({"naive": 0.5, "ewc": 0.48, "ewc-block": 0.46, "ewc-block-rand": 0.47, "replay": 0.6}, n=4, scale=0.5)
    b["circuit"] = "MB2"
    r = e331.reading({"0p00": _write(a), "0p50": _write(b)})
    assert e331.judge(r)[0]["verdict"].startswith("FALSIFIER")

    # T2 and T3: `replay` behind on a penalty arm, and unresolved on one
    assert e331.judge(_reading(replay_gap=-0.10))[1]["verdict"].startswith("FALSIFIER")
    assert e331.judge(_reading(replay_gap=-0.10, loop_gap=-0.10))[2]["verdict"].startswith("FALSIFIER")
    # T4: a move under the STILL bar fires, one between it and MOVED is the null, and a large one is the MET
    assert e331.judge(_reading(replay_gap=0.10, loop_gap=0.105))[3]["verdict"].startswith("FALSIFIER")
    assert e331.judge(_reading(replay_gap=0.10, loop_gap=0.12))[3]["verdict"].startswith("NULL")
    assert e331.judge(_reading(replay_gap=0.10, loop_gap=0.15))[3]["verdict"].startswith("MET")

    # and one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e331.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = _write(_run({"naive": 0.5, "ewc": 0.48, "ewc-block": 0.46, "ewc-block-rand": 0.47, "replay": 0.6}))
    r = e331.reading({"0p00": a, "0p50": tmp_path / "absent.json"})
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e331.judge(r))


def test_the_live_pair_is_one_configuration_in_two_loops():
    r = e331.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert set(r["arms"]) == set(e331.ARMS), r["arms"]
    assert all(v == [5, 5] for v in r["n_replicates"].values()), r["n_replicates"]
    assert r["env"]["noise"] == 1.0 and r["env"]["n_symbols"] == 24, r["env"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e331_the_ordering_under_the_loop.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e331.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert len(d["ordering"]) == 3, d["ordering"]
