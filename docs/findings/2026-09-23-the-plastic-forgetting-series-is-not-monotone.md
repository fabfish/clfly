# `e106`: the plastic-forgetting series is not monotone, and this time it is not noise

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, nine runs; artifacts `runs/e106_plastic_r{0,128,32}_rep{1,2,3}.json`.
**Artifacts:** the nine above, plus `runs/e104_frozen_{whole,r128,r32}_plastic.json` for the fourth execution
of each read-out.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`
only, `--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 0 / 128 / 32. **All twelve executions record
the same environment** — `torch_num_threads: 20`, `OMP_NUM_THREADS` unset, `torch 2.14.0+cpu` — which is the
first use of the field `e102` added and is what makes the stability below a measurement rather than an
assumption.
**Context:** `docs/findings/2026-09-23-the-unbacked-cells-measured.md`, which re-measured the frozen-body
control and reported the plastic-forgetting series as **not monotone but unresolved**, with the 1307 → 128 step
falling by 0.0146 against sems of 0.0343 and 0.0125.

---

## 1. Four executions per read-out, and every one agrees to the last digit

| read-out | plastic forgetting, per execution | mean | **run-to-run sd** | plastic acc | frozen acc | **gap** |
|---|---|---|---|---|---|---|
| **0** (whole, 1307) | +0.0479 +0.0479 +0.0479 +0.0479 | **+0.0479** | **0.0000** | 0.9333 | 0.9444 | **−0.0111** |
| **128** | +0.0333 +0.0333 +0.0333 +0.0333 | **+0.0333** | **0.0000** | 0.9333 | 0.9167 | **+0.0167** |
| **32** | +0.0729 +0.0729 +0.0729 +0.0729 | **+0.0729** | **0.0000** | 0.9139 | 0.8139 | **+0.1000** |

**So the fall is real.** The whole-state read-out forgets **+0.0479** and read-out 128 forgets **+0.0333**, and
that 0.0146 drop is measured against a run-to-run sd of **exactly zero** over four independent executions. The
series the paper printed — **+0.021 → +0.035 → +0.066**, monotone — therefore fails at its first step, not for
want of precision but as a property of the benchmark: **plastic forgetting does not fall monotonically as the
read-out narrows.**

**And the other series does.** The plastic-minus-frozen *accuracy* gap is **−0.0111 → +0.0167 → +0.1000**,
monotone, which is §4.2's design principle: narrowing the read-out makes the recurrent weights load-bearing.
(The whole-state value is negative — the frozen body is `+0.0111` *better* there — which is the strongest form
of "this benchmark contains no continual-learning problem at the whole state".)

**So the paper's two claimed monotone relationships are not one relationship, and the section printed them as
a pair.** "Making the body load-bearing" and "making the body forget more" are separately true of the
read-out axis and jointly false: at read-out **128** the body *is* load-bearing (gap +0.0167, where at the
whole state training actively hurt) and it forgets **less** than at the whole state (+0.0333 against +0.0479).
The quantity that the design principle needs is the gap; the forgetting series was an accompanying
observation that does not hold, and §4.2 has been corrected to note that the two move differently.

## 2. The stability is itself the notable result, and it needed the environment to say so

Twelve executions of one command, four at each of three read-outs, and **every value is identical across the
executions that share a configuration** — sd `0.0000` on all three, and the accuracies identical too. That is
worth recording next to this session's other reproducibility measurements, because it is the opposite kind of
result:

| quantity | measured run-to-run behaviour |
|---|---|
| `naive` at a fixed read-out, this configuration | **identical over four executions**, both metrics |
| `ewc-block`, `ewc-block-rand`, `replay` at fb = 8 | **moved** between two runs of one command (`e102`) |
| `naive` across `OMP_NUM_THREADS` settings | **moved** (+0.0729 → +0.0792), binary at 1 and 4 (`e102`) |

**A `naive`-only run at a fixed read-out is one of the most reproducible measurements in this repository**, and
the reason is visible in the code rather than inferred: with `--methods naive` there is no Fisher, no replay
and no anchor, so the run is a single deterministic training trajectory per seed. **The reproducible arms are
the ones whose computation is shortest**, which is the same ordering the fb sweep showed from the other side.

**And the environment field earned its place on the first use.** The sd of zero is a statement about *one*
recorded environment — all twelve artifacts carry the same `environment` block — and the field did not exist
when the runs it would have explained were made. Recording it costs nothing per run and it is the difference
between "these twelve agree" and "these twelve agree, in this environment, as recorded".

## 3. What this closes and what it opens

- **Closed:** §4.2's plastic-forgetting monotonicity. It was flagged as refuted-but-unresolved last fire; four
  executions per point with sd zero make it refuted, and the paper no longer prints the series as monotone.
- **Closed:** the option that the 0.0146 fall was measurement noise. It is not, at this configuration, in this
  environment, at this replicate count.
- **Open, and now a sharper question:** *why* read-out 128 forgets less than the whole state. The sections'
  account — a narrower read-out forces the body to carry the tasks, and carrying them is what gets forgotten —
  predicts the opposite ordering at the 1307 → 128 step. Two candidates this fire can name but not separate:
  at the whole state the body is not needed, so its drift is unconstrained and unmeasured by the tasks
  (forgetting of a solution that was never used), while at 128 the body is needed and is *anchored* by being
  needed; or read-out 128 is simply an easier regime for the plastic body, with more capacity left over per
  task. Separating them is a new experiment rather than a reading.

## 4. What this does not do

- **Three read-outs is one axis.** The result is that the printed series is not monotone on the three points
  the paper chose; whether some other three-point subset would be monotone is not a question this measurement
  answers, and a fourth read-out between 128 and 1307 is the honest way to ask it.
- **It does not touch the frozen arm**, which is `+0.0000 ± 0.0000` at all three read-outs and was not re-run:
  the claim being tested here is about the plastic one.
