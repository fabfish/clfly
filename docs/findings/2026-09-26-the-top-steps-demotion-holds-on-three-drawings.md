# The top step's demotion holds on three drawings per size, and the ER level is the tightest at every size

*2026-09-26 04:59, `runs/e219_draws_cs{300,400}_rs{0,1,2}.json` — six drawings, eighteen cells, ~35 min. Read by
`e220_ladder_draws_read.py`, exit 0. The registration is
`docs/findings/2026-09-26-registered-the-ladders-levels-with-drawings-at-the-two-new-sizes.md`.*

## 1. The verdicts

| | claim | verdict |
|---|---|---|
| **R1** | at each size, the mean top step below 1.5× and no drawing at 2.0× | **MET** — cs 300 **1.18×** (worst 1.28×), cs 400 **1.11×** (worst 1.19×) |
| **R2** | at each size, in every drawing the two one-side nulls within 2× | **MET** — cs 300 worst 1.44×, cs 400 worst 1.11× |

**So `e217`'s single-drawing verdict was not a drawing artifact.** The top step's demotion stands on three drawings per
size, and it is now stated in the form the data supports: **1.18× at cs 300 and 1.11× at cs 400 against cs 800's
2.76×/3.02×** — not 1.28× and 1.08×, which were single points inside those ranges.

## 2. The eighteen cells

| size | drawing | `alloy1` | `inalloy1` | `erdos_renyi` | top step | middle ratio |
|---|---|---|---|---|---|---|
| cs 300 | rs0 | 0.12247 | 0.12233 | 0.15668 | 1.28× | 1.00× |
| cs 300 | rs1 | 0.14080 | 0.10040 | 0.15900 | 1.13× | 1.40× |
| cs 300 | rs2 | 0.09431 | 0.13581 | 0.15412 | 1.13× | 1.44× |
| cs 400 | rs0 | 0.13859 | 0.13249 | 0.15015 | 1.08× | 1.05× |
| cs 400 | rs1 | 0.12618 | 0.13014 | 0.15497 | 1.19× | 1.03× |
| cs 400 | rs2 | 0.13808 | 0.12480 | 0.14779 | 1.07× | 1.11× |

## 3. R3's ranges: the two-side level is the tightest at every size, and the one-side levels are the loosest

| size | `alloy1` | `inalloy1` | `erdos_renyi` |
|---|---|---|---|
| cs 300 | **1.49×** (0.09431–0.14080) | 1.35× | **1.03×** |
| cs 400 | 1.10× | 1.06× | **1.05×** |
| cs 800 | **3.34×** (five drawings) | 1.24× (three) | **1.05×** (nine) |

**Erdős–Rényi reproduces to 3–5% at every circuit size and the destroyed-one-side nulls do not** — 1.35–1.49× at
cs 300, 1.06–1.10× at cs 400, 1.24–3.34× at cs 800 — so the pattern is not a size effect but a construction effect:
**the construction with nothing left to lose is the reproducible one, and the constructions with exactly one side
preserved are where the drawing matters.** That is the same asymmetry the cs-800 spread table showed, now measured at
three sizes.

**And a detail the means hide**: at cs 300 the two one-side nulls *swap places* between drawings — `alloy1` leads at
rs0 and rs1, `inalloy1` at rs2 — so "the middle is one level" means the two sides are statistically
indistinguishable, not that one of them consistently leads. R2 is MET on that reading, and the cs-300 mean ratio
(1.28×) is five times the cs-400 one (1.06×).

## 4. What the record now says about the ladder

- **What holds at three circuit sizes**: destroying a graph's degree structure raises the penalty; the intact
  connectome is the lowest level; freeing either side alone gives one level rather than two (all drawings within
  1.44×); and the two-side level is the most reproducible quantity in the family (1.03–1.05× at every size).
- **What does not**: the **top step's size** — 2.76×/3.02× at cs 800, **1.18× at cs 300 and 1.11× at cs 400** on three
  drawings each — because the one-side level rises with shrinking circuits (0.047 → 0.122–0.139) while the two-side
  level barely moves (0.142 → 0.157).
- **And the mechanism candidate is still untested**: that at smaller circuits a task's support is a larger fraction of
  the neuron set, so one-sided damage goes further. Testing it needs the support fraction varied *independently* of
  the circuit size, which no design here has done.

> **TESTED 2026-09-26 05:43, and only half of it held**: `e221` varied the support at cs 800 (20 and 160 against
> the convention's 80, two drawings each) and **U1 was MET** — the one-side level is **1.42×** higher at the
> smaller share (0.07642 against 0.05374, bar 1.3×) — while **U2 landed outside all three of its registered
> outcomes**: the top step is 1.96× at support 20 and 2.10× at support 160, both *above* 1.5× and only 1.07×
> apart, and the relation is **non-monotone** (2.76× at the convention's 80). So the share is a real variable
> for the one-side level and **not** for the ladder's shape, and the circuit-size dependence of the top step
> still has no tested explanation. The candidate's direction was also corrected on the way in, since
> `--support` is 10% of the circuit SIZE while the neuron count is not proportional
> (`docs/findings/2026-09-26-the-support-share-moves-the-one-side-level-but-not-the-top-step.md`).

## 5. What this cannot do

Six drawings across two sizes is a range and not an sd (the project's convention for a handful of samples); the support
fraction stays at the 10%-of-circuit convention throughout, so size and support are not separated; cs 800's levels are
five- and three-drawing means from *other* designs rather than three drawings of this one, so the three sizes are not
equal in their evidence; and nothing here speaks for the sign pattern or the network substrate.
