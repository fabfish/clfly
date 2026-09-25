# The penalty follows how many degree sequences the construction destroys, not the alignment

*2026-09-26 03:49, `runs/e216_inalloy_rs0.json` … `rs2.json` — three cells, 12 min. The registration is
`docs/findings/2026-09-26-registered-the-source-alloy-which-side-of-the-edge.md`.*

## 1. The three cells

| drawing | alignment | × chance | excess | sem | `top_eig_share` | eff. rank |
|---|---|---|---|---|---|---|
| rs0 | 0.18202 | 3.28× | +0.04212 | 0.00049 | 0.690 | 2.40 |
| rs1 | 0.16978 | 3.06× | +0.04593 | 0.00054 | 0.666 | 2.35 |
| rs2 | 0.08997 | 1.62× | +0.05208 | 0.00042 | 0.426 | 9.71 |

- **Y1's falsifier landed**: the excess is **0.04212–0.05208**, at or below the 0.06 bound. Destroying the
  **out**-structure while preserving every in-degree leaves the penalty at the alloy's and the axis's order — so the
  out-side is **not** the driver, and with Erdős–Rényi high while destroying *both* sides, the registered
  "joint destruction" reading is the one left standing.
- **Y2's null band**: two of the three cells are inside the band (0.18202, 0.16978) and one is at its floor (0.08997),
  none above 0.20 — so this null reaches the hole's **middle**, the best coverage any construction has produced after
  the alloy's single 4.18× drawing.
- **Y3, reported**: the within-drawing spread is **1.24×** (0.00996) over three drawings — **tight**, next to Erdős–Rényi
  at 1.05× and the sign shuffle at 1.07×, against the **alloy's 3.34×**.

## 2. The ladder: how many degree sequences are destroyed

Four constructions now separate cleanly by one property, and the penalty follows it:

| construction | out-degree | in-degree | **sequences destroyed** | penalty | alignment |
|---|---|---|---|---|---|
| `swap*` (the walk) | preserved | preserved | **0** | 0.012–0.023 | 0.65–1.72× |
| `signshuffle` | preserved | preserved | **0** (signs instead) | 0.0278–0.0298 | 0.34–0.40× |
| **`inalloy1`** | free | **preserved** | **1** | **0.042–0.052** | 1.62–3.28× |
| `alloy0.9` / `alloy1` | **preserved** | free | **1** | 0.0175–0.101 (mean 0.044) | 1.55–4.18× |
| `erdos_renyi` | free | free | **2** | **0.141–0.149** | 4.89–5.23× |

**The two ways of destroying exactly one degree sequence give the same penalty** — the source alloy's mean is 0.0467
and the target alloy's is 0.0440, agreeing to **5%** from two independent constructions with different free sides —
while destroying none gives ≈0.02 and destroying both gives ≈0.145. **A three-level ladder with a 7× top step**, and
the top step needs *both* sides destroyed.

## 3. And the alignment does not follow the same ladder

The same table sorted by alignment tells a different story: the sign shuffle sits at **0.34–0.40× chance** with a
penalty of 0.028, i.e. *below* the axis's alignment and *above* its penalty; `inalloy1` and the alloy overlap in
alignment (1.6–4.2×) with penalties 0.042–0.052 and 0.0175–0.101; Erdős–Rényi's alignment (4.89–5.23×) is only 1.2×
above the alloy's best drawing (4.18×) while its penalty is 2.7× higher. **So the two quantities are decoupled across
constructions**, which is the same conclusion the coverage census and the ten-cell regression reached from inside a
single construction, now confirmed at the level of the constructions themselves.

## 4. What this establishes and what it leaves

**Established**: the penalty's response is **ordinal in the number of destroyed degree sequences** (0 → ≈0.02, 1 →
≈0.045 by two independent routes, 2 → ≈0.145), and it is **not** a function of the tasks' alignment. The sign pattern
is excluded (`e215`), and this null excludes the reading that either side alone carries the jump.

**Left open**: *why* destroying both sides is worth 3× while destroying either alone is worth 2×, and whether the
ladder survives at other circuit sizes — the four constructions have all been measured at cs 800 with `seed0` 0, so
the ladder is a statement about one circuit. The mechanism candidates that remain are about the **interaction** of the
two margins: with one side preserved, a neuron's edge set still respects one of the two structures the task
propagation uses, and with both destroyed nothing does. Nothing here tests that, and the all-important caution holds:
these are four constructions at three to ten drawings each, so the levels are ranges and not fitted values.
