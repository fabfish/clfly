# The ladder's plateau is circuit-specific — by 2×, not 16×, and only the like-for-like quantity says so

**Date:** 2026-09-25
**Read of:** `runs/e73_ladder_named_head_to_head.json`'s `ladder_rows` (d = 1307, the `delta` quantity) against
`runs/e83_ladder_d1874_robustness.json`'s `pool_ladder` (d = 1874, **the same `delta` quantity**), with
`runs/e79_ladder_d1874_perseed.json` as the *other* d = 1874 analysis and the source of this finding's first error.
**Corrects an earlier version of this finding written an hour earlier**, whose headline — "the optimum moves from
`pool4` to `pool64`, sixteen times coarser, and on the second circuit there is no interior optimum at all" — was an
artefact of comparing two different quantities.

---

## The correction first

The first version of this read took d = 1307 from `e73`'s `delta` — *the biological partition's advantage over its
group-size-matched random control* — and d = 1874 from `e79`'s `excess_mean` — *the distance from the analytic
oracle*. **Those are different questions**, and they have different shapes: the matched-control quantity has an
**interior optimum**, while the oracle-distance quantity is **monotone toward the coarsest rungs** (0.014713 at
`pool1` down to 0.001208 at `pool64`/`pool128`). Comparing them produced a 16× shift and the disappearance of the
interior optimum. **A fourth look at the corpus found the right artifact**: `e83_ladder_d1874_robustness.json`'s
`pool_ladder` is the d = 1874 ladder in the **same `delta`** as `e73`'s rows.

## The like-for-like comparison

| rung | d = 1307 — `delta` (n = 12) | d = 1874 — `delta` (n = 12) |
|---|---|---|
| `pool1` | +0.000191 ± 0.000026 | +0.000353 ± 0.000036 |
| `pool2` | −0.008007 ± 0.000343 | −0.005859 ± 0.000084 |
| **`pool4`** | **−0.008844 ± 0.000199** | −0.007218 ± 0.000181 |
| **`pool8`** | −0.006852 ± 0.000221 | **−0.007763 ± 0.000169** |
| `pool16` | −0.007651 ± 0.000197 | −0.005898 ± 0.000102 |
| `pool32` | −0.006986 ± 0.000192 | −0.005014 ± 0.000082 |
| `pool64` | −0.005485 ± 0.000269 | −0.004068 ± 0.000181 |
| `pool128` | −0.004094 ± 0.000229 | −0.004801 ± 0.000196 |

| | d = 1307 | d = 1874 |
|---|---|---|
| minimum rung | **`pool4`** (−0.008844) | **`pool8`** (−0.007763) |
| rungs within 2 sem of the minimum | **{4}** | **{8}** |
| interior optimum? | **yes** | **yes** |
| `pool1` (no pooling) worst? | **yes** | **yes** |

**So: the lesson transfers, the plateau is one rung wide on both circuits and interior on both, and its location
moves from `pool4` to `pool8` — a factor of two, not sixteen.**

## What this does to the mechanism, and to the hole it fills

**The mechanism is better supported at 2× than at 16×.** `pool_below` is an **absolute neuron count**, so the same
rung merges fewer labels on a larger circuit and the optimum should sit *coarser* there: the circuits differ by
**1.43×** and the optimum moved by **2×**, which is the direction and roughly the size the mechanism predicts. The
16× figure was too large for a 1.43× circuit — it was the sign that the comparison was wrong, and the correction
removes it.

**And the two d = 1874 analyses disagree in shape, which is the informative part**: the *matched-control* question
has an interior optimum at `pool8`, while the *distance-to-oracle* question is monotone to the coarsest partition.
**The metric decides the shape** — the lesson §6 of the paper draws about the ratio metric, appearing again one
level up, between two ways of scoring the same ladder. **The ladder's lesson is a statement in the matched-control
quantity**, because that is the quantity the paper's claim is about.

**And the two ladders differ in a second field, deliberately: `--support`.** The d = 1307 ladder drives **80**
neurons per task and the d = 1874 one drives **150** — **10% of the circuit in both**, which is the line's
convention rather than an accident. So the comparison above is *"the same relative support at two sizes"*, and that
matters for the mechanism: **the support scales with the circuit and the pooling threshold does not**, and that
asymmetry — a *relative* design knob against an *absolute* rung — is exactly the kind of thing that can move an
optimum. A third circuit is registered below to separate them; without it, "the optimum moves 2×" is a statement
about a comparison in which two things changed and one of them (support) changed on purpose.

**And it is a fourth time this night that the right artifact was already on disk**: `e83` is the file that makes the
like-for-like comparison available, and the first version of this read did not look for it.

## What this cannot settle

- **Two circuits are two points.** The shift (2×) is consistent with the size ratio (1.43×) but does not show the
  optimum is a function of size: a third circuit would say whether it tracks size, the vocabulary, or neither.
- **`e3_seeds18.json` is the d = 1307 ladder at eighteen seeds** and this read did not use it: its
  `topologies["real"]` rungs are not named `bio:pool*` like `e79`'s, so a like-for-like pull needs its own look.
  **So the first circuit's plateau at 18 seeds is not checked here.**
- **Both ladders are twelve seeds**, so each rung carries its own resolution and the "one rung wide" claim is read
  at 2 sem rather than tested as an interval.
- **And the first version of this finding stood for an hour.** It was caught by looking for *another* artifact of
  the same kind rather than by any audit: the numbers in it were all correct and its error was entirely in which
  two numbers to compare.
