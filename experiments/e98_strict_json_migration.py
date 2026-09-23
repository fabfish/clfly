"""E98 -- normalise every artifact that a strict JSON parser rejects, and count the writers that can still
produce one.

`clfly/bench/artifacts.write_json` exists so that `runs/*.json` is spec-conformant: Python's `json` writes
`NaN` and `Infinity` by default, `JSON.parse` / `serde_json` / `encoding/json` / `pandas.read_json` all reject
them, and the rate-network line contains them legitimately as a *"not yet trained"* marker that belongs in the
file as `null`.

The paper's §9 says **"seven rate-network artifacts"** were written in the non-conformant form and that
**"every writer now goes through write_json"**, and this module's own docstring repeats the seven. A scan of
`runs/` finds **thirteen** files a strict parser refuses, of which **eight** are rate-network, and it finds
that **32 of 42 modules write with `json.dump` directly** — so neither sentence is true of the corpus or of
the code as it stands. This script fixes the artifacts and counts the writers, so both claims can be restated
from a measurement instead of from memory.

    python -m experiments.e98_strict_json_migration            # report only
    python -m experiments.e98_strict_json_migration --write    # normalise in place
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from clfly.bench.artifacts import nonfinite_to_null, write_json

RUNS = Path("runs")
#: a bare NaN / Infinity token, i.e. one not inside a string
BARE_NONFINITE = re.compile(r'(?<![\w"])(NaN|Infinity|-Infinity)(?![\w"])')


def strict_parse(text: str):
    """Parse with a strict parser, so a non-conformant file raises rather than passing silently."""
    return json.loads(text, parse_constant=lambda tok: (_ for _ in ()).throw(ValueError(tok)))


def scan():
    offenders = []
    for p in sorted(RUNS.glob("*.json")):
        text = p.read_text(encoding="utf-8", errors="replace")
        hits = BARE_NONFINITE.findall(text)
        if not hits:
            continue
        try:
            strict_parse(text)
            continue                      # a valid file that merely spells the token in a string
        except ValueError as exc:
            offenders.append((p, len(hits), str(exc)))
    return offenders


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="normalise the offending artifacts in place")
    ap.add_argument("--json-out", default="runs/e98_strict_json_migration.json")
    args = ap.parse_args()

    all_artifacts = sorted(RUNS.glob("*.json"))
    offenders = scan()
    print("=" * 108)
    print("1. WHICH ARTIFACTS A STRICT JSON PARSER REFUSES")
    print("=" * 108)
    print(f"   artifacts in runs/                     : {len(all_artifacts)}")
    print(f"   refused by a strict parser             : {len(offenders)}"
          f"   ({100 * len(offenders) / max(len(all_artifacts), 1):.1f}%)")
    print(f"   {'artifact':<52}{'tokens':>8}  first token")
    for p, n, tok in offenders:
        print(f"   {p.name:<52}{n:>8}  {tok}")

    print()
    print("=" * 108)
    print("2. WHICH WRITERS COULD PRODUCE ANOTHER ONE")
    print("=" * 108)
    modules = sorted(list(Path("experiments").glob("*.py")) + list(Path("clfly").glob("*/*.py")))
    via, direct = [], []
    for m in modules:
        text = m.read_text(encoding="utf-8", errors="replace")
        if "json.dump(" in text:
            direct.append(m.name)
        elif "write_json" in text:
            via.append(m.name)
    print(f"   modules that write artifacts with `json.dump` DIRECTLY : {len(direct)}")
    print(f"   modules that use `write_json`                          : {len(via)}")
    print(f"   so \"every writer now goes through write_json\" is true of {len(via)} of "
          f"{len(via) + len(direct)}")
    print(f"\n   the direct writers: {', '.join(direct)}")

    if args.write and offenders:
        print()
        print("=" * 108)
        print("3. NORMALISING IN PLACE, AND CHECKING THAT NO VALUE MOVED")
        print("=" * 108)

        def norm(o):
            """Every non-finite value mapped to None, on both sides of the comparison, so the check asks
            whether the *numbers* moved rather than whether the spelling of 'not a number' did."""
            if isinstance(o, dict):
                return {k: norm(v) for k, v in o.items()}
            if isinstance(o, list):
                return [norm(v) for v in o]
            if isinstance(o, float):
                return None if not math.isfinite(o) else o
            return o

        identical = []
        for p, _, _ in offenders:
            before = json.loads(p.read_text(encoding="utf-8"))      # lenient read of the old text
            write_json(p, before)                                    # NaN -> null, strict output
            after = json.loads(p.read_text(encoding="utf-8"))
            same = norm(before) == norm(after)
            identical.append(same)
            print(f"   {p.name:<52} values identical after NaN -> null: {same}")
        print(f"\n   normalised {len(identical)}; every value identical: {all(identical)}")

    if args.write:
        remaining = scan()
        print(f"\n   artifacts a strict parser still refuses, after normalising: {len(remaining)}")
        offenders = remaining

    write_json(args.json_out, dict(n_artifacts=len(all_artifacts),
                                   n_refused_now=len(offenders),
                                   refused=[p.name for p, _, _ in offenders],
                                   writers_direct=direct, writers_via_write_json=via,
                                   wrote=bool(args.write)))
    print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
