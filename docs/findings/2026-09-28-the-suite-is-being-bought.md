# The suite is being bought: one of the three configurations that cannot see its own spread, re-run

> **Read 2026-09-29 00:15:** all three registered falsifiers fired. Z1's column is held-out and could not have held;
> the column that is on the training set is identical at 5 of 5 arms. Z2's failure is the denominator's movement, not
> the suite's. Z3 is met for eight of the ten arm-by-metric fractions.
> (`docs/findings/2026-09-29-the-suite-bought-eight-of-ten.md`)

*2026-09-28 23:35. Runs: **one launched** — `e8_rate_network` at the `e140_r32_methods_frozenbias_40reps`
configuration (cs 800, `readout_size` 32, `lam` 0.003, `--frozen-bias`, five arms, forty replicates, `--seed0 0`) with
the held-out suite raised from 48 to **200** per task, its artifact to be written as
`runs/e275_frozenbias_suite600_40reps.json` and read by `experiments/e275_the_suite_makes_it_visible.py`
(`runs/e275_the_suite_makes_it_visible.json`), whose claims are registered below.*

## 1. The item: an open item that became affordable

`e267` turned the benchmark's own noise block into the suite each configuration would need, and found **three** whose
every arm has its test-set floor at or above its replicate spread — configurations that cannot tell the test set from
the training. **`e269` then measured what a suite costs, held-out decision by held-out decision, and found it free**
next to the training that produces them. This unit spends that on the configuration whose requirement is the largest
of the three.

| run | suite | the five arms' variance fractions |
|---|---|---|
| `e140_r32_methods_frozenbias_40reps` | 144 items | **2.086, 1.112, 1.293, 1.104, 1.309** — every one above 1 |
| `e275_frozenbias_suite600_40reps` | **600** items | predicted `144/600` of those: 0.50, 0.27, 0.31, 0.26, 0.31 |

The new run has the **same configuration and the same seed sequence**; only the suite moved. That is what makes the
comparison a price for the measurement rather than for the experiment.

## 2. The registered claims, before the data

- **Z1 — the training did not move.** Every arm's per-replicate **training** column (`learned`, the per-task accuracy
  on the training set) is **identical** between the two runs, because the seeds and the configuration are the same.
  This is the built-in control: if the training columns differ, the two runs are not the same experiment and nothing
  below is a price for the suite. **Falsifier**: any arm whose training column differs.
- **Z2 — and the floor falls by the ratio of the suites.** The test-set variance scales as `1/n_eval`, so each arm's
  fraction should fall by `144/600`; the check allows a factor of 1.5 either way, because the *replicate spread* is
  itself a draw between two runs and not only the floor moved. **Falsifier**: any arm outside that band.
- **Z3 — so the configuration becomes readable.** Every arm's fraction is below 1 in the new run, where all five were
  at or above **1.10**. **Falsifier**: any arm at or above 1.

**The module reports its own absence rather than a number**, so while the run is in flight it refuses all three and is
**not yet in `tools/gates.sh`** — a gate entry whose data has not landed is a red gate for a reason that is not a
defect, which is `e266`'s arrangement and the reason this row names no artifact under `runs/` for the run itself.

## 3. What it would mean either way

**If Z1 to Z3 hold**, the corpus contains a configuration that could not see its own noise and now can, for the price
`e269` measured — and the item `e267` opened closes with a demonstration rather than an argument. **If Z1 fails**, the
two runs are not the same experiment and the unit has produced a control failure rather than a price; that is the one
outcome that would make the whole comparison uninterpretable, which is why the control is a claim and not a check.
**If Z2 or Z3 fail**, the floor does not scale as `1/sqrt(n_eval)` at this configuration — a statement about the
binomial model the benchmark's own block assumes, and a larger one than the item it was bought to close.

## 4. What it cannot do

**One configuration of the three**, chosen because its requirement is the largest, so nothing here says the other two
behave the same way. **Forty replicates** estimate each arm's spread on thirty-nine degrees of freedom, so a fraction
near the boundary of 1 is a factor-of-1.1 statement and not a sharp one. **Z2 is a band** because the replicate spread
moves between runs as well as the floor. **`frozen_bias` removes most of the training variance**, which makes this the
easiest case in which to see the floor at all — the opposite of a hard test. And the run is **one seed sequence**, so
it replicates the configuration's *visible* spread and not the claim it was read for.
