# `e127`: rule 22's one-line check was never code — and the first automated pass found a broken row in its own table

**Date:** 2026-09-24
**Script:** `experiments/e127_programme_table_audit.py` (new); artifact `runs/e127_programme_table_audit.json`.
**Tests:** `tests/test_e127_programme_table_audit.py`, 7 cases across both directions.
**Repaired:** `docs/research_plan.md`'s `e124` programme row, which rendered as **two** table rows.
**Context:** `docs/research_plan.md` rule 22, which records that this table has drifted **four times in the same
direction** — toward *more open* — and that the check that catches it *"is one line and needs no artifacts: print
the opening of each status cell beside the end of it and ask whether they agree."*

---

## 1. The rule existed; the check did not

`e85` ran that check **by hand** over 59 rows and found eight stale ones. A later pass found three more that
contradict themselves — `**launched, prediction before the run.**` in a cell whose own body reports the finished
answer, because an update got appended to the body and the header stayed. **Both passes were manual, and the rule
was never made into code**, so the check happens only when somebody remembers — which is the condition that
produced four drifts in one direction.

`e127` is that check as a script, with one routine per documented failure mode, and it runs in a second:

| check | what it asks | result on the live plan |
|---|---|---|
| **A** | does every `runs/*.json` the row names exist? | **0** flags |
| **B** | does the status cell contradict itself (an open word **before** a done marker)? | **0** flags |
| **C** | two rows with the same first cell? | **0** flags |
| **D** | a table row with a raw `\|` in a cell, which Markdown splits in two? | **0** flags, after §2 |

**86 rows parsed, 78 carrying a status indicator** — printed because a zero with no denominator is not a check.

## 2. It found one real defect, and it was mine, in the table it audits

Check **D** fired once, on the `e124` row added to the programme table **earlier in this same session**. The row
contained `` `|Δforgetting|` `` — **unescaped pipes inside a code span**. In a GFM table a literal `|` separates
cells *unless escaped as `\|`, and that holds even inside backticks*, so the row rendered as two rows with the
table broken between them for every reader. Repaired by removing the pipes rather than escaping them, since
escaped pipes inside code spans render inconsistently across renderers.

**Two things about this are worth more than the fix.** The first is that **none of this project's audits could
have caught it**: `e97` reads artifact existence, `e105` reads a table's arithmetic, and `e126` reads counts —
all three read the numbers, and the numbers were all correct. A broken row is a claim about the *table* rather
than about the values in it. The second is that the defect was **introduced by the same session that then
audited it**, which is the ordinary case rather than a coincidence: the table is edited by whoever is working,
and nobody re-reads a rendered version to check that a row is still one row.

## 3. Three false-positive classes, each of which would have made the checker worse than nothing

Rule 22's own last paragraph is the specification: *"a scanner that reports a file as missing when it is present
is worse than no scanner, because its output looks like evidence."* This script produced three such classes on
its first passes, and all three are now in the tests as cases that must stay silent.

1. **It split rows on every `|`.** The plan contains a correctly-written `largest \|Δ\| = 0.58`, and the check
   reported a well-formed row as malformed — one false alarm and no catch, on its first run. The split now
   respects `\|`, the reported context is centred on the first pipe **beyond** the row's five structural borders
   (centring on the fifth showed the row's own trailing border and nothing else), and an offending offset is
   printed so that the output is an edit rather than a diagnosis.
2. **It flagged "an open word after a done marker" as a contradiction — 9 of 9 false positives.** Every one was a
   status cell reading `done — …` with the word "launched" or "PENDING" in later **prose about a different
   experiment**: *"`e48` launched to close it"*, *"a pair whose measurement was absent was counted PENDING"* —
   and one of them was the row whose own correction note quotes the phrase it was being flagged for. This is the
   failure rule 22 already had on record from the manual passes, reproduced exactly by the automated one. The
   check is now **counted and printed as a denominator and never as a finding**.
3. **Artifacts named in the `why` column were never checked.** The search covered the `what` and `status` cells
   only, and the `why` cell is where a row says what closed a gap. A test caught it. Had a row cited its closed
   gap's artifact there — which is the natural place to write it — check A would have reported zero while
   skipping it, **which is the failure mode where a checker's silence looks like coverage**.

**Two more were caught by the tests rather than by the corpus**: the column header and the `|---|---|` separator
were both being counted as data rows (the separator's cells contain `|`, so the `set(body) <= set("-: ")` skip
never fired), and a test that hard-coded a line number failed because it had assumed the wrong table offset.

## 4. What this establishes, and what it does not

**Established:** the programme table, as it stands today, passes all four of rule 22's mechanical checks — every
named artifact exists, no status cell announces itself as open and then reports an answer, no two rows share a
first cell, and no row is broken. The check that found the last four drifts now runs in a second instead of when
somebody thinks of it, and it carries its denominator.

**Not established, and this is most of rule 22:**

- **Check B is a word test, and the defect it is built for is not always a word.** Rule 22's fourth failure was
  *four rows marked done while summarising a number the project had since overturned* — the status word is
  correct and the **number** is stale. Nothing here catches that; it needs the result re-derived from an artifact,
  which is what `e97` and `e105` do for findings and tables and what no script does for this table's prose.
- **The self-contradiction rule has a false-negative side.** *"Print the opening of each status cell beside the
  end of it and ask whether they agree"* is a **reading** instruction, and a machine can only compare keywords.
  A cell that opens `done —` and closes with a retraction of its own opening would pass.
- **C is a text match on the first cell.** Two rows describing the same work in different words are not caught,
  and `e85`'s duplicate was found by reading rather than by matching.
- **The four checks are the four documented modes.** Rule 22 lists five, the fifth being the self-contradicting
  row — covered by B. Nothing here is a claim that the table is *right*, only that it is *self-consistent* in
  four mechanical respects.
