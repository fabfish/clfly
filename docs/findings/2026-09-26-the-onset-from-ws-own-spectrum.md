# The onset from `W`'s own spectrum: the eigenvalue gap orders the residual rank perfectly at cs 300 — and not at cs 800

*2026-09-26 13:05, `runs/e238_weight_spectrum.json` through `e238_weight_spectrum.py`. `stable_weights` ends in
`(W * (rho / radius))`, a **pure scalar rescale**, so with `Ŵ = W / radius`: `W(rho) = rho Ŵ`,
`G(rho) = (I − rho Ŵ)^-1` and `eig(G) = 1/(1 − rho λ̂)`. The **eigenvalue** side of the collapse is therefore exactly
computable from `Ŵ`'s leading eigenvalues — no tasks, no seeds, no solves — and `e237`'s measured whole-matrix rank
becomes a test rather than a description. Two registered claims; **S2 is MET at cs 300 and falsified at cs 800**.*

## 1. `Ŵ`'s leading spectrum, and how non-normal it is

| cs 300 | `\|λ̂₁\|` | `\|λ̂₂\|` | `\|λ̂₃\|` | gap `1−\|λ̂₂\|` | `σ₁` | `σ₁/\|λ̂₁\|` |
|---|---|---|---|---|---|---|
| `real` | 1.0000 | 0.6793 | 0.5380 | **0.3207** | 1.974 | 1.97 |
| `alloy1` | 1.0000 | 0.9816 | 0.9816 | 0.0184 | 6.462 | **6.46** |
| `inalloy1` | 1.0000 | 0.9985 | 0.9985 | 0.0015 | 4.041 | 4.04 |
| `erdos_renyi` | 1.0000 | **1.0000** | 0.9960 | ~0 | 1.989 | 1.99 |

| cs 800 | `\|λ̂₁\|` | `\|λ̂₂\|` | `\|λ̂₃\|` | gap | `σ₁` | `σ₁/\|λ̂₁\|` |
|---|---|---|---|---|---|---|
| `real` | 1.0000 | 0.7875 | 0.7104 | 0.2125 | 1.873 | 1.87 |
| `alloy1` | 1.0000 | **1.0000** | 0.8299 | ~0 | 5.986 | **5.99** |
| `inalloy1` | 1.0000 | **1.0000** | 0.9675 | 0.0000 | 5.691 | 5.69 |
| `erdos_renyi` | **1.0090** | 1.0090 | 1.0072 | ~0 | 2.023 | 2.01 |

Two facts before any claim. **The one-side nulls are strongly non-normal**: `σ₁/|λ̂₁|` is 5.7–6.5 for `alloy1` and
`inalloy1` against 1.9–2.0 for `real` and `erdos_renyi` — randomising one side of every edge destroys the near-symmetry
that keeps the spectral radius and the largest singular value close. And **`erdos_renyi` at cs 800 has `|λ̂₁| = 1.0090`
for a matrix built to have radius exactly 1**: `stable_weights` estimates the radius from a two-eigenvalue ARPACK
call, and a near-degenerate leading pair makes that estimate ~0.9% low, so that cell's *effective* `rho` is 0.9%
higher than nominal — an instrument fact about every cell of this line that uses `stable_weights`.

## 2. S2: the second eigenvalue orders the residual rank — at cs 300 perfectly, at cs 800 not at all

S2 registered that the family keeping the largest measured whole-matrix rank has the largest `|λ̂₂|`.

| cs 300, `rho` 0.99 | `real` | `alloy1` | `inalloy1` | `erdos_renyi` |
|---|---|---|---|---|
| `|λ̂₂|` | 0.6793 | 0.9816 | 0.9985 | 1.0000 |
| measured `pr_G` (`e237`) | 1.04 | 1.05 | 1.08 | **4.14** |

**MET — the two orderings are identical.** The eigenvalue gap is what decides how much rank survives near
criticality at cs 300: a family whose second eigenvalue sits 0.32 below the leading one loses *all* of its residual
rank, while one with a degenerate leading pair (`erdos_renyi`) keeps 4.14.

| cs 800, `rho` 0.99 | `real` | `alloy1` | `inalloy1` | `erdos_renyi` |
|---|---|---|---|---|
| `|λ̂₂|` | 0.7875 | **1.0000** | **1.0000** | 1.0090 |
| measured `pr_G` (`e237`) | 1.08 | **29.94** | **1.26** | 4.35 |

**FALSIFIED at cs 800, and by the sharpest possible counterexample**: `alloy1` and `inalloy1` have the same `|λ̂₂|`
(1.0000) to four decimals and their whole-`G` ranks differ by **24×** (29.94 against 1.26). Two operators with
near-identical modulus spectra, one of which is 24 times rank-richer, says the eigenvalue *moduli* are not sufficient
— whatever separates them is in the eigenvectors or in the non-normal structure, and `σ₁/|λ̂₁|` does not separate them
either (5.99 against 5.69).

## 3. S1: the ordering of the predicted eigencollapse matches at cs 300 and fails at cs 800

The prediction is `pr_eig(rho)` = the participation ratio of `|1/(1 − rho λ̂_i)|²` over the 40 leading modes.

| cs 300, `rho` 0.99 | `real` | `alloy1` | `inalloy1` | `erdos_renyi` |
|---|---|---|---|---|
| predicted `pr_eig` | 1.02 | 3.20 | 6.91 | 11.44 |
| measured `pr_G` | 1.04 | 1.05 | 1.08 | 4.14 |

The **ordering is identical** (the prediction is MET at cs 300 and at low `rho`) and the **magnitudes are not**: the
prediction is up to **6.4× too high**, and it is furthest off for `alloy1` — the most non-normal family
(`σ₁/|λ̂₁| = 6.46`). That is the expected direction: an eigenvalue rank cannot see the singular-value collapse that
non-normality adds, so the measured operator collapses *further* than its spectrum predicts.

At cs 800 the ordering fails outright: predicted 1.02 / 2.15 / 3.02 / 3.28 against measured 1.08 / 29.94 / 1.26 /
4.35 — `alloy1` is the *lowest* predicted and by far the *highest* measured. Both claims therefore say the same
thing: **at cs 300 the collapse is an eigenvalue-gap phenomenon, and at cs 800 it is not.**

## 4. What this cannot do

- **One drawing per cell** (`seed0`), and the cs-800 counterexample is exactly a single drawing of each family — which
  is the same exposure `e232` measured for the task-side asymmetry (10.10×, 1.06×, 0.23× across three drawings). The
  cs-800 falsification is therefore a real refutation of the *claim* and an unmeasured property of the *families*.
- **40 modes**: the prediction cannot be read at low `rho`, where hundreds of modes carry the Frobenius norm, and the
  claim is only evaluated where the leading modes dominate (`rho >= 0.9`).
- **Eigenvalues are not singular values** for a non-normal operator; that gap is what S1 tests rather than an error.
- **`rho` rescales the whole matrix**, so nothing here separates propagation depth from weight scale — although this
  measurement does make that explicit: the rescale is the *only* rho dependence in `W`, and everything else follows
  from `1/(1 − rho λ̂)`.
