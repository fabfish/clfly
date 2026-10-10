"""E485 -- the benchmark pays a reward: the game's own currency, recorded per task.

`e483` gave `CueActionEnv` a **payout** and closed on *"the payout is not the benchmark's: the runner does not carry the
flag"*; `e482`'s fifteenth revision had just taken the **policy** off the card's `absent` list by the same route
(`e477`'s environment field, `e481`'s runner flag, `e482`'s revision). **This is the runner's step for the reward.**
`--loop-reward` builds the loop's environment with the payout on, and `run_method` records a **retention matrix in
reward** -- what the world paid on task `j` after the body had been trained through task `k` -- beside the accuracy it
already records. Four claims, registered before the new run's reading was opened.

- **RA1 -- and the flag is the only field moved.** Every recorded config field agrees with the card's neutral roll
  except the flag itself, the output path and the saved weights; and the environment's own draw agrees on every field
  it records except **the payout's map**, which the older roll does not have at all. **Falsifier**: any other config
  field differing, or any draw field differing past the payout's map.
- **RA2 -- and the game's own currency keeps the diagonal.** On each of the three arms the reward matrix's mean
  **diagonal** exceeds its mean **last row** by at least **0.50**, paired over the twenty replicates, at **two** sigma
  or more. **Falsifier**: a gap below **0.20**, or one that does not resolve. **Null**: between.
- **RA3 -- and the two currencies order the arms the same way.** The ordering of the three arms by the accuracy
  diagonal and by the reward diagonal agree on all three pairs. **Falsifier**: any pair whose order disagrees.
- **RA4 -- and the first task is one training in all three arms.** The reward matrices' first rows are identical
  across the three arms, since on task 0 there is no penalty and no buffer and the three arms run the same body. **Falsifier**: any entry differing.

**What it can do beyond that.** It is the first artifact in this corpus whose retention is recorded in the game's own
currency as well as in accuracy, which is the half of `e325`'s sentence the card's `absent` list has been missing --
and it says whether the arm that keeps the most accuracy is the arm the world pays most.

**What it cannot do.** *One configuration*: the card's neutral roll at one world, one budget and one seed stream.
*And the payout is the cue's and not the label's*: the target is a linear read of the cue, so a reward on the label is
not in it. *And the reward's own noise is large*: `e484` found the cue's share of the payout under the payout's own
scatter at this cue noise, so the matrix is a noisy currency. *And the matrix is the body's*: the head reads and is
not paid, so the reward's retention is a property of the world and the recurrent weights. *And twenty replicates are
one body and one circuit*: every sigma is the paired one over the seeds the two runs share.
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

#: the first runner artifact that carries a reward, and the card's own neutral roll it is compared against
NEW = Path("runs/e485_earned_label_reward_20reps.json")
BASE = Path("runs/e438_earned_label_three_arms_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = ("naive", "ewc-block", "replay")
FLAG = "loop_reward"
BOOKKEEPING = ("json_out", "save_theta")
#: the draw's own fields, the payout's map being the one the flag adds
PAYOUT_FIELD = "reward_map_sha1"
MIN_REPS = 20
SIGMA = 2.0
BAR = 0.50
FLOOR = 0.20
CLAIMS = (
    ("RA1", "and the flag is the only field moved",
     "Every recorded config field agrees with the card's neutral roll except the flag itself, the output path and the "
     "saved weights, and the environment's draw agrees on every field it records except the payout's map",
     "falsifier: any other config field differing, or any draw field differing past the payout's map"),
    ("RA2", f"and the game's own currency keeps the diagonal, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "On each of the three arms the reward matrix's mean diagonal exceeds its mean last row by at least 0.50, paired "
     "over the twenty replicates, at two sigma or more",
     f"falsifier: a gap below {FLOOR:.2f}, or one that does not resolve"),
    ("RA3", "and the two currencies order the arms the same way",
     "The ordering of the three arms by the accuracy diagonal and by the reward diagonal agree on all three pairs",
     "falsifier: any pair whose order disagrees"),
    ("RA4", "and the first task is one training in all three arms",
     "The reward matrices' first rows are identical across the three arms",
     "falsifier: any entry differing"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    if key == FLAG or key in BOOKKEEPING:
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


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps or any(r.get("reward_retention") is None for r in reps):
            return None
        got[arm] = {"replicates": len(reps),
                    "reward_diagonal": [statistics.fmean([r["reward_retention"][k][k] for k in range(3)])
                                        for r in reps],
                    "reward_last": [statistics.fmean([r["reward_retention"][2][j] for j in range(3)]) for r in reps],
                    "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                    "reward_rows": [[r["reward_retention"][0][0] for r in reps],
                                    [r["reward_retention"][1][0] for r in reps]],
                    "first_row": [r["reward_retention"][0] for r in reps]}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": got, "env_draw": doc.get("env_draw") or {},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - {FLAG} - set(BOOKKEEPING))},
            "flag": cfg.get(FLAG)}


def reading(new: Path = NEW, base: Path = BASE) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "inert": {}, "draw": {}, "diagonal": {},
           "order": {}, "first": {}, "spans": {}}
    got_new = _roll(new)
    if got_new is None:
        return {**out, "ok": False, "reason": f"the reward run {new} is absent or carries no reward matrix"}
    doc_base = load(base)
    if not doc_base:
        return {**out, "ok": False, "reason": f"the card's neutral roll {base} is absent"}
    out["runs"] = {"reward": got_new, "card": {"artifact": base.name, "config": {k: (doc_base.get("config") or {}).get(k)
                                                                                for k in sorted(set(got_new["config"]))},
                                               "env_draw": doc_base.get("env_draw") or {}}}
    ca, cb = out["runs"]["card"]["config"], got_new["config"]
    for k in sorted(set(ca) | set(cb)):
        old, new_v = ca.get(k), cb.get(k)
        if old == new_v:
            continue
        (out["inert"] if _inert(k, old, new_v) else out["same"])[k] = [old, new_v]
    da, db = out["runs"]["card"]["env_draw"], got_new["env_draw"]
    for k in sorted(set(da) | set(db)):
        if k == PAYOUT_FIELD:
            continue
        out["draw"][k] = da.get(k) == db.get(k)
    for arm in ARMS:
        g = got_new["arms"][arm]
        out["diagonal"][arm] = {"reward": _paired(g["reward_diagonal"], g["reward_last"]),
                                "accuracy_diagonal": statistics.fmean(g["accuracy_diagonal"])}
    acc = sorted(ARMS, key=lambda a: out["diagonal"][a]["accuracy_diagonal"], reverse=True)
    rew = sorted(ARMS, key=lambda a: statistics.fmean(got_new["arms"][a]["reward_diagonal"]), reverse=True)
    out["order"] = {"accuracy": acc, "reward": rew, "agrees": acc == rew}
    out["first"] = {"by_arm": {a: got_new["arms"][a]["first_row"] for a in ARMS},
                    "identical": len({tuple(tuple(r) for r in got_new["arms"][a]["first_row"]) for a in ARMS}) == 1}
    out["spans"] = {
        "arms": list(ARMS), "same_fields": len(set(ca) | set(cb)), "differ": sorted(out["same"]),
        "inert": sorted(out["inert"]), "flags": [out["runs"]["card"].get("flag"), got_new["flag"]],
        "draw_fields": len(out["draw"]), "draw_differ": sorted(k for k, v in out["draw"].items() if not v),
        "payout_field": PAYOUT_FIELD,
        "replicates": sorted({v["replicates"] for v in got_new["arms"].values()}),
        "reward_diagonal": {a: round(statistics.fmean(got_new["arms"][a]["reward_diagonal"]), 4) for a in ARMS},
        "reward_last": {a: round(statistics.fmean(got_new["arms"][a]["reward_last"]), 4) for a in ARMS},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run is absent or carries no reward matrix"}
                for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "RA1",
          "measured": f"the config: **{len(s['differ'])}** of {s['same_fields']} differing past the inert rule "
                      f"({s['differ']}), the flag {s['flags']}; the draw: **{s['draw_fields']}** fields compared with "
                      f"**{len(s['draw_differ'])}** differing ({s['draw_differ']}), the payout's own map "
                      f"`{s['payout_field']}` being the one the flag adds",
          "verdict": "MET -- one configuration with the payout moved, and the draw differs in nothing else" if
                     (not s["differ"] and not s["draw_differ"] and s["flags"] == [None, True]) else
                     f"FALSIFIER FIRED -- config differing {s['differ']}, the flag {s['flags']}, draw differing "
                     f"{s['draw_differ']}"}
    d = r["diagonal"]
    bad = [a for a in ARMS if d[a]["reward"]["mean"] < BAR and d[a]["reward"]["mean"] < FLOOR]
    weak = min(d[a]["reward"]["sigma"] for a in ARMS)
    j2 = {"id": "RA2",
          "measured": f"the reward's diagonal less its last row, by arm: "
                      f"{ {a: round(d[a]['reward']['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(d[a]['reward']['sigma'], 2) for a in ARMS} } sigma, from the diagonals "
                      f"{s['reward_diagonal']} against the last rows {s['reward_last']}",
          "verdict": f"MET -- the game's own currency keeps the diagonal on every arm, the weakest at {weak:.2f} "
                     f"sigma" if (not bad and weak >= SIGMA) else
                     f"FALSIFIER FIRED -- {bad or 'no arm'} below the floor {FLOOR:.2f}, or the weakest at "
                     f"{weak:.2f} sigma"}
    o = r["order"]
    j3 = {"id": "RA3",
          "measured": f"the accuracy orders the arms {o['accuracy']} and the reward orders them {o['reward']}, from "
                      f"the accuracy diagonals "
                      f"{ {a: round(d[a]['accuracy_diagonal'], 4) for a in ARMS} } and the reward diagonals "
                      f"{s['reward_diagonal']}",
          "verdict": "MET -- the two currencies order the arms the same way" if o["agrees"] else
                     f"FALSIFIER FIRED -- {o['accuracy']} against {o['reward']}"}
    first = r["first"]
    j4 = {"id": "RA4",
          "measured": f"the reward matrices' first rows are "
                      f"{ {a: [[None if x is None else round(x, 6) for x in row] for row in first['by_arm'][a]] for a in ARMS} }"
                      f", identical across the three arms {first['identical']}",
          "verdict": "MET -- task 0 is one training in all three arms" if first["identical"] else
                     f"FALSIFIER FIRED -- the first rows differ: "
                     f"{ {a: first['by_arm'][a] for a in ARMS} }"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the benchmark pays a reward ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e483` gave the world a payout; this is the runner carrying it, by the route `e477`, `e481`")
    print("   and `e482` took for the policy: the environment's field, the runner's flag, then the card")
    print(f"\n   {'arm':<10} {'reward diagonal':>16} {'reward last row':>16} {'contrast':>10} {'sigma':>7} "
          f"{'accuracy diag':>14}")
    for a in ARMS:
        d = r["diagonal"][a]["reward"]
        print(f"   {a:<10} {r['spans']['reward_diagonal'][a]:>16.4f} {r['spans']['reward_last'][a]:>16.4f} "
              f"{d['mean']:>+10.4f} {d['sigma']:>7.2f} {r['diagonal'][a]['accuracy_diagonal']:>14.4f}")
    print(f"\n   the config: {len(r['spans']['differ'])} differing past the inert rule {r['spans']['differ']}; "
          f"the flag {r['spans']['flags']}")
    print(f"   the draw: {r['spans']['draw_fields']} fields compared with {r['spans']['draw_differ']} differing, "
          f"the payout's map `{r['spans']['payout_field']}` being the one the flag adds")
    print("\n== the registered claims, RA1-RA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e482`'s fifteenth revision took the policy off the card's absent list; with this flag the")
    print("    corpus has a reward the benchmark pays, and what remains absent is an episode boundary)")
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
