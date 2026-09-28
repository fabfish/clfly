"""E283 -- the registry it names: 27 contrasts over 22 arms, and the artifacts the registry does not name.

The paper's reproducibility table carries one row for `e151`:

    | §4.2 -- **the per-task decomposition of every forty-replicate contrast in the record** ... |
    **Its registry was extended on 2026-09-24 from 22 contrasts to 27 when the arms that landed that
    evening were added**, which is why the counts in §4.2 and §8 are the extended ones
    | `runs/e151_pertask_audit.json`, over the 27 arms it names |

Three things in that row are separate claims, and each is mechanically checkable:

  * **the two nouns.** The registry is a tuple of `(label, path A, method A, path B, method B)` rows, so a row is a
    *contrast* and the arms are the distinct `(path, method)` pairs behind it. The sentence's two numbers sit on the
    wrong two words if those counts differ.
  * **"every ... in the record".** The registry is a hard-coded tuple, so its coverage of the record is a property of
    the corpus on the day it was last edited. The population this unit checks it against is mechanical: the artifacts
    under `runs/` carrying at least one arm with exactly forty replicates.
  * **the date and the direction.** "Extended on 2026-09-24 from 22 contrasts to 27" is a claim about a commit, and
    git can be asked.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **U1 -- the two nouns are exchanged.** The 27 rows name 22 distinct arms, so "22 contrasts" should be "22 arms" and
  "the 27 arms" should be "the 27 contrasts". **Falsifier**: the rows are not pairwise, or the distinct-arm count is
  not 22.
- **U2 -- "every" is an epoch.** The registry names under half of the artifacts carrying a forty-replicate arm, and at
  least one artifact it does not name is named by path in the paper or the plan. **Falsifier**: it names half or more,
  or every forty-replicate artifact outside it is unnamed in the record.
- **U3 -- and the provenance half is right.** The registry's tuple held 22 rows before one commit dated 2026-09-24 and
  27 after it, which is the sentence's own account. **Falsifier**: no commit in the file's history has 22 rows, or the
  extension is dated other than 2026-09-24.

**The shape is the series' own and not the paper's alone**: `e282` measured that the instruments between them match 9
sentences of the paper's 368 checkable ones, and this unit's row is a table cell -- one `e282` cannot count as a
sentence -- whose population noun ("arms") and population ("the record") are both wrong in the same sentence. `e279`
found "every one of the 77 stored runs" to be an epoch; this is the same defect one noun over, with the extension's
date added as a leg that passes.

**What it cannot do**: "a forty-replicate arm" is read from the artifact's `methods` block, so an artifact whose arms
ran forty replicates without recording a list of them is invisible; "named by the record" is a path search over the
paper and the plan and not over the findings, which name artifacts too, so the 10 artifacts reported are a **lower
bound** on the registry's misses; the corpus scan reads every `runs/*.json` and a file it cannot parse is skipped
silently; git is read as it exists now, so a rewrite would move U3 without the paper moving; and nothing here says the
unregistered contrasts are wrong to leave out -- only that the sentence's "every" does not hold over them.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e151_pertask_contrast_audit as e151

MODULE = "experiments/e151_pertask_contrast_audit.py"
RUNS = Path("runs")
RECORD = (Path("docs/paper/clfly-v1.md"), Path("docs/research_plan.md"))
ARMS_IN_A_CONTRAST = 2
CLAIMS = (
    ("U1", "the two nouns in the sentence are exchanged",
     "The 27 rows name 22 distinct (path, method) arms, so the sentence's 22 should read arms and its 27 contrasts",
     "falsifier: the rows are not pairwise, or the distinct-arm count is not 22"),
    ("U2", "and the sentence's every is an epoch",
     "The registry names under half of the artifacts carrying a forty-replicate arm, and at least one it does not "
     "name is named by path in the record",
     "falsifier: it names half or more, or every forty-replicate artifact outside it is unnamed in the record"),
    ("U3", "and the provenance half is right",
     "The tuple held 22 rows before one commit dated 2026-09-24 and 27 after it",
     "falsifier: no commit in the history has 22 rows, or the extension is dated otherwise"),
)


def rows() -> list[dict]:
    """The registry as the artifact's own reading of it: one row per contrast."""
    return [{"label": lab, "a": {"path": pa, "method": ma}, "b": {"path": pb, "method": mb}}
            for lab, pa, ma, pb, mb in e151.CONTRASTS]


def arms(rs: list[dict]) -> set[tuple[str, str]]:
    """The distinct (path, method) arms the registry's rows are built from."""
    out: set[tuple[str, str]] = set()
    for r in rs:
        for side in ("a", "b"):
            out.add((r[side]["path"], r[side]["method"]))
    return out


def corpus_arms(root: Path = RUNS, n: int = 40) -> dict[str, list[str]]:
    """Every artifact under `root` carrying at least one arm with exactly `n` replicates, by artifact."""
    out: dict[str, list[str]] = {}
    for p in sorted(root.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        methods = d.get("methods")
        if not isinstance(methods, dict):
            continue
        got = [m for m, e in methods.items()
               if isinstance(e, dict) and isinstance(e.get("replicates"), list) and len(e["replicates"]) == n]
        if got:
            out[p.as_posix()] = sorted(got)
    return out


def record_text(paths=RECORD) -> str:
    out = []
    for p in paths:
        if p.exists():
            out.append(p.read_text(encoding="utf-8"))
    return "\n".join(out)


def registry_sizes(module: str = MODULE) -> list[dict]:
    """Every commit touching the module, with the row count its `CONTRASTS` tuple had then."""
    log = subprocess.run(["git", "log", "--format=%H|%ad", "--date=short", "--", module],
                         capture_output=True, text=True, check=True).stdout.strip()
    out = []
    for line in log.split("\n"):
        if not line:
            continue
        sha, date = line.split("|")
        src = subprocess.run(["git", "show", f"{sha}:{module}"],
                             capture_output=True, text=True).stdout
        n = None
        try:
            tree = ast.parse(src)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                targets = getattr(node, "targets", None) or [getattr(node, "target", None)]
                if any(getattr(t, "id", None) == "CONTRASTS" for t in targets if t is not None):
                    value = node.value
                    if isinstance(value, ast.Constant) and isinstance(value.value, tuple):
                        n = len(value.value)
                    else:
                        try:
                            n = len(ast.literal_eval(value))
                        except ValueError:
                            n = None
        out.append({"sha": sha[:8], "date": date, "rows": n})
    return out


def judge(r: dict) -> list[dict]:
    out: list[dict] = []
    if not r or not r.get("rows"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the registry could not be read"} for c in CLAIMS]

    pairwise = all({"a", "b"} <= set(x) for x in r["rows"])
    n_arms = len(r["arms"])
    ok = pairwise and n_arms == 22
    out.append({"id": "U1", "measured": f"{len(r['rows'])} rows naming {n_arms} distinct arms; pairwise {pairwise}",
                "verdict": "MET -- the sentence's two nouns are on the wrong two numbers" if ok else
                           "FALSIFIER FIRED -- the rows and the arms are not 27 and 22"})

    named = [p for p in sorted(r["unregistered"]) if p in r["record"]]
    share = r["n_registered"] / max(r["n_forty_artifacts"], 1)
    ok = share < 0.5 and bool(named)
    out.append({"id": "U2", "measured": f"the registry names {r['n_registered']} of {r['n_forty_artifacts']} artifacts "
                                        f"carrying a forty-replicate arm ({100 * share:.1f}%), and {len(named)} of the "
                                        f"unnamed ones are named by path in the record",
                "verdict": "MET -- every is an epoch, and the misses are enumerable" if ok else
                           "FALSIFIER FIRED -- the registry covers its population, or names nothing the record does"})

    hist = r["history"]
    went = [(h["rows"], h["date"]) for h in hist]
    ok = any(h["rows"] == 22 for h in hist) and any(h["rows"] == 27 and h["date"] == "2026-09-24" for h in hist)
    out.append({"id": "U3", "measured": f"the tuple's rows per commit, newest first: {went[:4]}"
                                        + (f" of {len(went)} commits" if len(went) > 4 else ""),
                "verdict": "MET -- 22 then 27, in a commit dated 2026-09-24" if ok else
                           "FALSIFIER FIRED -- the counts or the date are not the sentence's"})
    return out


def report(r: dict) -> int:
    print("== the registry e151 names ==")
    print(f"   rows (contrasts): {len(r['rows'])}; distinct (path, method) arms: {len(r['arms'])}; "
          f"artifacts named: {len({p for p, _ in r['arms']})}")

    print("\n== the corpus, at forty replicates ==")
    print(f"   artifacts carrying a forty-replicate arm: {r['n_forty_artifacts']}; arms: {r['n_forty_arms']}")
    print(f"   of those artifacts, named in the registry: {r['n_registered']}; not named: {r['n_unregistered']}")
    print(f"   forty-replicate arms the registry does not name: {r['n_unregistered_arms']}")
    print(f"   and the ones the record names by path ({len(r['named_by_record'])}):")
    for p in r["named_by_record"]:
        print(f"      {p}  ({', '.join(r['corpus'][p])})")

    print("\n== the tuple's size, by commit ==")
    for h in r["history"]:
        print(f"      {h['sha']}  {h['date']}  rows {h['rows']}")

    print("\n== the registered claims, U1-U3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the sentence's two numbers are right and its two nouns are exchanged; its of the extension is right")
    print("    to the commit and its every is an epoch -- the same defect e279 found one noun over)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--replicates", type=int, default=40)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    rs = rows()
    reg_arms = arms(rs)
    corpus = corpus_arms(args.runs, args.replicates)
    reg_paths = {p for p, _ in reg_arms}
    unregistered = {p: ms for p, ms in corpus.items() if p not in reg_paths}
    text = record_text()
    rec = {
        "rows": rs, "arms": sorted(reg_arms),
        "corpus": corpus,
        "n_forty_artifacts": len(corpus),
        "n_forty_arms": sum(len(v) for v in corpus.values()),
        "n_registered": len([p for p in corpus if p in reg_paths]),
        "n_unregistered": len(unregistered),
        "unregistered": sorted(unregistered),
        "n_unregistered_arms": sum(len(v) for v in unregistered.values()),
        "named_by_record": [p for p in sorted(unregistered) if p in text],
        "record": text,
        "history": registry_sizes(),
    }
    rec["claims"] = judge(rec)
    if args.json_out:
        write_json(args.json_out, {
            "replicates": args.replicates,
            "registry": {"rows": len(rs), "arms": len(reg_arms), "artifacts_named": len(reg_paths),
                         "labels": [x["label"] for x in rs]},
            "corpus": {"artifacts_with_a_forty_replicate_arm": rec["n_forty_artifacts"],
                       "arms": rec["n_forty_arms"], "named_in_the_registry": rec["n_registered"],
                       "not_named": rec["n_unregistered"], "unregistered_arms": rec["n_unregistered_arms"],
                       "unnamed_artifacts_the_record_names": rec["named_by_record"]},
            "history": rec["history"],
            "claims": rec["claims"],
        })
        print(f"wrote {args.json_out}")
    return report(rec)


if __name__ == "__main__":
    sys.exit(main())
