"""E347 -- the one family that disagrees, moved to a budget the corpus does not hold it at.

`e346` read every experiment in the corpus carrying both the `replay` and the `ewc-block` arm and found the ordering
travels: **fourteen** experiments resolve it in `replay`'s favour and **none** resolve it against, at both circuit
budgets, in both suites and in the loop. It also found the six point estimates that go the other way, and named what
they are: not six substrates but **one family**, at `fisher_batches` 8 or 128 where the rest of the corpus uses 32,
each member carrying five replicates and every one of them inside 1.54 sigma. `e346`'s own "what it cannot do" is the
sentence this unit acts on -- *"it cannot separate 'the ordering travels' from 'the ordering was the same
experiment'"*, because no run was made.

**So one run is made, on the family itself, where the corpus has the fewest replicates.** The family's members are
all at `circuit_size = 800` and all at five replicates; this runs the derived configuration at **300** with **twenty**
replicates, and the flags are taken from `e101_rate_fb8`'s own config through the corpus's `e163 --command` path
rather than typed, so the only fields that differ are the two that were meant to. The question is sharp: the family's
point estimate is **negative**, this is the first powered reading of it, and it can come out either way.

Four claims, registered before the run's reading was opened.

- **T1 -- one configuration, two fields moved.** Every field the derivation set agrees with `e101_rate_fb8`'s, and
  `circuit_size` (800 to 300) and `repeats` (5 to 20) are the only ones that differ. **Falsifier**: any other field
  differing, or a moved field that did not move.
- **T2 -- and the ordering resolves on this substrate.** `replay` minus `ewc-block` on `final_accuracy` is positive
  at **2 sigma**. **Falsifier**: negative at 2 sigma, i.e. the ordering inverting where the family's five-replicate
  estimates pointed the same way. **Null**: unresolved. This is the claim the run exists for, and either resolution
  is a result: `e346` found no experiment in the corpus that resolves against `replay`.
- **T3 -- and it lands inside the family's band.** The new contrast is within **0.03** of the family's artifact-level
  mean. **Falsifier**: apart by **0.05** or more, which would say the circuit budget moves this contrast and the
  family's near-zero estimates are a budget artefact rather than a family property. **Null**: between.
- **T4 -- and the forgetting side agrees.** The new run's `mean_forgetting` contrast is negative at **2 sigma**, as
  the family's members mostly are. **Falsifier**: positive at 2 sigma, which would say `replay` buys the accuracy it
  is ahead on with forgetting. **Null**: unresolved.

**What it cannot do.** *One run, one budget and one seed stream*: the new run uses the corpus's `seed0 = 0` and the
same overlap suite, so it is the same experiment at a smaller circuit and not an independent stream -- an independent
stream is `e337`'s and `e340`'s axis. *Twenty replicates* give the contrast the power to see a family-sized effect
and not to bound a small one: an unresolved T2 is a bound and not a nil. *The family is defined by a config field*
(`fisher_batches` 8 or 128), which is the grouping `e346` named and not a mechanism, and nothing here says why the
field would move a method contrast. *And `ewc-block` is one penalty*: nothing here is about `ewc`,
`ewc-block-rand`, the lambda, or the basis contrast.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e346_does_the_method_contrast_travel import ACC, ARM, BASELINE, FORGET, across, load, one_artifact

RUNS = Path("runs")
NEW = RUNS / "e347_fb8_at_cs300.json"
#: the artifact the flags were derived from, and the two fields that were meant to move
SOURCE = RUNS / "e101_rate_fb8.json"
ALLOWED = {"circuit_size", "repeats", "json_out"}
MOVED = {"circuit_size": (800, 300), "repeats": (5, 20)}
#: the family `e346` named: `fisher_batches` 8 or 128, where the rest of the corpus uses 32
FAMILY_FISHER = (8, 128)
SIGMA = 2.0
SAME = 0.03
APART = 0.05
CLAIMS = (
    ("T1", "one configuration, two fields moved",
     f"Every field the derivation set agrees with `{SOURCE.name}`'s, with `circuit_size` and `repeats` the only ones "
     f"differing",
     "falsifier: any other field differing, or a moved field that did not move"),
    ("T2", f"and the ordering resolves on this substrate, at {SIGMA:.0f} sigma",
     f"`{ARM}` minus `{BASELINE}` on `{ACC}` is positive at 2 sigma",
     "falsifier: negative at 2 sigma; null: unresolved"),
    ("T3", f"and it lands inside the family's band, within {SAME:.2f}",
     "The new contrast is within 0.03 of the family's artifact-level mean",
     f"falsifier: apart by {APART:.2f} or more"),
    ("T4", f"and the forgetting side agrees, at {SIGMA:.0f} sigma",
     f"The new run's `{FORGET}` contrast is negative at 2 sigma",
     "falsifier: positive at 2 sigma; null: unresolved"),
)


def family(root: Path = RUNS) -> list[dict]:
    """Every collapsed experiment in the corpus whose configuration puts it in the family `e346` named."""
    from clfly.bench import corpus
    skip = corpus.repeat_paths(root)
    out = []
    for p in sorted(root.glob("*.json")):
        if p.name in skip or p.name == NEW.name:
            continue
        d = load(p)
        if d is None:
            continue
        c = d.get("config") or {}
        if c.get("fisher_batches") not in FAMILY_FISHER:
            continue
        row = one_artifact(p, d)
        if row is not None:
            out.append(row)
    return out


def field_diff(source: dict, new: dict) -> dict:
    """The fields the derivation set, and which of them moved."""
    src, dst = source.get("config") or {}, new.get("config") or {}
    return {k: [src.get(k) if k in src else None, dst.get(k)] for k in sorted(set(src) & set(dst))
            if src.get(k) != dst.get(k)}


def reading(root: Path = RUNS, new_path: Path | None = None, source_path: Path | None = None) -> dict:
    np_ = new_path or NEW
    new_doc, src_doc = load(np_), load(source_path or SOURCE)
    rows = family(root)
    out = {"new": one_artifact(np_, new_doc) if new_doc else None,
           "family": rows, "source": (source_path or SOURCE).name,
           "moved": {k: list(v) for k, v in MOVED.items()},
           "field_diff": field_diff(src_doc, new_doc) if (src_doc and new_doc) else None,
           "family_accuracy": across(rows, ACC), "family_forgetting": across(rows, FORGET)}
    return out


def _branch(new, metric, direction):
    est = (new or {}).get(metric) or {}
    if est.get("delta") is None or est.get("sigma") is None:
        return "REFUSED", est
    ok = est["delta"] > 0 if direction == "positive" else est["delta"] < 0
    if ok and est["sigma"] >= SIGMA:
        return "MET", est
    if not ok and est["sigma"] >= SIGMA:
        return "FALSIFIER", est
    return "NULL", est


def judge(r: dict) -> list[dict]:
    new, fam = r.get("new"), r.get("family") or []
    if not new or len(fam) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the run or the family is not on disk"}
                for c in CLAIMS]

    diff = r.get("field_diff") or {}
    wrong = {k: v for k, v in diff.items() if k not in ALLOWED}
    missed = {k: v for k, v in MOVED.items() if list(v) != diff.get(k)}
    j1 = {"id": "T1", "measured": f"derived from `{r['source']}`, the fields that differ from it being {diff}, "
                                  f"against the intended {r['moved']}",
          "verdict": "MET -- only the circuit budget and the replicate count differ" if not wrong and not missed
          else f"FALSIFIER FIRED -- unintended fields {wrong}, intended fields that did not move {missed}"}

    st2, e2 = _branch(new, ACC, "positive")
    m2 = (f"`{ARM}` minus `{BASELINE}` on `{ACC}`: {e2.get('delta'):+.4f} on a sem of {e2.get('sem'):.4f} "
          f"({e2.get('sigma'):.2f} sigma) over {new['repeats']} replicates at circuit size "
          f"{new['circuit_size']}") if e2.get("delta") is not None else "the contrast was not computable"
    j2 = {"id": "T2", "measured": m2,
          "verdict": f"MET -- the ordering resolves for `{ARM}`, {e2['delta']:+.4f} at {e2['sigma']:.2f} sigma" if
          st2 == "MET" else
          f"FALSIFIER FIRED -- it resolves AGAINST `{ARM}`, {e2['delta']:+.4f} at {e2['sigma']:.2f} sigma" if
          st2 == "FALSIFIER" else
          f"NULL -- {e2['delta']:+.4f} at {e2['sigma']:.2f} sigma, unresolved" if st2 == "NULL" else
          "REFUSED -- the contrast was not computable"}

    fa = r.get("family_accuracy") or {}
    gap = None if (fa.get("delta") is None or e2.get("delta") is None) else abs(e2["delta"] - fa["delta"])
    if gap is None:
        j3 = {"id": "T3", "measured": "the family's estimate was not computable",
              "verdict": "REFUSED -- the family's estimate was not computable"}
    else:
        j3 = {"id": "T3", "measured": f"the family's artifact-level mean is {fa['delta']:+.4f} over {fa['n']} "
                                      f"experiments and the new contrast is {e2['delta']:+.4f}, {gap:.4f} apart",
              "verdict": f"MET -- inside the family's band, {gap:.4f} apart" if gap < SAME else
              f"FALSIFIER FIRED -- the budget moves the contrast by {gap:.4f}" if gap >= APART else
              f"NULL -- {gap:.4f} apart, between {SAME:.2f} and {APART:.2f}"}

    st4, e4 = _branch(new, FORGET, "negative")
    fam_f = (r.get("family_forgetting") or {}).get("delta")
    m4 = (f"`{ARM}` minus `{BASELINE}` on `{FORGET}`: {e4.get('delta'):+.4f} on a sem of {e4.get('sem'):.4f} "
          f"({e4.get('sigma'):.2f} sigma), against the family's "
          f"{fam_f:+.4f}" if fam_f is not None else " (the family's estimate is absent)") if \
        e4.get("delta") is not None else "the contrast was not computable"
    j4 = {"id": "T4", "measured": m4,
          "verdict": f"MET -- `{ARM}` forgets less, {e4['delta']:+.4f} at {e4['sigma']:.2f} sigma" if
          st4 == "MET" else
          f"FALSIFIER FIRED -- `{ARM}` forgets MORE, {e4['delta']:+.4f} at {e4['sigma']:.2f} sigma" if
          st4 == "FALSIFIER" else
          f"NULL -- {e4['delta']:+.4f} at {e4['sigma']:.2f} sigma, unresolved" if st4 == "NULL" else
          "REFUSED -- the contrast was not computable"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    new, fam = r.get("new"), r.get("family") or []
    if not new:
        print("== the family that disagrees ==\n   REFUSED -- the run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return sum("REFUSED" in row["verdict"] for row in judge(r))

    print("== the family that disagrees ==")
    print(f"   the new run: circuit size {new['circuit_size']}, {new['repeats']} replicates, "
          f"{new['n_tasks']} tasks, overlap {new['overlap']}")
    print(f"   the family (`fisher_batches` {FAMILY_FISHER[0]} or {FAMILY_FISHER[1]}): {len(fam)} experiments")
    print(f"\n   {'experiment':<44} {'cs':>5} {'rep':>4} {'acc':>9} {'sig':>6} {'forget':>9} {'sig':>6}")
    for row in fam:
        a, f = row[ACC], row[FORGET]
        print(f"   {row['artifact'][:44]:<44} {str(row['circuit_size']):>5} {row['repeats']:>4} "
              f"{a['delta']:+9.4f} {_sg(a['sigma']):>6} {f['delta']:+9.4f} {_sg(f['sigma']):>6}")
    a, f = new[ACC], new[FORGET]
    print(f"   {'>> e347_fb8_at_cs300.json (this run)':<44} {str(new['circuit_size']):>5} {new['repeats']:>4} "
          f"{a['delta']:+9.4f} {_sg(a['sigma']):>6} {f['delta']:+9.4f} {_sg(f['sigma']):>6}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e346` found the six estimates that disagree are one family at five replicates each, every one of")
    print("    them inside 1.54 sigma; this is the first powered reading of that family, at a circuit it never ran)")
    return sum("REFUSED" in row["verdict"] for row in j)


def _sg(sigma) -> str:
    return "inf" if sigma is None else f"{sigma:.2f}"


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
