# Where in the pass the label sits: the placement is an axis, and its working end is the first trial

*2026-10-13. `experiments/e505_where_in_the_pass_the_label_sits.py` puts the cue the `label_first` clause names at
trial **0**, **1** and **2** of a three-trial pass -- **11**, **7** and **3** drive steps to the read -- and moves
nothing else. **VA1, VA2 and VA3 all MET**: the pass reads **0.8538**, **0.8392** and **0.8580** with the label at
trial **0** and falls to **0.3257**, **0.3069**, **0.3274** at trial **1** and **0.2566**, **0.2576**, **0.2542** at
trial **2**, the end-to-end move **+0.5816** to **+0.6038** at **66.33** to **88.97** sigma, and the label's own part
of the read falls **1.0571** to **0.0489** to **0.0314**.*

## 1. The runs and the instrument

`e497`'s own command with `--loop-label-at` in place of `--loop-label-first`, so the label-at-1 and label-at-2 runs are
the placement field apart from `e497`'s own over one pass, one read, one world and one boundary channel.

| the arm | the label at trial 0 | at trial 1 | at trial 2 | the last row, trial 0 | trial 1 | trial 2 |
|---|---|---|---|---|---|---|
| `naive` | **0.8538** | 0.3257 | 0.2566 | 0.6802 | 0.2969 | 0.2698 |
| `ewc-block` | **0.8392** | 0.3069 | 0.2576 | 0.7024 | 0.2823 | 0.2622 |
| `replay` | **0.8580** | 0.3274 | 0.2542 | 0.8108 | 0.3212 | 0.2503 |

and the paired contrasts over the twenty replicate seeds:

| the arm | trial 0 less trial 1 | sigma | trial 1 less trial 2 | sigma | trial 0 less trial 2 | sigma |
|---|---|---|---|---|---|---|
| `naive` | **+0.5281** | **+42.50** | **+0.0691** | **+6.68** | **+0.5972** | **+74.23** |
| `ewc-block` | **+0.5323** | **+43.67** | **+0.0493** | **+4.98** | **+0.5816** | **+66.33** |
| `replay` | **+0.5306** | **+48.61** | **+0.0733** | **+6.20** | **+0.6038** | **+88.97** |

and the label's own part of the read at the last step, at the card's own body with deterministic cues and the
episode's other symbols held fixed -- one width, one read, one world, three placements:

| the placement | the window in drive steps | the across-symbol spread | the read's own scale | the spread as a share of the scale |
|---|---|---|---|---|
| the label at trial **0** | **11** | 4.3099 | 4.0771 | **1.0571** |
| the label at trial **1** | **7** | 0.2078 | 4.2495 | **0.0489** |
| the label at trial **2** | **3** | 0.1332 | 4.2445 | **0.0314** |

| claim | measured | verdict |
|---|---|---|
| VA1 the flag moves the placement and nothing else | **0** config fields differing past the inert rule on each new run with `loop_label_first` and `loop_label_at` the fields moved, the draw adding `label_at` and dropping `label_first` with **0** fields outside the pair, and **20** replicates on each run | **MET** |
| VA2 the placement orders the pass | **3** of three arms non-increasing and **3** of three resolving: the diagonals fall **0.8538**, **0.8392**, **0.8580** to **0.3257**, **0.3069**, **0.3274** to **0.2566**, **0.2576**, **0.2542** against a chance of **0.25**, and the end-to-end move is **+0.5972**, **+0.5816** and **+0.6038** at **+74.23**, **+66.33** and **+88.97** sigma | **MET** |
| VA3 the label's window is what orders it | the shares fall **1.0571** at **11** drive steps to **0.0489** at **7** to **0.0314** at **3**, over the spreads **4.3099**, **0.2078** and **0.1332** | **MET** |

## 2. What it says

**The flag moves the placement and nothing else.** **0** config fields differing past the inert rule on either new
run, with `loop_label_first` and `loop_label_at` the fields moved; the draw adding `label_at` and dropping
`label_first` and moving **0** fields outside that pair; and **20** replicates on each run. **So the three points are
one configuration**, which is what makes the fall below the placement's and not something else's -- the environment's
draw for `e497`'s own run is unchanged field for field through the flag, and `e497`'s, `e500`'s and `e503`'s readings
re-read byte for byte.

**And the pass falls with the placement on every arm.** **3** of three arms are non-increasing from trial **0** to
trial **1** to trial **2**, and the end-to-end move is **+0.5972**, **+0.5816** and **+0.6038** at **+74.23**,
**+66.33** and **+88.97** sigma. **So the placement is an axis and not a pair**: the clause `e495` moved and `e496`
and `e497` wrote as the label's cue at the episode's first trial or its last sits on a graded line, and the pair's two
points are its ends.

**And the fall is a step at the first placement, not a gentle slope.** The drop from trial **0** to trial **1** is
**+0.5281** to **+0.5323** at **42.50** to **48.61** sigma, and the drop from trial **1** to trial **2** is only
**+0.0493** to **+0.0733** at **4.98** to **6.68** sigma -- and both interior placements, **0.2566** to **0.3274**,
sit at or within **0.08** of the four-class chance of **0.25**. **So the pass's usable end is the first trial**: with
the label at trial **1** the pass is worth **0.067** to **0.077** over chance, and with it at trial **2** it is
**0.004** to **0.008** over chance, so at three trials the two placements after the first are both at the floor and
what the pass teaches is nearly nothing. *What the interior is not: a graded descent. The three points are a step, and
whether a longer pass would put an interior placement above the floor is not in this unit.*

**And the label's window orders the share the same way.** Measured at the card's own body with deterministic cues and
the episode's other symbols held fixed, the label's own part of the read is **1.0571** with it at trial **0**,
**0.0489** at trial **1** and **0.0314** at trial **2** -- a drop of a factor of **21.6** over the first step and only
**1.56** over the second, over spreads of **4.3099**, **0.2078** and **0.1332**. **So the label's presence in the read
collapses as soon as a distractor arrives before it**: the share at trial **0** is the corpus's own single-trial
reading (a share above one is the case where the read *is* the label's response, `e495`), and the two placements that
put a cue ahead of the label leave it near nothing -- which is the same step the accuracy shows, in the instrument
that reads the label's own part of the read rather than the pass's outcome.

**And so the clause's pair is the working end of a step.** `e495` moved the label from the episode's last trial to
its first and got **0.82** to **0.83**; `e496` wrote that into the card as the placement the episode's label has to
be in; `e497` put a second distractor in the same window and it stayed a family. **This unit reads the axis under
that pair and finds the pair's own first point is the only working placement at three trials**: with the label at
trial **1** or trial **2** the pass is at the floor on all three arms. **So the clause's clause is a step whose
usable side is the pass's first trial**, and what the clause calls *the label first* is, at three trials, *the label
before every other cue*.

## 3. What it cannot do

- **Three placements are not a curve's shape**: trials **0**, **1** and **2** are three points, so a knee between them
  and a placement beyond the pass's own three trials are not in the unit.
- **And one episode length**: a three-trial pass of four steps, so the placement and the pass's length still move
  together -- trial **1**'s seven-step window is a placement in a three-trial pass, and what the label at trial **1**
  of a six-trial pass would do is a different unit.
- **And the label first and no cue before it are one flag**: the only placement with a share of **1.0571** is also the
  only placement with nothing before it, so nothing here separates the window from the label's position in the cue
  order.
- **And one read and one body**: the model's own thirty-two columns, which `e493` showed is the better of the
  corpus's two, at a body that has never been trained, so a share is where that body puts the label and the trained
  arms are the measurement.
- **And the payout is not on these runs**: the three commands carry no `--loop-reward`, so nothing here is read
  against the world's currency.
- **And one world, budget and seed stream**: the card's own setting with `--seed0 0`, so a second world and a second
  stream are not in it.

## RE-READ 2026-10-13

**The window and the position are separated, and it is the window that orders the pass.** This unit's *cannot do*
closed on *three placements is not a curve's shape* and *the placement and the pass's length still move together*.
`e506` adds the **four-trial** pass -- trials of three steps, the label at trial **0**, **1** and **2** with windows
**11**, **8** and **5** -- so this unit's window **7** and window **3** are joined by window **11** on a third pass
length and window **5** on a second. The two window-**5** placements, the corpus's two-trial label-last and a
four-trial pass with the label at trial **2**, read **0.3104**, **0.2944** and **0.3031** against **0.3031**,
**0.2986** and **0.2903**, differing by at most **0.0128** and inside the window-eleven family's own spread of
**0.0312**; the four-trial window-**8** point reads **0.3667**, **0.3580** and **0.3653** against this unit's own
window-**7** **0.3257**, **0.3069** and **0.3274**, and the label's own part of the read follows the window down
**1.0424** at **11** to **0.0878** at **8**, **0.0489** at **7**, **0.0374** at **5** and **0.0314** at **3**. **So
the axis this unit named as one is the window** -- the label's trial index is only how those drive steps are counted
at a given split -- and this unit's three placements stand.

## RE-READ 2026-10-14

**The curve this unit saw three points of is now read whole, and its own phrase was half right -- a step at the top
and a slope below it.** This unit's *cannot do* closed on *three placements is not a curve's shape*, `e506` added a
fourth pass length and found a knee at window **11**, and `e509` added the six-trial pass, so `e510` pools every
placement on disk and reads the ladder over **six** windows -- **11**, **9**, **8**, **7**, **5** and **3** -- with
eleven placements behind them. Read whole, the ladder is non-increasing on **3 of 3** arms (**0.8384** to **0.2566**
on `naive`, **0.8272** to **0.2576** on `ewc-block` and **0.8376** to **0.2542** on `replay`), and the floor windows
this unit's own window **3** belongs to -- **7**, **5** and **3** -- all sit within **0.10** of the four-class chance
of **0.25**. **And the fall is not one graded collapse**: the step from window **11** to window **9** carries
**0.599**, **0.620** and **0.582** of the whole fall from **11** to **3**, so the largest single step carries three
fifths of it while four of the five steps resolve. **So this unit's phrase "a step and not a slope" names the top
step and misses the slope**: the curve is a step into window **9** and a graded slope from **9** down to **3**, which
is what the three points this unit held (**11**, **7** and **3**) could not tell apart -- it saw the two ends and one
rung between them, and the rung it called the slope is the knee. This unit's own numbers stand.
