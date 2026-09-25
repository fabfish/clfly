# One quantity, two spellings, and the two readers did not know about each other

*2026-09-25. Census and check: `experiments/e205_duration_field_census.py` (exit code = violations, 0 today),
helper: `duration_seconds` in `clfly/bench/artifacts.py`, tests: `tests/test_e205_duration_field_census.py`.
Artifacts read: the 329 under `runs/` that carry a `config` dict, as of 22:38.*

> **CORRECTED AND EXTENDED 2026-09-25, later the same evening**: the vocabulary is **three** spellings, not two —
> the third is `summary = {"time_s": ...}`, one level down, written by the predictor analyses, and this finding's
> own check had printed it as an uncounted near-miss. See
> `docs/findings/2026-09-25-the-vocabulary-was-three-spellings-and-the-third-was-one-level-down.md`.

This is not a registered hypothesis with a draw in it: nothing here varies, so nothing here needs a null. It
is a census of the record's own vocabulary taken because **the last two evenings' defects were all of this
shape** — `e201`'s draw-field list was hand-written and had missed `rewire_seed`, `e160`'s environment
identity had the machine's own speed inside it, `e198` found 238 (artifact, draw) pairs that could not say
which draw they used. Each time the defect was one level below the thing last audited. The level this unit
audits is the **field name a duration is written under**, because every cost statement this project makes —
rule 49's prices, the "hours" columns in `e38`'s tables, the quotations in the plan — rests on reading one.

## 1. The census: one quantity, two spellings, split by instrument

Of the **329** artifacts `e103`'s loader can see, **311 carry a duration**, and every one of them carries it
under exactly one of two names:

| spelling | artifacts | hours | share | who writes it |
|---|---|---|---|---|
| `timing_s` | 298 | 129.8 | 86.7% | the trained runners, every one of them carrying `methods` |
| `timing.total_s` | 13 | 19.9 | 13.3% | the analytic line, none of them carrying `methods` |

The split is **not random and not partial**: no artifact carries both, and the 13 are
`e3_real`, `e3_analytic`, `e3_large`, `e3_seeds18`, `e3_ladder`, `e3_ladder_v2`, `e9_ladder_pilot_1seed`,
`e9_ladder_d1874`, `e13_control3_d952`, `e58_bases_18seeds_perseed`, `e79_ladder_d1874_perseed`,
`e181_ladder_d300_12seeds` and `e202_ladder_d300_12seeds_seed0-100` — i.e. **the analytic line and everything
the C2 ladder argument has ever been measured on**. Both spellings are the same measurement, `time.time() - t0`
taken at the end of `main`, so they are interchangeable and no reader ever needed to branch.

**And the blind half is the expensive half.** Ranked by recorded duration, **2 of the record's 10 longest
artifacts and 4 of its 13 longest are analytic** (`e9_ladder_d1874` at 5.64 h is second overall, behind
`e178_rung_side_cs300_144reps` at 7.39 h), against a median artifact of **11.7 minutes**. So a reader keying
on `timing_s` cannot see plain artifacts *and* the ones whose price is largest.

## 2. The exposure, measured rather than asserted

Three readers in this corpus consume a duration, and all three keyed on `timing_s`:
`e169`'s scope gate (`payload["timing_s"]`), `e190`'s cost line (`d.get("timing_s")`) and `e38`'s cost table
(`d.get("timing_s")`). Every one of them was blind to the 13.

**What that blindness actually cost, measured**: `e169`'s scope contains **150** artifacts under the new
keying and **150** under the old one — the fix admits **zero** artifacts, because the 13 fail `e169`'s other
two conditions anyway (a `methods` dict and a 25-key config). So the field name is *not* what excludes them,
and no verdict in the record moves. Same for `e190` and `e38`: their artifacts are trained runs and their
numbers are unchanged. **The honest verdict on the exposure is therefore: none of the corpus's current
answers depends on it.**

Three things make that a thin margin rather than a reason not to fix it:

- **the direction of the two readers' blindness is not symmetric.** A reader keying on `timing_s` misses 13
  artifacts; one keying on `timing.total_s` misses 298. A future analytic-only reader (a ladder-cost table,
  say) that copied the analytic line's own spelling would be blind to nearly the whole corpus, and nothing in
  the record would say so — the failure mode is silent by construction, since a missing duration reads as an
  artifact that recorded none.
- **the price of the ladder line was read by hand, twice.** The plan's rule-49 costs for `e181` (2653 s) and
  `e202` (1758.9 s) are transcribed from the nested field by a human, because no command in this repository
  prints it. Those two numbers differ by **1.5×** for the *same command*, and rule 49 exists precisely because
  a price is where a run's cost enters an argument. A number that only a human can read is a number no check
  can be wrong about.
- **`e169`'s own counts are stale in the record**, which is the same defect in a different coat: its plan row
  says *"the 129 run artifacts carrying a duration"*. The scope is 150 today and the corpus will keep growing,
  so the row now carries an in-place note; the honest general statement is that the row's numbers are *as of
  the run*, and the plan's own convention already prints that for several other rows.

## 3. Four run-like artifacts that record no duration at all

> **CORRECTED 2026-09-25, later the same evening**: the paragraph below named *three* runners and put two of the
> four gaps on `e136_geometry_persistence.py`, and both are wrong — that module **reads** the two `barrier_r*`
> grids and defines three flags. `e205` now derives each gap's writer from `e172`'s parser registry and counts a
> disagreement as a violation, and the derived writers are `e122_path_geometry.py` (28 of 29 keys) and
> `e124_barrier_distribution.py` (30 of 31, 32 of 33, 32 of 33). **Two** runners had no clock, not three, and
> both now write `timing_s` — verified by two real runs. All four also carry the same key their own parser does not
define -- `save_theta`, which the runners assign into their own namespace at runtime -- which is why `e172`'s
> containment test names nobody for them. See
> `docs/findings/2026-09-25-the-four-artifacts-with-no-duration-are-also-the-four-no-parser-can-claim.md`.

Reading the spelling question forced a second one: *does every run say how long it took?* Of the **161**
run-like artifacts (a `methods` dict, or a parser-sized config), **4 record no duration under either
spelling**: `e122_path_geometry`, `e124_barrier_12seeds`, `e130_barrier_r32`, `e131_barrier_r1307`. They came
from **two** runners — `e122_path_geometry.py` and `e124_barrier_distribution.py` (the second wrote three of
them, at three read-outs) — and **neither imported `time`** [see the correction box above: this paragraph
first said three runners and named the module that reads two of the grids]. So this is not a misspelling but
an absence: the quantity was never computed.

The four artifacts are already written and their durations are unknowable now, so this finding **records the
gap and declares the four in the module** rather than counting them: a check that reports an unfixable historical
gap as a violation is a check that runs red forever, and this project's standing rule about checkers is that one
which reports everything gets ignored. [Correction: the `timing_s` write **was** then applied to both runners
and verified by two real runs, which the box above records.]

## 4. The fix, and the standing check that keeps it fixed

`duration_seconds(payload)` in `clfly/bench/artifacts.py` reads a duration under **either** spelling, and the
corpus's three readers now go through it. That is the whole repair, and it is the shape this project prefers:
one place where a quantity's storage is known, so a reader cannot be right about one line and silent about
another.

`e205` also becomes a **standing check**, in the same sense as `e103`, `e126`, `e192`: its exit code is the
number of violations, and three classes count toward it —

1. **an unknown spelling**: any top-level numeric key whose name begins `tim` or `dur` and is not in the
   declared vocabulary. **0 today.** This is the `e201` lesson as a guard: the vocabulary is declared in the
   module and printed on every run, so a third spelling cannot appear silently; and the class is honest about
   its own shape, since it matches the key's *name* — a duration stored as `total_seconds` would be missed,
   which is why the vocabulary is printed rather than merely asserted.
2. **an undeclared run-like artifact with no readable duration. 0 today**, with the four known ones declared
   beside their writer.
3. **a reader that bypasses the helper**: a source line that reads a raw duration key in a module that does
   not import `duration_seconds`. **0 today**, having been 3 before this unit. Its false-positive class is
   declared: a module re-reading a duration from a dict it built itself is a text-level READ, and is excluded
   by the module having imported the helper rather than by inspecting the receiver, because a text check
   cannot follow dataflow.

The rule this implies, stated as an instruction rather than as a fact about this corpus — **a quantity that
two instruments record under two names has two sets of readers, and neither knows about the other; the repair
is one function, and the check is that the vocabulary is declared** — is the fourth time this week a defect
has been one level below the last audit (`e160`'s environment, `e201`'s field list, `e198`'s draws, this), and
the first time the record's own *storage* rather than its *sampling* was the level.

## 5. What this cannot do

- It reads `runs/*.json` through `e103`'s loader, so a file with no `config` dict is invisible to it — and to
  `e198` and `e201` as well. The census is therefore of the loader's view, not of the directory.
- The source check is text: a module that obtained a duration some third way is invisible to it, and a raw-key
  read inside a module that also imports the helper is deliberately not counted.
- **It checks that the quantity is readable, not that it means what a sentence about it says.** A reader that
  prints `e10`'s `timing_s` as "the cost of the side rung" would pass this check and still be wrong; the only
  thing standing behind that reading is the convention that every runner writes the same expression at the end
  of `main`, which `e205` verifies for the 11 write sites it lists and cannot verify for their semantics.
- **It says nothing about which duration is the right denominator for a price.** `e202` versus `e181` differ
  1.5× for one command, which is a machine-load question (`e38`'s environment band) and not a field-name one.
