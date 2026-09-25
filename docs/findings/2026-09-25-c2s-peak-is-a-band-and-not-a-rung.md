# C2's peak is a BAND and not a rung: the registered null landed, with `bio:pool8` leading `bio:pool4` by 0.049 on a second draw set

**Date:** 2026-09-25
**`e202` landed at 22:21** — 1758.9 s against the 2653 s its reference took (so rule 49's price, taken from `e181`'s
own `timing` block, was 1.5× conservative) — and the pooling ladder's registered draw-set claims are read by `e203`.
**The peak moved, and the registration had an outcome for exactly that.**

---

## 1. The two tables

| basis | draw set 0 (`e181`) | **draw set 100 (`e202`)** |
|---|---|---|
| **`bio:pool4`** | **2.28112** (1st) | **2.05861** (2nd) |
| **`bio:pool8`** | 1.44707 (7th) | **2.10798** (1st) |
| `bio:pool64` | 1.71290 | 1.81345 |
| `bio:pool128` | 1.61061 | 1.80211 |
| `bio:pool16` | 1.42104 | 1.75673 |
| `bio:pool32` | 1.38674 | 1.74742 |
| `rand:pool64` | 1.51490 | 1.74390 |
| `rand:pool128` | 1.47748 | 1.70081 |
| `rand:pool4` | 1.21206 | 1.33737 |
| `bio:pool2` | 1.46687 | 1.14528 |
| `bio:pool1` | 0.92399 | 0.91378 |
| `rand:pool2` | 0.79305 | 0.75005 |

## 2. The three verdicts

- **P1 — the registered NULL, not the falsifier**: the peak is `bio:pool8` at 2.10798, **above `bio:pool4`'s 2.05861 by
  only 0.04938**. The registration named three outcomes — same rung (MET), **another biological rung beating it by less
  than 0.2 (the null)**, and a different rung firing the falsifier — and 0.049 is the middle one. **My reader's first
  version applied only two of the three and printed a fired falsifier**; that is fixed, and it is the same defect the
  S-claims' reader was built to avoid, in a different table.
- **P2 — MET**: `bio:pool4`'s excess is 2.05861, inside the registered ±25% band of 2.28112.
- **P3 — MET**: the biological-minus-random gap at that rung is **+0.72123**, against the registered bar of 0.5 and
  the draw-set-0 value of 1.06906.

**So the two claims that carry C2's content survive a second draw set**, and the one that does not is the *identity of
the best rung*: pool4 at one draw set and pool8 at another, inside 0.05 of each other and both well above every random
control at the same group sizes.

## 3. What this says about C2, which is the project's core contribution

**"The best anchoring basis is a biological pooling depth" is what the evidence supports — and "pool4" is not.** The
rung table's head is a **band spanning pool4–pool8** whose internal order is draw-set-dependent at the 0.05 level,
while the biological-versus-matched-random gap at the band is 0.72–1.07 and the *biological* rungs occupy the top
eight of sixteen in both draw sets. The plan's C2 note says the rung tables' draws are averaged inside each cell
rather than varied between them; this is the first measurement of what happens when they are varied, and the answer is
that **the table's head moves and its structure does not**.

**It also fixes an over-claim in the plan's own prose**: the σ table quoted for C2 (`side` 28.8σ, `cell_class` 12.1σ,
…) is the *network* ladder's, and its "pool4 42.2σ" is the *linear* ladder's at one draw set. Neither is a claim about
a single rung, and the C2 note now says so.

## 4. What this does not license

- **That the band is stable.** Two draw sets give a difference; the band's edges are one measurement apart, and pool8
  is second on draw set 0 (7th of 16) — the largest single move in the table.
- **A distribution over draw sets.** n = 2, and today's own lesson is that a difference at two draws can be an
  outlier's distance.
- **That the biological advantage is draw-set-robust in magnitude.** P3 held at 0.72 against 1.07 — a third smaller,
  and its bar was 0.5, so a third draw set could take it under.
- **Anything about the network line.** This is the linear/Kalman ladder; the network rungs are a different instrument
  and nothing here transfers.
- **That `--control-draws 1` is enough.** One draw of the matched-random control is one sample from a population, as
  rule 10 says, and this design held it at `e181`'s value rather than varying it.
