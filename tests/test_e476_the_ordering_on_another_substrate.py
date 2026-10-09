"""`e476` reads the method ordering on the assembly suite, so the tests pin both faces of the four claims, the inert
rule that admits the two artifacts' generation gap, and the refusal when an artifact is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e476_the_ordering_on_another_substrate as e476

ARMS = e476.ARMS


def _paired(mean, sigma, n=40):
    return {"n": n, "mean": mean, "sd": 0.02, "se": 0.005, "sigma": sigma}


def _contrasts(buf_diag=0.0441, buf_sig=9.09, buf_forget=-0.0607, buf_fsig=-8.42, pen_diag=0.0043, pen_sig=0.80):
    return {
        "buffer_over_penalty": {"diagonal": _paired(buf_diag, buf_sig), "forgetting": _paired(buf_forget, buf_fsig)},
        "penalty_over_baseline": {"diagonal": _paired(pen_diag, pen_sig), "forgetting": _paired(-0.01, -1.0)},
        "buffer_over_baseline": {"diagonal": _paired(0.0484, 9.83), "forgetting": _paired(-0.07, -9.0)},
        "means": {a: {"diagonal": 0.90, "forgetting": -0.01} for a in ARMS},
    }


def _doc(same=None, inert=None, shared_differ=False, thin=False, suite=("0.0", None), buf_diag=0.0441, buf_sig=9.09,
         buf_forget=-0.0607, buf_fsig=-8.42, pen_sig=0.80, ok=True, reason="an artifact is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "inert": {}, "shared": {}, "suite": {},
                "contrasts": {}, "base_contrasts": {}, "spans": {}}
    reps = {"assembly": [39] if thin else [40], "overlap0": [40]}
    return {
        "ok": True, "reason": None,
        "runs": {"assembly": {"artifact": "e476_assembly_r32_methods_40reps.json", "n_arms": 3, "arms": {},
                              "config": {}},
                 "overlap0": {"artifact": "e140_r32_methods_plastic_40reps.json", "n_arms": 5, "arms": {},
                              "config": {}}},
        "same": {k: [1, 2] for k in (same or [])},
        "inert": {k: [1, 2] for k in (inert or [])},
        "shared": {"circuit": not shared_differ, "readout": True},
        "suite": {"field": "input_overlap", "old": suite[0], "new": suite[1]},
        "contrasts": _contrasts(buf_diag, buf_sig, buf_forget, buf_fsig, pen_diag=0.0043, pen_sig=pen_sig),
        "base_contrasts": _contrasts(),
        "spans": {"same_fields": 53, "differ": sorted(same or []), "inert": sorted(inert or []),
                  "shared_equal": ["circuit", "readout"],
                  "shared_differ": ["circuit"] if shared_differ else [],
                  "replicates": reps, "n_arms": {"assembly": 3, "overlap0": 5}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e476.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one configuration with the suite moved, the buffer ahead of the penalty, not paying in forgetting,
    #: and the penalty's own gain a null
    j = _judge()
    for cid in ("RA1", "RA2", "RA3", "RA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # RA1: a key both artifacts carry disagreeing, a shared field differing, a thin arm, and a suite that did not move
    assert _judge(same=["lam"])["RA1"].startswith("FALSIFIER")
    assert _judge(same=["iters"])["RA1"].startswith("FALSIFIER")
    assert _judge(shared_differ=True)["RA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["RA1"].startswith("FALSIFIER")
    assert _judge(suite=("0.0", "0.0"))["RA1"].startswith("FALSIFIER")
    #: an inert admission alone does not fire it
    assert _judge(inert=["closed_loop", "loop_symbols"])["RA1"].startswith("MET")

    # RA2: the ordering unresolvable, and the ordering reversed
    assert _judge(buf_sig=1.50)["RA2"].startswith("FALSIFIER")
    assert _judge(buf_sig=-9.00)["RA2"].startswith("FALSIFIER")
    assert _judge(buf_sig=2.10)["RA2"].startswith("MET")

    # RA3: a forgetting contrast that does not resolve, and one that says the buffer pays
    assert _judge(buf_fsig=-1.00)["RA3"].startswith("FALSIFIER")
    assert _judge(buf_fsig=8.00)["RA3"].startswith("FALSIFIER")
    assert _judge(buf_fsig=-2.10)["RA3"].startswith("MET")

    # RA4: the penalty's own gain resolving, in either direction
    assert _judge(pen_sig=3.00)["RA4"].startswith("FALSIFIER")
    assert _judge(pen_sig=-3.00)["RA4"].startswith("FALSIFIER")
    assert _judge(pen_sig=1.50)["RA4"].startswith("MET")

    #: an artifact that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e476.judge(_doc(ok=False)))


def test_the_runs_the_arms_and_the_inert_rule_are_registered():
    assert e476.NEW.name == "e476_assembly_r32_methods_40reps.json"
    assert e476.BASE.name == "e140_r32_methods_plastic_40reps.json"
    assert e476.RUNNER.name == "e8_rate_network.py"
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert e476.BASE_ARMS == ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay"), e476.BASE_ARMS
    assert (e476.BASELINE, e476.PENALTY, e476.BUFFER) == ("naive", "ewc-block", "replay")
    assert e476.SHARED == ("circuit", "readout"), e476.SHARED
    assert (e476.SIGMA, e476.MIN_REPS) == (2.0, 40), (e476.SIGMA, e476.MIN_REPS)
    assert e476.SUITE_FIELD == "input_overlap" and set(e476.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e476.INERT_FOR_ALL == ("methods",), e476.INERT_FOR_ALL
    #: the registry the rule reads must have found the runner's flags
    assert len(e476.DEFAULTS) >= 40, len(e476.DEFAULTS)


def test_the_inert_rule_admits_only_what_the_code_path_decides():
    #: the suite, the bookkeeping and the arm list are declared inert
    assert e476._inert("input_overlap", 0.0, None)
    assert e476._inert("json_out", "a", "b") and e476._inert("save_theta", None, "t")
    assert e476._inert("methods", "naive", "naive,replay")
    #: a key both artifacts carry and disagree on is not inert, and neither is a default neither records
    assert not e476._inert("lam", 0.003, 1.0)
    assert not e476._inert("iters", 500, 100)
    #: the two spellings of "not frozen" are one value
    assert e476._inert("frozen_bias", None, False) and e476._inert("frozen_bias", False, None)
    #: a key the older artifact lacks is inert exactly when the newer one holds that flag's default
    declared = set(e476.INERT_FOR_ALL) | set(e476.BOOKKEEPING) | {e476.SUITE_FIELD}
    for key, default in e476.DEFAULTS.items():
        if default is None or key in declared:
            continue
        assert e476._inert(key, None, default), (key, default)
        away = 0.5 if isinstance(default, float) else (default + 1 if isinstance(default, int)
                                                       and not isinstance(default, bool) else "different")
        assert not e476._inert(key, None, away), (key, default, away)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e476_the_ordering_on_another_substrate.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e476.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: forty paired replicates on the three arms the claims read is structural
    assert sorted(d["spans"]["replicates"]) == ["assembly", "overlap0"], d["spans"]["replicates"]
    for label, reps in d["spans"]["replicates"].items():
        assert reps == [40], (label, reps)
    assert d["suite"]["field"] == "input_overlap" and d["suite"]["old"] != d["suite"]["new"], d["suite"]
    assert sorted(d["spans"]["shared_equal"]) == ["circuit", "readout"], d["spans"]
    assert d["spans"]["same_fields"] >= 40, d["spans"]["same_fields"]
    for name in ("contrasts", "base_contrasts"):
        for key in ("buffer_over_penalty", "penalty_over_baseline", "buffer_over_baseline"):
            assert d[name][key]["diagonal"]["n"] == 40, (name, key)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
