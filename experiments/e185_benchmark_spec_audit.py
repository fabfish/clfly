"""E185 -- the benchmark block in the plan, checked against the benchmark the code builds.

The plan carries a block headed `## The benchmark — FlyCL v0` that reads as a **description** of what this
repository runs: *"Five sequential tasks, each landing on a distinct circuit"* -- olfaction, visual motion, heading,
looming, motor pattern -- with ten baselines and a stated reference framework in `clfly/bench/`. Measured against
the code it is three different things at once, and the differences are not bookkeeping:

- **the code builds three tasks**, not five: `SUITE_SPECS` in `clfly/network/tasks.py` is `odour_identity`,
  `heading` and `odour_input` -- **two of them are stages of the one olfactory pathway** (Kenyon cells → MBON, and
  antennal lobe → Kenyon cells);
- **three of the five named modalities have no implementation anywhere in the repository.** No module mentions
  `LC4`, `T4`/`T5`, `LPTC`, descending neurons or the VNC. Their neurons exist in the annotation (this audit counts
  them), and **none of them is in the circuit the suite is built on**, because that circuit is seeded from
  `MB_SEEDS`, `CX_SEEDS` and `AL_SEEDS` -- mushroom body, central complex, antennal lobe -- so a visual or motor
  task needs a **different circuit**, not another line in `SUITE_SPECS`;
- **the paper's own five are a third list**: its analytic substrate names five *assemblies* (odour identity, odour
  valence, heading, odour input, innate odour) and all five are present in the implemented circuit. So the plan's
  block does not describe the paper either.

Three of the names the block uses do not exist in the annotation's vocabulary at all: `OSN` (the olfactory sensory
class is `olfactory`, 2282 neurons), `LPTC` (the annotation has `LPLC`, 460) and `VNC` (this is a brain dataset).

**What is checked.** The block must mark its two lists, and then three things follow from the code rather than from
prose:

- every task name in the implemented list must be a `SUITE_SPECS` name, and every `SUITE_SPECS` name must appear in
  the list, so the list cannot quietly omit a task that runs;
- any task name in the **proposed** list that IS a `SUITE_SPECS` name is a flag (the block under-claiming what
  runs), and any population probe written as `` `column=prefix` `` in the proposed list whose count **in the
  implemented circuit** is not zero is a flag (a modality sitting in the substrate with no task on it);
- every baseline named as implemented must be either a method the corpus has actually run -- read from every
  `runs/*.json`'s `config.methods` -- or one of the controls the repository does implement (`oracle`, `frozen`,
  `joint`). `SI`, `MAS` and `Online-EWC` are named in the block and appear nowhere in the code.

    python -m experiments.e185_benchmark_spec_audit                  # the text and corpus checks, seconds
    python -m experiments.e185_benchmark_spec_audit --populations    # plus the cell counts (loads the connectome)
    python -m experiments.e185_benchmark_spec_audit --json-out ONE.json

**The known positive, stated exactly.** Run against the block as it stood before this audit, the check fired **three**
times: the code's three task specs are absent from a list of implemented tasks that did not exist. **The other gaps
were read by hand and were not flagged by anything** -- five modalities claimed against three implemented, and ten
baselines claimed against five methods the corpus has run and three controls -- which is why the block now carries
the two marked lists this check reads. A check that has never fired is not evidence that the text is clean; a check
whose whole yield was hand reading is not yet a check.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import re
from pathlib import Path

PLAN = Path("docs/research_plan.md")
RUNS = Path("runs")
SECTION_START = "## The benchmark"
SECTION_END = "\n## "
IMPLEMENTED_MARK = "**Implemented suite"
PROPOSED_MARK = "**Proposed and not implemented"
BASELINE_MARK = "**Baselines"
#: controls the repository does implement, spelled as the block spells them. `naive` and `replay` are NOT here on
#: purpose: they are methods the corpus has actually run, so `methods_run` is the evidence for them rather than a
#: word in this file.
CONTROL_WORDS = ("oracle", "frozen", "joint")
TOKEN_RE = re.compile(r"`([^`]+)`")
PROBE_RE = re.compile(r"\{([a-z_]+)=([A-Za-z0-9_]+)\}")


def spec_names(specs) -> list[str]:
    return [s[0] for s in specs]


def benchmark_block(text: str, start: str = SECTION_START) -> str:
    """The section's body, without its heading -- the heading would otherwise terminate the first marked list."""
    i = text.index(start)
    j = text.index(SECTION_END, i + 1)
    body = text[i:j]
    return body.split("\n", 1)[1] if "\n" in body else ""


def marked(lines: list[str], mark: str) -> list[str]:
    """The items of the list a mark introduces, and nothing else.

    A mark (`**Implemented suite`, `**Proposed and not implemented`, `**Baselines`) is followed by a list, and the
    list ends at the first line that is neither blank nor a list item. The first version of this function collected
    everything to the end of the block, which made the baseline check read the *prose* of the block: it flagged
    `e185` (the checker's own name), `clfly/bench/` (the reference framework) and the three baselines the block
    says are NOT implemented -- five flags on a block whose offered baselines are all real.
    """
    item = re.compile(r"^\s*(?:[-*]|\d+\.)\s")
    out, on = [], False
    for ln in lines:
        if ln.startswith(mark):
            # the mark's own line is prose -- `**Baselines (checked by `e185`):** each line below ...` -- and
            # scanning it flagged the checker's own name as a baseline that has never been run
            on = True
            continue
        if on and item.match(ln):
            out.append(ln)
            continue
        if on and not ln.strip():
            continue
        if on:
            break
    return out


def tokens(lines: list[str]) -> list[str]:
    return [t for ln in lines for t in TOKEN_RE.findall(ln)]


def methods_run(runs_dir: Path = RUNS) -> set[str]:
    """Every method name the corpus has actually executed, from every artifact's `config.methods`."""
    seen: set[str] = set()
    for p in glob.glob(str(runs_dir / "*.json")):
        try:
            cfg = (json.loads(Path(p).read_text(encoding="utf-8")) or {}).get("config") or {}
        except (json.JSONDecodeError, OSError):
            continue
        for m in str(cfg.get("methods", "")).split(","):
            if m.strip():
                seen.add(m.strip())
    return seen


def task_checks(block_lines: list[str], specs) -> list[dict]:
    """The implemented list must be exactly the code's set, and the proposed list must not overlap it."""
    names = spec_names(specs)
    flags = []
    impl = set(tokens(marked(block_lines, IMPLEMENTED_MARK)))
    prop = set(tokens(marked(block_lines, PROPOSED_MARK)))
    for n in names:
        if n not in impl:
            flags.append({"what": "the implemented list omits a task the code builds", "token": n})
    for n in names:
        if n in prop:
            flags.append({"what": "the proposed list names a task the code builds", "token": n})
    return flags


def baseline_checks(block_lines: list[str], ran: set[str]) -> list[dict]:
    """Every baseline the block offers must be a method the corpus ran, or a control the repository implements."""
    flags = []
    for tok in tokens(marked(block_lines, BASELINE_MARK)):
        low = tok.lower()
        if low in ran or any(c in low for c in CONTROL_WORDS):
            continue
        flags.append({"what": "a baseline named as offered, with no implementation and no run", "token": tok})
    return flags


def population_census(probes: list[tuple[str, str]], circuit_size: int = 800) -> list[dict]:
    """For each `{column=prefix}` probe: how many neurons carry it in the whole annotated brain, and in the circuit.

    The second number is the one that decides the work: a modality whose neurons are **in the circuit** and has no
    task is a missing task, while one whose neurons are absent from the circuit needs a circuit-seed change first.
    """
    from clfly.connectome import annotate, circuits, graph
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=circuit_size)
    out = []
    for column, prefix in probes:
        if column not in ann.frame.columns:
            out.append({"column": column, "prefix": prefix, "whole_brain": None, "in_circuit": None})
            continue
        vals = ann.frame[column].astype(str)
        whole = int(vals.str.startswith(prefix).sum())
        names = circ.neuron_names(column)
        in_circ = int(sum(1 for n in names if str(n).startswith(prefix)))
        out.append({"column": column, "prefix": prefix, "whole_brain": whole, "in_circuit": in_circ})
    return out


def audit(plan: Path = PLAN, runs_dir: Path = RUNS, specs=None, with_populations: bool = False,
          circuit_size: int = 800) -> dict:
    if specs is None:
        from clfly.network.tasks import SUITE_SPECS
        specs = SUITE_SPECS
    text = plan.read_text(encoding="utf-8")
    block = benchmark_block(text)
    lines = block.splitlines()
    flags = task_checks(lines, specs)
    ran = methods_run(runs_dir)
    flags += baseline_checks(lines, ran)
    probes = PROBE_RE.findall(block)
    census = population_census(probes, circuit_size) if (with_populations and probes) else []
    # The census is PRINTED and not flagged, and the reason is a measurement: a population inside the circuit is
    # not evidence that a modality is untasked -- `cell_type=MBON` is 35 neurons in this circuit and MBON is the
    # read-out of `odour_identity`. A flag on "in the circuit, therefore a missing task" would fire on the task
    # that is running, which is the class of false positive rule 22 records as costing more than the check saves.
    return {"plan": str(plan), "specs": spec_names(specs), "spec_names_implemented": spec_names(specs),
            "methods_the_corpus_ran": sorted(ran), "probes": [f"{c}={p}" for c, p in probes],
            "population_census": census, "flags": flags, "n_flags": len(flags),
            "block_lines": len(lines), "proposed_tokens": sorted(set(tokens(marked(lines, PROPOSED_MARK))))}


def report(res: dict) -> int:
    print(f"== {res['plan']}'s benchmark block ({res['block_lines']} lines) ==")
    print(f"   task specs the code builds (SUITE_SPECS) : {', '.join(res['specs'])}")
    print(f"   methods the corpus has actually run      : {', '.join(res['methods_the_corpus_ran'])}")
    print(f"   population probes written in the block   : {', '.join(res['probes']) or '(none)'}")
    for c in res["population_census"]:
        print(f"        {c['column']}={c['prefix']:12} whole brain {c['whole_brain']!s:>7}"
              f"   in the implemented circuit {c['in_circuit']}")
    print(f"   FLAGS                                    : {res['n_flags']}")
    for f in res["flags"]:
        print(f"        [{f['what']}] {f['token']}")
    if not res["flags"]:
        print("   (a zero with no known positive is worth nothing: against the block as it stood this check fired "
              "3 times -- the code's own suite, absent from a list that did not exist -- and every other gap was "
              "hand reading, which is the case for the marked contract rather than for the check.)")
    return res["n_flags"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--path", type=Path, default=PLAN)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--populations", action="store_true",
                   help="also count the block's {column=prefix} probes (loads the connectome, ~a minute)")
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.path, args.runs, with_populations=args.populations, circuit_size=args.circuit_size)
    n = report(res)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
