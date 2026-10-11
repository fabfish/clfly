"""E494 -- the episode without the world: whether the loop is what buries the label.

Three units have taken the episode apart and none of them has taken the **loop** out of it. `e491` removed the world's
share of the earlier trials exactly and the accuracy did not move; `e492` lengthened the label's window and thinned
the episode and it did not move; `e493` handed the head the model's own thirty-two columns instead of the world's
eight and every arm gained **0.0521** to **0.0698** at four to seven sigma -- and stayed at chance, the bar being
**0.35**. **This unit asks the blunt version of the question**: the same episode, the same read, the same pass and
**no world at all**. The runner's own `--no-feedback` is the same suite and the same seeds with the feedback channel
disconnected, so what is left is two cues and a label through the network and nothing else.

One run and one instrument:

  * `e494 ... episode2_noworld` -- `e493`'s own command with `--no-feedback` on, so the episode's cues reach the
    model through the input and nothing comes back (new);
  * `e493 ... episode2_modelread` -- the same pass, the same read and the same boundary channel with the loop wired,
    which is the world this one removes.

Three claims, registered before the new run's reading was opened.

- **KB1 -- and the loop is the one flag moved.** Against `e493`'s run every recorded config field agrees except
  `no_feedback`, the output path and the saved weights, and the environment's draw agrees on **every** field -- the
  two runs build the same world, the same two trials and the same boundary channel and one of them does not wire it
  -- with twenty replicates each. **Falsifier**: any other config field differing, a draw field differing, or a
  replicate count other than twenty.
- **KB2 -- and the label's part of the read survives without the world.** Measured at the card's own body with
  deterministic cues and the earlier trials held fixed, the label's own part of the read at the last step -- the
  across-symbol spread as a share of that read's scale, **one width, two worlds**, which is the comparison this
  instrument can make -- is **larger with the loop unwired than with it wired** at two trials. **Falsifier**: the
  unwired share at or below the wired one, or a share that is not positive on either.
- **KB3 -- and without the world the label comes back.** On **at least two of the three arms** the new run's accuracy
  diagonal is at least **0.10** above the four-class chance of **0.25** and above `e493`'s own at **two** sigma.
  **Falsifier**: fewer than two arms, or an arm within **0.05** of chance. *It can fire, and that is the unit's own
  question: the corpus's one-trial runs read **0.76** to **0.86** with the loop wired, so a loop is not fatal to a
  single trial, and what an episode costs the loop is what has never been measured.*

**What it can do beyond that.** It is the last of the pass's four parts to be taken out one at a time -- the split,
the carry, the read and now the loop -- and it decides between two readings of everything above it. If the label comes
back with the world unwired, then the five-step window's worth of world is what buries it and the benchmark's
closed-loop episodic mode is priced at the loop rather than at the episode; if it does not, the episode's cost is in
the pass itself and a world that carries nothing is carrying the same loss.

**What it cannot do.** *No world is not a world*: with `--no-feedback` the corpus's own suite label records
*"feedback off"*, the head reads the model and the environment's state is never consulted, so this is the corpus's
loop-less reading and not a game. *And two things change with the flag*: the feedback channel and -- through the
runner's own rule that the world read needs the loop -- the read's source, which `e493` already moved once; the
comparison here is between runs whose reads are the same and whose worlds are not. *And one episode length and one
read*: two trials of six steps, the model's thirty-two columns, the card's own world. *And one budget, one seed
stream and twenty replicates*: the card's own setting, so a recovery is the setting's and a failure is the setting's
too.
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
from experiments import e493_the_read_the_world_loses as e493
from experiments.e172_parser_registry import parser_flags

#: the new run and the wired one it is read against
NOWORLD = Path("runs/e494_earned_label_episode2_noworld_20reps.json")
WIRED = e493.MODEL
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
MOVED = ("no_feedback",)
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = 2                          # the pass this line reads: two trials, six steps each
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
SYMBOLS = e493.SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
BAR = 0.10
CLAIMS = (
    ("KB1", "and the loop is the one flag moved",
     "Against e493's run every recorded config field agrees except no_feedback, the output path and the saved "
     "weights, and the environment's draw agrees on every field, with twenty replicates each",
     "falsifier: any other config field differing, a draw field differing, or a replicate count other than twenty"),
    ("KB2", "and the label's part of the read survives without the world",
     "Measured at the card's own body with deterministic cues and the earlier trials held fixed, the label's own part "
     "of the read at the last step is larger with the loop unwired than with it wired, at two trials",
     "falsifier: the unwired share at or below the wired one, or a share that is not positive on either"),
    ("KB3", f"and without the world the label comes back, at {BAR:.2f} and {SIGMA:.0f} sigma",
     "On at least two of the three arms the new run's accuracy diagonal is at least 0.10 above the four-class chance "
     "of 0.25 and above e493's own at two sigma",
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
    draw = {k: theirs.get(k) == mine.get(k) for k in sorted(set(mine) | set(theirs))}
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "draw": {"fields": len(draw), "differ": sorted(k for k, ok in draw.items() if not ok)}}


def read_share(circ, net) -> dict:
    """The label's own part of the model's read at the last step, with the loop wired and with it unwired.

    One width and two worlds, which is the comparison this instrument can make: the cues are deterministic and the
    earlier trials are held fixed across the examples, so one symbol is one trajectory and what varies from one
    symbol to the next is the label. What is reported for each is the across-symbol spread as a share of that read's
    own scale.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    env = fly_env.build(circ, readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0,
                        noise=0.0, world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0,
                        boundary=True, episode=EPISODE)
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    earlier = np.tile(np.arange(1, EPISODE, dtype=np.int64), (n, 1)) % SYMBOLS
    u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=earlier), dtype=np.float32))
    got = {}
    for label, wired in (("wired", True), ("unwired", False)):
        fn = env.feedback() if wired else None
        with torch.no_grad():
            traj = net(u, feedback=fn) if wired else net(u)
        w = traj[:, -1, :][:, rs].detach()
        means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
        across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
        within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
        scale = float(w.norm(dim=1).mean())
        got[label] = {"across": across, "within": within, "scale": scale,
                      "share": (across / scale) if scale else 0.0, "width": int(w.shape[1])}
    return got


def reading(noworld: Path = NOWORLD, wired: Path = WIRED) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    other = load(wired)
    got = {"unwired": _roll(noworld, other), "wired": _roll(wired, other)}
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
        out["share"] = read_share(circ, net)
    except (ImportError, OSError, ValueError) as exc:
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    out["recovery"] = {a: _paired(got["unwired"]["arms"][a]["accuracy_diagonal"],
                                  got["wired"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
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
    moved = s["config"]["unwired"]["moved"]
    differ = s["config"]["unwired"]["differ"]
    draw = s["draw"]["unwired"]
    j1 = {"id": "KB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: {draw['fields']} fields of the wired run's with **{len(draw['differ'])}** "
                      f"differing ({draw['differ']}); replicates {s['replicates']}",
          "verdict": "MET -- the loop is the one flag moved, over one world and one boundary channel" if
                     (not differ and moved.get("no_feedback") is True and not draw["differ"]
                      and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    share = r["share"]
    wired, unwired = share["wired"], share["unwired"]
    j2 = {"id": "KB2",
          "measured": f"the label's own part of the read at the last step as a share of its scale, at "
                      f"{EPISODE} trials: the wired read **{wired['share']:.4f}** (spread {wired['across']:.4f} "
                      f"against a scale of {wired['scale']:.4f}) against the unwired **{unwired['share']:.4f}** "
                      f"(spread {unwired['across']:.4f}, scale {unwired['scale']:.4f})",
          "verdict": "MET -- the label's part of the read is larger once the loop is out of it" if
                     (unwired["share"] > wired["share"] and unwired["share"] > 0.0 and wired["share"] >= 0.0) else
                     f"FALSIFIER FIRED -- wired {wired['share']:.4f} against unwired {unwired['share']:.4f}"}
    rec = r["recovery"]
    diag = s["accuracy_diagonal"]["unwired"]
    up = [a for a in ARMS if diag[a] >= CHANCE + BAR and rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
    thin = [a for a in ARMS if diag[a] < CHANCE + 0.05]
    j3 = {"id": "KB3",
          "measured": f"the unwired run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f}, and "
                      f"against the wired run's {s['accuracy_diagonal']['wired']} they change by "
                      f"{ {a: round(rec[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, with {len(up)} of three arms over "
                      f"the bar and {len(thin)} within 0.05 of chance",
          "verdict": f"MET -- without the world the label comes back, on **{len(up)}** of three arms ({up})" if
                     (len(up) >= 2 and not thin) else
                     f"FALSIFIER FIRED -- {len(up)} of three arms over the bar and two sigma ({up}), thin {thin}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the episode without the world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e491`, `e492` and `e493` took the carry, the split and the read out of the episode; this takes the")
    print("   loop out -- the same pass, the same read and the same boundary channel with --no-feedback")
    print(f"\n   {'arm':<10} {'unwired':>9} {'wired':>9} {'change':>9} {'sigma':>7} {'unwired last':>13} "
          f"{'wired last':>11}")
    for a in ARMS:
        c = r["recovery"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['unwired'][a]:>9.4f} "
              f"{r['spans']['accuracy_diagonal']['wired'][a]:>9.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['unwired'][a]:>13.4f} "
              f"{r['spans']['accuracy_last']['wired'][a]:>11.4f}")
    print(f"\n   the label's share of the read: wired {r['share']['wired']['share']:.4f} against unwired "
          f"{r['share']['unwired']['share']:.4f} (spreads {r['share']['wired']['across']:.4f} and "
          f"{r['share']['unwired']['across']:.4f})")
    print(f"   the config: {len(r['spans']['config']['unwired']['differ'])} differing past the inert rule; the draw: "
          f"differing {r['spans']['draw']['unwired']['differ']}")
    print("\n== the registered claims, KB1-KB3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e493` handed the head the model's own state inside the loop; this asks what the loop costs it)")
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
