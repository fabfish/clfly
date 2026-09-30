"""E302 -- the benchmark's five metrics and its fixed orders, checked against the code and the corpus.

The FlyCL v0 block in the plan is a **contract with the code**, and `e185` reads two of its lists: the tasks it says
are implemented and the baselines it offers. **Its metrics paragraph and its comparability promise have never been
read against anything**, and they are the two sentences a new benchmark's users act on.

The block names five metrics:

    average accuracy; decomposed forgetting -- irreducible drift term separated from estimation degradation, as
    LGCL section 5 recommends, because the conventional forgetting metric rewards shrinkage and can be gamed;
    backward transfer; the per-task observability spectrum; and pairwise task principal angles.

and promises "fixed task orders and seeds, so numbers are comparable across methods".

Four claims, registered before the readings below were taken:

- **M1 -- the metric list is part-implemented.** At least one of the five is implemented nowhere under any of the
  spellings this instrument declares. **Falsifier**: all five are.
- **M2 -- and it is almost entirely unrecorded.** At most two of the five have a field in `runs/` under any declared
  spelling. **Falsifier**: three or more.
- **M3 -- and the forgetting metric the block prescribes is not the one the corpus carries.** The block rejects the
  conventional metric; the field the artifacts carry is the conventional one, and the prescribed one is carried
  nowhere. **Falsifier**: an artifact carrying the prescribed one.
- **M4 -- and the orders are comparable because only one order was ever used.** Every artifact that records a task
  list records its suite's own naming order, and no permutation of any suite appears. **Falsifier**: two artifacts of
  one suite with different orders.

**The instrument is lexical and the spellings are its definition.** A metric counts as **implemented** when a
declared spelling appears in a module under `clfly/` or `experiments/`, and as **carried** when a declared spelling
appears as a key anywhere in a `runs/*.json` payload. `e185`'s finding is the reason the arm is spelled out: a check
that matches a word rather than evidence blessed a joint-training baseline that exists nowhere. The same defect is
available here in both directions -- a metric implemented under a name none of these lists anticipates reads as
absent, and a word that happens to occur in prose reads as present -- so the report prints the spellings it used.

**What it cannot do.** *The order claim is about what the artifacts record*: a runner that shuffled tasks internally
and wrote the suite's canonical list would pass M4, and nothing in the corpus distinguishes that from a fixed order,
so M4 says the order is not a variable the corpus can be asked about and not that the runner iterates in the order it
writes. *Only artifacts carrying a `tasks` list of named objects are read*, so the analytic artifacts that carry no
tasks are outside the claim. *And a metric's absence is an absence under these spellings*: the decomposed forgetting
is implemented in `clfly/lgcl/`, so M3 is about what the corpus **stores** and not about what the repository can
compute.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json
from experiments import e185_benchmark_spec_audit as e185

PLAN = Path("docs/research_plan.md")
RUNS = Path("runs")
#: Where a metric has to be findable to count as implemented, as in `e185`.
CODE_DIRS = (Path("clfly"), Path("experiments"))
#: This unit's own file, which the code arm must not read: its spelling table and its prose contain every name it
#: looks for, so counting itself would make `backward transfer` look implemented -- the defect `e185`'s first version
#: recorded, where a check that matches a word rather than evidence blessed a baseline that exists nowhere.
SELF = Path(__file__).name
#: And this unit's own artifact, for the same reason: it writes the spelling table out, so every declared name
#: occurs in it as a key and the carried arm would read its own output as the corpus carrying the metric.
SELF_ARTIFACT = f"{Path(__file__).stem}.json"


def is_auditor(path) -> bool:
    """Whether a module is this unit or reads its spelling table, and so carries every name by construction.

    The exclusion has to be transitive: `e303` re-reads this unit's five metrics, so its docstring contains
    `backward transfer`, and an arm that only excluded *this* file would take that mention as evidence and lose the
    one metric the earlier reading found missing. A module that reads the table is not evidence that a name in the
    table is implemented.
    """
    p = Path(path)
    if p.name == SELF:
        return True
    return Path(__file__).stem in p.read_text(encoding="utf-8", errors="replace")
#: The block introduces its metric list with this token, and the list runs to the paragraph's end.
METRICS_MARK = "Metrics:"
#: The block's phrase, the spellings this instrument declares for it, and the corpus's own spelling of the field.
#:
#: This table is the instrument's **definition** and not a discovery: a metric the repository computes under a name
#: none of these lists anticipates reads as absent, which is the caveat `e185`'s first version earned.
SYNONYMS = {
    "average accuracy": ("average_accuracy", "final_accuracy"),
    "decomposed forgetting": ("decompose_forgetting", "decomposed_forgetting", "drift_term", "mean_forgetting"),
    "backward transfer": ("backward_transfer", "bwt", "backward transfer"),
    "per-task observability spectrum": ("observability", "observability_spectrum"),
    "pairwise task principal angles": ("principal_angle", "principal_angles"),
}
#: The spelling whose presence in an artifact is the corpus **carrying** the metric, and the one it carries instead.
CARRIED = {"average accuracy": "final_accuracy",
           "decomposed forgetting": "mean_forgetting"}
#: The prescribed-forgetting spelling M3 turns on, and the conventional one the block rejects.
PRESCRIBED = "decompose_forgetting"
CONVENTIONAL = "mean_forgetting"
CLAIMS = (
    ("M1", "the metric list is part-implemented",
     "At least one of the five metrics the block names is implemented nowhere",
     "falsifier: all five are"),
    ("M2", "and it is almost entirely unrecorded",
     "At most two of the five have a field in the corpus",
     "falsifier: three or more"),
    ("M3", "and the forgetting metric the block prescribes is not the one the corpus carries",
     "The corpus carries the conventional forgetting metric the block rejects, and carries the prescribed one nowhere",
     "falsifier: an artifact carrying the prescribed one"),
    ("M4", "and the orders are comparable because only one order was ever used",
     "Every suite is recorded in one order",
     "falsifier: two artifacts of one suite with different orders"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def metric_phrases(text: str) -> list[str]:
    """The block's metric list, split into phrases, in the block's own spelling.

    The paragraph is one sentence separated by semicolons and the first item is introduced by the mark, so the
    phrases are read positionally rather than by any knowledge of what a metric is.
    """
    block = e185.benchmark_block(text)
    i = block.index(METRICS_MARK)
    para = block[i + len(METRICS_MARK):].split("\n\n", 1)[0].replace("\n", " ")
    out = []
    for part in para.split(";"):
        part = re.sub(r"[*`]", "", part)
        # each item's name is the phrase before its first comma or em dash; the rest is the reason it is named
        name = re.split(r",|\u2014| -- ", part, maxsplit=1)[0]
        name = name.strip().strip(".").lower()
        # a list item can open with an article or a conjunction, which is not part of the metric's name
        name = re.sub(r"^(?:and\s+|the\s+)", "", name)
        if name:
            out.append(name)
    return out


def code_evidence(spellings: tuple[str, ...], dirs=CODE_DIRS) -> dict[str, int]:
    """How often each spelling occurs in a module -- the arm that says a metric is implemented.

    This unit's own file is excluded, because a spelling table contains every name it looks for.
    """
    src = ""
    for d in dirs:
        for p in Path(d).rglob("*.py"):
            if is_auditor(p):
                continue
            src += p.read_text(encoding="utf-8", errors="replace") + "\n"
    return {s: src.count(s) for s in spellings}


def artifact_keys(root: Path = RUNS, collapse: bool = True) -> Counter:
    """Every key anywhere in the corpus, with how many payloads carry it.

    Second copies are dropped when `collapse` is set, as everywhere else in this repository since `e301`: a field
    the corpus carries is carried once, however many times its experiment was executed.
    """
    counts: Counter = Counter()
    skip = corpus.repeat_paths(root) if collapse else set()
    skip = set(skip) | {SELF_ARTIFACT}
    for p in sorted(Path(root).glob("*.json")):
        if p.name in skip:
            continue
        d = load(p)
        if d is None:
            continue
        seen: set[str] = set()
        stack = [d]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k, v in o.items():
                    seen.add(k)
                    stack.append(v)
            elif isinstance(o, list):
                stack.extend(o[:3])
        for k in seen:
            counts[k] += 1
    return counts


def orders(root: Path = RUNS, collapse: bool = True) -> list[dict]:
    """Every artifact that records a named task list, with the order it records.

    Second copies are dropped when `collapse` is set (`e301`), so a suite's order is counted once however many
    times its experiment was executed.
    """
    out = []
    skip = set(corpus.repeat_paths(root)) if collapse else set()
    for p in sorted(Path(root).glob("*.json")):
        if p.name in skip:
            continue
        d = load(p)
        if d is None:
            continue
        t = d.get("tasks")
        if not (isinstance(t, list) and t and isinstance(t[0], dict) and "name" in t[0]):
            continue
        names = tuple(str(x["name"]) for x in t)
        out.append({"artifact": p.name, "order": list(names),
                    "suite": tuple(sorted(names)),
                    "seed0": (d.get("config") or {}).get("seed0")})
    return out


def audits(root: Path = RUNS, plan: Path = PLAN) -> dict:
    phrases = metric_phrases(plan.read_text(encoding="utf-8"))
    counts = artifact_keys(root)
    rows = []
    for ph in phrases:
        spell = SYNONYMS.get(ph, (ph.replace(" ", "_"),))
        code = code_evidence(spell)
        carried = sorted((s, counts[s]) for s in spell if counts[s])
        rows.append({"metric": ph, "declared": list(spell), "code": code,
                     "implemented": any(code.values()), "carried_by": carried,
                     "carried_total": sum(n for _, n in carried)})
    rows = [r for r in rows if r["metric"]]
    os_ = orders(root)
    by_suite: dict[tuple, set] = defaultdict(set)
    for o in os_:
        by_suite[o["suite"]].add(tuple(o["order"]))
    return {"metrics": rows, "n_metrics": len(rows),
            "orders": os_, "n_orders": len(os_),
            "suites": {",".join(k): sorted(",".join(v) for v in vs) for k, vs in by_suite.items()},
            "seeds": Counter(o["seed0"] for o in os_),
            "prescribed": counts[PRESCRIBED], "conventional": counts[CONVENTIONAL],
            "declared": SYNONYMS, "plan": plan.as_posix()}


def judge(r: dict) -> list[dict]:
    rows = r.get("metrics") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the block names no metric"} for c in CLAIMS]

    absent = [x["metric"] for x in rows if not x["implemented"]]
    out = [{"id": "M1", "measured": f"{len(rows) - len(absent)} of {len(rows)} metrics occur in a module; "
                                     f"implemented nowhere: {absent or 'none'}",
            "verdict": "MET -- the list names something the repository does not implement" if absent else
                       "FALSIFIER FIRED -- every named metric is implemented"}]

    carried = [x for x in rows if x["carried_by"]]
    names = ", ".join(f"{x['metric']} -> {[k for k in x['carried_by']]}" for x in carried) or "none"
    out.append({"id": "M2", "measured": f"{len(carried)} of {len(rows)} metrics have a field in the corpus ({names})",
                "verdict": "MET -- the block's metrics are computed and not recorded" if len(carried) <= 2 else
                           f"FALSIFIER FIRED -- {len(carried)} are carried"})

    out.append({"id": "M3", "measured": f"the prescribed spelling `{PRESCRIBED}` is a key in {r['prescribed']} "
                                        f"payloads and `{CONVENTIONAL}`, which the block rejects, in "
                                        f"{r['conventional']}",
                "verdict": "MET -- the corpus stores the metric the block says it avoids"
                if not r["prescribed"] and r["conventional"] else
                "FALSIFIER FIRED -- the prescribed metric is carried, or nothing carries the conventional one"})

    split = {k: v for k, v in r["suites"].items() if len(v) > 1}
    out.append({"id": "M4", "measured": f"{r['n_orders']} artifacts record a named task list over "
                                        f"{len(r['suites'])} suites, and {len(split)} suite(s) record more than one "
                                        f"order; seeds recorded: {dict(r['seeds'])}",
                "verdict": "MET -- one order per suite, so the order is not a variable the corpus varies"
                if not split else f"FALSIFIER FIRED -- {split}"})
    return out


def report(r: dict) -> int:
    print("== the benchmark block's five metrics ==")
    print(f"   {'metric':34} {'implemented':>12} {'carried by':>26}  declared spellings")
    for x in r["metrics"]:
        code = ", ".join(f"{k}x{v}" for k, v in x["code"].items() if v) or "nothing"
        car = ", ".join(f"{k}x{v}" for k, v in x["carried_by"]) or "nothing"
        print(f"   {x['metric'][:34]:34} {code[:12]:>12} {car[:26]:>26}  {list(x['declared'])}")

    print("\n== and the orders the corpus records ==")
    for suite, got in sorted(r["suites"].items()):
        print(f"   {len(got)} order(s) over the suite {suite}:  " + "  |  ".join(got))

    print("\n== the registered claims, M1-M4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the block's task list and baseline list are checked by `e185`; its metric list is nearly all")
    print("    implemented and almost none of it is recorded, and its comparability promise rests on one order)")
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

    r = audits(args.runs, args.plan)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
