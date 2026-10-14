"""`e511` puts the world's payout on the pass at the window curve's knee, so the tests pin the three claims' both
faces, the constants they are registered with, the three points the reading assembles, and the refusal when an input
is absent.

The falsifier test drives `reading` on synthetic artifacts on disk and then `judge` on the reading, so a claim's
outcome is never asserted as the artifact's shape: what is pinned is that each registered falsifier does fire and that
the three claims read both faces. Counts that grow with the corpus are read as bounds.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e511_the_earning_at_the_knee as e511

ARMS = e511.ARMS


def _sample(mean: float, e: float, n: int = 20) -> list:
    """A paired sample of ``n`` values with mean ``mean``: ten at ``mean + e`` and ten at ``mean - e``."""
    return [mean + e] * (n // 2) + [mean - e] * (n - n // 2)


def _per(value) -> dict:
    return dict(value) if isinstance(value, dict) else {a: value for a in ARMS}


def _run(path, cfg, draw, acc, level, move, n=20, e=0.20):
    """One synthetic run: each arm's accuracy, its reward level per replicate and its map's movement."""
    acc, level, move = _per(acc), _per(level), _per(move)
    methods = {}
    for a in ARMS:
        reps = []
        for i in range(n):
            rep = {"learned": [acc[a]] * 4, "final_per_task": [acc[a]] * 3}
            if level[a] is None:
                rep["reward_retention"] = [[None] * 3 for _ in range(3)]
            else:
                d = _sample(level[a], e, n)[i]
                m = [[None] * 3 for _ in range(3)]
                for k in range(3):
                    m[k][k] = d
                for j in range(3):
                    m[2][j] = d
                rep["reward_retention"] = m
            rep["policy_move"] = None if move[a] is None else move[a]
            reps.append(rep)
        methods[a] = {"replicates": reps}
    path.write_text(json.dumps({"config": cfg, "env_draw": draw, "methods": methods}), encoding="utf-8")
    return path


def _cfg(earn=True, **kw):
    base = {"loop_policy": earn, "loop_earn": earn, "loop_episode": 6, "loop_label_at": 1,
            "json_out": "earn" if earn else "meter", "save_theta": None, "iters": 500}
    base.update(kw)
    return base


def _docs(tmp_path, earn_cfg=None, meter_cfg=None, earn_draw=None, meter_draw=None,
          here_acc=0.49, here_meter=-20.0, here_gain=3.0, n=20, move=4.0,
          learned_acc=0.83, learned_meter=-6.0, learned_gain=1.3,
          chance_acc=0.30, chance_meter=-42.0, chance_gain=7.0):
    """The three points: this unit's pair, `e500`'s learned pair and `e507`'s chance pair, on disk."""
    draw = {"episode_len": 6, "label_at": 1, "cue_sha1": "a"}
    meter_level = _per(here_meter)
    earn_level = {a: meter_level[a] + _per(here_gain)[a] for a in ARMS}
    learned_level, chance_level = _per(learned_meter), _per(chance_meter)
    learned_earn = {a: learned_level[a] + _per(learned_gain)[a] for a in ARMS}
    chance_earn = {a: chance_level[a] + _per(chance_gain)[a] for a in ARMS}
    return {
        "earned": _run(tmp_path / "new_earn.json", _cfg(True) if earn_cfg is None else earn_cfg,
                       draw if earn_draw is None else earn_draw, _per(here_acc), earn_level, move, n, e=0.35),
        "meter": _run(tmp_path / "new_meter.json", _cfg(False) if meter_cfg is None else meter_cfg,
                      draw if meter_draw is None else meter_draw, _per(here_acc), meter_level, move, n),
        "learned_earn": _run(tmp_path / "learned_earn.json", _cfg(True), draw, _per(learned_acc),
                             learned_earn, 5.5, n),
        "learned_meter": _run(tmp_path / "learned_meter.json", _cfg(False), draw, _per(learned_acc),
                              learned_level, 5.5, n),
        "chance_earn": _run(tmp_path / "chance_earn.json", _cfg(True), draw, _per(chance_acc),
                            chance_earn, 10.5, n),
        "chance_meter": _run(tmp_path / "chance_meter.json", _cfg(False), draw, _per(chance_acc),
                             chance_level, 10.5, n),
    }


def _read(tmp_path, **kw):
    p = _docs(tmp_path, **kw)
    return e511.reading(new=p["earned"], meter=p["meter"], learned_earn=p["learned_earn"],
                        learned_meter=p["learned_meter"], chance_earn=p["chance_earn"],
                        chance_meter=p["chance_meter"], beside={})


def _judge(r):
    return {row["id"]: row["verdict"] for row in e511.judge(r)}


def test_the_three_claims_read_both_faces(tmp_path):
    j = _judge(_read(tmp_path))
    for cid in ("BA1", "BA2", "BA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BA1: another config field differing, the flags not both moved, a draw field differing, added or missing, a thin
    # run
    assert _judge(_read(tmp_path, earn_cfg=_cfg(True, iters=100)))["BA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_cfg=_cfg(True, loop_earn=False)))["BA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_draw={"episode_len": 6, "label_at": 1, "cue_sha1": "b"})
                  )["BA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_draw={"episode_len": 6, "label_at": 1}))["BA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_draw={"episode_len": 6, "label_at": 1, "cue_sha1": "a", "extra": 1})
                  )["BA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, n=19))["BA1"].startswith("FALSIFIER")

    # BA2: a replicate whose map distance is not positive, a run that records no movement, a contrast that does not
    # resolve, and one that is negative
    assert _judge(_read(tmp_path, move=0.0))["BA2"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, move=None))["BA2"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, here_gain=0.05))["BA2"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, here_gain=-3.0))["BA2"].startswith("FALSIFIER")

    # BA3: a meter level outside the interval on an arm, a gain outside it on two arms, an accuracy outside it
    assert _judge(_read(tmp_path, here_meter={a: -50.0 for a in ARMS}))["BA3"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, here_gain={"naive": 0.5, "ewc-block": 0.5, "replay": 3.0})
                  )["BA3"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, here_acc={a: 0.95 for a in ARMS}))["BA3"].startswith("FALSIFIER")

    #: each claim refuses on its own absent input, and BA3 refuses while BA1 and BA2 still read
    p = _docs(tmp_path)
    gone = e511.reading(new=tmp_path / "nope.json", meter=p["meter"], learned_earn=p["learned_earn"],
                        learned_meter=p["learned_meter"], chance_earn=p["chance_earn"],
                        chance_meter=p["chance_meter"], beside={})
    v = _judge(gone)
    assert v["BA1"].startswith("REFUSED") and v["BA2"].startswith("REFUSED") and v["BA3"].startswith("REFUSED")
    no_points = e511.reading(new=p["earned"], meter=p["meter"], learned_earn=tmp_path / "nope.json",
                             learned_meter=tmp_path / "nope.json", chance_earn=p["chance_earn"],
                             chance_meter=p["chance_meter"], beside={})
    w = _judge(no_points)
    assert w["BA3"].startswith("REFUSED") and w["BA1"].startswith("MET") and w["BA2"].startswith("MET")
    #: with no reading at all every claim refuses
    assert all(row["verdict"].startswith("REFUSED") for row in e511.judge({"ok": False, "reason": "no run"}))


def test_the_runs_the_points_and_the_pass_are_registered():
    assert e511.NEW.name == "e511_label_at1_episode6_reward_earn_20reps.json"
    assert e511.METER.name == "e511_label_at1_episode6_reward_20reps.json"
    assert e511.LEARNED_EARN.name == "e500_earned_label_episode2_labelfirst_reward_earn_20reps.json"
    assert e511.LEARNED_METER.name == "e498_earned_label_episode2_labelfirst_reward_20reps.json"
    assert e511.CHANCE_EARN.name == "e507_label_at1_episode3_reward_earn_20reps.json"
    assert e511.CHANCE_METER.name == "e507_label_at1_episode3_reward_20reps.json"
    assert set(e511.MOVED) == {"loop_policy", "loop_earn"}, e511.MOVED
    assert set(e511.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e511.EPISODE, e511.LABEL_AT, e511.TRIAL_LEN) == (6, 1, 2)
    assert e511.WINDOW == 9, e511.WINDOW
    assert e511.TAU == 12 and e511.SIZE == 300 and e511.READOUT_SIZE == 32
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e511.MIN_REPS, e511.SIGMA, e511.CHANCE, e511.ARMS_NEEDED) == (20, 2.0, 0.25, 2)
    assert e511._inert("loop_policy", False, True) and e511._inert("loop_earn", False, True)
    assert e511._inert("json_out", "a", "b")
    assert not e511._inert("iters", 500, 100)
    #: between, whichever of the two ends is the larger
    assert e511._between(-20.0, -6.05, -42.3) and e511._between(0.49, 0.83, 0.30)
    assert not e511._between(-50.0, -6.05, -42.3)
    #: the three claims are registered with their falsifiers beside them, before the reading was opened
    assert [c[0] for c in e511.CLAIMS] == ["BA1", "BA2", "BA3"]
    assert all("falsifier:" in c[3] for c in e511.CLAIMS)


def test_the_reading_builds_the_three_points_from_artifacts(tmp_path):
    r = _read(tmp_path)
    assert r["ok"] and r["reward"] is not None and r["accuracy"] is not None and r["reward_last"] is not None
    #: the pair is two flags apart and the draw moves nothing
    cfg = r["spans"]["config"]["earned"]
    assert cfg["differ"] == {}, cfg
    assert sorted(cfg["inert"]) == ["json_out", "loop_earn", "loop_policy"], cfg
    draw = r["spans"]["draw"]["earned"]
    assert draw["differ"] == [] and draw["added"] == [] and draw["missing"] == []
    assert r["spans"]["replicates"] == [20], r["spans"]["replicates"]
    #: the pass is six trials with the label at trial 1, window 9, and the gain is the earned diagonal less the meter
    assert (r["spans"]["episode"], r["spans"]["label_at"], r["spans"]["window"]) == (6, 1, 9)
    for a in ARMS:
        assert r["reward"][a]["mean"] == r["points"]["here"]["gain"][a], (a, r["reward"][a])
        assert r["points"]["here"]["meter"][a] == -20.0, (a, r["points"]["here"])
    #: the three points are ordered the way the synthetic data was written above and below the knee
    assert r["points"]["learned"]["meter"]["naive"] == -6.0
    assert r["points"]["chance"]["meter"]["naive"] == -42.0
    #: the config and the draw are compared inside the runs, so the artifact carries no top-level `config`
    assert "config" not in r and "env" not in r and "tasks" not in r, sorted(r)
    #: an absent run reads as absent and refuses the claims that need it, rather than raising
    gone = e511.reading(new=tmp_path / "nope.json", meter=tmp_path / "nope.json",
                        learned_earn=tmp_path / "nope.json", learned_meter=tmp_path / "nope.json",
                        chance_earn=tmp_path / "nope.json", chance_meter=tmp_path / "nope.json", beside={})
    assert gone["ok"] and gone["reward"] is None
    assert all(row["verdict"].startswith("REFUSED") for row in e511.judge(gone))


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e511_the_earning_at_the_knee.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e511.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    #: the two runs, the two reference pairs, the payout, the map and the three points are structural
    assert sorted(d["runs"]) == ["earned", "meter"], sorted(d["runs"])
    assert sorted(d["learned"]) == ["earned", "meter"], sorted(d["learned"])
    assert sorted(d["chance"]) == ["earned", "meter"], sorted(d["chance"])
    assert sorted(d["map"]) == ["beside", "earned"], sorted(d["map"])
    assert sorted(d["points"]) == ["chance", "here", "learned"], sorted(d["points"])
    assert (d["spans"]["episode"], d["spans"]["label_at"], d["spans"]["window"]) == (6, 1, 9)
    #: the counts that grow with the corpus are read as bounds, so a longer artifact does not break the test
    assert all(v >= 1 for v in d["spans"]["replicates"]), d["spans"]["replicates"]
    assert d["spans"]["config"]["earned"]["same"] >= 40, d["spans"]["config"]["earned"]["same"]
    assert len(d["spans"]["draw"]["earned"]["agree"]) >= 15, len(d["spans"]["draw"]["earned"]["agree"])
    if d["reward"] is not None:
        assert sorted(d["reward"]) == sorted(ARMS), sorted(d["reward"])
        for a in ARMS:
            assert d["reward"][a]["n"] >= 1, (a, d["reward"][a])
            #: the payout is a negative squared distance, so its cells are at or below zero; whether the earned run's
            #: diagonal is above the meter run's is the claim's business and the judge re-derives the verdict
            assert d["spans"]["reward_diagonal"]["earned"][a] <= 0.0, a
            assert d["spans"]["reward_diagonal"]["meter"][a] <= 0.0, a
            assert 0.0 <= d["spans"]["accuracy_diagonal"]["earned"][a] <= 1.0, a
    mv = d["map"]["earned"]
    if mv is not None:
        for a in ARMS:
            assert mv[a]["replicates"] >= 1, (a, mv[a])
            assert 0 <= mv[a]["above_zero"] <= mv[a]["replicates"], (a, mv[a])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
