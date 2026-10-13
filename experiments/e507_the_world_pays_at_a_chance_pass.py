"""E507 -- the world pays at a chance pass: whether the payout reaches the map on a pass the head cannot learn.

`e500` reads the earned-versus-meter ablation on a pass that is **learned**: its own two-trial, label-first pass reads
about **0.83** and the payout reaches the map there -- **+1.5086**, **+1.4123** and **+1.0722** at **+22.74**,
**+22.57** and **+15.54** sigma, with the map above the identity on **60 of 60** replicates. `e506` then showed what
orders the pass is the label's **window** in drive steps: a placement whose window is small reads at or within **0.08**
of the four-class chance of **0.25** -- `e505`'s three-trial label-at-1 (window **7**) reads **0.3257**, **0.3069** and
**0.3274** and its label-at-2 (window **3**) reads **0.2566**, **0.2576** and **0.2542** -- and `e506`'s own *cannot do*
says *the payout is not on these runs*. **So every earned run in this repository is on a pass the head can learn, and
nothing has measured whether the world still pays the agent when the pass it is paying inside is one the head cannot
learn.** This unit puts the payout on such a pass.

Two runs, `e500`'s own configuration with the pass at **three trials** and the label at trial **1** (window **7**, at
chance): the **meter** run (`--loop-reward` only) and the same plus `--loop-policy --loop-earn`, the **earned** run.
They are read against `e500`'s own earned and meter runs on the learned, label-first pass -- the band is registered from
those two runs' spreads -- and beside `e505`'s placement runs, which carry the window's own reading.

Three claims, registered before either new run's reading was opened. Each has an explicit falsifier.

- **XA1 -- and the pair is two flags apart.** Against the meter run the earned run's recorded `config` agrees on every
  field except `loop_policy`, `loop_earn`, the output path and the saved weights; the environment's draw agrees on
  **every** field; and both carry **20** replicates. **Falsifier**: any other config field differing, a draw field
  differing, or a replicate count other than twenty.
- **XA2 -- and the world still pays at a pass at chance.** The earned run's map ends above the identity on **every**
  replicate, and its reward diagonal is above the meter run's on at least **two of the three** arms at **two** sigma.
  **Falsifier**: a replicate whose map distance is not positive, or fewer than two arms resolving upward.
- **XA3 -- and the earning does not need the pass to be learned.** The earned run's reward gain over its meter run is
  within the registered band of `e500`'s own gain on the learned label-first pass -- the band's half-width is the larger
  of the two comparisons' own paired spreads, so it is registered from the runs and not from the head -- while this
  pass's accuracy diagonal is at most **0.10** above the four-class chance of **0.25** (on at least two of the three
  arms). **Falsifier**: a gain outside the band, or an accuracy above that bar.

**What it can do beyond that.** It closes the clause `e506`'s own *cannot do* left open -- *the payout is not on these
runs* -- and it puts the earning where `e500`'s pass is not: what `e500` measured on a pass reading **0.83** is measured
here on one reading about **0.31**, so whether the payout's reach is a property of the earning or of the head is the
question. Read with `e506` it is the same placement the window orders, with a payout on it.

**What it cannot do.** *One placement and one pass length, so the window is **7** and no other*: the three-trial pass
with the label at trial **1**, the label at trial **0** (window **11**) and trial **2** (window **3**) not in it, so
whether the payout's reach falls with the window as the accuracy does is not measured. *And one payout and one
currency*: the environment's own state-matching target rule, a linear read of the cue, so a payout read on the action
(`e502`'s currency) is not on these runs, and sparse or shaped rewards are a different unit. *And the head is never
paid*: the map the agent acts through is what the payout ascends, and the body's task loss is untouched, so an agent
paid through its own head is a different unit. *And one world, one budget, one learning rate and one seed stream*: the
card's own setting with `--lr 0.003` and `--seed0 0`, so a second world, a second budget, the swept ascent rate of
`e504` and a second seed stream are not in it.
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

ARMS = e489.ARMS
#: the pair this unit adds: `e500`'s own paid, reward-carrying command at three trials with the label at trial 1
#: (window seven, at chance) -- the meter run and the same plus the two earning flags
NEW = Path("runs/e507_label_at1_episode3_reward_earn_20reps.json")
METER = Path("runs/e507_label_at1_episode3_reward_20reps.json")
#: `e500`'s own earned and meter runs on the learned, label-first, two-trial pass: the band is registered from these
REF_EARN = Path("runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json")
REF_METER = Path("runs/e498_earned_label_episode2_labelfirst_reward_20reps.json")
#: the map's distance beside these two runs, so this unit's figure has the corpus's learned passes next to it
BESIDE = {"two_trials": REF_EARN,
          "three_trials": Path("runs/e501_earned_label_episode3_labelfirst_reward_earn_20reps.json")}
#: `e505`'s placement runs at the same pass length, read so the window's own accuracy is beside this unit's: the key
#: is the placement's own name, the trial the label's cue sits at, and the run on disk
PLACEMENTS = (("at1", 1, Path("runs/e505_label_at1_episode3_20reps.json")),
              ("at2", 2, Path("runs/e505_label_at2_episode3_20reps.json")))
#: the two fields the pair moves, and the run's own bookkeeping
MOVED = ("loop_policy", "loop_earn")
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = e489.EPISODE
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
ARMS_NEEDED = 2
#: the bar the pass's accuracy has to stay under, over the four-class chance
BAR = 0.10
PLACES = 4
#: where the label's cue sits in the pass's trials, and the drive steps that leaves to the read
LABEL_AT = 1
WINDOW = (TAU - 1) - LABEL_AT * (TAU // EPISODE)
CLAIMS = (
    ("XA1", "and the pair is two flags apart",
     "Against the meter run the earned run's recorded config agrees on every field except loop_policy, loop_earn, the "
     "output path and the saved weights; the environment's draw agrees on every field; and both carry twenty "
     "replicates",
     "falsifier: any other config field differing, a draw field differing, or a replicate count other than twenty"),
    ("XA2", f"and the world still pays at a pass at chance, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "The earned run's map ends above the identity on every replicate, and its reward diagonal is above the meter "
     "run's on at least two of the three arms at two sigma",
     "falsifier: a replicate whose map distance is not positive, or fewer than two arms resolving upward"),
    ("XA3", f"and the earning does not need the pass to be learned, within the runs' own band at {BAR:.2f}",
     "The earned run's reward gain over its meter run is within the registered band of e500's own gain on the learned "
     "label-first pass -- the band's half-width taken from the two comparisons' own paired spreads -- while this "
     "pass's accuracy diagonal is at most 0.10 above the four-class chance of 0.25 on at least two of the three arms",
     "falsifier: a gain outside the band, or an accuracy above that bar"),
)


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return False


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


def _roll(path) -> dict | None:
    """One run's per-arm reading: both currencies' diagonals and last rows, the map's movement, config and draw."""
    path = Path(path)
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
        #: a run without the payout records the field with a matrix of `None`s, so the cell's presence is not the
        #: payout's: what is checked is the matrix's own corner
        if any(x is None or x[0] is None or x[0][0] is None for x in rw):
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


def _paid(roll: dict | None) -> bool:
    return roll is not None and all(roll["arms"][a]["reward_diagonal"] is not None for a in ARMS)


def _gain(earn: dict, meter: dict) -> dict:
    """The world's payout the earning bought: the earned run's reward diagonal less the meter run's, per arm."""
    return {a: _paired(earn["arms"][a]["reward_diagonal"], meter["arms"][a]["reward_diagonal"]) for a in ARMS}


def _band(ref: dict, new: dict) -> dict:
    """The band the new run's gain is read inside, registered from the two comparisons' own spreads.

    The reference is `e500`'s own earned-less-meter gain per arm; the band's half-width is the **larger of the two
    comparisons' own paired spreads** -- `e500`'s earn-vs-meter and this unit's -- so the width is the runs' own
    scatter at read time and not a number from the head. A gain falls inside when it is within that width of the
    reference.
    """
    out = {}
    for a in ARMS:
        g0, g1 = ref[a], new[a]
        w = max(g0["sd"], g1["sd"])
        out[a] = {"reference": g0["mean"], "new": g1["mean"], "width": w,
                  "low": g0["mean"] - w, "high": g0["mean"] + w,
                  "inside": abs(g1["mean"] - g0["mean"]) <= w}
    return out


def reading(new=NEW, meter=METER, ref_earn=REF_EARN, ref_meter=REF_METER,
            beside: dict | None = None, placements=None) -> dict:
    """Every run this unit reads, the band it registered, and the extra readings beside them.

    A run that is absent is recorded as absent rather than refused here, so each claim refuses on its own input: the
    two new runs are the pair's claim, the earned run's map and reward are the payout's, and `e500`'s own two runs are
    the band's. The map's neighbours and `e505`'s placements are extra readings and refuse nothing.
    """
    beside = dict(BESIDE if beside is None else beside)
    places = tuple(PLACEMENTS if placements is None else placements)
    runs = {"earned": _roll(new), "meter": _roll(meter)}
    ref = {"earned": _roll(ref_earn), "meter": _roll(ref_meter)}
    out = {"ok": True, "reason": None, "runs": runs, "map": {}, "reward": None, "accuracy": None,
           "reward_last": None, "band": None, "ref": None, "spans": {}}
    against = (_against(runs["earned"], runs["meter"])
               if runs["earned"] is not None and runs["meter"] is not None else None)
    reward = _gain(runs["earned"], runs["meter"]) if _paid(runs["earned"]) and _paid(runs["meter"]) else None
    out["reward"] = reward
    out["reward_last"] = ({a: _paired(runs["earned"]["arms"][a]["reward_diagonal"],
                                      runs["earned"]["arms"][a]["reward_last"]) for a in ARMS}
                          if _paid(runs["earned"]) else None)
    out["accuracy"] = ({a: _paired(runs["earned"]["arms"][a]["accuracy_diagonal"],
                                   runs["meter"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
                       if runs["earned"] is not None and runs["meter"] is not None else None)
    out["ref"] = _gain(ref["earned"], ref["meter"]) if _paid(ref["earned"]) and _paid(ref["meter"]) else None
    out["band"] = (_band(out["ref"], reward) if out["ref"] is not None and reward is not None else None)
    out["map"] = {"earned": _map(runs["earned"]),
                  "beside": {k: _map(_roll(v)) for k, v in beside.items()}}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(runs), "episode": EPISODE, "label_at": LABEL_AT, "window": WINDOW,
        "trial_len": TAU // EPISODE, "tau": TAU, "chance": CHANCE, "bar": BAR, "sigma": SIGMA,
        "arms_needed": ARMS_NEEDED,
        "replicates": sorted({v["replicates"] for roll in runs.values() for v in roll["arms"].values()}
                             if all(roll is not None for roll in runs.values()) else set()),
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "config": (None if against is None else {"earned": against, "pass": {
            "loop_episode": runs["earned"]["config"].get("loop_episode"),
            "loop_label_at": runs["earned"]["config"].get("loop_label_at"),
            "loop_reward": runs["earned"]["config"].get("loop_reward"),
            "loop_earn": runs["earned"]["config"].get("loop_earn")}}),
        "draw": (None if against is None else {"earned": against["draw"], "pass": {
            "episode_len": runs["earned"]["env_draw"].get("episode_len"),
            "label_at": runs["earned"]["env_draw"].get("label_at")}}),
        "accuracy_diagonal": {label: ({a: round(statistics.fmean(runs[label]["arms"][a]["accuracy_diagonal"]), PLACES)
                                       for a in ARMS} if runs[label] is not None else None) for label in runs},
        "accuracy_last": {label: ({a: round(statistics.fmean(runs[label]["arms"][a]["accuracy_last"]), PLACES)
                                   for a in ARMS} if runs[label] is not None else None) for label in runs},
        "reward_diagonal": {label: ({a: round(statistics.fmean(runs[label]["arms"][a]["reward_diagonal"]), PLACES)
                                     for a in ARMS} if _paid(runs[label]) else None) for label in runs},
        "reward_last": ({a: round(statistics.fmean(runs["earned"]["arms"][a]["reward_last"]), PLACES) for a in ARMS}
                        if out["reward_last"] is not None else None),
        "map_move": {"earned": (None if out["map"]["earned"] is None else
                                {a: {"mean": round(out["map"]["earned"][a]["mean"], PLACES),
                                     "smallest": round(out["map"]["earned"][a]["smallest"], PLACES)} for a in ARMS}),
                     "beside": {k: (None if out["map"]["beside"][k] is None else
                                    {a: round(out["map"]["beside"][k][a]["mean"], PLACES) for a in ARMS})
                                for k in out["map"]["beside"]}},
        "band": ({a: {"reference": round(out["band"][a]["reference"], PLACES),
                      "new": round(out["band"][a]["new"], PLACES),
                      "width": round(out["band"][a]["width"], PLACES),
                      "inside": out["band"][a]["inside"]} for a in ARMS} if out["band"] is not None else None),
        "ref_gain": ({a: round(out["ref"][a]["mean"], PLACES) for a in ARMS} if out["ref"] is not None else None),
        "placement": {k: ({"at": at, "window": (TAU - 1) - at * (TAU // EPISODE),
                           "accuracy_diagonal": {a: round(statistics.fmean(roll["arms"][a]["accuracy_diagonal"]),
                                                          PLACES) for a in ARMS}}
                           if roll is not None else None)
                      for k, at, roll in ((k, at, _roll(v)) for k, at, v in places)},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'an input is absent')}"}
                for c in CLAIMS]
    runs = r["runs"]
    s = r["spans"]
    #: XA1 -- the pair is two flags apart
    against = s["config"]
    if runs["earned"] is None or runs["meter"] is None or against is None:
        j1 = {"id": "XA1", "measured": "a new run is absent",
              "verdict": "REFUSED -- one of the two new runs is not on disk, so the pair's own config and draw are "
                         "not compared"}
    else:
        cfg, draw = against["earned"], s["draw"]["earned"]
        moved = cfg["moved"]
        both_moved = all(moved.get(k) is True for k in MOVED)
        draw_ok = not draw["differ"] and not draw["added"] and not draw["missing"]
        j1 = {"id": "XA1",
              "measured": f"the config: **{len(cfg['differ'])}** differing past the inert rule ({cfg['differ']}) over "
                          f"**{cfg['same'] + len(cfg['inert'])}** fields, the fields moved {moved}; the draw: "
                          f"**{len(draw['agree'])}** fields with **{len(draw['differ'])}** differing, "
                          f"**{len(draw['added'])}** added and **{len(draw['missing'])}** missing; replicates "
                          f"{s['replicates']}; the pass is three trials with the label at trial "
                          f"{s['config']['pass']['loop_label_at']} (window {s['window']}), the draw's "
                          f"`episode_len` {s['draw']['pass']['episode_len']} and `label_at` "
                          f"{s['draw']['pass']['label_at']}",
              "verdict": "MET -- the paid, at-chance pass runs with the map earned, one world and one payout, two "
                         "flags from its own meter run" if (not cfg["differ"] and both_moved and draw_ok
                                                            and s["replicates"] == [MIN_REPS]) else
                         f"FALSIFIER FIRED -- differing {cfg['differ']}, moved {moved}, draw {draw}, replicates "
                         f"{s['replicates']}"}
    #: XA2 -- the world still pays at a pass at chance
    mv = r["map"]["earned"]
    if runs["earned"] is None or runs["meter"] is None or r["reward"] is None:
        j2 = {"id": "XA2", "measured": "a new run or its reward matrix is absent",
              "verdict": "REFUSED -- the earned run or its meter run carries no reward matrix, so the payout is not "
                         "read"}
    else:
        thin = ([] if mv is None else
                [a for a in ARMS if mv[a]["above_zero"] != mv[a]["replicates"] or mv[a]["smallest"] <= 0.0])
        up = [a for a in ARMS if r["reward"][a]["mean"] > 0.0 and r["reward"][a]["sigma"] >= SIGMA]
        j2 = {"id": "XA2",
              "measured": (f"the map's distance from the identity is **{mv}** on the new run; the reward's diagonal "
                           f"less the meter run's, paired over the replicates: "
                           f"**{ {a: round(r['reward'][a]['mean'], PLACES) for a in ARMS} }** at "
                           f"**{ {a: round(r['reward'][a]['sigma'], 2) for a in ARMS} }** sigma, from "
                           f"**{s['reward_diagonal']['earned']}** against "
                           f"**{s['reward_diagonal']['meter']}**"
                           if mv is not None else "the new run records no policy movement on any replicate"),
              "verdict": f"MET -- the payout reaches the map on every replicate and lifts the reward's diagonal "
                         f"above the meter run's on **{len(up)}** of three arms ({up})" if (mv is not None
                                                                                            and not thin
                                                                                            and len(up) >= ARMS_NEEDED)
                         else f"FALSIFIER FIRED -- thin {thin}, {len(up)} of three arms lifting at two sigma "
                              f"({up}), moved {mv is not None}"}
    #: XA3 -- the earning does not need the pass to be learned
    diag = s["accuracy_diagonal"]
    if r["reward"] is None or r["band"] is None or diag["earned"] is None:
        j3 = {"id": "XA3", "measured": "the new pair or `e500`'s own pair is absent",
              "verdict": "REFUSED -- the band is registered from `e500`'s own earned and meter runs, so the new "
                         "gain is not read without both pairs"}
    else:
        inside = [a for a in ARMS if r["band"][a]["inside"]]
        above = [a for a in ARMS if diag["earned"][a] > CHANCE + BAR]
        j3 = {"id": "XA3",
              "measured": f"the new gain over its meter run is "
                          f"**{ {a: round(r['reward'][a]['mean'], PLACES) for a in ARMS} }** against `e500`'s own "
                          f"gain **{ {a: round(r['ref'][a]['mean'], PLACES) for a in ARMS} }**, the band half-widths "
                          f"**{ {a: round(r['band'][a]['width'], PLACES) for a in ARMS} }** (the larger of the two "
                          f"comparisons' own paired spreads), with **{len(inside)}** of three arms inside "
                          f"({inside}); this pass's accuracy diagonal is **{diag['earned']}** against the chance of "
                          f"{CHANCE:.2f}, with **{len(above)}** of three arms more than {BAR:.2f} above it "
                          f"({above})",
              "verdict": f"MET -- the earning does not need the pass to be learned: **{len(inside)}** of three arms "
                         f"within the band and the accuracy at or under {CHANCE + BAR:.2f} on "
                         f"**{len(ARMS) - len(above)}** of three arms" if (len(inside) >= ARMS_NEEDED
                                                                            and len(above) <= len(ARMS) - ARMS_NEEDED)
                         else f"FALSIFIER FIRED -- {len(inside)} of three arms inside the band ({inside}), "
                              f"accuracy above {CHANCE + BAR:.2f} on {len(above)} of three arms ({above})"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the world pays at a chance pass ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an input is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   every earned run on disk is on a pass the head learns; this moves the payout onto a three-trial pass")
    print(f"   with the label at trial {LABEL_AT} (window {WINDOW}, at chance) and reads the same ablation again")
    s = r["spans"]
    if r["reward"] is not None:
        print(f"\n   {'arm':<10} {'reward earn':>12} {'reward meter':>13} {'payout gain':>12} {'sigma':>7} "
              f"{'gain vs e500':>13} {'band':>8} {'acc earn':>9} {'acc meter':>10} {'map move':>9}")
        for a in ARMS:
            g, c = r["reward"][a], (r["accuracy"][a] if r["accuracy"] else None)
            moved = (0.0 if r["map"]["earned"] is None else r["map"]["earned"][a]["mean"])
            ref = (0.0 if r["ref"] is None else r["ref"][a]["mean"])
            band = (0.0 if r["band"] is None else r["band"][a]["width"])
            print(f"   {a:<10} {s['reward_diagonal']['earned'][a]:>12.4f} "
                  f"{s['reward_diagonal']['meter'][a]:>13.4f} {g['mean']:>+12.4f} {g['sigma']:>7.2f} "
                  f"{ref:>+13.4f} {band:>8.4f} "
                  f"{s['accuracy_diagonal']['earned'][a]:>9.4f} {s['accuracy_diagonal']['meter'][a]:>10.4f} "
                  f"{moved:>9.4f}")
        if r["reward_last"] is not None:
            print("   the earned run's reward diagonal against its own last row: "
                  + ", ".join(f"{a} {r['reward_last'][a]['mean']:+.4f} at {r['reward_last'][a]['sigma']:+.2f} sigma"
                              for a in ARMS))
    else:
        print("   a new run or its reward matrix is absent, so the payout's two levels are not read")
    print(f"   the pass: three trials of {s['trial_len']} steps, the label at trial {s['label_at']}, window "
          f"{s['window']} drive steps; `e505`'s placements at this length read "
          f"{ {k: (None if v is None else v['accuracy_diagonal']) for k, v in s['placement'].items()} }")
    cfg = s["config"]
    if cfg is not None:
        print(f"   the config: {len(cfg['earned']['differ'])} differing past the inert rule "
              f"{cfg['earned']['differ']}; the fields moved {cfg['earned']['moved']}")
        draw = s["draw"]["earned"]
        print(f"   the draw: {len(draw['agree'])} fields with {len(draw['differ'])} differing, {len(draw['added'])} "
              f"added and {len(draw['missing'])} missing")
    mv = s["map_move"]["earned"]
    if mv is not None:
        print(f"   the map's distance from the identity, mean per arm { {a: mv[a]['mean'] for a in ARMS} }, beside "
              f"{s['map_move']['beside']}")
    print("\n== the registered claims, XA1-XA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e500` earned on a pass the head learns; this is the world's payout on one it does not)")
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
