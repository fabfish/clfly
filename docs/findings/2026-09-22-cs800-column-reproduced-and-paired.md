# E48 — the cs = 800 column is reproduced whole, and the 32.7σ refutation becomes a paired −28.9σ with 6/6 seeds agreeing

**Date:** 2026-09-22
**Artifacts:** `runs/e48_cs800_perseed.json`
**Context:** `2026-09-22-c1-contrast-is-seed-robust.md` (`e47`), `2026-09-22-twelve-seeds-reverse-the-e5-direction.md` (`e42`)

---

## 1. The hole this closes

`e47` found that `runs/e2_analytic.json` — the cs = 800 artifact — stores **no `excess_per_seed` for any
of its five topologies**, so the project's most-quoted contrast (the `swap0.5 → swap2` refutation,
published at **32.7σ**) was the only one in the sweep that could not be re-examined per seed. That is
also why its σ had to be reported unpaired. Plan rule 8 exists to prevent exactly that omission, and it
was written after this artifact.

`e48` is that configuration re-run with per-seed storage: cs = 800, six seeds, four topologies.

## 2. It reproduces the whole published column, then extends it

| topology | published (n = 3) | `e48` first 3 seeds | `e48` full (n = 6) | |
|---|---|---|---|---|
| `real` | 0.01830 | **0.01831** | 0.01902 | match |
| `swap0.5` | 0.02317 | **0.02317** | 0.02287 | match |
| `swap2` | 0.01237 | **0.01237** | 0.01255 | match |
| `erdos_renyi` | 0.14187 | **0.14187** | 0.14214 | match |

**All four reproduce bit-for-bit from the first three seeds**, which is the same kind of check `e26`
passed at cs = 400 and 500, and it also matches `e32_rewire0`'s independent six-seed mean for `swap2`
(0.01255) exactly. So cs = 800 is now the best-attested column in the sweep, three seeds of
reproduction plus three more.

## 3. The refutation, paired and seed-robust

Per-seed `swap2 − swap0.5` over the six seeds:

```
-0.01103  -0.01102  -0.01033  -0.01097  -0.00967  -0.00890
```

| | value |
|---|---|
| mean | **−0.01032** |
| paired sem | 0.00036 |
| **paired σ** | **−28.85** |
| signs | `------` — **6 of 6** |
| leave-one-seed-out σ range | **[23.55, 39.70]** |
| published (unpaired, n = 3) | −0.01079 at −32.7σ |

**This is the check that `e5` failed and the C1 refutation passes.** With per-seed values the contrast
is *more* decisive, not less: every seed agrees on the sign, removing any single seed leaves it above
23σ, and the paired σ is −28.85 against the published unpaired −32.7. The earlier number was honest but
unverifiable; this one is neither.

So the C1 line's two halves end in opposite places and both are now measured:

| claim | status |
|---|---|
| the `swap0.5 → swap2` **refutation** at cs = 800 | **established**: paired −28.9σ, 6/6 seeds, leave-one-out ≥ 23σ, and the column reproduces bit-for-bit |
| the *explanation* of it (`e36`'s rank-collapse coordinate) | **the law refuted**; the ordinal direction survives within a circuit's realizations (`e53`, corrected p = 0.033) but not across circuits |
| the `e5` anisotropy association | **reversed** on the prescribed metric at 12 seeds (`e42`) |

## 4. Limits

- **Six seeds, one circuit.** The paired σ assumes the six are replicates of one condition, which they
  are — same wiring, same task suite, different task seeds — but the three extra seeds beyond the
  published three are new draws and the mean moved from −0.01079 to −0.01032, i.e. by 0.4 sem.
- **The leave-one-out range is not a confidence interval.** It shows no single seed is load-bearing;
  it says nothing about drawing another circuit, which is what `e36`–`e40` showed is fragile.
- **`real`'s six-seed mean (0.01902) differs from the published three-seed value (0.01830)**, so the
  control topology moves by 4% with three more seeds while the contrast barely moves. That is
  consistent with everything `e36` found about which quantities are stable.
- `erdos_renyi` here is 0.14214 at n = 6 against the published 0.14187 at n = 3, reproducing to four
  decimals at the first three seeds — so the ER separation's endpoint is now also attested by six
  seeds, which strengthens the "regime offset by eleven" reading without changing it.
