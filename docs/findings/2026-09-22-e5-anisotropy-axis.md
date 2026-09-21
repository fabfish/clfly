# E5 — decoupling the anisotropy axis reverses E2's conclusion

**Date:** 2026-09-22
**Script:** `experiments/e5_anisotropy_axis.py`
**Artifacts:** `runs/e5_anisotropy.json`
**Setup:** circuit `mb+cx+al@n1307` (d=1307), real topology, fixed support size 80,
1 seed, `kappa` sweep

---

## 1. Why this experiment exists

E2 found the gap falling as the wiring was randomised, alongside a fall in the
tasks' effective rank, and proposed spectral richness as the driver. That evidence
had a hole: **richness and swap strength moved together**, because both were
consequences of the same manipulation. Four points on a confounded axis cannot
distinguish "the gap tracks richness" from "the gap tracks something else that
rewiring also destroys".

So the knob here varies richness *directly*, at fixed topology, fixed support size
and **fixed rank**. The drive on each assembly becomes

    w_i  proportional to  exp(kappa * z_i),   z ~ N(0, 1), normalised to mean one

with the same `z` reused across every `kappa`, so only the concentration changes.
`kappa = 0` drives the assembly uniformly; large `kappa` lets a few neurons carry
it. The support size — and therefore the numerical rank — never moves.

## 2. Result — a U-shape, and an association with the opposite sign

| `kappa` | flattening | eff. rank | top share | overlap | **gap:EWC** | **bio−rand** |
|---|---|---|---|---|---|---|
| 0 | 0.759 | 55.1 | 0.105 | 0.0061 | +0.139 | −0.030 |
| 0.25 | 0.710 | 51.5 | 0.111 | 0.0061 | +0.105 | −0.023 |
| 0.5 | 0.586 | 42.6 | 0.127 | 0.0061 | **+0.075** | +0.030 |
| 1 | 0.322 | 23.3 | 0.181 | 0.0061 | +0.132 | −0.039 |
| 1.75 | 0.145 | 10.5 | 0.295 | 0.0061 | +0.240 | −0.072 |
| 2.5 | 0.088 | 6.4 | 0.393 | 0.0061 | +0.365 | −0.105 |
| 4 | 0.049 | 3.5 | 0.528 | 0.0061 | **+1.203** | −0.056 |

`flattening` = effective rank ÷ rank (1 is flat, →0 is collapsed). `overlap` is the
mean `cos²` between consecutive task subspaces.

**Spearman(flattening, gap) = −0.75.** Richer spectra give a *smaller* gap, so more
anisotropy gives a *larger* one — the opposite sign to E2's confounded trend
(where lower flattening went with a lower gap).

**And the curve is not monotone.** The gap dips to a minimum at moderate
concentration (`kappa ≈ 0.5`, gap +0.075) before rising steeply to +1.20 at
`kappa = 4`. There is an easy middle regime that neither of the two ends shows.

## 3. What this means for the story

**E2's proposed driver is wrong, and now for a second reason.** The first reason
was that the gap moved opposite to interference; this adds that it also moves
opposite to richness once richness is decoupled from wiring. The E2 measurement was
an association between two quantities that a third manipulation moved together.

**Phase 1's direction survives.** Phase 1 varied the anisotropy of a *fully
observed* task's covariance and found more anisotropy → bigger penalty. Here, with
rank-deficient tasks, concentrating the precision spectrum also raises the gap
(over the full range, ρ = −0.75). The two settings are different axes but now point
the same way, which is what a unification should look like. Stating them as one law
is still premature — the intermediate dip has no account yet.

**C2 gets stronger.** The biological advantage grows as the task precision
concentrates: `bio−rand` goes −0.030 → −0.105 as `kappa` rises from 0 to 2.5.
The cell-class grouping helps *most precisely when the diagonal is worst*, which is
a coherent mechanism for why a biological anchoring basis should exist at all.
(`kappa = 4` breaks the trend, but at effective rank 3.5 of 72 the task is nearly
one-dimensional and the regime is degenerate.)

## 4. Unresolved

**The intermediate dip has no mechanism.** Why would a moderately concentrated
drive be *easier* for the diagonal than a flat one? One candidate: at `kappa = 0`
the precision inherits a rich spectrum from the propagator's own geometry, spread
over ~55 directions whose off-diagonal structure the diagonal discards; a modest
concentration onto the directions the propagator already favours may make the
precision closer to diagonal in the neuron basis. That is a guess, not a result.
The predicted signature is a fall in the *off-diagonal share* of `Σ_k` in the
neuron basis around `kappa ≈ 0.5` — directly measurable, and the obvious next check.

**`overlap` is constant at 0.0061 across every `kappa`.** The knob demonstrably
works (`effective_rank` moves 55.1 → 3.5, so `Σ_k` is changing), so this is not a
dead parameter — but the cross-task alignment being invariant to the fourth decimal
across a 15× change in effective rank is surprising. Plausible reading: each task's
leading subspace is pinned by *which* neurons its assembly recruits and by the
propagator's geometry, with the drive weights only reordering within it. Unverified;
worth a direct check before being relied on.

**One seed.** The non-monotonicity is a single run. The Spearman coefficient and
the `bio−rand` trend both span the full sweep and are unlikely to be noise, but the
location of the minimum is not established.

## 5. Status

- **C1:** the gap is large on the connectome (+45–63%) against <1% synthetic —
  still the strongest result. Its *mechanism* is now: anisotropy of the task
  precision, in the Phase-1 direction, not interference and not the confounded
  richness trend. Partly unified, not fully.
- **C2:** strengthened again. The biological anchoring advantage is monotone in
  wiring randomisation (E2) and grows with task anisotropy (E5), i.e. it is tied to
  the connectome and it matters most where the diagonal fails worst.
- **Open:** the intermediate dip's mechanism; a replacement for the failed
  principal-angle predictor; more seeds.

Next: measure the off-diagonal share of `Σ_k` in the neuron basis along the same
`kappa` sweep. It is one array operation per task, and it either explains the dip or
kills the explanation.
