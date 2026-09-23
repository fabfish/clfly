# `e126`: the paper said "Five" over four bullets for two days, and the mirror image of it sat fourteen lines away

**Date:** 2026-09-24
**Script:** `experiments/e126_enumeration_audit.py` (new); artifact `runs/e126_enumeration_audit.json`.
**Documents repaired:** `docs/paper/clfly-v1.md` (§7's trap list, and §4.3's superseded σ column).
**Tests:** `tests/test_e126_enumeration_audit.py`, 9 cases, both directions — the positive control and the four
near-misses three earlier designs of the checker fired on.
**Context:** `docs/research_plan.md` rule 28 ("a table is a claim") and rule 32. This fire started as an
audit of the *counts* a document states about itself, which none of this project's audits read.

---

## 1. Two defects, one of them a self-contradiction inside a single subsection

**The trap list.** §7 of the paper carried

> **Five measurement traps, every one of which the project fell into before finding it.**
> - four bullets

and `git log -S` dates the off-by-one precisely: commit `1743573` (2026-09-22) rewrote **"Two measurement
traps"** to **"Five"** while adding two bullets to the two that were there — so it said five and listed four
from the day it was written. **That commit's own message is about stale aggregate statements.** The defect it
was fixing was committed in the fix, and it survived two days and several audits because every audit here reads
numbers and none reads counts. Repaired to **six**, because this fire produced exactly the kind of trap the list
exists for — see §3.

**The mirror image, and it is worse because it is a contradiction rather than a stale number.** §4.3 said, at
line 666:

> All eight ladder rungs now have a measured draw sd of their own (`e74` supplied the last three …), so the
> comparison is a measurement on both sides.

and fourteen lines later, at line 681:

> …on measured draw sds and paired sems the same column reads 2.6–13.7σ, **and it is a floor, since three of its
> eight rungs have no measurement of their own.**

Both are about the same fact — how many of the ladder's eight rungs have their own measured control-draw sd —
and they are opposite. The artifact decides it, and decides it in one field:
`runs/e73_ladder_named_head_to_head.json` contains `"n_ladder_measured": 8, "n_ladder": 8`, and every one of its
eight ladder rows carries `"draw_sd_measured": true`. **So the abstract and line 666 are right and line 681 was
stale**, and its provenance is a fix that missed one place: the clause entered with `632e54a` when five of the
eight were measured, `d683a86b` corrected the sibling paragraph at 665–667 and did not touch 681, and `c897113`
corrected the same clause in the Abstract and also did not touch 681. It even quoted the *post-`e74`* range
(2.6–13.7σ) while calling itself a floor for the *pre-`e74`* reason — internally inconsistent, and that is the
tell that would have caught it by eye had anyone compared the two sentences.

Repaired to name the evidence and the artifact field. `e90`'s contribution is now stated too: `pool32` and
`pool64` are the same partition at d = 1307 and had been *borrowing* a draw sd, so "all eight" is true only
after `e90` as well as `e74` — a detail the abstract's "all eight" also glosses.

**And a third, smaller one found on the way.** §4.3's σ table (line 497) prints `pool4` at **42.2σ** and the
sentence under it calls the ladder "an order of magnitude more decisive than the five-rung ladder's best". The
abstract already warns that "the single-draw figure of 42.2σ overstates it several-fold" — but the table itself
carried no marker, so a reader arriving at §4.3 takes 42.2σ for the result. It now says, in place: the column is
against zero with a seed-only sem and an *assumed* 1.0e-3 draw sd, on measured per-rung draw sds and paired sems
the same eight deltas give **2.6–13.7σ**, that is a **3.1×** overstatement at the best rung, and the head-to-head
with the named rungs moves from an order of magnitude to a factor of **1.9**. §9's own rule — *"naming the
command behind a superseded number is worse than naming none"* — is about exactly this.

## 2. What was checked and found correct, which is most of it

- **The abstract's "Thirteen" retractions.** The list has **12** top-level semicolon-separated entries plus one
  nested inside a parenthesis (the C1 refutation's own refutation), which is 13 — and the sentence's own claim
  that *"the thirteenth is the only one on this list whose number survived the check"* matches the last entry.
  Correct, and it required the nested item to be counted, which is worth knowing before anyone "fixes" it to 12.
- **§4.2.1's "four attempts, none of which survived"** — the section lists exactly four bullets (as a law, as a
  predictor, as a sign rule, as a testable mechanism). Correct, and so is the abstract's matching "four
  independent levels".
- **§4.2.1's "we spent six further experiments"** cites **nine** ids (`e36–e40, e49, e51, e53, e56`) and closes
  with "four experiments of increasing precision". **Checked and left alone**: all nine ids appear in findings
  elsewhere in the corpus, so they are real, and the three counts can be reconciled (six runs, four levels as
  bullets, four that narrowed the claim) — but the record does not let me *verify* which reading is intended, and
  rewriting a count I cannot source would be a worse act than leaving a loose one. It is reported here so that
  the next reader does not have to rediscover that it is loose.

## 3. The audit, and the three designs of it that failed first

**A count is a claim about the document itself, and nothing in this project was reading it.** `e97` checks that
a cited artifact exists, `e105` checks that a table's arithmetic closes, `e103` checks that an arm executes
twice. All three read the numbers. `e126` reads the document's own enumerations against its own contents.

Each failed design is the next one's specification, and they are worth recording because **a checker that
reports everything is worse than no checker: it looks like coverage**:

1. *Any `<number> <plural noun>` adjacent to a list.* Fires on "17 cores", "34 tests", "75 minutes", "12 seeds"
   — counts of something other than the list's length. About **forty mismatches, not one real**. Repair: a
   curated lexicon of nouns that *name list items*; quantity nouns are excluded on purpose, which costs
   coverage and is printed rather than hidden.
2. *Count a numbered list like a bulleted one.* Read the abstract's four numbered findings as **three**, because
   two blank lines separate its items and a double blank line ended the block — **the mismatch was manufactured
   by the checker**, the one error this script cannot afford. Repair: for `1. 2. 3.` the numbering *is* the
   document's own length claim, and a numbered block that does not start at 1 is a **mid-list fragment**, whose
   length says nothing about the whole list, so it is skipped rather than reported.
3. *Widen the lookback to reach a heading.* Then a **later** line inside the window wins: §7's own correction
   note says *"adding two bullets"*, so the nearest match claimed **2 over a six-item list** — the checker
   poisoned by the very note explaining the defect it had just fixed. Repair, and it is the pattern that
   actually describes the defect: a count is read only when it **opens a line or opens a bold run**.
4. *The residual two false alarms* (`"Two things worth noting…"`, `"Two things do change."`) came from the
   lookback **crossing a section heading** into the next section's bullets. Repair: stop at `#`.
5. *And one more, found only by the test suite*: `CLAIM_RE` had been tightened until it could no longer match
   **"Five *measurement* traps"**, so the positive control failed — the checker had stopped catching the very
   defect it was written for while still reporting a clean corpus. **That is the failure a corpus test cannot
   see** and the reason the test file is a positive control first and a silence test second.

Two further real bugs the tests caught: the ratio counter lacked `IGNORECASE` and so missed "Seven of the eight"
(0 of 205), and Markdown's **lazy-continuation** rule was missing, so the paper's item 3 — whose wrapped tail
lost the three-space indent items 1 and 2 have — read as three items. In Markdown that text *is* item 3, so the
parser was wrong and the "defect" was invented.

**The result on the corpus: 166 documents, 9 count claims found next to a list, 9 matched, 0 mismatches, 0
numbering holes, 205 ratio phrases reported as not-checked.** The denominator is asserted in the test suite
(`found >= 5`), because a checker that finds nothing passes every silence test.

## 4. What this cannot settle

- **It reads one pattern.** A count that opens a line or a bold run and is followed within six lines by a list,
  stopping at a heading. A stale count buried mid-sentence — `e125`'s cited experiment list, `e97`'s own
  denominators, §4.2.1's "six further experiments" — is **invisible to it**, and that is most counts in this
  corpus. The lexicon is 17 nouns; "the four grounds" and "the two axes" are not in it.
- **The `LIST_NOUNS` choice is a judgement, not a measurement.** Every word in it is there because a real
  enumeration in this corpus uses it, but nothing establishes that the set is complete, and a defect whose
  count noun is missing from the list will be missed silently rather than reported as unchecked.
- **It cannot see intent.** "Two things worth noting in the completed numbers" over four bullets is not an
  error; "Five measurement traps" over four is. Both are the same shape, which is why the checker needs the
  heading rule and the opening rule, and why it will still be wrong somewhere.
- **And it says nothing about whether a corrected count is the *right* number** — only that a document agrees
  with itself. The two defects here were found by a human comparing a count to a list; the script reproduces
  that comparison, not the judgement of which count is true.
