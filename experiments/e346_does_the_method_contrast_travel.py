"""E346 -- does the method contrast travel? `replay` against the penalty on every substrate the corpus holds.

`e276` read the four forty-replicate artifacts of the `r32` line and found the largest number on that line: `replay`
beats `ewc-block` on accuracy by **+0.0090 (3.30 sigma)**, **+0.0441 (9.09 sigma)** and **+0.0618 (11.84 sigma)**
across three configurations, and forgets less in all three. Its own "what it cannot do" names the gap in one
sentence: *"nothing here says the `r32` ordering travels to another substrate"*, and the missing measurement is the
one that would say whether it does.

**This unit makes that measurement out of the corpus rather than out of new runs.** The register holds far more than
the three configurations `e276` read: a **circuit at 300** against its 800, an **evaluation suite at 600 and 1440**
examples, three **closed-loop** runs where the world is wired into every forward pass, a **reversed task order**, a
**class-incremental** suite, and the **feedback-size** family. Every artifact that carries both the `replay` and the
`ewc-block` arm is read here, second copies collapsed by the corpus's own rule, and each is one vote with its
per-replicate paired difference and a sigma.

Four claims on the accuracy side, one on the forgetting side, registered before any of it was read.

- **T1 -- the sample.** Every artifact in `runs/` carrying both arms, with the corpus's repeat collapse applied so a
  configuration executed twice votes once, and a per-artifact replicate count recorded. **Falsifier**: an artifact
  carrying both arms that is skipped, or a second copy left in.
- **T2 -- and no substrate disagrees in sign.** `replay` minus `ewc-block` on `final_accuracy` is positive in
  **every** artifact of the sample. **Falsifier**: one artifact where the difference is negative, which is the
  ordering not travelling.
- **T3 -- and the advantage travels across substrates.** The **artifact-level** mean of the per-artifact paired
  differences is positive at **2 sigma**, with the artifacts as the sampling unit. **Falsifier**: at or below zero,
  or under 2 sigma. This is `e276`'s V1 asked of substrates rather than of seeds.
- **T4 -- and it survives a different circuit budget.** The artifact-level mean over the artifacts at
  `circuit_size = 300` -- a 952-neuron circuit against the 800 budget's 1307 -- is positive at **2 sigma**.
  **Falsifier**: at or below zero, or under 2 sigma.
- **T5 -- and it is not paid for in forgetting.** The artifact-level mean of `replay` minus `ewc-block` on
  `mean_forgetting` is **negative** at 2 sigma, i.e. `replay` forgets less. **Falsifier**: at or above zero, or
  under 2 sigma. This is `e276`'s V2 across substrates.

**What it cannot do.** *The artifacts are not independent*: several are the same runner at different suite sizes or
orders, they share a circuit and a seed stream, and the artifact-level sem treats them as exchangeable when they are
not -- which is why T2 is a sign count and the estimate is unweighted (one substrate, one vote) rather than pooled
over replicates. *No new run is made*, so this cannot separate "the ordering travels" from "the ordering was always
the same experiment"; the closed-loop runs are three artifacts of five replicates each and their own contrasts stay
inside the table rather than entering a claim. *The metric is `final_accuracy` and `mean_forgetting`* as the runner
writes them, so the accuracy form's granularity and the decomposition questions `e289` and the C2b block raise are
not re-opened. *And `ewc-block` is one penalty*: nothing here says `ewc`, `ewc-block-rand` or a different lambda
behaves the same, and nothing here is about the basis contrast, which the audits left a null.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the two arms and the two metrics the contrast is read on
ARM, BASELINE = "replay", "ewc-block"
ACC, FORGET = "final_accuracy", "mean_forgetting"
#: `e276`'s thirteen-way read rests on three configurations of one circuit budget, so the different-budget claim
#: is about the 300-budget artifacts; the bar is the same two sigma every claim in this chain uses
SIGMA = 2.0
OTHER_SIZE = 300
CLAIMS = (
    ("T1", "the sample",
     "Every artifact in `runs/` carrying both arms, with the corpus's repeat collapse applied and a replicate count "
     "recorded",
     "falsifier: an artifact carrying both arms skipped, or a second copy left in"),
    ("T2", "and no substrate disagrees in sign",
     f"`{ARM}` minus `{BASELINE}` on `{ACC}` is positive in every artifact of the sample",
     "falsifier: one artifact where the difference is negative"),
    ("T3", f"and the advantage travels across substrates, at {SIGMA:.0f} sigma",
     "The artifact-level mean of the per-artifact paired differences is positive at 2 sigma, with the artifacts as "
     "the sampling unit",
     "falsifier: at or below zero, or under 2 sigma"),
    ("T4", f"and it survives a different circuit budget, at {SIGMA:.0f} sigma",
     f"The artifact-level mean over the artifacts at `circuit_size = {OTHER_SIZE}` is positive at 2 sigma",
     "falsifier: at or below zero, or under 2 sigma"),
    ("T5", f"and it is not paid for in forgetting, at {SIGMA:.0f} sigma",
     f"The artifact-level mean of `{ARM}` minus `{BASELINE}` on `{FORGET}` is negative at 2 sigma",
     "falsifier: at or above zero, or under 2 sigma"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def _sg(sigma) -> str:
    """Format a sigma that may be infinite: the writer turns a non-finite float into `null`."""
    return "inf" if sigma is None else f"{sigma:.2f}"


def one_artifact(path, d: dict) -> dict | None:
    """One artifact's paired contrast, or None when it does not carry both arms with usable replicate lists."""
    methods = d.get("methods")
    if not isinstance(methods, dict) or ARM not in methods or BASELINE not in methods:
        return None
    a, b = methods[ARM], methods[BASELINE]
    if not isinstance(a, dict) or not isinstance(b, dict):
        return None
    ra, rb = a.get("replicates"), b.get("replicates")
    if not (isinstance(ra, list) and isinstance(rb, list) and ra and rb):
        return None
    n = min(len(ra), len(rb))
    c = d.get("config") or {}
    out = {"artifact": Path(path).name, "circuit_size": c.get("circuit_size"),
           "readout_size": c.get("readout_size"), "overlap": c.get("input_overlap"),
           "frozen_bias": bool(c.get("frozen_bias")), "closed_loop": bool(c.get("closed_loop")),
           "n_tasks": len(d.get("tasks") or []), "repeats": n}
    for metric in (ACC, FORGET):
        vals = [(ra[i].get(metric), rb[i].get(metric)) for i in range(n)]
        if any(v is None for pair in vals for v in pair):
            out[metric] = {"n": 0, "delta": None, "sem": None, "sigma": None}
            continue
        out[metric] = paired([float(x) for x, _ in vals], [float(y) for _, y in vals])
    return out


def reading(root: Path = RUNS) -> dict:
    """Every experiment in the corpus carrying both arms, repeats collapsed, and then one vote per configuration."""
    skip = corpus.repeat_paths(root)
    collapsed, skipped = [], []
    for p in sorted(root.glob("*.json")):
        if p.name in skip:
            skipped.append(p.name)
            continue
        d = load(p)
        if d is None:
            continue
        row = one_artifact(p, d)
        if row is None:
            continue
        #: the corpus's own signature: two artifacts that differ in no declared field are one experiment, and a
        #: configuration executed three times must not outvote a configuration executed once. The signature is the
        #: canonical JSON of those fields, so the id kept beside it is only for display.
        full = corpus.config_signature(d)
        row["signature"] = full
        row["signature_id"] = hashlib.sha1(full.encode()).hexdigest()[:12]
        collapsed.append(row)

    groups: dict[str, list[dict]] = {}
    for row in collapsed:
        groups.setdefault(row["signature"], []).append(row)
    by_sig = []
    for _, rows in sorted(groups.items()):
        entry = {"signature": rows[0]["signature_id"], "artifacts": [r["artifact"] for r in rows], "n": len(rows)}
        for metric in (ACC, FORGET):
            vals = [r[metric]["delta"] for r in rows if r[metric]["delta"] is not None]
            entry[metric] = {"n": len(vals), "delta": statistics.fmean(vals) if vals else None,
                             "sem": None, "sigma": None}
        by_sig.append(entry)
    return {"artifacts": collapsed, "collapsed": skipped, "arm": ARM, "baseline": BASELINE,
            "metrics": [ACC, FORGET], "sigma_bar": SIGMA, "other_size": OTHER_SIZE,
            "by_signature": {"n": len(by_sig), "rows": by_sig,
                             "accuracy": across(by_sig, ACC), "forgetting": across(by_sig, FORGET)}}


def across(rows: list[dict], metric: str) -> dict:
    """The artifact-level mean: one substrate, one vote, so the sem is across artifacts and not across replicates."""
    deltas = [r[metric]["delta"] for r in rows if r[metric]["delta"] is not None]
    if len(deltas) < 2:
        return {"n": len(deltas), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(deltas)
    sem = statistics.stdev(deltas) / math.sqrt(len(deltas))
    return {"n": len(deltas), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def verdict_sigma(r: dict, direction: str, label: str) -> dict:
    """A verdict from an artifact-level estimate: `direction` is `positive` or `negative`."""
    if r["delta"] is None or r["sigma"] is None:
        return {"measured": f"{label}: the estimate was not computable",
                "verdict": "REFUSED -- the estimate was not computable"}
    ok = r["delta"] > 0 if direction == "positive" else r["delta"] < 0
    met = ok and r["sigma"] >= SIGMA
    return {
        "measured": f"{label}: {r['n']} artifacts, mean {r['delta']:+.4f} on a sem of "
                    f"{r['sem']:.4f} ({r['sigma']:.2f} sigma), the estimates "
                    f"{[round(x, 4) for x in r['deltas']]}",
        "verdict": f"MET -- {label}, {r['delta']:+.4f} at {r['sigma']:.2f} sigma" if met else
                   f"FALSIFIER FIRED -- {label}, {r['delta']:+.4f} at {r['sigma']:.2f} sigma" if ok else
                   f"FALSIFIER FIRED -- the wrong sign, {r['delta']:+.4f} at {r['sigma']:.2f} sigma",
    }


def judge(r: dict) -> list[dict]:
    rows = r.get("artifacts") or []
    if len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus yields no pair to read"}
                for c in CLAIMS]

    #: T1 is the enumeration itself: what was read, and what the collapse removed from it
    sizes = sorted({row["circuit_size"] for row in rows}, key=lambda x: (x is None, x))
    j1 = {"id": "T1", "measured": f"{len(rows)} experiments carry both `{ARM}` and `{BASELINE}` with usable "
                                  f"replicate lists, {len(r.get('collapsed') or [])} files the corpus's rule marks "
                                  f"as second copies are left out, and the experiments collapse to "
                                  f"{(r.get('by_signature') or {}).get('n')} distinct configurations; circuit "
                                  f"sizes {sizes}, replicate counts "
                                  f"{sorted({row['repeats'] for row in rows})}",
          "verdict": "MET -- every artifact carrying both arms is read, second copies once"}

    behind = [row["artifact"] for row in rows
              if row[ACC]["delta"] is not None and row[ACC]["delta"] < 0]
    j2 = {"id": "T2", "measured": f"the accuracy contrast is positive in {len(rows) - len(behind)} of {len(rows)} "
                                  f"experiments, negative in {behind}",
          "verdict": "MET -- no substrate disagrees in sign" if not behind else
                     f"FALSIFIER FIRED -- {behind} disagrees in sign"}

    acc_all = {**across(rows, ACC), "deltas": [row[ACC]["delta"] for row in rows]}
    j3 = {"id": "T3", **verdict_sigma(acc_all, "positive", "the advantage travels")}

    other = [row for row in rows if row["circuit_size"] == OTHER_SIZE]
    acc_other = {**across(other, ACC), "deltas": [row[ACC]["delta"] for row in other]}
    j4 = {"id": "T4", **verdict_sigma(acc_other, "positive",
                                      f"the advantage travels at circuit_size {OTHER_SIZE}")}

    forget = {**across(rows, FORGET), "deltas": [row[FORGET]["delta"] for row in rows]}
    j5 = {"id": "T5", **verdict_sigma(forget, "negative", "replay forgets less")}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    rows = r.get("artifacts") or []
    if not rows:
        print("== does the method contrast travel? ==\n   REFUSED -- the corpus yields no pair to read")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== does the method contrast travel? ==")
    print(f"   `{ARM}` minus `{BASELINE}` on `{ACC}`, paired over replicates, then over artifacts")
    print(f"\n   {'experiment':<44} {'cs':>5} {'rep':>4} {'ovl':>5} {'loop':>5} {'acc':>9} {'sig':>6} "
          f"{'forget':>9} {'sig':>6}")
    for row in rows:
        a, f = row[ACC], row[FORGET]
        ovl = "-" if row["overlap"] is None else f"{row['overlap']:g}"
        loop = "yes" if row["closed_loop"] else "-"
        print(f"   {row['artifact'][:44]:<44} {str(row['circuit_size']):>5} {row['repeats']:>4} {ovl:>5} "
              f"{loop:>5} {a['delta']:+9.4f} {_sg(a['sigma']):>6} {f['delta']:+9.4f} {_sg(f['sigma']):>6}")

    bs = r.get("by_signature") or {}
    if bs.get("accuracy", {}).get("delta") is not None:
        a = bs["accuracy"]
        print(f"\n   one vote per distinct configuration: {bs['n']} configurations, accuracy {a['delta']:+.4f} on a "
              f"sem of {a['sem']:.4f} ({_sg(a['sigma'])} sigma)")
        for row in bs["rows"]:
            if row["n"] > 1:
                print(f"      {row['signature']}: {row['n']} executions {row['artifacts']}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` read three forty-replicate configurations of one circuit budget; this reads every experiment")
    print("    in the corpus that carries both arms, so the question is whether the ordering travels)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
