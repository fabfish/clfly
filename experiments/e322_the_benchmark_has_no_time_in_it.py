"""E322 -- the trial's time axis, measured: every task in `FlyCL v0` delivers a stimulus that never changes.

The benchmark block calls this suite a continual-learning benchmark for a **recurrent** network, and the plan's own
description of a task says the stimulus is *"injected into a task's input population as a sustained drive"*. That
word is load-bearing and has never been measured: if the drive is sustained for the whole trial, then the trial's
time axis carries no information, the recurrence is a settling transient from a zero state toward a fixed point, and
the label is a property of where the state lands rather than of anything happening over time.

That distinction decides what this benchmark can be asked. A **game** needs the environment's next input to depend on
the agent's previous output, which is exactly a stimulus that changes with time; an open-loop classification suite
cannot contain one, however many tasks are stacked on it. So this unit measures the axis before anyone builds on it.

**The instrument has three parts.** A **structural scan** of every module that authors task stimuli, an
**invariance measurement** on the real circuit for both suite builders, and a **settling and read-out measurement**
on the frozen connectome network, which isolates the circuit's own time constant from the training.

Five claims, registered before the reading below was taken:

- **T1 -- the stimulus is exactly time-invariant in both suite builders.** For every task of `make_suite` and
  `make_overlap_suite`, at every circuit size, support seed and overlap level tested, the stimulus at every step
  equals its first step **exactly**. **Falsifier**: one task with a nonzero deviation.
- **T2 -- and there is exactly one site in the repository that writes one.** Of the modules under `clfly/` and
  `experiments/` -- the modules that author the corpus -- exactly one subscript store targets a stimulus-shaped array,
  and its time axis is a full slice. **Falsifier**: a second site, or a site whose time index is not a slice.
- **T3 -- so the trial is a settling transient and not a sequence.** On the frozen network, the state's step size at
  the last step is **below 5%** of its first step, for every task of both suites and at both circuit sizes.
  **Falsifier**: any task at or above 5%, which would say the trial ends while the state is still moving.
- **T4 -- and the read-out is in place by the midpoint.** For every task whose final-rung linear probe is at least
  0.05 above chance, the probe's accuracy at step ``tau // 2`` is **within 0.05** of its final-rung accuracy.
  **Falsifier**: a gap of 0.10 or more on any such task. **Null**: a gap between 0.05 and 0.10.
- **T5 -- and the corpus is inside these two builders.** Every task name in every artifact under `runs/` belongs to
  one of the two builders' naming families. **Falsifier**: an artifact naming a task in neither.

**What it cannot do.** *The frozen network is the connectome initialisation and not a trained one*: a trained
network's time constant moves, and this unit measures the circuit's own, which is the part the substrate contributes.
*The probe is linear* and fitted per step on the trajectory's read-out population, so a task that is not linearly
decodable at all is reported as such rather than as a bad time axis. *Three tasks and two circuit sizes* at one
connectome, one weight scale and one leak: whether the settling fraction is a property of the circuit or of
`alpha` is not separated. *And a settled trajectory is not the same as a useless one*: the state still depends on the
input, so `T3` says the label is a fixed point and never that the recurrence does nothing.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the modules that author the corpus, and the two builders whose tasks the corpus is built from
AUTHOR_DIRS = ("clfly", "experiments")
SCAN_DIRS = ("clfly", "experiments", "tests")
#: T3's bar, as a fraction of the first step's size, and T4's two windows
SETTLED = 0.05
IN_PLACE = 0.05
GAP = 0.10
#: the overlap-suite task names, so a corpus task can be assigned to a family without loading a suite
OVERLAP_NAME = re.compile(r"^ov[0-9.]+_t\d+$")
CLAIMS = (
    ("T1", "the stimulus is exactly time-invariant in both suite builders",
     "Every task's stimulus equals its first step exactly, at every tested size, seed and overlap",
     "falsifier: one task with a nonzero deviation"),
    ("T2", "and there is exactly one site in the repository that writes one",
     "Exactly one subscript store in `clfly/` and `experiments/` targets a stimulus-shaped array, its time axis a "
     "full slice",
     "falsifier: a second site, or a site whose time index is not a slice"),
    ("T3", f"so the trial is a settling transient: the last step is below {SETTLED:.0%} of the first",
     f"On the frozen network every task's step size at the last step is below {SETTLED:.0%} of its first step",
     "falsifier: one task at or above that bar, so the trial ends while the state is still moving"),
    ("T4", f"and the read-out is in place by the midpoint, within {IN_PLACE:.2f}",
     f"Every task above chance reads within {IN_PLACE:.2f} of its final-rung probe at step `tau // 2`",
     f"falsifier: a gap of {GAP:.2f} or more on any such task"),
    ("T5", "and the corpus is inside these two builders",
     "Every task name in every artifact under `runs/` belongs to one of the two builders' families",
     "falsifier: an artifact naming a task in neither"),
)


# --------------------------------------------------------------------------
# the structural scan
def scan_stimulus_writers(dirs=SCAN_DIRS) -> list[dict]:
    """Every subscript store in ``dirs`` whose target is indexed in three dimensions with a slice.

    A store of this shape is the only way a task's stimulus gets into the array the model consumes:
    the array is ``(n, tau, n_neurons)``, so index 1 is the time axis. A store whose index tuple has
    a **full slice** at position 1 writes the same value at every step by construction; one whose
    position 1 is anything else (a name, a range) writes along time and is what this scan is for.
    """
    sites = []
    for root in dirs:
        for path in sorted(Path(root).rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Assign, ast.AugAssign)):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for tgt in targets:
                    if not isinstance(tgt, ast.Subscript) or not isinstance(tgt.slice, ast.Tuple):
                        continue
                    elts = tgt.slice.elts
                    if len(elts) < 3 or not any(isinstance(e, ast.Slice) for e in elts):
                        continue
                    time_axis = elts[1]
                    sites.append({
                        "file": path.as_posix(),
                        "line": tgt.lineno,
                        "ndim": len(elts),
                        "time_is_full_slice": (isinstance(time_axis, ast.Slice)
                                               and time_axis.lower is None and time_axis.upper is None
                                               and time_axis.step is None),
                    })
    return sorted(sites, key=lambda s: (s["file"], s["line"]))


# --------------------------------------------------------------------------
# the measurement on the real circuit
def circuit(size: int):
    from clfly.connectome import annotate, circuits, graph
    conn = graph.build()
    ann = annotate.load_annotations()
    return circuits.extract(conn, ann, hops=0, max_neurons=size)


def suites(circ, n_train: int, n_test: int, classes: int):
    from clfly.network import tasks as rate_tasks
    kw = dict(n_train=n_train, n_test=n_test, n_classes=classes)
    built = [("assembly", rate_tasks.make_suite(circ, **kw))]
    for overlap in (0.0, 1.0):
        built.append((f"overlap{overlap:g}",
                      rate_tasks.make_overlap_suite(circ, overlap=overlap, seed=0, **kw)))
    return built


def invariance(name: str, suite) -> dict:
    """``max |u[:, t] - u[:, 0]|`` over every task and every step of both splits."""
    worst = 0.0
    per_task = {}
    for task in suite:
        dev = max(float(np.max(np.abs(np.asarray(u)[:, t] - np.asarray(u)[:, 0])))
                  for u in (task.u_train, task.u_test) for t in range(task.tau))
        per_task[task.name] = dev
        worst = max(worst, dev)
    return {"suite": name, "n_tasks": len(suite), "worst": worst, "per_task": per_task}


def roll(net, u) -> np.ndarray:
    """The frozen network's trajectory, ``(n, tau, n_neurons)``."""
    import torch
    with torch.no_grad():
        traj = net.torch_model()(torch.from_numpy(np.asarray(u, dtype=np.float32)))
    return traj.numpy()


def probe(traj_tr: np.ndarray, y_tr, traj_te: np.ndarray, y_te, neurons, ridge: float = 1e-2) -> list[float]:
    """A linear read-out of the class from ``neurons`` at each step, fitted per step.

    The closed-form least-squares decoder is the weakest read-out a step could offer, which is what a
    statement about *when* the label becomes available needs: a stronger decoder would move the answer
    earlier and flatter, not later.
    """
    out = []
    for t in range(traj_tr.shape[1]):
        X = traj_tr[:, t, :][:, neurons]
        Xt = traj_te[:, t, :][:, neurons]
        X = np.concatenate([X, np.ones((len(X), 1))], axis=1)
        Xt = np.concatenate([Xt, np.ones((len(Xt), 1))], axis=1)
        Y = np.eye(int(np.max(y_tr)) + 1)[y_tr]
        W = np.linalg.solve(X.T @ X + ridge * np.eye(X.shape[1]), X.T @ Y)
        out.append(float(np.mean(np.argmax(Xt @ W, axis=1) == y_te)))
    return out


def time_axis(conn_net, name: str, suite, chance: float) -> dict:
    """Per task: the settling curve, the settled fraction, and the per-step probe."""
    tasks = {}
    for task in suite:
        tr = roll(conn_net, task.u_train)
        te = roll(conn_net, task.u_test)
        steps = [float(np.max(np.abs(tr[:, t + 1] - tr[:, t]))) for t in range(task.tau - 1)]
        acc = probe(tr, np.asarray(task.y_train), te, np.asarray(task.y_test), task.readout_neurons)
        mid = task.tau // 2
        final = acc[-1]
        best = int(np.argmax(acc))
        top = max(steps) if steps else 0.0
        tasks[task.name] = {
            "chance": chance,
            "step_sizes": steps,
            "settled_fraction": (steps[-1] / steps[0]) if steps[0] else None,
            #: the same question with an unbiased denominator: the first step is `alpha * tanh(u)` from a zero
            #: state and carries no recurrent contribution, so it is the smallest step by construction. The
            #: ratio to the trial's largest step asks whether the trajectory has stopped moving, and it is
            #: reported beside the registered statistic rather than in its place.
            "last_over_max": (steps[-1] / top) if top else None,
            "first_over_max": (steps[0] / top) if top else None,
            "probe": acc,
            "probe_final": final,
            "probe_midpoint": acc[mid],
            "probe_gap": (final - acc[mid]) if final - chance >= IN_PLACE else None,
            #: where the read-out peaks, recorded because the curve above is the measurement and this is the
            #: one number a reader wants from it. It is a description of the recorded curve taken after the
            #: five claims were registered, and it decides none of them.
            "probe_best_step": best,
            "probe_best": acc[best],
            "probe_last_minus_best": final - acc[best],
        }
    return {"suite": name, "chance": chance, "tasks": tasks}


def corpus_families(pattern: str = "runs/*.json") -> dict:
    """Which naming family every artifact's tasks belong to, over the whole corpus."""
    assembly, overlap, other, artifacts = set(), set(), set(), 0
    names = set()
    for path in sorted(Path(".").glob(pattern)):
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        tasks = payload.get("tasks")
        if not isinstance(tasks, list):
            continue
        artifacts += 1
        for t in tasks:
            name = str(t.get("name") if isinstance(t, dict) else t)
            names.add(name)
            if OVERLAP_NAME.match(name):
                overlap.add(name)
            else:
                assembly.add(name)
    from clfly.network.tasks import SUITE_SPECS
    known = {s[0] for s in SUITE_SPECS}
    for name in sorted(assembly):
        if name not in known:
            other.add(name)
    return {"artifacts": artifacts, "scanned": True, "suite_names": sorted(known),
            "assembly_names": sorted(assembly),
            "overlap_names": sorted(overlap), "unclassified": sorted(other), "n_names": len(names)}


# --------------------------------------------------------------------------
def reading(sizes=(300, 800), n_train: int = 48, n_test: int = 24, classes: int = 4,
            corpus: bool = True) -> dict:
    from clfly.network.model import RateConfig, build_net
    out = {"scan": scan_stimulus_writers(), "sizes": list(sizes), "invariance": [], "time_axis": []}
    for size in sizes:
        circ = circuit(size)
        conn_net = build_net(circ, RateConfig(tau=12))
        for name, suite in suites(circ, n_train, n_test, classes):
            out["invariance"].append({"circuit": circ.name, "size": circ.n_neurons,
                                      **invariance(name, suite)})
            out["time_axis"].append({"circuit": circ.name, "size": circ.n_neurons,
                                     **time_axis(conn_net, name, suite, 1.0 / classes)})
    out["corpus"] = corpus_families() if corpus else {"artifacts": 0, "scanned": False}
    return out


def judge(r: dict) -> list[dict]:
    inv = r.get("invariance", [])
    axis = r.get("time_axis", [])
    if not inv or not axis:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the circuit was not measured"}
                for c in CLAIMS]

    worst = max(x["worst"] for x in inv)
    n_tasks = sum(x["n_tasks"] for x in inv)
    j1 = {"id": "T1", "measured": f"{n_tasks} task instances over {len(inv)} suite builds and "
                                  f"{len(r['sizes'])} circuit sizes; worst deviation {worst:g}",
          "verdict": "MET -- the stimulus is the same array at every step" if worst == 0.0 else
                     f"FALSIFIER FIRED -- a task's stimulus varies across the trial by {worst:g}"}

    authored = [s for s in r["scan"] if any(s["file"].startswith(d + "/") for d in AUTHOR_DIRS)]
    varying = [s for s in authored if not s["time_is_full_slice"]]
    where = ", ".join(f"`{s['file']}:{s['line']}`" for s in authored) or "none"
    j2 = {"id": "T2", "measured": f"{len(authored)} stimulus-writing site(s) under "
                                  f"{' and '.join('`' + d + '/' + '`' for d in AUTHOR_DIRS)}: {where}; "
                                  f"{len(r['scan']) - len(authored)} further site(s) under `tests/`",
          "verdict": "MET -- one site, writing the same value along the time axis"
          if len(authored) == 1 and not varying else
          f"FALSIFIER FIRED -- {len(authored)} authored site(s), {len(varying)} writing along time"}

    rows = [(x["suite"], t, v) for x in axis for t, v in x["tasks"].items()]
    worst_f = max(v["settled_fraction"] for _, _, v in rows)
    worst_m = max(v["last_over_max"] for _, _, v in rows)
    detail = "; ".join(f"{s} {t} {v['settled_fraction']:.2e}" for s, t, v in rows)
    j3 = {"id": "T3", "measured": f"{len(rows)} tasks, worst settled fraction {worst_f:.4f} against a bar of "
                                  f"{SETTLED}: {detail}; and with the trial's largest step as the denominator the "
                                  f"worst last step is {worst_m:.3f} of it",
          "verdict": f"MET -- every task's last step is below {SETTLED:.0%} of its first" if worst_f < SETTLED else
                     f"FALSIFIER FIRED -- a task is still moving at {worst_f:.2%} of its first step"}

    eligible = [(s, t, v) for s, t, v in rows if v["probe_gap"] is not None]
    gaps = [v["probe_gap"] for _, _, v in eligible]
    late = [v["probe_gap"] for _, _, v in eligible if v["probe_gap"] >= GAP]
    above = sum(1 for _, _, v in rows if v["probe_final"] - v["chance"] >= IN_PLACE)
    worst_gap = max(gaps) if gaps else None
    j4 = {"id": "T4", "measured": f"{above} of {len(rows)} tasks read above chance; worst midpoint-to-final gap "
                                  f"{'n/a' if worst_gap is None else f'{worst_gap:.4f}'} against a window of "
                                  f"{IN_PLACE:.2f} and a falsifier at {GAP:.2f}",
          "verdict": ("REFUSED -- no task reads above chance, so the read-out has nothing to be in place by"
                      if not above else
                      f"FALSIFIER FIRED -- {len(late)} task(s) gain {GAP:.2f} or more after the midpoint"
                      if late else
                      "MET -- every above-chance task is read at the midpoint to within the window"
                      if worst_gap <= IN_PLACE else
                      f"NULL -- the worst gap is {worst_gap:.4f}, between the window and the falsifier")}

    c = r.get("corpus", {})
    j5 = {"id": "T5", "measured": f"{c.get('artifacts', 0)} artifacts name {len(c.get('overlap_names', []))} "
                                  f"overlap-family and {len(c.get('assembly_names', []))} assembly-family task "
                                  f"names; unclassified {c.get('unclassified', [])}",
          "verdict": ("REFUSED -- the corpus was not scanned" if not c.get("scanned") else
                      "MET -- every corpus task is inside these two builders"
                      if not c.get("unclassified") else
                      f"FALSIFIER FIRED -- {c.get('unclassified')} belong to neither family")}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== does the trial's time axis carry anything? ==")
    print(f"   circuits {r['sizes']}, {len(r['scan'])} stimulus-shaped store(s) scanned")
    for site in r["scan"]:
        mark = "time = full slice" if site["time_is_full_slice"] else "TIME = VARIABLE"
        print(f"      {site['file']}:{site['line']}  ndim {site['ndim']}  {mark}")

    print("\n== T1, on the real circuit ==")
    for x in r["invariance"]:
        print(f"   {x['suite']:9} at {x['circuit']:20} ({x['n_tasks']} tasks)  worst |u[:,t]-u[:,0]| = "
              f"{x['worst']:g}")

    print("\n== T3 and T4, on the frozen network ==")
    print(f"   {'suite':9} {'task':14} {'last/first':>10} {'last/max':>9} {'first/max':>10} {'probe by step':>34}")
    for x in r["time_axis"]:
        for t, v in x["tasks"].items():
            curve = " ".join(f"{a:.2f}" for a in v["probe"])
            print(f"   {x['suite']:9} {t:14} {v['settled_fraction']:10.2e} {v['last_over_max']:9.3f} "
                  f"{v['first_over_max']:10.3f} {curve:>34}")
    for x in r["time_axis"]:
        first = next(iter(x["tasks"].items()))
        curve = " ".join(f"{s:.3e}" for s in first[1]["step_sizes"])
        print(f"   step sizes, {x['suite']}/{first[0]} at {x['circuit']}: {curve}")

    print("\n== T5, the corpus ==")
    c = r.get("corpus", {})
    print(f"   {c.get('artifacts', 0)} artifacts; assembly names {c.get('assembly_names', [])}; "
          f"overlap names {len(c.get('overlap_names', []))}; unclassified {c.get('unclassified', [])}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (a game needs the next input to depend on the last output, which is a stimulus that changes with")
    print("    time; this measures whether the suite can hold one before anything is built on it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", default="300,800", help="circuit sizes to measure, comma separated")
    ap.add_argument("--train", type=int, default=48)
    ap.add_argument("--test", type=int, default=24)
    ap.add_argument("--classes", type=int, default=4)
    ap.add_argument("--no-corpus", action="store_true", help="skip the scan of `runs/`")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(sizes=tuple(int(s) for s in args.sizes.split(",") if s.strip()),
                n_train=args.train, n_test=args.test, classes=args.classes, corpus=not args.no_corpus)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
