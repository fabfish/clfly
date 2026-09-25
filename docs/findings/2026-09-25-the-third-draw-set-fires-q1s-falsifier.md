# The third draw set fires Q1's falsifier: the band is biological by its matched contrast and not by its height

*2026-09-25 23:05, `runs/e204_ladder_d300_12seeds_seed0-200.json` (36 min against `e202`'s 29 and `e181`'s 44 —
the same command, so rule 49's price for it is the 20–45 min range this row quotes). Read by
`experiments/e203_ladder_draw_read.py --drawn .../seed0-100.json --drawn .../seed0-200.json`, exit 0. The
registration is `docs/findings/2026-09-25-registered-a-third-draw-set-for-the-band.md`.*

> **CORRECTED 2026-09-26 by the fourth draw set**: this finding reads the lead over the best `rand:` rung as a
> MONOTONE DECAY (0.76623 → 0.36409 → 0.02401) and calls the height-based statement dead. The fourth value is
> **+0.29046** — it fell and came back — so the decay was three points of a noisy quantity. The falsifier did
> fire at this draw set (that part stands, and it is 1 of 4 draws so far), and the matched claim this finding
> calls marginal holds 4 for 4 at +1.15902 on the fourth. See
> `docs/findings/2026-09-26-the-fourth-draw-set-holds-c2s-claim-and-breaks-the-decay.md`.

## The three registered claims

| | claim | verdict at draw set 200 |
|---|---|---|
| **Q1** | the peak exceeds **every** `rand:` rung by at least 0.5; falsifier a `rand:` rung within **0.2** of the peak; null 0.2–0.5 | **THE FALSIFIER FIRES** — `rand:pool16` sits **0.02401** below the peak |
| **Q2** | `bio:pool4` within 25% of its mean over the first two draw sets (2.16987), i.e. in [1.627, 2.712] | **MET** — 1.85069 |
| **Q3** | the peak's excess spans **below 0.5** across the three draw sets; falsifier at or above 1.0 | **MET** — span **0.43043** |

The third draw set's table is led by `bio:pool4` at **1.85069** — the same rung that led draw set 0 — after
draw set 100's `bio:pool8` at 2.10798. So the peak's identity is `pool4`, `pool8`, `pool4`: **the identity does
not survive as a rung, and its value does not survive as a constant**, which is what Q3 says in one number.

## The two gaps, and why they part company

Everything the C2 line claims about the ladder is one of two statements, and the third draw set separates them:

| draw set | peak | best `rand:` rung | peak's lead over it (**unmatched**) | `bio:pool4` vs `rand:pool4` (**matched**) | biological rungs in the top 8 |
|---|---|---|---|---|---|
| 0 (`e181`) | `bio:pool4` 2.28112 | `rand:pool64` 1.51490 | **+0.76623** | **+1.06906** | 6 of 8 |
| 100 (`e202`) | `bio:pool8` 2.10798 | `rand:pool64` 1.74390 | **+0.36409** | **+0.72123** | 6 of 8 |
| 200 (`e204`) | `bio:pool4` 1.85069 | `rand:pool16` 1.82668 | **+0.02401** | **+0.51409** | 5 of 8 |

- **The unmatched lead decays monotonically**, 0.766 → 0.364 → 0.024, and at the third draw set it is
  effectively gone. A reader who asked *"is the best rung biological?"* gets **not supported** at n = 3: at draw
  set 200, `rand:pool16` and `rand:pool64` are second and third, above `bio:pool32`, `bio:pool8`, `bio:pool128`
  and `bio:pool16`.
- **The matched contrast survives all three draws** — `bio:pool4` against its own size-matched random control at
  the same rung is +1.069, +0.721 and **+0.514**, every one above the 0.5 bar — but the third draw set lands
  **0.014 above that bar**, so the claim is now marginal rather than comfortable, and it is the *same claim in
  the same form* that C2 registered. Note the two quantities are not comparable to each other: at draw set 100
  the matched gap at the **peak** (`bio:pool8` against `rand:pool8`) is +1.27079, the largest of the three,
  while the matched gap at `pool4` is the smallest of its own three. The peak and the named rung are different
  objects once the peak moves.

**So the honest 3-draw statement of C2 is**: *a biological pooling partition beats a group-size-matched random
partition at the same rung, at every draw set measured (+0.51 to +1.27), while the claim that the best rung is
biological is not supported — the top of the table is a band of biological and random rungs whose order is
draw-set-dependent.* The previous pass's phrase *"the biological rungs occupy the top eight of sixteen in both
draw sets"* was a two-draw statement; at the third it is **5 of 8**, and that clause should not be quoted again
as though it were three.

## What this costs, and what it does not touch

- **Cost (rule 49)**: 36 min measured, against the row's registered 20–45 min range; the same command has now
  been executed three times in this configuration family (2653 s, 1758.9 s, and this one), so the range is
  earned rather than extrapolated.
- **Not touched**: nothing here bears on the network line's claims (`e193`'s axis, `e188`/`e191`'s interference,
  the λ = 1.0 saturation). Those are a different instrument with different draws, and the draw lesson that
  applies to them is the one already recorded — it cancels between arms at the same draw and does not cancel
  between conditions.
- **Still not separable**: the three ladders each draw task sets, matched-random partitions and rewiring from
  one `seed0`, so this design cannot say which of the three draws moves the unmatched lead. Three draw sets are
  two degrees of freedom, so Q3's span is a span and never an sd.

## What would settle the remaining question

The unmatched lead's decay is the one number here with a shape (0.766 → 0.364 → 0.024), and three points of a
decaying quantity invite a fourth. **Registered as a question rather than as a claim**: a fourth draw set
(`--seed0 300`) would give the decay a fourth point and Q3's span a fourth term — but the honest prior is that
the unmatched statement is already dead at the third, and what a fourth point buys is a *slope* for a quantity
that C2 does not rest on. The claim C2 does rest on — the matched contrast at the same rung — is the one that
would benefit from more draw sets, because its third value (0.514) sits 0.014 above its own bar.
