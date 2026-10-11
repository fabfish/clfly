"""`e489` gives the pass an episode of trials and the episode a boundary channel, so the tests pin both faces of the
five claims, the endpoint's construction, the fields the episode adds to a draw, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e489_the_benchmark_has_an_episode as e489

ARMS = e489.ARMS
#: the reading's shape: an exact endpoint, the episode carried by the world, a channel of its own, a learned task and
#: a boundary that does not buy the accuracy
EPISODE = e489.EPISODE
MARKS = [1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0]
BOUND_ACC = {"naive": 0.7200, "ewc-block": 0.6900, "replay": 0.6800}
PLAIN_ACC = {"naive": 0.7300, "ewc-block": 0.7000, "replay": 0.6900}
ACC_LAST = {a: 0.4500 for a in ARMS}
MOVED = {"bound": {"loop_episode": EPISODE, "loop_boundary": True},
         "plain": {"loop_episode": EPISODE, "loop_boundary": False}}
ADDED = {"bound": sorted(e489.ADDED), "plain": ["episode_len"]}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.1, "se": 0.05, "sigma": sigma}


def _carry(episode=(0.7601, 12.62), single=0.0):
    return {"episode": {"pairing": _paired(episode[0], episode[1], n=64), "largest": 1.7013, "smallest": 0.003,
                        "state_scale": 0.7727},
            "single": {"pairing": _paired(0.0, 0.0, n=64), "largest": single, "smallest": 0.0, "state_scale": 0.7856}}


def _boundary(added=None, differ=None, moved=None, identical=True, endpoint_added=None, steps_agree=True,
               overlap=0, in_input=True, off_has_channel=False, accuracy=None, plain_acc=None, replicates=(20,)):
    return {
        "ok": True, "reason": None, "runs": {"bound": {"artifact": "b"}, "plain": {"artifact": "p"}},
        "endpoint": {"fields": 22, "added": list(endpoint_added or []), "missing": [], "identical": identical},
        "carry": _carry(),
        "boundary": {"gain": 1.0, "n_boundary": 8, "marks": list(MARKS), "wanted": list(MARKS),
                     "steps_agree": steps_agree, "overlap": overlap, "in_input": in_input,
                     "off_has_channel": off_has_channel, "off_input_gap": 8},
        "accuracy": {a: _paired(*(accuracy or {}).get(a, (-0.0100, -0.50))) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["bound", "plain"], "episode": EPISODE,
                  "replicates": list(replicates),
                  "config": {label: {"same": 47, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": dict((moved or MOVED)[label])} for label in ("bound", "plain")},
                  "draw": {label: {"agree": {"cue_sha1": True}, "differ": [], "added": list((added or ADDED)[label]),
                                   "missing": [], "card_fields": 22} for label in ("bound", "plain")},
                  "accuracy_diagonal": {"bound": {a: BOUND_ACC[a] for a in ARMS},
                                        "plain": {a: (plain_acc or PLAIN_ACC)[a] for a in ARMS}},
                  "accuracy_last": {"bound": dict(ACC_LAST), "plain": dict(ACC_LAST)},
                  "chance": e489.CHANCE, "bar": e489.BAR, "episode_fields": list(e489.ADDED),
                  "sigmas": e489.SIGMA},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e489.judge(_boundary(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("FA1", "FA2", "FA3", "FA4", "FA5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # FA1: an endpoint that adds a field, a non-identical array, another config field differing, the wrong move, a
    # wrong draw addition, and a thin run
    assert _judge(endpoint_added=["episode_len"])["FA1"].startswith("FALSIFIER")
    assert _judge(identical=False)["FA1"].startswith("FALSIFIER")
    assert _judge(differ=["iters"])["FA1"].startswith("FALSIFIER")
    assert _judge(moved={"bound": {"loop_episode": EPISODE, "loop_boundary": False},
                         "plain": {"loop_episode": EPISODE, "loop_boundary": False}})["FA1"].startswith("FALSIFIER")
    assert _judge(added={"bound": sorted(e489.ADDED), "plain": []})["FA1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["FA1"].startswith("FALSIFIER")

    # FA2: an episode that carries nothing, one that does not resolve, and an endpoint with a difference
    doc = _boundary()
    doc["carry"]["episode"]["pairing"] = _paired(0.0, 0.0, n=64)
    assert {r["id"]: r["verdict"] for r in e489.judge(doc)}["FA2"].startswith("FALSIFIER")
    doc = _boundary()
    doc["carry"]["episode"]["pairing"] = _paired(0.2, 0.9, n=64)
    assert {r["id"]: r["verdict"] for r in e489.judge(doc)}["FA2"].startswith("FALSIFIER")
    doc = _boundary()
    doc["carry"]["single"]["largest"] = 0.4
    assert {r["id"]: r["verdict"] for r in e489.judge(doc)}["FA2"].startswith("FALSIFIER")

    # FA3: a marker at the wrong step, a population overlap, a channel outside the input, and a channel at the endpoint
    assert _judge(steps_agree=False)["FA3"].startswith("FALSIFIER")
    assert _judge(overlap=3)["FA3"].startswith("FALSIFIER")
    assert _judge(in_input=False)["FA3"].startswith("FALSIFIER")
    assert _judge(off_has_channel=True)["FA3"].startswith("FALSIFIER")

    # FA4: the episodic task at chance
    assert _judge(plain_acc={"naive": 0.2600, "ewc-block": 0.7000, "replay": 0.6900})["FA4"].startswith("FALSIFIER")

    # FA5: a boundary that buys the accuracy
    assert _judge(accuracy={"naive": (+0.0400, +2.60)})["FA5"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e489.judge({"ok": False, "reason": "a run is absent"}))


def test_the_runs_the_flags_and_the_bars_are_registered():
    assert e489.BOUND.name == "e489_earned_label_episode3_boundary_20reps.json"
    assert e489.PLAIN.name == "e489_earned_label_episode3_20reps.json"
    assert e489.CARD.name == "e438_earned_label_three_arms_20reps.json"
    assert e489.RUNNER.name == "e8_rate_network.py"
    assert set(e489.MOVED) == {"loop_episode", "loop_boundary"}, e489.MOVED
    assert set(e489.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e489.ADDED == ("episode_len", "boundary_sha1", "n_boundary", "boundary_gain"), e489.ADDED
    assert (e489.EPISODE, e489.TAU) == (3, 12), (e489.EPISODE, e489.TAU)
    assert e489.TAU % e489.EPISODE == 0
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e489.MIN_REPS, e489.SIGMA, e489.CHANCE, e489.BAR) == (20, 2.0, 0.25, 0.10)
    assert e489._inert("loop_episode", None, 3) and e489._inert("loop_boundary", None, True)
    assert not e489._inert("iters", 500, 100)
    assert e489.DEFAULTS.get("loop_episode") == 1, e489.DEFAULTS.get("loop_episode")
    assert e489.DEFAULTS.get("loop_boundary") is False, e489.DEFAULTS.get("loop_boundary")


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e489_the_benchmark_has_an_episode.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e489.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["runs"]) == ["bound", "plain"], sorted(d["runs"])
    assert sorted(d["accuracy"]) == sorted(ARMS), sorted(d["accuracy"])
    assert sorted(d["spans"]["accuracy_diagonal"]["bound"]) == sorted(ARMS), d["spans"]["accuracy_diagonal"]
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    assert d["endpoint"]["fields"] > 0, d["endpoint"]
    assert len(d["boundary"]["marks"]) == e489.TAU, d["boundary"]["marks"]
    assert d["carry"]["episode"]["pairing"]["n"] > 0, d["carry"]
    for a in ARMS:
        assert d["accuracy"][a]["n"] == 20, (a, d["accuracy"][a])
        #: the accuracy is a rate: what is asserted here is the shape, and whether the episode was learned is the
        #: judge's business
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["plain"][a] <= 1.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["bound"][a] <= 1.0, a
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
