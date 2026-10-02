"""E357 -- the basis contrast on the earned label: the corpus's own headline, asked where the answer lives in the world.

`e355` and `e356` moved the corpus's method contrast onto the earned label -- a task whose answer exists only in the
environment -- and `e356` resolved it at **11.65 sigma** over twenty replicates. Both closed with the same missing
piece: *"three arms and no matched-random pair: the basis contrast -- `ewc-block` against the size-matched random
partition, the corpus's own headline and the null eleven audits left standing -- is not in this run, so nothing here
is about the connectome's block structure."*

**This unit supplies it, and it supplies half of it from the corpus rather than from a new run.** `e356`'s artifact
already carries twenty replicates of `ewc-block` on exactly this configuration -- the same world to the fingerprint,
the same tasks, the same seeds -- so the only thing missing is the matched-random arm, and one run of
`--methods ewc-block-rand --repeats 20` at the same flags produces it. `e356`'s artifact records the matched-random
partition it drew as `{'matched_random_draw_seed': 0, 'n_groups': 98, 'fingerprint_sha1': '0467b1a5f7a0'}`, and the
new run records the same, so the two arms are one configuration in two files and their replicate *r* is the same
seed.

Four claims, registered before the new run's reading was opened.

- **T1 -- one configuration in two artifacts.** The two runs agree on the world's fingerprints, the basis, the
  matched-random partition's fingerprint and group count, the task names and read-out widths, the replicate count
  and the seed stream, and they differ only in the arm each trained. **Falsifier**: any of those differing, or a
  replicate count that is not twenty in either.
- **T2 -- and the basis contrast does not resolve on the earned label.** `ewc-block` and `ewc-block-rand` differ in
  `mean_forgetting` by at most **0.05**, paired over the twenty replicates. **Falsifier**: **0.10** or more, which
  would be the connectome's block structure mattering where the answer lives in the environment -- the finding
  eleven audits did not produce on the state read-out. **Null**: between.
- **T3 -- and not on the diagonal either.** The two arms' diagonal means differ by at most **0.05**. **Falsifier**:
  **0.10** or more. **Null**: between.
- **T4 -- and both arms are learned and earned.** Each arm's diagonal mean is at least **0.10** above chance and its
  paired channel reading is at least **0.10** and positive at **2 sigma**. **Falsifier**: either arm failing any of
  those, which would mean the contrast is being read between an arm that works and one that does not.

**What it cannot do.** *The pair is assembled from two artifacts rather than produced in one run*: the runner's own
matched-pair block draws both partitions and could have trained both arms in one process, and what makes this pairing
legitimate is the recorded partition fingerprint and the per-replicate seed stream agreeing -- both checked in T1 --
and not the sharing of a process. *Two arms and one basis*: `cell_class` only, with `--anchor-bias`, the frozen
controls and the oracle line unrun, and nothing here is about `ewc` or the lambda. *One world, one leak and one
width*: `leak = 0.35`, eight dimensions and four symbols per task. *And a null is a bound*: twenty replicates bound
the contrast at roughly the run's own noise floor (0.106 at five replicates, near 0.05 here), so a basis effect
smaller than that is not excluded, only unsupported.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the arm already on disk at twenty replicates, and the arm this unit runs
PENALTY = Path("runs/e356_earned_label_r32_20reps.json")
RANDOM = Path("runs/e357_earned_label_rand_20reps.json")
ARM_BIO, ARM_RAND = "ewc-block", "ewc-block-rand"
#: the matched-random partition and the world both runs record, which is what makes them one configuration
PARTITION_SHA1 = "0467b1a5f7a0"
WORLD_READ_SHA1 = "3a7ba76b3619"
REPLICATES = 20
SIGMA = 2.0
SAME = 0.05
SAME_FIRES = 0.10
CARRIES = 0.10
CLAIMS = (
    ("T1", "one configuration in two artifacts",
     "The two runs agree on the world's fingerprints, the basis, the matched-random partition's fingerprint and "
     "group count, the task names and read-out widths, the replicate count and the seed stream, differing only in "
     "the arm each trained",
     "falsifier: any of those differing, or a replicate count that is not twenty in either"),
    ("T2", f"and the basis contrast does not resolve on the earned label, within {SAME:.2f}",
     f"`{ARM_BIO}` and `{ARM_RAND}` differ in `mean_forgetting` by at most 0.05, paired over the replicates",
     f"falsifier: {SAME_FIRES:.2f} or more; null: between"),
    ("T3", f"and not on the diagonal either, within {SAME:.2f}",
     "The two arms' diagonal means differ by at most 0.05",
     f"falsifier: {SAME_FIRES:.2f} or more; null: between"),
    ("T4", f"and both arms are learned and earned, by {CARRIES:.2f}",
     "Each arm's diagonal mean is at least 0.10 above chance and its paired channel reading at least 0.10 and "
     "positive at 2 sigma",
     "falsifier: either arm failing any of those"),
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
    """One arm's per-replicate numbers and its paired channel reading, averaged over the tasks."""
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


def _run_facts(run: dict | None) -> dict:
    settings = (run or {}).get("config") or {}
    draw = (run or {}).get("env_draw") or {}
    pd = (run or {}).get("partition_draw") or {}
    return {"readout_from_world": bool(settings.get("readout_from_world")),
            "world_dims": settings.get("loop_world_dims"), "world_leak": settings.get("loop_world_leak"),
            "closed_loop": bool(settings.get("closed_loop")), "replicates": settings.get("repeats"),
            "circuit_size": settings.get("circuit_size"), "readout_size": settings.get("readout_size"),
            "basis": settings.get("basis"), "seed0": settings.get("seed0"),
            "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "world_read_sha1": draw.get("world_read_sha1"), "world_drive_sha1": draw.get("world_drive_sha1"),
            "env_world_dims": draw.get("world_dims"),
            "partition_sha1": pd.get("fingerprint_sha1"), "n_groups": pd.get("n_groups"),
            "matched_random_draw_seed": pd.get("matched_random_draw_seed")}


def reading(bio_path: Path = PENALTY, rand_path: Path = RANDOM) -> dict:
    bio, rand = load(bio_path), load(rand_path)
    rows = {ARM_BIO: arm_reading(bio, ARM_BIO), ARM_RAND: arm_reading(rand, ARM_RAND)}
    facts = {ARM_BIO: _run_facts(bio), ARM_RAND: _run_facts(rand)}
    out = {"rows": rows, "facts": facts, "runs": {ARM_BIO: Path(bio_path).name, ARM_RAND: Path(rand_path).name},
           "expected_partition_sha1": PARTITION_SHA1, "expected_world_read_sha1": WORLD_READ_SHA1,
           "expected_replicates": REPLICATES,
           "forgetting_contrast": None, "diagonal_contrast": None, "final_contrast": None}
    if rows[ARM_BIO].get("ok") and rows[ARM_RAND].get("ok"):
        out["forgetting_contrast"] = paired(rows[ARM_BIO]["forgetting"], rows[ARM_RAND]["forgetting"])
        out["diagonal_contrast"] = paired(rows[ARM_BIO]["diagonal"], rows[ARM_RAND]["diagonal"])
        out["final_contrast"] = paired(rows[ARM_BIO]["final"], rows[ARM_RAND]["final"])
    return out


def judge(r: dict) -> list[dict]:
    rows, facts = r.get("rows") or {}, r.get("facts") or {}
    if not all(rows.get(a, {}).get("ok") for a in (ARM_BIO, ARM_RAND)):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- both arms are not on disk"} for c in CLAIMS]

    b, d = facts[ARM_BIO], facts[ARM_RAND]
    shared = ("world_read_sha1", "world_drive_sha1", "env_world_dims", "world_dims", "world_leak", "closed_loop",
              "replicates", "circuit_size", "readout_size", "basis", "seed0", "task_names", "task_readout_widths",
              "partition_sha1", "n_groups", "matched_random_draw_seed", "readout_from_world")
    differ = {k: [b.get(k), d.get(k)] for k in shared if b.get(k) != d.get(k)}
    ok = (not differ and b.get("replicates") == REPLICATES
          and b.get("partition_sha1") == PARTITION_SHA1 and d.get("partition_sha1") == PARTITION_SHA1
          and b.get("world_read_sha1") == WORLD_READ_SHA1 and d.get("world_read_sha1") == WORLD_READ_SHA1
          and rows[ARM_BIO]["n"] == REPLICATES and rows[ARM_RAND]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"`{ARM_BIO}` from `{r['runs'][ARM_BIO]}` and `{ARM_RAND}` from "
                                  f"`{r['runs'][ARM_RAND]}`: circuits {b['circuit_size']}, tasks {b['task_names']} "
                                  f"with read-out widths {b['task_readout_widths']}, {b['replicates']} replicates "
                                  f"each at seed0 {b['seed0']}, basis {b['basis']}, world read fingerprint "
                                  f"{b['world_read_sha1']} (expected {r['expected_world_read_sha1']}), matched-random "
                                  f"partition {b['partition_sha1']} of {b['n_groups']} groups (expected "
                                  f"{r['expected_partition_sha1']}), the fields differing between the runs being "
                                  f"{differ}",
          "verdict": "MET -- one configuration in two artifacts" if ok else
          f"FALSIFIER FIRED -- the runs are not one configuration: {differ}, replicates "
          f"{b.get('replicates')}/{d.get('replicates')}, partitions {b.get('partition_sha1')}/"
          f"{d.get('partition_sha1')}, world {b.get('world_read_sha1')}/{d.get('world_read_sha1')}"}

    verdicts = {}
    for cid, key, field, short in (("T2", "forgetting_contrast", "mean_forgetting", "forgetting"),
                                   ("T3", "diagonal_contrast", "mean_diagonal", "diagonal")):
        est = r.get(key) or {"delta": None}
        if est.get("delta") is None:
            verdicts[cid] = {"id": cid, "measured": "the paired contrast was not computable",
                             "verdict": "REFUSED -- the paired contrast was not computable"}
            continue
        measured = (f"`{ARM_BIO}`'s {short} is {rows[ARM_BIO][field]:.4f} and `{ARM_RAND}`'s is "
                    f"{rows[ARM_RAND][field]:.4f}, so the contrast is {est['delta']:+.4f} on a sem of "
                    f"{est['sem']:.4f} ({_sg(est['sigma'])} sigma) over {est['n']} paired replicates")
        verdicts[cid] = {
            "id": cid, "measured": measured,
            "verdict": (f"MET -- the {short} contrast does not resolve, {est['delta']:+.4f} at "
                        f"{_sg(est['sigma'])} sigma" if abs(est["delta"]) <= SAME else
                        f"FALSIFIER FIRED -- the {short} contrast resolves at {est['delta']:+.4f} at "
                        f"{_sg(est['sigma'])} sigma" if abs(est["delta"]) >= SAME_FIRES else
                        f"NULL -- {est['delta']:+.4f}, between {SAME:.2f} and {SAME_FIRES:.2f}")}
    j2, j3 = verdicts["T2"], verdicts["T3"]

    weak = []
    for a in (ARM_BIO, ARM_RAND):
        above = rows[a]["mean_diagonal"] - rows[a]["chance"]
        ch = rows[a]["paired"]
        if not (above >= CARRIES and ch["delta"] is not None and ch["delta"] >= CARRIES
                and (ch["sigma"] or 0) >= SIGMA):
            weak.append(a)
    j4 = {"id": "T4", "measured": f"diagonals above chance: `{ARM_BIO}` "
                                  f"{rows[ARM_BIO]['mean_diagonal'] - rows[ARM_BIO]['chance']:+.4f}, `{ARM_RAND}` "
                                  f"{rows[ARM_RAND]['mean_diagonal'] - rows[ARM_RAND]['chance']:+.4f}; paired "
                                  f"channel: `{ARM_BIO}` {rows[ARM_BIO]['paired']['delta']:+.4f} at "
                                  f"{_sg(rows[ARM_BIO]['paired']['sigma'])} sigma, `{ARM_RAND}` "
                                  f"{rows[ARM_RAND]['paired']['delta']:+.4f} at "
                                  f"{_sg(rows[ARM_RAND]['paired']['sigma'])} sigma",
          "verdict": "MET -- both arms are learned and earned" if not weak else
          f"FALSIFIER FIRED -- not learned or not earned in {weak}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or {}
    if not all(rows.get(a, {}).get("ok") for a in (ARM_BIO, ARM_RAND)):
        print("== the basis contrast on the earned label ==\n   REFUSED -- both arms are not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the basis contrast on the earned label ==")
    print(f"   `{ARM_BIO}` from `{r['runs'][ARM_BIO]}` against `{ARM_RAND}` from `{r['runs'][ARM_RAND]}`")
    print(f"\n   {'arm':>15} {'final':>8} {'diagonal':>9} {'forget':>8} {'forget sem':>11} {'channel':>9} {'sigma':>6}")
    for a in (ARM_BIO, ARM_RAND):
        row = rows[a]
        print(f"   {a:>15} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} {row['mean_forgetting']:8.4f} "
              f"{statistics.stdev(row['forgetting']) / math.sqrt(row['n']):11.4f} {row['paired']['delta']:+9.4f} "
              f"{_sg(row['paired']['sigma']):>6}")
    for key, name in (("forgetting_contrast", "forgetting"), ("diagonal_contrast", "diagonal")):
        est = r.get(key) or {}
        if est.get("delta") is not None:
            print(f"   the {name} contrast, `{ARM_BIO}` minus `{ARM_RAND}`: {est['delta']:+.4f} on a sem of "
                  f"{est['sem']:.4f} ({_sg(est['sigma'])} sigma)")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (eleven audits left the basis contrast a null on the state read-out; this asks it on a task whose")
    print("    answer is read from the environment, pairing the two arms by replicate and by partition fingerprint)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bio", type=Path, default=PENALTY)
    ap.add_argument("--rand", type=Path, default=RANDOM)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(bio_path=args.bio, rand_path=args.rand)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
