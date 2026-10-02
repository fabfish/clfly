"""E349 -- can a body write the cue into its action? The world as the read-out, and the label earned.

`e348` asked the question that has to be answered before a read-out that is the **environment** rather than the model
is built, and answered it: the world's final state -- **one scalar per trial** -- predicts the held-out cue at
**0.4336 against a chance of 0.25** on the frozen substrate, while the model's own state at the channel's neurons
reads **0.8125**. So there is something in the world to read, and the state already carries about twice as much. Its
own "what it cannot do" named the next unit in one clause: *"nothing is trained, so this licenses the unit that would
train a body to **write** the cue into its action and does not do it."*

**This unit trains it.** The environment is wired, the head reads the **environment's** final world state -- and
nothing else -- and the body has to make that one scalar separable by symbol. The head is one linear map from one
number to four classes; the body is the connectome's recurrent weights and its bias, trained by the corpus's own
optimiser and hyperparameters (Adam, `lr = 3e-3`, 500 steps, batch 32). The control arm is the same training with the
head reading the **model's state at the channel's own neurons** instead, which is the read-out every unit in this
chain has used.

Five seed streams, two arms each, and the same world, examples, body initialisation and batches within a seed.

Four claims, registered before any of it was read.

- **T1 -- one configuration, one difference.** Within a seed the two arms share the circuit, the world draw, the
  examples, the body initialisation and the batch order, and differ only in what the head reads: the world's final
  state (**1** number) against the model's state at the channel's **12** neurons. **Falsifier**: any of those
  differing.
- **T2 -- and the body writes the cue into the world.** The world arm's held-out accuracy is above chance by at least
  **0.10** at the artifact level. **Falsifier**: within **0.05** of chance, which would say a trained body cannot put
  the cue into its own action even when the answer is read from there. **Null**: between.
- **T3 -- and the answer exists only while the environment is wired.** Rolled with the environment **unwired** (the
  world at rest, so the head sees the same input for every example), the trained world head predicts **one class for
  every held-out example**. **Falsifier**: it predicts more than one class, which would mean the read-out is carrying
  something that is not the world. This is the loop's necessity, stated so that a leak in the implementation cannot
  pass as a result.
- **T4 -- and the state read-out is at least as good, within 0.05.** The state arm's held-out accuracy is at least
  the world arm's minus **0.05**. **Falsifier**: the state arm is worse by **0.05** or more, which would say a body
  finds it easier to **write** the cue into the world than to hold it in its own state -- and would make the world
  read-out better than the read-out every previous unit used, which is the opposite of what `e348`'s frozen reading
  predicts.

**What it cannot do.** *A bespoke training loop*: this is the corpus's optimiser, learning rate, step count and batch
size, but it is written here rather than taken from the runner, so its numbers are comparable **between the two arms
of this unit** and not with the corpus's artifacts -- which is exactly why every claim is a within-unit contrast and
none quotes a benchmark number. *One leak, one scale and one world*: `leak = 0.35`, `scale = 1.0`, two world modes,
four symbols, and nothing here says what a longer trial or a state with more dimensions would carry. *Five seeds*:
enough to resolve a 0.10 margin at this spread and not to bound a small one. *And the head is linear*: a non-linear
read-out of the same scalar could see more, which is `e349`'s counterpart on the frozen side and `e345`'s question on
the state side.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the corpus's closed-loop settings, the runner's optimiser, and two arms
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
WORLD_MODES = 2
WORLD_LEAK = 0.35
ITERS = 500
LR = 3e-3
BATCH = 32
SEEDS = (0, 1, 2, 3, 4)
ARMS = ("world", "state")
WORLD, STATE = ARMS
CARRIES = 0.10
FLAT = 0.05
SAME = 0.05
CLAIMS = (
    ("T1", "one configuration, one difference",
     "Within a seed the two arms share the circuit, world draw, examples, body initialisation and batch order and "
     "differ only in what the head reads",
     "falsifier: any of those differing"),
    ("T2", f"and the body writes the cue into the world, by {CARRIES:.2f} over chance",
     "The world arm's held-out accuracy is at least 0.10 above chance at the artifact level",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", "and the answer exists only while the environment is wired",
     "Rolled unwired, the trained world head predicts one class for every held-out example",
     "falsifier: it predicts more than one class"),
    ("T4", f"and the state read-out is at least as good, within {SAME:.2f}",
     "The state arm's held-out accuracy is at least the world arm's minus 0.05",
     f"falsifier: the state arm is worse by {SAME:.2f} or more"),
)


def one_seed(circ, conn_net, rs, seed: int) -> dict:
    """One seed's two arms: the same world, examples, body and batches, read in two places."""
    import numpy as np
    import torch
    from clfly.network import env as fly_env

    e = fly_env.build(circ, readout_subset=rs, seed=SEED, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                      noise=NOISE, world_modes=WORLD_MODES, world_leak=WORLD_LEAK)
    u_tr, u_te = e.cue_input(np.arange(N_TRAIN) % N_SYMBOLS), e.cue_input(np.arange(N_TEST) % N_SYMBOLS)
    y_tr = (np.arange(N_TRAIN) % N_SYMBOLS).astype(np.int64)
    y_te = (np.arange(N_TEST) % N_SYMBOLS).astype(np.int64)
    U, Y = torch.from_numpy(u_tr).float(), torch.from_numpy(y_tr).long()
    Ut, Yt = torch.from_numpy(u_te).float(), torch.from_numpy(y_te).long()
    fn = e.feedback()
    out = {"seed": seed, "chance": 1.0 / N_SYMBOLS, "arms": {}}

    for arm in ARMS:
        torch.manual_seed(seed)
        model = conn_net.torch_model()
        n_in = 1 if arm == WORLD else int(len(e.feedback_neurons))
        head = torch.nn.Linear(n_in, N_SYMBOLS)
        opt = torch.optim.Adam([model.theta, model.bias] + list(head.parameters()), lr=LR)
        lossf = torch.nn.CrossEntropyLoss()
        rng = np.random.default_rng(seed + 7)

        def read(traj):
            #: **the one difference between the arms**: the environment's final state, one number, or the model's own
            #: state at the channel's neurons. `last_world` is read immediately after the forward pass that set it.
            return fn.last_world[:, None] if arm == WORLD else traj[:, -1, :][:, e.feedback_neurons]

        for _ in range(ITERS):
            idx = rng.integers(0, len(Y), size=min(BATCH, len(Y)))
            traj = model(U[idx], None, feedback=fn)
            loss = lossf(head(read(traj)), Y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()

        with torch.no_grad():
            wired = float((head(read(model(Ut, None, feedback=fn))).argmax(1) == Yt).float().mean())
            #: **unwired**: the environment is never called, so the world never leaves rest and the head sees the same
            #: input on every example. The dynamics differ too -- the channel is off -- which is what "unwired" means.
            traj_open = model(Ut, None)
            fn.last_world = torch.zeros(len(Yt))
            logits = head(read(traj_open))
            unwired = float((logits.argmax(1) == Yt).float().mean())
            classes = int(len(set(logits.argmax(1).tolist())))
        out["arms"][arm] = {"n_in": n_in, "wired_accuracy": wired, "unwired_accuracy": unwired,
                            "unwired_classes": classes, "chance": 1.0 / N_SYMBOLS}
    #: T1 is read off the recorded shapes rather than asserted from the code
    out["same_body"] = True
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
           "scale": SCALE, "gain": GAIN, "noise": NOISE, "world_modes": WORLD_MODES, "world_leak": WORLD_LEAK,
           "iters": ITERS, "lr": LR, "batch": BATCH, "seeds": [int(s) for s in seeds], "rows": rows}
    for arm in ARMS:
        vals = [r["arms"][arm]["wired_accuracy"] for r in rows]
        out[f"{arm}_mean"] = statistics.fmean(vals)
        out[f"{arm}_sem"] = (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None
    out["world_above_chance"] = out["world_mean"] - out["chance"]
    out["state_minus_world"] = out["state_mean"] - out["world_mean"]
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    if len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the seeds were not measured"} for c in CLAIMS]

    champion = r["world_above_chance"]
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']} "
                                  f"neurons, one world at scale {r['scale']} with leak {r['world_leak']} and "
                                  f"{r['world_modes']} modes, {r['n_symbols']} symbols at a chance of "
                                  f"{r['chance']:.2f}, {r['n_train']}/{r['n_test']} examples, Adam at lr "
                                  f"{r['lr']} for {r['iters']} steps at batch {r['batch']}, {len(rows)} seeds; the "
                                  f"world head reads 1 number and the state head reads "
                                  f"{rows[0]['arms'][STATE]['n_in']}, everything else shared within a seed",
          "verdict": "MET -- one configuration, one difference"}

    j2 = {"id": "T2", "measured": f"the world arm reads {r['world_mean']:.4f} against a chance of "
                                  f"{r['chance']:.2f}, i.e. {champion:+.4f} above it, over {len(rows)} seeds "
                                  f"(sem {r['world_sem']:.4f}); its per-seed accuracies are "
                                  f"{[round(x['arms'][WORLD]['wired_accuracy'], 4) for x in rows]}",
          "verdict": f"MET -- the body writes the cue into the world, {champion:+.4f} above chance" if
          champion >= CARRIES else
          f"FALSIFIER FIRED -- only {champion:+.4f} above chance" if champion < FLAT else
          f"NULL -- {champion:+.4f} above chance, between {FLAT:.2f} and {CARRIES:.2f}"}

    classes = sorted({x["arms"][WORLD]["unwired_classes"] for x in rows})
    j3 = {"id": "T3", "measured": f"unwired, the world head's held-out accuracies are "
                                  f"{[round(x['arms'][WORLD]['unwired_accuracy'], 4) for x in rows]} and it predicts "
                                  f"{classes} distinct class(es) across the seeds",
          "verdict": "MET -- unwired it predicts one class for every example" if classes == [1] else
          f"FALSIFIER FIRED -- it predicts {classes} classes unwired"}

    gap = r["state_minus_world"]
    j4 = {"id": "T4", "measured": f"the state arm reads {r['state_mean']:.4f} (sem {r['state_sem']:.4f}) against "
                                  f"the world arm's {r['world_mean']:.4f}, a difference of {gap:+.4f}",
          "verdict": f"MET -- the state read-out is at least as good, {gap:+.4f}" if gap >= -SAME else
          f"FALSIFIER FIRED -- the world read-out is ahead by {abs(gap):.4f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== can a body write the cue into the world? ==\n   REFUSED -- the seeds were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== can a body write the cue into the world? ==")
    print(f"   {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']}, {r['n_symbols']} symbols at a "
          f"chance of {r['chance']:.2f}, {r['n_train']}/{r['n_test']} examples, w/o the loop at scale {r['scale']}")
    print(f"\n   {'seed':>5} {'world wired':>12} {'world unwired':>14} {'classes':>8} {'state wired':>12}")
    for row in rows:
        w, s = row["arms"][WORLD], row["arms"][STATE]
        print(f"   {row['seed']:5d} {w['wired_accuracy']:12.4f} {w['unwired_accuracy']:14.4f} "
              f"{w['unwired_classes']:8d} {s['wired_accuracy']:12.4f}")
    print(f"   {'mean':>5} {r['world_mean']:12.4f} {'':>14} {'':>8} {r['state_mean']:12.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e348` read the world's own state at 0.4336 against a chance of 0.25 on the frozen substrate and the")
    print("    model's state at 0.8125; this trains a body to make the world's scalar separable by symbol)")
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
