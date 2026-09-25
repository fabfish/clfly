"""The S claims -- the shape AND COST claims registered on `e193`'s overlap axis, judged in one command.

Registered 2026-09-25 in the plan's row for `e193`, **before level 0.75 landed**: S1 and S2 off the near/far split the
midpoint revealed, S3 off the two lines' distant-pair components, S4 off the accuracy account's interior, and S5 off
the decomposition of the accuracy cost into *learned worse* and *forgot more*. Written before the artifact for the
reason `e190` was written before `e178`'s: so that the verdict is one command rather than a fresh argument, and so
that a claim whose level has not landed is **refused** rather than given a number.

    python -m experiments.e194_s_claims_read                       # the registered three levels
    python -m experiments.e194_s_claims_read --dose runs/e193_r32_overlap075_methods_40reps.json

## What it reads, and what it refuses

Every claim names an **achieved overlap** and a **quantity on it**, never a target overlap -- the x-axis is measured
first (`e191`'s `ACHIEVED_OVERLAP`) and a claim stated at a target would move if the circuit or the seed set changed.
A claim whose levels are absent, or whose arm was refused a `progress_fraction` by the reader that owns it (the
penalised arms have no 0 -> 1 change to divide by), prints `REFUSED` with the reason and is counted in the exit code.

The three-valued verdict is the registrations' own: each names a bar and a falsifier, and a measurement that clears
neither is reported as **between them** rather than forced into one. S1 also names a null.

`measure()` additionally carries the **cost decomposition** (`learned_older`, `forgetting` and their sems) that S5
reads. It is taken against `e116`, the disjoint baseline the registered P1's bar is half of, and the pairing is
checkable: `readout` and `seed0` are identical across the four artifacts, and the task supports are not recorded at
all -- they are reconstructed from the target overlap, which is the limitation the registration itself names.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from experiments.e151_pertask_contrast_audit import paired
from experiments.e188_overlap_contrast import ACHIEVED_OVERLAP, dose_read as accuracy_read, load
from experiments.e191_interference_across_lines import dose_read as interference_read

#: The three registered levels, named the way the LAUNCH wrote them: `n=$(echo $ov | tr -d '.')` turns 0.25 into
#: `025`, 0.50 into `050` and 0.75 into `075`. The registration's prose writes them `overlap{25,50,75}`, which reads
#: as the unpadded names, and four files copied that spelling -- so the reads pointed at paths that do not exist and
#: reported "not written yet", which is exactly the state they were written to describe. A path that does not resolve
#: makes a reader refuse, and a refusal looks like an answer.
LEVELS = [Path(f"runs/e193_r32_overlap{n:03d}_methods_40reps.json") for n in (25, 50, 75)]

#: The disjoint baseline the cost decomposition is against. The registered P1's bar is half of this artifact's 0 -> 1
#: forgetting change, so the decomposition and the bar are read off the same pair of artifacts.
DECOMPOSITION_BASELINE = Path("runs/e116_r32_40reps.json")

#: Where the claims are registered, so a verdict names its source and a reader can check the bar's sentence.
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
    ("S5", 0.6000, "learned_older", ">", -0.0100, "<=", -0.0200, None,
     "how well the OLDER tasks were learned, against the disjoint baseline -- the component the midpoint's cost "
     "came from, so a value here says whether that mechanism persists"),
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
    """Every quantity the claims name, per achieved overlap, from the readers that own them.

    A value is present only when the reader that owns it produced a `progress_fraction` for the `naive` arm at that
    exact achieved overlap; anything else is absent and the claim that needs it is refused.

    The cost decomposition is the exception: it needs no fraction, only the two per-task series the runner records,
    so it is present whenever the level and the disjoint baseline both carry a `naive` arm. The identity it rests on
    is exact and is checked in the tests: `mean(final_per_task[:-1]) == mean(learned[:-1]) - mean_forgetting`, so the
    accuracy cost *is* the sum of a learning term and a retention term and the two can be read off separately.
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
    if not Path(DECOMPOSITION_BASELINE).is_file():
        return out
    base = load(DECOMPOSITION_BASELINE)["methods"]["naive"]["replicates"]
    b_learned = np.array([float(np.mean(r["learned"][:-1])) for r in base])
    b_forget = np.array([r["mean_forgetting"] for r in base])
    for path in levels:
        if not Path(path).is_file():
            continue
        d = load(path)
        if "naive" not in (d.get("methods") or {}):
            continue
        ach = ACHIEVED_OVERLAP.get((d.get("config") or {}).get("input_overlap"))
        if ach is None:
            continue
        reps = d["methods"]["naive"]["replicates"]
        for key, series, b in (("learned_older", [float(np.mean(r["learned"][:-1])) for r in reps], b_learned),
                               ("forgetting_cost", [r["mean_forgetting"] for r in reps], b_forget)):
            p = paired(np.array(series), b)
            vals = out.setdefault(ach, {})
            vals[key] = p["change"]
            vals[key + "_sem"] = p["sem"]
            vals[key + "_sigma"] = abs(p["change"]) / p["sem"] if p["sem"] else 0.0
    return out


def report(values: dict) -> int:
    print(f"   == the S claims: the registered shape and cost claims, judged at the achieved overlap each one names ==")
    print(f"   (registered in {REGISTRATION})")
    # Which levels RESOLVED is printed before any verdict, because a claim's refusal has two causes -- the artifact is
    # not written yet, or the path does not name it -- and the first version's output was identical for both. An
    # empty list here is a statement about the paths rather than about the claims.
    found = sorted(values)
    print("   levels found: " + (", ".join(f"achieved {a}" for a in found) if found
                                 else "NONE -- check the artifact names before reading any refusal below"))
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
        side = {k: f"{v:.4f}" if k.startswith("learned") or "forgetting" in k else f"{v:.1f}"
                for k, v in sorted(vals.items()) if not k.endswith(("_sem", "_sigma"))}
        print(f"        {cid}: {value:8.4f}  {op} {bar:g} -> {verdict}")
        print(f"             {meaning}; falsifier {fals_op} {fals:g}")
        if cid in REGISTERED_EXTRAPOLATION:
            print(f"             registered before the run: {REGISTERED_EXTRAPOLATION[cid]}")
        if key + "_sigma" in vals:
            print(f"             resolution: {value:+.4f} +/- {vals[key + '_sem']:.4f} = "
                  f"{vals[key + '_sigma']:.2f}s against the disjoint baseline")
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
