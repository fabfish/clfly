# The floor is not an independent draw: 85 of 269 arms where the nominal noise exceeds the total, and the effective suite that implies

*2026-09-29 01:46. Runs: **none new** — `experiments/e290_the_floor_is_not_an_independent_draw.py` reads the runner's
own source and every variance fraction in the corpus, writing
`runs/e290_the_floor_is_not_an_independent_draw.json`. Seconds.*

## 1. The premise the statistic carries

`e267` turns the benchmark's noise block into the suite each configuration would need, and this line rests on it:
`e269` priced a held-out decision, `e275` bought a suite with it, and `e285` to `e289` read the sample swaps it is
about. Its statistic is

```
variance fraction = (binomial sem of one accuracy at n_eval)^2 / (that arm's across-replicate variance)
```

read as *"is the test set's own noise as large as the spread you are trying to resolve"*. That reading carries a
premise nobody has stated: **that the binomial noise is an independent draw per replicate.** Under it, the measured
accuracy is `true + noise` with the noise independent across replicates, so the across-replicate variance is at least
the binomial variance and **the fraction cannot exceed one**.

## 2. Q1 MET — the suite is one draw, shared by every replicate

The runner builds its suite on **line 943 or 947** and opens its replicate loop on **line 1026**, so every replicate
of every arm is trained and evaluated against the **same held-out items**. The binomial noise is therefore a *common*
term across replicates and not an independent one, and sharing it does not add a component to the across-replicate
variance — it removes one, which is why the fraction has no upper bound.

## 3. Q2 MET — and the corpus says the premise fails, in 85 arms

**85 of 269 arms (32%) carry a fraction above one**, from **1.01 to 43.1**. Under the premise those arms are
impossible; with the suite shared they are expected. The extremes are the clearest because they are the arms with the
least training variance to hide behind:

| artifact | arm | fraction | implied effective count, of 144 |
|---|---|---|---|
| `e111_readout900_frozen.json` | naive | **43.06** | **3.3** |
| `e112_readout300_frozen.json` | naive | 26.37 | 5.5 |
| `e104_frozen_r128_frozen.json` | naive | 22.00 | 6.5 |

A frozen arm has almost no training-driven movement, so its across-replicate spread *is* its measurement noise — and
the corpus's own arithmetic then implies that a 144-decision held-out suite carries **about three independent
decisions** for that arm. That is the same conclusion the paper reaches from the other side, where it solves for an
*effective* **49** independent decisions against a nominal 144.

## 4. Q3 MET — so a suite's worth is an *effective* size, and it is arm-level

Where the fraction is at or above one, the nominal binomial variance is the only measured noise there is, and it
implies `n_effective = n_eval / fraction` independent held-out decisions. Over the 32 artifacts carrying three or more
arms, **31 have their arms more than 1.2x apart** in that number, with a **median ratio of 2.72** and a largest of
**7.42** (`e102_rate_fb8_omp4.json`, whose five arms span 0.171 to 1.273 in share). So "the suite this configuration
needs" is not one number even inside one artifact: the read-out and the method each set their own.

**What this leaves standing.** `e267`'s requirement is real arithmetic on a real artifact and this unit does not
overturn it. What it shows is *what the divisor is*: the nominal binomial variance of **one accuracy**, on a sample
every replicate shares — so the quantity a suite buys is an effective count, and the corpus's own route to that count
(3.3 of 144 for the frozen read-out-900 arm, 49 of 144 in the paper's solved case) is far below `n_eval`. That is
consistent with everything `e285` to `e289` measured, where the spread fell by less than `1/sqrt(k)` demanded.

## 5. What it cannot do

**The fraction is a ratio of two noises and not a decomposition**, so Q2 is evidence that the premise fails and not a
measurement of how the held-out items are correlated. **`n_effective` is defined only where the fraction is at or
above one**: below one the spread is larger than the nominal floor, the arm has real training-driven movement, and the
number is an extrapolation rather than a count — the module reports the two regimes apart for that reason. **The
source check is lexical**: it locates the suite's construction and the replicate loop in the runner's text, not a
dataflow, so a runner that built its suite elsewhere would read differently. **The corpus spans four days of runner
changes**, so a fraction computed under an earlier `evaluation_noise` formula is in the population and nothing here
separates the formula's epochs. **And neither `e267` nor `e269` is re-run**: what is new is the premise, the count of
arms where it fails, and the effective count that follows.

## RE-READ 2026-10-01 03:04 — the counts shifted and the three claims held

`e301` found seventeen files in `runs/` that are a second execution of an experiment already in the corpus, so this
census now reads **246 arms** where the file count gave 279 — and the eighteen arms it drops carried fractions above
one more often than the corpus average, so **Q2 moves from 85 of 269 (32%) to 77 of 246 (31%)**, still MET. **Q3 moves
from 31 of 32 artifacts to 29 of 30** with the median ratio **x2.64** and the largest **x7.42**
(`e102_rate_fb8_omp4.json`) unchanged. Q1 is a line-number claim and does not move. The premise Q2 refutes — that a
nominal binomial variance cannot exceed the total — is refuted at the same rate as before.

**RE-READ 2026-10-03: the live test's band lost its top edge, and nothing else moved.** The stored-artifact test
bounded the share of arms above their own floor at `0.25 < share < 0.35`, a band written when the share was about
thirty per cent; the window's closed-loop runs have taken it to **35.03 on 394 arms**, past the edge, while the
unit's own claim (**Q2**) has no upper edge at all -- its falsifier is *fewer than a tenth*, and it reads MET at
35.03. The band's top edge was therefore pinning a quantity that grows with the corpus, and it is replaced by the
claim's own direction, that the floor swallows more than a quarter of the arms, with Q2's verdict read off the
artifact. Q1 and Q3 are unchanged, and this is the same class of defect `e267`, `e292`, `e309` and `e314` have each
had to shed: a number that tracks the corpus belongs in the reading and not in the gate.

## RE-READ 2026-10-08: the band's bottom edge goes the way of its top

The RE-READ above replaced the band's **top** edge with the claim's own direction. Its **bottom** edge has now gone the
same way: the share of arms whose variance fraction is above one read **0.25**, then **0.2477** on **161 of 650** arms,
three thousandths under the floor -- and `e466`'s six rolls at a hundred updates are what closed it, since a body
trained to a fifth of the budget has arms whose fraction sits lower. So the band is widened to the shape the finding is
about -- a substantial minority of the arms and not half of them, **0.20** to **0.45** -- and the share's value is what
the comment beside it pins. This is the same class of defect as the top edge and as the counts `e267`, `e292`, `e309`
and `e314` have each had to shed: a number that tracks the corpus belongs in the reading and not in the gate. Q1, Q2
and Q3 are unchanged
(`docs/findings/2026-10-08-the-width-ladder-at-another-budget.md`).
