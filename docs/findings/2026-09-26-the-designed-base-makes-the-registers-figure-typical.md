# The designed base makes the register's figure typical, and doubles the dispersion of its own interval

*2026-09-26 14:43. Runs: `e2_topology_gap` at cs 800, support 80, `rho` the builder's default (the artifacts record
`config.rho: None`), `--seeds 3 --seed0 0 -q 0.02 --topologies alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed
{6,7,8}` — three runs, three cells each, one artifact per run (`e243_convention_rs6.json`, `_rs7.json`, `_rs8.json`),
13:53 to 14:31, ~13 min per run, all exit 0.*

## 1. What landed

| drawing | `alloy1` (rank) | `inalloy1` (rank) | `erdos_renyi` (rank) |
|---|---|---|---|
| rs 6 | 0.09037 (8.83) | 0.05090 (4.92) | 0.14055 (28.52) |
| rs 7 | 0.04010 (2.55) | 0.09921 (18.82) | 0.14307 (30.38) |
| rs 8 | 0.07077 (3.64) | 0.10863 (16.19) | 0.14624 (32.03) |

The three drawings behave differently by family, and that is the whole mechanism of what follows:

- **`erdos_renyi` sits inside its own band.** 0.14055 to 0.14624 against the six accidental drawings' 0.14134 to
  0.14897, so **the two-side family's spread over nine drawings is 1.06×** (it was 1.05× over six) — still the
  tightest thing in this record by an order of magnitude.
- **`alloy1` sits inside its accidental range** (0.0401 to 0.0904 inside 0.03011 to 0.10067), so its own spread does
  not move at all: **3.34× over eight drawings, exactly the 3.34× it was over five**.
- **`inalloy1` does not.** The three newest are the two **highest at this cell ever drawn** (0.10863, 0.09921) plus
  one that lands just above the accidental three (0.05090 against 0.04212, 0.04593, 0.05208), so **`inalloy1`'s
  spread more than doubles: 1.24× over three drawings to 2.58× over six.**

## 2. The registered claims

- **H1** — the ER-over-`alloy1` median stays within **1.25×** of the accidental base's **3.45×**. Falsifier: a move
  beyond **1.5×**; null: 1.25× to 1.5×.
- **H2** — the register's **2.76×** remains **below the 25th percentile**. Falsifier: it lands inside the central
  half, which would make the quoted number typical after all; null: exactly at q25.
- **H3** — the enlarged IQR over the median stays above **20%** (against the spellings' 9% gap). Falsifier: below
  **15%**, which would make the two-spelling presentation defensible.

## 3. Verdicts

**H1 MET.** The median moves 3.45× to **3.285×**, a factor of **1.05** — well inside the bound. The other spelling
moves a little more and the same way: 3.10× to **2.791×**, a factor of 1.11. Adding three drawings to the cell did
not move where the cell's centre is.

**H2 FALSIFIER FIRED.** On the enlarged base the register's **2.76× is at the 37.5th percentile** — inside the
central half [1.986, 3.715]. The registered falsifier was exactly this case: *"it lands inside the central half, which
would make the quoted number typical after all."* On the accidental base the same figure was at the 20.0th
percentile. **The quoted number stops being a low draw.**

**H3 MET.** The interquartile range over the median is **53%** and **60%** for the two spellings (the module's
figures; 50.8% and 59.7% on the index-median), far above the 20% bar and far above the 9% gap between the two quoted
spellings — against 26% and 18% on the accidental base. The quantity remains one whose dispersion dwarfs the
presentation's distinction.

## 4. The distribution, before and after

| spelling | base | drawings | pairs | min | q25 | median | q75 | max | IQR/median | where the register's figure falls |
|---|---|---|---|---|---|---|---|---|---|---|
| ER ÷ `alloy1` | accidental | 5 | 30 | 1.404 | 3.016 | 3.45 | 3.896 | 4.947 | 26% | 2.76× at the **20.0th** percentile |
| ER ÷ `alloy1` | enlarged | 8 | 72 | 1.396 | **1.986** | 3.285 | 3.715 | 4.947 | **53%** | 2.76× at the **37.5th** percentile |
| ER ÷ `inalloy1` | accidental | 3 | 18 | 2.714 | 2.820 | 3.10 | 3.368 | 3.537 | 18% | 3.02× at the 33.3rd percentile |
| ER ÷ `inalloy1` | enlarged | 6 | 54 | 1.294 | **1.434** | 2.791 | 3.099 | 3.537 | **60%** | 3.02× at the 66.7th percentile |

**The quartile moved by a factor of 1.52 while the median moved by 1.05.** That is the finding in one line: what the
accidental five-drawing base got wrong about this cell was not its centre but its **shape**, and the shape is what
the register's percentile reading was read off. The 42 pairs the designed drawings add fill the low half of the ratio
distribution, which the accidental grid of 5 × 6 ordered pairs — correlated by construction, since each drawing
appears in five or six of them — had left thin.

**And by the mean-spelling, which is the form the register quotes, the enlarged base reads 2.51×** (mean
`erdos_renyi` 0.143716 over mean `alloy1` 0.057259): the nine per-drawing mean-spellings run **2.4547 to 2.6016**, so
**the quoted 2.76× is above every one of them.**

## 5. What this withdraws

`e242`'s percentile reading is withdrawn as a statement about the cell. "2.76× sits at the 20th percentile of its own
30 drawing pairs — a low draw of its own drawings" was true of the accidental five, and on a designed base of the
same cell the same figure is at the 37.5th. `e242`'s own **R1** flips with it, from its null band to **MET** ("both
quoted spellings sit in the central half"), and **R2** stays MET with wider quartiles. The interval the record should
carry at this cell is now **3.285× [1.986, 3.715]** for the `alloy1` spelling and **2.791× [1.434, 3.099]** for the
`inalloy1` one — a **low** quartile 1.52× further down and a median 1.05× lower than `e242` reported.

Nothing here says the register's 2.76× is wrong. It says that at this cell the figure is **not distinguishable from
the cell's typical value**, and that the previous "low draw" reading was the accidental base's own property —
the same shape of retraction this session has now made three times (the rank contrast, the size effect, and the
cross-family advantage).

## 6. Four readers re-read on the enlarged census

The three artifacts enter every drawing census in the corpus, so four readers committed earlier were re-run:

- **`e242`** (the register's interval): **R1 flips from its null band to MET** and R2 stays MET — §4 and §5 above.
- **`e230`** (the rank scatter audit): cs 800's `inalloy1` stays RESOLVABLE, but its own rank scatter **widens from
  4.14× to 8.02×** against a contrast that stays 45.14×, so **the margin narrows from 10.8× to 5.6×**. This is the
  first time one of this record's survivorship checks has been *weakened* by new drawings rather than withdrawn; it
  survives, at half the margin, and `e230`'s `alloy1` side is unaffected (19 drawings still spanning 16.44×).
- **`e240`** (cross-family drawings): C1 still MET (six cells, median rank ratios 0.53× to 1.10×), C2 still
  FALSIFIER FIRED — and now *more* clearly, since the convention cell's median excess ratio reads **3.29×** where it
  read 3.45×, against 1.12× to 2.22× at the other five cells — and C3 still MET (15 of 18 cells with the
  within-family spread the larger).
- **`e244`** (the spread by construction kind, committed minutes before these artifacts landed): K1 stays MET with
  kind 1's pooled median moving 1.234× to **1.292×**; K2 stays MET, 0.2102 to **0.2517**; and K3 stays FALSIFIER
  FIRED at 6 of 7 cell-pairs with the reversal **widening from 2.29× to 2.96×**, because the family whose spread
  moved is exactly `inalloy1`. The designed base **confirms** `e244`'s reversal on three new drawings rather than
  dissolving it on a pooling argument.

## 7. What it cannot do

The enlarged base is **mixed** — three designed drawings on top of five or six accidental ones — so the shape change
cannot be attributed wholly to design; the pairs remain a grid of ordered ratios rather than independent draws, which
is why the quartiles summarise those drawings and not a population; three drawings is a small addition, and the
quartile moved because they are precisely the drawings that fill the ratio distribution's low half; one cell, one
size, one `rho`; and the mean-spelling's 2.51× is a ratio of means, so it is a different estimator from the 2.76× it
is compared against.
