# `e110`, pre-registered: a fourth read-out, testing the one surviving hypothesis

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, three runs; artifacts `runs/e110_readout512_plastic.json`,
`runs/e110_readout512_frozen.json`, `runs/e110_readout512_plateau.json` (in flight at registration).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 512** — between the 128 already measured and the
1307 whole state.
**Context:** `docs/findings/2026-09-23-the-second-order-term-changes-sign-at-128.md`, whose one surviving claim
is qualitative and has never been tested on a read-out whose forgetting was not already known.

---

## 1. What is being tested, and why this is the first clean test in the sequence

Four attempts to order this benchmark's forgetting have been measured and three failed:

| quantity | monotone in the read-out? | orders the forgetting? |
|---|---|---|
| the body's displacement | **yes** | no (`e107`) |
| the load-bearing (plastic − frozen) gap | **yes** | no (`e107`) |
| the first-order interference `<grad_j, Δθ>` | **yes** | no, both predictions failed (`e108`) |
| the second-order term `ΔθᵀH_jΔθ` | **no** — negative at 128 | **aggregation-dependent** (`e109`) |

The second-order term's *ordering* is unresolved because one pooling matched and another failed. But the fire
that measured it also produced the only **qualitative** pattern anyone has found at the anomalous read-out:

> **read-out 128 is the only one of the three where the curvature is negative for both tasks, and it is the one
> that forgets least** (+0.0333 against +0.0479 and +0.0729).

**And a three-point series cannot test that, because every point's forgetting was already known when the pattern
was noticed.** Read-out **512** is between 128 and the whole state, its forgetting has never been measured, and
its curvature is measured by the same instrument. That makes this the first prediction in the sequence that is
**not** a post-hoc reading of numbers already in hand — which is exactly what the project's rules ask for and
what the last four fires have not been able to do.

## 2. The predictions, written before the runs finish

| | prediction |
|---|---|
| **P1** | at read-out 512 the curvature is **negative for both tasks** — the negative region is an interval containing 128 rather than a single point |
| **P2** | its forgetting is **≤ 0.0479**, the whole-state value, so the four points fall into a low group {128, 512} and a high group {0, 32} |
| **Falsifier (a)** | 512's curvature is **positive for at least one task** *and* its forgetting is the **smallest of the four** — sign would then not track level at all |
| **Falsifier (b)** | 512's curvature is **negative for both tasks** *and* its forgetting is the **largest of the four** — the pattern would be refuted directly |

**P1 is the hypothesis's own extension and P2 is what would make it useful, and they can come apart**, which is
why both are stated: a negative curvature that predicts nothing about the level is a curiosity, and a low
forgetting with a positive curvature is the falsifier.

**A second run at read-out 512 is included** (`_plateau`) for the same reason `e106` ran four executions at each
read-out: a single execution cannot distinguish a value from an accident, and at this configuration the `naive`
arm's run-to-run sd was measured as **exactly zero** over four executions, so a repeat either reproduces bit for
bit — in which case the value is solid — or it does not, in which case that is the finding.

**And the frozen control is re-run at 512**, because the plastic-minus-frozen gap is one of the three failed
candidates and there is no reason to stop measuring it just because it failed: a fourth point either continues
its monotonicity or breaks it, and both are informative.

## 3. What this cannot settle

- **One new read-out is one new point.** If P1 and P2 both hold, the honest statement is a four-point
  correlation on an interval, not a mechanism; the mechanism would need the curvature measured *along the path*
  rather than at the endpoint, which is a different instrument.
- **Read-out 512 is one choice among many.** It was chosen because it lies between 128 and 1307, and a different
  fourth point could have given a different answer; the choice was made before the run, which is the only
  protection available and is not the same as the choice being forced.
- **The curvature is a property of the direction the body moved**, which depends on the training trajectory, so
  a 512 run in a different environment would have a different direction. The environment is recorded now
  (rule 21) and will be reported beside the result.
