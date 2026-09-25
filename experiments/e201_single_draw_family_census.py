"""E201 -- which of the corpus's FAMILIES are single-draw, i.e. make manipulation claims at one draw?

`e200` checks that the two sides of a DECLARED comparison drew the same thing, and today's work established the
complement it cannot see: **a family that varies a manipulation while holding every draw fixed has within-family
effects that are attributable, and generalizations that are untested.** The overlap axis was exactly that -- eleven
hours of claims measured at support draw 0 and read as properties of the overlap -- and nothing in the corpus could
see it, because a family with one artifact per configuration passes `e200` trivially.

`e198 --reconstruct` identifies the draw of 264 of the 299 live (artifact, draw) pairs, so this is answerable from
the metadata alone:

    python -m experiments.e201_single_draw_family_census
    python -m experiments.e201_single_draw_family_census --json-out runs/e201_single_draw_family_census.json

**Analysis only**; no artifact is re-measured.

## How a family is defined, and why that is the honest part

A family is a set of artifacts sharing a DESIGN KEY -- the config fields that say what the experiment *is*: the
circuit, the basis, the support, the read-out size, the task counts, the method list and the run length. Everything
else in the config is either a **manipulation** (a field that varies within the family: `input_overlap`, `lam`,
`noise`, `iters`, ...) or a **draw** (`readout_seed`, `support_seed`, `partition_seed`), and the two are separated by
the fields' own names rather than by a curated list. A reader who disagrees with the grouping can change `DRAW_FIELDS`
and rerun; the artifacts are the same.

A family is **single-draw** when it varies at least one manipulation field while using exactly **one** support draw
and **one** read-out draw. It is **replicated** when it varies a draw too. Families that vary no manipulation field at
all are **replicates** (the same configuration run again) and are reported separately, since their purpose is
different.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from experiments.e198_artifact_draw_census import _circuit_neurons

RUNS = Path("runs")

#: The keys that are the BASE and the COUNT of a draw set rather than draws themselves: `seed0` is 0 in every artifact
#: in the corpus, and `seeds` is how many task draws a linear run averages -- which `draw_keys` handles as its own
#: component.
SEED_LIKE_NOT_DRAWS = ("seed0", "seeds")


def draw_fields(configs) -> tuple:
    """The config fields that NAME a draw, derived from the corpus's own vocabulary rather than listed by hand.

    A hand-written list was wrong twice in one evening: it missed the linear line entirely (whose draws are
    `seed0`/`seeds`/`control_draws`, so 3- and 18-seed ladders looked "single-draw") and it missed `rewire_seed`, which
    the null-model families `e32`/`e33`/`e65` vary across 26 artifacts -- and because `draw_keys` builds its tuple from
    components it names, a field in the list but not the tuple still leaves one draw. So the rule is:

        a key whose name contains "seed" and whose values are ALL integers or None is a draw,

    with `seed0` and `seeds` excluded as the base and the count of a draw set. `matching_seeds` holds a path string and
    is therefore not a draw -- it is a design input, and a family varying it is a manipulation family. A future line
    naming its flag something else is still invisible, which is the honest limit of a rule over a vocabulary.
    """
    seen: dict[str, list] = {}
    for c in configs:
        for k, v in c.items():
            if "seed" in k.lower() and k not in SEED_LIKE_NOT_DRAWS:
                seen.setdefault(k, []).append(v)
    out = []
    for k in sorted(seen):
        if all(v is None or (isinstance(v, (int, float)) and not isinstance(v, bool)) for v in seen[k]):
            out.append(k)
    return tuple(out)


IGNORED = ("json_out", "seed0", "repeats")


def draw_keys(d: dict) -> tuple:
    """The (readout, support) draw keys this artifact used, each `None` when the draw is not live."""
    c = d.get("config") or {}
    n = _circuit_neurons(d)
    out = []
    size = c.get("readout_size")
    if size and n and 0 < size < n:
        seed = c.get("readout_seed")
        out.append(("readout", seed if seed is not None else c.get("seed0", 0), n, size))
    else:
        out.append(("readout", None))
    if c.get("input_overlap") is not None and n:
        seed = c.get("support_seed")
        out.append(("support", seed if seed is not None else c.get("seed0", 0), n, c.get("support")))
    else:
        out.append(("support", None))
    # **The linear line has none of the network line's draw flags and encodes its draws in `seed0`.** `e3` builds
    # its tasks with `build_tasks(..., seed=seed)` for `seed in range(seed0, seed0 + seeds)` -- verified by three
    # distinct `Sigma` matrices at seeds 0, 1 and 2 -- and draws its matched-random partitions from
    # `default_rng(seed0)` with `--control-draws` averaging. So a linear family's cells each AVERAGE `seeds` task
    # draws, and a census that looked only for `readout_seed`/`support_seed`/`partition_seed` called 3- and 18-seed
    # rung tables "single-draw".
    if c.get("seeds") is not None:
        out.append(("tasks", c.get("seed0", 0), c.get("seeds")))
    if c.get("control_draws") is not None:
        out.append(("control", c.get("seed0", 0), c.get("control_draws")))
    # And the NULL-MODEL draw: `rewire_seed` chooses the rewiring a topology control is built from, so a family that
    # varies it is varying a draw and not a manipulation -- `e32`/`e33`/`e65` vary it across 26 artifacts and were
    # being called "replicates", which hides the one family type that measures a draw.
    if c.get("rewire_seed") is not None:
        out.append(("rewire", c.get("seed0", 0), c.get("rewire_seed")))
    return tuple(out)


def averaging(d: dict) -> str:
    """How many draws each CELL of this artifact averages inside itself, from the fields that say so."""
    c = d.get("config") or {}
    bits = []
    # NOT `repeats`: the network line builds its suite ONCE per artifact and runs `--repeats` training replicas at
    # that one draw, so replicates are samples of the training noise and not of a draw. Counting them would make
    # every network family look like a draw average, which is the opposite of what today measured.
    for field in ("seeds", "control_draws", "draws"):
        v = c.get(field)
        if isinstance(v, int) and v > 1:
            bits.append(f"{field}={v}")
    return ", ".join(bits)


def family_of(path: Path) -> str:
    """The family is the project's own experiment id, parsed from the artifact's name.

    A first version tried to infer the family from a DESIGN KEY -- the config fields held constant -- and got the
    honest part of the problem wrong twice: `json_out` was counted as a manipulation (so a set of reruns under
    different filenames looked like a manipulation family), and `input_overlap` was *in* the key, which split each
    overlap family by the very field it manipulates so that no family appeared to vary anything. The experiment id is
    what the project itself groups by, and the varying fields are then reported per family rather than assumed.
    """
    m = re.match(r"(e\d+)", path.name)
    return m.group(1) if m else path.name


def census(runs_dir: Path = RUNS) -> dict:
    fams: dict[str, list] = {}
    for path in sorted(runs_dir.glob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict) or "config" not in d:
            continue
        fams.setdefault(family_of(path), []).append((path.name, d))
    # the draw fields are derived from THIS corpus's vocabulary, so the rule and the run agree
    fields = draw_fields([dict(m[1].get("config") or {}) for ms in fams.values() for m in ms])
    rows = []
    for key, members in fams.items():
        if len(members) < 2:
            continue
        cfg = [dict(m[1].get("config") or {}) for m in members]
        varying = sorted({k for k in set().union(*[set(c) for c in cfg]) if k not in IGNORED
                          and len({str(c.get(k)) for c in cfg}) > 1})
        draws = {draw_keys(m[1]) for m in members}
        manipulations = [k for k in varying if k not in fields]
        avg = sorted({averaging(m[1]) for m in members} - {""})
        rows.append({
            "averaging": avg,
            "family": key,
            "n_artifacts": len(members),
            "examples": [m[0] for m in members[:3]],
            "varies": varying,
            "manipulations": manipulations,
            "n_draws": len(draws),
            # Four verdicts, because "varies nothing" and "varies only the draw" are different purposes: the first
            # is a rerun, the second is a DRAW REPLICATION -- the design that measures a draw's own effect, which is
            # what today's replication was. Collapsing them called a draw replication a "replicate".
            "verdict": ("replicates" if not manipulations and len(draws) == 1
                        else "DRAW ONLY" if not manipulations
                        else "REPLICATED ACROSS DRAWS" if len(draws) > 1 else "SINGLE-DRAW"),
        })
    rows.sort(key=lambda r: (-r["n_artifacts"], r["family"]))
    return {"families": rows, "n_artifacts": sum(r["n_artifacts"] for r in rows),
            "draw_fields": list(fields)}


def report(res: dict) -> int:
    rows = res["families"]
    print(f"   == which families make manipulation claims at one draw: {len(rows)} families, "
          f"{res['n_artifacts']} artifacts ==")
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        arts = sum(r["n_artifacts"] for r in rows if r["verdict"] == k)
        print(f"   {k:22} {v:3} families, {arts:4} artifacts")
    print()
    avg_fams = [r for r in rows if r["averaging"]]
    n_arts = sum(r["n_artifacts"] for r in avg_fams)
    print(f"   {len(avg_fams)} of those families ({n_arts} artifacts) AVERAGE more than one DRAW inside each cell -- "
          f"the verdicts count only draws varied BETWEEN artifacts, and `--repeats` is NOT counted here because the "
          f"network line runs its replicas at ONE draw (a sample of the training noise, not of a draw):")
    for r in avg_fams[:6]:
        print(f"     {r['family']:8} n={r['n_artifacts']:3} averages {', '.join(r['averaging'])[:50]:50} {r['verdict']}")
    print()
    singles = [r for r in rows if r["verdict"] == "SINGLE-DRAW"]
    print(f"   the SINGLE-DRAW families that vary a manipulation ({len(singles)}), largest first:")
    for r in singles[:12]:
        print(f"     n={r['n_artifacts']:3}  varies {', '.join(r['manipulations'])[:60]:60}  e.g. {r['examples'][0]}")
    replicated = [r for r in rows if r["verdict"] == "REPLICATED ACROSS DRAWS"]
    print()
    print(f"   and the families that DO vary a draw while varying a manipulation ({len(replicated)}):")
    for r in replicated[:6]:
        print(f"     n={r['n_artifacts']:3}  varies {', '.join(r['varies'])[:70]:70}  e.g. {r['examples'][0]}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--json-out", type=Path, default=None)
    a = p.parse_args(argv)
    res = census(a.runs)
    if a.json_out:
        from clfly.bench.artifacts import write_json
        write_json(a.json_out, res)
        print(f"wrote {a.json_out}")
    return report(res)


if __name__ == "__main__":
    sys.exit(main())
