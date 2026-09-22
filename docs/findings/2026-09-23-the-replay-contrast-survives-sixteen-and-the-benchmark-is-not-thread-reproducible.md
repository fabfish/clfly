# E68 / E77 — the replay contrast survives sixteen replicates at **6.73σ**, and the benchmark is not reproducible across thread counts

**Date:** 2026-09-23
**Scripts:** `experiments/e77_thread_determinism_probe.py`, analysis over `runs/e68_replay96_step8_16reps.json`
**Artifacts:** `runs/e68_replay96_step8_16reps.json`, `runs/e77_thread_determinism_probe.json`
**Context:** `2026-09-23-the-replay-result-reproduces.md` (e61), `2026-09-22-the-c2b-rung-result-was-three-seeds.md` (e46), `2026-09-22-naive-arm-census.md` (e54)

---

## 1. The result: this is the first thing in the line that survives sixteen replicates

`e61` recreated the missing artifact behind the network line's headline positive result and gave the
contrast at −0.08542 ± 0.01293 = **6.61σ** on five replicates. Its own finding named the test that
matters, because it is the one that killed `e46`:

> a sixteen-replicate version of this one configuration is the obvious next run; note that this is
> exactly the move that killed `e46`'s −0.0648, so it is a real test and not a formality.

`e68` is that run. **It survives.**

| metric | naive | replay | delta | sem (paired) | **σ** | signs | LOO min σ |
|---|---|---|---|---|---|---|---|
| mean forgetting | +0.06250 | **−0.00521** | **−0.06771** | 0.01006 | **6.73** | **16/16 −** | 6.2 |
| final accuracy | 0.91970 | **0.95747** | **+0.03776** | 0.00591 | **6.39** | 15+/1− | 5.9 |

**Sixteen of sixteen replicates agree in sign on forgetting**, the leave-one-out minimum is 6.2σ, and
the contrast is 6.73σ against 6.61σ at five replicates. So the effect neither collapsed nor grew as the
sample grew — which is what a real effect does, and the opposite of what happened to `e46`'s −0.0648
(2.65σ → 0.24σ) under exactly the same discipline.

**And the one claim that did weaken is the absolute one.** Replay's own forgetting from zero is
**−0.00521 ± 0.00624 = 0.83σ** at sixteen replicates, against **3.21σ** at five. So:

> **"replay beats naive at this configuration" is 6.73σ with sixteen of sixteen signs agreeing.**
> **"replay drives forgetting below zero" is not resolved at sixteen replicates.**

The five-replicate run supported both. The honest form of the result is the relative one, and the
absolute one was always the weaker of the two — the paper's own numbers imply it (a 3.21σ arm reading
behind a 6.61σ contrast means most of the contrast is naive being *bad*, not replay being *good*).

## 2. But the run is not a nested extension, and finding out why is a second result

`e61` has five replicates and `e68` sixteen of the same configuration, so the natural reading is that
`e68` extends `e61` and the first five replicates should be identical. **They are not** — from the very
first replicate:

```
e61 (5 reps, no OMP_NUM_THREADS): 0.923611  0.951389  0.875     0.895833  0.923611
e68 (16 reps, OMP_NUM_THREADS=4): 0.875     0.9375    0.895833  0.916667  0.923611  0.951389 ...
```

The two configurations are identical in **every** stored field except `repeats`, so this is either a
bug in the seeding or an unrecorded variable. `e77` separates the two candidates by running the same
small configuration three times, one variable at a time:

| run | setting | `naive` accuracies |
|---|---|---|
| A | `repeats 3`, default threads | 0.875000, 0.902778, 0.909722 |
| B | `repeats 4`, default threads | 0.875000, 0.902778, 0.909722, 0.819444 |
| C | `repeats 3`, **`OMP_NUM_THREADS=4`** | **0.826389, 0.840278, 0.930556** |

**A and B agree on their first three replicates exactly, so `repeats` is inert** — the seeding is what
the code says it is, one replicate per `seed0 + 100·r`. **C shares *zero* of its three accuracy values
with A.** So:

> **The same command under a different thread setting trains to a different result.**

PyTorch's CPU reductions are order-dependent, so the thread count changes the arithmetic and, over 500
iterations of a nonlinear recurrent system, the trajectory. The benchmark is deterministic *given an
environment* and not across environments.

## 3. What that rescopes, which is a real correction and not a caveat

`e54` established the project's determinism control: the `naive` arm is bit-identical across runs, so it
is a free instrument and a free way to accumulate seeds. Its census verified agreement **by value**
between every artifact pair it grouped — which is the strongest available check — and it did not vary
the **environment**, because nothing recorded one.

So the corrected statement is: **the `naive` arm is a determinism control within a thread setting, not
across environments.** Concretely:

* `e54`'s census is not wrong. Its cluster members really do agree to the last decimal, and its
  conclusion — six distinct computations, the largest with sixteen seeds — stands for the artifacts it
  grouped. But *which* artifacts group together is partly a statement about which were launched with
  `OMP_NUM_THREADS` set, and that is nowhere in the artifacts.
* **The project's own runs are split.** Of the network runs, `e68`, `e64`, `e60` and `e61` were launched
  this session with different environments, and `OMP_NUM_THREADS` was set on some and not others. Any
  comparison across them inherits a variable no artifact records.
* **`e68` is a separate sample of the same configuration, not an extension of `e61`.** It answers "does
  the effect hold at sixteen replicates" — yes, at 6.73σ with 16/16 signs — and it does **not** answer
  "does the effect shrink as `n` grows", which is the question `e46`'s nested comparison answered for
  the C2b rung. That question is now open for replay, and closing it needs the two runs to share an
  environment.
* The 16/16 sign record is unaffected by any of this. Sixteen paired differences agreeing in sign under
  two different environments is stronger evidence than five agreeing under one.

## 4. And the analytic line is thread-sensitive too — at the fourth digit, not the first

Everything above is the torch path. The analytic (numpy) path is what the paper's reproduction claims
actually rest on — "the cs = 800 column reproduces bit-for-bit" — so whether *it* is environment-stable
decides how much of the record is at risk. `e77` runs `e12_control_spread` twice on the same small
configuration, once with `OMP_NUM_THREADS` unset and once at 4:

| quantity | default threads | `OMP_NUM_THREADS=4` | abs diff | relative |
|---|---|---|---|---|
| biological excess mean | 0.00151944497748 | 0.00151935491472 | 9.0e-8 | 5.9e-5 |
| control sd across draws | 0.00170586293021 | 0.00170580016040 | 6.3e-8 | 3.7e-5 |
| delta | −0.00220874212934 | −0.00220874007566 | 2.1e-9 | **9.3e-7** |
| per-seed excesses (2) | — | — | — | **1.8e-4** worst |
| control means (2 draws) | — | — | — | 2.8e-5 worst |

**So the analytic path is thread-sensitive as well, at about the fourth significant digit** — where the
torch path under the same manipulation produces a *different answer* (0.875 against 0.826). The two
substrates fail differently in kind, not just in degree.

**No conclusion moves, and that is checkable rather than asserted.** The tightest standard error the
project quotes is `cell_type`'s paired seed sem of **1.29e-5** against a delta of 2.61e-4 (`e66`); the
environment noise on a per-seed excess is of order **3e-7 absolute** (1.8e-4 relative of 1.7e-3), i.e.
**40× below that sem** and three orders below the delta. So every σ in this project is two or more
orders of magnitude clear of the environment, which is why none of them has ever moved.

**What does have to change is the language.** "Bit-for-bit" and "bit-identical" are wrong for this
project's numbers, and they are used repeatedly — including in `e62`'s reproduction check and in the
paper's reproducibility section. The correct claim is **"identical to about four significant digits
given an environment"**. `e65`'s realization 0 reproducing `e48`'s published `swap0.5` value "to six
decimals" was printing precision, not bit-exactness — and the same is true of every "reproduces
bit-for-bit" in the record.

## 5. Limits

- **One environment pair.** `e77` varies the thread count and nothing else; it does not establish
  *which* part of the environment matters, and a different torch build or BLAS backend would be a
  different experiment again.
- **The analytic (numpy) experiments may be immune, and one observation says they are.** `e65`'s
  realization 0 reproduced `e48`'s published `swap0.5` value to six decimals under a different
  `OMP_NUM_THREADS` than `e48` ran with. That is one point and it is suggestive, not a measurement;
  the sensitivity demonstrated here is in the torch training path.
- **`iters` 100 and cs = 300 for the probe**, against 500 and 800 for the runs it explains. The probe is
  a controlled demonstration of the mechanism, not a measurement of the size of the difference at the
  production configuration.
- **Sixteen replicates is still below the "above ten" bar only in spirit** — `e54`'s replicate
  arithmetic says a 0.03 effect needs 19 — so the forgetting contrast is at or near the floor the
  detection arithmetic wants, even at 6.73σ.
- **Pool 96 / per-step 8 remains the only surviving positive result in the network line.** Nothing here
  changes the other rows, which are nulls at their best available power.
