"""E310 -- the position effect: where a task sits in the sequence predicts how well it is learned.

`e302` read the FlyCL v0 block's promise of **"fixed task orders and seeds, so numbers are comparable across
methods"** and registered M4: every artifact that records a named task list records its suite's own naming order, and
no permutation of any suite has ever been run -- so the promise holds **trivially**, because the order is a variable
with one value. What that could not say is whether the order *would* move the numbers.

This unit measures it from the retention matrices the corpus already stores. For every arm that records a
three-task suite, the diagonal of `R` is the level each task reached when it was learned, so the task's **position in
the sequence** can be read against that level with nothing new run:

    position 0 (learned first)   0.9605
    position 1 (learned second)  0.9168
    position 2 (learned third)   0.9345        over 5581 arm-replicates

Four claims, registered before the reading below was taken:

- **W1 -- the position predicts the level.** The three positions are ordered first > last > middle, with the first
  above the middle by at least 0.02. **Falsifier**: a different order, or a gap below 0.02.
- **W2 -- and it is a within-arm effect.** Paired over the arm-replicates, the first position beats the middle in at
  least 60% of them. **Falsifier**: fewer than 60%.
- **W3 -- and it is a within-configuration effect.** Among the artifacts with at least ten three-task arms, the first
  position beats the middle in at least four fifths. **Falsifier**: fewer than four fifths.
- **W4 -- and it is not one suite's task identities.** The ordering first > last > middle holds in **both** families:
  the overlap suites, whose three tasks are drawn per artifact, and the assembly suite, whose three modalities are
  fixed for every run. **Falsifier**: the ordering is absent in one of them.

**What it means for the benchmark.** The order promise is **not vacuous**: the position moves the level a task
reaches by more than four points of accuracy on average, so a permuted order would move the numbers a methods table
reports. `e302`'s M4 stands -- the corpus has never varied the order -- and this says what varying it would cost,
which is the measurement a benchmark needs before it decides the order is fixed on purpose.

**What it cannot do.** *The diagonal is measured right after the task was learned*, so a task that was hard at the
time and recovered later is scored by its position and not by its end state. *The two families are not a controlled
comparison*: their configurations differ in everything, so W4 is an argument that the ordering survives a change of
suite and not that the families have the same effect size. *`odour_identity`, `heading` and `odour_input` are three
different modalities in one fixed order*, so the assembly family cannot separate "first" from "`odour_identity`" on
its own, which is why W4 needs both families and not either. *And the arms are not independent*: the same
configuration recurs, so the counts are counts of entries and carry no interval.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e304_the_decomposition_the_block_asked_for as e304

RUNS = Path("runs")
#: The gap W1 asks for between the first and middle positions, and the shares W2 and W3 ask for.
GAP = 0.02
MAJORITY = 0.60
MOST = 0.80
#: How many arms an artifact needs before W3 counts it.
POWERED = 10
CLAIMS = (
    ("W1", "the position predicts the level",
     "The three positions are ordered first > last > middle, the first above the middle by at least 0.02",
     "falsifier: a different order, or a gap below 0.02"),
    ("W2", "and it is a within-arm effect",
     "Paired over the arm-replicates, the first position beats the middle in at least 60%",
     "falsifier: fewer than 60%"),
    ("W3", "and it is a within-configuration effect",
     "Among the artifacts with ten or more three-task arms, the first beats the middle in at least four fifths",
     "falsifier: fewer than four fifths"),
    ("W4", "and it is not one suite's task identities",
     "The ordering first > last > middle holds in both the overlap suites and the assembly suite",
     "falsifier: absent in one of them"),
)


def task_names(root: Path = RUNS) -> dict:
    """Each artifact's recorded task names, so a suite family can be told from the names it writes."""
    out = {}
    for p in sorted(Path(root).glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        t = d.get("tasks")
        if isinstance(t, list) and t and isinstance(t[0], dict) and "name" in t[0]:
            out[p.name] = [str(x["name"]) for x in t]
    return out


def family(names: list[str]) -> str:
    """The overlap suites name their tasks `ov*.t*`; the assembly suite names three modalities."""
    return "overlap" if names and names[0].startswith("ov") else "assembly"


def reading(root: Path = RUNS) -> dict:
    names = task_names(root)
    rows, _ = e304.replicates(root)
    three = [r for r in rows if r["n_tasks"] == 3 and r["artifact"] in names]
    positions = {j: [r["reached"][j] for r in three] for j in range(3)}
    paired = [(r["reached"][0], r["reached"][1], r["reached"][2]) for r in three]
    n = len(paired)
    by_family: dict[str, list] = {}
    for r in three:
        by_family.setdefault(family(names[r["artifact"]]), []).append(r["reached"])
    families = {}
    for k, got in sorted(by_family.items()):
        m = len(got)
        families[k] = {"arms": m, "means": [statistics.fmean(x[j] for x in got) for j in range(3)],
                       "first_above_middle": sum(1 for x in got if x[0] > x[1]) / m,
                       "order": [statistics.fmean(x[j] for x in got) for j in range(3)]}
    per_artifact = {}
    for r in three:
        per_artifact.setdefault(r["artifact"], []).append(r["reached"])
    powered = [v for v in per_artifact.values() if len(v) >= POWERED]
    return {"arms": n, "means": [statistics.fmean(positions[j]) for j in range(3)],
            "first_above_middle": sum(1 for f, m, l in paired if f > m) / n if n else None,
            "first_above_last": sum(1 for f, m, l in paired if f > l) / n if n else None,
            "last_above_middle": sum(1 for f, m, l in paired if l > m) / n if n else None,
            "artifacts_powered": len(powered),
            "powered_first_above_middle": sum(1 for v in powered if statistics.fmean(x[0] for x in v)
                                              > statistics.fmean(x[1] for x in v)),
            "families": families, "suites": {k: len(v) for k, v in sorted(per_artifact.items())}}


def aligned(means: list[float]) -> bool:
    """Whether three position means are ordered first > last > middle."""
    return means[0] > means[2] > means[1]


def judge(r: dict) -> list[dict]:
    if not r.get("arms"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm records a three-task suite"}
                for c in CLAIMS]

    m = r["means"]
    ok = aligned(m) and (m[0] - m[1]) >= GAP
    out = [{"id": "W1", "measured": f"over {r['arms']} arm-replicates the levels by position are "
                                    f"{m[0]:.4f} > {m[2]:.4f} > {m[1]:.4f}, a first-to-middle gap of "
                                    f"{m[0] - m[1]:.4f}",
            "verdict": "MET -- where a task sits predicts how well it is learned" if ok else
                       f"FALSIFIER FIRED -- {[round(x, 4) for x in m]}"}]

    fm = r["first_above_middle"]
    out.append({"id": "W2", "measured": f"paired within the arm, the first position beats the middle in "
                                        f"{100 * fm:.0f}% of them, the last beats the middle in "
                                        f"{100 * r['last_above_middle']:.0f}%, and the first beats the last in "
                                        f"{100 * r['first_above_last']:.0f}%",
                "verdict": "MET -- the effect survives pairing, so it is not a pooled artefact" if fm >= MAJORITY
                else f"FALSIFIER FIRED -- {100 * fm:.0f}%"})

    share = r["powered_first_above_middle"] / r["artifacts_powered"] if r["artifacts_powered"] else 0.0
    out.append({"id": "W3", "measured": f"of {r['artifacts_powered']} artifacts with {POWERED} or more three-task "
                                        f"arms, {r['powered_first_above_middle']} show the first above the middle "
                                        f"({100 * share:.0f}%)",
                "verdict": "MET -- the effect is a property of the configurations" if share >= MOST else
                           f"FALSIFIER FIRED -- {100 * share:.0f}%"})

    fam = r["families"]
    both = [k for k, v in fam.items() if aligned(v["means"])]
    detail = "; ".join(f"{k} ({v['arms']} arms) {v['means'][0]:.4f} > {v['means'][2]:.4f} > {v['means'][1]:.4f}"
                       for k, v in sorted(fam.items()))
    out.append({"id": "W4", "measured": f"{len(both)} of {len(fam)} families show the ordering -- {detail}",
                "verdict": "MET -- the effect is not one suite's task identities"
                if len(both) == len(fam) and len(fam) >= 2 else f"FALSIFIER FIRED -- {sorted(fam)}"})
    return out


def report(r: dict) -> int:
    print("== the level each task reaches, by its position in the sequence ==")
    print(f"   {r['arms']} arm-replicates over three-task suites")
    for j, name in enumerate(("learned first", "learned second", "learned third")):
        print(f"   position {j} ({name:14}) {r['means'][j]:.4f}")
    print(f"   paired: first above middle {100 * r['first_above_middle']:.0f}%, last above middle "
          f"{100 * r['last_above_middle']:.0f}%, first above last {100 * r['first_above_last']:.0f}%")

    print("\n== and by suite family ==")
    for k, v in sorted(r["families"].items()):
        print(f"   {k:9} {v['arms']:5} arms   {v['means'][0]:.4f} > {v['means'][2]:.4f} > {v['means'][1]:.4f}   "
              f"first above middle in {100 * v['first_above_middle']:.0f}%")

    print("\n== the registered claims, W1-W4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the block promises fixed task orders so numbers are comparable, and `e302` found the corpus has")
    print("    only ever used one order; this says the order would have moved the numbers, by four points)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
