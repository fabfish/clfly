"""E309 -- the benchmark's conformance contract: what a result must record, and the blocks the corpus records it in.

The FlyCL v0 block calls its reference framework *"a shared protocol that CL-for-SNN work currently lacks"*. A shared
protocol is a claim about **what a result contains**, and `e302` and `e303` read the block's metric list without ever
asking the question that makes a protocol work: **can a reader who is not the author recompute the numbers?** This
unit writes the contract down as eight checkable fields -- `clfly/bench/conformance.py`, each row with the reason a
third party needs it -- and reads the corpus against it.

Four claims, registered before the reading below was taken:

- **K1 -- the contract binds.** The scarcest field is carried by under a quarter of the corpus.
  **Falsifier**: every field carried by a quarter or more.
- **K2 -- and the binding field is the one the corpus's own methodology line required.** The scarcest field is the
  read-out draw fingerprint. **Falsifier**: another field is scarcer.
- **K3 -- and the conjunction is rare.** Under a quarter of the corpus carries all eight. **Falsifier**: a quarter or
  more.
- **K4 -- and the record is in blocks rather than a gradient.** No artifact carries between two and four of the eight
  fields: a payload has the result block or it has almost nothing. **Falsifier**: one artifact in between.

**What it cannot do.** *The eight are this unit's selection from a reader's task*: a benchmark that also wanted the
per-task observability spectrum or the pairwise principal angles would add rows, and the counts would move -- K1 and
K3 are claims about a contract, and a different contract gives different numbers. *A predicate reads one spelling*:
`seed0` under `config` and a `tasks` list count, and a runner that recorded the same fact under another name would
read as non-conformant. *Conformance is not quality*: an artifact can carry all eight and be wrong, which is every
other unit's business. *And the census is over the artifacts the corpus holds*, on `e301`'s collapse, so it describes
this repository's output and not what a fresh run would produce.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench import conformance
from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: K1's and K3's thresholds.
QUARTER = 0.25
CLAIMS = (
    ("K1", "the contract binds",
     "The scarcest field is carried by under a quarter of the corpus",
     "falsifier: every field carried by a quarter or more"),
    ("K2", "and the binding field is the one the corpus's own methodology line required",
     "The scarcest field is the read-out draw fingerprint",
     "falsifier: another field is scarcer"),
    ("K3", "and the conjunction is rare",
     "Under a quarter of the corpus carries all eight fields",
     "falsifier: a quarter or more"),
    ("K4", "and the record is in blocks rather than a gradient",
     "No artifact carries between two and four of the eight fields",
     "falsifier: one artifact in between"),
)


def reading(root: Path = RUNS) -> dict:
    c = conformance.census(root)
    c["rates"] = {k: v / c["artifacts"] for k, v in c["per_field"].items()} if c["artifacts"] else {}
    c["scarcest"] = min(c["per_field"], key=lambda k: c["per_field"][k]) if c["per_field"] else None
    return c


def judge(r: dict) -> list[dict]:
    if not r.get("artifacts"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus holds no artifact"} for c in CLAIMS]

    scar = r["scarcest"]
    out = [{"id": "K1", "measured": f"over {r['artifacts']} artifacts the scarcest field is `{scar}` at "
                                    f"{r['per_field'][scar]} ({100 * r['rates'][scar]:.0f}%)",
            "verdict": "MET -- a field the benchmark needs is carried by a minority" if
            r["rates"][scar] < QUARTER else f"FALSIFIER FIRED -- every field is at {100 * r['rates'][scar]:.0f}%"}]

    out.append({"id": "K2", "measured": f"the scarcest field is `{scar}`; the read-out draw is carried by "
                                        f"{r['per_field']['a read-out draw']}",
                "verdict": "MET -- the fingerprint `e103` required is the rarest thing a result must carry"
                if scar == "a read-out draw" else
                f"FALSIFIER FIRED -- `{scar}` is scarcer than the read-out draw"})

    share = r["conformant"] / r["artifacts"]
    out.append({"id": "K3", "measured": f"{r['conformant']} of {r['artifacts']} artifacts ({100 * share:.0f}%) "
                                        f"carry all {len(r['fields'])} fields",
                "verdict": "MET -- a small minority of the corpus is a recomputable result" if share < QUARTER else
                           f"FALSIFIER FIRED -- {100 * share:.0f}%"})

    gaps = r["gaps"]
    out.append({"id": "K4", "measured": f"the artifacts' counts of the {len(r['fields'])} run "
                                        f"{sorted(r['by_count'])}; {len(gaps)} fall between two and four",
                "verdict": "MET -- the record comes in blocks and not in degrees" if not gaps else
                           f"FALSIFIER FIRED -- counts {gaps}"})
    return out


def report(r: dict) -> int:
    print("== what a result must record, and how much of the corpus records it ==")
    for name in r["fields"]:
        why = dict((f[0], f[2]) for f in conformance.FIELDS)[name]
        print(f"   {name:20} {r['per_field'][name]:4} ({100 * r['rates'][name]:3.0f}%)  {why}")

    print("\n== and the blocks the corpus records them in ==")
    for b in r["blocks"]:
        carried = ", ".join(b["carries"]) or "nothing"
        print(f"   {b['n']:4} artifacts carry {len(b['carries'])}: {carried[:96]}")
        print(f"        e.g. {b['example']}")

    print("\n== the registered claims, K1-K4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (a benchmark whose protocol is a claim about what a result contains has to say what that is, and the")
    print("    field a reader needs most to trust the numbers -- the draw the run actually used -- is the rarest)")
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
