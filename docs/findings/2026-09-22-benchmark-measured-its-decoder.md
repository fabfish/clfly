# E8f — the benchmark was measuring its decoder, not its connectome

**Date:** 2026-09-22
**Scripts:** `experiments/e8_rate_network.py --input-overlap / --noise / --readout-size / --frozen-body`
**Artifacts:** `runs/e8_hardened.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, shared head, chance 0.25

> **Correction (2026-09-23).** **The `--frozen-body` sweep this document is built on is in no artifact.** Not
> one of the 204 files under `runs/` has `frozen_body: true`, a `frozen` arm, or a frozen-body result anywhere
> in its payload — and the artifact declared above, `runs/e8_hardened.json`, has `naive`, `ewc` and `replay` and
> no frozen row. So **§5's six-row table has three rows nothing backs**, and with them the two series the paper
> quotes from it (+0.007 → +0.009 → +0.102 accuracy gap against +0.021 → +0.035 → +0.066 forgetting). This is
> not a missing capability: this document *is* the commit that added `--frozen-body` (09-22 10:18), so the runs
> were made in this fire and printed rather than saved. The diagnostic may well be sound — it is a measurement
> that was never written down, which is why the paper's design principle now carries the qualifier that it is
> asserted and not yet measured here
> (`docs/findings/2026-09-23-the-frozen-body-control-is-in-no-artifact.md` §1).

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

**(*Regime caveat added 2026-09-24, and it is a caveat about this table rather than about its arithmetic.*)**
**The overlap table above was taken at the whole-state read-out, and this finding's own §4 shows that at that
read-out the plastic weights were not load-bearing** — the frozen body reached 0.944 against the plastic arm's
0.951. A benchmark whose decoder solves the tasks with the recurrent weights untouched **has no forgetting for
input overlap to create**, so the refutation is **conditional on the read-out**, and at read-out 32 the narrow
setting every later result in this project reports, the same construction gives frozen **0.8134** against plastic
**0.9125**, a 0.10 gap. **The question is therefore open again where the body matters**, and it is registered
there as `e142` (`docs/findings/2026-09-24-the-overlap-family-at-a-narrow-read-out-registered.md`). The
conclusion in the paragraph below — that overlap and difficulty were the wrong two levers *for this benchmark* —
stands as written, because it is a conclusion about the benchmark that was run.

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

**(*Regime caveat added 2026-09-24, and it is the same one §2 now carries.*)** **This table's four rows are from
the same runs whose `--frozen-body` diagnostic is §4 — where freezing the recurrent weights costs 0.007 accuracy
and eliminates forgetting entirely.** In that regime the body is not doing the work, so *"difficulty does not
create forgetting"* is a statement about **a benchmark the decoder solves**, and it cannot be read as a statement
about what difficulty does where the plastic weights are load-bearing. **The same construction at read-out 32
gives a 0.10 accuracy gap between the plastic and frozen bodies**, and nothing in this project has yet measured a
noise or class-count sweep there. **So the two levers this finding closed — input separation and task
difficulty — are closed at the whole-state read-out and open at the narrow one**, with the caveat that the
difficulty axis differs from the overlap axis in one respect: the `e142` registration could name an existing
comparator at read-out 32 (`e133`'s `naive`, the same construction at overlap 0), while a noise sweep at
read-out 32 has **no comparator in the record at all** and would need its own `naive` arm measured with it. That
is why the overlap arm was the one run first, and the noise axis is recorded here as the next one rather than as
a second launch.

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
forgetting, with accuracy also slightly better.** **(*Superseded in two steps, both measured on 2026-09-24, and
neither by re-running this table.*)** Running the identical command at **forty** replicates gives a paired
**−0.0096 ± 0.0080 = 1.21σ** against `naive` — **the five seeds above are a ~1-in-55 draw** from this
configuration's own distribution (their mean +0.0208 against +0.0717 for replicates 6–40, ranks 10, 6, 9, 1, 16
among the forty), so the 2.5σ does not survive; **and then the same forty seeds with the 800 offsets *inside* the
penalty give −0.0458 ± 0.0095 = 4.84σ**, recovering 84.8% of the gap to the free freeze. **So this section's
direction was right and its evidence was five seeds**: the row does resolve, at **4.84σ** rather than 2.5σ, once
the penalty covers the channel that carries 70% of this configuration's forgetting — and §4.2 of the paper
carries both corrections
(`docs/findings/2026-09-24-diagonal-ewc-does-not-survive-its-own-configuration.md`,
`docs/findings/2026-09-24-the-arm-that-fixes-the-forgetting-has-more-interference.md`). Replay, which was the one method that
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
