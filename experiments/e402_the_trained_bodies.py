"""E402 -- the trained bodies: does the movement of the weights separate the one world from the nine?

`e401` retired the last near-geometry candidate and registered the direction that was left: *"the screen is empty --
the hop count, `e400`'s five properties and now the weight's own test all fail to separate the card's world from the
other nine, and what remains unmeasured is ... anything about the **trained body**, which is where the difference
appears."* This unit measures what the trained body offers without rolling anything: the six worlds whose far-point
bodies are on disk have their weights saved, so the movement from the connectome's own weights to the trained ones is
a number, and how the six movements relate to each other is another. Five claims, registered before any weight was
loaded.

- **AB1 -- and the six bodies start from one body.** For every replicate, the six `theta_initial` arrays are
  **identical** -- the connectome's own weights, not a per-world draw. **Falsifier**: any of them differing on any
  replicate, which would make every comparison below a comparison of starting points.
- **AB2 -- and how far the training moved them does not separate the one.** The card's world's mean relative
  movement, over twenty replicates, lies within **0.005** of the range the five failing worlds' means span.
  **Falsifier**: outside it by more than **0.010**. *The card's world holds the cue by 0.0854 where the others lose
  it by 0.1479 to 0.2490, so if the one differed in how far its training walked, a tenth of a reading would have a
  distance to show for it.*
- **AB3 -- and the movements are not one direction.** Every world's mean cosine with the other five, over the same
  replicates, is below **0.5**, so the six updates are near-orthogonal and there is no common direction the card's
  world could be the exception to. **Falsifier**: any world at or above 0.5. **Null**: between 0.3 and 0.5.
- **AB4 -- and the card's body is not an outlier among them.** Its mean cosine with the other five lies inside the
  range the five failing worlds' own mean cosines span. **Falsifier**: outside that range.
- **AB5 -- and the head does not separate it either.** The card's trained head reads task 0 inside the range the
  five failing worlds' heads span. **Falsifier**: outside it. *`e379` and `e380` found the head and the world agree
  after training, so if the head were the discriminator the world's failure would be a head's failure -- and the
  heads are 0.5208 to 0.8333, a range the card's 0.7500 sits inside.*

**What it can do beyond that.** It closes the cheapest remaining reading of "look at the trained body": the bodies
are on disk, their movement and their mutual alignment are two numbers each, and neither separates the one world
that keeps the cue. Together with `e397` to `e401` it says the difference between the card's world and the other
nine is **not** in the draw's near geometry, not in how far training moved the weights, and not in which way.

**What it cannot do.** *Two numbers are not a trajectory*: relative movement and pairwise cosine say nothing about
which directions in the weight space the updates took, and a difference spread over a subspace orthogonal to the
common direction would be invisible here. *And the failing set is five of nine*: the four engine redraws and the four
other cue populations that failed at the near point are not at the far point, so this compares the card's world with
five others and not with all nine. *And it is one budget and one arm*: the 500-update `naive` bodies only. *And a
reading is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the six worlds whose 500-update bodies are on disk, and the theta directory each one's weights are in
BODIES = {
    "card": Path("runs/e380_theta"),
    "cue1": Path("runs/e398_theta_cue1_iters500"),
    "cue3": Path("runs/e398_theta_cue3_iters500"),
    "cue9": Path("runs/e399_theta_cue9_iters500"),
    "cue14": Path("runs/e399_theta_cue14_iters500"),
    "cue6": Path("runs/e401_theta_cue6_iters500"),
}
REPLICATES = tuple(100 * r for r in range(20))
#: the trained heads, read from the artifacts `e398` to `e401` wrote
HEADS = {"card": 0.7500, "cue1": 0.7500, "cue3": 0.8333, "cue9": 0.8125, "cue14": 0.8333, "cue6": 0.5208}
#: the readings the bodies are the bodies of, so the separation being asked about is a tenth of a reading
GAINS = {"card": 0.0854, "cue1": -0.1813, "cue3": -0.1635, "cue9": -0.2250, "cue14": -0.1479, "cue6": -0.2083}
NEAR = 0.005
FIRES = 0.010
ALIGNED = 0.5
NULL_ALIGNED = 0.3
CLAIMS = (
    ("AB1", "and the six bodies start from one body",
     "For every replicate the six initial weight arrays are identical",
     "falsifier: any of them differing on any replicate"),
    ("AB2", f"and how far the training moved them does not separate the one, within {NEAR:.3f}",
     "The card's world's mean relative movement lies within 0.005 of the range the five failing worlds' means span",
     f"falsifier: outside it by more than {FIRES:.3f}"),
    ("AB3", f"and the movements are not one direction, under {ALIGNED:.1f}",
     "Every world's mean cosine with the other five is below 0.5",
     f"falsifier: any world at or above {ALIGNED:.1f}; null: between {NULL_ALIGNED:.1f} and {ALIGNED:.1f}"),
    ("AB4", "and the card's body is not an outlier among them",
     "Its mean cosine with the other five lies inside the range the five failing worlds' mean cosines span",
     "falsifier: outside that range"),
    ("AB5", "and the head does not separate it either",
     "The card's trained head reads task 0 inside the range the five failing worlds' heads span",
     "falsifier: outside it"),
)


def reading(bodies: dict = BODIES, replicates=REPLICATES) -> dict:
    out = {"ok": True, "reason": None, "bodies": {}, "replicates": len(replicates), "movement": {},
           "alignment": {}, "heads": dict(HEADS), "gains": dict(GAINS)}
    initial = None
    same = {}
    deltas = {}
    for name, d in bodies.items():
        rel, first = [], None
        for r in replicates:
            p = Path(d) / f"naive_seed{r}.npz"
            if not p.is_file():
                return {**out, "ok": False, "reason": f"world {name}: {p} is absent"}
            z = np.load(p)
            ti = z["theta_initial"].ravel().astype(np.float64)
            ta = z["after_task_0"].ravel().astype(np.float64)
            if initial is None:
                initial = ti.copy()
            same.setdefault(r, True)
            same[r] = same[r] and bool(np.array_equal(ti, initial))
            rel.append(float(np.linalg.norm(ta - ti) / np.linalg.norm(ti)))
            deltas[(name, r)] = ta - ti
        out["movement"][name] = {"mean": statistics.fmean(rel),
                                 "sem": statistics.stdev(rel) / len(rel) ** 0.5 if len(rel) > 1 else 0.0,
                                 "min": min(rel), "max": max(rel)}
    out["one_initial_body"] = all(same.values())
    names = list(bodies)
    for name in names:
        cs = [float(deltas[(name, r)] @ deltas[(m, r)]
                    / (np.linalg.norm(deltas[(name, r)]) * np.linalg.norm(deltas[(m, r)])))
              for m in names if m != name for r in replicates]
        out["alignment"][name] = {"mean_cosine": statistics.fmean(cs), "max_cosine": max(cs),
                                  "min_cosine": min(cs)}
        out["bodies"][name] = {"mean_movement": out["movement"][name]["mean"],
                               "mean_cosine": out["alignment"][name]["mean_cosine"],
                               "head_task_0": HEADS.get(name), "gain": GAINS.get(name)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a body's weights are absent"} for c in CLAIMS]
    j1 = {"id": "AB1", "measured": f"over {r['replicates']} replicates and {len(r['bodies'])} worlds the initial "
                                   f"arrays are identical: {r['one_initial_body']}",
          "verdict": "MET -- the six bodies start from the connectome's own weights and not from a per-world draw"
          if r["one_initial_body"] else
          "FALSIFIER FIRED -- the initial bodies differ, so every comparison below is of two starting points"}

    losers = [v["mean"] for n, v in r["movement"].items() if n != "card"]
    card = r["movement"]["card"]["mean"]
    gap = max(0.0, min(losers) - card, card - max(losers))
    j2 = {"id": "AB2", "measured": f"the card's world's mean relative movement is {card:.4f} against the five "
                                   f"failing worlds' {[round(v, 4) for v in sorted(losers)]}, so it is {gap:.4f} "
                                   f"outside their range",
          "verdict": f"MET -- how far the training walked does not separate the one, {gap:.4f} outside" if
                     gap <= NEAR else
          f"FALSIFIER FIRED -- {gap:.4f} outside the failing worlds' range" if gap > FIRES else
          f"NULL -- {gap:.4f}, between {NEAR:.3f} and {FIRES:.3f}"}

    worst = max(v["mean_cosine"] for v in r["alignment"].values())
    j3 = {"id": "AB3", "measured": f"the six worlds' mean cosines with each other are "
                                   f"{ {n: round(v['mean_cosine'], 4) for n, v in r['alignment'].items()} }, the "
                                   f"largest {worst:.4f}",
          "verdict": f"MET -- the six updates are near-orthogonal, largest {worst:.4f}" if worst < NULL_ALIGNED else
          f"FALSIFIER FIRED -- a world at {worst:.4f}" if worst >= ALIGNED else
          f"NULL -- {worst:.4f}, between {NULL_ALIGNED:.1f} and {ALIGNED:.1f}"}

    lcos = [v["mean_cosine"] for n, v in r["alignment"].items() if n != "card"]
    ccos = r["alignment"]["card"]["mean_cosine"]
    good4 = min(lcos) <= ccos <= max(lcos)
    j4 = {"id": "AB4", "measured": f"the card's mean cosine is {ccos:+.4f} against the five failing worlds' "
                                   f"{[round(v, 4) for v in sorted(lcos)]}",
          "verdict": "MET -- the card's body is not an outlier among them" if good4 else
          f"FALSIFIER FIRED -- {ccos:+.4f} is outside the failing worlds' range"}

    lhead = [v for n, v in r["heads"].items() if n != "card"]
    chead = r["heads"]["card"]
    good5 = min(lhead) <= chead <= max(lhead)
    j5 = {"id": "AB5", "measured": f"the card's trained head reads {chead:.4f} against the five failing worlds' "
                                   f"{sorted(lhead)}",
          "verdict": "MET -- the head does not separate it either" if good5 else
          f"FALSIFIER FIRED -- {chead:.4f} is outside the failing heads' range"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the trained bodies ==")
        print(f"   REFUSED -- {r.get('reason', 'a body is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the trained bodies ==")
    print(f"   {len(r['bodies'])} worlds' 500-update bodies, {r['replicates']} replicates each, against the "
          f"connectome's own weights they started from")
    print(f"\n   {'world':>7} {'gain':>9} {'move (mean)':>12} {'sem':>8} {'mean cos':>9} {'head':>7}")
    for name in sorted(r["bodies"], key=lambda n: r["bodies"][n]["gain"]):
        v = r["bodies"][name]
        print(f"   {name:>7} {v['gain']:9.4f} {r['movement'][name]['mean']:12.4f} "
              f"{r['movement'][name]['sem']:8.5f} {v['mean_cosine']:+9.4f} "
              f"{v['head_task_0'] if v['head_task_0'] is not None else float('nan'):7.4f}")

    print("\n== the registered claims, AB1-AB5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e401` retired the last near-geometry candidate and named the trained body as what was left;")
    print("    this measures the bodies' movement and their mutual alignment, rolling nothing)")
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
