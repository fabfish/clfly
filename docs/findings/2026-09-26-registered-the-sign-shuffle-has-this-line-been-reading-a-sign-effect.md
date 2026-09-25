# Registered: the sign shuffle — has this line been reading a topology effect that is a sign effect?

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written: `runs/e215_signshuffle_rs0.json` …
`rs2.json` (three realizations, one cell each).

---

## 1. The confound this design exists to test

`erdos_renyi` in this project's rewiring module draws its edge set uniformly **and assigns every edge a random sign**
(`erdos_renyi(..., signed=True)`), while the alloy of the last hour preserves the connectome's **own** weights and
moves only their targets. The tasks are not built from an unsigned graph: `tasks.build_tasks` propagates assemblies
through `stable_weights(circ.net, rho)`, i.e. through the **signed** synapse matrix. So the sign pattern is part of the
substrate the tasks live in.

**Which means every contrast this line has made against `erdos_renyi` has changed two things at once**: the wiring
*and* which synapses are excitatory. C1's own statement of what is supported — *"the connectome's task subspaces are
7× more orthogonal than chance, and rewiring monotonically destroys that (up to 5× more aligned than chance at
Erdős–Rényi)"* — attributes that to the wiring, and the free parameter it has not separated is the sign pattern. The
same applies to every ER cell in `e207`'s join, to the tight high regime (0.14134–0.14897 over eight cells), and to
the interval `[0.23632, 0.27135]` this week's work identified as where the penalty changes.

**`signshuffle` moves only the second of the two.** It keeps the edge set, the per-row edge counts and the multiset of
weights **exactly**, and permutes the pairing of a weight to an edge (checked on a toy graph: the (row, col) set is
identical, the sorted weights are identical, per-row edge counts are identical, and 72% of the weights move).

## 2. The design

One command, three realizations (the last week's lesson: one drawing is not a measurement):

```
experiments/e2_topology_gap.py --circuit-size 800 --support 80 --seeds 3 --seed0 0 --q 0.02 \
  --topologies signshuffle --rewire-seed {0,1,2} --no-realized \
  --json-out runs/e215_signshuffle_rs{0,1,2}.json
```

**Cost (rule 49)**: 225–240 s per cell measured from `e213`'s ten cells, so **three cells ≈ 12 min**, one command per
realization on an idle machine.

## 3. The claims

**X1 — the sign pattern moves the tasks' alignment.** The three cells' `all_pairs_alignment` is **at or above 0.20**
(i.e. inside the hole's upper half, where only Erdős–Rényi and one alloy drawing have ever reached). **Falsifier**:
below **0.0912** — not even in the band — which would say the sign pattern does not move the task geometry at all and
the ER alignment must be an edge-set effect; **null**: in the band but below 0.20, which would put signs among the
constructions that populate the lower half.

**X2 — the sign pattern carries the penalty's jump (the confound's test).** The three cells' analytic excess is **at
or above 0.10** — approaching the ER band of 0.14134–0.14897, and twice the alloy's mean of 0.05136. **Falsifier**:
at or below **0.06**, i.e. sign shuffling leaves the penalty near the alloy's, in which case the jump between the
alloy and Erdős–Rényi is a property of the **edge set or the degree sequence** and the sign confound, while real, is
not the driver; **null**: 0.06–0.10.

**X3 — reported, not claimed**: the three cells' `top_eig_share`, `effective_rank` and `flattening` beside the same
statistics for the alloy, the swap and ER cells, so the construction-by-construction table can be read in one place.

**And the reading that follows whichever way it goes**: if X2 is met, then every ER-based contrast in this record
carries a sign effect and the paper's C1 sentence has to say so; if X2's falsifier lands, then the topology story
survives its first confound test and the sign pattern is a *separate* axis this project has not varied.

## 4. What this cannot do

- **Separate signs from magnitudes.** The shuffle permutes the whole weight (sign and count together), so a change
  could come from moving the *excitatory/inhibitory* assignment or from moving the larger counts; separating those
  needs a second null that permutes only the sign.
- **Give a distribution.** Three drawings, so a range and not an sd.
- **Speak for the other degrees of freedom**: the same test at the *task* level (rebuilding the tasks from a
  sign-shuffled wiring while keeping the graph) is a different experiment and is not this one — here the wiring is
  shuffled once and the three seeds' tasks are built inside it, the same way every other cell in the family is made.
- **Speak for other circuit sizes or for the network substrate.**
