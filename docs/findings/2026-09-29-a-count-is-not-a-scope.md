# A count is not a scope: the paper's denominators have grown 2.45× and 6.44×, and a universal now covers 16%

*2026-09-29 00:35. Runs: **none new** — `experiments/e277_a_count_is_not_a_scope.py` extracts the counts the paper
states about the corpus by pattern, maps each to what its noun covers on disk, and checks the universal built on one of
them, writing `runs/e277_a_count_is_not_a_scope.json`. Seconds.*

## 1. The item: `e270`'s premise one step down

`e270` checked one **existence premise** of the paper against the corpus and found it false. A **count** is the same
kind of claim one step down, and it fails in the same direction for the same reason: the corpus grows, so a number that
was the whole record becomes a share of it — and every **universal** quantified over that number narrows with it while
the sentence still reads as a statement about all of it.

    "every one of the 25 rate-network runs used 8 or 32"

The counts are extracted **by pattern** rather than from a hand-made registry — unlike `e268`'s quoted figures, a count
about the corpus has a shape a regex can name — so this audit is exhaustive over the forms it lists and prints how many
counts it found.

## 2. What the patterns find

| form | the paper says | what the noun covers now | ratio |
|---|---|---|---|
| `13 of 216 artifacts` | 216 | **529** | **2.45×** |
| `the 25 rate-network runs` | 25 | **161** | **6.44×** |
| `every one of the 25` (same sentence, its universal form) | 25 | **161** | **6.44×** |

Seven counts are extracted and three map to a corpus noun; the rest name things this module has no predicate for
(`the 27 arms`, `every one of the 132`, `the 77`, `the 17`), which the report prints rather than drops.

**W1 MET — every stated count is below today's corpus, in the only direction a growing record can produce.**
**W2 MET — and the universal is quantified over such a count**: `every one of the 25 rate-network runs` names **25 of
161**, i.e. **16%** of what that noun now covers. The sentence reads as a statement about the line; it is a statement
about a sixth of it, and the number is the only thing in it that says so.

**W3 MET — and its clause is false as written, independently of the count.** `8 or 32` is contradicted by **three**
rate-network artifacts carrying `fisher_batches` 128 — the same three `e270` found — and **two** early ones
(`e8_basis`, `e8_rate`) that leave the field unrecorded. So the sentence is wrong twice over: about which runs it
covers and about what those runs used.

## 3. What it means

**A count is not a scope, and the paper's counts are its scopes in disguise.** "Every one of the 25 rate-network runs"
was, when written, a statement about the line; a reader today cannot tell whether the twenty-five were chosen or
whether they were all there was. The correction is not a bigger number — it is a **scope**: which runs, from which
corpus, at which date. That is the same lesson `e268` and `e270` each produced from a different sentence, and this
audit is the one that generalises them, because a count is the form in which a stale claim keeps its syntax while
losing its meaning.

**And the direction is the one that flatters the paper.** Every count that maps is *smaller* than the corpus, so the
claims it quantifies over are narrower than they read; a reader who re-checks finds the paper understating its own
evidence and overstating its scope in the same sentence.

## 4. What it cannot do

**The patterns are the module's**, so a count written another way is invisible, and the report prints the count it
extracted beside the forms it looked for rather than claiming completeness. **`rate-network` is a configuration
signature** — a `methods` list with `iters` and `circuit_size` — so an artifact of that line recorded without those
keys counts as something else. **The corpus on disk is the whole input**, so a count the paper states about the
findings corpus or the plan is checked only where the module names a predicate for it. Nothing here says a count was
**wrong when it was written**, only that it is not what it was; and the four counts with no predicate are reported
unchecked, which is the audit's largest gap and the one the module states.
