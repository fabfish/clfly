# The limitations section was more severe than the results, and that direction is the hard one

**Date:** 2026-09-23
**Method:** a read of the paper's §7 against §4.3's own corrected tables and against the runs' recorded timings.
**Context:** `docs/findings/2026-09-23-the-programme-table-had-drifted.md` (`e85`), which found the `pool1` error
in this same section, and the five audits since, all of which found drift **toward more open**.

---

## 1. §7 contradicted §4.3 about the same quantity, in the paper's own pages

§7's scale bullet read:

> Note that every coarse-rung σ in this paper, including `side`'s (4 groups), is a **single-draw** figure and
> is inflated **several-fold** by the control-draw component (§4.3, `e12`).

§4.3, fifteen hundred lines earlier and citing the same sources, reports the measured table and says of it:

> The "3–6× for coarse partitions" figure is wrong for every one of them: the real overstatements are
> **1.0–1.6×**.

Measured per rung: `side` **1.64×**, `cell_class` **1.35×**, `ito_lee_hemilineage` **1.01×**, `supertype`
**1.03×**, `cell_type` **1.02×** — each from its own control-draw run, so **none of the five is a single-draw
figure any more** and none is inflated several-fold. **"Several-fold" survives only for the granularity
ladder's rungs**, whose control draws move much further (`pool4`: **42.2σ → 13.7σ**, 3.1×).

So the correct statement is *two families with two correction factors*, and §7 was applying the ladder's
factor to the named rungs while calling all of them single-draw. Corrected in place.

## 2. The direction is the opposite of every other instance, and that is why it lasted

Each of the audits this project has run — the programme table's eight rows, the abstract's six figures, the
`side` "never been run" pair, the status word, the `e8c` sweep — found drift **toward more open**, i.e. the
project looking less settled than the record supports. **This one drifts the other way: §7 made a limitation
look more severe than the measurements do.**

That is the harder error to catch, for a reason worth stating plainly: **a limitations section is where a
reader expects the conservative statement, so it is the section least likely to be challenged, and it is the
section an author has the least incentive to re-derive.** Every audit in this record has started from a
result that looked *too strong*; this one had to start from a limitation that looked *too strict*, which no
prior check was pointed at. The direction rule this project has been carrying ("drift runs toward more
open") is therefore **false as a general law and true as a frequency**: six of seven instances, and the
exception is the one with the least scrutiny.

## 3. And a number that was right for a reason that cannot be

§7's next bullet said *"The exact oracle is O(d³), so a larger circuit costs **7×** more per run than
d = 1307."* The runs' own timings (`runs/e3_analytic.json`, `runs/e3_large.json`) give **8.3× per
basis-evaluation** — 121.5 s against 14.6 s — so the figure was roughly right.

**But O(d³) predicts (3150/1307)³ = 2.95×, so the reason given cannot produce the number.** The ratio is
measured and the *explanation* is decorative: several d³ operations per basis, plus whatever support 150
costs over 80, is not one scaling. Corrected to quote the measurement instead of the derivation — and worth
recording because a correct number with an incorrect derivation is exactly the kind of claim that survives
review and misleads the next person who tries to estimate a cost.

## 4. What this suggests for where to look next

§7 is 15,349 characters and 180 lines of hedged claims, and it has now produced two errors (the `pool1` null
and these two). The audits that found them were **reads against the results they cite**, not scans. Since
`e97` established that every *structured* surface of this corpus is clean — artifacts exist, configs agree,
no machine-checkable provenance gap — **the remaining value is in the hedged prose of the sections that a
reader trusts without checking**: limitations, reproducibility, and the "what we would do next" list whose
first item was already found stale. That is a small, specific, finite surface, and it is the one this
project has been walking past.
