# The room account agrees with every resolved level move — and does not explain the gain

**Date:** 2026-09-24
**Script:** `experiments/e166_gain_tracks_room.py` — analysis only, no runs. Artifact:
`runs/e166_gain_tracks_room.json`.
**Design:** every pair of artifacts on disk that differs in **exactly one `config` field**, shares a penalty arm
and has the same replicate count, restricted to pairs carrying both a `naive` arm and a penalty arm — so replicate
*i* is seed *i* on both sides and both differences below are **paired**. 48 artifacts qualify, giving **48 pairs,
127 (pair, arm) rows over 11 fields**.

---

## 1. The question, and why it is a design and not a regression

`e165` closed the matched-λ family test and left one account standing beside the one it supports: the wiring
family's penalty gains **3.68σ** where the base family's loses **0.91σ** **either because the wiring family
tolerates a stronger penalty or because it has more forgetting to remove** — its `naive` sits at **0.1068**
against **0.0750** — and a level difference and a tolerance difference predict the same interaction. The
registration named the separating experiment: the naive level varied *within* a family, or a third family between
the two levels.

This unit asks what the corpus already says. For each single-field pair it reports two paired differences: the
**level step** (`naive`'s forgetting, second minus first — how much room moved) and the **gain step** (the
penalty's advantage over its own `naive`, second minus first). **The room account predicts these share a sign.**

## 2. The design's own negative control: a field that cannot move the room

`fisher_batches` is the most-varied field in the corpus and the cleanest control available, because `e160` derives
it as **unread by `naive`** — so it cannot change what there is to remove, only the penalty's Fisher estimate.
**78 rows**, and:

- the two `naive` arms are **bit-identical in 54 rows**;
- the **24 that differ are 6 pairs, and every one of them involves `e102_rate_fb8_omp1` or `..._omp4`**, with the
  same level step **+0.00625** — the thread difference, i.e. the environmental class `e163` measured, and
  **0 unexplained**;
- **not one of the 78 rows moves the level at ≥ 2σ** — a field that cannot move the room does not move it.

**And the gain moves anyway: by up to 0.0500 at n ≥ 5** (0.1250 if the single-seed pairs are included, whose
steps have no resolution at all by construction). The largest level-driven gain step in §3 is **0.0583 at the same
n = 5**. So **a manipulation that provably cannot change the room moves the penalty's advantage by as much as the
manipulation that does** — the gain is not a function of the level, and that is what bounds everything below.

## 3. Where the level did move, and which way the gain went

13 of 127 rows move the level at ≥ 2σ, over **3 fields**:

| field | pair | n | level step | resolution | gain steps, by arm | resolution |
|---|---|---|---|---|---|---|
| `classes` | `e100_rate_cs800_classes2` → `e101_rate_fb32` | 5 | **+0.0563** | **9.00σ** | `ewc` **+0.0583**, `ewc-block-rand` **+0.0333**, `ewc-block` +0.0208, `replay` +0.0188 | **2.85σ**, **2.36σ**, 0.99σ, 1.62σ |
| `frozen_bias` *(diagnostic)* | `e140_r32_methods_plastic` → `..._frozenbias` | 40 | **−0.0523** | **5.90σ** | `replay` **−0.0576**, `ewc` +0.0151, `ewc-block-rand` +0.0164, `ewc-block` −0.0013 | **6.15σ**, 1.76σ, 1.51σ, 0.14σ |
| `frozen_bias` *(diagnostic)* | `e135_r32_methods_plastic` → `..._frozenbias` | 5 | −0.0479 | 2.37σ | `replay` −0.0563, `ewc` −0.0167, `ewc-block-rand` −0.0146, `ewc-block` −0.0042 | **2.23σ**, 0.42σ, 0.48σ, 0.21σ |
| `readout_size` | `e155_r128_naive_replay` → `e155_r700_naive_replay` | 40 | −0.0148 | 2.18σ | `replay` **−0.0253** | **3.43σ** |

**Of the 13 rows, the gain resolves in the room account's direction 5 times and against it 0 times.** Two rows
resolve *against* the account in sign but not in magnitude — `ewc` under `frozen_bias` (+0.0151 at **1.76σ**) and
its block-rand control (+0.0164 at **1.51σ**) — and they are printed rather than dropped, because a table that
kept only its agreeing rows would be the failure mode rule 43 exists against.

**The strongest case is the largest level move**: four classes per task instead of two raises `naive`'s forgetting
by **0.0563 at 9.00σ**, and **all four arms' gains rise with it** — two of them resolved. That is the room
account's prediction, in its purest available form.

## 4. Why this still does not credit the account with `e165`'s interaction

- **The control in §2 is the disqualifier.** A field that cannot move the room moves the gain by 0.0500 at the
  same n, so a resolved gain step *co-occurring* with a resolved level step is not evidence that the level caused
  it — the field moved both, and the gain has a driver the level does not summarise.
- **8 of the 13 rows are `frozen_bias`**, and this project has closed that arm as a **diagnostic rather than a
  method** whose rankings are not practical advice: it freezes the one trained parameter no penalty covers.
- **The other two fields do not vary the level alone either**: `classes` 2 → 4 changes the *task structure* (the
  shared head's class ranges and offsets), and `readout_size` changes the *decoder* (128 → 700 neurons), where the
  penalty acts on the recurrent body. In both cases the level and the penalty's advantage can respond to different
  machinery, and the design cannot tell that from "more room, more gain".
- **The one clean row is the smallest**: the `classes` pair's `ewc` gain step, **+0.0583 at 2.85σ**, is the only
  level-driven gain step in the table that is both resolved and free of the epoch problem in the next bullet.
- **Epoch caveat, from `e163`**: both artifacts in the `classes` pair are from 09-23's unrecorded epoch. The
  *level* step (0.0563 at 9.00σ) is three times the epoch's largest movement (0.017) and safe; but the epoch moved
  `ewc-block`, `ewc-block-rand` and `replay` by up to 0.0396 **and those are exactly the three arms whose gain
  steps in that row are 0.0333, 0.0208 and 0.0188** — so of the four classes rows, only `ewc`'s is clean, and
  `ewc` is precisely the arm `e163`'s epoch did not touch.
- **The rank statistic is uninterpretable here, by rule 43.** ρ(level, gain) = **+0.274** over all 127 rows
  (leave-one-out **+0.257 to +0.297**) and **+0.120** over the 102 rows at n ≥ 5 (LOO **+0.096 to +0.145**), while
  only **13 rows resolve on the level, 8 on the gain, 5 on both**. The coefficient is stable and is a statistic
  over mostly-unresolved inputs; both facts are printed because the first alone would read as a result.

**So the account survives this census and is not established by it.** Its direction is right in every resolved
case, which is worth recording; and the census's own control says the effect it would be credited with is smaller
than what the gain does for reasons that have nothing to do with the room.

## 5. What would settle it, and the corpus does not have it (rule 42)

The separating design is a **level knob inside one family that touches neither the task structure nor the
decoder**, so that the level moves while everything the penalty acts on stays put. The fields this corpus has
varied in isolation, over artifacts carrying a naive and a penalty arm, are exactly: `fisher_batches` (78 rows),
`basis` (14), `methods` (8), `frozen_bias` (8), `lam` (4), `circuit_size` (4), `classes` (4), `replay_batch` (3),
`shared_head` (2), `replay_per_task` (1), `readout_size` (1). **`iters`, `train` and `noise` are not among them** —
a shorter training run, a smaller training set or a noisier stimulus would move the forgetting level with the
architecture and the task structure fixed, and each is one flag on the existing runner.

## 6. What this cannot settle

- **It cannot attribute any gain step to the level**, for the reasons in §4, and the two near-miss rows are
  unresolved rather than absent.
- **It cannot separate "more room" from "a different task"**: 12 of the 13 level-moving rows are manipulations of
  the task or of the read-out, not of difficulty at fixed structure.
- **The 127 rows are not 127 independent observations**: the 48 pairs come from 48 artifacts, several of which
  appear in many pairs (the `--fisher-batches {8,32,128}` family alone gives 21 pairs), so the effective sample on
  the level axis is **3 fields and 5 rows**, as §3 counts.
- **The single-seed pairs (9 of 78 control rows, and `e96`'s three) can move the gain by 0.1250** with no
  resolution at all; they are reported as steps and never as findings, which is why the n ≥ 5 column is printed
  beside every maximum above.
