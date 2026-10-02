"""E359 -- the world gets its own dynamics: does the earned label survive a world that mixes its own state?

`e350` gave the world a **dimension** -- a state vector driven by the whole action population -- and `e351` found the
width bought 88% of that unit's gain. But every dimension of that state is still an **independent leaky integrator**
of the drive, and `e333` named exactly that as its own gap: *"The world's rule is linear and scalar: one leaky
integrator of one action, with no state-to-state coupling and nothing the agent's actions can push it into."*

**This gives the world its own dynamics.** `CueActionEnv` gained `world_coupled`: a fixed
`(world_dims, world_dims)` matrix replaces the independent integrators with

    w_t = (1 - leak) * (w_{t-1} @ K.T) + leak * drive_t

so the world mixes its own dimensions as it carries them, and **`K = I` is the uncoupled rule exactly** -- the
endpoint the control uses and the reason the change is additive. The matrix is drawn from the environment's seed,
scaled so its largest singular value is one, and fingerprinted in the draw; `--loop-world-coupled` exposes it to the
runner, off by default.

One run at `e356`'s exact flags plus `--loop-world-coupled`, `--methods naive,replay`, `--repeats 20`, paired against
`e356`'s uncoupled arms at the same seeds. Five claims, registered before the new run's reading was opened.

- **T1 -- one configuration except the world's rule.** The coupled run agrees with the uncoupled one on the
  populations, the basis, the tasks and read-out widths, the sizes, the replicate count and the seed stream, and its
  own draw records the coupling while the other's does not. **Falsifier**: any of those differing, or a coupling that
  is not recorded where it should be.
- **T2 -- and the coupled world is learnable.** The coupled `naive` arm's diagonal mean is at least **0.10** above
  chance. **Falsifier**: within **0.05** of chance, which would say a body cannot drive a world that moves on its
  own -- and that the earned label needs a world without dynamics. **Null**: between.
- **T3 -- and the answer is still earned.** Both coupled arms' paired channel readings are at least **0.10** and
  positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved. This is the property
  `e355`, `e356` and `e358` measured on the uncoupled world, asked of one that mixes itself.
- **T4 -- and the coupled suite still forgets.** The coupled `naive` arm's `mean_forgetting` is at least **0.05**.
  **Falsifier**: below **0.02**. **Null**: between.
- **T5 -- and the buffer still helps there.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least
  **0.05**, paired over the twenty replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**:
  between.

**What it cannot do.** *One coupling and one draw*: a single matrix from one seed, with its spectrum scaled to one
but its shape unexamined -- a rotation, a contraction, a near-singular map and a K drawn differently are four
different worlds and only the first is run. *The uncoupled reference is a different artifact*: the arms come from
`e356`, and what makes the pairing legitimate is the recorded fingerprints and the per-replicate seed stream
agreeing -- checked in T1. *One leak and one width*: `leak = 0.35` and eight dimensions. *And a coupled world is not
a nonlinear one*: the rule stays linear, so nothing here makes the world a state machine the agent can be trapped
by, which is the next thing `e333`'s sentence asks for.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the uncoupled arms already on disk at the same seeds, and the coupled run this unit made
PLAIN = Path("runs/e356_earned_label_r32_20reps.json")
COUPLED = Path("runs/e359_earned_label_coupled_20reps.json")
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
WORLD_READ_SHA1 = "3a7ba76b3619"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
FORGETS = 0.05
NOTHING = 0.02
CLAIMS = (
    ("T1", "one configuration except the world's rule",
     "The coupled run agrees with the uncoupled one on the populations, the basis, the tasks and read-out widths, the "
     "sizes, the replicate count and the seed stream, and its own draw records the coupling while the other's does "
     "not",
     "falsifier: any of those differing, or a coupling that is not recorded where it should be"),
    ("T2", f"and the coupled world is learnable, by {LEARNS:.2f} over chance",
     "The coupled `naive` arm's diagonal mean is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the answer is still earned, by {CARRIES:.2f} at 2 sigma",
     "Both coupled arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("T4", f"and the coupled suite still forgets, by {FORGETS:.2f}",
     "The coupled `naive` arm's `mean_forgetting` is at least 0.05",
     f"falsifier: below {NOTHING:.2f}"),
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
    return {"loop_world_coupled": bool(s.get("loop_world_coupled")), "world_coupled": d.get("world_coupled"),
            "world_coupling_sha1": d.get("world_coupling_sha1"), "readout_from_world": bool(s.get("readout_from_world")),
            "loop_world_dims": s.get("loop_world_dims"), "loop_world_leak": s.get("loop_world_leak"),
            "closed_loop": bool(s.get("closed_loop")), "repeats": s.get("repeats"),
            "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"), "basis": s.get("basis"),
            "seed0": s.get("seed0"), "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "world_read_sha1": d.get("world_read_sha1"), "world_drive_sha1": d.get("world_drive_sha1"),
            "cue_sha1": d.get("cue_sha1"), "action_sha1": d.get("action_sha1"),
            "feedback_sha1": d.get("feedback_sha1")}


def reading(plain_path: Path = PLAIN, coupled_path: Path = COUPLED) -> dict:
    plain, coupled = load(plain_path), load(coupled_path)
    out = {"rows": {**{f"plain_{a}": arm_reading(plain, a) for a in ARMS},
                    **{f"coupled_{a}": arm_reading(coupled, a) for a in ARMS}},
           "facts": {"plain": _facts(plain), "coupled": _facts(coupled)},
           "runs": {"plain": Path(plain_path).name, "coupled": Path(coupled_path).name},
           "expected_world_read_sha1": WORLD_READ_SHA1, "expected_replicates": REPLICATES,
           "coupled_buffer": None}
    out["ok"] = {"plain": all(out["rows"][f"plain_{a}"].get("ok") for a in ARMS),
                 "coupled": all(out["rows"][f"coupled_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["coupled"]:
        out["coupled_buffer"] = paired(out["rows"][f"coupled_{REPLAY}"]["forgetting"],
                                       out["rows"][f"coupled_{NAIVE}"]["forgetting"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("coupled"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the coupled run is not on disk"} for c in CLAIMS]

    p, c = r["facts"]["plain"], r["facts"]["coupled"]
    shared = ("readout_from_world", "loop_world_dims", "loop_world_leak", "closed_loop", "repeats", "circuit_size",
              "readout_size", "basis", "seed0", "task_names", "task_readout_widths", "world_read_sha1",
              "world_drive_sha1", "cue_sha1", "action_sha1", "feedback_sha1")
    differ = {k: [p.get(k), c.get(k)] for k in shared if (p and p.get(k) != c.get(k))}
    #: the uncoupled reference predates the field -- `e356` was written before `world_coupled` existed -- so an
    #: absent record on that side means the uncoupled rule, which is exactly what that code path does; the coupled
    #: side has to record it, and a coupled run that records nothing is T1's falsifier.
    recorded = (c.get("world_coupled") is True and bool(c.get("world_coupling_sha1"))
                and (p is None or (not p.get("world_coupled") and not p.get("world_coupling_sha1"))))
    good = (not differ and recorded and c.get("repeats") == REPLICATES
            and c.get("world_read_sha1") == WORLD_READ_SHA1
            and rows[f"coupled_{NAIVE}"]["n"] == REPLICATES and rows[f"coupled_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"coupled arms from `{r['runs']['coupled']}` against `{r['runs']['plain']}`: "
                                  f"circuits {c['circuit_size']}, tasks {c['task_names']} at read-out widths "
                                  f"{c['task_readout_widths']}, {c['repeats']} replicates each at seed0 "
                                  f"{c['seed0']}, basis {c['basis']}, world read {c['world_read_sha1']} (expected "
                                  f"{r['expected_world_read_sha1']}), cue/action/feedback "
                                  f"{c['cue_sha1']}/{c['action_sha1']}/{c['feedback_sha1']}, the coupling "
                                  f"recorded {c['world_coupled']} with fingerprint {c['world_coupling_sha1']} "
                                  f"against the uncoupled run's {p and p.get('world_coupling_sha1')}, other fields "
                                  f"differing {differ}",
          "verdict": "MET -- one configuration except the world's rule" if good else
          f"FALSIFIER FIRED -- the runs differ beyond the coupling: {differ}, coupling "
          f"{c.get('world_coupled')}/{c.get('world_coupling_sha1')} against "
          f"{p and p.get('world_coupled')}/{p and p.get('world_coupling_sha1')}, replicates "
          f"{c.get('repeats')}"}

    naive = rows[f"coupled_{NAIVE}"]
    above = naive["mean_diagonal"] - naive["chance"]
    j2 = {"id": "T2", "measured": f"the coupled `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} against "
                                  f"a chance of {naive['chance']:.2f}, {above:+.4f} above it, over {naive['n']} "
                                  f"replicates",
          "verdict": f"MET -- the coupled world is learnable, {above:+.4f} above chance" if above >= LEARNS else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance" if above < FLAT else
          f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'coupled_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'coupled_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"coupled_{a}"]["paired"]["delta"] is not None
                                    and rows[f"coupled_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"coupled_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j3 = {"id": "T3", "measured": f"the coupled arms' paired channel readings over {naive['n']} replicates: {detail}",
          "verdict": "MET -- the answer is still earned in both arms, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    forget = naive["mean_forgetting"]
    j4 = {"id": "T4", "measured": f"the coupled `{NAIVE}` arm's `mean_forgetting` is {forget:.4f} with retention "
                                  f"{[[None if x is None else round(x, 3) for x in row] for row in naive['retention']]}",
          "verdict": f"MET -- the coupled suite forgets, {forget:.4f}" if forget >= FORGETS else
          f"FALSIFIER FIRED -- below {NOTHING:.2f}, {forget:.4f}" if forget < NOTHING else
          f"NULL -- {forget:.4f}, between {NOTHING:.2f} and {FORGETS:.2f}"}

    buf = r.get("coupled_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the coupled buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the coupled `{REPLAY}` arm forgets {rows[f'coupled_{REPLAY}']['mean_forgetting']:.4f} "
                                      f"against the coupled `{NAIVE}` arm's {forget:.4f}, so the buffer changes it by "
                                      f"{buf['delta']:+.4f} on a sem of {buf['sem']:.4f} ({_sg(buf['sigma'])} sigma)",
              "verdict": f"MET -- the buffer still helps there by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS
              else f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS
              else f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("coupled"):
        print("== the world gets its own dynamics ==\n   REFUSED -- the coupled run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world gets its own dynamics ==")
    print(f"   coupled arms from `{r['runs']['coupled']}` against `{r['runs']['plain']}`")
    print(f"\n   {'world':>8} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        body, arm = key.split("_", 1)
        print(f"   {body:>8} {arm:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e333` named the world's own gap -- one leaky integrator of one action with no state-to-state")
    print("    coupling; this gives it one and asks whether a body can still earn the answer from it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plain", type=Path, default=PLAIN)
    ap.add_argument("--coupled", type=Path, default=COUPLED)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(plain_path=args.plain, coupled_path=args.coupled)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
