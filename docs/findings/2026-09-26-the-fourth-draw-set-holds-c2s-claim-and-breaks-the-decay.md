# The fourth draw set holds the claim C2 rests on, and breaks the decay I read from three points

*2026-09-26 00:04, `runs/e206_ladder_d300_12seeds_seed0-300.json` (launched 23:36, 1773 s ≈ 30 min from its own
`timing` block, inside the registered 29–44 min). Read by `e203 --drawn` on all three earlier draw sets, exit 0. The
registration is `docs/findings/2026-09-25-registered-a-fourth-draw-set-for-the-claim-c2-rests-on.md`.*

## 1. The verdicts

| | claim | verdict at draw set 300 |
|---|---|---|
| **Q4** | `bio:pool4` − `rand:pool4` is **at least 0.5** | **MET** — **+1.15902**, the largest of the four |
| **Q5** | the peak's lead over the best `rand:` rung of any size is **below 0.2** | **null band** — +0.29046 |
| **Q6** | at least **5 of the top 8** rungs are biological | **MET** — 6 of 8 |

**Q4 is the one that mattered.** The third draw set left the matched contrast 0.014 above its bar and I registered
this run to find out whether that was the edge of a fall. It was not: the band gap goes **+1.06906 → +0.72123 →
+0.51409 → +1.15902**, so **C2's registered claim holds four for four**, and the collapse its falsifier named is not
happening. The four values span **0.64493** — a factor of 2.25 between the smallest and the largest — so the claim is
*"the matched advantage holds at every draw set measured"* and **not** *"the matched advantage has a stable size"*.

## 2. And the decay I read from three points does not exist

My reading of the third draw set said the peak's lead over the best `rand:` rung *"decays monotonically"*
(0.76623 → 0.36409 → 0.02401). The fourth point is **+0.29046**, so the sequence is 0.766, 0.364, 0.024, **0.290** —
it fell to near zero and came back. **The monotone decay was three points of a noisy quantity, and the fourth
point is what says so**, which is exactly the failure this project has now recorded three times in one evening
(a two-draw conclusion, a three-draw conclusion, and this). What survives is weaker and true:

- the height-based statement's **falsifier fired at 1 of 4 draws** (draw set 200, where a `rand:` rung came within
  0.024 of the peak), and at the other three the peak led by 0.29–0.77;
- the **peak's identity is unstable**: `bio:pool4`, `bio:pool8`, `bio:pool4`, **`bio:pool32`** — four draws, three
  distinct rungs, so P1's "the same rung peaks" holds at 2 of 4;
- the **match** form is stable where both are measured (Q4 4/4, Q6 4/4), which is the split between the two
  statements stated more sharply than before.

## 3. What the reader had to be fixed for, again

Running four tables exposed that `judge_band` judged Q1 and Q2 off **the last table given** — so with `e206` supplied
they would have been computed at draw set 300, which is **not their subject**: Q1's registered sentence names draw
set 200 and Q3's names three draw sets. The reader now addresses each claim to a fixed position (Q1/Q2 at the third
table, Q3 the span over the first three, Q4–Q6 at the fourth), and a test builds a case where the third table fires
Q1 while the fourth does not. This is the same defect as the one repaired one pass earlier — *the reader printed the
neighbouring quantity* — one level over: **the reader judged the neighbouring draw set**, and the fix is the same
shape (address the claim to its own subject, refuse when it is absent).

## 4. Q3's span is now weaker than it reads, and the readers should say so

Q3's bar is *"the span of the peak's excess across the three draw sets is below 0.5"* and it reads **0.43043** at
four draws — **unchanged**, because the fourth peak (1.99555) falls between the existing minimum (1.85069) and
maximum (2.28112). A span is a min-to-max statistic, so **a new draw set can only move it by setting a new extreme**,
and three of four additions have not. The claim is MET and it is *less* informative at four draws than at three: it
no longer says the fourth draw was inside the band, only that it did not extend it. Registered as a note rather than a
correction: the bar and the sentence are the third draw set's and were not restated for a fourth.

## 5. The band's own claims, four draws in, in one line each

- **the matched advantage (C2's form)**: holds at all four draws, +0.51 to +1.16, span 0.64493.
- **the height-based form**: fires its falsifier at one draw of four; the lead is 0.29–0.77 at the other three.
- **the peak's identity**: `pool4`/`pool8`/`pool4`/`pool32`; the registered "same rung" claim holds 2 of 4.
- **the head's level**: span 0.43043 across the peaks' values, and the span has not moved since the third draw set.
- **the membership**: 6, 6, 5, 6 of the top eight biological — at its registered bar at every draw set.

## 6. What this does not do

It does not make the identity claim stable, does not give the matched contrast a distribution (four draws are 3 df, and
the span is the honest statistic), does not separate the task draw from the control draw and the rewiring (all three
come from `seed0`), and does not touch the network line's claims, which are a different instrument. The registration
named one thing it could not buy, and this confirms it: a fourth point turned a three-point "trend" into a scatter,
which is a *reduction* in what the height-based statement can claim even though its falsifier did not fire here.
