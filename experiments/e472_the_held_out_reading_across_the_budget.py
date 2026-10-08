"""E472 -- the held-out reading across the budget: where the twelve thousandths arrive.

`e471` moved the held-out task to a fifth of the card's budget and found the probe going **0.6875** to **0.7594** there
-- a paired **+0.0719** at **4.89** sigma -- with the remaining four hundred updates adding **+0.0125**, which it reads
at **0.89** sigma and cannot separate from a redraw. It closed on *two budgets are not a curve: the budgets between
them, where the twelve thousandths must actually arrive, are not measured*.

**This unit walks the axis.** Four more rolls of the same configuration with the same world at **200** and **350**
updates, both anchors, twenty replicates each, read beside `e471`'s two at 100 and `e469`'s two at 500, so the held-out
reading is a **four-point curve** on the one axis the corpus's own ladder has. Four claims, registered before either new
roll's reading was opened.

- **YA1 -- and the new budgets are one configuration with the update count moved.** Each new roll carries the three arms
  at **20** replicates, every recorded config field agreeing with the hundred-update roll of the same side except
  `iters`, the output path and the saved weights, and the held-out task's name and counts the same on all eight rolls.
  **Falsifier**: any other field differing, an arm missing or short, or a held-out task whose name or counts differ.
- **YA2 -- and the trained reading does not fall as the budget grows.** The baseline arm's trained reading is
  non-decreasing across the four budgets. **Falsifier**: any budget whose reading is below its predecessor's. *The
  smallest object a plateau or a fall can be seen in is four points.*
- **YA3 -- and what the rest of the budget adds is bought in its first doubling.** The change from **100** to **200**
  is at least **half** of the change from **100** to **500**. **Falsifier**: under **a quarter**; **null**: between.
  *This is `e471`'s front-loading made exact rather than stated.*
- **YA4 -- and the anchoring does not move it at any budget.** Each anchor's paired difference from its own baseline's
  trained reading is under **two** sigma in absolute value at each of the four budgets. **Falsifier**: an anchor at any
  budget whose contrast resolves.

**What it can do beyond that.** It turns the held-out reading into a four-point curve on the axis this corpus has walked
most often, so *the reading is bought early* is a shape with a place in it and not two numbers.

**What it cannot do.** *Four budgets are still a curve and not a mechanism*: the axis is the number of updates and the
corpus carries no run that separates it from the training it buys. *And a probe is not a task*: every reading is of
**linear readability** from the frozen body. *And one held-out draw*: the flag's own draw of the fourth cue set, so all
four points are one cue set's. *And one ridge*: **1e-2** is `e469`'s, and a different one would move every point.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the four budgets with the fourth cue set held out, both anchors, by budget and side
RUNS = {
    "100/bio": Path("runs/e471_earned_label_neurons_holdout_iters100_20reps.json"),
    "100/rand": Path("runs/e471_earned_label_rand_neurons_holdout_iters100_20reps.json"),
    "200/bio": Path("runs/e472_earned_label_neurons_holdout_iters200_20reps.json"),
    "200/rand": Path("runs/e472_earned_label_rand_neurons_holdout_iters200_20reps.json"),
    "350/bio": Path("runs/e472_earned_label_neurons_holdout_iters350_20reps.json"),
    "350/rand": Path("runs/e472_earned_label_rand_neurons_holdout_iters350_20reps.json"),
    "500/bio": Path("runs/e469_earned_label_neurons_holdout_20reps.json"),
    "500/rand": Path("runs/e469_earned_label_rand_neurons_holdout_20reps.json"),
}
BUDGETS = (100, 200, 350, 500)
#: the budgets as the artifact's own keys carry them: `json` stringifies an integer key
BK = tuple(str(b) for b in BUDGETS)
NEW = ("200", "350")
SIDES = ("bio", "rand")
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
IGNORED = ("iters", "json_out", "save_theta")
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
FRONT_LOADED = 0.5
FRONT_FLOOR = 0.25
CLAIMS = (
    ("YA1", f"and the new budgets are one configuration with the update count moved, at {MIN_REPS} replicates",
     "Each new roll carries the three arms at twenty replicates, every recorded config field agreeing with the "
     "hundred-update roll of the same side except iters, the output path and the saved weights, and the held-out "
     "task's name and counts the same on all eight rolls",
     "falsifier: any other field differing, an arm missing or short, or a held-out task whose name or counts differ"),
    ("YA2", "and the trained reading does not fall as the budget grows",
     "The baseline arm's trained reading is non-decreasing across the four budgets",
     "falsifier: any budget whose reading is below its predecessor's"),
    ("YA3", f"and the first doubling carries at least {FRONT_LOADED:.0%} of the whole change",
     "The change from 100 to 200 updates is at least half of the change from 100 to 500",
     f"falsifier: under {FRONT_FLOOR:.0%}; null: between"),
    ("YA4", f"and the anchoring does not move it at any budget, under {SIGMA:.0f} sigma",
     "Each anchor's paired difference from its own baseline's trained reading is under two sigma in absolute value at "
     "each of the four budgets",
     "falsifier: an anchor at any budget whose contrast resolves"),
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
                     "ridge": sorted({b.get("ridge") for b in blocks})}
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: (doc.get("config") or {}).get(k)
                       for k in sorted(set(doc.get("config") or {}) - set(IGNORED))}}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "curve": {}, "steps": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label.split("/")[1]])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent, carries no {ANCHOR_OF[label.split('/')[1]]} arm, or "
                              f"carries no holdout block"}
        out["runs"][label] = got
    base = {side: out["runs"][f"{BUDGETS[0]}/{side}"] for side in SIDES}
    for side in SIDES:
        for b in NEW:
            roll = out["runs"][f"{b}/{side}"]
            fields = sorted(set(roll["config"]) | set(base[side]["config"]))
            for k in fields:
                out["same"][f"{side}.{k}"] = out["same"].get(f"{side}.{k}", True) and \
                    roll["config"].get(k) == base[side]["config"].get(k)
            out["same"][f"{side}.circuit"] = out["same"].get(f"{side}.circuit", True) and \
                roll["shared"].get("circuit") == base[side]["shared"].get("circuit")
            out["same"][f"{side}.tasks"] = out["same"].get(f"{side}.tasks", True) and \
                roll["shared"].get("tasks") == base[side]["shared"].get("tasks")
    counts = {f"{label}.{arm}.{k}": tuple(got["arms"][arm][k]) for label, got in out["runs"].items()
              for arm in got["arms"] for k in ("task", "n_train", "n_eval", "ridge")}
    for b in BK:
        out["curve"][b] = {}
        for side in SIDES:
            roll = out["runs"][f"{b}/{side}"]
            base_arm = roll["arms"][BASELINE]
            out["curve"][b][side] = {
                "budget": int(b), "side": side, "anchor": roll["anchor"],
                "initial": statistics.fmean(base_arm["before"]), "trained": statistics.fmean(base_arm["after"]),
                "change": _paired(base_arm["after"], base_arm["before"]),
                "arms": {arm: {"initial": statistics.fmean(got["before"]),
                               "trained": statistics.fmean(got["after"]),
                               "change": _paired(got["after"], got["before"]),
                               "against_baseline": _paired(got["after"], base_arm["after"])}
                         for arm, got in roll["arms"].items()},
            }
    for side in SIDES:
        seq = [out["curve"][b][side]["trained"] for b in BK]
        after = [out["runs"][f"{b}/{side}"]["arms"][BASELINE]["after"] for b in BUDGETS]
        out["steps"][side] = {
            "trained": seq,
            "first": out["curve"][BK[0]][side]["trained"],
            "total": out["curve"][BK[-1]][side]["trained"] - out["curve"][BK[0]][side]["trained"],
            "steps": [seq[i + 1] - seq[i] for i in range(len(seq) - 1)],
            #: each step paired across the two budgets' replicates, which share `seed0` and so share a body
            #: initialisation and a read-out draw
            "step_paired": {f"{BUDGETS[i]}-{BUDGETS[i + 1]}": _paired(after[i + 1], after[i])
                            for i in range(len(BUDGETS) - 1)},
            "whole_paired": _paired(after[-1], after[0]),
            "non_decreasing": all(seq[i + 1] >= seq[i] for i in range(len(seq) - 1)),
        }
    thin = {label: v["replicates"] for label, roll in out["runs"].items()
            for arm, v in roll["arms"].items() if v["replicates"] < MIN_REPS}
    out["spans"] = {
        "budgets": list(BUDGETS), "sides": list(SIDES), "runs": len(out["runs"]),
        "same_fields": len(out["same"]), "thin": thin,
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "tasks": sorted({t for got in out["runs"].values() for arm in got["arms"].values() for t in arm["task"]}),
        "counts": counts,
        "short": {label: sorted(roll["arms"]) for label, roll in out["runs"].items() if len(roll["arms"]) < N_ARMS},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no holdout block"}
                for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    tasks = {k: v for k, v in s["counts"].items() if k.endswith(".task")}
    nt = {k: v for k, v in s["counts"].items() if k.endswith(".n_train")}
    ne = {k: v for k, v in s["counts"].items() if k.endswith(".n_eval")}
    ridges = {k: v for k, v in s["counts"].items() if k.endswith(".ridge")}
    counts_ok = (len({tuple(v) for v in tasks.values()}) == 1 and len({tuple(v) for v in nt.values()}) == 1
                 and len({tuple(v) for v in ne.values()}) == 1 and len({tuple(v) for v in ridges.values()}) == 1)
    j1 = {"id": "YA1",
          "measured": f"{s['runs']} rolls at {s['replicates']} replicates over {s['same_fields']} compared fields, the "
                      f"held-out task {s['tasks']} with counts "
                      f"{sorted({tuple(v) for v in nt.values()})} and {sorted({tuple(v) for v in ne.values()})}",
          "verdict": "MET -- one configuration at four budgets with the update count moved and the same held-out cue "
                     "set on all eight rolls" if (not differ and counts_ok and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, tasks {tasks}, thin {s['thin']}, short {s['short']}"}
    st = r["steps"]
    fell = sorted(side for side in SIDES if not st[side]["non_decreasing"])
    j2 = {"id": "YA2",
          "measured": f"the baseline's trained reading at {BUDGETS} updates runs "
                      f"{ {side: [round(v, 4) for v in st[side]['trained']] for side in SIDES} }, the steps "
                      f"{ {side: [round(v, 4) for v in st[side]['steps']] for side in SIDES} } at "
                      f"{ {side: {k: round(v['sigma'], 2) for k, v in st[side]['step_paired'].items()} for side in SIDES} } "
                      f"sigma paired",
          "verdict": "MET -- no budget's reading is below its predecessor's, on either roll" if not fell else
                     f"FALSIFIER FIRED -- {fell} fall somewhere on the axis"}
    share = {side: (st[side]["steps"][0] / st[side]["total"]) if st[side]["total"] else 0.0 for side in SIDES}
    worst = min(share.values(), default=0.0)
    j3 = {"id": "YA3",
          "measured": f"the first doubling adds { {side: round(st[side]['steps'][0], 4) for side in SIDES} } of the "
                      f"whole { {side: round(st[side]['total'], 4) for side in SIDES} }, a share of "
                      f"{ {side: round(share[side], 3) for side in SIDES} }",
          "verdict": f"MET -- the first doubling carries {100 * worst:.0f}% of the whole change at its weakest" if
                     worst >= FRONT_LOADED else
                     f"FALSIFIER FIRED -- the weakest share is {100 * worst:.0f}%" if worst < FRONT_FLOOR else
                     f"NULL -- the weakest share is {100 * worst:.0f}%, between {100 * FRONT_FLOOR:.0f}% and "
                     f"{100 * FRONT_LOADED:.0f}%"}
    bad = sorted(f"{b}/{side}/{anchor}" for b in BUDGETS for side in SIDES
                 for anchor, got in r["curve"][str(b)][side]["arms"].items()
                 if anchor != BASELINE and abs(got["against_baseline"]["sigma"]) >= SIGMA)
    j4 = {"id": "YA4",
          "measured": f"each anchor against its own baseline at each budget: "
                      f"{ {f'{b}/{side}': {a: (round(v['against_baseline']['mean'], 4),
                                                round(v['against_baseline']['sigma'], 2))
                                          for a, v in r['curve'][str(b)][side]['arms'].items() if a != BASELINE}
                          for b in BUDGETS for side in SIDES} }",
          "verdict": "MET -- the anchoring does not move the held-out reading at any of the four budgets" if not bad
                     else f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the held-out reading across the budget ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world with a fourth cue set held out, at four budgets and on both anchors -- one world, one")
    print("   held-out cue set, and the budget the only field that moves")
    print(f"\n   {'budget/roll/arm':<26} {'initial':>8} {'trained':>8} {'change':>8} {'sigma':>7} {'vs base':>9} {'sigma':>7}")
    for b in BUDGETS:
        for side in SIDES:
            cell = r["curve"][str(b)][side]
            for arm in (BASELINE, cell["anchor"], BUFFER):
                got = cell["arms"][arm]
                vs = got["against_baseline"]
                print(f"   {str(b) + '/' + side + '/' + arm:<26} {got['initial']:>8.4f} {got['trained']:>8.4f} "
                      f"{got['change']['mean']:>+8.4f} {got['change']['sigma']:>7.2f} " +
                      (f"{vs['mean']:>+9.4f} {vs['sigma']:>7.2f}" if arm != BASELINE else f"{'-':>9} {'-':>7}"))
    print("\n   the baseline's trained reading, by budget:")
    for side in SIDES:
        print(f"      {side}: " + ", ".join(f"{b}: {r['curve'][str(b)][side]['trained']:.4f}" for b in BUDGETS))
    print(f"      the steps: " + "; ".join(
        f"{side} " + ", ".join(f"{v:+.4f}" for v in r["steps"][side]["steps"]) for side in SIDES))
    print("\n== the registered claims, YA1-YA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e471` found the held-out reading bought early and left the budgets between its two points unmeasured;")
    print("    this walks them)")
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
