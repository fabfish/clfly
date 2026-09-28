# The recommendation needed a comparator and a metric: three basis recommendations, none of them scoped, and the clause each now carries

*2026-09-29 04:09. Runs: **none new** — `experiments/e298_the_recommendation_needs_a_comparator.py` reads the paper's
basis recommendations and re-reads them after this fire's correction, writing
`runs/e298_the_recommendation_needs_a_comparator.json`. Seconds.*

## 1. Why a recommendation needs a scope now

`e295`, `e296` and `e297` establish three things the paper's advice cannot be read without: the block-anchored penalty
is **better on accuracy and worse on forgetting** than the diagonal at every resolved comparison; it beats its
**matched random** control on forgetting only where the power is and **loses** to it on accuracy by count; and the
corpus's two metrics order the five arms into two chains whose ends are swapped. **A recommendation that names neither
its comparator nor its metric is not yet a statement a reader can act on.**

## 2. What was found

The instrument reads the paper for sentences carrying an advice cue and a basis noun — **three** of them — and each is
read for a metric and for the alternative it is preferred to:

| sentence | what it recommends | metric named | comparator named |
|---|---|---|---|
| §4.4 | *pool the rarest cell types and anchor there* | **none** | **none** |
| §5 | the wiring's preferred directions are a better place to anchor a Fisher than … | **none** | `than the neuron coordinate basis` |
| §8 item | *anchor at the coarsest granularity the arithmetic allows* | **none** | **none** |

**As found: 0 of 3 named a metric and 1 of 3 named a comparator.**

Two readings of the instrument had to be repaired before that count was trustworthy, and both are worth recording
because they were found by reading the instrument's own output rather than by a test: the sentence rule inherited from
`e282` splits on punctuation alone, so a paragraph opening with bold text was being **merged into its predecessor**
(which pulled the λ-sweep's numbers into the first recommendation); and `anchor` was in the basis-noun list, so a
λ-sweep sentence that merely *quotes* the aphorism *"Anchor gently, and do not estimate the curvature too carefully"*
read as a basis recommendation. `anchor` is the advice, not the basis; with it removed and paragraphs made a hard
boundary, the three sentences above are what remains.

## 3. The correction, and the invariant it leaves behind

Each of the three now carries a scope clause: **against the diagonal** on `accuracy` (8 of that arm pair's 9 resolved
comparisons) and **against a matched random partition** on `forgetting` where forty replicates have the power, with the
units cited (`docs/findings/2026-09-29-which-metric-selects-the-basis.md`,
`docs/findings/2026-09-29-the-matched-random-control.md`, `docs/findings/2026-09-29-the-ordering-of-the-arms.md`). The
middle sentence keeps its own comparator and gains the metric.

The three registered claims are stated as the **invariant the paper now satisfies** — every basis recommendation names
its metric, names its comparator, and cites the unit that supplies the scope — because that is what makes the unit
useful going forward: a future edit that adds an unscoped recommendation turns it red. Re-read after the correction:
**3 of 3, 3 of 3, 3 of 3.**

## 4. What it cannot do

**The sentence rule and the two lists are lexical**, so a recommendation phrased without an advice cue is invisible and
the count is a lower bound — `e282`'s splitter's limits apply, plus the paragraph boundary added here. **The comparator
list can only see comparators named as phrases**: a sentence that says "better" without saying *than what* reads as
unscoped, which is the reading this unit wants and not a reading that catches every omission. **N3 is a ledger claim
about text**, so it verifies that a scope clause exists and not that the clause's numbers are right — that provenance is
`e295` to `e297`'s business. **As-found claims about a corrected document cannot be re-run**: the claims are the
invariant, and the as-found counts (0 of 3 metrics, 1 of 3 comparators) live in this finding rather than in the
artifact. **And nothing here re-reads the corpus**: the units that measured what the scope should say are the ones
cited.
