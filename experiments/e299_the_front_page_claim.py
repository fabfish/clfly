"""E299 -- the front-page claim: an absence of forgetting, and the 64 arms of 294 that support one.

The repository's front page opens with two claims of **absence**: *"One brain, many behaviours, no catastrophic
forgetting"* and *"sequentially, without its olfactory memories being erased by its navigation lessons"*. The audits in
this line have read the paper, the programme table and the findings; the README has never been read against the
corpus, and it is the sentence a visitor reads first.

An absence is a *bound* and not a difference, so it is checkable in a way the corpus is unusually well set up for:
every arm's `mean_forgetting` has a mean and a sem over its own replicates, so each arm either resolves away from zero
or fails to, and the arms that fail to are the arms where an absence is what the corpus measured. This unit reads the
README for absence claims and the corpus for the arms that support them.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **F1 -- the front page claims an absence.** **Falsifier**: it makes no absence claim about forgetting.
- **F2 -- and the corpus supports an absence for a named minority.** A substantial share of the corpus's arms have a
  forgetting indistinguishable from zero at two sigma, including arms at forty replicates whose bound is a few per
  cent of the baseline's. **Falsifier**: no arm is indistinguishable from zero.
- **F3 -- and it refutes the absence as a general claim.** Most arms resolve away from zero, and the largest is tens
  of sigma. **Falsifier**: most arms are indistinguishable from zero.

**What the three add up to.** The front page's sentence is **true of a minority and false as written**: the corpus
contains 64 of 294 arms where forgetting is not distinguishable from zero -- three of them at forty replicates with a
bound under ±0.004, against a baseline whose median is +0.073 -- and 230 arms where it is, up to 25 sigma. So the
absence is a *result about particular arms* (which this unit names) and not a property of the claim the front page
makes about a fly. The correction applied in this fire scopes the two sentences rather than deleting them.

**What it cannot do.** *Zero is not absence*: an arm indistinguishable from zero at two sigma is an arm whose
forgetting is smaller than its own noise, which for a well-run but noisy configuration can be true of a real effect of
0.01 -- so F2's count is a statement about resolution and not about a fly remembering perfectly. *The arms are not
independent*: the same configuration recurs, so 64 of 294 over-counts the distinct configurations in the way `e290`
measured for the variance fraction. *`mean_forgetting` is a mean over the first `T - 1` tasks*, so an arm can be
indistinguishable from zero while one of its tasks forgets and another does not -- `e151`'s per-task decomposition is
the instrument for that and this unit does not use it. *The two-sigma line is a convention*: at one sigma the count
rises and at three it falls, and the arms named are the ones inside whichever line is drawn. *And the README's claim
is about a *fly*, while every number here is about a connectome-constrained network on four-way classification tasks*
-- the distance between the two is the whole of the modelling question and nothing here closes it.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json

README = Path("README.md")
RUNS = Path("runs")
#: A sentence claims an absence when it carries one of these and a forgetting-or-memory subject. `never` is
#: deliberately absent: the README uses it for a different claim (*"never for forgetting curves"*), which is about the
#: literature and not about a fly, and admitting it matched two bullet fragments as if they were absence claims.
ABSENCE = ("no catastrophic", "without", "cannot forget", "does not forget", "not erased")
SUBJECT = ("forgetting", "memories", "memory")
RESOLVED = 2.0
MIN_REPLICATES = 3
CLAIMS = (
    ("F1", "the front page claims an absence",
     "The README carries a sentence claiming an absence of forgetting",
     "falsifier: it makes no absence claim about forgetting"),
    ("F2", "and the corpus supports an absence for a named minority",
     "A substantial share of the corpus's arms have a forgetting indistinguishable from zero at two sigma, and at "
     "least one of them has forty replicates",
     "falsifier: no arm is indistinguishable from zero"),
    ("F3", "and it refutes the absence as a general claim",
     "Most arms resolve away from zero",
     "falsifier: most arms are indistinguishable from zero"),
)


def absence_claims(text: str) -> list[dict]:
    """The README's sentences that claim an absence about forgetting or memory."""
    out = []
    for n, para in enumerate(re.split(r"\n\s*\n", text)):
        for s in re.split(r"(?<=[.:;])\s+(?=[A-Z(])", para):
            flat = re.sub(r"\s+", " ", s).strip()
            low = flat.lower()
            cues = [c for c in ABSENCE if c in low]
            subjects = [x for x in SUBJECT if x in low]
            if cues and subjects:
                out.append({"sentence": n, "cues": cues, "subjects": subjects, "text": flat,
                            # a description and not a claim: does the sentence now carry the scope this fire adds?
                            "scoped": "scoped 2026-09-29" in low or "docs/findings/" in flat})
    return out


def zeros(root: Path = RUNS, minimum: int = MIN_REPLICATES, collapse: bool = True) -> list[dict]:
    """Every arm with a forgetting and enough replicates, with its distance from zero in sigmas."""
    out = []
    # `e301`: a second execution of an experiment the corpus already holds is not a second experiment, and a
    # census of the corpus's experiments is not a census of its files.
    skip = corpus.repeat_paths(root) if collapse else set()
    for p in sorted(root.glob("*.json")):
        if p.name in skip:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        meth = d.get("methods")
        if not isinstance(meth, dict):
            continue
        for arm, v in sorted(meth.items()):
            if not isinstance(v, dict) or not isinstance(v.get("replicates"), list):
                continue
            xs = [r.get("mean_forgetting") for r in v["replicates"]
                  if isinstance(r.get("mean_forgetting"), (int, float))]
            if len(xs) < minimum:
                continue
            mean = statistics.fmean(xs)
            sem = statistics.stdev(xs) / math.sqrt(len(xs))
            if not sem or sem < 1e-12:
                continue
            out.append({"artifact": p.name, "arm": arm, "n": len(xs), "mean": mean, "sem": sem,
                        "sigma": abs(mean) / sem, "at_zero": abs(mean) / sem < RESOLVED})
    return out


def judge(r: dict) -> list[dict]:
    rows = (r or {}).get("arms") or []
    claims = (r or {}).get("absence_claims") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm carries a forgetting"} for c in CLAIMS]

    out = [{"id": "F1", "measured": f"{len(claims)} absence claim(s) on the front page: "
                                     + "; ".join(f"[{x['sentence']}] {x['text'][:110]}" for x in claims[:2])
                                     if claims else "none",
            "verdict": "MET -- the front page states an absence" if claims else
                       "FALSIFIER FIRED -- no absence claim found"}]

    at_zero = [x for x in rows if x["at_zero"]]
    big = [x for x in at_zero if x["n"] >= 40]
    out.append({"id": "F2", "measured": f"{len(at_zero)} of {len(rows)} arms "
                                        f"({100 * len(at_zero) / len(rows):.0f}%) have a forgetting "
                                        f"indistinguishable from zero at two sigma; {len(big)} of them have forty or "
                                        f"more replicates, the smallest bound being "
                                        f"+-{min((x['sem'] for x in big), default=float('nan')):.4f}",
                "verdict": "MET -- the absent forgetting is a measured result for a minority of arms" if big else
                           f"FALSIFIER FIRED -- none of the {len(at_zero)} is at forty replicates"})

    resolved = [x for x in rows if not x["at_zero"]]
    largest = max(rows, key=lambda x: x["sigma"])
    out.append({"id": "F3", "measured": f"{len(resolved)} of {len(rows)} arms resolve away from zero, the largest at "
                                        f"{largest['sigma']:.2f} sigma ({largest['artifact'][:34]}, "
                                        f"{largest['arm']})",
                "verdict": "MET -- the absence is refuted as a general claim" if len(resolved) * 2 > len(rows) else
                           f"FALSIFIER FIRED -- only {len(resolved)} of {len(rows)} resolve"})
    return out


def report(r: dict) -> int:
    print("== the front page's absence claims ==")
    for x in r["absence_claims"]:
        print(f"   [{x['sentence']}] cues {x['cues']} subjects {x['subjects']} scoped {x['scoped']}")
        print(f"        {x['text'][:200]}")
    if not r["absence_claims"]:
        print("   none")
    scoped = [x for x in r["absence_claims"] if x["scoped"]]
    print(f"   {len(scoped)} of them carry the clause inline; the README carries a scope marker: "
          f"{r['scoped_marker_in_the_readme']} (a description, not a claim)")

    at_zero = [x for x in r["arms"] if x["at_zero"]]
    print(f"\n== the {len(r['arms'])} arms, by their distance from zero ==")
    print(f"   indistinguishable from zero at two sigma: {len(at_zero)} "
          f"({100 * len(at_zero) / len(r['arms']):.0f}%); resolved away: {len(r['arms']) - len(at_zero)}")
    print("   the tightest bounds on zero, small mean and small sem:")
    for x in sorted(at_zero, key=lambda x: (abs(x["mean"]), x["sem"]))[:6]:
        print(f"      {x['mean']:+.5f} +- {x['sem']:.5f}  ({x['sigma']:4.2f} sigma)  n {x['n']:3}  "
              f"{x['artifact'][:38]:38} {x['arm']}")

    print("\n   and the largest resolved forgeries of that absence:")
    for x in sorted([y for y in r["arms"] if not y["at_zero"]], key=lambda y: -y["sigma"])[:5]:
        print(f"      {x['mean']:+.5f} +- {x['sem']:.5f}  ({x['sigma']:5.2f} sigma)  n {x['n']:3}  "
              f"{x['artifact'][:38]:38} {x['arm']}")

    print("\n== the registered claims, F1-F3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the front page's absence is true of a named minority of arms and false as a general claim, so the")
    print("    correction scopes the two sentences rather than deleting them)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--readme", type=Path, default=README)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    r = {"readme": str(args.readme), "resolved_at": RESOLVED}
    text = args.readme.read_text(encoding="utf-8") if args.readme.is_file() else ""
    r["absence_claims"] = absence_claims(text)
    r["scoped_marker_in_the_readme"] = "scoped 2026-09-29" in text.lower()
    r["arms"] = zeros(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
