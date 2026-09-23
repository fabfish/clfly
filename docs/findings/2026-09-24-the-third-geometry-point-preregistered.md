# `e131` pre-registered: the third geometry point, at read-out 1307 — so that the barrier's ordering can be read

**Date:** 2026-09-24
**Status:** pre-registered **before** the run. Committed as its own commit; the run is launched after it.
**Script:** `experiments/e124_barrier_distribution.py`, unchanged, using the `--matching-seeds` extension control
built in for `e130`.
**Planned artifact:** `runs/e131_barrier_r1307.json`, twelve seeds, 66 pairs, 21-point chords, at **read-out
1307 — the whole circuit state** — with `--iters 500 --test 48 --shared-head --input-overlap 0.0 --seed0 0
--circuit-size 800 --methods naive`.
**C0's comparator:** `runs/e116_r1307_40reps.json` (read-out 1307, 40 replicates, mean **+0.0357**, per-repeat sd
**0.0423**), of which these twelve seeds are the first twelve.
**Context:** `docs/findings/2026-09-24-the-connected-set-claim-is-read-out-dependent.md`, which found that
`e124`'s registered P1 **fails at read-out 32** and that the barrier's growth with the number of tasks is
**1.57×** at read-out 128 against **3.98×** at read-out 32. **Both that finding and `e124`'s §6 say the next step
is this point and say why it is now load-bearing rather than hypothetical**: with two read-outs, *"the barrier is
a property of the geometry"* and *"the barrier is a monotone function of the read-out"* are **two claims the data
cannot separate**, and the whole-state read-out is where they come apart.

## The two read-outs it will sit beside

| fit-task barrier / chance | read-out **32** | read-out **128** | read-out **1307** |
|---|---|---|---|
| per-repeat sd of the forgetting (`e116`) | 0.0556 | 0.0325 | **0.0423** |
| checkpoint 0 median / max | 0.0550 / 0.1342 | 0.0284 / 0.1221 | *this run* |
| checkpoint 2 median / max | **0.2187** / **0.4419** | 0.0445 / 0.1252 | *this run* |
| pairs above the 0.25 threshold | **21 of 66** | 0 of 66 | *this run* |

## The predictions

- **C0a, the extension control, and it is exact.** The twelve seeds' `mean_forgetting` must be **bit-identical**
  to `runs/e116_r1307_40reps.json`'s first twelve. This has now delivered twice — at read-out 128 by hand and at
  read-out 32 through the built-in check — so it is a control with two known answers rather than a hope.
- **C0b.** The three saved checkpoints pass `e122`'s endpoint control **6 of 6**.
- **P1.** **Every one of the 66 pairs** has a fit-task barrier below **25%** of chance. Reused verbatim from
  `e124`/`e130`, so this is a third replication of one threshold and not a new one.
- **P2, and it is what the fire is for.** The **median** fit-task barrier is **ordered 32 > 128 > 1307**. The
  reason is specific: read-out 1307 is the **whole state**, which is the configuration where the recurrent body is
  *least* load-bearing — the paper's own §4.2 says the whole state "contains no continual-learning problem" and
  the load-bearing gap is negative there (−0.0111) — so the seeds' solutions should be the **most** similar at
  that read-out and their connecting paths the flattest. **This is the prediction that separates the two
  readings**: if the ordering holds, the barrier is monotone in the read-out and *"a property of the geometry"* is
  doing no work that *"a function of the read-out"* does not already do; if the ordering does not hold, the
  barrier is not simply tracking the read-out and the geometry reading gains content.
- **Falsifier.** **The ordering inverts or ties at the top** — i.e. read-out 1307's median is **not below**
  read-out 128's 0.0361. Then the barrier is not driven by how much the body is needed, the two-read-out
  ambiguity is resolved in favour of neither explanation, and the whole-state read-out is a fourth thing rather
  than the low end of an axis.

## Why this is worth a run rather than an argument

The barrier at read-out 1307 is the one point of the three where **a low value is a positive prediction rather
than a null**. `e124` measured a low barrier at 128 and `e130` a high one at 32, and with those two alone a
sceptic can say the barrier merely traces the per-repeat spread — which is exactly what the read-out axis is
(`e118`, `e121`: the drift, the load-bearing gap and the fit depth are *all* monotone in it). The whole state is
the read-out where that confound is **weakest**: its per-repeat sd (0.0423) is *between* the other two
(0.0556 and 0.0325), so **an ordering of the medians that follows 32 > 128 > 1307 cannot be the per-repeat
spread's ordering, because the spread's ordering is 32 > 1307 > 128.** That is a separation this fire gets for
free from the `e116` sds, and it is the reason the prediction is stated as an ordering and not a magnitude.

## What this cannot settle, in advance

- **Three read-outs is still a curve on three points**, and the ordering test uses medians of 66 heavily
  dependent values (each seed appears in 11 pairs, so the effective `n` for anything about seeds is 12).
- **The separation from the spread is an argument from two orderings, not a measurement.** If the medians come
  out 32 > 1307 > 128 — the spread's ordering — the fire will not distinguish the two, and it will say so.
- **Read-out 1307 is not "read-out 0" in the sense the frozen-body control uses**, although both read the whole
  state: `--readout-size 0` and `--readout-size 1307` are the same read-out in this codebase but appear as
  different config values, so **an artifact's `readout_size` is not a reliable way to tell them apart** and this
  run's 1307 is chosen to match `e116_r1307_40reps.json` exactly.
- **The chords are still through checkpoints, not minimisers**, and 21 points can miss a ridge, so every barrier
  is a lower bound — the safe direction for P1 and the unsafe one for P2.
