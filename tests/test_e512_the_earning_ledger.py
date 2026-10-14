"""`e512` reads every earned-versus-meter cell the corpus holds, so the tests pin the four claims' both faces, the
constants the census and the two orderings are registered with, and the refusal when `runs/` holds no cell.

The falsifier test drives `reading` on synthetic artifacts on disk and then `judge` on the reading, so a claim's
outcome is never asserted as the artifact's shape: what is pinned is that each registered falsifier does fire and that
the four claims read both faces. Counts that grow with the corpus are read as bounds.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e512_the_earning_ledger as e512

ARMS = e512.ARMS
TAU = e512.TAU


def _alt(n: int, mean: float, spread: float) -> list:
    """A paired sample of ``n`` offsets around ``mean``: half above it and half below.

    The spread is what gives the paired contrast a sigma at all -- twenty identical offsets have no scatter, so the
    contrast's own sem is zero and nothing ever resolves at two sigma.
    """
    half = n // 2
    return [mean + spread] * half + [mean - spread] * (n - half)


def _run(path: Path, cfg: dict, draw: dict, level: float, accuracy: float, offsets: list,
         move: float) -> Path:
    """One synthetic run: every arm at one reward level, one accuracy per replicate and one map distance."""
    methods = {}
    for a in ARMS:
        reps = []
        for off in offsets:
            m = [[None] * 3 for _ in range(3)]
            for k in range(3):
                m[k][k] = level
            for j in range(3):
                m[2][j] = level
            reps.append({"learned": [accuracy + off] * 4, "final_per_task": [accuracy + off] * 3,
                         "policy_move": move, "reward_retention": m})
        methods[a] = {"replicates": reps}
    path.write_text(json.dumps({"config": cfg, "env_draw": draw, "methods": methods}), encoding="utf-8")
    return path


def _pair(root: Path, name: str, level: float, accuracy: float, gain: float, n: int = 20,
          spread: float = 0.03, change: float = 0.0, move: float = 4.0, iters: int = 500,
          episode: int = 2, differ: dict | None = None, draw_differ: bool = False,
          pay_earned: bool = True, earn_lr=None) -> None:
    """One earned-versus-meter pair on disk: the meter at ``level`` and the earned run ``gain`` above it.

    The meter's own accuracy is flat across the replicates and the earned run's is ``change`` away from it with the
    spread around it, so the paired accuracy contrast carries a sigma: twenty identical offsets have none.
    """
    label_at = 0
    root.mkdir(parents=True, exist_ok=True)
    cfg = {"loop_reward": True, "loop_policy": False, "loop_earn": False, "loop_episode": episode,
           "loop_label_at": label_at, "loop_earn_lr": earn_lr, "json_out": f"runs/{name}_meter.json",
           "save_theta": None, "iters": iters}
    draw = {"episode_len": episode, "label_at": label_at, "tau": TAU, "n_symbols": 4}
    _run(root / f"{name}_meter.json", cfg, draw, level, accuracy, [0.0] * n, move)
    earned_cfg = dict(cfg, loop_policy=True, loop_earn=True, json_out=f"runs/{name}_earn.json")
    if differ:
        earned_cfg.update(differ)
    earned_draw = dict(draw, **({"label_at": 1} if draw_differ else {}))
    _run(root / f"{name}_earn.json", earned_cfg, earned_draw,
         None if not pay_earned else level + gain, accuracy, _alt(n, change, spread), move)


#: the ledger the four claims are read on: the levels fall, the gains rise with the fall, and two cells carry an
#: accuracy that sits above a nearer cell's -- which is what makes the accuracy ordering fail
GOOD = (("a", -5.0, 0.85, 1.0), ("b", -8.0, 0.82, 1.5), ("c", -9.0, 0.83, 2.0),
        ("d", -20.0, 0.70, 4.0), ("e", -40.0, 0.48, 6.0), ("f", -50.0, 0.49, 8.0))


def _corpus(root: Path, spec) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for i, (name, level, accuracy, gain) in enumerate(spec):
        _pair(root, name, level, accuracy, gain, iters=500 + i, episode=2 + i)
    return root


def _judge(root: Path) -> dict:
    return {row["id"]: row["verdict"] for row in e512.judge(e512.reading(root))}


def test_the_four_claims_read_both_faces(tmp_path):
    #: a ledger whose levels order the gains and whose accuracies do not: every claim's own face
    good = _judge(_corpus(tmp_path / "good", GOOD))
    for cid in ("LA1", "LA2", "LA3", "LA4"):
        assert good[cid].startswith("MET"), (cid, good[cid])

    # LA1: one cell over two artifacts, and a cell under the replicate floor of twenty
    assert _judge(_corpus(tmp_path / "thin", GOOD[:1]))["LA1"].startswith("FALSIFIER")
    thin = tmp_path / "under"
    _pair(thin, "a", -5.0, 0.85, 1.0, n=5)
    assert _judge(thin)["LA1"].startswith("FALSIFIER")

    # LA2: the closest meter carrying the largest gain, which inverts every arm
    inverted = tuple((name, level, accuracy, 9.0 - gain) for name, level, accuracy, gain in GOOD)
    fired2 = _judge(_corpus(tmp_path / "inverted", inverted))
    assert fired2["LA2"].startswith("FALSIFIER"), fired2["LA2"]

    # LA3: the gains rising with the accuracy, which orders every arm
    rising = (("a", -5.0, 0.90, 1.0), ("b", -8.0, 0.86, 2.0), ("c", -9.0, 0.82, 3.0),
              ("d", -20.0, 0.78, 4.0), ("e", -40.0, 0.75, 5.0), ("f", -50.0, 0.70, 6.0))
    fired3 = _judge(_corpus(tmp_path / "rising", rising))
    assert fired3["LA3"].startswith("FALSIFIER"), fired3["LA3"]

    # LA4: one arm's accuracy contrast moving at two sigma
    moving = tmp_path / "moving"
    _corpus(moving, GOOD)
    _pair(moving, "g", -60.0, 0.45, 9.0, change=0.05, spread=0.01, iters=900)
    assert _judge(moving)["LA4"].startswith("FALSIFIER")

    #: a corpus that could not be read at all, and a corpus with no cell, refuse every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e512.judge({"ok": False, "reason": "absent"}))
    empty = _judge(tmp_path / "empty")
    assert all(v.startswith("REFUSED") for v in empty.values()), empty


def test_the_census_rule_admits_what_it_says_and_leaves_out_the_rest(tmp_path):
    root = tmp_path / "census"
    root.mkdir()
    #: a pair two flags apart is a cell, and the ascent rate the earned run alone moves is one of the exempt fields
    _pair(root, "plain", -5.0, 0.8, 1.0, earn_lr=0.01, episode=2)
    #: a second field differing past the rule is not a cell -- `iters` is neither flag, path nor saved weights
    _pair(root, "otherpass", -6.0, 0.8, 1.0, differ={"iters": 900}, episode=3)
    #: a pair that draws differently is not a cell
    _pair(root, "otherdraw", -7.0, 0.8, 1.0, draw_differ=True, episode=4)
    #: an arm with no reward matrix on a side is not a cell
    _pair(root, "unpaid", -8.0, 0.8, 1.0, pay_earned=False, episode=5)
    #: a run with `loop_policy` alone is neither the meter nor the earning side
    (root / "e999_policy_only.json").write_text(json.dumps({
        "config": {"loop_reward": True, "loop_policy": True, "loop_earn": False, "loop_episode": 7,
                   "json_out": "policy"},
        "env_draw": {"episode_len": 7}, "methods": {a: {"replicates": []} for a in ARMS}}), encoding="utf-8")
    #: a meter whose own pass carries no earned run
    (root / "e999_lonely_meter.json").write_text(json.dumps({
        "config": {"loop_reward": True, "loop_policy": False, "loop_earn": False, "loop_episode": 8,
                   "json_out": "lonely"},
        "env_draw": {"episode_len": 8}, "methods": {a: {"replicates": []} for a in ARMS}}), encoding="utf-8")

    r = e512.reading(root)
    assert [c["artifact"] for c in r["cells"]] == ["plain_earn.json"], [c["artifact"] for c in r["cells"]]
    left = {row["artifact"]: row["why"] for row in r["left_out"]}
    assert left["e999_policy_only.json"] == ("carries the payout or a flag but not the paid pair of flags, so it is "
                                            "neither the meter nor the earning side of a cell")
    assert left["e999_lonely_meter.json"].startswith("a meter run with no earned run")
    #: the attempts that are not cells are counted by reason, so a reader can see what was dropped
    assert r["attempts"] == len(r["candidates"]["meters"]) * len(r["candidates"]["earned"])
    assert set(r["rejected"]) <= {"config", "draw", "no payout on an arm"}, sorted(r["rejected"])
    assert "otherpass_earn.json" in {row["earned"] for row in r["rejected"]["config"]}
    assert "otherdraw_earn.json" in {row["earned"] for row in r["rejected"]["draw"]}
    assert "unpaid_earn.json" in {row["earned"] for row in r["rejected"]["no payout on an arm"]}
    #: every cell's own cell-arms carry the two run's levels and the contrast between them
    cell = r["cells"][0]
    for a in ARMS:
        arm = cell["arms"][a]
        assert abs(arm["gain"] - (arm["earned_level"] - arm["meter_level"])) < 1e-9, a
        assert abs(cell["naive_accuracy"] - cell["arms"]["naive"]["accuracy"]) < 1e-12


def test_the_census_and_the_orderings_are_registered():
    #: the glob's root, the arms, the tau the window is read from, and the exempt fields a pair may differ in
    assert e512.ROOT == Path("runs") and e512.ARMS == ("naive", "ewc-block", "replay") and e512.TAU == 12
    assert e512.EXEMPT == ("loop_policy", "loop_earn", "loop_earn_lr", "json_out", "save_theta")
    assert e512.PAID == ("loop_policy", "loop_earn") and e512.REWARD == "loop_reward"
    #: the census's floor, the replicate floor, the tolerance and the resolution bar
    assert (e512.MIN_CELLS, e512.MIN_ARTIFACTS, e512.MIN_REPS) == (5, 4, 20)
    assert e512.TOL == 0.25 and (e512.SIGMA, e512.ARMS_NEEDED) == (2.0, 2)
    #: the inert rule: the fields a pair may move are free, and a flag added later reads null beside false
    assert all(e512._inert(k, None, False) for k in e512.EXEMPT)
    assert e512._inert("loop_reward_on_action", None, False)
    assert not e512._inert("iters", 500, 900)
    #: the pass's own window, the formula the ladder is pooled by
    assert e512._pass({"loop_episode": 2, "loop_label_first": True})["window"] == 11
    assert e512._pass({"loop_episode": 6, "loop_label_at": 1})["window"] == 9
    assert e512._pass({})["window"] == TAU - 1 and e512._pass({})["one_trial"]
    #: and the four claims are registered with their falsifiers
    assert [c[0] for c in e512.CLAIMS] == ["LA1", "LA2", "LA3", "LA4"]
    assert all(c[3].startswith("falsifier") for c in e512.CLAIMS)


def test_the_live_ledger_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e512_the_earning_ledger.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e512.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the census is a bound that grows with the corpus, not a frozen count
    assert len(d["cells"]) >= e512.MIN_CELLS and len(d["artifacts"]) >= e512.MIN_ARTIFACTS, (len(d["cells"]),
                                                                                              len(d["artifacts"]))
    #: every cell carries a replicate count per arm, and the counted keys stay out of the payload
    assert all(c["replicates"] for c in d["cells"])
    assert all(set(c["arms"]) == set(e512.ARMS) for c in d["cells"])
    #: every cell's two sides are one meter and one earned run of the same pass, and the contrast is their difference
    for c in d["cells"]:
        assert c["meter"] != c["artifact"]
        assert sorted(c["pairing"]["moved"]) == sorted(e512.PAID)
        for a in e512.ARMS:
            arm = c["arms"][a]
            assert abs(arm["gain"] - (arm["earned_level"] - arm["meter_level"])) < 1e-9, (c["artifact"], a)
        assert c["naive_accuracy"] == c["arms"]["naive"]["accuracy"]
    #: the two orderings are read per arm, and every inversion is a separated pair of the ledger's own cells
    names = {c["artifact"] for c in d["cells"]}
    for key in ("by_level", "by_accuracy"):
        assert sorted(d["orderings"][key]) == sorted(e512.ARMS)
        for a in e512.ARMS:
            o = d["orderings"][key][a]
            assert set(o["sequence"]) <= names and len(o["sequence"]) == len(d["cells"])
            for inv in o["inversions"]:
                assert inv["closer"] in names and inv["further"] in names and inv["gain"][0] > inv["gain"][1]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
