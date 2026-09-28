# "Every one of the 77 stored runs" was an epoch: 167 artifacts now, and an eighth outside the clause

*2026-09-29 01:40. Runs: **none new** — `experiments/e279_every_one_of_the_77.py` enumerates the population a paper
universal names and checks whose setting it describes, writing `runs/e279_every_one_of_the_77.json`. Seconds.*

## 1. The item: the count `e277` left unchecked, and it is not a count

`e277` extracted seven of the paper's counts and could map three to a corpus noun, naming the four it could not as the
audit's largest gap. One of them is a **universal about a configuration**:

> `e62` found that **every one of the 77 stored runs** used **16 stored stimuli per task and 16 replayed samples per
> step**

Both halves are enumerable — the population is every artifact carrying a `replay_per_task` or `replay_batch` field,
and the clause is what those fields say. **And the corpus has moved on by the paper's own account**: the same
paragraph names the pool-96 / per-step-8 configuration as the thing that replaced 16/16.

## 2. What the population says

| stored stimuli per task / replayed samples per step | artifacts |
|---|---|
| **16 / 16** — the sentence's clause | **144** |
| **96 / 8** | **14** |
| 16 / unrecorded | 7 |
| 96 / 16 | 1 |
| 96 / 48 | 1 |

**W1 MET — the population is 167 against the sentence's 77 (2.17×).** **W2 MET — and an eighth of it is outside the
clause**: 16 artifacts record a different setting and 7 more leave the batch unrecorded. **W3 MET — and the paper
names `pool-96` itself**: the universal and the configuration that superseded it sit in one paragraph and neither
notices the other.

## 3. What it means

**A universal about a configuration is a statement about the configurations that existed when it was written.** The
sentence reads as a fact about the line's replay method; it is a fact about an **epoch** of it, and the epoch ended
twenty words later in the same paragraph. The fix is the same one `e278` applied to an extremum — an **epoch rather
than a bigger count**: which runs, under which replay setting, at which date. The paper now carries that clause.

**And it closes the second of the four gaps `e277` named.** Two remain (`the 27 arms`, `every one of the 132
pair-checkpoints`), and they are of the same kind: a population named by a phrase whose enumerator is in another
document.

## 4. What it cannot do

**`stored runs` is the sentence's own phrase** and the module's enumeration — any artifact carrying either replay
field — is the one the words admit and not necessarily the author's; a stricter reading (only artifacts that trained a
replay arm) is plausible and would move W1, which is why the report prints the setting tally rather than only the
count. **The seven artifacts with an unrecorded batch** are counted outside the clause although they may have used 16,
so the eighth is an upper bound. And **nothing here says the sentence was wrong when it was written** — that is the
point of the unit, and the reason the correction is an epoch and not a number.
