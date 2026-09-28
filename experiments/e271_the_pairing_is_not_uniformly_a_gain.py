"""E271 -- the pairing is not uniformly a gain: 9 of 64 paired contrasts are negative, and it hurts where it is read.

The whole network line quotes its central contrast **paired**: `paired_contrast` returns `sem_paired` beside the
unpaired figure, on the strength of the arm-to-arm correlation of the replicates, and `e263`, `e264` and `e265` spent
three fires on what that correlation means on three artifacts. **Nobody has censused it**, and every artifact that ran
both EWC arms carries the number in its own `matched_pair` block -- `corr`, the two sems and their ratio -- so the
census is a read of the register rather than a new measurement.

Thirty-two artifacts carry the block, giving **64** (artifact, metric) rows. Registered, all **confirmatory** and
computed in the exploration that wrote the module:

- **W1 -- the correlation is positive on the median and negative in a seventh of the rows.** Median **+0.302** over
  the 64, and **9 are negative** -- but five of those nine are **one configuration counted four times** (the `fb8`
  family at **-0.210**, plus its second metric), so the negative cases are **six distinct configurations** and not
  nine independent findings. **Falsifier**: fewer than five negative rows.
- **W2 -- at the budgets the register reads, the pairing's median gain is 1.18x and it is bounded.** Over the 24 rows
  at sixteen replicates or more the unpaired-over-paired sem ratio is median **1.180**, minimum **0.970** and maximum
  **1.645** -- so the pairing never buys more than 65% and never costs more than 3%. **Falsifier**: a median outside
  1.1 to 1.3.
- **W3 -- and an unpaired report is not uniformly conservative.** In **2 of the 24** powered rows the paired sem is
  *wider* than the unpaired one (0.970 and 0.978, both on the same configuration), so the register's practice of
  quoting the paired figure is wrong by a few per cent in one twelfth of the powered record, in the direction nobody
  checks. **Falsifier**: no powered row with a ratio below 1.

**What it cannot do**: the census reads the block the runner computes, so an artifact that ran a single arm, or that
predates `paired_contrast`, is invisible rather than neutral; the ratio is a ratio of sems and says nothing about
whether either figure is right for the question; `corr` is computed from the same replicates as the contrast, so a
seed that moves both arms is counted once as agreement; the six distinct negative configurations are named but not
explained, and the cause of a negative arm-to-arm correlation is a question for a run and not for this census; and the
negative cases are four-fifths one family, so the census reports a rate over rows and states the row-to-configuration
ratio rather than resolving it.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json

METRICS = ("final_accuracy", "mean_forgetting")
#: The budget at and above which the line reads its contrasts.
POWERED = 16
CLAIMS = (
    ("W1", "the correlation is positive on the median and negative in a seventh of the rows",
     "At least five of the 64 paired rows are negative, and the census states how many distinct configurations carry "
     "them",
     "falsifier: fewer than five negative rows"),
    ("W2", "and at the budgets the register reads the pairing's median gain is 1.18x",
     "Over the rows at sixteen replicates or more the unpaired-over-paired ratio has a median between 1.1 and 1.3",
     "falsifier: a median outside that band"),
    ("W3", "and an unpaired report is not uniformly conservative",
     "At least one powered row has a paired sem wider than its unpaired one",
     "falsifier: every powered row has a ratio of 1 or more"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def census(root: Path = Path("runs")) -> list[dict]:
    """Every (artifact, metric) row the corpus's own `matched_pair` blocks carry."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        mp = (d or {}).get("matched_pair")
        if not isinstance(mp, dict):
            continue
        for metric, v in mp.items():
            if not isinstance(v, dict) or "corr" not in v:
                continue
            unpaired, paired = v.get("sem_unpaired"), v.get("sem_paired")
            out.append({"artifact": Path(path).name, "metric": metric, "n": v.get("n"), "corr": v["corr"],
                        "sem_unpaired": unpaired, "sem_paired": paired,
                        "ratio": (unpaired / paired) if unpaired and paired else None,
                        "key": tuple(sorted((k, str(val)) for k, val in ((d.get("config") or {})).items()
                                            if k != "json_out"))})
    return out


def configurations(rows: list[dict]) -> dict:
    """One representative artifact per configuration key: the same configuration written twice is one case."""
    out: dict = {}
    for r in rows:
        # a key read back from the artifact is a list of pairs, which is not hashable until it is tupled
        key = r["key"]
        if isinstance(key, list):
            key = tuple(tuple(x) if isinstance(x, list) else x for x in key)
        out.setdefault(key, []).append(r["artifact"])
    return out


def judge(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact carries a matched_pair block"}
                for c in CLAIMS]

    neg = [r for r in rows if r["corr"] <= 0]
    distinct = configurations(neg)
    repeated = {next(iter(v)): len(v) for v in distinct.values() if len(v) > 1}
    out.append({"id": "W1", "measured": f"{len(rows)} paired rows over {len({r['artifact'] for r in rows})} "
                                        f"artifacts; median correlation {sorted(r['corr'] for r in rows)[len(rows) // 2]:+.3f}; "
                                        f"{len(neg)} rows negative, carried by {len(distinct)} distinct "
                                        f"CONFIGURATIONS"
                                        + (f", of which one supplies {max(repeated.values())} rows "
                                           f"({max(repeated, key=lambda k: repeated[k])})" if repeated else ""),
                "verdict": "MET -- the correlation is positive on the median and negative often enough to matter"
                if len(neg) >= 5 else f"FALSIFIER FIRED -- only {len(neg)} rows are negative"})

    powered = [r for r in rows if r["n"] and r["n"] >= POWERED and r["ratio"]]
    if not powered:
        out.append({"id": "W2", "measured": "no powered row", "verdict": "REFUSED -- no row at that budget"})
        out.append({"id": "W3", "measured": "no powered row", "verdict": "REFUSED -- no row at that budget"})
        return out
    ratios = sorted(r["ratio"] for r in powered)
    med = ratios[len(ratios) // 2]
    out.append({"id": "W2", "measured": f"{len(powered)} rows at {POWERED} replicates or more: the unpaired-over-paired "
                                        f"sem ratio runs {ratios[0]:.3f} to {ratios[-1]:.3f} with a median of {med:.3f}",
                "verdict": "MET -- the gain is bounded and its median is 1.18x" if 1.1 <= med <= 1.3 else
                           f"FALSIFIER FIRED -- the median is {med:.3f}"})

    worse = [r for r in powered if r["ratio"] < 1.0]
    out.append({"id": "W3", "measured": f"{len(worse)} of {len(powered)} powered rows have a paired sem wider than "
                                        f"the unpaired one: "
                                        + "; ".join(f"{r['artifact']} {r['metric'][:3]} ratio {r['ratio']:.3f}"
                                                    for r in sorted(worse, key=lambda r: r["ratio"])),
                "verdict": "MET -- an unpaired report is not uniformly conservative" if worse else
                           "FALSIFIER FIRED -- every powered row is at or above 1"})
    return out


def report(rows: list[dict]) -> int:
    print("== the corpus's own paired correlations ==")
    print(f"   {len(rows)} (artifact, metric) rows over {len({r['artifact'] for r in rows})} artifacts")
    by_n: dict = defaultdict(list)
    for r in rows:
        by_n[r["n"]].append(r["corr"])
    for n in sorted(by_n, key=lambda x: (x is None, x)):
        v = sorted(by_n[n])
        print(f"   n = {str(n):>4}  rows {len(v):3d}  median corr {v[len(v) // 2]:+.3f}  min {v[0]:+.3f}  "
              f"negative {sum(1 for x in v if x <= 0)}")

    print("\n== the negative rows, with the configuration they belong to ==")
    for r in sorted((r for r in rows if r["corr"] <= 0), key=lambda r: r["corr"]):
        print(f"   n = {str(r['n']):>4}  corr {r['corr']:+.3f}  unpaired/paired "
              f"{('%.3f' % r['ratio']) if r['ratio'] else 'n/a'}  {r['artifact'][:42]:42} {r['metric'][:3]}")

    powered = sorted((r for r in rows if r["n"] and r["n"] >= POWERED and r["ratio"]), key=lambda r: r["ratio"])
    print(f"\n== the powered rows ({len(powered)}), thinnest gain first ==")
    for r in powered[:8]:
        print(f"   ratio {r['ratio']:.3f}  corr {r['corr']:+.3f}  n = {r['n']:4d}  {r['artifact'][:42]:42} "
              f"{r['metric'][:3]}")

    print("\n== the registered claims, W1-W3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the line quotes its contrast paired everywhere on the strength of this correlation; the census says")
    print("    the median gain is real, bounded at 65%, and negative in a seventh of the rows)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = census(args.runs)
    if not rows:
        raise SystemExit("need artifacts carrying a matched_pair block -- they are what this census reads")
    if args.json_out:
        write_json(args.json_out, {"metrics": list(METRICS), "powered_at": POWERED, "rows": rows,
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
