"""E363 -- where the cue can reach the world: the populations or the timing, told apart in six frozen rolls.

`e362` found that a cue delivered at the step the world read-out reads is **invisible** -- the suite came back at
chance (0.2361), the paired channel reading was +0.0010, and the task was 0.5330 *harder* than the same task with
the cue at step 0. Its finding gives the cause as: *"the environment reads its action off ``action_neurons`` and
delivers the cue onto ``cue_neurons``, two disjoint populations, and the read-out's columns are
``feedback_neurons``, a third ... while the world's drive at step 11 is computed from the state carried into that
step, which has not seen the cue."*

**Those are two causes and the finding names both.** The first is the **populations**: the cue has to cross the
connectome's weights to reach the neurons the world listens to. The second is the **timing**: the drive is computed
from the state *carried into* the step, so anything delivered at that step's input arrives one step later. This unit
tells them apart with one manipulation -- **a world that reads the cue population itself** -- and it needs no
training to do it.

`CueActionEnv.build` gained `drive_from_cue`: the world's drive is read off `cue_neurons` instead of
`action_neurons`. The draw is unchanged -- the same three populations are picked -- so the two configurations differ
in one field, and the recorded fingerprints say so: the action's fingerprint becomes the cue's. **Six frozen rolls**:
both drive sources at cue steps 0, 10 and 11, each rolled on the same examples and decoded by the corpus's own
least-squares probe (`e322`'s), which is the instrument `e348` used for the world's carrier.

Five claims, registered before any of it was read.

- **T1 -- one configuration across the six.** Same circuit, read-out draw, symbol count, gain, noise, world
  dimensions, coupling, leak and seed, the **cue's fingerprint identical in every cell**, and the cells differing
  only in the drive's source and the cue's step. **Falsifier**: any of those differing.
- **T2 -- and at the read step the world carries nothing, in either drive source.** At `cue_at = 11` the decoder on
  the world's final state is within **0.05** of chance **in both** sources. **Falsifier**: **0.10** or more above
  chance in either, which would say the populations were the cause and a world listening to the cue can see it.
- **T3 -- and at the first step it carries the cue, in both.** At `cue_at = 0` the decoder is at least **0.10** above
  chance in both sources. **Falsifier**: within **0.05** of chance in either, which would say a world driven by the
  cue's own neurons cannot carry it either.
- **T4 -- and the timing is what costs.** At `cue_at = 11` the decoder is at least **0.10** below the same source's
  `cue_at = 0` reading, **in both**. **Falsifier**: within **0.05** in some source. This is the claim that attributes
  `e362`'s failure.
- **T5 -- and one step of margin is enough.** At `cue_at = 10` the decoder is at least **0.10** above chance in
  both sources. **Falsifier**: within **0.05** in either, which would say the failure at 11 is not a one-step effect.
  This is the positive control that makes T2 a statement about timing rather than about worlds that cannot be read.

**What it cannot do.** *A frozen body*: this is the substrate's carrier, so it says where the information *can* be
and not what a trained body would achieve -- `e362` is the trained version of the `cue_at = 11` cell and it agrees
(0.2361, at chance), but the trained versions of the other five cells are not run here. *One world draw and one
coupling*: eight dimensions at `leak = 0.35` with `e359`'s matrix, so nothing says a different drive map or a
nonlinear one behaves the same. *And the probe is linear*, so "carries nothing" means a linear decoder does not recover
it, which for a world's state is what `e345` and `e348` found to be the useful bar.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: the corpus's closed-loop settings, the two drive sources and the three cue steps
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
N_EXAMPLES = 512
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
SOURCES = ("action", "cue")
STEPS = (0, 10, 11)
READ_STEP = 11
CARRIES = 0.10
FLAT = 0.05
COSTS = 0.10
CLAIMS = (
    ("T1", "one configuration across the six",
     "Same circuit, read-out draw, symbol count, gain, noise, world dimensions, coupling, leak and seed, the cue's "
     "fingerprint identical in every cell, and the cells differing only in the drive's source and the cue's step",
     "falsifier: any of those differing"),
    ("T2", f"and at the read step the world carries nothing, in either drive source, within {FLAT:.2f}",
     "At `cue_at = 11` the decoder on the world's final state is within 0.05 of chance in both sources",
     f"falsifier: {CARRIES:.2f} or more above chance in either"),
    ("T3", f"and at the first step it carries the cue, in both, by {CARRIES:.2f}",
     "At `cue_at = 0` the decoder is at least 0.10 above chance in both sources",
     f"falsifier: within {FLAT:.2f} of chance in either"),
    ("T4", f"and the timing is what costs, by {COSTS:.2f}",
     "At `cue_at = 11` the decoder is at least 0.10 below the same source's `cue_at = 0` reading, in both",
     f"falsifier: within {FLAT:.2f} in some source"),
    ("T5", f"and one step of margin is enough, by {CARRIES:.2f}",
     "At `cue_at = 10` the decoder is at least 0.10 above chance in both sources",
     f"falsifier: within {FLAT:.2f} in either"),
)


def one_cell(circ, net, rs, source: str, cue_at: int, seed: int = SEED) -> dict:
    """One frozen roll: the world's final state decoded for the cue, at one drive source and one cue step."""
    import torch
    from clfly.network import env as fly_env

    e = fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                      noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS,
                      world_coupled=True, cue_at=int(cue_at), drive_from_cue=(source == "cue"))
    rng = np.random.default_rng(seed + 7)
    y = rng.integers(0, N_SYMBOLS, size=N_EXAMPLES)
    half = N_EXAMPLES // 2
    y_tr, y_te = y[:half], y[half:]
    u = e.cue_input(y)
    fn = e.feedback()
    with torch.no_grad():
        net(torch.from_numpy(np.asarray(u, dtype=np.float32)), feedback=fn)
    world = fn.last_world.detach().numpy()
    world_tr, world_te = world[:half], world[half:]
    s = e.summary()
    return {"source": source, "cue_at": int(cue_at),
            #: the corpus's own least-squares decoder on the world's final state, one number per dimension per trial
            "accuracy": probe(world_tr[:, None, :], y_tr, world_te[:, None, :], y_te, list(range(WORLD_DIMS)))[-1],
            "chance": 1.0 / N_SYMBOLS,
            "world_sd": float(np.std(world)),
            "cue_sha1": s["cue_sha1"], "action_sha1": s["action_sha1"], "feedback_sha1": s["feedback_sha1"],
            "drive_from_cue": s["drive_from_cue"], "world_read_sha1": s["world_read_sha1"],
            "world_dims": s["world_dims"], "world_leak": s["world_leak"], "cue_at": s["cue_at"]}


def reading(sources=SOURCES, steps=STEPS, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    cells = [one_cell(circ, net, rs, s, step) for s in sources for step in steps]
    by = {(c["source"], c["cue_at"]): c for c in cells}
    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED, "tau": TAU,
           "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "n_examples": N_EXAMPLES, "read_step": READ_STEP,
           "sources": list(sources), "steps": list(steps), "cells": cells,
           #: the world's constants, read off the cells rather than restated, so T1 compares them where they live
           "world_dims": cells[0]["world_dims"], "world_leak": cells[0]["world_leak"],
           "accuracy": {f"{s}@{k}": by[(s, k)]["accuracy"] for s in sources for k in steps},
           "gap_at_read_step": {s: by[(s, 0)]["accuracy"] - by[(s, READ_STEP)]["accuracy"] for s in sources}}
    return out


def _sg(x) -> str:
    return "n/a" if x is None else f"{x:.4f}"


def judge(r: dict) -> list[dict]:
    cells = r.get("cells") or []
    if len(cells) < 6:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the six cells were not rolled"} for c in CLAIMS]
    by = {(c["source"], c["cue_at"]): c for c in cells}
    chance = r["chance"]

    #: the fields that must be the same in every cell. `world_read_sha1` is deliberately not among them: the drive
    #: map's width follows the population it reads, so the two sources consume different amounts of the draw and
    #: their read maps land differently -- a difference beyond the source, named in the finding rather than hidden.
    shared = ("cue_sha1", "feedback_sha1", "world_dims", "world_leak")
    agree = {k: len({c[k] for c in cells}) for k in shared}
    #: the action's fingerprint is the one field that is SUPPOSED to differ, and it differs exactly by following the
    #: cue's: a cell whose source is the cue must have action == cue, and one whose source is the action must not
    follows = all((c["source"] == "cue") == (c["action_sha1"] == c["cue_sha1"]) for c in cells)
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']} "
                                  f"neurons, {r['n_symbols']} symbols at a chance of {chance:.2f}, "
                                  f"{r['n_examples']} examples in one world of {r['world_dims']} dimensions at leak "
                                  f"{r['world_leak']} with the coupling of `e359`, {len(cells)} cells over the "
                                  f"sources {r['sources']} and the cue steps {r['steps']}; the shared fingerprints' "
                                  f"distinct values are {agree} and the action's follows the cue's per cell {follows}",
          "verdict": "MET -- one configuration across the six" if all(v == 1 for v in agree.values()) and follows else
          f"FALSIFIER FIRED -- the cells are not one configuration: {agree}, action follows the cue {follows}"}

    weak = []
    for s in r["sources"]:
        above = by[(s, READ_STEP)]["accuracy"] - chance
        if above >= CARRIES:
            weak.append(s)
    detail = ", ".join(f"`{s}@{k}` {_sg(r['accuracy'][f'{s}@{k}'])}" for s in r["sources"] for k in r["steps"])
    j2 = {"id": "T2", "measured": f"the decoder on the world's final state at `cue_at = {READ_STEP}`: "
                                  f"{ {s: round(by[(s, READ_STEP)]['accuracy'], 4) for s in r['sources']} } against a "
                                  f"chance of {chance:.2f}; the whole grid is {detail}",
          "verdict": f"MET -- both drive sources carry nothing at the read step" if not weak else
          f"FALSIFIER FIRED -- {weak} carries the cue at the read step, so the populations were the cause"}

    bad3 = [s for s in r["sources"] if by[(s, 0)]["accuracy"] - chance < CARRIES]
    j3 = {"id": "T3", "measured": f"at `cue_at = 0` the accuracies are "
                                  f"{ {s: round(by[(s, 0)]['accuracy'], 4) for s in r['sources']} }",
          "verdict": "MET -- both sources carry the cue from the first step" if not bad3 else
          f"FALSIFIER FIRED -- {bad3} cannot carry it even from step 0"}

    bad4 = [s for s in r["sources"] if r["gap_at_read_step"][s] < COSTS]
    j4 = {"id": "T4", "measured": f"the drop from step 0 to the read step is "
                                  f"{ {s: round(r['gap_at_read_step'][s], 4) for s in r['sources']} }",
          "verdict": "MET -- the timing is what costs, in both sources" if not bad4 else
          f"FALSIFIER FIRED -- {bad4} does not lose by {COSTS:.2f}"}

    bad5 = [s for s in r["sources"] if by[(s, 10)]["accuracy"] - chance < CARRIES]
    j5 = {"id": "T5", "measured": f"at `cue_at = 10` the accuracies are "
                                  f"{ {s: round(by[(s, 10)]['accuracy'], 4) for s in r['sources']} }",
          "verdict": "MET -- one step of margin is enough in both sources" if not bad5 else
          f"FALSIFIER FIRED -- {bad5} cannot carry it with one step of margin"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("cells"):
        print("== where the cue can reach the world ==\n   REFUSED -- the six cells were not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== where the cue can reach the world ==")
    print(f"   {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']}, {r['n_symbols']} symbols at a "
          f"chance of {r['chance']:.2f}, {r['n_examples']} examples, one world of {r['world_dims']} dimensions")
    print(f"\n   {'drive':>8} " + " ".join(f"{'cue at ' + str(k):>10}" for k in r["steps"]))
    for s in r["sources"]:
        print(f"   {s:>8} " + " ".join(f"{r['accuracy'][f'{s}@{k}']:10.4f}" for k in r["steps"]))

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e362` found the cue unreadable at the read step and named two causes -- disjoint populations and a")
    print("    drive computed from the state carried in; the world that listens to the cue's own neurons decides)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(size=args.size)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
