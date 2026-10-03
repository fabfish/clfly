# The benchmark's metrics: four of five are implemented, one of five is recorded, and the forgetting metric the block rejects is the one the corpus stores

*2026-10-01 04:11. Runs: **none new** — `experiments/e302_the_benchmark_metrics.py` reads the FlyCL v0 block in
`docs/research_plan.md`, every module under `clfly/` and `experiments/`, and every payload under `runs/`, writing
`runs/e302_the_benchmark_metrics.json`. Seconds.*

## 1. The two sentences nobody had read

The FlyCL v0 block is a **contract with the code**, and `e185` reads two of its lists — the tasks it says are
implemented and the baselines it offers. Its **metrics paragraph** and its **comparability promise** had never been
read against anything, and they are what a benchmark's users act on: the metrics are what a number is quoted in, and
the promise is what makes two methods' numbers comparable.

## 2. The five metrics

| metric | implemented | carried by the corpus |
|---|---|---|
| average accuracy | `final_accuracy`, 111 occurrences in modules | **`final_accuracy`, 163 payloads** |
| decomposed forgetting | `decompose_forgetting` (`clfly/lgcl/`), and `drift_term` | **`mean_forgetting`, 163 payloads** |
| backward transfer | **nothing** | **nothing** |
| per-task observability spectrum | `observability` (`clfly/diagnostics/`) | **nothing** |
| pairwise task principal angles | `principal_angle`, `principal_angles` | **nothing** |

**M1 MET — the list names one thing the repository does not implement.** `backward transfer` occurs nowhere under any
spelling this instrument declares: no module, no flag, no artifact key. `e185`'s finding is the reason the arm is
spelled out rather than matched loosely, and the same defect was available here in the other direction — see §5.

**M2 MET — four of five are computed and one of five is recorded.** The block's metric list is almost entirely
**unrecorded**: the per-task observability spectrum and the pairwise principal angles are implemented in
`clfly/diagnostics/` and appear in no artifact of any kind, so a reader comparing methods on the benchmark the block
describes cannot get two of its five metrics out of the corpus at all.

## 3. The forgetting metric the block rejects is the one the corpus stores

The block is explicit about why it names a decomposed forgetting — the conventional metric *"rewards shrinkage and can
be gamed"*. The corpus's answer: **`decompose_forgetting` is a key in 0 payloads and `mean_forgetting`, the
conventional metric, in 163.** **M3 MET.** The metric the block prescribes to avoid gaming is computed by
`clfly/lgcl/metrics.py` and is stored by nothing; the metric it rejects is the corpus's forgetting field, in every arm
of every run, and it is the field the README's scoped front-page claim is written in.

## 4. The comparability promise rests on one order

The block promises **"fixed task orders and seeds, so numbers are comparable across methods"**. The corpus reads:

- **147 payloads record a named task list** over **6 suites** — `ov0_t0` to `ov0_t2`, `ov1_t0` to `ov1_t2`, three
  intermediate overlap rungs, and the assembly suite's `odour_identity`, `heading`, `odour_input`.
- **No suite records more than one order.** Every payload writes its suite's tasks in the suite's own naming order.
- **146 of the 147 record `seed0` 0**; the odd one out records 100.

**M4 MET.** The promise holds, and it holds **trivially**: no permutation of any suite has ever been run, so
"fixed task orders" is a property nobody has varied. A claim that a benchmark's numbers are comparable across methods
*because* the order is fixed is a claim about a variable the corpus has exactly one value of — and that is worth
saying before the order-free claim is repeated, not after.

## 5. Two self-reads had to be removed before any of this was true

The first run reported **5 of 5 metrics implemented** and `backward transfer` **carried by one payload**. Both were
the instrument reading itself: the module's own spelling table contains every name it looks for, and its own artifact
writes that table out, so `backward_transfer`, `bwt` and `backward transfer` all matched. The module now excludes its
own file and its own artifact **by name**, and the verdict moves from *nothing is missing* to *one metric is missing*.

That is `e185`'s defect reproduced in a new unit within a day of recording it, which is the reason its finding is
cited in this module's docstring rather than only in its own.

## 6. What it cannot do

**The instrument is lexical and the spellings are its definition.** A metric implemented under a name none of the
declared lists anticipates reads as absent, and a word that happens to occur in prose reads as present — so
`per-task observability spectrum` counts as implemented on the strength of `clfly/diagnostics/`'s docstring saying
*observability spectra*, and a stricter arm would want the module that computes it named. **M3 is about what the
corpus stores and not about what the repository can compute**: the decomposed forgetting exists, and a unit that
reads `clfly/lgcl/metrics.py` could produce it from stored quantities. **M4 is a claim about what the artifacts
record**: a runner that shuffled tasks internally and then wrote the suite's canonical list would pass, and nothing in
the corpus distinguishes that, so M4 says the order is not a variable the corpus varies and not that the loop iterates
in the order it writes. **And only artifacts carrying a `tasks` list of named objects are read**, which leaves the
analytic artifacts outside the order claim.

## 7. RE-READ 2026-10-01 04:37 — the code arm was reading docstrings

`e302`'s code arm counted a declared spelling anywhere in a module's text, and **a docstring is text**. `e303`
re-reads the same six spellings with every `STRING` and `COMMENT` token removed, and two move:

- **`decompose_forgetting` occurs once, in `clfly/lgcl/model.py`'s docstring, and in no code.** The docstring defers
  to `clfly.lgcl.metrics.decompose_forgetting`, and **`clfly/lgcl/metrics.py` does not exist**.
- **`observability` occurs three times, all in prose**, so the per-task observability spectrum is implemented nowhere
  rather than implemented and unrecorded.

**So M1's answer is bigger than this finding said and M2's is unchanged**: `backward transfer` and the per-task
observability spectrum are implemented **nowhere**, and the one metric that looks implemented under the block's own
name is implemented only through `mean_forgetting` — the conventional form the block rejects. The repaired reading is
**two of five implemented, not four of five**; the carried arm is untouched, because it counts keys in artifacts and
not words in modules. §5 recorded this unit reading its own spelling table as evidence; `e303` is the same defect one
level down, with a different module's documentation as the evidence
(`docs/findings/2026-10-01-the-metrics-against-definitions.md`).

## 8. RE-READ 2026-10-01 11:04 — **M4 has fired**: the corpus now holds a permuted suite

`e315` ran the corpus's **first permutation of a suite** — `ov1_t0, ov1_t1, ov1_t2` forwards and its full reversal —
so M4's invariant is over: **149 artifacts record a named task list over 6 suites, and one suite records more than
one order**, the second being the first reversed. M1, M2 and M3 stand unchanged.

That is what M4 was registered to catch and it is a **result, not a regression**: the claim was *"no permutation of
any suite has ever been run"*, `e310` measured what varying the order would cost, and `e315` varied it. The unit's
live test now asserts the **shape** of the violation — exactly one suite, two orders, each the other reversed —
rather than the absence
(`docs/findings/2026-10-01-the-order-the-runner-never-took.md`).

## RE-READ 2026-10-03: a card is not evidence, and the code arm read one

`e392` published the game card, and the card's metric clause names the block's metrics -- `backward transfer` among
them. This unit's code arm is a substring count over `clfly/` and `experiments/`, so it read a **description** of
the metric as an implementation of it: M1's absent list emptied and `backward transfer` looked implemented by being
named. A module that publishes a card carries every name by construction, exactly as this unit's own spelling table
does, and it is the same defect `e185`'s first version recorded -- a check that matches a word rather than evidence.
The carriers are now excluded with the auditors, and **M1's absent list is `backward transfer` again**: the metric
the block names and the repository does not compute.
