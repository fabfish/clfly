"""E492 -- the episode at two trials: the window the label gets, and whether the label comes back.

`e489` gave the pass an episode and every arm came out at the four-class chance; `e491` made the world obey the
boundary and the world's share of the earlier trials went to **exactly zero** while the accuracy did not move -- so
what was left was the **model's** own carry and the **window**: at three trials the label's cue arrives at step **8**
of the twelve-step pass and the read is at step **11**, three drive steps, against the corpus's own eleven from a cue
at zero. **This unit shortens the episode to two trials**, which is the pass's other split of the same twelve: the
label's cue then arrives at step **6** and the read is at the same step **11**, five drive steps, and the episode
carries one distractor trial instead of two.

Two runs and one instrument:

  * `e492 ... episode2_boundary` -- the card's command with `--loop-episode 2 --loop-boundary` (new);
  * `e489 ... episode3_boundary` -- the same flags at three trials, which is the episode and the window this one
    changes;
  * the corpus's own roll at one trial per pass, whose label gets eleven steps, is read beside both.

Three claims, registered before the new run's reading was opened.

- **HB1 -- and the pass's split is the one flag moved.** Against `e489`'s boundary run every recorded config field
  agrees except `loop_episode` (two against three), the output path and the saved weights, and every draw field
  agrees except `episode_len` (two against three), the boundary channel's own three fields being the same channel;
  each run carries twenty replicates. **Falsifier**: any other config field differing, a draw field differing past
  `episode_len`, or a replicate count other than twenty.
- **HB2 -- and the label's own part of the read grows when the trial does.** Measured at the card's own body with
  **deterministic cues** and the earlier trials **held fixed across the examples**, so each symbol is one trajectory,
  the within-symbol spread sits at the float's own floor -- under a thousandth of the across-symbol spread it is
  checked against -- and what varies from one symbol to the next is the label: the
  across-symbol spread of the world's state at the read step is **larger at two trials than at three**, with the
  one-trial value carried beside them and the three splits of the pass measured at once. **Falsifier**: the spread
  at two at or below the spread at three, or a spread that is not positive at one trial. *The instrument is a
  measurement of the window and not a result: it says how much of the read is the label at each split, at a body that
  has not been trained.*
- **HB3 -- and the label comes back when the trial is longer.** On **at least two of the three arms** the two-trial
  run's accuracy diagonal is at least **0.10** above the four-class chance of **0.25** and above the three-trial
  run's diagonal at **two** sigma. **Falsifier**: fewer than two arms, or an arm within **0.05** of chance. *It can
  fire: the model's recurrent state still carries the earlier trials, which `e491` showed the world's rule does not,
  and a five-step window is longer than three and not the corpus's eleven.*

**What it can do beyond that.** It is the sweep `e489` and `e491` both named as the thing they could not do: the
pass's splits at one, two and three trials, with the label's window at eleven, five and three drive steps and the
episode's crowding at none, one and two distractor trials, against the same four-class task, the same world and the
same read step. If the label comes back at two trials the game has an episodic mode that works and a measured reason
why; if it does not, the cardinality of the episode is not what the corpus's read-out is paying for.

**What it cannot do.** *Two splits are not a sweep*: the pass offers four (two, three, four and six trials) and this
unit carries two of them against the corpus's one. *And the two changes travel together*: two trials is a longer
window **and** one fewer distractor, and no split of a fixed twelve-step pass separates them. *And the model's carry
is untouched*: the cues still reach the last trial's actions through the recurrent state, which `e491` neither
removed nor measured. *And one budget, one world and one seed stream*: the card's own setting. *And the instrument is
at an untrained body*: the label's share of the read is measured before any training, so it ranks the splits and does
not say what a head can find in them.
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

#: the new run and the two it is read against
TWO = Path("runs/e492_earned_label_episode2_boundary_20reps.json")
THREE = e489.BOUND
CARD = e489.CARD
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the one field the run moves in the configuration, and the one its draw moves
MOVED = ("loop_episode",)
DRAW_MOVED = ("episode_len",)
BOOKKEEPING = ("json_out", "save_theta")
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
CHANCE = e489.CHANCE
SYMBOLS = 4
MIN_REPS = 20
SIGMA = 2.0
BAR = 0.10
#: the pass's own splits, the two this unit reads and the corpus's one beside them
SPLITS = (1, 2, 3)
CLAIMS = (
    ("HB1", "and the pass's split is the one flag moved",
     "Against e489's boundary run every recorded config field agrees except loop_episode, the output path and the "
     "saved weights, and every draw field agrees except episode_len, with twenty replicates each",
     "falsifier: any other config field differing, a draw field differing past episode_len, or a replicate count "
     "other than twenty"),
    ("HB2", "and the label's own part of the read grows when the trial does",
     "Measured at the card's own body with deterministic cues, the across-symbol spread of the world's state at the "
     "read step is larger at two trials than at three, with the one-trial value beside them",
     "falsifier: the spread at two at or below the spread at three, or a spread that is not positive at one trial"),
    ("HB3", f"and the label comes back when the trial is longer, at {BAR:.2f} and {SIGMA:.0f} sigma",
     "On at least two of the three arms the two-trial run's accuracy diagonal is at least 0.10 above the four-class "
     "chance of 0.25 and above the three-trial run's diagonal at two sigma",
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
    if key in MOVED or key in DRAW_MOVED or key in BOOKKEEPING:
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
    draw = {}
    for k in sorted(set(mine) | set(theirs)):
        if k in DRAW_MOVED:
            continue
        draw[k] = theirs.get(k) == mine.get(k)
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "draw": {"fields": len(draw), "differ": sorted(k for k, ok in draw.items() if not ok),
                     "moved": {k: [theirs.get(k), mine.get(k)] for k in DRAW_MOVED}}}


def label_share(circ, net) -> dict:
    """The label's own part of the world's state at the read step, at each split of the pass.

    The cues are **deterministic** -- a drawn body, `noise = 0` -- so one symbol is one trajectory and the
    within-symbol spread sits at the float's own floor; what is left is the across-symbol spread, which is the label's
    part of the
    state the head reads. It is the instrument of HB2 and not a result: the body has not been trained.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=0.0,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0, boundary=True)
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    got = {}
    for k in SPLITS:
        env = fly_env.build(circ, **{**common, "episode": k})
        #: the earlier trials are **held fixed** across the examples, so the only thing that varies from one symbol
        #: to the next is the label: the past is a constant and what the across-symbol spread measures is the label's
        #: own part of the state
        earlier = (np.tile(np.arange(1, k, dtype=np.int64), (n, 1)) % SYMBOLS if k > 1 else None)
        u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=earlier), dtype=np.float32))
        fn = env.feedback()
        with torch.no_grad():
            net(u, feedback=fn)
        w = fn.last_world.detach()
        means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
        across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
        within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
        got[k] = {"across": across, "within": within, "state_scale": float(w.norm(dim=1).mean()),
                  "examples": n}
    return got


def reading(two: Path = TWO, three: Path = THREE) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    other = load(three)
    got = {"two": _roll(two, other), "three": _roll(three, other)}
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
        out["share"] = label_share(circ, net)
    except (ImportError, OSError, ValueError) as exc:
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    out["recovery"] = {a: _paired(got["two"]["arms"][a]["accuracy_diagonal"],
                                  got["three"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "chance": CHANCE, "symbols": SYMBOLS,
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
    moved = s["config"]["two"]["moved"]
    differ = s["config"]["two"]["differ"]
    draw = s["draw"]["two"]
    j1 = {"id": "HB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: {draw['fields']} fields compared with **{draw['differ']}** differing, "
                      f"`episode_len` moving {draw['moved'].get('episode_len')}; replicates {s['replicates']}",
          "verdict": "MET -- the pass's split is the one flag moved, and the boundary channel is the same channel"
                     if (not differ and moved.get("loop_episode") == 2 and not draw["differ"]
                         and draw["moved"].get("episode_len") == [3, 2] and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    share = {int(k): v for k, v in r["share"].items()}   # a JSON artifact carries the splits as strings
    order = {k: share[k]["across"] for k in SPLITS}
    floor = {k: share[k]["within"] for k in SPLITS}
    scale = {k: share[k]["state_scale"] for k in SPLITS}
    #: the cues are deterministic and the past is fixed, so the within-symbol spread is the float's own floor and not
    #: a quantity: the check is that it stays under a thousandth of the across-symbol spread it sits beside
    worse = [k for k in SPLITS if floor[k] > 1e-3 * order[k]]
    j2 = {"id": "HB2",
          "measured": f"the across-symbol spread of the world's state at the read step is "
                      f"{ {k: round(order[k], 4) for k in SPLITS} } at one, two and three trials, against a "
                      f"within-symbol spread of { {k: f'{floor[k]:.2e}' for k in SPLITS} } and a state scale of "
                      f"{ {k: round(scale[k], 4) for k in SPLITS} }",
          "verdict": "MET -- the label's part of the read is larger at two trials than at three, at a body where each "
                     "symbol is one trajectory" if (order[2] > order[3] and order[1] > 0.0 and not worse) else
                     f"FALSIFIER FIRED -- across { {k: round(order[k], 4) for k in SPLITS} }, within above the floor "
                     f"at {worse}"}
    rec = r["recovery"]
    diag = s["accuracy_diagonal"]["two"]
    up = [a for a in ARMS if diag[a] >= CHANCE + BAR and rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
    thin = [a for a in ARMS if diag[a] < CHANCE + 0.05]
    j3 = {"id": "HB3",
          "measured": f"the two-trial run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f}, and "
                      f"against the three-trial run's {s['accuracy_diagonal']['three']} they change by "
                      f"{ {a: round(rec[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, with {len(up)} of three arms over "
                      f"the bar and {len(thin)} within 0.05 of chance",
          "verdict": f"MET -- the label comes back at two trials, on **{len(up)}** of three arms ({up})" if
                     (len(up) >= 2 and not thin) else
                     f"FALSIFIER FIRED -- {len(up)} of three arms over the bar and two sigma ({up}), thin {thin}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the episode at two trials ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e491` showed the world's carry is not what costs the label; this shortens the episode to two trials,")
    print("   which gives the label five drive steps instead of three and one distractor instead of two")
    print(f"\n   {'arm':<10} {'two trials':>11} {'three':>9} {'change':>9} {'sigma':>7} {'two last':>10} "
          f"{'three last':>11}")
    for a in ARMS:
        c = r["recovery"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['two'][a]:>11.4f} "
              f"{r['spans']['accuracy_diagonal']['three'][a]:>9.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['two'][a]:>10.4f} "
              f"{r['spans']['accuracy_last']['three'][a]:>11.4f}")
    print(f"\n   the label's share of the read, at the card's body: across "
          f"{ {k: round(r['share'][k]['across'], 4) for k in SPLITS} } and within "
          f"{ {k: round(r['share'][k]['within'], 6) for k in SPLITS} }")
    print(f"   the config: {len(r['spans']['config']['two']['differ'])} differing past the inert rule; the draw: "
          f"differing {r['spans']['draw']['two']['differ']} with `episode_len` moving "
          f"{r['spans']['draw']['two']['moved'].get('episode_len')}")
    print("\n== the registered claims, HB1-HB3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e489` read the split at three trials and `e491` excluded the world's carry; this is the split)")
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
