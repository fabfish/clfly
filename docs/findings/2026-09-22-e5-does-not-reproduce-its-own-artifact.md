# E41 — `e5`'s headline is one cell of an artifact that does not reproduce it, and the association is carried by one seed of three

**Date:** 2026-09-22
**Script:** `experiments/e41_anisotropy_seed_fragility.py` (read-only over `runs/`)
**Artifacts:** `runs/e41_anisotropy_seed_fragility.json`, `runs/e5_anisotropy.json`
**Context:** `2026-09-22-e5-anisotropy-axis.md`, plan §C1 and measurement rule 3

---

## 1. Why this matters more than it looks

`e5` is the experiment the plan uses to **correct `e2`**: "vary the task's spectral concentration
directly, at fixed topology, fixed support and fixed rank, and the gap is U-shaped with an overall
negative association with flatness (Spearman **−0.75**) — i.e. more anisotropy gives a larger gap."
That is the project's *replacement mechanism*, and this line has been quoting it — including in the
C1 topology write-ups — as the direction that survived when the interference story did not. So it is
worth checking against its own artifact.

## 2. The cited artifact does not reproduce the published table

`2026-09-22-e5-anisotropy-axis.md` cites `runs/e5_anisotropy.json` and its header says **"1 seed"**.
That file contains **21 points across three seeds**, `config.seeds = 3`. Comparing the published table
against its seed-0 subset, cell by cell:

| column | cells disagreeing |
|---|---|
| `flattening` | 0 of 7 |
| `effective rank` | 0 of 7 |
| `top_eig_share` | 0 of 7 |
| `overlap` | 0 of 7 |
| **`gap:EWC`** | **4 of 7** |
| **`bio−rand`** | **3 of 7** |

**Every geometry cell reproduces within rounding and every realized-error cell does not.** That split
is exactly the plan's rule 5 — eigenvector-derived quantities are bit-reproducible, realized
estimation errors are not — and it identifies the artifact as a re-run after a change that moved
realized errors while leaving the spectrum alone. The worst two cells:

| `kappa` | column | published | stored | ratio |
|---|---|---|---|---|
| 0 | `gap:EWC` | **+0.139** | **+0.0621** | **2.2×** |
| 0 | `bio−rand` | **−0.030** | **−0.0026** | **11×** |

I cannot recover the earlier run: `runs/` is gitignored and has no history, so I cannot tell whether
the published `+0.139` was a transcription error or a genuine pre-fix computation. What is checkable
is that **the file the finding cites does not contain it**, and that the finding's provenance line
("1 seed") does not describe the file either.

## 3. The headline number and the U-shape both come from one of those cells

Substituting **only** the published `gap:EWC(kappa=0) = 0.139` into the otherwise stored seed-0 row:

| | Spearman(flattening, gap) | argmin |
|---|---|---|
| stored seed 0 | **−0.9643** | `kappa = 0` |
| with the published cell | **−0.7500** | `kappa = 0.5` |

The published −0.75 is reproduced **exactly** (−0.7500 to machine precision), and the same
substitution is what moves the curve's minimum from `kappa = 0` to `kappa = 0.5`. So the finding's
two headline claims — the number, and *"the gap dips to a minimum at moderate concentration
(`kappa ≈ 0.5`) before rising steeply to +1.20. There is an easy middle regime that neither of the
two ends shows"* — are both that one cell. **With the stored value there is no U-shape**; the gap is
smallest at `kappa = 0`.

Note the direction of the correction: the stored data gives a *stronger* seed-0 association than the
published one (−0.964 against −0.75). The discrepancy does not weaken `e5`'s seed 0 — it removes the
shape claim and puts the artifact's provenance in doubt.

## 4. On the artifact that exists, the association is carried by one seed of three

Each seed is a complete repeat of the whole `kappa` sweep, so it is the honest unit. Both metrics are
reported: the relative gap `e5` uses, and the **absolute excess** that the plan's measurement rule 3
prescribes (`absolute = gap × oracle_final`, exact because `gap_vs_oracle` returns a relative excess
of final average error — verified in the source).

| scope | n | ρ(gap, flattening) | p | ρ(absolute, flattening) | p |
|---|---|---|---|---|---|
| pooled, all points | 21 | −0.282 | 0.216 | **+0.040** | **0.862** |
| `kappa` means | 7 | −0.643 | 0.119 | **+0.143** | **0.760** |
| seed 0 | 7 | −0.964 | 0.0004 | −0.929 | 0.003 |
| seed 1 | 7 | −0.321 | 0.482 | +0.214 | 0.645 |
| seed 2 | 7 | +0.107 | 0.819 | +0.071 | 0.879 |

**The association is real in one seed of three.** Neither pooling nor averaging over `kappa` reaches
significance, and under the metric the plan requires it is **+0.040 with p = 0.86** — nothing at all.
So `e5`'s "more anisotropy gives a larger gap" is *supported by one realisation* and is **not
established** by this artifact. That is a weaker statement than "it is false", and it is the one the
data supports.

## 5. A nuance that cuts against the easy fix

It would be tidy to conclude "use the absolute metric and the association returns". It does not.
The per-`kappa` spread across the three seeds:

| `kappa` | relative gap per seed | CV | absolute excess per seed | CV |
|---|---|---|---|---|
| 0 | 0.062 / 0.576 / 0.370 | 0.77 | 0.0032 / 0.0308 / 0.0219 | 0.76 |
| 1 | 0.134 / 0.149 / 0.189 | 0.18 | 0.0061 / 0.0067 / 0.0104 | 0.30 |
| 2.5 | 0.365 / 0.297 / 1.509 | 0.94 | 0.0092 / 0.0082 / 0.0421 | 0.97 |
| **4** | **1.208 / 1.393 / 0.009** | 0.86 | **0.0174 / 0.0191 / 0.0001** | 0.86 |

The coefficient of variation is **no smaller for the absolute excess** (0.30–0.97 against 0.18–0.94).
At `kappa = 4` the absolute excesses are 0.0174, 0.0191 and **0.0001** — seed 2's EWC lands on the
oracle — while the oracle's own error is stable across the same three seeds (0.01444, 0.01372,
0.01207). So rule 3's prescription removes the *ratio-of-two-small-numbers* pathology, which is what
it was written for, and it does **not** remove `e5`'s seed variance. Any re-run has to buy seeds, not
a better metric.

## 6. What this does to the plan

| statement | status |
|---|---|
| "Spearman(flattening, gap) = −0.75" | **not in the cited artifact** — the stored seed-0 value is −0.9643, and −0.7500 is reproduced exactly by substituting one published cell |
| "the gap dips to a minimum at `kappa ≈ 0.5` … an easy middle regime" | **withdrawn** — the stored minimum is at `kappa = 0`; the dip is the same substituted cell |
| "more anisotropy gives a larger gap, the opposite sign to `e2`" | **not established** — real in 1 of 3 seeds, p = 0.216 pooled, and **+0.040 (p = 0.86)** under the prescribed absolute metric |
| "`e5` corrects `e2`'s confounded trend" | **cannot carry that weight as it stands** — a correction resting on one of three realised sweeps is itself a single-draw result, which is the trap this project has fallen into four times |
| the finding cites 1 seed; the artifact has 3 | **provenance mismatch**, recorded |

I have been citing `e5`'s direction in the C1 write-ups. Those citations should be read as citing a
one-seed result from now on, and the plan's C1 and §C2 discussions that lean on `e5` are annotated
accordingly.

## 7. Limits

- **The earlier run is gone.** `runs/` is gitignored with no history, so this finding establishes
  that the cited artifact does not contain the published numbers, not what produced them.
- **n = 3 seeds.** A within-seed Spearman on 7 `kappa` points has a wide interval: seed 0's −0.964 has
  p = 0.0004 and seed 1's −0.321 has p = 0.48, and three seeds is not enough to put an interval on
  the *between-seed* spread of ρ. Section 4's point is that the three disagree by more than any of
  them is precise, which is what `e12`'s control-draw lesson should have made us expect.
- **The seeds are independent sweeps.** The docstring's "reuse the same `z` draw" is *within* a seed
  across `kappa` values, so the three seeds are three draws of the whole manipulation, which is what
  makes the per-seed view the right one.
- **The absolute column is derived**, not stored — a re-run should store it directly, and rule 8's
  argument for per-seed values extends to per-seed *metrics*.
