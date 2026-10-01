# It does not replicate on another seed stream

*2026-10-02. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak {1.0, 0.35} --seed0 4` -- read by `experiments/e337_does_it_replicate_on_another_stream.py`
against `e333`'s pair at `--seed0 0`.*

## 1. The question that sat under four units

`e333` measured `replay`'s mean forgetting **rising 0.0375 at 2.45 sigma** when the world's channel acquired a
transition rule, on five replicates at `--seed0 0`. Four units then went after it:

    e334   not the stored features fitting worse     0.32 sigma on the loss the arm minimises
    e335   not the buffer's contents differing       byte-identical, element by element
    e335   not the body drifting further             the carried body moved 2.93% LESS
    e336   not the update's direction differing      not a reproducible quantity at five replicates at all

And `e336` left a question **under** all four: its within-run cosines sit on the 0.0625 random-overlap floor of their
own 256-dimensional subspace, so at five replicates a seed stream carries very little information about a
configuration -- and every number in the chain comes from **one** stream.

**So this unit asks the effect itself of a redraw**: `e333`'s two worlds again, at `--seed0 4` instead of 0, five
replicates each, everything else the same. The replicate seeds are `4, 104, 204, 304, 404` against
`0, 100, 200, 300, 400`.

**T1 MET.** Each stream's two runs agree on circuit, read-out, task names, replicate count, cue symbols, cue noise
and world state count, and differ only in the leak; the two streams' seed schedules differ.

**T4 MET.** And the first stream reads exactly what `e333` read: **+0.0375 on a sem of 0.0153, i.e. 2.45 sigma** --
so this reader is measuring that object and not another.

## 2. And the sign flips

| stream | instantaneous | carried | Δ forgetting | σ | Δ accuracy | σ |
|---|---|---|---|---|---|---|
| `seed0 = 0` | 0.0479 | 0.0854 | **+0.0375** | 2.45 | −0.0222 | 0.94 |
| `seed0 = 4` | 0.0958 | 0.0188 | **−0.0771** | **3.36** | +0.0181 | 1.26 |

**T2's falsifier FIRED.** The registered claim was that the sign replicates; on the second stream the world with a
rule makes `replay` forget **0.0771 less**, at **3.36 sigma** -- resolved, and in the opposite direction. **T3 MET**,
and that is worth reading carefully: the second stream's difference is **2.06 times** the first's *in magnitude*,
so a claim stated on size alone would have been met by a sign reversal. **T4 MET**, which is what makes the reversal
a statement about the effect and not about this reader.

**So the thread's headline effect is not a property of the world.** Two redraws of the seed stream give
**+0.0375 at 2.45 sigma** and **−0.0771 at 3.36 sigma**: both resolved, both above 2.4, in opposite directions. The
honest description of `e333`'s measurement is that it is **that stream's**, and the honest description of the effect
is that at five replicates it is **not distinguishable from a redraw**.

**And that reframes the four units that came after it.** `e334` and `e335` each excluded a mechanism, and both
exclusions stand -- the stored features do not fit worse, the buffer's contents do not differ, the body does not
drift further, the direction is not reproducible. What does **not** stand is the premise they were excluding
accounts *of*: they were four mechanisms for an effect whose size and sign are not stable across a redraw, and none
of them could have found that, because each was measured on the same single stream.

## 3. What it says

**The most useful thing in this thread is now a statement about its instrument.** `e336` found that five replicates
put a *direction* on its noise floor; this finds that five replicates put the *retention difference itself* on
theirs. The two are the same lesson at two levels, and it is the lesson `e307` and `e308` reached from a different
direction in this corpus's earlier work: **a contrast at five replicates is a point estimate with an unmeasured
redraw**, and a resolved sigma is not a substitute for a second sample.

**What survives is the ordering, and it was never in question here.** `e331` measured `replay` ahead of every
penalty arm on the noisy environment at 4.4 to 7.6 sigma; that contrast is between arms **within** a stream and does
not depend on a redraw the way a difference between two *configurations* does. The lesson is specific: a
configuration against a configuration, at five replicates, on this task, is a coin; an arm against an arm is not.

**And the next unit is a design, not a mechanism.** Making the loop's effect measurable needs either many more
replicates -- `e328` needed forty to put a forget-rate difference at 1.92 sigma and that was on a saturated task --
or a **paired** design, in which the two worlds' runs share a seed's trajectory so that the redraw cancels. Neither
exists in this corpus for the closed loop, and the second is the cheaper of the two.

## 4. What it cannot do

**Two streams**: another redraw would change the answer again, and two points give a span and not a standard
deviation -- the honest statistic across two seeds is the pair, and nothing here estimates how the effect is
distributed over streams. *Five replicates per run*: that is the design's stated weakness and this unit does not fix
it, it measures it. *One arm*: `naive`, `ewc` and the block arms are not run, so whether the instability is
`replay`'s or the task's is not separated. *One circuit, one read-out width, one task and one pair of worlds*:
`e332`'s other sign is not asked, and the worlds compared are `leak = 1.0` against `leak = 0.35` and not the space
of channels between them. *And a failed replication does not say the effect is absent*: it says the effect is not
separable from a redraw at this replicate count, which is a statement about the design and not about the world.
