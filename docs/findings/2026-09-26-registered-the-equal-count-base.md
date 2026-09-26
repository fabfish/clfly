# Registered: the equal-count base — six families at three drawings each, one run

*2026-09-26 16:40, registered before its run. Run: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3
--seed0 0 -q 0.02 --topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed 5` — **one run, one cell**, to be
written as `e245_cs300_kind0_rs5.json`. The only other artifact in this line with that name pattern is `e245`'s pair at
seeds 3 and 4, so the file name keeps the family.*

## 1. The band `e247` left, and the cheapest way out of it

`e247` showed that every spread this line has compared is a max-over-min over **however many drawings the cell
happened to have**, and that count-matching post hoc turns the numbers into bands: `alloy1`'s cross-cell drift is
somewhere between 1.6× and 3.0×, `inalloy1`'s between 1.2× and 2.4×, the kind-0 families' between 1.0× and 1.8×, and
the reason is that a count-matched statistic computed from a corpus with two-drawing cells rests on single pairs.

Resolving a band needs a **designed** base whose families all have the same number of drawings, and the corpus is one
run away from having one. At cs 300/support 30:

    alloy1        n = 3   (rewire seeds 0, 1, 2)
    inalloy1      n = 3   (0, 1, 2)
    erdos_renyi   n = 3   (0, 1, 2)
    swap0.5       n = 2   (3, 4)     <- e245
    swap2         n = 2   (3, 4)     <- e245
    signshuffle   n = 2   (3, 4)     <- e245

**One run at `rewire_seed` 5 gives each of the three kind-0 families its third drawing**, and the cell becomes
**six families at three drawings each** — 18 groups, every count equal, no post-hoc subsetting. That is the whole
design: the confound `e247` found is removed by construction rather than by arithmetic, at the cost of one run.

## 2. The registered claims

- **S1 — the (1, 0) question at equal count, which is the point of the run.** With every family at three drawings, the
  kind-0 families' **median** spread is **below** the kind-1 families' median — i.e. the pooled ordering holds inside
  the cell once the sample sizes are equal. **Falsifier**: kind 0 at or above kind 1, the reversal at equal count;
  **null**: the medians within 10%.
  Two earlier readings point opposite ways and neither was taken at equal count: `e245`'s all-drawings form at this
  cell had kind 0 1.39× against kind 1 1.42× (+2.2%, its registered null band), and `e247`'s two-drawing form had
  kind 0 1.39× against kind 1 1.26× (the pooled way). **What the third kind-0 drawing does is the measurement.**
- **S2 — the two-side rung at equal count.** `erdos_renyi`'s spread is below **both** kind-1 families' spreads, as it
  is in every cell of this corpus. **Falsifier**: kind 2 at or above either.
- **S3 — the reading is stable to which drawing is dropped.** `erdos_renyi` is the tightest of the six families under
  **every** leave-one-out subset of the base (each family's spread recomputed on each of its three two-drawing
  subsets). **Falsifier**: a subset in which another family is tighter — which would say the "tightest family"
  statement depends on one drawing.
- **S4 — reported, not claimed.** All six families' excesses, ranks and spreads at the cell, the level confound beside
  them, and what the new drawing does to the three readers (`e244`, `e246`, `e247`) whose live censuses this cell is
  in.

## 3. Cost, and what it cannot do

**Cost**: `e245`'s two runs at this cell were three topologies each and took ~7 min apiece, so this is **≈7 min**.

It is **one cell at one size and one `rho`** (the builder's default, `config.rho: None`); three drawings is still a
range and not a distribution, so this narrows the band rather than closing it; the three kind-0 families share the
run's one `rewire_seed`, so their third drawings are not independent of each other; the earlier three drawings of the
kind-1 and kind-2 families come from `e217`/`e219` rather than from this design, so the base is **equal-count but not
equally drawn** — the identity of the drawings still differs, which no equal count can fix; and the comparison remains
one of **spreads**, saying nothing about the levels.
