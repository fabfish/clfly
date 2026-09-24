"""E157 -- the price of resolving each of the line's live contrasts, in seeds.

`e149` answered this for one quantity (the two interventions' interaction: 62 seeds for 2 sigma, 139 for 3). The
line now carries about a dozen contrasts whose resolutions are quoted in the paper, and the plan keeps choosing
between "run it at forty like everything else" and "leave it as a bound" without a table of what the choice costs.
This is that table.

For each contrast, from the forty paired seeds already on disk:

    d, sem      the paired change and its standard error
    sd          the PAIRED per-seed sd, i.e. sem * sqrt(40)
    n(2s), n(3s)  the seeds this very contrast would need for 2 and 3 sigma, if the observed effect is the true one

**The circularity is the whole point, so it is reported rather than hidden**: an effect estimated from an
underpowered design is biased away from zero, so `n(3s) = (3*sd/d)^2` uses an optimistic `d`. The last two columns
therefore repeat the count for **half** and **a quarter** of the observed effect, which is what a larger study
would tend to find. A contrast that needs 40 seeds at the observed effect and 640 at a quarter of it is a contrast
whose *form* is wrong, not one that needs more seeds.

    python -m experiments.e157_power_table
    python -m experiments.e157_power_table --json-out runs/e157_power_table.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: (label, path A, method A, path B, method B). Defaults are the family's own baseline, so a contrast against
#: `naive` is against the arm of the family it was run in.
C2B_PLASTIC = "runs/e140_r32_methods_plastic_40reps.json"
C2B_FROZEN = "runs/e140_r32_methods_frozenbias_40reps.json"
WIRING = "runs/e144_r32_overlap1_methods_40reps.json"
E133 = "runs/e133_r32_naive_ewc_40reps.json"
E150_4 = "runs/e150_r32_overlap1_frozenbias_ewc_lam3e-4.json"
E150_3 = "runs/e150_r32_overlap1_frozenbias_ewc_lam3e-3.json"
E147_4 = "runs/e147_r32_frozenbias_ewc_lam3e-4.json"
E147_3 = "runs/e147_r32_frozenbias_ewc_lam3e-3.json"
CONTRASTS: tuple[tuple[str, str, str, str, str], ...] = (
    ("plastic: replay - naive", C2B_PLASTIC, "replay", C2B_PLASTIC, "naive"),
    ("plastic: ewc - naive", C2B_PLASTIC, "ewc", C2B_PLASTIC, "naive"),
    ("plastic: block - block-rand (the BIOLOGY)", C2B_PLASTIC, "ewc-block", C2B_PLASTIC, "ewc-block-rand"),
    ("frozen: ewc - naive", C2B_FROZEN, "ewc", C2B_FROZEN, "naive"),
    ("frozen: replay - naive", C2B_FROZEN, "replay", C2B_FROZEN, "naive"),
    ("frozen: block - block-rand (the BIOLOGY)", C2B_FROZEN, "ewc-block", C2B_FROZEN, "ewc-block-rand"),
    ("wiring: ewc - naive", WIRING, "ewc", WIRING, "naive"),
    ("wiring: block - block-rand (the BIOLOGY)", WIRING, "ewc-block", WIRING, "ewc-block-rand"),
    ("frozen+ewc, lambda step 3e-4 -> 3e-3 (base)", E147_3, "ewc", E147_4, "ewc"),
    ("frozen+ewc, lambda step (shared-input)", E150_3, "ewc", E150_4, "ewc"),
    ("frozen+ewc 3e-4 - the freeze (shared-input)", E150_4, "ewc", "runs/e143_r32_overlap1_frozenbias.json", "naive"),
    ("frozen offsets - naive (base)", "runs/e125_r32_frozenbias.json", "naive", E133, "naive"),
)
#: the same list restricted to the column this project only recently started reading
NEWEST_OF = ("plastic: replay - naive", "frozen: ewc - naive", "frozen: block - block-rand (the BIOLOGY)",
             "frozen: replay - naive", "wiring: block - block-rand (the BIOLOGY)")


def load(path: Path, method: str) -> dict | None:
    if not Path(path).is_file():
        return None
    entry = __import__("json").loads(Path(path).read_text(encoding="utf-8")).get("methods", {}).get(method)
    if entry is None:
        return None
    reps = entry["replicates"]
    return {"forgetting": np.array([r["mean_forgetting"] for r in reps]),
            "newest": np.array([r["final_per_task"][-1] for r in reps]), "n": len(reps)}


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.asarray(a) - np.asarray(b)
    n = len(d)
    sd = float(d.std(ddof=1)) if n > 1 else float("nan")
    sem = sd / math.sqrt(n) if n > 1 else float("nan")
    mean = float(d.mean())
    return {"change": mean, "sem": sem, "sd": sd, "n": n,
            "sigma": (abs(mean) / sem) if sem else float("nan")}


def seeds_for(sd: float, effect: float, z: float) -> float:
    """Seeds a contrast with this paired sd needs for ``z`` sigma at this effect size. Infinite at zero."""
    if effect == 0 or not np.isfinite(sd):
        return float("inf")
    return (z * sd / abs(effect)) ** 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    rows = []
    for label, pa, ma, pb, mb in CONTRASTS:
        a, b = load(Path(pa), ma), load(Path(pb), mb)
        if a is None or b is None:
            print(f"   missing: {label}")
            continue
        for metric in ("forgetting",) + (("newest",) if label in NEWEST_OF else ()):
            r = paired(a[metric], b[metric])
            rows.append({"label": label, "metric": metric, "change": r["change"], "sem": r["sem"], "sd": r["sd"],
                         "sigma": r["sigma"], "n_now": r["n"],
                         "n_2s": seeds_for(r["sd"], r["change"], 2), "n_3s": seeds_for(r["sd"], r["change"], 3),
                         "n_3s_half": seeds_for(r["sd"], r["change"] / 2, 3),
                         "n_3s_quarter": seeds_for(r["sd"], r["change"] / 4, 3)})

    print("== what each live contrast costs, in seeds (paired, forty on disk) ==")
    print(f"   {'contrast':<48}{'metric':<11}{'d':>9}{'sigma':>7}{'n(2s)':>7}{'n(3s)':>7}{'x2':>7}{'x4':>8}")
    for r in sorted(rows, key=lambda r: (not np.isfinite(r["n_3s"]), r["n_3s"])):
        def f(x):
            return "inf" if not np.isfinite(x) else f"{x:.0f}"
        print(f"   {r['label']:<48}{r['metric']:<11}{r['change']:>+9.4f}{r['sigma']:>7.2f}"
              f"{f(r['n_2s']):>7}{f(r['n_3s']):>7}{f(r['n_3s_half']):>7}{f(r['n_3s_quarter']):>8}")

    fin = [r for r in rows if np.isfinite(r["n_3s"])]
    print(f"\n   contrasts measured: {len(rows)}   already resolved at 3s at forty seeds: "
          f"{sum(1 for r in rows if r['sigma'] >= 3)}")
    if fin:
        print(f"   median n(3s) at the observed effect {np.median([r['n_3s'] for r in fin]):.0f}; "
              f"at half the effect {np.median([r['n_3s_half'] for r in fin]):.0f}")
        print("   the two end columns are the honest ones: an effect estimated at forty seeds is biased away")
        print("   from zero, so a contrast whose n(3s) is fine at the observed d and hopeless at d/2 needs a")
        print("   different FORM, not more seeds (rule 41).")

    if args.json_out:
        write_json(args.json_out, {"rows": rows})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
