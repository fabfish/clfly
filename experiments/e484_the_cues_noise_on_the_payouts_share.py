"""E484 -- the cue's noise on the payout's cue-share: why `e483`'s second claim fired.

`e483` gave the environment a reward and closed on the one thing there that it could not do: *"the cue's noise is one
setting: `noise = 1.0` is the corpus's own, and a noisier or quieter cue would move the margin RA2 fired on, which is
a sweep this unit does not run."* **This unit runs it.** The same payout, the same world and the same eight
replicates, with the cue's noise at **five levels** -- `0`, `0.25`, `0.5`, `1.0` (the corpus's own) and `2.0` -- three
of them quieter than the setting `e483`'s falsifier fired at.

The mechanism the sweep is against is the payout's own definition: the goal is a **linear read of the cue's activity one
step after the cue arrives**, so the noise the cue carries enters the goal as well as the world, and a noisier cue
should leave less of the payout to the symbol. Four claims, registered before any level was read.

- **SA1 -- and the level is the only field the sweep moves.** At each replicate the recorded draw fields agree across
  the five levels -- the populations, the cue templates, the drive's map, the read map, the coupling and the payout's
  own map -- since the cue's noise is an **amplitude on one realisation** and not a redraw. **Falsifier**: any draw
  field differing between two levels, or the payout's map not being one draw across them.
- **SA2 -- and a quieter cue carries more of the payout.** The across-minus-within margin at `noise = 0` exceeds the
  one at `noise = 1.0` by at least **1.00**, paired over the replicates, at **two** sigma or more. **Falsifier**: a
  gap below **0.50**, or one that does not resolve. **Null**: between.
- **SA3 -- and at a quiet cue the cue sets the payout.** At `noise = 0` the across-symbol spread exceeds the
  within-symbol spread on **every** replicate. **Falsifier**: any replicate not separating them. *This is `e483`'s
  RA2, which fired at `noise = 1.0`, asked again where the cue is exact.*
- **SA4 -- and the payout is still earned where the cue is exact.** At `noise = 0` the trained policy's payout exceeds
  the identity policy's by at least **1.00**, paired, at **two** sigma or more. **Falsifier**: a gain below **0.30**,
  or one that does not resolve. **Null**: between. *The bar is lower than `e483`'s 2.00 because that unit measured
  **+1.4600** at the noisier setting and this unit does not raise a bar the corpus has already missed.*

**What it can do beyond that.** It says whether a fired claim was fired by the game or by the instrument: `e483`'s RA2
said the cue's share of the payout is under the payout's own noise, and this unit says whether that is a fact about
this payout or a fact about the cue's amplitude.

**What it cannot do.** *One payout and one map*: the goal is a linear read of the cue through one drawn map, so a
nonlinear or sparser goal is not in it. *And one axis*: the noise is the cue's and not the world's, whose dynamics add
scatter this sweep does not move. *And five levels are a ladder and not a curve*: no point between them is measured.
*And the body is frozen*: the policy is 64 numbers over the action population. *And the payout is not the benchmark's*:
the runner does not carry the flag. *And eight replicates are not the population*: the sigma is the paired one over
the worlds the replicates share.
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
from experiments import e483_the_environment_pays_a_reward as e483

#: the ladder of cue noises, the corpus's own `1.0` in the middle and three of them quieter
NOISES = (0.0, 0.25, 0.5, 1.0, 2.0)
REPLICATES = e483.REPLICATES
SIZE = e483.SIZE
READOUT_SIZE = e483.READOUT_SIZE
#: the two ends the claims compare, named so a reader of the artifact does not have to guess
QUIET = 0.0
CORPUS = 1.0
SIGMA = 2.0
MARGIN_BAR = 1.00
MARGIN_FLOOR = 0.50
GAIN_BAR = 1.00
GAIN_FLOOR = 0.30
CLAIMS = (
    ("SA1", "and the level is the only field the sweep moves",
     "At each replicate the recorded draw fields agree across the five levels, the payout's own map included, since the "
     "cue's noise is an amplitude on one realisation and not a redraw",
     "falsifier: any draw field differing between two levels, or the payout's map not being one draw across them"),
    ("SA2", f"and a quieter cue carries more of the payout, by {MARGIN_BAR:.2f} at {SIGMA:.0f} sigma",
     "The across-minus-within margin at noise 0 exceeds the one at noise 1.0 by at least 1.00, paired over the "
     "replicates, at two sigma or more",
     f"falsifier: a gap below {MARGIN_FLOOR:.2f}, or one that does not resolve"),
    ("SA3", "and at a quiet cue the cue sets the payout",
     "At noise 0 the across-symbol spread exceeds the within-symbol spread on every replicate",
     "falsifier: any replicate not separating them"),
    ("SA4", f"and the payout is still earned where the cue is exact, by {GAIN_BAR:.2f} at {SIGMA:.0f} sigma",
     "At noise 0 the trained policy's payout exceeds the identity policy's by at least 1.00, paired, at two sigma or "
     "more",
     f"falsifier: a gain below {GAIN_FLOOR:.2f}, or one that does not resolve"),
)


def key(noise: float) -> str:
    return f"{noise:g}"


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(noises=NOISES, replicates=REPLICATES, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(e483.SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=e483.TAU)).torch_model()
    levels = [key(n) for n in noises]
    cells = {k: [e483.one_replicate(circ, net, int(r), noise=float(n)) for r in replicates]
             for k, n in zip(levels, noises)}
    out = {"ok": True, "reason": None, "cells": cells, "margin": {}, "gain": {}, "levels": {}, "spans": {},
           "worlds": {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": e483.SEED,
                      "tau": e483.TAU, "n_symbols": e483.N_SYMBOLS, "dims": e483.WORLD_DIMS,
                      "leak": e483.WORLD_LEAK, "noises": levels, "replicates": list(map(int, replicates)),
                      "steps": e483.STEPS, "lr": e483.LR, "quiet": key(QUIET), "corpus": key(CORPUS)}}
    out["margin"] = {k: _paired([c["across"] for c in cells[k]], [c["within"] for c in cells[k]]) for k in levels}
    out["gain"] = {k: _paired([c["trained"] for c in cells[k]], [c["identity"] for c in cells[k]]) for k in levels}
    out["levels"] = {k: {"across": [round(c["across"], 4) for c in cells[k]],
                         "within": [round(c["within"], 4) for c in cells[k]],
                         "identity": [round(c["identity"], 4) for c in cells[k]],
                         "trained": [round(c["trained"], 4) for c in cells[k]],
                         "separating": sum(1 for c in cells[k] if c["across"] > c["within"]),
                         "reward_sha1": [c["reward_sha1"] for c in cells[k]]} for k in levels}
    #: SA1 -- the draw fields across the levels, at each replicate
    fields = e483.DRAW_FIELDS
    differ = {}
    for k in levels:
        in_level = sorted({f for c in cells[k] for f, v in c["draw_agrees"].items() if not v})
        if in_level:
            differ[k] = in_level
    cross = {f for f in fields
             if len({tuple(c["draw_agrees"][f] for c in cells[k]) for k in levels}) > 1}
    out["spans"] = {
        "levels": levels, "replicates": len(replicates), "fields": len(fields),
        "within_level_differ": differ, "across_level_differ": sorted(cross),
        "reward_sha1_one_draw": all(len({cells[k][i]["reward_sha1"] for k in levels}) == 1
                                    for i in range(len(replicates))),
        "target_spread": {k: [round(c["target_spread"], 4) for c in cells[k]] for k in levels},
        "late_target_max": max(c["late_target_max"] for k in levels for c in cells[k]),
        "moves": {k: [round(c["move"], 3) for c in cells[k]] for k in levels},
    }
    out["pair"] = _paired([c["across"] - c["within"] for c in cells[key(QUIET)]],
                          [c["across"] - c["within"] for c in cells[key(CORPUS)]])
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok") or len(r.get("cells") or {}) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the ladder was not walked"} for c in CLAIMS]
    s = r["spans"]
    q, c_ = s["levels"][0], key(CORPUS)
    j1 = {"id": "SA1",
          "measured": f"{s['fields']} draw fields at {s['replicates']} replicates over the levels {s['levels']}: "
                      f"within a level {s['within_level_differ']} differ and across them {s['across_level_differ']} "
                      f"do, with the payout's map one draw across every level "
                      f"{s['reward_sha1_one_draw']}",
          "verdict": "MET -- the level is the only field the sweep moves, and the payout's map is one draw" if
                     (not s["within_level_differ"] and not s["across_level_differ"] and s["reward_sha1_one_draw"]) else
                     f"FALSIFIER FIRED -- differing within {s['within_level_differ']} and across "
                     f"{s['across_level_differ']}, one draw {s['reward_sha1_one_draw']}"}
    p = r["pair"]
    j2 = {"id": "SA2",
          "measured": f"the margin runs "
                      f"{ {k: round(v['mean'], 4) for k, v in r['margin'].items()} }, so the quiet cue's is "
                      f"**{p['mean']:+.4f}** above the corpus's at **{p['sigma']:+.2f}** sigma",
          "verdict": f"MET -- a quieter cue carries more of the payout, by {p['mean']:+.4f} at {p['sigma']:+.2f} "
                     f"sigma" if (p["mean"] >= MARGIN_BAR and p["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- a gap of {p['mean']:+.4f} at {p['sigma']:+.2f} sigma, against a bar of "
                     f"{MARGIN_BAR:.2f}" if (p["mean"] < MARGIN_FLOOR or p["sigma"] < SIGMA) else
                     f"NULL -- a gap of {p['mean']:+.4f} between {MARGIN_FLOOR:.2f} and {MARGIN_BAR:.2f}"}
    sep = r["levels"][q]["separating"]
    j3 = {"id": "SA3",
          "measured": f"at `noise = {q}` the across-symbol spread is {r['levels'][q]['across']} against the "
                      f"within-symbol spread {r['levels'][q]['within']}, separating them on **{sep} of "
                      f"{s['replicates']}** replicates (the corpus's level separates "
                      f"{r['levels'][c_]['separating']} of {s['replicates']})",
          "verdict": f"MET -- at an exact cue the cue sets the payout on every replicate" if sep == s["replicates"]
                     else f"FALSIFIER FIRED -- the quiet level separates {sep} of {s['replicates']}"}
    g = r["gain"][q]
    j4 = {"id": "SA4",
          "measured": f"at `noise = {q}` the payout runs {r['levels'][q]['identity']} at the identity policy and "
                      f"{r['levels'][q]['trained']} trained, a paired gain of **{g['mean']:+.4f}** at "
                      f"**{g['sigma']:+.2f}** sigma (the corpus's level {r['gain'][c_]['mean']:+.4f} at "
                      f"{r['gain'][c_]['sigma']:+.2f})",
          "verdict": f"MET -- the payout is earned where the cue is exact, {g['mean']:+.4f} at {g['sigma']:+.2f} "
                     f"sigma" if (g["mean"] >= GAIN_BAR and g["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- a gain of {g['mean']:+.4f} at {g['sigma']:+.2f} sigma, against a bar of "
                     f"{GAIN_BAR:.2f}" if (g["mean"] < GAIN_FLOOR or g["sigma"] < SIGMA) else
                     f"NULL -- a gain of {g['mean']:+.4f} between {GAIN_FLOOR:.2f} and {GAIN_BAR:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the cue's noise on the payout's cue-share ==")
    if not r.get("ok") or len(r.get("cells") or {}) < 2:
        print("   REFUSED -- the ladder was not walked")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    w = r["worlds"]
    print(f"   circuit {w['circuit']} ({w['size']} neurons), the card's {w['dims']}-dimensional coupled world, "
          f"{w['n_symbols']} cue symbols, the cue noise at {w['noises']}, {w['replicates']} replicates")
    print(f"\n   {'noise':>6} {'margin':>9} {'sigma':>8} {'separating':>11} {'identity':>10} {'trained':>10} "
          f"{'gain':>8} {'sigma':>8}")
    for k in w["noises"]:
        m, g = r["margin"][k], r["gain"][k]
        print(f"   {k:>6} {m['mean']:>+9.4f} {m['sigma']:>8.2f} "
              f"{str(r['levels'][k]['separating']) + '/' + str(w['replicates']):>11} "
              f"{statistics.fmean(r['levels'][k]['identity']):>10.4f} "
              f"{statistics.fmean(r['levels'][k]['trained']):>10.4f} {g['mean']:>+8.4f} {g['sigma']:>8.2f}")
    print(f"\n   the payout's map is one draw across every level: {r['spans']['reward_sha1_one_draw']}")
    print("\n== the registered claims, SA1-SA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e483`'s RA2 fired at the corpus's own cue noise and named this sweep as what it could not run;")
    print("    this unit walks it, three of the five levels quieter than the one that fired)")
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
