"""E511 -- the earning at the knee of the window curve: whether the world's payout on the pass at the curve's knee
follows the meter's distance from the target or the pass's own accuracy.

The corpus holds the earned-versus-meter ablation at **two** passes. `e500` reads it at a pass the head **learns**:
its two-trial, label-first pass reads about **0.83**, the meter's cells run about **-6.05** and the payout's gain is
**+1.5086**, **+1.4123** and **+1.0722**. `e507` reads it at a **chance** pass: the three-trial pass with the label at
trial **1** (window **7**) reads about **0.31**, the meter's cells run about **-42.3** and the gain is **+7.6020**,
**+9.0113** and **+5.9397** -- and read that as the meter sitting **further from the target**. `e510` then put the
whole window ladder together and found the curve's **knee**: the six-trial pass with the label at trial **1** sits at
window **9** and reads **0.4899**, **0.4743** and **0.4979**, between the learned window **11** at about **0.83** and
the chance windows at or below **7**. **That knee is a third point between the two the ablation has been read at,
and no unit has put the payout there.** This unit does.

Two runs, `e500`'s own configuration with the pass at **six trials** and the label at trial **1** (window **9**): the
**meter** run (`--loop-reward` only) and the same plus `--loop-policy --loop-earn`, the **earned** run. They are read
against each other and against `e500`'s own earned and meter runs on the learned, two-trial pass and `e507`'s own on
the chance, three-trial pass -- the three points of the window curve, at the three passes the ablation has been read
at.

Three claims, registered before either new run's reading was opened. Each has an explicit falsifier.

- **BA1 -- and the pair is two flags apart.** Against the meter run the earned run's recorded `config` agrees on every
  field except `loop_policy`, `loop_earn`, the output path and the saved weights; the environment's draw agrees on
  **every** field; and both carry **20** replicates. **Falsifier**: any other config field differing, a draw field
  differing, or a replicate count other than twenty.
- **BA2 -- and the world pays at the knee.** The earned run's map ends above the identity on **every** replicate, and
  its reward diagonal is above the meter run's on at least **two of the three** arms at **two** sigma. **Falsifier**: a
  replicate whose map distance is not positive, or fewer than two arms resolving upward.
- **BA3 -- and the earning is ordered by the meter's own distance from the target, not by the pass's accuracy.** The
  meter run's reward level here sits **between** `e500`'s (about **-6.05**) and `e507`'s (about **-42.3**) on **every**
  arm, and the earned run's gain over its meter sits **between** `e500`'s gain and `e507`'s on at least **two of the
  three** arms, while this pass's accuracy (about **0.49**) is **between** theirs on every arm. **Falsifier**: a meter
  level outside the interval on any arm, a gain outside it on two or more arms, or an accuracy outside it.

**What it can do beyond that.** It reads the ablation at the one pass the window curve puts **between** the two it has
been read at, so the two accounts `e500` and `e507` each named -- the earning as a property of the ablation, and the
earning as a function of how far the meter sits from the target -- are read at a third point that neither was read at.
Read with `e510` it is the payout on the curve's own knee, and read with `e507` it is the middle of the three points
the meter's distance orders.

**What it cannot do.** *Three points are not a curve*: `e500`'s learned pass, this unit's knee at window **9** and
`e507`'s chance pass at window **7** are three readings on the window axis and no pass between window **9** and
window **11** or between window **9** and window **7** is paid here, so the shape of the earning against the window
is read at three points and not drawn. *And the three passes differ in the number of trials, the trial's length and
the window at once*: two trials of six steps, six trials of two steps and three trials of four steps, at windows
**11**, **9** and **7**, so the meter's distance, the pass's own difficulty and the trial's structure move together
and the claim's ordering cannot separate them. *And the payout's own shape and the currency on the action are not on
these runs*: the environment's state-matching target rule, a linear read of the cue, and no run here scores the
agent's **action** the way `e502`'s currency does; the earned diagonal's lift over its own last row is carried as an
extra reading rather than a claim. *And one world, one budget, one learning rate and one seed stream*: the card's own
setting with `--lr 0.003` and `--seed0 0`, so a second world, a second budget, the swept ascent rate of `e504` and a
second seed stream are not in it.
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
#: the pair this unit adds: `e500`'s own paid, reward-carrying command at six trials with the label at trial 1
#: (window nine, the curve's knee) -- the meter run and the same plus the two earning flags
NEW = Path("runs/e511_label_at1_episode6_reward_earn_20reps.json")
METER = Path("runs/e511_label_at1_episode6_reward_20reps.json")
#: `e500`'s own earned and meter runs on the learned, label-first, two-trial pass (window 11): the point above
LEARNED_EARN = Path("runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json")
LEARNED_METER = Path("runs/e498_earned_label_episode2_labelfirst_reward_20reps.json")
#: `e507`'s own earned and meter runs on the chance, label-at-1, three-trial pass (window 7): the point below
CHANCE_EARN = Path("runs/e507_label_at1_episode3_reward_earn_20reps.json")
CHANCE_METER = Path("runs/e507_label_at1_episode3_reward_20reps.json")
#: the map's distance beside these runs, so this unit's figure has the corpus's learned passes next to it
BESIDE = {"two_trials": LEARNED_EARN,
          "three_trials": Path("runs/e501_earned_label_episode3_labelfirst_reward_earn_20reps.json"),
          "chance_pass": CHANCE_EARN}
#: the two fields the pair moves, and the run's own bookkeeping
MOVED = ("loop_policy", "loop_earn")
BOOKKEEPING = ("json_out", "save_theta")
#: this unit's pass: six trials, the label at trial 1, which is window 9 -- the window curve's knee
EPISODE = 6
LABEL_AT = 1
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
ARMS_NEEDED = 2
PLACES = 4
TRIAL_LEN = TAU // EPISODE
WINDOW = (TAU - 1) - LABEL_AT * TRIAL_LEN
CLAIMS = (
    ("BA1", "and the pair is two flags apart",
     "Against the meter run the earned run's recorded config agrees on every field except loop_policy, loop_earn, the "
     "output path and the saved weights; the environment's draw agrees on every field; and both carry twenty "
     "replicates",
     "falsifier: any other config field differing, a draw field differing, or a replicate count other than twenty"),
    ("BA2", f"and the world pays at the knee, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "The earned run's map ends above the identity on every replicate, and its reward diagonal is above the meter "
     "run's on at least two of the three arms at two sigma",
     "falsifier: a replicate whose map distance is not positive, or fewer than two arms resolving upward"),
    ("BA3", f"and the earning is ordered by the meter's own distance and not by the pass's accuracy, on "
            f"{ARMS_NEEDED} arms for the gain",
     "The meter run's reward level here sits between e500's own (about -6.05) and e507's own (about -42.3) on every "
     "arm, and the earned run's gain over its meter sits between e500's gain and e507's on at least two of the three "
     "arms, while this pass's accuracy (about 0.49) is between theirs on every arm",
     "falsifier: a meter level outside the interval on any arm, a gain outside it on two or more arms, or an "
     "accuracy outside it"),
)


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return False


def _between(x: float, a: float, b: float) -> bool:
    """Whether ``x`` sits between ``a`` and ``b``, whichever of the two is the larger."""
    return min(a, b) - 1e-12 <= x <= max(a, b) + 1e-12


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


def _earned(roll: dict | None) -> bool:
    return roll is not None and all(roll["arms"][a]["reward_diagonal"] is not None
                                    and roll["arms"][a]["reward_last"] is not None for a in ARMS)


def _gain(earn: dict, meter: dict) -> dict:
    """The world's payout the earning bought: the earned run's reward diagonal less the meter run's, per arm."""
    return {a: _paired(earn["arms"][a]["reward_diagonal"], meter["arms"][a]["reward_diagonal"]) for a in ARMS}


def _level(roll: dict | None) -> dict | None:
    """The meter's own cells, per arm: the reward diagonal's level, which is how far the world sits from its target."""
    if not _paid(roll):
        return None
    return {a: statistics.fmean(roll["arms"][a]["reward_diagonal"]) for a in ARMS}


def _acc(roll: dict | None) -> dict | None:
    if roll is None:
        return None
    return {a: statistics.fmean(roll["arms"][a]["accuracy_diagonal"]) for a in ARMS}


def _point(runs: dict) -> dict:
    """One of the three points of the curve: the meter's level, the gain and the pass's accuracy, per arm."""
    gain = _gain(runs["earned"], runs["meter"]) if _paid(runs["earned"]) and _paid(runs["meter"]) else None
    return {"meter": _level(runs["meter"]),
            "gain": None if gain is None else {a: gain[a]["mean"] for a in ARMS},
            "accuracy": _acc(runs["earned"])}


def reading(new=NEW, meter=METER, learned_earn=LEARNED_EARN, learned_meter=LEARNED_METER,
            chance_earn=CHANCE_EARN, chance_meter=CHANCE_METER, beside: dict | None = None) -> dict:
    """Every run this unit reads, the three points of the curve, and the extra readings beside them.

    A run that is absent is recorded as absent rather than refused here, so each claim refuses on its own input: the
    two new runs are the pair's claim, the earned run's map and reward are the payout's, and the three points are the
    ordering's. The map's neighbours are extra readings and refuse nothing.
    """
    beside = dict(BESIDE if beside is None else beside)
    runs = {"earned": _roll(new), "meter": _roll(meter)}
    learned = {"earned": _roll(learned_earn), "meter": _roll(learned_meter)}
    chance = {"earned": _roll(chance_earn), "meter": _roll(chance_meter)}
    out = {"ok": True, "reason": None, "runs": runs, "learned": learned, "chance": chance, "map": {},
           "reward": None, "reward_last": None, "accuracy": None, "points": None, "spans": {}}
    both = runs["earned"] is not None and runs["meter"] is not None
    against = _against(runs["earned"], runs["meter"]) if both else None
    reward = _gain(runs["earned"], runs["meter"]) if _paid(runs["earned"]) and _paid(runs["meter"]) else None
    out["reward"] = reward
    out["reward_last"] = ({a: _paired(runs["earned"]["arms"][a]["reward_diagonal"],
                                      runs["earned"]["arms"][a]["reward_last"]) for a in ARMS}
                          if _earned(runs["earned"]) else None)
    out["accuracy"] = ({a: _paired(runs["earned"]["arms"][a]["accuracy_diagonal"],
                                   runs["meter"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
                       if both else None)
    out["points"] = {"here": _point(runs), "learned": _point(learned), "chance": _point(chance)}
    out["map"] = {"earned": _map(runs["earned"]),
                  "beside": {k: _map(_roll(v)) for k, v in beside.items()}}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(runs), "episode": EPISODE, "label_at": LABEL_AT, "window": WINDOW,
        "trial_len": TRIAL_LEN, "tau": TAU, "chance": CHANCE, "sigma": SIGMA, "arms_needed": ARMS_NEEDED,
        "replicates": (sorted({v["replicates"] for roll in runs.values() for v in roll["arms"].values()})
                       if all(roll is not None for roll in runs.values()) else []),
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
        "reward_diagonal": {label: ({a: round(statistics.fmean(runs[label]["arms"][a]["reward_diagonal"]), PLACES)
                                     for a in ARMS} if _paid(runs[label]) else None) for label in runs},
        "reward_last": ({a: round(statistics.fmean(runs["earned"]["arms"][a]["reward_last"]), PLACES) for a in ARMS}
                        if _earned(runs["earned"]) else None),
        "map_move": {"earned": (None if out["map"]["earned"] is None else
                                {a: {"mean": round(out["map"]["earned"][a]["mean"], PLACES),
                                     "smallest": round(out["map"]["earned"][a]["smallest"], PLACES)} for a in ARMS}),
                     "beside": {k: (None if out["map"]["beside"][k] is None else
                                    {a: round(out["map"]["beside"][k][a]["mean"], PLACES) for a in ARMS})
                                for k in out["map"]["beside"]}},
        "points": {label: {field: (None if value is None else {a: round(value[a], PLACES) for a in ARMS})
                           for field, value in out["points"][label].items()}
                   for label in out["points"]},
        "accuracy_change": ({a: {"mean": round(out["accuracy"][a]["mean"], PLACES),
                                 "sigma": round(out["accuracy"][a]["sigma"], 2)} for a in ARMS}
                            if out["accuracy"] is not None else None),
        "reward_last_change": ({a: {"mean": round(out["reward_last"][a]["mean"], PLACES),
                                    "sigma": round(out["reward_last"][a]["sigma"], 2)} for a in ARMS}
                               if out["reward_last"] is not None else None),
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'an input is absent')}"}
                for c in CLAIMS]
    runs = r["runs"]
    s = r["spans"]
    #: BA1 -- the pair is two flags apart
    against = s["config"]
    if runs["earned"] is None or runs["meter"] is None or against is None:
        j1 = {"id": "BA1", "measured": "a new run is absent",
              "verdict": "REFUSED -- one of the two new runs is not on disk, so the pair's own config and draw are "
                         "not compared"}
    else:
        cfg, draw = against["earned"], s["draw"]["earned"]
        moved = cfg["moved"]
        both_moved = all(moved.get(k) is True for k in MOVED)
        draw_ok = not draw["differ"] and not draw["added"] and not draw["missing"]
        j1 = {"id": "BA1",
              "measured": f"the config: **{len(cfg['differ'])}** differing past the inert rule ({cfg['differ']}) over "
                          f"**{cfg['same'] + len(cfg['inert'])}** fields, the fields moved {moved}; the draw: "
                          f"**{len(draw['agree'])}** fields with **{len(draw['differ'])}** differing, "
                          f"**{len(draw['added'])}** added and **{len(draw['missing'])}** missing; replicates "
                          f"{s['replicates']}; the pass is six trials with the label at trial "
                          f"{s['config']['pass']['loop_label_at']} (window {s['window']}), the draw's "
                          f"`episode_len` {s['draw']['pass']['episode_len']} and `label_at` "
                          f"{s['draw']['pass']['label_at']}",
              "verdict": "MET -- the paid pass at the curve's knee runs with the map earned, one world and one "
                         "payout, two flags from its own meter run" if (not cfg["differ"] and both_moved and draw_ok
                                                                        and s["replicates"] == [MIN_REPS]) else
                         f"FALSIFIER FIRED -- differing {cfg['differ']}, moved {moved}, draw {draw}, replicates "
                         f"{s['replicates']}"}
    #: BA2 -- the world pays at the knee
    mv = r["map"]["earned"]
    if runs["earned"] is None or runs["meter"] is None or r["reward"] is None:
        j2 = {"id": "BA2", "measured": "a new run or its reward matrix is absent",
              "verdict": "REFUSED -- the earned run or its meter run carries no reward matrix, so the payout is not "
                         "read"}
    else:
        thin = ([] if mv is None else
                [a for a in ARMS if mv[a]["above_zero"] != mv[a]["replicates"] or mv[a]["smallest"] <= 0.0])
        up = [a for a in ARMS if r["reward"][a]["mean"] > 0.0 and r["reward"][a]["sigma"] >= SIGMA]
        j2 = {"id": "BA2",
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
    #: BA3 -- the earning is ordered by the meter's own distance and not by the pass's accuracy
    pts = r["points"]
    here, learned, chance = pts["here"], pts["learned"], pts["chance"]
    missing = [k for k, v in (("here", here), ("learned", learned), ("chance", chance))
               if v["meter"] is None or v["gain"] is None or v["accuracy"] is None]
    if missing:
        j3 = {"id": "BA3", "measured": f"the point(s) {missing} carry no meter level, gain or accuracy",
              "verdict": "REFUSED -- the ordering is read over the three passes the ablation has been read at, so "
                         "the three points' meter levels, gains and accuracies are all needed"}
    else:
        inside_meter = [a for a in ARMS if _between(here["meter"][a], learned["meter"][a], chance["meter"][a])]
        inside_gain = [a for a in ARMS if _between(here["gain"][a], learned["gain"][a], chance["gain"][a])]
        inside_acc = [a for a in ARMS if _between(here["accuracy"][a], learned["accuracy"][a], chance["accuracy"][a])]
        j3 = {"id": "BA3",
              "measured": f"the meter's level, the gain and the accuracy at the three points, per arm -- **here** "
                          f"the meter **{ {a: round(here['meter'][a], PLACES) for a in ARMS} }**, the gain "
                          f"**{ {a: round(here['gain'][a], PLACES) for a in ARMS} }**, the accuracy "
                          f"**{ {a: round(here['accuracy'][a], PLACES) for a in ARMS} }**; **e500's learned pass** "
                          f"the meter **{ {a: round(learned['meter'][a], PLACES) for a in ARMS} }**, the gain "
                          f"**{ {a: round(learned['gain'][a], PLACES) for a in ARMS} }**, the accuracy "
                          f"**{ {a: round(learned['accuracy'][a], PLACES) for a in ARMS} }**; **e507's chance pass** "
                          f"the meter **{ {a: round(chance['meter'][a], PLACES) for a in ARMS} }**, the gain "
                          f"**{ {a: round(chance['gain'][a], PLACES) for a in ARMS} }**, the accuracy "
                          f"**{ {a: round(chance['accuracy'][a], PLACES) for a in ARMS} }** -- with the meter's level "
                          f"between the two on **{len(inside_meter)}** of three arms ({inside_meter}), the gain on "
                          f"**{len(inside_gain)}** of three ({inside_gain}) and the accuracy on "
                          f"**{len(inside_acc)}** of three ({inside_acc})",
              "verdict": f"MET -- the earning is ordered by the meter's own distance from the target and not by the "
                         f"pass's accuracy: the meter's level is between the other two points on every arm, the gain "
                         f"on **{len(inside_gain)}** of three and the accuracy on every arm"
                         if (len(inside_meter) == len(ARMS) and len(inside_gain) >= ARMS_NEEDED
                             and len(inside_acc) == len(ARMS)) else
                         f"FALSIFIER FIRED -- the meter's level between on {len(inside_meter)} of three "
                         f"({inside_meter}), the gain on {len(inside_gain)} of three ({inside_gain}) and the "
                         f"accuracy on {len(inside_acc)} of three ({inside_acc})"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the earning at the knee of the window curve ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an input is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the ablation has been read at a learned pass (window 11) and at a chance pass (window 7); this puts")
    print(f"   it at the curve's knee -- six trials, the label at trial {LABEL_AT}, window {WINDOW}")
    s = r["spans"]
    if r["reward"] is not None:
        print(f"\n   {'arm':<10} {'reward earn':>12} {'reward meter':>13} {'payout gain':>12} {'sigma':>7} "
              f"{'acc earn':>9} {'acc meter':>10} {'d acc':>8} {'map move':>9}")
        for a in ARMS:
            g, c = r["reward"][a], (r["accuracy"][a] if r["accuracy"] else None)
            moved = (0.0 if r["map"]["earned"] is None else r["map"]["earned"][a]["mean"])
            print(f"   {a:<10} {s['reward_diagonal']['earned'][a]:>12.4f} "
                  f"{s['reward_diagonal']['meter'][a]:>13.4f} {g['mean']:>+12.4f} {g['sigma']:>7.2f} "
                  f"{s['accuracy_diagonal']['earned'][a]:>9.4f} {s['accuracy_diagonal']['meter'][a]:>10.4f} "
                  f"{c['mean']:>+8.4f} {moved:>9.4f}")
        if r["reward_last"] is not None:
            print("   the earned run's reward diagonal against its own last row: "
                  + ", ".join(f"{a} {r['reward_last'][a]['mean']:+.4f} at {r['reward_last'][a]['sigma']:+.2f} sigma"
                              for a in ARMS))
    else:
        print("   a new run or its reward matrix is absent, so the payout's two levels are not read")
    print("\n   the three points of the curve, per arm:")
    print(f"   {'the point':<22} {'window':>7} {'meter level':>24} {'the gain':>24} {'the accuracy':>24}")
    for label, name, win in (("learned", "e500 learned", 11), ("here", "this unit (the knee)", WINDOW),
                             ("chance", "e507 chance", 7)):
        p = s["points"][label]
        if p["meter"] is None or p["gain"] is None or p["accuracy"] is None:
            print(f"   {name:<22} {win:>7} {'-':>24} {'-':>24} {'-':>24}")
            continue
        meter = "  ".join("{:.2f}".format(p["meter"][a]) for a in ARMS)
        gain = "  ".join("{:+.2f}".format(p["gain"][a]) for a in ARMS)
        acc = "  ".join("{:.3f}".format(p["accuracy"][a]) for a in ARMS)
        print(f"   {name:<22} {win:>7} {meter:>24} {gain:>24} {acc:>24}")
    print(f"   the pass: six trials of {s['trial_len']} steps, the label at trial {s['label_at']}, window "
          f"{s['window']} drive steps")
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
    print("\n== the registered claims, BA1-BA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e500` read the ablation above the knee, `e507` below it; this is the knee itself)")
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
