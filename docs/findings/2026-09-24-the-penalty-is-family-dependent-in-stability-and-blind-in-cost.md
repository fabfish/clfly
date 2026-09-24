# The penalty's stability benefit scales with the family; its plasticity price does not

**Date:** 2026-09-24
**Artifacts:** `runs/e150_r32_overlap1_frozenbias_ewc_lam3e-4.json` (landed) — `--input-overlap 1.0
--frozen-bias --methods ewc --lam 3e-4`, forty replicates — against `runs/e143_r32_overlap1_frozenbias.json`
(that family's freeze alone), `runs/e144_r32_overlap1_methods_40reps.json` (its `naive`),
`runs/e147_r32_frozenbias_ewc_lam3e-4.json` and `runs/e125_r32_frozenbias.json` (the base family's counterparts).
**The λ = 3e-3 arm of the same design is still running**, so the registration's λ-invariance clause is pending;
**P1 and its falsifier are both decided by this arm.**
**The registration** is `docs/findings/2026-09-24-the-pair-under-the-freeze-registered.md`: the base family's
pair removes **88.5%** of its freeze's residual (0.0201 of 0.0227), and three readings made different
predictions for the harder family — **the pair is the unit → +0.0069** (P1 ≤ **+0.0149**); the family scales it →
+0.0314; the penalty is saturated → +0.0398 (**falsifier ≥ +0.0318**).

---

## 1. The registered reading: neither P1 nor the falsifier, and the middle is what happened

| arm (shared-input family) | forgetting | mean accuracy | newest-task accuracy |
|---|---|---|---|
| `naive` (`e144`) | +0.1068 | 0.8939 | 0.9724 |
| freeze alone (`e143`) | +0.0599 | 0.9104 | 0.9479 |
| **freeze + ewc λ = 3e-4 (`e150`)** | **+0.0190** | 0.9193 | **0.9141** |

| contrast | change | resolution |
|---|---|---|
| **the arm − the freeze alone** | **−0.0409 ± 0.0059** | **6.87σ** |
| the arm − `naive` | −0.0878 ± 0.0090 | 9.72σ |
| the arm − the freeze, newest task | −0.0339 ± 0.0055 | **6.14σ** |

**+0.0190 lies between the P1 bar (+0.0149) and the falsifier bar (+0.0318)** — so the registered *middle* is the
outcome, and the registration said in advance that it is **informative rather than a failure**. The two numbers
that make it informative:

- **the penalty removes 0.0409 of the freeze's 0.0599 = 68.3% of the residual**, against **0.0201 of 0.0227 =
  88.5%** on the base family; and
- **the absolute effect is 2.04× larger there: −0.0409 against −0.0201, a difference of −0.0208 ± 0.0070 =
  2.99σ** — resolved.

**So "the pair is a unit" (P1) is dead in its strict form and the family-scaled reading is right in *direction*
but not in *size***: the effect grows with the residual, by a factor this arm measures at **0.68 against 0.89**.
A fixed *fraction* would have put it at 0.0069; a fixed *amount* would have put it at 0.0398; it landed at 0.0190.
The honest form is the one the registration wrote for the middle: **partial scaling**.

## 2. And the second half is sharper than the registration asked for

The registration asked whether the *stability* effect scales. It did not ask what the **price** does, and the
answer is that the price does not move at all:

| quantity | base family | shared-input family | difference |
|---|---|---|---|
| conditional effect on forgetting (the benefit) | −0.0201 ± 0.0036 | **−0.0409 ± 0.0059** | −0.0208 = **2.99σ** |
| newest-task cost of the same pair | −0.0328 ± 0.0051 | **−0.0339 ± 0.0055** | −0.0010 ± 0.0079 = **0.13σ** |
| the freeze's own newest-task cost | −0.0266 ± 0.0060 | −0.0245 ± 0.0060 | +0.0021 ± 0.0085 = 0.25σ |

**The penalty's plasticity price is the same on both families to 0.13σ** — computed per seed as the difference of
the two differences, not in quadrature — while its stability benefit doubles at 2.99σ. Put beside the previous fire's result (**the channel × λ interaction is 1.23σ on the newest task and 4.10σ
on forgetting**), the picture is now a clean separation:

> **The penalty buys stability at a rate that depends on the channel and on the family (4.10σ and 2.99σ
> interactions), and it pays for it at a price that depends on neither (1.23σ and 0.13σ).**

That is the sharpest form of this session's two-axis claim: the *cost* is a property of the mechanism, and the
*benefit* is a property of the substrate it is applied to. And it is why the "efficiency" index in `e152` moves so
much across families: it is a ratio whose denominator is constant and whose numerator is not.

## 3. The manipulation checks and the census entry

- **The freeze's instrument check passes in the form it forces**: the whole-body term's bias component is
  **exactly 0.0** in all forty replicates, as are all three `bias_from_zero` entries. The arm's accuracy is
  **0.9193 ± 0.0034**, above its own family's freeze (0.9104) and above its `naive` (0.8939).
- **Against its own family's baseline the arm is a 9.72σ win with a resolved cost**: `naive` −0.0878 (9.72σ) on
  forgetting, and **−0.0583 at 7.66σ** on the newest task — a third entry in `e151`'s census of constrained arms
  that pay there, which the census cannot yet contain (its registry predates this arm).

## 4. What this cannot settle

- **One λ** (the second arm is running), one read-out (32), one circuit, three tasks, one seed stream, and a
  **`--frozen-bias` diagnostic rather than a method** — the ranking under it is not advice, and what is measured
  is a property of the penalty and of the benchmark.
- **Two families that are siblings**: both are `cs = 800`, read-out 32, three tasks, differing only in
  `--input-overlap` (0.0 against 1.0). "Family" here means *the task family used in this paper*, and the factor by
  which the benefit scales could be the baseline's forgetting rather than the family as such — this design cannot
  separate those, which is the same gap the `e148` finding names for `replay`'s margin.
- **The registered prediction was a point prediction with a 2σ window**, and the arm landed 0.004 from the P1 bar;
  the outcome is "neither registered yes nor registered no", the third time this session a registration has ended
  in its own middle rather than at a bar (`e141`'s P2, `e142`'s P1, `e148`'s P2). The pattern is now itself a
  finding about the *bar-setting*, and rule 37 is the rule it produced.
- And **the price's constancy rests on two families and one λ at each** — 0.15σ is a statement about this
  interval, not a law about penalties.
