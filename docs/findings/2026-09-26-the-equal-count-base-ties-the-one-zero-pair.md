# The equal-count base: the (1, 0) pair is a tie at three drawings, and the two-side family is the last thing standing

*2026-09-26 16:55. Run: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3 --seed0 0 -q 0.02
--topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed 5` — **one run, one cell, ~7 min, exit 0**, written
as `runs/e245_cs300_kind0_rs5.json` and read by `experiments/e248_equal_count_base.py`
(`runs/e248_equal_count_base.json`).*

## 1. What one run bought

`e247` left this line's spread numbers as **bands**, because every comparison was a max-over-min over however many
drawings a cell happened to have. The fix was to design a base instead of correcting one afterwards, and at
cs 300/support 30 the corpus was a single drawing short of it: `alloy1`, `inalloy1` and `erdos_renyi` already carried
three drawings each, the three kind-0 families two. **One run at `rewire_seed` 5 gives six families three drawings
each — 18 groups, every count equal, no post-hoc subsetting.**

| family | kind | excesses (three drawings) | spread | rank spread |
|---|---|---|---|---|
| `swap0.5` | 0 | 0.01526, 0.02920, 0.04288 | **2.809×** | 7.40× |
| `swap2` | 0 | 0.03015, 0.04089, 0.02897 | 1.412× | 1.57× |
| `signshuffle` | 0 | 0.05161, 0.07184, 0.06939 | 1.392× | 1.19× |
| `alloy1` | 1 | 0.12247, 0.14080, 0.09431 | 1.493× | 2.73× |
| `inalloy1` | 1 | 0.12233, 0.10040, 0.13581 | 1.353× | 2.08× |
| `erdos_renyi` | 2 | 0.15668, 0.15900, 0.15412 | **1.032×** | 1.06× |

## 2. Verdicts

**S1 lands in its registered NULL BAND.** kind 0's median is **1.412×** and kind 1's **1.423×** — **+0.8%**, inside
the 10% band the registration called undecided. The measured claim was that the kind-0 families would be the *tighter*
at equal count; they are the looser, by less than a percent. **At matched counts the two rungs are
indistinguishable at this cell.**

**S2 MET.** `erdos_renyi` at 1.032× is below both one-side families (1.493×, 1.353×).

**S3 MET.** `erdos_renyi` is the tightest of the six families under **every** leave-one-out subset — 1.03×, 1.02×,
1.01× when the first, second and third drawing is dropped respectively — so its tightness is not one drawing's
property.

## 3. The pair has now been read five ways, and four put the one-side rung on top

| reading | kind 0 | kind 1 | which is looser |
|---|---|---|---|
| cs 300/30, **equal count 3** (this run) | 1.412× | 1.423× | kind 1, by **+0.8%** |
| cs 300/30, `e245`'s unequal form (0 at n=2, 1 at n=3) | 1.39× | 1.42× | kind 1, by +2.2% |
| cs 300/30, `e247`'s two-lowest-seed form | 1.34× | 1.26× | **kind 0**, by +6.3% |
| cs 800/80, all drawings | 1.45× | 2.96× | kind 1, by +104.4% |
| cs 800/80, `e247`'s two-lowest-seed form | 1.12× | 1.24× | kind 1, by +10.7% |

**Four of the five readings put the one-side rung on top and one puts it below, and the size ranges over a factor of
100.** So the honest form of `e245`'s sentence ("the reversal replicates in direction at 2 of 2 cells") is: the sign
is *mostly* the one-side rung's and the magnitude is entirely the cell's — 0.8% here, 104% at cs 800/support 80. The
equal-count base removes the sample-size explanation for that difference and leaves the cell as the explanation, which
is what `e247`'s R3 measured from the other side (the cell's support share and circuit size do not order the spread
either, so the cell-specific driver is still unnamed).

**What the third drawing changed**, and it is the unit's sharpest detail: `swap0.5`'s spread goes **1.91× at two
drawings to 2.809× at three**, and its three excesses are **monotone in the rewire seed** (0.01526 < 0.02920 <
0.04288). Drop-one-out moves it over 1.47× to 2.81×, so **the family that is loosest in the equal-count base is also
the one whose spread is least stable there.** Which family occupies the kind-0 rung's top is therefore a drawing's
business, and `swap0.5`'s rank spread at this cell (7.40×) says the same on the other observable.

## 4. What survives, and what the readers say now

**The two-side family's tightness is the only cross-family spread statement this record has that has survived every
audit**: 1.02×–1.06× in six cells, the tightest of five families at both sizes, unaffected by count-matching
(`e247`: 1.06× → 1.02× at its nine-drawing cell), and now the tightest under every leave-one-out subset of a base
designed to be equal-count (S3). Everything else about the spread has narrowed to a band or a tie.

The new drawing enters the censuses of three readers, and **all three keep their verdicts while their numbers move**:

- **`e244`** — K1 MET, kind 0's pooled median 1.42× → **1.43×** and its range widening to [1.072, **2.809**]; K3
  still fired at 6 of 8 cell-pairs, the cs-300 reversal now reading 1.42× against 1.41×.
- **`e246`** — N1/N2 MET with the non-kind-1 span range 1.04×–1.36× → **1.04×–1.94×** (that is `swap0.5`'s rise);
  N3 still fired, its between-family Spearman −0.371 → **−0.486**.
- **`e247`** — all five MET, R5's shared noise **+0.724 → +0.806**, and R4's count-matched (1, 0) pair at cs 300/30
  moving to 1.34× against 1.26×.

## 5. What it cannot do

Three drawings is a range and not a distribution, so this **narrows** `e247`'s bands rather than closing them; the
base is equal-**count** and not equally **drawn** (`swap0.5`'s third drawing is monotone in its seed while `alloy1`'s
three are not ordered at all), and no count can make those the same drawings; the three kind-0 families share this
run's single `rewire_seed`, so their third drawings are not independent; one cell at one size and one `rho`; the
10% null band was fixed before the run, so S1's +0.8% is a tie only by that convention; and it compares spreads,
saying nothing about the levels, which differ by 2× to 5× between the kinds at this cell.
