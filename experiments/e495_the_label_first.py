"""E495 -- the label first: whether what buries the episode's label is the window it gets.

`e489` to `e494` took the pass apart one flag at a time. The **carry** went and the accuracy did not move (`e491`),
the **split** and its window went and it did not move (`e492`), the **read** was worth **0.0521** to **0.0698** at
four to seven sigma and the bar stayed out of reach (`e493`), and the **loop** itself went and every arm **lost**
**0.0208** to **0.0306** (`e494`). What is left is the pass's shape, and the sharpest version of it is **where the
label sits**: at two trials the label is the episode's **last** trial, so its cue arrives at step **6** and only
**five** drive steps and no distractor lie between it and the read at step **11**, where the corpus's own single-trial
run gives the label **eleven**. **This unit moves the label to the first trial** and puts the episode's other symbol
after it, so the label's window is the whole pass and the label is the oldest cue in it.

One run and one instrument:

  * `e495 ... episode2_labelfirst` -- `e493`'s own command with `--loop-label-first` added, so the label is at step
    **0** and the distractor at step **6** (new);
  * `e493 ... episode2_modelread` -- the same pass, the same read and the same boundary channel with the label at
    step **6** and the distractor at step **0**, which is the placement this one moves.

Three claims, registered before the new run's reading was opened.

- **LB1 -- and the placement is the one flag moved.** Against `e493`'s run every recorded config field agrees except
  `loop_label_first`, the output path and the saved weights, and the environment's draw agrees on every field except
  the one the flag adds (`label_first`), with twenty replicates each. **Falsifier**: any other config field differing,
  a draw field differing past the one the flag adds, or a replicate count other than twenty.
- **LB2 -- and the label's part of the read grows when its window does.** Measured at the card's own body with
  deterministic cues and the episode's other symbol held fixed, the label's own part of the read at the last step --
  the across-symbol spread as a share of that read's scale, **one width, one world, two placements** -- is **larger
  with the label first than with it last**, with the two spreads carried beside them. **Falsifier**: the label-first
  share at or below the label-last one, or a share that is not positive on either.
- **LB3 -- and the label comes back when it gets the pass.** On **at least two of the three arms** the new run's
  accuracy diagonal is at least **0.10** above the four-class chance of **0.25** and above `e493`'s own at **two**
  sigma. **Falsifier**: fewer than two arms, or an arm within **0.05** of chance. *It can fire: the label-first pass
  hands the label the corpus's own eleven steps, and `e494`'s evidence that the loop is an asset rather than a
  distorter says the recurrence can carry a cue that far -- one trial's runs are **0.76** to **0.86**.*

**What it can do beyond that.** It decides what the episode's cost is *made of*: if the label comes back when it is
first, the pass is fine and the label's **window** is what the corpus's last-trial placement was paying, which makes
the episodic mode usable with one flag; if it does not, the pass costs the label whatever position it takes and the
distractor is what is in the way. Either way the four exclusions above are held fixed and this is the pass's own
shape being swept.

**What it cannot do.** *One placement pair and one episode length*: first against last at two trials, with the
distractors' own symbols held to the same generator, and the three-cue, four-cue and longer passes are not in it.
*And the label's position and its window are the same flag*: the first trial is the longest window a pass of two has,
so what a window at three or four trials would buy is not separable here. *And one read*: the model's own thirty-two
columns, which `e493` showed is the better of the corpus's two. *And the payout is not on these runs*: the runner
refuses `--loop-label-first` with `--loop-reward`, since the environment's target is read off the pass's last cue.
*And one budget, one world and one seed stream*: the card's own setting.
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

#: the new run and the placement it is read against
FIRST = Path("runs/e495_earned_label_episode2_labelfirst_20reps.json")
LAST = e493.MODEL
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
MOVED = ("loop_label_first",)
ADDED = ("label_first",)
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = 2
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
    ("LB1", "and the placement is the one flag moved",
     "Against e493's run every recorded config field agrees except loop_label_first, the output path and the saved "
     "weights, and the environment's draw agrees on every field except the one the flag adds, with twenty replicates "
     "each",
     "falsifier: any other config field differing, a draw field differing past the one the flag adds, or a replicate "
     "count other than twenty"),
    ("LB2", "and the label's part of the read grows when its window does",
     "Measured at the card's own body with deterministic cues and the episode's other symbol held fixed, the label's "
     "own part of the read at the last step is larger with the label first than with it last",
     "falsifier: the label-first share at or below the label-last one, or a share that is not positive on either"),
    ("LB3", f"and the label comes back when it gets the pass, at {BAR:.2f} and {SIGMA:.0f} sigma",
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
                     "added": sorted(set(mine) - set(theirs)), "missing": sorted(set(theirs) - set(mine))}}


def read_share(circ, net) -> dict:
    """The label's own part of the model's read at the last step, with the label first and with it last.

    One width, one world and two placements: the cues are deterministic and the episode's other symbol is held fixed
    across the examples, so one symbol is one trajectory and what varies from one symbol to the next is the label.
    What is reported for each placement is the across-symbol spread as a share of that read's own scale.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    other = np.tile(np.arange(1, EPISODE, dtype=np.int64), (n, 1)) % SYMBOLS
    got = {}
    for label, first in (("last", False), ("first", True)):
        env = fly_env.build(circ, readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0,
                            noise=0.0, world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0,
                            boundary=True, episode=EPISODE, label_first=first)
        u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=other), dtype=np.float32))
        fn = env.feedback()
        with torch.no_grad():
            traj = net(u, feedback=fn)
        w = traj[:, -1, :][:, rs].detach()
        means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
        across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
        within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
        scale = float(w.norm(dim=1).mean())
        got[label] = {"across": across, "within": within, "scale": scale,
                      "share": (across / scale) if scale else 0.0, "width": int(w.shape[1])}
    return got


def reading(first: Path = FIRST, last: Path = LAST) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    other = load(last)
    got = {"first": _roll(first, other), "last": _roll(last, other)}
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
    out["recovery"] = {a: _paired(got["first"]["arms"][a]["accuracy_diagonal"],
                                  got["last"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
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
    moved = s["config"]["first"]["moved"]
    differ = s["config"]["first"]["differ"]
    draw = s["draw"]["first"]
    j1 = {"id": "LB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: **{draw['added']}** added and **{draw['differ']}** differing; replicates "
                      f"{s['replicates']}",
          "verdict": "MET -- the placement is the one flag moved, over one world, one pass and one read" if
                     (not differ and moved.get("loop_label_first") is True and draw["added"] == sorted(ADDED)
                      and not draw["differ"] and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    share = r["share"]
    last, first = share["last"], share["first"]
    j2 = {"id": "LB2",
          "measured": f"the label's own part of the read at the last step as a share of its scale, at {EPISODE} "
                      f"trials: the label last **{last['share']:.4f}** (spread {last['across']:.4f} against a scale "
                      f"of {last['scale']:.4f}) against the label first **{first['share']:.4f}** (spread "
                      f"{first['across']:.4f}, scale {first['scale']:.4f})",
          "verdict": "MET -- the label's part of the read grows when its window does" if
                     (first["share"] > last["share"] and first["share"] > 0.0 and last["share"] >= 0.0) else
                     f"FALSIFIER FIRED -- label last {last['share']:.4f} against label first {first['share']:.4f}"}
    rec = r["recovery"]
    diag = s["accuracy_diagonal"]["first"]
    up = [a for a in ARMS if diag[a] >= CHANCE + BAR and rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
    thin = [a for a in ARMS if diag[a] < CHANCE + 0.05]
    j3 = {"id": "LB3",
          "measured": f"the label-first run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f}, and "
                      f"against the label-last run's {s['accuracy_diagonal']['last']} they change by "
                      f"{ {a: round(rec[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, with {len(up)} of three arms over "
                      f"the bar and {len(thin)} within 0.05 of chance",
          "verdict": f"MET -- the label comes back when it gets the pass, on **{len(up)}** of three arms ({up})" if
                     (len(up) >= 2 and not thin) else
                     f"FALSIFIER FIRED -- {len(up)} of three arms over the bar and two sigma ({up}), thin {thin}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the label first ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the pass's carry, split, read and loop are each measured and none is the cost; this moves the label")
    print("   from the episode's last trial to its first, so its window is the whole pass instead of five steps")
    print(f"\n   {'arm':<10} {'label first':>11} {'label last':>11} {'change':>9} {'sigma':>7} {'first last':>11} "
          f"{'last last':>10}")
    for a in ARMS:
        c = r["recovery"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['first'][a]:>11.4f} "
              f"{r['spans']['accuracy_diagonal']['last'][a]:>11.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['first'][a]:>11.4f} "
              f"{r['spans']['accuracy_last']['last'][a]:>10.4f}")
    print(f"\n   the label's share of the read: last {r['share']['last']['share']:.4f} against first "
          f"{r['share']['first']['share']:.4f} (spreads {r['share']['last']['across']:.4f} and "
          f"{r['share']['first']['across']:.4f})")
    print(f"   the config: {len(r['spans']['config']['first']['differ'])} differing past the inert rule; the draw: "
          f"added {r['spans']['draw']['first']['added']} and differing {r['spans']['draw']['first']['differ']}")
    print("\n== the registered claims, LB1-LB3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e493` and `e494` measured the read and the loop; this is the pass's own shape -- where the label is)")
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
