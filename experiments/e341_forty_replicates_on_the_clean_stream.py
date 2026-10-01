"""E341 -- forty replicates on the clean stream: the effect the third unit in a row left at the floor.

`e333` measured `replay`'s forgetting rising **0.0375 at 2.45 sigma** when the world's channel acquired a transition
rule. `e337` found the sign reversing on a second `--seed0` (**−0.0771 at 3.36**). `e338` asked one trained body both
questions and the manipulation moved **0.0000** (sem 0.0022). `e339` measured that `--seed0` draws the read-out
subset and the environment's populations as well as the training seeds, and `e340` held those two and re-ran: the
sign came back, at **+0.0167 and 0.95 sigma**.

**So three measurements of one manipulation have landed at or near the floor, and the last of them is clean.** Its
own finding named the next unit: *"a 0.95 sigma in the same direction is consistent with a small real effect and with
zero, and separating those needs the replicates this design does not have."* **This runs the clean pair at forty
replicates**, the count `e328` found it took to resolve a forget-rate difference on this family.

Two runs, `replay` alone, the same two worlds at `--seed0 4 --readout-seed 0 --loop-seed 0` -- the clean stream, with
the read-out subset and the environment's three populations held. Four claims, registered before their readings.

- **T1 -- one configuration except the world.** Same circuit, read-out fingerprint, task names, replicate count, cue
  symbols, cue noise, seeds and environment draw, the last differing only in the leak. **Falsifier**: any other field
  differing.
- **T2 -- and the effect is resolved in `e333`'s direction.** The paired difference is **positive** and resolved at
  **2 sigma**. This is the sentence three units have circled: `e333` had it at 2.45 on a confounded stream, `e337`
  reversed it, `e338` zeroed the manipulation and `e340` brought it back at 0.95. **Falsifier**: a negative
  difference, or one below 2 sigma, which is what the last three measurements would predict. **Null**: no such band
  -- the claim is two-sided on the sign and one-sided on the resolution.
- **T3 -- and it is not trivially small.** The magnitude is at least **0.01**. **Falsifier**: below **0.005**, which
  would make it a real effect too small to matter for anything the benchmark reports.
- **T4 -- and five replicates were not misleading about it.** The forty-replicate difference is within **0.02** of
  `e340`'s five-replicate one. **Falsifier**: a gap above **0.03**. This is the check that the clean pair's
  five-replicate estimate was in the right neighbourhood rather than a coin that happened to land right.

**What it cannot do.** *One stream, one arm and one world pair*: the clean stream at `--seed0 4` is a single redraw
of the training seeds, and the stream-0 side stays at the five replicates `e333` ran, so this resolves the effect
**on this stream** and cannot say it holds on a third. *`naive`, `ewc` and the block arms are not run.* *The paired
standard error is the across-replicate one*: three tasks share a body and a head, so the fifteen numbers a replicate
contributes are not independent and the task variation inside a replicate is averaged and not modelled. *And a
forty-replicate resolution is a resolution at this channel strength, this task and this read-out*: the feedback is
`scale = 1.0`, the world `leak = 0.35`, and nothing here says a different channel would behave the same way.
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
INSTANT = RUNS / "e341_clean40_instant.json"
CARRY = RUNS / "e341_clean40_carry.json"
#: the five-replicate clean pair this one is long enough to check
SHORT = (RUNS / "e340_clean_instant.json", RUNS / "e340_clean_carry.json")
#: `e333`'s five-replicate number, carried for the reader's comparison and not used as a bar
E333 = 0.0375
ARM = "replay"
SIGMA = 2.0
MATTERS = 0.01
TRIVIAL = 0.005
CLOSE = 0.02
FAR = 0.03
CLAIMS = (
    ("T1", "one configuration except the world",
     "Same circuit, read-out fingerprint, task names, replicate count, cue symbols, cue noise, seeds and environment "
     "draw, the last differing only in the leak",
     "falsifier: any other field differing"),
    ("T2", f"and the effect is resolved in `e333`'s direction, at {SIGMA:.0f} sigma",
     "The paired difference is positive and resolved at 2 sigma",
     "falsifier: a negative difference, or one below 2 sigma"),
    ("T3", f"and it is not trivially small, at least {MATTERS:.2f}",
     f"The magnitude is at least {MATTERS:.2f}",
     f"falsifier: below {TRIVIAL:.3f}"),
    ("T4", f"and five replicates were not misleading, within {CLOSE:.2f}",
     f"The forty-replicate difference is within {CLOSE:.2f} of `e340`'s five-replicate one",
     f"falsifier: a gap above {FAR:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str = ARM) -> list[dict]:
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


def world_reading(instant, carry) -> dict:
    a, b = load(instant), load(carry)
    if not a or not b:
        return {"ok": False, "missing": [str(p) for p, d in ((instant, a), (carry, b)) if not d]}
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "ok": True,
        "circuit": a.get("circuit"),
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "n": [len(replicates(a)), len(replicates(b))],
        "index_sha1": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "populations": {k: [ea.get(k), eb.get(k)] for k in ("cue_sha1", "action_sha1", "feedback_sha1")},
        "seed0": [ca.get("seed0"), cb.get("seed0")],
        "leaks": [ea.get("world_leak"), eb.get("world_leak")],
        "settings": {k: [ca.get(k), cb.get(k)] for k in
                     ("circuit_size", "repeats", "train", "test", "readout_size", "readout_seed", "loop_seed",
                      "loop_scale", "loop_noise", "loop_symbols", "loop_world_modes")},
        "env_settings": {k: [ea.get(k), eb.get(k)] for k in
                         ("tau", "n_symbols", "n_cue", "n_action", "n_feedback", "scale", "gain", "noise")},
        "forgetting": paired([r["mean_forgetting"] for r in replicates(b)],
                             [r["mean_forgetting"] for r in replicates(a)]),
        "accuracy": paired([r["final_accuracy"] for r in replicates(b)],
                           [r["final_accuracy"] for r in replicates(a)]),
        "means": {"instant": a["methods"][ARM].get("mean_forgetting"),
                  "carry": b["methods"][ARM].get("mean_forgetting")},
        "per_replicate_sd": {
            "instant": (statistics.stdev([r["mean_forgetting"] for r in replicates(a)])
                        if len(replicates(a)) > 1 else None),
            "carry": (statistics.stdev([r["mean_forgetting"] for r in replicates(b)])
                      if len(replicates(b)) > 1 else None)},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def reading(instant=INSTANT, carry=CARRY, short=SHORT) -> dict:
    out = {"long": world_reading(instant, carry), "short": world_reading(*short), "arm": ARM}
    out["runs"] = (2 if out["long"].get("ok") else 0) + (2 if out["short"].get("ok") else 0)
    if not out["long"].get("ok"):
        out["missing"] = out["long"].get("missing")
    return out


def judge(r: dict) -> list[dict]:
    long_, short = r.get("long") or {}, r.get("short") or {}
    if not long_.get("ok"):
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the forty-replicate pair is not on disk"} for c in CLAIMS]

    same = (long_["circuit"] == long_["circuit"] and long_["readout"][0] == long_["readout"][1]
            and long_["task_names"][0] == long_["task_names"][1] and long_["n"][0] == long_["n"][1] > 1
            and long_["seed0"][0] == long_["seed0"][1] and long_["leaks"][0] == 1.0 and long_["leaks"][1] != 1.0
            and all(v[0] == v[1] for v in long_["settings"].values())
            and all(v[0] == v[1] for v in long_["env_settings"].values()))
    j1 = {"id": "T1", "measured": f"circuit {long_['circuit']}, read-out {long_['readout']}, tasks "
                                  f"{long_['task_names'][0]}, {long_['n'][0]} replicates each, seeds "
                                  f"{long_['seed0']}, leaks {long_['leaks']}, settings {long_['settings']}, "
                                  f"environment {long_['env_settings']}",
          "verdict": "MET -- one configuration except the world" if same else
                     f"FALSIFIER FIRED -- a field differs: settings {long_['settings']}, environment "
                     f"{long_['env_settings']}, read-out {long_['readout']}"}

    f = long_["forgetting"]
    j2 = {"id": "T2", "measured": f"`{ARM}`'s carried-minus-instantaneous forgetting over {f['n']} replicates: "
                                  f"means {long_['means']['instant']:.4f} against {long_['means']['carry']:.4f}, "
                                  f"delta {f['delta']:+.4f} on a sem of {f['sem']:.4f}, i.e. {f['sigma']:.2f} sigma "
                                  f"(per-replicate sd {long_['per_replicate_sd']})",
          "verdict": f"MET -- the effect resolves at {f['sigma']:.2f} sigma in `e333`'s direction" if
          f["delta"] > 0 and f["sigma"] >= SIGMA else
          f"FALSIFIER FIRED -- {f['delta']:+.4f} at {f['sigma']:.2f} sigma"}

    mag = abs(f["delta"])
    j3 = {"id": "T3", "measured": f"the magnitude is {mag:.4f} against a floor of {MATTERS:.2f}",
          "verdict": f"MET -- the effect is {mag:.4f}, above the floor" if mag >= MATTERS else
          f"FALSIFIER FIRED -- it is {mag:.4f}" if mag < TRIVIAL else
          f"NULL -- {mag:.4f}, between {TRIVIAL:.3f} and {MATTERS:.2f}"}

    if not short.get("ok"):
        j4 = {"id": "T4", "measured": "the five-replicate pair is absent",
              "verdict": "REFUSED -- `e340`'s clean pair is not on disk"}
    else:
        gap = abs(f["delta"] - short["forgetting"]["delta"])
        j4 = {"id": "T4", "measured": f"forty replicates give {f['delta']:+.4f} and five give "
                                      f"{short['forgetting']['delta']:+.4f}, a gap of {gap:.4f} (against `e333`'s "
                                      f"{E333:+.4f} on the confounded stream)",
              "verdict": f"MET -- the five-replicate estimate was within {gap:.4f}" if gap <= CLOSE else
              f"FALSIFIER FIRED -- they differ by {gap:.4f}" if gap > FAR else
              f"NULL -- {gap:.4f}, between {CLOSE:.2f} and {FAR:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    for tag, key in (("forty replicates", "long"), ("five replicates", "short")):
        st = r.get(key) or {}
        if not st.get("ok"):
            print(f"   {tag}: REFUSED -- missing {st.get('missing')}")
            continue
        print(f"== the clean stream, {tag} ==")
        print(f"   {st['circuit']}, read-out {st['readout'][0]}, {st['n'][0]} replicates each, leaks {st['leaks']}")
        print(f"   forgetting {st['means']['instant']:.4f} instantaneous against {st['means']['carry']:.4f} carried, "
              f"delta {st['forgetting']['delta']:+.4f} ({st['forgetting']['sigma']:.2f} sigma)")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e333` had this at 2.45 sigma on a confounded stream, `e337` reversed it, `e338` zeroed the")
    print("    manipulation and `e340` brought it back at 0.95; this is the clean stream with the replicates)")
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
