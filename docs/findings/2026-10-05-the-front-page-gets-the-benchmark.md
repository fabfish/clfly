# The front page gets the closed-loop benchmark: every number in the section is one of the card's clauses

*2026-10-05. `experiments/e429_the_front_page_gets_the_benchmark.py` adds a section to `README.md` -- the front page
`e307` reads the scope blockquote of -- and reads it back against the card's artifact. The section is written once, by
hand, with the rest of this unit; the module reads it rather than rewriting it, so the gate never touches a source
file. Five claims, registered before this unit's pass over the README and the card.*

## 1. What the front page now says

| clause | number on the page | the card's own |
|---|---|---|
| the far-point cells | 12 | 12 |
| the far point's newest task cost | 12 | 12 |
| the oldest task's recovery at the far point | 0.2333 | 0.23333 |
| the newest task's loss at the far point | 0.1031 | 0.103125 |
| the near-point cells | 13 | 13 |
| the near point's newest task cost | 8 | 8 |
| the oldest task's recovery at the near point | 0.0750 | 0.075 |
| the oldest task's learning term | 0.0 | 0.0 |
| the newest task's retention term | 0.0 | 0.0 |
| the middle task's retention over its learning price | 3.99 | 3.9861 |
| the buffer's retention over the penalty's | 7.13 | 7.1282 |
| the two learning prices' gap | 0.0344 | 0.03437 |
| the arm-rolls of the order axis | 16 | 16 |
| the arm-rolls with the first position ahead | 16 | 16 |
| the reversal's largest cost | 0.0694 | 0.0694 |
| the reversal's smallest cost | 0.0028 | 0.0028 |
| the penalty arm-rolls worst in the middle | 9 | 9 |
| the frozen-body cells | 3 | 3 |
| the largest gain on a frozen body | 0.0017 | 0.00174 |
| the frozen bias's share of the buffer's gain | 0.27 | 0.2688 |
| the frozen bias's share of the buffer's cut | 0.27 | 0.2658 |

| claim | measured | verdict |
|---|---|---|
| BE1 the region is carried and names its source | **21** rows of a **21**-label vocabulary, the section naming the artifact and revision **6** | **MET** |
| BE2 and its trade rows are the card's | the **7** trade rows equal the card's | **MET** |
| BE3 and its order rows are the card's | the **5** order rows equal the card's | **MET** |
| BE4 and its controls rows are the card's | the **4** controls rows equal the card's | **MET** |
| BE5 and its terms rows are the card's, and its findings are on disk | the **5** terms rows equal the card's, **6** findings named and all present | **MET** |

## 2. What the section says

**The front page now names the second benchmark and holds it to the first one's discipline.** Until this unit a reader
reaching `README.md` learned about the anchored-Fisher question and the frozen connectome; the closed-loop benchmark --
the card `e409` to `e428` maintain by revision, with three arms, six worlds and a fixed task order -- was named nowhere
on the page. The section states what the closed-loop setting is, lists **21** of the card's numbers, and names the card
itself, this revision's finding, and the six findings behind the trade, the split, the penalty, the order and the
controls.

**And every number on the page is checked against the artifact that measured it.** The module parses the marked region,
requires every row's label to be one of its own vocabulary's, and compares each row with the card's value: a number the
card does not carry, or one disagreeing with it, turns the unit red. So a later card revision that moves a number
cannot leave the front page behind -- the pair of them is checked, not just the card.

**And the front page's existing text is untouched.** The section is an insertion; the scope blockquote at the top, which
`e307` reads, is byte-identical, and the unit's live test asserts that the blockquote is still there.

## 3. What it cannot settle

- **A front page is not a result**: the section summarises the card and the card summarises its artifacts, so the
  section's authority is the chain and not the page.
- **And the region is one table**: it carries the numbers this unit's vocabulary holds, not every clause of the card,
  so a new clause arrives on the page only when the vocabulary grows with it.
- **And the check is the unit's own**: the vocabulary, the tolerances and the marker syntax are this unit's choices, so
  a reader should take the region as a checked summary rather than as the card.
- **And the card's own coverage is what it is**: the order clause is measured on the overlap and assembly suites rather
  than the earned-label world, and the controls are two flags, which the page does not say.
- *And a summary is not a benchmark.*
