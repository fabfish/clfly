# The conclusion was right and its evidence was a single-seed sweep that no longer exists

**Date:** 2026-09-23
**Method:** the three network fires of this week (`e99`, `e100`, `e101`) read back against what the paper
already said, and against the audit that found the `e8c` artifact unreproducible.
**Context:** `docs/findings/2026-09-23-the-batch-count-discriminator.md` (`e101`);
`docs/findings/2026-09-23-the-fisher-batch-sweep-is-a-stitch-of-first-replicates.md`, which found that
`runs/e8_fisher_batches.json` had been overwritten by a later run and that **no artifact on disk carries a
128-batch Fisher at all**.

---

## 1. The paper ruled out the estimation-noise account before this week started

§4.7 says it twice, and both sentences are about the same account:

> Two candidate explanations were tested and both ruled out: the block Fisher's failure is not estimation
> noise (**raising the batch count does not help**, and the effect sizes *halve* under more replicates), and it
> is not a badly tuned λ (five values swept, with the bio-versus-random ordering flipping between them).

> That reversal is **suggestive, not established**: it is 0.9σ at 8 batches and absent at 128, and it was
> never above 2σ. The mechanism proposed for it — estimation noise, the block Fisher having 5.3e7 entries to
> fill from 1024 observations — was **tested and refuted**: a 16-fold better estimate does not recover the
> block's position, so its disadvantage is not an artefact of a poor estimate.

**So the account I spent three fires supporting was already refuted in the paper.** `e99` and `e100` reported
a 58% and then a 95% reduction in the block's penalty as its Fisher got better estimated, and `e100`'s
discriminator clause was read as *two independent confirmations*. **Both fires were re-deriving a hypothesis
the project had ruled out**, and `e101` — the one manipulation that changes estimation quality alone, with the
level provably fixed — **returned to the ruled-out verdict on replicated data**.

## 2. What was actually wrong was the evidence, not the conclusion

The ruling-out rested on the `e8c` sweep: **one seed**, three batch counts, in an artifact that the later audit
found had been **overwritten** — so that no artifact on disk carries a 128-batch Fisher at all, and the
sweep's numbers survived only in a finding's prose table. §4.7's "0.9σ at 8 batches and absent at 128" is
therefore a reading of single-seed point estimates whose record is gone.

**`e101` replaces it with a replicated version, and the replacement is stronger in three ways**:

| | `e8c` (the evidence §4.7 cites) | `e101` |
|---|---|---|
| replicates | **1 seed** | **5**, with sems |
| level control | none — the batch sweep also moves every arm | **`naive` identical to six decimals** across 8, 32 and 128, so the level is provably fixed |
| the block's standing vs its matched control | "does not help" | **negative at both controlled ends** (−0.0354 at 8, −0.0167 at 128 — it *beats* the control) |
| artifact | **overwritten; the 128-batch point exists nowhere** | `runs/e101_rate_fb8.json`, `runs/e101_rate_fb128.json` |

So the correct sentence for §4.7 is not *"the account is refuted"* alone but *"the account is refuted **and the
refutation is now replicated rather than single-seed**"* — and §4.7's "0.9σ at 8 batches" should be replaced by
the replicated figure with its σ, because a reader cannot check the old one and it is not the same number.

## 3. The same week found the same evidence base unreproducible, from the other side

This is the second time the `e8c` sweep has been the weak point. The earlier audit followed §4.7's *other*
claim — that the diagonal degrades as its Fisher estimate improves — to `runs/e8_fisher_batches.json` and
found a three-repeat 32-batch run where the sweep should have been, plus **four numbers that appear in no
artifact at all**. So one sweep was simultaneously:

- the evidence for a claim that is *true* (the block's disadvantage is not estimation noise — `e101` confirms),
  and
- the evidence for a claim that is *false* (the diagonal's forgetting rising to +0.250 — no artifact, and
  `e96` measured +0.146 at 128 batches).

**A single untraceable sweep was carrying a true conclusion and a false one**, and nothing in the project
distinguished them until each was followed to its source. The lesson is not that one of them was wrong; it is
that **a shared evidence base makes two claims look equally well supported when their support differs**, and
the only way to tell is to check each independently — which is what took two fires.

## 4. And the design lesson, which belongs in the rules

`e101`'s discriminating power came entirely from the benchmark containing **arms that cannot depend on the
manipulated variable**: `naive` and `replay` consult no Fisher matrix, so the level is fixed by construction.
**That is a property worth building into every cross-run comparison on this line**, because the alternative is
what the last fire found — two candidate explanations whose separating experiment needed ~57 replicates per
arm. The check is one line: *does this manipulation leave anything bit-identical, and is that thing sensitive
to the effect I am claiming?*

**And the same property flagged a defect**: `replay` came out identical between the two new runs and different
at the older one, which is how the 32-batch point was identified as a different environment. **A Fisher-free
arm is therefore both the level control and the environment detector**, and neither role needs any new
machinery — only the observation that the arm should not have moved.
