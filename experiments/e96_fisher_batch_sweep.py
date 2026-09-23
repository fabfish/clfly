"""E96 -- the Fisher-batch sweep `e8c` reported, whose artifact no longer exists on disk.

`docs/findings/2026-09-22-fisher-batches-negative.md` reports a **single-seed sweep** of the Fisher batch
count (8, 32, 128) at λ = 0.1, and names `runs/e8_fisher_batches.json` as its artifact. That path no longer
holds the sweep: it now holds a **three-repeat, 32-batch** run written later, whose `config` says
`fisher_batches: 32` and `repeats: 3` against the finding's "single seed, sweeping". A scan of every
`fisher_batches` value anywhere under `runs/` returns only **8 and 32** — **no 128-batch run exists on
disk at all.**

So the paper's §4.7 quotes a sweep — "the diagonal's forgetting from +0.063 to **+0.250**" as batches go
8 → 128, and a monotone "+0.010 → +0.028 → +0.035" — whose only surviving record is the finding's prose
table. This script re-measures it at the finding's own setup so the claim has an artifact again.

**A re-run is a new measurement, not a recovery of the lost one.** Rule 21 measured the torch path as
sensitive to `OMP_NUM_THREADS` at the third decimal, so the numbers below are expected to agree with the
finding's table rather than to reproduce it exactly; where they disagree the disagreement is reported rather
than averaged away.

    python -m experiments.e96_fisher_batch_sweep
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e8_rate_network import main as e8_main

#: the finding's setup, read off `docs/findings/2026-09-22-fisher-batches-negative.md` §2
BATCH_COUNTS = [8, 32, 128]
SETUP = dict(circuit_size=800, iters=500, lr=0.003, batch=32, lam=0.1,
             methods="naive,ewc,ewc-block,ewc-block-rand", basis="cell_class",
             train=96, test=48, repeats=1)

#: what the finding's table records, for the comparison -- (mean forgetting, final accuracy)
REPORTED = {
    8: dict(naive=(+0.010, 0.896), ewc=(+0.063, 0.826), bio=(+0.104, 0.826), rand=(+0.042, 0.854)),
    32: dict(naive=(+0.010, 0.896), ewc=(+0.125, 0.792), bio=(+0.104, 0.833), rand=(+0.010, 0.868)),
    128: dict(naive=(+0.010, 0.896), ewc=(+0.250, 0.701), bio=(+0.073, 0.792), rand=(+0.094, 0.819)),
}


def artifact(nb: int) -> Path:
    return Path(f"runs/e96_fisher_batches_{nb}_1seed.json")


def measure(args) -> int:
    for nb in BATCH_COUNTS:
        path = artifact(nb)
        if path.exists() and not args.overwrite:
            print(f"   {nb:>4} batches   present, skipped")
            continue
        print(f"=== {nb} Fisher batches, {SETUP['repeats']} repeat(s)")
        argv = ["--circuit-size", str(SETUP["circuit_size"]), "--iters", str(SETUP["iters"]),
                "--lr", str(SETUP["lr"]), "--batch", str(SETUP["batch"]),
                "--lam", str(SETUP["lam"]), "--methods", SETUP["methods"],
                "--basis", SETUP["basis"], "--train", str(SETUP["train"]),
                "--test", str(SETUP["test"]), "--repeats", str(SETUP["repeats"]),
                "--fisher-batches", str(nb), "--json-out", str(path)]
        e8_main(argv)
        print()
    return 0


def report(args) -> int:
    print("=" * 112)
    print("1. THE SWEEP, RE-MEASURED, AGAINST WHAT THE FINDING REPORTS")
    print("=" * 112)
    print("   mean forgetting (final accuracy), single seed, lambda 0.1, cs = 800\n")
    print(f"   {'batches':>8}{'source':>12}{'naive':>16}{'ewc diagonal':>16}"
          f"{'ewc block (bio)':>18}{'ewc block (rand)':>18}")
    rows = {}
    for nb in BATCH_COUNTS:
        d = json.load(open(artifact(nb), encoding="utf-8")) if artifact(nb).exists() else None
        if d is not None:
            rows[nb] = {m: dict(forgetting=float(v["mean_forgetting"]),
                                accuracy=float(v["final_accuracy"]))
                        for m, v in d["methods"].items()}
            cells = "".join(f"{rows[nb][m]['forgetting']:>+8.3f} ({rows[nb][m]['accuracy']:.3f})"
                            for m in ("naive", "ewc", "ewc-block", "ewc-block-rand")
                            if m in rows[nb])
            print(f"   {nb:>8}{'e96':>12}{cells}")
        rep = REPORTED[nb]
        cells = "".join(f"{rep[m][0]:>+8.3f} ({rep[m][1]:.3f})"
                        for m in ("naive", "ewc", "bio", "rand"))
        print(f"   {nb:>8}{'finding':>12}{cells}")
    if not rows:
        print("\n   nothing measured yet")
        return 0

    print()
    print("=" * 112)
    print("2. THE TWO CLAIMS THE PAPER MAKES FROM THIS SWEEP")
    print("=" * 112)
    diag_forget = [rows[nb]["ewc"]["forgetting"] for nb in BATCH_COUNTS if "ewc" in rows[nb]]
    diag_acc = [rows[nb]["ewc"]["accuracy"] for nb in BATCH_COUNTS if "ewc" in rows[nb]]
    if len(diag_forget) == len(BATCH_COUNTS):
        mono_f = all(diag_forget[i] < diag_forget[i + 1] for i in range(len(diag_forget) - 1))
        mono_a = all(diag_acc[i] > diag_acc[i + 1] for i in range(len(diag_acc) - 1))
        print(f"   (a) 'the diagonal's forgetting rises from {diag_forget[0]:+.3f} to {diag_forget[-1]:+.3f}"
              f" as batches go 8 -> 128'")
        print(f"       re-measured: {diag_forget[0]:+.3f} -> {diag_forget[-1]:+.3f}, "
              f"monotone over the three points: **{mono_f}**"
              f"   (accuracy {diag_acc[0]:.3f} -> {diag_acc[-1]:.3f}, monotone declining: {mono_a})")
        print(f"   (b) 'the biological partition never overtakes the diagonal, naive, or consistently its")
        print(f"       own matched control'")
        for nb in BATCH_COUNTS:
            if "ewc-block" not in rows[nb]:
                continue
            bio, rnd, diag = rows[nb]["ewc-block"], rows[nb]["ewc-block-rand"], rows[nb]["ewc"]
            print(f"       {nb:>4} batches: bio {bio['forgetting']:+.3f} vs rand {rnd['forgetting']:+.3f}"
                  f" (bio {'worse' if bio['forgetting'] > rnd['forgetting'] else 'BETTER'})"
                  f"   vs diagonal {diag['forgetting']:+.3f}"
                  f" (bio {'worse' if bio['forgetting'] > diag['forgetting'] else 'BETTER'})")
        signs = [np.sign(rows[nb]["ewc-block"]["forgetting"] - rows[nb]["ewc-block-rand"]["forgetting"])
                 for nb in BATCH_COUNTS]
        print(f"       bio-minus-rand sign across the sweep: {[int(s) for s in signs]}, "
              f"consistent: **{len(set(signs)) == 1}**")
    out = dict(config=vars(args), setup=SETUP, batch_counts=BATCH_COUNTS,
               measured=rows, reported=REPORTED, note=(
                   "a re-run, not a recovery: rule 21 measured the torch path as OMP_NUM_THREADS-sensitive "
                   "at the third decimal"))
    write_json(args.json_out, out)
    print(f"\nwrote {args.json_out}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--report-only", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--json-out", default="runs/e96_fisher_batch_sweep.json")
    args = p.parse_args(argv)
    if not args.report_only:
        measure(args)
    return report(args)


if __name__ == "__main__":
    raise SystemExit(main())
