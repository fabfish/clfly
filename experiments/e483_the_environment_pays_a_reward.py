"""E483 -- the environment pays a reward: the other half of the sentence `e325` and `e361` both closed on.

`e325` closed on *"What is missing is the thing that makes it a game rather than a loop: **a reward and a policy**"*,
and the card's `absent` list has carried **a reward** and **a policy** since its first revision. `e477` gave the
environment a **policy**, `e481` put one in the runner, and `e482`'s fifteenth revision took the policy off the list.
**This unit gives the environment a reward**, which is the half still owing.

`CueActionEnv` gains **`reward_map`**: a `(world_dims, n_cue)` map, drawn from the environment's seed when the new
`reward` flag is on, against which the **cue itself** sets a target -- the cue population's activity one step after the
cue arrives, through that map -- and the trial's reward is the **negative squared distance** from the world's final
state to it, read at the last step and per example. **The target depends on the cue and not on the label**, which is
what lets an environment pay a reward the agent's own action decides, since the environment never sees a label. Four
claims, registered before any reward was read.

- **RA1 -- and the payout is the only field the flag draws.** Two environments at one seed, one with the reward and
  one without, agree on every recorded draw field -- the populations, the cue templates, the drive's map, the read
  map, the coupling and the world's dimensions and leak -- and differ only in the payout's own map, which is drawn
  last and recorded only where it exists. **Falsifier**: any other draw field differing, or the payout's map absent
  where it was asked for.
- **RA2 -- and the cue sets the payout.** Across the four cue symbols the mean reward's spread exceeds the spread of
  the rewards **within** a symbol, on every replicate, and the two do not overlap. **Falsifier**: the across-symbol
  spread at or below the within-symbol one on any replicate.
- **RA3 -- and the payout is the agent's to earn.** A 64-number linear policy, initialized at the identity and trained
  by ascent on the reward through the loop, earns at least **2.00** more than the identity policy on cues it was not
  trained on, paired over the replicates, at **two** sigma or more. **Falsifier**: a gain below **0.50**, or one that
  does not resolve.
- **RA4 -- and the goal is the cue's, read one step after it arrives.** At a cue delivered at the read step the
  target is read from a state at rest, so its own across-symbol spread is **zero** while at the first step it is above
  zero. **Falsifier**: a target spread above zero at the late step, or one at zero at the first.

**What it can do beyond that.** It closes the reward half of `e325`'s sentence at the environment, which is where
`e477` closed the policy half before `e481` and `e482` carried it into the benchmark: the reward is a scalar the world
pays, its goal is the agent's own cue, and what the agent does about it is its action.

**What it cannot do.** *The payout is not the benchmark's*: the runner does not carry the flag, so no artifact in the
corpus records a reward and the card's `absent` list still names one -- a runner change and a revision are different
units, which is the order `e477`, `e481` and `e482` already followed. *And the goal is a linear read of the cue*: a
payout on the label, on the action or sparse in time is not in it. *And the reward is bounded above by zero*, a
squared distance, so its scale is the world's and not a designer's. *And the body is frozen on the frozen rolls*: the
policy is 64 numbers over the action population. *And eight replicates are not the population*: the sigma is the
paired one over the worlds the replicates share.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: the card's own substrate and world, and the payout's flag on top of it
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
N_TRAIN = 512
N_HELD = 512
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
REPLICATES = (0, 1, 2, 3, 4, 5, 6, 7)
STEPS = 300
LR = 0.05
#: the draw fields two environments at one seed must agree on, the payout's map aside
DRAW_FIELDS = ("n_symbols", "n_cue", "n_action", "n_feedback", "cue_sha1", "action_sha1", "feedback_sha1",
               "world_sha1", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1", "world_coupled",
               "world_nonlinear", "world_dims", "world_leak", "cue_at", "drive_from_cue")
SIGMA = 2.0
GAIN_BAR = 2.00
GAIN_FLOOR = 0.50
CLAIMS = (
    ("RA1", "and the payout is the only field the flag draws",
     "Two environments at one seed, one with the reward and one without, agree on every recorded draw field except the "
     "payout's own map, which is drawn last and recorded only where it exists",
     "falsifier: any other draw field differing, or the payout's map absent where it was asked for"),
    ("RA2", "and the cue sets the payout",
     "Across the four cue symbols the mean reward's spread exceeds the spread of the rewards within a symbol, on every "
     "replicate",
     "falsifier: the across-symbol spread at or below the within-symbol one on any replicate"),
    ("RA3", f"and the payout is the agent's to earn, by {GAIN_BAR:.2f} at {SIGMA:.0f} sigma",
     "A policy initialized at the identity and trained by ascent on the reward earns at least 2.00 more than the "
     "identity policy on cues it was not trained on, paired over the replicates, at two sigma or more",
     f"falsifier: a gain below {GAIN_FLOOR:.2f}, or one that does not resolve"),
    ("RA4", "and the goal is the cue's, read one step after it arrives",
     "At a cue delivered at the read step the target's own across-symbol spread is zero while at the first step it is "
     "above zero",
     "falsifier: a target spread above zero at the late step, or one at zero at the first"),
)


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _fingerprint(mat) -> str:
    return hashlib.sha1(np.asarray(mat, dtype=np.float64).tobytes()).hexdigest()[:12]


def one_replicate(circ, net, seed: int, noise: float = NOISE) -> dict:
    """One replicate: the payout's map, the cue's own target, the spread it makes, and a policy trained on it.

    ``noise`` is the cue's own noise and is this unit's constant unless a caller moves it, which is what the sweep
    beside this unit does; the same value reaches every environment a replicate builds, and the cue's noise is drawn
    from the same per-example generator whatever it is, so two levels differ in the amplitude of one realisation.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))

    def build(reward: bool, cue_at: int = 0):
        return fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE,
                             gain=GAIN, noise=noise, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS,
                             world_coupled=True, cue_at=cue_at, reward=reward)

    e, bare = build(True), build(False)
    drew = {k: (e.summary().get(k) == bare.summary().get(k)) for k in DRAW_FIELDS}
    rng = np.random.default_rng(seed + 7)
    y_all = rng.integers(0, N_SYMBOLS, size=N_TRAIN + N_HELD)
    y_tr, y_te = y_all[:N_TRAIN], y_all[N_TRAIN:]
    u_tr = torch.from_numpy(np.asarray(e.cue_input(y_tr, np.random.default_rng(seed + 31)), dtype=np.float32))
    u_te = torch.from_numpy(np.asarray(e.cue_input(y_te, np.random.default_rng(seed + 61)), dtype=np.float32))

    def payout(policy, u_batch):
        e.policy = None if policy is None else policy
        fn = e.feedback()
        with torch.no_grad():
            net(u_batch, feedback=fn)
        return fn.last_reward, fn.last_target

    eye = torch.eye(len(e.action_neurons), dtype=torch.float32)
    rw_id, tgt_id = payout(None, u_te)
    rw_eye, _ = payout(eye, u_te)
    per_symbol = [float(rw_eye[torch.as_tensor(y_te) == s].mean()) for s in range(N_SYMBOLS)]
    within = statistics.fmean([float(rw_eye[torch.as_tensor(y_te) == s].std()) for s in range(N_SYMBOLS)])
    across = max(per_symbol) - min(per_symbol)
    target_spread = (max(float(tgt_id[torch.as_tensor(y_te) == s].mean(dim=0).abs().mean())
                         for s in range(N_SYMBOLS))
                     - min(float(tgt_id[torch.as_tensor(y_te) == s].mean(dim=0).abs().mean())
                           for s in range(N_SYMBOLS)))
    #: the late-cue control: the same environment with the cue delivered at the read step, so the state the target
    #: is read from is at rest. It gets **its own** cue input -- the same examples through an environment whose cue
    #: arrives at the last step -- since feeding it the first environment's array would put the cue at step 0 again.
    late = build(True, cue_at=TAU - 1)
    fn = late.feedback()
    with torch.no_grad():
        net(torch.from_numpy(np.asarray(late.cue_input(y_te, np.random.default_rng(seed + 61)), dtype=np.float32)),
            feedback=fn)
    lw, lt = fn.last_reward, fn.last_target
    late_target_max = float(lt.abs().max()) if lt is not None else None

    pol = torch.nn.Parameter(eye.clone())
    opt = torch.optim.Adam([pol], lr=LR)
    for _ in range(STEPS):
        opt.zero_grad()
        e.policy = pol
        fn = e.feedback()
        net(u_tr, feedback=fn)
        (-fn.last_reward.mean()).backward()
        opt.step()
    rw_trained, _ = payout(pol.detach(), u_te)

    return {"seed": int(seed), "draw_agrees": drew, "reward_sha1": e.summary().get("reward_map_sha1"),
            "per_symbol": per_symbol, "within": within, "across": across,
            "target_spread": target_spread,
            "late_target_max": late_target_max,
            "late_reward": float(lw.mean()) if lw is not None else None,
            "identity": float(rw_eye.mean()), "with_none": float(rw_id.mean()),
            "trained": float(rw_trained.mean()), "move": float((pol.detach() - eye).norm())}


def reading(replicates=REPLICATES, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    cells = [one_replicate(circ, net, int(r)) for r in replicates]
    out = {"ok": True, "reason": None, "cells": cells, "spreads": {}, "payout": {}, "spans": {},
           "worlds": {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED,
                      "tau": TAU, "n_symbols": N_SYMBOLS, "n_train": N_TRAIN, "n_held": N_HELD,
                      "dims": WORLD_DIMS, "leak": WORLD_LEAK, "replicates": list(map(int, replicates)),
                      "steps": STEPS, "lr": LR}}
    out["spreads"] = _paired([c["across"] for c in cells], [c["within"] for c in cells])
    out["spreads"]["values"] = [c["across"] - c["within"] for c in cells]
    out["payout"] = _paired([c["trained"] for c in cells], [c["identity"] for c in cells])
    out["payout"]["values"] = [c["trained"] - c["identity"] for c in cells]
    out["spans"] = {
        "replicates": len(cells), "fields": len(DRAW_FIELDS),
        "draw_agrees": {k: all(c["draw_agrees"][k] for c in cells) for k in DRAW_FIELDS},
        "draw_differ": sorted(k for k in DRAW_FIELDS if not all(c["draw_agrees"][k] for c in cells)),
        "reward_sha1": [c["reward_sha1"] for c in cells],
        "across": [round(c["across"], 4) for c in cells], "within": [round(c["within"], 4) for c in cells],
        "target_spread_min": min(c["target_spread"] for c in cells),
        "late_target_max": max(c["late_target_max"] for c in cells),
        "late_reward": [round(c["late_reward"], 4) for c in cells],
        "identity": [round(c["identity"], 4) for c in cells],
        "with_none": [round(c["with_none"], 4) for c in cells],
        "moves": [round(c["move"], 3) for c in cells],
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the replicates were not rolled"} for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "RA1",
          "measured": f"{s['fields']} draw fields compared between the same environment with the payout and without "
                      f"it, over {s['replicates']} replicates: **{len(s['draw_differ'])}** differing "
                      f"({s['draw_differ']}), and the payout's own map is "
                      f"{'recorded' if all(s['reward_sha1']) else 'absent'} on "
                      f"{len([x for x in s['reward_sha1'] if x])} of {s['replicates']}",
          "verdict": "MET -- the flag draws the payout and nothing else" if
                     (not s["draw_differ"] and all(s["reward_sha1"])) else
                     f"FALSIFIER FIRED -- differing {s['draw_differ']}, maps {s['reward_sha1']}"}
    bad = [c["seed"] for c in r["cells"] if c["across"] <= c["within"]]
    d = r["spreads"]
    j2 = {"id": "RA2",
          "measured": f"the across-symbol spread runs {s['across']} against the within-symbol spread {s['within']}, a "
                      f"paired margin of **{d['mean']:+.4f}** at **{d['sigma']:+.2f}** sigma over {d['n']} replicates, "
                      f"with {len(bad)} replicates not separating them",
          "verdict": f"MET -- the cue sets the payout on every replicate, by {d['mean']:+.4f} at {d['sigma']:+.2f} "
                     f"sigma" if (not bad and d["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- {bad} do not separate, the margin {d['mean']:+.4f} at {d['sigma']:+.2f}"}
    p = r["payout"]
    j3 = {"id": "RA3",
          "measured": f"the payout runs {s['identity']} at the identity policy and {[round(c['trained'], 4) for c in r['cells']]}"
                      f" trained, a paired gain of **{p['mean']:+.4f}** at **{p['sigma']:+.2f}** sigma",
          "verdict": f"MET -- the payout is earned, {p['mean']:+.4f} above the identity policy at {p['sigma']:+.2f} "
                     f"sigma" if (p["mean"] >= GAIN_BAR and p["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- a gain of {p['mean']:+.4f} at {p['sigma']:+.2f} sigma, against a bar of "
                     f"{GAIN_BAR:.2f}" if (p["mean"] < GAIN_FLOOR or p["sigma"] < SIGMA) else
                     f"NULL -- a gain of {p['mean']:+.4f} between {GAIN_FLOOR:.2f} and {GAIN_BAR:.2f}"}
    j4 = {"id": "RA4",
          "measured": f"the target's own across-symbol spread is at least **{s['target_spread_min']:.4f}** at the "
                      f"first cue step and at most **{s['late_target_max']:.1e}** at the read step, with the payout "
                      f"there {s['late_reward']}",
          "verdict": "MET -- the goal is the cue's, read one step after it arrives, and at rest when the cue arrives "
                     "at the read step" if (s["target_spread_min"] > 0.0 and s["late_target_max"] == 0.0) else
                     f"FALSIFIER FIRED -- the first-step spread {s['target_spread_min']:.4f} and the late-step "
                     f"{s['late_target_max']:.1e}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the environment pays a reward ==")
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        print("   REFUSED -- the replicates were not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    w = r["worlds"]
    print(f"   circuit {w['circuit']} ({w['size']} neurons), the card's {w['dims']}-dimensional coupled world at "
          f"leak {w['leak']}, {w['n_symbols']} cue symbols, {w['replicates']} replicates")
    print("   the world's payout is the negative squared distance from its final state to the target the CUE sets,")
    print("   read off the state one step after the cue arrives through a map the environment draws")
    print(f"\n   {'rep':>4} {'across':>8} {'within':>8} {'identity':>9} {'trained':>9} {'gain':>8} "
          f"{'target spr':>11} {'late target':>12}")
    for c in r["cells"]:
        print(f"   {c['seed']:>4} {c['across']:>8.4f} {c['within']:>8.4f} {c['identity']:>9.4f} "
              f"{c['trained']:>9.4f} {c['trained'] - c['identity']:>+8.4f} {c['target_spread']:>11.4f} "
              f"{c['late_target_max']:>12.1e}")
    print(f"\n   the draw fields the flag leaves alone: {r['spans']['fields']} compared, "
          f"{r['spans']['draw_differ']} differing")
    print("\n== the registered claims, RA1-RA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e325` closed on *a reward and a policy*; `e477` gave the environment the second and `e481`/`e482`")
    print("    carried it into the benchmark and the card. This is the first)")
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
