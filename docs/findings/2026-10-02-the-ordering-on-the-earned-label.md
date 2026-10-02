# The ordering on the earned label: `replay` beats the penalty by 0.2521 at 11.65 sigma, all twenty replicates agreeing

*2026-10-02. One runner invocation: `--circuit-size 300 --iters 500 --readout-size 32 --train 96 --test 48
--repeats 20 --methods naive,ewc-block,replay --closed-loop --loop-symbols 4 --loop-noise 1.0 --loop-world-dims 8
--loop-world-leak 0.35 --loop-scale 1.0 --readout-from-world`, into `runs/e356_earned_label_r32_20reps.json`.
Thirty-two minutes. Read by `experiments/e356_the_earned_label_at_twenty_replicates.py`.*

## 1. The replicates `e355` could not buy

`e355` closed the gap every unit from `e349` to `e354` had named -- the earned label now runs through the corpus's
own runner, with its optimiser, its metrics and its paired-channel instrument -- and it closed with what five
replicates could not do: its own power note put detectability at **0.106**, and the matched-random pair came out a
0.0125 near-tie.

**This unit buys twenty paired replicates for the two arms the corpus's headline method contrast is between.**
`e276` found `replay` beating `ewc-block` by **3.30 to 11.84 sigma** on the state read-out; `e346` found the ordering
travelling across twenty-six experiments and never resolving against; `e347` found the one family that disagreed
resolving at 3.11 sigma once it was powered. **Whether it holds where the answer is read from the environment is a
question the corpus has never asked.**

## 2. The answer

| arm | final accuracy | diagonal | `mean_forgetting` | sem | paired channel | sigma |
|---|---|---|---|---|---|---|
| `naive` | 0.5493 | 0.8226 | 0.4099 | 0.0194 | +0.2951 | 19.73 |
| `ewc-block` | 0.5219 | 0.7719 | 0.3750 | 0.0190 | +0.2660 | 16.52 |
| `replay` | **0.6983** | 0.7802 | **0.1229** | 0.0142 | **+0.4434** | **34.84** |

chance 0.2500. **T1 MET**: the world read-out is recorded, the read-out widths are `[8]`, all three arms carry
twenty replicates, and the world is the same draw `e355` and the local loop used -- `world_read_sha1
3a7ba76b3619` against `e355`'s own value.

**T2 MET, and it is the finding: the ordering resolves on the earned label at 11.65 sigma.** `replay` forgets
**0.2521** less than `ewc-block`, paired over the twenty replicates -- `[-0.344, -0.125, -0.219, -0.146, -0.167,
-0.406, -0.240, -0.375, -0.417, -0.188, -0.375, -0.198, -0.146, -0.135, -0.260, -0.167, -0.208, -0.281, -0.333,
-0.312]` -- **every one of the twenty negative**. **T3 MET**: and it is not paid for on the newest task, where
`replay`'s diagonal is actually **+0.0083 above** `ewc-block`'s, with a final accuracy **+0.1764** higher. **T4
MET**: every arm's answer is earned, the paired channel reading being **+0.2660 to +0.4434 at 16.52 to 34.84
sigma**.

**The retention matrices show where it comes from.** On replicate 0, `naive` reads task 0 at **0.292**, `ewc-block`
at **0.208** and `replay` at **0.458** -- the buffer holds the first task at more than twice the penalty's level.
And **the penalty is barely better than nothing on this substrate**: `ewc-block`'s forgetting is 0.3750 against
`naive`'s 0.4099, while its final accuracy is *lower* (0.5219 against 0.5493), which is the corpus's own standing
result -- the penalty's gain over the naive baseline was unresolved at every configuration the C2b line read --
reappearing on a task where the answer lives in the environment.

## 3. What it means for the two lines

**For the method line**, `e276`'s contrast now has a seventh configuration and a fourth kind of substrate: not the
800 or 300 circuit, not the overlap or assembly suite, not the open or closed loop, but **the earned label**, where
the read-out is the environment and unwired it is at rest. The ordering is **11.65 sigma** there, inside the range
the state read-out gave (3.30 to 11.84), so `e346`'s conclusion -- the advantage travels -- extends to it.

**For the earned-label line**, this is the power `e355` lacked: the paired channel reading moves from 6.06 to 16.64
sigma at five replicates to **16.52 to 34.84** at twenty, the suite's forgetting is **0.4099 (sem 0.0194)** under
`naive`, and the buffer's value is **0.2521 at 11.65 sigma**. What is still missing is the basis contrast: the
matched-random pair is not in this run.

## 4. What it cannot do

*Three arms and no matched-random pair*: the basis contrast -- `ewc-block` against the size-matched random
partition, the corpus's own headline and the null eleven audits left standing -- is not in this run, so nothing here
is about the connectome's block structure. *One world, one leak and one width*: `leak = 0.35`, eight dimensions and
four symbols per task, with `e351`'s finding that the width is 88% of the carrier's value and its shape a seventh.
*One seed stream*: the corpus's `seed0 = 0`, so this is a configuration and not a stream comparison. *And the paired
reading's unwired side is exact rather than evaluated*: an unwired world does not run, so the head sees one constant
and that accuracy is computed from the rest state, which is what makes the label earned rather than predicted.
