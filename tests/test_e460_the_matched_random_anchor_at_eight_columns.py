"""`e460` reads the matched-random anchor at eight neuron columns, so the tests pin both faces of the five claims and
the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e460_the_matched_random_anchor_at_eight_columns as e460

#: the shape of the three rolls: fixed true values, so a mutation under test moves one of them
RAND_PRICE = (-0.0700, 3.50)
RAND_STANDING = (0.0080, 0.60)
BIO_STANDING = (0.0017, 0.12)
BIO_PRICE = (-0.0615, 4.48)
OVER_RAND = (0.1500, 9.00)
OVER_BIO = (0.1785, 10.48)
NARROW = 8
WIDE = 32


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(rand_price=RAND_PRICE, rand_standing=RAND_STANDING, over_rand=OVER_RAND, narrow=NARROW, from_world=False,
         same_differ=None, bit_identical=True, reps=20, arms=e460.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "readouts": {},
                "contrasts": {}, "spans": {}}
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "readout_size")}
    same.update({"circuit": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    bit = {f"new/biological:{a}": {"equal": bit_identical, "n": reps,
                                   "first_differing": None if bit_identical else 0, "fields": []}
           for a in e460.SHARED_ARMS}

    def _roll(size, world):
        return {"arms": run_arms, "readouts": [size] * 3, "from_world": world}
    return {"ok": True, "reason": None,
            "runs": {"new": _roll(narrow, from_world), "biological": _roll(NARROW, False),
                     "wide": _roll(WIDE, False)},
            "same": same, "identical": bit,
            "readouts": {"new": {"readouts": [narrow] * 3, "from_world": from_world},
                         "biological": {"readouts": [NARROW] * 3, "from_world": False},
                         "wide": {"readouts": [WIDE] * 3, "from_world": False}},
            "contrasts": {"rand_over_naive": _paired(rand_standing[0], rand_standing[1]),
                          "rand_last": _paired(rand_price[0], rand_price[1]),
                          "bio_over_naive": _paired(BIO_STANDING[0], BIO_STANDING[1]),
                          "bio_last": _paired(BIO_PRICE[0], BIO_PRICE[1]),
                          "buffer_over_rand": _paired(over_rand[0], over_rand[1]),
                          "buffer_over_bio": _paired(OVER_BIO[0], OVER_BIO[1]),
                          "wide_rand_last": _paired(e460.RAND_WIDE_PRICE, e460.RAND_WIDE_PRICE_SIGMA)},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e460.RUNS},
                      "same_fields": len(same),
                      "readout": {"new": narrow, "biological": NARROW, "wide": WIDE,
                                  "from_world": {"new": from_world, "biological": False, "wide": False}},
                      "standing": {"rand": rand_standing[0], "rand_sigma": rand_standing[1],
                                   "bio": BIO_STANDING[0], "bio_sigma": BIO_STANDING[1]},
                      "price": {"rand": rand_price[0], "rand_sigma": rand_price[1],
                                "bio": BIO_PRICE[0], "bio_sigma": BIO_PRICE[1]},
                      "buffer_over_rand": _paired(over_rand[0], over_rand[1]),
                      "known": {"bio_narrow_price": e460.BIO_NARROW_PRICE,
                                "bio_narrow_price_sigma": e460.BIO_NARROW_PRICE_SIGMA,
                                "rand_wide_price": e460.RAND_WIDE_PRICE,
                                "rand_wide_price_sigma": e460.RAND_WIDE_PRICE_SIGMA,
                                "rand_label_price": e460.RAND_LABEL_PRICE,
                                "rand_label_price_sigma": e460.RAND_LABEL_PRICE_SIGMA}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e460.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration at eight neuron columns with the second arm's price resolving
    j = _judge()
    for cid in ("DG1", "DG2", "DG3", "DG4", "DG5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DG1: a field differing, a read-out at another width, one read from the world, a shared arm that is not
    # bit-identical, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["DG1"].startswith("FALSIFIER")
    assert _judge(narrow=WIDE)["DG1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["DG1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["DG1"].startswith("FALSIFIER")
    assert _judge(reps=19)["DG1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["DG1"].startswith("FALSIFIER")

    # DG2: a price that does not resolve, and one of the wrong sign
    assert _judge(rand_price=(-0.0200, -1.50))["DG2"].startswith("FALSIFIER")
    assert _judge(rand_price=(0.0500, 3.00))["DG2"].startswith("FALSIFIER")

    # DG3: a standing that resolves at this head, in either direction
    assert _judge(rand_standing=(0.0300, 2.50))["DG3"].startswith("FALSIFIER")
    assert _judge(rand_standing=(-0.0300, -2.50))["DG3"].startswith("FALSIFIER")

    # DG4: two standings that disagree at this head, and one between the bars
    assert _judge(rand_standing=(0.1200, 1.50))["DG4"].startswith("FALSIFIER")
    assert _judge(rand_standing=(0.0700, 1.50))["DG4"].startswith("NULL")

    # DG5: a buffer that is not ahead of the matched-random anchor, and one that does not resolve
    assert _judge(over_rand=(-0.0300, -2.50))["DG5"].startswith("FALSIFIER")
    assert _judge(over_rand=(0.0300, 1.20))["DG5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e460.judge(_doc(ok=False)))


def test_the_runs_and_the_heads_are_registered():
    #: the matched-random roll at eight neuron columns is this unit's, and the two beside it are the fifth cell's pair
    assert e460.RUNS["new"].name == "e460_earned_label_rand_neurons8_20reps.json"
    assert e460.RUNS["biological"].name == "e458_earned_label_neurons8_20reps.json"
    assert e460.RUNS["wide"].name == "e456_earned_label_rand_neurons_20reps.json"
    assert e460.ARMS == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e460.BASELINE, e460.BIO, e460.RAND, e460.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert e460.NARROW == 8 and e460.SIGMA == 2.0
    assert (e460.ALIKE, e460.ALIKE_FIRES) == (0.05, 0.10)
    assert set(e460.IGNORED) == {"json_out", "save_theta", "methods"}, e460.IGNORED
    assert e460.N_TASKS == 3 and e460.N_ARMS == 3 and e460.MIN_REPS == 20
    assert (e460.BIO_NARROW_PRICE, e460.BIO_NARROW_PRICE_SIGMA) == (-0.0615, 4.48)
    assert (e460.RAND_WIDE_PRICE, e460.RAND_WIDE_PRICE_SIGMA) == (-0.0323, 2.77)
    assert (e460.RAND_LABEL_PRICE, e460.RAND_LABEL_PRICE_SIGMA) == (-0.1135, 4.49)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e460_the_matched_random_anchor_at_eight_columns.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e460.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates at eight neuron columns is structural
    assert sorted(d["runs"]) == ["biological", "new", "wide"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block-rand", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e460.MIN_REPS, arm
        assert len(got["final"]) == e460.N_TASKS, arm
    assert sorted(d["identical"]) == ["new/biological:naive", "new/biological:replay"], sorted(d["identical"])
    for key, got in d["identical"].items():
        assert got["n"] >= e460.MIN_REPS, key
    assert d["spans"]["readout"]["new"] == e460.NARROW, d["spans"]["readout"]
    assert d["spans"]["readout"]["from_world"] == {"new": False, "biological": False, "wide": False}, d["spans"]["readout"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
