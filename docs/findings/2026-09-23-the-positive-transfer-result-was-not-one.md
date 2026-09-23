# The "positive transfer result" was not one: I compared against `naive` and stopped there

**Date:** 2026-09-23
**Method:** the previous fire's counter-result re-checked against the matched-random control, which is the
comparison this project requires and the one I did not carry the framing through.
**Context:** `docs/findings/2026-09-23-the-batch-count-discriminator.md`, which reported *"a positive transfer
result the paper does not report"*; and the paper's §4.7, which exists to make this comparison.

---

## 1. The claim, and its counterexample, both on the same artifacts

Last fire reported that the biological synapse block resolves an advantage over `naive` — **2.48σ at 8 batches
and 3.12σ at 128** — and called it a transfer result the paper's §4.7 did not carry. Every number was right.
What was missing was the row beside it:

| contrast, mean forgetting | 8 batches | 128 batches |
|---|---|---|
| block (biological) − `naive` | −0.0562 (**2.48σ**) | −0.0625 (**3.12σ**) |
| **block-rand (matched control) − `naive`** | −0.0208 (0.89σ) | **−0.0458 (2.60σ)** |
| diagonal − `naive` | −0.0458 (2.40σ) | −0.0479 (2.31σ) |
| **block − its matched control** | −0.0354 (**1.44σ**) | −0.0167 (**1.04σ**) |

**At 128 batches the advantage over `naive` is shared almost entirely by a size-matched *random* partition of
the same synapses** — 2.60σ against the block's 3.12σ — so it is a **granularity** effect and not a biology
one. At 8 batches the block's advantage is larger than its control's (2.48σ against 0.89σ), but the
biology-specific contrast is still **1.44σ** and does not resolve.

**So across all three batch counts the one contrast that isolates biology is −0.0354 (1.44σ), +0.0167 (0.65σ)
and −0.0167 (1.04σ)** — its **sign is unstable** and nothing is resolved at any batch count. That is not a new
positive result; it is the paper's existing claim, exactly:

> **at `cell_class` granularity the biological synapse partition shows no advantage over its size-matched random
> control in any of the five settings tested** … and its ordering against that control **flips sign between
> them** — the null-effect signature.

**The paper was right and my counter-result was an artefact of stopping one comparison short.** §4.7's
sentence has been restored to that claim, with the three batch counts of `e101` added to its five settings.

## 2. Why this is the same error the week has been about, one level in

The cron's standing rule for this project is *"a biological partition must always be compared against a
group-size-matched random partition."* **I complied with it — the contrast is in the finding, at 1.44σ and
1.04σ — and then wrote the conclusion from the comparison that flattered biology anyway.** Having the control
and *using* it are different acts, and only the second is the discipline.

**And it is the same shape as the three corrections of this week, in a new place**: `e99` and `e100` read a
monotone reduction from point estimates whose movements were inside their own error bars; I read a transfer
result from a contrast whose control made the same claim. **In each case the number was measured, the
comparator was available, and the sentence was written from the half that supported the conclusion.** That is
four instances in three fires, and all four were mine.

**The check that catches this one is arithmetic rather than procedural**: before calling a difference an
*advantage*, compute the same difference for the control and see whether it survives. It costs one line, and
on these artifacts it would have cost nothing at all — the control's own contrast was already in the run's
output, printed four lines below the block's.

## 3. What the network line's batch sweep does establish

The four fires that produced and then removed this claim leave three things that stand:

- **The estimation-noise account is refuted**, replicated: five replicates, the level held bit-identical, and
  the block's gap against its control negative at both controlled batch counts rather than merely absent
  (`docs/findings/2026-09-23-the-conclusion-was-right-and-its-evidence-was-one-seed.md`).
- **All three Fisher variants beat `naive` at λ = 0.003** (2.31–3.12σ across the two controlled batch counts),
  which is a *granularity* result: the matched random control gets the same benefit, so what helps is
  partitioning the synapses coarsely and not the fly's grouping of them.
- **And the biology-specific contrast has now been measured at three batch counts in one design and resolves
  at none of them**, with a sign that moves. That is a *stronger* form of §4.7's existing claim — the same
  conclusion, from a design whose comparator is a partition of the same shape and the same batch count.
