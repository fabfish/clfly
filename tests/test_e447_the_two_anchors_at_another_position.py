"""`e447` reads the two anchors at another position, so the tests pin both faces of the five claims and the refusal when
a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e447_the_two_anchors_at_another_position as e447

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
RAND_LAST = -0.0960
RAND_SIGMA = -3.10
BIO_LAST = -0.0917
BIO_SIGMA = -3.38
BASIS = 0.0040
STANDING = {"rand": 0.0100, "rand_sigma": 0.70, "bio": 0.0083, "bio_sigma": 0.63}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(rand_last=RAND_LAST, bio_last=BIO_LAST, basis=BASIS, standing=None, same_differ=None,
         bit_identical=True, reversal=True, reps=20, arms=e447.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "reversed": {},
                "contrasts": {}, "spans": {}}
    st = dict(STANDING if standing is None else standing)
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_coupled")}
    same.update({f"env_draw.{k}": True for k in e447.DRAW_FIELDS})
    same.update({"circuit": True, "readout": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    bit = {f"new/biological:{a}": {"equal": bit_identical, "n": reps,
                                   "first_differing": None if bit_identical else 0, "fields": []}
           for a in e447.SHARED_ARMS}
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e447.RUNS},
            "same": same, "identical": bit,
            "reversed": {"new": ["t2", "t1", "t0"] if reversal else ["t0", "t1", "t2"],
                         "card": ["t0", "t1", "t2"], "is_the_reversal": reversal,
                         "orders": {"new": "reverse", "biological": "reverse", "card": "as-built"}},
            "contrasts": {"rand_over_naive": _paired(st["rand"], st["rand_sigma"]),
                          "rand_last": _paired(rand_last, RAND_SIGMA),
                          "bio_over_naive": _paired(st["bio"], st["bio_sigma"]),
                          "bio_last": _paired(bio_last, BIO_SIGMA),
                          "basis_accuracy": _paired(basis, 0.25),
                          "basis_forgetting": _paired(-0.0200, 1.20)},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e447.RUNS},
                      "same_fields": len(same), "orders": {"new": "reverse", "biological": "reverse",
                                                           "card": "as-built"},
                      "last": {"rand": rand_last, "bio": bio_last, "rand_sigma": RAND_SIGMA, "bio_sigma": BIO_SIGMA,
                               "last_task": "loop_odour_identity"},
                      "standing": st,
                      "as_built_last_gap": e447.AS_BUILT_LAST_GAP, "as_built_basis": e447.AS_BUILT_BASIS}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e447.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration reversed, and the two anchors reading alike where the price is known
    j = _judge()
    for cid in ("BY1", "BY2", "BY3", "BY4", "BY5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BY1: a field differing, a shared arm that is not bit-identical, a suite that is not the reversal, thin
    # replicates and a short arm list
    assert _judge(same_differ="config.iters")["BY1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["BY1"].startswith("FALSIFIER")
    assert _judge(reversal=False)["BY1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BY1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BY1"].startswith("FALSIFIER")

    # BY2: a matched-random arm that is ahead on the newest task, and one between the bars
    assert _judge(rand_last=0.1000)["BY2"].startswith("FALSIFIER")
    assert _judge(rand_last=0.0200)["BY2"].startswith("NULL")

    # BY3: two anchors that pay the newest task very differently, and one between the bars
    assert _judge(rand_last=0.0500)["BY3"].startswith("FALSIFIER")
    assert _judge(rand_last=-0.0400)["BY3"].startswith("NULL")

    # BY4: a basis contrast at the falsifier and one between the bars
    assert _judge(basis=0.1200)["BY4"].startswith("FALSIFIER")
    assert _judge(basis=0.0700)["BY4"].startswith("NULL")

    # BY5: an anchor whose standing resolves here
    assert _judge(standing={**STANDING, "bio_sigma": 2.50})["BY5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e447.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the matched-random roll is this unit's, and the two beside it are the biological arm's and the card's
    assert e447.RUNS["new"].name == "e447_earned_label_rand_reverse_20reps.json"
    assert e447.RUNS["biological"].name == "e446_earned_label_anchor_reverse_20reps.json"
    assert e447.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e447.ARMS == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e447.BASELINE, e447.BIO, e447.RAND, e447.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert e447.ORDER == "task_order" and e447.ORDER in e447.IGNORED
    assert e447.N_TASKS == 3 and e447.N_ARMS == 3 and e447.MIN_REPS == 20
    assert (e447.LAST_BAR, e447.LAST_FIRES) == (0.0, 0.05)
    assert (e447.ALIKE, e447.ALIKE_FIRES) == (0.05, 0.10)
    assert e447.SIGMA == 2.0
    assert (e447.AS_BUILT_LAST_GAP, e447.AS_BUILT_BASIS) == (0.0042, 0.0063), "the as-built pair e439 read"


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e447_the_two_anchors_at_another_position.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e447.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on three rolls is structural
    assert sorted(d["runs"]) == ["biological", "card", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block-rand", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e447.MIN_REPS, arm
        assert len(got["final"]) == e447.N_TASKS, arm
    assert sorted(d["identical"]) == ["new/biological:naive", "new/biological:replay"], sorted(d["identical"])
    for key, got in d["identical"].items():
        assert got["n"] >= e447.MIN_REPS, key
    assert d["spans"]["orders"]["new"] != d["spans"]["orders"]["card"], d["spans"]["orders"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
