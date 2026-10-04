"""`e414` writes the card's third revision and reads every number in it from an artifact that measured it, so the
tests pin both faces of the five claims, the refusal when one of those artifacts is absent, and the live re-framing
the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e414_the_game_card_revision_three as e414

#: the card's second revision, as `e409` wrote it: the draw's side only, which the third carries unchanged
REVISION2 = {
    "substrate": {"circuit": "mb+cx+al@n952", "circuit_size": 300, "readout_subset": "59926518137c",
                  "basis": "cell_class", "support": 80, "seed0": 0, "classes_per_task": 4},
    "loop": {"cue_at": 0, "drive": "action", "world_dims": 8, "coupled": True, "leak": 0.35, "nonlinear": False,
             "readout": "world"},
    "protocol": {"tasks": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "train": 96, "test": 48,
                 "lr": 0.003, "schedule": "iteration budget"},
    "arms": ["naive", "replay"],
    "metrics": ["accuracy", "the retention matrix's diagonal", "its last row", "their difference", "backward transfer"],
    "absent": ["a reward", "a policy", "an episode boundary", "a held-out task", "a second world", "a second draw"],
    "world": {"span_at_20": 0.075, "span_at_500": 0.3104, "worlds_measured": 6},
    "stream": {"span_at_500": 0.0323, "against_the_worlds": 0.3344, "streams_measured": 3},
    "recovery": {"worlds_at_the_far_point": 5, "recovering": 1, "bar": 0.05},
    "invariance": {"reading": 0.6875, "spread": 0.0, "over_at_least": 10},
}
#: the arm's series, as `e413` read it off the six worlds at budgets 1, 20 and 500
ARM = {"artifact": "e413_the_aid_turns_on_in_every_world.json", "budgets": [1, 20, 500],
       "worlds": ["card", "cue1", "cue14", "cue3", "cue6", "cue9"],
       "small_band": [-0.017361111069718993, 0.036458333333333315],
       "top_band": [0.132986109269162, 0.1593749985098839],
       "rise_band": [0.1142361148881414, 0.16388888352861009],
       "span_at_20": 0.0409722183520595, "least_rise": 0.1142361148881414,
       "least_rise_over_span_at_20": 0.1142361148881414 / 0.0409722183520595}
DRAW = {"artifacts": ["e410_the_benchmarks_own_metric.json", "e411_the_rehearsal_on_the_six_worlds.json"],
        "draw_span_at_500": 0.030902775128682558, "least_gain_at_500": 0.132986109269162,
        "gain_over_draw_span": 0.132986109269162 / 0.030902775128682558}
CUTS = {"artifact": "e413_the_aid_turns_on_in_every_world.json", "at_20": 0.06354166716337203,
        "at_500": 0.23385416166856887}


def _doc(arm=None, draw=None, cuts=None, revision=None, mutate=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision2": {}, "arm": {}, "draw": {}, "cuts": {}}
    card = {k: json.loads(json.dumps(v)) for k, v in REVISION2.items()}
    card["name"] = "the closed-loop earned-label game"
    card["revision"] = e414.REVISION if revision is None else revision
    card["arm"] = dict(e414.ARM_CLAUSE)
    card["draw_terms"] = dict(e414.DRAW_CLAUSE)
    if mutate:
        card[mutate] = {"changed": True}
    return {"ok": True, "reason": None, "card": card,
            "revision2": {k: json.loads(json.dumps(v)) for k, v in REVISION2.items()},
            "arm": dict(ARM if arm is None else arm), "draw": dict(DRAW if draw is None else draw),
            "cuts": dict(CUTS if cuts is None else cuts)}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e414.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the second revision carried, the arm's bands the artifact's own, and the ratio above twice
    j = _judge()
    for cid in ("AN1", "AN2", "AN3", "AN4", "AN5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AN1: a clause changed, and a revision number that is not three
    assert _judge(mutate="loop")["AN1"].startswith("FALSIFIER")
    assert _judge(revision=2)["AN1"].startswith("FALSIFIER")

    # AN2: a band that is not the artifact's, and a world count that is not six
    wide = {k: (list(v) if isinstance(v, list) else v) for k, v in ARM.items()}
    wide["small_band"] = [ARM["small_band"][0], 0.07]
    assert _judge(arm=wide)["AN2"].startswith("FALSIFIER")
    short = {k: (list(v) if isinstance(v, list) else v) for k, v in ARM.items()}
    short["worlds"] = ARM["worlds"][:5]
    assert _judge(arm=short)["AN2"].startswith("FALSIFIER")

    # AN3: a ratio the artifact does not read, and one at or below the bar
    off = {k: v for k, v in ARM.items()}
    off["least_rise_over_span_at_20"] = 2.50
    assert _judge(arm=off)["AN3"].startswith("FALSIFIER")
    under = {k: v for k, v in ARM.items()}
    under["least_rise_over_span_at_20"] = 1.80
    under["least_rise"] = 1.80 * ARM["span_at_20"]
    assert _judge(arm=under)["AN3"].startswith("FALSIFIER")

    # AN4: a draw span that is not the artifact's
    drifted = {k: v for k, v in DRAW.items()}
    drifted["draw_span_at_500"] = 0.05
    assert _judge(draw=drifted)["AN4"].startswith("FALSIFIER")

    # AN5: a five-hundred cut under the bar
    shallow = {k: v for k, v in CUTS.items()}
    shallow["at_500"] = 0.15
    assert _judge(cuts=shallow)["AN5"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e414.judge(_doc(ok=False)))


def test_the_artifacts_and_the_clauses_are_registered():
    #: revision 2's artifact, the three the arm's term is read from, and the clause the third revision adds
    assert e414.CARD2.name == "e409_the_game_card_revision_two.json"
    assert e414.ARMS.name == "e413_the_aid_turns_on_in_every_world.json"
    assert e414.BENCH.name == "e410_the_benchmarks_own_metric.json"
    assert e414.REHEARSAL.name == "e411_the_rehearsal_on_the_six_worlds.json"
    assert e414.REVISION == 3 and e414.TWICE == 2.0 and e414.CUT_BAR == 0.20
    assert e414.REVISION2_FIELDS == ("substrate", "loop", "protocol", "arms", "metrics", "absent", "world", "stream",
                                     "recovery", "invariance")
    assert e414.ARM_CLAUSE["budgets"] == [1, 20, 500] and e414.ARM_CLAUSE["worlds_measured"] == 6
    assert e414.ARM_CLAUSE["small_band"] == [-0.0174, 0.0365] and e414.ARM_CLAUSE["top_band"] == [0.1330, 0.1594]
    assert e414.ARM_CLAUSE["rise_band"] == [0.1142, 0.1639] and e414.ARM_CLAUSE["least_rise_over_span_at_20"] == 2.79
    assert e414.DRAW_CLAUSE == {"draw_span_at_500": 0.0309, "least_gain_at_500": 0.1330,
                                "gain_over_draw_span": 4.30}


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e414_the_game_card_revision_three.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e414.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e414.judge(d)}
    #: the second revision being carried and the arm's clause being the artifact's are structural facts
    assert verdicts["AN1"].startswith("MET") and verdicts["AN2"].startswith("MET"), verdicts
    card = d["card"]
    assert card["revision"] == e414.REVISION, card["revision"]
    #: the third revision's own clause is present beside the four revision 2 wrote, and every number is a read one
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms"):
        assert k in card, k
    assert card["arm"] == e414.ARM_CLAUSE and card["draw_terms"] == e414.DRAW_CLAUSE
    assert len(d["arm"]["worlds"]) == e414.ARM_CLAUSE["worlds_measured"]
    assert d["cuts"]["at_500"] > e414.CUT_BAR, d["cuts"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
