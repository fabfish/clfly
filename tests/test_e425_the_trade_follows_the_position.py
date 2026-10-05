"""`e425` reads three configurations rolled under both task orders, so the tests pin both faces of the five claims, the
refusal when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e425_the_trade_follows_the_position as e425

#: the corpus's shape: per configuration, the two rolls' task names and per-task gains
ROLLS = {
    "overlap": (["ov1_t0", "ov1_t1", "ov1_t2"], [0.0542, 0.0542, -0.0000],
                ["ov1_t2", "ov1_t1", "ov1_t0"], [0.1042, -0.0000, -0.0042]),
    "assembly": (["odour_identity", "heading", "odour_input"], [0.2333, 0.0937, 0.0021],
                 ["odour_input", "heading", "odour_identity"], [0.0875, 0.0667, -0.0104]),
    "assembly-five": (["odour_identity", "heading", "odour_input"], [0.2792, 0.0667, -0.0042],
                      ["odour_input", "heading", "odour_identity"], [0.0667, 0.0875, -0.0208]),
}


def _roll(tasks, gains, reps=5):
    return {"artifact": "x.json", "tasks": list(tasks), "gain": list(gains),
            "per_task": dict(zip(tasks, gains)), "replicates": reps}


def _config(spec, reps=5, differing=("task_order",), same=True):
    a_tasks, a_gains, b_tasks, b_gains = spec
    a, b = _roll(a_tasks, a_gains, reps), _roll(b_tasks, b_gains, reps)
    first, last = a["tasks"][0], a["tasks"][-1]
    contrasts = {
        "first_then_last": {"task": first, "at_first": a["per_task"][first], "at_last": b["per_task"].get(first)},
        "last_then_first": {"task": last, "at_last": a["per_task"][last], "at_first": b["per_task"].get(last)},
    }
    for c in contrasts.values():
        c["difference"] = c["at_first"] - c["at_last"]
    return {e425.AS_BUILT: a, e425.REVERSE: b, "differing_config": list(differing), "same_tasks": same,
            "contrasts": contrasts}


def _doc(spec=None, reps=5, differing=("task_order",), same=True, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "configs": {}, "spans": {}}
    spec = ROLLS if spec is None else spec
    cfg = {n: _config(s, reps, differing, same) for n, s in spec.items()}
    rolls = [(n, o, c[o]) for n, c in cfg.items() for o in (e425.AS_BUILT, e425.REVERSE)]
    import statistics as st
    return {"ok": True, "reason": None, "configs": cfg,
            "spans": {"configs": len(cfg), "rolls": len(rolls),
                      "replicates": sorted({r["replicates"] for _, _, r in rolls}),
                      "worst_first_over_last": min(r["gain"][0] - r["gain"][-1] for _, _, r in rolls),
                      "worst_last": max(r["gain"][-1] for _, _, r in rolls),
                      "smallest_position_contrast": min(c["contrasts"][k]["difference"]
                                                        for c in cfg.values() for k in c["contrasts"]),
                      "mean_drops": {n: st.fmean(c[e425.REVERSE]["gain"]) - st.fmean(c[e425.AS_BUILT]["gain"])
                                     for n, c in cfg.items()}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e425.judge(_doc(**kw))}


def _with(name, spec):
    out = {k: tuple(v) for k, v in ROLLS.items()}
    out[name] = tuple(spec)
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: three pairs, the first-taught task ahead in every roll, the same task moving with position
    j = _judge()
    for cid in ("BA1", "BA2", "BA3", "BA4", "BA5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BA1: another field differing, a task set that is not the same reversed, too few replicates, too few configs
    assert _judge(differing=("task_order", "batch"))["BA1"].startswith("FALSIFIER")
    assert _judge(same=False)["BA1"].startswith("FALSIFIER")
    assert _judge(reps=4)["BA1"].startswith("FALSIFIER")
    assert _judge(spec={k: v for k, v in list(ROLLS.items())[:2]})["BA1"].startswith("FALSIFIER")

    # BA2: a roll whose last position gains at least as much as the first
    assert _judge(spec=_with("assembly", (ROLLS["assembly"][0], [0.10, 0.09, 0.12],
                                          ROLLS["assembly"][2], ROLLS["assembly"][3])))["BA2"].startswith("FALSIFIER")

    # BA3: a last position above the bar, and one between the bars
    assert _judge(spec=_with("assembly", (ROLLS["assembly"][0], [0.2333, 0.0937, 0.06],
                                          ROLLS["assembly"][2], ROLLS["assembly"][3])))["BA3"].startswith("FALSIFIER")
    assert _judge(spec=_with("assembly", (ROLLS["assembly"][0], [0.2333, 0.0937, 0.03],
                                          ROLLS["assembly"][2], ROLLS["assembly"][3])))["BA3"].startswith("NULL")

    # BA4: a task that gains the same under either order, and one whose margin is between the bars
    flat = _with("assembly", (ROLLS["assembly"][0], [0.005, 0.0937, 0.001],
                              ROLLS["assembly"][2], ROLLS["assembly"][3]))
    assert _judge(spec=flat)["BA4"].startswith("FALSIFIER")
    mid = _with("assembly", (ROLLS["assembly"][0], [0.03, 0.0937, 0.001],
                             ROLLS["assembly"][2], ROLLS["assembly"][3]))
    assert _judge(spec=mid)["BA4"].startswith("NULL")

    # BA5: a configuration where reversing the order helps
    assert _judge(spec=_with("assembly", (ROLLS["assembly"][0], ROLLS["assembly"][1],
                                          ROLLS["assembly"][2],
                                          [0.20, 0.20, 0.20])))["BA5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e425.judge(_doc(ok=False)))


def test_the_pairs_and_the_thresholds_are_registered():
    #: three configurations rolled under both orders, the assembly one twice
    assert sorted(e425.PAIRS) == ["assembly", "assembly-five", "overlap"], sorted(e425.PAIRS)
    for n, (a, b) in e425.PAIRS.items():
        assert "as_built" in a.name and "reverse" in b.name, n
    assert e425.ARMS == ("naive", "replay") and e425.RUN_FIELDS == ("json_out", "save_theta")
    assert e425.MIN_CONFIGS == 3 and e425.MIN_REPS == 5
    assert e425.FIRST_OVER_LAST == 0.0
    assert (e425.LAST_BAR, e425.LAST_FIRES) == (0.01, 0.05)
    assert (e425.POSITION, e425.POSITION_FIRES) == (0.05, 0.02)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e425_the_trade_follows_the_position.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e425.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e425.judge(d)}
    #: the pairing being carried and the last position being worth nothing are structural facts
    assert verdicts["BA1"].startswith("MET") and verdicts["BA3"].startswith("MET"), verdicts
    assert len(d["configs"]) >= e425.MIN_CONFIGS, len(d["configs"])
    for n, c in d["configs"].items():
        assert c["differing_config"] == ["task_order"], (n, c["differing_config"])
        assert c["same_tasks"], n
        for o in (e425.AS_BUILT, e425.REVERSE):
            assert c[o]["replicates"] >= e425.MIN_REPS, (n, o)
            assert len(c[o]["gain"]) == len(c[o]["tasks"]), (n, o)
            assert abs(sum(c[o]["per_task"].values()) - sum(c[o]["gain"])) < 1e-9, (n, o)
        #: each contrast is the same task's two readings, and its difference is the two
        for k, con in c["contrasts"].items():
            assert con["task"] in c[e425.AS_BUILT]["tasks"], (n, k)
            assert abs(con["difference"] - (con["at_first"] - con["at_last"])) < 1e-12, (n, k)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
