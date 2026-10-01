# What the time axis costs

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive,ewc,ewc-block,ewc-block-rand,replay --sequence --json-out runs/e324_sequence_five_as_built.json`
(603 s), read by `experiments/e324_what_the_time_axis_costs.py --json-out
runs/e324_what_the_time_axis_costs.json`, against `runs/e317_five_as_built.json` (612 s).*

## 1. The run this closes

`e322` measured that every task in this benchmark delivers a stimulus equal to its first step **exactly**, so the
trial's time axis carried nothing. `e323` built the first writer that changes with time -- one symbol for the first
half of the trial and another for the second, labelled by their ordered pair -- and measured on the **frozen**
network that the connectome carries the first symbol across the boundary (+0.25 above chance at its worst) while the
read-out decodes the conjunction only weakly (+0.083). Both were statements about the substrate before any training.

`e8_rate_network` gained a `--sequence` flag, and because `make_sequence_suite` returns the same `RateTask` as the
sustained builder, **the five arms ran on it unchanged** -- which is what `e323` predicted. The comparison is against
`e317`'s sustained run at the same circuit, the same read-out subset and the same seeds, so the two artifacts differ
in exactly one field.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out subset `59926518137c`, five replicates on every arm of both
runs, and **no config field differing** once the builder and the output path are excluded.

## 2. The claim that held, and the two that were refuted

`delta` is the sequence run minus the sustained one, paired by replicate index.

| arm | sustained | sequence | Δ accuracy | σ | Δ forgetting | σ |
|---|---|---|---|---|---|---|
| `naive` | 0.8111 | 0.6042 | **−0.2069** | 15.01 | **−0.0896** | 3.44 |
| `ewc` | 0.7542 | 0.5611 | −0.1931 | 5.40 | −0.0375 | 0.59 |
| `ewc-block` | 0.7208 | 0.5792 | −0.1417 | 5.06 | −0.1146 | 2.36 |
| `ewc-block-rand` | 0.8097 | 0.6097 | −0.2000 | 7.83 | −0.0563 | 1.31 |
| `replay` | 0.9250 | 0.6417 | −0.2833 | 26.67 | +0.0250 | 0.93 |

**T2 MET, and it is the largest effect in the table.** `naive` reads **0.2069 lower** on the sequence suite at
**15.01 sigma**. A trial whose label requires a symbol to be carried across a boundary through which its drive has
stopped is a much harder task for every arm: the drops run from 0.14 (`ewc-block`) to 0.28 (`replay`) and every one
resolves above 5 sigma.

**T4's falsifier fired, and in the opposite direction to the registration.** The claim was that the time axis raises
what a task costs the one after it, on the reasoning that the state now has to hold a symbol the next task
overwrites. `naive`'s mean forgetting is **−0.0896**, i.e. it forgets **less** on the sequence suite, at 3.44 sigma --
and four of the five arms move the same way (`ewc-block` −0.1146 at 2.36, `ewc-block-rand` −0.0563, `ewc` −0.0375),
while the one arm that moves the other way is `replay` (+0.0250 at 0.93). So the registered mechanism is refuted:
a trial with a time axis, on this substrate and at this circuit, loses less to the next task and not more. What it
costs instead is level: every arm's accuracy falls by at least 0.14 while its forgetting does not rise.

## 3. And the line's headline contrast does not survive it

**T3's falsifier fired.** `replay` is still the best arm on the sequence suite -- 0.6417 against `ewc-block-rand`'s
0.6097, `naive`'s 0.6042, `ewc-block`'s 0.5792 and `ewc`'s 0.5611 -- but the **contrasts** are not what they were:

| contrast | sustained (`e317`) | sequence (`e324`) |
|---|---|---|
| `replay` − `ewc` | +0.1708 at **4.74** σ | +0.0806 at **2.49** σ |
| `replay` − `ewc-block` | +0.2042 at **5.77** σ | +0.0625 at **3.20** σ |
| `replay` − `ewc-block-rand` | +0.1153 at **5.92** σ | +0.0319 at **0.92** σ |

Every contrast roughly halves, and the one that was the **strongest** on the sustained suite -- against the
size-matched random control, 5.92 sigma -- falls to **0.92 sigma**, below resolution. So `e276`'s twelve-sigma
headline and `e321`'s finding that it survives the **order** inversion are both statements about a suite with no time
in it: put one in, and the strongest of the three contrasts stops resolving.

That is the sharper form of what `e321` measured. The order inverts the **size** of these contrasts and never their
sign; the time axis moves the size further and takes the weakest of the three under the bar entirely. A benchmark
that wants to report `replay` against the penalty arms has to say which trial it means.

## 4. What it cannot do

**Five replicates per arm**: the paired standard errors run from 0.003 (`replay`'s accuracy) to 0.026 (`naive`'s
forgetting), so T3's `ewc-block-rand` contrast at 0.92 sigma is unresolved rather than absent, and the run's own
noise floor reports that it detects accuracy effects above about 0.048. **Two suites at one circuit, one read-out
width, one penalty, one order**: the difference between them is the boundary **and** the four classes being ordered
pairs rather than singletons **and** the second noise draw, and nothing here separates them -- a sustained suite with
a *two-symbol* label and no boundary is the control that would. **The two runs are not the same trained models**,
since the labels differ and the gradients follow them, so every delta is the whole trajectory's. **Nothing here
closes a loop**: the sequence task's input still does not depend on the agent's output, so this is the benchmark's
first temporal task and not yet a game. **And the per-replicate seed is not in the artifact** -- `config_diff` is what
makes T1 here, because the corpus records no per-replicate seed field, which is the check `e321` should have used and
did not.
