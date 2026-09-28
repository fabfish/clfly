# The pairing's gain falls with the tasks' input overlap — and the point it turns on is one replicate from flipping

*2026-09-28 22:30. Runs: **none new** — `experiments/e273_the_pairing_falls_with_the_overlap.py` reads the corpus's
overlap axis (`runs/e193_r32_overlap025_methods_40reps.json`, `runs/e193_r32_overlap050_methods_40reps.json`,
`runs/e193_r32_overlap075_methods_40reps.json` and `runs/e153_r32_overlap1_methods_40reps.json`), writing
`runs/e273_the_pairing_falls_with_the_overlap.json`. Seconds.*

## 1. The item: a question `e271` left to a run, answered from the corpus

`e271`'s census found the only powered rows in the record where the pairing *hurts* — both on
`e193_r32_overlap075_methods_40reps`, whose `ewc-block` and `ewc-block-rand` arms are anti-correlated across
replicates — and left the cause to a run. **The corpus already has most of the answer**, because that configuration
was run at three input overlaps and a fourth exists at full overlap. The first three differ in **nothing but the
overlap** (checked field by field before anything is compared), so the number that licenses the paired sem can be read
as a function of the task geometry.

## 2. What the axis says

| `input_overlap` | correlation, accuracy | correlation, forgetting | unpaired over paired sem, accuracy |
|---|---|---|---|
| 0.25 | **+0.257** | +0.265 | 1.160 |
| 0.50 | **+0.101** | +0.164 | 1.055 |
| 0.75 | **−0.063** | −0.047 | **0.970** |
| 1.00 | +0.131 | +0.139 | 1.072 |

**X1 MET — the correlation falls at every step over the controlled range, on both metrics.** **X2 MET — and the
pairing's gain follows it into reverse**: 1.160, 1.055, **0.970**, so at the tightest of the three the paired figure is
*looser* than the unpaired one, which is the sign `e271` found without being able to say why. The mechanism the pattern
suggests is interference: with more overlapping task inputs the two arms compete for the same representations, so a
seed that helps the treatment hurts its control and their fluctuations stop agreeing.

**X3 MET — but the relation fails at the fourth point.** At full overlap the correlation is **+0.131** on accuracy and
**+0.139** on forgetting — above the 0.75 point and back near the 0.50 point — so "more overlap means less sharing"
holds across the controlled range and not across the whole one.

**X4's falsifier fired, and it is the counterweight.** Dropping any single replicate leaves the correlation on the same
side of zero in six of the eight matrices, **but not in the two that matter**: at overlap 0.75 the accuracy reading
becomes **+0.004** when one replicate is dropped, and the forgetting reading **+0.043**. So **the negative correlation
that the whole pattern turns on is one replicate wide**, and the point the story rests on is the one whose sign is not
robust.

## 3. What follows

**The number that licenses the paired sem is a property of the task geometry, and the corpus's own axis says so** — a
fact the register has been treating as a per-run incidental. And the honest form of the 0.75 point is not "the arms are
anti-correlated there" but **"the arms are not detectably correlated there, and the reading is a draw that could have
gone either way"** — which is what a −0.063 correlation at forty replicates with a standard error near 0.16 amounts to.
The register's practice of quoting the paired figure is unaffected at the other three points; at 0.75 it is quoting a
number whose sign is a coin, and `e271`'s rule — look at `corr` before quoting the paired sem — is exactly the right
response.

## 4. What it cannot do

**The fourth point is not a controlled comparison**: the full-overlap run carries two more arms beside the three these
matrices use, and nothing here shows that an arm's own training is unaffected by the arm list, which is the assumption
the comparison rests on. The overlap axis has four points and one is out of the controlled range, so the shape is a
direction and not a law. A correlation at forty replicates has a standard error near **0.16**, which is the order of
the *whole* fall from 0.25 to 0.75 — so three draws ordered themselves and could in principle have ordered themselves
the other way. X4 shows the endpoint is fragile and the two inner points are not tested for fragility at all. The
mechanism is a candidate — interference between overlapping inputs — and not a measurement of it. And no run is made,
so nothing here varies the overlap at a fixed arm list.
