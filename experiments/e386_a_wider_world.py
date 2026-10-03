"""E386 -- a wider world at the tight step: does the read-out's width survive the collapse that one update causes?

`e379` froze the tight step's body and `e382` showed the whole loss in **one** gradient step: the connectome's own
weights carry task 0 at **0.6875** where one update at `cue@8` leaves **0.2083**. `e286` names the read-out's width
as the real variable behind this line's spread, and the world *is* the read-out here -- with `--readout-from-world`
the head reads the world's numbers -- so widening the world widens the read-out, and the question this unit asks is
whether that changes what the update costs.

**This unit runs the same cell with `--loop-world-dims 32`.** Everything else is `e379`'s: the action source, the
cue's step, the corpus's larger rate, twenty replicates, and the body kept, so the corpus's own probe can be fitted
on the world before training and after each task exactly as `e379` and `e381` did it.

Five claims, registered before the new run's reading was opened.

- **G1 -- one configuration except the world's dimension.** The run agrees with `e379`'s on the circuit, the tasks
  and their widths, the basis, the read-out draw, the seed stream, the replicate count, the iteration budget, the
  rate, the batch, the leak, the coupling flag, the cue's step, the drive's source and its seven fields and the
  controllability flags -- differing in `loop_world_dims`, and in the draws that follow from it: the drive map, the
  read map and the coupling matrix, whose widths and consumption move with the dimension, which is the pattern
  `e367`'s T1 registered. **Falsifier**: any other field differing.
- **G2 -- and the wider world is live at this step.** The probe on the initial body, on task 0's examples, reads at
  least **0.10** above chance. **Falsifier**: within **0.05**. **REFUSED** when the artifact or the weights are
  absent. *The licence: without a live channel there is nothing for the update to destroy.*
- **G3 -- and a wider read-out survives the collapse.** The probe on the trained body reads at least **0.10** above
  chance. **Falsifier**: within **0.05**, which would say the collapse is not about the read-out's width -- the
  update takes the label out of a 32-number world as completely as out of an 8-number one. **Null**: between. *This is
  the claim the unit exists for.*
- **G4 -- and it beats the narrow world's floor.** The trained body's probe exceeds `e379`'s reading for the
  eight-dimensional world at this cell (**0.2361**) by at least **0.10**. **Falsifier**: within **0.05** of it.
  **Null**: between. **REFUSED** when that artifact is absent.
- **G5 -- and the head tracks the world down here too.** The trained head's own accuracy for task 0 is within
  **0.05** of the probe on the trained body. **Falsifier**: **0.10** apart, which would say a wider read-out gives
  the head something the probe cannot reach, or the reverse.

**What it can do beyond that.** `e286`'s read-out axis has been a property of this corpus's *decoders*; here it is a
property of the **world the agent acts in**, which is the axis a game is designed on, and the two ends of the window
now have a width beside them as well as a step.

**What it cannot do.** *One width against one other*: eight dimensions against thirty-two, so a monotone trend is
not established and a third width is a run of its own. *And the draws follow the manipulation*: the drive map, the
read map and the coupling matrix all change with the dimension, so the comparison is between two worlds and not
between one world read two ways -- the same limit `e363`'s source manipulation had. *One cell, one source, one draw*:
the action source at `cue@8` with the corpus's larger rate, so the wide end and the cue source are not compared at
this width. *And a probe is not a mechanism*: a reading above chance says a linear fit recovers some of the label
from the world's thirty-two numbers, not that the body kept it there.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e379_what_the_body_did import _roll, _set
from experiments.e379_what_the_body_did import N_TASKS, NAIVE, TAU  # noqa: F401  (the same instrument)

#: the run this unit made, its weights, and `e379`'s reading for the eight-dimensional world at the same cell
RUN = Path("runs/e386_earned_label_dims32_cue8_actionsource_20reps.json")
THETA = Path("runs/e386_theta")
REFERENCE = Path("runs/e379_what_the_body_did.json")
DIMS = 32
REPLICATES = 20
SAME = 0.05
FIRES = 0.10
LEARNS = 0.10
#: the fields the dimension moves: the drive map, the read map and the coupling matrix all widen with it
FOLLOWS_FROM_THE_DIMENSION = ("world_drive_sha1", "world_read_sha1", "world_coupling_sha1", "loop_world_dims")
CLAIMS = (
    ("G1", "one configuration except the world's dimension",
     "Every recorded field agrees with `e379`'s except `loop_world_dims` and the three world draws whose widths "
     "follow from it",
     "falsifier: any other field differing"),
    ("G2", f"and the wider world is live at this step, {LEARNS:.2f} over chance",
     "The probe on the initial body reads at least 0.10 above chance",
     f"falsifier: within {SAME:.2f}; refused when the artifact or the weights are absent"),
    ("G3", f"and a wider read-out survives the collapse, {LEARNS:.2f} over chance",
     "The probe on the trained body reads at least 0.10 above chance",
     f"falsifier: within {SAME:.2f} of chance; null: between"),
    ("G4", f"and it beats the narrow world's floor, by {FIRES:.2f}",
     "The trained body's probe exceeds `e379`'s 0.2361 for the eight-dimensional world by at least 0.10",
     f"falsifier: within {SAME:.2f} of it; refused when that artifact is absent"),
    ("G5", f"and the head tracks the world down here too, within {SAME:.2f}",
     "The trained head's accuracy for task 0 is within 0.05 of the probe on the trained body",
     f"falsifier: {FIRES:.2f} apart"),
)


def setup(dims: int = DIMS, size: int = 300, readout_size: int = 32, seed0: int = 0):
    """The circuit, the read-out draw and the closed-loop suite at `cue@8`, at `dims` world dimensions.

    `e379`'s own setup fixes the dimension at eight, and its roll fits the probe on the first eight columns, so this
    unit carries its own pair rather than borrowing one that would read a thirty-two-number world through eight of
    them.
    """
    from clfly.connectome import annotate, circuits, graph
    from clfly.network import env as fly_env
    from clfly.network import tasks as rate_tasks

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(seed0).choice(circ.n_neurons, size=readout_size, replace=False))
    loop_env = fly_env.build(circ, readout_subset=rs, seed=seed0, n_symbols=4 * N_TASKS, tau=TAU,
                             scale=1.0, gain=1.0, noise=1.0, world_modes=0, world_leak=0.35, world_dims=dims,
                             world_coupled=True, cue_at=8, drive_from_cue=False)
    suite = [fly_env.make_env_task(loop_env, f"loop_{spec[0]}",
                                   symbols=range(i * 4, (i + 1) * 4), n_train=96, n_test=48,
                                   readout_neurons=rs, class_offset=i * 4, seed=i)
             for i, spec in enumerate(rate_tasks.SUITE_SPECS)]
    return circ, rs, loop_env, suite


def probe_cells(doc: dict, theta_dir: Path, dims: int, arm: str, reps: int) -> dict:
    """The probe on the initial and the after-task-0 bodies, for every task, per replicate."""
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup(dims)
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    cell = {(c, k): [] for c in ("initial", "after_task_0") for k in range(N_TASKS)}
    for r, _ in enumerate(((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []):
        if r >= reps:
            break
        seed = doc["config"].get("seed0", 0) + 100 * r
        path = Path(theta_dir) / f"{arm}_seed{seed}.npz"
        if not path.is_file():
            return {"ok": False, "reason": f"{path} is absent"}
        z = np.load(path)
        for k, task in enumerate(tasks):
            for c in ("initial", "after_task_0"):
                key = "theta_initial" if c == "initial" else "after_task_0"
                bias = np.zeros(circ.n_neurons) if c == "initial" else z["bias_after_task_0"]
                _set(model, z[key], bias)
                u = np.concatenate([task.u_train, task.u_test])
                world = _roll(model, loop_env, u)
                tr, te = world[:96], world[96:]
                acc = float(probe(tr[:, None, :], task.y_train, te[:, None, :], task.y_test, list(range(dims)))[-1])
                cell[(c, k)].append(acc)
    return {"ok": True, "cell": cell}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(run_path: Path = RUN, theta_dir: Path = THETA, reference: Path = REFERENCE,
            arm: str = NAIVE, reps: int = REPLICATES) -> dict:
    from clfly.network.model import RateConfig, build_net

    doc = load(run_path)
    if not doc:
        return {"ok": False, "reason": "the artifact is absent", "cells": {}, "present": False}
    dims = int(doc["config"].get("loop_world_dims", DIMS))
    got = probe_cells(doc, theta_dir, dims, arm, reps)
    if not got.get("ok"):
        return {"ok": False, "reason": got["reason"], "cells": {}, "present": False}
    cell = got["cell"]
    out = {"ok": True, "present": True, "reason": None, "run": Path(run_path).name, "arm": arm, "reps": reps,
           "dims": dims, "readout": doc.get("readout", {}).get("size"),
           "probe_initial_task_0": statistics.fmean(cell[("initial", 0)]),
           "probe_trained_task_0": statistics.fmean(cell[("after_task_0", 0)]),
           "probe_initial_mean": statistics.fmean([statistics.fmean(cell[("initial", k)]) for k in range(N_TASKS)]),
           "probe_trained_mean": statistics.fmean([statistics.fmean(cell[("after_task_0", k)])
                                                   for k in range(N_TASKS)]),
           "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0]),
           "head_mean": float(statistics.fmean(doc["methods"][arm]["replicates"][0]["learned"])),
           "reference_facts": None,
           "facts": {**_facts(doc), "loop_world_dims": doc["config"].get("loop_world_dims"),
                     "lr": doc["config"].get("lr"), "batch": doc["config"].get("batch")},
           "cells": {f"{c}|{k}": v for (c, k), v in cell.items()}, "reference": None}
    ref_doc = load(Path("runs/e379_earned_label_lr03_cue8_actionsource_20reps.json"))
    if ref_doc:
        out["reference_facts"] = {**_facts(ref_doc),
                                  "loop_world_dims": ref_doc["config"].get("loop_world_dims"),
                                  "lr": ref_doc["config"].get("lr"), "batch": ref_doc["config"].get("batch")}
    ref = load(reference)
    if ref:
        rnaive = (ref.get("arms") or {}).get(arm) or {}
        out["reference"] = {"artifact": Path(reference).name,
                            "trained_probe": rnaive.get("trained_probe"),
                            "initial_probe": rnaive.get("initial_probe")}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the run or its weights are absent"}
                for c in CLAIMS]
    facts = r["facts"]
    keys = ("lr", "batch") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    #: the reference's own facts, carried in the reading from the artifact that holds them, so the check is against
    #: the run `e379` wrote and not against a remembered list
    ref_facts = r.get("reference_facts")
    differ = {}
    if ref_facts is not None:
        for k in keys:
            if facts.get(k) != ref_facts.get(k):
                differ[k] = [facts.get(k), ref_facts.get(k)]
    follows = sorted(k for k in differ if k in FOLLOWS_FROM_THE_DIMENSION or k == "world_drive_sha1"
                     or k == "world_read_sha1" or k == "world_coupling_sha1")
    other = sorted(k for k in differ if k not in follows)
    bad = [k for k in other if k != "repeats"]
    j1 = {"id": "G1", "measured": f"the fields differing from `e379`'s run: {sorted(differ)}, of which the ones the "
                                  f"dimension moves are {follows} and the others {other}; the world's dimension is "
                                  f"{r['dims']} against that run's 8, the read-out draw is "
                                  f"{r['readout']} neurons in both",
          "verdict": "MET -- one configuration except the dimension and the draws that follow it" if not bad else
          f"FALSIFIER FIRED -- {bad} differ and do not follow from the dimension"}

    chance = 1.0 / 4
    above = r["probe_initial_task_0"] - chance
    j2 = {"id": "G2", "measured": f"the connectome's own weights read {r['probe_initial_task_0']:.4f} on task 0's "
                                  f"examples against a chance of {chance:.2f}, {above:+.4f} above it",
          "verdict": f"MET -- the wider world is live at this step, {above:+.4f} over chance" if above >= LEARNS
          else f"FALSIFIER FIRED -- only {above:+.4f} over chance: the wider world is not live here" if above < SAME
          else f"NULL -- {above:+.4f}, between {SAME:.2f} and {LEARNS:.2f}"}

    kept = r["probe_trained_task_0"] - chance
    j3 = {"id": "G3", "measured": f"the probe on the trained body reads {r['probe_trained_task_0']:.4f} against a "
                                  f"chance of {chance:.2f}, {kept:+.4f} above it, where the connectome's own "
                                  f"weights read {r['probe_initial_task_0']:.4f}",
          "verdict": f"MET -- a wider read-out survives the collapse, {kept:+.4f} over chance" if kept >= LEARNS
          else f"FALSIFIER FIRED -- only {kept:+.4f} over chance: the update empties a wider world too" if
          kept < SAME else f"NULL -- {kept:+.4f}, between {SAME:.2f} and {LEARNS:.2f}"}

    ref = r.get("reference")
    if not ref or ref.get("trained_probe") is None:
        j4 = {"id": "G4", "measured": "the reference artifact or its reading is absent",
              "verdict": "REFUSED -- the narrow world's floor is not on disk"}
    else:
        gain = r["probe_trained_task_0"] - float(ref["trained_probe"])
        j4 = {"id": "G4", "measured": f"the trained body reads {r['probe_trained_task_0']:.4f} at "
                                      f"{r['dims']} dimensions and `{ref['artifact']}` records "
                                      f"{float(ref['trained_probe']):.4f} at 8, so the wider world is "
                                      f"{gain:+.4f}",
              "verdict": f"MET -- the wider read-out beats the narrow world's floor, {gain:+.4f}" if gain >= FIRES
              else f"FALSIFIER FIRED -- only {gain:+.4f}: the width does not change the floor" if gain < SAME else
              f"NULL -- {gain:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    gap = r["probe_trained_task_0"] - r["head_task_0"]
    j5 = {"id": "G5", "measured": f"the probe on the trained body reads {r['probe_trained_task_0']:.4f} and the "
                                  f"trained head {r['head_task_0']:.4f}, {gap:+.4f} apart",
          "verdict": f"MET -- the head tracks the world down here too, {gap:+.4f}" if abs(gap) < SAME else
          f"FALSIFIER FIRED -- {gap:+.4f} apart at this width"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== a wider world at the tight step ==")
        print(f"   REFUSED -- {r.get('reason', 'the run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== a wider world at the tight step ==")
    print(f"   `{r['run']}` at {r['dims']} world dimensions, the body after task 0 read with the corpus's own probe, "
          f"{r['reps']} replicates on the `{r['arm']}` arm")
    print(f"\n   {'cell':>16} {'task 0':>9} {'mean over tasks':>16}")
    print(f"   {'connectome':>16} {r['probe_initial_task_0']:9.4f} {r['probe_initial_mean']:16.4f}")
    print(f"   {'after task 0':>16} {r['probe_trained_task_0']:9.4f} {r['probe_trained_mean']:16.4f}")
    print(f"   {'trained head':>16} {r['head_task_0']:9.4f} {r['head_mean']:16.4f}")
    if r.get("reference"):
        print(f"   the eight-dimensional world at this cell reads {float(r['reference']['trained_probe']):.4f} "
              f"trained against {float(r['reference']['initial_probe']):.4f} on its own connectome weights "
              f"(`{r['reference']['artifact']}`)")

    print("\n== the registered claims, G1-G5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e382` found the tight step's whole loss in one update and `e286` names the read-out's width as")
    print("    this line's real variable; here the world is the read-out, and this widens it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=REPLICATES)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(reps=args.reps)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
