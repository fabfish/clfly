# At the registered midpoint P1 and P2 both fail, the registered null is what landed — and the distant-pair term is 82% done while the adjacent-pair term is 20%

**Date:** 2026-09-25
**The measurement the three-level registration was built for.** `runs/e193_r32_overlap050_methods_40reps.json`
landed at 16:14:12 with target `--input-overlap 0.50`, achieving **Jaccard 0.3333** — the registered midpoint, to
four decimals. Both dose reads were run on it the moment it appeared (`e191 --dose` on the interference account,
`e188 --dose` on the accuracy one), and the pre-read predictions this session wrote down **before** the artifact
existed are scored in §4. No number here is quoted from a run launched for this finding.

---

## 1. The registered bars, and both of them fail

The registration (`docs/findings/2026-09-25-registered-the-overlap-axis-at-three-intermediate-levels.md` §4) put P1
and P2 on the **`naive`** arm at achieved overlap 0.3333, against the disjoint baseline `e116` (overlap 0.0,
λ = 3e-3 — `naive` does not read `lam`, and the admission rule prints the pair it used):

| | measurement at achieved 0.3333 | bar | verdict |
|---|---|---|---|
| **P1** adjacent-pair interference vs `e116` | **+0.02463 ± 0.01555 = 1.58σ** | > **+0.0617** (half the 0 → 1 rise) | **NOT met** |
| **P2** that rise as a fraction of its own 0 → 1 rise | **20.0%** | **≥ 60%** (the registered, absolute reading) | **NOT met** |

P2 fails under the analytic-relative reading too (45.9% at the midpoint), so **the correction in
`docs/findings/2026-09-25-p2s-bar-is-60-percent-and-the-read-applied-46.md` did not decide this verdict** — it
changed which bar the read states, not which way this point came out. That is worth saying plainly because the same
correction would have decided a 50% measurement, and this one is 20.0%.

The registered **falsifier** — "the near component at achieved 0.1429 equals its 1.0 value within 2σ", which would
say *any* overlap suffices — **did not fire**: at 0.1429 the rise is 12.3% of the total, i.e. 0.01516 against
0.12337, a gap of 0.108 = 6.8σ.

## 2. The registered null is what landed, and it was registered as worth keeping

The registration's own null clause: *"Three ~1σ rises whose means sit between the ends would leave the direction
standing on the two-point contrast while the shape stays unmeasured, and that is a statement about the effect's size
rather than about its existence."*

That is the measurement. On the adjacent-pair term:

| achieved overlap | rise vs `e116` | σ | progress |
|---|---|---|---|
| 0.0000 | 0 (by construction) | — | 0% |
| 0.1429 | +0.01516 ± 0.01229 | 1.23σ | 12.3% |
| **0.3333** | **+0.02463 ± 0.01555** | **1.58σ** | **20.0%** |
| 1.0000 | +0.12337 ± 0.01579 | 7.81σ | 100% |

Every intermediate is ~1σ, the means are ordered between the ends, and **the direction still rests entirely on the
0 → 1 contrast** (7.81σ). The registered P1 and P2 therefore fail *as bars* while the null they were built to
distinguish from lands exactly: the shape of the *adjacent-pair* response is unmeasured at forty seeds.

Rule 42's price says it in the instrument's own units — the midpoint read prints it: the measured change
(+0.02463 = **1.58σ**) would need **143 seeds** for 3σ, while P1's bar itself is **3.97σ** at this level's sem and
would need only **23**. So P1 was a bar the design could have resolved and the effect it named is not there; P2's bar
is a fraction, and the fraction is a third of it.

## 3. The finding the registration did not ask for: the two terms have OPPOSITE shapes

`e191` splits interference into the **adjacent** task pairs and the **distant** ones, and the same instrument, on the
same arm (λ = 3e-3 family: baselines `e116` at 0.0 and `e144` at 1.0), the same 40 seeds, gives two completely
different shapes along the overlap axis:

| achieved overlap | **near** (adjacent) | **far** (distant) |
|---|---|---|
| 0.1429 | +0.01516 ± 0.01229 = 1.23σ → **12.3%** | +0.00659 ± 0.02186 = **0.30σ** → 7.5% |
| **0.3333** | +0.02463 ± 0.01555 = 1.58σ → **20.0%** | **+0.07239 ± 0.02190 = 3.31σ** → **82.1%** |
| 1.0000 | +0.12337 ± 0.01579 = 7.81σ → 100% | +0.08818 ± 0.02825 = 3.12σ → 100% |

**At the registered midpoint the distant-pair term has completed 82.1% of its 0 → 1 rise, resolved at 3.31σ, while
the adjacent-pair term has completed 20.0% and is resolved at nothing.** The gap is 62 percentage points, and it is
the far term that carries *all* of the resolved overlap response at this point.

This is directly load-bearing for C4's box, which localises the analytic/network disagreement to the **adjacent**
pairs and finds the distant pairs pointing the same way in both accounts
(`docs/findings/2026-09-25-the-composition-survives-the-quantity-the-proxy-could-not-see.md`). If the distant pairs
are the term that responds to the overlap, and they rise in *both* accounts, then the manipulation's shared,
line-independent part is the **distant** one, and the disagreement lives entirely in the adjacent term — which this
measurement now shows is the **slow** term, three fifths of the way through the axis still unmeasured at forty seeds.

**And the accuracy account splits the same way.** On the same artifact (`e188 --dose`), `naive`'s forgetting at the
midpoint is **+0.0083 ± 0.0106 = 0.79σ** — under 1σ, and its rule-42 price is **583 seeds** — while its accuracy cost
is **−0.0328 ± 0.0074 = 4.47σ**, resolved. So at the midpoint of the overlap axis the network's cost is visible in
the accuracy and invisible in the forgetting, which is the same "one instrument moves, the other does not" pattern
`e139` first reported, now on the axis rather than across methods.

**An unregistered wrinkle worth recording**: `naive`'s forgetting *means* are **non-monotone** across the two
intermediates — +0.0141 (1.2σ) at 0.1429 and +0.0083 (0.79σ) at 0.3333, i.e. 44% then 26% of the 0 → 1 rise of
+0.0318. Both are unresolved, so this is not evidence of non-monotonicity; but it does mean the forgetting account's
shape is not merely unmeasured, it is not even ordered in the means, and the "raising the overlap raises forgetting"
claim is a claim about the 0 → 1 endpoints on that account.

## 4. The pre-read predictions, scored

Both numbers below were written into
`docs/findings/2026-09-25-p2s-bar-is-60-percent-and-the-read-applied-46.md` §5 **before** the level-0.50 artifact
existed, from the level-0.25 point alone, and both were named as extrapolations rather than bars:

| extrapolation from +0.01516 at achieved 0.1429 | predicted progress at the midpoint | measured |
|---|---|---|
| holding the slope in achieved overlap (86.0 points/unit) | 28.7% | — |
| holding the ratio to the analytic line (0.306) | 23.4% | — |
| **either of them, against the two bars** | **below 60% and below 45.9%** | **20.0% — below both** |

The measurement came in **below both extrapolations**, so the adjacent-pair response is more back-loaded than either
simple projection: 20% of its range at a third of the axis, and the remaining 80% has to arrive over the last
two-thirds. Both extrapolations nonetheless got the *conclusion* right — the registered bar would not be met — which
is the only thing they were written to carry.

## 5. The λ = 1.0 family, which this launch accidentally produced

The second registration (`docs/findings/2026-09-25-registered-the-lambda-one-familys-dose-response.md`) put P1 and P2
on the block arms against `e153` (λ = 1.0, overlap 1.0). At the new point:

| `ewc-block` vs `e153` | at 0.1429 | at 0.3333 |
|---|---|---|
| forgetting (e188) | +0.0453 ± 0.0110 = **4.10σ** | +0.0185 ± 0.0116 = **1.60σ** |
| accuracy (e188) | −0.0309 = **4.2σ** | **−0.0458 ± 0.0083 = 5.53σ** |
| adjacent-pair interference (e191) | +0.0010 = 0.3σ | −0.0059 ± 0.0051 = **1.20σ** |
| distant-pair interference (e191) | — | −0.0007 ± 0.0028 = 0.26σ |

- **P1 holds so far**: forgetting at 0.3333 (+0.0185) lies between the 0.1429 value (+0.0453) and zero, ordered as
  registered. The 0.6000 point decides the ordering.
- **P2 is broken at the midpoint, marginally, and this is the honest reading of it.** P2 says the interference term
  stays within **1σ of zero at every level**; `ewc-block`'s adjacent-pair term has moved **−0.0059 = 1.20σ**. The
  registered **falsifier** needs ≥2σ and did **not** fire, so this is a violated clause rather than a refuted design —
  but a clause is a clause and the row should not be read as clean.
- **The accuracy column strengthens as the overlap rises while forgetting shrinks** for the same arm: at 0.1429 the
  cost was −0.0309 (4.2σ) and at 0.3333 it is −0.0458 (5.53σ). Lower overlap costs this arm *less* accuracy, not more,
  which is the opposite ordering to its forgetting on the same two points.
- `ewc-block-rand` moves with it on accuracy (−0.0281 = 3.16σ) and not on forgetting (+0.0021 = 0.17σ).

## 6. Registered now, before the last level lands

Level 0.75 (achieved 0.6000) is running when this is written. Two shape claims, registered here before its artifact
exists, prompted by §3 — a claim written after seeing two points but before the third is a registration, and the
alternative is a post-hoc shape story:

- **S1 — the separation persists.** At achieved 0.6000 the `naive` distant-pair progress exceeds the adjacent-pair
  progress by **at least 40 percentage points** (measured at 0.3333: 82.1% against 20.0%, a gap of 62). **Falsifier**:
  the gap falls below **15 points**, which would say the 0.3333 separation was one point's noise rather than a shape.
  **Null worth keeping**: both between 30% and 60%, which would leave the two terms of one instrument
  indistinguishable on this axis.
- **S2 — the adjacent-pair term is still back-loaded.** At achieved 0.6000 the adjacent-pair progress is **below 50%**
  of its 0 → 1 rise, with the two §4 extrapolations from the first two points reading **30.8%** (constant slope from
  the 0.3333 point) and **22.6%** (constant ratio to the analytic line, whose own progress there is 86.5%).
  **Falsifier**: at or above **50%**, which would say the response accelerates early and the 20.0% at the midpoint was
  the anomaly.

Both are read by the same two commands (`e191 --dose`, `e188 --dose`) on the artifact when it lands. **S1's
distant-pair progress was not printed by the reader when this was written** — it printed P2 for the near term only,
which is the defect rule 42's footer was added to the same function to remove — so the claim's read would have been a
hand computation. It is now computed for **both** terms (`full_rise` and `progress_fraction` are keyed by term, and
the near row prints the far term beside it), so §3's table is the read written out rather than an instrument
substituted by hand, and the §3 numbers were reproduced by the changed reader before this was committed.

## 7. What this does not license

- **That the network line's overlap response is unmeasured.** It is measured: 7.81σ on the 0 → 1 contrast, and 3.31σ
  on the distant-pair term at the midpoint. What is unmeasured is the **shape** of the adjacent-pair term, which is
  the term both registered bars were placed on.
- **That P1's failure means the adjacent term does not respond.** It means the response at a third of the axis is
  below half the 0 → 1 rise, which the registration named in advance as a possible outcome.
- **Any magnitude against the λ = 1.0 family.** The block rows are an ordering within one family and one draw per
  family, exactly as that registration says.
- **That the far-term shape is a connectome property.** It is measured on `mb+cx+al@n1307`, three tasks of eighty
  neurons at seed 0, and the achieved-overlap table is a property of that circuit; a reader changing the circuit
  changes every cell of §3.
- **That the two accounts' splits share a cause.** The adjacent/distant split (interference) and the
  forgetting/accuracy split (cost) are two different decompositions of the same run, and nothing here measures
  whether they are the same phenomenon.
