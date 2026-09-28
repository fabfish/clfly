# The registry it names: 27 contrasts over 22 arms, and 62 artifacts at forty replicates it does not name

*2026-09-28 23:20. Runs: **none new** — `experiments/e283_the_registry_it_names.py` reads `e151`'s registry, the corpus
under `runs/`, git, and the paper, writing `runs/e283_the_registry_it_names.json`. Seconds.*

## 1. The row, which carries three claims

The paper's reproducibility table has one row for `e151`, and it says three separable things:

> **the per-task decomposition of every forty-replicate contrast in the record** … **Its registry was extended on
> 2026-09-24 from 22 contrasts to 27 when the arms that landed that evening were added**, which is why the counts in
> §4.2 and §8 are the extended ones | `runs/e151_pertask_audit.json`, over the 27 arms it names |

1. **the two nouns**: `e151`'s registry is a tuple of `(label, path A, method A, path B, method B)` rows, so a row is a
   *contrast* and the *arms* are the distinct `(path, method)` pairs behind it. The sentence's two numbers sit on two
   nouns, and the two counts may not match the nouns they are on.
2. **"every … in the record"**: the registry is a hard-coded tuple, so its coverage is a property of the corpus on the
   day it was last edited — 2026-09-24, four days and 300-odd artifacts ago.
3. **the date and the direction**: "extended on 2026-09-24 from 22 contrasts to 27" is a claim about a commit.

Registered before the reading: **U1** the rows name 22 distinct arms, so the two nouns are exchanged; **U2** the
registry names under half of the artifacts carrying a forty-replicate arm, and at least one it does not name is named
by path in the record; **U3** the tuple held 22 rows before one commit dated 2026-09-24 and 27 after it.

## 2. The reading

**U1 MET — 27 rows, 22 distinct arms, every row pairwise.** The paper's sentence reads "from **22 contrasts** to **27**
… over **the 27 arms** it names". Both numbers are right and both nouns are wrong: the registry names **22 arms** and
**27 contrasts**. The committing author knew which was which — the commit that made the extension is titled *"the two
censuses were extended to today's arms"* and its body says *"e151: 22 -> 27 contrasts"* — so the slip is in the paper's
sentence and not in the unit.

**U2 MET — "every" is an epoch, and the misses are enumerable.** The corpus holds **62** artifacts carrying at least one
arm at exactly forty replicates (**97** such arms). The registry names **14** of those artifacts — **22.6%** of the
population the sentence's noun describes, against a falsifier at half. **75** forty-replicate arms are outside it, and
**10** of the 48 unnamed artifacts are named by path in the paper or the plan:

```
runs/e115_r300_40reps.json            naive            runs/e119_r128_test480.json   naive
runs/e116_r128_40reps.json            naive            runs/e119_r300_test480.json   naive
runs/e116_r1307_40reps.json           naive            runs/e123_r128_test480.json   naive
runs/e116_r32_40reps.json             naive            runs/e123_r300_test480.json   naive
runs/e139_r32_wholebody.json          naive, ewc       runs/e142_r32_overlap1_frozen.json   naive
```

Those are the ones a mechanical path search finds; the paper's §8 item 4 row names `e142_r32_overlap1_frozen.json` as
the forty-replicate diagnostic of the harder family, and the registry's only `e142` row is *overlap1 minus base* — so
the frozen-body contrast that row leans on is not one of the 27. **The count the row defends is 27, and what has
outgrown the row is not the count but the population noun under it.**

**U3 MET — and the provenance half is exactly right, to the commit.** `e283` walks every commit that touched the
module and parses the tuple out of each version of the source:

| commit | date | rows |
|---|---|---|
| `a574d3bc` | 2026-09-24 | 27 |
| `59f85dd0` | 2026-09-24 | 22 |

Two commits, both that day, 36 minutes apart: 22 then 27, as the sentence says. **This is the series' first leg that
passes on a positive control built from git** — and it is worth having beside the two that fail, because it separates
"the sentence is wrong" from "the sentence is unverifiable".

## 3. The correction, and a census that moved because of it

The paper's row now carries a **Corrected 2026-09-28** clause naming the exchanged nouns (22 arms, 27 contrasts) and
scoping the *every* to the fourteen it names plus the ten the record names outside it;
`e151`'s own docstring now says the catalogue is a snapshot bounded by the day it was last edited.

**And the correction moved a number in `e282`, which is worth recording rather than hiding.** `e282` measured the paper
at **426 sentences / 368 checkable** earlier this fire; the clause appended here is one more sentence by `e282`'s own
split, so the same instrument now reads **427 / 369**. Every correction this series writes is itself a checkable
sentence, so the denominator `e282` measured grows by exactly the audit's own output — the coverage figure is a moving
target that this line moves. The two findings' readings are each true of the paper as it stood when they were taken,
and the artifact `runs/e282_the_coverage_of_the_series.json` has been regenerated so that it and the paper agree.

## 4. What it cannot do

**"A forty-replicate arm" is read from the artifact's `methods` block**, so an arm that ran forty replicates without
recording a list of them is invisible, and a list-shaped `methods` field (one artifact has one) is not read. **"Named
by the record" is a path search over the paper and the plan and not over the findings**, which name artifacts too, so
the ten artifacts reported are a **lower bound** on the registry's misses and the true figure is larger. **The corpus
scan reads every `runs/*.json` and skips a file it cannot parse without saying so.** **Git is read as it exists now**,
so a history rewrite would move U3 without the paper moving — the leg is exactly as reliable as the repository's own
history, which is the point of a provenance check and also its limit. **And nothing here says the unregistered
contrasts are wrong to leave out**: `e151`'s registry is a list of the contrasts the record *quotes*, and this unit
does not check the quotes — only that the sentence's *every* does not hold over the corpus at forty replicates.
