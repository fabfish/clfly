# The penalty's cost is overlap-dependent: at λ = 1.0 the same two artifacts make `naive` better and `ewc-block` worse

**Date:** 2026-09-25
**Read of:** `runs/e193_r32_overlap025_methods_40reps.json` (λ = 1.0, overlap **0.1429**, 40 replicates) against
`runs/e153_r32_overlap1_methods_40reps.json` (λ = **1.0**, overlap **1.0**, 40 replicates) — the **λ-matched** pair,
which is what makes the comparison available at all (see
`docs/findings/2026-09-25-a-333x-penalty-step-dressed-as-an-overlap-effect.md`).
**Instrument:** `e151`'s `load_arm`/`paired`, applied by hand; the two-point read itself is `e188 --dose`/`e191 --dose`.

---

## 1. The interaction, on one axis at one penalty strength

| arm | forgetting at overlap 0.1429 | at overlap 1.0 | **change (0.1429 − 1.0)** | σ |
|---|---|---|---|---|
| **`naive`** | +0.0891 | +0.1068 | **−0.0177 ± 0.0104** | **1.71** |
| **`ewc-block`** | +0.1086 | +0.0633 | **+0.0453 ± 0.0110** | **4.10** |
| `ewc-block-rand` | +0.0898 | +0.0740 | +0.0159 ± 0.0108 | 1.47 |

**The two arms move in opposite directions on the same manipulation, at the same penalty strength, measured on the
same pair of artifacts.** Sharing less of the input makes the *unpenalised* arm forget less — the intuitive direction,
and the one the overlap axis's own two-point contrast found for `naive` at λ = 3e-3 — while it makes the
*block-penalised* arm forget **more, by 4.10σ**. The interaction contrast is the difference of the two:
**+0.0630**.

`ewc-block-rand` moves with `ewc-block`'s sign (+0.0159) and is unresolved, so the ordering across the three arms at
this axis point is `ewc-block` > `ewc-block-rand` > `naive` in change, with only the first resolved.

## 2. Why this is not the drift account, and not the first-order account either

The same two artifacts carry the diagnostics, and they say the *body* is not what moved:

| arm | Δθ drift, tasks 1 and 2 | Δ bias step, tasks 1 and 2 | Δ forgetting |
|---|---|---|---|
| `naive` | +0.0011 / +0.0033 | +0.0161 / +0.0578 | −0.0177 (1.71σ) |
| `ewc-block` | +0.0008 / +0.0035 | −0.1410 / +0.1607 | **+0.0453 (4.10σ)** |
| `ewc-block-rand` | +0.0005 / +0.0037 | −0.0947 / +0.2101 | +0.0159 (1.47σ) |

**The body drifts by the same ±0.004 in every arm** — the penalised arm's 4.10σ change in forgetting comes with a
body displacement indistinguishable from the unpenalised arm's. And the first-order interference term for the same
arms moves **+0.0010 = 0.3σ** (`e191 --dose`, recorded). So **two of this project's instruments for this quantity —
the drift and the first-order account — are both flat where the 4.10σ is**, which is the `e139` shape (the θ-only
form cut by 98% while forgetting moved) appearing now as a *penalty-overlap interaction* rather than as a penalty
effect.

## 3. What this licenses, and what it does not

- **licensed**: *at λ = 1.0, the effect of the input-overlap level on forgetting depends on whether the arm carries
  the block penalty* — `naive` better by 1.71σ, `ewc-block` worse by 4.10σ, on the same manipulation and the same
  pair of runs. This is the first interaction between the penalty and the overlap axis in the corpus; the λ = 3e-3
  rows of `e188` had only `naive` and no comparator at the same λ.
- **not licensed**: any magnitude against the λ = 3e-3 family. `e153` and the level share λ = 1.0 and one partition
  draw; λ = 1.0 is not a neutral setting (`e153`'s own finding records that at λ one the wiring family's arms are the
  λ = 1.0 arms), so the claim is *an interaction within the family*, not a penalty-vs-overlap response surface.
- **not licensed either**: that the interaction is mediated by the offsets. The bias step moves by **−0.141 / +0.161** on
  the penalised arm against **+0.016 / +0.058** on `naive` — so the offset channel moves **three to nine times more** in the
  arm whose forgetting changes 4.10σ — but with one axis point on each side and a paired difference of that size
  against an unresolved one, nothing here separates "the offsets are the mechanism" from "the offsets are the
  symptom". The 0.3333 and 0.6000 points are what would.

**And one correction to this table, made before it was committed**: its first version carried `naive`'s bias-step
changes as `−0.0061 / +0.0107`, which are not in either artifact — the values above are read from the aggregates
(1.1908/1.2847 at 0.1429 against 1.1747/1.2269 at 1.0). The other two rows were right, and the error was in the one
row whose arm moves *least*, which is the row a reader would be least likely to check.

## 4. Falsifiers

- **The interaction** dies if the 0.3333 or 0.6000 points put `naive` and `ewc-block` on the same side of their
  overlap-1.0 values (i.e. if the sign flip is a two-point accident) — the levels are running and this read will be
  applied to them unchanged.
- **§2's flatness** dies if the drift or the interference term moves ≥2σ at either new point; both are printed by the
  same commands.
- **The λ-matched pairing** dies if a further field differs that `ewc-block` reads — the read prints every admitted
  difference, and the only one left is `methods`/`replay_*`, all inert by the runners' code paths.

## Reproduce

```
uv run python -m experiments.e191_interference_across_lines --dose runs/e193_r32_overlap025_methods_40reps.json
uv run python -m experiments.e188_overlap_contrast       --dose runs/e193_r32_overlap025_methods_40reps.json
```
