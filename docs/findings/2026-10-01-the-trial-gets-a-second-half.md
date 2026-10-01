# The trial gets a second half

*2026-10-01. Runs: `experiments/e323_the_trial_gets_a_second_half.py --json-out
runs/e323_the_trial_gets_a_second_half.json` -- two circuit sizes, two read-out configurations, the frozen connectome
network. Minutes. Plus `clfly/network/tasks.py::make_sequence_task`, the repository's second writer of a stimulus.*

## 1. What `e322` named and this builds

`e322` measured the trial's time axis across both suite builders, both splits and two circuit sizes and found the
stimulus equal to its first step **exactly**, everywhere. Its conclusion was that a temporal task needs *either a
second writer with a time index or an environment in the training loop*, and its "what it cannot do" left the choice
open. This takes the first option, because it fits the `(n, tau, n_neurons)` contract the runner already consumes: a
task with a time axis can be **trained** with no change to the training loop, and only a **closed** loop needs one.

`make_sequence_task` delivers two sub-stimuli per trial -- one symbol's template plus one noise draw for the first
``tau // 2`` steps, another symbol's plus a second draw for the rest -- and labels the example by the **ordered
pair**. The second half's symbol is in the drive throughout the second half; the **first** half's symbol is not in the
drive any more once the boundary is crossed, so a decoder reporting the pair from the last step has to have carried it
there in the recurrent state. That is the thing a sustained drive can never ask for.

**T1 MET.** Six tasks at the narrow read-out over two circuit sizes: the worst deviation **within** a half is
**exactly 0**, and the least change **at** the boundary over all examples is **1.9960**.

**T4 MET, and it is the result.** A two-way probe of the **first** half's identity, fitted and read at the **last**
step of the trial, reads **0.7500 at its worst** against a 0.50 chance -- a margin of **+0.25** -- and it does not
decay: the curve for `seq_odour_identity` at the narrow read-out of `mb+cx+al@n952` runs 0.79 0.96 1.00 0.96 1.00
0.96 1.00 0.96 0.96 0.92 0.92 0.92 across all twelve steps. **The connectome, frozen and untrained, carries a
symbol across a boundary through which its drive has stopped**, which is the first thing in this benchmark that the
time axis pays for. Set against `e322`: on a constant drive the read-out peaks after one or two steps and *declines*
for the rest of the trial; here the first symbol is held at its ceiling for the whole trial, and it is the *second*
symbol arriving that the state has to accommodate.

**T2 landed on its registered NULL.** The four-way pair probe at the last step reads **+0.0833** above chance at its
worst (narrow read-out), between the 0.05 window and the 0.15 bar, and at the task head the six margins spread from
**+0.0417 to +0.4583**. So the circuit holds each symbol and does not hold their **conjunction** at this
initialisation, and the pair curves are not monotone in the trial -- `seq_heading` at `mb+cx+al@n952` reads 0.62 at
the midpoint and 0.33 at the last step. A frozen, untrained network is a weak place to look for a conjunction; the
memory it does have is the part that needed no training to be there.

**T3's falsifier FIRED, and the registration is what fired.** The claim was that the pair is not readable before the
second half arrives: at most 0.05 above chance at the last step of the first half. It measured **+0.3750**, so the
falsifier fired -- and **it could not have done anything else.** The label is the ordered pair ``a * k + b`` with
``a`` and ``b`` independent, so a probe that reads ``a`` correctly and guesses ``b`` is right half the time: **0.50 is
a floor for this quantity, and the registered bar of 0.40 sat below it.** The quantity the claim was about is the
**second** symbol's probe at that step, and it was recorded beside the pair probe for exactly this reason: it reads
0.4167 to 0.6250 against a 0.50 chance, i.e. **-0.0833 to +0.1250**, inside 1.4 standard errors of chance at 24 test
examples. So the second half's symbol genuinely is not there before it starts, and the claim as registered was not
the test of it.

## 2. What it says

**The benchmark now has a task whose label is not in the drive at the moment it is read**, and the substrate passes
the memory half of it with room to spare while failing the conjunction half. That splits what "a temporal task"
means here into two questions that were one before this unit: *can the state carry something past its drive* (yes,
+0.25 at its worst) and *can the read-out decode what it carried together with what is current* (not at this
initialisation, +0.083 at its worst).

**And the runner does not need to change to train on it.** The sequence builder returns the same `RateTask` as the
sustained one, so a five-arm run on the sequence suite is a command, not a build. The **closed** loop -- an
environment whose next input depends on the agent's last output -- is the other option `e322` named and it is the one
that still needs the training loop, since `_RateNet.forward` consumes a precomputed `u`.

## 3. A correction to `e322`'s structural claim, and it is the one that unit predicted

`e322`'s **T2** registered that exactly **one** site in `clfly/` and `experiments/` writes a stimulus and that its
time axis is a full slice. Adding the second writer **fired it**, exactly as that unit's own "what it cannot do" said
it would: *"a temporal task needs either a second writer with a time index or an environment in the training loop"*.
The artifact now reports T2 as **FALSIFIER FIRED** with two authored sites, one full-slice and one carrying an
explicit step index, and the assertion in `tests/test_e322_*.py` is now the structural one that replaced the count --
one of each, in `clfly/network/tasks.py`, the sustained builder older than the sequence builder -- so a third writer
has to arrive deliberately rather than as a drift in a count.

The rest of `e322` stands unchanged: T1 MET (the invariance measurement, which was never about the count), T5 MET
(182 artifacts, none outside the two families), T3's falsifier still FIRED on the registered denominator and T4 still
on its null.

## 4. What it cannot do

**Twenty-four test examples** put one standard error of a four-way accuracy at about **0.09**, so T2's entire null
window is one standard error wide and T4's +0.25 margin is about 2.5 of them. **The frozen network is the connectome
initialisation**, so T4 is the substrate's memory and not a trained model's; whether training strengthens it or
destroys it is a run. **Two circuit sizes, one boundary position, one alphabet size and one leak**: ``k = 2`` gives a
two-way symbol and four classes, and a larger alphabet, a later boundary or a shorter half would each change what the
state has to hold. **The pair probe is one linear decoder at one read-out width**, and its spread across the six
configurations (+0.0417 to +0.4583) is wider than its distance from chance -- a non-linear decoder or a wider read-out
would place the conjunction ceiling differently. **And a boundary the noise redraws is not a boundary the symbol
redraws**: when the two symbols coincide the halves differ only by their noise draw, so "the stimulus changes at the
boundary" is guaranteed by the fresh noise rather than by the symbols, which is what the builder's tests now assert in
both directions.

## 5. RE-READ 2026-10-01: a third writer joined the two

`e325`'s closed-loop environment writes the cue into its input array, so `clfly/network/` now holds **three**
authored writers into a stimulus-shaped array: the sustained builder's full-slice broadcast, the sequence builder's
step-indexed write, and the environment's cue at step 0. Section 3 above described the pair; `e322` now reports
three sites for T2 and its assertion is the structural one -- one constant writer, the rest timed, all in
`clfly/network/`. The assertion here is correspondingly the statement of where the sequence writer sits (a timed
site in the same module, later in the file than the sustained one) rather than how many timed writers there are.
