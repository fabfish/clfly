# The last surviving direction does not survive a designed drawing base — and the enlarged base removes the only falsifier `e240` had

*2026-09-26 13:50, `runs/e241_support{20,160}_rs{2,3}.json` (four geometry-only runs, three cells each, ~25 min) read
together with `e221`'s two existing drawings per support. **G1's falsifier fires, G2 is MET, G3 is MET** — and re-running
`e240`'s census on the enlarged base turns its own **C1 from a falsifier into MET at all six cells**.
Registration: `docs/findings/2026-09-26-registered-the-one-surviving-cross-family-direction.md`.*

## 1. Four drawings per support, at cs 800, `rho` 0.9

| support 160 | rw 0 | rw 1 | rw 2 | rw 3 | pairwise median |
|---|---|---|---|---|---|
| `alloy1` | 28.35 | 2.42 | 2.23 | 2.00 | |
| `inalloy1` | 2.46 | 2.67 | 8.99 | 6.50 | |
| `erdos_renyi` | 32.23 | 33.20 | 41.92 | 39.61 | |
| ratio | **11.54×** | 0.91× | **0.25×** | 0.31× | **0.83×** |

| support 20 | rw 0 | rw 1 | rw 2 | rw 3 | pairwise median |
|---|---|---|---|---|---|
| `alloy1` | 12.74 | 2.60 | 2.27 | 2.03 | |
| `inalloy1` | 2.91 | 3.42 | 6.43 | 6.10 | |
| `erdos_renyi` | 13.06 | 13.13 | 14.63 | 14.13 | |
| ratio | 4.38× | 0.76× | 0.35× | 0.33× | **0.68×** |

## 2. G1's falsifier fired: the direction `e240` named was two drawings'

G1 registered that the support-160 pairwise median over four drawings exceeds 2×, with a falsifier at or below 1.25×.
It is **0.83×** — *below one*, i.e. by this measure the direction has reversed — and the four individual ratios span
**0.25× to 11.54×**, a factor of 46. So the one cross-family direction that had survived `e240`'s accidental re-test
**does not survive a designed one**, and the support-160 "5.81×" was the drawing `e221_rs0`'s.

**G2 is MET** — the support-20 median is 0.68×, far below the 5× bar — and G2's own falsifier (support 20 at or above
10×) was never in play.

**And `e240`'s C1 is now MET at every cell.** Re-running its census on the enlarged base gives medians **0.65×, 1.10×,
0.82×, 0.83×, 0.68×, 0.85×** at the six multi-drawing cells — the support-160 cell moved from 5.81× (two drawings) to
0.83× (four), and with it `e240`'s only falsifier disappeared. **The last cross-family direction in this session was
itself a drawing.**

## 3. G3 is MET, on a designed base for the first time

| support | within-family spread | between-family difference |
|---|---|---|
| 160 | `alloy1` **14.2×** (2.00–28.35), `inalloy1` 3.7× (2.46–8.99) | **1.0×** |
| 20 | `alloy1` **6.3×** (2.03–12.74), `inalloy1` 2.2× (2.91–6.43) | **1.0×** |

The drawings dominate at both supports, so G3's falsifier — *"the first designed case where one drawing is enough"* —
does not exist here. This is the same conclusion `e232`, `e236`, `e239` and `e240` reached, now on a drawing **axis**
(`rewire_seed` 0–3) rather than on the drawings the corpus happened to have.

## 4. What the four drawings do say, and it is not about the comparison

The **levels** are stable across the two supports even where the comparisons are not:

- the out-destroyed family's **median** rank is **4.58** (support 160) and **4.76** (support 20) against the
  in-destroyed family's **2.32** and **2.44** — i.e. *"the out-structure-destroyed null keeps about 1.9× the rank of
  the in-structure-destroyed one"* holds at both supports by the median-of-drawings measure, while the **pairwise
  ratio's median is 0.83× and 0.68×** (below one) and its range is 0.22×–11.54×;
- `erdos_renyi` is by far the tightest family across drawings — **13.06–14.63 (1.12×)** at support 20 and
  **32.23–41.92 (1.30×)** at support 160 — against the one-side families' 6.3× and 14.2×.

So the right form of the claim this cell supports is a **level** statement with its spread attached, not a
between-family contrast: the levels are measurable to ~1.1–1.3× for the two-side null and swing by 6–14× for the
one-side ones, which is exactly why the *contrast* between them is a draw.

## 5. What this cannot do

- **Four drawings** are a sample and `rewire_seed` 0–3 is an axis, not a population; the median of sixteen pairs is a
  summary of that axis.
- **`--geometry-only`**: these cells carry no penalty and are outside `e207`'s join by construction, so nothing here
  speaks to the excess — where `e240`'s C2 also showed the two-side *advantage* to be cell-specific.
- **One size and one `rho`**, so the support dependence found here is one cell configuration's.
- **The pairwise median and the median-of-medians disagree by sign** (0.83× against 0.51×) because the ratio
  distribution is skewed; both are reported and neither is presented as *the* answer.
