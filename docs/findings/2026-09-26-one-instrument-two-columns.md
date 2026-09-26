# One instrument, two columns: the audit's verdict moves to the means and the out-of-scope state closes

*2026-09-26 21:10. Runs: **none new** — `experiments/e230_rank_draw_census.py`'s verdict moved to its means column and
`e257` records what that finds (`runs/e230_rank_draw_census.json`, `runs/e257_audit_on_means.json`). Seconds.*

## 1. What changed

`e230` read each family's between-`rho` contrast from the **single-drawing** rho cells the record quotes. `e255` and
`e256` drew the whole `rho` grid at both sizes, so the ladder families — the ones the mechanism readings are made of —
have **no single-drawing rho group left**: the as-read column went undefined for them, they left the table, and the
audit **silently absorbed an unresolvable family for a session** (cs 800 `alloy1`, whose 19:20 un-declaration was
bookkeeping rather than a resolution — `e257` re-read the same families on the means and found it at a ratio of 0.48).

So, as of this fire:

- **the verdict is the means column** — the ratio of the largest to the smallest rho-group mean against the family's own
  scatter at `rho` 0.9;
- **the as-read column is printed and no longer judged**, kept as a diagnostic and as a record of what the corpus once
  supported;
- **a family with fewer than two rhos owes no verdict** rather than being skipped silently, and the report states the
  audit's reach: **11 of the 42 families**, the other 31 being the size-ladder cells and the swap rungs;
- **the declarations are re-derived on the means**: cs 800 `alloy1` (**7.84** against its own **16.44** scatter, a ratio
  of **0.48**), cs 300 `swap0.5` (8.10 against 8.77) and cs 300 `swap2` (5.65 against 7.77);
- **the exit code** is the families unresolvable on the means and not declared — currently **0**, with three declared.

## 2. Why folding them into one instrument is the point

The two columns living in two modules is exactly how a verdict went missing. With one instrument:

    RESOLVABLE        the means contrast beats the family's own scatter
    NOT RESOLVABLE    it does not -- and if it is not declared, the exit code says so
    NO CONTRAST       fewer than two rhos: no verdict is owed, and the reach is stated

**There is no fourth state.** The `OUT OF SCOPE` category that absorbed cs 800 `alloy1` came from a column that could be
emptied by *drawing the corpus* — an instrument whose subject is a property of the record's design rather than of the
substrate will lose that subject as the record improves, and a verdict must not be able to leave the table with it. On
the means column every family with two or more rhos is judged, whatever the corpus does to its drawing counts.

## 3. What it changes, and one honest wrinkle in the ledger

**For the record**: the family that was unresolvable, then un-declared, then re-found is now *declared* on the reading
that found it, and the audit says so in a column a reader can check — which is the difference between a declaration and
a disappearance. The table also carries the family's own scatter beside both columns, so `alloy1`'s 16.44× at cs 800
and the 7.84× contrast that fails it are visible in the same row.

**The wrinkle**: this instrument's verdict has now moved **three times in one session** — as-read, declared-as-read,
out-of-scope, means — and each move was forced by the corpus rather than by a mistake in the arithmetic. That is a
statement about how thin the original corpus was: an audit built on single-drawing cells was asking its question of
cells that were themselves draws, and the answer it gave changed as soon as they were drawn again. The means reading is
the first form of it that cannot be emptied by more data.

## 4. What it cannot do

The fold does **not** widen the reach: **31 of the 42 families carry a single rho group**, so no column can judge them,
and the other 11 are all the audit will ever speak for under this design — its reach is 26% of the corpus and the
report now says so instead of leaving it to be inferred from a table that quietly omitted rows. The means contrast is
still compared against a scatter measured **at `rho` 0.9 only**, so a family that scatters more at another `rho` can
read resolvable; "means" are means over drawings that may straddle a code epoch (`e227`); and the three declarations
are conventions — a ratio of 0.92 fails a bar of 1, and nothing here tests whether a ratio of 0.92 and one of 0.48 are
the same kind of failure.
