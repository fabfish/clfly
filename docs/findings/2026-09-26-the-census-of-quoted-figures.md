# The census of quoted figures: twelve headline numbers, six safe, four decomposed by accident, two still thin

*2026-09-26 18:40. Runs: **none new** — `experiments/e254_quoted_figure_census.py` reads the corpus's drawing counts
against a hand-made registry of the figures this session quotes, written as `runs/e254_quoted_figure_census.json`.
JSON-only, seconds.*

## 1. Why this exists

Four times this session a headline figure turned out to be a single drawing's, and every time it was found by a run
looking at something else: the `rho`-0.99 top step of 14.77× (`e251`), the "late advantage" at 0.95 and 0.98 (`e253`),
and `e230`'s cs-300 rank contrasts, whose withdrawal had to be written into the paper's prose. The instrument that
should have existed is a census: **every quoted figure, with the exact (cell, family) inputs its arithmetic uses and
how many drawings each of those inputs has.**

## 2. The census

Twelve registered figures, classified by the corpus as it stands:

| figure | inputs | verdict | thinnest input |
|---|---|---|---|
| the cs-300 rank contrasts resolve | 14 | **STILL EXPOSED** | `alloy1` at cs 300/`rho` 0.5, **1 drawing** |
| the rank curve falls monotonically in `rho` | 14 | **STILL EXPOSED** | `alloy1` at cs 300/`rho` 0.5, **1 drawing** |
| the top step 2.76× and 3.02× | 3 | DECOMPOSED (`e242`/`e243`) | every input has two or more |
| `alloy1`'s own spread 3.34× | 1 | DECOMPOSED (`e247`) | — |
| the (1, 0) margin across cells | 20 | DECOMPOSED (`e245`–`e250`) | — |
| the late advantage | 6 | DECOMPOSED (`e251`/`e253`) | — |
| `erdos_renyi` does not collapse | 3 | SAFE | — |
| the ladder's levels at the convention cell | 3 | SAFE | — |
| the "7× top step is cs 800's" | 6 | SAFE | — |
| the floor's level | 2 | SAFE | — |
| the one-side level rises as the circuit shrinks | 2 | SAFE | — |
| the two-side level is nearly flat | 3 | SAFE | — |

**C1 FALSIFIER FIRED** — I registered that at least **three** figures would still be exposed and only **two** are. The
reason is the session's own work: four figures that would have been exposed when this line started have since been
drawn again, so the census finds the record in better shape than the registration assumed.

**C2 MET** — and this is the census's deliverable: **both remaining exposures run through the same three cells**, cs
300/support 30 at `rho` **0.5, 0.7 and 0.8**, each carrying **one drawing per family**. So the un-checked region of
this record is not diffuse; it is the **low-`rho` end of the rank curve**, and it can be closed with three runs.

## 3. The corpus's own unevenness, and one thing it shows about the convention cell

**17 of the corpus's 22 cells carry a family with a single drawing.** The distribution:

    minimum 3 drawings   2 cells   cs 300/support 30 and cs 400/support 40, at rho 0.9 (the equal-count bases)
    minimum 2 drawings   3 cells   cs 300/support 30/rho 0.99, cs 800/support 20 and cs 800/support 160
    minimum 1 drawing   17 cells   everything else

The convention cell — the most-quoted cell in the record — is thin **only through `swap0.1`, `swap4`, `swap8` and
`swap16`**, the weak rungs of the swap axis whose analytic arm was never run; its core families carry 3 to 9 drawings
each. That is why the ladder's levels, the top step and the floor all come out SAFE while the rank curve at other
`rho` values does not: **the record's thinness is where its expensive runs were not repeated, and that is a fact about
the design history rather than about the substrate.**

## 4. What the census says to do, and what it cannot say

The work list is now two items rather than a worry: **draw the cs-300/`rho` 0.5, 0.7 and 0.8 cells once more** (three
runs of the ladder families, ~10 min each) and both remaining figures become DECOMPOSED, or declare those cells and
carry the low-`rho` end of the rank curve with a single drawing attached — which the record would then be stating
rather than assuming.

It cannot: make the registry anything but **hand-made and finite** — it covers the figures this session quotes and a
figure missing from it is invisible; say whether an exposure *matters*, since the census counts drawings and not
risk, and the two thin figures here are at low `rho` where `e230` measured the *scatters* to be small (alloy1's
within-scatter at cs 300 is 2.73× against the 8.77× and 7.77× of the swap families at the same size) — so the low-`rho`
rank curve may well be the safe end of the corpus, and the census cannot tell that from the counts; treat SAFE as
"resolved", since `e247` measured a two-drawing spread to be the corpus's noisiest statistic, so SAFE here means "two
or more"; or treat DECOMPOSED as "agreed", since `e253`'s decomposition of the `rho`-0.98 point moved the quoted top
step by a factor of 4.47.
