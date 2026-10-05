"""`e427` reads the plastic/frozen-bias pair and the two further frozen-bias suites, so the tests pin both faces of the
five claims, the refusal when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e427_most_of_the_aid_needs_a_plastic_bias as e427

#: the corpus's shape: per roll, the naive arm's level and the buffer's gain and cut at forty replicates
ROLLS = {
    "frozen": {"naive_accuracy": 0.9306, "naive_mf": 0.0227, "gain": 0.0130, "cut": 0.0208},
    "plastic": {"naive_accuracy": 0.9125, "naive_mf": 0.0750, "gain": 0.0484, "cut": 0.0784},
}
SUITES = {"suite600": {"naive_accuracy": 0.9391, "naive_mf": 0.0258, "gain": 0.0145, "cut": 0.0222},
          "suite1440": {"naive_accuracy": 0.9280, "naive_mf": 0.0293, "gain": 0.0158, "cut": 0.0238}}
ARMS = ["ewc", "ewc-block", "ewc-block-rand", "naive", "replay"]


def _roll(spec, reps=40, arms=ARMS):
    got = {a: {"replicates": reps, "accuracy": spec["naive_accuracy"], "mean_forgetting": spec["naive_mf"],
               "gain": 0.0, "cut": 0.0} for a in arms}
    got[e427.BUFFER]["gain"] = spec["gain"]
    got[e427.BUFFER]["cut"] = spec["cut"]
    got[e427.BUFFER]["accuracy"] = spec["naive_accuracy"] + spec["gain"]
    return {"artifact": "x.json", "naive": {"accuracy": spec["naive_accuracy"], "mean_forgetting": spec["naive_mf"]},
            "arms": got, "frozen_bias": True, "doc": {"config": {}}}


def _doc(frozen=None, plastic=None, suites=None, differing=(e427.FROZEN_FLAG,), same_draws=True, reps=40,
         want_suites=True, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "pair": {}, "suites": {}, "spans": {}}
    f = dict(ROLLS["frozen"] if frozen is None else frozen)
    p = dict(ROLLS["plastic"] if plastic is None else plastic)
    suites = SUITES if suites is None else suites
    fr, pr = _roll(f, reps), _roll(p, reps)
    sr = {n: _roll(v, reps) for n, v in suites.items()}
    rolls = [fr] + list(sr.values())
    gains = [r["arms"][e427.BUFFER]["gain"] for r in rolls]
    return {"ok": True, "reason": None,
            "pair": {"frozen": fr, "plastic": pr, "differing_config": list(differing), "same_draws": same_draws},
            "suites": sr,
            "spans": {"pair_replicates": sorted({fr["arms"][e427.BUFFER]["replicates"],
                                                 pr["arms"][e427.BUFFER]["replicates"]}),
                      "frozen_suites": len(sr), "arms": sorted(fr["arms"]),
                      "frozen_gain": f["gain"], "plastic_gain": p["gain"], "frozen_cut": f["cut"],
                      "plastic_cut": p["cut"], "frozen_naive_mf": f["naive_mf"], "plastic_naive_mf": p["naive_mf"],
                      "gain_ratio": (f["gain"] / p["gain"]) if p["gain"] else None,
                      "cut_ratio": (f["cut"] / p["cut"]) if p["cut"] else None,
                      "suite_gain_span": (max(gains) - min(gains)) if gains else None}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e427.judge(_doc(**kw))}


def _rolls(**kw):
    out = {k: dict(v) for k, v in ROLLS.items()}
    out.update({k: dict(v) for k, v in (kw.pop("override", {}) or {}).items()})
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the freeze taking the buffer to a quarter of its worth, three frozen rolls agreeing
    j = _judge()
    for cid in ("BC1", "BC2", "BC3", "BC4", "BC5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BC1: another field differing, draws that are not shared, too few replicates, and too few suites
    assert _judge(differing=("frozen_bias", "batch"))["BC1"].startswith("FALSIFIER")
    assert _judge(same_draws=False)["BC1"].startswith("FALSIFIER")
    assert _judge(reps=39)["BC1"].startswith("FALSIFIER")
    assert _judge(suites={"suite600": SUITES["suite600"]})["BC1"].startswith("FALSIFIER")

    # BC2: a buffer the freeze barely touches, and one between the bars
    assert _judge(frozen={**ROLLS["frozen"], "gain": 0.0484})["BC2"].startswith("FALSIFIER")
    assert _judge(frozen={**ROLLS["frozen"], "gain": 0.0300})["BC2"].startswith("NULL")

    # BC3: the same on the cut
    assert _judge(frozen={**ROLLS["frozen"], "cut": 0.0784})["BC3"].startswith("FALSIFIER")
    assert _judge(frozen={**ROLLS["frozen"], "cut": 0.0450})["BC3"].startswith("NULL")

    # BC4: a freeze that leaves the naive arm forgetting the same or more
    assert _judge(frozen={**ROLLS["frozen"], "naive_mf": 0.0750})["BC4"].startswith("FALSIFIER")

    # BC5: a suite whose frozen gain reaches the plastic one, and one whose span is wide
    assert _judge(suites={**SUITES, "suite600": {**SUITES["suite600"], "gain": 0.0484}})["BC5"].startswith("FALSIFIER")
    assert _judge(suites={**SUITES, "suite600": {**SUITES["suite600"], "gain": 0.0500}})["BC5"].startswith("FALSIFIER")

    #: a roll absent or carrying no naive arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e427.judge(_doc(ok=False)))


def test_the_rolls_and_the_thresholds_are_registered():
    #: one configuration rolled both ways, and two further suites rolled under the frozen bias
    assert e427.PAIR[0].name == "e140_r32_methods_frozenbias_40reps.json"
    assert e427.PAIR[1].name == "e140_r32_methods_plastic_40reps.json"
    assert sorted(e427.SUITES) == ["suite1440", "suite600"], sorted(e427.SUITES)
    assert e427.FROZEN_FLAG == "frozen_bias" and e427.RUN_FIELDS == ("json_out", "save_theta")
    assert e427.BASELINE == "naive" and e427.BUFFER == "replay"
    assert (e427.MIN_ARMS, e427.MIN_REPS, e427.MIN_SUITES) == (4, 40, 2)
    assert (e427.HALF, e427.HALF_FIRES) == (0.5, 0.7)
    assert (e427.SPAN, e427.SPAN_FIRES) == (0.01, 0.03)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e427_most_of_the_aid_needs_a_plastic_bias.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e427.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e427.judge(d)}
    #: the ledger being carried and the freeze taking most of the buffer are structural facts
    assert verdicts["BC1"].startswith("MET") and verdicts["BC2"].startswith("MET"), verdicts
    pair = d["pair"]
    assert pair["differing_config"] == [e427.FROZEN_FLAG] and pair["same_draws"], pair["differing_config"]
    assert len(pair["frozen"]["arms"]) >= e427.MIN_ARMS, sorted(pair["frozen"]["arms"])
    assert all(v["replicates"] >= e427.MIN_REPS for v in pair["frozen"]["arms"].values())
    assert len(d["suites"]) >= e427.MIN_SUITES, sorted(d["suites"])
    for n, roll in d["suites"].items():
        assert roll["frozen_bias"], n
        assert roll["arms"][e427.BUFFER]["gain"] < pair["plastic"]["arms"][e427.BUFFER]["gain"], n
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
