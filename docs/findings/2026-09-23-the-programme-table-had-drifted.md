# E85 — the programme table had drifted on eight rows, and the paper's limitations section had a **null that is really a resolved disadvantage**

**Date:** 2026-09-23
**Artifact:** `docs/research_plan.md` §"Experimental programme", `docs/paper/clfly-v1.md`
**Context:** `2026-09-22-e5-artifact-is-live.md` (e43, the project's first stale-table lesson), `2026-09-23-cell-type-is-not-a-null.md` (e66), every finding referenced below

---

## 1. Why a table audit is a unit of work

The programme table is the plan's operational core: it is where "what is open" lives, and it is the first
thing a reader — or a later fire — consults before deciding what to run. Its rows are written **when a
script is launched** and are supposed to be rewritten when it lands.

Eight rows had not been. The project already has this failure on record once, in the other direction:
`e41` found that a *finding's table* did not reproduce from the artifact it cited, and `e43` resolved it by
showing the artifact was live and the table was stale. The lesson was recorded as being about findings.
**The same drift had accumulated in the plan**, which nothing was checking, because the plan is not a
result and so no experiment ever cited it.

## 2. What the audit found

Each row was checked against the artifacts and findings on disk.

**Four rows reported work as unfinished that was finished:**

| row | said | is |
|---|---|---|
| `e3 --ladder × d = 1874` | *in flight* | **done** — `runs/e9_ladder_d1874.json` exists and produced a finding; `e79` later re-ran it with per-seed storage and `e57 --artifact` analysed both ladders (**8 of 8 rungs unanimous over 12/12 seeds**) |
| `e3 --ladder` (re-run) | *in flight* | **done** — `runs/e3_ladder_v2.json` exists and `e57` analysed it |
| `e2 --circuit-size 700` | *in flight*, prediction pre-registered | **done** — `runs/e26_size700.json` exists and the pre-registered prediction **failed**, which is what closed the geometry reading |
| `e3 --control-draws K` | "the K=3/K=4 runs are queued" | **K = 3 exists** (`runs/e13_control3_d952.json`, d = 952, 3 seeds, written up in `2026-09-22-e13-averaged-controls.md`); **K = 4 was never run** and nothing in the record says it needs to be |

**One row was duplicated**, identically titled and contradicting itself: `e66_named_bases_seed_robustness.py`
appeared twice, once as *done* (with the `cell_type` reversal it found) and once as *queued behind `e58`*.
The stale copy is deleted; the live one is kept.

**Four rows were marked done but summarised a number the project has since overturned:**

| row | stale summary | current |
|---|---|---|
| `e2_topology_gap.py` | "mechanism refuted at 32.7σ" | **two numbers**: −28.85σ about the cs = 800 graphs, **2.2σ about the rewiring rule** after `e65`'s six-draw sweep; the 32.7σ was the unpaired, single-realization figure |
| `e3_basis_selection.py` | "7 of 8 rungs resolve; 2.8–7.9σ once the control-draw component is included" | **both families measured on one footing**: five named rungs at 18.1 / 12.1 / 26.1 / 13.3 / 3.8σ about the rule, eight ladder rungs at 2.6–13.7σ, and the named family **stronger** rather than an order of magnitude behind |
| `e12_control_spread.py` | "draw sd is ~1.1e-3 coarse, ~4e-5 fine; coarse-rung σ are provisional" | that reading is **refuted** (`e67`: `side` at 2.16e-4, 4.8× below the model), the mechanism is **`projection_pressure` at r² = 0.828** (`e81`), and every σ now takes the draw component from a per-rung measurement |
| `e38_variance_budget.py` | "it is learner seed-to-seed variability, not measurement" | **the emphasis was backwards** (`e71`): the evaluation floor is **55%** of the `naive` arm's variance, the learner 38–45% of the arm and ≥54% of the contrast — so the conclusion (seeds bind) holds for the *opposite* stated reason |

One further passage, in the C2b section rather than the table, still described `e60` as *running*
`side` at sixteen replicates "to restate the cross-rung contrast". `e60` finished and `e76` restated it:
**the contrast is a null on both metrics** (0.88σ and 1.21σ), so the λ = 0.1 rung question is closed
rather than pending.

## 3. The pattern, which is the reason this is a finding and not housekeeping

All eight were stale in the same direction: **they made the project's position look more open, or its
numbers stronger, than the artifacts support.** That is the same direction as the six earlier failures
this project has on record — `e41`'s stale table, `e54`'s assumed config key, `e62`'s missing artifact,
`e63`'s unpaired σ, `e46`'s three seeds, `e84`'s failed fingerprint — and the mechanism is the same
one each time:

> a document written from the state of the work at the time it was written, and never re-derived from
> the artifacts, drifts in whichever direction the work moved.

Here it drifted toward "more unfinished". In the four summary rows it drifted toward "larger effect".

**The cheap guard, and the one this fire applied:** treat the programme table as a claim with an
artifact behind every row, and re-derive its status column from disk rather than from memory. The check
is mechanical — every row names either a `runs/*.json` or a finding, and both either exist or do not.
Two of the eight would have been caught by nothing else, because they were not wrong about a *result*:
the duplicate row and the "K=4 was never run" claim are statements about the project's own bookkeeping.

## 4. And the same audit applied to the paper, which found one scientific error

Rule 22's mechanism is not specific to the plan, so the check was run on the paper's number-bearing
sentences too — grepping for the figures recent fires have overturned. Five had not been updated, and one
of them was not a bookkeeping slip:

* **§7's limitations said the ladder "resolves the same 7 of 8 rungs with the same exception (`pool1`, the
  un-pooled `cell_type` partition — a fourth independent confirmation of that null)".** `e66` overturned
  that. `pool1` is **not a null**: its two arms co-move at ρ = 0.9987 across task draws, so the unpaired
  sem is 27× too large, and the rung is a **reliable disadvantage** — +0.000261 ± 0.0000129 = **20.3σ
  paired** at d = 1307 and **+0.00035 at 9.85σ, 12/12 signs** at d = 1874. So the paper's limitations
  section was asserting that a *disadvantage* had been independently confirmed as a *null*, four times
  over. This is the sharpest instance of the pattern in this audit and it is the one that would have been
  hardest to notice, because the sentence is a *limitation* — a reader is primed to take it as the
  conservative statement.
* **§5 said the predictor's count "holds: 13 of 13 at the estimated draw sd"** in the same paragraph that
  the pairing later supersedes. An arithmetic re-derivation cannot fix a denominator; the paragraph is now
  written in the order the project learned it.
* **§7 and the methodological-lessons list both used the *assumed* control-draw spread of ~1.1e-3.** `e67`
  refuted that figure — the ladder's own rungs measure 6.8e-5 to 9.6e-4 — and the mechanism is now known
  (`e81`). Both sentences now carry the measured range.
* **§4.6's reproduction check said "bit-for-bit"**, which rule 21 withdrew; it now says "to the last printed
  decimal", which is what an environment-scoped identity test can actually claim.
* **The retraction list's C1 entry gave the refutation at 32.7σ** without the rule-level figure. It now
  carries both: −28.85σ about the two graphs and **2.2σ about the rewiring rule**.

**The direction is the same as the table's, and worse.** Four of the five drifted toward a *larger* or
more comfortable claim, and the fifth — the limitations section — drifted toward *understating* the
project's own result by recording a resolved disadvantage as a null. A paper's limitations section is the
last place a reader expects an error, which is exactly why it is worth auditing.

## 5. Limits

- **This audit covers the programme table and one adjacent passage**, not the whole plan. The plan is
  ~1200 lines and much of it is prose that asserts numbers; a full pass against artifacts has not been
  done, and the same drift could exist elsewhere.
- **The four "stale summary" rows were corrected to the *current* reading, which is itself a moving
  target** — `e82`'s third circuit size is still running and will change what the `e81` row can say.
- **Nothing here re-derives a number.** Every correction cites the artifact or finding that already did,
  so the audit can be checked the same way it was performed: from disk.
