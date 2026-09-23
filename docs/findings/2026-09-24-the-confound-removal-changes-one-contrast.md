# `e135`: the confound's removal changes one contrast — and it is the paper's strongest one

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, unchanged; artifacts `runs/e135_r32_methods_plastic.json` and
`runs/e135_r32_methods_frozenbias.json`, five methods × five replicates × two arms.
**C0a passed on three controls at once**: the plastic arm reproduces `runs/e8_hardened_basis.json`'s **`naive`**
(+0.0417, +0.0521, +0.1042, +0.1146, +0.0521) and **`ewc`** (+0.0417, +0.0104, +0.0313, −0.0312, +0.0521) rows
and `runs/e61_replay96_step8.json`'s **`replay`** (−0.0104, −0.0208, +0.0000, −0.0104, −0.0208) row
**per replicate** — so the `ewc` match says the *Fisher's own arithmetic* is epoch-stable and not merely the
plastic arm.
**Pre-registration:** `docs/findings/2026-09-24-the-method-table-with-the-confound-removed-preregistered.md`.
**Context:** `e125` measured that **70%** of this configuration's `naive` forgetting lives in the 800 per-neuron
offsets no penalty covers, and `e137` that **the penalty relocates adaptation into that channel** — so the
question is whether the five methods' *comparison with each other* survives its removal.

---

## 1. The table, and both predictions fail on one arm

| method | plastic | frozen-bias | level change | contrast vs naive, plastic | contrast, frozen | contrast's move |
|---|---|---|---|---|---|---|
| naive | +0.0729 | +0.0250 | −0.0479 | — | — | — |
| **ewc** | +0.0208 | **−0.0104** | −0.0312 | −0.0521 | −0.0354 | **+0.0167 ± 0.0393 = 0.42σ** |
| **ewc-block** | +0.0604 | +0.0167 | −0.0437 | −0.0125 | −0.0083 | **+0.0042 ± 0.0202 = 0.21σ** |
| **ewc-block-rand** | +0.0438 | +0.0104 | −0.0333 | −0.0292 | −0.0146 | **+0.0146 ± 0.0303 = 0.48σ** |
| **replay** | **−0.0125** | **−0.0042** | **+0.0083** | **−0.0854** | **−0.0292** | **+0.0563 ± 0.0252 = 2.23σ** |

**The three Fisher-based penalties are exactly as the code predicts: their contrasts against `naive` are unchanged
within half a sigma** — the bias's contribution is **method-independent** for them, because no penalty touches it.
**And replay is not.** Its advantage over naive is **cut by 66%, from −0.0854 to −0.0292**, the only contrast that
moves and the only level that *rises*.

So **P1 fails** (`|Δ| < 2σ` for every contrast) and **P2 fails** (every level falls) — **exclusively on the
replay arm** — while the **falsifier does not fire**: it was registered at **≥ 3σ** and replay's move is
**2.23σ**. **The registration named replay as the likeliest mover and did not predict which** (*"its arm has
something the others do not"*), which is the registration behaving as a design: the risk was stated, it
materialised, and it materialised at a size the registration had already bounded.

## 2. Why replay, and it is the arithmetic of a baseline

Replay's own forgetting is **below zero** in both arms (−0.0125 and −0.0042): it has already driven the forgetting
to nothing, so **there is no bias-channel forgetting left in it to remove**. `naive` had **0.0479** of its
forgetting in that channel. So freezing the bias in both arms helps the *baseline* a great deal and replay not at
all, and the difference between them shrinks because **their comparison was partly a comparison between a method
that forgets and a baseline that forgets through a channel the method does not use.**

**Which makes the paper's strongest network claim its most confound-sensitive one.** §4.2's replay row is
**−0.0854 ± 0.0129 = 6.6σ**, described there as the number the project had to *recreate*; with the unpenalised
channel removed from every arm it is **−0.0292**, and the change is **2.23σ** — below the registered falsifier and
well above the registered "unchanged". **A method that drives the forgetting to zero cannot be credited with the
forgetting a baseline does not have to suffer either.**

**And the accuracies move in the same direction**: replay's final accuracy *falls* from **0.9681 to 0.9472** while
the three penalty arms' mostly *rise* (naive 0.9139 → 0.9333, ewc-block 0.9153 → 0.9319, ewc-block-rand
0.9278 → 0.9333, ewc 0.9222 → 0.9181). **Replay is the one method that gets worse on both metrics when the
confound is removed from all five arms.**

## 3. What this does and does not change

**Changes §4.2's ordering as a statement about methods.** With the bias frozen in every arm, the ranking by
forgetting is **ewc (−0.0104) < replay (−0.0042) < ewc-block-rand (+0.0104) < ewc-block (+0.0167) < naive
(+0.0250)** — so **diagonal EWC is now the best method and replay is second**, where the plastic table has replay
first by a wide margin. **The paper's "replay is the stronger method in every setting" is a claim about the
*plastic* configuration**, and this run shows it is partly a claim about the baseline's unpenalised channel.

**Does not change**: the penalties' mutual ordering (ewc best, block worse, matched-random between) is identical
in both arms, and that is the paper's central network result — the *basis* question — with the confound removed.
**The three Fisher arms are confound-robust; the replay comparison is not.**

**And it does not say replay is bad.** Replay's forgetting is ≤ 0 in both arms, which no penalty achieves. What it
says is that **its margin over naive is 66% smaller when the thing naive forgets through is taken away**, and that
the two facts a reader should hold together are *"replay is the only method that reaches zero"* and *"its margin
is mostly against a baseline with a confound"*.

## 4. What this cannot settle

- **Five replicates**, matching the paper's table, so 2.23σ is a suggestion and 0.2σ is a bound that five points
  can carry for a *small* effect only. **The falsifier's threshold is why this is not a refutation**, and the
  honest form is that the contrast moved by more than the registration allowed it to and less than the
  registration's falsifier.
- **One configuration**, read-out 32 with three tasks, so this is the read-out where the confound is largest
  (70%: `e134` measures 89% and 83% at read-out 128 and 1307, where the *absolute* amounts are smaller).
- **The within-arm comparison is untouched by §2's arithmetic**, and it should be said: the three penalties'
  ordering and replay's own level are statements inside one arm, and every one of them stands as it was. **What
  moves is only the contrast against `naive`.**
- **And the two arms are the same seeds but different epochs' comparators for `naive`** — `e135`'s own plastic
  arm is the control for the plastic side, and it matched three other-epoch artifacts per replicate.
