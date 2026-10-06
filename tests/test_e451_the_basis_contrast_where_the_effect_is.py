"""`e451` reads the basis contrast where the effect is, so the tests pin both faces of the five claims and the refusal
when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e451_the_basis_contrast_where_the_effect_is as e451

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
STANDING = {"rand": -0.0250, "rand_sigma": -2.40, "bio": -0.0271, "bio_sigma": -2.29}
LAST = {"rand": -0.0900, "rand_sigma": -2.60, "bio": -0.0937, "bio_sigma": -2.81}
BASIS = 0.0040


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(standing=None, last=None, basis=BASIS, same_differ=None, bit_identical=True, width=4, reps=20,
         arms=e451.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "widths": {},
                "contrasts": {}, "spans": {}}
    st = dict(STANDING if standing is None else standing)
    lt = dict(LAST if last is None else last)
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_dims")}
    same.update({"circuit": True, "task_names": True})
    if same_differ:
        same[same_differ] = False
    bit = {f"new/biological:{a}": {"equal": bit_identical, "n": reps,
                                   "first_differing": None if bit_identical else 0, "fields": []}
           for a in e451.SHARED_ARMS}
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e451.RUNS},
            "same": same, "identical": bit, "widths": {"new": width, "biological": width},
            "contrasts": {"rand_over_naive": _paired(st["rand"], st["rand_sigma"]),
                          "rand_last": _paired(lt["rand"], lt["rand_sigma"]),
                          "bio_over_naive": _paired(st["bio"], st["bio_sigma"]),
                          "bio_last": _paired(lt["bio"], lt["bio_sigma"]),
                          "basis_accuracy": _paired(basis, 0.30),
                          "basis_forgetting": _paired(-0.0180, 0.90)},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e451.RUNS},
                      "same_fields": len(same), "widths": {"new": width, "biological": width},
                      "standing": st, "last": lt,
                      "known": {"bio_standing": e451.BIO_STANDING, "bio_sigma": e451.BIO_SIGMA}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e451.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration at four columns with both anchors carrying a resolved deficit
    j = _judge()
    for cid in ("CX1", "CX2", "CX3", "CX4", "CX5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # CX1: a field differing, a shared arm that is not bit-identical, a width that is not four, thin replicates
    # and a short arm list
    assert _judge(same_differ="config.iters")["CX1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["CX1"].startswith("FALSIFIER")
    assert _judge(width=8)["CX1"].startswith("FALSIFIER")
    assert _judge(reps=19)["CX1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["CX1"].startswith("FALSIFIER")

    # CX2: a matched-random arm with no deficit, and one whose deficit does not resolve
    assert _judge(standing={**STANDING, "rand": 0.0100, "rand_sigma": 0.80})["CX2"].startswith("FALSIFIER")
    assert _judge(standing={**STANDING, "rand": -0.0200, "rand_sigma": -1.20})["CX2"].startswith("FALSIFIER")

    # CX3: two deficits that disagree, and one between the bars
    assert _judge(standing={**STANDING, "rand": 0.1000, "rand_sigma": 4.00})["CX3"].startswith("FALSIFIER")
    assert _judge(standing={**STANDING, "rand": 0.0300, "rand_sigma": 1.20})["CX3"].startswith("NULL")

    # CX4: a basis contrast at the falsifier and one between the bars
    assert _judge(basis=0.1200)["CX4"].startswith("FALSIFIER")
    assert _judge(basis=0.0700)["CX4"].startswith("NULL")

    # CX5: a matched-random price that does not resolve
    assert _judge(last={**LAST, "rand": -0.0200, "rand_sigma": -1.20})["CX5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e451.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the matched-random roll at four columns is this unit's, and the biological arm's is what it is read against
    assert e451.RUNS["new"].name == "e451_earned_label_rand_worlddims4_20reps.json"
    assert e451.RUNS["biological"].name == "e449_earned_label_worlddims4_20reps.json"
    assert e451.ARMS == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e451.BASELINE, e451.BIO, e451.RAND, e451.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert e451.WIDTH_FIELD == "loop_world_dims" and e451.WIDTH == 4
    assert set(e451.IGNORED) == {"json_out", "save_theta", "methods"}, e451.IGNORED
    assert e451.N_TASKS == 3 and e451.N_ARMS == 3 and e451.MIN_REPS == 20
    assert (e451.ALIKE, e451.ALIKE_FIRES) == (0.05, 0.10)
    assert e451.SIGMA == 2.0
    assert (e451.BIO_STANDING, e451.BIO_SIGMA) == (-0.0271, 2.29), "the biological arm's deficit e449 read"


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e451_the_basis_contrast_where_the_effect_is.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e451.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates at four columns is structural
    assert sorted(d["runs"]) == ["biological", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block-rand", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e451.MIN_REPS, arm
        assert len(got["final"]) == e451.N_TASKS, arm
    assert sorted(d["identical"]) == ["new/biological:naive", "new/biological:replay"], sorted(d["identical"])
    for key, got in d["identical"].items():
        assert got["n"] >= e451.MIN_REPS, key
    assert d["widths"]["new"] == e451.WIDTH and d["widths"]["biological"] == e451.WIDTH, d["widths"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
