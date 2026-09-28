# An existence premise the corpus falsifies: three artifacts carry the 128-batch Fisher the paper says none do

*2026-09-28 20:20. Runs: **none new** — `experiments/e270_an_existence_premise_falsified.py` scans the corpus for the
thing the paper says does not exist, writing `runs/e270_an_existence_premise_falsified.json`. Seconds. **Two sentences
of the paper were corrected in the same fire.***

## 1. The item: a different kind of stale sentence

`e268` closed supersession for **numbers**: a registry names a quoted number, the finding that moved it and the
replacement. An **existence premise** — "no artifact on disk carries X" — is not superseded by a finding; it is
falsified by the corpus, and it is the kind of sentence a reader can check in one command. Two instruments, two kinds
of stale sentence.

The paper states one such premise **twice**, in two scopes:

    no artifact on disk carries a 128-batch Fisher at all

## 2. What the scan says

The corpus carries **three** artifacts with `fisher_batches` 128:

| artifact | replicates | cell |
|---|---|---|
| `e101_rate_fb128` | 5 | cs 800, λ 0.003, `cell_class` |
| `e102_rate_fb128_rerun` | 5 | cs 800, λ 0.003, `cell_class` |
| `e96_fisher_batches_128_1seed` | 1 | cs 800, λ 0.1, `cell_class` |

**V1 MET — the premise is false as written.** **V2 MET — and it is true as intended**: all three carry fewer than
sixteen replicates, so no *powered* run used 128 batches, which is what the sentences are doing in their paragraphs.
The fix is therefore a qualification and not a retraction — but the written form is the one on the page, and it is the
one a reader falsifies first.

## 3. And the same audit catches a forwarded number in the wrong cell

The paper's forward-looking section carries:

> `e178` runs at 144, which is conservative: at that sd a 0.0152 effect reads at **3.6σ**

**V3 MET, and the arithmetic is right.** `0.0152 / (0.051108 / √144) = 3.57σ` — but `0.051108` is `e60`'s per-replicate
sd and 144 is `e178`'s replicate count, and those are **two different cells**: `e60` is cs 800 with λ 0.1 and `e178`
is cs 300 with λ 1.0. At the cell whose sd the sentence uses the corpus holds **two** artifacts — `e60` itself at
sixteen replicates and its three-replicate precursor — and **the largest carries sixteen**. The artifact that does run
144 replicates is another cell, where the same contrast reads **0.28σ**.

So the sentence forwards a conservative-looking number for a run the record never made, in the specific way `e265`
found orders arms differently. It is the same defect class as `e261`'s: **arithmetic across configurations, stated as
if inside one.**

## 4. The registered claims (V1-V3, all MET)

| claim | measured |
|---|---|
| **V1** | the paper states the premise twice; the corpus carries 3 artifacts with a 128-batch Fisher |
| **V2** | all three carry fewer than sixteen replicates (1, 5, 5), so no powered run used one |
| **V3** | the forwarded arithmetic gives 3.57σ at 144 replicates; the cell it uses holds 2 artifacts, the largest at 16, and the 144-replicate run is another cell |

**Both sentences now carry a `CORRECTED 2026-09-28` clause in the paper** naming the three artifacts, the power
qualification, and the cell difference. `e192` (the paper's number audit) and `e268` (the supersession registry) both
stay green, and `e268`'s own registry does **not** contain these sentences — which is the point: it checks numbers, and
a premise is not a number.

## 5. What it cannot do

It checks **existence and not meaning**, so a premise that is true and misleading passes it. The scans read artifacts
that carry both a `config` and a `methods` block, so a run recorded another way is invisible. V2's bar of sixteen
replicates is a convention taken from the line's own budgets and not a tested boundary. And nothing here says whether
the paragraphs around these sentences are right — only that these two can be falsified as written, which is what a
reader does first.
