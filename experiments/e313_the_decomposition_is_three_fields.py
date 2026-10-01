"""E313 -- the decomposition is three stored fields, and the retention matrix is their redundancy.

`e304` reads the shortfall `1 - R[T-1][j]` off the retention matrix and splits it at the level `R[j][j]`; `e312`
showed the shortfall is `1 - final_accuracy`. **This unit tests where each of those three cells comes from**, and the
answer is that the corpus already writes all of them down, per task:

    R[j][j]        ==  `learned`[j]                 the level the task reached when it was learned
    R[T-1][j]      ==  `final_per_task`[j]          the level it ended at
    their difference == `forgetting_per_task`[j]    the lost term

so the matrix is the **redundancy** and not the source. Four claims, registered before the reading below was taken:

- **Y1 -- the diagonal is a stored field.** `retention[j][j]` equals `learned[j]` for every task of every
  arm-replicate that carries both. **Falsifier**: one that differs.
- **Y2 -- and the last row is another.** `retention[T-1][j]` equals `final_per_task[j]` likewise. **Falsifier**: one.
- **Y3 -- and the difference is the third.** `learned[j] - final_per_task[j]` equals `forgetting_per_task[j]`
  likewise. **Falsifier**: one.
- **Y4 -- and so no term of `e304`'s split is a quantity the corpus lacks.** Each of its three terms is a stored
  field or its complement: `unlearned_mean` is `1 - mean(learned)`, `shortfall_mean` is `1 - mean(final_per_task)`,
  and `lost_mean` is `mean(forgetting_per_task)`. **Falsifier**: a term that is neither.

**What this corrects.** `e312`'s finding closes by saying *"the currency the corpus lacks is `unlearned`"*, and that
is wrong: the corpus has it, **as `learned`**, in the same payload as the matrix. What `e304` still adds is the
**verification** -- the three fields agree with the matrix per task in every arm, which is what makes a split taken
from either one trustworthy -- and the reading of the *share*, which is a ratio of two of them and is where `e305`
and `e306`'s surviving R3 live.

**What it cannot do.** *These are identities between recorded numbers*, so Y1 to Y4 check a writer and not a result:
a runner that wrote `learned` wrongly and a matrix wrongly would pass. *Only arm-replicates carrying all three
fields are read*, and the count of those is reported rather than assumed. *The claim is about this corpus's runner*,
so another runner's spelling would read as absent, which is `e309`'s conformance question and not this unit's. *And
nothing here says the matrix is redundant in **size***: it is larger than the three fields and carries nothing they
do not, which is a fact about the writer and not a reason to drop it.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: What counts as the same number between a matrix cell and a stored field.
TOLERANCE = 1e-9
CLAIMS = (
    ("Y1", "the diagonal is a stored field",
     "`retention[j][j]` equals `learned[j]` for every task of every arm-replicate carrying both",
     "falsifier: one that differs"),
    ("Y2", "and the last row is another",
     "`retention[T-1][j]` equals `final_per_task[j]` likewise",
     "falsifier: one that differs"),
    ("Y3", "and the difference is the third",
     "`learned[j] - final_per_task[j]` equals `forgetting_per_task[j]` likewise",
     "falsifier: one that differs"),
    ("Y4", "and so no term of the split is a quantity the corpus lacks",
     "Each term of `e304`'s split is a stored field or its complement",
     "falsifier: a term that is neither"),
)


def payloads(root: Path = RUNS):
    for p in sorted(Path(root).glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        methods = d.get("methods")
        if not isinstance(methods, dict):
            continue
        for arm, entry in methods.items():
            if not isinstance(entry, dict):
                continue
            for rep in entry.get("replicates") or []:
                if isinstance(rep, dict):
                    yield p.name, arm, rep


def close(a, b) -> bool:
    return abs(a - b) <= TOLERANCE


def cells(rep: dict) -> dict | None:
    """The matrix's diagonal and last row, or ``None`` if the matrix cannot supply them."""
    R = rep.get("retention")
    if not R or not isinstance(R, list):
        return None
    T = len(R)
    if any(not isinstance(row, list) or len(row) != T for row in R):
        return None
    reached = [R[j][j] for j in range(T)]
    ended = [R[T - 1][j] for j in range(T)]
    if any(v is None for v in reached + ended):
        return None
    return {"reached": reached, "ended": ended, "T": T}


def by_index(root: Path = RUNS) -> dict:
    """Every replicate keyed by `(artifact, arm, position)`, which is how `e304`'s rows name it."""
    out = {}
    for p in sorted(Path(root).glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        methods = d.get("methods")
        if not isinstance(methods, dict):
            continue
        for arm, entry in methods.items():
            if not isinstance(entry, dict):
                continue
            for i, rep in enumerate(entry.get("replicates") or []):
                if isinstance(rep, dict):
                    out[(p.name, arm, i)] = rep
    return out


def reading(root: Path = RUNS) -> dict:
    """The matrix checked against the three fields, and `e304`'s three terms checked against the fields."""
    from experiments import e304_the_decomposition_the_block_asked_for as e304

    n = 0
    ok = {"learned": 0, "final_per_task": 0, "forgetting_per_task": 0}
    carried = {k: 0 for k in ("learned", "final_per_task", "forgetting_per_task", "retention")}
    wrong_index = 0
    first_bad: dict = {}
    for name, arm, rep in payloads(root):
        for k in carried:
            if rep.get(k) is not None:
                carried[k] += 1
        c = cells(rep)
        if c is None:
            continue
        T = c["T"]
        lrn, fpt, fgt = rep.get("learned"), rep.get("final_per_task"), rep.get("forgetting_per_task")
        if not (isinstance(lrn, list) and isinstance(fpt, list) and isinstance(fgt, list)
                and len(lrn) == len(fpt) == len(fgt) == T):
            wrong_index += 1
            continue
        n += 1
        for key, got, want in (("learned", c["reached"], lrn), ("final_per_task", c["ended"], fpt),
                               ("forgetting_per_task", [a - b for a, b in zip(c["reached"], c["ended"])], fgt)):
            if all(close(a, b) for a, b in zip(got, want)):
                ok[key] += 1
            elif key not in first_bad:
                first_bad[key] = (name, arm, got, want)

    #: `e304`'s three arm-level terms against the stored fields, on the rows that carry both
    index = by_index(root)
    rows, _ = e304.replicates(root)
    ledger = {"unlearned_mean": 0, "shortfall_mean": 0, "lost_mean": 0}
    term_rows = 0
    for got in rows:
        rep = index.get((got["artifact"], got["arm"], got["replicate"]))
        if not rep:
            continue
        lrn, fpt = rep.get("learned"), rep.get("final_per_task")
        if not isinstance(lrn, list) or not isinstance(fpt, list) or len(lrn) != len(fpt):
            continue
        term_rows += 1
        if close(got["unlearned_mean"], statistics.fmean(1.0 - v for v in lrn)):
            ledger["unlearned_mean"] += 1
        if close(got["shortfall_mean"], statistics.fmean(1.0 - v for v in fpt)):
            ledger["shortfall_mean"] += 1
        if close(got["lost_mean"], statistics.fmean(a - b for a, b in zip(lrn, fpt))):
            ledger["lost_mean"] += 1
    return {"rows": n, "ok": ok, "carried": carried, "term_rows": term_rows, "terms": ledger,
            "wrong_index": wrong_index,
            "first_bad": {k: [str(x) for x in v] for k, v in first_bad.items()}}


def judge(r: dict) -> list[dict]:
    if not r.get("rows"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm carries a matrix and its fields"}
                for c in CLAIMS]

    n = r["rows"]
    out = []
    for cid, key, what in (("Y1", "learned", "`retention[j][j]`"),
                           ("Y2", "final_per_task", "`retention[T-1][j]`")):
        got = r["ok"][key]
        out.append({"id": cid, "measured": f"{what} equals `{key}` in {got} of {n} arm-replicates",
                    "verdict": f"MET -- the matrix's cell is the stored field" if got == n else
                               f"FALSIFIER FIRED -- {n - got} differ"})

    got = r["ok"]["forgetting_per_task"]
    out.append({"id": "Y3", "measured": f"`learned[j] - final_per_task[j]` equals `forgetting_per_task[j]` in "
                                        f"{got} of {n} arm-replicates",
                "verdict": "MET -- the lost term is a stored field and not a difference this unit takes"
                if got == n else f"FALSIFIER FIRED -- {n - got} differ"})

    t = r["terms"]
    rows = r["term_rows"]
    ok = all(v == rows for v in t.values()) and rows > 0
    out.append({"id": "Y4", "measured": f"of {rows} arm-replicates carrying both levels, "
                                        f"{t['unlearned_mean']} have `unlearned_mean` equal to "
                                        f"`1 - mean(learned)`, {t['shortfall_mean']} have `shortfall_mean` equal "
                                        f"to `1 - mean(final_per_task)`, and {t['lost_mean']} have `lost_mean` "
                                        f"equal to `mean(learned) - mean(final_per_task)`",
                "verdict": "MET -- every term of the split is a stored field or its complement"
                if ok else f"FALSIFIER FIRED -- {t}"})
    return out


def report(r: dict) -> int:
    print("== the three fields the corpus writes, and the matrix they are the cells of ==")
    for k, v in r["carried"].items():
        print(f"   {k:22} carried by {v:5} arm-replicates")
    print(f"   {r['rows']} arm-replicates carry a matrix and all three per-task fields")
    for k, v in r["ok"].items():
        print(f"   the matrix agrees with `{k}` in {v} of {r['rows']}")
    if r["first_bad"]:
        for k, v in r["first_bad"].items():
            print(f"   first disagreement on {k}: {v}")

    print("\n== the registered claims, Y1-Y4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the matrix is the redundancy and not the source: `learned`, `final_per_task` and")
    print("    `forgetting_per_task` are the three cells `e304` reads off it, written out in full)")
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

    r = reading(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
