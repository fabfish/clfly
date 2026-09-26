"""E262 -- the replicate order is not a variable: the one clustered sign sequence is what a scan of six gives for free.

`e261` closed on an open lead rather than a claim: of the six paired readings the C2b line reports, one
(`cell_class` on forgetting) has a sign sequence a runs test calls clustered -- four runs in sixteen replicates,
p = 0.019 uncorrected, with a Spearman correlation against replicate index of -0.508. The tempting reading is that
the sixteen replicates are not exchangeable, so a null on that rung is an average of two regimes rather than an
absence. **This module tests that reading against the null it needs, and it does not survive.**

Three things are measured, all from artifacts on disk, and the first two need a null this module builds rather than
reads. The null is the right one for the question: hold each sequence's own counts of positive, negative and tied
replicates fixed, permute them, and ask **what the best of six such sequences looks like** -- because the lead was
found by looking at six sequences and taking the most extreme.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **N1 -- the lead is inside its own null.** The smallest of the six runs-test p-values is **0.0187**, and the 5th
  percentile of the best-of-six null is **0.0103**: **12.6%** of exchangeable corpora produce a reading at least that
  clustered. **Falsifier**: the observed minimum below the null's 5th percentile.
- **N2 -- and the nominal 0.05 scan costs a fifth.** Under the same null, the best of six lands below 0.05 in
  **22.4%** of draws, so "one of these six sequences is significant at 0.05" carries no weight at all. **Falsifier**:
  the simulated rate below 5%.
- **N3 -- the two order statistics do not agree about which reading is most ordered.** The most clustered sequence's
  own half-split is **-1.35 sigma** while the largest half-split in the corpus is **+1.88 sigma** on a sequence whose
  runs-test p is 0.782, and no half-split reaches 2 sigma. **Falsifier**: a half-split at or above 2 sigma, or the
  same reading extremal on both statistics.
- **N4 -- and there is no order to recover anyway.** Across **309** artifacts carrying replicate lists -- **5366**
  replicate records and thirteen distinct per-replicate keys -- **not one record carries a seed or a draw**, so for
  every paired reading the index is the only order there is. **Falsifier**: a replicate record with a seed-shaped key.
- **N5 -- the replicate values are a deterministic function of the seeds.** The corpus's one rerun of a configuration
  (`e153` against `e159`) reproduces the 40-replicate by three-arm replicate lists **bit for bit** while its wall
  clock differs by **21%** (14616 s against 11553 s) and its own machine-calibration constant differs by 1.5x.
  **Falsifier**: any difference between the two replicate lists.

N5 is what makes the whole question answerable rather than merely quiet: if the values are deterministic in the seeds,
then the only randomness a paired sem scales over is the seed sequence, a within-process drift enters **both arms** of
a pair and cancels in the difference, and an index trend in the difference can only be noise.

**What it cannot do**: the runs test is a normal approximation on 15 or 16 values, so a sequence with four runs is at
the edge where that approximation is honest but not exact; the null permutes signs within each reading and so holds
that reading's own counts fixed, which is the right null for "is this sequence ordered" and not a null over the
effects themselves; the six readings are not independent (both rungs share the naive arm and the cross-rung is built
from the two rungs), so the best-of-six null is conservative -- it treats them as six free sequences; and nothing here
re-opens the question of whether the effects are real, which is `e76`'s and `e259`'s subject.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import duration_seconds, write_json

RUNGS = {"side": "runs/e60_side_lam0.1_16reps.json", "cell_class": "runs/e46_c2b_powered.json"}
METRICS = ("final_accuracy", "mean_forgetting")
#: The rerun pair, for N5: one configuration run twice.
RERUN = ("runs/e153_r32_overlap1_methods_40reps.json", "runs/e159_r32_overlap1_methods_rerun.json")
B = 4000
SEED = 20260926
CLAIMS = (
    ("N1", "the clustered sign sequence is inside its own null",
     "The smallest of the six runs-test p-values is at or above the 5th percentile of the best-of-six null",
     "falsifier: the observed minimum below the null's 5th percentile"),
    ("N2", "and a nominal 0.05 scan of six costs about a fifth",
     "Under exchangeability the best of six sequences lands below 0.05 in more than 5% of draws",
     "falsifier: the simulated rate below 5%"),
    ("N3", "the two order statistics disagree about which reading is most ordered",
     "No half-split reaches 2 sigma, and the most clustered sequence is not the one with the largest half-split",
     "falsifier: a half-split at or above 2 sigma, or the same reading extremal on both"),
    ("N4", "there is no per-replicate order to recover",
     "No replicate record in the corpus carries a seed or a draw, so the index is the only order",
     "falsifier: a replicate record with a seed-shaped key"),
    ("N5", "the replicate values are a deterministic function of the seeds",
     "The corpus's one rerun of a configuration reproduces its replicate lists bit for bit while its wall clock "
     "differs by a fifth",
     "falsifier: any difference between the two replicate lists"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def deltas(path, metric: str) -> list[float]:
    """One run's matched pair per replicate: the biological basis minus its size-matched random one."""
    d = load(path)
    blk = d["methods"]
    return [a[metric] - b[metric] for a, b in zip(blk["ewc-block"]["replicates"],
                                                 blk["ewc-block-rand"]["replicates"])]


def sequences() -> dict[str, list[float]]:
    """The six paired readings the C2b line reports, each as its per-replicate differences."""
    out = {}
    for rung, path in RUNGS.items():
        for metric in METRICS:
            out[f"{rung}/{metric}"] = deltas(path, metric)
    for metric in METRICS:
        out[f"cross/{metric}"] = [a - b for a, b in zip(deltas(RUNGS["side"], metric),
                                                       deltas(RUNGS["cell_class"], metric))]
    return out


def signs_of(dl: list[float]) -> str:
    return "".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl)


def runs_test(signs: str) -> dict:
    """The two-sided runs test on a sign sequence, ties dropped, by the normal approximation."""
    s = [c for c in signs if c != "0"]
    n = len(s)
    runs = 1 + sum(1 for a, b in zip(s, s[1:]) if a != b)
    n1, n2 = s.count("+"), s.count("-")
    if n1 == 0 or n2 == 0 or n < 2:
        return {"runs": runs, "n": n, "expected": float("nan"), "z": float("nan"), "p": float("nan")}
    expected = 2 * n1 * n2 / n + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n * n * (n - 1))
    z = (runs - expected) / math.sqrt(var) if var > 0 else float("nan")
    return {"runs": runs, "n": n, "expected": expected, "z": z,
            "p": float(math.erfc(abs(z) / math.sqrt(2))) if var > 0 else float("nan")}


def half_split_z(dl: list[float]) -> float:
    """The last eight replicates' mean minus the first eight's, in units of the difference's null sd."""
    d = np.asarray(dl, dtype=float)
    half = d.size // 2
    sd = float(d.std(ddof=1))
    return float((d[half:].mean() - d[:half].mean()) / (sd / math.sqrt(half) * math.sqrt(2.0)))


def index_rho(dl: list[float]) -> float:
    """Spearman correlation between replicate index and the paired difference, ties averaged."""
    d = np.asarray(dl, dtype=float)

    def ranks(v):
        order = np.argsort(v, kind="stable")
        r = np.empty(v.size, dtype=float)
        r[order] = np.arange(v.size, dtype=float)
        for value in np.unique(v):
            m = v == value
            if m.sum() > 1:
                r[m] = r[m].mean()
        return r

    x, y = ranks(np.arange(1.0, d.size + 1)), ranks(d)
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(((x - x.mean()) * (y - y.mean())).mean() / (x.std() * y.std()))


def best_of_six_null(seqs: dict[str, list[float]], draws: int = B, seed: int = SEED) -> np.ndarray:
    """The smallest runs-test p over six sequences, under permutation of each sequence's own signs."""
    rng = np.random.default_rng(seed)
    masks, plusses = {}, {}
    for name, dl in seqs.items():
        s = signs_of(dl)
        masks[name] = [i for i, c in enumerate(s) if c != "0"]
        plusses[name] = s.count("+")
    out = np.empty(draws)
    for b in range(draws):
        ps = []
        for name in seqs:
            idx = masks[name]
            seq = ["0"] * len(signs_of(seqs[name]))
            lab = ["-"] * len(idx)
            for j in rng.permutation(len(idx))[: plusses[name]]:
                lab[j] = "+"
            for pos, c in zip(idx, lab):
                seq[pos] = c
            ps.append(runs_test("".join(seq))["p"])
        out[b] = min(ps)
    return out


def seed_field_census(root: Path = Path("runs")) -> dict:
    """Every artifact in the corpus that carries a replicate list, and whether any record names a seed."""
    artifacts, records, keys, named = 0, 0, set(), []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        meth = (d or {}).get("methods")
        if not isinstance(meth, dict):
            continue
        for name, blk in meth.items():
            reps = blk.get("replicates") if isinstance(blk, dict) else None
            if not isinstance(reps, list) or not reps:
                continue
            artifacts += 1
            for r in reps:
                if not isinstance(r, dict):
                    continue
                records += 1
                keys.update(r)
                if any("seed" in str(k).lower() or "draw" in str(k).lower() for k in r):
                    named.append(Path(path).name)
    return {"artifacts": artifacts, "records": records, "keys": sorted(keys), "named": sorted(set(named))}


def rerun_check() -> dict | None:
    """The one configuration the corpus ran twice: same numbers, different clock?"""
    a, b = load(RERUN[0]), load(RERUN[1])
    if a is None or b is None:
        return None
    reps_same = a["methods"] == b["methods"]
    mp_same = a.get("matched_pair") == b.get("matched_pair")
    ta, tb = duration_seconds(a), duration_seconds(b)
    return {"replicates_identical": reps_same, "matched_pair_identical": mp_same,
            "seconds": [ta, tb], "clock_ratio": (tb / ta) if (ta and tb) else float("nan"),
            "config_differs_only_in_json_out": [k for k in set(a["config"]) | set(b["config"])
                                                if a["config"].get(k) != b["config"].get(k)] == ["json_out"]}


def judge(seqs: dict, rows: dict, null: np.ndarray, census: dict, rerun: dict | None) -> list[dict]:
    out: list[dict] = []
    p_best = min(r["p"] for r in rows.values())
    q05, q01 = (float(np.percentile(null, q)) for q in (5, 1))
    out.append({"id": "N1", "measured": f"the smallest of the six runs-test p-values is {p_best:.4f}; the best-of-six "
                                        f"null over {null.size} draws has median {np.median(null):.4f}, 5th "
                                        f"percentile {q05:.4f} and 1st {q01:.4f}; "
                                        f"P(best of six at or below the observed) = {float((null <= p_best).mean()):.3f}",
                "verdict": "MET -- the clustered sequence is what a scan of six gives for free"
                if p_best >= q05 else "FALSIFIER FIRED -- the observed minimum is below the null's 5th percentile"})

    rate = float((null <= 0.05).mean())
    out.append({"id": "N2", "measured": f"under exchangeability the best of six lands below 0.05 in {rate:.3f} of draws",
                "verdict": "MET -- the nominal scan is not evidence" if rate > 0.05 else
                           "FALSIFIER FIRED -- the simulated rate is at or below 5%"})

    worst_runs = min(rows, key=lambda n: rows[n]["p"])
    worst_half = max(rows, key=lambda n: abs(rows[n]["half_z"]))
    biggest = abs(rows[worst_half]["half_z"])
    out.append({"id": "N3", "measured": f"the most clustered sequence is {worst_runs} (p = {rows[worst_runs]['p']:.3f}, "
                                        f"its own half-split {rows[worst_runs]['half_z']:+.2f} sigma) while the largest "
                                        f"half-split is {worst_half} at {rows[worst_half]['half_z']:+.2f} sigma "
                                        f"(p = {rows[worst_half]['p']:.3f})",
                "verdict": "MET -- the two order statistics disagree and neither reaches 2 sigma"
                if biggest < 2.0 and worst_runs != worst_half else
                "FALSIFIER FIRED -- an order statistic reaches the bar, or both agree"})

    out.append({"id": "N4", "measured": f"{census['artifacts']} artifacts with a replicate list, {census['records']} "
                                        f"replicate records, {len(census['keys'])} distinct keys, "
                                        f"{len(census['named'])} records naming a seed or a draw",
                "verdict": "MET -- the index is the only order the corpus records" if not census["named"] else
                           f"FALSIFIER FIRED -- {census['named'][:3]} name one"})

    if rerun is None:
        out.append({"id": "N5", "measured": f"{RERUN[0]} and {RERUN[1]}",
                    "verdict": "REFUSED -- the rerun pair is not on disk"})
    else:
        ta, tb = rerun["seconds"]
        out.append({"id": "N5", "measured": f"the rerun reproduces the replicate lists bit for bit "
                                            f"({rerun['replicates_identical']}, matched pair "
                                            f"{rerun['matched_pair_identical']}) while the clock runs "
                                            f"{ta:.0f} s against {tb:.0f} s ({rerun['clock_ratio']:.2f}x); the "
                                            f"configurations differ only in `json_out` "
                                            f"({rerun['config_differs_only_in_json_out']})",
                    "verdict": "MET -- the values are a function of the seeds and the timing is not"
                    if rerun["replicates_identical"] and rerun["matched_pair_identical"] and not
                    math.isclose(rerun["clock_ratio"], 1.0, rel_tol=0.05) else
                    "FALSIFIER FIRED -- the rerun is not a rerun, or it did not differ in clock"})
    return out


def report(seqs: dict, rows: dict, null: np.ndarray, census: dict, rerun: dict | None) -> int:
    print("== the six paired readings, by replicate index ==")
    print(f"   {'reading':26} {'signs':18} {'runs (expected)':>16} {'p':>7} {'rho(index)':>11} {'half-split z':>13}")
    for name in sorted(rows, key=lambda n: rows[n]["p"]):
        r = rows[name]
        print(f"   {name:26} {r['signs']:18} {r['runs']:5d} ({r['expected']:5.1f}) {r['p']:7.3f} "
              f"{r['rho']:+11.3f} {r['half_z']:+13.3f}")

    print("\n== the null the lead needs: the best of six exchangeable sequences ==")
    for q in (1, 5, 25, 50, 75, 95):
        print(f"   {q:2d}th percentile of the best-of-six p-value: {np.percentile(null, q):.4f}")
    p_best = min(r["p"] for r in rows.values())
    print(f"   the observed best of six: {p_best:.4f}   ->  "
          f"P(best of six at or below it) = {float((null <= p_best).mean()):.3f}")
    print(f"   P(best of six at or below 0.05) = {float((null <= 0.05).mean()):.3f}")

    print("\n== is there an order to recover at all? ==")
    print(f"   {census['artifacts']} artifacts carry a replicate list, {census['records']} replicate records; "
          f"their keys are {census['keys']}")
    if rerun is not None:
        ta, tb = rerun["seconds"]
        print(f"   the corpus's one rerun: identical replicate lists {rerun['replicates_identical']}, "
              f"identical matched pair {rerun['matched_pair_identical']}, clock {ta:.0f} s to {tb:.0f} s "
              f"({rerun['clock_ratio']:.2f}x)")

    print("\n== the registered claims, N1-N5 ==")
    j = judge(seqs, rows, null, census, rerun)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a lead closed as noise: the reading of the record is that the replicate index carries no signal,")
    print("    not that the effects behind the six readings are absent -- that question is e76's and e259's)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--draws", type=int, default=B)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    seqs = sequences()
    if not seqs:
        raise SystemExit("need the C2b artifacts -- they are what the six readings come from")
    rows = {}
    for name, dl in seqs.items():
        rt = runs_test(signs_of(dl))
        rows[name] = dict(rt, signs=signs_of(dl), rho=index_rho(dl), half_z=half_split_z(dl), n_reps=len(dl))
    null = best_of_six_null(seqs, args.draws)
    census = seed_field_census(args.runs)
    rerun = rerun_check()

    if args.json_out:
        write_json(args.json_out, {"sequences": {n: [float(x) for x in dl] for n, dl in seqs.items()},
                                   "readings": rows, "draws": int(null.size),
                                   "null_percentiles": {str(q): float(np.percentile(null, q))
                                                        for q in (1, 5, 25, 50, 75, 95)},
                                   "best_of_six": float(min(r["p"] for r in rows.values())),
                                   "p_best_at_or_below_observed": float((null <= min(r["p"] for r in rows.values())).mean()),
                                   "p_best_at_or_below_0.05": float((null <= 0.05).mean()),
                                   "seed_census": census, "rerun": rerun,
                                   "claims": judge(seqs, rows, null, census, rerun)})
        print(f"wrote {args.json_out}")
    return report(seqs, rows, null, census, rerun)


if __name__ == "__main__":
    sys.exit(main())
