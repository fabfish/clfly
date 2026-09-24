# `e150`, pre-registered: is the pair freeze-plus-penalty a *unit*, or is the family?

**Date:** 2026-09-24
**Design:** `--input-overlap 1.0 --readout-size 32 --shared-head --frozen-bias --methods ewc
--lam {3e-4, 3e-3} --repeats 40 --fisher-batches 32 --seed0 0`, forty replicates each, writing
`runs/e150_r32_overlap1_frozenbias_ewc_lam{3e-4,3e-3}.json`.
**Status: registered and NOT yet launched** — the queue holds four runs and the discipline all session has been
to add the fifth only when a slot frees.

---

## 1. The number this is built on, and it is arithmetic rather than hope

`e147` measured the base family with the unpenalised channel held still: the freeze alone leaves **+0.0227** and
the freeze plus a weak diagonal penalty (**λ = 3e-4**) leaves **+0.0026**. The conditional effect of the penalty
is **−0.0201 ± 0.0036 = 5.53σ**, i.e. it removes **88.5%** of what the freeze leaves, and the *residual
fraction* — the freezing-plus-penalty forgetting as a share of the freezing-alone forgetting — is **11.5%**.

The harder family (`--input-overlap 1.0`) is the one where that fraction was never measured, and the two facts
that make it the right place to measure it are both already on disk:

- **the freeze covers much less there**: `e143` leaves **+0.0599** against a `naive` arm of **+0.1068**
  (`e144`), so the freeze removes **43.9%** of the baseline's forgetting against **69.7%** on the base family;
- **the penalty alone is much stronger there**: `ewc` at λ = 3e-3 gives `ewc − naive` = **4.73σ** on this family
  against **1.21σ** on the base family at the same forty replicates (`e144` against `e140`).

So the two candidate readings make numerically different predictions, which is what a registration needs:

| reading | what it says | predicted arm |
|---|---|---|
| **the pair is the unit** | the residual fraction is a property of *freeze plus penalty*, not of the family | **+0.0069** (the same 11.5%) |
| the family scales it | the penalty's conditional effect scales with the family's forgetting (×1.42) | +0.0314 (52%) |
| the penalty is saturated | the conditional effect is the same −0.0201 in both families | +0.0398 (66%) |

**The resolution is arithmetic too.** The relevant contrast is paired against `e143`'s forty seeds at the same
settings on the same seed stream — the two configurations differ only in `frozen_bias` being true and the method
being `ewc` rather than `naive`, which is exactly the pair `e147` measured on the base family, whose paired sem
was **0.0036**. Against a residual of 0.0599 that is **6.0%** of the residual per σ, so a 2σ window is ±12
points of the fraction.

## 2. The predictions, and the falsifier, written before the runs

- **P1 — the pair is the unit.** The λ = 3e-4 arm lands at or below **+0.0149**, i.e. within 2σ of the 11.5%
  residual fraction (prediction +0.0069).
- **Falsifier — the family is the unit.** The arm lands at or above **+0.0318**, i.e. the penalty removes no
  more than the base family's −0.0201 in absolute terms. Then the conditional effect does **not** scale with the
  residual, the pair-property reading is dead, and the reason the diagonal is worth 4.73σ on this family
  unanchored has to be found somewhere other than the size of the channel the freeze leaves behind.
- **And the middle is registered as informative rather than as a failure**: between the two, the penalty's reach
  grows *partly* with the residual — which is not a null and would be the reading the arithmetic above cannot
  distinguish from either extreme at 2σ.

**The second arm asks whether the pair is a *λ*-invariant unit.** The base family's λ = 3e-3 arm lands this
session (`e147`'s other half), so the wiring family at both λ makes the design a 2×2 of family × λ under the
freeze, and the question *"is the residual fraction the same at both λ"* is answerable in it. With the base
family's two λ the same comparison is one arm short.

## 3. The controls this will be read against, and they exist already

- **C0, the pairing**: `e143`'s config agrees with the planned one on **every seed-stream field** (`seed0` 0,
  `repeats` 40, `circuit_size` 800, `iters` 500, `lr` 3e-3, `batch` 32, `train` 96, `test` 48, `noise` 1.0,
  `classes` 4, `support` 80, `shared_head` true, `input_overlap` 1.0, `readout_size` 32) and differs only in
  `frozen_bias` and `methods`.
- **C1, the instrument check the freeze forces**: the whole-body first-order term's bias component must be
  **exactly 0.0** in both new arms, as it is in `e147`'s, since a frozen offset cannot move. `e149` now asserts
  this rather than checking it by eye.
- **`e149`'s caution applies and is named here**: the interaction between the two interventions is **additive at
  1.61σ** on the base family, so this design's *marginal* effects are the only quantities it may read — nothing
  here licenses a claim about their shared part.

## 4. What this cannot settle even if it lands as predicted

- One read-out (32, where the offsets' share is largest by construction), one circuit, three tasks, and one
  freeze variant (the offsets, not the body).
- **`--frozen-bias` is a diagnostic and not a method** (`e147`'s own caveat): a residual fraction measured under
  it is a statement about the penalty and about the benchmark, not advice.
- The base family's 88.5% is **one λ and one arm**; the pair-property hypothesis it motivates is being tested on
  a second family, not established.
