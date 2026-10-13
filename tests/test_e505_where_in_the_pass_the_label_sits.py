"""`e505` moves the label across a three-trial pass and reads the placement as an axis, so the tests pin the three
claims' both faces, the constants they are registered with, and the refusal when a run is absent.

The falsifier test drives `judge` on synthetic readings rather than on the artifact, so a claim's outcome is never
asserted as the artifact's shape: what is pinned is that each registered falsifier does fire, and that the three
claims read both faces. A second test drives `reading` on synthetic artifacts on disk, so the pipeline that compares
the placements is exercised as well.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e505_where_in_the_pass_the_label_sits as e505

ARMS = e505.ARMS
#: the reading's shape: the pass learned at the label first and fell as the placement moved later
ACC = {"at0": {"naive": 0.8538, "ewc-block": 0.8392, "replay": 0.8580},
       "at1": {"naive": 0.5500, "ewc-block": 0.5400, "replay": 0.5600},
       "at2": {"naive": 0.3000, "ewc-block": 0.3100, "replay": 0.3200}}
#: the label's share of the read, falling with the window
SHARES = {"at0": {"share": 1.0571, "window": 11, "across": 4.3099},
          "at1": {"share": 0.5900, "window": 7, "across": 2.3000},
          "at2": {"share": 0.0300, "window": 3, "across": 0.1200}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.01, "se": 0.001, "sigma": sigma}


def _against(differ=None, draw_differ=None, added=None, missing=None, moved=None):
    return {"same": 60, "inert": ["loop_label_first", "loop_label_at"],
            "differ": {k: [None, 1] for k in (differ or [])},
            "moved": (moved if moved is not None else {"loop_label_first": False, "loop_label_at": 1}),
            "draw": {"agree": {"cue_sha1": True, "episode_len": True},
                     "differ": list(["label_first"] if draw_differ is None else draw_differ),
                     "added": list(["label_at"] if added is None else added),
                     "missing": list(["label_first"] if missing is None else missing)}}


def _doc(differ=None, draw_differ=None, added=None, missing=None, replicates=20,
         diag=None, end_to_end=None, shares=None, absent=False):
    diag = {k: dict(v) for k, v in (diag or ACC).items()}
    end_to_end = dict(end_to_end or {a: _paired(+0.5538, +12.00) for a in ARMS})
    shares = {k: dict(v) for k, v in (shares or SHARES).items()}
    if absent:
        return {"ok": False, "reason": "the label-at-1 run is absent", "runs": {}, "share": {}, "recovery": {},
                "spans": {}}
    return {
        "ok": True, "reason": None,
        "runs": {label: {"artifact": f"{label}.json", "arms": {a: {"replicates": replicates} for a in ARMS}}
                 for label in ("at0", "at1", "at2")},
        "share": shares,
        "recovery": {"end_to_end": end_to_end,
                     "step_01": {a: _paired(+0.30, +6.00) for a in ARMS},
                     "step_12": {a: _paired(+0.25, +5.00) for a in ARMS}},
        "spans": {
            "arms": list(ARMS), "placements": dict(e505.PLACE), "windows": dict(e505.WINDOW),
            "episode": e505.EPISODE, "trial_len": e505.TAU // e505.EPISODE, "chance": e505.CHANCE,
            "sigma": e505.SIGMA, "arms_needed": e505.ARMS_NEEDED,
            "replicates": [replicates],
            "config": {"at0": _against(), "at1": _against(differ, draw_differ, added, missing),
                       "at2": _against(differ, draw_differ, added, missing)},
            "draw": {"at0": _against()["draw"], "at1": _against(differ, draw_differ, added, missing)["draw"],
                     "at2": _against(differ, draw_differ, added, missing)["draw"]},
            "accuracy_diagonal": diag,
            "accuracy_last": {k: {a: 0.60 for a in ARMS} for k in ("at0", "at1", "at2")},
            "share": {k: dict(v) for k, v in shares.items()},
        },
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e505.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("VA1", "VA2", "VA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # VA1: another config field differing, a draw field outside the placement added, missing or differing, and a
    # thin run
    assert _judge(differ=["iters"])["VA1"].startswith("FALSIFIER")
    assert _judge(added=["reward_map_sha1"])["VA1"].startswith("FALSIFIER")
    assert _judge(missing=["boundary_sha1"])["VA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["VA1"].startswith("FALSIFIER")
    assert _judge(replicates=19)["VA1"].startswith("FALSIFIER")

    # VA2: fewer than two arms non-increasing, and fewer than two arms whose end-to-end move resolves
    not_ordered = {"at0": {"naive": 0.8538, "ewc-block": 0.5300, "replay": 0.5300},
                   "at1": {"naive": 0.8200, "ewc-block": 0.5400, "replay": 0.5600},
                   "at2": {"naive": 0.3000, "ewc-block": 0.3100, "replay": 0.3200}}
    assert _judge(diag=not_ordered)["VA2"].startswith("FALSIFIER")
    thin = {"naive": _paired(+0.5538, +12.00), "ewc-block": _paired(+0.2000, +1.00),
            "replay": _paired(-0.1000, -0.80)}
    assert _judge(end_to_end=thin)["VA2"].startswith("FALSIFIER")

    # VA3: a share that does not fall
    flat = {"at0": {"share": 0.5000, "window": 11, "across": 2.0},
            "at1": {"share": 0.6000, "window": 7, "across": 2.4},
            "at2": {"share": 0.0500, "window": 3, "across": 0.2}}
    assert _judge(shares=flat)["VA3"].startswith("FALSIFIER")

    #: a reading with no run at all refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e505.judge(_doc(absent=True)))


def test_the_runs_the_arms_and_the_axis_are_registered():
    assert e505.ZERO.name == "e497_earned_label_episode3_labelfirst_20reps.json"
    assert e505.ONE.name == "e505_label_at1_episode3_20reps.json"
    assert e505.TWO.name == "e505_label_at2_episode3_20reps.json"
    assert set(e505.MOVED) == {"loop_label_first", "loop_label_at"}, e505.MOVED
    assert set(e505.DRAW_MOVED) == {"label_first", "label_at"}, e505.DRAW_MOVED
    assert set(e505.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e505.PLACE == {"at0": 0, "at1": 1, "at2": 2}, e505.PLACE
    assert e505.WINDOW == {0: 11, 1: 7, 2: 3}, e505.WINDOW
    assert e505.CHANCE == 0.25
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e505.EPISODE, e505.MIN_REPS, e505.SIGMA, e505.ARMS_NEEDED) == (3, 20, 2.0, 2)
    assert e505._inert("loop_label_at", None, 2) and e505._inert("loop_label_first", True, False)
    assert not e505._inert("iters", 500, 100)
    #: the three claims are registered with their falsifiers beside them, before the reading was opened
    assert [c[0] for c in e505.CLAIMS] == ["VA1", "VA2", "VA3"]
    assert all("falsifier:" in c[3] for c in e505.CLAIMS)


def _replicate(acc):
    return {"learned": [acc] * 4, "final_per_task": [acc] * 3}


def _write(path: Path, cfg: dict, draw: dict, acc: float) -> None:
    doc = {"config": cfg, "env_draw": draw,
           "methods": {a: {"replicates": [_replicate(acc) for _ in range(20)]} for a in ARMS}}
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_the_reading_compares_the_placements_from_artifacts(tmp_path):
    base = {"loop_episode": 3, "loop_label_first": True, "json_out": "base.json", "save_theta": None}
    base_draw = {"cue_sha1": "a", "episode_len": 3, "label_first": True}
    _write(tmp_path / "zero.json", base, base_draw, 0.8538)
    _write(tmp_path / "one.json", {**base, "loop_label_first": False, "loop_label_at": 1,
                                   "json_out": "one.json"},
           {"cue_sha1": "a", "episode_len": 3, "label_at": 1}, 0.5500)
    _write(tmp_path / "two.json", {**base, "loop_label_first": False, "loop_label_at": 2,
                                   "json_out": "two.json"},
           {"cue_sha1": "a", "episode_len": 3, "label_at": 2}, 0.3000)
    r = e505.reading(zero=tmp_path / "zero.json", one=tmp_path / "one.json", two=tmp_path / "two.json")
    assert set(r["runs"]) == {"at0", "at1", "at2"}, sorted(r["runs"])
    one = r["runs"]["at1"]
    assert one["config"]["differ"] == {}, one["config"]
    assert one["config"]["moved"]["loop_label_at"] == 1
    assert one["draw"]["added"] == ["label_at"], one["draw"]
    assert one["draw"]["missing"] == ["label_first"], one["draw"]
    assert {v["replicates"] for v in one["arms"].values()} == {e505.MIN_REPS}
    #: the config and the draw are compared inside the runs, so the artifact carries no top-level `config`
    assert "config" not in r and "env" not in r and "tasks" not in r, sorted(r)
    #: an absent run reads as absent and refuses, rather than raising
    gone = e505.reading(zero=tmp_path / "zero.json", one=tmp_path / "nope.json", two=tmp_path / "two.json")
    assert gone["ok"] is False
    assert all(row["verdict"].startswith("REFUSED") for row in e505.judge(gone))


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e505_where_in_the_pass_the_label_sits.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e505.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    assert sorted(d["runs"]) == ["at0", "at1", "at2"], sorted(d["runs"])
    assert d["spans"]["replicates"] == [e505.MIN_REPS], d["spans"]["replicates"]
    #: the counts that grow with the corpus are read as bounds, so a longer artifact does not break the test
    for label in ("at0", "at1", "at2"):
        assert d["spans"]["config"][label]["same"] >= 40, label
        assert len(d["spans"]["draw"][label]["agree"]) >= 20, label
        for a in ARMS:
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (label, a)
    assert d["share"]["at0"]["window"] == 11 and d["share"]["at2"]["window"] == 3
    for a in ARMS:
        assert d["recovery"]["end_to_end"][a]["n"] >= e505.MIN_REPS, a
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
