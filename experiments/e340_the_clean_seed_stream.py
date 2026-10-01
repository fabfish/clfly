"""E340 -- the clean seed stream: `e337`'s question asked again with the other two draws held.

`e337` ran `e333`'s two worlds on what it called a **second seed stream** (`--seed0 4` in place of 0) and the effect
**reversed**: +0.0375 at 2.45 sigma one way, -0.0771 at 3.36 the other. `e338` then asked one trained body both
questions and found the manipulation moves **nothing** (0.0000 on a sem of 0.0022), so the calibration the thread
reached is that the redraw dominates a configuration-against-configuration comparison.

**And `e339` measured what that redraw was**: `--seed0` also draws the **read-out subset** (`--readout-seed` defaults
to it) and the environment's **three populations** (`fly_env.build` is seeded from it), so `e337`'s two runs differed
in three draws at once. `e339` named the fix and this unit is it: **`--readout-seed 0` holds the decoder's draw and a
new `--loop-seed 0` holds the populations, so `--seed0` is the training seed stream alone.**

**The stream-0 side of the pair already exists.** `e333`'s two runs were issued at `--seed0 0` with both other draws
at their defaults, and those defaults are seed 0 -- so `e333`'s pair **is** the clean stream-0 configuration. This
unit runs only the other side: the two worlds at `--seed0 4 --readout-seed 0 --loop-seed 0`.

Four claims, registered before those runs' readings. `delta` is `replay`'s carried-minus-instantaneous mean
forgetting, paired by replicate index within a stream.

- **T1 -- and it is a clean pair.** The stream-4 runs' read-out fingerprint, cue, action and feedback fingerprints,
  and every setting but `seed0` agree with `e333`'s; the new flag is recorded and matches on both sides of the pair.
  **Falsifier**: a differing fingerprint or a differing non-seed setting, which would say the confound is still there.
- **T2 -- and the sign.** The clean stream-4 difference has the **same sign** as `e333`'s on stream 0, where `e337`'s
  confounded one did not. **Falsifier**: the opposite sign, which would say the flip survives the fix.
- **T3 -- and the size is comparable, within a factor of 2.** **Falsifier**: a factor of 4 or more. **Null**: between.
- **T4 -- and holding the draws mattered.** The clean difference **differs** from `e337`'s confounded one by at least
  **0.02**, so the read-out and the populations were not innocent bystanders. **Falsifier**: they agree within
  **0.01**, which would say the confound changed nothing and `e337`'s number is the clean one after all.

**What it cannot do.** *One clean pair*: the read-out and the populations are now held, but the training seeds are
still a single redraw, and two points give a span and not a standard deviation. *The stream-0 side is `e333`'s run and
not a re-run*: it is the same configuration by the defaults' arithmetic and not by the same command line, so a reader
who changes `fly_env.build`'s seeding would break that identity without breaking this unit's claims. *Five replicates*,
the count `e336` and `e337` both found to be at the floor for a configuration contrast. *One arm and one world pair*:
`naive`, `ewc` and the block arms are not run, and only `leak = 0.35` against `1.0` is asked.
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
#: stream 0 is `e333`'s pair, which was issued at `--seed0 0` with both other draws at their defaults; stream 4 is
#: this unit's, with both of them named
STREAMS = {
    "clean, seed0=0": (RUNS / "e333_world_instant.json", RUNS / "e333_world_carry.json"),
    "clean, seed0=4": (RUNS / "e340_clean_instant.json", RUNS / "e340_clean_carry.json"),
}
#: the confounded stream-4 pair `e339` diagnosed, carried beside the two clean ones
CONFOUNDED = {"instant": RUNS / "e337_stream4_instant.json", "carry": RUNS / "e337_stream4_carry.json"}
ORDER = ("clean, seed0=0", "clean, seed0=4")
ARM = "replay"
SIGMA = 2.0
COMPARABLE = 2.0
LOOSE = 4.0
MATTERED = 0.02
INNOCENT = 0.01
CLAIMS = (
    ("T1", "and it is a clean pair",
     "The stream-4 runs' read-out, cue, action and feedback fingerprints and every setting but `seed0` agree with "
     "`e333`'s, and the environment seed flag matches on both sides",
     "falsifier: a differing fingerprint or a differing non-seed setting"),
    ("T2", "and the sign",
     f"The clean stream-4 difference has the same sign as stream 0's, where `e337`'s confounded one did not",
     "falsifier: the opposite sign, which would say the flip survives the fix"),
    ("T3", f"and the size is comparable, within a factor of {COMPARABLE:.0f}",
     f"The clean stream-4 difference is within a factor of {COMPARABLE:.0f} of stream 0's",
     f"falsifier: a factor of {LOOSE:.0f} or more"),
    ("T4", f"and holding the draws mattered, by {MATTERED:.2f}",
     f"The clean difference differs from `e337`'s confounded one by at least {MATTERED:.2f}",
     f"falsifier: they agree within {INNOCENT:.2f}, which would say the confound changed nothing"),
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


def stream_reading(instant, carry) -> dict:
    a, b = load(instant), load(carry)
    if not a or not b:
        return {"ok": False, "missing": [str(p) for p, d in ((instant, a), (carry, b)) if not d]}
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "ok": True,
        "circuit": a.get("circuit"),
        "seed0": [ca.get("seed0"), cb.get("seed0")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "readout_seed": [ca.get("readout_seed"), cb.get("readout_seed")],
        "populations": {k: [ea.get(k), eb.get(k)] for k in ("cue_sha1", "action_sha1", "feedback_sha1")},
        "env_seed": [ca.get("loop_seed"), cb.get("loop_seed")],
        "settings": {k: [ca.get(k), cb.get(k)] for k in
                     ("circuit_size", "repeats", "train", "test", "readout_size", "loop_scale",
                      "loop_noise", "loop_symbols", "loop_world_modes", "loop_world_leak")},
        "forgetting": paired([r["mean_forgetting"] for r in replicates(b)],
                             [r["mean_forgetting"] for r in replicates(a)]),
        "accuracy": paired([r["final_accuracy"] for r in replicates(b)],
                           [r["final_accuracy"] for r in replicates(a)]),
        "means": {"instant": a["methods"][ARM].get("mean_forgetting"),
                  "carry": b["methods"][ARM].get("mean_forgetting")},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def reading(streams=None, confounded=None) -> dict:
    streams = streams or STREAMS
    out = {"streams": {}, "arm": ARM}
    for tag in ORDER:
        if tag in streams:
            instant, carry = streams[tag]
            out["streams"][tag] = stream_reading(instant, carry)
    confounded = confounded or CONFOUNDED
    out["confounded"] = stream_reading(confounded["instant"], confounded["carry"])
    out["runs"] = sum(2 for s in out["streams"].values() if s.get("ok")) + (
        2 if out["confounded"].get("ok") else 0)
    if out["runs"] < 4:
        out["missing"] = [t for t in ORDER if not out["streams"].get(t, {}).get("ok")]
    return out


def judge(r: dict) -> list[dict]:
    s = r.get("streams") or {}
    first, second = s.get("clean, seed0=0", {}), s.get("clean, seed0=4", {})
    if not first.get("ok") or not second.get("ok"):
        return [{"id": c[0], "measured": f"streams present: {sorted(k for k, v in s.items() if v.get('ok'))}",
                 "verdict": "REFUSED -- both clean streams are not on disk"} for c in CLAIMS]

    same = all(first[k] == second[k] for k in ("circuit", "readout"))
    pops = all(first["populations"][k] == second["populations"][k] for k in first["populations"])
    settings = all(first["settings"][k][0] == second["settings"][k][0] for k in first["settings"])
    seeds_differ = first["seed0"][0] != second["seed0"][0]
    j1 = {"id": "T1", "measured": f"circuit {second['circuit']}, read-out {first['readout']} against "
                                  f"{second['readout']}, populations {'equal' if pops else 'differing'}, "
                                  f"seed0 {first['seed0'][0]} against {second['seed0'][0]}, environment seeds "
                                  f"{first['env_seed']} and {second['env_seed']}, the stream-4 settings "
                                  f"{ {k: v[0] for k, v in second['settings'].items()} }",
          "verdict": "MET -- one configuration except the training seed stream" if same and pops and settings
          and seeds_differ else
          f"FALSIFIER FIRED -- circuit {same}, populations {pops}, settings {settings}, seeds differ "
          f"{seeds_differ}"}

    d1, d2 = first["forgetting"], second["forgetting"]
    j2 = {"id": "T2", "measured": f"`{ARM}`'s carried-minus-instantaneous forgetting: {d1['delta']:+.4f} at stream 0 "
                                  f"({d1['sigma']:.2f} sigma) and {d2['delta']:+.4f} at the clean stream 4 "
                                  f"({d2['sigma']:.2f} sigma)",
          "verdict": "MET -- the sign holds once the other two draws are held" if d1["delta"] * d2["delta"] > 0 else
                     f"FALSIFIER FIRED -- {d1['delta']:+.4f} against {d2['delta']:+.4f}"}

    ratio = abs(d2["delta"]) / abs(d1["delta"]) if d1["delta"] else None
    j3 = {"id": "T3", "measured": f"the clean stream 4 is {'n/a' if ratio is None else f'{ratio:.2f}x'} stream 0 "
                                  f"({d2['delta']:+.4f} against {d1['delta']:+.4f})",
          "verdict": ("REFUSED -- stream 0's difference is zero" if ratio is None else
                      f"MET -- the size is comparable at {ratio:.2f}x" if COMPARABLE >= max(ratio, 1 / ratio) else
                      f"FALSIFIER FIRED -- a factor of {max(ratio, 1 / ratio):.2f}" if
                      LOOSE <= max(ratio, 1 / ratio) else
                      f"NULL -- a factor of {max(ratio, 1 / ratio):.2f}, between {COMPARABLE:.0f} and "
                      f"{LOOSE:.0f}")}

    conf = r.get("confounded") or {}
    if not conf.get("ok"):
        j4 = {"id": "T4", "measured": "the confounded pair is absent",
              "verdict": "REFUSED -- `e337`'s pair is not on disk"}
    else:
        gap = abs(d2["delta"] - conf["forgetting"]["delta"])
        j4 = {"id": "T4", "measured": f"the clean stream 4 gives {d2['delta']:+.4f} and `e337`'s confounded one "
                                      f"{conf['forgetting']['delta']:+.4f}, a gap of {gap:.4f}",
              "verdict": f"MET -- holding the draws moved the answer by {gap:.4f}" if gap >= MATTERED else
              f"FALSIFIER FIRED -- they agree within {gap:.4f}" if gap < INNOCENT else
              f"NULL -- {gap:.4f}, between {INNOCENT:.2f} and {MATTERED:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the clean seed stream ==")
    for tag in ORDER + ("confounded, seed0=4",):
        st = (r.get("streams") or {}).get(tag) if tag in ORDER else r.get("confounded")
        if not st or not st.get("ok"):
            print(f"   {tag}: REFUSED -- {st.get('missing') if st else 'absent'}")
            continue
        print(f"   {tag}: seed0 {st['seed0']}, environment seed {st['env_seed']}, read-out {st['readout'][0]}, "
              f"cue {st['populations']['cue_sha1'][0]}")
        print(f"      forgetting {st['means']['instant']:.4f} instantaneous against {st['means']['carry']:.4f} "
              f"carried, delta {st['forgetting']['delta']:+.4f} ({st['forgetting']['sigma']:.2f} sigma)")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e339` found `--seed0` drawing the read-out subset and the environment's populations as well as the")
    print("    training seeds; this holds the first two and moves only the third)")
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
