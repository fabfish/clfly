# `e104`: the unbacked cells, measured — the frozen-body control mostly **confirms** its claim

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, eight runs; artifacts `runs/e104_frozen_{whole,r128,r32}_{plastic,frozen}.json`
and `runs/e104_{taskil,classil}_naive_ewc.json`.
**Artifacts:** the eight above.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25; frozen sweep at
`--readout-size 0/128/32 --input-overlap 0.0 --noise 1.0 --shared-head --frozen-body`, `--methods naive`; EWC
fills at `--readout-size 0` and `--methods naive,ewc` with λ = 0.003 and 8 Fisher batches, `--shared-head` for
class-IL. Every artifact now records its `environment` (rule 21) — `torch_num_threads: 20`, `OMP_NUM_THREADS`
unset, for all eight.
**Context:** `docs/findings/2026-09-23-the-frozen-body-control-is-in-no-artifact.md`, which measured that the
paper's §4.2 plastic-minus-frozen series and §4.4's two EWC cells match no artifact, and named this as the
cheapest available repair.

---

## 1. The frozen-body control, measured for the first time

| read-out | plastic | frozen | **gap** | claimed gap |
|---|---|---|---|---|
| **0** (whole, 1307) | 0.9333 ± 0.0204, f **+0.0479 ± 0.0343** | **0.9444 ± 0.0000**, f **+0.0000 ± 0.0000** | **−0.0111** | +0.007 |
| **128** | 0.9333 ± 0.0068, f **+0.0333 ± 0.0125** | **0.9167 ± 0.0022**, f **+0.0000 ± 0.0000** | **+0.0167** | +0.009 |
| **32** | 0.9139 ± 0.0131, f **+0.0729 ± 0.0151** | **0.8139 ± 0.0034**, f **+0.0000 ± 0.0000** | **+0.1000** | +0.102 |

**And the claim it was said to support is confirmed in almost every particular.** Three things, in order of how
much they matter:

- **The frozen accuracies reproduce to three decimals**: measured **0.9444 / 0.9167 / 0.8139** against the
  claim's **0.944 / 0.917 / 0.815**. Three independent quantities, none of which had an artifact, all landing
  where they were printed. **The unbacked series was right**, and this is worth saying as plainly as the
  phantom cells are worth condemning — the difference between them is not care, it is that one was re-measured
  and the other was not.
- **The gap grows monotonically as the read-out narrows** — measured −0.0111 → +0.0167 → +0.1000 — which is the
  paper's design principle, now measured rather than asserted. **Its end point has the wrong sign in the
  claim**: at the whole state the frozen body is `+0.0111` accuracy *better* than the plastic one, where the
  claim printed `+0.007` for plastic. That is small and unresolved, and it is on the side that *strengthens*
  the principle: if a frozen body is at least as good as a trained one, the benchmark contains no
  continual-learning problem there, which is exactly the sentence the series was written to license.
- **Freezing the body drives forgetting to exactly zero with zero variance** — `+0.0000 ± 0.0000` at all three
  read-outs, five replicates each. The claim printed `+0.000`; the measurement is that all fifteen replicates
  agree to the last digit, so this is not a small number but a structural one.

**And one half of the claim is refuted.** The *plastic* forgetting series was printed as monotone,
**+0.021 → +0.035 → +0.066** as the read-out narrows from 1307 to 128 to 32. Measured: **+0.0479 → +0.0333 →
+0.0729**. The 1307 → 128 step **falls** (0.0479 → 0.0333) rather than rising, so of the two relationships the
section printed, one is measured and monotone (the accuracy gap), and the other is **not monotone at the
coarser step** — a 0.0146 fall against sems of 0.0343 and 0.0125, so unresolved, but the level at read-out 128
is *below* the whole-state level, which a strictly increasing series cannot be.

**And the sweep's configuration is validated by its own control.** The read-out-32 plastic row is the hardened
configuration's `naive`, and it comes out at **+0.0729 ± 0.0151 at 0.9139 ± 0.0131** — reproducing
`e8_hardened_basis` and the seven runs that agree with it, to the last printed digit. So the sweep was run on
the same benchmark the rest of the network line uses, which is a claim the sweep could not previously make
because it had left no artifacts at all.

## 2. The two EWC cells, and both are ties

| setting | run | `naive` | EWC, diagonal | within-run contrast |
|---|---|---|---|---|
| task-IL (per-task heads) | `e104` (`naive,ewc`) | +0.1062 ± 0.0299 | **+0.1062 ± 0.0372** | **+0.0000 ± 0.0477 (0.00σ)** |
| class-IL (shared head, whole state) | `e104` (`naive,ewc`) | +0.0437 ± 0.0182 | **+0.0479 ± 0.0117** | **+0.0042 ± 0.0216 (0.19σ)** |

**Both cells now exist and both say the diagonal does nothing**, which is what the paper's §4.4 concluded from
numbers that were in no artifact — so the conclusion is **confirmed** and one of its numbers is **corrected**:
the task-IL row claimed EWC was *worse* than `naive` (+0.128 against +0.101, "+0.027"), and the measured
within-run contrast is **+0.0000**, a dead tie. The class-IL row claimed "+0.004 (tie)" and the measurement is
**+0.0042** — to the precision printed.

**And the task-IL `naive` cell is the third instance of the process-dependence this session has been about.**
The pair of runs behind that setting's two rows do not share a `naive`:

| setting | `e104` (`naive,ewc`) | `e84` (`naive,replay`) | the paper printed |
|---|---|---|---|
| task-IL | +0.1062 at 0.8319 | +0.1000 at 0.8417 | +0.101 ± 0.049 |
| class-IL | **+0.0437 at 0.9361** | +0.0688 at 0.9194 | +0.059 ± 0.028 |

So each setting's `naive` takes **two values in two processes**, and the paper printed a **third** that matches
neither artifact. For class-IL the pair is worth naming: `e104`'s `naive` is **exactly** the stored
`e8_class_incremental.json` value (+0.0437 / 0.9361), so that run re-landed in the configuration's original
environment, while `e84`'s is half a sem away in a different one. **Three executions of one configuration have
produced three `naive` values, two of which have artifacts, and only one of which is in the paper.**

**Which means the honest table is one row per run, and that is the change this fire makes to §4.4.** A table
that prints one `naive` and two contrasts computed in two different processes is the §4.2 defect in a new
place, so the paper's table now carries the run beside each row and leaves a cell empty where that run did not
measure it — the same rule the last fire applied to the EWC column, applied now to the `naive` column.

## 3. What this does to the two findings that sent it

- **`the-frozen-body-control-is-in-no-artifact` is repaired rather than confirmed or overturned.** Its
  measurement was that the control was absent, and it remains true of the *record before this fire*; the
  paper's §4.2 can now carry its series with artifacts, and the repair cost **eight runs of a few minutes
  each**, which is the number that finding predicted ("the cheapest repair available in this project and the
  reason it should be run rather than argued about").
- **`the-frozen-body-control-is-in-no-artifact` §5 said "no replacement is proposed for the seven unbacked
  cells, and filling them is a new experiment"** — six of those seven are now filled: three frozen rows, three
  plastic rows, and the two EWC cells, with only §4.4's `naive` cells left as two-runs-one-column, which is a
  presentation problem rather than a missing measurement.
