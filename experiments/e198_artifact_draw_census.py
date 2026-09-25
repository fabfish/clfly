"""E198 -- which RNG DRAWS does each artifact record, and which of its claims depend on the ones it does not?

`e168` asked this question of the matched-random partition draw alone and found that **31 of 38 artifacts which ran
a `*-rand` arm could not say which partition they drew**
(`docs/findings/2026-09-24-the-random-control-is-a-sample-and-31-of-38-artifacts-do-not-say-which.md`). Two more
draws exist and neither had a census:

| draw | field | records | added |
|---|---|---|---|
| the read-out subset | `readout.subset_sha1` | which 32 of 1307 neurons are read out | mid-project |
| the matched-random partition | `partition_draw.fingerprint_sha1` | which size-matched random partition the control used | `e168` |
| **the overlap SUPPORTS** | `support_draw.fingerprint_sha1` | which neurons each task drives | **today** |

**And today measured what the last of those is worth**: on the overlap suite, two support draws differ by 3.3–6.6σ on
the learning quantities *on identical configurations and identical seeds*, and six of the axis's claims failed to
replicate across them. So a census is not bookkeeping -- an artifact that does not record its draw is an artifact
whose overlap-sensitive claims cannot be attributed to the manipulation rather than to the draw.

    python -m experiments.e198_artifact_draw_census                 # every artifact under runs/
    python -m experiments.e198_artifact_draw_census --json-out runs/e198_artifact_draw_census.json

**Analysis only**: it reads the artifacts' own metadata and never a measurement. An artifact "needs" a draw when its
configuration makes that draw live -- `readout_size` below the circuit's neuron count, an `ewc-block-rand` arm, or an
`--input-overlap` suite -- and a draw is "recorded" when the artifact carries the field with a non-null fingerprint.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNS = Path("runs")

#: (label, the field, what makes it live, how it is identified)
DRAWS = (
    # The read-out subset is a draw only when it is a SUBSET: an artifact read out from every neuron has nothing to
    # identify, and counting those as unidentified is the false-alarm class `e126`'s preamble is about -- a checker
    # that reports everything gets ignored.
    ("readout", "the read-out subset",
     lambda d: (d.get("config") or {}).get("readout_size") is not None
     and (d.get("config") or {}).get("circuit_size") is not None
     and (d.get("config") or {}).get("readout_size") < (d.get("config") or {}).get("circuit_size"),
     lambda d: ((d.get("readout") or {}).get("subset_sha1")),
     "`--readout-seed`"),
    ("partition_draw", "the matched-random partition",
     lambda d: "ewc-block-rand" in ((d.get("config") or {}).get("methods") or ""),
     lambda d: ((d.get("partition_draw") or {}).get("fingerprint_sha1")),
     "`--partition-seed`"),
    ("support_draw", "the overlap suite's SUPPORTS",
     lambda d: (d.get("config") or {}).get("input_overlap") is not None,
     lambda d: ((d.get("support_draw") or {}).get("fingerprint_sha1")),
     "`--support-seed`"),
)


def census(runs_dir: Path = RUNS) -> dict:
    rows, unreadable = [], []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            unreadable.append(path.name)
            continue
        if not isinstance(d, dict) or "config" not in d:
            continue
        row = {"artifact": path.name, "config": {}, "live": {}, "recorded": {}}
        for key, _label, live, recorded, _flag in DRAWS:
            is_live = bool(live(d))
            row["live"][key] = is_live
            row["recorded"][key] = recorded(d) if is_live else None
        rows.append(row)
    return {"rows": rows, "unreadable": unreadable}


def report(res: dict) -> int:
    rows = res["rows"]
    print(f"   == which draw does each artifact record, and which draws does it need: {len(rows)} artifacts ==")
    print(f"   {'draw':16} {'live in':>8} {'recorded':>9} {'UNIDENTIFIED':>13}   how it is named")
    unidentified_total = 0
    worst = None
    for key, label, _live, _rec, flag in DRAWS:
        live = [r for r in rows if r["live"][key]]
        rec = [r for r in live if r["recorded"][key]]
        un = [r for r in live if not r["recorded"][key]]
        unidentified_total += len(un)
        print(f"   {key:16} {len(live):8} {len(rec):9} {len(un):13}   {flag}")
        if worst is None or len(un) > len(worst[1]):
            worst = (label, un, key)
    print()
    print(f"   {unidentified_total} (artifact, live draw) pairs cannot say which draw they used")
    if worst:
        label, un, key = worst
        print(f"   the largest class is {label} (`{key}`): {len(un)} artifacts, e.g. "
              f"{', '.join(r['artifact'] for r in un[:4])}{' ...' if len(un) > 4 else ''}")
    # the artifacts that need the draw today measured to matter, and cannot identify it
    overlap = [r for r in rows if r["live"]["support_draw"]]
    if overlap:
        identified = [r for r in overlap if r["recorded"]["support_draw"]]
        print(f"   of {len(overlap)} artifacts whose supports are a live draw, {len(identified)} identify it "
              f"({100 * len(identified) / len(overlap):.1f}%) -- and today measured that two support draws differ by "
              f"3.3-6.6 sigma on the learning quantities")
    if res["unreadable"]:
        print(f"   ({len(res['unreadable'])} artifacts could not be parsed and are excluded: "
              f"{', '.join(res['unreadable'][:3])})")
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
