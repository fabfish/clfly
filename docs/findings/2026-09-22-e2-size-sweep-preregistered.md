# E26 — the `swap2` non-replication: a size sweep, and the prediction written before it lands

**Date:** 2026-09-22
**Script:** `experiments/e2_topology_gap.py` (`--no-realized` added), `runs/e26_size*.json` (in flight)
**Context:** `docs/findings/2026-09-22-c1-refutation-does-not-replicate.md`

---

## 1. The question

The previous fire found that the contrast carrying C1's interference refutation **reverses** between
two circuit sizes. At d = 1307 the excess falls from `swap0.5` to `swap2` by 32.7σ; at d = 952 it
rises by 21.8σ (paired). `real` and `swap0.5` replicate to within 4%; only `swap2` moves, by a
factor of **4.67**. Rewiring strength was matched (swap fraction 0.912 against 0.924) and
conditioning behaves oppositely at the two sizes, so neither explains it.

Two points cannot tell a scale dependence from an unstable object. This sweep supplies four more.

## 2. The design

`d` is a smooth function of the `--circuit-size` cap, so intermediate sizes are available:

| circuit-size | 300 | **400** | **500** | **600** | **700** | 800 | 1500 |
|---|---|---|---|---|---|---|---|
| d | 952 *(known)* | **1010** | **1086** | **1149** | **1229** | 1307 *(known)* | 1874 |

The sweep runs `real`, `swap0.5`, `swap2` at the four bold sizes, 6 seeds, analytic estimator only
(`--no-realized` is new and halves the runtime; the analytic estimator supersedes the realized one
everywhere a conclusion is drawn).

**The internal control is `real` and `swap0.5`.** They replicated to within 4% between the two known
sizes, so if they stay flat across the four new ones, the composition differences between subsamples
are small and `swap2`'s trajectory is interpretable as a function of the circuit. If they do *not*
stay flat, the sweep is measuring subsample variation and nothing can be read from it.

## 3. The prediction, before the numbers exist

- **If the change is a scale effect:** `real` and `swap0.5` stay within ~5% of 0.0190 and 0.0228
  across all six sizes, and `swap2` moves **monotonically** between 0.058 (d = 952) and 0.012
  (d = 1307), whatever the shape of the curve.
- **If `swap2` is an unstable object rather than a scale-dependent one:** its excess jumps between
  neighbouring sizes by more than the monotone trend allows — e.g. 0.058, 0.013, 0.050 at
  consecutive `d` — which no smooth function of the circuit can produce.
- **A third outcome is possible and would be the most interesting:** `swap2` moves monotonically but
  `real`/`swap0.5` do not, which would mean the sweep's composition differences dominate and the
  earlier d = 952 vs d = 1307 comparison is confounded rather than decisive.

Each outcome has a distinct reading, which is why the prediction is worth writing down: the
alternative is to look at four new numbers and construct whichever story fits.

## 4. Two small guards added on the way

Adding `--no-realized` exposed two report paths that assumed data was always present:

- the results table indexed `['realized']['excess_mean']` unconditionally — now it renders a
  placeholder, and the monotonicity block drops the realized reading when it is absent;
- the contrast table assumed `paired_contrast` would return `sigma_paired`, which it cannot with one
  seed — the guard now distinguishes "1 seed" from "no per-seed data", since those are different
  reasons for the same missing number.

Both are the same class of failure as the `n_eval` crash in `e8` earlier today: a path that is only
exercised when an option is used for the first time. That is an argument for exercising new flags in
the same fire they are added, which is what the smoke run above did.
