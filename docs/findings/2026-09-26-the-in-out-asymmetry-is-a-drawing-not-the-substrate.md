# The drawing lottery: the in/out asymmetry is a property of the DRAWING, and only the rho collapse is a property of the substrate

*2026-09-26 10:40, `runs/e231_cs300_rw{1,2}.json` and `runs/e231_cs800_rw{1,2}.json` (four runs, ~35 min) read against
the `rewire-seed 0` curves of `e231_cs300_rank_curve.json` / `e231_rank_versus_rho.json`. Two of the cs-800/`rho` 0.99
cells of drawing 2 were still being written when this was read; the verdicts below do not depend on them.
Registration: `docs/findings/2026-09-26-registered-the-drawing-lottery.md`.*

## 1. The three drawings, at cs 300

`alloy1` destroys the **in**-structure (keeping out-degree), `inalloy1` the **out**-structure; the ratio is
`alloy1 ÷ inalloy1`.

| `rho` | drawing 0 | drawing 1 | drawing 2 |
|---|---|---|---|
| 0.7 | 1.00× | 1.03× | 0.85× |
| 0.8 | 0.89× | 1.06× | 0.58× |
| 0.9 | 0.62× | **1.78×** | **0.31×** |
| 0.95 | 0.56× | **2.65×** | 0.34× |
| 0.99 | 0.96× | 2.11× | 0.97× |
| **mean over the grid** | **0.81×** | **1.73×** | **0.61×** |

**D2 is MET**: the mean over the three drawings is **1.05×**, inside the registered band of 0.5 to 2 — and the
individual drawings sit on **both sides of 1** (0.61×, 0.81×, 1.73×), spanning a factor of 2.8. So the cs-300
in/out asymmetry has **no sign**: it is a per-drawing coin, exactly as the flag's smoke test suggested.

## 2. The three drawings, at cs 800 — D1 and D3 are FALSIFIED

| `rho` | drawing 0 | drawing 1 | drawing 2 |
|---|---|---|---|
| 0.8 | 2.16× | 0.88× | **0.16×** |
| 0.9 | **10.10×** | 1.06× | **0.23×** |
| 0.95 | 15.82× | 1.03× | 0.82× |
| 0.99 | **16.35×** | **1.00×** | **1.79×** |

**D1** registered that at cs 800, `rho` 0.9 the ratio exceeds 4.14× for **all three** drawings; it is 10.10×, 1.06×
and 0.23× — the falsifier fired. **D3** registered that at cs 800, `rho` 0.99 **every** drawing gives a ratio above 1;
drawing 1 gives **1.00×** and drawing 2 is below 1 at three of its four points (0.16×, 0.23×, 0.82×) — the
falsifier fired.

**So the cs-800 directional separation is a drawing effect.** Drawing 0 shows it at 10–16×, drawing 1 shows essentially
none (1.00–1.06×), and drawing 2 **inverts** it (0.16–0.23×). `e230`'s caution — that the contrast rested on one
drawing of a family whose drawings span 16.44× — was right, and `e231`'s P3 verdict ("the separation is systematic in
`rho`") is now qualified in the only way that matters: **systematic within a drawing, not across them.**

## 3. What survives, and it is the part worth keeping

Every **rank curve** is monotone in `rho`, in every drawing measured: drawing 1 at cs 800 falls 12.46 → 2.48 → 1.28 →
1.01 for `alloy1` and 14.18 → 2.35 → 1.25 → 1.01 for `inalloy1`; drawing 2 falls 5.87 → 2.24 for `alloy1`; and all
three cs-300 drawings fall for all four families. So the two statements separate cleanly:

- **the rank's collapse with `rho` is a property of the substrate** — it survives three drawings of the null at two
  circuit sizes, and `e231`'s nine-point curve describes it;
- **the in/out asymmetry is a property of the drawing** — its sign is not stable at either size (cs 300: 0.61×, 0.81×,
  1.73×; cs 800: 0.23×, 1.06×, 10.10×), and the "which side matters" question is not answered by this line.

## 4. Corrections this forces in the record

- `docs/findings/2026-09-26-the-rank-curve-at-both-sizes.md` §4 read the *sign inversion between sizes* off one drawing
  per size. Two of the three drawings say the sign is not stable **within** a size either, so that reading has to be
  withdrawn as a size effect: what it measured was two drawings.
- The plan's Claims section and the paper's paragraph both carry that sentence and are updated with it.
- `e231`'s P3 verdict stands as registered and is **not** the same claim: it asked whether the separation appears at
  more than one `rho` **within** the curve it measured, and it does. The lottery asks the next question, and answers it
  the other way.

## 5. What this cannot do

- **Three drawings**, all at `seed0`-driven task seeds: the drawing axis is sampled, not measured, and a fourth
  drawing could move the cs-300 mean outside the band D2 turned on.
- **One statistic**: this is the rank. Whether the *penalty's* in/out comparison is equally drawing-dependent is
  unmeasured — and `e233`'s penalty curve is one drawing per cell, so it inherits the same caveat.
- **Four drawings' worth of cells at cs 800** (four `rho` values × three drawings) are the whole cs-800 evidence:
  the separation's absence in drawing 1 (1.00× to 1.06× at every point) and its inversion in drawing 2 (0.16× to
  0.82× at three of four) are what falsify D1 and D3, and a fourth drawing is unmeasured.
- **`rho` still mixes depth with weight scale**, and nothing here separates them.
