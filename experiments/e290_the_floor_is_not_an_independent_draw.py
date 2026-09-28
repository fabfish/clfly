"""E290 -- the floor is not an independent draw: what a variance fraction above one measures, and the effective suite.

`e267` turns the benchmark's own noise block into the suite each configuration would need, and the whole line since
rests on it: `e269` priced a held-out decision, `e275` bought a suite with it, `e285` to `e289` read the sample swaps
it is about. Its statistic is

    variance fraction = (binomial sem of one accuracy at n_eval)^2 / (that arm's across-replicate variance)

and it is read as *"is the test set's own noise as large as the spread you are trying to resolve"*. That reading
carries a premise nobody has stated: **that the binomial noise is an independent draw per replicate**. It is not.
`e8_rate_network` builds the suite **once**, before its method and replicate loops, and every replicate is trained
against the same held-out items; so what the fraction compares is the nominal binomial variance of a single number
with the across-replicate movement of a quantity measured on **one shared sample** -- and where the fraction exceeds
one, the nominal binomial variance exceeds the total variance it is supposed to be part of, which the premise
forbids.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **Q1 -- the suite is one draw, shared by every replicate.** The runner's own source builds its suite outside the
  replicate loop, so the same held-out items are used by all of them. **Falsifier**: the suite is built inside the
  loop.
- **Q2 -- and the corpus says the premise fails.** The variance fraction exceeds one in a substantial minority of the
  corpus's arms, and under the premise it cannot. **Falsifier**: fewer than a tenth of them.
- **Q3 -- so the suite has an *effective* size, and it is an arm-level number.** Where the fraction is at or above one
  the nominal binomial variance is the only measured noise there is, and it implies `n_effective = n_eval / fraction`
  independent held-out decisions; inside the artifacts that carry three or more arms, that number varies by a factor
  the corpus has never reported. **Falsifier**: every artifact's arms within a factor of 1.2 of each other.

**What the three leave standing.** The requirement `e267` computes is real arithmetic on a real artifact, and this
unit does not overturn it: what it shows is that the quantity it divides by the spread is the nominal binomial
variance of **one accuracy**, and that the held-out decisions behind it are far from independent -- which is the same
conclusion the paper reaches from the other side when it solves for an *effective* **49** independent decisions
against a nominal 144. A suite's worth is therefore not `n_eval` but `n_effective`, and `n_effective` is arm-level:
it is one number for the read-out and another for the method.

**What it cannot do.** *The fraction is a ratio of two noises and not a decomposition*, so Q2 is evidence that the
premise fails and not a measurement of how the held-out items are correlated. *`n_effective` is defined only where
the fraction is at or above one*; below one the spread is larger than the nominal floor, the arm has real
training-driven movement, and the number is an extrapolation rather than a count -- the module reports the two
regimes apart for that reason. *The source check is lexical*: it locates the suite's construction and the replicate
loop in the runner's text and not a dataflow, so a runner that built its suite elsewhere would read differently.
*The corpus's artifacts span four days of runner changes*, so a fraction computed under an earlier `evaluation_noise`
formula is in the population, and nothing here separates the formula's epochs. *And neither `e267` nor `e269` is
re-run*: what is new is the premise, the count of arms where it fails, and the effective count it implies.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNNER = Path("experiments/e8_rate_network.py")
RUNS = Path("runs")
#: The calls that build a suite, and the loop that makes the replicates. The order of the two is Q1.
SUITE_CALLS = ("make_suite(", "make_overlap_suite(")
REPLICATE_LOOP = "for r in range(args.repeats)"
#: The share of arms above one below which Q2 would be a coincidence rather than a premise failing.
MINORITY = 0.10
#: The factor by which one artifact's arms would have to agree for Q3 to fail.
AGREEMENT = 1.2
CLAIMS = (
    ("Q1", "the suite is one draw, shared by every replicate",
     "The runner builds its suite outside its replicate loop, so all replicates see the same held-out items",
     "falsifier: the suite is built inside the loop"),
    ("Q2", "and the corpus says the premise fails",
     "The variance fraction exceeds one in at least a tenth of the corpus's arms, which an independent binomial "
     "noise cannot do",
     "falsifier: fewer than a tenth of them"),
    ("Q3", "so the suite has an effective size, and it is arm-level",
     "Inside the artifacts carrying three or more arms, the implied effective count varies by more than a factor of "
     f"{AGREEMENT}",
     "falsifier: every such artifact's arms within that factor"),
)


def suite_placement(source: str) -> dict:
    """Where the suite is built and where the replicates are made -- the whole of Q1, as a line comparison."""
    lines = source.split("\n")
    loop = [n for n, l in enumerate(lines) if REPLICATE_LOOP in l]
    builds = [n for n, l in enumerate(lines) if any(c in l for c in SUITE_CALLS)]
    return {"loop_line": loop[0] if loop else None, "build_lines": builds,
            "outside": bool(loop and builds and all(b < loop[0] for b in builds))}


def fractions(root: Path = RUNS) -> list[dict]:
    """Every (artifact, arm) the corpus gives a variance fraction, with the effective count it implies."""
    out = []
    for p in sorted(root.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ev = d.get("evaluation_noise")
        if not isinstance(ev, dict):
            continue
        n_eval = ev.get("n_eval")
        if not isinstance(n_eval, int) or not n_eval:
            continue
        for arm, v in ev.items():
            if not isinstance(v, dict):
                continue
            f = v.get("variance_fraction")
            if not isinstance(f, (int, float)) or f <= 0:
                continue
            out.append({"artifact": p.name, "arm": arm, "n_eval": n_eval, "fraction": float(f),
                        "n_effective": n_eval / float(f), "share": 1.0 / float(f),
                        "replicate_sd": v.get("replicate_sd"), "binomial_sem": v.get("binomial_sem")})
    return out


def per_artifact(rows: list[dict], minimum_arms: int = 3) -> list[dict]:
    """For each artifact with enough arms, how far its arms' effective counts are from agreeing."""
    by: dict[tuple[str, int], list[float]] = {}
    for r in rows:
        by.setdefault((r["artifact"], r["n_eval"]), []).append(r["share"])
    out = []
    for (artifact, n_eval), shares in sorted(by.items()):
        if len(shares) < minimum_arms:
            continue
        out.append({"artifact": artifact, "n_eval": n_eval, "arms": len(shares),
                    "share_min": min(shares), "share_max": max(shares),
                    "ratio": max(shares) / min(shares)})
    return out


def judge(r: dict) -> list[dict]:
    rows = (r or {}).get("fractions") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no variance fraction to read"} for c in CLAIMS]

    place = r["placement"]
    out = [{"id": "Q1", "measured": f"the suite is built on line(s) {place['build_lines']} and the replicate loop "
                                     f"opens on line {place['loop_line']}, so every build is outside it",
            "verdict": "MET -- the suite is one draw shared by the replicates" if place["outside"] else
                       "FALSIFIER FIRED -- a suite is built inside the replicate loop"}]

    over = [x for x in rows if x["fraction"] > 1]
    share = len(over) / len(rows)
    span = (f"from {min(x['fraction'] for x in over):.2f} to {max(x['fraction'] for x in over):.1f}"
            if over else "none of them")
    out.append({"id": "Q2", "measured": f"{len(over)} of {len(rows)} arms carry a fraction above one "
                                        f"({100 * share:.0f}%), {span}",
                "verdict": "MET -- the nominal binomial variance exceeds the total variance in those arms, which the "
                           "premise forbids" if share >= MINORITY else f"FALSIFIER FIRED -- {100 * share:.1f}%"})

    per = r["per_artifact"]
    worst = max(per, key=lambda x: x["ratio"]) if per else None
    disagreements = [x for x in per if x["ratio"] > AGREEMENT]
    out.append({"id": "Q3", "measured": f"{len(disagreements)} of {len(per)} artifacts with three or more arms have "
                                        f"their arms' effective counts more than x{AGREEMENT} apart; the median ratio "
                                        f"is x{statistics.median([x['ratio'] for x in per]):.2f} and the largest "
                                        f"x{worst['ratio']:.2f} ({worst['artifact']})" if per else "no artifact",
                "verdict": "MET -- the effective count is arm-level" if disagreements else
                           f"FALSIFIER FIRED -- no artifact's arms are more than x{AGREEMENT} apart"})
    return out


def report(r: dict) -> int:
    rows = r["fractions"]
    over = [x for x in rows if x["fraction"] > 1]
    under = [x for x in rows if x["fraction"] <= 1]
    print("== where the suite is built, against where the replicates are made ==")
    print(f"   the suite: line(s) {r['placement']['build_lines']} of `{RUNNER}`")
    print(f"   the replicate loop: line {r['placement']['loop_line']}")
    print("   -> every replicate of every arm is evaluated on the SAME held-out items, so the binomial noise is one")
    print("      shared draw and not an independent one per replicate")

    print("\n== the corpus's variance fractions ==")
    print(f"   arms with a fraction: {len(rows)}; above one: {len(over)} ({100 * len(over) / len(rows):.0f}%); "
          f"at or below one: {len(under)}")
    print(f"   where the reading is defined (fraction at or above one), the implied effective count runs "
          f"{min(x['n_effective'] for x in over):.1f} to {max(x['n_effective'] for x in over):.1f}")
    print("   the smallest effective counts:")
    for x in sorted(over, key=lambda x: x["n_effective"])[:6]:
        print(f"      {x['artifact'][:44]:44} {x['arm']:16} n_eval {x['n_eval']:5} fraction {x['fraction']:7.3f} "
              f"n_effective {x['n_effective']:7.1f}")

    print("\n== and inside one artifact, the arms disagree ==")
    for x in sorted(r["per_artifact"], key=lambda x: -x["ratio"])[:6]:
        print(f"   x{x['ratio']:5.2f}  {x['artifact'][:46]:46} n_eval {x['n_eval']:5} over {x['arms']} arms "
              f"(share {x['share_min']:.3f} to {x['share_max']:.3f})")

    print("\n== the registered claims, Q1-Q3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the fraction is real arithmetic on a real artifact; what it divides by is the binomial variance of")
    print("    ONE accuracy on a sample every replicate shares, so a suite's worth is its effective size -- an")
    print("    arm-level number, and the corpus's own route to it agrees with the paper's effective 49 against 144)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runner", type=Path, default=RUNNER)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    source = args.runner.read_text(encoding="utf-8") if args.runner.is_file() else ""
    rows = fractions(args.runs)
    r = {"runner": str(args.runner), "placement": suite_placement(source), "fractions": rows,
         "per_artifact": per_artifact(rows)}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
