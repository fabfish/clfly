"""What a result artifact has to record for this benchmark's metrics to be recomputable by someone else.

The FlyCL v0 block calls its reference framework *"a shared protocol that CL-for-SNN work currently lacks"*. A shared
protocol is a claim about **what a result contains**, and this module is that claim made checkable: eight fields, each
with the reason a third party needs it, and a census over `runs/`.

    required field          why a reader who is not the author needs it
    --------------------    -------------------------------------------------------------------------------
    a task list             names the suite, so two results are about the same tasks and the order is readable
    a seed                  says which replicate this is, so results are paired rather than pooled
    an eval size            says which held-out sample the numbers are on -- the axis `e286` measures
    `final_accuracy`        the accuracy the benchmark reports
    `mean_forgetting`       the forgetting the benchmark reports
    a retention matrix      the per-task levels, which is what makes the decomposition of `e304` computable
    a read-out draw         the fingerprint of the read-out the run actually used, which is `e103`'s requirement
    a code revision         the epoch the numbers came from, which is what makes a re-run comparable

Each reason is a sentence about a reader's task and not about tidiness, and the tests name them one at a time. **A
field a runner records but a reader cannot use is not one of these**: `e205` found three spellings of a duration and
`e184` found three kinds of citation, so the predicates below read the spelling the corpus's own readers read.

**What this is not.** *It is not a schema*: it says what must be *findable* and not where, so `seed0` under `config`
and under a top level both count. *It is not complete*: a benchmark that also wants the per-task observability
spectrum or the pairwise principal angles would add two rows, and this module is the eight a reader needs today.
*And conformance is not quality*: an artifact can carry all eight and be wrong, which is every other unit's business.
"""

from __future__ import annotations

import json
from pathlib import Path


def _replicates(payload: dict) -> list[dict]:
    """Every replicate row of every arm, flattened, so a field is looked for where the arms keep it."""
    methods = payload.get("methods")
    if not isinstance(methods, dict):
        return []
    out = []
    for entry in methods.values():
        if isinstance(entry, dict) and isinstance(entry.get("replicates"), list):
            out += [r for r in entry["replicates"] if isinstance(r, dict)]
    return out


def has_task_list(d) -> bool:
    return bool(d.get("tasks"))


def has_seed(d) -> bool:
    return isinstance((d.get("config") or {}).get("seed0"), int)


def has_eval_size(d) -> bool:
    return bool((d.get("evaluation_noise") or {}).get("n_eval"))


def has_accuracy(d) -> bool:
    return any("final_accuracy" in r for r in _replicates(d))


def has_forgetting(d) -> bool:
    return any("mean_forgetting" in r for r in _replicates(d))


def has_retention(d) -> bool:
    return any("retention" in r for r in _replicates(d))


def has_readout_draw(d) -> bool:
    return bool(d.get("readout"))


def has_revision(d) -> bool:
    return bool(d.get("code_revision")) or bool((d.get("environment") or {}).get("torch_version"))


#: The contract, in the order the report prints it, each row a field and the reason a reader needs it.
FIELDS = (
    ("task list", has_task_list, "names the suite, so two results are about the same tasks"),
    ("a seed", has_seed, "says which replicate this is, so results are paired rather than pooled"),
    ("an eval size", has_eval_size, "says which held-out sample the numbers are on"),
    ("final_accuracy", has_accuracy, "the accuracy the benchmark reports"),
    ("mean_forgetting", has_forgetting, "the forgetting the benchmark reports"),
    ("a retention matrix", has_retention, "the per-task levels, which make `e304`'s decomposition computable"),
    ("a read-out draw", has_readout_draw, "the fingerprint of the read-out the run actually used"),
    ("a code revision", has_revision, "the epoch the numbers came from"),
)
NAMES = tuple(f[0] for f in FIELDS)


def carries(payload: dict) -> list[str]:
    """Which of the required fields this payload has, in the contract's order."""
    return [name for name, predicate, _ in FIELDS if predicate(payload)]


def conformant(payload: dict) -> bool:
    return len(carries(payload)) == len(FIELDS)


def census(root=Path("runs"), collapse: bool = True) -> dict:
    """Every artifact read for the contract, and the counts that say where the record stops.

    ``collapse`` drops the corpus's second executions of experiments it already holds (`e301`), so a conformant
    experiment counts once however often it was run.
    """
    from clfly.bench import corpus

    skip = corpus.repeat_paths(root) if collapse else set()
    per_field: dict[str, int] = {n: 0 for n in NAMES}
    by_count: dict[int, int] = {}
    blocks: dict[tuple, int] = {}
    examples: dict[tuple, str] = {}
    n = 0
    for path in sorted(Path(root).glob("*.json")):
        if path.name in skip:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        n += 1
        got = tuple(carries(payload))
        for name in got:
            per_field[name] += 1
        by_count[len(got)] = by_count.get(len(got), 0) + 1
        blocks[got] = blocks.get(got, 0) + 1
        examples.setdefault(got, path.name)
    return {"artifacts": n, "fields": NAMES, "per_field": per_field, "by_count": by_count,
            "blocks": [{"carries": list(k), "n": v, "example": examples[k]}
                       for k, v in sorted(blocks.items(), key=lambda kv: -kv[1])],
            "conformant": by_count.get(len(FIELDS), 0),
            #: K4 is about the middle: a count of two, three or four of the eight, which is what a gradient in the
            #: record would look like. The ends are the blocks.
            "gaps": sorted(k for k in by_count if 1 < k < len(FIELDS) - 3)}
