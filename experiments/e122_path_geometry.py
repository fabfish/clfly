"""E122 -- the loss along the chord between two seeds' solutions, which is a question about geometry.

Every seed of this benchmark starts from the **same** connectome-initialised body, so a pair of endpoints is a
chord through the loss landscape and the loss along it answers a question no trajectory quantity can: **are the
solutions the seeds find connected?** If the loss stays low along the whole chord the two are in one connected
region ("linear mode connectivity"); a barrier between them means they are not, and then *which interpolant a
run lands in* is really *which region*, decided by the seed.

That distinction is what the last six fires have been circling. The benchmark **interpolates its training data at
every read-out** (`e121`, a factor of 300-10,000 better than chance), the seed-to-seed spread survives a tenfold
test set (`e119`) and four times the training (`e120`), and five candidate quantities failed to order the
forgetting -- the drift, the load-bearing gap, the first-order interference term, the second-order quadratic form
and the fit depth. **All five are properties of a walk or of an endpoint; none of them can say which of many
interpolating solutions a seed lands in**, and this script asks whether "many" means *many regions* or *one
connected set*.

    python -m experiments.e122_path_geometry --readout-size 128 --json-out runs/e122_path_geometry.json

Three deliberate construction choices, each of which the first version of this script got wrong and each of
which is a check rather than a comment:

**1. The chord is the whole solution, not the recurrent weights.** The forward pass reads `theta` *and*
`model.bias`, and `train_task` optimises both; the first version interpolated only `theta` and evaluated on top
of a **zero bias**, a configuration the benchmark never produces. It reported endpoint losses of ~0.105 where the
benchmark's own full-train-set loss on the same body is **0.0017** -- a factor of sixty, on the endpoint, which
is the loudest possible place for a bug to be. So `--save-theta` now writes the bias per task as well, and the
chord interpolates `theta`, the bias and the shared decoder together. Both ends are then configurations the
benchmark actually produces.

**2. The endpoint control is built in and is the strongest check available.** At ``t = 0`` the interpolated state
*is* seed A's checkpoint, so the loss there must equal seed A's own recorded `full_train_loss` for that task --
and likewise for seed B at ``t = 1``. This is not a tolerance: it is the same number the runner wrote down while
training, recomputed from the saved body. A mismatch means the instrument is not reconstructing the benchmark,
and it is what would have caught (1) in one line. **The interpolation is in `float64` and only the assignment
back to the model is `float32`, so at the endpoints the arithmetic is exact and the check is exact.**

**3. The reproduction check runs first.** This script rebuilds the benchmark's setup rather than importing it (so
that nothing about the runner changes), and it therefore trains seed A and compares the result to the stored
forty-replicate artifact's replicate 0. If that disagrees, the duplicated setup is wrong and the geometry below
is meaningless -- the cheapest possible way to find out.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from clfly.connectome import annotate, circuits, graph
from clfly.network import tasks as rate_tasks
from clfly.network.model import RateConfig, build_net
from experiments.e8_rate_network import run_method

HEAD_PARTS = ("weight", "bias")


def checkpoint(npz, key: str, n_heads: int) -> dict:
    """One saved state: the recurrent weights, the recurrent bias, and every decoder.

    ``key`` is ``after_task_{k}`` and the bias lives under ``bias_after_task_{k}``. Reading *both* here rather
    than at the call site is the point -- a checkpoint that silently omits a parameter the forward pass reads is
    the failure this function exists to make impossible.
    """
    return {
        "theta": npz[key],
        "bias": npz["bias_" + key],
        "heads": [{p: npz[f"head_{i}_{p}_{key}"] for p in HEAD_PARTS} for i in range(n_heads)],
    }


def lerp(x, y, t: float) -> np.ndarray:
    """``(1 - t)*x + t*y`` in ``float64``, so the interpolation itself adds no float32 rounding.

    Exact at both ends: ``t = 0`` and ``t = 1`` return the inputs' values bit-for-bit, which is what makes the
    endpoint control an equality check rather than a tolerance.
    """
    return (1.0 - t) * np.asarray(x, dtype=np.float64) + t * np.asarray(y, dtype=np.float64)


def apply_state(model, heads, a: dict, b: dict, t: float, decoder_from: str | None = None) -> None:
    """Put the state at chord position ``t`` into the live module.

    Every array the forward pass reads is written, which is the point of doing this in one function. With
    ``decoder_from = None`` the decoders are interpolated along with the body (the whole-solution chord); with
    ``"a"`` or ``"b"`` one seed's decoders are held fixed while the body moves (the asymmetry check).
    """
    import torch

    def put_(param, x):
        param.data.copy_(torch.from_numpy(np.ascontiguousarray(x, dtype=np.float32)))

    with torch.no_grad():
        put_(model.theta, lerp(a["theta"], b["theta"], t))
        put_(model.bias, lerp(a["bias"], b["bias"], t))
        fixed = None if decoder_from is None else (a if decoder_from == "a" else b)["heads"]
        for i, h in enumerate(heads):
            for p in HEAD_PARTS:
                put_(getattr(h, p),
                     lerp(a["heads"][i][p], b["heads"][i][p], t) if fixed is None else fixed[i][p])


def barrier(losses: list[float], reference: int | None = None) -> dict:
    """The height the loss must climb to get from the reference end of the chord to the other.

    ``max(losses) - losses[reference]``: how much worse the *worst* interior point is than the endpoint we are
    measuring *from*. Zero or less means the chord is monotone or valley-shaped with no interior maximum; a
    large positive value means there is a wall between them. Reported beside both endpoint values, because a
    barrier is only meaningful relative to the scale of the loss it sits on.

    ``reference`` defaults to the **worse** endpoint, which is the standard mode-connectivity form and the
    stronger of the two available readings: a peak above the worse end is above *both* ends, so the chord
    certainly is not monotone and neither end is a minimum along it. (Measured against the better end instead the
    barrier is larger, and for the chords in `e122` the two differ by at most a factor of 1.8.) It is set
    explicitly for the body-only chords, where one end is a mismatched body-and-decoder pair that is not a
    solution we may measure a barrier from.
    """
    ends = max(losses[0], losses[-1]) if reference is None else losses[reference]
    peak = max(losses)
    return {"barrier": float(peak - ends), "peak": float(peak), "reference": float(ends),
            "reference_index": (int(np.argmax([losses[0], losses[-1]])) if reference is None else reference),
            "relative_to_reference": float((peak - ends) / ends) if ends else float("nan")}


def setup(args):
    """The benchmark, built exactly as `e8_rate_network.main` builds it -- duplicated deliberately, and checked."""
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    rs = None
    if args.readout_size and args.readout_size < circ.n_neurons:
        draw_seed = args.seed0 if args.readout_seed is None else args.readout_seed
        rs = np.sort(np.random.default_rng(draw_seed).choice(
            circ.n_neurons, size=args.readout_size, replace=False))
    common = dict(n_train=args.train, n_test=args.test, noise=args.noise, n_classes=args.classes)
    if args.input_overlap is None:
        suite = rate_tasks.make_suite(circ, shared_head=args.shared_head, readout_subset=rs, **common)
    else:
        suite = rate_tasks.make_overlap_suite(
            circ, n_tasks=len(rate_tasks.SUITE_SPECS), support=args.support,
            overlap=args.input_overlap, shared_head=args.shared_head, readout_subset=rs, **common)
    net = build_net(circ, RateConfig(seed=args.seed0))
    return net, suite


def full_loss(model, readout, task, shared: bool = False, split: str = "train") -> float:
    """Mean cross-entropy over a whole split, so the path is measured on all of the data rather than a batch."""
    import torch

    U = torch.from_numpy(getattr(task, f"u_{split}")).float()
    Y = torch.from_numpy(getattr(task, f"y_{split}")).long()
    with torch.no_grad():
        traj = model(U, None)
        logits = _logits_of(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
        return float(torch.nn.functional.cross_entropy(logits, Y).item())


def _logits_of(readout, x, task, shared: bool):
    out = readout(x)
    return out[:, task.class_offset:task.class_offset + task.n_classes] if shared else out


def chord_profile(model, suite, heads, a: dict, b: dict, points: int, shared: bool,
                  split: str = "train", upto: int | None = None,
                  decoder_from: str | None = None) -> dict:
    """The loss on each task along the chord, at ``points`` equally spaced ``t`` including both ends.

    ``decoder_from = None`` interpolates the whole solution. ``"a"`` or ``"b"`` holds that seed's decoders fixed
    while the body moves -- the asymmetry check, whose far end is a mismatched body-and-decoder pair and is
    therefore an upper bound rather than a solution.
    """
    tasks = range(len(suite) if upto is None else upto)
    ts = np.linspace(0.0, 1.0, points)
    out = {"t": [float(t) for t in ts], "tasks": {}}
    for j in tasks:
        readout = heads[0] if shared else heads[j]
        losses = []
        for t in ts:
            apply_state(model, heads, a, b, float(t), decoder_from=decoder_from)
            losses.append(full_loss(model, readout, suite[j], shared, split))
        # A barrier is measured *from* an end. With the whole solution interpolated both ends are solutions and
        # the worse one is the reference (see `barrier`); with a decoder held fixed the far end is a mismatched
        # pair, so the reference has to be the genuine end explicitly.
        ref = {"a": 0, "b": len(losses) - 1}.get(decoder_from)
        out["tasks"][str(j)] = {
            "losses": losses,
            "barrier": barrier(losses, ref),
            "endpoint_losses": [losses[0], losses[-1]],
        }
    return out


def endpoint_control(profile: dict, scalars: dict, checkpoint: int, upto: int | None = None) -> dict:
    """Does the chord's ``t = 0`` reproduce seed A's own recorded loss on every task, and ``t = 1`` seed B's?

    The runner records the **loss retention matrix** `retention_loss[k][j]` -- the full train-set loss on task
    ``j`` at checkpoint ``k`` -- so the chord through checkpoint ``k`` has a recorded counterpart on *every*
    task it can measure, not only the last. Both numbers come from the same body and the same split, so this is
    an equality check, not a tolerance. It is also the only check in this script that would notice a parameter
    missing from the checkpoint, which is precisely the bug it caught: without the recurrent bias the endpoints
    read ~0.105 against a recorded 0.0017, a factor of sixty, on the endpoint.

    The earlier version compared `full_train_loss[j]`, which is recorded at checkpoint ``j`` -- a different body
    for every ``j`` below the last -- so it demanded agreement between two configurations and reported a failure
    where there was none. A control has to compare like with like, and the *thing to compare with* had to be
    recorded before it could be compared.
    """
    rows = []
    for j, entry in sorted(profile["tasks"].items(), key=lambda kv: int(kv[0])):
        if upto is not None and int(j) >= upto:
            continue
        rows.append({
            "task": int(j),
            "recorded_a": scalars["a"]["retention_loss"][checkpoint][int(j)],
            "chord_t0": entry["endpoint_losses"][0],
            "recorded_b": scalars["b"]["retention_loss"][checkpoint][int(j)],
            "chord_t1": entry["endpoint_losses"][-1],
        })
    for r in rows:
        r["a_agrees"] = abs(r["recorded_a"] - r["chord_t0"]) < 1e-6
        r["b_agrees"] = abs(r["recorded_b"] - r["chord_t1"]) < 1e-6
    return {"rows": rows, "all_agree": bool(rows) and all(r["a_agrees"] and r["b_agrees"] for r in rows)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--iters", type=int, default=500)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lam", type=float, default=3e-3)
    p.add_argument("--train", type=int, default=96)
    p.add_argument("--test", type=int, default=48)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--noise", type=float, default=1.0)
    p.add_argument("--classes", type=int, default=4)
    p.add_argument("--support", type=int, default=80)
    p.add_argument("--shared-head", action="store_true", default=True)
    p.add_argument("--input-overlap", type=float, default=0.0)
    p.add_argument("--readout-size", type=int, default=128)
    p.add_argument("--readout-seed", type=int, default=None)
    p.add_argument("--replay-per-task", type=int, default=16)
    p.add_argument("--replay-batch", type=int, default=16)
    p.add_argument("--basis", default="cell_class")
    p.add_argument("--fisher-batches", type=int, default=8)
    p.add_argument("--pool-below", type=int, default=0)
    p.add_argument("--pool-buckets", type=int, default=1)
    # `run_method` reads these, and the benchmark they describe is the one this script reproduces.
    p.add_argument("--frozen-body", action="store_true")
    p.add_argument("--normalise-fisher", action="store_true", default=True)
    p.add_argument("--points", type=int, default=21)
    p.add_argument("--seed-b", type=int, default=100)
    p.add_argument("--theta-dir", type=Path, default=Path("runs/e122_theta"))
    p.add_argument("--reproduce", type=Path, default=None,
                   help="an artifact whose replicate 0 must match this run's, as the check that the duplicated "
                        "setup is the benchmark's (default: the e116 forty-replicate run at this read-out)")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    net, suite = setup(args)
    shared = bool(args.shared_head)
    n_heads = 1 if shared else len(suite)
    profiles = {}
    seeds = {"a": args.seed0, "b": args.seed_b}
    states = {}
    scalars = {}
    for name, seed in seeds.items():
        args.save_theta = args.theta_dir
        result = run_method(net, suite, "naive", args, seed=seed, partitions=None)
        scalars[name] = result
        with np.load(args.theta_dir / f"naive_seed{seed}.npz") as npz:
            states[name] = {k: checkpoint(npz, f"after_task_{k}", n_heads) for k in range(len(suite))}
        print(f"  seed {name} = {seed}: forgetting {result['mean_forgetting']:+.4f}, "
              f"accuracy {result['final_accuracy']:.4f}, "
              f"final train loss {result['full_train_loss'][-1]:.5f}")

    # The check the docstring promises: this script's setup is a copy, so it has to *reproduce* the benchmark.
    check = {"attempted": False}
    ref = args.reproduce
    if ref is None and args.readout_size == 128:
        ref = Path("runs/e116_r128_40reps.json")
    if ref and Path(ref).exists():
        import json
        stored = json.loads(Path(ref).read_text(encoding="utf-8"))["methods"]["naive"]["replicates"][0]
        check = {"attempted": True, "artifact": str(ref),
                 "stored_forgetting": stored["mean_forgetting"],
                 "this_run_forgetting": scalars["a"]["mean_forgetting"],
                 "stored_accuracy": stored["final_accuracy"],
                 "this_run_accuracy": scalars["a"]["final_accuracy"]}
        check["reproduces"] = (abs(check["stored_forgetting"] - check["this_run_forgetting"]) < 1e-9
                               and abs(check["stored_accuracy"] - check["this_run_accuracy"]) < 1e-9)
        print(f"  setup check against {ref}: forgetting {check['stored_forgetting']:+.4f} vs "
              f"{check['this_run_forgetting']:+.4f}, accuracy {check['stored_accuracy']:.4f} vs "
              f"{check['this_run_accuracy']:.4f} -> {'REPRODUCES' if check['reproduces'] else 'DOES NOT REPRODUCE'}")

    # The chords. `t = 0` is seed A's checkpoint and `t = 1` seed B's, so the two ends of the whole-solution
    # chord are both configurations the benchmark produces and the endpoint control below is an equality.
    import torch

    def fresh_heads():
        if shared:
            return [torch.nn.Linear(suite[0].n_readout, sum(t.n_classes for t in suite))]
        return [torch.nn.Linear(t.n_readout, t.n_classes) for t in suite]

    # Every checkpoint is validated before any of them is measured, and the validation is two points long
    # because an endpoint check needs only the endpoints. This is what makes a wrong instrument loud: a dropped
    # parameter shows up here as a mismatch on the endpoint, where the number is 60x off rather than 6%.
    controls = {}
    for k in range(len(suite)):
        prof = chord_profile(net.torch_model(), suite, fresh_heads(), states["a"][k], states["b"][k], 2, shared,
                             split="train", upto=k + 1)
        controls[f"after_task_{k}"] = endpoint_control(prof, scalars, checkpoint=k, upto=k + 1)
        n_ok = sum(r["a_agrees"] and r["b_agrees"] for r in controls[f"after_task_{k}"]["rows"])
        n_tot = len(controls[f"after_task_{k}"]["rows"])
        print(f"  endpoint control, checkpoint after_task_{k}: {n_ok}/{n_tot} task-endpoints agree with the "
              f"runner's own recorded retention loss -> "
              f"{'AGREE' if controls[f'after_task_{k}']['all_agree'] else '** DISAGREES **'}")

    for label, key, upto in [("final", len(suite) - 1, None), ("after_task_0", 0, 1)]:
        for decoder_from in (None, "a"):
            tag = "whole solution" if decoder_from is None else "body only (decoder a)"
            model = net.torch_model()
            heads = fresh_heads()
            a, b = states["a"][key], states["b"][key]
            prof = chord_profile(model, suite, heads, a, b, args.points, shared,
                                 split="train", upto=upto, decoder_from=decoder_from)
            profiles[f"{label} / {tag}"] = prof
            for j, entry in sorted(prof["tasks"].items(), key=lambda kv: int(kv[0])):
                bb = entry["barrier"]
                print(f"  {label:12} {tag:24} task {j}: ends {entry['endpoint_losses'][0]:.5f} / "
                      f"{entry['endpoint_losses'][-1]:.5f}  barrier {bb['barrier']:+.5f} "
                      f"(peak {bb['peak']:.5f}, ref {bb['reference']:.5f})")

    if args.json_out:
        write_json(args.json_out, {"config": vars(args), "check": check, "controls": controls,
                                   "scalars": scalars, "profiles": profiles})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
