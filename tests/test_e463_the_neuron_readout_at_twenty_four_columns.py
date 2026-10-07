"""`e463` reads the neuron read-out at twenty-four columns, so the tests pin both faces of the five claims, the
four-point ladder the fourth and fifth claims are about, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e463_the_neuron_readout_at_twenty_four_columns as e463

#: the shape of the eight rolls: the six outer rungs are the corpus' own readings and twenty-four is this unit's
BIO_PRICE = {8: (-0.0615, 4.48), 16: (-0.0406, 3.71), 24: (-0.0250, 3.00), 32: (-0.0115, 0.78)}
RAND_PRICE = {8: (-0.0594, 4.18), 16: (-0.0396, 2.46), 24: (-0.0350, 2.60), 32: (-0.0323, 2.77)}
BIO_STANDING = {8: (0.0017, 0.12), 16: (0.0215, 1.48), 24: (0.0140, 1.20), 32: (0.0187, 1.03)}
RAND_STANDING = {8: (-0.0271, 1.80), 16: (0.0042, 0.27), 24: (0.0030, 0.20), 32: (0.0104, 0.59)}
OVER_BIO = (0.1628, 9.95)
OVER_RAND = (0.1802, 10.37)
NEW = 24


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(bio_price=BIO_PRICE, rand_price=RAND_PRICE, bio_standing=BIO_STANDING, rand_standing=RAND_STANDING,
         over_bio=OVER_BIO, over_rand=OVER_RAND, width=NEW, from_world=False, same_differ=None, bit_identical=True,
         reps=20, short=False, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "readouts": {},
                "contrasts": {}, "ladder": {}, "gaps": {}, "spans": {}}
    labels = list(e463.RUNS)
    run_arms = {label: {a: {"replicates": reps} for a in (e463.BASELINE,) +
                        (e463.ANCHOR_OF[label.split("/")[1]], e463.BUFFER)[:1 if short else 2]}
                for label in labels}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "readout_size")}
    same.update({"circuit": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    identical = {f"new:bio-rand:{a}": {"equal": bit_identical, "n": reps,
                                       "first_differing": None if bit_identical else 0, "fields": []}
                 for a in e463.SHARED_ARMS}
    contrasts, ladder = {}, {}
    for side, prices, standings, over in (("bio", bio_price, bio_standing, over_bio),
                                          ("rand", rand_price, rand_standing, over_rand)):
        ladder[side] = {}
        for w in e463.RUNGS:
            label = f"{w}/{side}"
            i = int(w)
            contrasts[label] = {"anchor_over_naive": _paired(standings[i][0], standings[i][1]),
                                "anchor_last": _paired(prices[i][0], prices[i][1]),
                                "buffer_over_anchor": _paired(over[0], over[1]) if i == NEW else _paired(0.2, 10.0)}
            ladder[side][w] = {"width": i,
                               "standing": standings[i][0], "standing_sigma": standings[i][1],
                               "price": prices[i][0], "price_sigma": prices[i][1],
                               "buffer_over_anchor": over[0] if i == NEW else 0.2,
                               "buffer_over_anchor_sigma": over[1] if i == NEW else 10.0}
    readout = {label: (width if label.startswith(f"{NEW}/") else int(label.split("/")[0])) for label in labels}
    fromw = {label: (from_world if label.startswith(f"{NEW}/") else False) for label in labels}
    gaps = {w: {"price": abs(bio_price[int(w)][0] - rand_price[int(w)][0]),
                "standing": abs(bio_standing[int(w)][0] - rand_standing[int(w)][0])} for w in e463.RUNGS}
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms[label],
                             "readouts": [readout[label]] * 3,
                             "from_world": fromw[label],
                             "anchor": e463.ANCHOR_OF[label.split("/")[1]]} for label in labels},
            "same": same, "identical": identical,
            "readouts": {label: {"readouts": [readout[label]] * 3, "from_world": fromw[label]} for label in labels},
            "contrasts": contrasts, "ladder": ladder, "gaps": gaps,
            "spans": {"replicates": [reps],
                      "arms": {label: len(run_arms[label]) for label in labels},
                      "same_fields": len(same),
                      "readout": {"new_bio": width, "new_rand": width, "from_world": fromw},
                      "new": {"standing": {s: (bio_standing if s == "bio" else rand_standing)[NEW][0]
                                           for s in ("bio", "rand")},
                              "standing_sigma": {s: (bio_standing if s == "bio" else rand_standing)[NEW][1]
                                                 for s in ("bio", "rand")},
                              "price": {s: (bio_price if s == "bio" else rand_price)[NEW][0]
                                        for s in ("bio", "rand")},
                              "price_sigma": {s: (bio_price if s == "bio" else rand_price)[NEW][1]
                                              for s in ("bio", "rand")}}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e463.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: two rolls at the new rung whose anchors both pay, whose magnitudes sit between their neighbours'
    #: and whose standing gap sits between the gaps at the rungs either side
    j = _judge()
    for cid in ("DJ1", "DJ2", "DJ3", "DJ4", "DJ5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DJ1: a field differing, a read-out at another width, one read from the world, a shared arm that is not
    # bit-identical, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["DJ1"].startswith("FALSIFIER")
    assert _judge(width=32)["DJ1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["DJ1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["DJ1"].startswith("FALSIFIER")
    assert _judge(reps=19)["DJ1"].startswith("FALSIFIER")
    assert _judge(short=True)["DJ1"].startswith("FALSIFIER")

    # DJ2: the biological arm's price not resolving at the new rung, and one arm of the wrong sign
    assert _judge(bio_price={**BIO_PRICE, NEW: (-0.0050, 0.80)})["DJ2"].startswith("FALSIFIER")
    assert _judge(rand_price={**RAND_PRICE, NEW: (0.0500, 3.00)})["DJ2"].startswith("FALSIFIER")

    # DJ3: a pair that has already separated here, and one between the bars
    assert _judge(rand_price={**RAND_PRICE, NEW: (-0.1600, 4.00)})["DJ3"].startswith("FALSIFIER")
    assert _judge(rand_price={**RAND_PRICE, NEW: (-0.1000, 4.00)})["DJ3"].startswith("NULL")

    # DJ4: one arm's new magnitude above its sixteen-column one, and one below its thirty-two column one
    assert _judge(bio_price={**BIO_PRICE, NEW: (-0.0900, 5.00)})["DJ4"].startswith("FALSIFIER")
    assert _judge(rand_price={**RAND_PRICE, NEW: (-0.0100, 2.50)})["DJ4"].startswith("FALSIFIER")

    # DJ5: a standing gap above the sixteen-column one, and one below the thirty-two column one
    assert _judge(bio_standing={**BIO_STANDING, NEW: (0.0300, 1.00)})["DJ5"].startswith("FALSIFIER")
    assert _judge(bio_standing={**BIO_STANDING, NEW: (0.0010, 1.00)})["DJ5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e463.judge(_doc(ok=False)))


def test_the_runs_and_the_rungs_are_registered():
    #: the two rolls at twenty-four columns are this unit's; the six beside them are the rungs the ladder is read on
    assert e463.RUNS[f"{NEW}/bio"].name == "e463_earned_label_neurons24_20reps.json"
    assert e463.RUNS[f"{NEW}/rand"].name == "e463_earned_label_rand_neurons24_20reps.json"
    assert e463.RUNS["8/bio"].name == "e458_earned_label_neurons8_20reps.json"
    assert e463.RUNS["8/rand"].name == "e460_earned_label_rand_neurons8_20reps.json"
    assert e463.RUNS["16/bio"].name == "e462_earned_label_neurons16_20reps.json"
    assert e463.RUNS["16/rand"].name == "e462_earned_label_rand_neurons16_20reps.json"
    assert e463.RUNS["32/bio"].name == "e455_earned_label_neurons_20reps.json"
    assert e463.RUNS["32/rand"].name == "e456_earned_label_rand_neurons_20reps.json"
    assert e463.RUNGS == ("8", "16", "24", "32"), e463.RUNGS
    assert (e463.NEW_WIDTH, e463.BELOW, e463.ABOVE) == (24, 16, 32)
    #: the ladder is keyed as the artifact carries it, so a reading off disk and one in memory are read alike
    assert (e463.NEWK, e463.BELOWK, e463.ABOVEK) == ("24", "16", "32")
    assert e463.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e463.ANCHOR_OF
    assert (e463.BASELINE, e463.BIO, e463.RAND, e463.BUFFER) == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert (e463.SIGMA, e463.ALIKE, e463.ALIKE_FIRES) == (2.0, 0.05, 0.10)
    assert set(e463.IGNORED) == {"json_out", "save_theta", "methods"}, e463.IGNORED
    assert e463.N_TASKS == 3 and e463.N_ARMS == 3 and e463.MIN_REPS == 20


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e463_the_neuron_readout_at_twenty_four_columns.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e463.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: eight rolls at twenty replicates is structural; the counts that grow with the corpus are read as a floor
    assert sorted(d["runs"]) == ["16/bio", "16/rand", "24/bio", "24/rand", "32/bio", "32/rand",
                                 "8/bio", "8/rand"], sorted(d["runs"])
    for label, roll in d["runs"].items():
        assert len(roll["arms"]) >= e463.N_ARMS, label
        for arm, got in roll["arms"].items():
            assert got["replicates"] >= e463.MIN_REPS, (label, arm)
            assert len(got["final"]) == e463.N_TASKS, (label, arm)
    assert sorted(d["ladder"]) == ["bio", "rand"], sorted(d["ladder"])
    for side, rungs in d["ladder"].items():
        assert sorted(rungs) == sorted(e463.RUNGS), (side, sorted(rungs))
        assert [rungs[w]["width"] for w in e463.RUNGS] == [8, 16, 24, 32], (side, rungs)
    assert sorted(d["gaps"]) == sorted(e463.RUNGS), sorted(d["gaps"])
    assert d["spans"]["readout"]["new_bio"] == e463.NEW_WIDTH, d["spans"]["readout"]
    assert d["spans"]["readout"]["new_rand"] == e463.NEW_WIDTH, d["spans"]["readout"]
    assert d["spans"]["readout"]["from_world"][f"{NEW}/bio"] is False, d["spans"]["readout"]["from_world"]
    assert d["spans"]["readout"]["from_world"][f"{NEW}/rand"] is False, d["spans"]["readout"]["from_world"]
    assert d["spans"]["same_fields"] >= 40, d["spans"]["same_fields"]
    assert all(row["n"] >= e463.MIN_REPS for row in d["identical"].values()), d["identical"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
