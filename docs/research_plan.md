# Research plan

## The question

EWC anchors its Fisher matrix in the **neuron coordinate basis** — that is what
"diagonal Fisher" means. LGCL makes the consequence exact: EWC *is* a Kalman
filter whose posterior covariance is projected onto the coordinate basis at every
step, so the diagonal is not a computational shortcut, it is the entire
approximation.

Which raises a question nobody has asked systematically:

> If you are going to project the posterior covariance onto some structure, why
> that structure?

The literature is thin. One 2018 paper (*Rotate your Networks*) rotates weights
to improve the diagonal Fisher. There is no matched-budget comparison of
parameter / eigen / neuron / module / cell-type bases. And there is no work at
all applying continual learning to a connectome-constrained network — full-text
searches for `connectome AND continual learning` and `connectome AND catastrophic
forgetting` both return nothing.

The reason the question has gone unasked is in the Phase-1 findings: in synthetic
tasks with random rotations the diagonal projection is **nearly lossless** (<1%
excess), so there was nothing to notice. But that flatness is a property of random
task geometry, not a law. Our probe (`docs/findings/2026-09-20-phase1-lgcl-port.md`
§3.2) shows the penalty is governed by task **anisotropy and low effective rank**,
rising ~500× as the spectrum steepens. And a real network's task geometry is
extremely anisotropic — LGCL v7 measured effective rank ≈ 2.0 in a trained MLP's
feature Gram.

So the substrate choice is not decorative. It decides whether the question has an
answer.

## The substrate

FlyWire adult brain, public release 783: **138,639 neurons, 15,091,983 connections**
(read from the data — `graph.build()`; the annotation table has 139,248 rows), with a
systematic annotation table giving **flow, superclass, cell
class, nerve, lineage, side, morphology group, neurotransmitter** for most
neurons.

Wiring is frozen (a fixed sparse mask from the connectome); synaptic weights are
learned. That is the standard connectome-constrained regime, and it is what makes
the basis question well-posed: the neurons, and every biological grouping of them,
are given, so "anchor here or there" is a fair choice rather than a modelling
artefact.

Why not the alternatives:

- **`flyvis`** (Turaga lab) is genuinely trainable and pip-installable, but covers
  only the optic lobe. No mushroom body, no central complex — which kills C3 and
  C4 below. Kept as an optional integration.
- **The Shiu/Eon whole-brain LIF model** has no plasticity at all: weights are
  fixed and only activation/silencing are supported. Nothing to train, so nothing
  to forget.
- **Codex / neuPrint APIs** now require Google sign-in or tokens. The Zenodo dumps
  and two GitHub mirrors are open, so we use those.

## Claims

Stated so they can fail.

### C1 — Substrate effect

The EWC↔Kalman gap is **substantially larger** on the connectome topology than on
controls with matched degree sequence, matched edge count, and matched spectrum.

*Status after `e2`: the effect is real and large, the mechanism is not what we
first said. The measured gap on wiring-derived tasks is **+33–34%** of the oracle's
error (`e3_analytic.json`, 5 and 18 seeds, and `e3_large.json` at cs = 3000) against <1%
in LGCL's random-rotation family.*

*And the realization-based estimate of the same contrast, which this line used to quote as
`+45–63%`, is **not a value**: the same configuration gives +35.8 ± 13.5% at five seeds and
+60.1 ± 43.9% at three (`runs/e3_analytic.json`, `runs/e2_analytic.json`), because its
per-seed sd is as large as its own mean. The `+45–63%` range matched no artifact in `runs/`
— its upper end was the mean of the per-seed ratios rather than `gap_of_means`, its lower end
nothing — and the analytic figure above is what the claim rests on
(`docs/findings/2026-09-23-the-realization-range-has-no-artifact.md`).*

*What is supported:* the connectome's task subspaces are **7× more orthogonal than
chance**, and rewiring monotonically destroys that (up to 5× *more aligned* than
chance at Erdős–Rényi). The geometry half of the claim holds cleanly.

> **And this half is now measured to be seed-robust**, which the interpretation below is not. Every
> one of the **27** task seeds behind the five checkable `swap0.5 → swap2` contrasts agrees with its
> contrast's sign (6/6 at each of cs400/500/600/700, 3/3 at cs300), **no leave-one-seed-out removal
> flips any of them**, and the largest single-seed leverage is **0.58–0.77** on a scale whose
> ceiling is 1 (for a single-outlier contrast leverage is *exactly* 1, an identity pinned in the
> tests). Contrast `e5`'s association, where one seed of three carried it and another had the
> *opposite* sign and every pooled statistic was null. So **the existence of the instability is
> solid and only its interpretation failed** — that split has been implicit for four findings and
> `e47` makes it measured
> (`docs/findings/2026-09-22-c1-contrast-is-seed-robust.md`).

*What is refuted:* the gap does **not** track task overlap. Across the
degree-preserving family the gap moves *opposite* to interference — overlap rises
8× while the gap falls by two-thirds. The first mechanism story was wrong.

> **And that refutation is a statement about one graph — but not because the statistic is noisy.**
> It rests on a single contrast, `swap0.5 → swap2`, and across five circuit sizes that contrast is
> **+0.03525 (21.8σ), −0.00304 (4.8σ), +0.01054 (14.5σ), −0.00223 (4.4σ), −0.01079 (32.7σ)** at
> d = 952, 1010, 1086, 1149 and 1307. The earlier "the sign alternates, and every step is decisive"
> was a property of having exactly four points: the fifth breaks it (+, −, +, −, −). Two fires ago
> I attributed that spread to re-drawing the swap realization; **measured directly at fixed circuit
> size and fixed tasks, re-drawing moves `excess(swap2)` with sd 0.00303 at four realizations — 6.8×
> less than the 0.0205 attributed** (χ² p = 0.0044), and ER's is 0.00353, 5.8× less (p = 0.0069).
> The final counts settle it at a **~5.4×** margin: `swap2` **0.00377** over all 6 realizations
> (p = 0.00059, range 0.00930) and ER **0.00320** over 6 (p = 0.00026), the latter spanning **5.3% of
> its own mean** against the 67% the withdrawn attribution required. The margin moved 16.3× → 6.8× →
> 5.9× → **5.4×** as realizations were added, i.e. it is settling rather than drifting.
> So the sweep's spread is not realization noise, and `e34`'s "the 152σ becomes 4.5σ" is void.
>
> **And the coordinate I proposed for the sign does not work either.** Across those five circuits the
> sign is monotone in `swap2`'s effective task-precision rank (`−, −, −, +, +`, ρ = +1.000, exact
> p = 0.0083, separator bracketed in [2.476, 5.040]), and neither effrank nor the excess is monotone
> in d. But that is a property of the five points: the bracket has no coverage and the first
> realization drawn **above** it (effrank 5.853) gives a contrast of **−0.00377 at −10.0σ** when the
> rule requires positive, taking the nine-point ρ to **+0.767**. The sign is therefore neither
> explained by the geometry nor reliably predicted by it. (`cs700`, d = 1229, was the pre-registered
> sixth point and **missed the stated ±0.0034 band by 1.84×**, residual −0.00627, which took the
> six-point ρ from 1.000 to **+0.829** and the fit's own in-sample maximum residual from 0.00296 to
> 0.00512. It landed *inside* the sign rule's bracket, so it tests neither the rule nor the mechanism
> — and narrows the bracket's lower edge from 2.476 to 2.806.)
>
> The mechanism behind that coordinate is withdrawn at the same time, refuted on two further axes.
> Re-drawing the rewiring at fixed circuit size, which moves the effective rank a second way, gives
> log slopes **13.6σ apart** between `swap2` and ER (0.0047 ± 0.0009 against 0.0340 ± 0.0020) with the
> circuit sweep's own 0.0206 matching neither; the linear-in-effrank form is the one the two
> realization families agree on (0.00147 against 0.00110) and it is 2–2.7× too shallow for the circuit
> sweep. **No single monotone form fits all three families** — the implied slope depends on which
> interval of effective rank you probe, which is what a shared confound looks like and a carrier does
> not. And the curve misses realizations whose effective rank lies *inside* its own fitted range, worst
> by **0.01902**, 6.4× its in-sample maximum residual.
>
> **And the intervention that was supposed to test the mechanism cannot run where the mechanism was
> proposed — but where it *can* run, it no longer contradicts it.** `e37` has finished all four
> `kappa` sweeps. At `real` the knob travels **0.68–0.73** in `flattening` across κ 0→4 against a
> seed-to-seed spread of 0.0026–0.0050, i.e. **142–271× the noise**; at `swap2`/cs = 800 it travels
> **0.004–0.008** against 0.00044, i.e. **8.6–19.3×** — **~90× less travel**, because the carrier is
> *already* collapsed (`effective_rank` 1.70 against `real`'s 55) and its precision is 99%
> off-diagonal. So that configuration is **untested, not null** (plan rule 18).
>
> At **`swap2`/cs = 300** the knob *does* have leverage — **30×** the noise, driving `effective_rank`
> from **16.6 → 2.35** — and there, on the prescribed absolute metric, the three seeds give
> **+0.143, +0.214, +0.357**: the **mechanism's** direction, unanimously, none significant
> (p ≥ 0.43), over a non-monotone curve that falls from 0.0766 to 0.0381 across κ 0→2.5 and then
> **rises back to 0.0821 at κ = 4**.
>
> **So the mechanism's status splits.** Its *quantitative* form — a shared log slope, ±0.0034 bands —
> is refuted (cross-family slopes 6.06σ apart, `cs700` 1.84× outside its pre-registered band,
> realizations inside the fitted range missed by 0.01902), and so is the cross-circuit sign rule
> (above its bracket at −10σ). The §6b smoke-test caveat that shaped this paragraph for two fires was
> **one seed of three** — it reproduces seed 0 exactly (1.1244 → 1.2572) while seeds 1 and 2 fall, and
> the 3-seed means fall too — so it is withdrawn.
>
> **And its *ordinal* direction is now measured at twelve seeds, not three, in both places it can be:**
>
> | configuration | metric rule 3 prescribes |
> |---|---|
> | `real`/cs = 800 — where `e5` was published | **reversed, marginally**: mean +0.265, 9 positive / 2 negative / 1 tied, sign p = **0.065**, pooled p = 0.037 |
> | `swap2`/cs = 300 — where the mechanism is testable | **null**: mean −0.009, **6 positive / 4 negative / 2 tied**, sign p = **0.754**, Wilcoxon p = 1.00, pooled p = 0.49 |
> | `swap2`/cs = 800 — where the mechanism was proposed | **untested** — the knob is inert there (rule 18) |
>
> The three seeds this paragraph previously cited as "3 of 3 point its way at p ≥ 0.43" are three of
> the six positives of a null distribution. So the mechanism is **reversed in one place, absent in the
> other, and untestable in the third**, and the honest summary of four fires is: **the effective rank
> orders the excess within a circuit's task draws, and nothing about it predicts or explains the
> excess across circuits.**
>
> **And the metric choice decides the answer in both directions.** At `real`/cs = 800 the banned
> relative gap **hid** the reversal (mean +0.009, 7/5/0, p = 0.77 against the prescribed p = 0.065); at
> `swap2`/cs = 300 it **manufactured** a strong negative association (3 positive / 9 negative,
> Wilcoxon p = 0.0068, pooled p = 4e-6) which the rank decomposition attributes to the **oracle**:
> ρ(oracle, flattening) = +0.79 and `rank(gap) = 32.0 − 0.66 rank(oracle) + 0.89 rank(excess)` at
> R² = 0.85. Rule 3 now carries both directions of failure, which is what makes it auditable rather
> than asserted.
> (`docs/findings/2026-09-22-mechanism-null-at-12-seeds-and-my-sign-test-was-wrong.md`)
>
> **And the coordinate search is now enumerated rather than anecdotal.** All eight recorded geometry
> coordinates, on three axes, with the multiple-comparison structure reported instead of assumed
> (`e53`): **no coordinate survives across circuit sizes alone** (ρ = +0.829, raw p = 0.058 at n = 6,
> corrected 0.117 — a power limit, not a refutation), but **`effective_rank` and its negative
> `top_eig_share` do survive across one circuit's realizations** (ρ = +0.943, corrected **p = 0.033**)
> **and on all twelve points pooled** (ρ = −0.895, corrected **p = 0.0008**). Two corrections were
> needed to see that: the eight coordinates collapse to **two** distinct orderings on the cross-size
> axis and five on the pooled one, so Holm over eight counts one line of evidence five times and put
> the realization axis on the wrong side of 0.05; and the intended negative control
> (`chance_alignment`) turns out to equal `mean_rank / d`, so it is collinear with a real coordinate
> and this sweep has **no** internal falsification test.
>
> **So the plan's phrasing is corrected: the coordinate accounts for the *ordering* of the excess and
> not for its *magnitude law*.** The law is refuted separately (cross-family slopes, the missed
> pre-registered band) and the across-circuit sign rule separately again. "No coordinate accounts for
> it" invited the reading that the ordinal relation was dead too, and it is not.
> (`docs/findings/2026-09-22-coordinate-search-enumerated.md`)
>
> **The position on the instability itself is unchanged: `excess(swap2)` is not a stable quantity
> across circuits, and no coordinate accounts for it *quantitatively*.** What does carry weight is
> structural and unchanged over six circuits: the two control topologies hold to **10.5%** (`real`)
> and **24.3%** (`swap0.5`) while `swap2` spans **166%** — measured seed-robust at 27/27 unanimous
> signs (`e47`) — and the Erdős–Rényi separation remains a regime offset by a factor of eleven with
> its realization check done and passed.
> (`docs/findings/2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md`,
> `docs/findings/2026-09-22-cs700-rejects-the-geometry-reading.md`,
> `docs/findings/2026-09-22-the-knob-is-inert-where-the-mechanism-was-proposed.md`,
> `docs/findings/2026-09-22-the-smoke-test-was-one-seed.md`)

*Replacement, after `e5`: anisotropy, in the same direction Phase 1 found.* Vary
the task's spectral concentration **directly**, at fixed topology, fixed support
size and fixed rank, and the gap is U-shaped in concentration with an overall
negative association with flatness (Spearman −0.75) — i.e. more anisotropy gives a
larger gap, matching Phase 1's direction on a different axis. Two corrections to
the intermediate story: the confounded `e2` trend had the *opposite* sign, and the
curve is non-monotone, dipping to a minimum at moderate concentration (+0.075)
before rising to +1.20. **The intermediate dip has no mechanism yet**; the
predicted signature is a fall in the off-diagonal share of `Σ_k` in the neuron
basis around `kappa ≈ 0.5`. Unifying the fully-observed and rank-deficient
anisotropy axes is the main open theoretical question.

> **⚠ This replacement is a single-seed result and is now marked as such.** `e41` re-checked it
> against the artifact it cites and found three things. The finding says "1 seed" but
> `runs/e5_anisotropy.json` holds **three**, and the published table reproduces in **35 of 42
> cells — every disagreement in the two realized-error columns** (`gap:EWC` 4, `bio−rand` 3) while
> every geometry cell matches, which is rule 5 exactly. `e43` then settled which side is stale:
> `e37`'s `real` cs=800 arm re-ran the same configuration in another process and reproduces **all
> 21** `(seed, kappa)` points of the artifact, worst deviation 0.5× the log's print-rounding
> tolerance — so **the artifact is live and the published table is the stale thing.** Substituting
> **one** published cell
> (`gap:EWC` at `kappa = 0`, +0.139 for the stored +0.0621) reproduces the published Spearman
> **−0.7500 exactly** *and* is what moves the curve's minimum from `kappa = 0` to `kappa = 0.5`, so
> **the −0.75 and the "easy middle regime" are the same single cell; with the stored value there is
> no U-shape.** And the association is carried by one seed of three: per-seed ρ(gap, flattening) is
> **−0.964 (p = 0.0004), −0.321 (p = 0.48), +0.107 (p = 0.82)**, pooled **−0.282 (p = 0.216)**, and
> under the metric rule 3 actually prescribes — the **absolute** excess — pooled **+0.040 (p = 0.86)**
> and `kappa`-mean +0.143 (p = 0.76). **So "more anisotropy gives a larger gap" is supported by one
> realisation and not established**; it is not refuted, and the direction may well be right, but it
> cannot carry the corrections below until it is re-run with more seeds. Note also that the absolute
> metric does **not** fix the seed variance here (CV 0.30–0.97 against the relative metric's
> 0.18–0.94; at `kappa = 4` the absolute excesses are 0.0174, 0.0191, **0.0001**), so a re-run has to
> buy seeds, not a better metric.
> (`docs/findings/2026-09-22-e5-does-not-reproduce-its-own-artifact.md`)
>
> **And the same manipulation run at cs = 300 — an independent task draw — does not rescue it, and
> points the other way.** Four pooled statistics, **none significant**: on the relative gap cs = 800
> gives **−0.282 (p = 0.216)** and cs = 300 gives **−0.395 (p = 0.077)**; on the **absolute** excess
> that rule 3 prescribes they are **+0.040 (p = 0.862)** and **−0.103 (p = 0.658)** — two of the four
> with the *opposite sign* to the claimed direction. So under the metric the project itself prescribes
> the association is **absent from the pooled statistic at both circuit sizes**.
>
> What does repeat is the shape of the failure: **exactly one seed of three** shows a strong
> association in each draw, and the two strong seeds agree closely — **−0.964 and −0.893** (relative)
> and **−0.929 and −0.893** (absolute). The reading is that the association is a **per-seed event
> occurring in a minority of seeds**, not a uniform property with noise on top: that is consistent
> with both draws (2 strong hits in 6 seeds) *and* with every pooled statistic being null, which is
> what a mixture produces when it is averaged. Six seeds can say the shape repeats; they cannot
> estimate the mixing weight — `e42`'s 12 seeds can.
>
> *(This paragraph replaces an earlier version of itself, committed ten minutes earlier in the same
> fire, which reported that the pooled verdict "flips" to significant at cs = 300. That was an
> artifact of pooling an **incomplete seed** from `e37`'s in-flight log: completing it moved the
> p from 0.032 to 0.077, across the significance line, and also retracted a second claim about an
> opposite-signed seed.)*
> (`docs/findings/2026-09-22-e5-pattern-repeats-at-a-second-circuit.md`)
>
> ### ⚠ And with twelve seeds it is **reversed**, not merely absent
>
> `e42` ran the same configuration — cs = 800, `real`, the same seven `kappa`, `--seed0 0` — with
> **twelve** seeds. On the **absolute** excess that rule 3 prescribes, per-seed ρ(·, flattening) is
> **−0.929, +0.214, +0.071, −0.500, +0.643, +0.643, +0.929, +0.321, +0.429, +0.750, +0.607, 0.000**:
> **9 of 12 positive**, mean **+0.265**, median +0.375, sign test **p = 0.0654** (9 positive, 2 negative, **1 tied** — ties dropped; see
> the correction in that finding), and pooled over all
> 84 points **ρ = +0.228, p = 0.037**. `e5` claims ρ < 0, so **the direction is reversed** — with
> Wilcoxon (p = 0.13) and t (t = +1.69) dissenting, so the honest reading is *reversed, marginally*,
> the disagreement living in two large negative seeds.
>
> **On the relative gap `e5` reports, the same twelve seeds say nothing**: 5 of 12 negative, sign
> p = 0.77, pooled ρ = −0.071 (p = 0.52). **The metric rule 3 was written about decides whether this
> experiment reports a null or a reversal — and it cuts against the project's own published number.**
>
> So `e45`'s "a minority of seeds carries it" is **superseded**: the per-seed distribution is centred
> at a *positive* ρ with one strongly negative tail, not a mixture with a minority of hits. That
> reading was itself an n = 3 shape, which `e45` §5 listed as its own limit. Seeds 0–2 of `e42`
> reproduce the published artifact exactly (−0.964 / −0.321 / +0.107), so the three-seed sample was not
> unlucky in any identifiable way — its mean was simply reported as the result for three fires.
> (`docs/findings/2026-09-22-twelve-seeds-reverse-the-e5-direction.md`)
>
> Everything in the paragraph below about `swap2`'s opposite sign is unaffected — it rests on the
> `e2` scale sweep, not on `e5` — but the sentence "two of three topologies follow `e5`" now compares
> against a reference whose direction is **reversed at 12 seeds** and should be read accordingly.

*And the sign is not topology-free.* In the `e2` scale sweep — where the **wiring** is
the variable and `flattening` is a consequence of it rather than an intervention —
`swap2` shows the **opposite** sign: its most anisotropic point (flattening 0.0235) has
the *smallest* excess and its least anisotropic (0.2334) the largest, while `real` and
`swap0.5` follow the direction above. So the relation here is a statement **at fixed
topology**, and applying it where the wiring varies is not licensed. `swap2`'s flattening
also spans **895%** across the sweep against `real`'s 4.2%, which localises that anomaly
to the propagated task spectrum rather than the filter
(`docs/findings/2026-09-22-swap2-geometry-anomaly.md`). The test is `e5`'s own
intervention applied at a rewired topology — **now run** (`e5_anisotropy_axis.py
--topology`, `e37`) because the smoke test already contradicted the sign `e37` was
built to confirm.

*And `e2`'s replacement is itself a single-draw result.* Everything immediately
above about `swap2` rests on **one realization per topology** at one circuit size,
which is why `e36`-`e40` went after it: five then six circuit sizes, four
realizations per topology, and an intervention on concentration. All three axes
rejected the coordinate — see the C1 section above.

*Controls (all required, or the claim is uninterpretable):* degree-preserving
double-edge swaps at several strengths, Erdős–Rényi at matched density, and a
matched-spectrum random graph. Note Erdős–Rényi is a **separate regime**, not the
end of the swap axis: it also destroys the degree sequence and makes `(I − W)`
near-singular, so the propagator conditioning changes too.

*And every σ in this family is a single-realization figure — but the realization is no longer the
thing to worry about.* Each topology is one draw of its rewiring rule, so the reported σ measures
seed noise *within* that draw and says nothing about drawing another graph. That exposure has now
been **measured** rather than assumed, and it is small: at fixed circuit size and fixed tasks,
re-drawing `swap2`'s rewiring moves its excess with **sd 0.00125** (3 realizations, χ² p = 0.0037
against the previously assumed 0.0205) and re-drawing Erdős–Rényi moves it by **0.00047**, 0.33% of
its own value. So the 152σ is not realization-fragile in the way the earlier arithmetic feared, and
`e34`'s "the 152σ becomes 4.5σ" is **void** — its input was the 0.0205 that the size sweep's spread
was mistakenly attributed to. What the sweep's 367% actually reflects is the circuit, interacting
with the rewiring through the **effective rank of the task precision** (`e36`); the realization
contributes about 1/20th of it. The line's numbers remain single-graph statements, and the
**structural** reading — a separate regime, offset by a factor of eleven — is still what should
carry the weight (`docs/findings/2026-09-22-realization-attribution-refuted.md`).

### C2 — Basis selection *(the core contribution)*

The best anchoring basis is a **biological module basis** — cell class, cell type,
hemilineage, or nerve — and it beats the neuron basis by more than
capacity-matched random partitions do.

*Status: **resolved at the rung level; the curve's shape is not**.* The five-rung table below is at
5 task seeds; re-running at **18 seeds** refines it to `side` 28.8σ, `cell_class` 12.1σ,
`hemilineage` 9.3σ, `supertype` 4.3σ, `cell_type` 0.7σ — four resolved, and the fifth is the rung
that is nearly the diagonal. **Every σ in that table is seed-only and therefore inflated for the
coarse rungs**, by the control-draw component (rule 10, and
`docs/findings/2026-09-22-control-drawn-once.md`); the ladder's best rung is 42.2σ seed-only and
**13.7σ** at the measured draw sd (`docs/findings/2026-09-22-draw-budget.md` §9). The five rungs
are what the annotation vocabulary offers, and four of them sit in the top 15% of the

> ### ✔ And the core claim passes the per-seed discipline that overturned C1
>
> `e57` asked the three questions C1 was taken apart by — sign unanimity, leave-one-out, and which
> axis carries the noise — of the pool ladder, the one C2 family whose artifact stores
> `excess_per_seed` (twelve seeds, cs = 800):
>
> | rung | Δ | seed sem | σ (seed only) | signs | LOO min σ | leverage |
> |---|---|---|---|---|---|---|
> | `pool1` | +0.00019 | 0.00003 | +7.35 | `++++++++-+++` | 6.6 | 0.80 |
> | `pool2` | −0.00801 | 0.00034 | −23.3 | `------------` | 21.3 | 0.53 |
> | `pool4` | −0.00884 | 0.00020 | **−44.4** | `------------` | 40.7 | 0.71 |
> | `pool8` … `pool128` | −0.0069 … −0.0041 | 0.0002–0.0003 | −31.0 … −17.9 | all `-`×12 | 16.3–35.4 | 0.51–0.60 |
>
> **Seven of eight rungs are unanimous over all twelve seeds, no leave-one-seed-out removal flips any
> sign, the smallest LOO σ is 6.6, and single-seed leverage is 0.51–0.80** on a scale whose ceiling is
> 1. C1's contrasts were unanimous over 3–6 seeds at 4–33σ; **C2 is unanimous over twelve and its
> weakest rung is still 16σ on the seed axis alone.** So the discipline that repeatedly overturned the
> side line does not touch the core one, which is the check that makes the discipline worth having.
>
> **The seed σ is nonetheless the inflated one.** The seed sem is 2–3e-05 while the measured
> control-draw sd reaches **0.001010** (`cell_type` min_size 3, five draws) — more than ten times it —
> so the −44σ is naive and the plan's 3–8σ rung-level figures, which fold the draw in, are the right
> ones. What is new is the per-seed structure, not the σ.
>
> **And the per-seed evidence is for the wrong family.** The headline is stated on the **named
> annotation bases**; the per-seed values exist for the **pool ladder**. `e3_seeds18` — **18 seeds, the
> most in the project, on the family the claim is on** — stores none, nor does the d = 1874 ladder.
> `e58` is launched to close the first (same configuration, 1.31 h the first time; the current code
> stores the field and that artifact predates it). The d = 1874 ladder is 5.64 h and stays open.
>
> **And the three lines have three different binding axes**: C1 the **circuit/realization**, C2 the
> **control draw**, C2b the **learner's seeds**. So "the bracket is a bracket", "the control is one
> draw" and "the floor is the floor" are three different corrections to three different lines, and
> none of them transfers — which is why each line needed its own check rather than a shared rule.
> (`docs/findings/2026-09-22-c2-passes-the-per-seed-discipline.md`)
>
> **Corrected (`e71`):** `e57` wrote C2b's figure as "62% of the per-replicate variance is the
> learner, not the test set". That is the inverse of the field it comes from — `e38`'s
> `floor_share_of_variance` is **0.619 for the `naive` arm at n = 9**, i.e. the *test set's* binomial
> sampling floor, so the learner is the other 38% there and **45%** in `e54`'s sixteen-replicate pool.
> For the **contrast** — the quantity the axis argument is actually made on — the floor's share is
> **43–46%** and the learner's at least 54%. The conclusion (seeds, not test size, are the lever) is
> unchanged: ten times the test set divides the floor by `sqrt(10)` for a 1.41× gain and no more.
> (`docs/findings/2026-09-23-the-62-percent-is-the-floor-not-the-learner.md`)
granularity range. The earlier
"consistent direction, ~1.3σ" reading was limited by the realized-error metric, not by
the effect. Measured on the **analytic expected error** (exact, no sampling noise — see
`docs/findings/2026-09-22-analytic-expected-error.md`), the
biological-minus-matched-random delta at 5 seeds is:

| rung | delta | σ (5 seeds) | σ (18 seeds) |
|---|---|---|---|
| `side` | −0.00480 | **12.93** | **28.78** |
| `cell_class` | −0.00307 | **3.68** | **12.14** |
| `ito_lee_hemilineage` | −0.00280 | **2.61** | **9.32** |
| `supertype` | −0.00146 | 1.23 | **4.26** |
| `cell_type` | +0.00026 | 0.22 | 0.74 |

The deltas agree in magnitude with the realized-error estimates, so the analytic
estimator measures the same effect with ~8× smaller standard errors. **The fly's own
groupings do beat size-matched random partitions, at four of five rungs, up to
28.8σ**, and the rung that shows nothing is the one the granularity result predicts
should (`cell_type` at 0.979 constrained is nearly the diagonal).

At d = 3150 with 2 seeds only two rungs resolve, which is a statement about budget
rather than about the effect: `cell_class` goes from 3.7σ at 5 seeds to 12.1σ at 18, on
the same measured delta.

The strongest basis *the annotation vocabulary offers* is `side`: four left/right/centre
groups beat a random 4-group partition of identical sizes at 28.8σ. The coarsest
structural split in the annotation table is its most valuable rung — but it is not the
best basis available, as the ladder below shows.

*What is also resolved:* **the annotation vocabulary under-reports biology's contribution.**
The five rungs put four of their number in the top 15% of the granularity range, and reading
the effect off them gave "granularity beats biology". A **granularity curve** — the cell-type
partition with groups smaller than ``N`` merged, for ``N`` ∈ {1…128}, each with a matched
random control — replaces them (`--ladder`, `docs/findings/2026-09-22-granularity-ladder.md`)
and gives a different picture: **7 of 8 rungs resolve**, at 17.8σ to **42.2σ**.

| pooling | constrained | biological excess | matched-random | σ |
|---|---|---|---|---|
| `pool1` (= plain `cell_type`) | 0.979 | +0.01743 | +0.01723 | 0.4 |
| `pool2` | 0.674 | +0.00496 | +0.01296 | **24.8** |
| **`pool4`** | **0.540** | **+0.00156** | +0.01041 | **42.2** |
| `pool8` | 0.450 | +0.00137 | +0.00822 | 30.1 |
| `pool16` | 0.432 | +0.00133 | +0.00898 | 39.1 |
| `pool32` | 0.322 | +0.00115 | +0.00814 | 37.9 |
| `pool64` | 0.322 | +0.00115 | +0.00664 | 20.9 |
| `pool128` | 0.191 | +0.00079 | +0.00488 | 17.8 |

Three things follow. **Merging only the singleton cell types** cuts the excess by 72% and
already beats a matched random control at 24.8σ. **The advantage is a plateau, not a peak** —
every rung's delta is resolved from zero (0.4σ at 0.979, 42.2σ at 0.540, 17.8σ at 0.191) but
the adjacent contrast `pool2 − pool4` is only 2.2σ while `pool1 − pool2` is 13.6σ, so what
resolves is a flat top over ~0.32–0.67 with both ends falling off, not an optimum at 0.540.
That non-monotonicity the five rungs could not see at all, having no rung between 0.50 and
0.83. And **the ladder's own best rung is
beaten at its own granularity**: `side` (0.501) has excess +0.00391 while `pool4` (0.540) has
**+0.00156**, 2.5× smaller, with the random control at that granularity (+0.01041) *worse* than
`side`.

So the honest form of a *rung-level* headline is: **the fly's own annotation vocabulary
under-reports biology's contribution, because four of its five rungs sit where biology
contributes almost nothing.** The practical recommendation is **"pool the rarest cell types and
anchor there"**, which needs no new ontology.

*But the curve's shape is unresolved, and it was the second time this fire that a shape claim
was withdrawn.* A matched-random control is a **single draw** from the population of
size-matched random partitions, and that population has a spread which was never measured.
Measured now (`experiments/e12_control_spread.py`): the draw-to-draw sd is ~**1.1e-3** for
coarse partitions (2–10 groups) — 3–6× the seed sem — and ~**4e-5–9e-5** for near-diagonal ones.
`pool32` and `pool64` are in fact the *same partition* and their controls disagree at 4.7σ,
which is where the question came from; and the ladder has only **six distinct partitions**
across its eight rungs (one group grows 723 → 867 → 952 → 968 → 1062 → 1167 while a 140-neuron
cell type never merges, so `pool32 ≡ pool64` and `pool128` is 2 groups). With the draw component
included the rung-level result is **4–9σ, not 20–42σ** — still a result — while the plateau, the
optimum's location, "`side` is uniquely weak", and the headline "granularity sets where you are
on the curve, biology sets the height" all collapse: they rest on differences of 0.0015–0.004,
the same order as the draw sd. `pool2 → pool4` goes 2.2σ → ≈0.6σ. The fine-end decline
(`pool1 → pool2`, ≈7σ) survives, because one of its rungs has a precise control.

*And the budgets are now known exactly* (`docs/findings/2026-09-22-draw-budget.md`). Averaging
the control over ``K`` draws enters as ``sd_draw^2/K`` — a per-observation spread, not a standard
error, so seeds do not reduce it. Inverting that gives, per claim, the required ``K``: the two
large steps need only **1.0–1.4** (`pool2 → cell_class`, `side → pool4` — the claim that a pooled
partition beats the vocabulary's own best rung), `pool128 → pool32` needs 2.9, and the plateau's
internal steps are **infeasible at any K** because their floor under the current 12-seed budget is
below 3σ (`pool4 → pool2` reaches only 2.2σ). That verdict contains no `sd_draw` at all — it is the
best the *seed budget* can deliver — so it cannot be overturned by measuring the draw sd better,
only by buying seeds (and the two claims worth buying need `K ≤ 5.5` even if `sd_draw` is wrong by
2×; §7 of the finding). The model calibrates on two contrasts whose true
value is zero (`pool32 ≡ pool64`, `pool1 ≡ cell_type`): it predicts the observed noise to within
4%, and the seed-only method had called one of them 4.7σ.

*These numbers were 2× too large in the first version*, because `draws_needed` applied its own
factor of √2 to terms the caller had already combined. One verdict was wrong (a contrast with a
3.3σ floor was reported infeasible), and the inconsistency was visible in the table — a floor above
the target beside a `K` column saying "infeasible" — and nobody looked. It is an invariant test now.

**So the region is a broad band, not a curve with structure**, and the two claims worth buying are
`pool2 → cell_class` and `side → pool4`, at two control draws each. The K=4 run is queued
behind the CPU queue (`e3 --control-draws K` is implemented and its wiring validated).

*And the ladder replicates at a second configuration — in form, not in number.* `e9` re-ran it at
**d = 1874 with support 150** (a 43% larger circuit *and* wider tasks, 12 seeds):

| | d = 1307, support 80 | d = 1874, support 150 |
|---|---|---|
| rungs resolved | 7 of 8 | **7 of 8** |
| the exception | `pool1` (`cell_type`), 0.4σ | **`pool1`, 1.6σ** — fourth confirmation of that null |
| rung σ range | 4–42σ | **22–62σ** |
| peak of \|delta\| | constrained **0.540** (`pool4`) | constrained **0.638** (`pool8`) |
| delta / oracle at matched granularity | **17.0%** | **9.5%** |
| distinct partitions | 6 of 8 rungs (`pool32 ≡ pool64`) | **6 of 8** (`pool64 ≡ pool128`) |

So the *form* replicates — a broad interior maximum, the `cell_type` null, biology beating matched
random throughout — while the **peak's position moves and the relative effect halves**. The degeneracy
is also systematic rather than accidental: each configuration has six distinct partitions across
eight rungs, in both cases duplicated at the coarse end, because the device is a count threshold
against a size distribution whose median is 1. A **rank-based** ladder (merge the *k* smallest
groups) gives eight distinct rungs by construction — it spans 0.469–0.979 at d = 1307 with no
duplicates — and is the fix for the fine-to-mid range
(`docs/findings/2026-09-22-ladder-replicates-at-d1874.md`).

**But the coarse end of any such curve is low-resolution by arithmetic, not by choice of device.**
`constrained ≤ 1 − (d/m + 1)/(d+1) ≈ 1 − 1/m` for a partition into ``m`` groups, so a rung at
constrained 0.5 needs at most four groups and anything below 0.67 needs at most three — and few
groups means blunt instruments. There is **no way to sample constrained < 0.47 with more than about
ten groups**, whatever the pooling rule. That is also *why* the annotation vocabulary is crowded near
the diagonal: constrained ≈ 1 − 1/m means most of the range is reachable only with many groups.
So "the vocabulary under-reports biology by placing four of its five rungs near the diagonal" is right
about the vocabulary and wrong to imply a device could do better — the honest recommendation is to
**anchor at the coarsest granularity the arithmetic allows you to distinguish (≈0.5–0.7, i.e. 4–10
groups) and accept that the fine structure of the coarse end is not measurable**
(`docs/findings/2026-09-22-coarse-end-is-arithmetic.md`).

The predictor handles the ladder at Spearman **+0.995** over 17 partition bases, including
eight of similar granularity distinguished only by which groups were merged — a case where a
predictor that merely recovered `constrained_fraction` would give them all the same score.

*Honest accounting:* `RotatedDiagonal` bases must carry `d(d-1)/2` rotation
parameters, so unless the rotation is shared across tasks a "rotated basis EWC" is
not a compression. Baselines rarely mention this; `bases.py` tracks it in
`n_shared_parameters`.

*Predictive machinery:* LGCL v8 showed the diagonalisation penalty is a geometric
resonance requiring the anchoring basis to align with the task's precision basis.
The principal-angle scalar **fails** — raw alignment is anti-correlated with the
benefit, and adding an empirical chance level recovers only 3 of 5 orderings, with or
without spectral truncation.

**It has been replaced by a working predictor.**
`clfly.bench.analytic.projection_pressure` runs the **exact** filter — whose prior
trajectory is basis-independent, so the number is available before any anchored filter
exists — and measures how much of each predicted prior the basis would discard,
weighted by the task's measurement information:

    pressure = sum_k || J_k^{1/2} disc_k J_k^{1/2} ||_F^2 / || J_k^{1/2} P_pred,k J_k^{1/2} ||_F^2

The weighting is what makes it more than a restatement of `constrained_fraction`.
On the real connectome it ranks 11 bases against the analytic excess at Spearman
**+0.991** and gets the sign right at all five matched bio/random pairs — including
the one where biology loses. Out of sample, across task width, drift rate, topology
and circuit size, it holds at **mean Spearman +0.984**, with **24 of 24** correct on
every matched pair whose excess difference clears 2σ *on the paired seed sem* — **19 of 20** once each
rung's measured control-draw component is included (`experiments/e6_predictor.py` re-run as `e64` with
per-seed storage; `experiments/e64_predictor_per_seed.py`). That count was re-derived with
the control-draw component included: it holds at **12 of 12** even if the fine columns' draw sd is
four times the estimate, with the sign record perfect at any multiplier from 0.1× to 10×, while
`side`'s individual σ at d=1307 falls from 15.53 to 4.47
(`docs/findings/2026-09-22-predictor-survives-draw-correction.md`). The sign test is the
decisive one: a predictor that only recovered `constrained_fraction` would score 0/25,
because matched pairs share it exactly.

> **Two refinements from reading the stored `resolvable` column (`e63`), neither of which changes the
> score.** The five conditions resolve **3, 4, 3, 0 and 3** of their five pairs on the *unpaired* sem,
> so the 13/13 was the whole of the evidence under that formula.
>
> **`e64` supersedes both halves of that**: on the paired sem the conditions resolve **5, 5, 5, 4 and 5**
> of their five pairs, and the swap2 condition is neither a null nor untested — it contains a 10.63σ,
> six-of-six-sign agreement that the predictor calls the wrong way.
> First, **the named "one failure" is an unresolved observation, not a wrong call with a large
> margin.** In the `rewired-swap2` condition the five pairs sit at **0.09, 1.74, 0.06, 0.75 and
> 0.23σ**; the disagreement is `cell_class` at **1.74σ**, the largest of the five, against a
> confidently-predicted negative (pressure delta −0.911 vs an observed +0.0034). Reaching 3σ on the
> seed component alone would need ≈18 seeds. So that condition is better described as **untested**:
> **zero of its five pairs resolve**, and the predictor has never been tested on a rewired topology.
>
> Second, the resolvable calls are effectively about the **three coarser rungs**: `cell_type` never
> resolves in any condition (0.03–0.26σ) and `supertype` in none either (1.5–2.2σ), so the score is
> carried by `side`, `cell_class` and `ito_lee_hemilineage`. That is `e35`'s arithmetic bound
> (`constrained ≤ 1 − 1/m`, hence a very fine partition *is* the diagonal) showing up in the
> predictor's own score sheet.
> (`docs/findings/2026-09-22-the-predictor-failure-is-unresolved.md`)

**And one gap this exposes:** the pairs' deltas are stored as **six-seed means**, with a σ but no
per-seed values, so whether any individual call is carried by one or two seeds is unchecked — the same
rule-8 omission `e57` found for C2's headline family (closed by `e58`), `e54` for the network `naive`
arm, and `e47` for the cs = 800 contrast. **`e64` has now closed it**: per seed, **24 of the 25 pairs
clear 2σ**, all 24 have unanimous per-seed signs, none flips under leave-one-out, the smallest LOO σ is
6.31, and the record is **23 of 24** — the one miss being `rewired-swap2`/`cell_class` at **10.63σ with
six of six signs agreeing**, which is a confident failure rather than the untested case `e63` inferred
from the unpaired σ (`docs/findings/2026-09-23-the-predictors-record-per-seed.md`).

Two honest limits. It is a **ranking** predictor, not a calibrated one — its dynamic
range varies by more than an order of magnitude across conditions while the
corresponding excess deltas stay of order 0.003–0.010. And it applies to **fixed**
anchoring structures only: it fails on state-dependent ones (spectral truncation),
because it scores each step myopically and cannot see the retained subspace being
renewed under it — measured step-to-step overlap 0.03 for `Rank(4)`, against 1.0 for a
fixed partition.

*Anti-p-hacking:* every comparison is at matched `n_parameters`, and the primary
control is a group-size-matched random permutation of the labels — identical group
sizes, identical parameter count, no biology.

*Honest accounting:* `RotatedDiagonal` bases must carry `d(d-1)/2` rotation
parameters, so unless the rotation is shared across tasks a "rotated basis EWC" is
not a compression. Baselines rarely mention this; `bases.py` tracks it in
`n_shared_parameters`.

### C3 — Modularity is itself a continual-learning mechanism

Interpolating the connectome toward a random graph by densifying **cross-module**
edges increases forgetting monotonically, and re-partitioning the same graph into
non-biological modules removes the benefit.

*Status: untested, and weakened by C1's refutation.* The claim assumed that task
interference is what a modular wiring protects against. `e2` refuted that mechanism —
along the degree-preserving swap family the diagonalisation penalty moves *opposite* to
task overlap, falling by a resolved 32.7σ between `swap0.5` and `swap2` while overlap
doubles — so the mechanism C3 was built on does not hold in the linear substrate. C3
would now have to be restated as a claim about whatever *does* drive the penalty
(anisotropy of the task precision), and that is not yet well enough understood to state
as a testable prediction.

*(That 32.7σ is an **unpaired** figure for a comparison whose seeds are shared across
topologies, so it is conservative in expectation rather than optimised — see the σ audit at
`docs/findings/2026-09-22-sigma-audit.md`. `e21` measures the paired figure and
`e2_topology_gap.py`'s contrast table now uses the paired formula where per-seed values
exist.)*

### C4 — Circuit overlap predicts interference

FlyCL tasks engage different circuits (olfaction → mushroom body, vision → optic
lobe, navigation → central complex). Each task is therefore naturally **partially
observed**, which by LGCL finding 4 puts the benchmark in the memory-dominated
regime. The prediction: **circuit overlap between two tasks predicts the
interference between them.**

*Status after `e7`: refuted as stated, supported in a corrected form.* A controlled
sweep with **exactly uniform** input-population overlap finds the opposite sign —
`Spearman(overlap, mean interference) = −1.000`, perfectly monotone, and at full
overlap adjacent tasks *help* (interference goes slightly negative). Sharing
measurement directions lets the next task confirm rather than compete. This is the
second independent refutation of the interference story, agreeing with `e2`.

The correction is that "circuit overlap" was ambiguous, and the ambiguity is the
whole finding. In the real circuit **all ten task pairs have exactly zero anatomical
support overlap** — the assemblies recruit disjoint cell types, so anatomical overlap
is not a variable there and +0.103 is noise around a constant. What *does* predict
interference is the **propagated** representation: the alignment of the tasks'
precision subspaces after the propagator mixes their disjoint inputs, at
**ρ = +0.939**, leave-one-out range [+0.917, +0.983], and not a size artefact (size
correlates +0.164 with interference).

> **An interference prior for a connectome-constrained benchmark must be read from the
> propagated representation, not from the anatomy.** Compute the task covariances,
> measure their subspace alignment, and the prior is available before any training run.

Limitation: ten pairs from five tasks. A benchmark with more tasks would test the
prior on more pairs — and the reason is sharper than "more pairs are better": the
pairs are not independent, so the test that matches the design permutes the **task
labels**, of which there are only ``T!``. **The smallest attainable p-value is
therefore ``1/(T!+1)``, so claiming p < 0.001 needs at least 7 tasks** (5 gives a floor
of 0.0083) however perfect the association is. Measured on the present run, the
task-level permutation gives **p = 0.0165** against 0.0002 for a naive pair
permutation — the naive figure overstates the significance by **83×**, and the
association is real but not as precise as it was implied to be
(`docs/findings/2026-09-22-task-permutation-c4.md`).

### C2b — the network basis negative has never been asked at the rung that matters

The rate-network line reports that a biological synapse partition never beats a
size-matched random one, across five settings. Every one of those settings used
`--basis cell_class`, and `cell_class` is a **single granularity point**: sweeping
`pool_below` over it moves `constrained_fraction` from 0.9250 to 0.9027, i.e. by 0.02.
The negative is therefore a statement about one rung, not about biological synapse
structure — the same confound E3b found on neurons.

The synapse annotation ladder is real, has five rungs, and its ordering matches the
neuron-level ordering exactly:

| column | groups | largest | constrained | GB | neuron-level (E3) |
|---|---|---|---|---|---|
| `side` | 10 | 10,126 | **0.6947** | 1.724 | 0.501 |
| `cell_class` | 100 | 5,509 | **0.9250** | 0.424 | 0.828 |
| `ito_lee_hemilineage` | 2,148 | 601 | 0.9945 | 0.031 | 0.967 |
| `supertype` | 9,938 | 452 | 0.9988 | 0.007 | 0.974 |
| `cell_type` | 19,618 | 421 | 0.9992 | 0.004 | 0.979 |

Three of the five rungs cost under 0.04 GB and all three sit near the diagonal — the
affordable rungs are precisely the uninformative ones, which is E3b's crowding
reproduced on synapses. **The coarsest rung, `side`, is the rung the neuron result most implicates — on
neurons it was the strongest rung (28.8σ) and the best basis the vocabulary offered — and it has since
been run: see the update below, which reports the negative holding and the test too weak to be decisive.**
*(This sentence read "has never been run" until 2026-09-23; `runs/e10_rung_side.json` has carried the run
since before the update paragraph was written, which is rule 22's drift in its usual direction — the gap
described as larger than the record shows.)*

`pool_below` is not a substitute: it does nothing on `cell_class` (0.9250 → 0.9027), and
on `cell_type` it jumps from 0.9992 (the diagonal wearing a label) straight to 0.6165
because merging every rare label into *one* shared group manufactures a single
`(pooled × pooled)` block holding **98.7%** of the partition's 2.165 GB. Bucketing the
merged mass into ``B`` groups (now implemented, `pool_buckets`) does drop storage as
``1/B`` — but it raises `constrained_fraction` back toward the diagonal by nearly as
much (0.6165 → 0.9744 at ``B = 4``), so it buys the fine end, not the middle.

What bounds the coarse end is **time, not memory** (33.6 GB available): block-Fisher
accumulation cost also scales with ``sum_g s_g^2``, so a coarse rung takes minutes per
run rather than seconds. That is affordable. **And a 4× share of that time was not
granularity at all** — the constant Fisher was being re-converted from numpy to torch on
every training step; `make_penalty` binds it once per task, taking the `side` rung from
24.3 to 6.0 minutes of penalty calls
(`docs/findings/2026-09-22-penalty-bound-once.md`).

> **But the footprint is only *one* of the two cost terms, and it is the wrong one at the fine end.**
> `e44` measured the per-step cost at the ladder's five real group counts and it is
> **`cost(µs) = 28 x G + 7.6e-4 x sum_g s_g^2`** (two fits under load: 28.3 and 32.9 µs/group; max
> relative residual 13–20%, against a pure `G^a` fit's 1.52 *in log*, i.e. a factor of 4.6). The
> reason is that `make_penalty` loops in Python over every group, so there is a per-group dispatch
> cost of tens of microseconds that is **independent of block size**, in addition to the dense matvec
> that scales with the footprint. The two terms cross at `G ~ sum_g s_g^2 / 40,000`, which puts `side`
> (10 groups) and `cell_class` (100) on the footprint side and `ito_lee_hemilineage` (2,148),
> `supertype` (9,938) and `cell_type` (19,618) on the **dispatch** side. So the sentence above is
> right where it was aimed and inverted at the fine end: the *fine* rungs are the most expensive per
> step despite having the smallest footprint, which is why `supertype` consumed **3.5 CPU-hours**
> finishing two of three arms while `ito_lee_hemilineage` finished all three in 46 minutes.
>
> The fix is to bind every block once into a single block-diagonal sparse matrix and replace the
> loop with one sparse matvec: **50x at `ito_lee_hemilineage`, 357x at `supertype`, 891x at
> `cell_type`** — and it **hurts** the coarse end (0.3x at `side`, 0.6x at `cell_class`), because a
> block-diagonal matvec has to touch the whole footprint. So a single route is not the answer; the
> right form is a hybrid keyed on the crossover. The measured numerical disagreement is 2.8e-15
> relative, which is **not** the bit-agreement `make_penalty`'s docstring promises with
> `penalty_tensor`, so the route is **not swapped here** — the measurement is the deliverable, and
> the change belongs behind an explicitly-named opt-in.
>
> **Which makes the cheapest correct action the same one `e35`'s arithmetic already implied: do not
> run `supertype` and `cell_type` at all.** They are the most expensive rungs *and* the ones whose
> answer is fixed in advance (`supertype`'s measured `constrained` is 0.9988, i.e. the diagonal).
> The five-rung ladder was a reasonable design before either fact was known; with both known, `side`
> (0.6947), `cell_class` (0.9250) and `ito_lee_hemilineage` (0.9945) are the rungs that can carry a
> claim (`docs/findings/2026-09-22-penalty-cost-has-two-terms.md`).

**So the honest claim is: at `cell_class` granularity, biology does not beat matched
random on synapses, in any setting tested.** Recorded in
`docs/findings/2026-09-22-synapse-annotation-ladder.md` while the
neuron line was being used to argue the network line was settled.

*Update — `side` has now been run and the negative holds, but the test is too weak to be decisive.*

| method at `side` | final accuracy | sem | mean forgetting |
|---|---|---|---|
| naive | 0.8241 | 0.0359 | +0.1007 |
| `ewc-block` (biological) | 0.8148 | 0.0346 | +0.0972 |
| `ewc-block-rand` (matched control) | 0.8264 | 0.0212 | +0.0938 |

Biological minus matched random: **−0.0116 accuracy** — the biological partition is
slightly *worse* and does not beat the naive baseline, so *this rung*, at *this* λ, shows nothing:
the network negative is not an artefact of having measured the wrong granularity. But the run only
bounds the advantage at **≈0.09 accuracy**, because the benchmark's own per-repeat sd is 0.048
(0.077 for forgetting). Detecting a 0.01 effect would take 86–202 repeats, i.e. **50–118 hours per
rung** — but 0.01 is the wrong target: at **0.03** resolution the same arithmetic gives 5–16
replicates, i.e. **0.9–12 hours depending on the rung** *(corrected 2026-09-23; this said 0.2–6 hours)*, which is one long working session rather than a short one. **The correction comes from re-measuring the per-arm-replicate cost on the four completed `e10` rung runs**: `ito_lee_hemilineage` **5.12 min**, `cell_class` 7.73, `side` 11.72 and `supertype` **22.86** — against the finding's stated **1.1–11.7 min**, whose upper end is `side`'s value alone and which excludes `supertype` entirely, almost certainly because that run was still finishing when the range was written. The arithmetic, explicitly: 2 arms x 5 replicates x 5.12 min = **0.9 h** at the cheapest, and 2 x 16 x 22.86 = **12.2 h** at the dearest. **The direction is the familiar one: the excluded run is the expensive one**, so the range made the rung question look roughly four times cheaper at its low end than the measurements support
(`docs/findings/2026-09-22-network-variance-is-learner-variability.md`).

Two consequences worth acting on, both **corrected by `e38`**.

The rate-network JSON stores `replicates`, and the bio-versus-control comparison shares a seed
sequence, so the paired sem *looked* like the right error bar (1.5× tighter at `side`). **That is
now unresolved rather than established**: at n = 3 a correlation is estimated with a standard error
near 0.7, the six rung runs give estimates from **−0.98 to +0.97**, and the only run with enough
replicates to measure it (`n = 9`, λ = 0.003 `cell_class`) gives **+0.02 with a 95% interval of
[−0.65, +0.67]** — which contains all six and spans pairing gains from 0.83× to ~4×. So the choice
of error bar moves σ by a factor of two in either direction, and the honest move is to report the
replicate requirement as a function of the assumed correlation rather than to pick one.

And the diagnosis was wrong even though the arithmetic was right. **The `naive` arm is bit-for-bit
identical in every run that shares its training configuration** (0.8240740763, per-replicate
[0.895833, 0.791667, 0.784722] in the five that do), which confirms the shared seed sequence *and*
shows the benchmark is **deterministic given the seed**. The per-repeat spread is therefore not
measurement noise but genuine learner seed-to-seed variability, and no measurement change reduces it:
the plan's earlier reading of the 0.032 evaluation floor as "44% of the variance, removable" is
bounded at **1.28×** by `e38` on the one well-measured run (the floor is at most 43% of the
*contrast's* variance there). `--test 480` is still worth running because it is nearly free and
removes the only genuinely-measurable part — but the lever the plan wanted does not exist.

> **The independence is narrower than that sentence first implied, and `e54` measured it.** `naive`
> is independent of `basis`, `lam`, `fisher_batches`, `methods` and `repeats` — and of **nothing
> else**: it still depends on `iters`, `lr`, `batch`, `train`, `test`, `classes`, `noise`, `support`,
> `shared_head`, `input_overlap`, `readout_size` and `circuit_size`. A census of the fifteen artifacts
> that carry the arm finds **six distinct `naive` computations**, only one of which has more than five
> seeds — and the artifact set therefore holds **no more than nine seeds of any one computation**
> (n = 9, mean 0.8395, sd **0.0389** [0.0263, 0.0745], binomial floor 0.0306 = **62% of the
> variance**, so **38% of the spread is the learner**). Every cluster difference is explained by an
> affecting field, so there is no stale artifact hiding in the set — the census is about which runs
> compute the same thing. Agreement is established **from the data** (clustering runs that agree
> bit-for-bit on every *shared* seed) rather than from an assumed config key, because a wrong key
> looks like a larger sample: the first version merged `e8_rate` with the `e10` rungs and showed a
> seed carrying two values inside one group. `e46`'s 16 replicates will extend this to n = 16 with no
> change to the script. (`docs/findings/2026-09-22-naive-arm-census.md`)

*Remaining:* none. **The ladder stops at four rungs.** `supertype` landed at **3.43 h** for a fourth
null (Δ = −0.0185, −0.58σ, floor ±0.063, 119 replicates needed), and `cell_type` was **started and
stopped** on four independent grounds: its answer is entailed by `e35`'s arithmetic bound (19,618
groups over 26,568 weights is the diagonal), it is the most expensive rung per `e44`'s measured cost
model (~6 h against `supertype`'s 3.43 h), `e38`'s power analysis says a 3-replicate run cannot
resolve the effect anyway, and the three rungs that *can* carry a claim are already measured. The
freed queue goes to `e46` — 16 replicates at λ = 0.1, the only C2b measurement with a detection floor
small enough to matter
(`docs/findings/2026-09-22-ladder-stops-at-four-rungs.md`).

**Three of five rungs are now measured**, all at λ = 1.0:

| rung | constrained | biological | matched random | Δ accuracy | σ paired |
|---|---|---|---|---|---|
| `side` | 0.6947 | 0.8148 | 0.8264 | −0.0116 | 0.43 |
| `cell_class` | 0.9250 | 0.8426 | 0.8611 | −0.0185 | 0.35 |
| `ito_lee_hemilineage` | 0.9945 | 0.8333 | 0.8333 | 0.0000 ± 0.0305 | degenerate (mean in its own sem) |

All three are nulls with intervals of roughly ±0.03 accuracy, and none beats the naive baseline. Two
things about that: **λ = 1.0 is the λ at which the `cell_class` contrast is *smallest*** (−0.0185
against −0.0648 at λ = 0.1), so the rungs had been sampled where the effect is weakest. And ±0.03
accuracy against a neuron-level effect of about 10% of the oracle gap means a network effect of that
relative size would be invisible here
(`docs/findings/2026-09-22-ito-rung-and-degenerate-sigma.md`).

**And at λ = 0.1 the rung contrast appears to resolve — but its main term was three seeds.** `e28`
put the coarsest rung at that λ, and both runs share seeds, so the two deltas can be contrasted
paired:

| rung (λ = 0.1, batches 8) | constrained | Δ accuracy vs its own control | σ paired |
|---|---|---|---|
| `side` | 0.6947 | +0.0069 ± 0.0145 (n = 3) | 0.48 |
| `cell_class` | 0.9250 | **−0.0648 ± 0.0245 (n = 3)** | **2.65** |
| `side` − `cell_class` | | +0.0718 ± 0.0336 | 2.13 (same sign in all 3 replicates) |

> ### ✗ WITHDRAWN — `e46` ran `cell_class` at λ = 0.1 with **sixteen** replicates
>
> Same configuration, same code, and **its first three replicates reproduce `e31`'s six values
> bit-for-bit on both arms**, so the comparison is legitimate. The sixteen-seed deltas:
>
> | first k seeds | mean Δ | sem | σ | signs |
> |---|---|---|---|---|
> | **3** | **−0.0648** | 0.0245 | **−2.65** | `---` |
> | 6 | −0.0023 | 0.0353 | −0.07 | `---+-+` |
> | 12 | −0.0006 | 0.0214 | −0.03 | `---+-+-+--++` |
> | **16** | **+0.0039** | 0.0161 | **+0.24** | `---+-+-+--++++-+` |
>
> **The first three seeds are the three most negative of the sixteen, and they are the entire effect.
> Three more seeds take it from −2.65σ to −0.07σ.** At sixteen the signs are 7 negative / 2 tied /
> 7 positive — a perfect split — and the detection floor is **0.032** (19 replicates for 0.03, 167 for
> 0.01).
>
> So **"the rung contrast resolves at λ = 0.1" is withdrawn, and with it the mechanism reading** that
> the coarse rung wins because the fine one loses to its own control. The paired `side − cell_class`
> contrast loses its main term; `side` needs its own sixteen-replicate run (`e60`, launched) before the
> contrast can be restated. The line's position is now **nulls at every rung and every λ tested, with
> the best-powered measurement also a null** — a stronger negative than the plan had, because it is the
> *well-powered* configuration that is null.
> (`docs/findings/2026-09-22-the-c2b-rung-result-was-three-seeds.md`)

The cross-run comparison assumes an `ewc-block` arm is independent of the run's method list, and
**that is now verified bit for bit**: `e31` reproduced both arms across the two method lists
identically to the last decimal. That check had to be run deliberately — every cross-run comparison
in this line depends on it, and none of them could have detected a violation, because a violation
would have looked exactly like the difference between configurations they were measuring.

Three open items remain: n = 3 (the sem carries ~50% relative
error); the two intermediate rungs are still λ = 1.0 only, which is what decides between a gradient
and a step; and the mechanism — the coarse rung wins because the fine one *loses to its own control*
(−0.0648, 2.65σ), not because the coarse one gains (+0.0069, 0.48σ).

> **All three items are now answered and the third has nothing left to explain.** `e54` extended the seed
> censuses; `e46` ran `cell_class` at λ = 0.1 with **sixteen** replicates and the mechanism's main term
> collapsed from **−0.0648 (2.65σ) to +0.0039 (+0.24σ)**, because the three seeds it rested on are the
> three most negative of sixteen — so the mechanism reading is **withdrawn**. `e60` then ran `side` at
> sixteen replicates and `e76` restated the cross-rung contrast: **`side − cell_class` = −0.0191 ± 0.0216
> = 0.88σ on accuracy and +0.0352 ± 0.0291 = 1.21σ on forgetting**, against a published 3-replicate
> +0.0718 at 2.13σ — a null on both metrics, with detection floors of 0.026 / 0.032 / 0.043 saying the
> run could have seen it. So the λ = 0.1 rung question is closed as a null, and what remains open is only
> the **intermediate rungs at λ = 1.0** — a question about a line whose every well-powered measurement is
> a null (`docs/findings/2026-09-22-the-c2b-rung-result-was-three-seeds.md`,
> `docs/findings/2026-09-23-the-cross-rung-contrast-is-a-null-at-sixteen.md`).

> **All of `e10` is λ-conditional, and λ was never set.** The rungs ran at **λ = 1.0**, the argparse
> default — 300× the value the project's own sweep recommends (0.003) and beyond the range it swept
> (0.003–0.3), whose conclusion is that every λ ≥ 0.01 leaves EWC worse than naive. So the
> biological-versus-random contrast above is **confounded with λ** and cannot carry the rung
> conclusion until a tuned-λ arm exists. The power analysis and the pairing result are unaffected
> (they are properties of the benchmark's variance, not the penalty strength).
> `runs/e25_cell_class_lam0.003.json` supplies that arm on the same seeds and batch count
> (`docs/findings/2026-09-22-e10-lambda-not-set.md`). **And the λ dependence is not even monotone** —
> in the sweep, λ = 0.1 is worse than both 0.003 and 0.3 — so "0.003 is the only useful setting" is
> itself a claim about one configuration at one seed.

## The benchmark — FlyCL v0

Five sequential tasks, each landing on a distinct circuit, driven through the
connectome:

1. **Olfaction** — combinatorial odour coding through OSN → AL → KC → MBON
2. **Visual motion** — direction discrimination, optic lobe → LPTC
3. **Heading / navigation** — landmark-guided turning, central complex
4. **Looming / escape** — LC4 pathway
5. **Motor pattern** — descending neurons → VNC targets

Metrics: average accuracy; **decomposed forgetting** — irreducible drift term
separated from estimation degradation, as LGCL §5 recommends, because the
conventional forgetting metric rewards shrinkage and can be gamed; backward
transfer; the per-task observability spectrum; and pairwise task principal angles.

Baselines: Naive, EWC (neuron basis), EWC in each biological basis, Online-EWC,
SI, MAS, capacity-matched replay, joint-training upper bound, the Kalman oracle on
a low-rank linearisation, and a frozen-random control.

Reference framework: `clfly/bench/` with fixed task orders and seeds, so numbers
are comparable across methods — a shared protocol that CL-for-SNN work currently
lacks.

## Experimental programme

All of it has been run. The scripts as delivered:

| Script | Claim | Deliverable | Status |
|---|---|---|---|
| `e2_topology_gap.py` | C1 | excess vs topology along a swap family, four arms | done — mechanism refuted, and **the refutation is two numbers rather than one**: a paired **−28.85σ about the cs = 800 graphs** (6/6 task seeds negative) and **2.2σ about the rewiring rule** once `e65`'s six-draw `swap0.5` realization sweep is included (3.4σ comparing rule means, 5.8σ dropping each arm's worst draw). The original 32.7σ was the unpaired, single-realization figure |
| `e3_basis_selection.py` | C2 | basis ranking at matched capacity, analytic effect size | done — and **both families are now measured on one footing**: the five named rungs as **18.1 / 12.1 / 26.1 / 13.3 / 3.8σ about the rule** (paired, with the measured draw sds) and the eight ladder rungs as **2.6–13.7σ**, so the best named rung is 1.9× the best ladder rung rather than the ladder being an order of magnitude ahead (`e66`, `e73`, `e74`) |
| `e5_anisotropy_axis.py` | — | task spectral richness vs penalty, decoupled | done — e2's confounded trend corrected |
| `e6_predictor.py` | C2 | candidate predictor, out-of-sample, with resolvability | done — +0.984 (+0.995 on the ladder). **`e64` re-ran it with per-seed storage and the denominator doubles**: **24 of 25 pairs clear 2σ on the paired seed sem** (was 13), **24/24 unanimous per seed with no leave-one-out flip and LOO σ ≥ 6.31**, and **23 of 24 called correctly**. With each rung's measured draw sd, **21 clear and 20 are called right**. **`e63` is overturned**: its "the one failure is 1.74σ where nothing resolves" was an unpaired-σ artifact — the pair is `rewired-swap2`/`cell_class` at **10.63σ with `++++++`**, a confident wrong call, and `supertype`/`cell_type` resolve in every condition rather than never |
| `e64_predictor_per_seed.py` | C2 | the predictor's matched pairs checked per seed, at three denominators | done — `runs/e64_predictor_per_seed_analysis.json`. 25 pairs → 24 resolvable on σ(task) → 21 on σ(rule); correct 24, 23, 20 respectively. The single miss is `rewired-swap2`/`cell_class`. **One stale source had to be fixed to get this right**: the first version used `e14`'s *pooled* `cell_type` draw sd as a proxy for `cell_type`, which collapsed its σ(rule) to 0.07–0.42 and reported six pairs below 2σ where the answer is four. **AND THE DENOMINATOR TABLE ITSELF HAS A SECOND, UNFIXED DEFECT** (`e93`): `DRAW_SD_SOURCES` at `experiments/e64_predictor_per_seed.py:33-40` is keyed by **rung only** — five rows, no circuit-size key — and all five sources were measured at **cs = 800 / d = 1307 / support 80**, while four of the five conditions in the table ran at **cs = 300**. So **20 of the 25 pairs carry the wrong circuit's denominator and zero of those 20 carry one measured at cs = 300**; they were not interpolated, they were **borrowed from the other circuit size**, which is a different error with a different fix. `e86`'s cs = 300 half matches `baseline` exactly (support 30, q 0.02, `real`) and supplies the measurement for five of the twenty: the cs = 300 sds are **1.34× to 5.26×** the borrowed ones, and re-deriving `baseline` with `e64`'s own arithmetic leaves the count at **21 of 25 with no verdict changed** — the largest correction is `baseline`/`cell_class`, σ falling **11.26 → 4.92**, still far above the line, and `e94` then measured the other three conditions and the count DOES move: **20 of 25 clearing 2σ and 19 of 20 called correctly**, with exactly one pair changing verdict (`rewired-swap2`/`cell_type`, 2.32 → 0.87, called right). The twenty ratios between measured and borrowed denominators are **all above 1** (1.09 to 6.73, median 2.33), so the borrowing was systematically **optimistic** rather than merely noisy — see the `e94` row belowour times above the line. Untested and therefore still borrowed: `wider-tasks` (support 60), `faster-drift` (q 0.10) and `rewired-swap2` (`swap2`). **The fix is to key the table by `(rung, circuit_size)`** — and note the negative result is a statement about where the affected pairs sit, not that the denominators do not matter: §5 records a version of this count whose 2σ line fell between 1.94 and 2.17, where a 2.3× denominator change is decisive. |
| `e7_interference.py` | C4 | circuit overlap vs measured interference | done — anatomy carries zero signal; post-propagation predicts at +0.94 |
| `e8_rate_network.py` | — | the non-linear substrate, both settings, frozen-body control | **artefact restored, headline reproduces** — the claim (replay, pool 96 / per-step 8, −0.010 ± 0.006 = 4.2σ) had **no artifact**: all 77 runs stored `replay_per_task: 16`, `replay_batch: 16`, and the nearest instance gave **−1.17σ with `+----` signs, LOO σ [0.67, 5.66]**. `e61` recreated the configuration and gives **−0.08542 ± 0.01293 = 6.61σ paired** (5.48σ unpaired), 5/5 replicates negative, LOO σ **[5.19, 7.35]** with no flip, leverage 0.77; the naive arm is bit-identical to `e8_hardened`'s and replay's own forgetting is **3.21σ** where the published claim implies 1.67σ. **Per-step 16 gives +0.0104 against the claimed +0.017, and the inversion `16 − 8` is +0.02292 ± 0.00390 = 5.88σ paired.** `e62`'s "cannot be checked either way" resolves **in the claim's favour** |
| `e3_basis_selection.py --ladder` × d=1874 | C2 | second configuration (support 150, d=1874), 12 seeds | done — `runs/e9_ladder_d1874.json`, and the finding it produced ("replicates in form, not in number"). **Its `excess_per_seed` was missing, so `e79` re-ran the identical configuration** and `e57 --artifact` now analyses either ladder: **8 of 8 rungs unanimous over 12/12 seeds**, no leave-one-out flips, smallest LOO σ **9.0**, largest leverage **0.67** — against d = 1307's 7 of 8, 6.6 and 0.80, so the second configuration is the *more* robust of the two. And `pool1`'s disadvantage replicates: +0.00035 at **9.85σ paired**, 12/12 positive — the first independent confirmation of `e66`'s reversal |
| `e3_basis_selection.py --ladder` (re-run) | C2 | per-seed excesses for a paired shape test + determinism check | done — `runs/e3_ladder_v2.json`, analysed by `e57`; the paired shape test is what moved the ladder's σ from unpaired 20–42 to a paired 17.9–44.4 on the task axis, and `e73` later put it on the same footing as the named rungs (2.6–13.7 about the rule, all eight rungs now with a measured draw sd) |
| `e8_rate_network.py` × 5 rungs | C2b | synapse annotation ladder (0.6947 → 0.9992) | **four rungs and stopped** — all nulls at λ = 1.0, 3 of 4 with biology *below* its matched control, none resolving (largest \|σ\| = 0.58), floors ≥0.05 and `supertype` cost 3.43 h. `cell_type` was started and stopped on four independent grounds (`e35`'s bound, `e44`'s cost, `e38`'s power, and the three rungs that can carry a claim already being measured) |
| `e4_modularity.py` | C3 | never written | **C3 deprioritised** — its mechanism is contradicted by `e2` |
| `e12_control_spread.py` | C2 | how much of a matched-pair delta is the control *draw* | done — and **its headline reading is superseded by the runs it motivated**. It reported a draw sd of ~1.1e-3 for coarse partitions against ~4e-5 for fine ones, with a group-count mechanism; `e67` measured `side` (4 groups) at **2.16e-4** — 4.8× below the model's prediction and closer to the value the model was written to overrule — and `e72`/`e75` refuted two replacements for the scalar. **The mechanism is now known and is not a subspace overlap**: `projection_pressure` explains **83%** of the draw-to-draw variance on the same relabelling (`e81`), replicated at a second circuit size to ±0.02 (`e82`). Every σ in the paper takes the draw component from a per-rung measurement rather than from this model |
| `e3 --control-draws K` | C2 | average the matched control over K draws | done for **K = 3** — `runs/e13_control3_d952.json` (d = 952, 3 seeds), analysed in `2026-09-22-e13-averaged-controls.md`: averaging the control over three draws shrinks the draw component and is the cheap half of the fix. **K = 4 was never run** — the K = 3 result was enough to validate the wiring, and every σ that needs the draw component now takes it from a per-rung *measurement* instead |
| `e2_topology_gap.py --rewire-seed` | C1 | separate the swap *realization* from the circuit subsample | done — realization sd measured at 0.00125 for `swap2` (16× below the attributed 0.0205); ER moves by 0.00047, 0.33% of its own value |
| `e2_topology_gap.py --circuit-size 700` | C1 | the sixth point of the size sweep, and the test of the geometry reading | done — `runs/e26_size700.json`, and the pre-registered prediction **failed**: cs = 700 lands **1.84× outside** the ±0.0034 band the `e36` finding registered in advance, and the implementation the band was meant to bracket is missed by 0.01902 (`docs/findings/2026-09-22-cs700-rejects-the-geometry-reading.md`). The sixth point is what closed the geometry reading at four independent levels |
| `e36_geometry_carrier.py` | C1 | is the 367% spread a realization effect or a geometry effect? | done — geometry; the contrast's *sign* is a function of the effective rank of the task precision, ρ = +1.000, exact p = 0.0083 |
| `e5_anisotropy_axis.py --topology` | C1 | `e5`'s concentration intervention applied at a *rewired* topology | done, all four configurations — at `swap2`/cs = 800 the knob is **inert** (rule 18) so that config is untested; at `swap2`/cs = 300 it has **30×** leverage and the prescribed metric gives **+0.143, +0.214, +0.357**, the mechanism's *direction*, unanimously and none significant over a non-monotone curve |
| `e38_variance_budget.py` | C2b | what limits the network benchmark, and is `--test 480` the lever? | done — **the numbers are right and the emphasis was backwards**, per `e71`: the evaluation floor is **55% of the `naive` arm's per-replicate variance** (61.9% at n = 9), so the *learner* contributes 38–45% of the arm and at least 54% of the contrast. The `--test 480` gain is bounded at 1.28× and reproduces to 1.31×; ten times the test set buys 1.41×. So the binding constraint is the seeds, for a reason the original summary stated in the opposite direction |
| `e41_anisotropy_seed_fragility.py` | C1 | does `e5`'s anisotropy association survive its artifact, its other seeds and the metric rule? | done — **no**: the cited file is the 3-seed rerun and disagrees with the table in 7 of 42 cells (all in the realized-error columns); one cell reproduces both headlines exactly; the association is 1 of 3 seeds, p = 0.216 pooled, **+0.040 (p = 0.86)** on the prescribed absolute metric |
| `e43_e5_replication.py` | C1 | is the `e5` artifact live output or a stale file? | done — **live**: `e37`'s same-configuration arm reproduces all 21 `(seed, kappa)` points, worst 0.50× print-rounding tolerance, so the published table's discrepant cells are the stale thing |
| `e44_penalty_cost_scaling.py` | C2b | what actually bounds each rung's cost? | done — **two terms**: `28 µs x G + 7.6e-4 x sum_g s_g^2`, crossing at `G ~ sum_g s_g^2 / 40,000`; the fine rungs are dispatch-dominated (which is why `supertype` ate 3.5 CPU-hours) and a block-diagonal sparse route is 50–891× faster there but **slower** at the coarse end |
| `e45_e5_seed_pattern_across_circuits.py` | C1 | does `e5`'s seed pattern repeat at a second circuit size? | done — **no rescue**: four pooled statistics over two circuit sizes and two metrics are **all null** (p = 0.216, 0.077, 0.862, 0.658), two with the opposite sign; exactly one seed of three is strong in each draw (−0.964 and −0.893 relative, −0.929 and −0.893 absolute), so the association is a per-seed event in a minority of seeds |
| `e47_contrast_per_seed_signs.py` | C1 | is the C1 contrast seed-robust, or is it `e5` all over again? | done — **robust**: 27/27 task seeds agree with their contrast's sign, no leave-one-seed-out removal flips any, max single-seed leverage 0.58–0.77. **And it found a rule-8 hole**: `runs/e2_analytic.json` stores no per-seed values, so the 32.7σ figure is the one contrast that cannot be checked — `e48` launched to close it |
| `e2_topology_gap --circuit-size 800 --seeds 6` | C1 | per-seed storage for cs = 800 (`e48`), the only contrast lacking it | done — **the column reproduces bit-for-bit from its first three seeds** (all four topologies) and the refutation becomes a **paired −28.85σ with 6/6 seeds negative**, leave-one-out ≥ 23σ, against the published unpaired −32.7σ |
| `e49_kappa_leverage_by_topology.py` | C1 | does the concentration knob move the carrier where the mechanism was proposed? | done — **no**: travel/noise is **142–271×** at `real` and **9.4×, 20.2×, 5.3×** at `swap2`/cs = 800 because the carrier starts already collapsed (effrank 1.70 vs 55), so that configuration is **untested, not null**; the one `swap2` seed with leverage (−0.786, p = 0.036) gives the `e5` direction |
| `e54_naive_seed_pool.py` | C2b | is the `naive` arm a free instrument, and how many seeds exist for one computation? | done — **six distinct `naive` computations** across 15 runs, the largest with **n = 9** (sd 0.0389, floor 62% of the variance, so 38% is the learner); agreement established from the data, not an assumed config key |
| `e55_seed_resolution_of_excess.py` | — | is the "below ~0.05 not resolvable" figure still right, at n = 12? | done — **stale by 3× and the wrong shape**: the absolute metric's CV is 0.70–1.26, the same as the relative gap's, so it fixes the *ratio* not the spread; unpaired resolution is **0.0159 at n = 12** (0.0319 at n = 3) but **0.00100** as a within-seed difference, and the same topology's sd moves **11×** with the drive construction |
| `e56_metric_pathology_both_ways.py` | C1 | where does the metric choice decide the answer, and in which direction? | done — **both directions measured**: at cs800/`real` the banned metric **hid** a reversal (prescribed p = 0.065 vs banned 0.77); at cs300/`swap2` it **manufactured** one (prescribed null at 6/4/2, p = 0.754; banned Wilcoxon p = 0.0068, pooled p = 4e-6) and the rank decomposition puts it on the **oracle** (ρ(oracle, flatten) = +0.79, negative oracle coefficient, R² = 0.85) |
| `e57_basis_ladder_seed_robustness.py` | C2 | does the CORE claim survive the per-seed discipline that overturned C1? | done — **yes, by a wider margin**: 7 of 8 pool rungs unanimous over **12/12** seeds, no leave-one-out flip, smallest LOO σ **6.6**, leverage 0.51–0.80. But the per-seed evidence is for the **pool ladder** while the headline is stated on the **named bases**, whose 18-seed artifact stores none — `e58` launched to close it |
| `e59_separation_with_both_components.py` | C1 | every σ here is one of two — how strong is each headline claim about the *rule*? | done — **98%+ of a single point's variance is the wiring draw** (realization sds 0.00377 / 0.00320 against seed sems 0.00025 / 0.00047). ER separation **364.9σ about these graphs, 26.1σ about the rule** (was 152σ); C1 contrast **28.8σ / 2.7σ** (was 32.7σ). The 2.7σ was the *most favourable* reading, computed with `swap0.5`'s realization sd set to zero; `e65` measured it and the answer is **2.2σ** |
| `e3_basis_selection --extra-bases --seeds 18` | C2 | per-seed storage for the named annotation bases (`e58`), the family the headline is stated on | done — `runs/e58_bases_18seeds_perseed.json`, all 15 bases carry `excess_per_seed`. It closes `e57`'s census gap and, through `e66`, **reverses one verdict**: see the `e66` row |
| `e66_named_bases_seed_robustness.py` | C2 | the named annotation rungs under the per-seed discipline, with both σ and the measured draw sds | done — **all five rungs pass**: 5/5 have unanimous per-seed signs (18/18), no leave-one-out removal flips any, smallest LOO σ 19.1, largest leverage 0.61. **And `cell_type` is not a null**: its two arms correlate at ρ = 0.9987, so the unpaired sem is **27× too large** and the published 0.74σ becomes **20.3σ paired, 18/18 positive** — a real *disadvantage* — and **3.8σ about the rule**. Paired rule-σ: 18.1 / 12.1 / 26.1 / 13.3 / 3.8. The spread between best and worst rung narrows from 39× to **1.6×**. The four non-partition extras get their first per-seed check too: `eigbasis` −0.00491 at **26.0σ, 18/18 negative**, and `rank4/16/64` +0.0046–0.0047 at **~30σ, 18/18 positive** — which is §4.4's headline and the "adaptive candidates are worst" claim, both now seed-robust |
| `e8_rate_network --lam 0.1 --repeats 16` | C2b | the properly-powered rung contrast at λ = 0.1 (`e46`), the λ where it appeared to resolve | done — **NULL**: Δ = **+0.0039 ± 0.0161** at n = 16 against the 3-seed **−0.0648**; the first three seeds are the three most negative of sixteen and three more take it from −2.65σ to −0.07σ. Signs 7/2/7, floor 0.032, 19 replicates for 0.03. The 3-seed run's values reproduce bit-for-bit, so the config is identical |
| `e8_rate_network --basis side --lam 0.1 --repeats 16` | C2b | `side` at sixteen replicates (`e60`), to restate the cross-rung contrast | done — **and the cross-rung contrast is a null.** The two runs are the same configuration in 23 of 23 comparable fields (only `basis` differs, by design) and their `naive` arms are **bit-identical over all 16 replicates**, so the seeds are aligned by value rather than assumption. At 16 replicates: `side` −0.0152 ± 0.0128 (**1.19σ**) accuracy and +0.0241 ± 0.0198 (1.22σ) forgetting; `cell_class` +0.0039 ± 0.0161 (0.24σ) and −0.0111 ± 0.0227 (0.49σ). **`side − cell_class` = −0.0191 ± 0.0216 (0.88σ)** accuracy and +0.0352 ± 0.0291 (1.21σ) forgetting, against a published 3-replicate +0.0718 at 2.13σ. Detection floors 0.026 / 0.032 / 0.043: the `cell_class` figure was 2.0× its floor and the cross-rung figure 1.7×, so both were resolvable and both are absent |
| `e76_c2b_cross_rung_powered.py` | C2b | the C2b rung question at sixteen replicates on both rungs | done — `runs/e76_c2b_cross_rung_powered.json`. **The line's last outstanding figure is closed and it is a null**, so C2b now has a well-powered measurement at both rungs and at the contrast between them, all null, with the floor at ~0.03 accuracy. Note the leave-one-out asymmetry: `cell_class`'s accuracy contrast has a **LOO minimum of 0.08σ with a sign flip**, while `side`'s is 0.72σ with none — the rung whose published claim was strongest is the one a single replicate can erase |
| `e8_rate_network --replay-per-task 96 --replay-batch {8,16,48}` | C2b | recreate the missing artifact behind the network line's headline replay result (`e61`) | **complete, and the whole claim reproduces.** Per-step 8: −0.08542 ± 0.01293 = **6.61σ**; 16: −0.06250 ± 0.01545 = **4.05σ**; 48: −0.07083 ± 0.01693 = **4.19σ** — all 5/5 negative. Replay's own forgetting: −0.0125 (3.21σ), +0.0104 (1.58σ), **+0.0021 (0.34σ)**. The **budget inversion** is **`16 − 8` = +0.02292 ± 0.00390 = 5.88σ**, 5/5 positive, LOO σ [4.70, 8.66], no flips, leverage 0.80 — but its fine structure is not resolved: **`48 − 16` = −0.00833 ± 0.00896 = −0.93σ**, so the reproducible content is "8 is best" at 5.88σ, not a three-point curve |
| `e61_replay_recreation.py` | C2b | the recreated sweep against the published claim, with paired per-replicate structure | done, sweep complete — `runs/e61_replay_recreation_analysis.json`; §3 reports the inversion as a **paired** contrast rather than as two means, because the per-step arms share their replicate seeds |
| `e8_rate_network` at the other two settings, pool 96 / per-step 8 | C2b | the task-IL and class-IL replay arms (`e84`) — the two pool-96 numbers `e61` does not cover | **done — the prediction reproduces on both settings, and the third thing it was asked about does not.** *(This row opened with "launched, prediction before the run" long after its body reported the result, because the update was appended to the cell and the opening word was never re-derived — see the finding on the status word.)* task-IL is the default (per-task heads, `--readout-size 0`, **no `--input-overlap`**) and class-IL is `--shared-head` with `--readout-size 0` and no overlap; both at λ = 0.003 / 8 Fisher batches / 5 replicates so they sit beside `e61`'s. Neither has an artifact: a census of the 17 stored artifacts carrying a `naive` arm finds `replay_per_task: 96` in **exactly one**, `e61`'s own step-8 run. **The two arms differ in how far they can be trusted, and the fingerprint is what separates them:** task-IL's claimed naive (+0.101) matches `e10_rung_*`'s **0.8241 / +0.1007** exactly, so a recreation whose naive reproduces that *is* the same computation; class-IL's claimed naive (+0.059 ± 0.028) matches **no** stored artifact — and `e8_class_incremental`'s stored class-IL naive is **0.9361**, half a sem away from nothing in particular — so that arm is a **re-measurement under the best-matching configuration, not a confirmation**, and the run's own naive will say which it is. **Prediction:** task-IL's naive reproduces 0.8241 / +0.1007 to the printed precision; **falsifier:** a naive that does not, which would mean the settled finding's task-IL row was computed under a configuration no stored artifact shares and the recreation is a new measurement rather than a restoration. For class-IL no fingerprint prediction is possible and the honest output is a fresh number with its own detection floor. **RESULT, task-IL: the falsifier fires — it is a re-measurement, not a restoration.** The naive reproduces only to **0.8417 against the stored 0.8241**, with per-seed differences up to 0.063 and *mixed signs* — the signature of a different training trajectory, and the cause is the environment (`OMP_NUM_THREADS=3` here, unrecorded for `e10_rung_*`). That is **rule 21's first practical casualty**: a missing artifact cannot be restored across environments, though the census stays sound within one (`e10_rung_*`'s 3-seed mean 0.8241 is exactly `e54` cluster 0's first-three mean). At n = 5 the re-measurement gives contrast **−0.10417 ± 0.01647 = 6.32σ** on forgetting (`-----`, LOO 4.84) and **+0.09028 ± 0.00761 = 11.87σ** on accuracy (`+++++`, LOO 9.62) — stronger evidence than the claimed 3.1σ, magnitude 34% smaller — while replay's own forgetting is **−0.0042 ± 0.0091 (0.46σ from zero)** against the claimed −0.056 ± 0.009, a **6.3σ disagreement**. So "replay eliminates forgetting in task-IL" holds and "replay drives it 0.056 below zero" does not. **RESULT, class-IL: also a re-measurement (naive 0.9194/+0.0688 against `e8_class_incremental`'s stored 0.9361/+0.0437), and the closest reproduction of a network-line claim in the project** — every one of the claim's four numbers is inside the measurement's interval: naive forgetting +0.0688 against +0.059 ± 0.028, replay forgetting +0.0063 against −0.010, replay accuracy 0.9611 against 0.975, contrast **−0.06250 ± 0.01647 = 3.79σ** (`-----`, LOO 2.84) against −0.069 at 2.2σ. Its accuracy contrast is +0.04167 ± 0.00905 = 4.60σ (`+++++`, LOO 3.48). **A wrinkle**: this arm's recreation is *closer to the claim* than to the stored artifact it is compared with, so the original's configuration is neither — the fingerprint had no valid reference for it, which is why the plan said in advance it could be re-measured but not confirmed. **And one claim the abstract must lose**: it says replay drives forgetting "to zero or below", but in neither setting does replay's own forgetting sit below zero with confidence (−0.0042 ± 0.0091 = 0.46σ for task-IL; +0.0063 ± 0.0150 = 0.42σ *above* zero for class-IL). What reproduces is *driven to zero*, which is the part LGCL's prediction needs |
| `e2_topology_gap.py --topologies swap0.5 --rewire-seed 0..5` | C1 | the `swap0.5` realization sweep (`e65`) — the one component missing from the two-σ decomposition | done — **the C1 contrast is 2.2σ about the rule, not the 2.7σ bound.** `swap0.5`'s realization sd is **0.00269** against `swap2`'s 0.00377, so the two rules have the *same order* of wiring spread (every rule measured is ≈0.003) and the branch `e59` called pessimistic (1.9σ) was the close one. Three readings, all reported: **28.8σ about the two graphs**, **2.2σ** on one redraw of each rule, **3.4σ** comparing rule means (**5.8σ** if each arm's worst draw is dropped). **And the partial reading was wrong out loud**: at four draws the sd was 0.00054 and the bound looked exact; the fifth draw (0.01631) multiplied it by five, which is rule 15 arriving on the *realization* axis |
| `e12_control_spread.py --column {side,cell_type}` | C2 | measure the two draw-sds that the predictor's correction had to *interpolate* (`e67`) | **done, both arms, and the pre-registration is refuted.** The mechanism finding predicted `side`'s draw sd at ~1.0e-3 (concentration 0.498, interpolated between 0.325 and 0.678) and predicted that the 2-draw smoke value 9e-5 would not replicate. Eight draws give **2.16e-4** — 4.8× below the prediction and closer to the value it was written to overrule. The relation is non-monotone: **6.8e-5** → 9.3e-4 → **2.16e-4** → 1.06e-3 as concentration rises 0.020 → 0.325 → 0.498 → 0.678, and the fine point itself moved 1.75× when it went from 2 draws to 8. Consequence: the §5 correction of `side` (15.53σ → 4.47σ) is a 2.8× over-correction — with the measurement it is **12.74σ** — and **all five** named rungs can now be corrected with measurements: **17.5 / 9.0 / 9.3 / 4.1 / 0.73σ**, overstatements **1.0–1.6×**, not 3–6×. The predictor's 13 of 13 is **not** untouched, it turns out: `e64` shows the pairing moves the denominator to 24 and the swap2 failure is a 10.63σ wrong call |
| `e71_variance_share_audit.py` | C2b | audit the "62% of the variance is the learner" figure against the artifact field it comes from | done — **the sentence is inverted in three documents**. `e38`'s `floor_share_of_variance` is **0.619** for the `naive` arm at n = 9, i.e. the *test set's* binomial floor; the learner is 38.1% there and **45.1%** in `e54`'s n = 16 pool (95% interval [0%, 77%]). For the **contrast** — what the axis argument is made on — the floor is 43–46%. Conclusion unchanged: ten times the test set buys **1.41×** and no more, so seeds remain the lever |
| `e72_alignment_draw_spread.py` | C2 | **pre-registered**: which variable predicts the control's draw spread, now that concentration does not? | done — **the prediction is REFUTED and the falsifier it named FIRES**; the result is at the end of this row. `e67` refuted the one-scalar model, and the refutation has a mechanical explanation the scalar cannot express: concentration is invariant under relabelling (a relabelling preserves group sizes exactly), so the only thing a control draw changes is *which* neurons share a group — i.e. how the partition's indicator span sits against the task subspaces. The candidate predictor is therefore the **draw-to-draw spread of a partition's task alignment** (`e3`'s `alignment_of` excess over random subspaces, recomputable per draw with no filter). **Prediction:** over the partitions with both a measured excess draw sd and a computable alignment spread — `side` (2.16e-4), `cell_class` (2.37e-4), hemilineage (4.16e-5), `supertype` (8.35e-5), pooled `cell_type` at min sizes 2/4/32 (9.3e-4, 6.13e-4, 1.06e-3) — the alignment spread ranks the excess spread at Spearman **≥ +0.8**, where concentration is non-monotone (0.325 → 9.3e-4, **0.498 → 2.2e-4**, 0.678 → 1.06e-3). **Falsifier:** `side`'s alignment spread coming out *larger* than pooled-min-2's while its excess spread is 4.3× smaller. **RESULT (nine points, concentration 0.020–0.536):** Spearman(alignment spread, measured sd) = **+0.283, p = 0.46**, against the pre-registered ≥ +0.80; `side`'s alignment spread is 0.371 against pooled-min-2's 0.071 — 5.2× larger — while its excess spread is 4.3× smaller, so **the falsifier fires**. And the failure is **structural**: the candidate is a re-expression of partition size, ρ = **+0.850** with concentration (p = 0.0037) and **−0.904** with indicator-span dimension (p = 0.0008), so it inherits the failure of the scalar it was meant to replace. The mechanism is that `alignment_of` reports `raw / chance` with a *generic* random subspace as the denominator, which strips the free size advantage and, on this measurement, the task information with it. **A refinement of `e67` comes with it**: over nine points concentration itself scores **+0.617 (p = 0.077)** — a weak *global* ordering rather than noise, though not significant at n = 9 and non-monotone exactly in the 0.3–0.7 region the project's claims live in, so what stands is `e67`'s *local* refutation |
| `e75_task_pair_spread.py` | C2 | **pre-registered**: does the control's excess MOVE WITH the partition's alignment? | done — **the fourth candidate fails, and this one had every structural advantage.** The design fixed both flaws `e72` diagnosed: no chance denominator, and co-movement rather than spread, with the task draw held fixed (each correlation is *within a seed*, across draws, after centring by the seed mean). Result: within-partition co-movement **mean ρ +0.130 (mean r +0.170, r² 0.066)**, against a pre-registered ≥ +0.5, and **+0.17 ± 0.24 is not distinguishable from zero**. Spearman(co-movement, measured draw sd) = **+0.150** against a pre-registered ≥ +0.8, while concentration scores **+0.617** — the fourth time a plain partition-size scalar beats a task-relative candidate. **The falsifier fires for 3 of 9 partitions**, including `cell_class` (−0.102) and `side` (−0.096), the two rungs the C2 claims lean on. So the conclusion is substantive rather than another closed door: the draw spread is **not** the relabelled span's geometry against the task's precision subspace |
| `e80_pressure_draw_spread.py` | C2 | **pre-registered**: does the draw-to-draw spread of **`projection_pressure`** predict the draw-to-draw spread of the control's excess? | done — **the first candidate in five that works, and it is not a size scalar.** The **absolute** pressure spread ranks the measured draw spread at **+0.767 (p = 0.016)** over nine partitions spanning concentration 0.020–0.536, and is only **+0.317** with concentration and −0.433 with the pressure level. Neither form satisfies both pre-registered clauses and *how the other one fails is the diagnostic*: the **relative** form hits the target exactly (+0.850, p = 0.004) but scores +0.767 with concentration, because **the pressure level is itself −0.983 with concentration** — so dividing by the level manufactures the size correlation, the mirror image of `e72`, where dividing by a random subspace collapsed the quantity onto span size. The falsifier (concentration ≥ +0.85) fires for neither form. **Mechanistically this is a real advance**: the four failures all used the task's *subspace* (which directions the drive occupies); pressure uses the task's *information* `J_k` (how strongly each direction is measured), and the draw spread turns out to be about the latter. Limits: n = 9 and four candidate families tested on the same targets, so the nominal p is not a discovery on its own; the two forms are ±0.083 apart on the target and the preference for the absolute one rests on its *diagnosed* independence; and the targets themselves carry 20–50% error (3–8 draws each). `per_draw_seed` is kept in the artifact so the co-movement question can be asked of the pressure without recomputing the filter |
| `e81_pressure_comovement.py` | C2 | **pre-registered**: does `projection_pressure` CO-MOVE with the control's excess, within a seed? | done — **the pre-registration passes on every clause and this is the mechanism.** Mean within-seed co-movement **+0.906** (predicted ≥ +0.5) and mean ***r*² 0.828** (predicted ≥ 0.25), against the bare alignment's **+0.170** from `e75`; the falsifier does not fire and **0 of 9 partitions have a non-positive co-movement**. The decisive row is the **paired** one, because it is the same design twice — same nine partitions, six relabellings, three seeds, same within-seed centring, only the quantity differs: **pressure − alignment = +0.736 ± 0.061, 9 of 9 positive, sign p = 0.0039**. So the control's excess moves across relabellings because the **precision-weighted projected deficit** moves (83% of the variance) and barely at all because the subspace geometry does (6.6%) — which retro-explains all four failures, since every one of them was a subspace overlap and none could see `J_k`. **Two things it does not say, both measured**: the per-partition co-movement does **not** rank the draw spreads (Spearman **+0.067**), so `e81` *explains* the variation while `e80` *calibrates* it and neither implies the other; and `side` is the weakest partition at +0.681 (*r*² 0.464) — the honest form is "83% on average, 46% for the one partition whose σ the paper leans on" |
| `e81_pressure_comovement.py --circuit-size {300,1500}` | C2 | **pre-registered**: does the mechanism replicate at two other circuit sizes? (`e82`) | done, **three sizes and the mechanism is not size-invariant.** At cs = 300 (d = 952): mean *r* **+0.923**, *r*² 0.854. At d = 1307: +0.906 / 0.828. At cs = 1500 (d = 1874): **+0.810 / 0.676**. **All 81 seed-level correlations across the three sizes are positive** (smallest +0.368) and the bare alignment's +0.170 is beaten everywhere by 4.8× in *r*². **Paired: d = 1307 − d = 952 is −0.0166 ± 0.0198 (0.84σ, p = 1.0000) — a null — and d = 1874 − d = 1307 is −0.0962 with signs `+--------`.** **BUT THE SECOND IS NOT RESOLVED** (`e87`): the nine partitions share their six relabellings, so a sem over the nine treats correlated numbers as independent. Resampling the **draws** gives **4.0× the sem** and an interval that spans zero — −0.0962 [−0.3110, +0.1468] = **0.75σ**, with 80.5% of resamples below zero — and the same correction takes the first comparison from 0.84σ to 0.45σ. So the apparent decay is a **point estimate, not a measurement**, and the eight-of-nine sign record — which is exactly what a shared-draw effect produces — was never independent evidence. The mechanism's strength at the largest size is 0.810 against 0.906 and any future design should assume the difference may be real, but it is not established here. Per partition, what decays is `side` (0.681 → **0.418**, the only *r*² below 0.5 at any size and a monotone decline across three) and `ito_lee_hemilineage` (0.980 → 0.771), while the four `cell_type` poolings, `supertype` and `cell_class` stay at 0.83–0.90. **Two untested explanations, separable by one cheap run:** either the decay is a property of the *design* (a Frobenius aggregate over three tasks samples a smaller fraction of the perturbation space at larger d, so more draws would restore *r*), or of the *quantity* (the excess picks up contributions pressure does not represent, so it would not). Also recorded: at cs = 300 `cell_type` min 4 and min 6 are the **same partition**, so there are eight distinct and not nine — the same crowding `e3` found at d = 1307. **And the *spread* statistic is not replicated at all**: `e80`'s +0.767 needs the nine measured draw sds, which are d = 1307 numbers, so the script refuses to print it away from d = 1307 |
| `e12_control_spread.py` × 9 partitions × cs = {300, 1500} | C2 | the measured draw sds at the two other circuit sizes (`e86`) — the target `e80`'s spread statistic never had away from d = 1307 | **done — the clause passes at two of the three sizes.** *(This row opened with "launched, prediction before the run" while its own body, thirty lines into the same cell, reported the completed verdict — the status word was never re-derived when the completion was written.)* `e80`'s is the half of the mechanism that matters for a *predictor*: the co-movement says pressure and the excess move together, the spread statistic says the **size** of pressure's own variation calibrates the **size** of the control's — and `e82` already stores the pressure spreads at both sizes, so the only missing piece is the target. Eighteen runs at `e14`/`e74`'s protocol (3 task seeds, 5 draws) so the new points sit beside the old ones; ~2 h. **Prediction:** at each new size the absolute pressure spread outranks the measured draw spread at **Spearman ≥ +0.7** *and* beats concentration on the same nine partitions. **Falsifier:** it failing to beat concentration at either size — a live risk, since at d = 1307 the margin was only **+0.767 against +0.617** on nine points, and the target itself carries 20–50% error at five draws. **RESULT at d = 952: the falsifier FIRES.** The absolute pressure spread scores **+0.412 (p = 0.27)**, below the pre-registered +0.70 and well below concentration's **+0.832 (p = 0.005)** — so the ordering `e80` found **reverses** at a second circuit size. The form that does score well there, the relative spread at +0.882, correlates **+0.950 with concentration**, i.e. a size restatement — **and that inference was itself overstated**: with concentration rank-partialled out the relative form keeps **+0.531** at d = 952, above the absolute form's +0.509, though on a rank residual with almost no variance left (ρ = +0.950 with the confound, and +1.000 at d = 1874), so it is the fragile-denominator situation `e72` was diagnosed with. What the nine points support is the weaker "not distinguishable from concentration, raw or partial"; the instrument that settles it is `e92`'s grid; that is the same failure mode `e80` diagnosed at d = 1307 when the relative form hit +0.767 with concentration. So `e80`'s headline was a **d = 1307 event**, and the second size *contradicts* it rather than merely failing to confirm. **d = 1874's targets are now all nine, and the clause PASSES there too**: the absolute pressure spread gives **+0.800 against concentration's +0.483** (p = 0.010 against 0.187), clearing +0.70 AND beating concentration — the same two clauses d = 1307 passes and d = 952 fails. **So the verdict is 2–1, not the 1–1 split this row predicted**, and the single failure is the size whose nine are bimodal with two byte-identical rows. The overlap restriction, which the corrected range now allows at two sizes, resolves nothing: it is **vacuous** at d = 1874 (that size's own range *is* the common range, since `side` sits at 0.498 at all three sizes), a **four-point tie** at d = 1307 (+0.400 against +0.400), and uncomputable at d = 952 (2 of 9 rows). Partials, given concentration: **+0.765 (d = 1307, p = 0.027)**, **+0.779 (d = 1874, p = 0.023)**, +0.509 (d = 952, p = 0.197). The last cell (`supertype`, 639 groups) took ~1,000 s against ~690 s for the rest. **AND THE TEST ITSELF IS NOT WELL-POSED** (`docs/findings/2026-09-23-the-cross-size-test-is-not-well-posed.md`): the nine labels are the same and the **partitions are not** — the concentration ranges of the nine are **0.006–0.754 at d = 952, 0.020–0.536 at d = 1307, 0.034–0.498 at d = 1874** — **corrected from 0.034–0.324, which was read off the pressure artifact while it held five of the nine rows at that size**, and whose real maximum is set by `side` at 0.498; `side` is in fact a **fixed point** of the whole design (0.4981/0.4985/0.4984 at the three sizes), and the common range 0.034–0.498 holds **2/4/9** of the nine rows, so the overlap cannot be computed at d = 952, the size whose reversal is in question (rule 17's second shape), so the "replication" compares a set with four partitions beyond 0.69 against a set whose coarsest is 0.536, and the overlap of all three ranges holds enough rows at only one size. **Why d = 952 fires is then visible**: its nine are **bimodal** — four rows at 0.690–0.754 with measured sds 2.96–3.54e-3 (and `cell_type` min 4 ≡ min 6 there are the *same run*, byte-identical rows) against five at 0.006–0.159 with 0.9e-4–1.2e-3 — and **restricted to the fine end (conc < 0.6, n = 5) all three candidates tie at +0.900**. So the reversal is a bimodal design in which four near-duplicate coarse rows occupy four of the nine ranks at the top of both orderings, which concentration captures by construction and which carries almost no discriminating information. **The standing position: one complete size in the spread statistic's favour (d = 1307, where it was found), one complete size against (d = 952), and neither test is over the same partitions as the other.** The design that would test it properly is pre-registered in the finding: **choose partitions by concentration, not by label, and use the same concentration grid at every size** — which also removes the bimodality, since binning forces the coarse end to be sampled at several levels |
| `e92_grid_profiles.py` × 20 cells × cs = {300, 800, 1500} | C2 | **pre-registered**: the spread statistic on a grid whose cells are **group-size profiles**, chosen by concentration rather than by annotation label, so that "cell *i*" names the same region of partition space at every circuit size (`e92`) | **launched, prediction before the run** (`docs/findings/2026-09-23-the-concentration-matched-grid-preregistered.md`). The design turns on one observation that makes the fix both exact and cheap: **both halves of the measurement depend on the partition only through its group-size multiset** — `e80`'s pressure is evaluated on `random_partition(labels, rng)`, a size-matched relabelling, and `e12`'s target is the draw spread of that same size-matched control — so a profile is a legitimate object and concentration can be *set* rather than *found*. `flat` profiles have concentration exactly `1/k` at every circuit size and are therefore matched exactly; `harmonic` ones add a skew at the same `k`, so two cells at one concentration that disagree measure what concentration does not determine. Group counts `k` ∈ {2, 3, 5, 8, 13, 21, 34, 55, 96, 160} × shapes {flat, harmonic} = 20 cells per size × 3 sizes, at `e14`/`e74`'s protocol (3 seeds, 5 relabellings), one artifact per cell so the grid is resumable. **The statistic is the PARTIAL Spearman of the pressure spread against the measured draw spread, concentration partialled out of both ranks** — a raw rank correlation cannot separate "pressure predicts the draw spread" from "both grow with concentration", which is the confound `e86` could not remove. **Predictions:** partial positive at all three sizes; the raw pressure correlation above concentration's own at every size on the same twenty cells; partial ≥ +0.5 at d = 1307 (where the raw margin was +0.767 against +0.617); ≥ 7 of 9 per-seed partials positive. **Falsifier that matters: the partial at or below zero at two or more sizes** — then the pressure spread's ranking power is a concentration restatement everywhere and §4.3's predictor claim fails as stated. Cost measured: ≈ 24 / 44 / 93 minutes per size, **≈ 2.7 h total**. **DONE — all three sizes complete at 20 of 20, and the clause passes at all of them.** Verdict: **P1 PASS** (+0.919, +0.618, +0.872), **P2 FAIL** (at d = 1307 raw concentration beats raw spread, +0.923 against +0.582), **P3 PASS**, **P4 PASS (9 of 9 per-seed partials positive)** — against a predicted 7 of 9 — **P5 PASS** (median level 6.18x against median target 0.24x, 20 of 20 cells), **P6 FAILED with its falsifier firing**, **P7 PASS**, F1 does not fire, F2 does. Every size has no leave-one-cell-out flip and a profile bootstrap above zero (0.00%, 0.20%, 0.00% at or below zero). **AND THE 'DECLINING TREND' THIS ROW RECORDED WAS THE SUBSET TALKING**: the 8-of-20 row that read +0.120 is **+0.872** when complete, so the apparent trend was a partial set, and the real shape is a **dip at d = 1307** — 952->1307 is -0.301 [-0.645, -0.015] (98.15% at or below zero), 952->1874 is -0.048 [-0.253, +0.138] (unresolved), 1307->1874 is +0.254 [-0.021, +0.581] (nearly resolved POSITIVE) — and the dip tracks the coupling (+0.923 at d = 1307 against +0.677 and +0.571): the statistic is weakest where the confound it removes is strongest. §4.3's sentence is rewritten against the completed table. The earlier state of this cell was: 59 of 60 cells, the sixtieth re-measured after a TIMEOUT KILLED IT. cs = 300 and cs = 800 are both complete at 20 of 20 and cs = 1500 has 19, so the only missing cell is `cs1500/harmonic/k160` — the last one the loop reached. **The sweep ran all sixty cells as one background task behind a four-hour timeout and was killed on the sixtieth**, which is a design fault rather than bad luck: a single `for` loop means the timeout kills the *loop*, and the per-cell artifacts made recovery possible only by enumerating which files were missing and re-running that one by hand. **`e92_grid_profiles` now skips a cell whose artifact exists unless `--overwrite` is passed**, so the same loop is resumable and costs only what the timeout ate — the guard its absence paid for. Its earlier state was 48 of 60: cs = 1500 at 8, `flat` only). **cs = 300 is COMPLETE at 20 of 20** and it is the round's result, recorded in `docs/findings/2026-09-23-the-grid-at-one-size-is-whole.md`: at d = 952 — **the one size `e86`'s raw test failed at** — the absolute spread gives **+0.908 raw against concentration's +0.677** and **+0.919 with the confounder partialled out (p = 2.7e-08)**, 3 of 3 per-seed partials positive, leave-one-cell-out **+0.896..+0.951 with no sign flip**, and a 4000-resample profile bootstrap of **+0.892 [+0.718, +0.977] with 0.00% at or below zero**. So the d = 952 failure was the nine's bimodal design and not the statistic, which `e86` could state only as a suspicion. **And the second shape earns its place**: `flat` alone leaves the coupling at +0.891 and the partial at +0.590, `harmonic` alone +0.782 / +0.715, and **together +0.677 / +0.919** — complementary, not redundant. A joint log fit adds that **shape carries information concentration does not** on all three dependent variables (F = 121 / 82 / 153, p < 1e-4), and on the target **shape alone explains 78% against concentration's 50%**, refuting the one-scalar model a second way. **New clause P6** pre-registered at this point: d = 1307's nine cells are all `flat`, coupling **+0.983**, partial +0.654 with **25% of bootstraps at or below zero** — unreadable, and the predicted consequence of the missing shape; P6 says the harmonic cells will drop the coupling below +0.80 and lift the partial above +0.654, and its falsifier is the coupling staying above +0.90. **The report's verdict block now prints PENDING rather than FAIL for clauses scoped to "every size" while a size is unscored**, which it was getting wrong. **AND THE TWO COMPLETE SIZES NOW CARRY A PAIRED TEST**, which the earlier form of this row did not have: since the twenty profiles are the same objects at every size, the cross-size comparison is paired on the profile and the interval must be too. d = 952 -> d = 1307 is **-0.301 with a paired bootstrap of [-0.638, -0.006] (97.75% at or below zero) for the absolute form and [-0.779, +0.044] (96.10%) for the relative one** -- so the decline is resolved by a hair for one form and not for the other, and the two forms disagree for the third time in this thread. The remaining 12 cells are all cs = 1500 (2 `flat`, 10 `harmonic`) at ~5 min each. |
| `e94_predictor_denominators.py` × 3 conditions × 5 rungs, cs = 300 | C2 | the predictor's three remaining **borrowed** denominators, measured (`e94`) | **done — the count moves and the borrowing was optimistic.** `e93` found that `e64`'s count gave **20 of 25 pairs a d = 1307 draw sd while those pairs ran at cs = 300**, because `DRAW_SD_SOURCES` is keyed by rung and not by circuit size. `e86` repaired one of the four conditions (`baseline`) with no change to the count; the other three could not be repaired because **no artifact had their configuration** — `wider-tasks` needs support 60, `faster-drift` needs q 0.10, `rewired-swap2` needs `swap2`, and `e12_control_spread.py` had no topology option at all, so it gains one (opt-in, default `real`, so every earlier artifact keeps its meaning; `e6_predictor.py`'s `default_rng(seed0)` is matched). Only the predictor's own five rungs are measured — `e86` also ran `cell_type` min 2/3/4/6, which `e64`'s pairs do not contain — at `e86`'s protocol (3 seeds, 5 relabellings). Report: **21 of 25 with the borrowed denominators against 20 of 25 and 19 of 20 called correctly with all twenty measured** — the correction moves both numbers toward less support, and the one pair that changes verdict is `rewired-swap2`/`cell_type` (2.32 → 0.87, called right). **The twenty ratios between measured and borrowed denominators are all above 1, 1.09 to 6.73 with median 2.33**, so the borrowing was systematically **optimistic** rather than noisy: a relabelling perturbs a larger share of a smaller circuit, so the draw spread is larger at cs = 300 for the same rung in every case, and the sign of the bias was predictable from that rather than needing to be discovered. Note also that the *largest* σ corrections change no verdict (`faster-drift`/`cell_class` 11.79 → 5.05, `wider-tasks`/`cell_class` 13.47 → 6.46); the count moves because of a pair that was **near** the 2σ line, which is why a count is a poor summary of a distribution of σ. A pair whose measurement was absent was counted **PENDING**, not as failing 2σ, since counting a missing denominator as a failure would move the count in the direction of the hypothesis under test. Caveat carried from `e93`: `e86` and `e94` use 3 task seeds where `e64` used 6, so each measured across-draw sd carries slightly more seed noise and is biased high, making every σ reduction a conservative upper bound. |
| `e8_rate_network.py --circuit-size 300` with `e8_hardened_basis`'s config | C2b | **pre-registered**: the reversed-ordering question at a smaller circuit (`e99`) | **done — all three predictions hold, the falsifier did not fire, and two unanticipated results.** **All three write-ups are in the plan for the record:** the block-minus-diagonal gap falls from **+0.0396 to +0.0167 (58%)**, the direction the estimation-quality account predicts, which is **the first evidence the project has *for* that account rather than against it** — and it is weak, because the gap is 0.39σ. The arms are individually noisier at cs = 300 (forgetting sems 0.0362/0.0432 against 0.0255/0.0250), so the σ fell because the numerator fell faster than the denominator rose. **Two unanticipated results**: the **diagonal's advantage over `naive` disappears at the smaller circuit** (**2.47σ → 0.25σ**), which is a size dependence in the network line's *baseline* result that the paper does not state; and **`replay` is best on both metrics at cs = 300** (0.9389 / +0.0458), so the network line's only resolved positive result **replicates at a second circuit size**, which it had not been asked to do. Net: the item is **resolved in direction and unresolved in size**, and its remaining route is the lower-rank task family §8 also names — cheaper than a third circuit because it changes the suite rather than the substrate (`docs/findings/2026-09-23-the-reversed-ordering-question-at-a-smaller-circuit.md`). The earlier state of this cell was: launched, prediction before the run, with the cs = 800 contrasts 0.65σ and 1.59σ. §8's item 2 has asked since the first network run whether a configuration exists in which the block Fisher's structure *is* well estimated — *"a smaller circuit, or a lower-rank task family"* — and **every rate-network artifact in this repository is at cs = 800** (all 25 of them), so it never has. At cs = 800 with 32 Fisher batches the block is **+0.0604 ± 0.0201** against its matched random's **+0.0438 ± 0.0156** (0.65σ) and against the diagonal's **+0.0208 ± 0.0147** (1.46σ) — neither resolves. `e99` changes `--circuit-size 300` and **nothing else**, field for field, so the contrast is a circuit-size change at fixed everything: at d = 952 the block Fisher has far fewer entries to estimate from the same 32 batches. **P1** the negative replicates; **P2** the block-minus-diagonal gap is *smaller* in magnitude than +0.0396, because a better-estimated refinement should behave more like the thing it refines; **P3** it is still unresolved, since the `naive` per-repeat sd is 0.048 and five replicates give a sem near 0.02. **Falsifier, and the informative direction: the gap is LARGER at cs = 300.** That would say a better-estimated block Fisher is *worse*, which is evidence against estimation quality being the limit and for the reverse ordering being real — the reading §4.7 currently calls unresolved. Cannot settle: one size is one point, and the honest figure of merit is the `naive` arm's own per-repeat sd rather than the sem, which shrinks while the per-observation spread does not |
| `e8_rate_network.py --classes 2` with `e8_hardened_basis`'s config | C2b | **pre-registered**: the reversed-ordering question with a lower-rank task family (`e100`) — §8's item 2 names **two** routes and this is the second | **done — all four predictions hold and P4's discriminator favours the account twice.** Block minus matched random is **+0.0042** (0.27σ, same direction); **block minus diagonal falls from +0.0396 to +0.0021, a 95% reduction**, against the circuit route's 58%; it is 0.14σ, so nothing resolves. **P4: both routes shrink the gap, by 58% and by 95%, via two different mechanisms** with the circuit, partition, entry count and batch count held fixed in one of them — so the estimation-noise account now has **two independent confirmations in direction**, and the gap orders as it wants across all three configurations (largest where the estimation problem is hardest, nearly zero where the target is simplest). **A third result the pre-registration did not ask for**: `naive` minus diagonal is **+0.0521 at 2.47σ** in the baseline configuration, **+0.0104 at 0.25σ** at cs = 300 and **−0.0063 at 0.46σ** at 2 classes — so §4.7's "2.6σ advantage" over naive at λ = 0.003 is real in **one of three** configurations and the paper stated it as if it were the λ = 0.003 result. **The strongest competing explanation, recorded because nothing addresses it**: `--classes 2` also makes the benchmark *easier* (naive's forgetting +0.0729 → +0.0167, every arm's accuracy ~0.97), and "an easier benchmark compresses all the gaps" predicts exactly what was observed. Earlier state: launched, prediction before the run (`docs/findings/2026-09-23-the-lower-rank-task-family-preregistered.md`, `docs/findings/2026-09-23-the-lower-rank-task-family.md`). `e99` changed the *circuit*, so the block Fisher had **fewer entries to estimate** from the same 32 batches; `e100` changes the *task family* — `--classes 2` makes each task a 2-way discrimination where the configuration has been 4-way, so the readout's discriminating rank per task falls from 3 to 1 — with the circuit, the partition, the number of block entries and the Fisher batch count **all unchanged**. So it tests the account by making the **target** lower-rank rather than the **estimate** cheaper, and the two mechanisms can come apart, which is why both are run. Same prediction: the block is **+0.0396 ± 0.0250** worse than the diagonal at 4 classes (1.59σ), and the estimation-noise account says a lower-rank family puts less penalty mass in the off-diagonals whose noise hurts, so **P2: the gap shrinks**. **P1** the negative replicates; **P3** still unresolved (the `naive` per-repeat sd is 0.048, so 0.04 is within one replicate's spread). **P4 is the discriminator: if the account is right, BOTH routes shrink the gap; if one shrinks and one grows, the account is incomplete** — a negative result about it that a single route could not have produced. **Falsifier: the gap is larger at 2 classes.** Cannot settle: `--classes 2` also makes the benchmark *easier*, which is a confound the contrast survives but one configuration cannot exclude, and the matched-random control moves with the block and not with the classes, so the block-minus-random and block-minus-diagonal contrasts carry different weights and are separate clauses |
| `e8_rate_network.py --fisher-batches {8,128}` with `e8_hardened_basis`'s config | C2b | **pre-registered**: the batch-count discriminator — a manipulation that fixes the forgetting level **exactly** (`e101`) | **done — P1 REFUTED, the falsifier fires, and the account is refuted on the ONE axis that isolates its mechanism.** **P2 half holds and the failing half is informative**: `naive` is **identical to six decimals** at 8, 32 and 128 batches, so the level is provably fixed as the design requires — but **`replay` is NOT identical** (+0.0333 in both new runs against **+0.0500 at the old 32-batch point**), and `replay` consults no Fisher matrix, so that run came from a **different environment**: **only the 8-vs-128 pair is fully controlled**. **CORRECTION (2026-09-23, `e102`): this diagnosis is inverted.** `e101_rate_fb32`'s command re-run today reproduces `e8_hardened_basis` on **280 of 280 numeric fields** 13 h and five commits later (`replay` included), while **two runs of the 8-batch command an hour apart agree on `naive` and `ewc` and disagree on `ewc-block` (0.0167 vs 0.0229), `ewc-block-rand` (0.0521 vs 0.0396) and `replay` (0.0333 vs 0.0500)** — so **the 32-batch point is the reproducible one and the 8-batch point is not**. And `--methods naive,replay`, the arm set with **no Fisher in it at all**, gives `replay` the *same* 15 numbers at 8 batches as at 32, so the batch count is not what moved it: `replay` is **process-dependent, not manipulation-dependent**, and the environment-detector role is withdrawn while the level control survives. Which arms reproduce is a **configuration-specific fact** to be measured, not inferred (`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`). On the 8-vs-128 pair the block-minus-matched-random gap is **negative at both ends** (−0.0354 at 8, −0.0167 at 128 — the block *beats* its control) with the flagged middle point the only positive one, so **the gap's sign is not stable and P1's monotone direction appears nowhere**. **This re-reads `e99` and `e100`**: their 58% and 95% reductions are **coincidences of configuration**, not confirmations of a mechanism, because the one manipulation that changes estimation quality *alone* says no — two axes moved the gap and one did not, and the one that did not is the one the account is about. **Two results neither predicted**: the biological block **beats `naive` by 2.48σ at 8 batches and 3.12σ at 128**, and at 128 it is the **best arm in the table on both metrics** (+0.0104 forgetting against naive's +0.0729; accuracy **0.950**), a positive transfer result §4.7 did not carry — **WITHDRAWN the same day: the size-matched *random* control beats `naive` by −2.60σ at the same batch count (0.9431 accuracy), so this is a granularity result and not a biological one, and the block's own value at 8 batches moves by 0.006 between two runs of one command** (`docs/findings/2026-09-23-the-positive-transfer-result-was-not-one.md`); and `naive` − diagonal is the **most stable contrast in the network line** (+0.0458, +0.0521, +0.0479, all 2.3–2.5σ) *because* its comparator is the bit-identical arm. Earlier state: launched, prediction before the run (`docs/findings/2026-09-23-the-batch-count-discriminator-preregistered.md`, `docs/findings/2026-09-23-the-batch-count-discriminator.md`). The expensive control asked for by the previous fire varies *difficulty* and hopes the level and the mechanism move apart; **`--fisher-batches` separates them by construction**, because `naive` and `replay` consult no Fisher matrix and are therefore **bit-identical** across the sweep while the three Fisher arms move — verified from `e96`'s existing sweep, where `naive` is **+0.1354** at 8, 32 and 128 batches to four decimals. So any change in the block's standing under this manipulation **cannot be a level effect**. **P1 (primary):** the block-minus-**matched-random** gap shrinks as batches rise, **block − rand(8) > block − rand(32) > block − rand(128)** — the symmetric contrast, because the matched random control is the same partition shape and sees the same batch count, so penalty-strength changes cancel. **P2 (built-in control, checked first):** `naive` and `replay` are identical to four decimals across the three runs; **if they are not, the run is reported as void rather than as a result.** **P3:** block-minus-diagonal is reported as *secondary and not used to decide H1*, because raising the batch count strengthens the diagonal's penalty at fixed λ — `e96` measured its forgetting rising +0.052 → +0.083 → +0.146 — so both arms worsen together. **Falsifier: the block − rand gap does NOT shrink with the batch count while `naive` stays identical** — a positive disconfirmation of the account on the axis built to test it, with no level explanation available. The single-seed version on disk is undecided (+0.1250, +0.0625, +0.0833 for block − rand, against a per-repeat sd of 0.019–0.084), which is why two replicated runs supply the test. Cannot settle: three points on one axis is one axis, the batch count changes penalty strength as well as estimation quality, and five replicates resolve only ~0.06 between two gaps |
| `e8_rate_network.py --fisher-batches {8,32,128}` at `e8_hardened_basis`'s config, plus `--methods naive,replay` controls | C2b | **reproduction run for `e101`, registered after the fact as a measurement**: which arms of the network benchmark reproduce, and whether a Fisher-free arm can act as an environment detector (`e102`) | **done — the previous fire's environment diagnosis is INVERTED, and five of seven runs reproduce exactly.** Re-running `e8_hardened_basis`'s command reproduces it on **280 of 280 numeric fields** 13 h and five commits later, `replay` included, so the 32-batch point is **not** an artifact of an older environment — its config does date its code epoch (no `--replay-batch`, added 09-22 11:48; has `--frozen-body`, added 10:18), and that epoch is numerically inert, because **a code epoch is not an environment**. The sweep was then run out to **seven executions**: **`naive` is bit-identical in all seven**; **`ewc` is identical within every batch count** (0.0271 / 0.0208 / 0.0250); and **`ewc-block`, `ewc-block-rand` and `replay` are not** — five of the seven executions reproduce exactly against their partner on every arm and every replicate, and **the two that do not are `e101`'s own 8- and 128-batch runs, and only those two**. So **the two runs the previous fire declared fully controlled are the two that fail to reproduce, and the point it flagged is the one with two exact reproductions.** And the flag's premise is refuted at its root: `--methods naive,replay`, the arm set with no Fisher in it at all, gives `replay` the **same 15 numbers at 8 batches as at 32**, so the batch count is not what moved it and `replay` is **process-dependent rather than manipulation-dependent** — the environment-detector role is withdrawn while the level control survives, and **which arms reproduce is a configuration-specific fact to be measured rather than inferred from the code's data flow**. The clause `e101` decides survives with its status restated: the block-minus-matched-random gap is **reproducible in sign at every batch count and not in magnitude** (−0.0354, −0.0167, −0.0167 at 8; +0.0167, +0.0167 at 32; −0.0167, −0.0062 at 128), so the sign function **−, +, −** is reproducible while the magnitude moves by up to **0.021** between runs of one command against a within-run paired sem of 0.022 — the sign change (0.033) is larger than the run-to-run movement, so **P1's monotone direction appears nowhere and the account stays refuted on the one axis that isolates it**. Also corrected: the block-minus-control σ was quoted from the **unpaired** sem (1.44σ) where the runner's stored `matched_pair` uses the **paired** one (**1.63σ**) and the two arms share a seed sequence. Cannot settle: seven runs identify *that* an arm is process-dependent, not *which* environment variable carries it |
| `e103_reproducibility_audit.py` | programme-wide (C2b and every line that writes a `config`) | **infrastructure, registered after the fact**: the two checks this session was taught by hand — per-arm reproduction for every repeated configuration, and each artifact's code epoch from its `config` keyset (`e103`) | **done — and the corpus number is the finding.** Of **204** artifacts under `runs/` carrying a `config`, **38** are run artifacts; they hold **35 distinct configurations**, and **2 of the 35 have ever been executed more than once — both in this session**, so before it **none of thirty-three configurations had a second execution**, which is the concrete reason this week's reproducibility claims were prose: `e101` inferred an environment difference from a single pair of values because a second execution of the same configuration was not something the record contained. Where a second execution now exists, the per-arm answer is identical at both batch counts: **`naive` and `ewc` reproduce exactly; `ewc-block`, `ewc-block-rand` and `replay` do not** (movement 0.0062–0.0208 forgetting). The epoch check reports **5** rows, all in the rate-network family, and it **agrees with a value-based audit that used a different mechanism**: `e8_fisher_batches.json` — the artifact the paper's §4.7 table was attributed to — lacks `shared_head`, `readout_size`, `frozen_body`, `classes`, `input_overlap`, `noise` and `support`, i.e. it predates the 09-22 10:18 commit whose subject is that the benchmark had been measuring its decoder, which matches the earlier finding that its stored rows are replicate #0 of a run whose numbers match no cell of the sweep. **Both first drafts of the epoch check shipped wrong and are recorded in the finding**: key-overlap families reported **50** rows of noise, and the second dated *aggregate* artifacts (its `config` has three keys and is a hand-built summary), so the shipped version asks only what it can answer — run artifacts within a family of at least three. 14 unit tests, built from synthetic payloads because `runs/` is gitignored. Cannot settle: it dates an artifact against the newest of its own family on disk rather than against the current parser (that needs a runner→parser registry this project does not have), and it reports an unreproducible arm only *after* a second run exists, so it could not have raised the question any earlier than the second run finished |
| corpus search, three shapes (arm, row, column) | C2b and the paper's summary tables | **audit, registered after the fact**: every number in §4.2's and §4.4's tables searched against every arm of all 204 artifacts, in three shapes — does an arm contain this value; do all cells of one row come from one run; is a column's comparator one number | **done — three findings, and the biggest is upstream of the tables.** **(1) The `--frozen-body` control is in NO artifact**: 0 of 204 files have `frozen_body: true`, a `frozen` arm, or a frozen-body result in the payload, and `e8f` — the very commit that added the flag (09-22 10:18) — declares `runs/e8_hardened.json`, which has no frozen row. So §4.2's plastic-minus-frozen series (+0.007 → +0.009 → +0.102 accuracy gap against +0.021 → +0.035 → +0.066 forgetting) and §7's imperative design rule ("a benchmark whose frozen-body control matches its trained accuracy contains no CL problem") rest on a measurement that was printed and not saved; the principle may be right and the record does not test it. **(2) §4.4's table: three of nine cells are backed and all three are `replay` cells** — `e62` and `e84` re-measured replay three times while the `naive` and EWC columns beside it never were. Every cell of the EWC column matches nothing: the hardened cell (+0.010 ± 0.010) is **below all 17 diagonal arms on disk** (minimum +0.0208), and its `naive` (+0.066 ± 0.019) is matched by no artifact where **seven** artifacts of that configuration agree on +0.0729 ± 0.0151. The sentence "replay beats EWC wherever both work — 4.2σ against 2.6σ" was computed against a `naive` no run contains, while §1 prints the same contrast correctly as −0.0854 = 6.6σ: the 4.2σ is `e62`'s pre-recreation figure and the run launched to replace it went into §1 and not into the table. **(3) §4.2's "vs naive" column has two baselines in it** — +0.0729 for the two block rows and +0.066 for the EWC and replay rows — so of its four contrasts two are right and two are against a phantom, and the internal inconsistency is the only tell a single-cell check cannot see. Paper corrected: both tables rebuilt artifact-backed, the diagonal's 2.6σ/2.47σ disagreement resolved to one measurement, the frozen-body series flagged in place, and the two EWC cells in §4.4's upper rows **left empty** rather than filled, because "EWC does nothing where the body is not load-bearing" is now established for one setting and asserted for two. Registered as the next infrastructure step: a cell-level table audit, since transcribing tables faithfully should be done once in code and reviewed. Cannot settle: whether the four phantom cells were runs that were overwritten or runs that never happened — `2026-09-22-network-line-settled.md` declares no `Artifacts:` line at all (`docs/findings/2026-09-23-the-frozen-body-control-is-in-no-artifact.md`) |
| `e105_table_audit.py` | programme-wide (the paper's tables) | **infrastructure, registered in advance by the previous fire**: rule 28's three checks, mechanised — a contrast column against the comparator its header names, an inline contrast against its own row, and a location listing (`e105`) | **done — and both arithmetic checks now PASS on the repaired tables, with the positive control built in as a test rather than asserted.** Check (a) covers the **1** table with a `vs` column (§4.2) and reports **CLOSES** on all four rows; check (b) covers **4** inline contrasts (§4.4 and neighbours) with **0 failing**; check (c) locates and cannot convict, which is stated in the output rather than hidden — of **18** tables, **2** have every number located, **6** none, **10** mixed, and the highest-located mixed table is §4.2's own at 75% where the unmatched tokens are its **four σ values and four contrasts**, i.e. the derived quantities a table should contain. The positive control is a test that constructs §4.2 as it stood (one row closing against the printed `naive`, one whose contrast came from a baseline in no column of its own table) and asserts the second is reported with its expected difference; and **the denominator is printed** (`0 of 4`, not `0`) because a count of zero is otherwise indistinguishable from a check that never fired — the same defect `e97`'s own positive-control paragraph records. Cannot settle: a table with neither a contrast column nor an inline contrast is audited only by the location listing, which cannot convict — filling those cells with measurements (`e104`) is the repair, and the tool's job is only to stop the next one being invisible; and it reads the *paper*, so the source findings' own tables are still unbacked and uncounted. **Extended the same fire**: `--findings docs/findings` runs both checks over all **133** findings documents, and **the sharp check's result is a ZERO — every contrast in every findings document closes.** That is the finding rather than a clean bill: `2026-09-22-network-line-settled.md` prints nine cells of which six match no artifact and its contrasts pass because they are internally consistent, so **a table built from numbers that do not exist can still add up**. Two shapes had to be fixed before the check could be trusted there and both are recorded: a **blocked table has one comparator row per block** (pairing all rows with the first made every row after block one look like it failed — corpus failures 2 → 1), and **`vs X` is ambiguous between "minus X" and "correlated with X"** (a column whose comparator row holds exactly `1.000` is a correlation diagonal and is now skipped with the reason — count 1 → 0). So the two failures this project has are different in kind: **inconsistent and locatable** (a column subtracting two different baselines — found by check (a), appeared **exactly once**, in the table repaired two fires ago) and **consistent and unlocatable** (§4.4's six of nine; invisible to (a), signature present in **68** documents, though most of those are legitimately derived numbers). **The failure mode the project keeps paying for is not arithmetic that does not add up — the arithmetic has added up every time — but numbers that were never a measurement** (`docs/findings/2026-09-23-the-two-table-checks-and-both-pass.md` §5) |
| `e8_rate_network.py --methods naive` at read-out 0/128/32, three repeats each (`e106`) | C2b | **settle the one thing `e104` left unresolved**: is the 1307 → 128 fall in plastic forgetting real, or run-to-run noise (`e106`) | **done — the fall is real, and the check was run with sd exactly ZERO.** Four executions at each read-out, all twelve recording the same environment (`torch_num_threads: 20`, `OMP_NUM_THREADS` unset — the field `e102` added, on its first real use): plastic forgetting **+0.0479 (×4), +0.0333 (×4), +0.0729 (×4)**, accuracies identical within each read-out. So the printed series **+0.021 → +0.035 → +0.066** fails at its first step as a property of the benchmark, not of the measurement. **And the section printed two monotone relationships as a pair when only one holds**: the plastic-minus-frozen accuracy gap is monotone (**−0.0111 → +0.0167 → +0.1000**, the design principle, with the whole-state value *negative*), while at read-out 128 the body **is** load-bearing and forgets **less** than at the whole state where training actively hurt. The quantity the principle needs is the gap; the forgetting series was an accompanying observation that does not survive. **The zero sd is itself a reproducibility datum and it sits opposite this session's others**: a `naive`-only run at a fixed read-out is among the most reproducible measurements in the repository — no Fisher, no replay, no anchor, so one deterministic trajectory per seed — against `ewc-block`/`ewc-block-rand`/`replay` moving between two runs of one command (`e102`) and `naive` moving across thread settings. **The reproducible arms are the ones whose computation is shortest.** Cannot settle: three read-outs is one axis, so this refutes the printed series on the three points the paper chose and does not ask whether another three-point subset would be monotone; and *why* 128 forgets less than the whole state is now the sharper open question, with two candidates named and not separated — an unused body drifts unmeasured, or 128 is simply an easier regime with capacity left over (`docs/findings/2026-09-23-the-plastic-forgetting-series-is-not-monotone.md`) |
| `theta_drift` recorded in the runner, read-out 0/128/32, plus a frozen control (`e107`) | C2b | **instrument and test, one fire after the question was named**: measure how far the recurrent body actually travels, which no run in this project had ever recorded, and use it to test the two candidates for the non-monotone forgetting (`e107`) | **done — the instrument validates exactly and the two candidates are both REMOVED.** `theta_drift` = `‖θ_after − θ_before‖ / ‖θ_before‖` per task; the frozen control gives **0.0000 / 0.0000 / 0.0000** against 0.0197 / 0.0424 / 0.0510 plastic, so the instrument's zero is a zero. Three series: **mean drift 0.0195 → 0.0391 → 0.0493** (monotone in the read-out, ×2.5 from the whole state to 32), **accuracy gap −0.0111 → +0.0167 → +0.1000** (monotone), **forgetting +0.0479 → +0.0333 → +0.0729** (**monotone in neither, and failing at a different step against each**). So **"an unused body drifts unmeasured" is refuted in the opposite direction** — the body drifts *least* where it is least needed — and **"drift ⇒ forgetting" fails too**: at read-out 128 the body moves **2× as far** as at the whole state and forgets **less**, while at 32 it moves 2.5× as far and forgets **more**. **A 2× change in drift reverses the forgetting ordering between one pair of read-outs and the next**, so displacement does not order it. **The per-task structure narrows it further**: drift is near-constant across tasks within a configuration (spreads 0.0014 / 0.0056 / 0.0033) while forgetting varies **sevenfold** over those same tasks, so the three tasks do not differ in how far they move the body and what differs is how much of that motion costs an earlier task. Both candidates being monotone-in-the-read-out and both failing rules out the **family**, not a member: forgetting here is not a monotone function of either "the body moved" or "the body mattered". **The surviving candidate is interaction-shaped** — the overlap between what a task changes and what an earlier task uses, which the *linear* line has measured all along (`e7`, the interference prior) and the network line never has; that is a new instrument and is now the named next step. Cannot settle: three read-outs, one seed-block each, and the drift's own run-to-run spread is not reported (the forgetting beside it reproduces with sd zero) (`docs/findings/2026-09-23-the-bodys-drift-is-monotone-and-forgetting-is-not.md`) |
| gradient-overlap instrument `<grad_j(theta_final), theta_final - theta_after_j>` per task pair, read-out 0/128/32 plus a frozen control (`e108`) | C2b | **pre-registered before its runs**: does the first-order interference term order the forgetting that the drift and the load-bearing gap did not (`e108`) | **done — the falsifier fires on BOTH predictions, and the third candidate inherits the first two's failure.** Control first: the frozen body gives `first_order = 0.0` for both tasks with a defined cosine, so nothing is read off a broken instrument. **P1 fails at two of three read-outs**: at read-out 0 the term for task 0 is **negative** while task 0's forgetting is the *largest*, and at 128 task 1's term is larger while task 0 forgets more; only at 32 does the ordering match. **P2 fails under every aggregation** — forgetting orders the read-outs **128 < 0 < 32**, the term orders them **0 < 128 < 32** whether averaged (−7.1e-03 / +3.7e-02 / +1.6e-01), maximised (+3.1e-03 / +4.1e-02 / +1.6e-01) or made dimensionless (+0.023 / +0.689 / +0.948). **And the reason is structural: the term is ITSELF monotone in the read-out, exactly as the displacement and the gap are — all three mechanistic quantities this project has measured are monotone in the read-out, and forgetting is the only series that is not.** The decomposition says why: the cumulative cosines are **+0.003 to +0.048**, so the displacement is nearly **orthogonal** to the earlier task's gradient and the term's size comes almost entirely from its two magnitude factors, both read-out-axis quantities — **a quantity dominated by its magnitude factors cannot order a per-task pattern**. What the account gets right is the **sign** (positive in 5 of 6 task-level cases), which is what a truncation error looks like when the displacement is not infinitesimal and the loss is not quadratic. **The reportable outcome is the three-member negative the pre-registration anticipated**: forgetting here is not ordered by how far the body moved, by how much the task needed it, or by the first-order interference of the two — and the next candidate must not be a function of the read-out at all, which points at the **task-pair** structure (the per-task displacements `theta_k - theta_{k-1}` and their mutual alignment, both stored and neither yet examined) rather than at any further aggregate over the read-out axis. Cannot settle: three tasks and three read-outs means a failure is conclusive and a success would have been a correlation on a small grid; and first order only, so a mismatch falsifies the account *as tested* rather than refuting it — the truncation is a live alternative explanation (`docs/findings/2026-09-23-the-interference-term.md`, pre-registered in `docs/findings/2026-09-23-the-interference-term-preregistered.md`) |
| second-order term `d'Hd` by exact double backward, plus the Rayleigh quotient, with a frozen control (`e109`) | C2b | **pre-registered before its runs**: the first candidate that is not a function of the displacement magnitude (`e109`) | **done — the structural premise is refuted, and the term is the first candidate whose structure is NOT monotone in the read-out.** Controls: the frozen body gives `quad = 0.0` and `curvature = 0.0` for both tasks; and `d'Hd` by double backward is compared against **`torch.autograd.functional.hvp`** in a test (agreement to 1e-4 relative), because the values include **negative** quadratic forms, which is possible for a non-convex loss and is also what a broken implementation looks like — and the finite-difference form of the instrument **failed its own cross-check** (8.512e-01 at a step of 1e-3‖θ‖ against 1.709e-01 at 1e-2‖θ‖, disagreeing with itself by 5×, against an exact 3.027). **P1 refuted**: the prediction was structural — a quadratic form is positive by construction for a PSD Hessian — and `quad` is **negative in 3 of the 6** task-level cases, so `H_j` is not positive-semidefinite along the direction the body moved; **the sign argument that motivated measuring this term is not available**, and the negatives say the body moved into directions where the earlier task's loss *decreases* to second order. **P2 not confirmed and aggregation-dependent**: averaged over tasks the curvature orders the read-outs **128 < 0 < 32** (matching the forgetting), at its maximum **128 < 32 < 0** (failing) — and one aggregation agreeing while another fails is not a confirmation, the standard applied to `e99`/`e100` earlier. **P3 refuted against my own expectation**: I predicted `quad` would be monotone in the read-out and fail; measured it is **not monotone** — it is **negative at read-out 128** (mean −2.92e-1 against +1.48e-1 at 0 and +8.59e-1 at 32), which makes the second-order term **the first quantity in this sequence whose structure is not a function of the read-out**, exactly the property `e108` said the next candidate had to have and I did not expect this one to be it. **What survives every aggregation, stated as a hypothesis rather than a result**: read-out 128 is the **only** one where the curvature is negative for **both** tasks, and it is the one that forgets least — a qualitative difference where the previous three candidates differed from each other only in magnitude along one axis. **Its test is cheap and specific: a fourth read-out between 128 and 1307**, where the forgetting is not yet known, should have negative curvature for both tasks if the pattern is real. Cannot settle: `H_j` is taken at one point (the final body, not where the displacement happened); second order only, with the third-order term unbounded at these cosine sizes; and the pooling choice was made after seeing both aggregations, which is a degree of freedom this project has a rule against (`docs/findings/2026-09-23-the-second-order-term-changes-sign-at-128.md`) |
| `--readout-size 512`, plastic + repeat + frozen (`e110`) | C2b | **pre-registered before its runs**: the one cleanly falsifiable test of the surviving hypothesis — read-out 512's forgetting was not already known (`e110`) | **done — the hypothesis is REFUTED and the fourth point relocates the anomaly.** **P1 fails**: at 512 the curvature is **positive for task 0 and negative for task 1**, so the negative region is not an interval. **P2 holds**: its forgetting is **+0.0208**, the **smallest of the four**. **Falsifier (a) fires verbatim** — positive curvature for one task *and* the smallest forgetting — so **the sign of the curvature does not track the level of the forgetting**, and the one qualitative pattern found at the anomalous read-out is dead. **And the four points change what the anomaly is**: along the axis the forgetting is **+0.0479 → +0.0208 → +0.0333 → +0.0729**, which is not monotone, but **the three narrow read-outs are** (+0.0208 < +0.0333 < +0.0729) — so the non-monotonicity is **not a mid-range dip but one configuration's excess at the WHOLE STATE**, which forgets more than 512 and 128 despite being the widest read-out and the one where the body is *least* needed (its gap is the only negative one, −0.0111) and the one the paper itself says "contains no continual-learning problem". **Forgetting measured there is measuring something else**, which reframes four fires of searching: the question was *what makes the middle anomalous* and the middle is not anomalous. **Across all four points the drift is monotone (0.0195 → 0.0258 → 0.0391 → 0.0493) and the gap is monotone (−0.0111 → +0.0014 → +0.0167 → +0.1000) while the forgetting is not** — five fires of instrumentation saying every mechanical quantity this project can measure is monotone in the read-out. **The 512 execution was repeated and is bit-identical** in both forgetting and curvature, extending the `sd = 0.0000` result to a fourth read-out in the same recorded environment. Cannot settle: four read-outs is still a curve on four points, and the reframed claim is exactly as strong as three-plus-one can be — a fifth read-out between 512 and 1307 would put a point inside the interval the new question is about; the curvature's negatives were validated only against `torch`'s own `hvp`, which is an independent implementation of the same derivative rather than an independent measurement; and it says *where* the excess is, not what it is (`docs/findings/2026-09-23-the-anomaly-is-the-whole-state-not-the-middle.md`) |
| `--readout-size 900`, plastic + repeat + frozen (`e111`) | C2b | **pre-registered before its runs**: a fifth read-out inside the interval the reframed question is about — is the wide arm monotone, or is the whole state an outlier? (`e111`) | **done — both predictions hold, and the fifth point RETIRES the framing rather than a hypothesis.** Read-out 900 was pre-registered as **strictly between** 512 and 1307 on both series: forgetting **+0.0292** (between +0.0208 and +0.0479) ✓ and the gap **−0.0014** (between −0.0111 and +0.0014) ✓, with the frozen control at **exactly `+0.0000`** and the repeat bit-identical in the same recorded environment. **So the five points are 0.0479 > 0.0292 > 0.0208 < 0.0333 < 0.0729 — read as two arms, EACH IS MONOTONE** and the minimum is at 512. **There is no outlier**: the previous fire's "the whole state is the one point above them" was an artifact of having only one point on the wide half, and its numbers stand while its name for them does not — the third time in this sequence a shape claim was revised by adding a point, and the first time the revision retired a framing. **Per task**: task 0 is a clean two-sided minimum with both arms monotone (0.0833 > 0.0375 > 0.0333 < 0.0583 < 0.0833); task 1 is non-monotone on the wide half between two *small* values (0.0125 vs 0.0208, a 0.0083 difference) with its only large value at 32 (+0.0625) — so the reported metric's clean V is carried by task 0 and that residual is named rather than averaged away. **And this is the first DESIGN statement in the sequence, about the benchmark rather than a candidate mechanism**: the paper's principle is about the body being load-bearing, and the gap says that monotonically (−0.0111 → −0.0014 → +0.0014 → +0.0167 → +0.1000), while the forgetting is minimized at **512 of 1307** — *between the two extremes the principle brackets* — so the two quantities a practitioner would use to pick a read-out are monotone in **different** respects and the second has an interior optimum. **Which is also why four candidate mechanisms failed here rather than by coincidence**: every mechanical quantity this project has measured is monotone in the read-out, and **a two-sided minimum cannot be ordered by a monotone quantity**. Cannot settle: five points is a curve on five points and the minimum's location is known only to within (128, 900); the depth of the minimum is 0.0125 below its neighbours, the same size as task 1's wide-arm residual; and with two forgetting values per configuration the mean is a two-point average, the last task being excluded by construction (`docs/findings/2026-09-23-the-read-out-axis-has-an-interior-minimum.md`) |
| `--readout-size {300,700}`, each plastic + frozen, plus a repeat at 300 (`e112`) | C2b | **pre-registered before its runs**: bracket the minimum from both sides — one point on each arm, so a bowl whose minimum sits at 700 is distinguishable from a corner at 512 (`e112`) | **done — BOTH predictions FAILED, the five-point bowl is refuted, and the result is a design statement instead.** P1 failed: f(700) = **+0.0354**, *above* 900's +0.0292, so **the wide arm is not monotone** (a local bump at 700, +0.0062 against 900). P2 failed: f(300) = **+0.0083**, *below* 512's +0.0208 — the minimum **moved** to the narrow side and is **2.5× deeper** — which is the exact branch the pre-registration separated in advance (a deeper, shifted bowl is a *better* benchmark result and a *worse* location claim), so **the location claim is refuted and the benchmark statement strengthened**. Seven points with both metrics: forgetting **+0.0479 / +0.0292 / +0.0354 / +0.0208 / +0.0083 / +0.0333 / +0.0729** and accuracy **0.9333 / 0.9347 / 0.9431 / 0.9486 / 0.9569 / 0.9333 / 0.9139** — so **read-out 300 has BOTH the lowest forgetting and the highest accuracy of the seven**, and its forgetting is the **lowest plastic `naive` value in the whole corpus** (0.0083 against 68 such arms; the next lowest is the 2-class configuration's 0.0167), with task 1 **negative** (−0.0042) and task 0's minimum **also** at 300, so this shape is per-task consistent where the five-point one was not. **The accuracy series is non-monotone too, peaking at the same read-out**, so **the two metrics agree on an interior optimum** — the strongest form of the statement. **Which separates two statements the paper makes only one of**: the load-bearing gap rises monotonically as the read-out narrows (−0.0111 → −0.0014 → −0.0014 → +0.0014 → +0.0153 → +0.0167 → +0.1000) and that is what the design principle is about, while **both reported metrics are optimized at ~23% of the state's width and are worse at either extreme** — read-out 32 has the **largest** gap and the **worst** forgetting and accuracy. So *"narrow the read-out so the body is load-bearing"* and *"do not narrow it past an optimum"* are different statements, and the second is the one a practitioner needs. **And the five-point bowl was not a bowl**: its description came from monotone arms of length three and four, and two more points broke one arm and moved the minimum by 1.7× — the fourth shape revision in this sequence, each from a pre-registered prediction about the next point. **A monotone arm of length three is the weakest possible evidence for monotonicity, and it has now failed twice here.** Cannot settle: seven points is a curve on seven points and the minimum is bracketed by (128, 512); the 700 bump (+0.0062) is real at this configuration (sd 0) but unexplained and may be a second local feature; and the accuracy peak carries the test-set floor — 0.9569 on 144 held-out decisions per replicate, so a 0.008 difference between 512 and 300 is comparable to that floor even though the replicate spread is zero (`docs/findings/2026-09-23-both-metrics-have-an-interior-optimum.md`) |
| `--readout-seed` added to the runner; read-out 300 at **four independent draws** and 512 at two (`e113`) | C2b | **pre-registered before its runs**: is the read-out shape about the SIZE or about WHICH NEURONS were drawn — the control its own construction was missing (`e113`) | **done — the confound was real, the falsifier fired at exactly the threshold, and the previous fire's design statement is WITHDRAWN.** The subset is drawn **independently per size** (`choice(size=300)` is **not** a superset of `choice(size=32)`; two draws at one size overlap in **63–73 of 300** against a chance rate of 69; a size-32 draw is **not contained in** a size-300 draw), so **every point on the seven-point axis differed from every other in *how many* neurons were read out AND in *which* ones**, with only the first treated as the variable — **five fires of shape work violated rule 26 at the level of the axis's own construction**. Four independent draws at read-out 300 give forgetting **+0.0083 / +0.0146 / +0.0208 / +0.0208**, a span of **0.0125**, and **0.0125 is exactly the across-size difference the design statement rested on** (512 vs 300); two draws at 512 also span 0.0125. **P1 and P2 both fail, at exactly the number the pre-registration named**, so **the variation a practitioner cannot control (which neurons) is the same size as the variation they can (how many)** and "read-out ≈ 300 is the optimum on both metrics" is not distinguishable from a property of which 300 neurons were drawn — **withdrawn**, and with it the "anomaly" language of the two fires before it. **What survives, against the draw's own sd (0.0060, four draws)**: three of six neighbour steps are resolved — 1307 → 900 (3.13 sd), 300 → 128 (4.18), 128 → 32 (6.61) — and three are not: 900 → 700 (1.04, so **the bump is unresolved rather than a second feature**), 700 → 512 (2.44), and **512 → 300 (2.09), the step the statement rested on**. The interior minimum *exists*; its location and depth do not survive. **And the draw is a second source on top of the reported sem** (0.0101 at 300, over five training replicates at a fixed draw), so **the paper's uncertainty was not wrong — it measures something else**, this line's oldest lesson on a new axis. **Durable fix made in the same commit**: the payload now carries a `readout` block (`size`, effective `draw_seed`, `subset_sha1`), because until this fire **the artifact identified its read-out size and not its subset** — so every "bit-identical over seven executions" result in this record is reproducibility *given a draw*, not across draws. **The added rule: a factor that is not the manipulated variable is not thereby held constant; `config` records what was asked for, and "identical config except the variable" is a claim about the code's other inputs, one of which was an RNG draw.** Cannot settle: four draws at one size and two at another (the draw sd is measured only at 300, and read-out 32 — one of the three surviving steps — has no second draw); a paired treatment is not done here even though all seven runs share the training seeds, which would be tighter and is the honest next step; and the mechanism claim *"mechanical quantities are monotone while both metrics are not"* now rests on a series whose fine structure is inside the draw, so its honest form is the coarse one (`docs/findings/2026-09-23-the-draw-is-as-large-as-the-effect.md`) |
| all 21 read-out pairs from the seven stored artifacts, against the per-repeat spread and the draw span (`e114`) | C2b | **analysis, and it tests the two things `e113` named as next**: the paired treatment all seven runs licence, and a second draw at every read-out (`e114`) | **done — the cross-read-out series REDUCES TO ONE SENTENCE, and the paired treatment is the wrong tool for it.** **Paired**: it makes **four of the six neighbouring steps worse** and none decisive (the per-replicate differences do not share a sign — at the whole state one replicate's forgetting runs −0.0104 / +0.0833 / −0.0104 / +0.0104 / +0.1667) — and where it looks strong it is **structurally blind**: 900 → 300 at **6.32σ paired against 1.54σ unpaired** and 300 → 32 at **8.44 vs 3.56**, because a **systematic difference between two read-outs' draws is a constant offset in the paired difference**. Pairing removes the shared training-seed variance and **cannot touch the draw**, which is fixed within a run — so its σ is optimistic by exactly the draw's contribution (0.0125, measured), and 900 → 300's 0.0208 is **1.7 draw-spans**: suggestive, not decisive, where the paired σ would have read as a resolution. **A statistic blind to its own confound is not a tighter measurement.** **Unpaired**: only **4 of 21** pairs resolve at 2σ — **900 → 32 (2.49), 512 → 32 (3.04), 300 → 32 (3.56), 128 → 32 (2.02)** — and **every other pair is below 2σ** with all six neighbour steps below 1.6σ, including **512 → 300 at 0.97σ, the step the withdrawn statement rested on**. Read-out 32 does not resolve against the whole state either (0.67σ), because that point carries the largest per-repeat spread of the seven (**0.0768** against 0.018–0.039). **So five fires of shape work reduce to: read-out 32 forgets more than 900, 512, 300 and 128** — the interior minimum, its location, the 700 bump and the coarse decline are each inside the noise of at least one uncontrolled factor. **The cost table is the deliverable**: against the per-repeat sd at each end, the 700 bump needs **200 replicates per side (≈147 min)** and must be **abandoned rather than chased**, while the **512 → 300 step needs 22 per side (≈16 min)** — so the registration that follows is 22 replicates at 300 and 512, and **not** the second draw at 32, because the binding limit at every step is the per-repeat spread (the paper's own §4.7 sentence) and the way to beat it is replicates rather than draws. **The boundary of the damage is the draw**: every arm within one run shares that run's subset, so **within-run contrasts (block vs matched control, diagonal vs `naive`, replay) are immune** and their σ's stand — what is reduced is the **cross-read-out** series, whose frozen-body trend survives (−0.0111 → +0.1000, far beyond any draw span) but whose individual steps have not been tested against the draw. Cannot settle: the draw span is measured at one size, so the cost table's counts are upper bounds; and whether read-out 32 is *special* or simply the far end of a monotone trend is exactly what does not resolve (`docs/findings/2026-09-23-the-axis-reduces-to-one-statement.md`) |
| `--repeats 40` at read-out 300 and 512 (`e115`) | C2b | **pre-registered before its runs**: forty replicates on the one step an interior minimum stands on — a deliberate departure from the cost table's 22, because a design that lands exactly on its own 2σ criterion cannot answer the question it is asked (`e115`) | **done — C0 passes, P1 FAILS, and the interior minimum is a flat trough.** **C0, the extension control, passes at both read-outs**: the training seed is `seed0 + 100r`, so the first five replicates of a forty-replicate run must be **bit-identical** to the stored five-replicate runs, and they are — so the runs are extensions rather than separate samples (the `e61`/`e68` check, made in advance here). **P1 fails**: 512 = **+0.0250 ± 0.0048** and 300 = **+0.0232 ± 0.0040**, a difference of **+0.0018 at 0.29σ** — and the reason is in the means rather than the arithmetic: **read-out 300 moved from +0.0083 at five replicates to +0.0232 at forty**, a change of **+0.0149**, *larger than the whole step the withdrawn statement rested on* (0.0125). With forty replicates the two lowest points on the axis are **statistically indistinguishable** and neither differs from 900 (0.61σ and 0.41σ), so **the interior minimum is not a minimum but a FLAT TROUGH** — the third consecutive retraction on this axis and **the first made by replicates rather than by points** (five points gave a bowl, two more broke it, the draw control showed the scale was wrong, and more replicates show the floor is flat). **And it falsifies a second claim from the same measurement**: read-out 300 was recorded as *"the lowest plastic `naive` forgetting in this corpus"*, true of the five-replicate value (0.0083 against 68 such arms) and false of the forty-replicate one (+0.0232, above the 2-class configuration's +0.0167) — **a corpus record built on five-replicate minima has five-replicate resolution**. **P2 held by its letter and failed by its purpose**: the forty-replicate sds are **1.69×** and **1.12×** the five-replicate ones, inside the registered factor-of-two — but **a factor-of-two tolerance on an sd is a factor-of-FOUR tolerance on a replicate count** (`n ∝ sd²`), and the observed ratios moved the cost table's counts by **2.9× and 1.2×**, so the step priced at 22 replicates per side was really **~63**. **The durable rule: when a cost is computed from an sd, the sd needs the same evidence standard as the effect.** What survives is unchanged — **read-out 32's excess** (+0.0497 at **3.2σ** against the forty-replicate 300; 2.0–3.6σ against 900, 512 and 128) — and everything between 128 and 900 is a flat region whose internal structure does not resolve. **The axis is now measured with unequal precision**: 300 and 512 carry forty replicates and the other five carry five, so every comparison involving one of them is dominated by the *other* side's noise (900's sem 0.0090 against 300's 0.0040) — **finishing the axis means forty replicates at the other five points, ≈ 75 minutes**, which is the concrete next step rather than any further point. Cannot settle: the draw is still one per read-out, so forty replicates are forty samples of the *training* noise at one draw and the draw span (0.0125 at that size) is not averaged over; and the forty-replicate sds are themselves estimates from forty points (`docs/findings/2026-09-23-forty-replicates-refute-the-minimum.md`) |
| `--repeats 40` at the five remaining read-outs (`e116`) | C2b | **pre-registered before its runs**: put the whole axis on ONE precision, with the direction of the noise predicted (`e116`) | **done — all five C0 controls pass, P2 and P3 confirmed, P1 (my own directed correction) FALSIFIED, and the axis finally has one error bar.** **C0 at all five read-outs**: the first five replicates of each forty-replicate run are **bit-identical** to the stored five-replicate run, so each is an extension rather than a second sample. **The shape** (40 replicates each): **1307 +0.0357, 900 +0.0219, 700 +0.0221, 512 +0.0250, 300 +0.0232, 128 +0.0370, 32 +0.0750** — so **900 through 300 is a FLAT PLATEAU** (four read-outs spanning **0.0031**, every neighbouring step inside 0.43σ; **900 → 700 is 0.04σ**) and **the narrow end is resolved above it**: 300 → 128 by **2.12σ** and 128 → 32 by **3.73σ** (the latter 5.5σ above the plateau's low point), with the whole state at 128's level, **1.79σ above the plateau — nominally elevated, not resolved**. **P3 confirmed** (the flat region extends from 300 to 900, none of those four steps resolving) and **P2 confirmed** (32 remains the maximum). **Every fine feature of the previous five fires was a five-replicate artifact**: the whole-state "outlier" is indistinguishable from 128 (0.29σ), the 700 bump is 0.04σ, and the interior minimum at 512 and the interior optimum at 300 are both inside the same four-point plateau — read-out 300's five-replicate value, which was **the lowest in this corpus**, moved from **+0.0083 to +0.0232**. **P1 FALSIFIED**: the forty-replicate sds are **0.55×, 1.22×, 0.75×, 1.69×, 1.12×, 1.16×, 1.65×** the five-replicate ones — three of seven *down*, the largest movement *downward* (the whole state 0.0768 → 0.0423) — so **a five-point sd is noisy in BOTH directions rather than biased**, and the previous fire's "2.9× underestimate" was one draw from a distribution spanning 0.55–1.69×. **The corrected rule: a replicate count computed from an sd is uncertain by a factor of ~3 in EITHER direction**, not low by a factor — and the five-replicate *means* moved in both directions too (four down, three up). **What survives is the first shape on this axis measured at the resolution it is stated at**: *narrowing the read-out below 300 raises three-task naive forgetting, mildly at 128 and sharply at 32; 900 down to 300 is one plateau; and the whole state is nominally above that plateau but not measurably.* Cannot settle: the draw is still one per read-out, and while the plateau's internal range (0.0031) is below the measured draw span (0.0125), the plateau-to-128 step (0.0138) is not — **the draw could account for that step**, and separating them needs replicate draws rather than replicates, at ~40× the cost (`docs/findings/2026-09-24-the-axis-is-a-plateau.md`) |
| `--readout-seed {1,2,3}` at read-out 128, 20 replicates each (`e117`) | C2b | **pre-registered before its runs**: the draw may have been the wrong culprit — `e113`'s four draws were five replicates each, so each mean carried an sem (~0.010) LARGER than the 0.006 effect it was looking for (`e117`) | **done — P1 holds, the falsifier does not fire, and the draw is NOT detectable.** Four independent draws at read-out 128: **+0.0370 (40 reps), +0.0469, +0.0411, +0.0349 (20 each)**, with **observed scatter sd 0.0053 against a replicate-noise expectation of 0.0079 — ratio 0.67**, so the draw variance component estimates to **zero**. The same arithmetic on `e113`'s four five-replicate draws at read-out 300 gives **0.61**. **Two read-outs, two estimates, both below one: the draw is not detectable at the size the earlier data suggested (≥ 0.0079).** So **`e113`'s "draw span 0.0125" was four underpowered means rather than four draws** — a design cannot measure a variance smaller than its own noise — and its withdrawal of the design statement was **right at the time and for a reason it did not give**: the five-replicate *means* were unreliable (what `e115`/`e116` showed), while the **draw itself was never shown to matter**. **And the plateau's one resolved step survives the control**: all four draws of read-out 128 land **above** the plateau (+0.0138, +0.0237, +0.0179, +0.0117 against the 300 point = **2.1σ, 2.3σ, 2.0σ, 1.3σ**), three resolving on their own with the fourth in the same direction, and the scatter among them smaller than replicate noise — so **the elevation of read-out 128 is a property of the read-out SIZE and not of which 128 neurons were drawn**. **What is restored is the INTERPRETATION** (the axis can be read as a size axis) **rather than the withdrawn claim**, which the two fires before had already replaced with the plateau. **Three revisions of one sentence in four fires** (optimum at 300 → flat trough → plateau), and the first whose confound has been measured rather than assumed. Cannot settle: a draw sd below 0.0079 is not excluded (the honest null is *"no draw effect at or above the size the earlier data suggested"*); it is measured at two read-outs and not at 32, whose 3.73σ step is argued rather than shown to be draw-immune; and the four draw means have unequal sems (40 reps at one, 20 at three), so the ratio test is an approximation whose direction does not depend on the weighting (`docs/findings/2026-09-24-the-draw-is-not-detectable.md`) |
| the forty-replicate sds of `theta_drift` and `mean_forgetting` at all seven read-outs, plus the four draws at 128 (`e118`) | C2b | **analysis, no runs**: the relative precision of the metric against the quantity it has been compared to, and the one decoupling the axis cannot provide (`e118`) | **done — the metric is THIRTY TIMES noisier than the quantities compared against it, and the drift question is closed in its strongest form.** At forty replicates per read-out: **the drift is monotone in the read-out to three decimals** (0.0191, 0.0216, 0.0236, 0.0260, 0.0309, 0.0395, 0.0497) **and measured to 2.6–3.5% of itself**, while **the forgetting is a plateau measured to 74–134% of itself** — a **30× difference in relative precision on seven read-outs**, which is not an effect size but a difference in the estimator: the drift is a norm over 26,568 numbers and averages out a 26-millifold of contributions, the forgetting is a difference of accuracies over 48 held-out decisions twice, with granularity 1/240. **§4.7 already says the binding limit is the benchmark's per-repeat spread; this measures the ratio that makes it binding** — and it **reframes rather than repeats** the mechanism search: the four mechanical candidates failed for a reason diagnosed as *shape*, and a plateau is also what a signal looks like when the noise is thirty times the effect, the two being one fact from two sides. **And the decoupling closes the drift question in its strongest form**: across the seven read-outs the drift is monotone and perfectly confounded with size, but the **four independent draws at read-out 128** hold the size fixed and vary the draw — drift **0.0395 / 0.0382 / 0.0376 / 0.0396 (sd 0.00095, 2.4%)** beside forgettings **0.0370 / 0.0469 / 0.0411 / 0.0349 (sd 0.0053, 14%)** — so **the same drift sits beside forgettings spanning 0.0349 to 0.0469** and **forgetting is not a function of how far the body moved**. That also kills a reading the axis alone made tempting — *"forgetting is flat until the body has moved more than ≈ 0.031 and rises after"* — as an artefact of the drift being a re-parameterisation of the read-out. **So `theta_drift` is this line's best instrument and its least useful predictor: it reproduces to 3% across forty replicates and 2.4% across four draws, it is monotone to three decimals, and it carries no information about the forgetting — a quantity can be precise, monotone and irrelevant at once, and the way that was found out was to measure it.** Cannot settle: the 3% drift figure is conditional on the configuration (cs = 800, three tasks, 500 iterations); it does not say the metric cannot be ordered by anything, only that the four quantities tried are thirty times more precise than it is; and "thirty times" is a ratio of coefficients of variation rather than of variances, so it describes the comparison's difficulty rather than any underlying randomness. **The productive directions it implies: a metric with a better SNR (more held-out decisions, more tasks), or a statement that does not need the metric to be ordered — which is what the plateau is** (`docs/findings/2026-09-24-the-metric-is-thirty-times-noisier.md`) |
| `--test 480` at read-out 128 and 300, 40 replicates (`e119`) | C2b | **pre-registered before its runs**: enlarge the test set — the first of the two routes `e118` named — since the runner's own block says the test-set share is *"cheap to reduce and easy to forget"* (`e119`) | **done — P1 FAILS at both read-outs (marginally), P3 holds, and the FAILURE IS THE FINDING: the metric's removable noise is 94% removed by a tenfold test set and the rest is the SUBSTRATE's.** Per-repeat sd: 128 **0.0325 → 0.0221** (1.47×) and 300 **0.0252 → 0.0188** (1.34×), against a pre-registered band of 1.5–3.2× and a predicted 2.1×. Solving for the forgetting's own split (the binomial part must fall by √10 while the training part does not move): **128 = 60% evaluation / 40% training, 300 = 49% / 51%**, so the **ceilings are 1.57× and 1.41×** and **the tenfold test set captured 94% and 95% of what is removable**. **The remainder — 0.0207 and 0.0179 — is the substrate's own run-to-run variation, which §4.7 names as the binding limit, now decomposed and priced.** **And the run corrects how the section's own noise block should be read**: `evaluation_noise` is computed on the arm's **accuracy** (85% removable at read-out 128), while the **forgetting's** own share is **60%** — because the forgetting is a difference of two accuracies evaluated on the **same** test set, so hard items are hard in both, the test-set errors are positively correlated and **partly cancel**; the binomial arithmetic that governs one accuracy overstates what a bigger test set can do for a difference of them. **The handicap narrows from thirtyfold to eighteenfold** (the forgetting's sd is 55% of its own value at 128 against the drift's 3%) — a factor of two existed and has been taken, **and the rest is not noise**. **P3 holds**: the plateau-to-128 step is **+0.0133 at 2.90σ** (was 2.12σ), so the axis's one resolved step survives a better metric and sharpens. **P2** holds at 128 (+0.0032 within the new sem) and marginally fails at 300 (+0.0037 at 1.23 of its new sem) — both upward and small, and neither is what a test-set change should do, so the honest reading is that the moves are not resolvable, which is the same statement as before: this metric cannot separate a 0.003 movement from zero even at forty replicates. **What this points at is a hypothesis about the SUBSTRATE rather than the measurement**: if the residual is the training trajectory's, then 500 iterations of SGD from a connectome-masked initialisation land in materially different places for different seeds, and **the test is whether converging further collapses it** — 4× the iterations at 40 replicates, ≈1 hour, and the first next step this sequence has proposed that aims at the substrate rather than at the axis, the metric or the statistic. Cannot settle: the decomposition assumes the evaluation component scales exactly as √10, which is approximate because the two accuracies in the difference are correlated, so the 60/40 split is an estimate from two runs rather than a measurement of two components; and two read-outs is a pattern rather than a law (`docs/findings/2026-09-24-the-metric-noise-is-mostly-the-substrates.md`) |
| `--iters 2000 --test 480` at read-out 128, 40 replicates (`e120`) | C2b | **pre-registered before its run**: four times the training, to test whether the substrate's residual is under-convergence — the second and last member of the "improve the measurement" family (`e120`) | **done — P1 HOLDS, the falsifier does NOT fire, and the limit is INTRINSIC.** 500 → 2000 iterations: forgetting **+0.0402 → +0.0461** with per-repeat sd **0.0221 → 0.0305**, accuracy **0.9215 → 0.9276** with sd **0.0196 → 0.0222** (a factor of **0.88** against a pre-registered bound of 1.3, so the spread RISES slightly), and drift **0.0395 → 0.0460**. **So four times the compute does not make two seeds agree** — the seeds land in genuinely different places, and a longer walk in a different direction is still a different direction, which is what the fire predicted from the drift's 2.9% relative reproducibility. **P2's propagation held including its direction**: the forgetting's sd rose with the accuracy's, so the two move together through **√(2(1−ρ))** as the diagnostic said, with **ρ ≈ 0.14 at 500 and ≈ 0.06 at 2000** — longer training makes the two accuracies *less* correlated across seeds, the same statement as the spread rising. **And C1's prediction was WRONG in an informative way**: the drift grew only **1.16×** for four times the iterations against a predicted "roughly doubling or more", so **the body is essentially done moving at 500 iterations** — which refutes the convergence hypothesis by a second route and makes the drift series across read-out sizes a series of **converged** distances rather than snapshots of an interrupted optimisation. **What four times the compute buys is +0.0060 accuracy and +0.0059 forgetting, and no reduction in spread at all**, smaller than one per-repeat sd of either quantity — so "train the benchmark longer" is not a route to precision either. **§4.7's sentence now has a mechanism and has survived both attempts to remove its cause**: more replicates remove the sem (40×) and leave the per-repeat sd; a tenfold test set removes 94% of the removable evaluation noise and leaves 40% of the variance in the training trajectory; four times the training removes nothing and the sd rises — **forty seeds of one configuration, trained four times as long, still disagree by 0.0305, which is 74% of the value they are disagreeing about.** **Both members of the "improve the measurement" family are now closed**, and what is left is what `e119` named second: **a statement that does not need the metric to be ordered, which is what the plateau already is.** Cannot settle: one read-out and one seed block (32, where the spread is largest, is untested); two iteration counts is a line rather than a curve, so the budget is ruled out *at the scale the benchmark uses*; and it does not distinguish "multi-basin landscape" from "same basin, different direction" — that needs the loss along the interpolated path between two seeds' solutions, a different instrument and the first this sequence has proposed that is about the geometry rather than the noise (`docs/findings/2026-09-24-four-times-the-training-does-not-help.md`) |
| the final minibatch training loss per replicate across all seven read-outs, plus its seed-level correlations with the held-out metrics (`e121`) | C2b | **analysis, no runs**: whether the limit is intrinsic because of the *regime* rather than the optimiser — is this benchmark interpolating its training data? (`e121`) | **done — the benchmark INTERPOLATES at every read-out, and that is why no trajectory quantity can order the forgetting.** Final training loss per read-out: **1307 0.00014, 900 0.00022, 700 0.00028, 512 0.00035, 300 0.00067, 128 0.00158, 32 0.00451** against a chance-level **ln 4 = 1.386** — **a factor of 300 to 10,000 better than chance at every read-out, including the narrowest**, where the tasks are still fitted to 0.005. With 96 training samples per task against 26,568 body parameters that is roughly **300 parameters per training sample**: **no read-out tested is capacity-limited.** **The fit depth is itself monotone in the read-out (×32 from the whole state to 32)** — a **fourth** monotone quantity against the plateau, alongside the drift, the gap and the first-order term. **So the seeds agree on the fit and disagree on the generalization**: all forty drive the training loss to ~1e-4 while their held-out metrics differ by 0.0196 and 0.0221, and **the fit depth carries no information about retention** (correlations of loss with forgetting −0.05 and +0.34, disagreeing in sign between budgets; aggregates at zero) — a **fifth** quantity and a fifth failure, and the first that is a property of the ENDPOINT rather than the trajectory. **One seed-level structure did appear**: the two tasks' fits correlate **−0.35** and **−0.31** at the two budgets, both at the 5% threshold for n = 40 and agreeing in sign — a **capacity-allocation** trade-off and the first seed-level correlation this line has found (a lead, not a result). **And it qualifies the design principle**: "load-bearing" means the **read-out cannot carry the task**, not that the body is near its capacity, because **the body still interpolates at 32 neurons** — **the benchmark is over-parameterised at every read-out the paper uses**, which is the same fact that produces the plateau: **in a regime where every seed interpolates, the forgetting is a property of WHICH INTERPOLANT the run lands in, and no trajectory-level quantity has purchase on that** — one story rather than five failures. Cannot settle: `losses[k]` is a single 32-sample minibatch's loss at the last training step rather than the full training-set loss (a per-seed full-set loss is cheap to add and would be stronger); the trade-off correlation is at the significance threshold and 40 seeds can produce one by chance, so 120 seeds would be the natural test (`docs/findings/2026-09-24-the-benchmark-interpolates-its-training-data.md`) |
| `e122_path_geometry.py` at read-out 128, 21 points along each chord, seeds 0 and 100 (`e122`) | C2b | **the one question `e120` explicitly left open, and the first instrument in this sequence that is about the GEOMETRY rather than about the noise** — the loss along the chord between two seeds' solutions, which separates "multi-basin" from "same basin, different direction". **Not pre-registered**, and §5 of the finding states what that costs the claim | **done — the seeds' solutions are CONNECTED, the barrier between them is a factor rather than a wall, and TWO bugs were found by the endpoint control this fire built.** **The result, on the cleanest chord** (through the checkpoint after task 0, so nothing is retained yet and the only question is the task just fitted): the endpoints are **0.00172** and **0.00182** — the two seeds' own recorded full-train-set loss on that task, agreeing to 5% — and the loss rises smoothly and symmetrically to a single interior maximum of **0.05399 at t = 0.45**, i.e. **a factor of 30 above the worse endpoint** (31× above the better, so the reading does not depend on which end is called the reference). **And 0.05399 is 3.9% of the chance level ln 4 = 1.386**, the loss at which the task is not solved at all — so the path never comes within a factor of **26** of a solution that has learned nothing. **There is a barrier — the maximum is strictly above both ends, so neither is a minimum along the path and the path is not monotone — and it is not a wall**, which is what a multi-basin landscape would require: separating basins means crossing a ridge at the scale of a *bad* solution. **In the operational sense the question was asked in, the two seeds land in one connected set, and "which basin" is not what the seed chooses between — it chooses a point of a connected, over-parameterised, interpolating set.** The three other chords agree and are quoted because two are dominated by retention: the just-trained task has the same single interior maximum (**final/task 2: 0.00118 → peak 0.04394 at t = 0.55, ×35, 3.2% of chance**), while the retained tasks' maxima sit at an interior point **near the seed that retained worse** and the chord is then a slope — **final/task 1** peaks at 0.10705 at t = 0.25 against its worse end (0.05885) and falls monotonically to 0.01719, and **final/task 0** is essentially **monotone** (barrier +0.00264, 1.5%, peak at t = 0.95 against its worse end at t = 1) — so those two chords mostly measure the 1.8× and 3.4× difference between their ends (retention, not geometry). **Connected as solutions, NOT interchangeable as parts**: holding seed A's decoder fixed while the body moves, seed B's body read through it rises monotonically from 0.00118 to **0.16010 on the final task — a factor of 135** with no interior maximum — so **the recurrent body and its decoder are jointly determined by the run and neither is transportable alone**; the whole-solution chord is the right instrument for this question and the body-only chord is not a weaker version of it but a different one. **And the interpolant story now has ratios**: the two seeds agree to **5%** on the task they just trained (0.00118 vs 0.00124) and differ by **1.8×** (0.09678 vs 0.17250) and **3.4×** (0.05885 vs 0.01719) on the two retained tasks — `e121`'s "they agree on the fit and disagree on the generalization", as a ratio, and **the first time this project has the retained LOSS rather than only the retained accuracy**. **The two bugs, both invisible to every audit in this project and both caught by one control**: (1) `run_method` saved the decoders only at the end, so a chord through a mid-run body was evaluated with the *final* decoder — a configuration the benchmark never produces; (2) **`--save-theta` never saved the recurrent bias**, and `train_task` optimises `[model.theta, model.bias]` (`experiments/e8_rate_network.py:72`), so every point on every chord — both endpoints included — sat on a **zero bias**, and the first version reported endpoint losses of **0.105** for a body whose own recorded loss was **0.0017**. **The control is an equality rather than a tolerance and it needed the runner to record the right number first**: the chord at t = 0 *is* seed A's checkpoint, so its loss must equal the runner's own figure, which meant adding **`retention_loss[k][j]`, the full-train-set loss on task j at checkpoint k** — **the retention matrix in loss, the first loss-valued retention record in this project** (`full_train_loss[j]` is recorded at checkpoint *j*, a different body for every j < T−1, so the control's first version demanded agreement between two configurations and reported a failure where there was none). Result: **6 of 6 task-endpoints agree exactly** across the three checkpoints, plus the independent reproduction of `e116_r128_40reps.json` replicate 0 (forgetting +0.0208, accuracy 0.9375, four decimals) by a setup the script rebuilds rather than imports. `tests/test_e122_checkpoint.py` makes it permanent: reload a checkpoint into a fresh module and require the runner's recorded loss, for every task at every checkpoint, shared and per-task decoder — **a key-list assertion would pass the moment somebody adds a trainable parameter and forgets it in the same way, so the test is the control**. **Registered next rather than claimed**: `retention_loss` has no granularity floor (**e118** measured the accuracy-based forgetting to 74–134% of its own value against the drift's 2.6–3.5%, with 1/240 as the structural half of the gap), so it is a candidate fix for the thirty-fold handicap — **but two seeds is not a distribution and at n = 2 the ratio points the other way** (1.8× apart in loss against 3.0× in accuracy), so the test is `e119`'s configuration re-run with the new key, 40 replicates at 128 and 300, one hour. Cannot settle: **nothing here was pre-registered and the criterion was not fixed in advance** (the barrier is read against the loss of a solution that has failed, which is the literature's convention, but *which* scale changes the sentence and only the chance level makes the answer "connected"); one seed pair (100 was the second replicate already on disk, not the pair with the largest gap), one read-out, one task order — read-out 32, where the spread is largest, is untested; **21 points can miss a ridge, so every barrier is a lower bound**; **the chords are through checkpoints rather than through minimisers**, so the four chords are four different objective functions and the first-task chord is the one that can be read; and it says nothing about *where* the retained loss comes from — the five failed trajectory quantities are still failed, and this fire replaces "many basins" with "one connected set, many interpolants" without measuring the selecting mechanism (`docs/findings/2026-09-24-the-seeds-solutions-are-connected.md`) |
| `e124_barrier_distribution.py`, 12 seeds, all 66 pairs, 21-point chords (`e124`) | C2b | **pre-registered before its run**: the one seed pair `e122` measured becomes the population — *"one seed pair, one read-out, one task order"* is the first weakness that finding lists, and its seed 100 was not chosen for the question but was the second replicate already on disk (`e124`) | **done — P1 HOLDS on all 66 pairs, the falsifier does not fire, C0 is BIT-IDENTITY, and the barrier turns out NOT to be the pairs' disagreement.** **Every one of the 132 pair-checkpoints has a fit-task barrier below 25% of chance**: min **0.0108**, median **0.0361**, max **0.1252** — so **the worst chord in the entire grid peaks at 12.5% of `ln 4`, a factor of 11.1 below the loss of a solution that has learned nothing**, and the median is **3.6%**, which is `e122`'s single pair almost exactly (0.05399/1.386 = 3.9%). **So `e122`'s pair was typical and not lucky, and the multi-basin explanation is dead for the population rather than for one draw**: the falsifier's threshold sits a factor of four above the worst of the 66. Two readings come free: **the median barrier grows with the number of tasks** (0.0284 after task 1 → 0.0445 after task 3, **1.57×**, which more interference should do) and **the distribution has a tail** — 26 of 132 chords (20%) within a factor of 2 of the worst, so pairs differ by an order of magnitude (0.011 to 0.125) and "every pair is below 25%" is true where "every pair is equally connected" is not. **C0 is bit-identity rather than agreement**: pair (0,1) reproduces `runs/e122_path_geometry.json` exactly (peak 0.05399 vs 0.05399, barrier +0.05217 vs +0.05217; 0.04394 / +0.04270 at the last checkpoint), the three saved checkpoints pass `e122`'s endpoint control **6 of 6**, and — a free extension control — **all twelve seeds reproduce `runs/e116_r128_40reps.json`'s first twelve bit-identically** (12-seed sd 0.0324 against the 40-replicate 0.0325), which also settles that this session's three `e8` additions are **recording** changes and not behavioural ones. **And the barrier is not the disagreement**: P3 as *registered* — the pair's fit-task barrier against its own forgetting difference (`abs(forgetting_i - forgetting_j)`), one point per pair — gives **r = +0.144 at 66 pairs** (2% of variance), and the third-worst chord in the grid (**400/600, 0.1138**) joins two seeds whose forgetting differs by **0.0104**, while the pair with the *largest* difference (700/1000, 0.1146) is fifth. **Which puts the barrier where the last five fires left the trajectory quantities**: drift, load-bearing gap, first-order term, second-order quadratic form, fit depth, and now the barrier's relation to retention disagreement — **six quantities measured and none of them orders or explains the forgetting**, while the geometry says the seeds' solutions are **one connected set** (`e124`), **not interchangeable** (`e122`: one seed's decoder reads the other's body 135× worse), and **nothing measured says which point of the set a seed lands on**. **The seeds' own numbers bound what "the spread" means at n = 12**: forgetting mean +0.0339, sd 0.0324, range **[−0.0312, +0.0833]** — an ordinary draw from `e116`'s 40-replicate distribution at this read-out (mean +0.0370, sd 0.0325), −2.1 to +1.4 sd — and **two of twelve have forgetting at or below zero**: seed 1000 is **−0.0312 with the best accuracy of the twelve** and seed 300 is exactly 0.0000 with the second-best, so the signed difference a "forgetting" is has a seed-dependent sign and a twelve-seed sample contains both. **All twelve fit the last task to 0.00118–0.00157**, reproducing `e121` on a disjoint seed block. **A DEVIATION FROM THE REGISTRATION, and the repair**: P3 as registered is one point per pair, and the script first computed the *retained-task endpoint loss ratio* instead — a different quantity on a different unit (**132 rows**), printed under the name `P3`, giving **+0.060 against the registered +0.144**. The agreement is luck, not vindication. Repaired in three parts: the registered quantity is computed and named (`p3_registered`); the substituted one is **kept and labelled as not the registered quantity** rather than deleted, because deleting it would hide the substitution instead of correcting it; and the script gained **`--reanalyse PATH`**, which recomputes the distributions and both P3 values from a stored artifact **with no training**, because the statistics are a function of the stored rows and scalars — the artifact on disk was corrected that way and its distributions are unchanged (min 0.0108, median 0.0361, max 0.1252 before and after), so the re-analysis is verifiably non-destructive. **A pre-registration whose statistic can be swapped and then quietly re-run is not a registration**, and the flag exists so that the next substitution costs one command rather than being invisible. Cannot settle: **one read-out** (read-out 32, whose per-repeat spread is the largest at 0.0556 against 0.0325 here, is untested — and since the drift, the gap and the fit depth are all monotone in the read-out, a barrier that is a property of the geometry *and* a monotone function of the read-out would be two claims where this fire supports one); **66 pairs are 12 observations** (each seed appears in 11, so the pair-level statements are exact only for those pairs and the effective `n` for anything about seeds is 12); **21 points can miss a ridge**, which is the safe direction for P1 and the unsafe one for the spread; **the tail is unexplained** (the worst chord joins a pair agreeing to 0.0104, and four pairs is too small a set to look for the cause); and it cannot distinguish "connected" from "connected and flat", since a straight-line maximum is a lower bound on the region's connectivity and not a characterisation of it. **AND THE CLAIM IS SCOPED TO A READ-OUT, WHICH THIS FINDING'S OWN REGISTERED REPLICATION THEN SHOWED BY FAILING** (`e130`, read-out 32): the identical grid puts **21 of the 66 final-checkpoint pairs above the 25% threshold**, the worst chord at **0.4419** of chance — a margin of **3.1×** below a solution that has learned nothing rather than **11.1×** — and the falsifier still does not fire. **The failure is entirely at the final checkpoint** (after one task all 66 pairs are below the threshold at both read-outs, maxima 0.1221 and 0.1342, a factor of 1.10) and the barrier's **growth with the number of tasks is 1.57× at read-out 128 against 3.98× at 32**, so the barrier is a property of the read-out **jointly with** the task count and **the narrowest read-out is the configuration in which the seeds' solutions come closest to being separated** (`docs/findings/2026-09-24-the-connected-set-claim-is-read-out-dependent.md`) |
| `e124_barrier_distribution.py` at **read-out 32**, 12 seeds, all 66 pairs (`e130`) | C2b | **pre-registered before its run**: `e124`'s own §6 names this as its first limitation — read-out 32 has the largest per-repeat spread on this axis (0.0556 against 0.0325) and the barrier there is untested; **`e124`'s thresholds reused verbatim**, so a failure here is a failure of a claim already in the record (`e130`) | **done — P1 FAILS, the falsifier does NOT fire, P2 holds by 4.91×, and the failure is confined to the checkpoint after three tasks.** **P1 fails**: **21 of 132 pair-checkpoints exceed 25% of chance**, all of them at the final checkpoint (**21 of 66**), against **0 of 132** at read-out 128; the worst chord peaks at **0.4419** of `ln 4`, i.e. **3.14×** below the loss of a solution that has learned nothing against **11.07×** at read-out 128. **The falsifier does not fire** — nothing reaches 50% — so "the seeds' solutions are one connected set" survives as a statement about *not crossing a wall*, with a margin that is no longer comfortable. **And the failure is entirely at the second checkpoint**: after the **first** task all 66 pairs are below the threshold at *both* read-outs, maxima **0.1221** and **0.1342**, a factor of **1.10**; after the **third** the gap is **3.53×** (0.1252 against 0.4419). So **the read-out's effect on the barrier appears only as tasks accumulate**, and the barrier is a property of the read-out **jointly with** the task count rather than of either alone. **P2 holds and harder than registered**: stated as a direction only, it comes out at **3.2×** over the whole grid (median 0.1157 against 0.0361) and **4.91×** at the final checkpoint — and **P2 holding is what makes P1's failure interpretable rather than merely negative**, since the two predictions answered different questions (*"is every pair connected?"* and *"does the barrier grow where the seeds differ most?"*) and the answers are **no** and **yes**, which is the ordering the geometry predicts; a fire that had registered only the first would have reported a refutation with no idea. **Controls**: C0a the extension control is **bit-identity** (twelve seeds against `runs/e116_r32_40reps.json`'s first twelve, max ABS difference **0.000e+00**) — and it was **built into the script** for this fire as `--matching-seeds`, on the ground that a control run by hand afterwards is a control that gets skipped; C0b passes **6 of 6**; and **P3 replicates its null with the opposite sign** (**r = −0.108** against read-out 128's **+0.144**), which is the honest form of a second null since two near-zero correlations of opposite sign are two samples of nothing. **What it changes in the record**: `e124`'s P1 is **restated as read-out dependent**, the finding and the paper's §4.2 paragraph are corrected in place with the date, and **the design statement gains a condition** — a practitioner choosing the narrowest read-out is choosing the configuration in which the seeds' solutions come closest to being separated, at a factor of 3.1 rather than 11. **It does not become a multi-basin result**: the falsifier was registered at 50% and nothing reached it, so the claim is **qualified, not overturned**. Cannot settle: **two read-outs is a line and not a curve**, so P2 holding does not separate "the barrier is a property of the geometry" from "the barrier is monotone in the read-out" — read-out 0 is the third point and is now load-bearing rather than hypothetical; **the threshold's location is a choice** (25% was registered in `e124` and reused verbatim, which is what makes this a replication, but a reader who thinks the line should sit at 30% or 40% reads the same numbers as a pass, which is why both the count and the magnitude are printed); 66 pairs from 12 seeds remain heavily dependent; and **21 points per chord can miss a ridge**, which is the safe direction for the connectedness claim and the unsafe one for the size of the worst pair (`docs/findings/2026-09-24-the-connected-set-claim-is-read-out-dependent.md`) |
| `e123_loss_metric.py` over `--test 480` at read-out 128, 40 replicates, with `retention_loss` recorded (`e123`) | C2b | **pre-registered before its run**: the loss-valued retention matrix is continuous where the reported metric has granularity **1/240** — so does re-expressing the forgetting in nats remove the **thirty-fold** handicap `e118` measured against the drift? (`e123`) | **done — C0 is BIT-IDENTITY, the registered predictions FAIL, the falsifier FIRES, and the honest verdict is that the loss metric buys NOTHING — while the reason it looked worse turns out to be the units, and `e118`'s granularity diagnosis is measured and refuted as the explanation.** **C0 passes exactly**: the per-repeat accuracy forgetting equals `e119`'s forty replicates with **max ABS difference = 0.000e+00** and identical per-task rows, so recording `retention_loss` in the loop changed what is *recorded* and nothing about what is *trained*. **As registered**: P1 (`sd_loss/sd_acc < 1`) FAILS at **2.163**, P2 (`< 0.71`) FAILS, and the falsifier (`>= 1`) **FIRED** — the loss-valued matrix is 2.16x *noisier* than the metric it was meant to improve, and the falsifier's own stated consequence follows. **But that ratio divides 0.04790 nats by 0.02215 accuracy** — two different units — and **the registration contradicts itself in saying so**: P3 states that the claim *"is about the precision of each quantity against itself, never about agreement between them"*, while P1 and P2 are written as a cross-unit sd ratio. Read the way P3 says it must be: accuracy **0.04021 +/- 0.02215 → 55.1%**, loss **0.09561 +/- 0.04790 → 50.1%**, so **relative-sd(loss)/relative-sd(accuracy) = 0.910** — the loss is **9% better, i.e. the same thing**. Both readings agree on the verdict (*no improvement*, since 0.91 is nowhere near the registered 0.71), which is why the conclusion survives the flaw in the threshold, but **a cross-unit threshold that reaches the right verdict is still a threshold that should not have been registered**. **And the granularity floor is real, measured, and irrelevant** — the direct test of `e118`'s *mechanism* rather than its conclusion: the accuracy forgetting takes **30 distinct values of 40** replicates and the loss-valued one takes **40 of 40**, so the floor exists and the continuous quantity breaks it; removing it moves the relative spread by **9%**. **The two metrics rank the seeds almost identically** across the forty replicates (**r = +0.785**, Spearman **+0.800**, the log-ratio companion +0.695), so the finer scale carries no different signal. **Which refutes the granularity diagnosis as the explanation of the handicap**: the floor was there, was removed, and did nothing — so the eighteenfold gap against the drift is **intrinsic to the QUANTITY**, not to its estimator. "How much did this task's retained performance change" varies between seeds by about half its own value whether measured as an accuracy, an absolute loss, or a log ratio, and **no re-expression of a coarse thing is more precise than the thing it re-expresses** — which is a stronger form of §4.7's sentence than the project had. **Four corrections to my own analysis, each found by auditing it against the runner**: (1) the cross-unit threshold above; (2) **the wrong window** — the registration wrote the accuracy forgetting as `max_{k in [j,T-1]}`, and the runner computes `nanmax(R[:j+1, j])`, the window **0..j** (`experiments/e8_rate_network.py:517`); the implementation mirrored the mis-statement and the two windows differ by up to **0.0073 per replicate**, and fixing it moves the accuracy side from 53.5% to **55.1%** and the ratio from 0.937 to **0.910** — while leaving the **loss side identical under both windows**, because a task's loss is lowest at `k = j` and high at every earlier checkpoint, so the window cannot affect it; (3) **`sd/mean` on a log scale is an artifact** — the first version reported the log-ratio's precision as **12.6%**, which read as four times *better* than either metric and is meaningless, since adding 10 to every value divides it by five; the invariant form is multiplicative, **exp(sd) = 1.64x**, i.e. slightly *worse* than both linear forms, and the general lesson is that **a "relative" precision is only comparable on a linear scale**; (4) both sides of a paired comparison must be computed the same way, which (2) is an instance of and which is why the fire's numbers changed *after* the run — from a re-analysis of the stored artifact rather than a re-run. Cannot settle: the registration names read-out 128 **and 300**, and only 128 has run (the 300 arm's comparison is within that run, needing no comparator, but a ratio of 0.91 at one read-out is a point rather than a law); the loss is measured on the **training** split, whose 96 samples every seed interpolates (`e121`), so its sampling floor is not removable by a bigger test set and the ratio is a comparison of two precisions rather than the variance decomposition `e119` made; three tasks means the forgetting averages **two** numbers per replicate; and nothing here says the accuracy metric is the right one to report — only that its cheapest replacement is not. **AND THE REGISTERED SECOND READ-OUT REPLICATES IT**: read-out 300 (40 replicates, `--test 480`, C0 **bit-identical** to `runs/e119_r300_test480.json` with max ABS difference **0.000e+00**) gives accuracy **69.9%** and loss **63.5%** relative — worse than 128's 55/50% because read-out 300's forgetting is smaller (0.0269 against 0.0402) — with a **relative-sd ratio of 0.908 against read-out 128's 0.910, agreeing to 0.002**, and the falsifier firing again. So the stability is in **the ratio between the two estimators**, not in either one's own precision, and "about 9% better in relative precision" is now replicated rather than a point estimate (`docs/findings/2026-09-24-the-loss-metric-buys-nothing.md`) |
| the two-point comparison of `e116` (test 48) against `e123` (test 480), same 40 seeds (`e128`) | C2b | **analysis, no runs**: `evaluation_noise` reports a *nominal* removable share, and the two artifacts differ in exactly one config field — so what share is **achievable**? (`e128`) | **done — the nominal share is 85% and the achievable one is 29%, the paper's `2.6x` was stitched from a second artifact, and the explanation belonged to the other quantity.** **The pair is clean**: `runs/e116_r128_40reps.json` and `runs/e123_r128_test480.json` differ in **exactly one config field**, `test` (48 against 480), with the same 40 seeds — verified field by field. The nominal binomial sem falls **2.98×** against the 3.16 a genuinely independent tenfold set gives, so **the formula is internally consistent**, while the accuracy's per-replicate sd falls only **1.163×**; a 85.3% removable share with a tenfold test set predicts **2.07×**. **Solving the two equations for the one piece the pair can identify** — taking the training component as constant — gives an effective binomial sem of **0.01229 against a nominal 0.02109** (1.72× smaller), i.e. **an effective 49 independent held-out decisions rather than 144, and an achievable removable share of 29% rather than 85%**. **The runner's own else-branch had carried that caveat as a clause since it was written** — *"a fraction above 100% is a signal, not a number … or the 144 held-out decisions are not independent"* — and this is the first time it is measured rather than invoked. **And the section's explanation belongs to the other quantity**: it attributed the over-prediction to the *difference* of two accuracies, but the forgetting's removable component **does** fall by √10 — *because the 60% split was solved for by assuming it, which makes that a tautology rather than a test* — while the **single accuracy's** directly-computed 85% is the one that fails, predicting 2.07× against a measured **1.16×**, so **the correlation between two accuracies is not the mechanism and the mechanism is upstream of it, in the held-out decisions themselves**. **And the paper's `2.6x` never followed from its own `85%`**: 2.6× needs a **94.7%** share, and 0.9467 is `runs/e102_rate_fb8_omp1.json`'s **0.9461** — an artifact at **read-out 32 with five replicates** against the **read-out 128 / forty** the 85% comes from, so **a sentence paired a statistic from one run with a prediction computed from another's**. That is rule 28's *"a column whose comparator is not one number"* **in prose rather than in a table**, which is why `e97` (artifact existence), `e105` (table closure) and `e126` (counts) all passed it and why it survived from `e119` to this fire: **both halves are real numbers from real artifacts and neither is wrong on its own**. **The check is the cheapest kind and needs nothing on disk — recompute the stated prediction from the stated input**, one line for any `f`; the corrected arithmetic is **2.07×**, and the honest sentence is one line shorter, since the forgetting's 1.47× is definitional and there is no contrast between the two to report. Repaired in the paper and dated in the source finding. **Which strengthens rather than weakens the section's conclusion**: if only 29% of the accuracy's variance is removable at all then `e119`'s tenfold test set captured **even more** of what was available than its 94% said, the test-set route is **more exhausted** than it looked, and the residual is even more clearly the substrate's. **AND IT REPLICATES AT A SECOND READ-OUT, WHERE THE NOMINAL MODEL GIVES UP ENTIRELY**: the pair `runs/e115_r300_40reps.json` (test 48) against `runs/e123_r300_test480.json` gives an effective binomial sem **2.07×** smaller than nominal, an effective **n_eval of 33.5 against a nominal 144**, and an **achievable removable share of 26%** — and there the nominal model is not merely optimistic but **incoherent**, because `variance_fraction = 1.1165`, i.e. the binomial sem it computes (0.01983) **exceeds the observed per-replicate sd** (0.01877), which is exactly the case the runner's own else-branch prints as *"this run cannot separate them"* rather than as a number, and why the sd fall it predicts is **undefined rather than a number**. **The two-point solve is well-posed anyway** because it never uses the nominal sem as an input — only the two observed sds and the one fact the design licenses, that the sampling component falls by √10. So **the nominal block fails in two different ways at two read-outs, optimistic at 128 and incoherent at 300**, and the removable share is **unknown from the block alone and measurable from a pair** (`docs/findings/2026-09-24-the-nominal-removable-share-is-not-the-achievable-one.md`) |
| `e127_programme_table_audit.py` over the plan's programme table (`e127`) | C2b | **analysis, and it makes rule 22's check executable** — the check that found eight stale rows in `e85` and three self-contradicting ones in a later pass was run **by hand both times** and was never code, which is the condition that produced four drifts in the same direction (`e127`) | **done — the table passes all four mechanical checks, and the first automated pass found a broken row in the very table it audits, added to that table earlier in the same session.** **86 rows parsed, 78 carrying a status indicator**, and four checks, one per documented failure mode: **(A)** every `runs/*.json` the row names exists — **0** flags; **(B)** no status cell announces itself as open and then reports an answer — **0**; **(C)** no two rows share a first cell — **0**; **(D)** no row contains a raw pipe in a cell — **0, after one repair**. **The repair is the finding**: the `e124` row added to this table earlier in this same session contained an absolute-value expression written with two BARE PIPE CHARACTERS inside a code span, and in a GFM table a literal pipe separates cells **unless each pipe is escaped with a backslash, and that holds even inside backticks** — so the row rendered as **two** rows and broke the table between them for every reader. **None of this project's audits could have caught it**: `e97` reads artifact existence, `e105` reads a table's arithmetic, `e126` reads counts, and the numbers here were all correct — a broken row is a claim about the *table* rather than about the values in it. **And it was introduced by the same session that then audited it**, which is the ordinary case rather than a coincidence: the table is edited by whoever is working, and nobody re-reads a rendered version to check a row is still one row. **Three false-positive classes, all of which would have made the checker worse than nothing**, per rule 22's own last paragraph: (1) **it split rows on every pipe**, so a correctly-escaped absolute-value expression was reported malformed — one false alarm and no catch on its first run — and the split now respects the backslash escape while the reported context centres on the first pipe *beyond* the row's five structural borders (centring on the fifth showed the row's own trailing border and nothing else); (2) **it flagged "an open word after a done marker" as a contradiction, and fired on 9 of 9 rows as false positives** — every one a status cell reading `done — …` with the word "launched" or "PENDING" in later **prose about a different experiment**, including the row whose own correction note quotes the phrase it was being flagged for; this is the failure rule 22 already had on record from its manual passes, reproduced exactly by the automated one, so it is now **counted as a denominator and never as a finding**; (3) **artifacts named in the `why` column were never checked** — the search covered `what` and `status` only, and `why` is where a row says what closed a gap, so a row citing its gap's artifact there would have had check A report **zero while skipping it**, which is the failure mode where a checker's silence looks like coverage; a test caught it. **Two more came from the tests rather than the corpus**: the column header and the all-dashes separator row were both being counted as data rows (the separator's own cells contain pipe characters, so the skip condition never fired), and a test that hard-coded a line number had assumed the wrong table offset. Cannot settle: **check B is a word test and rule 22's fourth failure is not a word** — four rows marked done while summarising a number the project had since overturned, where the status word is right and the *number* is stale, needs the result re-derived from an artifact and **nothing does that for this table's prose**; the self-contradiction rule has a **false-negative side**, since *"print the opening of each status cell beside the end of it and ask whether they agree"* is a **reading** instruction and a machine can only compare keywords, so a cell that opens `done —` and closes with a retraction of its own opening passes; **C is a text match** on the first cell, so two rows describing one piece of work in different words are not caught; and the four checks are the four documented modes, so this is a claim that the table is **self-consistent**, never that it is right (`docs/findings/2026-09-24-rule-22-had-no-code.md`) |
| `e126_enumeration_audit.py` over the paper, the plan and the whole findings corpus (`e126`) | C2b | **analysis, the first check here that reads a document's own claims about its own shape** — every other audit reads numbers (`e97` artifact existence, `e105` table closure, `e103` arm re-execution) (`e126`) | **done — two defects had been in the paper for two days, and a third was found on the way; the corpus is now clean at this audit's precision.** **(1)** §7's trap list heading said **"Five measurement traps" over four bullets**, and `git log -S` dates it exactly: commit `1743573` rewrote *"Two measurement traps"* to **"Five"** while adding two bullets to the two that were there, so it said five and listed four from the day it was written — **and that commit's message is about stale aggregate statements**, so the defect it was fixing was committed in the fix; repaired to **six** with the two traps this session found (a saved state can omit a parameter and the omission is invisible until something is recomputed from it; a run compared with a copy of *itself* is still a contrast across code epochs). **(2) And the mirror image, which is worse because it is a self-contradiction rather than a stale number**: §4.3 said at line 666 *"All eight ladder rungs now have a measured draw sd of their own"* and fourteen lines later at 681 that the column *"is a floor, since three of its eight rungs have no measurement of their own"*. `runs/e73_ladder_named_head_to_head.json` decides it in one field — **`n_ladder_measured` = 8 of `n_ladder` = 8**, every one of the eight rows carrying `draw_sd_measured: true` — so the abstract and 666 are right and 681 was stale, written when five of eight were measured and missed by **two** later commits that corrected its sibling paragraph and its abstract twin. **The tell that needed no tooling: the stale clause quoted the post-`e74` range (2.6–13.7σ) while giving the pre-`e74` reason**, a sentence internally inconsistent with itself. Repaired to name `e74` (the last three) and `e90` (the pair that had been *borrowed*, since `pool32` and `pool64` are the same partition at d = 1307) — a detail the abstract's "all eight" also glosses. **(3)** §4.3's σ table printed `pool4` at **42.2σ** with no marker while the abstract warns it "overstates it several-fold"; it now says in place that the column is against zero with a seed-only sem and an assumed 1.0e-3 draw sd, that the corrected column is **2.6–13.7σ** (a **3.1×** overstatement at the best rung) and that the head-to-head moves from an order of magnitude to a factor of **1.9** — §9's own rule that naming the command behind a superseded number is worse than naming none. **Checked and correct, which is most of it**: the abstract's **"Thirteen"** retractions (12 top-level entries plus one nested in a parenthesis, and the sentence's own "the thirteenth is the one whose number survived" matches the last entry); **§4.2.1's "four attempts"** against its four bullets; and **§4.2.1's "six further experiments"** against nine cited ids — left alone rather than rewritten, because all nine ids are real and the counts reconcile, but the record does not let it be *verified* and rewriting an unsourceable count would be worse than a loose one. **The audit's four failed designs are recorded in its docstring**, because each is a way a checker is worse than nothing: matching any number-adjacent-to-a-list gave **~40 mismatches of which not one was real**; counting a numbered list like a bulleted one read the abstract's four findings as three (the mismatch was *manufactured*, and the repair is that for `1. 2. 3.` the numbering is the document's own length claim, so a block not starting at 1 is a mid-list fragment and is skipped); widening the lookback let the §7 correction note's own phrase *"adding two bullets"* claim 2 over a six-item list; and the residual two false alarms came from crossing a section heading. **Two more bugs were caught only by the test suite** — `CLAIM_RE` had been tightened until it could no longer match *"Five measurement traps"*, so the checker had stopped catching the defect it exists for while still reporting a clean corpus, and Markdown's lazy-continuation rule was missing so the paper's item 3, whose wrapped tail lost its indent, read as three items. Result: **166 documents, 9 count claims found next to a list, 9 matched, 0 mismatches, 0 numbering holes, 205 ratio phrases reported as not-checked**, with the denominator asserted in the test suite (`found >= 5`) because a checker that finds nothing passes every silence test. Cannot settle: it reads **one** pattern, so a stale count buried mid-sentence — `e125`'s cited experiment list, §4.2.1's "six further experiments", `e97`'s own denominators, which is most counts in this corpus — is invisible to it; the 17-noun lexicon is a judgement and a defect whose noun is missing will be missed **silently rather than reported as unchecked**; it cannot distinguish "Two things worth noting" over four bullets (not an error) from "Five measurement traps" over four (an error), which is why it needs the opening rule and the heading rule and will still be wrong somewhere; and it only says a document **agrees with itself**, never that the stated count is the right one (`docs/findings/2026-09-24-the-paper-counted-its-own-bullets-wrong.md`) |
| `e8_rate_network.py` --frozen-body at read-out 0 / 128 / 32, and `--methods naive,ewc` at the two upper settings (`e104`) | C2b | **the cheapest repair the control audit identified**: fill the cells that match no artifact, rather than arguing about them (`e104`) | **done — and the unbacked claim was largely RIGHT, which the record could not have told anyone.** Read-out **0 / 128 / 32**: plastic acc 0.9333 / 0.9333 / 0.9139 with forgetting **+0.0479 / +0.0333 / +0.0729**; frozen acc **0.9444 / 0.9167 / 0.8139** with forgetting **+0.0000 ± 0.0000 at all three** (fifteen replicates agreeing to the last digit — structural, not small). So **the frozen accuracies reproduce the claim to three decimals** (0.944/0.917/0.815), **the gap is monotone** (−0.0111 → +0.0167 → +0.1000) with the whole-state end point **negative** rather than +0.007 — small, unresolved, and on the side that *strengthens* §4.2's principle — and **one half is refuted**: the plastic forgetting series was printed monotone (+0.021 → +0.035 → +0.066) and measured the 1307 → 128 step **falls** (+0.0479 → +0.0333), below the whole-state level, which a strictly rising series cannot be. **The sweep also validates itself**: its read-out-32 plastic row *is* the hardened configuration's `naive` and reproduces `e8_hardened_basis` to the last printed digit. **And the two EWC cells both say tie**: task-IL **+0.0000** (the claim said EWC was *worse* by +0.027) and class-IL **+0.0042** (the claim said +0.004), so "EWC resolves in exactly one setting" is now measured for three settings rather than asserted for two. **A third instance of this session's process-dependence came with it**: each upper setting's `naive` takes two values in two processes (task-IL +0.1062 / +0.1000; class-IL +0.0437 / +0.0688) while the paper printed a third (+0.101 / +0.059), and `e104`'s class-IL `naive` is **exactly** the stored `e8_class_incremental.json` value, so that execution re-landed in the configuration's original environment. §4.4's table is therefore rebuilt **one row per execution** with empty cells where a run did not measure an arm, because a single `naive` column above two contrasts from two processes is the §4.2 defect in a new place. **And the price is the point**: the repair was eight executions of a few minutes each, which is what the control audit predicted ("the cheapest repair available in this project and the reason it should be run rather than argued about") — so **an unbacked number is not thereby a wrong one, and the way to tell costs minutes** (`docs/findings/2026-09-23-the-unbacked-cells-measured.md`) |
| `e87_paired_co_movement_bootstrap.py` | C2 | resample the unit that is actually shared — the draw, not the partition — in the two comparisons that used a nine-partition sign record | done — `runs/e87_paired_co_movement_bootstrap.json`. **It corrected one of my own claims and upheld the other.** For `e82`'s size steps the draw interval is **4.0× the partition sem** and both comparisons include zero, so "3.29σ decay with eight of nine partitions declining" becomes **0.75σ, [−0.3110, +0.1468]** — the sign pattern was exactly what a shared-draw effect produces. For `e81`'s paired `pressure − alignment` the interval is **2.31×** the partition sem and **excludes zero**: **+0.7364, [+0.4184, +0.9808] = 5.15σ with 100% of 4000 resamples above zero**. **The difference is the design, not the subject**: a comparison of two *runs* has no protection, while a comparison of two quantities measured *on the same draws* has partial cancellation. Rule 23 records the guard |
| `e75_task_pair_spread.py` re-run | C2 | `e88` — the alignment values the `e81` paired check needs, which `e75`'s artifact does not carry | done — `runs/e88_alignment_perseed_rerun.json`, reproducing `e75`'s *r* to three decimals on all nine partitions with `side` differing by 0.001 (rule 21's fourth-digit thread sensitivity, and a different `OMP_NUM_THREADS`). **The lesson is that fixing a script does not add fields back to an artifact already written**: `e75`'s output filter was removed the day it was written, and the check still could not run until the *run* was repeated |
| `e3_basis_selection --circuit-size 1500 --ladder` | C2 | per-seed storage for the **d = 1874** granularity ladder (`e79`), the second configuration of the headline family | done — `runs/e79_ladder_d1874_perseed.json` (17 of 18 bases carry `excess_per_seed`; the 18th is `_abs`). **8 of 8 rungs are unanimous over 12/12 seeds**, no leave-one-out removal flips any, smallest LOO σ **9.0**, largest leverage **0.67** — against d = 1307's 7 of 8, 6.6 and 0.80, so the second configuration is the *more* robust of the two. **And `pool1`'s disadvantage replicates**: +0.00035 at **9.85σ paired**, 12/12 positive, which is the first independent confirmation of `e66`'s reversal that the finest granularity is a reliable disadvantage rather than a null. The crowding repeats too: `bio:pool64 ≡ bio:pool128` (identical `constrained_fraction`, `n_parameters`, excess and pressure) **while their controls are separate draws**, differing by 0.00073 ≈ one measured draw sd — the same structure as `pool32 ≡ pool64` at d = 1307, which is where the whole draw-spread line started. `e57` now takes `--artifact` so both ladders get identical treatment. Caveat: the draw sds in `e57`'s part 2 are d = 1307 numbers, so its ratio at a second size is a cross-size comparison and is **computed and flagged** rather than asserted |
| `e12_control_spread.py --column cell_type --min-size {8,16,128}` | C2 | the three ladder rungs whose draw sd had never been measured (`e74`) — the floor under `e73`'s head-to-head | done — `runs/e74_drawsd_min{8,16,128}.json` at `e14`'s own protocol (3 seeds, 5 draws), so the new points sit beside the old ones. **All three came in *below* the 1.0e-3 the tables assumed** — `pool8` **7.07e-4**, `pool16` **6.68e-4**, `pool128` **9.65e-4** — so their σ(rule) *rose*: 6.7 → **9.3**, 7.5 → **11.0**, 4.0 → **4.1**. The e73 head-to-head is therefore a measurement on both sides rather than a comparison against a floor, and the factor stays **1.9×** |
| `e12_control_spread.py --column cell_type --min-size 32` | C2 | the last **borrowed** draw sd in the ladder's column (`e90`): `pool32`/`pool64` | done — `runs/e90_drawsd_min32.json` at `e14`'s protocol. **`pool32` and `pool64` are the same partition at d = 1307** (both pool `cell_type` to 3 groups, verified directly), and their own spread is **7.41e-4** where the row had been using `e14` min 2's **9.29e-4** — 25% too high, because the borrowed value came from a *different partition* at a similar concentration, which is exactly what `e67` refuted the concentration scalar for. Their σ moved 7.4 → **9.1** and 5.7 → **7.0**, the ladder's series is now 2.6 / 8.1 / 13.7 / 9.3 / 11.0 / **9.1** / **7.0** / 4.1, and **no number in the head-to-head is borrowed any more** |
| `e6_predictor.py --seeds 6` with per-seed rows | C2 | per-seed storage for the predictor's matched pairs (`e64`), the **last** headline number without one | **relaunched after a caught failure.** The first launch was killed at 73% (4,433 s) because `e6`'s `run_condition` did not copy `excess_per_seed` into its rows: the artifact would have looked complete and reproduced `e6_predictor_6` exactly while proving nothing per seed. The field is now carried through, and `e64_predictor_per_seed.py` **refuses to run** on an artifact without it rather than reporting pooled numbers as if they were per-seed. This is rule 8's cousin: *check that the artifact will contain the field the question needs*, not just that it will exist |
| `e73_ladder_named_head_to_head.py` | C2 | the ladder against the named rungs on the SAME footing — paired sems and measured draw sds on both sides | done — the paper's comparison was apples-to-oranges (the ladder used unpaired sems and an *assumed* 1.0e-3 draw sd). On one footing the ladder's σ(rule) are 2.6 / 8.1 / **13.7** / 6.7 / 7.5 / 7.4 / 5.7 / 4.0 and the named family's 18.1 / 12.1 / 3.8 / **26.1** / 13.3: **26.1 against 13.7, a factor of 1.9, not an order of magnitude** — and three of the ladder's eight rungs carry an *upper* draw-sd estimate, so its column is a floor. The pairing gain is what made the two tables incomparable: **0.9–1.1×** across the ladder (except `pool1` at 19.6×) against **1.1–27.3×** across the named rungs. Measuring the three missing draw sds (`e12 --column cell_type --min-size {8,16,128}`) is the obvious completion |
| `e8_rate_network --replay-per-task 96 --replay-batch 8 --repeats 16` | C2b | does the recreated result survive the discipline that killed `e46`? (`e68`) | done — **it survives**: the paired contrast is **−0.06771 ± 0.01006 = 6.73σ on forgetting with 16/16 signs agreeing** and +0.03776 ± 0.00591 = 6.39σ on accuracy, LOO minima 6.2 and 5.9. Against 6.61σ at five replicates, so the effect neither collapsed nor grew. **What weakened is the absolute claim**: replay's own forgetting is **0.83σ from zero at sixteen against 3.21σ at five.** One caveat that scopes it: `e68` ran under `OMP_NUM_THREADS=4` and `e61` did not, so this is a *separate sample* rather than a nested extension — see the `e77` row |
| `e77_thread_determinism_probe.py` | — | is the project reproducible across runs and across thread counts? | done — **the network line is not; the analytic line is, to four digits.** `repeats` is inert (3-vs-4 agree on their first three replicates) but `OMP_NUM_THREADS` is not: the same command gives 0.875/0.902778/0.909722 at default threads against 0.826389/0.840278/0.930556 at 4 — **zero of three values shared**. The analytic path (`e12_control_spread`) is sensitive too but only at the **fourth significant digit** (max relative difference 1.8e-4 on a per-seed excess, 9.3e-7 on an aggregate delta), against the tightest sem the project quotes (1.29e-5) that is **40× of headroom**, so no conclusion moves. What must change is the language: **"bit-for-bit" is wrong and should read "identical to about four significant digits given an environment"** — `e62`'s and the paper's reproducibility checks included |
| `e5_anisotropy_axis.py --seeds 12` | C1 | `e5` re-run with 12 seeds (`e42`) — the binding test for the replacement mechanism | done — **the direction is REVERSED on the prescribed metric**: 9 positive / 2 negative / **1 tied**, mean +0.265, sign p = **0.0654** (ties dropped; an earlier 0.0386 was my error), pooled +0.228 (p = 0.037); on the relative gap the same seeds say nothing (7/5/0, p = 0.77). Seeds 0–2 reproduce the published artifact exactly |

Every figure carries its control arm, and every recall/precision number in this document
carries a resolvability check. The prediction scoreboard, including the refutations,
lives in `docs/findings/`.

## Method

Research here runs as a bounded, measured loop: one metric, constrained scope,
automatic rollback, git as the record. Phase 1's gate was `repro_max_abs_err`,
now closed at 4.7e-5.

Two rules that keep the loop honest:

1. **The oracle stays in.** Every experiment keeps the Kalman/RTS reference line,
   so "better than the baseline" can always be read as a fraction of the gap that
   actually exists.
2. **Failures ship.** The Phase-1 negative result (no unimodal peak in the
   coordinate basis) is in the findings log with the same prominence as the
   successes, because it is what redirected the programme.

### Measurement rules

Added 2026-09-22, after the headline metric was found to be chaotic
(`docs/findings/2026-09-22-metric-instability.md`).

3. **Do not report the relative gap bare.** On the connectome substrate EWC's
   relative excess over the oracle has a standard deviation comparable to its own
   mean — up to 1.38 across seeds at *fixed* settings — and moves by ±0.04 under a
   **1e-15 relative** change in the spectral radius. It is a ratio of two small,
   close numbers, so it inherits the EWC estimator's full relative variance.
   Report `clfly.bench.oracle.paired_excess`: the **absolute** excess with its
   standard error across >= 3 seeds, plus `gap_of_means` if a ratio is wanted.
   At current settings, excess differences below ~0.05 are not resolvable.

   > **Measured at n = 12 (`e55`), and corrected in two ways.**
   >
   > **The stated reason is not diagnostic.** The absolute excess's across-seed CV is
   > **0.70–1.26** at the seven κ values, against the relative gap's **0.73–1.15** — the same.
   > What the absolute metric fixes is the *ratio-of-two-close-numbers* pathology (the 1-ULP
   > sensitivity and the 1.38 CV), **not the across-seed spread**. A reader who takes this rule as
   > "the absolute excess is more stable across seeds" is wrong by a factor of one.
   >
   > **The 0.05 is stale and is the wrong kind of number.** The across-seed sd of the absolute excess
   > has a median over κ of **0.01971**, so the unpaired minimum detectable difference (2.8 × sem,
   > 80% power) is **0.0159 at n = 12** and **0.0319 at n = 3** — 3.1× and 1.6× below the quoted 0.05.
   > **But the project's contrasts are within-seed differences**, where the same measurement on `e48`
   > gives **0.00100** — and *not* because pairing cancels much (the arms correlate at only r = +0.29),
   > but because the *difference* is stable relative to its signal while either arm is comparable to
   > its own mean. So this rule needs a **pair** of numbers with the comparison named: the basis deltas
   > the neuron ladder resolves (0.0015–0.0040) look unmeasurable against 0.0159 and are comfortably
   > resolved against 0.0010.
   >
   > **And attach the configuration.** `excess(real)` at cs = 800 has an across-seed sd of 0.01971 in
   > `e5`'s uniform-drive sweep and **0.00175** in `e2`'s default-drive run — the same topology, circuit
   > and seed count, differing in the task construction. "At current settings" covers an 11× range.
   > (`docs/findings/2026-09-22-the-resolution-figure-is-stale-and-wrong-shaped.md`)
4. **Pin the spectral radius, and report it.** `stable_weights` must use a
   deterministic ARPACK start vector. With the default random start, `W` differs by
   1 ULP between identical calls and the reported gap moves by several percent.
   This was a real bug, found and closed.
5. **Geometry is safe; realized errors are not.** Quantities computed from
   eigenvectors (task overlap, effective rank) are bit-reproducible. Anything built
   from a realized estimation error is not. Prefer geometric statements.
6. **Watch for range-space degeneracy.** Taking the top-`rank` subspace of a
   rank-`rank` matrix returns its entire range space, which for these tasks is
   determined by support *membership* and is blind to how strongly each neuron is
   driven. A predictor built on it cannot see spectral structure — the most likely
   reason the principal-angle alignment scalar failed in `e3`. Use
   `task_subspaces(..., top=k)` for a spectrally selected subspace.
7. **"Resolves from zero" is not "differs from its neighbour".** A claim about the
   *shape* of a curve — where an optimum sits, whether an advantage is monotone —
   needs contrasts between the curve's own points, not a per-point σ against zero.
   Contrasts must be **paired on the seed**, since every base in a run sees the same
   task geometries in the same order: use `clfly.bench.analytic.paired_delta` and
   `contrast_of_contrasts`, which report the seed correlation ρ and both sems. The
   quadrature figure is not a bound — a matched difference has variance
   ``sd_a^2 + sd_b^2 − 2ρ sd_a sd_b``, so it is the *larger* one when ρ < 0. And
   order the points by granularity before contrasting them; an alphabetically sorted
   table makes "adjacent" meaningless.
8. **Store per-seed values.** A pooled mean and sem cannot be re-analysed paired,
   and re-deriving a two-hour run to recover them is avoidable: `analytic_excess`
   records `excess_per_seed`. `--report-from <json>` re-prints any finished run's
   report without recomputing it.
9. **Time the pieces before calling a configuration untestable.** Twice now a
   scientific conclusion rested on an implementation artefact — a benchmark that
   measured its decoder, and a "coarse rungs are too slow" reading that was 4×
   redundant work inside the step loop (a constant Fisher re-converted from numpy
   on every step; `SynapsePartition.make_penalty` binds it once per task instead).
   When something is too slow to run, profile it before concluding the science is
   expensive. Related: a module with no tests hid a dtype crash one argument away
   — the penalty was one float64 anchor from raising.
10. **A matched-random control must be averaged over draws.** The control is the
   *population* of size-matched random partitions, and one draw is one sample from
   it. The draw-to-draw sd is ordered by the partition's **concentration**,
   ``sum_g s_g^2 / d^2`` (`clfly.bench.control.concentration`), **not by its group
   count**. It is a **coarse/fine** axis only: on d = 1307 the coarse range
   0.325–0.678 measures 6.1e-4 to 1.06e-3 draw sd with no ordering — 1.01e-3 at
   0.395 against 6.1e-4 at 0.459, a non-monotone 40% swing between two runs of the
   same experiment — and the level differs between circuits (4.9e-4 at d = 952
   against 1.06e-3 at d = 1307, at the same concentration near 0.7). A group
   count gets `side` exactly backwards — 4 groups but a concentration of 0.498,
   so it belongs with the coarse partitions. Concentration 1.0 means a single
   group, i.e. the `Full` basis with excess exactly zero — at d = 952 two ladder
   rungs are that, so they are not granularity points at all. **For a budget,
   use ≈1e-3 for any coarse rung rather than an interpolation**: it is the top of
   the observed range, so it overstates the required K rather than understating
   it. The interpolation is nevertheless usable when a measurement is unavailable,
   but its error is not bounded: four columns measured so far give ratios of
   1.15×, 1.18×, 1.26× and **2.0×** (`supertype`). Where the draw term dominates —
   the coarse partitions — the error has been 15–26%; the 2× case is a fine column
   whose seed sem is an order of magnitude larger than the draw sd, so it does not
   matter there. The two failure modes are disjoint, which is why a constant budget
   and a seed-dominated fine column are both safe, and neither should be assumed of
   the other. Where the draw term
   dominates, a single-draw σ overstates the evidence several-fold: coarse-rung σ
   in the basis study are provisional, `pool4` 42.2σ → ≈8.7σ with the component
   included, and `pool2 → pool4` (the plateau question) 2.2σ → ≈0.6σ. Report the
   two components separately, and never rest a claim about a curve's *shape* on
   single-draw controls. The paired column needs ≥12 seeds to be usable: at 3
   seeds the sample correlation hits ±1.00 by chance and σ_p disagrees with σ by
   up to 3×.
11. **Artifacts are strict JSON.** Non-finite floats go in as `null`, never as `NaN`
   or `Infinity` — Python reads those back happily, and `JSON.parse`, `serde_json`,
   `encoding/json` and `pandas.read_json` all refuse them. Seven rate-network
   artifacts were unreadable to a strict consumer before this was noticed. Write
   through `clfly.bench.artifacts.write_json`; do not call `json.dump` directly.
12. **Budget a question before buying it.** The cost of settling a curve claim is
   set by how far the effect sits above its floor, and the floor may not involve
   the parameter you were about to spend compute measuring. Working that out
   first turned a 5-hour re-run into a 1.9-hour one over three rungs
   (`docs/findings/2026-09-22-draw-budget.md`).
13. **Match the test to the design, and say the design's floor.** Four separate
   comparisons in this project were reported with a formula that did not match how
   they were built: matched rungs tested unpaired, a single control draw treated as
   the population, a paired bio/control comparison reported unpaired, and a mean of
   two sds used as the sd of a difference. The same omission errs **oppositely** in
   two regimes — optimistic when the dominant noise is the control draw; when the
   arms share seeds it depends on the sign of their correlation, which **must be
   measured, not argued**: a variance-decomposition argument said `e2`'s must be
   conservative and the measurement gave r = −0.27, making it mildly optimistic
   (`docs/findings/2026-09-22-sigma-audit.md` §3 and its correction). So "we used the
   unpaired formula" is not a diagnosis on its own. And a design has a floor:
   pairs from ``T`` tasks admit only ``T!`` labelings, so a pair-level prior cannot
   report p < 0.001 with fewer than 7 tasks
   (`docs/findings/2026-09-22-task-permutation-c4.md`).
14. **Set every hyperparameter deliberately, and diff configs before comparing two
   runs.** A run that never passes a flag is not measuring at "the default" — it is
   measuring at a value nobody inspected. The rung ladder ran two rungs at λ = 1.0
   (300× the recommended 0.003) because it never set `--lam`, and the mistake
   survived reading the script, reading the config dict, and being written up as a
   "reproducibility check"; the intended comparison against a λ = 0.1 run was
   therefore invalid, and the `naive` arm matching bit-for-bit is what proved the
   seeds were fine and the λ was not
   (`docs/findings/2026-09-22-e10-lambda-not-set.md`). Comparing two artifacts field
   by field is a one-line script and should precede any claim that two runs agree.
15. **Three replicates cannot decompose a variance, and cannot measure a correlation.**
   The network benchmark's noise floor was split into "evaluation, removable" and
   "training" from 3 replicates, where the 95% interval on the training remainder spans
   a factor of four — the same computation on a longer run that already existed
   (`n = 9`) narrows it 4× and puts the evaluation floor at 43% rather than 44% of the
   wrong quantity. A correlation at `n = 3` has standard error near 0.7, so the six rung
   runs' values from **−0.98 to +0.97** are what one true value looks like; the `n = 9`
   estimate is +0.02 [−0.65, +0.67], which contains all of them. **Before quoting an
   error bar that depends on an unmeasured nuisance parameter, check whether the
   repository already contains a run with the degrees of freedom to measure it.**
   Related and cheaper than it looks: an arm that is *indifferent to the manipulation*
   (here `naive`, which carries no penalty and no basis) is bit-identical across every
   run, so it is a free determinism control — and it settled the diagnosis here, showing
   the spread is learner seed-to-seed variability rather than measurement noise
   (`docs/findings/2026-09-22-network-variance-is-learner-variability.md`).
16. **Long runs must be launched without the default timeout.** A four-topology ×
   seven-`kappa` sweep was killed at ten minutes having produced 3 of its 21 points,
   because the background default applied. Any run expected to exceed ~10 minutes needs
   an explicit long timeout or none at all; otherwise the fire ends with a partial log
   and no artifact, which looks like a slow run rather than a dead one.
17. **Never compute a pooled statistic from an in-flight run.** A progress log is fine for
   reading individual points and for replication checks, and it is *not* fine for a
   pooled figure, because the last seed is partial and a partial seed is both badly
   estimated and over-weighted. This was done once, in `e45`, and the incomplete seed
   moved a pooled p from **0.077 to 0.032** — across the significance line — producing a
   finding that had to be corrected ten minutes later. The same partial data also
   inverted a per-seed ρ from −0.179 to +0.500 and a second claim fell with it. If the
   artifact is not finished, report the per-seed values and wait; `e45` now excludes
   incomplete sections and says so. The general form: **a pooled number needs every
   component finished, and partial data fails silently rather than loudly because a
   partial pool is still a number.**

   **And a second shape of the same failure, which rule 17 as first written did not cover: an artifact
   that is finished but covers fewer *targets* than the claim.** `e86`'s pressure-spread artifact came
   from a run that measured five of the nine partitions at d = 1874, and the finding quoted "the nine's"
   concentration range at that size as **0.034–0.324** — read off those five rows. The five were all
   `cell_type` poolings, so the range was correct *for them* and wrong for the nine: the missing rows
   include `side`, whose concentration is **0.498**, and the true range is **0.034–0.498**. Nothing in the
   artifact was partial in rule 17's sense — no seed was half-weighted — so every guard this project had
   would pass it. **The check that catches it is to compare the artifact's own `n` against the `n` of the
   claim** (5 against 9), and it is worth doing before quoting any min, max or sd, because a range is the
   most over-generalising summary there is: nine named partitions are a *design*, and five of them is a
   different design. The error propagated a second time, into the finding's conclusion — "the overlap of
   all three ranges contains enough rows at only one size" was true of the truncated range and false of
   the real one, which is computable at two sizes
   (`docs/findings/2026-09-23-the-cross-size-test-is-not-well-posed.md`).

   **A third shape, about quoting rather than computing: a statistic read off a set that is still growing is
   a moving target, and partial coverage is a *different set*, not a noisier version of the final one.** The
   grid's d = 952 partial was **+0.736 at ten cells and +0.795 at twelve**, two cells later, and both
   numbers were quotable-looking. What survives is the qualitative fact plus the count it was measured on —
   *positive, robust to leave-one-cell-out over twelve cells, no sign flip* — and what does not survive is
   the value. So the convention is to quote the sign, the stability check and the cell count from a running
   experiment and to hold the number until it is complete; the tell that it is being done wrong is a
   three-decimal figure with no `n` beside it. This is rule 17's theme one level up in the aggregation:
   there the unit was a seed, here it is a design cell, and in both cases the incompleteness is invisible in
   the number itself.
18. **Show that an intervention moves its own target variable, at the configuration you
   apply it.** `e49`: the `kappa` concentration knob was used to test a mechanism about
   the task precision's rank collapse, and at `swap2`/cs = 800 — the configuration the
   mechanism was *proposed* for — the knob travels **0.004–0.008** in `flattening`
   against **0.68–0.73** at `real`, i.e. ~90× less, because the carrier is already
   collapsed (`effective_rank` 1.70 against 55). Measured against the seed-to-seed
   spread the knob is **8.6–19.3×** the noise there, against **142–271×** at
   `real`. So the correlation it produces at `swap2` is over noise, and its sign means
   nothing in either direction. **Report such configurations as *untested*, not as
   null** — and note the shape of the trap: the mechanism was stated in terms of the
   collapse, and the collapse is what pins the variable the intervention acts on, so
   the mechanism is inert exactly where it was proposed. Four consecutive findings read
   a correlation at that configuration and argued about its sign; none checked whether
   the knob had moved anything. The check costs one column and belongs with the
   pre-registration.
   **And "untested" must not be read as "refuted"**: at the one configuration where the
   knob *does* have leverage for that mechanism (`swap2`/cs = 300, 30× the noise,
   `effective_rank` driven 16.6 → 2.35) the prescribed metric gives +0.143, +0.214,
   +0.357 — the mechanism's own direction, unanimously, and none of the three
   significant. The mechanism's *law* is refuted; its *direction* is underpowered.
19. **A smoke test checks that a flag runs; it does not read a direction out of anything.**
   Three readings in this sequence were taken off the smallest sample that could produce a
   shape, and all three misled: an "alternating sign" from four points (`e36`), a pooled
   statistic from a partial seed that moved p across 0.05 (`e45`), and — the clearest —
   `e36` §6b's caveat that the `kappa` intervention "already went the wrong way", from a
   **2-point, 1-seed** smoke test. The finished 3-seed run reproduces that smoke test in
   seed 0 *exactly* (1.1244 → 1.2572) while seeds 1 and 2 go the other way, and the 3-seed
   mean reverses it (1.1746 → 1.0606); the caveat then shaped the mechanism's status for two
   fires, in the plan and in a finding. **If a smoke test's output is quoted anywhere, quote
   its `n` beside it** — `--seeds` defaults to 1 in `e5` and this was not noticed while the
   number was being read.

20. **Quote the `n` beside every pooled figure, and treat any `n` below about ten as provisional
   until its per-seed values have been looked at.** Five results in this project have reversed or
   nulled when more seeds arrived, and each was a legitimate computation on the data available:
   `e36`'s "the sign alternates" from **four** points; `e42`'s three-seed mean published as the
   result for three fires; `e45`'s "a minority of seeds carries it" from **three**; `e51`/`e52`'s
   "the mechanism's direction, 3 of 3 unanimous" from **three**; and `e46`'s C2b rung contrast,
   where three negative seeds took `cell_class` at λ = 0.1 from **−0.0648 (2.65σ) to
   +0.0039 (0.24σ)** at sixteen — and the effect died at the *sixth* seed, which no summary
   statistic at n = 3 could have shown. The cheap guard is `e47`'s and `e57`'s: compute the
   per-seed values and look at them **before** quoting the pooled number.

21. **Quantify reproducibility; do not assert it.** "Bit-for-bit" and "bit-identical" were used
   throughout this project and they are **wrong for its numbers**. `e77` measured what the same command
   does under a different `OMP_NUM_THREADS`: on the **analytic** (numpy) path the results move at about
   the **fourth significant digit** — 1.8e-4 relative on a per-seed excess, 9.3e-7 on an aggregate delta
   — which is far below every σ the project quotes (the tightest is 1.29e-5 against a delta of 2.6e-4,
   so the environment sits 40× below it) but is not zero. On the **network** (torch) path the phrase
   fails outright: three replicates of 0.875 / 0.902778 / 0.909722 at the default setting against
   0.826389 / 0.840278 / 0.930556 at four threads, sharing no value at all. So the form to use is
   **"identical to N significant digits given an environment"**, with N measured. Two consequences the
   project has already had to absorb: a determinism control is a control *within* an environment (no
   artifact recorded one until this rule existed), and a run at a different replicate count but the same
   configuration is a **separate sample**, not an extension, unless its earlier replicates are compared
   and found equal (`e61` vs `e68` were not).

   **And the environment is now on the record (`e102`).** Saying "given an environment" is empty while no
   artifact says which one, and this session paid 58 minutes for it: `OMP_NUM_THREADS=1` on a five-replicate
   sweep, run solely to learn whether the thread count was the variable responsible for a two-vector
   difference between runs of one configuration — and the answer was *no*, which the seven artifacts already on
   disk would have shown for free had they recorded their thread counts. `experiments/e8_rate_network.py` now
   writes an **`environment`** block into every artifact (`omp_num_threads`, `mkl_num_threads`,
   `torch_num_threads`, `torch_num_interop_threads`, `torch_version`, `python`, `platform`) with **`"unset"`
   recorded as a value rather than as a missing key**, since most artifacts in this repository were produced
   with no `OMP_NUM_THREADS` set at all and a reader who cannot distinguish "unset" from "not recorded" has
   learned nothing. Two tests pin it (`tests/test_network.py`). **The default on this machine is 20 threads**,
   and none of the runs compared this session recorded its own.

22. **The programme table is a claim with an artifact behind every row: re-derive its status column from
   disk, not from memory.** Eight rows had drifted before `e85` audited them — four reported finished work
   as *in flight*, one row was **duplicated and contradicting itself**, and four were marked *done* while
   summarising a number the project had since overturned. **Every one of the eight was stale in the same
   direction**: toward *more open* in the status column and toward *larger effect* in the summary. That is
   the same direction as the six earlier failures this project has on record (`e41`'s stale table, `e54`'s
   assumed config key, `e62`'s missing artifact, `e63`'s unpaired σ, `e46`'s three seeds, `e84`'s failed
   fingerprint), and the mechanism is one mechanism: a document written from the state of the work when it
   was written, and never re-derived from the artifacts, drifts in whichever direction the work moved. The
   check is mechanical — each row names a `runs/*.json` or a finding, and both either exist or do not —
   and two of the eight were invisible to any check on a *result*, because the duplicate row and the
   "K = 4 was never run" claim are statements about the project's own bookkeeping. **The same check was
   then run on the paper and found five rows, one of which was a scientific error rather than a
   bookkeeping one**: §7's limitations recorded `pool1`'s **resolved disadvantage** — 20.3σ paired — as a
   null that had been "confirmed four times over", which is the hardest kind of drift to notice because a
   limitations section is where a reader expects the conservative statement
   (`docs/findings/2026-09-23-the-programme-table-had-drifted.md`).

   **A fifth way it misses, found when the check was re-run over all 59 rows and returned nothing**: a row
   can contradict *itself*. Three rows opened with **`**launched, prediction before the run.**`** while
   reading to the end of the same cell showed the finished result — two of them genuinely stale, including
   the `e86` row whose completion was written *into that cell* this week, thirty lines below its own opening
   word. **An update gets appended to the body while the header stays**, so the status word records the state
   when the row was created rather than the state now. This is a different failure from the eight of `e85`,
   where nobody had gone back at all: here someone went back and the edit landed in the wrong half of the
   cell, and the numbers are all correct, so no re-derivation of *results* can find it. **The drift is again
   toward more open** — a row that says "launched" reads as work in progress when its body reports the answer
   — which is the fourth consecutive audit in that direction and the first where the drift is in the
   formatting rather than the content. **The check is one line and needs no artifacts: print the opening of
   each status cell beside the end of it and ask whether they agree.** A word-based scan passes these rows and
   a full re-derivation of their numbers passes them too
   (`docs/findings/2026-09-23-the-status-word-is-a-header-nobody-re-derives.md`).

   **And a scanner that reports a file as missing when it is present is worse than no scanner**, because its
   output looks like evidence. This pass produced one such flag — a row reported as both citing a missing
   artifact and being stale, when the artifact was present and the word "launched" merely appeared in later
   prose — and a flag like that costs a reader more than the check saved. **So a mechanical audit's false
   positives have to be verified before they are reported, exactly as its findings do.**

23. **Resample the unit that is actually shared.** Two comparisons in this project crossed nine
   *partitions* and quoted a σ over their nine differences — `e82`'s size steps and `e81`'s paired
   `pressure − alignment`. **The nine partitions of one run see the same six relabellings**, so a draw-level
   effect moves all nine together and a sem over the nine understates the uncertainty. Resampling the
   **draws** instead gives **4.0× the sem**, and turns `e82`'s "3.29σ decay, eight of nine partitions
   declining" into **0.75σ with an interval spanning zero** — because an eight-of-nine sign pattern is
   exactly what a shared-draw effect produces, so it was never independent evidence. **The test is to ask
   which factor the observations share, and resample that**: a partition is one draw of a partition but one
   slot of a shared set of relabellings. And the distinction decides which comparisons are protected — a
   comparison of two *runs* has no protection, while a comparison of two *quantities measured on the same
   draws* (which `e81` is) should cancel the shared component, a claim `e88` exists to test
   (`docs/findings/2026-09-23-the-three-size-decay-is-not-resolved.md`).

   **And a grep for the overturned figure is not an audit.** `e85`'s paper pass found five stale sentences
   by searching for the numbers recent fires had changed, and that method has two blind spots the later
   abstract pass (`e89`) exposed: **a variant spelling escapes it** ("bit-for-bit" and "bit-identical" were
   withdrawn by rule 21, but §4.2 was written "**bit-reproducible**", which matches neither pattern and
   survived five passes), and **a hybrid range looks locally plausible** (the abstract's "**+33–63%**" mixed
   the measured +33% with the upper end of an earlier *realization-based* +45–63% that the paper states
   nowhere, and neither endpoint had been overturned so neither was searched for). The check that catches
   both is to ask **where each number should be sourced** and go there, rather than to ask whether the
   number looks familiar. **And search with a whitespace-insensitive pattern.** That audit has now missed
   something for four distinct reasons across four passes — a variant spelling ("bit-reproducible" for
   "bit-for-bit"), a hybrid range ("+33–63%" joining a measured 33% to a realization-based 63%), and twice
   a **line wrap**: "its standard / deviation across seeds" made a search for `standard deviation` return
   one hit where there were four, and the phrase "bit-identical" wraps in one place and not another.
   Replacing the patterns with `standard\s+deviation` and re-running upgraded one count from 1 to 4 and
   found a leftover §4.7 still said "bit-identical to `e8_hardened`'s". Three of the four misses were
   found by *reading* rather than by searching; the whitespace-insensitive pattern is the one guard that
   cost nothing and found something
   (`docs/findings/2026-09-23-the-abstract-had-six-stale-figures.md`,
   `docs/findings/2026-09-23-a-third-hybrid-and-a-line-break.md`).

**And the audit programme has a measured boundary, established by auditing the sections it had not
touched.** §3 (Substrate) verifies to the digit against the loader — seven of seven numbers, with
`cell_class` and `cell_type` at full coverage on the extracted circuit — and §6 (Methodology) survives its own
four figures and its derivation. **Not one of this week's eight drift instances is in a section that
describes what the substrate is or what the method does**; every one is in a section that *summarises, hedges
or points at* a result. The descriptive sections take their numbers from the data and the code; the summary
sections re-tell them, and a number that is re-told can be re-told from the part of the record being argued
about (`docs/findings/2026-09-23-the-last-two-unaudited-sections-were-clean.md`).

24. **A partial correlation is not a licence to control a confound statistically when the two are nearly
   collinear — prefer a design that sets the confound.** `e92` needs to separate *"the pressure spread
   predicts the control's draw spread"* from *"both grow with concentration"*, which is the confound `e86`
   could not remove, and partialling concentration out of both ranks is the obvious instrument. **On the
   nine named partitions it produces a number that reads like a result and is not one.** Rank-partialling
   *raised* the relative spread's correlation with the target from +0.882 raw to a partial of **+0.531**,
   above the less-coupled absolute form's **+0.509** — which is not what a restatement of the confound
   should produce. But the relative spread correlates **+0.950** with concentration, so its rank residual
   has almost no variance left and the partial is a ratio taken on a small denominator; the mirror-image
   number, concentration's partial *given* the spread, is **−0.040**, and that is nearly forced by the same
   collinearity rather than being independent evidence. **So the rule is to report the coupling beside the
   partial** — ρ(predictor, confound) and the residual spread, not just the partial and its p — and when
   that coupling exceeds roughly +0.9, to stop reading the partial altogether and get a design in which the
   confound is **set by construction**. That is what the grid is for: its `flat` cells have concentration
   exactly `1/k` at every circuit size, so the confound is matched rather than regressed out. The failure
   mode this guards against is the same one `e72` was diagnosed with a *chance denominator*, one level up:
   there the denominator was random, here it is real but thin, and both make the ratio look like a
   measurement when it is a division.

   **And a pre-registration may be amended, but the amendment has to be dated and visible.** The `e92`
   document's first version said "the pressure spread" without naming whether the absolute or the relative
   form carried the gate, which would have left the gated quantity selectable after the numbers were in.
   The clause was fixed **while the first cells were being measured and before any cell had been scored**,
   and both that amendment and its timing are recorded in the document's own §0 rather than folded in
   silently. So the convention is: chapters of a pre-registration that move after the launch get a
   *what-was-written-when* section naming them, and a reader who wants the untouched prediction is told
   which paragraphs to ignore. A pre-registration whose text can move without a mark is not one, and the
   cost of the mark is two sentences.

25. **On the network line the binding limit is the per-repeat spread, not the replicate count, and the two
   limits are not the same kind of thing.** Measured across the four configurations of `e8`/`e99`/`e100`,
   each arm's per-repeat forgetting sd is **0.019–0.084** while the mean forgettings being compared are
   **0.017–0.094** — so every gap the line reports is a fraction of one replicate's own variation, and
   more replicates shrink the *sem* without touching that. **On the linear substrate the analogous limit
   (the control-draw spread, rule 13/`e12`) is beaten by budget: more seeds eventually win. Here it is
   not**, because the quantity being compared moves as much within one run as the differences being
   claimed. The consequence is procedural rather than numerical: a network-line contrast is reported as
   **a gap with its sem**, never as a resolution, and separating two competing explanations for one
   contrast costs **~57 replicates per arm, 6–44 hours** — the same order as the rung question's own
   price. This is now stated in the paper's §4.7 and §7, and it is the conclusion of three findings
   (`docs/findings/2026-09-23-the-competing-explanation-is-not-excluded.md`).

26. **Build the control into the manipulation, by checking what the manipulation cannot move.** `e101`
   separated two candidate explanations for the network line's block-Fisher penalty at a cost of two runs
   instead of the ~57 replicates per arm the alternative needed, and the reason is that the benchmark
   contains arms that **cannot depend on the manipulated variable**: `naive` and `replay` consult no Fisher
   matrix, so varying `--fisher-batches` should leave them **bit-identical** — which both fixes the forgetting
   level by construction and proves it, since a level-based explanation is then unavailable. **The check is
   one line: does this manipulation leave anything bit-identical, and is that thing sensitive to the effect I
   am claiming?** The same property is an environment detector: `replay` came out identical between two new
   runs and different at an older one, which is how the older point was identified as a different environment
   (rule 21) — so **a Fisher-free arm is both the level control and the environment control, and neither role
   needs new machinery**. And the trap it closes is a real one: `e99` and `e100` compared configurations
   whose movements were inside their own error bars, and read two coincidences as confirmations of a
   mechanism the paper had already ruled out
   (`docs/findings/2026-09-23-the-conclusion-was-right-and-its-evidence-was-one-seed.md`).

   **Correction (2026-09-23, `e102`), and it splits the rule in two.** The *level* control is sound and the
   *environment detector* is **not** — but the arm assignment is the opposite of what this correction first
   said, and the measurement that settled it came last. Measured: `naive` is **bit-identical at the replicate
   level in all seven processes run** within one environment (three batch counts × two arm sets, including
   `e8_hardened_basis` re-run 13 hours and five commits later, **280 of 280 numeric fields equal**), so the
   level genuinely is fixed *within an environment* and every claim that needed that survives. **`replay` is
   not invariant**: its 15 stored numbers take exactly two values on disk, and the arm set with no Fisher in it
   at all gives `replay` the *same* value at 8 batches as at 32 — so the batch count is not what moves it, and
   an arm that moves while `naive` is silent has a source of variation that is not the environment. **Then
   `OMP_NUM_THREADS=1` and `=4` moved all five arms, `naive` included (+0.0729 → +0.0792), matched neither
   stored vector, and agreed with *each other* on `naive` while disagreeing on the other four.** So the
   repaired rule is:

   - **`naive` is a detector in one direction only: a mobile `naive` proves the environment moved, a silent one
     does not prove it did not.** It is the most sensitive Fisher-free arm available — invariant under every
     manipulation in this benchmark, because it consults no Fisher and no replay — and it fired when nothing but
     `OMP_NUM_THREADS` changed (+0.0729 → +0.0792, and *identically* at 1 and 4, so the variable is binary in
     effect here against a 20-thread default). It was **silent** across the X-versus-Y difference, which moved
     `ewc-block`, `ewc-block-rand` and `replay` anyway. So the earlier instruction to *never* use it as an
     environment detector was wrong, and this fire's first draft — that its silence is *evidence* of a shared
     environment — was wrong in the other direction.
   - **`replay` is neither**, despite being Fisher-free: it moved between runs where `naive` did not, so it has
     two sources of variation and can date nothing.
   - **And the search is not over**: the carrier of the X-versus-Y difference is something other than
     `OMP_NUM_THREADS ∈ {1, 4}` at this configuration, and it is not visible to the Fisher-free arm. X is
     reproducible across four executions spanning 13 hours and Y appeared exactly twice, inside one session, so
     the economical reading is a transient state of that session rather than a property of any recorded
     variable — which is now testable going forward, since the environment is on the record (`e102`, rule 21).
     **Four revisions of this claim in one session — each from a run, not from re-reading — is itself the
     argument for registering the *variable* rather than the intuition**
     (`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).

27. **An artifact's `config` keyset dates its code epoch, and a control is only readable against a comparator
   from the same epoch.** A runner that dumps `vars(args)` **cannot omit a flag its parser has**, so a key the
   current parser defines and a stored artifact lacks is proof that the artifact predates that flag — a
   timestamp a migration cannot fake, unlike `mtime`. The check is one line and it is exact: compare
   `set(artifact["config"])` against the parser's option strings. It found that
   **`runs/e8_hardened_basis.json` — the artifact behind the paper's §4.7 table and the baseline of `e99`,
   `e100` and `e101` — predates `--replay-batch`**, and is therefore from a code epoch at least five commits
   older than the runs compared against it; only **2 of the 27 artifacts written by that runner** are from
   that epoch, and their `mtime`s are all identical because `e98`'s in-place normalisation rewrote them
   (rule 17's "a set that changes under you" in its *provenance* form: here the file is rewritten without its
   payload changing, so the tell has to come from inside the payload). The consequence is not that such an
   artifact is unusable but that **a contrast whose two sides come from two epochs is a contrast in code as
   well as in the variable**, and the repair is to re-measure the older side rather than to argue about it.

28. **A table is a claim, and its cells must come from one run.** Every audit this project runs is either
   *number → artifact* (does any artifact contain this figure?) or, since `e103`, *arm → second execution*. Both
   are blind to the failure found in the paper's own summary tables: **a row whose cells are stitched from
   different runs**, and **a column whose comparator is not one number**. `docs/paper/clfly-v1.md` §4.2's
   "vs naive" column subtracted **+0.0729 for two rows and +0.066 for two others** while its `naive` row printed
   +0.066, so two of its four contrasts were correct and two were computed against a baseline no run contains —
   and a reader checking any single cell against any single finding finds nothing wrong. Three checks make this
   mechanical: **(a)** each cell against the corpus, **(b)** all cells of one row against **one** run, and
   **(c)** a column's comparator against **one** number. And the level above it: **a control can be missing, not
   just wrong** — the `--frozen-body` sweep that justifies the hardened configuration, and that §7 states as an
   imperative design rule, is in **no artifact** (0 of 204 have `frozen_body: true` or a `frozen` arm), because
   the fire that added the flag printed its table and saved only one command's output. **So when a claim rests
   on a control, check that the control exists before checking what it says**
   (`docs/findings/2026-09-23-the-frozen-body-control-is-in-no-artifact.md`).

29. **A factor that is not the manipulated variable is not thereby held constant.** `config` records what was
   **asked for**, so "identical configuration apart from the variable" is a claim not about the config but about
   the code's *other inputs*, and one of those inputs is the random draws. `e113`'s seven read-outs were
   supposed to differ in one variable and differed in two — the size of the read-out subset **and which
   neurons were drawn** — because `choice(size=n)` consumes the RNG differently at every `n`, so a factor
   nobody treated as a variable was varied at every step and never held fixed. The tell is that the "identical
   config" claim is checked against the *file*, and the file cannot contain the draw: the config has
   `readout_size` and not the subset. **The generalisation is that every "held constant" in a design is an
   assumption to be *tested*, not inherited from the config dump**, and the fix is to make the varying input
   explicit (`--readout-seed` is now recorded, default seed0, so an artifact names its draw and old artifacts
   are bit-for-bit unchanged) rather than to argue that it does not matter
   (`docs/findings/2026-09-23-the-draw-is-as-large-as-the-effect.md`, and the withdrawal it forced in
   `docs/findings/2026-09-24-the-draw-is-not-detectable.md`).

30. **A cost computed from an sd needs the same standard of evidence as the effect it is set against, and the
   tolerance compounds.** A two-sided factor-of-two tolerance on an sd is a factor-of-**four** tolerance on the
   count that feeds it, and it is worse than a wide interval: a wide interval on a mean is *honest*, whereas a
   wide interval on an sd is *a licence*, because the sd is what everything else is measured in units of. The
   instance: a "the forty-replicate sds are within 2× of the five-replicate ones" pre-registration passed at
   1.69×, and 1.69× on an sd is 2.9× on the count — so the check that was meant to catch an underestimate
   licensed most of one. **The repair is to state the direction rather than the tolerance** wherever the
   direction is derivable (a five-point sd of a heavy-tailed quantity should be an *underestimate*), and to
   give the sd's own derived quantities their error bars before quoting them
   (`docs/findings/2026-09-23-the-axis-at-one-precision-preregistered.md`; the same arithmetic is what makes
   `e119`'s variance decomposition readable — a factor of √10 of removability on a test-set term is a factor
   of ten in the noise it removes).

31. **A saved state must contain every parameter the forward pass reads, and the control for that is a
   recomputation rather than a key list.** `e122`'s chord reported endpoint losses of **0.105** for a body whose
   own recorded loss was **0.0017** — a factor of **sixty, on the endpoint**, which is the loudest place a bug
   can be — and the cause was not the geometry: `train_task` optimises `[model.theta, model.bias]`
   (`experiments/e8_rate_network.py:72`), and `--save-theta` wrote `theta` and the decoders. **Every point on
   every chord, both endpoints included, was evaluated on top of a zero bias the benchmark never produces.**
   The rule this fire adds is about the *check*: the repaired instrument's control is that the chord at `t = 0`
   **is** a saved checkpoint, so its loss must equal a number the runner wrote down while training —
   an **equality**, not a tolerance — and that needed the runner to record the right number first
   (`retention_loss[k][j]`, the retention matrix in loss, added for this). **A key-list assertion would pass the
   moment somebody adds a trainable parameter and forgets it in the same way**, which is why the permanent test
   (`tests/test_e122_checkpoint.py`) reloads a checkpoint into a fresh module and requires the recorded loss,
   and why its sibling asserts *how big* the failure is (a factor of 3 on a tiny circuit, 60 on the real one) so
   that "we would have noticed" is a measurement rather than a hope.

32. **An artifact's key set dates its epoch, so a run compared with a nominal copy of *itself* is not exempt
   from rule 27.** `e125` needed the plastic arm at read-out 32 and found it on disk twice:
   `runs/e116_r32_40reps.json`, identical configuration at forty replicates, and
   `runs/e104_frozen_r32_plastic.json` at five. **Their first five replicates are not bit-identical, and the
   reason is a keyset rather than a number**: `e104`'s replicate dicts lack `theta_drift` and `e116`'s lack
   `retention_loss`, so the two files are two code epochs. Rule 27 was written for a *contrast* between an
   experiment and its control; this is the case it was not written for — **the same variable on both sides** —
   and it says the run must be redone rather than cited, because a difference between two epochs is a
   difference in code even when nothing was manipulated. The repair is cheap and the cost of not making it is a
   comparison whose two halves are dated differently: `e125` re-runs the plastic arm in its own epoch and treats
   the on-disk copies as **labelled, tolerance-bounded** comparators instead.

   **And the rule's converse is worth stating, because this session produced two proofs of it: a keyset
   difference dates the epochs, and it does NOT say the numbers differ.** `e125`'s plastic arm was registered to
   match `runs/e116_r32_40reps.json` within **one sem** and came out **per-replicate identical** (mean +0.0750,
   sd 0.0556, max difference 0.0). And `runs/e123_r300_test480.json` — written with `retention_loss`,
   `bias_norms`, `--frozen-bias` and the per-task checkpoint all present — reproduces
   `runs/e119_r300_test480.json`, which has **none** of them, with max ABS difference **0.000e+00**. So the
   session's four `e8` additions are **record-only**, and that is measured twice at two read-outs rather than
   argued from the fact that they sit outside the training loop. **The rule as it stands is a warning about
   what a keyset can hide; these two results are what tells you, case by case, whether it is hiding anything** —
   and the discipline is that the *check* has to be made (a re-run, or a stored comparator at the same
   configuration) because the keyset itself cannot decide.

33. **A count is a claim about the document, and nothing here was reading one.** Every audit this project has
   reads *numbers*: `e97` checks that a cited artifact exists, `e105` checks that a table's arithmetic closes,
   `e103` checks that an arm executes twice. **A count is not a number — it is a claim about the shape of the
   thing that contains it**, and `e126` is the first check that compares a document's enumerations to its own
   contents. Two defects had been sitting in the paper for two days and neither was findable by any of the
   others: **§7's heading said "Five measurement traps" over four bullets**, and it was born wrong in commit
   `1743573` — *the commit whose message is about stale aggregate statements*; and **§4.3 contradicted itself
   fourteen lines apart**, one sentence saying all eight ladder rungs have a measured draw sd of their own and
   another saying three of the eight have none, with `runs/e73_ladder_named_head_to_head.json` settling it in one
   field (`n_ladder_measured` = 8 of `n_ladder` = 8). The second is the more instructive: its clause was written
   when five of eight were measured, two later commits corrected the *sibling* sentence and the *abstract* and
   both missed it, and **the tell that a human would have caught was that the stale clause quoted the post-fix
   range while giving the pre-fix reason** — a sentence internally inconsistent with itself is the cheapest
   possible detector and it needs no tooling. The audit that now exists reads one narrow pattern (a count opening
   a line or a bold run, followed within six lines by a list, stopping at a heading), reports its denominators,
   and reports every ratio phrase it declines to check; **its four failed designs are documented in its own
   docstring, because a checker that reports everything gets ignored and an ignored checker is worse than none**
   (`docs/findings/2026-09-24-the-paper-counted-its-own-bullets-wrong.md`).

34. **A sentence can stitch two runs as easily as a table can, and the tell is arithmetic.** Rule 28 requires
   every cell of a table to come from one run; this is the same defect in **prose**, where no audit looks. §4.2
   said *"85% predicted a 2.6× fall and the fall was 1.47×"*, and **the 2.6× never followed from the 85%**: a
   85% removable share with a tenfold test set predicts **2.07×**, and 2.6× needs **94.7%** — which is
   `runs/e102_rate_fb8_omp1.json`'s **0.9461**, an artifact at **read-out 32 with five replicates** against the
   **read-out 128 / forty** the 85% comes from. **Both halves were real numbers from real artifacts and neither
   was wrong on its own**, which is why `e97` (artifact existence), `e105` (table closure) and `e126` (counts) all
   passed it, and why it survived from `e119` to this fire. **The check is the cheapest kind and needs nothing
   on disk: recompute the stated prediction from the stated input.** `1/sqrt(0.1f + 1 − f)` is one line for any
   `f`, and the same discipline catches any claim of the form *"X% implies Y×"*. **And the correction moved the
   explanation to the other quantity**: the sentence attributed the over-prediction to the *difference* of two
   accuracies, while the measurement shows the forgetting's removable component does fall by √10 — *because the
   60% split was solved for by assuming it, so that is a tautology rather than a test* — and the **single
   accuracy's** directly-computed 85% is the one that fails, predicting 2.07× against a measured **1.16×**.
   Solving the same-seed pair for the accuracy's effective binomial sem gives **0.01229 against a nominal
   0.02109**: **an effective 49 independent held-out decisions rather than 144, and an achievable removable share
   of 29% rather than 85%.** The runner's own else-branch had carried that caveat as a clause since it was
   written — *"or the 144 held-out decisions are not independent"* — and the rule for reading such a clause is
   that **a named mechanism in a docstring is a hypothesis until a pair of artifacts measures it**
   (`docs/findings/2026-09-24-the-nominal-removable-share-is-not-the-achievable-one.md`).

   **And the rule found a second instance within the same session, which is the evidence that it has yield.**
   `e120`'s pre-registration derived a seed-to-seed correlation from the forgetting's and the accuracy's sd's —
   **naming its own formula, `sd_forgetting = sd_accuracy·√(2(1−ρ))`** — and reported **ρ ≈ 0.14**. On the
   paragraph's own rounded input that formula gives **0.246** and on the artifacts' exact values
   (**0.01963** and **0.02215**, both from `runs/e119_r128_test480.json`) it gives **0.364**; the `≈ 0.018` it
   used was itself a slight understatement of 0.01963, which is where part of the drift entered. **The
   2000-iteration value in the same pair is right** (0.062 against a reported 0.06), so this was one wrong
   number and not a wrong method — and **the correction strengthens the mechanism rather than weakening it**:
   the drop is **0.364 → 0.062**, a factor of six against the 2.5 the wrong number implied. A third reading
   explains both: **at test 48 the same propagation gives ρ = −0.014**, so the two accuracies are uncorrelated
   across seeds when the test set is coarse and correlated once its sampling noise is removed, which is the
   ordering the mechanism predicts and which was invisible while one of the three values was wrong. **All four
   of this project's audits were green on it** — `e97` reads artifact existence, `e105` table closure, `e126`
   counts, `e127` the programme table — because it is a sentence (`docs/findings/2026-09-24-rule-34-had-a-second-instance.md`).
   **What the rule cannot catch, stated because a rule that looks total is dangerous: it applies only where the
   text names its own formula.** `e128`'s `2.6×` named none and was caught by recomputing anyway; a claim whose
   model the reader cannot reconstruct from the sentence is invisible to this check, and there the only defence
   is that **a number quoted beside its input is worth more than a number quoted alone**.

## Related work to differentiate against

Four papers are close enough to require explicit positioning — all use fly
*biology* to inspire a learning rule, none uses a connectome-constrained network
as a CL substrate:

- Shen, Dasgupta & Navlakha, *Neural Computation* 35(11):1797, 2023 — associative
  learning in the fly olfactory circuit reduces forgetting.
- Robinson et al., bioRxiv 2023, doi:10.1101/2023.01.18.524467 — long-term memory
  formation inspires generative replay.
- Norman-Tenazas et al., GECCO 2023, doi:10.1145/3589737.3605985 — local learning
  for replay with a recurrent model of the insect memory centre.
- Max, Shen et al., *Neuromorphic Computing and Engineering*, 2026,
  doi:10.1088/2634-4386/ae9177 — few-shot continual learning for spiking
  neuromorphic olfaction.

Crowded areas to avoid claiming novelty in: SNN continual learning by
regularisation / replay / structural growth; gradient-subspace and null-space
projection CL (GPM, InfLoRA); K-FAC and structured Laplace; statistical-physics
theories of task similarity; CW10/CW20-style CL-RL benchmarks.
