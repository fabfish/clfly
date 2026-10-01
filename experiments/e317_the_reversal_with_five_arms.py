"""E317 -- the reversal with all five arms: is the position effect about the task's place or about one method?

`e315` made the corpus's first permuted suite and found all six of its moved-position contrasts favouring the run
that trains the task first, in three arms. `e316` repeated the reversal on the assembly family and found the effect
carried by **`ewc` alone** -- +0.0854 at 4.38 sigma and -0.0958 at 6.27 -- with `naive` and `replay` at or below
0.71 sigma and three of their six contrasts the other way. `e316`'s own limitation names what that leaves open:
**`ewc` is the arm that reads the largest penalty in this design, so whether the effect is about the penalty is a
third configuration's question.**

**This is the third configuration, and the question is asked directly.** The same reversal, on the same assembly
family and the same circuit, with **all five** arms: `naive` and `replay` read no penalty, and `ewc`, `ewc-block` and
`ewc-block-rand` each read one -- the diagonal, a biological partition and a size-matched random one.

    runs/e317_five_as_built.json    ov-order: odour_identity, heading, odour_input
    runs/e317_five_reverse.json     its full reversal

Four claims, registered before the reading below was taken:

- **R1 -- the two runs are one configuration in two orders.** Same circuit, same read-out subset, same seeds, one
  task list the other reversed. **Falsifier**: a differing circuit or read-out, or a list that is not a reversal.
- **R2 -- and the direction is the position's for most of the arms.** At least half of the ten moved-position
  contrasts favour the run that trains the task first. **Falsifier**: fewer than half.
- **R3 -- and it is carried by the arms that read a penalty.** Every contrast that clears **1 sigma** belongs to one
  of `ewc`, `ewc-block` or `ewc-block-rand`. **Falsifier**: a contrast of `naive` or `replay` clears 1 sigma.
- **R4 -- and the control holds in most methods.** The unchanged-position task is the smallest of a method's three
  contrasts in at least **three of the five** arms. **Falsifier**: fewer than three.

**What it cannot do.** *One configuration and five replicates per arm*, so the magnitudes are this configuration's and
five replicates put a wide interval on a contrast near 1 sigma. *The arms are not independent experiments*: they are
trained on the same suite with the same seeds, so their contrasts share the tasks and the initial body, and R3's
"carried by the penalty arms" is a statement about which arms move and not about a mechanism. *A penalty arm's*
`naive` *counterpart is not run here*: the design compares arms that read a penalty with arms that do not, and not one
arm against itself with the penalty switched off. *And a reversal is one permutation*: the middle task holds its
position by construction and nothing here samples orders.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
FORWARDS = RUNS / "e317_five_as_built.json"
BACKWARDS = RUNS / "e317_five_reverse.json"
#: The five arms, and which of them read a penalty.
ARMS = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
PENALTY = ("ewc", "ewc-block", "ewc-block-rand")
#: R2's share, R3's sigma and R4's count.
HALF = 0.5
SIGMA = 1.0
CONTROLS = 3
CLAIMS = (
    ("R1", "the two runs are one configuration in two orders",
     "Same circuit, same read-out subset, same seeds, and one task list the other reversed",
     "falsifier: a differing circuit or read-out, or a list that is not a reversal"),
    ("R2", "and the direction is the position's for most of the arms",
     f"At least half of the moved-position contrasts favour the run that trains the task first",
     "falsifier: fewer than half"),
    ("R3", "and it is carried by the arms that read a penalty",
     f"Every moved-position contrast that clears {SIGMA} sigma belongs to `ewc`, `ewc-block` or `ewc-block-rand`",
     "falsifier: a contrast of `naive` or `replay` clears it"),
    ("R4", "and the control holds in most methods",
     f"The unchanged-position task is the smallest of its three contrasts in at least {CONTROLS} of the five arms",
     "falsifier: fewer than that"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / (len(diffs) ** 0.5)
    if sem < 1e-12:
        return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": float("inf") if mean else None}
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem}


def reading(fwd: Path = FORWARDS, bwd: Path = BACKWARDS) -> dict:
    a, b = load(fwd), load(bwd)
    if not a or not b:
        return {"runs": 0}
    names_a = [str(t["name"]) for t in a["tasks"]]
    names_b = [str(t["name"]) for t in b["tasks"]]
    out = {"runs": 2, "circuits": [a.get("circuit"), b.get("circuit")],
           "same_circuit": a.get("circuit") == b.get("circuit"),
           "readout_subsets": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
           "orders": [a.get("config", {}).get("task_order"), b.get("config", {}).get("task_order")],
           "names": [names_a, names_b],
           "reversed_names": names_b == names_a[::-1] and names_a != names_b}
    out["same_readout"] = out["readout_subsets"][0] == out["readout_subsets"][1]
    methods = {}
    for m in ARMS:
        ea, eb = a.get("methods", {}).get(m), b.get("methods", {}).get(m)
        if not isinstance(ea, dict) or not isinstance(eb, dict):
            continue
        la = [r.get("learned") for r in ea.get("replicates") or []]
        lb = [r.get("learned") for r in eb.get("replicates") or []]
        if not la or not lb or any(x is None for x in la + lb) or len(la) != len(lb):
            continue
        n = len(la)
        rows = {}
        for task in names_a:
            ia, ib = names_a.index(task), names_b.index(task)
            rows[task] = {"forward_position": ia, "backward_position": ib, "moved": ia != ib,
                          **paired([la[r][ia] for r in range(n)], [lb[r][ib] for r in range(n)])}
        moved = [x for x in rows.values() if x["moved"]]
        still = [x for x in rows.values() if not x["moved"]]
        methods[m] = {"n": n, "tasks": rows, "reads_a_penalty": m in PENALTY,
                      "control_smallest": (min((x["sigma"] or 0) for x in still) < min((x["sigma"] or 0) for x in moved))
                      if moved and still else None}
    out["by_method"] = methods
    out["same_seeds"] = ([r.get("seed") for r in a["methods"][ARMS[0]]["replicates"]]
                         == [r.get("seed") for r in b["methods"][ARMS[0]]["replicates"]]) if methods else None
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the two runs are not both on disk"}
                for c in CLAIMS]

    out = [{"id": "R1", "measured": f"circuits {r['circuits']}, read-out {r['readout_subsets']}, orders "
                                    f"{r['orders']}, task lists {r['names']}, same seeds {r['same_seeds']}",
            "verdict": "MET -- one configuration in two orders" if
            r["same_circuit"] and r["same_readout"] and r["reversed_names"] else
            f"FALSIFIER FIRED -- circuit {r['same_circuit']}, read-out {r['same_readout']}, "
            f"reversed {r['reversed_names']}"}]

    moved = [(m, t, row) for m, v in r["by_method"].items() for t, row in v["tasks"].items() if row["moved"]]
    firsts = [x for x in moved
              if (x[2]["forward_position"] == 0 and (x[2]["delta"] or 0) > 0)
              or (x[2]["backward_position"] == 0 and (x[2]["delta"] or 0) < 0)]
    share = len(firsts) / len(moved) if moved else 0.0
    out.append({"id": "R2", "measured": f"{len(firsts)} of {len(moved)} moved-position contrasts favour the run that "
                                        f"trains the task first: " + "; ".join(
                                            f"{m}/{t} {row['delta']:+.4f} at {row['sigma']:.2f}"
                                            for m, t, row in moved),
                "verdict": "MET -- most of the arms carry the direction" if share >= HALF else
                           f"FALSIFIER FIRED -- {len(firsts)} of {len(moved)}"})

    cleared = [(m, t, row) for m, t, row in moved if (row["sigma"] or 0) >= SIGMA]
    strangers = [(m, t, row) for m, t, row in cleared if m not in PENALTY]
    out.append({"id": "R3", "measured": f"{len(cleared)} of {len(moved)} contrasts clear {SIGMA} sigma, in arms "
                                        f"{sorted({m for m, _, _ in cleared})}; the arms that read no penalty are "
                                        f"`naive` and `replay`",
                "verdict": "MET -- the arms that read a penalty are the ones that move" if cleared and not strangers
                else f"FALSIFIER FIRED -- {[(m, t) for m, t, _ in strangers]}"})

    controls = {m: v["control_smallest"] for m, v in r["by_method"].items() if v["control_smallest"] is not None}
    held = sorted(m for m, ok in controls.items() if ok)
    out.append({"id": "R4", "measured": f"the unchanged-position task is the smallest contrast in {len(held)} of "
                                        f"{len(controls)} arms ({', '.join(held) or 'none'})",
                "verdict": "MET -- the task that did not move is the quiet one in most arms" if
                len(held) >= CONTROLS else f"FALSIFIER FIRED -- {len(held)} of {len(controls)}"})
    return out


def report(r: dict) -> int:
    print("== the assembly suite reversed, with all five arms ==")
    print(f"   orders {r['orders']}; circuits {r['circuits']}; read-out {r['readout_subsets']}")
    print(f"   {r['names'][0]}  and  {r['names'][1]}; same seeds {r['same_seeds']}")
    print(f"\n   {'arm':16} {'penalty':8} {'task':18} {'pos fwd':>8} {'pos bwd':>8} {'delta fwd-bwd':>14} {'sigma':>7}")
    for m, v in sorted(r["by_method"].items()):
        for t, row in sorted(v["tasks"].items()):
            print(f"   {m:16} {str(v['reads_a_penalty']):8} {t:18} {row['forward_position']:8} "
                  f"{row['backward_position']:8} {row['delta']:+14.4f} {row['sigma']:7.2f}"
                  f"{'' if row['moved'] else '  <- control'}")
        print(f"   {'':16} {'':8} ({v['n']} replicates; control smallest: {v['control_smallest']})")

    print("\n== the registered claims, R1-R4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e316` found the effect in `ewc` alone on this family and named the question: with five arms and")
    print("    the three that read a penalty separated from the two that do not, the question has an answer)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forward", type=Path, default=FORWARDS)
    ap.add_argument("--backward", type=Path, default=BACKWARDS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.forward, args.backward)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
