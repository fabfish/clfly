# The last two unaudited sections were clean, and the only error this fire found was mine

**Date:** 2026-09-23
**Method:** §3 (Substrate) and §6 (Methodology) read against the connectome on disk and against the arithmetic;
these were the two sections no audit had touched.
**Context:** the week's eight drift instances, all in the plan table, the abstract, §4.3, §4.5, §4.7, §7, §8,
§9 — i.e. **every one of them in a section that summarises or hedges a result.**

---

## 1. §3.1 verifies to the digit

Every substrate number the paper states, against `clfly.connectome.graph`'s own `stats()` on the FlyWire
v783 data:

| quantity | paper | loader | |
|---|---|---|---|
| neurons | 138,639 | **138,639** | ✓ |
| connections | 15,091,983 | **15,091,983** | ✓ |
| synapses | 54,492,922 | **54,492,922** | ✓ |
| inhibitory fraction | 40.0% | 0.399728 | ✓ |
| mean out-degree | 108.9 | 108.858 | ✓ (rounds) |
| max out-degree | 9,783 | **9,783** | ✓ |
| largest weakly connected component | 138,113 | **138,113** | ✓ |

**Seven for seven.** And §3.3's named circuit sizes resolve exactly as stated — `--circuit-size 800` gives
**d = 1307** and `--circuit-size 3000` gives **d = 3150** — with every annotation column at or near full
coverage on the extracted circuit. The one figure that is not reproduced is `cell_type` at "99.9%" against a
measured 100.00%, and that is not a contradiction: the paper's sentence is about the **hop-0 seeds**, not
about the circuit they expand into, which is a different object.

## 2. And §6's figures check out, including its own correction

§6 states four numbers and a derivation, and all four survive: the metric's seed spread reaching **1.38 as a
range** (with the note that an earlier version called it a standard deviation, already corrected in place),
moving **±0.04 under a 1e-15 relative change**, the replacement's precision gain of **~8× in standard error,
i.e. ~64× in seed count** (8² = 64), and the derivation's cost claim. Its formula is the one `analytic.py`
implements, and its validation claims — nine Monte Carlo configurations and finite differences to 1e-9 — are
the kind of statement that would have to be withdrawn loudly if wrong.

## 3. So where has the drift actually been?

Eight instances this week, by section:

| section | what it is | instances |
|---|---|---|
| the programme table | a status summary | 1 (+3 found earlier) |
| abstract, §1 | summaries of results | 2 |
| §4.3, §4.5, §4.7 | result narratives | 3 |
| §7 | a hedged limitation | 1 |
| §8 | a forward-looking list | 1 |
| §9 | a reproducibility table | 1 |
| **§3, §6** | **the substrate and the method** | **0** |

**Not one instance is in a section that describes what the substrate *is* or what the method *does*.** Every
one is in a section that *summarises, hedges or points at* a result. That is a sharper statement than the
direction rules the project has been carrying ("toward more open", then "sometimes toward more severe"), and
it is testable against the record rather than asserted: the descriptive sections are where the numbers come
from the data and the code, and the summary sections are where they are re-told — and a number that is re-told
can be re-told from the part of the record that is being argued about.

**And the only error this fire found was mine.** §4.3 said *"all three pre-registered clauses pass"* about a
four-clause design in which P2 failed — written hours earlier, against the completed grid, with the full
clause list in my context. It is recorded separately
(`docs/findings/2026-09-23-the-drift-recurred-in-my-own-summary.md`) because its lesson is the specific one:
**a summary of one's own experiment is the least-audited surface, because it reads as a restatement rather
than as a claim.** This fire's own evidence is that the two sections which *describe* were exact and the one
sentence which *summarised* was wrong.

## 4. What is left to check

Nothing in the paper's prose that a machine can check, and nothing in the corpus's structured surfaces
(`e97`). What remains is the residue this week has characterised three ways:

- **honest but unverified claims** — the "validated against Monte Carlo" and "finite differences to 1e-9"
  statements in §6, whose evidence is a finding rather than a run here;
- **statuses nothing depends on** — the class-IL row was the only one, and it is fixed;
- **summaries of experiments**, which is where all eight instances live and where the only defence is the
  discipline of enumerating the clause list rather than the interesting clauses.

The project's audit programme has therefore reached its natural end for this substrate: it has gone from
"re-derive the table" through "re-derive the tables' inputs" to "the tables are the risk and the descriptions
are not", and the last two unread sections confirm the boundary.
