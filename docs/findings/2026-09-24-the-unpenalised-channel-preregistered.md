# `e125` pre-registered: does the 800-parameter channel that no penalty covers carry the forgetting?

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py`, with one new diagnostic flag (`--frozen-bias`) and one new record
(`bias_norms`).
**Planned artifacts:** three arms, all in **one code epoch** (this commit's), each
`--readout-size 32 --iters 500 --test 48 --repeats 40 --methods naive --shared-head --input-overlap 0.0
--seed0 0 --circuit-size 800`:
`runs/e125_r32_plastic.json`, `runs/e125_r32_frozenbias.json`, `runs/e125_r32_frozenbody.json`.
**Labeled comparators, and they are from other epochs:** `runs/e116_r32_40reps.json` (40 replicates,
read-out 32, plastic: **+0.0750**, per-repeat sd **0.0556**) and `runs/e104_frozen_r32_plastic.json`
(5 replicates, **+0.0729 / 0.9139**) and `runs/e104_frozen_r32_frozen.json` (**+0.0000 / 0.8139**).
**Context:** the flag does not come from a hypothesis about biology. It comes from reading `train_task` and
`diagonal_fisher` together.

## The defect this checks, stated as code rather than as an intuition

`train_task` optimises `[model.theta, model.bias]` (`experiments/e8_rate_network.py:72`), so the body is **two**
trained parameter sets: 26,568 masked recurrent weights that *are* the connectome, and **800 per-neuron offsets**
at cs = 800. Every penalty in this project covers the first only:

- the diagonal EWC term is `sum(fisher * (model.theta - anchor) ** 2)` — `theta`, and not the bias;
- the block penalty is built from a `SynapsePartition`, whose blocks are partitions of **synapses**, so the bias
  has no block structure to be penalised in at all.

And the justification on record is **incoherent for the bias**. `diagonal_fisher`'s docstring says: *"Only
`theta` is differentiated: the decoder is task-specific and the bias is shared, and letting either into the
Fisher would blur the object the project is studying."* That reason works for the decoder — a per-task decoder is
not part of the body — and it **does not work for the bias**, because *"the bias is shared"* is equally true of
`theta`, which **is** anchored. So the omission is deliberate, and the stated reason for one of its two halves is
wrong. Whether the omission *matters* is a measurement.

**The measurement is the diagnostic this project already trusts, split in two.** `--frozen-body` freezes `theta`
and the bias together, so it cannot say which of them carries anything; at read-out 32 it drives the forgetting
to exactly `+0.0000` (fifteen replicates agreeing to the last digit), which establishes that the body is
load-bearing and **not** what inside it is. `--frozen-bias` freezes the bias alone, holding it at its
initialisation — the only value it has ever had before task 0, since it starts at exactly zero.

## Why three arms in one epoch, and the epoch finding that forced it

The plastic arm already exists twice: `e116_r32_40reps.json` is the identical configuration at 40 replicates.
**It cannot be used, and the reason is a measurement rather than a caution.** Its first five replicates are
**not** bit-identical to `e104_frozen_r32_plastic.json`'s five: the two artifacts' replicate dicts carry
**different key sets** — `e104`'s lack `theta_drift`, `e116`'s lack `retention_loss` — so they are two code
epochs, and a contrast whose two sides come from two epochs is a contrast in code as well as in the variable
**even when the variable is the same on both sides**. That is rule 27 applied to a comparison of a run with
*itself*, which is the case it was not written for, and it is why this fire runs the plastic arm again rather
than citing it.

## The predictions

- **C0a, structural and exact.** The `--frozen-body` arm gives `mean_forgetting == 0.0000` at **all 40**
  replicates, `final_accuracy` equal across replicates to the last digit, and every `bias_norms` entry exactly
  `0.0` — a recorded zero rather than an absent field, which is `e122`'s lesson applied.
- **C0b, structural and exact, and it is the new flag's own control.** The `--frozen-bias` arm has every
  `bias_norms` entry exactly `0.0` **while** `theta_drift` is non-zero at every task and every replicate. Both
  halves are needed: the first alone would pass for a run that froze everything, which is the failure
  `--frozen-body` exists to detect in the other direction.
- **C0c, cross-epoch and labeled as such.** The fresh plastic arm's 40-replicate mean is within **one sem** of
  `e116`'s +0.0750, i.e. inside **±0.0088** (`0.0556/√40`), and its per-repeat sd is within a factor of 1.5 of
  0.0556. A tolerance rather than an equality, because the comparators are other epochs, and stated with its
  width so that "it reproduced" is a bounded claim.
- **P1, and it is the fire.** Freezing the bias **does not halve the forgetting**: with
  `F_plastic` the fresh plastic mean and `F_frozen_bias` the frozen-bias mean,
  `F_frozen_bias > 0.5 · F_plastic`.
- **Falsifier.** `F_frozen_bias <= 0.5 · F_plastic` — freezing the bias removes **at least half** the
  forgetting. Then **800 parameters, 2.9% of the body, carry the majority of this benchmark's forgetting**,
  EWC's unpenalised channel is a first-order defect rather than a footnote, and every EWC number in this project
  is measured against a naive baseline whose forgetting partly lives where the penalty cannot see.
- **P2, the mechanism half — registered as a direction, not a threshold.** The plastic arm's
  `bias_from_zero` grows across tasks and `max_t bias_step > 0`. A plastic arm in which the bias does not move
  at all would make P1 vacuous rather than true. **Registered separately from P1 because P1 can pass for two
  different reasons** — the channel matters little, or it matters and the weights absorb its absence — and P2
  does not decide between them, it only rules out the vacuous reading.

## Power, computed from the measured sd rather than a guessed one

Read-out 32's plastic per-repeat sd is **0.0556** at forty replicates (`e116`; note this is the *largest* of the
axis's seven and **not** the 0.0423 that belongs to read-out 1307 — a number this registration got wrong in its
first draft by reaching for a remembered figure instead of the artifact, which is why the sd is quoted with its
source). At 40 replicates per arm the unpaired two-arm standard error of a difference is
`0.0556 · √(2/40) = 0.0124`, so a drop of half the forgetting (0.0375) is resolvable at **3.0σ** and a drop to a
third of it at 4.0σ. **At 20 replicates the same drop would be 2.1σ**, which is why the arm is 40 and not 20:
`e115`'s rule is that a design landing on its own criterion cannot answer the question it is asked.

The arms share their training seeds, so a paired treatment is available and is reported **beside** the unpaired
one. `e115` found a paired σ optimistically tight when the shared term is fixed within a run; here the shared
term is the seed block, which is exactly what pairing removes, so **the verdict is read off the unpaired
figure** and the paired one is a tightening reported beside it, not the basis of the verdict.

## What this cannot settle, in advance

- **It tests the omission, not the penalty.** It says how much forgetting the unpenalised channel carries; it
  does not say what an EWC whose penalty covered the bias would do, because there is no natural way to block a
  per-neuron offset (no synapse, no block) and mixing a diagonal bias term into the block arm would make the two
  arms differ in two places at once.
- **One read-out, and it is the one chosen for the opposite reason.** Read-out 32 is where the body is most
  load-bearing, which maximises the chance of seeing the bias matter — so if the falsifier does **not** fire here
  it is weak evidence that it would not fire at read-out 128 or 0, *not* strong evidence. The direction is stated
  because it is what bounds a null.
- **`bias_norms` is a movement, not a mechanism.** A large `bias_from_zero` beside unchanged forgetting would say
  the channel moves and the weights absorb its absence — a real possibility this design cannot exclude.
- **The bias has no wiring semantics, which is a reason the omission might be right.** The partition is a
  partition of synapses; the bias is not on a synapse. So a result that the omission is harmless is a cleaner
  outcome than the argument for the omission currently on record, which is part of why P1 is the prediction.
