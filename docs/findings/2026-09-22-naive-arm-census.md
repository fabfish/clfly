# E54 — the `naive` arm as a free instrument, and a census of which artifacts compute the same thing

**Date:** 2026-09-22
**Script:** `experiments/e54_naive_seed_pool.py`
**Artifacts:** `runs/e54_naive_seed_pool.json`
**Context:** `2026-09-22-network-variance-is-learner-variability.md` (`e38`), plan rules 8 and 17

---

## 1. Why the `naive` arm is the right instrument, and how far that goes

`e38` found two things about the network benchmark that together make the *number of seeds* its
binding constraint: the per-replicate spread is **learner seed-to-seed variability** rather than
measurement noise, and the **`naive` arm is bit-identical across runs**, which makes it a free
determinism control and a free way to accumulate seeds.

The second claim was **too broad as stated**. `naive` carries no penalty and no basis, so it is
independent of `basis`, `lam`, `fisher_batches`, `methods` and `repeats` — and of nothing else. It
still depends on `iters`, `lr`, `batch`, `train`, `test`, `classes`, `noise`, `support`,
`shared_head`, `input_overlap`, `readout_size` and `circuit_size`.

The first version of this script keyed runs on the fields that *ought* to matter and found **seeds 0–2
carrying two different values inside one group** — which is exactly what a wrong key looks like, and
it would have averaged two different computations into one larger-looking sample. So the census below
establishes agreement **from the data**: runs are clustered by agreeing bit-for-bit on every seed they
share, and a run that disagrees on any shared seed is kept out rather than merged in.

## 2. The census: six distinct `naive` computations across fifteen runs

| cluster | runs | seeds | n | what differs from the reference |
|---|---|---|---|---|
| **0** | **9** | **0–8** | **9** | — |
| 1 | 2 (`e8_hardened` ×2) | 0–4 | 5 | `shared_head=True`, `readout_size=32`, `input_overlap` |
| 2 | 1 (`e15_artifact_check`) | 0 | 1 | `iters=2` |
| 3 | 1 (`e20b_noisefloor_check`) | 0–2 | 3 | `iters=40` |
| 4 | 1 (`e8_class_incremental`) | 0–4 | 5 | `support`, `classes`, `noise`, `shared_head`, `readout_size` |
| 5 | 1 (`e8_rate`) | 0–2 | 3 | `support`, `classes`, `noise`, `readout_size`, `shared_head` |

**Every difference is explained by a field that genuinely changes the computation.** An earlier draft
of this section read `e8_rate`'s missing `basis` field as a marker for predating the
`torch.manual_seed` fix the script documents — the field list refutes that, because `e8_rate` differs
in five affecting fields anyway. **There is no evidence here of a stale or pre-fix artifact**; the
census is a statement about which runs compute the same thing and nothing more.

And the pool **cannot be grown from the artifacts**: nine seeds is the most that exist for one
computation. `e46` is running with 16 replicates and its `naive` arm is complete in the log, so n = 16
needs only that artifact to land — `e54` will pick it up with no change.

## 3. The learner-variability estimate, reproduced at n = 9

| quantity | value |
|---|---|
| n | 9 |
| mean accuracy | 0.8395 |
| seed-to-seed sd | **0.0389** (95% CI [0.0263, 0.0745]) |
| binomial floor at `n_eval` = 144 | 0.0306, i.e. **62% of the variance** |
| seed component | at most **0.0679**; at least **38% of the spread is learner variability** |

This reproduces `e38`'s n = 9 numbers exactly (sd 0.0389, floor 0.0306, 62% share), from a different
construction — `e38` read `e8_tuned_lambda` alone while this pools every artifact that agrees with it.
That agreement is a useful check that the pooling adds no error, and it also confirms that the nine
seeds really are one computation spread across nine files.

**What the number means for the C2b programme is unchanged and worth restating plainly: 38% of the
benchmark's per-replicate spread is the learner, not the measurement, so `--test 480` cannot remove
it** (`e38` bounded that lever at 1.28×) and the only way through is more seeds. At 0.0389 per
replicate and a 0.03 target, that is the 12–16 replicates `e46` is buying.

## 4. Two mistakes in my own first version

- **The assumed config key.** Described in §1: it silently merged `e8_rate` with the `e10` rungs.
  Caught because the merged group showed a seed carrying two values — the diagnostics in the script
  now print any within-seed disagreement *before* reporting statistics, and the real data has none.
- **Clustering merged runs with disjoint seed sets.** An empty intersection makes `all(...)`
  vacuously true, so a run starting at a different `seed0` would have joined any cluster. It does not
  bite in the artifacts (every run starts at 0), but it is a latent bug that a test now pins: a
  cluster requires **at least one genuinely shared seed** with agreement.

## 5. Limits

- **Nine seeds, one configuration.** The estimate is for cs = 800, `iters` = 500, `train`/`test` =
  96/48, `support` = 80, `noise` = 1.0, `classes` = 4. Nothing here says the seed component is the
  same at another circuit or another task suite, and `e38` already noted that per-rung costs vary by
  10×.
- **The instrument is the `naive` arm, not the arms under test.** `naive` has one head per task and no
  penalty; `ewc-block`'s per-seed spread need not match it. `e38` measured `ewc-block` at sd 0.0363
  and `ewc-block-rand` at 0.0500 on the same nine seeds, so the arms differ from each other by more
  than this estimate's own confidence interval.
- **Agreement is necessary, not sufficient, for "same computation."** Two runs could differ in a way
  neither the config nor the values reveal — a different code revision with the same behaviour on
  these seeds, for instance. The census is the best available evidence, not proof.
- `e54` reports no p-values, because there is nothing to test: it is a census and a variance
  decomposition on one sample.
