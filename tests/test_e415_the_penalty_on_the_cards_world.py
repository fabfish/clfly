"""`e415` reads the card's world's three-arm cell off `e356` and `e355`, so the tests pin both faces of the five
claims, the refusal when an artifact is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e415_the_penalty_on_the_cards_world as e415

#: the corpus's shape: the buffer beats the basis-matched penalty on both axes, and the penalty is not resolved
ACC = {"naive": 0.5493, "ewc-block": 0.5219, "replay": 0.6983}
MF = {"naive": 0.4099, "ewc-block": 0.3750, "replay": 0.1229}
#: the paired contrasts `(accuracy difference, its se, forgetting difference, its se)` over the twenty shared seeds
PAIRS = {
    "replay_minus_ewc-block": (+0.1764, 0.0153, -0.2521, 0.0216),
    "ewc-block_minus_naive": (-0.0274, 0.0141, -0.0349, 0.0232),
    "replay_minus_naive": (+0.1490, 0.0158, -0.2870, 0.0219),
}
FIELD = "env_draw.cue_sha1"


def _pair(spec):
    da, sea, df, sef = spec
    return {"accuracy": {"n": 20, "difference": da, "se": sea, "sigma": da / sea},
            "forgetting": {"n": 20, "difference": df, "se": sef, "sigma": df / sef}}


def _doc(contrasts=None, differ=None, reps=20, control=True, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "arms": {}, "contrasts": {}, "cell": {}, "control": {}, "world": {}}
    contrasts = dict(PAIRS) if contrasts is None else contrasts
    same = {f"f{i}": True for i in range(21)}
    if differ:
        same[differ] = False
    out = {"ok": True, "reason": None,
           "arms": {a: {"replicates": reps, "final_accuracy": ACC[a], "mean_forgetting": MF[a]}
                    for a in ("naive", "ewc-block", "replay")},
           "contrasts": {k: _pair(v) for k, v in contrasts.items()},
           "cell": {"artifact": "e356_earned_label_r32_20reps.json",
                    "reference": "e380_earned_label_cue0_actionsource_20reps.json", "same": same,
                    "coupling_recorded": True, "coupling_in_this_artifact": False},
           "control": {}, "world": {}}
    if isinstance(control, dict):
        out["control"] = control
    elif control:
        out["control"] = {"artifact": "e355_earned_label_r32_5reps.json", "replicates": 5,
                          "accuracy": {"n": 5, "difference": 0.0, "se": 0.0, "sigma": 0.0},
                          "forgetting": {"n": 5, "difference": -0.0125, "se": 0.02, "sigma": -0.6}}
    return out


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e415.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: three arms over the card's world, the buffer ahead on both axes, the penalty unresolved
    j = _judge()
    for cid in ("AP1", "AP2", "AP3", "AP4", "AP5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AP1: a shared field differing, and too few replicates
    assert _judge(differ=FIELD)["AP1"].startswith("FALSIFIER")
    assert _judge(reps=19)["AP1"].startswith("FALSIFIER")

    # AP2: a margin under the falsifier bar, and one between the bars
    assert _judge(contrasts={**PAIRS, "replay_minus_ewc-block": (+0.03, 0.015, -0.2521, 0.0216)})[
        "AP2"].startswith("FALSIFIER")
    assert _judge(contrasts={**PAIRS, "replay_minus_ewc-block": (+0.07, 0.015, -0.2521, 0.0216)})[
        "AP2"].startswith("NULL")

    # AP3: a cut under the falsifier bar, and one between the bars
    assert _judge(contrasts={**PAIRS, "replay_minus_ewc-block": (+0.1764, 0.015, -0.05, 0.021)})[
        "AP3"].startswith("FALSIFIER")
    assert _judge(contrasts={**PAIRS, "replay_minus_ewc-block": (+0.1764, 0.015, -0.12, 0.021)})[
        "AP3"].startswith("NULL")

    # AP4: a penalty that buys accuracy on this substrate
    assert _judge(contrasts={**PAIRS, "ewc-block_minus_naive": (+0.06, 0.014, -0.0349, 0.023)})[
        "AP4"].startswith("FALSIFIER")

    # AP5: a basis distinguished from its matched control, and the control's artifact absent
    big = {"artifact": "e355.json", "replicates": 5,
           "accuracy": {"n": 5, "difference": 0.12, "se": 0.02, "sigma": 6.0},
           "forgetting": {"n": 5, "difference": -0.0125, "se": 0.02, "sigma": -0.6}}
    assert _judge(control=big)["AP5"].startswith("FALSIFIER")
    assert _judge(control=False)["AP5"].startswith("REFUSED")

    #: an artifact the reading needs being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e415.judge(_doc(ok=False)))


def test_the_artifacts_and_the_thresholds_are_registered():
    #: the three-arm cell, the same cell with the matched control, and the card's world's own two-arm run
    assert e415.CELL20.name == "e356_earned_label_r32_20reps.json"
    assert e415.CELL5.name == "e355_earned_label_r32_5reps.json"
    assert e415.REFERENCE.name == "e380_earned_label_cue0_actionsource_20reps.json"
    assert e415.MIN_REPS == 20 and e415.N_TASKS == 3
    assert (e415.BIG, e415.BIG_FIRES, e415.CUT, e415.CUT_FIRES) == (0.10, 0.05, 0.15, 0.10)
    assert (e415.PENALTY_BAR, e415.PENALTY_FIRES) == (0.0, 0.05)
    assert (e415.CONTROL_BAR, e415.CONTROL_FIRES) == (0.05, 0.10)
    assert e415.CONTRASTS == (("replay", "ewc-block"), ("ewc-block", "naive"), ("replay", "naive"))
    assert "iters" in e415.CONFIG_FIELDS and "cue_sha1" in e415.DRAW_FIELDS


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e415_the_penalty_on_the_cards_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e415.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e415.judge(d)}
    #: the cell being carried and the buffer being ahead on both axes are structural facts
    assert verdicts["AP1"].startswith("MET") and verdicts["AP2"].startswith("MET"), verdicts
    assert sorted(d["arms"]) == ["ewc-block", "naive", "replay"], sorted(d["arms"])
    assert all(v["replicates"] >= e415.MIN_REPS for v in d["arms"].values()), d["arms"]
    #: the paired contrast the two central claims rest on is the artifact's own
    got = d["contrasts"]["replay_minus_ewc-block"]
    assert abs(got["accuracy"]["difference"] - (ACC["replay"] - ACC["ewc-block"])) < 1e-4, got
    assert got["accuracy"]["n"] == 20 and got["forgetting"]["n"] == 20, got
    assert d["cell"]["same"] and all(d["cell"]["same"].values()), d["cell"]["same"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
