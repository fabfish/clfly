# `e110`: the surviving hypothesis is refuted, and the anomaly is the whole state rather than the middle

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, three runs; artifacts `runs/e110_readout512_plastic.json`,
`runs/e110_readout512_plateau.json`, `runs/e110_readout512_frozen.json`.
**Artifacts:** the three above, plus the `e109`/`e104` artifacts at read-out 0 / 128 / 32.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 512**, plus a frozen control and a second
execution.
**Pre-registration:** `docs/findings/2026-09-23-a-fourth-read-out-preregistered.md`, committed before the runs.
**Context:** `docs/findings/2026-09-23-the-second-order-term-changes-sign-at-128.md`, whose one surviving claim
was that read-out 128 is the only one of three where the curvature is negative for both tasks **and** the one
that forgets least.

---

## 1. The four points

| read-out | **forgetting** | body drift | load-bearing gap | curvature negative for both tasks? |
|---|---|---|---|---|
| **1307** (whole) | +0.0479 | 0.0195 | −0.0111 | no |
| **512** | **+0.0208** | 0.0258 | +0.0014 | **no** |
| **128** | +0.0333 | 0.0391 | +0.0167 | **yes** |
| **32** | +0.0729 | 0.0493 | +0.1000 | no |

**P1 fails and P2 holds, which makes the falsifier fire and refutes the hypothesis.** At 512 the curvature is
**positive for task 0 and negative for task 1** — not both negative, so the negative region is not an interval
containing 128 — while the forgetting is **+0.0208, the smallest of the four**. That is falsifier (a) exactly as
the pre-registration wrote it: *positive for at least one task* **and** *the smallest forgetting of the four*, so
**the sign of the curvature does not track the level of the forgetting**, and the one qualitative pattern found
at the anomalous read-out is dead.

**And the fourth point changes what the anomaly is.** Along the read-out axis the forgetting is
**+0.0479 → +0.0208 → +0.0333 → +0.0729**, which is not monotone — but **the three narrow read-outs are**:
512, 128 and 32 give **+0.0208 < +0.0333 < +0.0729** monotonically. **So the non-monotonicity is not a
mid-range dip: it is a single point's excess at the whole state**, which forgets more than 512 and 128 despite
being the widest read-out and the one where the body is *least* needed (its gap is the only negative one,
−0.0111, i.e. training actively hurts there).

**That reframes four fires of searching.** The question being asked was *what makes the middle of the axis
anomalous*, and the middle is not anomalous — the **widest** configuration is, and it is the configuration the
paper itself says "contains no continual-learning problem". Forgetting measured there is measuring something
else, which is now a specific and testable statement rather than a search.

## 2. What holds across all four points

- **The body's drift is monotone**: 0.0195 → 0.0258 → 0.0391 → 0.0493 ✓
- **The load-bearing gap is monotone**: −0.0111 → +0.0014 → +0.0167 → +0.1000 ✓
- **The forgetting is not**, and the deviation is at the widest read-out only.

So the pattern five fires of instrumentation have produced is not "some candidate orders the forgetting" but
**every mechanical quantity this project can measure is monotone in the read-out, and the forgetting is
monotone over the three narrow read-outs and excess only at the whole state.** The candidate that would explain
the excess has to explain a property of *that configuration* — where the head can absorb the body's motion, the
body is not needed, and the forgetting is nevertheless higher than at 512 — rather than a property of the axis.

## 3. The repeat, and the reproducibility datum it extends

**The second execution at 512 is bit-identical to the first** — the mean forgetting, and every stored
curvature — so the `sd = 0.0000` result of `e106` now holds at a **fourth** read-out, with the same recorded
environment (`torch_num_threads: 20`, `OMP_NUM_THREADS` unset). A `naive`-only run at a fixed read-out remains
among the most reproducible measurements in this repository, and the reason is unchanged: no Fisher, no replay,
no anchor, one deterministic trajectory per seed.

## 4. What this cannot settle

- **Four read-outs on one axis is still a curve fitted to four points**, and the claim "monotone over the narrow
  three, excess at the whole state" is exactly as strong as three-plus-one points can be. A fifth read-out
  between 512 and 1307 would put a point inside the interval the reframed question is about.
- **The curvature instrument is unchanged and its negatives were validated only against `torch`'s own `hvp`**,
  which is an independent implementation of the same derivative rather than an independent measurement.
- **It does not say what the excess at the whole state is.** It says where it is, which is what a fourth point
  can do, and it is the first time in this sequence that a prediction was tested on a point whose value was not
  already in hand.
