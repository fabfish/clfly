# Registered: five drawings at each of two alloy fractions, so the penalty can be regressed on measured alignment

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written: `runs/e213_alloy_draws_rs0.json` …
`rs4.json` (five runs, two cells each).

---

## 1. What the last fire established, and what it left the next design owing

`e212` measured penalties inside the alignment hole for the first time — and its two `alloy1` drawings **disagreed by a
factor 2.44×** (excess +0.10067 at alignment 0.14179 / 2.55× chance, against +0.04130 at 0.12815 / 2.31×) while two
`alloy0.75` drawings agreed to 0.00558. The comparison that made it structural: the **Erdős–Rényi** family spans
**1.05× across nine drawings**, so the high regime is the tightest thing in the record and the transition region the
loosest. The registered verdict was its own **null**: a rise that is not monotone, unresolved at ≤4 cells.

Two obligations follow, and both are measured rather than assumed:

- **several drawings per alignment band**, because one cell per alignment is not a measurement of that alignment;
- **the penalty regressed on each drawing's MEASURED alignment**, because the drawings' alignments move too (2.55×
  against 2.31× at one fixed fraction), so a design that fixes the requested fraction and hopes the alignment repeats
  confounds the drawing with the alignment.

## 2. The design

Ten cells, **full analytic mode** (each artifact carries both the `geometry` block and the penalty, so no
cross-artifact assumption is needed):

```
experiments/e2_topology_gap.py --circuit-size 800 --support 80 --seeds 3 --seed0 0 --q 0.02 \
  --topologies alloy0.9,alloy1 --rewire-seed {0..4} --no-realized \
  --json-out runs/e213_alloy_draws_rs{0..4}.json
```

`alloy0.9` and `alloy1` are the two fractions that reached the band in `e212`'s screen (`alloy0.75`'s alignment is
0.78–0.95× chance, below it); five realizations each gives **ten (alignment, penalty) pairs** with five drawings at
each of two fractions. **Cost (rule 49)**: two cells per run at 225–240 s each plus the circuit build, so **five runs ≈
40–45 min**, one command per realization on an idle machine.

## 3. The claims

**W1 — the band is populated.** At least **three of the ten** cells have alignment inside `[0.09101, 0.27135]`.
**Falsifier**: fewer than three, which would say the top of the alloy family is itself scattered around the band's
floor and that reaching the interior needs the third construction (sources randomised as well, or an Erdős–Rényi mix)
rather than more drawings of this one. **Null**: exactly two, leaving the regression to rest on a pair.

**W2 — the fraction effect is larger than the drawing effect (the question the last fire raised).** The mean excess of
the five `alloy1` drawings differs from the mean of the five `alloy0.9` drawings by **at least 1.5× the larger of the
two within-fraction ranges**. **Falsifier**: the means differ by **less than** the larger within-fraction range, i.e.
**the requested fraction tells you nothing once the drawing is accounted for** — which would make the
alignment→penalty relation unmeasurable at this scale and would make the alloy a poor instrument for C3 even though it
is a good one for *placing* alignment. **Null**: a difference of 1.0–1.5× the range.

**W3 — the penalty tracks measured alignment across drawings.** The **Spearman** rank correlation between the ten
cells' measured `all_pairs_alignment` and their analytic excess is **at least +0.5**. **Falsifier**: at or below **0**,
which would say the two quantities are unrelated across drawings and that the regime structure (`e207`'s flat regime
against the tight high regime) is a property of the *constructions' names* rather than of the alignment they produce.
**Null**: 0 to +0.5, unresolved at ten points from two fractions.

**Reported rather than claimed**: every cell's alignment, × chance, `top_eig_share`, `effective_rank`, `flattening`,
excess and sem, and the paired contrasts between the two fractions at the shared task seeds — so the numbers can be
re-read by a reader rather than by a session.

## 4. What this cannot do

- **Separate alignment from `top_eig_share` and `effective_rank`.** The alloy moves all three, and this design holds
  only the fraction and the realization; a statistic that tracks alignment perfectly across these ten cells cannot be
  told from alignment itself here.
- **Reach the upper half of the hole** `[0.20, 0.271]`: `alloy1` is this family's ceiling (a fraction cannot exceed 1),
  so that interval needs a third construction — and it is the interval where `e212`'s one high drawing sat, so the
  graded reading of the transition may live there rather than in the lower half.
- **Speak for other circuit sizes** or for the task draw (`seed0` 0 throughout).
- **Give a distribution**: five drawings give a range and not an sd, and the project's own convention after the
  support-draw work is to quote spans for a handful of samples.
