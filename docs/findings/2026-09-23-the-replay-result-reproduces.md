# E61 — the network line's headline replay result **reproduces**, and stronger than published

**Date:** 2026-09-23
**Script:** `experiments/e61_replay_recreation.py`
**Artifact:** `runs/e61_replay96_step{8,16}.json` (per-step 48 still running)
**Context:** `2026-09-22-the-replay-result-has-no-artifact.md` (e62), `2026-09-22-replay-budget-inversion.md`, plan rules 8, 17, 20

---

## 1. What was missing, and what has now landed

`e62` found that the network line's only surviving positive result had **no artifact**: the claim was

> replay (pool 96, per-step 8) reduces forgetting to **−0.010 ± 0.006** against naive's
> **+0.066 ± 0.019** — **4.2σ** — at **0.968 ± 0.013** accuracy

and a census of all 77 stored runs found `replay_per_task: 16` eighteen times and
`replay_batch: 16` eleven times, with no 96, no 8, and no 48 anywhere. The nearest instance that did
exist gave the contrast at **−1.17σ with `+----` signs**.

`e62` launched a recreation rather than arguing about the number. Its per-step-8 arm has landed.

## 2. Result: the claim checks out, on all four of its numbers

| quantity | published | **recreated** | agree? |
|---|---|---|---|
| naive forgetting | +0.066 ± 0.019 | **+0.0729 ± 0.0151** | yes |
| replay forgetting | −0.010 ± 0.006 | **−0.0125 ± 0.0039** | yes |
| replay final accuracy | 0.968 ± 0.013 | **0.9681 ± 0.0078** | yes |
| replay − naive contrast | 4.2σ | **−0.08542 ± 0.01293 = 6.61σ** | yes, stronger |

The `naive` arm is additionally **bit-identical to `e8_hardened`'s** (0.9139 accuracy, +0.0729
forgetting), which is the check `e62` ran on the partial log: the reconstructed configuration is the
same configuration, so the comparison is like-for-like rather than approximate.

So `e62`'s "the claim cannot be checked either way" resolves in the claim's favour. Three of the four
numbers agree within their own error bars, and the axis that had no artifact is the axis that
reproduces.

## 3. Under the per-seed discipline — which is where the published number is weakest

The published 4.2σ was never given a per-seed structure. This one has five replicates and the two arms
are paired (same replicate seed within one run):

| per-step 8, replicate | naive | replay | Δ |
|---|---|---|---|
| 0 | +0.04167 | −0.01042 | **−0.05208** |
| 1 | +0.05208 | −0.02083 | **−0.07292** |
| 2 | +0.10417 | 0.00000 | **−0.10417** |
| 3 | +0.11458 | −0.01042 | **−0.12500** |
| 4 | +0.05208 | −0.02083 | **−0.07292** |
| **mean** | **+0.07292** | **−0.01250** | **−0.08542** |

* **Signs are 5/5 negative** on the paired difference. The sign test's p is 0.0625, which is the
  *floor* for n = 5 — a five-replicate experiment cannot reach 0.05 this way, so the sign record is
  unanimous but not independently significant. The paired σ is what carries it.
* **Leave-one-out σ ∈ [5.19, 7.35]** and **no removal flips the sign.** The published figure had no
  such check, and the *nearest existing artifact* had a LOO range of [0.67, 5.66] — an eight-fold
  spread across one seed. This one does not have that pathology.
* **Single-replicate leverage 0.77** (1 = one replicate is worth a whole sem), against `e46`'s
  three-seed claim where the sixth seed destroyed the effect.
* Unpaired σ is **5.48**, so pairing helps here (ρ > 0 as expected, both arms share the replicate
  seed) but the conclusion does not depend on the pairing convention.
* Replay's own forgetting is **3.21σ** from zero, against the published claim's implicit **1.67σ** —
  so even the weaker of the two readings survives, which the published numbers did not.

## 4. What this does to the line's status

`e62` summarised the network line as *"every well-powered measurement is a null"*, on the strength of
`e46` (+0.0039 ± 0.0161 at n = 16) plus the missing artifact. That summary was **one claim too broad**:
it was true of the basis contrast and of every artifact on disk, and it assumed the unverifiable claim
would fail. It did not. The line now has **one measured, artifact-backed, seed-robust positive result**
— replay at pool 96 / per-step 8 — and it is the only one.

This is the mirror image of the C1 story. There, six fires of per-seed checks turned a 32.7σ refutation
into 2.7σ about the rewiring rule. Here, the per-seed check *strengthens* the number it is applied to
(4.2σ → 6.61σ) and removes the single-seed fragility that the nearest available artifact displayed.
The discipline is not a demolition device; it is what tells these two cases apart.

## 5. Limits — the honest form

- **This is a recreation, not the original run.** It cannot confirm that the missing artifact held
  −0.010 ± 0.006; it shows that this configuration, with these seeds, produces that number and
  stronger. Combined with the ×3 agreement of the naive arm across two independent runs, the most
  probable history remains a real run whose JSON was overwritten.
- **n = 5.** Plan rule 20 says treat below ~ten as provisional, and that rule is not suspended because
  the answer is convenient. What n = 5 *does* support is the absence of the failure mode that killed
  `e46`: LOO min σ 5.19 and leverage 0.77 leave no single replicate carrying the effect. A
  sixteen-replicate version of this one configuration is the obvious next run; note that this is
  exactly the move that killed `e46`'s −0.0648, so it is a real test and not a formality.
- **The budget inversion is half checked, and the half that is checked reproduces.** Per-step 16
  (claimed +0.017, measured **+0.0104**) has landed; per-step 48 (claimed +0.007) is still running. See
  §7, which is where the finding's second half now lives.
- **The other arms' spread is not small.** `e54`'s census puts this `naive` computation in a cluster of
  its own (`shared_head`/`readout_size` differ from the main cluster), so the contrast carries both
  arms' spread; the paired sem handles what sharing the replicate seed can remove, and no more.
- **Pool size is held at 96** throughout, as the finding names; "best when tuned" is not tested.

## 7. The budget inversion, which is the other half of the claim, and it reproduces too

The published finding made **two** assertions in one breath: that replay at pool 96 / per-step 8 drives
forgetting negative, and that **more replay is worse** — per-step 8 → −0.010, 16 → +0.017, 48 → +0.007.
The second is a claim about a *shape*, and `e62` found the artifact behind it missing along with the
first.

Per-step 16 has now landed:

| per-step | replay forgetting | claimed | naive minus replay contrast | paired σ |
|---|---|---|---|---|
| 8 | **−0.01250** | −0.010 | −0.08542 ± 0.01293 | **6.61** |
| 16 | **+0.01042** | +0.017 | −0.06250 ± 0.01545 | **4.05** |
| 48 | — | +0.007 | — | — |

So the shape holds where it is checkable: the smaller per-step amount is the better one, and it is the
only one of the two that drives forgetting negative. The claimed +0.017 against the measured +0.0104 is
a 0.007 discrepancy — with the claim carrying no error bar of its own, that is one replicate's worth.

**And the inversion is itself a contrast, so it can be tested paired rather than compared as two
means.** Both per-step arms of one configuration run on the *same* replicate seeds, so
`forgetting(16) − forgetting(8)` is a matched quantity over five replicates:

| contrast | delta | sem (paired) | σ | signs | LOO σ range | flips | leverage |
|---|---|---|---|---|---|---|---|
| **16 − 8** | **+0.02292** | 0.00390 | **5.88** | `+++++` | [4.70, 8.66] | no | 0.80 |

**The inversion is 5.88σ on the same five replicates that the effect itself rests on, with all five
signs agreeing and no leave-one-out removal changing it.** That is a stronger statement about the shape
than the original finding made — it had three point estimates, and this has a paired σ.

One distinction worth keeping, because the two numbers are easy to conflate: per-step 16's replay
forgetting is **+0.01042 ± 0.0066, i.e. 1.58σ from zero** — it is *not* resolved as positive on its
own — while its contrast against `naive` is −0.0625 at 4.05σ. So "per-step 16 is worse than per-step 8"
is established at 5.88σ, and "per-step 16's forgetting is positive" is not. The comparison that carries
the shape is the paired one, not the sign of a single arm.

## 6. Where the numbers live

```bash
uv run python -m experiments.e61_replay_recreation
```

reads `runs/e61_replay96_step{8,16,48}.json` and writes
`runs/e61_replay_recreation_analysis.json`. Adding the remaining two draws requires no code change —
the script reports the inversion section as soon as a second artifact exists.
