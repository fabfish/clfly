# `e178` read at last: the `side` rung's negative does not replicate, and the design was under-powered by the assumption it borrowed

**Date:** 2026-09-25
**Read of:** `runs/e178_rung_side_cs300_144reps.json` — the same three arms at the same basis at **cs = 300**, 144
replicates — against `runs/e10_rung_side.json` (cs = 800, 3 replicates) and the registration in
`docs/findings/2026-09-25-the-side-rungs-negative-priced-before-it-is-bought.md` §3.
**Instrument:** `experiments/e190_side_rung_read.py`, which was written and calibrated against `e10` five fires
before the artifact existed, so the read was one command.

---

## 1. The read

| | cs = 800 (`e10`, n = 3) | **cs = 300 (`e178`, n = 144)** |
|---|---|---|
| `naive` mean forgetting | +0.1007 | **+0.1904** |
| `ewc-block` | +0.0972 | +0.2233 |
| `ewc-block-rand` | +0.0938 | +0.2224 |
| **paired `ewc-block − ewc-block-rand`, forgetting** | +0.0035 ± 0.0409 = **0.08σ** | **+0.0009 ± 0.0110 = 0.08σ** |
| **paired gap, accuracy** (the registered quantity) | −0.0116 ± 0.0267 = 0.43σ | **−0.0020 ± 0.0072 = 0.28σ** |

**The registered outcomes:**

- **P1 does not hold**: the gap at cs = 300 is not resolved at 2σ — it is **0.28σ** over 144 paired seeds, with
  **75 negative and 67 positive**.
- **The falsifier does not fire**: it is not ≥ 2σ positive either.
- **P2 does not agree**: the gap is **less** negative at the smaller circuit, not more.
- **The registered null is the outcome**, and the registration says what that means: *"unresolved even at 144
  replicates, which would say the effect is smaller than the first circuit's triple — and that would be evidence for
  the account, since both circuits' gaps would then shrink as the partition's estimation problem shrinks."*

So the item's own claim — the `side` rung's negative "holds" — **does not replicate at the circuit it asked to be
replicated at**. At cs = 300 the block-minus-random gap is 0.28σ from zero on accuracy and 0.08σ from zero on
forgetting.

## 2. Two things changed at once, and only one of them was in the registration

The effect is **83% smaller** (−0.0116 → −0.0020), which is the branch the registration allowed. But **the
per-replicate scatter is also 1.9× larger at the second circuit**, and that the registration did not allow for — it
borrowed the first circuit's sd, measured from **three** replicates:

| quantity | sd at cs = 800 (n = 3) | sd at cs = 300 (n = 144) | ratio |
|---|---|---|---|
| paired accuracy gap | 0.0462 | **0.0869** | 1.88× |
| paired forgetting gap | 0.0708 | **0.1320** | 1.86× |

**So the design's power was mis-estimated at its input, not at its arithmetic.** With the measured sd:

- resolving **the first circuit's effect** (0.0116) at 2σ needs **224** replicates — the run used 144;
- resolving **the effect that is actually there** (0.0020) at 2σ needs **7,552**.

The registration's own power line — *"with the first circuit's per-replicate sd (0.0462) and 144 replicates the sem
is 0.0038, so an effect as large as +0.0116 would read at 3.0σ"* — was arithmetically correct and rested on a
3-replicate estimate from a **different circuit**. The realized sem is 0.0072, **1.9×** the planned 0.0038, so the
planned 3.0σ became **1.6σ** for that effect size — and the effect is not that size.

## 3. What replicates is not the negative but its absence

**0.08σ at both circuits** on forgetting (+0.0035 ± 0.0409 and +0.0009 ± 0.0110) and under half a sigma at both on
accuracy. That is the same number at n = 3 and at n = 144, from the same design, and it is the strongest form of
what this run licenses: **the block partition and its group-size-matched random control are indistinguishable on
this rung at both circuit sizes** — a claim that is thin evidence for the penalty's usefulness at cs = 800 and
adequate evidence at cs = 300, where 144 replicates put the estimate 0.0020 from zero.

**And one level fact is worth stating because it is large and was not in the registration**: at cs = 300 `naive`
forgets **+0.1904** against **+0.1007** at cs = 800 — the smaller circuit forgets **1.9× more**, again the same
factor 1.9 — while both block arms forget *more* than `naive` (+0.2233, +0.2224 against +0.1904). So on the small
circuit the side-basis penalty is **worse than the unpenalised arm by +0.033 of forgetting**, which the cs = 800
triple could not have shown (there the arms are +0.0972/+0.0938 against `naive`'s +0.1007, i.e. all three within
0.007). The registration did not predict the level's direction and this is a fact about it.

## 4. The price, and the field this run could not carry

The artifact's own `timing_s` is **26608 s = 7.39 h** against the registered 6.5 h — **+14%**, which the plan row had
already decomposed in flight (the probe's 162 s was all three arms for one replicate, i.e. 54.2 s per arm-replicate,
so the arithmetic was right and the machine was slower).

**`cpu_time_s` is absent from this artifact**, because the run started before that field was added an hour ago — so
this is the last artifact whose price cannot be projected in CPU terms, which is the gap the field exists to close.

## 5. Falsifiers and scope

- **What would overturn §1**: a re-read of the artifact that finds the registered quantity resolved — the reader
  prints every term, and the test suite reads this artifact on every run now that it exists (a `skipif` guard in
  `tests/test_e190_side_rung_read.py` asserts the mechanics: n = 144, both arms, a non-zero sd, one of the four
  registered outcomes).
- **What §2 does not license**: that 224 replicates would have resolved the effect. It would have resolved **the
  first circuit's effect size** at the second circuit's scatter; the effect at the second circuit is 83% smaller, so
  the honest statement is that the design was under-powered *for the effect it was built to detect* and that the
  effect's own size moved.
- **Scope**: one basis (`side`), one read-out (32), one task count (three), one partition draw per arm
  (`partition_draw` records seed 0, 11 groups, fingerprint `fc064656e855`), and `--readout-size 32` with a draw
  fingerprint `59926518137c`. Rule 10's population question — whether the draw is a sample from a wider
  distribution — is not addressed by one draw, and the registration did not claim it was.

## Reproduce

```
uv run python -m experiments.e190_side_rung_read            # the registered read, both quantities, its own cost
uv run pytest tests/test_e190_side_rung_read.py -q          # six tests, the sixth reading the real artifact
```
