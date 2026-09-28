"""E280 -- the audit series' positive control: a paper claim that enumerates its own population, and checks out.

Five fires have found the paper stating things the corpus no longer supports: a number superseded by a later finding
(`e268`), an existence premise contradicted by three artifacts (`e270`), counts over denominators that grew 2.45x and
6.44x (`e277`), an extremum over a population named only as "on disk" (`e278`) and a universal over an epoch of the
line (`e279`). **A check that only ever fires is uninterpretable** -- `e97`'s own docstring says so and carries a known
positive for that reason -- so the series needs a claim whose population its sentence fully enumerates.

There is one, and it is complete:

    Twelve seeds and all 66 pairs, 21-point chords at the first and last checkpoints, pre-registered before the run:
    every one of the 132 pair-checkpoints has a fit-task barrier below 25% of chance, with min 0.0108, median 0.0361
    and max 0.1252

**The sentence gives its enumerator**: twelve seeds, **66 pairs**, the **first and last** checkpoints, i.e. 132 rows.
`runs/e124_barrier_12seeds.json` carries exactly that population in `fit_tasks`, with a `barrier_over_chance` per row
and its own `distributions.fit` summary beside it -- so the claim, the population and the artifact's own arithmetic can
be checked against each other.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **C1 -- the population is what the sentence says it is.** **132** rows, **66** distinct seed pairs, checkpoints
  **0 and 2** -- the first and the last. **Falsifier**: a different row count, pair count or checkpoint set.
- **C2 -- and its three quoted numbers are the artifact's.** Recomputed from the rows: min **0.0108**, median
  **0.0361**, max **0.1252** at the precision the sentence quotes. **Falsifier**: any number that does not match.
- **C3 -- and the universal holds, with the artifact agreeing with itself.** Every one of the 132 is below **25%** of
  chance -- the largest is **0.1252** -- and the artifact's own `distributions.fit` summary (n, min, median, max)
  equals a recomputation from its own rows. **Falsifier**: a row at or above 0.25, or the summary disagreeing with its
  rows.

**Why this is the control and not a fifth finding.** The five stale statements were each about a population the
sentence did **not** define -- a count, an "on disk", an epoch -- so a broken checker and a genuine staleness would
look alike. Here the sentence defines its population, the population is complete, and the claim is confirmed to the
last quoted digit: **the checker can pass, which is what makes its failures mean something.** The contrast is also the
series' own conclusion in one line: **a claim is checkable exactly to the extent that it names its enumerator.**

**What it cannot do**: it checks the claim against the artifact and the artifact against itself, not the artifact
against a re-run, so a defect shared by the run and its own summary is invisible; `barrier_over_chance` is the field
read, and the sentence's "of chance" is taken to be that field rather than re-derived; the sentence's "pre-registered
before the run" is a claim about a document and not about the corpus, and nothing here checks it; and the control is
one claim, so it establishes that the checker *can* pass and not what fraction of the paper it passes.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

ARTIFACT = "runs/e124_barrier_12seeds.json"
#: The sentence's own enumerator, and the three numbers it quotes at the precision it quotes them.
WANTED_ROWS, WANTED_PAIRS = 132, 66
WANTED_CHECKPOINTS = [0, 2]
QUOTED = {"min": 0.0108, "median": 0.0361, "max": 0.1252}
#: The universal's bar, as the sentence states it.
BAR = 0.25
CLAIMS = (
    ("C1", "the population is what the sentence says it is",
     "The artifact carries 132 rows, 66 distinct seed pairs and the first and last checkpoints",
     "falsifier: a different row count, pair count or checkpoint set"),
    ("C2", "and its three quoted numbers are the artifact's",
     "A recomputation from the rows gives 0.0108, 0.0361 and 0.1252 at the precision quoted",
     "falsifier: any number that does not match"),
    ("C3", "and the universal holds, with the artifact agreeing with itself",
     "Every row is below 25% of chance and the artifact's own summary equals a recomputation from its own rows",
     "falsifier: a row at or above the bar, or a summary disagreeing with its rows"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def reading(d: dict) -> dict:
    rows = d["fit_tasks"]
    vals = sorted(r["barrier_over_chance"] for r in rows)
    return {"n": len(rows), "pairs": len({(r["seed_a"], r["seed_b"]) for r in rows}),
            "checkpoints": sorted({r["checkpoint"] for r in rows}),
            "min": vals[0], "median": statistics.median(vals), "max": vals[-1],
            "n_below_bar": sum(1 for v in vals if v < BAR), "vals": vals,
            "summary": {k: d["distributions"]["fit"][k] for k in ("n", "min", "median", "max")}}


def judge(r: dict | None) -> list[dict]:
    if r is None:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the artifact is absent"} for c in CLAIMS]
    out: list[dict] = []

    ok1 = r["n"] == WANTED_ROWS and r["pairs"] == WANTED_PAIRS and r["checkpoints"] == WANTED_CHECKPOINTS
    out.append({"id": "C1", "measured": f"{r['n']} rows, {r['pairs']} distinct seed pairs, checkpoints "
                                        f"{r['checkpoints']} -- the sentence says {WANTED_ROWS} rows, "
                                        f"{WANTED_PAIRS} pairs, the first and the last",
                "verdict": "MET -- the population is complete and enumerated as the sentence says" if ok1 else
                           "FALSIFIER FIRED -- the population differs from the sentence's enumerator"})

    got = {"min": round(r["min"], 4), "median": round(r["median"], 4), "max": round(r["max"], 4)}
    off = {k: (got[k], v) for k, v in QUOTED.items() if abs(got[k] - v) > 5e-5}
    out.append({"id": "C2", "measured": f"recomputed min {got['min']:.4f}, median {got['median']:.4f}, max "
                                        f"{got['max']:.4f} against the sentence's {QUOTED}",
                "verdict": "MET -- the quoted numbers are the artifact's, to the precision quoted" if not off else
                           f"FALSIFIER FIRED -- {off}"})

    summary_ok = (r["summary"]["n"] == r["n"] and abs(r["summary"]["min"] - r["min"]) < 1e-12
                  and abs(r["summary"]["median"] - r["median"]) < 1e-12 and abs(r["summary"]["max"] - r["max"]) < 1e-12)
    ok3 = r["n_below_bar"] == r["n"] and summary_ok
    out.append({"id": "C3", "measured": f"{r['n_below_bar']} of {r['n']} rows below {BAR:g} of chance, the largest "
                                        f"{r['max']:.4f}; the artifact's own summary equals the recomputation: "
                                        f"{summary_ok}",
                "verdict": "MET -- the universal holds and the artifact agrees with itself" if ok3 else
                           "FALSIFIER FIRED -- a row is above the bar, or the summary disagrees with its rows"})
    return out


def report(r: dict | None) -> int:
    print("== the claim, and the population its sentence enumerates ==")
    print(f"   the artifact: {ARTIFACT}")
    if r is not None:
        print(f"   {r['n']} rows, {r['pairs']} pairs, checkpoints {r['checkpoints']}")
        print(f"   the recomputation: min {r['min']:.4f}, median {r['median']:.4f}, max {r['max']:.4f}")
        print(f"   the sentence:      min {QUOTED['min']:.4f}, median {QUOTED['median']:.4f}, max {QUOTED['max']:.4f}")
        print(f"   the artifact's own summary: {r['summary']}")
        print(f"   rows below {BAR:g} of chance: {r['n_below_bar']} of {r['n']}")

    print("\n== the registered claims, C1-C3 ==")
    j = judge(r)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the five stale statements this series found were each about a population their sentence did not")
    print("    define -- a count, an 'on disk', an epoch -- so here the sentence defines its population, the population")
    print("    is complete, and the claim is confirmed: a checker that can pass is what makes its failures mean")
    print("    something)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    d = load(ARTIFACT)
    r = reading(d) if d is not None and "fit_tasks" in d else None
    if args.json_out:
        write_json(args.json_out, {"artifact": ARTIFACT, "wanted": {"rows": WANTED_ROWS, "pairs": WANTED_PAIRS,
                                                                    "checkpoints": WANTED_CHECKPOINTS},
                                   "quoted": QUOTED, "bar": BAR,
                                   "reading": ({k: v for k, v in r.items() if k != "vals"} if r else None),
                                   "claims": judge(r)})
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
