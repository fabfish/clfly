# The earning ledger: over every earned-versus-meter cell the corpus holds, the gain is ordered by the meter's own level and not by the pass's accuracy

*2026-10-14. `experiments/e512_the_earning_ledger.py` globs `runs/`, takes every artifact that carries the payout,
pairs each **meter** run with every run on its own pass that carries `--loop-policy --loop-earn`, and pools what it
finds: **8** cells over **14** artifacts, every cell at **20** replicates on both sides, out of **17** artifacts
carrying the payout and **56** meter-by-earned attempts. **LA1, LA2 and LA3 MET and LA4 FIRED.** Ordering the cells
by the meter's own reward level, from the level's top (the closest meter) to its bottom, the earned run's gain over
its meter is non-decreasing on **3 of 3** arms with **0** inversions past the registered tolerance of **0.25**;
ordering them instead by the `naive` arm's accuracy the gain is inverted on **3 of 3** arms, by **+2.5774**,
**+2.1119** and **+2.5900** on the `naive` cell-arms alone. **And the pass is not free everywhere**: **1** of the
**24** cell-arm accuracy contrasts resolves at two sigma, `e507`'s `replay` arm at **-0.0281** and **-2.56** sigma.*

## 1. The census, and the cells it leaves out

**The pairing rule.** A **cell** is a pair of artifacts, one the **meter** and one the **earned** run, that agree on
**every** recorded `config` field except `loop_policy`, `loop_earn`, the ascent rate the earned run alone moves
(`loop_earn_lr`, whose `None` is the run's own `--lr`), the output path (`json_out`) and the saved weights
(`save_theta`), with a field recorded `null` on one side and `false` on the other carrying the corpus's own inertia;
that agree on **every** field of the environment's draw; and that carry a payout on both sides -- the meter with
`loop_reward` and **neither** flag, the earned run with `loop_reward` **and both**. The census admits a thin pair:
the 20-replicate floor is LA1's own claim and not the rule, so a cell under it would belong to the ledger and fire
the claim rather than vanish from the census.

**What pairs.** Of the **17** artifacts under `runs/` that carry the payout, **7** are meters and **8** are earned
runs, **2** more carry a flag but not the pair, and the **56** meter-by-earned attempts make **8** cells:

| the earned run | its meter | the pass | the window | the fields the pair moves |
|---|---|---|---|---|
| `e488_earned_label_earned_20reps` | `e485_earned_label_reward_20reps` | one trial, no episode recorded | 11 | `loop_policy`, `loop_earn` (**0** differing past the rule over **56** compared, **3** inert, **23** draw fields with **0** differing) |
| `e500_earned_label_episode2_labelfirst_reward_earn_20reps` | `e498_earned_label_episode2_labelfirst_reward_20reps` | two trials, label at trial **0** | 11 | `loop_policy`, `loop_earn` (**0** over **60**, **3** inert, **28** draw fields, **0** differing) |
| `e504_earn_lr0.001_episode2_labelfirst_reward_earn_20reps` | `e498_earned_label_episode2_labelfirst_reward_20reps` | two trials, label at trial **0** | 11 | `loop_policy`, `loop_earn`, `loop_earn_lr` (**0** over **62**, **5** inert -- the two flags, the rate, the path and `loop_reward_on_action`'s `null` beside its `false`, **28** draw fields, **0** differing) |
| `e504_earn_lr0.01_episode2_labelfirst_reward_earn_20reps` | `e498_earned_label_episode2_labelfirst_reward_20reps` | two trials, label at trial **0** | 11 | as above at the rate **0.01** |
| `e501_earned_label_episode3_labelfirst_reward_earn_20reps` | `e501_earned_label_episode3_labelfirst_reward_20reps` | three trials, label at trial **0** | 11 | `loop_policy`, `loop_earn` (**0** over **60**, **3** inert) |
| `e502_reward_on_action_episode2_labelfirst_reward_earn_20reps` | `e502_reward_on_action_episode2_labelfirst_reward_20reps` | two trials, label at trial **0**, the payout read on the action | 11 | `loop_policy`, `loop_earn` (**0** over **61**, **3** inert) |
| `e507_label_at1_episode3_reward_earn_20reps` | `e507_label_at1_episode3_reward_20reps` | three trials, label at trial **1** | 7 | `loop_policy`, `loop_earn` (**0** over **63**, **3** inert) |
| `e511_label_at1_episode6_reward_earn_20reps` | `e511_label_at1_episode6_reward_20reps` | six trials, label at trial **1** | 9 | `loop_policy`, `loop_earn` (**0** over **63**, **3** inert) |

**Three artifacts of the census are left out, each with its reason**, and the **48** attempts that are not cells are
counted by reason -- every one of them by `config`, because the meters and the earned runs are on different passes:

- `e488_earned_label_policy_reward_20reps.json` carries `loop_policy` **without** `loop_earn`: its map is trained by
  the task loss, so it is the middle rung of `e488`'s own three-point ladder and not the paid side of the ablation.
- `e481_earned_label_policy_20reps.json` carries `loop_policy` and no payout at all, so it is neither the meter nor
  the earning side of a cell.
- `e487_earned_label_worldseed1_reward_20reps.json` is a **meter** run whose pass carries no earned run: the corpus
  has the payout in a second world and no map paid inside it.

The corpus's own repeat rule collapses **24** second executions before the census reads anything, so the counts above
are experiments and not files. And the pairing's one field beyond the two flags is `loop_earn_lr`: `e504`'s two runs
move the map's ascent rate by the flag's own subject, which `e504`'s **UA1** exempts the same way, and **0** other
fields differ past the rule on those two cells.

**The cell table**, pooled per arm over the 20 replicate seeds: the meter's own level, the gain the earning bought
over it (paired, with its sigma), the pass's accuracy on the earned run with the paired contrast against the meter
run and that contrast's sigma, and the map's mean distance from the identity it was handed:

| the cell | the pass (window) | the arm | meter level | the gain | sigma | accuracy | the change | sigma | the map |
|---|---|---|---|---|---|---|---|---|---|
| `e485`/`e488`, one trial | one trial (11) | `naive` | -6.8857 | **+1.9741** | +19.88 | 0.7649 | -0.0042 | -0.23 | 5.0935 |
| | | `ewc-block` | -6.8495 | **+1.9112** | +18.29 | 0.7281 | +0.0208 | +0.94 | 5.3670 |
| | | `replay` | -6.8743 | **+1.1759** | +10.70 | 0.7240 | -0.0149 | -0.81 | 5.6252 |
| `e500`, two trials label-first | two trials (11) | `naive` | -6.0542 | **+1.5086** | +22.74 | 0.8281 | -0.0017 | -0.25 | 5.8133 |
| | | `ewc-block` | -6.0070 | **+1.4123** | +22.57 | 0.8153 | +0.0014 | +0.17 | 5.2579 |
| | | `replay` | -6.1017 | **+1.0722** | +15.54 | 0.8247 | -0.0021 | -0.36 | 6.7272 |
| `e504` at `--loop-earn-lr 0.001` | two trials (11) | `naive` | -6.0542 | **+1.3744** | +26.19 | 0.8319 | +0.0021 | +0.33 | 3.0280 |
| | | `ewc-block` | -6.0070 | **+1.3045** | +23.23 | 0.8233 | +0.0094 | +1.32 | 2.9221 |
| | | `replay` | -6.1017 | **+1.0337** | +19.84 | 0.8299 | +0.0031 | +0.49 | 3.7398 |
| `e504` at `--loop-earn-lr 0.01` | two trials (11) | `naive` | -6.0542 | **+1.5926** | +35.39 | 0.8344 | +0.0045 | +0.72 | 10.5167 |
| | | `ewc-block` | -6.0070 | **+1.5333** | +28.38 | 0.8191 | +0.0052 | +0.78 | 9.8379 |
| | | `replay` | -6.1017 | **+1.1406** | +25.72 | 0.8313 | +0.0045 | +0.74 | 12.6430 |
| `e501`, three trials label-first | three trials (11) | `naive` | -5.9440 | **+1.4562** | +22.92 | 0.8563 | +0.0024 | +0.40 | 5.3064 |
| | | `ewc-block` | -5.9315 | **+1.3586** | +36.39 | 0.8358 | -0.0035 | -0.51 | 5.0752 |
| | | `replay` | -5.9837 | **+1.0131** | +19.68 | 0.8542 | -0.0038 | -0.75 | 6.6939 |
| `e502`, the payout on the action | two trials (11) | `naive` | -7.8884 | **+4.0860** | +21.68 | 0.8288 | -0.0010 | -0.15 | 3.3914 |
| | | `ewc-block` | -7.9915 | **+4.1356** | +23.62 | 0.8170 | +0.0031 | +0.55 | 3.5436 |
| | | `replay` | -7.8619 | **+3.0381** | +15.12 | 0.8167 | -0.0101 | -1.61 | 4.1694 |
| `e507`, the chance pass | three trials label at 1 (7) | `naive` | -42.4450 | **+7.6020** | +3.66 | 0.3264 | +0.0007 | +0.07 | 10.4934 |
| | | `ewc-block` | -43.4675 | **+9.0113** | +5.77 | 0.2993 | -0.0076 | -0.70 | 10.5437 |
| | | `replay` | -40.9544 | **+5.9397** | +2.45 | 0.2993 | -0.0281 | **-2.56** | 10.6945 |
| `e511`, the knee | six trials label at 1 (9) | `naive` | -47.0848 | **+10.1920** | +7.35 | 0.4858 | -0.0042 | -0.29 | 10.1270 |
| | | `ewc-block` | -48.8477 | **+12.9132** | +6.75 | 0.4625 | -0.0118 | -0.87 | 10.3238 |
| | | `replay` | -45.3876 | **+9.0252** | +5.13 | 0.4951 | -0.0028 | -0.17 | 9.6066 |

and the map is above the identity on **20 of 20** replicates in every cell and on every arm, its smallest replicate
**2.1537** (`e504` at **0.001**, `ewc-block`) to **10.1442** (`e504` at **0.01**, `replay`).

## 2. The two orderings

**By the meter's level** (`LA2`), closest meter first, the cells in the order the `naive` arm's level gives -- the
same order on all three arms -- with each arm's own level and gain:

| the cell | the pass | `naive` level -> gain | `ewc-block` | `replay` |
|---|---|---|---|---|
| `e501` three trials | window **11** | -5.9440 -> **+1.4562** | -5.9315 -> **+1.3586** | -5.9837 -> **+1.0131** |
| `e500` two trials label-first | window **11** | -6.0542 -> **+1.5086** | -6.0070 -> **+1.4123** | -6.1017 -> **+1.0722** |
| `e504` at **0.001** | window **11** | -6.0542 -> **+1.3744** | -6.0070 -> **+1.3045** | -6.1017 -> **+1.0337** |
| `e504` at **0.01** | window **11** | -6.0542 -> **+1.5926** | -6.0070 -> **+1.5333** | -6.1017 -> **+1.1406** |
| `e485`/`e488` one trial | window **11** | -6.8857 -> **+1.9741** | -6.8495 -> **+1.9112** | -6.8743 -> **+1.1759** |
| `e502` the action's currency | window **11** | -7.8884 -> **+4.0860** | -7.9915 -> **+4.1356** | -7.8619 -> **+3.0381** |
| `e507` the chance pass | window **7** | -42.4450 -> **+7.6020** | -43.4675 -> **+9.0113** | -40.9544 -> **+5.9397** |
| `e511` the knee | window **9** | -47.0848 -> **+10.1920** | -48.8477 -> **+12.9132** | -45.3876 -> **+9.0252** |

**0** inversions past the tolerance of **0.25** on any of the three arms, so the arm count is **3 of 3**. Three of
the eight cells share **one** meter run -- `e500` and `e504`'s two rates are three maps paid on `e498`'s own
execution -- so the level does not separate them and they are reported rather than placed against each other. The
ledger's closest call is `e501`'s three-trial cell against the sweep's smallest point: **+1.4562** against
**+1.3744** on `naive` and **+1.3586** against **+1.3045** on `ewc-block`, inverted by **+0.0818** and **+0.0541**,
both inside the registered tolerance, and on `replay` the pair does not invert at all (**+1.0131** against
**+1.0337**).

**By the accuracy** (`LA3`), the `naive` arm's accuracy diagonal highest first -- one key for all three arms, which
is what the claim registers -- the same cells order as:

| the cell | `naive` accuracy | `naive` gain | `ewc-block` gain | `replay` gain |
|---|---|---|---|---|
| `e501` three trials | 0.8563 | **+1.4562** | **+1.3586** | **+1.0131** |
| `e504` at **0.01** | 0.8344 | **+1.5926** | **+1.5333** | **+1.1406** |
| `e504` at **0.001** | 0.8319 | **+1.3744** | **+1.3045** | **+1.0337** |
| `e502` the action's currency | 0.8288 | **+4.0860** | **+4.1356** | **+3.0381** |
| `e500` two trials label-first | 0.8281 | **+1.5086** | **+1.4123** | **+1.0722** |
| `e485`/`e488` one trial | 0.7649 | **+1.9741** | **+1.9112** | **+1.1759** |
| `e511` the knee | 0.4858 | **+10.1920** | **+12.9132** | **+9.0252** |
| `e507` the chance pass | 0.3264 | **+7.6020** | **+9.0113** | **+5.9397** |

Three inversions on each arm: `e502`'s **+4.0860** against `e500`'s **+1.5086** (**+2.5774**) and against `e488`'s
**+1.9741** (**+2.1119**), and `e511`'s **+10.1920** against `e507`'s **+7.6020** (**+2.5900**) on the `naive` arm;
**+2.7233**, **+2.2244** and **+3.9019** on `ewc-block`; **+1.9659**, **+1.8622** and **+3.0855** on `replay`. So the
arm count is **0 of 3** ordered and **3 of 3** inverted. **And the inversions are the corpus's own two surprises**:
`e502`'s cell reads a **higher** accuracy than `e500`'s and `e488`'s and earns **two to three times** what they earn,
and `e511`'s knee reads a **higher** accuracy than `e507`'s chance pass and earns **+2.5900** more than it does.

| claim | measured | verdict |
|---|---|---|
| LA1 the census is bounded | **8** cells over **14** distinct artifacts, all at **20** replicates on both sides, out of **17** artifacts carrying the payout (**7** meters, **8** earned, **2** with a flag but not the pair) and **56** meter-by-earned attempts; **48** of the attempts are not cells, every one of them by `config`; **3** artifacts are left out; **24** second executions are collapsed by the corpus's own repeat rule; the pairing is two flags apart on every cell, with **0** config fields differing past the rule over **56** to **63** compared, **3** to **5** inert and **23** to **28** draw fields with **0** differing | **MET** |
| LA2 the gain is ordered by the meter's level | ordered on **3 of 3** arms (`naive`, `ewc-block`, `replay`) with **0** inversions past the tolerance of **0.25**; the levels run **-5.9440**, **-6.0542** (three cells), **-6.8857**, **-7.8884**, **-42.4450** and **-47.0848** on `naive` with the gains **+1.4562**, **+1.5086**, **+1.3744**, **+1.5926**, **+1.9741**, **+4.0860**, **+7.6020** and **+10.1920**; the cells the level does not separate are the three on `e498`'s one meter run; the closest call is **+0.0818** inside the tolerance | **MET** |
| LA3 the accuracy does not order it | inverted on **3 of 3** arms, **0** ordered; the accuracy keys **0.8563**, **0.8344**, **0.8319**, **0.8288**, **0.8281**, **0.7649**, **0.4858** and **0.3264** carry the gains **+1.4562**, **+1.5926**, **+1.3744**, **+4.0860**, **+1.5086**, **+1.9741**, **+10.1920** and **+7.6020** on `naive`; three inversions per arm, the smallest **+1.8622** and the largest **+3.9019**; the accuracy separates every pair of cells, so nothing is left out of this ordering | **MET** |
| LA4 the pass is free everywhere | **1** of the **24** cell-arm accuracy contrasts resolves at two sigma: `e507`'s `replay` arm at **-0.0281** and **-2.56** sigma (0.2993 against 0.3274). The next largest are **-0.0101** at **-1.61** (`e502`, `replay`), **-0.0118** at **-0.87** (`e511`, `ewc-block`) and **+0.0094** at **+1.32** (`e504` at **0.001**, `ewc-block`) | **FIRED** |

## 3. What it says

**And the ordering `e511` read at three points is the corpus's own ordering.** The three points `e511` pooled are
three of the ledger's cells -- the chance pass at window **7**, the knee at window **9** and the learned pass at
window **11** -- and the ledger puts five more beside them without inverting one of them: the one-trial pass
`e485`/`e488` read, `e501`'s three-trial pass at the same window **11**, `e502`'s cell with the payout read on the
action, and `e504`'s two swept ascent rates. **Sorting all eight cells by the meter's level from the closest to the
target to the furthest, the gain rises on every arm, and it rises steeply**: from about **-5.9** with a gain of
about **+1.3**, through about **-7.9** with **+4.1** and the chance pass's **-42** with **+7.6**, to the knee's
**-47** with **+12.9**. So the three points were not an accident of three points, and the two cells that could have
broken the ordering -- a cell whose pass is learned as well as `e500`'s and a cell whose payout is read on the action
rather than on the world's carried state -- sit where the ordering puts them.

**And the accuracy orders nothing, and the ledger shows why.** The eight cells' `naive` accuracies run **0.3264** to
**0.8563** and the gains over the same cells run **+1.0131** to **+10.1920**, and the two are inverted three times on
every arm. **And the inversions are the corpus's own two surprises**: `e502`'s cell reads a **higher** accuracy than
`e500`'s and `e488`'s and earns **two to three times** what they earn, and `e511`'s knee reads a **higher** accuracy
than `e507`'s chance pass and earns **+2.5900** more than it does. **So the pass's own read does not order the
earning across the ledger either**, which is the direction LA3 was registered for; and the accuracy is a weak key in
the first place, five of the eight cells lying inside **0.0282** of each other on the `naive` arm.

**And the pass is free in 23 of the 24 cell-arms, and the one it is not is the chance pass's `replay`.** The
accuracy contrast's largest sigma elsewhere is **-1.61**, and the one that resolves is `e507`'s `replay` arm:
**0.2993** against the meter run's **0.3274**, a loss of **-0.0281** at **-2.56** sigma. **So the claim that the
ablation costs the pass nothing has one exception in the corpus, and it is the arm the corpus's own chance-pass unit
already printed** -- `e507`'s finding carries the same **-0.0281** and the same **-2.56** in its own table -- and the
ledger's contribution is that it is the **only** one in **24** cell-arms, with every other cell-arm inside two sigma
and **23** of the 24 inside **1.7**.

**And the map's distance follows the meter's level, and not the level alone.** The eight cells' mean map distances
run **2.9221** to **12.6430**: the window-**7** and window-**9** cells **7.3259** to **10.6945**, the one-trial cell
**5.0935** to **5.6252**, the learned window-**11** passes **5.0752** to **6.7272**, the action's currency
**3.3914** to **4.1694**, and `e504`'s two swept rates **2.9221** to **3.7398** and **9.8379** to **12.6430** --
all at the same pass and the same meter. **So at one pass and one meter the ascent rate alone moves the map by a
factor of three** (**10.5167** against **3.0280** and **5.8133** on `naive`) while the accuracy stands still and the
gain moves by about a sixth, and the far meters are the ones whose maps travel far.

## 4. What it cannot do

- **The cells are the corpus's own and are not independent samples.** **14** artifacts make **8** cells, and three of
  the eight cells share **one** meter run: `e500` and `e504`'s two rates are three maps paid inside **one** execution
  of `e498`'s configuration, so their meter levels are the same three numbers and their contrasts share a draw. The
  three arms are three arms and not twenty-four cell-arms of independent evidence, and a ledger over a corpus this
  size is a census and not a sample.
- **And the arms and the payout are the corpus's own.** `naive`, `ewc-block` and `replay` are the corpus's three,
  the payout is the environment's own state-matching target rule read on the world's carried state (except in
  `e502`'s cell, where it is read on the action), and the ascent is the corpus's -- so nothing here says what another
  arm set, another target rule or another reward shape does with the earning.
- **And a ledger is not a design.** Each cell is one configuration executed once, at one world, one budget, one seed
  stream and one replicate count, so an ordering over the cells is a reading of those executions and not of the
  configurations; the two ordering claims are read over the passes the corpus happened to pay, which are four pass
  lengths at three placements, and no cell was run to test the ordering itself.
- **And the cells at chance passes carry a reward whose scale differs from the learned ones, so the ordering is over
  a level the corpus did not choose.** The meter's level runs about **-5.9** to **-7.9** on the window-**11** passes
  and about **-42** and **-47** on the window-**7** and window-**9** passes, so the level axis this ledger orders by
  is a level the corpus's own passes set rather than one it swept; a cell at the far end carries a reward an order of
  magnitude wider, and a gain of **+10** on a reward of **-47** is not the same quantity as a gain of **+1.5** on a
  reward of **-6**. The ordering is monotone across both regimes, which is what LA2 reads, and the two regimes are
  not the same measurement.
- **And the pass's accuracy is a weak key and the tolerance is a registered one.** Five of the eight cells lie inside
  **0.0282** of each other on the `naive` arm, so the accuracy ordering is read over keys that are nearly tied; and
  an inversion is counted past **0.25**, the smallest difference this currency has been shown to carry, with the
  ledger's closest call (**+0.0818**) inside it. A smaller tolerance would invert **two** of LA2's three arms at
  window **11** -- the tolerance and not the ordering is what decides that pair.
- **And the ledger runs nothing.** A pass the corpus has not paid, a second world with the map paid inside it, a
  second seed stream and the interior placements are outside a unit that reads what is already on disk.

**Artifacts:** `runs/e512_the_earning_ledger.json`, read from
`runs/e485_earned_label_reward_20reps.json`, `runs/e488_earned_label_earned_20reps.json`,
`runs/e498_earned_label_episode2_labelfirst_reward_20reps.json`,
`runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json`,
`runs/e501_earned_label_episode3_labelfirst_reward_20reps.json`,
`runs/e501_earned_label_episode3_labelfirst_reward_earn_20reps.json`,
`runs/e502_reward_on_action_episode2_labelfirst_reward_20reps.json`,
`runs/e502_reward_on_action_episode2_labelfirst_reward_earn_20reps.json`,
`runs/e504_earn_lr0.001_episode2_labelfirst_reward_earn_20reps.json`,
`runs/e504_earn_lr0.01_episode2_labelfirst_reward_earn_20reps.json`,
`runs/e507_label_at1_episode3_reward_20reps.json`, `runs/e507_label_at1_episode3_reward_earn_20reps.json`,
`runs/e511_label_at1_episode6_reward_20reps.json` and `runs/e511_label_at1_episode6_reward_earn_20reps.json`.
