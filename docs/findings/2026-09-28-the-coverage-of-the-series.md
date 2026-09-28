# The coverage of the series: 9 of 368 sentences, and the residue is not typed

*2026-09-28 23:00. Runs: **none new** — `experiments/e282_the_coverage_of_the_series.py` reads the paper with the six
instruments' own registered phrases and patterns, writing `runs/e282_the_coverage_of_the_series.json`. Seconds.*

## 1. The item: a series that never said what fraction of the paper it reads

`e280` ended with the question it could not answer — one claim that enumerates its own population establishes that the
checker *can* pass, not how much of the paper it passes — and `e281` repeated it in its own closing line: the ledger
covers the instruments that exist, so a stale statement nobody built an instrument for is invisible. Nothing in the
series had ever measured the denominator side of its own work.

So this unit asks the paper directly. **A checkable sentence** is one carrying a digit or a quantifier word, because
those are the sentences an instrument could read. **A read sentence** is one containing a phrase or pattern one of
`e268`, `e270`, `e277`, `e278`, `e279`, `e280` registers. Both definitions are lexical and both are printed in the
module.

Three claims were registered before the run, all confirmatory: **C1** the series reads under half of the checkable
sentences; **C2** the unread residue is typed — fewer than a third of it carries a quantifier, so it is bare numbers
rather than universals; **C3** no instrument is silent, and the report prints how many sentences each one reads.

## 2. The census

**426 sentences; 368 of them checkable (86.4%); 9 read by some instrument (2.4%).** Of the 368, 343 carry a digit and
25 are quantifier-only. All nine read sentences carry a digit.

| instrument | registered form | sentences of the paper it reads |
|---|---|---|
| `e268` — the supersession registry | three phrases | 2 |
| `e270` — the 128-batch premise | one phrase | 2 |
| `e277` — the counts | three patterns | 6 |
| `e278` — the extremum over "on disk" | one phrase | 1 |
| `e279` — the universal over an epoch | one phrase | 1 |
| `e280` — the positive control | one phrase | 1 |

Thirteen matches over nine sentences, because a sentence can carry two forms. The unread checkable set is 359
sentences: **334 carry a digit, 250 carry a quantifier, 225 carry both, and not one carries neither.**

**C1 MET — 9 of 368, 2.4%, against a falsifier at half.** **C3 MET — every registered instrument reads at least one
sentence**, which is what makes the coverage attributable sentence by sentence rather than asserted.

**C2 FALSIFIER FIRED — 250 of 359, 69.6%, carry a quantifier, against a falsifier at a third.** The guess was
backwards. The series does not read the universals and leave the bare numbers; the unread set is *mostly* quantified
prose, and the reason is visible in the same census: the two legs overlap almost completely inside it (225 of the 250
quantified sentences also carry a digit), so "carries a quantifier" does not separate a sentence that names a
population from ordinary academic English. `every claim below cites the experiment that produced it` is a quantifier
and is not a denominator. The quantifier leg of the definition is also small — 25 sentences, 6.8% — and the paper is 86%
checkable because **it is a numbers paper**: nearly every sentence in it states a number, so nearly every sentence is
one an instrument *could* read.

## 3. What the census establishes

**The series' volume lives on the artifacts, not on the prose.** `e281`'s ledger counts 572 statements across the six
instruments — `e278` 262 arms, `e279` 167 artifacts, `e280` 132 pair-checkpoints. Against the paper those same six
instruments match nine sentences. Both numbers are right and they measure different things: an instrument's *reading*
is a population it enumerates in its own artifact, and its *reach into the prose* is the sentences whose numbers those
artifacts speak to. The audit series has been growing by populations while the paper's checkable sentences have stayed
at 368, so the coverage figure can be read as the series' own distance from the text it audits.

**And the definition should have been the instrument.** C2's falsifier is not a fact about the paper; it is a fact
about a lexical test. "Names a population" is what separates a checkable sentence from prose — that is the whole
lesson of `e278` and `e279`, where a sentence became checkable exactly when it named its enumerator — and a list of
nine English quantifiers is a poor proxy for it. The census shows the two legs behaving differently (digit 343,
quantifier-only 25) and the residue carrying both, which is the measurement C2 was supposed to make and did not.

## 4. What it cannot do

**The sentence split is the module's** — a period, colon or semicolon followed by a space and a capital — so a claim
spanning two sentences is read as two, a heading is counted as a sentence, and a continuation in lower case stays
inside the previous sentence. **"Checkable" is lexical**: a number written as a word is invisible and a digit inside a
filename counts as one, which is why the paper reads as 86% checkable. **A phrase match says a sentence is read, not
that the instrument's claim about it is the same claim** — `e277`'s patterns will match a counterexample sentence as
readily as the sentence it was built for. **The paper's tables are counted as sentences and not as cells**, so the
numbers in them are under-counted. **And nothing here reads `docs/research_plan.md` or `docs/findings/`**, which carry
their own checkable statements; the coverage measured is the coverage of the paper.
