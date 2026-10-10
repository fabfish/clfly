"""E487 -- the reward in a second world: whether `e485`'s currency disagreement is a world's.

`e485` gave the runner `--loop-reward` and found the game's own currency disagreeing with the accuracy -- the reward's
diagonal **below** its last row on every arm while the accuracy's is above, and the two currencies ordering the three
arms **exactly in reverse** -- and it closed on *"one configuration: the card's neutral roll at one world, one budget
and one seed stream"*. **This unit redraws the world.** The same command with `--loop-seed 1` on, both with the payout
and without it, read beside `e485`'s world-0 run.

Three artifacts, one configuration apart in one field each:

  * `e487` -- world **1**, payout **on** (new);
  * `e443` -- world **1**, payout **off** (the corpus's own roll at that world);
  * `e485` -- world **0**, payout **on**.

Four claims, registered before the new run's reading was opened.

- **RA1 -- and the three runs are one configuration with the world and the payout moved.** Every recorded config field
  agrees except `loop_seed`, `loop_reward`, the output path and the saved weights; the two world-1 runs agree on every
  draw field except the payout's map; and each run carries twenty replicates. **Falsifier**: any other config field
  differing, or a draw field differing between the two world-1 runs past the payout's map.
- **RA2 -- and the reward keeps its shape in the second world.** In world 1 the reward's mean diagonal is **below** its
  mean last row on every arm, paired over the replicates, at **two** sigma or more. **Falsifier**: an arm at or above
  zero, or one that does not resolve.
- **RA3 -- and the payout does not touch the accuracy.** The world-1 runs with the payout on and off agree on every
  replicate's accuracy: each arm's `learned` vector and its `final_per_task` vector, record for record. **Falsifier**:
  any entry differing. *The flag draws the payout last and the reward enters no loss, so the two runs' bodies should be
  the same body -- and this is the check that they are.*
- **RA4 -- and the two currencies disagree in the second world too.** In world 1 the ordering of the three arms by the
  accuracy diagonal and by the reward diagonal disagree on at least one pair. **Falsifier**: the two agreeing.

**What it can do beyond that.** It says whether `e485`'s disagreement is a property of the game or of the world it was
read in -- the same question `e476` asked of the method ordering and `e474` of the held-out level, on the newest axis
this corpus has.

**What it cannot do.** *Two worlds are not a population*: a second world is one more sample of the environment.
*And one budget and one seed stream*: both worlds are the card's own setting, so a budget or a stream is not in it.
*And the reward is the corpus's noisiest currency*: `e484` found its cue-share under its own scatter, so these sigmas
are large numbers about small differences. *And the head is never paid*: what the reward says is the body's.
*And nothing here optimizes the payout*: it is recorded and not played for, which is a different unit.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e172_parser_registry import parser_flags

#: the new run and the two it is read against
W1R = Path("runs/e487_earned_label_worldseed1_reward_20reps.json")
W1 = Path("runs/e443_earned_label_worldseed1_20reps.json")
W0R = Path("runs/e485_earned_label_reward_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = ("naive", "ewc-block", "replay")
#: the two fields the three runs move, and the run's own bookkeeping
MOVED = ("loop_seed", "loop_reward")
BOOKKEEPING = ("json_out", "save_theta")
PAYOUT_FIELD = "reward_map_sha1"
MIN_REPS = 20
SIGMA = 2.0
CLAIMS = (
    ("RA1", f"and the three runs are one configuration with the world and the payout moved, at {MIN_REPS} replicates",
     "Every recorded config field agrees except loop_seed, loop_reward, the output path and the saved weights; the two "
     "world-1 runs agree on every draw field except the payout's map; and each run carries twenty replicates",
     "falsifier: any other config field differing, or a draw field differing between the two world-1 runs past the "
     "payout's map"),
    ("RA2", f"and the reward keeps its shape in the second world, at {SIGMA:.0f} sigma",
     "In world 1 the reward's mean diagonal is below its mean last row on every arm, paired over the replicates, at two "
     "sigma or more",
     "falsifier: an arm at or above zero, or one that does not resolve"),
    ("RA3", "and the payout does not touch the accuracy",
     "The world-1 runs with the payout on and off agree on every replicate's accuracy, each arm's learned vector and "
     "its final_per_task vector, record for record",
     "falsifier: any entry differing"),
    ("RA4", "and the two currencies disagree in the second world too",
     "In world 1 the ordering of the three arms by the accuracy diagonal and by the reward diagonal disagree on at "
     "least one pair",
     "falsifier: the two agreeing"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return old is None and key in DEFAULTS and new == DEFAULTS[key]


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path, needs_reward: bool) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        diag = [statistics.fmean(r["learned"]) for r in reps]
        last = [statistics.fmean(r["final_per_task"]) for r in reps]
        entry = {"replicates": len(reps), "diagonal": diag, "last": last,
                 "learned": [list(r["learned"]) for r in reps],
                 "final_per_task": [list(r["final_per_task"]) for r in reps]}
        if needs_reward:
            if any(r.get("reward_retention") is None for r in reps):
                return None
            rw = [r["reward_retention"] for r in reps]
            entry["reward_diagonal"] = [statistics.fmean([x[k][k] for k in range(3)]) for x in rw]
            entry["reward_last"] = [statistics.fmean([x[2][j] for j in range(3)]) for x in rw]
            entry["reward_first"] = [[x[0][0] for x in rw], [None] * len(rw)]
        got[arm] = entry
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": got, "env_draw": doc.get("env_draw") or {},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(MOVED) - set(BOOKKEEPING))},
            "moved": {k: cfg.get(k) for k in MOVED}}


def reading(w1r: Path = W1R, w1: Path = W1, w0r: Path = W0R) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "inert": {}, "draw": {}, "reward": {},
           "accuracy_same": {}, "order": {}, "spans": {}}
    got = {"w1_reward": _roll(w1r, True), "w1": _roll(w1, False), "w0_reward": _roll(w0r, True)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"{label} is absent or carries no reward matrix"}
    out["runs"] = got
    base = got["w1"]["config"]
    for label in ("w1_reward", "w0_reward"):
        roll = got[label]
        for k in sorted(set(roll["config"]) | set(base)):
            old, new = base.get(k), roll["config"].get(k)
            if old == new:
                continue
            (out["inert"] if _inert(k, old, new) else out["same"])[f"{label}.{k}"] = [old, new]
    da, db = got["w1"]["env_draw"], got["w1_reward"]["env_draw"]
    for k in sorted(set(da) | set(db)):
        if k in MOVED or k == PAYOUT_FIELD:
            continue
        out["draw"][k] = da.get(k) == db.get(k)
    arms = got["w1_reward"]["arms"]
    out["reward"] = {a: _paired(arms[a]["reward_diagonal"], arms[a]["reward_last"]) for a in ARMS}
    acc_same = {}
    for a in ARMS:
        on, off = got["w1_reward"]["arms"][a], got["w1"]["arms"][a]
        acc_same[a] = {"learned": on["learned"] == off["learned"],
                       "final_per_task": on["final_per_task"] == off["final_per_task"],
                       "replicates": on["replicates"] == off["replicates"]}
    out["accuracy_same"] = acc_same
    acc_order = sorted(ARMS, key=lambda a: statistics.fmean(got["w1_reward"]["arms"][a]["diagonal"]), reverse=True)
    rew_order = sorted(ARMS, key=lambda a: statistics.fmean(arms[a]["reward_diagonal"]), reverse=True)
    out["order"] = {"accuracy": acc_order, "reward": rew_order, "agrees": acc_order == rew_order}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "same_fields": len(set(base) | set(got["w0_reward"]["config"])),
        "differ": sorted(out["same"]), "inert": sorted(out["inert"]),
        "moved": {label: got[label]["moved"] for label in got},
        "draw_fields": len(out["draw"]), "draw_differ": sorted(k for k, v in out["draw"].items() if not v),
        "payout_field": PAYOUT_FIELD,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "reward_diagonal": {a: round(statistics.fmean(arms[a]["reward_diagonal"]), 4) for a in ARMS},
        "reward_last": {a: round(statistics.fmean(arms[a]["reward_last"]), 4) for a in ARMS},
        "accuracy_diagonal": {a: round(statistics.fmean(got["w1_reward"]["arms"][a]["diagonal"]), 4) for a in ARMS},
        "accuracy_last": {a: round(statistics.fmean(got["w1_reward"]["arms"][a]["last"]), 4) for a in ARMS},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run is absent or carries no reward matrix"}
                for c in CLAIMS]
    s = r["spans"]
    moved_ok = (s["moved"]["w1_reward"].get("loop_seed") == 1
                and s["moved"]["w1_reward"].get("loop_reward") is True
                and s["moved"]["w1"].get("loop_seed") == 1 and s["moved"]["w1"].get("loop_reward") in (None, False)
                and s["moved"]["w0_reward"].get("loop_seed") is None
                and s["moved"]["w0_reward"].get("loop_reward") is True)
    j1 = {"id": "RA1",
          "measured": f"the config: **{len(s['differ'])}** of {s['same_fields']} differing past the inert rule "
                      f"({s['differ']}), the fields moved {s['moved']}; the draw: **{s['draw_fields']}** fields between "
                      f"the two world-1 runs with **{len(s['draw_differ'])}** differing ({s['draw_differ']}), the "
                      f"payout's map `{s['payout_field']}` being the one the payout adds; replicates "
                      f"{s['replicates']}",
          "verdict": "MET -- one configuration with the world and the payout moved, and the two world-1 runs differ in "
                     "nothing else" if (not s["differ"] and not s["draw_differ"] and s["replicates"] == [MIN_REPS]
                                        and moved_ok) else
                     f"FALSIFIER FIRED -- differing {s['differ']}, draw differing {s['draw_differ']}, replicates "
                     f"{s['replicates']}, moved {s['moved']}"}
    rw = r["reward"]
    bad = [a for a in ARMS if rw[a]["mean"] >= 0.0 or rw[a]["sigma"] >= -SIGMA]
    j2 = {"id": "RA2",
          "measured": f"in world 1 the reward's diagonal less its last row is "
                      f"{ {a: round(rw[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rw[a]['sigma'], 2) for a in ARMS} } sigma, from the diagonals "
                      f"{s['reward_diagonal']} against the last rows {s['reward_last']}",
          "verdict": "MET -- the reward's diagonal is below its last row on every arm in the second world, the weakest "
                     "at " + f"{min(rw[a]['sigma'] for a in ARMS):.2f} sigma" if not bad else
                     f"FALSIFIER FIRED -- {bad}"}
    same = r["accuracy_same"]
    differ = sorted(f"{a}.{k}" for a, v in same.items() for k, ok in v.items() if not ok)
    j3 = {"id": "RA3",
          "measured": f"the two world-1 runs against each other, arm by arm: learned vectors "
                      f"{ {a: same[a]['learned'] for a in ARMS} }, final_per_task vectors "
                      f"{ {a: same[a]['final_per_task'] for a in ARMS} } and replicate counts "
                      f"{ {a: same[a]['replicates'] for a in ARMS} }, {len(differ)} differing",
          "verdict": "MET -- the payout does not touch the accuracy: the two world-1 runs are the same accuracy, "
                     "record for record" if not differ else f"FALSIFIER FIRED -- {differ}"}
    o = r["order"]
    j4 = {"id": "RA4",
          "measured": f"in world 1 the accuracy orders the arms {o['accuracy']} (from "
                      f"{s['accuracy_diagonal']}) and the reward orders them {o['reward']} (from "
                      f"{s['reward_diagonal']})",
          "verdict": "MET -- the two currencies disagree in the second world too" if not o["agrees"] else
                     f"FALSIFIER FIRED -- both order the arms {o['accuracy']}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the reward in a second world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e485` found the game's own currency disagreeing with the accuracy at one world; this redraws")
    print("   the world with `--loop-seed 1` and asks both runs again")
    print(f"\n   {'arm':<10} {'reward diag':>12} {'reward last':>12} {'contrast':>10} {'sigma':>7} "
          f"{'accuracy diag':>14} {'accuracy last':>14}")
    for a in ARMS:
        c = r["reward"][a]
        print(f"   {a:<10} {r['spans']['reward_diagonal'][a]:>12.4f} {r['spans']['reward_last'][a]:>12.4f} "
              f"{c['mean']:>+10.4f} {c['sigma']:>7.2f} {r['spans']['accuracy_diagonal'][a]:>14.4f} "
              f"{r['spans']['accuracy_last'][a]:>14.4f}")
    print(f"\n   the config: {len(r['spans']['differ'])} differing past the inert rule {r['spans']['differ']}; "
          f"the fields moved {r['spans']['moved']}")
    print(f"   the draw, between the two world-1 runs: {r['spans']['draw_fields']} compared, "
          f"{r['spans']['draw_differ']} differing")
    print("\n== the registered claims, RA1-RA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e485` closed on *one configuration ... one world*; this is the world it did not draw)")
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
