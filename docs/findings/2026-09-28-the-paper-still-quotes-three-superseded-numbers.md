# The paper still quotes three numbers a later finding superseded — and its own number audit cannot see them

*2026-09-28 19:35. Runs: **none new** — `experiments/e268_paper_supersession_audit.py` checks a hand-made registry of
supersessions against `docs/paper/clfly-v1.md` and against the findings that carry the replacements, writing
`runs/e268_paper_supersession_audit.json`. Seconds. **Three corrections were applied to the paper in the same fire.***

## 1. The item: provenance is not currency

The paper is machine-audited twice over. `e97` asks whether every `runs/` file it names exists, and `e192` asks
whether a number it states, **in a sentence that cites a finding**, is a number that finding contains. Both are
checks of **provenance** — where a number came from — and both pass while a claim is dead: a superseded number is
still supported by the finding its sentence cites. The finding that *withdrew* it is a later one, and nothing in the
record relates the two.

    a provenance audit cannot see supersession: it checks where a number came from, not whether it still stands

So this unit closes the gap the only way it can be closed — **with a registry**. Which numbers have been superseded is
not a property of the text but a fact about the programme, so the registry is hand-made (three entries, each a phrase
the paper carries, the finding that superseded it, and the replacement). Everything after that is mechanical: is the
phrase still in the paper, is there a correction note beside it, does the superseding finding exist, and does the
replacement appear inside it.

## 2. What the audit found

| phrase in the paper | superseded by | replaced by |
|---|---|---|
| `3.34× at cs 800 over five drawings` | `e247` (count-matched: **1.64×**), and `e252` excludes that cell from the declared domain | **1.64×** |
| `14.77× at 0.99` | `e251`: the seed-0 drawing's arithmetic, two other drawings at 2.22×, three pooled at **2.91×** | **2.91×** |
| `5.53× at 0.98` | `e253`: a second drawing at 0.98 reads **1.24×**, as does the one at 0.95 | **1.24×** |

**All three were still in the paper with no note beside them**, while the one withdrawn statement the paper *does*
carry (`7.68× to 25.25×`, withdrawn by `e253` at 18:20) shows it has the idiom and had used it twice. So the gap is
not that the paper never corrects itself; it is that corrections were applied where a **finding's status cell** was
being written and not where the paper was — and nothing checks the second.

**Q2 is the sharp one, and it is why the paper's own audit is green.** Each of the three phrases sits in a sentence
whose citation is on disk, so `e192` pairs the number with the finding that produced it and passes. The registry is
therefore not a better `e192`; it is a check of a different quantity.

## 3. The registered claims (Q1-Q3)

| claim | measured |
|---|---|
| **Q1** | 3 of the registry's 3 phrases were in the paper with no correction beside them — the falsifier fires *after* the fix, which is its signature |
| **Q2** | all 3 sit in a sentence whose finding is on disk, so a provenance audit passes them while they are dead |
| **Q3** | all 3 replacements are present in the finding that superseded them, so the fix is a substitution and not a deletion |

**And the paper was corrected in the same fire.** Each phrase now carries a `CORRECTED 2026-09-28` clause naming the
replacement and the finding path that holds it, in the paper's own idiom. Re-running the module reports **0 stale of
3**, and Q1's falsifier firing is exactly the signal that the fix landed — the check is live and will fire again on
the next superseded number.

**One defect fell out on the way.** The module's first version crashed when it printed a window of the paper: the
console's GBK codec cannot encode the double acute in `Erdős–Rényi`, so stdout is now pinned to UTF-8 with
replacement. The audit's own output quotes the document it audits, so it inherits the document's encoding — a
reminder that a check which prints its evidence has to be able to print it.

## 4. What it cannot do

It cannot find a supersession nobody registered, so a withdrawal that was never written down is invisible here — the
same limit as `e254`'s census of quoted figures, and for the same reason. The registry names **phrases** rather than
semantic claims, so a paraphrase of a superseded number is invisible, and a replacement is checked for presence and
not for meaning. The three entries are the ones this session's audits moved and for which a later finding stated a
replacement, which is a work list and not a census. And nothing here decides whether a sentence should be edited or
deleted — that is a judgement about the sentence, not about the numbers in it.
