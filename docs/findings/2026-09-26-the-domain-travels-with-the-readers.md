# The domain travels with the readers: one claim each, the same three `e252` names

*2026-09-26 22:40. Runs: **none new** — the declared domain moves into `experiments/domain_rule.py`, `e244`, `e246`
and `e247` each take a `--domain` flag that prints their claims twice, and `experiments/e260_domain_in_the_readers.py`
reads the three readers' own two readings (`runs/e260_domain_in_the_readers.json`). Seconds.*

## 1. The item: the queued half of `e252`

`e252` declared a domain — a cell is in when every family measured there scatters by at most `T = 4` across its own
drawings — and re-read every pooled claim inside it. The rule, though, lived in that one module while the three
readers it applies to knew nothing about it, and `e252`'s D4 kept firing for a structural reason rather than a
statistical one: **the moved list was computed in a module a reader's own report never mentions.** This line has
already paid for that shape once — `e230` folded away a second column because a verdict could leave the table when the
instrument's subject stopped applying to it — and the spread line's version of the hole is that a reader is pooled
over the whole corpus, so a cell that scatters silently demotes its verdict while the domain-restored reading stays
somewhere else. `domain_rule` now holds the rule, `e252` delegates to it, and each of the three readers takes
`--domain`: it prints its claims outside the domain and inside it, and writes `claims_domain` beside `claims`. **The
readers' exit codes are untouched**, so what a reader's status stands on is the same reading it stood on before.

## 2. What each reader's second reading does

| reader | claims | moved | outside the domain | inside it |
|---|---|---|---|---|
| `e244` | 3 (K1-K3) | **K1** | null band | **MET** |
| `e246` | 3 (N1-N3) | **N3** | FALSIFIER FIRED | **MET** |
| `e247` | 5 (R1-R5) | **R2** | null band | **MET** |

**3 of the 11 pooled claims move, exactly one per reader, and every one of them moves toward MET.** K2, K3, N1, N2,
R1, R3, R4 and R5 read the same inside the domain as outside. R1 is the interesting hold: `e255`'s six low-`rho`
groups are **inside** the domain, so the falsification `e251` caused survives the filter — the same asymmetry `e252`
recorded when it re-registered D3 as a share. And **no reader loses a claim**: 3 to 3, 3 to 3, 5 to 5, with the same
ids inside and outside, so the filter costs a reader cells and not claims. That is the property the fold is for — the
readers report the demotion and the restoration in one command instead of one of them quietly disappearing.

## 3. The registered claims (F1-F4, all MET)

| claim | what it says | measured |
|---|---|---|
| **F1** | no reader's claim leaves the table when the domain is applied | 3 to 3, 3 to 3, 5 to 5; no id appears or disappears |
| **F2** | the domain is not decorative for any of the three | `e244` `['K1']`, `e246` `['N3']`, `e247` `['R2']` |
| **F3** | the readers move what `e252` names, and only toward MET | readers `['K1', 'N3', 'R2']` = `e252`'s list; 3 of 11 claims, all to MET |
| **F4** | the flag is additive | each reader run twice: exit 0 to 0, identical `claims`, a domain reading written |

**F3 is the cross-instrument check.** The readers' moved set is computed from their own `judge` rows; `e252`'s is
computed by its own `verdicts` table over the same corpus; and the two lists are equal. On today's corpus the domain
is **13 cells in and 5 out** (`rho` 0.98 and 0.99 at cs 300, and `rho` 0.95 to 0.99 at cs 800).

## 4. One real defect the fold surfaced

`e247`'s report **crashed** — `TypeError: unsupported format string passed to NoneType.__format__` — on any corpus too
small for the covariate rank correlation to exist, because the two Spearman columns are `None` when there are fewer
than three groups and were formatted as floats. The live corpus always has enough groups, so the defect was invisible
until a test pointed the reader at a two-artifact directory; the columns now print `nan` like the spans do. A second
thing the module's tests caught is the import shape: the rule cannot import `e247` at module scope, because `e247`
imports `e246` and `e246` imports `e244` — the reader import is inside `corpus()` instead.

## 5. What it cannot do

**F1 to F3 are statements about today's corpus and are re-read on every run rather than pinned.** `e252` has watched
the moved list change twice as cells were drawn, and the same growth moves it again; a green F1 to F3 says the two
readings travel together, not that the list is fixed. `e246`'s CLI takes no `--runs`, so its half of F4 is always
checked against `runs/` under the working directory. F4 measures that the flag changes nothing a reader's exit code
stands on, which is the property that keeps a green gate meaningful — it is not a claim that the domain reading is the
right one. The fold makes **no claim stronger than `e252`'s**: it moves the same three verdicts to the same words. And
nothing here measures the substrate.
