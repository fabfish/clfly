# Is it the body: freezing the recurrent weights recovers 0.2156 at 229 sigma, and the readable-but-not-learnable gap turns out to have two halves

*2026-10-03. `experiments/e375_is_it_the_body.py` runs the same cell `e374` trained -- the action source at `cue@8`,
the last step `e368`'s curve says both channels are alive -- with `--frozen-body`, so the gradient stops at the head
and the recurrent weights stay at their connectome initialisation. Same optimizer, same 500 iterations, same twenty
seeds. 1081 s; the reader is `runs/e375_is_it_the_body.json`. Five claims, registered before the run's reading was
opened.*

## 1. The result

| body | arm | diagonal | forgetting | paired channel |
|---|---|---|---|---|
| **frozen** | naive | **0.4490** | **0.0000** | **+0.2128** (204.33 sigma) |
| **frozen** | replay | 0.4472 | **0.0000** | +0.2111 (180.32 sigma) |
| plastic | naive | **0.2333** | -0.0094 | -0.0083 (0.92 sigma) |
| plastic | replay | 0.2431 | -0.0125 | +0.0017 (0.19 sigma) |

chance 0.2500. The probe on the **same frozen body** reads **0.7617** (`e368`).

| claim | measured | verdict |
|---|---|---|
| U1 one configuration except the body | fields differing `{'frozen_body': [True, False]}` and nothing else | **MET** |
| U2 the world is live at this step | `e368`'s cell at **+0.5117** over chance, spread **0.0478** | **MET** |
| U3 a frozen body still trains | **+0.1990** over chance | **MET** |
| U4 the body's own training is what loses it | **+0.2156** on a sem of **0.0009**, **229.59 sigma** paired | **MET** |
| U5 the answer is earned with the body frozen | **+0.2128 at 204.33 sigma** and **+0.2111 at 180.32 sigma** | **MET** |

**So the account's first half is confirmed and by a wide margin.** `e374` found the frozen body readable at 0.7617
where the plastic body trained to chance, and named the body's own training as the candidate. Freezing it is worth
**+0.2156**, and the two arms tell the rest of the story: with the body frozen the paired channel is **+0.2128** in
both, so the answer is coming through the loop rather than being read off a static body, while the plastic run's
channel is **-0.0083**, nothing. The same cell, the same budget and the same seeds: what changes is whether the
recurrent weights are allowed to move.

**The 229 sigma is a paired statistic and the per-replicate spread is what it is.** The frozen body's diagonal has a
standard deviation of **0.0047** across the twenty replicates and the plastic one's **0.0057**; the paired difference
has a sem of **0.0009** because the two move together across seeds -- both are dominated by the same evaluation
noise, so pairing removes it. Reported so that the sigma is read as the design it is and not as a claim that each
replicate is that precise.

## 2. The gap has two halves, and this unit only explains one

**The frozen body does not give the probe's number back.** A trained head on the frozen body reads **0.4490**; the
closed-form least-squares probe on the same frozen body reads **0.7617**. So the readable-but-not-learnable gap of
**0.5284** between the probe and the plastic body splits into:

- **0.2156** that the body's own training costs -- this unit's U4, measured, paired at 229 sigma;
- **0.3127** that a trained head still loses to a probe **on the same frozen body** -- reported, not claimed, since
  a trained head under SGD and a closed-form least-squares fit are different instruments and this unit registered no
  bar between them.

So the account `e374` named is **half right**: the body's plasticity is what destroys the reading, and it is not the
whole of what the probe has. A trained head recovers **59%** of it. That second half is the more interesting one for
anyone who wants the game to be playable: it says that even with the body held still, this task is read better by a
decoder fitted in closed form than by a head trained with the same objective and budget.

## 3. What else fell out

**A frozen body forgets exactly nothing, again.** Both frozen arms record `mean_forgetting` of **0.0000** to four
decimals, on a three-task sequential suite, in a closed loop, at twenty replicates. That is `e358`'s finding -- *all
the forgetting is the body's* -- arriving on a different task, a different reading and a different drive source:
what this corpus measures as interference is entirely in the recurrent weights, and the moment they are held the
interference is exactly zero rather than merely small.

**And the frozen body is more stable than the plastic one.** Its per-replicate standard deviation is **0.0047**
against the plastic **0.0057** for `naive`, and the two arms land **0.0018** apart (0.4490 against 0.4472) where the
plastic arms land **0.0098** apart. Reported, not claimed: with the body fixed the only thing a replicate can vary
is the head, so this is closer to a check that the head is being fitted reproducibly than to a finding about the
buffer.

## 4. What it cannot do

*One cell and one draw*: `cue@8` on this draw, so nothing here says whether a frozen body recovers more or less of
the probe at `cue@0` or at the boundary, where `e370` showed the boundary itself moves. *And freezing is a
diagnostic*: `--frozen-body` stops the gradient at the head, so this run answers what the plastic one would have
done with the same budget; it does not identify the representation the probe is using, and a positive U4 is evidence
that plasticity matters and not a demonstration of which quantity it moved. *And the probe's 0.7617 is not paired*:
one roll of 512 examples against twenty replicates, so the 0.3127 half of the split carries that grid's precision
and not this unit's. *And the second half is named and not tested*: whether a trained head can be made to match a
closed-form probe on a frozen body -- more iterations, a different head or a different optimizer -- is a unit of its
own.
