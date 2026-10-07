"""`e462` reads the neuron read-out at sixteen columns, so the tests pin both faces of the five claims, the ladder the
fourth claim is about, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e462_the_neuron_readout_at_sixteen_columns as e462

#: the shape of the six rolls: the four outer rungs are the corpus' own readings and the middle rung is this unit's
BIO_PRICE = {"narrow": (-0.0615, 4.48), "mid": (-0.0300, 3.00), "wide": (-0.0115, 0.78)}
RAND_PRICE = {"narrow": (-0.0594, 4.18), "mid": (-0.0400, 2.50), "wide": (-0.0323, 2.77)}
BIO_STANDING = {"narrow": (0.0017, 0.12), "mid": (0.0017, 0.12), "wide": (0.0187, 1.03)}
RAND_STANDING = {"narrow": (-0.0271, 1.80), "mid": (0.0104, 0.59), "wide": (0.0104, 0.59)}
OVER_BIO = (0.1785, 10.48)
OVER_RAND = (0.2073, 12.00)
MID = 16


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(bio_price=BIO_PRICE, rand_price=RAND_PRICE, bio_standing=BIO_STANDING, rand_standing=RAND_STANDING,
         over_bio=OVER_BIO, over_rand=OVER_RAND, mid=MID, from_world=False, same_differ=None, bit_identical=True,
         reps=20, short=False, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "readouts": {},
                "contrasts": {}, "ladder": {}, "spans": {}}
    labels = list(e462.RUNS)
    run_arms = {label: {a: {"replicates": reps} for a in (e462.BASELINE,) +
                        (e462.ANCHOR_OF[label.split("/")[1]], e462.BUFFER)[:1 if short else 2]}
                for label in labels}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "readout_size")}
    same.update({"circuit": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    identical = {f"mid/bio-mid/rand:{a}": {"equal": bit_identical, "n": reps,
                                           "first_differing": None if bit_identical else 0, "fields": []}
                 for a in e462.SHARED_ARMS}
    contrasts = {}
    ladder = {}
    for side, prices, standings, over in (("bio", bio_price, bio_standing, over_bio),
                                          ("rand", rand_price, rand_standing, over_rand)):
        ladder[side] = {}
        for rung in e462.RUNGS:
            label = f"{rung}/{side}"
            contrasts[label] = {"anchor_over_naive": _paired(standings[rung][0], standings[rung][1]),
                                "anchor_last": _paired(prices[rung][0], prices[rung][1]),
                                "buffer_over_anchor": _paired(over[0], over[1]) if rung == "mid"
                                else _paired(0.2, 10.0),
                                "anchor_forgetting": _paired(0.0, 1.0)}
            ladder[side][rung] = {"width": e462.WIDTHS[rung],
                                  "standing": standings[rung][0], "standing_sigma": standings[rung][1],
                                  "price": prices[rung][0], "price_sigma": prices[rung][1],
                                  "buffer_over_anchor": contrasts[label]["buffer_over_anchor"]["mean"],
                                  "buffer_over_anchor_sigma":
                                      contrasts[label]["buffer_over_anchor"]["sigma"]}
    readout = {label: (mid if label.startswith("mid") else e462.WIDTHS[label.split("/")[0]]) for label in labels}
    fromw = {label: (from_world if label.startswith("mid") else False) for label in labels}
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms[label],
                             "readouts": [readout[label]] * 3,
                             "from_world": fromw[label],
                             "anchor": e462.ANCHOR_OF[label.split("/")[1]]} for label in labels},
            "same": same, "identical": identical,
            "readouts": {label: {"readouts": [readout[label]] * 3, "from_world": fromw[label]} for label in labels},
            "contrasts": contrasts, "ladder": ladder,
            "spans": {"replicates": [reps],
                      "arms": {label: len(run_arms[label]) for label in labels},
                      "same_fields": len(same),
                      "readout": {"mid_bio": mid, "mid_rand": mid, "from_world": fromw},
                      "mid": {"standing": {s: bio_standing["mid"][0] if s == "bio" else rand_standing["mid"][0]
                                           for s in ("bio", "rand")},
                              "standing_sigma": {s: bio_standing["mid"][1] if s == "bio" else rand_standing["mid"][1]
                                                 for s in ("bio", "rand")},
                              "price": {s: bio_price["mid"][0] if s == "bio" else rand_price["mid"][0]
                                        for s in ("bio", "rand")},
                              "price_sigma": {s: bio_price["mid"][1] if s == "bio" else rand_price["mid"][1]
                                              for s in ("bio", "rand")}}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e462.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: two rolls at sixteen neuron columns whose anchors both pay and whose magnitudes lie between the rungs
    j = _judge()
    for cid in ("DI1", "DI2", "DI3", "DI4", "DI5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DI1: a field differing, a read-out at another width, one read from the world, a shared arm that is not
    # bit-identical, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["DI1"].startswith("FALSIFIER")
    assert _judge(mid=e462.WIDTHS["wide"])["DI1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["DI1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["DI1"].startswith("FALSIFIER")
    assert _judge(reps=19)["DI1"].startswith("FALSIFIER")
    assert _judge(short=True)["DI1"].startswith("FALSIFIER")

    # DI2: the biological arm's price not resolving at the middle rung, and one arm of the wrong sign
    assert _judge(bio_price={**BIO_PRICE, "mid": (-0.0050, 0.80)})["DI2"].startswith("FALSIFIER")
    assert _judge(rand_price={**RAND_PRICE, "mid": (0.0500, 3.00)})["DI2"].startswith("FALSIFIER")

    # DI3: a pair that separates at the middle rung, and one between the bars
    assert _judge(rand_price={**RAND_PRICE, "mid": (-0.1500, 4.00)})["DI3"].startswith("FALSIFIER")
    assert _judge(rand_price={**RAND_PRICE, "mid": (-0.1000, 4.00)})["DI3"].startswith("NULL")

    # DI4: one arm's middle magnitude above its narrow one, and one below its wide one
    assert _judge(bio_price={**BIO_PRICE, "mid": (-0.0900, 5.00)})["DI4"].startswith("FALSIFIER")
    assert _judge(rand_price={**RAND_PRICE, "mid": (-0.0100, 2.50)})["DI4"].startswith("FALSIFIER")

    # DI5: a buffer that is behind an anchor, and one that does not resolve
    assert _judge(over_bio=(-0.0300, -2.50))["DI5"].startswith("FALSIFIER")
    assert _judge(over_rand=(0.0300, 1.20))["DI5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e462.judge(_doc(ok=False)))


def test_the_runs_and_the_rungs_are_registered():
    #: the two rolls at sixteen columns are this unit's; the four beside them are the rungs the ladder is read against
    assert e462.RUNS["mid/bio"].name == "e462_earned_label_neurons16_20reps.json"
    assert e462.RUNS["mid/rand"].name == "e462_earned_label_rand_neurons16_20reps.json"
    assert e462.RUNS["narrow/bio"].name == "e458_earned_label_neurons8_20reps.json"
    assert e462.RUNS["narrow/rand"].name == "e460_earned_label_rand_neurons8_20reps.json"
    assert e462.RUNS["wide/bio"].name == "e455_earned_label_neurons_20reps.json"
    assert e462.RUNS["wide/rand"].name == "e456_earned_label_rand_neurons_20reps.json"
    assert e462.RUNGS == ("narrow", "mid", "wide"), e462.RUNGS
    assert e462.WIDTHS == {"narrow": 8, "mid": 16, "wide": 32}, e462.WIDTHS
    assert e462.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e462.ANCHOR_OF
    assert (e462.BASELINE, e462.BIO, e462.RAND, e462.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e462.SIGMA, e462.ALIKE, e462.ALIKE_FIRES) == (2.0, 0.05, 0.10)
    assert set(e462.IGNORED) == {"json_out", "save_theta", "methods"}, e462.IGNORED
    assert e462.N_TASKS == 3 and e462.N_ARMS == 3 and e462.MIN_REPS == 20


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e462_the_neuron_readout_at_sixteen_columns.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e462.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: six rolls at twenty replicates is structural; the counts that grow with the corpus are read as a floor
    assert sorted(d["runs"]) == ["mid/bio", "mid/rand", "narrow/bio", "narrow/rand", "wide/bio", "wide/rand"], \
        sorted(d["runs"])
    for label, roll in d["runs"].items():
        assert len(roll["arms"]) >= e462.N_ARMS, label
        for arm, got in roll["arms"].items():
            assert got["replicates"] >= e462.MIN_REPS, (label, arm)
            assert len(got["final"]) == e462.N_TASKS, (label, arm)
    assert sorted(d["ladder"]) == ["bio", "rand"], sorted(d["ladder"])
    for side, rungs in d["ladder"].items():
        assert sorted(rungs) == sorted(e462.RUNGS), (side, sorted(rungs))
        assert [rungs[r]["width"] for r in e462.RUNGS] == [8, 16, 32], (side, rungs)
    assert d["spans"]["readout"]["mid_bio"] == e462.WIDTHS["mid"], d["spans"]["readout"]
    assert d["spans"]["readout"]["mid_rand"] == e462.WIDTHS["mid"], d["spans"]["readout"]
    assert d["spans"]["readout"]["from_world"]["mid/bio"] is False, d["spans"]["readout"]["from_world"]
    assert d["spans"]["readout"]["from_world"]["mid/rand"] is False, d["spans"]["readout"]["from_world"]
    assert d["spans"]["same_fields"] >= 40, d["spans"]["same_fields"]
    assert all(row["n"] >= e462.MIN_REPS for row in d["identical"].values()), d["identical"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
