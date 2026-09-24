# The corrections index: 45 self-corrections in 39 findings, and only six of them say where they land

**Date:** 2026-09-24
**Script:** `experiments/e158_correction_index.py` — **an index, no runs**. Artifact:
`runs/e158_corrections_index.json`.
**Why it exists:** this project corrects in place and says so, which means the record's *true* state is spread
between the paper, the plan and the findings. The audits that exist cover tables (`e105`), enumerations (`e126`),
derivations (`e132`) and the programme table (`e127`) — **none of them covers corrections**, so a reader arriving
fresh cannot tell from the paper alone which of its sentences has since been qualified.

---

## 1. What it counts

| | |
|---|---|
| correction sentences carrying an explicit marker | **45**, in **39** findings |
| of those, sentences that name a **paper or plan section** | **6** |
| of those, sentences that name **no destination** | **39** |
| in-place correction markers **inside the paper itself**, under the same conventions | **8** |

**Two of those numbers moved while this finding was being written, and both moves are instructive.** The first
scan reported *24 paper markers* because its count matched the words anywhere — and 14 of the 24 were prose like
*"has been corrected"*; counted with the same nine conventions the paper uses, the number is **8**, which is the
comparable one and is what the script now prints beside the loose figure. The second scan reported *43 sentences*
where the first said 43 and this finding's own text says `CORRECTED`, `corrected in place` and `was wrong` — **the
index counts itself**, because it scans a live corpus, so every number here is "as of 2026-09-24" and will be
stale by construction.

The marker list is explicit in the script (nine conventions: `CORRECTED`, `corrected in place`, `must be
corrected`, `is withdrawn`, `was wrong`, `is REFUTED`, `was REFUTED`, `this sentence used to say`, `read here until
2026-`) — so a new convention is a visible edit rather than a silent miss. And a `§N` inside a finding is only
attributed to the paper **when the sentence says "paper"**, because most `§N` in the corpus mean *the finding's
own* section N; without that rule the index attributed nine corrections to the paper and six of them were the
findings talking to themselves.

## 2. What it says, and it is not a defect

**The 39 unnamed corrections and the paper's 8 markers are the two halves of one practice.** A finding that
corrects its own claim in place *has* named its destination — the sentence above it — and the paper records the
corrections that land on it in the same convention, in place, with the date. So the index's real content is
**where to look**: 45 sentences in the findings corpus, 8 markers in the paper, and **exactly six sentences
that point from one to the other**.

**And it makes the case for the two artifacts that carry the current state**: the plan's `C2b` status block and
its rules 1–42. Those exist *because* the corrections are distributed: a reader who has them does not have to
reconstruct the state from 39 findings, and this index is what says how many there are to reconstruct from.

**The one correction from today that named a paper location was checked by hand and is applied**: the `e140`
two-draw finding says *"the paper's §4.7 sentence that this session wrote must be corrected in place"*, and §4.7
now carries the three-draw reading (**1.33σ**, falsifier fired) in place of the single-draw 2.08σ, with the date.
That hand check is the whole of this fire's verification, and the index is what made it a two-minute job rather
than a re-read.

## 3. What this cannot settle, and why it prints no verdict

**It deliberately prints no "applied / not applied" verdict.** Deciding whether a correction has landed needs a
judgement about whether two sentences say the same thing, and **a scanner that guesses wrong is worse than no
scanner** (rule 22) — the same reason `e105` reports *counts and locations* rather than convicting cells. What it
does exactly is find the sentences and count the unnamed ones, and both of those are string operations.

- The marker list is a **hand-chosen list of nine conventions**, so a correction written in a tenth way is
  invisible to it — and the count above is a count of *marked* corrections, not of all corrections.
- **The 43 are not independent**: one finding can carry several, several describe one correction, and the corpus
  is written by one process in one week, so the count is not a rate.
- And the sentence split is naive: a correction whose marker sits in the *next* sentence from the claim it
  corrects is indexed under the marker's sentence, which is why the JSON holds the full sentence rather than a
  verdict about it.
