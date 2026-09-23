# `e142` pre-registered: the overlap family at a narrow read-out — where the body is load-bearing

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Planned artifacts:** `runs/e142_r32_overlap1.json` and `runs/e142_r32_overlap1_frozen.json`, each
`--circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --lam 3e-3 --train 96 --test 48 --noise 1.0 --classes 4
--support 80 --shared-head --input-overlap 1.0 --readout-size 32 --fisher-batches 32 --seed0 0 --repeats 40
--methods naive`, with the second adding `--frozen-body`.
**Comparators, and they are on the same construction one step away:**
`runs/e133_r32_naive_ewc_40reps.json`'s `naive` arm (**+0.0750 ± 0.0088**, forty replicates, `--input-overlap
0.0`, read-out 32 — the same `make_overlap_suite` at `overlap = 0`), and `runs/e125_r32_frozenbody.json`'s
frozen body at the same setting (**0.8134** accuracy against the plastic arm's **0.9125**).

## Why this is a new question and not a re-run

**The overlap family was measured once, and it was measured in the one regime where the answer cannot be about
the wiring.** `docs/findings/2026-09-22-benchmark-measured-its-decoder.md` drove the tasks into input
populations with exactly uniform overlap at 3 replicates and found **no monotone trend and tiny forgetting** — at
*identical* input populations, +0.003 ± 0.009, *lower* than the disjoint case — and concluded that input-level
separation is **not** why forgetting is mild.

**The same finding's next section is what makes that conclusion conditional**: at its read-out (the whole state),
a `--frozen-body` diagnostic gave **0.944 against the plastic arm's 0.951**, i.e. **the recurrent weights were
not load-bearing at all** — a linear decoder over ~1300 features solved the tasks by itself. A benchmark in which
the plastic weights can be frozen with no loss has **no forgetting to create**, whatever is done to the inputs.

**And the narrow read-out is the change that fixed that.** At read-out 32 on the same construction, the frozen
body reaches only **0.8134** against a plastic **0.9125** — a **0.10** accuracy gap, and it is the setting every
result this session reports. **So the overlap question has never been asked where it means something**, and it is
the second of the two routes §8's item 4 names for a harder connectome-constrained benchmark: *"either by
freezing the offsets, or by a task family whose solution genuinely requires routing through the wiring"*.

## The predictions

- **C1, the premise, and it is measured rather than assumed.** At read-out 32 with **identical** input
  populations, the frozen body's final accuracy is **≥ 3σ below** the plastic arm's. If it is not, then sharing
  the input population has **restored decoder-solvability**, the body is not load-bearing for this family either,
  and P1 is void — and that would itself be the finding, because it would say the wiring's load-bearingness is a
  property of the *read-out width* rather than of the task family.
- **P1, the fire.** **Raising the input overlap raises the forgetting**: overlap 1.0's `naive` forgetting is
  **larger** than `e133`'s overlap-0.0 `naive` (+0.0750), resolved at **≥ 3σ** over the forty shared seeds. *The
  direction is registered, and it is the opposite of what the 3-replicate whole-state run found.*
- **P2, the reading that would follow.** If P1 holds, then a task family whose tasks **share their input
  population** is the route §8's item 4 names, and it is available **without freezing or penalising anything** —
  which matters because `e125`/`e138`'s route changes the model.
- **Falsifier.** Overlap 1.0's forgetting is **within 2σ of `e133`'s `naive`**. Then the 2026-09-22 refutation
  **survives at the narrow read-out**, input separation is not what makes this benchmark mild even where the body
  matters, and §8's second route is **empty** — the only way to a harder benchmark would be to change the model
  (freeze or penalise the offsets), which is a statement about the benchmark's design rather than about the
  connectome.
- **Registered because a knife-edge is a registered outcome rather than an excuse**: the family's **learnability**
  is reported per task in both arms. The 3-replicate whole-state run learned it at 0.958/0.903/0.979; if at
  read-out 32 the tasks' `learned` accuracies collapse toward chance, then the family is **too hard rather than
  harder** and the forgetting it shows is uninterpretable — so the learning numbers are part of the verdict and
  not a caveat.

## What this cannot settle, in advance

- **One read-out (32), one overlap value (1.0), one seed set, and the shared head.** The suite supports overlap
  0.25/0.5/0.75 and the ten-neuron resolution exists (`e7`'s ladder), so a *shape* in overlap is a second fire;
  and per-task heads instead of a shared head would change what the body must do, which is also not varied here.
- **The comparator is a different suite from the default one.** `--input-overlap 0.0` picks its input populations
  **at random** and the default suite uses identified circuits (`KC → MBON`, `CX`, `ALPN → KC`), so `e133`'s
  `naive` is the right comparator for *overlap* and is not the same tasks. Nothing here is a claim about the
  default suite.
- **Forty replicates with a per-repeat sd of ~0.05** puts the 3σ threshold at an effect of about **0.024**, so a
  modest overlap effect is invisible at this n — and the direction, not the size, is what is registered.
- **And it does not touch the method question**: no penalty and no replay is run, so the fire can say that the
  *problem* is harder and cannot say anything about which method handles it.
