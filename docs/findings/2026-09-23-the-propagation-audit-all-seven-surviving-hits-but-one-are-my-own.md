# The propagation audit: seven of twelve corrected claims still appear, and six are this week's own correction notes

**Date:** 2026-09-23
**Method:** every claim corrected this week, searched across the whole paper with whitespace-insensitive
patterns (rule 22), and each surviving hit read in context rather than counted.
**Context:** the audits of this week — the abstract's figures, the programme table, the `e86` range, the
denominators, the `e8c` sweep, the status word, §7, §9.

---

## 1. The audit, and why "7 of 12 still present" is the wrong reading

| corrected claim | hits | verdict on reading |
|---|---|---|
| `21 of 25` | 1 | **intentional** — the corrective sentence naming the old value |
| `20 of 21` | 0 | — |
| `interpolated rather than measured` | 0 | — |
| `seven rate-network` | 1 | **intentional** — the corrected §9 text quotes the old count |
| `+0.063 to +0.250` | 0 | — |
| `0.701` | 2 | **intentional** — both inside the §4.7 correction, naming the unbacked value |
| `45–63` | 2 | **intentional** — both name it as withdrawn |
| `inflated several-fold` | 0 | — |
| `single-draw figure` | 3 | **2 intentional** (§7's correction quoting the old text) and **1 correct** — line 64's is about the ladder's `pool4`, whose 42.2σ *is* a single-draw figure and does overstate by 3.1× |
| `never been run` | 1 | **intentional** — §8's correction note |
| `confirmed four times` | 0 | — |
| `still running\|in flight` | 1 | **GENUINE STALENESS** — see §2 |

**So six of the seven are this week's own correction notes**, which have to quote the value they withdraw;
one is a phrase that is correct where it sits; and **one is a real survivor**. A count of surviving hits is
therefore *not* a measure of propagation — the correction notes inflate it — and it is not a measure of
safety either, since the one genuine item was a single hit among six harmless ones. **The audit's output has
to be read, which is the third time this week the answer has been that a scan is not a check.**

## 2. The one that survived

§4.7 said:

> the class-IL row is **still running** and was **never validatable**.

Both halves were false, and the paper contradicted itself in two places to say so: **line 115**, in the
contributions list, states **"+0.042 ± 0.009 = 4.60σ at class-incremental"**, and **line 940**, in §4.7's own
table forty lines below line 902, states **"+0.042 ± 0.009 (4.60σ), five of five replicates positive each"**.
And the artifact is on disk: `runs/e84_replay96_classIL_5reps.json`.

So this is the same shape as the `e86` status word and the C2b section: **a sentence that its own document
contradicts, in the direction of more open.** The task-IL row had been carefully updated to *"re-measured but
not restored"* with its fingerprint failure named, and the class-IL row beside it was left in the state it had
before the re-measurement run — which is what happens when one half of a sentence is edited and the other half
is read past.

Corrected: both rows now read *re-measured and not restored* with the same fingerprint caveat, and the
class-IL contrast is quoted where the status was.

## 3. What this week's propagation actually looks like

Setting the correction notes aside, **every claim corrected this week reached every surface it needed to**:
the abstract's figures, §1's contribution list, §4.3, §4.7, §5, §7, §8, §9, the programme table, and the
findings corpus. The one exception above had no upstream claim to propagate — it was a *status* that nothing
depended on, which is precisely why nothing caught it. **A number that a table depends on gets corrected; a
status that nothing depends on gets read past**, and that is the same conclusion the status-word audit reached
from the other direction.

**And one verification worth recording as a positive**: the abstract now carries the corrected figures
(`+33–34%`, `24 of 24`, `19 of 20`, the withdrawn `+45–63%` labelled as withdrawn) and none of the nine
withdrawn numbers this project has corrected this week — `21 of 25`, `20 of 21`, the bare `55%`, `0.701`,
`+0.250`, `1.1e-3`, `33–63`, `seven`, `confirmed four times` — survives in it in an asserting position.
