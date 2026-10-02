"""E350 -- the world gets a dimension: is the earned label's price the carrier's width?

`e349` trained a body to write the cue into its own action and measured what it costs: reading the answer out of the
**environment's** final state, **one scalar per trial**, the world arm reads **0.5208** against a chance of 0.25 while
the same training with the head on the model's own state reads **0.9958** -- a gap of **0.4750**. And unwired the
world arm reads exactly chance, because the world at rest is a constant, which is the whole point of an earned label.

**Two readings of that gap were left open, and they are different units.** One is that a body cannot *write* a rich
answer into an integrator of its own actions; the other is that the integrator is **scalar**, so there is nowhere to
write it. `e333` named the second as its own gap in one sentence: *"The world's rule is linear and scalar: one leaky
integrator of one action, with no state-to-state coupling and nothing the agent's actions can push it into."*

**This unit gives the world a dimension and asks which reading it is.** `CueActionEnv` gained `world_dims`: above
zero the world's state is a **vector** of that many numbers, driven by the whole action **population** through a
fixed map and answering through a second one, both drawn from the environment's seed and fingerprinted in its draw.
Zero leaves every earlier artifact bit-identical, so the scalar world `e349` ran is still exactly there.

Three arms, one body each, the same circuit, populations, examples, initialisation and batches within a seed:

- **`w1`** -- the scalar world of `e349` (`world_dims = 0`, two templates), the head reading **one** number;
- **`w8`** -- the vector world (`world_dims = 8` for eight action neurons), the head reading **eight** numbers;
- **`state`** -- the head reading the model's state at the channel's twelve neurons, the read-out every unit before
  `e348` used. It is the ceiling this unit is measuring against and not the object of interest.

Four claims, registered before any of it was read.

- **T1 -- one configuration, two differences.** Within a seed the three arms share the circuit, the cue, action and
  feedback populations, the examples, the body initialisation and the batch order; `w1` against `w8` differ in the
  world's dimension and its channel, and `w8` against `state` differ in what the head reads. **Falsifier**: any of
  the shared fields differing.
- **T2 -- and the vector world is learnable.** `w8`'s held-out accuracy is at least **0.10** above chance at the
  artifact level. **Falsifier**: within **0.05** of chance, which would say a body cannot write into a world with
  eight numbers either. **Null**: between.
- **T3 -- and the dimension is what the gap was.** `w8` beats `w1` by at least **0.05**. **Falsifier**: within
  **0.02**, which would say the scalar world already carried everything the body had to say and the gap is about
  writing rather than about width. **Null**: between.
- **T4 -- and it closes the state's gap.** The state arm's lead over `w8` is at most **0.05**. **Falsifier**: still
  behind by **0.10** or more, which would say eight numbers do not close it either. **Null**: between.

**What it cannot do.** *The two arms' worlds are different objects and not two widths of one*: `w8` replaces the
scalar recursion and the two-template blend with a linear map in and a linear map out, so a difference between the
arms is the dimension **and** the shape of the channel together, and only a dimension sweep would separate those.
*Eight is the action population's size*, not a ladder: nothing here says what four or sixteen would do. *One leak,
one scale and four symbols*, with `leak = 0.35`, `scale = 1.0` and 96/48 examples. *Five seeds*, enough to resolve a
0.10 margin and not to bound a small one. *And the training loop is written here rather than taken from the runner*,
so every claim is a within-unit contrast and none of these numbers is comparable with the corpus's benchmark
artifacts.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: `e349`'s settings, plus the vector world's dimension: eight action neurons, so eight is the full-rank choice
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
N_TRAIN = 96
N_TEST = 48
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_MODES = 2
WORLD_DIMS = 8
ITERS = 500
LR = 3e-3
BATCH = 32
SEEDS = (0, 1, 2, 3, 4)
#: the arms: what the head reads, and the world it reads from
ARMS = ("w1", "w8", "state")
W1, W8, STATE = ARMS
CARRIES = 0.10
FLAT = 0.05
BUYS = 0.05
NOTHING = 0.02
CLOSES = 0.05
BEHIND = 0.10
CLAIMS = (
    ("T1", "one configuration, two differences",
     "Within a seed the three arms share the circuit, populations, examples, body initialisation and batch order; "
     "`w1` against `w8` differ in the world's dimension and channel, `w8` against `state` in what the head reads",
     "falsifier: any of the shared fields differing"),
    ("T2", f"and the vector world is learnable, by {CARRIES:.2f} over chance",
     "`w8`'s held-out accuracy is at least 0.10 above chance at the artifact level",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the dimension is what the gap was, by {BUYS:.2f}",
     "`w8` beats `w1` by at least 0.05",
     f"falsifier: within {NOTHING:.2f}"),
    ("T4", f"and it closes the state's gap, leaving at most {CLOSES:.2f}",
     "The state arm's lead over `w8` is at most 0.05",
     f"falsifier: still behind by {BEHIND:.2f} or more"),
)


def one_seed(circ, conn_net, rs, seed: int) -> dict:
    """One seed's three arms: the same body, examples and batches, read in three places."""
    import numpy as np
    import torch
    from clfly.network import env as fly_env

    u_tr = None
    u_te = None
    y_tr = (np.arange(N_TRAIN) % N_SYMBOLS).astype(np.int64)
    y_te = (np.arange(N_TEST) % N_SYMBOLS).astype(np.int64)
    out = {"seed": seed, "chance": 1.0 / N_SYMBOLS, "arms": {}}

    for arm in ARMS:
        dims = 0 if arm == W1 else (WORLD_DIMS if arm == W8 else 0)
        modes = WORLD_MODES if arm == W1 else 0
        e = fly_env.build(circ, readout_subset=rs, seed=SEED, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                          noise=NOISE, world_modes=modes, world_leak=WORLD_LEAK, world_dims=dims)
        if u_tr is None:
            #: the cue depends only on the populations and the templates, which no arm changes; the first arm's
            #: arrays are the ones every arm is given, and a mismatch would show up as a different record
            u_tr, u_te = e.cue_input(y_tr), e.cue_input(y_te)
        fn = e.feedback()
        U, Y = torch.from_numpy(u_tr).float(), torch.from_numpy(y_tr).long()
        Ut, Yt = torch.from_numpy(u_te).float(), torch.from_numpy(y_te).long()
        torch.manual_seed(seed)
        model = conn_net.torch_model()
        n_in = 1 if arm == W1 else (WORLD_DIMS if arm == W8 else int(len(e.feedback_neurons)))
        head = torch.nn.Linear(n_in, N_SYMBOLS)
        opt = torch.optim.Adam([model.theta, model.bias] + list(head.parameters()), lr=LR)
        lossf = torch.nn.CrossEntropyLoss()
        rng = np.random.default_rng(seed + 7)

        def read(traj):
            if arm in (W1, W8):
                return fn.last_world if arm == W8 else fn.last_world[:, None]
            return traj[:, -1, :][:, e.feedback_neurons]

        for _ in range(ITERS):
            idx = rng.integers(0, len(Y), size=min(BATCH, len(Y)))
            traj = model(U[idx], None, feedback=fn)
            loss = lossf(head(read(traj)), Y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            wired = float((head(read(model(Ut, None, feedback=fn))).argmax(1) == Yt).float().mean())
            #: **unwired**: the environment is never called, so the world never leaves rest and its read-out is a
            #: constant. The eight-dimensional arm's rest state is a zero vector, so its head also sees one input.
            traj_open = model(Ut, None)
            if arm == W8:
                fn.last_world = torch.zeros(len(Yt), WORLD_DIMS)
            elif arm == W1:
                fn.last_world = torch.zeros(len(Yt))
            logits = head(read(traj_open))
            unwired = float((logits.argmax(1) == Yt).float().mean())
            classes = int(len(set(logits.argmax(1).tolist())))
        summary = e.summary()
        out["arms"][arm] = {"n_in": n_in, "world_dims": summary["world_dims"],
                            "world_drive_sha1": summary["world_drive_sha1"],
                            "world_read_sha1": summary["world_read_sha1"],
                            "world_leak": summary["world_leak"], "cue_sha1": summary["cue_sha1"],
                            "action_sha1": summary["action_sha1"], "feedback_sha1": summary["feedback_sha1"],
                            "wired_accuracy": wired, "unwired_accuracy": unwired, "unwired_classes": classes}
    #: T1's shared fields, read off the arms' own draws rather than asserted from the code
    out["shared"] = {k: len({a[k] for a in out["arms"].values() if a[k] is not None})
                     for k in ("cue_sha1", "action_sha1", "feedback_sha1", "world_leak")}
    return out


def reading(seeds=SEEDS, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    import numpy as np
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    conn_net = build_net(circ, RateConfig(tau=TAU))
    rows = [one_seed(circ, conn_net, rs, int(s)) for s in seeds]
    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED, "tau": TAU,
           "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "n_train": N_TRAIN, "n_test": N_TEST,
           "scale": SCALE, "gain": GAIN, "noise": NOISE, "world_leak": WORLD_LEAK, "world_modes": WORLD_MODES,
           "world_dims": WORLD_DIMS, "iters": ITERS, "lr": LR, "batch": BATCH, "seeds": [int(s) for s in seeds],
           "rows": rows}
    for arm in ARMS:
        vals = [r["arms"][arm]["wired_accuracy"] for r in rows]
        out[f"{arm}_mean"] = statistics.fmean(vals)
        out[f"{arm}_sem"] = (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None
    out["w8_above_chance"] = out[f"{W8}_mean"] - out["chance"]
    out["w8_minus_w1"] = out[f"{W8}_mean"] - out[f"{W1}_mean"]
    out["state_minus_w8"] = out[f"{STATE}_mean"] - out[f"{W8}_mean"]
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    if len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the seeds were not measured"} for c in CLAIMS]

    shared = rows[0]["shared"]
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']} "
                                  f"neurons, {r['n_symbols']} symbols at a chance of {r['chance']:.2f}, "
                                  f"{r['n_train']}/{r['n_test']} examples, leak {r['world_leak']}, Adam at lr "
                                  f"{r['lr']} for {r['iters']} steps at batch {r['batch']}, {len(rows)} seeds; the "
                                  f"heads read 1, {r['world_dims']} and {rows[0]['arms'][STATE]['n_in']} numbers and "
                                  f"the populations' distinct fingerprints across the arms are {shared}",
          "verdict": "MET -- one configuration, two differences" if all(v == 1 for v in shared.values()) else
          f"FALSIFIER FIRED -- the shared fields are not shared: {shared}"}

    above = r["w8_above_chance"]
    j2 = {"id": "T2", "measured": f"the `{W8}` arm reads {r[f'{W8}_mean']:.4f} against a chance of {r['chance']:.2f}, "
                                  f"i.e. {above:+.4f} above it, over {len(rows)} seeds (sem {r[f'{W8}_sem']:.4f})",
          "verdict": f"MET -- the vector world is learnable, {above:+.4f} above chance" if above >= CARRIES else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance" if above < FLAT else
          f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {CARRIES:.2f}"}

    buys = r["w8_minus_w1"]
    j3 = {"id": "T3", "measured": f"the `{W8}` arm reads {r[f'{W8}_mean']:.4f} and the `{W1}` arm "
                                  f"{r[f'{W1}_mean']:.4f}, so the dimension buys {buys:+.4f}",
          "verdict": f"MET -- the dimension is what the gap was, {buys:+.4f}" if buys >= BUYS else
          f"FALSIFIER FIRED -- within {NOTHING:.2f} of it, {buys:+.4f}" if buys < NOTHING else
          f"NULL -- {buys:+.4f}, between {NOTHING:.2f} and {BUYS:.2f}"}

    lead = r["state_minus_w8"]
    j4 = {"id": "T4", "measured": f"the `{STATE}` arm reads {r[f'{STATE}_mean']:.4f} and the `{W8}` arm "
                                  f"{r[f'{W8}_mean']:.4f}, so the state's lead is {lead:+.4f} against the "
                                  f"{r[f'{STATE}_mean'] - r[f'{W1}_mean']:+.4f} it had over `{W1}`",
          "verdict": f"MET -- the gap is closed to {lead:+.4f}" if lead <= CLOSES else
          f"FALSIFIER FIRED -- still behind by {lead:.4f}" if lead >= BEHIND else
          f"NULL -- {lead:+.4f}, between {CLOSES:.2f} and {BEHIND:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== the world gets a dimension ==\n   REFUSED -- the seeds were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world gets a dimension ==")
    print(f"   {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']}, {r['n_symbols']} symbols at a "
          f"chance of {r['chance']:.2f}, {r['n_train']}/{r['n_test']} examples, leak {r['world_leak']}")
    print(f"\n   {'seed':>5} {'w1 (1 number)':>14} {'w8 (8 numbers)':>15} {'state (12)':>12} {'w8 unwired':>11}")
    for row in rows:
        a = row["arms"]
        print(f"   {row['seed']:5d} {a[W1]['wired_accuracy']:14.4f} {a[W8]['wired_accuracy']:15.4f} "
              f"{a[STATE]['wired_accuracy']:12.4f} {a[W8]['unwired_accuracy']:11.4f}")
    print(f"   {'mean':>5} {r[f'{W1}_mean']:14.4f} {r[f'{W8}_mean']:15.4f} {r[f'{STATE}_mean']:12.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e349` measured the earned label's price at 0.4750 with a scalar world; `e333` named the scalar")
    print("    rule as its own gap, and this asks whether the width of the carrier is what that price was)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", default=",".join(str(x) for x in SEEDS), help="seed streams to train")
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(seeds=tuple(int(x) for x in args.seeds.split(",")), size=args.size)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
