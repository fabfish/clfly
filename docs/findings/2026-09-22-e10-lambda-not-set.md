# E25 — the rung ladder runs at a λ outside the project's own swept range, and the "reproducibility check" was not one

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py` (config audit), `runs/e25_cell_class_lam0.003.json` (launched)
**Artifacts:** `runs/e10_rung_side.json`, `runs/e10_rung_cell_class.json`, `runs/e8_basis.json`, `runs/e8_tuned_lambda.json`

---

## 1. What I set out to do, and what went wrong

`e10`'s `cell_class` rung finished, and I read it as a **reproducibility check on the published
network negative** — the same basis, the same 3 repeats, the same 500 iterations. Its numbers
differed substantially from `runs/e8_basis.json`:

| method | published (`e8_basis`) | new (`e10_rung_cell_class`) |
|---|---|---|
| `naive` | 0.8241 | **0.8241** |
| `ewc-block` | 0.7755 | **0.8426** |
| `ewc-block-rand` | 0.8403 | **0.8611** |

The `naive` arm is **bit-identical**, which proves the seeds, task draws and model initialisation
are identical between the two runs — so the divergence had to be in the block-EWC path, which is
the code I had just optimised for speed. I spent the first half of this fire testing that
suspicion, and it was **wrong**:

- `make_penalty` against `penalty_tensor`, 20 training steps from identical initial conditions and
  an identical data order: **max |loss difference| = 0.0**, trajectories bit-identical. The
  optimisation is sound.
- The actual cause is in the configs, and a config diff takes one line: **`lam` is 0.1 in the
  published run and 1.0 in mine.**

So the intended comparison was never valid. `naive` matches because λ cannot affect a method that
has no Fisher. Nothing else was wrong.

## 2. The consequence is larger than the mistaken comparison

**λ = 1.0 is outside the range this project has swept, and it is not a setting anyone chose.**
It is the argparse default, and `e10`'s runs never passed `--lam`.

| artifact | λ | Fisher batches |
|---|---|---|
| `e8_basis` (published basis comparison) | 0.1 | 8 |
| `e8_tuned_lambda` (the sweep) | 0.003–0.3 | **32** |
| `e8_hardened_basis` (the hardened config) | 0.003 | 8 |
| **`e10_rung_side`, `e10_rung_cell_class`** | **1.0** | 8 |

The sweep's own conclusion is that **λ matters enormously and 0.003 is the only useful setting**,
with every λ ≥ 0.01 leaving EWC worse than naive on both metrics. So the two completed rungs of the
synapse ladder test the rung question at a λ the project has already characterised as
over-constrained — and a null there **is confounded with λ**. It cannot be read as "the rung is not
the problem".

## 3. And the λ story is not as settled as that conclusion suggests

Two things in the same comparison break the monotone reading:

| λ (batches 32, single seed, naive 0.896) | block — biological |
|---|---|
| 0.003 | 0.910 |
| 0.01 | 0.792 |
| 0.1 | 0.833 |
| 0.3 | 0.819 |

λ = 0.1 is *worse* than both 0.003 and 0.3 — the dependence is **not monotone**. And in the new
run at **λ = 1.0** the block methods are *better* than naive on both accuracy (0.8426, 0.8611
against 0.8241) and forgetting (+0.0590, +0.0347 against +0.1007), which the "λ ≥ 0.01 is
over-constrained" summary does not predict.

Two further differences make the two runs incomparable even beyond λ: `e8_tuned_lambda` used
**fisher_batches = 32** against `e10`'s 8 (and the fisher-batches finding established that more
batches is effectively a *stronger* penalty at fixed λ), and its **naive baseline is 0.896** against
e10's **0.8241**, which means the two used different task draws.

So neither the λ sweep nor the rung ladder can be compared across configurations as they stand, and
"0.003 is the only useful setting" is a statement about *that* configuration at *one seed*.

## 4. What I am doing about it

`runs/e25_cell_class_lam0.003.json` is running: the same `cell_class` configuration as `e10`, 3
repeats, 500 iterations, at **λ = 0.003**. With λ = 1.0 already measured, that gives a two-point λ
arm on the *same* seeds, task draws, batch count and repeats — the comparison the project has never
had. It costs ~35 minutes.

The rung ladder's other rungs should not be read as rung-level evidence until that lands. If λ = 0.003
turns the `cell_class` rung around, then `C2b`'s conclusion inverts and the rung question is live
again; if it does not, the null survives the λ arm and is much stronger for it.

## 5. The process lesson, which is the durable part

**A run that never passes a hyperparameter is not measuring at "the default" — it is measuring at a
value nobody inspected.** The λ axis had been swept, written up, and drawn a conclusion from; the
rung ladder then ran 300× above the recommended value for two rungs because it never set the flag,
and the mistake survived a `git log` of the script, a reading of the config dict, and being
described in a finding as a "reproducibility check".

What caught it was **comparing two artifacts' configs field by field**, which is a one-line script
and should be the first thing done whenever two runs are compared. The cheaper lesson: a benchmark
whose config contains 24 fields and whose conclusion depends on three of them should print the
relevant ones in the results table, not bury them in a JSON blob.

## 6. Limits

- The λ = 1.0 result is 3 repeats, so its "better than naive" is within noise (both deltas ~0.4σ).
  Its *sign* should not be read as a finding; its *existence* is what matters, as a demonstration
  that the λ dependence is not monotone in the sense the sweep's prose implies.
- The `e8_tuned_lambda` sweep is single-seed, which is precisely the reason the project's own
  `e13` work says its per-point numbers cannot carry a conclusion.
- Nothing here questions the *other* e10 results (the `side` rung, the power ceiling, the
  evaluation-noise decomposition); those are λ-conditional in the same way and are now labelled as
  such.

## 7. The (λ, batches) plane has two lines through one point, and the ladder sits off both

Reading the configs of every artifact that swept either axis:

| artifact | λ | Fisher batches |
|---|---|---|
| `e8_fisher_batches` | 0.1 | 8, **32**, 128 |
| `e8_tuned_lambda` | 0.003–0.3 (**32**) | 32 |
| `e8_basis` | 0.1 | 8 |
| **`e10` rungs** | **1.0** | **8** |
| **`e25`** (running) | **0.003** | **8** |

**The two sweeps are lines through the single shared point (λ = 0.1, batches = 32), not a grid.**
The λ conclusion ("0.003 is the only useful setting") is a statement *at batches 32*, and the
batches conclusion ("the diagonal degrades as its Fisher estimate improves") is a statement *at
λ = 0.1*. Nobody has measured λ = 0.003 at batches 8 — which is exactly the cell `e25` now fills —
and nobody has measured the batches axis at any λ other than 0.1.

That matters because the two axes are not independent. The fisher-batches finding established that
more batches is effectively a **stronger** penalty at fixed λ, so λ = 1.0 at batches 8 and λ = 0.1 at
batches 32 are not far apart in effective strength, and **"0.003 is the only useful setting" was
never tested in the regime the rung ladder runs in.** The early partial result from `e25` supports
this reading: at λ = 0.003 the block method's accuracy is **0.840 ± 0.025** against **0.8426 ± 0.0101**
at λ = 1.0 — the same to within noise — while its forgetting is **+0.087** against **+0.059**, i.e.
*worse* at the tuned λ. That is the opposite of what the sweep's prose predicts for this
configuration.

A tuning effect that does not appear where the sweep says it should, in a cell the sweep never
measured, is a reason to stop calling the rung result "λ-confounded" and start calling it
"**untuned in an unmapped plane**".

## 8. The experiment that would settle it

A 3×3 grid, λ ∈ {0.003, 0.1, 1.0} × batches ∈ {8, 32, 128}, on `cell_class`, 3 repeats, 500
iterations: **9 runs at ~35 minutes each ≈ 5 hours**, of which `e10` already supplies (1.0, 8) and
`e25` is supplying (0.003, 8). Two lines through one point cannot distinguish a tuning artefact from
a rung effect; a grid can, and the answer decides whether `C2b`'s negative means anything.

The cheaper version if 5 hours is too much: the diagonal of the grid, {(0.003, 8), (0.1, 32),
(1.0, 128)} — three runs, ~1.8 h, and it spans the effective-strength range rather than the nominal
one.

## 9. Update: two of the three points in the ladder's own λ arm already existed

§8 proposed a grid. It turns out the λ arm **at the ladder's batches (8)** has two of three points
already on disk, in files with no reason to have been compared:

| λ | batches | artifact |
|---|---|---|
| 0.1 | 8 | `runs/e8_basis.json` — the published basis comparison |
| 1.0 | 8 | `runs/e10_rung_cell_class.json` — the rung ladder |
| 0.003 | 8 | `runs/e25_...` — running |

All three share seeds, task draws, repeats and batch count. Analysing the first two
(`docs/findings/2026-09-22-bio-partition-worse-than-random.md`) changes the network line's headline:
at (0.1, 8) the biological partition is **worse** than its matched random control in all three
replicates, on both metrics, at **2.65σ / 2.73σ paired** — and the published analysis of that same
run was unpaired, read it as within-noise, and the project summarised it as "no advantage".

So the "λ-confounded" framing of §2 was itself too narrow. The rung ladder is not merely at an
unusual λ; **the λ arm it belongs to had never been assembled**, and assembling it from existing
artifacts produced a resolved result that four fires of λ work had not surfaced.
