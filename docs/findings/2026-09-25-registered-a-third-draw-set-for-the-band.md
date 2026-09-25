# Registered: a THIRD draw set, because the band's edges are two measurements wide

**Date:** 2026-09-25
**Registered before its run.** The pooling ladder at a second draw set moved its head from `bio:pool4` (2.28112) to
`bio:pool8` (2.10798), by 0.04938 — the middle outcome its registration had named — while the biological-minus-random
gap at the band held at 0.72 against a bar of 0.5
(`docs/findings/2026-09-25-c2s-peak-is-a-band-and-not-a-rung.md`). **Two draw sets give a difference and not a span**,
which is today's own lesson applied to today's own result: `δ`'s earlier sign reversal looked like a stable structure
until the third support draw dissolved it. So this adds the third.

---

## 1. What the three draw sets will be able to say

| rung | draw set 0 | draw set 100 | **draw set 200** |
|---|---|---|---|
| `bio:pool4` | **2.28112** (1st) | 2.05861 (2nd) | ? |
| `bio:pool8` | 1.44707 (7th) | **2.10798** (1st) | ? |
| `bio:pool64` | 1.71290 | 1.81345 | ? |
| `bio:pool128` | 1.61061 | 1.80211 | ? |
| `rand:pool4` | 1.21206 | 1.33737 | ? |

Three draws are 2 df and no good for a standard deviation, but they give the **span** of each rung — which is the
statistic today's support-draw work settled on — and they give the band's membership a count rather than a pair.
`bio:pool4`'s span so far is 0.22251 and `bio:pool8`'s is 0.66091, i.e. the largest single move in the table is the
rung that took the head.

## 2. The design

The same command as `e202`, `--seed0 200`, everything else from `e181`'s own config (rule 44):

```
experiments/e3_basis_selection.py --ladder --circuit-size 300 --support 30 --seeds 12 --q 0.02 \
  --align-top 16 --no-realized --topologies real --control-draws 1 --seed0 200 \
  --json-out runs/e204_ladder_d300_12seeds_seed0-200.json
```

**Cost (rule 49)**: `e202` at the same settings took **1758.9 s (29 min)** against `e181`'s 2653 s, and the earlier
price taken from `e181` alone was 1.5× conservative — so **20–45 min**, quoted as a range because the two measured
costs of the same command differ by 1.5×. One command on an idle machine.

**The read**: `e203` judges P1–P3 against `e181` as before, and the three-draw table is the comparison this
registration is about. The reader is extended to print the per-rung values **across** the draw sets it is given,
because that view — not the pairwise verdicts — is what a band claim needs.

## 3. The claims

**Q1 — the biological advantage is present again.** At draw set 200 the peak's `excess` exceeds **every** `rand:` rung's
by **at least 0.5** (draw sets 0 and 100: the peak beat its own size-matched control by 1.069 and 0.721). **Falsifier**:
a `rand:` rung comes within 0.2 of the peak — the band would then be a pooling-depth effect rather than a biological
one, which is the same falsifier P3 carried and the reason it is restated here rather than assumed. **Null worth
keeping**: a gap of 0.2–0.5, i.e. the advantage survives and shrank again.

**Q2 — `bio:pool4` is the stable member of the band.** Its excess at draw set 200 lies within **25%** of its mean over
draw sets 0 and 100 (2.16987), i.e. in **[1.627, 2.712]**. The claim is that the rung which *lost* the head is the one
whose value is stable — which is what the span above suggests, since pool4 moved 0.223 and pool8 moved 0.661.
**Falsifier**: outside **50%** (below 1.085 or above 3.255), which would say both members of the band move by a third
of their own size and the band is not a band. **Null worth keeping**: between 25% and 50%.

**Q3 — the head's value stays in a band of half a unit.** The **span of the peak's excess across the three draw
sets** is **below 0.5** (draw sets 0 and 100: 2.28112 and 2.10798, span 0.1731). **Falsifier**: a span at or above
**1.0**, i.e. the leading value moves by half its own size across draw sets and the table's *level* is as
draw-set-dependent as its order. **Null worth keeping**: between 0.5 and 1.0.

**A registered note rather than a claim**: the rungs' spans (pool4 0.223, pool8 0.661, pool64 0.100, pool128 0.192 so
far) are reported as they are. A *fine* rung's near-constancy would be as interesting as a coarse one's movement,
because the pooled bases' group sizes are the same across draw sets while their *labels* are not — the pooling is a
coarser partition of the same labels, so `pool4` and `pool64` are different objects at every draw set and not a
subsampling of one.

## 4. What this cannot do

- **A distribution.** Three draw sets are 2 df; the spans are descriptive and the pairwise differences are distances
  between specific samples.
- **Separate the task draw from the control draw and the rewiring.** All three come from `seed0`; to vary the task
  draw alone needs a flag that does not exist, which is why the unit under study is the *draw set*.
- **Speak for the network ladder.** Different instrument, 1.2–3.4 h per rung, and nothing here transfers.
- **Settle the band's membership.** Three draw sets with two different heads make "one of pool4/pool8" a
  2-of-3 statement, not a rule.
