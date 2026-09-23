# E91 — a third hybrid, a line break that hid a phrase — and the whitespace-insensitive search that fixed the method

**Date:** 2026-09-23
**Artifact:** `docs/paper/clfly-v1.md` §6 and §4.7
**Source:** `docs/findings/2026-09-22-metric-instability.md`
**Context:** `2026-09-23-the-abstract-had-six-stale-figures.md` (e89, which found the first two hybrids), plan rule 22

---

## 1. What the sentence said, and what the finding it cites actually measured

§6 opened with:

> At fixed settings its **standard deviation across seeds reaches 1.38** while its mean is 0.87.

The cited finding, `metric-instability.md`, contains **two different diagnostics** and the sentence takes
one figure from each:

| diagnostic | what it gives | value |
|---|---|---|
| the κ sweep at d = 1307, 3 seeds | the ratio's **spread across seeds**, i.e. max − min | **1.384** at κ = 4 (values 1.208, 1.393 and 0.009) |
| a separate run at **400 neurons, support 40**, 3 seeds | **gap standard deviations** | **up to 1.06**, "against a mean of 0.87" |

So "a standard deviation of 1.38" is really a **range of 1.38**, and it is paired with the 0.87 that
belongs to the *other* run's mean. For three seeds a range is roughly 1.7 standard deviations, so the
sentence overstates the sd by about 1.3× **and reports the wrong kind of statistic**, on the number whose
whole purpose is to establish that this metric is unusable.

The corrected sentence states both diagnostics separately, and says which is which.

## 2. Why it was not caught, and the second blind spot in the same method

`e89` established one blind spot of a grep-based audit: **a variant spelling escapes it** ("bit-reproducible"
survived five passes because rule 21 withdrew "bit-for-bit"). This instance adds another, and it is
mechanical:

> **A phrase split across a line break escapes a line-based grep.**

§6's sentence is wrapped as `its standard` / `deviation across seeds reaches`, so a search for
"standard deviation" does not match it. The phrase "standard deviation" appears in the paper **twice** and
the grep returned one — the one that happens to fit on a line.

That is worth recording because it is the cheapest possible failure to guard against, and the guard is
mechanical: **search with a whitespace-insensitive pattern** — `standard\s+deviation` rather than
`standard deviation`. Running that over the paper upgraded the count of "standard deviation" hits from
**1 to 4** (three of them were the corrected §6 and its note, so §6 was the only real error there) and
found **one further leftover**: §4.7's "the `naive` arm is bit-identical to `e8_hardened`'s", an instance
of the phrase rule 21 withdrew that the line-based greps for "bit-for-bit" and "bit-identical" both
matched only in their unwrapped occurrences. That one is now "reproduces `e8_hardened`'s to the last
printed decimal", which is what an environment-scoped identity test can claim.

The audit method that has been finding these — grep for the overturned figure — has now missed something
for **four** distinct reasons across four passes (variant spelling, hybrid range, line wrap, and a phrase
whose two occurrences wrap differently), and three of the four misses were found by reading rather than by
searching. The whitespace-insensitive search is the one improvement that has cost nothing and found
something.

## 3. The pattern, now at three instances

The paper has carried **three hybrid figures**, all constructed by joining a number to the wrong
companion:

| claim | joined | from | should be |
|---|---|---|---|
| the abstract's excess-error range, "**+33–63%**" | the measured 33% | + the *realization-based* 63% | +33–34%, both measured (e89) |
| §6's "**standard deviation** of 1.38 **with mean 0.87**" | the κ sweep's range | + the 400-neuron run's mean | a range of 1.38, or an sd of 1.06 against 0.87 |
| §7's "the ladder resolves 7 of 8 with **the same exception** (`pool1`), a fourth confirmation of **that null**" | the count of rungs | + the *null* reading of a rung that is a resolved disadvantage | 8 of 8 per-seed unanimous, `pool1` a 20.3σ disadvantage (e85) |

**All three have the same shape**: a summary sentence that inherits its numbers from two places rather than
re-deriving them from one, which is the mechanism `e85` identified for the plan's drift and `e84` for the
failed fingerprint. The distinguishing feature of this family is that **each element is individually
defensible**, which is why no check aimed at the elements finds them.

## 4. Limits

- **Reading is the only method that has caught these.** Three passes of the same automated audit missed one
  each, for three unrelated reasons; §6 was found by reading the section. That is a statement about the
  audit's power, not about the section's importance.
- **The corrected §6 sentence is now longer than the wrong one was**, and it names the two diagnostics
  explicitly. The paper's §6 is a methodological section and can absorb the length; the abstract's
  corresponding claim ("a standard deviation exceeding its own mean") was already correct, because it
  quoted the **400-neuron** diagnostic's sd against **that same run's** mean.
- **No result changes.** Both numbers come from the same finding; what was wrong was which statistic one of
  them is and which run the other belongs to.
