"""E348 -- can the world be the read-out? The environment's own state against the cue, on the frozen substrate.

The chain that ends at `e345` is a chain of nils about the **loop**, and every one of them reads the **model's own
state**: `e341` and `e344` read accuracy, `e342` and `e343` read frozen decoders, `e345` read four widths of them.
The conclusion they share is that the channel changes the state and never the answer -- and `e333`, whose subject was
the world's transition rule, closed with the sentence that names the way out: *"And the label is still delivered:
the cue arrives at step 0, so the reward is still not earned."*

**A reward that is earned has to be read from somewhere the model's state is not.** The environment's world is
exactly such a place: it is a leaky integral of the agent's own actions, it is reset with the trial, and until this
unit nothing could see its final value at all. `CueActionEnv.feedback()` now exposes it as `last_world` (and the
action as `last_action`), set on every call, so a read-out that is the **environment** rather than the model is
buildable, and this unit asks the question that has to be answered before one is built: **does the world's final
state carry the cue at all, on the frozen substrate, without any training?**

Nothing trains. The frozen connectome network is rolled on one world's examples at the corpus's closed-loop
settings, and its **final world state** -- a single scalar per trial -- is handed to the corpus's own least-squares
decoder (`e322`'s `probe`) alongside the same decoder on the model's state at the channel's own neurons. Four
claims, registered before any of it was read.

- **T1 -- one configuration across the two leaks.** Same circuit, read-out draw, examples, symbols, scale, gain and
  noise, the two rows differing only in `world_leak`, and the cue is what moves the world: the world's final state
  takes at least two distinct values across the four symbols. **Falsifier**: any other field differing, or a world
  state that is constant across the symbols.
- **T2 -- and the carried world carries the cue.** At `leak = 0.35` the decoder on the world's final state predicts
  the held-out symbol at least **0.10** above chance. **Falsifier**: within **0.05** of chance, which would say the
  frozen substrate's world state is a constant and a world read-out has nothing to read.
- **T3 -- and the leak is what sets how much.** The accuracy from the carried world is at least the accuracy from
  the instantaneous one (`leak = 1.0`, where the recursion is the identity). **Falsifier**: the carried world is
  worse by **0.05** or more, which would say integrating the trial's actions destroys the cue rather than holding
  it. **Null**: between.
- **T4 -- and the model's own channel neurons carry it at least as well.** At `leak = 0.35` the decoder on the
  state at `feedback_neurons` is at least the world's accuracy minus **0.05**. **Falsifier**: the state is worse by
  **0.05** or more, which would say the world carries something the state's own channel neurons do not -- the one
  result that would make a world read-out more than a new place to put the same answer.

**What it cannot do.** *A frozen body and a linear decoder*: this is the substrate's carrier capacity and not a
trained model's, and a non-linear decoder could see more from the same scalar; `e343` and `e345` are the units that
have already said what a decoder on this substrate can and cannot do across widths. *One cue step and one world*:
the cue is a pulse at step 0, with `scale = 1.0`, `gain = 1.0`, two world modes and one leak pair, and nothing here
says what a longer trial, a stronger channel or a state with more than one dimension would carry. *The decoder is
one scalar*: the world's state is one number by construction, so the accuracy above chance is a statement about a
one-dimensional carrier and not about the channel. *And no task is trained*: this says a world read-out has
something to read and not that a body can learn to write it, which is the unit this one licenses and not the unit it
is.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: the corpus's closed-loop settings, and two leaks: the corpus's own 0.35 and the identity endpoint
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
N_TRAIN = 512
N_TEST = 256
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_MODES = 2
LEAKS = (0.35, 1.0)
CARRIED = 0.35
#: T2's margin over chance and its falsifier, T3's and T4's
CARRIES = 0.10
FLAT = 0.05
FALLS = 0.05
CLAIMS = (
    ("T1", "one configuration across the two leaks",
     "Same circuit, read-out draw, examples, symbols, scale, gain and noise, the rows differing only in "
     "`world_leak`, and the world's final state taking at least two distinct values across the symbols",
     "falsifier: any other field differing, or a world state constant across the symbols"),
    ("T2", f"and the carried world carries the cue, by {CARRIES:.2f} over chance",
     f"At `leak = {CARRIED}` the decoder on the world's final state predicts the held-out symbol at least "
     f"{CARRIES:.2f} above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", "and the leak is what sets how much",
     "The accuracy from the carried world is at least the accuracy from the instantaneous one",
     f"falsifier: the carried world is worse by {FALLS:.2f} or more"),
    ("T4", f"and the model's own channel neurons carry it at least as well, within {FLAT:.2f}",
     f"At `leak = {CARRIED}` the decoder on the state at `feedback_neurons` is at least the world's accuracy minus "
     f"{FLAT:.2f}",
     f"falsifier: the state is worse by {FALLS:.2f} or more"),
)


def one_leak(circ, net, rs, leak: float, seed: int = SEED) -> dict:
    """One world's frozen roll: its final state per trial, and the decoders on it and on the model's own channel."""
    import torch
    from clfly.network import env as fly_env

    e = fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                      noise=NOISE, world_modes=WORLD_MODES, world_leak=float(leak))
    rng = np.random.default_rng(seed + 7)
    y_tr = rng.integers(0, N_SYMBOLS, size=N_TRAIN)
    y_te = rng.integers(0, N_SYMBOLS, size=N_TEST)
    u_tr, u_te = e.cue_input(y_tr), e.cue_input(y_te)
    fn = e.feedback()

    def roll(u):
        """The closed roll, and the world's final state read off the closure **before any other pass overwrites it**."""
        with torch.no_grad():
            traj = net(torch.from_numpy(np.asarray(u, dtype=np.float32)), feedback=fn).numpy()
        world = fn.last_world.detach().numpy()
        return traj, world

    def roll_open(u):
        with torch.no_grad():
            return net(torch.from_numpy(np.asarray(u, dtype=np.float32))).numpy()

    closed_tr, w_tr = roll(u_tr)
    closed_te, w_te = roll(u_te)
    open_tr, open_te = roll_open(u_tr), roll_open(u_te)
    peak = float(np.max(np.abs(open_tr))) or 1.0
    #: the world is one scalar per trial, so it enters the corpus's decoder as a one-step, one-neuron trajectory
    out = {
        "leak": float(leak),
        "world_mean": float(np.mean(w_tr)), "world_sd": float(np.std(w_tr)),
        #: how many distinct values the world takes, rounded at the decoder's own resolution: a constant is T1's
        #: falsifier and a continuum is what a carrier looks like
        "world_distinct": int(len(np.unique(np.round(w_tr, 6)))),
        "world_accuracy": probe(w_tr[:, None, None], y_tr, w_te[:, None, None], y_te, [0])[-1],
        "state_accuracy": probe(closed_tr, y_tr, closed_te, y_te, e.feedback_neurons)[-1],
        "chance": 1.0 / N_SYMBOLS,
        "peak": peak,
        #: the divergence on the channel's own neurons, the same quantity `e342` to `e345` read, for context
        "channel_divergence_of_peak": float(max(
            np.max(np.abs(closed_tr[:, -1, :][:, e.feedback_neurons] - open_tr[:, -1, :][:, e.feedback_neurons])),
            np.max(np.abs(closed_te[:, -1, :][:, e.feedback_neurons] - open_te[:, -1, :][:, e.feedback_neurons])))) / peak,
    }
    #: the per-symbol means, which is what "the cord carries the cue" looks like before any decoder
    out["world_by_symbol"] = [float(np.mean(w_tr[y_tr == k])) for k in range(N_SYMBOLS)]
    return out


def reading(leaks=LEAKS, size: int = SIZE, readout_size: int = READOUT_SIZE, seed: int = SEED) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(seed).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    rows = [one_leak(circ, net, rs, leak, seed=seed) for leak in leaks]
    carried = next(r for r in rows if abs(r["leak"] - CARRIED) < 1e-12)
    instant = next((r for r in rows if abs(r["leak"] - 1.0) < 1e-12), None)
    return {
        "circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "readout_sha1": None, "seed": seed,
        "tau": TAU, "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "n_train": N_TRAIN, "n_test": N_TEST,
        "scale": SCALE, "gain": GAIN, "noise": NOISE, "world_modes": WORLD_MODES,
        "leaks": [float(x) for x in leaks], "carried_leak": CARRIED, "rows": rows,
        "carried_accuracy": carried["world_accuracy"],
        "carried_state_accuracy": carried["state_accuracy"],
        "state_minus_world": carried["state_accuracy"] - carried["world_accuracy"],
        "carried_minus_instant": (carried["world_accuracy"] - instant["world_accuracy"]) if instant else None,
    }


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    carried = next((x for x in rows if abs(x["leak"] - CARRIED) < 1e-12), None)
    if carried is None:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the carried world was not measured"}
                for c in CLAIMS]
    chance = r["chance"]

    fields = ("circuit", "size", "readout", "seed", "tau", "n_symbols", "n_train", "n_test", "scale", "gain", "noise",
              "world_modes")
    distinct = min(x["world_distinct"] for x in rows)
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), read-out {r['readout']} neurons, "
                                  f"seed {r['seed']}, {r['n_symbols']} symbols, {r['n_train']} train and "
                                  f"{r['n_test']} test examples, scale {r['scale']}, gain {r['gain']}, noise "
                                  f"{r['noise']}, {r['world_modes']} world modes; the rows differ in `world_leak` "
                                  f"({r['leaks']}) and the world's final state takes {distinct} distinct values "
                                  f"at the least; per-symbol means at the carried leak "
                                  f"{[round(x, 3) for x in carried['world_by_symbol']]}",
          "verdict": "MET -- one configuration across the two leaks" if distinct >= 2 else
          f"FALSIFIER FIRED -- the world's final state is constant across the symbols ({distinct} distinct values)"}

    above = carried["world_accuracy"] - chance
    j2 = {"id": "T2", "measured": f"at leak {carried['leak']} the decoder on the world's final state reads "
                                  f"{carried['world_accuracy']:.4f} against a chance of {chance:.2f}, "
                                  f"{above:+.4f} above it; the world's own values average "
                                  f"{carried['world_mean']:+.4f} on a sd of {carried['world_sd']:.4f}",
          "verdict": f"MET -- the carried world carries the cue, {above:+.4f} above chance" if above >= CARRIES else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance" if above < FLAT else
          f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {CARRIES:.2f}"}

    rise = r.get("carried_minus_instant")
    if rise is None:
        j3 = {"id": "T3", "measured": "the instantaneous world was not measured",
              "verdict": "REFUSED -- the endpoint was not measured"}
    else:
        j3 = {"id": "T3", "measured": f"the carried world reads {carried['world_accuracy']:.4f} and the "
                                      f"instantaneous one reads "
                                      f"{carried['world_accuracy'] - rise:.4f}, a difference of {rise:+.4f}",
              "verdict": f"MET -- the leak is not what sets it, differing by {rise:+.4f}" if rise > -FALLS else
              f"FALSIFIER FIRED -- carrying the trial costs {abs(rise):.4f}"}

    gap = r["state_minus_world"]
    j4 = {"id": "T4", "measured": f"at leak {carried['leak']} the model's state on the channel's own neurons reads "
                                  f"{carried['state_accuracy']:.4f} against the world's "
                                  f"{carried['world_accuracy']:.4f}, a difference of {gap:+.4f}",
          "verdict": f"MET -- the state carries it at least as well, {gap:+.4f}" if gap >= -FLAT else
          f"FALSIFIER FIRED -- the world carries {abs(gap):.4f} that the state's own channel does not"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== can the world be the read-out? ==\n   REFUSED -- the world was not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== can the world be the read-out? ==")
    print(f"   {r['circuit']} ({r['size']} neurons), read-out {r['readout']}, seed {r['seed']}, "
          f"{r['n_symbols']} symbols at a chance of {r['chance']:.2f}, {r['n_train']}/{r['n_test']} examples")
    print(f"\n   {'leak':>6} {'world acc':>10} {'state acc':>10} {'world sd':>9} {'distinct':>9} "
          f"{'channel div':>12}")
    for row in rows:
        print(f"   {row['leak']:6.2f} {row['world_accuracy']:10.4f} {row['state_accuracy']:10.4f} "
              f"{row['world_sd']:9.4f} {row['world_distinct']:9d} {row['channel_divergence_of_peak']:12.2%}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e333` closed with 'the reward is still not earned'; the environment's world is where a read-out")
    print("    that is not the model's state would live, and this asks what it carries before one is built)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leaks", default=",".join(str(x) for x in LEAKS), help="world leaks to measure")
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(leaks=tuple(float(x) for x in args.leaks.split(",")), size=args.size, seed=args.seed)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
