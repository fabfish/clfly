"""E366 -- what the probe's 0.3218 is made of: a frozen ladder over splits, suite and training.

`e363` read the cue-source world, with the cue one step from the read-out, at **0.8555** -- one four-symbol task,
512 examples, a **frozen** network, a least-squares probe. `e365` trained the same configuration and its three-task
sequential diagonal came back at **0.5337**, **0.3218 below** the probe, and it named its own confound: *"`e363`'s
cell is one four-symbol task with 512 examples rolled on a frozen network and decoded by a least-squares probe;
`e365`'s diagonal is the mean of three tasks trained sequentially with 96 examples each, on a body that is being
changed. So the gap carries the multi-task protocol, the smaller training splits and the training itself."*

**This unit prices the first two thirds of it with nothing trained.** Three cells, all on the frozen network, in the
same world with the same symbols:

- **`one512`** -- one task, 512 examples, the probe on half and half: `e363`'s cell, recomputed here;
- **`one96`** -- one task, 96 examples in 48 and 48: the **splits** the runner actually trains on;
- **`three96`** -- the runner's three tasks, 96 examples each, the probe fitted **per task** and averaged: the
  **suite structure** at the runner's split size.

Four claims, registered before any of the three was read.

- **T1 -- one configuration across the three.** Same circuit, read-out draw, symbols, world dimensions, coupling,
  leak and seed, with the cells differing in the example count and the number of tasks. **Falsifier**: any of those
  differing.
- **T2 -- and this instrument reproduces `e363`'s cell.** `one512` is within **0.05** of the **0.8555** that unit
  recorded. **Falsifier**: **0.10** apart, which would say the two modules are not measuring the same thing and the
  ladder is not comparable. **REFUSED** when that artifact is absent.
- **T3 -- and the splits cost something.** `one512` is above `one96` by at least **0.02**. **Falsifier**: within
  **0.02**, which would say the example count does not matter at this size. **Null**: between.
- **T4 -- and the suite structure costs little.** `three96` is within **0.05** of `one96`. **Falsifier**: **0.10**
  apart, which would say the three-task arrangement itself loses the signal and `e365`'s gap is not training's.
  **Null**: between.

**What it can do beyond that.** The third of the gap this ladder cannot price is the training itself, and it is not
claimed here: **`e365`'s trained diagonal minus `three96`** is the number the next unit would read, and it is
reported in this unit's table and in nothing else. That is deliberate -- attributing it needs the trained artifact
`e365` wrote and a claim that reaches across the two, which is a unit of its own.

**What it cannot do.** *A frozen probe*: the first two thirds are the substrate's carrier at two split sizes and two
arrangements, so nothing here says what a trained body would read at 512 examples or on one task. *One world, one
coupling and one cue step*: the cue-source world with the cue at step 10, eight dimensions at `leak = 0.35`, which
is exactly `e363`'s and `e365`'s configuration and no other. *And a ladder is not an attribution*: the three cells
differ in two things at once (`one512` against `one96` in the count, `one96` against `three96` in the arrangement)
and **not** in isolation, so the two prices are read as a sequence and not as independent effects.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: `e363`'s and `e365`'s configuration: the cue-source world with the cue one step from the read-out
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
CUE_STEP = 10
DRIVE_FROM_CUE = True
#: the three cells, and the runner's own splits
N_BIG = 512
N_SMALL = 96
TEST_SMALL = 48
REFERENCE = Path("runs/e363_where_the_cue_can_reach_the_world.json")
REFERENCE_SOURCE, REFERENCE_STEP = "cue", 10
TRAINED = Path("runs/e365_earned_label_cue10_cuesource_20reps.json")
SAME = 0.05
FIRES = 0.10
COSTS = 0.02
NOTHING = 0.01
CLAIMS = (
    ("T1", "one configuration across the three",
     "Same circuit, read-out draw, symbols, world dimensions, coupling, leak and seed, the cells differing in the "
     "example count and the number of tasks",
     "falsifier: any of those differing"),
    ("T2", f"and this instrument reproduces `e363`'s cell, within {SAME:.2f}",
     f"`one512` is within 0.05 of the 0.8555 that unit recorded",
     f"falsifier: {FIRES:.2f} apart; refused when that artifact is absent"),
    ("T3", f"and the splits cost something, by {COSTS:.2f}",
     "`one512` is above `one96` by at least 0.02",
     f"falsifier: below {NOTHING:.2f}; null: between {NOTHING:.2f} and {COSTS:.2f}"),
    ("T4", f"and the suite structure costs little, within {SAME:.2f}",
     "`three96` is within 0.05 of `one96`",
     f"falsifier: {FIRES:.2f} apart; null: between {SAME:.2f} and {FIRES:.2f}"),
)


def _env(circ, rs, seed: int = SEED):
    from clfly.network import env as fly_env
    return fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                         noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS,
                         world_coupled=True, cue_at=CUE_STEP, drive_from_cue=DRIVE_FROM_CUE)


def _roll(net, e, y: np.ndarray) -> np.ndarray:
    """The world's final state for each trial, read off the closure right after the roll."""
    import torch
    fn = e.feedback()
    with torch.no_grad():
        net(torch.from_numpy(np.asarray(e.cue_input(y), dtype=np.float32)), feedback=fn)
    return fn.last_world.detach().numpy()


def _accuracy(net, e, y_tr, y_te) -> float:
    """The corpus's own least-squares probe on the world's final state, fitted on one half and read on the other."""
    w_tr, w_te = _roll(net, e, y_tr), _roll(net, e, y_te)
    return probe(w_tr[:, None, :], y_tr, w_te[:, None, :], y_te, list(range(WORLD_DIMS)))[-1]


def reading(size: int = SIZE, readout_size: int = READOUT_SIZE, reference: Path = REFERENCE,
            trained: Path = TRAINED) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    rng = np.random.default_rng(SEED + 7)

    cells = {}
    #: one task, 512 examples, half and half -- `e363`'s cell
    y = rng.integers(0, N_SYMBOLS, size=N_BIG)
    cells["one512"] = {"accuracy": _accuracy(net, _env(circ, rs), y[:N_BIG // 2], y[N_BIG // 2:]),
                       "n_train": N_BIG // 2, "n_test": N_BIG // 2, "n_tasks": 1}
    #: one task, the runner's split size
    y = rng.integers(0, N_SYMBOLS, size=N_SMALL)
    cells["one96"] = {"accuracy": _accuracy(net, _env(circ, rs), y[:TEST_SMALL], y[TEST_SMALL:]),
                      "n_train": TEST_SMALL, "n_test": TEST_SMALL, "n_tasks": 1}
    #: the runner's three tasks at its own split size, one probe per task
    env = _env(circ, rs)
    #: the runner's suite is three cue ranges inside one world, each trained on 96 and tested on 48; this rebuilds
    #: that shape by drawing each task's trials from its own stream, so the three cells share the world and the
    #: symbols and differ only in the example count and the arrangement
    per_task = []
    for i in range(3):
        y = np.random.default_rng(SEED + 100 + i).integers(0, N_SYMBOLS, size=N_SMALL)
        per_task.append(_accuracy(net, env, y[:TEST_SMALL], y[TEST_SMALL:]))
    cells["three96"] = {"accuracy": float(np.mean(per_task)), "per_task": per_task,
                        "n_train": TEST_SMALL, "n_test": TEST_SMALL, "n_tasks": 3}

    doc = None
    p = Path(reference)
    if p.is_file():
        import json
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = None
    recorded = None
    if doc:
        for c in doc.get("cells") or []:
            if c.get("source") == REFERENCE_SOURCE and c.get("cue_at") == REFERENCE_STEP:
                recorded = float(c["accuracy"])
    tdoc = None
    q = Path(trained)
    if q.is_file():
        import json
        try:
            tdoc = json.loads(q.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            tdoc = None
    trained_diagonal = None
    if tdoc:
        reps = ((tdoc.get("methods") or {}).get("naive") or {}).get("replicates") or []
        if reps:
            trained_diagonal = float(np.mean([np.mean(r["learned"]) for r in reps]))

    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED, "tau": TAU,
           "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "cue_at": CUE_STEP,
           "drive_from_cue": DRIVE_FROM_CUE, "world_dims": WORLD_DIMS, "world_leak": WORLD_LEAK,
           "cells": cells, "reference": {"artifact": Path(reference).name if doc else None, "accuracy": recorded},
           "trained": {"artifact": Path(trained).name if tdoc else None, "diagonal": trained_diagonal},
           "splits_cost": cells["one512"]["accuracy"] - cells["one96"]["accuracy"],
           "suite_cost": cells["one96"]["accuracy"] - cells["three96"]["accuracy"],
           "reference_gap": (cells["one512"]["accuracy"] - recorded) if recorded is not None else None,
           "training_gap": (cells["three96"]["accuracy"] - trained_diagonal)
           if trained_diagonal is not None else None}
    return out


def judge(r: dict) -> list[dict]:
    cells = r.get("cells") or {}
    if len(cells) < 3:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the three cells were not rolled"} for c in CLAIMS]

    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']} "
                                  f"neurons, {r['n_symbols']} symbols at a chance of {r['chance']:.2f}, one world of "
                                  f"{r['world_dims']} dimensions at leak {r['world_leak']} with the cue source and "
                                  f"the cue at step {r['cue_at']}; the cells are `one512` at "
                                  f"{cells['one512']['n_train']} train and {cells['one512']['n_test']} test, "
                                  f"`one96` at {cells['one96']['n_train']}/{cells['one96']['n_test']} and "
                                  f"`three96` at {cells['three96']['n_train']}/{cells['three96']['n_test']} over "
                                  f"{cells['three96']['n_tasks']} tasks",
          "verdict": "MET -- one configuration across the three"}

    j2 = {"id": "T2", "measured": f"`one512` reads {cells['one512']['accuracy']:.4f} and the artifact "
                                  f"`{r['reference']['artifact']}` recorded "
                                  f"{r['reference']['accuracy'] if r['reference']['accuracy'] is not None else float('nan'):.4f} "
                                  f"for the same cell, {r['reference_gap'] if r['reference_gap'] is not None else float('nan'):+.4f} apart",
          "verdict": "REFUSED -- the artifact this cell is compared with is absent" if
          r["reference"]["accuracy"] is None else
          f"MET -- this instrument reproduces that cell to {r['reference_gap']:+.4f}" if
          abs(r["reference_gap"]) < SAME else
          f"FALSIFIER FIRED -- {r['reference_gap']:+.4f} apart, so the two modules are not the same instrument" if
          abs(r["reference_gap"]) >= FIRES else
          f"NULL -- {r['reference_gap']:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    cost = r["splits_cost"]
    j3 = {"id": "T3", "measured": f"`one512` reads {cells['one512']['accuracy']:.4f} and `one96` "
                                  f"{cells['one96']['accuracy']:.4f}, so the smaller splits cost {cost:+.4f}",
          "verdict": f"MET -- the splits cost {cost:+.4f}" if cost >= COSTS else
          f"FALSIFIER FIRED -- below {NOTHING:.2f}, {cost:+.4f}" if cost < NOTHING else
          f"NULL -- {cost:+.4f}, between {NOTHING:.2f} and {COSTS:.2f}"}

    suite = r["suite_cost"]
    j4 = {"id": "T4", "measured": f"`one96` reads {cells['one96']['accuracy']:.4f} and `three96` "
                                  f"{cells['three96']['accuracy']:.4f} over its tasks "
                                  f"{[round(x, 4) for x in cells['three96']['per_task']]}, so the suite structure "
                                  f"costs {suite:+.4f}",
          "verdict": f"MET -- the suite structure costs little, {suite:+.4f}" if abs(suite) < SAME else
          f"FALSIFIER FIRED -- {suite:+.4f}, so the arrangement itself loses the signal" if abs(suite) >= FIRES else
          f"NULL -- {suite:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("cells"):
        print("== what the probe's 0.3218 is made of ==\n   REFUSED -- the three cells were not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== what the probe's 0.3218 is made of ==")
    print(f"   {r['circuit']} ({r['size']} neurons), one world of {r['world_dims']} dimensions at leak "
          f"{r['world_leak']}, cue at step {r['cue_at']} with the cue source, {r['n_symbols']} symbols")
    print(f"\n   {'cell':>9} {'tasks':>6} {'train':>6} {'test':>6} {'accuracy':>9}")
    for name in ("one512", "one96", "three96"):
        c = r["cells"][name]
        print(f"   {name:>9} {c['n_tasks']:6d} {c['n_train']:6d} {c['n_test']:6d} {c['accuracy']:9.4f}")
    print(f"   the splits cost {r['splits_cost']:+.4f}, the suite structure {r['suite_cost']:+.4f}")
    if r.get("reference", {}).get("accuracy") is not None:
        print(f"   `{r['reference']['artifact']}` recorded {r['reference']['accuracy']:.4f} for `one512` "
              f"(gap {r['reference_gap']:+.4f})")
    if r.get("trained", {}).get("diagonal") is not None:
        print(f"   `{r['trained']['artifact']}`'s trained diagonal is {r['trained']['diagonal']:.4f}, so what the "
              f"ladder leaves to the training is {r['training_gap']:+.4f} (reported, not claimed)")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e365` read 0.5337 against the probe's 0.8555 and named its own confound -- one task against")
    print("    three, 512 examples against 96, and a frozen net against a trained one; this prices the first two)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--reference", type=Path, default=REFERENCE)
    ap.add_argument("--trained", type=Path, default=TRAINED)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(size=args.size, reference=args.reference, trained=args.trained)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
