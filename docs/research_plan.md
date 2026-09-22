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
first said. The measured gap on wiring-derived tasks is +45–63% of the oracle's
error against <1% in LGCL's random-rotation family.*

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
> draw" and "the floor is 62% learner" are three different corrections to three different lines, and
> none of them transfers — which is why each line needed its own check rather than a shared rule.
> (`docs/findings/2026-09-22-c2-passes-the-per-seed-discipline.md`)
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
and circuit size, it holds at **mean Spearman +0.984**, with **13 of 13** correct on
every matched pair whose excess difference clears 2σ (`experiments/e6_predictor.py`;
the 24/25 headline count includes one pair that is not measurable — see
`docs/findings/2026-09-22-predictor-no-unexplained-failure.md`). That count was re-derived with
the control-draw component included: it holds at **12 of 12** even if the fine columns' draw sd is
four times the estimate, with the sign record perfect at any multiplier from 0.1× to 10×, while
`side`'s individual σ at d=1307 falls from 15.53 to 4.47
(`docs/findings/2026-09-22-predictor-survives-draw-correction.md`). The sign test is the
decisive one: a predictor that only recovered `constrained_fraction` would score 0/25,
because matched pairs share it exactly.

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

**And at λ = 0.1 the rung contrast resolves — in the direction the neuron result predicts.** `e28`
put the coarsest rung at that λ, and both runs share seeds, so the two deltas can be contrasted
paired:

| rung (λ = 0.1, batches 8) | constrained | Δ accuracy vs its own control | σ paired |
|---|---|---|---|
| `side` | 0.6947 | **+0.0069 ± 0.0145** | 0.48 |
| `cell_class` | 0.9250 | **−0.0648 ± 0.0245** | **2.65** |
| **`side` − `cell_class`** | | **+0.0718 ± 0.0336** | **2.13** (same sign in all 3 replicates) |

So the coarse rung is better than the fine one at 2.13σ, opposite signs at the same λ — but **it wins
because the finer rung loses, not because it gains**: `side`'s own delta is +0.0069 (0.48σ, nothing)
while `cell_class`'s is a resolved *disadvantage*. Not the neuron-level mechanism, which had the
coarse grouping genuinely better than random
(`docs/findings/2026-09-22-rung-question-resolved-at-lambda-0.1.md`).

The cross-run comparison assumes an `ewc-block` arm is independent of the run's method list, and
**that is now verified bit for bit**: `e31` reproduced both arms across the two method lists
identically to the last decimal. That check had to be run deliberately — every cross-run comparison
in this line depends on it, and none of them could have detected a violation, because a violation
would have looked exactly like the difference between configurations they were measuring.

Three open items remain: n = 3 (the sem carries ~50% relative
error); the two intermediate rungs are still λ = 1.0 only, which is what decides between a gradient
and a step; and the mechanism — the coarse rung wins because the fine one *loses to its own control*
(−0.0648, 2.65σ), not because the coarse one gains (+0.0069, 0.48σ).

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
| `e2_topology_gap.py` | C1 | excess vs topology along a swap family, four arms | done — mechanism refuted at 32.7σ |
| `e3_basis_selection.py` | C2 | basis ranking at matched capacity, analytic effect size | done — 7 of 8 rungs resolve; 2.8–7.9σ once the control-draw component is included |
| `e5_anisotropy_axis.py` | — | task spectral richness vs penalty, decoupled | done — e2's confounded trend corrected |
| `e6_predictor.py` | C2 | candidate predictor, out-of-sample, with resolvability | done — +0.984 (+0.995 on the ladder), 13/13 measurable pairs |
| `e7_interference.py` | C4 | circuit overlap vs measured interference | done — anatomy carries zero signal; post-propagation predicts at +0.94 |
| `e8_rate_network.py` | — | the non-linear substrate, both settings, frozen-body control | done — replay 2.2–4.2σ, best when tuned |
| `e3_basis_selection.py --ladder` × d=1874 | C2 | second configuration (support 150, d=1874), 12 seeds | **in flight** — `runs/e9_ladder_d1874.json` |
| `e3_basis_selection.py --ladder` (re-run) | C2 | per-seed excesses for a paired shape test + determinism check | **in flight** — `runs/e3_ladder_v2.json` |
| `e8_rate_network.py` × 5 rungs | C2b | synapse annotation ladder (0.6947 → 0.9992) | **four rungs and stopped** — all nulls at λ = 1.0, 3 of 4 with biology *below* its matched control, none resolving (largest \|σ\| = 0.58), floors ≥0.05 and `supertype` cost 3.43 h. `cell_type` was started and stopped on four independent grounds (`e35`'s bound, `e44`'s cost, `e38`'s power, and the three rungs that can carry a claim already being measured) |
| `e4_modularity.py` | C3 | never written | **C3 deprioritised** — its mechanism is contradicted by `e2` |
| `e12_control_spread.py` | C2 | how much of a matched-pair delta is the control *draw* | done — draw sd is ~1.1e-3 coarse, ~4e-5 fine; coarse-rung σ are provisional |
| `e3 --control-draws K` | C2 | average the matched control over K draws | done — wiring validated; the K=3/K=4 runs are queued behind the CPU queue |
| `e2_topology_gap.py --rewire-seed` | C1 | separate the swap *realization* from the circuit subsample | done — realization sd measured at 0.00125 for `swap2` (16× below the attributed 0.0205); ER moves by 0.00047, 0.33% of its own value |
| `e2_topology_gap.py --circuit-size 700` | C1 | the sixth point of the size sweep, and the test of the geometry reading | **in flight** — prediction pre-registered in the `e36` finding |
| `e36_geometry_carrier.py` | C1 | is the 367% spread a realization effect or a geometry effect? | done — geometry; the contrast's *sign* is a function of the effective rank of the task precision, ρ = +1.000, exact p = 0.0083 |
| `e5_anisotropy_axis.py --topology` | C1 | `e5`'s concentration intervention applied at a *rewired* topology | done, all four configurations — at `swap2`/cs = 800 the knob is **inert** (rule 18) so that config is untested; at `swap2`/cs = 300 it has **30×** leverage and the prescribed metric gives **+0.143, +0.214, +0.357**, the mechanism's *direction*, unanimously and none significant over a non-monotone curve |
| `e38_variance_budget.py` | C2b | what limits the network benchmark, and is `--test 480` the lever? | done — it is learner seed-to-seed variability, not measurement; the pairing claim is unresolved (+0.02 [−0.65, +0.67] at n=9) and the `--test 480` gain is bounded at 1.28× |
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
| `e59_separation_with_both_components.py` | C1 | every σ here is one of two — how strong is each headline claim about the *rule*? | done — **98%+ of a single point's variance is the wiring draw** (realization sds 0.00377 / 0.00320 against seed sems 0.00025 / 0.00047). ER separation **364.9σ about these graphs, 26.1σ about the rule** (was 152σ); C1 contrast **28.8σ / 2.7σ** (was 32.7σ) — and 2.7σ is a *lower bound* because `swap0.5` has no realization sweep |
| `e3_basis_selection --extra-bases --seeds 18` | C2 | per-seed storage for the named annotation bases (`e58`), the family the headline is stated on | **in flight** — `runs/e58_bases_18seeds_perseed.json`; 1.31 h the first time and the current code stores the field |
| `e8_rate_network --lam 0.1 --repeats 16` | C2b | the properly-powered rung contrast at λ = 0.1 (`e46`), the λ where it resolves | **in flight** — `runs/e46_c2b_powered.json` |
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
