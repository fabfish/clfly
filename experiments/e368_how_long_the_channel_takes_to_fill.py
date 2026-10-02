"""E368 -- how long the channel takes to fill: the curve behind `e363`'s two points, and the invariance `e367` named.

`e367` trained the closed loop whose world's drive reads the agent's **own action population** with the cue one step
from the read-out and found the run **bit-identical** to the same source's run at the read step, all twenty
replicates of both arms, with the paired channel readings at **0.16** and **0.31 sigma**. It read that after its own
five claims were registered and reported rather than claimed the account: at step 11 the action population's input
is `W @ x_10` with `x_10` the zero vector, so `x_11[action]` is zero whatever the weights are, the world's drive is
exactly zero, and the world is at rest. `e363` had already recorded the number that says so -- `world_sd`, the
spread of the world's final state, is **exactly 0.0** for the action source at `cue@10` and `cue@11` while it is
**0.2029** at `cue@0` -- and no unit read it as anything but chance.

**This unit makes both into measurements of its own, and turns the two points into the curve a game needs.**

- **`e368`'s instrument**: one frozen circuit, one world of eight dimensions at `leak = 0.35` with the coupling of
  `e359`, four symbols, 512 examples, the corpus's own least-squares probe on the world's **final state** -- the
  instrument `e363` used, recomputed here at **every** cue step from 0 to 11 and both drive sources rather than at
  three steps.
- **and nine bodies**: the connectome's own weights with a zero bias, which is the untrained body every frozen unit
  in this line rolled, plus eight whose weights and biases are drawn at random on the same connectome mask. `e367`'s
  account is a statement about **every** body; a claim about it that rolled one body would not test it.

Four claims, registered before any cell of the curve was read.

- **W1 -- and the two at-rest cells reproduce `e363` exactly.** For the untrained body, the action source's world has
  a spread of **exactly 0.0** at `cue@10` and `cue@11`, and that artifact records **0.0** for the same two cells.
  **Falsifier**: any spread at either step here, or a recorded value that is not zero. **REFUSED** when that artifact
  is absent.
- **W2 -- and the world does not move with the trial, for any body.** At those two steps the action source's world's
  final state is identical across all 512 examples for **every** one of the nine bodies, and at least one body has a
  **nonzero** spread, so the invariance is not the at-rest case in disguise. **Falsifier**: any body whose final
  state moves with the trial, or every body at rest, in which case this claim is vacuous and is reported as such.
  *This is the claim the unit exists for.*
- **W3 -- and the channel is real in time.** The action source's world at `cue@0` is decodable: the probe clears
  chance by **0.05**. **Falsifier**: within **0.05** of chance, which would say the action channel never fills and
  `e363`'s **0.6602** for that cell does not reproduce.
- **W4 -- and the population's price is time.** Scanning the cue step downward from the read step, the last step at
  which a source's probe still clears chance by **0.05** is **earlier** for the action source than for the cue
  source: the world listening to the agent's own action needs more margin than the world listening to the cue.
  **Falsifier**: the action source clearing at the same step or a later one, which would say the two populations
  cost the same and `e363`'s separation is about something else.

**What it can do beyond that.** The curve itself is reported for both sources at every step -- probe accuracy and
the world's spread -- and it is the number a game built on this world needs: how many steps of margin a read-out of
the agent's own action requires before it carries anything. `e367`'s account is only checked at the two steps it
makes a statement about; the curve is what says where the channel turns on.

**What it cannot do.** *A frozen probe on one world draw*: the curve is the corpus's linear decoder on one coupling
matrix at `leak = 0.35`, so nothing here is a statement about a different drive map or a nonlinear world. *Nine
bodies and not every body*: the invariance is structural, since the state entering the world's last step is a
function of the state before the cue arrived, and the nine draws are a check on that argument and not a proof of it.
*And "clears chance" is a linear read-out at one split*: 512 examples in half and half sets the resolution at about
0.02, so a step within 0.05 of chance is unresolved and is reported as unresolved rather than as absent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: `e363`'s configuration, recomputed here at every cue step
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
SOURCES = ("cue", "action")
STEPS = tuple(range(TAU))
#: the two steps `e367` makes its statement about: the read step and the one before it
LATE = (TAU - 1, TAU - 2)
#: the bodies: the connectome's own weights with a zero bias, then draws on the same mask
UNTRAINED = "untrained"
BODIES = (UNTRAINED,) + tuple(f"draw{i}" for i in range(1, 9))
WEIGHT_SCALE, BIAS_SCALE = 0.05, 0.5
REFERENCE = Path("runs/e363_where_the_cue_can_reach_the_world.json")
EXACT = 1e-12
CLEARS = 0.05
CLAIMS = (
    ("W1", "and the two at-rest cells reproduce `e363` exactly",
     "For the untrained body the action source's world has a spread of exactly 0.0 at cue@10 and cue@11, and "
     "`e363` records 0.0 for the same two cells",
     "falsifier: any spread at either step, or a recorded value that is not zero; refused when that artifact is "
     "absent"),
    ("W2", f"and the world does not move with the trial, for any of the {len(BODIES)} bodies",
     "At those two steps the action source's world's final state is identical across all 512 examples for every "
     "body, and at least one body has a nonzero spread",
     "falsifier: any body whose final state moves with the trial, or every body at rest"),
    ("W3", f"and the channel is real in time, {CLEARS:.2f} over chance at the first step",
     "The action source's world at cue@0 is decodable: the probe clears chance by 0.05",
     f"falsifier: within {CLEARS:.2f} of chance"),
    ("W4", "and the population's price is time",
     "The last cue step at which a source clears chance by 0.05 is earlier for the action source than for the cue "
     "source",
     "falsifier: the action source clearing at the same step or a later one"),
)


def _env(circ, rs, source: str, cue_at: int, seed: int = SEED):
    from clfly.network import env as fly_env
    return fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                         noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS,
                         world_coupled=True, cue_at=int(cue_at), drive_from_cue=(source == "cue"))


def _body(net, name: str, rng):
    """The untrained body, or a draw of weights and biases on the same connectome mask."""
    model = net.torch_model()
    if name == UNTRAINED:
        return model
    import torch
    with torch.no_grad():
        theta = rng.standard_normal(model.theta.shape) * WEIGHT_SCALE
        bias = rng.standard_normal(model.bias.shape) * BIAS_SCALE
        model.theta.copy_(torch.from_numpy(theta.astype(np.float32)))
        model.bias.copy_(torch.from_numpy(bias.astype(np.float32)))
    return model


def _roll(model, e, y: np.ndarray) -> np.ndarray:
    """The world's final state for each trial, read off the closure right after the roll."""
    import torch
    fn = e.feedback()
    with torch.no_grad():
        model(torch.from_numpy(np.asarray(e.cue_input(y), dtype=np.float32)), feedback=fn)
    return fn.last_world.detach().numpy()


def _spread(world: np.ndarray) -> float:
    """The standard deviation of the world's final state, which is `e363`'s own `world_sd`."""
    return float(np.std(world))


def _trial_range(world: np.ndarray) -> float:
    """The largest entry of the world's across-trial range: zero exactly when the trial's cue cannot be seen."""
    return float(np.max(np.max(world, axis=0) - np.min(world, axis=0)))


def _cell(model, circ, rs, source: str, cue_at: int, y_tr, y_te) -> dict:
    e = _env(circ, rs, source, cue_at)
    world = _roll(model, e, np.concatenate([y_tr, y_te]))
    return {"accuracy": float(probe(world[:, None, :][:len(y_tr)], y_tr, world[:, None, :][len(y_tr):], y_te,
                                    list(range(WORLD_DIMS)))[-1]),
            "world_sd": _spread(world), "trial_range": _trial_range(world)}


def _reference(path: Path = REFERENCE) -> dict | None:
    import json
    p = Path(path)
    if not p.is_file():
        return None
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    out = {}
    for c in doc.get("cells") or []:
        out[(c.get("source"), c.get("cue_at"))] = {"accuracy": float(c["accuracy"]), "world_sd": float(c["world_sd"])}
    return out or None


def reading(size: int = SIZE, reference: Path = REFERENCE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    net = build_net(circ, RateConfig(tau=TAU))
    rng = np.random.default_rng(SEED + 7)
    y = rng.integers(0, N_SYMBOLS, size=N_EXAMPLES)
    y_tr, y_te = y[:N_EXAMPLES // 2], y[N_EXAMPLES // 2:]

    untrained = _body(net, UNTRAINED, rng)
    cells = {}
    for source in SOURCES:
        for step in STEPS:
            cells[f"{source}@{step}"] = _cell(untrained, circ, rs, source, step, y_tr, y_te)

    #: the invariance `e367` named: the same two late steps, every body
    bodies = {UNTRAINED: {f"action@{step}": {"world_sd": cells[f"action@{step}"]["world_sd"],
                                             "trial_range": cells[f"action@{step}"]["trial_range"],
                                             "accuracy": cells[f"action@{step}"]["accuracy"]} for step in LATE}}
    for name in BODIES[1:]:
        model = _body(net, name, np.random.default_rng(SEED + 1000 + int(name[4:])))
        bodies[name] = {f"action@{step}": _cell(model, circ, rs, "action", step, y_tr, y_te) for step in LATE}

    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED, "tau": TAU,
           "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "n_examples": N_EXAMPLES, "sources": list(SOURCES),
           "steps": list(STEPS), "late": list(LATE), "world_dims": WORLD_DIMS, "world_leak": WORLD_LEAK,
           "cells": cells, "bodies": bodies, "body_names": list(BODIES),
           "reference": {f"{s}@{t}": v for (s, t), v in (_reference(reference) or {}).items()},
           "clears": CLEARS, "clears_bar": 1.0 / N_SYMBOLS + CLEARS}
    out["last_clearing"] = {s: last_clearing(out, s) for s in SOURCES}
    return out


def last_clearing(r: dict, source: str):
    """The largest cue step whose probe still clears chance by `CLEARS`, or None when no step does."""
    cells = r.get("cells") or {}
    good = [step for step in STEPS
            if cells.get(f"{source}@{step}") and cells[f"{source}@{step}"]["accuracy"] >= 1.0 / N_SYMBOLS + CLEARS]
    return max(good) if good else None


def judge(r: dict) -> list[dict]:
    cells = r.get("cells") or {}
    if not cells:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the curve was not rolled"} for c in CLAIMS]

    late = r.get("late") or list(LATE)
    untrained = (r.get("bodies") or {}).get(UNTRAINED) or {}
    spreads = {step: untrained.get(f"action@{step}", {}).get("world_sd") for step in late}
    recorded = {step: (r.get("reference") or {}).get(f"action@{step}", {}).get("world_sd") for step in late}
    if any(v is None for v in recorded.values()):
        j1 = {"id": "W1", "measured": "the frozen grid is not on disk",
              "verdict": "REFUSED -- the artifact the two cells are compared with is absent"}
    else:
        ok = all(spreads[s] is not None and spreads[s] <= EXACT for s in late) and all(recorded[s] == 0.0 for s in late)
        j1 = {"id": "W1", "measured": f"the untrained body's action-source world has spread "
                                      f"{ {s: spreads[s] for s in late} } at the steps {list(late)}, and the corpus "
                                      f"records { {s: recorded[s] for s in late} }",
              "verdict": "MET -- both cells are at rest here and in the corpus's own record" if ok else
              f"FALSIFIER FIRED -- spread { {s: spreads[s] for s in late} } against the recorded "
              f"{ {s: recorded[s] for s in late} }"}

    bodies = r.get("bodies") or {}
    moved = {name: {s: v.get("trial_range") for s, v in per.items()} for name, per in bodies.items()}
    any_moves = sorted(n for n, per in moved.items() if any((x or 0.0) > EXACT for x in per.values()))
    some_spread = sorted(n for n, per in bodies.items() if any((per.get(f"action@{s}", {}).get("world_sd") or 0.0) > EXACT
                                                              for s in late))
    j2 = {"id": "W2", "measured": f"across the {len(bodies)} bodies at the steps {list(late)}, the largest entry of "
                                  f"the world's across-trial range is "
                                  f"{ {n: {s: moved[n][s] for s in moved[n]} for n in (BODIES[0], BODIES[-1])} } "
                                  f"(first and last), with {len(some_spread)} of {len(bodies)} bodies carrying a "
                                  f"nonzero spread and {any_moves} moving with the trial",
          "verdict": "MET -- the world is invariant across the trial for every body, and the invariance is not the "
                     "at-rest case" if not any_moves and some_spread else
          f"FALSIFIER FIRED -- the world moves with the trial in {any_moves}" if any_moves else
          "FALSIFIER FIRED -- every body is at rest, so the invariance is vacuous and this claim says nothing"}

    first = cells.get("action@0") or {}
    above = first.get("accuracy", 0.0) - 1.0 / N_SYMBOLS
    j3 = {"id": "W3", "measured": f"the action source at cue@0 reads {first.get('accuracy'):.4f} against a chance of "
                                  f"{1.0 / N_SYMBOLS:.2f}, {above:+.4f} above it, on a world with spread "
                                  f"{first.get('world_sd'):.4f}",
          "verdict": f"MET -- the channel is real in time, {above:+.4f} over chance at the first step" if above >= CLEARS
          else f"FALSIFIER FIRED -- only {above:+.4f} over chance: the action channel never fills"}

    last = r.get("last_clearing") or {}
    la, lc = last.get("action"), last.get("cue")
    if la is None or lc is None:
        j4 = {"id": "W4", "measured": f"the last clearing step is {la} for the action source and {lc} for the cue source",
              "verdict": "REFUSED -- one of the two sources clears chance at no step, so there is no step to compare"}
    else:
        j4 = {"id": "W4", "measured": f"the last cue step whose probe clears chance by {CLEARS:.2f} is {lc} for the "
                                      f"cue source and {la} for the action source, so the world listening to the "
                                      f"agent's own action needs {lc - la} more step(s) of margin",
              "verdict": f"MET -- the population's price is time, {lc - la} step(s) of it" if la < lc else
              f"FALSIFIER FIRED -- the action source clears at {la} against the cue source's {lc}: the two cost the "
              f"same or the action source is cheaper"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("cells"):
        print("== how long the channel takes to fill ==\n   REFUSED -- the curve was not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== how long the channel takes to fill ==")
    print(f"   {r['circuit']} ({r['size']} neurons), one world of {r['world_dims']} dimensions at leak "
          f"{r['world_leak']}, {r['n_examples']} examples, {r['n_symbols']} symbols, chance {r['chance']:.2f}")
    print(f"\n   {'cue at':>7} {'cue acc':>9} {'cue sd':>9} {'act acc':>9} {'act sd':>9} {'act range':>10}")
    for step in r["steps"]:
        c = r["cells"].get(f"cue@{step}", {})
        a = r["cells"].get(f"action@{step}", {})
        print(f"   {step:>7} {c.get('accuracy', float('nan')):9.4f} {c.get('world_sd', float('nan')):9.4f} "
              f"{a.get('accuracy', float('nan')):9.4f} {a.get('world_sd', float('nan')):9.4f} "
              f"{a.get('trial_range', float('nan')):10.2e}")
    print(f"\n   {'body':>10} " + " ".join(f"{'act@' + str(s):>16}" for s in r["late"]))
    for name in r["body_names"]:
        per = r["bodies"][name]
        print(f"   {name:>10} " + " ".join(
            f"{per.get(f'action@{s}', {}).get('world_sd', float('nan')):>7.4f}/"
            f"{per.get(f'action@{s}', {}).get('trial_range', float('nan')):>7.1e}" for s in r["late"]))
    print(f"   (spread / across-trial range; the last clearing step is {r['last_clearing']})")

    print("\n== the registered claims, W1-W4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e363` read three steps and two sources and `e367` trained the cell they implied is empty; this is")
    print("    the same instrument at all twelve steps, and the invariance the trained run could only report)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--reference", type=Path, default=REFERENCE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(size=args.size, reference=args.reference)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
