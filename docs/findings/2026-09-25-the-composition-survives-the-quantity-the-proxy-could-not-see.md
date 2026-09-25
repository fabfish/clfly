# The composition survives the quantity the proxy could not see

**Date:** 2026-09-25
**Read of:** both task lines' **own** interference terms — `runs/e7_interference.json`'s six-level controlled sweep
for the analytic line, and `methods.<m>.replicates[r].interference[j]["per_task"][k]` in the `e188` artifacts for
the network line — split by task distance and paired over replicates.
**Instrument:** `experiments/e191_interference_across_lines.py`, tested in
`tests/test_e191_interference_across_lines.py`. **Corrects `e189`'s retraction**, which was made on a proxy.

---

## 1. The proxy, and why there is no need for one

`e189` compared the analytic line's `interference` with the network line's **accuracy drop on older tasks** — a
proxy, because that is what the retention matrix gives. Its standard errors are large: on the accuracy drop the
network line's **far** component cleared 2σ in **one of nine** comparisons, and `e189` therefore retracted its own
first claim that the far component is shared between the lines ("a small rise in both lines and unresolved in
both").

**The network line records an interference account of its own**, per pair, for every run:
`e8_rate_network.py` stores, for each task `j` with `j < T-1`, the first-order damage from the displacement that
training task `k` caused — `interference[j]["per_task"][k]["first_order"]`. So both lines can be split by task
distance **on quantities that share a name and a construction** (a first-order term in a loss's Taylor expansion),
without a proxy.

## 2. The two lines, on their own terms

**Analytic** (`e7`'s controlled sweep, six overlap levels, 5 tasks):

| | level 0.00 | 0.10 | 0.25 | 0.50 | 0.75 | 1.00 | direction |
|---|---|---|---|---|---|---|---|
| **near** (d = 1) | +0.0258 | +0.0220 | +0.0149 | +0.0051 | +0.0023 | **−0.0013** | **falls** |
| **far** (d > 1) | +0.0084 | +0.0071 | +0.0079 | +0.0088 | +0.0098 | **+0.0111** | **rises** |

**Network** (the nine comparisons `e188` admitted, interference per ordered pair, per-replicate component means
paired across the overlap arms):

| comparison | near Δ (ov1 − ov0) | far Δ (ov1 − ov0) |
|---|---|---|
| naive, disjoint vs identical inputs | **+0.1234 ± 0.0158 = 7.8σ** | **+0.0882 ± 0.0283 = 3.1σ** |
| naive, second overlap-0 arm | **+0.1234 ± 0.0158 = 7.8σ** | **+0.0882 ± 0.0283 = 3.1σ** |
| naive, third overlap-0 arm | **+0.1234 ± 0.0158 = 7.8σ** | **+0.0882 ± 0.0283 = 3.1σ** |
| ewc-block (biological side partition) | **+0.0514 ± 0.0143 = 3.6σ** | **+0.0486 ± 0.0150 = 3.2σ** |
| replay | +0.0005 ± 0.0003 = 1.6σ | **+0.0009 ± 0.0004 = 2.4σ** |
| ewc-block-rand, draw 1 | **+0.0921 ± 0.0170 = 5.4σ** | **+0.0535 ± 0.0251 = 2.1σ** |
| ewc-block-rand, draw 2 | **+0.0888 ± 0.0107 = 8.3σ** | **+0.0382 ± 0.0135 = 2.8σ** |
| ewc + frozen bias, λ = 3e-3 | **+0.0182 ± 0.0027 = 6.8σ** | **+0.0111 ± 0.0018 = 6.3σ** |
| ewc + frozen bias, λ = 3e-4 | **+0.0652 ± 0.0064 = 10.2σ** | **+0.0624 ± 0.0085 = 7.4σ** |

**near: 8 of 9 rise at 2σ, none fall** (the one unresolved is `replay` at 1.6σ). **far: 9 of 9 rise at 2σ**, from
2.1σ to 7.4σ.

## 3. The composition, which is now measured twice over

- **The adjacent pairs are where the two lines disagree, and both are resolved there.** The analytic near component
  falls monotonically and crosses below zero; the network's rises, in eight of nine comparisons. This is `e189`'s
  localisation, and it survives on the quantity that shares a name rather than on the proxy.
- **The distant pairs move the same way in both lines, and the network's far component is resolved.** Nine of nine,
  2.1σ–7.4σ. So `e189`'s first version was right and its retraction was an artefact of the **accuracy drop**'s
  error bars: on that quantity the far change was the size of its own error, and on the account's own terms it is
  five to twenty times it.

**So the finding is the composition, and the correction is to the correction**: raising the input overlap raises
*both* components of the network line's interference, most steeply the adjacent one; the analytic line's adjacent
component moves the *other* way; and the analytic line's distant component moves the same way as the network's —
which is the "shared far trend, opposite near trend" sentence `e189` printed first, deleted second, and which the
name-matched quantity restores.

## 4. Falsifiers and scope

- **What would refute it**: a network near component that falls with overlap on its own interference terms, or an
  analytic near component that rises — either moves the disagreement out of the adjacent pairs. The gate asserts
  the current tallies, so a new artifact on this axis either reproduces them or fails the test.
- **The two accounts are still not the same construction.** The analytic term comes from a task's measurement
  operator under a linear propagator; the network term is a gradient–displacement inner product at the final body.
  They share the first-order form and the name, not a derivation — which is why §2 reports both lines' numbers in
  full rather than a single "correlation between the lines".
- **The one refusal is declared**: `e153` (the overlap-1 arm at λ = 1.0) is not a pair for a penalised method,
  because `lam` is not inert there.
- **A defect this instrument found in itself**: the first version checked only the *first* arm for the interference
  terms, so a payload without them came through as a row of NaNs instead of a refusal — the same mistake `e188`'s
  sibling audit made with `retention`, and now refused for both arms.

## Reproduce

```
uv run python -m experiments.e191_interference_across_lines      # both lines, both components, 0 contradictions
uv run pytest tests/test_e191_interference_across_lines.py -q
```
