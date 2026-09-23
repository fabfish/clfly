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
#: ... and the same header saying the column's cells *are* differences: "delta vs the diagonal", "gap vs oracle",
#: "contrast vs swap0.5". Closure is not well-posed for those, because the comparator is a reference outside the
#: table and the table holds no absolute value to subtract from -- see `check_closure`. Distinguished from a
#: header naming two columns, which is not a contrast column at all, and from a correlation, which is not a
#: difference.
DELTA_HEADER = re.compile(r"\b(delta|change|difference|gap|contrast|\u0394)\b", re.I)
#: a header naming a *correlation* rather than a difference. "Spearman vs measured draw sd" compares two columns
#: of the same row, so its second half is a column name and there is no comparator row to close against -- which
#: is how the corpus's six such columns were being read as contrasts against rows that do not exist.
CORRELATION_HEADER = re.compile(r"\b(spearman|pearson|correlation|corr|rank)\b", re.I)
#: the inline form §4.4 prints, in two typographies: `(-0.1042, 6.3σ)` and the arrow form `→ +0.0000 (0.00σ, tie)`.
#: Coverage is *presentation-dependent*, which is why the check prints how many contrasts it examined: an edit
#: that changes how a table prints its contrasts can take this check's coverage to zero without failing
#: anything, and it did exactly that once during this script's own first session.
INLINE_CONTRASTS = (
    re.compile(r"[(\[]\s*([+\-−]?\d+\.\d+)\s*,\s*(?:\d+\.\d+\s*)?σ"),
    re.compile(r"→\s*([+\-−]?\d+\.\d+)\s*\("),
)

SCALAR_FIELDS = ("mean_forgetting", "forgetting_sem", "final_accuracy", "final_sem")
#: Every array the runner writes per method, not a subset of them. It *was* a subset -- `theta_drift`,
#: `bias_step`, `bias_from_zero` and `full_train_loss` were missing -- and the paper quotes three drift values
#: (`2026-09-24`, the body's-motion table) that this listing therefore called **unmatched**: the numbers were in
#: the artifacts all along, in a field the index did not read. One of the three located anyway, because a
#: per-task entry happened to equal the mean, which is how a coverage gap looks like a coincidence.
ARRAY_FIELDS = ("learned", "forgetting_per_task", "final_per_task", "theta_drift", "bias_step", "bias_from_zero",
                "full_train_loss")


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
    """Half a unit in the last place of each printed number, summed: both sides of a subtraction are rounded.

    A token without a decimal point contributes nothing rather than raising: the tolerance is called with a
    comparator cell, and a column that carries a contrast against a value the *header* holds passes an empty
    string there.
    """
    return sum(0.5 * 10.0 ** (-len(t.split(".")[1]))
               for t in tokens if "." in t) + 1e-9


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
            targets[j] = {"comparator": m.group(1).strip().rstrip(":"), "start": m.start()}
    if not targets:
        return None

    body = table["rows"][1:]
    findings = []
    for j, t in targets.items():
        comparator, start = t["comparator"], t["start"]
        head_cell = header[j]
        # A header containing a correlation word names a *correlation*, not a difference -- "Spearman vs
        # measured draw sd" compares two columns of the same row and has no comparator row to close against.
        # The row-based version of this (a comparator row holding 1.000) is handled below; this one catches the
        # case where the second half of the header is a column name rather than a row name, which is how the
        # corpus's six `Spearman vs X` columns were being read as contrasts against missing rows.
        if CORRELATION_HEADER.search(head_cell):
            findings.append({"contrast_column": j, "comparator": comparator, "kind": "correlation",
                             "status": "skipped: the header names a correlation, so the column is a correlation "
                                       "and not a difference against a comparator row"})
            continue
        # A comparator row may be written with decoration -- "— (naive)" in a table whose naive row is anonymous
        # -- so an exact label match is tried first and a whole-word containment second. The arithmetic still
        # has to close afterwards, so a wrong match shows up as a failing row rather than as a silent pass.
        cmp_rows = [i for i, r in enumerate(body) if any(label(c) == label(comparator) for c in r[1])]
        loose = False
        if not cmp_rows:
            pat = re.compile(r"\b" + re.escape(re.sub(r"[`*\s]", " ", comparator).strip()) + r"\b", re.I)
            cmp_rows = [i for i, r in enumerate(body)
                        if any(pat.search(re.sub(r"[`*]", " ", c)) for c in r[1])]
            loose = bool(cmp_rows)
        # ... and the header itself may carry the comparator's value, as "vs printed `naive` (+0.066)" does. Then
        # closure IS checkable: the reference is the number in the parentheses, and every other column is
        # subtracted from it. This is how two of the corpus's flagged tables turned out to close all along.
        # **Only a parenthesised number counts**: a bare number in the header is part of the comparator's *name*
        # far more often than it is a value -- `contrast vs swap0.5` names a rewiring level, and reading its 0.5
        # as a reference made four rows of that table "fail" against an arithmetic nobody had written.
        ref = None
        if not cmp_rows:
            m_ref = re.search(r"\(\s*([+\-\u2212]?\d+\.\d+)", head_cell[start:])
            ref = float(ascii_token(m_ref.group(1))) if m_ref else None
        if not cmp_rows and ref is None:
            # Two shapes reach here and they are not the same claim. A column headed `vs X` whose table has no
            # `X` row is a **defect**: the contrast has no comparator to close against. A column headed
            # **`delta vs X`** -- or `gap vs X`, `contrast vs X` -- is a different object: its cells *are* the
            # differences, and the reference's absolute value lives in the surrounding prose, so no pair of the
            # table's own cells can produce them however the table is written. A third shape reaches here too
            # and is neither: a header naming **two columns** ("absolute pressure sd vs measured sd") describes a
            # within-row comparison, so it is not a contrast column at all. Reporting all three as the first
            # inflated this check's headline, which is the number a reader takes away -- so they are counted
            # apart and each is printed with its reason rather than dropped.
            prefix = head_cell[:start].strip().rstrip("(`*")
            if prefix and not DELTA_HEADER.search(prefix):
                kind, status = "two-column comparison", (
                    "skipped: the header names two quantities rather than a comparator row, so the column "
                    "compares cells within a row and is not a contrast against a row")
            elif prefix:
                kind, status = "delta column (external reference)", (
                    "not checkable: the column carries differences against a comparator that is not a row of "
                    "this table, so the reference's own value is not here to subtract")
            else:
                kind, status = "comparator value not in the table", (
                    "not checkable: the comparator's value is in no row of this table and the header does not "
                    "carry it either -- which is a table whose comparator is in another artifact as readily as "
                    "it is a table that forgot to print it, and this check cannot tell the two apart")
            findings.append({"contrast_column": j, "comparator": comparator, "kind": kind, "status": status})
            continue
        # A blocked table has one comparator row per block -- §4.4's spans three settings -- so each row is
        # checked against the nearest *preceding* comparator, falling back to the first. Using a single
        # comparator row made every row after the first block look like it failed, which is the same mistake as
        # reading one `naive` for a table whose blocks have three.
        # A column headed "vs X" is ambiguous: it usually carries a difference, but "Spearman vs X" carries a
        # *correlation*, whose comparator row holds 1.000 by construction. Reading that as a difference made
        # the check report a correlation matrix as failing, so a self-correlation diagonal is skipped with the
        # reason recorded rather than guessed at.
        diagonal = (first_number(body[cmp_rows[0]][1][j])
                    if cmp_rows and j < len(body[cmp_rows[0]][1]) else None)
        if diagonal == 1.0:
            findings.append({"contrast_column": j, "comparator": comparator, "kind": "correlation",
                             "status":
                             "skipped: the comparator row holds 1.000 in this column, so it is a correlation "
                             "diagonal rather than a difference"})
            continue
        # With the reference taken from the header there is no comparator row to subtract, so the tolerance's
        # comparator side is empty and the check runs against the header's own value for every column.
        cmp_source = body[cmp_rows[0]] if cmp_rows else (0, [""] * len(header))
        rows = []
        for i, r in enumerate(body):
            if i in cmp_rows:
                continue
            cmp_row = body[max((c for c in cmp_rows if c < i), default=cmp_rows[0])] if cmp_rows else cmp_source
            printed_cell = r[1][j] if j < len(r[1]) else ""
            printed_all = numbers_of(printed_cell)
            if not printed_all:
                continue                                   # a dash, a bracket, "no artifact"
            closes, fails = [], []
            for k in range(1, len(header)):
                if k == j:
                    continue
                got = first_number(r[1][k])
                base = ref if ref is not None else first_number(cmp_row[1][k])
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
                         "comparator_line": cmp_rows[0] if cmp_rows else None,
                         "comparator_source": ("row" if not loose else "decorated row label")
                                             if ref is None else "value in the header",
                         "rows": rows})
    return {"table": [table["start"], table["end"]], "header": header, "findings": findings}


def closure_counts(closures: list[tuple[dict, dict]]) -> dict:
    """The headline numbers of check (a), kept in one place so that they are not re-counted by hand.

    ``failures`` is the sharp count, and after the corpus evidence it is the *only* defect class the check can
    claim: **a row whose printed contrast no pair of its own cells gives**. A contrast column with no comparator
    row is reported as **not checkable** with its reason rather than as a failure, because the tool cannot tell a
    table that forgot its comparator row from one whose comparator lives in another artifact -- and claiming the
    first when it is the second is exactly the false positive that inflated this check's headline on §4.4.
    ``not_checkable`` is the count of those columns, broken down by reason so that a change in the mix is
    visible: a `delta vs X` column, a comparator whose value is nowhere in the table, a header naming two
    quantities, and a correlation.
    """
    failures = rows_closed = 0
    by_kind: dict[str, int] = {}
    for _t, c in closures:
        for f in c["findings"]:
            if "rows" not in f:
                by_kind[f.get("kind", "unspecified")] = by_kind.get(f.get("kind", "unspecified"), 0) + 1
                continue
            fails = [r for r in f["rows"] if r["verdict"] == "fails"]
            failures += len(fails)
            rows_closed += len([r for r in f["rows"] if r["verdict"] == "closes"])
    return {"failures": failures, "not_checkable": sum(by_kind.values()), "not_checkable_by_kind": by_kind,
            "rows_closed": rows_closed,
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


def audit_table(table: dict, index: list, aggregate_index: list | None = None) -> dict:
    """Check 2's counts: how many printed numbers an artifact field contains, per row.

    Three buckets rather than two, because "an artifact field holds this number" and "an artifact **averages**
    to this number" are different claims and a number can be backed by either. ``aggregate_index`` is consulted
    only for tokens the direct index misses, so nothing moves out of the first bucket.
    """
    rows = []
    for lineno, cells in table["rows"]:
        matched, aggregate, unmatched = [], [], []
        for cell in cells:
            for token in NUMBER.findall(cell):
                hits = locate(index, token)
                if hits:
                    matched.append({"token": ascii_token(token), "hits": hits})
                    continue
                agg = locate(aggregate_index, token) if aggregate_index else []
                (aggregate if agg else unmatched).append(
                    {"token": ascii_token(token), "hits": agg} if agg
                    else {"token": ascii_token(token)})
        rows.append({"line": lineno, "matched": len(matched), "aggregate": len(aggregate),
                     "unmatched": len(unmatched),
                     "unmatched_tokens": sorted({m["token"] for m in unmatched}),
                     "aggregate_tokens": sorted({m["token"] for m in aggregate})})
    data = rows[1:]
    n_match = sum(r["matched"] for r in data)
    n_agg = sum(r["aggregate"] for r in data)
    n_unmatched = sum(r["unmatched"] for r in data)
    return {"start": table["start"], "end": table["end"], "header": table["header"],
            "matched": n_match, "aggregate": n_agg, "unmatched": n_unmatched, "rows": data,
            "verdict": ("mixed" if (n_match or n_agg) and n_unmatched else
                        "all located" if n_match and n_agg == 0 else
                        "all located or aggregated" if n_match or n_agg else
                        "nothing located" if n_unmatched else "no numbers")}


def corpus_index(artifacts: list[dict], aggregates: bool = False) -> list[tuple[float, str, str]]:
    """Every scalar an artifact records, as ``(value, field, source)``.

    ``aggregates`` adds one *derived* entry per array field: its mean. A table that prints an array's mean over
    its elements -- as the body's-motion table does for `theta_drift`, 0.0195 against a stored
    `[0.0197, 0.0187, 0.0201]` -- is backed by the artifact and by no *field*, so reading those as unmatched
    understates how much of the corpus resolves. They are kept in a **separate index** rather than mixed in, so
    that "located" and "located once you average" stay two different answers.
    """
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
                values = [v for v in (entry.get(field) or []) if isinstance(v, (int, float))]
                for i, v in enumerate(values):
                    index.append((float(v), f"{field}[{i}]", f"{a['name']}:{method}"))
                if aggregates and len(values) > 1:
                    index.append((sum(values) / len(values), f"{field}[mean]",
                                  f"{a['name']}:{method}"))
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
               "not_checkable": [], "matched": 0, "unmatched": 0}
        for t in tables:
            for r in check_inline_contrasts(t):
                if r["verdict"] != "closes":
                    doc["closure_failures"].append({"lines": [t["start"], t["end"]], "token": r["token"]})
            c = check_closure(t)
            if c:
                for f in c["findings"]:
                    if "rows" not in f:
                        # The corpus mode used to skip every finding without rows, which made **all** of these
                        # invisible here -- a `delta vs X` column, a header naming two columns, a correlation,
                        # and a column naming a comparator its table does not have, which *is* the shape the
                        # corpus's own count called zero. Now the same split as the paper's mode: a failing row
                        # is the only defect the check claims, and every unchecked column is counted with its
                        # reason.
                        entry = {"lines": [t["start"], t["end"]],
                                 "token": f"column {f['contrast_column']}: {f['comparator']}",
                                 "kind": f.get("kind")}
                        doc["not_checkable"].append(entry)
                        continue
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
            "entirely_unlocated": silent,
            "with_not_checkable_columns": [d for d in docs if d["not_checkable"]]}


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
    # The same index plus one derived entry per array field: its mean. Kept apart so that "an artifact field
    # holds this number" and "an artifact averages to this number" are two answers rather than one -- and so
    # that a table whose cells are element-means is not reported as unmatched.
    agg_index = corpus_index(load_artifacts(args.runs, skip=skip), aggregates=True)
    tables = parse_tables(args.paper.read_text(encoding="utf-8"))
    closures = [(t, check_closure(t)) for t in tables]
    closures = [(t, c) for t, c in closures if c]
    located = [audit_table(t, index, agg_index) for t in tables]

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
    kinds = ", ".join(f"{v} {k}" for k, v in sorted(counts["not_checkable_by_kind"].items()))
    print(f"\n   check (a) failures: {counts['failures']}, over {counts['contrast_columns']} contrast "
          f"column(s) and {counts['rows_closed']} row(s) that close;")
    print(f"   check (a) NOT CHECKABLE: {counts['not_checkable']} column(s) -- reported with the reason rather "
          f"than counted as failures, because the check cannot tell a missing comparator row from one whose "
          f"value is in another artifact: {kinds or 'none'};")
    print(f"   check (b) failures: {inline_bad} of {inline_checked}")

    print()
    print("=" * 104)
    print("2. LOCATION ONLY -- a number an artifact field contains.  Unmatched is NOT unbacked: a sigma, a")
    print("   ratio and a cost are all derived.  Listed are the tables where at least a quarter of their")
    print("   numbers resolve, which is the reading aid that keeps this section short; the JSON holds all.")
    print("=" * 104)
    interesting = [t for t in located
                   if t["verdict"] == "mixed" and t["matched"] + t["aggregate"] >= 3
                   and (t["matched"] + t["aggregate"])
                   / (t["matched"] + t["aggregate"] + t["unmatched"]) >= 0.25]
    for t in sorted(interesting,
                    key=lambda t: -((t["matched"] + t["aggregate"])
                                    / (t["matched"] + t["aggregate"] + t["unmatched"]))):
        share = (t["matched"] + t["aggregate"]) / (t["matched"] + t["aggregate"] + t["unmatched"])
        print(f"\n   lines {t['start']}-{t['end']}  {t['matched']} located, {t['aggregate']} as an array's mean,"
              f" {t['unmatched']} not ({share:.0%} resolved)   header: {' | '.join(t['header'])[:80]}")
        for r in t["rows"]:
            if r["aggregate_tokens"]:
                print(f"     line {r['line']:4}: only as a mean: {', '.join(r['aggregate_tokens'])[:80]}")
            if r["unmatched_tokens"]:
                print(f"     line {r['line']:4}: unmatched: {', '.join(r['unmatched_tokens'])[:90]}")
    counts: dict[str, int] = {}
    for t in located:
        counts[t["verdict"]] = counts.get(t["verdict"], 0) + 1
    n_agg = sum(t["aggregate"] for t in located)
    print(f"\n   verdicts over {len(located)} tables: {counts}")
    print(f"   cells that resolve only as an array field's mean: {n_agg} "
          f"(a derived entry, counted apart from a field that holds the number)")
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
        by_kind: dict[str, int] = {}
        for d in findings["with_not_checkable_columns"]:
            for e in d["not_checkable"]:
                by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1
        print(f"   with a contrast column whose arithmetic could NOT be checked, i.e. not a failure and not a "
              f"verification: {len(findings['with_not_checkable_columns'])} document(s)")
        print(f"     by reason: {by_kind or 'none'}")
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
