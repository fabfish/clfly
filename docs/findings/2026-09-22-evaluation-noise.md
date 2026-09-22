# E20 — the rate-network benchmark reports a paired comparison as unpaired, and 44% of its noise floor is its own test set

**Date:** 2026-09-22
**Script:** `clfly/bench/control.py` (`paired_contrast`, `evaluation_noise`), `experiments/e8_rate_network.py`
**Artifacts:** `runs/e10_rung_side.json` (re-analysed), `runs/e20b_noisefloor_check.json` (block validated)

---

## 1. Two reporting gaps, both load-bearing

`e8_rate_network` never printed the comparison the whole network line is about. The
biological-versus-matched-random contrast was computed **by hand in the findings** and, when it was
computed, **unpaired** — even though the two arms share a seed sequence, so their replicates are
matched observations and the paired sem is the right one.

That matters because the binding constraint on `C2b` turned out to be variance, not the effect
(`docs/findings/2026-09-22-e10-side-rung-underpowered.md`): a 0.01-accuracy effect would need 94
repeats, i.e. 55 hours per rung. A benchmark that reports the wrong sem, and prints no detection
floor, makes a null look like a measurement of zero.

**Both are now in the experiment.** Two functions carry the logic, so they are testable and shared
rather than ad hoc:

- `paired_contrast(a, b)` — delta, unpaired and paired sems, the replicate sd, and the detection
  floor (`min_detectable`, `repeats_for_0.01`, `repeats_for_0.03`);
- `evaluation_noise(accuracy, n_eval)` — the binomial se of an accuracy measured on ``n_eval``
  held-out decisions.

## 2. The paired figure, on the numbers that motivated it

From `runs/e10_rung_side.json` (`side`, 3 repeats):

| comparison | unpaired sem | **paired sem** | improvement |
|---|---|---|---|
| final accuracy | 0.0406 | **0.0267** | 1.5× |
| mean forgetting | 0.0673 | **0.0409** | 1.6× |

Per-repeat accuracy deltas are +0.0278, −0.0625, −0.0000 — mixed in sign and large, the signature of
dominant run-to-run variance. This is the same lesson as the neuron ladder
(`2026-09-22-shape-needs-paired-contrasts.md`), reached independently in a second substrate.

## 3. And 44% of that variance is the test set

`final_accuracy` averages one evaluation per task over `len(y_test)` held-out samples each — three
tasks × 48 = **144 decisions** — so it carries a binomial se. At an accuracy near 0.82 that is
**0.032**. The measured per-replicate spread is 0.048 (pooled over the two arms). Decomposing:

| arm | per-replicate sd | evaluation se | **share of the variance that is the test set** | residual (training) sd |
|---|---|---|---|---|
| `ewc-block` (biological) | 0.0599 | 0.0324 | **29%** | 0.0504 |
| `ewc-block-rand` (control) | 0.0367 | 0.0316 | **74%** | 0.0188 |
| pooled | 0.0483 | 0.0320 | **44%** | 0.0362 |

**For the control arm, three quarters of the observed run-to-run variance is finite-test-set noise.**
And enlarging the test set costs almost nothing next to training.

The right way to state the saving is in **repeats**, and it needs the per-replicate sd of a
*difference* — not the mean of the two arms' sds, which is not a valid pooled sd for a difference of
means and is the error corrected in §7 below:

| design | per-replicate sd of the difference | repeats for 0.01 accuracy at 2σ |
|---|---|---|
| unpaired | 0.0702 | **198** |
| **paired** (as the comparison actually is) | 0.0463 | **86** |
| paired, with the evaluation component removed | 0.0411 | **68** |

So **pairing is worth 2.3× in repeats** (198 → 86) — the 1.5× figure is the sem improvement at fixed
n, and the requirement scales as its square. Removing the evaluation noise on top of that gives
86 → 68, a further 1.26×, i.e. 55 hours down to ~43 per rung. **That is the cheapest available lever
by a wide margin, and it was invisible before this decomposition.** Neither lever makes the
experiment feasible; together they make it 2.9× cheaper.

Two further readings, both flagged as suggestive rather than established:

- **The two arms have different variance structure.** The biological arm's residual training sd is
  0.0504 against the control's 0.0188 — a factor of 2.7 — so the *control* is close to
  evaluation-limited while the *biological* arm is not. With 3 replicates an sd is barely estimated,
  so this is a hint about where to look rather than a result.
- **The decomposition is what makes a null interpretable at all.** "No advantage at `side`"
  previously came with a 95% interval of ±0.08 accuracy. Saying *why* that interval is that wide —
  44% of it is the benchmark's own test set — is the difference between a benchmark limitation and a
  scientific null.

## 4. What the experiment now prints

```
  --- noise floor (n_eval = 144 held-out decisions per replicate) ---
    ewc-block-rand   per-replicate sd 0.0367  of which evaluation 0.0316 (74% of the variance,
                     and removable); training 0.0188

  --- matched pair: biological partition vs its size-matched random control ---
    final_accuracy     delta -0.0116  unpaired 0.0406 (0.29 sigma)  paired 0.0267 (0.43 sigma)
                       this run detects effects above 0.053; 0.03 would need 10 repeats and 0.01 86
```

(The values are the real ones from `runs/e10_rung_side.json`, reproduced by the committed code.)
Both blocks are stored in the JSON (`evaluation_noise`, `matched_pair`), so the numbers are in the
artifact rather than only in a log.

**One honest edge case the code handles rather than hides.** If the replicate spread comes out *at or
below* the binomial floor, the variance fraction exceeds 100%. That is a signal — the replicates are
nearly identical (a very short run) or the 144 held-out decisions are not independent, which the
binomial model assumes — so the report says exactly that instead of printing "130% of the variance".
Observed in the validation run (`--iters 2`, `runs/e20b_noisefloor_check.json`).

## 5. The verification that has not been done

The claim "enlarging `--test` recovers 1.8× fewer repeats" is **arithmetic from a binomial model, not
a measurement**. It is falsifiable in one run: `--test 480 --repeats 6` should drop the per-replicate
sd from ≈0.048 toward ≈0.036, and it costs about half an hour rather than the 55 hours of repeats it
would otherwise be buying. **That is the next thing to run, and it should be run before any more
repeats are bought** — a cheap test of whether the expensive plan is necessary is exactly the
`budget a question before buying it` rule applied one step earlier.

## 6. Limits

- The binomial se assumes the held-out decisions are independent; they share a task, a stimulus
  distribution and a model, so 0.032 is a **lower** bound on the evaluation contribution. A higher
  true floor would make the "removable" share larger, not smaller — the direction is safe.
- The decomposition rests on **3 replicates** per arm, so each variance is itself uncertain by ~50%.
  The pooled 44% is better determined than either arm's figure.
- `mean_forgetting` has no analogous closed form (it is a difference of accuracies, so it would be
  roughly √2 times the accuracy se if the two evaluations were independent, which they are not), so
  only the accuracy decomposition is reported.
- The **noise-floor** block is validated end to end (`runs/e20b_noisefloor_check.json`, `--iters 2`,
  where it also exercised the above-100% branch). The **matched-pair** block is validated at
  `runs/e20_matchedpair_check.json` (`--iters 20`, 3 repeats): it printed both rows and stored both
  in the JSON, and it produced a useful illustration of the pairing argument — the two arms
  correlate at **r = 0.899**, so the paired sem is 0.0221 against an unpaired 0.0528 (**2.4×**),
  turning 1.62σ into 3.88σ. **That run's deltas are not results**: at `--iters 20` the model is
  barely trained (accuracy 0.63 against 0.72), so the sign and size of its reported difference are
  artefacts of an undertrained network. Only the mechanics are being checked here.

## 7. A figure I published an hour earlier was wrong, and this is the correction

The `e10` finding contains a power table whose "repeats needed" column was computed from
**0.0483** — the *mean* of the two arms' per-replicate sds. That is not a valid pooled sd for a
difference of means, and it is neither of the two quantities that matter:

| quantity | correct value | what I used |
|---|---|---|
| sd of the difference, **unpaired** | `hypot(0.0599, 0.0367)` = **0.0702** | 0.0483 |
| sd of the difference, **paired** | `sqrt(a² + b² − 2 r a b)` with r = 0.636 = **0.0463** | 0.0483 |

So the published figure of **94 repeats** for a 0.01-accuracy effect is wrong in both directions: the
unpaired design needs **198** and the paired one **86**. The `e10` finding's table has been corrected
in place, and the error is worth naming because it is the third time in this line of work that a
*fixed, single* number was carried where the *design* determines which combination is right:

- the shape work used the unpaired formula for matched rungs (`2026-09-22-shape-needs-paired-contrasts.md`);
- the ladder work used a single control draw where the population was meant (`…control-drawn-once.md`);
- and here a mean of sds stood in for the sd of a difference.

Each was a shortcut that happened to be defensible-looking. The pattern is that **an error bar is a
property of the design, not of the measurements**, so it cannot be summarised as one number and
reused across designs.

The correction does not change the conclusion — every version of the number says the experiment is
54–200 repeats away from a 0.01 effect — but it changes the *recommendation*: pairing (which the
comparison already has) is worth 2.3×, more than the test-set fix, whereas the published table
implied pairing was nearly free of consequence.
