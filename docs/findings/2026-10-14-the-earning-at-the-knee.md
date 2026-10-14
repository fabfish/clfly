# The earning at the knee of the window curve: the middle pass is where the world pays most and sits farthest from its target

*2026-10-14. `experiments/e511_the_earning_at_the_knee.py` runs `e500`'s own paid, label-first command with the pass
at **six trials** and the label at trial **1** -- window **9**, the knee `e510` read on the window curve -- as a
**meter** run and with `--loop-policy --loop-earn` added as an **earned** run, read against `e500`'s own learned pair
and `e507`'s own chance pair. **BA1 and BA2 MET and BA3 FIRED.** The pair is two flags apart -- **0** config fields
differing past the inert rule over **63**, the draw **28** fields with nothing differing, **20** replicates each --
and the world pays at the knee: the map ends above the identity on **60 of 60** replicates and the reward's diagonal
rises **+10.1920**, **+12.9132** and **+9.0252** on every arm at **+7.35**, **+6.75** and **+5.13** sigma. **BA3's
registered interval fired**: the meter's cells here run about **-47**, past `e507`'s about **-42**, and the gain
**+9.03** to **+12.91** is past `e507`'s **+5.94** to **+9.01** -- so the knee is the **largest** of the three points
and not between them, while its accuracy **0.4625** to **0.4951** is the one quantity that does sit between.*

## 1. The pair, the pass and the three points

Two new runs of `e500`'s own command with `--loop-episode 6 --loop-label-at 1` -- the meter run with `--loop-reward`
alone and the earned run with `--loop-policy --loop-earn` added -- one flag pair apart, each carrying **20**
replicates, read against each other and against `e500`'s own earned and meter runs on the learned, label-first,
two-trial pass and `e507`'s own on the chance, label-at-1, three-trial pass. The pass is **six trials** of **two**
steps with the label's cue at trial **1**, which leaves **nine** drive steps between that cue and the read: the window
`e510` pooled as the curve's knee.

The two currencies on the two new runs, with the map's distance from the identity:

| the arm | earned reward diagonal | meter reward diagonal | the gain | sigma | earned accuracy diagonal | meter accuracy diagonal | the change | sigma | the map's distance from the identity |
|---|---|---|---|---|---|---|---|---|---|
| `naive` | **-36.8929** | -47.0848 | **+10.1920** | **+7.35** | 0.4858 | 0.4899 | -0.0042 | -0.29 | 10.1270 |
| `ewc-block` | **-35.9345** | -48.8477 | **+12.9132** | **+6.75** | 0.4625 | 0.4743 | -0.0118 | -0.87 | 10.3238 |
| `replay` | **-36.3623** | -45.3876 | **+9.0252** | **+5.13** | 0.4951 | 0.4979 | -0.0028 | -0.17 | 9.6066 |

and the meter run reads `e509`'s own six-trial label-at-1 placement exactly -- **0.4899**, **0.4743** and **0.4979**
-- so the pass this unit pays inside is the pass `e510` pooled as window **9**, and the payout flag changes nothing
about it.

The three points the ablation has been read at, each cell in the order `naive` / `ewc-block` / `replay`:

| the point | the pass | the window | the accuracy | the meter's level | the gain | the map's distance from the identity |
|---|---|---|---|---|---|---|
| `e500` learned | two trials, label at trial 0 | **11** | 0.8281 / 0.8153 / 0.8247 | -6.0542 / -6.0070 / -6.1017 | +1.5086 / +1.4123 / +1.0722 | 5.8133 / 5.2579 / 6.7272 |
| **this unit, the knee** | six trials, label at trial 1 | **9** | **0.4858** / **0.4625** / **0.4951** | **-47.0848** / **-48.8477** / **-45.3876** | **+10.1920** / **+12.9132** / **+9.0252** | **10.1270** / **10.3238** / **9.6066** |
| `e507` chance | three trials, label at trial 1 | **7** | 0.3264 / 0.2993 / 0.2993 | -42.4450 / -43.4675 / -40.9544 | +7.6020 / +9.0113 / +5.9397 | 10.4934 / 10.5437 / 10.6945 |

the map's distance from the identity, per replicate, beside `e500`'s two-trial, `e501`'s three-trial and `e507`'s
chance earned runs:

| the arm | this unit's mean | its smallest replicate | replicates above zero | `e500`'s own mean | `e501`'s own mean | `e507`'s own mean |
|---|---|---|---|---|---|---|
| `naive` | **10.1270** | 7.3259 | **20 of 20** | 5.8133 | 5.3064 | 10.4934 |
| `ewc-block` | **10.3238** | 7.9173 | **20 of 20** | 5.2579 | 5.0752 | 10.5437 |
| `replay` | **9.6066** | 8.1312 | **20 of 20** | 6.7272 | 6.6939 | 10.6945 |

and the earned run's reward diagonal against its own last row, which is the payout's own shape:

| the arm | the earned reward diagonal | its last row | the contrast | sigma |
|---|---|---|---|---|
| `naive` | -36.8929 | -39.9742 | +3.0814 | +2.75 |
| `ewc-block` | -35.9345 | -36.3885 | +0.4540 | +0.46 |
| `replay` | -36.3623 | -36.7220 | +0.3596 | +0.38 |

| claim | measured | verdict |
|---|---|---|
| BA1 the pair is two flags apart | **0** config fields differing past the inert rule over **63** compared (`loop_policy` and `loop_earn` the two moved, `json_out` the bookkeeping), the draw **28** fields with **0** differing, **0** added and **0** missing, **20** replicates each; the pass is six trials with the label at trial **1**, window **9**, and the draw's `episode_len` **6** with `label_at` **1** | **MET** |
| BA2 the world pays at the knee | the map is above zero on **60 of 60** replicates, the smallest **7.3259**; the reward's diagonal is above the meter run's on **3 of 3** arms -- **+10.1920**, **+12.9132** and **+9.0252** at **+7.35**, **+6.75** and **+5.13** sigma, from **-36.89**, **-35.93** and **-36.36** against **-47.08**, **-48.85** and **-45.39** | **MET** |
| BA3 the earning is ordered by the meter's own distance and not by the pass's accuracy | the meter's level here is **-47.0848**, **-48.8477** and **-45.3876**, outside the interval between `e500`'s **-6.0542**, **-6.0070** and **-6.1017** and `e507`'s **-42.4450**, **-43.4675** and **-40.9544** on **3 of 3** arms; the gain **+10.1920**, **+12.9132** and **+9.0252** is outside `e500`'s **+1.5086**, **+1.4123** and **+1.0722** and `e507`'s **+7.6020**, **+9.0113** and **+5.9397** on **3 of 3** arms; the accuracy **0.4858**, **0.4625** and **0.4951** is between `e500`'s **0.8281**, **0.8153** and **0.8247** and `e507`'s **0.3264**, **0.2993** and **0.2993** on **3 of 3** arms | **FIRED** (the meter's level and the gain stand past the interval on every arm, not inside it; only the accuracy sits between) |

## 2. What it says

**The pair moves the two flags and the pass is the knee's pass.** **0** config fields differing past the inert rule
over the **63** the runs record, with `loop_policy` and `loop_earn` moved and `json_out` the bookkeeping; the draw
**28** fields with nothing differing, nothing added and nothing dropped; **20** replicates each. **And the meter run
reads `e509`'s own window-9 placement exactly** -- **0.4899**, **0.4743** and **0.4979** -- so the pass this unit
pays inside is the one `e510` pooled as the knee, and the payout flag changes nothing about it.

**And the world pays at the knee.** The map ends **7.3259** to **8.1312** from the identity it was handed, above
zero on **every one of the sixty** replicates, and what the world pays rises on **every arm**: **+10.1920**,
**+12.9132** and **+9.0252** at **+7.35**, **+6.75** and **+5.13** sigma, in cells running about **-47** on the meter
run. **So the payout reaches the map on the pass whose own read is neither learned nor at chance**, and the pass's
accuracy does not move (**-0.0042**, **-0.0118** and **-0.0028** against the meter run, none resolving).

**And the earning at the knee is the largest of the three points, so BA3's interval fired.** The meter's level here
is **-47.0848**, **-48.8477** and **-45.3876** -- past `e507`'s **-42.4450**, **-43.4675** and **-40.9544** on every
arm, further from the target than either of the other two points -- and the gain **+9.0252** to **+12.9132** is past
`e507`'s **+5.9397** to **+9.0113** on every arm. **So the knee is not between the learned pass and the chance pass
on either the world's own level or the earning**: it is beyond the chance pass on the far side, and the falsifier
BA3 registered fires on the meter's level and on the gain, with only the accuracy sitting between.

**And the ordering the claim named is the ordering the three points show.** Sorting the three points by the meter's
level, from the closest to the target to the furthest, the gain rises with every step on all three arms:

| the arm | `e500` learned | the knee | `e507` chance | the accuracy's own order |
|---|---|---|---|---|
| `naive` | **-6.0542** -> +1.5086 | **-47.0848** -> +10.1920 | **-42.4450** -> +7.6020 | 0.83, 0.49, 0.33 |
| `ewc-block` | **-6.0070** -> +1.4123 | **-48.8477** -> +12.9132 | **-43.4675** -> +9.0113 | 0.82, 0.46, 0.30 |
| `replay` | **-6.1017** -> +1.0722 | **-45.3876** -> +9.0252 | **-40.9544** -> +5.9397 | 0.82, 0.50, 0.30 |

The accuracy runs **0.83**, **0.49** and **0.30** across the same three points and orders the earning on no arm --
the knee reads the middle accuracy and takes the largest earning. **So the meter's own distance from the target
orders the earning at the three points the ablation has been read at, and the pass's accuracy does not**, which is
the direction BA3 was registered for; what fired is the stricter interval the claim also demanded, and it fired
because the knee's distance is not between the other two but beyond the further of them.

**And the knee's map travels as far as the chance pass's and about twice the learned passes'.** The map's distance
here is **10.1270**, **10.3238** and **9.6066**, against `e500`'s **5.8133**, **5.2579** and **6.7272** and
`e501`'s **5.3064**, **5.0752** and **6.6939** on the learned passes and `e507`'s **10.4934**, **10.5437** and
**10.6945** on the chance pass. **So the map's movement follows the meter's distance and not the accuracy either**:
the knee's accuracy (**0.49**) is between the other two points' (**0.83** and **0.33**) while its map is at the
chance pass's distance, about twice the learned passes'.

**And the payout's own shape is sharper here than at the chance pass and flatter than at the learned pass.**
Against its own last row the earned run's reward diagonal is **+3.0814** at **+2.75** sigma, **+0.4540** at
**+0.46** and **+0.3596** at **+0.38** -- one arm resolving, where on `e507`'s chance pass it was **+0.3379**,
**-0.1733** and **-1.6319** with nothing resolving and on `e500`'s learned pass **+0.7061** and **+0.7794** on two
arms. **So the diagonal's own lift sits between the two other points'**, which is the one ordering the knee does
satisfy on the payout's shape.

## 3. What it cannot do

- **Three points are not a curve.** The ablation is read at window **11** (`e500`'s learned pass), window **9** (this
  unit's knee) and window **7** (`e507`'s chance pass), and no pass between window **9** and window **11** or between
  window **9** and window **7** is paid here, so the shape of the earning against the window is read at three points
  and is not drawn.
- **And the three passes differ in the number of trials, the trial's length and the window at once.** Two trials of
  six steps, six trials of two steps and three trials of four steps, at windows **11**, **9** and **7**, so the
  meter's distance from the target, the pass's own difficulty and the trial's structure move together and the
  ordering this unit reads cannot separate them: a longer window and a shorter trial are one step here.
- **And the payout's own shape and the currency on the action are not on these runs.** The environment's own
  state-matching target rule, a linear read of the cue, so the reward `e502` reads on the agent's **action** is
  absent; the earned diagonal's lift over its own last row is carried as an extra reading and not as a claim, and a
  sparse or shaped reward is a different unit.
- **And the head is never paid.** The map the agent acts through is what the payout ascends, and the body's task loss
  is untouched, so an agent paid through its own head is a different unit.
- **And one world, one budget, one learning rate and one seed stream.** The card's own setting with `--lr 0.003` and
  `--seed0 0`, so a second world, a second budget, the swept ascent rate of `e504` and a second seed stream are not
  in it.

**Artifacts:** `runs/e511_the_earning_at_the_knee.json`, read from
`runs/e511_label_at1_episode6_reward_20reps.json`, `runs/e511_label_at1_episode6_reward_earn_20reps.json`,
`runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json`,
`runs/e498_earned_label_episode2_labelfirst_reward_20reps.json`, `runs/e507_label_at1_episode3_reward_20reps.json`,
`runs/e507_label_at1_episode3_reward_earn_20reps.json` and, as the map's neighbours,
`runs/e501_earned_label_episode3_labelfirst_reward_earn_20reps.json`.

## RE-READ 2026-10-14

**This document's three points are the ledger's first three, and the ordering it read them at is the corpus's own
ordering.** `e512` globs `runs/`, pairs every **meter** run with every run on its own pass that carries
`--loop-policy --loop-earn`, and pools **8** cells over **14** artifacts, this document's three among them: `e500`'s
learned window-**11** pass, this document's knee at window **9** and `e507`'s chance pass at window **7**. Ordering
all eight by the meter's own level, from the closest to the target to the furthest -- **-5.9440**, **-6.0542** (three
cells on one meter run), **-6.8857**, **-7.8884**, **-42.4450** and **-47.0848** on `naive` with the gains
**+1.4562**, **+1.3744** to **+1.5926**, **+1.9741**, **+4.0860**, **+7.6020** and **+10.1920** -- the gain is
non-decreasing with **0** inversions past the registered tolerance of **0.25** on all **3** arms. **So the ordering
this document read at three points is the ordering of the whole ledger**, and the five cells it could not see -- the
one-trial pass, `e501`'s three-trial pass at the same window, `e502`'s action currency and `e504`'s two swept ascent
rates -- sit where the ordering puts them.

**And the accuracy orders nothing across the ledger either.** Ordering the same eight cells by the `naive` arm's
accuracy diagonal, highest first, the gain is inverted on **3 of 3** arms, by **+2.5774** (`e502` against `e500`),
**+2.1119** (`e502` against `e488`) and **+2.5900** (this document's knee against `e507`'s chance pass) on the
`naive` arm. **So this document's *the accuracy runs 0.83, 0.49 and 0.30 across the same three points and orders the
earning on no arm* is what the whole corpus shows**: five of the eight cells lie inside **0.0282** of each other on
that arm, and the one this document read as the middle of the accuracy's own ladder is the second of the three
inversions.

**And the pass's own accuracies this document reported are the ledger's, and one of them is the ledger's exception.**
The ledger's fourth claim -- that no arm's accuracy contrast between the earned and the meter run resolves at two
sigma -- **fired**, on exactly one of its **24** cell-arms: `e507`'s `replay` arm at **-0.0281** and **-2.56** sigma,
which is the number this document's own table carries in the row above. This document's own arms stand as it read
them (**-0.0042**, **-0.0118** and **-0.0028**, none resolving, the largest **-0.87**), and the ledger puts the
corpus's one resolved accuracy loss at the chance pass's buffer arm and nowhere else.

**What this does not change.** This document's **BA3** registered an **interval** -- the meter's level and the gain
between `e500`'s and `e507`'s -- and it fired, because the knee's meter sits past the chance pass's and not between
the other two; the ledger reads the **ordering** and not the interval, so the two are not in conflict and the fired
falsifier this document reported is not re-read here. Its numbers, its pair and its three points stand as what it
measured.
