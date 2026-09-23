# `e111`: the read-out axis has an interior minimum at 512, and there was never an outlier

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, three runs; artifacts `runs/e111_readout900_plastic.json`,
`runs/e111_readout900_plateau.json`, `runs/e111_readout900_frozen.json`.
**Artifacts:** the three above, plus the `e109`/`e110`/`e104` artifacts at read-out 1307 / 512 / 128 / 32.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 900**, plus a frozen control and a second execution.
**Pre-registration:** `docs/findings/2026-09-23-a-fifth-read-out-preregistered.md`, committed before the runs.
**Context:** `docs/findings/2026-09-23-the-anomaly-is-the-whole-state-not-the-middle.md`, which had four points
and read the shape as *"forgetting is monotone over the three narrow read-outs and the whole state is the one
point above them"*.

---

## 1. Both predictions hold, and the control is exact

**P1 held**: forgetting at read-out 900 is **+0.0292**, strictly between 512's **+0.0208** and 1307's **+0.0479**.
**P2 held**: the load-bearing gap at 900 is **−0.0014**, strictly between 1307's **−0.0111** and 512's
**+0.0014** — the gap series continues rather than breaking, which is what licenses reading P1 as a result about
the axis rather than about a stray environment. The frozen control at 900 gives **exactly `+0.0000`** for all
three tasks, and the **second execution is bit-identical** in forgetting and accuracy, in the same recorded
environment (`torch_num_threads: 20`, `OMP_NUM_THREADS` unset).

## 2. Five points, and both arms are monotone

| read-out | **forgetting** | load-bearing gap | body drift |
|---|---|---|---|
| **1307** (whole) | +0.0479 | −0.0111 | 0.0195 |
| **900** | +0.0292 | −0.0014 | 0.0213 |
| **512** | **+0.0208** | +0.0014 | 0.0258 |
| **128** | +0.0333 | +0.0167 | 0.0391 |
| **32** | +0.0729 | +0.1000 | 0.0493 |

**Read as two arms, each is monotone:**
**0.0479 > 0.0292 > 0.0208 < 0.0333 < 0.0729.** The wide arm (1307 → 900 → 512) declines, the narrow arm
(512 → 128 → 32) rises, and the minimum is at **512**.

**So there is no anomaly, and the previous fire's reading of the same numbers was an artifact of where its points
were.** With one point on the wide arm the shape looked like *an outlier above a plateau*; with two, the wide arm
is a clean monotone decline and the correct description is **a two-sided interior minimum**. The numbers in the
previous finding stand — 0.0479 really is above 0.0208 and 0.0333 — and its *name* for that fact does not, which
is the third time in this sequence that a shape claim has been revised by adding a point and the first time that
the revision retired a framing rather than a hypothesis.

## 3. The per-task structure, and one residual

| read-out | task 0 | task 1 | mean |
|---|---|---|---|
| **1307** | +0.0833 | +0.0125 | +0.0479 |
| **900** | +0.0375 | +0.0208 | +0.0292 |
| **512** | **+0.0333** | +0.0083 | **+0.0208** |
| **128** | +0.0583 | +0.0083 | +0.0333 |
| **32** | +0.0833 | +0.0625 | +0.0729 |

**Task 0 is a clean two-sided minimum with both arms monotone** — 0.0833 > 0.0375 > **0.0333** < 0.0583 < 0.0833
— which is the paper's `mean_forgetting` shape appearing in a single task.

**Task 1 is not, and the residual should be named rather than averaged away**: its wide arm is **0.0125 → 0.0208**
up then 0.0083 down, so it is non-monotone, with the deviation between **two small values** (1307's 0.0125 and
900's 0.0208, a difference of 0.0083). Its only large value is at read-out 32 (+0.0625). So the mean's clean V is
**carried by task 0**, and the honest statement is *"the reported metric and task 0 have a monotone two-sided
minimum at 512; task 1 is flat and slightly non-monotone across the wide half, where every value is below
0.021"*.

## 4. What this says about the benchmark, and it is the first design statement here

**Forgetting on this benchmark is minimized at an intermediate read-out width, not at either extreme.** The
paper's design principle — *"a connectome-constrained CL benchmark must use a narrow read-out, or it measures its
decoder"* — is a statement about the body being **load-bearing**, and the gap series says that monotonically
(−0.0111 → −0.0014 → +0.0014 → +0.0167 → +0.1000): narrowing the read-out always makes the body matter more.
**But the forgetting is not monotone in the same direction**, and its minimum sits at 512 of 1307, i.e. **between
the two extremes the principle brackets**. So the two quantities a practitioner would use to pick a read-out —
"is the body load-bearing" and "how much is forgotten" — are monotone in *different* respects, and the second has
an interior optimum.

**That is consistent with every mechanical measurement this project has made**, and it is the first statement in
this sequence that is about the benchmark rather than about a candidate mechanism: **every mechanical quantity is
monotone in the read-out (the drift, the gap, the first-order interference term, and the second-order quadratic
form), and the forgetting has a two-sided minimum** — so no monotone quantity can order it, which is *why* four
candidate mechanisms failed in this sequence rather than by coincidence.

## 5. What this cannot settle

- **Five points, and the minimum's location is known only to within the interval (128, 900).** A point at 300 or
  at 700 would narrow it, and the *depth* of the minimum is 0.0125 below its neighbours — the same size as task
  1's wide-arm residual.
- **Tasks 0 and 1 disagree** on whether both arms are monotone, and with two forgetting values per configuration
  the mean is a two-point average; the paper's metric excludes the last task by construction, so this is a
  two-sample statement at each read-out.
- **The curvature instrument is not re-run here**, which is deliberate: it was refuted at the fourth point, and
  adding its value at 900 would be a fifth series to aggregate rather than a test.
