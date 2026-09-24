# The level knob moves the gain: the room account is confirmed at the low end, and the high end is a null

**Date:** 2026-09-25
**Script:** `experiments/e171_noise_level_knob.py` — written **before** the data existed; run on both of `e167`'s
arms. Artifact: `runs/e171_noise_level_knob.json`.
**Registered as:** `e167` (the run) and `e171` (the read), both in the programme table before either existed.

---

## 1. The two ends

`e166`'s census found the room account's direction in **5 of 5 resolved cases and 0 against**, and then
disqualified its own evidence: the field that cannot move the level moves the gain by **0.0500**, 8 of the 13
level-moving rows are the closed `frozen_bias` diagnostic, and the other two fields change the task structure
(`classes`) or the decoder (`readout_size`). **What was missing is a level knob at fixed architecture and fixed
task structure**, and `e167` runs one at λ = 3e-4, where the base family's penalty is resolved.

| setting | `naive` forgetting | level step | resolution | the penalty's gain | gain step | resolution |
|---|---|---|---|---|---|---|
| noise 1.0 (reference) | 0.0750 | — | — | **+0.0354** | — | — |
| **noise 0.5** | **0.0438** | **−0.0312** | **3.55σ** | **−0.0016** | **−0.0370** | **3.57σ** |
| noise 2.0 | 0.0896 | +0.0146 | **1.15σ** | +0.0310 | −0.0044 | 0.39σ |

**P1 holds** — the level moved at ≥2σ, at the low end. **P2 agrees there** — the gain's step has the level's sign
and resolves at 3.57σ. **The falsifier does not fire.** And **the high end is the design's own null**: doubling the
noise moves the level by only **+0.0146 at 1.15σ**, which is not a movement this sample can call, so `noise = 2.0`
is not a level knob for this metric and the two-sided *shape* is not available from this design.

**So the account gets a one-sided confirmation, and the side it gets is the surprising one.** At noise 1.0 the
penalty beats `naive` by **+0.0354 at 4.27σ**; at noise 0.5 it beats it by **−0.0016, unresolved**. The same
method, λ, Fisher estimate, partition and architecture — and **the penalty has no advantage at all where the tasks
left less to forget.** The gain's step (−0.0370) is *larger than the whole effect it moves*.

## 2. The asymmetry is a measurement, not a failure

**`noise`'s effect on the level is asymmetric, and by a lot**: halving it cuts `naive`'s forgetting by **41%**
(0.0750 → 0.0438, 3.55σ), while doubling it raises it by **19%** (0.0750 → 0.0896, 1.15σ). The design therefore
has power where the level falls and none where it rises, and the null at the high end is a statement about the
*knob* rather than about the account:

> **over `noise ∈ [0.5, 2.0]` at this configuration, the level moves down by 0.0312 (3.55σ) and up by 0.0146
> (1.15σ)** — so the corpus now knows the knob's range in the direction that matters and knows that its upper end
> is flat.

`e167`'s second artifact also decided a readership cell it was not run for: **`noise` is `read` by `naive`** on
`e167`'s own two arms (`only noise`, n=40), and those two artifacts are **the corpus's first pair where both sides
carry `code_revision`** — the field's intended use, satisfied on a pair that differs in one config field.

**And the loop closes through `e166`.** That census named `noise` as one of the three knobs the corpus had never
varied in isolation on a pair carrying a naïve arm and a penalty arm; `e167` varied it, and the census row it
produced — the two `e167` arms against each other, differing in `noise` alone — is a **fourth level-moving field**
in the census and agrees with the account's direction like the other three. The census's own count of
level-moving rows goes from 13 to 14, and its `noise` field joins `classes`, `frozen_bias` and `readout_size`.

## 3. The confound, stated before the run and still standing

**`noise` is not a clean level knob, and its impurity is exactly what the room account needs held fixed.** The
Fisher is estimated at the **initial** parameters from minibatches of the training data — and `noise` changes the
data. So the stimulus noise may move the penalty's advantage by changing **how strong the penalty is**, not only
how much there is to forget. A monotone Fisher effect predicts the same signs at both ends; this design has
resolution at one end, so it neither confirms nor excludes it — and **the high end's null makes the Fisher
account's prediction there untestable too**.

~~**`--iters` is the knob with zero impurity**~~ — **that is FALSE, corrected the same night**: the Fisher and the
anchor are computed *after* each task's training (`experiments/e8_rate_network.py`, inside the task loop, at the
parameters the knob has moved), so `--iters` moves the penalty's *inputs* exactly as `noise` does. **And the
consequence is general: no single-field manipulation in this corpus can isolate the room**, because every knob
that moves the level also moves the parameters the Fisher and the anchor are measured at. `e173`'s 250-iteration
arm is that confound demonstrated from the other side — **the level flat at +0.0044 (0.55σ) while the advantage
falls −0.0214 (2.09σ)** — so the honest statement of this unit is: the room account's direction is confirmed at a
level knob that leaves the architecture, read-out, class structure and partition untouched, and the alternative
that the knob changed the penalty's inputs is **bounded, not excluded**
(`docs/findings/2026-09-25-the-fisher-is-measured-after-training-so-no-knob-is-clean.md`).
## 4. What this cannot settle

- **The Fisher confound of §3**, which `e173` exists to remove and which no `noise` design can.
- **The two-sided shape.** The high end is flat, so the tracking is demonstrated as a *fall* and not as a line —
  and a line is what would make it a function rather than two numbers with the same sign.
- **λ = 3e-4 is one penalty strength**, and one family (the base family's plastic arm), one read-out (32), three
  tasks, one seed stream. The wiring family's λ-insensitivity (`e162`) is a different regime and not re-tested.
- **`e171`'s reference is formed across two artifacts** (`e133`'s `naive` and `e141`'s λ = 3e-4 `ewc`), which is
  licensed by the readership table's `lam × naive = unread` at n=40 and is checked rather than assumed.
- **A null at 2.0 is a statement about 40 seeds**: 0.0146 at 1.15σ could be a real movement the sample cannot
  call, and rule 42's arithmetic — what the test would need — is not computed here.
