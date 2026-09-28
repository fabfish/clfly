"""E265 -- the arm ladder over the whole corpus: the ordering `e264` read does not reproduce, and "the same
configuration" is not the same experiment.

`e264` asked the corpus's third arm what the shared component is and answered: at the largest budget the two arms
that differ only in their basis correlate about 2.3x as much as either does with the naive arm, so what the pairing
exploits is the penalty's machinery rather than the task. That reading rests on **one artifact** (`e178`, cs 300 with
144 replicates) -- which its own text says ("at the largest budget of each metric"), but which a reader would take as
the corpus's ordering.

**Thirty-five artifacts carry all three pairs of that contrast, and the corpus has more arms than the three the line
uses.** Five arms exist in the record -- `naive`, `ewc` (a penalty with no basis), `ewc-block`, `ewc-block-rand` and
`replay` -- and `e263`/`e264`'s device, the item ceiling a pair's correlation is measured against, is only meaningful
where an arm's test-set floor sits **below** its own replicate spread. Both together turn the single-artifact reading
into a census with a filter, and the ordering does not survive either.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **W1 -- a whole configuration can sit inside its own test-set floor.** In `e140_r32_methods_frozenbias_40reps`
  **all five** arms' test-set variance exceeds their own replicate spread on accuracy (variance fractions 1.10 to
  2.09), so no item ceiling can be formed for any pair and the run cannot separate the test set from the training at
  all; its **plastic twin** at the same cell, arms and replicate count has four of five below 1 (0.36 to 0.60).
  **Falsifier**: every arm of the frozen-bias run below 1.
- **W2 -- the basis pair's lead does not reproduce.** Of the **50 readable** (artifact, metric) matrices, the pair the
  line's contrast is about is the highest of the three in **21**, the middle in 14 and the lowest in 15 -- **42%**
  against a 33% chance baseline. **Falsifier**: the basis pair highest in more than half the readable matrices.
- **W3 -- and the corpus's own replications do not fix the ordering either.** Four configurations were run more than
  once; in the `fb8` group, whose five artifacts share **every** configuration field, the basis pair's rank takes
  1, 0, 1, 0 and 0. **Falsifier**: one rank for every repeat of a configuration.
- **W4 -- because "the same configuration" is not the same experiment.** In that group only two runs are bit-identical
  (`e102_rate_fb8_rerun` against `e102_rate_fb8_rerun2`) while the other three each carry different replicate lists,
  with runtimes spanning **963 s to 3487 s**, and **no artifact records the thread count** their filenames name.
  **Falsifier**: every run of a shared configuration agreeing bit for bit.

**What it cannot do**: the census is over artifacts that carry the three pairs, so a configuration that never ran all
three arms is invisible to W2; the rank of a pair is a coarse statistic and this module reports it rather than a
distribution of the correlations; the five arms are not equally represented (only 26 artifacts carry `ewc`), so the
corpus cannot separate the penalty form from the basis by arm counts alone; and W4 identifies the *effect* of an
unrecorded setting, not the setting -- the thread counts are inferred from filenames and from the runtimes, which is
what the artifacts offer.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

#: The three pairs of the line's contrast, in the order the reports print them.
PAIRS = (("ewc-block", "ewc-block-rand"), ("naive", "ewc-block"), ("naive", "ewc-block-rand"))
METRICS = ("final_accuracy", "mean_forgetting")
#: The configuration whose five runs share every field, for W3 and W4.
GROUP = "fb8"
FROZEN = "e140_r32_methods_frozenbias_40reps.json"
PLASTIC = "e140_r32_methods_plastic_40reps.json"
CLAIMS = (
    ("W1", "a whole configuration can sit inside its own test-set floor",
     "Every arm of the frozen-bias run has its test-set variance above its own replicate spread on accuracy, while "
     "its plastic twin has all but one below",
     "falsifier: every arm of the frozen-bias run below 1"),
    ("W2", "the basis pair's lead does not reproduce over the corpus",
     "Among the readable matrices the pair the contrast is about is the highest of the three in at most half",
     "falsifier: the basis pair highest in more than half the readable matrices"),
    ("W3", "and the corpus's own replications do not fix the ordering",
     "In the configuration whose runs share every field, the basis pair's rank is not the same for every repeat",
     "falsifier: one rank for every repeat of a configuration"),
    ("W4", "because the same configuration is not the same experiment",
     "In that group only two runs are bit-identical while the others carry different replicate lists, with runtimes "
     "spanning a factor of three, and none records the thread count its name claims",
     "falsifier: every run of a shared configuration agreeing bit for bit"),
)


def variance(xs: list[float]) -> float:
    n = len(xs)
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - 1)


def covariance(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def config_key(d: dict) -> tuple:
    """Every configuration field but the output path, which is a name and not a setting."""
    return tuple(sorted((k, str(v)) for k, v in d["config"].items() if k != "json_out"))


def scan(root: Path = Path("runs")) -> list[dict]:
    """Every artifact carrying all three pairs of the contrast, with its matrices, readabilities and identities."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        meth = (d or {}).get("methods")
        ev = (d or {}).get("evaluation_noise") or {}
        if not isinstance(meth, dict) or "config" not in d:
            continue
        arms = [a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates")]
        if not all(x in arms for pair in PAIRS for x in pair):
            continue
        n = len(meth["naive"]["replicates"])
        if n < 3:
            continue
        row = {"artifact": Path(path).name, "n": n, "arms": sorted(arms), "key": config_key(d),
               "seconds": duration_seconds(d), "matrices": {}}
        for metric in METRICS:
            vals = {a: [r[metric] for r in meth[a]["replicates"]] for a in arms}
            v = {a: variance(vals[a]) for a in arms}
            b = {a: ((ev.get(a) or {}).get("binomial_sem", 0.0)) ** 2 for a in arms}
            # an arm that does not move at all has no correlation with anything, and no ceiling either: the pair is
            # reported as not readable rather than as a division by zero
            live = all(v[a] > 0 for a in arms)
            corr = {p: (covariance(vals[p[0]], vals[p[1]]) / math.sqrt(v[p[0]] * v[p[1]]) if live else float("nan"))
                    for p in PAIRS}
            ceiling = {p: (math.sqrt(b[p[0]] * b[p[1]]) / math.sqrt(v[p[0]] * v[p[1]]) if live else float("nan"))
                       for p in PAIRS}
            row["matrices"][metric] = {"corr": corr, "ceiling": ceiling,
                                       "excess": {p: corr[p] - ceiling[p] for p in PAIRS},
                                       "fraction": {a: (b[a] / v[a] if v[a] > 0 else float("inf")) for a in arms},
                                       "readable": live and all(b[a] < v[a] for a in arms)}
        row["replicates"] = {a: meth[a]["replicates"] for a in arms}
        out.append(row)
    return out


def repeat_groups(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[r["key"]].append(r)
    return {k: v for k, v in groups.items() if len(v) > 1}


def judge(rows: list[dict], groups: dict) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact carries the three pairs"} for c in CLAIMS]

    frozen = next((r for r in rows if r["artifact"] == FROZEN), None)
    plastic = next((r for r in rows if r["artifact"] == PLASTIC), None)
    if frozen is None or plastic is None:
        out.append({"id": "W1", "measured": f"{FROZEN}, {PLASTIC}",
                    "verdict": "REFUSED -- the frozen-bias pair is not both on disk"})
    else:
        ff = frozen["matrices"]["final_accuracy"]["fraction"]
        pf = plastic["matrices"]["final_accuracy"]["fraction"]
        ok = all(v >= 1.0 for v in ff.values()) and sum(1 for v in pf.values() if v < 1.0) >= len(pf) - 1
        out.append({"id": "W1", "measured": f"frozen bias: " + ", ".join(f"{a} {v:.2f}" for a, v in ff.items())
                    + f" (all over the floor: {all(v >= 1.0 for v in ff.values())}); plastic: "
                    + ", ".join(f"{a} {v:.2f}" for a, v in pf.items()),
                    "verdict": "MET -- the frozen-bias configuration's whole spread is inside its test-set floor"
                    if ok else "FALSIFIER FIRED -- an arm of it sits below its floor"})

    readable, ranks = [], []
    for r in rows:
        for metric, m in r["matrices"].items():
            if not m["readable"]:
                continue
            order = sorted(PAIRS, key=lambda p: -m["corr"][p])
            readable.append((r["artifact"], metric))
            ranks.append(order.index(PAIRS[0]))
    top, mid, low = ranks.count(0), ranks.count(1), ranks.count(2)
    n_m = len(rows) * len(METRICS)
    out.append({"id": "W2", "measured": f"{len(rows)} artifacts carry the three pairs, {n_m} matrices, "
                                        f"{len(ranks)} readable; the basis pair is highest in {top}, middle in {mid} "
                                        f"and lowest in {low} of them ({100 * top / len(ranks):.0f}% against a third "
                                        f"by chance)",
                "verdict": "MET -- the basis pair leads in at most half the readable matrices"
                if top <= len(ranks) / 2 else "FALSIFIER FIRED -- it leads in more than half"})

    multi = {k: v for k, v in groups.items() if len(v) > 1}
    unstable, fb8_ranks = [], None
    for key, rs in multi.items():
        for metric in METRICS:
            readable = [r for r in rs if r["matrices"][metric]["readable"]]
            if len(readable) < 2:
                continue
            per = []
            for r in readable:
                order = sorted(PAIRS, key=lambda p: -r["matrices"][metric]["corr"][p])
                per.append((r["artifact"], order.index(PAIRS[0])))
            if len({rank for _, rank in per}) > 1:
                unstable.append((metric, per))
                if all(GROUP in a for a, _ in per):
                    fb8_ranks = per
    measured = (f"{len(multi)} configurations were run more than once; {len(unstable)} (configuration, metric) pairs "
                f"among them disagree about the basis pair's rank across repeats")
    if fb8_ranks:
        measured += "; the fb8 group gives " + ", ".join(f"rank {rank} for {a}" for a, rank in fb8_ranks)
    out.append({"id": "W3", "measured": measured,
                "verdict": "MET -- a configuration's repeats do not agree on the ordering"
                if unstable else "FALSIFIER FIRED -- every repeated configuration agrees"})

    fb8 = next((rs for rs in multi.values() if all(GROUP in r["artifact"] for r in rs)), None)
    if fb8 is None:
        out.append({"id": "W4", "measured": f"no group of {GROUP} runs", "verdict": "REFUSED -- the group is absent"})
    else:
        same = []
        for i, x in enumerate(fb8):
            for y in fb8[i + 1:]:
                if x["replicates"] == y["replicates"]:
                    same.append((x["artifact"], y["artifact"]))
        secs = [r["seconds"] for r in fb8 if r["seconds"]]
        # the registered falsifier is EVERY run agreeing bit for bit; zero agreement is the same finding
        # one step further, and the count of identical pairs is what the measured string carries
        ok = len(same) < len(fb8) * (len(fb8) - 1) / 2
        out.append({"id": "W4", "measured": f"{len(fb8)} runs share every configuration field; bit-identical pairs: "
                                            f"{same}; runtimes " + ", ".join(f"{r['artifact']} {r['seconds']:.0f} s"
                                                                            for r in sorted(fb8, key=lambda r: r["seconds"] or 0)),
                    "verdict": "MET -- one configuration, several different experiments" if ok else
                               "FALSIFIER FIRED -- the runs of one configuration agree bit for bit"})
    return out


def report(rows: list[dict], groups: dict) -> int:
    print("== every artifact that carries all three pairs of the contrast ==")
    print(f"   {'artifact':44} {'n':>4} {'arms':>5} {'readable':>9} {'basis':>7} {'n-E':>7} {'n-R':>7} {'fraction':>8}")
    for r in sorted(rows, key=lambda r: (r["n"], r["artifact"])):
        m = r["matrices"]["final_accuracy"]
        print(f"   {r['artifact'][:44]:44} {r['n']:4d} {len(r['arms']):5d} "
              f"{str(m['readable']):>9} {m['corr'][PAIRS[0]]:+7.3f} {m['corr'][PAIRS[1]]:+7.3f} "
              f"{m['corr'][PAIRS[2]]:+7.3f} {max(m['fraction'].values()):8.2f}")

    print("\n== the same, on the forgetting metric ==")
    for r in sorted(rows, key=lambda r: (r["n"], r["artifact"])):
        m = r["matrices"]["mean_forgetting"]
        print(f"   {r['artifact'][:44]:44} {r['n']:4d} {str(m['readable']):>9} "
              f"{m['corr'][PAIRS[0]]:+7.3f} {m['corr'][PAIRS[1]]:+7.3f} {m['corr'][PAIRS[2]]:+7.3f} "
              f"{max(m['fraction'].values()):8.2f}")

    print("\n== the arm names the corpus uses ==")
    tally = defaultdict(int)
    for r in rows:
        for a in r["arms"]:
            tally[a] += 1
    print("   " + ", ".join(f"{a} in {n} artifacts" for a, n in sorted(tally.items())))

    print("\n== configurations the corpus ran more than once ==")
    for key, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print(f"   {len(rs)} runs: {[r['artifact'] for r in rs]}")

    print("\n== the registered claims, W1-W4 ==")
    j = judge(rows, groups)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the item ceiling of e263 and e264 is a bound only where an arm's test-set floor sits below its own")
    print("    spread, and the corpus is a collection of configurations rather than one experiment repeated)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = scan(args.runs)
    if not rows:
        raise SystemExit("need artifacts carrying all three pairs -- they are what this census is over")
    groups = repeat_groups(rows)
    if args.json_out:
        def keyed(obj):
            """The matrices carry tuple keys at several depths, and JSON can only hold strings."""
            if isinstance(obj, dict):
                return {("/".join(k) if isinstance(k, tuple) else k): keyed(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [keyed(v) for v in obj]
            return obj

        write_json(args.json_out, {"pairs": [list(p) for p in PAIRS], "metrics": list(METRICS),
                                   "artifacts": [{**{k: v for k, v in r.items() if k not in ("replicates",
                                                                                            "matrices")},
                                                  "matrices": keyed(r["matrices"])} for r in rows],
                                   "repeat_groups": {str(len(v)): [r["artifact"] for r in v] for v in groups.values()},
                                   "claims": judge(rows, groups)})
        print(f"wrote {args.json_out}")
    return report(rows, groups)


if __name__ == "__main__":
    sys.exit(main())
