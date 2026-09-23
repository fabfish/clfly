"""E124 -- the barrier between two seeds' solutions, over ALL pairs of a dozen seeds rather than one pair.

`e122` measured the loss along the chord between two seeds' solutions and found a barrier of 30x that is still
**3.9% of the chance level** `ln 4 = 1.386`: there is an interior maximum, so the chord is not monotone, and it
is nowhere near a wall, so the two seeds' solutions sit in one connected set. That settled the multi-basin
question **for one pair** -- seed 100 was not even chosen for the question, it was the second replicate already
on disk -- and "one seed pair, one read-out, one task order" is the first weakness its own finding lists.

This script generalises the measurement the cheap way. A chord costs forward passes; it was `e122`'s *training*
that was expensive. So: train twelve seeds once, save every checkpoint, and evaluate **all 66 unordered pairs**.
1,386 chord evaluations at the first checkpoint and 4,158 at the last, against twelve training runs.

    python -m experiments.e124_barrier_distribution --seeds 12 --json-out runs/e124_barrier_12seeds.json

The chord instrument is **imported from `e122`**, not reimplemented -- `checkpoint`, `chord_profile`,
`endpoint_control` -- so there is exactly one definition of the chord in this project and this script cannot
drift from the fire it is generalising.

**C0 is an equality against `runs/e122_path_geometry.json`**: pair (0, 1) of this run's seed set *is* seeds 0 and
100, at the same configuration, so the two chords must come out **bit-identical** -- not close, identical, because
the training is seeded and the interpolation is exact at the endpoints. If they do not, this script is not
running the chord and no distribution below is comparable to it.

Registered in `docs/findings/2026-09-24-the-barrier-over-all-pairs-preregistered.md`, committed before the run:
P1 is that **every** pair is below 25% of the chance level on a fit task, and the falsifier is **any** pair above
50%. The thresholds are registered as a band with a gap so that a value landing between them is a stated
"neither" rather than a rounding argument.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e122_path_geometry import checkpoint, chord_profile, endpoint_control, setup
from experiments.e8_rate_network import run_method

CHANCE = math.log(4.0)
FIT_WALL = 0.25          # P1's threshold: the barrier as a fraction of chance
FALSIFIER_WALL = 0.50    # the falsifier's threshold


def train(args):
    """Train every seed once, saving the checkpoints, and return the suite and the per-seed records."""
    net, suite = setup(args)
    states: dict[int, dict[int, dict]] = {}
    scalars: dict[int, dict] = {}
    for k in range(args.seeds):
        seed = args.seed0 + args.seed_step * k
        args.save_theta = args.theta_dir
        result = run_method(net, suite, "naive", args, seed=seed, partitions=None)
        scalars[seed] = result
        with np.load(args.theta_dir / f"naive_seed{seed}.npz") as npz:
            n_heads = 1 if args.shared_head else len(suite)
            states[seed] = {j: checkpoint(npz, f"after_task_{j}", n_heads) for j in range(len(suite))}
        print(f"  seed {seed:4d}: forgetting {result['mean_forgetting']:+.4f}, "
              f"accuracy {result['final_accuracy']:.4f}, fit loss {result['full_train_loss'][-1]:.5f}")
    return net, suite, states, scalars


def fresh(net, suite, shared: bool):
    """A module and its decoders. Every chord gets its own, so nothing carries over between pairs."""
    import torch

    if shared:
        return net.torch_model(), [torch.nn.Linear(suite[0].n_readout, sum(t.n_classes for t in suite))]
    return net.torch_model(), [torch.nn.Linear(t.n_readout, t.n_classes) for t in suite]


def all_pairs(net, suite, states, seeds: list[int], points: int, shared: bool, checkpoints: list[int]) -> dict:
    """Every unordered pair at every checkpoint, evaluated on every task that checkpoint has seen."""
    out = {}
    for i, j in itertools.combinations(range(len(seeds)), 2):
        si, sj = seeds[i], seeds[j]
        for k in checkpoints:
            model, heads = fresh(net, suite, shared)
            out[(si, sj, k)] = chord_profile(model, suite, heads, states[si][k], states[sj][k], points,
                                             shared, split="train", upto=k + 1)
    return out


def flatten(profiles: dict) -> tuple[list[dict], list[dict]]:
    """One row per (pair, checkpoint, task), split into the FIT task and the RETAINED tasks.

    The split is the whole point of separating them: on the fit task (`j == k`) both ends are configurations
    that have *just* solved it, so its barrier is about geometry alone. On a retained task the two ends differ
    because the two seeds kept different amounts, so its "barrier" is mostly that difference.
    """
    fit, retained = [], []
    for (si, sj, k), prof in profiles.items():
        for j, entry in sorted(prof["tasks"].items(), key=lambda kv: int(kv[0])):
            j = int(j)
            ends = entry["endpoint_losses"]
            lo, hi = min(ends), max(ends)
            row = {"seed_a": si, "seed_b": sj, "checkpoint": k, "task": j,
                   "barrier": entry["barrier"]["barrier"], "peak": entry["barrier"]["peak"],
                   "barrier_over_chance": entry["barrier"]["barrier"] / CHANCE,
                   "endpoint_losses": ends,
                   "endpoint_ratio": (hi / lo) if lo > 0 else float("nan")}
            (fit if j == k else retained).append(row)
    return fit, retained


def distribution(rows: list[dict], key: str = "barrier_over_chance") -> dict:
    """The full sorted list plus the few summaries the claim needs -- and the claim is about the MAXIMUM."""
    xs = np.array([r[key] for r in rows], dtype=float)
    if not len(xs):
        return {}
    worst = float(xs.max())
    return {"n": int(len(xs)), "min": float(xs.min()), "median": float(np.median(xs)),
            "mean": float(xs.mean()), "max": worst,
            "max_at": {k: rows[int(xs.argmax())][k] for k in ("seed_a", "seed_b", "checkpoint", "task")},
            "within_factor_2_of_max": int((xs >= worst / 2).sum()),
            "sorted": [float(x) for x in np.sort(xs)]}


def correlate(rows: list[dict], x_of, y_of=lambda r: r["barrier_over_chance"]) -> dict:
    """Pearson r over rows, with its n stated rather than its p.

    Rows are not independent -- 66 pairs from 12 seeds, and each pair contributes one row per retained task --
    so the n is the row count and the honest effective n for anything about *seeds* is 12. Stated in the return
    value rather than in a footnote, because `e121`'s r = -0.35 lead came apart for exactly this reason.
    """
    xs = np.array([x_of(r) for r in rows], dtype=float)
    ys = np.array([y_of(r) for r in rows], dtype=float)
    keep = np.isfinite(xs) & np.isfinite(ys)
    xs, ys = xs[keep], ys[keep]
    if len(xs) < 3 or xs.std() == 0 or ys.std() == 0:
        return {"n_rows": int(len(xs)), "r": float("nan")}
    return {"n_rows": int(len(xs)), "r": float(np.corrcoef(xs, ys)[0, 1])}


def p3_registered(fit_rows: list[dict], scalars: dict) -> dict:
    """The quantity `docs/findings/2026-09-24-the-barrier-over-all-pairs-preregistered.md` actually registered.

    P3 as written is *"whether the fit-task barrier of a pair correlates with that pair's own forgetting
    difference (`|mean_forgetting_i - mean_forgetting_j|`)"* — **one point per pair**, 66 of them. The script's
    first version correlated the retained-task **endpoint loss ratio** instead, which is a different quantity on a
    different unit (132 rows, one per pair per retained task). That is a deviation from a registration, so both
    are computed and reported: the registered one is the claim, and the other is kept only because it was in the
    first artifact and deleting it would hide the substitution rather than correct it.
    """
    per_pair: dict[tuple, list[float]] = {}
    for r in fit_rows:
        per_pair.setdefault((r["seed_a"], r["seed_b"]), []).append(r["barrier_over_chance"])
    if not per_pair:
        return {"n_pairs": 0, "r": float("nan")}
    gaps, worst = [], []
    for (a, b), xs in per_pair.items():
        gaps.append(abs(scalars[a]["mean_forgetting"] - scalars[b]["mean_forgetting"]))
        worst.append(max(xs))
    gaps, worst = np.array(gaps, dtype=float), np.array(worst, dtype=float)
    if len(gaps) < 3 or gaps.std() == 0 or worst.std() == 0:
        return {"n_pairs": int(len(gaps)), "r": float("nan")}
    return {"n_pairs": int(len(gaps)), "r": float(np.corrcoef(gaps, worst)[0, 1]),
            "note": "one point per pair, as registered; the pair's worst fit-task barrier"}


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
    p.add_argument("--seed-step", type=int, default=100)
    p.add_argument("--seeds", type=int, default=12)
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
    p.add_argument("--frozen-body", action="store_true")
    p.add_argument("--normalise-fisher", action="store_true", default=True)
    p.add_argument("--points", type=int, default=21)
    p.add_argument("--theta-dir", type=Path, default=Path("runs/e124_theta"))
    p.add_argument("--checkpoints", default="first,last", choices=("first,last", "all"),
                   help="'first,last' (2 chords per pair) or 'all' (one per checkpoint, ~3x the work)")
    p.add_argument("--matching-seeds", type=Path, default=Path("runs/e116_r128_40reps.json"),
                   help="C0b: the extension control -- a stored run whose first `--seeds` replicates this "
                        "run's twelve must reproduce. Every run here uses seed0 + 100r, so a twelve-seed run "
                        "IS the first twelve of a forty-replicate one at the same configuration")
    p.add_argument("--matching-pair", type=Path, default=Path("runs/e122_path_geometry.json"),
                   help="C0: the artifact whose seeds 0/100 chord this run's pair (0,1) must reproduce")
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--reanalyse", type=Path, default=None,
                   help="recompute the distributions and both P3 values from a stored artifact, with no "
                        "training -- the statistics are a function of the stored rows and scalars, so a "
                        "statistic that was computed wrongly can be corrected without paying for the run again")
    args = p.parse_args(argv)

    if args.reanalyse:
        art = json.loads(args.reanalyse.read_text(encoding="utf-8"))
        scalars = {int(k): v for k, v in art["scalars"].items()}
        fit_rows, retained_rows = art["fit_tasks"], art["retained_tasks"]
        p3 = p3_registered(fit_rows, scalars)
        p3_alt = correlate(retained_rows, lambda r: r["endpoint_ratio"] - 1.0)
        art["distributions"] = {"fit": distribution(fit_rows), "retained": distribution(retained_rows)}
        art["P3"], art["P3_as_first_computed"] = p3, p3_alt
        fit = art["distributions"]["fit"]
        print(f"reanalysed {args.reanalyse}: fit-task barrier/chance n = {fit['n']}, "
              f"min {fit['min']:.4f}, median {fit['median']:.4f}, MAX {fit['max']:.4f}")
        print(f"  P1 (every pair below {FIT_WALL}) : {'HOLDS' if fit['max'] < FIT_WALL else 'FAILS'}")
        print(f"  falsifier (any pair above {FALSIFIER_WALL}): "
              f"{'FIRED' if fit['max'] > FALSIFIER_WALL else 'does not fire'}")
        print(f"  P3 REGISTERED: {p3['n_pairs']} pairs, r = {p3['r']:+.3f}")
        print(f"  P3 as first computed: {p3_alt['n_rows']} rows, r = {p3_alt['r']:+.3f}")
        write_json(args.reanalyse, art)
        print(f"rewrote {args.reanalyse}")
        return 0

    net, suite, states, scalars = train(args)
    seeds = [args.seed0 + args.seed_step * k for k in range(args.seeds)]
    n_tasks = len(suite)
    checkpoints = list(range(n_tasks)) if args.checkpoints == "all" else sorted({0, n_tasks - 1})
    shared = bool(args.shared_head)

    print(f"\n  {args.seeds} seeds, {len(seeds) * (len(seeds) - 1) // 2} pairs, "
          f"checkpoints {checkpoints}, {args.points} points per chord")
    profiles = all_pairs(net, suite, states, seeds, args.points, shared, checkpoints)
    fit_rows, retained_rows = flatten(profiles)

    fit = distribution(fit_rows)
    print(f"\n  barrier on the FIT task, as a fraction of chance (ln 4 = {CHANCE:.3f}):")
    print(f"    n = {fit['n']}   min {fit['min']:.4f}   median {fit['median']:.4f}   "
          f"mean {fit['mean']:.4f}   MAX {fit['max']:.4f}")
    print(f"    worst pair: {fit['max_at']}")
    print(f"    within a factor of 2 of the worst: {fit['within_factor_2_of_max']} of {fit['n']}")
    print(f"  P1 (every pair below {FIT_WALL}) : {'HOLDS' if fit['max'] < FIT_WALL else 'FAILS'}")
    print(f"  falsifier (any pair above {FALSIFIER_WALL}): "
          f"{'FIRED' if fit['max'] > FALSIFIER_WALL else 'does not fire'}")
    for k in checkpoints:
        d = distribution([r for r in fit_rows if r["checkpoint"] == k])
        if d:
            print(f"    checkpoint {k}: n {d['n']}, min {d['min']:.4f}, median {d['median']:.4f}, "
                  f"max {d['max']:.4f}")

    ret = distribution(retained_rows)
    if ret:
        print(f"\n  barrier on the RETAINED tasks (ends differ because retention differs):")
        print(f"    n = {ret['n']}   min {ret['min']:.4f}   median {ret['median']:.4f}   MAX {ret['max']:.4f}")
        print(f"    worst pair: {ret['max_at']}")

    # C0b -- the extension control, and it is the one that generalises across read-outs. Every run of this
    # benchmark uses `seed0 + 100r`, so a twelve-seed run's seeds ARE the first twelve of any forty-replicate
    # run at the same configuration. At read-out 128 those twelve came out **bit-identical** to
    # `runs/e116_r128_40reps.json`'s first twelve; this makes the same check automatic at any read-out, so a
    # second read-out cannot quietly be a different benchmark.
    ext = {"attempted": False}
    if args.matching_seeds and args.matching_seeds.is_file():
        ref = json.loads(args.matching_seeds.read_text(encoding="utf-8"))
        ref_reps = ref["methods"]["naive"]["replicates"][:len(seeds)]
        ref_forg = [r["mean_forgetting"] for r in ref_reps]
        mine = [scalars[s]["mean_forgetting"] for s in seeds]
        ext = {"attempted": True, "artifact": str(args.matching_seeds),
               "n_compared": len(mine), "n_available": len(ref["methods"]["naive"]["replicates"]),
               "identical": mine == ref_forg,
               "max_abs_difference": max(abs(a - b) for a, b in zip(mine, ref_forg)),
               "mean_new": float(np.mean(mine)), "mean_reference": float(np.mean(ref_forg))}
        print(f"  extension control: {ext['n_compared']} of the reference's {ext['n_available']} replicates, "
              f"max |difference| {ext['max_abs_difference']:.3e} -> "
              f"{'BIT-IDENTICAL' if ext['identical'] else '** DIFFERS **'}")

    # C0 -- the chord through seeds 0 and 100, which is pair (0, 1) here, against what e122 recorded.
    c0 = {"attempted": False}
    if args.matching_pair and args.matching_pair.is_file():
        old = json.loads(args.matching_pair.read_text(encoding="utf-8"))
        c0 = {"attempted": True, "artifact": str(args.matching_pair), "rows": []}
        for label, k, task in (("after_task_0", 0, 0), ("final", n_tasks - 1, n_tasks - 1)):
            new = profiles.get((seeds[0], seeds[1], k))
            ref = old["profiles"].get(f"{label} / whole solution")
            if new is None or ref is None:
                continue
            n_e, r_e = new["tasks"][str(task)], ref["tasks"][str(task)]
            c0["rows"].append({
                "chord": label, "task": task,
                "peak_new": n_e["barrier"]["peak"], "peak_recorded": r_e["barrier"]["peak"],
                "barrier_new": n_e["barrier"]["barrier"], "barrier_recorded": r_e["barrier"]["barrier"],
                "endpoints_new": n_e["endpoint_losses"], "endpoints_recorded": r_e["endpoint_losses"],
                "bit_identical": n_e["losses"] == r_e["losses"],
            })
        c0["all_identical"] = bool(c0["rows"]) and all(r["bit_identical"] for r in c0["rows"])
        for r in c0["rows"]:
            print(f"  C0 {r['chord']:13} task {r['task']}: peak {r['peak_new']:.5f} vs recorded "
                  f"{r['peak_recorded']:.5f}, barrier {r['barrier_new']:+.5f} vs "
                  f"{r['barrier_recorded']:+.5f} -> {'BIT-IDENTICAL' if r['bit_identical'] else '** DIFFERS **'}")

    # e122's endpoint control, re-run here: every saved checkpoint must reproduce the runner's own loss.
    controls = {}
    for k in range(n_tasks):
        model, heads = fresh(net, suite, shared)
        prof = chord_profile(model, suite, heads, states[seeds[0]][k], states[seeds[1]][k], 2, shared,
                             split="train", upto=k + 1)
        controls[f"after_task_{k}"] = endpoint_control(
            prof, {"a": scalars[seeds[0]], "b": scalars[seeds[1]]}, checkpoint=k, upto=k + 1)
        rows = controls[f"after_task_{k}"]["rows"]
        n_ok = sum(r["a_agrees"] and r["b_agrees"] for r in rows)
        print(f"  endpoint control after_task_{k}: {n_ok}/{len(rows)} agree -> "
              f"{'AGREE' if controls[f'after_task_{k}']['all_agree'] else '** DISAGREES **'}")

    p3 = p3_registered(fit_rows, scalars)
    print(f"\n  P3 REGISTERED: across the {p3['n_pairs']} pairs, the fit-task barrier vs the pair's own "
          f"|forgetting difference| gives r = {p3['r']:+.3f}")
    p3_alt = correlate(retained_rows, lambda r: r["endpoint_ratio"] - 1.0)
    print(f"  P3 as this script first computed it -- retained-task endpoint loss ratio, NOT the registered "
          f"quantity: r = {p3_alt['r']:+.3f} at n_rows = {p3_alt['n_rows']}")

    if args.json_out:
        write_json(args.json_out, {
            "config": vars(args), "n_params": net.n_params, "seeds": seeds,
            "scalars": {str(s): {"mean_forgetting": scalars[s]["mean_forgetting"],
                                 "final_accuracy": scalars[s]["final_accuracy"],
                                 "retention_loss": scalars[s]["retention_loss"]}
                        for s in seeds},
            "fit_tasks": fit_rows, "retained_tasks": retained_rows,
            "distributions": {"fit": fit, "retained": ret},
            "C0": c0, "C0b_extension_control": ext,
            "endpoint_controls": {k: {"all_agree": v["all_agree"]} for k, v in controls.items()},
            "P3": p3, "P3_as_first_computed": p3_alt,
        })
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
