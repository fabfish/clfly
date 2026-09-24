# `e155`, pre-registered: does the floor model survive a read-out axis?

**Date:** 2026-09-24
**Design:** `--readout-size {128, 700} --methods naive,replay --repeats 40` with the C2b suite's settings
unchanged (`--circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --train 96 --test 48 --noise 1.0 --classes 4
--support 80 --shared-head --input-overlap 0.0 --fisher-batches 32 --seed0 0 --replay-per-task 96 --replay-batch
8`), writing `runs/e155_r128_naive_replay.json` and `runs/e155_r700_naive_replay.json`.
**Status: launched**, on the slot the queue had free.

---

## 1. What is being tested, and why it is not the same question as last time

`e148`'s finding proposed that **`replay`'s margin over `naive` is simply the baseline's forgetting** — because
replay drives its own forgetting to ≈ 0, whatever the baseline had to forget is what the margin is. It fits four
configurations with no free parameter:

| configuration | baseline's forgetting | replay's margin | ratio |
|---|---|---|---|
| base family, channel free | +0.0750 | −0.0784 | 1.045 |
| shared-input family | +0.1068 | −0.0984 | 0.921 |
| base family, channel frozen in every arm (`e135`, 5 reps) | +0.0250 | −0.0292 | 1.17 |
| base family, channel frozen in every arm (`e140`, 40 reps) | +0.0227 | −0.0208 | **0.918** |

**The fourth row is the model's only out-of-sample test so far**, and it passed because the model had been
written before that arm landed. **This run varies a different thing: the read-out**, where the baseline's
forgetting is already measured at five levels (`e116`, forty replicates each) — **+0.0750 at 32, +0.0370 at 128,
+0.0221 at 700, +0.0219 at 900, +0.0357 at 1307** — so the model predicts **−0.0370 and −0.0221** for the two arms
here, and the *lower* one is below every baseline level the model has been tested at except the frozen arms.

## 2. The predictions, and what this design can and cannot separate

- **P1 — the model generalises across the read-out.** Each arm's margin is within **2σ** of its own baseline's
  forgetting: **−0.0370 ± 0.0051** at read-out 128 and **−0.0221 ± 0.0047** at 700 (the sems are `e116`'s, and
  they are the right ones because the margin and the baseline use the same forty seeds). A paired sem of about
  **0.004** puts the 2σ window at about **±0.008**.
- **Falsifier.** Either margin is more than 2σ from its prediction. The stronger form, registered because it is
  the one that would matter: **the margin is proportional to the *frozen/covered* part of the baseline's
  forgetting rather than to the whole of it** — the channel-share reading `e135` motivated, which at read-out 128
  gives **−0.89 × 0.0370 = −0.0329** if the offsets carry the 89% that `e134` measured at that read-out.
- **And the honest statement of what this design *cannot* separate, which rule 41 now requires before the run**:
  at read-out 128 those two predictions are **0.0041 apart**, inside each other's 2σ windows, so **that arm
  tests generalisation and not discrimination**. At read-out 700 the share is unmeasured; if it is near 60% the
  channel reading predicts **−0.0133** against the model's **−0.0221**, i.e. **0.0088 apart ≈ 2.2σ** — so **the 700
  arm is the one that could separate them**, and the 128 arm is the one that would catch the model being wrong
  outright.

## 3. The controls

- **C0 — a reproduction test on two configurations.** `naive` at these two read-outs has already been run at forty
  replicates (`runs/e116_r128_40reps.json`, `runs/e116_r700_40reps.json`, same `seed0`, same suite), so **both new
  `naive` rows must be per-replicate identical to `e116`'s**, worst absolute difference 0.000 — and §9 of the paper
  says why the criterion is per-replicate identity and never an aggregate agreement. A failure here is a finding
  about the configuration's reproducibility, and it would also take `e116`'s five baselines with it.
- **C1 — the floor's own premise.** replay's forgetting must be near zero (the model's mechanism), and if it is
  *not* near zero at these read-outs then the model does not apply and the margin's value is uninformative about
  it. Registered as an instrument check rather than as a prediction.
- **And the arm this run does not have**: it does not run the frozen-bias diagnostics at these read-outs, so it
  cannot say what the offsets carry there — the share it would need to compute the channel reading's prediction at
  700 is the one number this design leaves to inference rather than measurement.

## 4. What this cannot settle however it lands

- One circuit, three tasks, one task order, one `replay-per-task`/`replay-batch` setting; the read-out axis is
  already known to move the *plastic-minus-frozen* gap and the metric's noise, so a margin that tracks the
  baseline here is a statement about this axis on this benchmark.
- **Two arms is not a ladder**: it adds points at 0.0370 and 0.0221 to four existing ones, and a *line* through
  them is still an empirical regularity with a ratio near 1 rather than a law — the mechanism (a method at zero
  forgetting cannot gain more than the baseline had) predicts the *form*, not the ratio's exact value.
- And it cannot separate the model from the channel reading at read-out 128 at all, which is registered above.
