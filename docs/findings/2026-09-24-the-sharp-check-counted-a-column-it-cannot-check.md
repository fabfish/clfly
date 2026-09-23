# `e105`'s sharp check counted a column it cannot check

**Date:** 2026-09-24
**Script:** `experiments/e105_table_audit.py` — `check_closure`, the new `closure_counts`, and the report.
**Tests:** `tests/test_table_audit.py`, three new cases (20 pass in the file).
**Trigger:** a routine re-run of the five audits printed `check (a) failures: 1` for the paper, while the
programme table's own row for this tool recorded the check as covering **one** table and reporting **CLOSES** on
all four rows.

---

## 1. What the failure was

The flagged column is §4.4's basis table, `docs/paper/clfly-v1.md:760-765`:

```
| basis | delta vs the diagonal | σ (18 seeds, paired) | signs | LOO min σ | leverage |
```

The auditor reported *"column 1 names 'the diagonal' but no row matches this comparator"* and counted it as a
failure. **But the column's cells *are* the differences** — `+0.00472`, `+0.00469`, `+0.00458`, `−0.00491` — and
the reference they are differences from is a *method*, not a basis, so it has no row here and never could. No pair
of cells in that table can produce those four numbers, however the table is written, because the table holds
**no absolute value** to subtract from; the diagonal's own `+0.01762` is in the prose below (line 773) and in a
paragraph above (line 744). **So the check's verdict was false, and the number a reader takes away — "check (a)
failures: 1" — was wrong.**

## 2. The two shapes were sharing one number, and they are not the same claim

- **A missing comparator row is a defect.** A column headed `vs naive` in a table with no `naive` row is a
  contrast nothing can close against, and the sharp check exists to say so.
- **A `delta vs X` column is not checkable, and that is a property of the column, not a fault in the table.**
  The cell is the answer; the question is elsewhere.

Counting them together meant that the *reason* for the headline was invisible, which is the same defect the
check's own output already guards against one level down (`check (b)` prints its denominator, `0 of 4` rather
than `0`, so that a check which never fired cannot look like a clean bill). **The count of a check is itself a
claim and needs the same treatment as a cell.**

## 3. The change, and it is narrow

`DELTA_HEADER` recognises a header that says the column *is* a difference (`delta`, `change`, `difference`, `Δ`,
before the `vs`). When such a column has no comparator row, the finding is recorded with
`"kind": "external reference"` and a status saying closure is **not checkable** and why; a column whose header
does not say that keeps the old `"kind": "missing comparator row"` and the old status. A new pure function,
`closure_counts(closures)`, returns `failures`, `not_checkable`, `rows_closed` and `contrast_columns`, and the
report prints them on separate lines — so the headline is now `failures: 0` beside
`NOT CHECKABLE: 1`, and the JSON carries both. **The exemption cannot be used to hide a bad number**: a `delta`
column whose comparator *row does exist* is still checked cell by cell, and a test asserts that a failing row in
such a column is still counted as a failure.

## 4. What the re-run now says, re-derived rather than remembered

| scope | before this fire | now |
|---|---|---|
| paper, tables | 18 (`2` all located / `6` none / `10` mixed) | **27** (**3** / **5** / **19**) |
| paper, check (a) | "1 table with a `vs` column, CLOSES on 4 rows" | **2 columns: 0 failures, 1 not checkable, 4 rows close** |
| paper, check (b) | 4 inline contrasts, 0 failing | **6 inline contrasts, 0 failing** |
| findings corpus | 133 documents | **187 documents, 0 with a closure failure** |

**The programme table's row for this tool was stale in four separate counts** — not wrong when written, and
nobody had re-derived them, which is rule 33's point arriving at the audit layer rather than at the findings
layer. The row is corrected in the same fire.

## 5. And it opens one arithmetic question in §4.4

With the delta column no longer counted as a *failure*, it is still not checked, and the arithmetic that would
check it is available: the diagonal's `+0.01762` plus the four deltas gives **0.02234**, **0.02231**,
**0.02220**, **0.01271**. The prose below calls the worst candidate *"+0.0222 against the diagonal's
+0.01762"* — which is the **third** of those, not the largest, while the table's own deltas make `rank4`
(+0.00472) the largest.

**Two readings, and this fire does not choose between them.** Either the prose's `+0.0222` is the worst
candidate's value and one of the two numbers is off by **0.00014**, or the worst of the fourteen is a candidate
**not in this table** and `0.01762 + 0.00458 = 0.02220` is a coincidence at the fifth decimal — plausible, with
fourteen candidates spanning 0.0127 to 0.0223, but worth writing down rather than waving at. **What would settle
it is `e66`'s per-seed storage plus the identity of the fourteen**, neither of which this fire opened, so it is
recorded as an **open item** rather than reported as a defect: a number that cannot be checked from the table it
sits in is exactly the shape this whole check exists for, and §5 is the first thing it caught after ceasing to
count it wrongly.

## 6. What this does not change

- **It is not a repair of the paper.** Check (a) going from 1 to 0 is a change in the **tool**; no table was
  edited. The paper's only other contrast column, §4.2's `vs naive`, closes on all four rows, before and after.
- **Check (b) and check (c) are untouched**, and the findings corpus's zero is unchanged in both runs.
- **The check is weaker than it was, in the honest direction**: one column that was "failing" is now "not
  checkable", which is a *smaller* claim about the paper, not a larger one. The compensating measurement is that
  the not-checkable count is printed rather than dropped, so the next `delta vs X` column added to the paper
  appears in the report as itself.
