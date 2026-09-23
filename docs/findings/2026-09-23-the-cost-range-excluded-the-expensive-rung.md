# The cost range excluded the expensive rung, and the excluded one was the run that was still going

**Date:** 2026-09-23
**Method:** the per-(arm × replicate) cost recomputed from the four completed `e10` rung runs' own `timing_s`
and recorded arm-replicate counts.
**Context:** the plan's C2b cost sentence and `docs/findings/2026-09-22-network-variance-is-learner-variability.md`
§5, which between them set the rung question's price at 0.2–6 hours; and last fire's finding that cost figures
need their environment, where this range had been mis-attributed to §4.7 — **the paper contains no timing in
hours at all**.

---

## 1. The measurement

Each `e10_rung_*.json` records its own `timing_s` and its `replicates`, and every one of the four completed
all three arms at three replicates, so the cost per (arm × replicate) is arithmetic:

| rung | `timing_s` | arm-replicates | **minutes per arm-replicate** |
|---|---|---|---|
| `ito_lee_hemilineage` | 2,763 | 9 | **5.12** |
| `cell_class` | 4,176 | 9 | 7.73 |
| `side` | 6,328 | 9 | **11.72** |
| `supertype` | 12,342 | 9 | **22.86** |

**The finding states "1.1–11.7 minutes per (arm × replicate) depending on the rung".** Its upper end is
`side`'s value alone, its lower end matches none of the four, and **`supertype` — the dearest rung, at more
than double the stated maximum — is excluded entirely.**

**And the exclusion has a known cause rather than a mystery.** The penalty-cost finding records that
`supertype` "consumed **3.5 CPU-hours** finishing two of three arms" — i.e. that run was still going when
the range was written, and its partial timing was not used. So the range was built from the runs that had
finished, which is a reasonable thing to do and produces a number that is wrong in the direction of the
question looking cheaper than it is.

## 2. The corrected range, with its arithmetic shown

The finding's §5 tables the replicates needed against an assumed cross-arm correlation (5 at 0.75, 16 at
0.00), and a rung comparison needs **two** arms. So, explicitly:

- cheapest: 2 arms × **5** replicates × **5.12** min = **51 min ≈ 0.9 h**
- dearest: 2 arms × **16** replicates × **22.86** min = **731 min ≈ 12.2 h**

**So the rung question costs 0.9–12 hours, not 0.2–6** — 4.4× more at the low end and 2.0× at the high end.
Both the plan's C2b sentence and the finding now say so, with the per-rung numbers beside them.

**The conclusion the sentence was drawing survives, and is worth restating because it was the argument**: at
0.03 resolution the question *is* answerable in a working session, whereas the 0.01 target genuinely is not
(50–118 hours). **One long session rather than a short one** — which is a different scheduling decision, and
the kind of thing a fourfold error at the low end changes.

## 3. Two provenance errors on the way, both mine and both the same shape

- **The figure was mis-attributed.** Last fire's finding listed "§4.7's 0.2–6 hours" among the paper's cost
  figures. The paper contains **no timing in hours at all** — `grep -n hours docs/paper/clfly-v1.md` returns
  nothing — and the figure is the plan's C2b plus the variance finding. Corrected there.
- **And the same figure had two homes with one of them now fixed and the other not**, which is last fire's
  own lesson: the plan and the finding both carried 0.2–6 hours, and I found the second only because the
  first sent me looking for its source. **The claim-subject pass would have found both in one grep for
  `0.2–6`**, and that pass is what last fire's finding prescribed and this fire ran — crudely, on numbered
  claims, where it found no disagreements at all. **Its one catch came from following a sentence to its
  source instead.**

## 4. What the pass did and did not do

Running the prescribed pass over seven load-bearing claims found **no figure that disagreed between the paper
and the plan**. It is a weak instrument as written — it counts figures near a subject rather than comparing
them, it cannot see tables, and it splits on `[.;]` — so "no disagreements" is close to "no information".
What actually found this fire's error was the older method: **take a claim, find its source, and read the
source's own numbers.** Three fires have now produced corrections that way, and nothing mechanical has
produced one.
