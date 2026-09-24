# The cost spread is real, its obvious fix is refuted, and the record cannot attribute it

**Date:** 2026-09-24
**Data:** the `timing_s` and `config` blocks of sixteen artifacts this session wrote — every one already in `runs/`.
**Change:** `experiments/e8_rate_network.py`'s `environment()` block now carries a **calibration**
(`calibration_matmul_s`), one fixed 256×256 matrix multiply, timed.
**Trigger:** four background jobs have held this machine since 10:00 and artifact after artifact has taken
**two to three times** its solo cost, with nothing in the record to say why.

---

## 1. The spread, measured from the artifacts' own timings

| artifact | replicate-trainings | total s | **s per replicate** |
|---|---|---|---|
| `e138_r32_ewc_anchorbias1` | 40 | 1785 | **44.6** |
| `e139_r32_wholebody` | 80 | 4444 | 55.5 |
| `e133_r32_naive_ewc_40reps` | 80 | 4560 | 57.0 |
| `e141_r32_ewc_lam3e-2` | 40 | 2143 | 53.6 |
| `e142_r32_overlap1_frozen` | 40 | 3174 | 79.4 |
| `e143_r32_overlap1_frozenbias` | 40 | 3410 | 85.2 |
| `e141_r32_ewc_lam3e-4` | 40 | 3635 | 90.9 |
| **`e144_r32_overlap1_rand_draw1`** | 40 | 5278 | **132.0** |

**A 3.0× spread across one session's runs of the same script at the same configuration.** The project's cost
figures are already known to be environment-shaped (`§9` says so about the timings themselves), and this is what
that looks like at the scale of one afternoon.

## 2. The obvious explanation, and the cheap probe that refutes its fix

This machine has **20 cores**, torch reports **20 threads** per process, and up to **four** jobs ran at once —
60–80 threads on 20 cores. The natural diagnosis is oversubscription and the natural fix is to throttle. **The
probe costs three short runs and says no**: on the same saturated machine, 40 iterations plus setup took

| `OMP_NUM_THREADS` | wall clock |
|---|---|
| **20** | **19.5 s** |
| 4 | 22.0 s |
| 1 | 28.7 s |

**Fewer threads makes each process *slower*, not faster** — so on this workload and this machine, throttling is
not the lever, and the 3.0× spread is **not** explained by the thread setting. (It is not explained by anything
else in the record either: the artifacts record `torch_num_threads` and not the load, so no two runs can be
compared in the same units.)

## 3. The repair is an instrument rather than a policy

**A calibration**, timed inside `environment()` and recorded in every artifact: one fixed 256×256 matmul, warm-up
excluded. It is a **rate rather than a load count** — the runner cannot see what else is running, and asking it to
describe its own queue would be a claim rather than a measurement. With a rate in the artifact, a 3× slower run
can be compared against a 3× slower calibration and **the two costs become commensurable**: *"this took 40 minutes
on a machine that was 2.4× slower than the one the 17-minute figure came from"* is a sentence the record can now
support, and it could not before.

**Which is `§9`'s own rule made mechanical.** That section already says a cost must be quoted beside the
environment it was measured in, and until now the "environment" was a list of versions and thread counts — none of
which is a speed. **A calibration is the missing half.**

## 4. What this does not settle

- **The three probe runs are single trials** and were run on a machine that was already saturated, which is the
  condition of interest but also the condition under which a single trial is least stable.
- **The calibration is one operation on one machine.** A matmul is the right op for this workload — the model is
  small and BLAS-bound — but a different bottleneck (disk, the connectome load, Python startup) would need its
  own calibration, and the connectome load in particular happens *before* `environment()` is written.
- **And the scheduling lesson is deliberately left as a hypothesis the data do not support**: four concurrent jobs
  did not obviously buy wall-clock and did lengthen every result, but since the thread setting is not the lever,
  **the queue's tuning is unmeasured** — which is exactly what the calibration is for, and why this fire records
  the spread and the instrument rather than a policy.
