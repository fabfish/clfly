# The status word is a header nobody re-derives

**Date:** 2026-09-23
**Method:** a mechanical re-derivation of the programme table's status column from disk — the check rule 22
prescribes, run over all 59 rows of the section.
**Context:** `docs/findings/2026-09-23-the-programme-table-had-drifted.md` (`e85`), which found eight drifted
rows and named four ways the audit misses things. This is a fifth.

---

## 1. What the mechanical check found, and what it missed

The scan looked for rows whose status column could be falsified from disk: an artifact named but absent, an
artifact present but the status still *in flight* or *launched*, or no status word at all.

- **Rows naming an artifact that does not exist: zero.** Every `runs/*.json` and every
  `docs/findings/*.md` cited by a programme row is on disk.
- **Rows with no status word: eight**, and all eight are *false positives* — the status cell opens with a
  bolded phrase rather than one of the four status words (`**artefact restored, headline reproduces**`,
  `**four rungs and stopped**`, `**C3 deprioritised**`, …). A word-based check cannot see those, which is
  the same class of blind spot `e85` recorded for variant spellings.
- **One flag that was wrong in both directions at once**: a row whose cell mentions "launched" in later prose
  and cites an artifact that exists. My own check reported it as both missing and stale. **A scanner that
  reports a file as missing when it is present is worse than no scanner**, because its output looks like
  evidence.

So the mechanical pass found **no** drift. What it did surface, by printing the *opening* of each cell next
to the *end* of each cell, is a shape no word-based check can find.

## 2. The shape: the status word is a header nobody re-derives

Three rows opened with **`**launched, prediction before the run.**`** — and reading each cell to its end:

| row | opening word | what the rest of the cell reports | artifacts |
|---|---|---|---|
| `e84` (other two settings) | `launched` | the finished result, including that replay's own forgetting "does sit below zero … What reproduces is *driven to zero*" | both `e84_*_5reps.json` present |
| `e86` (9 partitions × cs = {300, 1500}) | `launched` | **the completed verdict** — the clause passes at two of three sizes, written into this same cell | all 18 `e86_drawsd_*` present |
| `e92` (20 cells × cs = {300, 800, 1500}) | `launched` | 32 of 60 cells and the whole d = 952 result | genuinely in flight — this one is **correct** |

**Two of the three were stale, and both had been updated.** The `e86` row is the clearest: this week's
completion was written *into the cell*, reporting that the clause passes at two of three sizes, while the
cell's opening word still said the run had just been launched — thirty lines above its own contradiction.

The mechanism is that **an update gets appended to the body while the header stays**, so the status word
records the state at the moment the row was created rather than the state now. That is a *different* failure
from `e85`'s eight, which were rows where nobody had gone back at all: here someone went back, and the edit
landed in the wrong half of the cell.

**And it drifts in the same direction as every other instance this project has recorded**: *toward more
open*. A row that says "launched" reads as work in progress even when its body reports the answer, so the
project looks less settled than it is — the fourth consecutive audit where the drift ran that way, and the
first where the drift was in the *formatting* rather than in the content.

## 3. The check that catches it, and why it is cheap

**Print the opening of each status cell next to the end of it, and ask whether they agree.** That is one
line of code and it needs no artifacts, no numbers and no domain knowledge — it asks only whether a cell
contradicts itself. It found two rows that a word-based scan passed and that a full re-derivation of the
*numbers* would also have passed, because the numbers in those cells are correct.

So rule 22 gains a fifth blind spot, of a kind its four existing ones are not: the previous four were all
ways a *search* can miss something, and this one is a way a *cell* can miss itself. The guard belongs to the
same family as the paragraph-level check this project added for the C2b section, which carried both
"`side` has never been run" and its own Update paragraph reporting the run — there the contradiction was
between two paragraphs, here it is between a header and its body, and both are found by reading a claim next
to the claim it is supposed to be about.

## 4. Corrections applied

- The `e84` and `e86` rows: the opening word is now `done`, and each carries the old wording in a visible
  parenthetical naming why it was stale, so the drift is on the record rather than silently repaired.
- The `e92` row: its cell counts are refreshed to **48 of 60**, and its body gains the paired cross-size
  result from this week (`-0.301, [-0.638, -0.006]` for the absolute form against `[-0.779, +0.044]` for the
  relative one) with the two complete sizes stated, since a row that reports a grid's progress should name
  which parts of it are whole.
- `docs/research_plan.md`'s rule 22 gains this as its fifth blind spot.
