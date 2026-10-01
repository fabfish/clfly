"""E335 -- what replay stores is the input and not the feature, so the staleness is in the body.

`e334` read the loss on `replay`'s stored features out and found the mechanism `e333` named **refuted in the form it
was named**: the two worlds' retention differs by 0.0375 at 2.45 sigma, and the loss `replay` actually minimises is
the same to within **0.32 sigma** and falls in both. Its own "what it cannot do" gave the reading in advance --
*the stored features are not read out, so a change that makes them different without making them worse fitted is
invisible* -- and it named the next unit: comparing the stored activations **themselves**, which needs a feature
dump and not a loss.

**This unit finds that no dump is needed, because there are no stored activations.** `run_method`'s replay buffer is

    replay.extend((task.u_train[i], int(task.y_train[i]), k) for i in idx)

-- an **input** and a label, taken from the task. The features `e334` measured the loss on are **recomputed by the
current body at replay time**, which is why they are called features of the body and not of the buffer. So the
staleness `e333` proposed is not the buffer's: the buffer is the same object in both worlds, and what has moved is
the network that reads it.

Four claims, registered before this unit's reading. Two are measured on the environment and the runner's source and
two on `e334`'s artifacts, which are already on disk -- so this unit runs nothing.

- **T1 -- the buffer's contents are identical in the two worlds.** The tasks' stimulus arrays are **byte-identical**
  between `leak = 1.0` and `leak = 0.35`, because the world's channel is added by the feedback closure at roll time
  and never enters the array a task is built from. **Falsifier**: any element differing, which would put the
  world's change into the stored objects after all.
- **T2 -- and what the buffer holds is an input, not an activation.** The runner's `replay.extend` call stores
  `task.u_train[i]` with its label. **Falsifier**: a call that stores a trajectory, a read-out state or a feature.
- **T3 -- and the bodies differ between the two worlds.** The `theta_drift` the artifacts already record differs
  between them by at least **1%** of the instantaneous run's own drift, averaged over tasks and replicates.
  **Falsifier**: a difference below **0.1%**, which would say the two bodies are the same object and the retention
  difference is somewhere else entirely. **Null**: between.
- **T4 -- and the drift is larger in the world with a rule.** `e333` measured `replay`'s retention worse there
  (+0.0375 at 2.45 sigma), so if the retention difference lives in the body then the body that moved more is the
  carried one. **Falsifier**: the carried run's drift lower by the same 1%. **Null**: between.

**What it cannot do.** *Two artifacts, one arm and one pair of worlds*: `naive`, `ewc` and the block arms are not
read, and `e332`'s other sign -- retention *improving* when the response became a state -- is not asked. *Drift is a
norm and not a direction*: a body that moved the same distance in a different direction is invisible to T3 and T4,
and the metric the artifacts record is `||theta - theta_before|| / ||theta_before||`. *T4 is a claim about two runs*,
which is why its falsifier is stated on the same 1% as T3's rather than on a sigma. *And the claim that the world's
change never enters the task array is a claim about this environment*: a future environment that wrote the world
into `u` would make the buffer itself world-dependent, which is what T1 would then catch.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
INSTANT = RUNS / "e334_replay_instant.json"
CARRY = RUNS / "e334_replay_carry.json"
RUNNER = Path("experiments/e8_rate_network.py")
ARM = "replay"
LEAKS = {"instant": 1.0, "carry": 0.35}
#: T3's and T4's bars, as shares of the instantaneous run's own drift
MOVED = 0.01
STILL = 0.001
CLAIMS = (
    ("T1", "the buffer's contents are identical in the two worlds",
     "The tasks' stimulus arrays are byte-identical between the two worlds, the world's channel being added by the "
     "feedback closure at roll time",
     "falsifier: any element differing"),
    ("T2", "and what the buffer holds is an input and not an activation",
     "`run_method`'s `replay.extend` call stores a task input with its label",
     "falsifier: a call that stores a trajectory, a read-out state or a feature"),
    ("T3", f"and the bodies differ, by {MOVED:.0%} of the instantaneous run's own drift",
     f"The `theta_drift` the two artifacts record differs between them by at least {MOVED:.0%}, averaged over tasks "
     f"and replicates",
     f"falsifier: a difference below {STILL:.1%}"),
    ("T4", "and the drift is larger in the world with a rule",
     f"`e333` measured `replay`'s retention worse in the carried world, so the body that moved more is the carried one",
     f"falsifier: the carried run's drift lower by the same {MOVED:.0%}"),
)


def buffer_contents(n_symbols: int = 4, n_train: int = 8, n_test: int = 8, seed: int = 0) -> dict:
    """T1: build the same task under both worlds and compare the arrays a replay buffer is filled from."""
    from clfly.network import env as fly_env

    class _Circ:
        n_neurons = 64

    out = {}
    for tag, leak in LEAKS.items():
        e = fly_env.build(_Circ(), n_symbols=n_symbols, tau=8, n_cue=6, n_action=4, n_feedback=6,
                          seed=seed, world_modes=2, world_leak=leak, noise=1.0)
        task = fly_env.make_env_task(e, f"loop_{tag}", symbols=range(n_symbols), n_train=n_train,
                                     n_test=n_test, readout_neurons=np.arange(4), seed=0)
        out[tag] = task
    a, b = out["instant"], out["carry"]
    return {
        "n_train": n_train, "n_test": n_test,
        "u_train_identical": bool(np.array_equal(a.u_train, b.u_train)),
        "u_test_identical": bool(np.array_equal(a.u_test, b.u_test)),
        "y_train_identical": bool(np.array_equal(a.y_train, b.y_train)),
        "y_test_identical": bool(np.array_equal(a.y_test, b.y_test)),
        "leaks": [LEAKS["instant"], LEAKS["carry"]],
    }


def buffer_source(path: Path = RUNNER) -> dict:
    """T2: what the runner's replay buffer is filled with, read off the source rather than asserted from memory."""
    text = path.read_text(encoding="utf-8")
    calls = [ln.strip() for ln in text.splitlines() if re.search(r"\breplay\.extend\(", ln)]
    #: the extension runs over the next line or two, so the statement is read up to its closing bracket
    start = next((i for i, ln in enumerate(text.splitlines()) if re.search(r"\breplay\.extend\(", ln)), None)
    statement = ""
    if start is not None:
        lines = text.splitlines()
        depth = 0
        for ln in lines[start:start + 6]:
            statement += ln.strip() + " "
            depth += ln.count("(") - ln.count(")")
            if depth <= 0:
                break
    return {"calls": calls, "statement": statement.strip(),
            "stores_an_input": "u_train" in statement, "mentions_a_feature": bool(
                re.search(r"traj|readout|feat|state", statement))}


def drifts(instant=INSTANT, carry=CARRY) -> dict:
    """T3 and T4: the two runs' recorded `theta_drift`, per task and per replicate."""
    out = {"runs": 0}
    loaded = {}
    for tag, path in (("instant", instant), ("carry", carry)):
        p = Path(path)
        if not p.is_file():
            out.setdefault("missing", []).append(str(p))
            continue
        try:
            loaded[tag] = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            out.setdefault("missing", []).append(str(p))
    if len(loaded) < 2:
        return out
    out["runs"] = 2
    per_task = {}
    for tag, d in loaded.items():
        reps = d["methods"][ARM]["replicates"]
        per_task[tag] = [[float(x) for x in r["theta_drift"]] for r in reps]
    means = {tag: statistics.fmean([v for row in rows for v in row]) for tag, rows in per_task.items()}
    task_means = {tag: [statistics.fmean([row[j] for row in rows]) for j in range(len(per_task[tag][0]))]
                  for tag, rows in per_task.items()}
    out.update({"per_task": per_task, "mean": means, "task_means": task_means,
                "share": (means["carry"] - means["instant"]) / means["instant"] if means["instant"] else None,
                "forgetting": {tag: d["methods"][ARM].get("mean_forgetting") for tag, d in loaded.items()},
                "accuracy": {tag: d["methods"][ARM].get("final_accuracy") for tag, d in loaded.items()},
                "leaks": [(d.get("env_draw") or {}).get("world_leak") for d in loaded.values()]})
    return out


def reading() -> dict:
    return {"buffer": buffer_contents(), "source": buffer_source(), "drift": drifts()}


def judge(r: dict) -> list[dict]:
    buf = r.get("buffer") or {}
    same = bool(buf) and all(buf.get(k) for k in ("u_train_identical", "u_test_identical",
                                                  "y_train_identical", "y_test_identical"))
    j1 = {"id": "T1", "measured": f"{buf.get('n_train')} train and {buf.get('n_test')} test examples built under "
                                  f"leaks {buf.get('leaks')}: stimulus arrays identical "
                                  f"{buf.get('u_train_identical')} train and {buf.get('u_test_identical')} test, "
                                  f"labels identical {buf.get('y_train_identical')} and "
                                  f"{buf.get('y_test_identical')}",
          "verdict": "MET -- the buffer's contents are the same objects in both worlds" if same else
                     "FALSIFIER FIRED -- the world's change reaches the stored arrays"}

    src = r.get("source") or {}
    j2 = {"id": "T2", "measured": f"the runner's replay buffer is filled by `{src.get('statement')}`",
          "verdict": "MET -- it stores an input and a label" if src.get("stores_an_input")
          and not src.get("mentions_a_feature") else
          f"FALSIFIER FIRED -- `{src.get('statement')}`"}

    d = r.get("drift") or {}
    if d.get("runs", 0) < 2:
        tail = [{"id": c[0], "measured": f"missing {d.get('missing')}",
                 "verdict": "REFUSED -- the two artifacts are not both on disk"} for c in CLAIMS[2:]]
        return [j1, j2] + tail
    share = d["share"]
    detail = ", ".join(f"{tag} {d['task_means'][tag]}" for tag in d["task_means"])
    j3 = {"id": "T3", "measured": f"`theta_drift` per task: {detail}; means "
                                  f"{ {k: round(v, 6) for k, v in d['mean'].items()} }, carried minus instantaneous "
                                  f"{share:+.4%}",
          "verdict": f"MET -- the bodies differ by {abs(share):.2%} of the instantaneous drift" if abs(share) >= MOVED
          else f"FALSIFIER FIRED -- they differ by only {abs(share):.4%}" if abs(share) < STILL else
          f"NULL -- {abs(share):.4%}, between {STILL:.1%} and {MOVED:.0%}"}
    j4 = {"id": "T4", "measured": f"carried minus instantaneous drift {share:+.4%}, with `{ARM}`'s forgetting "
                                  f"{ {k: round(v, 4) for k, v in d['forgetting'].items()} } there",
          "verdict": f"MET -- the carried body moved {share:.2%} further and its retention is the worse one" if
          share >= MOVED else
          f"FALSIFIER FIRED -- the carried body moved {share:+.4%}, the other way" if share <= -MOVED else
          f"NULL -- {share:+.4%}, between {-MOVED:.0%} and {MOVED:.0%}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== what replay stores ==")
    b, s, d = r.get("buffer") or {}, r.get("source") or {}, r.get("drift") or {}
    print(f"   buffer: {b.get('n_train')} train / {b.get('n_test')} test examples under leaks {b.get('leaks')}; "
          f"identical u {b.get('u_train_identical')}/{b.get('u_test_identical')}, "
          f"y {b.get('y_train_identical')}/{b.get('y_test_identical')}")
    print(f"   the runner fills it by: {s.get('statement')}")
    if d.get("runs", 0) == 2:
        print(f"   theta_drift per task: " + ", ".join(f"{t} {v}" for t, v in d["task_means"].items()))
        print(f"   means: { {k: round(v, 6) for k, v in d['mean'].items()} }, carried minus instantaneous "
              f"{d['share']:+.4%}")
        print(f"   forgetting: { {k: round(v, 4) for k, v in d['forgetting'].items()} }, accuracy "
              f"{ {k: round(v, 4) for k, v in d['accuracy'].items()} }")
    else:
        print(f"   REFUSED for the drift -- missing {d.get('missing')}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e334` refuted the staleness mechanism in the form it was named and said the next unit needed a")
    print("    feature dump; this finds there is nothing to dump, because the buffer holds inputs)")
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
