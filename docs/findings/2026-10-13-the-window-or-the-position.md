# The window or the position: the pass's cost is the label's window, and the position is a name for it

*2026-10-13. `experiments/e506_the_window_or_the_position.py` adds the **four-trial** pass -- trials of three steps,
the label at trial **0**, **1** and **2** with windows **11**, **8** and **5** -- beside every placement run on disk,
so window **11** is carried by three pass lengths and window **5** by two. **WA1, WA2 and WA3 all MET**: the two
window-**5** placements read **0.3104**, **0.2944** and **0.3031** (two trials, the label at trial **1**) against
**0.3031**, **0.2986** and **0.2903** (four trials, the label at trial **2**), differing by at most **0.0128** where
the window-eleven family's own spread is **0.0312**; the end-to-end move is **+0.5750**, **+0.5708** and **+0.5740**
at **+70.70**, **+52.45** and **+61.22** sigma; and the label's own part of the read falls **1.0424** at window **11**
to **0.0878** at **8**, **0.0489** at **7**, **0.0374** at **5** and **0.0314** at **3**.*

## 1. The runs and the instrument

Three new runs of `e497`'s own command with `--loop-episode 4` and the placement moved -- `--loop-label-at 0`, `1` and
`2` -- one flag apart from each other and each carrying **20** replicates, read beside every placement run the corpus
already holds: `e495`'s two-trial label-first, `e493`'s two-trial label-last, `e497`'s three-trial label-first and
`e505`'s label-at-1 and label-at-2.

| the placement | the pass | the label's trial | the window in drive steps | `naive` | `ewc-block` | `replay` | the label's share |
|---|---|---|---|---|---|---|---|
| two trials, the label first | 2 | 0 | **11** | 0.8299 | 0.8139 | 0.8267 | **1.0551** |
| two trials, the label last | 2 | 1 | 5 | 0.3104 | 0.2944 | 0.3031 | **0.0386** |
| three trials, the label first | 3 | 0 | **11** | 0.8538 | 0.8392 | 0.8580 | **1.0571** |
| three trials, the label at trial 1 | 3 | 1 | 7 | 0.3257 | 0.3069 | 0.3274 | **0.0489** |
| three trials, the label at trial 2 | 3 | 2 | 3 | 0.2566 | 0.2576 | 0.2542 | **0.0314** |
| **four trials, the label first** | 4 | 0 | **11** | **0.8316** | **0.8285** | **0.8281** | **1.0151** |
| **four trials, the label at trial 1** | 4 | 1 | **8** | **0.3667** | **0.3580** | **0.3653** | **0.0878** |
| **four trials, the label at trial 2** | 4 | 2 | **5** | **0.3031** | **0.2986** | **0.2903** | **0.0362** |

and the three new runs' paired contrasts over the twenty replicate seeds:

| the arm | trial 0 less trial 1 | sigma | trial 1 less trial 2 | sigma | trial 0 less trial 2 | sigma |
|---|---|---|---|---|---|---|
| `naive` | **+0.4649** | **+56.22** | **+0.0635** | **+5.51** | **+0.5285** | **+62.70** |
| `ewc-block` | **+0.4705** | **+38.78** | **+0.0594** | **+3.92** | **+0.5299** | **+64.59** |
| `replay` | **+0.4628** | **+33.77** | **+0.0750** | **+5.92** | **+0.5378** | **+55.32** |

and their last rows, beside the placements at the same windows:

| the placement | the window | `naive` | `ewc-block` | `replay` |
|---|---|---|---|---|
| two trials, the label first | 11 | 0.6514 | 0.6549 | 0.7917 |
| three trials, the label first | 11 | 0.6802 | 0.7024 | 0.8108 |
| **four trials, the label first** | **11** | **0.6375** | **0.6361** | **0.7670** |
| **four trials, the label at trial 1** | **8** | **0.3503** | **0.3257** | **0.3552** |
| three trials, the label at trial 1 | 7 | 0.2969 | 0.2823 | 0.3212 |
| two trials, the label last | 5 | 0.2892 | 0.2802 | 0.2896 |
| **four trials, the label at trial 2** | **5** | **0.2910** | **0.2698** | **0.2670** |
| three trials, the label at trial 2 | 3 | 0.2698 | 0.2622 | 0.2503 |

and the label's own part of the read at the last step, at the card's own body with deterministic cues and the
episode's other symbols held fixed -- one width, one read, one world, every placement:

| the placement | the window | the across-symbol spread | the read's own scale | the spread as a share of the scale |
|---|---|---|---|---|
| two trials, the label first | 11 | 4.2967 | 4.0724 | **1.0551** |
| three trials, the label first | 11 | 4.3099 | 4.0771 | **1.0571** |
| **four trials, the label first** | **11** | **4.1286** | **4.0670** | **1.0151** |
| **four trials, the label at trial 1** | **8** | **0.3734** | **4.2530** | **0.0878** |
| three trials, the label at trial 1 | 7 | 0.2078 | 4.2495 | **0.0489** |
| two trials, the label last | 5 | 0.1648 | 4.2687 | **0.0386** |
| **four trials, the label at trial 2** | **5** | **0.1542** | **4.2632** | **0.0362** |
| three trials, the label at trial 2 | 3 | 0.1332 | 4.2445 | **0.0314** |

| claim | measured | verdict |
|---|---|---|
| WA1 the three runs are one flag apart | **0** config fields differing past the inert rule on each of the three pairs over **61** compared (`json_out` and `loop_label_at` the inert fields), the draw differing in `label_at` only with **0** added and **0** missing, **20** replicates each | **MET** |
| WA2 the read is a function of the window and not of the position | the same-window spreads are window **11** **0.0240**, **0.0253** and **0.0312** across its three pass lengths and window **5** **0.0073**, **0.0042** and **0.0128** across its two, with **0** arm-windows over the registered bound of **0.0312** (window 11's own), and the end-to-end move, four trials at window **11** less three trials at window **3**, is **+0.5750**, **+0.5708** and **+0.5740** at **+70.70**, **+52.45** and **+61.22** sigma, resolving on **3** of three arms | **MET** |
| WA3 the label's share follows the window | the window-mean shares fall **1.0424** at window **11** to **0.0878** at **8**, **0.0489** at **7**, **0.0374** at **5** and **0.0314** at **3**, with **0** same-window families outside the registered factor of **2** (window 11's own ratio **1.0414**, window 5's **1.066**) | **MET** |

## 2. What it says

**The flag moves the placement and nothing else.** **0** config fields differing past the inert rule on each of the
three pairs over the **61** the runs record, with `loop_label_at` the placement and `json_out` the bookkeeping; the
draw moving `label_at` alone with nothing added and nothing dropped; and **20** replicates on each run. **So the three
points are one configuration**, and the falls below are the placement's and not something else's.

**And the read is a function of the window, not of the position.** The two placements at window **5** are as different
as the unit can make them: a **two-trial** pass with the label at trial **1** (one cue before it, one after) and a
**four-trial** pass with the label at trial **2** (two cues before it, one after). They read **0.3104**, **0.2944**
and **0.3031** against **0.3031**, **0.2986** and **0.2903** -- differing by at most **0.0128**, inside the window-
eleven family's own spread of **0.0312** and a factor of two and a half smaller. **So the position is a name for the
window**: the label's trial, the pass's length and the number of cues before the label all move between those two
points, and the pass reads the same place. *And the window carries the whole of it on the largest family too*: window
**11** is three pass lengths at three different trials of the pass's own order and reads **0.8299** to **0.8580**,
inside its own **0.0312**.

**And the window orders the read even where the position is held.** The four-trial label-at-1 has window **8** and the
three-trial label-at-1 has window **7** -- the same position in the pass's order, one cue before the label in both --
and the four-trial point reads **0.3667**, **0.3580** and **0.3653** against **0.3257**, **0.3069** and **0.3274**, a
rise of **+0.0379** to **+0.0511**. **So where the position is held and the window is not, the read follows the
window**, which is the same reading the two window-5 points give from the other side.

**And the ladder is a knee at the largest window, then a slope.** The three new runs fall from trial **0** to trial
**1** by **+0.4628** to **+0.4705** at **33.77** to **56.22** sigma, and from trial **1** to trial **2** by only
**+0.0594** to **+0.0750** at **3.92** to **5.92** sigma; the end-to-end move is **+0.5750** to **+0.5740** at
**52.45** to **70.70** sigma. **So the knee `e505` found at three trials is the knee at four**: window **11** reads
**0.83** and windows **8**, **7**, **5** and **3** read **0.26** to **0.37**, with a slope of four to seven hundredths
between the windows below the knee. *What the knee is not: a step at a window.* Window **8** reads **0.36** and window
**3** reads **0.26**, so the windows below **11** are graded even where the pass is nearly at the four-class chance of
**0.25**.

**And the label's own part of the read follows the window down.** **1.0424** at window **11** (across the three pass
lengths, **1.0151** to **1.0571**), **0.0878** at **8**, **0.0489** at **7**, **0.0374** at **5** and **0.0314** at
**3**, over spreads of **4.1286** to **4.3099** at the knee and **0.1332** to **0.3734** below it. **So the instrument
that reads the label's own part of the read ranks the windows the same way the trained arms rank them, and both
same-window families agree inside the factor** -- window **11**'s three placements within **1.0414** of each other and
window **5**'s two within **1.066** -- which is the second reading under WA2. *And the share is graded where the
accuracy is thin*: window **8**'s share **0.0878** is above window **7**'s **0.0489**, the one place the window below
the knee separates two adjacent windows by more than the read's own scatter.

**And so the axis `e505` left one is the window, and the clause's clause is drive steps.** `e495` said the pass's cost
was the label's window; `e505` found the placement an axis and its working end the first trial, and left the window and
the position one movement because three trials carry one window each. **This unit puts the window behind more than one
pass length** -- window **11** on two, three and four trials and window **5** on two and four -- **and the pass reads
by the window and not by the position**: the two window-5 points agree to **0.0128**, the window-11 family to
**0.0312**, and the whole fall is **+0.5708** to **+0.5750** from window **11** to window **3**. **So what the pass
needs is 11 - i * 12/N drive steps** between the label's cue and the read, and the label's trial index is only how
those steps are named at a given split.

## 3. What it cannot do

- **Four pass lengths at most, three of them sharing one window**: two, three and four trials, with window **11**
  carried by three of them and window **5** by two, so window **8**, window **7** and window **3** are each a single
  pass length -- a placement and not a test -- and the six-trial split and the placements beyond each pass's own trials
  are not in it.
- **And the pass's length and the trial's length move together**: the pass is twelve steps, so a pass of `N` trials has
  trials of `12/N` steps and the label at trial `i` leaves `11 - i * 12/N` drive steps. Window **8** is trial **1** of
  four trials and window **7** is trial **1** of three, and both put exactly one cue before the label, so the two
  differ in the window and in the trial's length at once; **what would separate a step's worth of window from a
  trial's worth is a twelve-step pass with a fixed trial length, and that is not measured here.**
- **And no window between eight and eleven, and none beyond eleven**: the windows the corpus and these runs hold are
  **3**, **5**, **7**, **8** and **11**, so where the knee sits between **8** and **11**, and whether a window longer
  than **11** reads higher, are not in it.
- **And the payout is not on these runs**: the three new commands carry no `--loop-reward`, so nothing here is read
  against the world's currency.
- **And one read and one body**: the model's own thirty-two columns, which `e493` showed is the better of the corpus's
  two, at a body that has never been trained, so a share is where that body puts the label and the trained arms are the
  measurement.
- **And one world, budget and seed stream**: the card's own setting with `--seed0 0`, so a second world and a second
  stream are not in it.

## RE-READ 2026-10-13

**The payout is put on the placement this unit left at chance, and the window's own read is what is paid.** This
unit's *cannot do* closed on *the payout is not on these runs*; `e507` takes the three-trial pass with the label at
trial **1** -- this unit's own window **7** -- and runs `e500`'s paid command there. The meter run reads this unit's
**0.3257**, **0.3069** and **0.3274** exactly, and the earned run lifts the reward's diagonal by **+7.6020**,
**+9.0113** and **+5.9397** at **+3.66**, **+5.77** and **+2.45** sigma, with the map above the identity on **60 of
60** replicates at a mean distance of **10.4934**, **10.5437** and **10.6945** and the accuracy unchanged to
**0.0281**. So the window this unit reads as the pass's cost is where the world pays, and the earning there is larger
than on the learned label-first pass, where `e500`'s own gain was **+1.07** to **+1.51**. This unit's numbers stand.
