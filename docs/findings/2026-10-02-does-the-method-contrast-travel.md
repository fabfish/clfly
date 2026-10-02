# The method contrast travels: fourteen of twenty-six and none against

*2026-10-02. Runs: none new — `experiments/e346_does_the_method_contrast_travel.py` reads every experiment in
`runs/` that carries both the `replay` and the `ewc-block` arm, with the corpus's repeat collapse applied and the
experiments then collapsed once more by configuration signature. Seconds. Writes
`runs/e346_does_the_method_contrast_travel.json`.*

## 1. The question `e276` left in one sentence

`e276` found the largest number on the network line: `replay` beats `ewc-block` on accuracy by **+0.0090 (3.30σ)**,
**+0.0441 (9.09σ)** and **+0.0618 (11.84σ)** across three forty-replicate configurations, and forgets less in all
three. Its own "what it cannot do" closed with the gap: *"nothing here says the `r32` ordering travels to another
substrate"*, and the missing measurement is the one that would say whether it does.

**The register already holds the other substrates**, and this unit reads them rather than running one. Twenty-six
experiments carry both arms with usable replicate lists: a circuit budget of **300** against the 800 those three
use, an evaluation suite at **600 and 1440 examples**, **three closed-loop runs** where the world is wired into
every forward pass, a **reversed task order**, a **class-incremental** suite, and the **fisher-batch** family. Each
is one vote, paired over replicates first and then over experiments.

## 2. The answer

| read | experiments | mean | sem | sigma |
|---|---|---|---|---|
| accuracy, every experiment | 26 | **+0.0390** | 0.0108 | **3.62** |
| accuracy, one vote per configuration | 22 | **+0.0471** | 0.0119 | **3.97** |
| accuracy, the `circuit_size = 300` subset | 7 | **+0.0994** | 0.0210 | **4.74** |
| forgetting, every experiment (negative is better) | 26 | **-0.0502** | 0.0151 | **3.33** |

**T1 MET**: 26 experiments read, 24 files the corpus's rule marks as second copies left out, and the experiments
collapse to 22 distinct configurations. **T3 MET**: the artifact-level mean is **+0.0390 at 3.62σ**, or
**+0.0471 at 3.97σ** with a configuration voting once. **T4 MET**: on the **300 budget** the advantage is
**+0.0994 at 4.74σ** — larger than on the 800 budget the three `e276` configurations use. **T5 MET**: `replay`
forgets less at the artifact level, **-0.0502 at 3.33σ**.

**And the sign is where the interesting part is. T2 FALSIFIER FIRED, honestly and narrowly.** The accuracy contrast
is positive in **20 of 26** experiments and negative in **six**:

| experiment | `replay` − `ewc-block`, accuracy | sigma |
|---|---|---|
| `e101_rate_fb128` | -0.0222 | 1.54 |
| `e101_rate_fb8` | -0.0208 | 1.43 |
| `e102_rate_fb8_rerun` | -0.0083 | 0.69 |
| `e164_fb8_today_a` | -0.0083 | 0.69 |
| `e8_class_incremental` | -0.0056 | 0.15 |
| `e102_rate_fb8_omp1` | -0.0014 | 0.10 |

**None of the six resolves**, and of the twenty that point the other way **fourteen resolve**. So the ordering
travels in the only sense that matters statistically: **fourteen experiments resolve the advantage in `replay`'s
favour and none resolve it against**, at every budget, both suites, the reversed order, the class-incremental
suite, the 600- and 1440-example evaluations, and the closed loop.

## 3. What the six have in common, and why it is not six independent votes

**Three of the six are one configuration executed three times.** `e101_rate_fb8`, `e102_rate_fb8_omp1` and
`e102_rate_fb8_rerun` share one configuration signature, and a fourth, `e164_fb8_today_a`, is the same
configuration as `e101_rate_fb8` on every field but one — `frozen_bias` written `false` where the older artifact has
no such key, which is what keeps the corpus's own repeat rule from merging them, since it asks for bit-identical
replicate lists. The six negatives therefore fall to **four distinct configurations**, and the configuration-level
estimate is the larger one for that reason.

**And five of the six are one knob's worth of runs.** Eleven experiments use `fisher_batches = 8` and two use 128,
against the twelve that use the 32 every one of `e276`'s three configurations uses; four of the six negatives are in
the first group and one in the second, and exactly one of the twelve at 32 is negative, the class-incremental suite.
The knob is the candidate this read can name, and it is named as a candidate: `e102_rate_fb128_rerun` is in the same
family and positive, and `e102_rate_fb8_omp1` and `e102_rate_fb8_omp4` are the same configuration at one and four
threads with the point estimate **-0.0014** in one and **+0.0139** in the other — the noise floor `e164` measured,
sitting inside this contrast. The honest reading of the six is not "six substrates disagree" but **one configuration
family, executed repeatedly, whose point estimate sits near zero**. Two knobs co-vary with the group — the
fisher-batch count above, and the **16-example replay buffer** (`replay_per_task = 16` against the 96 of `e276`'s
three, where the seven experiments at 96 carry **no negative sign at all**) — and neither separates on its own,
because the 300-budget runs, the largest positives in this table, use the 16-example buffer too.

## 4. What it cannot do

*The experiments are not independent*: several are the same runner at a different suite size, order or thread
count, they share a circuit and a seed stream, and the artifact-level sem treats them as exchangeable when they are
not. That is why T2 is a sign count, why the configuration collapse is reported beside the artifact-level one, and
why the estimate is unweighted — one substrate, one vote — rather than pooled over replicates. *It cannot separate
"the ordering travels" from "the ordering was the same experiment"*, because no run is made: every number here is
already on disk, and a substrate the corpus does not hold is not tested by it. *And `ewc-block` is one penalty*:
nothing here says `ewc`, `ewc-block-rand` or a different lambda behaves the same, and nothing here touches the basis
contrast, which the audits left a null.

## RE-READ 2026-10-02 — `e347`'s run joined the corpus and the counts moved by one

`e347` wrote a twenty-replicate run of the `fisher-batches 8` family at `circuit_size = 300`, and it carries both
arms, so this census now reads **27 experiments**: **21 positive and 6 negative**, with **15 resolving in `replay`'s
favour and none against** where the first read had fourteen. The artifact-level mean is **+0.0382 at 3.68σ** over the
twenty-seven, or **+0.0458 at 4.02σ** with a configuration voting once (23 distinct configurations); the
300-budget subset grows from seven experiments to **eight** and reads **+0.0892 at 4.28σ**; the forgetting contrast
stays negative at **-0.0492 (3.38σ)**. T1, T3, T4 and T5 stay MET and T2 stays FIRED on the same six negatives, none
of which is `e347`'s run — that run's own contrast is **+0.0177 at 3.11σ**, on the positive side of the count, which
is the subject of its own finding.
