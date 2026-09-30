"""E301 -- the corpus holds eleven clusters of files that are one execution written twice.

Every census in this project reads the corpus as ``runs/*.json`` and therefore counts **files**. On 2026-09-29 the
corpus gained a second execution of a configuration it already held, and the discovery that followed is this unit's
subject: the corpus does not hold one such pair, it holds **eleven clusters and seventeen files** that are a copy of an
experiment already here, and the censuses had been counting them all along.

The eleven, and what each pair is:

    e102_rate_fb8_rerun                ==  e102_rate_fb8_rerun2                       a re-run kept beside its original
    e104_frozen_r128_plastic           ==  e106_plastic_r128_rep{1,2,3}                four executions of one command
    e104_frozen_r32_plastic            ==  e106_plastic_r32_rep{1,2,3}
    e104_frozen_whole_plastic          ==  e106_plastic_r0_rep{1,2,3}
    e110_readout512_plastic            ==  e110_readout512_plateau                     the plateau flag is not read
    e111_readout900_plastic            ==  e111_readout900_plateau
    e112_readout300_plastic            ==  e112_readout300_plateau
    e113_r300_draw1                    ==  e113_r300_draw1_plateau
    e153_r32_overlap1_methods_40reps   ==  e159_r32_overlap1_methods_rerun             the corpus's largest reproduction
    e164_fb8_today_a                   ==  e164_fb8_today_b                            two executions, one command
    e287_frozenbias_suite1440_40reps   ==  e288_frozenbias_suite1440_40reps           **the new one**

Ten of the eleven are the corpus's **deliberate reproduction record** -- `e026`, `e103` and `e159` built a line out
of exactly these pairs, and the largest of them is 200 values across a three-hour re-execution. The eleventh was not
deliberate: the 1440-item suite of the read-out-32 frozen-bias configuration was launched twice while one launch was
believed dead, both finished, and both wrote.

Three claims, registered before the readings below were taken:

- **R1 -- the corpus holds repeats beyond the ones its findings noticed.** Eleven clusters, seventeen files, of which
  ten clusters are named in a finding and one is named nowhere. **Falsifier**: fewer than three clusters.
- **R2 -- and a repeat is bookkeeping rather than a difference.** For every pair, the two payloads agree on every key
  outside the output path, the two calendar keys, the code revision and the environment calibration. **Falsifier**:
  a pair with one further differing key.
- **R3 -- and the repair is verdict-neutral.** Dropping the second copies changes every count in the three censuses
  that read the corpus -- `e286`'s candidates, swaps and comparisons, `e295`'s and `e296`'s comparisons -- and **no
  verdict in any of them**. That is the licence for the repair, and it is why the fix is in the reader rather than in
  the file. **Falsifier**: a verdict that moves.

**What it cannot do.** *The detector cannot tell two executions from one execution run twice*: it sees the artifacts,
and two runs of one configuration seeded the same way are deterministic, so "the runner was launched twice" and "the
runner was launched once and reproduced" are the same evidence -- which is why the unit reports a *cluster* and not an
accident. *No arm is bit-identical by construction*: agreement is required on the six training-derived fields, and a
pair agrees only because the training ran identically. *The canonicity is lexical* -- the alphabetically first member
is kept, and because R2 holds for every pair any other choice gives the same numbers, but the *name* a finding cites
is a convention and not a discovery. *And the clusters are ten of them deliberate*: this unit cannot say that a
duplicate is a mistake, only that it is a duplicate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json
from experiments import e286_the_fall_is_not_the_samples_size as e286
from experiments import e295_which_metric_selects_the_basis as e295
from experiments import e296_the_matched_random_control as e296

RUNS = Path("runs")
#: The claim that says the corpus noticed most of these: ten of eleven clusters are named in a finding.
DELIBERATE = 10
#: The minimum number of clusters R1 asks the corpus to hold.
FEWEST = 3
CLAIMS = (
    ("R1", "the corpus holds repeats, and more of them than its findings noticed",
     f"At least {FEWEST} clusters of files are one execution written twice",
     f"falsifier: fewer than {FEWEST}"),
    ("R2", "and a repeat is bookkeeping rather than a difference",
     "Every pair agrees on every key outside the output path, the calendar keys, the code revision and the "
     "environment calibration",
     "falsifier: a pair with one further differing key"),
    ("R3", "and the repair is verdict-neutral",
     "Dropping the second copies moves every count in the three censuses and no verdict in any of them",
     "falsifier: a verdict that moves"),
)


def clusters(root: Path = RUNS) -> list[dict]:
    """Each cluster of one experiment, with the evidence that makes it one."""
    by_pair = {(p["canonical"], p["duplicate"]): p for p in corpus.pairs(root)}
    out = []
    for g in corpus.groups(root):
        evidence = [by_pair[(g[i], g[j])] for i in range(len(g)) for j in range(i + 1, len(g))]
        out.append({"members": [Path(m).name for m in g], "n_pairs": len(evidence),
                    "arms": len(evidence[0]["arms"]), "replicates": evidence[0]["replicates"],
                    "differing_paths": sorted({p for e in evidence for p in e["differing_paths"]})})
    return out


def e286_reading(collapse: bool, root: Path = RUNS) -> dict:
    """`e286`'s census as its own `main` assembles it, so the verdicts are the ones the unit registers."""
    cands = e286.candidates(root, collapse=collapse)
    swaps = [c for c in cands if c["swap"]]
    rows = [c for p in swaps for c in e286.comparisons(p)]
    r = {"n_candidates": len(cands), "pairs": swaps, "comparisons": rows}
    return {"n_candidates": len(cands), "n_swaps": len(swaps), "n_comparisons": len(rows),
            "claims": {x["id"]: x["verdict"] for x in e286.judge(r)}}


def e295_reading(collapse: bool, root: Path = RUNS) -> dict:
    """`e295`'s census as its own `main` assembles it."""
    rows = e295.comparisons(root, collapse=collapse)
    r = {"comparisons": rows, "by_metric": e295.by_metric(rows) if rows else {},
         "disagreement": e295.disagreement(rows) if rows else {},
         "a": e295.A, "b": e295.B, "resolved_at": e295.RESOLVED}
    return {"n_comparisons": sum(1 for x in rows if x["metric"] == "final_accuracy"),
            "claims": {x["id"]: x["verdict"] for x in e295.judge(r)}}


def e296_reading(collapse: bool, root: Path = RUNS) -> dict:
    """`e296`'s census as its own `main` assembles it."""
    rows = e296.comparisons(root, collapse=collapse)
    r = {"comparisons": rows, "by_metric": e296.by_metric(rows) if rows else {},
         "a": e296.A, "b": e296.B, "resolved_at": e296.RESOLVED, "powered": e296.POWERED, "diagonal": {}}
    return {"n_comparisons": sum(1 for x in rows if x["metric"] == "final_accuracy"),
            "claims": {x["id"]: x["verdict"] for x in e296.judge(r)}}


def censuses(collapse: bool, root: Path = RUNS) -> dict:
    """The three censuses that glob the corpus, read with the second copies kept or dropped."""
    return {"e286": e286_reading(collapse, root), "e295": e295_reading(collapse, root),
            "e296": e296_reading(collapse, root)}


def outcome(verdict: str) -> str:
    """A verdict's class rather than its sentence, because the counts inside the sentence are R3's subject."""
    return verdict.split(" --")[0].strip()


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    cl = r.get("clusters") or []
    if not cl:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no cluster of one experiment was found"}
                for c in CLAIMS]

    files = sum(len(c["members"]) - 1 for c in cl)
    named = sum(1 for c in cl if "suite1440" not in " ".join(c["members"]))
    out.append({"id": "R1", "measured": f"{len(cl)} clusters hold {files} files that are a second copy of an "
                                        f"experiment already in the corpus; {named} clusters predate the newest pair",
                "verdict": "MET -- the corpus holds repeats and more than its findings noticed" if len(cl) >= FEWEST
                           else f"FALSIFIER FIRED -- {len(cl)} clusters"})

    dirty = {tuple(c["members"]): c["differing_paths"] for c in cl if c["differing_paths"]}
    arms = {c.get("arms") for c in cl} - {None}
    span = f"the clusters run {min(arms)} to {max(arms)} arms" if arms else "no cluster records its arms"
    out.append({"id": "R2", "measured": f"{len(cl) - len(dirty)} of {len(cl)} clusters agree on every key outside "
                                        f"the output path, the clock, the revision and the calibration; {span}",
                "verdict": "MET -- a second execution is bookkeeping and not a difference" if not dirty
                           else f"FALSIFIER FIRED -- {len(dirty)} clusters differ elsewhere"})

    before, after = r["censuses"]["kept"], r["censuses"]["dropped"]
    moved = {f"{k}.{n}": (before[k][n], after[k][n])
             for k in ("e286", "e295", "e296") for n in before[k] if n.startswith("n_") and before[k][n] != after[k][n]}
    #: The verdict's **class** and not its sentence: `FALSIFIER FIRED -- 2 of 54 did not fall` and
    #: `FALSIFIER FIRED -- 1 of 34 did not fall` are one outcome, and the counts they quote are R3's subject.
    verdicts = [f"{k}.{cid}" for k in ("e286", "e295", "e296") for cid in before[k]["claims"]
                if outcome(before[k]["claims"][cid]) != outcome(after[k]["claims"][cid])]
    counts = ", ".join(f"{k} {n} {before[k][n]} to {after[k][n]}" for k in ("e286", "e295", "e296")
                       for n in before[k] if n.startswith("n_"))
    out.append({"id": "R3", "measured": f"{len(moved)} counts move when the copies are dropped ({counts}), and "
                                        f"{len(verdicts)} verdicts change class",
                "verdict": "MET -- the repair moves counts and leaves every verdict where it was" if not verdicts
                           else f"FALSIFIER FIRED -- {verdicts}"})
    return out


def report(r: dict) -> int:
    print("== the clusters of files that are one experiment ==")
    for c in r["clusters"]:
        print(f"   {len(c['members'])} files, {c['n_pairs']} pairs, {c['arms']} arms, "
              f"{c['replicates']} replicates:  " + "  ==  ".join(c["members"]))
    print(f"   the corpus holds {r['n_files']} files and {r['n_files'] - r['n_second_copies']} experiments")

    print("\n== and the three censuses, with the second copies kept and dropped ==")
    for k in ("e286", "e295", "e296"):
        before, after = r["censuses"]["kept"][k], r["censuses"]["dropped"][k]
        print(f"   {k}: " + ", ".join(f"{n} {before[n]} to {after[n]}" for n in before if n.startswith("n_")))

    print("\n== the registered claims, R1-R3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the corpus was never told to keep one experiment once: ten of these pairs are its reproduction")
    print("    record and one was an accident, and a census that counts files counts the accident as a result)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    cl = clusters(args.runs)
    files = sorted(p.name for p in Path(args.runs).glob("*.json"))
    r = {"clusters": cl, "n_files": len(files), "n_second_copies": len(corpus.repeat_paths(args.runs)),
         "second_copies": sorted(corpus.repeat_paths(args.runs)),
         "censuses": {"kept": censuses(False, args.runs), "dropped": censuses(True, args.runs)}}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
