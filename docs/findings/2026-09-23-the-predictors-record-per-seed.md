# E64 — the predictor, checked per seed: **24 of 24 resolvable pairs are called correctly**, and `e63` is overturned by its own paired σ

**Date:** 2026-09-23
**Script:** `experiments/e64_predictor_per_seed.py`
**Artifacts:** `runs/e64_predictor_6_perseed.json` (five conditions × six seeds), `runs/e64_predictor_per_seed_analysis.json`
**Context:** `2026-09-22-the-predictor-failure-is-unresolved.md` (e63, overturned here), `2026-09-22-predictor-survives-draw-correction.md`, `2026-09-23-cell-type-is-not-a-null.md` (e66), plan rule 8

---

## 1. The last rule-8 gap, and why the denominator moves

The project's predictor was quoted as "**13 of 13** on every pair the excess metric can resolve, with
the sign record 24 of 25 overall". Every earlier fire closed a rule-8 gap somewhere else — `e47`/`e48`
for the C1 contrast, `e54` for the `naive` arm, `e57`+`e58` for the basis ladders — and this one was
last: `e6_predictor_6.json` stored only pooled means, so the 13 could not be re-analysed paired.

`e64` re-runs the same five conditions at the same six seeds with per-seed storage. **Every basis in a
condition sees the same task geometries in the same order**, so a biological basis and its
size-matched control are matched observations and their contrast is *paired* — which is the same
correction that turned `cell_type`'s 0.74σ into 20.3σ in `e66`, and it moves this record the same way.

**And the first launch of `e64` had to be killed at 73%**: `e6`'s row builder never copied
`excess_per_seed` into its output, so the run would have produced a complete-looking artifact that
reproduced the pooled numbers exactly and proved nothing per seed. The field is now carried through and
the analysis script **refuses to run** on an artifact without it.

## 2. The record, at three denominators

| denominator | pairs | called correctly |
|---|---|---|
| all matched pairs | 25 | **24** (published 24/25) |
| σ(task) > 2 — the paired seed sem only | **24** | **23 of 24** |
| σ(rule) > 2 — with the **measured** control-draw sd folded in | **21** | **20 of 21** |

The published denominator was **13**, and the change is entirely the pairing: the published σ used
`hypot(sem_bio, sem_rand)`, which for a pair whose two arms co-move across task draws is an order of
magnitude too large. **On the paired sem, 24 of the 25 pairs resolve.**

**And the resolvable set is completely seed-robust:**

* **all 24 resolvable pairs have unanimous per-seed signs (6/6)**;
* **no leave-one-out removal flips any of them**, and the smallest leave-one-out σ is **6.31**;
* the largest single-seed leverage is well below the 1 on which a single replicate would carry a pair.

## 3. The single miss is a confident, strongly-resolved wrong call — which overturns `e63`

Under the most conservative denominator the record is **20 of 21**, and the one miss is:

| condition / rung | delta | σ(task) | σ(rule) | signs | the predictor said |
|---|---|---|---|---|---|
| **`rewired-swap2` / `cell_class`** | **+0.00340** | **10.63** | **8.54** | **`++++++`** | **bio** — and `rand` is better |

`e63` concluded the opposite, in these words:

> the call is 1.74σ, the largest of five σ's in a condition where nothing resolves (0.06–1.74σ), so it
> is a confident prediction meeting an unresolved observation rather than a wrong call with a large
> margin, and the condition is better described as UNTESTED.

**Both halves of that are unpaired-σ artifacts.** The pair resolves at **10.63σ on the task axis and
8.54σ with the draw component in**, with six of six seeds agreeing in sign; and the condition is not a
null — four of its five pairs resolve, and the predictor gets three of them right. So `e63`'s
softening is withdrawn and the **original `e6` reading is restored**: the predictor has *one confident
failure*, on heavily rewired wiring, called the wrong way with a large margin. That is a known failure
mode of a working predictor, which is a more useful statement than "untested" — and it is the statement
the project's own first version of this analysis made.

`e63`'s second conclusion falls with it: it held that `cell_type` (0.03–0.26σ) and `supertype`
(1.5–2.2σ) never resolve, "so the 13/13 is actually about the three coarser rungs". Paired,
**`supertype` resolves in every condition at 8.1–14.8σ** and `cell_type` at 7.8–13.9σ. All five rungs
resolve, everywhere, on the task axis.

## 4. And the cells where the draw component does bite

Folding in each rung's **measured** control-draw sd — `e67` for `side` and `cell_type`, `e17`/`e17b`
for the rest — four of the 25 pairs fall below 2σ:

| pair | σ(task) | σ(rule) | note |
|---|---|---|---|
| `baseline` / `cell_type` | 11.72 | **0.89** | correct call, not measurable |
| `wider-tasks` / `cell_type` | 11.27 | **0.65** | correct call, not measurable |
| `faster-drift` / `cell_type` | 12.41 | **1.08** | correct call, not measurable |
| `rewired-swap2` / `side` | 0.39 | **0.21** | the pair that is genuinely untested |

So the honest headline has two clauses: **20 of 21 pairs clear 2σ with the draw component in and the
predictor calls 20 of them right**; and **three of the four pairs the draw component removes are
`cell_type`, whose delta (+0.00006) is smaller than its own control-draw spread (6.8e-5)** — the
predictor's calls there are correct but there is nothing to measure, which is `e72`'s finding arriving
from the other side.

**One stale source had to be fixed to get this right**: the script's first version used `e14`'s
*pooled* `cell_type` draw sd (6.1e-4) as a proxy for `cell_type` itself, which collapsed its σ(rule) to
0.07–0.42 and would have reported "6 of 25 below 2σ" with five of the six being `cell_type`. The
measured value (`e67`, 6.8e-5) gives the table above.

## 5. What changes in the paper

* "13 of 13 on every pair the excess metric can resolve" becomes **"24 of 24 on the paired seed sem, or
  20 of 21 once the control-draw component is included"**.
* "and the single failure turns out not to be one" is **withdrawn**: the failure is real, resolved, and
  unanimous over six seeds.
* "the 13/13 is about the three coarser rungs" is **withdrawn**: all five rungs resolve.
* The predictor's own limits section gains a stronger claim than it had: it is not merely uncalibrated,
  it is **confidently wrong in one identifiable region** — heavily rewired wiring, at `cell_class`
  granularity.

## 6. Limits

- **Six seeds per condition.** The paired sem at six seeds is what makes 24 of 25 resolve, and rule 20's
  caution applies: these are 6σ-per-seed records, not sixteen.
- **The 24 resolvable pairs are not independent** — five rungs appear in each of five conditions, so
  the record is 25 observations of a five-rung ordering. Counting them as independent overstates the
  evidence; the honest form is that **every matched pair in every condition is unanimous**.
- **`rewired-swap2` is one rewire draw.** `e2`'s realization work says a single draw of a rule is one
  sample; the predictor's one confident failure is measured on one heavily-rewired graph, and whether
  it survives redrawing that graph is open. That is the same exposure `e59`/`e65` found for the C1
  contrast, and it is not closed here.
- **The draw sds are per rung, not per condition** — measured at one circuit size each, and `e67`
  refuted exactly the scalar that was being used to interpolate them.
