"""E205 -- the corpus records one quantity under two spellings, and the split is by instrument rather than chance.

Every artifact in this record that says how long it took says it in one of two ways: a top-level
``timing_s``, written by the trained runners, or ``timing = {"total_s": ...}``, written by the analytic
line (`e3_basis_selection` and the things built on it). Both are the same measurement -- ``time.time() - t0``
taken at the end of ``main`` -- and **nothing in the corpus was reading both**: `e169`'s scope gate read
``payload["timing_s"]``, `e190`'s cost line and `e38`'s cost table read ``d.get("timing_s")``, so an
analytic artifact's duration was invisible to every reader in the record that prices a run.

That is the defect class this project keeps finding one level below where it last looked: `e201`'s
draw-field list was hand-written and missed ``rewire_seed``; `e160`'s environment identity included the
machine's own speed; and here **two readers of one quantity do not know about each other**, with the
split falling exactly along the line boundary -- so a reader keying on either spelling is blind to a whole
line of the project, and the blind half is the *expensive* half.

Three questions, all answered from disk, none of them requiring a run:

  * **the census** -- how many artifacts carry a duration, under which spelling, and how much of the
    record's compute sits in each;
  * **the exposure** -- which readers read which spelling, whether the exclusion each makes coincides
    with a scope it would make anyway, and what it costs a reader to be wrong (rule 49's price: the
    analytic line's own costs are quoted in this project's plan by hand, and the two quotations of one
    command differ by 1.5x);
  * **the standing check** -- the spellings are a **declared vocabulary**, every artifact that looks like
    a run must have a readable duration, and no module may read a raw duration key instead of going
    through `duration_seconds`. The exit code is the count of violations, which is 0 as of this writing.

**What it cannot do**: it reads `runs/*.json` through `e103`'s loader, so a file with no ``config`` dict is
outside its view (and outside `e198`'s and `e201`'s too); its source check is text, so a module that
obtained a duration some third way would be invisible to it; and it cannot tell whether a duration that
*is* recorded is the duration of the thing the reader thinks it is -- it checks that the quantity is
readable, not that it means what a sentence about it says.

    python -m experiments.e205_duration_field_census
    python -m experiments.e205_duration_field_census --json-out runs/e205_duration_field_census.json

Reads artifacts and source text; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_field, duration_seconds, write_json
from experiments.e103_reproducibility_audit import load_artifacts

RUNS = Path("runs")
EXPERIMENTS = Path("experiments")

#: the spellings a duration is allowed to be recorded under. Anything else holding a number in a
#: ``tim*``/``dur*`` top-level key is a violation, which is what keeps a third spelling from appearing
#: silently -- the failure `e201`'s hand-written field list suffered.
SPELLINGS = ("timing_s", "timing.total_s")
#: a top-level numeric key that names a duration-shape but is not a run's duration
SHAPED_BUT_OTHER = ("summary.time_s",)

#: run-like artifacts that record no duration at all, declared with the runner that wrote each. These are
#: printed and NOT counted: those runs are over and their durations are unknowable, so the honest output is
#: the gap itself plus the fix for the next run (a ``timing_s`` write in `e122_path_geometry.py`,
#: `e124_barrier_distribution.py` and `e136_geometry_persistence.py`, none of which imports ``time``).
NO_DURATION = {
    "e122_path_geometry.json": "e122_path_geometry.py",
    "e124_barrier_12seeds.json": "e124_barrier_distribution.py",
    "e130_barrier_r32.json": "e136_geometry_persistence.py",
    "e131_barrier_r1307.json": "e136_geometry_persistence.py",
}

#: a run artifact's config is `vars(args)` from a runner; below this size it is hand-built
PARSER_SIZED = 25

KEY = re.compile(r'["\'](timing_s|timing\.total_s|timing)["\']')
#: setting the key rather than reading it: a dict literal or an item assignment. Both spellings are written
#: from `time.time()` at the end of main, so a write is the one place a spelling can appear for the first time.
WRITES = re.compile(r'["\']timing_s["\']\s*:|\[["\']timing_s["\']\]\s*='
                    r'|\[["\']timing["\']\]\[["\']total_s["\']\]\s*=|["\']timing["\']\s*:\s*\{')


def is_run_like(artifact: dict) -> bool:
    """Whether this artifact was produced by a runner: a per-arm result dict or a parser-sized config."""
    return (isinstance(artifact["payload"].get("methods"), dict)
            or len(artifact["config"]) >= PARSER_SIZED)


def strange_spellings(payload: dict) -> list[str]:
    """Top-level numeric keys that name a duration and are not in the declared vocabulary.

    The test is on the key's **name** -- a leading ``tim`` or ``dur`` -- and not on its meaning, which is the
    only thing a reader of an unknown artifact can do. Two consequences, both declared: a key like ``time_used``
    is flagged (correctly, since nothing else tells the reader what it is), and a duration recorded under a name
    that names no time at all (``total_seconds``) is missed, which is why the vocabulary is printed on every run.
    """
    out = []
    for key, value in payload.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        if re.match(r"^(tim|dur)", key) and key not in SPELLINGS:
            out.append(key)
    return out


def read_sites(root: Path = EXPERIMENTS) -> list[dict]:
    """Every source line that mentions a duration key, classified as a write or a read of one.

    The classification is by shape rather than by dataflow, and its false-positive class is declared: a
    module re-reading a duration from a dict it built itself is a READ here, and is excluded below because
    the module went through `duration_seconds`, not because the receiver was inspected.
    """
    sites = []
    for path in sorted(root.glob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        uses_helper = any("duration_seconds" in ln for ln in lines)
        for lineno, line in enumerate(lines, 1):
            if not KEY.search(line):
                continue
            kind = "write" if WRITES.search(line) else "read"
            sites.append({"module": path.name, "line": lineno, "kind": kind,
                          "uses_helper": uses_helper, "text": line.strip()[:96]})
    return sites


def census(runs: Path = RUNS) -> dict:
    """The two spellings' population, the compute each holds, and the artifacts that hold none."""
    arts = load_artifacts(runs)
    rows, unknown, run_like, no_duration = [], [], 0, []
    for a in arts:
        seconds = duration_seconds(a["payload"])
        run_like_here = is_run_like(a)
        rows.append({"name": a["name"], "field": duration_field(a["payload"]), "seconds": seconds,
                     "config_keys": len(a["config"]), "run_like": run_like_here,
                     "has_methods": isinstance(a["payload"].get("methods"), dict)})
        unknown += [{"artifact": a["name"], "key": k} for k in strange_spellings(a["payload"])]
        if run_like_here:
            run_like += 1
            if seconds is None:
                no_duration.append(a["name"])
    by_field: dict = {}
    for r in rows:
        if r["field"] is None:
            continue
        slot = by_field.setdefault(r["field"], {"artifacts": 0, "seconds": 0.0, "names": [], "seconds_of": {}})
        slot["artifacts"] += 1
        slot["seconds"] += r["seconds"]
        slot["names"].append(r["name"])
        slot["seconds_of"][r["name"]] = r["seconds"]
    sites = read_sites()
    reads = [s for s in sites if s["kind"] == "read"]
    return {
        "artifacts": len(rows), "run_like": run_like, "rows": rows,
        "by_field": by_field,
        "total_seconds": sum(s["seconds"] for s in by_field.values()),
        "no_duration": sorted(no_duration),
        "no_duration_declared": sorted(NO_DURATION),
        "unknown_spellings": unknown,
        "shaped_but_other": list(SHAPED_BUT_OTHER),
        "read_sites": reads,
        "outside_helper": [s for s in reads if not s["uses_helper"]],
        "write_sites": [s for s in sites if s["kind"] == "write"],
    }


def report(res: dict) -> int:
    by = res["by_field"]
    total = res["total_seconds"] or float("nan")
    print("== the census ==")
    print(f"   artifacts visible to `e103`'s loader (a `config` dict is the price of admission): {res['artifacts']}")
    print(f"   of them, run-like (a `methods` dict or a parser-sized config): {res['run_like']}")
    print(f"   carrying a duration: {sum(v['artifacts'] for v in by.values())}"
          f"; carrying none: {res['artifacts'] - sum(v['artifacts'] for v in by.values())}")
    print(f"   recorded compute: {total / 3600:.1f} h")
    print(f"\n   {'spelling':<17}{'artifacts':>10}{'hours':>9}{'share':>8}  who writes it")
    for field in SPELLINGS:
        slot = by.get(field)
        if slot is None:
            print(f"   {field:<17}{0:>10}")
            continue
        who = "the trained runners (all carry `methods`)" if field == "timing_s" else "the analytic line"
        print(f"   {field:<17}{slot['artifacts']:>10}{slot['seconds'] / 3600:>9.1f}"
              f"{slot['seconds'] / total:>8.1%}  {who}")

    nested_slot = by.get("timing.total_s", {"names": [], "seconds_of": {}})
    nested = nested_slot["names"]
    top_level = by.get("timing_s", {}).get("artifacts", 0)
    print("\n== the blindness, which is not symmetric ==")
    if nested:
        print(f"   a reader keying on `timing_s` cannot see {len(nested)} artifacts -- the analytic line, whose "
              f"{nested_slot['seconds'] / 3600:.1f} h is {nested_slot['seconds'] / total:.1%} of the record's "
              f"compute -- and one keying on `timing.total_s` cannot see {top_level}.")
    print("   the analytic artifacts, largest first (rule 49's price for the ladder line is read from here):")
    for name in sorted(nested, key=lambda n: -nested_slot["seconds_of"][n]):
        print(f"      {name:<48}{nested_slot['seconds_of'][name] / 3600:>8.2f} h")
    flat = sorted(((r["name"], r["seconds"]) for r in res["rows"] if r["seconds"] is not None),
                  key=lambda p: -p[1])
    if flat:
        med = sorted(s for _, s in flat)[len(flat) // 2]
        print(f"   their place among the record's longest runs: "
              f"{sum(1 for n, _ in flat[:10] if n in nested)} of the top 10 and "
              f"{sum(1 for n, _ in flat[:13] if n in nested)} of the top 13 are analytic artifacts, "
              f"against a median artifact of {med / 60:.1f} min")

    print("\n== the run-like artifacts that record NO duration ==")
    undeclared = [n for n in res["no_duration"] if n not in NO_DURATION]
    for name in res["no_duration"]:
        print(f"   {name:<40}{NO_DURATION.get(name, 'UNDECLARED')}")
    print(f"   {len(res['no_duration'])} of {res['run_like']} run-like artifacts, every one declared "
          f"({len(undeclared)} undeclared); the three runners that wrote them import no clock at all, which is "
          f"the fix recorded rather than applied.")

    print("\n== the standing check ==")
    print(f"   artifacts holding a duration-shaped numeric key outside {SPELLINGS}: "
          f"{len(res['unknown_spellings'])}")
    for row in res["unknown_spellings"][:5]:
        print(f"      {row['artifact']:<40}{row['key']}")
    print(f"   declared near-miss to inspect rather than to count: {', '.join(res['shaped_but_other']) or 'none'}"
          f" (a hand-built summary's own timing, not a run's)")
    print(f"\n   source lines that READ a duration key: {len(res['read_sites'])}, of which "
          f"{len(res['outside_helper'])} sit in a module that does not import `duration_seconds`")
    for s in res["outside_helper"]:
        print(f"      {s['module']}:{s['line']}  {s['text']}")
    print(f"   and the lines that WRITE one: {len(res['write_sites'])}, which is where a spelling is born")
    for s in res["write_sites"]:
        print(f"      {s['module']}:{s['line']}  {s['text']}")
    verdict = len(res["unknown_spellings"]) + len(undeclared) + len(res["outside_helper"])
    print(f"\n   VERDICT: {verdict} violation(s) -- an unknown spelling, an undeclared run-like artifact with no "
          f"readable duration, or a reader that bypasses the helper")
    return verdict


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    res = census(args.runs)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return report(res)


if __name__ == "__main__":
    sys.exit(main())
