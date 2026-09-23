
---

## 4. Outcome, against the clauses as written

**All four predictions hold and the falsifier did not fire.** Block minus matched random is **+0.0042**
(0.27 sigma, same direction as the other two configurations); **block minus diagonal falls from +0.0396 to
+0.0021, a 95% reduction**, against the circuit route's 58%; and it is 0.14 sigma, so nothing resolves.
**P4, the discriminator, holds: both routes shrink the gap, by 58% and by 95%, via two different
mechanisms** with the circuit, partition, entry count and batch count held fixed in one of them. So the
estimation-noise account now has **two independent confirmations in direction**, and the ordering is the
one it wants: largest gap where the estimation problem is hardest, smaller where the estimate is cheaper,
nearly zero where the target is simplest.

**And the run produced a third result**: `naive` minus diagonal is **+0.0521 at 2.47 sigma** in the baseline
configuration, **+0.0104 at 0.25 sigma** at cs = 300 and **-0.0063 at 0.46 sigma** at 2 classes, so section
4.7's "2.6 sigma advantage" over naive at lambda = 0.003 is real in **one of three** configurations and the
paper states it as if it were the lambda = 0.003 result. Full reading:
`docs/findings/2026-09-23-the-lower-rank-task-family.md`.

**The strongest competing explanation, recorded because nothing here addresses it:** `--classes 2` also
makes the benchmark **easier** (naive's forgetting falls +0.0729 to +0.0167 and every arm's accuracy rises
to ~0.97), so "an easier benchmark compresses all the gaps" predicts exactly what was observed.

> **A note on the tool: `pathlib.write_text` on this machine defaults to GBK, and the sigma symbol is not
> in it.** That is how this appendix first failed to write. Every doc-editing script in this repository
> should pass `encoding="utf-8"` explicitly; one that does not will succeed for a while and then fail on
> the first document containing a character outside the local code page.
