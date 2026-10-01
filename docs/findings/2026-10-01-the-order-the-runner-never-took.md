# The order the runner never took: one suite trained forwards and backwards, and the direction is unanimous

*2026-10-01 11:00. Runs: **two new** — `runs/e315_order_as_built.json` and `runs/e315_order_reverse.json`, written by
`e8_rate_network.py --circuit-size 300 --readout-size 32 --input-overlap 1.0 --train 96 --test 48 --iters 500
--repeats 5 --methods naive,ewc,replay` with `--task-order as-built` and `--task-order reverse`. About three minutes
each.*

## 1. The axis nobody had run

`e302`'s M4 found that **no permutation of any suite had ever been run**: every artifact in the corpus records its
suite's own naming order, so the block's promise of fixed task orders held trivially, because the order was a
variable with one value. `e310` measured from the retention diagonals what varying it would cost — the position
predicts the level a task reaches, by **four points of accuracy**, in 90% of the configurations — and named the run.

**This is the run.** `--task-order` is now a flag on the runner: `as-built` (the identity and the default, so every
earlier artifact's `config` still describes what it ran), `reverse`, or an explicit permutation. A full reversal of
three tasks is a **designed** contrast rather than a sample of orders, because it leaves one task's position alone:

| task | forwards | backwards | |
|---|---|---|---|
| `ov1_t0` | position 0 | position 2 | changes |
| `ov1_t1` | position 1 | position 1 | **does not** |
| `ov1_t2` | position 2 | position 0 | changes |

**P1 MET** — the two runs record the same suite reversed and **the same support-draw fingerprint**
(`66eac73cc91d`), the same seeds and the same methods, so the x-axis did not move with the manipulation.

## 2. The direction is unanimous and the magnitude is partial

`delta` is forwards minus backwards, paired over the five replicates:

| method | task | positions | delta | sigma |
|---|---|---|---|---|
| `naive` | `ov1_t0` | 0 → 2 | +0.0125 | 0.80 |
| `naive` | `ov1_t2` | 2 → 0 | −0.0208 | 1.58 |
| `ewc` | `ov1_t0` | 0 → 2 | +0.0458 | 1.90 |
| `ewc` | `ov1_t2` | 2 → 0 | −0.1000 | **2.63** |
| `replay` | `ov1_t0` | 0 → 2 | +0.0167 | 1.00 |
| `replay` | `ov1_t2` | 2 → 0 | −0.0208 | **3.16** |

**P3 MET, and unanimously**: **6 of 6** moved-position contrasts favour the run in which the task is trained **first**
— every sign is the position's, across three methods. **P2 fired as registered**: **4 of 6** clear one sigma, and the
two that do not are both `naive`/`ov1_t0` at 0.80 and (just) `replay`/`ov1_t0` at 1.00. So the direction is what the
position predicts without exception, and the magnitude is this configuration's: up to **3.16 sigma** and **0.10** of
accuracy on the largest.

## 3. The control, and the claim that was mis-specified

**P4 fired as registered** — and the registration was wrong, not the control. It compared each method's
unchanged-position task against the **smallest moved contrast of any method**, so `replay`'s control at 1.63 sigma was
read against `naive`'s 0.80. Taken **inside each method**, which is the comparison a reader wants:

| method | control sigma | smallest moved sigma | control is smallest |
|---|---|---|---|
| `naive` | **0.17** | 0.80 | yes |
| `ewc` | **1.51** | 1.90 | yes |
| `replay` | 1.63 | 1.00 | **no** |

So **the control holds in 2 of 3 methods**, and this is **reported and not claimed**: the registration asked a
cross-method question that no reader would. What the table says is that a task whose position is unchanged still
moves a little in `replay` — which is expected, because the tasks *around* it changed and so the gradients did — and
that the two-position contrast is the larger one in the two methods where the effect is strongest.

## 4. What this settles and what it does not

**Settled**: the order is a variable, `e310`'s position effect is reproducible as a *direction* in a designed
contrast, and the corpus's fixed-order promise is not vacuous — a benchmark that permutes its suite will move its
numbers. **Not settled**: *one configuration and five replicates*, so the magnitudes are this configuration's;
*a reversal is one permutation and not a sample of them*; *the three tasks are draws from one construction*, so
nothing here says which task is harder; and *the two runs are not the same trained models*, since the sequence
changes the gradients, so a difference is the order's effect on the whole trajectory and not a controlled
perturbation of one step. **And the flag is new**: the two artifacts are the corpus's first with a
`task_order` other than `as-built`, and `e302`'s M4 is now a statement about the corpus **before** this run rather
than about the runner.
