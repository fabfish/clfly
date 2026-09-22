# E10b — the "time wall" on the coarse synapse rung was a per-step conversion, not a scaling cost

**Date:** 2026-09-22
**Script:** `clfly/network/fisher.py` (`make_penalty`), `experiments/e8_rate_network.py`
**Artifacts:** measured below; the e10 sweep restarted on the fixed code

---

## 1. The claim this revises

`docs/findings/2026-09-22-synapse-annotation-ladder.md` §4 concluded: *"What is blocked is
time, not memory"* — that a coarse synapse partition is expensive because the block Fisher's
cost scales with ``sum_g s_g^2``, so it takes minutes per run where `cell_class` takes
seconds. The first half of that survives. The second half does not.

The `side` rung (1.72 GB, 2.16e8 block entries) ran for ~15 minutes and had produced a single
method arm. Diagnosis: `SynapsePartition.penalty_tensor` is called **once per training step**
and converts every block from numpy to ``torch`` on each call:

```python
blk = torch_mod.from_numpy(blocks[off:off + s*s].reshape(s, s)).to(dtype).to(device)
```

For `side` that is **1.72 GB of copying per step**, and a 3-task × 3-repeat × 500-iteration
`ewc-block` run makes 4,500 such calls. The Fisher and the anchor are *constants* while a task
is trained, so all of that copying was waste — and it had nothing to do with granularity. The
scaling cost was real but was being paid a second time, per step.

## 2. The fix

`SynapsePartition.make_penalty(blocks, anchor, theta, lam, torch_mod)` binds the three
constants into a ``theta -> penalty`` callable, converting each block and the anchor **once**.
It is called once per task in `run_method`, outside the step loop.

The arithmetic is unchanged: the same `d @ (blk @ d)` per group, summed in the same order, at
the same dtype. A test asserts the two paths agree **bit for bit** at λ ∈ {0, 0.003, 1.0}.

`penalty_tensor` is kept rather than replaced: it is the honest thing to reach for when the
blocks *do* change every step, and a silent behavioural difference between two similarly-named
penalties would be worse than a slightly longer call. Its docstring now says not to call it in
a loop.

## 3. Measured

`d = 1307`, 26,568 synapses, ``theta`` float32, blocks float64, three calls each after warm-up:

| column | block entries | storage | bind | per-step before | per-step after | speedup | penalty time per 4,500-call run |
|---|---|---|---|---|---|---|---|
| `cell_class` | 52,950,862 | 0.42 GB | 0.095 s | 0.0580 s | 0.0513 s | 1.1× | 4.4 → 3.8 min |
| `side` | 215,532,832 | 1.72 GB | 0.200 s | 0.3247 s | 0.0805 s | **4.0×** | **24.3 → 6.0 min** |

The bind costs 0.2 s for the largest rung and is paid three times per run (once per task). The
speedup is 1.1× on `cell_class` and 4.0× on `side` precisely because it is proportional to how
much conversion was being done redundantly — the fine rungs (≤ 0.03 GB) gain almost nothing.

The visible effect is on the sweep the wall was blocking: the earlier `side` arm had not
finished its first block method after ~15 minutes; the restarted sweep is expected to complete
all five rungs in the time the single rung was taking.

## 4. A latent bug found on the way

`penalty_tensor` computed ``theta[idx] - anchor[idx]`` with a numpy ``anchor``, letting numpy
promotion pick the result dtype. Against a float32 ``theta`` that is float32 and works — which
is why it never failed in the benchmark, where ``anchor_b`` happens to be float32 numpy. With a
float64 anchor it raises:

```
RuntimeError: addmv input tensors must have the same dtype, but got Double, Float, and Double
```

The first test I wrote for `make_penalty` used a float64 anchor and hit exactly this. Both paths
now cast the anchor to ``theta.dtype`` explicitly, which also removes a NumPy 2.0
``__array_wrap__`` DeprecationWarning from the same expression. **The benchmark was one dtype
away from a crash that no test covered**, in a module that had no tests at all before this
session — `tests/test_synapse_partition.py` now has 12.

## 5. What this does not change

- Granularity really does cost: `sum_g s_g^2` governs both the accumulation and the memory, so
  a coarse rung still needs GBs of RAM and still does more arithmetic per Fisher estimate. The
  `side` partition's storage is unchanged at 1.72 GB, and `make_penalty` holds the numpy blocks
  and the torch copy at once (≈3.4 GB), which a caller should know.
- The five-rung comparison and its controls are unaffected; the restart reproduces the earlier
  `side` **naive** arm exactly, since that arm never touches the penalty.

## 6. Pattern

This is the third time in this project that a "wall" was an implementation artefact: the
chaotic headline metric (a redundant ratio), the benchmark measuring its decoder (a
non-load-bearing read-out), and now a 4× cost that was pure redundant conversion. In each case
the artefact was load-bearing for a *scientific* conclusion — here, for the belief that the
coarse rung was practically out of reach. Worth checking for directly: when a configuration is
"too slow to test", time the pieces before concluding it is the science that is expensive.
