# The counterexample was a drawing — and so was the ordering that made it one: across three drawings the λ̂₂ → residual-rank relation agrees in 3 of 6

*2026-09-26 13:35, `runs/e239_weight_spectrum_drawings.json` through `e239_weight_spectrum_drawings.py` — `e237`'s
whole-matrix rank and `e238`'s second eigenvalue re-measured at three `rewire_seed` values, changing nothing else.
**Both registered claims' falsifiers fire**, and the second one takes `e238`'s surviving verdict with it.
The internal control is exact: `real`'s whole-`G` rank at `rho` 0.99 is **1.0449** at cs 300 and **1.0802** at cs 800
in all three drawings — bit-identical, because the `real` topology is not rewired, so every movement below is the
null's and not the instrument's.*

## 1. W1's falsifier fires: the 24× was drawing 0's

`alloy1 ÷ inalloy1` whole-`G` rank at `rho` 0.99:

| | drawing 0 | drawing 1 | drawing 2 |
|---|---|---|---|
| cs 300 | 0.98× | **2.39×** | 0.98× |
| cs 800 | **23.70×** | **1.00×** | 1.83× |

The registered bar was 4× in all three drawings; the ratio is below it in four of the six (size, drawing) cells and
only once far above it — **drawing 0 at cs 800, the drawing `e238` reported**. So the counterexample was that
drawing's, and by `e232`'s lesson that was the expected outcome.

## 2. W2's falsifier fires: the "same second eigenvalue" was also a drawing

`e238`'s counterexample needed `alloy1` and `inalloy1` to share a second eigenvalue while their ranks differed 24×.
Measured across drawings, the two families' second eigenvalues:

| | drawing 0 | drawing 1 | drawing 2 |
|---|---|---|---|
| cs 300 `alloy1` / `inalloy1` | 0.9816 / 0.9985 | 1.0000 / 1.0000 | 1.0000 / 0.9790 |
| cs 800 `alloy1` / `inalloy1` | 1.0000 / 1.0000 | **0.7766 / 0.9503** | 1.0000 / 0.7457 |

The registered tolerance was 0.01; the gaps run 0.0000, 0.0000, 0.0169, 0.0210, **0.1737** and **0.2543**. Only the
two cs-800 cells of drawing 0 have the degeneracy the counterexample rested on — and in drawing 1, where the two
families' second eigenvalues differ by **0.1737**, their whole-`G` ranks are equal to within 1% (1.01 against 1.01).
**The counterexample is dissolved from both ends.**

## 3. And the surviving claim of `e238` does not survive either

`e238`'s S2 was MET at cs 300 because the second-eigenvalue ordering and the measured rank ordering were identical.
Both orderings, per drawing, at `rho` 0.99:

| | λ̂₂ order | rank order | agree |
|---|---|---|---|
| cs 300, drawing 0 | `real`, `alloy1`, `inalloy1`, `erdos_renyi` | `real`, `alloy1`, `inalloy1`, `erdos_renyi` | **yes** |
| cs 300, drawing 1 | `real`, `inalloy1`, `alloy1`, `erdos_renyi` | `real`, `inalloy1`, `alloy1`, `erdos_renyi` | **yes** |
| cs 300, drawing 2 | `real`, `inalloy1`, **`erdos_renyi`**, `alloy1` | `real`, **`erdos_renyi`**, `alloy1`, `inalloy1` | no |
| cs 800, drawing 0 | `real`, `alloy1`, `inalloy1`, `erdos_renyi` | `real`, `inalloy1`, `erdos_renyi`, `alloy1` | no |
| cs 800, drawing 1 | `alloy1`, `real`, `inalloy1`, `erdos_renyi` | `inalloy1`, `alloy1`, `real`, `erdos_renyi` | no |
| cs 800, drawing 2 | `inalloy1`, `real`, `alloy1`, `erdos_renyi` | `inalloy1`, `real`, `alloy1`, `erdos_renyi` | **yes** |

**Three of six.** So *"the eigenvalue gap decides how much rank survives criticality"* is **withdrawn**: it holds for
drawing 0 at cs 300 — the drawing it was measured on — and for one of three drawings at cs 800, and it fails for the
other three outright (drawing 2 at cs 300 puts `erdos_renyi` below `alloy1` in λ̂₂ while the ranks put it above both).
What survives of `e238` is the part that was exact rather than statistical: the scalar rescale and the resulting
exact predictability of the *eigencollapse* (`eig(G) = 1/(1 − rho λ̂)`), the non-normality ratios, and the
instrument fact about `stable_weights`' radius estimate.

## 4. The pattern, now with three instances

This is the third time in this thread that a cross-family ordering measured on one drawing has dissolved under a
second: `e232` on the task side (cs-800 ratio 10.10× / 1.06× / 0.23×), `e236` on the support side (the union's
collapse, which was a *size* mismatch rather than a drawing), and now `e239` on the spectral side, twice over. The
statement that has survived every one of them is narrower and now well-supported:

> **within a family, the `rho` curve is a property of the substrate** (every family's rank, at every size and in every
> drawing measured, falls monotonically with `rho`, and `real`'s whole-`G` rank is bit-identical across drawings);
> **across families, a single-drawing comparison is a draw**. Any claim of the second kind in this line needs its
> drawings, and the corpus's own `real` cells are the control that shows when the movement is the null's.

## 5. What this cannot do

- **Three drawings** are a sample, so "three of six orderings agree" is itself a small-sample statement; what is
  established is that one drawing is not enough, not what the distribution of orderings is.
- **It repeats `e237`/`e238`'s conventions** (whole-matrix rank, `seed0`-driven task stream, the corpus's support
  size) rather than adding a new measurement, so a convention error in either would propagate here — the
  bit-identical `real` rows are the reason to think it did not.
- **Nothing on the task side or the penalty**: this is the weight matrix's spectrum and the propagator's own rank.
- **`rho` still rescales the whole matrix**, so the mechanism statements remain about the rescaled operator.
