# The penalty four times: the effect is a threshold and not a dose, and `naive` is bit-identical at every setting

*2026-10-01 15:07. Runs: **eight new** — `runs/e319_lam{0p0,0p1,1p0,3p0}_{asbuilt,reverse}.json`, written by
`e8_rate_network.py --circuit-size 300 --readout-size 32 --train 96 --test 48 --iters 500 --repeats 5 --methods
naive,ewc` at four `--lam` values, each with `--task-order as-built` and `--task-order reverse`. About two minutes
each.*

## 1. The gap `e318` named

`e318` compared the penalty **on against off** on one arm and wrote in its own limitations that this *"is on against
off and not a dose-response curve"*. This unit dials the penalty four times — `lam` = **0.0, 0.1, 1.0, 3.0** — on the
same suite, the same circuit, the same read-out and the same seeds, with `naive` riding along in every one of the
eight runs as a constant.

**D1 MET** — each penalty's two orders agree on circuit, read-out and seeds and reverse their task lists, and the
four settings' configs differ in **nothing** outside `lam`, the output path and the order.

## 2. The sequence, and the two claims it fired

`ewc`'s moved-position contrasts at each penalty:

| `lam` | median sigma | the two contrasts | control smallest |
|---|---|---|---|
| **0.0** | **0.89** | −0.0083 (0.78σ), −0.0042 (1.00σ) | no |
| **0.1** | **3.73** | +0.0667 (**4.82σ**), −0.0708 (2.64σ) | yes |
| **1.0** | 3.54 | +0.0917 (2.75σ), −0.1083 (4.33σ) | yes |
| **3.0** | 3.99 | +0.0708 (3.67σ), −0.1125 (4.32σ) | yes |

**D2 FIRED** — the sequence is **not** non-decreasing: 0.89 → **3.73** → **3.54** → 3.99. So the effect does not
grow with the penalty: it **saturates at the first step**, `lam = 0.1`, and stays flat to within the wobble five
replicates put on a contrast (4.82 at 0.1 against 2.75 at 1.0 for the same contrast).

**D3 FIRED** — three of the four penalties have both contrasts above the line and **none** has both below, because
the one that would is `lam = 0.0` and its larger contrast sits **exactly on it** at 1.00 sigma, which is the same
line-crossing `e318` found. So the range contains the crossing only in the degenerate sense.

**D4 MET** — **7 of 7** contrasts clearing one sigma favour the run that trains the task first, including `lam = 0.0`'s
1.00-sigma one. Wherever the effect resolves, it points the position's way.

## 3. And the constant did not move at all

`naive`'s two moved contrasts, at every one of the four settings: **0.78 and 1.00 sigma, identical to six decimals in
all four runs.** That is the design's own check: `naive` does not read `lam`, the runner is deterministic given the
seeds, and the four settings share their suite and their seed set — so an arm that ignores the dial is untouched by
it, while the arm that reads it moves from 0.89 to 3.73 sigma on the first notch.

**What the axis now says, from `e315` to `e319`.** Reversing a suite's order moves the level of a task by up to four
points of accuracy; it moves the arms that **read a penalty** and leaves the arms that do not alone; it needs the
penalty term, since the same arm at `lam = 0.0` moves 0.78 and 1.00 sigma and at `lam = 1.0` moves 2.75 and 4.33; and
the penalty's **strength** does not matter past its first notch, because 0.1 already buys 4.82 sigma. So the effect is
a property of *whether* an arm regularises toward a basis and not of how hard.

## 4. What it cannot do

**Five replicates per contrast**, so the 3.73 against 3.54 step is inside the noise of a single contrast and D2's
firing is a sign test on three steps, not a curve: what the sequence shows is saturation and not a decrease.
**`lam = 3.0` is above everything the corpus ran before**, so the top of the range is a new regime. **One arm is
dialled**: `ewc-block` and `ewc-block-rand` read a penalty through a partition and nothing here dials theirs. **The
runs are not the same trained models**, since `lam` changes the gradients, so a difference across settings is the
penalty's effect on the whole trajectory. **And `lam = 0.0` is not `naive`**: the arm still computes a Fisher and
multiplies it by zero, which is why it is held at the threshold rather than absent.

## 5. And it fired `e267`'s S2

`e267` read the corpus for matrices whose **every** arm sits inside its own test-set floor — configurations the
144-item suite cannot separate from its own noise — and registered S2 as *"a whole configuration inside its own floor
is rare and named"*, with more than a few as the falsifier. **The penalty-free runs this unit made are exactly that**:
`lam = 0.0` on the assembly suite at 144 items is a matrix whose arms are all inside their floors, and the list of such
matrices grew past what the claim called rare. So **S2 has fired** and `e267` now reports the named set rather than a
count that is supposed to be small — one more consequence of adding a run rather than of an error
(`docs/findings/2026-09-28-the-test-set-the-benchmark-would-need.md`).
