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

*Status after the analytic effect size: **resolved at 3 of 5 rungs.*** The earlier
"consistent direction, ~1.3σ" reading was limited by the realized-error metric, not
by the effect. Measured on the **analytic expected error** (exact, no sampling noise
— see `docs/findings/2026-09-22-analytic-expected-error.md`), the
biological-minus-matched-random delta is:

| rung | delta | σ |
|---|---|---|
| `side` | −0.00480 | **12.93** |
| `cell_class` | −0.00307 | **3.68** |
| `ito_lee_hemilineage` | −0.00280 | **2.61** |
| `supertype` | −0.00146 | 1.23 |
| `cell_type` | +0.00026 | 0.22 |

The deltas agree in magnitude with the realized-error estimates, so the analytic
estimator measures the same effect with ~8× smaller standard errors. **The fly's own
groupings do beat size-matched random partitions, at three rungs, up to 12.9σ** —
and the two rungs that show nothing are the two the granularity result predicts
should show nothing (`supertype` and `cell_type` are ≥0.97 constrained, i.e. nearly
the diagonal).

The strongest basis in the ladder is `side`: four left/right/centre groups beat a
random 4-group partition of identical sizes at 12.9σ. The coarsest structural split
in the annotation table is the most valuable anchoring basis in it.

*What is also resolved:* **granularity beats biology as the headline.** The excess
is monotone in `constrained_fraction` (0.004 at 0.50 → 0.017 at 0.999), so the
reliably useful thing is anchoring in *broader* groups. C2 says biology adds on top
of that, at 3 of 5 rungs.

*Predictive machinery:* LGCL v8 showed the diagonalisation penalty is a geometric
resonance requiring the anchoring basis to align with the task's precision basis.
The principal-angle scalar **fails** — raw alignment is anti-correlated with the
benefit, and adding an empirical chance level recovers only 3 of 5 orderings.
Spectrally truncating the task subspace (fixing a genuine range-space degeneracy)
does not improve it. It agrees on the top two and bottom one and misses in the
middle, where the differences are only 1–2σ, so re-testing it against the now-resolved
ordering is the next step rather than writing it off.

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

*De-risking:* "modular networks forget less" is folk wisdom (PathNet and friends),
so the claim must not be that. It must be the **quantitative interpolation curve
plus the mechanism link to C2** — that the reason modularity helps is that it makes
the module basis the aligned basis. The non-biological re-partition is the arm that
separates the two stories.

### C4 — Circuit overlap predicts interference

FlyCL tasks engage different circuits (olfaction → mushroom body, vision → optic
lobe, navigation → central complex). Each task is therefore naturally **partially
observed**, which by LGCL finding 4 puts the benchmark in the memory-dominated
regime. The prediction: **circuit overlap between two tasks predicts the
interference between them.**

This would give the benchmark a property no existing CL suite has — a
biology-derived task-interference prior — and it is directly testable against the
measured interference matrix.

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

| Script | Claim | Deliverable |
|---|---|---|
| `e2_topology_gap.py` | C1 | gap vs topology, four arms |
| `e3_basis_selection.py` | C2 | basis ranking, predicted vs measured |
| `e4_modularity.py` | C3 | interpolated cross-module density vs forgetting |
| `interference.py` | C4 | circuit overlap vs measured interference |
| `e5_observability.py` | — | full vs partial regime, against LGCL's 12.7× |

Every figure carries its control arm. The prediction scoreboard, including
failures, goes in `docs/findings/`.

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
