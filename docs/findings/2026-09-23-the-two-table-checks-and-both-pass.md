# `e105`: the two table checks, and both now pass on the tables this week repaired

**Date:** 2026-09-23
**Script:** `experiments/e105_table_audit.py`; artifact `runs/e105_table_audit.json`; tests
`tests/test_table_audit.py` (12 cases).
**Artifacts:** every artifact under `runs/` is indexed (135 arms, 1350 scalar values); the paper is
`docs/paper/clfly-v1.md`.
**Setup:** a table audit over the paper's 18 markdown tables; the underlying runs are circuit
`mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, λ = 0.003, 4 classes, shared head, chance 0.25.
**Context:** rule 28, and `docs/findings/2026-09-23-the-frozen-body-control-is-in-no-artifact.md`, whose cell
search was done by hand and which named this script as the next infrastructure step.

---

## 1. Two checks, and they are not equally strong

**Check (a) — a contrast column must close against the comparator its header names.** If a column is headed
`vs naive` and the table has a `naive` row, then each other row's cell in that column must equal that row's own
value minus the `naive` row's value. This is arithmetic **inside one table**, so it needs no corpus and admits
almost no false positive, and it is aimed exactly at §4.2, where the column headed "vs naive" subtracted
**+0.0729 for two rows and +0.066 for two others** while the table's own `naive` row printed +0.066.

**Check (b) — a contrast printed inside a measurement cell must equal the difference of two of its row's own
cells.** §4.4 prints `−0.0042 ± 0.0091 (−0.1042, 6.3σ)`: no `vs` column exists, so (a) cannot see the table
that carries the six unbacked cells, and this is the weakest check that does apply.

**Check (c) — does any artifact field contain a printed number?** This *locates* and cannot *convict*: a sigma,
a ratio and a cost in minutes are all derived and belong in a table without being in any artifact. It is
reported as counts and a listing rather than as a verdict, and the honest summary of its noise is in §3.

## 2. Both arithmetic checks now pass, which is the point of building them

| check | coverage | result on the current paper |
|---|---|---|
| (a) contrast columns | 1 table with a `vs` column (§4.2) | **CLOSES** — all four rows |
| (b) inline contrasts | **4** contrasts checked, in §4.4 and §4.2's neighbours | **0 failing** |

**And (a) would have caught §4.2 before it was repaired.** The script was written after the fix and run against
it, so its positive control is the *shape*, not the instance: a test constructs the table as it stood — one row
whose contrast closes against the printed `naive` and one whose contrast came from a baseline in no column of
its own table — and asserts that the second is reported with its `expected` difference (`−0.0056` against a
printed `−0.013`). A check that has never fired on a known case is a check nobody can read, which is why that
test exists rather than a note saying "this would have caught it".

**The denominator is printed for the same reason.** (b)'s first version reported `inline contrasts that fail: 0`
with no count of how many were examined, which is indistinguishable from "the check never fired" — the same
defect the project has already recorded twice (`e97`'s positive control, and the "a flag is not a finding"
paragraph in the corpus audit). It now prints `0 of 4`.

## 3. What (c) shows, and why it is a listing rather than a verdict

Of the paper's 18 tables, **2 have every number located, 6 have none, and 10 are mixed.** The six are fully
derived — costs, partial correlations, ratios — and the ten are mostly so: the highest-located mixed table is
§4.2's own at 75%, where the eight unmatched tokens are its **four σ values and the four contrasts**, which are
exactly the derived quantities a table should contain. So a raw "mixed" verdict carries almost no signal, and
the useful form is the one this script prints: **for each mixed table, which tokens did not resolve.** On the
repaired tables that listing now names only sigmas and contrasts, which is what a correct measurement table
should look like.

**What (c) did locate is the shape of the previous fire's finding, and it separates the two cases.** §4.4's
table is 64% located with its unmatched tokens the σ's — but before the repair its unmatched set included
`+0.010 ± 0.010` and `+0.066 ± 0.019`, whose absence was the finding. The difference between then and now is
not the counts; it is *which* tokens are missing, and that still requires reading.

## 4. What this does not do

- **It does not cover a table with no contrast column and no inline contrast.** §4.4's `naive` and EWC cells are
  audited only by (c), which cannot convict. Filling those cells with measurements (the `e104` runs) is the
  actual repair; the tool's job is to stop the next one from being invisible.
- **It reads the paper, so it audits the paper.** Nothing here checks a *finding* document's tables, and the
  source findings of both repaired tables (`2026-09-22-network-line-settled.md`,
  `2026-09-22-benchmark-measured-its-decoder.md`) still print the old cells. They carry correction banners
  instead, which is the project's convention for a historical record — but it means the corpus's unbacked
  tables are still uncounted, and counting them is a different script.
- **`check_closure` reports one table as having a contrast column naming a comparator it has no row for**
  (lines 719–724, `vs the diagonal`). That is a naming mismatch rather than a bad contrast, and the tool says
  so rather than guessing; the one-line fix is in the paper's header, not in the script.
