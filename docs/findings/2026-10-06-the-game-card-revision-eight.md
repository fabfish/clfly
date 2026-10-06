# The game card at revision 8: the ledger clause, and which of the two arms' effects is there at all

*2026-10-06. `experiments/e445_the_game_card_revision_eight.py` adds one clause to the card and checks every other field
rather than quoting it. `e434` wrote revision 7, the **parameters** clause. Since then `e437` to `e444` have driven the
card's own world **four times** -- as-built, under the rotated order, with the environment redrawn and with the decoder
redrawn -- and what those four rolls say together had never been written into the card, though `e438` fired a claim on
exactly that (*a card that says `the buffer's gain` should say which arm it means*) and `e444` closed by reading all four
at once. Five claims, registered before this unit's pass over the four rolls.*

## 1. The clause

| roll | what moved | the buffer over `naive` | sigma | margin | the anchor over `naive` | sigma | its newest task | sigma |
|---|---|---|---|---|---|---|---|---|
| as-built | nothing | +0.1594 | **11.97** | **+0.3500** | -0.0302 | 1.77 | **-0.1177** | 3.71 |
| rotated | the order | +0.2080 | **13.51** | **+0.4240** | +0.0229 | 1.21 | **-0.0906** | 3.56 |
| environment redrawn | `--loop-seed 1` | +0.1757 | **11.66** | **+0.3677** | +0.0198 | 1.30 | **-0.0552** | 2.57 |
| decoder redrawn | `--readout-seed 1` | +0.1503 | **7.66** | **+0.3281** | -0.0111 | 0.59 | **-0.0615** | 2.62 |

**`ledger`, the clause revision 8 writes**, over the four rolls of the card's own world: the buffer is `replay` and the
anchor is `ewc-block`; the buffer's mean diagonal over the baseline is **+0.1503** to **+0.2080**, at least **7.66**
sigma, with first-over-last margins **0.3281** to **0.4240**; the anchor's is **-0.0302** to **+0.0229**, at most
**1.77** sigma, with newest-task costs **-0.1177** to **-0.0552** at least **2.57** sigma.

| claim | measured | verdict |
|---|---|---|
| BW1 the seventh revision is carried where it is not rewritten | **21** fields equal, the revision now **8** | **MET** |
| BW2 and the clause's buffer half is the four rolls' | +0.1503 to +0.2080 at least 7.66 sigma, margins 0.3500, 0.4240, 0.3677, 0.3281 | **MET** |
| BW3 and its anchor half is the four rolls' too | -0.0302 to +0.0229 at most 1.77 sigma, newest task -0.1177 to -0.0552 at least 2.57 sigma | **MET** |
| BW4 and the clause's reading holds on every one of the four | the seven sigmas above | **MET** |
| BW5 and the clause names the arms and the rolls it was measured on | `replay`, `ewc-block`, four artifacts, four rolls, margins 0.3281 to 0.4240 | **MET** |

## 2. What the clause says

**The card now carries the one thing this line has measured on its own world that survives everything it has done to
it, and the one thing about the anchor that is there at all.** The buffer's standing resolves on all four rolls at
**7.66** to **13.51** sigma with the same sign and moves **0.0577** across them; the anchor's resolves on **none** of
them, at **0.59** to **1.77** sigma, spanning **0.0531** and changing sign; and the anchor's newest-task cost resolves
on **all four** at **2.57** to **3.71** sigma, negative every time. Read beside the card's own `order` clause -- which
says the position effect is the sequence's -- a reader can take away the sentence this line has spent eight units on:
**the buffer's ledger is the benchmark's, the anchor's whole-diagonal effect is not there, and what the anchor has is a
price at the newest task.**

**And the card's own world is now four rolls deep rather than one.** `e393` redrew the world four times and wrote that
every published number is conditional on one world; the four rolls here are the card's own world under three
manipulations and the clause carries their **range** rather than a point, so a reader who wants one number gets the
range and a reader who wants to know whether it is one draw's gets the four sigmas. The card's `world` clause still
carries the older reading's `worlds_measured: 6` and its span, and the two clauses are about different things: that one
is about the body's reading across worlds, this one about the ledger across manipulations.

**And the clause is scoped to what it was measured on, which is what `e438`'s firing asked for.** It names `replay` as
the buffer and `ewc-block` as the anchor, and it is the first place in the card where a sentence about *the buffer*
names an arm; the `penalty` clause named `ewc-block` and the `parameters` clause named four arms, but neither said which
arm a phrase like *the buffer's gain* refers to. So the mis-reading `e438`'s falsifier was fired on -- reading its
three-position ledger as the trade of *the arm that anchors* rather than of *the arm that stored* -- is now closed by
the card rather than by a reader's care.

**And every number in the clause is recomputed rather than quoted.** BW2 and BW3 each take the four rolls' raw
artifacts, recompute the paired contrasts from the replicate lists, and compare to a thousandth of a point; BW4 reads
the recomputation's own sigmas against the two-sigma bar. So a revision that moves the clause without moving the
artifacts fails, which is the property the corpus's later revisions need and which `e434`'s BW-style checks established
for the parameters clause.

## 3. What it cannot settle

- **Four rolls**: four points and not a distribution, so the ranges the clause carries are four rolls' own and not
  intervals, and the **0.0577** the buffer's standing moves across them is not a standard error.
- **And one world's card**: the four rolls are the card's own world under three manipulations, so the clause says
  nothing about the other five worlds the `world` clause measured or about the other five permutations of the suite.
- **And a clause is not a result**: BW1 shows revision 7 survives into revision 8 and not that revision 7 was right, and
  BW2 and BW3 show the clause agrees with the four rolls and not that the four rolls should be believed.
- **And one anchor**: `ewc-block-rand` is on two of the four rolls, so the clause's anchor half is one arm's, and
  `e439`'s **0.0063** by which the two anchors differed is not carried here.
