# Registered: the pooling ladder at a SECOND draw set, which is the one draw never varied across a ladder's cells

**Date:** 2026-09-25
**Registered before its run.** The family census's correction
(`docs/findings/2026-09-25-the-census-was-reading-flag-names.md`) left one draw in the corpus with no measurement of
its own: **the linear line's task draw.** `e3` builds its tasks with `build_tasks(..., seed=seed)` for `seed in
range(seed0, seed0 + seeds)` — verified by three distinct `Σ` matrices at seeds 0, 1 and 2 — and draws its
matched-random partitions from `default_rng(seed0)`. So a ladder's cells each **average** 12 task draws, and **no
ladder in the record varies the draw set between its cells**: every pooling ladder is `seed0 = 0`.

That is the last of rule 53's three questions answered for the network suite and not for this one.

---

## 1. What the ladder reports, and what it says at draw set 0

`e181_ladder_d300_12seeds.json` — circuit 300 neurons, support 30, **12 task seeds**, `q` 0.02, `--ladder`,
`--no-realized`, `--topologies real`, `--control-draws 1`, **`--seed0 0`**, 2653 s — gives per basis an `excess`
(alignment above the chance level that same partition achieves against random task subspaces):

| basis | excess | alignment | chance |
|---|---|---|---|
| **`bio:pool4`** | **2.28112** | 0.03920 | 0.01718 |
| `bio:pool64` | 1.71290 | 0.02634 | 0.01538 |
| `bio:pool128` | 1.61061 | 0.02634 | 0.01635 |
| `rand:pool64` | 1.51490 | 0.02634 | 0.01739 |
| `rand:pool128` | 1.47748 | 0.02634 | 0.01783 |
| `bio:pool2` | 1.46687 | 0.03866 | 0.02636 |
| `bio:pool8` | 1.44707 | 0.02468 | 0.01705 |
| `bio:pool16` | 1.42104 | 0.02346 | 0.01651 |
| `bio:pool32` | 1.38674 | 0.02346 | 0.01692 |
| `rand:pool4` | 1.21206 | 0.01969 | 0.01624 |
| … | | | |
| `bio:pool1` | 0.92399 | 0.78821 | 0.85305 |
| `rand:pool1` | 1.01500 | 0.86602 | 0.85322 |

**`bio:pool4` is the peak, 1.069 above its size-matched random control at the same rung** — which is the form C2's
claim takes on this line: a biological pooling depth beats the matched-random partition of the same group sizes. The
table carries no uncertainty field, so this is a geometry computation's value at one draw set rather than a mean with
an sd.

## 2. The design

The same command, `--seed0 100`, everything else from `e181`'s own config (rule 44):

```
experiments/e3_basis_selection.py --ladder --circuit-size 300 --support 30 --seeds 12 --q 0.02 \
  --align-top 16 --no-realized --topologies real --control-draws 1 --seed0 100 \
  --json-out runs/e202_ladder_d300_12seeds_seed0-100.json
```

**Cost (rule 49)**: 2653 s at the same settings, i.e. **about 45 min**, measured from `e181`'s own `timing` block
rather than from a whole-family average. One command, launched on an idle machine.

**What `--seed0 100` varies, and what it cannot isolate.** It moves the task draws (12 of them), the matched-random
partitions and the rewiring at once, because the linear line seeds all three from `seed0`. To vary the task draw
*alone* would need a flag that does not exist; **this design varies the draw set**, which is the unit the census
flags — a family whose cells share one draw set — and not the task draw in isolation. That is the honest scope.

## 3. The claims

**P1 — the peak is the same rung.** At `seed0 100` the rung with the highest `excess` is **`bio:pool4`**.
**Falsifier**: a different rung peaks — the table's head is then one draw set's, and C2's "the best anchoring basis is
a biological pooling depth" would need the peak's identity stated as draw-set-conditional. **Null worth keeping**:
`bio:pool4` is second to another *biological* rung by less than 0.2, which keeps "a biological depth is best" while
moving which one.

**P2 — the peak's value is in the same range.** `bio:pool4`'s `excess` at `seed0 100` lies within **25%** of 2.28112,
i.e. in **[1.711, 2.851]**. **Falsifier**: outside **50%** (below 1.141 or above 3.422), which would make the value a
draw-set artefact of that size. **Null worth keeping**: between 25% and 50% — the rung is best and its margin is
draw-set-dependent.

**P3 — the matched-random control still loses at the peak.** `bio:pool4`'s excess exceeds **`rand:pool4`'s by at least
0.5** at `seed0 100` (seed set 0: 2.28112 − 1.21206 = **1.069**). **Falsifier**: the gap at or below **0.2**, which
would say the size-matched random partition matches the biological one at the same rung and that the peak's advantage
is a pooling-depth effect rather than a biological one. **Null worth keeping**: a gap of 0.2–0.5, i.e. the biological
advantage is real and half of what one draw set showed.

All three are read off the one artifact by the same three lines of arithmetic the table above used, and the read will
be a command before the artifact lands rather than a hand computation.

## 4. What this cannot do

- **Give a draw-set distribution.** One alternative draw set is a difference at n = 2, and today's own lesson is that
  such a difference can be an outlier's distance rather than a spread. Every verdict above is a *robustness* statement.
- **Separate the task draw from the control draw and the rewiring.** §2.
- **Speak for the network line.** The network ladder's rungs (`e10_rung_*`, 1.2–3.4 h each) are a different
  instrument, and nothing here transfers across the two lines — which is itself a reason to say which line a claim is
  about, as C2's note now does.
- **Replace the control-draw dimension.** `--control-draws 1` is held as `e181` had it, so this varies the draw *set*
  and not the number of control draws inside a cell.
