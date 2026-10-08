"""E469 -- the held-out cue set: the benchmark's fourth task, measured on a body that never trained on it.

The card's `absent` list has named *a held-out task* since its first revision and no unit of this corpus has ever run
one: the suite is three cue sets in one world, the evaluation is **per-task decoders**, and a task the sequence never
trained on has no decoder. **So the honest reading is a probe.** This unit drives two rolls of the card's own
configuration with a fourth cue set drawn in the same world (`--loop-holdout`): the sequence still trains on three
tasks, every field the ladder's rolls carry is unchanged, and at the end the body is **frozen** and a ridge read-out is
fitted on the held-out cue set's own train split and scored on its test split -- once for the trained body and once for
a freshly drawn initial one, so the difference is the training's and not the probe's.

**What the flag moves is the world's own draw**: one more block of cue templates, so a holdout run is a different world
from the run beside it and is compared **within itself** rather than against `e438`. Four claims, registered before
either roll's reading was opened.

- **VA1 -- and the two rolls are one configuration with the arm list moved.** Three arms each at **20** replicates,
  every recorded config field agreeing except `methods`, the output path and the saved weights, the three trained task
  names equal, and the held-out task's name **among neither of them**. **Falsifier**: any other field differing, an arm
  missing or short, or a held-out task that the sequence trained on.
- **VA2 -- and the probe is recorded for every arm and every replicate.** Each of the two rolls' three arms carries a
  holdout block on all twenty replicates, with the same task name and the same train and eval counts on both rolls.
  **Falsifier**: a block missing, a short list, or counts that differ between the rolls.
- **VA3 -- and the trained body reads the unseen cue set better than the initial one.** The paired `after` minus
  `before` for the **baseline** arm is positive at **two** sigma or more. **Falsifier**: under two sigma, or negative.
  *The baseline is the arm with no penalty and no buffer, so this is the trained body's own reading.*
- **VA4 -- and the anchoring does not move it.** Each anchor's paired `after` minus the baseline's `after` is under
  **two** sigma in absolute value. **Falsifier**: an anchor whose contrast with the baseline resolves. *This is the
  null the `basis` clauses of the card describe on the diagonal, asked on a task neither arm ever saw.*

**What it can do beyond that.** It adds the one thing the corpus's benchmark has never had: a task outside the
sequence, read on a frozen body with the control that makes the number interpretable. Read with `e438`'s ladder it
separates *what the sequence trains* from *what the body represents*, which is the question a benchmark's held-out
split exists to ask.

**What it cannot do.** *A probe and not a task*: the read-out is fitted on the held-out cue set's own labels, so this
measures how **linearly readable** the task is from the body and not how well the sequence's method would learn it if
it were trained. *And the probe is one ridge*: a different regulariser or a non-linear head would move the level, and
nothing here says which is the benchmark's. *And the held-out cue set is one draw*: a fourth block of cue templates
inside the world the sequence trained in, so *held out* means *not in the sequence* and not *from another world*.
*And two rolls*: the biological anchor and the matched-random one at twenty replicates, on a world that is the flag's
own draw.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the two rolls, by anchor, and the fields a holdout run's two rolls are allowed to differ in
RUNS = {
    "bio": Path("runs/e469_earned_label_neurons_holdout_20reps.json"),
    "rand": Path("runs/e469_earned_label_rand_neurons_holdout_20reps.json"),
}
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods")
N_ARMS = 3
MIN_REPS = 20
N_TASKS = 3
SIGMA = 2.0
CLAIMS = (
    ("VA1", f"and the two rolls are one configuration with the arm list moved, at {MIN_REPS} replicates",
     "Three arms each at twenty replicates, every recorded config field agreeing except methods, the output path and "
     "the saved weights, the three trained task names equal, and the held-out task's name among neither of them",
     "falsifier: any other field differing, an arm missing or short, or a held-out task that the sequence trained on"),
    ("VA2", "and the probe is recorded for every arm and every replicate",
     "Each of the two rolls' three arms carries a holdout block on all twenty replicates, with the same task name and "
     "the same train and eval counts on both rolls",
     "falsifier: a block missing, a short list, or counts that differ between the rolls"),
    ("VA3", f"and the trained body reads the unseen cue set better than the initial one, at {SIGMA:.0f} sigma",
     "The paired after minus before for the baseline arm is positive at two sigma or more",
     "falsifier: under two sigma, or negative"),
    ("VA4", f"and the anchoring does not move it, under {SIGMA:.0f} sigma",
     "Each anchor's paired after minus the baseline's after is under two sigma in absolute value",
     "falsifier: an anchor whose contrast with the baseline resolves"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        blocks = [r.get("holdout") for r in reps]
        if any(b is None for b in blocks):
            return None
        arms[arm] = {"replicates": len(reps), "blocks": blocks,
                     "before": [b["before"] for b in blocks], "after": [b["after"] for b in blocks]}
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "tasks": [t.get("name") if isinstance(t, dict) else None for t in (doc.get("tasks") or [])],
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: (doc.get("config") or {}).get(k)
                       for k in sorted(set(doc.get("config") or {}) - set(IGNORED))}}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "probe": {}, "contrasts": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent, carries no {ANCHOR_OF[label]} arm, or carries no "
                              f"holdout block on some replicate"}
        out["runs"][label] = got
    bio, rand = out["runs"]["bio"], out["runs"]["rand"]
    same = {}
    fields = sorted(set(bio["config"]) | set(rand["config"]))
    for k in fields:
        same[f"config.{k}"] = bio["config"].get(k) == rand["config"].get(k)
    same["circuit"] = bio["shared"].get("circuit") == rand["shared"].get("circuit")
    same["tasks"] = bio["shared"].get("tasks") == rand["shared"].get("tasks")
    out["same"] = same
    for label, roll in out["runs"].items():
        for arm, got in roll["arms"].items():
            blocks = got["blocks"]
            out["probe"][f"{label}/{arm}"] = {
                "task": sorted({b.get("task") for b in blocks}),
                "n_train": sorted({b.get("n_train") for b in blocks}),
                "n_eval": sorted({b.get("n_eval") for b in blocks}),
                "ridge": sorted({b.get("ridge") for b in blocks}),
                "before": statistics.fmean(got["before"]), "after": statistics.fmean(got["after"])}
    for label, roll in out["runs"].items():
        base = roll["arms"][BASELINE]
        out["contrasts"][f"{label}/baseline"] = _paired(base["after"], base["before"])
        for arm in (roll["anchor"], BUFFER):
            got = roll["arms"][arm]
            out["contrasts"][f"{label}/{arm}_over_baseline"] = _paired(got["after"], base["after"])
            out["contrasts"][f"{label}/{arm}_before"] = _paired(got["before"], base["before"])
    thin = {f"{label}/{arm}": v["replicates"] for label, roll in out["runs"].items()
            for arm, v in roll["arms"].items() if v["replicates"] < MIN_REPS}
    held = sorted({t for roll in out["runs"].values() for t in out["probe"][f"{'bio' if roll is bio else 'rand'}/"
                                                                           f"{roll['anchor']}"]["task"]})
    out["spans"] = {
        "rolls": len(out["runs"]), "same_fields": len(same), "thin": thin,
        "trained": {label: roll["tasks"] for label, roll in out["runs"].items()},
        "held_out": held,
        "n_train": sorted({v for p in out["probe"].values() for v in p["n_train"]}),
        "n_eval": sorted({v for p in out["probe"].values() for v in p["n_eval"]}),
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "before": {label: out["probe"][f"{label}/{roll['anchor']}"]["before"] for label, roll in out["runs"].items()},
        "after": {label: out["probe"][f"{label}/{roll['anchor']}"]["after"] for label, roll in out["runs"].items()},
        "baseline": {label: (out["probe"][f"{label}/{BASELINE}"]["before"], out["probe"][f"{label}/{BASELINE}"]["after"])
                     for label in out["runs"]},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll or a holdout block is not there"}
                for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    trained = sorted({t for names in s["trained"].values() for t in names})
    held = s["held_out"]
    trained_ok = all(len(names) == N_TASKS for names in s["trained"].values()) and not (set(held) & set(trained))
    j1 = {"id": "VA1",
          "measured": f"the two rolls carry {s['rolls']} anchors at {s['replicates']} replicates over "
                      f"{s['same_fields']} compared fields, the trained names "
                      f"{sorted(set(trained))[:4]}, and the held-out name {held}",
          "verdict": "MET -- one configuration with the arm list moved, and the held-out cue set is not one the "
                     "sequence trained on" if (not differ and trained_ok and not s["thin"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, trained {sorted(set(trained))}, held out {held}, "
                     f"thin {s['thin']}"}
    names = sorted({t for p in r["probe"].values() for t in p["task"]})
    counts = (s["n_train"], s["n_eval"])
    blocks_ok = all(v["n_train"] and v["n_eval"] and len(v["task"]) == 1 for v in r["probe"].values()) and \
        len(s["n_train"]) == 1 and len(s["n_eval"]) == 1
    j2 = {"id": "VA2",
          "measured": f"{len(r['probe'])} arm-rolls carry a holdout block, on {names} with {s['n_train']} train and "
                      f"{s['n_eval']} eval examples each, over {s['replicates']} replicates",
          "verdict": "MET -- every arm on both rolls carries a probe with the same task and the same counts" if
                     blocks_ok else f"FALSIFIER FIRED -- names {names}, counts {counts}"}
    c = r["contrasts"]
    base = {label: c[f"{label}/baseline"] for label in r["runs"]}
    worst = min((v["sigma"] for v in base.values()), default=0.0)
    j3 = {"id": "VA3",
          "measured": f"the baseline arm's probe reads { {l: round(r['probe'][f'{l}/{BASELINE}']['before'], 4) for l in r['runs']} } "
                      f"on the initial body and "
                      f"{ {l: round(r['probe'][f'{l}/{BASELINE}']['after'], 4) for l in r['runs']} } after the sequence, "
                      f"a paired contrast of "
                      f"{ {l: round(base[l]['mean'], 4) for l in r['runs']} } at "
                      f"{ {l: round(base[l]['sigma'], 2) for l in r['runs']} } sigma",
          "verdict": f"MET -- training raises the unseen cue set's decodability on both rolls, the weaker at "
                     f"{worst:.2f} sigma" if worst >= SIGMA else
                     f"FALSIFIER FIRED -- the weaker contrast is {worst:.2f} sigma"}
    anc = {f"{label}/{arm}": c[f"{label}/{arm}_over_baseline"]
           for label, roll in r["runs"].items() for arm in (roll["anchor"],)}
    resolved = sorted(k for k, v in anc.items() if abs(v["sigma"]) >= SIGMA)
    j4 = {"id": "VA4",
          "measured": f"each anchor's held-out reading against the baseline's is "
                      f"{ {k: (round(v['mean'], 4), round(v['sigma'], 2)) for k, v in anc.items()} }",
          "verdict": "MET -- neither anchor moves the held-out reading against the baseline" if not resolved else
                     f"FALSIFIER FIRED -- {resolved}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the held-out cue set ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll or a holdout block is not there')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, three trained cue sets")
    print("   and a fourth drawn in the same world, read by a ridge probe fitted on the FROZEN body at the end and on")
    print("   a freshly drawn initial one -- so the difference is the training's and not the probe's")
    print(f"\n   the trained cue sets: {sorted({t for names in r['spans']['trained'].values() for t in names})}")
    print(f"   the held-out one:    {r['spans']['held_out']}")
    print(f"\n   {'roll/arm':<26} {'before':>8} {'after':>8} {'delta':>8}")
    for label, roll in r["runs"].items():
        for arm in (BASELINE, roll["anchor"], BUFFER):
            p = r["probe"][f"{label}/{arm}"]
            print(f"   {label + '/' + arm:<26} {p['before']:>8.4f} {p['after']:>8.4f} "
                  f"{p['after'] - p['before']:>+8.4f}")
    print("\n== the registered claims, VA1-VA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the card's absent list has named a held-out task since its first revision; this is the first one run)")
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
