"""`e481` reads the first runner artifact that carries a policy, so the tests pin both faces of the four claims, the
inert rule that admits the older roll, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e481_the_benchmark_carries_a_policy as e481
from experiments.e172_parser_registry import parser_keys

ARMS = e481.ARMS


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same=None, inert=None, shared_differ=False, flags=(None, True), reps=20, moves=None,
         diag=0.70, contrast_sigma=0.5, ok=True, reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "inert": {}, "shared": {}, "moves": {},
                "diagonal": {}, "last_row": {}, "spans": {}}
    moves = list(moves if moves is not None else [0.1 + 0.01 * i for i in range(3 * reps)])
    got = [m for m in moves if m is not None]
    return {
        "ok": True, "reason": None,
        "runs": {"policy": {"artifact": e481.NEW.name}, "card": {"artifact": e481.BASE.name}},
        "same": {k: [1, 2] for k in (same or [])},
        "inert": {k: [1, 2] for k in (inert if inert is not None else ["loop_policy", "json_out"])},
        "shared": {"circuit": not shared_differ},
        "moves": {a: moves for a in ARMS},
        "diagonal": {a: {"policy": [diag] * reps, "card": [diag] * reps, "contrast": _paired(0.0, contrast_sigma)}
                     for a in ARMS},
        "last_row": {a: {"policy": [diag] * reps, "card": [diag] * reps, "contrast": _paired(0.0, contrast_sigma)}
                     for a in ARMS},
        "spans": {"arms": list(ARMS), "shared": list(e481.SHARED), "differ": sorted(same or []),
                  "inert": sorted(inert if inert is not None else ["loop_policy", "json_out"]),
                  "same_fields": 53, "flags": list(flags),
                  "shared_equal": ["circuit"] if not shared_differ else [],
                  "shared_differ": ["circuit"] if shared_differ else [],
                  "replicates": {"policy": [reps], "card": [20]},
                  "moves_recorded": len(got), "moves_total": len(moves),
                  "move_min": min(got) if got else None,
                  "move_mean": sum(got) / len(got) if got else None, "chance": e481.CHANCE},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e481.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one field moved, the freedom used, the game still learned and the numbers unmoved
    j = _judge()
    for cid in ("QA1", "QA2", "QA3", "QA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # QA1: another field differing, a shared field differing, a flag that did not move, and replicates that differ
    assert _judge(same=["iters"])["QA1"].startswith("FALSIFIER")
    assert _judge(shared_differ=True)["QA1"].startswith("FALSIFIER")
    assert _judge(flags=(True, True))["QA1"].startswith("FALSIFIER")
    assert _judge(reps=19)["QA1"].startswith("FALSIFIER")
    #: an inert admission alone does not fire it
    assert _judge(inert=["loop_policy", "json_out", "save_theta"])["QA1"].startswith("MET")

    # QA2: a policy that did not move, and one whose movement was not recorded at all
    assert _judge(moves=[0.1, 0.0, 0.2])["QA2"].startswith("FALSIFIER")
    assert _judge(moves=[0.1, None, 0.2])["QA2"].startswith("FALSIFIER")

    # QA3: a game that is not learned -- within the band fires it, and between the bands is a null
    assert _judge(diag=0.28)["QA3"].startswith("FALSIFIER")
    assert _judge(diag=0.33)["QA3"].startswith("NULL")
    assert _judge(diag=0.40)["QA3"].startswith("MET")

    # QA4: a contrast that resolves, on either quantity
    assert _judge(contrast_sigma=2.50)["QA4"].startswith("FALSIFIER")
    assert _judge(contrast_sigma=-2.50)["QA4"].startswith("FALSIFIER")
    assert _judge(contrast_sigma=1.90)["QA4"].startswith("MET")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e481.judge(_doc(ok=False)))


def test_the_runs_the_flag_and_the_inert_rule_are_registered():
    assert e481.NEW.name == "e481_earned_label_policy_20reps.json"
    assert e481.BASE.name == "e438_earned_label_three_arms_20reps.json"
    assert e481.RUNNER.name == "e8_rate_network.py"
    assert e481.FLAG == "loop_policy" and set(e481.BOOKKEEPING) == {"json_out", "save_theta"}
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e481.SIGMA, e481.CHANCE, e481.LEARNS, e481.FLAT) == (2.0, 0.25, 0.10, 0.05)
    assert e481.SHARED == ("circuit",), e481.SHARED
    #: the runner's own syntax tree carries the flag, and it is a `store_true` so its default is False
    assert e481.FLAG in parser_keys(e481.RUNNER), "the runner does not define --loop-policy"
    assert e481.DEFAULTS.get(e481.FLAG) is False, e481.DEFAULTS.get(e481.FLAG)
    #: a key the older roll lacks, at its default in the newer run, is inert; the flag is inert whatever it holds
    assert e481._inert("loop_policy", None, True) and e481._inert("json_out", "a", "b")
    assert e481._inert("iters", None, e481.DEFAULTS["iters"]) if "iters" in e481.DEFAULTS else True
    assert not e481._inert("iters", 500, 100)
    assert not e481._inert("repeats", 20, 40)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e481_the_benchmark_carries_a_policy.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e481.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["diagonal"]) == sorted(ARMS), sorted(d["diagonal"])
    assert sorted(d["last_row"]) == sorted(ARMS), sorted(d["last_row"])
    assert d["spans"]["flags"] == [None, True], d["spans"]["flags"]
    assert sorted(d["spans"]["shared_equal"]) == ["circuit"], d["spans"]
    for a in ARMS:
        assert len(d["diagonal"][a]["policy"]) == len(d["diagonal"][a]["card"]), a
        assert d["diagonal"][a]["contrast"]["n"] == d["last_row"][a]["contrast"]["n"], a
        for v in d["diagonal"][a]["policy"] + d["last_row"][a]["policy"]:
            assert 0.0 <= v <= 1.0, (a, v)
    assert d["spans"]["moves_total"] >= d["spans"]["moves_recorded"] >= 1, d["spans"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
