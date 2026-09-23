# E92 — the concentration-matched grid: the prediction, written before any cell is measured

**Date:** 2026-09-23
**Script:** `experiments/e92_grid_profiles.py` (measurement, one cell per invocation),
`experiments/e92_grid_report.py` (report); artifacts `runs/e92_grid_cs*_{shape}_k*.json` (none at the time
of writing; in flight now)
**Context:** `docs/findings/2026-09-23-the-cross-size-test-is-not-well-posed.md`

---

## 0. What was written when

Sections 1 to 6 below were written and committed as `e2280f5`, **before the grid was launched**, and the
launch command is the one in §5. Two amendments were made afterwards, both while the first grid cells were
still being measured and **before any cell had been scored** — no report had been run over a grid artifact:

- §3's paragraph fixing which form carries the gated verdict (the absolute spread, for continuity with
  `e86`), added because the original text said "the pressure spread" without naming a form, which would
  have left the gate selectable after the fact;
- §4's caution table, which uses only the **nine named partitions**' existing artifacts and no grid cell.

Both are recorded here rather than silently folded in, because a pre-registration whose text can move
after the launch is not one. A reader who wants the untouched prediction should read §4's clauses as they
stand and ignore §3's second paragraph and §4's second half.

## 1. What is being fixed

`e86` closed the cross-size test of the spread statistic as **not well-posed**, and the reason is not
statistical. The nine partitions of `e80`/`e72` are named by their annotation pooling, and a pooling that
leaves 29 groups at d = 1307 leaves a handful at d = 952. Measured concentrations:

| size | concentration range of "the same nine" | verdict |
|---|---|---|
| d = 952 (cs = 300) | 0.006 – 0.754 | bimodal: four rows at 0.690–0.754, five at 0.006–0.159 |
| d = 1307 (cs = 800) | 0.020 – 0.536 | the size the effect was found at |
| d = 1874 (cs = 1500) | 0.034 – 0.324 | pending |

So "the same row" names a different partition at each size, and the 1–1 split between d = 1307 and
d = 952 is a statement about the design as much as about the statistic. Two features of the d = 952 set do
the damage: four of its nine rows sit at concentration 0.690–0.754 — near-duplicates, two of which are
**the same run stored twice** — and they occupy four of the nine ranks at the top of every ordering, which
concentration captures by construction. Restricted to the fine end (concentration < 0.6, n = 5) all three
candidates tie at +0.900.

## 2. The design

**The observation that makes both the fix and the cost small.** Neither half of the measurement depends on
the partition itself, only on its **group-size multiset**:

- `e80`'s pressure is evaluated on `random_partition(labels, rng)` — a size-matched relabelling — so which
  neuron sits in which group never enters the number;
- `e12`'s target is the draw-to-draw spread of that same size-matched control's excess.

A **profile of group sizes** is therefore a legitimate object of study, and it lets concentration be *set*
rather than *found*. Two profiles at different circuit sizes with the same group sizes have the same
concentration by construction, so **cell *i* of the grid names the same region of partition space at every
size** — which is exactly what the nine labels failed to do.

**The grid.** Group counts `k ∈ {2, 3, 5, 8, 13, 21, 34, 55, 96, 160}`, log-spaced, times two shapes:

- `flat` — groups as equal as possible, whose concentration is **exactly `1/k`** and therefore identical at
  every circuit size even under rounding. This half of the grid is matched *exactly*, not approximately.
- `harmonic` — sizes declining as `1/r`, a Zipf-like profile, which at the same `k` is much more
  concentrated, because one group holds a large share of the neurons.

Twenty cells per size, three sizes (cs = 300, 800, 1500 → d = 952, 1307, 1874), at `e14`/`e74`'s protocol
(3 task seeds, 5 size-matched relabellings), so a cell is comparable to the nine it replaces.

Two shapes at one `k` are two points at two concentrations, so the grid is over concentration rather than
over shape — and where two cells land at the same concentration and disagree, that disagreement is a
direct measurement of what concentration does *not* determine.

## 3. The statistic, and why it is the one that matters

The raw rank correlation of the pressure spread against the measured draw spread cannot distinguish

- *"the pressure spread predicts the control's draw spread"* from
- *"both grow with concentration"*,

which is precisely the confound `e86` could not remove. The pre-registered statistic is therefore the
**partial** Spearman correlation, concentration partialled out of both ranks:

> **partial = Spearman(spread, measured sd | concentration)**, on ranks throughout, reported per size.

A positive partial is the claim in the only form a concentration restatement cannot fake. It also does not
need the partitions to be the same objects across sizes to be interpretable at each size — which is why the
grid is the *companion* design and not a prerequisite.

**Both forms of the spread are scored, and the gated clauses are on the absolute one.** `e80`'s primary
candidate was the *relative* spread, `sd / mean`; `e86`'s headline figure, +0.767 against concentration's
+0.617, was the *absolute* one. Since `e86` is the result being repaired, the gated verdict follows its
form, and the relative form is reported beside it on the identical cells. This choice of which form carries
the gate was written here **while the first grid cells were already being measured but before any cell had
been scored** — no report had been run over a grid artifact — so it could not have been steered by a
result. The two forms disagree, they cannot both be read as "the" result, and reporting only one of them
would be the fitting this project has paid for before.

## 4. The clauses

**Predictions.**

- **P1** — the partial is **positive at all three sizes**.
- **P2** — at every size the raw Spearman of the pressure spread exceeds concentration's own raw Spearman,
  *on the same twenty cells*.
- **P3** — the partial at **d = 1307 is at least +0.5**. That size is where the raw winner was +0.767
  against concentration's +0.617, so if the effect is real there, partialling cannot remove most of it.
- **P4** — at least **7 of the 9** per-seed partial correlations are positive. The companion per-seed
  column holds the task geometry fixed; three seeds per size is thin, so the clause is a count and not a
  test.

**Falsifiers.**

- **F1** — the partial is **at or below zero at two or more sizes**. Then the pressure spread's ranking
  power is a concentration restatement everywhere and the predictor claim, as the paper's §4.3 states it,
  **fails**. This is the falsifier that matters, and it is a live risk: at d = 952 the *raw* ordering
  already reverses, and the concentration-given-pressure partial there is +0.852 against the raw +0.832.
- **F2** — the raw ordering reverses at some size even on twenty matched cells. Then the size dependence is
  a property of the circuit and not of the design, and §4.3's "supported at exactly one circuit size" is
  the wrong reading — the reading would be "size-dependent" instead.

**Secondary, reported but not gated.** The same partial on the nine named partitions, computed from
`runs/e86_spread_at_other_sizes.json`, so the grid's answer can be read against the design it replaces; the
relative form of every clause above; a bootstrap over the twenty profiles; leave-one-profile-out leverage
on the partial; and the duplicate-cell check, since two cells at the same concentration are a genuine test
rather than a defect.

**A caution on the partial itself, learned from the nine before any grid cell was scored.** The nine named
partitions already give partials for both forms, and they disagree in a way that is a warning about the
instrument:

| set at d = 952 (n = 9) | raw vs measured sd | ρ with concentration | partial | concentration, given the spread |
|---|---|---|---|---|
| absolute spread | +0.412 | +0.160 | +0.509 | **+0.852** |
| relative spread | +0.882 | **+0.950** | +0.531 | **−0.040** |

The relative form's partial, +0.531, is *higher* than the absolute form's +0.509 — which is not what a
variable that is a restatement of the confound should produce — but its rank residual has almost no
variance left (ρ = +0.950), so the ratio is computed on a small denominator. The mirror-image number,
concentration's partial given the spread, is −0.040 for the relative form, and that is nearly forced by the
same collinearity rather than being independent evidence. **Both readings are therefore fragile**, and the
grid's value is that its cells have concentrations set by construction, which is the property the nine
lack — not that a partial correlation on twenty points is a strong instrument by itself.

## 5. Cost, and the command

Timed on this machine with `e86` still running: d = 952 costs 2.20 s per pressure call and 7.70 s per
analytic excess, d = 1307 costs 3.86 / 14.76, d = 1874 costs 7.61 / 33.04. A cell is 15 pressure calls and 5
excess calls, so a cell is ≈ 72 s / 132 s / 279 s and a size is ≈ 24 / 44 / 93 minutes. The whole grid is
**≈ 2.7 h of compute**, runnable at any time in any order because each cell is its own artifact.

```bash
for cs in 300 800 1500; do
  sup=$([ $cs = 300 ] && echo 30 || ([ $cs = 800 ] && echo 80 || echo 150))
  for shape in flat harmonic; do
    for k in 2 3 5 8 13 21 34 55 96 160; do
      uv run python -u -m experiments.e92_grid_profiles \
        --circuit-size $cs --support $sup --k $k --shape $shape --seeds 3 --draws 5
    done
  done
done
```

## 6. What this will change in the paper

§4.3 currently reads *"the predictor-shaped use of pressure is therefore supported at exactly one circuit
size and untested elsewhere"*. If P1 holds the sentence becomes *"supported at three circuit sizes once
concentration is partialled out"*; if F1 fires the sentence becomes *"the spread statistic's ranking power
is concentration in disguise"* and the co-movement is left as the whole of the mechanism. Either way the
sentence that exists now is replaced, because "untested elsewhere" stops being true.
