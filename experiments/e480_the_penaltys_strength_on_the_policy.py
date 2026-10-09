"""E480 -- the penalty's strength on the policy: whether the arm that stops learning is a cliff or a dose.

`e479` trained the agent's 64-number policy through a three-task sequence with a diagonal-Fisher penalty at the
card's own `lam = 1.0`, found that at that strength the **penalty arm stops moving** (its gains fall to **+0.2007** at
**1.00** sigma and **+0.0233** at **0.10**), and closed on the one thing that leaves: *"one strength and one penalty:
a diagonal Fisher at `lam = 1.0`, the card's own number, and a ladder over it is not run -- so the penalty stops the
policy learning is a statement about that strength, and a weaker one is the first thing a later unit should sweep."*

**This unit walks that ladder.** The same three separable tasks and the same 64-number policy, with `e479`'s own
penalty arm run at **six strengths** -- `0`, `3e-4`, `3e-3`, `0.03`, `0.3` and `1.0`, three and a half orders of
magnitude, with `3e-3` the corpus's own convention -- eight replicates each. Four claims, registered before any of the
six was read.

- **LA1 -- and the six points are one configuration with the strength moved.** Every point starts from the identity
  policy, which is the environment's own rule, bit for bit; the seeds and the target draws are shared; and the
  **`lam = 0` point reproduces `e479`'s `naive` arm bit for bit**, since a zero penalty is no penalty. **Falsifier**:
  any point whose identity world differs, or a `lam = 0` matrix differing from that arm's.
- **LA2 -- and the cost is a dose.** The largest strength's mean diagonal is below the **smallest non-zero**
  strength's by at least **0.50**, paired over the replicates, at **two** sigma or more. **Falsifier**: a gap below
  **0.20**, or one that does not resolve. **Null**: between.
- **LA3 -- and there is a strength at which the penalty is free.** At least one non-zero strength has a mean diagonal
  within **0.20** of the zero-strength point's. **Falsifier**: every non-zero strength at least **0.50** below it.
  **Null**: none free but none that far below. *This is what `e479`'s single strength could not say.*
- **LA4 -- and the retention is bought.** At the largest strength the mean last row exceeds the zero-strength point's
  by at least **0.50**, paired, at **two** sigma or more. **Falsifier**: a gap below **0.20**, or one that does not
  resolve. **Null**: between.

**What it can do beyond that.** It says whether the penalty's failure on the agent is a **cliff** -- an arm that never
works at the card's strength and works below it -- or a **dose**, which is the shape every other strength axis in this
corpus has been asked for. And it is the first ladder whose subject is a policy.

**What it cannot do.** *One penalty and one family*: a diagonal Fisher with 8 batches, so a block penalty, a KL anchor
or a different Fisher estimator is not in it. *And one buffer is absent*: this ladder is the penalty alone, so nothing
here says where the buffer sits between the points. *And the tasks share a circuit and a cue population*: they differ
in four cue symbols and one target block, so the sequence is easier than the benchmark's. *And the body is frozen*: the
only thing the penalty anchors is 64 numbers. *And six strengths are a ladder and not a curve*: no point between them
is measured, so a threshold between two of the six is located to an interval and not to a value. *And eight replicates
are not the population*: every sigma is the paired one over the worlds the replicates share.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments import e479_the_methods_on_the_policys_sequence as e479

#: the ladder, with the corpus's own `3e-3` in it and the card's `1.0` at the top
LAMS = (0.0, 3e-4, 3e-3, 0.03, 0.3, 1.0)
#: the artifact whose `naive` arm the zero-strength point must reproduce, bit for bit
E479 = Path("runs/e479_the_methods_on_the_policys_sequence.json")
TASKS = e479.TASKS
REPLICATES = e479.REPLICATES
SIZE = e479.SIZE
READOUT_SIZE = e479.READOUT_SIZE
#: the bars: MET at the bar and resolved, the falsifier at the floor or unresolved, and a null between
SIGMA = 2.0
BAR = 0.50
FLOOR = 0.20
#: what "free" means for LA3: a strength whose diagonal is this close to the zero-strength point's
FREE = 0.20
CLAIMS = (
    ("LA1", "and the six points are one configuration with the strength moved",
     "Every point starts from the identity policy, which is the environment's own rule, bit for bit; the seeds and "
     "the target draws are shared; and the lam = 0 point reproduces e479's naive arm bit for bit",
     "falsifier: any point whose identity world differs, or a lam = 0 matrix differing from that arm's"),
    ("LA2", f"and the cost is a dose, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "The largest strength's mean diagonal is below the smallest non-zero strength's by at least 0.50, paired over "
     "the replicates, at two sigma or more",
     f"falsifier: a gap below {FLOOR:.2f}, or one that does not resolve"),
    ("LA3", f"and there is a strength at which the penalty is free, within {FREE:.2f}",
     "At least one non-zero strength has a mean diagonal within 0.20 of the zero-strength point's",
     f"falsifier: every non-zero strength at least {BAR:.2f} below it"),
    ("LA4", f"and the retention is bought, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "At the largest strength the mean last row exceeds the zero-strength point's by at least 0.50, paired, at two "
     "sigma or more",
     f"falsifier: a gap below {FLOOR:.2f}, or one that does not resolve"),
)


def key(lam: float) -> str:
    """A strength's key in the artifact: a string, so a JSON round trip cannot turn it into something else."""
    return f"{lam:g}"


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


def reading(lams=LAMS, replicates=REPLICATES, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(e479.SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=e479.TAU)).torch_model()
    cells = [e479.one_arm(circ, net, int(r), "penalty", lam=float(l))
             for r in replicates for l in lams]
    out = {"ok": True, "reason": None, "cells": cells, "mean_R": {}, "diagonal": {}, "last_row": {},
           "learned": {}, "ladder": {}, "naive_check": {}, "spans": {},
           "worlds": {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": e479.SEED,
                      "tau": e479.TAU, "n_symbols": e479.N_SYMBOLS, "symbols_per_task": e479.SYMBOLS_PER_TASK,
                      "tasks": TASKS, "chance": 1.0 / e479.SYMBOLS_PER_TASK, "n_train": e479.N_TRAIN,
                      "n_held": e479.N_HELD, "dims": e479.WORLD_DIMS, "leak": e479.WORLD_LEAK,
                      "lams": [key(l) for l in lams], "replicates": list(map(int, replicates)),
                      "steps": e479.STEPS, "lr": e479.LR, "fisher_batches": e479.FISHER_BATCHES}}
    rows = [key(l) for l in lams]
    #: the cells were rolled replicate-major and strength-minor, so the index is the position in that product
    by = {(int(rr), rows[j]): cells[i * len(lams) + j]
          for i, rr in enumerate(replicates) for j, _ in enumerate(lams)}

    for k in rows:
        matrix = []
        for i in range(TASKS + 1):
            row = []
            for j in range(TASKS):
                vals = [by[(r, k)]["R"][i][j] for r in replicates if by[(r, k)]["R"][i][j] is not None]
                row.append(statistics.fmean(vals) if vals else None)
            matrix.append(row)
        out["mean_R"][k] = matrix
        out["diagonal"][k] = [statistics.fmean([by[(r, k)]["R"][i + 1][i] for i in range(TASKS)])
                              for r in replicates]
        out["last_row"][k] = [statistics.fmean([by[(r, k)]["R"][TASKS][j] for j in range(TASKS)])
                              for r in replicates]
        out["learned"][k] = {f"task{t}": _paired([by[(r, k)]["R"][t + 1][t] for r in replicates],
                                                 [by[(r, k)]["R"][0][t] for r in replicates])
                             for t in range(TASKS)}

    #: the zero-strength point against `e479`'s `naive` arm, replicate by replicate and entry by entry
    doc = load(E479)
    naive = None
    if doc:
        naive = {c["seed"]: c["R"] for c in doc.get("cells") or [] if c.get("arm") == "naive"}
    if naive and all(r in naive for r in replicates):
        worst = 0.0
        for r in replicates:
            a, b = by[(r, key(0.0))]["R"], naive[r]
            for i in range(TASKS + 1):
                for j in range(TASKS):
                    if a[i][j] is not None and b[i][j] is not None:
                        worst = max(worst, abs(a[i][j] - b[i][j]))
        out["naive_check"] = {"present": True, "worst_abs": worst, "bitwise": worst == 0.0}
    else:
        out["naive_check"] = {"present": False, "worst_abs": None, "bitwise": None}

    zero, top = key(0.0), key(max(lams))
    nonzero = [key(l) for l in lams if l > 0]
    smallest = nonzero[0]
    free = [k for k in nonzero
            if statistics.fmean(out["diagonal"][k]) >= statistics.fmean(out["diagonal"][zero]) - FREE]
    out["ladder"] = {
        "zero": zero, "top": top, "smallest_nonzero": smallest, "nonzero": nonzero,
        "diagonal": {k: statistics.fmean(out["diagonal"][k]) for k in rows},
        "last_row": {k: statistics.fmean(out["last_row"][k]) for k in rows},
        "cost_top_over_smallest": _paired(out["diagonal"][smallest], out["diagonal"][top]),
        "retention_top_over_zero": _paired(out["last_row"][top], out["last_row"][zero]),
        "cost_by_strength": {k: _paired(out["diagonal"][zero], out["diagonal"][k]) for k in nonzero},
        "free": free,
        "free_none": len(free) == 0,
    }
    out["spans"] = {
        "lams": rows, "replicates": len(replicates), "tasks": TASKS, "n_act": cells[0]["n_act"],
        "identity_all": all(c["identity_bitwise"] for c in cells),
        "identity_worst": max(c["identity_max_abs"] for c in cells),
        "cells": len(cells), "seeds": sorted({c["seed"] for c in cells}),
        "targets": sorted({c["targets_sha1"] for c in cells}),
        "moves": {k: [round(by[(r, k)]["policy_move"], 3) for r in replicates] for k in rows},
    }
    return out


def _band(mean, sigma, what):
    if mean >= BAR and sigma >= SIGMA:
        return f"MET -- {what} {mean:+.4f} at {sigma:+.2f} sigma"
    if mean < FLOOR or sigma < SIGMA:
        return f"FALSIFIER FIRED -- {what} {mean:+.4f} at {sigma:+.2f} sigma, against a bar of {BAR:.2f}"
    return f"NULL -- {what} {mean:+.4f} between the floor {FLOOR:.2f} and the bar {BAR:.2f}"


def judge(r: dict) -> list[dict]:
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the ladder was not walked"} for c in CLAIMS]
    s = r["spans"]
    nc = r["naive_check"]
    if not nc.get("present"):
        j1 = {"id": "LA1", "measured": f"the zero-strength point cannot be checked: {E479} is absent",
              "verdict": "REFUSED -- e479's artifact is absent"}
    else:
        j1 = {"id": "LA1",
              "measured": f"{s['cells']} cells over the lams {s['lams']} and {s['replicates']} replicates, the seeds "
                          f"{s['seeds']} and the target draws {len(s['targets'])}, the identity policy bit-identical "
                          f"to the environment's own rule on **{s['cells']} of {s['cells']}** cells (worst "
                          f"**{s['identity_worst']:.1e}**), and the **lam = 0** point against `e479`'s `naive` arm at "
                          f"a worst absolute difference of **{nc['worst_abs']:.1e}**",
              "verdict": "MET -- one configuration with the strength moved, and a zero penalty is no penalty" if
                         (s["identity_all"] and s["identity_worst"] == 0.0 and nc["bitwise"] and
                          len(s["seeds"]) == s["replicates"] and len(s["targets"]) == s["replicates"]) else
                         f"FALSIFIER FIRED -- identity {s['identity_all']} at {s['identity_worst']}, the zero point "
                         f"against e479's naive arm {nc['bitwise']} at {nc['worst_abs']}, {len(s['seeds'])} seeds "
                         f"over {s['replicates']} replicates and {len(s['targets'])} target draws"}
    lad = r["ladder"]
    top, small, zero = lad["top"], lad["smallest_nonzero"], lad["zero"]
    c2 = lad["cost_top_over_smallest"]
    j2 = {"id": "LA2",
          "measured": f"the mean diagonals are "
                      f"{ {k: round(v, 4) for k, v in lad['diagonal'].items()} }, so the largest strength "
                      f"({top}) is below the smallest non-zero ({small}) by **{c2['mean']:+.4f}** at "
                      f"**{c2['sigma']:+.2f}** sigma",
          "verdict": _band(c2["mean"], c2["sigma"], "the cost grows with the strength by")}
    free = lad["free"]
    below = [k for k in lad["nonzero"] if round(lad["diagonal"][zero] - lad["diagonal"][k], 6) >= BAR]
    j3 = {"id": "LA3",
          "measured": f"against the zero-strength point's diagonal "
                      f"**{lad['diagonal'][zero]:.4f}**, the strengths within {FREE:.2f} of it are {free} and the "
                      f"per-strength costs are "
                      f"{ {k: round(v['mean'], 4) for k, v in lad['cost_by_strength'].items()} } at "
                      f"{ {k: round(v['sigma'], 2) for k, v in lad['cost_by_strength'].items()} } sigma",
          "verdict": (f"MET -- the penalty is free at {free[0]} and above" if free else
                      f"FALSIFIER FIRED -- every non-zero strength is at least {BAR:.2f} below the zero-strength "
                      f"point: {below}" if len(below) == len(lad["nonzero"]) else
                      f"NULL -- no strength is within {FREE:.2f} of the zero-strength point and none is {BAR:.2f} "
                      f"below it")}
    c4 = lad["retention_top_over_zero"]
    j4 = {"id": "LA4",
          "measured": f"the mean last rows are { {k: round(v, 4) for k, v in lad['last_row'].items()} }, so the "
                      f"largest strength is above the zero-strength point by **{c4['mean']:+.4f}** at "
                      f"**{c4['sigma']:+.2f}** sigma",
          "verdict": _band(c4["mean"], c4["sigma"], "the largest strength retains more than the baseline by")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the penalty's strength on the policy ==")
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        print("   REFUSED -- the ladder was not walked")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    w = r["worlds"]
    print(f"   circuit {w['circuit']} ({w['size']} neurons), {w['tasks']} tasks of {w['symbols_per_task']} symbols "
          f"each, the lams {w['lams']}, {w['replicates']} replicates")
    print(f"\n   {'lam':>7} {'mean diagonal':>14} {'mean last row':>14} {'cost vs 0':>11} {'sigma':>8}")
    lad = r["ladder"]
    for k in w["lams"]:
        cost = lad["cost_by_strength"].get(k)
        print(f"   {k:>7} {lad['diagonal'][k]:>14.4f} {lad['last_row'][k]:>14.4f} " +
              (f"{cost['mean']:>+11.4f} {cost['sigma']:>8.2f}" if cost else f"{'-':>11} {'-':>8}"))
    print("\n   the retention matrices in reward, by strength (row 0 is the identity policy):")
    for k in w["lams"]:
        print(f"      lam {k}:")
        for i, row in enumerate(r["mean_R"][k]):
            print(f"         row {i}: " + "  ".join(f"{x:>9.4f}" if x is not None else f"{'-':>9}" for x in row))
    print("\n== the registered claims, LA1-LA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e479` found the penalty arm stopping at the card's lam = 1.0 and named this ladder;")
    print("    this unit walks it, and its lam = 0 point is that unit's naive arm to the bit)")
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
