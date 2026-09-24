# The ladder's plateau is circuit-specific: the optimum moves 16× when the circuit grows 1.43×

**Date:** 2026-09-25
**Read of:** `runs/e73_ladder_named_head_to_head.json` (its `ladder_rows`, the d = 1307 ladder from
`e3_ladder_v2.json`) against `runs/e79_ladder_d1874_perseed.json` (`topologies["real"]`, d = 1874). No new script
and no runs: §8's first item asks whether the ladder's *plateau* transfers to a second circuit, and both circuits'
ladders are already on disk at **twelve seeds each** with the **same eight rung names**.

---

## 1. What the two ladders look like

`pool_below = N` merges every annotation label appearing in fewer than **N neurons**, so `pool1` is the
unpooled end and `pool128` the coarse end. Both ladders are complete over `pool1 … pool128`, at twelve seeds:

| rung | d = 1307 — `delta` (bio minus its matched control; lower is better) | d = 1874 — excess over the oracle |
|---|---|---|
| `pool1` | +0.000191 ± 0.000026 | +0.014713 ± 0.000156 |
| `pool2` | −0.008007 ± 0.000343 | +0.006727 ± 0.000130 |
| **`pool4`** | **−0.008844 ± 0.000199** | +0.004822 ± 0.000096 |
| `pool8` | −0.006852 ± 0.000221 | +0.002025 ± 0.000029 |
| `pool16` | −0.007651 ± 0.000197 | +0.001468 ± 0.000024 |
| `pool32` | −0.006986 ± 0.000192 | +0.001467 ± 0.000024 |
| **`pool64`** | −0.005485 ± 0.000269 | **+0.001208 ± 0.000022** |
| **`pool128`** | −0.004094 ± 0.000229 | **+0.001208 ± 0.000022** |

**The two columns are different quantities and are not comparable in value** — the first is a *matched-control
contrast* (negative means the biological partition beats its group-size-matched random control) and the second is
an *excess over the analytic oracle*. What is comparable is the **shape**, and that is what the item asks about.

## 2. The answer: the direction transfers and the plateau does not

| | d = 1307 | d = 1874 |
|---|---|---|
| minimum rung | **`pool4`** (−0.008844) | **`pool64`** (+0.001208) |
| rungs within 2 sem of the minimum | **{4}** — one rung | **{64, 128}** — the coarse end |
| is `pool1` (no pooling) worst? | **yes** (+0.000191) | **yes** (+0.014713) |
| interior optimum? | **yes** | **no** — the curve is monotone toward the coarsest rungs |

**So the lesson transfers and its location does not.** On both circuits **pooling helps and no pooling is the worst
rung** — the qualitative claim §4.3 makes — while the **plateau sits sixteen times coarser** on the larger circuit
(`pool4` → `pool64`), and on the second circuit there is **no interior optimum at all**: the two coarsest rungs are
tied at 2 sem and are the best.

## 3. Why, and why it matters for how the ladder is read

**The threshold is an absolute neuron count, so a rung is not a fixed amount of pooling across circuits.** `pool4`
merges labels with fewer than four neurons; on a circuit with 1.43× the neurons the same label is bigger, so fewer
labels fall below the threshold and the *same rung does less*. **The ladder is therefore not scale-free, and its
optimum can move with the circuit for a reason that has nothing to do with biology** — which is a caveat the
paper's ladder reading does not currently carry. The observed shift (16×) is larger than the size ratio (1.43×), so
size is not the whole story — the annotation vocabulary's own distribution across circuits is in there too — but the
direction is the one this mechanism predicts.

**And it re-frames the item's own sentence.** §8 asks for "the plateau **re-measured** on a second circuit",
implying a location that a measurement can confirm or move. It has been measured and it moved: **what needs
re-measuring is not whether the lesson holds but *where*, and a second circuit answers that it is elsewhere.**

## 4. What this cannot settle

- **The two columns measure different things**, so "16×" is a statement about where each curve bottoms and not
  about how much better either is. A like-for-like comparison needs the *same* estimator at both circuits, and the
  artifacts on disk do not provide one.
- **Two circuits are two points**, and the shift is not shown to be monotone in size: a third circuit (d = 1307's
  own `--circuit-size 300`, or the 3000-neuron `e3_large`) would say whether the optimum tracks the size or the
  vocabulary.
- **`pool4`'s minimum at d = 1307 sits in a *single* rung's plateau** (one rung within 2 sem), which is a sharper
  statement than the paper's "pool the rarest groups" and is not what that phrase describes — the phrase suggests a
  region, and the region is one rung wide there.
- **Both ladders are twelve seeds**, so each rung's own resolution is what the table shows and the *shape* claims
  above are read at 2 sem, not tested as an interval.
