# `e141` pre-registered: the λ sweep at forty replicates, with substitution as the mechanism

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py`, unchanged; `--lam L --methods ewc --fisher-batches 32 --repeats 40`.
**Planned artifacts:** `runs/e141_r32_ewc_lam{L}.json` for **L ∈ {3e-4, 3e-2, 3e-1}**, each
`--circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --train 96 --test 48 --noise 1.0 --classes 4 --support 80
--shared-head --input-overlap 0.0 --readout-size 32 --seed0 0`.
**The λ = 3e-3 arm is not run**: it is `runs/e133_r32_naive_ewc_40reps.json`'s `ewc` arm, and **C0 is that this
sweep's other arms are on the same footing as it**.
**Comparators:** `e133`'s `naive` (+0.0750 ± 0.0088) and `ewc` (+0.0654 ± 0.0079) at forty paired seeds.

## Why a λ sweep now, and what is new about it

**The project already has a λ sweep, and it is one seed.** `docs/findings/2026-09-22-lambda-tuning-negative.md`
swept λ ∈ {0.003, 0.01, 0.03, 0.1, 0.3} on the **older** configuration (`mb+cx+al@n1307`, chance 0.25) at one
seed and concluded that **"λ matters enormously, and 0.003 is the only useful setting"** — at λ = 0.003 the
diagonal's forgetting was the baseline's (+0.010 against +0.010) with accuracy 0.875 against 0.896, and at
λ ≥ 0.01 its forgetting was **8 to 12 times** the baseline's with accuracy falling to 0.757–0.792.

**That is the shape of claim this project has repeatedly had to shrink** — five replicates were a ~1-in-55 draw in
`e133`, and a single seed cannot carry a factor of eight. **And the mechanism is now known, which it was not in
September:** `e137` measured that the diagonal penalty **relocates** adaptation into the 800 offsets no penalty
covers (its `theta` moves 28% less, its bias **25% more**), and `e139` that the penalty's own
interference term falls **98%** while the forgetting moves **1.21σ**. So a λ sweep is no longer a search for a
working hyper-parameter: it is **a test of whether squeezing the covered channel is a lever at all**, and the
quantity that says so is recorded in every artifact.

**This is the same question as `e138` from the other side.** `e138` puts the *channel* inside the penalty;
`e141` turns the *strength* up while the channel is still outside it. **If λ is a real lever, `e138` is
unnecessary; if it is not, `e138` is the only arm in which the penalty can act on the whole body.**

## The controls and the predictions

- **C0, and it is exact.** Every arm is the same command as `e133`'s except `--lam`, at the same seeds and the
  same epoch, so each arm's **`naive`**-free quantities must be comparable per replicate. There is no separate
  `naive` arm here: the baselines are `e133`'s, which is why the artifacts are named for λ alone. *(A `naive` row
  is not run because `naive` ignores λ; if a future fire wants the internal check, `runs/e116_r32_40reps.json`
  is the forty-replicate `naive` at these seeds.)*
- **P1, the mechanism, and it is the fire.** **The bias's cumulative movement rises monotonically in λ**, with the
  top contrast (**λ = 3e-1 against 3e-3**) resolved at **≥ 3σ**. `e137` gives the direction from an intervention
  on the same object, and the instrument is `bias_norms`' per-task steps, already recorded.
- **P2, and the effect must not follow.** **The forgetting does not fall as λ rises**: registered as the ordered
  contrast **λ = 3e-2 worse than λ = 3e-3** (larger forgetting) resolving at **≥ 2σ**, over the same forty seeds.
- **P2b, the two together.** **`theta_drift` falls monotonically in λ** (the top contrast at **≥ 3σ**) **while the
  forgetting does not.** So the arms are read as a pair: a penalty that visibly constrains the channel it covers
  and visibly does not help is a substitution, not a strength problem, and this fire is where that stops being an
  inference from one λ.
- **Accuracy is a registered cost to report**, not only a benefit: the single-seed sweep found it falling to
  0.757 at λ = 0.03, and `e133`'s diagonal at λ = 3e-3 is already **below** `naive` (0.8856 against 0.9125).
- **Falsifier.** The forgetting **falls monotonically in λ** and the top arm is **≥ 3σ better than λ = 3e-3**.
  Then **λ is the lever after all**, the penalty's failure at λ = 3e-3 is a strength problem rather than a
  coverage problem, and `e137`/`e139`'s substitution reading — that the penalty squeezes one channel while the
  damage lives in the other — is **wrong as an explanation of the null**, whatever it says about the trajectory.

## What this cannot settle, in advance

- **One read-out (32), one circuit, three tasks, one task order**, and read-out 32 is where the bias's share of
  the forgetting is **largest** (70%; `e134` measures 89% and 83% at read-outs 128 and 1307). So a null here is a
  null where the confound is strongest — the right place to ask whether covering the channel matters and the
  wrong place to generalise from.
- **It cannot replicate the September sweep, only the shape of its claim**: that sweep's configuration is a
  different point (`@n1307`, whole-state read-out, a different λ set), so agreement or disagreement is about the
  *ordering in λ*, not about its numbers.
- **Neither λ nor the basis is varied here.** `e140` varies the basis at λ = 3e-3 with the same forty seeds, and
  the two fires together cover two axes of §4.2's surface rather than the surface.
- **And a penalty is not a freeze**: `e125`'s frozen-bias value (+0.0227) is the level λ would be approaching if
  it could reach the channel, and nothing here is registered as reaching it.
