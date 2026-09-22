# E8d — tuning λ jointly with Fisher quality does not rescue EWC either

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --lam L --fisher-batches 32`
**Artifacts:** `runs/e8_tuned_lambda.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, Fisher batches = 32, 500 iterations, chance 0.25

---

## 1. Why this fire

The previous fire found that **λ is not transferable across Fisher quality**: the
diagonal's forgetting rose from +0.063 to +0.250 as the Fisher batch count went 8 → 128
at *fixed* λ, because a better-estimated Fisher is a stronger penalty. That made the
standing conclusion — "no Fisher-anchoring variant beats naive" — provisional, since it
had only ever been tested at λ values that might all have been wrong. This fire tunes λ
properly and re-asks.

## 2. The λ sweep, at Fisher batches = 32

Single seed; `naive` is constant at **0.896 accuracy / +0.010 forgetting** throughout and
is the reference (it uses no Fisher, so nothing in the Fisher machinery perturbs it).

| λ | EWC diagonal | block — **biological** | block — matched **random** |
|---|---|---|---|
| 0.003 | 0.875 / +0.010 | **0.910 / −0.021** | 0.743 / +0.250 |
| 0.01 | 0.778 / +0.125 | 0.792 / +0.115 | 0.847 / +0.062 |
| 0.03 | 0.757 / +0.083 | 0.778 / +0.115 | 0.813 / +0.115 |
| 0.1 | 0.792 / +0.125 | 0.833 / +0.104 | 0.868 / +0.010 |
| 0.3 | 0.792 / +0.094 | 0.819 / +0.083 | 0.764 / +0.115 |

*(final accuracy / mean forgetting.)*

**λ matters enormously, and 0.003 is the only useful setting.** For λ ≥ 0.01 every EWC
variant is worse than naive on *both* metrics — accuracy drops from 0.896 to 0.757–0.868
and forgetting rises. At λ = 0.003 the biological block partition is the best method in
the table: 0.910 accuracy against naive's 0.896, and forgetting **−0.021** against
naive's +0.010, while its size-matched random control is the *worst* (0.743 / +0.250).

So the λ concern was well founded — the earlier sweeps had been landing in an
over-constrained regime — and tuning found a setting where the biological partition looks
like a genuine win. That is exactly why it needed repeats.

## 3. With repeats, the reversal evaporates

| λ | method | final accuracy | mean forgetting |
|---|---|---|---|
| 0.003 | naive | 0.824 ± 0.036 | +0.101 ± 0.049 |
| 0.003 | EWC diagonal | 0.775 ± 0.053 | +0.177 ± 0.084 |
| 0.003 | **block — biological** | **0.868 ± 0.035** | **+0.049 ± 0.075** |
| 0.003 | block — matched random | 0.831 ± 0.048 | +0.125 ± 0.075 |
| 0.01 | naive | 0.824 ± 0.036 | +0.101 ± 0.049 |
| 0.01 | EWC diagonal | 0.829 ± 0.025 | +0.062 ± 0.032 |
| 0.01 | block — biological | 0.826 ± 0.028 | +0.076 ± 0.060 |
| 0.01 | **block — matched random** | **0.863 ± 0.010** | **+0.059 ± 0.015** |

*(3 replicates each.)* At λ = 0.003 the biological partition is still directionally best on
both metrics but nothing clears 1σ. **And the winner flips with λ**: at 0.003 the
biological partition is best and the random control second-worst; at 0.01 the **random**
control is best on both metrics and the biological one is middling. A three-fold change in
λ reverses the bio-versus-random ordering — and the previous fire showed the same
comparison also flips with the Fisher batch count. The ordering is unstable in **two**
hyperparameters.

## 3.1 With nine replicates, the effect sizes halve

The one directionally-promising configuration (λ = 0.003, 32 batches) deserved a firm
number:

| method | final accuracy | mean forgetting | vs naive |
|---|---|---|---|
| naive | 0.840 ± 0.013 | +0.101 ± 0.020 | — |
| block — biological | 0.865 ± 0.012 | +0.075 ± 0.026 | −0.026 ± 0.033 (**0.8σ**) |
| block — matched random | 0.845 ± 0.017 | +0.093 ± 0.027 | −0.008 ± 0.034 (0.2σ) |

**Nothing resolves**, and the estimates *shrank* on the way from 3 to 9 replicates:
forgetting's bio-minus-naive gap went from −0.052 to −0.026 and accuracy's from +0.044 to
+0.025. That halving is the signature of a point estimate that was noise-amplified at low
replicate count, and it is the cleanest possible statement that the single-seed λ = 0.003
"win" was an artefact.

The biological-versus-random difference at 9 replicates is **0.5σ** (−0.018 ± 0.037
forgetting, +0.020 ± 0.021 accuracy). That is now the fourth independent setting in which
the biological synapse partition fails to show a reproducible advantage.

## 4. What the network line now concludes

After **jointly** tuning λ over five values and the Fisher batch count over three, the
standing conclusion is unchanged and can now be stated with the tuning objection closed:

> **No Fisher-anchoring variant resolves a benefit over the naive baseline on this
> benchmark** — not the neuron diagonal, not a block-diagonal Fisher over cell-class
> synapse pairs, not at any (λ, batch-count) pair tried. **Replay** drives forgetting to
> ~0 with the best accuracy and is the only method that clearly works.

And the specific transfer claim is dead in a way that is now well-characterised:

> Grouping the 27k synapses by `(pre cell class, post cell class)` — the exact analogue of
> the partition that won on the linear substrate — shows no reproducible advantage over a
> size-matched random grouping. The comparison flips sign with λ and with Fisher batch
> count, and never clears 1σ in either direction.

**The interpretation stands.** The linear finding concerns the block structure of the
precision matrix over *neurons*; the network analogue groups *synapses* by endpoint cell
class. Those are different partitions of different spaces, and the linear result never
required the second to behave like the first. The transfer was an analogy, and the
analogy is wrong — not merely underpowered, since tuning the two hyperparameters that
could have hidden the effect did not reveal it.

It is also what the theory predicts. LGCL says EWC *is* a Kalman filter whose posterior
is projected onto the neuron coordinate basis, and §4.1 measured that projection to cost
**33% excess error** on this connectome. A method built on that projection should not be
expected to help, and making a better estimate of *which* projection to make — or turning
its strength down until it stops hurting — does not fix a projection that should not be
made at all.

## 5. Limits

- **Three tasks.** "Mean forgetting" averages two numbers, which is why standard errors
  are ~0.05–0.08 and why 3 replicates leave everything at ~1σ. The nine-replicate run at
  λ = 0.003 is reported above and settled the one directionally-promising
  configuration: the effect did not sharpen, it halved.
- **Task-incremental** with per-task heads, so the body is the only thing that can be
  forgotten.
- The λ grid is log-spaced with a factor of ~3; a win confined to a narrower window would
  have been missed. The 0.003→0.01 flip argues against a narrow window being the issue.
