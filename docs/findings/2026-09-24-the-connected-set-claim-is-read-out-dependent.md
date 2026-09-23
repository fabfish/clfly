# `e130`: the connected-set claim is read-out dependent — at read-out 32 it fails the registered test, and only at the final checkpoint

**Date:** 2026-09-24
**Script:** `experiments/e124_barrier_distribution.py` (unchanged except the `--matching-seeds` control built in
for this run); artifact `runs/e130_barrier_r32.json`.
**C0's comparator:** `runs/e116_r32_40reps.json`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive --shared-head
--input-overlap 0.0 --noise 1.0 --iters 500 --lr 3e-3 --batch 32 --test 48 --readout-size 32 --circuit-size 800`,
twelve seeds `0 + 100k`, 66 pairs, 21-point whole-solution chords at the first and last checkpoints.
**Pre-registration:** `docs/findings/2026-09-24-the-barrier-at-read-out-32-preregistered.md`, committed before the
run, with `e124`'s thresholds reused **verbatim**.
**Context:** `docs/findings/2026-09-24-the-barrier-over-all-pairs.md`, whose registered P1 was *"every one of the
66 pairs has a fit-task barrier below 25% of the chance level"* at read-out 128, and whose §6 named read-out 32 as
the first of its limitations.

---

## 1. P1 fails, the falsifier does not fire, and the failure is confined to one of the two checkpoints

| fit-task barrier / chance | read-out 128 | read-out 32 |
|---|---|---|
| checkpoint 0 — min / median / max | 0.0108 / 0.0284 / **0.1221** | 0.0158 / 0.0550 / **0.1342** |
| checkpoint 2 — min / median / max | 0.0148 / 0.0445 / **0.1252** | 0.0900 / **0.2187** / **0.4419** |
| pair-checkpoints above the 0.25 threshold | **0 of 132** | **21 of 132** |
| … at checkpoint 0 | 0 of 66 | **0 of 66** |
| … at checkpoint 2 | 0 of 66 | **21 of 66** |
| worst chord, as a factor below chance | **11.07×** | **3.14×** |

**P1 fails, and the pre-registration said in advance what that means**: *"a failure at read-out 32 is a failure of
a claim already in the record and not of a new one fitted to this run."* **`e124`'s P1 must be restated as
read-out dependent.** The falsifier does **not** fire — nothing reaches 50% of chance — so "the seeds' solutions
are one connected set" survives as a statement about **not crossing a wall**, while the margin on that statement
is no longer comfortable: at read-out 128 the worst path in the grid stays **11×** below the loss of a solution
that has learned nothing, and at read-out 32 it stays **3.1×** below.

**And the failure is entirely at the second checkpoint.** After the **first** task, all 66 pairs are below the
threshold at *both* read-outs, with maxima almost identical (**0.1221** and **0.1342**, a factor of 1.10). After
the **third**, the gap is **3.53×** (0.1252 against 0.4419). So **the read-out's effect on the barrier appears
only as tasks accumulate** — after one task the two read-outs agree, and after three they do not. That is the
shape more interference should produce, and it is a cleaner statement than the aggregate: the barrier is a
property of the read-out **jointly with the number of tasks**, not of either alone.

## 2. P2 holds, and it holds harder than the registration asked

P2 was registered as a **direction**: read-out 32's median barrier is higher than read-out 128's. It is, by
**3.2×** over the whole grid (0.1157 against 0.0361) and by **4.91×** at the final checkpoint. The registration
deliberately did not state a magnitude, so 4.91× is a measurement rather than a pass, and the reason it is large
is legible: read-out 32's per-repeat spread is **0.0556** against read-out 128's 0.0325, so this is where the
seeds land furthest apart — and the barrier between two solutions tracks that.

**P2 holding is also what makes P1's failure interpretable rather than merely negative.** The two predictions
were registered against different questions — *"is every pair connected?"* and *"does the barrier grow where the
seeds differ most?"* — and the answers are **no** and **yes**. A fire that had registered only the first would
have reported a refutation with no idea that it was the ordering the geometry predicts.

## 3. The controls, and one of them was worth building into the script

- **C0a, the extension control, is bit-identity**: the twelve seeds reproduce
  `runs/e116_r32_40reps.json`'s first twelve with **max |difference| 0.000e+00**. Registered as a check with a
  known-answer precedent at read-out 128, and it delivered at read-out 32 — so this run is the same benchmark, at
  a narrow read-out, rather than a new one. It was **built into the script** for this fire
  (`--matching-seeds`), on the ground that a control run by hand afterwards is a control that gets skipped.
- **C0b passes 6 of 6**: the three saved checkpoints reconstruct the runner's own recorded `retention_loss` at
  every task.
- **P3 replicates its null**: the registered correlation between a pair's fit-task barrier and its own forgetting
  difference is **r = −0.108** at read-out 32 against **+0.144** at read-out 128. Both are indistinguishable from
  zero and they disagree in **sign**, which is the honest form of a second null: the barrier is not the pair's
  disagreement at either read-out, and two near-zero correlations of opposite sign are two samples of nothing.

## 4. What this changes in the record

- **`e124`'s P1 is restated** as: *every pair is below 25% of chance **at read-out 128**; at read-out 32 that
  holds after one task and fails after three, for 21 of 66 pairs.* The finding and the paper's §4.2 paragraph are
  corrected in place with the date.
- **The design statement gains a condition.** §4.2 read the geometry as *"the seed chooses a point of a connected
  set rather than a basin"*. That is still what the measurements say, **and** the set's connectivity is
  read-out dependent with the margin thinning exactly where the seeds differ most — so the honest form is that a
  practitioner choosing the narrowest read-out is choosing the configuration in which the seeds' solutions come
  closest to being separated, at a factor of 3.1 rather than 11.
- **And it does not become a multi-basin result.** The falsifier was registered at 50% and nothing reached it:
  the worst chord in 66 pairs peaks at 44% of chance, i.e. still **below half** the loss of a solution that has
  learned nothing. The claim is qualified, not overturned.

## 5. What this cannot settle

- **Two read-outs is a line, not a curve.** P2 says the barrier grows as the read-out narrows; read-out 0 (the
  whole state) is the third point and is untested, and it is the one that would separate *"the barrier is a
  property of the geometry"* from *"the barrier is monotone in the read-out"* — the distinction `e124`'s §6
  raised and this fire has now made load-bearing rather than hypothetical.
- **The threshold's location is a choice.** 25% was registered in `e124` and reused here verbatim, which is what
  makes this a replication; but 21 of 66 is a count and 0.4419 is a magnitude, and a reader who thinks the line
  should sit at 30% or 40% would read the same numbers as a pass. **Both are printed for that reason.**
- **66 pairs from 12 seeds remain heavily dependent** — each seed appears in 11 of them — so the effective `n`
  for anything about seeds is 12, and the median is a median over dependent values.
- **21 points per chord can miss a ridge**, so every barrier is a lower bound; that is the safe direction for the
  connectedness claim and the unsafe one for the size of the worst pair, which could be larger than 0.4419.
