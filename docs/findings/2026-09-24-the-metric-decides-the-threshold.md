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

## 6. And it is a pattern rather than an instance: four contrasts, the same direction each time

P2 is one contrast. The same two quantities are in every artifact this session wrote, so the session's principal
contrasts can all be read both ways — and the loss-valued forgetting resolves **at least as strongly** in every
one:

| contrast | accuracy-valued | loss-valued |
|---|---|---|
| `e125`'s frozen bias − `naive` | −0.0523 ± 0.0089 = **5.90σ** | −0.1200 ± 0.0138 = **8.69σ** |
| `e138`'s anchored 33.2 − `naive` | −0.0458 ± 0.0095 = **4.84σ** | −0.0810 ± 0.0163 = **4.98σ** |
| `e138`'s anchored 33.2 − unanchored | −0.0362 ± 0.0090 = **4.03σ** | −0.0826 ± 0.0167 = **4.93σ** |
| `e141`'s λ = 3e-4 − the 3e-3 rule | −0.0258 ± 0.0069 = **3.74σ** | −0.0606 ± 0.0125 = **4.85σ** |
| **`e141`'s P2, λ = 3e-2 − 3e-3** | **+0.0156 ± 0.0098 = 1.60σ — the only failure** | **+0.0651 ± 0.0154 = 4.24σ** |

**Every direction agrees; three of the four resolved contrasts are stronger on loss and the fourth is equal; and
the contrast the accuracy metric failed is the one the loss metric carries.** So on this configuration the
loss-valued forgetting is not merely a second reading — it is **the more resolving of the two**, which is what
makes §3's qualification of `§8` item 5's *"it buys nothing"* a pattern rather than a single measurement.

**And the honest limits of "pattern" here.** These five rows are **not five replications**: they share one
configuration, one read-out (32), one circuit, three tasks and the same forty seeds, and two of them are the same
arm compared against two different references. **What is replicated is the *metric's* behaviour across contrasts,
not the contrasts themselves** — and §4's caveat stands unchanged, since a training-split loss measures fit where
the accuracy metric measures generalisation. The form of the claim is therefore: *on the configuration this
session has swept, the loss-valued retention resolves the same effects at least as well, and the one registered
threshold the accuracy metric missed is one it would have met.*

## 7. And it decides *both* of the session's knife-edge registrations

Two registrations this session missed their bars — `e142`'s **3σ** by **0.012σ** and `e141`'s **2σ** by **0.4σ** —
and both are cases where the *other* recorded metric clears the bar comfortably. The harder-family contrasts can
be read both ways for the same reason (every artifact carries both matrices), and they make the pattern sharper
because they are **independent measurements rather than more λ points**:

| contrast | accuracy-valued | loss-valued |
|---|---|---|
| **`e142`'s P1: overlap 1.0 − overlap 0.0, plastic** | **+0.03177 ± 0.01063 = 2.99σ — the registered bar is 3σ** | **+0.11372 ± 0.02310 = 4.92σ** |
| `e143`'s falsifier: the surviving family difference under the freeze | +0.03724 ± 0.00739 = 5.04σ | +0.08038 ± 0.00776 = **10.35σ** |
| the freeze within overlap 0.0 | −0.05234 ± 0.00887 = 5.90σ | −0.11997 ± 0.01381 = **8.69σ** |
| the freeze within overlap 1.0 | −0.04687 ± 0.00929 = 5.04σ | −0.15331 ± 0.01471 = **10.42σ** |

**So the metric decides both of the session's threshold-miss cases**: `e142`'s registered P1 fails at **2.99σ**
against its 3σ bar and the same forty pairs give **4.92σ** on the loss-valued forgetting, and `e141`'s P2 fails at
1.60σ and gives 4.24σ. **Two of two.**

**And the knife-edges were already suspect for an independent reason**, which is why this is a repair of the
reading rather than of the value: rule 37 was written from `e142`'s miss, and rule 38's bracketed-optimum language
exists because a bar at 3.00σ whose sem is estimated from forty pairs cannot separate 2.7 from 3.4. **What this
section adds is that the same data carry a second quantity which resolves it** — so the honest form of both
verdicts is *"failed on the metric the registration named, met on the other quantity in the same file"*, and the
registration's failure is a statement about the registration.

**And the pattern's count, for the record**: across the **eight contrasts** this session read both ways, the
directions agree **8 of 8**, the loss-valued reading is stronger in **7** and equal in **1**, and both
threshold-misses are among them. That is a pattern about *this configuration's two recorded metrics*, not about
either metric in general — §4's train-split caveat still stands, and the read-out-128 comparison in §3 still found
the loss metric no more precise than accuracy at a tenfold test set.
