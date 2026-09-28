"""E267 -- the test set the benchmark would need: `evaluation_noise`'s own terms, turned into a size.

The benchmark measures every arm's accuracy on the same **144** held-out decisions (three tasks of 48), prints the
binomial floor of that measurement beside each arm's own run-to-run spread, and says in its own note that the test-set
part is *removable*: the floor falls as `sqrt(p(1-p)/n_eval)` and enlarging the suite costs task generation rather
than training. What it never prints is **how large the suite would have to be** for a given configuration to see its
own spread at all -- and `e265` found a configuration where it cannot, with every arm's floor above its own spread.

The two numbers the block already holds fix the answer, so this is computable for every artifact in the corpus with no
run at all: if the floor is `f = variance_fraction` of the arm's own variance then the same floor is reached at
`n_eval * f`, so the suite a configuration would need is `n_eval` times the fraction it is read at. The census is
restricted to **method-comparison artifacts** -- one carrying `naive` and at least one other arm -- because an
artifact with a single arm, or a probe, has no method contrast whose resolvability this prices.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **S1 -- an arm inside its own test-set floor is not an edge case.** At least **a fifth** of the corpus's
  method-comparison matrices have at least one arm whose test-set floor is at or above its own replicate spread, so
  the readability precondition `e265` applied to the item ceiling is a property of the record and not of one run.
  **Falsifier**: under a fifth.
- **S2 -- but a whole configuration inside it is rare, and those are the ones that cannot see themselves.** Three of
  the corpus's matrices have **every** arm inside its floor, and they are the configurations whose run-to-run spread
  is invisible to the benchmark at that budget. **Falsifier**: five or more, or none.
- **S3 -- and the requirement is a multiple of the suite in use, bounded and computable from the block alone.** For
  those three the implied suite is **165, 300 and 1096** items against the 144 in use -- 1.1x to **7.6x** -- so the
  largest requirement is a suite six times the current one and not an unbounded ask. **Falsifier**: any requirement
  above 20x the suite in use.

**The fix is a task-suite regeneration and not a retraining**, which is the direction the benchmark's own note calls
cheap: the held-out samples come from the propagator over the connectome, so a suite of 1096 items is task-generation
time and not the 40 hours `e259` priced for a re-run of the `side` rung. Nothing here measures that cost, and it is
reported rather than claimed.

**What it cannot do**: the fraction is the model's own split of each arm's variance and inherits its assumption that
the held-out decisions are independent, which `e8` says is a signal when a fraction exceeds 100%; `n_eval * f` is the
size at which the floor *equals* the spread, so a configuration would want more than that to resolve anything above
it; the census is over artifacts that record an `evaluation_noise` block, so a run without one is invisible rather
than fine; the methods filter is by the arm names the corpus uses, so a differently-named control is invisible; and
nothing here enlarges a suite or checks that a larger one is generated the same way.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

METRICS = ("final_accuracy", "mean_forgetting")
#: A method comparison is an artifact carrying the baseline and at least one method beside it.
BASELINE = "naive"
CLAIMS = (
    ("S1", "an arm inside its own test-set floor is not an edge case",
     "At least a fifth of the corpus's method-comparison matrices have an arm whose test-set floor is at or above "
     "its own replicate spread",
     "falsifier: under a fifth"),
    ("S2", "but a whole configuration inside it is rare, and those cannot see themselves",
     "Between one and four matrices have every arm inside its own floor",
     "falsifier: none, or five or more"),
    ("S3", "and the requirement is a bounded multiple of the suite in use",
     "The implied suite for those matrices is above the 144 in use and below twenty times it",
     "falsifier: any requirement above 20x the suite in use"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def variance(xs: list[float]) -> float:
    n = len(xs)
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - 1)


def arms_of(d: dict) -> list[str]:
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return [a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates")]


def census(root: Path = Path("runs")) -> list[dict]:
    """Every method-comparison artifact's per-metric per-arm floor, as a fraction of its own spread and in items."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        ev = (d or {}).get("evaluation_noise") or {}
        arms = arms_of(d or {})
        if not isinstance(ev, dict) or "n_eval" not in ev or BASELINE not in arms or len(arms) < 2:
            continue
        n = len(d["methods"][arms[0]]["replicates"])
        for metric in METRICS:
            fractions = {}
            for a in arms:
                xs = [r[metric] for r in d["methods"][a]["replicates"]]
                e = (ev.get(a) or {}).get("binomial_sem")
                if len(xs) < 2 or e is None:
                    fractions = {}
                    break
                v = variance(xs)
                if v <= 0:
                    fractions = {}
                    break
                fractions[a] = e ** 2 / v
            if fractions:
                worst = max(fractions.values())
                out.append({"artifact": Path(path).name, "metric": metric, "n": n, "n_eval": ev["n_eval"],
                            "arms": sorted(fractions), "fraction": fractions, "worst": worst,
                            "worst_arm": max(fractions, key=lambda a: fractions[a]),
                            "all_over": all(f >= 1.0 for f in fractions.values()),
                            "any_over": any(f >= 1.0 for f in fractions.values()),
                            "needed": ev["n_eval"] * worst})
    return out


def judge(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no method-comparison artifact on disk"}
                for c in CLAIMS]

    share = sum(1 for r in rows if r["any_over"]) / len(rows)
    out.append({"id": "S1", "measured": f"{sum(1 for r in rows if r['any_over'])} of {len(rows)} matrices have an arm "
                                        f"at or above its own floor ({100 * share:.0f}%)",
                "verdict": "MET -- the precondition bites on a fifth of the record or more" if share >= 0.2 else
                           "FALSIFIER FIRED -- under a fifth of the matrices are affected"})

    whole = [r for r in rows if r["all_over"]]
    names = sorted(f"{r['artifact']}/{r['metric'][:3]}" for r in whole)
    out.append({"id": "S2", "measured": f"{len(whole)} matrices have EVERY arm inside its own floor"
                                        + (f": {'; '.join(names[:4])}" if whole else ""),
                "verdict": "MET -- a whole configuration inside its own floor is rare and named" if 1 <= len(whole) <= 4
                else f"FALSIFIER FIRED -- {len(whole)} such matrices"})

    if whole:
        needs = [r["needed"] for r in whole]
        n_eval = {r["n_eval"] for r in whole}
        suite = max(n_eval)
        ok = all(n > suite for n in needs) and all(n <= 20 * suite for n in needs)
        out.append({"id": "S3", "measured": f"the implied suite is {', '.join(f'{n:.0f}' for n in sorted(needs))} "
                                            f"items against the {suite} in use, i.e. up to "
                                            f"{max(needs) / suite:.1f}x",
                    "verdict": "MET -- the requirement is a bounded multiple of the suite" if ok else
                               "FALSIFIER FIRED -- a requirement is above twenty times the suite"})
    else:
        out.append({"id": "S3", "measured": "", "verdict": "REFUSED -- no configuration needs a larger suite"})
    return out


def report(rows: list[dict]) -> int:
    print("== the method-comparison artifacts and the suite each arm's spread would need ==")
    print(f"   {'artifact':46} {'n':>4} {'metric':>5} {'worst arm':18} {'fraction':>9} {'needs n_eval':>13}")
    for r in sorted(rows, key=lambda r: -r["worst"])[:24]:
        print(f"   {r['artifact'][:46]:46} {r['n']:4d} {r['metric'][:3]:>5} {r['worst_arm'][:18]:18} "
              f"{r['worst']:9.2f} {r['needed']:13.0f}")
    print(f"   ... {len(rows)} matrices in total")

    print("\n== the fractions by replicate count over the whole census ==")
    by_n: dict = {}
    for r in rows:
        by_n.setdefault(r["n"], []).append(r["worst"])
    for n in sorted(by_n):
        v = sorted(by_n[n])
        print(f"   n = {n:4d}  matrices {len(v):3d}  worst {v[-1]:7.2f}  median {v[len(v) // 2]:5.2f}  "
              f"any arm over its floor: {sum(1 for x in v if x >= 1.0)}")

    whole = [r for r in rows if r["all_over"]]
    print(f"\n== configurations that cannot see their own spread ({len(whole)}) ==")
    for r in sorted(whole, key=lambda r: -r["needed"]):
        print(f"   {r['artifact'][:48]:48} {r['metric'][:3]}  n = {r['n']:3d}  worst {r['worst']:6.2f}  "
              f"needs {r['needed']:7.0f} items against {r['n_eval']} in use ({r['needed'] / r['n_eval']:.1f}x)")

    print("\n== the suite the corpus reads at ==")
    print("   " + ", ".join(f"{n} items in {sum(1 for r in rows if r['n_eval'] == n)} matrices"
                            for n in sorted({r["n_eval"] for r in rows})))

    print("\n== the registered claims, S1-S3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the block already holds every term of the answer, so the size a configuration needs is arithmetic")
    print("    on the artifact -- and the suite is generated by the propagator, so enlarging it is task-generation")
    print("    time rather than another training run)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = census(args.runs)
    if not rows:
        raise SystemExit("need method-comparison artifacts with an evaluation_noise block")
    if args.json_out:
        write_json(args.json_out, {"metrics": list(METRICS),
                                   "matrices": [{**r, "fraction": r["fraction"]} for r in rows],
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
