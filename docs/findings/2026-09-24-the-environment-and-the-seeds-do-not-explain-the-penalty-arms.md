# What the record *can* say about the penalty arms' run-to-run difference: the environment and the seeds are not it

**Date:** 2026-09-24
**Script:** none — a read of the runner's seeding path and of the recorded environments behind `e144` and `e153`,
prompted by `e153`'s failed C0a control. It exists because the difference is large enough to matter to the paper's
method tables, and the cheapest progress is to rule out the two explanations the artifacts can rule out.
**Artifacts:** `runs/e144_r32_overlap1_methods_40reps.json`, `runs/e148_r32_overlap1_replay.json`,
`runs/e153_r32_overlap1_methods_40reps.json`, `runs/e140_r32_methods_{plastic,frozenbias}_40reps.json`,
`runs/e77_thread_determinism_probe.json`.

---

## 1. The environment is identical in every recorded field

| field | `e144` | `e148` | `e153` | `e140` plastic | `e140` frozen |
|---|---|---|---|---|---|
| `torch_num_threads` / `interop` | 20 / 20 | 20 / 20 | 20 / 20 | 20 / 20 | 20 / 20 |
| `python` / `torch` / `platform` | 3.12.14 / 2.14.0+cpu / Windows-11 | same | same | same | same |
| `omp_num_threads` / `mkl_num_threads` | unset | unset | unset | unset | unset |
| `calibration_matmul_s` | **absent** | 0.000359 | **0.000309** | **absent** | 0.000135 |

**Every recorded environmental field agrees**, and the only one that differs is a *timing* — which the two
`e140` arms bracket (0.000135 and 0.000309) while reproducing their `naive` rows exactly. So **the environment as
the artifacts record it does not explain the penalty arms**, and the field's absence from `e144` is itself
informative: it dates that process to before the probe existed, consistent with its missing `partition_seed`.

**And `e77` — the thread-determinism probe — already measured that this line is not environment-invariant**: the
same command at four threads gives different per-replicate accuracies ([0.8264, 0.8403, 0.9306]) from its default
([0.875, 0.9028, 0.9097]), with `threads_inert: false` and `repeats_inert: true`. **So "run-to-run equal" is not
a property this line was ever measured to have in general**; what is new in `e153` is that two executions *at the
same recorded settings* differ, and only on the arms that build a Fisher.

## 2. The seeding path, as read

- `torch.manual_seed(seed)` seeds the training of every replicate (line 501).
- the diagonal and block Fishers are both called with **`seed = seed + k`** (lines 585, 613), and the replay
  indices are drawn from `np.random.default_rng(seed + k)` (line 620).

**So every path in this runner is nominally seeded**, which is exactly why `naive`'s and `replay`'s bit-identity
is the expected outcome rather than a surprise — and why the three Fisher arms' divergence is **not explained by
the code as read**. Two mechanisms remain, and the artifacts cannot separate them:

1. **a nondeterministic accumulation inside the Fisher helpers** — a parallel reduction whose order varies with
   thread scheduling gives a 1e-15-scale difference in the Fisher, and the penalty multiplies it into every one of
   the 500 steps, which is the amplification rule 3 measured on the linear line ("a **1e-15** relative parameter
   change moves the ratio metric by **±0.04**"); or
2. **an unseeded draw inside one of the two helper functions**, which would make the Fisher estimate itself
   different rather than perturbed.

**Both are one code read away**, and neither is settled by the artifacts. What *is* settled is that the effect is
arm-selective (three arms of five, and the three that compute a Fisher), configuration-selective (the base family
at five replicates reproduced all five arms), and large enough to matter (up to 0.229 per replicate).

## 3. Why this matters to what the paper prints

**The measured between-run movement on those arms' means is 0.0068, 0.0201 and 0.0112**, and the paired sems of
§4.2's method-table contrasts are about 0.007 to 0.010 — **so if the difference repeats, it is the same size as
the contrasts the table reports**, and the table's rows would need a run-to-run term beside their seed term.
`e159` (the third execution, running) decides whether it repeats, and this note is what makes its reading
two-valued rather than four: **if `e159` matches `e153`, the mechanism is runner-side and rare (two of three
executions agree); if it matches neither, it is a distribution and its spread is what the table needs.**

## 4. What this cannot settle

- **Two helper functions were not read line by line**: `diagonal_fisher` and `block_fisher` are where the
  mechanism is, and this note stops at their call sites because the *empirical* question (does it repeat) is
  already running.
- **`e77`'s thread probe is a different configuration** (`cs = 300`, 100 iterations, `naive` only), so it
  establishes that the line is environment-sensitive *somewhere*, not that the fb32 wiring-family penalty arms are.
- And **the environment is only what the runner records**: thread counts and a calibration timing, not the
  scheduler's behaviour, not the BLAS library's kernel choice at a given moment, and not the machine's load —
  which is the honest limit of "the recorded environment is identical".
