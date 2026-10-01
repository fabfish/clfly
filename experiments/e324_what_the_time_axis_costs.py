"""E324 -- what the trial's time axis costs: the five arms on a sequence suite, against the same five on a sustained one.

`e322` measured that every task in this benchmark delivers a stimulus equal to its first step **exactly**, so the
trial's time axis carried nothing. `e323` built the first writer that changes with time -- one symbol for the first
half of the trial and another for the second, labelled by their ordered pair -- and measured on the **frozen**
network that the connectome carries the first symbol across the boundary (+0.25 at its worst) while the read-out
decodes the conjunction only weakly (+0.083). Both are statements about the substrate before any training.

This unit trains. `e8_rate_network` gained a `--sequence` flag, and because `make_sequence_suite` returns the same
`RateTask` as the sustained builder, the five arms run on it **unchanged** -- which is what `e323` predicted. The
comparison is against the sustained suite at the same circuit, the same read-out subset and the same seeds, which
`e317` already ran, so the two artifacts differ in exactly one field.

Four claims, registered before the sequence run's reading was taken. `delta` is the sequence run minus the sustained
one, paired by replicate index since the seeds are shared.

- **T1 -- one configuration in two suits.** Every `config` field agrees except the builder, the read-out subset
  fingerprint agrees, and the replicate counts agree. **Falsifier**: any other field differing, a differing read-out
  draw, or a differing replicate count.
- **T2 -- the sequence task is harder to fit.** `naive`'s `final_accuracy` is **lower** on the sequence suite by at
  least **0.05**. The pair label needs a symbol carried across the boundary, which the sustained label never does.
  **Falsifier**: higher by 0.05 or more. **Null**: within 0.05 either way.
- **T3 -- and the method ordering survives the time axis.** `replay` is ahead of all three penalty arms on
  `final_accuracy` on the sequence suite, each contrast resolved at **2 sigma**. **Falsifier**: one that is not, or
  one that resolves the other way.
- **T4 -- and the time axis raises what a task costs the one after it.** `naive`'s `mean_forgetting` is **higher**
  on the sequence suite by at least **0.02**, the state now having to hold a symbol the next task's training
  overwrites. **Falsifier**: lower by 0.02 or more. **Null**: within 0.02 either way.

**What it cannot do.** *Five replicates per arm* puts one standard error of a paired accuracy difference near 0.02
to 0.05, so T2's 0.05 bar is one to two of them. *Two suites at one circuit, one read-out width, one penalty and one
order*: the difference could be the boundary, the alphabet, the four classes being pairs rather than singletons, or
the second noise draw. *The two runs are not the same trained models*, since the labels differ and the gradients
follow them, so every delta is the whole trajectory's. *And nothing here closes a loop*: the sequence task's input
still does not depend on the agent's output, so this is the first temporal task and not yet a game.
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
SUSTAINED = RUNS / "e317_five_as_built.json"
SEQUENCE = RUNS / "e324_sequence_five_as_built.json"
#: the arm the difficulty and retention claims are stated on, and the three the ordering claim compares against
NAIVE = "naive"
REPLAY = "replay"
PENALTIES = ("ewc", "ewc-block", "ewc-block-rand")
#: the three thresholds, each with its falsifier on the other side
BAR_ACCURACY = 0.05
BAR_FORGETTING = 0.02
SIGMA = 2.0
#: fields a config may differ in without the comparison ceasing to be one configuration in two suits
IGNORED_CONFIG = ("json_out", "sequence")
CLAIMS = (
    ("T1", "one configuration in two suits",
     "Every config field agrees except the builder, the read-out fingerprint agrees, and the replicate counts agree",
     "falsifier: any other field differing, a differing read-out draw, or a differing replicate count"),
    ("T2", f"the sequence task is harder to fit: `{NAIVE}` reads lower by {BAR_ACCURACY:.2f}",
     f"`{NAIVE}`'s final accuracy is lower on the sequence suite by at least {BAR_ACCURACY:.2f}",
     "falsifier: higher by that much"),
    ("T3", f"and the method ordering survives the time axis: `{REPLAY}` ahead of every penalty arm",
     f"All three accuracy contrasts favour `{REPLAY}` on the sequence suite, each resolved at {SIGMA} sigma",
     "falsifier: one that is not, or one that resolves the other way"),
    ("T4", f"and the time axis raises what a task costs the one after it, by {BAR_FORGETTING:.2f}",
     f"`{NAIVE}`'s mean forgetting is higher on the sequence suite by at least {BAR_FORGETTING:.2f}",
     "falsifier: lower by that much"),
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
    """``one - two`` paired by replicate index, with its standard error."""
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem,
            "sigma": abs(mean) / sem if sem else float("inf")}


def config_diff(a: dict, b: dict) -> dict:
    """The `config` fields the two runs disagree on, ignoring the ones the comparison is allowed to move."""
    ca, cb = a.get("config", {}), b.get("config", {})
    keys = sorted(set(ca) | set(cb))
    out = {}
    for key in keys:
        if key in IGNORED_CONFIG:
            continue
        va, vb = ca.get(key, None), cb.get(key, None)
        if va != vb:
            out[key] = [va, vb]
    return out


def replicates(run: dict, arm: str) -> list[dict]:
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def arm_contrast(run: dict, one: str, two: str, metric: str) -> dict:
    """``one - two`` on one artifact, paired by replicate index."""
    return paired([r[metric] for r in replicates(run, one)], [r[metric] for r in replicates(run, two)])


def reading(sustained_path=SUSTAINED, sequence_path=SEQUENCE) -> dict:
    a, b = load(sustained_path), load(sequence_path)
    if not a or not b:
        return {"runs": 0, "missing": [str(p) for p, d in ((sustained_path, a), (sequence_path, b)) if not d]}
    arms = sorted(set(a.get("methods", {})) & set(b.get("methods", {})))
    diffs = {arm: paired([r["final_accuracy"] for r in replicates(b, arm)],
                         [r["final_accuracy"] for r in replicates(a, arm)]) for arm in arms}
    forgets = {arm: paired([r["mean_forgetting"] for r in replicates(b, arm)],
                           [r["mean_forgetting"] for r in replicates(a, arm)]) for arm in arms}
    return {
        "runs": 2,
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "n_replicates": {arm: [len(replicates(a, arm)), len(replicates(b, arm))] for arm in arms},
        "suites": [a.get("config", {}).get("input_overlap"), b.get("config", {}).get("sequence")],
        "task_names": {"sustained": [t.get("name") for t in a.get("tasks", [])],
                       "sequence": [t.get("name") for t in b.get("tasks", [])]},
        "config_diff": config_diff(a, b),
        "accuracy": diffs, "forgetting": forgets,
        #: the line's headline contrast, recomputed inside EACH artifact: `replay` minus each penalty arm
        "ordering": {arm: {"sustained": arm_contrast(a, REPLAY, arm, "final_accuracy"),
                           "sequence": arm_contrast(b, REPLAY, arm, "final_accuracy")} for arm in PENALTIES},
        "sustained": {arm: {"final_accuracy": a["methods"][arm].get("final_accuracy"),
                            "mean_forgetting": a["methods"][arm].get("mean_forgetting")} for arm in arms},
        "sequence": {arm: {"final_accuracy": b["methods"][arm].get("final_accuracy"),
                           "mean_forgetting": b["methods"][arm].get("mean_forgetting")} for arm in arms},
        #: through the shared helper, because the corpus spells a duration three ways and a reader that keys on
        #: one of them cannot see the other two (`e205`). The sustained run writes `timing_s` and the sequence run
        #: does too, but the reader is what makes that a property of the two artifacts rather than of this code.
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    counts = r["n_replicates"]
    same_counts = all(v[0] == v[1] for v in counts.values())
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, replicate counts {counts}; "
                                  f"config fields differing {r['config_diff']}",
          "verdict": "MET -- one configuration in two suits" if
          r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1] and same_counts
          and not r["config_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, read-out {r['readout']}"}

    nv = r["accuracy"].get(NAIVE, {})
    down = nv.get("delta")
    j2 = {"id": "T2", "measured": f"`{NAIVE}` final accuracy {r['sustained'].get(NAIVE, {}).get('final_accuracy')} "
                                  f"sustained against {r['sequence'].get(NAIVE, {}).get('final_accuracy')} sequence, "
                                  f"delta {down if down is None else f'{down:+.4f}'}",
          "verdict": ("REFUSED -- the arm is missing from one run" if down is None else
                      f"MET -- the sequence suite reads {abs(down):.4f} lower" if down <= -BAR_ACCURACY else
                      f"FALSIFIER FIRED -- it reads {down:+.4f} higher" if down >= BAR_ACCURACY else
                      f"NULL -- {down:+.4f}, within {BAR_ACCURACY:.2f}")}

    rows = [(arm, r.get("ordering", {}).get(arm, {})) for arm in PENALTIES]
    behind, weak = [], []
    for arm, v in rows:
        seq = v.get("sequence", {})
        d, sigma = seq.get("delta"), seq.get("sigma")
        if d is None:
            weak.append(arm)
            continue
        if d <= 0:
            behind.append(arm)
        elif sigma is None or sigma < SIGMA:
            weak.append(arm)
    detail = "; ".join(f"{arm} {v['sequence']['delta']:+.4f} at {v['sequence']['sigma']:.2f} sigma (sustained "
                       f"{v['sustained']['delta']:+.4f} at {v['sustained']['sigma']:.2f})"
                       for arm, v in rows if v.get("sequence", {}).get("delta") is not None)
    j3 = {"id": "T3", "measured": f"`{REPLAY}` minus each penalty arm on the sequence suite, paired: {detail}",
          "verdict": f"MET -- `{REPLAY}` is ahead of every penalty arm and every contrast resolves" if
          not behind and not weak and len(rows) == len(PENALTIES) else
          f"FALSIFIER FIRED -- not ahead on {behind}, unresolved on {weak}"}

    fv = r["forgetting"].get(NAIVE, {})
    up = fv.get("delta")
    j4 = {"id": "T4", "measured": f"`{NAIVE}` mean forgetting {r['sustained'].get(NAIVE, {}).get('mean_forgetting')} "
                                  f"sustained against {r['sequence'].get(NAIVE, {}).get('mean_forgetting')} sequence, "
                                  f"delta {up if up is None else f'{up:+.4f}'}",
          "verdict": ("REFUSED -- the arm is missing from one run" if up is None else
                      f"MET -- the sequence suite forgets {up:.4f} more" if up >= BAR_FORGETTING else
                      f"FALSIFIER FIRED -- it forgets {up:+.4f} less" if up <= -BAR_FORGETTING else
                      f"NULL -- {up:+.4f}, within {BAR_FORGETTING:.2f}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("runs"):
        print(f"== the sequence suite against the sustained one ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the sequence suite against the sustained one ==")
    print(f"   circuits {r['circuits']}  read-out {r['readout']}")
    print(f"   tasks sustained {r['task_names']['sustained']}")
    print(f"   tasks sequence  {r['task_names']['sequence']}")
    print(f"   config fields differing: {r['config_diff'] or 'none'}")
    print(f"\n   {'arm':16} {'sustained':>10} {'sequence':>10} {'delta':>9} {'sigma':>7} "
          f"{'forget s':>9} {'forget q':>9} {'delta':>9} {'sigma':>7}")
    for arm in sorted(r["accuracy"]):
        a, b = r["sustained"].get(arm, {}), r["sequence"].get(arm, {})
        va, vb = r["accuracy"][arm], r["forgetting"][arm]
        print(f"   {arm:16} {a.get('final_accuracy'):10.4f} {b.get('final_accuracy'):10.4f} "
              f"{va['delta']:+9.4f} {va['sigma']:7.2f} "
              f"{a.get('mean_forgetting'):9.4f} {b.get('mean_forgetting'):9.4f} "
              f"{vb['delta']:+9.4f} {vb['sigma']:7.2f}")
    print(f"   timing_s {r['timing_s']}")
    print(f"\n   {'contrast':26} {'sustained':>22} {'sequence':>22}")
    for arm in PENALTIES:
        v = r.get("ordering", {}).get(arm, {})
        s, q = v.get("sustained", {}), v.get("sequence", {})
        print(f"   {REPLAY}-{arm:21} {s.get('delta'):+9.4f} at {s.get('sigma'):5.2f} "
              f"{q.get('delta'):+9.4f} at {q.get('sigma'):5.2f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e322` measured that the trial's time axis carried nothing; `e323` built the writer that gives it")
    print("    one and measured it frozen; this asks what training on it costs, five arms on each side)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sustained", type=Path, default=SUSTAINED)
    ap.add_argument("--sequence", type=Path, default=SEQUENCE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.sustained, args.sequence)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
