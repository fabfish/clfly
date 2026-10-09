"""E475 -- the held-out reading in a second world: whether the change survives a redraw of the world.

Every finding of the held-out line closes on the same bullet, and `e474` made it the last one standing:
*one world* -- the four draws it read are four cue sets **inside one world**, so a redraw of the world is a
different axis and not that one. `e474` also showed that both the **level** and the **change** are the draw's
(**0.1281** and **0.0958** apart, four of the six pairs of draws resolving), so what the card's `holdout` clause
carries is one draw's change **in one world**.

**This unit redraws the world.** The same configuration as the four world-0 rolls with the environment's own
seed moved -- `--loop-seed 1` against the default `0` -- at the same four held-out draws (**3**, **7**, **11**,
**19**), the same hundred updates, the same head and both anchors. The read-out subset, the circuit, the net's
own seed and the three tasks' label sequences are held: the environment's populations, its cue templates and
its three maps are what move. Four claims, registered before either world-1 roll's reading was opened.

- **BA1 -- and the second world is one configuration with the first except the world's own seed.** At each draw
  and side every recorded config field agrees between the two worlds except `loop_seed`, the held-out seed, the
  output path and the saved weights; `loop_seed` is **1** on the new rolls against **null** on the old; and
  **within** world 1 the sequence's own replicates are **bit-identical** across the four draws on every arm the
  four rolls share. **Falsifier**: any other field differing, `loop_seed` not being 1 against null, or any
  shared trained replicate differing within world 1.
- **BA2 -- and the change resolves at every draw in the second world.** At each of world 1's four draws the
  baseline's paired trained-minus-initial reading is positive at **two** sigma or more. **Falsifier**: under two
  sigma, or negative, at any draw.
- **BA3 -- and the change is not the world's.** At each of the four held-out seeds the world-1 change and the
  world-0 change differ by under **two** sigma, paired across the replicates the two rolls share. **Falsifier**:
  any matched draw resolving. *This is the bullet every held-out finding names as unmeasured.*
- **BA4 -- and the draws disagree in the second world too.** Within world 1 every pair of draws' changes differs
  by under **two** sigma, paired. **Falsifier**: any pair resolving. *`e474`'s AA3, which FIRED at world 0, asked
  again one world over.*

**What it can do beyond that.** It closes the last bullet of the held-out line: if the change agrees across the
two worlds the sequence's contribution to an unseen cue set is a property of the task and not of the environment
it is read in, and if it does not, every held-out number this corpus has published is one world's.

**What it cannot do.** *Two worlds are not a population*: a second world is one more sample of the environment
and not its sd. *And a probe is not a task*: every level and every change is of **linear readability** from the
frozen body. *And one ridge*: **1e-2** is `e469`'s. *And one budget*: all eight rolls are at a hundred updates,
so the crossings `e467` and `e468` found on the sequence's own diagonal are not measured here. *And the world is
one field*: `--loop-seed` redraws the environment's populations, templates and maps together, so which of them
the movement (if any) rides on is not separated.
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

#: the first world's four draws, by draw and side, at the same hundred updates and the same head
WORLD0 = {
    "3/bio": Path("runs/e471_earned_label_neurons_holdout_iters100_20reps.json"),
    "3/rand": Path("runs/e471_earned_label_rand_neurons_holdout_iters100_20reps.json"),
    "7/bio": Path("runs/e473_earned_label_neurons_holdout_iters100_seed7_20reps.json"),
    "7/rand": Path("runs/e473_earned_label_rand_neurons_holdout_iters100_seed7_20reps.json"),
    "11/bio": Path("runs/e474_earned_label_neurons_holdout_iters100_seed11_20reps.json"),
    "11/rand": Path("runs/e474_earned_label_rand_neurons_holdout_iters100_seed11_20reps.json"),
    "19/bio": Path("runs/e474_earned_label_neurons_holdout_iters100_seed19_20reps.json"),
    "19/rand": Path("runs/e474_earned_label_rand_neurons_holdout_iters100_seed19_20reps.json"),
}
#: the second world: the same eight rolls with the environment's own seed at 1, and nothing else moved
WORLD1 = {
    "3/bio": Path("runs/e475_earned_label_bio_neurons_holdout_w1_iters100_seed3_20reps.json"),
    "3/rand": Path("runs/e475_earned_label_rand_neurons_holdout_w1_iters100_seed3_20reps.json"),
    "7/bio": Path("runs/e475_earned_label_bio_neurons_holdout_w1_iters100_seed7_20reps.json"),
    "7/rand": Path("runs/e475_earned_label_rand_neurons_holdout_w1_iters100_seed7_20reps.json"),
    "11/bio": Path("runs/e475_earned_label_bio_neurons_holdout_w1_iters100_seed11_20reps.json"),
    "11/rand": Path("runs/e475_earned_label_rand_neurons_holdout_w1_iters100_seed11_20reps.json"),
    "19/bio": Path("runs/e475_earned_label_bio_neurons_holdout_w1_iters100_seed19_20reps.json"),
    "19/rand": Path("runs/e475_earned_label_rand_neurons_holdout_w1_iters100_seed19_20reps.json"),
}
WORLDS = {"w0": WORLD0, "w1": WORLD1}
DRAWS = ("3", "7", "11", "19")
SEEDS = {"3": 3, "7": 7, "11": 11, "19": 19}
SIDES = ("bio", "rand")
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
#: what a roll's config may differ in **within** one world
IGNORED = ("loop_holdout_seed", "json_out", "save_theta")
#: and what it may additionally differ in **between** the two worlds
IGNORED_ACROSS = IGNORED + ("loop_seed",)
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
CLAIMS = (
    ("BA1", f"and the second world is one configuration with the first except the world's own seed, at {MIN_REPS} "
            f"replicates",
     "At each draw and side every recorded config field agrees across the two worlds except loop_seed, the held-out "
     "seed, the output path and the saved weights; loop_seed is 1 on the new rolls against null on the old; and "
     "within world 1 the sequence's own replicates are bit-identical across the four draws on every shared arm",
     "falsifier: any other field differing, loop_seed not being 1 against null, or any shared trained replicate "
     "differing within world 1"),
    ("BA2", f"and the change resolves at every draw in the second world, at {SIGMA:.0f} sigma",
     "At each of world 1's four draws the baseline's paired trained minus initial reading is positive at two sigma or "
     "more",
     "falsifier: under two sigma, or negative, at any draw"),
    ("BA3", f"and the change is not the world's, under {SIGMA:.0f} sigma",
     "At each of the four held-out seeds the world-1 change and the world-0 change differ by under two sigma, paired "
     "across the replicates the two rolls share",
     "falsifier: any matched draw resolving"),
    ("BA4", f"and the draws disagree in the second world too, under {SIGMA:.0f} sigma",
     "Within world 1 every pair of draws' changes differs by under two sigma, paired across the replicates the two "
     "rolls share",
     "falsifier: any pair resolving"),
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
            "loop_seed": cfg.get("loop_seed"),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED_ACROSS))}}


def reading(worlds: dict = WORLDS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "cross": {}, "identical": {}, "curve": {},
           "levels": {}, "pairs": {}, "worlds": {}, "spans": {}}
    for world, runs in worlds.items():
        for label, path in runs.items():
            got = _roll(path, ANCHOR_OF[label.split("/")[1]])
            if got is None:
                return {**out, "ok": False,
                        "reason": f"roll {world}/{label}: {path} is absent, carries no "
                                  f"{ANCHOR_OF[label.split('/')[1]]} arm, or carries no holdout block"}
            out["runs"][f"{world}/{label}"] = got
    #: **within** a world: the four draws must be one configuration with the held-out seed moved
    for side in SIDES:
        base = out["runs"][f"w1/{DRAWS[0]}/{side}"]
        for draw in DRAWS[1:]:
            roll = out["runs"][f"w1/{draw}/{side}"]
            for k in sorted(set(roll["config"]) | set(base["config"])):
                out["same"][f"{side}.{k}"] = out["same"].get(f"{side}.{k}", True) and \
                    roll["config"].get(k) == base["config"].get(k)
            for k in SHARED:
                out["same"][f"{side}.{k}"] = out["same"].get(f"{side}.{k}", True) and \
                    roll["shared"].get(k) == base["shared"].get(k)
        shared_arms = sorted(set.intersection(*[set(out["runs"][f"w1/{d}/{side}"]["arms"]) for d in DRAWS]))
        for arm in shared_arms:
            groups = [out["runs"][f"w1/{d}/{side}"]["arms"][arm]["records"] for d in DRAWS]
            out["identical"][f"{side}:{arm}"] = _identical(groups)
    #: **between** the worlds: at each draw and side the config must agree except the world's own seed
    for draw in DRAWS:
        for side in SIDES:
            a = out["runs"][f"w0/{draw}/{side}"]
            b = out["runs"][f"w1/{draw}/{side}"]
            for k in sorted(set(a["config"]) | set(b["config"])):
                out["cross"][f"{draw}/{side}.{k}"] = out["cross"].get(f"{draw}/{side}.{k}", True) and \
                    a["config"].get(k) == b["config"].get(k)
            for k in SHARED:
                out["cross"][f"{draw}/{side}.{k}"] = out["cross"].get(f"{draw}/{side}.{k}", True) and \
                    a["shared"].get(k) == b["shared"].get(k)
    #: the manipulation's own check: the world moved, so the sequence's replicates must **not** be identical
    for draw in DRAWS:
        for side in SIDES:
            for arm in sorted(set(out["runs"][f"w0/{draw}/{side}"]["arms"]) &
                              set(out["runs"][f"w1/{draw}/{side}"]["arms"])):
                got = _identical([out["runs"][f"w0/{draw}/{side}"]["arms"][arm]["records"],
                                  out["runs"][f"w1/{draw}/{side}"]["arms"][arm]["records"]])
                out["worlds"].setdefault("identical_across", {})[f"{draw}/{side}:{arm}"] = got["equal"]
    for world in WORLDS:
        out["curve"][world] = {}
        for draw in DRAWS:
            out["curve"][world][draw] = {}
            for side in SIDES:
                roll = out["runs"][f"{world}/{draw}/{side}"]
                b = roll["arms"][BASELINE]
                out["curve"][world][draw][side] = {
                    "draw": SEEDS[draw], "side": side, "world": world, "loop_seed": roll["loop_seed"],
                    "anchor": roll["anchor"],
                    "initial": statistics.fmean(b["before"]), "trained": statistics.fmean(b["after"]),
                    "change": _paired(b["after"], b["before"]),
                    "arms": {arm: {"initial": statistics.fmean(got["before"]),
                                   "trained": statistics.fmean(got["after"]),
                                   "change": _paired(got["after"], got["before"]),
                                   "against_baseline": _paired(got["after"], b["after"])}
                             for arm, got in roll["arms"].items()},
                }
    #: the world axis at each matched draw, and the draw axis within each world
    for draw in DRAWS:
        out["pairs"][f"world/{draw}"] = {}
        for side in SIDES:
            a = out["runs"][f"w0/{draw}/{side}"]["arms"][BASELINE]
            b = out["runs"][f"w1/{draw}/{side}"]["arms"][BASELINE]
            out["pairs"][f"world/{draw}"][side] = {
                "level": _paired(b["after"], a["after"]),
                "initial": _paired(b["before"], a["before"]),
                "change": _paired([p - q for p, q in zip(b["before"], b["after"])],
                                  [p - q for p, q in zip(a["before"], a["after"])]),
            }
    for world in WORLDS:
        for side in SIDES:
            levels = {d: out["curve"][world][d][side]["trained"] for d in DRAWS}
            changes = {d: out["curve"][world][d][side]["change"]["mean"] for d in DRAWS}
            pa = {}
            for x, y in itertools.combinations(DRAWS, 2):
                a = out["runs"][f"{world}/{x}/{side}"]["arms"][BASELINE]
                b = out["runs"][f"{world}/{y}/{side}"]["arms"][BASELINE]
                pa[f"{x}-{y}"] = {"level": _paired(b["after"], a["after"]),
                                  "change": _paired([p - q for p, q in zip(b["before"], b["after"])],
                                                    [p - q for p, q in zip(a["before"], a["after"])])}
            out["levels"][f"{world}/{side}"] = {
                "trained": levels, "change": changes,
                "level_spread": max(levels.values()) - min(levels.values()),
                "change_spread": max(changes.values()) - min(changes.values()),
            }
            out["pairs"].setdefault(f"draw/{world}", {})[side] = pa
    counts = sorted({tuple(got["arms"][arm][k]) for got in out["runs"].values()
                     for arm in got["arms"] for k in ("task", "n_train", "n_eval")}, key=repr)
    thin = {label: v["replicates"] for label, roll in out["runs"].items()
            for arm, v in roll["arms"].items() if v["replicates"] < MIN_REPS}
    across = out["worlds"].get("identical_across", {})
    out["spans"] = {
        "worlds": list(WORLDS), "draws": list(DRAWS), "seeds": {d: SEEDS[d] for d in DRAWS}, "sides": list(SIDES),
        "runs": len(out["runs"]), "same_fields": len(out["same"]), "cross_fields": len(out["cross"]),
        "counts": counts, "thin": thin, "identical": len(out["identical"]),
        "identical_equal": sum(1 for v in out["identical"].values() if v["equal"]),
        "across_worlds": len(across), "across_worlds_equal": sum(1 for v in across.values() if v),
        "world_seeds": {w: sorted({roll["loop_seed"] for label, roll in out["runs"].items()
                                   if label.startswith(w + "/")}, key=repr) for w in WORLDS},
        "held_out_seeds": sorted({got["seed"] for got in out["runs"].values()}),
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
    cross_differ = sorted(k for k, v in r["cross"].items() if not v)
    not_id = sorted(k for k, v in r["identical"].items() if not v["equal"])
    seeds_ok = sorted(s["held_out_seeds"]) == sorted(SEEDS.values())
    worlds_ok = s["world_seeds"] == {"w0": [None], "w1": [1]}
    j1 = {"id": "BA1",
          "measured": f"{s['runs']} rolls at {s['replicates']} replicates over {s['same_fields']} fields compared "
                      f"within the second world and {s['cross_fields']} between the worlds; the world seeds "
                      f"{s['world_seeds']}, the held-out seeds {s['held_out_seeds']}; {s['identical_equal']} of "
                      f"{s['identical']} shared trained arms bit-identical across the four draws **within** world 1, "
                      f"and {s['across_worlds_equal']} of {s['across_worlds']} identical **between** the worlds",
          "verdict": "MET -- one configuration with the world's own seed moved, and the sequence one draw's inside it"
                     if (not differ and not cross_differ and seeds_ok and worlds_ok and not not_id and not s["thin"]
                         and not s["short"]) else
                     f"FALSIFIER FIRED -- differing within {differ[:6]}, between {cross_differ[:6]}, seeds "
                     f"{s['held_out_seeds']}, world seeds {s['world_seeds']}, not identical {not_id[:4]}, thin "
                     f"{s['thin']}, short {s['short']}"}
    ch = {side: {d: r["curve"]["w1"][d][side]["change"] for d in DRAWS} for side in SIDES}
    worst = min((ch[side][d]["sigma"] for side in SIDES for d in DRAWS), default=0.0)
    j2 = {"id": "BA2",
          "measured": f"in the second world the baseline's change by draw is "
                      f"{ {side: {d: round(ch[side][d]['mean'], 4) for d in DRAWS} for side in SIDES} } at "
                      f"{ {side: {d: round(ch[side][d]['sigma'], 2) for d in DRAWS} for side in SIDES} } sigma",
          "verdict": f"MET -- the sequence raises the unseen cue set's decodability in the second world too, the "
                     f"weakest at {worst:.2f} sigma" if worst >= SIGMA else
                     f"FALSIFIER FIRED -- the weakest draw in the second world is {worst:.2f} sigma"}
    w = {d: {side: r["pairs"][f"world/{d}"][side]["change"] for side in SIDES} for d in DRAWS}
    bad3 = sorted(f"{d}/{side}" for d in DRAWS for side in SIDES if abs(w[d][side]["sigma"]) >= SIGMA)
    widest3 = max((abs(w[d][side]["sigma"]) for d in DRAWS for side in SIDES), default=0.0)
    j3 = {"id": "BA3",
          "measured": f"at each held-out seed the two worlds' changes differ by "
                      f"{ {side: {d: round(w[d][side]['mean'], 4) for d in DRAWS} for side in SIDES} } at "
                      f"{ {side: {d: round(w[d][side]['sigma'], 2) for d in DRAWS} for side in SIDES} } sigma, the "
                      f"widest |sigma| being {widest3:.2f}",
          "verdict": "MET -- the change is the task's and not the world's, at all four matched draws" if not bad3 else
                     f"FALSIFIER FIRED -- {bad3}"}
    bad4 = sorted(f"{side}/{k}" for side in SIDES for k, v in r["pairs"]["draw/w1"][side].items()
                  if abs(v["change"]["sigma"]) >= SIGMA)
    widest4 = max((abs(v["change"]["sigma"]) for side in SIDES
                   for v in r["pairs"]["draw/w1"][side].values()), default=0.0)
    j4 = {"id": "BA4",
          "measured": f"within the second world the {len(r['pairs']['draw/w1'][SIDES[0]])} pairs of draws differ in "
                      f"their changes by "
                      f"{ {side: {k: round(v['change']['mean'], 4) for k, v in r['pairs']['draw/w1'][side].items()} for side in SIDES} } "
                      f"at "
                      f"{ {side: {k: round(v['change']['sigma'], 2) for k, v in r['pairs']['draw/w1'][side].items()} for side in SIDES} } "
                      f"sigma, the widest |sigma| being {widest4:.2f}",
          "verdict": "MET -- the draws agree on the change in the second world too" if not bad4 else
                     f"FALSIFIER FIRED -- {bad4}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the held-out reading in a second world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the same circuit, read-out draw, net seed and label sequences as the four world-0 rolls, with the")
    print("   environment's own seed at 1 against the default 0: the world redrawn and the held-out seed moved")
    print(f"\n   {'world/draw/side/arm':<26} {'initial':>8} {'trained':>8} {'change':>8} {'sigma':>7} {'vs base':>9} "
          f"{'sigma':>7}")
    for world in WORLDS:
        for d in DRAWS:
            for side in SIDES:
                cell = r["curve"][world][d][side]
                for arm in (BASELINE, cell["anchor"], BUFFER):
                    got = cell["arms"][arm]
                    vs = got["against_baseline"]
                    print(f"   {world + '/' + d + '/' + side + '/' + arm:<26} {got['initial']:>8.4f} "
                          f"{got['trained']:>8.4f} {got['change']['mean']:>+8.4f} {got['change']['sigma']:>7.2f} " +
                          (f"{vs['mean']:>+9.4f} {vs['sigma']:>7.2f}" if arm != BASELINE else f"{'-':>9} {'-':>7}"))
    print("\n   the world axis, at each matched held-out seed:")
    for d in DRAWS:
        got = r["pairs"][f"world/{d}"]
        print(f"      seed {d}: change w1 - w0 " +
              ", ".join(f"{side} {got[side]['change']['mean']:+.4f} ({got[side]['change']['sigma']:+.2f}s)"
                        for side in SIDES))
    print("\n   the draw axis, within each world:")
    for world in WORLDS:
        for side in SIDES:
            lv = r["levels"][f"{world}/{side}"]
            print(f"      {world}/{side}: changes " + ", ".join(f"{d} {lv['change'][d]:+.4f}" for d in DRAWS) +
                  f"  spread {lv['change_spread']:.4f}  (levels spread {lv['level_spread']:.4f})")
    print(f"\n   the sequence's replicates bit-identical within world 1: {r['spans']['identical_equal']} of "
          f"{r['spans']['identical']}; and between the worlds: "
          f"{r['spans']['across_worlds_equal']} of {r['spans']['across_worlds']} identical")
    print("\n== the registered claims, BA1-BA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e474` read four draws of the held-out cue set in one world and closed on *one world*;")
    print("    this is the world the line had not drawn)")
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
