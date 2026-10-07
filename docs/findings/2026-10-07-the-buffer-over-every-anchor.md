# The buffer over every anchor: the corpus's method contrast resolves at 8.27 to 15.33 sigma on all ten rolls of the card's world

*2026-10-07. `experiments/e453_the_buffer_over_every_anchor.py` reads the corpus's **other** headline across every
manipulation this line has driven. `e276` read `replay` against the penalty at **3.30** to **11.84** sigma on the state
read-out and the register has quoted it since. On the card's world the line has since driven **ten** rolls -- seven
carrying `naive`, `ewc-block` and `replay`, three carrying `naive`, `ewc-block-rand` and `replay` -- each moving one
thing: nothing, the order, the environment's draw, the decoder's draw, or the world's width. `e438` read the contrast at
**10.89** sigma as-built and each later unit read it inside its own roll; what the ten say **together** had not been
said. No training and no probe. Five claims, registered before this unit's pass over the ten rolls.*

## 1. The ten

| family | roll | what it moves | the buffer over the anchor | sigma | on forgetting |
|---|---|---|---|---|---|
| biological | as-built | nothing | **+0.1896** | **10.89** | -0.2370 |
| biological | rotated | the order | **+0.1851** | **10.03** | -0.2271 |
| biological | env redrawn | `--loop-seed 1` | **+0.1559** | **8.40** | -0.2344 |
| biological | decoder redrawn | `--readout-seed 1` | **+0.1615** | **8.27** | -0.2245 |
| biological | reversed | the order | **+0.1753** | **8.38** | -0.2240 |
| biological | wide, 16 | the width | **+0.1250** | **8.38** | -0.2115 |
| biological | narrow, 4 | the width | **+0.1483** | **10.12** | -0.2057 |
| matched-random | as-built | nothing | **+0.1958** | **15.33** | -0.2615 |
| matched-random | reversed | the order | **+0.1861** | **12.90** | -0.2448 |
| matched-random | narrow, 4 | the width | **+0.1382** | **9.70** | -0.1776 |

| claim | measured | verdict |
|---|---|---|
| CZ1 the ledger is carried | **10** rolls, **7** biological and **3** matched-random, at twenty replicates | **MET** |
| CZ2 and the buffer is ahead of the biological anchor on all seven | **+0.1250** to **+0.1896**, **8.27** to **10.89** sigma | **MET** |
| CZ3 and ahead of the matched-random anchor on all three | **+0.1382** to **+0.1958**, **9.70** to **15.33** sigma | **MET** |
| CZ4 and the smallest of the ten is well clear of the bar | the least sigma is **8.27** | **MET** |
| CZ5 and the size of the contrast is not the manipulation's | the span is **0.0708** | **MET** |

## 2. What the ten say together

**The card's world has one robust headline and it is the method contrast, not the basis one.** On every one of the ten
rolls the buffer's mean diagonal over its anchor is positive at **8.27** sigma or more, the weakest instance is
**8.27** -- four times the two-sigma bar, and far clear of the **3.30** that is `e276`'s weakest on the state read-out --
and the ten span **0.0708** across five manipulations while the **basis** contrast spans **0.36** to **0.64** sigma and
never resolves. Read with the card's `ledger` and `width` clauses, which carry the buffer's per-position ledger and the
anchors' absence at two widths, this is the sentence neither states: **on this world storing beats anchoring at every
order, both redraws and all three widths, and which basis anchors does not.**

**And the contrast's forgetting side is as uniform as its accuracy side.** All ten are negative, from **-0.1776** to
**-0.2615**, so the buffer is not merely more accurate than either anchor in each roll -- it also forgets less in each,
and the two currencies do not trade off anywhere in the ten.

**And the two manipulations that move the contrast most are the widths, in the direction `e450` measured.** The smallest
two of the ten are **+0.1250** at sixteen columns and **+0.1483** at four, against **+0.1896** at the card's own eight;
the anchors' own effects peak at eight as well (`e448`, `e449`), so the width moves the two arms' **advantage over each
other** less than it moves either arm's effect, and the span it leaves -- **0.0708** -- is what CA4's span of **0.10**
was registered to be able to contain. The four other manipulations move the contrast by between **0.0045** (rotated
against as-built) and **0.0301** (the environment's redraw).

**And the contrast is larger against the matched-random anchor than against the biological one, in the two rolls both
families have.** As-built the buffer is **+0.1896** over `ewc-block` and **+0.1958** over `ewc-block-rand`, and at four
columns **+0.1483** against **+0.1382**; reversed it is **+0.1753** against **+0.1861**. So the two pairs' difference of
**0.0062**, **0.0101** and **0.0108** is in the same range as the **0.0042** to **0.0108** the three pair units found
between the two anchors themselves -- the buffer is being compared against one arm with two names, as `e451` put it, and
the ten rolls therefore carry at most seven independent cells rather than ten.

## 3. What it cannot settle

- **Ten rolls of one world**: the card's own, so other worlds are not in the reading and neither are the corpus's other
  suites, where `e276` took its three configurations and its **3.30** to **11.84** range.
- **And one pair per roll**: each roll pairs the buffer against **one** anchor, so the two anchors are compared through
  the buffer and not directly; `e439`, `e447` and `e451` do that, and the three readings above are why these ten carry
  fewer independent cells than they have rows.
- **And one arm pair**: `naive` and an anchor, so the penalty's **strength** is not in it -- `e276` and `e320` found the
  strength stops mattering at the first notch -- and neither are the frozen controls.
- **And two same-seed runs**: each contrast pairs replicate against replicate by the runner's `seed0 + 100 * r` schedule,
  which is a same-seed pairing and not the same run, so each of the ten carries whatever separates two runs beyond their
  seeds.
