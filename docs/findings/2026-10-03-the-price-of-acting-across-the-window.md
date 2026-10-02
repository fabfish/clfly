# The price of acting across the window: 0.0708 where the window is widest, 0.2976 one step inside it, and nothing at the read step

*2026-10-03. `experiments/e373_the_price_of_acting_across_the_window.py` reads `e363`'s six frozen cells together
with the six trained runs that have since been made on them -- `e364`, `e365`, `e362`, `e367`, `e371` and `e372`, 20
replicates each, the same suite, basis and seed stream -- and prices acting at every step the grid holds. No new
roll. Writes `runs/e373_the_price_of_acting_across_the_window.json`. Four claims, registered before any of the six
was opened in this unit.*

## 1. The shape

The **window** is the margin between the cue and the world's last readable state, so `cue@0` is widest, `cue@11` is
the read step, and `cue@10` is one step inside it. The **price of acting** is the cue-source diagonal minus the
action-source one, paired over the twenty shared seeds.

| cue at | cue source | action source | **frozen price** | **trained cost** | sem | sigma | shrunk by |
|---|---|---|---|---|---|---|---|
| **0** | **0.8399** | **0.7691** | 0.1289 | **0.0708** | 0.0099 | 7.13 | 0.0581 (45%) |
| **10** | **0.5337** | **0.2361** | 0.5977 | **0.2976** | 0.0156 | 19.04 | 0.3001 (50%) |
| **11** | **0.2326** | **0.2361** | 0.0000 | **-0.0035** | 0.0028 | 1.23 | 0.0035 |

| claim | measured | verdict |
|---|---|---|
| S1 each step is one configuration with two sources | shared fields differing `{}` at all three steps, the source moving all seven of its own fields, couplings `1b7d09f2b469` and `5326f4a0edb4` | **MET** |
| S2 the price grows as the window narrows | **+0.2267** from `cue@0` to `cue@10` | **MET** |
| S3 no price at the read step because there is no task | both **within 0.05** of chance, difference **-0.0035** at **1.23 sigma** | **MET** |
| S4 training shrinks the price where the task exists | removes **0.0581** and **0.3001** | **MET** |

## 2. What the middle of the table is, and what it is not

**The `cue@10` price is not the price of acting; it is the price of having fallen out of the window.** `e368` showed
that the action source's world is **at rest** at that step -- `world_sd` exactly 0.0, the read-out a constant -- and
`e369` and `e370` explained it from the wiring: the cue population is two hops from the action population in this
draw, so the world's last readable state, two steps before the end, cannot hold a trace that has had to travel that
far. The frozen grid's own two cells say the same thing before any training: **0.8555** for the cue source,
**0.2578** (chance) for the action source. So the 0.5977 the table calls the frozen price is the gap between a live
channel and a dead one, and **0.2976 is what survives that after training**: the action source learns the suite
through a channel that is at rest at the step the world is read, and it does as well as the read-step cells do.

**The honest measure of what acting costs is therefore the wide step, 0.0708**, and the growth S2 registers is the
boundary being crossed rather than a gradient inside the window. That distinction is the reason this unit's S2
verdict should not be read as "acting gets more expensive as the cue arrives later": the two steps it compares do
not have the same kind of channel. **Nothing in the corpus measures the price of acting at a step where both
channels are live and the margin is short** -- `cue@8` or `cue@9` on this draw -- and that is the unit this one
points at.

**And training removes about half of it.** 0.0581 of the frozen 0.1289 at the wide step, 0.3001 of the frozen 0.5977
in the middle: **45%** and **50%**. Reported and not claimed, since it is arithmetic on one frozen grid and six
diagonals and had no registered bar. What it says is that twenty replicates of training recover roughly half of what
the two drive sources start apart, whatever that gap is made of, which is a statement about the training and not
about the loop.

## 3. What else the six cells hold

**The forgetting rises with the margin, in both sources.** The `naive` arm's mean forgetting is **0.4094** at
`cue@0`, **0.0922** at `cue@10` and **-0.0307** at `cue@11` for the cue source, and **0.3750**, **-0.0229**,
**-0.0229** for the action source. The steps where the task exists are exactly the steps where there is something to
forget, which is a consistency check on the whole line rather than a result: at zero margin both sources read chance
and there is no interference to measure. Reported, not claimed.

**And the paired channels order the same way at every step where they are resolved**: the cue source at `cue@0` and
`cue@10` reads **+0.3115** and **+0.2236** against the action source's **+0.2642** and **+0.0010**. At `cue@10` the
action source's channel is **+0.0010 at 0.16 sigma** -- nothing -- which is `e367`'s finding appearing here as a row
in a table: the run that learns the suite at that step does not do it through the loop.

## 4. What it cannot do

*Three steps, and two of them are the same kind*: `cue@0`, `cue@10` and `cue@11` are the cells `e363` chose, so the
region between the widest step and the boundary -- the only place where the price of acting could be measured
without a dead channel in the comparison -- is not walked here. *And the frozen prices are not paired*: `e363` rolled
512 examples once per cell, so its two cells per step are two independent readings whose difference carries that
grid's resolution, while the trained costs carry twenty paired replicates; the two columns have different precision
and the "shrunk by" column is arithmetic across them. *And the cost is a diagonal*: all six runs carry retention
matrices, channel readings and per-task records, and this unit reads the level each task reached, so "the price of
acting" here is a statement about accuracy and not about what it costs to keep.
