# Registered: the READ-OUT draw, varied for the first time, tested against the one claim that survived three support draws

**Date:** 2026-09-25
**Registered before its runs.** The support-draw replication is closed and its tally is that **exactly one** of the
axis's four claims holds on all three draws — the endpoint's forgetting rises with the input overlap, +0.03177
(2.99σ), +0.03516 (3.30σ), +0.02161 (2.70σ)
(`docs/findings/2026-09-25-three-draws-four-claims-exactly-one-is-3-of-3.md`). That claim is the project's oldest —
nine of nine matched comparisons — and it now has the best support of anything on the axis.

**And it has only ever been measured at one read-out draw.** `--readout-seed` has existed since mid-project, but the
census counts **80 of the 144 artifacts whose read-out subset is a live draw and cannot say which one they used**
(`docs/findings/2026-09-25-more-of-the-corpus-cannot-say-which-draw-it-used-than-can.md`), and no artifact in the
record was ever run at a second one. Every "bit-identical over seven executions" result in this project's history is
conditional on a read-out subset that was never varied.

So this runs the surviving claim across the second draw dimension.

---

## 1. The design

Two commands, everything but one flag copied from `e116`'s and `e144`'s own configurations so that the read-out draw
is the only live difference:

```
experiments/e8_rate_network.py --circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --train 96 --test 48 \
  --classes 4 --support 80 --shared-head --readout-size 32 --fisher-batches 8 --basis cell_class --seed0 0 \
  --readout-seed 1 --methods naive --repeats 40 --input-overlap {0.0, 1.0} \
  --json-out runs/e199_r32_ovl{00,10}_rs1_naive_40reps.json
```

`--support-seed` is **not** passed, so the supports stay at draw 0: the read-out draw moves while the support draw is
held fixed, which is the only way to attribute the difference to one of them. **Two targets, 0.0 and 1.0**, because
the claim under test is a *difference* between them — the endpoint's forgetting rise — so both ends of the difference
have to be re-measured at the same new read-out draw.

**The artifact names are the launch's arithmetic** (`tr -d '.'` on `0.0` gives `00` and on `1.0` gives `10`), checked
by running the expression rather than by reading this sentence — a defect that has cost this project two documents
today.

**Cost (rule 49)**: `naive` at 20–31 s per arm-replicate from `e193`'s and `e197`'s own heartbeats, so **13–21 min per
command and about 30–40 min** for the design. One command at a time on an idle machine.

## 2. The claims

**F1 — the one surviving claim survives the read-out draw too.** At read-out draw 1 the endpoint's forgetting rise is
**at or above 2σ** and of the **same sign**, i.e. positive. Its three support-draw values are +0.02161, +0.03177 and
+0.03516, so a read-out draw that leaves it resolved makes the claim **3 of 3 on supports and 1 of 1 on read-outs**.
**Falsifier**: unresolved (below 2σ) or negative — the claim would then be conditional on the read-out subset as well,
and since that subset was never varied anywhere in the record, every "nine of nine" figure in the corpus would inherit
the condition. **Null worth keeping**: resolved but at less than half the smallest support-draw value (< 0.0108),
i.e. the effect is there and much smaller at this read-out — which would make the three support-draw values an
over-estimate and the claim's magnitude unusable.

**F2 — the read-out draw's own size on a learning quantity.** At overlap 0.0 the read-out draw moves `learned (older)`
by **at most 0.0150 in magnitude**. The bar is the support draw's own measured 0.01484, and the read-out subset is 32
of 1307 neurons against the supports' 240, so the expectation is a *smaller* lever on the same quantity. **Falsifier**:
above **0.0250**, which would make the read-out draw a larger nuisance than the support draw on the quantity that
dominates the axis's learning claims. **Null worth keeping**: between 0.0150 and 0.0250, comparable to the support
draw — in which case **both** of the substrate's draws are of the same size and no cross-overlap claim in the record
is attributable without varying both.

**And a third, registered as a measurement rather than a claim**: the read-out draw's effect on forgetting, accuracy,
the newest task and the two interference terms at overlap 0.0, reported beside F2's value so that the comparison of
the two draws' sizes is on the same five quantities.

## 3. What this cannot do

- **Give a between-draw spread.** One alternative read-out draw is a difference and not a distribution, exactly as one
  alternative support draw was — and today's lesson is that a difference at n = 2 can be an outlier's distance. So
  F1 and F2 are the *robustness* statements they are written as, and not magnitudes.
- **Say anything about intermediate overlaps.** 0.0 and 1.0 only, for the reason in §1.
- **Test the read-out SIZE axis.** `--readout-size` is a different question (the read-out axis's shape) and this design
  holds it at 32; the flag's own help text notes that subsets of different sizes are drawn independently, so a size
  sweep does not share a draw with this one.
- **Rehabilitate the axis's other claims.** F1 concerns the one claim that survived the support draws; the rest were
  already 1 or 2 of 3 and nothing here re-reads them.
