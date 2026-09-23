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
every matched pair whose excess difference clears 2σ *on the paired seed sem* — **20 of 21** once each
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
reproduced on synapses. **The coarsest rung, `side`, has never been run, and on neurons
`side` was the strongest rung (28.8σ) and the best basis the vocabulary offered.**

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
replicates, i.e. **0.2–6 hours depending on the rung**, which is one working session
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
| `e64_predictor_per_seed.py` | C2 | the predictor's matched pairs checked per seed, at three denominators | done — `runs/e64_predictor_per_seed_analysis.json`. 25 pairs → 24 resolvable on σ(task) → 21 on σ(rule); correct 24, 23, 20 respectively. The single miss is `rewired-swap2`/`cell_class`. **One stale source had to be fixed to get this right**: the first version used `e14`'s *pooled* `cell_type` draw sd as a proxy for `cell_type`, which collapsed its σ(rule) to 0.07–0.42 and reported six pairs below 2σ where the answer is four |
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
| `e8_rate_network` at the other two settings, pool 96 / per-step 8 | C2b | the task-IL and class-IL replay arms (`e84`) — the two pool-96 numbers `e61` does not cover | **launched, prediction before the run.** task-IL is the default (per-task heads, `--readout-size 0`, **no `--input-overlap`**) and class-IL is `--shared-head` with `--readout-size 0` and no overlap; both at λ = 0.003 / 8 Fisher batches / 5 replicates so they sit beside `e61`'s. Neither has an artifact: a census of the 17 stored artifacts carrying a `naive` arm finds `replay_per_task: 96` in **exactly one**, `e61`'s own step-8 run. **The two arms differ in how far they can be trusted, and the fingerprint is what separates them:** task-IL's claimed naive (+0.101) matches `e10_rung_*`'s **0.8241 / +0.1007** exactly, so a recreation whose naive reproduces that *is* the same computation; class-IL's claimed naive (+0.059 ± 0.028) matches **no** stored artifact — and `e8_class_incremental`'s stored class-IL naive is **0.9361**, half a sem away from nothing in particular — so that arm is a **re-measurement under the best-matching configuration, not a confirmation**, and the run's own naive will say which it is. **Prediction:** task-IL's naive reproduces 0.8241 / +0.1007 to the printed precision; **falsifier:** a naive that does not, which would mean the settled finding's task-IL row was computed under a configuration no stored artifact shares and the recreation is a new measurement rather than a restoration. For class-IL no fingerprint prediction is possible and the honest output is a fresh number with its own detection floor. **RESULT, task-IL: the falsifier fires — it is a re-measurement, not a restoration.** The naive reproduces only to **0.8417 against the stored 0.8241**, with per-seed differences up to 0.063 and *mixed signs* — the signature of a different training trajectory, and the cause is the environment (`OMP_NUM_THREADS=3` here, unrecorded for `e10_rung_*`). That is **rule 21's first practical casualty**: a missing artifact cannot be restored across environments, though the census stays sound within one (`e10_rung_*`'s 3-seed mean 0.8241 is exactly `e54` cluster 0's first-three mean). At n = 5 the re-measurement gives contrast **−0.10417 ± 0.01647 = 6.32σ** on forgetting (`-----`, LOO 4.84) and **+0.09028 ± 0.00761 = 11.87σ** on accuracy (`+++++`, LOO 9.62) — stronger evidence than the claimed 3.1σ, magnitude 34% smaller — while replay's own forgetting is **−0.0042 ± 0.0091 (0.46σ from zero)** against the claimed −0.056 ± 0.009, a **6.3σ disagreement**. So "replay eliminates forgetting in task-IL" holds and "replay drives it 0.056 below zero" does not. **RESULT, class-IL: also a re-measurement (naive 0.9194/+0.0688 against `e8_class_incremental`'s stored 0.9361/+0.0437), and the closest reproduction of a network-line claim in the project** — every one of the claim's four numbers is inside the measurement's interval: naive forgetting +0.0688 against +0.059 ± 0.028, replay forgetting +0.0063 against −0.010, replay accuracy 0.9611 against 0.975, contrast **−0.06250 ± 0.01647 = 3.79σ** (`-----`, LOO 2.84) against −0.069 at 2.2σ. Its accuracy contrast is +0.04167 ± 0.00905 = 4.60σ (`+++++`, LOO 3.48). **A wrinkle**: this arm's recreation is *closer to the claim* than to the stored artifact it is compared with, so the original's configuration is neither — the fingerprint had no valid reference for it, which is why the plan said in advance it could be re-measured but not confirmed. **And one claim the abstract must lose**: it says replay drives forgetting "to zero or below", but in neither setting does replay's own forgetting sit below zero with confidence (−0.0042 ± 0.0091 = 0.46σ for task-IL; +0.0063 ± 0.0150 = 0.42σ *above* zero for class-IL). What reproduces is *driven to zero*, which is the part LGCL's prediction needs |
| `e2_topology_gap.py --topologies swap0.5 --rewire-seed 0..5` | C1 | the `swap0.5` realization sweep (`e65`) — the one component missing from the two-σ decomposition | done — **the C1 contrast is 2.2σ about the rule, not the 2.7σ bound.** `swap0.5`'s realization sd is **0.00269** against `swap2`'s 0.00377, so the two rules have the *same order* of wiring spread (every rule measured is ≈0.003) and the branch `e59` called pessimistic (1.9σ) was the close one. Three readings, all reported: **28.8σ about the two graphs**, **2.2σ** on one redraw of each rule, **3.4σ** comparing rule means (**5.8σ** if each arm's worst draw is dropped). **And the partial reading was wrong out loud**: at four draws the sd was 0.00054 and the bound looked exact; the fifth draw (0.01631) multiplied it by five, which is rule 15 arriving on the *realization* axis |
| `e12_control_spread.py --column {side,cell_type}` | C2 | measure the two draw-sds that the predictor's correction had to *interpolate* (`e67`) | **done, both arms, and the pre-registration is refuted.** The mechanism finding predicted `side`'s draw sd at ~1.0e-3 (concentration 0.498, interpolated between 0.325 and 0.678) and predicted that the 2-draw smoke value 9e-5 would not replicate. Eight draws give **2.16e-4** — 4.8× below the prediction and closer to the value it was written to overrule. The relation is non-monotone: **6.8e-5** → 9.3e-4 → **2.16e-4** → 1.06e-3 as concentration rises 0.020 → 0.325 → 0.498 → 0.678, and the fine point itself moved 1.75× when it went from 2 draws to 8. Consequence: the §5 correction of `side` (15.53σ → 4.47σ) is a 2.8× over-correction — with the measurement it is **12.74σ** — and **all five** named rungs can now be corrected with measurements: **17.5 / 9.0 / 9.3 / 4.1 / 0.73σ**, overstatements **1.0–1.6×**, not 3–6×. The predictor's 13 of 13 is **not** untouched, it turns out: `e64` shows the pairing moves the denominator to 24 and the swap2 failure is a 10.63σ wrong call |
| `e71_variance_share_audit.py` | C2b | audit the "62% of the variance is the learner" figure against the artifact field it comes from | done — **the sentence is inverted in three documents**. `e38`'s `floor_share_of_variance` is **0.619** for the `naive` arm at n = 9, i.e. the *test set's* binomial floor; the learner is 38.1% there and **45.1%** in `e54`'s n = 16 pool (95% interval [0%, 77%]). For the **contrast** — what the axis argument is made on — the floor is 43–46%. Conclusion unchanged: ten times the test set buys **1.41×** and no more, so seeds remain the lever |
| `e72_alignment_draw_spread.py` | C2 | **pre-registered**: which variable predicts the control's draw spread, now that concentration does not? | done — **the prediction is REFUTED and the falsifier it named FIRES**; the result is at the end of this row. `e67` refuted the one-scalar model, and the refutation has a mechanical explanation the scalar cannot express: concentration is invariant under relabelling (a relabelling preserves group sizes exactly), so the only thing a control draw changes is *which* neurons share a group — i.e. how the partition's indicator span sits against the task subspaces. The candidate predictor is therefore the **draw-to-draw spread of a partition's task alignment** (`e3`'s `alignment_of` excess over random subspaces, recomputable per draw with no filter). **Prediction:** over the partitions with both a measured excess draw sd and a computable alignment spread — `side` (2.16e-4), `cell_class` (2.37e-4), hemilineage (4.16e-5), `supertype` (8.35e-5), pooled `cell_type` at min sizes 2/4/32 (9.3e-4, 6.13e-4, 1.06e-3) — the alignment spread ranks the excess spread at Spearman **≥ +0.8**, where concentration is non-monotone (0.325 → 9.3e-4, **0.498 → 2.2e-4**, 0.678 → 1.06e-3). **Falsifier:** `side`'s alignment spread coming out *larger* than pooled-min-2's while its excess spread is 4.3× smaller. **RESULT (nine points, concentration 0.020–0.536):** Spearman(alignment spread, measured sd) = **+0.283, p = 0.46**, against the pre-registered ≥ +0.80; `side`'s alignment spread is 0.371 against pooled-min-2's 0.071 — 5.2× larger — while its excess spread is 4.3× smaller, so **the falsifier fires**. And the failure is **structural**: the candidate is a re-expression of partition size, ρ = **+0.850** with concentration (p = 0.0037) and **−0.904** with indicator-span dimension (p = 0.0008), so it inherits the failure of the scalar it was meant to replace. The mechanism is that `alignment_of` reports `raw / chance` with a *generic* random subspace as the denominator, which strips the free size advantage and, on this measurement, the task information with it. **A refinement of `e67` comes with it**: over nine points concentration itself scores **+0.617 (p = 0.077)** — a weak *global* ordering rather than noise, though not significant at n = 9 and non-monotone exactly in the 0.3–0.7 region the project's claims live in, so what stands is `e67`'s *local* refutation |
| `e75_task_pair_spread.py` | C2 | **pre-registered**: does the control's excess MOVE WITH the partition's alignment? | done — **the fourth candidate fails, and this one had every structural advantage.** The design fixed both flaws `e72` diagnosed: no chance denominator, and co-movement rather than spread, with the task draw held fixed (each correlation is *within a seed*, across draws, after centring by the seed mean). Result: within-partition co-movement **mean ρ +0.130 (mean r +0.170, r² 0.066)**, against a pre-registered ≥ +0.5, and **+0.17 ± 0.24 is not distinguishable from zero**. Spearman(co-movement, measured draw sd) = **+0.150** against a pre-registered ≥ +0.8, while concentration scores **+0.617** — the fourth time a plain partition-size scalar beats a task-relative candidate. **The falsifier fires for 3 of 9 partitions**, including `cell_class` (−0.102) and `side` (−0.096), the two rungs the C2 claims lean on. So the conclusion is substantive rather than another closed door: the draw spread is **not** the relabelled span's geometry against the task's precision subspace |
| `e80_pressure_draw_spread.py` | C2 | **pre-registered**: does the draw-to-draw spread of **`projection_pressure`** predict the draw-to-draw spread of the control's excess? | done — **the first candidate in five that works, and it is not a size scalar.** The **absolute** pressure spread ranks the measured draw spread at **+0.767 (p = 0.016)** over nine partitions spanning concentration 0.020–0.536, and is only **+0.317** with concentration and −0.433 with the pressure level. Neither form satisfies both pre-registered clauses and *how the other one fails is the diagnostic*: the **relative** form hits the target exactly (+0.850, p = 0.004) but scores +0.767 with concentration, because **the pressure level is itself −0.983 with concentration** — so dividing by the level manufactures the size correlation, the mirror image of `e72`, where dividing by a random subspace collapsed the quantity onto span size. The falsifier (concentration ≥ +0.85) fires for neither form. **Mechanistically this is a real advance**: the four failures all used the task's *subspace* (which directions the drive occupies); pressure uses the task's *information* `J_k` (how strongly each direction is measured), and the draw spread turns out to be about the latter. Limits: n = 9 and four candidate families tested on the same targets, so the nominal p is not a discovery on its own; the two forms are ±0.083 apart on the target and the preference for the absolute one rests on its *diagnosed* independence; and the targets themselves carry 20–50% error (3–8 draws each). `per_draw_seed` is kept in the artifact so the co-movement question can be asked of the pressure without recomputing the filter |
| `e81_pressure_comovement.py` | C2 | **pre-registered**: does `projection_pressure` CO-MOVE with the control's excess, within a seed? | done — **the pre-registration passes on every clause and this is the mechanism.** Mean within-seed co-movement **+0.906** (predicted ≥ +0.5) and mean ***r*² 0.828** (predicted ≥ 0.25), against the bare alignment's **+0.170** from `e75`; the falsifier does not fire and **0 of 9 partitions have a non-positive co-movement**. The decisive row is the **paired** one, because it is the same design twice — same nine partitions, six relabellings, three seeds, same within-seed centring, only the quantity differs: **pressure − alignment = +0.736 ± 0.061, 9 of 9 positive, sign p = 0.0039**. So the control's excess moves across relabellings because the **precision-weighted projected deficit** moves (83% of the variance) and barely at all because the subspace geometry does (6.6%) — which retro-explains all four failures, since every one of them was a subspace overlap and none could see `J_k`. **Two things it does not say, both measured**: the per-partition co-movement does **not** rank the draw spreads (Spearman **+0.067**), so `e81` *explains* the variation while `e80` *calibrates* it and neither implies the other; and `side` is the weakest partition at +0.681 (*r*² 0.464) — the honest form is "83% on average, 46% for the one partition whose σ the paper leans on" |
| `e81_pressure_comovement.py --circuit-size {300,1500}` | C2 | **pre-registered**: does the mechanism replicate at two other circuit sizes? (`e82`) | done, **three sizes and the mechanism is not size-invariant.** At cs = 300 (d = 952): mean *r* **+0.923**, *r*² 0.854. At d = 1307: +0.906 / 0.828. At cs = 1500 (d = 1874): **+0.810 / 0.676**. **All 81 seed-level correlations across the three sizes are positive** (smallest +0.368) and the bare alignment's +0.170 is beaten everywhere by 4.8× in *r*². **Paired: d = 1307 − d = 952 is −0.0166 ± 0.0198 (0.84σ, p = 1.0000) — a null — and d = 1874 − d = 1307 is −0.0962 with signs `+--------`.** **BUT THE SECOND IS NOT RESOLVED** (`e87`): the nine partitions share their six relabellings, so a sem over the nine treats correlated numbers as independent. Resampling the **draws** gives **4.0× the sem** and an interval that spans zero — −0.0962 [−0.3110, +0.1468] = **0.75σ**, with 80.5% of resamples below zero — and the same correction takes the first comparison from 0.84σ to 0.45σ. So the apparent decay is a **point estimate, not a measurement**, and the eight-of-nine sign record — which is exactly what a shared-draw effect produces — was never independent evidence. The mechanism's strength at the largest size is 0.810 against 0.906 and any future design should assume the difference may be real, but it is not established here. Per partition, what decays is `side` (0.681 → **0.418**, the only *r*² below 0.5 at any size and a monotone decline across three) and `ito_lee_hemilineage` (0.980 → 0.771), while the four `cell_type` poolings, `supertype` and `cell_class` stay at 0.83–0.90. **Two untested explanations, separable by one cheap run:** either the decay is a property of the *design* (a Frobenius aggregate over three tasks samples a smaller fraction of the perturbation space at larger d, so more draws would restore *r*), or of the *quantity* (the excess picks up contributions pressure does not represent, so it would not). Also recorded: at cs = 300 `cell_type` min 4 and min 6 are the **same partition**, so there are eight distinct and not nine — the same crowding `e3` found at d = 1307. **And the *spread* statistic is not replicated at all**: `e80`'s +0.767 needs the nine measured draw sds, which are d = 1307 numbers, so the script refuses to print it away from d = 1307 |
| `e12_control_spread.py` × 9 partitions × cs = {300, 1500} | C2 | the measured draw sds at the two other circuit sizes (`e86`) — the target `e80`'s spread statistic never had away from d = 1307 | **launched, prediction before the run.** `e80`'s is the half of the mechanism that matters for a *predictor*: the co-movement says pressure and the excess move together, the spread statistic says the **size** of pressure's own variation calibrates the **size** of the control's — and `e82` already stores the pressure spreads at both sizes, so the only missing piece is the target. Eighteen runs at `e14`/`e74`'s protocol (3 task seeds, 5 draws) so the new points sit beside the old ones; ~2 h. **Prediction:** at each new size the absolute pressure spread outranks the measured draw spread at **Spearman ≥ +0.7** *and* beats concentration on the same nine partitions. **Falsifier:** it failing to beat concentration at either size — a live risk, since at d = 1307 the margin was only **+0.767 against +0.617** on nine points, and the target itself carries 20–50% error at five draws. **RESULT at d = 952: the falsifier FIRES.** The absolute pressure spread scores **+0.412 (p = 0.27)**, below the pre-registered +0.70 and well below concentration's **+0.832 (p = 0.005)** — so the ordering `e80` found **reverses** at a second circuit size. The form that does score well there, the relative spread at +0.882, correlates **+0.950 with concentration**, i.e. a size restatement — **and that inference was itself overstated**: with concentration rank-partialled out the relative form keeps **+0.531** at d = 952, above the absolute form's +0.509, though on a rank residual with almost no variance left (ρ = +0.950 with the confound, and +1.000 at d = 1874), so it is the fragile-denominator situation `e72` was diagnosed with. What the nine points support is the weaker "not distinguishable from concentration, raw or partial"; the instrument that settles it is `e92`'s grid; that is the same failure mode `e80` diagnosed at d = 1307 when the relative form hit +0.767 with concentration. So `e80`'s headline was a **d = 1307 event**, and the second size *contradicts* it rather than merely failing to confirm. **d = 1874's targets are still running**, so the spread verdict is a 1–1 split that could become 1–2 or 2–1. **AND THE TEST ITSELF IS NOT WELL-POSED** (`docs/findings/2026-09-23-the-cross-size-test-is-not-well-posed.md`): the nine labels are the same and the **partitions are not** — the concentration ranges of the nine are **0.006–0.754 at d = 952, 0.020–0.536 at d = 1307, 0.034–0.498 at d = 1874** — **corrected from 0.034–0.324, which was read off the pressure artifact while it held five of the nine rows at that size**, and whose real maximum is set by `side` at 0.498; `side` is in fact a **fixed point** of the whole design (0.4981/0.4985/0.4984 at the three sizes), and the common range 0.034–0.498 holds **2/4/9** of the nine rows, so the overlap cannot be computed at d = 952, the size whose reversal is in question (rule 17's second shape), so the "replication" compares a set with four partitions beyond 0.69 against a set whose coarsest is 0.536, and the overlap of all three ranges holds enough rows at only one size. **Why d = 952 fires is then visible**: its nine are **bimodal** — four rows at 0.690–0.754 with measured sds 2.96–3.54e-3 (and `cell_type` min 4 ≡ min 6 there are the *same run*, byte-identical rows) against five at 0.006–0.159 with 0.9e-4–1.2e-3 — and **restricted to the fine end (conc < 0.6, n = 5) all three candidates tie at +0.900**. So the reversal is a bimodal design in which four near-duplicate coarse rows occupy four of the nine ranks at the top of both orderings, which concentration captures by construction and which carries almost no discriminating information. **The standing position: one complete size in the spread statistic's favour (d = 1307, where it was found), one complete size against (d = 952), and neither test is over the same partitions as the other.** The design that would test it properly is pre-registered in the finding: **choose partitions by concentration, not by label, and use the same concentration grid at every size** — which also removes the bimodality, since binning forces the coarse end to be sampled at several levels |
| `e92_grid_profiles.py` × 20 cells × cs = {300, 800, 1500} | C2 | **pre-registered**: the spread statistic on a grid whose cells are **group-size profiles**, chosen by concentration rather than by annotation label, so that "cell *i*" names the same region of partition space at every circuit size (`e92`) | **launched, prediction before the run** (`docs/findings/2026-09-23-the-concentration-matched-grid-preregistered.md`). The design turns on one observation that makes the fix both exact and cheap: **both halves of the measurement depend on the partition only through its group-size multiset** — `e80`'s pressure is evaluated on `random_partition(labels, rng)`, a size-matched relabelling, and `e12`'s target is the draw spread of that same size-matched control — so a profile is a legitimate object and concentration can be *set* rather than *found*. `flat` profiles have concentration exactly `1/k` at every circuit size and are therefore matched exactly; `harmonic` ones add a skew at the same `k`, so two cells at one concentration that disagree measure what concentration does not determine. Group counts `k` ∈ {2, 3, 5, 8, 13, 21, 34, 55, 96, 160} × shapes {flat, harmonic} = 20 cells per size × 3 sizes, at `e14`/`e74`'s protocol (3 seeds, 5 relabellings), one artifact per cell so the grid is resumable. **The statistic is the PARTIAL Spearman of the pressure spread against the measured draw spread, concentration partialled out of both ranks** — a raw rank correlation cannot separate "pressure predicts the draw spread" from "both grow with concentration", which is the confound `e86` could not remove. **Predictions:** partial positive at all three sizes; the raw pressure correlation above concentration's own at every size on the same twenty cells; partial ≥ +0.5 at d = 1307 (where the raw margin was +0.767 against +0.617); ≥ 7 of 9 per-seed partials positive. **Falsifier that matters: the partial at or below zero at two or more sizes** — then the pressure spread's ranking power is a concentration restatement everywhere and §4.3's predictor claim fails as stated. Cost measured: ≈ 24 / 44 / 93 minutes per size, **≈ 2.7 h total**. |
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
