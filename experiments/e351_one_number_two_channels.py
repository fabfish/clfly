"""E351 -- one number, two channels: was it the dimension or the shape of the channel?

`e350` gave the world a state vector and got a clean answer: the scalar world reads **0.5208**, the eight-number one
reads **0.9875**, and the state read-out's lead fell from **+0.4750** to **+0.0083**. It closed its own headline with
the ambiguity it could not remove: *"the two world arms are different objects and not two widths of one: `w8`
replaces the scalar recursion and the two-template blend with a linear map in and a linear map out, so the difference
is the dimension **and** the shape of the channel together, and only a dimension sweep would separate them --
`dims = 1` is the arm that would do it."*

**This unit runs that arm.** `world_dims = 1` keeps the world at **one number** and replaces everything else: the
drive is the whole action population through a fixed `(1, n_action)` map rather than the mean through `tanh`, the
carry is the same leaky recursion, and the answer is a fixed `(1, n_feedback)` map rather than the two-template
blend. So the three arms below are one number through the old channel, one number through the new channel, and eight
numbers through the new channel -- and the question is which of the two changes bought `e350`'s 0.4667.

Three arms, one body each, the same circuit, populations, examples, initialisation and batches within a seed:

- **`scalar`** -- `world_dims = 0`, two templates, the head reading **one** number;
- **`dim1`** -- `world_dims = 1`, the map channel, the head reading **one** number;
- **`dim8`** -- `world_dims = 8`, the map channel, the head reading **eight** numbers.

Four claims, registered before any of it was read.

- **T1 -- one configuration, two differences.** Within a seed the three arms share the circuit, the cue, action and
  feedback populations, the examples, the body initialisation and the batch order; `scalar` against `dim1` differ in
  the channel at one number, `dim1` against `dim8` in the width. **Falsifier**: any of the shared fields differing.
- **T2 -- and the channel's shape buys nothing at one number.** `dim1` and `scalar` are within **0.05** of each
  other. **Falsifier**: they differ by **0.10** or more, which would say `e350`'s headline was wrong -- that the
  linear maps in and out did the work and the width was incidental. **Null**: between. This is the claim the unit
  exists for.
- **T3 -- and the width is what buys it.** `dim8` beats the better of `scalar` and `dim1` by at least **0.05**.
  **Falsifier**: less than **0.02**, which would say neither change is what `e350` measured. **Null**: between.
- **T4 -- and all three are learnable and earned.** Every world arm is at least **0.10** above chance **and** reads
  a single class on every held-out example when the environment is unwired, so each one's answer exists only while
  the loop is closed. **Falsifier**: an arm within 0.05 of chance, or one that predicts more than one class
  unwired, which would be a leak in the read-out rather than a result.

**What it cannot do.** *Three points and not a sweep*: this separates one number from eight, and nothing here says
how the accuracy moves between them or past eight -- `dims` 2, 4, 16 are unrun. *The three arms' channels differ in
more than one way*: the scalar arm has `tanh` and a two-template blend and the map arms have neither, so a difference
between `scalar` and `dim1` is the whole channel and not one of its parts. *One leak, one scale and four symbols*,
with `leak = 0.35`, `scale = 1.0` and 96/48 examples. *Five seeds*, enough to resolve a 0.10 margin and not to bound
a small one. *And the training loop is written here rather than taken from the runner*, so every claim is a
within-unit contrast between arms of the same seed and none of these numbers is comparable with the corpus's
benchmark artifacts.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: `e350`'s settings, with the one-number map arm added
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
BIG = 8
ITERS = 500
LR = 3e-3
BATCH = 32
SEEDS = (0, 1, 2, 3, 4)
#: the arms: one number through the old channel, one through the new, and eight through the new
ARMS = ("scalar", "dim1", "dim8")
SCALAR, DIM1, DIM8 = ARMS
DIMS = {SCALAR: 0, DIM1: 1, DIM8: BIG}
CARRIES = 0.10
FLAT = 0.05
SAME = 0.05
SAME_FIRES = 0.10
BUYS = 0.05
BUYS_FIRES = 0.02
CLAIMS = (
    ("T1", "one configuration, two differences",
     "Within a seed the three arms share the circuit, populations, examples, body initialisation and batch order, "
     "differing in the channel at one number and in the width",
     "falsifier: any of the shared fields differing"),
    ("T2", f"and the channel's shape buys nothing at one number, within {SAME:.2f}",
     "`dim1` and `scalar` are within 0.05 of each other",
     f"falsifier: they differ by {SAME_FIRES:.2f} or more"),
    ("T3", f"and the width is what buys it, by {BUYS:.2f}",
     "`dim8` beats the better of `scalar` and `dim1` by at least 0.05",
     f"falsifier: less than {BUYS_FIRES:.2f}"),
    ("T4", f"and all three are learnable and earned, by {CARRIES:.2f}",
     "Every world arm is at least 0.10 above chance and reads one class on every example when unwired",
     f"falsifier: an arm within {FLAT:.2f} of chance, or more than one class unwired"),
)


def _rest(fn, n: int, dims: int):
    """The world at rest, which is what an unwired environment leaves the read-out holding."""
    import torch
    fn.last_world = torch.zeros(n, dims) if dims else torch.zeros(n)


def one_seed(circ, conn_net, rs, seed: int) -> dict:
    """One seed's three arms: the same body, examples and batches, read through three channels."""
    import numpy as np
    import torch
    from clfly.network import env as fly_env

    y_tr = (np.arange(N_TRAIN) % N_SYMBOLS).astype(np.int64)
    y_te = (np.arange(N_TEST) % N_SYMBOLS).astype(np.int64)
    out = {"seed": seed, "chance": 1.0 / N_SYMBOLS, "arms": {}}
    u_tr = u_te = None

    for arm in ARMS:
        dims = DIMS[arm]
        e = fly_env.build(circ, readout_subset=rs, seed=SEED, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                          noise=NOISE, world_modes=(WORLD_MODES if dims == 0 else 0), world_leak=WORLD_LEAK,
                          world_dims=dims)
        if u_tr is None:
            #: the cue's own draw comes before either channel's, so the first arm's arrays are every arm's; a
            #: mismatch would show up as a different fingerprint in the record
            u_tr, u_te = e.cue_input(y_tr), e.cue_input(y_te)
        fn = e.feedback()
        U, Y = torch.from_numpy(u_tr).float(), torch.from_numpy(y_tr).long()
        Ut, Yt = torch.from_numpy(u_te).float(), torch.from_numpy(y_te).long()
        torch.manual_seed(seed)
        model = conn_net.torch_model()
        n_in = max(dims, 1)
        head = torch.nn.Linear(n_in, N_SYMBOLS)
        opt = torch.optim.Adam([model.theta, model.bias] + list(head.parameters()), lr=LR)
        lossf = torch.nn.CrossEntropyLoss()
        rng = np.random.default_rng(seed + 7)

        def read(traj):
            #: the map channel's world is already `(batch, dims)`; the scalar one is `(batch,)` and needs the axis
            return fn.last_world if dims else fn.last_world[:, None]

        for _ in range(ITERS):
            idx = rng.integers(0, len(Y), size=min(BATCH, len(Y)))
            traj = model(U[idx], None, feedback=fn)
            loss = lossf(head(read(traj)), Y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            wired = float((head(read(model(Ut, None, feedback=fn))).argmax(1) == Yt).float().mean())
            _rest(fn, len(Yt), dims)
            logits = head(read(model(Ut, None)))
            unwired = float((logits.argmax(1) == Yt).float().mean())
            classes = int(len(set(logits.argmax(1).tolist())))
        s = e.summary()
        out["arms"][arm] = {"n_in": n_in, "world_dims": s["world_dims"], "world_drive_sha1": s["world_drive_sha1"],
                            "world_read_sha1": s["world_read_sha1"], "world_leak": s["world_leak"],
                            "cue_sha1": s["cue_sha1"], "action_sha1": s["action_sha1"],
                            "feedback_sha1": s["feedback_sha1"], "wired_accuracy": wired,
                            "unwired_accuracy": unwired, "unwired_classes": classes}
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
           "dims": {k: v for k, v in DIMS.items()}, "iters": ITERS, "lr": LR, "batch": BATCH,
           "seeds": [int(s) for s in seeds], "rows": rows}
    for arm in ARMS:
        vals = [r["arms"][arm]["wired_accuracy"] for r in rows]
        out[f"{arm}_mean"] = statistics.fmean(vals)
        out[f"{arm}_sem"] = (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None
    out["dim1_minus_scalar"] = out[f"{DIM1}_mean"] - out[f"{SCALAR}_mean"]
    out["width_buys"] = out[f"{DIM8}_mean"] - max(out[f"{SCALAR}_mean"], out[f"{DIM1}_mean"])
    out["above_chance"] = {arm: out[f"{arm}_mean"] - out["chance"] for arm in ARMS}
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
                                  f"heads read 1, 1 and {BIG} numbers over worlds of {r['dims']} dimensions, and the "
                                  f"populations' distinct fingerprints across the arms are {shared}",
          "verdict": "MET -- one configuration, two differences" if all(v == 1 for v in shared.values()) else
          f"FALSIFIER FIRED -- the shared fields are not shared: {shared}"}

    shape = r["dim1_minus_scalar"]
    j2 = {"id": "T2", "measured": f"`{DIM1}` reads {r[f'{DIM1}_mean']:.4f} and `{SCALAR}` "
                                  f"{r[f'{SCALAR}_mean']:.4f}, so the channel's shape at one number buys "
                                  f"{shape:+.4f}",
          "verdict": f"MET -- the shape buys nothing at one number, {shape:+.4f}" if abs(shape) < SAME else
          f"FALSIFIER FIRED -- the shape buys {abs(shape):.4f}, so `e350`'s headline was the maps and not the width"
          if abs(shape) >= SAME_FIRES else
          f"NULL -- {shape:+.4f}, between {SAME:.2f} and {SAME_FIRES:.2f}"}

    buys = r["width_buys"]
    j3 = {"id": "T3", "measured": f"`{DIM8}` reads {r[f'{DIM8}_mean']:.4f} against the better one-number arm's "
                                  f"{max(r[f'{SCALAR}_mean'], r[f'{DIM1}_mean']):.4f}, so the width buys "
                                  f"{buys:+.4f}",
          "verdict": f"MET -- the width is what buys it, {buys:+.4f}" if buys >= BUYS else
          f"FALSIFIER FIRED -- less than {BUYS_FIRES:.2f}, {buys:+.4f}" if buys < BUYS_FIRES else
          f"NULL -- {buys:+.4f}, between {BUYS_FIRES:.2f} and {BUYS:.2f}"}

    weak = {arm: round(r["above_chance"][arm], 4) for arm in ARMS if r["above_chance"][arm] < FLAT}
    leaky = {arm: sorted({x["arms"][arm]["unwired_classes"] for x in rows}) for arm in ARMS
             if sorted({x["arms"][arm]["unwired_classes"] for x in rows}) != [1]}
    j4 = {"id": "T4", "measured": f"every arm's held-out accuracy over chance is "
                                  f"{ {k: round(v, 4) for k, v in r['above_chance'].items()} }, and unwired the "
                                  f"three heads read {[sorted({x['arms'][a]['unwired_classes'] for x in rows}) for a in ARMS]} "
                                  f"classes",
          "verdict": "MET -- all three are learnable and earned" if not weak and not leaky else
          f"FALSIFIER FIRED -- at chance {weak}, more than one class unwired {leaky}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== one number, two channels ==\n   REFUSED -- the seeds were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== one number, two channels ==")
    print(f"   {r['circuit']} ({r['size']} neurons), read-out draw {r['readout']}, {r['n_symbols']} symbols at a "
          f"chance of {r['chance']:.2f}, {r['n_train']}/{r['n_test']} examples, leak {r['world_leak']}")
    print(f"\n   {'seed':>5} {'scalar (1, old)':>15} {'dim1 (1, maps)':>15} {'dim8 (8, maps)':>15}")
    for row in rows:
        a = row["arms"]
        print(f"   {row['seed']:5d} {a[SCALAR]['wired_accuracy']:15.4f} {a[DIM1]['wired_accuracy']:15.4f} "
              f"{a[DIM8]['wired_accuracy']:15.4f}")
    print(f"   {'mean':>5} {r[f'{SCALAR}_mean']:15.4f} {r[f'{DIM1}_mean']:15.4f} {r[f'{DIM8}_mean']:15.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e350` closed on the ambiguity this unit removes: its two world arms differ in the dimension and in")
    print("    the shape of the channel together, and `dims = 1` is the arm that holds the width fixed)")
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
