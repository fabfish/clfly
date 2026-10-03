"""E381 -- the representation's retention matrix: what the world still holds after each task, from the bodies two
units already saved.

`e379` and `e380` each kept the body their run trained (`--save-theta`) and read a closed-form probe on it before
training and after each task. Both read **one column** of what those weights hold: the task the body had just been
trained on. The saved files carry the body at **every** task's end, so the other two columns are on disk already,
and together they are the thing this corpus spends its whole continual-learning line measuring -- a **retention
matrix** -- except read on the world instead of through the head.

**This unit rolls them.** No new run: for both saved runs, every arm, every replicate and all four checkpoints (the
connectome's own weights and then the body after each of the three tasks), it rolls **every** task's own examples and
fits the corpus's probe on the world's final state. That is a 4 by 3 matrix of readings per arm, and the artifact's
own `retention` block is the same matrix as the **head** saw it, so the two can be put side by side on the same
replicates.

Five claims, registered before any of these cells was opened in this unit.

- **R1 -- and the diagonal is what the two units recorded.** For both runs the representation matrix's diagonal --
  the probe on the body after task `k`, on task `k`'s examples -- is within **0.02** of the trained-body reading that
  `e379` and `e380` wrote into their artifacts. **Falsifier**: **0.05** apart, which would say this unit's roll is
  not the one those units read and its other four claims are about a different instrument. **REFUSED** when either
  of those artifacts is absent.
- **R2 -- and the representation forgets.** On the wide step's run, task 0 reads at least **0.10** higher on the body
  after task 0 than on the body after task 2, paired over the twenty replicates. **Falsifier**: within **0.05**,
  which would say the world keeps a task's cue through two more tasks of training. **Null**: between. *This is the
  claim the unit exists for.*
- **R3 -- and the world forgets at least what the head forgets.** On the same run and task, the representation's drop
  is no more than **0.10 smaller** than the head's own drop from the artifact's `retention` block, paired over the
  replicates. **Falsifier**: the representation's drop being **0.15 or more smaller**, which would say the head
  loses something the world still holds. **Null**: between **0.10** and **0.15**.
- **R4 -- and at the tight step there is nothing to forget.** On the tight step's run, task 0's reading on the body
  after task 2 is within **0.05** of its reading on the body after task 0, paired. **Falsifier**: **0.10** apart,
  which would say a step whose diagonal is chance still has a task-0 representation to lose. **Null**: between.
- **R5 -- and the buffer changes the world's forgetting.** On the wide step's run, the drop under `replay` is at
  least **0.05** smaller than under `naive`, paired. **Falsifier**: `replay`'s drop larger by **0.05** or more.
  **Null**: between. This is the buffer read on the representation rather than on the head, which is where `e375` to
  `e380` put the interesting differences in this window.

**What it can do beyond that.** It makes the window's forgetting measurable in the same currency as its levels. Every
diagonal this line has compared was a head's reading; here the same bodies give a matrix, and the head's own matrix
is in the artifact beside it, so "where the forgetting is" becomes a comparison of two matrices on the same
replicates instead of a claim about a mechanism.

**What it cannot do.** *Two cells, one draw*: the action source at `cue@0` and at `cue@8` on this draw, so the cue
source and the steps between them are not measured and `e370` showed the boundary moves with the draw. *And a probe
is not a mechanism*: a cell of this matrix says how much of a task's label a linear fit recovers from the world's
eight numbers at that point in the sequence, not which directions moved, and a label a linear fit cannot reach is not
thereby absent. *And four checkpoints are four**: the bodies are kept at task boundaries, so nothing here says how
the world moved inside a task's training, which would need a runner that saves intermediate iterations.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e379_what_the_body_did import (  # noqa: F401  (the primitives are the same instrument)
    ARMS,
    N_TASKS,
    NAIVE,
    REPLAY,
    REPLICATES,
    TAU,
    _one_body,
    _paired,
    _roll,
    _set,
    _sg,
)
from experiments.e379_what_the_body_did import setup as setup_tight
from experiments.e380_what_the_training_built import setup as setup_wide

#: the two runs whose bodies are on disk, with the reader each one's diagonal was recorded in
RUNS = {
    "wide": {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
             "theta": Path("runs/e380_theta"), "reader": Path("runs/e380_what_the_training_built.json"),
             "cue_at": 0},
    "tight": {"run": Path("runs/e379_earned_label_lr03_cue8_actionsource_20reps.json"),
              "theta": Path("runs/e379_theta"), "reader": Path("runs/e379_what_the_body_did.json"),
              "cue_at": 8},
}
CHECKPOINTS = ("initial", "after_task_0", "after_task_1", "after_task_2")
SAME = 0.02
FIRES = 0.05
FORGETS = 0.10
FLAT = 0.05
ROCKS = 0.05
SHRINKS = 0.05
STABLE = 0.05
CLAIMS = (
    ("R1", f"and the diagonal is what the two units recorded, within {SAME:.2f}",
     "For both runs the representation matrix's diagonal is within 0.02 of the trained-body reading those units "
     "wrote into their artifacts",
     f"falsifier: {FIRES:.2f} apart; refused when either artifact is absent"),
    ("R2", f"and the representation forgets, by {FORGETS:.2f}",
     "On the wide step's run, task 0 reads at least 0.10 higher after task 0 than after task 2, paired",
     f"falsifier: within {FLAT:.2f}; null: between {FLAT:.2f} and {FORGETS:.2f}"),
    ("R3", f"and the world forgets at least what the head forgets, within {FORGETS:.2f}",
     "The representation's drop is no more than 0.10 smaller than the head's own drop from the artifact's `retention` "
     "block, paired over the replicates",
     f"falsifier: the representation's drop 0.15 or more smaller; null: between 0.10 and 0.15"),
    ("R4", f"and at the tight step there is nothing to forget, within {STABLE:.2f}",
     "On the tight step's run, task 0's reading after task 2 is within 0.05 of its reading after task 0, paired",
     f"falsifier: {FORGETS:.2f} apart; null: between {STABLE:.2f} and {FORGETS:.2f}"),
    ("R5", f"and the buffer changes the world's forgetting, by {SHRINKS:.2f}",
     "On the wide step's run the drop under `replay` is at least 0.05 smaller than under `naive`, paired",
     f"falsifier: `replay`'s drop larger by {ROCKS:.2f} or more; null: between"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def matrix(theta_dir: Path, doc: dict, arm: str, tasks, model, loop_env, n_neurons: int) -> dict:
    """The 4 by 3 readings: every checkpoint against every task, per replicate."""
    cell = {(c, k): [] for c in CHECKPOINTS for k in range(len(tasks))}
    for r, _ in enumerate(((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []):
        seed = doc["config"].get("seed0", 0) + 100 * r
        path = Path(theta_dir) / f"{arm}_seed{seed}.npz"
        if not path.is_file():
            return {}
        z = np.load(path)
        for k, task in enumerate(tasks):
            for c in CHECKPOINTS:
                key = "theta_initial" if c == "initial" else c
                bias = np.zeros(n_neurons) if c == "initial" else z[f"bias_{c}"]
                _set(model, z[key], bias)
                acc, _ = _one_body(model, loop_env, task)
                cell[(c, k)].append(acc)
    return cell


def reading(runs: dict = RUNS) -> dict:
    from clfly.network.model import RateConfig, build_net

    out = {"ok": True, "reason": None, "runs": {}, "present": True}
    for name, spec in runs.items():
        doc = load(spec["run"])
        reader = load(spec["reader"])
        if not doc or not reader:
            return {"ok": False, "present": False, "runs": {},
                    "reason": f"{name}: the run or its reader is absent"}
        circ, rs, loop_env, tasks = (setup_wide() if spec["cue_at"] == 0 else setup_tight())
        model = build_net(circ, RateConfig(tau=TAU)).torch_model()
        entry = {"cue_at": spec["cue_at"], "run": spec["run"].name, "reader": spec["reader"].name,
                 "replicates": len(doc["methods"][NAIVE]["replicates"]), "arms": {}, "head": {}, "head_rows": {},
                 "recorded": {}}
        for arm in ARMS:
            entry["arms"][arm] = {f"{c}|{k}": v for (c, k), v in
                                  matrix(spec["theta"], doc, arm, tasks, model, loop_env, circ.n_neurons).items()}
            if not entry["arms"][arm]:
                return {"ok": False, "present": False, "runs": {}, "reason": f"{name}: the weights are absent"}
            entry["head"][arm] = [[None if x is None else float(x) for x in row]
                                  for row in doc["methods"][arm]["replicates"][0]["retention"]]
            #: keyed by arm: assigning this per arm without a key leaves the last arm's rows behind for every
            #: reader of the field, which is how this unit's first reading compared the world against the wrong head
            entry["head_rows"][arm] = [[[float(x) if x is not None else None for x in rep["retention"][j]]
                                        for rep in doc["methods"][arm]["replicates"]] for j in range(N_TASKS)]
        entry["recorded"] = {"naive": (reader.get("arms") or {}).get(NAIVE, {}).get("trained_probe"),
                             "replay": (reader.get("arms") or {}).get(REPLAY, {}).get("trained_probe")}
        out["runs"][name] = entry
    return out


def _drop(entry: dict, arm: str, k: int, frm: str = "after_task_0", to: str = "after_task_2") -> list[float]:
    a = entry["arms"][arm][f"{frm}|{k}"]
    b = entry["arms"][arm][f"{to}|{k}"]
    return [x - y for x, y in zip(a, b)]


def _paired_list(diffs: list[float]) -> dict:
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / (len(diffs) ** 0.5)
    return {"n": len(diffs), "delta": mean, "sem": sem}


def _head_drop(entry: dict, arm: str, k: int) -> list[float]:
    """The head's own drop for task k: its reading when learned against the last checkpoint's."""
    rows = entry["head_rows"][arm]
    last = N_TASKS - 1
    return [row[k] - rows[last][i][k] for i, row in enumerate(rows[k])]


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the runs or their weights are absent"}
                for c in CLAIMS]
    wide, tight = r["runs"]["wide"], r["runs"]["tight"]

    gaps = {}
    for name, entry in (("wide", wide), ("tight", tight)):
        rec = entry["recorded"].get(NAIVE)
        if rec is None:
            gaps[name] = None
            continue
        diag = [statistics.fmean(entry["arms"][NAIVE][f"after_task_{k}|{k}"]) for k in range(N_TASKS)]
        gaps[name] = statistics.fmean(diag) - float(rec)
    if any(v is None for v in gaps.values()):
        j1 = {"id": "R1", "measured": f"the readers behind these runs are missing: {gaps}",
              "verdict": "REFUSED -- a reader artifact is absent"}
    else:
        worst = max(abs(v) for v in gaps.values())
        j1 = {"id": "R1", "measured": f"the diagonal against the reading each unit recorded: wide "
                                      f"{gaps['wide']:+.4f} and tight {gaps['tight']:+.4f}, at most {worst:.4f} "
                                      f"apart",
              "verdict": f"MET -- the diagonal is those units' own reading, to {worst:.4f}" if worst < SAME else
              f"FALSIFIER FIRED -- {worst:.4f} apart, so this roll is not the one they read" if worst >= FIRES else
              f"NULL -- {worst:.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    drop = _paired_list(_drop(wide, NAIVE, 0))
    if drop.get("delta") is None:
        j2 = {"id": "R2", "measured": "the paired drop was not computable",
              "verdict": "REFUSED -- the two checkpoints do not pair"}
    else:
        after0 = statistics.fmean(wide["arms"][NAIVE]["after_task_0|0"])
        after2 = statistics.fmean(wide["arms"][NAIVE]["after_task_2|0"])
        j2 = {"id": "R2", "measured": f"on the wide step task 0 reads {after0:.4f} on the body after task 0 and "
                                      f"{after2:.4f} after task 2, so the world lost {drop['delta']:+.4f} on a sem "
                                      f"of {drop['sem']:.4f} over {drop['n']} paired replicates",
              "verdict": f"MET -- the representation forgets, by {drop['delta']:+.4f}" if drop["delta"] >= FORGETS
              else f"FALSIFIER FIRED -- {drop['delta']:+.4f}: the world keeps a task's cue through two more" if
              drop["delta"] < FLAT else
              f"NULL -- {drop['delta']:+.4f}, between {FLAT:.2f} and {FORGETS:.2f}"}

    head = _head_drop(wide, NAIVE, 0)
    if drop.get("delta") is None or not head:
        j3 = {"id": "R3", "measured": "the two drops are not both computable",
              "verdict": "REFUSED -- the comparison this claim makes is not computable"}
    else:
        diff = _paired_list([a - b for a, b in zip(_drop(wide, NAIVE, 0), head)])
        j3 = {"id": "R3", "measured": f"task 0 lost {drop['delta']:+.4f} in the world and "
                                      f"{statistics.fmean(head):+.4f} to the head, so the world's drop is "
                                      f"{diff['delta']:+.4f} against the head's, on a sem of {diff['sem']:.4f}",
              "verdict": f"MET -- the world forgets at least what the head forgets, {diff['delta']:+.4f}" if
              diff["delta"] >= -FORGETS else
              f"FALSIFIER FIRED -- the world loses {abs(diff['delta']):.4f} less than the head: the head forgets "
              f"something the world still holds" if diff["delta"] <= -0.15 else
              f"NULL -- {diff['delta']:+.4f}, between -0.15 and -0.10"}

    tdrop = _paired_list(_drop(tight, NAIVE, 0))
    if tdrop.get("delta") is None:
        j4 = {"id": "R4", "measured": "the paired drop was not computable",
              "verdict": "REFUSED -- the two checkpoints do not pair"}
    else:
        j4 = {"id": "R4", "measured": f"on the tight step task 0 reads "
                                      f"{statistics.fmean(tight['arms'][NAIVE]['after_task_0|0']):.4f} after task 0 "
                                      f"and {statistics.fmean(tight['arms'][NAIVE]['after_task_2|0']):.4f} after task "
                                      f"2, a change of {tdrop['delta']:+.4f} on a sem of {tdrop['sem']:.4f}",
              "verdict": f"MET -- nothing to forget at the tight step, {tdrop['delta']:+.4f} either way" if
              abs(tdrop["delta"]) < STABLE else
              f"FALSIFIER FIRED -- {tdrop['delta']:+.4f} apart: a step whose diagonal is chance still moves its "
              f"task-0 representation" if abs(tdrop["delta"]) >= FORGETS else
              f"NULL -- {tdrop['delta']:+.4f}, between {STABLE:.2f} and {FORGETS:.2f}"}

    pair = _paired_list([a - b for a, b in zip(_drop(wide, REPLAY, 0), _drop(wide, NAIVE, 0))])
    if pair.get("delta") is None:
        j5 = {"id": "R5", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two arms do not pair"}
    else:
        j5 = {"id": "R5", "measured": f"on the wide step task 0's drop is {statistics.fmean(_drop(wide, NAIVE, 0)):+.4f} "
                                      f"under `{NAIVE}` and {statistics.fmean(_drop(wide, REPLAY, 0)):+.4f} under "
                                      f"`{REPLAY}`, so the buffer changes it by {pair['delta']:+.4f} on a sem of "
                                      f"{pair['sem']:.4f}",
              "verdict": f"MET -- the buffer shrinks the world's forgetting by {abs(pair['delta']):.4f}" if
              pair["delta"] <= -SHRINKS else
              f"FALSIFIER FIRED -- it makes the world forget more, by {pair['delta']:+.4f}" if pair["delta"] >= ROCKS
              else f"NULL -- {pair['delta']:+.4f}, between {SHRINKS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the representation's retention matrix ==")
        print(f"   REFUSED -- {r.get('reason', 'the runs are absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the representation's retention matrix ==")
    print("   the corpus's own probe on the world read off the bodies `e379` and `e380` saved, at every checkpoint "
          "against every task; the head's matrix from the artifacts is beside it")
    for name, entry in r["runs"].items():
        print(f"\n   {name} step, cue@{entry['cue_at']}, {entry['replicates']} replicates, `{entry['run']}`")
        print(f"   {'checkpoint':>16} " + " ".join(f"{'task ' + str(k):>9}" for k in range(N_TASKS))
              + f" {'head row':>9}")
        for c in CHECKPOINTS:
            row = [statistics.fmean(entry["arms"][NAIVE][f"{c}|{k}"]) for k in range(N_TASKS)]
            print(f"   {c:>16} " + " ".join(f"{x:9.4f}" for x in row)
                  + f" {'':>9}")
        for j in range(N_TASKS):
            row = [x if x is not None else float("nan") for x in entry["head"][NAIVE][j]]
            print(f"   {'head after ' + str(j):>16} " + " ".join(f"{x:9.4f}" for x in row))

    print("\n== the registered claims, R1-R5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e379` and `e380` read one column each of what these bodies hold; the rest of the matrix was on")
    print("    disk, and it is the same retention matrix this corpus's continual-learning line has been measuring)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
