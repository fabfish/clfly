# The correction ledger: six instruments, 572 statements, and the one item the series had left open

*2026-09-29 02:40. Runs: **none new** — `experiments/e281_the_correction_ledger.py` runs every instrument of the audit
series again and reads the ledger off them, writing `runs/e281_the_correction_ledger.json`. Seconds.*

## 1. The item: a series that reports findings without a ledger

Six fires have aimed instruments at the paper: `e268` (superseded numbers, by registry), `e270` (an existence premise,
by scan), `e277` (counts, by pattern), `e278` (an extremum over a population named in prose), `e279` (a universal over
an epoch) and `e280` (the positive control). Each unit ended with a correction applied to the paper — **except one, and
nobody had checked which.** That is the same defect the series audits, turned on the series: a claim whose scope is not
stated, here the scope of its own outstanding work.

So this unit runs every instrument again and reads the ledger off the instruments themselves: how many statements each
reads, whether the paper's statement is **still uncorrected**, and whether a correction clause naming the instrument is
on the page.

## 2. The ledger, before and after this fire

| instrument | reads | stale, as found | corrected |
|---|---|---|---|
| `e268` — the supersession registry | 3 | 0 | yes |
| `e270` — the 128-batch premise | 1 | 0 | yes |
| **`e277` — the counts over grown denominators** | **7** | **4** | **no** |
| `e278` — the extremum over "on disk" | 262 | 0 | yes |
| `e279` — the universal over an epoch | 167 | 0 | yes |
| `e280` — the positive control | 132 | 0 | — |

**C1 MET — six of six instruments ran, reading 572 statements in all.** **C2 MET — and the outstanding work is
bounded and named: exactly one instrument was still stale, `e277`**, whose four mapped counts sit over denominators
that have grown while the paper's two sentences carry no scope. **C3 MET — no instrument read clean without a
correction**, so nothing in the series stopped flagging because the check weakened.

**Then the ledger's own item was closed in the same fire.** `e277`'s two sentences now carry scope clauses naming the
grown denominators (529 artifacts against 216, 161 rate-network runs against 25), and the ledger re-run reads **0
stale of 6** — the same shape as `e268`'s Q1 firing as the signature of its own fix.

## 3. What the ledger is for

**A series that reports findings without a ledger cannot tell its outstanding work from its finished work.** The
five stale statements this series found were each crisp and each real; what the series lacked was the one line that
says which of them the paper still says. That line is now an instrument, and it is the same instrument the series has
been applying to the paper — a claim is checkable exactly to the extent that it names its enumerator — turned on the
series' own output.

**And the ledger's numbers are modest in a way worth stating**: 572 statements read is not 572 claims checked — `e277`
reads seven counts, `e278` reads a population of 262 entries under one claim, `e279` a population of 167. The count
that matters is the one across instruments: **six units of work, five of them closed before this fire and one closed
by it.**

## 4. What it cannot do

**`stale` is each instrument's own criterion and they are not the same criterion** — a phrase with no note beside it
for `e268`, a premise unqualified for `e270`, a count over an old denominator for `e277`, a note naming the instrument
for `e278` and `e279` — so the ledger compares six questions rather than one, and the report prints each instrument's
own label for that reason. **`corrected` is a text search for a clause naming the instrument**, so a correction
phrased without its id counts as absent, and `e280`'s `True` is by construction since its claim never needed one.
**The ledger covers the instruments that exist**, so a stale statement nobody built an instrument for is invisible —
which is exactly the coverage question `e280` left open and this unit still does not answer. And the five corrections
are one statement each: nothing here checks that a correction clause is *right*, only that the sentence now carries
one.
