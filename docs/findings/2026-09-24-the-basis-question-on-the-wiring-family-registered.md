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

## Amendment, made before the first artifact lands: the control is a *population*, and one draw is one sample

**As first registered, `e144` would have evaluated P1 against a single draw of the matched-random partition.**
`experiments/e8_rate_network.py` builds `SynapsePartition.random_matched(bio, np.random.default_rng(args.seed0))`
**once, outside the replicate loop**, so all forty replicates of an `ewc-block-rand` arm share **one** partition
and that arm's sem contains **no draw variance at all**. **Rule 10 says the control is the *population* of
size-matched random partitions and one draw is one sample from it** — and the **linear** line implements exactly
that (`e3_basis_selection --control-draws`, which records `sd_across_draws`) — **so the network line has been
running its central biological-versus-random contrast with no mechanism to vary the control.**

**What is added, as a flag rather than a re-design.** `--partition-seed` names the draw (default `--seed0`, so
every artifact written before the flag is **bit-identical under an unchanged command**), and the artifact now
records `partition_draw.matched_random_draw_seed`, its group count and a **fingerprint** of the assignment, so two
artifacts' `ewc-block-rand` rows can be told apart without storing the partition. **The first `e144` run supplies
draw 0; two more runs at seeds 1 and 2 supply the rest**, and the in-flight artifact is dated by its missing
keyset as the pre-flag epoch (rule 27).

**How P1 is evaluated, amended in advance of the data.** The contrast is `ewc-block` minus the **mean of the three
`ewc-block-rand` draws**, with the standard error of the control's mean carrying the **between-draw** term: three
draws give that term **two** degrees of freedom, so **P1's ≥3σ threshold is now a three-draw control's**, and the
sd across draws is reported beside the mean whether or not the contrast resolves. The falsifier keeps its form —
the contrast within 2σ of zero — and is read on the averaged control too.

**And the same defect is in every `ewc-block-rand` row this project has**, which is why this is a finding and not
only a fix: `e135`'s five-replicate **−0.0125**, the paper's §4.2 block rows, `e140`'s arms in flight — **each is
one draw, and nothing in the record said so.** So the σ quoted for the base family's block contrast has been a sem
**without** the draw term, and rule 10's ≈1e-3 estimate of a coarse partition's draw sd is measured on the *linear*
substrate's excess rather than on this network's forgetting: **the network's draw sd is unmeasured until these
three draws exist**, and the honest form of every block contrast quoted before today is *"one draw"* rather than
*"the control"*.
