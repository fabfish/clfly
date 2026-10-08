"""E471 -- the held-out task at a fifth of the budget: whether the unseen cue set's decodability is a training's.

`e469` drove the corpus's first held-out task at the card's own budget -- **500 updates** -- and found the probe going
from **0.6875** to **0.7719**, a paired **+0.0844** at **10.11** sigma, with neither anchor moving it. Its own *cannot
do* names what that leaves open: **one budget**, since a reading taken after five hundred updates says nothing about
what a shorter sequence would leave.

**This unit moves the budget and holds the task.** Two more rolls of the same configuration with **`--iters 100`** --
the world the flag draws is the same one, because nothing in its seed depends on the update count, so the fourth cue
set is the same cue set -- read beside `e469`'s two. Four claims, registered before either new roll's reading was
opened.

- **XA1 -- and the two budgets are one configuration with the update count moved.** Each budget's side carries the three
  arms at **20** replicates, every recorded config field agreeing with the other budget's roll of the same side except
  `iters`, the output path and the saved weights, the held-out task's name and its train and eval counts equal, and the
  probe's ridge equal. **Falsifier**: any other field differing, an arm missing or short, or a held-out task whose name
  or counts differ; refused when a roll is absent.
- **XA2 -- and the sequence raises the unseen cue set's decodability at a fifth of the budget too.** At **100** updates
  the baseline arm's paired trained minus initial reading is positive at **two** sigma or more. **Falsifier**: under two
  sigma, or negative.
- **XA3 -- and the trained reading grows with the budget.** The baseline arm's trained reading at **500** updates
  exceeds its at **100** at **two** sigma or more, paired across the two budgets' replicates. **Falsifier**: under two
  sigma, or the other way. *The paired test is available because the two rolls share `seed0`, so replicate r of one is
  the same body initialisation and the same read-out draw as replicate r of the other.*
- **XA4 -- and the anchoring does not move it at either budget.** Each anchor's paired difference from its own
  baseline's trained reading is under **two** sigma in absolute value, at both budgets. **Falsifier**: an anchor at
  either budget whose contrast resolves.

**What it can do beyond that.** It turns a held-out reading into a **curve** on the smallest axis the corpus has:
whether what the sequence teaches is readable on a task it never saw is a question about the budget, and the answer
here is the difference between two of its values rather than one.

**What it cannot do.** *Two budgets are not a curve*: **100** and **500** are one pair and the budgets between them are
not measured. *And a probe is not a task*: the read-out is fitted on the held-out cue set's own labels, so both readings
are of **linear readability** and not of what the sequence's method would learn. *And one held-out draw*: the fourth cue
set is the flag's own draw and a redraw of it is not measured. *And one ridge*: **1e-2** is `e469`'s and not the
benchmark's.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the two budgets at the card's own head, both anchors, by budget and side
RUNS = {
    "100/bio": Path("runs/e471_earned_label_neurons_holdout_iters100_20reps.json"),
    "100/rand": Path("runs/e471_earned_label_rand_neurons_holdout_iters100_20reps.json"),
    "500/bio": Path("runs/e469_earned_label_neurons_holdout_20reps.json"),
    "500/rand": Path("runs/e469_earned_label_rand_neurons_holdout_20reps.json"),
}
BUDGETS = (100, 500)
#: the budgets as the artifact's own keys carry them: `json` stringifies an integer key
BK = tuple(str(b) for b in BUDGETS)
SIDES = ("bio", "rand")
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
IGNORED = ("iters", "json_out", "save_theta")
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
CLAIMS = (
    ("XA1", f"and the two budgets are one configuration with the update count moved, at {MIN_REPS} replicates",
     "Each budget's side carries the three arms at twenty replicates, every recorded config field agreeing with the "
     "other budget's roll of the same side except iters, the output path and the saved weights, the held-out task's "
     "name and its train and eval counts equal, and the ridge equal",
     "falsifier: any other field differing, an arm missing or short, or a held-out task whose name or counts differ; "
     "refused when a roll is absent"),
    ("XA2", f"and the sequence raises the decodability at a fifth of the budget too, at {SIGMA:.0f} sigma",
     "At 100 updates the baseline arm's paired trained minus initial reading is positive at two sigma or more",
     "falsifier: under two sigma, or negative"),
    ("XA3", f"and the trained reading grows with the budget, at {SIGMA:.0f} sigma paired",
     "The baseline arm's trained reading at 500 updates exceeds its at 100 at two sigma or more",
     "falsifier: under two sigma, or the other way"),
    ("XA4", f"and the anchoring does not move it at either budget, under {SIGMA:.0f} sigma",
     "Each anchor's paired difference from its own baseline's trained reading is under two sigma in absolute value, at "
     "both budgets",
     "falsifier: an anchor at either budget whose contrast resolves"),
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
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "curve": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label.split("/")[1]])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent, carries no {ANCHOR_OF[label.split('/')[1]]} arm, or "
                              f"carries no holdout block"}
        out["runs"][label] = got
    for side in SIDES:
        a, b = out["runs"][f"100/{side}"], out["runs"][f"500/{side}"]
        fields = sorted(set(a["config"]) | set(b["config"]))
        for k in fields:
            out["same"][f"{side}.{k}"] = a["config"].get(k) == b["config"].get(k)
        out["same"][f"{side}.circuit"] = a["shared"].get("circuit") == b["shared"].get("circuit")
        out["same"][f"{side}.tasks"] = a["shared"].get("tasks") == b["shared"].get("tasks")
    counts = {f"{label}.{arm}.{k}": tuple(got["arms"][arm][k]) for label, got in out["runs"].items()
              for arm in got["arms"] for k in ("task", "n_train", "n_eval", "ridge")}
    for b in BUDGETS:
        out["curve"][str(b)] = {}
        for side in SIDES:
            roll = out["runs"][f"{b}/{side}"]
            base = roll["arms"][BASELINE]
            out["curve"][str(b)][side] = {
                "budget": b, "side": side, "anchor": roll["anchor"],
                "initial": statistics.fmean(base["before"]), "trained": statistics.fmean(base["after"]),
                "change": _paired(base["after"], base["before"]),
                "arms": {arm: {"initial": statistics.fmean(got["before"]),
                               "trained": statistics.fmean(got["after"]),
                               "change": _paired(got["after"], got["before"]),
                               "against_baseline": _paired(got["after"], base["after"])}
                         for arm, got in roll["arms"].items()},
            }
    paired = {}
    for side in SIDES:
        a, b = out["runs"][f"100/{side}"]["arms"][BASELINE], out["runs"][f"500/{side}"]["arms"][BASELINE]
        paired[side] = {"trained": _paired(b["after"], a["after"]),
                        "initial": _paired(b["before"], a["before"])}
    out["paired"] = paired
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
                 and len({tuple(v) for v in ne.values()}) == 1
                 and len({tuple(v) for v in ridges.values()}) == 1)
    j1 = {"id": "XA1",
          "measured": f"{s['runs']} rolls at {s['replicates']} replicates over {s['same_fields']} compared fields, "
                      f"the held-out task {s['tasks']} with counts "
                      f"{sorted({tuple(v) for v in nt.values()})} and "
                      f"{sorted({tuple(v) for v in ne.values()})} and ridge "
                      f"{sorted({tuple(v) for v in ridges.values()})}",
          "verdict": "MET -- one configuration at two budgets with the update count moved, and the same held-out cue "
                     "set on both" if (not differ and counts_ok and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, tasks {tasks}, thin {s['thin']}, short {s['short']}"}
    small = {side: r["curve"][BK[0]][side]["change"] for side in SIDES}
    worst = min((v["sigma"] for v in small.values()), default=0.0)
    j2 = {"id": "XA2",
          "measured": f"at {BUDGETS[0]} updates the baseline's probe reads "
                      f"{ {side: round(r['curve'][BK[0]][side]['initial'], 4) for side in SIDES} } on the initial body "
                      f"and { {side: round(r['curve'][BK[0]][side]['trained'], 4) for side in SIDES} } after the "
                      f"sequence, a paired contrast of "
                      f"{ {side: round(small[side]['mean'], 4) for side in SIDES} } at "
                      f"{ {side: round(small[side]['sigma'], 2) for side in SIDES} } sigma",
          "verdict": f"MET -- the sequence raises the decodability at a fifth of the budget too, the weaker at "
                     f"{worst:.2f} sigma" if worst >= SIGMA else
                     f"FALSIFIER FIRED -- the weaker contrast is {worst:.2f} sigma"}
    grow = r["paired"]
    weak = min((v["trained"]["sigma"] for v in grow.values()), default=0.0)
    j3 = {"id": "XA3",
          "measured": f"the baseline's trained reading at {BUDGETS[1]} exceeds its at {BUDGETS[0]} by "
                      f"{ {side: round(grow[side]['trained']['mean'], 4) for side in SIDES} } at "
                      f"{ {side: round(grow[side]['trained']['sigma'], 2) for side in SIDES} } sigma paired, from "
                      f"{ {side: round(r['curve'][BK[0]][side]['trained'], 4) for side in SIDES} } to "
                      f"{ {side: round(r['curve'][BK[1]][side]['trained'], 4) for side in SIDES} }",
          "verdict": f"MET -- the unseen cue set's decodability grows with the budget, the weaker at {weak:.2f} "
                     f"sigma" if weak >= SIGMA else
                     f"FALSIFIER FIRED -- the weaker contrast is {weak:.2f} sigma"}
    bad = sorted(f"{b}/{side}/{anchor}" for b in BUDGETS for side in SIDES
                 for anchor, got in r["curve"][str(b)][side]["arms"].items()
                 if anchor != BASELINE and abs(got["against_baseline"]["sigma"]) >= SIGMA)
    j4 = {"id": "XA4",
          "measured": f"each anchor against its own baseline's trained reading: "
                      f"{ {f'{b}/{side}': {a: (round(v['against_baseline']['mean'], 4),
                                                round(v['against_baseline']['sigma'], 2))
                                          for a, v in r['curve'][str(b)][side]['arms'].items() if a != BASELINE}
                          for b in BUDGETS for side in SIDES} }",
          "verdict": "MET -- the anchoring does not move the held-out reading at either budget" if not bad else
                     f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the held-out task at two budgets ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world with a fourth cue set held out, at the card's own 500 updates and at a hundred; the")
    print("   flag's world does not depend on the update count, so both budgets carry the SAME held-out cue set")
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
    print("\n== the registered claims, XA1-XA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e469` took the corpus's first held-out reading at the card's own budget and closed on *one budget*;")
    print("    this asks what a fifth of it leaves)")
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
