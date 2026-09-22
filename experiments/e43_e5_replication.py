"""E43 — is `runs/e5_anisotropy.json` the live output of the current code, or a stale file?

`e41` established that the artifact `2026-09-22-e5-anisotropy-axis.md` cites does not contain the
numbers that finding publishes: **7 of 42 cells disagree, every one of them in a realized-error
column** (`gap:EWC` 4, `bio-rand` 3) while all 28 geometry cells reproduce. It could not decide
*which* side was stale, because `runs/` is gitignored with no history, and it recorded that as a
limit.

That limit is answerable by replication rather than by history: several other runs in this repository
use `e5`'s exact configuration (cs = 800, real topology, the same seven `kappa` values, seeds from
0). If one of them reproduces the artifact cell for cell, then the artifact is the current code's
output and the published table is what is stale — and if none does, the artifact is the stale thing.

    python -m experiments.e43_e5_replication
    python -m experiments.e43_e5_replication --log /tmp/e37.log

A log can be compared too, which matters because a long run writes its JSON only when it finishes and
its progress lines are already enough to settle this.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

#: The reference: the artifact the `e5` finding cites.
REFERENCE = "runs/e5_anisotropy.json"

#: Other `e5` outputs that may use the same configuration.  `e37`'s real cs=800 arm and `e42`'s
#: reseed are the two that do.
CANDIDATES = [
    "runs/e37_kappa_real_cs800.json",
    "runs/e42_e5_reseed.json",
]

#: Progress-line pattern from `e5`'s report.
LINE = re.compile(
    r"seed (\d+) kappa=(\S+)\s+flatten=([\d.]+) effrank=\s*([\d.]+).*gap_ewc=([+-][\d.]+)")

#: Field tolerances: the artifact stores full precision, so a genuine replication should agree to
#: far inside these.  They are the same numbers `e41` used to call a published cell reproduced.
TOL = {"flattening": 5e-5, "effective_rank": 5e-2, "gap_ewc": 5e-5, "excess_ewc": 5e-5}

#: The progress log prints 4 decimals for `flatten` and `gap_ewc` and 1 for the effective rank, so
#: its own rounding reaches 5e-5, 5e-5 and 0.05 respectively -- i.e. exactly `TOL`.  Comparing a log
#: against a full-precision artifact must therefore allow twice the print half-unit, or a perfect
#: replication fails on rounding alone (it did, at ratio 0.99).
LOG_TOL = {"flattening": 1e-4, "effective_rank": 0.11, "gap_ewc": 2e-4}


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def by_key(entry):
    return {(p["seed"], float(p["kappa"])): p for p in entry["points"]}


def compare(ref, other, name: str, fields=("flattening", "effective_rank", "gap_ewc")) -> tuple[int, int, list]:
    a, b = by_key(ref), by_key(other)
    shared = sorted(set(a) & set(b))
    worst = []
    rows = 0
    for k in shared:
        rows += 1
        for f in fields:
            if f not in a[k] or f not in b[k]:
                continue
            d = abs(a[k][f] - b[k][f])
            tol = TOL.get(f, 5e-5)
            if d > tol:
                worst.append((k[0], k[1], f, a[k][f], b[k][f], d / tol))
    return len(shared), rows - len({(w[0], w[1]) for w in worst}), worst


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference", default=REFERENCE)
    ap.add_argument("--log", default=None, help="an e5 progress log to compare as well")
    ap.add_argument("--json-out", default="runs/e43_e5_replication.json")
    args = ap.parse_args()

    ref = load(args.reference)
    if ref is None:
        print(f"reference {args.reference} is absent (runs/ is gitignored); nothing to do")
        return

    print("=" * 96)
    print("IS THE ARTIFACT THE LIVE OUTPUT OF THE CURRENT CODE?")
    print("=" * 96)
    print(f"   reference: {args.reference}")
    print(f"   config   : cs={ref['config']['circuit_size']} support={ref['config']['support']} "
          f"kappas={ref['config']['kappas']}")
    print(f"   points   : {len(ref['points'])} over seeds "
          f"{sorted({p['seed'] for p in ref['points']})}")
    print("\n   a run that uses the same configuration and reproduces these cells settles it:")
    print(f"\n   {'candidate':<34}{'shared':>8}{'cells agree':>13}{'worst deviation / tol':>24}")
    out: dict = {"reference": args.reference, "candidates": {}}

    verdicts = []
    for path in CANDIDATES:
        other = load(path)
        if other is None:
            print(f"   {path:<34}{'absent':>8}")
            continue
        shared, agree, bad = compare(ref, other, path)
        worst = max((w[5] for w in bad), default=0.0)
        print(f"   {path:<34}{shared:>8}{agree:>13}{worst:>24.2f}")
        for w in bad[:5]:
            print(f"        seed {w[0]} kappa={w[1]:g} {w[2]}: reference {w[3]:.6f} "
                  f"vs candidate {w[4]:.6f}")
        out["candidates"][path] = dict(shared=shared, agreeing_rows=agree, worst_ratio=worst,
                                       mismatches=[dict(seed=w[0], kappa=w[1], field=w[2],
                                                        reference=w[3], candidate=w[4])
                                                   for w in bad])
        verdicts.append((path, shared, agree, worst))

    if args.log:
        lp = Path(args.log)
        if not lp.exists():
            print(f"\n   log {args.log} absent")
        else:
            key = by_key(ref)
            rows = agreed = 0
            worst_ratio = 0.0
            for line in lp.read_text(errors="replace").splitlines():
                m = LINE.search(line)
                if not m:
                    continue
                s, k = int(m.group(1)), float(m.group(2))
                q = key.get((s, k))
                if q is None:
                    continue
                rows += 1
                ratios = [abs(float(m.group(3)) - q["flattening"]) / LOG_TOL["flattening"],
                          abs(float(m.group(4)) - q["effective_rank"]) / LOG_TOL["effective_rank"],
                          abs(float(m.group(5)) - q["gap_ewc"]) / LOG_TOL["gap_ewc"]]
                worst_ratio = max(worst_ratio, max(ratios))
                if max(ratios) <= 1:
                    agreed += 1
            print(f"\n   progress log {args.log}: {agreed} of {rows} (seed, kappa) points agree "
                  f"with the reference")
            print(f"     worst deviation = {worst_ratio:.2f} x tolerance")
            out["log"] = {"path": str(lp), "rows": rows, "agreeing": agreed,
                          "worst_ratio": worst_ratio,
                          "tolerance_basis": "the log prints 4 decimals, so LOG_TOL applies"}

    if verdicts:
        best = max(verdicts, key=lambda v: v[2] / max(v[1], 1))
        print(f"\n   VERDICT: {best[0]} agrees on {best[2]}/{best[1]} shared points.")
        if best[2] == best[1] and best[1] >= 7:
            print("   The reference artifact IS the current code's output, so the published table's")
            print("   discrepant cells are the stale thing -- they are not recoverable from the")
            print("   artifact and must not be quoted alongside it.")
        else:
            print("   The reference artifact is NOT reproduced by a same-configuration run, so it")
            print("   is itself stale and neither it nor the published table can be quoted.")
    elif out.get("log", {}).get("agreeing", 0) >= 7 and out["log"]["worst_ratio"] <= 1.0:
        lg = out["log"]
        print(f"\n   VERDICT: the in-progress same-configuration run agrees on {lg['agreeing']}"
              f" of {lg['rows']} (seed, kappa)")
        print(f"   points, worst deviation {lg['worst_ratio']:.2f} x tolerance.  That is a"
              f" partial run, but its agreement")
        print("   settles the direction: the reference artifact IS the current code's output, so"
              " the published")
        print("   table's discrepant cells are the stale thing.  Re-run once the JSON lands to"
              " confirm on all 21.")
    else:
        print("\n   VERDICT: not settled -- no same-configuration run has disagreed or agreed on"
              " enough points.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
