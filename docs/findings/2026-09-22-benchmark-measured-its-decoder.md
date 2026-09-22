# E8f — the benchmark was measuring its decoder, not its connectome

**Date:** 2026-09-22
**Scripts:** `experiments/e8_rate_network.py --input-overlap / --noise / --readout-size / --frozen-body`
**Artifacts:** `runs/e8_hardened.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, shared head, chance 0.25

---

## 1. What this fire set out to do

The previous fire identified the limiter on the network benchmark: all tasks were learned
to ~0.92–1.00 accuracy, leaving no headroom for a continual-learning method to
demonstrate anything, so nothing discriminated. Three candidate fixes were proposed —
raise the stimulus noise, add classes, and drive the tasks into **overlapping** input
populations (testing the hypothesis that input-level separation is *why* forgetting was
mild).

All three were tried. None of them worked, and chasing why produced a more useful result
than any of them would have.

## 2. Overlapping inputs do not create forgetting

Tasks driven into input populations with **exactly uniform** overlap (the same
pool-plus-private-complement construction as `e7`), shared head, 3 replicates:

| input overlap | learned | mean forgetting | final accuracy |
|---|---|---|---|
| 0.00 (disjoint) | [0.958, 0.965, 0.972] | +0.021 ± 0.031 | 0.951 |
| 0.25 | [0.958, 0.972, 0.972] | +0.031 ± 0.026 | 0.947 |
| 0.50 | [0.958, 0.861, 0.958] | +0.028 ± 0.003 | 0.907 |
| 0.75 | [0.958, 0.868, 0.944] | **−0.021 ± 0.010** | 0.937 |
| 1.00 (identical inputs) | [0.958, 0.903, 0.979] | +0.003 ± 0.009 | 0.944 |

**No monotone trend, and forgetting stays tiny.** At *identical* input populations —
three different label mappings over the same 80 neurons — forgetting is +0.003 ± 0.009,
*lower* than in the disjoint case. So the hypothesis from the previous fire, that
input-level separation is why forgetting is mild, is **refuted**: removing the separation
does not restore it.

This agrees with `e7`, which found on the linear substrate that more input overlap gives
*less* interference: sharing input directions lets a later task confirm rather than
compete. Two substrates, same direction.

## 3. Task difficulty does not either

Raising the stimulus noise does exactly what it should to accuracy — and nothing to
forgetting:

| noise | classes | learned | mean forgetting | final accuracy |
|---|---|---|---|---|
| 1.0 | 4 | [0.958, 0.965, 0.972] | +0.021 ± 0.031 | 0.951 |
| 3.0 | 4 | [0.639, 0.562, 0.569] | **+0.000 ± 0.022** | 0.590 |
| 6.0 | 4 | [0.389, 0.312, 0.264] | +0.028 ± 0.021 | 0.303 |
| 3.0 | 8 | [0.326, 0.438, 0.299] | +0.031 ± 0.022 | 0.333 |

At noise 6 the tasks are barely above chance (0.303 against 0.250) and **sequential
training still does not forget** (+0.028). Headroom in accuracy is not headroom for
forgetting, which rules out "the benchmark is too easy" as the explanation.

## 4. The actual explanation: the plastic weights were never load-bearing

A `--frozen-body` diagnostic — train only the decoder, freeze the recurrent weights —
settles it:

| noise | body | final accuracy | mean forgetting |
|---|---|---|---|
| 1.0 | plastic | 0.951 ± 0.017 | +0.021 ± 0.031 |
| 1.0 | **frozen** | **0.944 ± 0.000** | **+0.000** |
| 3.0 | plastic | 0.590 ± 0.011 | +0.000 ± 0.022 |
| 3.0 | **frozen** | **0.560 ± 0.002** | **+0.000** |

**Freezing the recurrent weights costs 0.007 accuracy and eliminates forgetting
entirely.** The fixed connectome propagates each stimulus well enough that a linear
decoder over the whole state — 1307 features into 12 classes — solves the tasks, so the
plastic body barely moves and there is nothing to forget. The benchmark was measuring its
decoder.

That single fact explains everything else this fire found: why the class-incremental
setting was *easier* than task-incremental (the decoder had all the features), why
overlap made no difference, and why difficulty made no difference. It also explains a
result from two fires ago that had looked like noise — the **original** per-task suite did
show forgetting (+0.101 ± 0.020), and it read out from **narrow** populations (MBON 35,
central-complex 220, Kenyon cells 129 neurons).

## 5. The fix, and it is now quantified

Restricting the shared read-out to a narrow population forces the recurrent weights to
*route* information there. Sweeping the read-out size, with the frozen-body control
alongside:

| read-out neurons | body | final accuracy | **plastic − frozen gap** | mean forgetting |
|---|---|---|---|---|
| **32** | plastic | 0.917 ± 0.022 | **+0.102** | **+0.066 ± 0.019** |
| 32 | frozen | 0.815 ± 0.006 | — | +0.000 |
| 128 | plastic | 0.926 ± 0.008 | +0.009 | +0.035 ± 0.014 |
| 128 | frozen | 0.917 ± 0.000 | — | +0.000 |
| 1307 (whole) | plastic | 0.951 ± 0.017 | +0.007 | +0.021 ± 0.031 |
| 1307 | frozen | 0.944 ± 0.000 | — | +0.000 |

Two clean monotone relationships:

- **the plastic-minus-frozen accuracy gap grows as the read-out narrows** (+0.007 →
  +0.009 → +0.102), i.e. the recurrent weights become load-bearing;
- **forgetting grows with it** (+0.021 → +0.035 → +0.066).

So the amount of "continual-learning problem" a connectome-constrained benchmark contains
is set by how much of the circuit it reads out from. That is a design principle, and it is
worth stating plainly:

> **A connectome-constrained CL benchmark must use a narrow read-out, or it measures its
> decoder rather than its connectome. The frozen-body control is the diagnostic that
> detects the failure — report the plastic-minus-frozen accuracy gap alongside any
> forgetting number.**

## 6. Consequences

- The previous three fires' network conclusions all sit on a benchmark where the body was
  not load-bearing, which is *why* no method separated. Those conclusions
  ("no Fisher-anchoring variant beats naive", "the basis finding does not transfer", "the
  block-Fisher failure is not estimation noise") were established as **negative** results,
  and a benchmark that cannot show a difference cannot overturn them — but it also could
  not have confirmed a positive one, so they need re-running on the hardened
  configuration before being treated as final. The one exception is the λ/batch-count
  entanglement, which is a property of the Fisher machinery and not of the task.
- The class-incremental-is-easier result is explained rather than refuted: with a
  whole-state read-out the shared decoder had every feature, so the usual
  shared-input-space competition never arose.

## 7. And on the hardened configuration, EWC finally resolves

Re-running the method comparison at read-out 32 (5 replicates, λ = 0.003, 32 Fisher batches):

| method | final accuracy | mean forgetting | vs naive |
|---|---|---|---|
| naive | 0.914 ± 0.013 | +0.073 ± 0.015 | — |
| **EWC, diagonal Fisher** | **0.922 ± 0.010** | **+0.021 ± 0.015** | **−0.052 ± 0.021 (2.5σ)** |
| replay (16 stimuli/task) | 0.932 ± 0.008 | +0.050 ± 0.016 | −0.023 ± 0.022 (1.0σ) |

**Diagonal EWC finally resolves a benefit over naive — 2.5σ — and it is the best method on
forgetting, with accuracy also slightly better.** Replay, which was the one method that
resolved anything on the *unhardened* benchmark, no longer resolves here.

This reverses three consecutive fires of "no Fisher-anchoring variant does anything, at any
basis, λ, or Fisher batch count". Those were all measured on a benchmark whose plastic
weights were not load-bearing — a benchmark that cannot show a difference cannot establish
a negative one, and §6 of this document said so before the re-run was done. The re-run was
done, and the negative flips.

**Reconciliation with the theory, because the theory is not overturned.** LGCL says the
diagonal Fisher is a Kalman filter whose posterior is projected onto the neuron coordinate
basis, and §4.1 measured that projection to cost **33% excess error** on this connectome.
That makes EWC an *approximation with a measurable flaw*; it does not make it useless. On a
benchmark where sequential training genuinely forgets (+0.073), an imperfect anchor is still
better than no anchor — the comparison is against naive, not against the Kalman oracle. The
theory constrains how much EWC can buy, and 0.052 of forgetting out of 0.073 is a partial
buy, which is what a method built on a 33%-lossy approximation should deliver.

The genuinely surprising part is not that EWC helps but that **replay stopped helping**.
Content memory was expected to matter more than regularisation in the partially-observed
regime (LGCL v7's 12.7× finding), and on the unhardened benchmark it did. With the read-out
narrowed, the picture inverts. That is now the most interesting open question in the network
line, and it is a question this benchmark can finally ask.

## 8. What has to be re-run

Every network negative from the previous three fires was established on a benchmark where
the body was not load-bearing:

| previous conclusion | status |
|---|---|
| "no EWC variant resolves a benefit over naive" | **overturned** — diagonal EWC at λ=0.003 resolves at 2.5σ |
| "replay is the only method that resolves" | **overturned** — replay does not resolve on the hardened configuration |
| "the basis finding does not transfer to synapses" | **needs re-running**; it was tested where nothing resolved at all |
| "the block-Fisher failure is not estimation noise" | **needs re-running** for the same reason |
| "the block-Fisher failure is not a bad λ" | **needs re-running** for the same reason |
| λ is entangled with Fisher batch count | **stands** — a property of the Fisher machinery, not of the task |

The lesson is general enough to state as a rule for the project:

> Measure the plastic-minus-frozen accuracy gap before believing any forgetting difference.
> A benchmark whose frozen-body control matches its trained accuracy has no continual-learning
> problem in it, and every method comparison on it is a comparison of decoders.

## 9. Next

Re-run the basis comparison (biological synapse partition versus its matched random control,
and the blocked-versus-diagonal question) on the hardened configuration, with the
frozen-body gap reported as the benchmark's health check.
