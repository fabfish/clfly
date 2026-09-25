# Registered: does the swap walk converge to the Erdős–Rényi alignment, or to a different ensemble?

**Date:** 2026-09-26. **Registered before its runs.** Artifact to be written:
`runs/e211_convergence_probe.json`.

---

## 1. The two ranges are disjoint, and there are two ways to read that

The alignment screen (`e209`) measures `all_pairs_alignment` at swap strengths 8, 16, 32 and 64, five realizations
each. The Erdős–Rényi family at the same circuit size (nine cells across `e2_analytic`, `e33`'s six `rewire_seed`s
and `e48`) sits at **0.27135 – 0.29039**, i.e. **4.89 – 5.23× chance**. The screen's cells sit at **0.03596 –
0.09120**, i.e. **0.65 – 1.64× chance** — *below* chance at six of the sixteen cells measured, and never above it by
more than 64%. **The two ranges are disjoint by a factor of 3.0 in alignment**, and the screen's own premise was that
alignment grows with swap strength.

Two hypotheses explain that, and they are separable with two cheap cells:

- **H1 — a slow axis.** The degree-preserving swap walk converges to the Erdős–Rényi level, but slowly; strength 64
  is simply not enough, and the hole in the record is a gap in the strength axis. Then four to sixteen times the
  strength would move alignment upward again.
- **H2 — two ensembles.** The **degree-preserving** random ensemble (what the swap walk approaches) and the
  **edge-count-matched** Erdős–Rényi ensemble (what `apply_null("erdos_renyi")` draws) are different distributions,
  and the walk converges to something like 0.04 rather than 0.29. Then the alignment jump is a difference between
  *kinds of null*, not a point on a rewiring continuum — and **C3's transition may not be reachable by rewiring at
  all**, which is a sharper and more interesting statement than "unmeasured".

## 2. The design

Two cells, in the runner's `--geometry-only` mode (112 s per cell measured at cs 800, 3 seeds):

```
experiments/e2_topology_gap.py --circuit-size 800 --support 80 --seeds 3 --seed0 0 --q 0.02 \
  --topologies swap256,swap1024 --rewire-seed 0 --geometry-only \
  --json-out runs/e211_convergence_probe.json
```

`swap256` and `swap1024` are 4× and 16× the screen's highest strength. `--rewire-seed 0` is the screen's rs0
realization, so **the contrast against rs0's own cells changes exactly one thing**: the strength (0.09120 max at
64 → whatever 256 and 1024 give). Cost ≈ **5 min**, one command on an idle machine.

## 3. The claims

**V1 — the walk is still climbing (H1).** At least one of the two cells has alignment **above 0.09120**, the screen's
maximum. **Falsifier**: both are at or below 0.09120 and inside the screen's own range (0.03596 – 0.09120), which
says four to sixteen times the strength buys nothing and the walk has converged — the natural reading of H2.
**Null worth keeping**: exactly one of the two climbs and the other does not, which is unresolved ordering at two
cells and needs realizations rather than strengths.

**V2 — the walk's level is below the Erdős–Rényi family (H2).** Both cells are **below 0.20**, i.e. at least 1.36×
below the lowest ER cell (0.27135). **Falsifier**: any cell **above 0.25**, which would put the walk in the ER range
and kill H2 outright. **Null**: 0.20 – 0.25, which would leave the walk climbing into a level between the two
families and would need the transition mapped rather than this question answered.

**Reported rather than claimed**: the full geometry block of both cells (alignment, × chance, `top_eig_share`,
`effective_rank`, `flattening`) beside rs0's four cells, since those four are the same realization at lower
strengths and therefore the cleanest fixed-everything comparison the record has for this question.

## 4. What this cannot do

- **Map a transition.** Two strengths at one realization say which ensemble the walk approaches, not where the
  penalty changes; the penalty is not measured here at all (the mode has no arms).
- **Separate `top_eig_share` and `effective_rank` from alignment** — they move with the swap operation by
  construction, and if the walk converges those statistics should converge together.
- **Rule out a slow approach that needs 10^4×** rather than 16×; that is what the falsifier's wording is for, and a
  null result is a statement about the range tested.
- **Speak for the task draw** (`seed0` 0 throughout) or for other circuit sizes.
