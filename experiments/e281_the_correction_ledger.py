"""E281 -- the correction ledger: what the audit series read, what still flags, and what the paper now says.

Six fires have aimed instruments at the paper: `e268` (superseded numbers, by registry), `e270` (an existence premise,
by scan), `e277` (counts, by pattern), `e278` (an extremum over a population named in prose), `e279` (a universal over
an epoch) and `e280` (the positive control). Each unit ended with a correction applied to the paper -- except one, and
**nobody has checked which**. A series that reports findings without a ledger cannot tell its own outstanding work
from its finished work, which is the same defect it audits: a claim whose scope is not stated.

So this unit runs every instrument again and reads the ledger off the instruments themselves:

    for each instrument: how many statements it reads, how many it flags TODAY, and whether the paper carries a
    correction note for the statement it flags

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **C1 -- the series runs end to end.** Every instrument executes and reads at least one statement of the paper, and
  together they read **six** distinct units of work. **Falsifier**: an instrument that cannot run or reads nothing.
- **C2 -- and the ledger shows bounded, named outstanding work.** At most **one** instrument still flags its statement
  today. **Falsifier**: three or more still flagging.
- **C3 -- and every instrument that stopped flagging did so because the paper was corrected.** For each instrument
  that reads its statement and finds it clean, the paper carries a correction clause naming the finding. **Falsifier**:
  an instrument that stopped flagging while the paper's sentence is unchanged, which would mean the check weakened
  rather than the paper being fixed.

**The work item is the point.** The series' own ledger is the check the paper's stale statements needed, turned on the
series: a finding that is not in the ledger is a finding nobody can close.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e268_paper_supersession_audit as e268
from experiments import e270_an_existence_premise_falsified as e270
from experiments import e277_a_count_is_not_a_scope as e277
from experiments import e278_on_disk_is_not_a_definition as e278
from experiments import e279_every_one_of_the_77 as e279
from experiments import e280_the_positive_control as e280

PAPER = Path("docs/paper/clfly-v1.md")
#: The finding each correction in the paper should name, per instrument.
INSTRUMENTS = ("e268", "e270", "e277", "e278", "e279", "e280")
CLAIMS = (
    ("C1", "the series runs end to end",
     "Every instrument executes and reads at least one statement of the paper",
     "falsifier: an instrument that cannot run or reads nothing"),
    ("C2", "and the ledger shows bounded, named outstanding work",
     "At most one instrument still flags its statement today",
     "falsifier: three or more still flagging"),
    ("C3", "and every instrument that stopped flagging did so because the paper was corrected",
     "For each clean instrument the paper carries a correction clause naming its finding",
     "falsifier: an instrument that stopped flagging while the paper's sentence is unchanged"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def ledger() -> list[dict]:
    """Each instrument: what it reads, whether the paper's statement is still uncorrected, and whether a correction
    clause naming it is on the page.

    `stale` is the instrument's OWN criterion for its statement -- a phrase still present with no note beside it, a
    premise still unqualified, a count still over its old denominator -- and not the verdict of its registered claims,
    which for `e278` to `e280` means the unit's own claims hold rather than that the paper is wrong.
    """
    text = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    out: list[dict] = []

    rows = e268.check()
    out.append({"instrument": "e268", "reads": len(rows), "note": "the supersession registry",
                "stale": sum(1 for r in rows if r["in_paper"] and not r["carries_a_note"]),
                "corrected": "CORRECTED 2026-09-28" in text and "CORRECTED 2026-09-29" in text})

    rows = e270.corpus()
    m = e270.judge(rows, text)
    premise = next((r for r in m if r["id"] == "V1"), None)
    out.append({"instrument": "e270", "reads": 1, "note": "the 128-batch premise",
                "stale": 1 if (premise and premise["verdict"].startswith("MET")
                               and "CORRECTED 2026-09-28 by `e270`" not in text) else 0,
                "corrected": "CORRECTED 2026-09-28 by `e270`" in text})

    found = e277.counts(text)
    counts_of = []
    for c in found:
        nums = [int(n.replace(",", "")) for n in c["numbers"]]
        if nums:
            c["stated"] = max(nums)
            c["statement"] = c["matched"]
            counts_of.append(c)
    have = e277.corpora()
    old_counts = [c for c in counts_of if c["noun"] in have and c["stated"] < have[c["noun"]]]
    out.append({"instrument": "e277", "reads": len(counts_of), "note": "the counts over grown denominators",
                "stale": len(old_counts) if "by `e277`" not in text else 0,
                "corrected": "by `e277`" in text})

    rows = e278.population()
    out.append({"instrument": "e278", "reads": len(rows), "note": "the extremum over on disk",
                "stale": 1 if (e278.QUOTED["phrase"] in text and "by `e278`" not in text) else 0,
                "corrected": "by `e278`" in text})

    rows = e279.population()
    out.append({"instrument": "e279", "reads": len(rows), "note": "the universal over an epoch",
                "stale": 1 if ("every one of the 77 stored runs used 16" in text and "by `e279`" not in text) else 0,
                "corrected": "by `e279`" in text})

    d = load(e280.ARTIFACT)
    if d is not None:
        r = e280.reading(d)
        out.append({"instrument": "e280", "reads": r["n"], "note": "the positive control",
                    "stale": 0, "corrected": True})
    return out


def judge(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no instrument reported"} for c in CLAIMS]

    ran = [r for r in rows if r["reads"] > 0]
    out.append({"id": "C1", "measured": f"{len(ran)} of {len(INSTRUMENTS)} instruments ran, reading "
                                        f"{sum(r['reads'] for r in ran)} statements in all: "
                                        + ", ".join(f"{r['instrument']} {r['reads']}" for r in rows),
                "verdict": "MET -- every instrument runs and reads" if len(ran) == len(INSTRUMENTS) else
                           f"FALSIFIER FIRED -- {len(ran)} ran"})

    still = [r["instrument"] for r in rows if r["stale"]]
    out.append({"id": "C2", "measured": f"instruments still flagging their statement: {still or 'none'}"
                                        f" ({len(still)} of {len(rows)})",
                "verdict": "MET -- the outstanding work is bounded and named" if len(still) <= 1 else
                           f"FALSIFIER FIRED -- {still}"})

    silent = [r["instrument"] for r in rows if not r["stale"] and not r["corrected"]]
    out.append({"id": "C3", "measured": f"instruments that read clean without a correction in the paper: "
                                        f"{silent or 'none'}; corrections found: "
                                        + ", ".join(f"{r['instrument']} {'yes' if r['corrected'] else 'NO'}"
                                                    for r in rows),
                "verdict": "MET -- every clean instrument's statement carries a correction" if not silent else
                           f"FALSIFIER FIRED -- {silent}"})
    return out


def report(rows: list[dict]) -> int:
    print("== the correction ledger ==")
    print(f"   {'instrument':10} {'reads':>7} {'stale':>6} {'corrected':>10}  what it reads")
    for r in rows:
        print(f"   {r['instrument']:10} {r['reads']:7d} {r['stale']:6d} {str(r['corrected']):>10}  {r['note']}")

    print("\n== the registered claims, C1-C3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a series that reports findings without a ledger cannot tell its outstanding work from its finished")
    print("    work, which is the same defect it audits: a claim whose scope is not stated)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    if not PAPER.exists():
        raise SystemExit(f"need {PAPER}")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rows = ledger()
    if args.json_out:
        write_json(args.json_out, {"paper": str(PAPER), "ledger": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
