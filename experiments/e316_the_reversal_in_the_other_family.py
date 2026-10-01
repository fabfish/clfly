"""E316 -- the reversal in the other family, and the control registered the way a reader wants it.

`e315` made the corpus's first permuted suite: the `ov1` overlap suite trained forwards and backwards, and every one
of its six moved-position contrasts favoured the run that trains the task first. Its own limitations named what that
could not say -- **one configuration and five replicates** -- and its P4 fired on a **mis-specified registration**,
having compared a method's control against the smallest moved contrast of *any* method rather than the one beside it.

**This unit answers both.** It reads `--task-order` run forwards and backwards on the **assembly** suite --
`odour_identity`, `heading`, `odour_input`, three different modalities rather than three draws from one construction,
and the family `e310` found the effect in at 78% rather than 67% -- at **ten replicates** per arm, and it registers
the control **inside each method**, which is the comparison e315's P4 should have asked for.

Four claims, registered before the reading below was taken:

- **Q1 -- the two runs are one configuration in two orders.** They record the same circuit and the same read-out
  subset, and the task list of one is the other reversed. **Falsifier**: a differing circuit or read-out, or a list
  that is not a reversal.
- **Q2 -- and the direction is the position's, in this family too.** Every moved-position contrast favours the run
  that trains the task first. **Falsifier**: one the other way.
- **Q3 -- and the control holds within every method.** For each method, the task whose position the reversal leaves
  alone is the *smallest* of its three contrasts. **Falsifier**: a method where it is not.
- **Q4 -- and the effect is not a small-sample artefact.** The largest moved-position contrast reaches at least
  **2 sigma**. **Falsifier**: below 2.

**What it cannot do.** *Two configurations and two orders*, so "the direction is the position's" is now two
instances and still not a law: a reversal is one permutation, and neither unit samples orders. *The magnitudes are
each configuration's*: `e315` ran five replicates on the overlap family and this runs ten on the assembly suite, so
the sigmas are not comparable across the two except in sign. *The two runs are not the same trained models*, since
the sequence changes the gradients, so a difference is the order's effect on the whole trajectory. *And the control
is weaker than the contrast*: the unchanged-position task still has the other two tasks around it changed, so its
"no move" is a statement about the position being held and not about the run being perturbed in one place only.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
FORWARDS = RUNS / "e316_assembly_as_built.json"
BACKWARDS = RUNS / "e316_assembly_reverse.json"
#: The earlier pair, read beside this one and reported rather than claimed.
EARLIER = (RUNS / "e315_order_as_built.json", RUNS / "e315_order_reverse.json")
#: Q2's and Q4's thresholds.
SIGMA = 1.0
LARGEST = 2.0
CLAIMS = (
    ("Q1", "the two runs are one configuration in two orders",
     "They record the same circuit and read-out subset, and one task list is the other reversed",
     "falsifier: a differing circuit or read-out, or a list that is not a reversal"),
    ("Q2", "and the direction is the position's, in this family too",
     "Every moved-position contrast favours the run that trains the task first",
     "falsifier: one the other way"),
    ("Q3", "and the control holds within every method",
     "For each method the unchanged-position task is the smallest of its three contrasts",
     "falsifier: a method where it is not"),
    ("Q4", "and the effect is not a small-sample artefact",
     f"The largest moved-position contrast reaches at least {LARGEST} sigma",
     f"falsifier: below {LARGEST}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def positions(run: dict) -> list[str]:
    return [str(t["name"]) for t in run["tasks"]]


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / (len(diffs) ** 0.5)
    if sem < 1e-12:
        return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": float("inf") if mean else None}
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem}


def pair_reading(a: dict, b: dict) -> dict:
    """One ordered pair of runs read the way the design asks: by task, by method, by position."""
    names_a, names_b = positions(a), positions(b)
    methods = [m for m in ("naive", "ewc", "replay")
               if isinstance(a.get("methods", {}).get(m), dict) and isinstance(b.get("methods", {}).get(m), dict)]
    per_method = {}
    for m in methods:
        la = [r.get("learned") for r in a["methods"][m].get("replicates") or []]
        lb = [r.get("learned") for r in b["methods"][m].get("replicates") or []]
        if not la or not lb or any(x is None for x in la + lb) or len(la) != len(lb):
            continue
        n = len(la)
        rows = {}
        for task in names_a:
            ia, ib = names_a.index(task), names_b.index(task)
            rows[task] = {"forward_position": ia, "backward_position": ib, "moved": ia != ib,
                          **paired([la[r][ia] for r in range(n)], [lb[r][ib] for r in range(n)])}
        per_method[m] = {"n": n, "tasks": rows,
                         "control_smallest": (min((x["sigma"] or 0) for x in rows.values() if not x["moved"])
                                              < min((x["sigma"] or 0) for x in rows.values() if x["moved"]))
                         if any(not x["moved"] for x in rows.values()) else None}
    readout = [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")]
    return {"circuits": [a.get("circuit"), b.get("circuit")],
            "same_circuit": a.get("circuit") == b.get("circuit"),
            "readout_subsets": readout, "same_readout": readout[0] == readout[1],
            "orders": [a.get("config", {}).get("task_order"), b.get("config", {}).get("task_order")],
            "names": [names_a, names_b],
            "reversed_names": names_b == names_a[::-1] and names_a != names_b,
            "same_seeds": [r.get("seed") for r in a["methods"][methods[0]]["replicates"]]
            == [r.get("seed") for r in b["methods"][methods[0]]["replicates"]] if methods else None,
            "by_method": per_method}


def reading(fwd: Path = FORWARDS, bwd: Path = BACKWARDS) -> dict:
    a, b = load(fwd), load(bwd)
    if not a or not b:
        return {"runs": 0}
    r = pair_reading(a, b)
    r["runs"] = 2
    earlier = [load(p) for p in EARLIER]
    r["earlier"] = {"present": all(earlier), **pair_reading(*earlier)} if all(earlier) else {"present": False}
    return r


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the two runs are not both on disk"}
                for c in CLAIMS]

    out = [{"id": "Q1", "measured": f"circuits {r['circuits']}, read-out subsets {r['readout_subsets']}, orders "
                                    f"{r['orders']}, task lists {r['names']}, same seeds {r['same_seeds']}",
            "verdict": "MET -- one configuration in two orders" if
            r["same_circuit"] and r["same_readout"] and r["reversed_names"] else
            f"FALSIFIER FIRED -- circuit {r['same_circuit']}, read-out {r['same_readout']}, "
            f"reversed {r['reversed_names']}"}]

    moved = [(m, t, row) for m, v in r["by_method"].items() for t, row in v["tasks"].items() if row["moved"]]
    wrong = [(m, t, row) for m, t, row in moved
             if (row["forward_position"] == 0 and (row["delta"] or 0) <= 0)
             or (row["backward_position"] == 0 and (row["delta"] or 0) >= 0)]
    detail = "; ".join(f"{m}/{t} positions {row['forward_position']}/{row['backward_position']} "
                       f"delta {row['delta']:+.4f} at {row['sigma']:.2f} sigma" for m, t, row in moved)
    out.append({"id": "Q2", "measured": f"{len(moved) - len(wrong)} of {len(moved)} moved-position contrasts favour "
                                        f"the run that trains the task first: {detail or 'none'}",
                "verdict": "MET -- the direction is the position's, in this family too" if moved and not wrong else
                           f"FALSIFIER FIRED -- {wrong}"})

    controls = {m: v["control_smallest"] for m, v in r["by_method"].items() if v["control_smallest"] is not None}
    held = sorted(m for m, ok in controls.items() if ok)
    out.append({"id": "Q3", "measured": f"the unchanged-position task is the smallest of its three contrasts in "
                                        f"{len(held)} of {len(controls)} methods{'' if not controls else ' (' + ', '.join(held) + ')'}"
                                        f"; each method's control and smallest moved sigma: "
                                        + "; ".join(f"{m} {min((x['sigma'] or 0) for x in v['tasks'].values() if not x['moved']):.2f} "
                                                    f"against {min((x['sigma'] or 0) for x in v['tasks'].values() if x['moved']):.2f}"
                                                    for m, v in r["by_method"].items()
                                                    if v["control_smallest"] is not None),
                "verdict": "MET -- the task that did not move is the quiet one, method by method" if
                controls and all(controls.values()) else
                f"FALSIFIER FIRED -- {[m for m, ok in controls.items() if not ok]}"})

    biggest = max((x["sigma"] or 0) for _, _, x in moved) if moved else 0
    out.append({"id": "Q4", "measured": f"the largest moved-position contrast is {biggest:.2f} sigma over "
                                        f"{r['by_method'][list(r['by_method'])[0]]['n']} replicates",
                "verdict": "MET -- the effect is not a small-sample artefact" if biggest >= LARGEST else
                           f"FALSIFIER FIRED -- {biggest:.2f}"})
    return out


def report(r: dict) -> int:
    print("== the assembly suite trained forwards and backwards ==")
    print(f"   orders {r['orders']}, circuits {r['circuits']}, read-out {r['readout_subsets']}")
    print(f"   {r['names'][0]}  and  {r['names'][1]}; same seeds {r['same_seeds']}")
    print(f"\n   {'method':8} {'task':18} {'pos fwd':>8} {'pos bwd':>8} {'delta (fwd - bwd)':>18} {'sigma':>7}")
    for m, v in sorted(r["by_method"].items()):
        for t, row in sorted(v["tasks"].items()):
            print(f"   {m:8} {t:18} {row['forward_position']:8} {row['backward_position']:8} "
                  f"{row['delta']:+18.4f} {row['sigma']:7.2f}"
                  f"{'' if row['moved'] else '  <- control'}")
        print(f"   {'':8} ({v['n']} replicates each; control smallest: {v['control_smallest']})")

    if r.get("earlier", {}).get("present"):
        e = r["earlier"]
        print(f"\n== and the earlier pair read the same way ({e['orders']}, {e['names'][0]}) ==")
        for m, v in sorted(e["by_method"].items()):
            moved = [x for x in v["tasks"].values() if x["moved"]]
            still = [x for x in v["tasks"].values() if not x["moved"]]
            print(f"   {m:8} {len(moved)} moved and {len(still)} control; control smallest: {v['control_smallest']}")

    print("\n== the registered claims, Q1-Q4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the reversal run a second time, on the family whose three tasks are different modalities, with ten")
    print("    replicates and the control taken inside each method -- which is what e315's P4 should have asked)")
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
    for key in ("runs_before",):
        r.pop(key, None)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
