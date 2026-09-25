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
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

from clfly.connectome.tasks import overlap_controlled_supports
from clfly.network import tasks as rate_tasks
from clfly.network.tasks import SUITE_SPECS

RUNS = Path("runs")

#: (label, the field, what makes it live, how it is identified)
DRAWS = (
    # The read-out subset is a draw only when it is a SUBSET: an artifact read out from every neuron has nothing to
    # identify, and counting those as unidentified is the false-alarm class `e126`'s preamble is about -- a checker
    # that reports everything gets ignored.
    ("readout", "the read-out subset",
     # `readout_size = 0` is the runner's "use the whole state" (`if args.readout_size and ...`), so it is NOT a
     # subset of size zero -- counting it as live is the false-positive class this census is written to avoid, and it
     # accounted for most of the residue before this test required the size to be TRUTHY as well as smaller than n.
     lambda d: bool((d.get("config") or {}).get("readout_size"))
     and _circuit_neurons(d) is not None
     and (d.get("config") or {}).get("readout_size") < _circuit_neurons(d),
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


def _circuit_neurons(d: dict) -> int | None:
    """The neuron count the draws were taken from: `config.circuit_size` is `max_neurons` and NOT the count.

    The runner draws from `circ.n_neurons`, which the artifact prints as "`N` neurons of `M`" and names in its
    `circuit` string (`mb+cx+al@n1307`). Using `circuit_size` here would be wrong by the difference between the two
    -- 800 against 1307 on this circuit -- and the read-out subset is drawn from `M`.
    """
    m = re.search(r"@n(\d+)", str(d.get("circuit") or ""))
    return int(m.group(1)) if m else None


def reconstruct_readout(d: dict) -> str | None:
    """The read-out subset's fingerprint, rebuilt from the artifact's own config.

    The expression is the runner's: ``sha1(" ".join(str(i) for i in sort(choice(n, size, replace=False))))`` with the
    draw seed `--readout-seed` or `--seed0`. **Validated against every artifact that records the field** -- 68 of 68
    reproduce -- which is what makes a reconstruction evidence rather than a guess.
    """
    c = d.get("config") or {}
    n = _circuit_neurons(d)
    size = (d.get("readout") or {}).get("size", c.get("readout_size"))
    if n is None or not size or size >= n:
        return None
    seed = c.get("readout_seed")
    seed = c.get("seed0", 0) if seed is None else seed
    rs = np.sort(np.random.default_rng(seed).choice(n, size=size, replace=False))
    return hashlib.sha1(" ".join(str(int(x)) for x in rs).encode()).hexdigest()[:12]


def reconstruct_supports(d: dict) -> str | None:
    """The overlap suite's support fingerprint, rebuilt from the artifact's own config. No connectome is needed:
    `overlap_controlled_supports` is a pure function of (n, T, size, overlap, seed). Validated against the 6 artifacts
    that record it, all of which reproduce."""
    c = d.get("config") or {}
    n = _circuit_neurons(d)
    if n is None or c.get("input_overlap") is None or not c.get("support"):
        return None
    seed = c.get("support_seed")
    seed = c.get("seed0", 0) if seed is None else seed
    try:
        sups = overlap_controlled_supports(n, len(SUITE_SPECS), c["support"], c["input_overlap"],
                                           np.random.default_rng(seed))
    except Exception:
        return None
    return hashlib.sha1(" ".join(",".join(str(int(x)) for x in np.sort(s)) for s in sups).encode()).hexdigest()[:12]


def census(runs_dir: Path = RUNS, reconstruct: bool = False) -> dict:
    rows, unreadable = [], []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            unreadable.append(path.name)
            continue
        if not isinstance(d, dict) or "config" not in d:
            continue
        row = {"artifact": path.name, "config": {}, "live": {}, "recorded": {}, "source": {}}
        for key, _label, live, recorded, _flag in DRAWS:
            is_live = bool(live(d))
            row["live"][key] = is_live
            val = recorded(d) if is_live else None
            row["source"][key] = "recorded" if val else None
            if is_live and not val and reconstruct:
                fn = {"readout": reconstruct_readout, "support_draw": reconstruct_supports}.get(key)
                if fn is not None:
                    val = fn(d)
                    row["source"][key] = "reconstructed" if val else None
            row["recorded"][key] = val
        rows.append(row)
    out = {"rows": rows, "unreadable": unreadable, "reconstructed": reconstruct}
    if reconstruct:
        # the reconstruction is only evidence if it reproduces the artifacts that DO record the field
        checks = {}
        for key, _label, live, recorded, _flag in DRAWS:
            fn = {"readout": reconstruct_readout, "support_draw": reconstruct_supports}.get(key)
            if fn is None:
                continue
            agree = disagree = 0
            for path in sorted(runs_dir.glob("*.json")):
                try:
                    d2 = json.loads(path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                rec = recorded(d2) if isinstance(d2, dict) else None
                if not rec:
                    continue
                got = fn(d2)
                if got == rec:
                    agree += 1
                else:
                    disagree += 1
            checks[key] = {"agree": agree, "disagree": disagree}
        out["checks"] = checks
    return out


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
    if res.get("reconstructed"):
        # The reconstruction is only evidence if it reproduces the artifacts that DO record the field: an
        # unvalidated rebuild would turn an unidentified draw into a mis-identified one, which is worse.
        print("   --reconstruct was given, so the draws that are pure functions of the config are rebuilt and "
              "VALIDATED against the artifacts that record them:")
        for key, c in (res.get("checks") or {}).items():
            print(f"     {key:16} reproduces {c['agree']} recorded fingerprints and disagrees with {c['disagree']}")
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
    p.add_argument("--reconstruct", action="store_true",
                   help="rebuild the read-out and support draws from each artifact's own config where the field is "
                        "absent, validating the reconstruction against the artifacts that record it")
    a = p.parse_args(argv)
    res = census(a.runs, reconstruct=a.reconstruct)
    if a.json_out:
        from clfly.bench.artifacts import write_json
        write_json(a.json_out, res)
        print(f"wrote {a.json_out}")
    return report(res)


if __name__ == "__main__":
    sys.exit(main())
