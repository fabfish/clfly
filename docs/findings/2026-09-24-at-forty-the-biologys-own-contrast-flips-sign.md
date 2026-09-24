# At forty replicates the biology's own contrast flips sign — the five-replicate control was the favourable draw

**Date:** 2026-09-24
**Artifact:** `runs/e140_r32_methods_plastic_40reps.json` — five methods, forty replicates, the paper's hardened
configuration at read-out 32, with `--replay-per-task 96 --replay-batch 8` (five-replicate comparator
`runs/e135_r32_methods_plastic.json`).
**C0a, and it is exact:** the `naive` and `ewc` rows are **per-replicate identical to `e133`'s forty values,
worst absolute difference 0.000** — so a run whose replay settings differ from `e133`'s (96/8 against 16/16)
reproduces them bit-for-bit, which is the registration's C0a and a second confirmation that the replay settings
are unused for those methods.
**The frozen-bias arm is still running; this reports the plastic arm.**

---

## 1. The first forty-replicate five-method table

| method | forgetting | sem | accuracy |
|---|---|---|---|
| `naive` | +0.0750 | 0.0088 | 0.9125 |
| `ewc` | +0.0654 | 0.0079 | 0.8856 |
| **`ewc-block`** (biological `cell_class`) | **+0.0573** | 0.0070 | **0.9168** |
| **`ewc-block-rand`** (matched random) | +0.0779 | 0.0099 | 0.9054 |
| **`replay`** | **−0.0034** | 0.0034 | **0.9609** |

Paired against `naive` over the forty shared seeds: `ewc` **−0.0096 ± 0.0080 = 1.21σ** (18/40 — reproducing
`e133`), `ewc-block` **−0.0177 ± 0.0085 = 2.09σ** (24/40), `ewc-block-rand` **+0.0029 ± 0.0102 = 0.28σ** (15/40),
and `replay` **−0.0784 ± 0.0084 = 9.35σ** (38/40). The ordering by forgetting is
**`replay` < `ewc-block` < `ewc` < `naive` < `ewc-block-rand`**.

## 2. And the contrast that isolates biology **reverses**

**The paper's central network claim is that what resolves is *granularity* and not the fly's grouping, because the
biological partition never beats its size-matched random control.** At forty replicates that contrast is

| | `ewc-block` | `ewc-block-rand` | **block − rand** |
|---|---|---|---|
| five replicates (`e135`) | +0.0604 | **+0.0438** | **+0.0167** — biology *worse* |
| **forty replicates (`e140`)** | +0.0573 | **+0.0779** | **−0.0206 ± 0.0099 = 2.08σ**, 28/40 negative — biology *better* |

**So the sign reverses**, and the decomposition says where it came from: the biological row barely moved
(**0.0604 → 0.0573**, −0.0031) while **the control's row rose by +0.0341** (0.0438 → 0.0779). **The five-replicate
"no advantage" was largely a favourable draw of the matched-random control**, and that is exactly what rule 10
warns about — one draw is one sample from the population of size-matched random partitions.

**And this session measured that population's spread**: two draws of the *same* arm on the same forty seeds differ
by **0.0138**, with a per-seed sd of 0.0658 (`docs/findings/2026-09-24-the-draw-moves-the-control-by-0014.md`).
A five-replicate mean also carries a seed sem of ≈0.025 at this sd. **So the +0.0341 move is inside the combined
noise — and that is the point: the contrast at five replicates was not merely unresolved, it was a sign that
forty replicates do not reproduce.**

**And at forty replicates it still does not resolve**, at **2.08σ** against the project's 3σ convention — **while
being a single-draw measurement whose control can wander by about the size of the effect** (one draw moves the
mean by 0.0138 against a contrast of 0.0206). **So the honest statement is: the strongest measurement of the
paper's central contrast is 2.08σ in favour of the biology, and it is not yet a measurement of the population
rather than of one draw.**

## 3. What this changes, and what it does not

- **It contradicts a sentence in the paper, plainly.** §4.7 says of this contrast *"it resolves nowhere"* and that
  its sign is *"reproducible at every one of them"*. **At forty replicates it is 2.08σ and its sign is the
  opposite of the five-replicate value at the same Fisher batch count.** The paper is updated in this fire.
- **It does not overturn the central claim, and it does not establish it either.** 2.08σ is below the project's
  convention, the measurement is single-draw, and §4.2's `ewc-block-rand` row has *never* been draw-averaged —
  so the honest form is *"the biology's own contrast is the strongest it has ever been measured and is not
  resolved, and its five-replicate value is not reproduced"*.
- **It explains a recorded volatility rather than repeating it.** The earlier record found the `ewc-block-rand`
  row moving between runs and attributed it to the environment; **the draw is a second, independent source of the
  same volatility on this row**, and until today the runner could not vary it.
- **And it registers the follow-up**: two more control draws for the **base** family (the same command with
  `--partition-seed 1` and `2`, `--methods ewc-block-rand`), so that the paper's central contrast is quoted as
  **block minus the mean of three draws** rather than against one. The harder family's three draws are already
  running for exactly this reason.

## 4. The follow-up, launched and specified rather than named

**Two more draws of the base family's control are running**: the identical command with
`--methods ewc-block-rand --partition-seed {1,2}`, forty replicates each, writing
`runs/e140_r32_rand_draw{1,2}.json`. Draw 0 is the `ewc-block-rand` row of `runs/e140_r32_methods_plastic_40reps.json`
itself, so the three-draw control needs no fourth run.

**How the contrast will be read, registered before the draws land**: `ewc-block` against the **mean of the three
draws**, over the same forty seeds, with the standard error's two components reported separately — the
between-draw term (**2** degrees of freedom at three draws) and the ordinary paired one. **P1**: the three-draw
contrast stays **negative and at least as large as the single-draw 2.08σ**, i.e. the biology's advantage was not
the favourable draw. **Falsifier**: the three-draw contrast is **within 2σ of zero**, which would say the 2.08σ
was the draw rather than the biology — the same falsifier form the harder family's registration uses, for the same
reason.

**And the threshold is quoted in the units this session measured**: with the draw sd at about **0.0138** over
three draws, the control's contribution to the standard error is roughly **0.008**, so a 3σ three-draw contrast
needs an effect of about **0.024** — and the single-draw 0.0206 is just under it. **So the honest expectation is
that the three-draw measurement lands near its own bar**, which is rule 37's situation and is why the form of the
reading is registered here rather than chosen afterwards.

## 5. And it is not the eighth trap: both tasks move the same way

**The project's eighth measurement trap is that an aggregate can be the cancellation of two resolved
components**, and the diagonal is exactly that shape: at these forty seeds `ewc` improves task 0's forgetting by
**−0.0355 (3.79σ)** and *worsens* task 1's by **+0.0162**, so its unresolved mean is a trade. **The paper's central
contrast is not that shape**:

| `ewc-block` − `ewc-block-rand` | value | resolution |
|---|---|---|
| **task 0** | −0.0198 | **1.38σ** (22/40 negative) |
| **task 1** | −0.0214 | **2.27σ** (26/40 negative) |
| mean of the two | −0.0206 | 2.08σ |

**Both terms are negative and neither resolves on its own, so the 2.08σ aggregate is a fair summary of two terms
that move together** — weak in size, consistent in sign, and the opposite of the diagonal's cancelling shape.
**So the central contrast's weakness is its magnitude and not its shape**, which matters for what could change it:
a draw of the control, not a different summary.

**And the matched random control behaves as a same-size random partition should**: against `naive` it is
**−0.0016 ± 0.0157 = 0.10σ on task 0 and −0.0042 ± 0.0126 = 0.33σ on task 1** — indistinguishable from the
baseline on both, i.e. it constrains nothing useful. That is the control doing its job, and it is the first time
this project has said so at forty replicates on this family.

**For contrast, the two contrasts that *do* resolve resolve consistently across tasks**: `replay` − `naive` is
**−0.0906 ± 0.0137 = 6.63σ** on task 0 and **−0.0661 ± 0.0096 = 6.91σ** on task 1, and `ewc-block` − `naive` is
1.36σ and 1.60σ. **So on this configuration the resolved contrasts are resolved on both tasks and the unresolved
ones are unresolved on both** — the diagonal is the single exception, and it is the one the paper's §4.2 caption
was written about.
