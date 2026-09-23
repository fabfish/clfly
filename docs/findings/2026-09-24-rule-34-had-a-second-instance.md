# `e129`: rule 34's second instance, found an hour after the rule — `ρ ≈ 0.14` should be `0.364`

**Date:** 2026-09-24
**Script:** none. This is arithmetic checked against two stored artifacts, which is the point of rule 34.
**Artifacts:** `runs/e119_r128_test480.json` (500 iterations), `runs/e120_r128_test480_2000iters.json`
(2000 iterations), `runs/e116_r128_40reps.json` (test 48, the third reading).
**Corrected:** `docs/paper/clfly-v1.md` §4.2; `docs/findings/2026-09-24-four-times-the-training-does-not-help.md`
§1; and `docs/findings/2026-09-24-four-times-the-training-preregistered.md` §2 and its P2 row, **as a dated
amendment rather than an edit**, since a pre-registration is a contract and its text may not silently move.
**Context:** rule 34, written in the previous fire from `e128` — *"a sentence can stitch two runs as easily as a
table can, and the tell is arithmetic: recompute the stated prediction from the stated input."* This is that
check applied to the next sentence of the same shape in the corpus.

---

## 1. The claim, and the formula it names

The `e120` pre-registration derives a diagnostic from the fact that the forgetting is a **difference of two
accuracies**:

> each of which varies across seeds with sd ≈ 0.018 at test 480. If they varied independently the difference
> would have sd √2·0.018 = 0.026; the measured 0.0221 implies a seed-to-seed correlation of **ρ ≈ 0.14**.

The formula is stated in the same paragraph, `sd_forgetting = sd_accuracy · √(2(1−ρ))`, so `ρ` is a **one-line
recomputation from two numbers the project already had**. On the paragraph's own rounded input,
`ρ = 1 − (0.0221/0.018)²/2 = 0.246`. On the artifacts' exact values:

| | sd_accuracy | sd_forgetting | ratio | **ρ** |
|---|---|---|---|---|
| `e119`, 500 iterations | 0.01963 | 0.02215 | 1.128 | **+0.364** |
| `e120`, 2000 iterations | 0.02225 | 0.03047 | 1.370 | **+0.062** |
| `e116`, test **48**, 500 iterations | 0.02283 | 0.03251 | 1.424 | **−0.014** |

**So `0.14` was out by 1.8× against the paragraph's own inputs and 2.6× against the measurement**, and the
`≈ 0.018` it used was itself a slight understatement of **0.01963** — which is where part of the drift entered,
since the ratio's square is what the formula uses. **The 2000-iteration value is right** (0.062 against the
reported 0.06), so this is one wrong number in a pair rather than a wrong method.

## 2. What the correction changes — and it is the mechanism's size, not its direction

The project's reading was *"longer training makes the two accuracies less correlated across seeds, which is the
same statement as the spread rising: more training gives each seed more room to become itself."* **That survives,
and it gets stronger**: the drop is **0.364 → 0.062**, a factor of **six**, against the factor of 2.5 the wrong
number implied. So four times the compute makes the seeds *more* individual than the record said — which is the
same direction as everything else this line has found about the training trajectory, and the largest such figure
it has.

**And the third reading is the one that explains the other two.** At **test 48** the same propagation gives
**ρ = −0.014**: the two accuracies are **uncorrelated across seeds when the test set is coarse**, and become
correlated at 0.36 when it is ten times larger. **That is not a contradiction but the expected ordering** — at
144 held-out decisions each accuracy is dominated by sampling noise that is independent between the two
evaluations, and at 1,440 the sampling noise is small enough that what remains is the **shared model
difference**, which is exactly what a positive correlation between two accuracies of the same network measures.
So the correction does not just fix a number: it turns an isolated figure into a **test-set-dependent series**
whose direction is what the mechanism predicts, and it was invisible while one of the three values was wrong.

## 3. Why nothing caught it, and what the rule buys

- **`e97`** checks that a cited artifact exists. All three exist.
- **`e105`** checks a table's arithmetic closure. This is a **sentence**, and the paragraph contains no table.
- **`e126`** checks counts. `0.14` is not a count.
- **`e127`** checks the programme table. This is a finding.

**Every audit this project runs is blind to it, and all four were green**, which is why rule 34 was written one
fire earlier and why this instance is worth recording separately: **the rule was created from an instance in the
paper and found a second instance in a finding within the same session.** The check is the cheapest one in this
project's rule list — a formula stated in prose, two numbers stated beside it, one line of arithmetic, no
artifact loading required beyond reading two `evaluation_noise` fields.

**What it cannot catch**, stated because a rule that looks total is dangerous: it applies only where the text
**names its own formula**. The `2.6×` of `e128` named none (it was a prediction whose input was in the previous
clause) and was caught by recomputing anyway; a claim whose model is implicit in a way the reader cannot
reconstruct is invisible to this check, and there the only defence is that a number quoted beside its input is
worth more than a number quoted alone.

## 4. What this does not settle

- **ρ is a diagnostic, not a measurement of a mechanism.** It is inferred from two sd's through an assumption
  (that the two accuracies' errors are exchangeable, and that the forgetting's per-task differences behave like
  one difference), and the number moves with the test set as §2 shows. It says the seeds' final accuracies share
  variance; it does not say what shares it.
- **Three points, three configurations** — 500/2000 iterations at one test set and 500 at another. The ordering
  is consistent with the mechanism and the mechanism is not independently measured.
- **The corrected value is not audited by anything either.** If `0.364` is wrong, the same sentence will carry
  the wrong number with a dated note beside it, which is the improvement this project can make and not a
  guarantee.
