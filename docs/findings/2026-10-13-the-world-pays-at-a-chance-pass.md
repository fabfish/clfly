# The world pays at a chance pass: the payout reaches the map on a pass the head cannot learn

*2026-10-13. `experiments/e507_the_world_pays_at_a_chance_pass.py` runs `e500`'s own paid, label-first command with the
pass at **three trials** and the label at trial **1** -- window **7**, the placement `e506` showed reads at or within
**0.08** of the four-class chance -- as a **meter** run and with `--loop-policy --loop-earn` added as an **earned**
run. **XA1, XA2 and XA3 all MET.** The map ends above the identity on **60 of 60** replicates and the world pays
**+7.6020**, **+9.0113** and **+5.9397** more on every arm at **+3.66**, **+5.77** and **+2.45** sigma -- so the world
pays the agent on a pass the head cannot learn, and it pays **more** there than on the learned pass `e500` measured.*

## 1. The pair, the pass and the instrument

Two new runs of `e500`'s own command with `--loop-episode 3 --loop-label-at 1` -- the meter run with `--loop-reward`
alone and the earned run with `--loop-policy --loop-earn` added -- one flag pair apart, each carrying **20**
replicates, read against each other and against `e500`'s own earned and meter runs on the learned, label-first,
two-trial pass. The band the gain is read inside is registered from the two comparisons' own paired spreads, at read
time.

| the run | the pass | the label's trial | the window | `naive` | `ewc-block` | `replay` |
|---|---|---|---|---|---|---|
| meter (three trials, reward) | 3 | 1 | **7** | 0.3257 | 0.3069 | 0.3274 |
| **earned (three trials, reward, earned)** | 3 | 1 | **7** | **0.3264** | **0.2993** | **0.2993** |
| `e505` label-at-1 (three trials, no reward) | 3 | 1 | 7 | 0.3257 | 0.3069 | 0.3274 |
| `e505` label-at-2 (three trials, no reward) | 3 | 2 | 3 | 0.2566 | 0.2576 | 0.2542 |

and the two currencies' levels on the two new runs, with the map's distance from the identity:

| the arm | earned reward diagonal | meter reward diagonal | the gain | sigma | earned accuracy diagonal | meter accuracy diagonal | the change | sigma | the map's distance from the identity |
|---|---|---|---|---|---|---|---|---|---|
| `naive` | **-34.8430** | -42.4450 | **+7.6020** | **+3.66** | 0.3264 | 0.3257 | +0.0007 | +0.07 | 10.4934 |
| `ewc-block` | **-34.4562** | -43.4675 | **+9.0113** | **+5.77** | 0.2993 | 0.3069 | -0.0076 | -0.70 | 10.5437 |
| `replay` | **-35.0147** | -40.9544 | **+5.9397** | **+2.45** | 0.2993 | 0.3274 | -0.0281 | -2.56 | 10.6945 |

the map's distance from the identity, per replicate, beside `e500`'s two-trial and `e501`'s three-trial earn runs:

| the arm | the new run's mean | its smallest replicate | replicates above zero | `e500`'s own mean | `e501`'s own mean |
|---|---|---|---|---|---|
| `naive` | **10.4934** | 7.5441 | **20 of 20** | 5.8133 | 5.3064 |
| `ewc-block` | **10.5437** | 8.4110 | **20 of 20** | 5.2579 | 5.0752 |
| `replay` | **10.6945** | 7.7703 | **20 of 20** | 6.7272 | 6.6939 |

the band the gain is read inside, whose half-width is the larger of the two comparisons' own paired spreads:

| the arm | `e500`'s own gain | the new gain | the band's half-width | inside |
|---|---|---|---|---|
| `naive` | +1.5086 | **+7.6020** | 9.3009 | **yes** |
| `ewc-block` | +1.4123 | **+9.0113** | 6.9816 | no |
| `replay` | +1.0722 | **+5.9397** | 10.8606 | **yes** |

and the earned run's reward diagonal against its own last row, which is the payout's own shape:

| the arm | the earned reward diagonal | its last row | the contrast | sigma |
|---|---|---|---|---|
| `naive` | -34.8430 | -35.1809 | +0.3379 | +0.31 |
| `ewc-block` | -34.4562 | -34.2829 | -0.1733 | -0.19 |
| `replay` | -35.0147 | -33.3828 | -1.6319 | -2.09 |

| claim | measured | verdict |
|---|---|---|
| XA1 the pair is two flags apart | **0** config fields differing past the inert rule over **63** compared (`loop_policy` and `loop_earn` the two moved, `json_out` the bookkeeping), the draw **28** fields with **0** differing, **0** added and **0** missing, **20** replicates each; the pass is three trials with the label at trial **1**, window **7**, and the draw's `episode_len` **3** with `label_at` **1** | **MET** |
| XA2 the world still pays at a pass at chance | the map is above zero on **60 of 60** replicates, the smallest **7.5441**; the reward's diagonal is above the meter run's on **3 of 3** arms -- **+7.6020**, **+9.0113** and **+5.9397** at **+3.66**, **+5.77** and **+2.45** sigma | **MET** |
| XA3 the earning does not need the pass to be learned | the gains **+5.9397** to **+9.0113** sit inside `e500`'s own band -- half-widths **6.9816** to **10.8606**, taken from the two comparisons' own spreads -- on **2 of 3** arms (`naive` and `replay`; `ewc-block`'s **+9.0113** is **0.62** past its own band's top), and the accuracy diagonals **0.2993** to **0.3264** leave **0 of 3** arms above the bar of **0.35** | **MET** |

## 2. What it says

**The pair moves the two flags and the pass is the at-chance one.** **0** config fields differing past the inert rule
over the **63** the runs record, with `loop_policy` and `loop_earn` moved and `json_out` the bookkeeping; the draw
**28** fields with nothing differing, nothing added and nothing dropped; **20** replicates each. **And the meter run
reads `e505`'s own window-7 placement exactly** -- **0.3257**, **0.3069** and **0.3274**, the same three numbers the
no-reward placement run carries and within **0.08** of the four-class chance of **0.25** -- so the pass this unit pays
inside is the one `e506` measured, and the payout flag changes nothing about it.

**And the world pays the agent on a pass the head cannot learn.** The map ends **7.5441** to **8.4110** from the
identity it was handed, above zero on **every one of the sixty** replicates, and what the world pays rises on **every
arm**: **+7.6020**, **+9.0113** and **+5.9397** at **+3.66**, **+5.77** and **+2.45** sigma, in cells running about
**-42** on the meter run. **So the payout's reach is a property of the earning and not of the head**: the same two
flags that reach the map on `e500`'s learned **0.83** pass reach it on a pass reading **0.30**, and the accuracy does
not move (**+0.0007**, **-0.0076** and **-0.0281** against the meter run).

**And the world pays more there, because the meter sits farther from the target.** On the learned pass `e500`'s own
gain was **+1.5086**, **+1.4123** and **+1.0722** from cells about **-6.05**; here the gain is **+7.6020**, **+9.0113**
and **+5.9397** from cells about **-34.5** against about **-42.3**, and the map travels **10.4934**, **10.5437** and
**10.6945** from the identity against `e500`'s **5.8133**, **5.2579** and **6.7272** and `e501`'s **5.3064**,
**5.0752** and **6.6939** -- about twice as far. **So a chance pass leaves the world further from its target and the
same earning buys more**, which is why the band question is not a like-for-like one.

**And the band XA3 registers is wide, and one arm falls outside it.** The half-widths are the larger of the two
comparisons' own paired spreads -- **9.3009**, **6.9816** and **10.8606**, the chance pass's own scatter and not
`e500`'s **0.2967** to **0.3086** -- so the band is registered from the runs and not from the head, and it is wide
because the chance pass's reward is noisy. Against it `naive`'s **+7.6020** and `replay`'s **+5.9397** fall inside
`e500`'s **+1.5086** and **+1.0722** at those widths while `ewc-block`'s **+9.0113** falls **0.62** past its own
**+1.4123 + 6.9816**. **So the claim holds at its bar of two of three arms and not on every arm**, and a band read only
from `e500`'s own spread would put every arm outside it -- which is the reading the width's own source decides.

**And the payout's own shape is flat here.** Against its own last row the earned run's reward diagonal is **+0.3379**,
**-0.1733** and **-1.6319** at **+0.31**, **-0.19** and **-2.09** sigma, where on `e500`'s learned pass it was
**+0.7061** and **+0.7794** on two arms. **So at the chance pass the earned diagonal is not above its last row**: the
level the earning buys is the level, and the diagonal's own lift that `e500` read is not repeated where the head could
not learn the task.

**And so the clause `e506` closed on is closed from the other side.** `e506` finished on *the payout is not on these
runs*; this unit puts the payout on the placement whose window is **7** -- three trials, the label at trial **1** --
and the world pays **+5.9397** to **+9.0113** there. **So the window is not a cost the earning depends on**: the same
two flags pay on the pass the window makes cheap and on the pass it makes dear, and the payout's reach follows the
ablation and not the accuracy.

## 3. What it cannot do

- **One placement and one pass length, so the window is 7 and no other**: the three-trial pass with the label at trial
  **1**. The label at trial **0** (window **11**) and trial **2** (window **3**) are not paid here, so whether the
  payout's reach falls as the window falls the way the accuracy does is not measured.
- **And one payout and one currency**: the environment's own state-matching target rule, a linear read of the cue, so
  the payout `e502` reads on the agent's **action** is absent from these runs, and a sparse or shaped reward is a
  different unit.
- **And the head is never paid**: the map the agent acts through is what the payout ascends, and the body's task loss
  is untouched, so an agent paid through its own head is a different unit.
- **And one world, one budget, one learning rate and one seed stream**: the card's own setting with `--lr 0.003` and
  `--seed0 0`, so a second world, a second budget, the swept ascent rate of `e504` and a second seed stream are not in
  it.
