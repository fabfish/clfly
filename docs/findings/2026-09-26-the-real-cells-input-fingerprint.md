# The excess is not the instrument for reproducibility: `real` cells carry a basis-independent fingerprint that says whether the inputs moved

*2026-09-26 11:40, `runs/e227_oracle_fingerprint_census.json` — the census is JSON-only and takes seconds; the two
rebuilds take ~5 min (cs 1500, twelve seeds) and ~10 s (cs 300, three seeds), and the thread sweeps ~1 min each. Read
from the artifacts' own `analytic` blocks, and from `clfly.connectome.tasks` + `clfly.bench.analytic` rebuilt from the
connectome. Registration: this fire picked up the open question `e225` left -- what the pooling family's 1.66e-6 is.*

## 1. The hole in `e225`'s FLOATING class

`e225` compared the `real` cell's analytic excess across the corpus and found one pair that differed by **1.66e-6**
relative, which it classified FLOATING -- *"the same runner at two epochs, and the arithmetic moved by less than a
millionth"*. Two things are wrong with using that number as the instrument:

- **the excess is a difference of two larger numbers**: `ewc_mean - oracle_mean` = `0.0771 - 0.0624`. Measured here,
  the group's excess spread is **5.3×** the spread of the quantity it is made of (`e227`'s census prints that ratio
  per group), so *any* input wobble is amplified by ~5 and a ratio column hides it;
- a difference cannot say **which side moved**. `e225` had no way to tell "the method drifted" from "the tasks
  drifted", and it chose the first.

## 2. The fingerprint that can tell them apart

Every artifact carrying a `real` block also carries `analytic.oracle_mean` -- the Kalman/RTS reference line. The
oracle sees no basis, so within one artifact it must be **one float across all of that artifact's bases**. That is
checked, not assumed: **0 of the 26 artifacts** carry more than one value across their own bases.

Across artifacts it is therefore a fingerprint of the **tasks alone**, and grouping by the fields that fix the circuit
and the tasks (`circuit_size`, `support`, `seeds`, `seed0`, `q`; `real` topology only) gives:

| group | artifacts | fingerprint |
|---|---|---|
| cs 400, support 80, seeds 3 | `e223_cs400_support80_rs0/rs1` | **EXACT, 0 ulp** |
| cs 800, support 80, seeds 12 | `e3_ladder`, `e3_ladder_v2` | **EXACT, 0 ulp** |
| cs 800, support 80, seeds 18 | `e3_seeds18`, `e58_bases_18seeds_perseed` | **EXACT, 0 ulp** |
| cs 800, support 80, seeds 3 | `e208_hole_sweep_cs800_3seeds` (09-26), `e2_analytic` (09-22) | **EXACT, 0 ulp across 3.89 days** |
| cs 1500, support 150, seeds 12 | `e9_ladder_d1874`, `e79_ladder_d1874_perseed` | DRIFT **3.11e-7** — attributed |
| cs 300, support 30, seeds 3 | `e13_control3_d952`, `e217_ladder_cs300` | DRIFT **6.27e-4** — **OPEN** |

Bit-exactness is a stronger statement than `e225` could make: the four EXACT groups include the pair spanning **3.89
days**, and now it is *the tasks themselves* that agree to the last bit, not just the excess to within 1e-12.

## 3. Drift A (cs 1500): attributed to the process's thread count

| artifact | written | start (mtime − `timing.total_s`) | `oracle_mean` |
|---|---|---|---|
| `e9_ladder_d1874` | 09-22 19:54 | 09-22 14:16 (5.64 h run) | `0.062351113784104656` |
| `e79_ladder_d1874_perseed` | 09-23 05:13 | 09-23 02:54 (2.31 h run) | `0.06235113315147103` |

**Rebuilt today at cs 1500, support 150, seeds 0–11: `0.062351113784104656` — `e9`'s stored value, to the last bit.**
So the *older* run is the reproducible one and the newer one deviated. The code is not the candidate: between the two
start epochs no commit touches `clfly/` at all.

**The mechanism is the thread count, and the module measures its size itself.** `--thread-sweep` runs the oracle in
child processes at each `OMP_NUM_THREADS`:

| setting | per-seed movement against the default |
|---|---|
| cs 1500, 1 thread vs default | **4.8e-7 to 1.1e-6** relative per seed |
| cs 300, 1 thread vs default | **3.5e-6 to 7.1e-6** relative per seed |

`e79`'s deviation (3.1e-7 on the twelve-seed mean) sits **inside** that class. The oracle is
`sum_k R_kj pinv(J_j) R_kj^T` over d = 1874 matrices; this environment's numpy is scipy-openblas 0.3.34 with 24
threads, and changing the thread count changes the reduction order inside the BLAS. So the arithmetic of the analytic
path is **exact in principle and reproducible to ~1e-6 in practice**, and *that* is the scale any exactness claim has
to be stated at on this machine.

## 4. Drift B (cs 300): open, and the census now says so out loud

| artifact | written | `oracle_mean` | rebuilt today |
|---|---|---|---|
| `e13_control3_d952` | 09-22 16:09 | `0.02995350224905204` | **this value, to the last bit** |
| `e217_ladder_cs300` | 09-26 03:59 | `0.02993473243181863` | — |

The same pattern -- the **older** artifact is the reproducible one -- but here the deviation is **6.27e-4**, which is
**100× the entire thread class measured at this size** (3.5e-6 to 7.1e-6). So the thread count is *ruled out*, and so
is a code change:

- every commit between the two epochs that touches the task or circuit path is inert for values (`434b512`'s
  `circuits.py` change is a **comment**; its `tasks.py` change drops `PB` and `NO` from the heading assembly, two
  values that select **0 neurons**);
- the cs-800 group straddling the same window agrees **to the bit**, so nothing global moved.

What remains is the **substrate** `e217`'s run saw, and three further measurements (this fire's second half) narrow
that to one candidate without closing it:

| probe | result |
|---|---|
| repeated processes at cs 300 | **identical circuit** (`neuron_sha1` `9af5a4080159` in every run) — the tight budget's neuron set is reproducible |
| `--task-thread-sweep default,1` | **same circuit, different Jacobians** — the task builder *is* in the thread class — but the oracle moves only **2.11e-6** and the basis-dependent `ewc_mean` **1.46e-7** |
| `--neighbour-sweep` (supports 10/20/30, seed0 0/1/2, q 0.0125/0.02/0.05) | **no neighbour reproduces the deviant** — nearest is `q = 0.0125` at 9.2e-4, then `seed0 = 1` at 2.2e-3 |

So the circuit is out, the arithmetic's thread class is an order *below* the oracle sweep's own class and ~300× below
this drift, and the value is not a neighbouring configuration's (which would have made it a transcription error
rather than an arithmetic one). What is left is the support draw -- whatever else that run saw that its config does
not name. It stays recorded as **OPEN -- not attributed**, with that one candidate, rather than attributed to a
mechanism nothing has measured. It also **corrects a reading of `e225`**: that census declared the cs-300 pair
"MATERIAL across families", and its cross-family declaration is what kept it out of the exit code. The pair is
confounded on **two** axes: different families *and* tasks that differ by 6.3e-4 -- and with the fingerprint's
measured amplification (149.6× here) the input difference cannot be separated from the method difference at all.

## 5. What changes for the corpus

- **An exact-reproduction claim must name its fingerprint.** "The value reproduced" is now checkable as *"the
  basis-independent input fingerprint reproduced to the bit"*, and `e227` is the gate for it.
- **"Same runner at two epochs" is retired as an explanation.** With the fingerprint, the pooling pair's 1.66e-6 is
  *the inputs of one member having moved*, at a scale the thread count alone produces.
- **The certificate is worth stating in the record**: in *both* drifts the reproducible value is the **older**
  artifact's, which means the two deviant runs are the newer ones -- and both were launched while other heavy runs
  were in flight on the same machine.
- **The excess's own class boundary matters less than it looked.** `e225` noted that any FLOATING/MATERIAL boundary
  in `[1e-5, 1e-3]` classifies this corpus identically. That is still true, and it is now beside the point: the
  classification that carries information is the fingerprint's ulps, not the excess's ratio.

## 6. What this cannot do

- It compares **one number per artifact**. A task change that leaves the oracle's mean unchanged is invisible.
- **Fingerprint agreement is not method agreement**: two artifacts can share tasks to the bit and still disagree in
  what they computed with them.
- The drifts are **one pair each**, so the ulp distribution of "a run that deviated" is unmeasured; the thread class
  is measured at two sizes and two settings, not swept.
- **The neighbour sweep covers a window, not the space**: supports {10, 20, 30}, seed offsets {0, 1, 2} and
  q ∈ {0.0125, 0.02, 0.05} at one circuit size. A transcription error outside that window -- a different circuit
  size, a different assembly set, a different runner -- would not appear in it.
- **A near-miss is not a match.** The neighbour sweep's nearest value (9.2e-4 away) is a *different* configuration
  that lands close by; the test is bit-equality, precisely because "close" is how a drift gets mistaken for a
  reproduction.
- Drift B is **open**. Nothing in this audit says the new run is wrong -- only that its tasks are not the ones the
  code produces today, at a scale 100× the arithmetic's own.
