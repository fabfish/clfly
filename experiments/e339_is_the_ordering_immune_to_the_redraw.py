"""E339 -- the seed stream is three draws at once: what `--seed0` moves besides the seeds.

`e337` ran `e333`'s two worlds on a **second seed stream** (`--seed0 4` instead of 0) and the effect **reversed**:
+0.0375 at 2.45 sigma one way, -0.0771 at 3.36 the other. `e338` then asked one trained body both questions and
found the manipulation moves **nothing** (0.0000 on a sem of 0.0022). The conclusion was that the redraw dominates,
and this unit was registered to test the same thing about `e331`'s **arm ordering**: five arms on `--seed0 4` in
place of 0, the same circuit, read-out, tasks, arms and settings.

**Its T1 came back FIRED and the reason is the unit.** The two runs are not one configuration in two seed streams:
`--seed0` also draws the **read-out subset** (`--readout-seed` defaults to it) and the environment's **three
populations** (`fly_env.build` is seeded from it). A run at `--seed0 4` differs from the same command at `--seed0 0`
in **three** draws at once -- which is a property of every seed-stream comparison in this thread, `e337`'s included.

So this unit measures the confound instead of asserting past it, on **two pairs**: `e331`'s five-arm run against
this unit's, and `e333`'s two-world run against `e337`'s. Four claims, registered before the second pair was read.

- **T1 -- one configuration except the seed stream.** Same circuit, read-out fingerprint, task names, replicate
  count, arms, environment draw and settings, the seed schedules the only difference. **Falsifier**: any other field
  differing.
- **T2 -- and `--seed0` moves the read-out draw.** The two runs of a pair record **different** read-out subset
  fingerprints. **Falsifier**: the same fingerprint, which would make this a seed-stream comparison after all.
- **T3 -- and it moves the environment's three populations.** The cue, action and feedback fingerprints differ within
  a pair. **Falsifier**: the same fingerprints.
- **T4 -- and every setting that carries no seed agrees.** Within a pair the settings that are not seeds are equal,
  so the confound is complete and not partial. **Falsifier**: a non-seed setting differing.

**What it cannot do.** *Two pairs, both at `--seed0 0` against 4*, and nothing here varies the read-out draw and the
populations **independently**, which is what separating the three draws would need: `--readout-seed` can be held
fixed and is not, and the environment's population seed has **no flag at all**. *The arms' numbers are read and not
re-measured*: this unit reports what the artifacts' fingerprints say and re-runs nothing, so its evidence is the two
runs' own records. *And it says nothing about the ordering's stability*, which was the registered question: that
question now needs a pair of runs whose read-out draw and populations are **held fixed**, and no such pair exists in
this corpus.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

RUNS = Path("runs")
#: two pairs, each the same command at `--seed0 0` and at `--seed0 4`
PAIRS = (
    ("five arms", RUNS / "e331_arms_scale_0p50.json", RUNS / "e339_arms_stream4.json"),
    ("two worlds", RUNS / "e333_world_instant.json", RUNS / "e337_stream4_instant.json"),
)
#: the settings a pair is allowed to differ in, and the rest of the config and environment must agree on
SETTING_KEYS = ("circuit_size", "repeats", "methods", "train", "test", "readout_size", "classes",
                "loop_scale", "loop_noise", "loop_symbols", "loop_world_modes", "loop_world_leak")
ENV_KEYS = ("tau", "n_symbols", "n_cue", "n_action", "n_feedback", "scale", "gain", "noise")
CLAIMS = (
    ("T1", "one configuration except the seed stream",
     "Same circuit, read-out fingerprint, task names, replicate count, arms, environment draw and settings, the seed "
     "schedules the only difference",
     "falsifier: any other field differing"),
    ("T2", "and `--seed0` moves the read-out draw",
     "The two runs of a pair record different read-out subset fingerprints",
     "falsifier: the same fingerprint, which would make this a seed-stream comparison after all"),
    ("T3", "and it moves the environment's three populations",
     "The cue, action and feedback fingerprints differ within a pair",
     "falsifier: the same fingerprints"),
    ("T4", "and every setting that carries no seed agrees",
     "Within a pair the settings that are not seeds are equal",
     "falsifier: a non-seed setting differing"),
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


def pair_reading(label: str, first, second) -> dict:
    a, b = load(first), load(second)
    if not a or not b:
        return {"label": label, "ok": False,
                "missing": [str(p) for p, d in ((first, a), (second, b)) if not d]}
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    arms = sorted(set(a.get("methods", {})) & set(b.get("methods", {})))
    return {
        "label": label,
        "ok": True,
        "circuit": a.get("circuit"),
        "tasks": [x.get("name") for x in a.get("tasks", [])],
        "arms": arms,
        "counts": {x: [len(replicates(a, x)), len(replicates(b, x))] for x in arms},
        "seed0": [ca.get("seed0"), cb.get("seed0")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "populations": {k: [ea.get(k), eb.get(k)] for k in ("cue_sha1", "action_sha1", "feedback_sha1")},
        "settings": {k: [ca.get(k), cb.get(k)] for k in SETTING_KEYS if k in ca or k in cb},
        "environment_settings": {k: [ea.get(k), eb.get(k)] for k in ENV_KEYS if k in ea or k in eb},
        "levels": {x: [a["methods"][x].get("final_accuracy"), b["methods"][x].get("final_accuracy")] for x in arms},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def reading(pairs=PAIRS) -> dict:
    out = {"pairs": [pair_reading(*p) for p in pairs]}
    out["runs"] = sum(2 for p in out["pairs"] if p.get("ok"))
    out["missing"] = [p["label"] for p in out["pairs"] if not p.get("ok")]
    return out


def judge(r: dict) -> list[dict]:
    pairs = [p for p in (r.get("pairs") or []) if p.get("ok")]
    if not pairs:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- no pair is on disk"} for c in CLAIMS]

    #: T1 is stated on the pair whose settings differ in the seed alone, which is the pair the unit was registered
    #: for: those two runs were issued with identical flags apart from `--seed0`
    target = next((p for p in pairs if p["label"] == "two worlds"), pairs[0])
    settings_agree = all(v[0] == v[1] for v in target["settings"].values())
    j1 = {"id": "T1", "measured": f"the `{target['label']}` pair at seeds {target['seed0']}: settings "
                                  f"{ {k: v for k, v in target['settings'].items()} }, read-out "
                                  f"{target['readout']}",
          "verdict": "MET -- one configuration except the seed stream" if
          target["seed0"][0] != target["seed0"][1] and settings_agree and target["readout"][0] == target["readout"][1]
          else f"FALSIFIER FIRED -- the seeds differ and so does the read-out draw {target['readout']}"}

    moved = [p["label"] for p in pairs if p["readout"][0] != p["readout"][1]]
    detail = "; ".join(f"{p['label']} {p['readout'][0]} against {p['readout'][1]}" for p in pairs)
    j2 = {"id": "T2", "measured": f"the read-out fingerprint of each pair: {detail}",
          "verdict": f"MET -- `--seed0` moves the read-out draw in {len(moved)} of {len(pairs)} pairs" if
          len(moved) == len(pairs) else
          f"FALSIFIER FIRED -- the draw agrees in "
          f"{sorted(set(p['label'] for p in pairs) - set(moved))}"}

    pop = [p["label"] for p in pairs if any(v[0] != v[1] for v in p["populations"].values())]
    detail = "; ".join(f"{p['label']} cue {p['populations']['cue_sha1'][0]} against "
                       f"{p['populations']['cue_sha1'][1]}" for p in pairs)
    j3 = {"id": "T3", "measured": f"the cue population's fingerprint: {detail}",
          "verdict": f"MET -- `--seed0` moves the cue population in {len(pop)} of {len(pairs)} pairs" if
          len(pop) == len(pairs) else
          f"FALSIFIER FIRED -- the populations agree in "
          f"{sorted(set(p['label'] for p in pairs) - set(pop))}"}

    bad = {p["label"]: {k: v for k, v in p["settings"].items() if v[0] != v[1]} for p in pairs}
    bad = {k: v for k, v in bad.items() if v}
    j4 = {"id": "T4", "measured": f"the settings that differ within a pair: {bad or 'none'}",
          "verdict": "MET -- every non-seed setting agrees, so the confound is complete" if not bad else
          f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the seed stream is three draws at once ==")
    for p in r.get("pairs", []):
        if not p.get("ok"):
            print(f"   {p['label']}: REFUSED -- missing {p['missing']}")
            continue
        print(f"   {p['label']}: {p['circuit']}, arms {p['arms']}, seeds {p['seed0']}")
        print(f"      read-out {p['readout'][0]} against {p['readout'][1]}")
        print(f"      cue {p['populations']['cue_sha1'][0]} against {p['populations']['cue_sha1'][1]}, "
              f"action {p['populations']['action_sha1'][0]} against {p['populations']['action_sha1'][1]}, "
              f"feedback {p['populations']['feedback_sha1'][0]} against "
              f"{p['populations']['feedback_sha1'][1]}")
        print(f"      settings {p['settings']}")
        print(f"      levels { {k: [round(x, 4) for x in v] for k, v in p['levels'].items()} }")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e337` compared two `--seed0` settings and called them two seed streams; `--seed0` draws the")
    print("    read-out subset and the environment's three populations as well, so it was three draws at once)")
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
