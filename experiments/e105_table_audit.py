"""E105 -- does a table's arithmetic close, and do its numbers exist in the artifacts?

Two checks over every markdown table in the paper, and they are very different in sharpness.

**Check 1, the sharp one: a contrast column must close against the comparator it names.** If a column is
headed ``vs naive`` and the table has a ``naive`` row, then every other row's cell in that column must equal
that row's own value minus the ``naive`` row's value, in whichever numeric column the two share. This is pure
arithmetic *inside one table*, so it needs no corpus and admits almost no false positive -- and it is what
found the paper's §4.2 by hand, where the column headed ``vs naive`` subtracted **+0.0729 for two rows and
+0.066 for two others** while the table's own ``naive`` row printed +0.066. Two of its four contrasts closed;
two did not, and the tell was internal.

**Check 2, the noisy one: does any artifact field contain a printed number?** This locates cells but cannot
convict them, because a sigma, a ratio and a cost in minutes are all *derived* and belong in a table without
being in any artifact. It is reported as counts and a listing rather than as a verdict, and the reason to keep
it at all is that a table whose cells resolve *and* fail to resolve is worth a reader's eye -- it is how §4.4's
three-of-nine came out, and knowing which cells were which took a hand search.

    python -m experiments.e105_table_audit
    python -m experiments.e105_table_audit --json-out runs/e105_table_audit.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import load_artifacts

NUMBER = re.compile(r"([+\-−]?\d+\.\d+)")
SEPARATOR = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
#: a column header naming the row it contrasts against: "vs naive", "delta vs naive", "vs `naive`"
CONTRAST_HEADER = re.compile(r"(?:vs\.?|versus)\s*`?\**([A-Za-z][\w \-]*)", re.I)
#: ... and the same header saying the column's cells *are* differences: "delta vs the diagonal". Closure is not
#: well-posed for those, because the comparator is a reference outside the table and the table holds no absolute
#: value to subtract from -- see `check_closure`. Distinguished from a missing comparator row, which is a defect.
DELTA_HEADER = re.compile(r"\b(delta|change|difference|\u0394)\b", re.I)
#: the inline form §4.4 prints, in two typographies: `(-0.1042, 6.3σ)` and the arrow form `→ +0.0000 (0.00σ, tie)`.
#: Coverage is *presentation-dependent*, which is why the check prints how many contrasts it examined: an edit
#: that changes how a table prints its contrasts can take this check's coverage to zero without failing
#: anything, and it did exactly that once during this script's own first session.
INLINE_CONTRASTS = (
    re.compile(r"[(\[]\s*([+\-−]?\d+\.\d+)\s*,\s*(?:\d+\.\d+\s*)?σ"),
    re.compile(r"→\s*([+\-−]?\d+\.\d+)\s*\("),
)

SCALAR_FIELDS = ("mean_forgetting", "forgetting_sem", "final_accuracy", "final_sem")
ARRAY_FIELDS = ("learned", "forgetting_per_task", "final_per_task")


def ascii_token(token: str) -> str:
    """The console here is a GBK code page: a U+2212 minus cannot be printed, and these tokens carry one."""
    return token.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")


def numbers_of(cell: str) -> list[tuple[str, float]]:
    """Every number in a cell, with its token -- a contrast cell prints ``value ± sem (contrast, σ)``."""
    out = []
    for token in NUMBER.findall(cell):
        try:
            out.append((ascii_token(token), float(ascii_token(token))))
        except ValueError:
            continue
    return out


def first_number(cell: str):
    """A cell's value: the *first* number in it.

    This paper's convention is ``value ± sem`` and ``value ± sem (contrast, σ)``, so the first number is the
    value in both; requiring a cell to hold exactly one number would skip every cell in §4.4's table, whose
    contrasts are printed inline.
    """
    found = numbers_of(cell)
    return found[0][1] if found else None


def number_of(cell: str):
    """The single number in a cell, or None -- kept for callers that need strictness."""
    found = numbers_of(cell)
    return found[0][1] if len(found) == 1 else None


def tolerance(*tokens: str) -> float:
    """Half a unit in the last place of each printed number, summed: both sides of a subtraction are rounded."""
    return sum(0.5 * 10.0 ** (-len(t.split(".")[1])) for t in tokens) + 1e-9


def label(cell: str) -> str:
    """A cell's text with markup removed, lowercased -- for matching a row against a column's comparator."""
    return re.sub(r"[`*\s]", "", cell).lower()


def check_closure(table: dict) -> dict | None:
    """Verify every contrast cell against the comparator its column names, and report what fails."""
    if len(table["header"]) < 2:
        return None
    header = table["header"]
    targets = {}
    for j, cell in enumerate(header):
        m = CONTRAST_HEADER.search(cell)
        if m:
            targets[j] = m.group(1).strip().rstrip(":")
    if not targets:
        return None

    body = table["rows"][1:]
    findings = []
    for j, comparator in targets.items():
        cmp_rows = [i for i, r in enumerate(body) if any(label(c) == label(comparator) for c in r[1])]
        if not cmp_rows:
            # Two shapes reach here and they are not the same claim. A column headed `vs X` whose table has no
            # `X` row is a **defect**: the contrast has no comparator to close against. A column headed
            # **`delta vs X`** is a different object -- its cells *are* the differences, and the reference's
            # absolute value lives in the surrounding prose, so no pair of the table's own cells can produce
            # them however the table is written. Reporting the second as the first inflated this check's
            # headline count by one on §4.4's basis table; the count is what a reader takes away, so the two are
            # now counted apart, and the not-checkable one is printed with its reason rather than dropped.
            external = bool(DELTA_HEADER.search(header[j]))
            findings.append({"contrast_column": j, "comparator": comparator,
                             "kind": "external reference" if external else "missing comparator row",
                             "status": ("not checkable: the column carries deltas against a comparator that is "
                                        "not a row of this table, so the reference's own value is not here to "
                                        "subtract" if external else "no row matches this comparator")})
            continue
        # A blocked table has one comparator row per block -- §4.4's spans three settings -- so each row is
        # checked against the nearest *preceding* comparator, falling back to the first. Using a single
        # comparator row made every row after the first block look like it failed, which is the same mistake as
        # reading one `naive` for a table whose blocks have three.
        # A column headed "vs X" is ambiguous: it usually carries a difference, but "Spearman vs X" carries a
        # *correlation*, whose comparator row holds 1.000 by construction. Reading that as a difference made
        # the check report a correlation matrix as failing, so a self-correlation diagonal is skipped with the
        # reason recorded rather than guessed at.
        diagonal = first_number(body[cmp_rows[0]][1][j]) if j < len(body[cmp_rows[0]][1]) else None
        if diagonal == 1.0:
            findings.append({"contrast_column": j, "comparator": comparator, "status":
                             "skipped: the comparator row holds 1.000 in this column, so it is a correlation "
                             "diagonal rather than a difference"})
            continue
        rows = []
        for i, r in enumerate(body):
            if i in cmp_rows:
                continue
            cmp_row = max((c for c in cmp_rows if c < i), default=cmp_rows[0])
            cmp_row = body[cmp_row]
            printed_cell = r[1][j] if j < len(r[1]) else ""
            printed_all = numbers_of(printed_cell)
            if not printed_all:
                continue                                   # a dash, a bracket, "no artifact"
            closes, fails = [], []
            for k in range(1, len(header)):
                if k == j:
                    continue
                got, base = first_number(r[1][k]), first_number(cmp_row[1][k])
                if got is None or base is None:
                    continue
                expected = got - base
                # any of the contrast cell's numbers may be the contrast; the cell may also carry a sigma
                hit = next(((tok, v) for tok, v in printed_all
                            if abs(v - expected) <= tolerance(tok, r[1][k], cmp_row[1][k])), None)
                (closes if hit else fails).append(
                    {"column": k, "row_value": got, "comparator_value": base, "expected": expected,
                     "printed": hit[1] if hit else printed_all[0][1],
                     "difference": (hit[1] if hit else printed_all[0][1]) - expected})
            # A row closes if the printed contrast matches the difference in **some** shared column: a table
            # may carry several metrics, and only one of them need be the one the contrast is about. It fails
            # when it matches none -- which is §4.2's block row, whose contrast came from a baseline that is
            # in no column of its own table.
            rows.append({"line": r[0], "printed": printed_all[0][1], "closes": closes, "fails": fails,
                         "verdict": "closes" if closes else ("fails" if fails else "not checkable")})
        findings.append({"contrast_column": j, "comparator": comparator,
                         "comparator_line": cmp_rows[0] if cmp_rows else None, "rows": rows})
    return {"table": [table["start"], table["end"]], "header": header, "findings": findings}


def closure_counts(closures: list[tuple[dict, dict]]) -> dict:
    """The headline numbers of check (a), kept in one place so that they are not re-counted by hand.

    ``failures`` is the sharp count: a row whose printed contrast no pair of cells gives, or a column naming a
    comparator the table does not have. ``not_checkable`` counts the columns that are *differences against an
    external reference* -- a `delta vs X` column -- which no arithmetic inside the table could check and which
    are therefore reported rather than counted as failures.
    """
    failures = not_checkable = rows_closed = 0
    for _t, c in closures:
        for f in c["findings"]:
            if "rows" not in f:
                if f.get("kind") == "missing comparator row":
                    failures += 1
                else:
                    not_checkable += 1
                continue
            fails = [r for r in f["rows"] if r["verdict"] == "fails"]
            failures += len(fails)
            rows_closed += len([r for r in f["rows"] if r["verdict"] == "closes"])
    return {"failures": failures, "not_checkable": not_checkable, "rows_closed": rows_closed,
            "contrast_columns": sum(len(c["findings"]) for _t, c in closures)}


def check_inline_contrasts(table: dict) -> list[dict]:
    """Verify a contrast printed *inside* a measurement cell against its own row's cells.

    §4.4 prints ``−0.0042 ± 0.0091 (−0.1042, 6.3σ)``: no ``vs`` column exists, so `check_closure` cannot see
    it, and that is the table with six unbacked cells. The check available here is **internal to the row** --
    a contrast must equal the difference of two of that row's own numbers -- and it is exactly what was wrong
    in §4.2, whose contrast came from a baseline obtainable from no cell of its own table.
    """
    header = table["header"]
    out = []
    for r in table["rows"][1:]:
        values = [first_number(c) for c in r[1]]
        for cell in r[1]:
            for pattern in INLINE_CONTRASTS:
                for m in pattern.finditer(cell):
                    token = ascii_token(m.group(1))
                    contrast = float(token)
                    closes = []
                    for a in range(1, len(header)):
                        for b in range(1, len(header)):
                            if a == b or values[a] is None or values[b] is None:
                                continue
                            expected = values[a] - values[b]
                            if abs(contrast - expected) <= tolerance(token, r[1][a], r[1][b]):
                                closes.append({"plus_column": a, "minus_column": b, "expected": expected})
                    out.append({"line": r[0], "token": token, "closes": closes,
                                "verdict": "closes" if closes else "no pair of its own cells gives it"})
    return out


def audit_table(table: dict, index: list) -> dict:
    """Check 2's counts: how many printed numbers an artifact field contains, per row."""
    rows = []
    for lineno, cells in table["rows"]:
        matched, unmatched = [], []
        for cell in cells:
            for token in NUMBER.findall(cell):
                hits = locate(index, token)
                (matched if hits else unmatched).append(
                    {"token": ascii_token(token), "hits": hits} if hits else {"token": ascii_token(token)})
        rows.append({"line": lineno, "matched": len(matched), "unmatched": len(unmatched),
                     "unmatched_tokens": sorted({m["token"] for m in unmatched})})
    data = rows[1:]
    n_match = sum(r["matched"] for r in data)
    n_unmatched = sum(r["unmatched"] for r in data)
    return {"start": table["start"], "end": table["end"], "header": table["header"],
            "matched": n_match, "unmatched": n_unmatched, "rows": data,
            "verdict": ("mixed" if n_match and n_unmatched else
                        "all located" if n_match else "nothing located" if n_unmatched else "no numbers")}


def corpus_index(artifacts: list[dict]) -> list[tuple[float, str, str]]:
    """Every scalar an artifact records, as ``(value, field, source)``."""
    index = []
    for a in artifacts:
        for method, entry in sorted((a["payload"].get("methods") or {}).items()):
            if not isinstance(entry, dict):
                continue
            for field in SCALAR_FIELDS:
                v = entry.get(field)
                if isinstance(v, (int, float)):
                    index.append((float(v), field, f"{a['name']}:{method}"))
            for field in ARRAY_FIELDS:
                for i, v in enumerate(entry.get(field) or []):
                    if isinstance(v, (int, float)):
                        index.append((float(v), f"{field}[{i}]", f"{a['name']}:{method}"))
    return index


def locate(index: list, token: str, hits: int = 4) -> list[list[str]]:
    """Artifact fields containing ``token``, at the precision printed (half a unit in the last place)."""
    value = float(ascii_token(token))
    tol = 0.5 * 10.0 ** (-len(token.split(".")[1])) * (1 + 1e-9)
    return [[f, s] for f, s in sorted({(f, s) for v, f, s in index if abs(v - value) <= tol})][:hits]


def parse_tables(text: str) -> list[dict]:
    """Every markdown table, as rows of ``(line number, cells)`` with the first row as the header."""
    tables, current = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("|"):
            if SEPARATOR.match(line):
                continue
            current.append((lineno, [c.strip() for c in line.strip().strip("|").split("|")]))
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return [{"start": rows[0][0], "end": rows[-1][0], "header": rows[0][1], "rows": rows}
            for rows in tables]


def scan_findings(directory: Path, index: list, share: float) -> dict:
    """Run both checks over every findings document, and count the shapes that matter at corpus level.

    The paper is audited and the corpus of findings is not, which is the gap this mode closes. Its useful
    output is not a per-document verdict -- a findings document is mostly prose and derived arithmetic -- but
    three corpus counts: how many documents have a contrast that fails to close, how many have a table with a
    substantial located fraction and cells that do not locate, and how many are entirely unlocatable.
    """
    docs, closure_failures, mixed, silent = [], [], [], []
    for path in sorted(directory.glob("*.md")):
        tables = parse_tables(path.read_text(encoding="utf-8", errors="replace"))
        doc = {"document": path.name, "tables": len(tables), "closure_failures": [], "mixed": [],
               "matched": 0, "unmatched": 0}
        for t in tables:
            for r in check_inline_contrasts(t):
                if r["verdict"] != "closes":
                    doc["closure_failures"].append({"lines": [t["start"], t["end"]], "token": r["token"]})
            c = check_closure(t)
            if c:
                for f in c["findings"]:
                    for row in f.get("rows", []):
                        if row["verdict"] == "fails":
                            doc["closure_failures"].append(
                                {"lines": [t["start"], t["end"]], "token": f"{row['printed']:+.4f}",
                                 "against": f["comparator"]})
            a = audit_table(t, index)
            doc["matched"] += a["matched"]
            doc["unmatched"] += a["unmatched"]
            total = a["matched"] + a["unmatched"]
            if total and a["unmatched"] and a["matched"] >= 3 and a["matched"] / total >= share:
                doc["mixed"].append({"lines": [a["start"], a["end"]], "matched": a["matched"],
                                     "unmatched": a["unmatched"], "share": a["matched"] / total,
                                     "unmatched_tokens": sorted(
                                         {tok for r in a["rows"] for tok in r["unmatched_tokens"]})[:12]})
        if doc["closure_failures"]:
            closure_failures.append(doc)
        if doc["mixed"]:
            mixed.append(doc)
        if doc["matched"] + doc["unmatched"] and not doc["matched"]:
            silent.append(doc)
        docs.append(doc)
    return {"documents": docs, "n_documents": len(docs),
            "with_closure_failures": closure_failures, "with_mixed_tables": mixed,
            "entirely_unlocated": silent}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paper", type=Path, default=Path("docs/paper/clfly-v1.md"))
    p.add_argument("--findings", type=Path, default=None,
                   help="also audit every markdown table under this directory, which is the gap e105's own "
                        "finding named: the paper is audited and the corpus of findings is not")
    p.add_argument("--share", type=float, default=0.25,
                   help="a table is listed as interesting when at least this share of its numbers locate")
    p.add_argument("--runs", type=Path, default=Path("runs"))
    p.add_argument("--skip", default="e105_table_audit.json,e103_reproducibility_audit.json")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    skip = tuple(s for s in args.skip.split(",") if s)
    index = corpus_index(load_artifacts(args.runs, skip=skip))
    tables = parse_tables(args.paper.read_text(encoding="utf-8"))
    closures = [(t, check_closure(t)) for t in tables]
    closures = [(t, c) for t, c in closures if c]
    located = [audit_table(t, index) for t in tables]

    print("=" * 104)
    print("1. CONTRAST COLUMNS: does each close against the comparator its header names?")
    print("=" * 104)
    print("   (a) columns headed 'vs X'")
    for t, c in closures:
        for f in c["findings"]:
            if "rows" not in f:
                if f.get("kind") == "missing comparator row":
                    print(f"   lines {t['start']}-{t['end']}: column {f['contrast_column']} names "
                          f"'{f['comparator']}' but {f['status']}")
                else:
                    print(f"   lines {t['start']}-{t['end']}: column {f['contrast_column']} names "
                          f"'{f['comparator']}' -- {f['status']}")
                continue
            fails = [r for r in f["rows"] if r["verdict"] == "fails"]
            oks = [r for r in f["rows"] if r["verdict"] == "closes"]
            tag = "CLOSES" if not fails else f"**{len(fails)} OF {len(fails) + len(oks)} DO NOT CLOSE**"
            print(f"   lines {t['start']}-{t['end']}: column 'vs {f['comparator']}' "
                  f"(row line {f['comparator_line']})  -> {tag}")
            for r in fails:
                for c_ in r["fails"]:
                    print(f"       line {r['line']:4}: printed {r['printed']:+.4f}  table says "
                          f"{c_['row_value']:.4f} - {c_['comparator_value']:.4f} = {c_['expected']:+.4f}  "
                          f"(off by {c_['difference']:+.4f})")
    if not closures:
        print("   (no table has a contrast column)")

    print()
    print("   (b) contrasts printed inside a measurement cell, e.g. '(contrast, 6.3σ)'")
    inline_bad = 0
    inline_checked = 0
    for t in tables:
        for r in check_inline_contrasts(t):
            inline_checked += 1
            if r["verdict"] != "closes":
                print(f"   lines {t['start']}-{t['end']}: line {r['line']:4} prints {r['token']} "
                      f"and {r['verdict']}")
                inline_bad += 1
    # the denominator, because a count of zero is otherwise indistinguishable from "the check never fired"
    print(f"   inline contrasts checked: {inline_checked}, of which no pair of their own row's cells "
          f"gives them: {inline_bad}")

    counts = closure_counts(closures)
    print(f"\n   check (a) failures: {counts['failures']}, over {counts['contrast_columns']} contrast "
          f"column(s) and {counts['rows_closed']} row(s) that close;")
    print(f"   check (a) NOT CHECKABLE: {counts['not_checkable']} -- a `delta vs X` column holds the "
          f"differences themselves, so no pair of its own cells can give them;")
    print(f"   check (b) failures: {inline_bad} of {inline_checked}")

    print()
    print("=" * 104)
    print("2. LOCATION ONLY -- a number an artifact field contains.  Unmatched is NOT unbacked: a sigma, a")
    print("   ratio and a cost are all derived.  Listed are the tables where at least a quarter of their")
    print("   numbers resolve, which is the reading aid that keeps this section short; the JSON holds all.")
    print("=" * 104)
    interesting = [t for t in located
                   if t["verdict"] == "mixed" and t["matched"] >= 3
                   and t["matched"] / (t["matched"] + t["unmatched"]) >= 0.25]
    for t in sorted(interesting, key=lambda t: -(t["matched"] / (t["matched"] + t["unmatched"]))):
        share = t["matched"] / (t["matched"] + t["unmatched"])
        print(f"\n   lines {t['start']}-{t['end']}  {t['matched']} located, {t['unmatched']} not"
              f" ({share:.0%} located)   header: {' | '.join(t['header'])[:90]}")
        for r in t["rows"]:
            if r["unmatched_tokens"]:
                print(f"     line {r['line']:4}: {', '.join(r['unmatched_tokens'])[:100]}")
    counts: dict[str, int] = {}
    for t in located:
        counts[t["verdict"]] = counts.get(t["verdict"], 0) + 1
    print(f"\n   verdicts over {len(located)} tables: {counts}")
    print(f"   tables listed above: {len(interesting)} of {counts.get('mixed', 0)} mixed")

    findings = None
    if args.findings:
        findings = scan_findings(args.findings, index, args.share)
        print()
        print("=" * 104)
        print("3. THE FINDINGS CORPUS, which the paper's audit does not cover")
        print("=" * 104)
        print(f"   documents: {findings['n_documents']}")
        print(f"   with a table whose contrasts FAIL to close: {len(findings['with_closure_failures'])}")
        print(f"   with a table that is >= {args.share:.0%} located and has cells that do not locate: "
              f"{len(findings['with_mixed_tables'])}")
        print(f"   with tables but not one number locating: {len(findings['entirely_unlocated'])}")
        print()
        print("   closure failures (a contrast no pair of its own row's cells gives):")
        for doc in findings["with_closure_failures"]:
            print(f"     {doc['document']}")
            for f in doc["closure_failures"][:4]:
                print(f"        lines {f['lines'][0]}-{f['lines'][1]}: {f.get('token')}"
                      + (f" against {f['against']}" if f.get("against") else ""))
        print()
        print("   the most-located mixed tables, i.e. the ones where a cell that does not locate sits beside "
              "cells that do:")
        ranked = sorted((d for d in findings["with_mixed_tables"]),
                        key=lambda d: -(d["matched"] / max(1, d["matched"] + d["unmatched"])))
        for doc in ranked[:8]:
            best = max(doc["mixed"], key=lambda m: m["share"])
            print(f"     {doc['document']:60} {best['matched']:3} located, {best['unmatched']:3} not "
                  f"({best['share']:.0%})")

    if args.json_out:
        write_json(args.json_out, {"paper": str(args.paper), "n_indexed": len(index),
                                   "closure_counts": counts, "inline_contrasts": {
                                       "checked": inline_checked, "failing": inline_bad},
                                   "closures": [c for _, c in closures], "tables": located,
                                   **({"findings": findings} if findings else {})})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
