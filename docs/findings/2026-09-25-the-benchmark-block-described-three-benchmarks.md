# The benchmark block described three benchmarks, and the code builds a fourth

**Date:** 2026-09-25
**Read of:** `docs/research_plan.md`'s `## The benchmark — FlyCL v0` block, `clfly/network/tasks.py`'s `SUITE_SPECS`,
`clfly/connectome/circuits.py`'s seed specs, the paper's own benchmark sections (`docs/paper/clfly-v1.md`), every
`runs/*.json`'s `config.methods`, and the annotation (`annotate.load_annotations()`, 139248 rows) read through
`circuits.extract`.
**Instrument:** `experiments/e185_benchmark_spec_audit.py`, tested in `tests/test_e185_benchmark_spec_audit.py`.

---

## 1. Three lists, and the block is a fourth

The block was written as a description: *"**Five sequential tasks**, each landing on a distinct circuit, driven
through the connectome"*. Three different lists exist in this repository, and they are not the same five.

| | list | members |
|---|---|---|
| the plan's block | **five modalities** | olfaction (OSN → AL → KC → MBON), visual motion (optic lobe → LPTC), heading (CX), looming (LC4), motor pattern (DN → VNC) |
| the paper's analytic substrate | **five assemblies** | odour identity (KC), odour valence (MBON + DAN), heading (CX), odour input (AL), innate odour (lateral horn) |
| the code | **three tasks** | `odour_identity` (KC in → MBON out), `heading` (PB/EPG-type in → CX out), `odour_input` (ALPN/ALLN in → KC out) |

**Two of the code's three are stages of the one olfactory pathway**, which is a property of the substrate rather
than of the design: the circuit is extracted from `MB_SEEDS`, `CX_SEEDS` and `AL_SEEDS` — mushroom body, central
complex, antennal lobe — so olfaction and the compass are what it contains. And the plan's block is a *fourth*
list: its five share only `heading` with the paper's five, and three of its five exist nowhere in the repository —
`LC4`, `T4`/`T5`, `LPTC`, descending neurons and the VNC appear in no module outside the annotation.

**Three of its names are not in the annotation's vocabulary either**: `OSN` (the olfactory sensory class is
`olfactory`, 2282 neurons), `LPTC` (the annotation carries `LPLC`, 460) and `VNC` (this is a brain dataset — 0
neurons).

## 2. Why this is a circuit away rather than a task spec away, measured

The obvious repair — add a line to `SUITE_SPECS` — does not work, and the reason is the seed choice plus the **soft**
budget. Adding the optic lobe to the same circuit at the same `--circuit-size 800`, and then adding the descending
neurons at 1500, gives this (each circuit built with `circuits.extract`, populations counted by the same prefix rule
the runner's `_population` uses):

| circuit | achieved | KC | MBON | CX | ALPN | T4 | T5 | optic | descending |
|---|---|---|---|---|---|---|---|---|---|
| `mb+cx+al` @800 (what runs today) | **1307** | 335 | 35 | 309 | 182 | 0 | 0 | 0 | 0 |
| `mb+cx+al+optic` @800 | **2262** | **50** | 35 | 239 | 182 | 55 | 53 | 1410 | 0 |
| `mb+cx+al+optic+dn` @1500 | **4013** | 87 | 35 | 241 | 182 | 101 | 97 | 1948 | 472 |

Two things follow, and neither was in the block:

- **the achieved circuit grows by 73% at the same budget** (1307 → 2262), because the budget is soft and every cell
  type keeps at least one member — and the optic lobe contributes hundreds of cell types;
- **the existing tasks' input populations collapse.** Kenyon cells go from **335 to 50** at the same
  `--circuit-size 800`: the olfactory task's input population is cut by **85%** by adding a modality to the same
  circuit. So a five-modality benchmark is not "three more lines": it either builds **separate circuits per task**
  (which breaks the shared-body premise the continual-learning question rests on) or it changes the substrate that
  every existing number was measured on. The `e8e` result that forgetting is mild because the tasks are separated
  at the input is a fact about *this* seed set, and the dilution is the mechanism that would perturb it.

The neuron counts say the extension is otherwise cheap: `{cell_type=T4}` 6241, `{cell_type=T5}` 6005,
`{cell_type=LC4}` 207, `{super_class=descending}` 1303 are all in the annotation. What is missing is a circuit, and
the budget to hold one.

## 3. The baselines the block offered and the repository does not have

The block listed ten baselines. The corpus has actually run **five methods** — `naive`, `ewc`, `ewc-block`,
`ewc-block-rand`, `replay`, read from every artifact's own `config.methods` — and the repository implements the
`oracle` (the Kalman/RTS line) and the `frozen` and `joint` controls. **`SI`, `MAS` and `Online-EWC` appear nowhere
else in the repository and have never been run**: they were offered for two days and are now marked as proposed.

## 4. What replaced the block, and what the checker can and cannot see

The block now carries two marked lists — **implemented suite** and **proposed and not implemented** — plus a
baseline list, and `e185` checks three things: every task the code builds appears in the implemented list (and no
task named as proposed is one the code builds — that arm exists because the drift runs both ways), and every
baseline line is either a method the corpus has run or a control the repository implements. `--populations` prints
the fourth column of §2 for the block's own `{column=prefix}` probes, so a modality is added to the proposed list by
naming its population rather than by describing it.

**The known positive, stated exactly.** Against the block as it stood, the check fired **three** times — the code's
three task names were absent from a list of implemented tasks that did not exist — and **everything else in §1 and
§3 was read by hand and flagged by nothing**. That is the case for the contract rather than for the check: a
description with nothing marked in it can be read as any of three benchmarks and cannot be wrong in a way a machine
can see.

**Four false positives were produced by the checker itself while it was being built, and each one cost a rule**:
the section's **heading** terminated the first list, so it reported the code's own suite as missing from the block
that names it; the list collector ran to the end of the block, so the baseline check read **prose** and flagged
`e185` (the checker's own name), `clfly/bench/` (the reference framework) and the three baselines the block says are
*not* implemented; the mark's own line was scanned, flagging `e185` a second time; and the `{column=prefix}` written
inside the block's explanation of the probe syntax was read as a probe. Each is pinned by a test.

## 5. Falsifiers and limits

- **The checker reads lists, not meaning.** Every claim it makes is "this token is or is not in the code/corpus"; a
  block that described a benchmark in prose alone would satisfy it while being wrong, which is exactly why the
  contract is a marked list and why the numbers live in `--populations` as printed output rather than as assertions.
- **The census numbers are properties of the seed set and the budget**, printed rather than asserted, so a change to
  `DEFAULT_SPECS` or to `subsample_fraction` moves them without reddening anything. The claim that survives such a
  change is the *direction*: adding a modality to a shared circuit dilutes the others at a fixed soft budget.
- **What would refute §1**: any module outside the annotation mentioning `LC4`, `T4`/`T5`, `LPTC` or the VNC; the
  search is stated in §1 and is one `grep`. What would refute §2: a seeded circuit holding the optic lobe **and**
  the current KC population at `--circuit-size 800` — the check is `circuits.extract` with the seeds in §2's table.

## Reproduce

```
uv run python -m experiments.e185_benchmark_spec_audit                # the contract: flags 0 on the block as it stands
uv run python -m experiments.e185_benchmark_spec_audit --populations  # plus the probe counts (§2's last three columns)
uv run pytest tests/test_e185_benchmark_spec_audit.py -q
```
