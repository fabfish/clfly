# `e132`: rule 34 is now a check — its yield was 2 defects in 3 hand-checks, and the corpus's one live derivation passes

**Date:** 2026-09-24
**Script:** `experiments/e132_derivation_audit.py` (new); artifact `runs/e132_derivation_audit.json`.
**Tests:** `tests/test_e132_derivation_audit.py`, 9 cases, **synthetic in both directions** because the corpus
yields one live derivation and it is correct.
**Context:** `docs/research_plan.md` rule 34, written one fire earlier from `e128`: *"A sentence can stitch two
runs as easily as a table can, and the tell is arithmetic. … recompute the stated prediction from the stated
input."* And rule 22's line, which this fire applies to rule 34 itself: *"the check is one line and needs no
artifacts"* — performed by hand for two days until it was made mechanical.

---

## 1. What the rule has actually found, now that its three instances are known

| instance | claimed | the formula gives | verdict |
|---|---|---|---|
| §4.2's `85% predicted a 2.6× fall` | 2.6 | **2.07** *(and 2.6 needs 94.7%)* | **wrong** — `e128` |
| `e120`'s `ρ ≈ 0.14` | 0.14 | **0.364** *(0.246 on its own rounded input)* | **wrong** — `e129` |
| `side`'s implied draw sd | 1.028e-3 | **1.031e-3** | **correct to 0.3%** |

**Two defects in three hand-checks**, on numbers the paper cites. That is the case for making it code, and this
fire does. The two families are the ones the corpus actually uses:

1. **A removable share implies an sd fall**: `<f>% predicted a <Y>× fall` must satisfy
   `Y = 1/sqrt(0.1f + 1 − f)`.
2. **A σ reduction at a stated sem implies a draw sd**: `d = s·sqrt((A/B)² − 1)`.

## 2. The corpus is clean, and the checker has exactly one subject

**One live derivation found, and it agrees** — `e129`'s hand-check of the `side` draw sd, now mechanical. **9
paragraphs are enumerated but not checked**, because their formula is not named in the sentence; **4 candidate
paragraphs are skipped as already-corrected**, which is the four quotations of the two defects above, each sitting
beside its dated correction. Both denominators are printed, because **a zero with no denominator is not a check**
— and here 0 failures out of 1 is a much weaker statement than it looks, which is why §3 exists.

## 3. Three ways prose defeated the checker, and one way it defeated the test

Each is a way a checker becomes worse than nothing, and each was found by **reading its own output** rather than
by the corpus:

- **It read lines, not sentences.** The derivation it exists to check *wraps across two lines*, so the first
  version **found nothing to check while the corpus held a derivation it could evaluate**. Silence and having no
  subject are indistinguishable from the outside, which is the failure mode this whole session keeps meeting. It
  now joins each paragraph.
- **It reported three already-corrected quotations as defects.** The convention is to leave a wrong sentence
  standing and correct it in a `>` blockquote after, so a same-line test is not enough.
- **Then the exclusion was too wide**, and that is the more instructive failure: a marker **five paragraphs
  later**, about a *different* figure in the same section, silently skipped a **correct** derivation. The
  exclusion is now the paragraph itself or the **immediately-following blockquote** — which is the convention's
  actual form — and that is the version that finds its subject.
- **And the test caught the same class of error in itself**: it asserted `share_sd_fall(0.85) = 2.074` and the
  formula gives **2.063**. 2.074 is what the *measured* share **0.8528** gives; the round number in the prose and
  the value in the artifact differ in the second decimal, and the formula uses one of them. The test now pins
  both, which is the arithmetic version of this project's rule that a quoted figure needs its source beside it.
- **And a fourth class appeared only once this finding existed**: the table in §1 quotes the claim, prints the
  correct value and says **wrong** — with no dated marker anywhere — so the checker flagged **its own summary**.
  A checker's exclusion set is therefore **empirical and grows with the corpus it audits**, and every addition to
  it is a wider evasion route. That is the honest form of "the corpus is clean": it is clean **for a marker list
  that was assembled by watching it fail**, and the skip count is printed for exactly that reason.

## 4. What it cannot do

- **It checks a derivation only when the sentence names its own formula.** `e128`'s `2.6×` named none — the input
  was in the clause before it — and was caught by recomputing by hand. **Two families out of however many the
  corpus uses is the honest scope**, and the 9 enumerated-but-unchecked paragraphs are the size of the gap.
- **The correction exclusion is also an evasion route**: a document could hide a live defect by writing a marker
  within one paragraph of it. The count of skips is printed so the exclusion is visible, and the hole is closed
  by reading rather than by the script.
- **It cannot tell a round number from a measured one**, which is the reason the false negative in §3 existed and
  the reason the test above had to pin both values: the formula is applied to whatever figure the sentence
  prints, and a sentence may reasonably print a rounded one. **So a disagreement within a few percent deserves a
  look rather than a verdict**, and the script's 1% tolerance is a choice made here, not a fact.
- **And it says nothing about whether a *correct* derivation is about the right quantities** — the `side` case
  passes arithmetic and says nothing about whether the interpolation it reproduces was a good idea.
