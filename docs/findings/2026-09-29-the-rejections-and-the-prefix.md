# The rejections and the prefix: the pairing rule discarded a replicate-count mismatch, and the pairs it recovers cannot carry the test

*2026-09-29 01:05. Runs: **none new** — `experiments/e287_the_rejections_and_the_prefix.py` reads the rejections
`e286` never read, writing `runs/e287_the_rejections_and_the_prefix.json`. Seconds. **A third suite size for the
frozen-bias configuration is being trained beside this unit** (1440 items, forty replicates, the same five arms and
the same seeds: the same forty models evaluated on a third sample), which is what the last section is for.*

## 1. The sentence `e286` wrote from the counts

`e286` ran a census under two pairing rules and reported the gap in a sentence: the weak rule admitted 28 pairs, the
training fields kept 3, and *"twenty-five … are the corpus's four days of runner changes"*. The counts were read; the
rejections were not. This unit reads them, and it finds the sentence wrong in a way that changes what the census is.

## 2. Y1 — the rejections are a replicate-count mismatch

Every rejected pair is compared key by key, over the config keys both sides record and the keys only one side records:

```
repeats                      24      (unrecorded) save_theta         9
(unrecorded) readout_seed    19      frozen_body                    3
readout_seed                  4      anchor_bias, fisher_from, partition_seed, support_seed, save_fisher   1 each
```

**Y1 MET — `repeats` in 24 of 25 (96%).** The dominant mismatch is not an epoch change: it is that one run made five
replicates and the other forty. The runner seeds its replicates `seed0 + 100 * r`, so **two runs of one configuration
at different replicate counts share their first replicates by construction**, and `e286`'s rule refused a pair whose
replicate *lists* had different lengths — which is not the same as refusing one whose *training* differs.

Second and third in the table are worth their own line: the read-out **draw** differs in 23 of the rejections (19 of
those recorded on one side only, where `e286`'s rule treated the missing record as no disagreement), and
`frozen_body` — a manipulation, and one that is **not in `e286`'s shape list** — differs in 3. So the weak rule was
permissive in exactly the two ways its own finding warned about, and the strong rule is what closed both.

## 3. Y2 — the prefix is a licensed pairing, and it adds three sample swaps

Pairing on the shared prefix, which the seed scheme licenses:

| pair | suite | prefix | arms |
|---|---|---|---|
| `e109_second_order_r128.json` → `e119_r128_test480.json` | 144 → 1440 | 5 | 1 |
| `e112_readout300_plastic.json` → `e119_r300_test480.json` | 144 → 1440 | 5 | 1 |
| `e112_readout300_plateau.json` → `e119_r300_test480.json` | 144 → 1440 | 5 | 1 |

**Y2 MET — the census is six, not three**, and the three new ones are all in the read-out widths (128 and 300) that
`e286` named as the axis its own pairs could not separate from the suite ratio.

## 4. Y3 — and the three cannot carry the test

**Y3 MET — none of their six comparisons resolves.** At five replicates the interval for a variance ratio is
`[r/9.60, r·9.60]`, so an interval contains 1 for any ratio between 0.10 and 9.60 — and their observed sd ratios run
**0.485 to 1.726**, with three of the six *above* 1:

| pair | metric | sd ratio | 95% interval | resolved |
|---|---|---|---|---|
| `e109`→`e119` | final_accuracy | 0.964 | 0.097 to 8.93 | no |
| `e109`→`e119` | mean_forgetting | 0.485 | 0.024 to 2.26 | no |
| `e112_plastic`→`e119` | final_accuracy | 1.121 | 0.131 to 12.07 | no |
| `e112_plastic`→`e119` | mean_forgetting | 1.726 | 0.310 to 28.62 | no |
| `e112_plateau`→`e119` | final_accuracy | 1.121 | 0.131 to 12.07 | no |
| `e112_plateau`→`e119` | mean_forgetting | 1.726 | 0.310 to 28.62 | no |

So the prefix pairs are **consistent with the fall `e286` measured and do not corroborate it** — which is the honest
reading of a five-replicate ratio whose own error is about 50%. And the arithmetic says what it would take: the fall
`e286` measured is a variance ratio near **0.64**, and resolving that at 95% needs **80 replicates per side**, twenty
times the prefix these pairs have.

## 5. What is being trained beside this unit, and why

`e286`'s test of the sample-size account is an *ordering* between two suite ratios, and the two ratios are confounded
with read-out width: the pairs that barely moved are read-out 128 and 300, the pair that moved by half is read-out 32.
The corpus cannot break that confound — every within-pair comparison holds the read-out fixed, and every cross-pair
one changes it. So the run launched with this unit adds a **third sample to the read-out-32 configuration**: the same
forty models, the same configuration, the same seeds, evaluated on a **1440**-item suite instead of 144 or 600. That
makes the sample-size question askable *inside one configuration* — three suite sizes, one model set — which is a
scaling check rather than an ordering test, and it is the only way the confound can be broken without changing a
second variable at the same time.

## 6. What it cannot do

**The prefix pairing assumes the seeds line up**, which the runner's scheme licenses and which nothing in the
artifacts records directly: a runner that chose replicate seeds another way would be mispaired here, and this unit
would read that as a sample swap. **Five replicates** put about 50% on an sd ratio, so Y3 is a statement about
resolution and not about the size of the effect; the new pairs neither confirm nor refute `e286`. **The rejection keys
are compared over the keys both sides record**, so a pair that differs only in a key one side records is typed by
nothing and lands in the `(unrecorded)` rows, which count a key per side rather than per pair. **The prefix pairs are
three five-replicate configurations**, so nothing generalises beyond them. And **the third sample is being trained**:
the confound section says what it is for, and no number from it appears here.
