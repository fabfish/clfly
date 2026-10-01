# The ordering survives the loop

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive,ewc,ewc-block,ewc-block-rand,replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale
{0.0, 0.5}` -- 713 s and 751 s, read by `experiments/e331_the_ordering_under_the_loop.py`.*

## 1. The line's headline, asked on the instrument with headroom

`e276` read the strongest method contrast in this corpus -- `replay` against each penalty arm, paired over the same
replicates -- at **twelve** sigma. `e321` found it surviving the **order** inversion in sign and not in size. `e324`
found the **time axis** halving it and taking its strongest edge, against the size-matched random control, from 5.92
sigma to **0.92**. And since `e325` the thread has been building a **closed loop**, with every ordering question so
far asked on an environment whose cue is two fixed vectors -- which `e330` resolved as a property of that ceiling
rather than of the loop.

This asks the line's own question on the instrument `e329` built: five arms, on the **noisy eight-symbol**
environment where `naive` reads about 0.51 against a chance of 0.125, at feedback strength **0.0** and **0.5**, five
replicates each and the same seeds.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, all five arms at
five replicates in both runs, the environment draw identical in every field the strength does not name, and **no
unexpected config or environment difference**.

## 2. The contrast is larger here than on the sequence suite, and the loop leaves it alone

| arm | open accuracy | loop accuracy | Δ | σ | open forgetting | loop forgetting |
|---|---|---|---|---|---|---|
| `naive` | 0.5292 | 0.4931 | −0.0361 | 0.92 | 0.2188 | 0.2354 |
| `ewc` | 0.5069 | 0.4917 | −0.0153 | 0.45 | 0.2000 | 0.2063 |
| `ewc-block` | 0.5292 | 0.5417 | +0.0125 | 0.87 | 0.1958 | 0.1500 |
| `ewc-block-rand` | 0.5139 | 0.5333 | +0.0194 | 0.55 | 0.2146 | 0.2000 |
| `replay` | **0.6458** | **0.6361** | −0.0097 | 0.42 | **0.0354** | **0.0437** |

**T2 MET.** On the open loop `replay` is ahead of `ewc` by **+0.1389 at 4.95 sigma**, of `ewc-block` by **+0.1167
at 7.56** and of `ewc-block-rand` by **+0.1319 at 4.36**. **T3 MET.** On the closed loop: **+0.1444 at 5.65**,
**+0.0944 at 3.67** and **+0.1028 at 6.87**. Every contrast favours `replay` and every one resolves.

**T4 landed on its NULL**: the loop moves the mean margin by **−0.0153**, between the 0.01 falsifier and the 0.03
bar. So the loop **does not** do what the time axis did -- `e324` halved this contrast and took one edge below
resolution, and the loop leaves all three above 3.6 sigma.

**And the numbers put this environment between the other two.** `e324`'s sequence suite gave 2.49, 3.20 and 0.92
sigma; this gives 4.36 to 7.56; and `e276`'s twelve-sigma reading was on the read-out-32 frozen-bias family at forty
replicates. So the ordering is neither a property of the substrate alone nor a constant: it is **strongest where the
task has headroom and the suite has no time axis**, and its weakest reading in the corpus is the one taken on the
suite whose order was inverted.

**And the arm that wins does so by an order of magnitude in the other currency.** `replay`'s forgetting is
**0.0354 open and 0.0437 under the loop**, against **0.15 to 0.24** for every other arm -- a gap of about 0.16, six
to ten times the size of any accuracy contrast in the table, and it is not one of the four claims. That is recorded
here as a description taken after the registration and not as a tested claim, and it is the largest thing this unit
found.

## 3. What it says

**The closed loop is not the time axis.** The two manipulations this thread has put under the headline contrast have
opposite effects on it: a step-varying stimulus halves its margins and takes the weakest under the bar, and a closed
loop -- the agent's own action in its own input, rewriting a third to a half of the state -- moves the mean margin by
0.0153 and leaves every one of the three contrasts resolved above 3.6 sigma. What the loop changes is the
**individual arms' levels** (four of five move between 0.010 and 0.036, none resolved at five replicates) and not
the ordering between them.

**And the ordering's own size is a property of the suite.** `e324`'s finding was that a benchmark reporting this
contrast has to say which trial it means; this unit adds the other half -- it also has to say **which** suit, because
the same five arms on the same circuit at the same read-out give 2.5 to 7.6 sigma depending on what the task is.

## 4. What it cannot do

**Five replicates**, which put one standard error of a paired accuracy difference near 0.02, so T4 can resolve 0.03
and not much less and the three contrasts in T2 and T3 share `replay`'s replicates and are not independent. *Two of
the four settings*: strengths 0.25 and 1.0 are not run, and `e327` and `e328` are the standing evidence that the
strength is not a monotone knob. *One circuit, one read-out width, one noise level and one alphabet*: the noise and
the alphabet arrived together in `e329`, so which of them bought the headroom is not separated. *The forgetting gap
is a description*, taken after the registration, with no interval and no falsifier. *And there is still no reward*:
the label is the cue, delivered at step 0, and the agent's action is an input rather than a decision.
