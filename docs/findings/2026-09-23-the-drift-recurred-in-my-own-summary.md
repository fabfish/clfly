# The drift recurred within hours, in my own summary, written against a complete record

**Date:** 2026-09-23
**Where:** `docs/paper/clfly-v1.md` §4.3, a paragraph written **earlier the same day** against the completed
60-of-60 grid — i.e. with every clause's outcome on screen.
**Context:** the week's audits — the programme table, the abstract, the `e86` range, the denominators,
`e8c`, the status word, §7, §9, the propagation pass. Six of them found drift toward more open; the seventh
found it toward more severe. This is the eighth, it is mine, and it is the opposite of both.

---

## 1. What the sentence said, and what the record said

I wrote:

> **All three pre-registered clauses pass**: the partial is positive at every size, **9 of 9** per-seed
> partials are positive, and no cell's removal flips any of them.

The grid was pre-registered against **four** clauses, and I had reported all four one commit earlier:

| clause | outcome, from my own commit message |
|---|---|
| P1 partial > 0 at every size | PASS |
| **P2 raw spread beats raw concentration at every size** | **FAIL** |
| P3 partial ≥ +0.5 at d = 1307 | PASS |
| P4 ≥ 7 of 9 per-seed partials positive | PASS (**9 of 9**) |

So "all three" both **dropped a clause** and **miscounted the set**: I summarised the three that supported
the claim and silently omitted the one that failed, then wrote a total that matches the three I had in mind.
A reader of §4.3 alone would have concluded the grid's clauses all passed. Corrected to lead with the failure.

**And the direction is neither of the two this project had recorded.** It is not "toward more open" (the
paper looking less settled than the record) and not "toward more severe" (§7's pessimism): it is **toward a
cleaner result** — the failure removed by omission from the summary of its own experiment. That is the third
direction, and it is the one with a motive attached rather than a habit.

## 2. Why the guard that caught it was not designed to

**I found it while grepping for the string `P2` for an unrelated reason** — I was checking whether the paper
anywhere still claimed the raw form works everywhere. So the catch was incidental. But the failure is
mechanically detectable, and the check is one line of writing discipline rather than of code:

> **A sentence that says "all *N* clauses pass" must enumerate the *N* and show that *N* is the number of
> clauses.** Here "three" versus four enumerated is the whole detection.

The instrument that would have caught it by design is the one already in place and unread: **the report
prints every clause including the failures, in one block, in the order they were pre-registered** — `P1 … PASS
/ P2 … FAIL / P3 … PASS / P4 … PASS`. I had that block in my context when I wrote the sentence. **The
information was not missing; the summary was written from the clauses that were interesting rather than from
the list.** That is exactly what `e85` found in the programme table — eight rows stale in the direction the
work had moved — and it is the same failure at the smallest possible scale: one sentence, hours old, written by
the person who had spent the week auditing it.

## 3. What this says about the week's audit programme

The eight instances now on record, by direction:

| direction | instances |
|---|---|
| toward more open | the programme table's eight rows; the abstract's figures; `side` "never been run" (×2); `e8c`'s sweep; the class-IL status; the `e86` range |
| toward more severe | §7's draw-sd inflation |
| **toward a cleaner result** | **this one** |

**Two of the eight were mine and both were in text less than a day old.** The audits that found the other six
were all *reads* — a claim next to the claim it is about — and none of them was a scan. This instance adds the
one thing the others could not show: **that the drift is not a property of old documents.** It is what happens
whenever a summary is written from the part of the record that is being argued about, and the fresher the
document, the less likely anyone is to re-derive it.

`e97` established that every structured surface of this corpus is clean; the class-IL audit established that a
*status* nothing depends on gets read past; this establishes that a **summary of one's own experiment** is the
least-audited surface of all, because it reads as a restatement rather than as a claim.
