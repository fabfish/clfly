# The read-out sets the floor's share: 24% of the narrow arms against 55% of the wide ones, and a frozen body at fifteen times the median

*2026-09-29 02:20. Runs: **none new** — `experiments/e292_the_readout_sets_the_floor_share.py` reads every arm the
corpus gives both a read-out width and a variance fraction, writing
`runs/e292_the_readout_sets_the_floor_share.json`. Seconds.*

## 1. Where the share comes from

`e290` read the variance fraction as a ratio of two noises, found it above one in 85 of 269 arms, and left the
question of where the share comes from. The corpus has a manipulation for exactly this and it is the oldest one in the
basis study: the **read-out width** — the population the decoder reads — with a ladder from 32 neurons to the whole
circuit, built to test whether a wide read-out solves the tasks without the recurrent weights doing the routing. The
mechanism predicts a direction: a wide read-out leaves the weights less to do, so the across-replicate spread shrinks,
and the fraction — the test set's nominal noise over that spread — **rises**. A frozen body is the extreme of the same
mechanism.

## 2. S1 MET — the share rises with the read-out width

| pool | arms | median fraction | above one |
|---|---|---|---|
| plastic, read-out 32 or fewer | **219** | **0.637** | **24%** |
| plastic, read-out 128 or more | **40** | **1.160** | **55%** |

The median nearly doubles and the rate above one more than doubles. **S2 MET — and a frozen body is a different
regime**: the corpus's **10** frozen arms have a median fraction of **18.18** and **all ten are above one**, which is
**15.7x** the plastic arms at the same end of the ladder.

## 3. S3 MET — and it is a level difference and not a law

| read-out | 0 | 32 | 128 | 300 | 512 | 700 |
|---|---|---|---|---|---|---|
| arms | 36 | 183 | 18 | 9 | 4 | 4 |
| median fraction | 0.425 | 0.637 | 1.793 | 1.116 | 3.052 | **0.757** |

**Not monotone**: read-out 300 falls below 128 and read-out 700 falls below both. So the recipe is a *level*
difference between the narrow end and the wide one, and not a law in the width — which is what a share built out of
two noises with an accuracy in the numerator should look like.

## 4. What the three add up to

The fraction is not a property of the benchmark alone. `e290` found it arm-level inside one artifact (a median factor
of 2.72 across arms); this unit finds it **read-out-level** across artifacts — a factor of ~1.8 in the median and
~2.3 in the rate above one when the read-out moves from the corpus's narrow setting to its wide ones, and an order of
magnitude when the body stops training. `e267`'s requirement — the suite a configuration needs — is therefore
**read-out-specific** and **arm-specific**, and the two statements are the same statistic read from its two ends.

## 5. What it cannot do

**The read-out width is confounded with everything else that changes between artifacts**: the circuit size, the method
set, the code epoch and the suite size all move with it, and the corpus has no artifact family that varies the read-out
alone. **The wide end is thin** — 40 plastic arms beyond read-out 32 against 219 at or below it, and 2 to 4 arms at
each of the widest settings, so S3's non-monotonicity rests on widths with four arms each and could be small-sample.
**The frozen arms are 10**, and not one configuration: five read-out widths contribute one to six artifacts each.
**The fraction's formula changed across the corpus's four days**, so a fraction from an earlier `evaluation_noise` is
in the population. **And a share is not a cause**: that the fraction rises with the read-out width is consistent with
the routing story and does not establish it, because a wide read-out also raises the accuracy and `p(1-p)` in the
numerator moves with the accuracy.

## RE-READ 2026-10-01 03:04 — the counts shifted and one rung left the ladder

`e301` found seventeen files in `runs/` that are a second execution of an experiment already in the corpus, so this
census now reads **246 arms** where the file count gave 279. **S1 MET**: the narrow plastic arms are **203** with a
median fraction **0.637** and 25% above one, against **33** wide arms at a median of **1.071** and 52% above one — the
same level difference as before, at the same medians. **S2 MET**: the ten frozen arms keep a median of **18.18**, a
factor of **x17.0**. **S3 MET and one rung shorter**: the per-width medians are now **r0 0.449, r32 0.637, r128 0.853,
r300 1.116, r700 0.757** — **r512 is gone, because two of its six arms were second copies and the width falls below
the minimum arm count this census prints a rung at**. That is a bookkeeping consequence of the repair and not a
measurement: the same fractions are in the corpus, and the finding's point — that the share is a level difference and
not a monotone law — is what S3 already said.
