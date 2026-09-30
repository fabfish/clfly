"""E303 -- the benchmark's metrics, re-read with the code arm counting definitions rather than mentions.

`e302` read the FlyCL v0 block's five metrics and found four implemented and one (`backward transfer`) implemented
nowhere. **Its code arm counted a spelling anywhere in a module's text, and a docstring is text.** Re-reading the
five with prose removed -- Python's own tokenizer, dropping every `STRING` and `COMMENT` token -- moves a verdict:

    metric                              e302 (any mention)    this unit (definition only)
    average accuracy                    implemented           implemented      final_accuracy
    decomposed forgetting               implemented           **nowhere**      the only mention is a docstring
    backward transfer                   nowhere               nowhere
    per-task observability spectrum     implemented           **nowhere**      three mentions, all prose
    pairwise task principal angles      implemented           implemented      def principal_angles

And the one case is worth naming rather than counting. `decompose_forgetting` occurs **once** in the repository, in
`clfly/lgcl/model.py`'s `summarize`:

    NOTE: this metric rewards shrinkage bias ... Use
    :func:`clfly.lgcl.metrics.decompose_forgetting` when that matters.

`clfly/lgcl/metrics.py` **does not exist**. The repository's own comment defers to a module nobody wrote, for exactly
the metric the benchmark block names -- and in the same sentence that says the conventional forgetting *"rewards
shrinkage bias"*, which is the block's reason for naming the decomposed one in the first place.

Three claims, registered before the readings above were taken:

- **R1 -- at least one metric's only code evidence is prose.** Its spelled form occurs in a module and not in the
  module's code. **Falsifier**: none.
- **R2 -- and the repaired arm leaves at least two metrics implemented nowhere.** **Falsifier**: fewer than two.
- **R3 -- and one of the prose-only mentions names a module that is not on disk.** **Falsifier**: the module it
  names exists.

**What it cannot do.** *Counting tokens is not reading code*: a metric implemented through a computed name, a
data-driven registry or a `getattr` reads as absent here, and a comment on the line that defines something is not
evidence either way. *`tokenize` can fail on a file*: a module whose source does not tokenise falls back to its raw
text and is reported rather than silently counted, because a fallback that reads prose as code is the defect this
unit exists to correct. *A docstring is not nothing*: a module documented as computing a metric and not doing so is a
different failure from a module that never mentions it, and R3 is the arm that sees the difference, over one
exhibit. *And this unit re-reads `e302`'s five metrics and not the block itself*: the phrases, the spelling table and
the carried arm are `e302`'s, so a change to the block moves both.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tokenize
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e302_the_benchmark_metrics as e302

PLAN = Path("docs/research_plan.md")
RUNS = Path("runs")
CODE_DIRS = (Path("clfly"), Path("experiments"))
#: A module written as a dotted path in prose -- `clfly.lgcl.metrics.decompose_forgetting` is three levels of
#: package and one attribute, so the longest prefix that resolves to a file is the one this unit tests for.
DOTTED = re.compile(r"\bclfly(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+")
STRIP = (tokenize.STRING, tokenize.COMMENT)
CLAIMS = (
    ("R1", "at least one metric's only code evidence is prose",
     "A spelled form of a metric occurs in a module and not in that module's code",
     "falsifier: none does"),
    ("R2", "and the repaired arm leaves at least two metrics implemented nowhere",
     "Two or more of the five metrics occur only in prose or not at all",
     "falsifier: fewer than two"),
    ("R3", "and one of the prose-only mentions names a module that is not on disk",
     "A prose-only mention writes a dotted `clfly` path whose module -- the path minus its last component, which is "
     "the attribute -- is not a file",
     "falsifier: the module it names exists"),
)
#: The auditors are found rather than listed -- `e302.is_auditor` and this unit's own name -- because the exclusion
#: is transitive: every unit that re-reads a name list carries that list's names by construction, so a hand-written
#: tuple of two files would be stale the moment a third re-reader appeared.


def strip_prose(src: str) -> tuple[str, bool]:
    """The source with every string and comment token removed, and whether the tokenizer could read it.

    Docstrings are `STRING` tokens, so this removes them along with comments and every other literal. A file that
    does not tokenise is returned unchanged and **flagged**, because falling back to raw text silently turns prose
    back into evidence -- the defect this unit corrects.
    """
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return src, False
    kept = [t.string for t in toks if t.type not in STRIP and t.type not in (tokenize.NEWLINE, tokenize.NL)]
    return "\n".join(kept), True


def modules(dirs=CODE_DIRS) -> list[Path]:
    """Every module that is not an auditor -- neither `e302` nor this unit, nor a reader of either's name list."""
    me = Path(__file__).stem
    return [p for d in dirs for p in sorted(Path(d).rglob("*.py"))
            if not e302.is_auditor(p) and me not in p.read_text(encoding="utf-8", errors="replace")]


def module_path(dotted: str) -> str:
    """The file a dotted reference names: everything but the last component, which is the attribute.

    `clfly.lgcl.metrics.decompose_forgetting` names the attribute `decompose_forgetting` in the module
    `clfly.lgcl.metrics`, and it is that module's existence the reference is a promise about. Resolving the longest
    prefix that happens to be a file would answer `clfly/lgcl/__init__.py` and bless a reference to a module that is
    not there, which is the defect this unit is correcting one level down.
    """
    parts = dotted.split(".")
    if len(parts) < 2:
        return ""
    stem = "/".join(parts[:-1])
    for cand in (f"{stem}.py", f"{stem}/__init__.py"):
        if Path(cand).is_file():
            return cand
    return ""


def readings(root: Path = RUNS, plan: Path = PLAN, dirs=CODE_DIRS) -> dict:
    """Every declared spelling counted twice: once in the module's text and once in its code."""
    phrases = e302.metric_phrases(plan.read_text(encoding="utf-8"))
    sources, unreadable = [], []
    for p in modules(dirs):
        text = p.read_text(encoding="utf-8", errors="replace")
        code, ok = strip_prose(text)
        if not ok:
            unreadable.append(p.as_posix())
        sources.append((p, text, code))

    rows, dangling = [], []
    for ph in phrases:
        spellings = e302.SYNONYMS.get(ph, (ph.replace(" ", "_"),))
        for s in spellings:
            raw = sum(t.count(s) for _, t, _ in sources)
            clean = sum(c.count(s) for _, _, c in sources)
            if not raw:
                continue
            rows.append({"metric": ph, "spelling": s, "in_text": raw, "in_code": clean})
            if clean:
                continue
            for p, text, _ in sources:
                for m in DOTTED.findall(text):
                    if s in m:
                        dangling.append({"module": p.as_posix(), "spelling": s, "writes": m,
                                         "names": f"{'/'.join(m.split('.')[:-1])}.py",
                                         "resolves_to": module_path(m)})
    implemented = sorted({x["metric"] for x in rows if x["in_code"]})
    return {"spellings": rows, "prose_only": [x for x in rows if not x["in_code"]],
            "implemented": implemented, "unreadable": unreadable, "dangling": dangling,
            "n_metrics": len(phrases), "metrics": phrases}


def judge(r: dict) -> list[dict]:
    rows = r.get("prose_only") or []
    if not r.get("metrics"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the block names no metric"} for c in CLAIMS]

    named = ", ".join(f"`{x['spelling']}` in {x['metric']}" for x in rows)
    out = [{"id": "R1", "measured": f"{len(rows)} of {len(r['spellings'])} spellings occur in the repository's text "
                                     f"and in none of its code: {named or 'none'}",
            "verdict": "MET -- the arm that counted mentions was reading documentation" if rows else
                       "FALSIFIER FIRED -- every spelled form occurs in code"}]

    absent = [ph for ph in r["metrics"] if ph not in set(r["implemented"])]
    detail = ", ".join(f"{ph} <- {[x['spelling'] for x in r['spellings'] if x['metric'] == ph and x['in_code']]}"
                       for ph in r["implemented"])
    out.append({"id": "R2", "measured": f"{len(r['implemented'])} of {r['n_metrics']} metrics have a spelling in "
                                        f"code ({detail}); implemented nowhere: {absent or 'none'}",
                "verdict": "MET -- the block's metric list is prose for as much as it is code"
                if len(absent) >= 2 else f"FALSIFIER FIRED -- {len(absent)} are absent"})

    broken = [d for d in r["dangling"] if not d["resolves_to"]]
    written = "; ".join(f"{d['spelling']} in {d['module']} writes `{d['writes']}`" for d in broken[:4])
    out.append({"id": "R3", "measured": f"{len(r['dangling'])} dotted path(s) written beside a prose-only spelling, "
                                        f"{len(broken)} of which name a module that is not a file ({written or 'none'})",
                "verdict": "MET -- a docstring defers to a module nobody wrote" if broken else
                           "FALSIFIER FIRED -- every named module is on disk"})
    return out


def report(r: dict) -> int:
    print("== every declared spelling, counted in the text and in the code ==")
    for x in r["spellings"]:
        mark = "" if x["in_code"] else "   <- prose only"
        print(f"   {x['metric'][:34]:34} {x['spelling']:24} text {x['in_text']:4}  code {x['in_code']:4}{mark}")
    if r["unreadable"]:
        print(f"   (returned to raw text, tokenizer refused: {r['unreadable']})")

    print("\n== and the modules the prose defers to ==")
    for d in r["dangling"]:
        where = d["resolves_to"] or "**not a file on disk**"
        print(f"   {d['module']}: `{d['writes']}` names {d['names']} -> {where}")

    print("\n== the registered claims, R1-R3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the block names a decomposed forgetting because the conventional metric can be gamed; the")
    print("    repository documents that metric in one comment and defers to a module that does not exist)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = readings(args.runs, args.plan)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
