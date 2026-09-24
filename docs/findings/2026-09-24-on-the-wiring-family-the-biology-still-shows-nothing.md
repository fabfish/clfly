# `e144`: on the family whose difficulty is in the wiring, the biology still shows no advantage — and the diagonal finally does

**Date:** 2026-09-24
**Artifact:** `runs/e144_r32_overlap1_methods_40reps.json` — four methods, forty replicates, `--input-overlap 1.0`,
read-out 32, the same seeds as every other run this session — plus the two control draws
`runs/e144_r32_overlap1_rand_draw{1,2}.json`.
**C0a, exact:** the `naive` row is **per-replicate identical** to `e142_r32_overlap1.json`'s, worst absolute
difference 0.000.
**Pre-registration:** `docs/findings/2026-09-24-the-basis-question-on-the-wiring-family-registered.md`, amended to a
three-draw control before the artifact landed.
**P1 fails and the falsifier fires — and the failure is the paper's central claim surviving the test its own
registration hoped would break it.**

---

## 1. The table, and the three-draw control

| method | forgetting | sem | accuracy |
|---|---|---|---|
| `naive` | +0.1068 | 0.0092 | 0.8939 |
| **`ewc`** (diagonal) | **+0.0630** | 0.0073 | 0.9003 |
| `ewc-block` (biological) | +0.0833 | 0.0088 | 0.9061 |
| `ewc-block-rand` (matched random) | +0.0852 | 0.0086 | 0.9049 |

**The central contrast, per draw and then combined as the registration specifies:**

| control draw | `ewc-block` − `ewc-block-rand` |
|---|---|
| draw 0 (this artifact) | −0.0018 ± 0.0108 = **0.17σ** |
| draw 1 (`3058aa874ae6`) | −0.0177 ± 0.0101 = **1.76σ** |
| draw 2 (`f6a658eabf9c`) | −0.0039 ± 0.0110 = **0.35σ** |
| **mean of the three** | **−0.0078, draw sd 0.0086 on 2 df; sem = 0.0050 (draw) + 0.0061 (paired) = 0.0079 → 0.99σ** |

**So P1 (≥3σ) fails and the falsifier (within 2σ of zero) fires.** The biological partition does **not** beat its
group-size-matched random control on this family — and on this family the extra forgetting was measured to live in
the **26,568 connectome-masked weights** (`e143`: it survives freezing the offsets at **5.04σ**), which is exactly
the channel a synapse partition acts on. **The registration's premise was that a null on the base family could be
an artefact of the base family's channel structure; this says it is not.**

**And the number is worth comparing with the base family's own**, which the same session measured at forty
replicates: there the same contrast is **2.08σ in favour of the biology** on **one** draw, i.e. **larger than this
family's three-draw 0.99σ** — and this fire's earlier analysis found that the base family's 2.08σ has **no
mechanism signature at all** (every recorded quantity is within 1.5σ, most within 0.6σ) **and a measured control
draw term of 0.0138 against the contrast's 0.0206**.

## 2. And the family produces the session's only resolved *method* result that is not replay

| contrast, forty paired seeds | value | resolution |
|---|---|---|
| **`ewc` − `naive`** | **−0.0437** | **4.73σ**, 31/40 negative |
| `ewc-block` − `naive` | −0.0234 | 2.26σ |
| `ewc-block-rand` − `naive` | −0.0216 | 2.48σ |
| `ewc` − `ewc-block` | −0.0203 | 1.94σ |
| accuracy: `ewc` − `naive` | +0.0064 | 1.05σ |

**On the base family at forty replicates the diagonal is 1.21σ from `naive`; here it is 4.73σ** — the first
configuration in this session where the *plain* diagonal penalty beats the baseline on forgetting at forty
replicates, **without any anchoring and without touching the channel** (`e138`'s anchored arms reach 4.84σ, and its
unanchored λ = 3e-4 arm 4.27σ). **And it beats both block arms**, 1.94σ over the biological one.

**So the two families disagree about the methods as well as about the magnitude**: on the harder family the plain
diagonal is the best Fisher arm and the block partition is no better than its random control, on both metrics
(accuracy: `ewc-block` − `naive` is 1.84σ and `ewc` − `naive` 1.05σ, i.e. the *ordering* is not even consistent in
accuracy). **Which is a second reading of the paper's central claim from a different direction**: not only does the
biology not help, **the coarser partition is not even the better granularity here.**

## 3. What this changes

- **The paper's central null now has a second configuration, chosen to stress the opposite channel.** §4.7's *"what
  resolves is partitioning the synapses coarsely and not the fly's grouping"* was measured on a benchmark where 70%
  of the forgetting lived where no partition looks; **on the family where that share is in the wiring, the biology
  still shows nothing (0.99σ over three draws)** — and the *granularity* claim weakens at the same time, since the
  block arms do not beat the diagonal.
- **And it makes the base family's 2.08σ harder to read as the biology.** That number is single-draw, its control
  is one sample from a population with a measured 0.0138 spread, and **the mechanism quantities are silent about
  it**; here the same contrast, measured properly with three draws, is **0.99σ**.
- **It is a negative result with a design that was registered against it**, which is the useful kind: the
  registration named the direction it hoped to find (the biology winning) and the falsifier that would close the
  question (within 2σ of zero), **and the falsifier is what fired.**

## 4. What it cannot settle

- **One read-out (32), one overlap value (1.0), one partition (`cell_class`), one λ (3e-3), forty replicates**, and
  the control's draw sd is estimated on **two** degrees of freedom, so 0.0086 is a bound on the draw term rather
  than a measurement of it.
- **The base family's 2.08σ remains unresolved rather than refuted** — its two extra draws are running, and its
  registration (P1 the three-draw contrast stays negative and at least as large as 2.08σ; falsifier within 2σ of
  zero) is the measurement that would settle it. **A 0.99σ here and a 2.08σ there are not a contradiction**, since
  the families differ and the numbers are two draws apart at most.
- **And the diagonal's 4.73σ is one contrast on one family**: it is not evidence that the diagonal is generally
  good, since on the base family at the same forty replicates it is 1.21σ, and this session's own λ sweep shows
  the diagonal's magnitude is hyper-parameter-shaped (`e141`: 3e-4 gives 4.27σ, 3e-3 gives 1.21σ).

## 5. And the two families differ in the *shape* of the diagonal's effect, not only in its size

The per-task decomposition — the project's eighth trap, applied to the contrast that *did* resolve here:

| diagonal − naive, per task | task 0 | task 1 |
|---|---|---|
| **base family** (`overlap 0.0`) | **−0.0354 ± 0.0094 = 3.79σ** | **+0.0161 ± 0.0118 = 1.37σ — *worse*** |
| **wiring family** (`overlap 1.0`) | **−0.0693 ± 0.0133 = 5.20σ** | **−0.0182 ± 0.0161 = 1.13σ — also better** |

**On the base family the diagonal buys task-0 retention and pays for it on task 1; on the wiring family it
improves both** — one decisively, the other unresolved. So the two families differ in the **shape** of the
penalty's effect and not only in the size of its mean, and **the shape difference is what the channel story
predicts**: on the base family the penalty's displacement into the 800 offsets is what costs the later task
(`e133` and `e137`), while on the wiring family there is no such displacement to pay with, because the difficulty
is already in the channel the penalty covers. **A trade is what a penalty looks like when part of the adaptation
escapes into something it does not press.**

**And the central contrast's null is uniform rather than a cancellation**: `ewc-block` − `ewc-block-rand` is
**−0.0047 ± 0.0118 = 0.40σ on task 0 and +0.0010 ± 0.0147 = 0.07σ on task 1** — flat on both, in *opposite*
directions, so the three-draw mean of −0.0078 is not two resolved terms cancelling but two unresolved terms
sitting near zero. **Which is the same shape its falsifier's firing implies, and the opposite of the base
family's, where the same contrast was uniform in sign on both tasks.**
