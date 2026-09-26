# What C2b's cross-rung null rules out: 219.5, 4.0 and 5.8 replicates

*2026-09-26 22:05. Runs: **none new** — `experiments/e259_c2b_null_power.py` reads `e76`'s own artifact
(`runs/e76_c2b_cross_rung_powered.json`) and turns its detection floors into the statement a null needs
(`runs/e259_c2b_null_power.json`). Seconds.*

## 1. The item, and the one thing `e76` left unsaid

`e76` closed C2b's last outstanding figure: the paired `side − cell_class` contrast at λ = 0.1, sixteen replicates on
both rungs, is **−0.01910 ± 0.02161 = 0.88σ** on accuracy and **+0.03516 ± 0.02907 = 1.21σ** on forgetting, where the
published three-replicate figure had been **+0.0718 at 2.13σ**. It also tabulated each figure's detection floor. What
it did not state is what a null needs in order to be worth anything:

    **was sixteen replicates enough to have seen the effect it replaced?**

That is computable from `e76`'s artifact alone, because the sem the run achieved and the effect the line published
together fix the replicates the published effect would need:

    sigma(n) = |effect| / (sem_16 · sqrt(16 / n))        n(2 sigma) = 64 · sem_16^2 / effect^2

## 2. The table, and the verdicts (P1-P3 all MET)

| figure | published (3 reps) | sem at 16 | implied σ at 16 | replicates needed for 2σ | floor at 16 |
|---|---|---|---|---|---|
| `side` | +0.0069 (0.48σ) | 0.01278 | **0.54σ** | **219.5** | 0.02555 |
| `cell_class` | −0.0648 (2.65σ) | 0.01615 | **4.01σ** | **4.0** | 0.03230 |
| `side − cell_class` | +0.0718 (2.13σ) | 0.02161 | **3.32σ** | **5.8** | 0.04321 |

**P1 MET — the null is powered for the claim it replaced.** The published cross-rung effect would have shown at
**3.32σ** with sixteen replicates. The sixteen-replicate run could have seen it and did not.

**P2 MET — and "underpowered" is not a uniform statement about this line.** The replicates the three published claims
would each need differ by a factor of **55** (219.5 against 4.0 and 5.8). One of the line's three figures belongs to a
rung that needs two hundred replicates and two belong to rungs that need fewer than six.

**P3 MET — which is the same statement twice.** The published `side` claim was **never detectable at sixteen
replicates** (0.54σ) while the published `cell_class` and cross-rung claims are **excluded at better than 3σ**. So the
answers to "was it underpowered?" and "does the null bite?" are one sentence: **the run was underpowered for `side` and
well powered for the other two.**

## 3. Two corollaries the floor table makes visible

**The `side` figure sits below its own detection floor at every replicate count this line has ever run.** Sixteen
replicates floor it at 0.02555 and forty at 0.01616 under the 1/√n scaling, against a published effect of **0.0069** —
so even the line's largest budget leaves that figure 2.3× under its own floor. A published 0.48σ was never falsifiable
here, which is a statement about what could be claimed rather than about what was measured.

**And the floors at n = 3 explain the original confusion.** At three replicates the three floors are 0.059, 0.075 and
0.100, against published effects of 0.0069, 0.0648 and 0.0718 — so **two of the line's three figures were published
below their own detection floor**, and the third was just above it. The three-replicate asymmetry that C2b was built on
("a 2.65σ disadvantage at the fine rung against a 0.48σ null at the coarse one") is a statement at a budget where
neither end could have been resolved.

## 4. What it cannot do

The `sem ~ 1/sqrt(n)` scaling is **assumed**, so every floor at n ≠ 16 is an extrapolation from one n and the
`n = 3` column is an extrapolation *downward* from a budget the run never had. The published effects are themselves
**three-replicate draws**, so the "replicates needed" figures inherit their noise — an effect that is really zero
needs infinitely many — and a line whose three-replicate figures are the ones under audit cannot use them to set its
own power without saying so, which this does. The comparison is on **accuracy** because that is the metric the
published cross-rung figure is stated on; forgetting's published counterpart does not exist in the same form. And no
run is made: this turns `e76`'s floors into the sentence a null needs, and measures nothing new.
