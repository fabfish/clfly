# Registered: a fourth draw set, aimed at the claim C2 actually rests on

**Date:** 2026-09-25. **Registered before its run.** Artifact to be written:
`runs/e206_ladder_d300_12seeds_seed0-300.json`.

---

## 1. Why a fourth, and why now

The third draw set did two things at once (`e204`, read by `e203` at 23:05):

- it **fired Q1's falsifier** — the peak's lead over the best `rand:` rung *of any size* decayed
  0.76623 → 0.36409 → **0.02401** across draw sets 0, 100 and 200, so *"the best rung is a biological pooling
  depth"* is not supported at n = 3;
- and it left the one claim C2 is registered on **0.014 above its own bar**: `bio:pool4` against its
  group-size-matched control `rand:pool4` reads **+1.06906 → +0.72123 → +0.51409** against a bar of 0.5.

So the situation is the mirror image of the one that motivated the third draw set. Then, two measurements made a
difference and not a span; now **the statement that died is the height-based one and the statement that lives is
the matched one, and the matched one is at its bar.** A fourth draw set is the cheapest way to learn whether the
matched advantage is a property of the ladder or a three-draw accident — and the unmatched decay, which has three
points, gets a fourth.

## 2. The design

The same command as `e202` and `e204`, `--seed0 300`, everything else from `e181`'s own config (rule 44):

```
experiments/e3_basis_selection.py --ladder --circuit-size 300 --support 30 --seeds 12 --q 0.02 \
  --align-top 16 --no-realized --topologies real --control-draws 1 --seed0 300 \
  --json-out runs/e206_ladder_d300_12seeds_seed0-300.json
```

`--seed0 300` draws task sets 300-311, disjoint from the three sets already measured (0-11, 100-111, 200-211), so
this is a fourth draw set and not a re-roll of one.

**Cost (rule 49), from the three artifacts' own `timing` blocks**: 2653.2 s, 1758.9 s and **1829.2 s** — i.e.
**29–44 min**, which is the range the last registration quoted from two of them and this one can now quote from
three. One command on an idle machine.

**The read**: `e203 --drawn` with all three existing artifacts, plus the three claims below added to its
`BAND_CLAIMS`. Its per-draw-set table now prints **three** gaps (the peak against the best `rand:` rung of any
size, the peak against its own size-matched control, and `bio:pool4` - `rand:pool4` at the named rung), so Q4's
quantity is readable across all four draws before this artifact lands.

## 3. The claims

**Q4 — the matched advantage holds at the bar, four for four.** `bio:pool4`'s excess exceeds `rand:pool4`'s by
**at least 0.5** at draw set 300 (0.5 is the bar P3 registered; measured so far +1.06906, +0.72123, +0.51409).
**Falsifier**: at or below **0.2**, i.e. the matched advantage has collapsed and the third draw set's 0.014
margin was the edge of a fall rather than a reading. **Null worth keeping**: 0.2–0.5, i.e. the advantage survives
and the bar is crossed downward — which would make the *claim* true only in its qualitative form.

**Q5 — the unmatched statement does not come back.** The peak's lead over the best `rand:` rung of any size is
**below 0.2** at draw set 300 (measured 0.76623 → 0.36409 → 0.02401). **Falsifier**: at or above **0.5**, which
would say the third draw set's near-tie was the fluctuation and the decay was the trend — the claim would then be
alive in the opposite direction. **Null worth keeping**: 0.2–0.5.

**Q6 — the biological rungs still hold the top of the table.** At least **5 of the top 8** rungs are biological
at draw set 300 (measured 6, 6, 5). **Falsifier**: **3 or fewer**, which would make the top of the table a
random-rung regime and would put the third draw set's 5 on a trajectory rather than at a level. **Null worth
keeping**: exactly 4.

These six outcomes are named so that every one of them is reportable: the matched claim failing (Q4's falsifier)
would be the most important result this ladder line has produced, because it is the claim the paper's C2 rests
on, and a registered falsifier that could not fire is not a test.

## 4. What this cannot do

- **A distribution.** Four draw sets are 3 df; the spans and the ordered values are descriptive, and no standard
  deviation is quoted from them.
- **Separate the task draw from the control draw and the rewiring.** All three come from `seed0`, which is why
  the unit under study is the *draw set* and not any one draw.
- **Rehabilitate the height-based statement.** Q5 can only keep it dead or revive it; a fourth point does not
  make three points into a curve, and the decline from 0.766 to 0.024 is not fitted by anything here.
- **Speak for the network ladder**, a different instrument at 1.2–3.4 h per rung.
- **Say what the matched advantage IS.** A matched contrast of +0.5 at one rung and +0.02 at the peak is a
  statement about the control's construction as much as about the biology: `rand:pool*` draws group sizes from
  the same vocabulary, and nothing here varies *how* the control is matched.
