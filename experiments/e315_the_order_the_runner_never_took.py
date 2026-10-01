"""E315 -- the order the runner never took: one suite, trained forwards and backwards, and the task that did not move.

`e302`'s M4 found that **no permutation of any suite had ever been run** -- every artifact in the corpus records its
suite's own naming order, so the block's promise of fixed task orders held trivially, because the order is a variable
with one value. `e310` then measured from the retention diagonals what varying it would cost: the position a task
sits in predicts the level it reaches by **four points of accuracy**, and 90% of the configurations show it.

**This is the run.** `--task-order` is now a flag on `e8_rate_network.py`, and this unit reads one configuration of
it in two orders:

    runs/e315_order_as_built.json    the suite's own order      ov1_t0, ov1_t1, ov1_t2
    runs/e315_order_reverse.json     the full reversal          ov1_t2, ov1_t1, ov1_t0

Same circuit, read-out, support draw, seeds and methods; **only the sequence differs**. A full reversal of three
tasks is a designed test rather than a sample of orders, because it leaves one task's position **unchanged**:

    ov1_t0    position 0 forwards, 2 backwards    <- changes
    ov1_t1    position 1 forwards, 1 backwards    <- does not
    ov1_t2    position 2 forwards, 0 backwards    <- changes

Four claims, registered before the reading below was taken:

- **P1 -- the two runs are one configuration in two orders.** They record the same suite reversed and the same
  support-draw fingerprint, so the x-axis did not move with the manipulation. **Falsifier**: a differing fingerprint.
- **P2 -- and the order moves the levels.** The two tasks whose position changes differ between the runs by more
  than their own paired sem. **Falsifier**: neither does.
- **P3 -- and the direction is the position's.** Each of those tasks reaches a **higher** level in the run where it is
  trained **first**: `ov1_t0` forwards and `ov1_t2` backwards. **Falsifier**: one of them the other way.
- **P4 -- and the control holds.** The task whose position is unchanged differs by **less** than both of the tasks
  that moved. **Falsifier**: it is not the smallest of the three.

**What it cannot do.** *One configuration and five replicates*, so P2's and P3's magnitudes are this configuration's
and not a scale: `e310` measured the effect across the corpus and this measures **one** instance of it. *A reversal is
one permutation and not a sample of them*: `ov1_t1`'s position is fixed by the design, which is what makes P4 possible
and also what makes the design a paired contrast rather than an experiment over orders. *The three tasks are draws from
one construction*, so their identities are not fixed across configurations and nothing here says which task is
"harder". *And the two runs are not the same trained models*: the sequence changes the gradients, so a difference is
the order's effect on the whole trajectory and not a controlled perturbation of one step.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
FORWARDS = Path("runs/e315_order_as_built.json")
BACKWARDS = Path("runs/e315_order_reverse.json")
#: What counts as a difference beyond a paired sem.
SIGMA = 1.0
CLAIMS = (
    ("P1", "the two runs are one configuration in two orders",
     "They record the same suite reversed and the same support-draw fingerprint",
     "falsifier: a differing fingerprint"),
    ("P2", "and the order moves the levels",
     "The two tasks whose position changes differ between the runs by more than their own paired sem",
     "falsifier: neither does"),
    ("P3", "and the direction is the position's",
     "Each of those tasks reaches a higher level in the run where it is trained first",
     "falsifier: one of them the other way"),
    ("P4", "and the control holds",
     "The task whose position is unchanged differs by less than both of the tasks that moved",
     "falsifier: it is not the smallest of the three"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def levels(run: dict, method: str) -> list[list[float]]:
    """Per replicate, the level each task reached, in the run's own order, keyed by task name."""
    out = []
    for rep in run["methods"][method]["replicates"]:
        got = rep.get("learned")
        if not got:
            return []
        out.append([float(v) for v in got])
    return out


def positions(run: dict) -> list[str]:
    return [str(t["name"]) for t in run["tasks"]]


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / (len(diffs) ** 0.5)
    #: A difference with no spread is infinite evidence and not absent evidence -- `e291`'s convention, kept here so
    #: a fixture that pairs constant lists does not read as an unresolved contrast.
    if sem < 1e-12:
        return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": float("inf") if mean else None}
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem}


def reading(fwd: Path = FORWARDS, bwd: Path = BACKWARDS) -> dict:
    a, b = load(fwd), load(bwd)
    if not a or not b:
        return {"runs": 0}
    names_a, names_b = positions(a), positions(b)
    methods = [m for m in ("naive", "ewc", "replay") if m in a.get("methods", {}) and m in b.get("methods", {})]
    per_method = {}
    for m in methods:
        la, lb = levels(a, m), levels(b, m)
        if not la or not lb or len(la) != len(lb):
            continue
        n = len(la)
        rows = {}
        for task in names_a:
            ia, ib = names_a.index(task), names_b.index(task)
            rows[task] = {"forward_position": ia, "backward_position": ib,
                          "moved": ia != ib,
                          **paired([la[r][ia] for r in range(n)], [lb[r][ib] for r in range(n)])}
        per_method[m] = {"n": n, "tasks": rows}
    return {"runs": 2, "forward": a, "backward": b,
            "same_fingerprint": a.get("support_draw", {}).get("fingerprint_sha1")
            == b.get("support_draw", {}).get("fingerprint_sha1"),
            "fingerprints": [a.get("support_draw", {}).get("fingerprint_sha1"),
                             b.get("support_draw", {}).get("fingerprint_sha1")],
            "reversed_names": names_b == names_a[::-1] and names_a != names_b,
            "names": [names_a, names_b],
            "orders": [a.get("config", {}).get("task_order"), b.get("config", {}).get("task_order")],
            "by_method": per_method,
            #: Reported and not claimed: P4 as registered compares a method's control against the smallest moved
            #: contrast of *any* method, and this is the same comparison taken inside each method, which is the one
            #: a reader wants and which the registration did not ask for.
            "control_smallest_within_method": {
                m: (min((row["sigma"] or 0) for t, row in v["tasks"].items() if not row["moved"]),)
                < (min((row["sigma"] or 0) for t, row in v["tasks"].items() if row["moved"]),)
                for m, v in per_method.items() if any(not x["moved"] for x in v["tasks"].values())},
            "same_seeds": [r.get("seed") for r in a["methods"][methods[0]]["replicates"]]
            == [r.get("seed") for r in b["methods"][methods[0]]["replicates"]] if methods else None}


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the two runs are not both on disk"}
                for c in CLAIMS]

    out = [{"id": "P1", "measured": f"orders {r['orders']}, task lists {r['names']}, support fingerprints "
                                    f"{r['fingerprints']}",
            "verdict": "MET -- one configuration in two orders, on one draw" if
            r["same_fingerprint"] and r["reversed_names"] else
            f"FALSIFIER FIRED -- fingerprints {r['fingerprints']}, reversed {r['reversed_names']}"}]

    moved = [(m, t, row) for m, v in r["by_method"].items() for t, row in v["tasks"].items() if row["moved"]]
    sig = [x for x in moved if (x[2]["sigma"] or 0) >= SIGMA]
    named = "; ".join(f"{m}/{t} {row['delta']:+.4f} at {row['sigma']:.2f} sigma" for m, t, row in moved)
    out.append({"id": "P2", "measured": f"{len(sig)} of {len(moved)} moved-position contrasts reach {SIGMA} sigma: "
                                        f"{named}",
                "verdict": "MET -- the order moves the levels of the tasks it moves" if len(sig) == len(moved)
                else f"FALSIFIER FIRED -- {len(sig)} of {len(moved)}"})

    #: A task is first in the run where its position is 0; P3 says that run's level is the higher one.
    wrong = [(m, t, x) for m, t, x in moved
             if (x["forward_position"] == 0 and (x["delta"] or 0) <= 0)
             or (x["backward_position"] == 0 and (x["delta"] or 0) >= 0)]
    detail = "; ".join(f"{m}/{t} positions {x['forward_position']}/{x['backward_position']} "
                       f"delta {x['delta']:+.4f}" for m, t, x in moved)
    out.append({"id": "P3", "measured": f"{len(moved) - len(wrong)} of {len(moved)} moved-position contrasts favour "
                                        f"the run that trains the task first: {detail}",
                "verdict": "MET -- training a task first is worth a higher level" if moved and not wrong else
                           f"FALSIFIER FIRED -- {wrong}"})

    still = [(m, t, row) for m, v in r["by_method"].items() for t, row in v["tasks"].items() if not row["moved"]]
    smallest = all((s["sigma"] or 0) <= min((x["sigma"] or 0) for _, _, x in moved) for _, _, s in still) \
        if still and moved else False
    held = "; ".join(f"{m}/{t} delta {row['delta']:+.4f} at {row['sigma']:.2f} sigma" for m, t, row in still)
    biggest = max((x["sigma"] or 0) for _, _, x in moved) if moved else 0
    inside = r.get("control_smallest_within_method") or {}
    out.append({"id": "P4", "measured": f"the unchanged-position task(s): {held or 'none'}; the largest moved "
                                        f"contrast is {biggest:.2f} sigma. **Reported and not claimed**: taken "
                                        f"inside each method instead, the control is the smallest contrast in "
                                        f"{sum(1 for v in inside.values() if v)} of {len(inside)} methods "
                                        f"({inside})",
                "verdict": "MET -- the task that did not move did not move" if smallest else
                           f"FALSIFIER FIRED -- {held}"})
    return out


def report(r: dict) -> int:
    print("== one suite in two orders ==")
    print(f"   {r['orders']}  {r['names'][0]}  and  {r['names'][1]}")
    print(f"   support fingerprint {r['fingerprints'][0]} vs {r['fingerprints'][1]}; same seeds: {r['same_seeds']}")
    print(f"\n   {'method':8} {'task':10} {'pos fwd':>8} {'pos bwd':>8} {'delta (fwd - bwd)':>18} {'sigma':>7}")
    for m, v in sorted(r["by_method"].items()):
        for t, row in sorted(v["tasks"].items()):
            mark = "  <- moved" if row["moved"] else "  <- control"
            print(f"   {m:8} {t:10} {row['forward_position']:8} {row['backward_position']:8} "
                  f"{row['delta']:+18.4f} {row['sigma']:7.2f}{mark}")
        print(f"   {'':8} ({v['n']} replicates each)")

    print("\n== the registered claims, P1-P4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the block promised fixed task orders so numbers are comparable, and the corpus had only ever used")
    print("    one; this is the second, and the task whose position the reversal leaves alone is the control)")
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
    r.pop("forward", None)
    r.pop("backward", None)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
