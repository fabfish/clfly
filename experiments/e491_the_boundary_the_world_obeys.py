"""E491 -- the boundary the world obeys: whether dropping the state at the trial's mark recovers the trial's label.

`e489` gave the pass an **episode** of trials and the episode a **boundary** channel, and measured what the carry
costs: two episodes sharing the last trial's cue and differing in the earlier ones left world states at the read step
that differed by **0.7601** at **12.62** sigma against a state scale of **0.7727**, and every arm sat at the
four-class chance. **So the channel was a signal over a world that carried the episode anyway**, which is what this
unit changes: `--loop-episode-reset` makes the world **obey** the boundary, dropping the carried state at every
trial's first step, so each trial starts from a world at rest and the read step sees the last trial alone.

One run and one measurement, one flag apart from `e489`'s boundary run:

  * `e491 ... reset` -- the card's command with `--loop-episode 3 --loop-boundary --loop-episode-reset` (new);
  * `e489 ... boundary` -- the same three flags without the reset, which is the carry this one drops.

Three claims, registered before the new run's reading was opened.

- **GB1 -- and the one flag moved, and the world's rule is what it moved.** Against `e489`'s boundary run every
  recorded config field agrees except `loop_episode_reset`, the output path and the saved weights, and every draw
  field agrees except the one field the flag adds (`episode_reset`), the two runs drawing one world, one payout-less
  environment and **one boundary channel**; each run carries twenty replicates. **Falsifier**: any other config field
  differing, a draw field differing past the one the flag adds, or a replicate count other than twenty.
- **GB2 -- and the world's rule obeys the mark.** Driven by hand, with no model and no cue -- one trajectory per
  example, two of them agreeing from the **last trial's first step** onward and differing before it -- the world's
  state at the read step differs by **exactly zero** with the reset, and by a difference that resolves at **two**
  sigma without it. **Falsifier**: a non-zero difference with the reset, or one that does not resolve without it.
- **GB3 -- and the trial's label is recoverable once the world starts at rest.** On **at least two of the three
  arms** the reset run's accuracy diagonal is at least **0.10** above the four-class chance of **0.25** and above
  `e489`'s boundary run's diagonal at **two** sigma. **Falsifier**: fewer than two arms, or an arm within **0.05**
  of chance. *This is the unit's own question and it can fire: the model's recurrent state still carries the earlier
  trials, so what the reset removes is the world's share of the carry and not the episode.*

**What it can do beyond that.** It separates the two things `e489` left joined: the boundary as a **signal** the agent
receives and the boundary as a **rule** the world follows. Neither the card nor the corpus has ever had the second,
and the ablation is the difference between a marker over a carry and a marker over a reset -- which is the smallest
form of "the world knows where the episode starts".

**What it cannot do.** *One episode length and one reset*: three trials of four steps is the length `e489` read, and
a sweep of two, three, four and six is not in the unit. *And the reset is the world's and not the agent's*: the
model's recurrent state still carries the earlier trials, so a label buried in **that** is not touched here. *And one
budget, one world and one seed stream*: the card's own setting. *And the accuracy is the corpus's own metric on a
task at chance*: a recovery is a comparison of two runs whose arms are near the floor, so the sigmas are large
numbers about small differences. *And the boundary channel is unedited*: what this unit changes is the world's rule,
and what a **policy** would make of a boundary it can act on is `e488`'s question, not this one.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489
from experiments.e172_parser_registry import parser_flags

#: the new run and the carry it drops
RESET = Path("runs/e491_earned_label_episode3_boundary_reset_20reps.json")
CARRY = e489.BOUND
CARD = e489.CARD
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the one field the run moves in the configuration, and the one the flag adds to the draw
MOVED = ("loop_episode_reset",)
ADDED = ("episode_reset",)
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = e489.EPISODE
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
NOISE = e489.NOISE
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
BAR = 0.10
CLAIMS = (
    ("GB1", "and the one flag moved, and the world's rule is what it moved",
     "Against e489's boundary run every recorded config field agrees except loop_episode_reset, the output path and "
     "the saved weights, and every draw field agrees except the one the flag adds, with twenty replicates each",
     "falsifier: any other config field differing, a draw field differing past the one the flag adds, or a replicate "
     "count other than twenty"),
    ("GB2", f"and the world's rule obeys the mark, at {SIGMA:.0f} sigma",
     "Driven by hand with two trajectories agreeing from the last trial's first step onward and differing before it, "
     "the world's state at the read step differs by exactly zero with the reset and by a difference that resolves at "
     "two sigma without it",
     "falsifier: a non-zero difference with the reset, or one that does not resolve without it"),
    ("GB3", f"and the trial's label is recoverable once the world starts at rest, at {BAR:.2f} and {SIGMA:.0f} sigma",
     "On at least two of the three arms the reset run's accuracy diagonal is at least 0.10 above the four-class "
     "chance of 0.25 and above e489's boundary run's diagonal at two sigma",
     "falsifier: fewer than two arms, or an arm within 0.05 of chance"),
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


def _roll(path: Path, other: dict | None) -> dict | None:
    doc = load(path)
    if not doc or other is None:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                    "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps]}
    cfg = doc.get("config") or {}
    their_cfg = other.get("config") or {}
    same, inert, differ = {}, {}, {}
    for k in sorted(set(cfg) | set(their_cfg)):
        old, new = their_cfg.get(k), cfg.get(k)
        if old == new:
            same[k] = new
        elif _inert(k, old, new):
            inert[k] = [old, new]
        else:
            differ[k] = [old, new]
    mine, theirs = doc.get("env_draw") or {}, other.get("env_draw") or {}
    agree = {k: theirs.get(k) == mine.get(k) for k in theirs}
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "draw": {"agree": agree, "differ": sorted(k for k, ok in agree.items() if not ok),
                     "added": sorted(set(mine) - set(theirs)), "missing": sorted(set(theirs) - set(mine)),
                     "card_fields": len(theirs)}}


def driven(circ) -> dict:
    """The world's own rule, driven by hand: no model, no cue, and the state at the read step for two pasts.

    The two trajectories agree from the **last trial's first step** onward -- which is where the boundary marks -- and
    differ at every step before it. So the difference this reports is the world's dependence on the episode's earlier
    trials and nothing else: the reset is the rule that drops it, and the model's own state is out of the measurement
    by construction.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=NOISE,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0)
    rng = np.random.default_rng(41)
    n = READOUT_SIZE * 2
    last_trial = TAU - TAU // EPISODE
    a = torch.from_numpy((rng.standard_normal((n, circ.n_neurons)) / 3.0).astype(np.float32))
    b = torch.from_numpy((rng.standard_normal((n, circ.n_neurons)) / 3.0).astype(np.float32))
    tail = torch.from_numpy((rng.standard_normal((n, circ.n_neurons)) / 3.0).astype(np.float32))
    got = {}
    for label, extra in (("carry", {}), ("reset", {"episode_reset": True})):
        env = fly_env.build(circ, **{**common, "episode": EPISODE, "boundary": True, **extra})
        states = []
        for early in (a, b):
            fn = env.feedback()
            with torch.no_grad():
                for t in range(TAU):
                    fn(tail if t >= last_trial else early, t)
            states.append(fn.last_world.detach().clone())
        gap = [float(x) for x in (states[0] - states[1]).norm(dim=1)]
        got[label] = {"pairing": _paired(gap, [0.0] * len(gap)), "largest": max(gap),
                      "scale": float(states[0].norm(dim=1).mean()), "at": last_trial, "examples": n}
    return got


def reading(reset: Path = RESET, carry: Path = CARRY) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "rule": {}, "recovery": {}, "spans": {}}
    other = load(carry)
    got = {"reset": _roll(reset, other), "carry": _roll(carry, other)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"{label} is absent"}
    out["runs"] = got
    try:
        from clfly.connectome import annotate, circuits, graph

        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=SIZE)
        out["rule"] = driven(circ)
    except (ImportError, OSError, ValueError) as exc:
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    out["recovery"] = {a: _paired(got["reset"]["arms"][a]["accuracy_diagonal"],
                                  got["carry"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "episode": EPISODE, "chance": CHANCE,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "config": {label: got[label]["config"] for label in got},
        "draw": {label: got[label]["draw"] for label in got},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), 4)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), 4)
                                  for a in ARMS} for label in got},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    moved = s["config"]["reset"]["moved"]
    differ = s["config"]["reset"]["differ"]
    draw = s["draw"]["reset"]
    j1 = {"id": "GB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: {draw['card_fields']} fields of the carry run's with "
                      f"**{draw['added']}** added and **{draw['differ']}** differing; replicates {s['replicates']}",
          "verdict": "MET -- one flag moved and the world's rule is what it moved, the two runs one world and one "
                     "boundary channel" if (not differ and moved.get("loop_episode_reset") is True
                                            and draw["added"] == sorted(ADDED) and not draw["differ"]
                                            and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    rule = r["rule"]
    c, z = rule["carry"], rule["reset"]
    j2 = {"id": "GB2",
          "measured": f"driven by hand at the step the boundary marks, the world's state at the read step differs "
                      f"between two pasts by **{z['pairing']['mean']:.4e}** (largest {z['largest']:.4e}) with the "
                      f"reset and by {c['pairing']['mean']:.4f} at {c['pairing']['sigma']:.2f} sigma (largest "
                      f"{c['largest']:.4f}) without it, against a state scale of {c['scale']:.4f}",
          "verdict": "MET -- the world's rule obeys the mark: the state at the read step is the last trial's alone "
                     "with the reset and the episode's without it" if
                     (z["largest"] == 0.0 and c["pairing"]["mean"] > 0.0 and c["pairing"]["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- reset largest {z['largest']:.4e}, carry mean {c['pairing']['mean']:.4f} at "
                     f"{c['pairing']['sigma']:.2f} sigma"}
    rec = r["recovery"]
    diag = s["accuracy_diagonal"]["reset"]
    up = [a for a in ARMS if diag[a] >= CHANCE + BAR and rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
    thin = [a for a in ARMS if diag[a] < CHANCE + 0.05]
    j3 = {"id": "GB3",
          "measured": f"the reset run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f}, and against "
                      f"the carry run's {s['accuracy_diagonal']['carry']} they change by "
                      f"{ {a: round(rec[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, with {len(up)} of three arms over "
                      f"the bar and {len(thin)} within 0.05 of chance",
          "verdict": f"MET -- the trial's label is recoverable once the world starts at rest, on **{len(up)}** of "
                     f"three arms ({up})" if (len(up) >= 2 and not thin) else
                     f"FALSIFIER FIRED -- {len(up)} of three arms over the bar and two sigma ({up}), thin {thin}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the boundary the world obeys ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e489` gave the pass an episode and the episode a boundary channel, and the world carried it anyway;")
    print("   this makes the world drop its state at the mark and asks whether the last trial's label comes back")
    print(f"\n   {'arm':<10} {'reset acc':>10} {'carry acc':>10} {'change':>9} {'sigma':>7} "
          f"{'reset last':>11} {'carry last':>11}")
    for a in ARMS:
        c = r["recovery"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['reset'][a]:>10.4f} "
              f"{r['spans']['accuracy_diagonal']['carry'][a]:>10.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['reset'][a]:>11.4f} "
              f"{r['spans']['accuracy_last']['carry'][a]:>11.4f}")
    print(f"\n   the config: {len(r['spans']['config']['reset']['differ'])} differing past the inert rule; the draw: "
          f"added {r['spans']['draw']['reset']['added']} and differing {r['spans']['draw']['reset']['differ']}")
    print(f"   the world's rule, driven by hand at the mark: with the reset {r['rule']['reset']['pairing']['mean']:.4e} "
          f"and without it {r['rule']['carry']['pairing']['mean']:.4f} at "
          f"{r['rule']['carry']['pairing']['sigma']:.2f} sigma")
    print("\n== the registered claims, GB1-GB3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e489` left the boundary a signal over a carry; this is the boundary the world itself follows)")
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
