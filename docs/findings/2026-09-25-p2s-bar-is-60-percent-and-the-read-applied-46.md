# P2's bar is 60% of the network's own rise; the read applied 45.9%, and the registration's arithmetic gives 76% where its sentence says 80%

**Date:** 2026-09-25
**Found by re-reading the level-0.25 dose while level 0.50 runs.** Three defects, all in the instrument and none in the
data: one arithmetic error inside the registration, and two in `e191` that the registration does not license. All
three are fixed before the midpoint that decides P2 exists — `e193`'s level 0.50 was due ~16:14 when this was
written. **No number here comes from a run launched for it**; every one is read off artifacts that already existed,
and the only file changed to produce it is the reader.

---

## 1. The registration's 80% is not its own arithmetic

`docs/findings/2026-09-25-registered-the-overlap-axis-at-three-intermediate-levels.md` §4 states that the analytic
near component "completes **80%** of its fall by achieved overlap 0.3333". The parenthetical it offers in support of
that number is

> (+0.0258 → +0.0051 of a total fall to −0.0013)

and that parenthetical is **76%**: (0.0258 − 0.0051) / (0.0258 − (−0.0013)) = 0.0207 / 0.0271 = **0.764**.

The artifact agrees with the parenthetical and not with the sentence. `analytic_progress` computes each fraction
from `e7`'s six levels rather than quoting them, and gives:

| level | achieved overlap | analytic near | fraction of its own 0 → 1 fall |
|---|---|---|---|
| 0.0 | 0.0000 | +0.025751 | 0.0% |
| 0.1 | 0.0526 | +0.022033 | 13.7% |
| 0.25 | 0.1429 | +0.014882 | **40.1%** |
| 0.5 | 0.3333 | +0.005050 | **76.4%** |
| 0.75 | 0.6000 | +0.002334 | 86.5% |
| 1.0 | 1.0000 | −0.001327 | 100.0% |

So the registered sentence sits **3.6 points above both its own arithmetic and the artifact**, and a grep of the
corpus finds the string `80%` in exactly one place: that sentence. There is no source for it.

**This does not move the bar**, because the bar is a statement about the *network's* own rise (§2). It matters
because the 80% is the number the same sentence's "so" clause leans on, so a reader checking the bar against the
analytic line would be checking it against the wrong anchor. The registration is left as written and the read now
prints the artifact's value beside it — §6.

## 2. The bar the read applied is not the bar the registration states

The registered sentence, in both places that carry it — the registration finding's §4 and the plan's row for `e193`
— is:

> the network's near rise should be **≥ 60% complete by achieved 0.3333**

"Complete" there is of the network's **own** 0 → 1 rise, and neither carrier says "60% of the analytic line"; the
60% is the 80% softened, and the softening is of the network's own fraction. The reader applied

```python
prog >= 0.6 * analytic
```

instead, i.e. **60% of the analytic line's fraction at the same achieved overlap**. At the midpoint the analytic line
is at 76.4%, so that bar is **45.9%** — **14 points looser** than the one the registration states.

The case that separates them is not hypothetical, and it is the case the tests now pin: a network at **50%**
completion is **NOT met** on the registered bar and would have been **MET** on the applied one. The band where the
two disagree is [45.9%, 60%), which is exactly where a measurement between the project's two plausible outcomes
would land.

Fixed: `P2_BAR = 0.60`, absolute, with the reason the reading was rejected written into the constant's comment. The
analytic line's progress is still printed, named as the ratio it is:

```
P2: 12% of its own 0->1 rise (bar 60%)   [the analytic line is 40% there,
                                          i.e. this line is at 31% of the analytic's progress]
```

## 3. P2 was given a verdict at every level

Five lines above the P2 code, P1's own comment records that its first version "printed 'NOT met' at every level,
which is a claim the registration does not make (and fired at achieved 0.1429, where P1 says nothing)". **P2, in the
same function, did exactly that to itself.** The live read printed, for the one level that exists:

- `ewc-block`: "P2: 1% … **NOT met**"
- `ewc-block-rand`: "P2: 2% … **NOT met**"
- `naive`: "P2: 12% … **NOT met**"

All three are verdicts at achieved 0.1429 on a sentence written for achieved 0.3333. Fixed: the verdict is withheld
away from the midpoint and the row says where the bar is written, which is what P1's row already did — and the
sibling read `e188` already did for its own bar, with the same comment. So **`e191`'s P2 was the only bar in either
dose read left ungated**: the earlier fix was applied to P1 in this file and to the bar in the other, and missed one
of the three.

## 4. For the block arms the denominator was not a 0 → 1 rise at all

Per-arm admission sends the block arms to `e153` as their baseline. `e153` is at overlap **1.0** — so the anchor the
reader divides by, `e144`, is *also* at overlap 1.0, and their difference is not a rise:

```
"full_rise" = paired(e144.near, e153.near) = +0.14538
```

Two runs at the **same input overlap**, whose configs differ in exactly two fields:

| field | `e144` | `e153` |
|---|---|---|
| `input_overlap` | 1.0 | 1.0 |
| `lam` | 0.003 | 1.0 |
| `methods` | `naive,ewc,ewc-block,ewc-block-rand` | the same **+ `replay`** |

The first version divided the level's rise by that and printed the ratio as "1% of the line's own 0->1 rise", with a
P2 verdict attached. **Nothing about the x-axis was measured in that number.** Fixed: the pairing is taken as a rise
only when the arm's own admitted baseline sits at overlap 0.0; otherwise it is recorded as `anchor_minus_baseline`
with the reason, and the row prints "P2: withheld".

**And the number it was hiding is worth having.** Read as what it is — a λ effect at the overlap-1.0 end, 40 seeds,
same circuit and read-out — it is a large and well-resolved measurement of the penalty:

| `ewc-block`, adjacent-pair near interference, overlap 1.0, 40 seeds | value |
|---|---|
| λ = 3e-3 (`e144`) | **+0.14700** |
| λ = 1.0 (`e153`) | **+0.00162** |
| difference | **+0.14538 ± 0.01183 = 12.3σ** |

(`e159` is `e153`'s own rerun: the two agree on `config` except for `json_out`, on all five arms' 40 replicates, on
`circuit`, `tasks`, `partition_draw`, `readout`, `evaluation_noise`, `matched_pair` and `n_params`, differing only in
`environment` and `timing_s` — so the λ = 1.0 column rests on one measurement drawn twice.)

A 333× penalty removes **98.9%** of the block arm's adjacent-pair interference at full overlap. The other end of the
measured range says the same thing from the other side:

| `ewc-block` near interference | λ = 3e-3 | λ = 1.0 |
|---|---|---|
| overlap 0.00 (`e140`) | **+0.09564** | *not measured at λ = 1.0* |
| overlap 0.25 (`e193` level 0.25) | *not measured at λ = 3e-3* | **+0.00264** |
| overlap 1.00 (`e144` / `e153`) | **+0.14700** | **+0.00162** |

At λ = 3e-3 the term **rises** with the overlap (+0.0956 → +0.1470, the direction `naive` shows too, +0.1330 →
+0.2564). At λ = 1.0 it reads ~0.002 at both points where it exists, against a 40-seed sem of ~0.004 on a change
in it.

**This reframes the dissociation this project has been reporting.** The λ = 1.0 rows say the block arm's forgetting
moves **4.1σ** with the overlap while its own interference term moves **0.3σ**
(`docs/findings/2026-09-25-a-333x-penalty-step-dressed-as-an-overlap-effect.md`), and that has been read as a channel
that reads one thing while the effect lives in another. The `e140`/`e144` values say the **same instrument on the
same arm** reads 0.096–0.147 at the same overlaps when the penalty is 333× weaker — so at λ = 1.0 the term is not
*insensitive*, it is **saturated**. The 0.3σ is a ceiling on the channel, not evidence that the forgetting is
mechanically independent of the interference.

## 5. What the midpoint can still decide, and the one measured point

The registered bar is 60% of the `naive` network's own 0 → 1 rise at achieved 0.3333. The single measured point on
that axis is the level-0.25 artifact:

- network at achieved 0.1429: **+0.01516 ± 0.01233 = 1.23σ** above the disjoint baseline (`e116`, +0.13302 →
  +0.14818), i.e. **12.3%** of its own 0 → 1 rise (+0.12337)
- the analytic line at the same achieved overlap: **40.1%** — so the network is at **31%** of the analytic's
  progress

**Two extrapolations, named as extrapolations and not as bars** (one point, and neither ratio need hold):

- holding the **slope in achieved overlap**, 12.29 points over 0.1429 = **86.0 points per unit**, carries the
  network to 12.3 + 86.0 × 0.1904 = **28.7%** at the midpoint;
- holding the **ratio to the analytic line**, 0.306 × 0.7645 = **23.4%**.

Both land below both readings' bars, so P2 fails if the network's rise keeps the shape it has shown. To clear the
registered 60% from 12.3% at 0.1429, the interval 0.1429 → 0.3333 must carry 47.7 points over 0.1904 of overlap —
**250.6 points per unit against 86.0**, i.e. **2.9× the slope**. The falsifier and the registered null are unchanged
and are read by the same command.

**One resolution note on the other instrument, since both are read at the same midpoint.** The forgetting bar the
same registration places on `naive` — `DOSE_HALF_DONE = 0.0159`, "half the 0 → 1 rise" of +0.0318 — sits **1.31σ**
from zero against the level-0.25 read's own sem of ±0.0121, which is rule 41's defect ("a bar at the noise scale does
not test a hypothesis, it tests the seeds") arriving by arithmetic rather than by choice: the bar is half the 0 → 1
rise and the 0 → 1 rise is 2.99σ. Whether the midpoint's sem is the same as the 0.1429 point's is **not measured**
and is not assumed here; it is recorded because a verdict at the midpoint consults that bar in the same breath as
P2's.

## 6. What this does not license

- **P2's verdict at any level other than achieved 0.3333**, and none at all from the block arms — their row prints
  numbers where the registration's shape claim would need a rise that does not exist for them.
- **That the two lines share a mechanism.** That is what P2 tests; §1's 76% is the analytic line's own timing and is
  not evidence of a shared one.
- **Attributing all of +0.1454 to the penalty.** `e144` and `e153` also differ in the methods list, so the
  attribution leans on "arms are independent of the methods list" (established three times, `e176`'s P0 the last)
  rather than on a run built to isolate λ at this overlap. `ewc-block` is not the `replay` arm, so the extra arm in
  `e153`'s list cannot reach it — but that is an argument, not a control.
- **The 2.9× slope, or either extrapolated value**, as anything but an extrapolation.
- **Correcting the registration's 80% in place.** It is a pre-registration: the record of what was claimed before the
  run. The read prints the artifact's 76.4% beside it, and the discrepancy is §1 of this finding, rather than the
  number being quietly replaced by the one that turns out to be right.

## 7. The instrument, after the fix

`experiments/e191_interference_across_lines.py`: `P2_BAR = 0.60`;
`P2_REGISTERED_ANALYTIC_AT_MIDPOINT = 0.80`; the rise denominator taken only when the arm's own admitted baseline is
at overlap 0.0, else `anchor_minus_baseline`; P2's verdict gated to achieved 0.3333; the analytic line's progress
printed as a ratio with the registration's quoted value beside the artifact's.

`tests/test_e191_interference_across_lines.py`: two tests added —
`test_a_block_arms_anchor_pairing_is_not_taken_as_a_zero_to_one_rise` (the denominator refuses, the pairing is still
recorded) and `test_the_midpoint_verdict_uses_the_registered_bar_and_not_sixty_percent_of_the_analytic` (the 50% case
that separates the two thresholds, the ratio printed as context, and no verdict away from the midpoint). 13 tests in
the file, all passing.
