# The hole is a sampling gap, not a design gap, and the penalty is flat across twenty times the alignment

*2026-09-26 00:48, `runs/e208_hole_sweep_cs800_3seeds.json` — 1826.2 s (30 min) against the registered 15–30. Read by
`e207_penalty_driver_join.py`, exit 0. The registration is
`docs/findings/2026-09-26-registered-filling-c3s-alignment-hole.md`.*

## 1. The verdicts

| | claim | verdict |
|---|---|---|
| **T1** | a new level lands inside the hole (0.08475–0.27135) | **MET** — `swap8` at 0.09101 |
| **T2** | the highest-alignment cell below 0.271 has excess ≥ 0.06 | **FALSIFIER FIRED** — `swap8`'s excess is **0.00598** |
| **T3** | the new levels' penalties are non-decreasing in alignment | **FALSIFIER FIRED** — the order is `swap4` 0.01977, `swap16` 0.01709, `swap8` 0.00598 |

`swap8`'s excess of **0.00598 is the lowest value in the entire 50-cell record** — lower than the *unrewired*
connectome's own 0.01830. So the cell with more task alignment than any axis cell has seen is also the cell with the
least diagonalisation penalty.

## 2. What the falsifiers mean, and what they do not

**T2 firing is the answer C3 needed, not a failure of the run.** The registered falsifier was *"the hole behaves like
the axis and the jump happens between it and Erdős–Rényi"*, and that is what happened: alignment up to 0.09101 (1.64×
chance) leaves the penalty at or below the axis's own level. So **the penalty is flat across a factor of 20 in
alignment** — 0.006–0.023 for every cell from 0.00444 to 0.09101 — and the jump to 0.141–0.149 lives entirely in the
Erdős–Rényi regime at 4.89–5.23× chance. **The transition is in [0.09101, 0.27135], and this run put one cell at the
bottom edge of that interval and nothing inside it.**

**T3 firing is a sampling artifact, and the record can say so with a number.** The three new levels are not ordered
in alignment — `swap4` 0.03944, `swap8` **0.09101**, `swap16` 0.04146 — which contradicts the registration's premise
that alignment grows with swap strength (an extrapolation from three points). But the corpus was already measuring
the spread of alignment **at a fixed strength across realizations**, and at cs 800 it is large:

| topology (cs 800) | cells | alignment | spread | ratio |
|---|---|---|---|---|
| `real` | 3 | 0.00557 – 0.00575 | 0.00018 | 1.03× |
| `swap0.5` | 9 | 0.02051 – 0.03451 | 0.01400 | **1.68×** |
| `swap2` | 9 | 0.03257 – **0.08475** | 0.05218 | **2.60×** |
| `erdos_renyi` | 9 | 0.27135 – 0.29039 | 0.01904 | 1.07× |

The realization spread at `swap2` — **2.60×**, six independent `rewire_seed`s plus three re-measurements — is
*larger* than the `swap8`/`swap16` difference (2.2×). So the new levels' ordering carries no information about the
axis: at one realization per strength, the swap operation's alignment is a **noisy** function of its strength, and
`swap2`'s own realizations already reach 0.08475 — the hole's lower edge was not a limit of the operation at all.

**That reframes the hole itself**: it is a gap in the record's *sampling*, not in the design space. The swap
operation reaches 0.085 at `swap2` and 0.091 at `swap8`; what was never run is a family whose cells are *chosen by
alignment* rather than by strength, and the correct way to fill the interval [0.091, 0.271] is to sample
realizations (of `swap8`, `swap16`, ER mixtures) and keep the cells that land there — not to add strengths.

## 3. The reproduction datum this run also produced

The five existing levels were re-measured in the same artifact, with `--no-realized` as the one config difference:

| level | `e2_analytic` | `e208` |
|---|---|---|
| `real` | 0.01830 | **0.01830** |
| `swap0.1` | 0.02087 | **0.02087** |
| `swap0.5` | 0.02317 | **0.02317** |
| `swap2` | 0.01237 | **0.01237** |
| `erdos_renyi` | 0.14187 | **0.14187** |

**All five agree to five decimals.** The analytic penalty is a deterministic function of the circuit, the tasks and the
wiring, so this is the corpus's cleanest same-configuration reproduction — and it is also the check that `--no-realized`
is inert for the joined quantities, since the flag is the only difference between the two artifacts and the realized
arm is the only thing it touches.

## 4. C3, restated with the run's numbers

> **The diagonalisation penalty is flat at 0.006–0.023 for every topology whose tasks' alignment is at or below
> 0.091 (1.64× chance) — a factor of 20 in alignment, with the most-aligned cell holding the *smallest* penalty — and
> it is tight at 0.141–0.149 once alignment reaches 4.89–5.23× chance.** The transition lies in
> **[0.09101, 0.27135]**, where the record now has one cell at the edge and none inside.

**The falsifier remains the same and is now sharper**: a cell with alignment between 0.091 and 0.271 whose penalty is
between the two regimes' values (≈0.08) would make the response graded, and a cell there at ≈0.02 would leave the jump
as a property of the Erdős–Rényi construction rather than of alignment. **And the design that would settle it is now
determined**: sample *by alignment* (realizations of the strongest swap levels, keeping the cells that land in the
interval) rather than by further strengths, because the strength axis is noisy at one realization per point — measured
above at 2.60× at `swap2`, larger than the effect the new levels were added to detect.

## 5. What this does not do

It does not locate the transition (one cell at the interval's edge), does not separate alignment from `top_eig_share`
(0.934 at `swap8`, 0.657 at `swap16`, 0.804 at `swap2` — the statistics move together and the new levels break their
co-movement too), does not average realizations for the new levels (one drawing per strength, which is exactly why T3
is uninformative), and says nothing about the network substrate. The three new levels are still worth having: they
give the record its first cell above 1.53× chance and its lowest penalty anywhere.
