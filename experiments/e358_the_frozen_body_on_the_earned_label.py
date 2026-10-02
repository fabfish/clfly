"""E358 -- the frozen body on the earned label: is the benchmark measuring the connectome, or only the head?

`e356` resolved the corpus's method contrast on the earned label -- a task whose answer exists only in the
environment -- at **11.65 sigma** over twenty replicates, and `e357` found the basis contrast a null on it at 1.47
sigma. Both closed with the same untested control: *"`frozen`, `frozen-bias` and the oracle line are not run."*

**The frozen body is the sharpest of them, and on this substrate it asks a question the state read-out cannot.** The
corpus's `--frozen-body` trains **the head and nothing else** -- the recurrent weights stay at the connectome's
initialisation -- and on the state read-out that is a diagnostic of whether the accuracy is being carried by the
decoder. **Here the answer is read from a world the agent's own actions drive**, so with the body frozen the head
alone has to make the frozen dynamics write a separable state into the world: if it can, the earned label's numbers
are about a linear map over an environment and not about the connectome's plasticity, and if it cannot, they are
about the body.

One run at `e356`'s exact flags plus `--frozen-body`, `--methods naive,replay`, `--repeats 20`, into
`runs/e358_earned_label_frozen_20reps.json`, paired against `e356`'s plastic arms which are already on disk at the
same seeds. Five claims, registered before the new run's reading was opened.

- **T1 -- one configuration except the body.** The frozen run agrees with `e356`'s on the world's fingerprints, the
  matched-random partition, the basis, the tasks and read-out widths, the circuit and read-out sizes, the replicate
  count and the seed stream, differing in `frozen_body` and in nothing else. **Falsifier**: any other field
  differing, or either replicate count not twenty.
- **T2 -- and the frozen body learns the suite.** The frozen `naive` arm's diagonal mean is at least **0.10** above
  chance. **Falsifier**: within **0.05** of chance, which would say the world read-out needs a plastic body and the
  headline numbers are about the connectome. **Null**: between.
- **T3 -- and the plastic body is worth something.** `e356`'s plastic `naive` diagonal exceeds the frozen one's by at
  least **0.05**. **Falsifier**: the frozen arm is at least as good by **0.05**, which would say the connectome's
  plasticity contributes nothing to the earned label and the benchmark measures a linear map. **Null**: between.
- **T4 -- and the frozen suite still forgets.** The frozen `naive` arm's `mean_forgetting` is at least **0.05**,
  which can only be the head being overwritten -- the body is not moving. **Falsifier**: below **0.02**. **Null**:
  between.
- **T5 -- and the buffer still helps there, at 2 sigma.** `replay`'s `mean_forgetting` is lower than `naive`'s by at
  least **0.05**, paired over the twenty replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**:
  between.

**What it cannot do.** *One control and two arms*: `frozen-bias`, `--anchor-bias` and the oracle line are unrun, so
this isolates the recurrent weights and not the bias, and nothing here is about the penalty. *The frozen reference is
a different artifact*: the plastic arms come from `e356`, and what makes the pairing legitimate is the recorded world
and partition fingerprints and the per-replicate seed stream agreeing -- checked in T1 -- and not the sharing of a
process. *One world, one leak and one width*: `leak = 0.35`, eight dimensions and four symbols per task. *And a
frozen body is not a lesioned one*: the connectome's initialisation still does what it does, so the control bounds
plasticity's contribution and does not measure the substrate's.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the plastic arms already on disk at the same seeds, and the frozen run this unit made
PLASTIC = Path("runs/e356_earned_label_r32_20reps.json")
FROZEN = Path("runs/e358_earned_label_frozen_20reps.json")
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
WORLD_READ_SHA1 = "3a7ba76b3619"
PARTITION_SHA1 = "0467b1a5f7a0"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
WORTH = 0.05
FORGETS = 0.05
NOTHING = 0.02
CLAIMS = (
    ("T1", "one configuration except the body",
     "The frozen run agrees with the plastic one on the world's fingerprints, the matched-random partition, the "
     "basis, the tasks and read-out widths, the sizes, the replicate count and the seed stream, differing in "
     "`frozen_body` and in nothing else",
     "falsifier: any other field differing, or either replicate count not twenty"),
    ("T2", f"and the frozen body learns the suite, by {LEARNS:.2f} over chance",
     "The frozen `naive` arm's diagonal mean is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the plastic body is worth something, by {WORTH:.2f}",
     "The plastic `naive` diagonal exceeds the frozen one's by at least 0.05",
     f"falsifier: the frozen arm is at least as good by {WORTH:.2f}"),
    ("T4", f"and the frozen suite still forgets, by {FORGETS:.2f}",
     "The frozen `naive` arm's `mean_forgetting` is at least 0.05",
     f"falsifier: below {NOTHING:.2f}"),
    ("T5", f"and the buffer still helps there, by {FORGETS:.2f} at 2 sigma",
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
    pd = (run or {}).get("partition_draw") or {}
    return {"frozen_body": bool(s.get("frozen_body")), "readout_from_world": bool(s.get("readout_from_world")),
            "loop_world_dims": s.get("loop_world_dims"), "loop_world_leak": s.get("loop_world_leak"),
            "closed_loop": bool(s.get("closed_loop")), "repeats": s.get("repeats"),
            "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"), "basis": s.get("basis"),
            "seed0": s.get("seed0"), "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "world_read_sha1": d.get("world_read_sha1"), "world_drive_sha1": d.get("world_drive_sha1"),
            "partition_sha1": pd.get("fingerprint_sha1"), "n_groups": pd.get("n_groups")}


def reading(plastic_path: Path = PLASTIC, frozen_path: Path = FROZEN) -> dict:
    plastic, frozen = load(plastic_path), load(frozen_path)
    out = {"rows": {f"{body}_{a}": arm_reading(run, a)
                    for body, run in (("plastic", plastic), ("frozen", frozen)) for a in ARMS},
           "facts": {"plastic": _facts(plastic), "frozen": _facts(frozen)},
           "runs": {"plastic": Path(plastic_path).name, "frozen": Path(frozen_path).name},
           "expected_world_read_sha1": WORLD_READ_SHA1, "expected_partition_sha1": PARTITION_SHA1,
           "expected_replicates": REPLICATES, "diagonal_gap": None, "frozen_buffer": None}
    out["ok"] = {body: all(out["rows"][f"{body}_{a}"].get("ok") for a in ARMS)
                 for body in ("plastic", "frozen")}
    if out["ok"]["plastic"] and out["ok"]["frozen"]:
        out["diagonal_gap"] = paired(out["rows"][f"plastic_{NAIVE}"]["diagonal"],
                                     out["rows"][f"frozen_{NAIVE}"]["diagonal"])
        out["frozen_buffer"] = paired(out["rows"][f"frozen_{REPLAY}"]["forgetting"],
                                      out["rows"][f"frozen_{NAIVE}"]["forgetting"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not (ok.get("plastic") and ok.get("frozen")):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the frozen run or the plastic arms are absent"}
                for c in CLAIMS]

    p, f = r["facts"]["plastic"], r["facts"]["frozen"]
    shared = ("readout_from_world", "loop_world_dims", "loop_world_leak", "closed_loop", "repeats", "circuit_size",
              "readout_size", "basis", "seed0", "task_names", "task_readout_widths", "world_read_sha1",
              "world_drive_sha1", "partition_sha1", "n_groups")
    differ = {k: [p.get(k), f.get(k)] for k in shared if p.get(k) != f.get(k)}
    good = (not differ and not p.get("frozen_body") and f.get("frozen_body")
            and p.get("repeats") == REPLICATES and f.get("repeats") == REPLICATES
            and f.get("world_read_sha1") == WORLD_READ_SHA1 and f.get("partition_sha1") == PARTITION_SHA1
            and rows[f"frozen_{NAIVE}"]["n"] == REPLICATES and rows[f"frozen_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"plastic arms from `{r['runs']['plastic']}` and the frozen run "
                                  f"`{r['runs']['frozen']}`: circuits {p['circuit_size']}, tasks {p['task_names']} "
                                  f"at read-out widths {p['task_readout_widths']}, {p['repeats']} replicates each "
                                  f"at seed0 {p['seed0']}, basis {p['basis']}, world {f['world_read_sha1']} "
                                  f"(expected {r['expected_world_read_sha1']}), partition {f['partition_sha1']} "
                                  f"(expected {r['expected_partition_sha1']}), `frozen_body` "
                                  f"{p['frozen_body']} against {f['frozen_body']}, other fields differing {differ}",
          "verdict": "MET -- one configuration except the body" if good else
          f"FALSIFIER FIRED -- the runs differ beyond `frozen_body`: {differ}, frozen_body "
          f"{p.get('frozen_body')}/{f.get('frozen_body')}, replicates {p.get('repeats')}/{f.get('repeats')}"}

    frozen_naive = rows[f"frozen_{NAIVE}"]
    above = frozen_naive["mean_diagonal"] - frozen_naive["chance"]
    j2 = {"id": "T2", "measured": f"the frozen `{NAIVE}` arm's diagonal mean is {frozen_naive['mean_diagonal']:.4f} "
                                  f"against a chance of {frozen_naive['chance']:.2f}, {above:+.4f} above it, over "
                                  f"{frozen_naive['n']} replicates",
          "verdict": f"MET -- the frozen body learns the suite, {above:+.4f} above chance" if above >= LEARNS else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance, so the earned label needs a plastic body" if
          above < FLAT else f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    est = r.get("diagonal_gap") or {"delta": None}
    if est.get("delta") is None:
        j3 = {"id": "T3", "measured": "the plastic-frozen diagonal difference was not computable",
              "verdict": "REFUSED -- the difference was not computable"}
    else:
        j3 = {"id": "T3", "measured": f"the plastic `{NAIVE}` diagonal is "
                                      f"{rows[f'plastic_{NAIVE}']['mean_diagonal']:.4f} and the frozen one "
                                      f"{frozen_naive['mean_diagonal']:.4f}, {est['delta']:+.4f} apart on a sem of "
                                      f"{est['sem']:.4f} ({_sg(est['sigma'])} sigma)",
              "verdict": f"MET -- the plastic body is worth {est['delta']:+.4f}" if est["delta"] >= WORTH else
              f"FALSIFIER FIRED -- the frozen arm is at least as good, {est['delta']:+.4f}" if
              est["delta"] <= -WORTH else f"NULL -- {est['delta']:+.4f}, between {WORTH:.2f} either way"}

    forget = frozen_naive["mean_forgetting"]
    j4 = {"id": "T4", "measured": f"the frozen `{NAIVE}` arm's `mean_forgetting` is {forget:.4f} with retention "
                                  f"{[[None if x is None else round(x, 3) for x in row] for row in frozen_naive['retention']]}",
          "verdict": f"MET -- the frozen suite forgets, {forget:.4f}, which only the head can do" if
          forget >= FORGETS else
          f"FALSIFIER FIRED -- below {NOTHING:.2f}, {forget:.4f}" if forget < NOTHING else
          f"NULL -- {forget:.4f}, between {NOTHING:.2f} and {FORGETS:.2f}"}

    buf = r.get("frozen_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the frozen buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the frozen `{REPLAY}` arm forgets "
                                      f"{rows[f'frozen_{REPLAY}']['mean_forgetting']:.4f} against the frozen "
                                      f"`{NAIVE}` arm's {forget:.4f}, so the buffer changes it by {buf['delta']:+.4f} "
                                      f"on a sem of {buf['sem']:.4f} ({_sg(buf['sigma'])} sigma)",
              "verdict": f"MET -- the buffer still helps there by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS
              else f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS
              else f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not (ok.get("plastic") and ok.get("frozen")):
        print("== the frozen body on the earned label ==\n   REFUSED -- the frozen run or the plastic arms are absent")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the frozen body on the earned label ==")
    print(f"   plastic arms from `{r['runs']['plastic']}`, frozen run `{r['runs']['frozen']}`")
    print(f"\n   {'body':>8} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
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
    print("\n   (`--frozen-body` trains the head and nothing else; on the state read-out that asks whether the")
    print("    accuracy is the decoder's, and here it asks whether the world read-out needs a plastic body)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plastic", type=Path, default=PLASTIC)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(plastic_path=args.plastic, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
