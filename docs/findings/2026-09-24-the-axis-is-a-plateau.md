# `e116`: the axis measured evenly is a plateau with the narrow end resolved higher

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, five runs; artifacts `runs/e116_r{1307,900,700,128,32}_40reps.json`
(40 replicates each).
**Artifacts:** the five above, plus `runs/e115_r{300,512}_40reps.json`, so **all seven read-outs now carry forty
replicates**.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, `--repeats 40`.
**Pre-registration:** `docs/findings/2026-09-23-the-axis-at-one-precision-preregistered.md`, committed before the
runs.
**Context:** `docs/findings/2026-09-23-forty-replicates-refute-the-minimum.md`, which left the axis measured with
**unequal precision** — 300 and 512 at forty replicates against five for the rest, so that the trough's *extent*
was not a measured quantity at all.

---

## 1. All five controls pass, so the axis is finally one measurement

**C0 passed at every read-out**: the first five replicates of each forty-replicate run are **bit-identical** to
the stored five-replicate run, which is what makes the extra thirty-five replicates an extension rather than a
second sample. **Seven read-outs, one precision, one error bar each** — and the deliverable the pre-registration
asked for is a shape rather than a new extreme.

## 2. The shape, and it is simpler than any of the five claims that preceded it

| read-out | **forgetting (40 reps)** | sem | per-repeat sd | 5-replicate value | sd ratio |
|---|---|---|---|---|---|
| **1307** (whole) | **+0.0357** | 0.0067 | 0.0423 | +0.0479 | 0.55 |
| **900** | **+0.0219** | 0.0039 | 0.0244 | +0.0292 | 1.22 |
| **700** | **+0.0221** | 0.0047 | 0.0297 | +0.0354 | 0.75 |
| **512** | **+0.0250** | 0.0048 | 0.0305 | +0.0208 | 1.69 |
| **300** | **+0.0232** | 0.0040 | 0.0252 | +0.0083 | 1.12 |
| **128** | **+0.0370** | 0.0051 | 0.0325 | +0.0333 | 1.16 |
| **32** | **+0.0750** | 0.0088 | 0.0556 | +0.0729 | 1.65 |

| neighbour step | difference | σ | resolved at 2σ |
|---|---|---|---|
| 1307 → 900 | −0.0138 | 1.79 | no |
| 900 → 700 | +0.0003 | **0.04** | no |
| 700 → 512 | +0.0029 | 0.43 | no |
| 512 → 300 | −0.0018 | 0.29 | no |
| **300 → 128** | **+0.0138** | **2.12** | **yes** |
| **128 → 32** | **+0.0380** | **3.73** | **yes** |

**So the axis is a flat plateau from 900 to 300 — four read-outs spanning +0.0219 to +0.0250, a range of
0.0031, with every neighbouring step inside 0.43σ — and the narrow end is resolved above it: 128 by 2.12σ and 32
by 3.73σ, the latter 5.5σ above the plateau's low point.** The whole state sits at **+0.0357**, i.e. at 128's
level and 1.79σ above the plateau: **nominally elevated and not resolved.**

**Every fine feature of the previous five fires is gone, and each was a five-replicate artifact:**

| claim | 5 replicates | 40 replicates |
|---|---|---|
| the whole-state "outlier" | +0.0479, the highest of three | **+0.0357, indistinguishable from 128** (0.29σ) |
| the local bump at 700 | +0.0354, above 900's +0.0292 | **+0.0221 against +0.0219 — 0.04σ** |
| the interior minimum at 512 | +0.0208, the lowest of five | **inside a four-point plateau** |
| the interior optimum at 300 | +0.0083, lowest in the corpus | **+0.0232, inside the same plateau** |
| "the plateau has an extent" | not measurable | **900 to 300, and it is flat** |

**The pre-registered P3 is confirmed** — the flat region extends from 300 to 900, with none of those four steps
resolving — and **P2 is confirmed** (32 remains the maximum, 5.5σ above the plateau). **It is the first shape
claim on this axis measured at the resolution it is stated at**, and it is much smaller than the five it
replaces: *spelling the read-out narrower than 300 makes three-task naive forgetting rise, first mildly at 128
and then sharply at 32; everything from 900 down to 300 is one plateau; and the whole state is nominally above
that plateau but not measurably.*

## 3. My own directed correction is falsified, and that is the methodological result

**P1 predicted the forty-replicate sds would be *larger* than the five-replicate ones**, on the argument that a
five-point sd of a heavy-tailed quantity is an underestimate and that read-outs 300 and 512 had both gone up. It
**fails: the ratios are 0.55, 1.22, 0.75, 1.69, 1.12, 1.16, 1.65 — three of seven went down**, and the largest
movement is *downward* (the whole state's sd falls from 0.0768 to 0.0423).

**So the five-replicate sd is noisy in both directions rather than biased**, which corrects last fire's
correction: the "2.9× underestimate" I derived from read-out 512 was not a systematic correction but one draw
from a distribution spanning 0.55×–1.69×. **And the consequence for the previous fire's best sentence is
direct**: a two-sided factor-of-two tolerance that "let a 1.69× underestimate through" would equally have let a
0.55× *overestimate* through — which it did, at the whole state, in the same table. **The rule should have been
"the count is uncertain by a factor of three in either direction", not "the counts are low".**

**And the five-replicate *means* were noisy in both directions too**: four moved down (1307 by 0.0122, 700 by
0.0133, 900 by 0.0073) and three moved up (300 by 0.0149, 512 by 0.0042, 128 by 0.0037). Read-out 300's
five-replicate value is the extreme case and it is the one a whole design statement was built on — which is the
sequence's recurring shape in its purest form, since the five-replicate value was the *lowest in the corpus* and
the forty-replicate value is in the middle of a plateau.

## 4. What this cannot settle

- **One draw per read-out.** Seven read-outs, one draw each, so the shape is a property of *these* seven subsets;
  the draw span measured at read-out 300 is 0.0125, which is **at** the plateau's internal range (0.0031 is
  below it, but the plateau-to-128 step of 0.0138 is not). So the plateau's flatness is smaller than one draw
  span and the 128 step is about one — **the draw could account for the whole difference between the plateau and
  128**, and separating them needs replicate draws rather than replicates, which is forty times dearer.
- **The whole state's 1.79σ is not a null.** It is nominally elevated and this design cannot say more; 72
  replicates per side was the earlier price for that step and it was computed from a five-replicate sd, which
  this fire has shown to be unreliable in both directions.
- **It does not touch the mechanism question**, which stands where five fires left it: every mechanical quantity
  measured is monotone in the read-out while both reported metrics are not, and the fine structure that claim was
  about is now known not to be there.
