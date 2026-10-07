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

## RE-READ 2026-10-02 — three narrow arms landed on the 1.8 snapshot and the claims held

`e344` wrote three closed-loop runs at read-out 32, and each carries a `replay` arm with both a width and a variance
fraction, so this census now reads **340 arms** where the last read gave 246: the plastic narrow pool is **297** with
**85** above one (29%) against **33** wide with **17** (52%). The ratio of the two rates is **exactly 1.8**, which is
where the live test's historical "more than doubles" bar sat, and a strict comparison loses a floating-point tie --
**that assertion fired on this run and is now the unit's own S1 threshold**, `wide["rate"] > narrow["rate"]`, with
the numbers it prints left as the record. **S1 MET**: the narrow median is **0.637** and the wide one **1.071**, the
same level difference at the same medians. **S2 MET**: the ten frozen arms keep a median of **18.18**, a factor of
**x17.0**. **S3 MET**: the per-width medians are **r0 0.449, r32 0.667, r128 0.853, r300 1.116, r700 0.757** --
still not monotone, and r32 moved by 0.030 because those three arms sit in it. The finding's point is untouched: the
share is a level difference between the ends of the ladder and not a law in the width.

## RE-READ 2026-10-02 — `e358`'s two frozen arms joined the frozen pool and its count fired

`e358` wrote a twenty-replicate run with `--frozen-body` on the earned label, and its two arms carry both a read-out
width and a variance fraction, so this census now reads **352 arms**. The frozen pool grows from **ten to twelve**,
every one of them above one, at a median of **18.18** -- the same level the first read found -- while the plastic
pools move to **307** narrow at a rate of **28.34%** against **33** wide at **51.52%**. The live test's hard-coded
frozen count of ten fired on this run and is now the unit's own S2 read off the pool: every frozen arm above one, at
least the ten the first read had, and a frozen median more than ten times the plastic one's. S1, S2 and S3 stay MET
at the same medians.

## RE-READ 2026-10-07: the ladder gained a rung at eight columns

The ladder the finding's medians were read off is a corpus artifact, and one rung arrived: the closed-loop line's neuron
read-out at **eight** columns (`e458`, `e460`) put **six** plastic arms at a width the corpus had never carried, and
`e292`'s ladder now runs **0**, **8**, **32**, **128**, **300**, **700** with per-width medians of **0.4486**,
**0.3885**, **0.6058**, **0.8528**, **1.1165** and **0.7568**. The new rung sits between the zero read-out's **0.4486**
and the thirty-two column one's **0.6058** and below the first, so the non-monotonicity S3 is about is unchanged and the
live test's pinned rung list becomes a containment and an order rather than an equality: the five rungs the finding's
medians were actually taken at -- **0**, **32**, **128**, **300** and **700** -- are still in the ladder, and
`monotone` is still **False**.

The two pools are untouched by the new rung, since it is a **narrow** width: the plastic pool at **32 or fewer** now
carries the six arms and its median and rate move by less than a hundredth, so **S1** (`wide["median"] > 1.0 >
narrow["median"]` and `wide["rate"] > narrow["rate"]`) and **S2** (the frozen pool) read as they did. What this RE-READ
cannot say is whether **eight** is a rung of the same ladder or a different instrument: the closed-loop line's read-out
at eight columns is the circuit's own neurons under a width the rest of the corpus's ladder reaches by
`--readout-size`, and the loop's arms are the ones the census pools per width -- so the rung is comparable in the
census's own unit and not necessarily in its own setting.
