"""E380 -- what the training built: a probe on the trained body at the wide step, where the trained head beats the
probe the frozen body was measured against.

`e379` read a probe on the **trained** body at `cue@8` and found the training had **removed** the cue from the world:
0.6597 before, **0.2361** after, and on the trained body the probe read exactly what the trained head read. That
answer is about the tight end of the window, and the wide end has the opposite sign in the record: `e371` trained the
same source at `cue@0` and its diagonal, **0.7691**, is **above** the **0.6602** that `e363`'s frozen grid read off
the **untrained** body at that cell. That comparison is across two bodies, like every other one in this window, and
it cannot say whether the training built a better representation or the head found more in the one that was there.

**This unit asks it the way `e379` did.** `e371`'s exact cell -- the action source at `cue@0`, the corpus's head, the
corpus's step size -- with `--save-theta`, and then, for every replicate and task, a roll of the saved recurrent
weights before training and after each task with the corpus's own probe fitted on the world each time.

Five claims, registered before the new run's reading was opened.

- **ZA1 -- and the reconstruction is faithful.** For every replicate and task the accuracy of the **saved head** on
  the roll of the **saved body** equals the artifact's own per-replicate `learned` within **0.05**. **Falsifier**:
  any replicate and task differing by more than that. *The other four rest on this.*
- **ZA2 -- and the initial body reproduces `e363`'s cell.** The probe on the initial body is within **0.10** of the
  **0.6602** that unit recorded for the action source at `cue@0`. **Falsifier**: **0.15** apart. **REFUSED** when
  that artifact is absent.
- **ZA3 -- and the trained body carries the cue.** The probe on the trained body reads at least **0.10** above
  chance. **Falsifier**: within **0.05** of chance, which at this step would say the training removed the cue from
  the wide end too.
- **ZA4 -- and the training put more of the cue there than was there before.** The trained body's probe exceeds the
  initial body's by at least **0.05**, paired over the replicates. **Falsifier**: within **0.02**, which would say
  the training changed nothing a linear probe can see at this step and `e371`'s gain over the frozen probe was a
  head effect. **Null**: between. *This is the claim the unit exists for.*
- **ZA5 -- and a probe on the trained body beats the trained head.** The trained body's probe exceeds the artifact's
  `learned` diagonal by at least **0.05**, paired. **Falsifier**: within **0.02**, which would say the head reaches
  everything the probe reaches. **Null**: between. `e379` found the opposite at the tight step -- the probe and the
  head agreeing on a body that held nothing -- so this is the same question at the other end of the window, and it
  is the one that says which of the two is the limit where the game can actually be played.

**What it can do beyond that.** With `e379` this makes the window's two ends a pair of the same measurement: what a
closed-form fit reaches on the body the run trained, at the step where nothing is left and at the step where a
trained head already beats the untrained body's probe.

**What it cannot do.** *One cell and one draw*: the action source at `cue@0` on this draw, so the cue source and the
steps between the two ends are not measured, and `e370` showed the boundary between them moves with the draw. *And a
probe is not a mechanism*: it says how much of the label a linear fit recovers from the world's eight numbers, and
not which directions the training moved, how fast, or whether what it built is a property of the drive population or
of the biases behind it. *And `--save-theta` writes one body per replicate and arm*, so what is compared is the body
at the end of each task's training and not the trajectory that produced it.
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
from experiments.e379_what_the_body_did import (  # noqa: F401  (the primitives are the same instrument)
    ARMS,
    N_TASKS,
    N_TEST,
    N_TRAIN,
    NAIVE,
    REPLAY,
    REPLICATES,
    TAU,
    WORLD_DIMS,
    _one_body,
    _paired,
    _roll,
    _set,
    _sg,
)

CUE_STEP = 0
#: the run's artifact and the directory it wrote its weights into, both under the gitignored `runs/`
RUN = Path("runs/e380_earned_label_cue0_actionsource_20reps.json")
THETA = Path("runs/e380_theta")
#: `e363`'s frozen grid, which holds the probe's reading for this cell on an **untrained** body
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
FROZEN_SOURCE, FROZEN_STEP = "action", 0
SIZE = 300
READOUT_SIZE = 32
SEED0 = 0
LOOP_SYMBOLS = 4
FAMILY = 0.05
SAME = 0.10
FIRES = 0.15
LEARNS = 0.10
FLAT = 0.05
BUILDS = 0.05
SHRANK = 0.02
CLAIMS = (
    ("ZA1", f"and the reconstruction is faithful, within {FAMILY:.2f}",
     "For every replicate and task the saved head's accuracy on the roll of the saved body equals the artifact's "
     "own per-replicate `learned` within 0.05",
     "falsifier: any replicate and task differing by more than that"),
    ("ZA2", f"and the initial body reproduces `e363`'s cell, within {SAME:.2f}",
     "The probe on the initial body is within 0.10 of the 0.6602 that unit recorded for this cell",
     f"falsifier: {FIRES:.2f} apart; refused when that artifact is absent"),
    ("ZA3", f"and the trained body carries the cue, {LEARNS:.2f} over chance",
     "The probe on the trained body reads at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance, which would say the wide end was emptied too"),
    ("ZA4", f"and the training put more of the cue there, by {BUILDS:.2f}",
     "The trained body's probe exceeds the initial body's by at least 0.05, paired over the replicates",
     f"falsifier: within {SHRANK:.2f}; null: between {SHRANK:.2f} and {BUILDS:.2f}"),
    ("ZA5", f"and a probe on the trained body beats the trained head, by {BUILDS:.2f}",
     "The trained body's probe exceeds the artifact's `learned` diagonal by at least 0.05, paired",
     f"falsifier: within {SHRANK:.2f}; null: between {SHRANK:.2f} and {BUILDS:.2f}"),
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
    """The circuit, the read-out draw and the closed-loop suite, at `cue@0` and otherwise as the runner builds them."""
    from clfly.connectome import annotate, circuits, graph
    from clfly.network import env as fly_env
    from clfly.network import tasks as rate_tasks

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(seed0).choice(circ.n_neurons, size=readout_size, replace=False))
    loop_env = fly_env.build(circ, readout_subset=rs, seed=seed0, n_symbols=LOOP_SYMBOLS * N_TASKS, tau=TAU,
                             scale=1.0, gain=1.0, noise=1.0, world_modes=0, world_leak=0.35, world_dims=WORLD_DIMS,
                             world_coupled=True, cue_at=CUE_STEP, drive_from_cue=False)
    suite = [fly_env.make_env_task(loop_env, f"loop_{spec[0]}",
                                   symbols=range(i * LOOP_SYMBOLS, (i + 1) * LOOP_SYMBOLS),
                                   n_train=N_TRAIN, n_test=N_TEST, readout_neurons=rs,
                                   class_offset=i * LOOP_SYMBOLS, seed=i)
             for i, spec in enumerate(rate_tasks.SUITE_SPECS)]
    return circ, rs, loop_env, suite


def frozen_cell(path: Path = FROZEN, source: str = FROZEN_SOURCE, step: int = FROZEN_STEP):
    doc = load(path)
    if not doc:
        return None
    for c in doc.get("cells") or []:
        if c.get("source") == source and c.get("cue_at") == step:
            return {"accuracy": float(c["accuracy"]), "world_sd": float(c["world_sd"]),
                    "artifact": Path(path).name}
    return None


def reading(run_path: Path = RUN, theta_dir: Path = THETA, frozen_path: Path = FROZEN) -> dict:
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
        reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
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
                w = np.asarray(z[f"head_{k}_weight_after_task_{k}"])
                b = np.asarray(z[f"head_{k}_bias_after_task_{k}"])
                world = _roll(model, loop_env, np.concatenate([task.u_train, task.u_test]))[N_TRAIN:]
                head = float(np.mean(np.argmax(world @ w.T + b, axis=1) == task.y_test))
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

    out = {"ok": True, "arms": {}, "present": True, "run": Path(run_path).name, "theta_dir": str(Path(theta_dir)),
           "run_settings": {"size": circ.n_neurons, "readout": int(len(rs)), "lr": doc["config"].get("lr"),
                            "cue_at": CUE_STEP, "replicates": len(doc["methods"][NAIVE]["replicates"])},
           "per_task": cells, "head_accuracy": heads, "recorded": learned,
           "frozen": None, "spread_initial": _mean(NAIVE, "sd_initial"), "spread_trained": _mean(NAIVE, "sd_trained")}
    out["frozen"] = frozen_cell(frozen_path)
    for arm in ARMS:
        init, trained = _mean(arm, "initial"), _mean(arm, "trained")
        rec = statistics.fmean(list(learned[arm].values()))
        out["arms"][arm] = {"initial_probe": init, "trained_probe": trained, "recorded": rec,
                            "head_accuracy": statistics.fmean(list(heads[arm].values())),
                            "built": trained - init, "readable_over_learned": trained - rec}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the run or its weights are absent"}
                for c in CLAIMS]

    per = {arm: {int(k): v for k, v in ((r.get("per_task") or {}).get(arm) or {}).items()} for arm in ARMS}
    worst, n_bad = 0.0, 0
    for arm in ARMS:
        for k in sorted(per[arm]):
            for a, b in zip(per[arm][k]["head"], per[arm][k]["recorded"]):
                if abs(a - b) > FAMILY:
                    n_bad += 1
                worst = max(worst, abs(a - b))
    za1 = {"id": "ZA1", "measured": f"the saved head's accuracy against the artifact's own per-replicate `learned`, "
                                    f"over {len(ARMS) * N_TASKS * REPLICATES} replicate-tasks, differs by at most "
                                    f"{worst:.4f}, with {n_bad} outside {FAMILY:.2f}",
           "verdict": f"MET -- the reconstruction reproduces the trained head to {worst:.4f}" if not n_bad else
           f"FALSIFIER FIRED -- {n_bad} replicate-tasks differ by more than {FAMILY:.2f}"}

    naive = r["arms"][NAIVE]
    fz = r.get("frozen")
    if not fz:
        za2 = {"id": "ZA2", "measured": "the frozen grid is not on disk",
               "verdict": "REFUSED -- the artifact this licence comes from is absent"}
    else:
        gap = naive["initial_probe"] - fz["accuracy"]
        za2 = {"id": "ZA2", "measured": f"the probe on the initial body reads {naive['initial_probe']:.4f} on this "
                                        f"unit's own roll of the tasks' examples and `{fz['artifact']}` records "
                                        f"{fz['accuracy']:.4f} for this cell, {gap:+.4f} apart",
               "verdict": f"MET -- the initial body reproduces that cell to {gap:+.4f}" if abs(gap) < SAME else
               f"FALSIFIER FIRED -- {gap:+.4f} apart" if abs(gap) >= FIRES else
               f"NULL -- {gap:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    chance = 1.0 / LOOP_SYMBOLS
    above = naive["trained_probe"] - chance
    za3 = {"id": "ZA3", "measured": f"the probe on the trained body reads {naive['trained_probe']:.4f} against a "
                                    f"chance of {chance:.2f}, {above:+.4f} above it, with the world's spread "
                                    f"{r['spread_trained']:.4f} against the initial body's "
                                    f"{r['spread_initial']:.4f}",
           "verdict": f"MET -- the trained body carries the cue, {above:+.4f} over chance" if above >= LEARNS else
           f"FALSIFIER FIRED -- only {above:+.4f} over chance: the wide end was emptied too" if above < FLAT else
           f"NULL -- {above:+.4f}, between {FLAT:.2f} and {LEARNS:.2f}"}

    built = _paired(per[NAIVE], "trained", "initial")
    if built.get("delta") is None:
        za4 = {"id": "ZA4", "measured": "the paired comparison was not computable",
               "verdict": "REFUSED -- the two bodies do not pair"}
    else:
        za4 = {"id": "ZA4", "measured": f"the initial body reads {naive['initial_probe']:.4f} and the trained one "
                                        f"{naive['trained_probe']:.4f}, so the training put "
                                        f"{built['delta']:+.4f} more of the cue into the world, on a sem of "
                                        f"{built['sem']:.4f} over {built['n']} paired replicate-tasks",
               "verdict": f"MET -- the training built the representation, by {built['delta']:+.4f}" if
               built["delta"] >= BUILDS else
               f"FALSIFIER FIRED -- it put {built['delta']:+.4f} there: the training changed nothing a probe can see "
               f"and `e371`'s gain was a head effect" if built["delta"] < SHRANK else
               f"NULL -- {built['delta']:+.4f}, between {SHRANK:.2f} and {BUILDS:.2f}"}

    read = _paired(per[NAIVE], "trained", "recorded")
    if read.get("delta") is None:
        za5 = {"id": "ZA5", "measured": "the paired comparison was not computable",
               "verdict": "REFUSED -- the probe and the recorded diagonal do not pair"}
    else:
        za5 = {"id": "ZA5", "measured": f"the probe on the trained body reads {naive['trained_probe']:.4f} and the "
                                        f"trained head {naive['recorded']:.4f}, so {read['delta']:+.4f} is left on "
                                        f"the body the run trained, on a sem of {read['sem']:.4f} over "
                                        f"{read['n']} paired replicate-tasks",
               "verdict": f"MET -- a probe on the trained body beats the trained head by {read['delta']:+.4f}" if
               read["delta"] >= BUILDS else
               f"FALSIFIER FIRED -- only {read['delta']:+.4f}: the head reaches everything the probe reaches" if
               read["delta"] < SHRANK else
               f"NULL -- {read['delta']:+.4f}, between {SHRANK:.2f} and {BUILDS:.2f}"}
    return [za1, za2, za3, za4, za5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== what the training built ==")
        print(f"   REFUSED -- {r.get('reason', 'the run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== what the training built ==")
    print(f"   `{r['run']}` at cue@{CUE_STEP} with its weights in `{r['theta_dir']}`: the corpus's own probe on the "
          f"world read off the saved bodies, {r['run_settings']['replicates']} replicates, {N_TASKS} tasks, "
          f"{N_TRAIN}/{N_TEST} examples")
    print(f"\n   {'arm':>7} {'initial':>9} {'trained':>9} {'head':>8} {'recorded':>9} {'built':>9} {'readable':>9}")
    for arm in ARMS:
        a = r["arms"][arm]
        print(f"   {arm:>7} {a['initial_probe']:9.4f} {a['trained_probe']:9.4f} {a['head_accuracy']:8.4f} "
              f"{a['recorded']:9.4f} {a['built']:+9.4f} {a['readable_over_learned']:+9.4f}")
    print(f"   the world's spread: initial {r['spread_initial']:.4f}, trained {r['spread_trained']:.4f}")
    if r.get("frozen"):
        print(f"   `{r['frozen']['artifact']}` records {r['frozen']['accuracy']:.4f} for this cell on an untrained "
              f"body")

    print("\n== the registered claims, ZA1-ZA5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e379` read a probe on the trained body at cue@8 and found nothing left there; this asks the same")
    print("    question at the wide step, where a trained head already beats the untrained body's probe)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=RUN)
    ap.add_argument("--theta", type=Path, default=THETA)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(run_path=args.run, theta_dir=args.theta, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
