# The window at six trials: the six-trial pass reads its windows, and the nearest placement at window 7 is the same position

*2026-10-14. `experiments/e509_the_window_at_six_trials.py` adds the **six-trial** pass -- trials of **two** steps, the
label at trial **1**, **2** and **3**, windows **9**, **7** and **5** -- beside the eight placements `e506` read, so
window **7** is carried by two pass lengths and window **5** by three, and window **9** is new and sits between the
measured window **8** and window **11**. **YA1, YA2 and YA3 are MET and YA4 FIRED**: the six-trial window-**7**
placement reads **0.3122**, **0.3073** and **0.3045** against the three-trial window-**7** placement's **0.3257**,
**0.3069** and **0.3274**, gaps of **0.0135**, **0.0003** and **0.0229** inside the registered bound of **0.0312**,
and the six-trial window-**5** placement **0.3000**, **0.2920** and **0.3035** against the two- and four-trial
window-**5** placements, gaps of at most **0.0132**; the label's own part of the read falls **0.1935** at window **9**
to **0.0446** at **7** and **0.0398** at **5**; and the new window-**9** point reads **0.4899**, **0.4743** and
**0.4979**, inside the band window **8** and window **11** bound. **And YA4 fired**: the six-trial trial-**2**
placement reads **0.0142** from the four-trial trial-**2** placement (window **5**) and **0.0229** from the
three-trial window-**7** placement, so its nearest neighbour is a **same-position** placement and not its own
window's.*

## 1. The runs and the instrument

Three new runs of `e506`'s own command with `--loop-episode 6` and the placement moved -- `--loop-label-at 1`, `2` and
`3` -- one flag apart from each other and each carrying **20** replicates, at **1,984**, **2,001** and **2,003**
seconds of wall time (**33.07**, **33.35** and **33.38** minutes, **0.3** seconds over ninety-nine minutes in all).
Beside them every placement run the corpus already holds: `e495`'s two-trial pair, `e497`'s three-trial label-first,
`e505`'s label-at-1 and label-at-2 and `e506`'s four-trial three. Eleven placements.

The **extended window table**, every placement the corpus now holds, ordered by window:

| the placement | the pass | the label's trial | the window in drive steps | the cues after the label | `naive` | `ewc-block` | `replay` | the label's share |
|---|---|---|---|---|---|---|---|---|
| two trials, the label first | 2 | 0 | **11** | 1 | 0.8299 | 0.8139 | 0.8267 | **1.0551** |
| three trials, the label first | 3 | 0 | **11** | 2 | 0.8538 | 0.8392 | 0.8580 | **1.0571** |
| four trials, the label first | 4 | 0 | **11** | 3 | 0.8316 | 0.8285 | 0.8281 | **1.0151** |
| **six trials, the label at trial 1** | 6 | 1 | **9** | 4 | **0.4899** | **0.4743** | **0.4979** | **0.1935** |
| four trials, the label at trial 1 | 4 | 1 | 8 | 2 | 0.3667 | 0.3580 | 0.3653 | **0.0878** |
| **six trials, the label at trial 2** | 6 | 2 | **7** | 3 | **0.3122** | **0.3073** | **0.3045** | **0.0446** |
| three trials, the label at trial 1 | 3 | 1 | 7 | 1 | 0.3257 | 0.3069 | 0.3274 | **0.0489** |
| **six trials, the label at trial 3** | 6 | 3 | **5** | 2 | **0.3000** | **0.2920** | **0.3035** | **0.0398** |
| four trials, the label at trial 2 | 4 | 2 | 5 | 1 | 0.3031 | 0.2986 | 0.2903 | **0.0362** |
| two trials, the label last | 2 | 1 | 5 | 0 | 0.3104 | 0.2944 | 0.3031 | **0.0386** |
| three trials, the label at trial 2 | 3 | 2 | 3 | 0 | 0.2566 | 0.2576 | 0.2542 | **0.0314** |

and the same-window families, each read across the pass lengths that carry it, against the registered bound, which is
the largest spread the placements already on disk carry and comes out at **0.0312** (window **11**'s own):

| the window | the placements, by pass length and label trial | the pass lengths | the spread per arm | inside the registered bound |
|---|---|---|---|---|
| **11** | two, three and four trials at trial 0 | 3 | **0.0240**, **0.0253**, **0.0312** | this family **is** the bound |
| **9** | six trials at trial 1 | 1 | none -- a single pass length | not a test, the band below |
| 8 | four trials at trial 1 | 1 | none -- a single pass length | not a test |
| **7** | three trials at trial 1, six trials at trial 2 | 2 | **0.0135**, **0.0003**, **0.0229** | **yes**, 0.0229 under **0.0312** |
| **5** | two trials at trial 1, four trials at trial 2, six trials at trial 3 | 3 | **0.0104**, **0.0066**, **0.0132** | **yes**, 0.0132 under **0.0312** |
| 3 | three trials at trial 2 | 1 | none -- a single pass length | not a test |

and the three new runs' paired contrasts over the twenty replicate seeds, and their last rows:

| the arm | trial 1 less trial 2 (window 9 to 7) | sigma | trial 2 less trial 3 (window 7 to 5) | sigma | trial 1 less trial 3 (window 9 to 5) | sigma |
|---|---|---|---|---|---|---|
| `naive` | **+0.1778** | **+14.99** | **+0.0122** | **+0.96** | **+0.1899** | **+13.14** |
| `ewc-block` | **+0.1670** | **+21.88** | **+0.0153** | **+1.50** | **+0.1823** | **+17.37** |
| `replay` | **+0.1934** | **+16.01** | **+0.0010** | **+0.11** | **+0.1944** | **+16.34** |

| the placement | the window | `naive` | `ewc-block` | `replay` |
|---|---|---|---|---|
| **six trials, the label at trial 1** | **9** | **0.3809** | **0.3812** | **0.4632** |
| four trials, the label at trial 1 | 8 | 0.3503 | 0.3257 | 0.3552 |
| **six trials, the label at trial 2** | **7** | **0.2688** | **0.2701** | **0.2788** |
| three trials, the label at trial 1 | 7 | 0.2969 | 0.2823 | 0.3212 |
| **six trials, the label at trial 3** | **5** | **0.2663** | **0.2597** | **0.2785** |
| four trials, the label at trial 2 | 5 | 0.2910 | 0.2698 | 0.2670 |
| two trials, the label last | 5 | 0.2892 | 0.2802 | 0.2896 |

and the label's own part of the read at the last step, at the card's own body with deterministic cues and the
episode's other symbols held fixed -- one width, one read, one world, the six-trial placements beside their families:

| the placement | the window | the across-symbol spread | the read's own scale | the spread as a share of the scale |
|---|---|---|---|---|
| **six trials, the label at trial 1** | **9** | **0.8184** | **4.2303** | **0.1935** |
| four trials, the label at trial 1 | 8 | 0.3734 | 4.2530 | **0.0878** |
| **six trials, the label at trial 2** | **7** | **0.1877** | **4.2062** | **0.0446** |
| three trials, the label at trial 1 | 7 | 0.2078 | 4.2495 | **0.0489** |
| **six trials, the label at trial 3** | **5** | **0.1663** | **4.1833** | **0.0398** |
| four trials, the label at trial 2 | 5 | 0.1542 | 4.2632 | **0.0362** |
| two trials, the label last | 5 | 0.1648 | 4.2687 | **0.0386** |

| claim | measured | verdict |
|---|---|---|
| YA1 the three runs are one flag apart | **0** config fields differing past the inert rule on each of the three pairs over **61** compared (`json_out` and `loop_label_at` the inert fields), the draw differing in `label_at` alone with **0** added and **0** missing, **20** replicates each | **MET** |
| YA2 the six-trial pass reads what its windows predict | the six-trial window-**7** placement reads **0.3122**, **0.3073** and **0.3045** against the three-trial window-**7** placement's **0.3257**, **0.3069** and **0.3274**, the gaps **0.0135**, **0.0003** and **0.0229**; the six-trial window-**5** placement reads **0.3000**, **0.2920** and **0.3035** against two trials **0.3104**, **0.2944** and **0.3031** and four trials **0.3031**, **0.2986** and **0.2903**, the gaps **0.0104**, **0.0066** and **0.0132**; the largest gap at either window is **0.0229** against the registered bound of **0.0312** | **MET** |
| YA3 the label's share follows the same window | the six-trial shares fall **0.1935** at window **9** to **0.0446** at **7** and **0.0398** at **5**; window **7**'s family is **0.0446** against **0.0489** (a factor of **1.096**) and window **5**'s is **0.0398**, **0.0386** and **0.0362** (a factor of **1.099**), with **0** six-trial families outside the registered factor of **2** | **MET** |
| YA4 the window is not the position | the six-trial trial-**2** placement (window **7**) reads **0.0229** from the three-trial trial-**1** placement (window **7**) and **0.0142** from the four-trial trial-**2** placement (window **5**), so it is **nearer a same-position placement**; the window-**9** point is **0.4899**, **0.4743** and **0.4979**, inside the band window **8** bound below (**0.3667**, **0.3580**, **0.3653**) and window **11** above (**0.8139** to **0.8580**), on **3 of 3** arms | **FIRED** (the window-7 pair is **0.0229** apart, the same-position pair at four trials **0.0142**) |

## 2. What it says

**The flag moves the placement and nothing else.** **0** config fields differing past the inert rule on each of the
three pairs over the **61** the runs record, with `loop_label_at` the placement and `json_out` the bookkeeping; the
draw moving `label_at` alone with nothing added and nothing dropped; and **20** replicates on each run. **So the three
points are one configuration**, and the falls below are the placement's and not something else's.

**And the six-trial pass reads what its windows predict, at the two windows the corpus can test.** Window **7** is now
carried by two pass lengths -- three trials with the label at trial **1** and six trials with it at trial **2** -- and
they read **0.3257**, **0.3069** and **0.3274** against **0.3122**, **0.3073** and **0.3045**, the largest per-arm gap
**0.0229** and the other two under **0.0140**; window **5** is now carried by three -- two trials at trial **1**, four
at trial **2** and six at trial **3** -- and reads **0.3104**, **0.2944** and **0.3031**, **0.3031**, **0.2986** and
**0.2903** and **0.3000**, **0.2920** and **0.3035**, every gap at most **0.0132**. Both are inside the registered
bound of **0.0312**. **So the fourth pass length lands on the windows the other three named**, and the two windows
that were a single pass length in `e506` are now a family of two and a family of three.

**And the new window 9 lands where its neighbours bound it.** The six-trial label-at-1 reads **0.4899**, **0.4743**
and **0.4979** -- above the four-trial window-**8** point's **0.3667**, **0.3580** and **0.3653** and below the
window-**11** family's **0.8139** to **0.8580** on every arm. **So the ladder below the knee is not a step at window
8**: window **9** reads **0.49** where window **8** reads **0.36** and window **7** reads **0.31** to **0.33**, which
is the reading `e506` reached from the other side when it found window **8** above window **7** at the same position.
*And the six-trial pass has a knee of its own, one rung lower than the corpus's*: the six-trial fall from trial **1**
to trial **2**, window **9** to window **7**, is **+0.1670** to **+0.1934** at **16.01** to **21.88** sigma, while
window **7** to window **5** is not resolved.

**And the share instrument ranks the six-trial placements the same way the arms do.** **0.1935** at window **9**,
**0.0446** at **7** and **0.0398** at **5**, against **0.0878** at window **8**, and both same-window families inside
the factor of **2** -- window **7**'s **0.0446** against **0.0489** and window **5**'s three within **1.099** of each
other. **So the label's own part of the read is ordered by the window a fourth time**, and the window-**9** share
**0.1935** is the first rung above the knee below **11** that the instrument separates by more than the read's own
scatter.

**And the position is not shut out at window 7.** The six-trial trial-**2** placement reads **0.3122**, **0.3073** and
**0.3045**; the three-trial window-**7** placement reads **0.3257**, **0.3069** and **0.3274**, a largest per-arm gap
of **0.0229**; and the four-trial trial-**2** placement (window **5**) reads **0.3031**, **0.2986** and **0.2903**, a
largest per-arm gap of **0.0142**. **So on the nearest-neighbour reading the six-trial trial-2 placement sits with
the four-trial trial-2 placement and not with the three-trial trial-1 placement whose window it shares**, and the
unit's own discriminating test comes out against the window being the whole of it: the six-trial label-at-2 leaves
**three** cues after it where the three-trial label-at-1 leaves **one** and the four-trial label-at-2 leaves **one**,
so at this point the step of the trial and the step of the cue-count cannot be told apart. *What the two readings
together say*: window **7** is **0.0229** wide across its two pass lengths -- inside the bound -- and the placement is
**0.0142** from a window-**5** point at the same position, which is the smaller of the two. A window-only account and
a position-only account both survive window **7**; the unit separates them only where the two disagree, and there they
disagree in the position's favour.

**And the six-trial ladder's own step from window 7 to window 5 is not resolved.** Six trials at trial **2** less six
at trial **3** is **+0.0122**, **+0.0153** and **+0.0010** at **0.96**, **1.50** and **0.11** sigma, where the step
from trial **1** to trial **2** is **+0.1670** to **+0.1934** at **16.01** to **21.88** sigma. **So the six-trial pass
has the corpus's shape** -- a knee at the long window and a slope below it -- with windows **7** and **5** only a
hundredth or two apart.

## 3. What it cannot do

- **Four pass lengths, and still not a step of window separated from a trial**: two, three, four and six trials, with
  window **11** carried by three of them, window **5** by three and window **7** by two, while window **9** is a
  single pass length. The window is `11 - i * 12/N`, so a six-trial step is **two** drive steps and it also changes
  **how many cues follow the label** -- the six-trial label-at-2 leaves three cues after it where the three-trial
  label-at-1 leaves one -- and both of those move at once. What would separate a step's worth of window from a
  trial's is a twelve-step pass with a fixed trial length, and that is not measured here.
- **And windows 1 and 3 on the six-trial pass are not run**: the label at trial **4** and trial **5** would leave
  windows **3** and **1**, and window **1** is carried by nothing in the corpus. So the six-trial end of the ladder
  stops at window **5**, and window **9** is the only window the six-trial pass adds.
- **And the payout is not on these runs**: the three commands carry no `--loop-reward`, so nothing here is read
  against the world's currency. `e507` put the payout on one placement -- the three-trial label-at-1, window **7** --
  and what the other windows are worth to an agent that acts is a different unit. What this unit does say is that the
  window-7 family now has a second member, the six-trial label-at-2, so a paid run at that placement would be paid
  there beside a different pass length.
- **And one read and one body**: the model's own thirty-two columns, which `e493` showed is the better of the
  corpus's two, at a body that has never been trained, so a share is where that body puts the label and the trained
  arms are the measurement.
- **And one world, budget and seed stream, and three arms**: the card's own setting with `--seed0 0`, so a second
  world and a second stream are not in it, and a claim over three arms is not a claim about the world.
