"""E189 -- the two lines move in opposite directions on the overlap axis, and the decomposition says where.

`e188` found that raising the input overlap from 0 to 1 raises the network line's forgetting in nine of nine
matched comparisons. `e7`'s own controlled sweep found the opposite in the analytic line: **more input overlap means
less interference**, perfectly monotone over six levels (Spearman = -1.000), which its finding records as the
refutation of C4's direction. Both are in this repository and nothing compares them.

**They are not simple opposites, and this is the measurement.** Both lines can be split by *task distance*, and the
split is what localises the disagreement:

- the analytic line's `controlled` block reports `mean_interference_near` (adjacent pairs) and
  `mean_interference_far` (distant pairs) per level, so the near and far responses are read directly;
- the network line's retention matrices give the same split: for a three-task sequence the ordered pairs are
  (1->0) and (2->1) at distance 1 and (2->0) at distance 2, and each pair's cost is `R[k-1, j] - R[k, j]`, paired
  over replicates.

The pairs and their admission rules are **imported from `e188`** rather than restated, so the two audits cannot
drift apart about which payloads are evidence.

    python -m experiments.e189_overlap_sign_across_lines
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e188_overlap_contrast import INERT_FOR, PAIRS, differing_fields, load

RUNS = Path("runs")
ANALYTIC = "e7_interference.json"

#: What each line says today, declared so the exit code counts changes rather than reporting a constant.
#:
#: The **analytic** line is one artifact and its two components are exact: over six overlap levels the near-pair
#: interference falls (and crosses below zero) while the far-pair interference rises.
#: The **network** line is nine comparisons and neither component is unanimous, so what is declared is the tally:
#: near rises in eight of nine with none falling, far rises in eight of nine with one falling. A declaration of
#: "rises" for a component that is mixed would be a claim the data do not support, which is the mistake this file
#: was written with on its first run.
DECLARED = {("analytic", "near"): "falls", ("analytic", "far"): "rises"}
DECLARED_TALLY = {"near": {"rises": 7, "falls": 0, "unresolved": 2},
                  "far": {"rises": 1, "falls": 0, "unresolved": 8}}


def direction(first: float, last: float, tol: float = 1e-12) -> str:
    if last - first > tol:
        return "rises"
    if first - last > tol:
        return "falls"
    return "flat"


def analytic_levels(path: Path = RUNS / ANALYTIC) -> list[dict]:
    """`e7`'s controlled sweep: six overlap levels with the near and far means already split."""
    d = json.loads(path.read_text(encoding="utf-8"))
    return [{"level": r["level"], "achieved": r["achieved_overlap"], "mean": r["mean_interference"],
             "near": r["mean_interference_near"], "far": r["mean_interference_far"]}
            for r in d["controlled"]]


def pair_costs(path: Path, method: str) -> dict[tuple[int, int], np.ndarray]:
    """The cost of each ordered pair, from the retention matrix: what training task k cost the older task j."""
    d = json.loads(path.read_text(encoding="utf-8"))
    arm = (d.get("methods") or {}).get(method)
    if arm is None:
        return {}
    R = np.array([[np.nan if v is None else v for v in r["retention"]] for r in arm["replicates"]], dtype=float)
    return {(k, j): R[:, k - 1, j] - R[:, k, j]
            for k in range(1, R.shape[1]) for j in range(k)}


def split(costs: dict[tuple[int, int], np.ndarray]) -> dict:
    """The same near/far split the analytic block reports, over the pairs a three-task sequence realises."""
    near = [v for (k, j), v in sorted(costs.items()) if k - j == 1]
    far = [v for (k, j), v in sorted(costs.items()) if k - j > 1]
    def agg(series):
        if not series:
            return {"mean": None, "sem": None, "n_pairs": 0}
        m = float(np.mean([s.mean() for s in series]))
        sem = float(np.sqrt(sum(s.var(ddof=1) / len(s) for s in series)) / len(series))
        return {"mean": m, "sem": sem, "n_pairs": len(series)}
    return {"near": agg(near), "far": agg(far)}


def audit(runs_dir: Path = RUNS, pairs=PAIRS, declared=DECLARED) -> dict:
    levels = analytic_levels(runs_dir / ANALYTIC)
    analytic_dir = {"near": direction(levels[0]["near"], levels[-1]["near"]),
                    "far": direction(levels[0]["far"], levels[-1]["far"]),
                    "mean": direction(levels[0]["mean"], levels[-1]["mean"])}
    rows, refused = [], []
    for label, method, lo, hi, expect in pairs:
        pa, pb = runs_dir / lo, runs_dir / hi
        if not pa.is_file() or not pb.is_file():
            refused.append({"label": label, "why": "artifact missing"})
            continue
        diff = differing_fields(load(pa)["config"], load(pb)["config"])
        bad = {k: v for k, v in diff.items() if k not in INERT_FOR.get(method, set())}
        if bad or expect != "pair":
            refused.append({"label": label, "why": f"not a pair: {sorted(bad)}" if bad else "declared as a refusal"})
            continue
        a, b = split(pair_costs(pa, method)), split(pair_costs(pb, method))
        if a["near"]["mean"] is None or b["near"]["mean"] is None:
            refused.append({"label": label, "why": "no retention matrix for this method"})
            continue
        rows.append({"label": label, "method": method, "overlap0": a, "overlap1": b,
                     "near_change": b["near"]["mean"] - a["near"]["mean"],
                     "far_change": b["far"]["mean"] - a["far"]["mean"]})
    # A component is called resolved only when the paired change clears twice its own standard error, so a
    # direction that is a rounding artefact is counted as unresolved rather than as a fall -- which is what the
    # first version did, on a change of 1e-5.
    tally = {comp: {"rises": 0, "falls": 0, "unresolved": 0} for comp in ("near", "far")}
    for r in rows:
        for comp in ("near", "far"):
            a, b = r["overlap0"][comp], r["overlap1"][comp]
            change = b["mean"] - a["mean"]
            sem = float(np.hypot(a["sem"] or 0.0, b["sem"] or 0.0))
            r[f"{comp}_change"] = change
            r[f"{comp}_sem"] = sem
            r[f"{comp}_direction"] = ("unresolved" if sem == 0 or abs(change) < 2 * sem else
                                      "rises" if change > 0 else "falls")
            tally[comp][r[f"{comp}_direction"]] += 1
    net_dir = {comp: (f"{tally[comp]['rises']} of {len(rows)} rise at 2 sigma"
                      + (f", {tally[comp]['falls']} fall" if tally[comp]["falls"] else "")
                      + f", {tally[comp]['unresolved']} unresolved") for comp in ("near", "far")}
    got = {("analytic", "near"): analytic_dir["near"], ("analytic", "far"): analytic_dir["far"]}
    mismatches = [{"what": f"{line} {comp}", "declared": want, "got": got[(line, comp)]}
                  for (line, comp), want in declared.items() if got[(line, comp)] != want]
    mismatches += [{"what": f"network {comp} tally", "declared": want, "got": tally[comp]}
                   for comp, want in DECLARED_TALLY.items() if tally[comp] != want]
    return {"analytic_levels": levels, "analytic_directions": analytic_dir,
            "network_comparisons": rows, "network_directions": net_dir, "network_tally": tally,
            "refused": refused, "mismatches": mismatches, "n_mismatches": len(mismatches)}


def report(res: dict) -> int:
    print("   == the analytic line: e7's controlled sweep, six overlap levels ==")
    print(f"   {'level':>6} {'achieved':>9} {'mean':>10} {'near (d=1)':>12} {'far (d>1)':>11}")
    for r in res["analytic_levels"]:
        print(f"   {r['level']:6.2f} {r['achieved']:9.4f} {r['mean']:10.6f} {r['near']:12.6f} {r['far']:11.6f}")
    print(f"   direction over the six levels: mean {res['analytic_directions']['mean']}, "
          f"near {res['analytic_directions']['near']}, far {res['analytic_directions']['far']}")
    print("   == the network line: the same split from the retention matrices ==")
    print(f"   {'comparison':48} {'near 0':>9} {'near 1':>9} {'far 0':>9} {'far 1':>9}")
    for r in res["network_comparisons"]:
        print(f"   {r['label']:48} {r['overlap0']['near']['mean']:+9.4f} {r['overlap1']['near']['mean']:+9.4f} "
              f"{r['overlap0']['far']['mean']:+9.4f} {r['overlap1']['far']['mean']:+9.4f}")
    for comp in ("near", "far"):
        print(f"   direction, {comp:4}: {res['network_directions'][comp]}")
    for r in res["refused"]:
        print(f"   refused -- {r['label']}: {r['why']}")
    print("   == the localisation ==")
    print("        NEAR (adjacent) pairs: the analytic line says they get BETTER -- a monotone fall that crosses")
    print("        below zero over six levels -- and the network line says they get WORSE, resolved in 7 of 9.")
    print("        That is the whole of the disagreement and it is resolved on both sides.")
    print("        FAR (distant) pairs: a SMALL rise in both lines and unresolved in both -- the analytic block")
    print("        reports three-seed means without an interval, and the network's far changes clear 2 sigma in")
    print("        one of nine. The first version of this script called the far trend shared, which the network's")
    print("        own sems refuse.")
    print(f"   declarations the corpus contradicts: {res['n_mismatches']}")
    for m in res["mismatches"]:
        print(f"        {m['what']}: declared {m['declared']}, got {m['got']}")
    return res["n_mismatches"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.runs)
    n = report(res)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
