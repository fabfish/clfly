"""E502 -- the world pays the action: whether the payout read on the agent's own action moves the agent.

`e500` and `e501` ran the paid, label-first episodic pass with the map the agent acts through taken out of the body's
optimizer and trained by ascent on the world's payout, at two and three trials, and the world paid **+1.07** to
**+1.51** more on every arm. In both the payout is a **state-matching** currency: the cue sets a target one step
after it arrives and the trial's reward is `-||w_final - target||^2`, where `w` is the world's **carried** state -- a
leaky integral of the whole action history. That is what `e500`'s own *cannot do* names as a different unit: *"the
payout is read on the map and not on the action ... a reward on the action, or one sparse in time, is a different
unit."*

**This unit reads the payout on the action.** `CueActionEnv` gains **`reward_on_action`**, a rule and not a draw:
off is the carried state every artifact holds, on is the world's **one-step response to the action** -- the `drive`
the step already hands the world before the carry -- scored against the same target at the same step. The runner
gains **`--loop-reward-on-action`**, recorded in the run's `config` as `loop_reward_on_action`, consuming nothing
from the generator.

Two runs: `e500`'s own two-trial, label-first, paid command with `--loop-reward-on-action` added, the **meter** run
and the same plus `--loop-policy --loop-earn`, the **earned** run. Both are artifacts on disk; this unit trains
nothing. Three claims, registered before the reading of either run was opened.

- **TA1 -- and the new flag moves the payout and nothing else.** Against `e500`'s own earned run every recorded
  `config` field agrees except `loop_reward_on_action`, the output path and the saved weights; the environment's draw
  agrees on **every** field with none added, none missing and none differing; and the run carries **twenty**
  replicates. **Falsifier**: any other config field differing, any draw field added, missing or differing, or a
  replicate count other than twenty.
- **TA2 -- and the action's currency is alive.** The earned run's reward diagonal is above its own meter run's on at
  least **two of the three** arms at **two** sigma, and the map ends above the identity on **every** replicate.
  **Falsifier**: fewer than two arms resolving upward, or a replicate whose map distance is not positive.
- **TA3 -- and the pass is still learned.** On at least **two of the three** arms the accuracy diagonal is at least
  **0.10** above the four-class chance of **0.25** and within **0.10** of the meter run's own. **Falsifier**: fewer
  than two arms over the bar, or an arm more than **0.10** under the meter run's.

Beyond the claims it carries, as extra readings rather than claims, each run's reward diagonal against its own last
row -- the shape `e488`, `e500` and `e501` found -- and the earned run's reward level beside `e500`'s carried-state
run.

**What it can do.** It closes the hole both earlier units left open: the currency was read on the world's carry and
never on the agent's action, so this is the same pass, world, read, placement and target with the payout read on what
the action did rather than on what the world has become.

**What it cannot do.** *One episode length and one placement*: two trials of six steps with the label first, so the
three- and four-trial splits and the interior placements are not in it. *And one threshold*: the payout is the
action's continuous one-step response, so a score, a sparse reward or a reward on the action at another step is a
different unit. *And one world, one budget, one learning rate and one seed stream*: the card's own setting, with the
map's ascent at the run's own `--lr`. *And three arms is a small population*: a claim over arms is not a claim about
the world. *And the carry is not removed from the world, only from the currency*: the world still integrates the
agent's history and the agent still acts on that state, so what changes is what the payout **reads** and not what the
loop **is**.
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

#: the earned run this unit is about, its own meter run, and `e500`'s own earned run -- the carried-state currency
#: this one is read against on config, draw and level
NEW = Path("runs/e502_reward_on_action_episode2_labelfirst_reward_earn_20reps.json")
METER = Path("runs/e502_reward_on_action_episode2_labelfirst_reward_20reps.json")
CARRIED = Path("runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the one field the flag moves, and the run's own bookkeeping
MOVED = ("loop_reward_on_action",)
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = 2
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
#: the bar an arm's accuracy has to clear over chance, and how far under the meter run's it may sit
BAR = 0.10
TOL = 0.10
ARMS_NEEDED = 2
PLACES = 4
CLAIMS = (
    ("TA1", "and the new flag moves the payout and nothing else",
     "Against e500's own earned run every recorded config field agrees except loop_reward_on_action, the output path "
     "and the saved weights, the environment's draw agrees on every field with none added, none missing and none "
     "differing, and the run carries twenty replicates",
     "falsifier: any other config field differing, any draw field added, missing or differing, or a replicate count "
     "other than twenty"),
    ("TA2", f"and the action's currency is alive, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "The earned run's reward diagonal is above its own meter run's on at least two of the three arms at two sigma, "
     "and the map ends above the identity on every replicate",
     "falsifier: fewer than two arms resolving upward, or a replicate whose map distance is not positive"),
    ("TA3", f"and the pass is still learned, on {ARMS_NEEDED} arms",
     "On at least two of the three arms the accuracy diagonal is at least 0.10 above the four-class chance of 0.25 "
     "and within 0.10 of the meter run's own",
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
            "theirs_moved": {k: other_cfg.get(k) for k in MOVED},
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


def reading(new: Path = NEW, meter: Path = METER, carried: Path = CARRIED) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "map": {}, "reward": {}, "accuracy": {}, "shape": {},
           "spans": {}}
    earned, base, peer = _roll(new), _roll(meter), _roll(carried)
    out["runs"] = {"earned": earned, "meter": base, "carried": peer}
    if earned is None:
        return {**out, "ok": False, "reason": "the earned run is absent, or carries no replicate to read"}
    #: TA2 and TA3 are read across the pair; TA1's config and draw are read against `e500`'s own earned run
    pair = base is not None and not _reward_missing(earned) and not _reward_missing(base)
    against = _against(earned, peer) if (peer is not None and not _reward_missing(earned)
                                         and not _reward_missing(peer)) else None
    out["map"] = {"earned": _map(earned), "carried": _map(peer)}
    if pair:
        out["reward"] = {a: _paired(earned["arms"][a]["reward_diagonal"],
                                    base["arms"][a]["reward_diagonal"]) for a in ARMS}
        out["accuracy"] = {a: _paired(earned["arms"][a]["accuracy_diagonal"],
                                      base["arms"][a]["accuracy_diagonal"]) for a in ARMS}
        #: an extra reading rather than a claim: each run's reward diagonal against **its own** last row
        out["shape"] = {label: {a: _paired(roll["arms"][a]["reward_diagonal"], roll["arms"][a]["reward_last"])
                                for a in ARMS} for label, roll in (("earned", earned), ("meter", base))}

    def _diag(roll, key):
        return (None if roll is None else {a: round(statistics.fmean(roll["arms"][a][key]), PLACES) for a in ARMS})

    out["spans"] = {
        "arms": list(ARMS), "runs": list(out["runs"]), "episode": EPISODE, "chance": CHANCE,
        "bar": BAR, "tol": TOL, "sigma": SIGMA, "arms_needed": ARMS_NEEDED,
        "readable": {k: v is not None for k, v in out["runs"].items()},
        "replicates": sorted({v["replicates"] for roll in (earned, base, peer) if roll
                              for v in roll["arms"].values()}),
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "config": {"earned": against},
        "draw": {"earned": (None if against is None else against["draw"])},
        "accuracy_diagonal": {label: _diag(roll, "accuracy_diagonal") for label, roll in
                              (("earned", earned), ("meter", base), ("carried", peer))},
        "accuracy_last": {label: _diag(roll, "accuracy_last") for label, roll in
                          (("earned", earned), ("meter", base), ("carried", peer))},
        "reward_diagonal": {label: _diag(roll, "reward_diagonal") for label, roll in
                            (("earned", earned), ("meter", base), ("carried", peer))},
        "reward_last": {label: _diag(roll, "reward_last") for label, roll in
                        (("earned", earned), ("meter", base), ("carried", peer))},
        "reward_shape": ({label: {a: {"mean": round(out["shape"][label][a]["mean"], PLACES),
                                     "sigma": round(out["shape"][label][a]["sigma"], 2)} for a in ARMS}
                          for label in out["shape"]} if out["shape"] else None),
        "map_move": {"earned": (None if out["map"]["earned"] is None else
                                {a: {"mean": round(out["map"]["earned"][a]["mean"], PLACES),
                                     "smallest": round(out["map"]["earned"][a]["smallest"], PLACES)}
                                 for a in ARMS}),
                     "carried": (None if out["map"]["carried"] is None else
                                 {a: {"mean": round(out["map"]["carried"][a]["mean"], PLACES)} for a in ARMS})},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    cfg = s["config"]["earned"]
    if cfg is None:
        j1 = {"id": "TA1",
              "measured": "the earned run's own config and draw have no carried-state run beside them",
              "verdict": f"REFUSED -- {CARRIED.name} is absent, or carries no reward matrix, so the flag's own "
                         f"config and draw are not compared"}
    else:
        draw = s["draw"]["earned"]
        moved = cfg["moved"]
        mine_moved = {k: moved.get(k) for k in MOVED}
        theirs_moved = {k: cfg.get("theirs_moved", {}).get(k) for k in MOVED}
        moved_ok = all(mine_moved[k] is True for k in MOVED) and all(theirs_moved[k] in (None, False)
                                                                     for k in MOVED)
        draw_ok = not draw["added"] and not draw["differ"] and not draw["missing"]
        j1 = {"id": "TA1",
              "measured": f"the config: **{len(cfg['differ'])}** differing past the inert rule ({cfg['differ']}) over "
                          f"**{cfg['same'] + len(cfg['inert'])}** fields, the field moved {mine_moved}; the draw: "
                          f"**{len(draw['agree'])}** fields with **{len(draw['differ'])}** differing, "
                          f"**{len(draw['added'])}** added and **{len(draw['missing'])}** missing; replicates "
                          f"{s['replicates']}",
              "verdict": "MET -- the payout is read on the action and the flag moves nothing else: one config field "
                         "past the carried-state run's, one world and one pass" if (not cfg["differ"] and moved_ok
                                                                                    and draw_ok
                                                                                    and s["replicates"] == [MIN_REPS])
                         else f"FALSIFIER FIRED -- differing {cfg['differ']}, moved {mine_moved}, draw {draw}, "
                              f"replicates {s['replicates']}"}
    mv = r["map"]["earned"]
    if mv is None or not r["reward"]:
        j2 = {"id": "TA2",
              "measured": "the pair's two currencies are not both readable, or the run records no policy movement",
              "verdict": "REFUSED -- the meter run is absent or carries no reward matrix, so the action's currency "
                         "has nothing beside it"}
    else:
        carried_mv = s["map_move"].get("carried")
        thin = [a for a in ARMS if mv[a]["above_zero"] != mv[a]["replicates"] or mv[a]["smallest"] <= 0.0]
        up = [a for a in ARMS if r["reward"][a]["mean"] > 0.0 and r["reward"][a]["sigma"] >= SIGMA]
        j2 = {"id": "TA2",
              "measured": (f"the map's distance from the identity is **{mv}** on the earned run"
                           + ("" if carried_mv is None else f", beside `e500`'s carried-state **{carried_mv}**")
                           + f"; the reward's diagonal less the meter run's, paired over the replicates: "
                             f"**{ {a: round(r['reward'][a]['mean'], PLACES) for a in ARMS} }** at "
                             f"**{ {a: round(r['reward'][a]['sigma'], 2) for a in ARMS} }** sigma, from "
                             f"**{s['reward_diagonal']['earned']}** against **{s['reward_diagonal']['meter']}**"),
              "verdict": f"MET -- the action's currency lifts the reward's diagonal above the meter run's on "
                         f"**{len(up)}** of three arms ({up}) at {SIGMA:.0f} sigma and the map is above the identity "
                         f"on every replicate" if (not thin and len(up) >= ARMS_NEEDED) else
                         f"FALSIFIER FIRED -- thin {thin}, {len(up)} of three arms lifting at {SIGMA:.0f} sigma "
                         f"({up})"}
    diag = s["accuracy_diagonal"]
    if diag["meter"] is None or not r["accuracy"]:
        j3 = {"id": "TA3",
              "measured": "the earned run's accuracy has no meter run beside it",
              "verdict": "REFUSED -- the meter run is absent, so the pass's own accuracy is not compared"}
    else:
        under = [a for a in ARMS if diag["earned"][a] < diag["meter"][a] - TOL]
        over = [a for a in ARMS if diag["earned"][a] >= CHANCE + BAR]
        j3 = {"id": "TA3",
              "measured": f"the earned run's accuracy diagonals **{diag['earned']}** against the meter run's "
                          f"**{diag['meter']}**, **{len(over)}** of three arms at least {BAR:.2f} above the chance "
                          f"of {CHANCE:.2f} and **{len(under)}** more than {TOL:.2f} under the meter run's "
                          f"({under}), for changes of "
                          f"**{ {a: round(r['accuracy'][a]['mean'], PLACES) for a in ARMS} }** at "
                          f"**{ {a: round(r['accuracy'][a]['sigma'], 2) for a in ARMS} }** sigma",
              "verdict": f"MET -- the pass is still learned with the payout on the action: **{len(over)}** of three "
                         f"arms over the bar ({over}) and none more than {TOL:.2f} under the meter run's"
                         if (len(over) >= ARMS_NEEDED and not under) else
                         f"FALSIFIER FIRED -- {len(over)} of three arms over the bar ({over}), under the meter run's "
                         f"by more than {TOL:.2f}: {under}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the world pays the action ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e500` and `e501` read the payout on the world's carried state; this reads it on the world's")
    print("   one-step response to the action, the same target and step, with `--loop-reward-on-action`")
    s = r["spans"]
    print(f"\n   {'arm':<10} {'reward act':>12} {'reward carry':>13} {'payout gain':>12} {'sigma':>7} "
          f"{'acc act':>9} {'acc carry':>10} {'d acc':>8} {'map act':>9} {'e500 map':>9}")
    for a in ARMS:
        g, c = r["reward"][a], r["accuracy"][a]
        moved = (0.0 if r["map"]["earned"] is None else r["map"]["earned"][a]["mean"])
        base = (0.0 if r["map"]["carried"] is None else r["map"]["carried"][a]["mean"])
        print(f"   {a:<10} {s['reward_diagonal']['earned'][a]:>12.4f} "
              f"{s['reward_diagonal']['meter'][a]:>13.4f} {g['mean']:>+12.4f} {g['sigma']:>7.2f} "
              f"{s['accuracy_diagonal']['earned'][a]:>9.4f} {s['accuracy_diagonal']['meter'][a]:>10.4f} "
              f"{c['mean']:>+8.4f} {moved:>9.4f} {base:>9.4f}")
    cfg = s["config"]["earned"]
    if cfg is not None:
        draw = s["draw"]["earned"]
        print(f"\n   the config: {len(cfg['differ'])} differing past the inert rule {cfg['differ']}; "
              f"the field moved {cfg['moved']}")
        print(f"   the draw: {len(draw['agree'])} fields with {len(draw['differ'])} differing, {len(draw['added'])} "
              f"added and {len(draw['missing'])} missing")
    if s.get("reward_shape"):
        print(f"   the reward's own shape, diagonal less last row: earned "
              f"{ {a: round(r['shape']['earned'][a]['mean'], 4) for a in ARMS} } against meter "
              f"{ {a: round(r['shape']['meter'][a]['mean'], 4) for a in ARMS} }")
    else:
        print("   the reward's own shape has no instrument: one of the pair's two currencies is absent")
    if s["reward_diagonal"].get("carried") is not None:
        print(f"   the earned run's reward level beside `e500`'s carried-state run: "
              f"{s['reward_diagonal']['earned']} against {s['reward_diagonal']['carried']}")
    print("\n== the registered claims, TA1-TA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e500` read the payout on the carry inside the episode; this reads it on the action)")
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
