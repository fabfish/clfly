"""E331 -- the arm ordering under the loop: the line's headline contrast asked on the instrument with headroom.

`e276` read the line's strongest method contrast -- `replay` against each penalty arm, paired over the same
replicates -- at twelve sigma. `e321` found it surviving the **order** inversion in sign and not in size. `e324`
found the **time axis** halving it and taking its strongest edge, against the size-matched random control, from
5.92 sigma to **0.92**. And the thread since `e325` has been building a **closed loop**, on which every ordering
question so far has been asked on an environment whose cue is two fixed vectors: `e330` resolved that the loop's one
apparent effect was a property of that ceiling rather than of the loop.

So the question this unit asks is the line's own, on the instrument `e329` built: **does the ordering survive the
loop?** Five arms, on the **noisy eight-symbol** environment where `naive` reads about 0.51 against a chance of
0.125, at feedback strength **0.0** and **0.5** -- the open loop and the middling setting -- with five replicates
each and the same seeds, so the runs are one configuration in two loops.

Four claims, registered before these runs' readings. Every contrast is **paired by replicate index**, within a run
for the ordering and across runs for the loop's effect.

- **T1 -- one configuration in two loops.** Same circuit, read-out fingerprint, task names, replicate counts and
  environment draw, the last differing only in the strength. **Falsifier**: any other field differing.
- **T2 -- and the headline holds on the open loop.** `replay` is ahead of **all three** penalty arms on accuracy at
  strength 0.0, each contrast resolved at **2 sigma**. This is `e276`'s claim re-asked on an environment with
  headroom rather than on the saturated one. **Falsifier**: one contrast that does not favour `replay`, or one
  below 2 sigma.
- **T3 -- and it survives the loop.** The same, at strength 0.5. **Falsifier**: one that does not, or one below
  2 sigma. This is `e324`'s answer for the time axis put to the loop.
- **T4 -- and the loop moves the contrast.** The mean over the three penalty arms of the difference between the
  closed-loop and open-loop `replay`-minus-penalty margins differs from zero by at least **0.03**. `e324` found the
  time axis **shrinking** this contrast; whether closing the loop shrinks it, leaves it, or grows it is what is
  registered here. **Falsifier**: a move of less than 0.01. **Null**: between 0.01 and 0.03.

**What it cannot do.** *Five replicates*, which put one standard error of a paired accuracy difference near 0.02 at
this per-replicate spread, so T4 can resolve 0.03 and not much less, and T2's and T3's three contrasts share
`replay`'s replicates and are not independent. *Two of the four settings*: strengths 0.25 and 1.0 are not run.
*One circuit, one read-out width, one noise level and one alphabet*: the ordering is this environment's, and `e324`
is the standing evidence that a suite's ordering is not a property of the substrate alone. *And there is still no
reward*: the label is the cue, delivered at step 0, and the agent's action is an input rather than a decision.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

RUNS = Path("runs")
PATHS = {"0p00": RUNS / "e331_arms_scale_0p00.json", "0p50": RUNS / "e331_arms_scale_0p50.json"}
ORDER = ("0p00", "0p50")
SCALES = {"0p00": 0.0, "0p50": 0.5}
REPLAY = "replay"
PENALTIES = ("ewc", "ewc-block", "ewc-block-rand")
ARMS = ("naive",) + PENALTIES + (REPLAY,)
SIGMA = 2.0
MOVED = 0.03
STILL = 0.01
CLAIMS = (
    ("T1", "one configuration in two loops",
     "Same circuit, read-out fingerprint, task names, replicate counts and environment draw, the last differing only "
     "in the strength",
     "falsifier: any other field differing"),
    ("T2", f"and the headline holds on the open loop: `{REPLAY}` ahead of all three penalty arms at {SIGMA} sigma",
     f"All three accuracy contrasts favour `{REPLAY}` at strength {SCALES['0p00']}, each resolved at {SIGMA} sigma",
     "falsifier: one that does not favour it, or one below that"),
    ("T3", f"and it survives the loop: the same at strength {SCALES['0p50']}",
     f"All three accuracy contrasts favour `{REPLAY}` at strength {SCALES['0p50']}, each resolved at {SIGMA} sigma",
     "falsifier: one that does not favour it, or one below that"),
    ("T4", f"and the loop moves the contrast, by {MOVED:.2f}",
     f"The mean over the three penalty arms of the closed-minus-open `{REPLAY}`-minus-penalty margin differs from "
     f"zero by at least {MOVED:.2f}",
     f"falsifier: a move of less than {STILL:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str) -> list[dict]:
    if not run:
        return []
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def arm_contrast(run: dict, one: str, two: str, metric: str = "final_accuracy") -> dict:
    return paired([r[metric] for r in replicates(run, one)], [r[metric] for r in replicates(run, two)])


def reading(paths=None) -> dict:
    paths = paths or PATHS
    runs = {tag: load(path) for tag, path in paths.items()}
    present = [tag for tag in ORDER if runs.get(tag)]
    if len(present) < 2:
        return {"runs": len(present), "missing": [str(paths[t]) for t in ORDER if not runs.get(t)]}
    a, b = runs[present[0]], runs[present[1]]
    arms = [arm for arm in ARMS if replicates(a, arm) and replicates(b, arm)]
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    ordering = {arm: {"open": arm_contrast(a, REPLAY, arm), "loop": arm_contrast(b, REPLAY, arm)}
                for arm in PENALTIES if arm in arms}
    return {
        "runs": 2,
        "levels": present,
        "scales": [SCALES[t] for t in present],
        "arms": arms,
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "n_replicates": {arm: [len(replicates(a, arm)), len(replicates(b, arm))] for arm in arms},
        "config_diff": {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                        if k not in ("json_out", "loop_scale") and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k != "scale" and ea.get(k) != eb.get(k)},
        "env": ea,
        "accuracy": {arm: paired([r["final_accuracy"] for r in replicates(b, arm)],
                                 [r["final_accuracy"] for r in replicates(a, arm)]) for arm in arms},
        "forgetting": {arm: paired([r["mean_forgetting"] for r in replicates(b, arm)],
                                   [r["mean_forgetting"] for r in replicates(a, arm)]) for arm in arms},
        "ordering": ordering,
        "open": {arm: {"final_accuracy": a["methods"][arm].get("final_accuracy"),
                       "mean_forgetting": a["methods"][arm].get("mean_forgetting")} for arm in arms},
        "loop": {arm: {"final_accuracy": b["methods"][arm].get("final_accuracy"),
                       "mean_forgetting": b["methods"][arm].get("mean_forgetting")} for arm in arms},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def _side(rows: list[tuple[str, dict]]) -> tuple[list[str], list[str]]:
    """Which penalty arms `replay` is behind on, and which are unresolved."""
    behind = [arm for arm, v in rows
              if v.get("delta") is None or v["delta"] <= 0]
    weak = [arm for arm, v in rows
            if v.get("delta") is not None and v["delta"] > 0
            and (v.get("sigma") is None or v["sigma"] < SIGMA)]
    return behind, weak


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "ordering" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    counts = r["n_replicates"]
    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1]
            and all(v[0] == v[1] and v[0] > 1 for v in counts.values()))
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks "
                                  f"{r['task_names'][0]}, arms {r['arms']}, counts {counts}, environment "
                                  f"{r['env']}, config differing {r['config_diff']}, environment differing "
                                  f"{r['env_diff']}",
          "verdict": "MET -- one configuration in two loops" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, counts {counts}"}

    rows_open = [(arm, v["open"]) for arm, v in r["ordering"].items()]
    rows_loop = [(arm, v["loop"]) for arm, v in r["ordering"].items()]
    for cid, rows, side in (("T2", rows_open, "open"), ("T3", rows_loop, "closed")):
        behind, weak = _side(rows)
        detail = "; ".join(f"{arm} {v.get('delta'):+.4f} at {v.get('sigma'):.2f} sigma" for arm, v in rows
                           if v.get("delta") is not None)
        verdict = (f"MET -- `{REPLAY}` is ahead of all three penalty arms on the {side} loop, every contrast "
                   f"resolving" if rows and not behind and not weak else
                   f"FALSIFIER FIRED -- not ahead on {behind}, unresolved on {weak}")
        if not rows:
            verdict = "REFUSED -- no penalty arm is present in both runs"
        measured = f"the {side} loop, `{REPLAY}` minus each penalty arm: {detail}"
        if cid == "T2":
            j2 = {"id": cid, "measured": measured, "verdict": verdict}
        else:
            j3 = {"id": cid, "measured": measured, "verdict": verdict}

    moves = [(arm, v["loop"]["delta"] - v["open"]["delta"]) for arm, v in r["ordering"].items()
             if v["open"].get("delta") is not None and v["loop"].get("delta") is not None]
    mean_move = statistics.fmean([m for _, m in moves]) if moves else None
    detail = "; ".join(f"{arm} {m:+.4f}" for arm, m in moves)
    j4 = {"id": "T4", "measured": f"closed minus open `{REPLAY}`-minus-penalty margins: {detail}, mean "
                                  f"{'n/a' if mean_move is None else f'{mean_move:+.4f}'}",
          "verdict": ("REFUSED -- no penalty arm is present in both runs" if mean_move is None else
                      f"MET -- the loop moves the contrast by {abs(mean_move):.4f}" if abs(mean_move) >= MOVED else
                      f"FALSIFIER FIRED -- it moves by only {abs(mean_move):.4f}" if abs(mean_move) < STILL else
                      f"NULL -- {abs(mean_move):.4f}, between {STILL:.2f} and {MOVED:.2f}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if r.get("runs", 0) < 2:
        print(f"== the ordering under the loop ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the ordering under the loop ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}, arms {r['arms']}")
    print(f"   environment: {r['env']}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'arm':16} {'open':>9} {'loop':>9} {'delta':>9} {'sigma':>7} "
          f"{'forget o':>9} {'forget l':>9} {'delta':>9} {'sigma':>7}")
    for arm in r["arms"]:
        a, b = r["open"].get(arm, {}), r["loop"].get(arm, {})
        va, vb = r["accuracy"][arm], r["forgetting"][arm]
        print(f"   {arm:16} {a.get('final_accuracy'):9.4f} {b.get('final_accuracy'):9.4f} "
              f"{va['delta']:+9.4f} {va['sigma']:7.2f} "
              f"{a.get('mean_forgetting'):9.4f} {b.get('mean_forgetting'):9.4f} "
              f"{vb['delta']:+9.4f} {vb['sigma']:7.2f}")
    print(f"\n   {'contrast':26} {'open':>18} {'loop':>18} {'move':>8}")
    for arm in PENALTIES:
        v = r["ordering"].get(arm)
        if not v:
            continue
        o, l = v["open"], v["loop"]
        print(f"   {REPLAY}-{arm:21} {o.get('delta'):+8.4f} at {o.get('sigma'):5.2f} "
              f"{l.get('delta'):+8.4f} at {l.get('sigma'):5.2f} "
              f"{l.get('delta') - o.get('delta'):+8.4f}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` read this contrast at twelve sigma, `e321` found it surviving the order inversion and `e324`")
    print("    found the time axis halving it; this asks the loop, on the first environment with headroom)")
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
