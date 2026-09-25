# The check the table promised and never ran — four rows were still telling the reader to wait after the artifacts had been read

**Date:** 2026-09-25
**Read of:** `docs/research_plan.md` — its programme table (140 rows) against the artifacts in `runs/`, and the four
findings that had already read the runs those rows were still calling unfinished.
**Instrument:** `experiments/e127_programme_table_audit.py`, whose **check C is implemented here for the first
time** (tests in `tests/test_e127_programme_table_audit.py`).

---

## 1. The defect in the checker, before the defect in the table

`e127`'s docstring lists four checks and the code implements four checks, and **until this fire they were not the
same four.** The docstring's C is *"a row says the work was never run while naming an artifact that exists — the
`e694` shape"*. The code's C, in the printed report, was *"duplicate first cell"* — the docstring's D. And the
code's D, *"a table row with a raw `|` in a cell"*, appears nowhere in the docstring.

So two things were wrong at once: the labels had drifted, and **the check the docstring called C had no
implementation at all**. The second is the one that matters, because rule 22 records that this table has drifted
**four times in the same direction — toward *more open*** — and the missing check is precisely the one that reads
the *other* direction: a row that under-claims what is on disk. A checker that only asks "does the row announce
itself as open after reporting an answer?" cannot see a row that announces itself as open and never updates, which
is the same error with the answer written somewhere else. The labels are now A–E in both the docstring and the
report, and C is implemented.

## 2. What implementing it found: four rows, each already read somewhere else

`uv run python -m experiments.e127_programme_table_audit` now reports **C: 4** — against a denominator of 111 rows
that name an experiment of their own that has artifacts in `runs/`:

| line | the row's claim | its own id | what is on disk | the finding that had already read it |
|---|---|---|---|---|
| 1024 | *"launched, prediction before the run"* | `e92` | **61 artifacts**, including `runs/e92_grid_report.json` | `2026-09-23-the-grid-at-one-size-is-whole.md`, `2026-09-23-the-grid-is-complete-and-the-decline-was-the-subset-talking.md` |
| 1093 | *"the `3e-3` arm is running"* | `e147` | `runs/e147_r32_frozenbias_ewc_lam3e-3.json` | `2026-09-24-under-the-freeze-lambda-does-not-matter-for-forgetting.md` |
| 1095 | *"the top of the sweep is running"* | `e141` | `runs/e141_r32_ewc_lam3e-1.json`, `…lam3e-2.json` | `2026-09-24-the-lambda-sweeps-floor-is-where-the-effect-is.md` §2b |
| 1110 | *"relaunched after a caught failure"* | `e6` | `runs/e64_predictor_6_perseed.json`, `runs/e64_predictor_per_seed_analysis.json` | `2026-09-23-the-predictors-record-per-seed.md` |

Two of the four were **registrations whose verdicts were already decided and never written back**, which matters
more than bookkeeping: L1093's registration had three named outcomes (P1, a falsifier, and "both arms land at
`e125`'s +0.0227"), and the second arm decided the middle one — **the falsifier fires**, since the λ step under the
freeze is −0.0047 ± 0.0032 = **1.46σ**, below its 2σ bar. The row's own text could not say so, because it was
written before the arm landed. A reader who trusted the table would have concluded that the λ question under the
freeze was still open.

## 3. The check's three forms, and the two false-positive classes that shaped them

Two shapes had to be told apart, because the corpus has one live instance of each and neither rule catches the
other:

1. **an arm is described as running** (`the 3e-3 arm is running`) and an artifact of the row's OWN id carries that
   arm's value in its name — `e147` … `lam3e-3.json`. The state word is read, not guessed: *"the `3e-4` arm is
   **in**"* means landed, and counting `in` as a running state flagged `e141`'s floor arm, which the very same cell
   reports.
2. **the cell registers a braced set of arm values** (`--lam {3e-4, 3e-2, 3e-1}`), still says something is running,
   and **every** registered value has an artifact on disk. This is the form that catches `e141`, because its running
   clause names no value at all: *"the top of the sweep is running"*.
3. **the cell says launched / no artifact / never run** — the docstring's original wording — with no finished word
   in the status cell's opening.

Forms 1 and 2 are deliberately **not** gated by the finished-word test, because a cell that reports one arm while
another is still described as running is exactly the shape being sought: `e141`'s row opens `done for the floor arm`
and its own first cell says the top of the sweep is running, and both top arms are on disk.

Form 3 needs that gate, and the gate is where the false positives were. The vocabulary of "this cell is reporting
the answer" had to be widened **twice**, and each time a false positive did the widening:

- the first version knew only `done`, and flagged rows whose cell opens **`READ —`** (4 rows in this table);
- the second added `read`/`landed`, and still flagged L1092, whose cell opens **`P1 HOLDS AND IS LARGER THAN THE
  BASE FAMILY'S`** and mentions "launched" three sentences later, about the queue it waited in;
- with `holds`/`fails`/`fires` in the list, the surviving flags are the four above.

The existing `why` column is deliberately excluded from the search: it is the *registration*, and it is allowed to
say "launched" forever, because that is what the row's state was when the prediction was written down. Searching it
would have flagged `e150`'s row, whose registration reads *"LAUNCHED when a slot freed"* and whose status correctly
reports the landed arm — a false positive of the shape rule 22 already records as costing more than the check saves.

## 4. The one flag whose evidence is weaker, said out loud

L1110's conviction rests on the human step, not on the machine's: the check fired on `runs/e6_predictor.json` and
`runs/e6_predictor_6.json`, which are the **pre-relaunch** artifacts, and the row is stale because of
`runs/e64_predictor_6_perseed.json` — a different id, named in the row's own status as the thing the relaunch exists
to carry. The check's rule ("the row's own runner id has artifacts") is what the corpus supports; the decisive
evidence is one step beyond it. A scanner is not a finding, and this flag is the instance that shows why the
distinction is kept rather than smoothed over.

## 5. What the four rows now say

Each was rewritten to report the read it had lost, citing the finding and the numbers, with the stale claim kept as
history rather than deleted: L1024 now carries the grid's seven clause verdicts (P1 **PASS** at +0.919 / +0.618 /
+0.872 on 20 of 20 cells at all three sizes, P2 **FAIL**, P6 **FAILED and its falsifier fired** at +0.923, P7
**PASS**, F2 **fires**); L1093 carries the fired falsifier and the 1.46σ λ step; L1095 carries the five-point sweep
and the bracketed optimum (3e-4 best of five, λ = 3e-1 dominated at 8.86σ of accuracy); L1110 carries 24 of 24
resolvable pairs called correctly on the paired seed sem and 20 of 21 with the measured draw sd folded in, against a
published denominator of 13. `e127` now reports **C: 0 of 111**, and the four rows' `what` cells no longer describe
an arm as running.

## 6. The mechanism, which is worth more than the four instances

This is not carelessness — it is a structural property of the loop, and rule 22's "drift toward more open" now has a
named cause. A row's status cell is written **when the run is launched**; the read is written by the fire that reads
the artifact, and when a run outlives the fire that launched it, the read lands in `docs/findings/` and the row keeps
its launch state. Four rows in two days, and every one of them has its own finding — the information was never lost,
only uncoupled from the index that a reader actually uses. The coupling is now checked on every run of `e127`.

**Falsifiers.** C's claim ("no row under-claims the disk") dies if any row's claim of an unfinished state is true
while the artifacts exist — the check prints the phrase, the id and the artifact names so the claim is falsifiable
by reading. The *completeness* claim is weaker and is stated as such: the check only sees rows that name their own
experiment in the two ways it recognises (a runner file name, or a parenthesised `eNNN` label) — **29 of the 140
rows name no own experiment that has artifacts at all**, and a row that under-claims via a third convention would
be invisible to it. That is the same limit `e182` measured on the prose side, from the other end.

## Reproduce

```
uv run python -m experiments.e127_programme_table_audit              # A 0, B 0, C 0 of 111 rows, D 0, E 0
uv run python -m experiments.e127_programme_table_audit --json-out ONE_PATH.json
uv run pytest tests/test_e127_programme_table_audit.py -q
```
