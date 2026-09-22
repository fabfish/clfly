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

FlyWire adult brain, public release 783: 139,255 neurons, ~3.7M proofread
connections, with a systematic annotation table giving **flow, superclass, cell
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

*What is refuted:* the gap does **not** track task overlap. Across the
degree-preserving family the gap moves *opposite* to interference — overlap rises
8× while the gap falls by two-thirds. The first mechanism story was wrong.

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

*Controls (all required, or the claim is uninterpretable):* degree-preserving
double-edge swaps at several strengths, Erdős–Rényi at matched density, and a
matched-spectrum random graph. Note Erdős–Rényi is a **separate regime**, not the
end of the swap axis: it also destroys the degree sequence and makes `(I − W)`
near-singular, so the propagator conditioning changes too.

### C2 — Basis selection *(the core contribution)*

The best anchoring basis is a **biological module basis** — cell class, cell type,
hemilineage, or nerve — and it beats the neuron basis by more than
capacity-matched random partitions do.

*Status: **resolved** — best rung 42.2σ on the granularity ladder; 4 of the 5 annotation
rungs resolve too.* The five-rung table below is at 5 task seeds; re-running at **18
seeds** refines it to `side` 28.8σ, `cell_class` 12.1σ, `hemilineage` 9.3σ, `supertype`
4.3σ, `cell_type` 0.7σ — four resolved, and the fifth is the rung that is nearly the
diagonal. It is kept because the ladder (below) is measured against it: those five rungs
are what the annotation vocabulary offers, and four of them sit in the top 15% of the
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
already beats a matched random control at 24.8σ. **The optimum is mid-granularity** — 0.4σ at
0.979, peaking at 42.2σ near 0.540, declining to 17.8σ at 0.191 — a non-monotonicity the five
rungs could not see, having no rung between 0.50 and 0.83. And **the ladder's own best rung is
beaten at its own granularity**: `side` (0.501) has excess +0.00391 while `pool4` (0.540) has
**+0.00156**, 2.5× smaller, with the random control at that granularity (+0.01041) *worse* than
`side`.

So the honest form of the headline is: **granularity sets where you are on the curve; biology's
contribution is what the curve's height shows — and the fly's own annotation vocabulary
under-reports it by placing four of its five rungs where biology contributes almost nothing.**
The practical recommendation becomes **"pool the rarest cell types and anchor there"**, which
needs no new ontology and delivers a 2.5× smaller penalty than the best rung the fly's
annotation happens to provide.

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
`docs/findings/2026-09-22-predictor-no-unexplained-failure.md`). The sign test is the
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
(anisotropy of the task precision), and that is not yet well enough understood to

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
prior on more pairs.

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
| `e3_basis_selection.py` | C2 | basis ranking at matched capacity, analytic effect size | done — 7 of 8 rungs on the `--ladder` sweep, up to 42.2σ |
| `e5_anisotropy_axis.py` | — | task spectral richness vs penalty, decoupled | done — e2's confounded trend corrected |
| `e6_predictor.py` | C2 | candidate predictor, out-of-sample, with resolvability | done — +0.984 (+0.995 on the ladder), 13/13 measurable pairs |
| `e7_interference.py` | C4 | circuit overlap vs measured interference | done — anatomy carries zero signal; post-propagation predicts at +0.94 |
| `e8_rate_network.py` | — | the non-linear substrate, both settings, frozen-body control | done — replay 2.2–4.2σ, best when tuned |
| `e4_modularity.py` | C3 | never written | **C3 deprioritised** — its mechanism is contradicted by `e2` |

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
