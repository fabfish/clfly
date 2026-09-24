# The readership table has decided its first `noise` cell, and the chain the level-knob read rests on

**Date:** 2026-09-25
**Read of:** `runs/e160_field_readership.json` (the table, unchanged code) against the corpus as it now stands,
one artifact after `e167`'s first arm landed. No new script: this is what the census says now.

---

## 1. `noise` is read by `ewc`, at forty replicates

`noise` had been **`possibly read` for every arm** since the table was built, because no pair of artifacts had
ever differed in it alone — `e166`'s census of single-field manipulations never listed it. One artifact changes
that:

| arm | `noise` verdict | evidence |
|---|---|---|
| `ewc` | **`read`** | **`e141_r32_ewc_lam3e-4` vs `e167_r32_noise0.5_lam3e-4`, n=40, `only noise`** |
| `naive` | `possibly read` | the only candidate pair is multi-field (`classes`+`environment:unrecorded`+`fisher_batches`) |
| `ewc-block`, `ewc-block-rand`, `replay` | `possibly read` | no pair of theirs differs in `noise` alone |

**And the pair is as clean as the design allows**: `e141` and `e167` are the same command except `noise`, at forty
papered seeds, and the artifact's whole purpose was to be that difference. **This is the table's first
`noise` decision and it is a strong one (n=40), where the corpus's other decided cells rest on n=5 or n=1.**

## 2. What the second arm will settle, and what it will not

`naive`'s row is the one the level-knob read needs, and it is **not** decided: the pair that would decide it —
`e167`'s two arms, differing in `noise` alone with both recording their environment and sharing a key set — needs
its second member, which is running. **So the fire that reads the noise-2.0 end will also decide the `naive` row
for free**, which is the kind of side effect worth reporting rather than discovering later.

**And the distinction matters for `e171`'s read.** That read compares `e167`'s `naive` with **`e133`'s**, which
differ in **`noise` and `lam`** — two fields, not one — and it is licensed because the table says **`lam` is
unread by `naive`** on clean n=40 evidence (`e116_r32_40reps` against `e125_r32_plastic`, and `e144` against
`e153`). So the level step at 3.55σ is attributable to `noise`, and the chain is:

```
lam unread by naive      (n=40, two pairs, from the table)
  => e167's naive at noise 0.5 differs from e133's only in what naive can read
  => the -0.0312 step is noise's, not lam's
  => the gain's -0.0370 step is formed at a level noise moved
```

**A read that compares two artifacts differing in two fields is only as good as the verdicts on the extra
fields**, and this one is checked rather than assumed — which is `e171`'s docstring's claim and this note's
verification of it.

## 3. What this cannot settle

- **`noise`'s effect on the arms that have no pair**: the three other arms remain `possibly read`, and `naive`
  waits for the second artifact. Nothing here says anything about the wiring family or about the block arms.
- **One field's one decision is not a mechanism.** That `ewc` moves with `noise` is what a penalty *must* do —
  its Fisher is estimated from data the noise changes — and the interesting quantity is not the verdict but the
  size of the movement, which is `e171`'s subject and not the table's.
- **And the table's own churn is the caveat**: every artifact added decides cells it was not run for (this one,
  one cell at n=40), and every count in it is as-of-a-run. The plan's rows now say so rather than quoting totals.
