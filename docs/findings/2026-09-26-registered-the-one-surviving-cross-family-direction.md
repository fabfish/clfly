# Registered: the one surviving cross-family direction, with a designed drawing base behind it

*2026-09-26 13:20. Runs: `e2_topology_gap` at cs 800, support {20, 160}, `--topologies alloy1,inalloy1,erdos_renyi`,
`--seeds 3 --seed0 0 --q 0.02 --no-realized --geometry-only --rewire-seed {2,3}` — **four runs, three cells each,
~25 min**, to be written as `e241_support{20,160}_rs{2,3}.json`. The two existing drawings per support (`e221_*_rs0`
and `rs1`) complete a **four-drawing** base; `--geometry-only` is the right economy because the claim is about the
task geometry's rank, not the penalty.*

## 1. What is being re-tested, and why a designed base

`e240` re-tested this session's cross-family claims on the drawings the corpus happened to have, and of the six cells
it could read, **exactly one showed a direction the drawings did not wash out**: at cs 800/support 160 the median
pairwise `alloy1`/`inalloy1` *rank* ratio is **5.81×**, against 0.85× at cs 800/support 80 and 2.31× at cs
800/support 20. Three things make that worth a designed test rather than another accidental one:

- it is the **first** cross-family effect in this thread to survive more than one drawing;
- it is **not monotone in the support share** (support 20 → 2.31×, 80 → 0.85×, 160 → 5.81×), so it is not the
  share mechanism the plan's earlier rows tested (those moved the *one-side level* by 1.16–1.42×);
- and it rests on **two** drawings per side, i.e. four pairs — `e240`'s own lesson is that this is thin.

## 2. The registered claims

- **G1 — the direction survives four drawings.** At cs 800/support 160 the median pairwise `alloy1`/`inalloy1` rank
  ratio over the four drawings (six pairs) is **above 2**. **Falsifier**: at or below **1.25**, which would say the
  5.81× was a two-drawing accident; **null**: 1.25–2.
- **G2 — the two supports do not agree.** The support-20 median over four drawings is **below 5** (the support-160
  value). **Falsifier**: support 20 at or above **10**, which would say both supports show a strong direction and the
  difference between them is magnitude only; **null**: 5–10.
- **G3 — the drawings dominate here too, on a designed base.** At **each** support, the larger of the two one-side
  families' drawing spreads (max/min of the rank over its four drawings) exceeds the between-family difference of
  their medians. **Falsifier**: the between-family difference larger at both supports — which would be the first
  designed case in this thread where a single drawing *is* enough.

**Reported**: every drawing's three ranks at both supports, the six pairwise ratios per support, and the two
one-side families' means, medians and spreads.

## 3. What it cannot do

- **Four drawings are still a sample**, and the four are `rewire_seed` 0–3 — a designed *axis*, not a population.
- **`--geometry-only` means these cells carry no penalty**, so nothing here speaks to the excess; they are screening
  cells and outside `e207`'s join by construction.
- **One circuit size and one `rho`** (cs 800, `rho` 0.9 = the builder's default), so the support effect it tests is
  the one `e240` found and not a support × size interaction.
- **`real` is not among the topologies** here (matching `e221`'s cells), so the contrast is between the two one-side
  nulls and not against the unrewired graph.
