# The corpus count was blind to fifteen columns — and three of them close

**Date:** 2026-09-24
**Script:** `experiments/e105_table_audit.py` — `check_closure`, `closure_counts`, `scan_findings`, `tolerance`.
**Tests:** `tests/test_table_audit.py`, 26 pass in the file (10 of them added across this fire and the last).
**Supersedes, on one point:** `docs/findings/2026-09-24-the-sharp-check-counted-a-column-it-cannot-check.md` §2,
which classified a column with no comparator row as a *defect* and counted it as a failure.
**Trigger:** the previous fire gave the paper's mode a `not_checkable` bucket and left the corpus mode alone —
and the corpus mode skipped **every** finding without rows, so its quoted zero was a count over rows only.

---

## 1. What opening it produced

Counting the shapes the corpus had been skipping turned "0 closure failures" into **12 documents and 15 columns**
in one run. Reading all fifteen by hand — which is what the count is for — gives four kinds, and **most are not
defects at all**:

| kind | columns | example header | why |
|---|---|---|---|
| **delta column (external reference)** | **5** | `delta vs the diagonal`, `gap vs oracle`, `contrast vs swap0.5` | the cells *are* the differences; the reference's value is in the prose |
| **correlation** | **5** | `Spearman vs measured draw sd`, `Spearman vs concentration` | a correlation, not a subtraction, and the second half is a *column* name |
| **two-column comparison** | **3** | `absolute pressure sd vs measured sd` | the header names two quantities, so it is not a contrast against a row |
| **comparator value not in the table** | **2** | `vs matched random`, `vs naive (paired)` | the comparator is a row of another table or of the prose |

**And three columns that the old corpus path could not see now close**, which is the opposite direction from the
previous fire:

- `2026-09-23-the-frozen-body-control-is-in-no-artifact.md`, columns 2 and 3 — `vs printed naive (+0.066)` and
  `vs the artifact's naive (+0.0729)`: **the reference value is in the header**, so closure is checkable, and all
  **four rows close against both**;
- `2026-09-22-replay-budget-inversion.md`, column 4 — `vs naive`, whose comparator row is written **`— (naive)`**:
  all **five rows close**.

So the check's coverage went **up by thirteen rows** in the same fire that its headline went from a wrong 1 to an
honest 0. **Both directions came from the same act: making the skipped shapes visible and then reading them.**

## 2. The four rules, each forced by the evidence

1. **A correlation header is skipped by its own word** (`Spearman`, `Pearson`, `corr`, `rank`). The existing rule
   caught a correlation only when its *comparator row* held 1.000 by construction, which never fires when the
   second half of the header is a column name — which is exactly the corpus's five.
2. **A header naming two quantities is not a contrast column**, so `absolute pressure sd vs measured sd` is
   skipped with that reason rather than reported as a contrast against a row named `measured sd`.
3. **A *parenthesised* number in the header is the comparator's value** (`vs printed naive (+0.066)`), and every
   other column is then subtracted from it. **A bare number is not**: `contrast vs swap0.5` names a rewiring level,
   and reading its `0.5` as a reference made **four rows of a real table "fail" against an arithmetic nobody had
   written** — the false positive this rule's own narrowing came from, and a warning about how readily a value can
   be found in a name.
4. **A comparator row written with decoration still matches** (`— (naive)`, whole-word, after exact matching
   fails). A wrong match cannot pass silently, because the arithmetic still has to close afterwards.

## 3. And the definition of "failure" narrowed, which is the part that matters

**A failure is now only a row whose printed contrast no pair of its own cells gives.** A contrast column with no
comparator row is **not checkable**, not a failure — because the tool cannot tell a table that forgot its
comparator row from one whose comparator is in another artifact, and those two are the same object to any
arithmetic that reads one table. The previous fire called the first a defect and counted it as a failure; with the
corpus opened, 2 of the 15 columns are that shape and both turned out to be the *second* case (`vs matched
random`, `vs naive (paired)` — the comparators are in other artifacts). **Claiming a defect the tool cannot see is
the same class of error as the false positive it replaced**, and the honest count is the one that says what could
not be checked as well as what failed.

The report now prints, in both modes, three numbers together: **failures**, **rows that close**, and the
**not-checkable columns broken down by reason** — so a change in the mix of reasons is visible, and "0 failures"
is never bare.

## 4. What the two modes now say

| scope | check (a) failures | not checkable | rows that close |
|---|---|---|---|
| paper | **0** | **1** (`delta vs the diagonal`, §4.4) | 4 |
| findings corpus (189 documents) | **0** | **15** columns in 12 documents — 5 delta, 5 correlation, 3 two-column, 2 comparator-not-in-table | 13 more than before, on three columns that now close |

## 5. What this does not settle

- **The loose row match is a judgement**: it can in principle pair a row with a comparator that is not meant,
  and the guard is arithmetic rather than semantics — a wrong pairing produces a failing row, not a silent pass.
- **The kind of a header is read from words.** A correlation written without a correlation word, or a delta
  column written without a delta word, falls back to the conservative branches (two-column comparison, or
  not-checkable), which is the direction that hides nothing and verifies less.
- **And a quoted table is audited too**: one of the five delta columns is inside the previous fire's own finding,
  where §4.4's table is reproduced. That is correct behaviour and worth saying out loud, because it means a
  finding that quotes a defective table inherits the defect's count.
