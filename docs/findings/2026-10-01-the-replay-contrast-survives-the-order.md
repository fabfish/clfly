# The replay-over-penalty contrast survives the order inversion in sign and not in size

*2026-10-01 16:31. Runs: **none new** — `experiments/e321_the_replay_contrast_survives_the_order.py` reads
`runs/e317_five_as_built.json` and `runs/e317_five_reverse.json` — the five-arm reversal this line already made —
writing `runs/e321_the_replay_contrast_survives_the_order.json`. Seconds.*

## 1. The contrast nobody had varied a knob under

`e276` read the line's **strongest method contrast** — `replay` against the penalty arms, paired over the same forty
replicates — at 3.30, 9.09 and 11.84 sigma on accuracy and up to 8.42 on forgetting, every contrast favouring
replay. Eleven fires of audit have left the **basis** contrast a null; this is the contrast that always resolves, and
**nothing had ever varied a knob under it**.

`e317`'s runs supply the knob: the assembly suite at this circuit, all five arms, the same seeds, trained forwards
and backwards. `e317` used them to show that the **block-against-diagonal** comparison flips sign with the order, so
the same question put to `replay`'s three contrasts is the one the line's headline needs.

**T1 MET** — same circuit `mb+cx+al@n952`, same read-out subset `59926518137c`, same seeds, and one task list the
other reversed.

## 2. The sign survives everywhere and the size does not

`delta` is `replay` minus the penalty arm, paired over the five replicates:

| contrast | forwards | sigma | backwards | sigma | ratio |
|---|---|---|---|---|---|
| `replay` − `ewc` / accuracy | +0.1708 | 4.74 | +0.1514 | 4.14 | **1.13** |
| `replay` − `ewc` / forgetting | −0.1854 | 3.72 | −0.1646 | 3.69 | **1.13** |
| `replay` − `ewc-block` / accuracy | +0.2042 | 5.77 | +0.0639 | 3.54 | **3.20** |
| `replay` − `ewc-block` / forgetting | −0.2687 | 4.42 | −0.0896 | 2.31 | **3.00** |
| `replay` − `ewc-block-rand` / accuracy | +0.1153 | 5.92 | +0.1056 | 3.17 | **1.09** |
| `replay` − `ewc-block-rand` / forgetting | −0.1417 | 7.31 | −0.1417 | 3.87 | **1.00** |

**T2 and T3 MET** — all six contrasts favour `replay` in **both** orders and every one resolves at **2.31 sigma or
better**. **T4 MET** — two of the six differ between the orders by a factor of three: `ewc-block`'s accuracy contrast
is **3.20 times** larger forwards than backwards and its forgetting contrast **3.00 times**, while the other four are
within **1.13**.

## 3. What that says

**The line's strongest result is the first of its claims to be tested under the order inversion, and it holds where
the other one broke.** `e317` found the block-against-diagonal comparison **flipping sign** between these same two
runs (+0.07500 at 2.60 sigma against −0.08333 at 2.64). `replay`'s three contrasts do not flip: the order moves their
**size** by up to a factor of three and never their direction or their resolution.

So the two method contrasts the corpus quotes differ in kind under this knob: **one is a coin flip whose sign is the
order's, and one is a real effect whose magnitude is.** A benchmark that permutes its suite's order can still report
`replay` against the penalty arms — with a caveat on `ewc-block`'s size, which is the contrast that moved most and is
also the one whose forwards and backwards readings sit closest to the smallest of the six.

## 4. What it cannot do

**One configuration and five replicates per arm**, so these sigmas are this circuit's and not `e276`'s: that unit's
3.30, 9.09 and 11.84 sigma are the read-out-32 frozen-bias family at **forty** replicates, and nothing here
re-measures them — what it does is vary a knob under this configuration's own version of the contrast. **The two runs
are not the same trained models**, since the sequence changes the gradients, so a magnitude difference is the order's
effect on the whole trajectory. **Six contrasts over three arms are not independent**: they share `replay`'s
replicates, so one unusual `replay` arm moves all six together, which is why T4's factor is a description and not an
estimate. **And T4's factor of two is a convention**: what the run shows is about three on `ewc-block` and about one
on the others.

## 5. RE-READ 2026-10-01: T1's seed check could not fail

Found by `e324` while writing the same check for its own pair of runs, and it is a defect in this unit's instrument
rather than in its result.

**T1 said the two runs share their seeds, and the check behind that sentence was `[None] * n == [None] * n`.**
`runs/e317_five_as_built.json`'s replicates carry `method`, `losses`, `final_accuracy`, `retention`, `theta_drift` and
the rest, and **no seed field at all** -- so `[r.get("seed") for r in replicates]` was five `None`s on each side and
compared equal whatever the two runs' seeds were. The fixture in `tests/test_e321_*.py` had invented a `"seed"` key,
which is why no test caught it: the fixture described an artifact the corpus does not write.

**The claim itself is still true and is now checked against what the artifacts do record.** What identifies a seed
schedule here is `config.seed0` and `config.repeats`, so those are compared, together with the replicate counts, and a
run whose config carries no `seed0` is no longer the same schedule as one that does. `tests/test_e321_*.py` has the
test that can fail -- a differing `seed0`, a differing `repeats`, and an absent one -- and the fixture no longer
invents the field. The verdicts T1 to T4 are unchanged: `runs/e317_*.json`'s two runs share `seed0 = 0` and five
replicates each, and every contrast still favours `replay` in both orders.

**And the same class of defect is worth naming**: a check whose two sides are both empty passes, and a fixture that
is kinder than the corpus hides it. `e324`'s T1 makes the equivalent check on the config for exactly this reason.
