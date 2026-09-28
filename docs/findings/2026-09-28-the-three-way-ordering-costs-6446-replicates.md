# The three-way ordering needs 6,446 replicates: state one bit of it instead

*2026-09-28 22:00. Runs: **none new** — `experiments/e272_the_budget_the_ordering_needs.py` prices the ordering from
the runs already on disk (the two `e266` matrices at sixteen replicates and `e178`'s 144-replicate matrix at the same
cell), writing `runs/e272_the_budget_the_ordering_needs.json`. Seconds.*

## 1. The item: the question `e266` left, priced instead of bought

`e266` bought two matched-settings runs to ask whether one configuration fixes the ordering of the three contrast
pairs, and it does not — the two seeds give three orderings while every pair's two correlations differ by less than the
95% Fisher band. That raises the obvious next question, **what budget would resolve the ordering?**, and the answer is
computable from disk: an ordering is a comparison of correlations, and a correlation's standard error is a function of
`n`.

Two inputs are needed and both are in the corpus — the **gaps** an ordering rests on (from the two `e266` matrices,
with `e178`'s 144-replicate matrix at the same cell) and the **rate** at which a replicate is bought (the two runs' own
clocks, and `e178`'s). The standard error is Fisher's, `(1 - r^2)/sqrt(n - 3)`, and it is **validated against the
corpus before it is used**: the two `e266` runs are two independent estimates of the same three quantities at the same
budget, so half the distance between them is an empirical standard error at `n = 16`.

## 2. What the arithmetic says

**W1 MET — the two estimators agree.** The empirical standard error at sixteen replicates is **0.311** against
Fisher's **0.244** — a factor of **1.28**. So the formula the pricing rests on is the right size for this corpus, and
its `1/sqrt(n)` scaling — the assumption `e259` flagged and `e261` found measurable — is not being stretched here.

**W2 MET — and the gaps an ordering rests on are tiny.** Over the two runs' four orderings the adjacent gaps run
**0.030 to 0.547**. The smallest is **0.030**, on the first run's forgetting metric, between the basis pair (0.364)
and `naive`-`ewc` (0.394) — **an ordering is being read across a three-hundredths gap on a correlation whose own
standard error is a quarter.**

**W3 MET — and resolving it is unpayable while one bit of it is already bought.** That 0.030 gap needs **6,446
replicates** at two sigma, which is **367 hours** at the cell's measured **205 s per replicate** — fifteen days of the
machine for one ordering. The highest-against-lowest gap in the same run is **0.877**, which needs **10 replicates**
and is already resolved within the 144 the corpus has. And the corpus's own best-powered matrix reads a gap of
**0.199** between its top and bottom pairs at 144 replicates — a reading it can support and a three-way ordering it
cannot.

## 3. What follows: the claim the register can afford

**The ordering should be stated as one bit — which pair leads — and not as a three-way ordering.** The one-bit form
costs tens of replicates and is already answered at this cell; the three-way form costs thousands and would be a
different experiment from the one the line has been reading. This is `e259`'s shape one level up: there the question
was whether sixteen replicates could see an effect, here it is whether any affordable budget can order three
correlations whose gaps are a tenth of their own error. **And it is why `e266`'s disagreement is the answer rather than
a call for more seeds**: the two runs do not disagree because sixteen is too few for *this* claim — they disagree
because the three-way claim is underpowered at *any* budget the line can pay, and the run that would settle it is
fifteen days long.

## 4. What it cannot do

The three pairs of one run **share arms**, so their correlations are not independent and the `sqrt(2)` between two of
them is an approximation — the empirical check is between two runs of the *same* quantity, not between two pairs, so
the dependence is disclosed and not measured. The standard error is Fisher's, whose `1/sqrt(n)` part is the scaling
`e259` assumed and `e261` measured rather than derived. The rate per replicate is a wall-clock average over three runs
on one machine, so the hours are a **budget and not a schedule**, and a faster configuration would move them. Only the
two contrast metrics are priced, since the ordering is a statement about them. And nothing here says a larger budget
would not change the ordering *again* — which is exactly what `e266`'s two runs warn about, and why the honest form is
to state the bit that is bought.
