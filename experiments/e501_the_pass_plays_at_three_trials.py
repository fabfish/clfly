"""E501 -- the pass plays at three trials: whether the earning `e500` measured survives the pass's second rung.

`e500` ran the paid, label-first, **two-trial** episodic pass with `--loop-policy --loop-earn` and found the world's
payout **reaches the map** -- **+1.07** to **+1.51** more on every arm at **+15.5** to **+22.7** sigma -- while the
pass's own accuracy is unchanged. Its *cannot do* is **one episode length and one placement**: two trials of six steps
with the label first, and it names the **three- and four-trial splits** as not in it. `e497` and the card's revision 19
then showed the label-first pass is a **family** and that three trials of four steps reads **higher** than two.
**What neither measured is whether the earning survives that pass.**

**This unit pays the three-trial pass.** One run: `e500`'s own configuration with **`--loop-episode 3`** -- one world,
one pass, one read, one label-first placement and one payout, the map the agent acts through taken out of the body's
optimizer and trained by ascent on the world's payout -- read against its **meter** run, the same configuration without
`--loop-policy --loop-earn`. Both are two artifacts on disk; this unit reads them and trains nothing.

Three claims, registered before the reading of either artifact was opened.

- **RA1 -- and the pair at three trials is two flags apart and the pass is the three-trial one.** Against the meter
  run every recorded `config` field agrees except `loop_policy`, `loop_earn`, the output path and the saved weights;
  the environment's draw agrees on every field, with none added and none missing; both runs carry **twenty**
  replicates; and the pass is the three-trial one, `loop_episode` **3** and `episode_len` **3**. **Falsifier**: any
  other config field differing, a draw field differing or added or missing, a replicate count other than twenty, or an
  episode length other than three.
- **RA2 -- and the payout reaches the map at three trials.** The map ends **above the identity on every replicate** --
  a positive distance, in the sense `e500` measures it -- and the earned run's **reward diagonal** is above the meter
  run's on **at least two of the three arms** at **two** sigma. **Falsifier**: a replicate whose map distance is not
  positive, or fewer than two arms resolving upward. *It can fire: the earning is measured against a meter run of the
  same configuration, and a longer pass has more steps for the map to move through, so whether the ascent still lifts
  the level at three trials is this claim.*
- **RA3 -- and the pass is still learned while the map is paid.** On **at least two of the three arms** the accuracy
  diagonal is at least **0.10** above the four-class chance of **0.25** and within **0.10** of the meter run's own
  diagonal on that arm. **Falsifier**: fewer than two arms over the bar, or an arm more than **0.10** under the meter
  run's. *It can fire: `e488` found the paid map's accuracy **below** the task-loss map's on every arm, by **0.0285**
  to **0.0410**, so a paid map inside a longer episode can cost the pass.*

**What it can do beyond that.** It takes the earning `e500` measured at the pass's first rung to the rung `e497` and
the card's revision 19 measured the pass at, so the pair the pass's own *cannot do* leaves open -- a payout played for
at three trials -- is read against a meter run of the same configuration. Read with `e500` it is the other length of
the same question: there the map was paid inside a two-trial episode whose target follows the label, here inside a
three-trial one. It carries, as extra readings rather than claims, each run's reward diagonal beside its own last row
(the shape `e500` and `e488` found) and the map's distance beside `e500`'s two-trial figure.

**What it cannot do.** *One payout shape*: the environment's own linear read of the cue, so a second payout shape is a
different unit. *And the payout is on the map and not on the world's carry*: what is ascended is the world's own
currency and not the episode's carried state, so what the earning does to what the world carries is not in the unit.
*And two rungs and not a sweep*: three trials against the two `e500` ran, so the **four- and six-trial splits** and
the passes with the label at an **interior trial** are not in it. *And one world, one budget, one learning rate and one
seed stream*: the card's own setting, with the map's ascent at the run's own `--lr`. *And three arms is a small
population*: a claim over arms is not a claim about the world.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489
from experiments.e172_parser_registry import parser_flags

#: the three-trial earned run and its own meter run, then `e500`'s own two-trial earn run, where the map's distance
#: from the identity was measured at the rung below
NEW = Path("runs/e501_earned_label_episode3_labelfirst_reward_earn_20reps.json")
METER = Path("runs/e501_earned_label_episode3_labelfirst_reward_20reps.json")
TWO = Path("runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the two fields the pair moves, and the run's own bookkeeping
MOVED = ("loop_policy", "loop_earn")
BOOKKEEPING = ("json_out", "save_theta")
#: the pass this unit reads: `e500`'s own configuration with `--loop-episode 3`
EPISODE = 3
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
#: the bar an arm's accuracy has to clear over chance, and how far under the meter run's it may sit
BAR = 0.10
TOL = 0.10
ARMS_NEEDED = 2
PLACES = 4
CLAIMS = (
    ("RA1", "and the pair at three trials is two flags apart and the pass is the three-trial one",
     "Against the meter run every recorded config field agrees except loop_policy, loop_earn, the output path and the "
     "saved weights, the environment's draw agrees on every field with none added and none missing, both runs carry "
     "twenty replicates, and the pass is the three-trial one with loop_episode 3 and episode_len 3",
     "falsifier: any other config field differing, a draw field differing or added or missing, a replicate count other "
     "than twenty, or an episode length other than three"),
    ("RA2", f"and the payout reaches the map at three trials, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "The map ends above the identity on every replicate, a positive distance in the sense e500 measures it, and the "
     "earned run's reward diagonal is above the meter run's on at least two of the three arms at two sigma",
     "falsifier: a replicate whose map distance is not positive, or fewer than two arms resolving upward"),
    ("RA3", f"and the pass is still learned while the map is paid, on {ARMS_NEEDED} arms",
     "On at least two of the three arms the accuracy diagonal is at least 0.10 above the four-class chance of 0.25 and "
     "within 0.10 of the meter run's own diagonal on that arm",
     "falsifier: fewer than two arms over the bar, or an arm more than 0.10 under the meter run's"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return old is None and key in DEFAULTS and new == DEFAULTS[key]


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    """One run's per-arm reading: both currencies' diagonals and last rows, the map's movement, config and draw.

    A run without the payout records the reward field with a matrix of `None`s, so the cell's presence is not the
    payout's: what is checked is the matrix's own corner. A run without the policy records `policy_move` as `None`.
    """
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        entry = {"replicates": len(reps),
                 "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                 "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps],
                 "policy_move": [None if r.get("policy_move") is None else float(r["policy_move"]) for r in reps]}
        rw = [r.get("reward_retention") for r in reps]
        if any(x is None or x[0][0] is None for x in rw):
            entry["reward_diagonal"] = None
            entry["reward_last"] = None
        else:
            entry["reward_diagonal"] = [statistics.fmean([x[k][k] for k in range(3)]) for x in rw]
            entry["reward_last"] = [statistics.fmean([x[2][j] for j in range(3)]) for x in rw]
        got[arm] = entry
    return {"artifact": path.name, "arms": got, "config": doc.get("config") or {},
            "env_draw": doc.get("env_draw") or {}}


def _against(mine: dict, theirs: dict) -> dict:
    """One run's config and draw against another's, the inert rule applied to the config."""
    cfg, other_cfg = mine["config"], theirs["config"]
    same, inert, differ = {}, {}, {}
    for k in sorted(set(cfg) | set(other_cfg)):
        old, new = other_cfg.get(k), cfg.get(k)
        if old == new:
            same[k] = new
        elif _inert(k, old, new):
            inert[k] = [old, new]
        else:
            differ[k] = [old, new]
    agree = {k: theirs["env_draw"].get(k) == mine["env_draw"].get(k) for k in theirs["env_draw"]}
    return {"same": len(same), "inert": sorted(inert), "differ": differ,
            "moved": {k: cfg.get(k) for k in MOVED},
            "draw": {"agree": agree, "differ": sorted(k for k, ok in agree.items() if not ok),
                     "added": sorted(set(mine["env_draw"]) - set(theirs["env_draw"])),
                     "missing": sorted(set(theirs["env_draw"]) - set(mine["env_draw"]))}}


def _map(roll: dict | None) -> dict | None:
    """The map's distance from the identity, per arm, or `None` where the run records no movement."""
    if roll is None:
        return None
    out = {}
    for arm in ARMS:
        moves = roll["arms"][arm]["policy_move"]
        if not moves or any(m is None for m in moves):
            return None
        out[arm] = {"replicates": len(moves), "above_zero": sum(1 for m in moves if m > 0.0),
                    "smallest": min(moves), "mean": statistics.fmean(moves)}
    return out


def _reward_missing(roll: dict) -> bool:
    return any(roll["arms"][a]["reward_diagonal"] is None for a in ARMS)


def reading(new: Path = NEW, meter: Path = METER, two: Path = TWO) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "map": {}, "reward": {}, "accuracy": {}, "shape": {},
           "spans": {}}
    got = {"earned": _roll(new), "meter": _roll(meter)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"the {label} run is absent, or carries no replicate to read"}
    if _reward_missing(got["earned"]) or _reward_missing(got["meter"]):
        return {**out, "ok": False, "reason": "a run carries no reward matrix, so the payout's two levels are not "
                                             "readable"}
    out["runs"] = got
    against = {"earned": _against(got["earned"], got["meter"]), "meter": _against(got["meter"], got["meter"])}
    out["map"] = {"earned": _map(got["earned"]), "two_trial": _map(_roll(two))}
    out["reward"] = {a: _paired(got["earned"]["arms"][a]["reward_diagonal"],
                                got["meter"]["arms"][a]["reward_diagonal"]) for a in ARMS}
    out["accuracy"] = {a: _paired(got["earned"]["arms"][a]["accuracy_diagonal"],
                                  got["meter"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    #: an extra reading rather than a claim: each run's reward diagonal against **its own** last row
    out["shape"] = {label: {a: _paired(got[label]["arms"][a]["reward_diagonal"],
                                       got[label]["arms"][a]["reward_last"]) for a in ARMS} for label in got}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "episode": EPISODE, "chance": CHANCE,
        "bar": BAR, "tol": TOL, "sigma": SIGMA, "arms_needed": ARMS_NEEDED,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "loop_episode": {label: got[label]["config"].get("loop_episode") for label in got},
        "episode_len": {label: got[label]["env_draw"].get("episode_len") for label in got},
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "config": against,
        "draw": {label: against[label]["draw"] for label in against},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), PLACES)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), PLACES)
                                  for a in ARMS} for label in got},
        "reward_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["reward_diagonal"]), PLACES)
                                    for a in ARMS} for label in got},
        "reward_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["reward_last"]), PLACES)
                                for a in ARMS} for label in got},
        "reward_shape": {label: {a: {"mean": round(out["shape"][label][a]["mean"], PLACES),
                                     "sigma": round(out["shape"][label][a]["sigma"], 2)} for a in ARMS}
                         for label in got},
        "map_move": {"earned": (None if out["map"]["earned"] is None else
                                {a: {"mean": round(out["map"]["earned"][a]["mean"], PLACES),
                                     "smallest": round(out["map"]["earned"][a]["smallest"], PLACES)}
                                 for a in ARMS}),
                     "two_trial": (None if out["map"]["two_trial"] is None else
                                   {a: {"mean": round(out["map"]["two_trial"][a]["mean"], PLACES)}
                                    for a in ARMS})},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    cfg = s["config"]["earned"]
    draw = s["draw"]["earned"]
    moved = cfg["moved"]
    mine_moved = {k: moved.get(k) for k in MOVED}
    theirs_moved = {k: s["config"]["meter"]["moved"].get(k) for k in MOVED}
    moved_ok = all(mine_moved[k] is True for k in MOVED) and all(theirs_moved[k] in (None, False) for k in MOVED)
    draw_ok = not draw["added"] and not draw["differ"] and not draw["missing"]
    ep = s["loop_episode"]
    elen = s["episode_len"]
    ep_ok = all(ep.get(label) == EPISODE and elen.get(label) == EPISODE for label in ("earned", "meter"))
    j1 = {"id": "RA1",
          "measured": f"the config: **{len(cfg['differ'])}** differing past the inert rule ({cfg['differ']}) over "
                      f"**{cfg['same'] + len(cfg['inert'])}** fields, the fields moved {mine_moved} against the meter "
                      f"run's {theirs_moved}; the draw: **{len(draw['agree'])}** fields with **{len(draw['differ'])}** "
                      f"differing, **{len(draw['added'])}** added and **{len(draw['missing'])}** missing; the pass is "
                      f"`loop_episode` **{ep}** and `episode_len` **{elen}**; replicates {s['replicates']}",
          "verdict": "MET -- the paid three-trial pass runs with the map earned, two flags from the meter run over "
                     "one world and one payout" if (not cfg["differ"] and moved_ok and draw_ok
                                                     and s["replicates"] == [MIN_REPS] and ep_ok) else
                     f"FALSIFIER FIRED -- differing {cfg['differ']}, moved {mine_moved} against {theirs_moved}, draw "
                     f"{draw}, the pass {ep}/{elen}, replicates {s['replicates']}"}
    mv = r["map"]["earned"]
    two = (s.get("map_move") or {}).get("two_trial")
    thin = ([] if mv is None else
            [a for a in ARMS if mv[a]["above_zero"] != mv[a]["replicates"] or mv[a]["smallest"] <= 0.0])
    up = [a for a in ARMS if r["reward"][a]["mean"] > 0.0 and r["reward"][a]["sigma"] >= SIGMA]
    j2 = {"id": "RA2",
          "measured": (f"the map's distance from the identity is **{mv}** on the new run"
                       + ("" if two is None else f", beside `e500`'s own two-trial **{two}**")
                       + f"; the reward's diagonal less the meter run's, paired over the replicates: "
                         f"**{ {a: round(r['reward'][a]['mean'], PLACES) for a in ARMS} }** at "
                         f"**{ {a: round(r['reward'][a]['sigma'], 2) for a in ARMS} }** sigma, from "
                         f"**{s['reward_diagonal']['earned']}** against **{s['reward_diagonal']['meter']}**"
                       if mv is not None else "the new run records no policy movement on any replicate"),
          "verdict": f"MET -- the payout reaches the map on every replicate and lifts the reward's diagonal above the "
                     f"meter run's on **{len(up)}** of three arms ({up}) at {SIGMA:.0f} sigma"
                     if (mv is not None and not thin and len(up) >= ARMS_NEEDED) else
                     f"FALSIFIER FIRED -- thin {thin}, {len(up)} of three arms lifting at {SIGMA:.0f} sigma ({up}), "
                     f"moved {mv is not None}"}
    diag = s["accuracy_diagonal"]
    under = [a for a in ARMS if diag["earned"][a] < diag["meter"][a] - TOL]
    over = [a for a in ARMS if diag["earned"][a] >= CHANCE + BAR]
    j3 = {"id": "RA3",
          "measured": f"the new run's accuracy diagonals **{diag['earned']}** against the meter run's "
                      f"**{diag['meter']}**, **{len(over)}** of three arms at least {BAR:.2f} above the chance of "
                      f"{CHANCE:.2f} and **{len(under)}** more than {TOL:.2f} under the meter run's ({under}), for "
                      f"changes of **{ {a: round(r['accuracy'][a]['mean'], PLACES) for a in ARMS} }** at "
                      f"**{ {a: round(r['accuracy'][a]['sigma'], 2) for a in ARMS} }** sigma",
          "verdict": f"MET -- the pass is still learned with the map paid: **{len(over)}** of three arms over the bar "
                     f"({over}) and none more than {TOL:.2f} under the meter run's"
                     if (len(over) >= ARMS_NEEDED and not under) else
                     f"FALSIFIER FIRED -- {len(over)} of three arms over the bar ({over}), under the meter run's by "
                     f"more than {TOL:.2f}: {under}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the pass plays at three trials ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e500` paid the two-trial, label-first episode and the world's payout reached the map; this is the same")
    print(f"   pass at the three-trial rung `e497` and the card's revision 19 measured, against its own meter run")
    two = (r["spans"].get("map_move") or {}).get("two_trial")
    print(f"\n   {'arm':<10} {'reward earn':>12} {'reward meter':>13} {'payout gain':>12} {'sigma':>7} "
          f"{'acc earn':>9} {'acc meter':>10} {'d acc':>8} {'map move':>9} {'e500 2tr':>9}")
    for a in ARMS:
        g, c = r["reward"][a], r["accuracy"][a]
        moved = (0.0 if r["map"]["earned"] is None else r["map"]["earned"][a]["mean"])
        base = (0.0 if two is None else two[a]["mean"])
        print(f"   {a:<10} {r['spans']['reward_diagonal']['earned'][a]:>12.4f} "
              f"{r['spans']['reward_diagonal']['meter'][a]:>13.4f} {g['mean']:>+12.4f} {g['sigma']:>7.2f} "
              f"{r['spans']['accuracy_diagonal']['earned'][a]:>9.4f} "
              f"{r['spans']['accuracy_diagonal']['meter'][a]:>10.4f} {c['mean']:>+8.4f} {moved:>9.4f} "
              f"{base:>9.4f}")
    cfg, draw = r["spans"]["config"]["earned"], r["spans"]["draw"]["earned"]
    print(f"\n   the config: {len(cfg['differ'])} differing past the inert rule {cfg['differ']}; "
          f"the fields moved {cfg['moved']}")
    print(f"   the draw: {len(draw['agree'])} fields with {len(draw['differ'])} differing, {len(draw['added'])} added "
          f"and {len(draw['missing'])} missing; the pass `loop_episode` {r['spans']['loop_episode']} and "
          f"`episode_len` {r['spans']['episode_len']}")
    print(f"   the reward's own shape, diagonal less last row: earned "
          f"{ {a: round(r['shape']['earned'][a]['mean'], 4) for a in ARMS} } against meter "
          f"{ {a: round(r['shape']['meter'][a]['mean'], 4) for a in ARMS} }")
    print("\n== the registered claims, RA1-RA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e500` earned at two trials inside the pass; this is the earning at the rung above it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
