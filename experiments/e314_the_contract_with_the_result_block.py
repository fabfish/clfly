"""E314 -- the contract with the result block: the three fields `e313` found, added to what a result must record.

`e309` declared eight fields a result must carry for a third party to recompute the benchmark's numbers, and found
that only 76 of the corpus's artifacts carry all eight. `e313` then showed that **the decomposition the block
prescribes is already written down per task** under `learned`, `final_per_task` and `forgetting_per_task`, and that
the retention matrix is the *redundancy* over them -- so a contract that asked for the matrix and not the fields was
asking a reader to re-derive three stored numbers.

Those three join, and the matrix stays: it is what an independent implementation is checked against. Four claims over
the **eleven** fields, registered before the reading below was taken:

- **K1 -- the contract still binds.** The scarcest of the eleven is carried by under a quarter of the corpus.
  **Falsifier**: every field at a quarter or more.
- **K2 -- and the scarcest is still the read-out draw**, which the three new fields do not displace: `e103`'s
  fingerprint remains the rarest thing a result must carry. **Falsifier**: another field scarcer.
- **K3 -- and the conjunction is still rare.** Under a quarter carry all eleven. **Falsifier**: a quarter or more.
- **K4 -- and the record has three levels with nothing between them.** No artifact carries between two and seven of
  the eleven: a payload has the result block or it has almost nothing. **Falsifier**: one in between.

**What changed and what did not.** K1, K2 and K3 are `e309`'s claims restated over a longer list, and the numbers
they turn on **did not move**: the three new fields are carried by the same artifacts that carry the other result
fields, so the scarcest field, the conformant count and the share are what they were. **K4 is sharper**: `e309` could
say only that nothing sat between one and five of eight, and over eleven the hole runs from two to seven -- the record
is one of three things and never a partial result.

**What it cannot do.** *The eleven are still this unit's selection from a reader's task*, so a benchmark wanting the
observability spectrum would add a twelfth and move nothing here except the denominators. *Adding fields can only
shrink the conformant set*, and it did not, because the fields travel with the matrix -- a corpus whose runners
recorded the matrix alone would show the drop. *A predicate reads one spelling*, unchanged from `e309`. *And
conformance is still not quality*: an artifact can carry all eleven and be wrong.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench import conformance
from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: K1's and K3's thresholds, and the counts K4 says are empty.
QUARTER = 0.25
HOLE = (2, 3, 4, 5, 6, 7)
CLAIMS = (
    ("K1", "the contract still binds",
     "The scarcest of the eleven fields is carried by under a quarter of the corpus",
     "falsifier: every field at a quarter or more"),
    ("K2", "and the scarcest is still the read-out draw",
     "The three new fields do not displace the read-out draw as the rarest thing a result must carry",
     "falsifier: another field scarcer"),
    ("K3", "and the conjunction is still rare",
     "Under a quarter of the corpus carries all eleven fields",
     "falsifier: a quarter or more"),
    ("K4", "and the record has three levels with nothing between them",
     "No artifact carries between two and seven of the eleven fields",
     "falsifier: one artifact in between"),
)


def reading(root: Path = RUNS) -> dict:
    c = conformance.census(root)
    c["rates"] = {k: v / c["artifacts"] for k, v in c["per_field"].items()} if c["artifacts"] else {}
    c["scarcest"] = min(c["per_field"], key=lambda k: c["per_field"][k]) if c["per_field"] else None
    c["fields_per_artifact"] = len(conformance.FIELDS)
    c["hole_present"] = sorted(k for k in c["by_count"] if k in HOLE)
    c["levels"] = sorted(c["by_count"])
    return c


def judge(r: dict) -> list[dict]:
    if not r.get("artifacts"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus holds no artifact"} for c in CLAIMS]

    scar = r["scarcest"]
    out = [{"id": "K1", "measured": f"over {r['artifacts']} artifacts and {r['fields_per_artifact']} fields the "
                                    f"scarcest is `{scar}` at {r['per_field'][scar]} "
                                    f"({100 * r['rates'][scar]:.0f}%)",
            "verdict": "MET -- a field the benchmark needs is carried by a minority" if
            r["rates"][scar] < QUARTER else f"FALSIFIER FIRED -- {100 * r['rates'][scar]:.0f}%"}]

    out.append({"id": "K2", "measured": f"the scarcest is `{scar}`; the three added fields are carried by "
                                        f"{r['per_field'].get('learned')}, "
                                        f"{r['per_field'].get('final_per_task')} and "
                                        f"{r['per_field'].get('forgetting_per_task')} artifacts, against the "
                                        f"read-out draw's {r['per_field'].get('a read-out draw')}",
                "verdict": "MET -- the fields a reader can use are not the scarce ones" if
                scar == "a read-out draw" else f"FALSIFIER FIRED -- `{scar}` is scarcer"})

    share = r["conformant"] / r["artifacts"]
    out.append({"id": "K3", "measured": f"{r['conformant']} of {r['artifacts']} artifacts ({100 * share:.0f}%) "
                                        f"carry all {r['fields_per_artifact']} fields",
                "verdict": "MET -- a small minority of the corpus is a recomputable result" if share < QUARTER else
                           f"FALSIFIER FIRED -- {100 * share:.0f}%"})

    out.append({"id": "K4", "measured": f"the artifacts' counts of the eleven run {r['levels']}; "
                                        f"{len(r['hole_present'])} of them fall between two and seven",
                "verdict": "MET -- the record is nothing, a seed, or the result block and more, and never a partial "
                           "one" if not r["hole_present"] else f"FALSIFIER FIRED -- counts {r['hole_present']}"})
    return out


def report(r: dict) -> int:
    print("== the contract, now eleven fields ==")
    why = {f[0]: f[2] for f in conformance.FIELDS}
    for name in r["fields"]:
        print(f"   {name:22} {r['per_field'][name]:4} ({100 * r['rates'][name]:3.0f}%)  {why.get(name, '')}")

    print("\n== and the three levels the record comes in ==")
    for b in sorted(r["blocks"], key=lambda b: len(b["carries"])):
        print(f"   {b['n']:4} artifacts carry {len(b['carries']):2}: {', '.join(b['carries'])[:88] or 'nothing'}")
    print(f"   counts present: {r['levels']}; empty from two to seven: {not r['hole_present']}")

    print("\n== the registered claims, K1-K4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the three fields the decomposition turned out to be were already being written, so the contract")
    print("    now asks for them and the share of the corpus that is a recomputable result did not move)")
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
