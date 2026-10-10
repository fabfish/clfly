"""E488 -- the reward trains the agent: whether the game's own currency moves the map, or only the task does.

`e481` gave the runner `--loop-policy` and closed on *"the policy is trained by the task loss, so the game still has
no reward"*; `e483` gave the environment the payout, `e485` gave the benchmark one, and `e486` carried it into the
card -- and `e487`'s third claim then measured what the payout does to the **training**: nothing. On two runs one
flag apart, `learned` and `final_per_task` agreed record for record on all three arms, so the currency the card
calls the reward was a **meter** and never a signal.

**This unit makes it a signal.** The runner gains `--loop-earn`: the map the agent acts through is taken out of the
body's optimizer, given one of its own, and trained by **ascent on the world's payout** -- the map's parameters and
nothing else -- so the task loss never touches it, and the game's own currency is what moves the agent.

Two runs, one configuration apart in one field:

  * `e488 ... earned` -- the map trained by the **payout** (new);
  * `e488 ... policy_reward` -- the map trained by the **task loss**, with the payout on and recorded (new).

Four claims, registered before either run was read.

- **XB1 -- and the two runs are one configuration with only what trains the map moved.** Every recorded config field
  agrees except `loop_earn`, the output path and the saved weights; **every** draw field agrees, the two runs drawing
  one world and one payout; and each run carries twenty replicates. **Falsifier**: any other config field differing,
  any draw field differing, or a replicate count other than twenty.
- **XB2 -- and the payout moves the map on every replicate.** On the paid run, every one of the sixty replicates
  records a policy distance from the identity it was initialized at, and the distance is above zero. **Falsifier**:
  any replicate with no recorded movement or a movement of zero. *The map is handed its freedom at the identity, so a
  zero here is a replicate the payout never reached.*
- **XB3 -- and being paid earns more than being trained on the task.** On **at least two of the three arms** the paid
  run's mean reward diagonal is **above** the task-loss run's, paired over the twenty replicate seeds, at **two**
  sigma or more, and the mean gap is at least **0.25**. **Falsifier**: fewer than two of the three arms at or above
  the bar **0.25** and two sigma. *The bar is the smallest difference this currency has been shown to
  carry: `e485`'s cells run about **-6.9** and its own diagonal-to-last-row gaps are **0.19** to **0.35**, while
  `e483`'s policy trained outside the benchmark gained **+1.46**.*
- **XB4 -- and being paid does not buy the task.** On no arm is the paid run's accuracy diagonal above the task-loss
  run's at **two** sigma. **Falsifier**: an arm resolving upward. *The two currencies are not one -- `e485` and `e487`
  both found the arms ordered in reverse by them -- so a paid map that also raises the accuracy would be a third
  thing, and the claim says which of the two the unit expects to move.*

**What it can do beyond that.** It closes the gap the project has named since `e325`: what is missing is *"the thing
that makes it a game rather than a loop: a reward and a policy"* -- the reward existed and was recorded, and this is
the first artifact in the corpus where the reward is what an agent is **trained by**. Read with `e487` it is the
other side of that unit's third claim: there the payout was inert for the training, and here the training is the
payout's.

**What it cannot do.** *One configuration*: the card's neutral roll at one world, one budget and one seed stream, so
what moves is measured against one ablation of the map's training and not against a sweep of it. *And one learning
rate*: the map's ascent runs at the run's own `--lr`, so the strength of the earning is not swept. *And the payout is
the corpus's noisiest currency*: `e484` found its cue-share under its own scatter, so these gaps are differences of a
fraction of a unit in cells running about **-6.9**, and `e487` found the currency's own level moving by half between
two worlds. *And the head is never paid*: the map drives the world and the world pays, while the labels train the body
and the decoders, so an agent that earns more is not thereby an agent that classifies better. *And the map is linear
over one population*, uncovered by any penalty, with the recurrent weights on the other side of the loop.
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

#: the paid map and the map the task trains, both new in this unit
PAID = Path("runs/e488_earned_label_earned_20reps.json")
LOSS = Path("runs/e488_earned_label_policy_reward_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = ("naive", "ewc-block", "replay")
#: the one field the two runs move, and the run's own bookkeeping
MOVED = ("loop_earn",)
BOOKKEEPING = ("json_out", "save_theta")
MIN_REPS = 20
SIGMA = 2.0
#: the smallest mean gap between the two runs' reward diagonals this unit will call an earning
BAR = 0.25
#: how many of the three arms have to resolve upward for the earning to be the map's
ARMS_NEEDED = 2
CLAIMS = (
    ("XB1", f"and the two runs are one configuration with only what trains the map moved, at {MIN_REPS} replicates",
     "Every recorded config field agrees except loop_earn, the output path and the saved weights; every draw field "
     "agrees; and each run carries twenty replicates",
     "falsifier: any other config field differing, any draw field differing, or a replicate count other than twenty"),
    ("XB2", "and the payout moves the map on every replicate",
     "On the paid run every one of the sixty replicates records a policy distance from the identity above zero",
     "falsifier: any replicate with no recorded movement or a movement of zero"),
    ("XB3", f"and being paid earns more than being trained on the task, on {ARMS_NEEDED} arms at {SIGMA:.0f} sigma and "
            f"a bar of {BAR:.2f}",
     "On at least two of the three arms the paid run's mean reward diagonal is above the task-loss run's, paired over "
     "the twenty replicate seeds, at two sigma or more, and the mean gap is at least 0.25",
     "falsifier: fewer than two of the three arms at or above the bar 0.25 and two sigma"),
    ("XB4", f"and being paid does not buy the task, at {SIGMA:.0f} sigma",
     "On no arm is the paid run's accuracy diagonal above the task-loss run's at two sigma",
     "falsifier: an arm resolving upward"),
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


def _roll(path: Path) -> dict | None:
    """One run's per-arm reading: both currencies' diagonals and last rows, the map's movements, the config and the draw."""
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        if any(r.get("reward_retention") is None for r in reps):
            return None
        if any(r.get("policy_move") is None for r in reps):
            return None
        rw = [r["reward_retention"] for r in reps]
        entry = {"replicates": len(reps),
                 "reward_diagonal": [statistics.fmean([x[k][k] for k in range(3)]) for x in rw],
                 "reward_last": [statistics.fmean([x[2][j] for j in range(3)]) for x in rw],
                 "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                 "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps],
                 "policy_move": [float(r["policy_move"]) for r in reps]}
        got[arm] = entry
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": got, "env_draw": doc.get("env_draw") or {},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(MOVED) - set(BOOKKEEPING))},
            "moved": {k: cfg.get(k) for k in MOVED}}


def reading(paid: Path = PAID, loss: Path = LOSS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "inert": {}, "draw": {}, "earning": {},
           "accuracy": {}, "move": {}, "spans": {}}
    got = {"paid": _roll(paid), "loss": _roll(loss)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False,
                    "reason": f"{label} is absent, or carries no reward matrix or no policy movement"}
    out["runs"] = got
    base = got["loss"]["config"]
    for k in sorted(set(base) | set(got["paid"]["config"])):
        old, new = base.get(k), got["paid"]["config"].get(k)
        if old == new:
            continue
        (out["inert"] if _inert(k, old, new) else out["same"])[k] = [old, new]
    da, db = got["loss"]["env_draw"], got["paid"]["env_draw"]
    for k in sorted(set(da) | set(db)):
        out["draw"][k] = da.get(k) == db.get(k)
    out["earning"] = {a: _paired(got["paid"]["arms"][a]["reward_diagonal"],
                                 got["loss"]["arms"][a]["reward_diagonal"]) for a in ARMS}
    out["accuracy"] = {a: _paired(got["paid"]["arms"][a]["accuracy_diagonal"],
                                  got["loss"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["move"] = {label: {a: {"replicates": got[label]["arms"][a]["replicates"],
                               "above_zero": sum(1 for m in got[label]["arms"][a]["policy_move"] if m > 0.0),
                               "smallest": min(got[label]["arms"][a]["policy_move"]),
                               "mean": statistics.fmean(got[label]["arms"][a]["policy_move"])}
                          for a in ARMS} for label in got}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got),
        "same_fields": len(set(base) | set(got["paid"]["config"])),
        "differ": sorted(out["same"]), "inert": sorted(out["inert"]),
        "moved": {label: got[label]["moved"] for label in got},
        "draw_fields": len(out["draw"]), "draw_differ": sorted(k for k, v in out["draw"].items() if not v),
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "reward_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["reward_diagonal"]), 4)
                                    for a in ARMS} for label in got},
        "reward_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["reward_last"]), 4)
                                for a in ARMS} for label in got},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), 4)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), 4)
                                  for a in ARMS} for label in got},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "",
                 "verdict": "REFUSED -- a run is absent, or carries no reward matrix or no policy movement"}
                for c in CLAIMS]
    s = r["spans"]
    moved_ok = (s["moved"]["paid"].get("loop_earn") is True and s["moved"]["loss"].get("loop_earn") in (None, False))
    j1 = {"id": "XB1",
          "measured": f"the config: **{len(s['differ'])}** of {s['same_fields']} differing past the inert rule "
                      f"({s['differ']}), the field moved {s['moved']}; the draw: **{s['draw_fields']}** fields with "
                      f"**{len(s['draw_differ'])}** differing ({s['draw_differ']}); replicates {s['replicates']}",
          "verdict": "MET -- one configuration with only what trains the map moved, and the two runs are one world"
                     if (not s["differ"] and not s["draw_differ"] and s["replicates"] == [MIN_REPS] and moved_ok)
                     else f"FALSIFIER FIRED -- differing {s['differ']}, draw differing {s['draw_differ']}, "
                          f"replicates {s['replicates']}, moved {s['moved']}"}
    mv = r["move"]["paid"]
    thin = [a for a in ARMS if mv[a]["above_zero"] != mv[a]["replicates"] or mv[a]["smallest"] <= 0.0]
    j2 = {"id": "XB2",
          "measured": f"on the paid run the map's distance from the identity is above zero on "
                      f"{ {a: mv[a]['above_zero'] for a in ARMS} } of "
                      f"{ {a: mv[a]['replicates'] for a in ARMS} } replicates, smallest "
                      f"{ {a: round(mv[a]['smallest'], 4) for a in ARMS} }, mean "
                      f"{ {a: round(mv[a]['mean'], 4) for a in ARMS} }",
          "verdict": "MET -- the payout moves the map on every replicate of every arm, the smallest movement at "
                     + f"{min(mv[a]['smallest'] for a in ARMS):.4f}" if not thin else
                     f"FALSIFIER FIRED -- {thin}"}
    earn = r["earning"]
    up = [a for a in ARMS if earn[a]["mean"] >= BAR and earn[a]["sigma"] >= SIGMA]
    bad = len(up) < ARMS_NEEDED
    j3 = {"id": "XB3",
          "measured": f"the paid run's reward diagonal less the task-loss run's, paired over the replicates: "
                      f"{ {a: round(earn[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(earn[a]['sigma'], 2) for a in ARMS} } sigma, from the diagonals "
                      f"{s['reward_diagonal']['paid']} against {s['reward_diagonal']['loss']}",
          "verdict": f"MET -- the payout earns on **{len(up)}** of three arms ({up}) over a bar of {BAR:.2f}"
                     if not bad else
                     f"FALSIFIER FIRED -- {len(up)} of three arms clear the bar and {SIGMA:.0f} sigma ({up})"}
    acc = r["accuracy"]
    rising = [a for a in ARMS if acc[a]["mean"] > 0.0 and acc[a]["sigma"] >= SIGMA]
    j4 = {"id": "XB4",
          "measured": f"the paid run's accuracy diagonal less the task-loss run's: "
                      f"{ {a: round(acc[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(acc[a]['sigma'], 2) for a in ARMS} } sigma, from the diagonals "
                      f"{s['accuracy_diagonal']['paid']} against {s['accuracy_diagonal']['loss']}",
          "verdict": "MET -- being paid does not buy the task: no arm's accuracy rises at two sigma" if not rising
                     else f"FALSIFIER FIRED -- {rising}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the reward trains the agent ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e487` measured the payout as inert for the training; this gives the agent's map its own")
    print("   optimizer and ascends the world's payout into it, and reads both runs again")
    print(f"\n   {'arm':<10} {'paid diag':>10} {'loss diag':>10} {'earned':>9} {'sigma':>7} "
          f"{'paid acc':>9} {'loss acc':>9} {'d acc':>8} {'map move':>9}")
    for a in ARMS:
        e, c = r["earning"][a], r["accuracy"][a]
        print(f"   {a:<10} {r['spans']['reward_diagonal']['paid'][a]:>10.4f} "
              f"{r['spans']['reward_diagonal']['loss'][a]:>10.4f} {e['mean']:>+9.4f} {e['sigma']:>7.2f} "
              f"{r['spans']['accuracy_diagonal']['paid'][a]:>9.4f} "
              f"{r['spans']['accuracy_diagonal']['loss'][a]:>9.4f} {c['mean']:>+8.4f} "
              f"{r['move']['paid'][a]['mean']:>9.4f}")
    print(f"\n   the config: {len(r['spans']['differ'])} differing past the inert rule {r['spans']['differ']}; "
          f"the field moved {r['spans']['moved']}")
    print(f"   the draw: {r['spans']['draw_fields']} fields compared, {r['spans']['draw_differ']} differing")
    print("\n== the registered claims, XB1-XB4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e325` closed on *a reward and a policy*; `e483`, `e485` and `e486` supplied the reward, and")
    print("    until this unit nothing was trained by it)")
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
