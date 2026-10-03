"""E379 -- what the body did: a closed-form probe on the **trained** body, which needs a run that keeps its weights.

`e374` read the action source at `cue@8` as chance and the frozen probe on the **untrained** body at that cell at
**0.7617**. `e375` froze the recurrent weights and recovered **0.2156 at 229.59 sigma**, `e376` priced the head's
step size at another **0.1965**, and `e377` showed that step size does nothing for a plastic body (**+0.0104 at 1.78
sigma**) while `e378` showed the same lever is worth **+0.2132** to the cue source. Every one of those readings is a
**diagonal** -- what a trained head reaches -- and none of them says what the body did to the world underneath it.
The runner can keep that body (`--save-theta`), and no unit has used it.

**This unit does.** It runs the same cell as `e377` -- the action source at `cue@8` with the head's step size at
`0.03`, twenty replicates, two arms -- with `--save-theta`, and then, for every replicate, every task and **both**
bodies, rolls the task's own examples through the saved recurrent weights and fits the corpus's own least-squares
probe on the world's final state. The **initial** body is saved alongside the trained ones, so the probe is read on
the same examples from the same world before and after the training, and the **saved head** is fitted to the same
roll so the reconstruction can be checked against the artifact rather than trusted.

Five claims, registered before the new run's reading was opened.

- **Z1 -- and the reconstruction is faithful.** For every replicate and every task, the accuracy of the **saved
  head** on the roll of the **saved body** equals the artifact's own per-replicate `learned` within **0.05**.
  **Falsifier**: any replicate and task where the two differ by more than that, which would say this unit is
  measuring a different dynamical system from the one that was trained and its other four claims are about that one.
  *This is the claim the other four rest on.*
- **Z2 -- and the initial body reproduces the curve's cell.** The probe on the initial body, on this unit's own roll
  of the tasks' examples, is within **0.10** of the **0.7617** that `e368` recorded for this cell at 512 examples in
  two halves. **Falsifier**: **0.15** apart, which would say the roll here is not the one the frozen grid read.
  **REFUSED** when that artifact is absent.
- **Z3 -- and the trained body still carries the cue.** The probe on the trained body reads at least **0.10** above
  chance. **Falsifier**: within **0.05** of chance, which would say the body's training **removed** the cue from the
  world rather than leaving it there to be read worse.
- **Z4 -- and it carries less than it did.** The initial body's probe exceeds the trained body's by at least
  **0.05**, paired over the twenty replicates. **Falsifier**: within **0.02**, which would say the body's training
  left the world's content where it was and the head is the whole of the loss. **Null**: between. Z3 and Z4 are the
  two halves of "what the body did": erased, or degraded.
- **Z5 -- and a probe on the trained body beats the trained head.** The trained body's probe exceeds the artifact's
  `learned` diagonal by at least **0.10**, paired. **Falsifier**: within **0.02**, which would say that on the body
  the run actually trained, nothing readable is left for the head to have missed. *This is the claim the
  readable-but-not-learnable thread has been asking for, on the body that was trained rather than on a frozen one.*

**What it can do beyond that.** It turns every diagonal in this window into a pair: what the trained head reached and
what a closed-form fit reached on the body the head was trained against. `e366` made this line price its example
counts and its arrangements; this makes it price its **reading**, which is the quantity every unit in the window has
compared across runs.

**What it cannot do.** *One cell and one draw*: `cue@8` on this draw, with the drive on the agent's own action, at
the corpus's own head and its larger step size -- so the probe here is read on a body trained for this cell and not
on the cue source's or another step's. *And a probe is not a decomposition*: it says how much of the label a linear
fit can recover from the world's eight numbers, not which directions the training moved or when during the run they
moved, and a body that has lost the label to a linear fit may still hold it nonlinearly. *And the initial body is
saved once*: `theta_initial` is the connectome's own weights, identical across replicates, so the before-and-after
comparison is paired in the examples and the seeds and not in the body.
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

SIZE = 300
READOUT_SIZE = 32
SEED0 = 0
LOOP_SYMBOLS = 4
N_TASKS = 3
N_TRAIN, N_TEST = 96, 48
TAU = 12
WORLD_DIMS = 8
CUE_STEP = 8
DRIVE_FROM_CUE = False
LR = 0.03
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
REPLICATES = 20
#: the run's artifact and the directory it wrote its weights into, both under the gitignored `runs/`
RUN = Path("runs/e379_earned_label_lr03_cue8_actionsource_20reps.json")
THETA = Path("runs/e379_theta")
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
CURVE_SOURCE, CURVE_STEP = "action", 8
FAMILY = 0.05
SAME = 0.10
FIRES = 0.15
LEARNS = 0.10
FLAT = 0.05
DEGRADES = 0.05
SHRANK = 0.02
READABLE = 0.10
CLAIMS = (
    ("Z1", f"and the reconstruction is faithful, within {FAMILY:.2f}",
     "For every replicate and task the saved head's accuracy on the roll of the saved body equals the artifact's "
     "own per-replicate `learned` within 0.05",
     "falsifier: any replicate and task differing by more than that"),
    ("Z2", f"and the initial body reproduces the curve's cell, within {SAME:.2f}",
     "The probe on the initial body is within 0.10 of the 0.7617 `e368` recorded for this cell",
     f"falsifier: {FIRES:.2f} apart; refused when that artifact is absent"),
    ("Z3", f"and the trained body still carries the cue, {LEARNS:.2f} over chance",
     "The probe on the trained body reads at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance, which would say the cue was removed rather than degraded"),
    ("Z4", f"and it carries less than it did, by {DEGRADES:.2f}",
     "The initial body's probe exceeds the trained body's by at least 0.05, paired over the replicates",
     f"falsifier: within {SHRANK:.2f}; null: between {SHRANK:.2f} and {DEGRADES:.2f}"),
    ("Z5", f"and a probe on the trained body beats the trained head, by {READABLE:.2f}",
     "The trained body's probe exceeds the artifact's `learned` diagonal by at least 0.10, paired",
     f"falsifier: within {SHRANK:.2f}, which would say nothing readable is left on the trained body"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def setup(size: int = SIZE, readout_size: int = READOUT_SIZE, seed0: int = SEED0):
    """The circuit, the read-out draw and the closed-loop suite, built the way the runner builds them."""
    from clfly.connectome import annotate, circuits, graph
    from clfly.network import env as fly_env
    from clfly.network import tasks as rate_tasks

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(seed0).choice(circ.n_neurons, size=readout_size, replace=False))
    loop_env = fly_env.build(circ, readout_subset=rs, seed=seed0, n_symbols=LOOP_SYMBOLS * N_TASKS, tau=TAU,
                             scale=1.0, gain=1.0, noise=1.0, world_modes=0, world_leak=0.35, world_dims=WORLD_DIMS,
                             world_coupled=True, cue_at=CUE_STEP, drive_from_cue=DRIVE_FROM_CUE)
    suite = [fly_env.make_env_task(loop_env, f"loop_{spec[0]}",
                                   symbols=range(i * LOOP_SYMBOLS, (i + 1) * LOOP_SYMBOLS),
                                   n_train=N_TRAIN, n_test=N_TEST, readout_neurons=rs,
                                   class_offset=i * LOOP_SYMBOLS, seed=i)
             for i, spec in enumerate(rate_tasks.SUITE_SPECS)]
    return circ, rs, loop_env, suite


def _roll(model, loop_env, u: np.ndarray) -> np.ndarray:
    import torch
    fn = loop_env.feedback()
    with torch.no_grad():
        model(torch.from_numpy(np.asarray(u, dtype=np.float32)), feedback=fn)
    return fn.last_world.detach().numpy()


def _set(model, theta, bias):
    import torch
    with torch.no_grad():
        model.theta.copy_(torch.from_numpy(np.asarray(theta, dtype=np.float32)))
        model.bias.copy_(torch.from_numpy(np.asarray(bias, dtype=np.float32)))


def _one_body(model, loop_env, task) -> tuple[float, float]:
    """The probe on this body and the world's spread, for one task, on that task's own examples."""
    u = np.concatenate([task.u_train, task.u_test])
    world = _roll(model, loop_env, u)
    tr, te = world[:N_TRAIN], world[N_TRAIN:]
    acc = float(probe(tr[:, None, :], task.y_train, te[:, None, :], task.y_test, list(range(WORLD_DIMS)))[-1])
    return acc, float(np.std(world))


def reading(run_path: Path = RUN, theta_dir: Path = THETA, curve: Path = CURVE) -> dict:
    import torch

    from clfly.network.model import RateConfig, build_net

    doc = load(run_path)
    if not doc:
        return {"ok": False, "reason": "the artifact is absent", "arms": {}, "present": False}
    circ, rs, loop_env, suite = setup(doc["config"].get("circuit_size", SIZE),
                                      doc.get("readout", {}).get("size", READOUT_SIZE),
                                      doc["config"].get("seed0", SEED0))
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()

    cells, heads, learned = {}, {}, {}
    for arm in ARMS:
        method = (doc.get("methods") or {}).get(arm) or {}
        reps = method.get("replicates") or []
        per_rep = {k: {"initial": [], "trained": [], "head": [], "recorded": [], "sd_initial": [], "sd_trained": []}
                   for k in range(N_TASKS)}
        for r, rec in enumerate(reps):
            seed = doc["config"].get("seed0", SEED0) + 100 * r
            path = Path(theta_dir) / f"{arm}_seed{seed}.npz"
            if not path.is_file():
                return {"ok": False, "reason": f"{path} is absent", "arms": {}, "present": False}
            z = np.load(path)
            for k, task in enumerate(suite):
                _set(model, z["theta_initial"], np.zeros(circ.n_neurons))
                init, sd_i = _one_body(model, loop_env, task)
                _set(model, z[f"after_task_{k}"], z[f"bias_after_task_{k}"])
                trained, sd_t = _one_body(model, loop_env, task)
                w = z[f"head_{k}_weight_after_task_{k}"]
                b = z[f"head_{k}_bias_after_task_{k}"]
                u = np.concatenate([task.u_train, task.u_test])
                world = _roll(model, loop_env, u)[N_TRAIN:]
                head = float(np.mean(np.argmax(world @ np.asarray(w).T + np.asarray(b), axis=1) == task.y_test))
                per_rep[k]["initial"].append(init)
                per_rep[k]["trained"].append(trained)
                per_rep[k]["head"].append(head)
                per_rep[k]["recorded"].append(float(rec["learned"][k]))
                per_rep[k]["sd_initial"].append(sd_i)
                per_rep[k]["sd_trained"].append(sd_t)
        cells[arm] = per_rep
        heads[arm] = {k: statistics.fmean(per_rep[k]["head"]) for k in range(N_TASKS)}
        learned[arm] = {k: statistics.fmean(per_rep[k]["recorded"]) for k in range(N_TASKS)}

    def _mean(arm, which):
        return statistics.fmean([statistics.fmean(cells[arm][k][which]) for k in range(N_TASKS)])

    out = {"ok": True, "arms": {}, "present": True, "run": Path(run_path).name,
           "theta_dir": str(Path(theta_dir)), "run_settings": {"size": circ.n_neurons, "readout": int(len(rs)),
                                                             "lr": doc["config"].get("lr"), "cue_at": CUE_STEP,
                                                             "replicates": len(doc["methods"][NAIVE]["replicates"])},
           "per_task": cells, "head_accuracy": heads, "recorded": learned,
           "curve": None, "spread_initial": _mean(NAIVE, "sd_initial"), "spread_trained": _mean(NAIVE, "sd_trained")}
    cdoc = load(curve)
    if cdoc:
        cell = (cdoc.get("cells") or {}).get(f"{CURVE_SOURCE}@{CURVE_STEP}")
        if cell:
            out["curve"] = {"artifact": Path(curve).name, "accuracy": float(cell["accuracy"]),
                            "world_sd": float(cell["world_sd"])}
    for arm in ARMS:
        init, trained = _mean(arm, "initial"), _mean(arm, "trained")
        out["arms"][arm] = {"initial_probe": init, "trained_probe": trained,
                            "head_accuracy": statistics.fmean(list(heads[arm].values())),
                            "recorded": statistics.fmean(list(learned[arm].values())),
                            "degradation": init - trained,
                            "readable_over_learned": trained - statistics.fmean(list(learned[arm].values()))}
    return out


def _paired(per_task_arm: dict, a: str, b: str) -> dict:
    """The paired difference of one quantity against another, over every replicate and task of one arm."""
    import math
    diffs = [x - y for k in sorted(per_task_arm) for x, y in zip(per_task_arm[k][a], per_task_arm[k][b])]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem}


def _sg(sigma) -> str:
    return "inf" if sigma is None else f"{sigma:.2f}"


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the run or its weights are absent"}
                for c in CLAIMS]

    #: an artifact on disk carries JSON's string keys where the in-memory reading carries the task indices,
    #: so both forms are normalized here rather than at every use
    per = {arm: {int(k): v for k, v in ((r.get("per_task") or {}).get(arm) or {}).items()} for arm in ARMS}
    worst, n_bad = 0.0, 0
    for arm in ARMS:
        for k in sorted(per[arm]):
            for a, b in zip(per[arm][k]["head"], per[arm][k]["recorded"]):
                if abs(a - b) > FAMILY:
                    n_bad += 1
                worst = max(worst, abs(a - b))
    z1 = {"id": "Z1", "measured": f"the saved head's accuracy against the artifact's own per-replicate `learned`, "
                                  f"over {len(ARMS) * N_TASKS * REPLICATES} replicate-tasks, differs by at most "
                                  f"{worst:.4f}, with {n_bad} outside {FAMILY:.2f}",
          "verdict": f"MET -- the reconstruction reproduces the trained head to {worst:.4f}" if not n_bad else
          f"FALSIFIER FIRED -- {n_bad} replicate-tasks differ by more than {FAMILY:.2f}: this unit is measuring a "
          f"different system from the one that was trained"}

    naive = r["arms"][NAIVE]
    fz = r.get("curve")
    if not fz:
        z2 = {"id": "Z2", "measured": "the curve has no cell for this step",
              "verdict": "REFUSED -- the artifact this licence comes from is absent"}
    else:
        gap = naive["initial_probe"] - fz["accuracy"]
        z2 = {"id": "Z2", "measured": f"the probe on the initial body reads {naive['initial_probe']:.4f} on this "
                                      f"unit's own roll of the tasks' examples and `{fz['artifact']}` records "
                                      f"{fz['accuracy']:.4f} for this cell at 512 examples, {gap:+.4f} apart",
              "verdict": f"MET -- the initial body reproduces the curve's cell to {gap:+.4f}" if abs(gap) < SAME
              else f"FALSIFIER FIRED -- {gap:+.4f} apart, so this roll is not the one the frozen grid read" if
              abs(gap) >= FIRES else
              f"NULL -- {gap:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    chance = 1.0 / LOOP_SYMBOLS
    above = naive["trained_probe"] - chance
    z3 = {"id": "Z3", "measured": f"the probe on the trained body reads {naive['trained_probe']:.4f} against a "
                                  f"chance of {chance:.2f}, {above:+.4f} above it, with the world's spread "
                                  f"{r['spread_trained']:.4f} against the initial body's "
                                  f"{r['spread_initial']:.4f}",
          "verdict": f"MET -- the trained body still carries the cue, {above:+.4f} over chance" if above >= LEARNS
          else f"FALSIFIER FIRED -- only {above:+.4f} over chance: the body's training removed the cue from the "
          f"world" if above < FLAT else
          f"NULL -- {above:+.4f}, between {FLAT:.2f} and {LEARNS:.2f}"}

    deg = _paired(per[NAIVE], "initial", "trained")
    if deg.get("delta") is None:
        z4 = {"id": "Z4", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two bodies do not pair"}
    else:
        z4 = {"id": "Z4", "measured": f"the initial body reads {naive['initial_probe']:.4f} and the trained one "
                                      f"{naive['trained_probe']:.4f}, so the training cost the world "
                                      f"{deg['delta']:+.4f} on a sem of {deg['sem']:.4f} over {deg['n']} paired "
                                      f"replicate-tasks",
              "verdict": f"MET -- the trained body carries less, by {deg['delta']:+.4f}" if deg["delta"] >= DEGRADES
              else f"FALSIFIER FIRED -- it carries {deg['delta']:+.4f} less: the world's content is where it was and "
              f"the head is the whole of the loss" if deg["delta"] < SHRANK else
              f"NULL -- {deg['delta']:+.4f}, between {SHRANK:.2f} and {DEGRADES:.2f}"}

    read = _paired(per[NAIVE], "trained", "recorded")
    if read.get("delta") is None:
        z5 = {"id": "Z5", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the probe and the recorded diagonal do not pair"}
    else:
        z5 = {"id": "Z5", "measured": f"the probe on the trained body reads {naive['trained_probe']:.4f} and the "
                                      f"trained head {naive['recorded']:.4f}, so {read['delta']:+.4f} is left on "
                                      f"the body the run actually trained, on a sem of {read['sem']:.4f} over "
                                      f"{read['n']} paired replicate-tasks",
              "verdict": f"MET -- a probe on the trained body beats the trained head by {read['delta']:+.4f}" if
              read["delta"] >= READABLE else
              f"FALSIFIER FIRED -- only {read['delta']:+.4f}: nothing readable is left on the trained body for the "
              f"head to have missed" if read["delta"] < SHRANK else
              f"NULL -- {read['delta']:+.4f}, between {SHRANK:.2f} and {READABLE:.2f}"}
    return [z1, z2, z3, z4, z5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== what the body did ==")
        print(f"   REFUSED -- {r.get('reason', 'the run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== what the body did ==")
    print(f"   `{r['run']}` with its weights in `{r['theta_dir']}`: the corpus's own probe on the world read off the "
          f"saved bodies, {r['run_settings']['replicates']} replicates, {N_TASKS} tasks, {N_TRAIN}/{N_TEST} examples")
    print(f"\n   {'arm':>7} {'initial':>9} {'trained':>9} {'head':>8} {'recorded':>9} {'degraded':>9} "
          f"{'readable':>9}")
    for arm in ARMS:
        a = r["arms"][arm]
        print(f"   {arm:>7} {a['initial_probe']:9.4f} {a['trained_probe']:9.4f} {a['head_accuracy']:8.4f} "
              f"{a['recorded']:9.4f} {a['degradation']:+9.4f} {a['readable_over_learned']:+9.4f}")
    print(f"   the world's spread: initial {r['spread_initial']:.4f}, trained {r['spread_trained']:.4f}")
    if r.get("curve"):
        print(f"   `{r['curve']['artifact']}` records {r['curve']['accuracy']:.4f} at 512 examples for this cell")

    print("\n== the registered claims, Z1-Z5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e374` to `e378` priced this cell by what a trained head reaches; the probe on the trained body is")
    print("    what says whether the world still holds the answer or the head cannot find what is there)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=RUN)
    ap.add_argument("--theta", type=Path, default=THETA)
    ap.add_argument("--curve", type=Path, default=CURVE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(run_path=args.run, theta_dir=args.theta, curve=args.curve)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
