# E10a — the synapse granularity ladder hits a memory wall, and the network basis negative is untested in the interval that matters

**Date:** 2026-09-22
**Script:** `clfly/network/fisher.py` (`SynapsePartition.from_labels`), driven through `experiments/e8_rate_network.py`
**Artifacts:** `runs/e10_smoke.json` (aborted), the granularity map below is from a direct partition construction

---

## 1. Why this experiment exists

E3b's ladder established a trap: **an annotation vocabulary can hide the very effect it is
supposed to measure, by placing its rungs where the effect is small.** Four of the five
neuron-level annotation rungs sat in the top 15% of the constrained range, and reading the
biological contribution off them produced a headline ("granularity beats biology") that the
ladder overturned.

The network line has the same shape of exposure. Its result — **the biological synapse
partition never beats a size-matched random one, in five settings tested** — was measured
with `--basis cell_class` in every one of those settings. If `cell_class` is one point on a
granularity curve, then that negative is a statement about one granularity, not about
biological synapse structure. E3b says this is exactly how a project talks itself into the
wrong headline, so the curve has to be traced.

It is not traceable with the current construction. This finding records why, with numbers,
so that the negative is not quietly upgraded into a stronger claim than it earned.

## 2. The granularity map

Circuit `mb+cx+al@n1307`, 26,568 trainable recurrent weights, full parameter-pair matrix
7.06e8 entries. Constructing the partition only — no training:

| column | `pool_below` | groups | median | largest | constrained | block entries | GB |
|---|---|---|---|---|---|---|---|
| `cell_class` | 0 | 100 | 36 | 5509 | 0.9250 | 52,950,862 | 0.424 |
| `cell_class` | 32 | 61 | 108 | 5509 | 0.9245 | 53,303,650 | 0.426 |
| `cell_class` | 128 | 28 | 462 | 5509 | 0.9027 | 68,701,142 | 0.550 |
| `cell_type` | **0** | 19,618 | 1 | 421 | **0.9992** | 553,934 | **0.004** |
| `cell_type` | **2** | 361 | 9 | 16,342 | **0.6165** | 270,671,420 | **2.165** |
| `cell_type` | 4 | 96 | 22 | 19,487 | 0.4567 | 383,507,748 | 3.068 |
| `cell_type` | 8 | 45 | 38 | 20,535 | 0.3973 | 425,420,504 | 3.403 |
| `cell_type` | 16 | 38 | 49 | 20,758 | 0.3842 | 434,638,236 | 3.477 |
| `cell_type` | 64 | 9 | 565 | 22,233 | 0.2946 | 497,941,052 | 3.984 |
| `cell_type` | 128 | 4 | 1008 | 24,138 | 0.1713 | 584,957,960 | 4.680 |

Two facts from this table decide the experiment.

**Sweeping `pool_below` on `cell_class` does not sweep granularity.** `cell_class` goes from
0.9250 at `pool_below = 0` to 0.9027 at `pool_below = 128` — the entire sweep moves
`constrained_fraction` by 0.02. Cell classes are large, so almost nothing falls below any
reasonable threshold. The published negative therefore sits at one granularity, full stop,
and the obvious-looking sweep would have been a sweep in name only.

**On `cell_type` the granularity range is real but the interesting part is unaffordable.**
`pool_below = 0` gives 0.9992 constrained and costs 0.004 GB — but with median group size 1
it *is* the diagonal wearing a finer label, which `fisher.py`'s own docstring already warns
about, and a diagonal-Fisher baseline is not a granularity test. The next available step,
`pool_below = 2`, jumps to 0.6165 constrained and **2.165 GB**. There is nothing between
0.6165 and 0.9992, and the coarse side costs 3–4.7 GB.

## 3. The wall is one block

The storage is `sum_g s_g^2`, and pooling concentrates it:

| column | `pool_below` | entries | largest group | **share of all storage in that one block** |
|---|---|---|---|---|
| `cell_type` | 0 | 553,934 | 421 | 32.0% |
| `cell_type` | 2 | 270,671,420 | 16,342 | **98.7%** |
| `cell_type` | 4 | 383,507,748 | 19,487 | **99.0%** |
| `cell_type` | 16 | 434,638,236 | 20,758 | **99.1%** |
| `cell_type` | 64 | 497,941,052 | 22,233 | **99.3%** |

The mechanism is structural, not incidental. `from_labels` merges every label below the
threshold into **one shared label**, and the partition is built on ordered `(pre, post)`
label pairs — so that merge creates a single `(pooled, pooled)` group holding every synapse
between two rare cell types. On this circuit that group has 16,342 of the 26,568 synapses at
`pool_below = 2`, and its block alone is 2.14 GB of the partition's 2.165 GB. Pooling
harder makes it bigger: raising the threshold moves synapses *into* the giant block rather
than splitting them, so the memory cost is monotone in exactly the direction the ladder
needs to go.

`cell_class` shows the same concentration more mildly — one block holds 57% of its storage
— but it is stable across `pool_below`, so there it costs nothing to live with.

## 4. Consequence for the network negative

**The negative is real where it was measured and untested where it matters.** The claim that
holds is: *at `cell_class` granularity (0.925 constrained), a biological synapse partition
does not beat a size-matched random one, in any of the five settings tested.* The claim that
does **not** hold — and which earlier drafts of the network line came close to making — is
*biology does not help synapse anchoring, at any granularity.*

This is the same confound E3b found on neurons, and it is now recorded before the neuron
result could be used to argue the network result is settled. The two lines disagree, and part
of that disagreement may be the rung, not the substrate.

## 5. The workaround, not yet implemented

The wall is an artefact of merging into **one** group. Merging into ``B`` buckets instead
(split the sub-threshold labels round-robin, or by a hash) turns the single oversized
`(pooled × pooled)` block into ``B^2`` blocks of a ``B``-th smaller side, so storage falls
roughly as ``1/B``: at `pool_below = 2` and ``B = 16`, the 2.14 GB block becomes ~0.13 GB and
the whole mid-granularity range opens up. The buckets carry no biological meaning, which is
the point — they exist only to keep the block-diagonal projection's storage bounded, and the
matched-random control is built from the same bucket structure so the comparison stays
capacity-matched.

Until that lands, no granularity sweep on synapses should be reported, and the network basis
result should be quoted with its granularity attached.

## 6. Limits

- One circuit (d = 1307) and one annotation vocabulary; the specific group sizes are
  configuration-specific, though the mechanism (one shared pooled label → one quadratic
  block) is not.
- The granularity map is from the partition constructor only. It makes no claim about how
  accuracy or forgetting would move across the sweep — that is the experiment the wall is
  blocking, and it has not been run.
- `constrained_fraction` is a storage proxy for granularity, as throughout; it ignores which
  pairs are grouped, which is why the matched-random control is still required at every rung.
