# E8c — the block-Fisher transfer failure is not estimation noise

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --fisher-batches N`
**Artifacts:** `runs/e8_fisher_batches.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, λ = 0.1, 500 iterations, chance 0.25

> **Correction (2026-09-23).** The artifact named above **no longer holds this sweep**. It now holds a
> three-repeat, 32-batch run written later (`config`: `fisher_batches: 32, repeats: 3`, against this
> document's "single seed, sweeping the Fisher batch count"), and **no artifact on disk carries a 128-batch
> Fisher at all** — every `fisher_batches` value under `runs/` is 8 or 32. Reading that artifact's stored
> `replicates` identifies §2's table exactly: its **32-batch row is replicate #0 for all four methods**, and
> the artifact's own three-replicate means differ, for the diagonal substantially — **+0.069 ± 0.028, against
> the +0.125 this document reports**, the first replicate being the worst of the three (+0.125, +0.031,
> +0.052). The 8-batch row's two block arms are replicate #0 of `e31_methodlist_check.json`; its `ewc` cell
> matches no replicate anywhere; and the 128-batch row matches nothing. **The table is left standing here
> because it is the only surviving trace of those numbers**, and the conclusion it was written to support —
> that the negative is not estimation noise — is now being re-measured by `e96` rather than resting on it
> (`docs/findings/2026-09-23-the-fisher-batch-sweep-is-a-stitch-of-first-replicates.md`).

---

## 1. The hypothesis being tested

The previous fire found that carrying the linear-substrate basis finding into the
trained network *fails*: the biological `(pre cell class, post cell class)` synapse
partition forgets more than the neuron diagonal and more than its own size-matched
random control. The leading explanation offered was **statistical** — the block Fisher
has `Σ s_g² = 5.3e7` entries to fill from 8 minibatches of 32 samples (256
observations), against the diagonal's 26,568 entries from the same 256, so its
within-group off-diagonals accumulate estimation noise that the diagonal simply
discards.

That is a cheap, decisive test: **raise the batch count.** If the block partition
improves and eventually overtakes the diagonal and its control, the negative result is a
power statement. If it does not, the block structure genuinely does not help.

## 2. Result: the explanation is ruled out, and at 3 repeats nothing resolves

Single seed, λ = 0.1, sweeping the Fisher batch count:

| Fisher batches | naive | EWC diagonal | EWC block — **biological** | EWC block — matched **random** |
|---|---|---|---|---|
| 8 | +0.010 (0.896) | +0.063 (0.826) | +0.104 (0.826) | +0.042 (0.854) |
| 32 | +0.010 (0.896) | +0.125 (0.792) | +0.104 (0.833) | **+0.010** (0.868) |
| 128 | +0.010 (0.896) | +0.250 (0.701) | +0.073 (0.792) | +0.094 (0.819) |

*(mean forgetting, final accuracy in parentheses.)*

**The biological partition never overtakes the diagonal, naive, or consistently its
own matched control**, at any batch count. The bio-versus-random comparison flips sign
across the sweep (+0.042 vs +0.104; +0.010 vs +0.104; +0.073 vs +0.094) — which is what
a null effect looks like. On the linear substrate the same grouping beat its matched
control at 3.7σ (5 seeds) and 12.1σ (18 seeds).

**`naive` is constant at +0.010 / 0.896 across the whole sweep**, the sanity check that
matters: it uses no Fisher, so nothing in the Fisher machinery perturbs the training
loop, and all variation in the other rows is attributable to the anchor.

### 2.1 But the single-seed sweep overstates the negative too

Re-running the most favourable single-seed point (32 batches, where the random control
appeared to tie naive exactly) with **3 repeats** removes most of what looked decisive:

| method | final accuracy | mean forgetting |
|---|---|---|
| naive | 0.824 ± 0.036 | +0.101 ± 0.049 |
| EWC diagonal | 0.843 ± 0.025 | +0.069 ± 0.028 |
| EWC block — biological | 0.838 ± 0.024 | +0.104 ± 0.024 |
| EWC block — matched random | 0.850 ± 0.022 | +0.069 ± 0.049 |

Everything clusters in 0.069–0.104. **Nothing resolves against naive** (the diagonal's
edge is 0.032 ± 0.057), and the biological-versus-random difference is
0.035 ± 0.055 — a **tie at 0.6σ**, not a loss.

So the previous fire's "the biological partition is *worse* than its matched control at
1.9σ" does not reproduce: at 32 batches with repeats it is a tie. What survives is the
weaker and still-useful statement — **the biological synapse partition shows no
advantage over a size-matched random one, and no anchoring variant shows a resolved
advantage over the naive baseline.** The earlier 1.9σ was seed luck, which is exactly
the failure mode this project has had to correct twice already.

## 3. A second, unexpected finding: the EWC family degrades as its Fisher improves

The diagonal's forgetting goes **+0.063 → +0.125 → +0.250** as the batch count rises
from 8 to 128, with accuracy collapsing from 0.826 to **0.701**. A better-estimated
Fisher is a *stronger* penalty at fixed λ, so the method moves steadily further into
over-constraint — and at 128 batches it is losing a fifth of its accuracy to a penalty
that is supposed to be protecting it.

This was partly masked before by an asymmetry I had introduced: `trace_normalise`
rescales the *block* Fishers to unit mean weight but the diagonal was left raw, so the
two families sat at different effective strengths and λ meant different things. Fixed —
both families are now normalised per task — and the fix makes the diagonal look *worse*,
not better (+0.052 → +0.063 at 8 batches).

The deeper lesson is that **λ is not transferable across Fisher quality** any more than
it is across partitions. An EWC comparison that holds λ fixed while the Fisher estimate
improves is comparing over-constraint against granularity. Any future EWC experiment on
this benchmark has to retune λ jointly with the Fisher batch count, and should report
the pair.

## 4. What this settles

The negative result now rests on three supports:

1. The biological block partition does not beat the diagonal, naive, or its matched
   random control at the default Fisher estimate (3 repeats).
2. It does not do so at **any** of three Fisher batch counts (8, 32, 128), so the
   statistical explanation is ruled out.
3. The bio-versus-random comparison **flips sign** across those settings, and at 3
   repeats it is a tie — which is what a null effect looks like.

And one correction to the previous fire's write-up: its 1.9σ "biology is worse than its
control" does not reproduce with repeats. The honest claim is *no advantage*, not *a
disadvantage*.

**Conclusion: transferring the basis finding from the linear-Gaussian reduction to a
trained connectome-constrained network does not work, and it is not an artefact of a
poorly estimated Fisher.** The analogy between "block structure of the precision matrix
over neurons" and "partition of the synapses by endpoint cell class" is not valid —
they are different partitions of different spaces, and the linear result never required
the second to behave like the first.

Combined with the previous fires, the rate-network picture is:

- **replay** drives forgetting to ~0 with the best accuracy — the only method that
  clearly works, at ~2σ over naive;
- **no Fisher-anchoring variant resolves a benefit over naive**, in the neuron diagonal
  basis or in a biological block basis, at any λ or Fisher batch count tried;
- and the family is **badly behaved as its curvature estimate improves** (§3), which is
  the most interesting thing this fire produced.

That last point is consistent with the project's theory: LGCL predicts the diagonal
projection costs 33% excess error on this connectome, so a method built on it is
fighting a losing battle — and improving the estimate of *which* projection to make
does not fix a projection that should not be made at all.

## 5. Limits

- **Single seed** for the batch sweep. The *pattern* — biology never consistently
  better — holds across three batch counts and agrees with the independent 3-repeat
  result at 8 batches, but the individual numbers carry ±0.05.
- λ was held at 0.1 throughout, which the §3 finding shows is not neutral: the correct
  comparison would retune λ at each batch count, and that retuning is the next
  experiment rather than this one.
- Three tasks, so "mean forgetting" averages two numbers.
