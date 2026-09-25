"""E205 -- the corpus records one quantity under THREE spellings, and every reader of it knew about one.

Every artifact in this record that says how long it took says it in one of three ways: a top-level
``timing_s``, written by the trained runners; ``timing = {"total_s": ...}``, written by the analytic line
(`e3_basis_selection` and the things built on it); or ``summary = {"time_s": ...}``, one level down,
written by the predictor analyses (`e6`, `e64`). All three are the same measurement -- ``time.time() - t0``
taken at the end of ``main`` -- and **nothing in the corpus was reading more than one**: `e169`'s scope gate
read ``payload["timing_s"]``, `e190`'s cost line and `e38`'s cost table read ``d.get("timing_s")``, so an
analytic artifact's duration was invisible to every reader in the record that prices a run.

That is the defect class this project keeps finding one level below where it last looked: `e201`'s
draw-field list was hand-written and missed ``rewire_seed``; `e160`'s environment identity included the
machine's own speed; and here **the readers of one quantity do not know about each other**, with the split
falling along the line boundary -- so a reader keying on one spelling is blind to whole instruments of the
project, and for two of the three the blind part is the *expensive* part.

**And this module committed the same defect it was written to catch, which is the sharpest thing in it.** Its
first version declared ``summary.time_s`` a *"near-miss to inspect rather than to count"* -- the phrase is
still visible in `e194`'s idiom, where it is right -- and scanned only the top level of each file, so the third
spelling was invisible to its own vocabulary check by construction. Three artifacts carrying **2.6 h** of
compute sat behind it, and they were found by taking the module's own declared near-miss seriously: a
near-miss declared by the check that exists to find unknown spellings is a spelling.

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

Reading the second question forced a third, about the four artifacts that record no duration at all: *who
wrote them?* `e172`'s parser registry answers it, and the answer is the finding's own second half -- a
``config`` is ``vars(args)``, so the writer is the parser that accounts for the most of the artifact's keys,
**and the four gaps have a unique best parser each** (`e122_path_geometry.py` at 28 of 29 keys, and
`e124_barrier_distribution.py` at 30 of 31, 32 of 33 and 32 of 33) **while `e172`'s own superset test finds
zero candidates for them**, because every one carries the same key its own parser does not define: ``save_theta``,
which BOTH runners assign into their own namespace at runtime (`args.save_theta = args.theta_dir`) to satisfy the
shared `run_method`. So a `config` is `vars(args)` **plus the runner's own plumbing**, and these four are the
record's most provenance-poor artifacts -- no duration, no
`environment`, no `code_revision`, and not attributable by the registry that exists to attribute -- and the
declaration below is **checked against the derived writer** rather than asserted.

**And a second correction, made by that check on its first run**: two of the four gaps were declared with
`e136_geometry_persistence.py` as the writer, which is the module that **reads** those grids and defines three
flags. The registry-derived writer disagrees and the disagreement is counted, so the artifact's reader is not
its writer -- the same shape as `e201`'s draw fields and `e172`'s epochs.

**What it cannot do**: it reads `runs/*.json` through `e103`'s loader, so a file with no ``config`` dict is
outside its view (and outside `e198`'s and `e201`'s too); its source check is text, so a module that obtained
a duration some third way would be invisible to it; it cannot tell whether a duration that *is* recorded is the
duration of the thing the reader thinks it is -- it checks that the quantity is readable, not that it means what
a sentence about it says; and a writer is a **best parser and not a proof**, so a runner that copied another's
flags would be attributed to whichever explains more keys, which is why the margin is printed.

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
from experiments.e172_parser_registry import registry as parser_registry

RUNS = Path("runs")
EXPERIMENTS = Path("experiments")

#: the spellings a duration is allowed to be recorded under. Anything else holding a number in a
#: ``tim*``/``dur*`` key is a violation, which is what keeps a further spelling from appearing silently -- the
#: failure `e201`'s hand-written field list suffered. A spelling is a **dotted path**, because the third one lives
#: one level down inside a block: the first version of this module scanned only the top level of the file, declared
#: `summary.time_s` a "near-miss to inspect" and printed it without counting it -- and it was a third spelling
#: holding an hour of compute, which is the same defect as the one this check exists to prevent.
SPELLINGS = ("timing_s", "timing.total_s", "summary.time_s")
#: the block keys whose contents are scanned for a duration-shaped numeric key, at one level down
BLOCKS = ("timing", "summary", "environment")

#: run-like artifacts that record no duration at all, declared with the runner that wrote each. The declared
#: runner is **checked against the registry-derived one** (see `derive_writer`), because the first version of
#: this table named `e136_geometry_persistence.py` for the two `barrier_r*` grids -- the module that READS them.
#: These four are printed and NOT counted: their runs are over and their durations are unknowable, so the honest
#: output is the gap itself plus the fix applied here (the ``timing_s`` write now in `e122_path_geometry.py` and
#: `e124_barrier_distribution.py`, the two runners that had no clock at all).
NO_DURATION = {
    "e122_path_geometry.json": "e122_path_geometry.py",
    "e124_barrier_12seeds.json": "e124_barrier_distribution.py",
    "e130_barrier_r32.json": "e124_barrier_distribution.py",
    "e131_barrier_r1307.json": "e124_barrier_distribution.py",
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
    """Numeric keys that name a duration and are not in the declared vocabulary, as dotted paths.

    The test is on the key's **name** -- a leading ``tim`` or ``dur`` -- and not on its meaning, which is the
    only thing a reader of an unknown artifact can do. Three consequences, all declared: a key like ``time_used``
    is flagged (correctly, since nothing else tells the reader what it is); a duration recorded under a name that
    names no time at all (``total_seconds``) is missed, which is why the vocabulary is printed on every run; and
    the scan descends into the blocks named in ``BLOCKS`` and no further, because that is where the third spelling
    was hiding and a nested scan is what a top-level scan cannot do.
    """
    out = []

    def visit(prefix: str, obj: dict) -> None:
        for key, value in obj.items():
            path = f"{prefix}{key}"
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if re.match(r"^(tim|dur)", key) and path not in SPELLINGS:
                    out.append(path)
            elif prefix == "" and key in BLOCKS and isinstance(value, dict):
                visit(f"{key}.", value)

    visit("", payload)
    return out


def derive_writer(config: dict, parsers: dict) -> dict:
    """Which module's parser accounts for the most of this artifact's config keys, with its margin.

    A ``config`` is ``vars(args)``, so a runner's parser defines every key the artifact carries -- except when a
    flag has since been **removed**, which is why `e172`'s superset test (`candidates`) returns nobody for the
    four artifacts this is used on. Ranking by overlap instead of requiring containment names one writer per gap
    with a margin of two to six keys over the runner-up, and the margin is the honesty of the answer: a copied
    flag set would be attributed to whichever explains more keys, and nothing here could tell.
    """
    ranked = sorted(((len(set(config) & flags), module) for module, flags in parsers.items()),
                    key=lambda pair: (-pair[0], pair[1]))
    best_keys, best = ranked[0]
    runner_up = ranked[1][0] if len(ranked) > 1 else 0
    return {"module": best, "overlap": best_keys, "keys": len(config), "runner_up": runner_up,
            "runner_up_module": ranked[1][1] if len(ranked) > 1 else None,
            "missing_from_best": sorted(set(config) - parsers[best])}


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
    parsers = parser_registry()
    rows, unknown, run_like, no_duration, plumbing = [], [], 0, [], []
    for a in arts:
        seconds = duration_seconds(a["payload"])
        run_like_here = is_run_like(a)
        rows.append({"name": a["name"], "field": duration_field(a["payload"]), "seconds": seconds,
                     "config_keys": len(a["config"]), "run_like": run_like_here,
                     "has_methods": isinstance(a["payload"].get("methods"), dict)})
        unknown += [{"artifact": a["name"], "key": k} for k in strange_spellings(a["payload"])]
        writer = derive_writer(a["config"], parsers)
        if writer["missing_from_best"]:
            plumbing.append({"artifact": a["name"], "module": writer["module"],
                             "missing": writer["missing_from_best"]})
        if run_like_here:
            run_like += 1
            if seconds is None:
                writer = derive_writer(a["config"], parsers)
                writer["artifact"] = a["name"]
                writer["declared"] = NO_DURATION.get(a["name"])
                writer["declared_agrees"] = writer["declared"] == writer["module"]
                no_duration.append(writer)
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
        "no_duration": sorted(no_duration, key=lambda w: w["artifact"]),
        "unknown_spellings": unknown,
        "plumbing": sorted(plumbing, key=lambda w: w["artifact"]),
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
        who = {"timing_s": "the trained runners (all carry `methods`)",
               "timing.total_s": "the analytic line (none carries `methods`)",
               "summary.time_s": "the predictor analyses (`e6`, `e64`), one level down"}[field]
        if slot is None:
            print(f"   {field:<17}{0:>10}{'-':>9}{'-':>8}  {who}")
            continue
        print(f"   {field:<17}{slot['artifacts']:>10}{slot['seconds'] / 3600:>9.1f}"
              f"{slot['seconds'] / total:>8.1%}  {who}")

    nested_slot = by.get("timing.total_s", {"names": [], "seconds_of": {}})
    nested = nested_slot["names"]
    summary_slot = by.get("summary.time_s", {"names": [], "seconds_of": {}, "seconds": 0.0})
    top_level = by.get("timing_s", {}).get("artifacts", 0)
    print("\n== the blindness, which is not symmetric: a reader keying on one spelling ==")
    for field in SPELLINGS:
        blind = sum(s["artifacts"] for f, s in by.items() if f != field)
        hidden_h = sum(s["seconds"] for f, s in by.items() if f != field)
        print(f"   {field:<17} cannot see {blind:>3} artifacts, {hidden_h / 3600:>5.1f} h = "
              f"{hidden_h / total:>5.1%} of the record's compute")
    print("   the analytic artifacts, largest first (rule 49's price for the ladder line is read from here):")
    for name in sorted(nested, key=lambda n: -nested_slot["seconds_of"][n]):
        print(f"      {name:<48}{nested_slot['seconds_of'][name] / 3600:>8.2f} h")
    if summary_slot["names"]:
        print("   and the three under `summary.time_s`, which no reader could see until this run:")
        for name in sorted(summary_slot["names"], key=lambda n: -summary_slot["seconds_of"][n]):
            print(f"      {name:<48}{summary_slot['seconds_of'][name] / 3600:>8.2f} h")
    flat = sorted(((r["name"], r["seconds"]) for r in res["rows"] if r["seconds"] is not None),
                  key=lambda p: -p[1])
    if flat:
        med = sorted(s for _, s in flat)[len(flat) // 2]
        print(f"   their place among the record's longest runs: "
              f"{sum(1 for n, _ in flat[:10] if n in nested)} of the top 10 and "
              f"{sum(1 for n, _ in flat[:13] if n in nested)} of the top 13 are analytic artifacts, "
              f"against a median artifact of {med / 60:.1f} min")

    print("\n== the run-like artifacts that record NO duration, and who wrote each ==")
    undeclared = [w for w in res["no_duration"] if w["declared"] is None]
    for w in res["no_duration"]:
        print(f"   {w['artifact']:<40}{w['module']:<36}{w['overlap']:>3} of {w['keys']} keys"
              f"   (runner-up {w['runner_up_module']} {w['runner_up']})")
        if not w["declared_agrees"]:
            print(f"      DECLARED {w['declared']}, DERIVED {w['module']} -- the declaration is wrong")
        if w["missing_from_best"]:
            print(f"      keys the best parser does not define: {', '.join(w['missing_from_best'])}"
                  f" (which is why `e172`'s superset test names nobody -- that key is the runner's own plumbing,")
            print("      assigned into its own namespace at runtime rather than declared as a flag)")
    print("   every one of them is unclaimed by `e172`'s containment test for that same reason, so a `config` is")
    print("   `vars(args)` PLUS what the runner adds to it -- which is also the direction `e169`'s key-clock reads")
    print(f"   {len(res['no_duration'])} of {res['run_like']} run-like artifacts, every one declared "
          f"({len(undeclared)} undeclared, "
          f"{sum(1 for w in res['no_duration'] if not w['declared_agrees'])} declared wrongly); the two runners "
          f"behind them now write `timing_s`, so the next run of either records its own cost.")

    print("\n== a config is `vars(args)` plus the runner's own plumbing ==")
    keys = sorted({k for w in res["plumbing"] for k in w["missing"]})
    mods = sorted({w["module"] for w in res["plumbing"]})
    print(f"   artifacts carrying a key their own best parser does not define: "
          f"{len(res['plumbing'])} of {res['artifacts']}, over {len(keys)} key(s) {keys}")
    print(f"   the runners that inject one: {mods} -- which is why `e172`'s containment test names nobody")
    for w in res["plumbing"][:6]:
        print(f"      {w['artifact']:<40}{w['module']:<34}{w['missing']}")

    print("\n== the standing check ==")
    print(f"   artifacts holding a duration-shaped numeric key outside the vocabulary {SPELLINGS}: "
          f"{len(res['unknown_spellings'])}")
    for row in res["unknown_spellings"][:5]:
        print(f"      {row['artifact']:<40}{row['key']}")
    print(f"\n   source lines that READ a duration key: {len(res['read_sites'])}, of which "
          f"{len(res['outside_helper'])} sit in a module that does not import `duration_seconds`")
    for s in res["outside_helper"]:
        print(f"      {s['module']}:{s['line']}  {s['text']}")
    print(f"   and the lines that WRITE one: {len(res['write_sites'])}, which is where a spelling is born")
    for s in res["write_sites"]:
        print(f"      {s['module']}:{s['line']}  {s['text']}")
    verdict = (len(res["unknown_spellings"]) + len(undeclared)
               + sum(1 for w in res["no_duration"] if not w["declared_agrees"])
               + len(res["outside_helper"]))
    print(f"\n   VERDICT: {verdict} violation(s) -- an unknown spelling, an undeclared run-like artifact with no "
          f"readable duration, a gap declared to the wrong writer, or a reader that bypasses the helper")
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
