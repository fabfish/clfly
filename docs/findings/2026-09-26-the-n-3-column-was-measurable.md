# The n = 3 column was measurable: one of the three published figures was under its own floor, not two

*2026-09-26 21:55. Runs: **none new** — `experiments/e261_three_rep_floor_measured.py` reads the three-replicate runs
`e259` extrapolated over (`runs/e28_side_lam0.1.json`, `runs/e31_methodlist_check.json`) and the corpus's largest
matched pair (`runs/e178_rung_side_cs300_144reps.json`), writing `runs/e261_three_rep_floor_measured.json`. Seconds.*

## 1. The item: a corollary of `e259`, and the assumption it spent

`e259`'s four registered claims stand and nothing here touches them — they are about the **sixteen**-replicate column.
What it added beside them, in its third section and in the programme table's status cell, was a second corollary:

    at n = 3 the three floors are 0.059, 0.075 and 0.100 against published effects of 0.0069, 0.0648 and 0.0718, so
    **two of the line's three figures were published below their own detection floor**

Those floors could only be built one way: by scaling the sixteen-replicate sem with `sem ~ 1/sqrt(n)`, which the same
module's P4 flagged as an assumption. **The runs that would test it were on disk.** The published figures are
recoverable to their own artifacts — `e28` is the `side` run at three replicates and `e31` the `cell_class` one, and
each is its powered re-run's configuration with `repeats` changed (`side`: only `json_out` and `repeats` differ;
`cell_class`: those two and the arm list, since `e31` ran two arms where `e46` ran three) — so the floors at three
replicates are measurable.

**The identification is itself a check.** The cross-rung figure's three-replicate run is the *pair* of them, and
reconstructing it from the two replicate lists gives **+0.07176 at 2.134σ** against the published **+0.0718 at
2.13** — four decimal places and both sigmas, so the runs are the right ones rather than merely the right shape.

## 2. The three floors, measured against the ones that were scaled

| figure | published | its own 3-replicate sem | measured floor (2 sem) | published / floor | `e259`'s scaled floor | factor too large |
|---|---|---|---|---|---|---|
| `side` | +0.0069 | 0.014456 | **0.02891** | **0.239** (below) | 0.05901 | **2.04x** |
| `cell_class` | −0.0648 | 0.024498 | **0.04900** | **1.323** (above) | 0.07459 | **1.52x** |
| `side − cell_class` | +0.0718 | 0.033625 | **0.06725** | **1.068** (above) | 0.09979 | **1.48x** |

**So the corollary holds for one of the three, not two.** `side` was indeed published below its own detection floor
(it is 0.48σ by its own sem, which is what "below a 2σ floor" means), while `cell_class`'s published 2.65σ figure was
**1.32x its own floor** and the cross-rung's 2.13σ was **1.07x** its own.

## 3. Why the scaling was the wrong instrument for that column

The two configurations the line has run at **both** budgets measure the floor ratio directly:

| configuration | floor at n = 3 | floor at n = 16 | measured ratio | `sqrt(16/3)` | sd ratio (3 against 16) |
|---|---|---|---|---|---|
| `side` (e28 against e60) | 0.02891 | 0.02555 | **1.131** | 2.309 | **0.490** |
| `cell_class` (e31 against e46) | 0.04900 | 0.03230 | **1.517** | 2.309 | **0.657** |

The whole deviation is the three-replicate run's own sd: at three replicates it comes out 0.49x and 0.66x the
sixteen-replicate one, and `1/sqrt(n)` then supplies only the 2.31x. **A floor scaled from another budget's variance
is a different quantity and not a worse estimate of the same one** — and the smaller budget is exactly where a
variance estimate is least trustworthy (the 0.49 ratio is well inside an F-test at 15 and 2 degrees of freedom, so
this is "the extrapolation is not supported" rather than "a different law holds").

## 4. The registered claims (R1-R3 all MET)

| claim | what it says | measured |
|---|---|---|
| **R1** | the extrapolated floor is not the measured one | all three are above it, by 2.04x, 1.52x and 1.48x |
| **R2** | and that flips one figure rather than none | 0.239, 1.323, 1.068: one below its own floor, two above |
| **R3** | the largest budget is 144 paired replicates | `e178` is a matched pair over 144 at another cell, where `e259`'s ladder stops at 40 |

**R3 is a correction to `e259`'s reach, not to its arithmetic.** `e178` (cs 300 / support 80 / lambda 1.0, 7.39 h, the
corpus's largest single run) reads **−0.00203 ± 0.00725 = 0.28σ** against a floor of 0.01449: the line's largest
budget on a `side` rung is itself a null. Its configuration is not the published figures', so it cannot re-test them —
which is the honest form of "the side figure sits below its own floor at every budget this line has run": true at the
two budgets of its **own** configuration (3 and 16), and the largest budget the line has paid for belongs to another
cell.

**The price, reported and not claimed.** 219.5 replicates — `e259`'s requirement for `side` — costs 40.5 h at that
configuration's own rate (664.2 s per replicate), 26.2 h at `cell_class`'s (429.3 s) and 11.3 h at `e178`'s
(184.8 s), against the corpus's largest single run of 7.39 h. So the question `e259` posed is buyable, but only on the
cheapest cell and not on the cell the published figure belongs to.

## 5. What it cannot do

It leaves `e259`'s four claims alone, and it re-reads its n = 3 column only — the sixteen-replicate figures and the
`1/sqrt(n)` floors at 6 and 40 are untouched. The three-replicate runs are configurations matched field by field to
their re-runs, not the same process. The measured floors carry their own sampling noise, which at three replicates is
large. And the corpus is scanned for the largest budget, so a run outside `runs/` is invisible.

**One defect, caught by the gates, of exactly the class `e205` was written about.** The module's first version priced
each run with `d.get("timing_s")` — the spelling the trained runners write, not the quantity. `e205` fired on five such
lines, and the module now goes through `clfly.bench.artifacts.duration_seconds`, which reads all three spellings. The
numbers here are unaffected (the two artifacts whose durations matter, `e60` and `e46`, write `timing_s`), but a reader
keyed on a spelling is blind to every instrument that writes another, which is `e205`'s finding recurring one module
later and in a module written the same fire that read it.
