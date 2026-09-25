# A pre-flight on a synthetic level found the two dose reads disagreeing about a count mismatch: one crashed, the other vanished

**Date:** 2026-09-25
**A pre-flight unit done while `e193`'s last level runs.** The four shape claims and the two cost claims are registered
and `e194` judges them — but `e194` reads two other readers, and the artifact that decides the claims had not landed.
A reader that **refuses** when the artifact finally appears wastes the run that waited for it, and a refusal cannot be
told from a level that is not there. So the pending achieved overlap was exercised on a **synthetic** level at target
`--input_overlap 0.75` first — and the pre-flight failed on its first attempt, for a reason that had nothing to do
with the claims.

---

## 1. What the pre-flight found: a crash where a refusal belongs

`e191.dose_read` guarded its **anchor** pairing against a replicate-count mismatch, in a comment that names this exact
class:

> the replicate count has to agree before the pairing exists: without this a synthetic level paired against the live
> overlap-1 artifact raised a broadcast error inside `paired` rather than being refused, **which is the same class of
> defect as an arm with the wrong count in `e188`'s audit**.

It did **not** guard the pairing one step above it — the level against its admitted baseline — and a level with 4
replicates against the live 40 raised exactly that broadcast error:

```
ValueError: operands could not be broadcast together with shapes (4,) (40,)
  at experiments/e151_pertask_contrast_audit.py:129 in paired
  from experiments/e191_interference_across_lines.py:294 in dose_read
```

**A crash is worse than a refusal here**: the exception aborts the whole read, so the levels that *were* fine produce
nothing. The guard had been written for one pairing and not for the next one, four lines up.

`e188`'s mirror defect is the other way round, and is what the same comment calls "the arm with the wrong count":

```python
if a is None or b is None or a["n"] != b["n"]:
    continue          # the arm disappears from the read with no trace
```

A silent `continue` reads as *the artifact does not carry this arm*, which is a different fact.

## 2. The fix, in both readers and in both reports

- `e191` refuses with the counts named — *"replicate counts differ: `e116_r32_40reps.json` has 40,
  `synth075.json` has 4"* — instead of broadcasting, and its other silent `continue`s (an absent arm, a payload with
  no per-pair interference) now record a reason too.
- `e188` records the reason instead of `continue`ing.
- **And both reports print the refusals.** Without that the level's heading prints with no arms under it, which is the
  same "a refusal looks like an answer" shape the reader's `levels found` line was added for
  (`docs/findings/2026-09-25-the-midpoints-cost-is-a-learning-deficit-not-forgetting.md` §3).

## 3. The pre-flight as a test, and what it proves

A synthetic level at target 0.75, with its **config derived from `e116`'s** rather than written from scratch — the
admission rule compares every key, so a minimal config is refused for differing in `circuit_size`, `iters` and the
rest, and the pre-flight would then be testing the refusal instead of the read. Run through `e194.measure`, it now
produces verdicts for **all six** claims:

```
levels found: achieved 0.6
    S1: -35.6062  >= 40 -> FALSIFIER FIRED
    S2: -26.7671  < 50 -> MET
    ...
```

**What it proves**: the pipeline can read a level at the pending achieved overlap end to end — both dose readers, both
components, the analytic far, the two accounts, the per-arm decomposition — so the artifact that lands will be judged
rather than debugged. **What it does not prove**: any verdict. The synthetic numbers are arbitrary; the test asserts
that every claim *resolves* and that a 4-replicate level is refused, and never what the answer is.

## 4. Why no audit covered it

`e127` audits the plan's table, `e184` censuses citations, `e192` checks quoted numbers — **all of them read
documents**. This defect is in the code path between a registered claim and an artifact, and the only thing that
exercises it is a level that exists. That is why the registered claims get a reader before their artifact, and it is
also why the reader needs a *payload* before its artifact: a pre-flight is the reader's own unit test, and it found
something the reader's tests had not, because every existing test built its payload with a matching count.

**Rule 52 is added for it**: a guard written for one pairing is not a guard for the next, and a reader that drops a row
silently is a reader whose absences cannot be read.

## 5. What this does not license

- **That the real levels are free of the defect.** They are: every `e193` level and both baselines carry 40
  replicates, which is why the read has worked. The defect was latent and would have cost the level-0.75 read.
- **That the six claims will be MET or falsified.** §3.
- **That the pre-flight replaces the artifact.** It proves the plumbing, not the measurement; the claims are decided
  by `e193_r32_overlap075_methods_40reps.json` and nothing here touches that.
