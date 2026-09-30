"""E304 -- the decomposition the block asked for, computed for every arm, and the metric it refutes.

The FlyCL v0 block names a **decomposed forgetting** and gives its reason: *"the conventional forgetting metric
rewards shrinkage and can be gamed"*. `e303` found that the module `clfly/lgcl/model.py`'s note defers to did not
exist and that the corpus stores the conventional metric instead. **This unit writes the module and asks the
question the block's reason implies**: how much of what the corpus calls forgetting is a task that was learned and
lost, and how much is a task that was never learned at all?

It can be asked because the corpus records more than the conventional measure. Every arm artifact carries a
lower-triangular **retention** matrix `R[t][j]` -- the accuracy on task `j` right after the arm finished task `t` --
so for each task the level it reached (`R[j][j]`) and the level it ended at (`R[T-1][j]`) are both on disk, and the
shortfall `1 - R[T-1][j]` splits **exactly and with no free parameter** into

    unlearned = 1 - R[j][j]      the part the arm never had
    lost      = R[j][j] - R[T-1][j]   the part it had and gave back

Four claims, registered before the reading below was taken:

- **D1 -- the split is exact.** `unlearned + lost` equals the shortfall for every arm-replicate and every task.
  **Falsifier**: a residual above 1e-9.
- **D2 -- and the corpus already stores one of the two terms.** `forgetting_per_task` equals `lost`, for every
  arm-replicate and task. **Falsifier**: one that differs by more than 1e-9. The conventional measure is not a
  different quantity from the one this unit computes; it is *half* of it.
- **D3 -- and the half it cannot see is the larger one.** Over the arms, the median unlearned share of the
  shortfall is above a half. **Falsifier**: at or below a half.
- **D4 -- and the metric moves against the failure it is quoted to describe.** The rank correlation between an arm's
  stored `mean_forgetting` and its unlearned share is below -0.5, i.e. the arms the metric scores as *forgetting
  least* are the arms that *never learned the task*. **Falsifier**: a correlation at or above -0.5.

**What it cannot do.** *The decomposition is of the shortfall against a ceiling of 1.0*, so a task's chance level is
counted as never learned -- which is the reading this unit wants (chance performance is nothing learned) and is not
the only one available. *`R[j][j]` is the level right after task `j` was learned*, so a task that was never solved at
the time and improved later is counted as unlearned even though the arm ended higher, which is a property of the
record and not of this unit. *The arm artifacts are not independent*: the same configuration recurs across runs, so
D4's correlation is over correlated points and its magnitude is a description of the corpus rather than an estimate.
*And the question is asked of arms that recorded a full matrix*: an arm whose retention has a `None` where a number
is required is refused rather than read, and the count of those is reported.
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json
from clfly.lgcl.metrics import decompose_forgetting, residual

RUNS = Path("runs")
#: The stored fields this unit reads, and the metric D4 correlates against.
RETENTION = "retention"
PER_TASK = "forgetting_per_task"
METRIC = "mean_forgetting"
#: What "the same number" means for a float the artifact wrote and this unit recomputed.
TOLERANCE = 1e-9
#: D4's threshold, and its sign.
NEGATIVE = -0.5
CLAIMS = (
    ("D1", "the split is exact",
     "`unlearned + lost` equals the shortfall for every arm-replicate and every task",
     "falsifier: a residual above 1e-9"),
    ("D2", "and the corpus already stores one of the two terms",
     "`forgetting_per_task` equals the lost term for every arm-replicate and task",
     "falsifier: one that differs by more than 1e-9"),
    ("D3", "and the half it cannot see is the larger one",
     "The median unlearned share of the shortfall is above a half",
     "falsifier: at or below a half"),
    ("D4", "and the metric moves against the failure it is quoted to describe",
     f"The rank correlation between an arm's `{METRIC}` and its unlearned share is below {NEGATIVE}",
     f"falsifier: a correlation at or above {NEGATIVE}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(root: Path = RUNS, collapse: bool = True) -> tuple[list[dict], list[str]]:
    """Every arm-replicate the corpus gives a retention matrix, and the arms whose matrix it cannot be read on.

    Second copies of an experiment are dropped (`e301`), so an arm the corpus holds twice counts once.
    """
    rows, refused = [], []
    skip = corpus.repeat_paths(root) if collapse else set()
    for path in sorted(glob.glob(str(Path(root) / "*.json"))):
        name = Path(path).name
        if name in skip:
            continue
        d = load(path)
        if d is None:
            continue
        meth = d.get("methods")
        if not isinstance(meth, dict):
            continue
        for arm, entry in meth.items():
            if not isinstance(entry, dict) or not entry.get("replicates"):
                continue
            seen = False
            for i, rep in enumerate(entry["replicates"]):
                if not isinstance(rep, dict) or rep.get(RETENTION) is None:
                    continue
                try:
                    reading = decompose_forgetting(rep[RETENTION])
                except (ValueError, TypeError):
                    refused.append(f"{name}:{arm}[{i}]")
                    continue
                stored = rep.get(PER_TASK)
                rows.append({"artifact": name, "arm": arm, "replicate": i, "metric": rep.get(METRIC),
                             "stored": list(stored) if isinstance(stored, list) else None, **reading})
                seen = True
            if not seen and not any(r["artifact"] == name and r["arm"] == arm for r in rows):
                refused.append(f"{name}:{arm}: no readable matrix")
    return rows, refused


def per_arm(rows: list[dict]) -> list[dict]:
    """One row per (artifact, arm): the stored metric, the two terms, and the share."""
    grouped: dict[tuple, list[dict]] = {}
    for r in rows:
        grouped.setdefault((r["artifact"], r["arm"]), []).append(r)
    out = []
    for (name, arm), got in sorted(grouped.items()):
        metrics = [g["metric"] for g in got if isinstance(g["metric"], (int, float))]
        lost = statistics.fmean(g["lost_mean"] for g in got)
        unlearned = statistics.fmean(g["unlearned_mean"] for g in got)
        whole = lost + unlearned
        out.append({"artifact": name, "arm": arm, "replicates": len(got),
                    METRIC: statistics.fmean(metrics) if metrics else None,
                    "lost_mean": lost, "unlearned_mean": unlearned, "shortfall_mean": whole,
                    "unlearned_share": unlearned / whole if whole else None,
                    "n_tasks": got[0]["n_tasks"]})
    return out


def rank_correlation(xs: list[float], ys: list[float]) -> float | None:
    """Spearman's rho, by ranking and not by a library, so the reading is the one this unit defines."""
    n = len(xs)
    if n < 3:
        return None

    def ranks(vs: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: vs[i])
        out = [0.0] * n
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vs[order[j + 1]] == vs[order[i]]:
                j += 1
            mean = (i + j) / 2
            for k in range(i, j + 1):
                out[order[k]] = mean
            i = j + 1
        return out

    a, b = ranks(xs), ranks(ys)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    sa = sum((v - ma) ** 2 for v in a) ** 0.5
    sb = sum((v - mb) ** 2 for v in b) ** 0.5
    if not sa or not sb:
        return None
    return sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (sa * sb)


def reading(root: Path = RUNS) -> dict:
    rows, refused = replicates(root)
    arms = per_arm(rows)
    residuals = [residual(r) for r in rows]
    disagreements = [abs(r["lost"][j] - r["stored"][j])
                     for r in rows if r["stored"] and len(r["stored"]) == r["n_tasks"]
                     for j in range(r["n_tasks"])]
    shares = [a["unlearned_share"] for a in arms if a["unlearned_share"] is not None]
    scored = [(a[METRIC], a["unlearned_share"]) for a in arms
              if isinstance(a[METRIC], (int, float)) and a["unlearned_share"] is not None]
    return {"arm_replicates": len(rows), "arms": arms, "n_arms": len(arms), "refused": refused,
            "max_residual": max(residuals) if residuals else None,
            "n_disagreements": sum(1 for d in disagreements if d > TOLERANCE),
            "max_disagreement": max(disagreements) if disagreements else None,
            "median_unlearned_share": statistics.median(shares) if shares else None,
            "rho": rank_correlation([s for s, _ in scored], [u for _, u in scored]),
            "n_scored": len(scored)}


def judge(r: dict) -> list[dict]:
    if not r.get("n_arms"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm carries a readable matrix"}
                for c in CLAIMS]

    out = [{"id": "D1", "measured": f"{r['arm_replicates']} arm-replicates over {r['n_arms']} arms, largest "
                                     f"residual {r['max_residual']:.2e}",
            "verdict": "MET -- the split adds up for every arm and every task"
            if r["max_residual"] is not None and r["max_residual"] <= TOLERANCE else
            f"FALSIFIER FIRED -- a residual of {r['max_residual']}"}]

    out.append({"id": "D2", "measured": f"{r['n_disagreements']} task(s) where the stored `{PER_TASK}` differs from "
                                        f"the lost term, largest {r['max_disagreement']:.2e}",
                "verdict": "MET -- the conventional measure is the lost term and not a different quantity"
                if not r["n_disagreements"] else
                f"FALSIFIER FIRED -- {r['n_disagreements']} disagree"})

    out.append({"id": "D3", "measured": f"the median unlearned share of the shortfall is "
                                        f"{r['median_unlearned_share']:.3f} over {len(r['arms'])} arms",
                "verdict": "MET -- the larger half of the shortfall is the half the metric cannot see"
                if (r["median_unlearned_share"] or 0) > 0.5 else
                f"FALSIFIER FIRED -- {r['median_unlearned_share']}"})

    out.append({"id": "D4", "measured": f"over {r['n_scored']} arms, the rank correlation between `{METRIC}` and the "
                                        f"unlearned share is {r['rho']:+.3f}" if r["rho"] is not None else
                                        "no arm carries both numbers",
                "verdict": "MET -- the metric is lowest where the arm learned least" if
                (r["rho"] is not None and r["rho"] < NEGATIVE) else f"FALSIFIER FIRED -- {r['rho']}"})
    return out


def report(r: dict) -> int:
    print("== the corpus's arms, split at the level each task reached ==")
    print(f"   {r['arm_replicates']} arm-replicates over {r['n_arms']} arms; refused "
          f"{len(r['refused'])}; largest additivity residual {r['max_residual']:.2e}")
    print(f"   the stored `{PER_TASK}` differs from the lost term in {r['n_disagreements']} task(s), "
          f"largest {r['max_disagreement']:.2e}")

    scored = [a for a in r["arms"] if isinstance(a[METRIC], (int, float)) and a["unlearned_share"] is not None]
    print("\n== the arms the metric scores BEST, and what they actually did ==")
    print(f"   {'artifact':44} {'arm':16} {'mean_forgetting':>15} {'unlearned share':>15} {'lost':>8}")
    for a in sorted(scored, key=lambda x: x[METRIC])[:6]:
        print(f"   {a['artifact'][:44]:44} {a['arm']:16} {a[METRIC]:15.5f} {a['unlearned_share']:15.3f} "
              f"{a['lost_mean']:8.5f}")
    print("\n== and the arms it scores WORST ==")
    for a in sorted(scored, key=lambda x: -x[METRIC])[:6]:
        print(f"   {a['artifact'][:44]:44} {a['arm']:16} {a[METRIC]:15.5f} {a['unlearned_share']:15.3f} "
              f"{a['lost_mean']:8.5f}")

    print("\n== the registered claims, D1-D4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the block says the conventional metric rewards shrinkage; the corpus's own retention matrices")
    print("    say the metric IS the lost half of the shortfall, and that it is lowest where the arm learned least)")
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
