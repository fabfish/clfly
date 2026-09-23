# `e115`, pre-registered: forty replicates on the one step an interior minimum stands on

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, two runs; artifacts `runs/e115_r300_40reps.json`,
`runs/e115_r512_40reps.json` (in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 300 and 512, `--repeats 40`**, `--seed0 0`.
**Context:** `docs/findings/2026-09-23-the-axis-reduces-to-one-statement.md`, whose cost table says the 512 → 300
step needs **22 replicates per side (≈ 16 min)** and whose count of resolving pairs is **4 of 21, all involving
read-out 32**.

---

## 1. Why forty and not the twenty-two the cost table computed

The cost table used the per-repeat sd measured at **five** replicates (0.0180 at read-out 512, 0.0226 at 300) and
a 2σ target, which puts the observed 0.0125 difference at **2.03σ** — *exactly* at the criterion. A design that
lands on its own threshold cannot answer the question it is asked, and it answers it with an sd estimated from
five points. **Forty replicates per side costs about 30 minutes** at ≈ 22 s per replicate and puts the same
difference at **≈ 2.7σ**, so the question becomes "does it resolve" rather than "is it exactly at 2".

**This is a deliberate departure from the registered count, and the reason is arithmetic rather than taste**: the
table's number was the *minimal* one, and a minimal design's failure is uninterpretable where a comfortable
one's is decisive.

## 2. The control, and it is checked before anything else

The training seed is `seed0 + 100·r`, so **replicates 0–4 of a forty-replicate run use exactly the seeds of the
stored five-replicate runs** at the same configurations. Therefore:

> **the first five replicates of each new run must be bit-identical to the stored run's replicates.**

**If they are not, the run is a separate sample rather than an extension and the extra thirty-five replicates do
not add power** — which is `e61`/`e68`'s lesson, where a sixteen-replicate run turned out to be a second sample
of the same configuration whose first five replicates did not match the five-replicate run's. That case was
discovered after the fact; here it is a pre-registered check with a defined consequence.

## 3. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **C0, the control** | the first five replicates of each new run match the stored run's **bit-for-bit**, so the extension is legitimate |
| **P1** | with forty replicates per side, the **512 → 300 difference** (observed +0.0125 against the 5-replicate sds) **reproduces its sign and reaches ≥ 2σ** unpaired |
| **P2** | the forty-replicate sds are **within a factor of two** of the five-replicate estimates (0.0180 and 0.0226) — otherwise the cost table's counts were computed from poor estimates, which is itself the finding and would revise the 22-replicate and 200-replicate figures |
| **Falsifier** | the difference's **sign flips**, or it is **below 2σ** at forty replicates — in which case the one step the interior minimum rests on is **not resolved**, the axis stays at the single surviving sentence (read-out 32 forgets more than four others), and the cost table's method is vindicated while its conclusion about this step is not |

**The three failure modes are separated on purpose.** A control failure means the run cannot answer the question;
a P2 failure means the *arithmetic* behind every other registration on this axis is wrong; only a P1 failure
means the effect is not there. Collapsing them would make the outcome uninterpretable, which is what the last
five fires have been about.

## 4. What this cannot settle

- **Two read-outs.** It tests one step of a seven-point axis; the other five steps keep their cost-table entries,
  and the 700 bump's 200-replicate price is untouched.
- **The draw is still one draw per read-out.** The draw span (0.0125 at read-out 300) is **not** averaged over,
  so a difference of 0.0125 that "resolves at 2.7σ against the per-repeat spread" is still **at** one draw-span;
  the honest reading of a positive result is *"the difference is larger than the training noise"*, not *"the
  difference is a property of the read-out size"*. Separating those requires averaging over draws, which is a
  different and more expensive design than either this fire or the cost table's.
- **Forty replicates is forty samples.** If P1 holds, the statement is about this configuration and this draw;
  the paper's §4.7 already says the line's binding limit is the benchmark's own spread rather than the replicate
  count, and this fire is a measurement of how far replicates can move that limit at one point.
