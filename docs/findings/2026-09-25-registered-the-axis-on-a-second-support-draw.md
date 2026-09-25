# Registered: the overlap axis on a SECOND support draw, because every artifact so far shares one

**Date:** 2026-09-25
**Registered before its runs, and launched from this registration.** The overlap axis is complete and all six of its
shape and cost claims are decided (`docs/findings/2026-09-25-the-axis-is-complete-and-the-two-terms-cross.md`) — and
**it rests on a single draw of which neurons each task drives.** `make_overlap_suite` built its supports with
`--seed0`'s default and there was no flag to vary it, so every level, both families and every endpoint in this
project's overlap record share one realization of the x-axis. Today's finding named exactly that as the axis's real
gap, in place of the overlap table it had wrongly blamed:

> what is unrecorded is the supports' **identity**, which does depend on the circuit and the seed and is recorded in
> no artifact.

This registers the replication of that draw's headline results, with the draw named.

---

## 1. What the flag changes, and what it makes checkable

`--support-seed` now exists (default `--seed0`, so every artifact written before it still identifies its draw), and
every overlap artifact records a `support_draw` block:

```json
{"draw_seed": 1, "fingerprint_sha1": "dd2e42ea3e0f", "n_per_support": 80}
```

**The fingerprint is read off the tasks the run actually used** (`RateTask.input_neurons`), not recomputed from the
construction — so it cannot describe a draw the run did not use. Two overlap artifacts are now comparable on the
x-axis exactly when their `support_draw` agrees, which is the check `partition_draw` has given the matched-random
control since `e168` (`docs/findings/2026-09-24-the-random-control-is-a-sample-and-31-of-38-artifacts-do-not-say-which.md`)
and which the supports never had.

**The x-axis itself needs no recomputation between draws**: the achieved Jaccard is `o/(2−o)` by construction for any
seed, which is the correction in
`docs/findings/2026-09-25-the-x-axis-is-arithmetic-not-a-measurement.md`. What changes across draws is which neurons
each task drives, and that is the thing being varied here.

## 2. The design

Three commands, everything but three flags copied from `e193`'s level-0.50 config so the only differences are the
manipulation, the draw and the arm list:

```
experiments/e8_rate_network.py --circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --train 96 --test 48 \
  --classes 4 --support 80 --shared-head --readout-size 32 --fisher-batches 32 --basis cell_class \
  --seed0 0 --support-seed 1 --methods naive --repeats 40 \
  --input-overlap {0.0, 0.5, 1.0} --json-out runs/e195_r32_ovl{000,050,100}_ss1_naive_40reps.json
```

`naive` only, because every registered claim on this axis is stated on `naive` — the P1/P2 pair, S1-S6 and the cost
decomposition. The penalised arms' family reads against `e153` at overlap 1.0, and **an overlap-1.0 run also draws its
shared population from the seed**, so replicating that family needs its own draw-1 anchor and is deliberately out of
scope here.

**Cost (rule 49)**: `naive` runs at 20–27 s per arm-replicate on this circuit, so 40 replicates is **13–18 min per
command** and the whole design is **about 45–55 min**, measured from `e193`'s own heartbeats rather than from the
per-level average that the block arms dominate. A probe at `--circuit-size 300`, one replicate, ran in 5 s and wrote
the block in §1.

**The read**: `e191 --dose` and `e188 --dose` with the draw-1 artifacts as `--baseline`/`candidates`/`overlap1`, and
`e194` with the same, because the admission rule **will and should refuse** a draw-1 level against a draw-0 baseline:
`support_seed` is not an inert field. That threading is part of this unit, so the claims are read by the same three
commands at a second draw rather than by hand.

## 3. The claims, and what each competing reading predicts

**R1 — the fitting deficit replicates.** At achieved 0.3333 on draw 1, `naive`'s `learned (older)` against the draw-1
overlap-0.0 baseline is **at or below −0.0200**, i.e. at least 62% of draw 0's −0.0326 ± 0.0040 (8.10σ).
**Falsifier**: above **−0.0100** — the deficit is then a property of draw 0's particular supports rather than of the
overlap, and the 8.10σ becomes a one-draw result. **Null worth keeping**: between −0.0200 and −0.0100, a deficit of
the same sign at half the size, which would leave *that the interior costs fitting* standing and its magnitude
draw-dependent.

**R2 — the two terms' shapes replicate.** At achieved 0.3333 on draw 1, the distant-pair progress minus the
adjacent-pair progress is **at least 40 points** (draw 0: 62.1, with the far term at 82.1% and the near at 20.0%).
**Falsifier**: below **15 points**, i.e. the two terms move together at the midpoint and draw 0's 62-point separation
was one draw's arrangement. **Null worth keeping**: a 15–40 point gap — the separation is there but half as large.

**R3 — the interior/endpoint split replicates.** At overlap 1.0 on draw 1, the cost is retention-dominated:
`forgetting` is **at or above +0.0200** (draw 0: +0.0318, 2.99σ) **and** `learned (older)` is within **±0.0100** of
zero (draw 0: +0.0010, 0.33σ). **Falsifier**: either forgetting below +0.0100 **or** `learned (older)` beyond
±0.0150 in either direction — the latter would say the endpoint costs fitting too, collapsing the split the completed
axis reports. **Null worth keeping**: forgetting resolved but `learned (older)` at 1–2σ with the same sign as the
interior's, i.e. the two components are present at both ends at different sizes rather than separated.

All three are read at the **same** achieved overlaps as their draw-0 counterparts, which is exact rather than
approximate because the axis is `o/(2−o)` at any seed.

## 4. What this cannot do

- **Test the penalised family.** §2.
- **Average over draws.** Three artifacts at one alternative draw give a **between-draw difference** and not a
  between-draw **sd**: two draws cannot separate a draw effect from the seed stream, and rule 10's answer is many
  draws averaged, which this design does not pay for. So the honest form of every verdict is *"the effect is present /
  absent at a second draw"*, never *"the effect has a draw-independent size"*.
- **Replicate the full five-level shape.** Three targets (0.0, 0.5, 1.0) test the midpoint and both ends; the 0.1429
  and 0.6 points have no draw-1 counterpart, so the *shape between* them is not replicated here.
