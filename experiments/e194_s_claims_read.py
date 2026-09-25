"""S1-S4 -- the four SHAPE claims registered for `e193`'s last level, judged in one command.

Registered 2026-09-25 in the plan's row for `e193`, **before level 0.75 landed**: S1 and S2 off the near/far split the
midpoint revealed, S3 off the two lines' distant-pair components, S4 off the accuracy account's interior. Written
before the artifact for the reason `e190` was written before `e178`'s: so that the verdict is one command rather than
a fresh argument, and so that a claim whose level has not landed is **refused** rather than given a number.

    python -m experiments.e194_s_claims_read                       # the registered three levels
    python -m experiments.e194_s_claims_read --dose runs/e193_r32_overlap075_methods_40reps.json

## What it reads, and what it refuses

Every claim names an **achieved overlap** and a **quantity on it**, never a target overlap -- the x-axis is measured
first (`e191`'s `ACHIEVED_OVERLAP`) and a claim stated at a target would move if the circuit or the seed set changed.
A claim whose levels are absent, or whose arm was refused a `progress_fraction` by the reader that owns it (the
penalised arms have no 0 -> 1 change to divide by), prints `REFUSED` with the reason and is counted in the exit code.

The three-valued verdict is the registrations' own: each names a bar and a falsifier, and a measurement that clears
neither is reported as **between them** rather than forced into one. S1 also names a null band, which is checked.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from experiments.e188_overlap_contrast import dose_read as accuracy_read
from experiments.e191_interference_across_lines import dose_read as interference_read

LEVELS = [Path(f"runs/e193_r32_overlap{n}_methods_40reps.json") for n in (25, 50, 75)]

#: Where the four claims are registered, so a verdict names its source and a reader can check the bar's sentence.
REGISTRATION = "docs/findings/2026-09-25-at-the-midpoint-p1-and-p2-fail-and-the-far-term-is-82-percent-done.md"

#: (id, achieved overlap, quantity key, comparison, bar, falsifier comparison, falsifier, null spec, what it means)
#: The null spec is `(keys, lo, hi)` and is checked against the keys it **names** rather than against the claim's own
#: quantity: S1's null is *"both in 30-60"*, a statement about each term, and the first version applied the band to
#: their difference -- a defect in the reader that no live print would have shown.
CLAIMS = (
    ("S1", 0.6000, "far_minus_near", ">=", 40.0, "<", 15.0, (("near", "far"), 30.0, 60.0),
     "the distant-pair term's progress exceeds the adjacent-pair term's, in points"),
    ("S2", 0.6000, "near", "<", 50.0, ">=", 50.0, None,
     "the adjacent-pair term is still back-loaded, in % of its own 0 -> 1 change"),
    ("S3", 0.6000, "far_minus_analytic", ">=", 15.0, "<=", 0.0, None,
     "the network's distant-pair progress exceeds `e7`'s far progress there, in points"),
    ("S4", 0.6000, "accuracy_progress", "<", 176.6, ">=", 176.6, None,
     "the accuracy cost comes back down from the midpoint's peak, in % of its own 0 -> 1 change"),
)

#: The extrapolations each registration wrote down before the run, printed beside the measurement rather than
#: silently remembered. Absent for S1, whose bar is a separation and not a predicted value.
REGISTERED_EXTRAPOLATION = {"S2": "constant slope 30.8%, constant ratio to the analytic line 22.6%",
                            "S3": "`e7`'s own far progress at achieved 0.6000 is 52.16%",
                            "S4": "the endpoint's own 100% and the midpoint's 176.6%"}


def compare(value: float, op: str, bar: float) -> bool:
    return {">=": value >= bar, "<": value < bar, "<=": value <= bar, ">": value > bar}[op]


def judge(values: dict[str, float], key: str, op: str, bar: float, fals_op: str, fals: float,
          null_spec: tuple[tuple[str, ...], float, float] | None) -> str:
    """The registration's own verdicts, in its own order: the bar, then the falsifier, then the null it named."""
    value = values[key]
    if compare(value, op, bar):
        return "MET"
    if compare(value, fals_op, fals):
        return "FALSIFIER FIRED"
    if null_spec:
        keys, lo, hi = null_spec
        if all(k in values for k in keys) and all(lo <= values[k] <= hi for k in keys):
            return "the registered null"
    return "between the bar and the falsifier"


def measure(levels: list[Path]) -> dict:
    """Every quantity the four claims name, per achieved overlap, from the two readers that own them.

    A value is present only when the reader that owns it produced a `progress_fraction` for the `naive` arm at that
    exact achieved overlap; anything else is absent and the claim that needs it is refused.
    """
    ints = interference_read(levels)
    accs = accuracy_read(levels)
    out: dict[float, dict[str, float]] = {}
    for row in ints["levels"]:
        if row.get("status"):
            continue
        ach = row.get("achieved_overlap")
        arm = (row.get("arms") or {}).get("naive") or {}
        prog = arm.get("progress_fraction")
        if ach is None or not prog:
            continue
        vals = {"near": 100 * prog["near"], "far": 100 * prog["far"],
                "far_minus_near": 100 * (prog["far"] - prog["near"])}
        an_far = (ints.get("analytic_progress_far") or {}).get(ach)
        if an_far is not None:
            vals["analytic_far"] = 100 * an_far
            vals["far_minus_analytic"] = 100 * (prog["far"] - an_far)
        out[ach] = vals
    for row in accs["levels"]:
        if row.get("status"):
            continue
        ach = row.get("achieved_overlap")
        arm = (row.get("arms") or {}).get("naive") or {}
        prog = arm.get("progress_fraction")
        if ach is None or not prog:
            continue
        out.setdefault(ach, {})["accuracy_progress"] = 100 * prog["accuracy"]
    return out


def report(values: dict) -> int:
    print(f"   == S1-S4: the registered shape claims, judged at the achieved overlap each one names ==")
    print(f"   (registered in {REGISTRATION})")
    refused = 0
    for cid, ach, key, op, bar, fals_op, fals, null_spec, meaning in CLAIMS:
        vals = values.get(ach)
        if vals is None:
            print(f"        {cid}: REFUSED -- no measured progress at achieved {ach}")
            refused += 1
            continue
        if key not in vals:
            print(f"        {cid}: REFUSED -- {key} is absent at achieved {ach} "
                  f"(the arm was refused the fraction, or the level is not written yet)")
            refused += 1
            continue
        value = vals[key]
        verdict = judge(vals, key, op, bar, fals_op, fals, null_spec)
        side = {k: f"{v:.1f}" for k, v in sorted(vals.items())}
        print(f"        {cid}: {value:8.2f}  {op} {bar:g} -> {verdict}")
        print(f"             {meaning}; falsifier {fals_op} {fals:g}")
        if cid in REGISTERED_EXTRAPOLATION:
            print(f"             registered before the run: {REGISTERED_EXTRAPOLATION[cid]}")
        print(f"             at achieved {ach}: {side}")
    return refused


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dose", action="append", default=None,
                   help="an artifact to read; repeatable. Default: the three registered levels.")
    a = p.parse_args(argv)
    values = measure([Path(x) for x in a.dose] if a.dose else LEVELS)
    missing = report(values)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
