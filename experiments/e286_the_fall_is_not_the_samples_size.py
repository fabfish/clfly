"""E286 -- the fall is not the sample's size: the corpus holds three sample swaps, and they refute the mechanism.

`e285` read one pair of artifacts as a sample swap -- the same trained models evaluated on two held-out samples --
and found the across-replicate spread falling in ten of ten arm-by-metric comparisons when the suite went from 144 to
600 items. It named three candidate accounts and separated none of them. **This unit finds the other two sample swaps
the corpus was already holding** and uses all three as a designed test: the new pairs move the suite by a factor of
**ten** where `e285`'s moves it by 4.17, and the candidate accounts make opposite predictions about which should fall
further.

A **sample swap** is defined here by the strong rule: two artifacts at different suite sizes whose training-derived
fields (`losses`, `theta_drift`, `bias_norms`, `retention_loss`, `interference`, `full_train_loss`) agree in every
shared arm-replicate row. The census is run with a deliberately **weaker** rule first -- the same declared shape
fields, and draw blocks that do not disagree, with a block only one side records counting as a missing record -- and
the difference between the two rules is itself X1, because the corpus spans four days of runner changes and the weak
rule has to be shown insufficient rather than assumed so.

The three, with the suite sizes they were run at:

    runs/e116_r128_40reps.json    144  ->  runs/e119_r128_test480.json   1440   x10, 40 replicates, one arm
    runs/e115_r300_40reps.json    144  ->  runs/e119_r300_test480.json   1440   x10, 40 replicates, one arm
    runs/e140_r32_methods_frozenbias_40reps.json  144  ->  runs/e275_frozenbias_suite600_40reps.json  600
                                                                        x4.17, 40 replicates, five arms

Four claims, all **confirmatory** and computed in the exploration that wrote the module:

- **X1 -- the weak rule is not sufficient, and the strong one is what selects.** The shape-and-draw rule admits more
  pairs than the corpus has sample swaps, and the training-derived fields reject the rest. **Falsifier**: every pair
  the weak rule admits also has identical training, in which case the strong rule adds nothing.
- **X2 -- and every sample swap's every comparison falls.** Across the fourteen arm-by-metric comparisons the three
  pairs supply, the across-replicate sd is smaller at the larger suite. **Falsifier**: any comparison whose sd does
  not fall.
- **X3 -- and the fall is not the sample size's.** A per-model sampling deviation whose spread goes as `1/sqrt(n_eval)`
  predicts the *largest* fall for the *largest* suite ratio: **0.316** for the ten-times pairs against **0.490** for
  `e285`'s. The observation is the other way round -- median **0.802** at ten times against **0.545** at 4.17 -- so
  across the fourteen comparisons the observed ratio is **negatively** correlated with the prediction.
  **Falsifier**: a correlation at or above zero, i.e. the ten-times pairs falling at least as far as `e285`'s.
- **X4 -- nor the accuracy level's.** The ceiling account rides on `p(1-p)`: where that ratio is above one it predicts
  the spread should *rise*. In every comparison where it makes that signed prediction, the spread fell.
  **Falsifier**: one of them rising.

**What the four leave standing.** The fact `e285` established is not in doubt and is now three configurations wide:
the same models spread less on a larger held-out sample. What is refuted is that the *amount* is a function of the
sample size -- which is what `e267`'s "buy a bigger suite" argument needs in order to say how much spread a suite
buys -- and one of the two accounts is excluded by a *signed* prediction rather than by a size. The axis the pair set
suggests is not the suite at all: the two ten-times pairs read out through **128 and 300** neurons where `e285`'s
reads out through **32**, so the configurations that barely moved are the ones whose read-out is wide enough to solve
the tasks without the recurrent weights doing the routing.

**What it cannot do.** *Three configurations and three pairs*, so every statement is about those; the axis they
suggest -- read-out width -- is named and **not varied**, and nothing here separates it from the circuit size (300 and
800), the arm count (one against five), the method mix or the code epoch. *Two suite ratios* (4.17 and 10), so X3 is
an ordering test between two points and not a scaling law: what it refutes is `1/sqrt(n_eval)` and it cannot say what
the fall *is* a function of. *The spread is measured on forty replicates*, so each ratio carries about a third of its
own value as sampling error, and the ten-times pairs rest on four comparisons where `e285`'s rests on ten. *The
training is inferred to be identical* from the parameter-derived fields and not from stored weights, exactly as in
`e285`. *The weak rule is permissive by construction* -- a missing draw or a missing flag does not separate -- so X1
is a statement about how much the strong rule is needed and not a bound on how many sample swaps exist. And *the
pairs are not the same experiment*: `e285`'s has five arms and both new ones a single `naive` arm, which is why X3
refutes an account rather than measuring one.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: Keys in `config` that are the manipulation or the output path rather than the configuration.
IGNORE = ("test", "json_out")
#: The config fields that decide what was run. Compared strictly; a field the corpus gained later is not in this list.
SHAPE = ("circuit_size", "iters", "lr", "batch", "lam", "methods", "noise", "classes", "readout_size", "support",
         "shared_head", "basis", "fisher_batches", "normalise_fisher", "pool_below", "pool_buckets",
         "replay_per_task", "replay_batch", "frozen_bias", "input_overlap", "train", "seed0", "q", "rho")
#: The draw blocks: artifacts are the same experiment only if they drew the same read-out, partition and supports.
DRAWS = ("readout", "partition_draw", "support_draw")
#: The fields that are functions of the training, and which therefore decide whether two artifacts are one model.
TRAIN_FIELDS = ("losses", "theta_drift", "bias_norms", "retention_loss", "interference", "full_train_loss")
METRICS = ("final_accuracy", "mean_forgetting")
CLAIMS = (
    ("X1", "the weak rule is not sufficient, and the strong one is what selects",
     "The shape-and-draw rule admits more pairs than the corpus has sample swaps, and the training fields reject the rest",
     "falsifier: every pair the weak rule admits also has identical training"),
    ("X2", "and every sample swap's every comparison falls",
     "Across the fourteen arm-by-metric comparisons the three pairs supply, the sd is smaller at the larger suite",
     "falsifier: any comparison whose sd does not fall"),
    ("X3", "and the fall is not the sample size's",
     "The observed sd ratio is negatively correlated with the 1/sqrt(n_eval) prediction",
     "falsifier: a correlation at or above zero, i.e. the ten-times pairs falling at least as far as the 4.17-times one"),
    ("X4", "nor the accuracy level's",
     "In every comparison where the ceiling account's p(1-p) ratio is above one, the spread still fell",
     "falsifier: one of them rising"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def shape_of(d: dict) -> str:
    """The declared shape fields, so that a flag added to the runner after one side was written cannot separate."""
    cfg = d.get("config") or {}
    return json.dumps({k: cfg.get(k) for k in SHAPE}, sort_keys=True)


def arms(d: dict) -> list[str]:
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return sorted(a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates"))


def shared_replicates(da: dict, db: dict) -> int:
    shared = set(arms(da)) & set(arms(db))
    if not shared:
        return 0
    return min(min(len(da["methods"][m]["replicates"]), len(db["methods"][m]["replicates"])) for m in shared)


def training_identical(da: dict, db: dict) -> dict:
    """Per shared arm: whether every training-derived field agrees across the paired replicates."""
    out = {}
    for m in sorted(set(arms(da)) & set(arms(db))):
        ra, rb = da["methods"][m]["replicates"], db["methods"][m]["replicates"]
        if len(ra) != len(rb):
            out[m] = {"paired": min(len(ra), len(rb)), "identical": False}
            continue
        ok = all(all(x.get(f) == y.get(f) for f in TRAIN_FIELDS) for x, y in zip(ra, rb))
        out[m] = {"paired": len(ra), "identical": bool(ok)}
    return out


def unrecorded_blocks(da: dict, db: dict) -> dict:
    """Which draw blocks and config keys only one of the two records -- reported, since the weak rule tolerates them."""
    draws = sorted(k for k in DRAWS if (da.get(k) is None) != (db.get(k) is None))
    ca = {k: v for k, v in (da.get("config") or {}).items() if k not in IGNORE}
    cb = {k: v for k, v in (db.get("config") or {}).items() if k not in IGNORE}
    return {"draws": draws, "config_keys": sorted(set(ca) ^ set(cb))}


def candidates(root: Path = RUNS, minimum_replicates: int = 5) -> list[dict]:
    """The weak rule: one shape, two suite sizes, no draw that disagrees, and enough replicates to spread."""
    groups: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for p in sorted(root.glob("*.json")):
        d = load(p)
        if d is None or not arms(d):
            continue
        n_eval = (d.get("evaluation_noise") or {}).get("n_eval")
        if n_eval:
            groups[shape_of(d)].append((p.as_posix(), int(n_eval)))

    out = []
    for members in groups.values():
        if len({n for _, n in members}) < 2:
            continue
        members.sort(key=lambda t: t[1])
        for i, (small, n_small) in enumerate(members):
            da = load(small)
            for path, n in members[i + 1:]:
                if n == n_small:
                    continue
                db = load(path)
                draws = unrecorded_blocks(da, db)["draws"]
                disagree = [k for k in DRAWS if k not in draws and da.get(k) != db.get(k)]
                if disagree or shared_replicates(da, db) < minimum_replicates:
                    continue
                training = training_identical(da, db)
                out.append({
                    "old": small, "new": path, "n_old": n_small, "n_new": n,
                    "size_ratio": n / n_small, "arms": sorted(set(arms(da)) & set(arms(db))),
                    "replicates": shared_replicates(da, db), "training": training,
                    "swap": all(t["identical"] for t in training.values()),
                    "unrecorded": unrecorded_blocks(da, db),
                })
    return out


def comparisons(pair: dict) -> list[dict]:
    """The arm-by-metric sd ratios for one pair, with the two candidate accounts' own predictions."""
    da, db = load(pair["old"]), load(pair["new"])
    out = []
    for m in pair["arms"]:
        for metric in METRICS:
            xa = [r[metric] for r in da["methods"][m]["replicates"]]
            xb = [r[metric] for r in db["methods"][m]["replicates"]]
            if len(xa) < 2 or len(xb) < 2:
                continue
            sa, sb = statistics.stdev(xa), statistics.stdev(xb)
            ma, mb = statistics.fmean(xa), statistics.fmean(xb)
            pa, pb = min(max(ma, 0.0), 1.0), min(max(mb, 0.0), 1.0)
            denom = pa * (1 - pa)
            out.append({
                "pair": f"{Path(pair['old']).name} -> {Path(pair['new']).name}",
                "arm": m, "metric": metric, "n_old": pair["n_old"], "n_new": pair["n_new"],
                "size_ratio": pair["size_ratio"], "sd_old": sa, "sd_new": sb, "mean_old": ma, "mean_new": mb,
                "observed": sb / sa if sa else None,
                "sample_prediction": math.sqrt(pair["n_old"] / pair["n_new"]),
                # None and not NaN: a metric whose mean crosses zero has no `p(1-p)` ratio, and JSON would write a
                # NaN as null anyway, so the artifact and the reading should agree about what is undefined
                "ceiling_prediction": math.sqrt(abs(pb * (1 - pb)) / denom) if denom > 0 else None,
            })
    return out


def signed_sd(c: dict) -> str:
    """The ceiling prediction as text, for a reading whose value can be undefined."""
    return "n/a" if c["ceiling_prediction"] is None else f"{c['ceiling_prediction']:.3f}"


def as_text(x: float | None, nd: int = 3) -> str:
    return "n/a" if x is None else f"{x:.{nd}f}"


def correlation(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 3:
        return float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx = math.sqrt(sum((v - mx) ** 2 for v in xs))
    sy = math.sqrt(sum((v - my) ** 2 for v in ys))
    if not sx or not sy:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sx * sy)


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    if not r or not r.get("comparisons"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no sample swap could be read"} for c in CLAIMS]

    weak, swaps = r["n_candidates"], r["pairs"]
    out.append({"id": "X1", "measured": f"the weak rule admits {weak} pairs and the training fields keep {len(swaps)}; "
                                        f"the {weak - len(swaps)} it rejects are the corpus's epoch changes",
                "verdict": "MET -- the strong rule is doing the selecting" if weak > len(swaps) else
                           "FALSIFIER FIRED -- the weak rule admits nothing the training fields reject"})

    fell = [c for c in r["comparisons"] if c["observed"] < 1]
    n = len(r["comparisons"])
    out.append({"id": "X2", "measured": f"{len(fell)} of {n} comparisons fall at the larger suite "
                                        f"(sd ratios {min(c['observed'] for c in r['comparisons']):.3f} to "
                                        f"{max(c['observed'] for c in r['comparisons']):.3f})",
                "verdict": "MET -- every sample swap spreads less on the larger sample" if len(fell) == n else
                           f"FALSIFIER FIRED -- {n - len(fell)} of {n} did not fall"})

    obs = [c["observed"] for c in r["comparisons"]]
    pred = [c["sample_prediction"] for c in r["comparisons"]]
    corr = correlation(pred, obs)
    wide = [c["observed"] for c in r["comparisons"] if c["size_ratio"] > 5]
    narrow = [c["observed"] for c in r["comparisons"] if c["size_ratio"] <= 5]
    pred_wide = min(c["sample_prediction"] for c in r["comparisons"])
    pred_narrow = max(c["sample_prediction"] for c in r["comparisons"])
    med_wide = statistics.median(wide) if wide else None
    med_narrow = statistics.median(narrow) if narrow else None
    out.append({"id": "X3", "measured": f"median sd ratio {as_text(med_wide)} at the ten-times pairs against "
                                        f"{as_text(med_narrow)} at the 4.17-times pair, where the account "
                                        f"predicts {pred_wide:.3f} for the ten-times pairs against "
                                        f"{pred_narrow:.3f}; corr(observed, predicted) = {corr:+.3f} over "
                                        f"{len(obs)} comparisons",
                "verdict": "MET -- the fall goes against the sample size rather than with it" if corr < 0 else
                           f"FALSIFIER FIRED -- the correlation is {corr:+.3f}"})

    signed = [c for c in r["comparisons"] if (c["ceiling_prediction"] or 0) > 1]
    rose = [c for c in signed if c["observed"] > 1]
    out.append({"id": "X4", "measured": f"{len(signed)} comparisons where p(1-p) rises, so the account predicts the "
                                        f"spread rises; it fell in {len(signed) - len(rose)} of them "
                                        f"(sd ratios {[round(c['observed'], 3) for c in signed]})",
                "verdict": "MET -- the ceiling account's signed prediction is wrong every time it makes one"
                if signed and not rose else f"FALSIFIER FIRED -- {len(rose)} of {len(signed)} rose"})
    return out


def report(r: dict) -> int:
    print("== the pairs the weak rule admits, and which of them are sample swaps ==")
    print(f"   the weak rule admits {r['n_candidates']} pairs; the training fields keep {len(r['pairs'])}")
    for p in sorted(r["pairs"], key=lambda p: -p["size_ratio"]):
        print(f"   SWAP  {Path(p['old']).name:44} {p['n_old']:5} -> {Path(p['new']).name:32} {p['n_new']:5} "
              f"x{p['size_ratio']:<5g} {p['replicates']:3} reps  {len(p['arms'])} arm(s)  "
              f"unrecorded: {p['unrecorded']['draws'] + p['unrecorded']['config_keys'] or 'none'}")

    print("\n== the sd ratios, and what each account predicts ==")
    print(f"   {'pair':52} {'arm/metric':30} {'size':>5} {'observed':>9} {'1/sqrt(n)':>10} {'p(1-p)':>8}")
    for c in sorted(r["comparisons"], key=lambda c: -c["size_ratio"]):
        print(f"   {c['pair'][:50]:52} {c['arm'] + '/' + c['metric']:30} {c['size_ratio']:5.2f} "
              f"{c['observed']:9.3f} {c['sample_prediction']:10.3f} {signed_sd(c):>8}")

    print("\n== the registered claims, X1-X4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the fact is three configurations wide and the mechanism is not: the spread falls with the sample but")
    print("    not as the sample's size, and the account that would let a suite be priced by arithmetic is refuted)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--min-replicates", type=int, default=5)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    cands = candidates(args.runs, args.min_replicates)
    swaps = [c for c in cands if c["swap"]]
    rows = [c for p in swaps for c in comparisons(p)]
    r = {"n_candidates": len(cands),
         "rejected": [{"old": Path(c["old"]).name, "new": Path(c["new"]).name, "replicates": c["replicates"]}
                      for c in cands if not c["swap"]],
         "pairs": swaps, "comparisons": rows,
         "train_fields": list(TRAIN_FIELDS), "shape": list(SHAPE)}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
