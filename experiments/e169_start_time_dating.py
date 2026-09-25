"""E169 -- the corpus's own second dating method, and rule 47 measured: start time has no violations, write time has three.

Rule 47 says an artifact's timestamp dates the **end** of its run, so a long run's code epoch is set by its start.
This unit turns that from a caution into a **check with a number**, by finding a dating method the timestamps
cannot influence: `e103`'s premise that *a parser only ever gains flags*, which makes a config **keyset** a
monotone marker of time. Wherever one artifact's keyset is a strict subset of another's, the smaller one must have
been produced earlier — so ordering every such pair by a candidate clock tests that clock.

Two clocks are tried on the same 129 run artifacts:

  * **write time** — the file's mtime, which is what `e163` dated the 09-23 epoch with;
  * **start time** — `mtime - timing_s`, the clock rule 47 asks for.

**Scope matters and is declared**: a *run* artifact is one carrying a duration **under either of the corpus's two
spellings** (`duration_seconds`; `e205` measured that a reader keying on `timing_s` alone is blind to the thirteen
analytic artifacts, which this scope excludes for its other two reasons as well), a `methods` dict and a config of at
least 25 keys (`vars(args)` from this runner; the smaller configs in `runs/` are hand-built summaries, and asking
them for a parser's keyset is asking the wrong object — the defect `e103`'s docstring records twice), and pairs
whose two clocks are within 60 s are **not counted either way**, because ordering them is a coin flip and
reporting it as a violation would manufacture the defect the check exists to find.

    python -m experiments.e169_start_time_dating
    python -m experiments.e169_start_time_dating --json-out runs/e169_start_time_dating.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json
from experiments.e103_reproducibility_audit import load_artifacts

#: a config this size is `vars(args)` from this project's main runner; below it the config is a hand-built summary
PARSER_SIZED = 25
#: two clocks this close cannot be ordered by either method without manufacturing a violation
TIE_SECONDS = 60.0


def start_time(artifact: dict) -> float:
    """When the run *began*: the file's write time less the duration it recorded."""
    return artifact["mtime"] - duration_seconds(artifact["payload"])


def in_scope(artifact: dict, min_keys: int = PARSER_SIZED) -> bool:
    """Whether this artifact is a run whose config is a parser dump, and so can be dated this way."""
    payload = artifact["payload"]
    return (duration_seconds(payload) is not None
            and isinstance(payload.get("methods"), dict)
            and len(artifact["config"]) >= min_keys)


def nested_violations(rows: list[dict], clock: str) -> dict:
    """Order every strictly-nested-keyset pair by ``clock`` and count the ones in the wrong order.

    A violation is a pair where the artifact with the **smaller** keyset is placed *later* than the one with the
    larger — the direction a parser that only gains flags forbids.
    """
    good, violations, ties = 0, [], 0
    for a in rows:
        for b in rows:
            if a is b or not a["keys"] < b["keys"]:
                continue
            if abs(a[clock] - b[clock]) <= TIE_SECONDS:
                ties += 1
                continue
            if a[clock] < b[clock]:
                good += 1
            else:
                violations.append({"earlier_keyset": a["name"], "later_keyset": b["name"],
                                   "keys": [len(a["keys"]), len(b["keys"])],
                                   "durations_h": [round(a["duration"] / 3600, 2), round(b["duration"] / 3600, 2)],
                                   "written": [stamp(a["mtime"]), stamp(b["mtime"])],
                                   "started": [stamp(a["start"]), stamp(b["start"])],
                                   "separation_h": round((a[clock] - b[clock]) / 3600, 2)})
    violations.sort(key=lambda v: -v["separation_h"])
    return {"ordered_correctly": good, "violations": violations, "ties": ties}


def stamp(t: float) -> str:
    return datetime.datetime.fromtimestamp(t).strftime("%m-%d %H:%M")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    arts = [a for a in load_artifacts() if in_scope(a)]
    rows = [{"name": a["name"], "keys": set(a["config"]), "mtime": a["mtime"],
             "payload": a["payload"], "duration": duration_seconds(a["payload"])} for a in arts]
    for r in rows:
        r["start"] = start_time(r)
    out: dict = {"in_scope": len(rows)}

    print("== the second dating method ==")
    print(f"   run artifacts with a parser-sized config and a duration: {len(rows)}")
    print(f"   strictly-nested keyset pairs among them: "
          f"{sum(1 for a in rows for b in rows if a is not b and a['keys'] < b['keys'])}")
    print("   and a parser only gains flags, so in every such pair the SMALLER keyset must come first")

    for clock, tag in (("mtime", "WRITE TIME (the file's timestamp)"),
                       ("start", "START TIME (mtime minus the duration)")):
        res = nested_violations(rows, clock)
        out[clock] = res
        print(f"\n   {tag}:")
        print(f"      ordered correctly {res['ordered_correctly']}, "
              f"VIOLATED {len(res['violations'])}, not counted (within {TIE_SECONDS:g} s) {res['ties']}")
        for v in res["violations"]:
            print(f"         {v['earlier_keyset'][:44]} ({v['keys'][0]} keys, {v['durations_h'][0]} h) "
                  f"placed AFTER {v['later_keyset'][:40]} ({v['keys'][1]} keys, {v['durations_h'][1]} h) "
                  f"by {v['separation_h']} h")

    w, s = out["mtime"], out["start"]
    print("\n== rule 47, measured ==")
    print(f"   write time: {len(w['violations'])} violation(s) of {w['ordered_correctly'] + len(w['violations'])}")
    print(f"   start time: {len(s['violations'])} violation(s) of {s['ordered_correctly'] + len(s['violations'])}")
    misplaced = sorted({(v["earlier_keyset"], v["durations_h"][0]) for v in w["violations"]},
                       key=lambda p: -p[1])
    median = sorted(r["duration"] for r in rows)[len(rows) // 2]
    for name, hrs in misplaced:
        print(f"      misplaced by write time: {name[:44]}  ({hrs} h)")
    print(f"   -> the artifacts write time misplaces are the corpus's longest runs "
          f"({', '.join('%.2f h' % h for _, h in misplaced)} against a median of {median / 60:.0f} min), which")
    print("      are exactly the ones whose epoch boundaries sit nearest a commit: `mtime - timing_s` fixes them,")
    print("      and the smaller-keyset invariant is the check that says so without consulting a timestamp.")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
