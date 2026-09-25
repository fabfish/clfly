# The reader printed the neighbouring quantity, and the falsifier fired on the one it never printed

*2026-09-25, instrument pass on `e203`. Code: `experiments/e203_ladder_draw_read.py` (band claims `Q1`-`Q3` added,
both gaps printed per draw set), tests: `tests/test_e203_ladder_draw_read.py` (8 tests, 4 new).*

## 1. The defect, stated plainly

`e203` was written under the rule this project keeps re-learning: *a registered claim's read is a versioned,
tested, refusing reader, not an ad-hoc snippet.* It judged P1, P2 and P3 — and the third draw set's registration
added **Q1**, whose sentence is:

> At draw set 200 the peak's `excess` exceeds **every** `rand:` rung's by **at least 0.5**.

The reader had no quantity that could decide that sentence. It had **one** gap — the peak rung against its own
size-matched control (`rand:pool4` for `bio:pool4`) — and Q1 is about the peak against **every** `rand:` rung of
any size. So when I read `e204` I computed Q1's gap by hand, and **its falsifier fired**: `rand:pool16` sits
0.02401 below the peak, where P3's matched gap at the same table is a comfortable-looking +0.51409.

That is the whole finding: **a reader built to print the registered quantity was printing a neighbouring one, and
the claim whose falsifier fired was the one it had never printed.** The two quantities are not variations of each
other — they can point opposite ways:

| draw set | peak | best `rand:` rung (any size) | **unmatched** (Q1) | **matched** at the peak (P3's quantity) |
|---|---|---|---|---|
| 0 (`e181`) | `bio:pool4` | `rand:pool64` | +0.76623 | +1.06906 |
| 100 (`e202`) | `bio:pool8` | `rand:pool64` | +0.36409 | **+1.27079** |
| 200 (`e204`) | `bio:pool4` | `rand:pool16` | **+0.02401** | +0.51409 |

At draw set 100 the matched gap at the **peak** is the largest of its three while the matched gap at the **named**
rung (`bio:pool4` vs `rand:pool4`, P3's 0.72123) is the smallest of its own three. Once the peak moves, *the peak*
and *the rung P2/P3 name* are different objects, and a reader that prints only one of the two gaps is a reader that
can answer a question nobody asked precisely enough.

## 2. What the reader prints now

Per draw set, in one table: the peak and its value, the best `rand:` rung **of any size** and its value, both gaps,
and the count of biological rungs in the top eight. Then `Q1`-`Q3`, each with its registered sentence and falsifier
quoted into `BAND_CLAIMS`, and each decided from the tables given:

- **Q1** — the peak against every `rand:` rung, at the **last** draw set given.
- **Q2** — `bio:pool4` against **25%** of its mean over the **first two** draw sets, with the measured mean printed
  beside the registration's 2.16987 (measured: 2.16986, and the reader prints a NOTE if they ever diverge).
- **Q3** — the **span of the peak** across the three draw sets, which is a claim about the peak and not about the
  rung Q2 names; a test asserts that distinction, since `bio:pool4` can sit still while `bio:pool8` takes the head.

**And the refusals are the point of the design**: Q1 and Q2 are stated *at* the third draw set and Q2's band is the
mean of the first two, so a run given two tables prints Q3's two-draw span and **refuses** the other two rather than
substituting a neighbouring subject. Four new tests cover each claim firing, each null band, and the refusals.

## 3. The verdicts as the reader now prints them

    Q1: the peak bio:pool4 1.85069 against the best rand: rung rand:pool16 1.82668 = +0.02401  -> FALSIFIER FIRED
    Q2: bio:pool4 1.85069  -> MET   (the two-draw mean of bio:pool4 is 2.16986; off the mean by 14.7%)
    Q3: the peaks 2.28112, 2.10798, 1.85069 span 0.43043  -> MET

These agree with the hand computation published in
`docs/findings/2026-09-25-the-third-draw-set-fires-q1s-falsifier.md`, so the finding's numbers are now reproduced by
a reader rather than by a session's arithmetic — which is the standard this project imposes on every other number it
quotes.

## 4. The lesson, in the form this project uses

An instrument that prints *a* gap is not an instrument that prints *the* gap. The failure mode is quiet: P1-P3 all
came out with verdicts, the table was printed, the reader was tested, and the one sentence it could not decide was
the one whose falsifier fired. What made it visible was reading Q1's registered sentence against the reader's own
code — the check this project already applies to bars (rule 51: *quote the registered sentence, do not restate it*),
applied now to the **quantity** rather than to the **bar**.
