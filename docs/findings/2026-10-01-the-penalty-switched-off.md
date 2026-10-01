# The penalty switched off: the same arm, the same suite, the effect at 4.33 sigma and at 1.00

*2026-10-01 14:21. Runs: **four new** — `runs/e318_lam0_as_built.json`, `runs/e318_lam0_reverse.json`,
`runs/e318_lam1_as_built.json` and `runs/e318_lam1_reverse.json`, written by
`e8_rate_network.py --circuit-size 300 --readout-size 32 --train 96 --test 48 --iters 500 --repeats 5 --methods
naive,ewc` at `--lam 0.0` and `--lam 1.0`, each with `--task-order as-built` and `--task-order reverse`. About two
minutes each.*

## 1. The comparison `e317` said it lacked

`e317` found the reversal's position effect carried by the three arms that read a penalty and absent from the two that
do not, and named its own gap: **no arm is compared with itself**, so "carried by the penalty arms" was a statement
about which arms move and not about the penalty. **This is one arm, one suite, one seed set, with the penalty
dialled** — `ewc` at `lam = 0.0` and `lam = 1.0`, each trained forwards and backwards, with `naive` riding along in
every run as an internal constant.

**S1 MET** — the two settings' configs differ in **`lam` alone**, each penalty's two orders agree on circuit, read-out
and seeds, and each reverses the task list. (A first version of this check reported `json_out` as a configuration
difference; the constant that says the output path is not one was already in the module and the line did not use it,
which is `e185`'s defect in miniature and is now fixed.)

## 2. The reading

`delta` is forwards minus backwards, paired over the five replicates; `ewc`'s two moved contrasts and its control:

| task | position | **`lam = 0.0`** | **`lam = 1.0`** |
|---|---|---|---|
| `odour_identity` | 0 → 2 | −0.0083 (**0.78σ**) | **+0.0917 (2.75σ)** |
| `odour_input` | 2 → 0 | −0.0042 (**1.00σ**) | **−0.1083 (4.33σ)** |
| `heading` (control) | 1 → 1 | +0.0333 (1.97σ), **not smallest** | +0.0250 (0.68σ), **smallest** |

**S2 fired, and it fired on the line**: with the penalty off, `ewc`'s larger contrast is **exactly 1.00 sigma**, so the
claim as registered — *both moved contrasts below one sigma* — is false by the smallest margin the claim allowed, and
what the run says is that the penalty-off arm's position effect is **at most at the detection threshold** and not
absent.

**S3 MET** — with the penalty on, both contrasts clear the line (**2.75** and **4.33 sigma**) and **both** favour the
run that trains the task first. **S4 MET** — the unchanged-position task is the smallest of `ewc`'s three contrasts at
`lam = 1.0` and is **not** at `lam = 0.0`, where it is the *largest* of the three.

## 3. What the four runs say

**The same arm double the effect and double the resolution when its penalty is on.** `ewc` at `lam = 1.0` moves
+0.0917 and −0.1083 with the position; the same arm on the same suite with the same seeds at `lam = 0.0` moves
−0.0083 and −0.0042, and its control stops being the quiet contrast. So `e317`'s reading survives the controlled
version: what the position effect needs is the **penalty term**, and an arm that reads one carries it while the same
arm without one does not.

That also sharpens the benchmark warning these four runs and the three before them produce: **an order permutation
changes the penalty arms' numbers and leaves the penalty-free arms alone**, so a methods table whose suite order is
permuted is not comparing the same things across rows.

## 4. What it cannot do

**Two penalty strengths on one suite and five replicates**, so this is on against off and not a dose-response curve,
and the off-setting's 1.00 sigma is a threshold crossing this run does not resolve either way. **`lam = 0.0` is not
the same code path as `naive`** — the arm still computes a Fisher and multiplies it by zero — so "the penalty off"
means the penalty term is zero and not that the run is `naive`, and `naive`'s own contrasts are unchanged across the
two settings only because it does not read `lam`. **The four runs are not the same trained models**, since both the
penalty and the order change the gradients, and `ewc`'s two settings share a suite and a seed set and not a
trajectory. **And one arm was dialled**: `ewc-block` and `ewc-block-rand` read a penalty through a partition and
nothing here dials theirs.
