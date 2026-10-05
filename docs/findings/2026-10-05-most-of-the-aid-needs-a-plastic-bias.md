# Most of the aid needs a plastic bias: one flag apart, the buffer keeps a quarter of what it was worth

*2026-10-05. `experiments/e427_most_of_the_aid_needs_a_plastic_bias.py` reads the corpus's `frozen_bias` control: one
configuration rolled twice at **40** replicates with `config.frozen_bias` the only field that differs, the draws
identical, plus two further suites rolled under the frozen bias at the same depth. `e417` found the buffer worth
nothing when the recurrent **body** never moves; this asks the same of the head's bias alone. No training, no probe.
Five claims, registered before this unit's pass over the runs.*

## 1. The four rolls

| roll | naive accuracy | naive mean forgetting | buffer gain | buffer cut |
|---|---|---|---|---|
| pair, **frozen bias** | 0.9306 | **0.0227** | **+0.0130** | **+0.0208** |
| pair, plastic bias | 0.9125 | **0.0750** | **+0.0484** | **+0.0784** |
| suite600, frozen bias | 0.9391 | 0.0258 | +0.0145 | +0.0222 |
| suite1440, frozen bias | 0.9280 | 0.0293 | +0.0158 | +0.0238 |

All four carry five arms (`naive`, `replay` and the three penalties) at forty replicates.

| claim | measured | verdict |
|---|---|---|
| BC1 the ledger is carried | `frozen_bias` alone differing, the draws identical, **40** replicates, **5** arms | **MET** |
| BC2 and the freeze takes most of the buffer's accuracy gain | **+0.0130** against **+0.0484**, **0.27** of it | **MET** |
| BC3 and most of its forgetting cut too | **0.0208** against **0.0784**, **0.27** of it | **MET** |
| BC4 and the freeze changes the arm that does nothing | the naive arm forgets **0.0227** against **0.0750** | **MET** |
| BC5 and the frozen buffer's gain is a constant of the suite | span **0.0028** over three frozen rolls | **MET** |

## 2. What the four say

**Three quarters of the aid lives in the head's bias.** With the recurrent body trained and only the bias frozen, the
buffer's accuracy gain falls from **+0.0484** to **+0.0130** and its forgetting cut from **0.0784** to **0.0208** --
the same **0.27** on both axes, so the shrink is not an artefact of one metric. `e417` showed the aid needs the body
to move; this locates most of what is left in the smallest movable part of the head.

**And the freeze changes the arm that does nothing.** The `naive` arm's own mean forgetting falls from **0.0750** to
**0.0227** when the bias is frozen -- a **+0.0523** difference on the same configuration and draws. So the corpus's
drift is not only the buffer's business: the bias is where the forgetting that a continual-learning metric measures
mostly happens, and freezing it removes it without any arm being changed.

**And the frozen buffer's remainder is a constant of the suite.** Over three frozen-bias rolls at forty replicates the
gain is **+0.0130**, **+0.0145** and **+0.0158** -- a span of **0.0028**, a sixth of the drop the freeze itself
causes. So what survives the freeze is small and stable, while what the freeze removes is the part that moves with the
configuration.

## 3. What it cannot settle

- **One configuration pair and three suites**: the plastic side is a single configuration at overlap 0.0, so nothing
  here says how the frozen-bias result moves with the overlap, the circuit size or the suite.
- **And one control**: `frozen_bias` is the corpus's own flag, so the head's weights with a free bias, or the body with
  a frozen head, are not in this reading.
- **And the suites are the overlap family**: all four rolls are the class-incremental line at `circuit_size` 800, so
  the earned-label world's frozen-bias behaviour is not here.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned -- and a frozen bias plausibly changes what is learned as
  well as what is forgotten, which this decomposition cannot separate.
- *And a ledger is not a mechanism.*
