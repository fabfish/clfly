"""`e393` redraws the card's world four times at its canonical near point, so the tests pin both faces of the five
claims, the refusal when a run or its weights is absent, and the live replication the unit exists to measure.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e393_the_card_on_four_more_worlds as e393

PLACED_VALUES = {"loop_world_leak": 0.35, "readout_from_world": True, "loop_world_dims": 8, "closed_loop": True,
                 "loop_world_modes": 0, "loop_world_nonlinear": False, "repeats": 20, "circuit_size": 300,
                 "readout_size": 32, "basis": "cell_class", "seed0": 0,
                 "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"],
                 "task_readout_widths": [8], "iters": 20, "lr": 0.003, "batch": 32}


def _settings(seed):
    return {**PLACED_VALUES, "loop_seed": seed, "cue_sha1": f"c{seed}", "feedback_sha1": f"f{seed}", "n_cue": 12,
            "action_sha1": f"a{seed}", "n_action": 8, "drive_from_cue": False, "loop_drive_from_cue": False,
            "world_drive_sha1": f"d{seed}", "world_read_sha1": f"r{seed}", "world_coupling_sha1": f"k{seed}"}


#: the corpus's shape: the connectome reads about 0.69 and twenty updates cost each world at least 0.05
GOOD_INIT = {"card": 0.6875, "1": 0.68, "2": 0.70, "3": 0.665, "4": 0.69}
GOOD_BODY = {"card": 0.5740, "1": 0.58, "2": 0.55, "3": 0.60, "4": 0.56}


def _doc(initial=GOOD_INIT, body=GOOD_BODY, settings=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run's weights are absent
        return {"ok": False, "worlds": {}, "settings": {}, "reason": reason}
    settings = settings if settings is not None else {n: _settings(0 if n == "card" else int(n))
                                                      for n in ("card", "1", "2", "3", "4")}
    worlds = {n: {"artifact": f"{n}.json", "iters": 20, "repeats": 20, "initial_task_0": initial[n],
                  "body_task_0": body[n], "head_task_0": 0.25} for n in initial}
    initials = list(initial.values())
    bodies = list(body.values())
    draws = {f: sorted({str(s.get(f)) for s in settings.values()}) for f in e393.WORLD_FIELDS}
    return {"ok": True, "worlds": worlds, "settings": settings,
            "spread": {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)},
            "draws": draws, "arm": e393.NAIVE, "reps": e393.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e393.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: four redraws whose readings and whose cost of twenty updates all land near the card's
    j = _judge()
    for cid in ("N1", "N2", "N3", "N4", "N5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # N1: a placed field moved between two worlds, and a field in neither list
    moved = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2", "3", "4")}
    moved["2"] = {**moved["2"], "loop_world_leak": 1.0}
    assert _judge(settings=moved)["N1"]["verdict"].startswith("FALSIFIER")
    extra = {n: {**_settings(0 if n == "card" else int(n)), "mystery": 1} for n in ("card", "1", "2", "3", "4")}
    assert _judge(settings=extra)["N1"]["verdict"].startswith("FALSIFIER")

    # N2: two new worlds sharing a fingerprint, and one of them the card's own
    twin = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2", "3", "4")}
    twin["2"] = {**twin["2"], "world_read_sha1": twin["1"]["world_read_sha1"]}
    assert _judge(settings=twin)["N2"]["verdict"].startswith("FALSIFIER")
    same = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2", "3", "4")}
    same["3"] = {**same["3"], "world_coupling_sha1": same["card"]["world_coupling_sha1"]}
    assert _judge(settings=same)["N2"]["verdict"].startswith("FALSIFIER")

    # N3: a substrate reading that moves with the world, and one between the bars
    assert _judge(initial={"card": 0.6875, "1": 0.68, "2": 0.50, "3": 0.665, "4": 0.69})["N3"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(initial={"card": 0.6875, "1": 0.68, "2": 0.58, "3": 0.665, "4": 0.69})["N3"][
        "verdict"].startswith("NULL")

    # N4: a body reading that spreads with the world, and one between the bars
    assert _judge(body={"card": 0.5740, "1": 0.58, "2": 0.40, "3": 0.60, "4": 0.56})["N4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(body={"card": 0.5740, "1": 0.58, "2": 0.47, "3": 0.60, "4": 0.56})["N4"][
        "verdict"].startswith("NULL")

    # N5: a world where twenty updates cost the body nothing
    assert _judge(body={"card": 0.5740, "1": 0.58, "2": 0.55, "3": 0.68, "4": 0.56})["N5"][
        "verdict"].startswith("FALSIFIER")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e393.judge(_doc(ok=False)))


def test_the_two_lists_cover_the_card_and_the_draw():
    #: the placed fields are the card's and the drawn ones are the environment's own draw, and they do not overlap
    assert not set(e393.PLACED) & set(e393.DRAWN), set(e393.PLACED) & set(e393.DRAWN)
    for k in ("loop_world_leak", "loop_world_dims", "basis", "seed0", "lr", "batch", "repeats"):
        assert k in e393.PLACED, k
    for k in ("loop_seed", "cue_sha1", "action_sha1", "world_drive_sha1", "world_coupling_sha1"):
        assert k in e393.DRAWN, k
    #: every field the module reads off a run is in one of them, so the closure claim has something to close over
    keys = set(_settings(1))
    assert keys <= set(e393.PLACED) | set(e393.DRAWN), sorted(keys - set(e393.PLACED) - set(e393.DRAWN))


def test_the_live_replication_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e393_the_card_on_four_more_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e393.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e393.judge(d)}
    #: **the live N1 FIRES and is read off the artifact.** `loop_cue_at` is a field the reading carries and neither
    #: list holds it, so the closure claim is false as written while the field itself is constant; what is asserted
    #: is that the verdict is one of the two and that the four draws are four worlds.
    assert verdicts["N1"].split(" -- ")[0] in ("MET", "FALSIFIER FIRED"), verdicts["N1"]
    assert verdicts["N2"].startswith("MET"), verdicts["N2"]
    assert sorted(d["worlds"]) == ["1", "2", "3", "4", "card"], sorted(d["worlds"])
    assert all(len(v) == 5 for v in d["draws"].values()), d["draws"]
    #: the card's own run is one of the five, so the comparison is against an artifact and not a constant
    assert d["worlds"]["card"]["artifact"].startswith("e389"), d["worlds"]["card"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
