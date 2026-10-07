"""`e456` reads the matched-random anchor on the neuron read-out, so the tests pin both faces of the five claims and the
refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e456_the_matched_random_arm_on_the_neuron_readout as e456

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
STANDING = {"rand": 0.0110, "rand_sigma": 0.60, "bio": 0.0187, "bio_sigma": 1.03}
LAST = {"rand": -0.0080, "rand_sigma": 0.55, "bio": -0.0115, "bio_sigma": 0.78}
BUFFER_OVER_RAND = (0.0980, 6.90)
BUFFER_OVER_BIO = (0.1090, 7.66)
BASIS = 0.0077
READOUT = 32


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(standing=None, last=None, over_rand=BUFFER_OVER_RAND, readout=READOUT, from_world=False,
         same_differ=None, bit_identical=True, reps=20, arms=e456.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "readouts": {},
                "contrasts": {}, "spans": {}}
    st = dict(STANDING if standing is None else standing)
    lt = dict(LAST if last is None else last)
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "readout_size")}
    same.update({"circuit": True, "task_names": True})
    if same_differ:
        same[same_differ] = False
    bit = {f"new/biological:{a}": {"equal": bit_identical, "n": reps,
                                   "first_differing": None if bit_identical else 0, "fields": []}
           for a in e456.SHARED_ARMS}
    return {"ok": True, "reason": None,
            "runs": {"new": {"arms": run_arms, "readouts": [readout] * 3, "readout_from_world": from_world},
                     "biological": {"arms": run_arms, "readouts": [readout] * 3, "readout_from_world": from_world}},
            "same": same, "identical": bit,
            "readouts": {"new": {"readouts": [readout] * 3, "from_world": from_world},
                         "biological": {"readouts": [readout] * 3, "from_world": from_world}},
            "contrasts": {"rand_over_naive": _paired(st["rand"], st["rand_sigma"]),
                          "rand_last": _paired(lt["rand"], lt["rand_sigma"]),
                          "bio_over_naive": _paired(st["bio"], st["bio_sigma"]),
                          "bio_last": _paired(lt["bio"], lt["bio_sigma"]),
                          "basis_accuracy": _paired(BASIS, 0.45),
                          "buffer_over_rand": _paired(over_rand[0], over_rand[1]),
                          "buffer_over_bio": _paired(BUFFER_OVER_BIO[0], BUFFER_OVER_BIO[1])},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e456.RUNS},
                      "same_fields": len(same),
                      "readout": {"new": readout, "biological": readout,
                                  "from_world": {"new": from_world, "biological": from_world}},
                      "standing": st, "last": lt,
                      "buffer_over_rand": _paired(over_rand[0], over_rand[1]),
                      "known": {"bio_standing": e456.BIO_STANDING,
                                "bio_standing_sigma": e456.BIO_STANDING_SIGMA,
                                "bio_price": e456.BIO_PRICE, "bio_price_sigma": e456.BIO_PRICE_SIGMA}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e456.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration on the neuron read-out, both anchors unresolved and agreeing
    j = _judge()
    for cid in ("DC1", "DC2", "DC3", "DC4", "DC5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DC1: a field differing, a shared arm that is not bit-identical, a read-out that is the world's or another
    # width, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["DC1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["DC1"].startswith("FALSIFIER")
    assert _judge(readout=8, from_world=True)["DC1"].startswith("FALSIFIER")
    assert _judge(readout=16)["DC1"].startswith("FALSIFIER")
    assert _judge(reps=19)["DC1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["DC1"].startswith("FALSIFIER")

    # DC2: a standing that resolves, in either direction
    assert _judge(standing={**STANDING, "rand": 0.0300, "rand_sigma": 2.40})["DC2"].startswith("FALSIFIER")
    assert _judge(standing={**STANDING, "rand": -0.0300, "rand_sigma": -2.40})["DC2"].startswith("FALSIFIER")

    # DC3: a price that resolves
    assert _judge(last={**LAST, "rand": -0.0900, "rand_sigma": -3.00})["DC3"].startswith("FALSIFIER")

    # DC4: two anchors that disagree under this read-out, and one between the bars
    assert _judge(standing={**STANDING, "rand": 0.1200, "rand_sigma": 1.50})["DC4"].startswith("FALSIFIER")
    assert _judge(standing={**STANDING, "rand": 0.0700, "rand_sigma": 1.50})["DC4"].startswith("NULL")

    # DC5: a buffer that is not ahead of the matched-random anchor, and one that does not resolve
    assert _judge(over_rand=(-0.0300, -2.50))["DC5"].startswith("FALSIFIER")
    assert _judge(over_rand=(0.0300, 1.20))["DC5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e456.judge(_doc(ok=False)))


def test_the_runs_and_the_readout_are_registered():
    #: the matched-random roll is this unit's, and the biological arm's at the same read-out is what it is read against
    assert e456.RUNS["new"].name == "e456_earned_label_rand_neurons_20reps.json"
    assert e456.RUNS["biological"].name == "e455_earned_label_neurons_20reps.json"
    assert e456.ARMS == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e456.BASELINE, e456.BIO, e456.RAND, e456.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert e456.READOUT_FIELD == "readout_from_world" and e456.NEURON_READOUT == 32
    assert set(e456.IGNORED) == {"json_out", "save_theta", "methods"}, e456.IGNORED
    assert e456.N_TASKS == 3 and e456.N_ARMS == 3 and e456.MIN_REPS == 20
    assert (e456.ALIKE, e456.ALIKE_FIRES) == (0.05, 0.10)
    assert e456.SIGMA == 2.0
    assert (e456.BIO_STANDING, e456.BIO_STANDING_SIGMA) == (0.0187, 1.03)
    assert (e456.BIO_PRICE, e456.BIO_PRICE_SIGMA) == (-0.0115, 0.78)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e456_the_matched_random_arm_on_the_neuron_readout.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e456.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on the neuron read-out is structural
    assert sorted(d["runs"]) == ["biological", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block-rand", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e456.MIN_REPS, arm
        assert len(got["final"]) == e456.N_TASKS, arm
    assert sorted(d["identical"]) == ["new/biological:naive", "new/biological:replay"], sorted(d["identical"])
    for key, got in d["identical"].items():
        assert got["n"] >= e456.MIN_REPS, key
    assert d["spans"]["readout"]["new"] == e456.NEURON_READOUT, d["spans"]["readout"]
    assert d["spans"]["readout"]["from_world"] == {"new": False, "biological": False}, d["spans"]["readout"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
