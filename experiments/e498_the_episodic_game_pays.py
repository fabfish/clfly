"""E498 -- the episodic game pays: the payout's target is the cue the label names, so the pass can be paid for.

`e495` made the episode work by putting its label at the pass's first trial and `e496` wrote that into the card, and
the runner **refused** that placement with `--loop-reward` -- the environment's target was read one step after the
pass's **last** cue, which with the label first is a distractor. **This unit makes the target follow the label**:
`CueActionEnv.target_step` reads one step after the cue the label names, the last trial where the label is the
episode's last cue and the **first** where it is not, so the two placements are one rule instead of a refusal -- and
a single-trial environment is the one it always was, target step included. Then the episodic pass can be **paid**.

One run and one instrument:

  * `e498 ... episode2_labelfirst_reward` -- `e495`'s own command with `--loop-reward` added, so the world pays the
    pass whose label is its first cue (new);
  * `e495 ... episode2_labelfirst` -- the same pass, read, placement, world and boundary channel without the payout,
    which is the training this one should not touch.

Four claims, registered before the new run's reading was opened.

- **OB1 -- and the payout is the one flag moved.** Against `e495`'s run every recorded config field agrees except
  `loop_reward`, the output path and the saved weights, and every draw field agrees except the payout's own map,
  which is drawn last and recorded only where it exists; each run carries twenty replicates. **Falsifier**: any other
  config field differing, a draw field differing past the payout's map, or a replicate count other than twenty.
- **OB2 -- and the target is the cue the label names.** Measured from the environment's own arithmetic, the step the
  target is read at is the label's cue's step plus one under **either** placement -- **1** with the label first and
  **7** with it last at two trials -- and driven by hand with the payout on, redrawing the episode's other symbols
  leaves the label-first target **exactly** unchanged while the world's final state moves. **Falsifier**: a target
  step that is not the label's plus one under either placement, a label-first target that moves with the other
  symbols, or a final state that does not.
- **OB3 -- and the payout does not touch the training.** The two runs agree on every replicate's accuracy, each arm's
  `learned` vector and its `final_per_task` vector, **record for record**. **Falsifier**: any entry differing; refused
  when a run is absent. *`e487` measured this at one trial per pass and it is what makes the rewarded run's body the
  unpaid run's body, so OB4's currency is the same pass's.*
- **OB4 -- and the world pays in the pass.** On at least two of the three arms the reward's diagonal is **above** its
  last row, paired over the replicates, at **two** sigma. **Falsifier**: fewer than two arms, or one at or below zero.
  *It can fire: at one trial per pass `e485` found the reward's diagonal **below** its last row at **-4.91** to
  **-3.46** sigma, and whether the pass's own currency has the same shape is this claim.*

**What it can do beyond that.** It closes the last hole the episodic line had: the working pass had no payout, because
the environment's target was the pass's last cue's and the runner refused the pair. **So the game now pays for an
episodic pass against the cue the label names**, and the pass, the world, the read and the boundary channel are the
ones `e495` and `e496` measured and recorded.

**What it cannot do.** *One placement pair and one episode length*: two trials of six steps with the label first and
last, the three- and four-trial passes and the interior placements not in it. *And one payout*: the environment's own
target rule, with the payout a linear read of the cue; a reward on the action or sparse in time is a different unit.
*And the payout is a meter here*: `e481` and `e488` train a policy on it and no unit in this line trains anything but
the body and the head, so what the pass pays is what the world pays and not what the agent plays for. *And one
budget, one world and one seed stream*: the card's own setting. *And the target's step moved for the label-first
placement*: every earlier artifact is unaffected because the flag is off there, and the rule is the label's rather
than the last cue's as of this unit.
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
from experiments import e495_the_label_first as e495
from experiments.e172_parser_registry import parser_flags

#: the new run and the unpaid pass it is read against
REWARDED = Path("runs/e498_earned_label_episode2_labelfirst_reward_20reps.json")
UNPAID = e495.FIRST
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
MOVED = ("loop_reward",)
ADDED = ("reward_map_sha1",)
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = e495.EPISODE
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
SYMBOLS = e495.SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
CLAIMS = (
    ("OB1", "and the payout is the one flag moved",
     "Against e495's run every recorded config field agrees except loop_reward, the output path and the saved "
     "weights, and every draw field agrees except the payout's own map, with twenty replicates each",
     "falsifier: any other config field differing, a draw field differing past the payout's map, or a replicate count "
     "other than twenty"),
    ("OB2", "and the target is the cue the label names",
     "The target's step is the label's cue's step plus one under either placement, and redrawing the episode's other "
     "symbols leaves the label-first target exactly unchanged while the world's final state moves",
     "falsifier: a target step that is not the label's plus one under either placement, a label-first target that "
     "moves with the other symbols, or a final state that does not"),
    ("OB3", "and the payout does not touch the training",
     "The two runs agree on every replicate's accuracy, each arm's learned vector and its final_per_task vector, "
     "record for record",
     "falsifier: any entry differing; refused when a run is absent"),
    ("OB4", f"and the world pays in the pass, at {SIGMA:.0f} sigma",
     "On at least two of the three arms the reward's diagonal is above its last row, paired over the replicates, at "
     "two sigma",
     "falsifier: fewer than two arms, or one at or below zero"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in ADDED or key in BOOKKEEPING:
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
        entry = {"replicates": len(reps),
                 "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                 "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps],
                 "learned": [list(r["learned"]) for r in reps],
                 "final_per_task": [list(r["final_per_task"]) for r in reps]}
        rw = [r.get("reward_retention") for r in reps]
        #: a run without the payout records the field with a matrix of `None`s, so the cell's presence is not the
        #: payout's: what is checked is the matrix's own corner
        if any(x is None or x[0][0] is None for x in rw):
            entry["reward_diagonal"] = None
            entry["reward_last"] = None
        else:
            entry["reward_diagonal"] = [statistics.fmean([x[k][k] for k in range(3)]) for x in rw]
            entry["reward_last"] = [statistics.fmean([x[2][j] for j in range(3)]) for x in rw]
        got[arm] = entry
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
                     "added": sorted(set(mine) - set(theirs)), "missing": sorted(set(theirs) - set(mine))}}


def target_steps() -> dict | None:
    """The step the target is read at, from the environment's own arithmetic, under both placements."""
    try:
        from clfly.connectome import annotate, circuits, graph
        from clfly.network import env as fly_env

        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=SIZE)
        rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
        common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=1.0,
                      world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0, reward=True,
                      episode=EPISODE)
        out = {}
        for name, first in (("label_last", False), ("label_first", True)):
            env = fly_env.build(circ, **{**common, "label_first": first})
            out[name] = {"target_step": int(env.target_step), "label_step": int(env.cue_at if first
                                                                              else env.last_cue_step)}
        return out
    except (ImportError, OSError, ValueError):
        return None


def target_is_the_labels(circ, net) -> dict:
    """Driven by hand with the payout on: does the target move when the episode's other symbols do?

    Two draws of the episode's other symbols against the same labels, at the label's first trial and at its last. The
    label-first target is read **before** those symbols arrive, so it cannot move; the label-last one is read seven
    steps after them and does. And the world's final state moves under both, which is what says the manipulation
    reached the pass at all.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=1.0,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0, reward=True,
                  episode=EPISODE)
    rng = np.random.default_rng(29)
    n = SYMBOLS * 8
    y = np.arange(n) % SYMBOLS
    a = np.stack([rng.integers(0, SYMBOLS, size=n) for _ in range(EPISODE - 1)], axis=1)
    b = np.stack([rng.integers(0, SYMBOLS, size=n) for _ in range(EPISODE - 1)], axis=1)
    out = {}
    for name, first in (("label_first", True), ("label_last", False)):
        env = fly_env.build(circ, **{**common, "label_first": first})
        got = []
        for symbols in (a, b):
            u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=symbols), dtype=np.float32))
            fn = env.feedback()
            with torch.no_grad():
                net(u, feedback=fn)
            got.append((fn.last_target.detach().clone(), fn.last_world.detach().clone()))
        target_gap = [float(x) for x in (got[0][0] - got[1][0]).abs().max(dim=1).values]
        world_gap = [float(x) for x in (got[0][1] - got[1][1]).norm(dim=1)]
        out[name] = {"target_largest": max(target_gap), "target_mean": statistics.fmean(target_gap),
                     "world_mean": statistics.fmean(world_gap), "world_largest": max(world_gap), "examples": n}
    return out


def reading(rewarded: Path = REWARDED, unpaid: Path = UNPAID) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "target": {}, "same": {}, "reward": {}, "spans": {}}
    other = load(unpaid)
    got = {"rewarded": _roll(rewarded, other), "unpaid": _roll(unpaid, other)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"{label} is absent"}
    out["runs"] = got
    try:
        import torch

        from clfly.connectome import annotate, circuits, graph
        from clfly.network.model import RateConfig, build_net

        torch.manual_seed(0)
        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=SIZE)
        net = build_net(circ, RateConfig(tau=TAU)).torch_model()
        out["target"] = {"steps": target_steps(), "moves": target_is_the_labels(circ, net)}
    except (ImportError, OSError, ValueError) as exc:
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    same = {}
    for a in ARMS:
        on, off = got["rewarded"]["arms"][a], got["unpaid"]["arms"][a]
        same[a] = {"learned": on["learned"] == off["learned"],
                   "final_per_task": on["final_per_task"] == off["final_per_task"],
                   "replicates": on["replicates"] == off["replicates"]}
    out["same"] = same
    out["reward"] = {a: _paired(got["rewarded"]["arms"][a]["reward_diagonal"],
                                got["rewarded"]["arms"][a]["reward_last"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "episode": EPISODE, "chance": CHANCE,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "config": {label: got[label]["config"] for label in got},
        "draw": {label: got[label]["draw"] for label in got},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), 4)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), 4)
                                  for a in ARMS} for label in got},
        "reward_diagonal": {a: (None if got["rewarded"]["arms"][a]["reward_diagonal"] is None else
                                round(statistics.fmean(got["rewarded"]["arms"][a]["reward_diagonal"]), 4))
                            for a in ARMS},
        "reward_last": {a: (None if got["rewarded"]["arms"][a]["reward_last"] is None else
                            round(statistics.fmean(got["rewarded"]["arms"][a]["reward_last"]), 4))
                        for a in ARMS},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    moved = s["config"]["rewarded"]["moved"]
    differ = s["config"]["rewarded"]["differ"]
    draw = s["draw"]["rewarded"]
    j1 = {"id": "OB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: **{draw['added']}** added and **{draw['differ']}** differing; replicates "
                      f"{s['replicates']}",
          "verdict": "MET -- the payout is the one flag moved, over one pass, one read and one world" if
                     (not differ and moved.get("loop_reward") is True and draw["added"] == sorted(ADDED)
                      and not draw["differ"] and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    steps, moves = r["target"]["steps"], r["target"]["moves"]
    ok_steps = (steps["label_first"]["target_step"] == steps["label_first"]["label_step"] + 1
                and steps["label_last"]["target_step"] == steps["label_last"]["label_step"] + 1)
    ok_moves = (moves["label_first"]["target_largest"] == 0.0
                and moves["label_last"]["target_largest"] > 0.0
                and moves["label_first"]["world_mean"] > 0.0)
    j2 = {"id": "OB2",
          "measured": f"the target's step is {steps['label_first']['target_step']} with the label at step "
                      f"{steps['label_first']['label_step']} and {steps['label_last']['target_step']} with it at "
                      f"{steps['label_last']['label_step']}; redrawing the episode's other symbols moves the "
                      f"label-first target by **{moves['label_first']['target_largest']:.4e}** and its final state by "
                      f"{moves['label_first']['world_mean']:.4f}, and the label-last target by "
                      f"{moves['label_last']['target_largest']:.4f}",
          "verdict": "MET -- the target is the cue the label names under either placement, and the label-first one is "
                     "out of the other symbols' reach" if (ok_steps and ok_moves) else
                     f"FALSIFIER FIRED -- steps {steps}, target moving {moves['label_first']['target_largest']:.4e} "
                     f"and {moves['label_last']['target_largest']:.4f}, state "
                     f"{moves['label_first']['world_mean']:.4f}"}
    same = r["same"]
    differ_entries = sorted(f"{a}.{k}" for a, v in same.items() for k, ok in v.items() if not ok)
    j3 = {"id": "OB3",
          "measured": f"the two runs against each other, arm by arm: learned vectors "
                      f"{ {a: same[a]['learned'] for a in ARMS} }, final_per_task vectors "
                      f"{ {a: same[a]['final_per_task'] for a in ARMS} } and replicate counts "
                      f"{ {a: same[a]['replicates'] for a in ARMS} }, {len(differ_entries)} differing",
          "verdict": "MET -- the payout does not touch the training: the two runs are the same accuracy, record for "
                     "record" if not differ_entries else f"FALSIFIER FIRED -- {differ_entries}"}
    rw = r["reward"]
    missing = [a for a in ARMS if s["reward_diagonal"][a] is None]
    above = [a for a in ARMS if rw[a]["mean"] > 0.0 and rw[a]["sigma"] >= SIGMA]
    j4 = {"id": "OB4",
          "measured": f"the world pays in the pass: the reward's diagonals are {s['reward_diagonal']} against the "
                      f"last rows {s['reward_last']}, and the contrasts are "
                      f"{ {a: round(rw[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rw[a]['sigma'], 2) for a in ARMS} } sigma, with {len(missing)} arms carrying no "
                      f"reward matrix",
          "verdict": f"MET -- the reward's diagonal is above its last row on **{len(above)}** of three arms ({above})"
                     if (len(above) >= 2 and not missing) else
                     f"FALSIFIER FIRED -- {len(above)} of three arms above at two sigma ({above}), missing {missing}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the episodic game pays ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the runner refused the label-first placement with --loop-reward because the environment's target was")
    print("   the pass's last cue's; the target now follows the label, and this is the pass being paid")
    print(f"\n   {'arm':<10} {'reward diag':>12} {'reward last':>12} {'contrast':>10} {'sigma':>7} "
          f"{'accuracy diag':>14}")
    for a in ARMS:
        c = r["reward"][a]
        print(f"   {a:<10} {r['spans']['reward_diagonal'][a]:>12.4f} {r['spans']['reward_last'][a]:>12.4f} "
              f"{c['mean']:>+10.4f} {c['sigma']:>7.2f} {r['spans']['accuracy_diagonal']['rewarded'][a]:>14.4f}")
    print(f"\n   the target's step: {r['target']['steps']}")
    print(f"   the config: {len(r['spans']['config']['rewarded']['differ'])} differing past the inert rule; the draw: "
          f"added {r['spans']['draw']['rewarded']['added']} and differing {r['spans']['draw']['rewarded']['differ']}")
    print("\n== the registered claims, OB1-OB4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e495` and `e496` made the episodic pass work; this is the payout it can be read against)")
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
