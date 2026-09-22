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

*What is refuted:* the gap does **not** track task overlap. Across the
degree-preserving family the gap moves *opposite* to interference — overlap rises
8× while the gap falls by two-thirds. The first mechanism story was wrong.

> **And that refutation is configuration-specific.** It rests on a single contrast,
> `swap0.5 → swap2`. Re-measured with per-seed storage and matched rewiring strength
> (swap fraction 0.912–0.924), the contrast is **+0.03525 at d = 952 (21.8σ paired)**,
> **−0.00304 at d = 1010 (4.8σ paired)**, and −0.01079 at d = 1307 (32.7σ unpaired). `real` and
> `swap0.5` hold to **4–12%** across the whole sweep while `swap2` moves by a factor of **4.7** —
> and 3.3× of that happens between d = 952 and d = 1010, a **6% change in circuit size**. So the
> sign is positive at one point and negative at two, the gap between them spans an order of
> magnitude, and neither conditioning (which behaves oppositely at the two extremes) nor subsample
> composition (ruled out by the flat controls) explains it. **The honest status is "refuted at
> d = 1307, reversed at d = 952, and not a stable object across the sweep"**, and the mechanism
> question is open again rather than settled
> (`docs/findings/2026-09-22-c1-refutation-does-not-replicate.md`,
> `2026-09-22-swap2-scale-sweep-partial.md`). Three more sweep points are running and they decide
> between "anomaly at d = 952" and "unstable across subsamples".

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

*And the sign is not topology-free.* In the `e2` scale sweep — where the **wiring** is
the variable and `flattening` is a consequence of it rather than an intervention —
`swap2` shows the **opposite** sign: its most anisotropic point (flattening 0.0235) has
the *smallest* excess and its least anisotropic (0.2334) the largest, while `real` and
`swap0.5` follow the direction above. So the relation here is a statement **at fixed
topology**, and applying it where the wiring varies is not licensed. `swap2`'s flattening
also spans **895%** across the sweep against `real`'s 4.2%, which localises that anomaly
to the propagated task spectrum rather than the filter
(`docs/findings/2026-09-22-swap2-geometry-anomaly.md`). The test is `e5`'s own
intervention applied at a rewired topology — cheap, and not done.

*Controls (all required, or the claim is uninterpretable):* degree-preserving
double-edge swaps at several strengths, Erdős–Rényi at matched density, and a
matched-spectrum random graph. Note Erdős–Rényi is a **separate regime**, not the
end of the swap axis: it also destroys the degree sequence and makes `(I − W)`
near-singular, so the propagator conditioning changes too.

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

Biological minus matched random: **−0.0116 accuracy, 0.43σ paired** — the biological partition is
slightly *worse* and does not beat the naive baseline, so **the rung hypothesis is not supported**:
the network negative is not an artefact of having measured the wrong granularity. But the run only
bounds the advantage at **≈0.09 accuracy**, because the benchmark's own per-repeat sd is 0.048
(0.077 for forgetting). Detecting a 0.01 effect would take 86–202 repeats, i.e. **50–118 hours per
rung**, and five rungs remain. **Settling C2b is a benchmark-variance problem, not a rung problem**
(`docs/findings/2026-09-22-e10-side-rung-underpowered.md`).

Two consequences worth acting on. The rate-network JSON stores `replicates`, and the
bio-versus-control comparison is **paired by construction** while the printed summary reports
unpaired sems; the paired sem at `side` is 1.5× smaller, and the same lesson had to be learned
independently on the neuron ladder. And the variance, not the effect size, is now the binding
constraint on this question — which is the same shape as the frozen-body lesson.

*Remaining:* two rungs of the `e10` sweep are still queued, but they answer a weaker question than
the one above.

**Three of five rungs are now measured**, all at λ = 1.0:

| rung | constrained | biological | matched random | Δ accuracy | σ paired |
|---|---|---|---|---|---|
| `side` | 0.6947 | 0.8148 | 0.8264 | −0.0116 | 0.43 |
| `cell_class` | 0.9250 | 0.8426 | 0.8611 | −0.0185 | 0.35 |
| `ito_lee_hemilineage` | 0.9945 | 0.8333 | 0.8333 | 0.0000 ± 0.0305 | degenerate (mean in its own sem) |

All three are nulls with intervals of roughly ±0.03 accuracy, and none beats the naive baseline. Two
things about that: **λ = 1.0 is the λ at which the `cell_class` contrast is *smallest*** (−0.0185
against −0.0648 at λ = 0.1), so the rungs have been sampled where the effect is weakest — `e28` is
putting `side` at λ = 0.1 for that reason. And ±0.03 accuracy against a neuron-level effect of about
10% of the oracle gap means a network effect of that relative size would be invisible here
(`docs/findings/2026-09-22-ito-rung-and-degenerate-sigma.md`).

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
| `e8_rate_network.py` × 5 rungs | C2b | synapse annotation ladder (0.6947 → 0.9992) | `side` done — negative holds, but underpowered (bounds the advantage at ≈0.09 accuracy); four rungs queued |
| `e4_modularity.py` | C3 | never written | **C3 deprioritised** — its mechanism is contradicted by `e2` |
| `e12_control_spread.py` | C2 | how much of a matched-pair delta is the control *draw* | done — draw sd is ~1.1e-3 coarse, ~4e-5 fine; coarse-rung σ are provisional |
| `e3 --control-draws K` | C2 | average the matched control over K draws | done — wiring validated; the K=3/K=4 runs are queued behind the CPU queue |

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
