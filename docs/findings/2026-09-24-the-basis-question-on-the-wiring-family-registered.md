# `e144` pre-registered: the basis question on the family whose difficulty is in the wiring

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; launched when the CPU frees.
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Planned artifact:** `runs/e144_r32_overlap1_methods_40reps.json` —
`--input-overlap 1.0 --readout-size 32 --shared-head --repeats 40 --fisher-batches 32 --lam 3e-3
--replay-per-task 96 --replay-batch 8 --methods naive,ewc,ewc-block,ewc-block-rand`.
**Comparator for C0a:** `runs/e142_r32_overlap1.json`'s `naive` — the identical command with one method, forty
replicates, so its **`naive` row must be per-replicate identical**.

## Why this is the question and why it might have a different answer here

**The paper's central network result is that the *granularity* of the partition helps and the *biology* does
not.** On the base family the biological block partition never beats its **group-size-matched random** control —
`e135` measures the contrast at five replicates as **−0.0125**, and the two arms' contrasts against `naive` move
by **0.42σ, 0.21σ and 0.48σ** when the unpenalised channel is removed from every arm, i.e. method-independently.

**`e143` changed which difficulty the harder family has.** At overlap 1.0 the extra forgetting **survives
freezing the 800 offsets** (**5.04σ**), so it lives in the **26,568 connectome-masked weights** — the structured
channel — while on the base family **70%** of the forgetting is carried by offsets that **no partition can act
on at all**. **A partition of the synapses competes with the offsets for the forgetting the metric reports, and
in the base family the offsets win.** So the basis question has, until now, only ever been asked on a benchmark
where most of the forgettable signal was invisible to both arms of the comparison — **and on this family it is
not.**

## The arms, the controls and the predictions

- **C0a, must hold.** The `naive` row is per-replicate identical to `e142_r32_overlap1.json`'s — the same command
  at the same seeds — so the whole table is on one footing. (`e142`'s `naive` is itself a *new* baseline rather
  than `e133`'s, because `--input-overlap 1.0` is a different suite.)
- **P1, the fire.** **`ewc-block`, the biological `cell_class` partition, beats `ewc-block-rand`, its group-size
  matched random control, resolved at ≥ 3σ** over the forty shared seeds. *The direction is registered because it
  is the one the paper's central claim denies*, and the interest is that this is the first family in which the
  forgetting the metric reports is carried by the weights the partition acts on.
- **P2, descriptive and registered.** Whether the block arms beat the **diagonal** on this family — on the base
  family `ewc` is the best Fisher arm (confound-robustly), so a reversal here would be a second-order surprise
  worth reporting rather than a prediction.
- **Accuracy is a registered cost**: the harder family is 2.7σ below the base family's accuracy already
  (0.8939 against 0.9125), so a penalty that costs more of it is a cost against a smaller budget.
- **Falsifier.** The biological-minus-random contrast is **within 2σ of zero**. Then the null survives a family
  whose forgetting is in the wiring, the basis answer does not depend on where the forgetting lives, and the
  paper's *"granularity, not biology"* conclusion is a property of the substrate rather than of the base family's
  channel structure. **That is a real possibility and it is the one the project has already found three times**:
  a claim that looked like a configuration's property turned out to be about the measurement.

## What this cannot settle, in advance

- **One read-out (32), one overlap value (1.0), one partition (`cell_class`), one λ (3e-3), forty replicates.**
  At a per-repeat sd of ~0.055 the 3σ threshold is an effect of about **0.025**, so a small advantage is
  invisible here — and `e101`'s sweep found the Fisher batch count moves the penalty's effective strength, so
  **λ and the batch count are confounded as everywhere in this project**.
- **It is the *block* partition against its matched control, not the biology question as a whole**: `e66`'s
  fourteen candidates, the eigenbasis and the adaptive truncations were all measured on the linear substrate, and
  nothing here transfers them to this family.
- **One seed set.** The base family's basis contrast has been measured at five replicates and at forty, and the
  two differ; this family gets one measurement at forty and no five-replicate companion.
- **And it says nothing about `replay`**, which `e135` found is the method whose margin the unpenalised channel
  was inflating — and which `e140` is measuring at forty on the base family now.
