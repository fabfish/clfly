# Registered: two more interior levels, to localise the far term's peak and the near term's acceleration

**Date:** 2026-09-25
**Registered before its runs.** The completed axis left three things it could name but not locate:

- the **distant-pair term peaks at the midpoint**: 7.5% → **82.1%** → 75.9% → 100% of its own 0 → 1 change;
- the **adjacent-pair term is strongly back-loaded**: 12.3% → 20.0% → 47.9% → 100%, so more than half its rise lives
  in the last 40% of the axis;
- the **fitting deficit** is +0.0065 → **−0.0326** → −0.0263 → +0.0010, so it appears and recovers somewhere between
  the measured points.

Two more levels — one in the first gap, one in the last — turn each of those into a located shape rather than a
three-point sketch. The read is `e194`'s own machinery at the new achieved overlaps.

---

## 1. The design, and the target that is already taken

**Target 0.25 is NOT available**: it is already an axis point, and its achieved Jaccard is 0.1429. The axis is
targets 0.0 / 0.25 / 0.50 / 0.75 / 1.0 → achieved 0.0000 / 0.1429 / 0.3333 / 0.6000 / 1.0000, and the two useful *new*
targets are the midpoints of the two largest gaps:

| new target | achieved Jaccard `o/(2−o)` | why there |
|---|---|---|
| **0.375** | **0.2308** | between 0.1429 (far at 7.5%) and 0.3333 (far at 82.1%) — where the far term's rise lives |
| **0.875** | **0.7778** | between 0.6000 (near at 47.9%) and 1.0 (near at 100%) — where the near term accelerates |

Two commands, `naive` only — every registered claim on this axis is stated on `naive` — with everything but the
manipulation copied from `e193`'s level-0.50 config:

```
experiments/e8_rate_network.py --circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --train 96 --test 48 \
  --classes 4 --support 80 --shared-head --readout-size 32 --fisher-batches 32 --basis cell_class --seed0 0 \
  --methods naive --repeats 40 --input-overlap {0.375, 0.875} \
  --json-out runs/e196_r32_ovl{0375,0875}_naive_40reps.json
```

**The artifact names are checked against the launch's own arithmetic rather than written from the prose**: the
launcher's `n=$(echo $ov | tr -d '.')` turns `0.375` into `0375` and `0.875` into `0875`. That defect has now cost
this project two documents in one day (`overlap{25,50,75}` for `025`/`050`/`075`, and `{000,050,100}` for
`00`/`05`/`10`), so the names above are what `tr` produces and not what the numbers look like.

**Support draw 0**, the same as the rest of the axis: these are a continuation of it and not a replication, so the
existing baselines admit them (`support_seed` agrees and `input_overlap` is the manipulation).

**Cost (rule 49)**: `naive` at 20–31 s per arm-replicate on this circuit from `e193`'s and `e195`'s own heartbeats,
so **13–21 min per command** and **about 30–40 min** for the design. It starts when `e195`'s last artifact lands, so
the machine is never idle.

## 2. The claims

**T1 — the far term's early rise is graded rather than a step.** At achieved 0.2308 the distant-pair progress is **at
least 30%**. The two readings this separates: a graded rise puts it near 40–50% (a third of the way from 0.1429's
7.5% to 0.3333's 82.1% in *overlap* terms is 0.2308, which is 46% of the way in t, suggesting ~40%), while a step at
or above the midpoint puts it near 7.5% and a step below puts it near 80%. **Falsifier**: below **15%**, i.e. the far
term is flat until somewhere in (0.2308, 0.3333] and the jump is a threshold rather than a slope. **Null worth
keeping**: 15–30%, a rise that has begun but is much slower than linear in the target.

**T2 — the near term has not saturated at two thirds of the way to the end.** At achieved 0.7778 the adjacent-pair
progress is **above 60%**; interpolating between the measured 0.6 (47.9%) and the 1.0 endpoint in *achieved overlap*
gives **71%**. **Falsifier**: below **45%**, which would say the near term's acceleration is even later than the
endpoint implies and that its last quarter of the axis carries ~55% of its rise. **Null worth keeping**: 45–60%,
which keeps the back-loading while making it less extreme than the two measured points suggest.

**T3 — the fitting deficit recovers before the endpoint.** At achieved 0.7778 `learned (older)` against `e116` is
**above −0.0200** (measured at 0.6: −0.0263 ± 0.0035 = 7.48σ; at 1.0: +0.0010 ± 0.0032 = 0.33σ, so the recovery is
somewhere in the last 40% of the axis). **Falsifier**: **at or below −0.0263**, i.e. no recovery from the 0.6 value,
which would make the deficit's decline from the midpoint (−0.0326 → −0.0263) the beginning of a plateau rather than
of a return. **Null worth keeping**: between −0.0263 and −0.0200, a partial recovery that leaves the deficit
resolved at both interior levels.

## 3. What this cannot do

- **Average over draws.** These are draw 0, so they lengthen draw 0's shape and say nothing about draw 1; the
  replication of that draw is `e195`, running beside them.
- **Locate either term's extremum exactly.** Two added levels make the shape a seven-point object, not a fitted
  curve; if the far term's peak is between 0.2308 and 0.3333, both bracket it and neither finds it.
- **Speak to the penalised arms.** `naive` only, as with `e195`, and for the same reason: an overlap-1.0 run draws
  its shared population from the seed, so that family needs its own anchor.
