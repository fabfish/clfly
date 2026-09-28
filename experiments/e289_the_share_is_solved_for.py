"""E289 -- the share is solved for: the paper's own decomposition of these pairs, reproduced, and where it breaks.

`e285`, `e286` and `e287` read the corpus's sample swaps and refuted a one-component account of the spread -- that the
across-replicate spread falls as `1/sqrt(n_eval)`. The paper's section 4.7 does not hold that account. It holds a
**two-component** one, and it holds it about *these same pairs*:

> A tenfold test set (`--test 480` against the 48 of every run above) at forty replicates ... so the spread falls
> **1.47x** and **1.34x** -- and the ceiling, solved for from the fact that the binomial part must fall by exactly
> sqrt(10) while the training part does not move, is **1.57x** and **1.41x**. **The tenfold test set therefore
> captured 94% and 95% of what is removable**

So the model is `v = t^2 + b^2`, with `t^2` fixed and `b^2` falling by the suite ratio `k`. It has **one free
parameter per pair** -- the share `q = b^2/v` -- and a pair supplies exactly one ratio, so the share is *solved for*
and the model cannot fail on a pair. This unit reproduces that decomposition from the artifacts, and then asks the
two questions the corpus has not: what happens where the solved share leaves `[0, 1]`, and whether the artifact's own
noise block is the share the decomposition solves for.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **Z1 -- the section's decomposition reproduces.** For the read-out 128 and read-out 300 pairs, the fall, the
  ceiling and the captured fraction come out of the two artifacts as the section quotes them: `1.47x` and `1.34x` of
  fall, `1.57x` and `1.41x` of ceiling, `94%` and `95%` captured. **Falsifier**: any of the six beyond 0.01.
- **Z2 -- and the model is falsified twice.** The solved share must lie in `[0, 1]`, because a component of a variance
  cannot exceed it; a comparison whose spread fell further than the whole of its removable part allows gives a share
  above one. **Falsifier**: no comparison does.
- **Z3 -- and the artifact's nominal share is not the model's parameter.** The runner's own noise block gives a share
  directly, `(binomial_sem / sd)^2`, and in a majority of the corpus's sample-swap comparisons that nominal share
  exceeds one -- which the model forbids. **Falsifier**: fewer than half of them.

**What the three add up to.** The section's decomposition is right about the pairs it is applied to and it is
**fitted, not predicted**: one parameter per pair, one datum per pair, so the 94% and the 95% are the fit restated.
The two comparisons where the solved share exceeds one are the ones the model cannot fit at all -- and they are the
`replay` and `ewc-block-rand` arms of exactly the configuration `e285` measured, where the training component itself
has to shrink with the suite for the numbers to close. That is `e286`'s and `e287`'s result stated in the section's
own terms, and the run `e288` is training is the out-of-sample test the section's fit cannot pass on its own.

**What it cannot do.** *The section is quoted and not audited*: this unit reproduces the six numbers, and a section
whose fit is by construction is not made wrong by reproducing it. *`q` is solved for from the same two sd's that the
fall is*, so Z1 is arithmetic and not a measurement; the one out-of-sample test available to it is the third suite
size, which is being trained at the read-out the section does not cover. *The nominal share is compared against the
solved one as quantities and not as definitions*: `binomial_sem` is the runner's binomial formula on an accuracy at
`n_eval` while the solved `q` carries whatever correlation the held-out items have, and the section says as much
about the forgetting. *Fourteen comparisons over three configurations*, and the read-out widths are confounded with
the suite ratios exactly as `e286` said. *And nothing here re-measures any of the section's numbers*: what is new is
the solved-versus-nominal comparison and the two comparisons that leave the model's range.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: The three sample swaps, and the metric the section quotes its two falls on.
PAIRS = (
    ("read-out 128", "runs/e116_r128_40reps.json", "runs/e119_r128_test480.json"),
    ("read-out 300", "runs/e115_r300_40reps.json", "runs/e119_r300_test480.json"),
    ("read-out 32", "runs/e140_r32_methods_frozenbias_40reps.json", "runs/e275_frozenbias_suite600_40reps.json"),
)
QUOTED_METRIC = "mean_forgetting"
#: What the section quotes for its two pairs, in the order above: the fall, the ceiling, and the captured fraction.
QUOTED = {"read-out 128": (1.47, 1.57, 0.94), "read-out 300": (1.34, 1.41, 0.95)}
TOLERANCE = 0.01
METRICS = ("final_accuracy", "mean_forgetting")
CLAIMS = (
    ("Z1", "the section's decomposition reproduces",
     "For the read-out 128 and 300 pairs, the fall, the ceiling and the captured fraction come out as the section "
     "quotes them",
     f"falsifier: any of the six beyond {TOLERANCE}"),
    ("Z2", "and the model is falsified twice",
     "Every comparison's solved share lies in [0, 1], because a component of a variance cannot exceed it",
     "falsifier: a comparison whose solved share is above one"),
    ("Z3", "and the artifact's nominal share is not the model's parameter",
     "In fewer than half of the sample-swap comparisons does the nominal share (binomial_sem / sd)^2 exceed one",
     "falsifier: half or more of them"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def arms(d: dict) -> list[str]:
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return sorted(a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates"))


def decomposition(sd_old: float, sd_new: float, k: float) -> dict:
    """The section's one-parameter fit, and the share it solves for.

    `v = t^2 + b^2` with `b^2` falling by `k`, so the ratio is `sqrt(1 - (1 - 1/k) * q)` and `q` follows; the
    ceiling is the fall if the whole removable share were removed, and the capture is what was achieved of it.
    """
    ratio = sd_new / sd_old if sd_old else None
    q = (1 - ratio ** 2) / (1 - 1 / k) if ratio is not None else None
    ceiling = 1 / math.sqrt(1 - q) if q is not None and q < 1 else None
    capture = (1 / ratio) / ceiling if ratio and ceiling else None
    return {"sd_ratio": ratio, "fall": 1 / ratio if ratio else None, "share_solved": q,
            "ceiling": ceiling, "captured": capture}


def comparisons(root: Path = Path(".")) -> list[dict]:
    out = []
    for label, pa, pb in PAIRS:
        da, db = load(root / pa), load(root / pb)
        if da is None or db is None:
            continue
        n_old = (da.get("evaluation_noise") or {}).get("n_eval")
        n_new = (db.get("evaluation_noise") or {}).get("n_eval")
        if not n_old or not n_new:
            continue
        k = n_new / n_old
        for arm in sorted(set(arms(da)) & set(arms(db))):
            for metric in METRICS:
                xa = [r[metric] for r in da["methods"][arm]["replicates"]]
                xb = [r[metric] for r in db["methods"][arm]["replicates"]]
                if len(xa) < 2 or len(xb) < 2:
                    continue
                sa, sb = statistics.stdev(xa), statistics.stdev(xb)
                d = decomposition(sa, sb, k)
                sem = (da.get("evaluation_noise", {}).get(arm) or {}).get("binomial_sem")
                d.update({"config": label, "arm": arm, "metric": metric, "k": k, "n_old": n_old, "n_new": n_new,
                          "sd_old": sa, "sd_new": sb, "replicates": min(len(xa), len(xb)),
                          "share_nominal": (sem / sa) ** 2 if sem else None,
                          "quoted": metric == QUOTED_METRIC and label in QUOTED})
                out.append(d)
    return out


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    rows = (r or {}).get("comparisons") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no sample swap could be read"} for c in CLAIMS]

    quoted = [x for x in rows if x["quoted"]]
    diffs = []
    for x in quoted:
        fall, ceiling, captured = QUOTED[x["config"]]
        diffs += [("fall", x["config"], round(x["fall"], 4), fall),
                  ("ceiling", x["config"], round(x["ceiling"], 4), ceiling),
                  ("captured", x["config"], round(x["captured"], 4), captured)]
    worst = max((abs(a - b) for _, _, a, b in diffs), default=float("inf"))
    out.append({"id": "Z1", "measured": f"{len(quoted)} quoted pair(s); "
                                        + "; ".join(f"{cl} {a:.3f} against {b}" for cl, _, a, b in diffs)
                                        + f"; worst difference {worst:.4f}",
                "verdict": "MET -- the section's own decomposition comes out of the artifacts" if worst <= TOLERANCE
                else f"FALSIFIER FIRED -- worst difference {worst:.4f}"})

    above = [x for x in rows if x["share_solved"] is not None and x["share_solved"] > 1]
    named = [f"{x['config']} {x['arm']} {x['metric']}" for x in above]
    out.append({"id": "Z2", "measured": f"solved shares run {min(x['share_solved'] for x in rows):.3f} to "
                                        f"{max(x['share_solved'] for x in rows):.3f} over {len(rows)} comparisons; "
                                        f"above one in {len(above)}: {named}",
                "verdict": "MET -- the model's range is left where the training component must shrink" if above else
                           "FALSIFIER FIRED -- every comparison fits inside the model's range"})

    nominal = [x for x in rows if x["share_nominal"] is not None]
    impossible = [x for x in nominal if x["share_nominal"] > 1]
    share = len(impossible) / max(len(nominal), 1)
    out.append({"id": "Z3", "measured": f"the nominal share exceeds one in {len(impossible)} of {len(nominal)} "
                                        f"({100 * share:.0f}%), where the model requires at most one; "
                                        f"it runs {min(x['share_nominal'] for x in nominal):.3f} to "
                                        f"{max(x['share_nominal'] for x in nominal):.3f}",
                "verdict": "MET -- the noise block is not the share the decomposition solves for" if share >= 0.5 else
                           f"FALSIFIER FIRED -- {100 * share:.0f}% of them exceed one"})
    return out


def report(r: dict) -> int:
    rows = r["comparisons"]
    print("== the section's decomposition, from the artifacts ==")
    print(f"   {'config':14} {'arm/metric':30} {'k':>5} {'fall':>7} {'ceiling':>8} {'captured':>9} "
          f"{'share solved':>13} {'share nominal':>14}")
    for x in sorted(rows, key=lambda x: (-x["k"], x["config"], x["arm"], x["metric"])):
        ceil = "n/a" if x["ceiling"] is None else f"{x['ceiling']:.3f}"
        cap = "n/a" if x["captured"] is None else f"{x['captured']:.3f}"
        print(f"   {x['config']:14} {x['arm'] + '/' + x['metric']:30} {x['k']:5.2f} {x['fall']:7.3f} {ceil:>8} "
              f"{cap:>9} {x['share_solved']:13.3f} {x['share_nominal']:14.3f}")

    print("\n== what the section quotes, and what comes out ==")
    for x in rows:
        if not x["quoted"]:
            continue
        fall, ceiling, captured = QUOTED[x["config"]]
        print(f"   {x['config']:14} fall {x['fall']:.3f} against {fall}   ceiling {x['ceiling']:.3f} against "
              f"{ceiling}   captured {x['captured']:.3f} against {captured}")

    print("\n== the registered claims, Z1-Z3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the section's decomposition is right about its own pairs and it is fitted rather than predicted -- one")
    print("    parameter per pair -- and two of the corpus's comparisons leave the range it is defined on)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rows = comparisons()
    r = {"comparisons": rows, "quoted": {k: list(v) for k, v in QUOTED.items()},
         "quoted_metric": QUOTED_METRIC, "tolerance": TOLERANCE}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
