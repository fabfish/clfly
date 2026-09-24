# The metric decides the threshold

**Date:** 2026-09-24
**Script:** none new — both quantities were already in the artifacts `e141` wrote.
**Artifacts:** `runs/e141_r32_ewc_lam{3e-4,3e-2,3e-1}.json` and `runs/e133_r32_naive_ewc_40reps.json`'s `naive`
and `ewc` arms, forty replicates each on the same seeds.
**Context:** `e141`'s registered **P2** — *"the forgetting does not fall as λ rises"*, read as λ = 3e-2 worse than
3e-3 at ≥2σ — **failed at 1.60σ** while the mechanism predictions held at 16.63σ and 22.35σ. Every artifact
records `retention_loss` beside `retention`, so the same question can be asked of the other metric **without a
single new run**. It answers differently.

---

## 1. The same contrast on the two recorded metrics

Forgetting is defined so that **larger is worse in both metrics** — `max − final` for accuracy, `final − max` for
loss, since a loss is better when smaller:

| arm | accuracy-valued forgetting | loss-valued forgetting | acc. relative sd | loss relative sd |
|---|---|---|---|---|
| `naive` | +0.0750 | +0.1767 | 74.2% | 51.9% |
| **λ = 3e-4** | **+0.0396** | **+0.1177** | 113.4% | 44.9% |
| λ = 3e-3 | +0.0654 | +0.1783 | 76.8% | 45.9% |
| λ = 3e-2 | +0.0810 | +0.2434 | 70.2% | 33.6% |
| λ = 3e-1 | +0.0846 | +0.2905 | 62.5% | 36.7% |

**The registered contrast, on each metric, over the same forty pairs:**

| contrast | accuracy-valued | loss-valued |
|---|---|---|
| **P2, λ = 3e-2 minus 3e-3** | **+0.0156 ± 0.0098 = 1.60σ — FAILS** | **+0.0651 ± 0.0154 = 4.24σ — would have held** |
| the floor against 3e-3 | −0.0258 ± 0.0069 = 3.74σ | −0.0606 ± 0.0125 = **4.85σ** |

**So the registration's verdict on its own P2 is a statement about the metric as much as about the effect**: the
question it asked — *does raising λ worsen retention?* — is answered **yes at 4.24σ** by a quantity the project
was already recording in the same artifact, and the form it chose to ask it in failed at 1.60σ.

## 2. And the two metrics agree, which is what makes the above a measurement rather than a choice

- **In ordering, across all five arms**: third-best-to-worst reads 3e-4 < 3e-3 < 3e-2 < 3e-1 in **both** metrics,
  with `naive` between 3e-4 and 3e-3 in both.
- **Within arms, across seeds**: pearson **+0.51 to +0.71** and spearman **+0.51 to +0.64** in **five independent
  arms** — which **replicates, at a different read-out, the +0.785 of `§8` item 5** (measured at read-out 128 with
  a tenfold test set).

**So this is not "one metric is right and the other is wrong".** The two rank the same forty seeds at about +0.6,
agree on the arms' ordering, and disagree only on **whether a 0.016 effect is resolvable at forty pairs** —
which is the threshold question, not the effect question.

## 3. Which qualifies `§8` item 5's "it buys nothing"

That item measured, at read-out 128 with a tenfold test set, that the loss metric's relative precision is **50.1%
against the accuracy metric's 55.1%** — a ratio of **0.91** — and concluded that re-expressing the forgetting buys
nothing. **On this configuration the loss metric is the more precise of the two in every one of the five arms**:
its relative per-replicate spread is **33.6–51.9%** against the accuracy metric's **62.5–113.4%**, i.e. roughly
half at the noisy end. The two measurements are not in conflict — different read-out, different test-set size,
different normalisation — but **the honest form of item 5's conclusion is configuration-specific rather than
general**: *at read-out 128 a tenfold test set, the loss buys nothing; at read-out 32 it is the more precise of
the two and it resolves a registered contrast that the accuracy metric could not.*

## 4. And the loss metric has a property that has to be said out loud

**`retention_loss` is a *training-split* loss** — the runner computes it with `full_split_loss(..., "train")` —
so its "forgetting" is partly a statement about **fitting**: a network that has stopped fitting task *j* as well
has a larger loss there, and one that has *not* moved also has a smaller one. **The accuracy metric is measured
on the test split.** So the two are not the same quantity measured twice: one is generalisation and one is fit,
and **the loss metric's smaller relative spread is consistent with it being a less noisy but also less
independent measure** — it can fall, or fail to rise, because the model is fitting the *train* set of an old task
that its accuracy on the *test* set says it has forgotten.

**Which is a reason to prefer it as a *second* reading rather than as a replacement** — and a reason the
statement above is *"the same question answers differently on the other recorded metric"* rather than *"the loss
metric is the right one"*.

## 5. What this changes, and what it cannot settle

- **It adds a form to rule 37's problem.** Rule 37 says a registered threshold needs the statistic's own
  uncertainty, or it is a coin-flip dressed as a bar. **This is the same defect one level up: the *metric* is part
  of the statistic**, and a registration that names a contrast without naming the quantity it is read on has
  chosen its bar and its outcome together. The repair is the same one rule 37 prescribes — **name the form, and
  name the metric, before the number is known** — and `e141`'s registration named the metric as "mean forgetting",
  which is the accuracy one, so **its verdict stands as registered** even though the other metric would have
  carried it.
- **It does not settle which metric is the better measure of "forgetting"** — §4 is a reason to expect the loss
  metric to be *less* independent, and the read-out-128 result in §3 is a reason to expect it to be no more
  precise there. One configuration is one configuration.
- **It cannot be generalised from three tasks** and one read-out, and the contrast it resolves (0.065 on a
  quantity whose arm means are 0.118–0.291) is large in *absolute* loss terms and small in accuracy terms
  (0.016 against 0.039–0.085).
- **And it does not touch the mechanism results**: P1 and P2b were measured on the bias's displacement and θ's
  drift, where both metrics' arms move together, so the λ ordering that the loss metric resolves is the same
  ordering the mechanism predicts.
