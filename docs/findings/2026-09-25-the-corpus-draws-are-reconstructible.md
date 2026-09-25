# The corpus's draws are reconstructible: 238 unidentified (artifact, draw) pairs become 35

**Date:** 2026-09-25
**Analysis only, no runs.** `e198` found that the corpus cannot say which draw it used in **238** (artifact, draw)
pairs, and that the largest class was the overlap suite's supports at 127
(`docs/findings/2026-09-25-more-of-the-corpus-cannot-say-which-draw-it-used-than-can.md`). `e168` had already shown
the *partition* draw is reconstructible from the artifact; today's question was whether the other two are. **Both
are**, and the reconstruction is validated against every artifact that records the field.

---

## 1. The reconstruction, and its validation

The runner draws each subset as a pure function of values the artifact already carries:

```
rs = np.sort(np.random.default_rng(draw_seed).choice(n, size=readout_size, replace=False))
draw_hash = sha1(" ".join(str(int(x)) for x in rs)).hexdigest()[:12]
```

with `draw_seed = --readout-seed` (or `--seed0`), `size = --readout-size` and **`n = circ.n_neurons`**. That last one
is the trap: **`config.circuit_size` is `max_neurons` and not the count** — 800 against the circuit's 1307 neurons —
and the subset is drawn from the circuit, so a reconstruction using `circuit_size` would produce a plausible wrong
fingerprint. The count is in the artifact's `circuit` string (`mb+cx+al@n1307`).

`overlap_controlled_supports` is likewise a pure function of `(n, T, size, overlap, seed)`, all of which are in the
config, and needs **no connectome**.

| draw | reconstruction | reproduces the recorded fingerprints | disagrees |
|---|---|---|---|
| read-out subset | `sha1` over `choice(n, readout_size, seed)` | **68 of 68** | **0** |
| overlap supports | `sha1` over `overlap_controlled_supports(n, 3, support, overlap, seed)` | **6 of 6** | **0** |

**A reconstruction that were not validated would turn an unidentified draw into a mis-identified one, which is worse
than leaving it unknown** — so the validation is printed beside the result and asserted in the tests.

## 2. The census, before and after

| draw | live | identified (recorded) | **identified (reconstructed)** | unidentified after |
|---|---|---|---|---|
| read-out subset | 121 | 68 | **121** | **0** |
| matched-random partition | 45 | 14 | 14 | **31** |
| overlap supports | 133 | 6 | **129** | **4** |
| **total** | 299 | 88 | **264** | **35** |

**238 unidentified (artifact, draw) pairs become 35**, and the 35 that remain have two stated causes rather than a
mystery: **31** are partition draws, which are reconstructible by `e168 --reconstruct`, the machinery that builds the
connectome and rebuilds `random_matched` (`e168`'s own finding is that the draw "is reconstructible, and it
reproduces"); and **4** are support draws on artifacts that do not name their circuit at all
(`e122_path_geometry.json`, `e124_barrier_12seeds.json`, `e130_barrier_r32.json`, `e131_barrier_r1307.json`), so
there is no `n` to rebuild from.

## 3. A false positive this unit removed, of the class the census exists to avoid

The first version of the read-out liveness test required `readout_size < n`, which counts **`readout_size = 0`** as a
subset of size zero — 27 artifacts, all with `readout_size = 0`. In the runner `0` is **falsy**: `if args.readout_size
and args.readout_size < circ.n_neurons` means *use the whole state*, and no subset is drawn at all. So those 27 were
being reported as unidentified draws that do not exist, and requiring the size to be **truthy** as well as smaller
than `n` removed them: the read-out's live count fell from 148 to **121** and its unidentified count from 27 to **0**.

This is `e126`'s preamble in miniature — *a checker that reports everything gets ignored, and an ignored checker is
worse than none because it looks like coverage* — and it is the second such correction in `e198`'s short life (the
first was counting whole-circuit read-outs as subsets).

## 4. What this changes, and what it does not

**It changes what a reader can do.** An artifact that does not record its draw is no longer an artifact whose
condition is unknown: for 264 of the 299 live pairs the draw is now *identified*, either by the field or by
reconstruction, so **two artifacts can be checked for comparability without re-running anything** — which is the
practical form of rule 53. It also means a future audit can flag **pairs measured at different read-out draws**,
which is what made today's axis work necessary.

**It does not change any measurement.** A reconstruction identifies a draw; it does not re-measure it, and the
support draw's 3.3–6.6σ effect and the read-out draw's effect (being measured now, `e199`) are unaffected. Nor does it
say the identified-pair claims are reliable: the axis's failure was not that its draws were unknown but that they were
**never varied**.

**And the rank of the remaining gap is stated rather than implied**: after this, the partition draw is the only class
of any size, and it is the one whose reconstruction needs the connectome — so a reader wanting the whole corpus
identified runs `e168 --reconstruct` once.
