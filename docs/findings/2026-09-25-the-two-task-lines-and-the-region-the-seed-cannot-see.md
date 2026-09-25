# The two task lines, and the 551 neurons the central-complex seed cannot see

**Date:** 2026-09-25
**Read of:** `clfly/connectome/tasks.py`'s `TASK_ASSEMBLIES`, `clfly/network/tasks.py`'s `SUITE_SPECS`,
`clfly/connectome/circuits.py`'s `SeedSpec`s, the annotation (`annotate.load_annotations()`, 139248 rows, four
label columns) and every `runs/*.json`'s `config`.
**Instrument:** `experiments/e186_task_lines_compared.py`, tested in `tests/test_e186_task_lines_compared.py`.

---

## 1. Two lines, five assemblies against three tasks, compared value by value

`e185` found the network suite covers three of the analytic line's five assemblies. Comparing them *value by value*
is where the defects are, and three of different sizes came out:

| difference | size | what it is |
|---|---|---|
| `odour_valence`, `innate_odour` | 68 and 149 neurons in the circuit | the two assemblies the network suite does not have at all — the registered extension |
| `odour_input` omits `ALIN` | 24 whole brain, 10 in the circuit | the analytic assembly of that name includes it, the network spec does not: **two results that both say "odour input" are about different populations** |
| `heading` named `PB` and `NO` | **0 and 0** | two values that select **no neuron in any column** of the annotation |

The third is the one that was a mistake rather than a design difference, and it is now measured rather than
suspected: no annotation value **contains** `PB` in any of the four label columns (`cell_type`, `cell_class`,
`cell_sub_class`, `supertype`), and the noduli are spelled `Nod1`/`Nod2`/`Nod3`/`Nod5` — 10 neurons whole brain, and
**0 of them in the `mb+cx+al` circuit under either spelling**, so the fix is inert in every artifact and the values
were dropped with their intent recorded in the notes. The heading task's input population is, and always has been,
the **55** `EPG`/`PFN`/`PEN`/`ER` neurons.

## 2. The region the seed cannot see

The same question asked of the seed specs is where the real find is. `CX_SEEDS` asks `cell_class` for
`("CX", "FB", "EB", "PB", "NO", "LAL")`, and **five of the six values select nothing there**:

| value | as asked (`cell_class`) | exists as | in the circuit | why |
|---|---|---|---|---|
| `CX` | 2875 | ✓ | 309 | the class the seed actually selects |
| `FB` | **0** | `cell_type` `FB*` **593** | kept | the fan-shaped body is **inside** `cell_class=CX`, so the class keeps it |
| `EB` | **0** | **nowhere, any column** | absent | — |
| `PB` | **0** | **nowhere, any column** | absent | — |
| `NO` | **0** | `cell_type` `Nod*` 10 | absent | the noduli exist and are in no circuit built so far |
| `LAL` | **0** | `cell_type` `LAL*` **551** | **absent** | **all 551 are `super_class=central` with no `cell_class` at all (NaN)** |

**The lateral accessory lobe is 551 neurons that this project's circuit has never contained, because the seed asks
a column those neurons do not have a value in.** They are not missing from the annotation — they are in it, labelled
`central`, with an empty `cell_class`. So no `cell_class` seed can select them, and the seed that names `LAL` looks
like it covers the region: that is the defect this audit exists to make visible. The two other zeros behind real
populations are different again — `FB` is covered redundantly by `CX`, and `Nod*` is small and genuinely out of the
circuit — which is why the three are listed separately rather than counted together.

**This one is not fixable by editing the seed.** Asking `LAL` of `cell_type` (or adding a second seed spec) adds
~551 candidate neurons to a circuit whose budget is soft and already oversubscribed, so every existing number would
be measured on a different substrate. It is therefore **registered, not applied**: the finding's claim is that the
benchmark's "central complex" is `cell_class=CX` and nothing else, and the correction belongs in a run whose
config records the new specs.

## 3. What the runs actually read out, and why the spec read-outs are usually inert

A network task's read-out is the spec's population only when the suite is built with per-task heads. With
`--shared-head` the read-out is one decoder over the whole state or over a random draw, and **the tasks then differ
only in where the stimulus enters** — which is the condition `make_suite`'s own docstring says makes the recurrent
weights load-bearing. Read from every artifact carrying `shared_head`:

| how the corpus read the tasks out | runs |
|---|---|
| one shared draw of `--readout-size` neurons | **117** |
| per-task heads — the spec populations **are** the read-outs | **17** |
| the whole state, one shared head | **11** |

So the spec read-outs matter in 17 runs, and in those the `heading` task has a property worth stating: its input
population (55 neurons of `EPG`/`PFN`/`PEN`/`ER`) is **entirely inside its read-out** (`cell_class=CX`, 309
neurons) — **55 of 55 neurons in both**. The stimulus is injected into the decoder's own inputs, so that arm's
heading accuracy is not evidence that the recurrent body routed anything. The other two specs have zero overlap.

## 4. The extension's measured basis

The two assemblies the network suite lacks are already in the circuit, and the connectome says what a task on them
could read out. Pairwise reachability within the circuit, from each assembly to each other within two hops:

| from \ to | odour_identity | odour_valence | heading | odour_input | innate_odour |
|---|---|---|---|---|---|
| odour_identity (335) | 334 | 67 | 8 | 221 | 144 |
| odour_valence (68) | 334 | 68 | 38 | 249 | 92 |
| heading (55) | **0** | 11 | 49 | **0** | 2 |
| odour_input (288) | 333 | 68 | 12 | 288 | 149 |
| innate_odour (149) | 66 | 13 | **0** | 145 | 85 |

Both candidate inputs reach the rest of the circuit (68 and 149 neurons reaching 249 and 145 of `odour_input`), so
the extension is a spec away as `e185` said. The table also shows the two tasks that are **not** connected in the
circuit at either end: `heading`'s neurons reach **none** of `odour_identity` and **none** of `odour_input` within
two hops, and `innate_odour` reaches **none** of `heading`. The two tasks the corpus measures every day are
unreachable from each other in the substrate at this distance — a fact about the 55-neuron heading input population
that is worth having before reading a forgetting matrix as interference.

## 5. Falsifiers and limits

- **Every zero here is a statement about this annotation**, which is one FlyWire release with four label columns.
  A value that selects nothing today may select hundreds in the next release, which is exactly why the dead values
  were recorded in a note and not deleted from the seed spec's intent.
- **The reachability table is a two-hop reachability, not a functional claim.** Zero reachable neurons within two
  hops is not "no influence": it is "not through a path of length ≤ 2 in this circuit". The claim that would be
  refuted by a three-hop path is stated with its bound.
- **What would refute §2**: any `cell_class` value in the annotation that starts with `LAL` — the check counts the
  column directly, and the count is 0. What would refute §3: a `shared_head` artifact whose `config` means per-task
  heads and carries a read-out size; the three modes partition the 145 runs that carry the key.

## Reproduce

```
uv run python -m experiments.e186_task_lines_compared             # the value-level and corpus checks
uv run python -m experiments.e186_task_lines_compared --circuit   # plus §4's table and the overlaps
uv run pytest tests/test_e186_task_lines_compared.py -q
```
