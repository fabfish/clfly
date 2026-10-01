# The cost needs the ceiling

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 40
--methods naive --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale {0.0, 0.5}` -- 729 s and 785 s, read by
`experiments/e330_the_cost_needs_the_ceiling.py`.*

## 1. The fork `e329` named, taken

`e328` put the middling feedback strength at **1.92 sigma** on forty replicates of the **easy** environment, whose
cue is two fixed vectors in twelve cue neurons: every arm solved every task there, and the only quantity left to
move was **whether a replicate forgot at all**. `e329` then built the instrument that environment lacked -- eight
cue symbols per task and a noise of 1.0, so `naive` reads 0.5292 against a chance of 0.125 -- and at **five**
replicates saw **nothing reproduce**: `naive`'s accuracy fell by 0.0361 at 0.92 sigma, `ewc-block` read higher under
the loop, and neither arm resolved on either quantity. Its finding named the fork and priced it: *the effect is not
there on a task with headroom, or five replicates cannot see it*, with the honest interval being the difference plus
or minus 0.039.

This takes the fork at the same **forty** replicates `e328` used, for `naive` only, on the **noisy eight-symbol**
environment. The arithmetic is why: `e329`'s five-replicate standard error of 0.039 falls to about **0.0115**, so an
effect of the size that unit saw would land near **3.1 sigma** if it were there.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, forty replicates
each, the environment draw identical in every field the strength does not name (24 symbols, twelve cue neurons,
noise 1.0, gain 1.0, the same three population fingerprints), and **no unexpected config or environment difference**.

**T4 MET, and it is what makes T2's answer an answer.** The instrument still has headroom: `naive`'s open-setting
accuracy is **0.5104** against a chance of **0.125**, per-replicate sd **0.0404**.

## 2. The effect is not there

| quantity | open (0.0) | middling (0.5) | Δ | sem | σ |
|---|---|---|---|---|---|
| `naive` accuracy | 0.5104 | 0.5172 | **+0.0068** | 0.0115 | **0.59** |
| `naive` forgetting | 0.2289 | 0.2169 | −0.0120 | 0.0156 | 0.77 |

**T2 landed on its NULL.** The registered claim was that the middling setting reads at least **0.02 lower**; it
reads **0.0068 higher**, at 0.59 sigma. **T3 MET** -- the two settings differ by 0.0120 of forgetting, inside the
0.04 band.

**So the fork is resolved, and it resolves to the first branch: the effect is not there.** That is not an absence of
evidence, because the design has the power to say so -- at a standard error of **0.0115**, an accuracy effect of the
size `e329`'s five replicates suggested (0.0361) would have appeared at **3.1 sigma**, and one of `e328`'s
forget-rate size would have been visible as a forgetting shift far outside the 0.04 band. Instead both quantities
sit within a sigma of zero, with the accuracy leaning the **other** way.

**And the controlled comparison is exact.** The only field that differs between the two runs is the feedback
strength; the circuit, the read-out draw, the task names, the seeds, the cue templates, the noise, the action
population and the feedback population are the same objects in both. So this is not two settings of two
environments: it is `e328`'s middling setting, asked on `e329`'s task.

## 3. What it says

**`e328`'s middling-loop cost is a property of the ceiling and not of the loop.** On a task every arm solves
perfectly, the middling setting roughly doubled the rate at which replicates forgot anything; on a task with room
under the ceiling, at four times the power, it moves neither level nor retention.

The natural reading is that **a task that is already solved has no slack**: a perturbing feedback channel cannot
cost anything in accuracy, because accuracy is pinned at one, so whatever damage it does has to show up as retention
-- which is exactly the shape `e328` measured, a forgetting rate and no accuracy effect. Put the same loop on a task
where the body is still learning, and the perturbation is absorbed by the fit.

**What that means for the thread is a caution about its own instruments.** Every loop result before `e329` was
measured on the saturated environment, and this is the first one that is not: the two agree on nothing, and the
saturated one is the one whose numbers are quoted. A claim about what a closed loop costs in this benchmark has to
name which task it was measured on, which is the same sentence `e324` reached from the other direction when the
sequence suite's accuracy fell by 0.21 and its forgetting did not rise.

## 4. What it cannot do

**One arm.** `ewc-block`, `replay` and the block arms are not run, and `e329`'s only resolved lean was
`ewc-block`'s, backwards at 1.44 sigma -- so whether a penalty changes this is exactly the question this unit cannot
answer. *Two settings of four*: 0.25 and 1.0 are not run. *Forty replicates put the accuracy standard error at 0.0115
and the forgetting one at 0.0156*, so a real effect of 0.02 on either quantity would return as this unit's null, and
T3's 0.04 band is about two and a half of those. *The two claims rest on the same forty runs*: accuracy and
forgetting correlate within a replicate, so they are not two independent tests. *The environment has one noise
level, one alphabet and one cue width*, none swept, and the noise and the alphabet arrived together in `e329`. *And
there is still no reward*: the label is the cue, delivered at step 0, and the agent's action is an input rather than
a decision.
