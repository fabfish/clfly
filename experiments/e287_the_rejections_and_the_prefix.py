"""E287 -- the rejections and the prefix: what `e286`'s pairing rule actually discarded, and two corrections.

`e286` built its sample-swap census on two rules and reported the gap between them in one sentence: the weak rule
admitted 28 pairs, the training fields kept 3, and *"the twenty-five it rejects are the corpus's epoch changes"*. That
sentence was written from the counts and never from the rejections. This unit reads the rejections, and it finds two
things wrong with the sentence and one with the rule.

  * **what the rejections differ in.** Each rejected pair is compared key by key, and the mismatch is not usually an
    epoch: it is `repeats`.
  * **what the prefix is.** The runner seeds its replicates `seed0 + 100 * r`, so a run at five replicates and a run
    at forty share their **first** replicates by construction. `e286` refused a pair whose replicate lists had
    different lengths, which is not the same as refusing one whose training differs -- so pairing on the shared
    prefix is licensed, and it turns three of the rejections into sample swaps.
  * **and what those three can carry.** Pairing on the prefix is legitimate and the pairs are weak: at five
    replicates a variance ratio's 95% interval is so wide that it contains 1 for any ratio a factor of ten either
    way, so the three new pairs cannot answer the question the census was built to ask -- and the run launched beside
    this unit is what does answer it.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **Y1 -- the rejections are a replicate-count mismatch and not an epoch.** `repeats` is the config key that differs
  most often across the rejected candidates, and it accounts for most of them. **Falsifier**: fewer than half.
- **Y2 -- and the prefix is a licensed pairing that adds three sample swaps.** Pairing the rejections on their shared
  replicate prefix turns at least one of them into a sample swap. **Falsifier**: none of them.
- **Y3 -- and the new pairs cannot carry the test.** Every comparison the three prefix pairs supply has a 95% interval
  for its variance ratio that contains 1, because the prefix is five replicates. **Falsifier**: a comparison whose
  interval excludes 1.

**The correction this unit applies to `e286`'s prose**: its census stands at three full-prefix sample swaps and its
X1 claim is unaffected, but the clause naming the twenty-five as "the corpus's epoch changes" is wrong; the rejections
are typed below, and the finding carries the corrected sentence.

**What it cannot do.** *The prefix pairing assumes the seeds line up*, which the runner's scheme
(`seed0 + 100 * r`) licenses and nothing in the artifacts records directly, so a runner that chose replicate seeds
another way would be mispaired here. *Five replicates* put about 50% on an sd ratio, so Y3 is a statement about
resolution and not about the size of the effect -- the prefix pairs are consistent with the fall `e286` measured and
they do not corroborate it. *The rejection keys are compared over the keys both sides record*, so a pair that differs
in a key only one side records is typed by its other keys or by nothing. *And the three prefix pairs are three
configurations' worth of five replicates*, so nothing here generalises beyond them.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from scipy import stats

from clfly.bench.artifacts import write_json
from experiments import e286_the_fall_is_not_the_samples_size as e286

#: The key `e286`'s prose called an epoch, and the proportion of rejections it has to account for.
REPEATS = "repeats"
MAJORITY = 0.5
#: The confidence the interval in Y3 is taken at, and the dof a prefix of a given length implies.
ALPHA = 0.05
CLAIMS = (
    ("Y1", "the rejections are a replicate-count mismatch and not an epoch",
     f"`{REPEATS}` is the most common differing key across the rejected candidates and accounts for most of them",
     f"falsifier: {REPEATS} in fewer than half of them"),
    ("Y2", "and the prefix is a licensed pairing that adds three sample swaps",
     "Pairing the rejections on their shared replicate prefix turns at least one of them into a sample swap",
     "falsifier: none of them"),
    ("Y3", "and the new pairs cannot carry the test",
     "Every comparison the prefix pairs supply has a 95% interval for its variance ratio that contains one",
     "falsifier: a comparison whose interval excludes one"),
)


def differing_keys(da: dict, db: dict) -> dict:
    """The config keys that differ, split by whether both sides record them."""
    ca = {k: v for k, v in (da.get("config") or {}).items() if k not in e286.IGNORE}
    cb = {k: v for k, v in (db.get("config") or {}).items() if k not in e286.IGNORE}
    return {"recorded": sorted(k for k in set(ca) & set(cb) if ca[k] != cb[k]),
            "unrecorded": sorted(set(ca) ^ set(cb))}


def prefix_identical(da: dict, db: dict) -> dict:
    """Per shared arm: whether the training fields agree over the SHARED PREFIX of the two replicate lists."""
    out = {}
    for m in sorted(set(e286.arms(da)) & set(e286.arms(db))):
        ra, rb = da["methods"][m]["replicates"], db["methods"][m]["replicates"]
        n = min(len(ra), len(rb))
        if n < 2:
            out[m] = {"prefix": n, "identical": False}
            continue
        ok = all(all(x.get(f) == y.get(f) for f in e286.TRAIN_FIELDS) for x, y in zip(ra[:n], rb[:n]))
        out[m] = {"prefix": n, "identical": bool(ok), "len_old": len(ra), "len_new": len(rb)}
    return out


def f_interval(ratio: float, df: int, alpha: float = ALPHA) -> tuple[float, float]:
    """The interval a variance ratio of `ratio` sits in at `alpha`, given `df` degrees of freedom on each side."""
    crit = float(stats.f.ppf(1 - alpha / 2, df, df))
    return ratio / crit, ratio * crit


def replicates_for(ratio: float, alpha: float = ALPHA, cap: int = 2000) -> int | None:
    """The replicates per side a variance ratio of `ratio` needs for its interval to exclude one."""
    for df in range(2, cap):
        if float(stats.f.ppf(1 - alpha / 2, df, df)) <= 1 / ratio:
            return df + 1
    return None


def reading(minimum_replicates: int = 5) -> dict:
    cands = e286.candidates(minimum_replicates=minimum_replicates)
    swaps = [c for c in cands if c["swap"]]
    rejected = [c for c in cands if not c["swap"]]

    keys: Counter = Counter()
    typed = []
    for c in rejected:
        da, db = e286.load(c["old"]), e286.load(c["new"])
        d = differing_keys(da, db)
        for k in d["recorded"]:
            keys[k] += 1
        for k in d["unrecorded"]:
            keys[f"(unrecorded) {k}"] += 1
        typed.append({"old": Path(c["old"]).name, "new": Path(c["new"]).name,
                      "size_ratio": c["size_ratio"], "replicates": c["replicates"], **d})

    prefixes = []
    for c in rejected:
        da, db = e286.load(c["old"]), e286.load(c["new"])
        pre = prefix_identical(da, db)
        if not pre or not all(t["identical"] for t in pre.values()):
            continue
        n = min(t["prefix"] for t in pre.values())
        rows = []
        for m in c["arms"]:
            for metric in e286.METRICS:
                xa = [r[metric] for r in da["methods"][m]["replicates"]][:n]
                xb = [r[metric] for r in db["methods"][m]["replicates"]][:n]
                if len(xa) < 2 or len(xb) < 2 or statistics.stdev(xa) == 0:
                    continue
                ratio = (statistics.stdev(xb) / statistics.stdev(xa)) ** 2
                lo, hi = f_interval(ratio, n - 1)
                rows.append({"pair": f"{Path(c['old']).name} -> {Path(c['new']).name}", "arm": m, "metric": metric,
                             "prefix": n, "size_ratio": c["size_ratio"],
                             "variance_ratio": ratio, "sd_ratio": ratio ** 0.5,
                             "interval": [lo, hi], "resolved": not (lo <= 1 <= hi)})
        prefixes.append({"old": c["old"], "new": c["new"], "n_old": c["n_old"], "n_new": c["n_new"],
                         "size_ratio": c["size_ratio"], "prefix": n, "comparisons": rows})
    return {"n_candidates": len(cands), "n_swaps": len(swaps), "n_rejected": len(rejected),
            "swaps": [{"old": Path(c["old"]).name, "new": Path(c["new"]).name, "size_ratio": c["size_ratio"],
                       "replicates": c["replicates"]} for c in swaps],
            "rejection_keys": dict(keys.most_common()), "rejections": typed,
            "prefix_pairs": prefixes,
            "prefix_comparisons": [r for p in prefixes for r in p["comparisons"]],
            "f_critical_df4": float(stats.f.ppf(1 - ALPHA / 2, 4, 4)),
            "needed_for_the_measured_fall": replicates_for(0.64)}


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    if not r or not r.get("rejection_keys"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no rejected candidate to read"} for c in CLAIMS]

    keys = r["rejection_keys"]
    n_rep = keys.get(REPEATS, 0)
    top = max(keys, key=lambda k: (keys[k], k))
    share = n_rep / max(r["n_rejected"], 1)
    out.append({"id": "Y1", "measured": f"{r['n_rejected']} rejections: {REPEATS} in {n_rep} "
                                        f"({100 * share:.0f}%), the most common key is {top}; "
                                        f"the rest of the table is {dict(list(keys.items())[1:6])}",
                "verdict": "MET -- the rejections are a replicate-count mismatch, not an epoch" if n_rep >= MAJORITY * r["n_rejected"]
                else f"FALSIFIER FIRED -- {REPEATS} in {n_rep} of {r['n_rejected']}"})

    n_new = len(r["prefix_pairs"])
    added = [p for p in r["prefix_pairs"]]
    out.append({"id": "Y2", "measured": f"{r['n_swaps']} sample swaps on the full lists and {n_new} more on the shared "
                                        f"prefix ({[Path(p['old']).name for p in added]}), so the census is "
                                        f"{r['n_swaps'] + n_new}",
                "verdict": "MET -- the prefix pairing adds sample swaps the full-list rule discarded" if n_new else
                           "FALSIFIER FIRED -- no rejection becomes a sample swap on its prefix"})

    rows = r["prefix_comparisons"]
    unresolved = [x for x in rows if not x["resolved"]]
    out.append({"id": "Y3", "measured": f"{len(unresolved)} of {len(rows)} prefix comparisons have an interval "
                                        f"containing one (sd ratios "
                                        f"{min(x['sd_ratio'] for x in rows):.3f} to "
                                        f"{max(x['sd_ratio'] for x in rows):.3f} at {rows[0]['prefix']} replicates, "
                                        f"where the 95% factor for 4 dof is {r['f_critical_df4']:.1f})",
                "verdict": "MET -- five replicates cannot resolve the fall, so these pairs cannot carry the test"
                if len(unresolved) == len(rows) and rows else
                f"FALSIFIER FIRED -- {len(rows) - len(unresolved)} resolved"})
    return out


def report(r: dict) -> int:
    print("== the census `e286` ran, and what it discarded ==")
    print(f"   candidates {r['n_candidates']}; sample swaps {r['n_swaps']}; rejected {r['n_rejected']}")
    print(f"   what the rejections differ in: {r['rejection_keys']}")

    print("\n== pairing on the shared prefix ==")
    for p in r["prefix_pairs"]:
        print(f"   x{p['size_ratio']:<6g} {Path(p['old']).name:40} -> {Path(p['new']).name:32} "
              f"n_eval {p['n_old']}->{p['n_new']} prefix {p['prefix']}")
        for c in p["comparisons"]:
            print(f"        {c['arm'] + '/' + c['metric']:30} sd ratio {c['sd_ratio']:6.3f}  "
                  f"95% interval {[round(v, 3) for v in c['interval']]}  resolved {c['resolved']}")

    print("\n== what the prefixes cannot do ==")
    print(f"   the 95% factor for a variance ratio at 4 degrees of freedom is {r['f_critical_df4']:.2f}, so a ratio")
    print(f"   is resolved only outside 1/{r['f_critical_df4']:.2f} to {r['f_critical_df4']:.2f}")
    print(f"   the fall `e286` measured is a variance ratio near 0.64, which needs {r['needed_for_the_measured_fall']} "
          f"replicates per side to resolve")
    print("   -> that is what the run launched beside this unit is for: the same configuration and the same models at")
    print("      a 1440-item suite, so the scaling question is asked within one configuration instead of across three")

    print("\n== the registered claims, Y1-Y3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the pairing rule's rejections are typed, the prefix is licensed and weak, and the sentence `e286`")
    print("    wrote about them is corrected in the finding rather than left standing)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-replicates", type=int, default=5)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    r = reading(args.min_replicates)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
