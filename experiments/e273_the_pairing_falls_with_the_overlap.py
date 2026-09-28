"""E273 -- the pairing's gain falls with the tasks' input overlap, and fails at full overlap.

`e271` censused the corpus's paired correlations and named the two powered rows where the pairing *hurts* -- both on
`e193_r32_overlap075_methods_40reps`, the only configuration in the record whose arms are anti-correlated across
replicates -- and left the question of why to a run. **The corpus already answers most of it**, because `e193` ran the
same configuration at three input overlaps and `e153` ran a fourth at full overlap:

| `input_overlap` | artifact | n |
|---|---|---|
| 0.25 | `e193_r32_overlap025_methods_40reps` | 40 |
| 0.50 | `e193_r32_overlap050_methods_40reps` | 40 |
| 0.75 | `e193_r32_overlap075_methods_40reps` | 40 |
| 1.00 | `e153_r32_overlap1_methods_40reps` | 40 |

The first three differ in **nothing but the overlap** (checked field by field before anything is compared), so the
arm-to-arm correlation -- the number that licenses the paired sem -- can be read as a function of it. The mechanism the
pattern suggests is interference: with more overlapping task inputs the two arms compete for the same representations,
so a seed that helps the treatment hurts its control and their fluctuations stop agreeing.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **X1 -- the correlation falls monotonically over the three controlled points.** On accuracy **+0.257, +0.101,
  -0.063** and on forgetting **+0.265, +0.164, -0.047**. **Falsifier**: any step that rises.
- **X2 -- and the pairing's gain follows it into reverse.** The unpaired-over-paired sem ratio falls **1.160, 1.055,
  0.970**, so at the tightest of the three the paired figure is **looser** than the unpaired one. **Falsifier**: the
  ratio at the highest of the three is one or more.
- **X3 -- but the relation fails at the fourth point.** At full overlap (`e153`, otherwise the same configuration) the
  correlation is **+0.131** on accuracy and **+0.139** on forgetting -- **above** the 0.75 point and back near the 0.50
  point -- so "more overlap means less sharing" holds across the controlled range and not across the whole one.
  **Falsifier**: the full-overlap correlation below the 0.75 one.
- **X4 -- and the sign is the replicate set's and not an outlier's.** Dropping any one of the forty replicates leaves
  the correlation on the same side of zero at all six matrices; the closest call is **+0.004**, one replicate away
  from turning the 0.75 accuracy reading positive. **Falsifier**: a leave-one-out value with the opposite sign.

**What it cannot do**: the fourth point is not a controlled comparison -- `e153` carries two more arms beside the three
these matrices use, and nothing here shows that an arm's own training is unaffected by the arm list, which is the
assumption the comparison rests on; the overlap axis has four points and one of them is out of the controlled range,
so the shape is a direction and not a law; a correlation at forty replicates has a standard error near 0.16, which is
of the order of the *whole* fall from 0.25 to 0.75, so the monotone pattern is three draws that could in principle
have ordered themselves; the mechanism is a candidate -- interference between overlapping inputs -- and not a
measurement of it; and no run is made, so nothing here varies the overlap at a fixed arm list.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: The overlap axis, controlled (the first three) and the fourth point.
RUNS = (("0.25", "runs/e193_r32_overlap025_methods_40reps.json"),
        ("0.50", "runs/e193_r32_overlap050_methods_40reps.json"),
        ("0.75", "runs/e193_r32_overlap075_methods_40reps.json"),
        ("1.00", "runs/e153_r32_overlap1_methods_40reps.json"))
METRICS = ("final_accuracy", "mean_forgetting")
PAIR = ("ewc-block", "ewc-block-rand")
#: The fields the four runs may differ in; everything else has to match for the axis to be the overlap.
FREE = ("json_out", "input_overlap", "methods", "repeats")
CLAIMS = (
    ("X1", "the correlation falls monotonically over the three controlled points",
     "The arm-to-arm correlation of the three runs that differ only in the overlap falls at every step, on both "
     "metrics",
     "falsifier: any step that rises"),
    ("X2", "and the pairing's gain follows it into reverse",
     "The unpaired-over-paired sem ratio falls with the overlap and is below one at the highest of the three",
     "falsifier: a ratio at or above one"),
    ("X3", "but the relation fails at the fourth point",
     "The full-overlap run's correlation is above the 0.75 point on both metrics",
     "falsifier: it is below the 0.75 one"),
    ("X4", "and the sign is the replicate set's and not an outlier's",
     "Dropping any single replicate leaves every correlation on the same side of zero",
     "falsifier: a leave-one-out value with the opposite sign"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((v - mx) ** 2 for v in xs) / (n - 1))
    sy = math.sqrt(sum((v - my) ** 2 for v in ys) / (n - 1))
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / ((n - 1) * sx * sy)


def config_diff(a: dict, b: dict) -> list[tuple]:
    keys = sorted(set(a["config"]) | set(b["config"]))
    return [(k, a["config"].get(k), b["config"].get(k)) for k in keys
            if a["config"].get(k) != b["config"].get(k) and k not in FREE]


def reading(d: dict, metric: str) -> dict:
    a = [r[metric] for r in d["methods"][PAIR[0]]["replicates"]]
    b = [r[metric] for r in d["methods"][PAIR[1]]["replicates"]]
    full = pearson(a, b)
    loo = [pearson(a[:i] + a[i + 1:], b[:i] + b[i + 1:]) for i in range(len(a))]
    mp = d["matched_pair"][metric]
    return {"n": len(a), "corr": full, "ratio": mp["sem_unpaired"] / mp["sem_paired"],
            "loo_min": min(loo), "loo_max": max(loo),
            "loo_flips": any((x < 0) != (full < 0) for x in loo),
            "closest_to_zero": min(abs(x) for x in loo), "delta": mp["delta"]}


def readings() -> dict:
    out = {}
    for overlap, path in RUNS:
        d = load(path)
        if d is None or "naive" not in (d.get("methods") or {}):
            continue
        out[overlap] = {"artifact": Path(path).name,
                        "diffs": config_diff(d, load(RUNS[1][1])) if d is not None else [],
                        "metrics": {m: reading(d, m) for m in METRICS if m in (d.get("matched_pair") or {})}}
    return out


def controlled(rows: dict) -> list[str]:
    return [o for o in ("0.25", "0.50", "0.75") if o in rows]


def judge(rows: dict) -> list[dict]:
    out: list[dict] = []
    if len(rows) < 3:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the overlap axis is not on disk"} for c in CLAIMS]
    axis = controlled(rows)

    lines, ok1 = [], True
    for metric in METRICS:
        vals = [rows[o]["metrics"][metric]["corr"] for o in axis if metric in rows[o]["metrics"]]
        if len(vals) < 3:
            ok1 = False
            continue
        if any(vals[i + 1] >= vals[i] for i in range(len(vals) - 1)):
            ok1 = False
        lines.append(metric + ": " + ", ".join(f"{v:+.3f}" for v in vals))
    out.append({"id": "X1", "measured": "over the overlaps " + ", ".join(axis) + " -- " + "; ".join(lines),
                "verdict": "MET -- the correlation falls at every step on both metrics" if ok1 else
                           "FALSIFIER FIRED -- a step rises"})

    lines, ok2 = [], True
    for metric in METRICS:
        vals = [rows[o]["metrics"][metric]["ratio"] for o in axis if metric in rows[o]["metrics"]]
        if len(vals) < 3 or vals[-1] >= 1.0:
            ok2 = False
        lines.append(metric + ": " + ", ".join(f"{v:.3f}" for v in vals))
    out.append({"id": "X2", "measured": "; ".join(lines) + " (unpaired over paired sem)",
                "verdict": "MET -- the gain reverses into a loss at the tightest of the three" if ok2 else
                           "FALSIFIER FIRED -- the ratio does not fall below one"})

    if "1.00" not in rows:
        out.append({"id": "X3", "measured": "the full-overlap run is absent",
                    "verdict": "REFUSED -- no fourth point to read"})
    else:
        lines, ok3 = [], True
        for metric in METRICS:
            if metric not in rows["1.00"]["metrics"] or metric not in rows["0.75"]["metrics"]:
                continue
            hi, mid = rows["1.00"]["metrics"][metric]["corr"], rows["0.75"]["metrics"][metric]["corr"]
            if hi <= mid:
                ok3 = False
            lines.append(f"{metric}: 0.75 reads {mid:+.3f} and 1.00 reads {hi:+.3f}")
        out.append({"id": "X3", "measured": "; ".join(lines),
                    "verdict": "MET -- the relation fails at the fourth point" if ok3 else
                               "FALSIFIER FIRED -- the full-overlap point is below the 0.75 one"})

    flips = [(o, metric) for o in rows for metric in rows[o]["metrics"] if rows[o]["metrics"][metric]["loo_flips"]]
    closest = min((rows[o]["metrics"][metric]["closest_to_zero"], o, metric)
                  for o in rows for metric in rows[o]["metrics"])
    out.append({"id": "X4", "measured": f"{len(flips)} of the "
                                        f"{sum(len(rows[o]['metrics']) for o in rows)} matrices change sign when one "
                                        f"replicate is dropped; the closest call is {closest[0]:+.3f} at overlap "
                                        f"{closest[1]} on {closest[2]}",
                "verdict": "MET -- no single replicate carries the sign" if not flips else
                           f"FALSIFIER FIRED -- {flips}"})
    return out


def report(rows: dict) -> int:
    print("== the overlap axis, and what the four runs differ in ==")
    for overlap, r in sorted(rows.items()):
        print(f"   overlap {overlap}  {r['artifact']:44} fields differing from the 0.50 run: {r['diffs'] or 'none'}")

    print("\n== the arm-to-arm correlation and the pairing's gain, by overlap ==")
    print(f"   {'overlap':>8} {'metric':16} {'corr':>7} {'unpaired/paired':>16} {'delta':>9} "
          f"{'LOO range':>18}")
    for overlap, r in sorted(rows.items()):
        for metric, m in sorted(r["metrics"].items()):
            print(f"   {overlap:>8} {metric:16} {m['corr']:+7.3f} {m['ratio']:16.3f} {m['delta']:+9.4f} "
                  f"[{m['loo_min']:+.3f}, {m['loo_max']:+.3f}]")

    print("\n== the registered claims, X1-X4 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the correlation that licenses the paired sem is a function of the task geometry -- it falls as the "
          "tasks' inputs")
    print("    overlap and turns negative before the overlap is full, where it rises again)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = readings()
    if not rows:
        raise SystemExit("need the overlap axis -- it is what this unit reads")
    if args.json_out:
        write_json(args.json_out, {"axis": [list(r) for r in RUNS], "runs": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
