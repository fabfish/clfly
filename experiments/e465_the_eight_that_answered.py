"""E465 -- the eight that answered: which of them change their mind when the corpus goes.

`e464` ran the gate's own entries against a tree with no corpus and found **eight** entries that name a path under
`runs/`, carry the word `REFUSED` in their source, and answered anyway -- and its third claim's firing was reported as
*a refusal in the source is not a refusal*, with the eight named. What it could not do is the thing its reading needs to
be trusted for: **it ran each entry once**, so an entry that answered may have been reporting a number it would report
with the corpus in place, or a number that only an empty pool makes true, and the sweep cannot tell the two apart.

**This unit tells them apart.** For each of the eight it runs the module **twice** with its output written outside the
corpus, once with this repository as the working directory and once inside a corpus-less copy of it, and compares the
**claim verdicts the module writes for itself**: an entry whose verdicts are the same both ways never used the corpus it
mentions, and an entry whose verdicts move was answering a question its input could not support. Four claims,
registered before the first arm.

- **RB1 -- and the two arms are one configuration.** Each of the eight produces an artifact in both arms, every arm's
  artifact carries a `claims` block, the two arms' top-level keys are equal for each module, and the copy the second arm
  runs in carries no corpus. **Falsifier**: an arm with no artifact, a module whose two artifacts record no `claims`, a
  pair whose key sets differ, or a copy that carries `runs/`.
- **RB2 -- and most of the eight did not need the corpus.** At least **half** of the eight change no claim verdict when
  it is absent. **Falsifier**: fewer than **a quarter**; **null**: between. *This is the reading `e464`'s third claim
  fired on: if most of the eight never used `runs/`, its firing was about the source text and not about nine modules
  reporting numbers a clone should not have.*
- **RB3 -- and the rest answer a question their input cannot support.** At least **one** of the eight changes at least
  one claim verdict. **Falsifier**: none changes a verdict. *A firing here would be the other half of the correction:
  that at least one of the eight is exactly what `e464` called all of them.*
- **RB4 -- and the corpus arm is the gate's own reading.** For each module that also has an artifact from the gate, the
  corpus arm's verdict classes equal the gate artifact's. **Falsifier**: a module whose two verdict class maps differ;
  **null**: no module has a gate artifact to compare with. *This is the instrument's own check: an arm that disagrees
  with the gate is not the configuration the gate runs.*

**What it can do beyond that.** It turns *a refusal in the source is not a refusal* into a count of modules that answer
the same way with and without the corpus and a list of those that do not, which is the scope a repair of `e464`'s
finding needs and the one its own sweep could not give.

**What it cannot do.** *One pair of runs each*: a module whose verdicts happen to agree on this corpus and this machine
is called corpus-free, and a module that reads `runs/` for something no claim depends on is called the same way. *And
the corpus arm is the repository as it stands*: it reads the whole corpus and not a fixed sample, so the arm is a
reading of today's tree. *And a verdict class is coarse*: a claim whose numbers move while its verdict does not is
counted as unchanged, because what this unit asks is whether the answer would be different and not whether a digit in
it would. *And no repair*: this unit says which of the eight are vacuous and does not change any of them.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e452_what_a_fresh_clone_reports as e452
from experiments import e464_the_fresh_clone_simulated as e464

#: the sweep whose answering set this unit re-reads, and the gate whose commands name the modules
SWEEP = Path("runs/e464_the_fresh_clone_simulated.json")
GATES = Path("tools/gates.sh")
RUNS = Path("runs")
JSON_OUT = re.compile(r"--json-out\s+(\S+)")
TIMEOUT = 900.0
WORKERS = 4
HALF = 0.5
QUARTER = 0.25
CLAIMS = (
    ("RB1", "and the two arms are one configuration",
     "Each of the eight produces an artifact in both arms, every arm's artifact carries a claims block, the two arms' "
     "top-level keys are equal for each module, and the copy the second arm runs in carries no corpus",
     "falsifier: an arm with no artifact, a module whose two artifacts record no claims, a pair whose key sets "
     "differ, or a copy that carries runs"),
    ("RB2", f"and most of the eight did not need the corpus, at least {HALF:.0%}",
     "At least half of the eight change no claim verdict when the corpus is absent",
     f"falsifier: fewer than {QUARTER:.0%}; null: between"),
    ("RB3", "and the rest answer a question their input cannot support",
     "At least one of the eight changes at least one claim verdict",
     "falsifier: none changes a verdict"),
    ("RB4", "and the corpus arm is the gate's own reading",
     "For each module that also has an artifact from the gate, the corpus arm's verdict classes equal the gate "
     "artifact's",
     "falsifier: a module whose two verdict class maps differ; null: no module has a gate artifact to compare with"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def verdicts(doc: dict | None) -> dict:
    """The claim verdicts a module writes for itself, as the class of each: what moved and what did not."""
    out = {}
    for row in (doc or {}).get("claims") or []:
        if isinstance(row, dict) and "id" in row:
            out[str(row["id"])] = str(row.get("verdict", "")).split(" -- ")[0].strip()
    return out


def commands(gates: Path = GATES) -> dict:
    """Each gate entry's module path against the artifact its own command writes."""
    p = Path(gates)
    if not p.is_file():
        return {}
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    out = {}
    for e in e452.entries(text):
        if e["kind"] != "python":
            continue
        m = JSON_OUT.search(e["command"])
        if m:
            out[e["path"]] = m.group(1).replace("\\", "/")
    return out


def _kill_tree(proc) -> None:
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


def module_of(path: str) -> str:
    """The dotted name a gate entry's path is invoked as: `e452` parses the command into a path and the runner needs
    the name, and passing the path to `-m` fails instantly -- which is how the first run of this unit reported that
    none of the eight wrote an artifact."""
    if not path.endswith(".py") or "/" not in path:
        raise ValueError(f"{path} is not a module path")
    return path[:-3].replace("/", ".")


def run_arm(module: str, cwd: Path, out: Path) -> dict:
    """One module, one arm: what it exits with and the artifact it writes beside the corpus."""
    started = time.time()
    if out.exists():
        out.unlink()
    try:
        proc = subprocess.Popen([sys.executable, "-m", module_of(module), "--json-out", str(out)], cwd=str(cwd),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as exc:
        return {"exit": None, "timeout": False, "crashed": False, "seconds": time.time() - started,
                "claims": {}, "keys": [], "tail": f"the module could not be started: {exc}"}
    try:
        raw, _ = proc.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        return {"exit": None, "timeout": True, "crashed": False, "seconds": time.time() - started,
                "claims": {}, "keys": [], "tail": f"past the {TIMEOUT:.0f} s bound"}
    text = (raw or b"").decode("utf-8", "replace")
    doc = load(out)
    if out.exists():
        try:
            out.unlink()
        except OSError:
            pass
    return {"exit": int(proc.returncode), "timeout": False,
            "crashed": "Traceback (most recent call last)" in text,
            "seconds": time.time() - started,
            "claims": verdicts(doc), "keys": sorted(doc) if doc else [],
            "refused": "REFUSED" in text,
            "tail": text.strip().splitlines()[-1][:300] if text.strip() else ""}


def reading(sweep: Path = SWEEP, gates: Path = GATES, builder=e464.build_tree) -> dict:
    out = {"ok": True, "reason": None, "eight": [], "entries": {}, "tree": {}, "gate": {}, "spans": {}}
    doc = load(sweep)
    if doc is None:
        return {**out, "ok": False, "reason": f"{sweep} is not there, so there is no answering set to re-read"}
    answered = list((doc.get("spans") or {}).get("outside_ledger") or [])
    if not answered:
        return {**out, "ok": False, "reason": "the sweep names no corpus-dependent entry that answered"}
    tree = builder()
    if not tree.get("ok"):
        return {**out, "ok": False, "reason": tree.get("reason") or "the copy could not be built"}
    out["tree"] = {k: tree[k] for k in ("files", "fingerprint_sha1", "carries_runs")}
    if tree["carries_runs"]:
        return {**out, "ok": False, "reason": "the copy carries a corpus"}
    root = Path(tree["root"])
    out["eight"] = answered
    out["gate"] = commands(gates)
    tmp = Path(tempfile.mkdtemp(prefix="e465_out_"))

    def both(module: str) -> tuple:
        a = run_arm(module, Path.cwd(), tmp / "corpus.json")
        b = run_arm(module, root, tmp / "clone.json")
        return module, a, b

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            for module, a, b in pool.map(both, answered):
                gate_rel = out["gate"].get(module)
                gate_doc = load(RUNS / Path(gate_rel).name) if gate_rel else None
                out["entries"][module] = {
                    "corpus": a, "clone": b,
                    "gate": verdicts(gate_doc),
                    "keys_equal": a["keys"] == b["keys"] and bool(a["keys"]),
                    #: a module that records no claims in either arm writes the same (empty) verdict map both ways,
                    #: which is the same answer; `comparable` below is what says whether a verdict could move at all
                    "same_verdicts": a["claims"] == b["claims"],
                    "comparable": bool(a["claims"]) and bool(b["claims"]),
                    "moved": sorted(k for k in set(a["claims"]) | set(b["claims"])
                                    if a["claims"].get(k) != b["claims"].get(k)),
                }
    finally:
        for _ in range(20):
            try:
                if tmp.is_dir():
                    for p in tmp.iterdir():
                        p.unlink()
                    tmp.rmdir()
            except OSError:
                time.sleep(0.5)
                continue
            break
        e464.cleanup()
    ents = out["entries"]
    if ents and not any(e["corpus"]["keys"] or e["clone"]["keys"] for e in ents.values()):
        #: a harness that runs nothing would report eight FALSIFIERs, which is the one reading this unit must not
        #: produce from a tool fault -- so it refuses instead
        return {**out, "ok": False,
                "reason": "no module wrote an artifact in either arm, so the arms did not run"}
    out["spans"] = {
        "eight": len(answered),
        "with_artifact": sum(1 for e in ents.values() if e["corpus"]["keys"] and e["clone"]["keys"]),
        "with_claims": sum(1 for e in ents.values() if e["corpus"]["claims"] and e["clone"]["claims"]),
        "comparable": sorted(m for m, e in ents.items() if e["comparable"]),
        "keys_equal": sum(1 for e in ents.values() if e["keys_equal"]),
        "unchanged": sorted(m for m, e in ents.items() if e["same_verdicts"]),
        "changed": sorted(m for m, e in ents.items() if not e["same_verdicts"]),
        "unchanged_share": (sum(1 for e in ents.values() if e["same_verdicts"]) / len(ents)) if ents else 0.0,
        "crashed": sorted(m for m, e in ents.items() if e["corpus"]["crashed"] or e["clone"]["crashed"]),
        "timed_out": sorted(m for m, e in ents.items() if e["corpus"]["timeout"] or e["clone"]["timeout"]),
        "gate_compared": sorted(m for m, e in ents.items() if e["gate"]),
        "gate_agree": sorted(m for m, e in ents.items() if e["gate"] and e["gate"] == e["corpus"]["claims"]),
        "files": out["tree"]["files"], "fingerprint": out["tree"]["fingerprint_sha1"],
        "seconds": statistics.fmean([e["corpus"]["seconds"] + e["clone"]["seconds"] for e in ents.values()])
        if ents else 0.0,
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the sweep or the copy is not there"}
                for c in CLAIMS]
    s = r["spans"]
    ents = r["entries"]
    shaped = [m for m, e in ents.items() if e["corpus"]["keys"] and e["clone"]["keys"] and e["keys_equal"]]
    unshaped = sorted(set(ents) - set(shaped))
    j1 = {"id": "RB1",
          "measured": f"{s['with_artifact']} of {s['eight']} modules wrote an artifact in both arms, "
                      f"{s['with_claims']} of them record claims in both, and {s['keys_equal']} pairs have equal key "
                      f"sets, in a copy of {s['files']} files that carries no corpus",
          "verdict": "MET -- both arms are the same module on the same interface, with the corpus as the only "
                     "difference" if (s["with_artifact"] == s["eight"] and s["with_claims"] == s["eight"] and
                                       s["keys_equal"] == s["eight"]) else
                     f"FALSIFIER FIRED -- unshaped {unshaped[:6]}, crashed {s['crashed'][:4]}, "
                     f"past the bound {s['timed_out'][:4]}"}
    share = s["unchanged_share"]
    j2 = {"id": "RB2",
          "measured": f"{len(s['unchanged'])} of {s['eight']} modules write the same claim verdicts with and without "
                      f"the corpus ({100 * share:.0f}%), so they never read it; {len(s['comparable'])} of the eight "
                      f"record a claims block in both arms and could move at all: "
                      f"{[m.split('/')[-1] for m in s['unchanged']]}",
          "verdict": f"MET -- {100 * share:.0f}% of the eight answer the same way with the corpus as without it" if
                     share >= HALF else
                     f"FALSIFIER FIRED -- {100 * share:.0f}%" if share < QUARTER else
                     f"NULL -- {100 * share:.0f}%, between {QUARTER:.0%} and {HALF:.0%}"}
    changed = s["changed"]
    j3 = {"id": "RB3",
          "measured": f"{len(changed)} of {s['eight']} modules move at least one claim verdict when the corpus goes, "
                      f"of {len(s['comparable'])} that record verdicts at all: "
                      f"{ {m.split('/')[-1]: r['entries'][m]['moved'] for m in changed[:6]} }",
          "verdict": f"MET -- {len(changed)} of the eight were answering a question their input could not support" if
                     changed else
                     "FALSIFIER FIRED -- none of the eight changes a verdict, so every one of them never read the "
                     "corpus it names"}
    compared = s["gate_compared"]
    agreed = s["gate_agree"]
    j4 = {"id": "RB4",
          "measured": f"{len(compared)} of the eight have an artifact the gate writes for them and {len(agreed)} of "
                      f"those reproduce it in this unit's corpus arm: "
                      f"{sorted(set(compared) - set(agreed))}",
          "verdict": "MET -- the corpus arm is the reading the gate takes" if compared and len(compared) == len(agreed)
                     else (f"NULL -- none of the eight has a gate artifact to compare with" if not compared else
                           f"FALSIFIER FIRED -- {sorted(set(compared) - set(agreed))}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the eight that answered, run twice ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the sweep or the copy is not there')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    s = r["spans"]
    print("   the answering set is `e464`'s, and each module is run with its own output outside the corpus, once with")
    print("   this repository as the working directory and once inside a copy of it that has no `runs/`")
    print(f"\n   the copy: {s['files']} files, fingerprint {s['fingerprint']}, no corpus")
    print(f"\n   {'module':<48} {'corpus':>22} {'clone':>22} {'same':>5}")
    for m in r["eight"]:
        e = r["entries"][m]
        c = ",".join(f"{k}:{v.split()[0]}" for k, v in sorted(e["corpus"]["claims"].items()))
        b = ",".join(f"{k}:{v.split()[0]}" for k, v in sorted(e["clone"]["claims"].items()))
        print(f"   {m.split('/')[-1]:<48} {c[:22]:>22} {b[:22]:>22} {str(e['same_verdicts']):>5}")
    print("\n== the registered claims, RB1-RB4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e464` ran each of these once and reported that a refusal in the source is not a refusal; this asks")
    print("    which of the eight would have answered the same way with the corpus in place)")
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
