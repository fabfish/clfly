"""E278 -- "on disk" is not a definition: a paper extremum over a population it names in prose.

`e277` found that the paper's **counts** are scopes in disguise: the corpus grows and a universal quantified over a
number narrows silently. An **extremum over a population** is the same defect one step further out, because the
population itself is part of the claim -- and the paper names it in prose:

    the hardened row's EWC cell (+0.010 +- 0.010) is **below every one of the 17 diagonal arms on disk**,
    whose minimum is +0.0208

"On disk" is not a definition. The sentence does not say how the population was enumerated, so as written it is
**unfalsifiable** -- and under its plain reading, every artifact's diagonal arm under `runs/`, it is **false**: the
module enumerates the population, counts it, reads its minimum, and checks the sentence's own comparison against it.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **X1 -- the population the words admit is more than ten times the count the sentence gives.** Entries carrying a
  `diagonal(EWC)` analytic excess: **262** against the sentence's **17**. **Falsifier**: under three times.
- **X2 -- and the sentence's quoted minimum is not the minimum.** The population's minimum is **0.00022** -- **95
  times below** the quoted **+0.0208**, with **71** entries under the quoted figure. **Falsifier**: no entry below it.
- **X3 -- and the sentence's conclusion is falsified.** Its cell reads **+0.010**, which it says is below every one of
  the population; today **20** entries are below it, the smallest at 0.00022, so the cell is above **20** diagonal
  arms. **Falsifier**: none below.

**Either reading is a defect and they are different defects.** If "on disk" means every diagonal arm under `runs/`,
the sentence was wrong about its own population, its minimum and its conclusion -- three ways in one clause. If it
means some narrower set, the sentence does not say which, and a reader cannot check it at all. **The fix is the
enumerator, not a corrected number**: which artifacts, which field, which date.

**What it cannot do**: the module's enumeration is the one the words admit and not necessarily the one the author
used, so a narrower population would make X1 to X3 report a disagreement rather than a falsehood -- and the report
prints the population it enumerated beside the sentence's own numbers so a reader can see which is which; the field
read is `topologies[*]["diagonal(EWC)"]["analytic"]["excess_mean"]`, so an artifact recording a diagonal arm
elsewhere is invisible; the comparison in X3 borrows the sentence's own cell value rather than re-measuring it; and
nothing here says the sentence was wrong when it was written.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: The sentence's numbers, as printed, and the cell it compares against them.
QUOTED = {"phrase": "below every one of the 17 diagonal arms on disk",
          "quoted_count": 17, "quoted_min": 0.0208, "cell": 0.010, "cell_label": "the hardened row's EWC cell"}
#: The path a diagonal arm's excess is read from, and where the population is gathered.
FIELD = ("topologies", "diagonal(EWC)", "analytic", "excess_mean")
CLAIMS = (
    ("X1", "the population the words admit is more than ten times the sentence's count",
     "The entries under `runs/` carrying a diagonal arm's excess are at least three times the sentence's 17",
     "falsifier: under three times"),
    ("X2", "and the sentence's quoted minimum is not the minimum",
     "The population's smallest entry is below the quoted +0.0208",
     "falsifier: no entry below it"),
    ("X3", "and the sentence's conclusion is falsified",
     "The cell the sentence compares is above at least one entry of the population",
     "falsifier: none below it"),
)


def dig(d: dict, path: tuple):
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def population(root: Path = Path("runs")) -> list[dict]:
    """Every (artifact, arm) entry carrying the field the sentence's population is defined by."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        tops = (d or {}).get("topologies")
        if not isinstance(tops, dict):
            continue
        for arm, b in tops.items():
            v = dig(b if isinstance(b, dict) else {}, FIELD[1:])
            if isinstance(v, (int, float)):
                out.append({"artifact": Path(path).name, "arm": arm, "value": float(v)})
    return out


def judge(rows: list[dict], quoted: dict = QUOTED) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact carries the field"}
                for c in CLAIMS]

    lo = min(r["value"] for r in rows)
    under_quoted = [r for r in rows if r["value"] < quoted["quoted_min"]]
    under_cell = [r for r in rows if r["value"] < quoted["cell"]]
    small = sorted(rows, key=lambda r: r["value"])[:3]
    out.append({"id": "X1", "measured": f"the population is {len(rows)} entries over "
                                        f"{len({r['arm'] for r in rows})} arm names, against the sentence's "
                                        f"{quoted['quoted_count']} ({len(rows) / quoted['quoted_count']:.1f}x)",
                "verdict": "MET -- the words admit a population more than three times the sentence's count"
                if len(rows) >= 3 * quoted["quoted_count"] else
                "FALSIFIER FIRED -- under three times the sentence's count"})

    out.append({"id": "X2", "measured": f"the smallest entry is {lo:.5f} ({small[0]['artifact']} "
                                        f"{small[0]['arm']}) against the quoted +{quoted['quoted_min']:.4f}; entries "
                                        f"below the quoted figure: {len(under_quoted)}",
                "verdict": "MET -- the quoted minimum is not the minimum" if under_quoted else
                           "FALSIFIER FIRED -- nothing is below the quoted figure"})

    out.append({"id": "X3", "measured": f"the sentence's cell reads +{quoted['cell']:.3f} and it says it is below "
                                        f"every entry; entries below it: {len(under_cell)}"
                                        + (", the smallest " + ", ".join(f"{r['value']:.5f} ({r['artifact']})"
                                                                        for r in under_cell[:3]) if under_cell else ""),
                "verdict": "MET -- the sentence's conclusion is falsified under its own reading" if under_cell else
                           "FALSIFIER FIRED -- the cell is below every entry"})
    return out


def report(rows: list[dict]) -> int:
    print("== the sentence, and the population the words admit ==")
    text = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    print(f"   the paper says: {'the paper carries the phrase' if QUOTED['phrase'] in text else 'the phrase is absent'}"
          f" -- {QUOTED['phrase']!r}")
    print(f"   the field read: " + ".".join(("topologies[*]",) + FIELD[1:]))
    print(f"   the population: {len(rows)} entries over {len({r['arm'] for r in rows})} arm names")
    for r in sorted(rows, key=lambda r: r["value"])[:6]:
        print(f"      {r['value']:.5f}  {r['artifact'][:44]:44} {r['arm']}")
    print(f"      ... and {max(0, len(rows) - 6)} more")

    print("\n== the registered claims, X1-X3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a population named in prose is part of the claim and not a setting: 'on disk' admits an enumerator")
    print("    the sentence does not give, which makes it unfalsifiable as written and false under its plain reading)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = population(args.runs)
    if not rows:
        raise SystemExit("need artifacts carrying a diagonal arm's excess -- they are the population")
    if args.json_out:
        write_json(args.json_out, {"paper": str(PAPER), "quoted": QUOTED, "field": list(FIELD),
                                   "population_size": len(rows),
                                   "smallest": sorted(rows, key=lambda r: r["value"])[:10],
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
