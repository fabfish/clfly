# E10a — the synapse annotation ladder has five rungs, only one of which has ever been run

**Date:** 2026-09-22
**Script:** `clfly/network/fisher.py` (`SynapsePartition.from_labels`), driven through `experiments/e8_rate_network.py`
**Artifacts:** `runs/e10_rung_*.json` (in flight), `runs/e10_smoke.json` (aborted)

---

## 1. Why this experiment exists

E3b's ladder established a trap: **an annotation vocabulary can hide the very effect it is
supposed to measure, by placing its rungs where the effect is small.** Four of the five
neuron-level annotation rungs sat in the top 15% of the constrained range, and reading the
biological contribution off them produced a headline ("granularity beats biology") that the
ladder overturned.

The network line has the same exposure. Its result — **the biological synapse partition never
beats a size-matched random one, in five settings tested** — used `--basis cell_class` in
every one of those settings. If `cell_class` is one point on a granularity curve, that
negative is a statement about one rung, not about biological synapse structure.

## 2. The ladder is real, it has five rungs, and only the second-coarsest has been tested

Circuit `mb+cx+al@n1307`, 26,568 trainable recurrent weights, full parameter-pair matrix
7.06e8 entries. Partition construction only, no training:

| annotation column | labels | groups | largest | constrained | GB | neuron-level constrained (E3) |
|---|---|---|---|---|---|---|
| `side` | 4 | 10 | 10,126 | **0.6947** | 1.724 | 0.501 |
| `cell_class` | 12 | 100 | 5,509 | **0.9250** | 0.424 | 0.828 |
| `ito_lee_hemilineage` | 212 | 2,148 | 601 | 0.9945 | 0.031 | 0.967 |
| `supertype` | 508 | 9,938 | 452 | 0.9988 | 0.007 | 0.974 |
| `cell_type` | 812 | 19,618 | 421 | 0.9992 | 0.004 | 0.979 |

**The rung ordering is identical to the neuron-level ordering** — `side`, `cell_class`,
hemilineage, supertype, cell_type — which is a reassuring consistency check between the two
substrates, since the synapse partition is built on `(pre, post)` label pairs and the neuron
partition on the labels themselves.

Two things follow immediately.

**The published negative sits at 0.9250, and the rungs that are cheap cluster at the fine
end.** Three of the five rungs (hemilineage 0.9945, supertype 0.9988, cell_type 0.9992) cost
under 0.04 GB each and are all closer to the diagonal than to the coarse end. That is the
same crowding E3b found on neurons, reproduced on synapses: **the affordable rungs are
precisely the uninformative ones.**

**The coarsest rung is untested, and it is the one the neuron result implicates.** On neurons,
`side` was the strongest rung (28.8σ at 18 seeds) and the most valuable anchoring basis the
vocabulary offered. On synapses it has never been run. It costs 1.72 GB, which is not a wall
on this machine — see §4.

## 3. The `pool_below` dial is not a substitute, and bucketing does not open the middle

`from_labels(..., pool_below=N)` merges labels appearing in fewer than `N` neurons, which
looks like the neuron ladder's pooling device. Three facts rule it out as the ladder here.

**On `cell_class` it does not sweep anything.** `constrained_fraction` moves from 0.9250
(`pool_below = 0`) to 0.9027 (`pool_below = 128`) — by 0.02. Cell classes are large, so almost
nothing falls below any threshold. A sweep in name only.

**On `cell_type` the interesting interval is not reachable.** `pool_below = 0` gives 0.9992
constrained and costs 0.004 GB, but with median group size 1 it *is* the diagonal wearing a
finer label — `fisher.py`'s own docstring already warns about this, and a diagonal-Fisher
baseline is not a granularity test. The next available step, `pool_below = 2`, jumps to 0.6165
constrained and 2.165 GB. There is nothing between 0.6165 and 0.9992, and the coarse side
costs 3–5 GB (3.984 GB at `pool_below = 64`, 4.680 GB at 128).

**Why the coarse end is expensive is the same reason it is coarse.** The storage is
``sum_g s_g^2``, and `from_labels` merges every sub-threshold label into **one** shared label,
so the ordered `(pre, post)` construction creates a single `(pooled, pooled)` group holding
every synapse between two rare cell types:

| column | `pool_below` | entries | largest group | share of all storage in that one block |
|---|---|---|---|---|
| `cell_type` | 0 | 553,934 | 421 | 32.0% |
| `cell_type` | 2 | 270,671,420 | 16,342 | **98.7%** |
| `cell_type` | 4 | 383,507,748 | 19,487 | **99.0%** |
| `cell_type` | 16 | 434,638,236 | 20,758 | **99.1%** |
| `cell_type` | 64 | 497,941,052 | 22,233 | **99.3%** |

Pooling harder moves more synapses *into* the giant block rather than splitting it, so cost is
monotone in exactly the direction the ladder needs.

**Bucketing bounds the cost and pays for it in granularity, so it cannot reach the middle.**
`pool_buckets=B` splits the merged mass over `B` groups, turning the oversized block into
`B^2` blocks of a `B`-th the side each:

| `pool_below` | B | groups | largest | constrained | GB |
|---|---|---|---|---|---|
| 2 | 1 | 361 | 16,342 | 0.6165 | 2.1654 |
| 2 | 4 | 871 | 1,097 | **0.9744** | 0.1446 |
| 2 | 16 | 2,093 | 421 | 0.9975 | 0.0140 |
| 4 | 4 | 270 | 1,341 | 0.9643 | 0.2015 |
| 8 | 4 | 114 | 1,387 | 0.9606 | 0.2222 |

Storage falls roughly as `1/B`, and `constrained_fraction` rises back toward the diagonal by
almost as much — at `B = 4` the partition is *finer than `cell_class`*. Bucketing is not a way
to be coarse and cheap; it converts one coarse group into `B` finer ones, which is the
opposite of what the ladder needs. It is implemented and tested anyway
(`tests/test_synapse_partition.py`, 10 tests) because it does bound storage for anyone who
wants the fine-to-mid range, and because the negative result is worth having on the record.

## 4. What is blocked is time, not memory

> **Revised.** The *time* claim survives; the reason for it does not. A 4× share of this cost
> was a per-training-step numpy→torch conversion of the whole Fisher that had nothing to do
> with granularity, and is now bound once per task — see
> `docs/findings/2026-09-22-penalty-bound-once.md`. Granularity really does cost, but less than
> this section implies.

The machine has 33.6 GB, so 2.165 GB — or even 4.68 GB — is not a wall. The binding constraint
is the block Fisher's **accumulation cost**, which also scales with ``sum_g s_g^2``: one block
of 16,342² is 2.7e8 multiply-adds per accumulation, and there are `fisher_batches` × tasks of
them, twice over for the matched-random control. Concretely, `e8_rate_network` at
`pool_below = 16`, 100 iterations, one repeat, did not finish its `ewc-block` arm within 270 s,
while the same script runs a full 3-task × 3-repeat × 500-iteration suite at `cell_class` in
about 4 minutes.

So the honest statement is: **a coarse rung costs minutes per run rather than seconds, and that
is affordable.** `side` is 1.72 GB — half of the `pool_below = 16` configuration that was too
slow — so it is the natural first target, and it is also the rung with the strongest
neuron-level precedent.

## 5. Consequence for the network negative

**The negative is real where it was measured and untested at the rung that matters.** What
holds: *at `cell_class` granularity (0.9250 constrained), a biological synapse partition does
not beat a size-matched random one, in any of the five settings tested.* What does **not**
hold, and which earlier drafts came close to writing: *biology does not help synapse anchoring,
at any granularity.*

This is the same confound E3b found on neurons. It is recorded here before the neuron result
could be used to argue the network result is settled — the two lines disagree, and part of
that disagreement may be the rung rather than the substrate.

**In flight:** `e8_rate_network --basis {side, cell_class, ito_lee_hemilineage, supertype,
cell_type} --methods naive,ewc-block,ewc-block-rand --iters 500 --repeats 3`, one JSON per
rung at `runs/e10_rung_*.json`, which is the first synapse basis comparison to be run at more
than one granularity.

## 6. Limits

- One circuit (d = 1307) and one annotation vocabulary. The group sizes are
  configuration-specific; the mechanism (one shared pooled label → one quadratic block) is not.
- The maps in §2 and §3 come from the partition constructor only. They make no claim about how
  accuracy or forgetting move across the rungs — that is the experiment, and at the time of
  writing it has not reported.
- `constrained_fraction` is a storage proxy for granularity, as throughout; it ignores *which*
  pairs are grouped, which is why the matched-random control is still required at every rung.
- `--normalise-fisher` (on by default) matters more at coarse rungs, since a bigger block gets
  a larger unnormalised penalty at the same λ. Any cross-rung comparison must keep it on.
