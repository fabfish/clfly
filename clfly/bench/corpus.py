"""Which files under ``runs/`` are one experiment written twice.

Every census in this project reads the corpus as ``runs/*.json``, so it counts **files**. On 2026-09-29 the corpus
gained two files that are one experiment: ``e287_frozenbias_suite1440_40reps.json`` and
``e288_frozenbias_suite1440_40reps.json`` are the same configuration, the same draws and the same five arms at forty
replicates, written by two executions of the same runner. They differ in four bookkeeping keys and in nothing else --
the output path, the wall clock, the cpu time and the code revision the runner recorded when it started.

That is a **repeat**, and it inflates every census that globs the directory. `e286`'s sample-swap census went from
three swaps to seven, `e295`'s comparisons from 26 to 28 and `e296`'s from 40 to 42 -- not because the corpus learned
anything but because one experiment was counted twice. The fix belongs in the **reader** and not in the file: a
census should count experiments, and a result nobody wrote up twice is still one result (``e301``).

The detector is deliberately narrow. Two artifacts are one experiment only if they agree on

  * the ``config`` **minus** :data:`VOLATILE_CONFIG`, since ``json_out`` says where a file was written and not what
    was run;
  * the eval size, ``evaluation_noise.n_eval``, because the same model on two held-out samples is `e285`'s and
    `e286`'s subject and not a repeat;
  * the draw blocks ``readout``, ``partition_draw`` and ``support_draw``, for the same reason;
  * the arm set, and within it every shared replicate row on :data:`TRAIN_FIELDS`, with at least one of those fields
    actually **present** on both sides -- a field neither file records reads as equal and must not be allowed to
    carry the verdict on its own.

Two independent runs of one configuration seeded the same way are deterministic and will also match, which is the
point: :func:`pairs` cannot and should not distinguish "the runner was launched twice" from "the runner was launched
once and reproduced", because the artifacts cannot. What it *can* say is that the corpus holds one experiment and
not two.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

RUNS = Path("runs")
#: The `config` key that records where the runner was told to write rather than what it was told to run.
VOLATILE_CONFIG = ("json_out",)
#: The per-replicate fields that are functions of the training and not of the evaluation or the clock.
TRAIN_FIELDS = ("losses", "theta_drift", "bias_norms", "retention_loss", "interference", "full_train_loss")
#: The top-level keys that are properties of one execution rather than of the experiment.
VOLATILE_PAYLOAD = ("code_revision", "cpu_time_s", "timing_s", "environment")
#: The draw blocks: two files that drew them differently are two experiments whatever else agrees.
DRAWS = ("readout", "partition_draw", "support_draw")


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def arms(d: dict) -> list[str]:
    """The arms that carry replicates, so a summary entry is not mistaken for a trained one."""
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return sorted(a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates"))


def config_signature(d: dict) -> str | None:
    """The ``config`` minus :data:`VOLATILE_CONFIG` -- the identity of the run rather than of the file."""
    cfg = d.get("config")
    if not isinstance(cfg, dict):
        return None
    return json.dumps({k: v for k, v in cfg.items() if k not in VOLATILE_CONFIG}, sort_keys=True, default=str)


def eval_size(d: dict) -> int | None:
    n = (d.get("evaluation_noise") or {}).get("n_eval")
    return int(n) if n else None


def shared_training(da: dict, db: dict) -> dict:
    """Per shared arm: how many rows were paired, how many training fields were present, and whether they agree.

    ``present`` counts the fields **both** sides record for the paired row, so a field that only one side carries is
    counted as unrecorded rather than as a difference -- and :func:`is_repeat` refuses a pair whose every field is
    unrecorded, which is what stops two analytic artifacts with no training at all from reading as one experiment.
    """
    out = {}
    for m in sorted(set(arms(da)) & set(arms(db))):
        ra, rb = da["methods"][m]["replicates"], db["methods"][m]["replicates"]
        n = min(len(ra), len(rb))
        present = sum(1 for f in TRAIN_FIELDS
                      if any(f in r for r in ra[:n]) and any(f in r for r in rb[:n]))
        ok = len(ra) == len(rb) and all(all(x.get(f) == y.get(f) for f in TRAIN_FIELDS) for x, y in zip(ra, rb))
        out[m] = {"paired": n, "present": present, "identical": bool(ok and present)}
    return out


def is_repeat(da: dict, db: dict) -> bool:
    a, b = arms(da), arms(db)
    if not a or a != b or len(a) != len(b):
        return False
    if config_signature(da) is None or config_signature(da) != config_signature(db):
        return False
    if eval_size(da) is None or eval_size(da) != eval_size(db):
        return False
    if any(da.get(k) != db.get(k) for k in DRAWS):
        return False
    return all(t["identical"] for t in shared_training(da, db).values())


def _paths(da, db, prefix: str) -> list[str]:
    """The dotted paths at which two payloads disagree, ignoring the two volatile classes."""
    if isinstance(da, dict) and isinstance(db, dict):
        out: list[str] = []
        for k in sorted(set(da) | set(db)):
            if k in VOLATILE_PAYLOAD:
                continue
            child = f"{prefix}.{k}" if prefix else k
            if k not in da or k not in db:
                out.append(child)
            else:
                out += _paths(da[k], db[k], child)
        return out
    if isinstance(da, list) and isinstance(db, list):
        if len(da) != len(db):
            return [prefix]
        out = []
        for i, (x, y) in enumerate(zip(da, db)):
            out += _paths(x, y, f"{prefix}[{i}]")
        return out
    return [] if da == db else [prefix]


def differing_paths(da: dict, db: dict) -> list[str]:
    """Every key path at which two payloads disagree, excluding :data:`VOLATILE_PAYLOAD` and ``config.json_out``."""
    a = dict(da)
    b = dict(db)
    for d in (a, b):
        if isinstance(d.get("config"), dict):
            d["config"] = {k: v for k, v in d["config"].items() if k not in VOLATILE_CONFIG}
    return _paths(a, b, "")


def pairs(root=RUNS, minimum_replicates: int = 1) -> list[dict]:
    """Every pair of files that is one experiment, canonical member first, plus the evidence that it is one."""
    groups: dict[tuple, list[Path]] = defaultdict(list)
    for p in sorted(Path(root).glob("*.json")):
        d = load(p)
        if d is None or not arms(d):
            continue
        groups[(config_signature(d), eval_size(d), tuple(sorted(arms(d))))].append(p)

    out = []
    for members in groups.values():
        if len(members) < 2:
            continue
        members.sort(key=lambda p: p.name)
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                da, db = load(a), load(b)
                if da is None or db is None or not is_repeat(da, db):
                    continue
                if min(t["paired"] for t in shared_training(da, db).values()) < minimum_replicates:
                    continue
                out.append({"canonical": a.as_posix(), "duplicate": b.as_posix(),
                            "arms": arms(da), "replicates": min(len(da["methods"][m]["replicates"])
                                                                for m in arms(da)),
                            "training": shared_training(da, db),
                            "differing_paths": differing_paths(da, db)})
    return out


def groups(root=RUNS, minimum_replicates: int = 1) -> list[list[str]]:
    """The clusters of files that are one experiment, canonical member first.

    A cluster is the transitive closure of :func:`pairs`, because a configuration executed four times gives six
    pairs and one cluster: the count a finding reports is the number of **files** that are a second copy, which is
    the sum of the clusters' lengths minus their count.
    """
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[max(rx, ry)] = min(rx, ry)

    for p in pairs(root, minimum_replicates):
        union(p["canonical"], p["duplicate"])

    clusters: dict[str, list[str]] = defaultdict(list)
    for x in parent:
        clusters[find(x)].append(x)
    return [sorted(v) for _, v in sorted(clusters.items()) if len(v) > 1]


def repeat_paths(root=RUNS) -> set[str]:
    """The **names** of the non-canonical members, which a census that globs ``runs/*.json`` should skip."""
    return {Path(m).name for g in groups(root) for m in g[1:]}
