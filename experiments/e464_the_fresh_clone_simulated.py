"""E464 -- the fresh clone, simulated: the gate's own entries run against a tree with no corpus.

`e452` answered *what a fresh clone reports* by **reading source**: it parses the gate's entry list, asks whether each
module's text names a path under `runs/` and whether it carries a refusal, and named the modules that name `runs/` and
carry none -- the ones that would **report counts of nothing** on an empty corpus. That is a reading of the source and
`e452` said so: *no clone is simulated*.

**This unit simulates it.** It builds a tree that is this repository minus the corpus -- every tracked file, no `runs/`,
no `.git`, no virtual environment -- and then runs **every Python entry of `tools/gates.sh`** inside **its own copy of
that tree**, one subprocess each, with a wall-clock bound, and classifies what comes back: **declined** (printed
`REFUSED`, or exited non-zero, or ran past the bound), or **answered** (exited zero without a refusal). The copy is per
entry because some modules write an artifact to a default path when the gate does not pass `--json-out`, so a shared
tree would let the first such write seed the `runs/` directory the next entry is supposed to find empty. Four claims,
registered before the sweep.

- **CL1 -- and the tree under test is this repository and carries no corpus.** Every file the working tree holds is
  copied except `runs/`, the version-control directory, the virtual environment and the byte-cache directories; the
  copy carries at least **500** files and no `runs/`; and every Python entry of the gate names a module that is present
  in the copy. **Falsifier**: the copy fails, it carries `runs/`, it carries under **250** files, or a gate module is
  absent from it.
- **CL2 -- and the corpus-dependent entries decline rather than answer.** At least **four fifths** of the entries whose
  module names `runs/` decline. **Falsifier**: under **three fifths**; **null**: between. *A module that answers here
  reports a count of nothing, which is the one failure mode a clone must not have, and this is the measurement of how
  far the convention reaches.*
- **CL3 -- and nothing outside the ledger answers.** Every **corpus-dependent** entry that answers is one `e452`'s own
  reading calls artifact-dependent with no refusal path, so no module whose source *carries* a refusal answers anyway.
  **Falsifier**: a corpus-dependent entry that answers while its source carries a refusal. *Parity with `e452`'s number
  and not with its list is what this is about: a refusal in the source is not a refusal.*
- **CL4 -- and the entries that do not read the corpus are not disturbed by its absence.** At most **one fifth** of the
  entries whose module does not name `runs/` decline. **Falsifier**: over **two fifths**; **null**: between. *This is
  the control: without it, CL2 would be satisfied by a harness in which nothing runs at all.*

**What it can do beyond that.** It turns thread (b) from a list of names into a count of behaviours under the exact
condition a clone is in, and it separates the two ways the corpus's absence shows up -- a printed refusal, which is the
convention, and a non-zero exit, which is not the same thing. It also bounds the exposure: the list of modules that
would answer a clone is a list this unit prints and the gate can be read against.

**What it cannot do.** *A copy and not a checkout*: the tree under test is the working tree minus the corpus, so it
carries uncommitted files and its fingerprint moves with the working tree rather than with a commit. *And the corpus is
removed, not missing*: a module could in principle behave differently when `runs/` exists but is empty, and none of
that is measured here. *And one environment*: every entry is run with **this** interpreter and this machine's
libraries, so a module that fails for a reason unrelated to the corpus is counted as declining -- CL4 is the control
for that and it is a bound, not a proof. *And a bound is not a diagnosis*: this unit says which modules answer, not
why their refusal is missing.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e452_what_a_fresh_clone_reports as e452

GATES = Path("tools/gates.sh")
EXCLUDED = ("runs", ".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules")
ARTIFACT = "runs/"
REFUSAL = "REFUSED"
TIMEOUT = 300.0
WORKERS = 6
FILES_BAR = 500
FILES_FLOOR = 250
DECLINE_SHARE = 0.8
DECLINE_FLOOR = 0.6
CONTROL_SHARE = 0.2
CONTROL_FLOOR = 0.4
TAIL = 400
CLAIMS = (
    ("CL1", f"and the tree under test is this repository and carries no corpus, over {FILES_BAR} files",
     "Every file the working tree holds is copied except the corpus, the version-control directory, the virtual "
     "environment and the byte-cache directories; the copy carries at least 500 files and no runs; and every Python "
     "entry of the gate names a module present in the copy",
     "falsifier: the copy fails, it carries runs, it carries under 250 files, or a gate module is absent from it"),
    ("CL2", f"and the corpus-dependent entries decline rather than answer, at least {DECLINE_SHARE:.0%}",
     "At least four fifths of the entries whose module names a path under runs decline -- refused, non-zero, or past "
     "the bound",
     f"falsifier: under {DECLINE_FLOOR:.0%}; null: between"),
    ("CL3", "and nothing outside the ledger answers",
     "Every corpus-dependent entry that answers is one e452's reading calls artifact-dependent with no refusal path",
     "falsifier: a corpus-dependent entry that answers while its source carries a refusal"),
    ("CL4", f"and the entries that do not read the corpus are not disturbed, at most {CONTROL_SHARE:.0%} decline",
     "At most one fifth of the entries whose module does not name a path under runs decline",
     f"falsifier: over {CONTROL_FLOOR:.0%}; null: between"),
)


def load(path) -> str | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _ignored(name: str) -> bool:
    return name in EXCLUDED


#: the copies this process has made, so a caller can remove them again without the reading having to carry a path
CREATED: list[Path] = []


def build_tree(dst: Path | None = None) -> dict:
    """Copy this repository without its corpus, and report what the copy is."""
    root = Path(dst) if dst is not None else Path(tempfile.mkdtemp(prefix="e464_clone_"))
    try:
        shutil.copytree(Path.cwd(), root, dirs_exist_ok=True,
                        ignore=lambda d, names: [n for n in names if _ignored(n)])
    except (OSError, shutil.Error) as exc:
        return {"ok": False, "reason": f"the copy failed: {exc}", "root": None}
    if dst is None:
        CREATED.append(root)
    files = sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file())
    digest = hashlib.sha1(" ".join(files).encode()).hexdigest()[:12]
    return {"ok": True, "reason": None, "root": str(root), "files": len(files), "fingerprint_sha1": digest,
            "carries_runs": (root / "runs").exists()}


def cleanup(keep: bool = False) -> int:
    """Remove the copies this process made, unless they were asked for."""
    if keep:
        return 0
    gone = 0
    while CREATED:
        root = CREATED.pop()
        if root.is_dir():
            shutil.rmtree(root, ignore_errors=True)
            gone += 1
    return gone


def _kill_tree(proc) -> None:
    """Kill the entry and anything it started.

    A bare `kill` is not enough on Windows: the entries that run past the bound are the ones whose own children keep
    the pipe open, so the reader has to take the tree and then wait for the handle rather than assume it is gone.
    """
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=120)
        else:
            proc.kill()
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        proc.wait(timeout=120)
    except (subprocess.TimeoutExpired, OSError):
        pass


def _gone(path: Path) -> bool:
    """Whether the copy is really gone.

    `Path.exists()` is not usable for this: it swallows `OSError` and answers **False** for a directory Windows is
    holding, so the retry below broke on its first pass and six copies -- exactly the six entries that ran past the
    bound -- were left on disk. A locked path is still there.
    """
    try:
        path.stat()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False


def run_entry(entry: dict, root: str) -> dict:
    """One gate entry inside **its own** copy of the tree: what it exits with, whether it refuses, and how long.

    The copy is per entry and not shared, because some modules write an artifact to a default path when the gate does
    not pass `--json-out` -- `e97` is one -- and a shared tree would let the first such write seed the `runs/`
    directory the next entry is supposed to find empty.
    """
    started = time.time()
    try:
        work = Path(tempfile.mkdtemp(prefix=f"e464_{entry['name']}_"))
    except OSError as exc:
        return {"exit": None, "refused": False, "timeout": False, "crashed": False,
                "seconds": time.time() - started, "tail": f"no working copy could be made: {exc}"}
    try:
        shutil.copytree(root, work, dirs_exist_ok=True)
        try:
            proc = subprocess.Popen([sys.executable, "-m", entry["module"]], cwd=str(work),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except OSError as exc:
            return {"exit": None, "refused": False, "timeout": False, "crashed": False,
                    "seconds": time.time() - started, "tail": f"the entry could not be started: {exc}"}
        try:
            raw, _ = proc.communicate(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            return {"exit": None, "refused": False, "timeout": True, "crashed": False,
                    "seconds": time.time() - started, "tail": f"past the {TIMEOUT:.0f} s bound"}
        text = (raw or b"").decode("utf-8", "replace")
        return {"exit": int(proc.returncode), "refused": REFUSAL in text, "timeout": False,
                "crashed": "Traceback (most recent call last)" in text,
                "seconds": time.time() - started,
                "tail": text.strip().splitlines()[-1][:TAIL] if text.strip() else ""}
    except (OSError, shutil.Error) as exc:
        return {"exit": None, "refused": False, "timeout": False, "crashed": False,
                "seconds": time.time() - started, "tail": f"the working copy failed: {exc}"}
    finally:
        #: the copy goes even when the entry was killed, and a killed entry holds its directory for longer than a
        #: moment on Windows -- the retry is long and it is only ever entered by the entries that ran past the bound
        for _ in range(40):
            shutil.rmtree(work, ignore_errors=True)
            if _gone(work):
                break
            time.sleep(1.0)


def sweep(entries: list[dict], root: str, runner=run_entry) -> list[dict]:
    py = [e for e in entries if e["kind"] == "python"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        got = list(pool.map(lambda e: runner(e, root), py))
    return [{**{k: e[k] for k in ("name", "module", "path")}, **g} for e, g in zip(py, got)]


def reading(gates: Path = GATES, builder=build_tree, runner=run_entry) -> dict:
    out = {"ok": True, "reason": None, "tree": {}, "entries": [], "ledger": {}, "spans": {}}
    text = load(gates)
    if text is None:
        return {**out, "ok": False, "reason": f"{gates} is not on disk, so the gate has no entry list"}
    parsed = e452.entries(text)
    if not parsed:
        return {**out, "ok": False, "reason": f"{gates} carries no `run` entry"}
    py = [e for e in parsed if e["kind"] == "python"]
    tree = builder()
    if not tree.get("ok"):
        return {**out, "ok": False, "reason": tree.get("reason") or "the tree could not be built"}
    missing = sorted(e["path"] for e in py if not (Path(tree["root"]) / e["path"]).is_file())
    out["tree"] = {k: tree[k] for k in ("files", "fingerprint_sha1", "carries_runs")}
    out["tree"]["missing"] = missing
    if tree["carries_runs"] or missing:
        return {**out, "ok": False,
                "reason": f"the copy carries a corpus ({tree['carries_runs']}) or is missing {missing[:3]} of its "
                          f"own modules"}
    out["entries"] = sweep(parsed, tree["root"], runner)
    ledger = e452.reading(gates=gates, runs=Path("runs"))
    out["ledger"] = {"no_refusal": sorted(ledger.get("no_refusal") or []),
                     "dependent": sorted(ledger.get("dependent") or []),
                     "source_only": sorted(ledger.get("source_only") or [])}
    dep = set(out["ledger"]["dependent"])
    for e in out["entries"]:
        e["names_runs"] = e["path"] in dep
        e["declined"] = bool(e["refused"] or e["timeout"] or (e["exit"] not in (0, None)))
        e["answered"] = (e["exit"] == 0 and not e["refused"] and not e["timeout"])
        if e["path"] in out["ledger"]["no_refusal"]:
            e["ledger"] = "no refusal path"
        elif e["path"] in dep:
            e["ledger"] = "refuses"
        elif e["path"] in set(out["ledger"]["source_only"]):
            e["ledger"] = "does not read runs"
        else:
            e["ledger"] = "not in the ledger"
    dependent = [e for e in out["entries"] if e["names_runs"]]
    source_only = [e for e in out["entries"] if not e["names_runs"]]
    answered = [e["path"] for e in out["entries"] if e["answered"]]
    out["spans"] = {
        "entries": len(parsed), "python": len(py),
        "dependent": len(dependent), "source_only": len(source_only),
        "declined": sum(1 for e in out["entries"] if e["declined"]),
        "refused": sum(1 for e in out["entries"] if e["refused"]),
        "nonzero": sum(1 for e in out["entries"] if e["exit"] not in (0, None) and not e["timeout"]),
        "timeout": sum(1 for e in out["entries"] if e["timeout"]),
        "crashed": sum(1 for e in out["entries"] if e["crashed"]),
        "answered": len(answered), "answered_paths": sorted(answered),
        "dependent_declined": sum(1 for e in dependent if e["declined"]),
        "dependent_share": (sum(1 for e in dependent if e["declined"]) / len(dependent)) if dependent else 0.0,
        "source_declined": sum(1 for e in source_only if e["declined"]),
        "source_share": (sum(1 for e in source_only if e["declined"]) / len(source_only)) if source_only else 0.0,
        #: the two lists the third claim is read on: every answering entry, and the answering **dependent** ones
        "answered_dependent": sorted(e["path"] for e in out["entries"] if e["names_runs"] and e["answered"]),
        "outside_ledger": sorted(e["path"] for e in out["entries"]
                                 if e["names_runs"] and e["answered"] and e["ledger"] != "no refusal path"),
        "seconds": statistics.fmean([e["seconds"] for e in out["entries"]]) if out["entries"] else 0.0,
        "slowest": max((e["seconds"] for e in out["entries"]), default=0.0),
        "files": out["tree"]["files"], "fingerprint": out["tree"]["fingerprint_sha1"],
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the gate's entry list or the tree is not there"}
                for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "CL1",
          "measured": f"the copy carries {s['files']} files, fingerprint {s['fingerprint']}, no corpus, and all "
                      f"{s['python']} Python entries' modules are present",
          "verdict": f"MET -- the tree under test is this repository minus its corpus, over {FILES_BAR} files and "
                     "missing none of its own modules" if
                     (s["files"] >= FILES_BAR and not r["tree"]["carries_runs"] and not r["tree"]["missing"]) else
                     f"FALSIFIER FIRED -- {s['files']} files, corpus {r['tree']['carries_runs']}, missing "
                     f"{r['tree']['missing'][:3]}"}
    share = s["dependent_share"]
    if not s["dependent"]:
        j2 = {"id": "CL2", "measured": "no gate entry's module names a path under runs",
              "verdict": "REFUSED -- there is no corpus-dependent entry to measure"}
    else:
        j2 = {"id": "CL2",
              "measured": f"{s['dependent_declined']} of {s['dependent']} corpus-dependent entries decline "
                          f"({100 * share:.0f}%): {s['refused']} print a refusal, {s['nonzero']} exit non-zero and "
                          f"{s['timeout']} run past the bound",
              "verdict": f"MET -- the convention reaches {100 * share:.0f}% of the entries that need the corpus" if
                         share >= DECLINE_SHARE else
                         f"FALSIFIER FIRED -- {100 * share:.0f}%" if share < DECLINE_FLOOR else
                         f"NULL -- {100 * share:.0f}%, between {DECLINE_FLOOR:.0%} and {DECLINE_SHARE:.0%}"}
    outside = s["outside_ledger"]
    j3 = {"id": "CL3",
          "measured": f"{s['answered']} entries answer on the empty tree and {len(s['answered_dependent'])} of them "
                      f"name a path under runs, of which {len(outside)} are outside the ledger of "
                      f"{len(r['ledger']['no_refusal'])} modules `e452` calls artifact-dependent with no refusal",
          "verdict": "MET -- no entry that names the corpus and carries a refusal in its source answers anyway" if
                     not outside else
                     f"FALSIFIER FIRED -- a refusal in the source is not a refusal: {outside[:6]}"}
    control = s["source_share"]
    if not s["source_only"]:
        j4 = {"id": "CL4", "measured": "no gate entry's module avoids a path under runs",
              "verdict": "REFUSED -- there is no corpus-independent entry to control the sweep with"}
    else:
        j4 = {"id": "CL4",
              "measured": f"{s['source_declined']} of {s['source_only']} entries whose module names no corpus path "
                          f"decline ({100 * control:.0f}%), so the sweep is not one in which nothing runs",
              "verdict": f"MET -- the entries that do not read the corpus are not disturbed by its absence, "
                         f"{100 * control:.0f}%" if control <= CONTROL_SHARE else
                         f"FALSIFIER FIRED -- {100 * control:.0f}%" if control > CONTROL_FLOOR else
                         f"NULL -- {100 * control:.0f}%, between {CONTROL_SHARE:.0%} and {CONTROL_FLOOR:.0%}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the fresh clone, simulated ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the gate or the tree is not there')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    s = r["spans"]
    print("   this repository copied without `runs/`, without the version-control directory and without the virtual")
    print("   environment, and every Python entry of the gate then run inside the copy, one subprocess each")
    print(f"\n   the copy: {s['files']} files, fingerprint {s['fingerprint']}, no corpus")
    print(f"   the sweep: {s['python']} Python entries, {s['refused']} refusals, {s['nonzero']} non-zero exits, "
          f"{s['crashed']} tracebacks, {s['timeout']} past the bound, {s['answered']} answering; mean "
          f"{s['seconds']:.1f} s, slowest {s['slowest']:.1f} s")
    print("\n   the corpus-dependent entries that answer on an empty tree -- the ones a clone would take numbers from:")
    named = [e for e in r["entries"] if e["names_runs"] and e["answered"]]
    if not named:
        print("      (none)")
    for e in sorted(named, key=lambda x: x["path"]):
        print(f"      {e['path']:<62} {e['ledger']:<20} {e['tail'][:80]}")
    print("\n   the entries that answer and whose source names no corpus path, with what the ledger calls them:")
    rest = [e for e in r["entries"] if e["answered"] and not e["names_runs"]]
    for e in sorted(rest, key=lambda x: x["path"]):
        print(f"      {e['path']:<62} {e['ledger']:<20} {e['tail'][:80]}")
    print("\n   the entries whose module names no corpus path and which still decline on the empty tree:")
    broke = [e for e in r["entries"] if not e["names_runs"] and e["declined"]]
    for e in sorted(broke, key=lambda x: x["path"])[:12]:
        print(f"      {e['path']:<62} exit {str(e['exit']):>4}  {e['tail'][:80]}")
    print("\n== the registered claims, CL1-CL4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e452` read this out of the modules' source and said no clone was simulated; this runs the gate's own")
    print("    entries against one, so the refusal convention is measured rather than counted in the text)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--keep", action="store_true", help="leave the copy on disk for inspection")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    code = report(r)
    cleanup(keep=args.keep)
    return code


if __name__ == "__main__":
    sys.exit(main())
