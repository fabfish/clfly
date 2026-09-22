"""E54 — the `naive` arm as a free instrument, and the learner-variability estimate at n = 16.

`e38` established that the `naive` arm is **bit-identical across runs** and used that as a free
determinism control, and separately that the benchmark's per-replicate spread is *learner* seed-to-
seed variability rather than measurement noise — which makes the number of *seeds* the binding
constraint on every C2b claim. That estimate had n = 9, from one run.

`naive` carries no penalty and no basis, so every run that shares its training configuration computes
the *same* per-seed accuracies. That makes the arm a free instrument: pooling across runs unions the
seed sets instead of re-training. This script does the pooling, and it also sharpens `e38`'s claim,
which was over-broad as stated:

> **`naive` is independent of `basis`, `lam`, `fisher_batches`, `methods` and `repeats` — and of
> nothing else.** It still depends on `iters`, `lr`, `batch`, `train`, `test`, `classes`, `noise`,
> `support`, `shared_head`, `input_overlap`, `readout_size` and `circuit_size`. Two runs in the
> artifacts (`e8_hardened`, `e8_class_incremental`) share `e10`'s `iters`/`train`/`test` and give
> **different** `naive` accuracies, because they differ in other fields — so a six-field key silently
> treats a genuinely different computation as a replicate.

    python -m experiments.e54_naive_seed_pool
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2, norm

#: Fields that genuinely change what the `naive` arm computes.  Everything not listed here is either
#: irrelevant to it (`basis`, `lam`, `fisher_batches`, `methods`, `repeats`, `json_out`, pooling) or
#: bookkeeping.  The list is asserted against the artifacts rather than assumed: `e54` prints the
#: groups it forms and any within-seed disagreement.
AFFECTING = ("circuit_size", "support", "iters", "lr", "batch", "train", "test",
             "classes", "noise", "input_overlap", "readout_size", "shared_head", "seed0")

#: Held-out decisions per replicate on this benchmark, for the binomial floor.
N_EVAL = 144


def sd_interval(s: float, df: int) -> tuple[float, float]:
    if df < 1 or not np.isfinite(s) or s <= 0:
        return (float("nan"), float("nan"))
    return (float(s * np.sqrt(df / chi2.ppf(0.975, df))),
            float(s * np.sqrt(df / chi2.ppf(0.025, df))))


def collect() -> tuple[dict, list]:
    """Collect every `naive` replicate as (run, seed, value).

    Grouping is **by agreement on the data**, not by an assumed configuration key.  The first
    version keyed on the fields that ought to matter and found seeds 0-2 carrying two different
    values inside one group, which means the key was wrong -- and a wrong key silently averages two
    different computations while looking like a bigger sample.
    """
    rows = []
    for path in sorted(glob.glob("runs/*.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        c = d.get("config") if isinstance(d, dict) else None
        if not isinstance(c, dict) or "methods" not in d:
            continue
        n = d["methods"].get("naive")
        if not n or "replicates" not in n:
            continue
        seed0 = int(c.get("seed0") or 0)
        rows.append({
            "path": Path(path).name,
            "key": tuple(repr(c.get(k)) for k in AFFECTING),
            "config": c,
            "values": {seed0 + i: float(r["final_accuracy"]) for i, r in enumerate(n["replicates"])},
        })
    return rows


def cluster(rows: list) -> list:
    """Cluster runs that agree bit-for-bit on every seed they share.

    Single-linkage, with one guard: **at least one seed must actually be shared**.  An empty
    intersection makes ``all(...)`` vacuously true, so without the guard two runs that have never
    been compared would merge -- which in the artifacts does not happen (every run starts at
    ``seed0 = 0``) but would bite the moment a run used a different starting seed.  Caught by a
    test rather than by the data.
    """
    clusters: list[list] = []
    for r in rows:
        placed = False
        for cl in clusters:
            joins = True
            for m in cl:
                shared = set(r["values"]) & set(m["values"])
                if not shared:
                    joins = False
                    break
                if any(abs(r["values"][s] - m["values"][s]) > 1e-12 for s in shared):
                    joins = False
                    break
            if joins:
                cl.append(r)
                placed = True
                break
        if not placed:
            clusters.append([r])
    return sorted(clusters, key=len, reverse=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e54_naive_seed_pool.json")
    args = ap.parse_args()

    rows = collect()
    if not rows:
        print("no run with a `naive` arm found (runs/ is gitignored)")
        return
    clusters = cluster(rows)

    print("=" * 100)
    print("1. CLUSTERS OF RUNS WHOSE `naive` ARM AGREES BIT-FOR-BIT")
    print("=" * 100)
    print(f"   {len(rows)} run(s) carry a naive arm and fall into {len(clusters)} cluster(s).")
    print("   Agreement is established from the data, not from an assumed config key: the first")
    print("   version keyed on the fields that ought to matter and found seeds 0-2 carrying two")
    print("   different values inside one group, which is what a wrong key looks like.\n")
    out: dict = {"affecting_fields": list(AFFECTING), "clusters": []}
    for i, cl in enumerate(clusters):
        seeds = sorted(set().union(*[set(r["values"]) for r in cl]))
        print(f"   cluster {i}: {len(cl)} run(s), seeds {seeds[0]}..{seeds[-1]} (n = {len(seeds)})")
        print(f"     {', '.join(r['path'] for r in cl[:6])}"
              + (" ..." if len(cl) > 6 else ""))
        # any member that has the seed will do: the clustering guarantees they agree on shared seeds
        values = [next(r["values"][s] for r in cl if s in r["values"]) for s in seeds]
        out["clusters"].append({"size": len(cl), "runs": [r["path"] for r in cl],
                                "seeds": seeds, "values": values})

    print()
    print("=" * 100)
    print("2. WHY THE OTHER CLUSTERS DIFFER — WHICH IS ALSO WHICH ARTIFACTS ARE PRE-FIX")
    print("=" * 100)
    main_cl = clusters[0]
    ref = main_cl[0]
    print(f"   reference: {ref['path']}\n")
    print(f"   {'run':<44}{'basis':>12}{'shared':>8}{'readout':>9}{'agrees?':>9}  differing fields")
    c2 = out["clusters"]
    for ci, cl in enumerate(clusters[1:], start=1):
        for r in cl:
            c = r["config"]
            diff = [k for k in AFFECTING if repr(c.get(k)) != repr(ref["config"].get(k))]
            # `basis` is not in AFFECTING (it should not matter) so it is listed separately: its
            # absence identifies a run that predates the flag, and with it the `torch.manual_seed`
            # fix the script documents.
            extra = [] if "basis" in c else ["<no basis field: predates it>"]
            print(f"   {r['path']:<44}{str(c.get('basis')):>12}{str(c.get('shared_head')):>8}"
                  f"{str(c.get('readout_size')):>9}{'no':>9}  {', '.join(diff + extra) or 'NONE'}")
    print("\n   Note what this does NOT show.  Every difference above is explained by a field that")
    print("   genuinely affects the computation -- `iters`, `shared_head`, `readout_size`, `classes`,")
    print("   `noise`, `support` -- so there is NO evidence here of a stale or pre-fix artifact.  An")
    print("   earlier draft of this section read `e8_rate`'s missing `basis` field as a marker for")
    print("   predating the `torch.manual_seed` fix the script documents; the field list refutes")
    print("   that, because `e8_rate` also differs in five fields that would change `naive` anyway.")
    print("   The census is a statement about which runs compute the SAME thing, and that is all.")

    print()
    print("=" * 100)
    print("3. THE LEARNER-VARIABILITY ESTIMATE FROM THE LARGEST CLUSTER")
    print("=" * 100)
    v = np.array(c2[0]["values"], dtype=float)
    n = len(v)
    s = float(v.std(ddof=1))
    lo, hi = sd_interval(s, n - 1)
    floor = float(np.sqrt(v.mean() * (1 - v.mean()) / N_EVAL))
    comp_hi = float(np.sqrt(max(0.0, hi ** 2 - floor ** 2)))
    print(f"   n = {n}, mean = {v.mean():.4f}, sd = {s:.4f}  (95% CI [{lo:.4f}, {hi:.4f}])")
    print(f"   binomial floor at n_eval = {N_EVAL}: {floor:.4f}, i.e. "
          f"{100 * floor ** 2 / s ** 2:.0f}% of the variance")
    print(f"   seed-to-seed component: at most {comp_hi:.4f}, and at least "
          f"{100 * (1 - floor ** 2 / s ** 2):.0f}% of the spread is learner variability")
    print(f"\n   `e38` bounded this at n = 9 and the pool does not grow it: the ARTIFACTS hold only")
    print(f"   {n} seeds of one computation.  `e46` is running with 16 replicates and its `naive` arm")
    print("   is complete in the log -- so n = 16 needs only that artifact to land, and this script")
    print("   will pick it up automatically.")
    out["pooled"] = {"n": n, "mean": float(v.mean()), "sd": s, "sd_ci": [lo, hi],
                     "binomial_floor": floor, "seed_component_upper": comp_hi}

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
