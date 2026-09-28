"""E285 -- two runs, one model: the suite moved and the trained models did not, so the spread is the sample's.

`e275`'s READ left a question it could not answer from inside itself. Its registered control named a held-out column,
the column that is on the training set turned out to be identical, and that settled whether the two runs were the
same experiment -- but it also meant something larger, which nobody read off the two artifacts together: **if the
training is identical and only `--test` changed, then the same forty models were evaluated on two different held-out
samples.** That makes the pair a *sample-swap* experiment, at zero training cost, and it is the only such experiment
in the corpus.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **W1 -- the two artifacts are one configuration.** Their configs agree on every flag but the suite size and the
  output path. **Falsifier**: a second substantive flag that differs.
- **W2 -- and the fields that moved are exactly the held-out ones.** Every per-replicate field the artifact carries
  is declared here as **computed on the held-out sample** or **not**, and the declaration is checked against the
  observation: 200 arm-by-replicate rows, every held-out field moved and every other field is identical, with no
  exception in either direction. **Falsifier**: a field declared held-out that stayed, or one declared not that moved.
- **W3 -- so the replicate spread is a function of the evaluation sample.** With the same forty models, every arm's
  across-replicate sd for both aggregate metrics is **smaller** on the 600-item suite than on the 144-item one -- ten
  of ten, which is p = 2^-10 = 0.001 under a sign null. **Falsifier**: any arm-by-metric whose sd does not fall.

**What this does to the rest of the corpus is the reason to have it.** Every sigma this project prints divides a
difference by a spread, and `e267`'s floor is the same quantity read from the other side (a *numerator* floor against
a spread). `W3` says the spread is not a property of the models alone: measured on a smaller held-out sample it is
larger, by a factor of 1.25x to 2.34x in sd, and by 1.56x to 5.46x in variance. So an arm's error bar depends on the
suite it was measured on, in the same direction `e267` found, and the two findings are one phenomenon.

**What it cannot do.** *The models' identity is inferred and not exhibited*: the two artifacts carry no stored
parameters, so "the same forty models" rests on every parameter-derived field they do carry being byte-identical
(`theta_drift`, `bias_norms`, `retention_loss`, `interference`, `losses`, `full_train_loss`) together with the same
seeds, support draw, readout draw and matched-random partition -- strong, and not the same thing as a saved
`theta`. *The two runs are four days apart*, so a runner change between them would show up as a training field
moving, which is the falsifier; nothing here says which code revision trained the older artifact, whose
`code_revision` is null. *Two samples and one configuration*: W3 is a sign result over ten comparisons, so it
establishes the direction and the size on these two samples and not the rate at which the spread falls with the
suite. *The mechanism is not separated*: the candidate accounts -- a per-model sampling deviation whose spread goes as
`1/sqrt(n_eval)`, the accuracies' move toward the ceiling changing `p(1-p)`, and the accuracy grid going from 1/48 to
1/200 -- all predict a fall, and this unit reports the three side by side rather than choosing. *And the metrics are
aggregates over the tasks*, so what falls is the spread of a mean over three tasks, not of a single task's accuracy.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

OLD = "runs/e140_r32_methods_frozenbias_40reps.json"
NEW = "runs/e275_frozenbias_suite600_40reps.json"
#: The aggregate metrics the spread is compared on.
METRICS = ("final_accuracy", "mean_forgetting")
#: Every per-replicate field either is computed on the held-out sample or is not. The declaration is the claim.
HELD_OUT = ("final_accuracy", "final_per_task", "forgetting_per_task", "learned", "mean_forgetting", "retention")
NOT_HELD_OUT = ("bias_norms", "full_train_loss", "interference", "losses", "method", "retention_loss", "theta_drift")
#: Config keys whose difference is the manipulation rather than a second one.
EXPECTED_DIFFERENCES = ("test", "json_out")
CLAIMS = (
    ("W1", "the two artifacts are one configuration",
     "Their configs agree on every flag but the suite size and the output path",
     "falsifier: a second substantive flag that differs"),
    ("W2", "and the fields that moved are exactly the held-out ones",
     "In all 200 arm-by-replicate rows, every held-out field moved and every other field is identical",
     "falsifier: a field declared held-out that stayed, or one declared not that moved"),
    ("W3", "so the replicate spread is a function of the evaluation sample",
     "For every arm and both metrics, the across-replicate sd is smaller on the 600-item suite -- ten of ten",
     "falsifier: any arm-by-metric whose sd does not fall"),
)
#: The value the sign test takes if all ten comparisons fall the same way.
SIGN_P = 2 ** -10


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def arms(d: dict) -> list[str]:
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return sorted(a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates"))


def pairs(old: dict, new: dict) -> list[tuple[str, dict, dict]]:
    """Every arm-replicate row in both artifacts, paired by position -- the runner writes them in seed order."""
    out = []
    for a in arms(old):
        if a not in new.get("methods", {}):
            continue
        for ro, rn in zip(old["methods"][a]["replicates"], new["methods"][a]["replicates"]):
            out.append((a, ro, rn))
    return out


def field_census(old: dict, new: dict) -> dict:
    """Per field: how many paired rows carry it, how many moved, and how many did not."""
    census: dict[str, dict] = {}
    for _a, ro, rn in pairs(old, new):
        for f in set(ro) | set(rn):
            c = census.setdefault(f, {"rows": 0, "moved": 0, "identical": 0})
            c["rows"] += 1
            if ro.get(f) == rn.get(f):
                c["identical"] += 1
            else:
                c["moved"] += 1
    return census


def spreads(old: dict, new: dict) -> dict:
    """The across-replicate sd of each arm and metric, and the two ratios a candidate account predicts."""
    out = {}
    n_old = ((old.get("evaluation_noise") or {}).get("n_eval")) or 0
    n_new = ((new.get("evaluation_noise") or {}).get("n_eval")) or 0
    for a in arms(old):
        for m in METRICS:
            xo = [r[m] for r in old["methods"][a]["replicates"]]
            xn = [r[m] for r in new["methods"][a]["replicates"]]
            so, sn = statistics.stdev(xo), statistics.stdev(xn)
            mo, mn = statistics.fmean(xo), statistics.fmean(xn)
            out[f"{a}/{m}"] = {
                "sd_old": so, "sd_new": sn, "mean_old": mo, "mean_new": mn,
                "sd_ratio": sn / so if so else float("nan"),
                "variance_ratio": (so / sn) ** 2 if sn else float("nan"),
                "n_eval_ratio": math.sqrt(n_old / n_new) if n_new else float("nan"),
                "p_ratio": math.sqrt(abs(mn * (1 - mn)) / abs(mo * (1 - mo)))
                if mo * (1 - mo) else float("nan"),
                "seconds_old": duration_seconds(old), "seconds_new": duration_seconds(new)}
    return out


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    if not r or not r.get("census"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- one of the two artifacts is absent"} for c in CLAIMS]

    unexpected = [k for k in r["config_differences"] if k not in EXPECTED_DIFFERENCES]
    out.append({"id": "W1", "measured": f"config keys that differ: {sorted(r['config_differences']) or 'none'}; "
                                        f"unexpected: {unexpected or 'none'}",
                "verdict": "MET -- one configuration at two suites" if not unexpected else
                           f"FALSIFIER FIRED -- {unexpected} also differ"})

    held = {f: c for f, c in r["census"].items() if f in HELD_OUT}
    other = {f: c for f, c in r["census"].items() if f in NOT_HELD_OUT}
    unclassified = sorted(set(r["census"]) - set(HELD_OUT) - set(NOT_HELD_OUT))
    bad_held = [f for f, c in held.items() if c["moved"] != c["rows"]]
    bad_other = [f for f, c in other.items() if c["identical"] != c["rows"]]
    moved = sum(c["moved"] for c in held.values())
    stayed = sum(c["identical"] for c in other.values())
    out.append({"id": "W2", "measured": f"{len(held)} held-out fields moved in {moved} cells and {len(other)} others "
                                        f"stayed in {stayed}; held-out that stayed: {bad_held or 'none'}; others that "
                                        f"moved: {bad_other or 'none'}; unclassified fields: {unclassified or 'none'}",
                "verdict": "MET -- the split is the evaluation sample's and nothing else" if not bad_held and not bad_other
                else f"FALSIFIER FIRED -- {bad_held + bad_other}"})

    fell = [k for k, v in r["spreads"].items() if v["sd_ratio"] < 1]
    n = len(r["spreads"])
    out.append({"id": "W3", "measured": f"{len(fell)} of {n} arm-by-metric spreads fell with the larger suite "
                                        f"(sd ratios {min(v['sd_ratio'] for v in r['spreads'].values()):.2f} to "
                                        f"{max(v['sd_ratio'] for v in r['spreads'].values()):.2f}, p = {SIGN_P:g} "
                                        f"under a sign null)",
                "verdict": "MET -- the same models spread less on the larger sample" if len(fell) == n and n else
                           f"FALSIFIER FIRED -- {n - len(fell)} of {n} did not fall"})
    return out


def report(r: dict) -> int:
    print("== the two artifacts ==")
    print(f"   {OLD}\n      {r['n_old']} rows at n_eval {r['n_eval_old']}, {r['seconds_old'] / 3600:.2f} h")
    print(f"   {NEW}\n      {r['n_new']} rows at n_eval {r['n_eval_new']}, {r['seconds_new'] / 3600:.2f} h")
    print(f"   config keys that differ: {sorted(r['config_differences'])}")

    print("\n== every per-replicate field, by what it is computed on ==")
    for f in HELD_OUT:
        c = r["census"].get(f)
        if c:
            print(f"   held-out      {f:20} moved {c['moved']:4} of {c['rows']:4}")
    for f in NOT_HELD_OUT:
        c = r["census"].get(f)
        if c:
            print(f"   not held-out  {f:20} identical {c['identical']:4} of {c['rows']:4}")
    extra = sorted(set(r["census"]) - set(HELD_OUT) - set(NOT_HELD_OUT))
    if extra:
        print(f"   unclassified: {extra}")

    print("\n== the spread, on the same models at two samples ==")
    print(f"   {'arm/metric':34} {'sd 144':>8} {'sd 600':>8} {'sd ratio':>9} {'1/sqrt(n)':>10} {'p(1-p)':>8}")
    for k, v in sorted(r["spreads"].items()):
        print(f"   {k:34} {v['sd_old']:8.4f} {v['sd_new']:8.4f} {v['sd_ratio']:9.3f} "
              f"{v['n_eval_ratio']:10.3f} {v['p_ratio']:8.3f}")
    print("   (the last two columns are the candidate accounts, not the observation: a per-model sampling deviation")
    print("    that goes as 1/sqrt(n_eval), and the move of the accuracies toward the ceiling changing p(1-p))")

    print("\n== the registered claims, W1-W3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (two runs, one model: the suite changed and the trained models did not, so the pair is a sample swap")
    print("    and the replicate spread is the sample's as much as the configuration's)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    a, b = load(OLD), load(NEW)
    if a is None or b is None:
        print(f"both artifacts are needed: {OLD}, {NEW}")
        if args.json_out:
            write_json(args.json_out, {"old": OLD, "new": NEW, "census": None, "claims": judge(None)})
            print(f"wrote {args.json_out}")
        return report({"census": None})

    cfg_diff = {k: [a.get("config", {}).get(k), b.get("config", {}).get(k)]
                for k in set(a.get("config", {})) | set(b.get("config", {}))
                if a.get("config", {}).get(k) != b.get("config", {}).get(k)}
    r = {
        "old": OLD, "new": NEW, "config_differences": cfg_diff,
        "n_old": len(pairs(a, b)), "n_new": len(pairs(a, b)),
        "n_eval_old": (a.get("evaluation_noise") or {}).get("n_eval"),
        "n_eval_new": (b.get("evaluation_noise") or {}).get("n_eval"),
        "seconds_old": duration_seconds(a), "seconds_new": duration_seconds(b),
        "census": field_census(a, b), "spreads": spreads(a, b),
        "held_out": list(HELD_OUT), "not_held_out": list(NOT_HELD_OUT),
        "same_draws": {k: a.get(k) == b.get(k) for k in ("circuit", "readout", "partition_draw", "environment")},
        "sign_p": SIGN_P,
    }
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
