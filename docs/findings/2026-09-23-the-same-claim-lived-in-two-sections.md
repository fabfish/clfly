# The same claim lived in two sections, and I read past the stale half twice

**Date:** 2026-09-23
**Where:** `docs/paper/clfly-v1.md` §4.7's closing sentence and §8's first item, plus the abstract's network
sentence; the artifact used is `runs/e3_analytic.json`.
**Context:** the class-IL audit (`f2026-09-23-the-propagation-audit…`), where one half of a sentence had been
updated and the other read past; and the propagation pass, which grepped for corrected *numbers*.

---

## 1. The contradiction

§4.7 ended its synapse discussion with:

> So the defensible claim is that biology does not help *synapse* anchoring at 0.925 constrained, **and the
> rung the neuron result implicates is untested.**

§8's first item, fifty pages later, says the opposite and reports the run:

> `side` is the rung the neuron result most implicates, **and it has now been run** — `runs/e10_rung_side.json`
> … where the negative holds and the test is too weak to be decisive (−0.0116 accuracy …).

And the plan's C2b carries the table: naive 0.8241, `ewc-block` **0.8148 ± 0.0346**, `ewc-block-rand`
**0.8264 ± 0.0212**, i.e. **biological minus matched random = −0.0116 accuracy**. So the negative holds at
`side` and the test is weak — which is what §8 and the plan say and what §4.7 denied.

**I edited §4.7 twice this week** — the Fisher-batch paragraphs immediately below this sentence — and read
past it both times, because the paragraph I was fixing began *after* the line that was wrong.

## 2. Why the propagation pass could not have caught it

That pass grepped for the **corrected numbers** (`21 of 25`, `0.701`, `45–63`, `inflated several-fold`, …) with
whitespace-insensitive patterns, and it found the seven surviving hits. This one has **no number in it**:

| where | what it says |
|---|---|
| §4.7 | the rung "**is untested**" |
| §8 | the rung "**has now been run**" |

**Two different phrasings of one claim, neither containing a number.** So a number-grep cannot see it, and
rule 22's variant-spelling blind spot — "bit-for-bit" surviving a search for "bit-identical" — applies to
claims about *status* exactly as it applies to numbers. The check that finds it is to search for the **claim's
subject** (`side`, the rung, the network negative) across all sections, not for its wording or its figures.

**This is the third instance of the same mechanism this week**, and the three differ only in what the stale
half is keyed on: the class-IL row was half of a sentence; the `e86` status word was the header of a cell
whose body was updated; and this is a *different section* from the one that was updated. **The lesson is the
same in all three: an update has to be applied wherever the claim appears, and "wherever it appears" is not
findable by searching for what changed.**

## 3. And the same section-pair produced a second error, in the abstract

The abstract's network sentence called `cell_class` "**the rung where the neuron-level result is largest**".
Measured on `runs/e3_analytic.json`, the biological-minus-matched-random advantage by rung is:

| rung | bio excess | matched-random excess | advantage | constrained |
|---|---|---|---|---|
| **`side`** | 0.00395 | 0.00874 | **−0.00480** | 0.5011 |
| `cell_class` | 0.01142 | 0.01449 | −0.00307 | 0.8280 |
| `ito_lee_hemilineage` | 0.01414 | 0.01695 | −0.00280 | 0.9668 |
| `supertype` | 0.01566 | 0.01712 | −0.00146 | 0.9736 |
| `cell_type` | 0.01733 | 0.01707 | **+0.00026** | 0.9793 |

**`side` carries the largest advantage and `cell_class` is second of five** — so the parenthetical was false in
every reading: not by advantage, not by unpaired σ (`side` 28.78 against `cell_class` 12.14), and not by the
paired σ where `ito_lee_hemilineage`'s 26.1 leads. What `cell_class` actually is — the second-coarsest synapse
rung, the one the published negative used — is now what the abstract says.

## 4. The two errors are the same error

Both are in **summary** sentences about the network line: the abstract's parenthetical and §4.7's closing
clause. Neither is in a measurement. That is the boundary the last two audits established — **drift lives in
the sections that summarise, hedge or point at a result, and not in the sections that describe the substrate
or the method** — and this fire adds the case that boundary most needed: **a summary error whose stale half is
in a different section from its corrected half**, which makes it invisible to every check that operates on one
section or on one number at a time.

The guard is a checklist rather than a technique: **when a run completes, find the claim's subject everywhere
it is mentioned, including the abstract, and read each mention.** That is four places for this claim (§4.7, §8,
the abstract, the plan's C2b) and it took one grep for `side` to find them.
