"""E311 -- the two tasks the metric averages: what `mean_forgetting` is a mean *of*, position by position.

`e299` noted in passing that *"`mean_forgetting` is a mean over the first `T - 1` tasks"* and `e304` showed it is the
lost half of the shortfall. `e310` then measured that the position in the sequence predicts the level a task reaches
(0.9605 first, 0.9168 second, 0.9345 third). **This unit puts the two together**: the metric is a mean over the first
`T - 1` positions, and for this substrate's three-task suites those are **the highest-level and the lowest-level task
in the sequence**, while the excluded one is neither.

    position 0   level 0.9605   lost 0.07744      <- in the metric
    position 1   level 0.9168   lost 0.05605      <- in the metric
    position 2   level 0.9345   lost 0.00000      <- cannot be forgotten, by construction

Four claims, registered before the reading below was taken:

- **T1 -- the denominator is `T - 1`.** The stored `mean_forgetting` equals the mean of the lost term over the first
  two positions, in every arm. **Falsifier**: one that differs.
- **T2 -- and the excluded term is zero by construction.** The last position's lost term is exactly zero, because
  `R[T-1][T-1]` is both the level the task reached and the level it ended at. **Falsifier**: a non-zero last term.
- **T3 -- and the two terms in the mean are not exchangeable.** The first position's lost term exceeds the second's on
  average by at least a quarter, so the metric is a mean of the best-learned and the worst-learned task. **Falsifier**:
  a gap below a quarter.
- **T4 -- and what a task loses tracks what it had.** Over the arms, the rank correlation between the first position's
  reached level and its lost term is positive. **Falsifier**: a correlation at or above zero being absent, i.e. at or
  below zero.

**What it means.** The metric is a mean of two terms that come from opposite ends of the position profile `e310`
measured, and it is computed on a substrate where the profile is worth four points. So an arm's `mean_forgetting` is
partly a statement about how much there was to lose at the two positions the metric happens to average, which is why
`e304`'s decomposition and `e306`'s ordering both needed the level alongside the loss.

**What it cannot do.** *The last position's zero is arithmetic and not a result*: it is excluded from the metric
because it cannot be forgotten, so T2 checks the convention and not a finding about the substrate. *T4 is a
correlation over arms that are not independent*, so +0.28 describes the corpus and is not an estimate. *The three
positions are the sequence's and not the tasks'*: `e310` showed the ordering survives a change of suite, but for any
single artifact the position and the task are the same object, so nothing here separates "task 0" from "first". *And
this unit reads the corpus's three-task suites only*: a longer sequence would average more positions, and the shape of
the mean would be a different question.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e304_the_decomposition_the_block_asked_for as e304

RUNS = Path("runs")
#: The smallest gap T3 asks for between the first and second positions' lost terms, as a ratio.
GAP = 1.25
#: What counts as "the same number" between the stored field and the recomputed mean.
TOLERANCE = 1e-9
CLAIMS = (
    ("T1", "the denominator is `T - 1`",
     "The stored `mean_forgetting` equals the mean of the lost term over the first two positions in every arm",
     "falsifier: one that differs"),
    ("T2", "and the excluded term is zero by construction",
     "The last position's lost term is exactly zero in every arm",
     "falsifier: a non-zero last term"),
    ("T3", "and the two terms in the mean are not exchangeable",
     f"The first position's lost term exceeds the second's on average by a factor of at least {GAP}",
     "falsifier: a gap below a quarter"),
    ("T4", "and what a task loses tracks what it had",
     "The rank correlation between the first position's reached level and its lost term is positive",
     "falsifier: a correlation at or below zero"),
)


def reading(root: Path = RUNS) -> dict:
    rows, _ = e304.replicates(root)
    three = [r for r in rows if r["n_tasks"] == 3]
    n = len(three)
    if not n:
        return {"arms": 0}
    lost = {j: [r["lost"][j] for r in three] for j in range(3)}
    reached = {j: [r["reached"][j] for r in three] for j in range(3)}
    stored = [r.get("metric") for r in three if isinstance(r.get("metric"), (int, float))]
    first_two = [statistics.fmean(r["lost"][:2]) for r in three if isinstance(r.get("metric"), (int, float))]
    return {
        "arms": n,
        "levels": [statistics.fmean(reached[j]) for j in range(3)],
        "lost_means": [statistics.fmean(lost[j]) for j in range(3)],
        "matched": sum(1 for a, b in zip(stored, first_two) if abs(a - b) <= TOLERANCE),
        "scored": len(stored),
        "max_last_lost": max(abs(v) for v in lost[2]),
        "ratio": (statistics.fmean(lost[0]) / statistics.fmean(lost[1])) if statistics.fmean(lost[1]) else None,
        "rho_reached_lost_first": e304.rank_correlation(reached[0], lost[0]),
        "rho_gap_metric": e304.rank_correlation([r["reached"][0] - r["reached"][1] for r in three],
                                                [r["metric"] for r in three if isinstance(r.get("metric"), (int, float))]),
        "all_three_mean": statistics.fmean(statistics.fmean(r["lost"]) for r in three),
        "first_two_mean": statistics.fmean(statistics.fmean(r["lost"][:2]) for r in three),
    }


def judge(r: dict) -> list[dict]:
    if not r.get("arms"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm records a three-task suite"}
                for c in CLAIMS]

    out = [{"id": "T1", "measured": f"the stored `mean_forgetting` equals the mean of the lost term over the first two "
                                    f"positions in {r['matched']} of {r['scored']} arms",
            "verdict": "MET -- the metric's denominator is `T - 1` and not `T`" if
            r["scored"] and r["matched"] == r["scored"] else
            f"FALSIFIER FIRED -- {r['scored'] - r['matched']} arm(s) differ"}]

    out.append({"id": "T2", "measured": f"the largest absolute last-position lost term is {r['max_last_lost']:.2e}",
                "verdict": "MET -- the position the metric excludes cannot be forgotten at all"
                if r["max_last_lost"] <= TOLERANCE else
                f"FALSIFIER FIRED -- {r['max_last_lost']:.2e}"})

    ratio = r["ratio"]
    out.append({"id": "T3", "measured": f"the lost term averages {r['lost_means'][0]:.5f} at the first position and "
                                        f"{r['lost_means'][1]:.5f} at the second, a factor of {ratio:.3f}, while the "
                                        f"levels are {r['levels'][0]:.4f} and {r['levels'][1]:.4f}",
                "verdict": "MET -- the metric is a mean of the best-learned and the worst-learned task"
                if ratio is not None and ratio >= GAP else f"FALSIFIER FIRED -- {ratio}"})

    rho = r["rho_reached_lost_first"]
    out.append({"id": "T4", "measured": f"over {r['arms']} arms the rank correlation between the first position's "
                                        f"reached level and its lost term is {rho:+.3f}; the gap between the first "
                                        f"two positions against the metric is {r['rho_gap_metric']:+.3f}",
                "verdict": "MET -- a task that was learned better has more to lose" if rho is not None and rho > 0
                else f"FALSIFIER FIRED -- {rho}"})
    return out


def report(r: dict) -> int:
    print("== what `mean_forgetting` is a mean of, position by position ==")
    print(f"   {r['arms']} arm-replicates over three-task suites")
    print(f"   {'position':10} {'level reached':>14} {'lost':>10}  {'in the metric?':>16}")
    for j in range(3):
        where = "yes" if j < 2 else "no, and it is zero"
        print(f"   {j:<10} {r['levels'][j]:14.4f} {r['lost_means'][j]:10.5f}  {where:>16}")
    print(f"   the metric is a mean over the first two positions ({r['first_two_mean']:.5f}); over all three it would "
          f"be {r['all_three_mean']:.5f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the metric averages the two positions `e310` showed are the furthest apart in level, so an arm's")
    print("    forgetting is partly a statement about how much there was to lose where the average happens to fall)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
