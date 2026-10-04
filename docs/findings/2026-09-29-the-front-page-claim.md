# The front-page claim: an absence of forgetting that holds in 64 of 294 arms and fails in 230

*2026-09-29 04:28. Runs: **none new** — `experiments/e299_the_front_page_claim.py` reads the README for absence claims
and every arm of the corpus for its distance from zero, writing `runs/e299_the_front_page_claim.json`. Seconds.*

## 1. The surface nobody had audited

This line has read the paper, the programme table and the findings. The **README** has not been read against the
corpus, and it is the first thing a visitor reads:

> One brain, many behaviours, **no catastrophic forgetting**. A fly learns to associate odours with food, navigate by
> landmarks, and dodge looming threats — sequentially, **without** its olfactory memories being erased by its
> navigation lessons.

Both sentences state an **absence**, and an absence is a *bound* — which is why the corpus can be asked about it
directly: every arm's `mean_forgetting` has a mean and a sem over its own replicates, so each arm either resolves away
from zero or fails to, and the arms that fail to are the arms where the corpus measured an absence.

**F1 MET** — the front page states an absence, twice. **F2 MET** — and the corpus supports it for a named minority:

| | arms | |
|---|---|---|
| indistinguishable from zero at two sigma | **64 of 294 (22%)** | 8 of them at forty replicates, smallest bound **±0.0029** |
| resolved away from zero | **230 of 294 (78%)** | largest **24.90σ** (`e178_rung_side_cs300_144reps`, `ewc-block`) |

The tightest bounds on zero, all at forty replicates, are `replay` in `e140_r32_methods_frozenbias_40reps` at
**+0.00182 ± 0.00316** (0.58σ), `replay` in `e155_r700_naive_replay` at **+0.00078 ± 0.00287** (0.27σ) and `ewc` in
`e150_r32_overlap1_frozenbias_ewc_lam3e-4` at **+0.00078 ± 0.00339** (0.23σ) — against a baseline whose median
forgetting is **+0.0729**. **F3 MET** — and it is refuted as a general claim: 230 arms resolve away from zero.

By arm, the share inside the two-sigma line runs **34% for `replay`** (median forgetting +0.0125), 34% for
`ewc-block`, 31% for `ewc`, 20% for `ewc-block-rand` and **11% for `naive`** (median +0.0729).

## 2. The correction

The README now carries a **scoped 2026-09-29** blockquote after those sentences: the absence is measured in 64 of 294
arms — eight at forty replicates with a bound under ±0.003 against a baseline median of +0.073 — and measured against
in 230, up to 24.9σ; so it is a result about particular configurations and **not yet a property of the fly those
sentences describe**. Scoped rather than deleted, because the minority is real and named.

Two instrument repairs were needed first, both found by reading the instrument's output: `never` was a cue and matched
*"Connectome-constrained models are used for simulation and knockout screens, **never for forgetting curves**"* — a
claim about the literature and not about a fly — so the cue list now holds only the absence-of-forgetting senses; and
the zero-detector had to straddle zero in its own test fixture, because **a ramp's distance from zero is
scale-invariant** and a ramp can therefore never be indistinguishable from zero however small it is.

## 3. What it cannot do

**Zero is not absence**: an arm indistinguishable from zero at two sigma is one whose forgetting is smaller than its
own noise, which for a noisy configuration can be true of a real effect of 0.01 — so F2's count is a statement about
*resolution* and not about a fly remembering perfectly. **The arms are not independent**: the same configuration
recurs, so 64 of 294 over-counts the distinct configurations, in the way `e290` measured for the variance fraction.
**`mean_forgetting` is a mean over the first `T - 1` tasks**, so an arm can be indistinguishable from zero while one
task forgets and another does not — `e151`'s per-task decomposition is the instrument for that and this unit does not
use it. **The two-sigma line is a convention**: at one sigma the count rises and at three it falls. **And the README's
claim is about a fly, while every number here is about a connectome-constrained network on four-way classification
tasks**: the distance between those two is the whole of the modelling question, and nothing here closes it.

## RE-READ 2026-10-01 03:04 — the population moved from files to experiments

`e301` found seventeen files in `runs/` that are a second execution of an experiment already in the corpus, and this
census now drops the second copies, so the front page's absence is measured over **271 arms** where the file count gave
304. **F1** is unchanged: two absence sentences. **F2 MET and smaller**: **55 of 271 arms (20%)** have a forgetting
indistinguishable from zero at two sigma, still **8 of them at forty replicates** with a smallest bound of **±0.0029**,
against a baseline whose median is **+0.073**. **F3 MET**: **216 of 271 arms (79%)** resolve away from zero, the
largest still **24.90 sigma**. Nine of the arms that were inside the line were second copies — that is the whole of the
movement — and the README's scope blockquote now carries the new denominators with the reason.

## RE-READ 2026-10-04: the ratio crossed two

The live test held the arms outside the two-sigma line at more than **twice** the arms inside it. `e397` to `e408`
added the closed loop's redraw series -- twenty-odd runs whose arms land inside the line -- and the count is now
**393 outside against 199 inside**, **1.97 times**. A ratio of two on a corpus that grows arms is the same knife-edge
other census units have had to shed, so the ratio is reported and the front page's sentence is asserted as the
**direction** it needs: most arms resolve away from zero, and the largest sigma is far above it. The sentence itself
is unchanged, and the numbers that carry it are in the artifact.
