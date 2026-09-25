"""E187 -- which suite the corpus actually ran, and the correction that forces on the benchmark's description.

`clfly/network/tasks.py` has **two** builders, and they answer different questions:

- `make_suite` drives each task into an **identified circuit** -- Kenyon cells, central-complex ring neurons,
  antennal-lobe neurons -- and is what the plan's benchmark block, `e185` and `e186` describe;
- `make_overlap_suite` gives each task an **input support drawn at random** with an exact, uniform overlap, so
  "overlap = 0" is the default suite's *structure* with **randomly chosen neurons rather than identified circuits**,
  which is what its own docstring says.

Which one a run used is recorded, and this counts it: `config.input_overlap` is absent-`None` for the assembly
suite and a number for the overlap suite, while the task names carry the family (`ov0_t0` against
`odour_identity`) -- **two independent signals, and their agreement is the check.**

    python -m experiments.e187_suite_provenance

**The measurement, which is why this audit exists: 109 artifacts and 1660 replicate-runs are the overlap family at
overlap 0.0, 11 artifacts and 440 replicates are overlap 1.0, and the assembly suite is 20 artifacts with no
high-replicate run at all.** So the corpus's measured forgetting is overwhelmingly forgetting between **random
input supports**, not between the olfactory and compass circuits the block names -- and `e186`'s reachability table,
which measures the *assembly* suite, was reported two fires ago as a fact about "the two tasks the corpus measures
every day". That sentence is wrong and is corrected in
`docs/findings/2026-09-25-which-suite-the-corpus-actually-ran.md`.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
from pathlib import Path

RUNS = Path("runs")
ASSEMBLY = "assembly suite (identified circuits, `make_suite`)"
OVERLAP = "overlap suite (random supports, `make_overlap_suite`)"


def family(config: dict, tasks: list[dict]) -> tuple[str, str]:
    """The suite a payload's tasks came from, from two independent signals.

    Returns the family and the evidence. The config key is the direct record; the task names are the builder's own
    convention (`ov{overlap}_t{index}` against the assembly names). A payload whose two signals disagree is the only
    thing this function cannot classify, and it says so rather than picking one.
    """
    name = (tasks[0].get("name") or "") if tasks else ""
    by_name = OVERLAP if name.startswith("ov") else (ASSEMBLY if name else "no task names")
    key = config.get("input_overlap", "absent")
    if key is None:
        by_config = ASSEMBLY
    elif key != "absent":
        by_config = OVERLAP
    else:
        # An artifact older than the flag. The overlap builder is reachable only through `--input-overlap`, so a
        # payload with no such key and an assembly task name predates the flag rather than disagreeing with it --
        # the same reading `e172` takes of a config that is a subset of today's parser.
        by_config = ASSEMBLY if by_name == ASSEMBLY else "input_overlap absent from config"
    if by_name == by_config:
        return by_name, f"config.input_overlap={key!r}, first task name {name!r}"
    return "UNCLASSIFIED: the two signals disagree", (f"config says {by_config} (input_overlap={key!r}) while the "
                                                     f"task name {name!r} says {by_name}")


def audit(runs_dir: Path = RUNS) -> dict:
    counts: collections.Counter = collections.Counter()
    repeats: collections.Counter = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)
    disagreements = []
    for p in sorted(glob.glob(str(runs_dir / "*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(d, dict):
            continue
        tasks = d.get("tasks") or []
        if not tasks:
            continue
        fam, why = family(d.get("config") or {}, tasks)
        counts[fam] += 1
        r = (d.get("config") or {}).get("repeats")
        if isinstance(r, int):
            repeats[fam] += r
        if len(examples[fam]) < 6:
            examples[fam].append(Path(p).name)
        if fam.startswith("UNCLASSIFIED"):
            disagreements.append({"artifact": Path(p).name, "why": why})
    return {"artifacts_with_tasks": sum(counts.values()), "by_family": dict(counts),
            "replicates_by_family": dict(repeats), "examples": dict(examples),
            "disagreements": disagreements, "n_disagreements": len(disagreements)}


def report(res: dict) -> int:
    print(f"   payloads carrying tasks                 : {res['artifacts_with_tasks']}")
    print(f"   {'family':52} {'artifacts':>9} {'replicates':>11}")
    for fam, n in sorted(res["by_family"].items(), key=lambda kv: -kv[1]):
        print(f"   {fam:52} {n:9} {res['replicates_by_family'].get(fam, 0):11}")
    print("   examples, so a reader can open one:")
    for fam, names in res["examples"].items():
        print(f"        {fam[:44]:46} {', '.join(names[:3])}")
    print(f"   payloads whose two signals disagree     : {res['n_disagreements']}")
    for d in res["disagreements"]:
        print(f"        {d['artifact']}: {d['why']}")
    return res["n_disagreements"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.runs)
    n = report(res)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
