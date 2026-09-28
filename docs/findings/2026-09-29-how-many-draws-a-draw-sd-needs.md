# How many draws a draw sd needs: the paper's rung table reproduces, and six of its ten orderings are inside the error

*2026-09-29 02:20. Runs: **none new** — `experiments/e293_how_many_draws_a_draw_sd_needs.py` reads the five artifacts
the paper's section 4.3 table credits, writing `runs/e293_how_many_draws_a_draw_sd_needs.json`. Seconds.*

## 1. The one table whose subject is a draw sd

Section 4.3 carries a table of five named partition rungs, each with the draw-to-draw sd of its matched-random control
measured over 5 or 8 draws and each with the run that measured it credited in the row. It is the table that says which
rungs are near-diagonal and which are coarse, and the section's argument about **non-monotonicity** is read off the
ordering of those five numbers.

A standard deviation estimated from `k` draws has `k - 1` degrees of freedom, so its own relative standard error is
about `1/sqrt(2(k - 1))` — **27% at 5 draws and 35% at 8** — while the table's five entries are spread over a factor
of 5.7. That is close enough that the ordering needs checking rather than assuming.

## 2. V1 MET — the column reproduces, to 0.14%

| rung | draws | the artifact | the table | difference |
|---|---|---|---|---|
| `side` | 8 | 2.157e-4 | 2.16e-4 | +0.14% |
| `cell_class` | 5 | 2.371e-4 | 2.37e-4 | −0.04% |
| `ito_lee_hemilineage` | 5 | 4.158e-5 | 4.16e-5 | +0.05% |
| `supertype` | 5 | 8.351e-5 | 8.35e-5 | −0.01% |
| `cell_type` | 8 | 6.802e-5 | 6.80e-5 | −0.03% |

All five, from the runs the rows credit, and the recorded `draws` match the credited counts in all five. This is the
third of the paper's tables this line has re-derived from artifacts, after the `e151` registry (`e283`) and section
4.7's decomposition (`e289`).

## 3. V2 MET — and the column's own precision is the binding limit

**Six of the ten pairwise orderings are not resolved at 95%.** The four that are, are the coarse-versus-fine
comparisons:

| pair | ratio | resolved at 95% |
|---|---|---|
| `cell_class` / `ito_lee_hemilineage` | **5.70** | yes |
| `side` / `ito_lee_hemilineage` | 5.19 | yes |
| `cell_class` / `cell_type` | 3.49 | yes |
| `side` / `cell_type` | **3.17** | yes |
| `cell_class` / `supertype` | 2.84 | no |
| `side` / `supertype` | 2.58 | no |
| `ito_lee_hemilineage` / `supertype` | 2.01 | no |
| `ito_lee_hemilineage` / `cell_type` | 1.64 | no |
| `supertype` / `cell_type` | 1.23 | no |
| `side` / `cell_class` | 1.10 | no |

So the table's **middle** is what the error bars cannot separate — `ito_lee_hemilineage`, `supertype` and `cell_type`
are three rows whose orderings are all unresolved. And the arithmetic says what it would take: a **2x** ordering needs
**18 draws per rung** and a **1.5x** ordering needs **49**, against the 5 and 8 the table has. The fix is more
**draws** rather than more seeds, and the runner already has a `--draws` flag.

## 4. V3 MET — and the ordering the paper's argument uses is safe

The section's non-monotonicity argument contrasts `side` against `cell_type` — a ratio of **3.17**, which 5 and 8
draws *do* resolve. So the argument does not rest on an unresolved ordering, and what this unit adds is a warning
about the rows it does *not* use: a reader who takes the table's ordering as a ranking of rungs by draw sd would be
reading three of its rows past their own error bars.

## 5. What it cannot do

**The intervals assume the draws are independent normal samples** of the control's excess, which is the arithmetic the
runner's own `control_sd_across_draws` is built on and not something this unit checks. **The degrees of freedom are
`k - 1` and no more**: nothing here accounts for the seed component also inside each draw's mean, so the intervals are
a *lower* bound on the real uncertainty — the true ordering is weaker than reported, not stronger. **Six of ten
unresolved is not six of ten wrong**: an unresolved ordering is one the data cannot distinguish, and the true values
may still be ordered as printed. **The section's argument uses more rows than this table**, since it also reads a
four-point concentration series from other artifacts, so V3 clears the comparison this unit can check and not the
whole argument. **And no number of the paper's is re-measured**: what is new is the column's own error bar and what it
does to the ordering.
