# Which suite the corpus actually ran — and it is not the one the block describes

**Date:** 2026-09-25
**Read of:** every `runs/*.json` that carries tasks (145 payloads), its `config.input_overlap`, its `config.repeats`
and its task names, against `clfly/network/tasks.py`'s two builders.
**Instrument:** `experiments/e187_suite_provenance.py`, tested in `tests/test_e187_suite_provenance.py`.
**Corrects `e186`**, whose §4 reported a reachability table about the *assembly* suite as a fact about "the two tasks
the corpus measures every day", and the plan's benchmark block as `e185` left it, which named one builder.

---

## 1. Two builders, and the corpus is overwhelmingly the second

`clfly/network/tasks.py` builds tasks two ways, and they ask different questions:

- **`make_suite`** drives each task into an **identified circuit** — Kenyon cells, central-complex ring neurons,
  antennal-lobe neurons — so a task's identity is biological *and* the analytic line's five assemblies name the same
  populations;
- **`make_overlap_suite`** gives each task an **input support drawn at random** with an exact, uniform overlap. Its
  own docstring says what `overlap = 0` is: *"fully disjoint inputs (the default suite's structure, but with
  randomly chosen neurons rather than identified circuits)"*.

Which one a payload used is recorded in two places, and both are read here: `config.input_overlap`
(absent-`None` for `make_suite`, a number for `make_overlap_suite`) and the task names (`ov0_t0` is the overlap
family's convention, `odour_identity` the assembly suite's).

| family | artifacts | replicates |
|---|---|---|
| overlap suite — random input supports | **120** | **2439** |
| assembly suite — identified circuits | 25 | 107 |
| payloads whose two signals disagree | **0** | — |

**So 96% of this project's continuous-learning replicates are between randomly drawn input supports, and 4% are
between the identified circuits the benchmark block, `e185` and `e186` describe.** The overlap family splits 109
artifacts at `input_overlap = 0.0` (disjoint supports, 1660 replicates at ≥ 20 repeats) and 11 at `1.0` (identical
inputs, 440 replicates); the assembly suite has **no high-replicate run at all** — its largest `repeats` is 5.

**The five payloads the classifier first refused are the interesting corner**: `e8_basis.json`,
`e8_class_incremental.json`, `e8_fisher_batches.json`, `e8_rate.json`, `e8_tuned_lambda.json` carry **no
`input_overlap` key at all** while their task names are assembly names. They are not disagreements: the overlap
builder is reachable only through `--input-overlap`, so a payload without the key **predates the flag**, which is
the same reading `e172` takes of a config that carries a subset of today's flags. Reading only the config key would
have misclassified them; reading only the task names would have had nothing to check against.

## 2. The correction `e186` owes

`e186`'s §4 measured pairwise reachability between the five assemblies in the circuit and drew a conclusion about
"the two tasks the corpus measures every day": that `heading` reaches none of `odour_identity` and none of
`odour_input` within two hops. **The reachability numbers are right and the sentence is wrong**: in the overlap
family — 96% of the replicates — the tasks are random supports, so their reachability is a property of the draw, not
of the assemblies, and the corpus's measured forgetting is not (mostly) forgetting between the olfactory and compass
circuits. What survives is narrower and still worth having: *in the assembly suite, whose high-replicate
measurement does not exist yet, the heading input population is two-hop disconnected from the other two.*

That is also why the extension `e185` registered and `e186` measured lives in an awkward place: the assembly suite
is the one that could be extended to the analytic line's five assemblies, and it is the one the corpus has barely
run. The extension is therefore worth running for **two** reasons at once — five assemblies instead of three, and a
high-replicate measurement of the identified-circuit suite itself, which the project does not currently have.

## 3. What the plan block now says, and how it is checked

The block's implemented list gains the overlap family beside the assembly suite, because a reader who opens
`runs/` will mostly find the first: the list now carries the three assembly specs `e185` checks *and* the
`ov0`/`ov1` convention with its replicate counts. The contract is unchanged — every `SUITE_SPECS` name must appear
in the list and no task named as proposed may be one the code builds — and `e187` is the second instrument on the
same question, counting which builder produced which payload.

## 4. Falsifiers and limits

- **The classification is by the payload's own two records**, so a payload that agrees on both signals but was in
  fact built by the other builder would be invisible. What would show it: a payload whose task *input sizes* are the
  constant `support` of the overlap builder (80) rather than the assembly sizes (335, 55, 278) — a check this audit
  does not run, and the natural next one.
- **Replicates are `config.repeats` summed over artifacts**, not the number of completed replicate rows inside each
  payload: a run that died mid-way still counts its configured total. The artifacts here all carry a full
  `replicates` list, which is why the two agree, but the count is a configuration count and is stated as one.
- **What would refute §1**: an `ov0`-named payload whose config records `input_overlap: None` (the classifier
  reports that as unclassified rather than choosing), or a majority of replicates in the assembly family — the check
  is two `Counter`s over `runs/*.json`.

## Reproduce

```
uv run python -m experiments.e187_suite_provenance                      # the split, with examples to open
uv run python -m experiments.e187_suite_provenance --json-out ONE.json
uv run pytest tests/test_e187_suite_provenance.py -q
```

## RE-READ 2026-10-07: the overlap family's replicate dominance has been walked past parity

The finding's first sentence is that the corpus's replicates are **overwhelmingly** the overlap suite. That was measured
at **22x** when `e187` wrote it, `e178`'s 144 assembly-suite replicates moved it to **9.7x**, and this project's own
closed-loop line has now taken it past parity: the assembly family holds **3035** replicates against the overlap family's
**3029**, a ratio of **0.998**. Every one of the runs that closed the gap is an assembly-suite run by this unit's own
classifier -- `e399` to `e460`, the whole closed-loop line -- so the sentence above describes the corpus's **history**
and not its state, and the live test's strict inequality is **dropped rather than re-based**, as `e305`'s exhibit multiple
and `e168`'s exposure ratio were, and for the same reason: a comparison of two counts that both grow with the corpus is a
level one arithmetic away.

What the live test asserts now is the classification, which is what the unit is about: **the two signals never disagree**
(**0**), both families are counted, the artifact counts sum (**352**), and the overlap family's artifacts -- **137**
against the assembly family's **215** -- are still a large minority, the **137** being what the `>= 100` bound was always
meant to keep. So the reversal is in the **replicates** and not in the **artifacts**: the corpus has always had more
assembly-suite *files* than overlap-suite ones, and what changed on 2026-10-07 is that the closed-loop line gave the
assembly side more *seeds* as well. The one thing this RE-READ cannot say is whether the closed-loop suite is the assembly
family in the sense the finding meant: the classifier puts it there by the two signals that never disagree, and the loop's
tasks are built by a third builder (`fly_env.make_env_task`) that neither of the finding's two families names.
