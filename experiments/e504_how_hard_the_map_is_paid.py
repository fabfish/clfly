"""E504 -- how hard the map is paid: whether the map's own ascent rate moves the earning the pass plays for.

Every earned run in this repository ascends the world's payout into the policy map **at the run's own `--lr`**.
`e488` gave the map an optimizer of its own and named it as one of its own absences -- *"the map's ascent runs at the
run's own `--lr`, so the strength of the earning is not swept"* -- and `e500`, `e501` and `e502` each closed on the
same sentence: the rate the map is paid at is the rate the body is trained at, and nothing varies it.

**This unit gives the map its own learning rate.** The runner gains **`--loop-earn-lr`**, threaded to the map's own
optimizer where `--loop-earn` sets it, recorded in the run's `config` as `loop_earn_lr`, and **`None` is exactly
today's behaviour** -- the run's own `--lr`. Two new runs are `e500`'s own earned command with the flag at **0.001**
and **0.01**; the run's-own-`--lr` point is `e500`'s own earned artifact (`--lr 0.003`), and the meter run is
`e498`'s paid run, the same configuration without the pair. Four claims, registered before either new run's reading
was opened.

- **UA1 -- the flag moves the ascent and nothing else.** Against `e500`'s own earned run each new run's recorded
  `config` agrees on every field except `loop_earn_lr`, the output path and the saved weights, with the recorded
  `loop_earn_lr` equal to the rate it was asked for; the environment's draw agrees on **every** field with none
  added, none missing and none differing; and each run carries **twenty** replicates. **Falsifier**: any other config
  field differing, a recorded rate that is not the one asked for, any draw field added, missing or differing, or a
  replicate count other than twenty.
- **UA2 -- paying harder earns more.** At the largest earn-lr the reward diagonal is **above** the run's-own-`--lr`
  point's on at least **two of the three** arms at **two** sigma, and at the smallest earn-lr it is **not** above it
  on more than one arm. **Falsifier**: fewer than two arms resolving upward at the largest rate, or the smallest rate
  resolving upward on two or more arms. *It can fire: the run's-own-rate point is `e500`'s own, where the payout
  reaches the map on every replicate and the reward sits **above** its own last row on two arms (**+0.7061** and
  **+0.7794**), so a rate that is too small to move the level is this claim and a curve that is flat or turns over is
  a perfectly good outcome.*
- **UA3 -- the pass is free at every point.** At each of the three rates, on at least **two of the three** arms the
  accuracy diagonal is within **0.10** of the meter run's own and at least **0.10** above the four-class chance of
  **0.25**. **Falsifier**: fewer than two arms within the band at any rate, or an arm within **0.05** of chance. *It
  can fire: `e488` found the paid map's accuracy **below** the task-loss map's on every arm by **0.0285** to
  **0.0410** at one trial, so a hard enough earning rate can cost the pass as well.*
- **UA4 -- the map travels further when paid harder.** The map's distance from the identity is larger at the largest
  earn-lr than at the smallest on at least **two of the three** arms at **two** sigma. **Falsifier**: fewer than two
  arms resolving upward.

**What it can do beyond that.** It is the first sweep of the one parameter `e488` left at its default, so the earning
`e500` measured as a property of the pair is read as a function of how hard the world's currency is pushed -- and the
default is measured inert, three of the corpus's readings re-read byte for byte through the flag.

**What it cannot do.** *Three rates are not a curve's shape*: 0.001, 0.003 and 0.01 are three points, so a peak or a
knee inside or outside them is not in the unit. *And one episode length and one placement*: two trials of six steps
with the label first, so the three- and four-trial splits and the interior placements are not in it. *And two
currencies, one of them measured elsewhere*: the payout is read on the world's carried state, and the action's
currency is `e502`'s unit and not this one. *And the map's ascent rate is not the body's*: the flag moves the map's
optimizer only, so nothing here says what the body's rate does. *And one world, budget and seed stream*: the card's
own setting with `--seed0 0` (and no `--loop-seed`), so a second world and a second stream are not in it. *And three
arms is a small population*: a claim over arms is not a claim about the world.
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

#: the two new runs this unit adds, the run's-own-`--lr` point `e500` earned, and the meter run the pass is read
#: against; the mid point is `e500`'s own artifact, so the curve has one point that predates this unit
SMALL = Path("runs/e504_earn_lr0.001_episode2_labelfirst_reward_earn_20reps.json")
MID = Path("runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json")
LARGE = Path("runs/e504_earn_lr0.01_episode2_labelfirst_reward_earn_20reps.json")
METER = Path("runs/e498_earned_label_episode2_labelfirst_reward_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the rates the three earned points were run at, keyed the way the reading labels them
RATES = {"small": 0.001, "mid": 0.003, "large": 0.01}
#: the one field the flag moves, and the run's own bookkeeping
MOVED = ("loop_earn_lr",)
BOOKKEEPING = ("json_out", "save_theta")
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
#: the bar an arm's accuracy has to clear over chance, and how far from the meter run's it may sit
BAR = 0.10
TOL = 0.10
#: how close to chance an arm's accuracy may not be
FLOOR = 0.05
ARMS_NEEDED = 2
PLACES = 4
CLAIMS = (
    ("UA1", "the flag moves the ascent and nothing else",
     "Against e500's own earned run each new run's recorded config agrees on every field except loop_earn_lr, the "
     "output path and the saved weights, with the recorded loop_earn_lr equal to the rate it was asked for; the "
     "environment's draw agrees on every field with none added, none missing and none differing; and each run "
     "carries twenty replicates",
     "falsifier: any other config field differing, a recorded rate that is not the one asked for, any draw field "
     "added, missing or differing, or a replicate count other than twenty"),
    ("UA2", f"paying harder earns more, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "At the largest earn-lr the reward diagonal is above the run's-own-`--lr` point's on at least two of the three "
     "arms at two sigma, and at the smallest earn-lr it is not above it on more than one arm",
     "falsifier: fewer than two arms resolving upward at the largest rate, or the smallest rate resolving upward on "
     "two or more arms"),
    ("UA3", f"the pass is free at every point, on {ARMS_NEEDED} arms",
     f"At each of the three rates, on at least two of the three arms the accuracy diagonal is within {TOL:.2f} of the "
     f"meter run's own and at least {BAR:.2f} above the four-class chance of {CHANCE:.2f}",
     f"falsifier: fewer than two arms within the band at any rate, or an arm within {FLOOR:.2f} of chance"),
    ("UA4", f"the map travels further when paid harder, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "The map's distance from the identity is larger at the largest earn-lr than at the smallest on at least two of "
     "the three arms at two sigma",
     "falsifier: fewer than two arms resolving upward"),
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


def _reward_missing(roll: dict | None) -> bool:
    return roll is None or any(roll["arms"][a]["reward_diagonal"] is None for a in ARMS)


def reading(small: Path = SMALL, mid: Path = MID, large: Path = LARGE, meter: Path = METER) -> dict:
    """The four runs' rolls, the curve of the earning across the three rates, and the map's movement at each."""
    out = {"ok": True, "reason": None, "runs": {}, "map": {}, "reward": {}, "accuracy": {}, "shape": {},
           "spans": {}}
    rolls = {"small": _roll(small), "mid": _roll(mid), "large": _roll(large), "meter": _roll(meter)}
    out["runs"] = rolls
    out["map"] = {k: _map(rolls[k]) for k in rolls}
    #: each new point's reward diagonal against the run's-own-`--lr` point's, paired over the replicate seeds; and
    #: each point's accuracy diagonal against the meter run's on the same pairing
    for k in ("small", "large"):
        if not _reward_missing(rolls[k]) and not _reward_missing(rolls["mid"]):
            out["reward"][k] = {a: _paired(rolls[k]["arms"][a]["reward_diagonal"],
                                           rolls["mid"]["arms"][a]["reward_diagonal"]) for a in ARMS}
        if rolls[k] is not None and rolls["meter"] is not None:
            out["accuracy"][k] = {a: _paired(rolls[k]["arms"][a]["accuracy_diagonal"],
                                             rolls["meter"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    if rolls["mid"] is not None and rolls["meter"] is not None:
        out["accuracy"]["mid"] = {a: _paired(rolls["mid"]["arms"][a]["accuracy_diagonal"],
                                             rolls["meter"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    #: an extra reading rather than a claim: each point's reward diagonal against **its own** last row
    out["shape"] = {k: ({a: _paired(rolls[k]["arms"][a]["reward_diagonal"],
                                    rolls[k]["arms"][a]["reward_last"]) for a in ARMS}
                        if not _reward_missing(rolls[k]) else None) for k in ("small", "mid", "large")}
    #: the map's movement, largest point against smallest, paired over the replicate seeds
    if out["map"]["small"] is not None and out["map"]["large"] is not None:
        out["travel"] = {a: _paired(rolls["large"]["arms"][a]["policy_move"],
                                    rolls["small"]["arms"][a]["policy_move"]) for a in ARMS}
    else:
        out["travel"] = {}
    #: the four rolls' config and draw against the mid point's, for the two new runs
    out["spans"] = {
        "arms": list(ARMS), "rates": RATES, "chance": CHANCE, "bar": BAR, "tol": TOL, "floor": FLOOR,
        "sigma": SIGMA, "arms_needed": ARMS_NEEDED,
        "readable": {k: v is not None for k, v in rolls.items()},
        "replicates": sorted({v["replicates"] for roll in rolls.values() if roll for v in roll["arms"].values()}),
        "against": {k: (_against(rolls[k], rolls["mid"]) if (rolls[k] is not None and rolls["mid"] is not None)
                        else None) for k in ("small", "large")},
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "accuracy_diagonal": {k: (None if rolls[k] is None else
                                  {a: round(statistics.fmean(rolls[k]["arms"][a]["accuracy_diagonal"]), PLACES)
                                   for a in ARMS}) for k in rolls},
        "reward_diagonal": {k: (None if _reward_missing(rolls[k]) else
                                {a: round(statistics.fmean(rolls[k]["arms"][a]["reward_diagonal"]), PLACES)
                                 for a in ARMS}) for k in ("small", "mid", "large", "meter")},
        "reward_last": {k: (None if _reward_missing(rolls[k]) else
                            {a: round(statistics.fmean(rolls[k]["arms"][a]["reward_last"]), PLACES)
                             for a in ARMS}) for k in ("small", "mid", "large")},
        "map_move": {k: (None if out["map"][k] is None else
                         {a: {"mean": round(out["map"][k][a]["mean"], PLACES),
                              "smallest": round(out["map"][k][a]["smallest"], PLACES),
                              "above_zero": out["map"][k][a]["above_zero"],
                              "replicates": out["map"][k][a]["replicates"]} for a in ARMS}) for k in rolls},
        "reward_gain": {k: (None if k not in out["reward"] else
                            {a: {"mean": round(out["reward"][k][a]["mean"], PLACES),
                                 "sigma": round(out["reward"][k][a]["sigma"], 2)} for a in ARMS})
                        for k in ("small", "large")},
        "accuracy_change": {k: (None if k not in out["accuracy"] else
                                {a: {"mean": round(out["accuracy"][k][a]["mean"], PLACES),
                                     "sigma": round(out["accuracy"][k][a]["sigma"], 2)} for a in ARMS})
                            for k in ("small", "mid", "large")},
        "travel": (None if not out["travel"] else
                   {a: {"mean": round(out["travel"][a]["mean"], PLACES),
                        "sigma": round(out["travel"][a]["sigma"], 2)} for a in ARMS}),
        "reward_shape": {k: (None if out["shape"][k] is None else
                             {a: {"mean": round(out["shape"][k][a]["mean"], PLACES),
                                  "sigma": round(out["shape"][k][a]["sigma"], 2)} for a in ARMS})
                         for k in ("small", "mid", "large")},
    }
    return out


def _up(paired: dict, arms) -> list:
    return [a for a in arms if paired[a]["mean"] > 0.0 and paired[a]["sigma"] >= SIGMA]


def judge(r: dict) -> list[dict]:
    rolls = r["runs"]
    s = r["spans"]
    #: UA1 -- the flag moves the ascent and nothing else
    if rolls.get("small") is None or rolls.get("large") is None or rolls.get("mid") is None:
        j1 = {"id": "UA1", "measured": "a new run or the run's-own-rate point is absent",
              "verdict": "REFUSED -- one of the three earned runs is not on disk, so the flag's own config and draw "
                         "are not compared"}
    else:
        rows, bad = {}, []
        for k in ("small", "large"):
            cfgv = s["against"][k]
            draw = cfgv["draw"]
            reps = sorted({v["replicates"] for v in rolls[k]["arms"].values()})
            rate_ok = cfgv["moved"].get("loop_earn_lr") == RATES[k]
            rows[k] = {"differ": cfgv["differ"], "moved": cfgv["moved"]["loop_earn_lr"], "rate_ok": rate_ok,
                       "draw": draw, "replicates": reps,
                       "draw_ok": not draw["added"] and not draw["differ"] and not draw["missing"],
                       "reps_ok": reps == [MIN_REPS]}
            if (cfgv["differ"] or not rate_ok or not rows[k]["draw_ok"] or not rows[k]["reps_ok"]):
                bad.append(k)
        j1 = {"id": "UA1",
              "measured": "; ".join(
                  f"the {k} point ({RATES[k]}): **{len(rows[k]['differ'])}** config fields differing past the inert "
                  f"rule ({rows[k]['differ']}) with `loop_earn_lr` recorded {rows[k]['moved']} against the mid point's "
                  f"`None`, the draw **{len(rows[k]['draw']['agree'])}** fields with "
                  f"**{len(rows[k]['draw']['differ'])}** differing, **{len(rows[k]['draw']['added'])}** added and "
                  f"**{len(rows[k]['draw']['missing'])}** missing, replicates {rows[k]['replicates']}"
                  for k in ("small", "large")),
              "verdict": "MET -- the flag moves the map's ascent rate and nothing else: one config field past the "
                         "run's-own-rate point's on each new run, one world and one pass" if not bad else
                         f"FALSIFIER FIRED -- {bad} over { {k: rows[k] for k in bad} }"}
    #: UA2 -- paying harder earns more
    if not (r["reward"].get("small") and r["reward"].get("large")):
        j2 = {"id": "UA2", "measured": "the curve's payout is not readable at both ends",
              "verdict": "REFUSED -- a new run or the run's-own-rate point is absent, or carries no reward matrix, "
                         "so the payout's two levels are not compared"}
    else:
        up_large = _up(r["reward"]["large"], ARMS)
        up_small = _up(r["reward"]["small"], ARMS)
        ok = len(up_large) >= ARMS_NEEDED and len(up_small) <= 1
        j2 = {"id": "UA2",
              "measured": f"the reward's diagonal at each new point less the run's-own-rate point's, paired over the "
                          f"replicates: the 0.01 point "
                          f"**{ {a: round(r['reward']['large'][a]['mean'], PLACES) for a in ARMS} }** at "
                          f"**{ {a: round(r['reward']['large'][a]['sigma'], 2) for a in ARMS} }** sigma and the 0.001 "
                          f"point **{ {a: round(r['reward']['small'][a]['mean'], PLACES) for a in ARMS} }** at "
                          f"**{ {a: round(r['reward']['small'][a]['sigma'], 2) for a in ARMS} }** sigma, from the "
                          f"levels 0.001 **{s['reward_diagonal']['small']}**, 0.003 "
                          f"**{s['reward_diagonal']['mid']}** and 0.01 **{s['reward_diagonal']['large']}**",
              "verdict": f"MET -- paying harder earns more: **{len(up_large)}** of three arms resolve upward at the "
                         f"largest rate ({up_large}) and **{len(up_small)}** at the smallest ({up_small})" if ok
                         else f"FALSIFIER FIRED -- **{len(up_large)}** of three arms upward at the largest rate "
                              f"({up_large}) and **{len(up_small)}** at the smallest ({up_small})"}
    #: UA3 -- the pass is free at every point
    if rolls.get("meter") is None or any(k not in r["accuracy"] for k in ("small", "mid", "large")):
        j3 = {"id": "UA3", "measured": "the accuracy has no meter run beside it, or a point is absent",
              "verdict": "REFUSED -- the meter run or one of the three points is not on disk, so the pass's own "
                         "accuracy is not compared"}
    else:
        meter_diag = s["accuracy_diagonal"]["meter"]
        bands, floor_hits = {}, []
        for k in ("small", "mid", "large"):
            diag = s["accuracy_diagonal"][k]
            bands[k] = [a for a in ARMS if abs(diag[a] - meter_diag[a]) <= TOL and diag[a] >= CHANCE + BAR]
            floor_hits += [(k, a) for a in ARMS if diag[a] <= CHANCE + FLOOR]
        ok = all(len(bands[k]) >= ARMS_NEEDED for k in bands) and not floor_hits
        j3 = {"id": "UA3",
              "measured": f"the accuracy diagonals 0.001 **{s['accuracy_diagonal']['small']}**, 0.003 "
                          f"**{s['accuracy_diagonal']['mid']}** and 0.01 **{s['accuracy_diagonal']['large']}** against "
                          f"the meter run's **{meter_diag}**: in the band on "
                          f"{ {k: len(bands[k]) for k in ('small', 'mid', 'large')} } of three arms, and "
                          f"**{len(floor_hits)}** arms within {FLOOR:.2f} of the chance of {CHANCE:.2f} "
                          f"({floor_hits}), for changes of 0.001 "
                          f"**{ {a: round(r['accuracy']['small'][a]['mean'], PLACES) for a in ARMS} }**, 0.003 "
                          f"**{ {a: round(r['accuracy']['mid'][a]['mean'], PLACES) for a in ARMS} }** and 0.01 "
                          f"**{ {a: round(r['accuracy']['large'][a]['mean'], PLACES) for a in ARMS} }**",
              "verdict": f"MET -- the pass is free at every rate: **{ {k: len(bands[k]) for k in bands} }** of three "
                         f"arms within {TOL:.2f} of the meter run's and over the bar at every point, and no arm within "
                         f"{FLOOR:.2f} of chance" if ok else
                         f"FALSIFIER FIRED -- bands { {k: bands[k] for k in bands} } (needing {ARMS_NEEDED}), arms "
                         f"within {FLOOR:.2f} of chance: {floor_hits}"}
    #: UA4 -- the map travels further when paid harder
    if not r.get("travel"):
        j4 = {"id": "UA4", "measured": "the map's distance from the identity is not readable at both ends of the curve",
              "verdict": "REFUSED -- a new run is absent, or records no policy movement, so the map's travel is not "
                         "compared"}
    else:
        up = _up(r["travel"], ARMS)
        ok = len(up) >= ARMS_NEEDED
        j4 = {"id": "UA4",
              "measured": f"the map's distance from the identity at 0.01 less its distance at 0.001, paired over the "
                          f"replicates: **{ {a: round(r['travel'][a]['mean'], PLACES) for a in ARMS} }** at "
                          f"**{ {a: round(r['travel'][a]['sigma'], 2) for a in ARMS} }** sigma, from the means 0.001 "
                          f"**{ {a: s['map_move']['small'][a]['mean'] for a in ARMS} }** and 0.01 "
                          f"**{ {a: s['map_move']['large'][a]['mean'] for a in ARMS} }**",
              "verdict": f"MET -- the map travels further when paid harder: **{len(up)}** of three arms resolve upward "
                         f"({up}) at {SIGMA:.0f} sigma" if ok else
                         f"FALSIFIER FIRED -- **{len(up)}** of three arms resolve upward ({up}) at {SIGMA:.0f} sigma"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== how hard the map is paid ==")
    rolls = r["runs"]
    if not r["spans"]["readable"]["mid"]:
        print("   REFUSED -- the run's-own-rate point is absent, so the curve has no middle")
    if rolls.get("small") is None or rolls.get("large") is None:
        print("   REFUSED -- one of the two new runs is absent, so the curve has no end")
    else:
        print("   every earned run in this corpus ascends the payout at the run's own `--lr`; this gives the map")
        print("   its own rate and reads the same pass at 0.001, 0.003 (`e500`'s own) and 0.01")
        print(f"\n   {'point':<8} {'reward diag':>34} {'accuracy diag':>34} {'map move':>26}")
        print(f"   {'':<8} " + " ".join(f"{a:>10}" for a in ARMS) + "  " + " ".join(f"{a:>10}" for a in ARMS)
              + "  " + " ".join(f"{a:>8}" for a in ARMS))
        for k in ("small", "mid", "large"):
            rw = r["spans"]["reward_diagonal"][k]
            ac = r["spans"]["accuracy_diagonal"][k]
            mv = r["spans"]["map_move"][k]
            print(f"   {k:<8} " + " ".join(f"{rw[a]:>10.4f}" if rw else f"{'':>10}" for a in ARMS) + "  "
                  + " ".join(f"{ac[a]:>10.4f}" for a in ARMS) + "  "
                  + " ".join(f"{mv[a]['mean']:>8.4f}" if mv else f"{'':>8}" for a in ARMS))
        print(f"   meter    " + " ".join(f"{r['spans']['reward_diagonal']['meter'][a]:>10.4f}"
                                         if r["spans"]["reward_diagonal"]["meter"] else f"{'':>10}" for a in ARMS))
        for k in ("small", "large"):
            g = r["spans"]["reward_gain"][k]
            if g is not None:
                print(f"   {k} against the run's own rate: "
                      + ", ".join(f"{a} {g[a]['mean']:+.4f} at {g[a]['sigma']:+.2f} sigma" for a in ARMS))
        if r["spans"]["travel"] is not None:
            print("   the map's travel, 0.01 less 0.001: "
                  + ", ".join(f"{a} {r['spans']['travel'][a]['mean']:+.4f} at "
                              f"{r['spans']['travel'][a]['sigma']:+.2f} sigma" for a in ARMS))
        for k in ("small", "mid", "large"):
            sh = r["spans"]["reward_shape"][k]
            if sh is not None:
                print(f"   the {k} point's reward diagonal less its own last row: "
                      + ", ".join(f"{a} {sh[a]['mean']:+.4f} at {sh[a]['sigma']:+.2f} sigma" for a in ARMS))
    print("\n== the registered claims, UA1-UA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
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
