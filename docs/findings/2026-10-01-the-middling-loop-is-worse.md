# The middling loop is worse, at two sigma's edge

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 40
--methods naive --closed-loop --loop-scale {0.0, 0.5}` -- two commands, 752 s and 789 s, read by
`experiments/e328_is_the_middling_loop_worse.py`.*

## 1. The resolution `e327` said it needed

`e327` swept the feedback strength over 0.0, 0.25, 0.5 and 1.0 at five replicates each. Its registered ordering
fired, and its own finding said why that proved little: `learned` was `[1.0, 1.0, 1.0]` on all twenty arms, so
every replicate at every strength solved every task perfectly and the only quantity that moved was **whether a
replicate forgot anything at all** -- **1, 0, 2 and 0 of five**. The ordering rested on one replicate, and at those
proportions 2 sigma needs about forty per level.

This buys it, for the two settings whose rates differed: **0.0 and 0.5**, `naive`, **forty replicates each**. Two
runs and not four, because the question the sweep left open is the practical one -- is a middling loop worse than no
loop? -- and because `e327`'s T4 established that a feedback of 0.0 is **bit-identical** to the loop unwired, so the
0.0 arm is also the control.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, forty replicates
at both strengths, **no unexpected config or environment difference** once the strength itself is excluded.

## 2. The five-replicate point estimates held, and both were low

A replicate counts as **forgetting** when its `mean_forgetting` exceeds 0.05, a convention recorded in the
registration because the quantity is a share of what the arm had and gave back.

| feedback strength | n | replicates that forget | rate | accuracy | mean forgetting |
|---|---|---|---|---|---|
| 0.00 | 40 | **10** | **0.250** | 0.9625 | 0.0563 |
| 0.50 | 40 | **18** | **0.450** | 0.9135 | 0.1297 |

**T2 MET.** The middling setting forgets more often by **+0.2000**, against a two-proportion standard error of
**0.1043** -- **1.92 sigma**. That is above the registered 0.15 bar and a hair under the two-sigma line the rest of
this line uses, which is worth saying plainly rather than rounding up.

**T3 MET.** The open loop is not perfect either: **10 of 40**, a rate of **0.250** where `e327`'s five replicates
suggested 0.20. **Both five-replicate point estimates were low but right about the shape** -- 1 in 5 and 2 in 5
against 1 in 4 and 9 in 20 -- which is the useful thing a forty-replicate run does to a five-replicate one: it does
not overturn it, it prices it.

**T4 MET, and it is the claim that runs across all eighty replicates.** Every one of the **28** forgetting
replicates, at both strengths, has `learned` of **`[1.0, 1.0, 1.0]`**: they acquired all three tasks perfectly and
lost some of one afterwards. So the failure mode this whole thread measures is **retention and never acquisition**,
and it is not a replicate that failed to fit.

**And the accuracy moves with it.** 0.9625 against 0.9135, so the middling setting also reads **0.049 lower** --
this is the first setting in the thread where the loop costs level as well as retention, which is what `e326`'s
registration expected of every setting and found at none.

## 3. What it says

**A middling loop is worse than none, and the effect is at the edge of what forty replicates can resolve.** The
practical reading is that the feedback strength is not a resource to be tuned up but a hazard with a window: too
little and it does nothing (`e327` at 0.25 and 1.0 retained on every replicate of five), too much and the cue is
latched, and in between it perturbs the trajectory without holding it. That is a candidate a five-replicate grid
could not separate from a coin and forty replicates now separate at **1.92 sigma** -- which is not the same as
settled, and the run that settles it is the same design at 0.25 and 1.0, which this unit did not run.

**And the ceiling caveat of the whole thread is still in place.** Every replicate learns every task, so nothing here
speaks to acquisition; `e326` and `e327` both named a task whose read-out is not saturated as the missing
instrument, and it is still missing.

## 4. What it cannot do

**Two settings of four**: 0.25 and 1.0 remain at five replicates, so this settles 0.5 against 0.0 and cannot place
either of the other two. **1.92 sigma is not 2**: T2 clears the bar it registered and not the line the corpus
usually holds, and the honest interval is the difference plus or minus 0.10. **Forty replicates resolve a difference
of about 0.20 and not one of 0.10**, so a real but smaller dose effect would return as this unit's null. **One arm,
one circuit, one read-out width, one gain**: `replay` and the block arms are not run. **The threshold is a
convention**: 0.05 separates a forgetting replicate from a rounding artefact, and the counts would move a little at
a different one -- the replicates' own forgetting values are 0.0 or at least about 0.2, so the choice is not
load-bearing on this population. **And there is still no reward**: the label is the cue, delivered at step 0, and
the agent's action is an input rather than a decision.
