# The arms that forget nothing: 50 of the 55 barely learned, and 17 have more left to learn than the corpus's typical arm

*2026-10-01 05:49. Runs: **none new** — `experiments/e305_the_arms_that_forget_nothing.py` joins `e299`'s zero-line
rows to `e304`'s decomposition on `(artifact, arm)`, writing `runs/e305_the_arms_that_forget_nothing.json`. Seconds.*

## 1. Two readings on the same 271 arms

`e299` scoped the README's front-page claim by counting the arms whose `mean_forgetting` is indistinguishable from
zero at two sigma — **55 of 271**, eight of them at forty replicates. `e304` then showed what that field *is*: **the
lost half of the shortfall**, exact, and blind to the half that a task never learned contributes. This unit joins the
two readings.

**The join drops nothing.** All **271** of `e299`'s arms are among `e304`'s 301, on the same `e301` collapse, so
every number below is about one population and not a comparison between two.

## 2. The line picks the arms that learned least

| | arms | median unlearned share |
|---|---|---|
| inside the two-sigma line | 55 | **0.821** |
| outside it | 216 | **0.578** |

**C1 MET** — of the 55, **50 (91%) have an unlearned share above a half**, **31 above eight tenths** and **16 above
nine tenths**. **C2 MET** — the in-line median share is 0.821 against 0.578 outside. An arm the front page would call
one that does not forget is, eight times in ten, an arm whose shortfall is mostly a task it never learned.

## 3. And a third of them are worse than the typical arm

**C3 MET** — **17 of the 55 (30.9%)** have a shortfall above the corpus's median of **0.0861**. **C4 MET** — **8 of
the 55** are inside the line because their **lost term is negative**: they got *better* on the tasks they had
learned, so their entire shortfall is tasks they never had and there is nothing for them to forget.

The sharpest case:

| artifact | arm | `mean_forgetting` | sem | unlearned share | shortfall |
|---|---|---|---|---|---|
| `e20b_noisefloor_check.json` | `naive` | **+0.04167** | 0.02621 | **0.954** | **0.6088** |
| `e20_matchedpair_check.json` | `ewc-block-rand` | +0.02431 | 0.02842 | 0.943 | 0.2824 |
| `e10_rung_side.json` | `ewc-block` | +0.09722 | 0.06143 | 0.650 | 0.1852 |

The first row is inside the two-sigma line at 1.59 sigma, and its shortfall is **seven times the corpus median**. The
sentence *"the corpus measures the absence of forgetting in 55 of its arms"* is true; the sentence a reader will
hear, *"55 of its arms do not forget"*, is false about most of them, and the corpus's own retention matrices are what
say so.

## 4. What the README's scope does and does not now cover

`e299`'s scope clause says the absence is *"a result about particular configurations, not yet a property of the fly
these sentences describe"*. That is still true and this unit sharpens it: the particular configurations are, in the
majority, ones that **barely learned the tasks in the first place**, and the field the absence is measured in cannot
distinguish "held on to it" from "never had it". The clause should be read with this finding beside it.

## 5. What it cannot do

**The line is a two-sigma bound on a mean over replicates**, so an arm enters it by being noisy as well as by
forgetting little — `e20b_noisefloor_check`'s sem is 0.02621, the third largest of the 55 — which is why C3 is stated
about the shortfall and not about the bound. **The share and the mean are computed on the same replicates**, so this
join is a re-description of one set of numbers and not a second experiment on it. **An arm at a low replicate count
and one at forty are treated alike**, and `e299` reports that split; this unit names the eight and does not weight by
power. **And the corpus's arms are not independent configurations**, so 55, 50 and 17 are counts of entries and not
of experiments, and none of them carries a sampling error.

## RE-READ 2026-10-01: C3's quarter, and the arms `e332` to `e334` added

Five arms arrived in one day -- `e332`'s two-arm runs on the world with a state, `e333`'s two-arm runs on the world
with a rule, and `e334`'s single-arm probe -- and the in-line share this unit's **C3** is stated on moved from above
a quarter to **16 of 66, 0.242**. So **C3's falsifier FIRED**: the claim is that at least a quarter of the in-line
arms have a shortfall above the corpus median, and four arms short of it is what the larger corpus says.

**The bar is the unit's and the corpus is what changed**, so the verdict is reported as FIRED rather than re-based --
which is the whole point of registering a bar. C1, C2 and C4 are unchanged: the line still holds the arms that
learned least, still has a median share above the outside arms', still contains arms whose lost term is negative,
and the exhibit -- an in-line arm whose shortfall is more than five times the corpus median -- still stands.

What the test asserts is now the structure and the verdict: the share sits in a band rather than at a point, and
C3's cell is asserted to be **FIRED**, so a future corpus that pushes it back over the quarter has to be noticed
rather than silently absorbed. The one thing this RE-READ cannot say is whether 0.242 is a *different regime* or the
same one measured on more arms -- the statistic is a share over a population that grows, and nothing here separates
a real decline in shortfall-heavy in-line arms from the arithmetic of adding arms.

## RE-READ 2026-10-02: C3's quota crossed back over its bar, which is what a share on a growing corpus does

Six more rows arrived (`e332` to `e337`), and the share C3 is stated on moved from **16 of 66, 0.242** -- the value
the RE-READ above recorded as FIRED -- to **0.312**. So **C3 reads MET again**: the claim is that at least a quarter
of the in-line arms have a shortfall above the corpus median, and 0.312 is above it.

**What this pair of readings establishes is not which way the claim points but that the point is moving.** Two
readings one day apart, on either side of the bar, from arms arriving -- and neither is a statement about the line's
behaviour, since the population and the statistic's denominator both changed. The test therefore asserts **the
verdict against the unit's own bar** rather than a fixed direction, and the share inside a band, so neither the bar
nor the verdict is re-based while a corpus that pushes the share somewhere genuinely different still fires.

The one thing this RE-READ cannot do is what the previous one could not either: separate a real change in the
population from the arithmetic of a ratio over arms that arrive. A share whose denominator grows is not a
measurement of the line until the population is held fixed, and nothing here holds it.

## RE-READ 2026-10-03: the cap was the wrong shape

`e388` and `e389` added sixteen closed-loop runs to `runs/`, and the in-line share C3 is stated on moved from
**0.312** to **86 of 141, 0.610** -- past the `< 0.60` upper cap the 2026-10-01 RE-READ had left in both faces of the
test.

A cap on a ratio whose denominator grows with the corpus is not a statement about the line, which this finding's own
last paragraph already says. So the cap is gone. What the join test asserts now is the comparison the claim is
about, computed from the same join rather than pinned to a level: the arms inside the zero-line carry more shortfall
than the arms outside it, **0.610** against **0.453** -- 86 of 141 against 151 of 333. The artifact face keeps the
direction and the lower bar, because the stored summary does not carry the outside count, and the verdict-agreement
assertion is unchanged. **C3 reads MET at 0.610**, against its own bar of a quarter, and the finding's own caveat
stands: a share whose denominator grows is not a measurement of the line until the population is held fixed.

## RE-READ 2026-10-03, second: the exhibit's multiple was a level

The live test's exhibit is *"an arm inside the line whose shortfall is many times the corpus median"*, pinned at
`5 *` that median. `e393`'s four redrawn worlds brought four more arms in, the median moved to **0.1579** and the
worst in-line shortfall -- `e382`'s five-update tight-step `replay` arm, at **0.7806** with an unlearned share of
**0.977** -- is now **4.94** times it rather than five. A multiple of a quantity that grows with the corpus is the
same defect as a fixed level, one multiplication away, so the multiple is replaced by the exhibit's own shape at
`3 *` and the measured ratio is reported here. The arm is still exactly what the exhibit was for: it has forgotten
nothing and it carries several times the corpus's typical shortfall.

## RE-READ 2026-10-07, third: the exhibit's multiple was a level, and it is gone

The live test's exhibit is *"an arm inside the line whose shortfall is many times the corpus median"*. The 2026-10-03
RE-READ above moved that multiple from `5 *` to `3 *` and said why -- a multiple of a quantity that grows with the
corpus is a fixed level one multiplication away -- and the corpus has now crossed `3 *` as well. The closed-loop runs of
`e438` to `e449` raised the corpus from **271** to **623** arms, the median shortfall from **0.1579** to **0.2604**, and
the worst in-line shortfall is still `e382`'s five-update tight-step `replay` arm at **0.7806** with an unlearned share
of **0.977**, which is **2.997** times the median rather than three. So the multiple is **removed rather than re-based**:
what the join test asserts now is the comparison the exhibit is about -- an arm that has forgotten nothing and carries
more shortfall than the corpus's typical arm -- with the ratio reported here.

The arm is still exactly what the exhibit was for, and the rest of the join reads as it did: **623** arms, **199**
inside the zero-line and **424** outside, with **135 of 199, 0.678** of the in-line arms carrying more shortfall than
the median against **0.415** of the arms outside it -- the comparison the 2026-10-03 RE-READ left as the live test's
substance, unmoved by the corpus's growth and in the same direction. **C3 reads MET at 0.678** against its own bar of a
quarter, and its caveat stands unchanged: a share whose denominator grows is not a measurement of the line until the
population is held fixed. The one thing this RE-READ cannot say is the thing neither of the two before it could: whether
the median the exhibit is compared against moved because the line grew or because the arms arriving in it are of another
kind, and the closed-loop runs that arrived are of a kind this line had not added before.
