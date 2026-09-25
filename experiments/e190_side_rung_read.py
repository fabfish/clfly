"""E190 -- the read `e178` was launched for, written before the artifact exists.

`e178` registered four outcomes for one command -- the same three arms at the **same basis** at **cs = 300**, 144
replicates -- and the registration is `docs/findings/2026-09-25-the-side-rungs-negative-priced-before-it-is-bought.md`
section 3. This is the reader, so that the moment the JSON lands the verdict is one command rather than a fresh
argument about which quantity the claim is about.

**Which quantity is not a detail.** The registration's arithmetic is on per-replicate **accuracy** -- it exists to
correct the paper's §8 figure, whose quoted sd was *unpaired*, and its triple is
`+0.0278  -0.0625  -0.0000` (mean **-0.0116**, sd 0.0462) on accuracy. The same three replicates give
`-0.0521  +0.0833  -0.0208` on **forgetting**, i.e. a different sign pattern, because the two quantities are not
monotone transforms of one another in a three-task retention matrix. So the reader prints both, names which is
registered, and never mixes them.

    python -m experiments.e190_side_rung_read                  # the registered read, if the artifact is there
    python -m experiments.e190_side_rung_read --quantity both

**The registration, quoted so the bars cannot drift** (P1 at least 2σ negative; P2 the gap *larger* at cs = 300
than at cs = 800, i.e. more negative; the falsifier ≥ 2σ positive; and an unresolved result worth keeping, because
both circuits' gaps shrinking would be evidence *for* the estimation-quality account rather than against it).
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
DEFAULT_ARTIFACT = "runs/e178_rung_side_cs300_144reps.json"
DEFAULT_COMPARATOR = "runs/e10_rung_side.json"
PAIR = ("ewc-block", "ewc-block-rand")


def paired_gap(artifact: Path, quantity: str = "accuracy", pair=PAIR) -> dict | None:
    """The per-replicate paired difference `pair[0] - pair[1]`, on the quantity the registration names.

    `accuracy` reads each replicate's `final_accuracy`; `forgetting` reads its `mean_forgetting`. Paired by list
    index, which is seed order because every run here starts at `seed0 = 0` with the same replicate count.
    """
    if not Path(artifact).is_file():
        return None
    d = json.loads(Path(artifact).read_text(encoding="utf-8"))
    keys = ("final_accuracy",) if quantity == "accuracy" else ("mean_forgetting",)
    arms = {}
    for m in pair:
        entry = (d.get("methods") or {}).get(m)
        if entry is None:
            return None
        arms[m] = np.array([r[keys[0]] for r in entry["replicates"]], dtype=float)
    if len(arms[pair[0]]) != len(arms[pair[1]]):
        return None
    diff = arms[pair[0]] - arms[pair[1]]
    n = len(diff)
    sd = float(diff.std(ddof=1)) if n > 1 else float("nan")
    sem = sd / np.sqrt(n) if n > 1 else float("nan")
    config = d.get("config") or {}
    return {"artifact": Path(artifact).name, "quantity": quantity, "n": n,
            "mean": float(diff.mean()), "sd": sd, "sem": sem,
            "sigma": abs(float(diff.mean())) / sem if sem else None,
            "n_negative": int((diff < 0).sum()), "n_positive": int((diff > 0).sum()),
            "circuit_size": config.get("circuit_size"), "basis": config.get("basis"),
            "repeats": config.get("repeats"), "readout_size": config.get("readout_size"),
            "input_overlap": config.get("input_overlap"),
            "timing_s": d.get("timing_s"), "per_replicate": [float(x) for x in diff]}


def verdict(gap: dict, comparator: dict | None) -> dict:
    """The four registered outcomes, decided from the numbers rather than from the prose around them."""
    if gap is None:
        return {"outcome": "not yet written"}
    negative = gap["mean"] < 0
    resolved = (gap["sigma"] or 0) >= 2
    if negative and resolved:
        outcome = "P1 HOLDS"
    elif not negative and resolved:
        outcome = "THE FALSIFIER FIRES"
    else:
        outcome = "UNRESOLVED AT %d REPLICATES (the null worth keeping)" % gap["n"]
    out = {"outcome": outcome, "P1": None, "P2": None, "falsifier": None}
    out["P1"] = "holds" if (negative and resolved) else "does not hold"
    out["falsifier"] = "fires" if (not negative and resolved) else "does not fire"
    if comparator is None:
        out["P2"] = "cannot be read: the comparator artifact is absent"
    else:
        out["P2"] = ("agrees -- the gap is more negative at the smaller circuit"
                     if gap["mean"] < comparator["mean"]
                     else "does NOT agree -- the gap is less negative at the smaller circuit"
                     if gap["mean"] > comparator["mean"] else "tied")
        out["comparator_mean"] = comparator["mean"]
    return out


def report(gap: dict | None, comparator: dict | None, v: dict) -> int:
    if gap is None:
        print(f"   {DEFAULT_ARTIFACT} is not written yet -- no number is printed from a design whose arms do not")
        print("   exist (rule 22). The registration is "
              "docs/findings/2026-09-25-the-side-rungs-negative-priced-before-it-is-bought.md section 3:")
        print("        P1     the gap at cs = 300 is negative and resolved at >= 2 sigma")
        print("        P2     the gap is LARGER (more negative) at cs = 300 than at cs = 800")
        print("        fals.  the gap resolves POSITIVE at >= 2 sigma")
        print("        null   unresolved even at 144 replicates, which is evidence FOR the account, not against")
        return 0
    print(f"   {gap['artifact']}: basis {gap['basis']}, cs = {gap['circuit_size']}, read-out "
          f"{gap['readout_size']}, overlap {gap['input_overlap']}, {gap['repeats']} configured replicates")
    if gap["timing_s"]:
        print(f"   its own recorded cost: {gap['timing_s']:.0f} s = {gap['timing_s'] / 3600:.2f} h (rule 49: the "
              f"registered price was an extrapolation and the artifact carries the real one)")
    for q in ("accuracy", "forgetting"):
        g = gap if gap["quantity"] == q else None
        if g is None:
            continue
        print(f"   {q:11} paired {PAIR[0]} - {PAIR[1]}: n {g['n']}, mean {g['mean']:+.4f}, sd {g['sd']:.4f}, "
              f"sem {g['sem']:.4f}, {g['sigma']:.2f} sigma, {g['n_negative']} negative / {g['n_positive']} positive")
    if comparator is not None:
        print(f"   comparator {comparator['artifact']} (basis {comparator['basis']}, cs "
              f"{comparator['circuit_size']}, n {comparator['n']}): mean {comparator['mean']:+.4f}, "
              f"sd {comparator['sd']:.4f}, sem {comparator['sem']:.4f}")
    print("   == the registered outcomes ==")
    print(f"        {v['outcome']}")
    print(f"        P1        : {v['P1']}")
    print(f"        P2        : {v['P2']}")
    print(f"        falsifier : {v['falsifier']}")
    if gap.get("sigma") is not None:
        # one line written to be pasted into the plan row, so the row quotes the reader rather than a retyping
        print(f"   PLAN-ROW LINE: {v['outcome']}: paired {PAIR[0]} - {PAIR[1]} on {gap['quantity']} "
              f"**{gap['mean']:+.4f} +/- {gap['sem']:.4f} = {gap['sigma']:.2f}σ** over {gap['n']} seeds "
              f"({gap['n_negative']} negative / {gap['n_positive']} positive); P2 {v['P2']}; "
              f"falsifier {v['falsifier']}; the artifact's own cost {gap['timing_s']:.0f} s"
              if gap.get("timing_s") else "")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifact", type=Path, default=Path(DEFAULT_ARTIFACT))
    p.add_argument("--comparator", type=Path, default=Path(DEFAULT_COMPARATOR))
    p.add_argument("--quantity", choices=("accuracy", "forgetting", "both"), default="both")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    quantities = ("accuracy", "forgetting") if args.quantity == "both" else (args.quantity,)
    gaps = {q: paired_gap(args.artifact, q) for q in quantities}
    comp = paired_gap(args.comparator, "accuracy")
    registered = gaps.get("accuracy") or next(iter(gaps.values()), None)
    v = verdict(registered, comp)
    n = report(registered, comp, v)
    if args.json_out:
        write_json(args.json_out, {"gaps": gaps, "comparator": comp, "verdict": v})
        print(f"wrote {args.json_out}")
    return n


if __name__ == "__main__":
    raise SystemExit(main())
