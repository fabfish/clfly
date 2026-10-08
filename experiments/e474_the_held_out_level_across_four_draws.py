"""E474 -- the held-out level across four draws: the spread of the level and the spread of the change.

`e473` drew the held-out cue set twice and found the two draws' **levels** **0.1281** apart while their **changes** agree
to **-0.0031** at **0.19** sigma, and it closed on *two draws are not a population: the reading's spread over the family
of fourth cue sets is estimated from two of them*. **Two draws give one difference and not a spread.**

**This unit draws it twice more.** Two further held-out seeds (**11** and **19**) at the same hundred updates, the same
head and both anchors, read beside the draws **3** and **7**, so the level has four points and the change has four. Four
claims, registered before either new draw's reading was opened.

- **AA1 -- and the four draws are one configuration with the held-out seed moved.** Every recorded config field agrees
  across the draws except the held-out seed, the output path and the saved weights; the seeds are **3**, **7**, **11**
  and **19**; and the sequence's own replicates are **bit-identical** across all four draws on every arm the four rolls
  share. **Falsifier**: any other field differing, the seeds not being those four, or any shared trained replicate
  differing.
- **AA2 -- and every draw's change resolves.** At each of the four draws the baseline's paired trained minus initial
  reading is positive at **two** sigma or more. **Falsifier**: under two sigma, or negative, at any draw.
- **AA3 -- and the four draws' changes agree.** Every pair of draws' changes differs by under **two** sigma, paired
  across the replicates the two rolls share. **Falsifier**: any pair resolving. *This is `e473`'s agreement with four
  points instead of two.*
- **AA4 -- and the level moves more between draws than the change does.** The spread of the four baseline **trained
  readings** -- the largest minus the smallest -- exceeds the spread of the four **changes**. **Falsifier**: the level's
  spread not exceeding the change's. *`e473`'s sentence with the two spreads beside each other rather than one
  difference and one contrast.*

**What it can do beyond that.** It makes the level's draw-dependence a **spread** rather than a difference, and it says
which of the two quantities a reader of the card's `holdout` clause is reading: the clause carries both, and only one of
them is the task's.

**What it cannot do.** *Four draws are still not the population*: the spread is the range of four samples of the fourth
cue set and not its sd, and two of the four seeds were chosen by this unit rather than drawn at random. *And a probe is
not a task*: every level and every change is of **linear readability** from the frozen body. *And one ridge*: **1e-2**
is `e469`'s. *And one budget*: all four draws are at a hundred updates, so the crossings `e467` and `e468` found on the
sequence's own diagonal are not measured at any of them. *And one world*: the four draws are four cue sets inside the
same world, so a redraw of the world is a different axis and not this one.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the four draws of the held-out task, by draw and side, at the same hundred updates and the same head
RUNS = {
    "3/bio": Path("runs/e471_earned_label_neurons_holdout_iters100_20reps.json"),
    "3/rand": Path("runs/e471_earned_label_rand_neurons_holdout_iters100_20reps.json"),
    "7/bio": Path("runs/e473_earned_label_neurons_holdout_iters100_seed7_20reps.json"),
    "7/rand": Path("runs/e473_earned_label_rand_neurons_holdout_iters100_seed7_20reps.json"),
    "11/bio": Path("runs/e474_earned_label_neurons_holdout_iters100_seed11_20reps.json"),
    "11/rand": Path("runs/e474_earned_label_rand_neurons_holdout_iters100_seed11_20reps.json"),
    "19/bio": Path("runs/e474_earned_label_neurons_holdout_iters100_seed19_20reps.json"),
    "19/rand": Path("runs/e474_earned_label_rand_neurons_holdout_iters100_seed19_20reps.json"),
}
DRAWS = ("3", "7", "11", "19")
SEEDS = {"3": 3, "7": 7, "11": 11, "19": 19}
SIDES = ("bio", "rand")
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
IGNORED = ("loop_holdout_seed", "json_out", "save_theta")
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
CLAIMS = (
    ("AA1", f"and the four draws are one configuration with the held-out seed moved, at {MIN_REPS} replicates",
     "Every recorded config field agrees across the draws except the held-out seed, the output path and the saved "
     "weights; the seeds are 3, 7, 11 and 19; and the sequence's own replicates are bit-identical across all four draws "
     "on every arm the four rolls share",
     "falsifier: any other field differing, the seeds not being those four, or any shared trained replicate differing"),
    ("AA2", f"and every draw's change resolves, at {SIGMA:.0f} sigma",
     "At each of the four draws the baseline's paired trained minus initial reading is positive at two sigma or more",
     "falsifier: under two sigma, or negative, at any draw"),
    ("AA3", f"and the four draws' changes agree, under {SIGMA:.0f} sigma",
     "Every pair of draws' changes differs by under two sigma, paired across the replicates the two rolls share",
     "falsifier: any pair resolving"),
    ("AA4", "and the level moves more between draws than the change does",
     "The spread of the four baseline trained readings exceeds the spread of the four changes",
     "falsifier: the level's spread not exceeding the change's"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _records(got: dict) -> list:
    return [{"final_per_task": list(r["final_per_task"]), "mean_forgetting": r["mean_forgetting"]}
            for r in (got or {}).get("replicates") or []]


def _identical(groups: list) -> dict:
    """Whether every one of these replicate lists is the same, record for record."""
    n = len(groups)
    if n < 2 or len({len(g) for g in groups}) != 1:
        return {"equal": False, "n": 0, "agrees": sum(1 for g in groups[1:] if g == groups[0])}
    same = all(g == groups[0] for g in groups[1:])
    return {"equal": same, "n": len(groups[0]), "agrees": sum(1 for g in groups[1:] if g == groups[0])}


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        reps = (methods.get(arm) or {}).get("replicates") or []
        blocks = [r.get("holdout") for r in reps]
        if not reps or any(b is None for b in blocks):
            return None
        arms[arm] = {"replicates": len(reps), "before": [b["before"] for b in blocks],
                     "after": [b["after"] for b in blocks],
                     "task": sorted({b.get("task") for b in blocks}),
                     "n_train": sorted({b.get("n_train") for b in blocks}),
                     "n_eval": sorted({b.get("n_eval") for b in blocks}),
                     "records": _records(methods[arm])}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "seed": cfg.get("loop_holdout_seed") if cfg.get("loop_holdout_seed") is not None else SEEDS["3"],
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "curve": {}, "levels": {},
           "pairs": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label.split("/")[1]])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent, carries no {ANCHOR_OF[label.split('/')[1]]} arm, or "
                              f"carries no holdout block"}
        out["runs"][label] = got
    for side in SIDES:
        base = out["runs"][f"{DRAWS[0]}/{side}"]
        for draw in DRAWS[1:]:
            roll = out["runs"][f"{draw}/{side}"]
            fields = sorted(set(roll["config"]) | set(base["config"]))
            for k in fields:
                out["same"][f"{side}.{k}"] = out["same"].get(f"{side}.{k}", True) and \
                    roll["config"].get(k) == base["config"].get(k)
            out["same"][f"{side}.circuit"] = out["same"].get(f"{side}.circuit", True) and \
                roll["shared"].get("circuit") == base["shared"].get("circuit")
            out["same"][f"{side}.tasks"] = out["same"].get(f"{side}.tasks", True) and \
                roll["shared"].get("tasks") == base["shared"].get("tasks")
        shared_arms = sorted(set.intersection(*[set(out["runs"][f"{d}/{side}"]["arms"]) for d in DRAWS]))
        for arm in shared_arms:
            groups = [out["runs"][f"{d}/{side}"]["arms"][arm]["records"] for d in DRAWS]
            out["identical"][f"{side}:{arm}"] = _identical(groups)
    for draw in DRAWS:
        out["curve"][draw] = {}
        for side in SIDES:
            roll = out["runs"][f"{draw}/{side}"]
            b = roll["arms"][BASELINE]
            out["curve"][draw][side] = {
                "draw": SEEDS[draw], "side": side, "anchor": roll["anchor"],
                "initial": statistics.fmean(b["before"]), "trained": statistics.fmean(b["after"]),
                "change": _paired(b["after"], b["before"]),
                "arms": {arm: {"initial": statistics.fmean(got["before"]),
                               "trained": statistics.fmean(got["after"]),
                               "change": _paired(got["after"], got["before"]),
                               "against_baseline": _paired(got["after"], b["after"])}
                         for arm, got in roll["arms"].items()},
            }
    for side in SIDES:
        levels = {d: out["curve"][d][side]["trained"] for d in DRAWS}
        changes = {d: out["curve"][d][side]["change"]["mean"] for d in DRAWS}
        pa = {}
        for x, y in itertools.combinations(DRAWS, 2):
            a = out["runs"][f"{x}/{side}"]["arms"][BASELINE]
            b = out["runs"][f"{y}/{side}"]["arms"][BASELINE]
            pa[f"{x}-{y}"] = {"level": _paired(b["after"], a["after"]),
                              "change": _paired([p - q for p, q in zip(b["before"], b["after"])],
                                                [p - q for p, q in zip(a["before"], a["after"])])}
        out["levels"][side] = {
            "trained": levels, "change": changes,
            "level_spread": max(levels.values()) - min(levels.values()),
            "change_spread": max(changes.values()) - min(changes.values()),
            "level_sd": statistics.stdev(list(levels.values())),
            "change_sd": statistics.stdev(list(changes.values())),
        }
        out["pairs"][side] = pa
    counts = sorted({tuple(got["arms"][arm][k]) for got in out["runs"].values()
                     for arm in got["arms"] for k in ("task", "n_train", "n_eval")}, key=repr)
    thin = {label: v["replicates"] for label, roll in out["runs"].items()
            for arm, v in roll["arms"].items() if v["replicates"] < MIN_REPS}
    out["spans"] = {
        "draws": list(DRAWS), "seeds": {d: SEEDS[d] for d in DRAWS}, "sides": list(SIDES),
        "runs": len(out["runs"]), "same_fields": len(out["same"]), "counts": counts, "thin": thin,
        "identical": len(out["identical"]),
        "identical_equal": sum(1 for v in out["identical"].values() if v["equal"]),
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "short": {label: sorted(roll["arms"]) for label, roll in out["runs"].items() if len(roll["arms"]) < N_ARMS},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no holdout block"}
                for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_id = sorted(k for k, v in r["identical"].items() if not v["equal"])
    seeds_ok = sorted(set(s["seeds"].values())) == sorted(SEEDS.values())
    j1 = {"id": "AA1",
          "measured": f"{s['runs']} rolls at {s['replicates']} replicates over {s['same_fields']} compared fields, the "
                      f"held-out seeds {s['seeds']}, and {s['identical_equal']} of {s['identical']} shared trained arms "
                      f"bit-identical across all four draws",
          "verdict": "MET -- one configuration with the held-out seed moved and the sequence one draw's" if
                     (not differ and seeds_ok and not not_id and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, seeds {s['seeds']}, not identical {not_id[:4]}, "
                     f"thin {s['thin']}, short {s['short']}"}
    ch = {side: {d: r["curve"][d][side]["change"] for d in DRAWS} for side in SIDES}
    worst = min((ch[side][d]["sigma"] for side in SIDES for d in DRAWS), default=0.0)
    j2 = {"id": "AA2",
          "measured": f"the baseline's change by draw is "
                      f"{ {side: {d: round(ch[side][d]['mean'], 4) for d in DRAWS} for side in SIDES} } at "
                      f"{ {side: {d: round(ch[side][d]['sigma'], 2) for d in DRAWS} for side in SIDES} } sigma",
          "verdict": f"MET -- the sequence raises the unseen cue set's decodability at all four draws, the weakest at "
                     f"{worst:.2f} sigma" if worst >= SIGMA else
                     f"FALSIFIER FIRED -- the weakest draw is {worst:.2f} sigma"}
    bad = sorted(f"{side}/{k}" for side in SIDES for k, v in r["pairs"][side].items()
                 if abs(v["change"]["sigma"]) >= SIGMA)
    widest = max((abs(v["change"]["sigma"]) for side in SIDES for v in r["pairs"][side].values()), default=0.0)
    j3 = {"id": "AA3",
          "measured": f"the {len(r['pairs'][SIDES[0]])} pairs of draws differ in their changes by "
                      f"{ {side: {k: round(v['change']['mean'], 4) for k, v in r['pairs'][side].items()} for side in SIDES} } "
                      f"at { {side: {k: round(v['change']['sigma'], 2) for k, v in r['pairs'][side].items()} for side in SIDES} } "
                      f"sigma, the widest |sigma| being {widest:.2f}",
          "verdict": "MET -- every pair of draws agrees on the change" if not bad else
                     f"FALSIFIER FIRED -- {bad}"}
    lv = r["levels"]
    ok = all(lv[side]["level_spread"] > lv[side]["change_spread"] for side in SIDES)
    j4 = {"id": "AA4",
          "measured": f"the four draws' baseline **trained readings** spread "
                      f"{ {side: round(lv[side]['level_spread'], 4) for side in SIDES} } (sd "
                      f"{ {side: round(lv[side]['level_sd'], 4) for side in SIDES} }) while their **changes** spread "
                      f"{ {side: round(lv[side]['change_spread'], 4) for side in SIDES} } (sd "
                      f"{ {side: round(lv[side]['change_sd'], 4) for side in SIDES} }), from levels "
                      f"{ {side: {d: round(lv[side]['trained'][d], 4) for d in DRAWS} for side in SIDES} }",
          "verdict": "MET -- the level is the draw's and the change is the task's, four draws deep" if ok else
                     f"FALSIFIER FIRED -- the level's spread does not exceed the change's: "
                     f"{ {side: (lv[side]['level_spread'], lv[side]['change_spread']) for side in SIDES} }"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the held-out level across four draws ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the same world, the same hundred updates and the same head, with the held-out cue set's own seed moved")
    print("   across four values: the sequence's three cue sets are one draw and every other field is held")
    print(f"\n   {'draw/side/arm':<22} {'initial':>8} {'trained':>8} {'change':>8} {'sigma':>7} {'vs base':>9} "
          f"{'sigma':>7}")
    for d in DRAWS:
        for side in SIDES:
            cell = r["curve"][d][side]
            for arm in (BASELINE, cell["anchor"], BUFFER):
                got = cell["arms"][arm]
                vs = got["against_baseline"]
                print(f"   {d + '/' + side + '/' + arm:<22} {got['initial']:>8.4f} {got['trained']:>8.4f} "
                      f"{got['change']['mean']:>+8.4f} {got['change']['sigma']:>7.2f} " +
                      (f"{vs['mean']:>+9.4f} {vs['sigma']:>7.2f}" if arm != BASELINE else f"{'-':>9} {'-':>7}"))
    lv = r["levels"]
    print("\n   the level and the change, draw by draw:")
    for side in SIDES:
        print(f"      {side}: levels " + ", ".join(f"{d} {lv[side]['trained'][d]:.4f}" for d in DRAWS) +
              f"  spread {lv[side]['level_spread']:.4f}")
        print(f"      {side}: changes " + ", ".join(f"{d} {lv[side]['change'][d]:+.4f}" for d in DRAWS) +
              f"  spread {lv[side]['change_spread']:.4f}")
    print(f"\n   shared trained arms bit-identical across the four draws: {r['spans']['identical_equal']} of "
          f"{r['spans']['identical']}")
    print("\n== the registered claims, AA1-AA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e473` drew the held-out cue set twice and found the level 0.1281 apart while the changes agree;")
    print("    two draws are one difference, and this is a spread)")
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
