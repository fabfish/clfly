"""E123 -- does reporting retention in LOSS beat the accuracy metric's thirty-fold handicap?

`e118` measured the reported metric at 74-134% relative precision against `theta_drift`'s 2.6-3.5% and named
the estimator: the forgetting is a difference of accuracies over a held-out set with granularity 1/240, while
the drift is a norm over 26,568 numbers. `e119` then removed 94% of the *removable* evaluation noise with a
tenfold test set and showed the rest is the training trajectory's -- so the handicap narrowed from thirtyfold to
eighteenfold and **the remainder is no longer noise to be removed but a floor under the estimator**.

`e122` then produced `retention_loss[k][j]`, the full-train-set loss on task `j` at checkpoint `k` -- the
retention matrix in loss, a continuous quantity with no granularity floor -- as a by-product of validating its
chords. This script measures what that buys. It is registered in
`docs/findings/2026-09-24-the-loss-metric-preregistered.md`, which was committed before the runs.

    python -m experiments.e123_loss_metric --run runs/e123_r128_test480.json \
        --reference runs/e119_r128_test480.json

Both metrics come from the **same replicates of the same run**, so the comparison is paired and no draw, seed or
environment term can enter it. C0 is exact and comes first: adding `retention_loss` records more and trains
nothing, so the per-repeat accuracy forgetting must be **bit-identical** to the reference artifact's. If it is
not, the instrumentation perturbed the run and every number below is a cross-run comparison.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def loss_forgetting(retention_loss: list[list[float]]) -> float:
    """``mean_{j < T-1} ( L[T-1][j] - min_{k >= j} L[k][j] )``, in nats.

    The accuracy forgetting is ``max_k R[k][j] - R[T-1][j]``; this is the same expression with the two
    directions swapped, because loss falls where accuracy rises. ``min`` includes ``k = T-1``, so the value is
    non-negative by construction, exactly as the accuracy form is.
    """
    L = np.asarray(retention_loss, dtype=float)
    T = L.shape[0]
    per_task = []
    for j in range(max(T - 1, 0)):
        column = L[j:, j]                        # checkpoints j..T-1, all finite (lower triangle)
        per_task.append(float(L[T - 1, j] - np.nanmin(column)))
    return float(np.mean(per_task)) if per_task else 0.0


def loss_forgetting_log_ratio(retention_loss: list[list[float]]) -> float:
    """The scale-free companion, ``mean_j log(L[T-1][j] / min_k L[k][j])`` in nats.

    Registered as the companion and not as the metric: its denominator is the just-fitted loss (~0.0018), where
    the fit is tightest and a relative error there is inflated.
    """
    L = np.asarray(retention_loss, dtype=float)
    T = L.shape[0]
    out = []
    for j in range(max(T - 1, 0)):
        column = L[j:, j]
        best = float(np.nanmin(column))
        if best > 0 and L[T - 1, j] > 0:
            out.append(math.log(float(L[T - 1, j]) / best))
    return float(np.mean(out)) if out else float("nan")


def accuracy_forgetting(replicate: dict) -> float:
    """The reported metric, recomputed from the retention matrix **with the runner's own window**.

    `experiments/e8_rate_network.py:517` computes `nanmax(R[:j+1, j]) - R[T-1, j]` — the max over checkpoints
    **0..j**, i.e. up to and including the one that learned task `j`. The first version of this script used
    `R[j:, j]` instead, the window **j..T-1**, which is a different statistic: it can see a *later* checkpoint
    that happens to do better on task `j`. It differs from the stored metric by up to **0.0073 per replicate**
    and 0.00057 on the mean, and a comparison meant to be paired has to compute both sides the same way, so this
    is a real defect rather than a rounding.

    **It does not affect the conclusion, and the reason is worth stating**: the loss-valued form is *identical*
    under both windows, because the minimum of a task's loss always lands on `k = j` — right after the task was
    trained — and is high at every earlier checkpoint, where the task had not been trained at all. So the window
    choice moves the accuracy side by 55.1% against 53.5% and the loss side by nothing, and the relative-sd ratio
    is **0.91 under both**.
    """
    R = np.asarray(replicate["retention"], dtype=float)
    T = R.shape[0]
    per_task = [float(np.nanmax(R[: j + 1, j]) - R[T - 1, j]) for j in range(max(T - 1, 0))]
    return float(np.mean(per_task)) if per_task else 0.0


def sd(xs) -> float:
    xs = np.asarray([x for x in xs if x is not None], dtype=float)
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else float("nan")


def extension_control(run: dict, reference: dict) -> dict:
    """C0: the same configuration's accuracy forgetting, per replicate, must be bit-identical.

    `retention_loss` evaluates under `torch.no_grad()`, steps no optimiser and draws no random number, so the
    training RNG streams are untouched and the forty replicates must land where they landed before.
    """
    a = [r["mean_forgetting"] for r in run["methods"]["naive"]["replicates"]]
    b = [r["mean_forgetting"] for r in reference["methods"]["naive"]["replicates"]]
    if len(a) != len(b):
        return {"same_length": False, "identical": False, "n_run": len(a), "n_reference": len(b)}
    diffs = [abs(x - y) for x, y in zip(a, b)]
    per_task_a = [r["forgetting_per_task"] for r in run["methods"]["naive"]["replicates"]]
    per_task_b = [r["forgetting_per_task"] for r in reference["methods"]["naive"]["replicates"]]
    return {"same_length": True,
            "identical": max(diffs) == 0.0,
            "max_abs_difference": max(diffs),
            "per_task_identical": per_task_a == per_task_b,
            "n_reference": len(b)}


def analyse(run_path: Path, reference_path: Path | None) -> dict:
    run = json.loads(run_path.read_text(encoding="utf-8"))
    reps = run["methods"]["naive"]["replicates"]
    missing = [i for i, r in enumerate(reps) if "retention_loss" not in r]
    if missing:
        raise SystemExit(f"{run_path}: {len(missing)} replicates carry no retention_loss "
                         f"(first at index {missing[0]}) -- written by a code epoch before e122")

    acc = np.array([accuracy_forgetting(r) for r in reps])
    los = np.array([loss_forgetting(r["retention_loss"]) for r in reps])
    log = np.array([loss_forgetting_log_ratio(r["retention_loss"]) for r in reps])

    sd_acc, sd_los, sd_log = sd(acc), sd(los), sd(log)
    ratio = sd_los / sd_acc
    # The relative form, which is what `e118`'s "74-134%" means: the sd as a fraction of the value it sits on.
    # **It is only meaningful on a linear scale.** For the log-ratio the same expression is an artifact of where
    # the log's zero happens to be -- adding 10 to every value would divide its "relative sd" by five while
    # changing nothing about the estimator -- so the log-scale precision is reported multiplicatively, as the
    # factor `exp(sd)` by which two seeds' forgetting ratios typically differ. Comparing 0.47 nats to 0.022
    # accuracy units is a ratio of two different things, and this script prints the units beside every number
    # for that reason.
    rel_acc = sd_acc / abs(np.mean(acc))
    rel_los = sd_los / abs(np.mean(los))
    mult_log = float(math.exp(sd_log))
    ratio_relative = rel_los / rel_acc

    out = {
        "run": str(run_path),
        "readout_size": run["config"]["readout_size"],
        "n": len(reps),
        "accuracy": {"mean": float(np.mean(acc)), "sd": sd_acc, "sem": sd_acc / math.sqrt(len(acc)),
                     "relative_sd": float(rel_acc)},
        "loss_nats": {"mean": float(np.mean(los)), "sd": sd_los, "sem": sd_los / math.sqrt(len(los)),
                      "relative_sd": float(rel_los)},
        "loss_log_ratio": {"mean": float(np.mean(log)), "sd": sd_log, "sd_multiplicative": mult_log},
        "ratio_loss_over_accuracy": float(ratio),
        "ratio_of_relative_sds_below_1": bool(ratio_relative < 1.0),
        "ratio_of_relative_sds": float(ratio_relative),
        "P1_sd_loss_below_sd_accuracy": bool(ratio < 1.0),
        "P2_ratio_below_0.71": bool(ratio < 0.71),
        "falsifier_fired": bool(ratio >= 1.0),
    }
    if reference_path and reference_path.exists():
        out["C0"] = extension_control(run, json.loads(reference_path.read_text(encoding="utf-8")))
    return out


def report(res: dict) -> None:
    a, l, g = res["accuracy"], res["loss_nats"], res["loss_log_ratio"]
    print(f"== {res['run']}  (read-out {res['readout_size']}, n = {res['n']}) ==")
    if "C0" in res:
        c = res["C0"]
        if c["same_length"]:
            print(f"  C0  per-repeat accuracy forgetting vs the reference's {c['n_reference']}: "
                  f"max |difference| = {c['max_abs_difference']:.3e} -> "
                  f"{'BIT-IDENTICAL' if c['identical'] else '** DIFFERS **'}"
                  f" (per-task rows identical: {c['per_task_identical']})")
        else:
            print(f"  C0  ** replicate counts differ: {c['n_run']} vs {c['n_reference']} **")
    print(f"  accuracy forgetting  mean {a['mean']:.5f}  sd {a['sd']:.5f}  sd/mean {100 * a['relative_sd']:.1f}%")
    print(f"  loss forgetting      mean {l['mean']:.5f}  sd {l['sd']:.5f}  sd/mean {100 * l['relative_sd']:.1f}%  (nats)")
    print(f"  log-ratio companion  mean {g['mean']:.4f}  sd {g['sd']:.4f}  (sd/mean is meaningless on a log scale; "
          f"the multiplicative form is {g['sd_multiplicative']:.2f}x)  (nats)")
    print(f"  sd_loss / sd_accuracy = {res['ratio_loss_over_accuracy']:.3f}   <-- CROSS-UNIT: nats against "
          f"accuracy, so this is a ratio of two different quantities")
    print(f"  relative-sd ratio (loss/accuracy) = {res['ratio_of_relative_sds']:.3f}   <-- the like-for-like "
          f"form, and the one the registration's P3 says the claim is about")
    print(f"  P1 as registered (sd_loss < sd_acc)      : {'HOLDS' if res['P1_sd_loss_below_sd_accuracy'] else 'FAILS'}")
    print(f"  P2 as registered (ratio < 0.71)          : {'HOLDS' if res['P2_ratio_below_0.71'] else 'FAILS'}")
    print(f"  falsifier as registered (ratio >= 1)     : {'FIRED' if res['falsifier_fired'] else 'does not fire'}")
    print(f"  P1 on the LIKE-FOR-LIKE reading (rel_sd_loss < rel_sd_acc): "
          f"{'HOLDS' if res['ratio_of_relative_sds_below_1'] else 'FAILS'}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", type=Path, action="append", required=True,
                   help="an e123 artifact; repeat for several read-outs")
    p.add_argument("--reference", type=Path, default=None,
                   help="the C0 comparator, e.g. runs/e119_r128_test480.json at read-out 128")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    results = [analyse(r, args.reference) for r in args.run]
    for r in results:
        report(r)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, {"results": results})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
