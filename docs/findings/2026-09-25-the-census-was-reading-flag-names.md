# The census was reading flag NAMES: the linear line's draws are `seed0` and `seeds`, and 17 families average a draw inside each cell

**Date:** 2026-09-25
**Analysis only, no runs; a correction to the family census.** `e201` classifies a family as SINGLE-DRAW when it
varies a manipulation while using one (read-out, support) draw pair — a verdict computed from the network line's three
draw flags, `readout_seed`, `support_seed` and `partition_seed`. **The linear line has none of those.** `e3` builds its
tasks with `build_tasks(..., seed=seed)` for `seed in range(seed0, seed0 + seeds)` and draws its matched-random
partitions from `default_rng(seed0)` with `--control-draws` averaging them, so a linear run's draws are encoded in
**`seed0`, `seeds` and `control_draws`** and the census saw none of them.

---

## 1. The linear line's task draw is per seed, measured rather than inferred

```
seed 0: Sigma sha1 0abd5e6bc45a  (shape (5, 952, 952))
seed 1: Sigma sha1 7b0b5a5ea644
seed 2: Sigma sha1 dd22d7238016
distinct draws: 3 of 3
```

`build_tasks(circ, support_size=40, q=0.02, seed=s)` returns a **different task draw** for each `s` — three distinct
Σ matrices at three seeds on a 300-neuron circuit — which is the same fact the project already relies on when it says
a table's achieved overlaps are *"a property of `mb+cx+al@n1307`, three tasks of 80 neurons, seed 0"*. So `--seeds N`
averages **N task draws** inside each cell, and `--control-draws` averages that many partitions for the control.

`draw_keys` now carries two more components for a config that has them — `("tasks", seed0, seeds)` and
`("control", seed0, control_draws)` — so a family that **varies** them counts as varying a draw.

## 2. The corrected census

| verdict | before | **after** |
|---|---|---|
| SINGLE-DRAW | 41 families, 215 artifacts | **38 families, 205 artifacts** |
| REPLICATED ACROSS DRAWS | 15, 63 | **18, 73** |
| DRAW ONLY | 1, 3 | 1, 3 |
| replicates | 2, 4 | 2, 4 |

Three families move out of SINGLE-DRAW once the linear line's draws are read as draws. **And the census now reports
something the verdicts cannot express**:

> **17 of the 59 families (146 artifacts) AVERAGE more than one draw inside each cell** — the ladder (`e92`, `e86`,
> `e94`: `seeds=3` and `draws=5`, so each cell is 3 task draws × 5 control draws), `e3` (up to `seeds=18`), and the
> rewire families (`e32` `seeds=6`, `e33` `seeds=4`).

**`--repeats` is deliberately NOT counted**, and the distinction is the point: the network line builds its suite
**once** per artifact and runs `--repeats` training replicas at that one draw, so replicates are samples of the
*training noise* and not of a draw. Counting them would have made every network family look like a draw average,
which is the opposite of what today measured — `e116` and `e195` differ in the **support** draw at identical
configuration and identical 40 seeds, and that difference is 3.34σ.

**So the two sentences the census supports are different, and the earlier finding ran them together:**

- **38 of 59 families (205 of 285 artifacts) do not VARY a draw between their artifacts** — their cells are different
  configurations at one draw set, and their generalization beyond it is untested.
- **17 of those families AVERAGE draws within each cell**, which is not the same thing: an 18-seed rung table has 18
  task draws inside every number, so its cells are better-sampled than "single-draw" suggests, while no cell is at a
  *different* draw from any other.

## 3. What this changes, and what it does not

**It changes the correction the census earns.** This morning's note in C2 said the rung tables "are single-draw
families" and that "a rung table at one draw is not automatically safe". The first clause was too strong: the ladder's
cells average 3 task draws and 5 control draws, and the project has spent real effort on the control-draw dimension
(rule 10, `e92`'s `draws=5`). What remains true is the second clause and the reason: **the draw is not varied
*between* the rungs**, so a rung *ranking* is a within-draw-set ranking — and the size a support draw can have is
measured (3.3–6.6σ on the network suite) while the linear line's own draw size is not measured at all.

**It does not change the network families.** Their draws are recorded fields, the census read them correctly, and the
overlap axis's replication stands: six of its claims failed across support draws, and the one that survived survives
four configurations.

## 4. What this does not license

- **That the ladder is a replicated family.** Averaging 3 task draws per cell is not varying the draw across cells;
  a ranking can still be one draw set's ranking.
- **That the linear line's draw is small.** Nothing measures it. `e3`'s own `--control-draws` machinery exists
  precisely because the *control* draw was seen to matter (rule 10), and the task draw has never been varied across a
  ladder's cells.
- **That the census is now complete.** It reads recorded fields; a line that encodes a draw in a field it does not name
  (as the linear line did until this unit) is invisible to it, and the remedy is per-line knowledge rather than a
  longer list of flag names.
