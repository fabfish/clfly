"""E360 -- the world gets a nonlinearity: a state that saturates, and the earned label on it.

`e359` gave the world its own dynamics -- a fixed coupling mixes the state's dimensions as it carries them -- and
found the earned label surviving it with every property intact: learned, earned at 18.08 and 31.65 sigma, forgotten
by 0.3750, and repaired by a buffer worth 0.2844. Its own "what it cannot do" closed on the other half of the
sentence it had answered: *"the rule stays linear, so the world cannot yet be pushed into a state and trapped there,
which is the next thing `e333`'s sentence asks for."*

**This gives the world a nonlinearity.** `CueActionEnv` gained `world_nonlinear`: with it on and a coupling drawn,
the world's own carry saturates,

    w_t = (1 - leak) * tanh(w_{t-1} @ K.T) + leak * drive_t

so the state is **bounded** and has its own fixed points -- a system the agent's actions can in principle push into
a corner and be held in. The flag draws nothing, so the two runs' couplings are the **same matrix to the
fingerprint**; it applies only where a coupling does, so the uncoupled rule is untouched and the linear coupled rule
is `K = I` with the saturation off.

One run at `e359`'s exact flags plus `--loop-world-nonlinear`, `--methods naive,replay`, `--repeats 20`, paired
against `e359`'s linear coupled arms at the same seeds. Five claims, registered before the new run's reading was
opened.

- **T1 -- one configuration except the saturation.** The nonlinear run agrees with the linear coupled one on the
  populations, the world, the **coupling fingerprint**, the basis, the tasks and read-out widths, the sizes, the
  replicate count and the seed stream, and records `world_nonlinear` true where the other records false.
  **Falsifier**: any of those differing, which would say the two runs are not one manipulation apart.
- **T2 -- and the nonlinear world is learnable.** The nonlinear `naive` arm's diagonal mean is at least **0.10**
  above chance. **Falsifier**: within **0.05** of chance, which would say a body cannot earn an answer from a world
  that saturates -- and that the benchmark needs a linear world. **Null**: between.
- **T3 -- and the answer is still earned.** Both nonlinear arms' paired channel readings are at least **0.10** and
  positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.
- **T4 -- and the saturation is not free.** The nonlinear `naive` diagonal differs from the linear coupled one's by
  at least **0.05**. **Falsifier**: within **0.02**, which would say the nonlinearity changes nothing the benchmark
  can see. **Null**: between. This is the claim that separates "the world got richer" from "the world got richer and
  the task did not notice", which is the shape `e343` and `e345` found on the state read-out's channel.
- **T5 -- and the buffer still helps there.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least
  **0.05**, paired over the twenty replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**:
  between.

**What it cannot do.** *One saturation and one strength*: `tanh` on the carry with no gain to tune, so "nonlinear" is
one point on an axis and not a family -- a sharper or softer saturation is unrun. *One coupling and one draw*: the
same matrix as `e359`, whose shape is itself unexamined. *The linear reference is a different artifact*, and what
makes the pairing legitimate is the recorded fingerprints -- the coupling's in particular -- and the per-replicate
seed stream agreeing. *And trapped is a claim about what a policy could do*: nothing here trains a policy to exploit
the fixed points, so the saturation's consequence for the game is a possibility this unit creates and does not test.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the linear coupled arms already on disk at the same seeds, and the nonlinear run this unit made
LINEAR = Path("runs/e359_earned_label_coupled_20reps.json")
NONLINEAR = Path("runs/e360_earned_label_nonlinear_20reps.json")
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
WORLD_READ_SHA1 = "3a7ba76b3619"
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
COSTS = 0.05
NOTHING = 0.02
FORGETS = 0.05
CLAIMS = (
    ("T1", "one configuration except the saturation",
     "The nonlinear run agrees with the linear coupled one on the populations, the world, the coupling fingerprint, "
     "the basis, the tasks and widths, the sizes, the replicate count and the seed stream, and records "
     "`world_nonlinear` true where the other records false",
     "falsifier: any of those differing, which would say the runs are not one manipulation apart"),
    ("T2", f"and the nonlinear world is learnable, by {LEARNS:.2f} over chance",
     "The nonlinear `naive` arm's diagonal mean is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the answer is still earned, by {CARRIES:.2f} at 2 sigma",
     "Both nonlinear arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("T4", f"and the saturation is not free, by {COSTS:.2f}",
     "The nonlinear `naive` diagonal differs from the linear coupled one's by at least 0.05",
     f"falsifier: within {NOTHING:.2f}; null: between"),
    ("T5", f"and the buffer still helps there, by {FORGETS:.2f}",
     "`replay`'s `mean_forgetting` is lower than `naive`'s by at least 0.05, paired over the replicates",
     f"falsifier: `replay` forgets more by {FORGETS:.2f} or more"),
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
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None, "vals": diffs}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf"),
            "vals": diffs}


def _sg(sigma) -> str:
    return "inf" if sigma is None else f"{sigma:.2f}"


def arm_reading(run: dict | None, arm: str) -> dict:
    if not run:
        return {"arm": arm, "ok": False}
    method = (run.get("methods") or {}).get(arm)
    if not isinstance(method, dict) or not method.get("replicates"):
        return {"arm": arm, "ok": False, "why": "no replicates"}
    reps = method["replicates"]
    channel, forgetting, diagonal, final = [], [], [], []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"arm": arm, "ok": False, "why": "no paired record"}
        channel.append(statistics.fmean([e["with_loop"] - e["without_loop"] for e in entries]))
        forgetting.append(float(r["mean_forgetting"]))
        diagonal.append(float(statistics.fmean(r["learned"])))
        final.append(float(r["final_accuracy"]))
    n_classes = int((run.get("tasks") or [{}])[0].get("n_classes") or 2)
    return {"arm": arm, "ok": True, "n": len(reps), "chance": 1.0 / n_classes, "forgetting": forgetting,
            "diagonal": diagonal, "final": final, "mean_forgetting": statistics.fmean(forgetting),
            "mean_diagonal": statistics.fmean(diagonal), "mean_final": statistics.fmean(final),
            "paired": paired(channel, [0.0] * len(channel)),
            "retention": [[None if x is None else float(x) for x in row] for row in (reps[0].get("retention") or [])]}


def _facts(run: dict | None) -> dict:
    s = (run or {}).get("config") or {}
    d = (run or {}).get("env_draw") or {}
    return {"loop_world_coupled": bool(s.get("loop_world_coupled")),
            "loop_world_nonlinear": bool(s.get("loop_world_nonlinear")),
            "world_coupled": d.get("world_coupled"), "world_coupling_sha1": d.get("world_coupling_sha1"),
            "world_nonlinear": d.get("world_nonlinear"), "readout_from_world": bool(s.get("readout_from_world")),
            "loop_world_dims": s.get("loop_world_dims"), "loop_world_leak": s.get("loop_world_leak"),
            "closed_loop": bool(s.get("closed_loop")), "repeats": s.get("repeats"),
            "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"), "basis": s.get("basis"),
            "seed0": s.get("seed0"), "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "world_read_sha1": d.get("world_read_sha1"), "world_drive_sha1": d.get("world_drive_sha1"),
            "cue_sha1": d.get("cue_sha1"), "action_sha1": d.get("action_sha1"),
            "feedback_sha1": d.get("feedback_sha1")}


def reading(linear_path: Path = LINEAR, nonlinear_path: Path = NONLINEAR) -> dict:
    linear, nonlinear = load(linear_path), load(nonlinear_path)
    out = {"rows": {**{f"linear_{a}": arm_reading(linear, a) for a in ARMS},
                    **{f"nonlinear_{a}": arm_reading(nonlinear, a) for a in ARMS}},
           "facts": {"linear": _facts(linear), "nonlinear": _facts(nonlinear)},
           "runs": {"linear": Path(linear_path).name, "nonlinear": Path(nonlinear_path).name},
           "expected_world_read_sha1": WORLD_READ_SHA1, "expected_coupling_sha1": COUPLING_SHA1,
           "expected_replicates": REPLICATES, "diagonal_gap": None, "nonlinear_buffer": None}
    out["ok"] = {"linear": linear is not None and all(out["rows"][f"linear_{a}"].get("ok") for a in ARMS),
                 "nonlinear": nonlinear is not None
                 and all(out["rows"][f"nonlinear_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["nonlinear"]:
        out["nonlinear_buffer"] = paired(out["rows"][f"nonlinear_{REPLAY}"]["forgetting"],
                                         out["rows"][f"nonlinear_{NAIVE}"]["forgetting"])
        if out["ok"]["linear"]:
            out["diagonal_gap"] = paired(out["rows"][f"nonlinear_{NAIVE}"]["diagonal"],
                                         out["rows"][f"linear_{NAIVE}"]["diagonal"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("nonlinear"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the nonlinear run is not on disk"}
                for c in CLAIMS]

    lin = r["facts"]["linear"]
    non = r["facts"]["nonlinear"]
    shared = ("readout_from_world", "loop_world_dims", "loop_world_leak", "closed_loop", "repeats", "circuit_size",
              "readout_size", "basis", "seed0", "task_names", "task_readout_widths", "world_read_sha1",
              "world_drive_sha1", "cue_sha1", "action_sha1", "feedback_sha1", "world_coupling_sha1")
    differ = {k: [lin.get(k), non.get(k)] for k in shared if (lin and lin.get(k) != non.get(k))}
    good = (not differ and non.get("world_nonlinear") is True and non.get("world_coupled") is True
            and (lin is None or (lin.get("world_nonlinear") in (False, None) and lin.get("world_coupled") is True))
            and non.get("world_coupling_sha1") == COUPLING_SHA1
            and non.get("world_read_sha1") == WORLD_READ_SHA1 and non.get("repeats") == REPLICATES
            and rows[f"nonlinear_{NAIVE}"]["n"] == REPLICATES and rows[f"nonlinear_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"nonlinear arms from `{r['runs']['nonlinear']}` against the linear coupled run "
                                  f"`{r['runs']['linear']}`: circuits {non['circuit_size']}, tasks "
                                  f"{non['task_names']} at read-out widths {non['task_readout_widths']}, "
                                  f"{non['repeats']} replicates each at seed0 {non['seed0']}, basis {non['basis']}, "
                                  f"world read {non['world_read_sha1']} (expected {r['expected_world_read_sha1']}), "
                                  f"coupling {non['world_coupling_sha1']} against the linear run's "
                                  f"{lin and lin.get('world_coupling_sha1')} (expected "
                                  f"{r['expected_coupling_sha1']}), saturation {non['world_nonlinear']} against "
                                  f"{lin and lin.get('world_nonlinear')}, other fields differing {differ}",
          "verdict": "MET -- one configuration except the saturation" if good else
          f"FALSIFIER FIRED -- the runs differ beyond the saturation: {differ}, coupling "
          f"{non.get('world_coupling_sha1')}/{lin and lin.get('world_coupling_sha1')}, saturation "
          f"{non.get('world_nonlinear')}/{lin and lin.get('world_nonlinear')}"}

    naive = rows[f"nonlinear_{NAIVE}"]
    above = naive["mean_diagonal"] - naive["chance"]
    j2 = {"id": "T2", "measured": f"the nonlinear `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} "
                                  f"against a chance of {naive['chance']:.2f}, {above:+.4f} above it, over "
                                  f"{naive['n']} replicates",
          "verdict": f"MET -- the nonlinear world is learnable, {above:+.4f} above chance" if above >= LEARNS else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance" if above < FLAT else
          f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'nonlinear_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'nonlinear_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"nonlinear_{a}"]["paired"]["delta"] is not None
                                    and rows[f"nonlinear_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"nonlinear_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j3 = {"id": "T3", "measured": f"the nonlinear arms' paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is still earned in both arms, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    est = r.get("diagonal_gap") or {"delta": None}
    if est.get("delta") is None:
        j4 = {"id": "T4", "measured": "the nonlinear-linear diagonal difference was not computable",
              "verdict": "REFUSED -- the difference was not computable"}
    else:
        j4 = {"id": "T4", "measured": f"the nonlinear `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} and the "
                                      f"linear coupled one {rows[f'linear_{NAIVE}']['mean_diagonal']:.4f}, "
                                      f"{est['delta']:+.4f} apart on a sem of {est['sem']:.4f} "
                                      f"({_sg(est['sigma'])} sigma)",
              "verdict": f"MET -- the saturation is not free, {est['delta']:+.4f}" if
              abs(est["delta"]) >= COSTS else
              f"FALSIFIER FIRED -- within {NOTHING:.2f} of it, {est['delta']:+.4f}" if
              abs(est["delta"]) < NOTHING else
              f"NULL -- {est['delta']:+.4f}, between {NOTHING:.2f} and {COSTS:.2f}"}

    buf = r.get("nonlinear_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the nonlinear buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the nonlinear `{REPLAY}` arm forgets "
                                      f"{rows[f'nonlinear_{REPLAY}']['mean_forgetting']:.4f} against the nonlinear "
                                      f"`{NAIVE}` arm's {naive['mean_forgetting']:.4f}, so the buffer changes it by "
                                      f"{buf['delta']:+.4f} on a sem of {buf['sem']:.4f} ({_sg(buf['sigma'])} sigma)",
              "verdict": f"MET -- the buffer still helps there by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS
              else f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS
              else f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("nonlinear"):
        print("== the world gets a nonlinearity ==\n   REFUSED -- the nonlinear run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world gets a nonlinearity ==")
    print(f"   nonlinear arms from `{r['runs']['nonlinear']}` against the linear coupled run `{r['runs']['linear']}`")
    print(f"\n   {'world':>10} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        world = key.split("_", 1)[0]
        print(f"   {world:>10} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e333` named the world's gap as a linear scalar rule with no coupling and nothing the agent can")
    print("    push it into; `e359` gave it the coupling and this gives it the saturation)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--linear", type=Path, default=LINEAR)
    ap.add_argument("--nonlinear", type=Path, default=NONLINEAR)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(linear_path=args.linear, nonlinear_path=args.nonlinear)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
