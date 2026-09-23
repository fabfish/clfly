# E99 — the reversed-ordering question at a smaller circuit, pre-registered

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, `e8_hardened_basis`'s configuration at `--circuit-size 300`;
artifact `runs/e99_rate_cs300_cell_class.json` (in flight).
**Context:** the plan's §8 item 2 and C2b, which have asked this since the first network run and have never
been able to answer it; and `docs/findings/2026-09-23-the-last-two-unaudited-sections-were-clean.md`, which
recorded that every rate-network artifact in this repository is at **cs = 800** — all 25 of them.

---

## 1. The question, and the configuration that has never varied

At cs = 800 with 32 Fisher batches (`runs/e8_hardened_basis.json`, 5 repeats, λ = 0.003), the block Fisher's
standing against its two references is:

| comparison, mean forgetting | gap | σ |
|---|---|---|
| block (bio) **+0.0604 ± 0.0201** vs its matched random **+0.0438 ± 0.0156** | **+0.0166** | 0.65σ |
| block **+0.0604** vs the neuron diagonal `ewc` **+0.0208 ± 0.0147** | **+0.0396** | 1.46σ |

**Neither resolves.** So the honest statement is the one the paper makes — the block's structure is not
distinguishable from the diagonal at this estimation budget — and the plan's §8 item 2 has said since the
beginning what would settle it: *"a configuration in which the block's structure **is** well estimated (a
smaller circuit, or a lower-rank task family)"*. **Every rate-network run in this repository is at cs = 800**,
so that configuration has never existed.

## 2. What is being changed, and what is not

`--circuit-size 300` alone, with `e8_hardened_basis`'s configuration otherwise **field for field identical**:
`--basis cell_class --lam 0.003 --fisher-batches 32 --normalise-fisher --repeats 5 --iters 500 --lr 0.003
--batch 32 --train 96 --test 48 --classes 4 --noise 1.0 --input-overlap 0.0 --readout-size 32 --shared-head
--support 80 --methods naive,ewc,ewc-block,ewc-block-rand,replay`. So the contrast is a **circuit-size
change at fixed everything else**, and the matched-random control is the size-matched relabelling of the
same synapse partition as always.

At d = 952 the trainable parameter count falls by roughly the square of the neuron ratio, so the **block
Fisher has far fewer entries to estimate from the same 32 batches** — which is the mechanism §8 names.

## 3. Predictions, written before the run

- **P1 — the negative replicates.** The biological block does **not** beat its matched random control at
  cs = 300, in the same direction as at cs = 800 (bio *worse* by +0.0166 there).
- **P2 — the gap shrinks, because the mechanism says it should.** The block-minus-diagonal forgetting gap is
  **smaller in magnitude** than cs = 800's **+0.0396**. A block Fisher estimated from the same 32 batches
  over fewer parameters should behave more like the diagonal it is a refinement of.
- **P3 — and it stays unresolved.** Neither contrast clears 2σ, because the benchmark's `naive` per-repeat
  sd is 0.048 and five replicates give a sem of ~0.02: **the resolution is not there at any affordable
  replicate count**, which is itself the answer to a question the plan has been carrying.

**Falsifier — and it is the informative direction.** The block-minus-diagonal gap is **larger** in magnitude
at cs = 300 than at cs = 800. That would say a *better-estimated* block Fisher is **worse**, which is
evidence against estimation quality being the limit and in favour of the reverse ordering being real: the
coarser the anchor, the more it hurts, and estimating it better only sharpens the penalty. That is the
reading the paper's §4.7 currently says is unresolved, and this is the run that would move it.

## 4. What this cannot settle

**One circuit size is one point.** If P2 holds, the finding is "the gap shrinks with circuit size, in the
direction the estimation-quality account predicts, and is resolved at neither" — which is a *weaker* claim
than the mechanism needs and a stronger one than the paper currently has. A second size (cs = 200, or the
lower-rank task family §8 also names) would be needed to call it a trend, and the task-family route is
cheaper than another circuit because it changes the suite rather than the substrate.

**And the figure of merit is the `naive` arm's own sd, not the sem.** `naive` at cs = 800 has a per-repeat sd
of 0.048 against a mean forgetting of +0.0729, so a 0.04 gap is *within one replicate's* spread however many
replicates are averaged — the sem shrinks, the per-observation spread does not. So an "unresolved" verdict
here means unresolved **at this benchmark's own noise**, which is the honest unit and the one §4.7's
variance-budget discussion already argues for.


---

## 5. Outcome, recorded against the clauses as written

**All three predictions hold and the falsifier did not fire.** The block is worse than its matched random
control at both sizes (+0.0167 and +0.0104; 0.65σ and 0.29σ), and the **block-minus-diagonal gap falls
from +0.0396 to +0.0167, a 58% reduction** — the direction P2 predicted. **P3 holds too**, and the reason
is worth keeping: the arms are individually *noisier* at cs = 300 (forgetting sems 0.0362 and 0.0432
against 0.0255 and 0.0250), so the gap shrank and the error bar grew, and the σ fell because the numerator
fell faster than the denominator rose. Two unanticipated results are in §4 of the results finding: the
**diagonal's advantage over `naive` disappears at the smaller circuit** (2.47σ → 0.25σ), and **`replay` is
best on both metrics at cs = 300**, so the network line's only resolved positive result replicates at a
second size. Full reading: `docs/findings/2026-09-23-the-reversed-ordering-question-at-a-smaller-circuit.md`.
