# The shape of the window curve: a knee at the top and a graded slope below it, a floor at chance, and one step carrying three fifths of the fall

*2026-10-14. `experiments/e510_the_shape_of_the_window_curve.py` reads every placement run on disk -- `e495`'s,
`e497`'s, `e505`'s two, `e506`'s three and `e509`'s three -- pools each window's family, and characterises the curve
the window ladder draws. The corpus holds **eleven placements over four pass lengths** and **six windows**, ordered
**11**, **9**, **8**, **7**, **5** and **3**. **ZA1, ZA3 and ZA4 are MET and ZA2 FIRED**: every family is
non-increasing down the ladder on **3 of 3** arms with no rise past its window's own spread; the floor windows
**7**, **5** and **3** sit within **0.10** of the four-class chance of **0.25** on every arm while window **11**
sits at least **0.577** above it; the three multi-pass-length families are inside the registered **0.0312** and their
cue counts vary by two or more; but **the step into window 9 carries 0.599, 0.620 and 0.582 of the whole fall from
window 11 to window 3**, so no single adjacent fall carries under half and the fall is a knee at the top with a
graded slope below it, not a graded collapse.*

## 1. The runs and the instrument

**One reader, no training, no probe.** `e510` globs nothing: it names the eleven placement run files the corpus holds
and reads each arm's per-replicate accuracy diagonal, then pools a window's family by **replicate** -- at replicate
`r` the family's value on an arm is the mean over the family's placements of that placement's diagonal at replicate
`r`, and the family's pooled accuracy is the mean of those values over the twenty replicate seeds. An adjacent fall
between two neighbouring windows is the per-replicate difference of the two families' pooled values, and its sigma
is that difference's mean over its own standard error across the twenty seeds. A window carried by a single pass
length is one placement and is read as its own mean. The runs are the eleven placements, in the window each carries:

| the window | the family, by pass length and label trial | the pass lengths | the cues after the label | `naive` | `ewc-block` | `replay` | the family's spread per arm |
|---|---|---|---|---|---|---|---|
| **11** | two, three and four trials at trial 0 | 3 | 1, 2, 3 | **0.8384** | **0.8272** | **0.8376** | **0.0240**, **0.0253**, **0.0312** |
| **9** | six trials at trial 1 | 1 | 4 | **0.4899** | **0.4743** | **0.4979** | none -- a single pass length |
| **8** | four trials at trial 1 | 1 | 2 | **0.3667** | **0.3580** | **0.3653** | none -- a single pass length |
| **7** | three trials at trial 1, six trials at trial 2 | 2 | 1, 3 | **0.3189** | **0.3071** | **0.3160** | **0.0135**, **0.0003**, **0.0229** |
| **5** | two trials at trial 1, four trials at trial 2, six trials at trial 3 | 3 | 0, 1, 2 | **0.3045** | **0.2950** | **0.2990** | **0.0104**, **0.0066**, **0.0132** |
| **3** | three trials at trial 2 | 1 | 0 | **0.2566** | **0.2576** | **0.2542** | none -- a single pass length |

**The whole fall and its five steps.** The total fall from window **11** to window **3** is **0.5818** on `naive`,
**0.5696** on `ewc-block` and **0.5834** on `replay`. Each adjacent step, its paired sigma and its share of that
total:

| the adjacent pair | `naive` | `ewc-block` | `replay` | the three shares of the total | resolved on all three arms |
|---|---|---|---|---|---|
| **11** to **9** | +0.3485 at +33.41 sigma | +0.3529 at +38.92 sigma | +0.3397 at +30.83 sigma | 0.599 / 0.620 / 0.582 | yes |
| **9** to **8** | +0.1233 at +8.51 sigma | +0.1163 at +9.10 sigma | +0.1326 at +9.65 sigma | 0.212 / 0.204 / 0.227 | yes |
| **8** to **7** | +0.0477 at +3.48 sigma | +0.0509 at +3.30 sigma | +0.0493 at +3.99 sigma | 0.082 / 0.089 / 0.085 | yes |
| **7** to **5** | +0.0144 at +1.34 sigma | +0.0121 at +1.32 sigma | +0.0170 at +2.20 sigma | 0.025 / 0.021 / 0.029 | no |
| **5** to **3** | +0.0479 at +5.53 sigma | +0.0374 at +3.88 sigma | +0.0448 at +6.37 sigma | 0.082 / 0.066 / 0.077 | yes |

**The registered claims and their verdicts:**

| claim | measured | verdict |
|---|---|---|
| **ZA1** the curve falls in the window and does not rise | the pooled ladder is **0.8384**, **0.4899**, **0.3667**, **0.3189**, **0.3045**, **0.2566** on `naive`, **0.8272**, **0.4743**, **0.3580**, **0.3071**, **0.2950**, **0.2576** on `ewc-block` and **0.8376**, **0.4979**, **0.3653**, **0.3160**, **0.2990**, **0.2542** on `replay` -- non-increasing on **3 of 3** arms -- with **0** rises past a window's own family spread | **MET** |
| **ZA2** the fall is graded and not one step | **4** of **5** adjacent falls resolve on all three arms (**11** to **9**, **9** to **8**, **8** to **7** and **5** to **3**), above the bar of two, but the widest share is **0.6196** (the `ewc-block` **11** to **9** fall, against **0.599** on `naive` and **0.582** on `replay`) against the bar of **0.50** | **FIRED** (one step carries three fifths of the fall) |
| **ZA3** the curve's floor is the chance band | the floor families are window **7** **0.3189**, **0.3071**, **0.3160**, window **5** **0.3045**, **0.2950**, **0.2990** and window **3** **0.2566**, **0.2576**, **0.2542**, each within **0.10** of **0.25** on every arm (**0** outside), while window **11** is **0.5884**, **0.5772** and **0.5876** above chance | **MET** |
| **ZA4** the curve is a function of the window and not of the pass | the multi-pass-length families are window **11** **0.0240**, **0.0253**, **0.0312**, window **7** **0.0135**, **0.0003**, **0.0229** and window **5** **0.0104**, **0.0066**, **0.0132**, every arm inside the registered **0.0312** (**0** over it), and all **3** of the windows vary in the cues after the label (window **11** and window **7** by **1** to **3**, window **5** by **0** to **2**) | **MET** |

## 2. What it says

**The curve falls, and it does not rise anywhere.** Every family is non-increasing down the ladder on **3 of 3**
arms, and no rise clears a window's own family spread: **0.8384** to **0.2566** on `naive`, **0.8272** to **0.2576**
on `ewc-block` and **0.8376** to **0.2542** on `replay`, with each window's family below the one above it. **So the
window orders the whole ladder and not only the placements `e505`, `e506` and `e509` each held**, which is ZA1.

**And the fall is a knee with a graded slope, not a graded collapse.** The step from window **11** to window **9**
carries **0.599**, **0.620** and **0.582** of the entire fall from **11** to **3** -- three fifths of it in one
step -- while the four steps below share the rest, and **4 of the 5** adjacent falls resolve on all three arms. **So
ZA2's falsifier fires on the share and not on the resolution**: the curve is graded in the sense that four
neighbouring steps each resolve, and it is one step in the sense that the largest of them carries more than half.
*That is the shape `e506` named from the other side when it found a knee at window **11** and a slope below, and it
is the shape `e505` saw from three points when it called the curve "a step and not a slope": the corpus holds both
halves of that phrase, a step at the top and a slope under it.*

**And below the knee the curve flattens onto the chance band.** Windows **7**, **5** and **3** pool to **0.3189**,
**0.3045** and **0.2566** on `naive` (**0.3071**, **0.2950** and **0.2576** on `ewc-block`; **0.3160**, **0.2990**
and **0.2542** on `replay`), each within **0.10** of the four-class chance of **0.25** on every arm, while window
**11** pools to **0.83** to **0.84**, at least **0.577** above chance. **So the floor is the chance band and the knee
is the only place the pass reads above it**, which is ZA3; and the two lowest windows, **3** and **5**, are the two
whose pooled readings are closest together (**0.2566** and **0.3045**) as well as closest to chance.

**And the curve is a function of the window, not of the pass.** The three multi-pass-length families are inside the
registered **0.0312** -- window **11** across two, three and four trials, window **7** across three and six trials,
window **5** across two, four and six trials -- and every one of them varies in the cues that follow the label by
two or more. **So the same window read across pass lengths that move the trial's length, the label's index and the
number of cues after the label still lands in one place**, which is ZA4, and it is the same reading `e506` reached
for the two window-**5** placements, now carried over the whole ladder.

**And one step is the top and the top only.** The **11** to **9** fall is the largest of the five on every arm
(**0.3485**, **0.3529** and **0.3397**) and the **7** to **5** fall the smallest (**0.0144**, **0.0121** and
**0.0170**, and the one step that fails to resolve on all three arms). **So the curve's resolution is not uniform
either**: the two steps at the top resolve by tens of sigma, the middle steps by three to ten, and the flat step
inside the chance band by **1.3** to **2.2**, which is where a graded curve's own scatter is larger than its step.

## 3. What it cannot do

- **Eleven placements and six windows are not a dense curve.** The ladder's six windows are carried by eleven
  placements over four pass lengths, and the spacing is uneven -- **11**, **9**, **8**, **7**, **5**, **3**. The
  six-trial split alone admits windows **11**, **9**, **7**, **5**, **3** and **1**, so window **1** is reached by
  no run, and no pass length the corpus carries produces a window between **3** and **5** or beyond **11**. A curve
  read at six points, one of them carried by three pass lengths and three by one, is not a dense sampling of the
  window axis.
- **And a window's family is not an independent sample.** The pass lengths that carry one window share the same
  world, the same draw and the same twenty replicate seeds, so two placements at one window are two readings of one
  configuration and not two draws: a family spread is the scatter of one setting read twice, not a standard error,
  and the pooled family mean over three placements is not a mean over three independent measurements.
- **And the position is not fully separated from the window.** `e509`'s own nearest-neighbour test fired: the
  six-trial label-at-2 (window **7**) reads **0.0142** from the four-trial label-at-2 (window **5**) and **0.0229**
  from the three-trial label-at-1 (window **7**), so its nearest neighbour is a same-position placement and not its
  own window's. At window **7** the step of the trial and the step of the cue-count move together and cannot be told
  apart on these runs; this unit reads the ladder by window and does not settle that.
- **And the payout is not on these runs.** No placement command here carries `--loop-reward`, so nothing in this
  curve is read against the world's currency: the shape is the accuracy diagonal's, and what a window is worth to an
  agent that acts is a different unit.
- **And one read, one body, one budget and one seed stream.** The accuracy diagonals are the corpus's own card
  setting, at one circuit, one thirty-two-column head, one budget and `--seed0 0`, so a second world, a second
  stream, a wider or narrower head and a second budget are not in it, and a curve over one draw is one draw's.

**Artifacts:** `runs/e510_the_shape_of_the_window_curve.json`, read from
`runs/e495_earned_label_episode2_labelfirst_20reps.json`, `runs/e493_earned_label_episode2_modelread_20reps.json`,
`runs/e497_earned_label_episode3_labelfirst_20reps.json`, `runs/e505_label_at1_episode3_20reps.json`,
`runs/e505_label_at2_episode3_20reps.json`, `runs/e506_label_at0_episode4_20reps.json`,
`runs/e506_label_at1_episode4_20reps.json`, `runs/e506_label_at2_episode4_20reps.json`,
`runs/e509_label_at1_episode6_20reps.json`, `runs/e509_label_at2_episode6_20reps.json` and
`runs/e509_label_at3_episode6_20reps.json`.
