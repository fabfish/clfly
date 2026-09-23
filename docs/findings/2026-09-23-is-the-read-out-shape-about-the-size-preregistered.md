# `e113`, pre-registered: is the read-out shape about the size, or about which neurons were drawn?

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py` (now with `--readout-seed`), five runs; artifacts
`runs/e113_r300_draw{1,2,3}.json`, `runs/e113_r512_draw1.json`, `runs/e113_r300_draw1_plateau.json` (in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 300 with three independent draws** and **512 with a
second draw**, training seeds held fixed at `--seed0 0`.
**Context:** `docs/findings/2026-09-23-both-metrics-have-an-interior-optimum.md`, the seven-point design
statement, and a property of the runner that none of the last five fires had noticed.

---

## 1. The confound, and it is in the runner rather than in the data

The read-out subset is drawn as

    rs = np.sort(np.random.default_rng(seed0).choice(n_neurons, size=readout_size, replace=False))

**independently for every size.** So `choice(size=300)` is **not** a superset of `choice(size=32)` — the two
draws are unrelated samples of the circuit's 1307 neurons, and the measurement of that is in a test:

| two draws | overlap | chance |
|---|---|---|
| size 300 vs size 300, different seeds | **63–73 of 300** | 69 |
| size 32 vs size 300 | **not nested** (0 of 32 contained) | — |

**So the "read-out axis" is not an axis of inclusion.** It is a sequence of independent random neuron samples of
different sizes, and **every shape claim this sequence has made along it — the whole-state outlier, the interior
minimum at 512, the two-sided bowl, the optimum at 300 — is a shape along a sequence whose points differ from
each other in *two* ways at once**: how many neurons are read out, **and which neurons they are**.

**`--readout-seed` is the control**, and it is the only one that separates them: hold the size, change the draw.
It defaults to `--seed0`, so every artifact written before the flag existed is **bit-identical** under it, which
a test pins.

## 2. What this can do to the previous three fires, stated before the runs

**If the draw matters as much as the size**, then the interior optimum is a property of *which 300 neurons were
drawn* rather than of reading out 300 of them, and the design statement of the previous fire **must be
withdrawn** — along with the "anomaly" language of the two before it, which rested on the same axis. **If the
draw barely matters**, then the axis is about size after all and the design statement stands on much firmer
ground than it did, because it will have survived the control that its own construction was missing.

**Both outcomes are worth this fire, and the second is worth more than a new point would be**: a claim that has
never been tested against the confound its own construction admits is not a claim yet.

## 3. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **P1, the test** | the forgetting across **three independent draws at read-out 300** spans **less than 0.0125** — the across-size difference it is being compared against (512's +0.0208 against 300's +0.0083) |
| **P2, the check at a second size** | the same holds at **512**: two draws there span less than the 0.0125 that separates 512 from its neighbours (700's +0.0354 and 300's +0.0083 — so 0.0146, and the tighter bound is 0.0125) |
| **Falsifier** | a draw-to-draw span of **0.0125 or more** at either size — the draw variation is then as large as the effect, the shape along the axis is confounded with the draw, and the previous fire's design statement is **withdrawn** rather than adjusted |

**The threshold is the effect size, not a significance test**, and that is deliberate: this project's conclusion
is a *design* statement about where a benchmark's optimum sits, so the question is whether the variation a
practitioner could not control (which neurons) is smaller than the variation they can (how many).

**A repeat of one draw** is included for the reason every configuration since `e106` has one: the `naive` arm at
a fixed configuration has reproduced bit-identically at seven executions, and the repeat is what says that the
*training* is deterministic so that any difference between draws is attributable to the draw and not to the
process.

## 4. What this cannot settle

- **Three draws is three samples.** If P1 holds, the honest statement is a range over three draws at one size,
  not a variance; a null result at one size and one read-out does not exclude a draw effect at another.
- **It does not test the whole axis.** Read-out 300 and 512 are the two sizes with a claim resting on them; the
  other five points are not re-drawn, and a full answer would need a second draw at every size — which is the
  right thing to run *if* this fire says the draw matters.
- **`--seed0` still controls the training seeds**, so the draws are compared at fixed training randomness rather
  than at fixed trajectory; a draw that changes the trajectory is a different thing from a draw that changes the
  read-out, and the two are confounded by construction because the read-out determines what the loss sees.
