# Registered: filling C3's alignment hole, because that is the one measurement its restatement needs

**Date:** 2026-09-26. **Registered before its run.** Artifact to be written:
`runs/e208_hole_sweep_cs800_3seeds.json`.

---

## 1. The hole, measured an hour ago

`e207` joined every (artifact, topology) cell in the record that carries both a task-geometry block and an analytic
diagonalisation penalty — 42 cells, 25 artifacts, circuit sizes 300–800 — and the sorted table shows **two regimes
with nothing between them**:

| regime | cells | alignment | × chance | penalty |
|---|---|---|---|---|
| the biological axis (`real`, `swap0.1`, `swap0.5`, `swap2` and the rewire families) | 34 | 0.00444 – **0.08475** | 0.07 – 1.53 | 0.01101 – 0.05782 |
| Erdős–Rényi | 8 | **0.27135** – 0.29039 | 4.89 – 5.23 | 0.14134 – 0.14897 |

The gap between the two penalty ranges is **0.08352**, and the **alignment hole is a factor 3.2 wide**
(0.08475 → 0.27135) **with no cell in it**. That hole is the entire reason C3 cannot yet be stated as a testable
prediction: the record contains a flat regime and a high regime and *no observation of the transition*, so
"threshold" and "steep gradient" are indistinguishable from the data.

## 2. The design

One command, derived from `e2_analytic`'s own config (rule 44) with **one field changed** — the topology list:

```
experiments/e2_topology_gap.py --circuit-size 800 --support 80 --seeds 3 --seed0 0 --q 0.02 \
  --topologies real,swap0.1,swap0.5,swap2,swap4,swap8,swap16,erdos_renyi --no-realized \
  --json-out runs/e208_hole_sweep_cs800_3seeds.json
```

- **The three new levels are `swap4`, `swap8` and `swap16`** — the same degree-preserving double-edge swap
  operation at 4×, 8× and 16× the edge count. The alignment axis grows roughly 2.4–2.8× per 5× of swap strength
  (0.00919 at 0.1, 0.02176 at 0.5, 0.06034 at 2), so these three strengths are where the hole should be reachable;
  `erdos_renyi` is kept as the high anchor and the four existing levels as the axis anchors.
- **The five existing levels are re-measured in the same artifact**, which makes the join self-contained *and* gives
  a same-configuration reproduction datum for the analytic path (`e2_analytic`'s own values are the comparison).
- **`--no-realized` is the one field that differs from `e2_analytic`'s config, and it is inert for everything this
  design reads**: the flag empties the `realized` block and nothing else — the `geometry` block and
  `analytic_excess` are computed above it in the same loop iteration. That is checked by reading the runner, and the
  claim it makes is that the five re-measured anchors reproduce `e2_analytic`'s analytic values *despite* the flag.
- **Cost (rule 49)**: `e2_analytic` took **1442.9 s** for five topologies with the realized arm, i.e. ~145 s per
  topology analytic-only (the realized arm is *"about half the runtime"* by the runner's own comment), so eight
  topologies are **15–30 min**, the upper end for `erdos_renyi`, which took ~9 min per topology at six seeds in
  `e48`. One command on an idle machine.

## 3. The claims

**T1 — the hole is filled (a design check, not a prediction about the substrate).** At least one of the new levels
has `all_pairs_alignment` inside the hole, i.e. **above 0.09 and below 0.271**. **Falsifier**: every new level lands
either below 0.085 or above 0.271, which would mean the swap operation cannot reach the intermediate regime at this
circuit size and the hole is a property of the *design space* rather than of the record — a result worth having and
not a failure of the run.

**T2 — threshold or gradient (the question C3 needs).** The quantity is the analytic diagonalisation penalty
(`diagonal(EWC).analytic.excess_mean`), which is 0.01237–0.02317 across the five existing levels and 0.14187 at
Erdős–Rényi. **The registered test is the highest-alignment cell that is still below 0.271**: its excess **at or
above 0.06** means the jump is already substantially made inside the hole, i.e. the response is a **steep gradient in
alignment**; **at or below 0.035** means the hole behaves like the axis and the jump happens between the last hole
cell and ER, i.e. a **threshold that alignment alone does not cross** — the ER jump is then a property of that
construction (degree distribution, densification) rather than of the tasks' geometry. **Null worth keeping**:
0.035–0.06, which is unresolved at three seeds and would need the middle level re-run at more seeds rather than more
levels.

**T3 — the order inside the new levels.** The new levels' penalties are **non-decreasing in alignment** (rank
correlation +1 across the three new cells, ties allowed). **Falsifier**: a negative rank correlation, which would say
penalty and alignment move oppositely *inside* the hole — the plan's oldest result ("the gap moves opposite to
overlap") holding over the one range where nobody has looked. **Null**: positive but not monotone.

**Reported rather than claimed**: whether the five re-measured anchors reproduce `e2_analytic`'s analytic values
(same command, same seeds, one inert flag apart), and the alignment and excess of every cell so that the join's new
points can be added to `e207`'s sorted table without a second transcription.

## 4. What this cannot do

- **Locate the transition.** Three new levels in a 3.2× window can say *graded* or *not graded* and cannot put a
  threshold on the axis.
- **Separate alignment from the other geometry statistics.** Effective rank, `flattening` and `top_eig_share` move
  together with alignment along a swap axis by construction, so a graded response is a graded response to *the
  swap operation as measured by alignment*, not to alignment alone.
- **Give a distribution.** Three seeds per topology, and one swap realization per strength (the rewiring stream is
  `seed0`, which is also the task stream — `--rewire-seed` exists and is deliberately not varied here, so the design
  stays comparable to `e2_analytic`).
- **Speak for the network substrate**, whose penalty is a different instrument, or for the other circuit sizes,
  which have their own anchor sets and no `erdos_renyi` high regime above cs 700 except at cs 800.
