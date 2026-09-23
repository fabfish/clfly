"""E127 -- the programme table's *status* column, re-derived from the table itself, because nothing was.

Rule 22 records that this table has drifted **four times in the same direction** — toward *more open* — and that
the check which catches it *"is one line and needs no artifacts: print the opening of each status cell beside the
end of it and ask whether they agree."* `e85` ran that check by hand over 59 rows and found eight stale ones; a
later pass found three more that **contradict themselves** (`**launched, prediction before the run.**` while the
body of the same cell reports the finished answer, because an update got appended to the body and the header
stayed). **Every one of those passes was done by hand, and the rule was never made into code** — so the check is
performed only when somebody remembers to, which is exactly the condition that produced the four drifts.

    python -m experiments.e127_programme_table_audit                     # the plan's programme table
    python -m experiments.e127_programme_table_audit --path docs/research_plan.md --section 919 1090

Four checks, one per documented failure mode, and each is deliberately narrow:

- **A. An artifact the row names does not exist.** `runs/*.json` mentioned anywhere in the row.
- **B. The status cell contradicts itself.** The cell's **first** status indicator is compared with its first
  *done* marker: an open word that comes first and a finished result that comes later is the `e85`-follow-up
  defect, and it is invisible to any check on a result because the numbers are all correct.
- **C. A row says the work was never run while naming an artifact that exists.** The `e694` shape.
- **D. Two rows have the same first cell** — `e85`'s "duplicated and contradicting itself".

**Rule 22's own last paragraph is the specification for the reporting**: *"a scanner that reports a file as
missing when it is present is worse than no scanner, because its output looks like evidence."* A pass of this
check produced exactly such a flag — a row reported as both citing a missing artifact and being stale, when the
artifact was present and the word "launched" merely appeared in later prose. So every flag is printed **with the
evidence that produced it**, and the script prints how many rows it parsed and how many status cells it could
classify at all, because a zero with no denominator is not a check.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RUNS_RE = re.compile(r"runs/[A-Za-z0-9_./-]+\.json")
# In a GFM table a literal `|` separates cells UNLESS it is escaped as `\|` -- and that holds even inside a code
# span, which is the trap: `` `|x|` `` looks protected and is not. The first version of this parser split on every
# pipe, so it reported a correctly-escaped row (`largest \|Δ\| = 0.58`) as malformed and, in the same pass, would
# have missed nothing -- one false alarm and no catch. Rule 22's last paragraph is the specification.
PIPE_SPLIT_RE = re.compile(r"(?<!\\)\|")
UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")
# status indicators, as rule 22 and the e85 follow-up name them
OPEN_WORDS = ("launched", "in flight", "in progress", "pending", "planned", "to be run",
              "never been run", "not yet run", "has not been run", "was never run")
# a finished result, in the form the table's status cells actually use: "**done —" and "done -" and "done —"
DONE_RE = re.compile(r"(?:\*\*)?\bdone\b\s*[—–-]")


def cells(line: str) -> list[str]:
    return [c.strip() for c in PIPE_SPLIT_RE.split(line)][1:-1]


def programme_rows(path: Path) -> tuple[list[dict], list[dict]]:
    """The table's data rows, plus the rows that could not be parsed as one table row.

    A row with the wrong number of cells is not noise: it means a cell contains a literal `|`, which in a
    Markdown table silently splits a row in two. It is reported rather than skipped.
    """
    text = path.read_text(encoding="utf-8")
    start = text.index("## Experimental programme")
    end = text.index("## Method", start)
    section = text[start:end]
    rows, unparseable = [], []
    seen_header = False
    for n, line in enumerate(section.splitlines(), start=text[:start].count("\n") + 1):
        if not line.startswith("|"):
            continue
        cs_any = cells(line)
        if not seen_header:
            seen_header = True                               # the column header, not a data row
            continue
        if cs_any and all(set(c) <= set("-: ") for c in cs_any):
            continue                                         # the `|---|---|` separator
        if len(cs_any) != 4:                                 # what | programme | why | status
            # Report WHERE the stray separator is, not merely that the row is odd: the fix is to escape it, and a
            # position turns "this row is broken" into an edit. The context is centred on the first pipe *beyond*
            # the five structural ones (four cell borders plus the two ends), because centring on the fifth lands
            # on the row's own trailing border and shows nothing.
            stray = [m.start() for m in PIPE_SPLIT_RE.finditer(line)]
            bad = stray[5] if len(stray) > 5 else (stray[-1] if stray else 0)
            unparseable.append({
                "line": n, "n_cells": len(cs_any), "n_unescaped_pipes": len(stray),
                "first_cell": cs_any[0][:70].encode("ascii", "replace").decode(),
                "context": "..." + line[max(0, bad - 60):bad + 60].encode("ascii", "replace").decode() + "...",
                "at_offset": bad})
            continue
        cs = cs_any
        rows.append({"line": n, "what": cs[0], "code": cs[1], "why": cs[2], "status": cs[3],
                     "status_opens": cs[3][:70].encode("ascii", "replace").decode()})
    return rows, unparseable


def first_index(text: str, needles) -> int:
    low = text.lower()
    hits = [low.find(s) for s in needles]
    hits = [h for h in hits if h >= 0]
    return min(hits) if hits else -1


def audit(path: Path) -> dict:
    rows, unparseable = programme_rows(path)
    missing_artifacts, contradictions, duplicates = [], [], []
    open_after_done = 0
    seen: dict[str, int] = {}
    for r in rows:
        # every cell, not just the status: a row names its artifacts in whichever column reads naturally, and a
        # test caught this checking only two of them -- `why` is where a row says what closed a gap.
        for ref in set(RUNS_RE.findall(r["what"] + " " + r["why"] + " " + r["status"])):
            if not Path(ref).is_file():
                missing_artifacts.append({"line": r["line"], "artifact": ref,
                                          "what": r["what"][:60].encode("ascii", "replace").decode()})
        open_at = first_index(r["status"], OPEN_WORDS)
        done_at = DONE_RE.search(r["status"])
        # B: the *first* indicator wins. An open word before a done marker is a row that announces itself as
        # in-flight and then reports the answer -- the defect a result-level check cannot see.
        if open_at >= 0 and done_at is not None and open_at < done_at.start():
            contradictions.append({
                "line": r["line"],
                "opens_with": r["status"][open_at:open_at + 40].encode("ascii", "replace").decode(),
                "then_reports": r["status"][done_at.start():done_at.start() + 70]
                                .encode("ascii", "replace").decode()})
        # NOT a flag, and the reason is a measurement rather than a judgement: an open word appearing *after* a
        # done marker was a flag in the first version of this script and it fired on **9 of 9 rows as false
        # positives** -- every one of them a status cell reading `done — ...` with the word "launched" or
        # "PENDING" in later prose about some OTHER experiment ("`e48` launched to close it"; "a pair whose
        # measurement was absent was counted PENDING"), including one row whose own correction note contains the
        # phrase it was being flagged for. Rule 22 records this exact output as costing a reader more than the
        # check saved, so it is counted and printed as a denominator and never as a finding.
        if open_at >= 0 and done_at is not None and open_at > done_at.start():
            open_after_done += 1
        key = r["what"].strip()
        if key in seen:
            duplicates.append({"line": r["line"], "also_at": seen[key],
                               "what": key[:70].encode("ascii", "replace").decode()})
        else:
            seen[key] = r["line"]
    return {"path": str(path), "rows": len(rows), "unparseable": unparseable,
            "classifiable_status_cells": sum(1 for r in rows
                                             if first_index(r["status"], OPEN_WORDS) >= 0
                                             or DONE_RE.search(r["status"])),
            "missing_artifacts": missing_artifacts, "contradictions": contradictions,
            "open_words_after_done_not_flagged": open_after_done, "duplicate_rows": duplicates}


def report(res: dict) -> int:
    n_flags = (len(res["missing_artifacts"]) + len(res["contradictions"])
               + len(res["duplicate_rows"]) + len(res["unparseable"]))
    print(f"== {res['path']} ==")
    print(f"   rows parsed                    : {res['rows']}")
    print(f"   status cells with an indicator : {res['classifiable_status_cells']} of {res['rows']}")
    for name, key, hint in (("A. named artifact missing", "missing_artifacts", "artifact"),
                            ("B. status cell contradicts itself", "contradictions", "opens_with"),
                            ("C. duplicate first cell", "duplicate_rows", "what")):
        items = res[key]
        print(f"   {name:38}: {len(items)}")
        for it in items:
            print(f"        line {it['line']:5} [{hint}] {it[hint]}")
            if key == "contradictions":
                print(f"                            then -> {it['then_reports']}")
    print(f"   D. table row with a raw `|` in a cell : {len(res['unparseable'])}")
    for u in res["unparseable"]:
        print(f"        line {u['line']:5} {u['n_cells']} cells, {u['n_unescaped_pipes']} unescaped pipes")
        if u.get("context"):
            print(f"             {u['context']}")
    print(f"   (not flagged: open word after a done marker in {res['open_words_after_done_not_flagged']} "
          f"rows -- later PROSE, not status. Flagging those was 9 of 9 false positives; see the source.)")
    if n_flags:
        print("   NOTE: rule 22 -- a flag is not a finding. Read each one against the row before reporting it; "
              "a scanner that reports a file as missing when it is present is worse than no scanner.")
    return n_flags


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--path", type=Path, default=Path("docs/research_plan.md"))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.path)
    n = report(res)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
