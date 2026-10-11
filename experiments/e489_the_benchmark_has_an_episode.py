"""E489 -- the benchmark has an episode: the pass is a run of trials, the world's state is the episode's, and a
boundary channel says where it opens.

`env.py`'s docstring has named three absences since the environment existed -- *"There is no reward, no episode
boundary and no policy"* -- and two of them are closed: `e477` gave the environment a policy and `e483` gave it a
payout, with `e481`, `e482`, `e485` and `e486` carrying both into the benchmark and the card. **The third is this
unit.** A pass has been **one trial** for every artifact in the corpus: a cue at step ``0``, the loop after it, and a
world whose state is that trial's. Here the pass becomes an **episode of `--loop-episode N` trials**, one every
``tau / N`` steps, each with its own cue, so what the world carries at the read step is the episode's state and the
earlier trials are the episode's own history. And the **boundary** -- `--loop-boundary` -- is a channel drawn from
the environment's own seed that carries ``+gain`` at the step the episode opens and ``-gain`` at every trial that
continues it: the one signal the cue cannot carry, since the cue pulses at every trial's first step whatever the
trial's position, so the agent is told whether the state it is carrying is at rest.

Two runs of the card's neutral roll, one flag apart, and the corpus's roll beside them:

  * `e489 ... episode3_boundary` -- the card's command with `--loop-episode 3 --loop-boundary` (new);
  * `e489 ... episode3` -- the same with `--loop-episode 3` alone (new);
  * `e438` -- the card's own roll, one trial per pass, which the endpoint is read against.

Five claims, registered before either run was read.

- **FA1 -- and the endpoint is exact, and only the episode moved.** Built with the flag off the environment is the
  one the corpus holds: its draw is the card's own `env_draw` **field for field**, it adds no `episode_len` and no
  `boundary_sha1`, and `cue_input` is bit-identical to the single-pulse array. Each run carries the card's config
  with **no** field differing past the inert rule, the fields moved being `loop_episode` and `loop_boundary` alone;
  the plain run's draw is the card's plus `episode_len` and nothing else, and the boundary run's is the card's plus
  `episode_len`, `boundary_sha1`, `n_boundary` and `boundary_gain`. **Falsifier**: a draw field of the card's
  differing, an added field at the endpoint, an array differing, a config field differing past the two flags, or an
  added or missing draw field that is not one of the five.
- **FA2 -- and the world's state at the read step is the episode's and not the last trial's.** At the card's own
  world and body, two episodes that **share** the last trial's cue and the cue's noise and differ in the earlier
  trials' cues give world states at the read step that differ, on the run's own examples, at **two** sigma; at one
  trial per pass the same manipulation moves the state by **exactly zero**. **Falsifier**: a mean difference of zero
  at the episode, or one that does not resolve, or a non-zero difference at the single-trial endpoint.
- **FA3 -- and the boundary is a channel of its own.** With the boundary drawn, the closure's drive is `+gain` on
  the boundary neurons at the episode's first step, `-gain` at every later trial's first step and **zero** at every
  other step, at the gain the draw records; the boundary neurons are disjoint from the cue, action and feedback
  populations and are in the task's own input set; and with the flag off no such channel is drawn and the input set
  is the cue's and the feedback's alone. **Falsifier**: a step whose marker is not the declared sign or is non-zero
  where it should be zero, a population overlap, a channel outside the input set, or a channel drawn at the endpoint.
- **FA4 -- and the episodic task is learned.** On the plain run -- three trials to the pass, no boundary -- every
  arm's accuracy diagonal is at least **0.10** above the four-class chance of **0.25**. **Falsifier**: an arm within
  **0.05** of chance. *Three trials of four steps is a shorter path from the label to the read than the corpus's own
  eleven, so whether the episode is learnable at all is a question and not an assumption.*
- **FA5 -- and the boundary does not buy the task.** On no arm is the boundary run's accuracy diagonal above the
  plain run's at **two** sigma. **Falsifier**: an arm resolving upward. *The channel is information about the
  world's state and not the label, so what it should move is how hard the episode is to carry, if anything.*

**What it can do beyond that.** It closes the third of the environment's three absences, so the card's `absent`
list loses its last entry: the game now has a world, a reward, a policy, a reward that trains the agent, and an
episode with a boundary. The structure it adds is the one `e322` and `e333` named as missing -- a time axis above
the trial -- and it is the first object in this corpus that is a **run of trials** rather than a trial.

**What it cannot do.** *One episode length*: three trials is the longest this pass gives a cue room for, and a sweep
of two, three, four and six is not in the unit. *And one budget, one world and one seed stream*: the card's own
setting. *And the boundary is a signal and not a policy*: nothing here asks the agent to act on it, and what it
would be worth to an agent whose map is trained by the payout is the unit `e488` opened and this one does not
enter. *And the endpoint is exact and not the corpus*: the single-trial path is bit-identical by construction, which
is a check on this unit's arithmetic and not evidence that the corpus's own numbers are right. *And three trials of
four steps is a short carry*: at the world's leak the first trial's drive has decayed by the read step, so the
episode is carried and thinly.
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
from experiments.e172_parser_registry import parser_flags

#: the two new runs and the corpus's own roll the endpoint is read against
BOUND = Path("runs/e489_earned_label_episode3_boundary_20reps.json")
PLAIN = Path("runs/e489_earned_label_episode3_20reps.json")
CARD = Path("runs/e438_earned_label_three_arms_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = ("naive", "ewc-block", "replay")
#: the two fields the runs move, and the run's own bookkeeping
MOVED = ("loop_episode", "loop_boundary")
BOOKKEEPING = ("json_out", "save_theta")
#: the episode, the card's world, and the fields the episode adds to a draw
EPISODE = 3
TAU = 12
SIZE = 300
READOUT_SIZE = 32
N_SYMBOLS = 12
NOISE = 1.0
ADDED = ("episode_len", "boundary_sha1", "n_boundary", "boundary_gain")
MIN_REPS = 20
SIGMA = 2.0
#: the accuracy's floor on the episodic task: the four-class chance, and how far above it the arms have to sit
CHANCE = 0.25
BAR = 0.10
CLAIMS = (
    ("FA1", "and the endpoint is exact, and only the episode moved",
     "Built with the flag off the environment's draw is the card's own field for field and carries no episode field, "
     "cue_input is bit-identical to the single-pulse array, each run carries the card's config with no field differing "
     "past the inert rule and the fields moved are loop_episode and loop_boundary, the plain run's draw is the card's "
     "plus episode_len and the boundary run's the card's plus the four episode fields, and each run carries twenty "
     "replicates",
     "falsifier: a draw field of the card's differing, an added field at the endpoint, an array differing, a config "
     "field differing past the two flags, an added or missing draw field that is not one of the four, or a replicate "
     "count other than twenty"),
    ("FA2", f"and the world's state at the read step is the episode's, at {SIGMA:.0f} sigma",
     "At the card's world and body two episodes sharing the last trial's cue and the cue's noise and differing in the "
     "earlier trials' cues give world states at the read step that differ at two sigma, and at one trial per pass the "
     "same manipulation moves the state by exactly zero",
     "falsifier: a mean difference of zero at the episode, one that does not resolve, or a non-zero difference at the "
     "single-trial endpoint"),
    ("FA3", "and the boundary is a channel of its own",
     "With the boundary drawn the drive is +gain at the episode's first step, -gain at every later trial's first step "
     "and zero everywhere else, the boundary neurons are disjoint from the cue, action and feedback populations and "
     "are in the task's input set, and with the flag off no channel is drawn",
     "falsifier: a step whose marker is not the declared sign or is non-zero where it should be zero, a population "
     "overlap, a channel outside the input set, or a channel drawn at the endpoint"),
    ("FA4", f"and the episodic task is learned, at {BAR:.2f} above a chance of {CHANCE:.2f}",
     "On the plain run every arm's accuracy diagonal is at least 0.10 above the four-class chance of 0.25",
     "falsifier: an arm within 0.05 of chance"),
    ("FA5", f"and the boundary does not buy the task, at {SIGMA:.0f} sigma",
     "On no arm is the boundary run's accuracy diagonal above the plain run's at two sigma",
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


def _roll(path: Path, card: dict | None) -> dict | None:
    doc = load(path)
    if not doc or card is None:
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
    other = card.get("config") or {}
    same, inert, differ = {}, {}, {}
    for k in sorted(set(cfg) | set(other)):
        old, new = other.get(k), cfg.get(k)
        if old == new:
            same[k] = new
        elif _inert(k, old, new):
            inert[k] = [old, new]
        else:
            differ[k] = [old, new]
    mine, theirs = doc.get("env_draw") or {}, card.get("env_draw") or {}
    draw_agree = {k: theirs.get(k) == mine.get(k) for k in theirs}
    added = sorted(set(mine) - set(theirs))
    missing = sorted(set(theirs) - set(mine))
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "draw": {"agree": draw_agree, "differ": sorted(k for k, ok in draw_agree.items() if not ok),
                     "added": added, "missing": missing, "card_fields": len(theirs)}}


def endpoint(circ) -> dict:
    """The endpoint, built rather than read: the flag off is the environment the corpus holds, bit for bit."""
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=NOISE,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0)
    plain = fly_env.build(circ, **common)
    summary = plain.summary()
    y = np.arange(64) % N_SYMBOLS
    return {"fields": len(summary),
            "added": sorted(set(summary) - set(_card_draw_fields())),
            "missing": sorted(set(_card_draw_fields()) - set(summary)),
            #: the episode's own path against the single-trial construction, both drawn from a generator at the same
            #: state -- so this is one environment's two methods and not a reconstruction of either
            "identical": bool(np.array_equal(plain.cue_pulse(y, np.random.default_rng(11)),
                                            plain.cue_input(y, np.random.default_rng(11))))}


def _card_draw_fields() -> set:
    doc = load(CARD)
    return set((doc or {}).get("env_draw") or {})


def episode_states(circ, net) -> dict:
    """The episode carried: the world's state at the read step, for two episodes that share everything but the past.

    The two conditions draw their cue noise from the **same** generator, so the only difference between them is the
    earlier trials' symbols -- which at one trial per pass are not in the input at all, so the difference there is
    exactly zero by construction and is the endpoint this measurement needs.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=NOISE,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0)
    rng = np.random.default_rng(23)
    y = rng.integers(0, N_SYMBOLS, size=64)
    got = {}
    for label, episode in (("episode", EPISODE), ("single", 1)):
        env = fly_env.build(circ, **{**common, "episode": episode})
        if episode > 1:
            a = np.stack([rng.integers(0, N_SYMBOLS, size=len(y)) for _ in range(episode - 1)], axis=1)
            b = np.stack([rng.integers(0, N_SYMBOLS, size=len(y)) for _ in range(episode - 1)], axis=1)
        else:
            a = b = None
        states = []
        for earlier in (a, b):
            u = torch.from_numpy(np.asarray(env.cue_input(y, np.random.default_rng(31), episode_symbols=earlier),
                                            dtype=np.float32))
            fn = env.feedback()
            with torch.no_grad():
                net(u, feedback=fn)
            states.append(fn.last_world.detach().clone())
        gap = [float(x) for x in (states[0] - states[1]).norm(dim=1)]
        got[label] = {"pairing": _paired(gap, [0.0] * len(gap)), "largest": max(gap), "smallest": min(gap),
                      "state_scale": float(states[0].norm(dim=1).mean())}
    return got


def boundary_channel(circ) -> dict:
    """The channel: the marker's sign at every step, the populations' disjointness, and the task's input set."""
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=NOISE,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0)
    env = fly_env.build(circ, **{**common, "episode": EPISODE, "boundary": True})
    off = fly_env.build(circ, **common)
    idx = np.asarray(env.boundary_neurons)
    x = torch.zeros(2, circ.n_neurons)
    fn = env.feedback()
    marks = []
    for t in range(TAU):
        add = fn(x, t)
        marks.append(float(add[0, idx].mean()))
    trials = [j * env.trial_len + env.cue_at for j in range(EPISODE)]
    want = [env.boundary_gain if t == env.cue_at else (-env.boundary_gain if t in trials else 0.0)
            for t in range(TAU)]
    task = fly_env.make_env_task(env, "loop_probe", symbols=range(4), n_train=8, n_test=8,
                                 readout_neurons=np.sort(np.random.default_rng(0).choice(
                                     circ.n_neurons, size=READOUT_SIZE, replace=False)))
    off_task = fly_env.make_env_task(off, "loop_probe", symbols=range(4), n_train=8, n_test=8,
                                     readout_neurons=np.sort(np.random.default_rng(0).choice(
                                         circ.n_neurons, size=READOUT_SIZE, replace=False)))
    populations = np.concatenate([env.cue_neurons, env.action_neurons, env.feedback_neurons])
    return {"gain": env.boundary_gain, "n_boundary": int(len(idx)), "marks": marks, "wanted": want,
            "steps_agree": all(abs(m - w) < 1e-6 for m, w in zip(marks, want)),
            "overlap": int(len(np.intersect1d(idx, populations))),
            "in_input": bool(np.isin(idx, task.input_neurons).all()),
            "off_has_channel": off.boundary_neurons is not None,
            "off_input_gap": int(len(np.setdiff1d(task.input_neurons, off_task.input_neurons)))}


def reading(bound: Path = BOUND, plain: Path = PLAIN, card: Path = CARD) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "endpoint": {}, "carry": {}, "boundary": {},
           "accuracy": {}, "spans": {}}
    card_doc = load(card)
    got = {"bound": _roll(bound, card_doc), "plain": _roll(plain, card_doc)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"{label} is absent, or the card's own roll is"}
    out["runs"] = got
    try:
        from clfly.connectome import annotate, circuits, graph
        from clfly.network.model import RateConfig, build_net
        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=SIZE)
        net = build_net(circ, RateConfig(tau=TAU)).torch_model()
        out["endpoint"] = endpoint(circ)
        out["carry"] = episode_states(circ, net)
        out["boundary"] = boundary_channel(circ)
    except (ImportError, OSError, ValueError) as exc:  # the substrate is not here
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    out["accuracy"] = {a: _paired(got["bound"]["arms"][a]["accuracy_diagonal"],
                                  got["plain"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "episode": EPISODE,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "config": {label: got[label]["config"] for label in got},
        "draw": {label: got[label]["draw"] for label in got},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), 4)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), 4)
                                  for a in ARMS} for label in got},
        "chance": CHANCE, "bar": BAR, "episode_fields": list(ADDED), "sigmas": SIGMA,
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    ep, bd = r["endpoint"], r["boundary"]
    want_added = {"plain": ["episode_len"], "bound": sorted(ADDED)}
    draw_ok = all(not roll["differ"] and not roll["missing"] and roll["added"] == want_added[label]
                  for label, roll in s["draw"].items())
    moved = {label: s["config"][label]["moved"] for label in s["config"]}
    moved_ok = (moved["bound"]["loop_episode"] == EPISODE and moved["bound"]["loop_boundary"] is True
                and moved["plain"]["loop_episode"] == EPISODE
                and moved["plain"]["loop_boundary"] in (None, False))
    differ = {label: s["config"][label]["differ"] for label in s["config"]}
    j1 = {"id": "FA1",
          "measured": f"the endpoint: {ep['fields']} draw fields, {ep['added']} added and {ep['missing']} missing "
                      f"against the card's own, `cue_input` bit-identical {ep['identical']}; the runs: config "
                      f"differing {differ} with the fields moved {moved}, and their draws against the card's "
                      f"{ {k: (v['added'], v['differ']) for k, v in s['draw'].items()} }",
          "verdict": "MET -- the flag off is the corpus's environment bit for bit, and the two runs move the episode "
                     "and nothing else" if (not ep["added"] and not ep["missing"] and ep["identical"] and draw_ok
                                            and moved_ok and not any(differ.values())
                                            and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- endpoint added {ep['added']} missing {ep['missing']} identical "
                     f"{ep['identical']}; config differing {differ}; moved {moved}; "
                     f"replicates {s['replicates']}"}
    c = r["carry"]["episode"]
    one = r["carry"]["single"]
    j2 = {"id": "FA2",
          "measured": f"at one trial the two episodes' world states differ by a mean of {one['pairing']['mean']:.4e} "
                      f"(largest {one['largest']:.4e}); at {EPISODE} trials by {c['pairing']['mean']:.4f} at "
                      f"{c['pairing']['sigma']:.2f} sigma over {c['pairing']['n']} episodes, the largest "
                      f"{c['largest']:.4f} against a state scale of {c['state_scale']:.2f}",
          "verdict": "MET -- the earlier trials are in the world's state at the read step, and at one trial the same "
                     "manipulation moves nothing" if (one["largest"] == 0.0 and c["pairing"]["mean"] > 0.0
                                                      and c["pairing"]["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- single-trial largest {one['largest']:.4e}, episode mean "
                     f"{c['pairing']['mean']:.4f} at {c['pairing']['sigma']:.2f} sigma"}
    j3 = {"id": "FA3",
          "measured": f"the marker at the {len(bd['marks'])} steps is {[round(m, 3) for m in bd['marks']]} against "
                      f"the declared {[round(w, 3) for w in bd['wanted']]}, gain {bd['gain']}, {bd['n_boundary']} "
                      f"neurons, {bd['overlap']} overlapping the three populations, in the input set "
                      f"{bd['in_input']}, and the flag off draws no channel {bd['off_has_channel']}",
          "verdict": "MET -- the boundary carries its sign at the episode's opening and at every continuing trial and "
                     "zero elsewhere, out of the three populations and inside the input" if
                     (bd["steps_agree"] and bd["overlap"] == 0 and bd["in_input"]
                      and not bd["off_has_channel"]) else
                     f"FALSIFIER FIRED -- marks {bd['marks']}, wanted {bd['wanted']}, overlap {bd['overlap']}, "
                     f"in_input {bd['in_input']}, off {bd['off_has_channel']}"}
    diag = s["accuracy_diagonal"]["plain"]
    thin = [a for a in ARMS if diag[a] < CHANCE + BAR]
    j4 = {"id": "FA4",
          "measured": f"the plain run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f} and a bar of "
                      f"{BAR:.2f} above it",
          "verdict": "MET -- the episodic task is learned on every arm, the weakest at "
                     + f"{min(diag[a] for a in ARMS) - CHANCE:+.4f} above chance" if not thin else
                     f"FALSIFIER FIRED -- {thin}"}
    acc = r["accuracy"]
    rising = [a for a in ARMS if acc[a]["mean"] > 0.0 and acc[a]["sigma"] >= SIGMA]
    j5 = {"id": "FA5",
          "measured": f"the boundary run's accuracy diagonal less the plain run's is "
                      f"{ {a: round(acc[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(acc[a]['sigma'], 2) for a in ARMS} } sigma, from "
                      f"{s['accuracy_diagonal']['bound']} against {diag}",
          "verdict": "MET -- the boundary does not buy the task: no arm rises at two sigma" if not rising else
                     f"FALSIFIER FIRED -- {rising}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the benchmark has an episode ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `env.py` names three absences -- a reward, an episode boundary and a policy; two are closed, and")
    print(f"   this gives the pass an episode of {EPISODE} trials with a boundary channel of its own")
    print(f"\n   {'arm':<10} {'boundary acc':>13} {'plain acc':>10} {'change':>9} {'sigma':>7} "
          f"{'boundary last':>14} {'plain last':>11}")
    for a in ARMS:
        c = r["accuracy"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['bound'][a]:>13.4f} "
              f"{r['spans']['accuracy_diagonal']['plain'][a]:>10.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['bound'][a]:>14.4f} "
              f"{r['spans']['accuracy_last']['plain'][a]:>11.4f}")
    print(f"\n   the config against the card's: "
          f"{ {k: v['differ'] for k, v in r['spans']['config'].items()} }")
    print(f"   the draws against the card's: "
          f"{ {k: (v['added'], v['differ'], v['missing']) for k, v in r['spans']['draw'].items()} }")
    print("\n== the registered claims, FA1-FA5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`env.py` closed on *no reward, no episode boundary and no policy*; the corpus now has all three)")
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
