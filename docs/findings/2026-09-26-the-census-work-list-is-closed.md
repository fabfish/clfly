# The census's work list is closed: the low-`rho` rank levels are stable, and the drawing noise has a profile in `rho`

*2026-09-26 19:05. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3 --seed0 0 -q 0.02
--topologies alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed 1`, one per `rho` (0.5, 0.7, 0.8) — **three runs,
~7 min apiece, all exit 0** — `runs/e255_cs300_rho{05,07,08}_rs1.json`, read by `experiments/e255_low_rho_cells.py`
(`runs/e255_low_rho_cells.json`).*

## 1. The unit: the census's own work list

`e254` left **two of the record's twelve quoted figures exposed**, both through the same three cells — cs 300/support 30
at `rho` 0.5, 0.7, 0.8, one drawing per family. Three runs of the ladder families add a second drawing to each:

| `rho` | `alloy1` rank | `inalloy1` rank | `erdos_renyi` rank | `alloy1` excess | rank factor | spread now |
|---|---|---|---|---|---|---|
| 0.5 | 26.52 → **26.41** | 25.82 → 25.90 | 26.75 → 26.84 | 0.02940 → 0.03025 | **1.00×** | 1.029× |
| 0.7 | 22.96 → **23.33** | 22.86 → 22.74 | 25.23 → 25.44 | 0.08417 → 0.08757 | **1.02×** | 1.040× |
| 0.8 | 17.54 → **19.26** | 19.77 → 18.10 | 23.08 → 23.42 | 0.11987 → 0.12663 | **1.10×** | 1.056× |

**R1 FALSIFIER FIRED.** All three cells agree within ±10% — the factors are **1.00×, 1.02× and 1.10×**, and the excesses
agree to 3–6%. So **the low-`rho` rank levels are stable**, and the census's flag was a **count of drawings and not a
measure of risk**, which is exactly what the falsifier's wording anticipated.

**R2 MET.** The monotone fall survives on the new drawings: 26.41 > 19.26 > 7.50 (the `rho`-0.9 mean of three).

**R4: the work list is closed — 0 of 12 registered figures still name a single-drawing input.**

## 2. What that gives the rank curve: a profile of its drawing noise in `rho`

This fire and `e251`/`e253` together measure the same statistic at both ends of the `rho` range, and they do not
resemble each other:

    rho 0.5 to 0.8, cs 300   alloy1's rank moves 0.4% to 9.8% between two drawings   -> STABLE
    rho 0.99, cs 300         alloy1's excess spans 32.04x over three drawings       -> EXPLODES
    rho 0.95 and 0.98        the top step moves by factors of 1.54 and 4.47         -> EXPLODES

**The drawing noise of the task geometry is a function of where the geometry sits, not a constant.** The mechanism is
visible in the two ceilings: at `rho` 0.5 an `alloy1` rank of 26.52 sits against the **30-neuron support**, so a drawing
has nowhere to move, while at `rho` 0.99 the rank is 1.05–3.48 and a small change in the assembly geometry moves it by
a large *relative* amount. And the spread the new drawings buy at those cells — **1.029×, 1.040×, 1.056×** — are the
tightest in the corpus against the 2.58× to 32.04× of the high-`rho` cells.

## 3. The session's audit ledger

With the census closed, this line's twelve quoted figures stand as: **6 SAFE** (never thin), **6 thin and now
checked** — and of those six, **4 agreed with their quoted form and 2 did not**:

| checked figure | quoted | after checking |
|---|---|---|
| the top step 2.76×/3.02× | two spellings | agreed (`e242`/`e243`: median 3.45× → 3.285×, within the 1.25× bar) |
| the (1,0) margin across cells | 0.787–1.660 | agreed (`e245`–`e250`) |
| the low-`rho` rank curve | falls monotonically | agreed (this fire) |
| the cs-300 rank contrasts resolve | 7.68×–25.25× | **moved** (`e253`: five of six families unresolvable) |
| `alloy1`'s own spread | 3.34× | **moved** (`e247`: 1.64× at a two-drawing budget) |
| the late advantage | 1.91 / 5.53 / 14.77 × | **moved** (`e251`/`e253`: 1.94× pooled, and no rise at all on the new drawings) |

So **three of six thin figures were wrong as quoted, and every one of the three was wrong in the same direction: a
headline that was a single drawing's.** That is the ledger this census was built to make.

## 4. And the readers moved again, which is the same lesson

The six new drawings grew the pooled corpus to **53 groups**, and everything downstream moved without any claim being
re-run on purpose:

    e244 K1   back to its NULL BAND (kind 1's median fell to 1.21x)      K3 now 14 of 17 cell-pairs
    e246 N1, N2 MET with a narrower one-side rank range (8.00x to 14.11x) N3 -0.257, 25 of 45 pairs (56%)
    e247 R1, R2 falsifiers (alloy1's span 31.15x against the 2.5x bar)    R5 +0.761 over 53 groups
    e252 D2   now a FALSIFIER: the domain no longer restores R1

The last of those is the sharpest: `e252`'s claim was that excluding the near-critical cell restores the three demoted
verdicts, and it did — but with the low-`rho` cells drawn, **R1's falsification survives inside the domain**, because
those cells are in-domain and they keep the drift. So the domain's restoration of R1 was itself a
corpus-composition fact, which is the third time this session that a verdict has flipped with the corpus rather than
with a measurement.

## 5. A third state `e230`'s audit has: drawing a family can take it *out* of scope

Trimming `e230`'s declarations turned up an unrecorded behaviour worth stating. The audit's verdict is computed from
the **as-read** contrast, which needs a rho group of exactly one drawing; and it **skips** any family without one —
neither resolvable, nor unresolvable, nor offending. So:

    cs 300 alloy1   at 25.25x as read     RESOLVABLE
                    at 1.51x (after e253) NOT RESOLVABLE, declared
                    now                   between_single is None -> OUT OF SCOPE, and un-declared

Every rho group at cs 300 now has two drawings, so the as-read column is undefined for those families and the audit
carries them no longer. A declaration is therefore **not permanent** — it is a statement about the corpus's current
drawings — and the audit's scope **shrinks as the corpus thickens**, which means a family can leave it without the
question being settled. `e230` now declares three families where it declared five this morning.

## 6. What it cannot do

Two drawings per cell is **one difference and not a distribution**; the ceiling at `rho` 0.5 makes the noise one-sided
there, so a 1.00× factor at that cell is not independent evidence of stability (only `rho` 0.8's 1.10× carries any
room); the kind-0 families are not drawn at these `rho` values at all, so the (1, 0) margin's low-`rho` behaviour stays
unmeasured; `rho` cannot be separated from the geometry it sets; and this closes **one** of the corpus's two thin
regions — cs 800's `rho` 0.5, 0.7 and 0.8 cells still carry three families at one drawing each, and the census's
registry does not yet name a figure that rests on them, which is a gap in the registry rather than in the corpus.
