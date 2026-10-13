"""`e507` puts the world's payout on a pass the head cannot learn, so the tests pin the three claims' both faces, the
constants they are registered with, the pipeline that builds the band, and the refusal when an input is absent.

The falsifier test drives `reading` on synthetic artifacts on disk and then `judge` on the reading, so a claim's
outcome is never asserted as the artifact's shape: what is pinned is that each registered falsifier does fire and that
the three claims read both faces. Counts that grow with the corpus are read as bounds.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e507_the_world_pays_at_a_chance_pass as e507

ARMS = e507.ARMS
KEYS = [k for k, _, _ in e507.PLACEMENTS]


def _diffs(mean: float, e: float, n: int = 20) -> list:
    """A paired sample of ``n`` differences with mean ``mean``: ten at ``mean + e`` and ten at ``mean - e``."""
    return [mean + e] * (n // 2) + [mean - e] * (n - n // 2)


def _run(path, cfg, draw, acc, reward, move, n=20):
    methods = {}
    for a in ARMS:
        reps = []
        for i in range(n):
            rep = {"learned": [acc[a]] * 4, "final_per_task": [acc[a]] * 3}
            if reward is None:
                rep["reward_retention"] = [[None] * 3 for _ in range(3)]
            else:
                d = reward[a][i]
                m = [[None] * 3 for _ in range(3)]
                for k in range(3):
                    m[k][k] = d
                for j in range(3):
                    m[2][j] = d
                rep["reward_retention"] = m
            rep["policy_move"] = None if move is None else move[a][i]
            reps.append(rep)
        methods[a] = {"replicates": reps}
    path.write_text(json.dumps({"config": cfg, "env_draw": draw, "methods": methods}), encoding="utf-8")
    return path


def _cfg(earn=True, **kw):
    base = {"loop_policy": earn, "loop_earn": earn, "loop_episode": 3, "loop_label_at": 1,
            "json_out": "earn" if earn else "meter", "save_theta": None, "iters": 500}
    base.update(kw)
    return base


def _reward(mean: float, e: float, level: float = -6.2, n: int = 20):
    return {a: [level + d for d in _diffs(mean, e, n)] for a in ARMS}


def _const(level: float, n: int = 20):
    return {a: [level] * n for a in ARMS}


def _move(level: float, n: int = 20):
    return {a: [level] * n for a in ARMS}


def _docs(tmp_path, earn_cfg=None, meter_cfg=None, earn_draw=None, meter_draw=None,
          earn_acc=0.3100, meter_acc=0.3100, earn_gain=1.30, meter_level=-6.2,
          ref_gain=1.30, ref_meter_level=-6.0, ref_earn_acc=0.83, n=20, move=5.0,
          place_acc=0.3257):
    draw = {"episode_len": 3, "label_at": 1, "cue_sha1": "a"}
    paths = {
        "new": _run(tmp_path / "new.json", _cfg(True) if earn_cfg is None else earn_cfg,
                    draw if earn_draw is None else earn_draw,
                    {a: earn_acc for a in ARMS}, _reward(earn_gain, 0.2, meter_level, n), _move(move, n), n),
        "meter": _run(tmp_path / "meter.json", _cfg(False) if meter_cfg is None else meter_cfg,
                      draw if meter_draw is None else meter_draw,
                      {a: meter_acc for a in ARMS}, _const(meter_level, n), _move(move, n), n),
        "ref_earn": _run(tmp_path / "ref_earn.json", _cfg(True), draw,
                         {a: ref_earn_acc for a in ARMS}, _reward(ref_gain, 0.15, ref_meter_level, n),
                         _move(5.5, n), n),
        "ref_meter": _run(tmp_path / "ref_meter.json", _cfg(False), draw,
                          {a: ref_earn_acc for a in ARMS}, _const(ref_meter_level, n), _move(5.5, n), n),
    }
    for k, at in (("at1", 1), ("at2", 2)):
        paths[k] = _run(tmp_path / f"{k}.json", {"json_out": k}, dict(draw, label_at=at),
                        {a: place_acc for a in ARMS}, None, None, n)
    return paths


def _read(tmp_path, **kw):
    p = _docs(tmp_path, **kw)
    return e507.reading(new=p["new"], meter=p["meter"], ref_earn=p["ref_earn"], ref_meter=p["ref_meter"],
                        beside={}, placements=tuple((k, at, p[k]) for k, at, _ in e507.PLACEMENTS))


def _judge(r):
    return {row["id"]: row["verdict"] for row in e507.judge(r)}


def test_the_three_claims_read_both_faces(tmp_path):
    j = _judge(_read(tmp_path))
    for cid in ("XA1", "XA2", "XA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # XA1: another config field differing, the flags not both moved, a draw field differing, added or missing, a thin
    # run
    assert _judge(_read(tmp_path, earn_cfg=_cfg(True, iters=100)))["XA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_cfg=_cfg(True, loop_earn=False)))["XA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_draw={"episode_len": 3, "label_at": 1, "cue_sha1": "b"})
                  )["XA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_draw={"episode_len": 3, "label_at": 1}))["XA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_draw={"episode_len": 3, "label_at": 1, "cue_sha1": "a", "extra": 1})
                  )["XA1"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, n=19))["XA1"].startswith("FALSIFIER")

    # XA2: a replicate whose map distance is not positive, a run that records no movement, a contrast that does not
    # resolve, and one that is negative
    assert _judge(_read(tmp_path, move=0.0))["XA2"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_gain=-1.30))["XA2"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_gain=0.05))["XA2"].startswith("FALSIFIER")

    # XA3: a gain outside the band -- the new gain runs to 0.10 where e500's own is 1.30 -- and an accuracy above the
    # bar of 0.10 over the chance of 0.25
    assert _judge(_read(tmp_path, earn_gain=0.10))["XA3"].startswith("FALSIFIER")
    assert _judge(_read(tmp_path, earn_acc=0.45, meter_acc=0.45))["XA3"].startswith("FALSIFIER")

    #: each claim refuses on its own absent input
    p = _docs(tmp_path)
    gone = e507.reading(new=tmp_path / "nope.json", meter=p["meter"], ref_earn=p["ref_earn"],
                        ref_meter=p["ref_meter"], beside={})
    v = _judge(gone)
    assert v["XA1"].startswith("REFUSED") and v["XA2"].startswith("REFUSED")
    #: with no reading at all every claim refuses
    assert all(row["verdict"].startswith("REFUSED") for row in e507.judge({"ok": False, "reason": "no run"}))


def test_the_runs_the_band_and_the_pass_are_registered():
    assert e507.NEW.name == "e507_label_at1_episode3_reward_earn_20reps.json"
    assert e507.METER.name == "e507_label_at1_episode3_reward_20reps.json"
    assert e507.REF_EARN.name == "e500_earned_label_episode2_labelfirst_reward_earn_20reps.json"
    assert e507.REF_METER.name == "e498_earned_label_episode2_labelfirst_reward_20reps.json"
    assert set(e507.MOVED) == {"loop_policy", "loop_earn"}, e507.MOVED
    assert set(e507.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e507.EPISODE, e507.TAU, e507.SIZE, e507.READOUT_SIZE) == (3, 12, 300, 32)
    assert (e507.LABEL_AT, e507.WINDOW) == (1, 7), (e507.LABEL_AT, e507.WINDOW)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e507.MIN_REPS, e507.SIGMA, e507.CHANCE, e507.BAR, e507.ARMS_NEEDED) == (20, 2.0, 0.25, 0.10, 2)
    assert e507._inert("loop_policy", False, True) and e507._inert("loop_earn", False, True)
    assert e507._inert("json_out", "a", "b")
    assert not e507._inert("iters", 500, 100)
    #: the three claims are registered with their falsifiers beside them, before the reading was opened
    assert [c[0] for c in e507.CLAIMS] == ["XA1", "XA2", "XA3"]
    assert all("falsifier:" in c[3] for c in e507.CLAIMS)


def test_the_reading_builds_the_band_and_the_placements_from_artifacts(tmp_path):
    r = _read(tmp_path)
    assert r["ok"] and r["reward"] is not None and r["band"] is not None and r["ref"] is not None
    #: the pair is one flag apart and the draw moves nothing
    cfg = r["spans"]["config"]["earned"]
    assert cfg["differ"] == {}, cfg
    assert sorted(cfg["inert"]) == ["json_out", "loop_earn", "loop_policy"], cfg
    draw = r["spans"]["draw"]["earned"]
    assert draw["differ"] == [] and draw["added"] == [] and draw["missing"] == []
    assert r["spans"]["replicates"] == [20], r["spans"]["replicates"]
    #: the band's half-width is the larger of the two comparisons' own spreads, and the gain is read inside it
    for a in ARMS:
        b = r["band"][a]
        assert b["width"] == max(r["ref"][a]["sd"], r["reward"][a]["sd"]), b
        assert b["inside"] is True, b
    #: the pass is three trials with the label at trial 1, window 7, and `e505`'s placements sit beside it
    assert r["spans"]["window"] == 7 and r["spans"]["label_at"] == 1
    assert r["spans"]["placement"]["at1"]["window"] == 7 and r["spans"]["placement"]["at2"]["window"] == 3
    assert r["spans"]["placement"]["at1"]["accuracy_diagonal"]["naive"] == 0.3257
    #: the config and the draw are compared inside the runs, so the artifact carries no top-level `config`
    assert "config" not in r and "env" not in r and "tasks" not in r, sorted(r)
    #: an absent run reads as absent and refuses the claims that need it, rather than raising
    gone = e507.reading(new=tmp_path / "nope.json", meter=tmp_path / "nope.json", ref_earn=tmp_path / "nope.json",
                        ref_meter=tmp_path / "nope.json", beside={})
    assert gone["ok"] and gone["reward"] is None and gone["band"] is None
    assert all(row["verdict"].startswith("REFUSED") for row in e507.judge(gone))


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e507_the_world_pays_at_a_chance_pass.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e507.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    #: the two runs, the payout, the map and the band are structural
    assert sorted(d["runs"]) == ["earned", "meter"], sorted(d["runs"])
    assert sorted(d["map"]) == ["beside", "earned"], sorted(d["map"])
    assert d["spans"]["window"] == 7 and d["spans"]["label_at"] == 1
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
