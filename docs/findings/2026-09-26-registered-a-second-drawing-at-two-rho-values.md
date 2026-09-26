# Registered: a second drawing at `rho` 0.95 and 0.98 — is the "late advantage" a cell's or a drawing's?

*2026-09-26 18:05, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30
--seeds 3 --seed0 0 -q 0.02 --topologies swap0.5,swap2,signshuffle,alloy1,inalloy1,erdos_renyi --no-realized` —
**two runs, one cell each**, `--rho 0.95 --rewire-seed 1` and `--rho 0.98 --rewire-seed 1`, to be written as
`e253_cs300_rho095_rs1.json` and `e253_cs300_rho098_rs1.json`. One run each because each of those cells carries
**exactly one drawing** today and a second is what the question needs.*

## 1. Why these two cells

This record's headline reading of the ladder's mechanism is that the two-side advantage is **late rather than
high-`rho`**: "*Erdős–Rényi over `alloy1` is 1.91× at `rho` 0.95, 5.53× at 0.98 and 14.77× at 0.99*". `e251` then
decomposed the third of those three points by drawing and found it is **one drawing's arithmetic** — the quoted 14.77×
comes from the corpus's seed-0 drawing, two more drawings at the same cell and the same `rho` give **2.22×**, and the
three pooled give 2.91×.

**The first two points of the same sentence rest on one drawing each as well**, and nobody has looked:

    rho 0.95   alloy1 0.06927  erdos_renyi 0.13223  ->  1.91x   (one drawing)
    rho 0.98   alloy1 0.01674  erdos_renyi 0.09253  ->  5.53x   (one drawing)
    rho 0.99   alloy1 0.00547  erdos_renyi 0.08078  -> 14.77x   (one drawing, decomposed by e251)

One run at each `rho` adds a second drawing to every family at those two cells, which is enough for the **first
decomposition of both points** — the same arithmetic `e251` did at 0.99.

## 2. The registered claims

- **W1 — the discriminating one: is the quoted figure a drawing's?** At `rho` 0.98 the top step (`erdos_renyi` over
  `alloy1`) on the new drawing differs from the corpus's single-drawing **5.53×** by a factor of **at least 1.5** in
  either direction — the same lottery `e251` found at 0.99 (**falsifier**: within **±10%**, which would say the quoted
  value is typical of its cell and that the rho-0.99 swing is peculiar to 0.99 rather than to the regime; **null**: a
  factor between **1.1 and 1.5**).
- **W2 — the trend's sign survives one more drawing.** On the new drawings the top step at `rho` 0.98 is still
  **above** the one at `rho` 0.95, as the quoted pair is (5.53× against 1.91×). **Falsifier**: the new pair reverses
  the order, which would leave the "late" reading with no support at the drawing level either.
- **W3 — reported, not claimed.** Both new drawings' six families at both cells: their excesses, the resulting top
  steps and one-side levels, and the levels the corpus's own drawings read there — so the two points' decomposition is
  visible as a table rather than an assertion.
- **W4 — reported.** What the two new cells do to the declared domain of `e252`: their families' drawing scatters at
  high `rho` are expected to exceed the bar, which would put two more cells outside the domain at no cost to any claim
  (they carry two drawings each and no kind-0 spread).

## 3. Cost, and what it cannot do

**Cost**: six topologies at cs 300 have run at ~9–13 min per run, so **two runs are 20–26 min** — about one fire's
wait.

It cannot: give a *distribution* — two drawings per cell is one difference, and `e251` measured that a two-drawing
spread is the corpus's noisiest statistic, so a large or small swing here is evidence about that pair and not a
variance; test the third point (rho 0.99) again, that having been done; separate the drawing lottery from the fact that
`rho` 0.95 and 0.98 are different **task geometries** as well as different scalars, so the two runs' `alloy1` values
are not a controlled contrast; give any kind-0 **spread** at these cells (one run means one drawing each, so the
(1, 0) margin is not computable there and this unit says nothing about it); or fix the fact that the corpus's own
drawings at both cells are `rewire_seed` 0 while the new ones are seed 1 — the same unequal drawing the earlier bases
had, stated rather than hidden.
