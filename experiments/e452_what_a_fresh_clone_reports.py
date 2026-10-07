"""E452 -- what a fresh clone reports: the census thread (b) has been listed for and never measured.

`tools/gates.sh` is the corpus's own gate -- the test suite and then one entry per module that carries a registered
claim -- and every entry that reads `runs/` reports **REFUSED** there when the artifact it wants is absent, because
`runs/` is gitignored. That convention is the reason a clone is *usable* rather than wrong, and it has been asserted in
prose by every plan row that closed with a refusal path and never measured. The open thread it belongs to is whether
`runs/` should ship, and the question has been listed on every fire without a single number beside it.

**This unit measures it.** No training and no probe: it parses `tools/gates.sh`'s own entry list, resolves each entry to
the module it invokes, reads that module's source for whether it names a path under `runs/` and whether it carries a
refusal, and censuses `runs/` itself -- its bytes, its files and its largest. Five claims, registered before this unit's
pass over the gate and the corpus.

- **CY1 -- and the ledger is carried.** Every `run` entry in `tools/gates.sh` parses, every Python entry names a module
  that exists on disk, and the pytest entry is reported as its own kind. **Falsifier**: any entry unparsed, any module
  absent, or a gate file that is not there.
- **CY2 -- and the gate is artifact-dependent.** At least **half** of the Python entries invoke a module whose source
  names a path under `runs/`. **Falsifier**: under **a quarter**; **null**: between.
- **CY3 -- and the dependence is not uniform.** At least **10** entries invoke a module that does not name `runs/`.
  **Falsifier**: fewer than **3**; **null**: between.
- **CY4 -- and the refusal convention covers most of the dependent entries.** At least **four fifths** of those modules
  carry a refusal path. **Falsifier**: under **three fifths**; **null**: between. *`REFUSED` in the source is what this
  reads, so it measures the convention's reach and not whether each refusal is right.*
- **CY5 -- and the corpus does not fit a repository.** `runs/` is over **100 MB** and over **1000** files.
  **Falsifier**: under **20 MB**; **null**: between. *This is the unit's decision number: `e463`'s kind of question has
  been asked without it.*

**What it can do beyond that.** It turns the open thread into three numbers and one defect. If the dependent share is
large and `runs/` is a gigabyte, then *ship `runs/`* is not a choice a repository can take and the thread's real
subject is what a clone should do instead; and the modules that name `runs/` **without** a refusal would, on an empty
corpus, report counts of nothing rather than declining -- which is the one failure mode a clone must not have, and this
unit names it.

**What it cannot do.** *A static reading*: whether a module names `runs/` is read from its source and not from running
it, so a module that builds its artifact path from a constant the source does not spell would be misclassified, and a
module whose refusal is spelled otherwise than `REFUSED` counts as having none. *And no clone is simulated*: the gate is
not re-run with `runs/` hidden, the entry list is read as it stands, and the counts are of entries rather than of the
work behind them. *And the corpus grows*: the entries, the files and the bytes are all counts that move with it, so
every bar here is a bound and the shares are the statements.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

GATES = Path("tools/gates.sh")
RUNS = Path("runs")
MODULE = re.compile(r"-m\s+(experiments\.[A-Za-z0-9_]+)")
RUN_LINE = re.compile(r"^run\s+(\S+)\s+(.*)$")
ARTIFACT = "runs/"
REFUSAL = "REFUSED"
TOTAL_BAR = 100 * 1024 * 1024
TOTAL_FLOOR = 20 * 1024 * 1024
FILE_BAR = 1000
CLAIM_SHARE = 0.5
CLAIM_FLOOR = 0.25
SOURCE_ONLY_BAR = 10
SOURCE_ONLY_FLOOR = 3
REFUSAL_SHARE = 0.8
REFUSAL_FLOOR = 0.6
BIG = 5 * 1024 * 1024
CLAIMS = (
    ("CY1", "and the ledger is carried",
     "Every run entry in tools/gates.sh parses, every Python entry names a module that exists on disk, and the pytest "
     "entry is reported as its own kind",
     "falsifier: any entry unparsed, any module absent, or a gate file that is not there"),
    ("CY2", f"and the gate is artifact-dependent, at least {CLAIM_SHARE:.0%} of the Python entries",
     "At least half of the Python entries invoke a module whose source names a path under runs/",
     f"falsifier: under {CLAIM_FLOOR:.0%}; null: between"),
    ("CY3", f"and the dependence is not uniform, at least {SOURCE_ONLY_BAR} entries",
     "At least 10 entries invoke a module that does not name runs/",
     f"falsifier: fewer than {SOURCE_ONLY_FLOOR}; null: between"),
    ("CY4", f"and the refusal convention covers most of them, at least {REFUSAL_SHARE:.0%}",
     "At least four fifths of the artifact-dependent modules carry a refusal path",
     f"falsifier: under {REFUSAL_FLOOR:.0%}; null: between"),
    ("CY5", f"and the corpus does not fit a repository, over {TOTAL_BAR // (1024 * 1024)} MB and {FILE_BAR} files",
     f"runs/ is over 100 MB and over 1000 files",
     f"falsifier: under {TOTAL_FLOOR // (1024 * 1024)} MB; null: between"),
)


def load(path) -> str | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def entries(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        m = RUN_LINE.match(line.strip())
        if not m:
            continue
        name, rest = m.group(1), m.group(2)
        found = MODULE.search(rest)
        out.append({"name": name, "command": rest,
                    "kind": "pytest" if name == "pytest" else ("python" if found else "other"),
                    "module": found.group(1) if found else None,
                    "path": (found.group(1).replace(".", "/") + ".py") if found else None})
    return out


def census() -> dict:
    if not RUNS.is_dir():
        return {"files": 0, "bytes": 0, "largest": None, "largest_bytes": 0, "over_big": 0}
    files = bytes_ = over = 0
    largest, largest_bytes = None, 0
    for p in RUNS.rglob("*"):
        if not p.is_file():
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        files += 1
        bytes_ += size
        if size >= BIG:
            over += 1
        if size > largest_bytes:
            largest, largest_bytes = p.name, size
    return {"files": files, "bytes": bytes_, "largest": largest, "largest_bytes": largest_bytes, "over_big": over}


def reading(gates: Path = GATES, runs: Path = RUNS) -> dict:
    out = {"ok": True, "reason": None, "entries": [], "by_kind": {}, "dependent": [], "source_only": [],
           "no_refusal": [], "missing": [], "corpus": {}}
    text = load(gates)
    if text is None:
        return {**out, "ok": False, "reason": f"{gates} is not on disk, so the gate has no entry list"}
    out["entries"] = entries(text)
    if not out["entries"]:
        return {**out, "ok": False, "reason": f"{gates} carries no `run` entry"}
    for e in out["entries"]:
        if e["kind"] != "python":
            continue
        src = load(e["path"])
        if src is None:
            out["missing"].append(e["path"])
            continue
        e["names_runs"] = ARTIFACT in src or "runs\\" in src
        e["refuses"] = REFUSAL in src
        e["json_out"] = "--json-out" in e["command"]
        if e["names_runs"]:
            out["dependent"].append(e["path"])
            if not e["refuses"]:
                out["no_refusal"].append(e["path"])
        else:
            out["source_only"].append(e["path"])
    out["by_kind"] = {k: sum(1 for e in out["entries"] if e["kind"] == k) for k in ("pytest", "python", "other")}
    out["corpus"] = census() if runs == RUNS else census()
    py = out["by_kind"]["python"]
    total = out["corpus"]
    out["spans"] = {
        "entries": len(out["entries"]), "pytest": out["by_kind"]["pytest"], "python": py,
        "dependent": len(out["dependent"]), "source_only": len(out["source_only"]),
        "refusing": len(out["dependent"]) - len(out["no_refusal"]), "no_refusal": len(out["no_refusal"]),
        "dependent_share": (len(out["dependent"]) / py) if py else 0.0,
        "refusal_share": ((len(out["dependent"]) - len(out["no_refusal"])) / len(out["dependent"]))
        if out["dependent"] else 0.0,
        "json_out": sum(1 for e in out["entries"] if e.get("json_out")),
        "files": total["files"], "mib": total["bytes"] / (1024 * 1024),
        "largest": total["largest"], "largest_mib": total["largest_bytes"] / (1024 * 1024),
        "over_big": total["over_big"], "missing": len(out["missing"]),
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the gate's entry list or the corpus is not there"}
                for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "CY1",
          "measured": f"{s['entries']} entries: {s['pytest']} the test suite, {s['python']} Python modules and "
                      f"{s['entries'] - s['pytest'] - s['python']} other, with {s['missing']} modules absent",
          "verdict": f"MET -- every entry parses and all {s['python']} Python entries name a module on disk" if
                     (s["entries"] > 0 and not r["missing"]) else
                     f"FALSIFIER FIRED -- absent {r['missing']}"}
    share = s["dependent_share"]
    j2 = {"id": "CY2",
          "measured": f"{s['dependent']} of the {s['python']} Python entries ({share:.3f}) invoke a module whose source "
                      f"names `runs/`, against {s['source_only']} that do not",
          "verdict": f"MET -- the gate is artifact-dependent, {share:.3f} of its entries" if share >= CLAIM_SHARE else
                     f"FALSIFIER FIRED -- {share:.3f} under {CLAIM_FLOOR:.2f}" if share < CLAIM_FLOOR else
                     f"NULL -- {share:.3f} between {CLAIM_FLOOR:.2f} and {CLAIM_SHARE:.2f}"}
    j3 = {"id": "CY3",
          "measured": f"{s['source_only']} entries invoke a module that does not name `runs/`",
          "verdict": f"MET -- {s['source_only']} entries read the corpus's sources rather than its artifacts" if
                     s["source_only"] >= SOURCE_ONLY_BAR else
                     f"FALSIFIER FIRED -- {s['source_only']} below {SOURCE_ONLY_FLOOR}" if
                     s["source_only"] < SOURCE_ONLY_FLOOR else
                     f"NULL -- {s['source_only']} between {SOURCE_ONLY_FLOOR} and {SOURCE_ONLY_BAR}"}
    rshare = s["refusal_share"]
    j4 = {"id": "CY4",
          "measured": f"{s['refusing']} of the {s['dependent']} dependent modules ({rshare:.3f}) carry a refusal path, "
                      f"and {s['no_refusal']} do not",
          "verdict": f"MET -- the refusal convention covers {rshare:.3f} of the dependent entries" if
                     rshare >= REFUSAL_SHARE else
                     f"FALSIFIER FIRED -- {rshare:.3f} under {REFUSAL_FLOOR:.2f}" if rshare < REFUSAL_FLOOR else
                     f"NULL -- {rshare:.3f} between {REFUSAL_FLOOR:.2f} and {REFUSAL_SHARE:.2f}"}
    j5 = {"id": "CY5",
          "measured": f"`runs/` holds {s['files']} files and {s['mib']:.1f} MiB, its largest {s['largest']} at "
                      f"{s['largest_mib']:.1f} MiB, with {s['over_big']} files over 5 MiB",
          "verdict": f"MET -- the corpus is {s['mib']:.1f} MiB over {s['files']} files, larger than a repository" if
                     (s["mib"] > TOTAL_BAR / (1024 * 1024) and s["files"] > FILE_BAR) else
                     f"FALSIFIER FIRED -- {s['mib']:.1f} MiB under {TOTAL_FLOOR // (1024 * 1024)}" if
                     s["mib"] < TOTAL_FLOOR / (1024 * 1024) else
                     f"NULL -- {s['mib']:.1f} MiB over {s['files']} files, between the bars"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== what a fresh clone reports ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the gate is not there')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    s = r["spans"]
    print("   the gate's own entry list, and the corpus it reads:")
    print(f"      entries            {s['entries']} ({s['pytest']} the test suite, {s['python']} Python modules)")
    print(f"      naming `runs/`     {s['dependent']} ({s['dependent_share']:.3f}) -- with `--json-out` on "
          f"{s['json_out']}")
    print(f"      sources only       {s['source_only']}")
    print(f"      carrying a refusal {s['refusing']} of the {s['dependent']} ({s['refusal_share']:.3f})")
    print(f"      `runs/`            {s['files']} files, {s['mib']:.1f} MiB, largest {s['largest']} at "
          f"{s['largest_mib']:.1f} MiB, {s['over_big']} files over 5 MiB")
    print(f"\n   and the {s['no_refusal']} dependent modules with no refusal in their source:")
    for p in r["no_refusal"]:
        print(f"      {p}")
    print("\n== the registered claims, CY1-CY5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (whether `runs/` should ship has been on every fire's thread list and no unit has put a number beside")
    print("    it; this is the number, and it is not a decision)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
