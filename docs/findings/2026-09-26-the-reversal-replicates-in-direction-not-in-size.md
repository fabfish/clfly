# The reversal replicates in direction and not in size — which puts it in kind 1, not kind 0

*2026-09-26 15:03. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3 --seed0 0 -q 0.02
--topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed {3,4}` — two runs, one cell each, both exit 0,
~7 min per run, written as `runs/e245_cs300_kind0_rs3.json` and `_rs4.json`. Read by `e244` re-run unchanged
(`runs/e244_drawing_spread_by_kind.json`).*

## 1. What the two runs bought

The no-destruction rung now exists at **two** cells instead of one. At cs 300/support 30, beside the three drawings
each of `alloy1`, `inalloy1` and `erdos_renyi` that were already there:

| kind | family | drawings | excess spread | mean excess | rank spread |
|---|---|---|---|---|---|
| 0 | `swap0.5` | 2 | 1.91× | 0.02223 | 7.41× |
| 0 | `swap2` | 2 | 1.36× | 0.03552 | 1.34× |
| 0 | `signshuffle` | 2 | 1.39× | 0.06173 | 1.01× |
| 1 | `alloy1` | 3 | 1.49× | 0.11919 | 2.73× |
| 1 | `inalloy1` | 3 | 1.35× | 0.11952 | 2.08× |
| 2 | `erdos_renyi` | 3 | 1.03× | 0.15660 | 1.06× |

## 2. The registered claims

- **M1 (discriminating)** — kind 0's median spread is **below** kind 1's at this cell, i.e. K1's ordering holds inside
  the cell and the convention cell's reversal was an accident. **Falsifier**: kind 0 at or above kind 1, a second
  reversal. **Null**: the two medians within **10%**.
- **M2** — kind 2's median stays below kind 1's (6 of 6 cells so far). **Falsifier**: kind 2 at or above kind 1.
- **M3 (reported)** — the levels, so the confound is stated with numbers.
- **M4 (reported)** — the first kind-0 drawings at any size other than cs 800.

## 3. Verdicts

**M1 lands in its registered NULL BAND.** kind 0's median is **1.39×** and kind 1's **1.42×** — a difference of
**+2.2%**, inside the 10% band the registration called undecided. The falsifier did not fire and the claim was not
met: at cs 300/support 30 **neither the pooled ordering nor the reversal is detectable**. That is the outcome the
null band existed to name, and it is the first claim this session has landed in one.

**M2 MET.** kind 2 reads 1.03× against kind 1's 1.42×, and the two-side family is below the one-side one in **all six**
cells now (per-cell medians 1.02× to 1.06×).

**M3 (reported).** The confound `e244` named is intact and now measured at a second size: kind 0's families sit at
0.02223, 0.03552 and 0.06173 against kind 1's 0.11919 and 0.11952 and kind 2's 0.15660, so the no-destruction rung
is 2× to 5× below the one-side one and 2.5× to 7× below the two-side one. **The spread comparison is still collinear
with level** and nothing here separates them.

**M4 (reported).** The floor's level at cs 300 is `swap0.5` 0.02223, `swap2` 0.03552, `signshuffle` 0.06173, against
cs 800's 0.02173, 0.01527 and 0.02850. So the floor is **0.02 to 0.06 at both sizes** — it does not rise with the
shrinking circuit the way the one-side level does (0.047 to 0.122, `e217`) — and `signshuffle` is the highest of the
three at **both** sizes while the `swap0.5`/`swap2` order **flips between them** (0.0222 against 0.0355 at cs 300,
0.0217 against 0.0153 at cs 800). The floor is not a level; it is three families that do not keep their order.

## 4. The structural reading: the direction replicates, the size does not

`K3` now fires its falsifier at **both** pairs that compare kind 1 with kind 0 — and the two margins are not
comparable:

| cell | kind 0 median | kind 1 median | kind 1 ÷ kind 0 |
|---|---|---|---|
| cs 300/support 30 | 1.39× (3 families) | 1.42× (2 families) | **+2.2%** |
| cs 800/support 80 | 1.45× (3 families) | 2.96× (4 families) | **+104.4%** |

**The sign is the same at 2 of 2 cells; the magnitude differs by a factor of 47.** That locates the effect: the
per-cell medians show which rung moved.

- **kind 0's spread is stable across the size change**: 1.39× and 1.45×, a span of **1.04×**. Its three families are
  also individually close (1.36× to 1.91× at cs 300, 1.07× to 1.84× at cs 800).
- **kind 2's is the most stable of all**: per-cell medians 1.02× to 1.06×, a span of 1.04×, in six cells.
- **kind 1's swings by 2.74×**: 1.42×, 1.08×, 1.09×, 1.89×, 1.32×, 2.96× across its six cells.

So `e244`'s pooled ordering — kind 0 loosest, kind 1 between, kind 2 tightest — survives on the **composition** of
the corpus and not on any cell: kind 1 has four cells where it is tighter than kind 0's 1.39×–1.45× (1.08×, 1.09×,
1.32×, 1.42×) and one where it is far looser (2.96×), while kind 0 is only ever measured at cells where it reads
1.39× or 1.45×. **At every cell that can compare them, the more destructive one-side rung is the looser one** — by
2% and by 104%. The convention cell's reversal was therefore not an artifact of its kind-0 sample: it is the sign
the second cell agrees with, and its 104% is the part that does not replicate.

The **rank** axis agrees with the excess one at cs 300 (kind 0 1.34× below kind 1 2.40×) where it disagreed at
cs 800 (kind 0 5.87× above kind 1 5.20×), so the two observables agree about the ordering exactly at the cell where
their difference is largest.

## 5. What the pooled verdicts read now

    K1: kind 0 n=6 median 1.42 [1.072, 1.913]   kind 1 n=14 median 1.292 [1.062, 3.344]   kind 2 n=6 median 1.029 [1.021, 1.06]
    K2: kind 0 n=6 median 0.3322                kind 1 n=14 median 0.2517                kind 2 n=6 median 0.02898
    K3: 6 of 8 cell-pairs support the ordering; reversed: cs 300/sup 30 (kind 1 1.42x >= kind 0 1.39x)
                                                     and cs 800/sup 80 (kind 1 2.96x >= kind 0 1.45x)

**K1 and K2 stay MET and are now better supported than before** — kind 0's rung rests on **6 groups at 2 cells**
(six families, three at each cell) instead of 3 groups at 1 cell, and its range widened to [1.072, 1.913] while
staying disjoint from kind 2's [1.021, 1.06]. **K3 stays falsified, at 2 of 2 (1,0) pairs instead of 1 of 1.** The
two verdicts are not in tension: K1 is a statement about the corpus's composition and K3 says that composition is
what carries it.

## 6. What it cannot do

Two drawings per family is a range and not a distribution, and the three kind-0 families at cs 300 share those two
drawings, so their spreads are not independent of each other — the 1.36×/1.39×/1.91× cluster is one pair of drawings
seen three ways; **the M1 null band of 10% was chosen before the run and is arbitrary**, so +2.2% would have read
"MET" under a 2% band and a reversal under a 5% one, and the honest statement is the one the null expresses, that
this cell cannot resolve the two rungs; the level confound survives the design; one size, one support, one `rho`
(`config.rho: None` in every artifact of this run); and nothing here is a statement about the *levels* the ladder is
made of — only about how much a level moves between drawings.
