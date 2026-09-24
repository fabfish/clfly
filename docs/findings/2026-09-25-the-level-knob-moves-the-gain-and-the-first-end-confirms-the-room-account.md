# The level knob moves the gain: the first end of `e167` confirms the room account, and names its own confound

**Date:** 2026-09-25
**Script:** `experiments/e171_noise_level_knob.py` — the read was written **before** the data existed; run now on
`runs/e167_r32_noise0.5_lam3e-4.json`. Artifact: `runs/e171_noise_level_knob.json`.
**Status: one of the two ends has landed.** `e167`'s noise-2.0 arm is still running, so this is a partial read —
and it is partial in a way that matters, because the confound below is one only the second end can settle.

---

## 1. The read

`e166`'s census found the room account's direction in **5 of 5 resolved cases and 0 against**, and then
disqualified its own evidence: the field that cannot move the level moves the gain by **0.0500**, 8 of the 13
level-moving rows are the closed `frozen_bias` diagnostic, and the other two fields change the task structure
(`classes`) or the decoder (`readout_size`). **What was missing is a level knob at fixed architecture and fixed
task structure**, and `e167` runs one: `--noise 0.5` and `2.0` against the noise-1.0 reference, at λ = 3e-4 where
the base family's penalty is resolved.

| setting | `naive` forgetting | level step | resolution | the penalty's gain | gain step | resolution |
|---|---|---|---|---|---|---|
| noise 1.0 (reference) | 0.0750 | — | — | **+0.0354** | — | — |
| **noise 0.5** | **0.0438** | **−0.0312** | **3.55σ** | **−0.0016** | **−0.0370** | **3.57σ** |

**P1 holds** — the level moved at 3.55σ. **P2 agrees at that end** — the gain's step has the level's sign and
resolves at 3.57σ. **The falsifier does not fire.** Both were registered before the artifact existed, and the
script that evaluates them was too.

**And the gain's step is larger than the whole effect it moves.** At noise 1.0 the penalty beats `naive` by
**+0.0354 at 4.27σ**; at noise 0.5 it beats it by **−0.0016**, which does not resolve. **The same method, the same
λ, the same Fisher and the same partition, on the same architecture — and the penalty has no advantage at all
merely because the tasks left less to forget.** That is the room account's prediction, and it is the first time
this project has produced it with a knob that leaves the architecture, the read-out, the class structure and the
partition untouched.

## 2. The confound, stated before the second end arrives

**`noise` is not a clean level knob, and its impurity is exactly the thing the room account needs held fixed.**
The Fisher is estimated at the **initial** parameters from minibatches of the training data — and `noise` changes
the data. So the stimulus noise may move the penalty's advantage by changing **how strong the penalty is**, not
only how much there is to forget. This end cannot separate those, and it is the reason the second end matters: the
room account predicts a *rise* of comparable size at noise 2.0, and the "weaker Fisher" account predicts the same
sign at both ends if the Fisher is weaker at both.

**And a strictly cleaner knob exists, which the corpus has never varied**: `--iters`. The Fisher is computed at
θ_init and does not depend on how long the network trains, so `--iters` moves the level — more training, more
forgetting to remove — while leaving **the penalty term itself identical**. `e166`'s census listed `iters`,
`train` and `noise` as the three knobs this corpus has never varied in isolation on a pair carrying a naive arm
and a penalty arm; **`iters` is the one of the three whose impurity is zero**, and it is registered below.

## 3. What this cannot settle

- **One end of two.** The second is running, and the two-sided shape (a rise at 2.0 as well as a fall at 0.5) is
  what would make the tracking a *line* rather than a coincidence of signs.
- **The Fisher confound of §2**, which the second end reduces and does not remove: with two ends that bracket the
  reference, a `noise` effect on the Fisher that is monotone in noise predicts the same signs, so **agreement at
  both ends is consistent with the room account and not exclusive to it**. Only a knob that leaves the Fisher
  bit-identical can exclude it, and `--iters` is that knob.
- **λ = 3e-4 is one penalty strength.** The room account is about what the penalty does *as a function of* the
  room, and a level knob at the base family's other λ values (`e165`'s ladder) is a different experiment.
- **One family, one read-out (32), three tasks, one seed stream.** The witness is the base family's plastic arm;
  the wiring family's λ-insensitivity (`e162`) is a different regime and not re-tested here.
- **`e171`'s reference is formed across two artifacts** (`e133`'s `naive` and `e141`'s λ = 3e-4 `ewc`), which is
  legal because they differ in `lam` — a field `e160` derives as unread by `naive` — and it is checked rather
  than assumed: the level is one number and the gain is what λ moves.
