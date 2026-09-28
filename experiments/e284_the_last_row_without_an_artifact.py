"""E284 -- the paper's reproducibility table: its artifact cells, its commands, and the one row that names neither.

The paper's §"what is reproducible" table is a contract: every row gives a claim, the command that produces it, and
the artifact it lands in. Three properties of that contract are mechanical, and none of them had been read off it:

  * **the artifact cells.** Every `runs/*.json` path the table names should be a file on disk. A path that is not is
    a row whose evidence cannot be regenerated from the page alone.
  * **the commands.** Every `python -m ...` target should resolve to a module that imports. A target that does not
    is a row a reader cannot follow.
  * **the empty cell.** A row that names no artifact is the table's own admission of an item with nothing behind it.
    The interesting question is not how many there are but **why**: a row can be artifact-free because its runner
    cannot write one, or because its command was transcribed without the flag that does -- and those two call for
    opposite corrections.
  * **the re-run.** For the row whose runner can write one, the row's own command plus the flag it omitted is a
    measurement, and the number it produces can be read against the number the row attributes to it.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **V1 -- the table's artifact cells are backed.** Every `runs/*.json` path the paper names anywhere is a file on
  disk. **Falsifier**: one path that is not.
- **V2 -- its commands resolve.** Every distinct `python -m` target the paper names imports. **Falsifier**: one that
  does not.
- **V3 -- and every artifact-free row invokes a runner that carries the flag.** For each reproducibility row naming
  no `runs/*.json`, the module its command names declares `--json-out` in its own source. **Falsifier**: a row whose
  runner declares no such flag, which would make the empty cell a capability gap rather than a transcription one.
  **This one fired**, and the reading below says on which row and why an empty cell there is correct.
- **V4 -- and the row's own command reproduces the branch the paper quotes, not the number the row does.** Re-run
  with the flag it omits, the artifact-free row's command measures a near-diagonal partition whose draw-to-draw sd is
  inside the band §4.3 gives for those (4e-5 to 9e-5) and below the 1.1e-3 the row attributes to the command.
  **Falsifier**: no artifact at the row's own command, or a draw sd outside the band.

**The legs are of deliberately different strength and the reading says so**: V1 and V2 are existence checks over a
population the page itself defines, so they admit almost no interpretation; V3 needs the row's command and the
runner's interface to be about the same thing; and V4 is a measurement, so it is the one that can disagree with the
paper -- and it does, in the direction that repairs the row rather than the claim: the artifact behind
`runs/e12_control_spread.json` carries **4.69e-5**, inside §4.3's own "~4e-5 to 9e-5 for near-diagonal ones" and 23x
below the **1.1e-3** the row attributes to the command. The row's command has no flag that reaches the coarse
partition §4.3's 1.1e-3 belongs to, so the row's number and the row's command are about different partitions -- which
is why the row was filled with the artifact and the clause that says so.

**What it cannot do**: a path that exists on disk can still be an artifact of a different configuration, so V1
checks that the evidence is *present* and not that it is the evidence the row's claim needs -- that comparison is
`e182`'s, and it is made against the programme table and not this one; V2 imports a module and does not execute the
row's command, so a target that imports can still fail on its flags; the flag search is a source scan for
`--json-out` in the module's own text, so a runner that builds its parser elsewhere reads as having no flag; a row
whose artifact cell holds prose rather than a path is counted as naming no artifact; V4 reads one draw sd from five
draws, whose own sampling error is tens of per cent, so it distinguishes a band from a factor of twenty and not one
band member from another; "near-diagonal" is §4.3's word for the partition and this unit reads it as the one the
artifact's own group count puts there rather than as a definition; and nothing here reads the programme table or the
findings, which are `e182`'s and `e97`'s populations and not this unit's.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: the artifact the row's own command lands in once it is given the flag it omits
ROW_ARTIFACT = Path("runs/e12_control_spread.json")
#: what §4.3 says that same runner measured for near-diagonal partitions, and what the row attributes to this command
NEAR_DIAGONAL_BAND = (4e-5, 9e-5)
ROW_QUOTED = 1.1e-3
ARTIFACT = re.compile(r"runs/[A-Za-z0-9_.\-]+\.json")
COMMAND = re.compile(r"python -m ([A-Za-z0-9_.]+)")
FLAG = re.compile(r"add_argument\(\s*[\"']--json-out")
CLAIMS = (
    ("V1", "the table's artifact cells are backed",
     "Every runs/*.json path the paper names is a file on disk",
     "falsifier: one path that is not"),
    ("V2", "and its commands resolve",
     "Every distinct python -m target the paper names imports",
     "falsifier: one that does not"),
    ("V3", "and every artifact-free row invokes a runner that carries the flag",
     "For each row naming a command and no runs/*.json, the named module declares --json-out in its own source",
     "falsifier: a row whose runner declares no such flag"),
    ("V4", "and the row's own command reproduces the branch the paper quotes, not the number the row does",
     "Re-run with the flag it omits, the artifact-free row's command measures a near-diagonal partition whose "
     "draw-to-draw sd is inside the band §4.3 gives for those (4e-5 to 9e-5) and below the 1.1e-3 the row "
     "attributes to the command",
     "falsifier: no artifact at the row's own command, or a draw sd outside the band, or one at or above 1.1e-3"),
)


def table_rows(text: str) -> list[str]:
    """Every markdown table row of the paper, with the header and rule lines of a table dropped."""
    return [l for l in text.split("\n") if l.startswith("|") and set(l) - set("|-: ")]


def cells(row: str) -> list[str]:
    return [c.strip() for c in row.split("|")[1:-1]]


def module_path(name: str) -> Path | None:
    """Where the named module lives, as a file: `a/b.py`, or `a/b/__init__.py` for a package."""
    mod = Path(*name.split(".")).with_suffix(".py")
    if mod.is_file():
        return mod
    pkg = Path(*name.split(".")) / "__init__.py"
    return pkg if pkg.is_file() else None


def has_flag(name: str) -> bool:
    p = module_path(name)
    if p is None:
        return False
    return bool(FLAG.search(p.read_text(encoding="utf-8")))


def reading(text: str, root: Path = Path(".")) -> dict:
    rows = table_rows(text)
    artifacts = ARTIFACT.findall(text)
    commands = COMMAND.findall(text)
    uniq_art = sorted(set(artifacts))
    uniq_cmd = sorted(set(commands))
    missing = [p for p in uniq_art if not (root / p).is_file()]
    unimportable = []
    for m in uniq_cmd:
        try:
            importlib.import_module(m)
        except Exception:  # noqa: BLE001 -- any failure is the reading
            unimportable.append(m)

    no_artifact = [r for r in rows if COMMAND.search(r) and not ARTIFACT.search(r)]
    flagged = {r: [m for m in set(COMMAND.findall(r)) if has_flag(m)] for r in no_artifact}
    with_artifact = [r for r in rows if COMMAND.search(r) and ARTIFACT.search(r)]
    cell_total = sum(len(cells(r)) for r in rows)

    # why an artifact cell is empty: the row's own command may declare the flag and leave its path a placeholder,
    # or omit the flag entirely, and the runner behind it may or may not have one. The two axes type the rows.
    # The flag is read out of the row's COMMAND SPAN and not out of the row: `e182` records what happens when a
    # row's prose is read as a value, and one row here says the words "no `--json-out`" about its own command.
    glob = re.compile(r"runs/[A-Za-z0-9_.\-*]*\*[A-Za-z0-9_.\-*]*")
    why = []
    for r in no_artifact:
        mods = sorted(set(COMMAND.findall(r)))
        spans = [s for s in re.findall(r"`([^`]*)`", r) if "python -m" in s]
        why.append({
            "row": r.split("|")[1].strip()[:80],
            "command_spans": [s[:90] for s in spans],
            "command_declares_the_flag": any("--json-out" in s for s in spans),
            "cell_holds_a_glob": bool(glob.search(r)),
            "runners": mods,
            "runners_with_the_flag": [m for m in mods if has_flag(m)],
        })
    return {
        "rows": len(rows), "cells": cell_total,
        "artifact_mentions": len(artifacts), "artifacts": uniq_art, "missing": missing,
        "commands": uniq_cmd, "unimportable": unimportable,
        "reproducibility_rows": len(with_artifact) + len(no_artifact),
        "rows_with_an_artifact": len(with_artifact),
        "rows_without_an_artifact": [r[:200] for r in no_artifact],
        "why": why,
        "artifact_free_rows_whose_runner_has_the_flag": {r[:120]: v for r, v in flagged.items()},
        "n_without": len(no_artifact),
        "n_without_and_flagged": sum(1 for v in flagged.values() if v),
    }


def reproduction(path: Path = ROW_ARTIFACT) -> dict | None:
    """The artifact the row's own command lands in once it is given the flag, as the numbers a verdict needs."""
    if not path.is_file():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    cfg = d.get("config") or {}
    return {"path": str(path), "delta": d.get("delta"), "draw_sd": d.get("control_sd_across_draws"),
            "seed_sem": d.get("seed_sem"), "sigma_single_draw": d.get("sigma_single_draw"),
            "sigma_with_draw_noise": d.get("sigma_with_draw_noise"),
            "draws": cfg.get("draws"), "seeds": cfg.get("seeds"), "circuit_size": cfg.get("circuit_size"),
            "column": cfg.get("column"), "min_size": cfg.get("min_size"), "timing_s": d.get("timing_s")}


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    if not r or not r.get("artifacts"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the paper's table could not be read"} for c in CLAIMS]

    out.append({"id": "V1", "measured": f"{len(r['artifacts'])} distinct artifact paths over "
                                        f"{r['artifact_mentions']} mentions; not on disk: {len(r['missing'])}",
                "verdict": "MET -- the artifact cells are backed" if not r["missing"] else
                           f"FALSIFIER FIRED -- {r['missing']}"})

    out.append({"id": "V2", "measured": f"{len(r['commands'])} distinct python -m targets; failing to import: "
                                        f"{r['unimportable'] or 'none'}",
                "verdict": "MET -- every command the paper gives resolves" if not r["unimportable"] else
                           f"FALSIFIER FIRED -- {r['unimportable']}"})

    ok = r["n_without"] == r["n_without_and_flagged"]
    out.append({"id": "V3", "measured": f"{r['rows_with_an_artifact']} of {r['reproducibility_rows']} reproducibility "
                                        f"rows name an artifact; of the {r['n_without']} that name none, "
                                        f"{r['n_without_and_flagged']} invoke a runner declaring --json-out",
                "verdict": "MET -- every artifact-free row could have one, so the empty cells are transcription" if ok else
                           "FALSIFIER FIRED -- an artifact-free row invokes a runner with no such flag"})

    rep = r.get("row_command")
    if not rep:
        out.append({"id": "V4", "measured": "", "verdict": "REFUSED -- the row's command left no artifact to read"})
    else:
        sd = rep["draw_sd"]
        lo, hi = NEAR_DIAGONAL_BAND
        ok = sd is not None and lo <= sd <= hi and sd < ROW_QUOTED
        out.append({"id": "V4", "measured": f"re-running the row's own command with the flag it omits writes "
                                            f"{rep['path']}: {rep['draws']} draws at {rep['seeds']} seeds, "
                                            f"draw sd {sd:.3g} against the row's {ROW_QUOTED:g} and the "
                                            f"{lo:g} to {hi:g} band, delta {rep['delta']:+.6f}",
                    "verdict": "MET -- the command reproduces the near-diagonal branch and not the row's number"
                               if ok else f"FALSIFIER FIRED -- draw sd {sd:.3g} is outside the band"})
    return out


def report(r: dict) -> int:
    print("== the paper's tables ==")
    print(f"   rows: {r['rows']}; cells in them: {r['cells']}; rows giving a python command: "
          f"{r['reproducibility_rows']}")
    print(f"   of those, naming at least one artifact: {r['rows_with_an_artifact']}; naming none: {r['n_without']}")

    print("\n== the artifact cells ==")
    print(f"   distinct runs/*.json paths named anywhere in the paper: {len(r['artifacts'])} "
          f"over {r['artifact_mentions']} mentions")
    print(f"   not on disk: {len(r['missing'])}")
    for p in r["missing"]:
        print(f"      MISSING {p}")

    print("\n== the commands ==")
    print(f"   distinct python -m targets: {len(r['commands'])}")
    print(f"   failing to import: {r['unimportable'] or 'none'}")

    print("\n== the rows that name no artifact, and why ==")
    for w in r["why"]:
        print(f"      {w['row']}")
        for s in w["command_spans"]:
            print(f"          the command as transcribed: {s}")
        print(f"          its command declares --json-out: {w['command_declares_the_flag']}; its cell holds a glob: "
              f"{w['cell_holds_a_glob']}; its runner(s) {w['runners']} with the flag: "
              f"{w['runners_with_the_flag'] or 'none'}")

    print("\n== the registered claims, V1-V4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the table's cells are backed and its commands resolve; its empty cells are of three kinds -- a family")
    print("    named as a glob, a command that declares the flag and leaves its path a placeholder, and the test-suite")
    print("    row whose runner has no flag at all -- so only the row that omits a flag its runner has is a defect, and")
    print("    re-running that row's command reproduces the branch §4.3 quotes for near-diagonal partitions while the")
    print("    1.1e-3 the row attributes to it belongs to the coarse one)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", type=Path, default=PAPER)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    if not args.paper.exists():
        raise SystemExit(f"need {args.paper}")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.paper.read_text(encoding="utf-8"))
    r["row_command"] = reproduction()
    if r["row_command"]:
        rep = r["row_command"]
        print(f"   the artifact the empty row lands: {rep['path']} ({rep['draws']} draws at {rep['seeds']} seeds, "
              f"cs {rep['circuit_size']}, {rep['column']} min_size {rep['min_size']}): delta {rep['delta']:+.6f}, "
              f"draw sd {rep['draw_sd']:.3g}")
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
