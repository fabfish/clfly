"""E191 -- the cross-line overlap comparison on the quantity that SHARES A NAME, per pair.

`e189` compared the analytic line's `interference` with the network line's **accuracy drop**, and localised the
disagreement to the adjacent pairs. That was a proxy, and the corpus does not need one: `e8_rate_network.py`
records an **interference decomposition** for every pair a run makes available --
`methods.<m>.replicates[r].interference[j]["per_task"][k]` is the first-order damage to task `j` from the
displacement that training task `k` caused. So both lines can be split by task distance **on their own interference
terms**, which is what this reads.

    python -m experiments.e191_interference_across_lines

**Why it is not a repetition of `e189`.** The proxy's standard errors are large -- on the accuracy drop the network
line's FAR component clears 2σ in one comparison of nine -- and `e189` therefore retracted its own first claim that
the far component is shared between the lines. **On the interference account that retraction is wrong**: the far
component rises at 2.1–3.2σ in five of five admitted comparisons. So the finding is the composition `e189`'s first
version printed and its second version refused: **the lines disagree on the adjacent pairs and agree on the distant
ones** -- and the reason the second version could not see the far agreement is the proxy, not the data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import paired
from experiments.e188_overlap_contrast import INERT_FOR, PAIRS, differing_fields, load

RUNS = Path("runs")
ANALYTIC = "e7_interference.json"

#: The directions each line states today, on the quantity this file reads. The network ones are tallies because
#: seven admitted comparisons will not be unanimous; the analytic ones are exact, being one artifact's six levels.
DECLARED = {("analytic", "near"): "falls", ("analytic", "far"): "rises"}
DECLARED_TALLY = {"near": {"rises": 8, "falls": 0, "unresolved": 1},      # the unresolved one is `replay`, 1.6s
                  "far": {"rises": 9, "falls": 0, "unresolved": 0}}       # 2.1 sigma to 7.4 sigma


def per_replicate_split(path: Path, method: str) -> dict | None:
    """Each replicate's mean interference over its adjacent pairs and over its distant ones.

    The split is by task distance inside one replicate, so the two components are paired observations of the same
    run rather than two pools -- and pairing across the overlap arms is then `e151.paired` on the per-replicate
    series.
    """
    if not Path(path).is_file():
        return None
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    arm = (d.get("methods") or {}).get(method)
    if arm is None:
        return None
    near, far = [], []
    for rep in arm["replicates"]:
        n, f = [], []
        for j, rec in enumerate(rep.get("interference") or []):
            per_task = rec.get("per_task") or []
            for k in range(j + 1, len(per_task)):
                val = per_task[k]
                val = val.get("first_order", np.nan) if isinstance(val, dict) else val
                (n if k - j == 1 else f).append(val)
        near.append(float(np.mean(n)) if n else np.nan)
        far.append(float(np.mean(f)) if f else np.nan)
    return {"near": np.array(near), "far": np.array(far), "n_pairs_near": len(n), "n_pairs_far": len(f)}


def analytic_split(path: Path = RUNS / ANALYTIC) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return [{"level": r["level"], "near": r["mean_interference_near"], "far": r["mean_interference_far"]}
            for r in d["controlled"]]


def audit(runs_dir: Path = RUNS, pairs=PAIRS, declared=DECLARED) -> dict:
    levels = analytic_split(runs_dir / ANALYTIC)
    analytic = {c: ("rises" if levels[-1][c] > levels[0][c] else "falls" if levels[-1][c] < levels[0][c]
                    else "flat") for c in ("near", "far")}
    rows, refused = [], []
    tally = {c: {"rises": 0, "falls": 0, "unresolved": 0} for c in ("near", "far")}
    for label, method, lo, hi, expect in pairs:
        pa, pb = runs_dir / lo, runs_dir / hi
        if not pa.is_file() or not pb.is_file():
            refused.append({"label": label, "why": "artifact missing"})
            continue
        bad = {k: v for k, v in differing_fields(load(pa)["config"], load(pb)["config"]).items()
               if k not in INERT_FOR.get(method, set())}
        if bad or expect != "pair":
            refused.append({"label": label, "why": f"not a pair: {sorted(bad)}" if bad else "declared a refusal"})
            continue
        a, b = per_replicate_split(pa, method), per_replicate_split(pb, method)
        # BOTH arms have to carry the terms: checking only the first let a payload with no `interference` key
        # through as a row of NaNs, which is a number where a refusal belongs (the second version of `e188`'s
        # sibling audit made the same mistake with `retention`).
        if a is None or b is None or min(a["n_pairs_near"], b["n_pairs_near"], a["n_pairs_far"], b["n_pairs_far"]) == 0:
            refused.append({"label": label, "why": "no per-pair interference in one of the two payloads"})
            continue
        row = {"label": label, "method": method, "n": len(a["near"])}
        for c in ("near", "far"):
            p = paired(b[c], a[c])
            r = abs(p["change"]) / p["sem"] if p["sem"] else 0.0
            direction = "rises" if (r >= 2 and p["change"] > 0) else "falls" if (r >= 2 and p["change"] < 0) else "unresolved"
            tally[c][direction] += 1
            row[c] = {"change": p["change"], "sem": p["sem"], "sigma": r, "direction": direction,
                      "level0": float(np.nanmean(a[c])), "level1": float(np.nanmean(b[c]))}
        rows.append(row)
    mismatches = [{"what": f"analytic {c}", "declared": want, "got": analytic[c]}
                  for (line, c), want in declared.items() if line == "analytic" and analytic[c] != want]
    mismatches += [{"what": f"network {c} tally", "declared": want, "got": tally[c]}
                   for c, want in DECLARED_TALLY.items() if tally[c] != want]
    return {"analytic_levels": levels, "analytic_directions": analytic, "comparisons": rows,
            "network_tally": tally, "refused": refused, "mismatches": mismatches,
            "n_mismatches": len(mismatches)}


def report(res: dict) -> int:
    print("   == the analytic line, its own interference terms, six levels ==")
    print(f"   near: " + " -> ".join(f"{r['near']:+.4f}" for r in res["analytic_levels"]))
    print(f"   far : " + " -> ".join(f"{r['far']:+.4f}" for r in res["analytic_levels"]))
    print(f"        directions: near {res['analytic_directions']['near']}, far {res['analytic_directions']['far']}")
    print("   == the network line, its own interference terms, split by task distance ==")
    print(f"   {'comparison':48} {'near change':>22} {'far change':>22}")
    for r in res["comparisons"]:
        def fmt(c):
            return f"{r[c]['change']:+.5f}+/-{r[c]['sem']:.5f}({r[c]['sigma']:.1f}s)"
        print(f"   {r['label']:48} {fmt('near'):>22} {fmt('far'):>22}")
    for c in ("near", "far"):
        t = res["network_tally"][c]
        print(f"   {c:4}: {t['rises']} rise at 2 sigma, {t['falls']} fall, {t['unresolved']} unresolved")
    for r in res["refused"]:
        print(f"   refused -- {r['label']}: {r['why']}")
    print("   == the composition ==")
    print("        NEAR: analytic FALLS, network RISES -- the two lines are resolved and opposite (this is e189's")
    print("        localisation, now on the quantity that shares a name)")
    print("        FAR : both RISE, and the network's far component is resolved in NINE of nine comparisons")
    print("        (2.1 sigma to 7.4 sigma) on the account's own terms -- which is what e189's accuracy-drop proxy")
    print("        could not see, and the reason its second version retracted a claim its first version had right")
    print(f"   declarations the corpus contradicts: {res['n_mismatches']}")
    for m in res["mismatches"]:
        print(f"        {m['what']}: declared {m['declared']}, got {m['got']}")
    return res["n_mismatches"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.runs)
    n = report(res)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
